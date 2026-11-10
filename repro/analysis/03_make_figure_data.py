#!/usr/bin/env python3
"""
03_make_figure_data.py
=========================================================================
Generates the data tables consumed by the pgfplots figures in manuscript/figures/.
Deliberately dependency-light (pandas + numpy only) so it runs anywhere, and
deliberately boring: every number that appears in a figure can be traced to a
frozen CSV and is written here in plain text.

Inputs   <EXPORT>/CSV/SCI_RESTART_20261008/SCI_STAGE08_P1_CONTINUOUS_E1/results/
           PER_SCENE_SPEARMAN.csv
           SELECTIVE_RISK_CONTINUOUS.csv
         <EXPORT>/CSV/SCI_RESTART_20261008/SCI_STAGE06_P2C_TRANSFER_DIAGNOSIS/results/
           TRANSFER_DIAGNOSIS_RESULTS.csv
Outputs  manuscript/figures/fig3_rho.dat        per method: quartiles + mean + CI
         manuscript/figures/fig3_rho_raw.dat    per method x cell (strip plot)
         manuscript/figures/fig4_selective.dat  coverage curves, two regimes
         manuscript/figures/fig5_exposure.dat   touch rate / exceedance by band

Usage
  python 03_make_figure_data.py \
      --export <PAPER_EVID_...> --out <PAPER_INTAKE_20261104>/manuscript/figures
"""
import argparse, os, sys
import numpy as np
import pandas as pd

CONT = ['F0_gauss6_3mm', 'F0_gauss6_8mm', 'F1_gauss12_3mm', 'F1_gauss20_3mm',
        'F2_disk_r8_3mm', 'F2_square_h8_3mm', 'F3_off4_3mm', 'F3_off8_3mm',
        'F5_dual_3mm']
# ordered for the figure: best to worst on the continuous endpoint
ORDER = ['B5b_p0_risk', 'B2_depth_fluct', 'B3_incidence', 'B5_m2_risk',
         'B1_valid_ratio', 'B0_gsnet', 'B4_margin']
LABEL = {'B5b_p0_risk': 'P0 reliability', 'B2_depth_fluct': 'Depth fluctuation',
         'B3_incidence': 'Incidence', 'B5_m2_risk': 'M2 reliability',
         'B1_valid_ratio': 'Valid ratio', 'B0_gsnet': 'Detector score',
         'B4_margin': 'Contact margin (B4)'}
BOOT = 2000
SEED = 20261104
# Frozen intervals from SCI_STAGE08_P1 .../reports/FINAL_GO_NO_GO.md s.2.
# These are the authoritative numbers quoted in the text; the bootstrap below is
# a cross-check, not a second source of truth.
FROZEN_CI = {
    'B5b_p0_risk':   (+0.151, +0.033, +0.260),
    'B2_depth_fluct': (+0.120, +0.029, +0.220),
    'B3_incidence':  (+0.104, +0.017, +0.188),
    'B5_m2_risk':    (+0.102, -0.006, +0.222),
    'B1_valid_ratio': (+0.040, -0.095, +0.202),
    'B0_gsnet':      (-0.059, -0.160, +0.043),
    'B4_margin':     (-0.103, -0.279, +0.070),
}


