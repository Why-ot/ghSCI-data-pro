"""Sensitivity of the graspness coefficients to the step-height estimator.

    python estimator_sensitivity.py

Reads estimator_comparison.csv beside this file: the same 90 units, with the step
height taken from the single frozen realisation (`joined`) and from the ten-draw
ensemble mean (`ensemble`), and the resulting signed biases.

Reports the pooled and within-target Spearman coefficients under both estimators, and
the distribution of the per-unit difference between them. This is the evidence behind
the sentence in Supplementary Section S6.
"""

import csv
import os
import statistics
import sys

from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "estimator_comparison.csv")


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    for r in rows:
        r["g"] = float(r["graspness_median"])
        r["bj"] = float(r["bias_joined_mm"])
        r["be"] = float(r["bias_ensemble_mm"])
        r["d"] = float(r["difference_mm"])

    print(f"n = {len(rows)} units")
    print()
    print(f"{'':22s} {'joined':>9s} {'ensemble':>9s}")
    pj = spearmanr([r["g"] for r in rows], [r["bj"] for r in rows]).statistic
    pe = spearmanr([r["g"] for r in rows], [r["be"] for r in rows]).statistic
    print(f"{'pooled rho':22s} {pj:9.3f} {pe:9.3f}")

    by = {}
    for r in rows:
        by.setdefault(r["target"], []).append(r)
    xs_j, ys_j, xs_e, ys_e = [], [], [], []
    for _, group in by.items():
        mg = statistics.mean(r["g"] for r in group)
        mbj = statistics.mean(r["bj"] for r in group)
        mbe = statistics.mean(r["be"] for r in group)
        for r in group:
            xs_j.append(r["g"] - mg)
            ys_j.append(r["bj"] - mbj)
            xs_e.append(r["g"] - mg)
            ys_e.append(r["be"] - mbe)
    wj = spearmanr(xs_j, ys_j).statistic
    we = spearmanr(xs_e, ys_e).statistic
    print(f"{'within-target rho':22s} {wj:9.3f} {we:9.3f}")

    d = [abs(r["d"]) for r in rows]
    print()
    print("per-unit |difference| / mm")
    print(f"  mean   {statistics.mean(d):6.3f}")
    print(f"  median {statistics.median(d):6.3f}")
    print(f"  max    {max(d):6.3f}")
    d450 = [abs(r["d"]) for r in rows if r["dataset"] == "live4_d450"]
    if d450:
        print(f"  448 mm group mean {statistics.mean(d450):6.3f}")

    biggest = sorted(rows, key=lambda r: -abs(r["d"]))[:5]
    print()
    print("five largest differences:")
    for r in biggest:
        print(f"  {r['dataset']:14s} {r['unit']:24s} joined {float(r['e_h_joined_mm']):8.3f}"
              f"  ensemble {float(r['e_h_ensemble_mm']):8.3f}  diff {r['d']:>8}")


if __name__ == "__main__":
    main()
