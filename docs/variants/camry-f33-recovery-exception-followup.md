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
fetch from other than CodeFlash.  The product manual's broad SYSERR wording is
not the final architectural classification for this subcase: matching
RH850G3M Software Rev.1.40 Table 4-1 classifies **instruction-fetch SYSERR as a
resumable FE exception**.  Exact F33 nevertheless makes it operationally
terminal because its selected SYSERR handler never executes `FERET`.  These
facts make SYSERR `13H` the bounded architecture-predicted interpretation of
the malformed call; the missing live FEIC observation remains distinct from
that interpretation.

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
of returning from the corrupted foreground call. The exact live FE exception-register values,
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

The incident fault model now closes the proposed CAN-flood nested-return route
more strongly than the earlier ISPR-only argument.  Whole-image raw system-
register scanning proves cold startup sets `PSW.EBV=1`, application startup sets
`EBASE=0x20000`, and the predicted SYSERR therefore vectors through `0x20010 ->
0x62E1E`.  Fetch-SYSERR sets `PSW.NP=1`; the `EI` inside `62E1E` clears ID but
not NP, while ordinary EIINT acknowledgement requires `ID=0 && NP=0`.  CAN RX/TX
and periodic maskable EIINTs therefore cannot execute at all after the predicted
incident fault.  ISPR still bounds recursion for ordinary EI-level handlers, but
it is no longer the decisive post-incident argument.

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

Whole-image raw scanning additionally proves the vector selection that was only
partly recovered in the first pass.  Hidden reset core-init writes
`PSW=0x00018020` at `0x204`, setting `EBV=1`; application startup then fixes
`EBASE=0x20000` at `0x715C8`.  The raw `+0x10` SYSERR vector is exactly
`syncp; jmp 0x62E1E`.  The jump is terminal: `62E1E` saves an EI-shaped RAM
frame, executes `EI`, calls `712CE`, and self-loops at `62E42`; there is **no
FERET after that jump**.  The raw `+0x90` vector instead jumps to the separate
`65BD4` handler which advances `FEPC` and executes `FERET`.  Matching G3M
architecture calls fetch-SYSERR resumable/precise, but Toyota's selected
`+0x10` handler deliberately does not return, so it provides neither a skip of
the malformed JARL nor a path into the resident.

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
writer remains the ordinary contact-type writer. Current CP-recovered
`CuwBackendService.dll` independently confirms the managed/native boundary:
`ConfigureCuwDll` copies `IsBlankECUOnlyFlag` into
`TypConfiguration.mblnTargetIsBlankECUOnlyFlag` and then calls the same native
`ConfigureCUWDLL`; managed `StartReprogramming` has no blank-specific branch
and directly calls the same native `StartReprogramming` entrypoint.

This is consistent with Toyota's first-class "Blank ECU Calibration Download"
workflow without making it a dead-target rescue primitive. The current
ReproStd P5 prepare writer still requires a direct target `10 02 -> 50 02`
before target SecurityAccess. A factory/replacement blank ECU can satisfy that
contract if its own validity state leaves its boot diagnostic listener active;
the incident F33 cannot, because `119E` accepts the CRC-valid bad image and
jumps to the application before boot CAN is initialized. The host blank flag
therefore does not make a silent, validity-passing target equivalent to a
factory blank target.

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

The current CP-unprotected GTS+ DLLs were checked rather than relying only on
the route INI. The tracked static analysis copies are under
`software/Techstream/gtsplus/cuwplus/CUWPlus/unpack/`; the current protected
`TCUWUnifiedUtils.dll`/`TCUWDHUtils.dll` bodies independently recover to the
same executable surface with `recover_cp_bodies.py`. P5 Unified writer
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
GTS+ does contain P5 central-gateway preparation behavior. The current ReproStd
prepare writer makes the target dependency explicit in its vtable at
`0x10005260`: virtual `+0x04 -> 0x10001990` builds direct target Diagnostic
Session Control `10 03` with expected `50 03`; virtual `+0x10 -> 0x10002D20`
builds direct target Programming Session `10 02` with expected `50 02`; and
virtual `+0x14 -> 0x100014D0` performs target SecurityAccess `27 01/02`. The
state machine performs the central-gateway `0x1011` preparation and then still
calls the target `10 02` method before target SecurityAccess. The post-transition
gateway `0x1012` work likewise surrounds rather than replaces the target UDS
exchange. No gateway-side payload execution, proxy FACI writer, or response
synthesis for an absent target was recovered.

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

## 14. J2534 pin-15 programming-voltage control is not selected by P5 EPS

The current CUW host stack does contain a target-independent physical J2534
control which initially looked recovery-relevant. `TCUWJ2534DeviceIF.dll`
exports `CJ2534IF::SetProgrammingVoltage(pin, voltage)`, and current
`CUW.unpack.dll` contains exactly two calls to it:

- helper `0x1003BCB0` passes pin `15`, value `0xFFFFFFFE`
  (`SHORT_TO_GROUND` in J2534 terminology);
- helper `0x1003BD30` passes pin `15`, value `0xFFFFFFFF`
  (`VOLTAGE_OFF`, releasing the programmed pin state).

The assert helper has a direct caller in `CUW.dll!ProcessBeforeReprogramming`
at `0x10064533`. It is not unconditional. `ProcessBeforeReprogramming` calls
`TCUWParameterForVC!CParameter::GetParameterboolWithKeys(...)` for
`FlagToChangeWFSE` and invokes the pin-15 helper only when the returned Boolean
is true. The paired later path uses the same parameter result before releasing
pin 15.

