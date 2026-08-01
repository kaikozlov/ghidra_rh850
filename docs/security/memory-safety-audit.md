# Memory-safety audit: externally reachable input handlers

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS MEM-SAFE-001 … MEM-SAFE-004
>
> **Canonical artifacts:** committed CodeFlash bytes, decompiled functions
>
> **Verification:** `tests/verify_memory_safety.py`
>
> **Related:** [bootloader payload gate](bootloader-payload-gate.md), [SecOC application chain](secoc/application-chain.md)

This report documents a systematic memory-safety audit of all firmware routines
that wait for or consume external input: ISO-TP reassembly, diagnostic transport,
UDS service handlers, CAN receive dispatch, variable-length copies, parsing loops,
queues/ring buffers, flash/download paths, seed/key inputs, and response
construction.

The goal is finding an externally reachable memory-safety defect that could
serve as a software wedge for getting comma working on newer SecOC/TSK EPS
devices. Each finding documents input reachability, transport/reassembly path,
session/security gating, the exact unsafe operation, the resulting security
primitive, and applicability to the target ECU generation.

## Summary

| ID | Finding | Primitive | Reachability | Grade |
|---|---|---|---|---|
| MEM-SAFE-001 | Partial AES-block TransferData chunks become raw RAM writes | Arbitrary RAM write within authenticated window | Post-auth (needs one prior CMAC success) | verified |
| MEM-SAFE-002 | Malformed RoutineControl lengths cause OOB CMAC reads | OOB read (no exfiltration consumer found) | Post-auth (needs prior CRC success) | verified |
| MEM-SAFE-003 | RID 0x10F3 provides byte-granular CodeFlash equality oracle | Constrained CodeFlash read-back | Post-auth (SA + DID sequence) | verified |
| MEM-SAFE-004 | ICU-S command-8 failure path zero-fills unbounded caller length | memset primitive | Not remotely controllable in this image | verified (latent) |

## MEM-SAFE-001: partial AES-block chunks produce raw RAM writes

**Severity: high — upgrades any prior authenticated payload into arbitrary
RAM-code execution without repeating CMAC.**

### Mechanism

`payload_decrypt_transfer_task @ 0x6BDE` processes AES-CBC blocks in a loop
whose iteration count is `floor(byte_count / 16)`:

```c
// 0x6BDE — simplified
uVar7 = DAT_febf2bdc;           // stored byte count
if (0xf < uVar7) uVar7 = 0x10;  // cap single-invocation work to 16
for (iVar6 = (int)uVar7 >> 4; iVar6 != 0; iVar6--) {
    aes_cbc_decrypt_block(...);  // decrypt one 16-byte block
    // copy 16 decrypted bytes to destination
}
uVar7 = remaining - uVar7;      // subtract full requested length
*(ushort *)(gp - 0x6c24) = uVar7;  // store new remaining
if (uVar7 == 0) done = true;     // mark complete
```

For chunk lengths 1..15, the loop executes **zero** iterations — no AES-CBC
decryption occurs — yet the full chunk length is subtracted from the remaining
counter and the task marks itself complete.

The raw, unmodified request bytes are then copied to the download destination by
the transfer completion path (`FUN_0000153a` memcpy at `0x153A`, invoked from the
periodic task around `0x4F7E`).

### Length gate

`FUN_00004B7C` (the TransferData handler for ordinary downloads) accepts final
chunks from 1 through `0x400` bytes without requiring a 16-byte multiple. The
only length constraints are:

- non-final chunks must be exactly `0x400`;
- final chunk must satisfy `remaining <= 0x400` and `remaining == chunk_len`;
- total must not exceed the RequestDownload-declared size.

Therefore a tester who has already completed one successful `0x10F0` authentication
can issue repeated small (1–15 byte) TransferData blocks to write arbitrary bytes
into the validated RAM window `0xFEBF0000..0xFEBF0FFF`, bypassing AES-CBC
transformation entirely.

### This is NOT an OOB write

`boot_memory_range_check_access @ 0x32D2` rejects:

