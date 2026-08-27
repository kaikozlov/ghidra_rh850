# Corolla H/F openpilot state bridge

This report narrows the newer-Corolla port from “decode the new Toyota messages”
to a concrete set of state carriers and remaining command-provenance questions.
It applies to Albino's `8965H1202000` and Span's `8965F1208000`: their complete
`0x20000..0xFFFFF` application regions are byte-identical, so the application
message implementation described here is shared.

The evidence order is deliberate:

1. exact H CodeFlash bytes and generated COM/PDU configuration;
2. H-target decompiler dataflow bound back to raw function-body hashes;
3. Toyota Techstream P5 monitor names/DIDs for the same H-native state;
4. old Corolla openpilot/opendbc only as the list of roles a usable port must
   recover.

A structural match to the older Sienna is corroboration. It is never sufficient
on its own to transfer an OEM meaning, scale, limit, or fault code.

## 1. What old Corolla openpilot actually needs from the EPS

The pre-TSS3 Corolla contract uses three important EPS-facing state messages:

- `0x025 STEER_ANGLE_SENSOR`: steering angle, fraction, and steering rate;
- `0x260 STEER_TORQUE_SENSOR`: driver steering torque, EPS steering torque,
  accurate steering angle, and angle-initialization state;
- `0x262 EPS_STATUS`: steering readiness/fault state through `LKA_STATE`.

Panda safety also directly depends on the driver/measured-torque state that old
Toyota exposes through `0x260`. Therefore discovering the new steering command is
not enough. A production port needs generation-native equivalents for driver
intervention, actual actuator response, sensor validity, and steering faults.

The old numeric `LKA_STATE` fault values and old Toyota torque limits are search
references only. They are **not portable constants** for H/F.

## 2. Exact H/F transmit generation

H/F no longer transmit `0x260` or `0x262`. The exact application COM Tx family is:

| PDU | CAN | Length | Raw descriptor first field | Role after this analysis |
|---:|---:|---:|---:|---|
| 0 | `0x030` FD | 32 B | `2` | live driver torque + telemetry/status/validity |
| 1 | `0x351` | 4 B | `200` | motor-B terminal-voltage fault/status family |
| 2 | `0x394` | 3 B | `60` | 17-state EPS fault/status projection |
| 3 | `0x4A3` | 8 B | `100` | alternate steering telemetry / Q-current bridge |
| 4 | `0x4C8` | 8 B | `196` | not needed for the conclusions here |

The raw first descriptor field is intentionally not converted into milliseconds
or Hertz here; its scheduler unit has not been established by this report.

The important correction to the previous priority is that `0x030` is **not the
only, or even the clearest, replacement-state target**. Three classic IDs survive
and preserve useful control-state architecture.

## 3. `0x4A3`: the strongest state bridge

The H producer chain is target-native and compact:

- `0x46C4C` prepares steering/torque/current-derived state;
- `0x46D9A` stages the eight `0x4A3` bytes;
- `0x4749A` packs PDU 3 into the CAN payload.

All three functions are bound to exact H raw-body hashes. They also have unique
instruction-shape homologs in the older Sienna image, but the semantics below come
from H dataflow and Techstream, not from that structural similarity.

### 3.1 Wire map recovered so far

| H `0x4A3` field | H-native source | Meaning now closed |
|---|---|---|
| B0[5] | constant `1` from `FEBE7DAE | 0x20` | constant marker bit |
| B0[0] | `FEBE7DAE` | selected steering fault/inhibit status aggregate; the same source is live on `0x030` B6[2] and is not an exhaustive EPS-fault state |
| B1:B2 | `FEBE7D34` | mirror of FD `0x025` signal184, signed12 steering angle at 1.5 deg/count |
| B3:B4 | `FEBE7A46` | DID `0x1037` **Steering Angle**, also 1.5 deg/count |
| B5 | `FEBE6554 -> trunc(*100/0x100) -> trunc(/10) -> signed-byte saturation` | DID `0x1035` **Steering Wheel Torque**, 0.1 N·m/count |
| B6:B7 | `FEBE6592 * -100 / 0x80`, big-endian signed16 | DID `0x1151` **Motor Actual Current (Q Axis)** with packet sign inverted, -0.01 A/count |

The torque scale is now closed rather than inferred from display precision. H DID
`0x1035` computes `(FEBE6554 * 1000) / 0x100`; Techstream defines the DID as signed
N·m with three decimal places. Therefore `FEBE6554 / 256` is N·m. The `0x4A3` B5
producer first forms `trunc(FEBE6554 * 100 / 256)` and then divides by ten before
signed-byte saturation, so one packet count is the intended **0.1 N·m** quantum.

The Q-current scale is also closed. DID `0x1151` computes
`(FEBE6592 * 100) / 0x80`, and Techstream displays the signed result in amperes with
two decimal places. `0x4A3` applies the same magnitude conversion with the opposite
sign. Thus B6:B7 is **-0.01 A/count** relative to Techstream's Q-axis-current sign
convention. It is actuator-current response, not the old `STEER_TORQUE_EPS` signal.

### 3.2 Port consequence

`0x4A3` is no longer required to obtain driver torque because live `0x030` carries
the same native torque source. It remains valuable as an alternate torque carrier,
a Q-axis actuator-response carrier, and a cross-check for the EPS fault aggregate.
Neither tracked moving route carries `0x4A3`, so its packet fields remain
firmware/Techstream-static until a relay-correct H/F capture observes them.

## 4. `0x351`: mixed status with a C159B49-linked electrical-monitor path

The earlier "generic plausibility/readiness candidate" description was incomplete.
The target-native upstream path is now joined through the H Dem table to Techstream:

- `0xB87E8` computes the C159B49-linked electrical-monitor predicate, reports Dem
  event `4` when it asserts, and stores its boolean at GP-`0x2EC` = `FEBEB514`;
- `0xBBA48` copies `FEBEB514 -> FEBEE82B`; `0x46E0C` propagates that monitor
  boolean while maintaining the exact seven-count transition state. The H calibration
  byte at `0x2B930` is `7`;
- separately, `0x3738C -> 0x472E0` supplies `FEBE7E13` from a bit-15 path;
- `0x46E62` normally stages the `0x46E0C` result, but when `(FEBE65E4 & 3) != 0`
  and `FEBE7E13 != 0`, it force-writes status code `7` and companion flag `1`.
  `0x47BA2` packs B2[7:5] and B2[4].

Dem event 4 selects enabled H DTC index 54, packed DTC `0x559B49`. Techstream
`EMPS_P5` names it **C159B49 — Power Steering Motor "B" Terminal Voltage Detect
Circuit / Internal Electronic Failure**.

The exact wire fields are still B2[7:5] = `FEBE7DD0` and B2[4] = `FEBE7DD1`.
C159B49 therefore names one upstream **base-status path**, not the whole `0x351`
packet or the separate force-7 condition. This is a mixed status carrier; it is not
a generic EPS-ready or old `LKA_STATE` replacement. Current tracked routes contain
no `0x351`, so the base path, force-7 override, and their asserted/clear transitions
remain to be captured on-vehicle.

## 5. `0x394`: exact 17-state EPS fault/status projection

`0x4B9AE` is the H classifier. It consumes startup latches, self-test results,
per-fault-class counters/latches, and operational predicates, then selects one row
from the 17×5-byte table at `0x29D54`. The homologous Sienna table at `0x2A33C` is
byte-identical. `0x46E96` projects the selected row into transmit staging, and
`0x47ADA` packs:

- B1[7:6] = table column 4 through `FEBE7F65 -> FEBE7DD5`;
- B1[5:3] = table column 1 through `FEBE7F62 -> FEBE7DD6`;
- B2[3:1] = table column 2 through `FEBE7F63 -> FEBE7DD7`;
- B2[0] = table column 3 through `FEBE7F64 -> FEBE7DD9`.

