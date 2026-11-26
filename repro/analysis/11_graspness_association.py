"""GSNet graspness against the measured step-height bias (Table 13).

    python 11_graspness_association.py

Reads repro/table12/table12_inputs.csv, the 90 frozen units, and reports the Spearman
coefficient for each subset together with a two-sided permutation p value.

The p values use 4000 permutations with seed 0, as stated in the table caption. The
permutation is unconditional: one variable is permuted and the other held fixed. The
caption calls these values descriptive because the sample contains 25 fixed-placement
recaptures and the same physical targets appear in several runs, so the units are not
exchangeable in the strict sense.
"""

import csv
import os
import statistics
import sys

import numpy as np
from scipy.stats import rankdata, spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INPUT = os.path.join(ROOT, "table12", "table12_inputs.csv")

N_PERM = 4000
SEED = 0


def permutation_p(x, y, n_perm=N_PERM, seed=SEED):
    rng = np.random.default_rng(seed)
    xr = rankdata(x)
    xr = xr - xr.mean()
    yr = rankdata(y)
    yr = yr - yr.mean()
    signed = float((xr * yr).sum() / np.sqrt((xr * xr).sum() * (yr * yr).sum()))
    obs = abs(signed)
    hits = 0
    for _ in range(n_perm):
        yp = rng.permutation(yr)
        r = abs(float((xr * yp).sum() / np.sqrt((xr * xr).sum() * (yp * yp).sum())))
        if r >= obs - 1e-12:
            hits += 1
    return signed, (1 + hits) / (1 + n_perm)


def main():
    if not os.path.exists(INPUT):
        sys.exit(f"missing {INPUT}")
    rows = list(csv.DictReader(open(INPUT, encoding="utf-8")))
    for r in rows:
        r["g"] = float(r["graspness_median"])
        r["b"] = float(r["bias_mm"])

    print(f"n = {len(rows)} units; {N_PERM} permutations, seed {SEED}")
    print()
    print(f"{'subset':16s} {'n':>3s} {'rho':>8s} {'p':>9s}")

    subsets = [("pooled", rows)]
    for ds in ("live2", "live3", "live_repeat", "live4_d450", "live4_d350"):
        s = [r for r in rows if r["dataset"] == ds]
        if len(s) > 3:
            subsets.append((ds, s))
    for part in ("S20", "S40A", "S40B", "S60"):
        s = [r for r in rows if r["target"] == part]
        if len(s) > 3:
            subsets.append((f"target {part}", s))

    for name, sub in subsets:
        rho, p = permutation_p([r["g"] for r in sub], [r["b"] for r in sub])
        pstr = "<0.001" if p < 0.001 else f"{p:.3f}"
        print(f"{name:16s} {len(sub):3d} {rho:8.3f} {pstr:>9s}")

    by = {}
    for r in rows:
        by.setdefault(r["target"], []).append(r)
    xs, ys = [], []
    for _, group in by.items():
        mg = statistics.mean(r["g"] for r in group)
        mb = statistics.mean(r["b"] for r in group)
        for r in group:
            xs.append(r["g"] - mg)
            ys.append(r["b"] - mb)
    rho, p = permutation_p(xs, ys)
    pstr = "<0.001" if p < 0.001 else f"{p:.3f}"
    print(f"{'within target':16s} {len(xs):3d} {rho:8.3f} {pstr:>9s}")

    # absolute error, for the sensitivity table of the main text
    for r in rows:
        r["ab"] = abs(r["b"])
    a90 = spearmanr([r["g"] for r in rows], [r["ab"] for r in rows]).statistic
    repl = [r for r in rows if r["dataset"] in ("live2", "live3")]
    a50 = spearmanr([r["g"] for r in repl], [r["ab"] for r in repl]).statistic
    print()
    print(f"absolute error |e_h|: pooled {a90:+.3f}, re-placed {a50:+.3f}")


if __name__ == "__main__":
    main()
