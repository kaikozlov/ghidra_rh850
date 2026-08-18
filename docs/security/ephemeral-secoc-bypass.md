# Ephemeral SecOC bypass feasibility

This report is the canonical static assessment of a **RAM-only, fail-stock**
alternative to the persistent receive-SecOC patch on Sienna calibration
`8965B4512000`.

The desired lifecycle is:

```text
stock boot
  -> legitimate programming/SecurityAccess
  -> authenticated bootloader RAM execution
  -> temporary RAM state / code
  -> stock application startup
  -> temporary SecOC or internal-command shim
  -> reset/power cycle restores stock behavior
```

The important result is now stronger than "RAM execution exists." Bootloader
RAM execution, a reset-cleared application-RWX retention pocket, and a complete
**callback-free foreground scheduler shell** are recovered. The payload does not
need stock application code to rediscover a RAM function pointer after startup:
it performs the stock transition/initialization sequence itself, then remains
the top-level foreground scheduler and inserts one bounded bridge between stock
SecOC processing and stock COM/control processing. The remaining boundary is
**dynamic bench validation**, not a missing static control-transfer primitive.

Evidence labels below follow `AGENTS.md`: **verified**, **recovered**,
**bounded**, **hypothesis**, and **disproved**.

## 1. Executive result

### What is established

1. **Verified:** normal reset startup clears `FEBE7000..FEBE7FFC`, then the
   effective clear loop at `0x143C` clears `FEBE8000..FEBFFFFC`. Therefore the
   authenticated payload window at `FEBF0000..FEBF0FFF` is reset-cleared.
2. **Verified:** `boot_application_handoff @ 0x13B0` does not itself perform
   those broad clears. The normal wrapper clears RAM first and then calls
   `0x13B0`. A boot-context payload that directly invokes `0x13B0` can therefore
   skip that reset-clear stage.
3. **Verified / generated-artifact bounded:** the application corpus has no
   recovered direct reference into `FEBF0000..FEBF0307`; its first recovered
   direct reference inside the authenticated-download page is `FEBF0308`.
   This leaves a 0x308-byte / 776-byte candidate retention pocket.
4. **Verified:** application MPU region 5 is
   `FEBEF400..FEBF33FC`, with MPAT `0xB8` in both recovered contexts. The
   candidate `FEBF0000..FEBF0307` pocket is therefore supervisor R/W/X after
   application MPU initialization.
5. **Verified:** the SecOC Gate-2 result is not controlled by a persistent RAM
   policy byte. `FEBE555C` has exactly one recovered producer-side parameter
   reference (`secoc_submit_cmac_verify @ 0x8E3EA`, site `0x8E41A`) and one
   consumer read (`FUN_0008E67A`, site `0x8E69E`). The ICU-S operation writes
   the result before Gate 2 consumes it, so pre-zeroing `FEBE555C` is not a
   bypass.
6. **Verified:** the two attractive RAM callback families do not survive
   application initialization. `FEBF1194` is zeroed during ICU-S startup, and
   `FEBE5600` is cleared by the startup chain
   `65626 -> 8A030 -> 96B82 -> 96B66 -> 8F1D0 -> 8F6A0 -> 8F688`.
7. **Verified from existing MEM-SAFE-001:** after one successfully authenticated
   `0x10F0` payload, the bootloader's retained authorization plus sub-block
   TransferData bug permits arbitrary raw-byte replacement anywhere in the
   validated `FEBF0000..FEBF0FFF` page. Consequently a legitimate accepted
   Toyota payload is sufficient to bootstrap **arbitrary boot-context RAM
   execution without knowing `PAYLOAD_BUILD_SECRET`**.
8. **Verified / generated-artifact:** the callback-free runtime is constructible
   inside the retained pocket. The pinned RH850 build is 704 bytes (`0x2C0`),
   entry offset 0, with zero relocations and 72 bytes of headroom inside
   `FEBF0000..FEBF0307`. It reproduces stock startup from the firmware's own 21
   consecutive `jarl disp22` instructions and preserves the stock TAUJ0 CH3
   foreground poll/clear sequence.
9. **Verified:** the stock scheduler exposes an exact splice for steering
   delivery. `FUN_65750` orders `0x68C0C -> 0x791C4 -> 0x96BAC -> 0x68DE6 ->
   0x57AC2 -> 0x6547C`; `0x791C4` reaches SecOC verify/Gate-2 processing, while
   `0x57AC2` runs the later COM/system-mode/control path. SecOC records 1/2 copy
   received `0x2E4`/`0x131` secured frames into `FEBE5490`/`FEBE5498` before
   verification. A resident scheduler can snapshot a marked frame, allow stock
   verification/rejection/cleanup to run, then call stock
   `application_com_rx_indication @ 0x7C640` before `0x57AC2`.
