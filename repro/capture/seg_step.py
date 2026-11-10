#!/usr/bin/env python3
"""
seg_step.py -- 稳健的台阶分割（v3）

v1 错在把 (u,v,Z) 当米制点；v2 错在全局 RANSAC 后凭"间距接近"选面，会配错。

v3 的判据不靠猜：
  1. 只接受法向接近光轴的平面（|n·z| > 0.98）——台阶的两个面都是水平的；
  2. 把 d 相近的平面合并（同一面被切碎时不会重复计数）；
  3. 两个面必须**在图像上相邻**（各自的掩膜膨胀后相交 > 500 像素），
     因为真实台阶的两侧一定隔着一条棱线贴在一起；
  4. 输出 label.png：高面红、低面绿、背景灰、无效黑，供人眼复核。

用法
    python3 seg_step.py <放置目录> [out.png]
"""
import sys, os, glob, json, itertools
import numpy as np
import cv2


def load(folder):
    fs = sorted(glob.glob(os.path.join(folder, 'depth_raw', '*.png')))
    if not fs:
        raise SystemExit('no depth frames')
    st = np.stack([cv2.imread(f, cv2.IMREAD_UNCHANGED) for f in fs]).astype(np.float32)
    med = np.median(st, axis=0)
    sd = np.nanstd(np.where(st > 0, st, np.nan), axis=0)
    meta = json.load(open(os.path.join(folder, 'meta.json'), encoding='utf-8'))
    return med, sd, len(fs), meta['intrinsics']


def backproject(depth, K, stride=2):
    h, w = depth.shape
    ys, xs = np.mgrid[0:h:stride, 0:w:stride]
    z = depth[ys, xs]
    ok = z > 0
    X = (xs[ok] - K['ppx']) * z[ok] / K['fx']
    Y = (ys[ok] - K['ppy']) * z[ok] / K['fy']
    return np.stack([X, Y, z[ok]], 1), (ys[ok], xs[ok])


def fit(P):
    c = P.mean(0)
    _, _, vt = np.linalg.svd(P - c, full_matrices=False)
    n = vt[2] / np.linalg.norm(vt[2])
    d = -float(n @ c)
    if n[2] < 0:
        n, d = -n, -d          # 统一朝 +z
    return n, d


def main():
    folder = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(folder, 'label.png')
    med, sd, nf, K = load(folder)
    print('frames %d | valid %.1f%% | temporal SD median %.2f mm'
          % (nf, 100 * np.mean(med > 0), np.nanmedian(sd)))

    P, (yy, xx) = backproject(med, K, 2)
    rng = np.random.default_rng(0)

    # ---- 1. 只找水平平面 ---------------------------------------------
    cand, cur = [], P
    for _ in range(8):
        if len(cur) < 3000:
            break
        best = (-1, None)
        for _ in range(2000):
            i = rng.choice(len(cur), 3, replace=False)
            p0, p1, p2 = cur[i]
            n = np.cross(p1 - p0, p2 - p0)
            nn = np.linalg.norm(n)
            if nn < 1e-9:
                continue
            n /= nn
            if abs(n[2]) < 0.98:          # 只要水平面
                continue
            d = -float(n @ p0)
            c = int(np.count_nonzero(np.abs(cur @ n + d) < 2.5))
            if c > best[0]:
                best = (c, (n, d))
        if best[1] is None:
            break
        n, d = best[1]
        inl = np.abs(cur @ n + d) < 2.5
        if inl.sum() < 800:
            break
        n2, d2 = fit(cur[inl])
        cand.append((n2, d2, int(inl.sum())))
        cur = cur[~inl]

    # ---- 2. 合并 d 相近的平面 -----------------------------------------
    cand.sort(key=lambda t: -t[2])
    merged = []
    for n, d, c in cand:
        hit = None
        for m in merged:
            if abs(m['d'] - d) < 3.0:
                hit = m
                break
        if hit:
            hit['pts'] += c
            hit['ds'].append(d)
        else:
            merged.append({'n': n, 'd': d, 'pts': c, 'ds': [d]})
    for m in merged:
        m['d'] = float(np.median(m['ds']))

    print('\nhorizontal planes (merged):')
    for i, m in enumerate(merged):
        print('  H%d  z=%7.2f mm  d=%8.2f  support=%6d' % (i + 1, -m['d'], m['d'], m['pts']))
    if len(merged) < 2:
        print('\nOnly one horizontal plane found - cannot measure a step.')
        return

    # ---- 3. 全分辨率掩膜 + 相邻性 -------------------------------------
    h, w = med.shape
    Z = med
    X = (np.arange(w)[None, :] - K['ppx']) * Z / K['fx']
    Y = (np.arange(h)[:, None] - K['ppy']) * Z / K['fy']
    masks = []
    for m in merged:
        r = m['n'][0] * X + m['n'][1] * Y + m['n'][2] * Z + m['d']
        masks.append((np.abs(r) < 2.5) & (Z > 0))
    k5 = np.ones((5, 5), np.uint8)

    print('\nadjacent pairs (gap 15-70 mm, overlap>500 px):')
    bestpair = None
    for i, j in itertools.combinations(range(len(merged)), 2):
        gap = abs(merged[i]['d'] - merged[j]['d'])
        if not (15 < gap < 70):
            continue
        a = cv2.dilate(masks[i].astype(np.uint8), k5) > 0
        b = cv2.dilate(masks[j].astype(np.uint8), k5) > 0
        ov = int((a & b).sum())
        if ov < 500:
            continue
        print('  H%d-H%d  gap=%6.2f mm  overlap=%6d px  support=%6d'
              % (i + 1, j + 1, gap, ov, merged[i]['pts'] + merged[j]['pts']))
        if bestpair is None or merged[i]['pts'] + merged[j]['pts'] > merged[bestpair[0]]['pts'] + merged[bestpair[1]]['pts']:
            bestpair = (i, j, gap)

    print('\n================ RESULT ================')
    if bestpair is None:
        print('no adjacent horizontal pair found; inspect label.png')
    else:
        i, j, gap = bestpair
        print('faces: H%d (z=%.1f) and H%d (z=%.1f)' % (i + 1, -merged[i]['d'], j + 1, -merged[j]['d']))
        print('step along normal : %.2f mm' % gap)
        print('support           : %d px' % (merged[i]['pts'] + merged[j]['pts']))
        # RMS
        for k in (i, j):
            m = merged[k]
            r = (m['n'][0]*X + m['n'][1]*Y + m['n'][2]*Z + m['d'])[masks[k]]
            print('  H%d RMS %.2f mm, %d px' % (k + 1, float(np.sqrt(np.mean(r**2))), int(masks[k].sum())))

    # ---- 4. 标签图 -----------------------------------------------------
    vis = np.zeros((h, w, 3), np.uint8)
    vis[Z == 0] = (0, 0, 0)
    vis[Z > 0] = (70, 70, 70)
    cols = [(0, 0, 255), (0, 255, 0), (255, 128, 0), (255, 0, 255)]
    for k, m in enumerate(masks):
        vis[m] = cols[k % 4]
    cv2.imwrite(outp, vis)
    print('\nlabel image: %s   (red/green = the two faces, grey = other surfaces)' % outp)
    print('=========================================')


if __name__ == '__main__':
    main()
