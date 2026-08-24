# Pre-TSS3 Corolla openpilot message contract vs. 2023/2025 EPS

> **Document type:** cross-generation communication comparison
> **Status:** active porting evidence
> **Upstream:** commaai/opendbc canonical pin `c9b31d21bc396e8958891e271936bdbdf1a6ca93`; current upstream `7343a66d46213d5f73528afc6c6db713ebd88a9d` checked 2026-08-23
> **Target images:** Albino `8965H1202000` (reported 2023 US Corolla) and Span `8965F1208000` (2025 Corolla acquisition)

This report answers a narrower question than the generic Toyota prior-art report:
**what does openpilot actually use on pre-TSS3 Corollas, and what survives in our
newer Corolla EPS applications?**

The machine-readable upstream contract is
[`../../data/external/opendbc/toyota_corolla_pre_tss3_contract.json`](../../data/external/opendbc/toyota_corolla_pre_tss3_contract.json).
The exact-image comparison is
[`../../data/generated/corolla_pre_tss3_opendbc_message_comparison.json`](../../data/generated/corolla_pre_tss3_opendbc_message_comparison.json).

## 1. First correction: the Corolla baseline is not the Sienna SecOC baseline

Neither pre-TSS3 Corolla profile in current openpilot/opendbc is a SecOC platform.
The two relevant profiles are:

| openpilot profile | Toyota generation | steering | longitudinal |
|---|---|---|---|
| `TOYOTA_COROLLA` | 2017–19 | torque/LKA | stock longitudinal; openpilot only sends cancel |
| `TOYOTA_COROLLA_TSS2` | 2020–22 | torque/LKA | camera-originated ACC replaced by openpilot |

Therefore **`0x131 STEERING_LTA_2` and `0x183 ACC_CONTROL_2` are not part of the
pre-TSS3 Corolla contract at all.** They are useful Toyota SecOC prior art for
other platforms, but including them in a Corolla-generation diff obscures the
actual migration.

The current upstream checkout at `7343a66d…` has the same Corolla wire contract
as the canonical `c9b31d21…` pin. The intervening Toyota changes replace model-set
membership tests with equivalent platform flags and add firmware-version regex
handling; the Corolla DBC definitions, builders, safety rules, message IDs/DLCs,
and cadences below are unchanged.

## 2. What openpilot transmits on pre-TSS3 Corolla

### 2.1 Lateral command: `0x2E4 STEERING_LKA`

Both Corolla generations use the classic **5-byte `0x2E4` torque command**.
openpilot emits it every control update (100 Hz) and Panda applies the Toyota
torque envelope. This is the active steering actuator interface on both Corolla
profiles.

The controller also uses EPS/driver feedback when calculating the command:
`0x260 STEER_TORQUE_SENSOR`, steering rate from `0x025`, and the `0x262`
`LKA_STATE` fault interface. In other words, the old Corolla lateral contract is
not just `0x2E4`; it is the closed loop `0x025 + 0x260 + 0x262 -> 0x2E4`.

### 2.2 TSS2 coexistence: `0x191 STEERING_LTA`

TSS2 Corolla additionally emits `0x191` at 50 Hz. **It is not the active Corolla
steering path.** `TOYOTA_COROLLA_TSS2` remains torque control, so openpilot sends
this frame neutral/inactive: no LTA request, zero angle, and zero torque wind-down.
Panda treats it as a replaced stock-camera message.

That distinction matters for the newer firmware: disappearance of `0x191` does
not imply that we need to find a replacement angle-command interface.

### 2.3 Longitudinal: `0x343 ACC_CONTROL`

The two Corolla profiles differ materially here:

- 2017–19: stock longitudinal remains in charge; openpilot uses `0x343` only to
  request cruise cancel with inactive acceleration.
- 2020–22 TSS2: the **forward camera is the stock ACC source**, and openpilot
  replaces its `0x343` command at about 33.3 Hz with acceleration, braking
  permission, standstill/release, cancel, ACC type, lead/distance, and related
  state.

This is a whole-vehicle camera/ACC contract. It is not an EPS-local interface.

### 2.4 Driver UI: `0x412 LKAS_HUD`

Both profiles send `0x412` at 5 Hz, plus immediate sends on relevant alert/cancel
edges, while preserving selected camera-originated HUD state. This too is a
whole-vehicle camera/cluster contract rather than an EPS-local one.