10. **Verified for this Sienna gate:** a matching CUW is **not** required for the
   initial authenticated RAM image. The repository already contains two pinned
   public 4 KiB encrypted payload fixtures whose CRC, CMAC, callback slot, and
   AES-CBC round trip are verified against this exact `8965B4512000` bootloader
   using tester-controlled `DID 0x0201 = 00*16` and `0x0202 = 00*16`. The
   matching CUW remains absent, so the OEM RAM driver's private command interface
   is still artifact-bounded; that interface is simply unnecessary for the
   MEM-SAFE-001 bootstrap on this image.

### Practical conclusion

The best currently supported architecture is:

```text
pinned public encrypted 4 KiB payload fixture
  + recovered boot SecurityAccess secret
  + tester DID 0x0201/0x0202 = zero
  -> bootloader SecurityAccess
  -> upload fixture and pass one authenticated 0x10F0
  -> MEM-SAFE-001 raw substitution
  -> arbitrary boot-context code in FEBF0000..0FFF
  -> stock boot transition prefix + boot validity check
  -> application_cpu_context_init @ 0x70524
  -> replay the stock startup JARL sequence @ 0x62760..0x627B0
  -> enable interrupts
  -> retained 704-byte foreground scheduler shell in FEBF0000..02BF
       -> preserve stock foreground task order
       -> snapshot newly queued zero-MAC 0x2E4 / 0x131
       -> run stock communication + SecOC verification/cleanup
       -> if stock did not already deliver it:
            application_com_rx_indication(PDU, saved secured frame)
       -> run stock COM unpack/system-mode/control path
       -> continue remaining stock foreground tasks
  -> hardware/watchdog/power reset clears RAM and returns to stock
```

The former `???` is resolved without finding a persistent callback: **the RAM
payload never relinquishes top-level foreground control**. It calls the stock
application functions in the same order and inserts the bridge at the boundary
already present inside `FUN_65750`.

This makes the RAM-only bypass **statically end-to-end constructible**. It is
still not a live result: direct transition, timing, one-shot record capture,
COM delivery, and steering behavior remain isolated-bench proofs.

## 2. Correction: the persistent Gate-2 patch address

Prior handoff prose that describes `0x8E6C8: 0x9A -> 0x95` as the working bypass
is stale and must not be used.

The source-of-truth bytes are:

```text
0x8E6C6  E0 D1    cmp r0,r26
0x8E6C8  9A 0D    bne 0x8E6DA
```

The corrected persistent neutralization is:

```text
0x8E6C6  E0 D1 -> E0 01    cmp r0,r0
0x8E6C8  9A 0D             unchanged
```

This makes the mismatch branch untakeable and preserves the success
fallthrough. See `secoc/application-chain.md` and CORR-064 for the earlier
predicate-direction correction.

This report uses the corrected `0x8E6C6` predicate as the semantic target.

## 3. RAM initialization and lifetime map

### 3.1 Reset-time broad clears

Reset startup contains the following explicit zero loops:

| Range | Evidence | Result |
|---|---|---|
| `FEBE7000..FEBE7FFC` | reset path `0x660..0x67A` | cleared before wrapper |
| `FEBE8000..FEBFFFFC` | wrapper `0x143C..0x1450` | cleared before handoff |
| `FEEF8000..FEF07FFC` | wrapper `0x1452..0x1466` | cleared before handoff |

The clear-shaped loop beginning at `0x1426` is **zero-trip** in this image. It
sets start `FEBF7C00` and endpoint `FEBE7000`, then uses the same unsigned
lower-than loop form seen in the real copy/clear loops. Since the start is
already above the endpoint, it does not clear the XCP shadow window. Existing
text that called this a startup clear is corrected by CORR-067.

### 3.2 Lower LocalRAM is retained by reset but not a free code cave

The broad reset loops do not cover `FEBE0000..FEBE6FFF`, but that does not make
it a safe `.noinit` region:

- application stack is based at `FEBE2000`;
- the generated corpus contains thousands of direct references throughout the
  lower LocalRAM range;
- `application_ram_default_init @ 0x57BFE` and the application subsystem
  initializers actively seed lower-RAM state.

No generic safe trampoline region is claimed there.

### 3.3 Direct handoff can preserve upper LocalRAM

`boot_application_handoff @ 0x13B0` performs peripheral/application handoff
work, reads the application entry pointer at CodeFlash `0xFFDB8` (`0x20880` in
this image), and computed-calls the application entry. The broad LocalRAM zero
loops are in its normal caller path, not inside `0x13B0`.

**Recovered implication:** arbitrary boot-context code can call `0x13B0`
directly instead of requesting a hardware reset. That avoids re-entering reset
startup and can preserve upper LocalRAM into application startup.

This is a static control-flow result, not a bench-proven transition from a
custom payload.

### 3.4 Application startup overwrites the XCP shadow window

`FUN_0006263E` copies CodeFlash `0x10000..0x17DEF` to LocalRAM beginning at
`FEBF7C00`. Therefore a bootloader trampoline placed in the normal XCP write
window cannot be expected to survive application initialization.

