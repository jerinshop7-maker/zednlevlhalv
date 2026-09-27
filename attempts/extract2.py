import numpy as np
from PIL import Image

A = np.load('A4.npy')
OFF = 92.0
CY = 475.0
img = np.array(Image.open('cryptoHALV.png').convert('L')).astype(float) / 255.0
M = img[:476, :].sum(axis=0)
w = 1.4784


def Am(k):
    x = int(round(OFF + 3 * k))
    return (A[x] + 0.74) if x < 950 else 0.0


def dv(k):
    x0 = int(round(OFF + 3 * k))
    return (0.5 * M[x0] + M[x0 + 1] + M[x0 + 2] + 0.5 * M[x0 + 3]) / w - 3.0


K0, K1 = 150, 256
v0 = int(round(Am(K0)))
beam = [(abs(v0 - Am(K0)) ** 2, [float(v0)])]
for k in range(K0, K1 - 1):
    base = int(round(dv(k)))
    cands = sorted({max(0, base - 1), base, base + 1})
    nb = []
    for sc, path in beam:
        pv = path[-1]
        for d in cands:
            for s in (1, -1):
                nv = pv + s * d
                if nv < 0:
                    continue
                p2 = path + [float(nv)]
                seg = p2[-3:]
                pred = max(seg)
                e = (pred - Am(k + 1)) ** 2
                nb.append((sc + e, p2))
    nb.sort(key=lambda t: t[0])
    beam = nb[:30]

best = beam[0]
v = np.zeros(256)
v[K0:] = best[1]
np.save('v2.npy', v)
print('score %.2f' % best[0])
print('v[150:256] =', [int(x) for x in v[K0:]])
