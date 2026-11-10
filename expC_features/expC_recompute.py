# Recompute the three single-frame features of Section 7 (Experiment C) from the raw
# depth frames, with an explicit definition, for both capture sessions.
#
# Definitions used here (and to be stated verbatim in the paper):
#   ROI      the inlier set of the raised-face plane, after closing and filling, so
#            that the valid-fraction denominator is the face itself and not its edges
#   valid    fraction of ROI pixels whose median-frame depth is > 0
#   fluct    median over ROI pixels of the 5x5 depth standard deviation, in mm
#   rms      RMS residual of the ROI points about their own least-squares plane, mm
#
# e_h is taken from measured_eh.csv so that both sessions use one step measurement.
import os, sys, json, glob, csv
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = r"C:\Users\lqx\Desktop\论文\_r3a_for_pc"
OUT  = r"C:\Users\lqx\Desktop\论文\_join\expC_recomputed.csv"
EH   = r"C:\Users\lqx\Desktop\论文\_join\measured_eh.csv"

def median_depth(d):
    fs = sorted(glob.glob(os.path.join(d, 'depth_raw', '*.png')))
    if not fs: return None
    st = np.stack([np.array(Image.open(f), dtype=np.float32) for f in fs])
    return np.median(st, axis=0)

def ransac_planes(z, K, seed=0, iters=1500, stride=3, tol=1.5):
    h, w = z.shape
    ys, xs = np.mgrid[0:h:stride, 0:w:stride]
    zz = z[ys, xs]; ok = zz > 0
    P = np.stack([(xs[ok]-K['ppx'])*zz[ok]/K['fx'],
                  (ys[ok]-K['ppy'])*zz[ok]/K['fy'], zz[ok]], 1)
    idx = np.stack([ys[ok], xs[ok]], 1)
    rng = np.random.default_rng(seed); out = []; cur = P; curi = idx
    for _ in range(6):
        if len(cur) < 800: break
        best = (-1, None)
        for _ in range(iters):
            i = rng.choice(len(cur), 3, replace=False)
            q0, q1, q2 = cur[i]
            n = np.cross(q1-q0, q2-q0); nn = np.linalg.norm(n)
            if nn < 1e-9: continue
            n /= nn
            if abs(n[2]) < 0.95: continue
            d = -float(n @ q0)
            c = int(np.count_nonzero(np.abs(cur @ n + d) < tol))
            if c > best[0]: best = (c, (n, d))
        if best[1] is None: break
        n, d = best[1]
        inl = np.abs(cur @ n + d) < tol
        if inl.sum() < 300: break
        Q = cur[inl]; c0 = Q.mean(0)
        _, _, vt = np.linalg.svd(Q - c0, full_matrices=False)
        n2 = vt[2]/np.linalg.norm(vt[2]); d2 = -float(n2 @ c0)
        if n2[2] < 0: n2, d2 = -n2, -d2
        res = np.abs(Q @ n2 + d2)
        out.append(dict(n=n2, d=d2, count=int(inl.sum()),
                        rms=float(np.sqrt(np.mean(res**2))),
                        pix=curi[inl]))
        keep = ~inl
        cur, curi = cur[keep], curi[keep]
    out.sort(key=lambda t: -t['count']); return out

def features(unit_dir, base):
    med = median_depth(unit_dir)
    if med is None: return None
    K = json.load(open(os.path.join(unit_dir, 'meta.json')))['intrinsics']
    pl = ransac_planes(med, K, abs(hash(os.path.basename(unit_dir))) % 997)
    cand = [p for p in pl if 250 <= -p['d'] <= 700]
    if not cand: return None
    tab = max(cand, key=lambda p: p['count']); tabd = -tab['d']
    LOW = tabd - base
    hi = [p for p in pl if p['count'] >= 400 and (LOW-80) < -p['d'] < (LOW-14)]
    if not hi: return None
    hp = max(hi, key=lambda p: p['count'])

    # ROI: raise the plane inlier pixels to a full mask, then close and fill
    m = np.zeros(med.shape, bool)
    yy, xx = hp['pix'][:, 0], hp['pix'][:, 1]
    m[yy, xx] = True
    m = ndi.binary_closing(m, np.ones((7, 7)))
    m = ndi.binary_fill_holes(m)
    m = ndi.binary_dilation(m, np.ones((3, 3))) & (med > 0)
    m = ndi.binary_fill_holes(m)
    if m.sum() < 200: return None

    valid = float(np.mean(med[m] > 0))
    z = med.copy(); z[z == 0] = np.nan
    mu = ndi.uniform_filter(np.nan_to_num(z, nan=0.0), 5)
    mu2 = ndi.uniform_filter(np.nan_to_num(z**2, nan=0.0), 5)
    sd = np.sqrt(np.maximum(mu2 - mu**2, 0))
    fluct = float(np.median(sd[m]))
    return dict(valid=valid, fluct=fluct, rms=hp['rms'], n=int(m.sum()))

eh = {(r['dataset'], r['unit']): r for r in csv.DictReader(open(EH, encoding='utf-8'))}
rows = []
for ds, base in (('live2', 5.878), ('live3', 6.117)):
    ddir = os.path.join(ROOT, ds)
    units = sorted(u for u in os.listdir(ddir) if os.path.isdir(os.path.join(ddir, u)))
    for u in units:
        if 'REJECT' in u or u.startswith('TEST') or u.startswith('S00'): continue
        f = features(os.path.join(ddir, u), base)
        e = eh.get((ds, u))
        if f is None or e is None or e['e_h_mm'] == '': continue
        rows.append(dict(dataset=ds, unit=u, part=e['part'], eh=float(e['e_h_mm']), **f))
        print(f"{ds:6s} {u:22s} valid={f['valid']:.4f} fluct={f['fluct']:.3f} rms={f['rms']:.3f} n={f['n']}", flush=True)

with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['dataset', 'unit', 'part', 'eh', 'valid', 'fluct', 'rms', 'n'])
    w.writeheader(); w.writerows(rows)
print("written:", OUT, len(rows), "rows")
