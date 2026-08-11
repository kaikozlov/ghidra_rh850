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
> **Verification:** `tests/verify_memory_safety.py`,
> `tests/verify_memory_safety_mutations.py`, and
> `ghidra/scripts/verify/AssertMemorySafetyPaths.java`
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
| MEM-SAFE-005 | No corruption found in the enumerated CAN/ISO-TP/SecOC receive boundary | Bounded negative | Calibration-specific enumerated graph | bounded |

## Claim-to-proof matrix

The curated [proof matrix](../../data/memory_safety_proof_matrix.csv) records,
for every claim, its entry functions, decisive arithmetic and branches, state
fields, source/destination pointers, controlling table rows, reachability
chain, exploitability assumptions, negative boundary, and verifier. The two
verification layers are deliberately independent:

- `tools/memory_safety_semantics.py` reads the committed firmware directly and
  pins only decisive instruction encodings and table values—not whole-body
  hashes or generated Ghidra artifacts.
- `AssertMemorySafetyPaths.java` independently checks live Ghidra instruction
  mnemonics/operands, basic-block flows, call/reference censuses, and table
  bytes in a rebuilt project.

The mutation suite zeros every load-bearing body and separately changes the
shift amount, endpoint subtraction, 16-byte increment, equality branch,
compare response, zero-fill length source, and both range-check branches. Each
mutant must fail its named proposition. An unrelated-byte mutant must still
pass. An independent arithmetic model covers lengths `0`, `1`, `15`, `16`,
`17`, and `0x400`.

`verified` below means the decisive static firmware propositions are now
deterministically asserted. It does not mean an exploit has been dynamically
demonstrated. MEM-SAFE-005 remains `bounded` because an enumerated negative is
not proof that an unknown indirect consumer cannot exist.

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
- the `0xFF00` request path inside `uds_routine_control @ 0x567E` accepts both
  `0x01` and `0x81` at `0x58A2–0x58B0`, calls `flash_erase_start @ 0x41E0`,
  then stores authorization state `0x81` and operation state `0x02` at
  `0x58C2–0x58C8`. `routine_erase_task @ 0x5B70` is the later asynchronous
  completion worker, not the request/authorization gate.

The downstream flash-engine callback invocation is direct and unvalidated:

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

### No direct exfiltration consumer in the bounded step graph

The exact direct-callee census for `payload_cmac_verify_step @ 0x7170` contains
only the CMAC primitive at `0x7E0C`. The OOB bytes therefore have no direct
response-buffer consumer in that bounded function graph. The malformed walk
never reaches final-tag comparison because the endpoint is never matched.
Expected external behavior is a hypothesis—hang, exception, or reset depends
on RH850 unmapped-read handling and has not been dynamically probed. This
negative does not exclude hardware timing or fault side channels.

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

The configured command-8 worker at `0x6823C` supplies a fixed 48-byte
result buffer and length. DID `0x1010` enforces an exact 64-byte request and a
49-byte status/result response. No diagnostic or CAN sender can control the
output pointer or expand the zero length.

The bounded caller census is exact in the rebuilt graph: command-8 prepare
`0x86E62` is called at `0x870DC` and `0x87142`; result copy `0x86EE8` is called
at `0x86FB4` and `0x871B2`; and driver dispatch `0x88936` has the single
configured call at `0x6828A`.

The defect would become exploitable if a future callback (or a corrupted
callback pointer via MEM-SAFE-001) supplied a caller-controlled output
pointer/length. It is documented to prevent regression and to flag the risk
for variant analysis.

## Bug-class taxonomy

The audit searched for five vulnerability patterns common in embedded
input-handling code:

1. **Short-frame stale-tail use** — receive N bytes into a larger buffer, leave
   residual bytes from a previous frame, then process the full buffer length.
2. **Length underflow** — compute `payload_len = received_len - trailer_len`
   without first proving `received_len >= trailer_len`.
3. **Parser differential** — transport layer accepts one length, service layer
   assumes another.
4. **Reject-path cursor corruption** — on error, roll back by the expected
   length rather than the bytes actually consumed.
5. **Unchecked sink** — caller validates capacity, callee blindly copies, and
   some alternate caller bypasses the validation.

Each path in the explicit proof-matrix boundary was checked against this
taxonomy. This is not an unqualified whole-image absence claim.

## Specific audited paths (safe primitives with caller-gated reachability)

### Application diagnostic Rx blind copy (`0x920D2`)

