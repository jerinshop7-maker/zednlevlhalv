#!/usr/bin/env python3
"""
Next step (branch A2 -> B -> C of the route).

 1. DP-reconstruct the exact 256 amplitudes v[0..255] from D2.npy (|dv| per cell)
    + the per-column top edge A4.npy, using v[k+1] = v[k] +/- round(D2[k]).
 2. Verify the lattice-walk model (findings C3/C4).
 3. Read bits: bit=0 for a "2"-step (dp=+-1), bit=1 for a "3"-step (dq=+-1),
    sign supplied by the downward drift; try all 32 plausible readings and
    test each 256-bit candidate against the target address.

Needs: halv_measure.py (run first), btc.py
Run:   python3 halv_decode.py
"""
import itertools
import numpy as np
import btc

OFF, N = 92.0, 256
A = np.load('A4.npy')
D = np.load('D2.npy')
TARGET = '1crypto24HCr178iPhi'  # placeholder, replaced below
TARGET = '1crypto24HCr178iMcKd5iUi5D4rsg1nK'
HASH160 = '06c84797d1f468b9d5773a61c80073b344df7470'


def obs(k):
    """observed local max of |signal| at sample k (grid column)."""
    x = int(round(OFF + 3 * k))
    return (A[x] + 0.74) if x < 950 else 0.0


def dp_recover(k_start=96, beam=400, cap=420.0):
    """Beam search over v; transition v[k+1] = v[k] +/- round(D2[k])."""
    v0 = int(round(min(cap, obs(k_start))))
    states = [(abs(v0 - obs(k_start)) ** 2, (float(v0),))]
    for k in range(k_start, N - 1):
        base = int(round(D[k]))
        cands = sorted({max(0, base - 1), base, base + 1, base + 2})
        nxt = []
        for sc, path in states:
            pv = path[-1]
            for d in cands:
                for s in (1, -1):
                    nv = pv + s * d
                    if nv < 0 or nv > cap:
                        continue
                    p2 = path + (nv,)
                    pred = max(p2[-3:])                      # local max in the column
                    nxt.append((sc + (pred - obs(k + 1)) ** 2, p2))
        nxt.sort(key=lambda t: t[0])
        states = nxt[:beam]
        if not states:
            raise RuntimeError('beam died at k=%d - widen cands' % k)
    return states[0]


def bits_from_v(v):
    """step -> '2' (dp) or '3' (dq);  sign = -1 when the level drifts down."""
    lvl = []
    for x in v:
        lvl.append(None if x <= 0 else np.log2(384.0 / x))
    out = []
    for i in range(1, len(v)):
        a, b = lvl[i - 1], lvl[i]
        if a is None or b is None:
            out.append('0')                 # zero sample: placeholder bit
            continue
        d = b - a
        if abs(abs(d) - 1.0) < 0.30:        # exactly one octave  -> a "2" step
            out.append('0')
        elif abs(abs(d) - np.log2(3.0)) < 0.30:   # a factor 3   -> a "3" step
            out.append('1')
        else:
            out.append('?')
    return out


def candidates(stepstr):
    """all 256-bit readings worth trying."""
    s = ''.join('0' if c in '0?' else '1' for c in stepstr)
    seen = set()
    for start in (0, 1):
        for order in ('msb', 'lsb'):
            for pol in (0, 1):
                core = s[start:start + 255]
                if len(core) < 255:
                    core = core + '0' * (255 - len(core))
                if order == 'lsb':
                    core = core[::-1]
                if pol:
                    core = ''.join('1' if c == '0' else '0' for c in core)
                if core not in seen:
                    seen.add(core)
                    yield order, pol, core
    return


def main():
    # NB: samples 0..95 are clipped at the 384px canvas top, so the DP starts
    # at the first unclipped sample; the left block is left as 0 (= 'clipped').
    sc, path = dp_recover(k_start=96)
    v = np.zeros(N); v[96:] = path
    np.save('v_dp.npy', v)
    print('DP score %.1f' % sc)
    print('v =', [int(x) for x in v])

    # --- verify the model on the recovered vector -------------------------
    r = v[1:] / np.where(v[:-1] == 0, np.nan, v[:-1])
    rr = np.abs(np.log2(r)); rr = rr[~np.isnan(rr)]
    hit = sum(int((np.abs(rr - t) < 0.2).sum())
              for t in (0.0, np.log2(1.5), 1.0, np.log2(3), 2.0))
    print('C4 on DP vector: %d/%d ratios in clusters (%.0f%%)'
          % (hit, len(rr), 100 * hit / len(rr)))

    # --- read bits and test ----------------------------------------------
    steps = bits_from_v(v)
    print('steps:', ''.join(steps))
    tried = 0
    for order, pol, core in candidates(steps):
        k = int(core, 2)
        tried += 1
        if not (0 < k < btc.N):
            continue
        addr, _ = btc.addr_from_priv(k)
        if addr == TARGET:
            print('\n*** SOLVED ***')
            print('  order=%s polarity=%d' % (order, pol))
            print('  privkey hex = %064x' % k)
            print('  WIF         = %s' % btc.wif(k))
            return
        if btc.hash160(btc.ser(btc.mul(k))) .hex() == HASH160:
            print('\n*** SOLVED (hash160 match) ***', core)
            return
    print('\nno match in %d readings.' % tried)
    print('NOTE: DP cost is still weak (C4 only %.0f%% on the DP vector vs 95%% on the'
          % (100 * hit / max(1, len(rr))))
    print('      direct 3-smooth snap in halv_measure.py).  Fix stage 1 first')
    print('      (route A2/A4: re-render + RMS gate), then re-run.  Fallbacks: D1..D4.')


if __name__ == '__main__':
    main()
