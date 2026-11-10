#!/usr/bin/env python3
"""
01_selective_risk_split.py
=========================================================================
Reproduces, from the frozen Stage08-P1 tables, the two-sided selective-risk
result quoted in the manuscript (section 5.3 and the abstract).

Why this script exists
----------------------
The frozen report states "all |delta| <= 0.016 mm at 70 % coverage" without
stating that this holds only for the exposure-saturated conditions. Recomputing
per condition family shows a second regime in which the *same* scorer halves
the mean error. Both numbers must appear together, with the zero fraction.

Inputs (read-only, from the evidence export)
    .../SCI_STAGE08_P1_CONTINUOUS_E1/results/SELECTIVE_RISK_CONTINUOUS.csv
    .../SCI_STAGE08_P1_CONTINUOUS_E1/results/p1_eval_table.csv

Outputs
    out/selective_risk_by_family.csv   one row per condition x method
    stdout                             the summary table used in the paper

Run
    python 01_selective_risk_split.py --root <PAPER_EVID_...>/CSV/SCI_RESTART_20261008
"""
import argparse, os, sys
import pandas as pd

COVS = [0.5, 0.7, 0.9, 1.0]
FAMILY_TOL = 1e-9


def classify(zero_frac):
    if zero_frac <= FAMILY_TOL:
        return "SATURATED"          # exposure saturated: every displacement > 0
    if zero_frac >= 1 - FAMILY_TOL:
        return "DEGENERATE"         # every displacement == 0
    return "ZERO_INFLATED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="out")
    a = ap.parse_args()

    res = os.path.join(a.root, "SCI_STAGE08_P1_CONTINUOUS_E1", "results")
    sel_p = os.path.join(res, "SELECTIVE_RISK_CONTINUOUS.csv")
    ev_p = os.path.join(res, "p1_eval_table.csv")
    for p in (sel_p, ev_p):
        if not os.path.exists(p):
            sys.exit("missing input: " + p)

    sel = pd.read_csv(sel_p)
    ev = pd.read_csv(ev_p)

    # --- 1. zero fraction per condition, straight from the candidate table ----
    zf = (ev.groupby("condition")["E1_mm"]
            .apply(lambda s: float((s == 0).mean()))
            .rename("zero_frac")
            .reset_index())
    zf["family"] = zf.zero_frac.map(classify)

    # --- 2. delta at each coverage versus full coverage -----------------------
    base = sel[sel.coverage == COVS[-1]].set_index(["condition", "method"])["mean_E1_mm"]
    rows = []
    for cov in COVS[:-1]:
        sub = sel[sel.coverage == cov]
        for _, r in sub.iterrows():
            b = float(base.loc[(r.condition, r.method)])
            rows.append(dict(condition=r.condition, method=r.method, coverage=cov,
                             mean_E1_mm=float(r.mean_E1_mm), base_E1_mm=b,
                             delta_mm=float(r.mean_E1_mm) - b,
                             delta_pct=(float(r.mean_E1_mm) - b) / b * 100.0 if b else float("nan")))
    d = pd.DataFrame(rows).merge(zf, on="condition", how="left")
    os.makedirs(a.out, exist_ok=True)
    d.to_csv(os.path.join(a.out, "selective_risk_by_family.csv"), index=False)

    # --- 3. the numbers quoted in the paper ----------------------------------
    print("zero fraction per condition")
    print(zf.sort_values(["family", "zero_frac"]).to_string(index=False))

    print("\n|delta mean E1| at 70 % coverage, by family")
    q = d[d.coverage == 0.7]
    g = (q.assign(absdelta=q.delta_mm.abs())
           .groupby("family")
           .agg(pairs=("absdelta", "size"), max_abs_mm=("absdelta", "max"),
                max_abs_pct=("delta_pct", lambda s: s.abs().max()),
                min_base_mm=("base_E1_mm", "min"), max_base_mm=("base_E1_mm", "max"))
           .round(4))
    print(g.to_string())

    sat = q[q.family == "SATURATED"]
    zin = q[q.family == "ZERO_INFLATED"]
    worst = q.loc[q.delta_mm.abs().idxmax()]
    print("\nclaims to check against the manuscript")
    print("  saturated  : max |delta| = %.4f mm, %d/%d pairs <= 0.016 mm"
          % (sat.delta_mm.abs().max(), int((sat.delta_mm.abs() <= 0.016).sum()), len(sat)))
    print("  zero-infl. : max |delta| = %.4f mm (%.1f %%), %s on %s"
          % (zin.delta_mm.abs().max(), zin.loc[zin.delta_mm.abs().idxmax()].delta_pct,
             zin.loc[zin.delta_mm.abs().idxmax()].method, zin.loc[zin.delta_mm.abs().idxmax()].condition))
    print("  overall    : %s on %s, %.4f mm (%.1f %%)"
          % (worst.method, worst.condition, worst.delta_mm, worst.delta_pct))

    # hard assertions: if the frozen tables ever change, fail loudly
    assert sat.delta_mm.abs().max() <= 0.017, "saturated regime changed"
    assert zin.delta_mm.abs().max() >= 1.0, "zero-inflated regime changed"
    print("\nOK  wrote " + os.path.join(a.out, "selective_risk_by_family.csv"))


if __name__ == "__main__":
    main()
