# 2026 Camry port: adversarial evidence review

This September 15 review audits the preceding integration checkpoint, rather
than accepting the earlier “essentially complete” summary as evidence. All
work is offline; no vehicle commands or persistent firmware writes are run.

## Confirmed corrections

### Tire stiffness is a baseline times a learned multiplier

`VehicleModel.update_params()` multiplies `CP.tireStiffnessFront/Rear` by
`vehicleParameters.stiffnessFactor`. `paramsd.VehicleParamsLearner` likewise
initializes its model globals from those same CP stiffnesses. A learned value
near 1.0 therefore supports preserving the configured baseline; it does not
justify replacing `CP.tireStiffnessFactor=0.7933` with 1.0. The PlotJuggler
label used in the previous pass is not authoritative over executable code.

The erroneous 1.0 override has been removed. The 15.3 steering-ratio default
is a separate absolute learned quantity and is not reverted with stiffness.
The 0.18 s actuator delay is left unchanged, but identical cached lagd values
on consecutive routes must not be described as independent fresh estimates.

### Radar integration requires more than plausible field distributions

The initial radar parser inherited Panda bus 1 from pre-repin Toyota code,
whereas this branch uses stock Toyota-B: ADAS/camera on the 0/2 relay and
EPS/Brake on unsplit bus 1. Its synthetic test fed the same wrong bus and did
not exercise that topology mismatch.

The first joined-object analyzer also indexed by segment and a repeating
B2:B3 value, overwriting earlier bursts after wrap. A streaming, time-bounded
join is required. Full-corpus reconstruction still supports the recovered
relative-speed field, but cycle identity, validity, track lifetime, lateral
sign/scale, and vision correspondence are being independently reviewed before
calling the RadarPoint path qualified.

### Continuous signer loses host-command liveness

The archived continuous helper replaces every distinct native B6 while the
last C7 sequence is nonzero. Its branch-to-NOP change removes one-shot
consumption without introducing command expiry. Native B6 arrivals can
therefore keep a stale host target active after host updates cease. The
historical steering witness does not establish host-loss behavior. This is an
adapter lifecycle defect, not a reason to add another engagement policy to
CarController or Panda.

## Completed independent radar-unit review

`data/generated/camry_2026_radar_anchors.json` and its raw-object-byte fixture
retain 17 original rlog identities and independent vision/gyro observations.
They supersede the prior direct FFD-to-CAN scale transfer:

| Quantity | Corrected observed wire interpretation | Independent anchor |
|---|---|---|
| Range | unsigned B0:B1 × 0.005 m | 1,953 vision-associated observations: r=0.998518, slope=1.029071, median absolute error 0.799 m |
| Lateral | signed12 B2:B3[7:4] × 0.04 m, left-positive | 240 off-center vision observations: slope=0.982563; 27,602 continuity-qualified gyro pairs: r=0.843106 and inferred LSB=0.038909 m/count |
| Relative speed | signed low14 B1:B2 × 0.025 m/s; B1[7:6] excluded | vision-speed slope=0.992347; signed12 wraps 113 retained high-closing-speed observations |

The previous range/range-rate correlation could not determine their common
scale: both were doubled. Signed13 and signed14 velocity interpretations agree
on the retained data; the wider field boundary is not independently resolved.
Object validity/confidence and silent same-slot reassignment are also not
resolved. The corrected parser remains available for offline/replay inspection;
normal CarParams retains the model-only radar-unavailable path until object
validity/lifecycle is established.

The corrected full August reconstruction consumes each time-bounded occurrence
rather than overwriting repeated counter values: 30,532 / 35,994 complete
four-record bank bursts. Its kinematic agreement is corroboration, not a
substitute for the independent unit anchors above.

## Completed diagnostic recovery review

FRC_P5 monitor 199 defines control modes 1/2/4 as distance control and mode 3
as conventional constant-speed cruise. Recovery now requires a distance-control
mode as well as the permission flag and a clear ACC-not-available flag. Truncated
DID1903/1905/1906 values are errors, never implicit false/no-fault booleans.
ISO-TP response-pending no longer terminates a transaction, malformed single
frames are rejected, and sequence errors cannot produce partial success.

The pre-clear snapshot is written atomically **before** the first clearing
request. A later timeout preserves that snapshot, completed clear responses,
and the failure instead of discarding the diagnostic evidence. Six offline
regression tests cover these cases, including an injected mid-clear failure
and final Panda ownership cleanup. Same-cycle physical DRCC restoration is
still a vehicle observation, not established by these tests.

## Completed host-loss correction

The v17 Camry kit selects a new **598-byte supervised helper**, padded to the
same 600-byte loader transfer. The 524-byte resident, staging image, and
boot-authenticated payload are byte-identical to the preceding runtime; no
CodeFlash patch or new memory region was introduced. The helper consumes a
changed host generation as a seven-foreground-tick lease, polls it even when
no native B6 is queued, never renews an unchanged generation, and leaves native
B6 untouched on expiry or sequence zero. At the nominal 5-ms foreground period,
this is 35 ms of host-command receive-loss supervision, not a new engagement
policy in openpilot.

`VerifyCamrySignerHostLiveness.java` executes the actual linked instructions in
Ghidra emulator-local memory. All 34 liveness assertions pass, including held-command
expiry, empty-queue aging, sequence wrap, zero release, normal 50-Hz updates,
and no resurrection across 520 further scheduler invocations. The archived
continuous helper fails the same expiry assertion. The emulator intercepts
NOP's custom pcode operation with its architectural no-op behavior and stops
before the first stock memory-copy/crypto call: this is a host-admission/liveness
test, not silicon command-5, full ECU scheduling, or vehicle validation.

The replacement method now rejects `replace-once` before sending a C7
substitution when a continuous/supervised helper is selected. Those helpers can legitimately
replace multiple native frames during one host generation; labeling that as a
one-frame experiment was incorrect. Historical binaries remain unchanged.

## Completed integration and safety corrections

