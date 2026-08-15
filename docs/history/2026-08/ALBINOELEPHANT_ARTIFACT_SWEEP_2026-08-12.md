> **Historical snapshot.** This is a point-in-time investigation journal, not
> current project state. Use [the current overview](../../OVERVIEW.md),
> [priorities](../../status/PRIORITIES.md), and
> [findings ledger](../../status/FINDINGS.md) for present conclusions.

# albinoelephant artifact sweep — 2026-08-12

## Scope

This follow-up re-analyzes the contributor-supplied 32 KiB Corolla DataFlash and
TSKM CAN oracle beyond the initial raw-key/triplicate-object pass. Exact EPS
F181/calibration remains unknown; all `4512000` owner names and descriptor
semantics are reference labels unless independently corroborated here.

Primary artifacts:

- `community/albinoelephant/dump_ff200000_ff208000.bin`
- `community/albinoelephant/can_oracle.ndjson`
- `community/albinoelephant/public_route_secoc_oracle.ndjson`

Machine-readable structural result:

- `data/generated/corolla_2023_albino_dataflash_analysis.json`

Verification:

- `tests/verify_albinoelephant_corolla_dataflash.py`
- `tests/verify_toyota_dataflash_analyzer.py`

## 1. CAN-oracle session boundary

The supplied TSKM oracle contains 1,232 `0x00F` rows, 616 on bus 0 and 616 on
bus 2, with no protected-message rows. All decode to `TRIP_CNT=0xD0D`. This is
the closest local oracle from the same TSKM investigation, but it is **not
proven to be the same EPS runtime epoch as the dump**. CAN capture and DataFlash
dumping are separate mutually-exclusive jobs; the dump then drives the EPS
through programming mode, SecurityAccess, code upload, and RAM execution.

The repository-derived public-route oracle contains genuine bus-1 traffic:

- `0x00F`: 588
- `0x116`: 2,499
- `0x24D`: 59

Its synchronization traffic has `TRIP_CNT=0xCE9`. It is therefore a different
ignition freshness epoch from the local TSKM oracle (`0xD0D`). Pairing this public-route traffic
with the dump is useful historical same-vehicle evidence, but protected-key
negatives from that pairing require the explicit assumption that the protected
key remained stable between sessions.

The old TSKM collector's Sienna-shaped bus/ID filter explains the sync-only
artifact; `0 protected` was a collection-profile false negative, not evidence
that the vehicle lacked protected traffic.

## 2. Cryptographic negatives

### Local TSKM synchronization domain

All 32,753 overlapping 16-byte positions in the dump collapse to 23,277 unique
raw windows. With `min_entropy=0`, all 23,277 were tested against the supplied
local TSKM `0x00F` oracle.

Result: **zero synchronization-key matches**.

This is the strongest local key-storage comparison available from the supplied
artifacts: the dump contains no raw 16-byte value equal to a key that
authenticates the nearby TSKM synchronization capture. Because capture and dump
are separate jobs with a programming transition between possible runtime
epochs, this excludes a static raw key hypothesis, not a session-derived key.

### Public-route protected domains

The same 23,277 unique raw windows were tested independently against the
public-route synchronization, `0x116`, and `0x24D` domains.

Result: **zero matches in every domain**.

The `0x116`/`0x24D` part is cross-session evidence as described above.

### Simple transformed representations

Every unique raw window was additionally transformed by each of:

- XOR `0x55` per byte;
- XOR `0xAA` per byte;
- bitwise NOT;
- reverse all 16 bytes;
- reverse bytes within each 32-bit word;
- reverse bytes within each 16-bit word.

Each transform produced 23,277 unique candidates for the tested corpus. None
survived even one public-route synchronization/`0x116`/`0x24D` cryptographic
probe.

This rules out those obvious encodings/endian representations. It does not
bound arbitrary AES/KDF/seed-dependent derivations.

Known triplicate objects were also decoded through raw/XOR55/XORAA before
sliding 16-byte tests; no decoded object-15 second field or other decoded
16-byte chunk authenticated the retained route traffic.

## 3. Complete reference NvM geometry transfer

Applying all 122 physical extents from the `8965B4512000` map finds **60
committed Corolla records**:

- triplicate class: 9
- checkpoint class: 51

All 51 committed checkpoint records have a valid `generation/~generation` pair
at the inverse location predicted by the reference geometry. Forty-nine map to
reference-enabled owners.

### Reference-disabled owner 28 is active on this specimen

The remaining two committed checkpoint records are:

| Storage | VA | Reference owner | Ref enabled | Generation | Inverse offset | Inverse |
|---:|---|---:|---|---|---:|---|
| 117 | `0xFF204280` | 28 | no | `0x25` | `+0x40` | `0xFFFFFFDA` |
| 118 | `0xFF204200` | 28 | no | `0x24` | `+0x40` | `0xFFFFFFDB` |

Both end in `0xAAAAAAAA`. They are adjacent generations of a coherent two-slot
ring. Reference owner 28 has an 8-byte data length, but the Corolla records have
nonzero bytes well beyond that boundary (24 and 22 nonzero bytes respectively
in the reference-padding interval before the inverse word).

Therefore the shared conclusion is narrower and stronger than “the Sienna map
partially fits”:

1. the physical page/storage geometry transfers very well;
2. the checkpoint envelope format transfers;
3. descriptor enablement/data semantics are calibration-specific and cannot be
   imported wholesale from `4512000`.

## 4. Short-record header integrity recovered

The second physical header u16 at record `+2` was previously kept opaque. The
additional specimen plus live firmware disassembly resolves it.

`FUN_000762C6 @ 0x762C6` is an unsigned byte-sum helper. For NvM payload lengths
below `0x21`, writer `FUN_000765D0 @ 0x765D0` constructs the 16-bit header value;
reader `FUN_0007668A @ 0x7668A` recomputes it and returns `0xFFFC` on mismatch.

For every committed short record observed across both DataFlash images, the
stored value is exactly:

```text
header_u16_at_+2 = 0xC000
                 + sum(0xAAAAAAAA commit-marker bytes)   # 0x2A8
                 + sum(storage_index as two little-endian bytes)
                 + sum(encoded payload bytes)
                 mod 2^16

# committed-record shorthand: base = 0xC2A8
```

Cross-image corpus:

- `4512000`: 18 committed short/triplicate records;
- Corolla: 9 committed short/triplicate records;
- total: **27/27 satisfy the formula**.

For longer records the writer formats header `+2` as zero and the reader skips
the short-block checksum comparison. Across the two images, **101/101 committed
checkpoint records have `+2 == 0x0000`**.

This lets the analyzer strengthen triplicate validity from outer commit markers
alone to outer markers plus the actual reader-enforced additive checksum.

## 5. Region-level characterization

Using the four `4512000` reference page ranges only as physical boundaries:

| Range | Corolla observations |
|---|---|
| lower `0x0000..0x3FFF` | 255 mixed 64-byte pages + 1 all-zero page; all 256 byte values occur; no aligned page ends in a known `AAAAAAAA` record marker |
| checkpoint `0x4000..0x6BFF` | 173 mixed + 3 all-zero pages; 51 coherent committed checkpoint records at mapped extents |
| triplicate `0x6C00..0x77FF` | all 48 pages mixed; 9 committed short records, objects 0/2/5 |
| tail `0x7800..0x7FFF` | exclusively `00000000`/`FFFFFFFF` 32-bit words; 320 zero words + 192 all-FF words |

The lower half is substantially non-erased-looking in this readback, but no
known NvM record framing was found there. Because RH850 DataFlash readback for
unallocated/erased areas is already bounded as potentially undefined, mixed
bytes alone do **not** prove an additional persistent allocation.

The tail preserves the same coarse all-zero/all-FF word-only character as the
`4512000` protected/reserved tail, although its bitmap differs. It reveals no
raw key material and should not be interpreted as a readable ICU-S key store.

## 6. What is now established

The supplied dump is more valuable as a **cross-calibration storage-format
specimen** than the first pass captured. It independently corroborates:

- the 122-record physical page geometry across a large fraction of active
  records;
- the checkpoint generation/complement envelope;
- raw/XOR55/XORAA triplicate storage at the same locations for active objects;
- the short-record additive integrity algorithm;
- variant-specific descriptor enablement/provisioning at owner 28.

For key storage, it excludes a static raw synchronization key matching the
local TSKM capture from all 16-byte DataFlash windows and excludes several
obvious transformed representations against historical route traffic. It does
not prove key continuity across the separate capture/programming jobs and does
not exclude an ICU-S/HSM-owned key, another address space, or a more complex or
session-derived key.

## 7. Highest-value remaining evidence

1. Exact EPS `F181` / software identity.
2. Corolla CodeFlash, which would permit target-specific recovery of the NvM
   descriptor tables and resolve what the active 117/118 object actually is.
3. If the vehicle is revisited, make a **controlled paired capture around the
   dump**: retain full-bus synchronization/protected CAN immediately before the
   programming transition and again after recovery/reset, together with the new
   DataFlash and exact `F181`. That would directly establish key continuity (or
   rotation) across the transition instead of assuming it.