The adjacent `FUN_00062662` also copies a 0x40-byte table to
`FEBF7BB0..FEBF7BEF`.

### 3.5 Retention pocket: `FEBF0000..FEBF0307`

A direct-reference census over the tracked decompiler corpus finds no
application function with a direct data reference into
`FEBF0000..FEBF0307`. The first recovered application direct reference in the
4 KiB boot payload window is `FEBF0308`, where the application's NvM/SecOC
state begins.

Candidate:

```text
FEBF0000..FEBF0307   0x308 bytes / 776 bytes
```

Confidence is deliberately split:

- **verified:** address relation, MPU coverage, reset clear, first direct
  application reference;
- **bounded:** absence of direct references does not exclude an unmodeled
  computed pointer, DMA, or hardware access.

### 3.6 Application execute permission

Application MPU setup at `0x647D4` loads 16 `MPLA/MPUA` pairs from the table at
`0x31814`; `0x648EE` loads the selected MPAT context. Relevant region:

```text
region 5: FEBEF400..FEBF33FC
context 0 MPAT: 0xB8  supervisor R/W/X
context 1 MPAT: 0xB8  supervisor R/W/X
```

Thus `FEBF0000..FEBF0307` remains supervisor-executable after application MPU
initialization.

### 3.7 Reset / failure semantics

- bootloader `SID 0x11` hard reset is non-returning and re-enters reset startup;
- application shutdown/reset ultimately performs a hardware reset;
- watchdog reset likewise re-enters reset startup;
- a power/ignition cycle loses SRAM physically.

Every real reset therefore removes state in the candidate upper-LocalRAM
pocket. The image does not expose a cause-specific path that skips those clear
loops.

That is favorable for fail-stock behavior:

```text
comma absent before install      -> normal stock boot
failure before install           -> normal stock boot / programming failure only
hardware/watchdog reset          -> temporary upper-RAM state cleared
ignition/power cycle             -> SRAM lost
```

A direct handoff is intentionally the one path that preserves the temporary
state; it is not itself a reset.

## 4. Exact SecOC verifier result path

### 4.1 Producer and consumer

The final application-visible result byte is `FEBE555C`.

Recovered direct-reference graph:

```text
secoc_rx_verify_worker @ 0x8E4BA
  -> secoc_submit_cmac_verify @ 0x8E3EA
       ...
       0x8E41A passes &FEBE555C as the result/output location
  -> ICU-S command-7 completion
       writes the verification result
  -> FUN_0008E67A
       0x8E69E reads FEBE555C
       result != 0 becomes r26 = 1
       ... bookkeeping ...
       0x8E6C6 cmp r0,r26
       0x8E6C8 bne mismatch/reject
       fallthrough = accepted/delivered
```

The whole tracked corpus contains exactly those producer/consumer direct
references for `FEBE555C`.

### 4.2 Why a one-time data write fails

Setting `FEBE555C=0` before a protected frame does not help. The verifier passes
that address to the crypto/ICU-S stack for the current operation and the
completion result is written before Gate 2 evaluates it.

No recovered RAM field changes the final `r26`/branch decision independently of
that result. Nearby profile/state bytes determine state-machine validity and
bookkeeping; they do not convert a failed MAC into the success delivery path.

**Result:** candidate A, a static data-only `result=SUCCESS` preseed, is
**disproved** for this local path.

## 5. Writable function-pointer / callback search

### 5.1 ICU-S interrupt callback: `FEBF1194`

The two ICU-S interrupt channels read the callback at `FEBF1194`, making it an
obvious hook candidate in isolation. It is not a retained boot-to-application
hook:

- `FUN_0008735E`, called by `crypto_icus_initialize`, explicitly zeros
  `FEBF1194` during application startup;
- command-5/7/8 start/completion code later writes fixed stack-owned callbacks
  or clears the cell;
- no request-derived arbitrary callback target is recovered.

A bootloader preseed is therefore destroyed before normal SecOC traffic.

### 5.2 Network/parser callback: `FEBE5600`

`FUN_0008F948` can computed-call the pointer in `FEBE5600`, which initially
looked like a stronger post-init trampoline trigger. Its lifecycle closes the
same way.

Startup chain:

```text
application_startup_coordinator @ 0x62758
  -> FUN_00065626
     -> FUN_0008A030
        -> FUN_00096B82
           -> FUN_00096B66
              -> FUN_0008F1D0
                 -> FUN_0008F6A0
                    -> FUN_0008F688
                       -> FEBE5600 = 0
```

Runtime writer `FUN_0008F750` obtains a callback from fixed descriptor/config
state, stores it to `FEBE5600`, and invokes it as part of the active
transaction. The pointer is not recovered as an attacker-supplied wire value.

A bootloader preseed therefore does not survive startup, and the normal runtime
writer does not furnish an arbitrary target.

### 5.3 Exception/vector and scheduler indirection

