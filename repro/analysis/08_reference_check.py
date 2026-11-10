#!/usr/bin/env python3
"""
08_reference_check.py
=========================================================================
Day-1 acceptance test for the R3-A reference chain.

Reads the filled measurement sheet and answers three questions before any depth
frame is captured:

    1. Is the operator repeatable?      (range over 3 repeats, per position)
    2. Do the two ways of getting the step agree?
         a) step = total height - base thickness
         b) step = depth-rod reading across the step
    3. Is the reference good enough to resolve the effect we care about?

The verdict is deliberately conservative: a reference that fails here is not
"approximately fine", it is unusable, because every downstream claim inherits
its error.

Usage
    python 08_reference_check.py --csv templates/day1_reference_measurements.csv
    python 08_reference_check.py --csv ... --nominal 20 40 60 --resolution 0.01
"""
import argparse, os, sys
import numpy as np
import pandas as pd

NOMINAL = {'S00': 0.0, 'S20': 20.0, 'S40A': 40.0, 'S40B': 40.0, 'S60': 60.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--resolution", type=float, default=0.01,
                    help="instrument resolution in mm (caliper/depth rod)")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()

    d = pd.read_csv(a.csv)
    d["reading_mm"] = pd.to_numeric(d["reading_mm"], errors="coerce")
    n_filled = d["reading_mm"].notna().sum()
    print("rows: %d | filled: %d (%.0f%%)" % (len(d), n_filled, 100 * n_filled / len(d)))
    if n_filled == 0:
        print("\nNothing measured yet - fill reading_mm in the CSV and rerun.")
        return 0
    parts = [p for p in d["part"].unique() if d.loc[d.part == p, "reading_mm"].notna().any()]
    print("parts with data:", ", ".join(parts))

    # ---------------- 1. repeatability -----------------------------------
    g = (d.dropna(subset=["reading_mm"])
           .groupby(["part", "method", "position_id"])["reading_mm"]
           .agg(["count", "mean", "min", "max", "std"])
           .reset_index())
    g["range"] = g["max"] - g["min"]
    g["n_rep"] = g["count"]
    short = g[g["n_rep"] < 3]
    if len(short):
        print("\nWARNING: positions with fewer than 3 repeats: %d" % len(short))
        print(short[["part", "method", "position_id", "n_rep"]].to_string(index=False))

    print("\n== repeatability by method (range over repeats, mm) ==")
    rep = (g.groupby(["part", "method"])["range"]
             .agg(median="median", worst="max", n_positions="size")
             .reset_index())
    print(rep.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    worst = rep["worst"].max() if len(rep) else np.nan

    # ---------------- 2. the two step estimates --------------------------
    print("\n== step height: subtraction vs direct ==")
    rows = []
    for p in parts:
        sub = d[(d.part == p) & d.reading_mm.notna()]
        th = sub[sub.method == "caliper_thickness"]["reading_mm"]
        to = sub[sub.method == "caliper_total_height"]["reading_mm"]
        di = sub[sub.method == "caliper_step_direct"]["reading_mm"]
        got = {}
        if len(th) and len(to):
            got["by_subtraction"] = to.mean() - th.mean()
        if len(di):
            got["direct"] = di.mean()
        if not got:
            continue
        row = dict(part=p, nominal=NOMINAL.get(p, np.nan), **got)
        if len(got) == 2:
            row["difference"] = got["direct"] - got["by_subtraction"]
        rows.append(row)
    s = pd.DataFrame(rows)
    if len(s):
        print(s.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
        for _, r in s.iterrows():
            dev = [abs(r[k] - r["nominal"]) for k in ("by_subtraction", "direct") if k in r and pd.notna(r[k])]
            if dev:
                print("  %-5s |measured - nominal| = %.3f mm" % (r["part"], max(dev)))
        if "difference" in s:
            dd = s["difference"].dropna()
            if len(dd):
                print("\n  subtraction-vs-direct disagreement: median %.3f mm, max %.3f mm"
                      % (dd.abs().median(), dd.abs().max()))
    else:
        print("  not enough data for a step estimate yet")

    # ---------------- 3. budget and verdict ------------------------------
    u_res = a.resolution / np.sqrt(12)          # uniform quantisation, type B
    u_rep = (worst / 2) / np.sqrt(3) if pd.notna(worst) else np.nan   # half-range -> sd (uniform)
    u_comb = float(np.sqrt(u_res ** 2 + (u_rep if pd.notna(u_rep) else 0) ** 2))
    U = 2 * u_comb
    print("\n== reference budget (partial: resolution + repeatability only) ==")
    print("  u_resolution      %.4f mm" % u_res)
    print("  u_repeatability   %.4f mm  (from worst half-range %.3f mm)" % (u_rep, worst))
    print("  u_combined        %.4f mm" % u_comb)
    print("  U (k=2)           %.4f mm" % U)
    print("  not yet included: temperature, operator, instrument calibration,")
    print("                    parallelism of the two faces")

    print("\n================ VERDICT ================")
    if pd.isna(worst):
        print("INCOMPLETE - no repeated readings")
    elif worst <= 0.03:
        print("GOOD      - repeatability %.3f mm; supports ~0.1 mm claims" % worst)
    elif worst <= 0.10:
        print("MARGINAL  - repeatability %.3f mm; claims limited to ~0.3 mm" % worst)
    else:
        print("FAIL      - repeatability %.3f mm; re-check technique/clamping" % worst)
        print("            do not start depth capture")
    if pd.notna(U):
        print("Reference U(k=2) so far: %.3f mm -> software-control target 2 mm is %s"
              % (U, "resolvable" if U < 0.5 else "NOT resolvable"))
    print("=========================================")

    os.makedirs(a.out, exist_ok=True)
    g.to_csv(os.path.join(a.out, "reference_repeatability.csv"), index=False)
    if len(s):
        s.to_csv(os.path.join(a.out, "reference_steps.csv"), index=False)
    print("\nwrote out/reference_repeatability.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
