#!/usr/bin/env python3
"""
02_metrology_u95.py
=========================================================================
Turns the filled caliper/micrometer sheets into the numbers the manuscript
is allowed to quote.

Rules enforced here (see 08_量具与实测协议_卡尺版.md):
  * without a calibration certificate the expanded uncertainty is UNKNOWN;
    we still report repeatability s_r, position scatter s_pos and the
    two-method discrepancy |A - B|.
  * resolution contributes u_res = res / sqrt(12) (rectangular assumption).
  * nothing is extrapolated to an absolute distance.

Inputs
    templates/part_thickness_survey.csv      (50 cells x 3 reads)
    templates/reference_step_readings.csv    (25 placements x 3 reads, +checks)

Output
    out/metrology_report.csv  + stdout summary

Usage
    python 02_metrology_u95.py --dir <PAPER_INTAKE_20261104>
"""
import argparse, math, os, sys
import numpy as np
import pandas as pd

RESOLUTION_MM = 0.02          # caliper 0.02 mm; set 0.01 if micrometer is used
TEMP_COEF = 80e-6             # PLA, 1/K (order of magnitude)


def pooled_sd(df, cols):
    """pooled within-cell SD over the three repeat readings"""
    v = df[cols].apply(pd.to_numeric, errors="coerce").values
    ok = ~np.isnan(v).all(axis=1)
    v = v[ok]
    if len(v) == 0:
        return float("nan")
    sd = np.nanstd(v, axis=1, ddof=1)
    sd = sd[~np.isnan(sd)]
    return float(np.sqrt(np.mean(sd ** 2))) if len(sd) else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--resolution", type=float, default=RESOLUTION_MM)
    a = ap.parse_args()

    survey_p = os.path.join(a.dir, "templates", "part_thickness_survey.csv")
    reads_p = os.path.join(a.dir, "templates", "reference_step_readings.csv")
    for p in (survey_p, reads_p):
        if not os.path.exists(p):
            sys.exit("missing: " + p)

    survey = pd.read_csv(survey_p, encoding="utf-8-sig")
    reads = pd.read_csv(reads_p, encoding="utf-8-sig")

    num = ["r1", "r2", "r3"]
    for c in num:
        survey[c] = pd.to_numeric(survey.get(c), errors="coerce")
    if survey[num].isna().all().all():
        print("SURVEY SHEET IS EMPTY -- fill part_thickness_survey.csv first.")
        return 1

    print("== 1. per-part geometry from the thickness survey ==")
    rows = []
    for t, g in survey.groupby("target_id", sort=False):
        s_r = pooled_sd(g, num)
        if t.upper().startswith("S00"):
            # flat control: no step. Report plate thickness + its scatter only.
            thick = float(np.nanmean(g[num].values))
            s_pos = float(np.nanstd(g[num].values.mean(axis=1), ddof=1)) if len(g) > 1 else float("nan")
            rows.append(dict(target_id=t, mean_high_mm=thick, mean_low_mm=float("nan"),
                             step_mm=float("nan"), s_r_mm=s_r, s_pos_mm=s_pos))
            print(f"  {t:5s}  thickness={thick:8.3f} mm (no step by design)"
                  f"   s_r={s_r:5.3f}  s_pos={s_pos:5.3f}")
            continue
        hi = g[g.face.isin(["high", "top"])]
        lo = g[g.face.isin(["low", "bottom"])]
        m_hi = float(np.nanmean(hi[num].values))
        m_lo = float(np.nanmean(lo[num].values))
        step = m_hi - m_lo
        s_pos = float(np.nanstd(hi[num].values.mean(axis=1), ddof=1)) if len(hi) > 1 else float("nan")
        rows.append(dict(target_id=t, mean_high_mm=m_hi, mean_low_mm=m_lo,
                         step_mm=step, s_r_mm=s_r, s_pos_mm=s_pos))
        print(f"  {t:5s}  high={m_hi:8.3f}  low={m_lo:8.3f}  step={step:8.3f} mm"
              f"   s_r={s_r:5.3f}  s_pos={s_pos:5.3f}")
    part = pd.DataFrame(rows)

    print("\n== 2. per-placement readings (the 75 primary readings) ==")
    A = ["mA_r1", "mA_r2", "mA_r3"]
    B = ["mB_r1", "mB_r2", "mB_r3"]
    for c in A + B:
        reads[c] = pd.to_numeric(reads.get(c), errors="coerce")
    if reads[A].isna().all().all():
        print("  placement sheet is empty -- survey numbers above are part-level only.")
        out = os.path.join(a.dir, "analysis", "out")
        os.makedirs(out, exist_ok=True)
        part.to_csv(os.path.join(out, "metrology_report.csv"), index=False)
        print("\nwrote " + os.path.join(out, "metrology_report.csv") + " (part level only)")
        return 0

    reads["mean_A"] = reads[A].mean(axis=1)
    reads["mean_B"] = reads[B].mean(axis=1)
    reads["A_minus_B"] = reads.mean_A - reads.mean_B
    print(reads.groupby("target_id")[["mean_A", "mean_B", "A_minus_B"]]
               .agg(["count", "mean", "std"]).round(3).to_string())

    print("\n== 3. uncertainty budget ==")
    u_res = a.resolution / math.sqrt(12)
    s_r = float(np.nanmean(part.s_r_mm))
    n_rep = 3
    u_rep = s_r / math.sqrt(n_rep)
    uc_known = math.sqrt(u_res ** 2 + u_rep ** 2)
    print(f"  resolution            {a.resolution:.3f} mm -> u_res = {u_res:.4f} mm")
    print(f"  repeatability (pooled) s_r = {s_r:.4f} mm -> u_rep = {u_rep:.4f} mm")
    print(f"  combined (known part)  u_c = {uc_known:.4f} mm   (k=1)")
    print(f"  U95 from known terms   {2*uc_known:.4f} mm   <-- NOT reportable as accuracy")
    print("  calibration term       UNKNOWN (no certificate) -> U95 = UNKNOWN")

    disc = reads.A_minus_B.dropna()
    if len(disc):
        print(f"  two-method discrepancy |A-B|: mean {disc.abs().mean():.3f} mm, max {disc.abs().max():.3f} mm")
        if disc.abs().max() > 0.10:
            print("  *** > 0.10 mm: STOP, re-check seating/perpendicularity (protocol s.6) ***")

    out = os.path.join(a.dir, "analysis", "out")
    os.makedirs(out, exist_ok=True)
    part.to_csv(os.path.join(out, "metrology_report.csv"), index=False)
    print("\nwrote " + os.path.join(out, "metrology_report.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
