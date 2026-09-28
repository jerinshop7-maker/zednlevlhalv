#!/usr/bin/env python3
"""Exploratory test of direct 6-pixel amplitude sampling against the HALV target.

This is deliberately a narrow test. It samples the visible upper-half
intensity centroid at each of the six possible 6-pixel phases, normalizes by the
confirmed 8x96 block scale, and rounds to q in {0,1,2,3}. It then exhausts the
24 state-to-bit bijections plus simple direction/bit-order conventions.

The centroid is only a proxy for the centerline and can be biased on sloped or
overlapping strokes. A no-match result applies only to candidates from this proxy;
it does NOT test a latent Q4 sequence recovered through a continuous renderer.

Run from the repository root:
    python3 halv/direct_q4.py
"""
from __future__ import annotations

import itertools

import numpy as np
from PIL import Image

from oracle import H160, N, TARGET, addr, check, hash160

try:
    from coincurve import PrivateKey
except ImportError:  # pragma: no cover - portable but slower fallback
    PrivateKey = None


PNG = "cryptoHALV.png"
X0 = 90
BLOCK = 96
CLOCK = 6
SYMBOLS = 128


def measured_amplitude() -> np.ndarray:
    """Upper-half intensity centroid, expressed as distance from y=475."""
    image = np.asarray(Image.open(PNG).convert("L"), dtype=np.float64) / 255.0
    rows = np.arange(475, dtype=np.float64)
    columns = image[:475, :].sum(axis=0)
    weighted = (image[:475, :] * rows[:, None]).sum(axis=0)
    centers = np.divide(
        weighted,
        columns,
        out=np.full(columns.shape, np.nan),
        where=columns > 1e-9,
    )
    return 475.0 - centers


def direct_states(amplitude: np.ndarray, phase: int) -> list[int]:
    states = []
    for i in range(SYMBOLS):
        x = X0 + phase + CLOCK * i
        block = min(7, max(0, (x - X0) // BLOCK))
        scale = 128.0 / (2**block)
        z = amplitude[x] / scale
        states.append(0 if not np.isfinite(z) else min(range(4), key=lambda q: abs(z - q)))
    return states


def candidate_bitstrings(states: list[int]):
    """Yield unique 256-bit strings and the convention that produced each."""
    seen: set[str] = set()
    for mapping in itertools.permutations(range(4)):
        for reverse_symbols in (False, True):
            ordered = states[::-1] if reverse_symbols else states
            for reverse_pair_bits in (False, True):
                bits = "".join(
                    format(mapping[q], "02b")[::-1]
                    if reverse_pair_bits
                    else format(mapping[q], "02b")
                    for q in ordered
                )
                for reverse_all_bits in (False, True):
                    stream = bits[::-1] if reverse_all_bits else bits
                    for reverse_byte_order in (False, True):
                        candidate = "".join(stream[i : i + 8] for i in range(0, 256, 8))
                        if reverse_byte_order:
                            candidate = "".join(stream[i : i + 8] for i in range(0, 256, 8))[::-1]
                        if candidate not in seen:
                            seen.add(candidate)
                            yield candidate, (mapping, reverse_symbols, reverse_pair_bits,
                                              reverse_all_bits, reverse_byte_order)


def matches_target(scalar: int) -> bool:
    if PrivateKey is None:
        return check(scalar)
    public = PrivateKey.from_int(scalar).public_key
    return any(
        hash160(public.format(compressed=compressed)).hex() == H160
        for compressed in (False, True)
    )


def main() -> None:
    # Oracle control: private key 1 has a known uncompressed P2PKH address.
    assert addr(1) == "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm"
    assert addr(1, comp=True) == "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH"
    amplitude = measured_amplitude()
    total = 0
    matches = []

    for phase in range(CLOCK):
        states = direct_states(amplitude, phase)
        counts = np.bincount(states, minlength=4).tolist()
        phase_candidates = 0
        for bitstring, convention in candidate_bitstrings(states):
            scalar = int(bitstring, 2)
            if not 0 < scalar < N:
                continue
            phase_candidates += 1
            if matches_target(scalar):
                matches.append((phase, scalar, convention))
        total += phase_candidates
        print(f"phase={phase} q_counts={counts} unique_valid_keys={phase_candidates}")

    print(f"tested={total} matches={len(matches)} target={TARGET} hash160={H160}")
    for phase, scalar, convention in matches:
        print(f"MATCH phase={phase} key={scalar:064x} convention={convention}")
    if not matches:
        print("RESULT: no match under direct centroid sampling; latent rendered Q4 remains untested")


if __name__ == "__main__":
    main()
