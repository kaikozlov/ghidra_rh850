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

B6[1] is independently live (`0/1`) but its exact steering semantic is still open;
B6[3] is runtime-produced and remains zero in this segment. Signal 34 is a signed16
calibrated derivative of the DID `0x1151` Q-current source. Its source role is
closed, but this report does not promote a physical packet scale because its
calibration factor is separate from the direct `0x4A3` conversion.

The capture contains no induced EPS fault and no stock-LTA off→active→off
transition. Therefore the asserted operational consequences of B6[2]/B6[0] remain
firmware-static, and they do not justify guessing openpilot temporary/permanent
fault classes.

### 6.4 Ready Status remains a diagnostic oracle

Techstream DID `0x1033` is exactly **Ready Status**. The H path is
`FEBE7D1B -> FEBEF052 -> FEBEB5A8 -> FEBEE811 -> DID 0x1033`. That corrects an
earlier tentative association with the SecOC synchronization message. No field in
`0x030/0x351/0x394/0x4A3` is yet proved to carry this exact boolean. Use DID 1033
as a future live-correlation oracle; do not invent a CAN ready bit.

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
extended status bit `0x02`; it is not the primary steering cutout. The CH3 timer's
absolute period is not statically recoverable here, so **7 ticks must not be
restated as milliseconds**.

B6 signal261 (B7[5:0]) is independently closed as a 6-bit rolling sequence
counter. `CB246` computes `(current-previous) mod 64`; deltas `0/1` normalize to an
effective gap of `1`, while larger gaps are retained up to a cap of `8`. The capped
gap reaches `CB4F4` plausibility/supervision. Signal258 (B6 bit2) gates one
profile-dependent controller contribution when equal to `1`; signal260 (B7[7:6])
is a four-state controller selector; signal264 (B10 bit7) is a special-control
validity/inhibit input used around the AP/Remote-Parking state machine; and
signal265 (B10[2:0]) is republished only while B6 communication is healthy. Their
literal OEM field names remain bounded; in particular, Techstream's
`Cooperative Control in Progress Flag` is family vocabulary, not a proved
one-to-one name for signal258.

Signals 262 and 263 remain important companion modifiers: B8/B9 feed `0xCC442` and
`0xCBFCE` as percentage-like scaling inputs to internal steering contributors.
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
route was identified. Arbitrary computed aliases and DMA/peripheral mutation remain
outside this static proof.

What remains open is no longer "where does the EPS get an autonomous target?",
"what is its physical scale?", "which Toyota features do the accepted profile IDs
mean?", or "how quickly does the EPS drop a missing B6 in its own scheduler?"
Receiver request selection, the 7-tick primary loss cutoff, and modulo-64 sequence
handling are closed. The remaining command-side unknowns are the **sender-side**
wall-clock cadence, SecOC freshness/key/source contract, stock-source suppression,
exact OEM names for the secondary B6 fields, and the upstream **payload/SecOC
producer contract**. Techstream now closes the module-level topology more tightly:
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
   `0x4A3/0x351/0x394` while recording DID `0x1033 Ready Status`;
2. exercise stock LTA off→active→off and deliberate safe fault/message-loss
   transitions to map the `0x394` projection and both `0x351` paths (the
   C159B49-linked base status plus separate force-7 override) to operational
   availability without inventing temporary/permanent classes;
3. correlate `0x4A3` B6:B7 Q-current with command-current DIDs and derive allowable
   actuator-response error/limits; and
4. derive a generation-native physical driver-override threshold using the live
   `0x030` torque signal before enabling `steeringPressed` or Panda torque policy.

### Command side

The receiver-side command carrier is now identified, so the decisive experiment is
**parameter recovery**, not generic provenance discovery:

- capture protected `0x0B6` during known stock-LTA intervals and correlate signal
  254, signed16 signal 255, signals 262/263, and B6 validity with steering angle,
  `0x1C02`, `0x1152`, and actual Q-current;
- treat signal254 request selection, the 7-foreground-tick receiver deadline, and
  the signal261 modulo-64/gap-cap-8 sequence rule as closed receiver requirements;
  use a stock capture to recover **sender wall-clock cadence**, exact secondary-field
  names/behavior, and normal target/rate bounds before any injection attempt;
- recover the B6 SecOC freshness/key/source contract and stock-source suppression
  requirements; and
- acquire/analyze true-TSS3 `FRC_P5` plus category-435 `ABS_P5`/Brake firmware,
  or synchronized FRC/Brake/EPS captures, to explain the still-open byte-level target
  transformation and SecOC sender/key/freshness ownership.

The command-side unknown is therefore upstream ownership and safe reproduction of a
known EPS receiver contract, not discovery of another replacement `0x2E4`.

## 10. Production boundary

These findings improve the roadmap but are not yet a Panda safety policy. Before a
real H/F openpilot port, recover and validate:

- a validated **driver-override threshold** for the now-closed `0x030` physical torque signal;
- allowable Q-current actuator-response error/limits;
- a Tx join for Ready Status and dynamic temporary/permanent fault semantics;
- sender wall-clock cadence, stock-source suppression, and dynamic confirmation of the statically closed 7-tick loss behavior;
- actual H/F rate and magnitude limits;
- fallback behavior when comma disappears;
- coexistence with brake/AEB and stock LTA/LDA/LCA functions.

The machine-readable evidence is
`data/generated/corolla_8965H1202000_openpilot_state_bridge.json`, plus the dedicated
`data/generated/corolla_8965H1202000_b6_receiver_contract.json`; their compact
raw-body-bound decompiler evidence is tracked alongside each artifact.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [COM-009](../reference/index.md#finding-com-009), [COM-010](../reference/index.md#finding-com-010), [COM-011](../reference/index.md#finding-com-011), [COM-012](../reference/index.md#finding-com-012)
- Corrections with this document as canonical home: [CORR-109](../reference/index.md#correction-corr-109)
<!-- knowledge-cross-references:end -->
