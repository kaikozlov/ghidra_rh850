# SecOC semantic patch resolver

> **Scope:** host-side discovery of the SecOC authenticated-delivery patch point
> and boot-CRC geometry without calibration-specific target offsets
>
> **Status:** Level-1 structural resolver verified on `8965B4512000`; cross-
> calibration transfer awaits F3/F4/Corolla/RAV4 CodeFlash images
>
> **Verification:** `tests/verify_secoc_semantic_patch_resolver.py`

The persistent Sienna patch recovered in SECOC-043 is a one-instruction change,
but its address (`0x8E6C8`) is calibration-specific. A useful patcher must not
ship a growing `software_id -> address` table or search for the Sienna bytes.
The durable target is the **semantic acceptance decision** that consumes the
MAC result and selects authenticated delivery versus failure/release.

This tooling therefore separates discovery from live flash mutation:

```text
CodeFlash imported in Ghidra
        |
        v
ResolveSecocAcceptanceGate.java
        |
        |  unique machine/CFG/data-flow result + program SHA-256
        v
semantic-resolution.json
        |
        +---- exact CodeFlash.bin
        v
build_secoc_patch_manifest.py
        |
        |  preimage check + dynamic boot-CRC descriptor discovery
        v
patch-manifest.json
        |
        v
future minimal live FCU RMW payload
```

The live payload should remain deliberately small: verify the manifest/preimage,
read-modify-write the resolved target block, recompute the CRC from **live**
CodeFlash using the resolved geometry, write the terminal fixup, and require the
final `0xFFFFFFFF` residue before reboot. Semantic program analysis belongs on
the host, not inside the 4 KiB RAM shellcode.

## 1. Semantic acceptance-gate discovery

Tracked resolver:

`ghidra/scripts/investigate/ResolveSecocAcceptanceGate.java`

The script contains **none** of the known Sienna target/function/MAC-result/CRC
addresses. It walks every recovered function and searches for this structural
shape:

```text
byte READ(global) -> cmp zero -> cmovne 1 -> auth_boolean
                                      |
                                      +---- later call(s), including state/freshness handling
                                      |
                              cmp zero, same auth_boolean
                                      |
                                  conditional branch
                                 /                  \
                       failure arm              success arm
                       call(s)                   call(s)
                                 \                  /
                                  common forward join
```

Additional fail-closed constraints:

1. the byte source has a Ghidra `PARAM` reference elsewhere in the image, i.e.
   the same global is passed by address as an output/result cell rather than
   merely being ordinary state;
2. the same materialized boolean survives to the final branch predicate;
3. at least one call occurs between boolean creation and the gate;
4. both branch arms contain calls and converge at a common forward join;
5. the gate is a two-byte RH850 `bne` whose condition nibble can be changed to
   unconditional `br` while preserving all opcode/displacement bits;
6. **exactly one** candidate must satisfy the complete predicate.

If zero or multiple candidates survive, the resolver emits `FAIL_CLOSED` and no
patch target is accepted.

On `8965B4512000`, a full-image scan returns exactly one candidate without being
told any of its addresses:

```text
result global   FEBE555C
load            0x8E69E
booleanize      0x8E6A4
pre-gate call   0x8E6C0
patch branch    0x8E6C8
original        9a 0d
replacement     95 0d
success target  0x8E6DA
join            0x8E6E2
failure calls   2
success calls   1
```

This independently rediscovers SECOC-043 from structure rather than from the
known patch offset.

Committed resolver fixture:

`data/generated/secoc_gate_resolution_4512000.json`

The result includes `program_sha256`. The manifest builder requires that hash to
match the supplied CodeFlash byte-for-byte, preventing a semantic result from
one calibration from being accidentally applied to another.

The same resolver was also run against a **fresh, unannotated CodeFlash-only
Ghidra import**. It still produced exactly one candidate and the same branch,
replacement, success target, and join. As expected, the bare import does not map
the GP-relative RAM result cell, so `mac_result_source.address` is explicitly
`null` rather than guessed. This proves that the Level-1 target does not depend
on the repository's Sienna annotations or function names. The committed bare-
import fixture is `data/generated/secoc_gate_resolution_4512000_minimal.json`.

## 2. Dynamic boot-CRC geometry

Tracked manifest builder:

`tools/build_secoc_patch_manifest.py`

It contains no Sienna CRC-region, fixup, or marker addresses. It scans the raw
CodeFlash for self-describing 16-byte CRC records of the form:

```text
region_start
region_length
pointer_to_embedded_region_start
pointer_to_embedded_region_length
```

A record is accepted only if both pointers resolve inside the image and their
stored values reproduce `region_start` and `region_length`. On the Sienna image
this raw scan finds exactly the two boot CRC descriptors independently known
from the bootloader analysis.

For the uniquely resolved descriptor covering the semantic patch, the tool
infers:

- CRC range from `start` + `length`;
- terminal adjustment word as the final four bytes of that range;
- nearby validity marker by an aligned trailer scan;
- FCU erase/program block containing the target and the fixup;
- stock prefix CRC, stored fixup, expected fixup, and full residue;
- the replacement fixup for the supplied offline image after applying the
  semantic branch patch.

The terminal-fixup construction is validated as:

```text
fixup = CRC32(prefix) XOR 0xFFFFFFFF
CRC32(prefix || LE32(fixup)) = 0xFFFFFFFF
```

If the target region does not validate on the supplied artifact, the tool does
**not** silently trust it. It requires at least one independently valid sibling
descriptor proving the terminal-fixup scheme and records the target region as
anomalous. This is what happens on the published `4512000` dump because of the
SECOC-044 one-bit artifact discrepancy. A reconstructed clean image validates
directly and yields the known Gate-2 replacement fixup `0x91698386` without any
resolver change.

The future live patcher must still recompute from **live ECU flash** rather than
copy an offline fixup from the manifest.

## 3. One-command workflow for an arbitrary P1M-E CodeFlash image

The normal cross-calibration entry point is:

```bash
tools/resolve_secoc_patch_image.sh \
  /path/to/CodeFlash.bin \
  build/secoc_patch_manifest.json
```

It does **not** use the canonical Sienna Ghidra project. Instead it creates a
fresh disposable project under `build/secoc-targets/<image-sha>/`, imports only
the supplied CodeFlash using the pinned RH850/P1M-E processor, runs ordinary
Ghidra analysis, then executes the semantic resolver. The input binary is never
modified.

The workflow:

1. hashes the input and creates a disposable per-image workspace;
2. performs a fresh unannotated RH850/P1M-E CodeFlash import;
3. runs the read-only semantic scan;
4. writes a semantic-resolution JSON containing the imported program SHA-256;
5. verifies that SHA-256 against the exact supplied binary;
6. verifies the resolved patch preimage bytes;
7. discovers the boot-CRC descriptor that covers the patch;
8. emits the complete host-side patch manifest.

Zero or multiple semantic candidates, a SHA mismatch, a wrong patch preimage,
or ambiguous/unsupported CRC geometry all fail closed.

For an already imported working project, `tools/resolve_secoc_patch.sh` remains a
faster developer path; the same SHA join prevents it from being paired with the
wrong binary.

## 4. What is generalized now

The following are no longer selected by Sienna calibration constants:

- MAC-result global;
- containing acceptance function;
- Gate-2 branch address;
- branch replacement bytes (synthesized from the local Bcond encoding);
- success target and branch join;
- CRC descriptor address;
- CRC range start/end;
- CRC adjustment-word address;
- validity-marker address;
- target/fixup FCU block base.

The P1M-E FCU block size and CRC32/Ethernet algorithm remain **backend
properties**, not vehicle properties. A future different RH850/flash-controller
family should be a different backend rather than another table of vehicle
offsets.

## 5. Current transfer boundary

This is deliberately a **Level-1 structural resolver**, not yet a proof that
one machine-code shape covers every Toyota SecOC implementation. It is verified
to uniquely rediscover the Sienna target; no F3/F4/Corolla/RAV4 CodeFlash image
has yet been run through it.

The next validation step is therefore not to add more Sienna heuristics. Acquire
one of the blurbdust-supported F3/F4 images and run the resolver unchanged.
Three outcomes are useful:

1. **one candidate:** inspect its callers/data flow and compare it with the
   blurbdust egg target;
2. **zero candidates:** compiler/stack variation exceeded Level 1; promote the
   resolver to higher-level p-code/CFG data-flow while keeping the same semantic
   invariants;
3. **multiple candidates:** add semantic provenance from the crypto verify
   output/caller graph, not a calibration-specific byte signature.

This also gives a direct way to determine whether the original blurbdust egg was
merely an under-reversed proxy for the same acceptance decision, a broader
shared predicate, or the wrong semantic target entirely.