The application does not install its primary exception dispatch through a
retained LocalRAM vector pointer. `application_cpu_context_init @ 0x70524`
installs `EBASE=0x20000` and `INTBP=0x20200`; both bases are in CodeFlash, and
the 384-entry EIINT table occupies the CodeFlash range `0x20200..0x207FF`.
Direct exception vectors likewise branch to fixed CodeFlash handlers. The
ICU-S EIINT wrappers eventually use `FEBF1194`, but that callback is explicitly
zeroed during startup as described above.

The foreground design is cooperative rather than an RTOS with a writable RAM
task table. Recovered system-mode and COM callback dispatchers use fixed
CodeFlash callback tables/configuration. The whole-corpus computed-call census
also closed additional RAM-backed targets beyond the two obvious callbacks:

- `FEBF7704` is called at `0x72E56`, but every recovered call path runs
  `FUN_72A9C -> FUN_72E5E` first, replacing the cell with fixed CodeFlash
  `0x75664` or `0x7575A`;
- ICU-S lower callbacks `FEBF117C/1180` are explicitly zeroed by `FUN_8735E`;
- crypto driver callbacks `FEBF131C/1320/1324` are reset by
  `icus_driver_state_initialize @ 0x89360`;
- crypto job pointer families around `FEBF1370..139C` are reset by the startup
  initializers selected by `FUN_88C28`.

The reusable investigation scripts are
`ghidra/scripts/investigate/ExportIndirectControlTransfers.java` and
`ClassifyComputedCallTargets.java`. The negative remains bounded against
unmodeled corruption/runtime aliasing, but no stock callback is needed by the
final scheduler-owned architecture.

### 5.4 Search conclusion

No recovered RAM callback/function pointer simultaneously satisfies all three
requirements:

1. survives application initialization;
2. is invoked after normal tasks begin; and
3. can be made to point to the retained/XCP RAM region from the available
   boot/application inputs.

That remains the conclusion for a **stock callback hook**. CORR-068 records why
it is no longer an architectural blocker: the retained payload can own the
application foreground schedule itself.

## 6. RAM-executed code already present in the firmware

### 6.1 Bootloader authenticated RAM execution: confirmed

The bootloader intentionally executes a 4 KiB authenticated object in
`FEBF0000..FEBF0FFF`. The validated metadata and callback live at the top of the
same page, and the `0xFF00` dispatcher loads the callback and uses an indirect
call.

This proves ordinary SRAM execution is a supported firmware design, not merely
an MPU-theory possibility.

### 6.2 Application executable RAM: confirmed; stock consumer still absent

The XCP/shadow window `FEBF7C00..FEBFFBFF` has supervisor execute permission and
is externally writable through the recovered XCP `F0 DOWNLOAD` / `EC
MODIFY_BITS` paths. The application startup also copies CodeFlash into that
window.

However, the direct-reference census still contains no stock code-transfer
consumer into the XCP window. Its usefulness is therefore:

- post-init code/data storage if a separate control-transfer primitive is found;
- a convenient command mailbox for a future resident shim;
- not, by itself, code execution.

### 6.3 No independent application relocation loader recovered

Beyond the bootloader payload mechanism and the application page-shadow copy,
this pass did not recover a generic application loader that takes an arbitrary
RAM destination and then branches there.

## 7. Toyota authenticated payload / flash-driver lifecycle

### 7.1 Bootloader side of the lifecycle

Recovered lifecycle:

```text
programming session + SecurityAccess
  -> DIDs 0203 / 0201 / 0202 establish payload parameters
  -> RequestDownload
  -> TransferData decrypt/copies into FEBF0000..FEBF0FFF
  -> TransferExit
  -> routine 10F0 validates address/size/CRC/CMAC
  -> accepted state retained
  -> 0xFF00 loads callback from FEBF0FD0 and calls RAM code
  -> bootloader flash-operation state machine invokes that callback for
     erase/program/check operations
```

The stock bootloader ABI therefore already provides legitimate RAM execution
and a callback-oriented flash-driver interface.

### 7.2 The payload-build secret is not required after one accepted payload

MEM-SAFE-001 is decisive here. After one successful `0x10F0`, subsequent
`RequestDownload`/`TransferData`/`TransferExit` sequences do not clear the
accepted authorization state. A 1..15-byte final download chunk executes zero
AES blocks but is still raw-copied to the validated destination.

Repeated small downloads can consequently substitute arbitrary raw bytes
throughout `FEBF0000..FEBF0FFF`, including the RAM callback.

Therefore:

```text
one legitimate authenticated Toyota payload
  -> accepted authorization state
  -> raw-substitution primitive
  -> arbitrary boot-context RAM code
```

This is stronger than needing the OEM driver's own private command surface.

### 7.3 What the local artifacts cannot answer

The local Techstream V18 corpus contains no matching `8965B4512000` `.cuw` or
`.cal`. It therefore cannot currently provide the exact OEM authenticated blob
for this ECU, nor can this repository statically reverse any private protocol
implemented inside that absent blob.

