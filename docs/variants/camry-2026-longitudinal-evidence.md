# 2026 Camry longitudinal evidence packet and status (WP4)

**Current disposition — September 16 request/result closure:** `0x160` is an
FRC-origin longitudinal/ego-state publication, not the demonstrated Camry
actuator ingress. The central request surface is `0x08A`: it carries the
FRC-submitted upper/lower longitudinal request packages plus the recovered lateral
request tuple. Brake-owned `0x081` publishes the downstream selected/employed result state.
The Camry `0x160` B4:B5+B12 encoder remains withdrawn.

The current architecture is more precise than the earlier shorthand
"FRC request -> Brake arbitration." Toyota Motor Corporation's
US20200070849A1 describes a generic vehicle-movement interface in which each
**request longitudinal ID is the identifier of an application**. A request
arbitration unit independently selects lower- and upper-limit longitudinal IF
packages from the applications; request-generation units then carry the
selected application IDs/accelerations toward the powertrain and brake
controllers. The powertrain additionally compares the selected application
request with the driver's accelerator request. The reported
`arbitration result_longitudinal ID` is the selected application's ID when the
application request is employed, or a distinct value that identifies a driver
request when the driver wins. The patent also defines the analogous lateral ID
as an application identifier. This is generic Toyota architecture, not by
itself a byte-level proof for F33, but it matches the recovered `0x08A/0x081`
behavior unusually closely.

That distinction explains the ID63 observation cleanly. On the Camry, FRC-origin
`0x08A` request slots carry IDs such as 0/4 and 11/17; **ID63 is not observed in
either request slot**. Brake/VMC-owned `0x081` can instead report ID63 after the
VMC compares the FRC-submitted bounds with driver demand. Toyota labels 63
`Driver Operation` on a P5 FRC diagnostic display surface, but that display does
not make 63 an FRC-origin request: dynamically it is result-side feedback from
the downstream VMC. The strongest current model is therefore **FRC-submitted
application request package(s) in `0x08A`, downstream arbitration/employed-source
feedback in `0x081`**.

The retained source document is local-only under
`REFERENCE/patents/toyota_vehicle_movement_arbitration_patent/US20200070849A1.pdf`
(`REFERENCE/` remains intentionally ignored). Public source:
<https://patents.google.com/patent/US20200070849A1/en>.

Transport, request semantics, physical publication/security ownership, and
actuator authority remain separate questions. Later source-direction evidence
places protected `0x08A` publication inside the FRC assembly, while the recovered
Toyota architecture places request arbitration downstream in the Brake/VMM
layer. The exact Brake code implementing that arbitration, the security/physical
handoff, and the upper-vs-lower A/B ordering remain unresolved.

**Request/result wire closure:** FRC normal-Tx suppression establishes `0x08A`
as the upstream TSS request/instruction plane; Brake owns `0x081` and continues
publishing it with request-loss supervision if the FRC request disappears. The
byte-level audit maps `0x08A B8:B9/B11:B12` to the indistinguishable signed16
x0.001 upper/lower acceleration-request pair, and maps `0x081 B6[5:0]` /
B20:B21 as the strongest `5284` employed-source-ID / `57DB` result-acceleration
pair. `0x0CA` remains protected longitudinal/chassis state but is no longer the
primary result interpretation. See
`data/generated/camry_2026_longitudinal_request_plane.json`.

## September 16: command versus feedback audit

Inputs are both complete tracked August-27 CAN captures and seven original
rlog segments: September-11 combined trial `000000d4--327b2c4bb8`, segments
2–5, and September-4 stock routes `0000003b--62262eb7a1` segment 84 and
`0000003c--97b9e7a69a` segments 26–27. Selected original frames, publication
timestamps, source-file identities, and SHA-256 values are retained in
`tests/fixtures/camry_20260916_longitudinal_motion_audit.jsonl.gz`. No live vehicle access,
new sender, firmware change, or production port change is part of this audit.

The reducer is
`tools/targets/camry/analysis/analyze_camry_20260916_longitudinal_motion_audit.py`; its
portable result is `data/generated/camry_20260916_longitudinal_motion_audit.json`.

### B4:B5 is feedback-like on this Camry

The existing signed-15/0.001 interpretation closely reproduces a derivative of
independent `0x0AA` wheel speed. This is not a comparison against our own
controller request or against another presumed command field. At speeds above
2 m/s and with the native cruise-operating latch clear:

| Complete capture | Samples | Correlation with measured acceleration | Fitted measured/field slope | Intercept (m/s²) |
|---|---:|---:|---:|---:|
| August drive A | 7,032 | 0.971345 | 0.966845 | −0.000761 |
| August drive B | 9,822 | 0.988851 | 0.970301 | −0.002508 |

These figures compare the field against a 400-ms centered wheel-speed
derivative 100 ms earlier. The same-time correlations are also high:
0.965798 and 0.986154. The all-moving populations give 0.966444 and 0.986667
at the −100-ms shift. The cruise-active subset of drive A has little excitation
and a much weaker relationship (r=0.616232); do not hide it or claim universal
per-regime precision. Both complete PDU streams pass the recovered CRC:
20,510 and 23,998 frames.

The negative shift is consistent with estimated/filtered motion being
reported after the physical change. It is **not a measured ECU or actuator
latency**: CAN publication times and the derivative filter both contribute.
The analysis rejects invalid wheel samples, long interpolation gaps,
extrapolation, future cruise-state samples, and joins across source files.

The stock start transients are a separate discriminator. Using the first
mean-wheel speed above 0.1 m/s near each previously identified resume:

| Stock resume | First nonzero B4:B5 after motion | B4:B5 at +200 ms | Mean wheel speed at +200 ms |
|---|---:|---:|---:|
| `3b`, near 5122.256 s | 261.861 ms | 0 | 0.479 m/s |
| `3c`, near 9068.054 s | 222.947 ms | 0 | 0.472 m/s |
| `3c`, near 9147.517 s | 252.375 ms | 0 | 0.472 m/s |

An unconstrained acceleration-demand interpretation for this field does not
explain these stock starts: the vehicle is already accelerating while the fine
field remains zero. A measured-acceleration/estimated-motion role is the
stronger interpretation. This is a **bounded semantic classification**, not
recovery of an OEM field name or proof that the entire PDU is read-only.

### Independent chassis-state and ego-speed cross-check

A second reduction in the maintained motion-audit producer now checks the two
complete August captures against raw chassis messages, rather than relying
only on the wheel-speed derivative or the current port's signal names. Inputs
are already tracked; regeneration needs neither `REFERENCE/` nor `build/`.

| Cross-check | Drive A | Drive B |
|---|---:|---:|
| Fine B4:B5 vs native `0x13C` acceleration-like word, all samples: r | 0.979516 | 0.989355 |
| Same comparison, cruise off: r | 0.979857 | 0.988391 |
| Cruise-off median absolute difference (m/s²) | 0.005 | 0.013 |
| Packed speed vs valid raw wheels above 2 m/s: r | 0.999758 | 0.999936 |
| Speed median absolute difference (m/s) | 0.018750 | 0.020139 |
| Moving speed samples | 8,930 | 14,413 |

The packed speed candidate spans B7:B9. Its observed numerical encoding is
compatible with the existing Toyota wheel-speed representation; this is an
ego-speed match, not a new OEM name or command definition. Invalid wheel flags
are rejected. The acceleration comparison uses the preceding chassis sample
within 100 ms; speed uses the preceding wheel sample within 80 ms. Neither
joins across original source files or consumes a future sample at the queried
instant. The `0x13C` word remains described structurally; the independently
derived physical acceleration and stock-start evidence are what anchor its
measured-motion interpretation.

This substantially strengthens the **ego-state publication** interpretation
of the PDU. It does not prove all its other fields are telemetry, that only a
radar consumes it, or that changing reported state could have no indirect
control effect. In particular, our DBC name `TSS3_LONGITUDINAL_REQUEST` is a
project-assigned hypothesis, not Toyota evidence.

### B12 timing favors a return-derived quantity, but does not measure a path delay

