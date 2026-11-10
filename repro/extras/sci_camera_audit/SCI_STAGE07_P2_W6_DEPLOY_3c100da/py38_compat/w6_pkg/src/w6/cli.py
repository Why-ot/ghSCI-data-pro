"""W6 command-line entry point.

    python -m w6.cli selfcheck                 run the synthetic geometry validation
    python -m w6.cli schema --out DIR          write the empty data skeleton + CSV templates
    python -m w6.cli check --placement DIR     report which artefacts are present/missing
    python -m w6.cli fit --placement DIR --roi ROI.json --intrinsics INTR.json
    python -m w6.cli worksheet --csv FILE      validate the 5x3 reference worksheet

No command opens a camera, a USB device or the network.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from . import core, uncertainty
from .synthetic import S40Truth, render_two_planes


def _load_rois(path: str) -> dict:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: core.ROI.from_json(v) for k, v in d.items()}


def cmd_selfcheck(args) -> int:
    intr = core.Intrinsics(927.17, 927.367, 651.315, 349.621, 848, 480)
    shape = (480, 848)
    z = 0.60
    truth = S40Truth(tag="SYNTHETIC", step_m=0.040,
                     front_normal=[0, 0, -1], back_normal=[0, 0, -1],
                     front_offset=-z, back_offset=-(z + 0.040), distance_m=z)
    depth, label = render_two_planes(intr, shape, truth)
    mf, mb = label == 1, label == 2
    pf = core.fit_plane(core.collect_points(mf, depth, intr))
    pb = core.fit_plane(core.collect_points(mb, depth, intr))
    sep = core.plane_separation(pf, pb)
    ok = abs(sep["separation_m"] - 0.040) < 1e-6
    print(json.dumps({"selfcheck": "PASS" if ok else "FAIL",
                      "recovered_step_m": sep["separation_m"], "truth_m": 0.040,
                      "front_rms_mm": pf.rms_m * 1000, "back_rms_mm": pb.rms_m * 1000,
                      "normal_angle_deg": sep["normal_angle_deg"], "tag": "SYNTHETIC"}, indent=2))
    return 0 if ok else 1


def cmd_schema(args) -> int:
    root = Path(args.out)
    for i in range(1, uncertainty.PLACEMENTS + 1):
        p = root / f"placement_{i:02d}"
        for sub in ("raw/depth", "raw/color", "meta", "reference"):
            (p / sub).mkdir(parents=True, exist_ok=True)
        (p / "meta" / "PLACEHOLDER.txt").write_text(
            "Fill with real D435 artefacts. Nothing here is a measurement.\n", encoding="utf-8")
    layout = uncertainty.placement_layout(root)
    (root / "schema.json").write_text(json.dumps(layout, indent=2), encoding="utf-8")
    print(json.dumps({"created": str(root), "placements": uncertainty.PLACEMENTS}, indent=2))
    return 0


def cmd_check(args) -> int:
    rep = uncertainty.check_placement_dir(args.placement)
    print(json.dumps(rep, indent=2))
    return 0 if rep["complete"] else 2


def cmd_worksheet(args) -> int:
    rows = uncertainty.read_reference_rows(args.csv)
    rep = uncertainty.validate_reference_rows(rows)
    rep.update(uncertainty.reference_mean_and_sd(rows))
    print(json.dumps(rep, indent=2))
    return 0 if rep["complete"] else 2


def cmd_fit(args) -> int:
    intr = core.Intrinsics.from_json(args.intrinsics)
    intr.validate()
    rois = _load_rois(args.roi)
    raw = core.read_depth_z16(args.depth, intr.width, intr.height)
    depth = core.depth_to_metres(raw, args.depth_scale)
    fits = {}
    for name, roi in rois.items():
        mask = core.erode(core.polygon_mask(depth.shape, roi.polygon), roi.boundary_erode_px)
        st = core.roi_stats(mask, depth, roi)
        if not st["ok"]:
            fits[name] = {"ok": False, **st}
            continue
        pts = core.collect_points(mask, depth, intr)
        pf = core.fit_plane(pts)
        fits[name] = {"ok": True, **st, "rms_mm": pf.rms_m * 1000,
                      "normal": pf.normal.tolist(), "offset_m": pf.offset, "n_points": pf.n_points}
    out = {"depth": str(args.depth), "depth_scale": args.depth_scale, "rois": fits}
    if all(v.get("ok") for v in fits.values()) and len(fits) >= 2:
        names = list(fits)[:2]
        pf = core.PlaneFit(np.array(fits[names[0]]["normal"]), np.zeros(3), fits[names[0]]["offset_m"],
                           0.0, fits[names[0]]["n_points"], np.zeros(3))
        pb = core.PlaneFit(np.array(fits[names[1]]["normal"]), np.zeros(3), fits[names[1]]["offset_m"],
                           0.0, fits[names[1]]["n_points"], np.zeros(3))
        out["separation"] = core.plane_separation(pf, pb)
    print(json.dumps(out, indent=2, default=float))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="w6", description="S40 measurement pipeline (offline only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selfcheck").set_defaults(fn=cmd_selfcheck)
    p = sub.add_parser("schema"); p.add_argument("--out", required=True); p.set_defaults(fn=cmd_schema)
    p = sub.add_parser("check"); p.add_argument("--placement", required=True); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("worksheet"); p.add_argument("--csv", required=True); p.set_defaults(fn=cmd_worksheet)
    p = sub.add_parser("fit")
    p.add_argument("--depth", required=True); p.add_argument("--intrinsics", required=True)
    p.add_argument("--roi", required=True); p.add_argument("--depth-scale", type=float, default=0.001)
    p.set_defaults(fn=cmd_fit)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
