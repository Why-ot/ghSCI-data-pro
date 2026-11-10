# Join the GSNet graspness features (PC side) with the step-height error measured
# here, and test whether graspness predicts the measured error.
#
# Inputs
#   measured_eh.csv             dataset, unit, part, e_h_mm, bias_mm, nz   (this machine)
#   03_graspness_per_unit.csv   dataset, condition, unit, ..., g_median, ...  (PC)
# Output
#   joined.csv, report.txt
import os, csv, json, sys
import numpy as np

D    = r"C:\Users\lqx\Desktop\论文\_join"
EH   = os.path.join(D, 'measured_eh.csv')
GR   = os.path.join(D, '03_graspness_per_unit.csv')
REF  = {'S20':19.96, 'S40A':39.97, 'S40B':39.98, 'S60':59.97}
OUTJ = os.path.join(D, 'joined.csv')
REP  = os.path.join(D, 'report.txt')

def spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 4: return float('nan')
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean(); ry -= ry.mean()
    den = np.sqrt((rx**2).sum() * (ry**2).sum())
    return float((rx*ry).sum()/den) if den > 0 else float('nan')

def perm_p(x, y, n=4000, seed=0):
    r0 = spearman(x, y)
    if not np.isfinite(r0): return float('nan')
    y = np.asarray(y, float); rng = np.random.default_rng(seed); c = 0
    for _ in range(n):
        if abs(spearman(x, rng.permutation(y))) >= abs(r0): c += 1
    return (c+1)/(n+1)

eh = {}
with open(EH, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        eh[(r['dataset'], r['unit'])] = r

rows = []
missing = 0
with open(GR, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        k = (r['dataset'], r['unit'])
        e = eh.get(k)
        if e is None or e['e_h_mm'] == '':
            missing += 1; continue
        part = e['part']
        e_h = float(e['e_h_mm'])
        valid = part in REF and abs(e_h - REF[part]) < 10.0   # drop units whose face was not captured
        rows.append(dict(dataset=r['dataset'], unit=r['unit'], part=part,
                         e_h=e_h, valid=int(valid),
                         g_median=float(r['g_median']), g_p90=float(r['g_p90']),
                         g_mean=float(r['g_mean']), n_pix=int(float(r['n_pix'])),
                         plane_rms=float(r['plane_rms_mm'])))

with open(OUTJ, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

L = []
def say(s):
    L.append(s); print(s)

say(f"joined rows: {len(rows)} (unmatched in measurement: {missing})")
say(f"valid stepped units: {sum(r['valid'] for r in rows)}")
say("")
V = [r for r in rows if r['valid']]
say("=== pooled over valid stepped units ===")
for feat in ('g_median', 'g_p90', 'g_mean'):
    x = [r[feat] for r in V]; y = [r['e_h'] for r in V]
    say(f"  rho({feat}, e_h) = {spearman(x,y):+.3f}  p_perm = {perm_p(x,y,2000):.3f}  n = {len(x)}")

say("")
say("=== within dataset ===")
for ds in sorted({r['dataset'] for r in V}):
    S = [r for r in V if r['dataset'] == ds]
    if len(S) < 5: 
        say(f"  {ds:12s} n={len(S)} (too few)"); continue
    x = [r['g_median'] for r in S]; y = [r['e_h'] for r in S]
    say(f"  {ds:12s} n={len(S):2d}  rho(g_median, e_h) = {spearman(x,y):+.3f}  p = {perm_p(x,y,1500):.3f}")

say("")
say("=== within condition (n=5 each) ===")
for ds in sorted({r['dataset'] for r in V}):
    conds = sorted({r['part'] for r in V if r['dataset'] == ds})
    for c in conds:
        S = [r for r in V if r['dataset'] == ds and r['part'] == c]
        if len(S) < 5: continue
        x = [r['g_median'] for r in S]; y = [r['e_h'] for r in S]
        say(f"  {ds:12s} {c:5s} n={len(S)}  rho = {spearman(x,y):+.3f}")

say("")
say("=== spread of g_median within dataset (is it discriminative?) ===")
for ds in sorted({r['dataset'] for r in rows}):
    v = [r['g_median'] for r in rows if r['dataset'] == ds]
    say(f"  {ds:12s} n={len(v):2d}  min={min(v):.3f}  max={max(v):.3f}  spread={max(v)-min(v):.3f}")

open(REP, 'w', encoding='utf-8').write("\n".join(L))
print("\nwritten:", REP)
