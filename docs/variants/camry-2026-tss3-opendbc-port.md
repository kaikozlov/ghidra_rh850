# 2026 Camry TSS3 openpilot/opendbc port

**Target:** maintainer 2026 Camry Hybrid, EPS application F181
`8965F3307000 / 8A3113303100`.

The [capability matrix](camry-2026-capability-matrix.md) owns current port status
and inspected software identities. This report owns the integration shape and
the retained request/state observations below.

## Maintained integration

The controller uses the protected `0x08A CONTROL_REQUEST` for **both lateral
and longitudinal control**. It passes the application through the EPS-resident
signer and publishes the signed request. It does not use a direct B6/C7
steering adapter or a `0x160` acceleration encoder.

- `CarInterface` advertises TSS3 Alpha Long. The toggle selects openpilot
  longitudinal; stock-longitudinal mode remains available.
- `CarController.update_tss3()` receives ordinary CarControl, applies its
  angle and acceleration limits, and supplies both axes to `SignerTransport`.
- In stock-longitudinal mode the transport preserves the FRC's longitudinal
  fields. In openpilot-longitudinal mode the controller authors those fields.
- Toyota safety checks the application independently and manages replacement
  of the FRC request, including native PCS handoff.
- Cancel and HUD outputs are implemented in `update_tss3()`. The existence
  of these paths and their safety permissions is not a causal interpretation
  of an older, physically confounded cancel capture.

The [runtime contract](../architecture/toyota-tss3-minimal-runtime.md) owns
transport/topology responsibilities. The
[longitudinal report](camry-2026-longitudinal-evidence.md) owns request/result
semantics. The [evidence review](camry-2026-port-evidence-review.md) owns radar,
vehicle-model, fault-projection and cancellation measurements.

Exact EPS transmit tables and field maps belong in the
[EPS transmit report](camry-f33-eps-tx.md); the native request/arbitration/controller
distinction belongs in the
[vehicle-movement report](../architecture/toyota-tss3-vehicle-movement-arbitration.md).
These are not additional prerequisites for acknowledging the implemented port.

## Brake/FRC feedback observations

Retained September-17/18 comparisons distinguish request loss, feature handoff
and lateral-failure state. `0x081 B13[5:0]` is the lateral result ID;
`B13[7:6]` is a **candidate** two-bit lateral fail class, not an OEM-joined
CAN field name.

- Across healthy routes `37/3b/3c/3d/3e/3f/45`, 871,888 logged `0x081`
  observations contain class `00` on 871,642 and class `10` on 246,
  with the latter confined to four cold-start episodes of about 0.87–0.95 s.
- Dead-EPS route `000000d4--327b2c4bb8` has no `0x030`. Its first
  `B13=0x80` state lasts 3.725304 s before changing to `0xC0`; adjacent
  application payloads differ only in B13. Request/result IDs stay zero and
  `0x081 B11` stays `0x04` across that transition.
- In healthy starts `3c/3d/3f/45`, B13 clears 39.215 / 20.779 / 40.711 /
  19.856 ms after the EPS driver-torque-invalid gate clears.
- Route `93` has B13 back at `00` while cruise remains unavailable.
  Thus this field alone is not the persistent DRCC latch.
- All 473 lateral-request-ID transitions in the examined 12-route corpus have
  matching result-ID transitions within 42.893 ms. Nonzero feature handoffs
  do not require a request-loss gap.

The semantic lead is recorder `5283_1 Lateral control system fail class
status`, together with Toyota's separate raw-reliability and application-fail-class
vocabulary. A synchronized recorder/wire join is still needed to assign that
OEM name to the high bits. Retained comparison:
`targets/camry-2026/raw-20260917/brake-frc-081-fault-status/`.
The [request-invalidation report](../architecture/toyota-request-invalidation-us20230166772.md)
owns the feature-selection interpretation.

## Stock lateral request and result observations

**Scope and grade:** observed, dynamic-trace. A separate read-only reduction of
all **253 segments** from routes `0000003b--62262eb7a1` (110),
`0000003c--97b9e7a69a` (81), and `0000003d--0e812cecba` (62) covers about
252 minutes and counts **27,173,143 native `can` records on Panda buses 0/1/2**.
None is `0x0B6`, `0x131`, or `0x2E4`. Openpilot `sendcan` and Panda TX returns
are excluded from this native census.