`FUN_000920D2` blindly copies application diagnostic Rx data from the request
buffer to a route-specific destination and subtracts the chunk length from
remaining. It performs no bounds check itself. However, its sole caller
`FUN_0009043C @ 0x9043C` checks `*(ushort *)(param_2 + 4) <= remaining` (via
`FUN_00092398`) before invoking the copy. No alternate caller bypasses this
validation — this is an unchecked-sink pattern that is currently closed by
caller gating.

### Bootloader request-prefix copy (`0x67B0`)

`FUN_000067B0` copies `param_2 & 0xffff` bytes from `DAT_febf30c0` (the 4 KiB
Dcm request buffer at `0xFEBF30C0`) to a caller-supplied destination. This is
used by WDBI, RequestDownload, and RoutineControl to copy fixed-size request
prefixes (19/13/14 bytes) before the handler validates the full request
length. The copy stays inside the 4 KiB buffer and may consume stale bytes
from a previous transaction, but all audited handlers enforce exact request
lengths before those prefix bytes affect any sensitive operation. No
stale-data response or memory escape was found through this path.

### TransferData ignored range-check return (`0x4B7C`)

`FUN_00004B7C` (the ordinary TransferData handler) calls
`boot_memory_range_check_access @ 0x32D2` but ignores its return value. It then
reads `acStack_d[0]` — the output class byte — which is only initialized if the
range check passed. On a failed range check, this byte would be uninitialized.

However, the address and remaining-length state were already validated by the
prior `RequestDownload @ 0x5D68`, which performs its own range check against
the same table. No external sequence was found that breaks this invariant: the
download address is set once by RequestDownload and cannot be changed by
TransferData alone. This is a real code-quality defect (missing error handling)
but not currently an externally reachable corruption primitive.

### SecOC trailer subtraction (`0x8E4BA`)

`secoc_rx_verify_worker @ 0x8E4BA` performs the length subtraction that
initially appeared vulnerable to a stale-tail or underflow attack: received
length minus the configured authentication trailer. However, the worker
explicitly rejects frames shorter than the trailer before any subtraction, and
`canif_validate_rx_length @ 0x7FF52` rejects frames below the configured PDU
minimum. Classic protected frames require DLC 8; FD protected frames require
at least 32 bytes; longer FD frames are clamped to 32 before SecOC. The
hypothesized short-frame/stale-tail pattern does not bypass these gates.

### Range checker wraparound rejection (`0x32D2`)

`boot_memory_range_check_access @ 0x32D2` explicitly validates
`start <= start + length - 1` before accepting a range, rejecting integer
wraparound. It also rejects zero length and ranges outside the three
configured windows. This is a well-designed bounds primitive.

## Memory-map geometry: why MainPE OOB reads cannot reach ICU-S

An ordinary MainPE out-of-bounds read cannot reveal ICU-S key-slot contents.
ICU-S key slots are not represented as CPU-addressable bytes — they live in
isolated hardware key storage accessible only through ICU-S command registers.

The CPU-visible ICU-S MMIO register window is at `0xFFC5D000`. MainPE RAM tops
out at `0xFEBFFFFF`. The gap between them is `0x10_6D_001` bytes (≈16.4 MiB).
A length underflow starting from any `0xFEBFxxxx` address can reach at most
`0xFEBFFFFF` — it cannot bridge to `0xFFC5D000`.

Even if the MMIO were reached, the ICU-S command/verify-result registers do
not contain raw key material. CPU-visible ICU-S products are limited to:
CMAC output (16 bytes), verification status (one 32-bit word), and command-8
M4/M5 proof (48 bytes).

SHE provides no command for exporting a nonvolatile key slot such as slot 4
(SECOC-025). Key extraction therefore requires a privileged memory read of a
CPU-visible key copy, not an OOB read into ICU-S address space.

## Strategic assessment: the signing-oracle path

**Key extraction is unnecessary for the comma goal.** The useful primitive is a
CMAC signing oracle: invoke ICU-S command 5 (MAC generation) with selector 4
(slot 4 = SecOC key) and attacker-chosen input, then return the 16-byte
generated MAC.

Four potential routes to this oracle:

1. **Overwrite the dormant command-5 test-bank activation/state** — the
   crypto-test bank at `FEBE508F` is the sole configured command-5 caller, but
   its activator `0x69018` has no recovered CodeFlash caller. A data-only
   corruption that sets `FEBE508F=1` could arm the bank through ordinary CAN
   traffic on `0x01B..0x01F`.