The classifier recovers an important state boundary. State `0` is reached by
the deepest clear/normal path only after the preceding aggregated fault-class branches
are clear and additional operational predicates pass. Its transmitted tuple is all
zero and is unique in the table, but this is **not** evidence that state 0 is the exact
Techstream `Ready Status` boolean or is by itself sufficient to authorize steering. States `1/2` are startup/settling holds; state `3` is selected
by the internal self-test/input-invalid branch; states `6..14` are active
fault/inhibit branches; state `15` is a distinct special operating state; and state
`16` is the fallback/not-normal branch. Table rows `4/5` remain present but are not
directly selected by the recovered classifier body.

Two limits matter. First, some nonzero internal states collide on the transmitted
four-field tuple, so the wire message is a status projection, not a lossless state
ID. Second, nothing in the recovered firmware maps these classes to openpilot's
`steerFaultTemporary` versus `steerFaultPermanent` contract. Treating every nonzero
state as one of those two categories would be an invention. State 0 is a useful future clear/normal discriminator candidate once routing and
Ready/LTA correlation are observed; temporary/permanent classification still requires
dynamic DTC/Ready/LTA evidence.
Current tracked routes contain no `0x394` frames.

## 6. `0x030`: live driver torque and fault/validity state

H `0x030` is 32-byte CAN-FD with 37 configured signal IDs (`0..36`). The packer
emits IDs `0..34`; IDs `35/36` are configured without a recovered direct pack call.
Signal 9 at B7 is exactly the low byte of `sum(payload bytes 0..6) + 0x38`.
Every one of Span's 6,000 moving `0x030` frames satisfies this H/F rule.

### 6.1 Correction to the writer census

The earlier direct textual-reference census incorrectly called eleven packed fields
"default-init-only". The same representation problem that affected the B6 command
path applies here: `0x47188` and `0x47430` write them through
`GP=0xFEBEB800 + constant offset`, so their absolute RAM names do not appear in the
assignment text. Exact image-bound recovery now closes runtime writers for signal
IDs **0, 1, 10, 14, 16, 17, 18, 27, 28, 31, and 34**. Among packed IDs `0..34`
there are now zero fields left in the false `default-init-only` class. This is a
positive correction for those eleven addresses, not a claim that arbitrary
computed-pointer mutation is globally impossible.

### 6.2 Live Steering Wheel Torque

Signals 0, 10, and 31 are three encodings of the same native torque intermediate
that also feeds `0x4A3` B5 and DID `0x1035 Steering Wheel Torque`:

- signal 0 = B0 signed8, a saturating truncation-toward-zero 0.1 N·m view;
- signal 10 = B8 signed8, the coarse component used for exact decimal
  reconstruction;
- signal 31 = B17[3:0] signed4, the signed hundredths remainder.

The exact reconstruction is:

`Steering Wheel Torque [N·m] = signed(B8) * 0.1 + signed4(B17[3:0]) * 0.01`

Span's 6,000-frame moving capture exercises **536 distinct values from -8.23 to
+2.85 N·m**. The fine nibble takes exactly `-5..+5`. Signal 0 and signal 10 differ
only by the expected rounding delta `-1/0/+1` coarse count; they are therefore not
byte-for-byte duplicates. This gives the read-only port a live, physically scaled
driver-torque observable without requiring unseen `0x4A3`.

### 6.3 Live safety-relevant gates

Two additional fields have target-native producer semantics and live nominal
polarity:

- signal 6, B6[2] from `FEBE7DAE`, is a **selected steering fault/inhibit
  status aggregate**, not an exhaustive EPS-fault bitmap. The same source is exported
  as `0x4A3` B0[0]. Span: `0` in 6,000/6,000 frames;
- signal 8, B6[0] from `FEBE7DB2`, is the driver-torque invalid/inhibit gate. The
  same producer condition suppresses the `0x4A3` driver-torque staging value.
  Span: `0` in 6,000/6,000 frames.

B6[1] is independently live (`0/1`) in Span, and its exact-H source is now closed:
`FEBE6BAE` **Motor Actual Current (Q Axis)** is snapshotted through
`FEBEEC0C/FEBEAFC4`, absolute-valued by `0xCF070`, thresholded at `0xBB8F6`,
debounced at `0xBB942`, then copied `FEBEB64C -> FEBEE848 -> FEBE7DB3 -> 0x030
B6[1]`. Exact H calibration `0xAEED8..0xAEEDF` is `5A 00 00 14 00 0A 00 00`:
feature flag `0x5A`, thresholds 5120/2560, debounce count 0. Under that calibration
the detector's enabled-only set branch is unreachable and its raw detector output is
forced clear each execution. Thus B6[1] is a **Q-axis-current-derived debounced status
whose exact-H threshold detector is calibration-disabled**, not a generic Ready or
authority bit. Span's 0/1 behavior remains cross-specimen evidence because its rlog is
not exact-F181-joined. B6[3] is runtime-produced and remains zero in that segment.
Signal 34 is separately a signed16 calibrated derivative of the same DID `0x1151`
Q-current source; its packet scale remains calibration-dependent.

The capture contains no induced EPS fault and no stock-LTA off→active→off
transition. Therefore the asserted operational consequences of B6[2]/B6[0] remain
firmware-static, and they do not justify guessing openpilot temporary/permanent
fault classes.

### 6.4 Ready Status is wire-visible on incoming `0x51E B0[7]`

Techstream DID `0x1033` is exactly **Ready Status**. The target-native H receive
path is now closed one step farther upstream than the earlier diagnostic-only
result. H Rx descriptor index 24 is classic `0x51E/8` (PDU29); its generated
COM signal154 is unpacked at `0x46144` from **`B0[7]` directly into
`FEBE7D1B`**. The downstream chain is exact:

`0x51E B0[7] -> FEBE7D1B -> FEBEF052 -> FEBEB5A8 -> FEBEE811 -> DID 0x1033 Ready Status`.

`FEBEF052 -> FEBEB5A8` is not an exclusive single-writer edge: exact-H
`0xBAB58` and `0xBAC16` both perform the operational copy, and the RAM nodes also
have initialization/reset writers. The Ready dataflow is therefore proved without
claiming exclusive-writer provenance.

The same field is observable in both retained TSS3 Corolla driving routes. The
public 2023 segment carries 59 `0x51E/8` frames and Span's 2025 moving segment
carries 60; **B0[7]=1 in every one**. This is strong operational-state
corroboration, but neither route exercises value `0`, so a Ready transition is
still required before using the bit as an openpilot engagement/fault classifier.
The join is an **incoming CAN Ready Status field**; it does not imply that
`0x030/0x351/0x394/0x4A3` republishes the same boolean on an EPS Tx PDU.


### 6.5 The cooperative system gate is a graded power-supply receive-validity/freeze state

The previously unnamed cooperative gate is now bounded substantially farther upstream.
Exact H writes shared state byte `FEBE7C58` from three calibrated monitor channels at
`0x44D84/0x44EC2/0x44FC4`, stages it once per scheduler cycle as
`FEBE7C58 -> FEBEF000` at `0x5262C`, and normalizes the staged value in the
`0xB8EEC` body to `FEBEACBD` with the exact mapping `0->0`, `2->2`, `3->4`, and
all other nonzero values -> `1`. Cooperative profile selection at `0xCBE6E` requires
`FEBEACBD==0` together with the independent B6 communication-health gate
`FEBEC26D==1`.

The three monitor classifiers are not B6-health logic. Their exact diagnostic joins
identify a **power-supply monitor subsystem**: `FEBE63B0` is exposed as IG Power
Supply, `FEBE63A6` is exposed under PIG Power Supply and Motor 1 Power Supply labels,
and `FEBE63A8` is Motor 2 Power Supply. The classifiers also consume unlabeled control
inputs (`FEBE63A4`, `FEBE65E4`, `FEBE7C5F`) and calibrated low/high windows. Firmware
therefore supports the bounded semantic name **graded power-supply
receive-validity/freeze state** for `FEBE7C58`; it does not justify inventing a
literal Toyota OEM name for `FEBE7C58/FEBEF000/FEBEACBD` or physical units for the
raw supply cells. B6 missing-message loss remains the separate
`FEBEADB9 -> FEBEC26D` path.

