#!/usr/bin/env python3
"""
plane_check.py -- 米制空间里分平面并验证台阶（v2）

v1 的错误：直接用 (u, v, Z) 拟合平面。像素坐标不是长度，法向和偏移都没有
几何意义，算出来的"台阶"是假的。v2 先用内参反投影到相机系（毫米）。

用法
    python3 plane_check.py <放置目录> [tol_mm]
"""
import sys, os, glob, json
import numpy as np
import cv2


def load(folder):
    fs = sorted(glob.glob(os.path.join(folder, 'depth_raw', '*.png')))
    if not fs:
        raise SystemExit('no depth frames in %s' % folder)
    st = np.stack([cv2.imread(f, cv2.IMREAD_UNCHANGED) for f in fs]).astype(np.float32)
    med = np.median(st, axis=0)
    sd = np.nanstd(np.where(st > 0, st, np.nan), axis=0)
    meta = {}
    mp = os.path.join(folder, 'meta.json')
    if os.path.exists(mp):
        meta = json.load(open(mp, encoding='utf-8'))
    return med, sd, len(fs), meta


def backproject(depth_mm, K, stride=3):
    """返回 Nx3 的相机系坐标（毫米）：X 右、Y 下、Z 沿光轴。"""
    h, w = depth_mm.shape
    ys, xs = np.mgrid[0:h:stride, 0:w:stride]
    z = depth_mm[ys, xs]
    m = z > 0
    xs, ys, z = xs[m].astype(np.float64), ys[m].astype(np.float64), z[m].astype(np.float64)
    X = (xs - K['ppx']) * z / K['fx']
    Y = (ys - K['ppy']) * z / K['fy']
    return np.stack([X, Y, z], axis=1)


def fit_plane(P):
    c = P.mean(axis=0)
    _, _, vt = np.linalg.svd(P - c, full_matrices=False)
    n = vt[2]
    n = n / np.linalg.norm(n)
    d = -float(np.dot(n, c))
    if d > 0:                      # 统一符号：让 d < 0，便于比较
        n, d = -n, -d
    return n, d


def ransac(P, tol, iters, rng):
    best_cnt, best = -1, None
    for _ in range(iters):
        p0, p1, p2 = P[rng.choice(len(P), 3, replace=False)]
        n = np.cross(p1 - p0, p2 - p0)
        nn = np.linalg.norm(n)
        if nn < 1e-9:
            continue
        n /= nn
        d = -float(np.dot(n, p0))
        cnt = int(np.count_nonzero(np.abs(P @ n + d) < tol))
        if cnt > best_cnt:
            best_cnt, best = cnt, (n, d)
    return best


def main():
    folder = sys.argv[1]
    tol = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
    med, sd, nf, meta = load(folder)
    K = (meta.get('intrinsics') or {})
    if not K or 'fx' not in K:
        K = {'fx': 430.6, 'fy': 430.6, 'ppx': 421.5, 'ppy': 236.1}
        print('WARNING: intrinsics not found in meta.json, using the values read from this camera earlier')
    print('frames %d | valid %.1f%% | temporal SD median %.2f mm p95 %.2f mm'
          % (nf, 100 * np.mean(med > 0), np.nanmedian(sd), np.nanpercentile(sd, 95)))
    print('intrinsics fx=%.2f fy=%.2f ppx=%.2f ppy=%.2f' % (K['fx'], K['fy'], K['ppx'], K['ppy']))

    P = backproject(med, K)
    print('metric points %d (stride 3), Z range %.0f-%.0f mm'
          % (len(P), P[:, 2].min(), P[:, 2].max()))

    # 深度直方图：先看有几个面
    v = P[:, 2]
    hist, edges = np.histogram(v, bins=np.arange(np.floor(v.min()), np.ceil(v.max()) + 1, 1.0))
    hs = np.convolve(hist, np.ones(7) / 7, mode='same')
    idx = [i for i in range(3, len(hs) - 3) if hs[i] == hs[i - 3:i + 4].max()]
    idx.sort(key=lambda i: -hs[i])
    peaks = sorted([(edges[i] + 0.5, hs[i]) for i in idx[:8]])
    print('\nZ peaks (mm): %s' % ', '.join('%.0f(%d)' % (p, h) for p, h in peaks))

    rng = np.random.default_rng(0)
    planes, cur = [], P
    for k in range(5):
        if len(cur) < 3000:
            break
        r = ransac(cur, tol, 1500, rng)
        if r is None:
            break
        n, d = r
        inl = np.abs(cur @ n + d) < tol
        if inl.sum() < 1500:
            break
        n2, d2 = fit_plane(cur[inl])
        res = cur[inl] @ n2 + d2
        planes.append({'n': n2, 'd': d2, 'n_in': int(inl.sum()),
                       'rms': float(np.sqrt(np.mean(res ** 2))),
                       'z': float(cur[inl][:, 2].mean())})
        cur = cur[~inl]

    print('\nplanes (metric):')
    for i, p in enumerate(planes, 1):
        print('  P%d  n=[% .3f % .3f % .3f]  d=%9.2f mm  inliers=%6d (%.1f%%)  rms=%.2f  z=%.0f mm'
              % (i, p['n'][0], p['n'][1], p['n'][2], p['d'], p['n_in'],
                 100 * p['n_in'] / len(P), p['rms'], p['z']))

    best = None
    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            a, b = planes[i], planes[j]
            dot = float(np.dot(a['n'], b['n']))
            ang = np.degrees(np.arccos(np.clip(abs(dot), -1, 1)))
            if dot < 0:
                bb_d = -b['d']
            else:
                bb_d = b['d']
            gap = abs(a['d'] - bb_d) if dot < 0 else abs(a['d'] - b['d'])
            if ang < 5 and 8 < gap < 90:
                score = a['n_in'] + b['n_in']
                if best is None or score > best[0]:
                    best = (score, i, j, ang, gap)

    print('\n================ VERDICT ================')
    if best:
        _, i, j, ang, gap = best
        a, b = planes[i], planes[j]
        print('best pair P%d & P%d' % (i + 1, j + 1))
        print('  normal angle      %.2f deg' % ang)
        print('  step along normal %.2f mm' % gap)
        print('  RMS %.2f / %.2f mm' % (a['rms'], b['rms']))
        print('  support %.1f%%' % (100 * (a['n_in'] + b['n_in']) / len(P)))
        print('  GEOMETRY: %s' % ('USEABLE' if ang < 5 and max(a['rms'], b['rms']) < 3 else 'MARGINAL'))
    else:
        print('NO parallel pair with an 8-90 mm gap in metric space.')
        print('See Z peaks above: if only one dominant peak is near the working')
        print('distance, the second face is not returning depth (occlusion or tilt).')
    print('=========================================')


if __name__ == '__main__':
    main()