The stock-harness source census places `0x412` and `0x101` on unsplit Panda bus
1, `0x160` on camera-side bus 2, and perception `0x180..0x185` on bus 0. The
previous controller's HUD-to-bus0 and brake-cancel-to-bus2 packets therefore did
not replace the native sources. They and their Panda permissions are removed;
CarState reads the HUD from its real PT-side parser. Automatic cancellation and
any stock-HUD replacement remain unresolved rather than merely “waiting for a
visual test.” See `camry_2026_stock_harness_topology.json` and the source-hashed
`camry_20260915_port_evidence_audit.json` for the independent retained census.

The actual successful steering segments report conventional cruise (`0x251`
B0 `0x88/0x90`), not adaptive operation. Camry now reports that through ordinary
`cruiseState.nonAdaptive`; unmodified openpilot `car_events.py` maps it to
`wrongCruiseMode`. This intentionally prevents treating the historical
conventional-cruise steering demonstration as a completed stock-DRCC port.
No synthetic engagement flag or new controller veto was added.

The generic angle-rate checker did not enforce an active absolute angle cap.
TSS3 now explicitly rejects targets outside ±1745 raw in addition to its usual
rate checks; the regression approaches the boundary in legal increments, so it
cannot pass merely because a large jump was rejected. CarController keeps its
sequence across inactive periods while emitting wire sequence zero, so a
subsequent engagement does not reuse a previously consumed generation.

Planner acceleration bounds now agree with the Camry actuator envelope
(−1.5..+1.3 m/s²). Both Python parsing and Panda verify native E2E Profile 5
CRC, using init FFFF and Data ID equal to the CAN address; this is wire-equivalent
to the old init-zero/Data-ID-444A expression for the fixed 32-byte `0x160` only.
The encoder preserves the unassigned high bit of B12.

Across the complete two August captures, **127/20,510 and 1,373/23,998** native
`0x160` frames exceed one or both host acceleration-field bounds. When the
controller intentionally hands back the native low-speed frame, rejecting that
copy while suppressing the original is a transport defect. Panda now recognizes
only a byte-exact copy of the latest valid camera frame for native passthrough;
modified requests retain the ordinary host limits and CRC requirements.
This does not establish unknown AEB priority or the causal Camry command scale.

## Final validation and scope

Openpilot `3f9f3c061` pins opendbc `093125ab`. The combined named suites passed
615 tests / 11,049 subtests, with 404 existing skips. Both debug and non-debug
H7 application ELF cross-builds pass `-Werror`. No build was deployed. The
17 original radar rlogs were independently re-extracted and reproduced the
committed raw-object fixture exactly.

The healthy-EPS original segment has 5,477/5,477 valid post-startup parser
samples after an explicit test-only topology translation; the stock-harness
recording correctly remains invalid in 5,476/5,476 samples solely because EPS
`0x030` is absent. Two compact, source-hashed opendbc fixtures retain the original
frame cadence, buses, and bytes and regression-test both outcomes.

These results substantially improve the implementation, but supersede rather
than confirm the earlier “offline/software essentially complete” assessment.
The [current capability matrix](camry-2026-capability-matrix.md) records the
remaining specific integration/semantic boundaries. No vehicle commands,
persistent firmware changes, or on-road tests were performed in this audit.

The compiled-helper suite also runs **52 golden differential/error cases**
against the archived continuous binary: all 16 received/committed low-counter
combinations at three target angles, three command-5 failure modes, and an epoch
mismatch. It compares the actual helper's domain, call-boundary inputs,
freshness witness, and final queue image. Encoder/crypto callees are supplied
identical deterministic stubs, not mistaken for a silicon CMAC oracle. All 86
compiled-instruction assertions pass; the intended change is command expiry,
not a changed signing construction or native-frame mutation tuple.

## Stock topology and ordinary controller/safety corrections

The four-original-rlog topology reducer pins radar bus0 / camera 0x160 bus2 /
chassis 0x025,0x101,0x412 bus1. It deliberately records the lack of EPS 0x030 in
these incident-era captures. The earlier wrong-bus HUD and fake-brake cancel
transmitters are removed rather than presented as a successful source
replacement. A genuine automatic-cancel ingress remains unresolved on stock
Toyota-B; reading a state mirror does not make it a command.

The seven-segment consolidated reducer additionally pins configured CP
stiffness 0.7933, learned multipliers near 1.0, repeated cached lag estimates,
and conventional cruise in the selected working steering samples. It also
finds 127/20,510 and 1,373/23,998 native August 0x160 frames outside the narrower
host-command envelope, all CRC-valid. Byte-exact native handback therefore
must not be clipped or rejected as though it were a modified host command.

The maintained opendbc changes align planner/controller/Panda bounds at
Camry −1.5..+1.3 m/s², preserve B12 bit7 while changing only the recovered low 7
request bits, validate Profile-5 RX/TX, allow only the byte-exact latest valid
native handback outside those bounds, enforce actual ±1745-raw C7 angle limits
in addition to rate limits, and preserve the host sequence across inactive
periods. Read-only conventional cruise is exposed through the normal
`cruiseState.nonAdaptive` field. No second engagement policy was added.

## Verification and committed integration

Current openpilot `3f9f3c061` pins opendbc `093125ab`. This combined command passes
**598 tests / 3,172 subtests**, with 262 existing selection skips:

```sh
cd /Users/kai/dev/inspect/repos/kai-openpilot/opendbc_repo
uv run pytest -q opendbc/car/toyota/tests opendbc/can/tests \
  opendbc/safety/tests/test_toyota.py \
  opendbc/car/tests/test_car_interfaces.py opendbc/car/tests/test_docs.py \
  opendbc/car/tests/test_platform_configs.py opendbc/car/tests/test_vehicle_model.py
uv run ruff check opendbc/car/toyota opendbc/can/dbc.py
```

Analysis verification is explicit and offline:

```sh
cd /Users/kai/dev/inspect/repos/ghidra_rh850_analysis
tools/test camry_f33_signer_host_liveness camry_f33_b6_stationary_probe \
  camry_f33_post_install_recovery camry_2026_radar_anchors \
  camry_2026_bus1_camera_output camry_2026_stock_harness_topology \
  camry_20260915_port_evidence_audit --jobs 2
```

The remaining adaptive-cruise/supervised-signer combination, genuine cancel
mechanism, fault classification, radar validity/lifecycle, and physical
longitudinal/AEB/hold behavior are not declared solved by these offline tests.
The corrected current capability matrix distinguishes each boundary.