- zero length;
- address wrap (`start > start + length - 1`);
- ranges outside the three configured windows.

TransferData also checks `chunk_len <= remaining`. The write stays within
bounds. The vulnerability is **missing AES-block alignment**, not destination
bounds.

### Security consequence: stale authorization enables payload substitution

The authorization byte at `0xFEBF2B11` (gp-relative `gp - 0x6CEF`) persists
across subsequent downloads:

- successful `0x10F0` sets authorization bit 0 via `routine_verify_crc_cmac_task @ 0x5936`;
- a subsequent RAM `RequestDownload` only rejects state `0x81` (not authorized
  state `0x01`) at `0x5E70–0x5E78`;
- SIDs `0x34/0x36/0x37` never clear this byte;
- `0xFF00` (`routine_erase_task @ 0x5B70`) accepts both `0x01` and `0x81`,
  then loads and calls the callback pointer at `*(uint32_t *)0xFEBF0FD0`.

The callback invocation is direct and unvalidated:

```text
0x434C  movhi  0xFEBF, r0, r29
0x4350  ld.w   0x0FD0[r29], r29    ; r29 = *(uint32_t *)0xFEBF0FD0
0x435E  jarl   r29, lp             ; indirect call
```

A second load/call site exists at `0x4402/0x440E`.

### Exploit chain

```text
1. SecurityAccess (SEED_KEY_SECRET)           → SA unlock
2. WriteDID 0x203 → 0x201 → 0x202             → crypto-ready
3. RequestDownload 0xFEBF0000, 0x1000         → download window
4. TransferData × 4 (encrypted, 0x400 each)   → authenticated image
5. RoutineControl 0x10F0                       → CRC + CMAC pass
   → authorization byte set to 0x01
6. RequestDownload 0xFEBF0000, N (N ≤ 15)     → re-open download (state 0x01 accepted)
7. TransferData × ceil(N/15)                   → raw bytes written (no decrypt)
   → overwrite callback pointer at 0xFEBF0FD0
8. RoutineControl 0xFF00                       → callback executed
```

Step 6–7 replaces the authenticated image — including the callback pointer at
offset `0xFD0` — with attacker-chosen shellcode, without passing another CMAC
check. The `0xFF00` erase path then calls the new callback.

**This does not provide an initial authentication bypass.** It upgrades
replay/possession of any accepted fixed payload into a second arbitrary RAM-code
execution without the original crypto material.

### What blocks initial reachability

- Programming session (`10 0x82`) is required.
- SecurityAccess state 2 (`0xFEBF2B0F == 2`) is required.
- DID `0203 → 0x201 → 0x202` sequence must be completed to enable crypto.
- One prior successful `0x10F0` CRC + CMAC authentication is required.

### Applicability to the comma goal

If the target ECU uses the same `8965B4x` bootloader family (RAV4 Prime B4209/
B4233, Sienna B4512000, B4509100), the same authenticated RAM-exec bootstrap
(SECOC-024) applies. MEM-SAFE-001 then provides a repeatable code-execution
primitive that does not require re-deriving the CMAC for each session. For
newer TSK/SecOC devices, the bootloader gate structure must be verified against
the target's CodeFlash.

## MEM-SAFE-002: malformed RoutineControl lengths cause OOB CMAC reads

**Severity: denial of service / potential watchdog reset; no exfiltration
consumer found.**

### Mechanism

`0x10F0`/`0x10F1` accept any nonzero RAM range from the caller. They do not
require the authenticated range length to be a multiple of 16 or exactly
`0x1000`.

`payload_cmac_verify_setup @ 0x7122` computes the message endpoint:

```c
*(int *)(gp - 0x6750) = start;
*(int *)(gp - 0x6758) = start + length - 16;  // endpoint
```

`payload_cmac_verify_step @ 0x7170` advances the source pointer by exactly
16 bytes per invocation and considers the block final only when `current ==
endpoint`. The step function returns 2 (continue) on every non-final block.

For `length % 16 != 0`, the endpoint has a different low nibble from the
16-byte walk and is **never reached**. The walker passes the fixed tag at
`0xFEBF0FF0`, skips that one block, and continues reading beyond the requested
range — eventually beyond mapped LocalRAM.