def boot_mean_ci(x, rng, n=BOOT):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(n, len(x)))
    m = x[idx].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(SEED)

    p1 = os.path.join(a.export, "CSV", "SCI_RESTART_20261008",
                      "SCI_STAGE08_P1_CONTINUOUS_E1", "results")
    p2 = os.path.join(a.export, "CSV", "SCI_RESTART_20261008",
                      "SCI_STAGE06_P2C_TRANSFER_DIAGNOSIS", "results")

    # ---------------- Fig.3  per-scene rho ---------------------------------
    ps = pd.read_csv(os.path.join(p1, "PER_SCENE_SPEARMAN.csv"))
    ps = ps[ps.condition.isin(CONT)]
    rows, raw = [], []
    for m in ORDER:
        g = ps[ps.method == m]
        v = g.groupby("scene")["spearman"].mean().values      # equal weight per scene
        v = v[~np.isnan(v)]
        lo, hi = boot_mean_ci(v, rng)
        fm, flo, fhi = FROZEN_CI[m]
        assert abs(v.mean() - fm) < 0.002, (m, v.mean(), fm)
        assert abs(lo - flo) < 0.012 and abs(hi - fhi) < 0.012, (m, lo, flo, hi, fhi)
        q1, q3 = np.percentile(v, [25, 75])
        rows.append(dict(method=m, label=LABEL[m], n=len(v), mean=v.mean(),
                         q1=q1, median=np.median(v), q3=q3,
                         whislo=v.min(), whishi=v.max(),
                         ci_lo=flo, ci_hi=fhi,                 # frozen, for the figure
                         ci_lo_boot=lo, ci_hi_boot=hi))        # cross-check only
        for scene, val in zip(g.scene.unique(), v):
            raw.append(dict(method=m, scene=scene, rho=val))
    pd.DataFrame(rows).to_csv(os.path.join(a.out, "fig3_rho.csv"), index=False)
    pd.DataFrame(raw).to_csv(os.path.join(a.out, "fig3_rho_raw.csv"), index=False)

    # ---------------- Fig.4  coverage curves -------------------------------
    sel = pd.read_csv(os.path.join(p1, "SELECTIVE_RISK_CONTINUOUS.csv"))
    base = sel[sel.coverage == 1.0].set_index(["condition", "method"])["mean_E1_mm"]
    recs = []
    for _, r in sel.iterrows():
        b = float(base.loc[(r.condition, r.method)])
        recs.append(dict(condition=r.condition, method=r.method,
                         coverage=float(r.coverage), mean_E1=float(r.mean_E1_mm),
                         delta_mm=float(r.mean_E1_mm) - b,
                         delta_pct=(float(r.mean_E1_mm) - b) / b * 100 if b else np.nan))
    d = pd.DataFrame(recs)
    # regime of each condition from the frozen report: 9 saturated, 4 zero-inflated
    zin = ["F4_tilt4deg", "F4_warp_3mm", "F6_object_neg8mm", "F6_object_pos8mm"]
    d["regime"] = np.where(d.condition.isin(zin), "zero-inflated", "saturated")
    agg = (d.groupby(["regime", "method", "coverage"])
             .agg(delta_mm=("delta_mm", "mean"), n_cond=("condition", "nunique"))
             .reset_index())
    agg.to_csv(os.path.join(a.out, "fig4_selective.csv"), index=False)
    # one file per panel, so the .tex side needs no filtering logic
    agg[agg.regime == "saturated"].to_csv(os.path.join(a.out, "fig4_left.csv"), index=False)
    agg[agg.regime == "zero-inflated"].to_csv(os.path.join(a.out, "fig4_right.csv"), index=False)
    # the headline single-condition case (P0 on F6 -8 mm), for annotation
    p0 = d[(d.method == "B5b_p0_risk") & (d.condition == "F6_object_neg8mm")][
        ["condition", "coverage", "mean_E1", "delta_mm"]]
    p0.to_csv(os.path.join(a.out, "fig4_p0_f6neg.csv"), index=False)

    # ---------------- Fig.5  exposure -------------------------------------
    exp = pd.read_csv(os.path.join(p2, "TRANSFER_DIAGNOSIS_RESULTS.csv"))
    exp.to_csv(os.path.join(a.out, "fig5_exposure.csv"), index=False)

    print("fig3: %d methods, mean rho range %.3f..%.3f"
          % (len(rows), min(r['mean'] for r in rows), max(r['mean'] for r in rows)))
    print("fig4: regimes =", dict(agg.groupby('regime').n_cond.max()))
    print("      saturated  max |delta| at 70%% = %.4f mm"
          % agg[(agg.regime == 'saturated') & (agg.coverage == 0.7)].delta_mm.abs().max())
    print("      zero-infl. max |delta| at 70%% = %.4f mm"
          % agg[(agg.regime == 'zero-inflated') & (agg.coverage == 0.7)].delta_mm.abs().max())
    print("fig5: bands =", list(exp.band.unique()))
    print("wrote", a.out)


if __name__ == "__main__":
    sys.exit(main())