The final analysis-side run passed all eight selected verification scripts,
including 86 compiled-helper liveness/differential/error assertions. The
differential cases substitute deterministic callback results to compare the
new helper with the archived one; they do not emulate or validate ICU-S silicon.
The standalone `build/out/camry-f33-car-kit-v17-audit` bundle passes `doctor`
and offline `plan`, with the supervised helper SHA pinned in its manifest.

Final targeted analysis result: **8 verification scripts passed, zero failures,
zero skips**. This includes byte-identical regeneration from the original
stock-topology and consolidated rlogs, all 121,941 selected radar source frames
passing Profile-5 CRC, the v17 kit build, and the compiled-helper positive plus
historical-negative regressions. No hardware execution was performed.

## September 15 follow-up: source lifecycle and live steering-fault projection

The subsequent offline pass resolves two previously unimplemented surfaces.
No vehicle command, EPS patch, signer change, or Panda-policy change is involved.

### Source-driven object lifecycle

The ordinary motion PDU for each bank (`0x183..0x185`) has eight seven-byte
records. In each record, byte4 bit7 starts a new track; byte5 bit4 ends the
**previous** track. Both flags occur together on occupied-to-occupied slot
replacement. Treating that combination as an empty slot is wrong, as is
preserving the old `trackId` because the distance never became the empty sentinel.

Both complete August captures establish the fields; a separate fixture from
17 September rlog segments verifies them without refitting. Across 1,020,048
object records, every one of 7,635 observed births has the start flag, every
one of 7,647 observed deletions has the end flag, and 32,043 occupied records
carry both flags. The raw low-two-bit state in motion byte5 is zero in every
empty record; 121 nonempty records also carry zero and must not be accepted
merely because the geometry bytes remain populated. The parser filters state
zero and sentinel/zero ranges. Nonzero states 1/2/3 remain structurally named;
no unsupported confidence percentage or sensor-source enum is assigned.

The decoder now consumes **every** source cycle in a host publication, so an
intermediate deletion/new-track flag is not lost by reading only the last CAN
parser value. Both cycle bytes increment independently modulo256, not as a
16-bit counter. Missing cycles retire identity because they may hide a one-frame
lifecycle event. Duplicates, mixed-cycle geometry/motion, bad CRC, truncation and
wrong buses cannot manufacture an update; ordinary CAN timeout clears stale
tracks and publishes a CAN error rather than waiting forever for a missing
trigger PDU. End-old/start-new ordering is explicit.

The actual opendbc parser replays all 60,969 held-out bank pairs as **20,323
complete updates**, **308,111 qualified point observations**, **17,868 observed
identity replacements**, and **zero reported CAN errors**. This is a source
replay result, not a new on-vehicle fusion/control qualification. Together with
the already independent distance, speed and lateral-sign anchors, the supported
Camry decoder is now selected by normal `CarParams` (`radarUnavailable=False`).
Corolla has no radar DBC assignment and remains model-only; no cross-variant
transfer is assumed. The exact signed13-versus-signed14 velocity boundary and
optional object-class/confidence labels remain bounded as before.

Reproducible source reduction:
`tools/targets/camry/analysis/analyze_camry_2026_radar_lifecycle.py`,
`data/generated/camry_2026_radar_lifecycle.json`, and
`tests/fixtures/camry_2026_radar_lifecycle_holdout.jsonl.gz`.
The extractor verifies original rlog hashes and P05 integrity before writing
its deterministic fixture. `tests/verify_camry_2026_radar_lifecycle.py` checks
both discovery captures and the independent holdout.

### Current fault versus a restart-required failure

Fresh exact-F33 decompilation/disassembly closes `0x4C000` as the producer of
`FEBE80DE`; `0x4C97A` publishes it through `FEBE8C35` as `0x030 B6[2]`. It is
an OR of three **active** class counters (`82BA/82C2/82C4`, classes02/10/20)
and three current status comparisons (`E857/E858/E859 == 0x22`). The event
assertion path `51C66 -> 50FC8` increments a newly active class; recovery
`51D5E -> 514BC` decrements it without underflow. Historical class latches at
`82A3/82A4/82A5` are separate and do not assert this bit after active counts clear.

`VerifyCamryFaultProjection.java` executes the **stock instructions**, after
checking the working Ghidra image byte-for-byte against the verified CodeFlash.
Its 85 assertions cover all 64 source combinations, each class assertion and
recovery, exclusion of history-only state, multiple active faults, and
non-underflow after final recovery. Only interrupt save/restore callees are
substituted; there is no concurrent actor in this emulator-local test.

Camry `CarState.steerFaultTemporary` now reports this current fault/inhibit
aggregate through the ordinary upstream interface. "Temporary" is current
steering-unavailability semantics, **not** a prediction that a physical defect
will repair itself. `steerFaultPermanent` is not fabricated from the same
one-bit aggregate: neither exact cause nor restart-required status can be
reconstructed from it. Other unrepresented classes remain outside this selected
fault projection. H/F and Crown are not assigned the F33 policy by analogy.

Reproducible proof:
`tools/targets/camry/analysis/analyze_camry_f33_live_fault_projection.py`,
`data/generated/camry_f33_live_fault_projection.json`, and
`tests/verify_camry_f33_live_fault_projection.py`.

### Validation

The combined Toyota, CAN, Toyota safety, generic interface, documentation,
platform and vehicle-model selection passes **615 tests and 3,183 subtests**,
with 262 pre-existing skips in that selection. Toyota lint passes. New radar
adversarial coverage includes batching, deletion/replacement, unqualified
retained geometry, duplicate/wrapped/skipped cycles, CRC, truncation, timeout,
startup spread across publications, and wrong-bus traffic. Exact-F33 CarState
fault assertion/recovery and unrelated status-bit separation are covered too.
Automatic cruise cancellation remains a separate receiver/ownership question;
none of these changes restores the invalid unsplit-bus fake-brake sender.

### Cooperative-control faults: two additional source-real inhibits