Do **not** claim that the Toyota driver itself supports arbitrary SRAM write or
arbitrary call. Those questions are artifact-bounded.

The bootloader/MEM-SAFE-001 composition is the supported route instead.

## 8. Reusing the pinned authenticated payload rather than forging one

The Sienna bootstrap has no remaining CUW/payload artifact dependency. Two
committed public encrypted fixtures are already accepted by the exact recovered
`8965B4512000` gate:

| fixture | ciphertext SHA-256 | size |
|---|---|---:|
| `tests/fixtures/payloads/ram_dump_payload.bin` | `d972d4bf432685217591768600a9abd7820d35b04a72270edc87074365356be2` | `0x1000` |
| `tests/fixtures/payloads/dataflash_dump_payload.bin` | `d48988366b5e6d2ddd7438caca5e6f6f02daba9b650263c323a2ffd770a06e34` | `0x1000` |

`tests/verify_payload_gate.py` decrypts each with this image's recovered payload
construction and proves:

- callback slot `+0xFD0 = FEBF0000`;
- CRC descriptor `FEBF0000 / 0xFF0`;
- CRC32 residue `0xFFFFFFFF`;
- CMAC over `DID_0x202_IV || plaintext[0:0xFF0]`;
- exact AES-CBC ciphertext round trip.

The fixture construction uses tester values `DID 0x0201 = 00*16` and
`DID 0x0202 = 00*16`, which `exploit/common/ram_exec.py` already writes. Thus
replaying the fixture does **not** require knowing `PAYLOAD_BUILD_SECRET` or
obtaining a matching CUW. Bootloader SecurityAccess remains mandatory, but its
separate `SEED_KEY_SECRET` is already recovered/verified for this firmware and
the host deliberately accepts it through an environment/file input rather than
hard-coding it into live tooling.

The matching CUW still matters for dealer-flow provenance and for targets where
these pinned fixtures do not transfer. It is not on the Sienna RAM-runtime
critical path.

Supported Sienna bootstrap:

```text
recovered boot SecurityAccess secret
  -> programming session + SecurityAccess
  -> DID 0203 setup; DID 0201/0202 = zero
  -> upload pinned encrypted 4 KiB fixture
  -> RID 10F0 passes CRC+CMAC
  -> MEM-SAFE-001 post-auth raw substitution
  -> arbitrary boot-context RAM execution
```

`exploit/ephemeral_runtime/build_substitution_plan.py` binds the RAM-dump fixture
SHA directly before emitting substitutions.

## 9. Transition back to normal application

### 9.1 Hardware reset is the wrong transition for retention

A normal `11 01`, watchdog reset, or other hardware reset re-enters reset startup
and clears the upper-RAM payload region. It cannot retain a trampoline.

### 9.2 Direct application handoff is the viable transition

A custom boot-context payload can in principle invoke
`boot_application_handoff @ 0x13B0` directly. That preserves the candidate
`FEBF0000..FEBF0307` pocket while still using the stock bootloader's handoff and
stock application entry.

Application startup then initializes CPU context, MPU, drivers, SecOC, CAN, and
normal tasks. The pocket remains within an application supervisor-RWX MPU
region.

### 9.3 Post-init re-entry is unnecessary: retain scheduler ownership

Application startup does intentionally destroy the known boot-preseedable
callback states and overwrite the XCP shadow region. The exhaustive computed-call
audit also closes additional attractive cells: `FEBF7704` is overwritten with
fixed CodeFlash targets immediately before its only call; `FEBF117C/1180`,
`FEBF1194`, `FEBF131C/1320/1324`, and the `FEBF1370..139C` crypto-job pointer
families are reset by their startup initializers.

Those negatives do **not** prevent a resident runtime. The stock application
transition is sufficiently flat that the RAM payload can perform it directly:

1. call the four stock boot transition initializers and `boot_validity_check`;
2. call `application_cpu_context_init @ 0x70524`, which installs application
   `INTBP/EBASE/GP/TP/SP` and returns through `lp`;
3. decode and call the 21 consecutive stock `jarl disp22` instructions at
   `0x62760..0x627B0`;
4. call final initializer `0x6F15A(0)` and execute `ei`;
5. remain resident and reproduce the top-level foreground loop instead of
   entering stock `application_foreground_cyclic_loop @ 0x64FCC`.

The top-level stock loop is small: it polls TAUJ0 CH3 and calls a short sequence
of coarse tasks. The audited resident build implements that sequence and fits
entirely in the 0x308-byte retained application-RWX pocket.

**Static conclusion:** no post-initialization callback is required. The
callback-free scheduler-shell architecture is constructible; hardware execution
remains unobserved.

### 9.4 Audited resident build

Tracked implementation: `exploit/ephemeral_runtime/`.

Pinned build result:

```text
entry offset: 0
.text size:   704 bytes / 0x2C0
retained max: 776 bytes / 0x308
headroom:     72 bytes
relocations:  0
sha256:       8f486d36ae38d233165563ad2cc4a71d006cf5c8cf9a876345a3b6ab72f10495
```

