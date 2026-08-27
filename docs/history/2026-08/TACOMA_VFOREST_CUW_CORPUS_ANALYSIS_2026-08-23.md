# Tacoma VFOREST CUW corpus analysis — 2026-08-23

## Scope

This pass analyzes the complete local Tacoma CUW corpus under `software/Techstream/cuw/`
using the recovered Toyota Techstream V18 CUW semantics. Raw CUWs remain ignored
external specimens. The tracked artifact
`data/generated/techstream_v18/cuw_tacoma_vforest_corpus.json` is generated
from those packages by `tools/techstream/inspect_cuw_vforest_corpus.py` and is
verified by `tests/verify_techstream_cuw_vforest_corpus.py`.

The corpus is 11 Tacoma ENG&ECT packages, containing 16 CPU images. It spans
2016–2021 application coverage and three integrated VFOREST size classes:

| CPUType | Techstream export | route | logical size | images |
|---|---|---|---:|---:|
| 86 | `VFOREST_2_0M` | `0P5-CAN86` | `0x200000` | 9 |
| 87 | `VFOREST_1_5M` | `0P5-CAN87` | `0x180000` | 2 |
| 89 | `VFOREST_1_25M` | `0P5-CAN89` | `0x140000` | 5 |

These names are Techstream writer/CPU-family labels. They do not by themselves
establish the exact MCU suffix or ISA.

## 1. Every Tacoma member decodes completely

All 16 CPU-image members use the same representation already recovered from
`T-0011-21 / 04C21`:

```text
Format-4 CUW member
  -> ASCII hexadecimal
  -> ZV00/ZV01 record stream
  -> standard LZF expansion where type == ZV01
  -> fixed 0x1000-byte logical blocks
```

Every member consumes its decoded ZV stream exactly. There are no odd nibbles,
trailing bytes, secondary S-record layers, or failed LZF records.

The resulting logical image sizes agree exactly with the Techstream CPU labels:
320 blocks for CPUType89, 384 for CPUType87, and 512 for CPUType86.

The exact package/image hashes, ZV hashes, raw/compressed record counts, source
passwords, new-image passwords, member identities, and fill boundaries are
pinned in the generated corpus artifact rather than duplicated here.

## 2. Multi-CPU package structure is positional

Five packages contain two Format-4 CPU-image members:

- `T-0034-18 - 04B04.cuw`
- `T-0036-18 - 04A61.cuw`
- `T-0022-20 - 04B33.cuw`
- `T-0023-20 - 04B81.cuw`
- `T-0012-21 - 04B82.cuw`

In every one, archive member 1 maps to descriptor `CPU01` and archive member 2
maps to `CPU02`.

The important trap is that both members in one package have the **same archive
member name**: `<CPU01NewCID>_<CPU02NewCID>.txt`. The member name is therefore
package-level and cannot identify the CPU. Tooling must preserve archive order.

The positional mapping is independently constrained by three byte-level facts:

1. member 1 contains the `CPU01` part identity at logical `0x100C`, and member 2
   contains the `CPU02` identity;
2. their expanded sizes match each section's CPUType geometry; and
3. predecessor-password closure works only with this ordering.

Across these packages CPU01 is CPUType89 / `89665-...` / LocationID
`0004000300010720`. CPU02 is CPUType87 in `04B04`, then CPUType86 in the later
packages, with LocationID `0002000100070720`.

## 3. The three real P5-CAN VFOREST routes share one legacy parameter model

The selected `Parameter.ini` rows for `0P5-CAN86`, `0P5-CAN87`, and
`0P5-CAN89` are identical in the security/orchestration fields recovered here:

```text
PasswordAddress                         = 0000100E
ByteOrder                               = 0
CalibrationType                         = 2
EngineTypeFlag                          = 1
FORESTTypeFlag                          = 1
M16CTypeFlag                            = 0
FlagToUseCIDGetterAndFlashWriterDLL     = 0
FlagToUseGetFlashSizeFunc               = 1
WaitTimeAfterIGOn                       = 10000
WaitTimeForIGOFFON                      = 10
FlagToChangeToReprogGWModeForCentralGW  = 1
FlagToCancelAutomaticIGOFF              = 1
FlagToDoIGOFFONAtCPUTypeChange          = 0
CPUTypeWithModeChangeAtCPUTypeChangeFlag= 0
```