All cited monitor, scheduler, and normalization code lies in the H/F byte-identical
application region, so this contract transfers exactly to `8965F1208000`.
Machine-readable evidence:
`data/generated/corolla_8965H1202000_power_supply_monitor_gate.json` and
`data/generated/corolla_8965H1202000_power_supply_monitor_decompiler_evidence.json`;
deterministic verifier: `tests/verify_corolla_h.py`.

### 6.6 Normal H/F Tx exposes a coarse system-mode derivative, not exact cooperative authority

A wider direct/fixed-GP/computed-alias search found one useful missed wire-visible
path from the same raw state:

`FEBE7C58 -> FEBEF000 -> B23A2 -> FEBEB118 -> BBA48 -> FEBEE887 -> 470C6 -> 0x030`.

`B23A2` tests **`FEBEF000 < 2` as only one conjunct of a larger aggregate
predicate**. When the aggregate succeeds, `0x470C6` duplicates its boolean into
three `0x030` sources that the packer emits as **B6[3]**, **B10[3]**, and
**B13[4]**. These bits are therefore useful coarse system-status telemetry, but they
cannot be used as an exact cooperative-authority signal: raw mode `0` and raw mode
`1` both satisfy `<2`, while the exact normalizer produces `FEBEACBD=0` for mode 0
and `FEBEACBD=1` for mode 1, yielding opposite cooperative-gate outcomes.

The bounded search also covers the five configured normal H/F Tx PDUs
`0x030/0x351/0x394/0x4A3/0x4C8`, direct cooperative-root reads, simple fixed-GP and
computed aliases, all raw absolute pointer materializations of the profile flags,
and both fixed CodeFlash profile-pointer table families. The profile pointers feed
internal gain selectors; no discrete exact `FEBEACBD`/`FEBEC26D`/active-profile
authority bit is recovered on those five Tx PDUs. This negative does not exclude
arbitrary mutable runtime pointers, DMA/peripheral mutation, physical-response
inference, or another ECU assigning additional meaning to the coarse `0x030` bits.

Machine-readable evidence:
`data/generated/corolla_hf_cooperative_authority_wire_visibility.json` and
`data/generated/corolla_8965H1202000_cooperative_authority_wire_decompiler_evidence.json`;
deterministic verifier: `tests/verify_corolla_hf.py`.

### 6.7 `0x394` states 6–14 now have exact DEM-class/DTC-family provenance

The 17-state `0x394` classifier is no longer merely a generic “fault family” bucket.
A complete scan of all **384** exact-H DEM event records at `0x2B988` finds **242**
records with a populated class byte. Their exact class histogram is:

- `0x01`: 8 events; populated but not consumed by `0x4B692`;
- `0x02`: 34 events -> classifier states **6/7**;
- `0x04`: 1 internal/no-named-DTC event -> states **8/9**;
- `0x08`: 1 internal event -> state **13** when its additional classifier gate permits;
- `0x0F`: 1 internal event -> state **14** under the corresponding gate;
- `0x10`: 173 events -> state **10**, the dominant hardware/electrical/current/sensor/communication family;
- `0x20`: 16 events -> state **11**;
- `0x40`: 1 internal event -> state **12**; and
- `0x80`: 7 internal events contributing to the general state-16 fallback.

`0x4B692` also implements class `0xF0`, but the exact-H event table contains no
`0xF0` row. State 11 also has a separate internal `0x20`-aggregate source, so it is
not uniquely synonymous with class `0x20`. Where H's event record carries a DTC
index, the exact H DTC table joins to pinned `EMPS_P5` Toyota names. Class `0x10`,
for example, includes motor terminal-voltage/current/inverter/relay/sensor/processor
faults and `U012987 Lost Communication with Brake System Control Module`; class
`0x20` includes software-incompatibility and steering-angle-sensor communication
families.

The paired class-2/class-4 states have exact internal aging structure rather than an
uninterpreted duplicate: primary latches use calibration **200**, the shared secondary
latch uses **600**, and primary clear is additionally gated on `FEBEE8B0 >= 17736`.
Those are Toyota classifier/latch mechanics. They are **not** renamed
`steerFaultTemporary`/`steerFaultPermanent`: openpilot's policy distinction still needs
a recoverable-versus-latched live fault/recovery sequence or another independent policy
join.

Machine-readable contract: `data/generated/corolla_hf_fault_state_contract.json`;
deterministic verifier: `tests/verify_corolla_hf.py`.

### 6.8 The `0x351` force-7 override source topology is closed

The C159B49-linked base status and the force-7 path are now structurally separable all
the way to their sources. The force condition at `0x46E62` is exactly:

`(FEBE65E4 & 0x0003) != 0 && FEBE7E13 != 0`.

The first side is a broad redundant 16-bit status bitmap maintained at `FEBE6FB4` by
`0x36AAA/0x36BBE` and copied to `FEBE65E4` by `0x5778E`; force-7 consumes bits 0/1.
The second side comes from `0x36CEC`, which walks **24** status records selected from
two 12-byte record banks, ORs each valid record's `+6` ushort (plus one gated extra
source), and passes aggregate bit **15** through `0x3738C -> 0x472E0 -> FEBE7E13`.
When both sides assert, `0x46E62` forces status code 7 and `FEBE7DD1=1`.

This closes topology and gating, not Toyota display names: the current corpus has no
unique OEM/DTC semantic label for status-bitmap bits0/1 or record `+6` bit15. Therefore
the force-7 path is a distinct conservative severe/special status input, **not** another
name for C159B49 and not yet an openpilot temporary/permanent classifier.

Machine-readable contract: `data/generated/corolla_hf_remaining_status_contract.json`;
raw-body evidence: `data/generated/corolla_8965H1202000_remaining_status_decompiler_evidence.json`;
deterministic verifier: `tests/verify_corolla_hf.py`.

## 7. Command ingress: what the complete generated-COM census says

The H generated scalar extractor `FUN_0007643A` has **101 constant scalar binding
calls** in the corrected-context H corpus. The existing supervisor-ingress audit
walks those generated scalar destinations through raw/staging/snapshot references
and the steering-supervisor cone.

The result is unusually restrictive:

- 22 distinct externally generated scalar signals reach the supervisor cone after
  resolving the fixed GP map;
- FD `0x025` signals 184 and 186 are the shared 12-bit steering angle/rate sensor
  fields; and
- the sole H-only command-sized field is protected B6 **signal 255**, signed16 at
  B4:B5. It reaches snapshot `0xFEBEAE82` through the GP-relative RTE copy that the
  earlier direct-reference census missed.

That fixed-map correction turns the former bounded negative into a positive command
ingress result.

### 7.1 Protected B6 carries the new target-angle command surface

Techstream still identifies `0x0B6` by source relationship, not by command-field
name: its missing-message DTC is U012987 **Lost Communication with Brake System
Control Module**. Target-native H firmware then supplies the command semantics:

- signal 254 is an unsigned 6-bit field at B3. It follows
  `FEBE7D96 -> FEBEF127 -> FEBEADB0`; `0xCBE6E` accepts values
  `1/4/10/11/19`, asserts one common active flag, and selects one of five mutually
  exclusive cooperative-control profile flags. Techstream's byte-anchored
  `Target Lateral ID` pattern dictionary closes those exact values as
  **`1=PCS`, `4=LDA`, `10=Hands Off LTA`, `11=LTA/LCA`, `19=PDA`**. Downstream
  helpers select distinct calibration banks from those profile flags. `0xC825A`
  additionally treats raw IDs `25/27`, which the same OEM dictionary names
  **`AP`** and **`Remote Parking`** respectively; only `25/AP` is in the accepted
  steering-controller profile set;