A native-sample sweep, restricted to the stock cruise-operating intervals,
aligns B12 best with `0x0CA` **50 ms earlier in both complete drives**:
r=0.951994 and 0.989911. However, same-time r is already 0.951673 and 0.989495.
The peak is shallow. The separately reviewed fixed-25-ms-grid role reducer
places its maxima at -50/-75 ms; this sampling dependence is another reason
not to claim an exact 50-ms or 75-ms ECU delay or causal chain.

The supported statement is narrower: the data does not show B12 uniquely
leading the result-like chassis channel. The three stock starts and the
intact-native comparator below provide more discriminating evidence than the
lag maximum alone. A state export derived from an already selected result, or
parallel outputs of a common internal calculation, both remain compatible.
There is no established byte-copy from a different FRC command.

The follow-up independently re-extracted the 28-source role-audit fixture
from the original rlogs: **306,073 publication events** reproduce byte-for-byte
(SHA-256 `c15b4e9544fc73624fe8aff09c2f40cda8196039de4eb83cee038605f37c2833`).
The companion role audit below was completed separately during this review.
The maintained motion-audit producer and its seven-source fixture independently
own the core physical-motion, native-comparator, resume, and direction checks;
the new cross-checks above use the already tracked full August captures.

### Combined replacement does not establish host influence

All **1,249** host frames can be paired to a CRC-valid preceding camera frame
with the **same B2 counter** in the same original source file. Source ages are
1.619–2.733 ms (median 1.879 ms). This is a local time-bounded match, not a
whole-route dictionary indexed by an 8-bit wrapping counter. All 1,249 have a
byte-identical returned Panda TX within 3.892–21.305 ms. Thus this audit is not
mistaking a host send request for proof that the frame was actually transmitted.
The returned TX still does **not** acknowledge receiver acceptance.

B4:B5 differs from its native source in 1,243 frames; B12 differs in 970.
Comparing the result-like `0x0CA B7:B8` with the intact source and replacement:

| `0x0CA` observation time relative to host | Intact native B12 correlation | Replacement B12 correlation |
|---|---:|---:|
| −100 ms | 0.932004 | 0.671457 |
| Nearest time | 0.930230 | 0.700465 |
| +100 ms | 0.923148 | 0.727055 |

Correlations use the historical `−0.1 × signed7(B12)` convention to align the
sign. The assumed magnitude is not a newly proved actuation scale. Restricting
to the **970 frames where the two B12 values actually disagree** preserves the
result: at nearest time native r=0.926554 versus host r=0.696919.

The native quantity is still the better predictor, including of a result
published before the host frame. Closed-loop co-movement can explain the
previously quoted host/result correlation without the modified field causing
it. This does **not** prove an effect is exactly zero; it invalidates that
correlation as independent evidence of acceptance, and it invalidates "DRCC
clamping" as an established explanation. The preceding cruise mode is
conventional-active `0x90` for 1,247 frames and conventional-available `0x88`
for two transition frames. Healthy adaptive-mode behavior is not represented.

### B12-before-motion is not B12-before-the-native-output

At 500 ms before the wheel-defined motion onsets, the three `0x0CA` result-like
values are already **+0.453, +0.335, and +0.516 m/s²**, while B12 remains at its
preceding baseline (+0.1, −0.1, and 0 under the historical comparison convention)
and B4:B5 remains zero. B12 changes later but still before wheel motion.
The complete neighborhoods, not only threshold-crossing timestamps, are in the
result artifact. Different quantization/filtering and parallel calculations
prevent treating this temporal order as a unique internal dataflow proof.
Nevertheless, "B12 changes before the car moves" cannot identify it as the
upstream command: an export of an already selected native acceleration can do
that too.

The three stock segments also directly separate native traffic from Panda
returns: `0x0CA` has **7,641 native bus0 frames and 7,641 returned bus2 TXs
(src=130)**, with no native bus2 copy. It is a chassis-to-camera publication on
the temporary repin, not a proven FRC-origin acceleration request. In these
same captures `0x160` is native on bus1. On the restored stock harness, the
camera link is the split bus2→bus0 pair and `0x0CA` is on unsplit bus1.
Toyota network numbers and Panda indices must not be mixed across harnesses.
The exact chassis ECU that publishes `0x0CA` remains unassigned here.

### What GTS and the source inventory do—and do not—establish

Direct reads of the retained `FRC_P5.ddb` expose both estimated motion and
request/output vocabulary. DID `0x1253` names **Estimate Vehicle Acceleration**.
DID `0x1B08` contains **Driver Acceleration for Output**, **Acceleration Limit
for Output**, and **Acceleration for Output**. Those names are diagnostic
observables, not an assignment to a particular byte of `0x160`.

The previously proposed `0x1B03..0x1B07` join is specifically an **ISA**
upper-limit/permission surface. It must not be described as a proved generic
DRCC demand decoder. Brake `0x10A1..0x10A4` and the TSS operation-FFD request
and arbitration records provide additional semantic candidates, but no retained
synchronized sample or receiver implementation binds them to these CAN fields.

The September-1 source-isolation notebook supports FRC normal-Tx ownership of
`0x160`; it does not prove every quantity in an FRC transmission is a request.
The `0x0C9` member of the same recorded source group was also checked rather
than promoted by ID adjacency: in the two August captures its only changing
application word is B12:B13, with zero header/counter/trailer. It is **not** a
SecOC-shaped alternative command in those captures. No alternate FRC command
is identified by this audit.

**Implementation consequence:** keep the Camry alpha encoder explicitly
unqualified. Do not call its current fine/coarse field writes production-ready,
rename them as OEM demand signals, remove the intact native comparator from
future analyses, or replace this hypothesis with a speculative different
sender. A mixed-role PDU or a mode-dependent request remains possible. The
available data supports exported/feedback-like quantities more strongly than
it supports the claimed direct control path, but does not prove `0x160` can
never carry a usable command on this or another Toyota.

Reproduce without `REFERENCE/`, `build/`, original September rlogs, or a car:

```bash
uv run python tools/targets/camry/analysis/analyze_camry_20260916_longitudinal_motion_audit.py
tools/test camry_20260916_longitudinal_motion_audit
```

The optional `--extract-fixture` path rereads the seven external originals using
an existing openpilot Python environment; it does not call vehicle tooling.


### Independent original-source recheck and the meaning of "echo"

The follow-up review reread the **28 original rlogs** selected by the expanded
local role analysis: September-11 `d1` segments 3–6 and 9–12, `d4` segments 0–6,
historical relay-direction route `2d` segments 0–5, September-4 `3b` segments
83–85, and `3c` segments 25–28. The last two groups retain the declared
four-second neighborhoods around the three stock-resume landmarks. This is a
selection of source files/windows, not a claim to have reviewed every Camry
route or every message in those files.

Re-extraction produced **306,073 original publication events** and was
byte-identical to the existing expanded local fixture
`tests/fixtures/camry_2026_longitudinal_role.jsonl.gz`
(SHA-256 `c15b4e9544fc73624fe8aff09c2f40cda8196039de4eb83cee038605f37c2833`).
Both `tools/test camry_20260916_longitudinal_motion_audit` and the existing
worktree suite `tools/test camry_2026_longitudinal_role` passed. The expanded
role files were already pending at the start of this review and were not
staged or altered; the committed seven-source motion audit above remains the
portable source for its reported conclusions.

The expanded comparison supplies useful independent corroboration: native
B4:B5 agrees with the chassis `0x13C` signed-15 numerical channel in both August
captures (r=0.979516/0.989355; median absolute difference 0.006/0.014 m/s²), and
a separate packed speed candidate in `0x160` agrees with raw wheel speed
(r=0.999789/0.999942). These are numerical/behavioral matches, **not** OEM
signal-name assignments or proof of a byte-for-byte forwarding operation.
The wheel-derivative audit and stock starts remain important because merely
matching a second presumed command would not resolve the original question.

The disposition must distinguish four claims:

- **FRC-origin publication:** supported by source isolation and camera-side
  observations. Sender identity alone says nothing about request authority.
- **Fine acceleration field:** motion/feedback-like on the captured Camry;
  treating B4:B5 as a demonstrated independent acceleration demand is not
  supported.
