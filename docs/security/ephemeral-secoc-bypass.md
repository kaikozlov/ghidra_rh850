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

The important result is narrower than "RAM execution exists." Bootloader RAM
execution and a reset-cleared application-RWX retention pocket are both
recovered. What is **not** recovered is a stock post-initialization control
transfer into that pocket. That is the remaining architectural blocker.

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
8. **Bounded:** the matching `8965B4512000` CUW / factory payload is not present
   in the local Techstream corpus, so the OEM RAM driver's private command
   interface cannot be recovered from current artifacts. This does not block
   the MEM-SAFE-001 bootstrap once any matching payload can be accepted.

### Practical conclusion

The best currently supported architecture is:

```text
matching CUW credentials / valid Toyota payload
  -> bootloader SecurityAccess
  -> one valid authenticated 0x10F0
  -> MEM-SAFE-001 raw substitution
  -> arbitrary boot-context code in FEBF0000..0FFF
  -> direct boot_application_handoff @ 0x13B0 (no hardware reset)
  -> retain code/data in FEBF0000..0307
  -> application initialization completes
  -> ??? post-init stock control-transfer trigger
  -> temporary hook or internal-command shim
```

Everything through the retained R/W/X pocket is statically supported. The
`???` remains unresolved. No recovered writable callback, exception pointer,
scheduler entry, or request-derived function pointer survives startup and then
jumps into attacker-selected RAM.

That means an ephemeral bypass is **feasible in storage/execution terms but not
yet end-to-end proven**.

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
CodeFlash callback tables/configuration. The whole-corpus indirect-call sweep
was reviewed for functions that also directly reference LocalRAM; it did not
recover a scheduler/task slot whose post-init target is both RAM-resident and
attacker-selectable. This is a bounded static negative, not a claim that a
computed pointer or corruption path cannot exist at runtime.

### 5.4 Search conclusion

No recovered RAM callback/function pointer simultaneously satisfies all three
requirements:

1. survives application initialization;
2. is invoked after normal tasks begin; and
3. can be made to point to the retained/XCP RAM region from the available
   boot/application inputs.

This is the central missing primitive for a RAM function hook.

## 6. RAM-executed code already present in the firmware

### 6.1 Bootloader authenticated RAM execution: confirmed

The bootloader intentionally executes a 4 KiB authenticated object in
`FEBF0000..FEBF0FFF`. The validated metadata and callback live at the top of the
same page, and the `0xFF00` dispatcher loads the callback and uses an indirect
call.

This proves ordinary SRAM execution is a supported firmware design, not merely
an MPU-theory possibility.

### 6.2 Application executable RAM: confirmed, stock consumer missing

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

## 8. Reusing stock payload rather than forging one

The architecture proposed in this investigation is statically supported with
one important target-artifact dependency:

```text
matching CUW
  -> obtain ECUAuthKey / ServiceAuthKey and original authenticated payload
  -> use recovered CUW SecurityAccess construction
  -> send the original payload unchanged
  -> one successful 0x10F0
  -> exploit post-auth raw substitution
  -> arbitrary boot-context RAM execution
```

Modern CUW SecurityAccess construction is already recovered in
`tooling/techstream.md`. A matching CUW credential pair should be sufficient to
perform SecurityAccess without learning the ECU-family root secret. The exact
`8965B4512000` pair remains unavailable locally.

**Conclusion:** recovering `PAYLOAD_BUILD_SECRET` is not a prerequisite to this
bootstrap. Acquiring a matching legitimate CUW/payload is the higher-value
artifact.

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

### 9.3 The unresolved problem is post-init re-entry

Application startup intentionally destroys the known boot-preseedable callback
states and overwrites the XCP shadow region. No retained pointer-to-pocket
trigger has been recovered.

A successful end-to-end design therefore still needs one of:

- a writable post-init callback/function pointer with a controllable target;
- a scheduler/task indirection that can be registered after startup;
- an exception/vector redirection that remains legal after the application sets
  `EBASE/INTBP`;
- a second application-mode control-flow vulnerability;
- a runtime trigger that reaches retained code through a computed address.

Until one is recovered or dynamically demonstrated, the ephemeral code-hook
architecture is **bounded, not operational**.

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

## 11. Internal steering-command injection

If a resident application shim is eventually obtained, injecting **before the
stock steering limiters** is preferable to forcing SecOC success or writing
low-level motor-current state.

Recovered protected `0x2E4` torque path:

```text
FEBE7F94
  -> FEBEF184
  -> system_mode_telemetry_snapshot @ 0xBA43A
  -> FEBEAE20
  -> 0xC853A clamp/gain
  -> FEBEBF80
  -> 0xC85B6 saturation/rate limit
  -> FEBEBF9A / FEBEBF84
  -> FEBEBFA2
```

Request/mode path:

```text
FEBE7F98
  -> FEBEF02A
  -> FEBEACFF
  -> 0xCA354 source arbitration
  -> FEBEC137
  -> 0xCA3F8 torque-mode selection
  -> FEBEC13D = external-request
  -> 0xCA6B8 selects common command at FEBEC144
```