- signal 255 is signed16 at B4:B5. It follows
  `FEBE7D94 -> FEBEF1CC -> 0xFEBEAE82`;
- `0xC9DB0/0xC9E54` turn signal 255 into replicated target state, beginning with
  `2 * signal255`;
- independently, FD `0x025` signal184 is signed12 coarse steering angle and
  signal185 is signed4 fractional steering angle. `0x42676` carries signal184
  without scaling into the exact H DID `0x1037 Steering Angle` source. Techstream
  `CDbPhyData` key 3 converts that raw count as `raw * 15`, with one decimal place
  and unit `deg`, proving **1.5 deg/count** for signal184;
- `0xB24D0` recombines `15 * signal184 + signal185`, and `0xB23A2` divides that
  combined quantity by `3600` for a full-revolution representation. Therefore
  signal185 is a signed **0.1-degree fraction** and the combined FD025 angle is in
  tenths of a degree;
- `0xCBD7E/0xCB096` convert the same measured angle into the controller domain as
  `trunc((15*coarse + fraction) * 1787 / 512)`;
- `0xCA138` applies the **same `0xB76/0x400` gain** to target and measured state and
  computes target minus measured; and
- that error enters the active steering controller and eventually contributes through
  `C2A8 -> CD3CC -> C3B8 -> ... -> C3D2`, the chain exposed by Techstream DID
  `0x1C02` **Command Value Torque**, then DID `0x1152` **Command Value Current
  (Q Axis)**.

This closes both the command domain and the controller-equivalent physical scale.
Equating the pre-comparator target and measured gains gives
`2 * signal255 = tenths_degree * 1787 / 512`, so **one signal255 count is
`1024/17870 deg = 0.057302742... deg = 1.000121519... mrad`** in the matched
controller domain. The 0.0122% offset from exactly 1 mrad/count is consistent with
H's `1787/512` fixed-point approximation; the firmware/Techstream evidence does not
itself name the B6 engineering unit as `mrad`, so that literal OEM wire-unit label
remains bounded. No Sienna `0x131` scale is transplanted. Techstream's P5 family
also contains **Target Steering Angle After Output Compensation** and related
`0x1CEE` observer fields; exact H lacks that DID, so those target-angle observer
names remain family corroboration. In contrast, the `Target Lateral ID` numeric
value dictionary is now an exact semantic join for every H-observed signal254
profile/special ID even though H firmware itself does not expose a literal wire
field name.

The receiver-side request and loss contract is also now statically closed in the
EPS scheduler domain. `Target Lateral ID=0` is the OEM **No Request (Manual
Operation)** state, while `CBE6E` asserts the common cooperative-control flag only
for the five supported active IDs above and only when the system gate
`FEBEACBD==0` and communication gate `FEBEC26D==1` hold. The communication gate
is target-native: B6 receive-status slot `0x18` follows
`44744(0x18) -> FEBE7DA0 -> FEBEF132 -> FEBEADB9`, and `CC7F8` requires that
snapshot to be zero. PDU42's exact descriptor is `060000002000000c`; successful
reception calls `769F6(pdu,1)` and reloads its first-u16 deadline value `6` to a
countdown of **7 foreground ticks**, while the deadline monitor `7683C` marks
activity[PDU42] `0x5A` on expiry. The same TAUJ0-CH3 foreground tick runs the
higher status path, so that first expiry makes `ADB9` nonzero and disables
cooperative selection immediately. The separate slot-18 status record
`2a00000bb8010200` carries a slower threshold of `440` ticks and can expose the
extended status bit `0x02`; it is not the primary steering cutout. TMS-053 closes
the CH3 timing that was previously missing: `0x5F660` configures TAUJ0 CH3 in
interval mode with a one-time `(400000+8000)`-count first interval, while `0x5F812`
rewrites CDR3 to `400000-1` for steady operation. Span's 6,000 live `0x030` frames
independently average `10.000012 ms` for the exact-H/F two-tick Tx descriptor.
Therefore the steady foreground tick is nominally **5.0 ms** (first interval
**5.1 ms**) and the seven-tick primary B6 cutout is nominally **35 ms**, subject to
normal foreground-phase quantization.

B6 signal261 (B7[5:0]) is independently closed as a 6-bit rolling sequence
counter. `CB246` computes `(current-previous) mod 64`; deltas `0/1` normalize to an
effective gap of `1`, while larger gaps are retained up to a cap of `8`. The capped
gap reaches `CB4F4` plausibility/supervision. TMS-053 corrects the earlier
signal258 polarity summary: in the exact `CBEEE` consumer, with a cooperative
profile active, the extra `CE864` add path requires **signal258 != 1** together
with the staged mode/sign mismatch predicate. Thus `258=1` suppresses that added
contribution; it is not required to enable it. Signal260 (B7[7:6]) has recovered
steady direct-consumer equivalence for values `0` and `3` aside from mode-change
history, while `1/2` select the special branch family and `2` has an additional
interpolation path. Signal264 (B10 bit7) is a special-control validity/inhibit
input used around the AP/Remote-Parking state machine; signal265 (B10[2:0]) is
republished only while B6 communication is healthy and downstream accepts modes
1/2/3 while normalizing other values to 0. Their literal OEM names remain bounded;
Techstream's `Cooperative Control in Progress Flag` is family vocabulary, not a
proved one-to-one name for signal258.

Signals 262 and 263 remain important companion modifiers: B8/B9 feed `0xCC442` and
`0xCBFCE` as percentage-like scaling inputs to internal steering contributors.
For their ordinary recovered paths, value `0` removes those percentage-scaled
terms. Consequently an EPS-consumer-derived minimal ID11 candidate is now
`258=1, 260=0, 262=0, 263=0, 264=0, 265=0`. This is **not** promoted as Toyota's
stock template or as cross-ECU-neutral; those properties still need isolated,
relay-correct validation.
The four configured nonscalar B6 IDs `252/253/266/267` still have no recovered
block/group/full-PDU consumer.

### 7.2 The classic camera/IPM-A interface was actually removed

H retains disabled DTC residue for U023A87 **Lost Communication with Image Processing
Module "A"**, but the older active monitor family for:

- `0x2E4`;
- `0x131`;
- `0x191`;
- `0x2FD`

is absent from H's active monitor table. Their old Dem records point at the disabled
DTC residue instead. Combined with the missing H `0x2E4/0x131` COM/SecOC profiles,
this is strong target-native evidence that the classic direct camera/IPM-A steering
interface was **disabled/removed**, not merely renumbered to `0x0B6`.

## 8. Computed/indirect ingress audit: the retained branch is live, not zero-fed

The earlier direct-symbol census had one important blind spot: H frequently writes
steering state through a fixed GP base (`0xFEBEB800`) plus constant offsets. A focused
audit of those computed stores changes the retained-branch interpretation without
resurrecting a hidden `0x2E4`-style scalar.

### 8.1 Mode enable `FEBEC26D` has a real GP-relative writer

`0xCC7F8` writes `GP+0xA6D`, exactly `FEBEC26D`. It combines communication-health
selectors `0x10` and `0x18` with the B6 validity snapshot `FEBEADB9`:

```text
health(0x10) = FUN_000BA090 -> FUN_00044CFC
health(0x18) = FUN_000BA090 -> FUN_00044CFC
C26D = ((health(0x10) | health(0x18)) != 0x5A) && (FEBEADB9 == 0)
```

The exact target configuration records are `0x28E2A = 025a2300000bb801` and
`0x28E6A = 02002b00000bffff`; both use health class 2, which `0x44CFC` maps to
`FEBE7C42`. `0x44C86` generates the `7C40/41/42` health family. Therefore the old
statement that `C26D` had only a zero initializer and readers was a representation
error: the decoder at `0xCBE6E` can receive a real enable.

