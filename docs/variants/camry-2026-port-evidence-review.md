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
Its 85 assertions cover all64 source combinations, each class assertion and
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
with262 pre-existing skips in that selection. Toyota lint passes. New radar
adversarial coverage includes batching, deletion/replacement, unqualified
retained geometry, duplicate/wrapped/skipped cycles, CRC, truncation, timeout,
startup spread across publications, and wrong-bus traffic. Exact-F33 CarState
fault assertion/recovery and unrelated status-bit separation are covered too.
Automatic cruise cancellation remains a separate receiver/ownership question;
none of these changes restores the invalid unsplit-bus fake-brake sender.