- **B12:** related to a native longitudinal result that can precede physical
  motion. Its best native alignment follows `0x0CA`, and the untouched native
  comparator outperforms the replacement during the combined trial. This
  favors an exported state/result interpretation, but does not recover the
  exact consumer or exclude mode-dependent use.
- **Entire PDU / alternative command:** neither "all 32 bytes are telemetry"
  nor "a byte-exact echo of another FRC command" is established. A mixed-role
  PDU is still possible. No replacement longitudinal command is identified by
  this review, and `0x0CA` must not silently be promoted to that role either.

The leading working model is an FRC publication of ego-motion and
longitudinal-state information onto the ADAS link, potentially for other
perception participants. The recipient and internal transformation remain
unrecovered. Even an observed vehicle response to altered state information
would not, by itself, establish a proper acceleration-demand interface.

This follow-up changed the review only. No vehicle interaction, sender,
controller, Panda rule, firmware, or experimental-mode default was changed.
`REFERENCE/` and `build/` remain ignored and were not staged.

## Expanded passive review: physical source is not control authority

The pending role audit was independently re-extracted from **28 original rlog
segments**. Its **306,073 retained publication events** reproduce the existing
fixture byte-for-byte (SHA-256
`c15b4e9544fc73624fe8aff09c2f40cda8196039de4eb83cee038605f37c2833`). Both complete
August captures were then reprocessed independently of those September logs.
The expanded evidence lives in:

- `tools/targets/camry/extract/extract_camry_2026_longitudinal_role.py`
- `tools/targets/camry/analysis/analyze_camry_2026_longitudinal_role.py`
- `tests/fixtures/camry_2026_longitudinal_role.jsonl.gz`
- `data/generated/camry_2026_longitudinal_role.json`

**Working diagnosis:** the examined Camry fields fit an FRC publication of ego
motion and selected longitudinal state better than a direct independent
acceleration-demand interface. A perception/radar-side state report is the
leading architectural interpretation, **not a recovered receiver contract**.
Neither "every field is telemetry" nor "the packet can never influence control"
follows. It is also not established that this is an exact echo of some other
FRC-origin command: the correlated `0x0CA` channel travels from the chassis
side toward the camera on the historical split.

### Independent ego-state comparisons

With no additional unit fit, the fine field agrees with the acceleration-like
quantity in chassis `0x13C`: all-sample correlations **0.979516 / 0.989355**, with
median absolute differences **0.006 / 0.014 m/s²** in August A/B. This names the
observed chassis channel, **not its physical ECU owner or an OEM signal**. The
independent wheel derivative and cruise-off moving results above avoid circularly
validating one presumed command against another presumed command.

A separate packed speed-like field in `0x160` follows mean wheel speed with
correlations **0.999789 / 0.999942** and median absolute differences about
**0.019 / 0.020 m/s**, above the declared low-speed cut. The selected packet
therefore contains ego-state information, not merely an acceleration-shaped
number. Its validity/sentinel semantics and every other field remain unmapped.
Invalid wheel flags are excluded rather than interpreted as zero speed.

In the restored-harness d1/d4 captures, with cruise disengaged and speed above
2 m/s, the fine field also agrees with the independently wheel-derived
`carState.aEgo`: **r=0.970690 / 0.957737**, using **6,096 / 6,503** samples.

### B12 timing is consistent with a report, but is not a causal clock

The complete native sweeps align B12 best with `0x0CA` **50 / 75 ms earlier**.
However, the level-correlation gain over zero lag is only
**0.000258 / 0.000472**; correlations of 200-ms changes peak at just
**0.185 / 0.455**. The peaks are broad, the series autocorrelated, and rlog
publication timestamps are shared by a CAN batch. Do not turn the maximizing
lag into an exact gateway delay or proof of an internal dataflow edge.

The actual start neighborhoods are more useful. Relative to the first three
consecutive raw-wheel samples above 0.025 m/s:

| Stock resume | `0x0CA` result-like field persistently >0.5 m/s² | Fine field persistently >0.05 m/s² |
|---|---:|---:|
| 3b / 5122.256 s neighborhood | −441 ms | +272 ms |
| 3c / 9068.054 s neighborhood | −372 ms | +263 ms |
| 3c / 9147.517 s neighborhood | −482 ms | +262 ms |

These definitions differ from the 0.1 m/s onset / first-nonzero-field table
above; they are not contradictory estimates. No gas, brake, RES, SET, or CANCEL
assertion is present in the declared −1.0 to +0.5 s windows. At the −500-ms
landmarks, `0x0CA` is already positive while B12 is still at its preceding
baseline. **B12 preceding wheel motion is not evidence that it precedes the
native longitudinal decision.** Different resolutions and filtering still
prevent an exact copy/transform claim.

### Actual replacements and the native comparator

The expanded d1 selection contains **10,259** host frames, **10,228** changed
fine fields, and no B12 modifications. The d4 selection contains **1,249** host
frames, **1,243** changed fine fields, and **970** changed B12 fields. Every host
frame has a source/time/counter-matched native template and valid CRC; d4 has
**1,249/1,249** exact returned TX payloads. All changed bytes are confined to the
historical encoder's declared fields and CRC. These establish transport only.

At a common 25-ms grid during d4 replacement, native B12 versus the `0x0CA`
result-like channel has **r=0.931904**, while replacement B12 has **r=0.699657**
(**1,244** observations). All 1,244 have a preceding conventional-active `0x90`
mode observation within 1.5 s. The age bound reflects the slow mode message;
unknown-mode observations remain explicitly counted instead of silently labeled.
No healthy adaptive-mode acceptance claim follows from this trial.

The host and stock controllers share a moving scene, and the camera continues
to observe the car while its ADAS-side output is being replaced. Either closed
loop can correlate with the same motion. The better intact-source fit defeats
the previous correlation-only proof of host authority; it does not prove zero
possible influence or identify a particular acceptance gate.

### Source ownership, vocabulary, and remaining information boundary

The September-1 notebook §19 records `0x160` **40 → 0 → 40** under FRC normal-Tx
suppression/restoration on the observed ADAS network. This supports the FRC
publication source, not a propulsion/brake destination. The full six-segment
historical relay capture has `0x0CA` **13,756 native bus-0 RXs** and **13,256
returned bus-2 TXs**, versus only 503 startup/native bus-2 observations. FRC-side
`0x08A` has the opposite dominant direction. On the restored stock harness,
`0x160` is the camera-side ADAS source and `0x0CA` remains on the unsplit chassis
network. Panda bus indices are not Toyota network numbers.

Direct GTS DDB queries reproduce `FRC_P5` DID `0x1253` (estimated acceleration)
and `0x1B08` (separate driver, limit and output accelerations). `0x1B03..0x1B07`
are ISA-specific request/permission observables, not a generic decoded DRCC
request. Brake `0x10A1..0x10A4` name TSS requests, but no retained synchronized
CAN/DID sample assigns these names to B4:B5 or B12. The current checked-in
firmware inventory contains EPS applications, not the relevant Camry
longitudinal producer/receiver implementation. EPS receive behavior cannot fill
that provenance gap. The candidate re-rank below identifies a protected
chassis-facing request carrier, but not yet the preferred upstream replacement
carrier.

### Longitudinal candidate re-rank after topology normalization

The earlier search mixed three harness eras too easily. Raw Panda bus numbers are
therefore normalized to Toyota network role before any candidate is compared:

| Capture era | Panda CAN0/CAN2 relay pair | Panda bus 1 | Longitudinal interpretation |
|---|---|---|---|
| Stock Toyota-B before the temporary repin | Toyota Bus 1 camera/ADAS: source side bus2 -> downstream bus0 | Toyota Bus 4 Brake/EPS/chassis, unsplit | Same physical wiring as the restored configuration below; direct-Panda ELM327 mux state is a separate axis |
| Temporary CAN0/CAN1 repin (Aug-27 through lateral development) | **Toyota Bus 4**: upstream `0x08A/0x0C9` on bus2 -> chassis bus0; `0x0CA` returns bus0 -> bus2 | **Toyota Bus 1** camera/radar/FRC P05 family | Healthy Sep-4 DRCC routes `3b/3c` are in this era |
| Stock Toyota-B restored in the Sep-11 integration cleanup | **Toyota Bus 1** camera/ADAS: FRC `0x020/0x160/0x230/0x440` source bus2 -> downstream bus0 | **Toyota Bus 4** request/result/chassis family `0x08A/0x0C9/0x0CA`, unsplit | Current production-shaped topology |

