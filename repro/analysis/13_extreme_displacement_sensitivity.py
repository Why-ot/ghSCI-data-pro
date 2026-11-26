"""Table 16: robustness of the conditional displacement ranking.

    python 13_extreme_displacement_sensitivity.py

Restricted to candidates with an exposed contact region and a finite displacement,
this script correlates each score with the displacement E1 under three subsets:

  all                  - every such candidate,
  E1 <= 1000 mm        - removes the heavy tail,
  two scenes removed   - removes scene_0086 and scene_0087, which carry the
                         local-tilt outliers.

Score columns are those of the candidate-level table. The signs are the raw ones
recorded in that table; the paper reports them without flipping.
"""

import csv
import os
import sys

from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(
    ROOT, "evidence", "CSV", "SCI_RESTART_20261008",
    "SCI_STAGE06_P2C_TRANSFER_DIAGNOSIS", "results", "exposure_and_strata.csv",
)
SCORES = [
    ("p0_mean", "P0"),
    ("m2_mean", "M2"),
    ("mv_mean", "Multi-view"),
    ("b0_mean", "GSNet"),
    ("score", "Detector"),
]


def value(r, key):
    v = (r.get(key) or "").strip()
    if not v:
        return None
    try:
        x = float(v)
    except ValueError:
        return None
    return x if x == x and abs(x) != float("inf") else None


def main():
    if not os.path.exists(CSV):
        sys.exit(f"missing {CSV}")
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    exposed = [r for r in rows
               if r.get("any_touch") == "True" and value(r, "E1_mm") is not None]

    subsets = [
        ("all", exposed),
        ("E1<=1000", [r for r in exposed if value(r, "E1_mm") <= 1000]),
        ("no 0086/87", [r for r in exposed
                        if r.get("scene") not in ("scene_0086", "scene_0087")]),
    ]

    print(f"exposed with finite displacement: {len(exposed)}")
    print("  " + ", ".join(f"{n}: {len(s)}" for n, s in subsets))
    print()

    header = "".join(f"{n:>18s}" for n, _ in subsets)
    print(f"{'score':12s}{header}")
    for col, label in SCORES:
        cells = []
        for _, sub in subsets:
            pairs = [(value(r, col), value(r, "E1_mm")) for r in sub]
            pairs = [(a, b) for a, b in pairs if a is not None]
            r = spearmanr([a for a, _ in pairs], [b for _, b in pairs])
            p = "<0.001" if r.pvalue < 0.001 else f"{r.pvalue:.3f}"
            cells.append(f"{r.statistic:+.3f} ({p})")
        print(f"{label:12s}" + "".join(f"{c:>18s}" for c in cells))


if __name__ == "__main__":
    main()
