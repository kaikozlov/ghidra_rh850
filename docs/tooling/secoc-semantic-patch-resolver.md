# SecOC semantic patch resolver

> **Scope:** host-side discovery of the SecOC Gate-2 delivery predicate and
> boot-CRC geometry without calibration-specific target offsets
>
> **Status:** corrected Level-1 structural resolver verified on
> `8965B4512000` and independently transferred to tracked Corolla
> `8965H1202000`; every additional calibration still resolves fail-closed
>
> **Verification:** `tests/verify_secoc_semantic_patch_resolver.py`

The durable target is not a raw Sienna byte string or software-ID table. It is
the decision that consumes the command-7 verification result and selects the
verified PduR/COM delivery fallthrough versus mismatch/retry bookkeeping.

The earlier resolver forced the forward BNE target. CORR-064 establishes that
this was backwards: command-7 result `0` is verification success, so the stock
BNE is **not taken** on success. The corrected resolver therefore patches the
CMP immediately before that BNE and leaves the branch itself untouched.

## 1. Semantic discovery

`ghidra/scripts/investigate/ResolveSecocAcceptanceGate.java` scans every
recovered function for:

```text
byte READ(result)
  -> cmp zero
  -> cmovne 1               ; boolean := (result != 0)
  -> later state/freshness call(s)
  -> cmp zero, same boolean
  -> forward BNE            ; taken when result != 0
       fallthrough: call(s) ----\
                                  -> common forward join
       branch target: call(s) ---/
```

Fail-closed constraints include:

1. when the RAM result cell is mapped, it must also be passed by address
   elsewhere, distinguishing an output/result cell from ordinary state;
2. the same materialized boolean must survive to the final predicate;
3. the predicate must be a two-register RH850 CMP followed immediately by a
   forward `bne`;
4. result-zero must be the fallthrough polarity represented by this Level-1
   shape; other compiler polarities are rejected rather than guessed;
5. both arms must contain calls and converge;
6. exactly one candidate must survive.

The patch is synthesized from the decoded RH850 Format-II CMP itself. Operand 0
is validated against bits `[4:0]`, operand 1 against bits `[15:11]`, and the
replacement copies operand 0 into operand 1 while preserving the opcode. In
other words, `cmp A,B` becomes `cmp A,A`. This forces equality and therefore
prevents the following BNE from taking the result-nonzero mismatch edge.

No Sienna target VA, MAC-result address, function address, CRC range, or fixup
address is embedded in the resolver.

### Sienna result

Both the fully annotated project and a fresh bare CodeFlash import resolve:

```text
result global             FEBE555C       (unmapped in bare import)
load                      0x8E69E
booleanize                0x8E6A4        r26 := result != 0
pre-gate call             0x8E6C0
patch CMP                 0x8E6C6
overwrite                 e0 d1 -> e0 01
preserved BNE             0x8E6C8        9a 0d
verified fallthrough      0x8E6CA
mismatch branch target    0x8E6DA
join                      0x8E6E2
```

The output schema is `toyota-secoc-semantic-target-v2` and explicitly carries
`verify_result_polarity = zero-is-verified-ok-nonzero-is-not-verified` plus the
preserved BNE and both arm addresses.

Committed fixtures:

- `data/generated/secoc_gate_resolution_4512000.json` — annotated project,
  mapped result provenance;
- `data/generated/secoc_gate_resolution_4512000_minimal.json` — fresh bare
  CodeFlash import, same target/CFG with RAM provenance explicitly unmapped.

The program SHA-256 is part of the resolution and must equal the exact supplied
CodeFlash image before a manifest can be built.

### Corolla `8965H1202000` foreign result

The tracked albinoelephant CodeFlash provides the first exact foreign-image
regression. A fresh unannotated import with normalized SHA-256
`0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f`
resolves exactly one homolog without adding any target address:

```text
Gate-2 function           0x88C16
booleanize                0x88C40
pre-gate call             0x88C5C
patch CMP                 0x88C62
overwrite                 e0 d1 -> e0 01
preserved BNE             0x88C64        9a 0d
verified fallthrough      0x88C66
mismatch branch target    0x88C76
join                      0x88C7E
```

