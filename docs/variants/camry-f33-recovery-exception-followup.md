# F33 recovery follow-up: exception masks, reset state, and transport execution

2026-09-11. Offline analysis of exact `8965F3307000` firmware and the retained
Renesas P1M-E hardware manual. No vehicle connection, CAN transmission, reset,
RAM upload, or flash write was performed. No working CAN-only recovery method
was established.

## Image-state check

The canonical stock CodeFlash is
`firmware/camry-8965F3307000/CodeFlash.bin` (VA equals file offset), SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.
The local reconstruction of the incident image hashes to
`aba6867f244dda42b754d6f455f25a226ee95025dee6a2d98b07b3ac550f2d74`,
the expected post-write image from the incident record. It is not a new live
whole-flash readback.

Comparing that reconstruction with stock shows that these reviewed regions
are unchanged: boot `00000..0FFFF`, CAN/DCM tables `21000..2BFFF`, startup and
exception code `60000..71FFF`, diagnostic workers `90000..98E7F`, the reviewed
XCP parser/gate body `98E80..98EF3`, MPU configuration `3167C..31787`, and
XCP-disable byte `30D68`. Earlier SecOC modifications are distinct from these
regions. The pre-hook stage-6 image is not an untouched factory image.

## 1. `ei` does not clear the separate FE-exception mask

Raw default application exception handler `62E1E` saves state, executes `ei`
at `62E36`, calls the register-save helper `712CE`, and spins at `62E42`.
There is no boot diagnostic call, exception return, or `PSW.NP` clear in that
reviewed path.

Renesas **R01UH0585EJ0120**, *RH850/P1M-E Hardware Rev.1.20*, p.198, distinguishes
`PSW.NP` from `PSW.ID`: acknowledgement of an FE-level exception sets NP and
inhibits the relevant EI/FE exception acknowledgements; `ei` clears ID, not NP.
Thus, **for an FE-level fault, `ei` alone does not prove that ordinary CAN/timer
interrupts remain serviceable**. The PSW table was visually checked in the PDF.

The exact live incident exception remains unobserved. At `7A272`, the recorded
four bytes and next stock halfword form `FF 02 92 5B 24 36`, a six-byte JARL to
`362BFE04`. Hardware Table 4.1 (p.257) marks `20000000..FEBDFFFF` reserved and
Section 4.2.1 limits instruction fetch to CodeFlash, LocalRAM-self, and
GlobalRAM. Table 3.80 assigns FEIC `13H` to a SYSERR caused by an instruction
fetch from other than CodeFlash. Section 3.2.3.3 classifies SYSERR as an FE-level
exception from which return or recovery is not possible. These facts make
SYSERR `13H` the bounded hardware-static interpretation of the malformed call;
the missing live FEIC observation should still be kept distinct from that
interpretation.

The broad firmware MPU region spanning `00000000..FEBDFFFF` does not map the
reserved system address range or make it a valid instruction source. Its
supervisor-execute permission is therefore not a competing recovery mechanism.

Sources: raw `62E1E..62E43`, `712CE`; MPU loader `6586A/65984`, bounds `31688`,
attributes `31708/31748`; manual pp.198, 215, 219–220, 244, 247, 257–259. The
separate vector-90 handler `65BD4` returning through saved `FEPC+4` is not
evidence that this fault returns through the malformed call's `LP`.

## 2. A receive callback can run without executing its diagnostic request

`79EDE -> 809FE -> 808D6 -> 80884` performs receive/deferred-indication work
before the bad call inside `7A254`. The normal foreground diagnostic worker
`988C2` and system-mode worker `58B5E` are later calls in `667E6`.

All three configured diagnostic routes use the same upper callback family:

| CAN ID | ISO-TP RX record | Lower handle | Upper PDU |
|---|---:|---:|---:|
| `7A1` | `22BDE` | `0804` | `0802` |
| `777` | `22BFE` | `0805` | `0803` |
| `7A0` | `22C1E` | `0806` | `0804` |

The reviewed single-frame chain is
`81200 -> 79DB0 -> 7A57A -> 7A4E4 -> 7ADF8 -> 7AD96`, through fixed PDU-router
callbacks and `7BE58/7BE6C/7BE90` to DCM `920BE/92152/921D2`.

