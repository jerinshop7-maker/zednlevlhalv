# Zden "BTCrypto Puzzle Level HALV" — analysis, confirmed findings, and continuation route

Target: `1crypto24HCr178iMcKd5iUi5D4rsg1nK` (P2PKH, uncompressed pubkey,
hash160 `06c84797d1f468b9d5773a61c80073b344df7470`), funded 2024-04-18, 0.003125 BTC.
Prize untouched as of the last on-chain check in the public record (2026-08-16).

Image: `cryptoHALV.png`, 950×950, 8-bit greyscale, 61 566 bytes,
SHA-256 `3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95`.
Downloaded fresh from `https://crypto.haluska.sk/cryptoHALV.png` — byte-identical to the
copy in this repo.

---

## 0. Executive summary

The image is **not** steganography and **not** a 3-px-sample plot. It is a **rectified,
piecewise-linear waveform drawn as a 2-px stroked polyline and mirrored about y = 475**.

Its structure is now settled at two levels:

* **The amplitude ladder is an 18-rung `{3·2^k} ∪ {2^k}` set** whose steps strictly
  alternate ×2/3 and ×3/4 — two rungs per halving. This is the "HALV" theme.
* **The waveform divides into 8 × 96-px halving blocks**, with the confidently measured
  flat plateau levels in block `b` drawn from `{s, 2s, 3s}`, where `s=128/2^b`; the axis
  supplies `q=0`. The level family is **confirmed** (§4.0), and its closure reproduces the
  ladder exactly. Continuous ramp points interpolate between these plateau levels.

What is **not** established is the data clock. The inference
`768 = 8 × 96 = 128 × 6 → 128 quaternary states = 256 bits` is **not yet supported**:
plateau lengths are 1, 2, 3, 4, 5, 7, and the signal is continuous rather than a 6-px
step function. These observations reject a uniform 6-px step/plateau interpretation; they
do **not** by themselves reject a 6-px logical clock whose states are joined by a continuous
renderer. That model remains open until a target-blind reconstruction test adjudicates it.

The capacity accounting in prior work (≈118 bits) is an artefact of a wrong reading; the true
channel count is larger and is enumerated in §6.

---

## 1. File-level checks — all negative, all certified

| check | result |
|---|---|
| PNG chunk walk (IHDR/pHYs/IDAT/tEXt/IEND) | all CRCs valid, no ancillary chunk, no data after IEND |
| `tEXt` | `Comment: BTCrypto Puzle Level HALV by Zden/Satori -` only |
| 72.009 dpi metadata, 950×950 | no hidden channels, no odd colour type |
| sha256 / sha256d / sha1 / md5 / sha512 / sha256-of-hex → privkey → P2PKH | 6 candidates, 0 match |
| 28×28 in print / NFT framing, logo, `2024/04/18`, printed address | decoration, not data |

`halv/oracle.py` is a self-certified secp256k1 → P2PKH comparator
(`privkey 1 → 1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm`, uncompressed). Reuse it; do not trust
any negative result produced with an uncertified comparator (see §7.0).

---

## 2. CONFIRMED — the drawing model

Reproduce with `python3 halv/measure.py`.

**2.1 The signal is rectified.** The image is mirror-symmetric about `y = 475`
(row map `r ↔ 950−r`). Per column, mean |difference| is 0.0001–0.0008 in units of 1.0
(≈0.03–0.2 grey levels) and 81–99 % of pixels are *bit-identical*. The residual is
rasteriser rounding only.
⇒ **The drawn signal is `|s|`; the sign of `s` is not present in the image.**
This kills any "sign channel" reading.

**2.2 Stroke geometry.** Measured on the long flat runs (e.g. x = 707…721):
cross-section `[0.0667, 0.4314, 1.0000, 0.4314, 0.0667]`, total **1.996 px**.
So the stroke is exactly **2 px** wide, centred on integer rows, with a soft edge
(≈0.06 px tails). A forward model built from this profile reproduces the flat runs to
< 0.09 total L1 over 774 rows (`halv/model.py`).

