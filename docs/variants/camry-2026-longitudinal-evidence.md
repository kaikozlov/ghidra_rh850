# 2026 Camry longitudinal request and result evidence

This report owns the wire semantics and capture analysis. The
[capability matrix](camry-2026-capability-matrix.md) owns current port status;
the [port report](camry-2026-tss3-opendbc-port.md) owns implementation.

`0x08A` carries the shared lateral and longitudinal application request.
Brake-owned `0x081` publishes downstream result/status.
`0x160` is FRC-origin state/evidence, not the Camry port's command interface.

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
as an application identifier. This generic Toyota architecture closely matches
the recovered `0x08A/0x081` behavior.

That distinction explains the ID63 observation cleanly. Camry `0x08A`
B6[7:2] carries candidate request IDs 0 and 11 in the two complete drives;
ID63 is observed in Brake/VMC-owned `0x081`. Toyota labels 63 `Driver
Operation` on a P5 FRC diagnostic display surface. **`0x08A` B7 is a
checksum, not a second request ID/allocation byte**; the lower-slot
requester and allocation remain unmapped. The supported model is
FRC-submitted acceleration bounds in `0x08A`, with downstream
arbitration/employed-source feedback in `0x081`.

The retained source document is local-only under
`REFERENCE/patents/toyota_vehicle_movement_arbitration_patent/US20200070849A1.pdf`
(`REFERENCE/` remains intentionally ignored). Public source:
<https://patents.google.com/patent/US20200070849A1/en>.

Transport, request semantics, physical publication/security ownership, and
actuator authority remain separate questions. Later source-direction evidence
places protected `0x08A` publication inside the FRC assembly, while the recovered
Toyota architecture places request arbitration downstream in the Brake/VMM
layer. The exact Brake code implementing that arbitration and the security/physical
handoff remain unresolved; the archive-wide unequal-bound census now strongly resolves
ordinary Camry A/B ordering as upper/lower.