The nested completion path `921D2 -> 91F72 -> 92B4A -> 92AB0/92A86` was also
inspected: it prepares request buffers/state, not the requested service.
`98B3A` writes timer deadlines and flags. Timer slot 6's callback `922EA`
queues event 0 through `989EC`; the latter writes an event ring, not an inline
service call. Timer worker `98AE4` and event consumer `98946` run under `988C2`.

The recovered application-to-boot handoff remains
`58B5E -> 5F464/5F91C -> 56CF6 -> 65F5E -> 9F00 -> 148E -> 1398`.
Thus, even granting surviving receive interrupts, the reviewed normal service
and handoff paths still require foreground execution past the corrupted call.
Suppressing a positive response does not remove that dependency. No direct
boot entry was found in the reviewed receive-completion chain.

Primary tables: `21FA0`, `22C4C`, `21CE8/21CEC/21CF4`, `2188C/21890/21898`.
Several real adapter/interrupt entries are absent as functions in the canonical
corpus, so their instruction bytes were read instead of treating a missing
function as proof that no code exists.

## 3. Cold startup clears flash-error status before boot selection

There is a relevant ordering edge before the already-known `119E` gate:

```text
1404 -> 802:  FFC62004 = 0F; FFC62008 = 1
     -> remaining cold startup
     -> 13B0 -> 119E -> 115A: read FFC62030, test bits 0 and 2
```

The manufacturer identifies `FFC62030` as **UCFDERSTR**, the CodeFlash
ECC-double-bit/address-parity status register, cleared through `FFC62008`.
It is not RESF, a failed-start counter, or a persistent application-crash flag
(manual p.2530, visually checked). The cold initializer clears that state
before the later validity check. A genuine new flash error can affect the
check; an erroneous but correctly stored branch is not evidence of one.

The three-attempt loops in `119E` retry validity checks during one invocation;
they are not a multi-boot crash counter. Backup words `FFC0A000/4/8/C` are used
as guarded error/reset records in the reviewed startup paths, not a recovered
network-controlled programming selector. Cold upper-RAM clearing must also
not be confused with retention across the application's live handoff.

Primary firmware: `802`, raw `1404..1477`, `E54`, `F80`, `10C6`, `115A`, `119E`,
`13B0`, `62BAE`. No electrical fault or deliberate integrity failure is proposed
as a recovery procedure.

## 4. XCP's fixed gate is decisive independently of scheduling

`8312E -> 830D0` copies a bounded frame to `FEBE4C34`. Subject to transport state,
`82FEC` directly calls the fixed pointer at `22B14`, which is `821D6`.
`821D6 -> 830C0 -> 98E80` reads CodeFlash byte `30D68=5A`, returns nonzero, and
prevents protocol command processing. That byte and the reviewed gate code are
unchanged in the incident reconstruction.

The callback relationship should not be replaced by a blanket assumption that
all XCP interpretation waits for DCM. Conversely, even granting that the
callback runs, reaching staging does not enable CONNECT/DOWNLOAD. This pass
does not claim a particular incident frame reached the parser before the
fault. The custom resident is not an independent listener: the malformed call
does not reach its intended entry.

## 5. Recovery boundary

The documented Renesas ROM programming mode is selected by hardware mode pins
at pin-reset release and uses UART/CSI, not a documented CAN-ROM listener
(manual pp.261–263 and 2867). The lockstep master/checker pair is not a second
independent application CPU with its own diagnostic service (p.2684). This
does not rule out another processor or connection elsewhere in the assembly.

Current local `tools/gts route P5-Unified --json` reports `PrepareRetryFlag=0`
for both `P5-Unified` and `P5-Unified10`, with no configured repro-gateway-mode
writer in those rows. This is a configuration observation, not an exhaustive
current-DLL or assembly-level proof.

A subsequent read-only check of the shipped current
`software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/CUWPlus/TCUWCanUnifiedPrepareWriter.dll`
found a single export, `StartPrepareWrite`, and no `PrepareRetry` export. Use
that absolute DLL path with `tools/gts pe`; the default CUWPlus evidence root
in this checkout locates route INIs but did not resolve this DLL by basename.
This confirms the export surface only, not every internal function or any
undocumented manufacturer recovery mechanism. The exact F33 binary was also
rechecked at `13B0/119E`, `7A254/667E6`, `65F5E`, and `98E80`; those checks do
not establish an additional recovery entry. No vehicle access occurred.