The decoded current `Ini/Parameter.ini` removes the apparent P5 recovery lead.
Its `P5-Unified` row is exactly `FlagToChangeWFSE=0`. The retained EPS control
packages `T-0035-22.cuw` and `T-0036-22.cuw` both select
`ContactType=P5-Unified` / diagnostic ID `0x7A1`. More broadly, every decoded
P5/CAN system row has `FlagToChangeWFSE=0`; the only 21 rows with value `1` are
SIL-family rows (`0SIL*`, `1SIL*`, `30SIL92`). Thus Toyota's host can drive an
independent DLC-pin-15 short-to-ground primitive, but that mechanism is not
selected by the P5 CAN/Unified EPS programming family and cannot be promoted to
an F33 hardware boot-mode control.

This is a host-route negative, not an electrical claim about every Toyota VCI
or DLC implementation. A future F33-specific package selecting a different
system/protocol row would need to be evaluated on its own. The current P5 EPS
package evidence, however, does not exercise this physical pin-control path.


## 15. Network-only recheck: the frozen RAM writer is not a recovery server

2026-09-12. This follow-up stayed with existing vehicle-network services and
performed no connector work, ECU requests, ECU resets, RAM upload, or flash
write. It rechecked the actual retained incident reconstruction and the exact
RAM writer rather than assuming that current corrected package files describe
the code used during the incident.

### 15.1 The reviewed stock recovery code really is unchanged in the incident

The surviving old image is
`build/out/f33-persistent-b6-signer-tail/CodeFlash.stage7-persistent-signer.bin`,
SHA-256 `aba6867f244dda42b754d6f455f25a226ee95025dee6a2d98b07b3ac550f2d74`.
Its stage-6 predecessor hashes to
`818338cc3e3dc23f1cf466c72f497699adc9ff33767e67b81fb65bccfab09010`.
The complete byte comparison finds exactly **eight** stage-6-to-incident byte
changes: the four-byte call site at `7A272..7A275` and four-byte CRC fixup at
`FFDEC..FFDEF`. This remains reconstructed write evidence, not live readback.

The earlier stock-to-incident unchanged-range comparison in the opening
image-state check was repeated successfully. Whole-image raw PSW, EBASE, RBASE
and ASID writer censuses are also unchanged; the added flash-tail resident does
not introduce a new writer to those registers. Thus using the exact stock
startup/diagnostic code for those specific unchanged regions is justified.

An independent `v850-elf-objdump -m v850e3v5` decode of the incident image
confirms the malformed destination. A raw direct-transfer census finds only
`65F82 -> 9F00` as an application-to-low-boot transfer inside a recovered
function. Seven other apparent low-target branches lie outside the recovered
functions in configuration/table regions and are not established code paths.
The survey does not prove absence of every unrecognized computed transfer.
The direct calls into `988C2` and `58B5E` remain at `667F2` and `667FA`, after
the corrupted aggregate. Fresh Ghidra decompilation of the supported boot
selection and handoff functions agrees with that ordering.

### 15.2 The alternative MPU exception does not supply a normal return path

The `20090 -> 65BD4` handler is real: raw instructions save `FEPC+4`, perform
its bounded protection bookkeeping, restore the FE context, and execute
`FERET`. It must not be confused with the terminal SYSERR handler. The question
was whether the incident's invalid fetch could enter this returning path instead.

Exact MPU setup does not support that explanation. `71398` restores attribute
profile **0** before `667E6`; region 0 has minimum `00000000` and effective
inclusive maximum `FEBDFFFF`. Its `MPAT0=B8` in both profiles enables supervisor
execution, read and write. The attributes require ASID 0, and the only raw ASID
writer in either stock or reconstructed incident is `LDSR r0,ASID` at `27A`.
MPM initialization at `65954` sets `MPE=1` and `SVP=1`. The incident destination
`362BFE04` is therefore inside an enabled supervisor-executable MPU region,
while still physically access-prohibited by the product memory map. The MPU
permission does not make that physical address valid, and it does not turn the
predicted fetch SYSERR into the returning protection exception.

Manufacturer evidence is **R01UH0585EJ0120**, CPU register table for ASID,
Table 3.39 (p.215), Tables 3.47/3.48 (p.219), and Table 3.49 (p.220). The MPAT
page was rendered and visually checked. The existing
`camry_8965f3307000_incident_fault_model` test passes. Live FE registers remain
unobserved; this result strengthens the existing model, not a claim of live
exception capture.

### 15.3 A still-running post-write payload would also be diagnostically silent

It was necessary to distinguish a crashed application from a RAM writer that
never returned: ignition transitions alone do not identify which code currently
runs. The frozen configured stage-7 writer is 4,048 bytes, SHA-256
`fe2c46b16096260fa6d438a43d0fc662f444648815058fbe60ee7ea0d12c893a`, retained as
`stage7-apply-payload.bin.shellcode.bin` alongside its metadata in the same old
package directory. Its code before the config slot equals the retained template
(`3d6c4e685ad8e6460a624e501948324e989a751a94cfd69f12078ab158e40426`).
These archived binaries, not a rebuilt/corrected package, were independently
decoded at their recorded load VMA `FEBF0000`.

The target lifecycle is explicit:

- `FEBF0004` executes `DI` before preflight or writing.
- The apply success path emits `SUCCESS` and then enters the same terminal
  helper as preflight/error completion.
- `FEBF00F2` loads stage `FF`, calls the telemetry transmitter, and reaches
  `FEBF00FE: BR FEBF00FE` after emitting `DONE`.
- That terminal path has no CAN receive polling, input parser, acknowledgment
  request, bootloader call, `EI`, `EIRET`, or `FERET`. The only waits in the
  telemetry sender concern its transmit-buffer status, not tester commands.