## 3. The old Corolla state/safety messages that matter most

The full tracked snapshot contains every `CarState` message. For the EPS/control
migration, these are the important ones:

| role | old Corolla message | old wire shape | why openpilot needs it |
|---|---|---:|---|
| steering angle/rate | `0x025 STEER_ANGLE_SENSOR` | 8-byte classic | angle, fraction, steering rate |
| wheel speed / safety | `0x0AA WHEEL_SPEEDS` | 8-byte classic | ego speed + wheel validity; Panda safety input |
| driver/EPS torque + accurate angle | `0x260 STEER_TORQUE_SENSOR` | 8-byte classic | driver override, EPS torque limiting, accurate angle/init |
| EPS readiness/fault | `0x262 EPS_STATUS` | 5 bytes pre-TSS2 / 8 bytes TSS2 | `LKA_STATE` temporary/permanent faults |
| cruise engagement | `0x1D2 PCM_CRUISE` | 8-byte classic | cruise-active state; Panda controls-allowed input |
| brake | `0x224` old / `0x226` TSS2 | 8-byte classic | brake disengagement; Panda safety input |

TSS2's 8-byte `0x262` also defines `LTA_STATE`, but Corolla TSS2 is not angle
control, so openpilot's Corolla steering-fault decision remains based on
`LKA_STATE`.

## 4. Albino 2023 vs. Span 2025: there is no application-level message delta

This is stronger than a structural similarity result. After normalizing the two
CodeFlash acquisitions, the entire application region
**`0x00020000..0x000FFFFF` is byte-identical**:

- application size: 917,504 bytes;
- H application SHA-256: `2ccb79cda1e8689ec91c389d3d7e3921c010ddc9c9d917f23c1705916a0e0d7f`;
- Span/F application SHA-256: the same;
- changed application bytes: **0**.

The two complete normalized images differ below the application region, including
boot/identity/calibration material. Those low-region differences do not create a
2023-versus-2025 application CAN contract difference. Every active application
Rx/Tx conclusion below applies equally to Albino and Span.

## 5. Exact newer-EPS message migration

### 5.1 `0x025`: same semantic role, new CAN-FD wire contract

The H/F application still has an active receive descriptor for **`0x025`**, but
it is now **32-byte CAN-FD**, not the old 8-byte classic frame.

This is not an ID-only guess. H target-native recovery independently proves the
same steering-sensor semantics:

- signal 184: signed 12-bit coarse steering angle;
- signal 185: signed 4-bit fractional component;
- signal 186: signed 12-bit steering rate;
- `0xC2176` reconstructs high-resolution angle as the coarse term plus fraction;
- `0xCB2E0` treats the rate value as steering-rate magnitude; and
- `0xCBD7E` jointly consumes angle and rate in plausibility logic.

**Porting consequence:** `0x025` is a very high-confidence bridge from old Corolla
openpilot to the newer vehicle, but its old 8-byte DBC must not be reused. We
need a TSS3 32-byte FD definition containing the already-proved angle/rate fields.

### 5.2 `0x0AA`: same ID and same 8-byte classic descriptor

The H/F application also still receives **classic 8-byte `0x0AA`**. That is the
same ID and DLC as pre-TSS3 Corolla `WHEEL_SPEEDS` and is therefore an excellent
capture/DBC starting point.

This comparison deliberately stops short of claiming identical bit offsets from
ID/DLC continuity alone. The old field layout should be validated against the
new vehicle before it is used for `CarState` or Panda safety.

### 5.3 `0x260 + 0x262`: removed; newer EPS transmits 32-byte FD `0x030`

The H/F generated Tx table is exactly:

`0x030(FD), 0x351, 0x394, 0x4A3, 0x4C8`

The older firmware-family table instead had separate `0x260` and `0x262` EPS
outputs before the shared `0x351/0x394/0x4A3/0x4C8` tail. The H/F `0x030` PDU is
32 bytes and has 37 configured generated signals.