A future shim should therefore prefer the pre-limiter copied inputs
`FEBEF184` (torque) and `FEBEF02A` (request/mode) rather than writing
`FEBEBFA2`, `FEBEC144`, or any d/q-current/PWM cell. That retains the recovered
stock clamp, rate-limit, source arbitration, driver/fault logic downstream of
the normal input-copy layer.

This is an **architecture recommendation, not a live mutator implementation**.
The separate static actuation study still has no proved direct join from this
command cone into the recovered d/q reference producers; dynamic isolated-bench
validation remains necessary.

A resident shim would also need its own freshness/timeout contract so loss of
comma input causes it to stop injecting and/or request a reset rather than hold
a stale command.

## 12. Can comma inject below SecOC?

Conceptually yes **if** the missing resident-code trigger is solved:

```text
comma/panda command channel
  -> application RAM mailbox (XCP window is one possible store)
  -> resident shim
  -> FEBEF184 / FEBEF02A
  -> stock downstream command pipeline
```

This is cleaner than manufacturing authenticated `0x2E4` frames because it
bypasses the CAN/SecOC entrance while preserving the stock pre-actuation command
processing.

It is not currently deployable because the resident shim lacks a proved
post-init execution trigger.

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
| retained RAM code + post-init hook | stock | shim policy-dependent; should timeout/reset | stock | none |
| internal-command shim | stock | requires explicit freshness/fail-silent strategy | stock | none |
| authenticated-loader bootstrap | stock/programming session only until handoff | depends on installed shim | stock | none if flash operations are not invoked |
| persistent Gate-2 patch | modified firmware | modified firmware | remains patched | yes |

A future implementation should never use the flash-driver write/erase commands
merely to obtain ephemeral behavior. The bootstrap should remain RAM-only after
SecurityAccess and payload acceptance.

## 15. Ranked architecture recommendation

### 1. D + B/C: authenticated Toyota bootstrap -> retained RAM -> runtime hook

**Rank: best supported direction, missing one post-init transfer primitive.**

D is largely solved statically by existing authenticated execution plus
MEM-SAFE-001. The retained `FEBF0000..0307` R/W/X pocket and direct handoff solve
storage/lifetime. The missing part is B: a post-init call into retained RAM. If
B is recovered, C (internal command injection before stock limiters) is the
preferred payload behavior.

### 2. C: internal steering injection

**Rank: preferred behavior once resident execution exists.**

Use `FEBEF184` / `FEBEF02A` or an equivalently early stock command ingress, not
low-level motor-current state. This avoids pretending a MAC passed and retains
more of the stock downstream command processing.

### 3. B: RAM function hook specifically around SecOC

**Rank: technically attractive, no stock hook found yet.**

The retained application-RWX pocket makes it possible in principle, but both
obvious callback families are startup-reset. A new post-init control transfer
must be found.

### 4. A: data-only SecOC bypass

**Rank: currently unsupported / local result-preseed approach disproved.**

No RAM policy/result field was found that persistsently forces Gate-2 success.

### 5. E: pre-auth bootloader vulnerability

**Rank: unnecessary unless matching CUW/payload acquisition fails.**

The current security/memory-safety audit has no verified primitive that bypasses
the *first* authenticated payload. MEM-SAFE-001 is post-auth and already gives
the needed execution upgrade. Do not spend broad effort on pre-auth bugs while
a legitimate CUW path remains plausible.

### 6. F: persistent CodeFlash patch

**Rank: proven fallback, worst failure semantics.**

The corrected Gate-2 predicate patch remains the only currently established
end-to-end bypass mechanism, but it is persistent and carries flash/recovery
risk. It should remain the fallback while the runtime-transfer dependency is
investigated.

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

## 17. Highest-value next experiments

Static work is exhausted enough that the next steps should be discriminating,
not another generic xref sweep.

1. **Acquire the matching `8965B4512000` CUW/payload.** This closes the only
   artifact dependency for the legitimate-authentication bootstrap and provides
   the actual factory credential pair/payload.
2. **Bench-prove direct-handoff retention with a harmless canary.** After an
   accepted payload/raw-substitution sequence, place a non-executable marker in
   `FEBF0000..0307`, invoke `0x13B0` without hardware reset, then observe the
   marker from an application read-only channel. Do not start with steering.
3. **Search dynamically for a post-init call primitive.** If XCP is physically
   reachable, use it first as a read-only observer. Any future control-transfer
   experiment should target inert instrumentation, not torque state.
4. **Only after resident execution is independently proved**, prototype a
   timeout/freshness-controlled shim against pre-limiter internal command state
   on an isolated bench.

## 18. Reproducer

`tests/verify_ephemeral_secoc_bypass.py` pins the current static boundary:

- reset clear geometry;
- direct handoff / application entry;
- application overwrite of the XCP shadow;
- retained-pocket direct-reference bound;
- MPU execute permission;
- exact `FEBE555C` producer/consumer graph;
- corrected Gate-2 predicate bytes;
- callback reset/initialization behavior.

It intentionally does **not** assert that an end-to-end post-init hook exists.
