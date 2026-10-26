# Toyota TSS3 field witnesses

**Issue:** [commaai/opendbc#3695 — Toyota TSS3 car port](https://github.com/commaai/opendbc/issues/3695)

This report owns the measured results and provenance of the named captures.
The [capability matrix](camry-2026-capability-matrix.md) owns current port status.

## Camry lateral: direct route evidence

### September 18 coexistence result

Route `0000010c--506d7277c7` records the C7-era exact-Camry integration. It was captured immediately after the parked same-ignition recovery sequence
that selectively reset **Brake/EPB first and FRC second** while leaving the EPS
RAM-resident lateral helper powered. Across 30 rlogs / 1,743.811 s, the route contains
13 openpilot lateral-active episodes totaling **919.594 s** and **19.772 km**.
Stock adaptive cruise overlaps those intervals for **919.572 s**; all 91,707
cruise-enabled `carState` samples are adaptive (`nonAdaptive=false`), while
`carControl.longActive` is never asserted.

This route measures lateral operation alongside normal Toyota DRCC. There are 91,570 active functional-C7 commands;
91,568 receive successful Panda TX returns. The two rejected nonzero C7 frames occur
only after `latActive` has already fallen false at disengagement transitions. Active
sequence progression has zero mismatches, with a 9.845-ms median / 13.523-ms p99
inter-command interval. Target angle spans -31.746..25.328 deg and measured steering
-31.3..24.8 deg. Across the full active population the best tested command lead is
260 ms, with **r=0.9939** and **0.505-deg MAE**; with `steeringPressed=false` and
|driver torque|<=0.5 N.m, the result is **r=0.9962 / 0.455 deg**.

Toyota's own request/result traffic separates the two controllers. During openpilot
`latActive`, all **36,779** native `0x08A` lateral request IDs and all **30,652**
`0x081` lateral result IDs are `0` (No Request / manual lateral), while Toyota
longitudinal request IDs remain active. During the adaptive+latActive overlap,
`0x08A` B6's upper request-ID candidate is 11 on 36,777/36,779 samples,
and `0x081` returns longitudinal result ID11 on
26,339 samples. Raw cruise display `0x251 B0` is `0xC0` on 1,100 overlap frames and
`0xA0` twice, with zero historical conventional `0x88/0x90` frames. The route also
includes a **15.871-s** stop below 0.5 m/s while the adaptive+lateral overlap remains
selected.

No permanent steering fault occurs. Thirteen temporary-fault samples are confined
to segment 29 after the drive, in Park with `latActive=false`, alongside parked
shutdown TX rejects; they are not a road-control dropout. The route records openpilot
`2768fa575fe16e79e1b9817b2c33d76183a05dd0`, branch `tss3`, version `0.11.2`.
All 30 source-rlog SHA-256 values and the reduction are retained at
`targets/camry-2026/raw-20260918/recovered-road-drive/summary.json`; the raw rlogs/qlogs
are archived outside git at
`/Users/kai/dev/inspect/logs/camry-2026/2026-09-18/0000010c--506d7277c7/`.

### September 10 authority result

Route `0000008d--a9f348691a` is the primary working-lateral record. Across 11
segments it contains eight lateral-active episodes totaling 167.289 seconds and
8,333 fresh active C7 angle commands at nominal 50 Hz. Panda returned 8,332 as
successfully transmitted and rejected one. The route spans repeated positive and
negative commands, with active C7 target angle covering -26.990..21.890 degrees
and measured steering covering -26.5..23.1 degrees. No EPS temporary or permanent
steering fault asserted during lateral-active state.

The cleanest low-driver-input witness is the 36.105-second lateral-active portion
of segment 6:

| Witness | Direct segment-6 result |
|---|---:|
| `carControl.latActive` samples | 3,596 |
| Active C7 `sendcan` frames | 1,799 |
| Active C7 successful Panda returns | 1,799 |
| Active C7 rejected returns | 0 |
| C7 target-angle range | -11.690..17.420 deg |
| Measured steering-angle range | -9.4..15.6 deg |
| Target/measured Pearson correlation | 0.989 at 400 ms tested lag |
| Target/measured mean absolute error | 0.873 deg at that lag |
| `carState` samples in interval | 3,595 |
| Driver `steeringPressed` samples | 38 (1.06%) |
| Absolute driver torque | 0.15 N.m median; 0.42 N.m p95; 0.97 N.m max |
| EPS temporary/permanent fault samples | 0 / 0 |

The command lead, repeated target/measured response, low driver torque, clean EPS
state, and inactive Toyota request plane establish **observed openpilot lateral
control**.

### Corroborating result

The later route `00000093--4066e7ae51`, segment 3 independently repeats the result
over one continuous 17.92-second interval at 10.61..10.94 m/s: 893/893 active C7
commands have successful Panda returns, target/measured correlation is 0.997 at the
tested 400-ms lag with 0.994-degree mean absolute error, driver torque is 0.23 N.m
median / 0.47 N.m p95 / 0.67 N.m max, and no EPS steering fault asserts. Its target
spans -3.954..20.228 degrees and measured steering spans -4.0..17.8 degrees.

### Toyota LTA was off

Across all eight primary-route lateral-active episodes, all 6,689 native bus-2
`0x08A` request frames and all 5,577 native bus-0 `0x081` result/reference frames
have Target Lateral ID `0`, which Toyota's recovered dictionary defines as **No
Request (Manual Operation)**. There are no native ID11 LTA/LCA requests or results
during the openpilot steering intervals. The corroborating route independently
repeats this with 717 `0x08A` and 597 `0x081` ID0 frames during its active interval.

This matters because the wheel response cannot be assigned to simultaneous
factory LTA. Openpilot was engaged from normal non-adaptive cruise after EPS
programming had made stock TSS/DRCC unavailable for that ignition cycle.

### Source integrity and scope

All 11 primary-route rlogs were copied from the comma on 2026-09-11 and SHA-256
inventoried in the retained session summary. The clean segment-6 witness is
`87ec47f75bf4ab45463cd70dbc0ba79e5aa339f9ec55493629931499c6fb4832`.
The local copy is intentionally outside git under
`/Users/kai/dev/inspect/logs/camry-2026/2026-09-10/0000008d--a9f348691a/`.

Both routes record openpilot parent
`ddd1f6fac47e636c6b5ec470849350587ee04272`, branch `kai`, version `0.11.2`,
and `dirty=true`. Their captured `GitDiff` is byte-identical, SHA-256
`e1caaf8276900c7aa64bb44e7f7e1a272e6026d432d7e654e1e530d4a6b6a705`, so the
later `93` route corroborates the same steering build and configuration.
The dirty state is material: the working C7 opendbc delta was not
part of base commit `baec01c15ac3fdf7361f862a483ad3a06e1f985a`.

The corroborating route's segment-3 evidence remains byte-identical to its retained
inventory. Its current comma segment 6 differs from the contemporaneously inventoried
copy, so its historical full-route totals remain pinned rather than recomputed; that
does not affect the segment-3 corroboration.

## Attributed Corolla field report

On 2026-09-10, albinoelephant reported a 2023 Corolla TSS3 drive with Toyota
safety active, 23,683 host `0x160` transmissions at 40 Hz, and observed lead
following. A later pass faulted at standstill. The contributor's description is
retained under `community/albinoelephant/`; the
[Corolla report](corolla-8965F1208000.md) owns the target-specific assessment.

The [longitudinal report](camry-2026-longitudinal-evidence.md) owns the
request/result interpretation.