For `length < 16`, the endpoint underflows below `start`, causing immediate
OOB reads.

### No exfiltration consumer

The OOB bytes feed only internal CMAC state through the AES engine. The
malformed walk never reaches final-tag comparison (because the endpoint is
never matched), so no comparison result is returned to the caller. Expected
external result: no completed UDS response, followed by a hang, exception,
watchdog reset, or hard reset depending on RH850 unmapped-read handling.

### Reachability constraint

The fixed CRC-descriptor stage must first pass. This is achievable without
CMAC knowledge because the partial-block primitive (MEM-SAFE-001) permits raw
construction of a CRC-correct RAM image.

### Applicability

A DoS/reset primitive may be useful for forcing a bootloader reboot into a
known state, but it does not directly advance the comma goal. It is documented
for completeness and to prevent regression.

## MEM-SAFE-003: RID 0x10F3 byte-granular CodeFlash equality oracle

**Severity: constrained application-CodeFlash exfiltration.**

### Mechanism

`0x10F3` arms a compare-mode RequestDownload (operation bit 5, state 8).
TransferData in compare mode queues `(tester_source, CodeFlash_target, length)`
for `memory_compare_task @ 0x6C8E`.

The compare task checks byte-by-byte:

```c
// 0x6C8E — simplified
uVar4 = min(remaining, 16);
for (uVar5 = 0; uVar5 < uVar4; uVar5++) {
    if (src[uVar5] != dst[uVar5]) { mismatch; return; }
}
// equality → positive response (76 blockSeqCounter)
// mismatch → NRC 0x10, transfer state 15
```

Equality produces `76 blockSequenceCounter` through `0x4B5A`. Mismatch is
detected at `0x4EF8` and produces NRC `0x10` at `0x4F0A`, then forces transfer
state 15.

Because a sub-16-byte TransferData block is not decrypted (MEM-SAFE-001), a
tester can submit single raw bytes and distinguish equality from mismatch.
Worst case: 256 re-armed attempts per byte.

### Accessible range

The compare-mode RequestDownload at `0x5D68` uses operation bit 5, validated
against the access table at `0x8DA0`. The accessible ranges are:

```text
0x10000..0x17DFF   (opmask 0x33, class 0)
0x18000..0xFFDFF   (opmask 0x33, class 0)
```

Both rows include bit 5 in their opmask.

Bootloader secrets at `0xBFD8`/`0xBFE8` are **below** `0x10000` and therefore
NOT reachable by the oracle. The oracle reads only application CodeFlash.

### Constraints

- Physical CAN/UDS path (`0x7A1`).
- Programming session and SecurityAccess state 2.
- DID crypto-ready sequence completed.
- Each failed guess requires reissuing `0x10F3` and RequestDownload.

### Applicability

An equality oracle on application CodeFlash could extract calibration data,
configuration tables, or function addresses from a target ECU without dumping
the full image. For the comma goal, this could identify whether a newer target
uses the same crypto routines, SecOC profiles, or callback structures.

## MEM-SAFE-004: latent ICU-S command-8 zero-fill on unbounded length

**Severity: latent — not remotely controllable in this firmware graph.**

### Mechanism

`0x86E62` (command-8 prepare) accepts any output capacity `>= 48` but does not
clamp the stored capacity.

In the result handler at `0x86EE8`:

- Success path: copies exactly 32 + 16 = 48 bytes and sets returned length to 48.
- Failure path: loads the caller's original output length (unbounded) and calls
  `0x89044` (zero-fill helper) with that length.

This creates a generic primitive:

```text
memset(caller_output_pointer, 0, caller_output_length)
```

provided the caller controls those CPU-side arguments and can induce command
failure.

### Why it is not exploitable here

The configured command-8 worker around `0x6828A` supplies a fixed 48-byte
result buffer and length. DID `0x1010` enforces an exact 64-byte request and a
49-byte status/result response. No diagnostic or CAN sender can control the
output pointer or expand the zero length.