`harnessStatus=flipped` means harness/cable orientation, **not** the physical
CAN0/CAN1 repin. Likewise Panda sources 128/130 are returned host-TX echoes, not
additional ECU transmitters. The regenerated stock-topology artifact checks all
seven request/result candidate IDs explicitly rather than inferring this mapping
from unrelated state messages.

With that normalization, protected Bus-4 **`0x08A` is the strongest direct
chassis-facing longitudinal candidate**. It was already recovered as a
multi-function TSS request/state PDU carrying Target Lateral ID and target
steering angle. The complete August captures add a second, independent shape:

- B8:B9 and B11:B12 are signed16 words and are **identical in 44,617/44,617
  source-side frames** across the two complete drives;
- their raw ranges are -1146..+995 and -1102..+1070, naturally giving
  -1.146..+0.995 and -1.102..+1.070 m/s² at 0.001 m/s²/count;
- the prior complete-capture census independently bounded these words away from
  simple measured-motion/steering interpretations: all four joins against
  wheel-derived acceleration, steering angle, driver torque, and target-angle
  rate have `|r| <= 0.0967`;
- in all three no-driver-input Sep-4 stock resumes, the B8/B11 value is already
  positive **500 ms before wheel motion** (+0.350, +0.277, +0.391 m/s²) and has
  risen to +0.828/+0.605/+0.590 m/s² at the wheel-defined onset. The duplicated
  words remain equal throughout these retained neighborhoods.

Toyota's own GTS surface supplies an unusually exact semantic template. Current
P5 Brake/Booster/EPB dictionaries expose `0x10A1` **Request Acceleration of
Upper Limit from Toyota Safety Sense** and `0x10A2` **...Lower Limit...**, both
signed16 at 0.001 m/s², plus 6-bit upper/lower request IDs (`0x10A3/0x10A4`) explicitly occupying bits7:2.
That geometry gives a new structural join: `0x08A B6` and `B7` each split exactly
as a six-bit request-ID candidate in bits7:2 plus a two-bit 0..3 allocation-method
candidate in bits1:0. Active Camry cruise uses `(ID11, allocation1)` and
`(ID17, allocation3)`; the Brake-side selected result is overwhelmingly ID11.
The FRC-hosted PCS Operation-FFD recorder independently contains record `5280`
"TSS required acceleration (lower limit)" and `5281` "TSS request acceleration
(upper limit)", again signed16 at 0.001 m/s², as well as longitudinal IDs,
braking/driving-force allocation, and arbitration-result records.

The original two-drive result did **not** resolve upper-versus-lower ordering because
B8:B9 == B11:B12 in all 44,617 frames in that selected corpus. A 2026-09-22
archive-wide raw-log census supersedes that limitation. Scanning every recoverable
`rlog.zst` / `*.rlog.zst` under `~/dev/inspect/logs` with `LogReader`, and retaining
native-RX `0x08A/32` observations (`src < 128`), yields **1,505,266 observations from
605 rlogs**. Only 48 have unequal B8:B9/B11:B12 values, but 12 of those are the
ordinary Camry DRCC tuple `(ID11,allocation1)/(ID17,allocation3)`, spread across six
independent route segments as two-frame episodes. Their `(B8:B9, B11:B12)` values in
m/s² are `(+0.682,-0.769)`, `(+0.687,-0.437)`, `(+0.217,-0.442)`,
`(+0.432,-0.659)`, `(+0.215,-0.452)`, and `(-0.621,-0.701)`: **A > B in 12/12
ordinary-DRCC unequal frames**. The first five episodes occur immediately before the
request drops to idle `0/4`; the sixth occurs on an idle->active transition. This is
strong dynamic evidence that, for the ordinary `11/17` DRCC package, **B8:B9 is the
upper acceleration bound and B11:B12 is the lower acceleration bound**, with B6/ID11
paired to the upper slot and B7/ID17 paired to the lower slot.

The other 36 unequal observations are one distinct route-45 intervention family with
request IDs `13/20`, B5=`0x04`, B8:B9 sweeping `-0.175..-0.500 m/s²`, and B11:B12
held at zero. That tuple is structurally different from ordinary DRCC and must not be
used to invert the `11/17` ordering; its exact application semantics remain unnamed.
This still stops short of a synchronized literal DID-to-byte proof for `0x10A1..0x10A4`,
but the ordinary-DRCC A/B upper/lower ordering is no longer open.

The alternatives now rank as follows:

1. **Protected `0x08A` B8:B9/B11:B12** — strongest direct downstream TSS
   acceleration-request candidate.
2. **Protected `0x5AF` B26** — a coarse longitudinal companion, not a
   replacement for the `0x08A` magnitude. Interpreting B26 as signed 6-bit gives
   a reproducible fit of **0.251/0.246 m/s² per count** against the `0x08A`
   request word (r=0.756/0.857), but its best alignment is **50/75 ms after**
   `0x08A`. Around the three stock resumes it steps through small signed values
   as the fine request rises. Low-rate `0x5F7` B7 shows a similar coarse family
   (raw signed6 values are multiples of four; fitted scale is ~0.062 per raw
   count, i.e. ~0.25 per four-count step) and likewise does not lead `0x08A`.
   These are better treated as quantized request/result/status companions than
   as the originating acceleration command; no OEM field name is assigned.
3. **`0x0C9`** — upstream-to-chassis and therefore directionally plausible as
   sideband/request metadata, but B12:B13 correlates only weakly with `0x0CA`
   (best |r| 0.265/0.140 in the two complete drives) and remains `0x1838`
   through the early portion of all three stock-resume ramps. It is not the
   leading acceleration-magnitude carrier.
4. **`0x0CA`** — other protected longitudinal/chassis state in the wrong
   direction for an FRC request. The newer `0x081` request/result audit supersedes
   the old B3:B4/B5:B6/B7:B8 arbitration-result interpretation.

The direct FRC Toyota-Bus-1 P05 candidates `0x020/0x160/0x230/0x440` were also
screened against the protected `0x08A` request word using every byte-aligned
8/16/24/32-bit signed/unsigned BE/LE field and +/-300 ms lags. `0x020`, `0x230`,
and `0x440` have **no** same-sign field reproducing at |r| >= 0.25 in both
complete drives. `0x160` has moderate state-related correlations (best
min-|r| 0.631), but those maximize at the **+300 ms search boundary** and overlap
its already recovered ego-state structure.

A second screen covers all **47 recurring protected Bus-4 PDUs** that vanished
under the Sep-1 FRC CommunicationControl normal-Tx suppression. `0x08A` itself
is excluded as the reference. Every byte-aligned signed16-BE field plus
signed-low6 fields is compared in both complete drives. This recovers the
coarse `0x5AF`/`0x5F7` companions above, but **no second same-scale signed16
acceleration carrier**. Thus there is no second same-scale request magnitude hiding in the
observed FRC-dependent protected domain. This does **not** mean a different semantic
request must exist before `0x08A`: the retained CommunicationControl experiment
already establishes `0x08A` as the upstream TSS request-side plane. A proxy or
signer may physically publish the protected Bus-4 PDU, but that is a
transport/cryptographic ownership question, not a second request layer.

This distinction matters for the port. On the temporary repin, `0x08A` sat on
the intercept pair and its source side was observable separately. On final
stock Toyota-B it sits on **unsplit Panda bus1 with the stock sender and chassis
consumer together**. Therefore "just transmit modified `0x08A`" is not a clean
production replacement strategy even if its acceleration fields are fully
recovered. The remaining integration problem is therefore **source suppression /
sole-emitter ownership for the already-recovered `0x08A` request plane**. If a
separate FRC-to-signer publication handoff exists, recovering it would solve that
physical ownership problem; it would not reveal a different semantic request.
Do not return to the disproved Camry `0x160` B4:B5+B12 encoder.