This agrees with `exploit/patcher/main.c` and
`exploit/common/runtime.c::runtime_halt`, but the frozen bytes are the evidence
for this incident. `DONE` reports completion; it does **not** mean the boot UDS
server has resumed. Therefore leaving the writer powered cannot expose a
network continuation or abort command that this payload does not implement.
A genuine reset would leave this RAM execution state, but the already-recorded
CRC-valid malformed application remains the separate cold-start problem.

### 15.4 Remaining live evidence limitation

A read-only attempt to reach the configured comma SSH endpoint timed out before
any remote command ran. The existing overlay-network record for a comma-named
peer was also offline and stale, so it was not treated as a substitute target.
Consequently this pass could not inspect the on-device incident transcript or
observe a new target response. No fresh transmission to the vehicle was made.

The archive to inspect when the device is reachable is
`/data/camry-f33-car-kit-incident-bad-hook-20260911` and its associated run/state
records. The immediate purpose is to recover the actual write/return/reset
sequence, not to execute its withdrawn scripts. A target-native diagnostic
response through an existing network route would override the present silent-
executor model and must be identified as application or boot before recovery
is considered. No such new response or working network-only repair was
established by this offline pass.


## 16. Network-only recheck: current Unified writer and pre-foreground work

2026-09-12. This pass addresses recovery over the vehicle network, not hidden
connector contacts, rack removal, or direct programming. It performed no
vehicle connection, transmission, session change, reset, RAM upload or flash
operation. No working network repair was established.

### The selected Unified writer itself requires the target response

The earlier ReproStd trace must not stand in for every P5 contact type.
`tools/gts route P5-Unified --json` selects
`TCUWCanUnifiedPrepareWriter.dll` for the ordinary P5-Unified row. The current
protected input, its `._` sidecar, and the previously recovered native body
were freshly matched against the recovery manifest. The ordinary imported
P5 exchange helper was independently bound to its current protected inputs
in the same way. These are observations of the current host implementation,
not an exact-F33 CUW package acquisition or a vehicle run.

Native instructions establish the following dependency without relying on
RetDec's incomplete reconstruction of local packet stores:

| Current native location | Recovered behavior |
|---|---|
| Unified writer `10002B50 -> 10001C00` | Exported `StartPrepareWrite` constructs the writer and enters its preparation state machine. |
| Unified writer `10002363 -> 10002550` | Calls the target programming-session exchange after gateway/periodic-message preparation. |
| Unified writer `100025C4`, `100025EA` | Stores little-endian words `0210` and `0250`, constructing request `10 02` and expected response prefix `50 02`. |
| Unified writer `10002654` | Calls `SendRequMsgAndReceiveRespMsgForP5Can` with that non-null expected response. |
| `TCUWCanDiagCommUtils!100019D0` | Writes the request, receives the specified CAN response (`10001BC1`), enforces the minimum size (`10001D23`), and compares the expected bytes (`10001D3A..10001DA4`). |
| Same exchange helper `10001F9A`, `10001FC4`, `10001FFD..10002046` | Short/mismatched responses and receive exceptions take error/throw paths, not a synthesized successful programming reply. |

The helper separately recognizes response-pending `7F <service> 78`; pending
is still a response from a running target, not permission to program an absent
one. In the Unified writer, the ordinary error handler translates target
`7F 10 22` into its preparation error; it does not supply another target-side
executor. The ordinary main preparation path calls `10002550` regardless of
which side of its emissions-related delay branch was taken. Object member
`+2C` comes from `GetEmissionsRelatedSystem` in the constructor; it is not
identified here as a blank-ECU recovery flag.

Thus the **actual current Unified flow**, not only the related ReproStd flow,
still needs the selected ECU to run programming-session service. Its network
preparation can affect delivery, but does not itself repair the missing
execution dependency in the reconstructed F33 incident. This does not prove
that every unacquired target package or supplier recovery implementation uses
this flow.

Reproduction inputs are the current `TCUWCanUnifiedPrepareWriter.dll` and
`TCUWCanDiagCommUtils.dll` plus their `._` files under the installed CUWPlus
tree. `tools/gts recover-cuw-bodies --only <filename>` recovers their analysis
bodies. For this pass the existing manifests matched all current inputs and
outputs: Unified recovered SHA-256
`797b15b8ae8049717c1f5ec2692b923dcea9abb52bd2add6415cf295281db1dc`;
P5 exchange-library recovered SHA-256
`dbdc60dfb92b88d572c5eb70278fb430f459242029a3b752a6598abdb6823fcb`.
The disposable raw disassemblies are under
`build/work/f33-network-recovery-20260912/`; that directory is not evidence
required by the committed tests.

### Earlier foreground work does exist, but is not another recovered UDS server

Fresh exact-target decompilation of `637EE`, `66062`, `65442`, `66FF2`, and
`68318` checks the work before the familiar `667E6` aggregate. The outer loop
waits for its scheduler flag, performs supervision and the
`66FF2 -> 68318 -> 79C60 -> 74164` worker, and then calls `667E6` without a
network-mode branch around that call.

`74164` operates on the internal job state rooted at `FEBF6102/6104`, rather
than directly interpreting UDS input. Its worker `72EEA` polls the current job;
`723D6 -> 73A5C` resolves its state key through the fixed ROM map at `27400`,
and `72342` dispatches the configured job operation. The mode helper `73EEE`
selects fixed internal callbacks `766F4`/`767EA`. None of the reviewed
entry/dispatch functions is the normal DCM worker or an independently identified
network programming listener. This is a specific preamble/dispatcher result,
not a new claim that every computed descendant has been exhaustively proven.

The startup and preamble observations were also checked against the **complete
cumulative incident reconstruction**, not only stock plus an imagined hook.
Its SHA-256 is the retained `aba6867f...50f2d74`; it differs from stock in 492
bytes across 22 contiguous intervals. The reviewed low boot (`00000..0FFFF`),
network tables (`21000..2BFFF`), startup/scheduler/vectors (`60000..71FFF`),
additional preamble/job-driver span (`72100..7A12F`), and diagnostic workers
(`90000..98E7F`) are byte-identical. Earlier modifications therefore do not
invalidate these particular stock-code traces. The reconstruction remains
**not a new live readback**.