2. **Redirect an existing asynchronous callback** — point an existing ICU-S
   or diagnostic callback at the command-5 dispatcher `0x88350`.
3. **Corrupt a diagnostic output pointer/length** — so the 16-byte ICU result
   from a command-5 invocation is returned over CAN/diagnostics.
4. **Application-context code execution** — call command 5 directly via the
   authenticated bootloader RAM callback (SECOC-019) or a persistent
   application-context hook.

Route 4 is the most direct: the authenticated bootloader callback already
provides code execution on the `8965B4x` family, and MEM-SAFE-001 makes it
repeatable without re-authentication. The bootloader callback runs in the wrong
context (boot GP/TP/RAM/interrupts) for the initialized application ICU, so a
persistent application hook or an application-context execution path is the
remaining gap.

## Next attack priorities for newer targets

The Sienna image identifies vulnerable shapes but cannot prove bugs in code we
don't possess. The following priorities apply when a newer target's CodeFlash
becomes available:

1. **CanIf DLC gate → PduR/CanTp copy path** — check for short-frame
   stale-tail or DLC/length differential between layers.
2. **SecOC queue → trailer split → authenticated-input builder → COM delivery**
   — look for lengths validated against different constants between layers
   (the N-vs-M byte differential).
3. **Diagnostic response construction** — especially multi-DID/DTC/event
   responses exceeding the 256-byte application route buffer.
4. **Asynchronous WDBI/RoutineControl callbacks** — where request buffers are
   reused after the original transaction.
5. **Malformed ISO-TP final frames, aborts, retransmissions, and re-entry** —
   not just oversized First Frames.

The core insight: **the real prize is making one layer authenticate or validate
N bytes while the next layer consumes M bytes.** That differential is enough to
own the control path without ever reading the ICU-S key.

## MEM-SAFE-005: bounded negative findings

The following enumerated externally reachable paths were audited and found to
reject malformed input correctly. The grade is `bounded`: the assertion covers
the named sinks, callers, tables, and branches, not every possible unknown
indirect consumer in the image.

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
  The suffix is ignored, producing an **ignored-suffix alias**, not an overflow.

No stale-tail, short-frame, or pointer-rewind vulnerability was identified in
the CAN receive path.

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

### TransferExit

`TransferExit @ 0x5C92` requires exact request length 1 and remaining count
zero. No length mismatch or state-reuse vulnerability was found.

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

## Appendix: instruction-level evidence

This appendix records the granular address-level evidence from the audit so a
future rebuild can cross-validate without re-deriving it.

### MEM-SAFE-001: bootloader download/decrypt/execute chain

| Stage | Function | Addresses | Evidence |
|---|---|---|---|
| TransferData length gate | `FUN_00004B7C` | `0x4BF0–0x4C24` | Accepts final chunk 1–0x400, no 16-byte alignment check |
| Decrypt enqueue | `FUN_00004B7C` → `payload_decrypt_enqueue` | `0x4C6E–0x4C72` | `payload_decrypt_enqueue(uVar6, iVar5, iVar5)` — source=dest=request_ptr+2 |
| Block count computation | `payload_decrypt_transfer_task` | `0x6BEA–0x6BFE` | `min(len,16) >> 4` = floor(len/16); zero iterations for len 1–15 |
| Completion marking | `payload_decrypt_transfer_task` | `0x6C3C–0x6C4A` | Subtracts full len from remaining, marks done |
| Raw byte copy to dest | periodic task → `FUN_0000153a` | `0x4F7E–0x4F84` (memcpy call), `0x4F88–0x4F92` (target advance) | Copies unmodified request bytes to download destination |
| `0x10F0` auth bit set | `routine_verify_crc_cmac_task` | `0x59E0/0x59E4` | Sets authorization bit 0 for class-1 region |
| Subsequent RequestDownload | `uds_request_download` | `0x5E70–0x5E78` | Rejects state `0x81` only; accepts authorized `0x01` |
| `0xFF00` accept | `uds_routine_control` | `0x58A2–0x58B0` | Accepts authorization `0x01` or `0x81` |
| `0xFF00` erase start/state | `uds_routine_control` → `flash_erase_start` | `0x58B4–0x58CC` | Starts the flash erase, then stores authorization `0x81`, operation state `0x02`, and launch flag `1`; `routine_erase_task @ 0x5B70` is the later asynchronous worker |
| Callback load | flash engine | `0x434C/0x4350` | `movhi 0xFEBF / ld.w 0x0FD0` → loads `*(uint32_t*)0xFEBF0FD0` |
| Callback call | flash engine | `0x435E` | `jarl r29, lp` — indirect call |
| Second callback path | flash engine | `0x4402/0x440E` | Second load/call of same pointer |

