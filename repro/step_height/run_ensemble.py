"""Run the step measurement under ten RANSAC seeds and combine them into one ensemble.

A single deterministic seed is still one arbitrary draw: the fitted planes move by
0.02-0.18 mm between draws, and a reported standard deviation moves by more. Ten draws
per unit give a median that is stable and a spread that can be quoted as the pipeline's
own uncertainty.
"""

import csv
import io
import os
import shutil
import statistics as st
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PY = sys.executable
SCRIPT = r"C:\Users\lqx\Desktop\论文\_join\measure_eh.py"
OUT = r"C:\Users\lqx\Desktop\论文\_join\measured_eh.csv"
WORK = r"C:\Users\lqx\Desktop\论文\_join\ensemble"
N = 10

os.makedirs(WORK, exist_ok=True)
runs = []

for k in range(N):
    env = dict(os.environ)
    env["SEED_OFFSET"] = str(k)
    r = subprocess.run([PY, SCRIPT], env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=3600)
    if not os.path.exists(OUT):
        print(f"run {k}: no output\n{r.stderr[-500:]}")
        continue
    dst = os.path.join(WORK, f"run_{k:02d}.csv")
    shutil.copy(OUT, dst)
    runs.append(dst)
    nrow = sum(1 for _ in open(dst, encoding="utf-8")) - 1
    print(f"run {k}: {nrow} rows -> {os.path.basename(dst)}", flush=True)

print(f"\n{N} runs collected; combining ...")

# combine
per = {}
for path in runs:
    for r in csv.DictReader(open(path, encoding="utf-8")):
        key = (r["dataset"], r["unit"], r["part"])
        try:
            v = float(r["e_h_mm"])
        except ValueError:
            v = None
        per.setdefault(key, []).append(v)

rows = []
for (ds, unit, part), vals in sorted(per.items()):
    good = [v for v in vals if v is not None]
    if not good:
        rows.append([ds, unit, part, "", "", "FAIL"])
        continue
    med = st.median(good)
    spread = st.stdev(good) if len(good) > 1 else 0.0
    rows.append([ds, unit, part, round(med, 3), round(spread, 3), "ENSEMBLE"])

ens = os.path.join(WORK, "ensemble_per_unit.csv")
with open(ens, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["dataset", "unit", "part", "e_h_mm", "seed_sd_mm", "flag"])
    w.writerows(rows)

# replace the canonical file with the ensemble so downstream consumers see it
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["dataset", "unit", "part", "e_h_mm", "bias_mm", "nz"])
    for ds, unit, part, med, sd, flag in rows:
        w.writerow([ds, unit, part, med, "", flag])

print(f"ensemble written: {ens}  ({len(rows)} units)")