An actual recovery lead must provide legitimate recovery execution independent
of returning from the corrupted foreground call. The exact live fault state,
unacquired ROM/extended-region contents, and complete assembly-level wiring
remain unknown. They are neither demonstrated recovery routes nor evidence
for an absolute impossibility claim. Known inverse bytes alone do not supply
an accessible way to perform the repair. No new vehicle job was left running.

## 6. Network-only route closure after exact-target recheck

The exact F33 cold-start selector was rechecked with
`tools/gtarget camry-8965F3307000`: `13B0` calls `119E`, and a valid image goes
directly through the fixed application-entry pointer at `FFDB8` to `20880`.
Only a failed validity check reaches `1398`. The only recovered application
handoff into that boot runtime remains `65F5E -> 9F00 -> 148E -> 1398`, and the
normal DCM/system-mode workers which reach it execute after the malformed call.
No boot-request polling window precedes the valid-image jump.

Enabling EI interrupts inside an interrupt or exception path does not create an
unbounded CAN-controlled stack pivot. Renesas Hardware Rev.1.20 pp.209-212
states that an acknowledged EIINT priority is recorded in `ISPR`; while its bit
is set, interrupts at the same and every lower priority are masked. The same CAN
receive source therefore cannot recursively nest. Higher-priority nesting is
finite, and the target-native saved-PC/callback/DMAC census found no tester-
controlled return-PC or indirect-call cell. This closes the proposed CAN-flood
nested-return route within the recovered hardware/software model; it is not a
general proof against every undiscovered implementation flaw.

The physical-route ambiguity is also narrower than “camera side versus Bus 4.”
On the installed repinned Toyota-B harness, Panda bus 0 is the car/chassis side
of the relay-intercepted **Toyota Bus 4** pair and Panda bus 2 is its camera-
connector side. The retained identity check
`targets/camry-2026/raw-20260911/eps-recovery/nrtd-identity-check-20260911T054713Z.json`
records `0x7A1 -> 0x7A9` timeouts on both bus 0 and bus 2. Another Panda logical
bus selection is therefore not an untried route around the central gateway.
The earlier inference that “via EBU” implied a second EBU-private CAN segment
was disproved: exact F33 has one CAN controller, and the successful repinned
diagnostic path reaches the same Bus-4 segment represented on both sides of the
camera relay. A supposed downstream EBU tap is therefore not a supported
software or wiring recovery route.

Current CUW recovery APIs restore host-side retry/CID state and then invoke the
ordinary writer. They do not provide a target-independent CAN recovery listener.
Together with the fixed XCP gate (`30D68 = 5A`) and the target-native negative
control-transfer census in
`data/generated/camry_8965F3307000_application_ram_loader_assessment.json`, no
stock camera-side CAN command is presently recovered that can rewrite `7A272`
while execution is trapped there. A software/network answer would require new
evidence of an independent manufacturer recovery executor or a concrete
pre-fault control-transfer vulnerability; neither is present in the acquired
firmware and tooling.

## 7. Reusing the intact resident signer

The stage-7 incident image changes only the hook after stage 6. The two resident
spans are byte-identical between the stage-6 and incident reconstructions:

| Resident span | Length | SHA-256 |
|---|---:|---|
| `FFE04..FFEF3` | 240 | `723eb074c632ce0397a798f8c4c9ff305eacb6a264860ec050cf5ccabeb308c4` |
| `FFF04..FFFFD` | 250 | `5725dabdcbd7c27f3ceaa5dea20295d56f420a8469e3312c56f8c2aef68ad0cd` |

Raw marker bytes `FFE00=5A A5 A5 5A` and `FFF00=01 00 00 00` remain around the
spans. The resident entry at `FFE04` initializes its fixed private state,
invokes the signer body, invokes displaced stock call `7BF60`, and returns. The body reads
fixed native B6/C7/freshness locations, constructs the fixed 36-byte command-5
domain, calls the fixed ICU-S/freshness helpers, and conditionally replaces the
fixed B6 queue fields. Its copies have constant lengths 28 and 7. It contains no
FACI erase/program sequence, arbitrary-address write, transport parser, loader,
or request-derived return/callback target. Executing it is therefore not itself
a flash repair primitive.