### MEM-SAFE-002: CMAC verify OOB read

| Stage | Function | Addresses | Evidence |
|---|---|---|---|
| Endpoint computation | `payload_cmac_verify_setup` | `0x7160–0x7166` | `end = start + length - 16` stored to state |
| Final-block check | `payload_cmac_verify_step` | `0x7174–0x7192` | Block is final only when `current == end` |
| CMAC engine read | `payload_cmac_verify_step` | `0x719C–0x71B0` | Reads 16 bytes per block through AES engine |
| Continue return | `payload_cmac_verify_step` | `0x71E0` | Returns 2 (continue) for non-final blocks |
| Step driver | `FUN_00006EE0` | — | Repeatedly calls step while it returns 2 |

### MEM-SAFE-003: CodeFlash equality oracle

| Stage | Function | Addresses | Evidence |
|---|---|---|---|
| State 8 set | `0x10F3` handler | `0x5924` | Sets transfer state 8 (compare mode) |
| Operation bit 5 | `uds_request_download` | `0x5EC0–0x5ECC` | Armed compare-mode selects bit 5 |
| Compare queue | `transfer_data_compare_request` | `0x4EC2–0x4ECC` | Queues (tester_source, CodeFlash_target, length) |
| Byte comparison | `memory_compare_task` | `0x6CAE–0x6CBE` | Byte-by-byte equality check |
| Positive response | TransferData handler | `0x4B5A` | Equality → `76 blockSequenceCounter` |
| Mismatch detection | TransferData handler | `0x4EF8` | Mismatch detected |
| NRC 0x10 | TransferData handler | `0x4F0A` | Mismatch → NRC 0x10, state 15 |

### CAN receive dispatch chain

| Stage | Function | Address | Evidence |
|---|---|---|---|
| DLC decode | lower CAN RX | `0x82C50` | 4-bit hardware DLC indexes table at `0x22F10` |
| Frame enqueue | `0x7FA56` | `0x7FA56` | Routes to copy routine |
| Payload copy | `0x7F95E` | `0x7F95E` | Copies in 32-bit increments; logical length preserved |
| Route demux | `application_can_normal_rx_demux` | `0x80006` | Calls validator `0x7FF52` before delivery |
| Route delivery | demux | `0x7FF86` | Only invoked after validator success |
| Length validation | `canif_validate_rx_length` | `0x7FF52` | Checks `actual <= physical_max` and `actual >= configured_min` |
| COM RX copy | `application_com_rx_indication` | `0x7C640` | Copies `min(actual_length, configured_COM_length)` |

### SecOC receive chain

| Stage | Function | Address | Evidence |
|---|---|---|---|
| SecOC entry | `secoc_rx_indication` | `0x8DC64` | Entry point from COM |
| Profile lookup | — | `0x8E024` | Selects SecOC profile by route index |
| Queue/copy | — | `0x8E0BE` | Enqueues frame for verification |
| Lower-bound check | `secoc_rx_verify_worker` | `0x8E510–0x8E51A` | `total_length >= trailer_length` before any subtraction |
| Trailer split | `secoc_rx_split_freshness_and_tag` | `0x8E1A8` | Independent `total >= trailer` check, then `trailer_start = base + total - trailer` |
| Ordinary freshness unpack | — | `0x8EBC2` | 4-bit mode reads 1 byte; 46-bit mode reads 6 bytes |
| Sync freshness unpack | — | `0x8EC82` | Unpacks sync frame freshness field |
| Freshness reconstruction | — | `0x8E8E6` | Reconstructs full freshness from truncated value |
| Freshness commit | — | `0x8E942` | Commits accepted freshness after verify |
| Post-verification | — | `0x8E67A` | Commit/delivery only on successful verification |
| MAC input builder | `secoc_build_authenticated_input` | `0x8DB22` | Checks `2 + payload + freshness <= capacity` before copy |
| Tag workspace | split helper | — | 20-byte local; configured tag/freshness widths ≤ 16 and 6 bytes |

### SecOC profile configuration

SecOC receive records at `0x25970`, stride `0x50`, six profiles:

