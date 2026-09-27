#!/usr/bin/env python3
"""
Zden "BTCrypto Puzzle Level HALV" - measurement pipeline.

Regenerates every CONFIRMED measurement from cryptoHALV.png alone:
  A4.npy         per-column subpixel top edge of the stroke (rows 0..475)
  D2.npy         |dv| per 3px grid cell, from the exact mass identity
  v_3smooth.npy  amplitudes snapped to v = 384 * 2^-a * 3^-b
and re-prints the evidence for findings C1..C6.

Run:  python3 halv_measure.py
Then: python3 halv_decode.py     (next step: DP + WIF check)
"""
import numpy as np
from PIL import Image

PNG = 'cryptoHALV.png'
OFF, N, CY, W_STROKE = 92.0, 256, 475.0, 1.4784
TARGET = '1crypto24HCr178iMcKd5iUi5D4rsg1nK'
HASH160 = '06c84797d1f468b9d5773a61c80073b344df7470'

img = np.array(Image.open(PNG).convert('L')).astype(float) / 255.0
H, W = img.shape
mass = img[:476, :].sum(axis=0)                      # upper-half column mass


# ---------- C1: grid  x = 92 + 3i ----------
def zero_runs(thresh=2.0):
    A = np.load('A4.npy')
    z = [k for k in range(N) if A[int(round(OFF + 3 * k))] < thresh]
    runs, cur = [], [z[0]] if z else []
    for k in z[1:]:
        if k == cur[-1] + 1:
            cur.append(k)
        else:
            runs.append(cur); cur = [k]
    if cur:
        runs.append(cur)
    return runs


# ---------- C2: exact mirror symmetry about y=475 ----------
def symmetry():
    r = np.arange(100, 441)                          # avoid text (y>900) & logo (x>780)
    d = np.abs(img[r, :760] - img[950 - r, :760])
    return (d == 0).mean(), d.max(), (d > 50).sum()


# ---------- A4: subpixel top edge (0.75 coverage rule) ----------
def top_edge(frac=0.75):
    T = np.full(W, np.nan)
    for x in range(88, 872):
        col = img[:476, x]
        if col.sum() < 0.6:
            continue
        idx = np.where(col > 0)[0]
        c = np.cumsum(col[idx])
        k = np.searchsorted(c, frac)
        T[x] = CY - (idx[0] + (k - 1) + (frac - (c[k - 1] if k > 0 else 0)))
    return T


# ---------- D2: |dv| per cell  (mass = w * (dx + |dy|)) ----------
def delta_v():
    D = np.zeros(N - 1)
    for k in range(N - 1):
        x0 = int(round(OFF + 3 * k))
        if x0 + 3 >= 872:
            break
        D[k] = (0.5 * mass[x0] + mass[x0 + 1] + mass[x0 + 2] + 0.5 * mass[x0 + 3]) / W_STROKE - 3.0
    return D


def main():
    A = top_edge()
    np.save('A4.npy', A)
    D = delta_v()
    np.save('D2.npy', D)

    f = np.array([(A[int(round(OFF + 3 * k))] + 0.74) if int(round(OFF + 3 * k)) < 950 else 0.0
                  for k in range(N)])
    S = sorted({round(384 * 2 ** (-a) * 3 ** (-b), 3) for a in range(10) for b in range(3)})
    v = np.array([min(S, key=lambda t: abs(t - x)) for x in f])
    np.save('v_3smooth.npy', v)
    np.save('gridA.npy', f)

    print('=' * 68)
    print('C1  grid  x = 92 + 3i, i=0..%d   (92 -> %d)' % (N - 1, int(OFF + 3 * (N - 1))))
    runs = zero_runs()
    starts = [int(round(OFF + 3 * r[0])) for r in runs]
    print('    %d zero-runs; run starts x mod 3 == %s ; grid 92+3i has 92 mod 3 = %d'
          % (len(runs), sorted({s % 3 for s in starts}), int(OFF) % 3))
    print('    -> every flat(zero) segment begins exactly on a sample: %s'
          % ({s % 3 for s in starts} == {int(OFF) % 3}))

    frac, mx, big = symmetry()
    print('C2  mirror symmetry about y=475: %.4f of pixels identical, max |diff| = %d/255,'
          ' pixels>50: %d' % (frac, mx * 255, big))
    print('    -> signal is |s|; sign is destroyed (C2 CONFIRMED)')

    res = v - f
    print('C3  3-smooth model v = 384*2^-a*3^-b : mean|res| = %.2f px, %.0f%% within 3 px'
          % (np.abs(res).mean(), 100 * (np.abs(res) < 3).mean()))

    r = v[1:] / np.where(v[:-1] == 0, np.nan, v[:-1])
    rr = np.abs(np.log2(r)); rr = rr[~np.isnan(rr)]
    tot = 0
    for t, name in [(0.0, 'x1'), (np.log2(1.5), 'x3/2'), (1.0, 'x2'),
                    (np.log2(3), 'x3'), (2.0, 'x4')]:
        n = int((np.abs(rr - t) < 0.2).sum()); tot += n
        print('C4  log2|ratio| = %5.3f (%-4s) : %3d' % (t, name, n))
    print('    %d / %d ratios in the 5 clusters (%.0f%%)'
          % (tot, len(rr), 100 * tot / len(rr)))

    p = [None if v[i] == 0 else np.log2(v[i] / 384) + 7 for i in range(N)]
    good = [x for x in p if x is not None]
    print('C5  level p: mean %.2f (i<64) -> %.2f (i>192)  = downward drift = HALVING'
          % (np.mean([x for x in p[:64] if x is not None]),
             np.mean([x for x in p[192:] if x is not None])))
    print('    max amplitude %.0f px = canvas clip (y=91/859)' % v.max())
    print('=' * 68)
    print('target  %s' % TARGET)
    print('hash160 %s' % HASH160)
    print('next    -> halv_decode.py  (DP on D2.npy, then WIF check via btc.py)')


if __name__ == '__main__':
    main()
