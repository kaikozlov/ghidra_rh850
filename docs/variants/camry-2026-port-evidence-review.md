# 2026 Camry vehicle-state and cancellation evidence

This report owns the retained vehicle-model, radar, fault-projection and
cancellation evidence. Current implementation status and software pins belong
in the [capability matrix](camry-2026-capability-matrix.md); longitudinal
request/result semantics belong in the
[longitudinal report](camry-2026-longitudinal-evidence.md).

## Vehicle-model interpretation

`VehicleModel.update_params()` multiplies `CP.tireStiffnessFront/Rear` by
`vehicleParameters.stiffnessFactor`. `paramsd.VehicleParamsLearner` likewise
initializes its model globals from those same CP stiffnesses. A learned value
near 1.0 therefore supports preserving the configured baseline; it does not
justify replacing `CP.tireStiffnessFactor=0.7933` with 1.0.

The 15.3 steering-ratio default is a separate absolute learned quantity.
The actuator-delay default is 0.18 s; identical cached lagd values on
consecutive routes are not independent fresh estimates.

## Radar units and lifecycle

`data/generated/camry_2026_radar_anchors.json` and its raw-object-byte fixture
retain 17 original rlog identities and independent vision/gyro observations.
The independent anchors are:

| Quantity | Corrected observed wire interpretation | Independent anchor |
|---|---|---|
| Range | unsigned B0:B1 × 0.005 m | 1,953 vision-associated observations: r=0.998518, slope=1.029071, median absolute error 0.799 m |
| Lateral | signed12 B2:B3[7:4] × 0.04 m, left-positive | 240 off-center vision observations: slope=0.982563; 27,602 continuity-qualified gyro pairs: r=0.843106 and inferred LSB=0.038909 m/count |
| Relative speed | signed low14 B1:B2 × 0.025 m/s; B1[7:6] excluded | vision-speed slope=0.992347; signed12 wraps 113 retained high-closing-speed observations |

Joint range/range-rate correlation cannot determine a common scale factor.
Signed13 and signed14 velocity interpretations agree on the retained data;
the wider field boundary is not independently resolved. Track lifecycle is
established below; optional confidence/class labels remain unassigned.

The corrected full August reconstruction consumes each time-bounded occurrence
rather than overwriting repeated counter values: 30,532 / 35,994 complete
four-record bank bursts. Its kinematic agreement corroborates the independent
unit anchors above.

### TSS3 0x123/16 is a new Profile-5 radar-status PDU

The old Toyota radar parser's STATUS_MSG is also CAN ID 0x123, but its
7-byte TSS2 layout does **not** transfer. In that DBC RADAR_STATUS occupies
B2 bits3..4; on TSS3 B2 is the rolling Profile-5 counter, so interpreting the
new frame with the old status definition produces a counter-derived fake state.

The retained August Camry drives establish the TSS3 envelope independently:
all **5,130 / 5,999** 0x123/16 frames pass Profile-5 CRC with Data ID
0x0123, B2 spans all 256 counter values, and the application payload is
01 0c 08 00 a0 00 00 00 00 00 00 00 00. A full local archive scan on
2026-09-23 covers **538,298** incoming 0x123/16 frames across **916** rlogs
and finds only two application payloads: the baseline above on 538,079 frames
and 01 0c 08 00 a0 10 00 00 00 00 00 00 00 on 219 frames across five
segments.