### Signal roles

Byte offsets are zero-based. These fields are passive observables.

| Carrier | Predominant captured side | Observable | Signal role |
|---|---|---|---|
| `0x08A` | Panda bus 2 | B21 request ID; signed BE16 B18:B19 request angle; B24 request level | Stock lateral-request state |
| `0x081` | Panda bus 0 | signed BE16 B16:B17 steering-reference word | Closely mirrors the `0x08A` request |
| `0x025` | Panda bus 0 | existing steering angle/fraction/rate decode | Measured steering |
| `0x030` | Panda bus 0 | driver torque and B22:B23 mapped motor-feedback proxy | EPS telemetry; ordinary driver assist also produces motor feedback |

The two reference words use the existing `1024/17870` (~0.057302742)
deg/count representation. Panda bus numbers identify harness sides.

### Reference relationship and discovery scope

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
on every route. `0x090` and bus-1 `0x160` also correlate with steering.
Event timestamps describe logger publication batches.

### Divergent-request witness

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
target is ineffective.

### Native ID4 episodes

Re-reading the original rlogs confirms **248 native bus-2 `0x08A` frames** with
the entire B21 byte equal to 4 in five episodes. B24 is 100 in every one.
The existing Toyota dictionary labels ID4 as LDA.

| Route | Segment | First–last ID4 frame (s) | Frames | Logged openpilot lateral |
|---|---:|---:|---:|---|
| `3b` | 6 | 28.626–28.907 | 12 | inactive |
| `3c` | 40 | 16.211–18.741 | 102 | active |
| `3c` | 56 | 43.964–45.441 | 60 | inactive |
| `3d` | 56 | 59.294–59.969 | 28 | inactive |
| `3d` | 57 | 19.884–21.012 | 46 | inactive |

Four episodes provide stock request activity without simultaneous openpilot
lateral activation, with driver torque present.

### Provenance and integration boundary

Times above are seconds from the earliest `can`, `sendcan`, `carState`, or
`carControl` event in the named segment, matching the exact September reducer origin.
Original inputs:
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

The route `carParams` records identify the Camry platform and Brake firmware.
Separate same-car evidence establishes exact EPS identity. The original September reducer source was
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
`build/out/camry-20260904-stock-steering/` as disposable review outputs.

For integration, retain measured angle and driver validity as measured state,
and request/reference fields as passive observables. Do not promote request IDs
to engagement/readiness authority or replace measured feedback with a target.

## Hands-on detection and HUD evidence

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

The same route measures the native HUD publication cadence. On route `3f`, 5,305 same-segment
`0x412` intervals have median **1002.490 ms** (p10 **701.920 ms**, p90
**1004.749 ms**) and minimum **79.514 ms**. The 367 intervals whose payload
changes have median **432.440 ms** and minimum **79.514 ms**. Route `3e`
independently gives a **995.572-ms** median heartbeat and **82.526-ms** minimum.
The source is a roughly **1-Hz periodic heartbeat with event-driven
publications**. This is a native-traffic measurement, not the current host schedule.

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
Exist=0**. This exact Camry has ordinary LTA and its wheel-contact warning.
The relevant Toyota vocabulary for the ordinary Camry LTA nag is the explicit
judgment/message/buzzer/cancel-by-hands-off family above.

