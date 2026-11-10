#!/usr/bin/env python3
"""
06_paired_contrasts.py
=========================================================================
Recomputes the scene-level paired contrasts of Section V-B directly from the
frozen per-scene table, and documents why the older frozen file is superseded.

Background
  SCI_STAGE08_P1 .../B4_PAIRED_CONTRASTS.csv reports contrasts that are
  systematically 1/4 of the values implied by PER_SCENE_SPEARMAN.csv:
  e.g. B4-P0 = -0.0638 there, while the difference of the two reported means is
  -0.103 - 0.151 = -0.254 and the scene-by-scene mean difference is also -0.254.
  A constant factor over all six contrasts points at an aggregation bug, not at
  rounding. This script prints both so the discrepancy is auditable.

Outputs
  stdout                       the two tables side by side
  out/paired_contrasts.csv     the values used in the paper

Usage
  python 06_paired_contrasts.py --root <EXPORT>/CSV/SCI_RESTART_20261008
"""
import argparse, os, sys
import numpy as np
import pandas as pd

CONT = ['F0_gauss6_3mm', 'F0_gauss6_8mm', 'F1_gauss12_3mm', 'F1_gauss20_3mm',
        'F2_disk_r8_3mm', 'F2_square_h8_3mm', 'F3_off4_3mm', 'F3_off8_3mm',
        'F5_dual_3mm']
OTHERS = ['B0_gsnet', 'B1_valid_ratio', 'B2_depth_fluct', 'B3_incidence',
          'B5_m2_risk', 'B5b_p0_risk']
SEED = 20261104


def boot_ci(x, rng, n=10000):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(n, len(x)))
    return tuple(np.percentile(x[idx].mean(axis=1), [2.5, 97.5]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    res = os.path.join(a.root, "SCI_STAGE08_P1_CONTINUOUS_E1", "results")
    ps = pd.read_csv(os.path.join(res, "PER_SCENE_SPEARMAN.csv"))
    frozen = pd.read_csv(os.path.join(res, "B4_PAIRED_CONTRASTS.csv")).set_index("contrast")["mean_delta"]

    sc = (ps[ps.condition.isin(CONT)]
          .groupby(["scene", "method"])["spearman"].mean().unstack())
    rng = np.random.default_rng(SEED)

    rows = []
    for m in OTHERS:
        d = sc["B4_margin"] - sc[m]
        lo, hi = boot_ci(d, rng)
        key = "B4_minus_" + m
        fz = float(frozen.get(key, np.nan))
        rows.append(dict(contrast=key, mean=d.mean(), ci_low=lo, ci_high=hi,
                         frozen=fz, ratio=fz / d.mean() if d.mean() else np.nan,
                         superseded=abs(fz - d.mean()) > 0.01))
    d = pd.DataFrame(rows)

    print("scenes: %d | conditions: %d" % (len(sc), len(CONT)))
    print("\n%-26s %8s  %-20s %8s %6s" % ("contrast", "mean", "bootstrap 95%", "frozen", "ratio"))
    for _, r in d.iterrows():
        print("%-26s %+8.4f  [%+.4f, %+.4f]  %+8.4f %6.2f%s"
              % (r.contrast, r["mean"], r.ci_low, r.ci_high, r.frozen, r.ratio,
                 "  <-- superseded" if r.superseded else ""))

    print("\nmeans: B4 %+0.4f | P0 %+0.4f | difference %+0.4f"
          % (sc["B4_margin"].mean(), sc["B5b_p0_risk"].mean(),
             sc["B4_margin"].mean() - sc["B5b_p0_risk"].mean()))

    os.makedirs(a.out, exist_ok=True)
    d.to_csv(os.path.join(a.out, "paired_contrasts.csv"), index=False)
    print("\nwrote " + os.path.join(a.out, "paired_contrasts.csv"))

    # a factor near 1/4 for every row is the signature of the aggregation bug
    assert (d.ratio.round(1) == 0.3).sum() + (d.ratio.round(1) == 0.2).sum() >= 5, \
        "the 1/4 pattern changed - re-read the frozen file before citing anything"
    return 0


if __name__ == "__main__":
    sys.exit(main())
