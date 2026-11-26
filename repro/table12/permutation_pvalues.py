"""Permutation p values for the graspness versus signed-bias correlations.

    python permutation_pvalues.py

Reads table12_inputs.csv beside this file and reports, for each subset, the
Spearman rho and a two-sided permutation p value. This is the test the manuscript
caption refers to; the analytic p that scipy reports by default is similar but not
identical, which is why the two must not be mixed.

Design choices, stated so a reader can reproduce them:

* one variable is permuted, the other held fixed;
* 100,000 permutations, fixed seed below;
* p = (1 + #{|rho_perm| >= |rho_obs|}) / (1 + N), so the estimate is never exactly
  zero.

Monte-Carlo standard error at p = 0.5 is about 0.0016 at this N, and about
0.0005 at p = 0.05.

The subsets mirror the manuscript table: all usable stepped units, the four capture
runs, and the within-target block obtained by removing each target's mean from both
variables.
"""

import csv
import os
import statistics
import sys

import numpy as np
from scipy.stats import rankdata

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(HERE, "table12_inputs.csv")

N_PERM = 100_000
SEED = 20261126


def spearman(x, y):
    """Spearman rho from average ranks; matches scipy's tie handling."""
    rx = rankdata(x)
    ry = rankdata(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / denom) if denom else float("nan")


def permutation_p(x, y, n_perm=N_PERM, seed=SEED):
    """Two-sided permutation p for a rank correlation, permuting y."""
    rng = np.random.default_rng(seed)
    obs = abs(spearman(x, y))
    xr = rankdata(x)
    xr = xr - xr.mean()
    y0 = np.asarray(y, dtype=float)
    yr = rankdata(y0)
    yr = yr - yr.mean()
    hits = 0
    done = 0
    chunk = 10_000
    while done < n_perm:
        m = min(chunk, n_perm - done)
        Y = np.tile(yr, (m, 1))
        for i in range(m):
            rng.shuffle(Y[i])
        # vectorised cosine of rank vectors equals Spearman
        num = Y @ xr
        den = np.sqrt((Y * Y).sum(axis=1) * (xr * xr).sum())
        hits += int((np.abs(num / den) >= obs - 1e-12).sum())
        done += m
    return obs, (1 + hits) / (1 + done)


def main():
    rows = list(csv.DictReader(open(INPUT, encoding="utf-8")))
    for r in rows:
        r["g"] = float(r["graspness_median"])
        r["b"] = float(r["bias_mm"])

    subsets = [("pooled", rows)]
    for ds in ("live2", "live3", "live_repeat", "live4_d450", "live4_d350"):
        s = [r for r in rows if r["dataset"] == ds]
        if len(s) > 3:
            subsets.append((ds, s))
    for part in ("S20", "S40A", "S40B", "S60"):
        s = [r for r in rows if r["target"] == part]
        if len(s) > 3:
            subsets.append((f"target {part}", s))

    print(f"{N_PERM:,} permutations, seed {SEED}")
    print()
    print(f"{'subset':16s} {'n':>3s} {'rho':>8s} {'perm p':>9s}")
    print("-" * 40)
    for name, sub in subsets:
        rho, p = permutation_p([r["g"] for r in sub], [r["b"] for r in sub])
        print(f"{name:16s} {len(sub):3d} {rho:8.3f} {p:9.4f}")

    # within-target block
    by = {}
    for r in rows:
        by.setdefault(r["target"], []).append(r)
    xs, ys = [], []
    for part, group in by.items():
        mg = statistics.mean(r["g"] for r in group)
        mb = statistics.mean(r["b"] for r in group)
        for r in group:
            xs.append(r["g"] - mg)
            ys.append(r["b"] - mb)
    rho, p = permutation_p(xs, ys)
    print(f"{'within target':16s} {len(xs):3d} {rho:8.3f} {p:9.4f}")


if __name__ == "__main__":
    main()
