# Measure step height e_h for every unit, using the same three-plane method as the
# paper (median frame -> back-projection -> sequential RANSAC -> table / low / high).
# Pure numpy + scipy + PIL (no cv2 on this machine).
import os, sys, json, glob, csv
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = r"C:\Users\lqx\Desktop\论文\_r3a_for_pc"
OUT  = r"C:\Users\lqx\Desktop\论文\_join\measured_eh.csv"
REF  = {'S20':19.96, 'S40A':39.97, 'S40B':39.98, 'S60':59.97, 'S00':6.05}
ITER = 800
STRIDE = 3
TOL = 1.5

def median_depth(d):
    fs = sorted(glob.glob(os.path.join(d, 'depth_raw', '*.png')))
    if not fs: return None
    stack = np.stack([np.array(Image.open(f), dtype=np.float32) for f in fs])
    return np.median(stack, axis=0)

def planes(med, K, seed):
    h, w = med.shape
    ys, xs = np.mgrid[0:h:STRIDE, 0:w:STRIDE]
    z = med[ys, xs]; ok = z > 0
    P = np.stack([(xs[ok]-K['ppx'])*z[ok]/K['fx'],
                  (ys[ok]-K['ppy'])*z[ok]/K['fy'], z[ok]], 1)
    rng = np.random.default_rng(seed); out = []; cur = P
    for _ in range(8):
        if len(cur) < 800: break
        best = (-1, None)
        for _ in range(ITER):
            i = rng.choice(len(cur), 3, replace=False)
            q0, q1, q2 = cur[i]
            n = np.cross(q1-q0, q2-q0); nn = np.linalg.norm(n)
            if nn < 1e-9: continue
            n /= nn
            if abs(n[2]) < 0.95: continue
            dd = -float(n @ q0)
            c = int(np.count_nonzero(np.abs(cur @ n + dd) < TOL))
            if c > best[0]: best = (c, (n, dd))
        if best[1] is None: break
        n, dd = best[1]
        inl = np.abs(cur @ n + dd) < TOL
        if inl.sum() < 300: break
        Q = cur[inl]; c0 = Q.mean(0)
        _, _, vt = np.linalg.svd(Q - c0, full_matrices=False)
        n2 = vt[2]/np.linalg.norm(vt[2]); d2 = -float(n2 @ c0)
        if n2[2] < 0: n2, d2 = -n2, -d2
        out.append([n2, d2, int(inl.sum())]); cur = cur[~inl]
    out.sort(key=lambda t: -t[2]); m = []
    for n, dd, c in out:
        if not any(abs(x[1]-dd) < 1.5 for x in m): m.append([n, dd, c])
    return m

def measure(unit_dir, base=None):
    med = median_depth(unit_dir)
    if med is None: return None
    try:
        K = json.load(open(os.path.join(unit_dir, 'meta.json')))['intrinsics']
    except Exception:
        K = {'fx':427.47,'fy':427.47,'ppx':424.16,'ppy':241.38}
    pl = planes(med, K, abs(hash(os.path.basename(unit_dir))) % 997)
    cand = [x for x in pl if 250 <= -x[1] <= 700]
    if not cand: return None
    tab = max(cand, key=lambda x: x[2]); tabd = -tab[1]
    if base is None:
        top = [x for x in pl if tabd-12 <= -x[1] <= tabd-2]
        if not top: return None
        return dict(value=tabd - (-max(top, key=lambda x: x[2])[1]), nz=float(abs(tab[0][2])), table=tabd)
    LOW = tabd - base
    # a step is 20-60 mm by design; allow 14-80 mm of margin so that the gripper
    # or a distant plane cannot be mistaken for the raised face
    hi = [x for x in pl if x[2] >= 400 and (LOW - 80) < -x[1] < (LOW - 14)]
    if not hi: return None
    hp = max(hi, key=lambda x: x[2])
    return dict(value=LOW - (-hp[1]), nz=float(abs(tab[0][2])), table=tabd, low_face=LOW, high=-hp[1])

rows = []
for ds in sorted(os.listdir(ROOT)):
    ddir = os.path.join(ROOT, ds)
    if not os.path.isdir(ddir): continue
    units = sorted(u for u in os.listdir(ddir) if os.path.isdir(os.path.join(ddir, u)))
    # anchor: median base thickness from this session's S00 units
    bases = []
    for u in units:
        if not u.startswith('S00'): continue
        r = measure(os.path.join(ddir, u))
        if r: bases.append(r['value'])
    base = float(np.median(bases)) if bases else 6.05
    print(f"{ds}: S00 n={len(bases)} base={base:.3f}", flush=True)
    for u in units:
        if 'REJECT' in u or u.startswith('TEST'): continue
        part = u.split('_')[0]
        r = measure(os.path.join(ddir, u), None if part == 'S00' else base)
        if r is None:
            rows.append([ds, u, part, '', '', 'FAIL']); continue
        e = r['value']
        ref = REF.get(part, '')
        bias = (e - ref) if ref != '' else ''
        rows.append([ds, u, part, round(e, 3), round(bias, 3) if bias != '' else '', round(r['nz'], 3)])
        print(f"  {u:26s} e_h={e:8.3f} bias={bias:+.3f}", flush=True)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['dataset', 'unit', 'part', 'e_h_mm', 'bias_mm', 'nz'])
    w.writerows(rows)
print("written:", OUT, len(rows), "rows")
