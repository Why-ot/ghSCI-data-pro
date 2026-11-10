# Second, independent implementation of the Section 7 features, with the region of
# interest taken as the convex hull of the raised-face plane rather than as the
# hole-filled inlier set. Used as a robustness check on the definition.
import os, json, glob, csv
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull
from matplotlib.path import Path
from scipy import stats

ROOT = r"C:\Users\lqx\Desktop\论文\_r3a_for_pc"
OUT  = r"C:\Users\lqx\Desktop\论文\_join\expC_hull.csv"
EH   = r"C:\Users\lqx\Desktop\论文\_join\measured_eh.csv"
src  = open(r"C:\Users\lqx\Desktop\论文\_join\expC_recompute.py", encoding="utf-8").read()
g = {}; exec(src.split("eh = {")[0], g)
median_depth, ransac_planes = g['median_depth'], g['ransac_planes']

def hull(shape, pix):
    pts = np.stack([pix[:, 1], pix[:, 0]], 1)
    try:
        h = ConvexHull(pts); poly = pts[h.vertices]
        yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
        return Path(poly).contains_points(np.stack([xx.ravel(), yy.ravel()], 1)).reshape(shape)
    except Exception:
        m = np.zeros(shape, bool); m[pix[:, 0], pix[:, 1]] = True
        return ndi.binary_fill_holes(m)

eh = {(r['dataset'], r['unit']): r for r in csv.DictReader(open(EH, encoding='utf-8'))}
rows = []
for ds, base in (('live2', 5.878), ('live3', 6.117)):
    ddir = os.path.join(ROOT, ds)
    for u in sorted(os.listdir(ddir)):
        d = os.path.join(ddir, u)
        if not os.path.isdir(d) or 'REJECT' in u or u.startswith('TEST') or u.startswith('S00'): continue
        med = median_depth(d)
        if med is None: continue
        K = json.load(open(os.path.join(d, 'meta.json')))['intrinsics']
        pl = ransac_planes(med, K, abs(hash(u)) % 997)
        cand = [p for p in pl if 250 <= -p['d'] <= 700]
        if not cand: continue
        tab = max(cand, key=lambda p: p['count']); LOW = -tab['d'] - base
        hi = [p for p in pl if p['count'] >= 400 and (LOW-80) < -p['d'] < (LOW-14)]
        if not hi: continue
        hp = max(hi, key=lambda p: p['count'])
        hm = hull(med.shape, hp['pix'])
        valid = float(np.mean(med[hm] > 0))
        z = med.copy(); z[z == 0] = np.nan
        mu = ndi.uniform_filter(np.nan_to_num(z, nan=0.0), 5)
        mu2 = ndi.uniform_filter(np.nan_to_num(z**2, nan=0.0), 5)
        sd = np.sqrt(np.maximum(mu2 - mu**2, 0))
        fluct = float(np.median(sd[hm]))
        e = eh.get((ds, u))
        if e is None or e['e_h_mm'] == '': continue
        rows.append(dict(dataset=ds, unit=u, part=e['part'], eh=float(e['e_h_mm']),
                         valid=valid, fluct=fluct, rms=hp['rms']))

with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['dataset', 'unit', 'part', 'eh', 'valid', 'fluct', 'rms'])
    w.writeheader(); w.writerows(rows)

print("written:", OUT, len(rows))
for ds in ('live2', 'live3'):
    S = [r for r in rows if r['dataset'] == ds]
    print(f"--- {ds} (n={len(S)}) ---")
    for c in ('valid', 'fluct', 'rms'):
        x = np.array([r[c] for r in S]); y = np.array([r['eh'] for r in S])
        if np.std(x) == 0:
            print(f"   {c:6s} constant"); continue
        rho, p = stats.spearmanr(x, y)
        print(f"   {c:6s} rho={rho:+.3f}  p={p:.3f}")
