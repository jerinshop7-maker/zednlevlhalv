#!/usr/bin/env python3
"""
Evaluation of the externally-supplied `solve_halv_q4.py`.

That script assumes a 6-px symbol clock (128 quaternary states, 2 bits each).
It runs to completion and reports 384 candidates, 0 matches.  That negative is
VACUOUS, for three independently checkable reasons:

  E1  the recovered q cannot represent the data: with scale s the model tops
      out at 3s, but block 0 measures a peak of 379 px against a model max of
      256 (q=3 never occurs in block 0)
  E2  the recovered q is not payload-like: a quaternary encoding of 256 bits of
      key material is uniform (~32 per value); this is 54% q==1 and 1.6% q==3
  E3  the model barely beats a trivial baseline: rms 39.1 px versus 43.2 px for
      "one constant per block" and 82.8 px for the axis

Root cause, visible in the code: `amplitude_trace` keeps only pixels >= 20% of
the column max, and in blocks 0-2 each column contains several stroke crossings,
so the centroid is meaningless; `recover_q` then takes the median of 6 columns of
what is a ramp, which is not a symbol value.

Run:  python3 halv/q4eval.py
"""
import os
import numpy as np

X0 = 90
TRACE = 'q4_trace.npy'
QSEQ = 'q4_recovered.npy'


def load():
    if not (os.path.exists(TRACE) and os.path.exists(QSEQ)):
        print('run:  python3 solve_halv_q4.py cryptoHALV.png   (writes %s, %s)' % (TRACE, QSEQ))
        return None, None
    return np.load(QSEQ), np.load(TRACE)


def step_model(q):
    pred = np.zeros(950)
    for n in range(len(q)):
        xc = X0 + 6 * n + 2.5
        b = min(7, (int(round(xc)) - X0) // 96)
        s = 128 >> b
        pred[X0 + 6 * n:X0 + 6 * n + 6] = q[n] * s
    return pred


def main():
    q, v = load()
    if q is None:
        return 1
    pred = step_model(q)
    idx = np.arange(90, 859)
    d = v[idx] - pred[idx]

    print('=' * 74)
    print('E1  can the q4 model even represent the waveform it claims to describe?')
    print('=' * 74)
    print(' blk   scale   model max (3s)   measured max   verdict')
    for b in range(8):
        lo = X0 + 96 * b; hi = lo + 95
        j = np.arange(lo, hi + 1)
        s = 128 >> b
        mm, mv = pred[j].max(), v[j].max()
        print('  %d   %5d   %8d        %8d        %s'
              % (b, s, mm, mv, 'OK' if mv <= 3 * s + 1 else 'MODEL TOO SMALL'))
    print()

    print('=' * 74)
    print('E2  is the recovered q payload-like?')
    print('=' * 74)
    u, c = np.unique(q, return_counts=True)
    print('  histogram : %s   (uniform would be ~%d each)' % (dict(zip(u.tolist(), c.tolist())), len(q) // 4))
    for val in (0, 1, 2, 3):
        print('    q==%d : %5.1f%%' % (val, 100 * np.mean(q == val)))
    print()

    print('=' * 74)
    print('E3  does the model explain the waveform, or just the block scales?')
    print('=' * 74)
    rms0 = np.sqrt((v[idx] ** 2).mean())
    per_block = []
    for b in range(8):
        j = np.arange(X0 + 96 * b, X0 + 96 * b + 96)
        per_block.append(((v[j] - np.median(v[j])) ** 2).mean())
    rmsc = np.sqrt(np.mean(per_block))
    rmsq = np.sqrt((d ** 2).mean())
    print('  rms vs the axis (q=0 everywhere)   : %6.2f px' % rms0)
    print('  rms vs one constant per block     : %6.2f px' % rmsc)
    print('  rms vs the 6-px q4 model          : %6.2f px' % rmsq)
    print('  correlation measured vs model     : %.4f' % np.corrcoef(v[idx], pred[idx])[0, 1])
    print()
    print('  The q4 model beats "a constant per block" by %.1f px only.' % (rmsc - rmsq))
    print('  A working decoding model drives this toward 0.')
    print()
    print('=' * 74)
    print('CONCLUSION: the 384-candidate negative is vacuous. It does not refute')
    print('the q4 idea; it shows the extractor returns a degenerate sequence.')
    print('The 8-block x q-in-{0,1,2,3} STRUCTURE is independently confirmed')
    print('(see halv/blocks.py T1); the 6-px CLOCK is refuted (T2/T3).')
    print('=' * 74)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
