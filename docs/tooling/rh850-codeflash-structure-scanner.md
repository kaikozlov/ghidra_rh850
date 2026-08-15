# RH850/P1M-E CodeFlash structural fingerprint scanner

> **Scope:** calibration-independent triage of future RH850/P1M-E CodeFlash
> images (anchors recovered on Sienna `8965B4512000`)
>
> **Document type:** tooling
>
> **Status:** active
>
> **Evidence source:** firmware-static structural anchors
>
> **Confidence:** triage only — every match is a candidate, never a transfer claim
>
> **Tool:** `tools/analyze_rh850_codeflash_structure.py`
>
> **Verification:** `tests/verify_rh850_codeflash_structure_scanner.py`

## Purpose

When a new EPS calibration arrives, the first question is which already
recovered mechanisms might exist in it. The scanner answers that offline with
**structural anchors** — byte patterns whose meaning is known from verified
findings — rather than inherited per-calibration offsets. It deliberately
contains no software-ID offset fallback table: targets are identified by
their own structure.

## Anchors scanned

| Anchor class | Signals | Provenance |
|---|---|---|
| Image geometry | exact bare 1 MiB CodeFlash vs `0x108000` DataFlash+CodeFlash concatenation; truncated/oversized rejection with explicit diagnosis | shared `validate_codeflash_geometry` with the SecOC patch-image resolver |
| Boot validity | self-describing boot-CRC descriptors; fixed `0x5AA5A55A` markers | ARCH-003 |
| RAM-exec package gate | download-window base `FEBF0000..FEBF0FFF`; post-link package descriptor pair; callback-pointer slot | SEC-BOOT-005/009, MEM-SAFE-001 |
| XCP `0x7F7/0x7F8` family | route constants; page-copy window `FEBF7C00..FEBFF9EF` and shadow-window bounds `FEBF7C00..FEBFFBFF`; eight-byte command-map records (selector byte + little-endian callback pointer) | COM-004/COM-005 |
| SecOC semantic gate | byte-level prefilter for 32-bit-displacement byte loads feeding a `cmov`-family materialization | SecOC resolver prefilter |

## Output

A JSON report (and human summary) listing, per anchor class, matched virtual
addresses and the byte evidence. Presence of an anchor is a **triage
candidate**: it flags where to point Ghidra first. Absence is weak evidence
only. Nothing in the report asserts that a mechanism *functions* in the new
image — every mechanism must be re-verified against the new firmware bytes.

## Boundary

- The scanner never imports into Ghidra and never mutates the input image.
- The optional SecOC-gate prefilter is deliberately coarse (byte-level); the
  authoritative resolution path remains the calibration-independent semantic
  resolver over a disposable project.
- Cross-calibration statements stay **hypothesis** in `docs/variants/` until
  verified on the target image (scope discipline per AGENTS.md).