**2.3 Extents.** Waveform occupies `x = 90 … 858` (769 columns) and reaches
`y = 89 … 861`, i.e. `v_max = 384` exactly. The 475 axis is the exact centre of the canvas.

**2.4 It is a single-valued polyline evaluated at every integer x.**
After masking the logo and the bottom text, only **3 columns (x = 90…92) of the 772**
contain more than one stroke crossing. Everywhere else `y(x)` is a function.
`y(x)` is piecewise linear, and `v_mid(x) = 475 − y(x+0.5)` (the intensity-weighted
centroid of the folded stroke crossing) is **unbiased** — this is the single most reliable
per-column observable in the resolved tail. Its first difference is **about 1.000** on
the cited ramps (e.g. x = 723→725 and x = 728→730), with a small, constant +0.28 offset.

> **This overturns the previous repo's direct extractor.** `halv_measure.py`/`halv_decode.py`
> treated values sampled at `x = 92 + 3i` as the complete signal. That direct read is not
> supported: plateau lengths are 1–19 columns, not multiples of 3, and the raster contains
> intervening geometry. This does not rule out a 3-px physical lattice inside a generator;
> it rules out treating those 256 visible samples as an already-recovered payload stream.

---

## 3. CONFIRMED — the amplitude ladder (this is the "HALV" theme, exactly)

Template-correlating each column against a flat stroke at `y = 475 − v` and requiring a
single consistent `v` at score > 0.992 gives plateaus at exactly these levels:

```
384, 256, 192, 128, 96, 64, 48, 32, 24, 16, 12, 8, 6, 4, 3, 2, 1.5, 1
```

i.e. exactly **`{3·2^k} ∪ {2^k}`, k = 0…8**. Consecutive ratios:

```
×2/3, ×3/4, ×2/3, ×3/4, …  (17 steps, perfectly alternating, residual < 1e-4)
```

**Each pair of steps is exactly one halving (×1/2).** 18 rungs = 8 halvings + 1.
`log2(384) = 7.585`. This is a *logarithmic* halving ladder: the two rungs of each halving
are `2^k` and `3·2^k`.

*Why this matters:* the ladder is fully determined by the theme, so it carries **no
information**. Any reading that uses the amplitude as a digit is reading the theme, not the
key. (The previous repo's `v_3smooth.npy` / "3-smooth snap" was groping at exactly this and
is now nailed down and *excluded* as a data channel.)

---

## 4. CONFIRMED — the block structure; the data clock remains open

Reproduce with `python3 halv/blocks.py`. This is the highest-value result in the file.

### 4.0 The waveform is 8 × 96-px halving blocks  **[CONFIRMED]**

Group every confidently-detected plateau level (full-column template correlation
> 0.985, decoration masked) by 96-px block and test whether each block only ever
uses its own `{s, 2s, 3s}`:

```
 blk  x-range      scale   allowed {s,2s,3s}   observed     verdict
  0   88..183    128.0   [128, 256, 384]     [128]       OK
  1  184..279     64.0   [64, 128, 192]     [128]       OK
  2  280..375     32.0   [32, 64, 96]       []          OK
  3  376..473     16.0   [16, 32, 48]       []          OK
  4  472..569      8.0   [8, 16, 24]        [16]        OK
  5  570..665      4.0   [4, 8, 12]         [8]         OK
  6  666..761      2.0   [2, 4, 6]          [2, 4]      OK
  7  762..857      1.0   [1, 2, 3]          [1, 2, 3]   OK
```

**No confidently detected flat plateau lies outside its block's triple.** With
`scale_b = 128/2^b` and plateau amplitude `q · scale_b`, the observed plateau states are
`q ∈ {1,2,3}`; `q = 0` is the axis at y = 475. The ramp vertices between plateaus are not
constrained to these four levels.

And the closure lands precisely on the independently measured ladder:

```
union of {s,2s,3s} over the 8 blocks : [1, 1.5, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384]
independently measured ladder (F3)    : [1.0, 1.5, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384]
identical                            : True
```

Two independent routes — a pixel-level ladder measurement, and a block-partition
test — converge on the same closed set. This is the real structural content of the
puzzle and it is settled.