Thus the real 86/87/89 packages do not expose distinct credential fields or a
modern dynamic writer selection. CPU type changes image geometry and CheckID
node data; it does not select a different visible authentication schema in the
chosen rows.

The integrated VFOREST route remains the older two-control design established
for `04C21`:

1. four-byte UDS SecurityAccess `27 01/02`, with the recovered legacy
   `key = seed XOR 00 60 60 00`; and
2. an independent proprietary CheckID software-password exchange.

The exact 86 integrated dispatch is already body-pinned by TMS-038. The 87/89
rows join the same integrated VFOREST parameter class; no modern
`ECUAuthKey`, `ServiceAuthKey`, `SeedKey`, `Nonce`, `OffsetAddress`, or
`SecurityProperty2` fields occur in these package descriptors. This is legacy
ENG&ECT evidence and must not be projected onto the tracked modern EPS.

## 4. Software-password semantics generalize across the corpus

For every Tacoma image:

- source/old software passwords decode from descriptor `TargetData` using the
  recovered Toyota index-subtraction transform;
- the new-image password comes from decoded ZV offset `0x100E`;
- `ByteOrder=0` reverses those four archive bytes for the host integer; and
- CheckID emits the integer little-endian, so the final four wire bytes equal
  the four bytes stored in the ZV stream.

The corresponding four bytes appear in the LZF-expanded logical image at
`0x1004`.

Two independent predecessor chains close exactly inside this corpus:

```text
8966304A7100 new password = 0x74B53E44
                         = 04A72 TargetData password for source 8966304A7100

8966304B8100 new password = 0x59CF08BF
                         = 04B82 TargetData password for source 8966304B8100
```

This cross-package equality simultaneously validates the target-data decoder,
new-image password extraction, archive/CPU member ordering, and the semantic
meaning of the source-calibration password table.

## 5. A stable logical-image envelope is now recovered

All 16 VFOREST logical images share the first **`0x1004` bytes exactly**.
The first divergence is the per-image software-password field at `0x1004`.
The common-prefix SHA-256 is:

```text
515a0f447cdf25ce3bab0978087a00162aad66c089c0c2454fd831a19f3a00cd
```

The first full 4-KiB block is identical across all 16 images:

```text
9973b8547c168795f279ae402a0777a08f4791f0a37395a3f74351f48b021eed
```

The common identity structure begins:

```text
logical 0x1000  00 00 00 00
logical 0x1004  per-image software-password bytes
logical 0x1008  9E 5D 12 3A
logical 0x100C  ASCII part identity (for example 89663-04B82-)
```

Every image also has the same 52-byte footer grammar at its own logical end:

```text
B270AD78E88F32B558FEEB58D03B3B1D
00000000
image[0x1004:0x1024]
```

In other words, the footer repeats the password/marker/identity metadata window
from the beginning of the logical image after a fixed 20-byte prefix.

The recurring unused-space word is `E203F133`. Each image has an exact
word-aligned run of that value immediately before its 52-byte footer. For the
CPUType86 lineage the start offsets are:

| CID | trailing fill start |
|---|---:|
| `8966304A6100` | `0x180708` |
| `8966304A7100` | `0x16032C` |
| `8966304A7200` | `0x160350` |
| `8966304B3300` | `0x184A64` |
| `8966304B4200` | `0x164640` |
| `8966304B8100` | `0x18BE08` |
| `8966304B8200` | `0x18BE18` |
| `8966304B9100` | `0x1677EC` |
| `8966304C2100` | `0x18BAF0` |

The generated evidence pins the corresponding CPUType87/89 boundaries.

## 6. Comparative CPUType86 structure

Across all nine 2-MiB CPUType86 images, the only 4-KiB blocks identical in
**every** image are block 0 and blocks 396..510. The latter are the common
`E203F133` fill region. This is a useful boundary: the long-term stable envelope
is small, while the active image body reflects several distinct build streams.

Pairwise changed-4-KiB-block counts, ordered
`A61 A71 A72 B33 B42 B81 B82 B91 C21`, are:

```text
A61   0 385 385 387 385 395 395 385 395
A71 385   0 284 389 355 396 396 359 396
A72 385 284   0 389 355 396 396 359 396
B33 387 389 389   0 389 395 395 389 395
B42 385 355 355 389   0 396 396 359 396
B81 395 396 396 395 396   0  73 396 392
B82 395 396 396 395 396  73   0 396 392
B91 385 359 359 389 359 396 396   0 396
C21 395 396 396 395 396 392 392 396   0
```

The descriptor-defined direct updates are the most informative comparisons.

### 6.1 `04A71 -> 04A72`

`04A72` explicitly lists `8966304A7100` as an accepted source calibration.
The logical images differ in 144,280 bytes (6.88%) across 284 4-KiB blocks.
The changed block ranges are:

```text
1-4, 7, 13-16, 19-21, 25-26, 45, 68-69, 74-76, 78-83,
91-96, 100-102, 104-108, 110-352, 511
```

This is not a simple small calibration-only patch; a large central portion of
the image changed while block 0 and the trailing unused region remained stable.

### 6.2 `04B81 -> 04B82`: controlled two-CPU A/B experiment

This is the strongest comparison in the corpus.

`04B81` and `04B82` are both dual-CPU packages. Their CPU01
`896650410100` member is **byte-identical**, including the decoded ZV stream and
the 1.25-MiB expanded logical image. Only CPU02 advances from `8966304B8100`
to `8966304B8200`.

The CPU02 logical images differ in 135,465 bytes (6.46%) across only 73 blocks:

```text
1-4, 15, 80, 82, 87, 101, 110-111, 113, 120, 124-126, 128,
130-133, 139, 141, 145, 147, 186, 237, 243, 306, 308, 318-319,
355-356, 358-395, 511
```

Many low/mid-image changed blocks differ by only a handful of bytes; for
example some changed blocks contain only 1–15 changed bytes. By contrast,
blocks 362..395 each differ in more than half their bytes, forming a dense
rewritten tail region.

That locality is strong evidence that the reconstructed logical image is
structured. It is inconsistent with treating the entire 2-MiB image as one
opaque cryptographic ciphertext whose bytes avalanche globally after a small
software change.

It does **not** prove that every reconstructed byte is directly executable
native CPU plaintext. A Denso/VFOREST word/block coding or storage transform can
still exist below the LZF layer. The exact MCU-native interpretation therefore
remains bounded.

## 7. What this closes and what it does not

### Closed by this corpus

- all 11 Tacoma CUW containers parse and CRC-check;
- all 16 CPU members decode from ASCII hex and ZV/LZF to exact logical images;
- CPUType 86/87/89 image geometry is validated by real artifacts;
- dual-CPU member association is positional and exact;
- all selected real routes share the same legacy integrated VFOREST parameter
  model;
- old/new software-password semantics generalize to all three size classes;
- predecessor password chains close across two independent update sequences;
- a stable logical header/footer/fill structure is recovered;
- the expanded representation is demonstrably structured and is not behaving
  as whole-image cryptographic ciphertext; and
- the `04B81 -> 04B82` package pair provides a controlled unchanged-CPU /
  changed-CPU differential experiment.

### Still bounded

- exact D76F0xxx MCU suffix and native core/ISA for these packages from
  first-party evidence;
- whether `E203F133` is the physical erased value, a transformed erased value,
  or another VFOREST representation sentinel;
- exact ECU-side LZF decompressor implementation and post-decompression storage
  transform;
- direct native-code interpretation of the expanded image;
- live timing/retry behavior beyond the recovered host parameter model; and
- any transfer of this legacy ENG&ECT security design to modern Toyota EPS.

Most importantly for the openpilot/TSS3 work, none of these packages is a
modern EPS CUW. They contain none of the modern Unified credential fields and
do not choose between the two byte-compatible Unified routes already recovered
for the tracked EPS bootloader. A matching modern EPS CUW remains the highest
value missing artifact.

## Reproduction

```bash
PYTHONPATH=tools/techstream uv run --locked python \
  tools/techstream/inspect_cuw_vforest_corpus.py software/Techstream/cuw \
  --output /tmp/cuw_tacoma_vforest_corpus.json

PYTHONPATH=tools/techstream uv run --locked python \
  tests/verify_techstream_cuw_vforest_corpus.py
```

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-039](../../reference/index.md#finding-tms-039)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