Thus the two exact messages that pre-TSS3 Corolla openpilot uses for
**driver/EPS torque + accurate angle (`0x260`)** and **EPS LKA readiness/fault
state (`0x262`)** are no longer transmitted by this EPS generation. FD `0x030`
occupies the new generated-feedback slot, but later target-native recovery shows
that the surviving classic `0x4A3/0x351/0x394` messages preserve clearer pieces
of those state roles; `0x030` is a mixed telemetry/status/validity carrier rather
than a proved monolithic `0x260+0x262` replacement.

The existing H-native field census already proves substantial runtime-produced
content inside `0x030`, including steering-angle-like coarse/fraction packing,
scaled control/sensor fields, status bits, and an exact byte-7 additive field.
However, this report does **not** prematurely label individual `0x030` fields as
`STEER_TORQUE_DRIVER`, `STEER_TORQUE_EPS`, or `LKA_STATE` without a direct
semantic join.

**Porting consequence:** do not treat FD `0x030` as a monolithic `0x260/0x262`
replacement. H `0x4A3` is already the clearest state bridge: it carries steering
angle, a source joined to Techstream **Steering Wheel Torque**, and motor Q-current
response. `0x351/0x394` are the strongest readiness/fault candidates. Decode only
the remaining `0x030` validity/control-state fields needed to complete CarState and
Panda safety, and derive H/F-native scales rather than copying old Corolla values.

### 5.4 `0x2E4`: torque control is replaced by protected B6 target-angle control

The complete H/F normal-Rx descriptor table has **no `0x2E4`**. The secured
application profile set is `0x00F / 0x0D7 / 0x0B6`, also with no classic `0x2E4`.
The retained Sienna-shaped torque-clamp input (`C91B6` / `AE12`) remains zero-fed,
so this is not an encoded or merely signed version of the old torque command.

The corrected fixed-map audit instead finds the H/F receiver contract on protected
CAN-FD `0x0B6`:

- **signal 254**, B3, unsigned 6-bit: control/profile ID. Its hidden GP-relative
  snapshot reaches `FEBEADB0`, and `0xCBE6E` decodes values `1/4/10/11/19` into
  five mutually exclusive cooperative-control profiles with distinct calibration
  banks;
- **signal 255**, B4:B5, signed16: target steering-angle command. It follows
  `FEBE7D94 -> FEBEF1CC -> FEBEAE82`;
- `0xC9DB0/0xC9E54` turn signal 255 into target state while `0xCBD7E/0xCB096`
  independently reconstruct the measured angle from FD `0x025`;
- FD025 signal184 is 1.5 deg/count through the exact H DID `0x1037` + Techstream
  P5 conversion record; signed4 signal185 supplies a 0.1-deg fraction; therefore
  the matched controller closes signal255 at **`1024/17870 deg/count` =
  `1.000121519... mrad/count`** controller-equivalent scale;
- `0xCA138` applies the same gain to both and computes target minus measured; and
- that error drives the steering controller, ultimately contributing to Techstream
  DID `0x1C02` **Command Value Torque** and DID `0x1152` **Command Value Current
  (Q Axis)**.

B6 signals 262/263 are additional 8-bit percentage-like modifiers on internal
controller contributors. Techstream identifies the immediate monitored source
relationship as **Brake System Control Module** traffic (U012987). Its exact P5
`Target Lateral ID` dictionary closes H signal254 values as **`1=PCS`, `4=LDA`,
`10=Hands Off LTA`, `11=LTA/LCA`, `19=PDA`**; the H-special values `25/27` are
**AP/Remote Parking**. `Target Steering Angle After Output Compensation` remains
observer-side family vocabulary because exact H lacks the corresponding `0x1CEE`
DID.

**Porting consequence:** the old Corolla command API did not merely move IDs; it
changed from classic torque command to protected target-angle control. Do not port
`0x2E4` limits or scaling. Signal255's controller-equivalent scale and signal254
feature labels are now closed; before any injection, recover request/validity
semantics, cadence/timeouts, SecOC freshness/key behavior, stock-source suppression,
and H/F-native safety bounds. The literal OEM B6 engineering-unit name remains
unjoined even though the degree/radian scale is known.

### 5.5 `0x191`: gone, but it was not Corolla's active steering path

H/F has no `0x191` normal-Rx descriptor. Since pre-TSS3 Corolla openpilot only
sent neutral `0x191` while actually steering with `0x2E4`, this does not create a
new “find LTA angle command” requirement by itself.

