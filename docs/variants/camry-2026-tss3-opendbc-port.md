# 2026 Camry TSS3 openpilot/opendbc port

> **September-16 evidence-audit supersession:** historical steering and `0x160`
> field experiments remain retained, but the current runtime contract is the one
> in [the capability matrix](camry-2026-capability-matrix.md),
> [the evidence review](camry-2026-port-evidence-review.md), and
> [the TSS3 arbitration note](../architecture/toyota-tss3-vehicle-movement-arbitration.md).
> In particular, `0x160` is no longer a native-long actuator candidate: `0x08A`
> is the shared TSS3 application-request plane, and both current TSS3 platforms
> keep Toyota stock longitudinal until clean `0x08A` source ownership exists.

**Target:** maintainer 2026 Toyota Camry Hybrid, EPS application F181
`8965F3307000 / 8A3113303100`.

**Current control result:** the September 10 development configuration produced
observed openpilot lateral control primarily on route `0000008d--a9f348691a`, with
later same-build route `00000093--4066e7ae51` as a shorter corroboration, while the
native `0x08A` and `0x081` request/result planes remained Target Lateral ID 0
(Toyota LTA off). The direct route evidence, exact software/RAM identities, and
the independent TSS3 Corolla longitudinal proof of concept are summarized in
[toyota-tss3-openpilot-bounty-evidence.md](toyota-tss3-openpilot-bounty-evidence.md).
Earlier passive/direct-B6 checkpoints below remain useful history, but they do
not supersede that working result.

**2026-09-16 runtime checkpoint:** the current production-shaped candidate no
longer host-transmits B6 or depends on a dummy/zero MAC. `CarController` sends
the unified Classical functional C7 frame `07 C7 C7 seq target_hi target_lo 00
00` on **stock Toyota-B Panda bus 1 / CAN `0x777`**; Panda permits only that
bounded envelope. The volatile continuous resident edits an already-native B6
inside the EPS and obtains a native-valid FV4+CMAC28 through the EPS ICU-S
command-5 path. Changed nonzero generations renew a seven-foreground-tick host
lease; expiry or sequence zero returns ownership to untouched native B6. The
current installer is a single cross-variant 4-KiB authenticated payload that
self-selects the exact F33/Crown/Corolla profile; F33 stages its helper through
`FEF07C00` and installs it at count 224, so no C6 loading phase remains.
Longitudinal remains entirely Toyota-owned:
openpilot advertises no TSS3 Alpha Long, does not synthesize or suppress `0x160`,
and does not transmit `0x08A`. HUD/cancel transmission claims from the older
integration are likewise bounded by the current capability matrix. The intended
lateral runtime requires **no persistent EPS CodeFlash patch**; the stage-5
receiver bypass and persistent signer below are historical development artifacts.
Current qualification status and exact next vehicle tests are maintained in
[camry-2026-capability-matrix.md](camry-2026-capability-matrix.md) and
[the minimal runtime contract](../architecture/toyota-tss3-minimal-runtime.md).

**Evidence boundary:** this report closes the exact-F33 generated-COM transmit
geometry, the software integration, and the development B6 sender/safety envelope.
The September 10 route establishes steering for the exact C7/RAM configuration;
it does not qualify direct host-B6 transmission or make the Camry adapter a
universal TSS3 interface. CORR-129/VAR-081 identify **73.303384 s of retained `0x08A` ID11 LTA/LCA request state with zero B6**; this is not a direct winner/grant oracle. CORR-134 recovers B21 as Target Lateral ID and B18:B19 as the signed request-angle quantity; CORR-135 rejects a presumed `0x08A -> B6` transform. Exact F33 neither accepts `0x08A` nor transmits it, while its B6-inactive internal path reaches physical steering; that makes zero B6 architecturally possible but does not prove the retained request was granted. VAR-091/CORR-136 place authenticated `0x08A` on the intercepted chassis network while observed Toyota-Bus-1 camera/radar PDUs use E2E. The later repin/source experiment resolves the source ambiguity those older rows could not: with the relay open, protected `0x08A` is native on the **FRC/camera-side endpoint** and forwarded byte-for-byte toward Brake, while `0x081` is native on the Brake/chassis side and returns toward FRC. FRC CommunicationControl removes `0x08A`; therefore the secured publisher/signing boundary is inside the FRC assembly, even though the exact internal key/HSM owner remains open. VAR-094 proves consecutive `5282` is absent from native Bus-1 CAN; CORR-138 retracts the former standing-echo interpretation of `0x160[22]`. VAR-101 proves the authenticated publication continues at zero request, not that the CMAC engine is downstream.

The integration and stock-architecture questions are deliberately separate.
OQ-054 now tracks the **internal FRC feature-owner + `0x08A` signer/key/freshness path** and the downstream Brake/VMM verification/request-arbitration/result/request-generation -> B6 path. That attribution is **not** a prerequisite for the demonstrated C7 ->
native-B6 ingress. Exact-F33 Gate-2 compare neutralization and the historical
zero-MAC/wrong-key host-B6 senders remain useful failure-localization evidence,
but they are not the current sender. VAR-155/156 and the September 10 road handoff
supersede that architecture: local selector-4 command-5 signing reproduces the
native trailer and continuously re-signs the resident's B3..B9 replacement before
the untouched SecOC consumer. The current `kai-openpilot`/opendbc path therefore
carries only C7 through ordinary Toyota safety; B6 construction/freshness/MAC
ownership stays inside the EPS. Upstream comma opendbc still has no Camry TSS3
platform, so the comparison target remains upstream architecture rather than a
preexisting wire implementation.

**September-17 `0x08A` sender-experiment checkpoint:** the exact F33 car kit now packages two deliberately separate, non-actuating discriminators. `f33-sign verify-native-08a` asks the already-live-qualified selector-4 command-5 path to reproduce stock `0x08A` MAC28 without transmitting `0x08A`. After a full EPS power-off, `f33-08a-route` installs a different volatile resident/helper and replays one unchanged stock Target-Lateral-ID0 `0x08A` through exact HTH0 lower object 47 / writer `0x85112`; the helper uses special software handle `0x00F0` and `FEBE502A` departure as a physical-completion witness. Both host and resident reject a nonzero Target Lateral ID and one successful EPS transmit closes the probe for that boot. The routing result distinguishes an EPS-local Tx path that reaches Panda from a selectively forwarded EBU/local segment. It does not yet create a new sender freshness stream or authorize longitudinal output. Runbook: [the F33 `0x08A` sender experiments](../../exploit/ephemeral_runtime/camry_f33_08a_sender_experiments.md).

**September-17 same-cycle DRCC checkpoint:** application reappearance after the
volatile bootstrap is not sufficient evidence that the rest of the vehicle has
returned to its pre-bootstrap state. The current loader intentionally enters the
EPS programming bootloader, so normal EPS application traffic disappears while the
boot transition, SecurityAccess, 4-KiB download, verify, and FF00 execution run.
The host path additionally retains a 700-ms extended-session settle before the
handoff. Toyota's own Unified prepare writer confirms that this outage is expected
for reprogramming rather than hidden from peer ECUs: it sends suppressed
`85 02` (DTCSettingOff) and `28 01 01` (normal-communication Tx suppression) as
part of preparation. Consequently the working hypothesis is **peer fail-safe /
communication-loss state that survives EPS application return**, with bootstrap
latency as an aggravating factor rather than the sole explanation.

The original DTC-clear-only same-cycle experiment was negative. The parked/READY
diagnostic clear can remove the communication-warning/DTC state while leaving the
RAM resident intact, but **DRCC did not re-enable after that clear by itself**. The
historical `recover-drcc` command therefore remains useful for preserving SID19
evidence rather than being the recovery mechanism. September-18 live work below
supersedes the earlier conclusion that a full vehicle power cycle was required.

Current GTS+ exposes several state layers below DTC storage. `ABS_P5` DID `0x102D`
provides live `Fail Status` (MSB0 bit57) and `Fail Control` (bit58), while DID
`0x102F` provides `EPS/Steering Control Actuator ECU Communication Open` at MSB0
bit74 with OEM states `Normal` / `Under intermittent`; these fields are also in the
Brake/EPB generic freeze-frame schema. FRC still exposes the immediate ACC consequence
through `0x1903 Control Mode`, `0x1905 Cruise Control Permission Flag`, and `0x1906`
`ACC Not Available Icon Lighting Request Flag`. `FRC_P5` DID `0x1B09` additionally
contains six unsigned bytes named `Fail-Safe Factor B1a`, `B1b`, `B2`, `C1`, `C2`,
and `D1`, and GTS+ snapshots them in FRC freeze frames. However, these bytes sit in the
`0x1B03..0x1B09` ISA/speed-limiter request block, and successor `ADCU_P6` explicitly
names the same six-factor shape `... for Speed Limiter`. They are therefore useful
ancillary fail-safe evidence but **not identified as the DRCC latch**.

The strongest DRCC-specific GTS+ state is in the exact Camry-installed Hybrid-Control
`HV_P5` RoB schema. Returned RoB DID `0x55FE` contains `Request Manual Cancel`
(MSB0 bit12), `Request Automatic Cancel` (bit13), `Cruise Brake Control Permission
Condition` (bit14, `NG/OK`), and `Cruise Control Permission Condition` (bit15,
`NG/OK`). RoB DID `0x55FF` carries `Cruise Control Condition` at bits80..87 with the
exact Toyota enum `1=No Control`, `2=Constant Speed Control Mode - Ready`,
`3=...Controlling`, `4=Vehicle Distance Control Mode - Ready`, `5=...Controlling`,
`6=Termination Control`, `7=Suspend`, `8=Abnormal Stop`. These are not ordinary
Data-List DIDs; they are behavior-record snapshots. Current GTS+ role `0xA0`
`GetRoBP5_DT.dll` retrieves them read-only by enumerating behavior codes with
`AB01/AB11`, frame IDs with `AB02/AB12`, and records with `AB03/AB13`; each returned
record is a set of DID/length/data blocks. The behavior dictionaries themselves
also provide useful named event classes: Hybrid includes `X0586 Shift Operation during
Power Steering System Preparation` and `X05A8 Lack of Advanced Drive Torque`; FRC
includes `X216E Front Recognition Camera => BRK Communication Invalid` and `X2400
Lateral Control System Malfunction`; Brake includes `X208E Power Steering Control
Module Malfunction`. Presence of one of those returned behavior codes is event-history
evidence, not by itself proof of the live gating owner. The maintained
`toyota-diagnostics` `health-check` implementation already executes and decodes that
exact current-GTS+ RoB protocol, so `toyota --profile camry-2026-f33 health-check
--out <file>` can capture FRC/Hybrid/Brake behavior history without a new vehicle
probe protocol. The same Health Check also issues the recovered ordinary-P5 per-DTC
freeze-frame request `19 04 <DTC:3> FF`, retaining and decoding returned snapshot
DID blocks. A post-bootstrap capture can therefore preserve both the U0131-specific
snapshot at fault time and the independent RoB behavior history before any DTC clear.

The current FRC Active-Test catalog has 69 routine candidates but no fail-safe/ACC
recovery or reset routine; its relevant entries are display/buzzer/steering-vibration
operations. Current GTS+ category-498 master frames likewise contain no `11 xx`
ECUReset request. A 2026-09-17 parked exact-car probe now closes the default-session
case. On the restored stock Toyota-B harness the live FRC route is Panda bus1; F181
returned `8646F3315000`. Before the reset attempt, `0x1903=01` reported DRCC all-speed
mode, `0x1905=8000` had Cruise Control Permission denied, and
`0x1906=e080e0008080` had the ACC-not-available indication asserted. Physical
`11 01` returned **`7F 11 7F`** and F181 remained continuously responsive, with all
three state DIDs unchanged afterward. A follow-up same-car probe then entered extended
session successfully (`10 03 -> 50 03 00 32 01 F4`) and immediately retried `11 01`.
The FRC again returned **`7F 11 7F`**. F181 answered every 100 ms across the following
2 s with no gap or identity change, and `0x1903/0x1905/0x1906` remained
`01 / 8000 / e080e0008080`. Thus ECUReset type `0x01` is unavailable in both tested
default and extended application sessions on this exact FRC; no hidden reset occurred.
Toyota's FRC ReproStd reprogramming path proves a third distinct session exists:
**programming session `10 02 -> 50 02`**. The same preparer also contains `10 83`, but
that is extended session `0x03` with the UDS suppress-positive-response bit set, not a
new session; the flash writer's `10 81` is likewise suppressed-response default session
`0x01`. No current FRC host/CUW evidence identifies a distinct `0x04` safety-system
session or Toyota-private DiagnosticSessionControl value. The ReproStd sequence enters
`10 02`, then performs level-1 SecurityAccess (`27 01 -> 67 01 || seed[16]`, followed
by `27 02 || key[16] -> 67 02`) before the flash flow, whose tail later issues `11 01`.
That made **programming + SecurityAccess** the strongest software-only reset
candidate before the live probe. The repository does not contain the exact
`8646F3315000` CUW; six available `0x792` FRC CUWs (`8646F1.../F4...` families)
share ServiceAuthKey `3A8A90AE0ED81B6C37E21C1C5179A93E`, SecurityProperty2
`0x9C`, and ReproMethod `0x07`. The September-18 exact-car probe below makes the
credential transfer unnecessary for reset: programming-session `10 02` followed
by `11 01` is accepted without SecurityAccess.

The stock comma harness cannot power-cycle the FRC. Panda's production `drive_relay`
controls the harness-box solid-state CAN0/CAN2 intercept pair only. The second
firmware control named `ignition_relay` is explicitly debug/test-only and drives the
SBU ignition-sense line; the open-source harness-box schematic shows no switched FRC
power path. Toyota-B carries the camera's brown `IGN` conductor straight through the
harness, and the harness box uses `IGN_12` as a hard-wired power/sense net. A true
selective FRC power cycle would therefore require an external/in-line relay or high-side
switch in that brown `IGN` conductor (or equivalent physical camera-power interruption),
not the existing CAN intercept relay. Such a test remains attractive because it would
leave the EPS LocalRAM resident powered, but it should follow the extended-session
ECUReset probe rather than be treated as an existing software capability.

A 2026-09-18 parked exact-car probe closes the remaining software-reset branch. The
FRC accepts **programming session `10 02 -> 50 02 00 32 01 F4`**, and in the same
continuous UDS session accepts **hard reset `11 01` without SecurityAccess**. Immediately
after the reset, four F181 probes returned negative responses before application F181
`8646F3315000` reappeared about **0.38 s** after the reset call returned, establishing a
real selective FRC restart while the EPS remained powered. The restart did **not** recover
DRCC/ACC: `1903/1905/1906` returned to `01 / 8000 / e080e0008080`, LDA remained disabled
(`1501=0101`), PCS availability remained disabled (`1703=f020`), and PCS ESA/AES invalid
flags remained asserted (`1705=ff18`). After restarting openpilot, `carState` remained
Park/0 m/s with `cruiseAvailable=false`; the EPS resident path survived, with 299 neutral
C7 frames observed in 3 s. Therefore the fault is not a simple volatile FRC application
latch cleared by restarting that ECU; it is retained or immediately reconstructed from
peer/persistent state. Raw summary: `targets/camry-2026/raw-20260918/frc-programming-reset/summary.json`.

A same-session follow-up immediately closes the higher-value dependency-order recovery.
The category-435 Brake/EPB ECU (`0x7B0`, F181 `F152633K0000`) likewise accepts
**`10 02 -> 11 01` without SecurityAccess** and stays off the normal F181 application
interface for about **1.46 s** before returning. Before reset, Brake `0x102D` already had
`Fail Status=OFF` and `Fail Control=OFF`, while `0x102F` reported EPS communication
`Normal`; nevertheless the FRC remained faulted (`1905=8000`, `1906=e080e0008080`,
`1703=f020`, `1705=ff18`). Resetting Brake alone changed the FRC PCS-facing state to
healthy (`1703=f000`, `1705=ff00`) but left DRCC permission denied and LDA disabled.
A **second selective FRC reset after Brake had recovered** then changed the FRC state to
`1905=8080` (**Cruise Control Allowed**), `1906=e080e0008000` (**ACC Not Available OFF**),
`1501=0100` (**LDA Enabled**), `1703=f000`, and `1705=ff00`. The EPS remained powered
through all three selective resets; after restarting openpilot, the resident path still
produced 299 neutral C7 frames in 3 s. The complete live sequence was **FRC -> Brake/VMM
-> FRC**: the first FRC reset left the fault intact, the Brake reset cleared the upstream
PCS invalid state, and the final FRC reset cleared its remaining DRCC/LDA latch. No DTC
clear occurred in this successful sequence.
Raw summary: `targets/camry-2026/raw-20260918/brake-frc-recovery/summary.json`.

The subsequent road route `0000010c--506d7277c7` closes the practical recovery
question rather than stopping at parked diagnostics. Its 30 rlogs span 1,743.811 s
and contain 13 openpilot lateral-active episodes totaling **919.594 s** and
**19.772 km** while stock adaptive cruise overlaps for **919.572 s**. Openpilot
`longActive` is never asserted. C7 contributes 91,570 active commands at ~100 Hz;
91,568 have successful Panda TX returns, and the two rejected nonzero frames occur
only after `latActive` has already fallen false at disengagement transitions. Active
sequence continuity has zero mismatches. C7 target angle spans -31.746..25.328 deg,
measured steering spans -31.3..24.8 deg, and the full active population has Pearson
r=0.9939 / 0.505-deg MAE at the best tested 260-ms command lead; the low-driver subset
improves to r=0.9962 / 0.455 deg. No permanent steering fault occurs; the 13 temporary
fault samples are all parked/inactive shutdown samples in segment 29.

The coexistence classification is independently visible on Toyota traffic. During
openpilot `latActive`, all 36,779 native `0x08A` lateral request IDs and all 30,652
`0x081` lateral result IDs are **0**, so factory LTA is not the steering source.
At the same time stock longitudinal is active: during the adaptive-cruise overlap,
`0x08A` upper request ID is 11 on 36,777/36,779 frames, the lower request is primarily
ID17 (36,709 frames), and `0x081` returns longitudinal result ID11 on 26,339 samples.
The route also contains a 15.871-s <0.5-m/s stop while the adaptive+lateral overlap
remains selected. Source hashes and the complete derived reduction are retained in
`targets/camry-2026/raw-20260918/recovered-road-drive/summary.json`; the 30 rlogs and
30 qlogs are archived outside git under
`/Users/kai/dev/inspect/logs/camry-2026/2026-09-18/0000010c--506d7277c7/`.

Thus GTS+ plus the programming-session probes now provide a concrete **same-ignition
recovery sequence that preserves the EPS RAM resident**, and route `10c` road-qualifies
that recovery with stock adaptive cruise. `camry_f33_post_install_recovery.py` now snapshots the FRC and Brake live state DIDs
before and after the known DTC clear, treating newly added DDB-derived DIDs as
best-effort until exact-car support is observed. The higher-value paired capture is a
before/after `health-check`: if DTC bits clear and Brake EPS communication has returned
normal while Hybrid RoB records show cruise permission `NG`, automatic cancel,
`Suspend`, or `Abnormal Stop`, the persistent denial is in the cruise-control state
machine rather than DTC memory. If Brake `Fail Control` or EPS communication-open stays
asserted, the brake-domain dependency remains active instead.