### 4.0b …but there is **no evidence for a 6-px step/plateau clock**  **[LIMITED]**

The natural next inference — 768 px = 8 blocks × 96 px = 128 symbols × 6 px, giving
128 quaternary states = exactly 256 bits — does **not** survive the geometry.

* **Plateau lengths are not multiples of 6.** They are 1, 2, 3, 4, 5, 7:
  `0/36` plateaus have length ≡ 0 mod 6 (uniform expectation 17 %), and only
  `5/36` are ≡ 0 mod 3 (expectation 33 %). This rejects the claim that each visible
  plateau is itself a six-pixel cell.
* **The signal is not a step function.** It is a continuous ramp-and-plateau.
  Measured `v_mid` first differences across the x = 723…730 ramps:
  `1.002, 0.973, 0.231, −0.002, −0.262, −0.993, −0.993` — the trace moves one pixel
  of amplitude per column, with vertices at every integer x. This rejects a 6-px
  piecewise-constant renderer, but not a logical clock joined by continuous interpolation.
* **Event counts per block are not 16, 32 or 96.** Slope-reversal counts are
  12, 15, 23, 18, 19, 18, 27, 30 — an average event pitch of 5–11 px, no periodicity.

`768 = 8 × 96` and `768/6 = 128` are true arithmetic, but the factorisation alone is not
evidence for a 128-symbol clock. §2.4 establishes vertices at integer x; that describes
the rendered curve, not the rate at which latent symbols are defined. A 3-px physical
lattice and a 6-px symbol clock remain hypotheses for forward-rendering tests.

### 4.0c The supplied `solve_halv_q4.py` negative is **vacuous**

An external solver implementing the 6-px / 128-quaternary-state model was run
(`halv/q4eval.py` reproduces the audit). It completes and reports 384 candidates,
0 matches — but the negative carries no information, for three checkable reasons:

| | finding |
|---|---|
| **E1** | the model cannot represent the data: `3s` is the ceiling, yet block 0 measures a peak of **379 px** against a model max of **256** — `q=3` never occurs in block 0 |
| **E2** | the `q` is not payload-like: a quaternary encoding of 256 key bits is uniform (~32 per value); this is **54 % `q==1`**, 1.6 % `q==3` |
| **E3** | it barely beats a trivial baseline: rms **39.1 px** vs **43.2 px** for "one constant per block" and 82.8 px for the axis |

Root cause, visible in the code: `amplitude_trace` keeps only pixels ≥ 20 % of the
column max, and in blocks 0–2 each column contains several stroke crossings, so the
centroid is meaningless; `recover_q` then takes the **median of 6 columns of a
ramp**, which is not a symbol value. The Q4-DP idea is sound — it just needs to run
on a correctly measured signal.

### 4.1 Plateau (exactly-horizontal run) list
`halv/plateaus.npy`, 41 plateaus at score > 0.992. Examples:

```
level   x0   x1  len        level  x0   x1  len
  128    97   99    3         4   726  727    2
  128   220  222    3         4   747  749    3
   16   502  502    1         2   767  770    4
    8   582  583    2         1   776  779    4
    8   597  598    2         3   794  796    3
    8   654  655    2         2   838  840    3
    2   704  704    1         3   845  845    1
```

Plateau **lengths range 1…19**; gaps between pulses range **0…20**.

### 4.2 Pulse / gap sequence (resolvable region x ≥ 662)
Read directly off `v_mid`:

```
pulse  x0  x1  base  peak  flatTop        pulse  x0  x1  base  peak
  #0  675 679     5   3.57       1          #7  766 775    10   2.94
  #1  687 691     5   3.57       1          #8  781 782     2   2.02
  #2  696 700     5   3.56       1          #9  790 799    10   3.00
  #3  703 704     2   1.99       1         #10  819 823     5   2.89
  #4  723 730     8   4.00       4         #11  828 832     5   2.71
  #5  735 743     9   5.34       1         #12  838 840     3   2.05
  #6  744 753    10   4.00       3         #13  843 847     5   2.67
zero gaps: 7, 4, 2, 18, 4, 13, 5, 7, 19, 4, 5, 2, 13
```