### 5.6 `0x343` and `0x412`: EPS absence is intentionally non-diagnostic

Neither appears in the H/F EPS application Rx/Tx tables. That does **not** mean
the newer vehicle abandoned those semantic roles. Pre-TSS3 Corolla used them in
the camera/ACC/cluster integration, not as EPS-local steering messages.

Their TSS3 replacements must be recovered from whole-bus captures and the
relevant FRC/radar/brake/gateway firmware. An EPS dump cannot settle them.

## 6. Compact migration matrix

| semantic contract | pre-TSS3 Corolla | H/F application | interpretation |
|---|---|---|---|
| steering angle/rate | `0x025`, 8B | `0x025`, **32B FD** | **role survives; wire format changed** |
| wheel speeds | `0x0AA`, 8B | `0x0AA`, 8B | strong continuity lead; validate fields |
| driver/EPS torque + accurate angle | `0x260`, 8B TX from EPS | no `0x260`; **`0x4A3` + FD `0x030`** | roles split across newer state carriers |
| EPS readiness/fault | `0x262`, 5/8B TX from EPS | no `0x262`; **`0x351/0x394` + FD `0x030`** | recover H/F-native state meanings |
| active lateral steering command | `0x2E4`, 5B torque RX | **protected FD `0x0B6` signal 255 target angle** | control law + protection generation changed |
| TSS2 neutral LTA coexistence | `0x191`, 8B | absent | not evidence of lost active angle control |
| longitudinal command/source replacement | `0x343`, 8B | absent from EPS | EPS-local comparison is non-diagnostic |
| lane/HUD replacement | `0x412`, 8B | absent from EPS | EPS-local comparison is non-diagnostic |
| secure LTA/ACC companion | `0x131` / `0x183` | irrelevant to baseline | **not pre-TSS3 Corolla prior art** |

## 7. What this changes in the TSS3 roadmap

The pre-TSS3 Corolla implementation gives us two immediate, concrete work items
that are more useful than another generic EPS search.

**First, finish the feedback side using the recovered state bridge.** Start with
`0x4A3` for angle / driver-torque-source / motor-Q-current response, correlate
`0x351/0x394` against readiness and fault transitions, and then decode the subset
of FD `0x030` needed to close remaining validity/control state. The target-native
recovery is documented in
[corolla-h-f-openpilot-state-bridge.md](corolla-h-f-openpilot-state-bridge.md).
This is more direct than treating all 37 `0x030` fields as equally likely old
`0x260/0x262` replacements.

**Second, characterize the recovered B6 command contract rather than searching for
another message.** Protected `0x0B6` signal 255 is the H/F target-angle ingress at
`1024/17870 deg/count` controller-equivalent scale, and signal 254 selects the
now-labeled `PCS/LDA/Hands Off LTA/LTA-LCA/PDA` profiles. The next dynamic work is
to correlate those fields with stock LTA, `0x1C02`, `0x1152`, measured steering
angle, and B6 validity to recover cadence/timeouts, request/validity semantics, and
production bounds. `FRC_P5` plus Brake/EPB/gateway analysis remains high priority
for the **upstream producer and SecOC/routing contract**, not for discovering the
EPS receiver setpoint, physical scale, or profile labels.

Longitudinal and HUD remain separate whole-vehicle workstreams. The old Corolla
prior art tells us exactly what roles must eventually be replaced, but the EPS
firmware does not identify their TSS3 wire messages.

## 8. Evidence and verification

- `tools/build_corolla_pre_tss3_message_comparison.py` rebuilds the exact H/F
  application identity, normal-Rx table, Tx table, and role migration report.
- `tests/verify_corolla_pre_tss3_message_comparison.py` enforces the upstream
  Corolla baseline and target-native migration conclusions.
- `data/generated/corolla_8965H1202000_fd_control_interface.json` provides the
  exact H FD `0x030` / `0x0B6` generated-interface evidence.
- `data/generated/corolla_8965H1202000_lta_command_provenance.json` and
  `data/generated/corolla_8965H1202000_b6_target_angle_ingress.json` provide the
  target-native `0x025` sensor proof and protected-B6 target-angle command proof.
- `data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json`
  proves the H/F application-byte identity.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [COM-008](../reference/index.md#finding-com-008)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