The defect would become exploitable if a future callback (or a corrupted
callback pointer via MEM-SAFE-001) supplied a caller-controlled output
pointer/length. It is documented to prevent regression and to flag the risk
for variant analysis.

## Negative findings: paths that reject safely

The following externally reachable paths were audited and found to reject
malformed input correctly:

### ISO-TP reassembly

- First Frame length is classic 12-bit (`≤0xFFF`).
- Functional First Frames are rejected at `0x27D8`.
- Consecutive Frame sequence and DLC are checked at `0x2946`.
- Dcm caps reception at `0x1000` bytes (`0x6374`).
- Receive cursor resets on new message (`0x636E`).
- Copy capacity is checked at `0x6464` and clamped at `0x6422`.

No CAN-reachable ISO-TP OOB read/write was found.

### CAN receive dispatch

- DLC decode at `0x82C50` uses a 16-byte lookup table at CodeFlash `0x22F10`
  that produces only valid lengths: `0..8, 12, 16, 20, 24, 32, 48, 64`.
- Local receive payload is a 64-byte stack buffer; no wire-controlled length
  above 64 is derivable.
- `canif_validate_rx_length @ 0x7FF52` rejects frames below the configured PDU
  minimum.
- Classic secured routes require **exactly** DLC 8.
- FD secured routes accept DLC 32, 48, 64 but clamp to 32 bytes before SecOC.

No stale-tail, short-frame, or pointer-rewind vulnerability exists in the CAN
receive path.

### SecOC receive chain

- `secoc_rx_verify_worker @ 0x8E4BA` performs the lower-bound check (total
  length >= trailer length) before any subtraction.
- `secoc_rx_split_freshness_and_tag @ 0x8E1A8` independently checks
  `total_length >= trailer_length` before computing `trailer_start`.
- `secoc_build_authenticated_input @ 0x8DB22` checks
  `2 + payload_length + freshness_length <= destination_capacity` before either
  copy.
- Configured authenticated lengths (7, 12, 36 bytes) fit exactly within the
  workspace capacities (36 bytes max).

The hypothesized short-frame/stale-tail/rewind pattern does **not** occur in the
recovered SecOC path.

### Bootloader WDBI

Four-entry descriptor loop, exact `descriptor.length + 3`, fixed 16-byte
destinations for `0x201/0x202`, and sequence enforcement. Malformed requests
return NRC `0x13/0x31/0x22`. No OOB destination was found.

### RequestDownload

Address/length wrap is rejected by `boot_memory_range_check_access @ 0x32D2`.
Only configured CodeFlash and 4 KiB RAM windows are accepted.

### Bootloader memory copies

WDBI, RequestDownload, and RoutineControl copy fixed 19/13/14-byte prefixes
before validating the supplied request length. Those reads remain inside the
4 KiB Dcm buffer and may consume stale bytes, but all effects are gated by
later exact-length checks. No stale-data response or memory escape was found.

### ICU-S result copies

All configured ICU-S wrappers copy bounded results:
- Command 1/3: exactly 16 bytes.
- Command 5: `min(caller_capacity, 16)` bytes.
- Command 7: one 32-bit verification result word.
- Command 8: exactly 48 bytes on success (defect on failure, see MEM-SAFE-004).

Raw slot-4 key bytes do not become CPU-visible. CPU-visible values include CMAC
output, verification status, and command-8 M4/M5 proof.

## Audit method

Three parallel subagents audited independent attack surfaces using Ghidra
decompilation, disassembly, x-ref, and raw CodeFlash bytes against
`build/project` only:

1. Application diagnostic receive path (ISO-TP → DCM → SID 0x22/0x2E/0x31/0xAB).
2. Bootloader download/update path (SID 0x34/0x36/0x37, WDBI, RoutineControl
   0x10F0/0xFF00, payload decrypt/verify/execute).
3. CAN COM/SecOC receive and ICU-S wrapper code.

All primary-evidence findings were independently verified by the parent session
against decompiled functions before documentation. The findings are scoped
strictly to Sienna `8965B4512000`; no Corolla/Camry projection.