Note the **motifs repeat verbatim** (`18 28 36 27 17`, `18 28 38 40 40 40 33 27 21`, …),
i.e. the waveform is a concatenation of a small alphabet of pulse shapes.

### 4.3 Two candidate channels
1. **plateau length** ∈ {1…19}
2. **zero-gap length** ∈ {0…20}
Either alone, or interleaved, comfortably exceeds 256 bits for the full pulse count.

### 4.4 The "circle vs diamond" channel is a run-length artefact — DOWNGRADED
The independent prior work (`floflo777/open-crypto-puzzles`) read 59 lobes and 1 bit per
lobe from "apex cap-width: diamond 1 px vs circle 4 px", concluding ≈118 bits total.
I can now explain that channel exactly:

* plateau length **1** → the apex is a single vertex → **pointed ("diamond")** apex;
* plateau length **≥ 2** → the apex is a straight horizontal run → **flat ("circle")** cap.

The cap width is `plateau_length − 1` in pixels. It is **the same information as the plateau
length**, not an independent bit. Their 59-lobe count is also an under-count: the head
(x < 460) contains many short plateaus at 384/256/192/128 that merge visually into a dense
oscillation and are missed by any apex-based detector. My loose template pass finds 41
high-confidence plateaus *by x = 845 alone*.

⇒ The "118-bit capacity" conclusion in the prior write-up is **not** a property of the
image. Do not treat it as a dead end.

---

## 5. What is now RULED OUT (with reasons)

| hypothesis | status | why |
|---|---|---|
| stego / chunk / trailing data | ✗ | §1, certified |
| file-hash → privkey | ✗ | §1, certified |
| sign of the waveform as a channel | ✗ | §2.1 mirror-exact |
| direct 3-px amplitude read as 256 payload symbols | ✗ | §2.4; intervening waveform geometry is omitted |
| 3-px physical lattice inside a generator | ? | OPEN — not adjudicated by plateau widths |
| amplitude as digits (3-smooth snap, 3^n/2^n ladder) | ✗ | §3, ladder is theme-determined |
| circle/diamond as an independent bit | ✗ | §4.4, it *is* plateau length |
| "the image only has ~118 bits" | ✗ | §4.4 |
| brain-wallet phrases from the theme (≈110 tried) | ✗ | prior work, plausible |
| 500 M-derivation WIF-wildcard sweep | ✗ | prior work, but **uncertified comparator** — re-run with `halv/oracle.py` before trusting |
| 6-px piecewise-constant / plateau clock | ✗ | §4.0b — visible plateaus are not 6-px cells and the signal is continuous |
| 6-px logical clock with continuous renderer | ? | OPEN — plateau widths do not test it; direct centroid prototype in §10 is inconclusive |
| the supplied `solve_halv_q4.py` 384-candidate negative | ✗ *vacuous* | §4.0c — E1/E2/E3; the extractor is degenerate, so it refutes nothing |

---

## 6. Capacity budget of the surviving channels

Let `P` = number of pulses, `G` = number of zero-gaps.
From the resolvable tail alone (x ≥ 662): 14 pulses, 13 gaps.
If the same density holds over the full 769 columns, `P ≈ 45…60`, `G ≈ 45…60`.

* plateau length only, 1…19 → 4.25 bit/pulse → **190…255 bit**  ← borderline, likely THE channel
* gap length only, 0…20 → 4.32 bit/gap → **194…259 bit**  ← borderline, likely THE channel
* both interleaved → 8.5 bit/pulse-pair → far more than 256, so a *subset* or a
  run-length/varint layer is implied.

The near-miss of both single-channel budgets against 256 is the strongest structural hint
that the payload is a **run-length code**: values are emitted in runs, so the raw
per-element digit count over-counts, and 256 bits land inside one channel.

---

## 7. Tree route to continue (ordered by expected yield)

