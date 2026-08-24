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
| 0 | `0x030` FD | 32 B | `2` | mixed telemetry/status/validity |
| 1 | `0x351` | 4 B | `200` | plausibility/debounce status family |
| 2 | `0x394` | 3 B | `60` | internal EPS status/fault family |
| 3 | `0x4A3` | 8 B | `100` | strongest openpilot state bridge |
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

| H `0x4A3` field | H-native source | Meaning we can support now |
|---|---|---|
| B0 | `FEBE7DAE | 0x20` | status/validity family; exact bit meaning unresolved |
| B1:B2 | `FEBE7D34` | mirror of FD `0x025` signal 184, the target-native signed-12 steering-angle sensor field |
| B3:B4 | `FEBE7A46` | same signed-12 quantity exposed by DID `0x1037` **Steering Angle** |
| B5 | `FEBE6554 -> *100/0x100 -> /10 -> signed-byte saturation` | same native source as DID `0x1035` **Steering Wheel Torque** |
| B6:B7 | `FEBE6592 * -100 / 0x80`, big-endian signed16 | exact sign-inverted raw quantity used by DID `0x1151` **Motor Actual Current (Q Axis)** |

The B5 pack path is additionally bounded by `0x6387C`, which saturates to the
signed-byte range. Techstream names the source quantity *Steering Wheel Torque*.
This report does not promote a physical B5 unit/scale yet because the wire-side
integer reductions need an explicit physical-scale validation rather than an
assumption from display precision.

B6:B7 is particularly useful, but it must be named correctly: it is a motor
Q-axis current-response observable. It is **not automatically the old
`STEER_TORQUE_EPS` quantity** merely because the old `0x4A3` reused the older EPS
Torque staging state. This new observable may be better for actuator-response
safety, but its relationship to commanded road-wheel torque must be measured and
bounded on H/F.

### 3.2 Why this matters for openpilot

`0x4A3` already gives a practical generation-native path to three state classes
that a port needs:

- steering angle;
- driver steering-torque source;
- motor response through Q-axis current.

That means a future H/F `CarState` and Panda safety design do not have to wait for
a field-for-field reconstruction of all 37 configured `0x030` signals. The next
job is to establish exact wire scaling, normal ranges, driver-override thresholds,
and the relation between Q-current response and the command path.

## 4. `0x351`: retained plausibility/debounce status architecture

H `0x351` is a four-byte message. Its relevant H chain is:

- `0x46E0C`: the same unique 86-byte/34-instruction structural family as the old
  EPS plausibility/debounce helper. It retains the counter/hold architecture and
  increments `FEBE7DFB` while the hold condition remains valid;
- `0x46E62`: stages status code/flag state; when its active gate is met it forces
  status `7` and flag `1`;
- `0x47BA2`: packs those values into `0x351`.

The exact H wire positions are:

- B2[7:5] = `FEBE7DD0`;
- B2[4] = `FEBE7DD1`.

This is strong continuity of the **status mechanism**, not permission to copy the
old OEM signal name. The target-native upstream boolean feeding the filter remains
unnamed at this stage.

For the port, `0x351` is therefore a high-value readiness/inhibit discriminator.
A stock-LTA capture should log it alongside the known steering DIDs and fault
transitions. It should not yet be hard-coded as the new `LKA_STATE`.

## 5. `0x394`: retained EPS internal status/fault carrier

H `0x394` is a three-byte message. `0x46E96` projects an internal state rooted at
`FEBE7F58` and copies four neighboring state values into the transmit staging bank.
`0x47ADA` then packs exactly four fields:

- B1[7:6] = `FEBE7DD5`;
- B1[5:3] = `FEBE7DD6`;
- B2[3:1] = `FEBE7DD7`;
- B2[0] = `FEBE7DD9`.

The producer classifies the `FEBE7F58` state into several coarse branches before
staging the adjacent values. This is consistent with the older `0x394` role as an
EPS internal status/fault carrier, and the producer is in the same unique structural
family. We do **not** transfer the older state table or numeric meanings.