This is **generated-artifact evidence**, not a bench observation. The builder
pins the Docker image content ID and rejects oversized or relocatable output.

## 10. Data-only alternatives

### 10.1 SecOC result preseed — disproved

`FEBE555C` is overwritten for each verification and has no recovered policy
indirection. Not viable.

### 10.2 Descriptor modification — no final-decision bypass recovered

ICU-S descriptors carry command/slot/message/tag/result information, but the
application constructs the verify operation around fixed profile logic and the
final success decision still consumes the current result byte. No RAM descriptor
field was recovered whose static modification converts a failed MAC into a
success result without either controlling code execution or changing the crypto
operation itself.

This remains a useful corruption surface only if a separate arbitrary writer is
available at the correct time; it is not an independent bypass.

### 10.3 Message-routing / callback redirection — startup-cleared

The attractive RAM callbacks are either actively initialized to zero or written
from fixed tables before use. No retained arbitrary routing pointer was found.

## 11. Stock COM delivery is the preferred steering injection boundary

Resident execution makes a cleaner hook available than writing
`FEBEF184/FEBEF02A` directly: reuse the stock COM receive-delivery API.

SecOC queue storage for the two recovered steering profiles is:

| CAN | record | secured raw buffer | descriptor | COM PDU | COM update counter |
|---:|---:|---:|---:|---:|---:|
| `0x2E4` | 1 | `FEBE5490..5497` | `FEBE545A` | 6 | `FEBE5332` |
| `0x131` | 2 | `FEBE5498..549F` | `FEBE5462` | 26 | `FEBE5346` |

`secoc_rx_queue_secured_pdu` copies the received secured frame into those raw
buffers **before** CMAC verification. The top-level task `FUN_65750` then calls:

```text
0x68C0C
0x791C4     communication stack; reaches SecOC verify/Gate 2 and cleanup
0x96BAC
0x68DE6
0x57AC2     later COM unpack + system-mode/control work
0x6547C
```

The resident runtime therefore:

1. snapshots a newly queued selected frame before `0x791C4`;
2. runs `0x791C4/0x96BAC/0x68DE6` unchanged;
3. if stock processing did not already deliver the PDU, calls
   `application_com_rx_indication @ 0x7C640` with the saved eight-byte frame;
4. enters `0x57AC2`, allowing the stock generated COM unpackers and normal
   steering pipeline to consume it.

The local-bridge marker is **MAC28 all zero**: byte-4 low nibble plus bytes 5..7,
matching the existing MAC28-only behavioral-proof transform. Authentic payload
bytes and byte-4 high transmitted-freshness nibble are preserved.

A saved pre-delivery COM update counter prevents duplicate delivery if stock
SecOC unexpectedly accepted the frame. An `active_mask` edge-detects a queue
record that remains pending across multiple foreground ticks, preventing stale
replay while an asynchronous operation is outstanding. When comma traffic
stops, no fresh marked record exists, no bridge call occurs, and the stock COM
timeout path remains responsible for command expiry.

This is preferable to direct internal-state writes because it preserves an even
larger portion of the stock receive/control pipeline: COM validity/update state,
normal unpacking, source arbitration, clamp/rate-limit, plausibility, and fault
logic all remain downstream.

The prior `FEBEF184/FEBEF02A` recommendation remains a useful fallback if the
COM bridge proves dynamically unsuitable, but it is no longer the primary
architecture.

## 12. Comma does not need a new command transport

The static implementation can reuse the **ordinary protected steering CAN
frames themselves**:

```text
comma/panda sends normal 0x2E4 / 0x131
  -> authentic payload fields populated normally
  -> MAC28 deliberately zeroed as local bridge marker
  -> EPS normal CAN/SecOC ingress queues secured frame
  -> resident scheduler snapshots it before verification
  -> stock SecOC rejects/cleans it
  -> resident scheduler re-delivers through stock Com_RxIndication
  -> stock COM unpack/system-mode/control pipeline
```

This avoids a new mailbox, XCP command channel, or proprietary side protocol.
It also leaves unmarked/valid stock SecOC traffic on the original path.

The mechanism is **not yet deployable evidence**: live CAN queue timing,
foreground jitter, and steering behavior still require isolated-bench
validation.

## 13. CAN proxy / "comma as EPS"

Pure CAN MITM/proxying does not solve this ECU's inbound command problem.
Protected steering frames still enter the real EPS receive stack and pass
through ICU-S verification and Gate 2 before the command state is delivered.
Suppressing or impersonating EPS-originated traffic does not change that
receiver-side enforcement.

A proxy can remain useful for capture, filtering, isolation, or experiments,
but it is not a standalone SecOC solution. Full EPS emulation is not justified
by the static graph and was not pursued.

## 14. Failure semantics