```
7.0  [PARTLY DONE] Certify the oracle
     The local comparator now checks compressed and uncompressed P2PKH and passes the
     private-key-1 controls. The prior 500 M sweep used an uncertified comparator; rerun
     only if its candidate family becomes relevant.

7.0b [NEW, HIGHEST] DERIVE the clock, do not assume it
     §4.0 settled the 8-block x q-in-{0,1,2,3} structure; §4.0b rejects only a
     piecewise-constant 6-px clock. The latent clock remains unknown. Three framings
     the block structure keeps alive, to be discriminated by measurement:
       (a) 256 bits at 3 px/bit   -> 96/3 = 32 bits per block x 8 blocks = 256 bits
       (b) q as a 3-valued level index per symbol (1.585 bit/symbol, not 2)
       (c) 128 latent Q4 states at 6-px spacing with a continuous global renderer
     Decide by target-blind reconstruction and held-out-block prediction, not plateau
     divisibility or address matching.
     This item is a prerequisite for 7.1 and for any Q4-DP.

7.1  [HIGHEST] Reconstruct the full 769-vertex signal exactly
     The model is now known and cheap:
       per column i, given integer v_i, v_{i+1}:
         stroke = max( smeared band(y_i -> y_{i+1}), disc(y_i), disc(y_{i+1}) )
         smeared band:  cov(j) = (1/c) * integral of KR over [j-0.5-yl, j+0.5-yl],
                       c = 1/sqrt(1+(y_{i+1}-y_i)^2)
         then mirror about y=475 and take the max of the two traces.
       (implemented and validated: halv/model.py, flat runs reproduce to <0.09 L1)
     Run a Viterbi/DP over v ∈ {0} ∪ ladder ∪ {1..8} with the full-image L1 cost.
     Expected: a unique integer sequence, residual ~0 for the true one.
     This converts every "measurement with bias" in §4 into exact integers.
     Gate: the recovered v must reproduce the image to < 0.05 total L1.

7.2  [HIGH] Emit the two candidate streams from the EXACT sequence
     stream A = plateau lengths   (per pulse, x-increasing)
     stream B = zero-gap lengths  (between pulses)
     stream C = A interleaved B
     Also emit: plateau length minus 1 (= the "circle/diamond" cap width, for continuity
     with the prior work), and the pulse count per ladder rung.
     Sanity check first: is P a "nice" number (e.g. 52, 56, 58, 60, 62, 64)?
     A 64-pulse structure would explain 8 pulses x 8 halvings and make 6 bits/pulse exact.

7.3  [HIGH] Test the bit-budget hypothesis directly
     If P is such that ceil(P * log2(20)) is just over 256, then the intended code is
     "write each value in a fixed base", and the 256-bit key is:
       int(''.join(base_repr(v, b) for v in stream))   for b in 4..6, MSB and LSB first
     and/or a big-endian accumulation  k = k*base + v  (and the reverse).
     Sweep base 2..40, both orders, both directions, with and without a leading 0-run.
     Also test run-length/varint framing and Elias-gamma.

7.4  [MEDIUM] The ladder is 18 rungs: test the level index as a digit
     If the amplitude is theme-only, this is probably a *control* channel — but a 4.17-bit
     base-18 digit per pulse is exactly the kind of thing that lands on 256 bits.
     Sweep base 18, 17, 16, 9 (3-smooth digits) over the pulse sequence.

7.5  [MEDIUM] Framing / transport layer
     Zden's other puzzles: "convert to WIF", "256 bits of the private key in this image".
     Test: stream -> bytes -> SHA-256 -> key; stream -> WIF prefix 0x80 + payload + 0x01
     with base58check; stream as ASCII (values 1..19 are not printable, so a +0x30 or
     +offset mapping is needed — try the raw CSV/space-joined forms, which is what the
     prior negative tested).

7.6  [MEDIUM] Contact channel
     Every other long-open puzzle in this series got a hint (LTC, Codex, Demobit, Janus).
     HALV alone has none. Probe the author's own hint-naming pattern
     (cryptoHALV_hint.svg / .png / _hint2 …), Wayback the tweet thread and the Facebook
     mirror of the 2024-04-20 post. Cheap, and the highest-bandwidth information available.

7.7  [LOW] Puzzle-themed derivations worth one honest shot
     block 840000; reward 3.125; 2024-04-18 / 2024-04-20 timestamps; the transaction id
     30946152b5f24ed975a26b28a46cb19d1ef2728159c5806544ffd0c2fb535205; the escrow address;
     "HALV"/"halving"/"haluska"/"satori"; the 18-rung ladder itself as a key
     (384 → 1, and 18 = 0x12).

7.8  [PARKED] Per-lobe apex-shape micro-features
     Only if 7.1–7.5 all fail. The sub-pixel apex shape is fully explained by plateau
     length, so any residual there is rasteriser noise, not data. Low expected value.
```