The stock exact-target image has no recovered reference into either resident
span. An exhaustive current control-transfer assessment reports 496 decoded
indirect transfers (487 in the application); all directly referenced RAM call
cells are below the former XCP window, and the residual computed calls resolve
to fixed, guarded CodeFlash callbacks. The image contains no decoded SYSCALL or
TRAP instruction, no SCCFG/SCBP writer, and only fixed EBASE/INTBP setup. Thus no
recovered diagnostic, callback, saved-PC, syscall-vector, DMA, or scheduler path
can be retargeted to `FFE04` by a tester before the bad call.

The hook guard does not create a network-controlled clean pass. `7A254` reads
`FEBE3DF2` and enters the bad sequence only when it equals `FE01`; the complete
direct-reference set contains two initialization writes in `7A132` (`FD02`,
then terminal `FE01`) and reads in `7A232/7A254`. `667E6` calls `7A254`
unconditionally before DCM worker `988C2` and mode/handoff worker `58B5E`.
Ordinary CAN receive can queue a request before the fault, but no recovered
request path writes this guard or services the queued request before the hook.

The application fixes `EBASE=20000` at `715C8`. Its raw `+10` vector decodes as
`syncp; jmp 62E1E; feret`; `62E1E` saves EI state, enables EI, records context,
and loops forever. The raw `+90` vector decodes as
`syncp; jmp 65BD4; feret`, and only that separate handler advances `FEPC` by
four before FERET. The hardware SYSERR classification above therefore does not
provide a resumable skip of the malformed JARL or a path into the resident.

Result: the intact resident is a useful known executable landing pad **only if
a separate pre-fault PC-transfer primitive is first recovered**. It would then
still need to be paired with an independently callable flash erase/program
chain to restore `7A272`. Neither prerequisite is present in the recovered
network-reachable surface. This is a bounded static negative, not a claim that
no undocumented manufacturer executor or unrecovered vulnerability exists.

## 8. CUW `BlankECU` and recovery state are host modes, not alternate executors

The current CUWPlus managed/native boundary was inspected rather than treating
the names as protocol evidence. `CuwBackendService.dll` copies its
`IsBlankECUOnlyFlag` into the native CUW configuration member which
`ConfigureCUWDLL` stores at native address `1008C460`. The recovered native
uses are orchestration and package-validation decisions. In particular,
`10034490` bypasses a calibration/CID eligibility path when the flag is set; it
does not select another J2534 transport or emit a target-independent repair
request.

CUW packages separately carry `[KindOfCal] IsBlankECU`. The native calibration
file reader parses and validates that package property into the CPU descriptor.
All 26 locally acquired CUWs have `IsBlankECU=0`; there is no blank-target
package in the retained corpus from which a different wire contract could be
recovered. `JudgeFlashable` consumes the blank-only host flag, but the selected
writer remains the ordinary contact-type writer.

The exported `ReadRecoveryInfoFile`, `GetNumberOfReceivedCIDForRecovery`,
`GetReceivedCIDForRecovery`, and `JudgeKindOfVehicleForRecovery` names also do
not establish an ECU recovery listener. Managed IL shows that they restore
host-side interrupted-flash state: J2534 device identity, VIN, calibration
metadata, flags, and the previously collected CID list. The subsequent job
still enters the configured CID getter/prepare writer/flash writer. This
explains Toyota's “recovery” terminology without supplying execution in the
faulted F33.

For `P5-Unified`, `TCUWCanUnifiedCIDGetter.dll!StartGetCID` connects through
J2534 protocol 6, installs ordinary flow-control filters, waits the package's
wake delay, and queries each package node through its diagnostic address. Its
object vtable at `1000524C` contains the normal destructor/contact operation
plus periodic-message helpers. The main contact operation at `100019D0` builds
the request/response addresses from the node descriptor and performs ordinary
P5 UDS exchanges. It is not a functional-address discovery request capable of
extracting a CID from an otherwise silent processor.

The relevant acquired package `T-0051-26.cuw` selects node diagnostic ID
`0724`, gateway descriptor `07505F`, `P5-Unified`, and
`ChargeLocalBusEcuReprogrammingFlow=00`. Its current route selects the ordinary
unified CID/prepare/flash DLLs and `PrepareRetryFlag=0`. These are package facts,
not evidence that `0724` is the F33 EPS diagnostic address.

## 9. “Charge local bus” controls another ECU; it is not a byte proxy