A September-17 retained-route comparison adds a much narrower Brake->FRC wire lead.
Toyota Prius 2023-2026 service-manual data (https://www.mytoyo.com/front_camera_system-1160.html)
describes FRC behavior record `X2400 Lateral Control System Malfunction` as the camera receiving a
**lateral-control-system-unachievable signal from the skid/brake controller**; the
associated fail-safe chart requires the malfunction to be resolved and the ignition
cycled before normal operation returns. Current GTS+ independently supplies the exact
`X2400` behavior name but not that wire-field encoding. The recovered current TSS3
recorder supplies a stronger intermediate semantic oracle: **`5283` byte 1 =
`Lateral control system fail class status`**. Its remaining bytes separately carry
drivetrain, auto-brake, parking-brake, driver-brake, and stand-still-control
fail-class state. `5283` is recorder-domain data, not yet a CAN-byte mapping, but
it is now the primary semantic join for the manual's skid/brake
`lateral-control-system-unachievable` condition.

A Toyota follow-on motion-manager patent adds an unusually strong independent
semantic match. US20230082947A1 separates **raw actuator reliability** from the
**application-facing fail class**: steering sends `STR2` reliability/state to
the Brake-hosted motion manager, and the manager's generation unit synthesizes
`PLN2` fail-class information back to the driver-assistance applications. The
steering reliability model distinguishes normal, protective-control, abnormal
but not yet confirmed with control invalid, and confirmed failure. Its
application-setting metadata can include influenced vehicle-speed range,
malfunctioning portion, and post-abnormality operation mode; communication
between steering and brake is explicitly one example of a malfunctioning
portion.

The patent permits a two-bit numerical representation for a fail class but does
not assign particular binary values to those four states. Independent Toyota
diagnostic vocabulary closes part of that gap: `DRS_P5` DID `0x100A DRS Fail
Class` is stored as u8 but has valid values only `0..3`, with `0 = steering
control request executable`, `1 = reserved`, `2 = steering control request not
executable (temporary)`, and `3 = steering control request not executable (with
failure decided)`. The same enum appears in rear-steering P6/P6F. This does not
prove the F33 lateral fail-class coding, but it makes `2` versus `3` a strong
Toyota-family temporary-versus-confirmed-failure oracle.

A deeper read of Toyota US20230166772A1 makes the source-suppression
lesson more specific. In its main embodiment PCS continues sending its
kinematic plan and application ID; a different application sends the motion
manager a separate invalidation request. The manager latches that policy,
receives PCS normally, but excludes only PCS from the ordinary arbitration
input. While that state is active it separately returns **request rejection
information** to PCS so PCS can avoid interpreting repeated non-selection as a
system abnormality. A distinct cancellation request restores ordinary
arbitration. Toyota explicitly generalizes the policy from literal invalidation
to a higher-priority request and extends the same architecture to steering
plans including LKA/LTA.

That is materially different from dropping the complete protected `0x08A`
publication. On this Camry, LTA/LDA/LCA/PDA/PCS are **FRC-resident feature
applications** and their ownership state is selected inside the FRC application
before `0x08A` is published. A healthy feature handoff therefore preserves the
FRC's request egress and changes the selected application ID on that egress;
complete FRC request loss instead exercises Brake/FRC communication/request-loss
supervision.

The patent-guided GTS vocabulary is now resolved more tightly. **`PCS Rejection
Request Determination Based On Functional Safety`** is a P6 ADCU DDR
freeze-frame field at `DID$20D4-byte16-bit$FF`; the same packed snapshot has
**`Arbitration Result (Vertical ID Value)`** at byte 25. Its wording is
conceptually closer to the requester->manager rejection/priority decision than
to the manager->PCS feedback signal, so it must not be used as proof that we
have found the latter. Separately, P6 Hybrid/EV PCM RoB rows pair **Required
Driving Force Lower/Upper Limit ID** with **Driving Force Lower/Upper Limit
Request Rejection Factors** in four consecutive 8-bit slots. These are strong
successor-generation semantics, not exact F33 fields.

Exact P5/TSS3 independently exposes priority vocabulary—most notably
`5280_7 TSS acceleration request low priority flag`, PDA priority-request
records, and FRC_P5 `0x1B06 ISA Speed Change Priority Request (Upper Limit)`.
For lateral, the missing object is now specifically the **FRC-internal
eligibility/priority/owner state** that chooses which feature populates generic
`5282`; any intentional-rejection feedback to the losing feature can likewise
remain internal to the FRC application. We should not keep looking for a
separate external lateral-client policy PDU at Brake without new evidence.

A transition-aligned scan of the retained 12-route native road corpus tightens
that boundary. All **473** observed `0x08A` lateral-request-ID transitions are
followed by the identical old-ID -> new-ID transition on `0x081` within
**42.893 ms**; none is unmatched within 100 ms, and the high-volume route
subset has no request/result-ID mismatch lasting 50 ms. Direct nonzero client
handoffs occur without an ID0/request-loss gap: there are 28 ID18 SDG/PDA-SA ->
ID11 LTA/LCA transitions plus rare ID11 <-> ID4 LDA transitions. In a clean
route-3c ID11 -> ID4 example, `0x08A B20:B24` changes only
`40 0B 10 20 64 -> 40 04 10 20 64` at the first switch sample; `0x081`
retains ID11 for one result cycle, then publishes ID4 with the newest ID4 angle
39.773 ms later while B11 remains `0x04`. Thus healthy wire-level mismatch is
bounded as result-publication latency, not a sustained rejected request.

The ownership boundary is inside the FRC application. LDA `5531/550D`, LTA
`5631/560D`, LCA `5681/5685/568E`, and PDA
`5A09/5A0A/5A0D/5A0F`/`5D8D` are feature-local FRC state/request surfaces;
those functions can be enabled simultaneously. The FRC state machine selects
the current lateral owner and writes the generic `5282` request, whose first
external representation is protected `0x08A`. Brake then returns downstream
result/status through `5285/57DE` / `0x081` and generates the actuator-side
target path. The best passive discriminator is therefore a natural FRC feature
handoff or `240E LCA Reject` capture containing feature-local objects and
`5282` together—not a search for multiple competing lateral requests at Brake.

The September-17 faulted e9/ec/ee routes supply the complementary negative
control: native request/result traffic remains alive with request ID0/result
ID0 and B11=`0x04`, while B13 remains `0xC0` (candidate lateral fail class 3).
So request-loss, application handoff, and lateral failure-decided are already
three distinct observable states.

See
[`../architecture/toyota-request-invalidation-us20230166772.md`](../architecture/toyota-request-invalidation-us20230166772.md).

The strongest exact-Camry candidate is now Brake-owned, ordinary-P5-SecOC-shaped **`0x081 B13`**.
Its low six bits were already recovered as Toyota Operation-FFD `5285` arbitration-result
lateral ID. Two healthy pre-brick controls never set B13 bit6: route
`00000045--805b7ca6ab` has 29,497 native `0x081` frames with B13 `00` (18,424),
`0B` (11,007), and only 66 transient `80`; an independent Sep-4 control likewise has
zero bit6 assertions. In dead-EPS route `000000d4--327b2c4bb8`, B13 is **`C0` on
13,496/13,620 frames** and `80` on the remaining 124. Replacement-rack post-bootstrap
routes `e9`, `ec`, and `ee` contain **83,286/83,286 `0x081` frames at B13=`C0`**.
Sep-10 working route `8d` is likewise `C0` on 22,128/22,128 frames, while later
same-build route `93` is `00` on 14,355/14,355 even though its cruise-state traffic
still contains `0x251=E0` unavailable and conventional `0x90` latch states.

The deeper patent/GTS join changes the leading interpretation of B13. Do
**not** name B13 bit6 alone `lateral control system unachievable`. Instead, the
stronger structured hypothesis is:

```text
B13[5:0] = arbitration-result lateral application ID   (already recovered)
B13[7:6] = two-bit lateral fail class                  (candidate)
```

That packing explains the retained values unusually well. Healthy `00`/`0B` have
high bits `00`. The rare healthy transient `80` has high bits `10`.
Dead-EPS traffic contains `80` and then overwhelmingly `C0` (`11`), while the
post-bootstrap faulted routes remain at `C0`. Toyota's independent `DRS Fail Class`
enum assigns value `2` to temporary steering-request non-executability and value `3`
to non-executability with failure decided, exactly the semantic progression that
`0x80 -> 0xC0` would represent if the high two bits are the lateral fail class.

This remains **unproved**. US20230082947A1 does not assign binary values to its four
semantic states, and successor `ADCU_P6` exposes `0x1ED3 Lateral Control ID of Arbitrated Result`
as a raw full u8 without decomposing the high bits. The decisive proof remains a
synchronous `5283_1` / raw-`0x081` capture or an exact F33/P5 decoder join.
Route `93` still proves that `C0` is not the persistent DRCC latch itself:
B13 can return to `00` while higher-level cruise remains unavailable.

A 2026-09-18 re-read of the retained raw rlogs turns that structural hypothesis
into a much stronger **state-transition** result. Across healthy routes
`37/3b/3c/3d/3e/3f/45`, 871,888 logged `0x081` observations contain only
high-two-bit classes `00` and `10`: `00` on 871,642 observations and `10`
on 246 observations confined to four cold-start episodes. No healthy observation
uses `01` or `11`. Those four startup episodes hold `B13=0x80` for
approximately 0.87--0.95 s and then clear to an ordinary `0x00` result.

Dead-EPS route `d4` captures the complementary transition. Its first
`0x081` appears with `B13=0x80`; with **zero `0x030` for the entire route**,
that state persists for 3.725304 s and then changes once to `0xC0`, where it
remains. The immediately adjacent 28-byte application payloads are byte-identical
except for B13 (`80 -> C0`); the security trailer changes normally. In a +/-2-s
window around that transition, `0x08A` remains lateral ID0 / pinion 0,
`0x081 B11` remains `0x04`, B13 low6 remains 0, and the sampled
`0x0D7/0x025/0x251` states do not step at the boundary. Dead-EPS routes
`d0/d1/d2` contain 9,882 / 5,873 / 9,104 `0x081` observations respectively,
all `B13=0xC0` and zero `0x030`.

The healthy cold starts provide a second independent timing join. In routes
`3c/3d/3f/45`, the recovered EPS `0x030 B6[0]` driver-torque-invalid gate
starts asserted and clears shortly before the Brake result returns healthy:
B13 clears **39.215 / 20.779 / 40.711 / 19.856 ms** after B6[0] clears,
respectively. `0x030 B6[2]` and B16[0] are already clear at those transitions,
while B19[0] remains asserted, so B6[0] is the only one of those recovered EPS
status bits with the observed transition ordering. This is a strong temporal
join, not proof that B6[0] is the sole steering-reliability input.

This also changes the interpretation of the valid stale-`0x030` bridge negative.
The exact repeated frame has B6=`0x01`: it continuously reports
**driver torque invalid** while it is being replayed. The experiment therefore
proves that raw `0x030` **presence** is insufficient, but it does not isolate
stale SecOC freshness as the only failure mechanism and does not test continuity
of a semantically healthy EPS status. The first changed/native application-return
frame in the later unproven early-`0x030` run has B6=`0x09`, so B6[0] is still
asserted there as well. Payload validity/reliability state and freshness remain
confounded until a fresh accepted healthy-status publication is observed.

This creates a concrete suppression experiment but rules out the naive version.
`0x081` is ordinary-P5-SecOC-shaped (`FV4||MAC28` candidate), so a B13 replacement
must not assume acceptance without reproducing the native tag; dropping the complete
frame risks replacing `X2400` with a communication fail-safe. The restored Toyota-B topology also observes Bus 4 on unsplit Panda bus1,
so the production harness cannot suppress the native `0x081` in-place without another
inline path / the prior Bus-4 relay repin. The command-5 probe now exposes passive
`verify-native-081`, which captures stock `0x081 + 0x00F` and tests candidate DataID
`0x0081` by asking EPS ICU-S slot 4 to reproduce the native MAC28 without transmitting
anything. A positive live result proves that candidate domain and is the cryptographic
prerequisite for a **selective `C0 -> healthy-result` re-signing**
experiment. It still does not solve the first programming-bootstrap interval before the
resident exists; preventing that first bad publication or eliminating application
downtime remains the preferred architecture.

The decisive onset capture should therefore sample **`5283` together with
`5285/57DE`, raw `0x081`, FRC `1905/1906`, and Brake `102D/102F`** across the
first EPS application outage. If `5283_1` changes before/with `0x081 B13=C0`,
that joins Toyota's named fail class to the network symptom. If `5283_1` stays
healthy while B13 becomes `C0`, the result ID is a different state and should
not be filtered as though it were the manual's unachievable signal.

Retained comparison:
`targets/camry-2026/raw-20260917/brake-frc-081-fault-status/`.

**Retained-log coverage:** some useful healthy/faulted baselines already exist, but not
the decisive post-bootstrap Hybrid state. The Aug-26 exact-car cruise-oracle captures
sample FRC `0x1905=8080` continuously across MAIN/RES+/SET-/CANCEL/distance exercises;
`0x1906` is normally `e080e0008000` with only the expected momentary switch-bit changes,
and its ACC-not-available byte remains clear. The same session records Brake `0x102F =
f700fd007c00a9000000`, decoded as `EPS/Steering Control Actuator ECU Communication =
Normal`. Sep-1 repeats that exact `0x102F` value before, during, and after deliberate FRC
normal-Tx suppression while every named Brake communication-open item stays `Normal`.
Yet after the broader source-isolation campaign the FRC itself remains in a disabled/
invalid feature state (`0x1501=0101`, `0x1601=01010000`, `0x1703=f020`, `0x1705=ff3a`)
after ordinary traffic is restored, demonstrating that a higher-level feature/fail-safe
state can outlive transport restoration and ordinary Brake communication-open state.
No retained structured capture contains FRC `0x1903`, Brake `0x102D`, or Hybrid RoB
DIDs `0x55FE/0x55FF`; an address-aware scan of retained NDJSON finds no Hybrid
`0x7D2/0x7DA` `AB01/11` RoB transaction. The Sep-1 `AB11/12/13` capture is FRC Operation
FFD only. Sep-10 working-steering artifacts retain the DRCC-unavailable outcome but no
corresponding diagnostic/RoB snapshot, so `Suspend` versus `Abnormal Stop` cannot be
recovered retroactively from those files. Later dead-EPS routes do preserve the CAN-side
consequence (`0x251=0xE0` unavailable; a successful latch is conventional `0x90`), but
not the internal Hybrid/FRC/Brake cause.

Production deployment must therefore either prevent the peer fail-safe/latch from
being entered or recover a deeper peer state than DTC memory. The current leading
path is a nondisruptive application-context resident installation/control-transfer
mechanism that never takes the EPS scheduler and normal CAN publishers offline.
Shortening the existing bootloader path remains useful as a timing discriminator,
but the timing boundary must be stated correctly. In the retained Aug-27 stock-handoff
run, boot F181 was present at `00:30:56.232`, the four-block 4-KiB payload completed at
`00:30:56.779`, FF00 was sent at `00:30:56.796`, and application F181 reappeared at
`00:30:57.219`: **987 ms from boot-endpoint observation to application identity return**,
including 547 ms to complete the payload and 423 ms from FF00 to application F181. The
host's 700-ms extended-session settle occurs before the programming request and is not
therefore proven EPS-CAN downtime. The decisive measurement is still the physical
last-normal-EPS-Tx → first-normal-EPS-Tx gap during bootstrap.

A separate Sep-11 parked discriminator already exists for the other obvious
continuity hypothesis: while native `0x030/32` is absent, replay retained stock
`0x030` at 100 Hz, clear FRC U0131, and observe `0x1903/0x1905/0x1906` plus
`0x251`. **No live result artifact exists for that post-latch probe.** Because `0x030`
is an EPS-owned SecOC transmit PDU, replaying old captured frames is only a bounded
test of peer tolerance to stale protected traffic.

The stronger prevention experiment is now packaged separately in the unified F33
field kit. On a **fresh ignition cycle in NRTD/Park**, the bridged installer requires a
healthy pre-bootstrap FRC state (`0x1903` DRCC mode, `0x1905` permission allowed,
`0x1906` ACC-not-available clear), enters the exact EPS DEFAULT→EXTENDED preparation,
then captures the final genuine **bus1** `0x030/32` immediately before application
`10 02`. It repeats that one exact protected frame at 100 Hz on the same unsplit bus1
while the EPS application is absent, performs the normal authenticated 4-KiB resident
bootstrap, and keeps replay active until the exact application F181 has returned **and
a new native bus1 `0x030` has been observed**. It then stops replay and rereads the FRC
oracles without any DTC clear. The field-kit command
`bringup-stale-030-bridge` refuses to continue to READY qualification unless FRC cruise
permission remains allowed and ACC-not-available remains clear. This deliberately tests
whether message-presence supervision can be kept alive by stale authenticated-looking
traffic; it does not assume the FRC accepts the repeated SecOC freshness/MAC and is not a
production keepalive design.

The first live attempt with kit source `474222b0` is explicitly **invalid**, not a
negative stale-replay result. The stock functional-mailbox preflight passed, but the
shared programming helper's boot rediscovery called `rediscover_route()`, which re-applied
ELM327 safety after the bridge thread had started. ELM327 then rejected every host-created
CAN-FD `0x030`; the installer caught `safety_tx_blocked 0 -> 125` and failed closed. The
corrected bridged handoff therefore never calls route rediscovery during the outage. It
keeps allOutput ownership, sends application `10 02`, and polls exact boot F181 only on
the already-qualified stock Toyota-B bus1 route. This preserves the diagnostic physical
route without changing Panda safety while `0x030` replay is active. The invalid attempt
is retained under `targets/camry-2026/raw-20260917/stale-030-bootstrap-invalid/`.

The corrected `7165bde9` run is a **valid negative** for stale `0x030` presence as the
complete prevention mechanism. The fresh-cycle NRTD baseline was healthy:
`0x1903=01`, `0x1905=8080` (Cruise Control Permission allowed), and
`0x1906=e080e0008000` (ACC Not Available clear). The tool captured 88 native bus1
`0x030` frames and repeated the final genuine frame
`000000002b000164000020002d420000000000010000000c0000000014ff61af`
at nominal 100 Hz across the outage. It sent 129 bridge frames with zero missed slots,
zero Panda TX blocks, zero CAN TX loss, and no bus-off; application F181 returned and a
new native `0x030` resumed 1293.294 ms after the last pre-handoff native frame. No DTC
clear occurred. Post-bootstrap `0x1903` and `0x1905` remained `01/8080`, but
`0x1906` changed to `e080e0008080`: **ACC Not Available asserted despite the stale
100-Hz bridge**. This rules out simple raw-message-presence supervision as sufficient.
It does not by itself distinguish receiver rejection of stale SecOC freshness/MAC from
payload/state validity or a separate private/non-Panda-visible EPS startup dependency.
The replayed frame itself has B6=`0x01`, so the recovered driver-torque-invalid gate
remained asserted throughout the bridge; the 2026-09-18 startup chronology independently
shows healthy B13 recovery 20--41 ms after that gate clears in four cold starts. Thus the
valid negative closes **message presence only**, not fresh/healthy `0x030` continuity.
Healthy exact-Camry captures show `0x030` at ~103 Hz on bus1 while all four other exact-F33 normal-Tx siblings
`0x351/0x394/0x4A3/0x4C8` are absent there. Exact-F33 Ghidra xrefs further show every
recovered `ICUSCMD` access in application crypto-driver code (`0x8A26A..0x8AECC`) and
**no boot-area (<0x9200) `ICUSCMD` xref**, so the existing bootloader does not expose a
recovered command-5 signing path for a fresh-`0x030` bridge. The valid negative is
retained under `targets/camry-2026/raw-20260917/stale-030-bootstrap-valid-negative/`.

The next prevention discriminator is now implemented as a separate exact-F33 kit rather
than being squeezed into the production signer resident. Exact static recovery closes the
native PDU0 path needed for this experiment: startup target `startup_18 = 0x666BC` calls
`0x8ED14`, which initializes SecOC Tx and finally writes `FEBE54F4 = 0xFE01`; before
that state, `0x8ED8E` rejects generated-COM Tx. The formerly uncarved Tx-freshness callback
at `0x903F6..0x90429` is now reproducibly seeded/decompiled and has the exact five-argument
ABI used by profile 0: freshness-value ID 3, full-freshness buffer + bit-capacity pointer,
and transmitted-freshness buffer + bit-capacity pointer. Its lower worker emits the exact
46-bit full freshness and 4-bit transmitted freshness used by `0x030`.

`camry_f33_early030_discriminator_resident.S` therefore replays stock application startup
through `startup_18`, calls `0x4C590/0x4C97A` to build PDU0, advances Toyota's own Tx
freshness through `0x903F6`, builds `00 30 || payload[28] || full_freshness[6]`, invokes
the field-proven synchronous selector-4 command-5 wrapper `0x89BC2`, packs
`FV4 || MAC28`, and submits lower PDU0 through `0x901D2`. It then runs `startup_19`,
`startup_20`, `0x701EA`, enables interrupts, and enters the unmodified stock foreground
loop at `0x66062`. The original resident was 432 bytes in the exact 524-byte retained
high-tail window; the current self-attesting/pre-EI-completion-pump resident is **520/524
bytes** with zero relocations. The staging shell remains inside the 776-byte authenticated
low-stage bound, and the authenticated payload remains the stock-proven 4-KiB RAM envelope.
The live host runner deliberately
keeps the last real `0x030` replay active through boot, stops it on the first different
bus1 `0x030` observed after FF00, immediately probes application F181 to determine whether
the forced frame beat normal DCM readiness, then reads FRC `0x1905/0x1906` with no DTC
clear. The mutation boundary is exactly one protected `0x030`; there is no B6 transmit,
steering actuation, CodeFlash write, or persistent flash mutation. This is a startup-timing
and freshness discriminator, not the production signer resident. A positive result would
justify optimizing the one-shot into the 522-byte signer; a negative result would show
that even one valid fresh `0x030` at the earliest recovered SecOC-ready startup point is
insufficient to prevent the FRC ACC-unavailable latch.

The first live early-`0x030` attempt from `6203caad` is **invalid due to host replay
starvation**, not a result on the ECU hypothesis. The same-process Python bridge sent 155
stale frames but missed seven native 10-ms slots, with a 40.542-ms maximum send gap.
Comma 4 exposes the Panda only over SPI (`usb=[]`, `spi=[3a0007000151343435333330]`).
`PandaSpiHandle` serializes each complete transaction with both an in-process
`threading.Lock` and an OS `flock`; the synchronous UDS/ISO-TP path busy-polls
`can_recv()`, so the bridge thread could starve behind repeated SPI acquisitions. The
error was reached only after the old runner had observed a non-replay `0x030`, application
return, and FRC post-state, but that exception path discarded those partial fields; they
are therefore not authoritative/recoverable for this attempt.

The corrected host architecture moves the stale-`0x030` writer into a separate spawned
process with its own Panda SPI handle, relying on the existing OS `flock` to serialize
whole cross-process SPI transfers. The main receive path additionally yields 1.5 ms after
each complete `can_recv()` transaction so the writer can acquire the kernel lock between
ISO-TP polls. A parked read-only contention stress run exercised 760 main-process SPI
receive polls over 2.2 s while the worker completed 249 scheduled 100-Hz SPI health
transactions: zero missed slots and a 14.539-ms maximum observed completion-to-completion
gap. The live probe still requires `missed_slots == 0` and zero Panda TX blocks; invalid
cadence now persists the already-collected non-replay frame/F181/FRC evidence instead of
throwing it away. The invalid first run is retained under
`targets/camry-2026/raw-20260917/early030-bootstrap-invalid-host-starvation/`.

The next `8c36d5c8` live run is **bridge-valid but not yet a conclusive early-one-shot
result**. The stale bridge sent 156 frames with zero missed slots and zero Panda TX blocks.
Relative to the final real pre-handoff `0x030`, boot F181 appeared at +118.015 ms,
FF00 send completed at +1066.095 ms, and the first non-replay `0x030` appeared only at
+1519.432 ms (+453.337 ms after FF00). An F181 request immediately after that frame already
returned the exact application identity. Post-bootstrap FRC state was `0x1905=8000`
(permission denied) and `0x1906=e080e0008080` (ACC Not Available asserted). However,
the prior stale-only run's first native-return frame has the same startup payload shape, so
the changed frame cannot be attributed uniquely to the explicit resident one-shot. The
old runner also waited through an F181 transaction before stopping stale replay, extending
stale traffic by roughly 42 ms after the first changed frame. This run is therefore stored
as `early030-bootstrap-bridge-valid-oneshot-unproven`, not as a definitive negative on the
one-shot itself.

The follow-up resident keeps a compact 8-byte self-attestation record in the final proven
retained high-tail bytes `FEBFFBF4..FEBFFBFB`: freshness callback RC, command-5 RC,
lower-PDU Tx RC, transmitted-FV byte, and the exact forced `FV4||MAC28` trailer. The host
now stops stale replay immediately on the first changed bus1 `0x030`, before any F181 read,
then RMBA-reads that telemetry and requires the forced trailer to equal the first observed
wire trailer. Only that byte-exact match plus three zero return codes qualifies the
`early_fresh_030` hypothesis as actually exercised.

The first self-attesting `ce8f3b83` attempt closed another missing startup dependency rather
than testing the FRC hypothesis. The host initially failed only because it attempted the
post-startup telemetry SID23 read from default session; the same ignition cycle was salvaged
by rebinding exact application F181, entering EXTENDED, and reading `FEBFFBF4/8` directly.
The retained bytes were exactly `0002ff4000000000`: Tx freshness callback RC `0`,
command-5 wrapper RC `2`, lower-PDU Tx RC `0xFF` (never reached), transmitted-FV byte
`0x40`, and no forced trailer. FRC was already `1905=8000`, `1906=e080e0008080`. Thus
`0x903F6` is usable at the `startup_18` boundary, but the explicit one-shot did **not**
transmit: `0x89BC2` submitted the record-0 command-5 job and exhausted its synchronous
`0xE07` done-flag polling window while global interrupts were still disabled.

The completion path is now closed statically rather than worked around. Exact record 0 at
`0x27DA4` binds adapter `0x88DBC`, async worker `0x88EC0`, and completion callback
`0x89C4C`; `0x89C4C` writes status to `FEBF13BD` and then sets the real done flag
`FEBF13BC=1`. After hardware submit, the stock periodic crypto service `0x88700` invokes
the callback pointer at `FEBF1194`; for this command that pointer is `0x88D04`, whose path
services ICU-S status through `0x8AF10`, copies the result, and propagates completion to
record 0. The resident therefore handles only wrapper RC `2` by keeping its stack and
output buffers alive and calling **stock service `0x88700`** with Toyota's own `0x9C4`
poll bound until the real `FEBF13BC` bit becomes set. It then consumes real `FEBF13BD`
status and proceeds only on zero. It never synthesizes done/status and does not enable
interrupts early. The telemetry read enters EXTENDED only after stale replay has already
stopped, so diagnostic session choice cannot affect the startup timing under test. The
salvaged timeout attempt is retained under
`targets/camry-2026/raw-20260917/early030-pre-ei-command5-timeout/`.

The first completion-pump build (`5896547a`) is also **invalid due to a self-attestation
layout bug**, not an ECU-side negative. Its resident was 520 bytes at `FEBFF9F0`, so the
executable body occupied `FEBFF9F0..FEBFFBF7`, but its eight-byte telemetry slot began at
`FEBFFBF4`. Exact linked disassembly shows `FEBFFBF4` is the final
`dispose 20,{r20-r21,lp},lp` return instruction. The resident wrote telemetry there before
returning and therefore self-modified its own exit path. The host saw no changed `0x030`
within its two-second window. A same-cycle read-only salvage later found exact application
F181 and a healthy FRC (`1905=8080`, `1906=e080e0008000`), but that outcome cannot be
attributed to the intended one-shot because control flow was corrupted. The invalid run is
retained under `targets/camry-2026/raw-20260917/early030-self-overlap-invalid/`.

The corrected resident removes per-stage RC telemetry and is **488/524 bytes**, leaving 36
bytes of real executable headroom. Self-attestation is reduced to the exact four-byte
forced `FV4||MAC28` trailer and moved to `FEBFFBF8..FEBFFBFB`, wholly outside executable
bytes but still inside the proven retained high-tail window. The builder/test now assert
`resident_end <= telemetry_start` and `telemetry_end <= retained_limit`; the host proves the
one-shot only when that nonzero retained trailer equals the first changed bus1 `0x030`
trailer byte-for-byte. If no changed frame appears, the run no longer throws away the
remaining application/FRC/telemetry evidence; it stops stale replay at the bounded timeout,
collects the rest, and marks the one-shot unproven.

**Current execution boundary:** VAR-155 proves the live native profile-2 B6 boundary and
byte-exact local slot-4 signing. VAR-156 then deliberately installed the preserved
native-application trailer on the modified ID11/target/100/100 application: all six samples
reached raw PDU44, generated COM, and the application snapshot. Cumulative stage 5 is
therefore dynamically valid, and the tested application construction is accepted; the old
stage-5 miss was before EPS queue ingress. The later C7 runtime handoff closed the road-control
boundary: primary route `0000008d--a9f348691a` contains 8,333 active angle commands with
8,332 successful Panda returns over 167.289 lateral-active seconds. Its clean 36.105-second
segment-6 witness has 1,799/1,799 successful active returns, commanded/measured response
`r=0.989` at the tested 400-ms lag, low driver torque, no EPS steering faults, and native
`0x08A/0x081` ID0 throughout. Route `00000093--4066e7ae51` independently corroborates the
same build with 893/893 successful active returns and `r=0.997` over 17.92 seconds.
The remaining work is upstream cleanup and broader release/fault qualification, not proof
that the exact development path can steer. VAR-148/CORR-179 close the ID11 composition
semantics statically: accepted B6 is co-modulated inside the ordinary EPS sum, not an
exclusive replacement mode.

**Current physical routing decision (2026-09-18 request-plane supersession):**
the direct-B6 development proof is retained as evidence, but it is no longer the
integration architecture. The production-shaped F33 path uses the measured relay-correct
Toyota-B repin:

```text
Panda bus0: chassis / Brake state, 0x081 result plane, and post-repin EPS diagnostics / MAC-oracle transport (0x7A1 -> 0x7A9)
Panda bus2: FRC source plane, including protected native 0x08A
Panda bus1: radar/object traffic
```

The chain remains **FRC-internal feature-owner selection -> generic request `5282` /
protected `0x08A` egress -> downstream Brake/VMM request arbitration -> `0x081`
arbitration result/status + post-arbitration request generation -> final B6**. Openpilot
now enters at that native request boundary rather than bypassing it with a direct B6
sideband. Do not send `0x08A` to EPS: the EPS contributes only selector-4 command-5 CMAC
service, while comma is the final chassis-bus sender. The EPS diagnostic/oracle route follows the repin too: `0x7A1 -> 0x7A9` is on Panda bus0, not bus1. The September-18 installer/runtime bug that still used bus1 caused both the NRTD/F181 install failure and would have broken the on-road oracle worker; the installer, host worker, Panda TX whitelist, kit manifest, and audited oracle metadata are now all bound to bus0.

**Road evidence checkpoint — ID0/ID11 lateral ownership (pre-final replay gate):**
route `00000135--dc6b4d88c4` (15 copied rlog/qlog segments) is the first moving request-plane
run after the bus/controls-mismatch fixes. It contains 36,036 authoritative native bus2
`0x08A` generations: 30,260 ID0 and 5,776 ID11. While openpilot `latActive=True`, Toyota
spent 2,799 native generations in ID0 (~69.98 s at 40 Hz) and 5,768 in ID11 (~144.2 s).
The old ID11-only host policy therefore left a large fraction of valid openpilot lateral
control time unable to command simply because Toyota's own lane-based application had
selected ID0.

The same route proves comma did reach the request plane. Nine signed ID11 substitutions
were attempted; four were Panda-accepted and appeared downstream as returned bus0 TX
echoes. Those accepted frames differed from their matched native generation only in
`B18:B19` plus the recomputed MAC28; examples include native raw `-12 -> -2`, `-4 -> 5`,
`4 -> 9`, and `12 -> 15`. Thus comma-authored protected `0x08A` lateral requests reached
the chassis side. Five later modified frames were rejected after `latActive` transitions:
while lateral was inactive the proxy had continued exact-cloning Toyota ID11 and Panda
reset its angle-rate baseline to Toyota's native request; CarController independently
reset to measured steering, so the next OP target resumed from a different baseline.

`kai-openpilot@65dcda237` with nested opendbc `f70060d9` corrects both limitations. The
current rule for each native source generation is:

- `CC.latActive` + native **ID0**: promote the request to Toyota's observed LTA/LCA shape:
  set `B21[5:0] 0 -> 11`, replace `B18:B19` with the normal rate-limited openpilot pinion
  target, and set **B24 raw 100 = assist gain 1.00**; preserve B21 high bits, B25 damping,
  B26 request sequence, both longitudinal request tuples, cruise/hold state, FV4 and every
  other application byte;
- `CC.latActive` + native **ID11**: preserve ID11 and replace only `B18:B19`;
- native ID4/ID18/other Toyota applications are never promoted and remain Toyota-owned;
- when `CC.latActive` becomes false, release relay ownership immediately and let stock
  forwarding resume instead of proxying exact frames through the override/disengagement;
- on the next active transition, reacquire atomically; Panda treats the first exact handoff
  clone as a relay witness and seeds its angle-rate baseline from measured steering, matching
  CarController's normal inactive-to-active behavior; and
- every modified generation is signed for the exact observed native freshness generation
  through the EPS command-5 oracle. There is still no N+1/N+2 prediction.

Panda now retains the **six newest** native bus2 `0x08A` generations and accepts each at
most once, **oldest unconsumed first**. This depth covers the measured one-retry oracle
pipeline without allowing host output to skip/reorder source generations. For an ID0
source, the permitted semantic edits are B18:B19, low-six-bit ID0->ID11, **B24=100**, and
MAC28; any other assist gain is rejected. Native ID11 retains its source-real ID and B24.
FV4 must match the exact source generation and ordinary `controls_allowed` plus the F33
angle/rate envelope still apply. The host ownership watchdog is **100 ms**, sized above the
measured ~80-ms lost-response retry gap while remaining bounded. The old C7/B6 sideband
remains blocked in request-plane mode.

**Reset/freshness rule:** `0x00F` and protected `0x08A` are asynchronous publishers. A normal
`RESET_CNT` increment can therefore appear on `0x00F` before the next native `0x08A` stops
carrying the preceding reset-low2/FV4. Latest `0x00F` is not an admissibility oracle for a
particular replacement frame. Panda matches host output to the actual unconsumed native
`0x08A` generation and compares FV4 to that generation directly. The host uses `0x00F` only
to reconstruct the nearby full freshness epoch, resolving the native reset-low2 against
current/adjacent epochs.

The September-19 full-route replay also corrects a more fundamental earlier assumption:
the 8-bit SecOC message counter is **local to each reset-counter epoch**, not continuous
across reset increments. On a source-real reset transition the first `0x08A` generation
uses full message counter **1**; later generations in that same reset epoch increment with
the native B26 sequence. Route `0000013c--4f85421eeb` contains **874** resolved reset
transitions whose first new-epoch frame has message-low2 `1` with zero exceptions. The
complete rule reproduces **9,962** consecutive generations after the first oracle seed and
matches all **19** independent EPS-command-5 full-counter anchors in that route. The older
mixed route `00000135--dc6b4d88c4` contributes **62** independently matched hardware
anchors across 35 reset epochs and agrees with the same reset-local rule. If the first
observed generation in a new reset epoch is not low2 `1`, the boundary was missed and the
host must recover the full counter instead of extrapolating across it. Regression tests
cover both the normal reset-to-message-1 transition and the missed-boundary recovery case.

The path no longer uses the private `ToyotaTss308aId0` / `ToyotaTss308aSignedId0`
rollout Params or a runtime parser rebuild. Exact F33 selects the host path during normal
`CarParams` construction when fingerprint topology contains chassis `0x025` on bus0 and
native FRC `0x08A` on bus2; stock/unrepinned topology therefore remains distinct.
`CarController` keeps the standard 100-Hz angle limiter across native ID0 and ID11 while
`CC.latActive`; ID0 is now an available host carrier because the proxy promotes it to ID11.
Across Toyota-owned ID4/ID18/other applications, or whenever `CC.latActive` is false, the
normal limiter returns to measured steering.

The live post-repin bus0 oracle transport was re-qualified after moving the EPS diagnostic
route from stale bus1 assumptions to the actual repinned `0x7A1 -> 0x7A9` bus0 path. A
100-request production-shaped pipelined run completed 100/100 with resident deltas
+100/+100/+100, zero NRCs, zero RX errors, median RTT 18.073 ms and p95 19.192 ms. One
reply took 34.407 ms; when combined with the preceding frame's completion time, the
source-ordered host-output gap reached 46.237 ms. The former 40-ms Panda replacement
watchdog was therefore too tight for the measured transport. `opendbc@841b2854` raises
that watchdog to 75 ms (three native ~25-ms `0x08A` periods), while the host oracle worker
still fails open independently on signing error or its 120-ms oracle timeout. Parent
`kai-openpilot@e9dcefca1` carries that safety revision.

A later no-steering run (`00000137--2d16ff3a64`) exposed a separate flipped-harness
transport bug after the ID0->ID11 code was deployed. In that route the proxy never armed:
15,493 native bus2 `0x08A` frames were observed (all ID0), including 2,377 while
`latActive=True`, but host `sendcan 0x08A` and ownership-admin `0x777` were both zero.
The oracle worker emitted 4,259 `0x7A1` ISO-TP frames, all Panda-accepted, yet saw zero
`0x7A9` flow-control/private replies. The resident itself remained healthy and signed the
same road domain directly, so the failure was below the oracle protocol.

The root cause was Panda control request `0xE8` (`set_canfd_auto`). On a flipped harness,
logical bus0 maps to physical CAN controller 2 via `CAN_NUM_FROM_BUS_NUM(0)`, but the
handler wrote `bus_config[req->param1].canfd_auto` directly. Thus pandad's F33 request to
keep logical bus0 host diagnostics classic disabled auto-FD on physical CAN0 instead of
the controller actually carrying logical bus0. Direct Panda tools masked the bug because
the Python constructor disables auto-FD on all three controllers. `panda@21701e3f` fixes
`0xE8` to update `bus_config[CAN_NUM_FROM_BUS_NUM(logical_bus)]`; parent
`kai-openpilot@c20b906cd` carries that Panda revision while retaining `opendbc@f70060d9`.
Live verification on the flipped vehicle under normal Toyota safety produced 67 requests
in an 8-second sample, 66 `30 00 28` flow-control responses and 64 completed `07 C9`
private replies, with `safetyRxChecksInvalid=false` and no Panda faults. This is the
required steady-state oracle path; no ELM/allOutput driving mode or relay override is used.

Route `0000013b--39a7512088` exposed one further host-freshness bug after the transport
fix. The route contained 21,561 native `0x08A` generations and 3,490 native generations
while openpilot `latActive=True`, but host `sendcan 0x08A` remained zero. Oracle transport
was healthy (115 completed private `07 C9` responses), and offline reconstruction found a
valid recovery match plus verify match, so crypto and counter reconstruction were not the
problem. Qualification was later destroyed by a real ~3-second native delivery gap at
1003.725 s: native `B26` jumped `26 -> 5` while reset advanced `0x48D8 -> 0x48E1`.
The first post-gap `0x08A` frames arrived before the matching `0x00F` frames in the same
backlog. The old code immediately restarted recovery from that first stale-sync frame;
`resolve_epoch()` therefore selected nearby reset `0x48D9`, and every recovery probe used
the wrong epoch even though `0x00F` caught up to `0x48E1/0x48E2` immediately afterward.

`kai-openpilot@84b254702` removes that premature recovery. On a tracker discontinuity the
proxy now fails open, drops the tracker, and waits for the existing eight-consecutive-native
cadence gate before starting recovery again. This uses the then-current `0x00F` state
instead of guessing forward epochs. Replaying the exact route through the patched proxy
starts post-gap recovery at native `B26=13`, reset `0x48E2`, candidate message 3; the old
runtime started from stale reset `0x48D9`. The regression suite covers this exact
sync-after-native backlog ordering. After deployment/reboot, parked runtime observation
showed no repeated `0x7A1` recovery traffic over 12 seconds, confirming recovery had
completed and the proxy was idle rather than looping.

Route `0000013c--4f85421eeb` is the first drive after the native-gap recovery fix and
finally reaches the ID0->ID11 path. It contains 10,484 native source `0x08A`, all ID0;
the host emitted 29 downstream `0x08A` frames: 20 exact clones and 9 promoted ID11.
Panda accepted 8 exact clones and 2 promoted ID11, rejecting 12 exact clones and 7
promotions as ownership repeatedly collapsed. All retained `0x081` frames stayed at
`LATERAL_RESULT_ID=0`; the two accepted promoted frames occurred at ~15.6 mph while
`steeringPressed=true`, so they are not a clean downstream-arbitration rejection test.
Their source envelopes already carried the normal Toyota ID11 companion shape
(`B20=0xC0`, `B22=0x10`, `B24=100`, `B25=0`), so no additional request-byte mutation is
justified from this route.

Two host-side failures explain the collapse. First, CarController continued advancing its
normal rate-limited angle while the request proxy was still qualifying/rearming. Panda's
atomic handoff correctly seeded its safety baseline from measured steering, but the first
post-handoff host target could already be several degrees away (for example measured
~ -5.6 deg versus controller output ~ -9.7 deg), causing immediate angle-rate rejection.
`opendbc@ad23a31b` adds only one ownership input to the existing F33 controller: while the
request proxy does not actually own `0x08A`, the angle limiter remains pinned to measured
steering; after ownership is confirmed it resumes the normal 100-Hz limiter from the same
baseline. `kai-openpilot@f5842b9ff` supplies that existing proxy-active state to
CarController before `CI.apply()`; no second permission state machine is introduced.

Second, the EPS command-5 transport occasionally loses a single private `0x7A9` response
while subsequent transactions succeed normally. In the first active interval, seq 11/12
completed in ~25 ms, seq 13 had no visible response, then seq 14..17 again completed in
~23-27 ms. The old proxy waited 120 ms on that one missing sign response, exceeding the
75-ms Panda ownership watchdog, then fail-open flushed stale exact clones which Panda
correctly rejected. `kai-openpilot@f341259c0` gives sign jobs one bounded retry: after
40 ms without a response, the exact same native-generation signing domain is resubmitted
immediately under a fresh private transaction sequence; only a second miss fails open.
Recovery/verify timeout policy remains unchanged. This stays within the observed command-5
RTT distribution and preserves exact source generation/order without loosening angle or
ownership safety limits.

**September-19 production-path replay gate — no road test until this passes:**
`kai-openpilot@71703da35` converts the retained road corpus into an executable integration
gate at `openpilot/tools/replay/toyota_f33_request_plane_replay.py`. The tool does not
replay prior host output. It feeds source-real CAN and recorded `CarControl` through the
**current** `CarInterface`/`CarController`, current authenticated request proxy, and the
actual C Panda Toyota safety hooks (`rx`, `fwd`, `tx`, timer/watchdog). Host TX accept/reject
echoes are fed back to the proxy exactly as the board does. The oracle stub is not allowed
to invent freshness: it reconstructs the native full counter independently per reset epoch
from source B26/FV4 phase and cross-checks that truth against the route's retained real EPS
command-5 responses before replay begins. Route `13c` supplies 19 hardware anchors; route
`135` supplies 62. A wrong reconstructed epoch/message counter therefore fails the gate
rather than being hidden behind a synthetic CMAC.

The strict authority invariant is now explicit: **while `proxy.active` is true, every host
lateral `0x08A` is authenticated ID11; there is no exact-ID0 timeout fallback.** The only
Toyota frame admitted during an owned interval is the single exact atomic-handoff witness;
pending blocked source generations are discarded at release rather than replayed as Toyota
before the relay changes owner. The replay fails on any
Panda TX rejection, native `0x08A` leak while owned, host non-ID11 authority frame, safety-RX
invalidity, freshness/sign mismatch, unexpected arm/release cycle, or unresolved oracle
truth.

That gate exposed and fixed three remaining structural defects before another road drive:

1. **Reset-local full message counter.** `NativeFreshnessTracker` now sets message counter
   `1` on a source-real reset epoch transition and increments only within the epoch. A missed
   boundary forces recovery. The prior cross-reset `message += B26 delta` model was wrong.
2. **Oracle sender phase drift.** Scheduling the next command-5 request as `now + 25 ms`
   accumulated every thread wake delay. After hundreds of generations a valid signed frame
   could be ~112 ms / four native generations old, outside Panda's three-generation matcher.
   The sender is now phase-locked to the previous deadline; only a true overrun resets phase.
3. **Authority-boundary races.** The proxy now mirrors the same source-real authority inputs
   Panda uses: native `CRUISE_OPERATING_LATCH` and fresh `CarState.brakePressed`, in addition
   to `CC.latActive`. Brake reached Panda about 4 ms before one rejected host frame while
   controlsd's `latActive=False` arrived ~1.5 ms later. The proxy now releases immediately on
   that fresh brake boundary, clears queued/in-flight sign work from the ended authority
   interval, and refuses re-arm until the native cruise latch is valid again. Logical
   `proxy.active` is cleared before exact restoration frames are emitted.

The final clean replay results are:

- **`0000013c--4f85421eeb` (all native ID0):** 51,179 replay events, 10,484 native
  `0x08A`, 875 resolved reset epochs, 19 hardware oracle anchors, 2 authority windows,
  **1,190 modified host ID11**, 1,193 native generations blocked while owned, **0 native
  leaks, 0 Panda TX rejects, 0 safety invalidity, 0 freshness/sign failures**.
- **`00000135--dc6b4d88c4` (mixed native ID0/ID11):** 178,359 replay events, 36,036
  native `0x08A`, 3,004 resolved reset epochs, 62 hardware oracle anchors, 8 authority
  windows, **8,434 modified host ID11**, 8,559 native generations blocked while owned,
  **0 native leaks, 0 Panda TX rejects, 0 safety invalidity, 0 freshness/sign failures**.

Fault injection is part of the same gate. `--drop-sign-response N` drops the Nth
first-attempt command-5 sign response and requires that exact source generation to be retried
under authority. Route `13c` passes injected losses at sign generations **100, 500, and
1000**; route `135` passes **500, 2000, 4000, and 8000**. Every injected run preserves the
normal arm/release count and reports zero rejects/leaks/freshness failures. Representative
commands are:

```text
python openpilot/tools/replay/toyota_f33_request_plane_replay.py /Users/kai/dev/inspect/logs/0000013c--4f85421eeb
python openpilot/tools/replay/toyota_f33_request_plane_replay.py /Users/kai/dev/inspect/logs/0000013c--4f85421eeb --drop-sign-response 500
python openpilot/tools/replay/toyota_f33_request_plane_replay.py /Users/kai/dev/inspect/logs/00000135--dc6b4d88c4
python openpilot/tools/replay/toyota_f33_request_plane_replay.py /Users/kai/dev/inspect/logs/00000135--dc6b4d88c4 --drop-sign-response 4000
```

The request mutation is intentionally narrow but now includes the missing Toyota assist
request. Engaged native ID0 periods already carry the same gate state used by lateral
requests (`B22=0x10`, B20 predominantly `0xC0`/sometimes `0x40`, B25=0), but **ID0 B24 is
0 while native LTA/LCA ID11 uses B24=100**. Therefore ID0->ID11 promotion modifies exactly
B18:B19, B21-low6, **B24=100**, and MAC28. Native ID11 continues to preserve its source-real
B24. No other companion-byte synthesis is introduced.

**Downstream low-speed arbitration evidence:** the retained September-7 Camry corpus contains
504 source-real native ID4/LDA request generations. Joining them to fresh `0x081` and
`CarState` shows Brake/VMM selecting `LATERAL_RESULT_ID=4` on **318/504** frames, including
source-real selection at essentially **0 mph** and throughout single-digit vehicle speeds.
The ID4 request carries the same relevant companion gate shape used by native ID11
(`B20=0xC0`, `B22=0x10`, B24=100, B25=0). Result-ID0 intervals coexist with driver-steering
activity, which is consistent with arbitration/override rather than a global speed floor.
The September-6 corpus independently contributes 50 additional native ID4 generations
(49/50 selecting result ID4, albeit at ~74 mph).

Natural ID11 is still only observed down to ~27.1 mph in the retained source-real routes;
therefore the corpus does not directly prove that Brake has no *ID11-specific* low-speed
rule. It does, however, rule out a generic downstream lateral-control minimum-speed gate:
the Brake/VMM request/result layer is demonstrably capable of selecting lateral authority
at standstill. Combined with the recovered architecture in which FRC chooses LTA/LDA/PDA
before protected `0x08A` egress, this strongly places Toyota's ordinary LTA speed floor in
the upstream FRC feature-selection policy rather than in the generic Brake/VMM lateral
arbiter. That is the exact policy boundary the ID0->ID11 host substitution is intended to
supersede.

**September-19 limp-run closure (`00000140--7bec8dde3f`):** this route finally proves the
low-speed downstream path itself. It contains 24,391 source bus2 `0x08A` generations, all
native ID0. During the ~18-mph active interval the host produced 31 promoted ID11 frames;
27 were Panda-accepted, and **26/27 fresh downstream `0x081` results selected
`LATERAL_RESULT_ID=11`**. The result pinion reference followed the host request, and measured
steering moved in the requested direction. Therefore Brake/VMM accepts and selects the
comma-authored ID11 at ~18 mph; the prior "limp" behavior was not a downstream low-speed
veto.

The same route exposed two real remaining defects. First, every selected promoted ID11
carried **B24=0**, inherited from native ID0, while the retained Toyota corpus shows native
LTA/LCA ID11 with **B24=100 / assist gain 1.00**. `kai-openpilot@7654d1cc0` now builds
ID0->ID11 with B24=100, while nested `opendbc@43754107` requires exactly B24=100 for that
promotion and preserves source-real B24 on native ID11. Second, individual private `0x7A9`
responses are occasionally absent. In the limp interval, seq22 was lost while seq23
succeeded; the source-order retry of seq22 completed only after the source generation had
aged to roughly 80 ms, causing the old three-generation/75-ms Panda contract to reject it
and collapse ownership. The current safety contract retains six generations oldest-first
and uses a 100-ms ownership watchdog, covering this measured retry geometry without
permitting source reordering.

Request-plane failure semantics are also changed. A **Panda TX reject, arm/admin reject,
handoff-clone reject, or second sign failure no longer destroys SecOC qualification**.
Those events end only the current authority interval, clear its queued/in-flight sign work,
release stock forwarding, and automatically re-arm on the next eligible native generation
using the still-valid freshness tracker. Only genuine native freshness loss/CAN invalidity
forces full recovery. Requalification itself now clears stale in-flight oracle jobs so old
transactions cannot occupy the sender window. Every real request-plane failure increments a counter and records an exact reason in
`logMessage/errorLogMessage` as `toyota_f33_request_plane_failure`. The original visible
implementation incorrectly reused `CarState.steerFaultTemporary`, which can generate a
soft-disable and therefore convert a brief authority drop into an approximately one-second
lateral limp interval. `kai-openpilot@dfc2c6662` replaces that with the additive generic
`CarState.steerFaultTemporarySilent` field from `opendbc@6dc2b5d3`; `CarEvents` maps it only
to the existing warning-only `steerTempUnavailableSilent` event. The driver still sees a
steering warning, but the notification itself no longer changes `latActive` or control state.

The updated production replay gate now accepts `--oracle-response-delay-ms`. At **30-ms
successful oracle latency** the new code passes all three retained drive shapes with zero
Panda TX rejects, zero native leaks, and zero freshness/sign failures: route `140` sustains
1,906 modified ID11 generations over two authority windows; route `13c` sustains 1,189;
route `135` sustains 8,429 over eight authority windows. Injected dropped sign responses
(`140` #500, `13c` #500, `135` #4000) are retried under authority and all three replays
still pass. The dedicated unit regression also proves an explicit active-host Panda reject
preserves qualification and begins a fresh atomic handoff on the next native generation.

Deployed heads after this closure are `kai-openpilot@7654d1cc0`, nested
`opendbc@43754107`, and `panda@21701e3f`; the Panda firmware was rebuilt/flashed and its
live signature matched the new image before the comma reboot. The first boot recorded one
visible `oracle_recovery_failure` during startup while the resident was not yet answering;
it subsequently requalified normally. A later lease-free parked observation showed Toyota
safety param 53833, valid RX checks, no Panda faults, no active failure warning, and no
unexpected request-plane traffic while parked.

**September-19 sustained-steering route (`00000142--2e058e3fef`):** after the B24=100 and
same-drive recovery changes, this 11-segment route proves sustained low-speed physical
steering and also quantifies the remaining interruptions. It contains **24,914** native
bus2 `0x08A` generations, all ID0. The host emitted 1,422 promoted ID11 frames with
**B24=100** plus 36 exact clones; Panda returned **1,392 accepted ID11** and 30 rejected
ID11. Downstream Brake/VMM published **1,256 `0x081` result-ID11** frames. Accepted-ID11
runs span roughly 13–29 mph and repeatedly last 1–3.3 seconds; measured steering follows
the selected pinion reference, so the low-speed request-plane actuation path is now directly
observed, not inferred.

There are **26 unique request-plane failures** in the route (each cloudlog event appears in
both `logMessage` and `errorLogMessage`, so raw log-message count is doubled): 15
`host_08a_rejected`, 9 `oracle_sign_failure`, one `handoff_clone_rejected`, and one startup
`oracle_recovery_failure`. All transient failures retain `qualified=true`, confirming that
the new same-drive recovery semantics work. In the old notification build, however, every
failure's one-second `steerFaultTemporary` pulse frequently became
`steerTempUnavailable/softDisable`; the next accepted ID11 therefore appeared about
**1.05 s** after most failures. That delay was notification-induced, not requalification.

The host-frame rejects were a second independent timing issue. Matching every rejected ID11
to its source generation shows source ages of **120.3–170.7 ms** and lags of **4–6 native
generations**. Accepted frames routinely reached 70–140 ms / lag 2–5. The stream was
therefore operating with essentially no backlog margin. Separately, the actual source
`0x08A` intervals are not a fixed 25 ms: mapped consecutive generations cluster around
20/30 ms and reach ~34 ms. CarController consequently produces legitimate adjacent source
samples up to **10 raw angle counts = 0.573 deg** apart. The earlier Panda request-plane
angle envelope assumed at most three 100-Hz controller ticks and could allow only about
eight raw counts in the tighter direction; three clean serialized-replay rejects were
exactly this one-count/two-count mismatch. `opendbc@6dc2b5d3` changes only the F33 request-
plane Panda envelope to the exact **four-controller-tick** bound: 0.60/0.30 deg up and
0.72/0.52 deg down (low/high-speed lookup). The 100-Hz CarController limit itself is
unchanged and remains tighter.

The nine real `oracle_sign_failure` episodes identify the remaining backlog source. The
successful command-5 RTT distribution across this route is **mean 22.30 ms, median 22.45
ms, p95 31.91 ms, max 39.13 ms**. The old worker nonetheless launched a new sign request
at ~25-ms cadence even when the preceding one was still outstanding. In every sign-failure
episode the missing request still received ISO-TP flow control (`30 00 28`), but its private
`07 C9` response disappeared while a newer request was in flight; the retry was then also
sent while that newer transaction remained outstanding. `kai-openpilot@dfc2c6662` makes
**active sign jobs strictly one-in-flight and response-driven**. A successful response wakes
the sender immediately, so the observed 22.3-ms mean service time provides real catch-up
capacity against 25-ms native cadence instead of accumulating source age. Recovery/verify
retain their already-qualified pipelined startup transport. Sign timeout is raised narrowly
from 40 to **45 ms**, just above the observed 39.13-ms successful maximum.

The updated replay gate reproduces the full route through current CarController, proxy, and
C Panda safety. With serialized signing and a conservative fixed **24-ms** synthetic oracle
latency, route `142` passes with **1,541 modified ID11**, 1,570 owned native generations,
zero native leaks, zero Panda TX rejects, zero safety invalidity, and zero freshness/sign
failures. The same route also passes an injected dropped sign response at generation 500,
which is retried under authority. Older routes `140` and `135` continue to pass under the
same serialized-signing model. Unit gates after this change are **40 proxy/car-event tests**
and **275 Toyota/Panda safety tests + 8 subtests**.

The resulting deployed heads are `kai-openpilot@dfc2c6662`, nested `opendbc@6dc2b5d3`,
and `panda@21701e3f`. The Panda safety image was rebuilt/flashed from that exact nested
opendbc state and its live firmware signature matched before the comma reboot. The comma
subsequently booted on those exact Git heads and started pandad/card/controlsd/selfdrived;
a final messaging-only parked observation remains the post-reboot verification boundary if
network access is temporarily unavailable.

**September-19 post-serialization drive (`00000144--ec7cf2b209`):** the warning-only path
worked as intended: `CarState.steerFaultTemporary` remained false while
`steerFaultTemporarySilent` carried the visible warning and `latActive` stayed true. The
remaining limpness was therefore not caused by the UI warning. In the analyzed active
segments the host produced **3,281** ID11/B24=100 frames; Panda accepted **3,174** and
rejected **107**, while Brake/VMM selected `0x081` result-ID11 **2,866** times. There were
117 unique request-plane failures: 107 `host_08a_rejected`, nine `oracle_sign_failure`, and
one startup `oracle_recovery_failure`.

Matching each rejected host frame back to its source generation shows the dominant failure
was the target-specific Panda buffering contract itself: rejected requests were only
**5–7 native generations / ~140–185 ms old**. The six-generation history therefore discarded
otherwise exact, single-use, in-order source generations before their MAC arrived. This is
not Toyota receiver policy and not an upstream steering authority rule. It was bring-up
scaffolding. `opendbc@805cb8f1` removes that narrow transport policy by treating history as
capacity rather than authority: the exact-generation FIFO is enlarged to **16 generations**,
while matching remains source-exact, single-use, and **oldest-unconsumed-first**. The
replacement fail-open watchdog moves from 100 to **250 ms**, long enough for serialized
command-5 catch-up while still restoring stock forwarding if the host stops producing
replacement traffic entirely. Ordinary `controls_allowed`, angle/rate checks, source
matching, source ordering, and one-use consumption are unchanged.

The same drive still contained nine cases where a source generation received ISO-TP flow
control on both the first sign attempt and its retry but no private `07 C9` response. The
surrounding serialized transactions resumed normally. `kai-openpilot@4fb0dfd4d` therefore
allows **two retries / three total serialized attempts** for the exact same source generation
before releasing that authority interval. The later coalescing change below supersedes the
"must eventually send every source generation" part of this interim design; generation
prediction remains forbidden. The production replay tool supports `--drop-sign-attempts 2`
so this exact double-loss class is exercised explicitly.

With the narrow Panda buffering policy removed, the complete local `144` route replay
(segments 0–8) passes at 24-ms synthetic oracle service time while deliberately dropping the
first **two** sign responses for generation 500: **4,268 modified ID11**, 4,273 owned native
generations, zero Panda TX rejects, zero native leaks, zero safety invalidity, zero
freshness/sign failures, and normal arm/release count. The older mixed route `135` also
passes the same double-loss injection with **8,432 modified ID11** and zero failures. Unit
gates remain **40 proxy/car-event tests** and **275 Toyota/Panda safety tests + 8 subtests**.

Deployed heads after this transport-policy removal are `kai-openpilot@4fb0dfd4d`, nested
`opendbc@805cb8f1`, and `panda@21701e3f`. Panda was rebuilt/flashed from that exact nested
opendbc state and its live firmware signature matched. After the comma reboot, a lease-free
12-second parked observation captured **481** native ID0 generations with zero B26/timing
gaps, Toyota safety param 53833, valid RX checks, no Panda faults, no request-plane warning,
and no unexpected host/ownership/oracle traffic.

**September-19 route `00000146--e87b3278be`: stale-generation backlog closure.** This is the
first drive after the 16-generation/250-ms policy removal. In the six retained segments the
host emitted 318 ID11/B24=100 frames; Panda accepted **316** and rejected only **2**, while
Brake/VMM selected `0x081` result-ID11 **295** times. There were four unique request-plane
failures: one startup `oracle_recovery_failure`, two `host_08a_rejected`, and one
`oracle_sign_failure`. The two host rejects were exact signed source generations that had
aged to roughly **404 ms / lag 16** and **425 ms / lag 17** respectively. This proved that
merely enlarging the FIFO continued to treat transport backlog as something steering should
wait for rather than eliminating the backlog itself.

The same route also characterizes the command-5 transport directly. Across 365 production
requests, 325 private `07 C9` responses succeeded and 40 did not. Successful RTT was median
**18.42 ms**, p95 **27.99 ms**, max **38.95 ms**. Every failure class still showed ISO-TP
flow control, but the fast transport sends all five CFs roughly **5.1 ms** after FF, before
flow control normally arrives. FC latency in this route was median ~16.8 ms and failures
were strongly concentrated when FC arrived late (26–30 ms). A parked normal-pandad benchmark
confirmed the throughput/reliability tradeoff: 5-ms pre-CF produced 72/80 successes, 8 ms
75/80, 10 ms 75/80, and 12 ms 79/80. Waiting long enough for near-perfect admission on every
request would therefore reduce service rate below the 40-Hz native stream. The fix cannot be
"wait longer for every generation".

`kai-openpilot@0ec4e2b3d` changed the active signer from a FIFO of every native source
generation to a **monotonic latest-generation queue**. At most one sign transaction was in
flight and one newest unsent generation was retained; older not-yet-started sign jobs were
marked superseded and omitted from the downstream stream. At the time this was treated as a
transport optimization: no skipped generation was forwarded as native Toyota ID0 while the
recovered freshness tracker still advanced over every source-real generation.

**This omission policy is superseded by the route-149 result below.** It was useful for
eliminating stale signing backlog, but it incorrectly assumed downstream arbitration cared
only about freshness of the latest request rather than continuity of every FRC publication
generation.

Nested `opendbc@97f0f1f7` makes the corresponding Panda matching rule monotonic rather than
contiguous: the host may send any **newer exact unconsumed** native generation, and successful
matching atomically consumes that generation plus all older skipped generations. Newer
history remains available. Replay/backward movement, duplicate consumption, fabricated
freshness, arbitrary application edits, controls-disallowed steering, and angle/rate
violations remain rejected. This removes the last "every generation must be host-transmitted"
bring-up policy without removing ordinary Panda steering safety.

The new regression suite explicitly covers both sides: a timed-out in-flight generation with
a newer queued source is superseded with no authority failure/warning, and Panda accepts a
forward exact-generation skip but rejects any attempt to replay an older skipped generation.
The exact `146` route then passes full production replay at 24-ms synthetic oracle service
with an injected lost sign response: **387 modified ID11**, 390 owned native generations,
zero Panda rejects, zero native leaks, zero freshness/sign failures, and zero authority
failures. The older mixed `135` route also passes the same injected-loss gate with **8,430**
modified ID11 and zero failures. Unit gates after this closure are **42 proxy/car-event
checks** and **275 Toyota/Panda safety tests + 8 subtests**.

Deployed heads are now `kai-openpilot@0ec4e2b3d`, nested `opendbc@97f0f1f7`, and
`panda@21701e3f`. Panda was rebuilt/flashed from that exact nested opendbc state and the live
firmware signature matched. After comma reboot, a lease-free 12-second parked observation
captured **481** native ID0 generations with zero B26/timing gaps, Toyota safety param 53833,
valid RX checks, no Panda faults, no warning-only steering fault, and no unexpected
host/ownership/oracle traffic.

**September-19 zero-steering regression (`00000148--f8f011b74d`):** the first drive after
`0ec4e2b3d/97f0f1f7` had **no host `0x08A` at all** and no ownership-admin `0x777` frames.
Across seven segments the route contains 15,451 native source `0x08A`, 12,874 downstream
`0x081`, but **zero** host steering frames. The only request-plane failure was a startup
`oracle_recovery_failure` while parked. A second recovery attempt then did receive valid
private command-5 responses and reconstructed the tracker, but the following one-shot
**verify** request lost its private `07 C9` response. The proxy had no verify-failure branch:
`tracker` remained valid, `qualified=false`, `recovery_active=false`, no verify/recovery job
was queued, and no arm was possible for the rest of the drive. This is the exact cause of
"no steering at all" in route148.

The same bug also explains why the comma gave no useful indication during the drive. The
startup failure pulse occurred before engagement and expired while parked; later
`CC.latActive=true` with `qualified=false` produced no new event. `kai-openpilot@468458ce1`
fixes both behaviors without changing Panda/opendbc. A failed verify is retried against the
**current** tracker event/message counter (native freshness may have advanced while the prior
verify was in flight); after two failed verify retries the proxy performs a full fail-open
recovery instead of becoming stranded. Separately, the warning-only steering-unavailable
surface now remains asserted whenever `CC.latActive` is true and the proxy has neither
active authority nor an atomic handoff pending. Thus an unqualified/no-authority state can
no longer be silently limp.

The unit regression directly drops a verify response and proves a retry can subsequently
qualify. The production replay tool now has `--drop-verify-response`; replaying the exact
route148 with the first verify response deliberately dropped still reaches **6 authority
windows**, **4,397 modified ID11** frames, zero Panda rejects, zero native leaks, zero
freshness/sign failures, and normal release count. Unit gates after this fix are **44
proxy/car-event tests**. This change is parent-Python only; nested `opendbc@97f0f1f7` and
Panda firmware remain unchanged, so no Panda reflash is required.

Deployed heads are `kai-openpilot@468458ce1`, nested `opendbc@97f0f1f7`, and
`panda@21701e3f`. After comma reboot, parked messaging showed Toyota safety param 53833,
valid RX checks, no Panda faults, no steering warning, and no ongoing oracle churn. The
current boot log shows startup recovery/verification traffic followed by silence rather than
the route148 stranded state.

**Route `00000149--82d77c5bdd`: downstream continuity and handoff closure.** The next road
drive disproved the remaining "latest generation is enough" assumption. Steering did work,
but only intermittently: while `CC.latActive` remained asserted, Panda repeatedly rejected
host `0x08A`, the proxy repeatedly released/re-armed ownership, and Brake/VMM `0x081`
asserted `REQUEST_LOSS_STATUS=1`. Near the final failure, the FRC's own `0x251`
`CRUISE_MAIN_STATE` changed from 1 (`c0 10 17 48 80 28 a0 80`) to 0
(`e0 00 00 48 80 08 00 80`); `CarState.cruiseState.available` fell with that source-real
change and did not recover during the drive. `accFaulted` and the permanent steering-fault
projection remained false. This is therefore not a parser/UI failure: repeated request-plane
continuity loss reached Toyota's arbitration/control domain and was followed by an FRC
cruise-main shutdown.

The exact failure mechanism has two coupled parts. First, the EPS command-5 **service** is
fast enough, but the host's speculative ISO-TP ingress is imperfect: successful private
`0x7A9` responses in the failing window commonly returned in roughly 15--30 ms while
isolated requests received FC but no private reply. The later latest-generation queue turned
those admission misses into **holes** in the owned downstream `0x08A` stream. Route149's
`0x081 REQUEST_LOSS_STATUS` is direct dynamic evidence that those omitted FRC generations
are semantically observable downstream. The earlier serialized whole-transaction retry
avoided overlap, but a new FF/retry attacked the wrong layer and could accumulate multiple
source generations of latency.

A short-lived September-19 fallback implementation then made the opposite mistake: on a
late/missing MAC it forwarded the exact authenticated Toyota source generation. That did
preserve cadence, but it **broke the chain of authority**. If Toyota selected ID0, comma's
lateral request disappeared for that generation; native ID11 could submit Toyota's different
pinion target; native ID4/LDA or ID18/SDG could submit a different Toyota application owner
to Brake/VMM. Re-basing CarController/Panda afterward made the software internally
consistent but did not fix the architectural error: Brake had already received Toyota's
request. Commits `04ad114db` / `fd9ac33e` and their fallback interpretation are therefore
superseded and must not be used for a road test.

The corrected ownership contract is strict:

- the exact source frame is used once as the **atomic handoff witness**; after that, while
  comma owns the relay and `CC.latActive`, every lateral host `0x08A` is ID11;
- all four lateral owners observed in the 12-route Camry corpus are takeover inputs, not
  pass-through modes: ID0 No Request, ID4 LDA, ID11 LTA/LCA, and ID18 SDG/PDA-SA are all
  converted to comma ID11 on the **same source generation** and re-signed;
- ID4 already carries B24=100 in every retained frame. ID18 uses B24=25/50, so ID18->ID11
  takeover explicitly normalizes B24 to the observed ID11 gain raw 100 while preserving all
  other source-envelope bytes except B18:B19, B21-low6, B24, and MAC28;
- an unexpected lateral ID is an authority failure, never an exact Toyota fallback;
- on disengage, cruise withdrawal, or unrecoverable signing failure, blocked pending source
  generations are dropped and the relay is released. Toyota resumes on the **next** native
  publication after the ownership boundary; no stale Toyota request is replayed through the
  host before release;
- Panda independently enforces the same rule: the first host frame is the one exact handoff
  witness. After that there is **no exact-clone/pass-through authority category at all**.
  Every host generation is validated only as comma's bounded ID11 request against the matched
  source generation. Byte equality with Toyota's ID11 has no authority meaning and is not a
  separate acceptance condition; the proxy still sends that generation through the EPS
  signing path even when comma's requested application bytes happen to equal Toyota's.

The transport repair now stays inside the same command-5 transaction. Active signing remains
one-transaction-at-a-time and source ordered. The normal fast path sends FF then the five CFs
after 5 ms. If the EPS's real `0x7A9` ISO-TP FC arrives **without** the private `07 C9` reply
in that same incoming CAN batch, the host repeats only CF1..CF5 once for the still-open
FF/session. It does **not** allocate a new private sequence, send a new FF, skip a source
generation, or substitute Toyota. Panda bounds the surface to at most two CF trains per FF.
If the repaired session still does not return the MAC within its bounded response deadline,
the whole comma authority interval is released rather than mixing owners.

The exact route149 replay now exercises this strict shape. At 20-ms synthetic successful
oracle latency with the selected sign reply deliberately omitted until EPS FC triggers the
same-session CF repair, all five recorded lateral windows complete with **5 arms / 5
releases**, **7,387/7,387 owned native generations blocked**, **7,387 accepted host `0x08A`**,
7,382 active host ID11 frames, zero owned non-ID11 transmissions, zero Panda rejects, zero
native leaks, zero safety invalidity and zero failures. The same route passes at a
conservative 24-ms synthetic reply latency. Mixed route `135` also passes the injected-loss
repair with **8 arms / 8 releases**, 8,550 active host ID11 frames, and zero non-ID11 owned
transmissions/rejects/leaks/failures, exercising the older Toyota lateral-owner transitions.

Focused gates after the correction are **26 proxy tests** and the complete **47-test Camry
TSS3 module**, plus route149 at 20/24 ms and mixed route135. The key invariant is no longer
"keep a frame on the wire somehow". It is: **one lateral authority owner per interval; while
comma owns, Toyota's application choice is input data only and Brake/VMM sees comma ID11.**

The short-lived fallback build was flashed while the vehicle was offroad and its live Panda
signature was verified, but it is superseded by this correction. It has now been replaced on
the comma by the strict build, then tightened once more to remove the useless post-handoff
byte-equality shortcut entirely. Final deployed heads are parent `kai-openpilot@f2c6b23a3`,
nested `opendbc@e75bb17d`, Panda source `21701e3f`. In this final shape the proxy always
queues an EPS signing job for every owned generation after the handoff witness, even when
comma's ID11 application bytes happen to equal Toyota's source ID11 application. Panda has
no post-handoff `exact_clone`/pass-through classifier; it validates every later generation
only through the bounded comma-ID11 command path.

The final signed Panda image is SHA-256
`8568b69724ca42ec9f24f1f3e0df1a761bdc598b9cddc1a18381d00f0e462cc5`; after an
offroad reboot, a cooperative direct-Panda lease read live signature
`13e1abff7abaee8117d601418e8ba2398c733430ae88ef22fb5e28554b4b5fec199ff8b0a189662e00b8fc4bdb92ed3320b0417909f98a6787be42e688071d29ea4d50a7d41e266664b8d53f8e484db69d5b093007f9b6b05a36bcf5288f227234f3fecfef39ef0d9aaed251fc7e1ba3a6d6f9aafd2de9ff15a2e90cd62fd3f2`, exactly matching the newly built expected signature. Live post-lease health was ignition line/CAN false, `controls_allowed=false`, zero safety TX blocks, zero faults, no heartbeat loss, and valid RX-check state; pandad resumed and no lease files remained.

### September-19 minimum-runtime reassessment: lifecycle and evidence limits

This is a source-level design review of `kai-openpilot@e3df394eb` and nested
`opendbc@5c481f89`, not another runtime modification or a vehicle qualification.
It supersedes the broad claims below that the simplified path has no further
coordination problems or that the custom replay proves a working transport.
No vehicle connection, actuation change, authentication change, safety relaxation,
or deployment was performed for this review.

**Minimum code means fewer independent responsibilities and assumptions, not just
fewer lines or shorter timeouts.** The previous cleanup removed scaffolding but
retained a distributed control lifecycle: `card`, the worker thread, Panda, and
the vehicle each have a different view of progress. The actual requirements are
bounded-age requests, ordered and observable lifecycle transitions, normal driver
cancellation, preserved non-lateral behavior, and independent safety enforcement.

#### Direct implementation findings

Paths below are relative to the openpilot checkout at the revisions above.
These are static findings; they do not establish which path caused a particular
road event.

- `opendbc_repo/opendbc/car/toyota/carcontroller.py:117-130`: the TSS3 branch
  handles `CC.cruiseControl.cancel` only for Corolla and then returns. Camry
  therefore has no cancel output in this controller branch. Letting go of lateral
  replacement is not proof that stock longitudinal cruise has been cancelled.
  This is missing lifecycle behavior, not a reason to disable a safeguard.
- `openpilot/selfdrive/car/toyota_tss3_08a_signed.py:290-301,433-435,521-548,
  696-707,732-745`: incoming source events capture control snapshots into an
  unbounded work deque and separate pending-output map. The response timeout
  starts at dispatch, not when that control snapshot was created. A response can
  be prompt relative to dispatch but the command can still be old. Panda's
  forwarding watchdog measures time since accepted host TX, not command age.
- `openpilot/selfdrive/car/card.py:176-191,253-266`: incoming source traffic is
  processed before the latest control subscription is refreshed; control updates
  are skipped when that subscription is no longer alive. The proxy has a cached
  activity/target and an independent worker. An explicit integration test must
  establish that loss of the control producer cannot leave that cached intent
  producing work. Other existing safety layers may intervene; this review does
  not claim an observed continued-steering event.
- `openpilot/selfdrive/car/toyota_tss3_08a_signed.py:763-786,808-814`: the sender
  takes work under a lock, then sends and sleeps outside that lock. Clearing
  queued/in-flight bookkeeping does not cancel work already taken by the sender.
  The shutdown path needs a tested no-output-after-cancellation property. A
  mutex around publication alone is not such a property.
- `openpilot/selfdrive/car/toyota_tss3_08a_signed.py:696-715` together with
  `_job_failure_locked` and `_abort_recovery_locked`: the timeout loop first
  collects expired keys, then pops them one by one. Recovery failure clears the
  in-flight map. If more than one recovery job expired, a later pop can therefore
  refer to a key just removed by the first failure. This is a static worker-crash
  risk, not a measured crash attribution.
- `openpilot/selfdrive/car/toyota_tss3_08a_signed.py:338-342,604-609` and
  `openpilot/selfdrive/car/card.py:181-186,254-265`: handoff pending suppresses
  the unavailable indication; a local TX echo sets active; the controller's
  baseline reset happens later in `card`. These are separate events, not one
  atomic end-to-end transfer acknowledged by the vehicle. Requested, queued,
  transmitted, and physically effective are distinct facts.

The safety source still has a fixed four-controller-tick angle allowance
(`opendbc_repo/opendbc/safety/modes/toyota.h:316-330`). The previous elapsed-time
implementation was reverted. The claimed timing consistency must not be assumed
from historical prose. Likewise, reducing history from sixteen entries to four
and a watchdog from 250 ms to 100 ms does not itself establish a receiver timing
contract. Keep driver override, cancellation, and actuation protections; establish
one consistent timing model rather than loosening protection to fit a replay.

#### What the custom replay actually proves

`openpilot/tools/replay/toyota_f33_request_plane_replay.py`:

- lines 223-225 and 319-323 use a hard-coded historical safety parameter, recorded
  CarParams, and `start_thread=False`. This is not a rebuild of the full deployed
  configuration or an execution of the production sender thread.
- lines 258-286 synthesize local TX echoes immediately from the safety-hook
  return. These are not device queue, bus-transmission, or receiver acknowledgements.
- lines 289-315 validate selected metadata but return a fixed stand-in for newly
  authored message authentication. Vehicle authentication and arbitration are not
  being exercised.
- lines 332-383 implement a different scheduler and explicitly manufacture a
  successful response after the chosen repair branch. This proves behavior under
  the model's assumption; it cannot prove that the real transport repair works.
- lines 264-271 classify any relevant rejection while controls are disallowed as
  expected, without proving a particular normal disengagement caused it.
- lines 432-444 replay recorded CarControl; lines 505-518 assert local ownership,
  generation, and safety invariants. There is no closed-loop vehicle response or
  rerun of the engagement controller against the new output.

The replay remains useful regression coverage. The earlier blanket descriptions
of zero unexpected failures and successful repair must be read within those
limits. In particular, local transmission acceptance is not vehicle acceptance,
and preserving source bytes does not preserve stock longitudinal *timing* when
an entire shared request message is delayed by the lateral path.

#### Minimal design target and decision order

Use the existing engagement and controller processes, a thin vehicle adapter, and
one explicit bounded-I/O boundary. Reuse normal driver cancellation, fault
reporting, and independent Panda enforcement. Setup/qualification is a separate
lifecycle from active control, not an additional policy engine embedded in each
control update. No new framework, daemon, registry, or general-purpose scheduler
is implied by this separation.

Measure complexity by independent state owners, asynchronous handoffs, clocks,
and inferred permissions. Do not optimize for line deletion while keeping the
same coordination problem. A single transport completion must not be promoted
to proof of steering effectiveness, nor should an uncertain response become an
unconditional permanent-disable policy.

First establish the complete disable/cancel contract, including producer death,
and truthful output/progress reporting in a non-actuating harness. Next test the
actual production scheduling and cancellation behavior with delayed/batched
acknowledgements and worker failures. Measure the full control-to-output age,
not just service RTT. Then establish receiver-side timing and selection from
independent evidence before changing buffer policy or interpreting all missing
messages as the same fault.

For a generic serial service, waiting time obeys
`W[n+1] = max(0, W[n] + service_time[n] - arrival_interval[n])`. A service that
cannot keep up cannot be made real-time by deeper buffering, shorter watchdogs,
or counting eventual completions. The choices require a validated interface
contract; neither arbitrary generation skipping nor native fallback is justified
by this review.

The claim that every native generation must receive a counterpart, and the claim
that one exact clone is sufficient for semantic ownership, remain implementation
assumptions rather than independently recovered receiver specifications. Do not
remove their checks blindly; separate actual protocol requirements from the
current host design and test each boundary without further road deployment.

### September-19 request-plane simplification audit

A post-route149 code audit treated every F33-specific state variable and branch as suspect
unless it protected one of four concrete boundaries: source freshness, atomic relay handoff,
MAC transport, or Panda TX safety. This removed a substantial amount of bring-up policy that
had accumulated while the path was still being discovered. Nested `opendbc@5c481f89` and
parent `kai-openpilot@e3df394eb` are the resulting simplified implementation.

The following scaffolding is now **deleted**, not merely disabled:

- proxy-local brake and native-cruise permission gates. `CC.latActive` is the sole normal
  lateral ownership input from controlsd; Panda independently owns ordinary brake/cruise
  safety. The proxy no longer runs a second engagement state machine;
- the persistent `CarController.tss3_request_plane_active` permission/veto input and private
  `CarState.tss3_lateral_request_id` plumbing. CarController runs ordinary angle limiting.
  The only request-plane synchronization is one one-shot measured-angle baseline reset after
  the handoff clone is actually accepted;
- native-frame fallback/restoration slots, transparent active output, `PendingOutput`
  wrapper state, and the old transparent ID0 proxy/runtime/test suite;
- the separate `TSS3_08A_SIGNED` rollout/safety flag. Relay-correct F33 request-plane mode is
  one mode now, `TSS3_08A_HOST`; current relay-correct safety param is therefore
  **`0x5249` / 21065**, not the historical `0xD249` / 53833;
- the second post-recovery oracle **verify** transaction and its retries. A successful native
  MAC equality match already identifies the full message counter; deterministic replay of
  retained consecutive native generations directly qualifies the tracker. The redundant
  verify gate was the exact mechanism that stranded route148 with zero steering after one
  missing private response;
- the arbitrary 2-second recovery cooldown, missing-generation tolerance (`B26` gaps up to
  eight), and the arbitrary four-recovery-error threshold. Freshness now requires strict
  source `B26 +1`; all observed gaps in routes 149 and 135 occur while lateral is inactive.
  A recovery transport error aborts that attempt immediately and retries only after the
  existing eight-clean-source gate;
- the one-second authority-warning latch. UI state is now derived directly: authority is
  unavailable iff controlsd still requests lateral control and the proxy is neither active
  nor completing a handoff. A Panda host-TX reject is logged as TX telemetry and releases
  ownership; it is not automatically promoted into a second timed fault state;
- the separate admin-accepted boolean/index/data ceremony. The accepted handoff clone itself
  proves Panda armed the relay. Exactly one native source generation may be cloned for that
  handoff; if another native generation arrives before its echo, the handoff aborts rather
  than emitting multiple Toyota clones.

Panda's old **16-generation / 250-ms** source buffer/watchdog was also a relic of the
serialized whole-transaction retry backlog. Same-session CF repair no longer creates that
backlog. Panda now retains only **four** source generations and fails open after **100 ms**
without accepted host replacement traffic. Exact generation matching remains because it is
a real safety boundary: `0x08A` carries longitudinal fields too, so Panda must prove the host
changed only the bounded lateral fields for the exact FRC freshness generation.

What deliberately remains custom is correspondingly small:

1. reconstruct the native SecOC freshness counter, using eight consecutive source frames
   before recovery after a gap;
2. one exact source clone as the atomic relay handoff witness;
3. one source-ordered command-5 sign transaction in flight, with one same-session CF repair
   if the EPS's real `30 00 28` flow-control arrives after the speculative 5-ms CF batch;
4. comma ID11 construction from observed FRC lateral owners `{0,4,11,18}` on the same source
   generation;
5. Panda exact-source binding, ordinary steering-angle safety, a four-generation transport
   window, and the 100-ms relay fail-open watchdog.

The simplified implementation still passes **28 proxy tests**, **46 Camry TSS3 tests**, and
three warning/event tests. Full production replay remains clean with an injected missing
sign reply repaired in-place. Route149 completes its five real lateral windows with
**5 arms / 5 releases**, 7,387 owned native generations blocked, 7,382 active host ID11
outputs, zero native leaks, zero safety invalidity and zero unexpected failures. The one
Panda-rejected ID11 occurs only after `controls_allowed=false` at the normal disengagement
edge and is classified as that safety-owned boundary, not an authority fault. Mixed route135
likewise completes **8 arms / 8 releases**, 8,552 active host ID11 outputs and zero unexpected
failures; its two Panda rejects are the same controls-disallowed disengagement ordering.

The simplification audit is deployed on the comma as parent `kai-openpilot@e3df394eb`,
nested `opendbc@5c481f89`, Panda source `21701e3f`. The rebuilt signed Panda image is
SHA-256 `d7c60228ca1cc10168b4504a5306f01fe15dbf5d50fdaae0faedc02386355c06`.
After an offroad reboot, a cooperative direct-Panda lease read live signature
`adef92bb94dbff01bf9f9935cf0bcf1b3b7977d5f4c53921143c1cb8f3e6392410fa383f3a2ced324bb336c21f9f90796e16dd3d45bd72116028c866b01b5ef5e25af83152de3518f88908948f848bf867aff22ebd153fe04b3fb10b5c19c4c79536475e4160191c200442d753789aeb127ac9149bd706c22091a404a0194c05`, exactly matching the new expected signature. Live health was ignition line/CAN false,
`controls_allowed=false`, zero safety TX blocks, zero faults, no heartbeat loss, valid RX
checks, and no direct-lease files left behind.

Same-session CF repair is software/replay-qualified but not yet live-EPS-qualified. Its next
hardware qualification is a **parked** oracle admission-loss test after the volatile resident
is installed. No moving test should precede that parked qualification.

The volatile EPS oracle resident is still a deployment prerequisite rather than an
openpilot-installed component. Without a qualified oracle response, the host never sends
the ownership arm and Panda continues forwarding stock `0x08A`; request-plane openpilot
lateral therefore remains unavailable rather than falling back to direct B6.

A parked vehicle still cannot prove downstream Brake/VMM steering selection or wheel motion,
but another road drive is **not** the next software-debug step. The full-route production
replay above is now the mandatory software gate and passes both the latest all-ID0 route and
the older mixed ID0/ID11 route, including bounded dropped-oracle-response injection. The
remaining pre-road work is a parked live deployment qualification only: reinstall/attest the
volatile EPS oracle after vehicle OFF, perform the already-established Brake->FRC recovery,
verify normal Toyota safety plus steady `0x7A9` oracle service, and confirm the proxy reaches
qualified/idle state without recovery churn. Only after that parked gate is clean should a
moving test be used for the one thing offline replay cannot prove: downstream `0x081`
selection/physical steering response to sustained authenticated host ID11.

**Parked live gate, September 18 evening:** after oracle reinstall and operator-completed
Brake->FRC recovery, the deployed heads were `kai-openpilot@71703da35`, nested
`opendbc@ad23a31b`, and `panda@21701e3f`. Live state was Park, `vEgo=0`,
`standstill=true`, `canValid=true`, Toyota safety param `53833`, flipped harness,
`safetyRxChecksInvalid=false`, and no Panda faults. A lease-free 30-second observation
captured exactly **1,200** source bus2 ID0 `0x08A` generations (40 Hz) with **zero**
B26/timing discontinuities, **zero** host `0x08A`, **zero** ownership-admin `0x777`, and
**zero** oracle/recovery traffic. This is the expected qualified/idle parked state.

An earlier short recovery burst in the same boot followed a **3.54-second native CAN hole**
caused by direct Panda-lease diagnostic activity during setup/inspection. Immediately after
that discontinuity the runtime re-qualified in three oracle transactions and returned to
silence; it is therefore classified as a diagnostic-tool-induced continuity break, not
steady-state proxy churn. Future parked qualification should avoid direct Panda lease/status
operations after the final recovery gate and use cereal/messaging observation only.

Working session notes for the GTS+ vehicle-type → install-set → family-`.ddb` → GetSupport funnel (not a claim ledger): [../history/2026-08/CAMRY_GTS_LATERAL_FUNNEL_2026-08-29.md](../history/2026-08/CAMRY_GTS_LATERAL_FUNNEL_2026-08-29.md).

## 1. Exact F33 generated-COM Tx carriers

The exact normalized `8965F3307000` CodeFlash (SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`) closes the
first five application generated-COM Tx descriptors at `0x21F58`:

| PDU | CAN ID | FD | PDU descriptor | Signals |
|---:|---:|:---:|---|---|
| 0 | `0x030` | yes | `(2,0,0,32,0,3)` | `0..37`, `283` |
| 1 | `0x351` | no | `(200,0,0,4,0,3)` | `38,39` |
| 2 | `0x394` | no | `(60,0,0,3,0,3)` | `40..43` |
| 3 | `0x4A3` | no | `(100,0,0,8,0,3)` | `44..51` |
| 4 | `0x4C8` | no | `(196,0,0,8,0,3)` | `52..55` |

The target signal-to-PDU table is `0x22488`, the PDU table is `0x226C0`, and the target
has 284 configured signal IDs. Target-native generic Tx scalar packer `0x7D1DC` indexes
that same signal map through `TP-0x1974`.

### 1.1 `0x351`

The target-native chain is:

- debounce/state preparation `0x4C1C0`;
- force/status producer `0x4C216`;
- packer `0x4CED0`.

`0x4CED0` packs signal 38 to `B2[7:5]` and signal 39 to `B2[4]`, then submits PDU1.
This closes the F33 wire projection, but not an openpilot temporary/permanent fault
classification. In particular, the force-7 path is not renamed as an old `LKA_STATE`.

### 1.2 `0x394`

The target-native projection/packer pair is `0x4C24A -> 0x4CE08`. PDU2 carries four
lossy state-table columns:

- `B1[7:6]`: column 4;
- `B1[5:3]`: column 1;
- `B2[3:1]`: column 2;
- `B2[0]`: column 3.

The exact H/F work already established the analogous 17-state classifier semantics, but
this F33 closure deliberately does not equate the deepest clear state with Ready or map
any numeric class to openpilot `steerFaultTemporary`/`steerFaultPermanent` without a
same-car asserted/recovery transition.

### 1.3 `0x030`

The target-native chain is `0x4C490 -> 0x4C97A` (PDU0, 32 bytes, CAN FD). Wire
geometry is derived from the pinned per-PDU slice-offset table at `0x22840`
(`FUN_0007d05c` copies each PDU out of the shared pack buffer at `FEBE4A48`;
`FUN_0007d31e`'s second argument is an absolute buffer byte offset, so wire bytes =
buffer offset - slice offset; PDU0 slice offset is 0):

- `B8` (signal 11): coarse signed steering-wheel torque, 0.1 N.m/count;
- `B17[3:0]` (signal 30): signed decimal digit, 0.01 N.m/count;
- combined: `signed8(B8)*0.1 + signed4(B17[3:0])*0.01` N.m;
- `B22:B23` (signal 33): **signed big-endian 16-bit mapped motor-feedback proxy**.

The `B22:B23` source chain is now target-natively closed: `0x37E48` forms dual-channel
feedback sums into `FEBE6D70` plus an extended Q-axis sum `FEBE6D78` (whose saturated
i16 `FEBE6D72` is the DID `0x1151` upstream source); `0x38678` maps
`abs(FEBE6D78)` through a lookup table conditioned by the sibling axis `FEBE6D70`;
`0x3879E` publishes the mapped result to `FEBE6E00`; `0x59448`/`0x5D12C` mirror it to
`FEBE6718` (GP-0x50E8, the same cell `0x4A3 B6:B7` reads); `0x4C490` stages
`signed16(((-FEBE6718 * FEBEE8D8) / 0x100) * 100 / 0x2000)` into `FEBE816C`; and
`0x4C97A` packs it at `B22:B23`. It is therefore a **motor-current-family feedback
proxy sharing DID1151's pre-clamp Q-axis aggregate**, but not DID1151 in wire units:
the sibling-axis-conditioned lookup and the runtime scale (`FEBEE8D8`, written at
runtime by `0xBF3AA`/`0xBF97A`) intervene. A second staging-cell writer `0x58C9A`
also writes `FEBE816C`; it is bounded with no semantic claim. Treat `B22:B23` as a
signed motor-feedback/assist proxy — never as amperes, commanded torque, or lateral
authority: driver EPS assist also creates current. The two-drive bounded correlation
of this field lives in the live-baseline report §24 (VAR-072).

#### 1.3.1 `0x030` is an EPS-owned production SecOC transmit PDU

The exact F33 firmware plus the retained READY RAM/CAN oracle now close the part that
the legacy DBC name obscured: **`0x030` is transmitted by this EPS, and its last
four bytes are the EPS's configured SecOC trailer.** This is not an inference from the
steering-shaped payload. Generated-COM PDU0 has CanIf descriptor `0x40000030`, length
32, and `0x7DF14 -> 0x81A7E/0x81AB2` routes it to the sole configured SecOC-Tx
entry `0x8ED8E`. `0x8FABA` then subtracts the configured four-byte security trailer
from the 32-byte PDU before queuing **28 authentic application bytes**.

The exact profile-0 constants and worker dataflow are:

| property | exact F33 value |
|---|---:|
| SecOC DataID | `0x0030` |
| application payload | 28 bytes (`B0..B27`) |
| full freshness | 46 configured bits, stored in 6 bytes |
| transmitted freshness | 4 bits |
| authenticator | 28 bits |
| security trailer | 4 bytes |
| freshness-value ID | 3 |
| CryptoIf job | 0 |
| lower PDU | 0 (`0x030`) |

`0x8FD90 -> 0x8ECB2` constructs the authentication input as
`DataID_be16 || payload[28] || full_freshness[6]`, i.e. 36 bytes. The configured
Tx freshness callback is `0x903F6`. The normal Toyota four transmitted freshness bits
are `message_low2 || reset_low2`; `0x8FED0` writes those first and immediately appends
28 generated authenticator bits. Therefore the exact wire trailer is:

```text
B28[7:6]  message counter low2
B28[5:4]  reset counter low2
B28[3:0]  MAC28 bits 27..24
B29:B31   remaining MAC28 bits
```

The cryptographic ownership is also closed rather than merely inferred from the wire.
`0x8F19A` loads key-selector descriptor 0 from `FEBE5504`; the retained READY snapshot
is exactly `01 00 00 00 04 00 ...`, and the lower command-5 builder requires the first
dword to be 1 and consumes byte `+4` as the hardware selector. `0x8A720` finally writes
`ICUSCMD = (selector << 16) | 5`. Thus stock `0x030` uses **ICU-S command 5, selector
4**, the same live slot later used by the resident B6 signer. This provides an independent
production-path explanation for why selector-4 MAC generation works on exact F33.

The two integrity layers are separate. `0x4C97A` still computes the inner B7 additive
byte (`low8(sum(B0..B6)+0x38)`) as part of the 28-byte application payload; SecOC then
authenticates that payload and appends `FV4 || MAC28`. In the retained PE1 snapshot the
generated-COM PDU0 slice at `FEBE4A48` has `B28:B31=00000000`, while the tracked CAN
oracle has 6,189/6,189 frames satisfying the B7 rule, all 16 FV4 phases, 6,189 unique
trailers/MAC28 candidates, and 5,981/5,981 consecutive same-reset pairs advancing
message-low2 by `+1 mod 4`. The outer trailer is therefore not generated by the
application packer.

Consequently, an old DBC attribution such as `POWERTRAIN_STATUS_3 (ECM)` does not apply
to this calibration. The exact producer is the EPS; the packet is an EPS status/feedback
PDU with an application checksum inside an EPS-generated SecOC envelope. It is **not pure
telemetry**: besides physical driver torque and motor-feedback-family quantities, exact F33
projects cooperative-control inhibit/status state into this same PDU (§4.7). Same-car road
evidence also strongly joins its physical driver-torque field to the FRC-side ordinary-LTA
driver-steering detector and nudge timer; that inter-ECU use is a dynamic join, not yet a
static FRC-parser recovery. Deterministic transmit-path evidence is
`tools/targets/camry/analysis/analyze_camry_f33_030_secoc_tx.py`,
`data/generated/camry_8965F3307000_030_secoc_tx.json`, and suite
`camry_f33_030_secoc_tx`.

### 1.4 `0x4A3`

The exact F33 chain is `0x4C000 -> 0x4C14E -> 0x4C7AA` and is materially better evidence
than transferring the H/F packer by shape.

`0x4C000` prepares the physical sources. `0x4C14E` stages the eight wire bytes, and
`0x4C7AA` packs global signal IDs 44 through 51 and submits PDU3. The recovered wire
geometry is:

- `B0[5]`: marker/status bit;
- `B0[0]`: selected steering fault/inhibit status;
- `B1[3:0]:B2`: signed12 coarse steering-angle source, 1.5 deg/count;
- `B3[3:0]:B4`: signed12 filtered/voted steering-angle quantity, 1.5 deg/count;
- `B5`: steering-wheel-torque telemetry at 0.1 N.m/count after F33 source staging;
- `B6:B7`: signed16 alternate motor-current telemetry from
  `(GP-0x50E8 * -100) / 0x80`.

The distinct `0x4A3` alternate-current source `GP-0x50E8 = FEBE6718` has four
direct references: readers `0x4C000/0x4C490` and writers `0x59448/0x5D12C`. The
`0x030 B22:B23` field reads this same cell, and its upstream is now closed (§1.3,
§2): `GP-0x50E8` is a nonlinear sibling-axis-conditioned map of the same extended
Q-axis sum that saturates into the DID1151 source. The packed fields therefore remain
structurally named (`MOTOR_CURRENT_ALT`, mapped motor-feedback proxy) — not because
the source relationship is unknown, but because the lookup and runtime scale mean the
wire values are not DID1151 units, amperes, or commanded torque.

### 1.5 Complete exact-F33 EPS transmit inventory

The full exact-F33 Tx surface is now closed separately in
`docs/variants/camry-f33-eps-tx.md`. In addition to `0x030` and `0x4A3`, the exact
normal generated-COM table contains `0x351`, `0x394`, and `0x4C8`; the document and
its machine-readable reducer recover every direct application field, PDU period, group
activation state, PduR/CanIf route, the `0x030` SecOC profile, diagnostic responses
`0x7A9/0x7A8`, and the stock-gated extended `0x1FE00002` response endpoint.

One runtime boundary remains explicit rather than guessed: retained PE1 RAM proves all
five normal PDUs were scheduler-armed, while retained external CAN captures expose
`0x030` but not the four classic sibling PDUs. The classic messages use a valid sibling
HTH on the same lower driver node; idle HTH state `0x69` is not a disabled flag. The
reason for the capture/runtime discrepancy is therefore left unresolved below CanIf or
in external topology/capture visibility. Deterministic evidence is
`data/generated/camry_8965F3307000_eps_tx.json` and suite `camry_f33_eps_tx`.

## 2. Canonical first-class source-reference census

The earlier scratch-project census evolved in two steps: VAR-056 initially found four
direct/fixed-GP driver-torque users, and CORR-120 added `0x4C000` as a fifth after
recovering the `0x4A3` telemetry producer. Both counts are now historical. The
first-class F33 project seeds the target-native GP from `0x715B4` and exports the
canonical Ghidra data-reference graph across **6,062 recovered functions**, so the
source census no longer depends on textual `unaff_gp` spelling.

For driver torque `GP-0x5158 = FEBE66A8`, the exact direct-reference set is **nine**:

- readers: `0x35A06`, `0x4C000`, `0x4C490`, `0x4DB70`, `0x52CA0`, `0x54244`, `0x564CE`;
- writers: `0x59448`, `0x5D5E0`.

For DID1151 Q-current `GP-0x50F2 = FEBE670E`, the exact direct-reference set is
**six**:

- readers: `0x4E394`, `0x52CA0`, `0x54244`, `0x564CE`;
- writers: `0x59448`, `0x5D12C`.

The distinct `0x4A3`/`0x030` mapped-current source `GP-0x50E8 = FEBE6718` has four
direct references: readers `0x4C000/0x4C490` and writers `0x59448/0x5D12C`.

The `0x030 B22:B23` upstream is now census-closed as well: the mapped feedback
`FEBE6E00` (GP-0x4A00) is written only by `0x3879E` and read by `0x57FD2`,
`0x59448`, `0x5D12C`; the extended Q-axis sum `FEBE6D78` (GP-0x4A8E) is written by
`0x37E48` and read by `0x375C2`-family consumers including the `0x38678` map input;
the DID1151 pre-clamp cell `FEBE6D72` is written by `0x37E48` and read by `0x37F92`,
`0x59448`, `0x5C7B6`, `0x5CA3A`, `0x5D12C`; and the `0x030` runtime scale
`FEBEE8D8` is read by `0x4C490` and written at runtime by `0xBF3AA`/`0xBF97A`.

The safety-relevant negative is unchanged and is now stronger: **none** of the direct
references to `FEBE66A8` or `FEBE670E` lies in the cooperative `C8xxx-D1xxx`
target-to-motor control cone. Computed aliases without a Ghidra data reference, DMA,
hardware mutation, and unrecovered code remain outside that bounded negative.
CORR-122 records why the old textual 4→5 census was incomplete.

## 3. Passive software implementation

The corresponding implementation is retained in:

- nested opendbc commit
  `ab60fd95d8a7b566e10ed1cf59738292f3498932` (`toyota: add passive Camry TSS3 lateral stack`);
- parent `kai-openpilot` commit
  `d7d7dfd7e49961e9d35eb7a7681e8756ceee8d04` (`toyota: advance passive Camry TSS3 port`).

### 3.1 Exact platform identity without an ambiguous legacy CAN fingerprint

The port adds `TOYOTA_CAMRY_TSS3` and a byte-exact EPS F181 discriminator for
`02 || 8965F3307000[16] || 8A3113303100[16]`. Known FRC and Brake identities are
corroborating constraints: if present, they must not conflict.

The retained same-car normal-harness CAN census contains a **179-ID** census. It is deliberately
*not* registered as a legacy CAN fingerprint because the current Corolla TSS3 fingerprint
is a **147-ID** set and is a strict subset of the Camry census. Registering both would
make Corolla identification order-dependent/ambiguous. The Camry census remains available
for topology and replay evidence while F181 performs the target binding.

### 3.2 Same-car CarState replay

The dedicated Camry tests replay source-real retained payloads for:

- `0x025` steering angle/rate;
- `0x030` driver-torque/status telemetry;
- complete `0x127` selector transitions: `P=0, R=1, N=2, D=3, B=4`;
- `0x51E B0[7]` Ready 0/1.

`0x4A3`, `0x351`, and `0x394` are parsed as static/presence-bounded internal inputs.
Their absence is distinguished from a real all-zero packet. They are not required for
CAN-alive checking and are not yet mapped to public openpilot fault policy.

VAR-088 established the byte-complete `0x08A` census; the September-16 follow-up
renames the DBC entry `TSS3_CONTROL_REQUEST` and maps the unified request/result
structure. B6/B7 split into two six-bit longitudinal request-ID candidates plus
two-bit allocation-method candidates, B8:B9/B11:B12 are the indistinguishable
signed16 x0.001 longitudinal acceleration-request pair, and B18:B19/B21/B24/B25
carry the lateral request tuple. Brake-owned `0x081` is now `TSS3_CONTROL_RESULT`,
with selected longitudinal ID B6[5:0], selected lateral ID B13[5:0], lateral
result pinion B16:B17, and longitudinal result acceleration B20:B21. Upper-vs-
lower A/B ordering and the remaining shift/EPB/override/priority/validity metadata
stay bounded rather than guessed.

### 3.3 B6 candidate construction and freshness/signing interfaces

The passive stack now has deterministic code for the exact known B6 contract:

- explicit 28-byte application template preserving unresolved bytes/bits;
- Target Lateral ID, signed target angle, secondary recovered scalar fields, and
  modulo-64 application sequence;
- FV46 construction and FV4 projection;
- full CMAC128 signer interface with transmitted MSB28 trailer;
- signer status/latency instrumentation;
- replacement freshness state that accepts the first authenticated `0x00F` only as a
  baseline and arms only after a **strictly newer authenticated sync epoch**.

The default application template is intentionally marked `stock_validated=false`.
No zero-filled candidate is represented as Toyota stock behavior.

### 3.4 Current fork state: exact-F33 output is enabled, not passively gated

The original passive implementation remains useful history, but it no longer describes the
code that produced the 2026-09-04 road logs. The current fork moved through three relevant
opendbc revisions:

- `78d03ddf` keeps Toyota `0x08A` passive/read-only and forwarded from the camera side;
- `91834530` restores exact-F33 B6 lateral output through the ordinary Toyota safety model;
- `c7a62eaf` reanchors the local B6 message counter whenever live `0x00F RESET_CNT` changes.

The corresponding historical parent `kai-openpilot` revisions are `75779fcdb`, `eda738486`,
and `d1914bbe7`. The current cross-repo checkpoint is **`kai-openpilot@7aece7f63`**, nested
**`opendbc@f207c273b645`**, and **`panda@bbc93b17d861`**. Root `60d57a89a` imported the
exact-F33 "only recovered external target-bearing ingress" result from analysis commit
`b531ec9`, but its first mirror still described the current sender as zero-MAC and promoted
B6 to a stock-command/EBU-private-handoff model. Follow-up `7aece7f63` corrects the mirror:
current B6 is normal-envelope wrong-key dummy-CMAC; exact F33 proves B6's external target
role but **not** factory use or an `0x08A -> B6` edge; and the `EBU` topology label does not
reopen a hidden second EPS application bus (VAR-066/CORR-139, VAR-095/CORR-137,
VAR-111/CORR-151, VAR-147/CORR-178).

For `TOYOTA_CAMRY_TSS3`, current `CarInterface` selects Toyota safety with
`STOCK_LONGITUDINAL|TSS3`, sets `dashcamOnly=False`, advertises angle control down to zero
speed, and does **not** require the former `ToyotaEphemeralSecOCBridge` /
`ToyotaTss3DevLateral` attestation parameters. Panda forwards stock `0x08A`, blocks a
camera-side stock `0x0B6` replacement source, and permits the controller's bus-0 B6.

The former state-decoding holdover is resolved: fork opendbc `e37bab6c` (2026-09-04)
replaces the hardcoded `steeringPressed=False` with the normal driver-state contract. The
initial 1.2 N.m bring-up threshold was deliberately provisional; VAR-139 now replaces it
with `abs(0x030 torque) >= 0.6 N.m`, selected from the same-car Toyota driver-steering
detector on two independent September-6 drives. Those post-fix routes also validate the
sign convention used by upstream DesireHelper: left nudge positive, right nudge negative.
§4.4 records why the original placeholder was not harmless.

## 4. Current exact-F33 Gate-2 development plumbing (VAR-102)

The first conservative sender was staged in opendbc `dde0fcf0` / parent `15f355036`, then
removed after the stock-template premise was disproved. Later development revisions rebuilt
the B6 candidate without claiming a stock template. The code exercised on 2026-09-04 is the
newer ordinary-path implementation at opendbc `78d03ddf -> 91834530 -> c7a62eaf`: stock
`0x08A` remains passive, B6 lateral is enabled for exact F33, and local freshness progression
is reanchored on each live reset epoch. This supersedes the former debug-only gating described
in older history.

### 4.1 Current sender contract

For exact F33, the current controller:

- sends one `0x0B6`, DLC-32 frame every other 100-Hz control frame (nominal 50 Hz) on
  Panda bus 0;
- reads live `0x00F` trip/reset state, resets the local message counter to zero whenever
  `RESET_CNT` changes, and owns the independent modulo-64 application sequence locally;
- sends Target Lateral ID 11 while `CC.latActive` and ID0 otherwise;
- applies the normal Toyota angle-control shaping, including the recovered ±1745-raw
  (~100-deg) absolute envelope and speed-dependent angle-rate limits;
- reports the actual slew-limited transmitted angle to controls;
- emits the normal Toyota DataID/application/full-freshness/AES-CMAC/FV4 envelope using the
  fixed all-zero **dummy AES-128 key** in `f207c273`; the real slot-4 key remains unknown, so
  this MAC28 is intentionally not stock-valid. CORR-178 proves that its invalid tag has no
  stronger stage-5 software acceptance behavior than the historical zero-MAC marker.

The 28-byte base is explicitly `stock_validated=false`: no unmatched native B6 exists in the
retained request/reference-state intervals, and those captures do not contain Toyota's
explicit winner/grant recorder state. Recovered command fields are packed exactly.
Current active companion fields set additive-term suppression to 0 and both
percentage contributions to 100, matching the recovered F33 selector shape;
inactive fields remain zero. This is a development candidate to validate
against an observed/bridged receiver, not a claim about Toyota stock bytes.

### 4.2 Receiver observation and conditional bridge

The historical cumulative CodeFlash stage-5 image remains a development artifact, not proof
of receiver/application admission: a stage-5 road run using the then-current zero-MAC sender
still left the steering response absent. VAR-146/147/149/150 now supersede MAC/counter A/Bs
and a bridge-first workflow. The next high-value experiment is the **stationary internal
first-divergence capture**: SecOC queue -> raw route44 -> generated COM -> `ADB0/CAFF/CB00`,
then only if that handoff passes, the remaining `ACCC` readiness operand, `CB20/CB38`, and
later common actuator gates.

The countered observer and deduplicating zero-MAC route44 bridge remain historical/audited
research tools; neither recovers or exposes the protected slot-class TSK key, and neither is
the normal openpilot architecture. The current sender uses the ordinary wrong-key dummy-CMAC
envelope and the cumulative stage-5 result-path patches are what make MAC validity irrelevant
at the recovered software layer.

### 4.3 Current Panda safety boundary

Current TSS3 Panda safety is no longer the earlier `ALLOW_DEBUG`/`TSS3_DEV_LATERAL`
sequence-and-timeout experiment. With the ordinary Toyota `TSS3` flag selected, bus-0
`0x0B6`/DLC-32 is whitelisted and checked as an **angle-steering command**. The B6 hook:

- allows only Target Lateral ID 0 (inactive) or 11 (LTA/LCA active);
- interprets B4:B5 as signed target steering angle;
- enforces ±1745 raw (~100 deg); and
- applies the standard Toyota speed-dependent angle-rate checks against measured `0x025`
  steering angle.

There is no B6 torque-command limit in this branch. The legacy Toyota
`MAX_LTA_DRIVER_TORQUE_ALLOWANCE` path is below the TSS3 controller's early return and is not
what constrains these B6 frames. `safetyTxBlocked` and Panda reject-return evidence therefore
provide a direct way to distinguish a Panda angle-safety rejection from an EPS that simply
does not act on a successfully transmitted command.

### 4.4 2026-09-04 highway evidence: B6 non-response and lane-change state failure (VAR-124/125)

Three long same-day routes were retained under
`/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/`: `0000003b--62262eb7a1`
(110 segments), `0000003c--97b9e7a69a` (81), and `0000003d--0e812cecba` (62). Together
they contain **751,664** openpilot B6 `sendcan` frames. The CAN returns contain **751,628**
Panda returned/TX-loopback B6 frames and only **33** `src=192` rejected B6 frames; the
Panda `safetyTxBlocked` counter rises by only **19** over roughly 252 minutes. This rules out
Panda steering limits as the explanation for the repeated long-duration non-response.

The failure is visible directly in angle space. During route `3d`'s first right-lane-change
warning, openpilot and its post-controller B6 output command roughly **+6.2 deg** while
measured steering remains near **-2.5 deg** for long enough to saturate. Route `3c` contains
an even larger window: B6 commands roughly **+15..+17 deg** while measured steering remains
near **-9.4 deg**. These are not marginal rate-limit clips. `LatControlAngle` declares
`saturated` when desired and measured steering differ by more than 2.5 deg for the configured
0.8-s `steerLimitTimer`; `selfdrived` then emits `steerSaturated` / “Turn Exceeds Steering
Limit”. The alert is therefore an **angle tracking failure**, not a report that a steering
torque allowance was too small.

Stock Toyota lateral state remains present at the same time. Native camera-side `0x08A` is
forwarded, and ID11 is frequent throughout all three routes; in route `3d` alone there are
226,470 sampled >5-m/s overlaps where openpilot B6 is active ID11 and stock `0x08A` is also
ID11. Because the two requested angles usually co-vary during straight highway driving, the
rlog alone cannot prove that Toyota is the *sole* actuator in every straight segment. The
large-divergence windows do prove the narrower and more important fact: successfully
transmitted openpilot B6 can fail to produce the commanded wheel motion while the stock
request plane remains live. A clean non-blinker route-`3c` interval strengthens that
interpretation: at ~25.7 m/s with only ~0.45 N.m driver torque, measured steering remains
near **3.2 deg** for ~1.25 s while stock `0x08A` is ~**3.1 deg** and openpilot/B6 is
~**6.36 deg**. This is directly consistent with the stock request/authority path continuing
to determine the wheel while B6 is ineffective in that window. It still does not prove sole
stock ownership when the two targets co-vary. Exact EPS B6 ingress/freshness/acceptance
therefore remains the primary actuation blocker; raising an openpilot/Panda steering limit is
not supported.

The lane-change warning had a second, independent software cause. The exact-F33
`CarState` that produced these routes decoded physical steering-wheel torque but set
`steeringPressed=False` on every sample.
Openpilot's `DesireHelper` requires `steeringPressed` plus torque in the indicated
direction to leave `preLaneChange` and enter `laneChangeStarting`. Across the three routes
there are thousands of `preLaneChangeLeft/Right` event samples and **zero `laneChange` event
samples**. The driver can therefore physically steer across the lane boundary while
openpilot continues requesting the old-lane path; the resulting desired/measured-angle gap
then triggers the same `steerSaturated` alert. Route `3d` torque distributions also showed why
the first threshold could not safely be selected from one drive: absolute torque during
`preLaneChange` has median ~1.30 N.m and p90 ~2.15 N.m, while >10-m/s no-blinker samples
still reach median ~0.37 N.m and p90 ~1.14 N.m with substantial overlap. Fork opendbc
`e37bab6c` therefore restored the missing state with a conservative **provisional** 1.2 N.m
bring-up threshold. VAR-139 supersedes that numeric policy with independent same-car
dynamic evidence: routes `3e` and `3f` join exact-F33 torque to Toyota's native
`0x371 B20[4]` driver-steering state, whose sampled assertion-transition median is
**0.67 N.m on both routes** and whose release median is 0.37/0.34 N.m. A simple 0.6 N.m
threshold gives ~94–95% specificity and ~75–77% sensitivity to that slower hysteretic state.
The fork therefore uses **`abs(torque) >= 0.6 N.m`** as an upstream-style stateless policy;
this is not a claim that Toyota itself uses one static torque comparator. Direction is
closed separately by actual post-fix behavior: all 45 observed `laneChangeStarting`
transitions across `3e+3f` have positive torque for left and negative torque for right.

Finally, the Sept-3 freshness change is demonstrably active on the wire but not yet proven
accepted by F33. Live `0x00F RESET_CNT` advances roughly every 300 ms rather than only at
ignition; the current sender reanchors its local message counter at each such epoch, and the
observed B28-high FV4 progression matches that implementation. Exact firmware still verifies
freshness before the patched Gate-2 MAC-result path and can return drop/retry/adopt verdicts.
Nothing in these rlogs proves which verdict B6 received. The corrected non-bypassing queue /
freshness observer remains the right discriminator; the wire-consistent FV4 trace is not a
substitute for receiver acceptance.

### 4.5 2026-09-04 wire-geometry, authority-attribution, and transport audit (VAR-126)

A full-corpus decode of the same three routes closes the three remaining observational
questions around §4.4: what the sender actually put on the wire, whether the wheel
tracks the stock or the openpilot request when they diverge, and whether any
transport-level event could explain the non-response.

**Historical sender application/FV4 progression is internally consistent.** All 751,664
B6 `sendcan` frames decompose into exactly two application shapes: inactive `Target Lateral ID 0` with companion byte
`B6=0x04` and `B8=B9=0`, and active `ID 11` with `B6=0x00` and `B8=B9=100` (0x64).
MAC28 is zero on every frame, every other application byte (`B0..B2`, `B10..B27`) is
zero on every frame, the modulo-64 sequence advances exactly +1 on every consecutive
pair (the only non-+1 differences are the 253 intra-route segment boundaries), the
message counter's low2 jumps only at epoch reanchors, and the transmitted reset low2
equals the current `0x00F RESET_CNT` epoch low2 on 100% of frames that had an observed
sync (751,664 − 603 segment-start frames). Cadence is a clean 50 Hz: per-segment median inter-frame gap 19.84–20.01 ms,
worst observed gap 34.6 ms. CORR-176 later identifies the separate envelope difference:
these routes use the bridge-only zero-MAC28 marker rather than the now-restored normal
dummy-CMAC construction. They are therefore not byte-identical captures of the current
sender, but VAR-147/CORR-178 prove that distinction is **not an acceptance variable under
the cumulative stage-5 F33 image**: both tags are invalid under the real slot-4 key, the
tag is opaque until ICU-S, and every recovered software-visible verification consequence
is neutralized before upper delivery. Their application/FV4 progression remains valid
evidence, and no zero-vs-dummy MAC road A/B is warranted.

**The apparent stock/message-counter phase difference is not a receiver requirement.**
The native protected `0x0D7` stream shares the FV4+MAC28 trailer and strongly prefers
first-in-epoch message-low2 **1**, while the later Camry B6 sender reanchors at **0**.
That contrast remains a real sender-policy observation, but VAR-146/CORR-177 close its
relevance to B6 admission from exact F33. `90A48` seeds a newer B6 trip/reset epoch by
copying the *received* message-low bits directly into pending message8; it does not
compare them with a fixed 0/1 phase. In the same epoch it reconstructs the next
strictly-forward congruent message8, accepting ordinary gaps +1..+4. The complete
13-route / 530-rlog Camry corpus then shows all 1,696,097 historical B6 sends and all
1,554,213 successful Panda TX echoes have FV4 progressions reconstructable by that
exact algorithm. Routes 45 and 48 start every observed B6 epoch at 0 and remain fully
freshness-admissible. Therefore there is no justified 0-vs-1 A/B test; D7's phase is a
sender convention, not a hidden EPS B6 permission rule. See live-baseline §63.

**The wheel tracks the stock request, corpus-level.** Restricting to samples where both
requests are active ID11 and fresh (≤50 ms), speed > 15 m/s, no blinker, |driver torque|
< 0.7 N.m, and the two requested angles diverge by ≥ 2.5 deg (181 samples across the
three routes): median |measured − stock| = **0.79 deg** versus median |measured − B6| =
**2.02 deg**; the stock request is closer in 134 samples versus 47, and there are 30
samples where stock tracks within 1 deg while B6 is off by more than 3 deg, against 2 in
the reverse direction. This generalizes §4.4's single route-`3c` interval to the whole
corpus. (In the unseparated bulk the B6 error is smaller — median 0.26 deg versus 0.69 —
but that is the openpilot controller closing the loop on the measured, stock-driven
plant and is not authority evidence; only the separated subset discriminates.)

**Transport is exonerated during driving.** All of route `3d`'s 56 bus-off events, its
single CAN core reset, and its receive-error accumulation (REC endpoint 127) fall inside
the final 100 ms of the route — power-down noise — and `canfdEnabled=false` intervals
exist only in the first/last ~0.1 s of each route. The four B6 sends in `3d`'s shutdown
window are the only non-rejected sends without a Panda return. During every driving
window `canfdEnabled=true`, `busOffCnt=0`, and `transmitErrorCnt=0`, while native
traffic (`0x00F` at 10 Hz, `0x0D7` at 50 Hz) and stock LTA functioned on the same bus.
Panda-level transport cannot explain the non-response. (Per CORR-159, Panda TX returns
still do not prove physical ACK; the same-bus native traffic bounds that residual.)

**The EPS raised no observable objection.** In the `0x030` telemetry nibble
(`EPS_STATUS_B6_BIT3 / STEERING_FAULT_INHIBIT_STATUS / EPS_STATUS_B6_BIT1 /
DRIVER_TORQUE_INVALID`), `STEERING_FAULT_INHIBIT_STATUS` and `DRIVER_TORQUE_INVALID`
(alone) are never asserted; `EPS_STATUS_B6_BIT1` appears in 0.3–1.1% of frames and
`EPS_STATUS_B6_BIT3` in 269 frames of each of routes `3c`/`3d` (none in `3b`; 72–73 of
them together with `DRIVER_TORQUE_INVALID`), all transient with the dominant state
zero. No fault latch, no inhibit, no status transition correlates with the B6 phases.
Combined with §4.4 this separates the failure cleanly: the receiver neither acts on nor
visibly rejects three-quarters of a million well-formed frames — silent non-admission
upstream of any observable application reaction, consistent with the unresolved
ingress/freshness/first-rejecting-stage boundary, while the lane-change alert was fully
explained by the former `steeringPressed=False` integration bug (VAR-125; fixed by fork
opendbc `e37bab6c`).

### 4.6 September 4 passive stock-steering observables (VAR-129)

**Scope and grade:** observed, dynamic-trace. A separate read-only reduction of
all **253 segments** from routes `0000003b--62262eb7a1` (110),
`0000003c--97b9e7a69a` (81), and `0000003d--0e812cecba` (62) covers about
252 minutes and counts **27,173,143 native `can` records on Panda buses 0/1/2**.
None is `0x0B6`, `0x131`, or `0x2E4`. Openpilot `sendcan` and Panda TX returns
are excluded from this native census. This is an absence within the logged buses,
not proof of complete vehicle-network coverage, EPS admission, or a stock B6 template.

#### Signal roles

Byte offsets are zero-based. These are passive observables, not transmit instructions.

| Carrier | Predominant captured side | Observable | Interpretation boundary |
|---|---|---|---|
| `0x08A` | Panda bus 2 | B21 request ID; signed BE16 B18:B19 request angle; B24 request level | Stock lateral-request state, not proved EPS authority or transmitter identity |
| `0x081` | Panda bus 0 | signed BE16 B16:B17 steering-reference word | Closely mirrors the `0x08A` request; propagation direction and command-versus-feedback role unresolved |
| `0x025` | Panda bus 0 | existing steering angle/fraction/rate decode | Measured steering, not a requested angle |
| `0x030` | Panda bus 0 | driver torque and B22:B23 mapped motor-feedback proxy | EPS telemetry; ordinary driver assist also produces motor feedback |

The two reference words use the existing `1024/17870` (~0.057302742)
deg/count representation. The `0x030` motor-feedback proxy is not commanded
torque or amperes; its source/scale boundary remains as documented in §1.3.
Panda bus numbers identify harness sides, not Toyota network-domain numbers or
CAN transmitter addresses.

#### Reference relationship and discovery scope

In clean native-ID11 samples, `0x081 B16:B17` versus `0x08A B18:B19` gives:

| Route | Samples | Pearson correlation | Median absolute difference | p90 absolute difference |
|---|---:|---:|---:|---:|
| `3b` | 40,789 | 0.998655 | 0 raw counts | 1 raw count |
| `3c` | 21,990 | 0.999381 | 0 raw counts | 2 raw counts |
| `3d` | 31,607 | 0.996073 | 0 raw counts | 1 raw count |

Method: 20-Hz last-observed samples, signal age at most 75 ms, speed >10 m/s,
absolute raw-decoded driver torque <0.5 N.m, no blinkers, valid torque, and native
ID11. The exploratory byte-aligned signed16 BE/LE sweep over native bus-0/1
payloads, excluding the final four bytes of FD PDUs, ranks `0x081 B16:B17` first
on every route. `0x090` and bus-1 `0x160` also correlate with steering, but that
does not establish another command. Bit-aligned, multiplexed, nonlinear, and
unlogged interfaces remain outside this sweep.

Near-identical references on opposite harness sides do not establish which ECU
originated either value, which direction information propagated, or whether an
EPS accepted it. Event timestamps describe logger publication batches, not
individual CAN arbitration times; no sub-batch causal ordering is claimed.

#### Divergent-request witness

Route `3c`, segment 43, **34.46–35.26 s** contains 17 qualified 20-Hz samples:
native and openpilot requests both active ID11, no blinkers, driver torque
absolute maximum 0.46 N.m, and median speed 25.62 m/s.

| Quantity | Median |
|---|---:|
| Measured `0x025` steering | 3.20 deg |
| Native `0x08A` request | 3.2663 deg |
| Native `0x081` reference | 3.2663 deg |
| Openpilot transmitted target | 6.5325 deg |

This interval is consistent with stock-reference tracking while the openpilot
target is ineffective. It does not establish sole stock control throughout the
drive or localize the EPS acceptance/actuation boundary. Shared road geometry,
driver intervention, and closed-loop controller response confound whole-drive
correlations; a lower aggregate tracking error is not evidence of control ownership.

#### Native ID4 episodes

Re-reading the original rlogs confirms **248 native bus-2 `0x08A` frames** with
the entire B21 byte equal to 4 in five episodes. B24 is 100 in every one.
The existing Toyota dictionary labels ID4 as LDA; the observed fact is the
numeric request state, not an independently proved LDA grant.

| Route | Segment | First–last ID4 frame (s) | Frames | Logged openpilot lateral |
|---|---:|---:|---:|---|
| `3b` | 6 | 28.626–28.907 | 12 | inactive |
| `3c` | 40 | 16.211–18.741 | 102 | active |
| `3c` | 56 | 43.964–45.441 | 60 | inactive |
| `3d` | 56 | 59.294–59.969 | 28 | inactive |
| `3d` | 57 | 19.884–21.012 | 46 | inactive |

Four episodes therefore provide stock request activity without simultaneous
openpilot lateral activation. They are not hands-off experiments: driver torque
is present, and actual EPS grant/actuation is not identified by these records.
The older August two-drive `0/11/18` state census remains scoped to those captures;
it must not be treated as an exhaustive alphabet for this September corpus.

#### Provenance and integration boundary

Times above are seconds from the exact September reducer origin: the earliest
`can`, `sendcan`, `carState`, or `carControl` event in the named segment, not
from startup metadata or ancillary `controlsState`/Panda-health records. Original inputs:
`/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/<full-route>/rlog-<segment>.zst`.
Compressed source SHA-256 identities:

| Route / segment | SHA-256 |
|---|---|
| `3b / 6` | `4395189b7f8f24f4085f978447951a401b34be63907bae180688e57d8e1e0512` |
| `3c / 40` | `73b946a8487c9d8f43d7ffe69287655775beaf595ec1099b6138f885ecb68902` |
| `3c / 43` | `ab6b4fbe4d14227919a022dbc2c3091467446262d6896d26ea021ecc5d54c356` |
| `3c / 56` | `ab3bf83295f653416567b75c770a8af83a847554968015f4fed4f650d6025d15` |
| `3d / 56` | `a02430cf010867fa3486a6d964dc8d832667ad666f2f0c96fe94a2588c8cf3a8` |
| `3d / 57` | `e13dd3880d08c827240017c76119038a65371a7d96149ebc44f4639b5319a793` |

The route `carParams` records identify the Camry platform and Brake firmware but
contain no EPS F181 response. Exact EPS identity comes from separate same-car
evidence, not these rlogs alone. The original September reducer source was
recovered under the disposable `build/tmp/` tree during WP1, which removed the
previous grid-phase ambiguity. The tracked deterministic implementation
`tools/targets/camry/analysis/analyze_camry_20260904_stock_steering.py` now reproduces its exact
absolute-monotonic 50 ms grid and stock/dual-active predicates from the original
rlogs. The tracked report/manifest and independent verifier reproduce the census
(27,173,143 native records; zero native B6/0x131/0x2E4;
751,664/751,628/33 sendcan/return/reject B6), the clean native-ID11 populations
**40,789 / 21,990 / 31,607**, their published 0x081↔0x08A correlations and raw
p90 differences, all **248** raw-byte-exact ID4 frames in five episodes, and the
17-sample route-3c segment-43 witness including its exact
34.458562074–35.258562074 s grid span and medians. The corrected current-cereal
health adapter additionally retains all **150,642** `pandaStates` samples and
reproduces the corpus `safetyTxBlocked` delta of **+19**; it preserves
`controlsAllowed`, RX-check/heartbeat/fault state, and per-bus REC/TEC,
`busOffCnt`, CAN-core-reset count, and CAN-FD-enable state. In particular the
route-3d bus-0 maxima reproduce §4.5's REC=127, TEC=0, bus-off count=56 and one
CAN-core reset. These health observations remain ancillary to the steering
sample time base and predicates. ID4 table times remain quoted
to the original published millisecond precision; frame counts, raw request-ID
bytes, levels, and source timestamps are retained independently.

`data/generated/camry_20260904_stock_steering_manifest.json` additionally pins
every compressed source SHA-256/byte size, parser/openpilot revision, Cap'n Proto
schema hash, service/event counts, first/last live timestamps, gaps/duplicates,
unreadable inputs, and source-publication timestamp regressions. Reduction uses
stable `logMonoTime` ordering only after that source-order quality scan; those
logger publication regressions are therefore reported rather than silently
sorted away. Compact source-derived JSONL fixtures preserve DLC, raw payloads,
control/activity fields and extraction provenance. Deterministic full-population
CSV plus witness/ID4 CSV, readable Markdown and SVG review aids are emitted under
`build/out/camry-20260904-stock-steering/`; they remain disposable review outputs,
not replacements for the source logs.

For integration, retain measured angle and driver validity as measured state,
and request/reference fields as passive observables. Do not promote request IDs
to engagement/readiness authority or replace measured feedback with a target.
The unresolved connection is stock request/reference → EPS acceptance and
actuation. No new steering transmission or message replacement follows from
this passive analysis.

### 4.7 2026-09-06 Toyota hands-off warning carrier and upstream-style HUD replacement (VAR-130 / VAR-138)

The September 6 Chicago outbound/return routes isolate the native Toyota
hands-off warning independently of openpilot driver monitoring. In clean
stock-LTA windows (cruise enabled, >15 m/s, no blinker, native bus-2 `0x08A`
ID11), `0x371/32 B19[6]` enters a short-lived state after a long interval without
meaningful driver steering torque. Using `abs(carState.steeringTorque) >= 0.9 N.m`
as a passive touch proxy, median onset time since the last touch is **15.84 s** on
route `3e` and **15.60 s** on route `3f`; the same state clears immediately after
renewed torque. That 0.9-N.m proxy is deliberately conservative and is **not the
Toyota timer threshold**; the driver-detector reduction below recovers the actual
countdown reset much more tightly. The earlier September-4 route `3d` gives the
same ~16.5 s proxy median, so this is Toyota-native behavior rather than a consequence of the September-5
`steeringPressed` integration fix. All 43/43 route-`3e` and 63/63 route-`3f`
qualified onsets occur while openpilot remains enabled, `CC.latActive` is true,
`steeringPressed` is false, and the latest transmitted B6 is active ID11.

A native FRC-side `0x412/8` HUD transition is edge-locked to that state. The
common active-LTA payload is `14 00 00 44 01 ee 93 07`; the warning form is
`14 0c 00 44 01 ee 93 07`, i.e. **B1[3:2] changes to `3`**. Route `3f` contains
six escalation frames `14 0c 40 44 01 ee 93 07`; every one occurs while the
`0x371` warning candidate is active, making **B2[6]** a bounded escalation
candidate. Exact OEM CAN-bit names are not transferred. Current recovered
Techstream Operation-FFD vocabulary independently exposes FRC-hosted
`Hands-Off Judgment Flag` (`5601`), `Hands-Off Message` (`5612`), `Hands-Off
Buzzer Request` (`5615`), and `Hands-Off State` (`5632`), but there is no static
DID-to-`0x412` bit join.

The same route also closes the **replacement cadence** rather than borrowing the
older Toyota controller's 5-Hz UI schedule. On route `3f`, 5,305 same-segment
`0x412` intervals have median **1002.490 ms** (p10 **701.920 ms**, p90
**1004.749 ms**) and minimum **79.514 ms**. The 367 intervals whose payload
changes have median **432.440 ms** and minimum **79.514 ms**. Route `3e`
independently gives a **995.572-ms** median heartbeat and **82.526-ms** minimum.
Thus the source is a roughly **1-Hz periodic heartbeat with event-driven
publications**, not a constant 5-Hz stream. The fork replacement follows that
shape: stable HUD state is refreshed at 1 Hz, while changed display state is
rate-bounded to 10 Hz. This timing result describes the observed camera-owned
HUD surface only; it does not assign an OEM scheduler name or prove the minimum
permitted receiver interval.

The Toyota `Hands-Off` vocabulary is **overloaded and must not be treated as one
state machine**. The same PCS recorder dictionary separately exposes capability
fields `Hands-Off Exist` and `LTA Driver Monitor Camera Collaboration Exist`, plus
`Hands-Off Main SW ... Customize` / driver-image-recording customization. Those
are strong evidence for a distinct driver-camera-backed hands-free LTA feature.
Likewise the EPS Target-Lateral dictionary's profile **10 = `Hands Off LTA`** is
a separate cooperative-control mode from ordinary **11 = `LTA/LCA`**. In both
September-6 routes the warning/escalation occurs while `0x08A` remains ID11 and
ID10 is never observed (route 3e IDs `{0,4,11}`; route 3f `{0,11}`). Therefore
`Hands-Off Control Condition` in FRC DID `0x1601` and Target-Lateral ID10 are
**not evidence for the normal wheel-nag state and must not be used as a proposed
nag-disable control** without an independent join. The retained same-car FRC
Operation-FFD `2818/0100` record closes this distinction directly: DID `0x5609`
is `f8c0`, which decodes through the recovered current PCS schema as **LTA
Exist=1**, **Hands-Off Exist=0**, and **LTA Driver Monitor Camera Collaboration
Exist=0**. Thus this exact Camry has ordinary LTA and its wheel-contact warning,
but not Toyota's driver-camera-backed hands-free LTA capability. For the ordinary
Camry LTA nag, the relevant Toyota vocabulary is the explicit
judgment/message/buzzer/cancel-by-hands-off family above.

Current GTS+ also makes clear that **TSS3 hands-on sensing is not intrinsically
torque-only across the fleet**. The recovered TSS3 PCS Operation-FFD dictionary
contains `5222 = Touch sensor presence` (`タッチセンサ有無`) as an explicit
TSS3 configuration datum, and the current category-498 `FRC_P5` DTC table contains
`C1A7796 Steering Touch Sensor / Component Internal Failure`. The ordinary
`FRC_P5` Data List does not expose a corresponding `touch vs torque` mode selector,
so those two facts prove TSS3/FRC support for steering-touch hardware but do not,
by themselves, prove whether a particular calibration uses touch **instead of**
torque or fuses both inputs. Toyota's 2026 Camry product matrix independently
closes the production-hardware side: TSS 3.0 is standard across the listed Camry
trims, while an XSE steering-wheel package is explicitly offered **with touch
sensor**. See the official [2026 Camry eBrochure](https://www.toyota.com/content/dam/toyota/brochures/pdf/2026/camry_ebrochure.pdf).

The XW60 Prius parts catalog supplies a stronger configuration join than trim
marketing. Toyota names the wheel controller `864A1A Computer, Multiplex Network
Steering` and splits its applications by safety package: `864A1-47010` appears in
TSS3 **BASIC** / cold-area combinations, while `864A1-47020`, `-47021`, and
`-47030` are explicitly listed for **ACTIVE SAFETY PACKAGE-TSS3 EXPANDED**
applications (with `-47031` superseding `-47030` in some applications). The
service manual independently shows the same controller has separate connectors
for **w/ Steering Touch Sensor** and **w/ Steering Heater**. This makes `5222`
look exactly like what its OEM name says: a vehicle/configuration presence datum,
not a continuously varying touch state. Sources:
[XW60 steering-wheel parts matrix](https://www.toyotapartsdeal.com/parts-list/2024-toyota-prius/power_train_chassis/steering_wheel.html) and
[XW60 controller service procedure](https://www.mytoyo.com/heated_steering_wheel_controller-2728.html).

The wider diagnostic corpus supplies useful boundaries for that configuration.
Same-generation `LDA_P5` (a predecessor semantic oracle, not a production
category-498 peer) exposes two independent judgments: DID `0x1044` **Not Holding
Steering Wheel Judgment Status (Torque Sensor)** and DID `0x1045` **... (Touch
Sensor)**. Successor `ADCU_P6` makes the source model explicit at DID `0x1B10`
**Steering Wheel Hold Detection**: `0=Release Detection`, `1=Hold Detection
(Steering Touch Sensor)`, `2=Hold Detection (Torque Sensor)`, and `3=Hold Detection
(Steering Touch Sensor and Torque Sensor)`. P6 is terminology-only evidence for
TSS3, but the four-state enum shows Toyota treats touch and torque as separable,
combinable hands-on inputs rather than synonyms.

Driver-camera attention is a third, separate dimension. Current `FRC_P5` exposes
DID `0x1210` **Drive Monitor Equipped** and DID `0x2129` **PCS Drive Monitor Early
Warning Function**; the TSS3 recorder separately carries `5509 LDA Driver Monitor
Camera Collaboration Exist`, `5609 LTA Driver Monitor Camera Collaboration Exist`,
and `5633 Driver Monitor Camera Warning Reasons`. These must not be collapsed into
the wheel-contact detector: a vehicle may have torque/touch hands-on sensing,
driver-monitor-camera functions, or both, and this exact Camry's retained `5609`
record says the LTA driver-monitor-camera collaboration feature is absent.

Toyota patent US20220001874A1 (priority 2020-07-01) independently documents that
same conceptual split for a hands-off-capable automated-steering system: a
**steering touch sensor** produces separate hands-on/hands-off "steering holding
information", while a **driver monitor** separately verifies surrounding/visual
confirmation and can influence the notification timer. The patent contains no
steering-torque sensor or torque threshold, and its illustrative ~10-minute
hands-off prompt interval is not the exact F33 ordinary-LTA ~13-second state
machine. It is therefore architecture/terminology corroboration, not a timer or
sensor implementation transferred onto this Camry. Deep review:
[`../architecture/toyota-driver-monitoring-us20220001874.md`](../architecture/toyota-driver-monitoring-us20220001874.md).

The steering-touch transport can now be bounded much more tightly. Toyota's XW60
Prius service data identifies the wheel electronics as a **Multiplex Network
Steering ECU (Touch Sensor)** inside the steering-wheel assembly; its terminal
`A-2` is explicitly **CXPI**. The same service data says FRC `C1A7796` is set when
the FRC receives a malfunction signal from that touch ECU, and FRC RoB `X2501`
records a **CXPI communication error between the multiplex network steering ECU
and combination meter received from the combination meter**. The SRS Vehicle
Control History independently describes `Grip Sensor Value (Left)` and `(Right)`
as left/right steering-touch detection (`Hands OFF` / `Hands ON`) and its invalid
flag as the validity of **received CAN data**. Public corroboration:
[XW60 front-camera service data](https://www.mytoyo.com/front_camera_system-1160.html),
[XW60 heated-wheel/CXPI terminals](https://www.mytoyo.com/heated_steering_wheel_system-2729.html),
and [XW60 SRS Vehicle Control History](https://www.mytoyo.com/airbag_system-4003.html).

The pinned GTS+ master closes the architectural placement without relying on the
service-manual drawings. Exact current NA CAN-Bus-Check entries for **Camry HV
12984, Prius 12933, Grand Highlander 12970, and RX350h 12968** all resolve the
same relevant shape: **Front Camera Module = Bus 1; Combination Meter = Bus 3;
EPS + spiral-cable/steering-angle sensor = Bus 4**. No touch/grip ECU appears as
a CAN node. A three-region install-set census also finds **zero** co-occurrence
between category 498 `FRC_P5` and every diagnostic category named Steering Pad,
Combination Switch, or Switch Module under the Steering Wheel; the apparent
category-811 under-wheel module is an unrelated generation-19/PSA-family entry.
Thus the capacitive wheel electronics are a **CXPI subnode behind the combination
meter**, not a hidden standalone TSS3 CAN/GTS ECU.

Current `A_B_CAN_P5` DDR data adds the downstream consumer side. Table 147 has six
consecutive records keyed **5500..5505**: left grip twice, right grip twice, then
two grip-validity records. Current `KgpDataCtrl.dll` independently proves the
`CDbDDRMonitorTable` key is the `u16` at row `+0x18` (`FindDbItem1` and
`ComparativeKey` both consume it); `GetExceptahandId` instead reads `+0x28` and
`GetExceptahandFlag` reads `+0x2D`. Therefore these decimal `5500..5505` values
are **SRS DDR-local monitor keys, not CAN IDs**. Following those keys into table
149 `CDbDDRAddressTable` does not reveal a wire carrier either: the host looks
that table up by selector bytes `+0x0A/+0x0B` and then local monitor key `+0x04`,
and the same grip key appears in multiple selector contexts with different
recorder-layout fields (`0x24` vs `0x60`). Table 150 independently pairs the
left/right values with local validity keys. This closes the GTS DDR-address path
as **recorder payload geometry**, not CAN routing. The TSS3 FRC Operation-FFD
namespace independently uses numeric IDs `5501` and `5505` for unrelated LDA
state/failure records, so numeric recorder IDs are not a cross-ECU wire namespace.

A tempting CAN candidate was explicitly rejected. The tracked 2021 Venza SRS
CodeFlash has four live SecOC receive profiles; the `0x024` profile maps to
application Rx PDU **14**, while both the ordinary Rx descriptor table and the
hardware acceptance table independently map index 14 to physical CAN-FD
**`0x024`**. That proves `0x024` is real traffic, but nothing in that firmware
joins it to grip sensing. More importantly, the retained Camry September-6
routes `3e` and `3f` contain **zero `0x024` frames on the comma-exposed buses**.
So `0x024` must not be promoted to the Camry touch carrier from the Venza SRS
profile alone.

The recovered path is therefore:

```text
capacitive wheel electrode
        -> Multiplex Network Steering ECU
        -> CXPI
        -> Combination Meter
        -> [unrecovered CAN/gateway publication]
        -> FRC / SRS consumers
```

The bracketed hop is the remaining RE boundary. We still need the exact
post-meter arbitration ID, bit positions/validity encoding, gateway transform,
and FRC parser. The cleanest closure is a touch-equipped TSS3 capture (for
example a touch-wheel Camry, XW60 Prius, Grand Highlander, or RX). **The FRC-side
Bus 1 is sufficient to discover the forwarded grip carrier**: hold the wheel
stationary with EPS torque near zero and dwell through four labeled states —
`neither`, `left only`, `right only`, `both` — while recording all FRC-side
traffic plus native EPS `0x030` and FRC `0x371`. Search each arbitration ID for
payload bits whose conditional state follows left/right touch independently,
while ignoring rolling/freshness/MAC fields. If `0x371 B20[4]` follows touch while
`0x030` remains near zero, that also directly proves the FRC's low-sensitivity
hands-on detector accepts the capacitive path independently of torque.

A direct tap on the **Combination Meter's Bus 3** is only required for the second
question: proving the meter-origin publication and any Central-Gateway transform
before the frame reaches FRC Bus 1. Toyota's SRS VCH gives an independent semantic
oracle for the four test windows: `Grip Sensor Value (Left)`, `Grip Sensor Value
(Right)`, and `Grip Sensor Value Invalid Flag`. The DDR-address selector values
`0x16/0x19/0x1B` are decimal **22/25/27**, exactly the VCH snapshot groups Toyota
lists for these grip fields; this is another direct confirmation that table 149
contains recorder-case geometry rather than vehicle-network IDs.

If a static image is easier to acquire than a car, the best current XW60 targets
are the **89170-47B60** SRS ECU (CYT2B93BAC is reported for this part family) and
the Yazaki **83800-4E47x / 83800-4E48x** combination-meter families. Neither an
89170-47B60 application image nor a 83800-4E47x/4E48x meter image exists in the
tracked CUW/firmware corpus, and the current public search produced part/service
references but no usable firmware dump. A plaintext image of either ECU should
close the bridge from the opposite direction: SRS RX parsing or meter CXPI->CAN
publication. The reproducible static evidence for the recovery so far is generated
by `tools/techstream/extract_gtsplus_tss3_steering_touch_path.py` into
`data/generated/gtsplus_2026/tss3_steering_touch_path.json`.

The September-6 CAN corpus also exposes the reset side of the ordinary nag state
machine. In clean ID11 LTA, `0x371 B20[4]` is a strong low-sensitivity
**driver-steering-detected candidate**, while `B17[0]` is its exact structural
complement. Across **33,621** clean `0x371` samples from routes `3e+3f`, there are
zero complement violations and zero frames where `B20[4]` and the `B19[6]`
warning state are simultaneously asserted. The dominant raw tuples are:

| observed state | `B17[0]` | `B19` | `B20` | interpretation boundary |
|---|---:|---:|---:|---|
| no-touch / pre-warning | 1 | `0x20` | `0x03` | driver detector clear; warning clear |
| driver steering detected | 0 | `0x20` | `0x13` | `B20[4]` asserted; warning clear |
| warning/judgment | 1 | `0x40` | `0x03` | warning asserted; driver detector clear |

The driver-state join is independently anchored to exact-F33 EPS telemetry rather
than to openpilot's `steeringPressed` policy. Native chassis-side `0x030` carries
physical driver torque as `signed(B8)*0.1 + signed4(B17[3:0])*0.01 N.m`; native
`0x371` is published on the FRC side. In route `3e`, `B20[4]` is present in only
**1.79%** of samples below 0.25 N.m but **95.72%** at 1.0–1.25 N.m; route `3f`
gives **2.08%** and **94.18%** respectively. Sampled detector-set transitions
have median absolute EPS torque **0.67 N.m** on both drives, while detector-release
transitions have medians **0.37/0.34 N.m**. These are dynamic hysteresis-like
transition distributions, **not an exact Toyota threshold**: `0x371` is slower
than `0x030` and rlog publication is batched. Current Toyota prior art provides
conceptual corroboration only: the older 8-byte `0x371 LTA_RELATED` layout names
a low-sensitivity `STEERING_PRESSED` signal, but that historical bit layout is
not transferred to this 32-byte TSS3 carrier. The current PCS OEM label
`560D Driver Steering Control Detection Status` (`保舵検出状態`) is likewise a
semantic match, not yet a static DID-to-CAN-bit mapping.

Using Toyota's own candidate instead of the 0.9-N.m proxy collapses the countdown
timing. The warning follows the most recent `B20[4]` **detector-release** transition
at almost exactly **13.0 s**: routes `3d`, `3e`, and `3f` all have median release-to-
warning times of ~13.00 s, with the 10th–90th percentile confined to roughly
**12.88–13.09 s**. The last asserted detector sample precedes warning by ~13.16 s,
consistent with the ~5-Hz `0x371` publication interval. This is strong evidence
that the FRC's ordinary-LTA countdown is reset by its low-sensitivity driver-
steering detector; the earlier ~16-s number reflects the deliberately higher
0.9-N.m analysis proxy, not Toyota's internal timeout.

Warning recovery follows that candidate directly. Of 43 qualified route-`3e`
warning clears, 38 already have `B20[4]` asserted on the clearing `0x371` sample;
route `3f` has 51/63 on the same sample and **56/63 within 0.35 s**. The remaining
clears include state/eligibility changes and do not establish a second reset
mechanism. Direction is also consistent with an FRC-derived judgment: on route
`3f`, `0x030` is overwhelmingly native Panda bus0 (501,427 native vs 1,185
bus2-side copies), while `0x371` is overwhelmingly native bus2 (26,948 native vs
64 bus0-side copies).

The exact-F33 transmit closure now upgrades the input side of that model from a routing
inference to an ECU identity. `0x030` is generated by the EPS as PDU0, routed through the
configured SecOC-Tx profile with DataID `0x0030`, and authenticated by ICU-S command 5 /
selector 4 before appearing on wire as `B0..B27 || FV4 || MAC28`. Therefore the physical
driver-torque quantity correlated with `0x371 B20[4]` is an **authenticated EPS-origin
publication**, not a stale DBC alias or another ECU's reused message. Combined with the
FRC's `U013187 Lost Communication with Power Steering Control Module A / Missing Message`
diagnostic dependency and the 13-s detector-release timing, the strongest current model is
**EPS 0x030 driver torque/state -> FRC driver-steering judgment -> FRC hands-off timer/state
publication -> 0x412 warning/escalation**. The remaining proof boundary is inside the FRC:
we have not yet statically identified its literal `0x030` parser/filter/comparator, so the
exact Toyota hysteresis/filter algorithm stays open.

There is a second timed warning stage. Route `3d` has one episode where
`0x412 B2[6]` first asserts **5.996 s** after `B19[6]` warning onset. Route `3f`
has three such episodes; their first escalation appears at 5.876–5.979 s after
warning onset (median **5.977 s**). Every escalated episode remains Target
Lateral ID **11** throughout. No retained September-6 episode reaches a Toyota
LTA-cancel transition; the driver-steering detector asserts first. Therefore the
current corpus proves `warning -> ~6 s escalation -> driver acknowledgment` but
not the timing or wire state of the later `Cancel Condition by Hands-Off` stage.

Newer Toyota P6 diagnostics provide a useful **semantic-only successor oracle**:
ADCU_P6 exposes separate `Hands-Off Duration` (ms), `LTA Driver Hands-On Flag`,
`Hands-Off Judgment Result`, and `EDSS Request Due to LTA Hands-Off` fields. This
matches the state decomposition above—duration accumulation, hands-on detection,
judgment, then later emergency/cancel handling—but no P6 wire position or numeric
state is transferred to this P5 Camry.

This changes the boundary of the `0x412` replacement. `0x412` is demonstrably a
presentation output of a deeper FRC state machine. Blocking/replacing it can hide
the observed cluster presentation fields, but there is **no evidence that doing so
resets the FRC's internal hands-off duration or prevents its eventual LTA cancel**.
That distinction matters on this Camry while stock ID11/FRC lateral authority is
still active. The decisive next observation is a normal warning captured with
synchronized native `0x030/0x371/0x412` plus read-only FRC Operation FFD,
prioritizing `560D`, `5601`, `5612`, `5615`, `5632`, and `550D`; a later
post-warning `AB11/AB12/AB13` read can also reveal whether the cancel/late-hands-on
RoB families become retained on this calibration.

The torque path is more nuanced than a single "driver touched / override" threshold. Current
Toyota diagnostic vocabulary explicitly separates the two concepts. On this exact P5/FRC
recorder, `560D` contains both **Driver Steering Control Detection Status** and a separate
**LTA Driver Steering Control prohibited** byte, while recorder objects `5774` and `5776`
are independently named **Driver steering override** and **Driver steering override for
steering**. For `5774/5776`, `SupportDID=1` is **not** a claim that SID `22` can read
those recorder IDs directly: recovered PCS Viewer `MeasuredValue::CheckSupportDataID` uses it
as a record-local support-bit gate in the byte immediately preceding the value. The read-only
Operation-FFD decoder now applies that gate. The current P6 successor likewise exposes separate
`LTA Driver Hands-On Flag` and `LTA Inhibition By Steering Override` monitors. An independent P5 Advanced-Drive
record (`ADS_Eth_P5`, DID `0x1E0F`) makes Toyota's intended state split especially explicit:
its repeated Driver Steering Condition snapshots use the three-value dictionary
**Not Steering / Steering(Low) / Steering(High)**. Those cross-system names do not transfer
a numeric threshold to this Camry, but they strongly reject the model that the first
hands-on detection necessarily implies steering override.

Same-car CAN supports the low side of that split. `0x371 B20[4]` has median physical-torque
set/release transitions of about **0.67 / 0.34--0.37 N.m**; in routes `3e/3f` its
assertion probability is already **90.1% / 86.4% at 0.75--1.0 N.m** and
**95.7% / 94.2% at 1.0--1.25 N.m**. Thus there is a plausible low-steering operating band in which a torque
observation can reset the ordinary hands-off timer without necessarily reaching Toyota's
higher steering-override/prohibition state. The exact upper boundary, duration filter and
sign dependence of that higher state are still unrecovered.

The public request plane does **not** provide that missing threshold. A full 12-route road
scan found nine direct `0x08A` ID11->ID0 transitions while cruise remained latched and no
blinker was active. Seven occurred with both model lane probabilities >=0.7, but their
instantaneous absolute EPS torques span **0.23..1.37 N.m** and several occur with the
low-sensitivity `B20[4]` detector itself clear. Therefore an ID11->ID0 edge is not a clean
"steering override" oracle; request withdrawal has other causes. Likewise the exact-F33
EPS contains a separate 2.00-N.m torque predicate in its own service/diagnostic logic, but
there is no evidence connecting that EPS-local predicate to the FRC LTA override threshold.

This reopens the synthetic-`0x030` idea as a **bounded experiment**, not as production code.
The useful discriminator is to characterize the low/high split directly. Current GTS+ gives
us a particularly promising trigger candidate: FRC RoB **`0x209D = LCS Steer Override`** is
configured at 0.2-s sampling with 36 pre-trigger and 8 post-trigger samples. No retained
same-car `209D` record has been observed yet, so its relationship to ordinary ID11 LTA remains
a dynamic join rather than an assumed threshold oracle. Neighboring RoBs independently
name **`0x2845 = LTA Hands Free Cancel`**, **`0x2846 = CSF Hands Free Warning Operation`**,
**`0x229C = Late hands-on timing`**, and **`0x229F = End of hands-off control`**. A slow real-
torque sweep during ordinary ID11 LTA, with native `0x030/0x371/0x08A/0x081/0x412` capture,
can therefore test whether `209D` fires at the high/override transition; if it does, the retained
pre/post window brackets that transition directly, and fetching the stored Operation-FFD record
can search for `560D`, `5774`, and `5776` around the same event, honoring each field's
record-local support bit when present. This is a much cleaner
experimental discriminator than treating any public request withdrawal as override. The
existing read-only `camry_frc_operation_ffd_capture.py` already defaults to `209D` and now
highlights `550D/560D/5774/5776`; after such a road event the focused fetch is simply
`--rob 0x209D`. Only after the physical low/high boundaries are pinned should an
ephemeral one-shot `0x030` substitution test whether a small signed EPS-origin torque value
is interpreted identically by the FRC. That test must also preserve the packet's **inner B7
additive checksum**: changing only B8 in the already-packed COM buffer and then letting SecOC
sign it produces an authenticated but internally inconsistent `0x030`. The clean experiment
is either to alter the torque staging value before `0x4C97A` packs PDU0, or to update B8 and
recompute B7 before the recovered SecOC-Tx path consumes B0..B27. A periodic keepalive should
remain out of `CarController`, Panda safety, and the resident signer until that discriminator
is complete; the reason is now **unknown higher-threshold behavior**, not an assumption that
every synthetic torque sample triggers override.

The retained reduction is generated by
`tools/targets/camry/analysis/analyze_camry_2026_driver_steering_threshold_split.py` into
`data/generated/camry_2026_driver_steering_threshold_split.json`.

Current upstream Toyota explains how comma normally removes the wheel-nudge nag.
`0x412` is a camera-owned replacement message in Toyota Panda safety
(`TOYOTA_BASE_TX_MSGS`, bus 0, `check_relay=true`), so the stock camera's `0x412`
is statically blocked across the relay and `CarController` transmits openpilot's
own `LKAS_HUD` instead. The legacy `STEERING_LTA.CLEAR_HOLD_STEERING_ALERT` field
is **not** the mechanism: upstream has hardcoded it to zero for years. The native
shape for the Camry is therefore the same message-ownership pattern, not a new
hands-off permission system.

The same September-6 corpus also closes the ordinary **lane-line display** state
alphabet far enough to replace opaque copying in the symmetric cases. Across all
**5,389** native bus2 `0x412` frames in route `3f`, B3's high/low nibbles are
`(4,4)=3,375`, `(2,2)=1,181`, `(1,1)=561`, `(1,2)=139`, `(2,1)=131`, plus two
startup `(0,0)` rows. Same-route `modelV2.laneLineProbs[1:3]` joined within 200 ms
supports `(4,4)` as active-LTA recognized lines, `(1,1)` as inactive recognized
lines, and `(2,2)` as weak/missing lanes. The active stock-LTA tuple is
B0=`0x14`, B3=`0x44`, B4=`0x01`; the inactive road tuple uses B0=`0x12`,
B4=`0x02` and nibble states `1` versus `2`.

Two boundaries matter. First, value `3` is **not globally absent**: route `3b`
contains four `(2,3)` frames, so its departure/color meaning remains unjoined and
is not synthesized. Second, modelV2 does not conclusively identify which B3
nibble is left versus right. The asymmetric `(1,2)/(2,1)` population mildly
supports one orientation in aggregate but is not direction-discriminating on all
routes (for example route `3e` contradicts the simple probability ordering and
route `3f`'s `(2,1)` visibility fractions are equal). Current Toyota Operation-FFD
supplies an exact passive oracle under DataID `5514`: `Left Lane Display`, `Right
Lane Display`, and `Steering Symbol Display`. A synchronized `5514` + `0x412`
capture can close side orientation without guessing.

Fork opendbc therefore follows the normal Toyota ownership pattern for TSS3
Camry while rendering only the HUD semantics whose direction is actually known.
`TSS3_LKAS_HUD` is parsed as an eight-byte FRC-side source and Panda treats
`0x412` bus 0 as a replacement TX object with `check_relay=true`. The controller
now **fully preserves** noncanonical modes such as retained B0=`0x10` frames,
including warning/escalation bits; canonical B0=`0x12/0x14`, B4=`2/1` road frames
alone are rewritten. Symmetric lane visibility can be rendered directly because
it is orientation-free. For asymmetric left/right requests, the controller keeps
the stock frame's existing high/low nibble orientation and only translates a
recognized nibble between inactive state `1` and active state `4`; it does not
guess which nibble is left. B1 `0x0C` is owned by openpilot's `steerRequired`
visual and B2 `0x40` remains suppressed only on those canonical road frames. It
also does **not** synthesize `leftLaneDepart/rightLaneDepart`: state `3` is real
but its semantics are not joined. There is no second permission state or
controller-side steering gate. Post-patch on-car cluster behavior and the
`5514` side-orientation join remain passive follow-up measurements.

Evidence and reproduction:

- `tools/targets/camry/analysis/analyze_camry_20260906_hands_off_warning.py`
- `data/generated/camry_20260906_hands_off_warning_audit.json`
- source routes `2026-09-04/{3b,3c,3d}` and `2026-09-06/{3e,3f}` under the
  maintainer Camry rlog archive
- fork opendbc Toyota safety/controller tests in
  `opendbc/car/toyota/tests/test_tss3_camry.py`

### 4.8 PDA / SDG lateral profiles: Proactive Driving Assist is not a second EPS ingress (VAR-131)

Toyota's customer-facing **Proactive Driving Assist (PDA)** name resolves an otherwise
confusing part of the generation-20 lateral-ID dictionary. Current Toyota owner
documentation divides PDA into steering, obstacle-anticipation and deceleration
functions; PDA steering operates while the driver is manually driving and is canceled
when DRCC/cruise is operating. The current TSS3 recorder supplies the firmware-side
distinction that matters on this Camry. RoB `22B4`, named **`PDA(SA)Rapid steering by
the customer during control`**, is assigned `SystemType=6`, `SystemName=SDG`. Thus
Toyota itself places **PDA Steering Assist (PDA-SA)** in the recorder's **SDG** system
family. PDA obstacle-anticipation assist is represented separately: `5A09/5A0A/5A0D`
carry a six-bit lateral request ID, signed request pinion angle, steering-support gain,
and damping gain. Those are the same semantic ingredients as the generic `5282`, LDA
`5531`, and LTA `5631` lateral request tuples, though PDA-OAA splits them across DIDs.

The same-car stored Operation-FFD corpus provides a positive SDG request/grant witness.
Record `2294/0001` contains `5282=1200173200`: generic request **ID18**, request pinion
`+0.023`, assist gain `0.50`, damping `0.00`; the same record carries
`5285=12`, so the arbitration-result lateral ID is also **18**. This is direct evidence
that ID18 is a real granted FRC lateral request on this car. Combined with the recorder
classification above, the strongest current identity is **ID18 = the PDA-SA/SDG
steering family**.

Exact F33 then closes the EPS-side architecture. Protected B6 signal261 is Toyota
`Target Lateral ID`; `FUN_000CEFFC` maps the accepted request identities onto one common
controller-bank selector: `1->0` PCS, `4->1` LDA, `11->2` LTA/LCA, `10->3` Hands-Off
LTA, **`19->4` PDA**, and **`18->5` SDG**. Fifty exact-image functions consume the
resulting `FEBECB00` selector, including the same return/dither, speed/angle-dependent
gain, limit, and cooperative-contribution machinery. The exact-image direct-consumer
census finds no ID19-specific target-snapshot branch outside `CEFFC`. PDA and SDG are
therefore **distinct calibration profiles inside the same protected B6 external
steering controller**, not a recovered second EPS command interface.

There *is* a second unusual target-native consumer, but it is not PDA.
`FUN_000CB73A` compares the same Target-Lateral-ID snapshot against ASCII `'1'` =
`0x31` = decimal **49**, which Toyota names **Self-Propelled Transport**, and drives the
separate self-terminating transient machine recovered in the exact-F33 command cone.
That is the special path that must remain separate from ordinary B6 profile selection.

The road corpus is consistent with the feature split. In route `3b`, ID18 appears
34,167 times; under a deliberately broad PDA-SA operating-regime proxy (fresh
CarState, cruise off, 10..140 km/h), ID18 contributes **33,703 / 52,653** native
`0x08A` frames. Routes `3c`, `3d`, `3e`, and `3f` each retain >30,000 frames in that
same proxy but contain **zero ID18** there. A supplemental pre-September-1 scan of
186,934 native `0x08A` frames across routes `27/29/2a/2c` adds 16,876 ID18 frames.
Across all of these scans **ID19 is never observed**. The disappearance of ID18 after
the user's recent PDA setting change is strong supporting evidence for the PDA-SA/SDG
join, but the exact setting-change timestamp is not used as a causal proof.

The remaining boundary is important: current Toyota diagnostics explicitly reserve
Target Lateral ID `19=PDA`, and PDA-OAA has its own pinion-angle/gain request tuple, so
**PDA-OAA -> ID19** is the strongest architectural interpretation. No same-car native
ID19 episode has yet been captured, however, so that subfeature-to-wire join remains
unproved dynamically. Nothing in this finding authorizes selecting ID18 or ID19 from
openpilot; the normal openpilot profile remains ID11/LTA-LCA.

Deterministic evidence: `tools/targets/camry/analysis/analyze_camry_2026_pda_sdg.py`,
`data/generated/camry_2026_pda_sdg_attribution.json`, and
`tests/verify_camry_2026_pda_sdg.py`, joined to the exact-F33 target and current TSS3
managed recorder artifacts.


### 4.9 Full road-corpus lateral-family census and exact-F33 profile switching (VAR-132)

The steering investigation is no longer scoped to LTA/ID11. A complete retained-road
census now treats Toyota's **Target Lateral ID** as one shared request-family selector
and keeps the three observable planes distinct:

1. native upstream `0x08A/32`, whose B21 low six bits carry the request-side Target
   Lateral ID and whose B18:B19 carry the request/reference angle;
2. native chassis-side protected `0x081/32`, whose B13 low six bits mirror the same
   family identity and whose B16:B17 carry the corresponding reference quantity; and
3. protected `0x0B6/32` / PDU44, the only positively recovered **external** Target
   Lateral ID plus target-angle ingress accepted by exact F33 EPS.

The selected corpus contains **12 retained road routes / 513 rlog segments**: archive
routes `1c/27/29/2a/2c`, relay-open route `2d`, Sep-1 route `37`, all Sep-4 routes
`3b/3c/3d`, and both Sep-6 routes `3e/3f`. Route `1c` emits LogReader's
`Corrupted events detected` warning and is retained only as a marginal-motion case; its
recoverable `0x08A` population is entirely ID0, so it supplies no positive steering-
profile witness. Across the selected corpus the request-side census is **1,219,584
native `0x08A` frames** with exactly four observed identities:

| Target Lateral ID | Toyota meaning | Frames | Nonzero episodes | Request-level geometry |
|---:|---|---:|---:|---|
| 0 | No Request / manual | 512,847 | — | mixed inactive/reference state |
| 4 | LDA | 298 | 6 | B24=100 in every frame; 146 cruise-off / 152 cruise-on |
| 11 | LTA/LCA | 653,586 | 165 | B24=100 and the `0x08A` cruise latch set in every frame |
| 18 | SDG / PDA-SA | 52,853 | 81 | cruise-off and B23=`0x20` in every frame; B24=50 on 27,837 and 25 on 25,016 |

No road frame in this corpus uses exact-F33 steering profiles `1=PCS`, `10=Hands Off
LTA`, or `19=PDA`, nor any of the wider generation-20 IDs such as AP/Remote
Parking/Lv3/Lv4/Self-Propelled Transport. The request plane also switches directly
between **nonzero** families without publishing ID0 in between: the full census contains
28 direct `18->11`, one `18->4`, two `11->4`, and two `4->11` transitions. That is an
FRC/request-plane observation only; it does not by itself prove what any downstream EPS
accepts.

The chassis-side `0x081` join makes the shared-family interpretation much stronger.
Across **1,016,141** pairs where a native bus0 `0x081` publication has a latest native
bus2 `0x08A` no older than 100 ms, the B13/B21 Target-Lateral identities agree in
**1,015,978 / 1,016,141 = 99.9839589%**. The returned-state population itself is
`0:427,400`, `4:248`, `11:544,673`, `18:44,045`; the small disagreement set is
concentrated around family transitions and includes the newly recovered ID4 state.
This is the first broad road-corpus proof that LDA, LTA/LCA, and SDG/PDA-SA are not
separate ad-hoc request encodings: they occupy one request/reference identity family on
both sides of the accessible relay.

The exact-F33 CodeFlash answers the corresponding EPS question. `FUN_000CEFFC` starts
every invocation with controller bank 7/default and, only when `FEBEACBD==0` and
`FEBECAFF==1`, maps the **current** B6 Target Lateral ID snapshot directly to a common
controller bank:

```text
1  PCS            -> bank 0
4  LDA            -> bank 1
11 LTA/LCA        -> bank 2
10 Hands-Off LTA  -> bank 3
19 PDA            -> bank 4
18 SDG            -> bank 5
```

The selector has no DRCC state, LTA-switch state, cruise-latch state, prior Target
Lateral ID, or elapsed-time ownership input. The exact raw B6 unpacker
`FUN_0004BD46` likewise accepts a new PDU44 generation from COM health plus generation
change and does **not** compare the new Target Lateral ID against the prior one. Across
the complete exact-F33 decompilation corpus, `FEBECB00` has only the default initializer
and `CEFFC` as writers. Therefore there is no recovered rule of the form "ID11 was
accepted, so reject ID18/ID4 for N milliseconds." A valid newly delivered B6 can select
a different profile on the next controller pass.

This does **not** mean the EPS blindly actuates any received value. The profile selector
is downstream of the normal protected-PDU admission/health machinery and the common
controller retains ordinary speed, angle/rate, fault, slew/limit and persistence state.
PDU44 still has the exact **seven 5-ms foreground-tick / nominal 35-ms communication
loss supervision**. `FUN_000CEF26` also uses profile-indexed threshold/persistence
calibrations (96 cycles; threshold 1280 for LDA/LTA/Hands-Off-LTA/PDA, 1536 for PCS,
2048 for SDG) that feed common readiness/fault state. These are controller supervisors,
not a Target-Lateral-ID ownership timer: `CEFFC` continues to recompute the selected bank
from the latest delivered ID every pass.

A complete exact-F33 direct-consumer census of B6 application signals 261..273 also
rules out the most obvious hidden "DRCC enabled" companion-bit theory. Signal261 is
Target Lateral ID and signal262 the target angle. Signal265 suppresses one additive
controller term when set; signal268 is the application modulo-64 sequence; signals
269/270 scale two contributions by `/100`. Signals264/267/271/272 have no recovered
downstream direct reader after the broad snapshot, while signal266 is staged but is not
propagated into that broad snapshot at all. Of the remaining live companions,
**signal263 B6[7]** feeds `CB664/C7B4`, a state subsequently used by `CB73A` only with
Target Lateral ID **49=Self-Propelled Transport**; **signal273 B10[2:0]** is conditionally
republished by `CFDA0` into a separate valid-gated status/mode machine consumed by
`CFDD4/CFE64`. Neither is an input to `CEFFC`. Under the recovered direct-reference
surface, no generic B6 secondary "command enabled / DRCC enabled" bit exists.
Computed aliases/DMA outside the recovered direct-reference model remain a normal proof
boundary, but they cannot change the explicit `CEFFC` input set.

Finally, the broad B6 road census needed one provenance correction before it could be
used. Archive route `27` contains **106,800** `src=2` B6 records, but every one has an
exact same-event, same-payload Panda `src=128` TX echo: `60,722` ID0 and `46,078` ID11.
The ordered payload sequences are byte-for-byte identical and timestamps are equal on
106,800/106,800 pairs. Those are our own pre-repin relay-side copies, not stock B6.
After this deduplication the full selected road corpus contains **zero unmatched
src0/1/2 native-B6 candidates**, despite 1.65M+ `sendcan` B6 attempts in historical
bring-up runs. This extends the earlier zero-native-B6 result without conflating our
sender with factory traffic.

The resulting architectural model is therefore sharper than "find the LTA command":
Toyota's FRC hosts a **general lateral feature/request family** whose road-observed
current owners include LDA, LTA/LCA and SDG/PDA-SA. Those feature applications can be
enabled simultaneously; the FRC application state machine chooses the current owner and
publishes that feature-selected, pre-VMM-arbitration generic request on `0x08A`. Exact F33 exposes
corresponding profiles inside one protected external B6 controller and does not
independently revalidate DRCC/LTA engagement when choosing that profile. Factory steering
still does not prove the exact `0x08A -> B6` transform: exact F33 receives neither
`0x08A` nor `0x081`, and the retained stock family operates with no unmatched native B6.
The unresolved factory step is therefore **downstream** of FRC feature selection: Brake/VMM
verification/request arbitration, `0x081` arbitration-result production, post-arbitration
request generation, plus the final steering-assembly authority handoff between the protected
`0x08A/0x081` family and the physical actuator path.

Deterministic reduction and verification:
`tools/targets/camry/analysis/analyze_camry_2026_lateral_family_census.py`,
`data/generated/camry_2026_lateral_family_census.json`, and
`tests/verify_camry_2026_lateral_family_census.py`.

### 4.10 Internal steering-state profile: stock F33 XCP DAQ is disabled

The 52-byte internal steering-state profile recovered for native XCP DAQ remains
useful, but **the installed exact-F33 application cannot execute XCP commands from
its stock CAN ingress**. Sep-6 closure corrected the endpoint to classic extended
CAN `0x1FDC0002 -> 0x1FE00002`; a non-command marker live-updated `FEBE4C34`,
proving physical CAN, rule46, FIFO1, owner routing, `0x8312E`, and `0x830D0` staging.
All runtime transport predicates were also active (`FEBE4EE6=0x5A`).

The remaining silence is fixed in CodeFlash, not runtime state: `0x821D6` invokes
`0x830C0 -> 0x98E80` before CONNECT/opcode parsing, and exact byte
`0x30D68=0x5A` makes that hook return nonzero. `0x821D6` processes protocol
commands only when the hook returns zero. Thus CONNECT, WRITE_DAQ, START, and the
other configured XCP commands are stock-disabled even though the DAQ machinery
itself is present. The capture tool now refuses `--execute`; do not patch this
gate merely to preserve a preferred observer architecture.

For the next live internal observation, use the audited RAM-resident observer with
the same recovered profile. It sends no steering command and gives the required
same-event internal terms without pretending the disabled XCP surface is stock-live.

`tools/targets/camry/live/camry_f33_steering_state_capture.py` defines two 28-byte single-list subsets plus
a default **52-byte `full-path`** union using lists 0 and 1. The first subset is the
decisive stock-source discriminator:

| profile `source-terms` | bytes | exact role |
|---|---:|---|
| `AC2B`, `C7BF` | 2 | `D0218` diagnostic/B6-active branch gates |
| `C43C` | 2 | additive short term |
| `C4C0` | 4 | additive 32-bit term |
| `C3BA` | 2 | additive short term |
| `CC2C` | 4 | additive 32-bit term |
| `BF3C` | 4 | additive 32-bit term |
| `CB38`, `C5EE` | 4 | bounded paired contribution |
| `CBE8` | 2 | final short contribution |
| `CC48` | 4 | complete `D0218` summed output |

This is the exact ordinary B6-inactive sum recovered from `FUN_000D0218`; no candidate
term is omitted. A stock ID11/ID18 capture synchronized with native `0x08A/0x081/0x030`
therefore answers whether one of the previously unnamed EPS-internal terms changes with
Toyota lateral authority, or whether `CC48` changes without a corresponding recovered
term transition.

The second profile follows the numeric result through the physical command funnel:

| profile `command-funnel` | bytes | exact role |
|---|---:|---|
| `CC48` | 4 | `D0218` output |
| `CC4C`, `CC4E` | 4 | `D0284` bounded/scaled value, then `D02DA` slew result |
| `AC52`, `CC60` | 4 | `D0382` limit and limited value |
| `CC50` | 2 | `D039E` pre-scale command |
| `AC5A`, `AC4C` | 4 | `D042C` scale and symmetric slew/limit inputs |
| `CC62`, `CC66`, `CC64` | 6 | pre-slew, post-slew/gate, and selected command |
| `AC54`, `AC56` | 4 | motor-driving `CC64` mirror and diagnostic `CC62` sibling |

`FUN_000D0AF6` calls these stages in order: `D0218 -> D0284 -> D02DA -> D0382 ->
D039E -> D042C -> D06D6 -> D047C -> D0AAE`. The default `full-path` profile is the
unique union of the two tables: **52 bytes**, with `CC48` sampled once, emitted as eight
ODTs across lists 0 and 1 during the same event-worker invocation. ODT reads are still
sequential rather than an atomic CPU snapshot; the tool records the assembly span and
drops incomplete/out-of-order events. It simultaneously records native
`0x025/0x030/0x081/0x08A/0x0B6/0x0FE/0x371/0x412` Panda receive traffic with host
monotonic batch timestamps. Older Panda Python bindings also expose raw `busTime`,
which the observer retains as an opaque wrapping hardware timer when present. The
current Comma/Panda binding returns `(address, data, bus)` and therefore exposes no
`busTime`; the observer records null/empty timing evidence rather than dropping those
frames. Host timestamps remain correlation aids rather than physical CAN ordering.

The recovered profile geometry remains deterministic: a full sample would be eight
classic-CAN DTOs if XCP command dispatch were enabled. On stock exact F33, however,
`tools/targets/camry/live/camry_f33_steering_state_capture.py --execute` is deliberately fail-closed because
CodeFlash `0x30D68=0x5A` blocks CONNECT/DAQ before any list can start. The tool remains
useful in plan mode:

```bash
$PY runtime/tools/targets/camry/live/camry_f33_steering_state_capture.py --profile full-path
```

For live collection, use the packaged **stripped RAM-only observer derived from the B6
transaction-resident framework** with the same target-cell profile. That is now the
intentional observation path, not a fallback after another XCP attempt. It adds no new
persistent flash patch; installation/heartbeat semantics remain the already-audited
RAM-only path.

Verification: `tests/verify_camry_f33_steering_state_capture.py`; the in-car packaging
path is `tools/targets/camry/builders/build_camry_f33_car_kit.py`.

### 4.11 Stock ACC delayed hold is request-ID/allocation state (VAR-140 supersession)

The September road corpus originally exposed the delayed stop/hold condition as
raw `0x08A B7={0x66,0x67}`. The unified request-layout recovery now explains that
byte rather than treating it as an opaque ACC state. `B6` and `B7` each pack a
six-bit longitudinal request ID in bits7:2 plus a two-bit braking/driving-force
allocation method in bits1:0. A full-frame re-read adds a cleaner structural
state bit: `0x08A B4[5]` is asserted on **198/198** retained delayed-hold frames
and clear on every other native `0x08A` frame in complete routes `3b/3c`.

The retained states decompose as follows:

| Raw B6/B7 | Request A | Request B | Dynamic state |
|---|---|---|---|
| `0x2D / 0x47` | ID11 / Engine+Brake1 | ID17 / Brake Only | ordinary active cruise |
| `0x2C / 0x46` | ID11 / Engine Only | ID17 / Engine+Brake2 | active accelerator override |
| `0x2D / 0x67` | ID11 / Engine+Brake1 | ID25 / Brake Only | delayed zero-speed hold |
| `0x2C / 0x66` | ID11 / Engine Only | ID25 / Engine+Brake2 | delayed hold with accelerator override |
| `0x47 / 0x65` | ID17 / Brake Only | ID25 / Engine+Brake1 | moving counterexample |

Routes `3b` and `3c` contain three independent delayed-hold episodes totaling
**198** native request frames: 192 `0x2D/0x67` plus six `0x2C/0x66`. Every hold
frame is effectively 0 m/s, enters only after the vehicle has already remained
stopped for more than five seconds, and all three episodes clear with accelerator
input before vehicle motion. No RES-button clear join is established. The moving
`B7=0x65` witness rejects both the old B7-bit5 rule and request-B ID25 alone as a
standstill predicate.

Fork opendbc therefore reports Camry stock-ACC standstill from the cruise latch
plus source-real structural `B4[5]`. Request-B ID25/allocation2-or-3 remains the
independent decoded-state corroboration, and the moving ID25/allocation1 witness
keeps that ID from being promoted to a standstill flag by itself. Corolla, where
B4[5] hold behavior is not independently retained, uses the decoded ID25 plus
allocation2/3 contract. No resume command is synthesized.

Evidence: `data/generated/camry_20260906_hands_off_warning_audit.json`,
`data/generated/camry_2026_longitudinal_request_plane.json`,
`tests/verify_camry_2026_longitudinal_request_plane.py`, and fork
`opendbc/car/toyota/tests/test_tss3_{camry,corolla}.py`.

### 4.12 Source-real parser liveness across the long routes (VAR-141)

The Camry parser liveness settings are now checked against the retained road corpus rather
than only against synthetic scheduling. Routes `3d`, `3e`, and `3f` contribute **62 + 78 +
84 rlog segments**. For every one of the **18** messages checked by the exact-Camry TSS3
parsers, the reducer uses only the established native Panda source side and resets its gap
clock at each rlog boundary. Every configured parser rate is a conservative nominal floor,
and every worst observed same-segment gap remains inside CANParser's normal ten-period alive
timeout.

The audit also catches one prior test/configuration overclaim: `0x127 GEAR_PACKET_HYBRID`
was labeled 60 Hz, but its median rate is consistently about **51 Hz** (lowest of the three
routes **50.970 Hz**). The fork now configures it at **50 Hz** and the integration test uses
the same conservative source-real floor. Other useful bounds include native bus-2 `0x08A`
at at least **43.741 Hz median** against a 40-Hz parser setting, `0x0FE` at at least **33.111
Hz** against 30 Hz, and variable `0x610` with a worst observed **1006.457-ms** gap against
a 3333.333-ms timeout. `0x412` remains the ~1-Hz/event-driven HUD surface from VAR-138;
its worst same-segment gap across these routes is **1758.564 ms**, far inside the 10-s
parser timeout.

The fork's liveness regression now removes **every** parser-checked source in turn and verifies
CAN invalidation followed by recovery; the helper is explicitly described as synthetic
scheduling at measured native cadence, not as an original-capture replay. This separates the
software timeout test from the dynamic evidence that supplies its rates.

Evidence: `tools/targets/camry/analysis/analyze_camry_2026_parser_liveness.py`,
`data/generated/camry_2026_parser_liveness.json`,
`tests/verify_camry_2026_parser_liveness.py`, and fork
`opendbc/car/toyota/tests/test_tss3_camry.py`.

## 5. Demonstrated B6 steering authority and remaining qualification

**2026-09-10 supersession:** the exact development path has established steering
authority. The working resident consumes a fresh C7 target, modifies and signs one
already-admitted native B6, and the route shows the corresponding lagged wheel-angle
response while Toyota LTA is off. See the dedicated
[bounty evidence report](toyota-tss3-openpilot-bounty-evidence.md). The older
direct-host-B6 localization plan below is retained to explain why that sender failed
and why the working adapter uses an internal native B6; it is no longer the current
control-status conclusion.

**Qualification boundary:** the modified-firmware observer/bridge work below is
historical/development RE used to localize receiver behavior. It is **not** the
upstream interface. Its successful road result proves the exact development path,
while general support still requires isolating the signer behind an exact platform
capability and preserving the normal `controlsd`/`CarInterface`/`CarState`/
`CarController`/Panda ownership boundaries.

The 2026-09-04 road logs show why further limit tuning is not the next step. The shortest
bounded execution path is independent of Toyota's unresolved stock FRC pipeline:

1. **Return B6 diagnosis to the stationary boundary.** The road corpus already proves that
   openpilot can request large angles without getting the expected wheel motion; another road
   drive cannot localize the receiver failure and adds no useful discriminator.
2. **Observe B6 ingress without bypass.** Install/heartbeat-attest observer v2 in NRTD,
   transition directly NRTD→READY without OFF, and run the stationary exact-signature probe.
   `D7 delta=0` invalidates the window.
3. **Separate transport from EPS acceptance when B6 remains zero.** With D7 advancing, use an
   independent physical bus receiver; Panda TX returns and REC/TEC endpoints alone do not
   prove wire acknowledgement.
4. **Bridge only after exact queue ingress.** Install the deduplicating route44 resident and
   repeat ID0/current-angle phases. Do not request a nonzero offset before the host classifier
   reports `ADMITTED`.
5. **Validate the B6 application candidate stationary.** With the wheels unloaded, test ID0
   inactive, ID11 zero angle, then one small bounded nonzero step. Establish sign, scale,
   application companions, motor response, and absence of an EPS fault latch.
6. **Driver-state mapping is now dynamically closed for the normal openpilot contract.**
   VAR-139 validates left-positive/right-negative torque on 45/45 post-fix lane-change
   starts and selects the stateless 0.6 N.m threshold against Toyota's native driver-
   steering detector. The richer `0x351/0x394` permanent/recoverable fault policy remains
   separate. `STEERING_FAULT_INHIBIT_STATUS` stays decoded as a raw selected fault/inhibit
   aggregate but is not promoted to temporary/permanent policy without asserted/recovery evidence.
7. **Only after receiver acceptance, validate the remaining safety transitions and tune.**
   Prove slew/rate limits, inactive release, inhibit, fault, recovery, and driver override
   before another on-road B6 test. VAR-148/CORR-179 already close the exact ID11 composition
   semantics: accepted B6 is co-modulated in the ordinary EPS sum, not made exclusive.

OQ-054 remains valuable for an elegant stock-compatible architecture. Synchronized FRC
Operation FFD should now target the **FRC-internal selector** directly: feature-local
`550D/5531`, `560D/5631`, `568x`, `5Axx/5D8D` state against generic `5282`, while
`5285/57DE/5265` and raw `0x081` provide the downstream Brake result. Exact FRC
firmware/HSM evidence must identify both the feature-owner state machine that populates
`5282` and the key/freshness/CMAC implementation that publishes protected `0x08A`.
Native Bus 1 has 22 frequent periodic camera/radar streams; `0x180..0x182` carry
recovered perception-object slots, but those are a separate FRC interface. The protected
`0x08A` request itself is already native at the FRC-side Bus-4 endpoint and is **post
feature-selection**. The downstream unknown is Brake/VMM verification/request arbitration/result/request
generation and B6 routing, not LTA-vs-LDA-vs-PDA selection. That attribution does **not**
block the independent B6 development probe above.
- `data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json`
- `data/generated/camry_8965F3307000_tss3_opendbc_port.json`
- `data/generated/camry_8965F3307000_external_lateral_ingress.json`
- `data/generated/camry_2026_motor_feedback_correlation.json`
- `data/generated/camry_2026_lta_state_reconciliation.json`
- `data/generated/camry_2026_08a_producer_bounds.json`
- `data/generated/camry_20260904_stock_steering_report.json` and
  `data/generated/camry_20260904_stock_steering_manifest.json`
  (from `tools/targets/camry/analysis/analyze_camry_20260904_stock_steering.py`; external
  `/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/` inputs)
- `tests/verify_camry_20260904_stock_steering.py`
- `tests/verify_camry_8965F3307000.py`
- `tests/verify_camry_2026_lta_state_reconciliation.py`
- `tests/verify_camry_2026_08a_producer_bounds.py`
- `tools/targets/camry/utilities/decode_camry_tss3_operation_ffd.py`
- `tests/verify_camry_tss3_operation_ffd_decoder.py`

## 7. Native longitudinal integration consequence of the Bus-1 E2E candidate

> **September-16 supersession:** the historical `0x160` demand interpretation
> below is no longer the current Camry contract. Retained F33 motion and
> replacement evidence classify its implemented B4:B5/B12 mapping as
> state/result-related rather than a demonstrated actuator ingress. The leading
> direct chassis-facing candidate is now protected Bus-4 `0x08A` B8:B9/B11:B12,
> whose signed16 ×0.001 shape matches Toyota's upper/lower TSS acceleration
> request vocabulary. Brake-owned `0x081` now supplies the matching result plane:
> B6[5:0] is the strongest selected-longitudinal-ID candidate and B20:B21 the
> strongest selected-acceleration candidate, superseding the older `0x0CA` result
> interpretation. Exact upper/lower request-word order and additional request
> metadata are partly closed: B6/B7 strongly fit the two packed request-ID/allocation
> bytes, but their upper/lower A/B ordering and shift/EPB/override/priority fields
> remain unresolved. The semantic request plane itself is `0x08A`;
> what remains unresolved is the clean physical source/suppression boundary. Camry therefore keeps
> stock longitudinal ownership and does **not** advertise Alpha Long. See
> `camry-2026-longitudinal-evidence.md` for the current evidence and topology
> normalization. The remainder of this section is retained as historical design
> context for why a proved upstream request carrier would fit native openpilot.

A 2026-09-05 comparison against current upstream openpilot
`a4f7c50d2a52a5865a40da2ebc5004c82929a0ef` and opendbc
`3e92d112129507debe45364891954db70238997a` clarifies what a proved Camry
Bus-1 request carrier would buy. The fork's core longitudinal stack is unchanged
from that upstream openpilot revision: `LongitudinalPlanner` chooses an acceleration
trajectory from cruise/model-lead constraints, `controlsd` runs `LongControl` and
publishes the resulting physical acceleration request as `CC.actuators.accel`, and
the brand `CarController` converts that generic actuator request into the vehicle's
native wire command. Toyota's existing upstream native-longitudinal implementation
does exactly that on older architectures: it enables
`CarParams.openpilotLongitudinalControl`, retains `pcmCruise=True`, and every third
controller frame maps `actuators.accel` through Toyota-specific compensation into
`ACC_CONTROL` (`0x343`) or, on the classic SecOC profile, authenticated
`ACC_CONTROL_2` (`0x183`). Stock cruise buttons/set-speed remain the engagement and
speed-selection UI; openpilot does not need to synthesize the RES/SET switch PDU in
order to own acceleration.

The September-16 request-plane recovery supersedes the old proposal to promote
`0x160 B12` into a native-long command. `0x08A` is the shared TSS3 application
request PDU: its packed request-ID/allocation fields and signed16 acceleration pair
sit in the same message as the lateral request tuple, while Brake-owned `0x081`
provides the corresponding result/reference family. `0x160` remains useful as an
FRC-origin Profile-5 state/evidence PDU, but its historical B4:B5/B12 correlations
and successful host modification do not establish authoritative command ingress.

The current fork remains intentionally stock-longitudinal. TSS3 returns
`openpilotLongitudinalControl=False`, `alphaLongitudinalAvailable=False`, and sets Toyota
`STOCK_LONGITUDINAL` on both Camry and Corolla. The F33 relay-correct path now does own the
complete `0x08A` carrier on behalf of the FRC, but every longitudinal field is copied
byte-for-byte from the matched native source generation; `CarController` emits no host
longitudinal request and `0x160` remains non-actuating evidence/state traffic. The offline
`camry_frc_request_poc.py` remains only a deterministic reproducer for the old `0x160`
field hypothesis and its exact Profile-5 transform.

Thus clean `0x08A` source ownership is no longer the native-long blocker on the repinned
F33 path. What remains is the longitudinal semantic/safety qualification: exact upper/lower
request mapping, Brake/VMC selection and feedback, PCS/AEB priority, driver override,
standstill/hold behavior, and the `0x081` result plane. Only after those are closed should
normal openpilot longitudinal output be connected to the two TSS3 acceleration requests.