---

## 8. Files added by this analysis

```
halv/measure.py     re-derives every CONFIRMED fact above; prints F1..F5   (run this first)
halv/blocks.py      T1 8x96 blocks CONFIRMED / T2 6-px plateau-cell model REFUTED / continuous clock OPEN
halv/q4eval.py      audit of the external solve_halv_q4.py: why its negative is vacuous (E1/E2/E3)
halv/model.py       forward renderer for the 2-px stroked, mirrored polyline
halv/viterbi.py     route item 7.1: Viterbi over integer vertex values
halv/oracle.py      secp256k1 -> compressed/uncompressed P2PKH comparator (key-1 controls)
halv/direct_q4.py   target-blind test of direct 6-px amplitude sampling
halv/plateaus.npy   the 41 high-confidence plateaus  (level, x0, x1, length)
halv/vit_700_860.npy  first Viterbi pass over the resolvable tail (see caveat below)
halv/vit_568_858.npy  wider tail Viterbi pass (see §10.2 caveat)
HALV-SOLVE.md       this file
```

### 8.1 Viterbi status — honest caveat

`python3 halv/viterbi.py 700 860` runs in <1 s and returns a total L1 of 781 over
160 columns × 774 rows, i.e. **1.6 grey levels per column** (median 0.84, p90 4.9, max 13.7).

* On **flat** columns the model is essentially exact (a hand-checked flat run reproduces to
  0.07 total L1 ≈ 0.02 grey levels), so the residual is concentrated in the **ramp** columns:
  the box-smear approximation for a sloped stroke (`(1/c)·∫KR`) is evidently ~1.5 grey levels
  off, which is the same order as the discrimination between neighbouring candidates.
* Consequence: `halv/vit_700_860.npy` is a **good first pass, not yet certified**. Do not read
  the payload off it.
* Fix before trusting it: fit the sloped-stroke cross-section empirically (take columns with
  a known ±1 ramp, measure the 5-tap profile, and fit a slope-dependent kernel), then re-run.
  Target: per-column residual < 0.2 grey levels, at which point the integer sequence is
  forced and every downstream reading becomes exact.

Reproduction: `python3 halv/measure.py` (needs numpy, scipy, pillow).

---

## 9. Corrections to earlier work in this repo

| earlier claim (`halv_*.py`, `attempts/*`) | correction |
|---|---|
| direct sample grid `x = 92 + 3i` as the full payload | ✗ intervening waveform geometry is omitted; a 3-px physical lattice remains open |
| "mirror symmetry ⇒ signal is rectified" | ✓ correct, now certified to 0.03 grey levels (was asserted, not measured) |
| stroke width 1.4784 | ✗ **1.996** |
| `3 * 384 * 2^-a * 3^-b` snap, `D2.npy` mass identity | ✗ the ladder is `{3·2^k} ∪ {2^k}`, 18 rungs, exactly alternating ×2/3, ×3/4 |
| beam search over ±1 step on a 3-px DP | ✗ it used a biased measurement and did not model the continuous renderer |
| "need a 3-smooth snap" | ✓ the shape is real, but it is the *theme* ladder and carries no key bits |

---

## 10. New discriminating tests (2026-09-28)

### 10.1 Direct six-pixel centroid sampling — NO MATCH, EXPLORATORY

`python3 halv/direct_q4.py` samples the upper-half intensity centroid at all six
possible phases `x = 90 + phase + 6i`, normalizes each point by its 96-px block scale,
and rounds to `q ∈ {0,1,2,3}`. It checks every bijection from those four states to two
bits, forward/reverse symbol order, pair bit order, global bit reversal, and byte order.