`0x08A` should also not be described as *all* authoritative TSS3 FRC egress.
It is the central observed continuous request PDU and already carries the full
recovered lateral request family plus the strongest longitudinal acceleration
request candidates. Toyota's FRC-hosted recorder also exposes upper/lower
longitudinal request IDs, braking/driving-force allocation, shift/EPB,
override/priority and other request metadata whose exact wire locations are not
all mapped. Ordinary FRC state/display/ego-motion publications (`0x020`,
`0x160`, `0x230`, `0x440`, `0x371`, `0x412`, etc.) also exist outside `0x08A`.
The bounded claim is **central control-request plane**, not exhaustive FRC output.


### Request/result recorder layout: what is actually mapped

Toyota's architecture changes the meaning of the longitudinal pair. The lower and
upper packages are independently arbitrated **bounds** on allowed acceleration, not
two redundant acceleration commands. The downstream powertrain compares driver demand
with those bounds and clips it into the selected range; the longitudinal result ID then
reports the request source whose acceleration was actually employed. This explains why
result ID63 (`Driver Operation`) can appear while neither `0x08A` bound-package ID is
63. Equality of the two retained acceleration words means the observed bounds collapse
to the same value in those states, or that a remaining wire/order assumption needs
refinement; it must not be described as intentional duplication by design.

GTS independently preserves the request-generation boundary described by Toyota.
Brake-domain P5/P6 databases expose `0x10A1..0x10A4` as upper/lower requests **from
Toyota Safety Sense**, then separately expose `0x10A5..0x10AA` as upper/lower target
acceleration, target ID, and target driving force **from Vehicle Motion Control**. That
is the diagnostic equivalent of application request -> arbitration/request generation
-> controller target.

The recorder schema and wire evidence now line up as follows. "Strong candidate"
means the width/scale, topology, and dynamic arbitration behavior match, but no
synchronized diagnostic/FFD value directly names that wire field.

| Toyota recorder quantity | Wire disposition | Evidence status |
|---|---|---|
| `5280` lower longitudinal request ID | one of `0x08A B6[7:2]` / `B7[7:2]` | strong structural candidate; A/B upper-vs-lower assignment unresolved |
| `5280` lower acceleration | one of `0x08A B8:B9` / `B11:B12`, s16 x0.001 m/s² | mapped as indistinguishable pair |
| `5280` force distribution | paired `B6[1:0]` / `B7[1:0]` with its ID byte | strong structural candidate; 0..3 exactly matches Toyota allocation enum; A/B ordering unresolved |
| `5280` shift / EPB / override / priority | unresolved | complete-drive byte census does not justify an OEM-name assignment |
| `5281` upper longitudinal request ID | the other of `0x08A B6[7:2]` / `B7[7:2]` | strong structural candidate; A/B upper-vs-lower assignment unresolved |
| `5281` upper acceleration | the other of `0x08A B8:B9` / `B11:B12`, s16 x0.001 m/s² | mapped as indistinguishable pair |
| `5281` upper force distribution | the other of `B6[1:0]` / `B7[1:0]` | strong structural candidate; no synchronized upper/lower oracle |
| `5282` lateral request ID | `0x08A B21[5:0]` | recovered |
| `5282` requested pinion angle | `0x08A B18:B19` | recovered; controller scale is 0.00100012 rad/count versus recorder 0.001 |
| `5282` steering assist gain | `0x08A B24` x0.01 | strong structural join |
| `5282` damping gain | `0x08A B25` x0.01 | bounded; zero in both complete drives |
| `5284` arbitration-result longitudinal ID | `0x081 B6[5:0]` | strong candidate; observed values 11 and 63 |
| `5285` arbitration-result lateral ID | `0x081 B13[5:0]` | recovered |
| `57D3` acceleration-valid flag | unresolved | `0x081 B11[4]` is proven request-loss supervision, but is not OEM-joined to `57D3` |
| `57DB` arbitration-result acceleration | `0x081 B20:B21`, s16 x0.001 m/s² | strong candidate |
| `57DE` arbitration-result pinion angle | `0x081 B16:B17` | recovered |

The packed-ID interpretation has an independent arbitration check. In the same
pairs, selected `0x081` result ID11 equals `0x08A B6[7:2]` in **1,525/1,529**
Drive-A and **3,276/3,281** Drive-B ID11 samples; it never equals the B7 candidate.
Every selected ID63 sample (**15,544 / 16,718**) has ID63 absent from both FRC
request A/B fields. Toyota's P5 FRC diagnostic display vocabulary includes
`63 = Driver Operation`, and Toyota's movement-control patent explicitly allows
the **result** longitudinal ID to carry a driver discriminator when driver demand
is employed. Thus 63 is evidence for Brake/VMC result feedback to the FRC, not an
FRC requester. This also strongly supports B6/B7 as packed FRC-submitted
application-ID/allocation bytes rather than generic ACC-state bytes.

The retained delayed-stop corpus gives a second dynamic check and supersedes the
old raw-byte `ACC_STATE` description. Ordinary active cruise is
`B6/B7=0x2D/0x47`, which decodes to request A `(ID11, allocation1)` and request B
`(ID17, allocation3)`. Accelerator override produces `0x2C/0x46`, preserving IDs
11/17 while changing allocation methods to 0/2. The three delayed hold episodes
contain **198** frames of `0x2D/0x67` or `0x2C/0x66`: request B changes to ID25
while the same allocation 3/2 distinction remains. Independently, `0x08A B4[5]`
is set on **198/198** of those delayed-hold frames and clear on every other native
`0x08A` frame in the complete `3b/3c` routes (zero XOR violations). A moving
retained `B7=0x65` is ID25/allocation1 with B4[5] clear, proving ID25 alone is not
a standstill flag. Camry runtime therefore uses the source-real B4[5] structural
hold state; the ID25/allocation2-or-3 tuple is its independent request-state
corroboration. The exact OEM recorder name for B4[5] remains unknown.

### Longitudinal request IDs versus result-source IDs

Do not flatten the FRC request IDs and Brake/VMC result IDs into one wire namespace.
`0x08A` carries **FRC-origin application request IDs** for the upper/lower bound
packages. `0x081` carries the downstream **employed-source result ID**; that result
can identify the driver even though no FRC request used that number. The numeric
values are identities, not priorities or ECU addresses. The current Toyota corpus
does not contain one complete longitudinal 0..63 request enum analogous to EMPS
`Target Lateral ID`. A six-region sweep
of current GTS+ and Techstream V18 (NA/EU/JP; 3,207 DDB files total) found the
same sparse named anchors but no hidden complete `5280/5281/5284`, `0x1284`, or
P6 longitudinal-arbitration value dictionary. The tracked request-plane producer
now extracts the relevant labels directly from Toyota DDBs rather than hard-coding
them.

The working namespace is:

| ID | Longitudinal evidence | Lateral comparison | Current disposition |
|---:|---|---|---|
| **0** | P5 FRC ISA Vertical ID names `No Request`; Camry request A uses 0 while idle | `No Request (Manual Operation)` | common no-request anchor |
| **4** | Camry request B idle/default | LDA | longitudinal OEM name unknown; lateral label must not be copied |
| **9** | P6 Speed Limiter Requesting Vertical ID explicitly names `ISA` | no generation-20 lateral label | named cross-generation longitudinal/vertical anchor; not observed on Camry `0x08A` |
| **11** | Camry request A during ordinary DRCC; `0x081` result ID11 when that application request is employed | LTA/LCA | **strong shared-TSS-application-ID hypothesis**, not yet an OEM longitudinal enum name |
| **17** | Camry active request B; retained 2025 Corolla active request A | no lateral label | repeatable cross-platform active longitudinal requester; OEM name unknown |
| **18** | not observed in Camry longitudinal A/B | SDG; P6 PDA-SA lateral request also uses 18 | lateral-only named anchor; no longitudinal transfer |
| **23** | retained 2025 Corolla active request B | no lateral label | observed longitudinal requester; OEM name unknown |
| **25** | Camry delayed ACC-hold request B (with allocation state distinguishing held/moving use) | AP | unresolved application identity; no longer treated as a namespace counterexample |
| **36** | 33-frame (~0.79 s) Camry startup-only request-B state; zero request acceleration; result stays 63 | no lateral label | startup/initialization requester; OEM name unknown |
| **41** | P6 MaaS lower-limit longitudinal ID = `Request 1 of MaaS Autonomous Driving System` | AD (Lv.4) | plausible shared automated-driving application identity |
| **45** | P6 MaaS lower-limit longitudinal ID = `Request 2 of MaaS Autonomous Driving System` | DES (Lv.4) | plausible shared automated-driving application identity |