### 8.2 `FEBEC17C/C17E/C184` also have a real GP-relative producer

The three replicated magnitude words are written by `0xCAD62` through
`GP+0x97C/+0x97E/+0x984`. Its input is the replicated `C1F8/C1FC/C206` state produced
by `0xCC2EC`; `0xCAD62` selects, calibrates, and scales that state before writing the
same result to all three magnitude words. `0xC9C16 -> 0xCB8BA -> 0xCB9B6` then
conditions that value into `C2A8`, which `0xCD3CC` includes as one conditional term
in the general torque composition.

The upstream magnitude is itself synthesized inside the steering pipeline. `0xCC18E`
produces the base replicated state family from local/mode/calibration inputs;
`0xCC442` and `0xCBFCE` apply the B6 262/263 modifiers described above before
`0xCC2EC` and `0xCAD62` publish the retained magnitude triplet. This is a **live
locally synthesized, B6-modulated conditioner**, not a dead leftover branch.

### 8.3 The general command siblings were also misread by a direct-only census

The same audit finds GP-relative runtime producers for several `0xCD3CC` terms that
previously looked zero-only when only named assignments were counted:

| Internal term | Recovered GP-relative producer | Static role boundary |
|---|---:|---|
| `FEBEBE04` | `0xC68F4` | local/calibration lookup product and limit |
| `FEBEBD90` | `0xC6146` | local/calibration interpolation and limit |
| `FEBEB678` | `0xBE25A` | local/calibration interpolation |
| `FEBEBEC6` | `0xC76FA` | conditioned local/calibration contribution |
| `FEBEC39C` | `0xCD31A` | bounded sum of local high-level contributors |

`BD0E` and `C358` retain their separately recovered local chains. This reinforces the
correct interpretation of DID `0x1C02 Command Value Torque`: it is a general internal
command observable built from multiple live terms, not an LTA-only wire echo.

### 8.4 What the computed audit closes

The deeper fixed-map audit does uncover the missing command surface. The old
"staged-only" result for B6 signal 255 was an artifact of looking only for named/direct
RAM references. `0xB8EEC` copies `FEBEF1CC` to `0xFEBEAE82` through GP-relative
addressing, after which the signed16 value drives the target-versus-measured angle
controller described above.

The combined scalar/fixed-map and copy-surface audit now has a narrow result:
**protected B6 signal 255 is the one recovered command-sized H-only wire ingress**;
B6 signal 254 supplies its cooperative mode/control ID; 262/263 modify controller
contributions; the D7 command-sized scalar is vehicle speed; shared large `0x025`
fields are sensor state; and no second command-sized generated scalar or recovered literal block/group/full-PDU
route was identified. The separate full-B6 application scan also closes named/absolute
and simple-GP-alias constant-displacement references; arbitrary value-set/computed-base
aliases and DMA/peripheral mutation remain outside this static proof.

What remains open is no longer "where does the EPS get an autonomous target?",
"what is its physical scale?", "which Toyota features do the accepted profile IDs
mean?", or "how quickly does the EPS drop a missing B6 in its own scheduler?"
Receiver request selection, the 7-tick primary loss cutoff, modulo-64 sequence
handling, and the **entire 32-byte receiver envelope** are closed. B0..B27 are the
authenticated application region; only selected B3..B10 bits have recovered EPS
semantics; B28..B31 are FV4+CMAC28; full freshness and the exact 36-byte CMAC input
are reconstructed; and config/job0 selects ICU-S slot4. The receiver freshness
algorithm plus authenticated `0x00F` now also close a deterministic **exclusive
replacement-sender** state machine: re-anchor on a strictly newer authenticated
trip/reset epoch, seed B6 message8 from the transmitted low2 on a new epoch,
advance message8 locally (normally +1; receiver window +1..+4), keep signal261 as a
separate modulo-64 application counter, and after a sender restart mid-epoch wait
for the next authenticated reset rather than guessing the committed message8.
No cross-power message8 persistence is needed under that startup rule. Toyota's
**stock** B6 cadence/initial-message policy remains unknown, but it is no longer
required to construct receiver-valid replacement freshness. Remaining command-side
unknowns are the slot-4 signing primitive/key, stock sender cadence/template and
cross-ECU secondary-field effects, stock-source suppression, and the upstream
**payload/SecOC producer contract**. Techstream now closes the module-level topology more tightly:
Corolla P5 pairs `FRC_P5` 498 with category 435 **`ABS_P5` = Brake/EPB** and
`EMPS_P5` 405; FRC has X216E `Front Recognition Camera => BRK Communication
Invalid`, ABS monitors EPS communication, and H maps B6 loss to U012987 Brake
System Control Module. `ABS_P5` DID `0x107E ADS Control EPS Pinion Angle2` is a
signed 0.00025-rad/count diagnostic observer. This still does not prove a
byte-level FRC→ABS→B6 forwarding chain or identify the SecOC signer. The literal
OEM engineering-unit name for signal255 is also still unjoined even though its
controller-equivalent degree/radian scale is closed.

## 9. Porting roadmap after this recovery

### State side

Driver torque is no longer an evidence hole: live `0x030` supplies the exact physical
quantity, and `0x4A3` B5 is an independently closed alternate carrier. The efficient
next state work is now:

1. capture a firmware-identified, relay-correct H/F vehicle that actually carries
   `0x4A3/0x351/0x394` while exercising the now-wire-identified `0x51E B0[7]`
   Ready Status through a `1->0->1` transition and recording DID `0x1033` as an
   independent diagnostic oracle;
2. exercise stock LTA off→active→off and deliberate safe fault/message-loss
   transitions to map the `0x394` projection and both `0x351` paths (the
   C159B49-linked base status plus separate force-7 override) to operational
   availability without inventing temporary/permanent classes;
3. correlate `0x4A3` B6:B7 Q-current with command-current DIDs and derive allowable
   actuator-response error/limits; and
4. choose a conservative openpilot/Panda physical driver-override policy using the
   live `0x030` torque signal and validate driver interaction/release dynamically.
   TMS-053's expanded exact-H source/snapshot census finds no physical-driver-torque
   comparator in the recovered C8xxx-CExxx target-to-motor control cone, so there is
   no Toyota EPS override constant left to recover under that census boundary.

### Command side

The receiver-side command carrier is now identified, so the decisive experiment is
**parameter recovery**, not generic provenance discovery:

- capture protected `0x0B6` during known stock-LTA intervals and correlate signal
  254, signed16 signal 255, signals 262/263, and B6 validity with steering angle,
  `0x1C02`, `0x1152`, and actual Q-current;
- treat signal254 request selection, the 7-foreground-tick receiver deadline,
  signal261 modulo-64/gap-cap-8 sequence rule, the complete B0..B31 receiver
  partition, FV4/CMAC28 trailer, full-freshness packing, CMAC input, and slot4
  selection as closed receiver requirements; use the authenticated-0x00F replacement
  state machine for receiver-valid message8 freshness, while a stock capture remains
  valuable for **stock sender wall-clock cadence**, secondary-field dynamics/cross-ECU
  behavior, and normal target/rate context before production actuation;
- recover a production-safe key/slot4 signing path and stock-source suppression
  requirements. Exact H/F command-5 software machinery accepts the required 36-byte
  B6 authenticated input, but the Sienna single-stage resident proxy geometry does
  **not** transfer: H startup clears `FEBF05CC..FEBF09CB` and
  `FEBF0B4C..FEBF0F4B`. TMS-054 now supplies a separately audited **static** H/F
  carrier candidate (332-byte inert canary / 462-byte fixed-B6 signer); what remains
  is live canary retention/health followed by selector-4 permission and latency; and
- acquire/analyze true-TSS3 `FRC_P5` plus category-435 `ABS_P5`/Brake firmware,
  or synchronized FRC/Brake/EPS captures, to explain the still-open byte-level target
  transformation and SecOC sender/key/freshness ownership.