This makes `0x394` the best present candidate for generation-native steering
readiness/fault decoding. The decisive next evidence is dynamic correlation against
Techstream DTC/status transitions, EPS assist availability, and stock-LTA engagement
and disengagement.

## 6. `0x030`: still important, but now correctly scoped

H `0x030` is 32-byte CAN-FD with 37 configured signal IDs (`0..36`). The recovered
packer directly emits IDs `0..34`; IDs `35/36` are configured but have no recovered
direct pack call.

The message is visibly mixed rather than one clean old-message replacement:

- it contains multiple angle/numeric families;
- it contains many one-/two-bit state and validity fields;
- some configured fields are runtime-produced while others are default-only or
  runtime-zero in this calibration;
- signal 9 at B7 is generated as the low byte of
  `sum(payload bytes 0..6) + 0x38`.

That B7 behavior is exact. This report does not infer an OEM checksum lineage from
the constant alone.

`0x030` remains necessary to close remaining validity/control-state semantics, but
the efficient order is now:

1. use `0x4A3` for angle / driver-torque-source / motor-response work;
2. use `0x351` and `0x394` to isolate readiness, inhibit, and fault state;
3. use `0x030` to fill the remaining holes rather than treating every field as an
   equally likely replacement for `0x260/0x262`.

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
"what is its physical scale?", or "which Toyota features do the accepted profile
IDs mean?" It is how to operate this known interface safely: remaining
request/validity semantics, cadence and loss behavior, SecOC freshness/key contract,
and the upstream `FRC_P5 -> Brake/EPB -> EPS` producer/routing chain. The literal
OEM engineering-unit name for signal255 is also still unjoined even though its
controller-equivalent degree/radian scale is closed.

## 9. Porting roadmap after this recovery

### State side

The efficient next state work is:

1. validate `0x4A3` B5 scaling against Techstream Steering Wheel Torque over signed
   driver inputs;
2. correlate `0x4A3` B6:B7 against DID `0x1151` and command/current DIDs
   `0x1152/0x1156` under assist and autonomous steering;
3. correlate `0x351` B2[7:4] and all four recovered `0x394` fields against normal,
   standby, active, temporary-fault, permanent-fault, high-driver-torque, and message-
   loss conditions;
4. then decode only the `0x030` fields needed to close remaining validity/readiness
   semantics.

### Command side

The receiver-side command carrier is now identified, so the decisive experiment is
**parameter recovery**, not generic provenance discovery:

- capture protected `0x0B6` during known stock-LTA intervals and correlate signal
  254, signed16 signal 255, signals 262/263, and B6 validity with steering angle,
  `0x1C02`, `0x1152`, and actual Q-current;
- use the now-closed `1024/17870 deg/count` signal255 scale and the closed
  signal254 profile map (`PCS/LDA/Hands Off LTA/LTA-LCA/PDA`) to recover the
  remaining request/validity rules, update cadence, timeout behavior, and normal
  target/rate bounds before any injection attempt;
- recover the B6 SecOC freshness/key/source contract and stock-source suppression
  requirements; and
- acquire/analyze true-TSS3 `FRC_P5` plus Brake/EPB/gateway producer-side firmware
  or synchronized captures to explain how the target is generated and routed to the
  EPS.

The command-side unknown is therefore upstream ownership and safe reproduction of a
known EPS receiver contract, not discovery of another replacement `0x2E4`.

## 10. Production boundary

These findings improve the roadmap but are not yet a Panda safety policy. Before a
real H/F openpilot port, recover and validate:

- exact driver-torque wire scale and override thresholds;
- an actuator-response quantity and its allowable command error;
- readiness and temporary/permanent fault semantics;
- command cadence, loss-of-message behavior, and stock-source suppression;
- actual H/F rate and magnitude limits;
- fallback behavior when comma disappears;
- coexistence with brake/AEB and stock LTA/LDA/LCA functions.

The machine-readable evidence is
`data/generated/corolla_8965H1202000_openpilot_state_bridge.json` with compact
raw-body-bound decompiler evidence in
`data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json`.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [COM-009](../reference/index.md#finding-com-009), [COM-010](../reference/index.md#finding-com-010), [COM-011](../reference/index.md#finding-com-011)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