| Profile | Secured length | Trailer length | Payload type |
|---|---|---|---|
| 0–3 (classic) | 8 | 8/4/4/4 | 4-byte ordinary + FV4/CMAC28 |
| 4–5 (FD) | 32 | 4/4 | 28-byte ordinary + FV4/CMAC28 |

Sync profile: 8-byte envelope = FV36 + CMAC28, no authentic payload.

Configured authenticated lengths: sync 7, ordinary classic 12, ordinary FD 36.
FD workspace capacity is 36 bytes — largest input fits exactly.

SecOC key configuration at `0x25950` selects slot 4.

### ICU-S command wrapper bounds

| Command | Prepare | Engine | Result | Input/output bounds |
|---|---|---|---|---|
| AES 1/3 (enc/dec) | `0x8768E` | `0x8954C` | `0x87712` | Exactly 16-byte input; result copy bounded to 16 |
| CMAC gen 5 | `0x87A94` | `0x89630` | `0x87B46` | Input ≤ 0x50 bytes; staging 80 bytes; result `min(capacity,16)` |
| CMAC verify 7 | `0x87ED0` | `0x897F4` | `0x897A8` (FIFO) | Message ≤ 0x50; tag ≤ 128 bits; one 32-bit result word |
| Key update 8 | `0x86E62` | `0x8997A` | `0x86EE8` | Exactly 64-byte M1/M2/M3; success copies 32+16 |

Command-5 word at `0x89734–0x8973A`: `(selector << 16) | 5`.
Command-7 SecOC result pointer is fixed RAM target `FEBE555C`, not wire-controlled.
Pointer and callback fields checked against stored bitwise complements before use.

### MEM-SAFE-004: command-8 failure path

| Stage | Address | Evidence |
|---|---|---|
| Prepare (any cap ≥ 48) | `0x86E62` | Accepts without clamping stored capacity |
| Success: copy 32 | `0x86F32` | Copies 32 bytes of M4 |
| Success: copy 16 | `0x86F42` | Copies 16 bytes of M5 |
| Success: set length | `0x86F46–0x86F4A` | Sets returned length to 48 |
| Failure: load original len | `0x86F50` | Loads unbounded caller capacity |
| Failure: zero-fill | `0x86F54` | Calls `0x89044` with unbounded length |

Configured command-8 worker `0x6828A` supplies fixed 48-byte buffer/length.

### ICU-S transfer mechanism

| Component | Address | Evidence |
|---|---|---|
| One-block input FIFO callback | `0x89448` | CPU source pointer, block index/count |
| One-block output FIFO callback | `0x894BE` | CPU destination pointer, block index/count |
| Completion/command-ID check | `0x89DE6` | Rejects submitted/tracked command mismatch |
| Common driver dispatcher | `0x89E20` | Interrupt-driven progress; one 16-byte block per callback |

Software state: CPU source/destination pointer, 128-bit block index/count,
callback pointer plus complement. No audited command programs a DMAC source,
destination, or wire-controlled descriptor size. No separate DMA descriptor
attack surface in this call graph.

### SecOC oracle/availability surface

- All ordinary profiles expose 28-bit truncated CMAC.
- Failed command-7 verification: does not commit freshness, does not deliver
  PDU, does not trigger per-source failure lockout.
- Synchronous CryptoIf path polls up to `0xE07` iterations.
- Raw command-7 result word is not returned on CAN.

### Command-5 dormant test bank

| Component | Address | Evidence |
|---|---|---|
| Input collector | `0x6875E` | Collects stable COM inputs (3 identical updates required) |
| Command-5 submit | `0x68B42` | Selects command 5 when mode byte is 1 |
| Bank activator | `0x69018` | Sets `FEBE508F=1`; no CodeFlash function-pointer reference |
| Result compare | `0x6926A` → `0x69068` | Compares 16 generated bytes locally; does not transmit |
| Command-5 dispatcher | `0x88350` | No CodeFlash function-pointer reference |

CAN inputs: `0x01B` (signals 95/96: selector/mode), `0x01C/0x01D` (97/98: 16-byte
message), `0x01E/0x01F` (99/100: 16-byte expected result). Update counters 20–24.

### ICUSCMD store census (nine sites)

```text
0x8919C, 0x89628, 0x8973A, 0x8990C, 0x89A2C,
0x89A8A, 0x89BB0, 0x89BF8, 0x89DDC
```

Account for: dynamic command 1/3, commands 5, 7, 8, 11, 0x22, abort 0x3F,
diagnostic 0x7000/0x7100. No command-13 writer was identified in the application.
