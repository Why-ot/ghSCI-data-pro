"""Regenerate Table 12 (Spearman rho and two-sided p) from table12_inputs.csv.

    python reproduce_table12.py

Uses scipy.stats.spearmanr, which is what a referee will use. Tested with
scipy 1.x; the p-value follows the t approximation with n-2 degrees of freedom,
which is scipy's default for n > 2. If scipy is absent the script still prints
rho, computed here with average ranks, and says so.
"""

import csv
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(HERE, "table12_inputs.csv")

try:
    from scipy.stats import spearmanr
    HAVE_SCIPY = True
    try:
        import scipy
        SCIPY_VERSION = scipy.__version__
    except Exception:
        SCIPY_VERSION = "unknown"
except ImportError:
    HAVE_SCIPY = False
    SCIPY_VERSION = None


def rank(xs):
    """Average ranks, matching scipy's tie handling."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def rho_only(xs, ys):
    n = len(xs)
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else float("nan")


def test(xs, ys):
    if HAVE_SCIPY:
        res = spearmanr(xs, ys)
        return res.statistic, res.pvalue
    return rho_only(xs, ys), float("nan")


def main():
    if not os.path.exists(INPUT):
        sys.exit(f"missing {INPUT}")
    rows = list(csv.DictReader(open(INPUT, encoding="utf-8")))
    for r in rows:
        r["g"] = float(r["graspness_median"])
        r["b"] = float(r["bias_mm"])

    print(f"n = {len(rows)} rows;  scipy = {SCIPY_VERSION or 'not installed'}")
    print()
    print(f"{'subset':16s} {'n':>3s} {'rho':>8s} {'p':>9s}")
    print("-" * 40)

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
        rho, p = test([r["g"] for r in sub], [r["b"] for r in sub])
        print(f"{name:16s} {len(sub):3d} {rho:8.3f} {p:9.4f}" if p == p
              else f"{name:16s} {len(sub):3d} {rho:8.3f} {'-':>9s}")

    # within-target: remove each target's mean from both variables
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
    rho, p = test(xs, ys)
    print(f"{'within target':16s} {len(xs):3d} {rho:8.3f} {p:9.4f}" if p == p
          else f"{'within target':16s} {len(xs):3d} {rho:8.3f} {'-':>9s}")

    print()
    print("manuscript, for comparison:")
    print("  pooled -0.462, live2 +0.042 (p 0.842), live3 -0.662 (p 0.0003),")
    print("  live_repeat -0.397 (p 0.050), live4_d450 +0.176 (p 0.627),")
    print("  live4_d350 +0.200 (p 0.747), within -0.074 (p 0.489)")
    if not HAVE_SCIPY:
        print()
        print("scipy is not installed here, so the p column is blank; install scipy")
        print("to reproduce it, or compare rho only.")


if __name__ == "__main__":
    main()