| Candidate | If comma never installs it | If comma dies after install | Hardware/watchdog reset | Persistent flash risk |
|---|---|---|---|---|
| data-only verifier preseed | stock | not viable | stock | none |
| retained RAM scheduler + COM bridge | stock | no fresh marked frame -> no bridge delivery; stock COM timeout remains active | stock | none |
| direct internal-command fallback | stock | requires explicit freshness/fail-silent strategy | stock | none |
| authenticated-loader bootstrap | stock/programming session only until transition | depends on installed RAM runtime | stock | none if flash operations are not invoked |
| persistent Gate-2 patch | modified firmware | modified firmware | remains patched | yes |

A future implementation should never use the flash-driver write/erase commands
merely to obtain ephemeral behavior. The bootstrap should remain RAM-only after
SecurityAccess and payload acceptance.

## 15. Ranked architecture recommendation

### 1. D + scheduler-owned COM bridge

**Rank: best supported RAM-only direction; statically constructible, bench proof pending.**

D is solved statically by existing authenticated execution plus MEM-SAFE-001.
The retained `FEBF0000..0307` R/W/X pocket provides clear-on-reset persistence,
and the 704-byte callback-free runtime fits with 72 bytes of headroom. By owning
the top-level foreground schedule, it removes the former post-init callback
dependency. Bridging marked `0x2E4/0x131` through stock
`application_com_rx_indication` preserves more stock behavior than direct state
writes.

### 2. C: direct internal steering injection

**Rank: fallback if the stock-COM bridge is dynamically unsuitable.**

`FEBEF184` / `FEBEF02A` remain the preferred direct-state fallback rather than
low-level motor-current state. They preserve clamp/rate-limit/source-arbitration
logic, but the COM bridge is now cleaner because it also preserves the stock COM
validity/update and unpack layers.

### 3. B: stock RAM callback/function hook

**Rank: unnecessary for the primary architecture; static candidates closed.**

The known RAM-backed computed-call targets are startup-reset or overwritten from
fixed CodeFlash descriptors before use. This no longer blocks RAM residency
because the scheduler-shell path never requires stock code to call back into
RAM.

### 4. A: data-only SecOC bypass

**Rank: currently unsupported / local result-preseed approach disproved.**

No RAM policy/result field was found that persistsently forces Gate-2 success.

### 5. E: pre-auth bootloader vulnerability

**Rank: unnecessary for `8965B4512000`; still relevant only to transfer targets.**

The current security/memory-safety audit has no verified primitive that bypasses
the *first* authenticated payload. It does not need one on this image: the
repository already possesses public encrypted fixtures that satisfy the exact
Sienna gate. MEM-SAFE-001 then gives the execution upgrade after their one
successful `0x10F0`. Pre-auth research only regains priority on a target where
neither the fixture nor known credential route transfers.

### 6. F: persistent CodeFlash patch

**Rank: proven fallback, worst failure semantics.**

The corrected Gate-2 predicate patch remains the only **live-field-corroborated**
bypass mechanism in this repository, but it is persistent and carries
flash/recovery risk. The RAM scheduler bridge is statically complete but has not
run on hardware, so the persistent patch remains the operational fallback until
that bench proof exists.

## 16. Explicitly ruled out / bounded approaches

| Approach | Status | Evidence |
|---|---|---|
| pre-zero `FEBE555C` | disproved | verifier writes current result before Gate 2 |
| preseed `FEBF1194` ICU-S callback | disproved across startup | crypto/ICU-S startup zeros it |
| preseed `FEBE5600` parser callback | disproved across startup | startup reset chain reaches `FUN_8F688` zeroing it |
| place trampoline in XCP window before app init | disproved as retention plan | app startup copies CodeFlash into `FEBF7C00..` |
| ordinary hardware reset after installing upper-RAM trampoline | disproved as retention plan | reset clears upper LocalRAM |
| pure CAN proxy / EPS impersonation | disproved as SecOC solution | real EPS still verifies inbound protected steering frames |
| OEM driver has arbitrary SRAM write/call | bounded / unknown | matching OEM payload absent from local artifacts |
| retained `FEBF0000..0307` pocket has no computed/DMA owner | bounded | direct-ref negative only; needs dynamic canary proof |
| stock post-init callback is required | disproved as architecture requirement | callback-free runtime owns the application foreground schedule |

## 17. Highest-value next experiments

Static work now supports a complete runtime architecture, so the next steps
should validate it in increasing-risk order rather than resume broad xref work.

1. **Bench-prove transition + scheduler ownership with the inert runtime.** The
   tracked `exploit/ephemeral_runtime/canary.c` performs the same
   boot/context/startup transition and preserves stock `0x65750` whole; it never
   calls `application_com_rx_indication`. Its audited build is 332 bytes and
   increments heartbeat `FEBFFBF0`, which is readable through stock application
   SID `0x23` via `application_rmba_probe.py --probe-ephemeral-canary`. Verify
   heartbeat progression, normal watchdog/tick behavior, and reset-to-stock.