**Result-side-only observation:** longitudinal ID63 is OEM-labeled `Driver Operation`
on a P5 FRC diagnostic display surface and is observed in Brake/VMC-owned `0x081`.
It is absent from both FRC-origin `0x08A` request slots in the retained Camry and
Corolla evidence, so it must not be listed as an observed FRC longitudinal requester.

Toyota's architecture materially strengthens the ID11 observation: it defines both
the longitudinal request ID and the lateral request ID as the **identifier of an
application**. The leading model is therefore a coordinated/shared application-ID
namespace, not two unrelated numeric enums. Camry ID11 is the ordinary DRCC
longitudinal application source while generation-20 lateral ID11 is LTA/LCA, making
ID11 a strong TSS continuous-driving application-identity candidate. This is still not
an OEM label assignment for the longitudinal field: the static corpus does not publish
the complete longitudinal value dictionary. ID25 and P6 41/45 are retained as semantic
clues, not counterexamples—axis-local labels can describe different control roles of
the same application.

Toyota also exposes feature-specific longitudinal-ID recorder fields that can
supply future direct joins: `5271` **IFU request vertical ID (lower limit)**,
`5A04` **PDA(OAA) Request Vertical ID**, and `5B07` **Longitudinal Request ID of
Lower Limit from PDA(DA)**, in addition to generic `5280/5281/5284`. The retained
same-car Operation-FFD samples do not contain those longitudinal records, so no
numeric values can yet be attached to those feature names. A future stock
capture that exercises them is a much better enum oracle than inferring names
from numeric coincidence.

The retained FRC CUWs do not currently solve the missing names. Their ReproStd
`.xx` members are Motorola-S-record framing around a manufacturer-encrypted
target representation (DFI encryption method 1); the selected host path does
not decrypt/decompress that application payload. Until that transform is
recovered, the FRC application image cannot be searched as plaintext for an ID
table, and **absence of a firmware enum has not been established**.

The cross-platform Corolla evidence is now owned by its tracked rlog reducer:
idle A/B are 0/4, active A/B are 17/23, and its `0x081` result stays ID63 across
all 2,000 retained result frames. That reinforces the requester-identity model
without assigning 17 or 23 an OEM feature name.

Across 17,073 / 19,999 request-result pairs in the complete A/B drives,
`0x081 B20:B21` correlates with the request at r=0.941674 / 0.836884. The more
discriminating result-ID split is stronger: for selected ID63 the median
result-minus-request is **0.000 m/s²** in both drives (p10/p90 only a few
milligravity-scale counts apart), while selected ID11 gives median deltas
**-0.181 / -0.435 m/s²**. That is the behavior expected of an employed-source/result publication rather
than a second request echo. In Toyota's documented architecture, the selected
application upper/lower request may still be constrained or superseded by the
driver request in the powertrain/brake execution layer.

This closes `0x08A` as the **unified observed continuous TSS3 request-side envelope**
for the recovered lateral tuple plus longitudinal request magnitudes. It does
*not* close the entire `5280/5281` metadata record into that PDU: the two request
ID/allocation bytes are now structurally located but their upper/lower ordering is
unresolved, while shift/EPB/override/priority and validity remain unmapped. Correspondingly, `0x081` is the Brake-owned selected/employed-result/reference
envelope, with the longitudinal result fields now visible alongside the previously
recovered lateral result. Physical publication ownership does not by itself prove
that every selection step executes inside the Brake ECU.

The reproducible reduction is
`data/generated/camry_2026_longitudinal_request_candidates.json`, generated by
`tools/targets/camry/analysis/analyze_camry_2026_longitudinal_request_candidates.py`
and protected by `tools/test camry_2026_longitudinal_request_candidates`.

Reproduce the portable reductions:

```bash
uv run python tools/targets/camry/analysis/analyze_camry_2026_longitudinal_role.py
tools/test camry_2026_longitudinal_role camry_20260916_longitudinal_motion_audit
```

This review changes only passive evidence tooling and documentation. No ECU,
Panda, authentication, vehicle-control, or firmware operation is performed.
The local research bundle under `REFERENCE/camry_2026_0x160_role_audit/` and
all re-extraction workspace files under `build/` remain ignored/untracked.

---

The following historical record predates this role audit. Its transport and
observational results remain useful; any earlier causal interpretation is
superseded by the intact-source comparison above.

## Discovery record

This Camry work predates the independent Corolla live report. Commit `6d02fc4`
documented the non-SecOC `0x160` request-plane candidate on 2026-08-31;
`d73baf5` added the offline generator later that day; `1661e5c` then recovered
and implemented the exact Profile-5 integrity contract. Commit `198d8da`
documented the native openpilot integration path on 2026-09-05. The attributed
albinoelephant Corolla field run was reported on 2026-09-10. Its contribution
is independent live validation, not the original discovery or generator. The
contributor's 2026-09-11 architecture/change reference is now retained under
`community/albinoelephant/`;
it documents the Corolla-specific B4:B5 request, Data ID `0x444A`, and the
post-fault handoff design, but the exact source checkout and rlog are still
external.


## Historical stock-ACC configuration (Milestone-A longitudinal arrangement)

Before the current test branch, `TOYOTA_CAMRY_TSS3` set `openpilotLongitudinalControl=False`,
`pcmCruise=True`, Toyota `STOCK_LONGITUDINAL`, and `autoResumeSng=False`; the
current TSS3 `CarController.update()` emits only the exact-F33 C7 lateral
sideband and returns, so Toyota still owns acceleration. Physical RES/SET
buttons and the parsed `0x08A`/`0x251` set-speed state choose `vCruise`;
`radarUnavailable=True` is not a planner blocker (generic radar interface
publishes an empty set; model-lead `radarState` continues). Verified in the WP2
audit replay and stock-harness opendbc `3c79d935`.

The current branch instead uses the ordinary openpilot ownership shape, gated
by the standard Alpha Long toggle: it captures the camera-side 32-byte `0x160`
and emits at most once per new camera B2 counter. Corolla retains its validated
signed-15 B4:B5 mapping at 0.001 m/s²/count. Camry modifies B4:B5 and the
additional inverse signed-7 B12 candidate at 0.1 m/s²/count, while otherwise
relaying the camera request byte-exact. Panda blocks the camera copy only while
its normal longitudinal-allowed state authorizes the replacement and bounds
both Camry request quantities independently. The 2026-09-11 trial below proved
the transport path and disproved B4:B5 alone as a sufficient Camry mapping; the
later dead-EPS trial observed protected-result co-movement during combined
replacement under conventional cruise, without the requested physical stopping
behavior. The September-16 audit does not attribute that co-movement to the host.

## Evidence matrix (FRC `0x160` request plane)