The one remaining suggestive P5-Unified mechanism was traced to its exact wire
construction. `TCUWUnifiedUtils.dll!RoutineControlForChargeLocalBus` addresses
the package-declared **controlling ECU**, optionally installs an ISO-TP flow
filter, and sends UDS RoutineControl request `31 01 11 7E` to start or
`31 02 11 7E` to stop. It expects the corresponding `71` response. The Phase-6
variant constructs the same routine around its fixed Phase-6 target address.
The CID getter uses this only for package flow values `01`/`02`, surrounding a
normal diagnostic contact with a power-on delay; it does not forward arbitrary
diagnostic bytes to the target node and does not invoke code inside a silent
node.

No locally acquired CUW declares a nonzero charge-local-bus flow, and the
Camry package above explicitly declares `00`. Exact F33 static topology also
recovers one CAN controller rather than a separate software-addressable EPS
local CAN. Consequently this facility is evidence of a controller-mediated
power/wake operation used by other package geometries, not presently a route
to call the resident at `FFE04` or rewrite `7A272`. Even if an external ECU
could power-cycle the F33, the valid incident image would make the same fixed
application jump and fault at the malformed call again.

The hook-reuse target is therefore precise: a new lead must either (a) transfer
the F33 PC to intact `FFE04` before `7A272`, or (b) independently enter a flash
executor able to repair the two hook bytes. Blank-only selection, interrupted-
job recovery, CID collection, and local-bus power control do neither. The
resident remains valuable because it removes the need to upload a signer after
such a transfer primitive is found; it does not by itself provide that
primitive.

## 10. The stock crypto oracle is ordered before the hook, but cannot be newly armed

The first outer foreground call before `7A254` is `69CA2`, which is the stock
ICU-S crypto-test state machine previously used as the command-5 oracle. This is
the strongest apparent resident-reuse lead because it is real target code with
CAN-derived inputs and it executes before the malformed instruction. Its exact
scheduling boundary nevertheless prevents a post-incident command from using
it.

Startup `666BC` calls `6914C`, `69064`, and then `7A132`. `6914C/69064` reset the
crypto-test modes and working state; `7A132` finishes communication
initialization by writing the `FE01` gate which admits `7A254`. In the foreground
aggregate, the order is fixed:

```text
667E6 -> 69CA2        crypto-test state machine, consuming prior collected state
      -> 7A254
           -> 79EDE   drain hardware/software CAN RX into normal COM
           -> 7A272   malformed resident call; FE/SYSERR before the suffix
      -> 988C2        DCM worker (unreached)
      -> 69E7C        crypto-test input/result maintenance (unreached)
      -> 58B5E        system-mode/programming worker (unreached)
```

The stock bank is not armed by CAN `01B..01F` alone. Its activation is the DCM
RoutineControl path for RID `100F`, and the DCM worker is after the malformed
call. The CAN RX drain can accept the control/input frames during the doomed
first iteration, but `69CA2` has already run, while the later crypto maintenance
and next `69CA2` invocation are never reached. Repeated resets do not accumulate
an armed state because the startup functions clear it each time.

This also bounds an exploit interpretation of the prior oracle: its CAN key
selector and message bytes feed fixed crypto buffers and guarded ICU-S command
dispatch only after diagnostic activation. The reviewed target-native indirect
transfer census found no unguarded selector-derived PC at this boundary. Thus
the oracle demonstrates that useful code exists before the hook, but it is not
a network-armable one-shot call or PC-transfer primitive in the incident boot
lifecycle.

## 11. P5 gateway preparation is not target-side execution

The current CP-unprotected GTS+ DLLs under `build/out/cuwplus-unprotected/` were
checked rather than relying only on the route INI. P5 Unified writer
`TCUWCanUnifiedPrepareWriter.dll` imports `JudgeReproGWNode`,
`GetCentralGWReqCanID`, `ChangeModeForCentralGW`, and
`RoutineControlForP5CentralGW`. `TCUWUnifiedUtils.dll` implements the gateway
mode request over extended IDs `0x750/0x758`, node byte `0x5F`, with request
`10 60` and expected response `50 60`. Its P5 gateway routines use these
request/response pairs:

| Routine type | Request | Expected response |
|---:|---|---|
| 0 | `31 01 10 11` | `71 01 10 11` |
| 1 | `31 03 10 11` | `71 03 10 11` |
| 2 | `31 01 10 12` | `71 01 10 12` |
| 3 | `31 03 10 12` | `71 03 10 12` |

