#!/usr/bin/env python3
"""
07_scorer_decoupling.py
=========================================================================
Answers the second-round review's central demand: show directly that the
scorers predict exposure, and separately that they do (not) predict the
magnitude of the displacement once a candidate is exposed.

Two hypotheses are distinguished:

    H-exposure   s  ->  T            (does the score identify touched candidates?)
    H-magnitude  s  ->  E1 | T=1     (among touched candidates, does it rank size?)

The first was previously only inferred from  T -> 1(E1>5mm); this script measures
it. It also reports the contribution of the unexposed term of Eq. (4), which the
first-round text asserted was negligible on the basis of an exceedance rate
rather than of the expectation itself.

Outputs
    out/scorer_decoupling.csv    per score: AUROC/AP for T, Spearman for E1 and E1|T=1
    out/exposure_terms.csv       P(T=0)E[E1|T=0] and its share of E[E1]

Usage
  python 07_scorer_decoupling.py --root <EXPORT>/CSV/SCI_RESTART_20261008
"""
import argparse, os, sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SCORES = {
    'p0_mean': 'P0 reliability',
    'm2_mean': 'M2 reliability',
    'b0_mean': 'GSNet score',
    'mv_mean': 'Multi-view consistency',
    'score': 'Raw detector score',
}


def auroc(y, s):
    y = np.asarray(y, bool); s = np.asarray(s, float)
    ok = ~np.isnan(s)
    y, s = y[ok], s[ok]
    n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0:
        return np.nan
    r = pd.Series(s).rank().values
    return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def average_precision(y, s):
    y = np.asarray(y, bool); s = np.asarray(s, float)
    ok = ~np.isnan(s); y, s = y[ok], s[ok]
    if y.sum() == 0:
        return np.nan
    order = np.argsort(-s)
    y = y[order]
    hits = np.cumsum(y)
    prec = hits / (np.arange(len(y)) + 1)
    return float((prec * y).sum() / y.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    p = os.path.join(a.root, "SCI_STAGE06_P2C_TRANSFER_DIAGNOSIS", "results",
                     "exposure_and_strata.csv")
    d = pd.read_csv(p)
    d = d[d.any_touch.notna()].copy()
    d["touched"] = d.any_touch.astype(bool)
    print("candidates with a defined exposure label: %d (touched %d, %.2f%%)"
          % (len(d), int(d["touched"].sum()), 100 * d["touched"].mean()))

    # ---------------- 1. s -> T and s -> E1 -----------------------------
    rows = []
    for col, lab in SCORES.items():
        if col not in d:
            continue
        au = auroc(d["touched"], d[col]); apr = average_precision(d["touched"], d[col])
        flags = "  (inverted orientation)" if au == au and au < 0.5 else ""
        au2 = max(au, 1 - au) if au == au else np.nan
        rho_all = spearmanr(d[col], d.E1_mm, nan_policy="omit").correlation
        t1 = d[d["touched"]]
        rho_t1 = spearmanr(t1[col], t1.E1_mm, nan_policy="omit").correlation
        rows.append(dict(score=lab, auroc_T=au2, ap_T=apr, spearman_E1=rho_all,
                         spearman_E1_given_T1=rho_t1, n_touched=len(t1), note=flags.strip()))
    r = pd.DataFrame(rows)
    print("\n== s -> T (exposure) and s -> E1 (magnitude) ==")
    print(r.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    print("\nreading: a score with high AUROC_T and near-zero Spearman(E1|T=1)"
          "\nis an exposure detector, not an error estimator.")

    # ---------------- 2. the two terms of Eq. (4) ------------------------
    p1 = float(d["touched"].mean()); p0 = 1 - p1
    e_all = d.E1_mm.mean()
    e_t1 = d.loc[d["touched"], "E1_mm"].mean()
    e_t0 = d.loc[~d["touched"], "E1_mm"].mean()
    term_t1 = p1 * e_t1
    term_t0 = p0 * e_t0
    terms = pd.DataFrame([dict(term="P(T=1)E[E1|T=1]", value_mm=term_t1,
                               share_pct=100 * term_t1 / e_all),
                          dict(term="P(T=0)E[E1|T=0]", value_mm=term_t0,
                               share_pct=100 * term_t0 / e_all),
                          dict(term="E[E1] (total)", value_mm=e_all, share_pct=100.0)])
    print("\n== contribution of the unexposed term ==")
    print(terms.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("  P(T=0)=%.3f  E[E1|T=0]=%.4f mm  max E1 observed when T=0: %.2f mm"
          % (p0, e_t0, d.loc[~d["touched"], "E1_mm"].max()))

    # ---------------- 3. per-condition touch rate -----------------------
    print("\n== exposure rate by condition (do not quote the pooled 6.07% alone) ==")
    g = (d.groupby("condition")["touched"].agg(["size", "sum", "mean"])
           .rename(columns={"size": "n", "sum": "touched", "mean": "rate"})
           .sort_values("rate", ascending=False))
    print(g.to_string(float_format=lambda x: f"{x:.3f}"))

    os.makedirs(a.out, exist_ok=True)
    r.to_csv(os.path.join(a.out, "scorer_decoupling.csv"), index=False)
    terms.to_csv(os.path.join(a.out, "exposure_terms.csv"), index=False)
    print("\nwrote out/scorer_decoupling.csv, out/exposure_terms.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())