Current GTS+ Fr_RadSen_P5.ddb gives a direct semantic join for B7:B8.
Front Radar Sensor DID 0x100F is a Data Monitor bitfield whose MSB0 bits
8..13 are, in order, **Dirt Detection for Radar Cruise**, **Dirt Detection for
PCS**, **Partially Dirt Detection**, **Foreign Matter Detection**, **Dirt
Detection**, and **Blockage Detection**. Mapping those six bits onto the
observed two-byte B7:B8 word places them exactly at B8[7:2]. The only dynamic
CAN bit seen in the archive is B8[4], which therefore lands exactly on GTS+
bit11 **Foreign Matter Detection**. This closes the generation-correct
0x123 status definition used by opendbc; it is not the legacy
RADAR_STATUS/RADAR_PRE_FAULT layout. GTS+ separately names temporary optical-
axis unavailability in DID 0x1012 and function restriction in DID 0x2093;
their CAN carriers remain unassigned and should not be invented from the
constant bytes of 0x123.

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
parser value. Each cycle byte increments independently modulo256. Missing cycles
retire identity because they may hide a one-frame
lifecycle event. Duplicates, mixed-cycle geometry/motion, bad CRC, truncation and
wrong buses cannot manufacture an update; ordinary CAN timeout clears stale
tracks and publishes a CAN error rather than waiting forever for a missing
trigger PDU. End-old/start-new ordering is explicit.

The retained opendbc replay of 60,969 held-out bank pairs produced **20,323
complete updates**, **308,111 qualified point observations**, **17,868 observed
identity replacements**, and **zero reported CAN errors** in source replay.
These Camry fixtures do not establish another vehicle's radar contract.

Reproducible source reduction:
`tools/targets/camry/analysis/analyze_camry_2026_radar_lifecycle.py`,
`data/generated/camry_2026_radar_lifecycle.json`, and
`tests/fixtures/camry_2026_radar_lifecycle_holdout.jsonl.gz`.
The extractor verifies original rlog hashes and P05 integrity before writing
its deterministic fixture. `tests/targets/camry/verify_camry_2026_radar_lifecycle.py` checks
both discovery captures and the independent holdout.

## Driver torque and sender-attribution evidence

The September-4 routes `0000003b--62262eb7a1`, `0000003c--97b9e7a69a`
and `0000003d--0e812cecba` distinguish successful sending from steering
control. They contain 751,664 direct-B6 host sends, 751,628 Panda TX returns
and 33 rejected returns. In 181 fresh, low-driver-torque samples where the
stock and host targets diverge by at least 2.5 degrees, median measured-angle
error is 0.79 degrees against stock versus 2.02 against host; stock is closer
in 134 samples versus 47. Driving windows have no Panda bus-off or transmit-
error accumulation. This is negative evidence for that sender/configuration,
not the status of the maintained `0x08A` port.

Those routes also expose a separate driver-state defect: the recorded parser
held `steeringPressed=False`, preventing ordinary torque-nudge lane changes.
The retained replay fixtures `tests/fixtures/camry_20260904/3c-seg43.jsonl`
and `3d-seg1-torque.jsonl` compare opendbc `c7a62eaf` with `ca52a67f`:
valid angle/torque decoding is unchanged, while the high-torque fixture changes
from zero to 797 pressed samples out of 1,001. The reproducer is
`tools/targets/camry/utilities/replay_camry_tss3_carstate_revisions.py`.

