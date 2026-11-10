"""02 — synthetic geometry sweep: run the 12 required cases and record recovered vs truth.

Outputs are SYNTHETIC. They validate the software, not the D435.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from w6 import core                                   # noqa: E402
from w6.synthetic import (S40Truth, render_two_planes, quantize, add_outliers,   # noqa: E402
                          add_boundary_mixing)

INTR = core.Intrinsics(927.17, 927.367, 651.315, 349.621, 848, 480)
SHAPE = (480, 848)
STEP = 0.040
OUT = HERE / "results"


def truth(z=0.60, step=STEP, tilt=0.0, unp=0.0, noise=0.0):
    t = math.radians(tilt); tb = math.radians(tilt + unp)
    nf = np.array([math.sin(t), 0.0, -math.cos(t)])
    nb = np.array([math.sin(tb), 0.0, -math.cos(tb)])
    cf = float(nf[2] * z)
    return S40Truth(tag="SYNTHETIC", step_m=step, front_normal=nf.tolist(), back_normal=nb.tolist(),
                    front_offset=cf, back_offset=cf - step, noise_sigma_mm=noise, distance_m=z)


def analyse(depth, label):
    pf = core.fit_plane(core.collect_points(label == 1, depth, INTR))
    pb = core.fit_plane(core.collect_points(label == 2, depth, INTR))
    sep = core.plane_separation(pf, pb)
    med = abs(float(np.nanmedian(depth[label == 1])) - float(np.nanmedian(depth[label == 2])))
    return {"recovered_m": sep["separation_m"], "angle_deg": sep["normal_angle_deg"],
            "front_rms_mm": pf.rms_m * 1000, "back_rms_mm": pb.rms_m * 1000,
            "naive_median_m": med, "n_front": pf.n_points, "n_back": pb.n_points,
            "sensitivity_mm": core.separation_sensitivity(pf, pb)["spread_over_40mm_window_m"] * 1000}


def main() -> int:
    rng = np.random.default_rng(20261029)
    rows = []
    cases = [
        ("01_ideal_parallel_40mm", truth()),
        ("02_global_tilt_5deg", truth(tilt=5.0)),
        ("03_global_tilt_15deg", truth(tilt=15.0)),
        ("04_unparallel_0p5deg", truth(unp=0.5)),
        ("05_noise_0p5mm", truth(noise=0.5)),
        ("06_noise_2mm", truth(noise=2.0)),
        ("07_distance_0p35m", truth(z=0.35)),
        ("08_distance_0p90m", truth(z=0.90)),
    ]
    for name, tr in cases:
        d, lb = render_two_planes(INTR, SHAPE, tr, rng=rng)
        r = analyse(d, lb)
        rows.append({"case": name, "truth_m": STEP, "recovered_m": r["recovered_m"],
                     "error_mm": (r["recovered_m"] - STEP) * 1000, "angle_deg": r["angle_deg"],
                     "front_rms_mm": r["front_rms_mm"], "back_rms_mm": r["back_rms_mm"],
                     "naive_median_error_mm": (r["naive_median_m"] - STEP) * 1000,
                     "sensitivity_mm": r["sensitivity_mm"], "tag": "SYNTHETIC"})

    # quantisation
    d, lb = render_two_planes(INTR, SHAPE, truth())
    raw = quantize(d, 0.001); dm = core.depth_to_metres(raw, 0.001)
    r = analyse(dm, lb)
    rows.append({"case": "09_quantized_z16", "truth_m": STEP, "recovered_m": r["recovered_m"],
                 "error_mm": (r["recovered_m"] - STEP) * 1000, "angle_deg": r["angle_deg"],
                 "front_rms_mm": r["front_rms_mm"], "back_rms_mm": r["back_rms_mm"],
                 "naive_median_error_mm": (r["naive_median_m"] - STEP) * 1000,
                 "sensitivity_mm": r["sensitivity_mm"], "tag": "SYNTHETIC"})

    # invalid pixels
    d2 = d.copy(); d2[100:160, 90:150] = 0.0; d2[300:320, 600:700] = np.nan
    r = analyse(core.depth_to_metres(quantize(d2, 0.001), 0.001), lb)
    rows.append({"case": "10_invalid_pixels", "truth_m": STEP, "recovered_m": r["recovered_m"],
                 "error_mm": (r["recovered_m"] - STEP) * 1000, "angle_deg": r["angle_deg"],
                 "front_rms_mm": r["front_rms_mm"], "back_rms_mm": r["back_rms_mm"],
                 "naive_median_error_mm": (r["naive_median_m"] - STEP) * 1000,
                 "sensitivity_mm": r["sensitivity_mm"], "tag": "SYNTHETIC"})

    # local outlier patch
    d3 = add_outliers(d, 4, rng, patch=14, delta_mm=25.0)
    r = analyse(d3, lb)
    rows.append({"case": "11_local_outliers_25mm", "truth_m": STEP, "recovered_m": r["recovered_m"],
                 "error_mm": (r["recovered_m"] - STEP) * 1000, "angle_deg": r["angle_deg"],
                 "front_rms_mm": r["front_rms_mm"], "back_rms_mm": r["back_rms_mm"],
                 "naive_median_error_mm": (r["naive_median_m"] - STEP) * 1000,
                 "sensitivity_mm": r["sensitivity_mm"], "tag": "SYNTHETIC"})

    # boundary mixing
    d4 = add_boundary_mixing(d, px=3)
    r = analyse(d4, lb)
    rows.append({"case": "12_boundary_mixing", "truth_m": STEP, "recovered_m": r["recovered_m"],
                 "error_mm": (r["recovered_m"] - STEP) * 1000, "angle_deg": r["angle_deg"],
                 "front_rms_mm": r["front_rms_mm"], "back_rms_mm": r["back_rms_mm"],
                 "naive_median_error_mm": (r["naive_median_m"] - STEP) * 1000,
                 "sensitivity_mm": r["sensitivity_mm"], "tag": "SYNTHETIC"})

    # wrong depth scale
    d5 = core.depth_to_metres(quantize(d, 0.001), 0.002)
    r = analyse(d5, lb)
    rows.append({"case": "13_wrong_depth_scale_2x", "truth_m": STEP, "recovered_m": r["recovered_m"],
                 "error_mm": (r["recovered_m"] - STEP) * 1000, "angle_deg": r["angle_deg"],
                 "front_rms_mm": r["front_rms_mm"], "back_rms_mm": r["back_rms_mm"],
                 "naive_median_error_mm": (r["naive_median_m"] - STEP) * 1000,
                 "sensitivity_mm": r["sensitivity_mm"], "tag": "SYNTHETIC"})

    # small visible area
    d6, lb6 = render_two_planes(INTR, SHAPE, truth(), front_size=0.03, back_size=0.03)
    roi = core.ROI("front", [(0, 0), (847, 0), (847, 479), (0, 479)], min_valid_ratio=0.90)
    st = core.roi_stats(core.polygon_mask(d6.shape, roi.polygon), d6, roi)
    rows.append({"case": "14_small_visible_area", "truth_m": STEP, "recovered_m": float("nan"),
                 "error_mm": float("nan"), "angle_deg": float("nan"), "front_rms_mm": float("nan"),
                 "back_rms_mm": float("nan"), "naive_median_error_mm": float("nan"),
                 "sensitivity_mm": float("nan"), "tag": "SYNTHETIC",
                 "roi_valid_ratio": st["valid_ratio"], "roi_gate_ok": st["ok"]})

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "synthetic_geometry_results.csv", index=False)
    print(df.to_string(index=False))
    ok = df[df.case.str.startswith(("01", "02", "03", "07", "08", "09", "10"))]
    print("\nmax |error| over exact/quantised cases (mm):", float(ok.error_mm.abs().max()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