Exact F33 also reports `CAFC` at `0x030 B16[0]` and `CAD9` at `0x030 B19[0]`.
These are separate from the selected hardware/DEM aggregate at B6[2]. Fresh
stock-code tracing closes their RTE staging through `D0D7C -> BF3AA -> 4C2DC ->
4C97A`; generated-COM signals 25 and 31 bind them to those wire locations.
`CE772` requires both clear before entering ready, and `CE7A6` leaves ready
when either asserts. Camry CarState now reports all three through ordinary
`steerFaultTemporary`, without changing Panda, the controller, or engagement
policy. The original unit-test telemetry was not healthy: its B19[0] flag is
set. A separately retained operating zero-torque frame replaces that default,
and an explicit regression preserves the original initializing/inhibited case.

The permanent/transient distinction is provably lossy at this projection:
`CEC72` ORs `CAFB==1` and `CAFD==1`. `CEE7C` clears the request-failure source
in inactive profile 7, whereas `CEF26` retains the asserted rate-latch source;
`CEC0C` clears both during subsystem initialization. These two causes publish
the same command-inhibit bit. Assigning a restart-required boolean from that
bit would therefore invent information. This does not rule out a distinct,
as-yet-unrecovered status or diagnostic source.

The additional verifier executes stock OR, RTE, readiness and recovery code;
only scalar packing/status submission is replaced by argument observation.
It checks the actual stock packer arguments and both values, not merely a
Python reconstruction of the RTE chain. **59 assertions pass**, adding to the
85 live hardware-fault assertions. Source, generated evidence and runnable
verifier are `analyze_camry_f33_cooperative_fault_projection.py`,
`data/generated/camry_f33_cooperative_fault_projection.json`, and
`tests/verify_camry_f33_cooperative_fault_projection.py`.

### Cancellation: the remaining command contract is not recovered

The durable reduction now retains **21 switch-CANCEL edges followed by genuine
cruise-latch release**, drawn from all three September 4 highway routes. Every
window has preceding cruise engagement and no overlapping brake assertion.
The observed publication-batch delay to release is 29.756..172.179 ms, with a
70.439 ms median; these timestamps are not physical CAN arbitration timing.
Original source hashes and both sides of each state transition are in
`tests/fixtures/camry_2026_cancel_windows.jsonl.gz`. Its tracked extractor
regenerates the fixture byte-for-byte from the original rlogs, including the
one window spanning a segment boundary.

The expanded fixture preserves **all 22 periodic ADAS ID/DLC streams** in
every event, including all 13 object-family PDUs; all **16,526 ADAS frames**
pass native Profile-5 CRC. The principal comparison uses a pre-window of
−1,000..−25 ms and a post-window of 0..1,000 ms relative to the physical
switch edge. Publication timestamps do not establish CAN arbitration order.

The literal-edge screen tests **17,824 fully covered single-bit/polarity
hypotheses**. No stable-before/asserted-after bit reproduces in every window,
even allowing a brief pulse anywhere in the post-window; the highest coverage
is 10/21. The broader enum screen tests **279,904 contiguous 1..16-bit field
layouts**, both big/MSB-first and little/LSB-first, at every bit start after
B2 across all 22 streams. It permits different or changing pre-cancel values
and requires a common post-only value in every event. **No candidate survives.**
A separate shorter-window screen (−300..−25 ms, 0..250 ms) covers 80,532 short
field layouts over the 20 streams with complete coverage and also yields no
fully reproduced candidate.

These are method-bounded negatives, not proof that an automatic-cancel command
is absent. They do not exclude noncontiguous or context-dependent encodings,
sparse traffic outside the windows, or an automatic command not exercised by
physical-switch cancellation. The search must not turn a post-cancel state
echo into an accepted command merely because its timing is correlated.

The current FRC catalogue has 69 routine Active-Test candidates and no direct
Active-Test table. Its only cancel-named test is **PDA Cancel Notification
Display**, not a cruise cancel actuator. DID 1B01 is grouped with ISA switch
recognition/output monitors; diagnostic bit positions do not establish CAN
positions or writable DRCC commands. No maintenance/test routine, artificial
fault, ECU communication suppression, or replay of a protected switch packet
is substituted for normal cancellation.

Retained comparison-source review does not supply the missing contract:
legacy Toyota implementations send their established `0x343`/PCM cancel
commands, whereas the retained TSS3 Corolla branch returns from its TSS3
controller before that legacy path. Neither constitutes target-native Camry
receiver evidence. The local Camry CUW `T-0051-26` is node 0724 Engine/MG, not
FRC or Brake/Skid; the repository's exact EPS firmware is not the missing
cruise-command receiver image. The next unresolved software fact is an
ordinary, accepted cancellation command and its receiver/transport ownership,
not whether the deleted wrong-bus fake-brake implementation passes a road test.
No automatic-cancel sender is added in this checkpoint.

Source/reducer: `tools/targets/camry/extract/extract_camry_2026_cancel_windows.py`,
`tools/targets/camry/analysis/analyze_camry_2026_cancel_evidence.py`,
`data/generated/camry_2026_cancel_evidence.json` (v2), and
`tests/verify_camry_2026_cancel_evidence.py`. Synthetic positive controls independently
check that both endian search directions recover a one-frame pulse, including
a 16-bit field crossing three bytes, and reject an otherwise identical
non-reproducing event or a pulse supplied only by a CRC-corrupt frame.

### Final software checkpoint and reproducible replay

Openpilot **`6d175daf9`** pins opendbc **`4f91b600`**, including radar lifecycle
commit `b579c04d` and the additional F33 cooperative fault reporting. The combined
Toyota/CAN/Toyota-safety/generic-interface/docs/platform/vehicle-model selection
passes **617 tests and 3,186 subtests**, with 262 existing skips in that selection.
Toyota Python lint passes. No EPS image, signer/runtime loader or Panda safety
policy was changed in this follow-up, and nothing was installed in a vehicle.

`tests/verify_camry_2026_radar_lifecycle_external.py` now makes the actual-parser
replay reproducible through the maintained sibling opendbc environment. Besides
the 17-source held-out reduction, it preserves original CAN publication
boundaries on six raw-source segments. Two are stock-harness bus0 captures,
and each produces 1,199 complete updates with zero reported CAN errors. Historical
repin inputs are explicitly remapped by the test; stock-harness sources are not.
This verifies source placement and parser behavior, not healthy EPS operation
in the incident-era stock-harness captures or a road qualification of fusion.

