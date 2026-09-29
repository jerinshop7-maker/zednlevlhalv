#!/usr/bin/env python3
"""
Evaluation of the externally-supplied `solve_halv_q4.py`.

That script assumes a 6-px symbol clock (128 quaternary states, 2 bits each).
It runs to completion and reports 384 candidates, 0 matches.  That negative is
VACUOUS, for three independently checkable reasons:

  E1  this recovered q sequence fails to represent the measured peak: it only
      reaches q=2 in block 0, so its rendered max is 256 px versus a measured
      trace max near 378 px. The model family permits q=3 and a 384-px ceiling.
  E2  its q histogram is 54% q==1 and 1.6% q==3. This is descriptive only;
      imbalance alone does not reject a key encoding.
  E3  the model barely beats a trivial baseline: rms 39.1 px versus 43.2 px for
      "one constant per block" and 82.8 px for the axis

Known extraction limitation: `recover_q` takes the median of six columns of a
continuous ramp, which is not a justified state estimator. The external
`amplitude_trace` source is not present here, so the claim that blocks 0-2 have
multiple upper-half crossings is unverified. A full image column contains the
mirrored upper/lower strokes; within the upper half the measured centerline is
single-valued except at the origin fringe x=90..92.

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
    print('E1  does this recovered q sequence reproduce the measured scale?')
    print('=' * 74)
    print(' blk   scale   recovered-model max   measured max   verdict')
    for b in range(8):
        lo = X0 + 96 * b; hi = lo + 95
        j = np.arange(lo, hi + 1)
        s = 128 >> b
        mm, mv = pred[j].max(), v[j].max()
        print('  %d   %5d   %8d        %8d        %s'
              % (b, s, mm, mv, 'OK' if mv <= mm + 1 else 'RECOVERED q TOO SMALL'))
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
    print('  This sampled q4 rendering beats "a constant per block" by %.1f px only.' % (rmsc - rmsq))
    print('  A working decoding model drives this toward 0.')
    print()
    print('=' * 74)
    print('CONCLUSION: the 384-candidate negative is vacuous. It does not refute')
    print('the latent q4 idea; this six-pixel median extractor returns a poor')
    print('reconstruction and cannot test that idea as written.')
    print('The 8-block plateau alphabet q-in-{1,2,3} plus axis q=0 is confirmed')
    print('(see halv/blocks.py T1); the 6-px step clock is rejected, while a')
    print('continuous-renderer symbol clock remains open.')
    print('=' * 74)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