2. **Bench-prove one-shot marked-frame capture without steering delivery.** Log
   queue descriptor/raw-buffer transitions for zero-MAC `0x2E4/0x131` and prove
   `active_mask` suppresses repeats across asynchronous pending ticks.
3. **Enable the COM bridge on an isolated bench.** First verify the PDU update
   counters and COM destinations, then perform the existing three-phase steering
   behavioral proof. Preserve timing, DTC, CAN, and reset evidence.
4. **Only if the stock-COM bridge fails dynamically**, fall back to the earlier
   pre-limiter `FEBEF184/FEBEF02A` direct-state injection architecture.

## 18. Reproducer

`tests/verify_ephemeral_secoc_bypass.py` pins the RAM-lifetime/MPU/callback
boundary. `tests/verify_ephemeral_runtime.py` independently pins the callback-free
runtime architecture:

- stock boot transition and application CPU-context install;
- exact 21-entry startup `jarl disp22` sequence;
- foreground TAUJ0 CH3 and top-level task order;
- `FUN_65750` splice ordering;
- communication -> SecOC verify/Gate-2 call chain;
- pre-verification secured-record buffers/descriptors for `0x2E4/0x131`;
- stock COM buffer/update-counter joins;
- audited 704-byte, zero-relocation resident build and source/toolchain identity.

Neither test claims hardware execution. The tracked canary and
`build_substitution_plan.py` now make the first dynamic proof reproducible:
post-`0x10F0` raw-substitute the 332-byte inert runtime, write `FEBF0FD0 =
FEBF0000` last, trigger the existing `0xFF00` callback path, and observe
`FEBFFBF0` through read-only application RMBA. The remaining proof class is
dynamic.


## Cross-calibration runtime transfer

The Sienna implementation is no longer an address-hard-coded payload.
`tools/resolve_ephemeral_runtime_image.sh` performs a fresh disposable CodeFlash
import, resolves Gate 2 plus the callback-free startup/scheduler skeleton, then
completes the pointer-table/RAM anchors from raw RH850 signatures and GP/TP-relative
displacements. `tools/build_ephemeral_runtime_manifest.py` derives the target's
queue-1 record count and Gate-2 table base from machine structure, validates each
configured SecOC record, and only then asks whether the current steering bridge's
`0x2E4/0x131` profiles exist. RAM execution/retention geometry remains a separate
join.

The separation is deliberate. A foreign image may resolve the same application
and SecOC architecture while either lacking Sienna's steering profiles or lacking
proof that its authenticated payload window survives into application-RWX RAM.
The former is emitted as `semantic-resolved-steering-unsupported`; the latter as
`semantic-resolved-geometry-unresolved`. Runtime builders refuse both. Sienna RAM
geometry is selected only by the exact CodeFlash SHA-256. Supplying the Sienna
variant ID against a foreign image is an error, not an override.

The tracked 2023-Corolla `8965H1202000` image is now the first foreign proof of
that distinction. The resolver transfers the boot/startup/foreground/Gate-2/COM
architecture unchanged, but the actual queue has exactly `0x00F/0x0D7/0x0B6`,
not `0x2E4/0x131`; its manifest therefore resolves successfully and stops at the
steering-capability boundary. The image also carries the same payload-build,
boot-SA, and application-SA roots as `8965B4512000`, while the owner-side range
dumps provide direct observed bootstrap execution evidence.

Both RH850 sources now consume only a generated `target_config.h`; boot calls,
application context/startup, foreground tasks, SecOC queue addresses, COM
delivery, update counters, and canary observation are supplied by the target
manifest. On `8965B4512000`, the target-driven build reproduces the previously
audited executables byte-for-byte: the 704-byte bridge retains SHA-256
`8f486d36ae38d233165563ad2cc4a71d006cf5c8cf9a876345a3b6ab72f10495`, and
the 332-byte inert canary retains
`81176c6e1c33451cfa63bd3b4a0e07b8b0fb952c70b3d67442f1a294ed6b651e`.

A canary build additionally requires a target-specific observation cell. Sienna
uses verified `FEBFFBF0` through manifest evidence; a new target cannot inherit
that address. Bootstrap compatibility is tracked separately in
`data/variant_bootstrap_profiles.json`: SECOC-024/028 already establish the
shared `f05f...` SecurityAccess/DID/`FEBF0000`/`10F0`/`FF00` family across
multiple B4/F3/F4 EPS targets, and `8965H1202000` now adds a tracked
field-observed execution case. What is target-specific is the evidence grade for
**exact encrypted payload bytes** and for retained application-RWX geometry.
`build_substitution_plan.py` therefore accepts any manifest with a matching
bootstrap-family profile, but requires an explicitly SHA-pinned target-accepted
fixture when the repository's Sienna fixture is not proven byte-for-byte for
that software ID.

Canonical tooling and failure modes are documented in
[../tooling/ephemeral-runtime-semantic-resolver.md](../tooling/ephemeral-runtime-semantic-resolver.md).