| Question | Status | Evidence |
|---|---|---|
| Wire geometry | **established** (firmware-static + captures) | 32-byte PDU; B0:B1 CRC-16/CCITT, B2 mod-256 counter, no secret; `tools/targets/camry/live/camry_frc_request_poc.py` clones/recomputes offline. The recovered init=`0xFFFF`/Data-ID=`0x0160` expression and the contributor's init=`0`/Data-ID=`0x444A` expression are deterministically wire-equivalent for this fixed PDU length. |
| Selected controller field | **Camry command mapping unproved; fine field is feedback-like; combined-trial causality withdrawn** | The independent Corolla road implementation causally establishes signed-15 B4:B5 at 0.001 m/s²/count. Route `000000d1--ad906be282` replaced 10,228 Camry frames with B4:B5 modifications while leaving B12 stock; the protected result continued tracking B12. In route `000000d4--327b2c4bb8`, 1,249 combined replacements changed B4:B5 and inverse signed-7 B12. Protected `0x0CA` varied, but the intact native camera value predicts it better than the replacement; the desired stop-sign response did not occur while stock DRCC was unavailable. |
| Command semantics | **correlation observed; host influence and full command authority unproved** | In three no-driver-input stock auto-resumes, B12 ramps in the acceleration direction 351–433 ms before ego motion. At the start of the combined trial, openpilot's B12 and protected `0x0CA` moved in the expected direction, but across strong-braking samples requested acceleration correlated only `r=0.276` with the protected result and `r=0.176` with measured acceleration. |
| Scale/sign | **comparison sign supported; request meaning/scale and gating unresolved** | Synthetic B12 and protected `0x0CA` result correlate negatively across the complete replacement windows, but when openpilot requested as much as −1.2 m/s² under conventional cruise, the protected result remained roughly −0.15 to −0.34 m/s². This does not prove a literal 0.1 m/s²/count physical scale or full authority. |
| Validity/counter rules | **transport observed, receiver processing unproved** | Profile-5 counter/CRC and one-for-one source-counter-paced TX are observed; absence of an observed integrity fault does not establish acceptance. Gap, replay, authority, and fault thresholds remain untested. |
| Receiver acceptance | **processing/authority unproved with a genuine conventional latch; `0x251` substitution did not establish engagement** | FRC DRCC attempts were rejected and the successful cruise latch in route `000000d4--327b2c4bb8` was conventional (`0x251` B0=`0x90`). Panda suppressed the stock downstream copy and transmitted the combined replacements, but the requested stopping deceleration was not applied. In route `000000d9--a1a459c5b5`, accepted synthetic `0x251` `0xA0/0xC0` frames did not make authenticated `0x08A` active even once; stock `0x251=0xE0` also continued on the unsplit bus. |
| Source ownership | **FRC transmit side observed; downstream receiver unresolved** | The 2026-09-01 selective normal-Tx suppression run isolates `0x160` as a 40-Hz FRC normal-Tx PDU. Which downstream participant accepts/transforms it, and its exact replacement/fallback contract, remain open. |
| Physical response | **combined synthetic stopping response negative without DRCC** | Four captured short stock stops auto-resume without gas/brake/RES/SET; in three examples B12 ramps before motion and protected `0x0CA` exceeds +0.5 m/s² 413–503 ms before motion. In the combined trial, measured acceleration closely followed the limited protected result (`r=0.912` over strong-braking samples), not openpilot's substantially stronger requested deceleration; the driver directly observed that the car did not slow for the modeled stop sign. |
| Release/override | **partially closed** | Short-stop auto-resume works natively. After ~5.2–9.3 s stopped, Toyota enters a delayed hold state (`0x08A` B7 `0x67`, `0x66` on accelerator override); all three retained long-hold exits require accelerator input, and hold clears before motion. The command-side hold/release semantic is not yet mapped. |
| Fault behavior | **no request-path fault observed; standstill remains open** | The moving combined-request trial completed without an observed request-integrity/system-malfunction fault. The Corolla port initially faulted at complete standstill; its 2026-09-11 contributor architecture note reports a successor frame-for-frame/camera-counter handoff plus <~1 mph stock relay that validates stop/go externally. That does not close the distinct Camry hold/release contract. |
| Source suppression | **live transport validated** | Route `000000d1--ad906be282` retained all camera-side bus-2 templates while the active replacement windows had no competing native bus-0 copy. Across segments 3–6 and 9–12, openpilot emitted 10,259 bus-0 `0x160` frames paced by the camera counter; 10,228 carried modified B4:B5, and only 13 transient Panda rejects occurred at control transitions. Route `000000d4--327b2c4bb8` repeats the one-for-one handoff for 1,249 combined replacements. |

## 2026-09-11 live B4:B5 replacement trial

Route `000000d1--ad906be282`, segments 3–6 and 9–12, is the first retained
Camry drive with active synthetic `0x160` replacement on restored stock
Toyota-B. Both driver attempts occurred in this one ignition route. The branch
at the time incorrectly forced `openpilotLongitudinalControl=True`, so changing
the Alpha Long setting between attempts did not distinguish them; the branch
was subsequently corrected to advertise `alphaLongitudinalAvailable` and honor
the standard toggle on the next `CarParams` initialization.

The software control and transport path did run:

- `CC.longActive` covered about 160 seconds in segments 3–6 and about 178
  seconds in segments 9–12; Panda `controlsAllowed` followed the stock cruise
  latch.
- The planner/controller requested −1.28 to +0.542 m/s².
- 10,259 bus-0 `0x160` replacements were sent. Of these, 10,228 differed from
  the nearest stock camera template only in the Profile-5 CRC and B4:B5; their
  decoded B4:B5 request matched `CC.actuators.accel` to 0.001 m/s² rounding.
- The camera-side bus-2 source remained observable as the live template while
  the competing stock downstream copy was suppressed. Panda recorded 19,197
  bus-0 TX returns and 13 rejected transition-race attempts across the eight
  analyzed segments.

The downstream result did not support the Corolla-to-Camry field transfer. In
two continuous representative active minutes, protected `0x0CA` B7:B8 had
correlation `r=0.596` and `r=0.507` with injected B4:B5, but `r=-0.916` and
`r=-0.890` with the untouched stock signed-7 B12. The moderate B4:B5
correlation is expected because openpilot and Toyota were responding to the
same vehicle-speed error; it is not evidence of synthetic causality. Together
with the driver's direct observation that behavior did not change, this is
strong negative evidence for **B4:B5 alone** as the Camry command. The corrected
test encoder therefore retains the fine B4:B5 request and also changes B12 as
`round(-accel / 0.1)`. The sign and 0.1-unit choice are supported by both the
stock cross-plane regressions and the GTS+ FRC output-acceleration vocabulary;
synthetic causality and any additional companion semantics still require the
next controlled drive.

Supporting bounds: the two retained drives give B12↔protected-`0x0CA`
correlation r = −0.9517/−0.9894 — strong association, explicitly **not** a
command calibration. Plain set-speed state (`0x08A B10`, `0x251 B2`) is
insufficient evidence of a writable cruise command. `0x0FE` is the
SecOC-shaped switch PDU (VAR-127) and cannot be forged without the key story.

## 2026-09-11 combined-request trial with stock DRCC unavailable

Route `000000d4--327b2c4bb8` was captured after the EPS stopped providing its
normal `0x030` traffic. MAIN attempts first produced the already-observed
DRCC-unavailable/rejection state; the later successful latch was conventional
cruise (`0x251` B0=`0x90`), not stock DRCC. This limits the route to a conventional-cruise observation. It does not
distinguish a DRCC-mode permission requirement from an ineffective field
substitution or a parallel/feedback publication.

During two `CC.longActive` windows, openpilot emitted **1,249**
combined B4:B5+B12 `0x160` frames at the camera-counter rate. The Panda relay
continued to expose the live camera-side `0x160` template and made the
replacement the sole downstream copy while longitudinal control was allowed.
No synthetic EPS `0x030`, FRC health response, or broad cruise-status spoof was
present.

At the start of the first control window, the relationship is directly visible:

```text
openpilot requested accel       -0.542  ...  +0.360 m/s²
synthetic 0x160 B12                  +5  ...      -4 counts
protected 0x0CA result          -0.320  ...  +0.397 m/s²
```

Across both windows, synthetic B12 versus the protected result gives
`r=-0.705` at nearest time and `r=-0.730` at +100 ms in the original reduction.
The September-16 counter-matched analysis reproduces comparable host
correlations but shows a substantially stronger intact-native correlation.
The earlier claim that this proves influence is withdrawn; it does not
establish either acceptance or full authority. Over the strong-braking subset,
openpilot requested as much as `-1.2 m/s²`, while the protected result remained
roughly `-0.15..-0.34 m/s²`; requested acceleration correlates only `r=0.276`
with the protected result and `r=0.176` with measured acceleration. Measured
acceleration instead tracks the limited protected result at `r=0.912`. The
driver's direct observation closes the practical consequence: the car did not
perform the modeled stop-sign deceleration.