The six explicitly selected analysis suites all pass: radar anchors,
radar lifecycle reduction, actual-opendbc radar replay, current hardware-fault
projection, cooperative-fault projection, and cancellation evidence reduction.

## September 15 cancellation ownership follow-up

**Automatic cancellation is not solved by this follow-up.** It recovers a
previously omitted switch-event mirror and tests the historical host attempts
for an independent acceptance witness. No controller, Panda whitelist, ECU
image, or runtime installation is changed.

### Correct the search domain and the topology argument

The prior cancellation sweep covered the historical-repin **ADAS bus1**. It did
not cover all FRC-side **chassis bus2** outputs. An all-native-bus extraction of
the same 21 physical CANCEL windows now retains 168 shared address/length/bus
streams: 92 on bus0, 22 on bus1, and 54 on bus2. The single-bit screen includes
B0..B2 and starts its post-window 100 ms **before** the sampled button report,
so an earlier-published event is not excluded merely by choice of time origin.
The existing ADAS CRC result remains 16,526 valid frames and zero failures.

The expanded screen finds cancellation-related chassis outputs, including
`0x1B2` and `0x5F6`, that the old ADAS-only negative did not cover. It does not
recover a new ADAS-bus cancellation bit even with this earlier window. Timing
is host-publication timing, not an arbitration-level causal ordering.

Likewise, **an unsplit bus does not by itself make an event-only cancellation
command impossible**. It prevents suppressing and replacing a native source
stream. An accepted, cancel-only event could in principle coexist with native
traffic. Current upstream Hyundai/Volkswagen button encoders illustrate that
architectural distinction; their receiver behavior is not evidence that this
Toyota accepts the same technique. The removed brake-copy implementation is
still not qualified, and a bus-number change alone would not qualify it.

### `0x1B2` is a switch-event mirror, not an established control API

The original stationary recording
`targets/camry-2026/raw-20260826/camry_nrtd_cruise_can_sync_20260826.json.gz`
contains three isolated physical switch operations, independent FRC `0x1906`
responses, and their later `0x1B2` indications:

| Physical operation | Raw `0x1B2` indication | Independent FRC monitor |
|---|---|---|
| RES/+ | B0[7] | DID1906 B3[7], **Up Switch** |
| SET/- | B0[6] | DID1906 B3[6], **Down Switch** |
| CANCEL | B0[5] | DID1906 B3[5], **Cancellation Switch Condition** |

All 1,475 retained `0x08A` samples in that stationary recording report cruise
inactive. Therefore the mirror indications cannot be explained solely as a
consequence of an engaged cruise controller stopping. They represent the
recognized switch events. The three mirror pulses outlast the physical switch
assertions; this is not a direct unlatched copy of the switch level. A second
stationary cancellation indication appears at `0x5F6 B4[7]`.

The 184 stationary `0x1B2/32` frames have zeros after byte2. That is an observed
payload property, **not** proof that every possible receiver accepts unauthenticated
commands on this identifier. No signed/unsigned receiver policy follows from
zeros in a recorded trailer.

On the historical repin, `0x1B2` is observed on the FRC-side chassis link, bus2.
Four original stock-harness source windows place `0x1B2`, `0x5F6`, `0x198`,
`0x19C`, and the physical `0x0FE/0x101` traffic on unsplit bus1. This closes the
physical observation location, not logical receiver ownership behind the link.

The material missing fact is still **an ordinary receiver that acts on an
externally supplied cancel event**. The OEM diagnostic name and the recovered
wire mirror do not prove that the FRC, brake, or hybrid controller consumes the
mirror as a command. No `CANCEL_REQ` actuator field or production transmitter
is created from these observations.

### A concrete counterexample to two attractive candidates

`0x198 B4[3]` and `0x19C B0[1]` change in 20 of the 21 cancellation windows.
In route `3b`, segment97, before cancellation at `5896422235458 ns`, both are
already asserted across the pre-window. There are nine asserted samples of
each candidate spanning approximately 802 ms, alongside 34 native `0x08A`
samples that remain engaged. This excludes treating either bit, on its own,
as an unconditional current-cancellation indication. It does not prove that
no context-dependent receiver contract involving those PDUs exists.

### Historical host attempts do not establish acceptance

A separate extraction enumerates **all 463 complete original rlog segments**
across ten specified September1/4/6/7/10 routes. It discovers **375 actual
`sendcan 0x101` frames**, grouped into **58 episodes**. Native forwarding/TX
returns are not used to discover an attempted host command.

Every episode has fresh native switch/brake observations, cruise engaged
before the first host send, and a subsequent native cruise release. Every
one also has a raw physical CANCEL or brake assertion **at or before the first
host send**. All 375 host payloads satisfy the ordinary `0x101` additive
checksum. Thus payload construction and subsequent release are both observed,
but **none of the 58 episodes separates host-command acceptance from the
already sufficient physical driver action**. A TX echo does not supply the
missing ECU-acceptance observation.

The classifier has synthetic positive controls for a host attempt followed by
a release without a competing button/brake input. It separately rejects
forwarded-only echoes, missing release, missing correct-bus input coverage,
and competing driver input before release. A driver action after release does
not retroactively confound the earlier observation. These synthetic cases
validate the classifier, not a Toyota receiver.

The current cereal schema does not expose the former `fd` field. This
extraction deliberately makes **no new FDF/BRS claim** from a defaulted
`getattr(..., 'fd', False)`. Historic CAN-FD investigations must use their own
appropriate original metadata/schema evidence.

### Durable artifacts and verification

- `tools/targets/camry/extract/extract_camry_2026_cancel_ownership.py`:
  original-rlog extraction, with deterministic compression and source hashes.
- `tools/targets/camry/analysis/analyze_camry_2026_cancel_ownership.py`:
  stationary OEM correlation, all-bus screen, counterexamples, and host-attempt
  attribution without vehicle I/O.
- `data/generated/camry_2026_cancel_ownership.json` and the corresponding
  `tests/fixtures/camry_2026_cancel_{all_buses,host_attempts}.jsonl.gz`:
  portable source reduction and complete evidence needed by the new tests.

