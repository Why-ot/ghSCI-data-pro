"""Table 15: treatment of candidates without a finite paired displacement.

    python 12_invalid_displacement_conventions.py

Reads the candidate-level table
repro/evidence/CSV/SCI_RESTART_20261008/SCI_STAGE06_P2C_TRANSFER_DIAGNOSIS/results/exposure_and_strata.csv
and reports the exceedance rate of the 5 mm displacement threshold under the three
conventions used in the paper:

  (a) a candidate without a finite displacement is counted as not exceeding,
  (b) such candidates are dropped from the denominator,
  (c) they are counted as exceeding.

The exposed/unexposed split is the `any_touch` column; the displacement is `E1_mm`.
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(
    ROOT, "evidence", "CSV", "SCI_RESTART_20261008",
    "SCI_STAGE06_P2C_TRANSFER_DIAGNOSIS", "results", "exposure_and_strata.csv",
)
THRESHOLD = 5.0


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

    exposed = [r for r in rows if r.get("any_touch") == "True"]
    untouched = [r for r in rows if r.get("any_touch") == "False"]

    def finite(group):
        return [r for r in group if value(r, "E1_mm") is not None]

    def exceed(group):
        return sum(1 for r in group if (value(r, "E1_mm") or -1) > THRESHOLD)

    print(f"candidates with an exposure label: {len(exposed) + len(untouched)}")
    print(f"  exposed {len(exposed)}, untouched {len(untouched)}")
    print(f"  no finite displacement: exposed {len(exposed) - len(finite(exposed))},"
          f" untouched {len(untouched) - len(finite(untouched))}")
    print()

    ee, eu = exceed(exposed), exceed(untouched)
    fe, fu = finite(exposed), finite(untouched)
    ie, iu = len(exposed) - len(fe), len(untouched) - len(fu)

    print(f"{'convention':34s} {'exposed':>18s} {'untouched':>18s}")
    print("-" * 74)
    print(f"{'(a) counted as not exceeding':34s} "
          f"{ee:4d}/{len(exposed):<4d}={100*ee/len(exposed):6.2f}% "
          f"{eu:4d}/{len(untouched):<5d}={100*eu/len(untouched):6.3f}%")
    print(f"{'(b) dropped from the denominator':34s} "
          f"{ee:4d}/{len(fe):<4d}={100*ee/len(fe):6.2f}% "
          f"{eu:4d}/{len(fu):<5d}={100*eu/len(fu):6.3f}%")
    print(f"{'(c) counted as exceeding':34s} "
          f"{ee+ie:4d}/{len(exposed):<4d}={100*(ee+ie)/len(exposed):6.2f}% "
          f"{eu+iu:4d}/{len(untouched):<5d}={100*(eu+iu)/len(untouched):6.3f}%")


if __name__ == "__main__":
    main()