**Request/result wire closure:** FRC normal-Tx suppression establishes `0x08A`
as the upstream TSS request/instruction plane; Brake owns `0x081` and continues
publishing it with request-loss supervision if the FRC request disappears. The
byte-level audit maps `0x08A B8:B9` to the ordinary-DRCC upper bound and
`B11:B12` to the lower bound at signed16 x0.001, and maps `0x081 B6[5:0]` as
the strongest `5284` employed-source-ID candidate. In the
[2026-09-30 VMC status corpus](#2026-09-30-vmc-status-corpus),
`B20:B21` is the closed-accelerator reference. The [stock braking comparison](#message-structure-and-drivebrake-decomposition)
supports `B4:B5` as the combined-result word and `B18:B19` as the drive-side
component. **`B4:B5` is the leading candidate for recorder `57DB`.**
The [braking-ceiling comparison](#repeated-braking-ceiling-and-request-policy-candidate)
narrows the weak-braking behavior; the subsequent
[stock scene comparison](#stock-following-versus-free-cruise-association) makes a
companion request-policy mismatch the leading hypothesis.
`0x0CA` remains protected longitudinal/chassis state but is no longer the primary
result interpretation. See `data/generated/camry_2026_longitudinal_request_plane.json`.

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
stronger interpretation.

### Independent chassis-state and ego-speed cross-check

A second reduction in the maintained motion-audit producer checks both complete
August captures against raw chassis messages. This adds an independent check to
the wheel-speed derivative and current port signal names. Inputs are tracked;
regeneration needs neither `REFERENCE/` nor `build/`.

| Cross-check | Drive A | Drive B |
|---|---:|---:|
| Fine B4:B5 vs native `0x13C` acceleration-like word, all samples: r | 0.979516 | 0.989355 |
| Same comparison, cruise off: r | 0.979857 | 0.988391 |
| Cruise-off median absolute difference (m/s²) | 0.005 | 0.013 |
| Packed speed vs valid raw wheels above 2 m/s: r | 0.999758 | 0.999936 |
| Speed median absolute difference (m/s) | 0.018750 | 0.020139 |
| Moving speed samples | 8,930 | 14,413 |

The packed speed candidate spans B7:B9. Its observed numerical encoding is
compatible with the existing Toyota wheel-speed representation. Invalid wheel
flags are rejected. The acceleration comparison uses the preceding chassis sample
within 100 ms; speed uses the preceding wheel sample within 80 ms. Neither
joins across original source files or consumes a future sample at the queried
instant. The `0x13C` word remains described structurally; the independently
derived physical acceleration and stock-start evidence are what anchor its
measured-motion interpretation.

This substantially strengthens the **ego-state publication** interpretation
of the PDU. Our DBC name `TSS3_LONGITUDINAL_REQUEST` is a project-assigned hypothesis.

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
1.619–2.733 ms (median 1.879 ms). Each match is local and time-bounded, so the
8-bit wrapping counter is disambiguated. All 1,249 have a byte-identical returned
Panda TX within 3.892–21.305 ms.

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
The result artifact contains the complete neighborhoods, including threshold-crossing
timestamps.

The three stock segments also directly separate native traffic from Panda
returns: `0x0CA` has **7,641 native bus0 frames and 7,641 returned bus2 TXs
(src=130)**, with no native bus2 copy. It is a chassis-to-camera publication on
the temporary repin. In these same captures `0x160` is native on bus1. On the restored stock harness, the
camera link is the split bus2→bus0 pair and `0x0CA` is on unsplit bus1.
Toyota network numbers and Panda indices must not be mixed across harnesses.
The exact chassis ECU that publishes `0x0CA` remains unassigned here.

### What GTS and the source inventory do—and do not—establish

Direct reads of the retained `FRC_P5.ddb` expose both estimated motion and
request/output vocabulary. DID `0x1253` names **Estimate Vehicle Acceleration**.
DID `0x1B08` contains **Driver Acceleration for Output**, **Acceleration Limit
for Output**, and **Acceleration for Output**.

The previously proposed `0x1B03..0x1B07` join is specifically an **ISA**
upper-limit/permission surface. Brake `0x10A1..0x10A4` and the TSS operation-FFD
request and arbitration records provide additional semantic candidates.

The September-1 source-isolation notebook supports FRC normal-Tx ownership of
`0x160`. In the two August captures, the `0x0C9` member of the same recorded source
group has only one changing application word, B12:B13, with zero header/counter/trailer.

**Implementation consequence:** keep the Camry alpha encoder explicitly
unqualified and retain the intact native comparator in future analyses.
The available data supports exported/feedback-like quantities more strongly than
it supports the claimed direct control path.

Reproduce without `REFERENCE/`, `build/`, original September rlogs, or a car:

```bash
uv run --locked python -m tools.targets.camry.analysis.analyze_camry_20260916_longitudinal_motion_audit
tools/test camry_20260916_longitudinal_motion_audit
```

The optional `--extract-fixture` path rereads the seven external originals using
an existing openpilot Python environment; it does not call vehicle tooling.


### Independent original-source recheck and the meaning of "echo"

The follow-up review reread the **28 original rlogs** selected by the expanded
local role analysis: September-11 `d1` segments 3–6 and 9–12, `d4` segments 0–6,
historical relay-direction route `2d` segments 0–5, September-4 `3b` segments
83–85, and `3c` segments 25–28. The last two groups retain the declared
four-second neighborhoods around the three stock-resume landmarks.

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
(r=0.999789/0.999942).

The disposition distinguishes three findings:

- **FRC-origin publication:** supported by source isolation and camera-side observations.
- **Fine acceleration field:** motion/feedback-like on the captured Camry.
- **B12:** related to a native longitudinal result that can precede physical
  motion. Its best native alignment follows `0x0CA`, and the untouched native
  comparator outperforms the replacement during the combined trial. This
  favors an exported state/result interpretation.

The leading working model is an FRC publication of ego-motion and
longitudinal-state information onto the ADAS link, potentially for other
perception participants.

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
leading architectural interpretation. The correlated `0x0CA` channel travels from
the chassis side toward the camera on the historical split.

### Independent ego-state comparisons

With no additional unit fit, the fine field agrees with the acceleration-like
quantity in chassis `0x13C`: all-sample correlations **0.979516 / 0.989355**, with
median absolute differences **0.006 / 0.014 m/s²** in August A/B.

A separate packed speed-like field in `0x160` follows mean wheel speed with
correlations **0.999789 / 0.999942** and median absolute differences about
**0.019 / 0.020 m/s**, above the declared low-speed cut. The selected packet
therefore contains ego-state information. Invalid wheel flags are excluded.

In the restored-harness d1/d4 captures, with cruise disengaged and speed above
2 m/s, the fine field also agrees with the independently wheel-derived
`carState.aEgo`: **r=0.970690 / 0.957737**, using **6,096 / 6,503** samples.

### B12 timing is consistent with a report, but is not a causal clock

The complete native sweeps align B12 best with `0x0CA` **50 / 75 ms earlier**.
However, the level-correlation gain over zero lag is only
**0.000258 / 0.000472**; correlations of 200-ms changes peak at just
**0.185 / 0.455**. The peaks are broad, the series autocorrelated, and rlog
publication timestamps are shared by a CAN batch.

The actual start neighborhoods are more useful. Relative to the first three
consecutive raw-wheel samples above 0.025 m/s:

| Stock resume | `0x0CA` result-like field persistently >0.5 m/s² | Fine field persistently >0.05 m/s² |
|---|---:|---:|
| 3b / 5122.256 s neighborhood | −441 ms | +272 ms |
| 3c / 9068.054 s neighborhood | −372 ms | +263 ms |
| 3c / 9147.517 s neighborhood | −482 ms | +262 ms |

These definitions use a different threshold from the 0.1 m/s onset /
first-nonzero-field table above. No gas, brake, RES, SET, or CANCEL
assertion is present in the declared −1.0 to +0.5 s windows. At the −500-ms
landmarks, `0x0CA` is already positive while B12 is still at its preceding
baseline.

### Actual replacements and the native comparator

The expanded d1 selection contains **10,259** host frames, **10,228** changed
fine fields, and no B12 modifications. The d4 selection contains **1,249** host
frames, **1,243** changed fine fields, and **970** changed B12 fields. Every host
frame has a source/time/counter-matched native template and valid CRC; d4 has
**1,249/1,249** exact returned TX payloads. All changed bytes are confined to the
historical encoder's declared fields and CRC.

At a common 25-ms grid during d4 replacement, native B12 versus the `0x0CA`
result-like channel has **r=0.931904**, while replacement B12 has **r=0.699657**
(**1,244** observations). All 1,244 have a preceding conventional-active `0x90`
mode observation within 1.5 s. The age bound reflects the slow mode message;
unknown-mode observations remain explicitly counted instead of silently labeled.

The host and stock controllers share a moving scene, and the camera continues
to observe the car while its ADAS-side output is being replaced. Either closed
loop can correlate with the same motion. The better intact-source fit defeats
the previous correlation-only proof of host authority.

### Source ownership, vocabulary, and remaining information boundary

The September-1 notebook §19 records `0x160` **40 → 0 → 40** under FRC normal-Tx
suppression/restoration on the observed ADAS network. This supports the FRC
publication source. The full six-segment
historical relay capture has `0x0CA` **13,756 native bus-0 RXs** and **13,256
returned bus-2 TXs**, versus only 503 startup/native bus-2 observations. FRC-side
`0x08A` has the opposite dominant direction. On the restored stock harness,
`0x160` is the camera-side ADAS source and `0x0CA` remains on the unsplit chassis
network. Panda bus indices are not Toyota network numbers.

Direct GTS DDB queries reproduce `FRC_P5` DID `0x1253` (estimated acceleration)
and `0x1B08` (separate driver, limit and output accelerations). `0x1B03..0x1B07`
are ISA-specific request/permission observables. Brake `0x10A1..0x10A4` name TSS
requests. The current checked-in firmware inventory contains EPS applications.
The candidate re-rank below identifies a protected chassis-facing request carrier.

### Longitudinal candidate re-rank after topology normalization

The earlier search mixed three harness eras too easily. Raw Panda bus numbers are
therefore normalized to Toyota network role before any candidate is compared:

| Capture era | Panda CAN0/CAN2 relay pair | Panda bus 1 | Longitudinal interpretation |
|---|---|---|---|
| Stock Toyota-B before the temporary repin | Toyota Bus 1 camera/ADAS: source side bus2 -> downstream bus0 | Toyota Bus 4 Brake/EPS/chassis, unsplit | Same physical wiring as the restored configuration below; direct-Panda ELM327 mux state is a separate axis |
| Temporary CAN0/CAN1 repin (Aug-27 through lateral development) | **Toyota Bus 4**: upstream `0x08A/0x0C9` on bus2 -> chassis bus0; `0x0CA` returns bus0 -> bus2 | **Toyota Bus 1** camera/radar/FRC P05 family | Healthy Sep-4 DRCC routes `3b/3c` are in this era |
| Stock Toyota-B restored in the Sep-11 integration cleanup | **Toyota Bus 1** camera/ADAS: FRC `0x020/0x160/0x230/0x440` source bus2 -> downstream bus0 | **Toyota Bus 4** request/result/chassis family `0x08A/0x0C9/0x0CA`, unsplit | September restored-harness captures |

The [runtime contract](../architecture/toyota-tss3-minimal-runtime.md) owns
maintained topology. The table above identifies the capture configurations.

`harnessStatus=flipped` describes harness/cable orientation. Physical CAN0/CAN1
repinning is a separate configuration. Panda sources 128/130 identify returned
host-TX echoes. The regenerated stock-topology artifact checks all
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

Current P5 Brake/Booster/EPB dictionaries expose `0x10A1` **Request
Acceleration of Upper Limit from Toyota Safety Sense** and `0x10A2`
**...Lower Limit...**, both signed16 at 0.001 m/s², plus 6-bit upper/lower
request IDs (`0x10A3/0x10A4`) occupying bits7:2 of their diagnostic fields.
Those offsets are not CAN offsets. `0x08A B6[7:2]` remains a request-ID
candidate, with B6[1:0] an allocation candidate; active Camry cruise uses
ID11/allocation1. **B7 equals `(0x8A + 8 + sum(B0..B6)) & 0xFF`**,
the eight-byte-prefix Toyota checksum. Its old lower-ID/allocation mapping
is withdrawn.
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
ordinary Camry DRCC raw header state `B6=0x2D`, `B7=0x47`, spread across six
independent route segments as two-frame episodes. Their `(B8:B9, B11:B12)` values in
m/s² are `(+0.682,-0.769)`, `(+0.687,-0.437)`, `(+0.217,-0.442)`,
`(+0.432,-0.659)`, `(+0.215,-0.452)`, and `(-0.621,-0.701)`: **A > B in 12/12
ordinary-DRCC unequal frames**. The first five episodes occur immediately before
B6 drops to zero; the sixth occurs on an idle-to-active transition. This supports
ordinary DRCC **B8:B9 as the upper acceleration bound and B11:B12 as the lower**.
The checksum supplies no lower-bound requester identity.

The other 36 unequal frames carry ID13 (`B6=0x35`, `B5=0x04`): the first
slot sweeps −0.175 to −0.500 m/s² and the second stays zero. The
[warning and chassis comparison](#two-rare-longitudinal-applications)
separates this application from ordinary DRCC.

The alternatives now rank as follows:

1. **Protected `0x08A` B8:B9/B11:B12** — strongest direct downstream TSS
   acceleration-request candidate.
2. **Protected `0x5AF` B26** — a coarse longitudinal companion. Interpreting B26 as signed 6-bit gives
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
acceleration carrier**. The retained CommunicationControl experiment establishes
`0x08A` as the upstream TSS request-side plane.

The maintained port intercepts the request source on the repinned relay
topology; see the [runtime contract](../architecture/toyota-tss3-minimal-runtime.md).

`0x08A` is the central observed continuous request PDU and already carries the full
recovered lateral request family plus the strongest longitudinal acceleration
request candidates. Toyota's FRC-hosted recorder also exposes upper/lower
longitudinal request IDs, braking/driving-force allocation, shift/EPB,
override/priority and other request metadata whose exact wire locations are not
all mapped. Ordinary FRC state/display/ego-motion publications (`0x020`,
`0x160`, `0x230`, `0x440`, `0x371`, `0x412`, etc.) also exist outside `0x08A`.


### Request/result recorder layout: what is actually mapped

Toyota's architecture changes the meaning of the longitudinal pair. The lower and
upper packages are independently arbitrated **bounds** on allowed acceleration.
The downstream powertrain compares driver demand
with those bounds and clips it into the selected range; the longitudinal result ID then
reports the request source whose acceleration was actually employed. This explains why
result ID63 (`Driver Operation`) can appear while the observed `0x08A` B6
request-ID candidate is not 63; the lower requester field is not mapped. Equality of the two retained acceleration words means the observed bounds collapse
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
| `5280` lower longitudinal request ID | unmapped | former B7[7:2] mapping withdrawn: B7 is a checksum |
| `5280` lower acceleration | `0x08A B11:B12`, s16 x0.001 m/s² | strongly resolved for ordinary Camry DRCC |
| `5280` force distribution | unmapped | former B7[1:0] mapping withdrawn |
| `5280` shift / EPB / override / priority | unresolved | complete-drive byte census does not justify an OEM-name assignment |
| `5281` upper longitudinal request ID | `0x08A B6[7:2]` candidate | B6 agrees with selected result ID11; synchronized diagnostic join remains open |
| `5281` upper acceleration | `0x08A B8:B9`, s16 x0.001 m/s² | strongly resolved for ordinary Camry DRCC |
| `5281` upper force distribution | `B6[1:0]` | strong structural join; synchronized DID oracle still absent |
| `5282` lateral request ID | `0x08A B21[5:0]` | recovered |
| `5282` requested pinion angle | `0x08A B18:B19` | recovered; controller scale is 0.00100012 rad/count versus recorder 0.001 |
| `5282` steering assist gain | `0x08A B24` x0.01 | strong structural join |
| `5282` damping gain | `0x08A B25` x0.01 candidate | All nonzero observations coincided with [native lane-departure warnings](#every-bit-of-native-0x08a). |
| `5284` arbitration-result longitudinal ID | `0x081 B6[5:0]` | strong candidate; observed values 11 and 63 |
| `5285` arbitration-result lateral ID | `0x081 B13[5:0]` | recovered |
| `57D3` acceleration-valid flag | unresolved | `0x081 B11[4]` is proven request-loss supervision, but is not OEM-joined to `57D3` |
| `57DB` arbitration-result acceleration | `0x081 B4:B5` leading candidate | [Independent wheel deceleration](#message-structure-and-drivebrake-decomposition) favors this word over the drive-side `B18:B19`. |
| `57DE` arbitration-result pinion angle | `0x081 B16:B17` | recovered |

The B6 candidate has an independent arbitration check. Selected `0x081`
result ID11 equals `0x08A B6[7:2]` in **1,525/1,529** Drive-A and
**3,276/3,281** Drive-B ID11 samples. Every selected ID63 sample
(**15,544 / 16,718**) differs from the B6 candidate. Toyota's P5 FRC
diagnostic vocabulary includes `63 = Driver Operation`, consistent with
the patent's distinct result-side driver discriminator.

The delayed-stop corpus retains **198** frames with B4[5] set while the
B3[3] cruise latch is set, across three hold episodes in routes `3b/3c`.
Ordinary raw B6/B7 pairs `0x2D/0x47` and `0x2C/0x46` become
`0x2D/0x67` and `0x2C/0x66` when B4[5] adds `0x20` to the checksum.
These are not two requester identities or independent hold corroboration.
The hold analysis now selects B4[5] directly; its exact OEM recorder name
remains unassigned.

### Longitudinal request IDs versus result-source IDs

Keep FRC request metadata and Brake/VMC result IDs distinct. `0x08A` B6
contains the observed request-ID candidate; the lower requester remains
unmapped. `0x081` carries the downstream **employed-source result ID**,
which can identify the driver.
The current Toyota corpus
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
| **9** | P6 Speed Limiter Requesting Vertical ID explicitly names `ISA` | no generation-20 lateral label | named cross-generation longitudinal/vertical anchor; not observed on Camry `0x08A` |
| **11** | Camry request A during ordinary DRCC; `0x081` result ID11 when that application request is employed | LTA/LCA | **strong shared-TSS-application-ID hypothesis** |
| **13** | brief deceleration request following late driver-nonresponse warnings on two Camry routes | — | likely emergency driving stop assistance; [episode evidence](#two-rare-longitudinal-applications) |
| **17** | Camry cruise-independent deceleration, also observed in the retained Corolla | — | PDA deceleration assist is the leading Camry hypothesis; [matched-scene comparison](#two-rare-longitudinal-applications) |
| **18** | not observed in Camry B6 in the two complete drives | SDG; P6 PDA-SA lateral request also uses 18 | lateral-only named anchor; no longitudinal transfer |
| **41** | P6 MaaS lower-limit longitudinal ID = `Request 1 of MaaS Autonomous Driving System` | AD (Lv.4) | plausible shared automated-driving application identity |
| **45** | P6 MaaS lower-limit longitudinal ID = `Request 2 of MaaS Autonomous Driving System` | DES (Lv.4) | plausible shared automated-driving application identity |

**Result-side-only observation:** longitudinal ID63 is OEM-labeled `Driver Operation`
on a P5 FRC diagnostic display surface and is observed in Brake/VMC-owned `0x081`.
It is absent from the B6 candidate in the retained Camry and Corolla evidence.
The checksum cannot establish presence or absence of another requester.

With the checksum removed from the selection predicate, every stable raw
**B6=0** request pairs with Brake/VMC longitudinal result ID63:
**18,645/18,645** Drive-A and **19,441/19,441** Drive-B. Above 1 m/s,
the counts are **7,713/7,713** and **10,563/10,563**. Drive A gains 37
stable pairs that the old checksum-derived filter excluded.

B11:B12 remains dynamic during B6=0. With accelerator=0, gear D, and
matched brake-pedal press edges below 1 m/s, all **9/9** events reduce the
slot: Drive-A 4/4 (median −0.0295 m/s²), Drive-B 5/5 (median −0.036 m/s²).
Combined changes span −0.071 to −0.0265 m/s². With the brake released,
Drive-B medians fall from +0.468 m/s² below 0.15 m/s to +0.277 at
0.15–0.5 m/s and +0.202 at 0.5–1.0 m/s. These are acceleration-slot
observations; the former “ID4 application” was a checksum decoding error.

Toyota's patent record supplies a possible physical interpretation.
`US20200070849A1` defines the lower longitudinal package as the
**minimum acceleration requested by an application**, separately reports the powertrain's
**full-closed estimated ground acceleration**, and has the powertrain compare driver
demand against the selected application bounds. Toyota's closely contemporary
`US20200094835A1 / US11285952B2` then describes the physical powertrain **lower limit
of availability** as the fully-closed/throttle-off baseline: it can be negative from
engine braking at speed, but below roughly 8--10 km/h creep torque becomes dominant and
drives that lower limit positive. Older Toyota `JP5195257B2` independently describes
accelerator-off creep torque and creep-cut control under brake demand.

This resembles a **closed-accelerator/manual baseline envelope**: positive
creep at low speed, coast/regen/engine-braking values at higher speed, and
a reduction with brake input. The available evidence does not identify
which application contributes that slot.

Toyota defines both longitudinal and lateral request IDs as application
identifiers. Camry B6 ID11 during ordinary DRCC and lateral ID11 LTA/LCA
remain a possible shared-application clue. The former checksum-derived
ID25 hold attribution supplies no evidence about that namespace.

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

The tracked Corolla reducer observes B6 IDs 0 and 17; `0x081` reports
ID63 across all 2,000 retained result frames. The [independent Corolla
onsets](#two-rare-longitudinal-applications) place ID17 outside cruise.

Across 17,073 / 19,999 request-result pairs in the A/B drives, closed-accelerator
reference `0x081 B20:B21` correlates with the request at r=0.941674 / 0.836884.
The median reference-minus-request delta is 0.000 m/s² in both drives for
result ID63 and −0.181 / −0.435 m/s² for ID11. This is consistent with the
[inactive camera using the earlier chassis reference](#where-the-inactive-acceleration-values-come-from).

`0x08A` is the observed continuous TSS3 request envelope for the recovered
lateral tuple and longitudinal acceleration slots. B6 metadata remains a
candidate; lower requester/allocation, shift/EPB/override/priority and
validity fields remain unmapped. `0x081` is the Brake-owned
selected/employed-result/reference envelope. Physical publication
ownership alone does not locate every internal selection step.

The reproducible reduction is
`data/generated/camry_2026_longitudinal_request_candidates.json`, generated by
`tools/targets/camry/analysis/analyze_camry_2026_longitudinal_request_candidates.py`
and protected by `tools/test camry_2026_longitudinal_request_candidates`.

Reproduce the portable reductions:

```bash
uv run --locked python -m tools.targets.camry.analysis.analyze_camry_2026_longitudinal_role
tools/test camry_2026_longitudinal_role camry_20260916_longitudinal_motion_audit
```

This review changes only passive evidence tooling and documentation. No ECU,
Panda, authentication, vehicle-control, or firmware operation is performed.
The local research bundle under `REFERENCE/camry_2026_0x160_role_audit/` and
all re-extraction workspace files under `build/` remain ignored/untracked.

## 2026-09-30 VMC status corpus

Across 1,232,664 native Brake status frames, `B20:B21` behaves as the
closed-accelerator reference. The [braking comparison](#message-structure-and-drivebrake-decomposition)
separates the inferred combined `B4:B5` result from the drive-side `B18:B19`
component. `B4/B18/B20/B22/B24` are signed16BE words at nominal
0.001 m/s²/count. `B26:B27` has a separate signed low-13-bit driver-brake
quantity with an unresolved scale.

### Scope and source artifacts

| Population | Routes | Segments | `0x081` status frames | Moving rows | Covered time |
|---|---:|---:|---:|---:|---:|
| Primary openpilot-longitudinal drives `86/87/88/8a` | 4 | 50 | 96,593 | 56,524 | 2,898.1 s |
| Historical stock (`openpilotLongitudinalControl=false`) | 21 | 353 | 689,752 | 494,875 | 20,692.3 s |
| Historical openpilot | 19 | 229 | 446,168 | 289,169 | 13,386.1 s |
| All status (union of the above plus two tiny no-mode clips) | 46 | 634 | 1,232,664 | 840,645 | 36,981.0 s |

Route `00000089--0dd1afd752` is primary-flagged but never reaches an openpilot
longitudinal phase; it and `00000042--169d4d611d` are one-segment no-mode clips
(74/77 status frames) counted only in the all-status totals. No vehicle
operations are involved: every source is an existing recorded rlog under an
external logs root.

Raw logs remain external. The committed compact evidence lives in
`data/generated/camry_20260930_vmc_status/`: `input_manifest.json` (per-route/
segment paths relative to the external logs root, sizes, SHA-256, software
metadata, and extraction/join cache identities), `summary.json`,
`corpus_validation.json` (per-route/per-phase recomputation),
`phase_comparison.csv` (route × git-phase aggregates),
`stock_epochs.csv` (the 126 window table), `b18_exceptions.csv` (every
non-exact `B18=max(B4,B24)` row with pedal context),
`representative_samples.json`, and the two plots below. Per-route software
provenance is committed alongside: available `initData` records identify
openpilot `0.11.2`, branches `kai`/`tss3`/`tss3-camry-port`, and per-route
git commits; available `TOYOTA_CAMRY_TSS3` CarParams retain
`openpilotLongitudinalControl`. Extraction/join intermediates are git-ignored
under `build/cache/camry_20260930_vmc_corpus/` and are regenerated on demand;
`--corpus-dir` explicitly accepts an existing extraction directory.

### Method, timing, and origin bounds

The pipeline is extract → join → analyze → plot (commands in
[WORKFLOW.md](../WORKFLOW.md#external-openpilot-rlog-reducers)). The join is
**preceding-only** with request windows of 75 ms and
carState/carControl/carOutput/wheel/pedal windows of 60 ms (plan/selfdriveState
120 ms); every snapshot carries per-source ages. Samples have bounded freshness.
They retain distinct acquisition times and exclude interpolation across gaps.
Covered time sums adjacent status intervals, capping each contribution at
100 ms. It includes parked time and bounds each recording-gap contribution.
`t_route` is seconds from the minimum recorded monotonic
timestamp; cached segment metadata timestamps may repeat and are not playback
anchors. All times are logger/event timestamps and must not be read as
physical wire timing or ECU execution/acceptance deadlines.

Each delivered `0x08A` request is classified by exact 32-byte payload match
against host sendcan versus native CAN traffic (plot legend `10=comma`,
`20=native`). Vehicle-side Tx confirmations establish observed publication.
`ID11` also appears on native stock traffic, so it is **not a comma-ownership
marker**.

The native zero-request-metadata comparison now selects fresh **raw B6=0**,
without conditioning on the checksum. It contains **719,312 rows**, 115
more than the former checksum-derived filter. The 1,232,664-status-frame
scope, 126 stock epochs, and four plotted moving-drive fits are unchanged.

### Six acceleration-like words: candidate roles

| Word | Candidate role | Dominant evidence and bounds |
|---|---|---|
| `B4:B5` | inferred combined longitudinal control/force-equivalent quantity; normally request-following | in every one of 126 excited no-pedal moving stock windows the direct `B4−request` RMS beats the direct `B4−wheel CarState` RMS (medians 0.00921 vs 0.09756 m/s²); `B4−B18` follows the separate driver-brake word during manual braking; −2.458 at held-brake standstill |
| `B18:B19` | inferred drive-side result/reference; empirically `max(B4,B24)` | exact in 1,232,419/1,232,664 frames; `B22 ≥ B18` in all frames; distinct from the combined quantity during braking |
| `B20:B21` | **closed-accelerator reference** | equals `B24` in 1,005,245/1,010,206 fresh closed-pedal frames (~99.5%); [precedes the inactive camera acceleration slots](#where-the-inactive-acceleration-values-come-from) |
| `B22:B23` | upper/open-accelerator envelope | `B22 ≥ B18` with zero violations in 1,232,664 frames; `B24` itself exceeds `B22` in 11 frames; exact quantity and speed/gear/grade dependence unresolved |
| `B24:B25` | driver-accelerator demand/reference | rises from `B20` toward `B22` with physical accelerator fraction |
| `B26:B27` low 13 bits | driver-brake-linked signed quantity | nonzero on 121,174/121,175 brake-on frames and negative whenever nonzero (135,686/135,686); remains zero in the route-86 automatic-braking example; physical scale unresolved |

Separately, `B6[7]` — the high bit above the six-bit result ID — is
**standstill-associated in this corpus**: it is set in 363,989 of 370,244
known `CarState.standstill=true` samples and zero known non-standstill
samples or raw-wheel moving rows above 0.5 m/s. Missing CarState samples
are excluded from the CarState denominators.

### Empirical envelope and its exceptions

Raw-count equality `B18 = max(B4, B24)` holds exactly in **1,232,419/1,232,664**
all-status frames (primary drives 96,591/96,593 exact with both remaining
frames within 5 counts; 1,232,427 within ±5 corpus-wide). The 245 remaining
rows split **234 above / 11 below** and are each listed with raw packet and
pedal/gas/brake transition context in `b18_exceptions.csv`. The 11 below
cases are exactly the frames where `B24` exceeds `B22` (routes `3f` and
`16a`, excesses of 5–139 counts). Including that ceiling gives
`B18 = min(max(B4, B24), B22)` exactly in **1,232,430/1,232,664** frames,
with **no below-envelope violations**. The remaining 234 above-envelope
rows are concentrated around braking and stop/launch transitions.

### Independent stock direct-difference comparison

An earlier draft of this comparison reported fitted-gain RMSE figures with
milli-g wording; that wording was **incorrect and is withdrawn**. The maintained
result uses direct differences with **no fitted gain or offset**: in the 126
existing excited no-pedal moving stock windows, comparing fresh vehicle-side
TX/request against `B4` and `B4` against wheel-derived `CarState.aEgo`, all
**126/126** windows have `RMS(B4−request) < RMS(B4−wheel CarState)`, with
medians **0.00921 vs 0.09756 m/s²** (≈0.009 vs 0.098). `B4` tracks the
delivered request far better than measured motion in this population. This
supports a control quantity rather than a literal body sensor; request-following
alone does not choose the OEM result name or distinguish drive-only from combined
braking/driving semantics.

The excitation selector uses an 11-sample centered median of wheel speed
and differentiates only **unique logger-time knots**. Different status
payloads sharing a batch timestamp remain in every status count; only the
derivative's time axis is deduplicated. This avoids zero-time division without
discarding status evidence or treating the selection filter as a latency oracle.

### Representative status states

Values are 0.001 m/s² counts converted to m/s²; ages are logger timestamps.

| Case | Route / segment / t_route | Delivered request (origin) | `B4` | `B18` | `B20` | `B22` | `B24` | Reading |
|---|---|---|---:|---:|---:|---:|---:|---|
| stock braking ramp start | `3f` seg21 t=1318.83 | −0.436 (native) | −0.303 | −0.303 | −0.314 | 3.113 | −0.314 | early request/result transient; wheel aEgo −0.084, result ID11 |
| **weak OP braking before pedal** | `86` seg4 t=253.876497 | −2.123 (comma) | −1.423 | −0.466 | −0.466 | 4.216 | −0.466 | no pedals, requestLoss 0, aEgo −1.453; `B4` under-follows while the envelope words hold the closed-pedal reference; see below |
| driver brake after disengagement | `86` seg4 t=254.028 | −4.0 (native, post-intervention) | −2.249 | −0.442 | −0.442 | 4.249 | −0.442 | brake on, `B26`=8097 raw (−95 as signed13); native request-loss supervision set |
| driver accelerator | `86` seg4 t=259.792 | −0.049 (native, inactive) | 1.649 | 1.649 | −0.082 | 5.760 | 1.649 | gas 0.25; `B24` leaves `B20` toward `B22`; result ID63 |
| normal OP acceleration | `86` seg4 t=272.840 | 0.642 (comma) | 0.636 | 0.636 | −0.461 | 2.960 | −0.461 | native FRC upper was 0.171; `B4` follows the delivered request, result ID11 |
| stationary with brake held | `87` seg0 t=9.973 | 0.666 (native, inactive) | −2.458 | 0.666 | 0.666 | 0.849 | 0.666 | aEgo 0; `B4` is not literal motion at standstill; result ID63 |

For the weak-braking case the full native-shaped status packet is
`00000018fa710b1700000004000b0000003ffe2efe2e1078fe2e0000a47702d5`
(`B4:B5=0xfa71`=−1423, `B18:B19`/`B20:B21`/`B24:B25`=`0xfe2e`=−466,
`B22:B23`=`0x1078`=4216, `B26:B27`=0). The native FRC was already
publishing an upper request of −4.0 **before** driver intervention, while
the vehicle-side publication remained the host's −2.123. Native forwarding
resumed only after the brake press. Driver braking therefore confounds the
subsequent deep deceleration and prevents attributing it to native execution alone.
The [repeated braking-ceiling comparison](#repeated-braking-ceiling-and-request-policy-candidate)
below explains the numerical shape of this gap; its exact policy cause remains open.

![Route-86 weak-braking incident and subsequent restart: request, status words, result ID, and pedals](../../data/generated/camry_20260930_vmc_status/incident_and_restart.png)

![Four current drives: B18=max(B4,B24), inactive request words vs B20, B4 vs wheel aEgo, and (B24−B20)/(B22−B20) versus accelerator fraction](../../data/generated/camry_20260930_vmc_status/cross_state_relationships.png)

## Every bit of native `0x08A`

The [bit census](../../data/generated/camry_2026_08a_bit_census/bits.csv)
covers **3,214,376 native camera frames** across 75 routes and 1,369
segments: 133 bits varied, 93 stayed zero and 30 stayed one. It indexes
each bit by field and evidence and counts changes over 3,213,007
within-segment pairs. Of 98 application bits, 87 varied. The other 158
positions comprise 46 checksum, sequence and trailer bits; two fixed
`0x7FFF` words; and 80 unassigned zeros. The same fixed positions held
in [119,173 Crown frames and three Corolla samples](../../data/generated/camry_2026_08a_bit_census/cross_variant_fixed_slots.csv)
(2,400, 596 and 2,355 frames). A separate [Camry holdout](../../data/generated/camry_2026_08a_bit_census/auxiliary_capture_check.csv)
replicated the observed tuples and fixed application bits in 55,735 frames
on `08`/`2d` and 238 on `2e` (calibration unavailable on `2e`).

The [61 observed application-state tuples](../../data/generated/camry_2026_08a_bit_census/application_states.csv)
give counts and logger timestamps. They contain eight combinations of
cruise operation, longitudinal ID, allocation and policy, and 13
combinations of lateral ID, effort and the two gains. B5[2] is set exactly
for IDs 13/17, B6[1] for ID17, B20[6] for ID11 and B22[4] for a nonzero
longitudinal ID. Older routes supply eight varying positions absent from
the 634-segment corpus: B6[1,6], B7[1], B21[4] and B24[0,1,3,4]. The three
November 16–17 drives supply 522,244 native frames; their 220 companion
qlogs cover the same driving time.

**B4[7] follows cruise-display startup.** All 338 lows occurred in the first
33–35 camera publications of ten recordings. It rose 0.821–0.884 s after the
first request and 8.8–19.7 ms after the `0x251` display left its initial
state. The preceding `0x251 B0[7]` agreed in 3,186,516/3,186,516 same-side
pairs within 1.125 s, including 147 lows. On `48` the marker rose 682 ms
before hybrid READY; in the [stationary READY capture](../../targets/camry-2026/raw-20260826/camry_ready_gear_20260826.json.gz)
it was high on all 2,475 requests, including before `0x51E` indicated READY
at 5.213 s.

The stock longitudinal comparisons use 606 original segments on 24 routes.

| Position | Interpretation | Discriminating observation |
|---|---|---|
| B3[3] | Cruise operating in adaptive or conventional mode | `0x251` and `0x27C` agreed in 103,580/103,590 held-out 10 Hz comparisons on 19 routes, including 68,524 available-but-inactive observations. |
| B4[5] | Camera-side delayed hold | `0x251` hold rose at the same time or ≤11 ms earlier at seven of eight onsets. Wheels were stopped on 366/458 highs. On host-longitudinal `171`, all 64 highs in segment 7 occurred while rolling (0.37–1.14 m/s); the display stayed clear during a 12-frame pulse in segment 4. |
| B22[4] | Longitudinal application present | Exactly followed nonzero B6 application ID. On older routes `27` and `3b` it was set on 2,616 cruise-clear frames. |
| B22[5] | Delayed longitudinal release | In [365 cruise exits](../../data/generated/camry_2026_08a_bit_census/cruise_exits.csv) the display was inactive by the last still-active request in 31/31 marked versus 2/332 resolvable unmarked exits (two ambiguous). Held out: 14/14 versus 0/113. All 30 moving marked exits retained chassis result ID11 until request release. Brake, CANCEL and MAIN each occurred with and without the marker. |
| B22[2] | [Near frontal target judged relevant at rest (inferred)](#what-triggers-b222) | Target crossings and matched replay pairs separate selection from proximity. |
| B6[0] in ID11 | Allocation changes with accelerator override | Override-associated allocation on 1,764/1,790 pedal-open and 0/24,027 pedal-closed anchors in stable cruise with brake released. Brake selected ID63 on 1,762/1,764 overrides. |
| B8:B9 and B11:B12 | Acceleration requests | Equal on 3,214,154/3,214,376 frames. In [20 unequal runs](../../data/generated/camry_2026_08a_bit_census/slot_divergences.csv), the first slot was higher on all 42 ID11 frames (32 marked for delayed release) and lower on all 180 ID13 frames. At 1,094/2,183 held-out moving accelerator-open anchors, wheels accelerated above +0.1 m/s² while the request was below −0.3 m/s². |
| B10 | Active internal cruise setpoint in km/h | [Cruise-entry and adjustment evidence](#how-b10-gets-its-value) distinguishes current-speed capture, restore and step changes. |
| B20[7:6] | Cruise policy | [Native display and radar comparison](#native-radar-separates-policy-display-state-and-headway) distinguishes policy from target detection. |
| B18:B19 in lateral ID0 | Angle reference follows earlier EPS feedback | A 35 ms lag fitted on `3b` improved agreement on all four holdouts. On `13e`, exact matches during steering movement rose from 666 to 4,427 of 8,066; 495 still differed by ≥1°. |
| B21[5:0] | Native lateral application | Native ID11 changed to ID0 21–83 ms after 45/45 held-out turn-indicator onsets with cruise and host lateral operating. During two native ID4 episodes on `13e`, the chassis selected host ID11 on all 98 fresh pairs. |
| B23[5] | Application-specific steering effort | [Torque timing differs in ID4 and ID11](#b235-steering-effort-depends-on-the-lateral-application). ID0 was always low; all 52,557 ID18 frames were high. |
| B24 | Retained lateral assist gain | ID4/11 used 100, ID18 used 25 or 50, and gain persisted into ID0 and park. The sole direct 50→25 change was stationary in ID0 (`3b` / 5, logger `371630682774` ns). Matched moving ID18 samples had identical median absolute EPS motor feedback at the two gains. |
| B25 | Lane-departure steering-vibration warning phase | All [five pulses](../../data/generated/camry_2026_08a_bit_census/lane_warning_episodes.csv) matched native warning-display onsets: 54 high frames in ID4 and 166 in ID0; another 2,070 ID4 frames were low. EPS feedback oscillated at ~25 Hz in three episodes. In both `13a` episodes the chassis selected host ID11 and the oscillations were absent. |

The [full-rate manifest](../../data/generated/camry_2026_08a_bit_census/captures.csv)
pins each segment's original path, native bus and SHA-256. The inventory
deduplicated 227 archive members against loose copies. It counts attributable
32-byte receive frames, excluding host sends, transport flags and forwarded
copies. For example, all 74,834 bare bus-0 rows on `27` have exact bus-2
peers at or before their timestamp. Truncated files contribute only readable
events. The [qlog-only census](../../data/generated/camry_2026_08a_bit_census/qlog_bits.csv)
keeps 37 observations and 13 adjacent pairs from [24 additional segments](../../data/generated/camry_2026_08a_bit_census/qlog_captures.csv)
outside the full-rate totals.

Replay in the [external log-reader environment](../WORKFLOW.md#external-openpilot-rlog-reducers):

```sh
uv run --no-sync --project "$OPENPILOT_ROOT" python -m tools.targets.camry.analysis.analyze_camry_2026_08a_bit_census \
  data/generated/camry_2026_08a_bit_census/captures.csv \
  --openpilot-root "$OPENPILOT_ROOT" --logs-root "$HOME/dev/inspect/logs"
```

### What triggers B22[2]?

**Inference: the camera marks a near frontal target as relevant at rest.**
Target qualification for *Acceleration Suppression at Low Speed* is a
plausible application. The [Camry owner's manual](https://assets.sia.toyota.com/publications/en/om-s/OM06266U/pdf/OM06266U.pdf)
(pp. 224–229) describes a PCS function for stopped vehicles, people,
bicycles and walls at roughly 0–15 km/h, with strong accelerator input
required for intervention. The recorded changes were target-state observations:
in the controlled trials, B22[2] alone changed in request B0:B25 at all 284
edges and Brake/VMM reported driver result ID63.

**Side, range and state.** In the [stationary road crossing](../../data/generated/camry_2026_08a_bit_census/stationary_target_crossing.csv)
(`140` / 4), B22[2] rose at 949.194 s as the reported target moved inward
from the right (PCS lateral code +3→+2, radar 1.36 m ahead and 0.80 m
right at entry). It stayed high through center and cleared at 950.698 s
as the code changed −2→−3. The wheels stayed stopped and both pedals were
released. Matching primary radar by range and relative speed alone gave
a median lateral error of 0.14 m across 272 held-out `0x5AE` publications
using signed `B6[7:3]` at about 0.30 m/count, right positive. The adjacent
speed field agreed within 2 km/h with radar relative speed on 107/112
moving-target samples and with negative ego speed on 2/112.

The [August 26 replay](../../data/generated/camry_2026_08a_bit_census/stationary_trials.json)
contains 142 rises and 142 falls in three stationary recordings: a
[cruise-button trial](../../targets/camry-2026/raw-20260826/NRTD_MANIFEST.txt)
and [two selector sweeps](../../targets/camry-2026/raw-20260826/READY_GEAR_MANIFEST.txt).
All 1,326 highs had zero wheel speed and accelerator, closed doors and
Brake Hold clear. The foot brake was on/off in 302/1,024 highs and the
EPB in 1,056/270.

| Recorded trial | Highs / frames | Separating observation |
|---|---:|---|
| Not READY, P | 625 / 1,475 | 22 rises preceded the first button action. |
| P/R/N/D/N/R/P | 495 / 2,475 | 395 highs in P, 78 in N and 22 in D; a pulse began 1.58 s after entering N. |
| P/D/B/D | 206 / 1,070 | 44 highs in P, 64 in D and 98 in B; rises began 3.27 s after entering B and 9.78 s after entering D. |

At 5 Hz PCS samples paired to a request ≤50 ms old, predicting high on
lateral code +2 rather than +3 classified 72/72 highs and 95/98 lows in
the first trial, then 74/75 highs and 335/344 lows in the selector sweeps.
Across all three trials, 68/76 inward crossings coincided with a rise
and 67/76 outward crossings with a fall; the other pairs stayed low.
Among PCS IDs matched to a unique bicycle-sized private outline at +2,
in P/N/D/B all 138 observations below 2.80 m were high, eight of 13 at
2.80 m were high, and the sole 2.85 m sample was low. All six +2 samples in
R were low; +3 in P/N/D/B gave one high and 415 lows. This is a transition
band for the recorded target.

**Object reports distinguish candidate types and track history.** The private
20 Hz `0x230` message has four 14-byte cells at B4, B18, B32 and B46. With
`R` denoting each cell after its two-byte prefix, `R3:R9` packs four
MSB-first pairs of unsigned 7-bit forward and signed 7-bit leftward
coordinates in 0.05 m counts. `R2[2:0]` distinguishes measured footprints:
1 (median 1.80 × 4.00 m), 2 (0.60 × 0.60 m), 3 (0.60 × 1.80 m) and
4 (point). `R0[3:0]` is a separate status; the high nibble minus one
modulo 16 agreed with `0x5AE B5[7:3]` in 15/17 held-out radar-matched targets.

In the [75-route road replay](../../data/generated/camry_2026_08a_bit_census/target_admission_routes.csv),
an object center in the first 3 m ahead and within ±0.80 m was present on
all 5,875 P/rest high epochs and 223,868 of 292,532 lows. Excluding status
`A` retained all highs and 96,412 lows. All [15 road rises](../../data/generated/camry_2026_08a_bit_census/target_admission_rises.csv)
had an in-window candidate on the next private report: nine status-1
squares and six point-only. The [per-route cohorts](../../data/generated/camry_2026_08a_bit_census/target_candidate_cohorts.csv)
divide the remaining candidates by whether all wheels had reached 1 km/h
earlier in that recording:

| In-window non-`A` candidates | Before motion: high / low | After motion: high / low |
|---|---:|---:|
| Points only | 5,638 / 26,655 | 0 / 67,735 |
| Laterally moving status-1 square | 187 / 41 | 15 / 22 |
| Other reports with an outline | 35 / 1,859 | 0 / 100 |

Signed `R11` agreed with lateral displacement in 237/245 continuous
square observations over 200 ms. Status-1 squares with `|R11| ≥ 6` and
`R1=0x3C` occurred on 79 highs and four lows; all four lows were outward
crossings at +0.75 or +0.80 m. Within ±0.60 m all 54 were high across
five routes. On `142` / 5 a square crossed the center at 2.30–2.35 m with
`R1` changing `0x14→0x34` and the bit stayed low.

Of 5,638 point-only high epochs, 2,775 were on `144`, whose recording began
high. Of the other 2,863, 2,766 followed an in-window moving square in
the same high interval. In the [same-ID handoff replay](../../data/generated/camry_2026_08a_bit_census/target_point_handoffs.csv),
two moving outlines became in-window points while high (`135` and `13c`),
accounting for 1,610 subsequent point-only highs and no lows before the next
track or timing break. One moving outline first became a point outside
the window and later accounted for 2,073 in-window lows; 13 slow outlines
that became in-window points accounted for another 4,101 lows. On `135` the
moving return converged on an existing stationary return as the older track
moved away. The private ID links reports, not necessarily the physical object.

A centered (within ±0.15 m) status-0 point occurred on 3,514 point-only
highs and 974 lows. On `3c` before driving, eight road thumbnails show a
parked vehicle roughly 1.35–1.40 m ahead, where the point and radar agreed
and the bit stayed low.

**Limits of the published signals.** On `142` / 5 (low) and `144` / 2
(high), both selected stationary points had the same status, footprint,
center (2.40 m ahead, 0.05 m right), velocity and primary radar coordinates.
The PCS payload B0:B25 differed only in track ID. On `13c` / 0, a falling
edge and the preceding high had identical private object and PCS bytes; the
persistent radar return's range increased from 2.495 to 2.545 m at the next
rise. In the controlled trials, 103/111 P/rest rises had a nearby low within
750 ms with the same preceding near-radar packet.

The [August 27 high capture](../../targets/camry-2026/raw-20260827/camry_post_repin_nrtd_20260827.json.gz)
(400/400) and [low capture](../../targets/camry-2026/raw-20260827/camry_post_repin_ready_20260827.json.gz)
(0/428) had the same closest near-radar position in P/rest with READY
observed in both. The matched PCS points were status `4` in 32 high reports
and `A` in 21 low reports; both recordings began at a stable level.
Ambient light changed at 28/28 road edges and 106/111 parked-low controls.
The [IMU and camera comparisons](../../data/generated/camry_2026_08a_bit_census/parked_motion_controls.csv)
found no vehicle jolt at those edges.

The [controlled matched pairs](../../data/generated/camry_2026_08a_bit_census/target_admission_trials.json)
give opposite bit values with identical preceding `0x230 B3:B63`, PCS
`0x5AE B0:B25` and selector in each of the three August 26 captures. The
next PCS lateral code separated the pair in both selector sweeps but not
in the not-READY trial. A second comparison in that trial matched seven
updates of the selected object, PCS and chassis signals, including prior
bit state and an 11-update high dwell; one high persisted and the other
cleared. In the gear sweep, matching three-update low histories preceded
either a rise or continued low. The capture evidence does not distinguish
shared PCS target selection from function-specific eligibility: GTS+
lists separate target (`1806`/`3806`, `5725`/`5727`/`572A`) and eligibility
(`57E5`/`57E6`) fields, and the [exact camera application](tss3-frc-firmware-acquisition.md)
is unavailable. The [recorded installation response](../../targets/camry-2026/raw-20260826/camry_nrtd_p5_oracles_extra_20260826.json)
identifies PCS as installed and Traffic Movement Notification as absent.

**Timing and release.** All 283 sequence-contiguous controlled edges took
the same phase of alternate 25 ms request publications. The [31 road edges](../../data/generated/camry_2026_08a_bit_census/stationary_road_edges.csv)
also kept one phase per route. All 28 P/rest edges followed the preceding
`0x180` cycle by 8.95–11.22 ms with zero camera-side ego speed and
unchanged `0x081 B0:B27` for ±1.25 s. The [12 complete P/rest pulses](../../data/generated/camry_2026_08a_bit_census/parked_pulses.csv)
lasted 49.6 ms–1.545 s. Three other highs persisted 1.17–1.37 s after
entering R and cleared within 29.85 ms of the first negative ego-speed
report. The bit stayed clear during three stock DRCC lead departures
(198 stopped hold frames) and during the `43` / 12 PCS escalation.

**Offline replay.** Run `uv run python -m tools.targets.camry.analysis.analyze_camry_2026_stationary_state`
for the checked-in recordings or add `--road-logs "$HOME/dev/inspect/logs" --openpilot-root "$OPENPILOT_ROOT"`
in the external log-reader environment for road edges (`--crossing` emits
the `140` / 4 comparison). The companion module
`tools.targets.camry.analysis.analyze_camry_2026_target_admission` uses the
same road arguments for filter counts; `--cohorts`, `--point-handoffs` and
`--rises` select individual evidence tables. With no road arguments it
prints the controlled same-input comparisons.

### B23[5]: steering effort depends on the lateral application

**ID11 responds to sustained effort.** On five held-out stock routes, the
[timestamped excursions](../../data/generated/camry_2026_08a_bit_census/driver_effort_excursions.csv)
show 0/50 short versus 150/150 sustained onsets, including the same split in
23/23 pairs matched by route and peak torque within 0.05 N·m. Release was
0/18 short versus 161/164 sustained. Median onset and release were 225 and
575 ms. On the 25 ms grid, short means 1–3 samples; sustained means at
least nine for onset and 23 for release.

The empirical ID11 fit on `3b/3c` used the magnitude of the five-sample
signed mean of EPS driver torque (`0x030`). Seven consecutive values
≥1.16 N·m predicted a rise three grid points later; 21 at ≤0.50 N·m
predicted a fall four points later. It held its prediction between these
conditions. On 17 held-out routes, the fit recovered 225/241 rises and
233/253 falls within ±75 ms (255 rises and 266 falls predicted). It
classified 40,340/41,646 highs and 353,382/355,505 lows. The same filter
without a duration requirement recovered 1/241 rises and 0/253 falls.
The [per-route counts](../../data/generated/camry_2026_08a_bit_census/driver_effort_routes.csv)
include unmatched predictions. ID11 B23[5] disagreed with the separate
`0x371` steering detector in 49,570/259,759 pairs.

**ID4 responds to shorter effort.** The bit was high on 236/2,124 native
publications, with and without the B25 warning. Across [27 episodes with
EPS coverage](../../data/generated/camry_2026_08a_bit_census/lane_departure_effort.csv),
2,064/2,088 publications had fresh 30 ms torque samples throughout the
comparison window. On `3b`–`3f`, the fitted high condition was a signed-mean
magnitude ≥1.20 N·m from 170 to 30 ms before publication on a 10 ms grid.
It classified 135/136 highs and 1,617/1,630 lows on ten held-out routes,
matching 7/9 rises and 9/9 falls wholly inside covered episodes within 75 ms.

### Where the inactive acceleration values come from

With B6 zero, both camera acceleration slots follow the earlier
`0x081 B20:B21` closed-accelerator reference. For consecutive native ID0
frames ≤100 ms apart with a change ≥3 counts, using the latest chassis
sample within 50 ms at a −25 ms offset matched **9,334/9,904** changes on
`3b`, versus 1,102 at zero offset. The same offset matched
**146,805/155,359** changes on [66 held-out routes](../../data/generated/camry_2026_08a_bit_census/neutral_acceleration_routes.csv)
versus 18,442 at zero. In the 121,334 holdout cases where the two chassis
words differed by ≥100 counts at publication, the earlier reference
matched 114,596 times and the earlier `B4:B5` combined result matched five.

### How B10 gets its value

**From inactive, MAIN captures current speed and RES restores the prior
target.** The [134 single-button stock entries](../../data/generated/camry_2026_08a_bit_census/cruise_entries.csv)
include 119 MAIN and 15 RES entries on 24 routes.

| Outcome | Five discovery routes | 19 held-out routes |
|---|---:|---:|
| MAIN: B10 within 1 km/h of four-wheel speed at press, floored to 29 km/h | 42/42 | 76/77 |
| MAIN below 29 km/h: B10 = 29, cluster setpoint = 19 mph | 3/3 | 26/26 |
| RES: B10 equals last recorded exit target | 3/3 | 10/10 (two exits unavailable) |
| RES: B10 within 2 km/h of current wheel speed with the same floor | 0/3 | 0/12 |

For 35 held-out MAIN entries with the retained `0x1B2 B1` and floored wheel
speed separated by ≥8 km/h, all new targets were within 2 km/h of wheel
speed and none within 1 km/h of the retained value. At `66` / 5, RES
restored 70 km/h with wheels at 34.90 and B1 at 71; a later MAIN captured
60 km/h with B1 still at 71. Across all 15 RES entries, B1 equaled B10
three times and was one count higher twelve times.

In the [270-entry timing replay](../../data/generated/camry_2026_08a_bit_census/main_capture_clocks.csv),
MAIN first published the new B10 27–85 ms after release. Using the integer
part of press-time SP1 (`0x0D7 B1:B2`, km/h), floored to 29 km/h, matched
40/40 discovery entries, 98/111 held-out stock entries and 112/119
host-longitudinal entries. Of 60 held-out cases where press and publication
predicted different integers, 53 matched press, four publication and
three neither. On `45` / 6, SP1 was 44.92 at press and 46.07 km/h at
publication; B10 became 44 and B1 became 45.

**While operating, `+` captures higher wheel speed with the accelerator
depressed.** Of [34 taps at ≥5 km/h overspeed](../../data/generated/camry_2026_08a_bit_census/cruise_overspeed_taps.csv)
(40–<400 ms, fresh pedal and wheel data), B10 captured within 0.58 km/h
on all 19 accelerator-open observations (5 stock, 14 native camera on
host-longitudinal drives). All 15 pedal-released taps changed the display
by one mph (2 stock, 13 host-longitudinal).

**Ordinary one-mph edits follow an empirical internal grid.** On
[395 single-step edits](../../data/generated/camry_2026_08a_bit_census/cruise_adjustment_grid.csv)
with released accelerator and settled B1, the fit
`H = round_to_half(1.571585 × displayed_mph − 0.436646)` km/h predicted
B10 as `floor(H)` and B1 as `ceil(H)`. Fit on 132 stock taps (35 display
settings), it predicted both bytes in all 67 stock and 196 native-camera
host-longitudinal holdouts, including 149 taps ending on settings absent
from the fit. The observed range was 19–78 mph. MAIN landed off-grid on
35/119 entries; all 12 ordinary edits from off-grid B10 ended on-grid.
At a steady 46 mph display on `45`, B10 could be 71 or 72 km/h. When
inactive, B10 was zero on 66,416 held-out observations with a retained
display setting.

**Long presses can repeat one mph at a time.** The
[20 recorded strokes of at least 400 ms](../../data/generated/camry_2026_08a_bit_census/cruise_hold_witnesses.csv)
include 14 inactive and one already at the minimum with no changes.
The other five produced [15 steps](../../data/generated/camry_2026_08a_bit_census/cruise_hold_steps.csv)
on the same grid. On stock `3b` / 67 and native camera `175` / 2, repeating
holds first stepped 632 and 643 ms after press, then every 292–303 ms
(ten intervals). On `13c` / 93, a 540 ms press stepped after release
and a 692 ms press stepped before release. In 89/90 held-out stock
pedal-free taps B10 stepped 30–80 ms after release. The other (`27` / 3,
`291965512542` ns) advanced `0x251 B2` 41→42 mph while B10 stayed at 65 km/h.

### Two rare longitudinal applications

B5[2] marks 2,802 frames across [29 episodes on four routes](../../data/generated/camry_2026_08a_bit_census/b5_episodes.csv).
The index includes exact logger timestamps, chassis/pedal pairs ≤75 ms old,
lead estimates ≤100 ms old and centered one-second wheel acceleration.

**ID13: driver-nonresponse deceleration.** Both episodes followed the same
native `0x371` warning progression with cruise operating, pedals released
and no reported lead. Of 3,209,179 requests paired to `0x371` within
260 ms, B19=`0x84` appeared only in those two segments (172/175 such
pairs carried ID13). The [owner's manual](https://www.toyota.com/content/dam/toyotaowners/dom/add-driver-pdfs/2026/camry-hv/MY26_Camry_OM_Excerpt_for_Driving_Support_Systems_D2_ML_0801.pdf)
and FRC P5 monitor `2181` (“Driver Emergency Stop Assist Function”)
support the inference that this is the deceleration phase of that function.

| Original | ID13 samples | Chassis result | Independent wheel motion during the request |
|---|---:|---|---|
| `45--805b7ca6ab` / 4, stock longitudinal | 36 | ID13 on 34; ID11 on the first two | median −0.37 m/s² |
| `91--4bfd0e2224` / 5, host longitudinal enabled | 144 | ID11 on all 144 | median **+0.19 m/s²** |

From 250 ms into each episode, at a first-slot request of −500 counts
and second slot zero, all 22 preceding results (<30 ms old) on `45`
were ID13 at −502 to −496 counts; all 133 on `91` were ID11 at +59 to
+75 counts.

**ID17: deceleration relative to the coast reference, usually outside
cruise.** Both slots were 2–934 counts below the earlier closed-accelerator
reference on all 2,622 frames in [27 Camry episodes](../../data/generated/camry_2026_08a_bit_census/id17_reference.csv)
using the ID0 lag. On the [independent Corolla capture](../../community/spanconstant/README.md#separate-july-29-driving-rlog),
36/37 were below and one equal; six absolute requests were positive.
The leading application inference is [Toyota PDA assistance behind a
preceding vehicle](https://pressroom.toyota.com/the-evolution-of-safety-at-toyota-part-3-the-future-of-safety/).

On `3b`, 2,612/2,618 frames had cruise clear, 2,110 accompanied lateral
ID18 and 2,241 paired with chassis result ID17. All 26 onsets followed
ID0 and had a model lead; 23 were closing faster than 0.5 m/s. In nine
same-segment ID0 controls matched for pedals, speed and lateral state,
all had a lead, but the >0.5 m/s closing criterion held for eight onsets
versus two controls. Native radar saw a persistent return within 120 m
and ±2.25 m closing >0.5 m/s on 25/26 onsets (eight onsets versus six
controls in the nine pairs). With the nearest persistent track within
±1.5 m and native range also matched, it was closing at 5/6 onsets versus
2/6 controls, with median relative speeds −1.21 versus −0.025 m/s. All
matched comparisons are from one drive.

The four frames on `27` / 7 had no model lead. Native radar tracked a
return 90.56→88.72 m ahead in 100 ms, about 2 m left of center, with
closure of 18.2–18.3 m/s against 18.47 m/s wheel speed. The brake pedal
was already pressed and the chassis selected ID63. At the [three Corolla
onsets](../../data/generated/camry_2026_08a_bit_census/corolla_id17.csv),
cruise was off, allocation was 3 and lateral ID was 0. The nearest
persistent central returns were 11.02, 11.58 and 11.33 m ahead, closing
at 1.00, 0.55 and 0.35 m/s respectively. The wheels showed 5.89–6.39 m/s
while `MOCK` CarState showed zero; all 37 fresh chassis results were ID63.

## Longitudinal request and result comparisons

### Message structure and drive/brake decomposition

Across all 1,232,664 native `0x081` frames, `B0:B3` was `00000018` and
the embedded Toyota prefix checksum satisfied
`B7 = (0x81 + 8 + sum(B0..B6)) & 255`.

The current byte-level reconstruction is:

| Message | Location | Supported interpretation |
|---|---|---|
| `0x08A` | `B0:B2`, `B15`, `B27` | Always zero in the 75-route census |
| `0x08A` | `B3[3]`, `B4[5]`, `B4[7]` | Cruise operation, delayed hold, startup-stage marker respectively |
| `0x08A` | `B3[2]`, `B4[6]`, `B5[2]` | [PCS-associated](#pcs-escalation-leaves-the-policy-field-unchanged) phases and [IDs 13/17](#two-rare-longitudinal-applications) marker |
| `0x08A` | `B6[7:2]` / `B6[1:0]`, `B8:B9` | Application ID / allocation / signed16BE first acceleration slot (upper DRCC bound) |
| `0x08A` | `B7`; `B11:B12` | eight-byte-prefix Toyota checksum; signed16BE lower acceleration slot (requester/allocation unmapped) |
| `0x08A` | `B10` | Internal cruise setpoint in km/h |
| `0x08A` | `B13:B14`, `B16:B17` | Invariant `0x7FFF` across the Camry, Crown and Corolla samples; field assignments open |
| `0x08A` | `B18:B19`, `B21[5:0]`, `B24`, `B25` | Lateral pinion reference; application IDs 0/4/11/18; assist gain; candidate damping gain with a measured lane-departure warning association |
| `0x08A` | `B20[7:6]`, `B22[2,4,5]`, `B23[5]` | Policy, longitudinal states, and steering association respectively; [driving-state tests above](#every-bit-of-native-0x08a) |
| `0x08A` | `B26[5:0]` | request sequence |
| `0x081` | `B4:B5`, `B6[5:0]`, `B6[7]`, `B7` | inferred combined quantity, result-source ID, standstill-associated state, verified checksum |
| `0x081` | `B11[4]`, `B13`, `B16:B17` | request-loss supervision; lateral result ID/status; pinion result/reference |
| `0x081` | `B18:B19`, `B20:B21`, `B22:B23`, `B24:B25`, `B26:B27` | inferred drive-side, closed/open capability, accelerator demand, and driver-brake quantities as bounded above |
| both | `B28:B31` | security trailer |

Manual-braking observations independently distinguish the two result-like words.
On primary-drive rows with result ID63, no accelerator, and signed13 brake word
below −50, the median raw-count ratio `(B4−B18)/brake_word` is **10.268**.
Applying that coefficient without refitting to **84,434 historical rows** gives
a median absolute residual of **3.53 counts** (nominal 0.00353 m/s²).
A fixed **10.24-count step with truncation** explains much of the apparent
gain difference, and transitions produce larger residuals. At held-brake
standstill on route `87`, t=9.972897, `B4=−2.458`, `B18=+0.666`,
brake word=−305, and wheel acceleration is zero. During route-86 automatic
braking, the brake word is zero despite `B4−B18=−0.957`.

[US20200070849A1, Fig. 4 and sections 2-1 through 2-4](https://patents.google.com/patent/US20200070849A1/en)
separates selected acceleration, sensor-derived body acceleration, fully
closed/open powertrain capability, and accelerator/brake-pedal demand.
The brake-pedal quantity explicitly excludes automatic braking.
[US20200094835A1, steps S104–S107](https://patents.google.com/patent/US20200094835A1/en)
separately describes powertrain availability and the additional braking needed
below that availability. These definitions support the decomposition.
The empirical `B18=min(max(B4,B24),B22)` relation uses the capability candidate
`B22`. The first patent's clamp instead uses the application-request upper bound,
so these formulas describe distinct bounds.

The recorder's float32 fields `5252/5253/5261/5262` describe brake-pedal
demand, body acceleration, fully closed ground acceleration and accelerator
demand. The [Operation-FFD guide](../tooling/pcs-data-viewer-tss3-dictionary.md#arbitration-result-acceleration-export)
documents Toyota's separate `57DB` **Arbitration result Acceleration**
field (signed16BE × 0.001).

**`B4:B5` is the leading `57DB` candidate.** Two [manifest-pinned stock
rlogs](../../data/generated/camry_20260930_vmc_status/input_manifest.json)
separate it from `B18:B19` during moving cruise deceleration (neither
pedal, ID11, native bus-0 `0x081`). The gap compares the lowest B18 with
the highest B4 in a ±150 ms window around each anchor.

| Original route / segment | Route time (s) | Frames | Median B18−B4 (m/s²) | Example raw B4 / B18 (logger ns) | Min gap at ±150 ms (m/s²) |
|---|---:|---:|---:|---|---:|
| `0000003f--36e72f5fdc` / 21 | 1319.043519–1321.019239 | 67 | 1.199 | `F9DD` / `FEFB` (`6212699916507`) | 0.209 |
| `00000165--97064ab212` / 2 | 161.154110–162.018722 | 30 | 0.533 | `FBE9` / `FE7A` (`314641639067`) | 0.326 |

All 97 anchors remain separated even with ±0.050 m/s² slack per word.
Route time is relative to the first `logMonoTime` in segment 0.

Independent wheel deceleration (`0x0AA`) favors the combined B4 result.
Each sampled second uses fault-free four-wheel means at ±0.5 s, with
endpoints ≤100 ms old, valid CarState/sensors, speed >5 m/s, gas released
and B18−B4 ≥0.5 m/s².
The driver-braking observations are partitioned by route SHA-256 parity:

| Braking population | Routes | One-second observations | Median absolute error B4 / B18 (m/s²) | B4 closer |
|---|---:|---:|---:|---:|
| Driver brake, result ID63; even partition | 6 | 176 | 0.154 / 1.147 | 171 |
| Driver brake, result ID63; odd partition | 15 | 284 | 0.188 / 1.164 | 278 |
| Stock cruise, neither pedal, result ID11; both partitions | 2 | 7 | 0.056 / 1.008 | 6 |

B4 had lower median error on all 21 manual-braking routes. The seven
automatic-braking observations favor the same assignment. A synchronized
`57DB` export would directly test the recorder-name join; the
[August 26 synchronized capture](../../targets/camry-2026/raw-20260826/camry_nrtd_cruise_can_sync_20260826.json.gz)
has 90,932 CAN frames and 1,742 diagnostic rows, with FRC DIDs `1906`/`1912`.

### Repeated braking ceiling and request-policy candidate

The weak-braking shape repeats as a roughly **−1.0 m/s² additional contribution**
below the closed-pedal baseline. In the route-86 packet above,
`−0.466 + (−0.957) = −1.423`, close to wheel-derived −1.453.
The drive/brake interpretation remains an inference; the subtraction is observed.

Selection uses the existing preceding-only joins and exact-payload host origin:
fresh request and CarState; no driver pedals; result ID11; no request loss;
speed >2 m/s; raw B6=`0x2D`, B7=`0x47`; bounds equal within
0.001 m/s²; upper request <−0.7; delivered `0x08A B20[7]=1`; and
`request−0x081.B18 <−1.1 m/s²` continuously for at least 300 ms.
Gaps over 100 ms break an episode; discard its first 300 ms.
**No selection condition uses the B4 tracking error.**

This yields **12 episodes / 8 routes / 708 status rows**. Every retained
`B4−B18` lies between **−1.010 and −0.956 m/s²**:

| Route suffix | Episode start, t_route (s) | Duration (s) | Rows after 300 ms | Median `B4−B18` (m/s²) |
|---|---:|---:|---:|---:|
| `03--78555c9090` | 505.788 | 0.512 | 7 | −1.000 |
| `51--894db634a8` | 69.214 | 1.792 | 50 | −1.004 |
| `51--894db634a8` | 338.208 | 2.009 | 57 | −1.003 |
| `55--0d20bbf0c0` | 110.319 | 1.118 | 28 | −1.004 |
| `64--6d1ea4acc9` | 178.423 | 2.426 | 72 | −0.981 |
| `64--6d1ea4acc9` | 604.445 | 1.436 | 38 | −0.997 |
| `64--6d1ea4acc9` | 639.328 | 1.265 | 33 | −0.990 |
| `67--abf9d48e19` | 278.071 | 1.166 | 29 | −0.997 |
| `67--abf9d48e19` | 411.124 | 2.490 | 73 | −1.002 |
| `86--575a5fd6a5` | 245.092 | 8.815 | 285 | −0.976 |
| `88--462e38e23b` | 454.885 | 0.819 | 18 | −0.974 |
| `175--6c2758b35b` | 58.539 | 0.814 | 18 | −1.008 |

All times and software identities resolve through the existing
`input_manifest.json`; full route IDs are zero-padded to eight hexadecimal
digits before `--`. A follow-on calculation over the saved raw/joined caches
produced these results separately from the original summary generator.
An empirical model for these states is
`B4 ≈ max(request, B18−1.0 m/s²)`; median absolute error is **0.008 m/s²**,
maximum **0.044 m/s²**.

The stock strong-braking comparison on route `3f`, segment21, is an important
counterexample to a universal cap. Its `B4−B18` reaches **−1.352 m/s²** while
B4 follows the request. A directly redecoded packet at t=1313.999846 is
`00000018f8c00b6400000004000b00000016fdddfddd1208fddd000094a9766d`:
`B4=−1.856`, `B18=−0.547`, difference=−1.309, driver-brake word=0.
Strong stock comparison coverage is limited to one observational episode.

**Request-policy lead in the recorded stack:** before opendbc commit
`3ec57f92`, `opendbc/car/toyota/toyotacan.py::create_tss3_control_request_values`
hardcoded `CRUISE_STATE_MIRROR=3` in its synthesized longitudinal request,
making `0x08A B20[7:6]=0b11` (`0xC0`). The stock strong-braking example uses
`0b01` (`0x40`). Stock-longitudinal pass-through retains the native longitudinal
fields. The following comparisons do not isolate the field's causal effect.
The [policy-one cutover](#policy-one-encoder-cutover) changes that constant.

### Stock following versus free-cruise association

**Observed:** the native `0x08A B20[7:6]` values have a strong association with
following-like versus free-cruise-like scenes. Selection of eight stock-ACC segments
used coverage of both field values, independently of lead presence:

| Stock route | Segments |
|---|---|
| `0000003e--1a2f20417d` | 23, 42, 54 |
| `0000003f--36e72f5fdc` | 25, 34, 48, 51, 61 |

The original rlogs, software identities, and SHA-256 hashes are listed in the
existing [input manifest](../../data/generated/camry_20260930_vmc_status/input_manifest.json).
Extraction read **9,599 `radarState` messages**. For the retained fresh
request/status samples above 2 m/s, each status row was paired with the
preceding `radarState.leadOne` sample only when its age was below 100 ms.
The resulting 15,741 status rows give:

| `0x08A B20[7:6]` | Matched status rows | Lead-present rows | Lead-present fraction | Median lead time gap when present |
|---|---:|---:|---:|---:|
| `1` (`0x40`) | 7,641 | 7,521 | 98.43% | 2.629 s |
| `3` (`0xC0`) | 8,100 | 1,656 | 20.44% | 3.479 s |

Time gap is `leadOne.dRel / vehicle_speed`. The lead-present rows under
`0xC0` generally have farther, lower-confidence leads. Both populations are
near their set speeds: median set-speed-minus-vehicle-speed is +0.101 m/s
under `0x40` and +0.056 m/s under `0xC0`.

These are **openpilot's radar/model lead estimates**. Status rows are temporally
correlated, and multiple rows can reuse one radar sample. This exploratory
two-route comparison uses retained request/status caches and additional raw-rlog
lead extraction. It supplements the existing VMC summary generator.

The native field changes while cruise remains active. Thus the observed
`0x40/0xC0` distinction is not adequately described as another copy of the
cruise latch. Following/free-cruise describe scene associations; the button-driven
transitions below also occur without a lead-presence change.

#### Native radar separates policy, display state and headway

The native-radar comparison covers 160,625 complete cycles in 134 segments
on 22 stock routes. The moving central-track proxy is the nearest 2–120 m
return within ±1.5 m, tracked for ≥250 ms and moving above 2 m/s over ground.
On `3b`–`3f` it was more common under policy 1 than 3 at matched speed
and setpoint error, with stable settings and pedals released in adaptive cruise.

**B20 policy tracks the following display more often than radar or model
lead presence.** Of 128 sustained policy changes away from button/setpoint
events, 83 matched a direction-consistent `0x251 B3[1]` edge within 600 ms,
versus 14 changes in moving central-track presence and 17 in openpilot lead
presence. On `3b` / 42 the display bit cleared 9.8 ms before policy 1→3
while the same track remained at 64.4–64.6 m. Display matches varied by
route (81/102 on `3b`–`3f`, 2/26 later); the samples also differed in speed
(90/102 early changes above 29 m/s, all 26 later below 22 m/s, both later
matches near 10.7 m/s). Only 6/204 button/setpoint-associated policy changes
matched a display-bit edge; none coincided with a change in the distance
bin or selected interval.

**`0x251 B4[7:5]` gives five speed-dependent following-distance bins.**
The driver-selected interval is in B5[7:5]. Highway time-gap boundaries
fitted on `3b` (0.88, 1.08, 1.51 and 2.00 s) matched 4,462/4,657 bins
on `3c/3d` and 4,469/4,688 on `3e/3f`, versus 3,522 and 4,012 using range
alone. Of [80 display steps](../../data/generated/camry_2026_08a_bit_census/headway_steps.csv)
with a continuous track and unchanged settings, all 51 holdouts moved in
the direction of both native range change and relative speed (48 up, three
down). Bin 4 also occurred with B3[1] clear and under both policies.

The same `2→3` step on `3c` occurred at 11.23 m and 2.84 m/s (3.95 s)
in segment 22, versus 43.36 m and 29.07 m/s (1.49 s) in segment 45. In
segment 24 a `3→4` step accompanied increasing range (12.52→13.85 m)
but decreasing time gap (4.34→4.13 s).

In [316 adjacent-bin transitions](../../data/generated/camry_2026_08a_bit_census/headway_edge_observations.csv)
with the same track, display state, policy and settings, fitting
`range = offset + slope × speed` on 114 `3b` transitions gave
4.5–7.7 m offsets. On the other 202 transitions, mean absolute range
error was 1.50 m versus 2.86 m for a fixed time gap. Below 15 m/s (49
transitions), it was 1.03 versus 4.96 m; adding direction and delay to
the time-gap fit improved it to 3.86 m. The offsets describe the
observed boundaries, with individual misses such as `3d` / 37
(crossing at 66.15 m, about 14 m above the fit).

### Native policy transitions and cruise-speed buttons

The follow-on census retains camera-origin requests separately from host
requests and vehicle-side forwarded copies. It finds **1,217 continuous
`1 ↔ 3` transitions** with ordinary raw B6/B7=`0x2D/0x47` unchanged:
610 `1 → 3`, 607 `3 → 1`. Continuity requires the same
route/segment and adjacent logger timestamps no more than 100 ms apart;
same-timestamp batches and gaps are not assigned transition order.

- Both directions occur with positive and negative acceleration requests.
- In **144 transitions**, neither acceleration bound changes.
- **379 of 610 `1 → 3` transitions** change requested speed in the same
  packet; none of the 607 reverse transitions does. Of those 379 speed
  changes, 139 are on stock-ACC routes and 240 on openpilot-longitudinal
  routes; the latter are native camera requests.
- Some scene-context transitions occur while openpilot continues detecting
  the same lead. Its lead selection is not Toyota's internal ACC target.

Original button packets establish driver-input association independently of
scene inference. One stock-ACC example, route `0000003f--36e72f5fdc`,
segment 15:

| Route time (s) | Observation |
|---|---|
| 902.257 | RES pressed |
| 902.298 | Native policy becomes `1`; requested speed remains 97 km/h; acceleration −0.068 m/s² |
| 902.349 | RES released |
| 902.399 | Native policy returns to `3`; requested speed becomes 98 km/h; acceleration −0.032 m/s² |

The original SET packets on stock route `0000003e--1a2f20417d`, segment 15,
show the corresponding decrement sequence: press at 932.356860 s, policy `1`
at 932.428377 s while speed remains 119 km/h, release at 932.449123 s, then
policy `3` and 117 km/h at 932.528814 s. Thus this is neither an
acceleration-sign flag nor solely a lead-present indicator.

For ordinary raw B6/B7=`0x2D/0x47` requests on stock-ACC recordings,
observed upper-acceleration ranges are −1.888…+0.925 m/s² under policy `1`
and −0.993…+0.942 m/s² under policy `3`. Native traffic during an
openpilot-longitudinal drive also switches
to policy `3` at −1.444 m/s², then relaxes toward zero; stronger braking does
not invariably imply policy `1`.

The corpus also contains hold-associated checksum changes, B6=`0x35` /
B5=`0x04` intervention headers, and B6 ID11 candidates with checksum
`0x00..0x03` and unequal acceleration bounds. Policy `0` is not a universal
no-request indicator. These header states are separate comparison populations.

Verification: eight representative before/after request packets were matched
byte-for-byte to the original rlogs, including source bus and logger timestamp.
Button observations above were extracted from the original segments. Source
identities are in the existing
[corpus manifest](../../data/generated/camry_20260930_vmc_status/input_manifest.json).

### PCS escalation leaves the policy field unchanged

In route `00000043--29caa20fbc`, segment 12, the native policy is
**`1` before, throughout, and after the B4[6]-asserted interval**.
Its preceding transition was about 79.5 s earlier under an ordinary
request. The host's policy `3` mismatch predates the PCS-associated flags.

The ordinary native request ramps from about +0.37 to −4.0 m/s² over
6.6 s and reaches −4.0 **20.226 ms before** B4[6] asserts. B6 remains
ID11/allocation1 and both acceleration slots remain equal:

| Offset from B4[6] entry (ms) | B7 checksum | Both bounds (m/s²) | B3[2] | B4[6] | B20 |
|---|---|---:|---:|---:|---|
| −20.226 | `0x47` | −4.000 | 0 | 0 | `0x40` |
| 0 | `0x8B` | −4.000 | 1 | 1 | `0x40` |
| +215.878 | `0x87` | −4.000 | 0 | 1 | `0x40` |
| +486.045 | `0x87` | −3.800 | 0 | 1 | `0x40` |
| +518.686 | `0x47` | −3.800 | 0 | 0 | `0x40` |

B3[2] marked the first nine flagged frames and B4[6] all 21.
At the third flagged frame, after driver braking began, B22[5] marked
[delayed release](#every-bit-of-native-0x08a). Native radar tracked the
same return from 14.37 m at −7.05 m/s just before onset, to 12.12 m
before B3[2] cleared and 10.13 m before B4[6] cleared.

The [bracketing CAN observations](../../data/generated/camry_2026_08a_bit_census/pcs_phase_edges.csv)
show changes on `0x411`, `0x5AE`, `0x1D9` and `0x608` in the same receive
batch. All four patterns occurred only in this episode across the 75-route
census. `0x1D9 B5[7]` cleared by +324 ms; `0x5AE B2[2]` was still high at
+486 ms. On `43` / 9, a similar closing return (14.28 m, −6.30 m/s) with
the brake pressed had none of those patterns. On `0x411`, B0[5:4] and
B3[1:0] both changed 0→3 while the older status-icon field B0[7:6] stayed
zero. On `1c` / 0 that icon field changed without either `0x08A` phase bit.
An audible cue remains unattributed: the host requested a disengagement
sound, and 2/19 matched non-PCS disengagement controls had an equal or
larger sound-pressure rise.

The raw brake switch reported pressed at +14.464 ms (`carState` at
+16.733 ms), and native forwarding resumed at +33.508 ms. The first two
flagged native packets lack vehicle-side TX confirmation; the host was
still publishing about −1.5 m/s² under policy 3 versus the native −4.0
under policy 1. The [PCS artifact](../../data/generated/camry_20260921_pcs_alert.json)
and [relay analysis](camry-2026-tss3-opendbc-port.md#pcs-recorder-semantics)
retain the publication boundary and source for the 2,401 native packets
matched to the raw cache.

### Policy-one encoder cutover

The constant originated in opendbc commit `089e6466` (September 21), which
replaced native-field preservation with a host-built template containing
B20=`0xC0`, based on 44,613 early native publications. Commit `b7e8ccad`
subsequently named its high bits `CRUISE_STATE_MIRROR`, claiming steady
cruise value `3`. The expanded corpus disproves that universal interpretation;
it does not establish an OEM name for the field.

At the owner's request, opendbc commit
[`3ec57f92`](https://github.com/kaikozlov/opendbc/commit/3ec57f92)
changes the synthesized openpilot-longitudinal value to **`1`** and Panda's
matching B20 requirement from `0xC0` to `0x40`. Stock-longitudinal forwarding
still preserves the factory value. The legacy DBC field name is retained;
neither its name nor this cutover establishes the signal's semantics.

Verification: 75 targeted Toyota safety/car/transport tests ran with four
skipped. An offline encoder/packer/compiled-safety smoke accepted policy `1`
at −3.5, −2.123, 0, +1, and +2 m/s², rejected host policy values `0/2/3`,
and accepted native-preserving stock-long requests under policies `1` and
`3`. The cutover is an experimental candidate.

The existing raw steering-assist gain `100` is `LATERAL_ASSIST_GAIN=1.0`;
it is not a longitudinal feedback-gain setting. The acceleration requests
and B20 policy are separate controls. GTS's responsiveness vocabulary remains
relevant, but has no verified B20 mapping.

### November 17 post-policy-one capture check

Screened all **83 qlogs** from `0000013a--8201802acc` and **33 qlogs** from
`0000013e--27d453251c`, then ran the existing VMC extractor/joiner on each
route's three strongest-demand segments. Both captures enable openpilot longitudinal;
the recorded openpilot commits are `c4d5e394` and `433eb007`, respectively.

| Route | Rlog segments | Eligible status rows | Minimum request (m/s²) | Minimum request minus B18 (m/s²) |
|---|---|---:|---:|---:|
| `13a` | 12, 13, 42 | 3,572 | −1.444 | −0.722 |
| `13e` | 5, 8, 18 | 4,860 | −1.111 | −0.654 |

All **8,432** eligible rows carry delivered B20 policy `1`. Selection requires
an exact host-payload match, active longitudinal control, no driver pedals,
speed >2 m/s, result ID11, request-loss clear, and equal request bounds.
All selected request/state/pedal joins satisfy the existing freshness windows.

Median `B4−request` is **−0.001 m/s²** in both selections. A segment-42
`13a` sample has request **−1.444**, B4 **−1.440**, and B18 **−0.722 m/s²**
at 24.681 m/s. These captures show ordinary request/result tracking. Neither
selection reaches the historical ceiling discriminator
`request < −0.7 && request−B18 < −1.1`; stronger-demand evidence is needed to
settle that regime after the policy change.

[Retained comparison](../../data/generated/camry_20260930_vmc_status/post_policy_one_20261117.json)
contains source hashes, capture identities, exact existing-reducer invocation,
selection arithmetic, quantiles, and representative raw status packets.

### GTS request-policy definitions and patent interpretation

Direct offline queries of the shipped `FRC_P5.ddb` records (`tools/gts did
FRC_P5 0x1B06 --json` and the corresponding `0x1B07` query) confirm separate
controls in the **ISA upper-request** diagnostic vocabulary:

| DID | Field | Decoded values |
|---|---|---|
| `0x1B06` | Braking Force and Driving Force Allocation Method Specification | 0 Engine Only; 1 Engine and Brake 1; 2 Engine and Brake 2; 3 Brake Only |
| `0x1B06` | Speed Change Priority Request | 0 no brake-coordination downshift request; 1 request exists |
| `0x1B06` | Responsiveness Request | 0 No FB; 1 FB Control High Gain; 2 FB Control Medium Gain; 3 FB Control Low Gain |
| `0x1B07` | Brake Hold Control Prohibited Flag | 0 Allowed; 1 Not Allowed |
| `0x1B07` | Stop Control Permission Flag | 0 Not Allowed; 1 Allowed |
| `0x1B07` | Brake Usage Limit Permission Flag | 0 Not Allowed; 1 Allowed |

Source: [recovered control-ownership vocabulary](../../data/generated/gtsplus_2026/tss3_control_ownership_surface.json).
The shipped PCS viewer's PDA(OAA) record `5A08_3` independently names
`ブレーキ使用制限許可フラグ`, with English alias **Brake Use Restriction Flag**.
The Japanese compound supports the reading **permission to restrict brake
use**. Record `5A07_3` separately names `応答性要求` / Response Priority Request.
Source: [EN/JA recorder dictionary](../../data/generated/gtsplus_2026/pcs_data_viewer_tss3_dictionary.json).

The [recorder decoder](../../data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json)
defines a **three-bit** response-priority field for `5A07` and three separate
one-bit flags for `5A08`; the DDB monitor uses a byte-wide responsiveness row
and another flag packing.

The **2026-10-01 offline GTS follow-up** is recorded in the
[recorder guide](../tooling/pcs-data-viewer-tss3-dictionary.md#separate-oaa-request-policy-fields):
it distinguishes OAA coasting/intermittent-drive permissions and four
acceleration-change limits, and reconfirms separate ACC target and
pre-jerk-limit request quantities. It also recovers the
[ADS field table](../tooling/pcs-data-viewer-tss3-dictionary.md#62-ads-recorder-schema)
and resolves the viewer's
[PBA event discriminator](../tooling/pcs-data-viewer-tss3-dictionary.md#pba-event-discriminator).
These results establish recorder definitions and consumer behavior.

[US20200094835A1, steps S104–S107](https://patents.google.com/patent/US20200094835A1/en)
describes powertrain availability and a remaining brake contribution below
that availability. [US12258022B2, Fig. 2 and its description](https://www.freepatentsonline.com/12258022.html)
separately describes application acceleration requests, conversion to force
or torque, actuator allocation, and actuator feedback. It also permits a
regenerative motor-generator in the brake subsystem. These disclosures support
the staged interpretation of request, drive-side contribution, and combined
result.

**[INFERENCE] Leading explanation: a companion request-policy mismatch.**
The recorded host stack requested stronger deceleration while fixing a field
to the value stock commonly associates with free cruising. In the documented
weak-braking episodes, the additional contribution stays near −1.0 m/s² despite
greater demand; the stock `0x40` comparison exceeds that magnitude. A restricted-braking
regime fits this shape better than merely insufficient controller gain.
Brake-restriction permission and responsiveness selection remain competing
field interpretations; a responsiveness setting could also select a regime
with a limiter.

The later policy-one cutover above changes the encoder and safety contract.

### What this changes and what stays open

The open comparisons are the direct [recorder `57DB` join](#message-structure-and-drivebrake-decomposition),
the [specific application behind stationary B22[2]](#what-triggers-b222),
and the [braking ceiling under policy 1](#november-17-post-policy-one-capture-check).

Reproduce from an external logs root (see
[WORKFLOW.md](../WORKFLOW.md#external-openpilot-rlog-reducers) for the full
prerequisites):

```bash
uv run --no-sync --project ../kai-openpilot/opendbc_repo python -m tools.targets.camry.analysis.analyze_camry_20260930_vmc_status --corpus-dir /tmp/tss3_vmc_corpus --logs-root ~/dev/inspect/logs --output-dir data/generated/camry_20260930_vmc_status
```