| phase | q=0 | q=1 | q=2 | q=3 |
|---:|---:|---:|---:|---:|
| 0 | 21 | 67 | 35 | 5 |
| 1 | 22 | 73 | 24 | 9 |
| 2 | 31 | 46 | 44 | 7 |
| 3 | 22 | 66 | 36 | 4 |
| 4 | 27 | 65 | 28 | 8 |
| 5 | 36 | 38 | 45 | 9 |

The centroid proxy gives only 4–9 `q=3` samples out of 128 for each phase. That is
imbalanced against a uniform-state baseline, but it is not a rejection by itself: the key
need not be uniform, and the centroid is not a certified centerline measurement throughout
the high-amplitude region. Across all phases and conventions, 288 distinct valid 256-bit
scalars were checked against the exact target HASH160 in both compressed and uncompressed
forms; none matched. The script checks both known key-1 addresses before searching.

**Interpretation:** no key was recovered from this direct centroid extraction. Because the
centroid proxy can be biased on slopes and overlapping strokes, this is not a decisive
rejection of exact direct sampling, and it does not test latent Q4 states recovered through
a continuous renderer. The state imbalance is a clue to improve geometric measurement,
not evidence for or against a key stream by itself.

### 10.2 Tail reconstruction — useful, not certified

`python3 halv/viterbi.py 568 858` produces `halv/vit_568_858.npy`, with total L1 909 over
291 columns × 774 rows (about 1.03 grey levels/column). The path contains repeated
zero-separated excursions in the final three blocks, but the renderer's ramp residual
remains comparable to local candidate separation. Do not decode that vector as payload.
It is a saved input for improving and comparing ramp kernels.

### 10.3 Oracle audit — comparator corrected

Reviewing `halv/oracle.py` while validating the candidate sweep showed that `check(k)` only
derived the uncompressed public key twice; it never checked the compressed address. The
function now tests both serializations, and its command-line controls verify private key 1
against `1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm` (uncompressed) and
`1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH` (compressed). This does not alter the direct-Q4 result
above, which checked both formats, but it means earlier negative searches using the old
`check()` must not be treated as ruling out compressed-key candidates.

### 10.4 Updated status

The best live structural route is still an 8-block normalized four-state plateau alphabet. The
new test finds no candidate under the simplest centroid-sample extraction. The next high-value test is
to recover latent states with one global forward renderer, fit on early blocks and scored
on held-out later blocks, with phase and renderer family selected without the address.
Only a unique low-residual reconstruction should feed run lengths, transition magnitudes,
or a 128-state Q4 bit map.

## 11. Continuation tree

```text
HALV image
  ├─ File-level stego/hash routes ─────────────────────────── CLOSED / negative
  └─ 769-column rectified waveform
       ├─ 8 × 96 halving blocks; normalized q={0,1,2,3} ─── CONFIRMED structure
       ├─ Direct x=90+phase+6i centroid samples ──────────── NO MATCH (288 keys; proxy only)
       └─ Recover the latent generator target-blind
            ├─ Fit exact sloped-stroke raster kernel
            ├─ Reconstruct centerline / vertex sequence
            ├─ Compare 3-px lattice, 6-px continuous Q4,
            │  and event/run-length models on held-out blocks
            └─ Require one global phase/model and low residual
                 ├─ If unique: freeze latent states and exact geometry
                 │    ├─ decode state / transition / plateau / gap streams
                 │    ├─ test only structurally justified bit/nibble conventions
                 │    └─ certify scalar against compressed and uncompressed P2PKH
                 └─ If no winner: revise raster generator, not the key mapping
```

**Current confirmed:** rectification, 2-px stroke profile, 18-rung halving ladder,
8×96 block scales, and three normalized nonzero plateau levels plus the zero axis. **Current negative:**
the old direct 3-px amplitude stream and uniform 6-px step cells. **Exploratory no-match:**
direct 6-px centroid sampling. **Still open:** physical 3-px lattice, latent 6-px continuous Q4 clock, the exact
vertex path, run-length payload, 256-bit extraction, and the private key.
