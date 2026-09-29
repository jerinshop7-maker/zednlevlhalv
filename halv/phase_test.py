#!/usr/bin/env python3
"""Target-blind phase audit for HALV waveform event coordinates.

The script compares several independently defined x-event sets modulo 3, 6,
and 96. The hand-tabulated tail pulse starts are included only as a replication
of the reported clue; they are not used to choose the other event detectors.

Run from repository root:
    python3 halv/phase_test.py
"""
from __future__ import annotations

from collections import Counter
from math import comb
import sys

import numpy as np

X0, X1 = 90, 858
BLOCK = 96
PHASES = (3, 6, 96)


def summarize(name: str, xs: list[int]) -> None:
    xs = sorted(set(int(x) for x in xs if X0 <= x <= X1))
    print(f"\n{name}: n={len(xs)}")
    if not xs:
        return
    for period in PHASES:
        hist = Counter(x % period for x in xs)
        vals = [hist.get(r, 0) for r in range(period)]
        best_phase = max(range(period), key=lambda r: vals[r])
        suffix = f"hist={vals}" if period <= 6 else f"top={Counter(x % period for x in xs).most_common(5)}"
        print(f"  mod {period:2}: nonzero residues={sum(v > 0 for v in vals)}/{period}; "
              f"max bin={vals[best_phase]}/{len(xs)} at residue {best_phase}; {suffix}")
    block_res = Counter((x - X0) % BLOCK for x in xs)
    common = block_res.most_common(8)
    print(f"  block-relative residues (top 8): {common}")


def zero_residue_scan(xs: list[int], period: int = 3) -> None:
    """Exact uniform-residue probability of at least one empty residue class."""
    n = len(set(xs))
    if n == 0:
        return
    p_empty_any = sum((-1) ** (j + 1) * comb(period, j) * ((period - j) / period) ** n
                      for j in range(1, period + 1))
    observed_empty = period - len({x % period for x in xs})
    print(f"  modulo-{period} empty-bin scan: {observed_empty} empty; "
          f"P(any empty under uniform residues)={p_empty_any:.6g} (phase already scanned)")


def max_bin_scan(xs: list[int], period: int = 3) -> None:
    """Family-wise null for choosing the phase with the largest residue count."""
    n = len(set(xs))
    if period != 3 or n == 0:
        return
    counts = Counter(x % period for x in set(xs))
    observed = max(counts.values())
    tail = sum(comb(n, k) * (1 / 3) ** k * (2 / 3) ** (n - k)
               for k in range(observed, n + 1))
    # The three extreme events are mutually exclusive when observed > n/2.
    p_scan = min(1.0, 3 * tail)
    print(f"  modulo-3 max-bin scan: max={observed}/{n}; "
          f"P(any phase reaches this count)≈{p_scan:.6g} (uniform independent events)")


def plateau_events() -> tuple[list[int], list[int]]:
    p = np.load("halv/plateaus.npy")
    return [int(r[1]) for r in p], [int(r[2]) for r in p]


_TEMPLATE_SCORES = None


def plateaus_at_threshold(threshold: float) -> list[tuple[int, int, int, int]]:
    """Use the repo's upper-half rung templates, varying only score threshold."""
    global _TEMPLATE_SCORES
    sys.path.insert(0, "halv")
    import measure
    if _TEMPLATE_SCORES is None:
        _TEMPLATE_SCORES = measure.template_scores()
    return measure.plateaus(_TEMPLATE_SCORES, threshold)


def turning_points_tail() -> tuple[list[int], list[int]]:
    """Turning vertices from the saved, uncertified tail Viterbi path."""
    v = np.load("halv/vit_568_858.npy").astype(float)
    x_start = 568
    # Viterbi stores one value per x in [568,858]. Collapse zero slopes and take
    # vertices only when nonzero slope changes sign.
    d = np.diff(v)
    turns, crossings = [], []
    for i in range(1, len(d)):
        if d[i - 1] * d[i] < 0:
            turns.append(x_start + i)
    for i in range(len(v) - 1):
        if v[i] == 0 and v[i + 1] > 0:
            crossings.append(x_start + i + 1)
        elif v[i] > 0 and v[i + 1] == 0:
            crossings.append(x_start + i + 1)
    return turns, crossings


def pulse_edges_tail() -> tuple[list[int], list[int]]:
    v = np.load("halv/vit_568_858.npy").astype(float)
    x_start = 568
    active = v > 0
    starts, ends = [], []
    i = 0
    while i < len(v):
        if not active[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(v) and active[j + 1]:
            j += 1
        starts.append(x_start + i)
        ends.append(x_start + j)
        i = j + 1
    return starts, ends


def axis_support_all() -> list[int]:
    """Columns whose center-axis row has visible ink (independent of Viterbi)."""
    # q=0/axis is not included in the nonzero template-score array, so inspect
    # the raw image row using the fixed threshold documented below.
    from PIL import Image

    image = np.asarray(Image.open("cryptoHALV.png").convert("L"))
    row = image[474:477, X0 : X1 + 1]
    support = row.max(axis=0) >= 16  # 16/255 threshold; fixed before phase tally
    xs = np.flatnonzero(support) + X0
    # Return starts of maximal support runs as zero-crossing/axis-contact events.
    return [int(x) for i, x in enumerate(xs) if i == 0 or x > xs[i - 1] + 1]


def main() -> None:
    pstarts, pends = plateau_events()
    summarize("high-confidence plateau starts (all blocks)", pstarts)
    zero_residue_scan(pstarts, 3)
    max_bin_scan(pstarts, 3)
    print("  per 96-px block mod-3 counts:")
    for block in range(8):
        xs = [x for x in pstarts if 88 + 96 * block <= x < 88 + 96 * (block + 1)]
        print(f"    block {block}: n={len(xs)} residues={dict(sorted(Counter(x % 3 for x in xs).items()))}")

    print("  threshold sensitivity (same template detector; start positions):")
    for threshold in (0.970, 0.980, 0.985, 0.990, 0.992, 0.995, 0.999):
        ps = plateaus_at_threshold(threshold)
        xs = [int(row[1]) for row in ps]
        hist = Counter(x % 3 for x in xs)
        print(f"    score>{threshold:.3f}: n={len(xs)} counts={dict(sorted(hist.items()))}")
    summarize("high-confidence plateau ends (all blocks)", pends)
    max_bin_scan(pends, 3)

    turns, crossings = turning_points_tail()
    summarize("slope-reversal vertices (tail Viterbi; uncertified)", turns)
    summarize("zero contacts (tail Viterbi; uncertified)", crossings)

    active_starts, active_ends = pulse_edges_tail()
    summarize("nonzero-excursion starts (tail Viterbi; uncertified)", active_starts)
    summarize("nonzero-excursion ends (tail Viterbi; uncertified)", active_ends)

    axis_starts = axis_support_all()
    summarize("axis-support run starts (pixel threshold; exploratory)", axis_starts)

    reported = [675, 687, 696, 703, 723, 735, 744, 766, 781, 790, 819, 828, 838, 843]
    summarize("reported tail pulse starts (§4.2 replication)", reported)
    residues = Counter(x % 3 for x in reported)
    print(f"reported starts mod 3: {dict(sorted(residues.items()))}")
    zero_residue_scan(reported, 3)


if __name__ == "__main__":
    main()