This corrects the narrower earlier observation based on route metadata: current
GTS+ does contain P5 central-gateway preparation behavior. The writer then
continues with ordinary physical target UDS, including `10 02`, an 18-byte
SecurityAccess exchange (`27 01 || tester-data16`, then `27 02 || key16`), and
the target programming sequence. No gateway-side payload execution, proxy
FACI writer, or response synthesis for an absent target was recovered.

The available current Camry CUW descriptor used to exercise this DLL is for a
different ECU and must not be projected onto the EPS. The meaningful bounded
result is in the generic DLL flow: central-gateway preparation opens the route
and controls network conditions, but the selected ECU still has to answer and
run its own programming services. It therefore does not supply the missing
independent executor for a faulted F33 application.

## 12. Malformed CAN/CAN-FD before the fault does not expose an overflow landing

Because `79EDE` can drain a frame before the malformed call, the exact-target
receive path was rechecked specifically as a possible PC-transfer primitive,
including CAN-FD lengths rather than only ordinary eight-byte frames. The lower
record carries a four-bit DLC. Its decoded payload length is bounded to the
CAN-FD maximum of 64 bytes; `7FD46` additionally clamps the local FD copy to
`0x40` before copying into its 64-byte staging buffer. Route/controller indices
are checked against fixed table counts before callback lookup.

At the next boundary, `7FEF8/7FF52` decomposes the encoded controller/route ID,
rejects an unknown controller class (`0xFF`), checks the route index against the
per-controller count at `21A48`, and only then derives the fixed descriptor and
callback. The queue writer in `7FD46` checks the configured cursor/capacity
relations before copying the payload. The normal COM path subsequently bounds
delivery by the configured PDU length. The ISO-TP route separately caps DCM
reassembly and checks copy capacity.

No wire-derived destination pointer, callback pointer, length above 64, or
unchecked route index was recovered in this pre-hook chain. Oversize FD DLCs
can produce configured-length truncation or ignored suffixes, but not a write
past the reviewed workspaces. Thus flooding, unknown CAN IDs, short classic
frames, and 12/16/20/24/32/48/64-byte FD shapes do not currently provide a
write into the saved FE context, a callback cell, or a resident entry address.
This is a bounded negative for the exact reviewed receive and ISO-TP paths, not
a proof against every undiscovered peripheral defect.

## 13. The malformed JARL has a clean epilogue re-encoding, but no flash shortcut

The malformed six-byte stream was also treated as an encoding problem rather
than only as a fixed bad destination. It is `FF 02 || 92 5B 24 36`, where the
last four bytes are the signed JARL32 displacement. The displacement has 14 set
bits, so there are exactly 16,384 values obtainable by clearing a subset of
those bits while leaving the `FF 02` JARL32 prefix intact. None lands in either
intact resident span at `FFE04..FFEF3` or `FFF04..FFFFD`.

One encoding does have exact stack-compatible behavior:

```text
current     FF 02 92 5B 24 36  -> JARL32 362BFE04, LP
candidate   FF 02 12 01 00 00  -> JARL32 0007A384, LP
cleared             80 5A 24 36
```

`7A254` enters with `prepare {lp},0`. Target `7A384` is the independently used
`dispose 0,{lp},lp` epilogue of the neighboring one-LP wrapper `7A376`. A call
there would restore the original saved LP from `7A254`'s frame and return to
the outer foreground aggregate, skipping the poisoned suffix cleanly. That
would let later DCM and system-mode work run; it is better behavior than simply
branching to an arbitrary interior instruction.

This encoding relation is **not an in-place repair procedure**. P1M-E Hardware
Rev.1.20 §35.12 explicitly prohibits additional writing to an already
programmed flash area and requires erasure before overwriting it. CodeFlash is
programmed in 256-byte units and the containing erase block must be preserved
and rebuilt. An executor capable of that erase/RMW can already restore the
known stock call or install the correct resident call directly, so the
clear-bits encoding does not remove the missing-executor requirement.

The deterministic byte/subset result is generated by
`analyze_f33_recovery_structure.py` and protected by the
`f33_recovery_structure` verification suite. It closes a tempting low-level
shortcut while retaining `FFE04` as a valid landing pad if a genuine pre-fault
PC-transfer primitive is later recovered.
