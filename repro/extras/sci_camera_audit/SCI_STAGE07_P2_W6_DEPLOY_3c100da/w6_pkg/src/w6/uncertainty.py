"""W6 uncertainty bookkeeping for the S40 reference step.

The unit of independence is the physical PLACEMENT (5), never the frame (150) and never the reference
reading (15). Everything here is descriptive statistics plus an explicit statement of what is unknown.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

PLACEMENTS = 5
READINGS_PER_PLACEMENT = 3
FRAMES_PER_PLACEMENT = 30


# ------------------------------------------------------------------------------------- variability


def within_placement(seps_m: list[float]) -> dict:
    """Frame-to-frame variability inside one placement."""
    a = np.asarray([s for s in seps_m if np.isfinite(s)], dtype=float)
    if a.size == 0:
        return {"n": 0, "mean_m": float("nan"), "std_m": float("nan"), "u95_m": float("nan")}
    std = float(a.std(ddof=1)) if a.size > 1 else 0.0
    return {"n": int(a.size), "mean_m": float(a.mean()), "std_m": std,
            "u95_m": float(1.96 * std / math.sqrt(a.size)) if a.size > 1 else 0.0}


def between_placement(per_placement_means: list[float]) -> dict:
    """Variability of the placement means — this is the level that enters the final uncertainty."""
    a = np.asarray([m for m in per_placement_means if np.isfinite(m)], dtype=float)
    if a.size < 2:
        return {"n": int(a.size), "mean_m": float(a.mean()) if a.size else float("nan"),
                "std_m": float("nan"), "u95_m": float("nan"),
                "note": "fewer than 2 placements; between-placement variability undefined"}
    std = float(a.std(ddof=1))
    return {"n": int(a.size), "mean_m": float(a.mean()), "std_m": std,
            "u95_m": float(1.96 * std / math.sqrt(a.size))}


# ------------------------------------------------------------------------------- reference worksheet


def read_reference_rows(path: str | Path) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def validate_reference_rows(rows: list[dict]) -> dict:
    """Check the 5x3 worksheet. Any blank/invalid cell is INCOMPLETE, never silently filled."""
    problems = []
    values: dict[str, list[float]] = {}
    for r in rows:
        pid = (r.get("placement_id") or "").strip()
        if not pid:
            problems.append("row without placement_id")
            continue
        raw = (r.get("reading_mm") or "").strip()
        try:
            v = float(raw)
        except ValueError:
            problems.append(f"{pid}: non-numeric reading '{raw}'")
            continue
        if not np.isfinite(v) or v <= 0:
            problems.append(f"{pid}: non-positive reading {v}")
            continue
        values.setdefault(pid, []).append(v)
        for required in ("instrument_model", "instrument_resolution_mm", "operator", "date"):
            if not (r.get(required) or "").strip():
                problems.append(f"{pid}: missing {required}")
    complete = (len(values) == PLACEMENTS
                and all(len(v) == READINGS_PER_PLACEMENT for v in values.values())
                and not problems)
    return {"complete": bool(complete), "placements": len(values),
            "readings": int(sum(len(v) for v in values.values())),
            "problems": problems[:20], "n_problems": len(problems)}


def reference_mean_and_sd(rows: list[dict]) -> dict:
    vals = []
    for r in rows:
        try:
            vals.append(float((r.get("reading_mm") or "").strip()))
        except ValueError:
            pass
    if not vals:
        return {"n": 0, "mean_mm": float("nan"), "sd_mm": float("nan")}
    a = np.asarray(vals)
    return {"n": int(a.size), "mean_mm": float(a.mean()),
            "sd_mm": float(a.std(ddof=1)) if a.size > 1 else float("nan")}


# -------------------------------------------------------------------------------------- combined U95


def combine_u95(components: dict) -> dict:
    """Root-sum-square combination; any UNKNOWN component makes the result UNKNOWN."""
    known, unknown = {}, []
    for k, v in components.items():
        if v is None or (isinstance(v, float) and not np.isfinite(v)) or v == "UNKNOWN":
            unknown.append(k)
        else:
            known[k] = float(v)
    if unknown:
        return {"u95_mm": "UNKNOWN", "known_components": known, "unknown_components": unknown,
                "reason": "at least one component is UNKNOWN; no combined U95 may be reported"}
    rss = math.sqrt(sum(v ** 2 for v in known.values()))
    return {"u95_mm": float(2.0 * rss), "k": 2.0, "known_components": known,
            "unknown_components": [], "expanded_from_standard": True}


# ---------------------------------------------------------------------------------------- data schema


PLACEMENT_FILES = {
    "raw_depth_z16": "raw/depth/*.raw",
    "raw_color": "raw/color/*.png",
    "camera_intrinsics": "meta/intrinsics.json",
    "camera_configuration": "meta/device_config.json",
    "depth_scale": "meta/depth_scale.json",
    "frame_timestamps": "meta/frame_timestamps.csv",
    "reference_measurements": "reference/reference_measurements.csv",
    "roi_definition": "meta/roi_definition.json",
}


def placement_layout(root: str | Path) -> dict:
    root = Path(root)
    return {f"placement_{i:02d}": {k: str(root / f"placement_{i:02d}" / v)
                                   for k, v in PLACEMENT_FILES.items()}
            for i in range(1, PLACEMENTS + 1)}


def check_placement_dir(path: str | Path) -> dict:
    """Report which required artefacts exist. Never fabricates a file, never marks a missing one OK."""
    p = Path(path)
    out = {}
    for name, rel in PLACEMENT_FILES.items():
        target = p / rel
        if rel.endswith("*.raw") or rel.endswith("*.png"):
            hits = sorted(target.parent.glob(target.name)) if target.parent.exists() else []
            out[name] = {"present": len(hits) > 0, "count": len(hits)}
        else:
            out[name] = {"present": target.exists()}
    out["complete"] = all(v["present"] for v in out.values() if isinstance(v, dict))
    return out