Current GTS+ also makes clear that **TSS3 hands-on sensing is not intrinsically
torque-only across the fleet**. The recovered TSS3 PCS Operation-FFD dictionary
contains `5222 = Touch sensor presence` (`タッチセンサ有無`) as an explicit
TSS3 configuration datum, and the current category-498 `FRC_P5` DTC table contains
`C1A7796 Steering Touch Sensor / Component Internal Failure`. These establish
TSS3/FRC support for steering-touch hardware. Toyota's 2026 Camry product matrix independently
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
for **w/ Steering Touch Sensor** and **w/ Steering Heater**. This supports the
OEM description of `5222` as a vehicle/configuration presence datum. Sources:
[XW60 steering-wheel parts matrix](https://www.toyotapartsdeal.com/parts-list/2024-toyota-prius/power_train_chassis/steering_wheel.html) and
[XW60 controller service procedure](https://www.mytoyo.com/heated_steering_wheel_controller-2728.html).

The wider diagnostic corpus supplies useful boundaries for that configuration.
Same-generation `LDA_P5`, used here as a predecessor semantic oracle, exposes two
independent judgments: DID `0x1044` **Not Holding
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
confirmation and can influence the notification timer. Deep review:
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
The capacitive wheel electronics form a **CXPI subnode behind the combination
meter**.

Current `A_B_CAN_P5` DDR data adds the downstream consumer side. Table 147 has six
consecutive records keyed **5500..5505**: left grip twice, right grip twice, then
two grip-validity records. Current `KgpDataCtrl.dll` independently proves the
`CDbDDRMonitorTable` key is the `u16` at row `+0x18` (`FindDbItem1` and
`ComparativeKey` both consume it); `GetExceptahandId` instead reads `+0x28` and
`GetExceptahandFlag` reads `+0x2D`. These decimal `5500..5505` values are
**SRS DDR-local monitor keys**. The host looks up table 149
`CDbDDRAddressTable` by selector bytes `+0x0A/+0x0B` and then local monitor key `+0x04`,
and the same grip key appears in multiple selector contexts with different
recorder-layout fields (`0x24` vs `0x60`). Table 150 independently pairs the
left/right values with local validity keys. This closes the GTS DDR-address path
as **recorder payload geometry**. The TSS3 FRC Operation-FFD
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
transitions have medians **0.37/0.34 N.m**, a dynamic hysteresis-like distribution.
The older 8-byte `0x371 LTA_RELATED` layout names a low-sensitivity
`STEERING_PRESSED` signal. The current PCS OEM label
`560D Driver Steering Control Detection Status` (`保舵検出状態`) provides a semantic match.

Using Toyota's own candidate instead of the 0.9-N.m proxy collapses the countdown
timing. The warning follows the most recent `B20[4]` **detector-release** transition
at almost exactly **13.0 s**: routes `3d`, `3e`, and `3f` all have median release-to-
warning times of ~13.00 s, with the 10th–90th percentile confined to roughly
**12.88–13.09 s**. The last asserted detector sample precedes warning by ~13.16 s,
consistent with the ~5-Hz `0x371` publication interval. This is strong evidence
that the FRC's ordinary-LTA countdown is reset by its low-sensitivity driver-
steering detector. The earlier ~16-s number measures the deliberately higher
0.9-N.m analysis proxy.

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
publication**. Combined with the
FRC's `U013187 Lost Communication with Power Steering Control Module A / Missing Message`
diagnostic dependency and the 13-s detector-release timing, the strongest current model is
**EPS 0x030 driver torque/state -> FRC driver-steering judgment -> FRC hands-off timer/state
publication -> 0x412 warning/escalation**.

There is a second timed warning stage. Route `3d` has one episode where
`0x412 B2[6]` first asserts **5.996 s** after `B19[6]` warning onset. Route `3f`
has three such episodes; their first escalation appears at 5.876–5.979 s after
warning onset (median **5.977 s**). Every escalated episode remains Target
Lateral ID **11** throughout. The observed sequence is
`warning -> ~6 s escalation -> driver acknowledgment`.

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
still active. The observed cancellation is documented in the
[hands-off cancellation report](camry-2026-hands-off-cancellation.md).

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

The retained reduction is generated by
`tools/targets/camry/analysis/analyze_camry_2026_driver_steering_threshold_split.py` into
`data/generated/camry_2026_driver_steering_threshold_split.json`.

Current upstream Toyota explains how comma normally removes the wheel-nudge nag.
`0x412` is a camera-owned replacement message in Toyota Panda safety
(`TOYOTA_BASE_TX_MSGS`, bus 0, `check_relay=true`), so the stock camera's `0x412`
is statically blocked across the relay and `CarController` transmits openpilot's
own `LKAS_HUD` instead. The legacy `STEERING_LTA.CLEAR_HOLD_STEERING_ALERT` field
is **not** the mechanism: upstream has hardcoded it to zero for years. Camry
integration follows the same message-ownership pattern.

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

Evidence and reproduction:

- `tools/targets/camry/analysis/analyze_camry_20260906_hands_off_warning.py`
- `data/generated/camry_20260906_hands_off_warning_audit.json`
- source routes `2026-09-04/{3b,3c,3d}` and `2026-09-06/{3e,3f}` under the
  maintainer Camry rlog archive
- fork opendbc Toyota safety/controller tests in
  `opendbc/car/toyota/tests/test_toyota.py`

## PDA and SDG lateral profiles

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
steering controller**.

A second target-native consumer handles Self-Propelled Transport.
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

Toyota diagnostics reserve Target Lateral ID `19=PDA`, and PDA-OAA has its own
pinion-angle/gain request tuple. **PDA-OAA -> ID19** is an architectural
**hypothesis**. The normal openpilot profile is ID11/LTA-LCA.

Deterministic evidence: `tools/targets/camry/analysis/analyze_camry_2026_pda_sdg.py`,
`data/generated/camry_2026_pda_sdg_attribution.json`, and
`tests/targets/camry/verify_camry_2026_pda_sdg.py`, joined to the exact-F33 target and current TSS3
managed recorder artifacts.
The attribution report uses
`data/generated/camry-8965F3307000/decompilations.jsonl` from commit `db0161f8`.



## Lateral-family census and EPS profile selection

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

The profile selector is downstream of the protected-PDU admission/health machinery,
and the common controller retains speed, angle/rate, fault, slew/limit and persistence state.
PDU44 still has the exact **seven 5-ms foreground-tick / nominal 35-ms communication
loss supervision**. `FUN_000CEF26` also uses profile-indexed threshold/persistence
calibrations (96 cycles; threshold 1280 for LDA/LTA/Hands-Off-LTA/PDA, 1536 for PCS,
2048 for SDG) that feed common readiness/fault state. These controller supervisors
operate while `CEFFC` recomputes the selected bank from the latest delivered ID
every pass.

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

Finally, the broad B6 road census needed one provenance correction before it could be
used. Archive route `27` contains **106,800** `src=2` B6 records, but every one has an
exact same-event, same-payload Panda `src=128` TX echo: `60,722` ID0 and `46,078` ID11.
The ordered payload sequences are byte-for-byte identical and timestamps are equal on
106,800/106,800 pairs. These are our own pre-repin relay-side copies.
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
`tests/targets/camry/verify_camry_2026_lateral_family_census.py`.

## Stock ACC delayed hold

The September road corpus originally exposed delayed hold through raw
`0x08A B7={0x66,0x67}`. **B7 is a checksum.** The actual structural
observation is B4[5], asserted on **198/198** retained delayed-hold
frames while the B3[3] cruise latch is set.

| Raw B6 | B4[5] | B7 checksum | Dynamic state |
|---|---:|---|---|
| `0x2D` | 0 | `0x47` | ordinary active cruise |
| `0x2C` | 0 | `0x46` | active accelerator override |
| `0x2D` | 1 | `0x67` | delayed zero-speed hold |
| `0x2C` | 1 | `0x66` | delayed hold with accelerator override |
| `0x47` | 0 | `0x65` | moving counterexample to checksum-based hold detection |

Routes `3b` and `3c` contain three delayed-hold episodes totaling
**198** native frames: 192 raw `0x2D/0x67` pairs and six `0x2C/0x66`.
Each episode enters after more than five seconds stopped and clears with
accelerator input before motion. No RES-button clear join is established.
The producer now segments these episodes on B4[5] with B3[3], preserving
the original raw pairs as observations rather than request identities.

B4[5]'s OEM name remains unmapped. The Corolla capture lacks an independent
hold witness, so its former checksum-derived standstill mapping is withdrawn.
No resume command follows from this analysis.

Evidence: `data/generated/camry_20260906_hands_off_warning_audit.json`,
`data/generated/camry_2026_longitudinal_request_plane.json`, and
`tests/targets/camry/verify_camry_2026_longitudinal_request_plane.py`.

## Parser-liveness measurements

The retained 18-message census uses native-source observations from routes
`3d/3e/3f` (62/78/84 segments), resetting its gap clock at each rlog boundary.

| Source | Retained measurement |
|---|---|
| `0x127` | approximately 51 Hz; lowest route median-derived rate 50.970 Hz |
| `0x08A` | at least 43.741 Hz median on the FRC source side |
| `0x0FE` | at least 33.111 Hz median |
| `0x610` | worst same-segment gap 1006.457 ms |
| `0x412` | worst same-segment gap 1758.564 ms; roughly 1-Hz heartbeat with event-driven updates |

These are capture measurements, not an inventory of every message checked by
the current parser. Current parser selection belongs to
`CarState.get_can_parsers_tss3()`.

Evidence: `tools/targets/camry/analysis/analyze_camry_2026_parser_liveness.py`,
`data/generated/camry_2026_parser_liveness.json`, and
`tests/targets/camry/verify_camry_2026_parser_liveness.py`.

## Native and host request cadence

The retained producer-bounds
drives measure native `0x08A` at **38.122 / 39.997 Hz** mean, while the later long routes
measure **43.741--43.947 Hz** from median same-segment spacing.

The fork therefore follows the ordinary openpilot **100-Hz CarController** cadence for the
host-owned request plane rather than waiting for native `0x08A` publications. This matches the
older Toyota steering precedent where openpilot sends `STEERING_LKA` every control tick even
though the source comment records stock traffic around 42 Hz. EPS remains responsible for
freshness and the `FV4 || MAC28` trailer, and Panda's vehicle-model angle check uses the same
100-Hz cadence. There is no present reason to exceed 100 Hz because the normal openpilot
vehicle-control state itself updates at 100 Hz.

## PCS recorder semantics

The recovered GTS+ PCS Data Viewer now supplies the complete 7,851-row ADU
recorder table. Its generic longitudinal interface is the same lower/upper
limit abstraction already seen dynamically: `2A02` records lower requester ID,
acceleration, distribution, shift/EPB/override/priority policy; `2A03` records
upper requester ID, acceleration, and distribution. `1592` separately records
the overall, brake, and powertrain arbitration-result IDs, while `161D` records
the resulting acceleration.

The recorder separately names PDA(OAA) upper-limit requests (`1F03..1F07`)
and PDA(DA) lower-limit requests (`5B07..5B11`). These describe Toyota's
request model; their recorder offsets do not identify CAN fields. In particular,
`0x08A` byte 7 is a checksum, so the former upper-ID-17/lower-ID-23
interpretation of the Corolla capture is withdrawn.

PCS evidence must be interpreted at the same boundary. The recorder separates
warning/target judgment, enable/prohibit state, deceleration request, generic
longitudinal arbitration, and final brake pressurization. A retained PCS alert
alone does not prove the downstream request was delivered. If the relay blocks
the FRC's native `0x08A`, VMC necessarily does not see the native PCS request
carried by that frame. Any supported architecture must preserve stock emergency
behavior through the normal openpilot/opendbc safety and CarController policy
shape; it cannot treat the result ID or alert as a sufficient PCS detector and
cannot add a separate vehicle-specific policy layer.

`1770_26` is `Automatic Start DDR Detection Signal`; DDR `5493/5494` are both
named `ACC Resume Trigger Signal`; and trigger 33 is `ACC cancel after resume`.
The next join is the DDR initializer plus the retained stop/resume and PCS-alert
logs, with the existing rule unchanged: no resume command is emitted until the
normal upstream state and safety contracts can express it.

Evidence:
`data/generated/gtsplus_2026/pcs_data_viewer_adu_semantics.json`,
`tools/techstream/extract_pcs_data_viewer_adu_semantics.py`, and
`tests/techstream/verify_gtsplus_pcs_data_viewer_adu_semantics.py`.

## PCS observation and implementation

The inspected port detects the native PCS request flag and returns `0x08A`
ownership to the FRC in both CarController and Toyota safety. The source names
the flag `PCS_BRAKE_REQUEST`; that implementation label does not supply an
OEM-stage mapping. The following capture records an earlier implementation,
not the present handoff behavior.


The user-reported PCS alert is localized to route `00000043--29caa20fbc`,
segment 12, route offset **752.436552–752.922597 s**. Native FRC-side
`0x08A` **byte 4 bit 6** is asserted for 21 consecutive frames.

**Byte 7 is the Toyota checksum of the eight-byte prefix:**
`(0x8A + 8 + sum(B0..B6)) & 0xFF`. The former ID34→ID33 interpretation was
the checksum changing `0x8B→0x87` when byte 3 bit 2 cleared. Neither those
requester IDs nor the former lower-slot “Brake Only” allocation are fields.

| Phase | Frames | B3[2] | B4[6] | B7 checksum | Both acceleration slots |
|---|---:|---:|---:|---|---|
| immediately before | 1 witness | 0 | 0 | `0x47` | −4.000 m/s² |
| first flagged phase | 9 | 1 | 1 | `0x8B` | −4.000 m/s² |
| second flagged phase | 12 | 0 | 1 | `0x87` | −4.000 to −3.800 m/s² |
| immediately after | 1 witness | 0 | 0 | `0x47` | −3.800 m/s² |

B6 remains ID11/allocation 1. The native acceleration slots already contain
−4.000 m/s² **20.226 ms before** B4[6] asserts. B20 remains `0x40` throughout.

### Recorded chronology

Offsets below use the first B4[6]-asserted receive batch:

| Offset | Observation |
|---:|---|
| −188.123 ms | prior native `0x5AE` has byte 2 bit 2 clear |
| −20.226 ms | prior native `0x08A` has B4[6] clear and both slots at −4.000 m/s² |
| 0.000 ms | `0x5AE` warning bit asserts at CAN-array index 16; flagged `0x08A` follows at index 28; forwarded `0x5AE` TX return is index 36 |
| +14.464 ms | second flagged native `0x08A`; neither of the first two has a bus-0 TX confirmation |
| +16.733 ms | first logged driver-brake press |
| +19.717 ms | openpilot disables on `pedalPressed/userDisable` |
| +33.508 ms | native forwarding resumes; the remaining 19 flagged frames are forwarded |
| +215.878 ms | B3[2] clears while B4[6] remains set |
| +486.045 ms | last B4[6]-asserted frame |
| +518.686 ms | first `0x08A` with B4[6] clear again |
| +646.872 ms | first `0x5AE` with its warning bit clear again |

`pandad` preserves Panda receive-buffer order within the CAN array. The
warning frame therefore precedes the flagged request in this batch; there
is no per-frame hardware timestamp for the sub-batch delay.

Across the retained September-21 corpus of **44 rlogs**, the warning bit is
set on four of **12,981 native `0x5AE` frames**, all in this segment. The
21 B4[6]-asserted `0x08A` frames are likewise confined to this event.

Immediately before entry, openpilot longitudinal is active and requests
−1.5 m/s²; vehicle speed is 7.691 m/s and neither pedal is pressed. The
last accepted replacement is at −7.941 ms. A final host replacement is
submitted at +15.685 ms and rejected at +22.175 ms. Forwarding resumes
after the pedal disable, rather than demonstrating a PCS-triggered handoff
while longitudinal remains active.

All four asserted `0x5AE` frames are forwarded from warning onset. The
separate warning path explains how the driver can receive a PCS alert while
replacement ownership suppresses the beginning of the native request-plane
transition.

Brake/VMM `0x081` remains longitudinal result ID11 across all 17 result
frames in the flagged interval, with request-loss supervision clear.
Its B20:B21 scalar spans −0.427 to −0.401 m/s²; the
[VMC status analysis](camry-2026-longitudinal-evidence.md#2026-09-30-vmc-status-corpus)
identifies that as a closed-accelerator reference candidate. No lower
requester ID is available to compare with the result.

### Meaning and ownership boundary

The user report, coincident warning, and native B4[6] transition establish
a **PCS-associated state**. Its exact OEM stage remains unmapped.
Toyota's shipped PCS Data Viewer distinguishes `15E5_9` Prefill Request
Flag, `15E6` PCS brake request status, `15E7` PBA Request Status, and
`1607_9` PCS Emergency Brake Activation Flag. These are recorder fields,
not a CAN mapping for B4[6]. Likewise `PCS2_P5` DID `0x100E` names warning
display requests without mapping `0x5AE` byte 2 bit 2.

The ownership consequence is unchanged: when yielding to this native
PCS-associated state, pass the **original authenticated `0x08A` frame**
untouched rather than synthesizing its payload. The recording proves the
then-active replacement blocked the first two flagged frames. Corrected
handoff timing and the exact PCS stage require their own evidence; the
unchanged result ID11 does not identify that stage.

Evidence:
`data/generated/camry_20260921_pcs_alert.json` (v3),
`tools/targets/camry/analysis/analyze_camry_20260921_pcs_alert.py`,
`tests/targets/camry/verify_camry_20260921_pcs_alert.py`,
`data/generated/gtsplus_2026/pcs_data_viewer_adu_semantics.json`, and
`software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/PCS Data Viewer/en-US/PCS Data Viewer.resources.dll`.