Independent September-6 routes `3e/3f` supply the sign and threshold evidence:
all 45 observed lane-change starts have positive torque for left and negative
for right. Toyota's `0x371 B20[4]` detector has a sampled assertion median of
0.67 N·m and release medians of 0.37/0.34 N·m. The port's 0.6 N·m threshold
is an openpilot policy, not an OEM single-comparator claim. Detailed source
reduction: `data/generated/camry_20260906_hands_off_warning_audit.json` and
[the hands-on evidence](camry-2026-tss3-opendbc-port.md#hands-on-detection-and-hud-evidence).

## Fault projections

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

Camry `CarState.steerFaultTemporary` reports this current fault/inhibit
aggregate through the ordinary upstream interface. "Temporary" describes current
steering unavailability.
`steerFaultPermanent` is not fabricated from the same
one-bit aggregate: neither exact cause nor restart-required status can be
reconstructed from it. Other unrepresented classes remain outside this selected
fault projection. H/F and Crown are not assigned the F33 policy by analogy.

Reproducible proof:
`tools/targets/camry/analysis/analyze_camry_f33_live_fault_projection.py`,
`data/generated/camry_f33_live_fault_projection.json`, and
`tests/targets/camry/verify_camry_f33_live_fault_projection.py`.

### Cooperative-control faults: two additional source-real inhibits

Exact F33 also reports `CAFC` at `0x030 B16[0]` and `CAD9` at `0x030 B19[0]`.
These are separate from the selected hardware/DEM aggregate at B6[2]. Fresh
stock-code tracing closes their RTE staging through `D0D7C -> BF3AA -> 4C2DC ->
4C97A`; generated-COM signals 25 and 31 bind them to those wire locations.
`CE772` requires both clear before entering ready, and `CE7A6` leaves ready
when either asserts. The inspected CarState maps B6[2] (`EPS_FAULT_INHIBIT`) to
`steerFaultTemporary`; the two cooperative inhibits remain decoded DBC fields.
Their firmware meaning does not imply that the current host aggregates them.


The permanent/transient distinction is provably lossy at this projection:
`CEC72` ORs `CAFB==1` and `CAFD==1`. `CEE7C` clears the request-failure source
in inactive profile 7, whereas `CEF26` retains the asserted rate-latch source;
`CEC0C` clears both during subsystem initialization. These two causes publish
the same command-inhibit bit. Assigning a restart-required boolean from that
bit would therefore invent information. This does not rule out a distinct,
as-yet-unrecovered status or diagnostic source.

The additional verifier executes stock OR, RTE, readiness and recovery code;
only scalar packing/status submission is replaced by argument observation.
It checks the actual stock packer arguments and both values. **59 assertions
pass**, adding to the
85 live hardware-fault assertions. Source, generated evidence and runnable
verifier are `analyze_camry_f33_cooperative_fault_projection.py`,
`data/generated/camry_f33_cooperative_fault_projection.json`, and
`tests/targets/camry/verify_camry_f33_cooperative_fault_projection.py`.

## Cancellation evidence

The maintained port implements cancel output; see the
[port report](camry-2026-tss3-opendbc-port.md#maintained-integration).
This section owns the bounded conclusions of the retained September captures,
not a declaration that the current feature is absent.

Three selections answer different questions and must not be added together:

| Selection | Result | Artifact |
|---|---|---|
| 58 actual host-send episodes, 375 `sendcan 0x101` frames across 463 segments | Every episode has physical CANCEL or brake input at or before the first host send; none isolates host-command acceptance | `camry_2026_cancel_ownership.json` |
| 79 rising CarControl cancel requests from 71 hashed rlogs / 16 routes | All follow physical driver input (53 switch, 26 brake); 76 have a release within 500 ms, three do not | `camry_2026_cancel_request_causality.json` |
| 77 native cruise releases from 1,103,695 frames in the ten-route ownership corpus | 74 have preceding decoded driver assertions; the other three have no host cancel request and therefore are not host-acceptance witnesses | `camry_2026_native_cruise_release.json` |

Artifact paths below are under `data/generated/`. Each reducer retains its
source hashes and selection rules. A TX return establishes transmission, not
an ECU acknowledgement.

### Physical-switch and mirror observations

The 21 retained physical CANCEL windows include preceding engagement, no
overlapping brake assertion, and release delays of 29.756–172.179 ms (median
70.439 ms) on the host publication clock. They are retained in
`tests/fixtures/camry_2026_cancel_windows.jsonl.gz`.

The ADAS-only screen tested 17,824 bit/polarity hypotheses and 279,904
contiguous field layouts without a common cancel edge. That negative applies
only to its 22 ADAS streams. The all-native-bus extraction covers 168 streams
and recovers the following switch mirrors; the ADAS CRC population remains
16,526 valid frames.

### `0x1B2` switch-event mirror

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

The 184 stationary `0x1B2/32` frames have zeros after byte2.

On the historical repin, `0x1B2` is observed on the FRC-side chassis link, bus2.
Four original stock-harness source windows place `0x1B2`, `0x5F6`, `0x198`,
`0x19C`, and the physical `0x0FE/0x101` traffic on unsplit bus1.

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
as an unconditional current-cancellation indication.

### Factory cruise input ownership

The 2025 Camry service information, with procedures applicable from April
2024, gives a more specific investigation target than the earlier generic
"FRC/Brake receiver" wording.

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
`0x1B2` remains a candidate.

The actual retained GTS registry keeps the following nodes distinct:

| Node | GTS category/database | Role |
|---|---|---|
| `0x724` | 395 / `MG_P5.ddb` | Motor Generator |
| `0x7D2` | 397 / `HV_P5.ddb` | Hybrid Control |
| `0x792` | 498 / `FRC_P5.ddb` | Front Recognition Camera |
| `0x7B0` | 435 / `ABS_P5.ddb` | Brake/EPB |

The source is `data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json`,
`profile.ecus` and the corresponding category bindings. The retained
`T-0051-26.cuw` is **node0724 Motor Generator**. Hybrid Control is node07D2.
The earlier convenient "Engine/MG" shorthand must not be interpreted as
possession of the cruise controller's application.

All ten members of that package were inspected through the existing validated
CUW parser and S-record decoder. Their records pass framing/checksum validation,
but the resulting application and routine bodies remain opaque; executable
receiver code was not recovered. The package names `8A2810602100`,
`8A2A10602100` and `8A2910601100` describe the MG package's logical blocks.

The ordinary current GTS Active-Test catalogues were checked for the retained
Engine, MG, Hybrid, Brake and FRC categories. No normal cruise-cancel actuator
was recovered. The separate `CCS_P5` and `HV_CCS_P5` views have data/diagnostic
and history tables but no direct or routine Active-Test tables in this corpus.
FRC's
"PDA Cancel Notification Display" controls notification display.

### Native releases without a decoded button edge

The native-release reduction scans every native chassis-side
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
across a cruise observation gap exceeding 100 ms. The offline analysis uses a
100-ms observation-gap limit and 500-ms context limit.
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
uv run --locked python -m tools.targets.camry.analysis.analyze_camry_2026_native_cruise_release
tools/test camry_2026_native_cruise_release

# Explicit full original-source scan, using the existing openpilot LogReader environment.
uv run --no-sync --project ../kai-openpilot/opendbc_repo python -m \
  tools.targets.camry.analysis.analyze_camry_2026_native_cruise_release --extract
```

Artifacts are `data/generated/camry_2026_native_cruise_release.json` and
`tests/fixtures/camry_2026_native_cruise_release.jsonl.gz`. The executable tests
check missing/stale/corrupt input handling, source-bus and TX-echo exclusion,
input/host ordering, unclassified brake bytes, raw mode distinctions, native
release witnesses, and Profile-5 integrity of the retained ADAS request frames.

### Cancellation reducers and fixtures

- `tools/targets/camry/analysis/analyze_camry_2026_cancel_evidence.py`
  and `data/generated/camry_2026_cancel_evidence.json` own the initial
  physical-switch windows and ADAS screen.
- `tools/targets/camry/extract/extract_camry_2026_cancel_ownership.py`
  and `tools/targets/camry/analysis/analyze_camry_2026_cancel_ownership.py`
  own the all-bus screen and host-send population.
- `tools/targets/camry/analysis/analyze_camry_2026_cancel_request_causality.py`
  owns the independent CarControl-edge population. Driver input leads those
  requests by 4.498020–8.364384 ms, median 5.259704 ms.
- The corresponding tracked fixtures are
  `tests/fixtures/camry_2026_cancel_{all_buses,host_attempts,request_causality}.jsonl.gz`.
  Classifier tests include independent positive and negative controls for
  driver-input timing, missing observations and forwarded-only echoes.

The retained switch mirrors and confounded host attempts do not identify a
receiving ECU's cancel-command parser. That is a limit of these captures, not
evidence that the maintained controller lacks an output path.