Its stock target CRC descriptor is clean rather than anomalous: region
`0x18000..0xFFDF0` validates with stored fixup `0xAD59D70C`. Applying the
resolved CMP neutralization gives prefix CRC `0x22A0EB88`, fixup `0xDD5F1477`,
and final residue `0xFFFFFFFF`. This proves the semantic target + CRC-resigning
pipeline transfers across these two exact images; it does **not** imply the
foreign target has Sienna's configured CAN profiles. Its queue census is
separately resolved as `0x00F/0x0D7/0x0B6`.

Committed foreign fixture:
`data/generated/secoc_gate_resolution_8965H1202000_minimal.json`. The exact raw
corpus and interpretation are in
[../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md).

## 2. Manifest and semantic rejection of the old patch

`tools/build_secoc_patch_manifest.py` accepts only resolver schema v2 and the
operation `cmp-second-register-to-first-force-fallthrough`. Before checking the
image preimage it independently verifies that:

- the patch is one 2-byte RH850 instruction;
- opcode bits are preserved;
- the replacement's second register equals the original first register;
- the original operands were different;
- the patch address is the resolved Gate-2 CMP;
- a preserved BNE with the recorded bytes follows;
- verified-fallthrough and mismatch-target provenance are present.

This prevents the superseded `0x8E6C8 9a0d -> 950d` branch patch from being
accepted even if someone relabels its operation as the new one. That old patch
is retained only in negative regression coverage because it forces the
mismatch arm.

## 3. Dynamic boot-CRC discovery

The manifest builder scans raw CodeFlash for self-describing CRC records:

```text
region_start
region_length
pointer_to_embedded_region_start
pointer_to_embedded_region_length
```

It selects the unique descriptor covering the semantic patch, derives the
terminal fixup as the final four bytes of the CRC range, discovers a nearby
validity marker, derives FCU block geometry, and verifies the terminal-fixup
construction:

```text
fixup = CRC32(prefix) XOR 0xFFFFFFFF
CRC32(prefix || LE32(fixup)) = 0xFFFFFFFF
```

The published `4512000` target region contains the separately documented
SECOC-044 one-bit artifact anomaly, so the builder requires a valid sibling
descriptor to prove the scheme rather than silently treating the target region
as clean.

For the corrected patch:

- committed published image: prefix `0x23247E0C`, fixup `0xDCDB81F3`;
- reconstructed-clean image: prefix `0xBE36F00D`, fixup `0x41C90FF2`;
- final resigned residue: `0xFFFFFFFF`.

These are offline fixtures only. Live deployment recomputes CRC from live
CodeFlash after target-block RMW. The old `0x91698386` fixup belongs to the
superseded wrong-direction branch patch.

## 4. Arbitrary-image workflow

```bash
tools/resolve_secoc_patch_image.sh \
  /path/to/CodeFlash.bin \
  build/out/secoc_patch_manifest.json
```

The wrapper validates bare 1 MiB P1M-E CodeFlash geometry before analysis,
creates a disposable unannotated project under `build/work/secoc-targets/<sha>/`,
runs the read-only semantic resolver, joins the resolver SHA to the exact image,
validates patch semantics/preimage, discovers CRC geometry, and emits a manifest.
The input image is never modified.

Zero/multiple semantic candidates, an incompatible branch polarity, SHA
mismatch, invalid CMP transform, wrong BNE provenance, patch preimage mismatch,
or ambiguous CRC geometry all fail closed.

For the already imported working project, `tools/resolve_secoc_patch.sh` is the
faster developer path and retains the same SHA/image join.

## 5. Transfer boundary

The resolver is now annotation-independent on Sienna and independently proven on
one exact foreign Corolla image. That is still not evidence that every Toyota
calibration uses the same address or even the same Level-1 machine shape. No
exact 2024 RAV4 Prime or 2025 bZ4X firmware/F181 artifact is present in the
repository.

A 2026-08-16 external field report from yc uses the same local transform
`e0d19a0d... -> e0019a0d...` on newer Toyota vehicles and strongly corroborates
the corrected **direction**, but cannot establish that an arbitrary image can be
patched by offset. Each acquired CodeFlash must run through the semantic resolver
independently.

If a future image yields zero candidates, promote the resolver to p-code/CFG
data-flow rather than adding an offset table. If it yields multiple candidates,
add stronger crypto-result provenance and continue to fail closed.