Run `tools/test camry_2026_cancel_ownership camry_2026_cancel_evidence`.
The new suite contains 17 tests, including the standalone extractor and
positive-control classifier cases. Receiver acceptance remains explicitly absent from the result; passing
these tests is not presented as completed automatic cancellation.

Both new fixtures were independently re-extracted from the original rlogs into
`build/out/cancel-ownership-regeneration` and compared byte-for-byte with their
tracked copies. Both comparisons pass. All 16 new regression tests and the
existing cancellation-evidence suite pass; lint and `git diff --check` pass.

The remaining uncertainty is not resolved by more accurate decoding of the
mirror itself. A controller that consumes only the original physical-switch
input and publishes `0x1B2` for observers, and a controller that also accepts
`0x1B2` as an external input, can both reproduce the retained observations.
Discriminating between them requires the relevant receiver's implementation
or an independent acceptance observation. The available exact EPS application
is not a substitute for that cruise-receiver implementation. No claim of
sender completion follows from the new passive mappings.

### Independent control-layer cancellation causality

An additional reduction starts at the ordinary
`carControl.cruiseControl.cancel` rising edge, rather than discovering episodes
from a particular outgoing CAN identifier. Its 79 explicitly retained requests
come from 71 SHA-256-checked original rlogs across 16 routes. This is a different
population from the 58 actual `sendcan 0x101` episodes described above; the two
counts must not be added or described as interchangeable.

Every one of the 79 requests is preceded by a source-real physical driver
assertion: 53 CANCEL-switch cases and 26 brake cases. The observed lead is
4.498020..8.364384 ms (median 5.259704 ms). All windows contain correct-bus
switch and brake observations on both sides of the host request. Historical
repin sources use physical input bus0 and native cruise bus2; the 11 retained
stock-harness requests use bus1 for both. Returned TX copies and other buses
are not used as driver inputs. The reducer verifies the brake additive
checksum and the recovered switch's complementary bit predicate; it does not
claim cryptographic verification of the protected switch trailer.

Native cruise is active before all 79 requests. Of those, 76 have an observed
release within 500 ms. Three have no release in that interval and are retained
as such, not converted into successful cancellation. In every release case,
the already preceding driver input prevents attributing release to an
independently initiated host command. `sendcan` is recorded as an attempt,
never as a receiving ECU acknowledgement. Missing event names in the old
`onroadEvents` message do not overcome this raw-CAN timing evidence.

The analysis also distinguishes a driver input between host request and cruise
release, an input only after release, missing input coverage, already-inactive
cruise, and an unwitnessed/held host flag. Even a release without a competing
observed driver input is only a candidate for further analysis, not an automatic
acceptance claim: unobserved causes and receiver ownership still matter.
These are offline evidence classifications, not new controller timing policy.

Reproduction uses
`tools/targets/camry/analysis/analyze_camry_2026_cancel_request_causality.py`,
`tests/fixtures/camry_2026_cancel_request_causality.jsonl.gz`, and
`data/generated/camry_2026_cancel_request_causality.json`. The extractor has
reproduced the fixture and report byte-for-byte from the original source files.
The 12 regression tests in
`tests/verify_camry_2026_cancel_request_causality.py` cover both the real windows
and independent synthetic counterexamples. Run
`tools/test camry_2026_cancel_request_causality camry_2026_cancel_evidence`.

The configured North-American Toyota ECU-supply-change lookup entry was also
checked through its ordinary public web entry. It redirected to a login page;
no account session, calibration result, or receiver firmware was acquired.
No calibration URL is inferred from a current software number. The available
EPS image cannot establish the cruise receiver's behavior, and the locally
retained Camry node0724 Engine/MG update is not an exact FRC/Brake receiver image.
This follow-up therefore adds no cancellation transmitter or vehicle mutation.

All three new cancellation fixtures were finally re-extracted from their
original rlogs and matched byte-for-byte, including the all-bus windows, the
463-segment host-transmission census, and the 79 control-layer request windows.
The three selected cancellation suites pass with zero failures or skips; the
new ownership and request-causality suites contain 17 and 12 tests respectively.
The direct extraction command also runs from outside the repository after
fixing its project-root import bootstrap. Python lint and diff checks pass.


### September 16: factory cruise input ownership and the missing receiver

The 2025 Camry service information, with procedures applicable from April
2024, gives a more specific investigation target than the earlier generic
"FRC/Brake receiver" wording. This is a same-generation 2025 circuit reference,
**not** proof that the maintainer's 2026 ECU has identical software or a given
CAN receive contract.

The factory Steering Pad Switch Circuit description assigns primary cruise
control to the **hybrid vehicle control ECU**. Its driving-assist, +RES,
minus and CANCEL switches use the CCS/CCSG resistor circuit. The wiring drawing
`GTY1267549` connects that circuit through the spiral cable to H63, while the
separate mode-select/LTA/distance circuit terminates at the forward recognition
camera's LKSW input. The hybrid system drawing `GTY1263732` also shows a direct
stop-light-switch input to the hybrid controller. These are circuit/ownership
facts; neither drawing supplies arbitration IDs or a CAN cancellation decoder.

Sources reviewed directly, including the drawings:

- [Camry Steering Pad Switch Circuit description](https://lemon-manuals.la/Toyota/2025/Camry%20SE%2C%202.5L%20Eng%20VIN%20A/Repair%20and%20Diagnosis/Accessories%20%26%20Equipment/Collision%2FAvoidance/Front%20Camera%20System%20-%20Diagnostic%20Codes%20%26%20Circuit%20Tests/Front%20Camera%20System/Steering%20Pad%20Switch%20Circuit%20%5B04%2F2024%20-%20%5D/Description/)
- [Camry Steering Pad Switch Circuit wiring, GTY1267549](https://lemon-manuals.la/Toyota/2025/Camry%20SE%2C%202.5L%20Eng%20VIN%20A/Repair%20and%20Diagnosis/Accessories%20%26%20Equipment/Collision%2FAvoidance/Front%20Camera%20System%20-%20Diagnostic%20Codes%20%26%20Circuit%20Tests/Front%20Camera%20System/Steering%20Pad%20Switch%20Circuit%20%5B04%2F2024%20-%20%5D/Wiring%20Diagram/)
- [Camry Hybrid Control System diagram, GTY1263732/GTY1268708/GTY1263832](https://lemon-manuals.la/Toyota/2025/Camry%20SE%2C%202.5L%20Eng%20VIN%20A/Repair%20and%20Diagnosis/Hybrid%2FElectric%20Powertrain/Testing%20and%20Diagnosis/Hybrid%20Control%20System%20-%20Diagnostics%20-%20Introduction/Hybrid%20Control%20System/System%20Diagram%20%5B04%2F2024%20-%20%5D/System%20Diagram%20%5B04%2F2024%20-%20%5D/)

This matters to the retained cancellation evidence. A primary physical button
or brake input can cancel cruise locally and subsequently appear on CAN. A
camera-side switch-event mirror remains an observable output until its
accepting receiver is established. Conversely, the direct circuit does **not**
prove that the hybrid controller lacks an additional CAN cancellation input,
and unsplit-bus placement alone does not exclude a cancel-only request.
`0x1B2` therefore remains a candidate requiring receiver evidence, not a proved
command or a disproved command.

The actual retained GTS registry keeps the following nodes distinct:

| Node | GTS category/database | Role |
|---|---|---|
| `0x724` | 395 / `MG_P5.ddb` | Motor Generator |
| `0x7D2` | 397 / `HV_P5.ddb` | Hybrid Control |
| `0x792` | 498 / `FRC_P5.ddb` | Front Recognition Camera |
| `0x7B0` | 435 / `ABS_P5.ddb` | Brake/EPB |

The source is `data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json`,
`profile.ecus` and the corresponding category bindings. The retained
`T-0051-26.cuw` is **node0724 Motor Generator**, not the hybrid-control node07D2.
The earlier convenient "Engine/MG" shorthand must not be interpreted as
possession of the cruise controller's application.

All ten members of that package were inspected through the existing validated
CUW parser and S-record decoder. Their records pass framing/checksum validation,
but the resulting application and routine bodies remain opaque; executable
receiver code was not recovered. The package names `8A2810602100`,
`8A2A10602100` and `8A2910601100` describe the MG package's logical blocks, not
a recovered exact-Camry hybrid-control application. Do not search these opaque
bytes for a coincidental CAN ID and call it a receive descriptor.

The ordinary current GTS Active-Test catalogues were checked for the retained
Engine, MG, Hybrid, Brake and FRC categories. No normal cruise-cancel actuator
was recovered. The separate `CCS_P5` and `HV_CCS_P5` views have data/diagnostic
and history tables but no direct or routine Active-Test tables in this corpus.
That is a bounded host-tool result, not proof of firmware absence. FRC's
"PDA Cancel Notification Display" remains a display test, not a DRCC command.

**Disposition:** prioritize the Hybrid Control receiver (`0x7D2`) and its
camera/brake request interfaces when acquiring additional firmware or receiver
specifications. Exact ECU identity/compatibility must still be established;
a related Crown or Grand Highlander node07D2 package is not automatically a
Camry receiver. Neither the EPS image, MG update, switch mirror nor the
confounded historical host attempts currently establishes automatic-cancel
acceptance. No sender, Panda permission, diagnostic control or vehicle command
was added in this investigation. The production feature remains unimplemented.

### Follow-up: select native releases, not host requests or physical CANCEL

The next pass changes the selection criterion. It scans every native chassis-side
`0x08A` cruise-latch falling edge in the **463 hash-checked sources across the ten
routes already enumerated by the host-attempt corpus**. This is independent of
whether the driver pressed CANCEL or openpilot requested cancellation. There are
**1,103,695 native cruise frames and 77 continuous active-to-inactive edges**.
The 500-ms preceding window contains a recovered CANCEL, main-switch, or brake
assertion at 74 edges. Three have continuous observations but no such assertion.
These counts describe this ten-route selection; they are not the same population
as the separate 79 rising host requests across sixteen routes.

The detector evaluates the whole CAN publication before attributing a release,
keeps malformed or missing input unknown, and does not carry an engaged state
across a cruise observation gap exceeding 100 ms. The 100-ms observation-gap and
500-ms context limits are declared analysis screens, not runtime control policy.
It retains raw pre-edge context for every release, original source identities,
and all native CAN, host sendcan, carControl and speed observations within three
seconds of the three selected edges. The new fixture is 621 KiB compressed;
none of the interpretation depends on an ignored scratch file.

| Selected route/segment | Native release timestamp (ns) | Recorded speed near edge | Source context |
|---|---:|---:|---|
| September 4 `0000003b--62262eb7a1`, segment 90 | 5499618127901 | 6.328 m/s | Adaptive mode; brake `0x101` B0[3] clear, but unnamed B1 takes 0/1/2/3 before release versus baseline 0/1 |
| September 7 `00000045--805b7ca6ab`, segment 4 | 671199398420 | 19.022 m/s | Adaptive mode; B0[3] clear, but unnamed brake B1 rises from baseline 0 to 3..7 in the preceding window |
| September 10 `0000008d--a9f348691a`, segment 6 | 3110034985633 | 8.084 m/s | Raw `0x251 B0` goes conventional-active `0x90` to conventional-available `0x88`; preceding brake B0[3] and B1 remain zero |

**None is an independent host-cancel acceptance observation.** All three have
no recorded `carControl.cruiseControl.cancel` assertion throughout their retained
six-second windows, no host sendcan on the enumerated cancel-candidate IDs, and
no assertion of the recovered `0x1B2` CANCEL mirror. The low-speed conventional
case is compatible with a stock operating-limit cancellation, but the source does
not establish its exact cause, threshold, or receiving command. Raw native mode
bytes take precedence over the historical `carState.nonAdaptive` default.

The two adaptive examples must not be named "automatic cancellations with no
driver input": the brake-byte variation is unresolved context. Conversely, B1
must not become a speculative `brakePressed` predicate. The reference images and
GTS descriptions available here do not establish what that byte represents,
whether its change is a cause or response, or an OEM threshold. The current
production brake decoder is therefore not changed by this analysis.

The retained `T-0051-26` Engine/MG package was reconsidered instead of rejected
solely for being node `0724`. Its twenty already-unpacked application/routine
regions are still opaque at this checkpoint; outer CUW and S-record decoding do
not provide an executable cruise receiver. This is distinct from saying that
Engine/MG cannot participate in cruise. The available exact EPS receive map and
brake consumers likewise do not establish FRC/Hybrid cruise-command acceptance.

Reproduction:

```sh
# Re-reduce the portable retained fixture and run classifier/source regressions.
uv run python tools/targets/camry/analysis/analyze_camry_2026_native_cruise_release.py
tools/test camry_2026_native_cruise_release

# Explicit full original-source scan, using the existing openpilot LogReader environment.
../kai-openpilot/.venv/bin/python \
  tools/targets/camry/analysis/analyze_camry_2026_native_cruise_release.py --extract
```

Artifacts are `data/generated/camry_2026_native_cruise_release.json` and
`tests/fixtures/camry_2026_native_cruise_release.jsonl.gz`. The executable tests
check missing/stale/corrupt input handling, source-bus and TX-echo exclusion,
input/host ordering, unclassified brake bytes, raw mode distinctions, native
release witnesses, and Profile-5 integrity of the retained ADAS request frames.

**Cancellation is not implemented or qualified by this follow-up.** The remaining
fact is an ordinary cancel input accepted by the actual cruise receiver, with its
format and ownership established. An isolated accepted-command observation or a
readable matching receiver implementation can close that fact; another search
of button mirrors cannot substitute for it. No production openpilot/opendbc or
Panda code, authentication path, EPS image, or vehicle state was changed.

Validation for this follow-up: **15 new native-release tests pass**. The native-release, existing host-request-causality and existing cancellation-ownership suites all pass (**3 suites, no failures or skips**). Targeted Python lint and `git diff --check` pass. These are analysis results, not a cancellation-feature qualification.


## September 16: 0x160 role and causality correction

The retained evidence does not establish the current Camry fine/coarse encoder
as a direct longitudinal-command interface. Independent wheel acceleration
matches native B4:B5 closely with cruise off (r=0.971345/0.988851 in the two
complete August captures), and B4:B5 stays zero until 223–262 ms after wheel
motion in three stock resumes. In all 1,249 counter-exact combined-trial pairs,
intact native B12 predicts the chassis result better than replacement B12
(r=0.930230 versus 0.700465 at nearest time). TX returns establish transport,
not receiver acceptance. The former "proves influence" wording is withdrawn.

Full source populations, timing/selection limits, GTS vocabulary boundaries,
and reproduction commands are in
[the longitudinal evidence report](camry-2026-longitudinal-evidence.md#september-16-command-versus-feedback-audit).
The tracked raw fixture and `camry_20260916_longitudinal_motion_audit.json` make this
correction reproducible without external September logs or ignored workspaces.
No production sender, safety policy, or vehicle firmware changed in this audit.

## September 16 follow-up: 0x160 is not a verified longitudinal command

The maintained [longitudinal evidence packet](camry-2026-longitudinal-evidence.md)
now includes an independent cross-check of camera B4:B5 against native chassis
`0x13C`, packed ego speed against valid raw wheels, and B12 alignment against
native `0x0CA`. Cruise-off fine-field correlations are 0.979857/0.988391 and
moving speed correlations are 0.999758/0.999936. These are affirmative
state-publication evidence, not just an absence of command acceptance.

The B12 lag advantage is shallow and sample-grid dependent; it is not a
measured ECU latency. The original replacement trial still does not establish
host influence when the untouched native camera value is included. No different
command, exact OEM field names, or complete receiver contract has been recovered.
The current Camry encoder must remain an unqualified hypothesis; neither
Corolla's reported behavior nor the project's DBC name establishes Camry demand
semantics. This follow-up changes only offline analysis, its tests/results,
and documentation. The companion role audit was independently completed; its
files were not staged or changed by this follow-up.


## September 16 follow-up: protected 0x08A is the leading longitudinal request candidate

Normalizing all retained captures by **Toyota network role** rather than raw
Panda bus number resolves the stock -> repinned -> stock ambiguity. During the
temporary CAN0/CAN1 repin, Toyota Bus 4 was the CAN0/CAN2 relay pair: protected
`0x08A/0x0C9` were native upstream on Panda bus2 and `0x0CA` was native chassis
return on bus0. After the Sep-11 restoration to stock Toyota-B, that Bus-4
request/result family is again on unsplit Panda bus1, while Toyota Bus-1 camera
FRC `0x020/0x160/0x230/0x440` uses source bus2 -> downstream bus0. The updated
stock-topology verifier pins those candidate families directly.

Against that corrected topology, `0x08A` B8:B9 and B11:B12 are the strongest
direct longitudinal candidates. Across both complete Aug-27 drives the two
signed16 words are identical in **44,617/44,617** source-side frames, span
roughly -1.15..+1.07 m/s² at 0.001 m/s²/count, and are independently bounded
away from simple measured-motion/steering identities. In all three retained
no-driver-input stock resumes they are already positive 500 ms before wheel
motion. Toyota's P5 Brake/Booster/EPB DDBs independently name upper/lower
"Request Acceleration ... from Toyota Safety Sense" as signed16 ×0.001, while
the FRC-hosted PCS recorder contains matching lower/upper TSS acceleration
request records plus IDs/allocation/arbitration results.

This is a strong **structural/semantic candidate**, not a byte-name proof:
upper versus lower cannot be assigned because the two words are equal in the
retained complete drives, and the 6-bit request IDs are still unmapped. The
direct FRC P05 streams `0x020/0x230/0x440` have no simple byte-aligned field that
reproduces the protected request word across both complete drives; `0x160` has
only state-related long-lag correlations and remains disqualified as the
implemented Camry demand interface. `0x0C9` is at most sideband/request metadata;
`0x0CA` is a chassis-to-upstream result/feedback return.

Because stock Toyota-B leaves protected `0x08A` on an **unsplit** network, the
preferred integration target is now the unrecovered **FRC -> arbitration/signing
precursor that produces 0x08A**, or another legitimate sole-emitter boundary.
Competing 0x08A injection is not authorized by this evidence. The Camry platform
therefore no longer advertises Alpha Long; stock longitudinal ownership remains
in force until a real actuator ingress is recovered. See the longitudinal
evidence packet and `data/generated/camry_2026_longitudinal_request_candidates.json`.