The command-side unknown is therefore upstream ownership and safe reproduction of a
known EPS receiver contract, not discovery of another replacement `0x2E4`.

### Candidate Panda lateral-safety contract (non-enabling)

The H/F firmware now closes enough of the EPS-side safety envelope to replace the
previous generic “Panda limits unknown” bucket with a concrete candidate contract.
This is **not enabled** in opendbc: the TSS3 platform remains `dashcamOnly` with
Panda `noOutput`, and the candidate deliberately separates the exact EPS envelope
from a stricter policy we would allow a future openpilot sender to use.

For protected CAN-FD `0x0B6/32`, exact H accepts active Target Lateral IDs
`1/4/10/11/19 = PCS/LDA/Hands Off LTA/LTA-LCA/PDA`; `0` is No Request. A future
openpilot lateral-only policy should be narrower: permit only **ID 11** while
controls are allowed and ID 0 while inactive. The LTA/LCA target-angle envelope is
now numeric rather than inferred from old Toyota Panda constants:

- `CB46E/CB4F4` select an absolute signal255 threshold of **1745 raw counts** for
  LTA/LCA. With the independently closed `1024/17870 deg/count` conversion, that is
  **99.9933 deg**, effectively the EPS's ~100-degree LTA bound.
- The same monitor selects **78 raw counts per effective sequence gap**
  (**4.4696 deg**) as the target-jump threshold. The exact EPS application gap is
  `(cur-prev) mod 64`, normalized to `1` for gaps 0/1 and otherwise capped at 8.
  Below `abs(target)=87` raw (~4.985 deg), the firmware bypasses that delta check.
- Because Panda controls its own sender, the candidate policy is intentionally
  stricter: after the first active frame require signal261 to advance **exactly +1
  mod 64** and allow at most **78 raw counts** of target change on every active
  frame, without exploiting the EPS's tolerated gaps or low-angle bypass.
- The independent C9E54 conditioner clamps the same LTA target to ±3490 in its
  doubled internal domain (= ±1745 B6 raw). Its selected low/vehicle bank also
  slews that internal target by 7 doubled-domain counts per steering-task call
  (3.5 B6 counts, ~0.2006 deg); the compiled high/default bank uses 4. The
  foreground scheduler is now closed at nominal **5 ms**. If this conditioner is
  invoked exactly once per foreground cycle, those steps correspond to ~40.1 deg/s
  (selected low/vehicle) and ~22.9 deg/s (high/default). That once-per-cycle call
  relation remains the condition; the per-call limits are the unconditional firmware
  facts.

Measured steering supervision is target-native too. `0x025` signal184/185 remains
`1.5 deg/count` coarse plus signed `0.1 deg/count` fraction, and signal186 is the
signed12 steering-rate input consumed by the EPS. `CB2E0` selects a raw LTA rate
threshold of **100**; the EPS debounces that over-rate condition for 79 low-bank
(or 63 high/default-bank) cycles before the persistent latch. A candidate Panda
policy should be conservative and stop active steering immediately when
`abs(signal186) > 100`, rather than wait for the EPS debounce. Firmware proves the
raw signed12 threshold; the current Toyota DBC's `1 deg/s/count` physical factor is
useful prior art but is not promoted here as an independently OEM-named unit proof.

The recovered internal gating also prevents over-reading those visible checks as
the complete EPS decision. `CB4F4` contributes target-plausibility state `C269`;
`CB59A` contributes a persistent **FEBEAE16 internal-command-state** latch `C26B`;
`CB22E` forms `C26A = C269 || C26B`; and `CADE4/CAE18` require that aggregate plus
the separate `C245` tracking gate clear before cooperative control survives. The
`FEBEAE16` monitor is not measured motor Q-current. The observable
Panda-side mapping is therefore:

- require valid `0x025` measured angle/rate;
- verify live `0x030`'s additive B7 rule before trusting its safety inputs;
- require `0x030 DRIVER_TORQUE_INVALID` (B6[0]) clear;
- require `0x030 STEERING_FAULT_INHIBIT_STATUS` (B6[2]) clear; and
- apply a physical driver-override threshold to the already closed `0x030` torque
  once that threshold is validated dynamically.

#### Firmware/calibration limit recovery beyond the basic Panda envelope

A deeper H/F supervisor/motor-control pass closes several additional distinctions
that matter more than importing pre-TSS3 Toyota constants:

- The hard LTA/LCA B6 ceiling remains **±1745 raw** in both calibration banks. The
  `CBFCE` profile path does have four `FEBEADF4`-indexed compensation LUTs
  (`bank+0x768/+0x798/+0x7C8/+0x7F8`), but every real point in the runtime-selected
  low/vehicle bank has value **0**. The compiled high/default counterparts become
  nonzero beginning at axis 7680. The physical identity of `FEBEADF4` is deliberately
  not guessed here. These are compensation maps, not a maximum-angle curve, and no
  speed-dependent reduction of the hard ±1745 B6 ceiling is recovered.
- `CB14E` uses an internal tracking half-window of **524** (a 1048-unit full
  comparison window) with persistence 40. `CB394` monitors `FEBEAE16` at **512**
  with persistence 79 in the selected low bank / 59 high-default; `CB59A` has a
  second `FEBEAE16` threshold **1280** with persistence 96. `CBD7E` retains raw
  reconstruction-validity bounds **80/90/512**, and `CAE18` contains a separate
  counter threshold 15. Their internal units are not promoted to fabricated
  steering-angle/current engineering units.
- The physical driver-torque path has a native acquisition clamp of **±2109** in
  the N·m×256 domain (~**±8.2383 N·m**) and exported telemetry saturation at
  **±10.00 N·m**. These explain representation behavior—including Span's -8.23 N·m
  observed floor—but neither is a driver-override threshold. TMS-053 expands the
  census to the full direct named/fixed-GP physical source/snapshot family
  `FEBE7B08 -> FEBE6554`: 13 exact-H functions consume/copy/export that family and
  **zero** fall inside the recovered C8xxx-CExxx target-to-motor control cone.
  Under that explicit negative boundary there is no Toyota EPS physical-driver-torque
  authority comparator left to recover; `driver_override_abs_nm` is an
  openpilot/Panda policy value to choose conservatively and validate dynamically.
- Physical motor Q-current remains closed as `FEBE6592` and `0x4A3 B6:B7`
  (-0.01 A/count, sign-inverted relative to the Techstream raw value). A promoted
  whole-corpus exact-symbol census finds that measured Q-current only in its
  snapshot/telemetry bridge, while the cooperative `CB394/CB59A` monitors reference
  `FEBEAE16` instead. Under that explicit direct-reference/computed-alias boundary,
  **no OEM measured-Q-current response comparator is recovered**. A future Panda
  response limit may still be desirable, but it is a separately designed and
  relay-correctly validated safety policy—not a constant to copy from the EPS.
- Additional torque-sensor fault calibrations (`2655/4233/4091/3341/1764`) are
  retained as raw internal fault/plausibility constants only. Their comparison
  domains do not justify relabeling them as physical driver-override thresholds.

The exact B6 receiver-loss guarantee remains **7 TAUJ0-CH3 foreground ticks**:
successful PDU42 receipt reloads 7 and first expiry disables cooperative selection.
TMS-053 closes the steady tick at nominal **5 ms**, so this is a nominal **35 ms**
primary cutout (with normal scheduler-phase quantization and one 5.1-ms startup
interval). After a future host/sender lapse, Panda should discard previous
sequence/desired-angle history and require a fresh inactive/reinitialization
transition before allowing active steering again.