### OEM labels and peer observations are not recovery commands

The suggestive GTS+ text about putting an ECU into reprogramming mode before
an ignition cycle is `U_English.ddb` text entry **4035**. The original BSM
attribution here was wrong: the resource table was joined by row ordinal instead
of its explicit text index. Current `UtilityDB.dll` consumes resource-record
`+0xA0` as that index; the corrected identifier is **`IDS_CCU_01_011_TEXT1`**,
part of the **Cable Check Utility**. Its neighboring pages test the engine's
SIL/L-line rather than describe an EPS recovery flow. Current
`UtilityExNK2.dll!Ex2CCU_01_SetProgrammingVoltage @ 10021E50` calls the physical
programming-voltage helper for DLC pin 15; the paired release is `10021D90`.
This is not a CAN request. The generic M_English labels “ECU Reprogramming” and
“ECU Reprogramming (Part#:89650-*****)” likewise do not, by themselves, identify
an independently running F33 programming service. See the corrected resource
layout in `docs/tooling/techstream.md` §6.2.1; source conclusions must not retain
the former BSM interpretation.

There is a concrete **read-only peer-side observer**, distinct from a repair:
current `Brk_Bst_P5.ddb` category **466** defines
`EPS/Steering Control Actuator ECU Communication Open` at primary DID **102F**,
bit **74**, with labels `0=Normal`, `1=Under intermittent`. This can be resolved
with `tools/gts search 'Communication' --kind did --ecu Brk_Bst_P5 --json`.
It is a status definition, not a writable communications-enable control, an
EPS acknowledgement counter, or proof of present EPS execution. Runtime
support and actual values were not measured in this pass. The sibling EPS
pinion-angle and zero-point labels are likewise observers, not programming
routes. Do not project P6 ADCU CAN-status labels onto this P5 brake module.

**Result:** the current normal host route still requires the target service
that the incident model leaves unexecuted. A network repair needs evidence of
an independently running recovery service, or a contrary target response that
invalidates that execution model. No such entry or response was obtained here.
Neither a new name in the diagnostic catalog nor another retry is a demonstrated
repair. The exact live fault registers and an exact-F33 recovery package remain
unobserved; the conclusion is not an absolute proof against every undocumented
implementation.


## 17. Network executor recheck: inline XCP and fixed-call alternatives

2026-09-12. This pass stayed entirely with the existing vehicle-network entry
paths and offline artifacts. It made no vehicle connection or request and did
not depend on a peer-ECU fault status, comma SSH, or a physical connector test.
No working recovery entry was found.

The XCP receive path was independently rechecked from exact-target Ghidra
instructions and the archived incident image. This **confirms the distinction
already recorded in section 4**; it is not a newly discovered listener. Any
broader statement that all XCP input merely waits for later foreground service
is inaccurate:

```text
8312E -> 830D0 -> 82FEC
                   -> [22B14 = 821D6], subject to interface-ready state
                   -> 830C0 -> 98E80
```

`830D0` copies a length-bounded frame and then calls `82FEC`; the latter can
invoke `821D6` synchronously. The interface-ready byte at `FEBE4EE6 + channel`
is separate: `82C9E` initializes it to `69`, and `82F18` writes `5A` only for
its enabled state. Granting that state does not open the command gate.

At `98E84..98E8E`, exact instructions load the **absolute CodeFlash byte at
30D68** and branch to `98EE6` when it is nonzero. At `98EE6..98EED`, the
function returns `1`. The dispatcher checks that result at `821E8..821EA` and
returns before its CONNECT case or normal command dispatch. Both stock and the
complete retained incident reconstruction contain `30D68 = 5A`. This is not a
session's RAM lock bit or an XCP seed/key negotiation that a different request
can satisfy; the rejection precedes those normal command handlers.

The full recovered function bodies of `79EDE`, `7A132`, `821D6`, `82C9E`,
`82F18`, `82FEC`, `830D0`, `830C0`, and `98E80` are byte-identical in stock
and the retained incident reconstruction `aba6867f...50f2d74`. The protocol
pointer block `22B00..22B1F` is also identical. `7A254` differs only in the
four recorded hook bytes in that comparison. The archived image remains a
reconstruction, not a live EPS readback.

A complementary check examined whether fixed CALLT/software-exception
instructions supplied a normal call path missed by ordinary direct-call
references. Linear disassembly of the archived image contains 490 CALLT-like
patterns and 30 FETRAP-like patterns, but **none is inside the body ranges of
the 6,065-function exact-target corpus**. It contains no CTRET, SYSCALL or TRAP
instruction in those ranges either. The observed patterns outside known code
must not be promoted from table bytes into executable recovery paths. This
result is bounded by the recovered code inventory; it does not claim that no
unrecognized executable region or computed call exists.

The earlier bootstrap result was also freshly checked through `481A`, `6C5A`,
`119E`, `13B0`, and `1398`: the normal CRC/descriptor/marker checks precede
the choice to initialize the boot diagnostic runtime. The reviewed alternative
XCP entry does not change that decision or provide a running repair handler
in the reconstructed incident state. These are target-execution results,
not conclusions drawn from an error message or from an unreachable host.


## 18. Network gateway preparation: an untested precondition, not an independent EPS programmer

2026-09-12. This pass follows only the existing diagnostic network. It does
not require lifting the car, a new physical connection, rack access, or another
ECU's DTC as its recovery mechanism. No vehicle request, reset, memory upload,
or flash write was performed.

### Correction to the earlier negative conclusion

The required final EPS `10 02 -> 50 02` exchange proves that the programming
executor must run on the EPS. It does **not** prove that completing the OEM
gateway preparation cannot restore access to an already-running EPS diagnostic
service which is hidden by routing state. Those are different questions.
The exact incident model still predicts no working EPS diagnostic worker after
the malformed call; gateway preparation is not a way around that instruction.
Its remaining relevance is the unproven distinction between a hidden surviving
listener and the reconstructed CPU-fault state.

The 39 retained post-incident segments were reread for the actual OEM gateway
traffic, with TX echoes/mirrors kept distinct from native reception. Among 184
selected diagnostic records (not unique wire transmissions), all 36 shared
`750/758` records decode to address extensions **0F or 6D**. There are no
`750/758` extension-**5F** records, and therefore no recorded gateway-preparation
exchange on that route. The same partially corrupted segment as in the liveness
census remains explicitly marked. These sparse captured spans do not establish
what was attempted outside them or inside the earlier unrecorded catcher.

Observation and producer identities:
`targets/camry-2026/raw-20260912/eps-recovery/gateway-preparation-observation.json`.
The sibling `reproduce_gateway_observation.py` is an offline-only historical
extractor against the same retained input paths; it never opens a vehicle
connection and writes only an ignored workspace report.

### The target identity read is optional before the gateway transition

Current `TCUWCanUnifiedPrepareWriter.dll!100026E0` wraps the direct target
`ReadSoftwareID` call at `10002778`. `TCUWUnifiedUtils.dll!100047F0` constructs
**F181**, not a programming-session request. The wrapper's exception metadata
is decisive: FuncInfo `10004B1C` has one try block over state2 and one
catch-all handler (`adjectives=40`, null type descriptor) at `100027AE`.
That handler's exact bytes `B8 7E 27 00 10 C3` select continuation `1000277E`,
the cleanup/return path. It does not rethrow or set a target-failed flag.

Consequently a failed **pre-transition identity read** does not, by itself,
stop this DLL before it performs the subsequent gateway transition. This is a
positive host-side control-flow result, not merely another timeout observation.
It corrects any interpretation that a responding EPS is required *before every
part* of OEM gateway preparation. The later EPS programming acknowledgement
at `10002363 -> 10002550` remains mandatory.

This is local to the prepare DLL. It does not prove that every GTS frontend,
Health Check, CID getter, or calibration-eligibility step will launch that DLL
for a silent target. The exact F33 calibration package and an end-to-end live
prepared-state transcript are still missing. Do not turn this local exception
handling result into a claim that the normal GUI has a verified dead-EPS mode.

### The gateway generation is selected, not guessed from the vehicle year

The current `CCanCommonPrepareWriter::JudgeReproGWNode` implementation is
`10001810 -> 10001820`. It uses the same `000007505F/000007585F` address pair
for its two protocol tests. The one-byte TesterPresent form selects internal
enum2; the two-byte UDS form selects enum1. They feed distinct authorization
and transition branches in the Unified writer. A guessed `10 60` must not be
presented as the universally correct Camry gateway preparation.

For the selected P5-style branch, the writer uses its ordinary gateway
SecurityAccess followed by the start/result pairs for routines **1011** and
**1012**, surrounding the ordinary network preparation and optional F181 read.
`TCUWUnifiedUtils.dll!10004E90` constructs all four messages. The result-query
expectations additionally require the trailing result byte **01**; receipt of
just a `71` service response is not its success condition. The actual last
transition pair occurs before the target's mandatory programming-session
exchange.

For the P4-style branch, the final gateway transition is
`ChangeModeForCentralGW` at `10001FB0`, followed by the target programming
exchange. This addresses **11-bit CAN 750/758 with ISO-TP address extension
5F**, not 29-bit CAN identifiers. The host constructs `10 60`; its recovered
response template explicitly checks the positive-service prefix `50`, not a
separately pinned `60` byte. The broader `50 60` shorthand must not be mistaken
for the exact matcher.

Both branches use normal manufacturer authorization. No seed/key derivation,
authentication bypass, parser corruption, or steering-control injection was
developed in this pass.

### Exit handling and two non-transferring alternatives

The reviewed prepare writer's failure cleanup stops its tester-periodic work
and removes host J2534 filters. Removing a host filter is **not** restoring
gateway or EPS state. The normal flash-writer finish path contains a gateway
DefaultSessionControl call only for its enum2 branch; the current helper
`DefaultSessionControlForP4CentralGW` constructs `10 01` for the shared 5F
route. It is not evidence that an arbitrarily aborted P5 preparation has a
fully recovered, state-restoring exit. This is why the extracted sequence is
not being shipped as a blind live-send script or advertised as an approved
recovery runbook.

`StopOTAReprogramming` was traced past its suggestive name. The reviewed
function constructs a Phase-6 operation addressed through logical target1C,
and the only import consumer in the recovered CUWPlus DLL set is
`TCUWP6CanReprostdPrepareWriter.dll`. No call from the selected P5-Unified EPS
prepare writer was recovered. It must not be presented as a Toyota-wide
command that restores this EPS or selects an alternate EPS firmware bank.

Similarly, the final target reset in the ordinary Unified flash-writer path
is a request serviced by the target. It supplies no hardware reset to an EPS
whose processor is not executing its diagnostic server.

### Recovery decision

The newly supported candidate is **complete, correctly selected OEM gateway
preparation followed by an EPS-specific programming/liveness exchange**, not a
peer error-code read. The preparation could distinguish a routing-hidden
listener from the currently reconstructed failure, and its absence from the
retained recordings prevents calling this network precondition live-exhausted.
It cannot repair a genuinely faulted EPS by proxy. No response proving such a
surviving listener, and no working network repair, has been observed.

The next action cannot be promoted to flash repair on the strength of a
gateway acknowledgement alone. It needs an actual EPS response in the prepared
state, correct target identity and image compatibility, and normal authorization.
Until then, the result remains a specific untested network avenue rather than
a recovery success. The exact current protected stubs/sidecars and recovered
bodies for all five involved CUW libraries were hash-matched against the
recovery manifest; their identities are retained in the observation artifact.


## 19. Network-selected startup state versus gateway routing

2026-09-12. This pass tested two alternatives to another EPS-directed diagnostic
retry: a retained programming request that could select a different startup
state, and a host-controlled intermediary routing mode. All work was offline.
There was no vehicle connection, traffic generation, session change, ECU reset,
RAM upload, flash write, or physical connector operation. No working recovery
route was established.

### 19.1 The normal programming handoff is not a next-reset request

Fresh target-native decompilation of `65F5E`, `9F00`, `148E`, and `1478`
establishes a direct transition rather than a persistent boot-request flag:

```text
normal application system-mode worker
  -> 65F5E: mask service; clear FFC0A000/4/8/C; call 9F00(31788)
  -> 9F00: disable interrupts/reset application context; call 148E
  -> 148E: copy nine configuration words through 1478; enter 1398
  -> boot diagnostic runtime
```

The nine ROM words at `31788` are `00000000, 000007A1, 00000000, 00000000,
00000002, 00000000, 00000000, 00000000, 00000000`. They are fixed handoff
configuration; this pass does not assign undocumented field names to them.
There is no reset between setting this configuration and entering `1398`.

The separate cold path was rechecked through `C9A`, `E54`, `F80`, `10C6`,
`119E`, `481A`, `3438`, and `344C`. The initializers set ports/ECM/clock state;
`E54` conditionally preserves error status from a complement-coded record, not
a boot request. The descriptor selectors are ROM-based. The boot decision still
uses descriptor/CRC/validity conditions and does not consume the live-handoff
configuration as a next-reset request. `7A132` independently initializes the
application communication state and ends with the unconditional `FE01` value.

Exact stock-to-complete-incident byte comparisons passed for `00C9A..0149B`,
`09F00..09F53`, `31788..317AB`, `65F5E..65F8D`, and `7A132..7A187`. The
incident reconstruction is the retained `aba6867f...50f2d74` image, and both
validity words remain `5AA5A55A`. This is a reconstruction check, not a new live
readback. It rules out using the *normal handoff's configuration* as evidence
for a CAN-selectable warm-reset recovery flag; it does not prove every unseen
hardware startup mechanism absent.

### 19.2 A package gateway list is not a generic intermediate-ECU programmer

The installed P5-Unified preparation module was checked at its gateway loop,
not merely at the later target `10 02` exchange. Current protected inputs,
sidecars, and recovered output hashes all matched the existing manifest for
`TCUWCanUnifiedPrepareWriter.dll`, `TCUWCanReproStdPrepareWriter.dll`,
`TCUWUnifiedUtils.dll`, and `TCUWDHUtils.dll`.

The decisive Unified preparation region is `10002230..10002310`:

- `10002234` obtains the number of package-declared gateways.
- `10002247` reads each gateway's diagnostic-ID string.
- Its first comparison uses `100041C8 = "07505F"`, selecting the central
  gateway routines already described in sections 11/16.
- Its second comparison uses `1000425C = "0751"`. A match invokes
  `RoutineControlForSMCCentralGW` at `100022FE` with routine type 2.
- A gateway matching neither string advances the loop at `1000230F`; this
  region does not invoke a generic routing-mode operation on arbitrary
  intermediaries. Afterward, the ordinary target transition is still called
  at `10002363`.

These literal identifiers describe the host dispatch. They are not proof that
both gateway variants are installed on this Camry, that `0751` is the brake
intermediary, or that such a routine runs a programmer inside the EPS.

The distinction from the related writer matters: Unified imports
`GetNumGateway` and `GetGatewayDiagID` but not `GetGatewayMode`. The current
ReproStd writer *does* call `GetGatewayMode` at `100022A0` for the first declared
gateway. That API's existence in a related module is not evidence that Unified
accepts an arbitrary replacement gateway-mode byte, or that the missing exact
EPS package selects ReproStd. No guessed gateway command was emitted.

### 19.3 Keep the delivery and execution hypotheses separate

A target instruction fault and an intermediary forwarding failure are different
explanations for diagnostic silence. Upstream traffic, a tester TX echo, or a
reply from a neighboring ECU cannot on its own establish the downstream EPS's
execution state. Conversely, opening a forwarding route would not repair the
malformed instruction if the reconstructed application is actually running and
faulting as predicted. A gateway-only recovery hypothesis therefore needs
independent evidence of an EPS recovery service that is alive but unreachable,
not merely evidence that some gateway mode exists.

The inspected host flow does not establish a network command for controlling
an additional brake-side forwarding hop. The exact intermediary firmware is
not in the registered firmware corpus. The known `7B0` / `F152633K0000` identity
is category-435 Brake/EPB; the separate category-466 Brake Booster catalog must
not be assigned that identity without a target match. Existing package-acquisition
evidence records no local exact `07B0` image and no validated download URL.
These are explicit evidence gaps, not proof that a supplier-level routing or
recovery facility cannot exist.

The outcome is narrower than declaring all network recovery impossible: the
normal direct handoff does not create a retained next-boot selector, and the
selected Unified gateway list does not provide arbitrary intermediate-node
mode control. Neither result supports another ordinary EPS request as a new
recovery technique, and neither is a completed repair.


The gateway-specific candidate in section 18 is compatible with this narrower
loop result: normal authorization and the correct recognized gateway branch
may expose an already-running EPS listener; merely adding an arbitrary brake
address to the package's gateway list does not do so. Its absence from the
retained traffic is a test-coverage gap, not a demonstration that preparation
will repair the incident.


The section-18 positive host result was independently rechecked: the
`100026E0` identity wrapper reaches `ReadSoftwareID` at `10002778`; its
FuncInfo at `10004B1C` points to one try block (`10004AE8`, states 2..2),
whose catch-all handler at `100027AE` returns continuation `1000277E`.
The exact six handler bytes are `B8 7E 27 00 10 C3`. Re-running the historical
gateway extractor also reproduced all `counts`, `messages`, per-file rows,
and parse warnings exactly: 39 inputs, 184 selected logged records, and only
0F/6D shared-address extensions in the retained transactions. No unrecorded
wire-format bit or traffic outside those captured spans was inferred.

The separately named `CDHUtils::ChangeDefaultSessionForPhase5` and
`StopCommunicationForPhase5` were checked rather than borrowed as a guessed
abort procedure. Their named import consumers are the DH/DHUDS writer families,
not Unified; the former builds suppressed-response default-session requests,
and the latter builds communication-control requests. Their names and presence
in a shared library do not by themselves establish the selected Unified P5
preparation's target-specific state-restoring exit.


The adjacent pre-transition helpers were also checked to avoid mistaking the
optional F181 wrapper for the whole preparation path: `100019A0` builds
TesterPresent transmissions, and `10002980` builds CommunicationControl
transmissions with positive-response suppression. Both use the J2534
`WriteMsgs` import rather than a mandatory EPS response matcher. The caller
at `10002115..10002227` performs this network preparation and the optional
identity wrapper before the final recognized-gateway loop. This supports the
local host-flow ordering only; it neither proves successful gateway preparation
on the vehicle nor permits borrowing an unverified abort procedure.


## 20. The current writer selects two distinct gateway-address families

The section-18 hypothesis was extended to the other gateway helper actually
imported by the current Unified writer, rather than treating every function
named “central gateway” as the same route. This was an offline pass: no network
mode change, vehicle request, flash write, or new physical connection occurred.

Fresh import/export, literal, vtable and instruction checks establish:

- `TCUWCanUnifiedPrepareWriter.dll!10001C00` first recognizes package gateway
  **07505F**. That selects the `JudgeReproGWNode`-qualified P4/P5 cases already
  described in section 18. Both forms use 11-bit CAN **750/758** with address
  extension **5F**; the number is not a 29-bit CAN arbitration ID.
- The separate branch compares the first package gateway against
  `TCUWDHUtils.dll!GetCentralGWReqCanID`, whose export at **10003FF0** constructs
  the two bytes **07 86** from the literal at **1000B204**. This family's
  default request/response strings at **1000B3C4/1000B3D0** are **00000786** /
  **0000078E**. Only the matching branch calls
  `StartCentralGWReprogGWModeForMultiTypes` at the writer's **10001E2C** callsite.
- The DH helper at **10007190** selects its own specification-dependent
  single-/two-CPU preparation. The constructor's vtable at **1000B290** binds
  the calls to the named gateway-session, normal authorization, and default-
  session helpers. Its `CheckConnectionWithCentralGW` at **10002470** is a
  gateway TesterPresent check, not a request for the EPS to run code. This is
  another manufacturer-defined gateway family, not an arbitrary substitute
  address for a silent EPS.

The current protected stub, sidecar and recovered output for `TCUWDHUtils.dll`
were hash-matched to the existing recovery manifest, as were the current
CommonPrepareWriter/UnifiedUtils/UnifiedPrepareWriter inputs. The additional
helper's identity is preserved in the section-18 observation artifact. The
unprotected DLL is the actual source of these control-flow facts; its name or a
past narrative was not used as proof.

The saved-log extractor now explicitly watches **786/78E** as well as the
previous address set and publishes that set in `watched_addresses`. All **39**
per-file observations, previously selected **184** logged records, decoded
messages and parse warnings reproduced unchanged. There are **zero 786/78E
records**, just as there are no **750/758 node-5F records**, in those captured
spans. The independent address-only census agrees. Neither negative proves what
happened outside those spans; neither identifies the installed gateway family.
No authentication exchanges or memory contents were retained by the reducer.

The acquired **T-0035-22** EPS-family package selects **07505F**, but is for
Tundra calibrations, not F33. The acquired Camry **T-0051-26** package also
selects **07505F**, but is an MG/inverter update, not an EPS update. These are
specific package-selection examples, not permission to guess the F33 package
or select the DH family merely because the car is new.

The useful network-only test remains completing the **correct OEM gateway
preparation**, with its real acknowledgement/result checks, before assessing
the EPS listener. The independently checked catch-all around the optional
pre-transition F181 read means initial EPS silence does not prevent that host
path from advancing. That is a real difference from another identical EPS
request. It is still a test of a routing-hidden surviving listener, not an
independent flash executor, a way to clear the CPU fault, or a verified repair.


## 18. Alternate diagnostic sessions and network modes, from the actual tables

2026-09-12. This pass investigated ordinary network mechanisms other than a
repeat of the primary programming-session request: the separately configured
manufacturer session `40`, protocol preemption, and CommunicationControl's
subnetwork/subnode modes. It was offline; no vehicle connection, transmission,
session change, reset, RAM upload, or flash operation occurred. It did not
establish a working network-only repair.

### Three service profiles, not one primary service list

The exact F33 service selector at `90F98` reads ROM **indices**, not a function
inventory. Its object table starts at `25C54`, with 24-byte objects. Three
8-byte descriptors at `25C0C/25C14/25C1C` select:

| External DCM source key | Selected service-object indices | Session-Control subfunctions |
|---|---|---|
| `2` | `0..16` (17 objects) | `01`, `02`, `03` |
| `3` | `17,2,7,9,13,14` (6 objects) | `01`, `03` |
| `4` | `18,19,20,21,22` (5 objects) | `01`, `40` |

These are the source keys that `93F0E` maps to the three internal receive
channels. The third profile contains SID `10/19/22/3E/AB`; it is not the
primary programming profile and does not select the download/transfer services.
An object appearing in a selected list is not, on its own, a claim that its
callback is non-null or available in the current session.

The third profile's `40` entry at `25B5C` points to **`95D3C`**. That callback
is absent from the canonical 6,065-function inventory, but its raw instructions
are real: the 18-byte wrapper supplies `r8=40` and calls **`95C52`**. Several
ordinary `10`/`28` wrappers are likewise not separately defined in that inventory.
Consequently a name/direct-caller census was insufficient to exclude these
configured modes. They were checked from ROM entries and independent RH850
instructions instead.

### Session `40` does not select the programming handoff

`95C52` routes an initial request to `95A3E`, cancellation to `95B48`, and
asynchronous polling to `95B88`. The initial handler looks up the requested
session in five 10-byte rows at `26122`. Relevant exact rows are:

| Row | Session | Transition-kind byte |
|---|---:|---:|
| `26122` | `01` | `00` |
| `2612C` | `02` | `02` |
| `26136` | `03` | `00` |
| `26140` | `40` | `00` |

Kind zero uses the ordinary session-state update and timing response. The
nonzero row for session `02` instead sets the asynchronous transition state
and enters the handoff-related processing. Session `40` therefore does **not**
select that boot-transition branch just because its numeric value is
manufacturer-specific.

The ordinary session notifications were also followed. `92518` invokes the
fixed `968CC/9704E` callbacks and `92044 -> 9202A -> 8B0DE`.
`8B0DE -> 4D582/6A156` resets application diagnostic bookkeeping and requests
cleanup of an already-active crypto test. The apparent `88` in
`4D582 -> thunk_B9320(88)` is only a write to `FEBEAF47`; it must not be
confused with the unrelated boot ASIC's SPI programming command. None of these
reviewed session-40 notifications supplies a new boot jump.

### The missing dispatcher callback is queued event zero, not an interrupt server

The ordinary service entry `91566` is called by `91C0A`. Its caller at `922CE`
was outside a recovered function, so `inspect --callers` misleadingly returned
zero callers for `91C0A`. Raw instructions recover **`922AA..922E7`**: it checks
DCM state `2`, then invokes `91C0A` for the selected receive channel.

The exact fixed pointer to `922AA` is **`26B18`**, event-zero slot in the DCM
callback array consumed by **`98946`**. This closes the actual scheduled entry:

```text
988C2 -> 98946 -> event[0] = 922AA -> 91C0A -> 91566
                                           -> ROM service-profile selection
```

Receive completion still uses `91F72 -> 92B4A -> 92A86` to prepare state;
`92A86` only writes the requested DCM state under its normal critical section.
`98B3A` only arms a timer, while `98AE4` consumes timer callbacks later in the
same `988C2` foreground worker. The timer callback at `922EA` enqueues event
zero through `989EC`; it does not invoke `922AA` inline.

Protocol preemption was checked separately rather than assuming all protocol
starts were deferred. `93978 -> 937B0` contains a synchronous protocol-change
approval callback, **`92040`**. In this exact image it is a literal
`return 0` stub. The other reviewed preemption work prepares state, cancellation,
and queued events. Thus the real alternate profile and its protocol approval
callback do not remove the dependency on the worker after the damaged call.

This is a reconstruction of the configured ordinary paths, not a proof that
every arbitrary computed transfer or undiscovered firmware defect is absent.

### Enhanced-address CommunicationControl is compiled but not configured here

The common `96E6A/96BFC` implementation contains handling for subfunctions
`04/05` and a node identifier. That is a legitimate reason to inspect it as a
possible alternate network-management path rather than stopping at the menu.
Exact ROM configuration nevertheless differs from the generic implementation:

- Both service profiles that select SID `28` select only callbacks for
  **`00`, `01`, and `03`**. The third profile does not select SID `28`.
- At `261C8..261D7`, there is one enabled all-channel entry (channel `0`),
  **zero specific-channel entries**, and **zero subnode entries**, with null
  specific-channel and subnode table pointers.
- `96BFC` consults these actual counts and tables when validating an enhanced
  node request. The presence of a generic node-processing branch is not a
  configured second programmer or downstream control channel in this F33.

No unsupported request was sent to test the unused branches. These results
apply to the **EPS image**, not to an unacquired brake/gateway firmware image.

### Reproduction and confidence

`tools/targets/camry/analysis/analyze_f33_recovery_structure.py` now extracts
these ROM-selected profiles, session rows, dispatcher slot, and channel counts
into `network_diagnostic_modes` in the existing generated report. The narrow
`f33_recovery_structure` suite verifies the indices, callback call targets,
transition-kind distinction, and absence of configured enhanced subnodes from
tracked firmware bytes. It does not test Markdown or require an external ECU.

The relevant service tables, ordinary-mode code, and event table were also
compared with the complete retained incident reconstruction
`aba6867f...50f2d74`; they are byte-identical. The raw table/call facts are
**verified** by the deterministic checks, and their execution interpretation is
**recovered**, not a new live capture. Temporary function recovery was limited
to the working project; the three extra function entries left after nested
transaction rollback were explicitly removed, and the resulting set of all
6,065 function entry addresses matches the original inventory. No committed
project snapshot was changed or promoted.

The alternative session exists, but its complete configured path still does
not execute a repair before the bad hook. This narrows a genuine inventory gap;
it is not a recovered unbrick sequence.