The explicit normal-CAN mode discriminator is `0x251` B0: retained healthy
DRCC uses `0xA0/0xC0` for available/active, while the dead-EPS route uses
`0x88/0x90` for conventional available/active. Route
`000000d9--a1a459c5b5` closes the proposed `0x251` middleman negatively.

### 2026-09-11 virtual-engagement / `0x251` middleman result

The test branch set `pcmCruise=False`, synthesized an openpilot MAIN state from
the physical buttons, and allowed openpilot/Panda to own engagement without
Toyota's authenticated cruise-operating latch. It also followed stock
`0x251=0xE0` with synthetic `0xA0/0xC0` states.

The host and transport paths worked: `CC.longActive` covered about **47.4 s**,
and **1,861** nonzero downstream `0x160` replacements matched the requested
acceleration over `-1.2..+1.296 m/s²`. Their B4:B5 and B12 correlations with
the controller request were `0.99982` and `0.99905`, respectively, and every
checked source, synthetic, and downstream frame passed the recovered E2E
Profile-5 integrity relation.

The Toyota authority path did not engage. Authenticated `0x08A` remained
inactive for every one of **9,525** driving-window samples. During the 1,861
active nonzero requests, protected `0x0CA` remained within 0.005 m/s² of its
lower arbitration bound in **96.45%** of samples and did not follow the
requested acceleration. Panda accepted 55 synthetic `0x251=0xC0` transmissions
(48 transition/state attempts were rejected), but none changed authenticated
`0x08A`; the FRC's stock `0x251=0xE0` publication continued on the same unsplit
bus. Thus `0x251` is not a sufficient downstream DRCC authority control, and
the virtual branch merely made openpilot believe cruise was engaged.

The virtual MAIN ownership, physical-button Panda permission state, MAIN-time
stock-`0x160` suppression, and `0x251` transmitter were consequently removed.
The integration again requires the genuine `0x08A` operating latch before it
replaces `0x160`.

### 2026-09-11 retained stop/resume audit

The long 2026-09-04 routes contain more longitudinal state than the original WP4
matrix used. A direct rlog reduction of routes `0000003b--62262eb7a1` and
`0000003c--97b9e7a69a` finds seven cruise-enabled stops longer than 0.4 s. Four
short stops, lasting **2.893–4.288 s**, resume with cruise still enabled and
with **no gas, brake, RES+, or SET- input within one second of motion**. Three
longer stops, lasting **6.941–13.079 s**, enter Toyota's delayed stock-ACC hold
state after **5.223–9.254 s** stopped. Those are the already-source-real
`0x08A` `CRUISE_SUBSTATE_2=0x67` episodes (`0x66` during accelerator override).
All three long-hold exits clear on accelerator input before ego motion; none has
a RES+/SET- edge.

The short no-input resumes are especially useful for `0x160`. In three examples
with complete local context:

| route / motion time | stopped B12 baseline | first persistent B12 departure | protected `0x0CA` result > +0.5 m/s² | driver input |
|---|---:|---:|---:|---|
| `3b` / 5122.256 s | −1 | **351 ms before motion** | **463 ms before motion** | none |
| `3c` / 9068.054 s | +1 | **404 ms before motion** | **413 ms before motion** | none |
| `3c` / 9147.517 s | 0 | **433 ms before motion** | **503 ms before motion** | none |

In each case B12 ramps more negative as the protected result rises positive and
the vehicle starts. During the last roughly one second stopped, the primary
`0x160` application template is otherwise stable (`B3=0x82`, `B4:B5=0x8000`,
`B6=0x40`, `B7=0x03`, `B8:B9=0x4DE8`, `B11=0`, `B15=0x80`, `B16=2`; B10
is route/state dependent, and B13/B14 continue their independent dynamic
pattern). This does not turn a stock correlation into a modified-frame receiver
proof, but it materially strengthens B12 as the request-related scalar: the
change precedes physical motion without any driver resume command.

The delayed-hold transition is a separate state boundary. At the exact
`0x08A` B7 `0x47 -> 0x67` edge, two of the three episodes have no `0x160`
application-byte change at all; the third changes only already-dynamic/cyclic
fields. The protected `0x0CA` result is already zero before hold and remains
zero through it, with the other two acceleration-like words settled near
`+3.75` and `+0.665 m/s²`. An all-Bus-4 bit sweep finds no one ordinary CAN bit
that makes a repeatable high-confidence transition at all three hold onsets.
Likewise, the apparent Bus-1 `0x230` candidates are ramps/counters rather than a
discrete hold edge. The captured hold therefore is not presently encoded as a
simple newly identified `0x160` or `0x0CA` flag; it may be downstream/local or
carried in a still-unmapped/request-side field.

That distinction matters to openpilot stop-and-go. Current `LongControl` will
stay in its stopping state while `CarState.cruiseState.standstill` remains true.
The current Camry parser intentionally maps the delayed Toyota hold state to
that standard field. The retained logs prove that ordinary **short-stop
stop-and-go is already compatible with the stock request pipeline**, because
four stops restart automatically before delayed hold. They do **not** yet prove
openpilot can automatically release Toyota's delayed long-stop hold. Current
GTS+ gives the exact semantic leads to close that gap: FRC DID `0x1B07` exposes
Brake-Hold Control Prohibited, Stop Control Permission, and Brake-Usage-Limit
Permission, while PCS request record `5280` additionally carries EPB, accelerator-
override-prohibition, low-priority, shift-range, and braking/driving-force
fields.

The retained normal rlogs do not contain synchronized `0x1B03..0x1B07` /
Brake `0x10A1..0x10A4` reads, nor a PCS/AEB intervention suitable for proving
that PCS wins over a replaced cruise request. Those remain targeted-live
questions. For implementation, the least-destructive candidate is therefore a
1:1 relay replacement of each live FRC `0x160`: preserve the current stock
application/context fields and B2 counter, modify only the request field(s) that
are positively recovered, recompute E2E Profile 5, and leave Toyota's downstream
arbitration/SecOC participants untouched.

## Branch implementation and validation boundary

`controlsd` owns `CC.longActive`/`CC.actuators.accel`; Toyota `CarController`
owns encoding and camera-counter pacing; Panda owns the TX whitelist, normal
longitudinal bounds, and selective forwarding. No second permission state or
legacy Toyota PCM compensation loop remains. Corolla can exercise the
contributor-reported field and handoff. Camry combined-request transport is
observed under conventional cruise; independent host influence and full
requested authority are not established. The exact-Camry branch again derives cruise availability and engagement
from Toyota's source-real state and does not transmit `0x251`.

## Next evidence steps

1. Establish which quantities are requests versus measured/selected-state
   exports, and identify the relevant receiver contract before changing another
   PDU or treating conventional-mode co-movement as acceptance. `0x251` is no longer a candidate
   authority input.
2. Run the existing synchronized FRC/Brake request capture during stock DRCC,
   including a short stop, delayed hold, release, and (if naturally observed)
   PCS intervention: FRC `0x792` `1B03..1B07`, Brake `0x7B0` `10A1..10A4`,
   `0x160`, protected `0x0CA`, and all ordinary state on one clock. This should
   bind the stop/hold permissions and request ID/acceleration to the wire without
   guessing from correlation.
3. Explicitly validate PCS/AEB coexistence before calling the path complete.
   The current logs show the OEM arbitration stack and ordinary stop/resume
   behavior, but they do not contain a PCS event that proves emergency authority
   survives request replacement.

**Exit status:** the historical B12 offline generator remains verified evidence,
and the test branch now implements the Corolla-validated B4:B5 request plus the
gap-free stock-Toyota-B replacement topology. For Camry, B4:B5 is strongly feedback-like in the retained evidence and the
combined B4:B5+B12 trial does not establish independent influence on the
protected plane. The requested stopping response did not occur; its cause
is not selected by this trial. The `0x251` mode-middleman and
virtual engagement path are disproved and removed; delayed-hold release, the
missing request/permission semantics, and PCS/AEB coexistence remain open.