This leaves three bounded **policy** classes rather than an undefined Panda model:
physical `driver_override_abs_nm`, extended fault policy (`0x394`/Ready/DTC classes
beyond the already-known immediate `0x030` gate), and a deliberately chosen
actuator-response policy. The third is no longer framed as an undiscovered OEM
Q-current threshold: static H/F evidence did not recover one in the cooperative
supervisor. Secondary B6 fields 258/260/262/263/264/265 are **not free safety
parameters**: the EPS-consumer-derived minimal ID11 candidate is
`1/0/0/0/0/0`, but production TX remains disabled until its cross-ECU effects and
stock-LTA behavior are validated on the isolated relay-correct path and the result is
whitelisted. Relay-side ownership/suppression and stock sender cadence remain open.
Receiver-valid replacement freshness construction is now closed; the remaining SecOC
deployment blocker is the actual slot-4 signing primitive/key (or a completed H/F
command-5 runtime carrier with live permission/latency).

#### Competing valid B6 senders: receiver arbitration and suppression requirement

The exact H/F receiver does **not** authenticate or arbitrate a named physical B6
sender. Generated SecOC has one B6 profile (`DataID=0x00B6`, freshness ID 2,
normal freshness slot 1, ICU-S slot 4), and the recovered 36-byte CMAC input is
`00 B6 || B0..B27 || freshness48`; no additional sender/source identifier is
concatenated. The application likewise has one PDU42 COM shadow. This means
"stock sender" versus "openpilot sender" is a network/topology distinction, not
an identity the EPS can prefer after authentication.

The ingress path nevertheless has deterministic **stage-dependent** arbitration:

- `0x8865A` gives each SecOC profile a single queue slot. From idle `E1`, the first
  B6 becomes pending `D2` and is inserted once through `0x87CD6`. A second B6
  arriving while that same profile is still `D2` calls `0x87DB0`, which updates
  the existing pending storage rather than inserting a second queue node. Thus the
  **last arrival before verification starts** is the payload presented to the verifier.
- `0x88702` changes `D2` (or retry `B4`) to verify state `C3`. `0x8865A` has no
  insert/update branch for `C3` or `B4`, so additional B6 arrivals while the current
  candidate is being verified/retried are not admitted to the profile queue.
- After a successful CMAC, the pending B6 freshness state commits before delivery.
  `0x76A3C` then copies the accepted PDU into the one PDU42 COM shadow and reloads
  the same communication deadline. Across separately accepted future-freshness
  frames, the **last successfully delivered B6** is therefore the current
  application command/profile, subject only to normal task sampling.

Freshness is the only recovered anti-replay arbiter, and it is shared rather than
source-specific. Once one B6 commits a full freshness value, replaying that same
full freshness does not authenticate again: same-epoch reconstruction chooses the
next congruent message8 candidate (for example committed message10 with received
low2=`2` reconstructs message14), so the old CMAC is checked against different
freshness. Conversely, another sender that can produce a valid slot-4 CMAC for an
acceptable **future** B6 freshness is not rejected merely for being a different
source; it advances the same committed B6 freshness state. Two capable senders thus
race one freshness timeline rather than receiving independent windows.

There is one important generated **verification-failure forwarding exception** that
an earlier receiver summary missed. B6 record byte `+0x09` is 0. `0x8857C` zeros a
global counter at `FEBE5408`; `0x88308→0x88288→0x886DA` increments it up to the raw
configured limit **204**, while `0x886FC` can reset it. On hard freshness result
`0x22`, `0x88A56` enters A5 and calls `0x888A6` without ever submitting command7.
On CMAC mismatch, the first failure uses B6's one retry; if that retry is exhausted,
`0x8891E` enters generic failure 96 and likewise calls `0x888A6`. For an ordinary
profile such as B6 (`+0x09 != 1`), `0x888A6` calls upper-delivery helper `0x88856`
while `FEBE5408 < 204`; it also does so whenever a separate global state at
`FEBE53EE` is D2 (`0x88512`), whose OEM mode name remains unrecovered. The queued
PDU can therefore reach COM **despite failed verification** during those bounded
modes. Its freshness is not committed, so this is fail-open delivery, not an
authenticated success. Once the counter is >=204 and that global D2 mode is inactive,
the recovered failure handler no longer routes B6 verification failures. The
wall-clock length of the 204-count window is not invented here.

Signal261 does not solve that race. `CB246` computes `(current-previous) mod 64`;
delta 0 and delta 1 both become effective gap 1, while larger gaps are capped at 8.
`CB4F4` uses that effective gap for target plausibility (78 raw target counts per
effective gap). A duplicate application sequence is therefore **not rejected** and
"newest sequence wins" is not an EPS arbitration rule. Target Lateral ID also has
no cross-frame priority scheme: `CBE6E` clears the profile flags and decodes only
the current B6 value (`1/4/10/11/19`). A later accepted B6 can simply replace the
active request/profile with another supported ID.

The production conclusion is consequently stricter than "parallel injection might
work": **deterministic lateral authority requires exclusive B6 control**. This is
not because the EPS demands a named stock source; it is because the EPS provides no
source preference, no request-ID priority, and no duplicate-sequence rejection to
resolve two valid streams. Depending on timing, pending frames coalesce, in-flight
arrivals are ignored, the first successful commit consumes a freshness value, and a
later future-valid delivery becomes the current command. Freshness racing or
pre-empting stock is therefore not a safe coexistence/fallback mechanism.

For production openpilot, suppress/isolate the stock B6 producer on the relay-correct
path before emitting replacement B6, **unless a future firmware-identified stock-LTA
capture proves that the stock producer is quiescent in every state where openpilot
would transmit**. Static receiver logic cannot identify which physical relay side
contains that producer, so the repinned capture remains required for the actual
suppression point. Machine-readable contract:
`data/generated/corolla_hf_b6_competing_sender_arbitration.json`; exact-H compact
queue/application evidence:
`data/generated/corolla_8965H1202000_b6_competing_sender_decompiler_evidence.json`.

All cited safety functions (`C9CEA/C9DB0/C9E54/CADE4/CAE18/CB14E/CB22E/CB246/CB2E0/
CB394/CB46E/CB4F4/CB59A/CBD7E/CBE6E`) are byte-identical between H and F, and the
cited calibration values are byte-identical as well. Machine-readable contract:
`data/generated/corolla_hf_panda_lateral_safety_contract.json`; compact exact-H
decompiler evidence:
`data/generated/corolla_8965H1202000_panda_lateral_safety_decompiler_evidence.json`.

### H/F command-5 portability and target-native carrier candidate

The useful **software** part of the Sienna command-5 signing work transfers to
H/F. Exact H record 0 at `0x27C88` selects completion `0x82F5C`, adapter
`0x820CC`, worker `0x821D0`, and config `0x27C84`; serialized dispatcher
`0x82750` reaches the same generated lower command-5 family, and `0x81E94`
accepts caller lengths below `0x51`, which covers the 36-byte B6 authenticated
input. These application bytes are identical on F.

The prior Sienna **546-byte** resident proxy still must not be copied blindly.
H startup `0x6149A` clears `FEBF05CC..FEBF09CB` and
`FEBF0B4C..FEBF0F4B`, disproving transfer of Sienna's full
`FEBF0000..FEBF0307` free-space assumption. A target-native census now narrows
the lower page further instead of abandoning it: after normalizing both absolute
`FEBFxxxx` references and simple `GP=FEBEB800` offsets, the exact H corpus has
**zero recovered references in `FEBF0000..FEBF01CF`**; the first recovered
normalized reference is exactly `FEBF01D0`. This is a bounded negative — arbitrary
computed aliases, DMA/hardware writers, and live lifetime are not statically
excluded.

Exact H's application MPU independently places that 464-byte pocket inside
region 5, `FEBEF400..FEBF33FC`. Both recovered MPU contexts assign MPAT
`0xB8`, i.e. supervisor read/write/execute and no user permissions. The relevant
MPU tables/loader, CPU-context transition, startup coordinator, foreground
scheduler, RAM initializer, command-5 dispatcher, and variable-length prepare
ranges are byte-identical on F. The selected 60-byte observation/mailbox region
`FEBFFB80..FEBFFBBB` is above the startup shadow-copy end `FEBFF9EF`, inside the
known XCP shadow window, and has zero recovered normalized direct references under
the same bounded census.

