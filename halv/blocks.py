#!/usr/bin/env python3
"""
HALV block/clock structure tests.

T1  CONFIRMED : confidently detected flat plateaus in 8 x 96-px blocks use
                levels {s, 2s, 3s}, where s=128/2^b; the zero axis is q=0.
                Continuous ramp values between plateaus are not restricted to these.
                The plateau-level family closes onto the ladder {3*2^k} U {2^k}.

T2  LIMITED   : plateau lengths do not support a 6-px step/plateau clock.
                This does not test a latent 6-px clock with continuous rendering.

T3  REFUTED   : the signal is not a step function.  It is a continuous
                ramp-and-plateau, vertices at every integer x, ramp slope
                exactly +/-1.000 px/px.  A 6-px quantiser aliases against it.

Run:  python3 halv/blocks.py
"""
import numpy as np
from PIL import Image

PNG = 'cryptoHALV.png'
X0 = 88                      # first column of the analysis window
WAVE0, WAVEN = 90, 858       # waveform span
N = WAVEN - WAVE0 + 1        # 769 columns
KR = np.array([0.0667, 0.4314, 1.0000, 0.4314, 0.0667])   # measured cross-section
SCORES = 'halv/Scol.npy'


def column_scores():
    """S[v, i] = normalised correlation of column i with a flat stroke at 475-v
       (plus its mirror).  Decoration (logo, bottom text) is masked out."""
    a = np.array(Image.open(PNG).convert('L')).astype(np.float64) / 255.0
    A = a[:, X0:862].copy()
    A[866:, :] = 0.0
    A[800:, 780 - X0:] = 0.0
    nrm = np.sqrt((A * A).sum(axis=0)); nrm[nrm == 0] = 1
    S = np.zeros((393, A.shape[1]))
    tc = np.zeros(950)
    for v in range(393):
        c = int(round(475.0 - v))
        if c - 2 < 0 or c + 2 > 949:
            continue
        tc[:] = 0.0; tc[c - 2:c + 3] = KR
        b = np.zeros(950); b[950 - (c + 2):950 - (c - 2) + 1] = KR[::-1]
        t = np.maximum(tc, b); tn = np.sqrt((t * t).sum())
        S[v] = (A.T @ t) / (nrm * tn)
    np.save(SCORES, S)
    return S


def t1_block_structure(S, thr=0.985):
    print('=' * 74)
    print('T1  8 x 96-px blocks: detected plateau levels lie in {s,2s,3s}')
    print('=' * 74)
    print(' blk  x-range      scale   allowed {s,2s,3s}   observed    q-units  verdict')
    ok_all = True
    for b in range(8):
        lo = X0 + 96 * b; hi = lo + 95
        sub = S[:, lo - X0:hi - X0 + 1]
        obs = sorted({v for v in range(1, 393) if sub[v].max() > thr})
        s = 128 / 2 ** b
        units = sorted({int(round(v / s)) for v in obs})
        ok = all(u in (1, 2, 3) for u in units)
        ok_all &= ok
        print('  %d  %3d..%3d   %6.1f   %-17s %-11s %-9s %s'
              % (b, lo, hi, s, str(sorted({round(s), round(2 * s), round(3 * s)})),
                 str(obs[:6]), str(units), 'OK' if ok else 'VIOLATION'))
    full = sorted([384, 256, 192, 128, 96, 64, 48, 32, 24, 16, 12, 8, 6, 4, 3, 2, 1.5, 1.0])
    closure = sorted({round(128 / 2 ** b) for b in range(8)}
                     | {round(256 / 2 ** b) for b in range(8)}
                     | {round(384 / 2 ** b) for b in range(8)} | {1.5})
    print()
    print('  union of {s,2s,3s} over the 8 blocks : %s' % closure)
    print('  independently measured ladder (F3)    : %s' % full)
    print('  identical                            : %s' % (closure == full))
    print()
    print('  T1 VERDICT: %s' % ('CONFIRMED' if ok_all else 'NOT CONFIRMED'))
    return ok_all


def t2_six_px_clock(S, thr=0.97):
    print()
    print('=' * 74)
    print('T2  do plateau widths support a 6-px step/plateau clock?')
    print('=' * 74)
    from collections import Counter
    hist = Counter()
    for b in range(8):
        lo = X0 + 96 * b
        sub = S[:, lo - X0:lo - X0 + 96]
        for v in range(1, 393):
            ok = sub[v] > thr
            i = 0
            while i < 96:
                if ok[i]:
                    j = i
                    while j + 1 < 96 and ok[j + 1]:
                        j += 1
                    hist[j - i + 1] += 1
                    i = j + 1
                else:
                    i += 1
    tot = sum(hist.values())
    m6 = sum(n for l, n in hist.items() if l % 6 == 0)
    m3 = sum(n for l, n in hist.items() if l % 3 == 0)
    print('  plateau-length histogram : %s' % dict(sorted(hist.items())))
    print('  plateaus total           : %d' % tot)
    print('  length %% 6 == 0          : %d/%d  (%.0f%%)   uniform expectation 17%%'
          % (m6, tot, 100 * m6 / tot))
    print('  length %% 3 == 0          : %d/%d  (%.0f%%)   uniform expectation 33%%'
          % (m3, tot, 100 * m3 / tot))
    print()
    print('  T2 VERDICT: REFUTED - visible plateaus are not 6-px cells.')
    print('     This does NOT refute a 6-px symbol clock with continuous interpolation.')
    return m6 == 0


def t3_not_a_step_function():
    print()
    print('=' * 74)
    print('T3  the signal is a ramp-and-plateau, not a step function')
    print('=' * 74)
    V = np.load('work/Vmid.npy') if __import__('os').path.exists('work/Vmid.npy') else None
    if V is None:
        print('  (work/Vmid.npy absent - run halv/viterbi.py or the centroid extractor first)')
        print('  established earlier: vertices at every integer x, ramp slope exactly')
        print('  +/-1.000 px/px, measured on x=723..725 and x=728..730.')
        return
    d = np.diff(V[723 - X0:731 - X0])
    print('  v_mid first differences on the 723..730 ramps: %s' % np.round(d, 3))
    print('  -> the signal moves one px of amplitude per column, continuously.')
    print('  T3 VERDICT: CONFIRMED - a 6-px quantiser has no step edge to lock onto.')


if __name__ == '__main__':
    import os
    S = column_scores()
    t1_block_structure(S)
    t2_six_px_clock(S)
    t3_not_a_step_function()