A dedicated fixed-B6 runtime now proves the machine-code fit rather than merely
estimating it. The audited command-5 proxy is **462 bytes**, entry offset zero,
zero ELF relocations, SHA-256 `3bb96eef...609f8d3`, and therefore leaves only
**2 bytes** of headroom in `FEBF0000..FEBF01CF`. It keeps the stock application
scheduler, uses H/F dispatcher `0x82750`, clean record 0, slot selector 4,
completion cells `FEBF1280/FEBF1281`, and a fixed 36-byte B6 authenticated input.
Shared-driver busy result 2 leaves the request pending for a later foreground
retry rather than aborting an in-flight command-7 operation. The hardened proxy no
longer relies on installer preinitialization: after stock final init and before `ei`
it writes mailbox `request_state=0`, then samples one host-committed state per
foreground tick. Completion callback bytes `FEBF1280/FEBF1281` are adjacent, so the
proxy reads them as one halfword after done=1 and mirrors status into mailbox byte
`FEBFFB81`; immediate non-busy dispatcher errors are mirrored there too. This keeps
all host-visible request/result state inside the XCP-readable 60-byte mailbox.

The required first live payload is deliberately smaller and inert: a **332-byte**
canary, also entry-zero and relocation-free, reproduces the same boot ->
application-context -> startup -> foreground transition but never calls command 5.
Its sole extra behavior is heartbeat progression at `FEBFFB80`. A hardware run
must establish that heartbeat progression, normal application health, and reset-
to-stock behavior before the 462-byte signer is exposed. Only after that should a
known-input selector-4 experiment establish live generation permission, followed
by independent MAC agreement and command-5 latency/jitter under normal command-7
verification load.

Albino's same-car `eps-telescope` replay now makes that first experiment directly
operational instead of leaving the bootstrap implicit. The exact specimen reports
application F181 `8965F1208000 / 8A3111202000`, boot F181 `02 || 32*0x21`, and
successful boot SecurityAccess plus `0x10F0` authentication of a zero-0201/0202
4-KiB `FEBF0000` envelope. `exploit/ephemeral_runtime/corolla_hf_direct_canary.py`
therefore packages the audited 332-byte canary directly under the target's
payload-build secret into deterministic ciphertext SHA-256
`313d1bb70fe6147c179e4b5a35e4556e536f062a80d53d85af3d4292b0b29d84`,
replays the exact single old-stack ladder and zero `0203/0201/0202` writes, uses
`01 46 01 00 FEBF0000 1000` + `10F0/45 00` + raw `FF00`, and performs **no**
post-`10F0` RAM substitution. Live mode is double-gated (`--execute` plus
`--bench-isolated`), pins both application and boot F181, rejects any package
hash drift, requires the `FEBFFB80` canary signature to advance after application
F181 reappears, and does not expose the command-5 proxy. Reset-to-stock still has
to be observed separately after a successful canary run. The subsequent guarded
`corolla_hf_direct_command5.py` path requires that successful canary result plus an
explicit reset confirmation before live mode, packages the audited proxy directly
(SHA-256 `a9497970...e9d5a58`), commits mailbox state last, and requires mirrored
status zero with a 16-byte non-sentinel result; it does not emit B6 or write flash.
The same-car bootstrap provenance is retained in
`data/generated/corolla_2023_albino_telescope_analysis.json` and the specimen
report [corolla-2023-us-public-route.md](corolla-2023-us-public-route.md) §7.39.

This closes the **static target-native carrier candidate**, not the live runtime.
`data/variant_ram_exec_requirements.json` therefore still gains **no** H/F verified
entry. Live retention/lifetime, provisioned slot-4 command-5 permission, signing
latency, and production B6 timing remain dynamic blockers, and nothing here
authorizes vehicle actuation. Machine-readable evidence:
`data/generated/corolla_hf_command5_runtime_carrier_evidence.json`,
`data/generated/corolla_hf_command5_runtime_carrier.json`, the exact same-car
`data/generated/corolla_2023_albino_telescope_analysis.json`, and the earlier
`data/generated/corolla_hf_command5_portability.json`.

## 10. Production boundary

The candidate safety math is now substantially closed, but it still does not authorize
actuation. Before a real H/F openpilot port, recover and validate:

- a deliberately chosen conservative **Panda/openpilot driver-override policy** for the now-closed `0x030` physical torque signal. The expanded exact-H static census found no physical driver-torque comparator in the recovered target-to-motor control cone; this is no longer an OEM-threshold-recovery blocker;
- a deliberate Panda/sender Q-current actuator-response policy validated against relay-correct dynamics, plus extended fault-policy mapping (the cooperative EPS supervisor exposes no recovered measured-Q-current comparator);
- dynamic validation of the now-closed incoming `0x51E B0[7]` Ready Status through
  value `0`, plus temporary/permanent steering-fault semantics; no EPS-Tx Ready
  duplicate is required for basic observation;
- stock B6 wall-clock cadence and the active-LTA template for the bounded secondary B6 fields. The replacement sender's SecOC message8 start/progression is statically closed by `0x00F` re-anchoring and no longer requires recovery of Toyota's B6-local counter-start policy;
- relay-correct **physical stock-B6 producer isolation/suppression point** and dynamic confirmation of the statically closed nominal **35 ms** seven-tick loss behavior (receiver-side competing-stream arbitration is already closed above);
- live proof that the audited 332-byte H/F carrier canary survives into healthy application scheduling, then confirmation that provisioned slot4 permits command 5 with acceptable latency using the audited 462-byte signer (or recover the slot4 secret/another approved MAC path); and
- fallback/coexistence behavior with brake/AEB and stock LTA/LDA/LCA functions.

The machine-readable evidence is
`data/generated/corolla_8965H1202000_openpilot_state_bridge.json`,
`data/generated/corolla_8965H1202000_b6_receiver_contract.json`,
`data/generated/corolla_8965H1202000_b6_secoc_verification.json`,
`data/generated/corolla_hf_b6_competing_sender_arbitration.json`,
`data/generated/corolla_hf_steering_limits.json`,
`data/generated/corolla_hf_panda_lateral_safety_contract.json`, and
`data/generated/corolla_hf_command5_portability.json`,
`data/generated/corolla_hf_command5_runtime_carrier.json`, and
`data/generated/corolla_2023_albino_telescope_analysis.json`; their compact
raw-body-bound decompiler/reference evidence is tracked alongside each artifact.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [COM-009](../reference/index.md#finding-com-009), [COM-010](../reference/index.md#finding-com-010), [COM-011](../reference/index.md#finding-com-011), [COM-014](../reference/index.md#finding-com-014), [COM-015](../reference/index.md#finding-com-015), [COM-016](../reference/index.md#finding-com-016), [COM-017](../reference/index.md#finding-com-017), [TMS-053](../reference/index.md#finding-tms-053), [TMS-054](../reference/index.md#finding-tms-054), [TMS-055](../reference/index.md#finding-tms-055), [TMS-056](../reference/index.md#finding-tms-056), [TMS-058](../reference/index.md#finding-tms-058), [TMS-059](../reference/index.md#finding-tms-059)
- Corrections with this document as canonical home: [CORR-109](../reference/index.md#correction-corr-109), [CORR-110](../reference/index.md#correction-corr-110), [CORR-111](../reference/index.md#correction-corr-111), [CORR-112](../reference/index.md#correction-corr-112), [CORR-113](../reference/index.md#correction-corr-113), [CORR-114](../reference/index.md#correction-corr-114), [CORR-115](../reference/index.md#correction-corr-115), [CORR-116](../reference/index.md#correction-corr-116)
<!-- knowledge-cross-references:end -->
