# Toyota openpilot porting contract

> **Document type:** architecture / external-prior-art synthesis
>
> **Status:** active roadmap
>
> **Evidence grade:** pinned external implementation + target-native firmware evidence

This report turns comma's existing Toyota support into an explicit checklist for
porting newer Toyota/TSS 3 systems. It deliberately separates two problems that
must both be solved:

1. **transport/authentication:** can we deliver a frame that the receiving ECU
   accepts, including SecOC where applicable; and
2. **vehicle control integration:** do we know the correct command, feedback,
   ownership, suppression, state, fault, timing, and safety contracts for this
   generation.

Passing (1) is not evidence that (2) is solved. Conversely, finding a plausible
TSS3 command payload is not enough unless its producer/route and safe replacement
behavior are understood.

The machine-readable upstream snapshot is
[`../../data/external/opendbc/toyota_porting_contract.json`](../../data/external/opendbc/toyota_porting_contract.json).
It is pinned to commaai/opendbc
`c9b31d21bc396e8958891e271936bdbdf1a6ca93`. Target firmware and captures remain
the source of truth; no classic CAN identifier or signal layout below transfers
to TSS3 without target-native evidence.

On 2026-08-23 the convenience `REFERENCE/opendbc` checkout was also reviewed at
`7343a66d46213d5f73528afc6c6db713ebd88a9d`. Relative to the canonical pin, its
Toyota diff is a platform-flag helper refactor plus firmware-version regex work;
there is no command-surface change that justifies moving the evidence pin for
this report.

### Two orthogonal axes: TSS generation is not SecOC/TSK

Keep the architecture model two-dimensional:

- **TSS/TSS2/TSS3** describes the ADAS/control generation: command vocabulary,
  producer ownership, feedback/readiness state, radar/object interface, UI, and
  vehicle-control behavior.
- **SecOC/TSK** describes security/authentication: protected-frame freshness/MAC
  handling, keys, SecurityAccess/reprogramming policy, and related tooling.

Neither axis determines the other. All three firmware dump families currently
tracked in this repository (Sienna `8965B4512000`, Corolla H, Corolla F) are
**SecOC/TSK evidence**, but that fact alone does not assign a TSS generation.
The Sienna image remains valuable security/control prior art even where its ADAS
architecture is not the true-TSS3 Corolla architecture. Conversely, a TSS3
platform definition must not acquire the `SECOC` flag merely because it is TSS3;
message protection is a separately proved target property.

The curated variant data now records these as separate `adas_generation` and
`security_architecture` columns in
[`../../data/toyota_eps_variant_matrix.csv`](../../data/toyota_eps_variant_matrix.csv).
This distinction is enforced by `tests/verify_toyota_eps_variant_matrix.py`.

## 1. What comma's Toyota implementation is actually modeling

The useful prior art is broader than the DBC.

| Layer | Pinned implementation | Porting lesson |
|---|---|---|
| Platform generation | `ToyotaTSS2PlatformConfig`, `ToyotaSecOCPlatformConfig`, orthogonal Toyota flags | Model architecture explicitly; do not accumulate one-off CAN hacks |
| Vehicle state | `CarState.update()` | Recover the feedback/state contract before declaring control support |
| Lateral controller | `CarController.update()` + `create_steer_command()` / LTA builders | Command format, cadence, driver override, EPS feedback, fault states, and rate limits are one unit |
| Longitudinal controller | `CarController.update()` + ACC builders | Command encoding is inseparable from which ECU owns stock ACC and how its output is suppressed |
| Stock-source replacement | Panda safety `check_relay` substitution; optional radar CommunicationControl | Identify the producer and duplicate-suppression point, not just the receiver |
| Driver UI | `LKAS_HUD` builder and preservation of camera state | A complete port must preserve stock-visible state/alerts rather than only actuate |
| SecOC | `opendbc/car/secoc.py` + three independent Toyota output counters | Authentication wraps selected semantic commands; it does not define the command architecture |
| Safety/tuning | `CarControllerParams`, Toyota safety flags, EPS fault interpretation | Limits must be recovered/validated per platform instead of copied because an old message still exists |

This is the central architectural lesson from openpilot: a Toyota port is a
**control contract**, not a list of arbitration IDs.

A second upstream clue is especially useful for acquisition triage. In
`values.py`, comma explicitly treats forward-camera, forward-radar, and EPS
firmware as platform-code ECUs, and notes that **EPS firmware describes lateral
API changes**, including generations that use LTA for lane keeping and reject LKA
messages. `radar_interface.py` likewise moves the stock track ranges from
`0x210..0x22F` pre-TSS2 to `0x180..0x19F` on TSS2. Generation identification is
therefore part of the control API itself, not bookkeeping after the DBC is known.

## 2. Older Toyota contract, by semantic role

### 2.1 Lateral torque control

The older implementation uses `STEERING_LKA` on CAN `0x2E4` as its torque command.
The classic ADAS DBC defines a 5-byte form; the pinned SecOC profile defines an
8-byte form with the 28-bit authenticator trailer. `CarController.update()` sends
the command every controller frame and applies measured-EPS-torque limits, driver
torque limits, and a high-steering-rate fault-avoidance policy before transmission.

The feedback side is equally important:

- `STEER_TORQUE_SENSOR` (`0x260`) supplies driver torque, EPS torque, and the
  torque-sensor steering angle;
- `STEER_ANGLE_SENSOR` (`0x025`) supplies steering angle/fraction/rate; and
- `EPS_STATUS` (`0x262`) supplies the LKA/LTA fault-state interface.

Our Sienna `8965B4512000` work already recovers the target-native `0x2E4`
`STEER_REQUEST` / signed torque path and its `0x262` status consequence. That is
exactly the sort of role-level join the prior art says must exist. The tracked
Corolla H firmware is the counterexample to blind transfer: its active SecOC
queue has no `0x2E4` steering profile even though older Toyota support uses this
ID extensively.

### 2.2 LTA / angle control

TSS2-era openpilot models angle control as a second path rather than a variant of
the torque signal:

- `STEERING_LTA` (`0x191`) carries the angle/request/mode/wind-down state and a
  classic Toyota checksum; and
- the SecOC profile additionally emits authenticated `STEERING_LTA_2` (`0x131`).

The controller sends this pair on every second controller frame when applicable.
Angle mode also changes the expected actuator delay/limit timer and requires the
more accurate torque-sensor steering-angle measurement to have initialized.

This history matters because the mere existence of an LTA path did not make it
the final production choice: upstream later switched SecOC platforms and RAV4
TSS2 back to torque control (`5e71fde2`, `e76c2cf5`) based on vehicle behavior.
At the pinned revision, Panda's Toyota safety hook goes further: it accepts the
`0x131` frame shape but explicitly blocks **all** `STEERING_LTA_2` actuation
(request bits or a nonzero angle). For a TSS3 port, an authenticated angle-looking
command is therefore a lead, not a finished or upstream-safety-approved lateral
interface.

Our exact Sienna donor contains a real protected `0x131` LTA command path and
converges it with the protected `0x2E4` torque mode. Exact Corolla H removes both
classic command profiles, but the deeper fixed-map audit now recovers the replacement
receiver contract on protected FD `0x0B6`: signal254 B3[5:0] is a cooperative
mode/control ID and signal255 B4:B5 is a signed target-steering-angle command.
`C9DB0/C9E54` form target state, `CBD7E/CB096` independently form measured angle
from FD `0x025`, and `CA138` applies the same gain to both before computing the
control error. The result conditionally reaches `C2A8`, general DID `0x1C02 Command
Value Torque`, and DID `0x1152 Command Value Current (Q Axis)`. B6 signals262/263
also percentage-modulate internal contributors. The physical relation is now closed
without importing the old `0x131` scale: FD025 coarse/fraction feedback is
1.5 deg + 0.1-deg fraction, and the matched controller makes signal255
`1024/17870 deg/count` (`~1.000121519 mrad/count`) controller-equivalent. The
receiver contract is now stronger still: Techstream's `Target Lateral ID` dictionary
defines `0=No Request (Manual Operation)` and closes the accepted H active requests
as `1=PCS`, `4=LDA`, `10=Hands Off LTA`, `11=LTA/LCA`, and `19=PDA`; PDU42's
receive deadline reloads to **7 TAUJ0-CH3 foreground ticks**, first expiry disables
cooperative selection through the slot-18 receive-status path, and signal261 is a
modulo-64 rolling sequence counter with effective-gap cap `8`. The CH3 wall-clock
period is not statically known. The remaining problem is therefore safe reproduction
of a known EPS receiver contract — exact OEM signal255 unit naming, sender wall-clock
cadence, exact secondary-field semantics where safety-relevant, SecOC freshness/key
state, stock-source suppression, and the upstream payload/SecOC producer contract.
Techstream now verifies the Corolla P5 module topology as `FRC_P5` 498 + category-435
`ABS_P5`/Brake-EPB + `EMPS_P5` 405, but not a byte-level forwarding transform or
SecOC signer — so the remaining work is not discovery of another steering message,
its scale, request selector, or loss rule.

### 2.3 Longitudinal control

The older contract uses classic `ACC_CONTROL` (`0x343`) and, on the pinned SecOC
profile, authenticated `ACC_CONTROL_2` (`0x183`). In the secure implementation,
`ACC_CONTROL` is still emitted but its main acceleration request is zero; the
signed acceleration command moves to the MACed `ACC_CONTROL_2`. Openpilot emits
longitudinal control on every third controller frame.

More important than the IDs is the ownership model in `interface.py` and
`carstate.py`:

- on ordinary TSS2, **the camera is treated as the stock longitudinal-control
  source**;
- `RADAR_ACC` marks a different architecture where the radar owns ACC traffic;
- enabling openpilot longitudinal on that architecture can require disabling
  radar transmission with UDS CommunicationControl; and
- the safety layer blocks stock copies of messages that openpilot replaces.

That is the roadmap for TSS3 longitudinal work. We must identify both the new
command contract and the stock producer/suppression point. A frame that makes
acceleration change while the stock producer is still active is not a viable
production integration.

The existing Corolla public-route evidence is already a hard warning: actual
CAN `0x183` traffic there is **64-byte CAN-FD**, not the classic 8-byte
`ACC_CONTROL_2` shape. The number `0x183` therefore has no portable semantic
meaning by itself.

### 2.4 Engagement, faults, and driver state

The old port does not infer readiness from a successful command transmission.
It consumes cruise availability/active/standstill/fault state, brake and gas,
wheel-speed validity, driver steering torque, accurate angle initialization,
and EPS LKA/LTA state.

The pinned implementation classifies EPS steering states `0/9/11/21/25` as
temporary faults and `3/17` as permanent faults. Those numeric values are
**prior-art probes only** for TSS3. What transfers is the requirement to recover:

1. the new EPS/controller readiness state machine;
2. temporary versus latched fault behavior;
3. driver override and torque blending semantics;
4. initialization prerequisites; and
5. the exact state used to decide whether openpilot may engage or must disengage.

### 2.5 Driver UI and stock coexistence

Older Toyota support also replaces/preserves `LKAS_HUD` (`0x412`) state, emits
alerts promptly, and keeps selected camera-originated lane-sway fields. This is
not cosmetic: it is part of making openpilot coexist predictably with the rest
of the vehicle.

For TSS3 we should explicitly recover which ECU now owns lane/LTA/LCA status and
which messages drive the cluster, rather than deferring all UI work until after
steering actuation.

## 3. SecOC is one column of the porting matrix

Pinned opendbc signs three independent command streams:
`STEERING_LKA`, `STEERING_LTA_2`, and `ACC_CONTROL_2`. Each has its own message
counter, while all three consume the live trip/reset synchronization state. Our
firmware work substantially exceeds that upstream implementation on receiver,
key-management, and bypass analysis.

But the architectural relationship is simple:

```text
planner/controller semantic command
        ↓
vehicle-generation command builder + limits
        ↓
SecOC wrapper, if this command is protected
        ↓
correct physical bus / producer replacement
        ↓
receiver acceptance + control-state consequence
```

Our SecOC work operates primarily on the third and fifth boxes. The TSS3 porting
work must recover the second and fourth boxes for each new generation as well.

## 4. Current target map against the old contract

| Semantic role from prior art | Sienna `8965B4512000` | Corolla H / Span family | True-TSS3 work still required |
|---|---|---|---|
| Platform identity / generation | exact firmware identity and P1M-E profile known | exact H and Span corpora known | bind each candidate vehicle to FRC/EPS/gateway firmware and real bus topology |
| Torque steering command | protected `0x2E4` request/torque path recovered | classic `0x2E4` absent; H/F instead receive protected B6 target-angle control | do not port torque limits/scales; derive H/F-native limits and finish SecOC sender/producer contract |
| LTA/angle command | protected `0x131` path recovered and converges with torque mode | active queue lacks `0x131`; protected `0x0B6` signal255 is target angle, signal254 is the OEM request selector, receiver loss is 7 foreground ticks, and signal261 is modulo-64 sequence state | module topology is now `FRC_P5` 498 + `ABS_P5`/Brake-EPB 435 + `EMPS_P5` 405; recover sender wall-clock cadence, limits, byte-level producer/forwarding transform, and SecOC sender ownership; do not transplant old `0x131` wire scaling |
| Steering feedback | `0x025`, `0x260`, `0x262` roles strongly mapped | H `0x025` is FD angle/rate; state roles split across `0x4A3/0x351/0x394/0x030` | derive H/F-native driver override, response, readiness/fault, and validity semantics |
| Longitudinal command | older SecOC DBC provides a useful comparator, not an EPS-local proof | route `0x183` is 64-byte CAN-FD and disproves old wire-shape transfer | locate ACC producer, target command, feedback, stock suppression, AEB coexistence |
| Stock producer ownership | old openpilot architecture gives camera/radar replacement model | physical Toyota-B/network differences already observed | map FRC/radar/gateway ownership and safe duplicate blocking for each command family |
| UI / alerts | older `0x412` is historical reference | old-camera U023A87 path is disabled residue in H | identify FRC/cluster LTA/LDA/LCA status and warning outputs |
| Authentication | Sienna SecOC receiver and bypass paths deeply recovered | command carrier is secured B6 using H slot-4 SecOC configuration; application signal261 sequence handling is separately closed | recover **SecOC** freshness/source behavior and production-safe signing/key path before actuation; do not confuse the application 6-bit sequence counter with SecOC freshness |
| Techstream producer probes | older diagnostic controls are only contextual | FRC fixed vibration routines and category-435 ABS/Brake Active Tests are now cataloged; the latter are brake-actuator-only and expose no named steering setpoint writer | use these as capture/probe triggers only; normal B6 payload production still requires FRC/ABS firmware or synchronized traffic |

### 4.1 Route-backed Corolla implementation readiness

The role checklist is now joined to actual whole-vehicle traffic in
[`corolla_tss3_opendbc_readiness.json`](../../data/generated/corolla_tss3_opendbc_readiness.json).
This is deliberately **not** an H-firmware-to-route join. The public 2023 Corolla
route has forced `TOYOTA_COROLLA_TSS2` `carParams` and no `carFw`; it is an
externally attributed whole-vehicle TSS3 Corolla oracle, while H/F firmware facts
remain exact to their own specimens. Span's separately supplied July-29 driving
rlog is a second vehicle-level oracle, not an exact F-image join: its embedded
`carParams` is `MOCK`, its logging dongle (`67fd5b833889fedf`) differs from the
later firmware-dump preflight dongle (`23257862c6bf2f83`), and it contains no usable
F181 identity. Contributor attribution therefore does not collapse those two Span
artifacts into one exact ECU specimen.

The visibility mismatch is stronger than a simple identity caveat. Exact H/F
firmware receives the protected SecOC set `0x00F/8`, `0x0D7/32`, `0x0B6/32` and
transmits `0x030/32`, `0x351/4`, `0x394/3`, `0x4A3/8`, `0x4C8/8`. The public route
exposes `0x00F` (588 frames) and `0x0D7` (2,943 frames) but **zero `0x0B6` frames**,
and from the H/F Tx set it exposes only `0x030` (5,888 frames). That surviving
`0x030` join is stronger than ID/DLC alone: **all 5,888 frames satisfy the exact
H/F firmware-derived byte-7 rule `B7 = (sum(B0..B6) + 0x38) mod 256`**. Span's
moving rlog independently repeats the same pattern: `0x00F` 600 frames,
`0x0D7` 3,000, zero B6, and only `0x030` from the H/F Tx set; all **6,000/6,000**
`0x030` frames satisfy the same exact-H/F rule. Treat these as format/producer-family
continuity, not firmware-identity proof.

The Span visibility result must also be read with the harness topology correctly.
All **599** Panda-state samples are `ELM327 param=1`, `harnessStatus=flipped`,
`controlsAllowed=false`. `harnessStatus=flipped` is the Panda/USB-C harness
**orientation**, not the physical Toyota-B CAN0/CAN1 pin repin. ELM327 param 1
keeps logical bus 1/FDCAN2 on the **normal harness CAN1 wires**, so the unmodified
harness can passively observe that unsplit stock network. The maintainer reports
that Span had **not** physically swapped the Toyota-B CAN0/CAN1 pairs for this
capture. That missing repin prevents putting the network on the CAN0/CAN2 relay
pair for normal comma interception, stock-source suppression, and camera-side vs
car-side attribution; it does **not** by itself make stock CAN1 traffic invisible
to logical bus 1. Therefore B6's absence is a real segment-level negative on the
observed stock CAN1 network, but it still cannot distinguish stock-LTA/request
gating or specimen/segment differences because no stock-LTA off→active→off
transition or exact F181 join is present.

What the exact segment-0 rlog *does* close is the old-openpilot role migration:

- **Reusable state/security plumbing exists.** On logical bus 1 the route carries
  `0x00F/8` (~9.6 Hz), `0x0AA/8` (~96 Hz), `0x101/8` (~48 Hz),
  protected `0x116/8` (~41 Hz), and `0x176/8` (~30 Hz). The old four
  `0x0AA` wheel-speed fields decode coherently over `0..~41.6 km/h`; the old
  `0x101` brake bit toggles; the old `0x116 GAS_PEDAL_USER` field is dynamic; and
  **all 1,855 `0x176` frames pass the existing Toyota additive checksum**. Cruise
  is never engaged in this segment, so `0x176` active-state semantics still need
  an exact-target transition capture. `0x00F` is reusable because the target is
  SecOC-protected, not because it is TSS3.
- **`0x025` is evolutionary at the signal level but not the PDU level.** The route
  carries `0x025/32` at ~96 Hz. Exact H firmware independently proves that the
  older signed-12 coarse angle, signed-4 fraction, and signed-12 rate positions
  survive inside the 32-byte FD PDU; the public route decodes a real dynamic
  range of `-471..348 deg` and `-270..410 deg/s`. A TSS3 DBC can therefore reuse
  those proved fields while defining the correct 32-byte message rather than
  pretending the old 8-byte PDU survived.
- **Several normal `CarState` roles move, but gear is now a concrete reuse
  candidate.** The 2023 route has no incoming `0x127`, `0x1D3`, `0x260`, `0x262`,
  `0x283`, `0x320`, `0x343`, `0x399`, `0x3BC`, or `0x3F6`. Span's driving rlog
  independently restores `0x127/8`: all **3,662/3,662** frames pass Toyota's
  existing additive checksum and the existing `GEAR_PACKET_HYBRID.GEAR` bitfield
  decodes raw `3 = D` throughout. That proves carrier, bit position, checksum and
  the D enum on this capture; P/R/N/B transitions remain untested. Exact H partially
  closes the steering replacements (`0x4A3`, `0x351`, `0x394`, mixed FD `0x030`),
  while cruise availability/set speed/fault/follow-distance, exact driver-torque
  scale, and production readiness/fault semantics still require vehicle-level
  evidence.
- **Same ID is not enough for body/UI reuse.** `0x3B7`, `0x411`, `0x412`,
  `0x610`, `0x614`, `0x620`, and `0x622` remain 8-byte frames, but most relevant
  transitions are static in this segment. One concrete warning is `0x610`: the
  old `UNITS` layout decodes value `7`, outside the old `1..4` domain. Reuse only
  individually validated fields.
- **The forced old Corolla profile demonstrably does not work as a parser.** Across
  5,639 logged `carState` samples, **`canValid=false`** and logged vehicle
  speed and steering state remain zero despite coherent raw TSS3 traffic. This
  is direct evidence for a generation-specific bus/DBC/CarState path, not just a
  theoretical DBC difference.

The ADAS/radar side shows an even harder generation break. The route extraction
uses **incoming CAN only (`src<128`)**; Panda returned/Tx echoes (`src=bus+128`) and
rejected echoes are excluded, so the baseline below is not contaminated by Panda
transmit returns. Public-route bus 0 has `0x123/16` (versus older Toyota radar status
`0x123/7`) and an exact 22-ID/DLC FD baseline:

```text
020/12  123/16  160/32
180..18B/64  18C/48  1A0/48
200/64  201/64  230/64  440/32  450/32
```

The retained Span 2025 source ZIP contains `tsk/uds-sweep/ready_capture.ndjson`
(SHA-256 `182ae388...d0ae9`, 75,192 rows). Despite its filename, the source
investigation later concluded this capture was probably **Not Ready to Drive**;
it is therefore structural evidence only. Its buses 0 and 2 carry the same
22-ID/DLC set and, within that capture, are payload-for-payload identical. The
2025 cadences also form stable families: `0x123` ~10 Hz, `0x160` ~40 Hz,
`0x180..` ~20 Hz, `0x200/0x201` ~10 Hz, and `0x440/0x450` ~2 Hz.

Span's separately supplied moving rlog now removes the NRtD-only caveat from the
**geometry** result. During its ~60-second incoming-CAN window, old `0x0AA` wheel
speeds reach ~24 km/h, brake/gas/steering are dynamic, and buses 0 and 2 again
carry exactly the same 22 ID/DLC shapes with **byte-identical payload sequences**.
The exact same 22-ID/DLC baseline also appears on the public 2023 route. Thus the
geometry persists across a real driving segment as well as the earlier static
capture. This is still a TSS3 Corolla network-geometry invariant, **not** a
field-semantics or producer-ownership proof.

This also bounds the community `0x18A` lead more sharply. **Thirteen** TSS3 FD
PDUs, `0x180..0x18C`, land inside comma's older TSS2 radar-track numeric namespace
`0x180..0x19F`; their geometry has changed radically from the old 8-byte tracks
(`0x180..0x18B` are now 64 bytes and `0x18C` is 48 bytes). This is a concrete
radar/object-family search prior, not proof that any one of these frames is a radar
track. In particular, `0x18A` is one 64-byte, ~20-Hz member of that family **and**
the community lateral-control heatmap lead. Those are competing hypotheses. Do not
assign producer, fields, integrity, or command ownership until firmware or synchronized
traffic joins one of them to a real source/consumer.

Finally, Panda topology is part of the port. Current Toyota safety consumes its
checked state inputs on logical bus 0, while the directly useful state above is
observed on logical bus 1. Official Toyota-B hardware makes CAN0/CAN2 the
intercept-relay pair and CAN1 an unsplit network. `ELM327 param=1 + logical bus 1`
is sufficient for direct diagnostics and passive observation of that stock CAN1
network; it is **not** relay-topology-equivalent to the physical CAN0/CAN1 repin.
Therefore "parse bus 1" is not itself a production architecture. We still need a
relay-correct capture to establish the B6 producer side, duplicate-suppression
point, and safe forwarding/transmit topology.

**What can be scaffolded now:** an explicit TSS3 control-generation axis separate
from `SECOC`, a 32-byte `0x025` definition with the proved steering fields,
carefully gated reuse candidates for `0x0AA/0x101/0x116/0x176`, and a TSS3
`0x127 GEAR_PACKET_HYBRID` reuse candidate whose checksum/bitfield/D value are
already dynamically supported. What cannot yet be made production-ready is the
lateral sender/safety contract, complete `CarState`, radar parsing, or longitudinal
control. The artifact records the exact blockers.

## 5. The concrete TSS3 investigation roadmap

The next TSS3 analysis should proceed in this order. Each stage produces facts
needed by the next; none is replaced by possession of a SecOC key.

### A. Identify owners before messages

For one exact vehicle, inventory the FRC, EPS/EMPS, radar/ADS if present, gateway,
and brake/ACC controller software IDs and the buses they actually transmit on.
Use simultaneous bus capture and ECU isolation/diagnostics where safe to separate
physical producer from gateway mirrors.

This directly mirrors comma's `TSS2` versus `RADAR_ACC` split and prevents us from
building around the wrong ECU.

For the Corolla family, the immediate dynamic target is now narrower than "get a
READY capture." Span's July driving rlog already supplies moving whole-vehicle
state, validates substantial legacy `CarState` reuse, and shows the 22-PDU FD
geometry under motion. What it does not supply is exact firmware identity, stock
LTA activation, or relay-correct interception topology.

The highest-value next capture is therefore a **firmware-identified H/F-family
vehicle with the Toyota-B CAN0/CAN1 pairs physically repinned onto the CAN0/CAN2
relay topology**, `carFw`/F181 preserved, and all buses logged while exercising
stock LTA off→active→off, ordinary driver steering, cruise main/engage/cancel,
brake/gas, and stationary P/R/N/D transitions. That one capture can simultaneously
close B6 sender cadence and producer side, stock-source suppression, remaining
gear enums, cruise-state replacements, safety-bus placement, driver override,
and readiness/fault behavior.

### B. Acquire and analyze `FRC_P5` and category-435 Brake firmware

Techstream has already narrowed the strongest true-TSS3 lead: generation-20
category 498 `FRC_P5` (**Front Recognition Camera 2**) owns the diagnostic-domain
LTA/LDA/LCA surface and exposes dedicated TSS3 plugin roles. Its fixed LTA
Steering Vibration routine `0x1588` is a useful synchronized stimulus even though
it is not itself a setpoint writer.

Acquire matched `0792` FRC and `07B0` category-435 Brake/EPB firmware for a known TSS3 vehicle and recover:

- Tx PDU/message descriptors and CAN/CAN-FD bus assignment;
- any target-angle, target-torque, curvature, lateral-acceleration, control-mode,
  validity, counter, freshness, and authenticator fields;
- the internal LTA/LDA/LCA state machine that gates those outputs;
- the downstream destination/receiver and expected acknowledgement/status; and
- any gateway/routing indirection between FRC and EPS.

The community `0x18A` 64-byte lead remains only a lead until this producer/field
join exists.

### C. Reconstruct the lateral closed contract

For each candidate command, correlate a known stock-LTA interval across:

1. FRC internal target/control state;
2. raw full-bus command traffic;
3. EPS receive state / command precursor;
4. EPS torque/current/control-state response; and
5. status/fault frames visible to openpilot.

A candidate graduates only when command value, enable/mode, cadence, validity,
feedback, and fault behavior are all joined. This is the TSS3 equivalent of the
older `STEERING_LKA` + `STEER_TORQUE_SENSOR` + `EPS_STATUS` contract.

### D. Recover longitudinal as a separate architecture

Do not assume the lateral producer owns ACC. Establish whether FRC, radar, ADS,
or another controller sends the stock acceleration/spacing command. Then recover:

- acceleration/deceleration setpoint and enable/cancel semantics;
- lead/distance/standstill behavior;
- brake/gas/AEB arbitration and fault state;
- command cadence and integrity/authentication; and
- the safe stock-source disable or Panda forwarding-substitution point.

Only after this should an opendbc TSS3 longitudinal builder or safety whitelist be
written. This is tracked separately as
[OQ-052](../status/OPEN_QUESTIONS.md), so completion of the FRC lateral path cannot
accidentally be treated as completion of the TSS3 vehicle port.

### E. Recover the production safety envelope

Measure or statically recover the TSS3 EPS/controller's own command bounds and
fault thresholds: rate, magnitude, driver override, steering-rate behavior,
message-loss timeout, mode-switch behavior, and recovery after invalid traffic.
Comma's older values are useful experiment bounds, not TSS3 constants.

### F. Encode support as a generation-specific platform contract

Once the facts above exist, add TSS3 support in the same architectural shape as
upstream Toyota support rather than scattering special cases:

- a TSS3 platform/config flag or class;
- generation-specific DBC/CAN-FD definitions;
- `CarState` parsing for the new feedback/readiness contract;
- `CarController` builders and cadence for lateral, longitudinal, and UI;
- source-ownership/suppression initialization;
- Panda safety rules for only the proven messages and limits; and
- SecOC signing/bypass integration as the protection layer for whichever of
  those messages actually require it.

## 6. Minimum completion criteria for a production TSS3 port

A platform is not "supported" merely because steering can be made to move. For
both lateral and longitudinal, require all of the following before treating the
port as production-ready:

- exact vehicle/ECU firmware identity;
- exact command producer and physical route;
- command field layout, cadence, counters, and integrity/authentication;
- receiver-side acceptance and control consequence;
- feedback/readiness/fault state decoded into `CarState`;
- driver override and actuator limits characterized;
- stock producer safely suppressed or coexistence proved;
- loss-of-comma / invalid-command behavior returns to stock-safe behavior;
- AEB/brake/ACC and LTA/LDA/LCA coexistence checked;
- cluster/UI warnings and state remain coherent; and
- Panda safety enforces the recovered envelope independently of openpilot.

This completion definition is the practical connection between the two work
streams: **When the target command is SecOC-protected, SecOC makes that command deliverable;
the generation-specific control contract tells us what valid command to send and
how to integrate it safely.**

## 7. Upstream history as a process template

The pinned repository history reinforces the staged approach:

- `e1ce3619` (2024-10-01): RAV4 Prime/Sienna SecOC DBC definitions;
- `fb4ac268` (2024-10-03): separate SecOC longitudinal command definition;
- `0ebc4cb4` (2024-10-07): Sienna secure-platform integration;
- `4d93a559` (2025-09-29): SecOC longitudinal control added later;
- `5e71fde2` (2026-01-29): SecOC platforms moved back to torque control; and
- `e76c2cf5` (2026-01-30): RAV4 TSS2 likewise moved to torque control.

The lesson is not to reproduce those exact stages. It is to preserve their
evidence discipline: wire vocabulary, state/ownership, safe control, then broader
features — with later vehicle behavior allowed to correct an apparently usable
command path.

## 8. Related local evidence

- [control-partition.md](control-partition.md) — recovered Sienna steering/motor
  control graph.
- [../communications/application-rx.md](../communications/application-rx.md) —
  exact Sienna receive surface.
- [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  — newer Corolla counterexamples to old TSS2 ID/shape assumptions.
- [../variants/toyota-eps-variant-comparison.md](../variants/toyota-eps-variant-comparison.md) —
  exact-EPS family comparison.
- [../tooling/techstream.md](../tooling/techstream.md) — `FRC_P5` TSS3 diagnostic
  semantics and fixed-routine evidence.
- [../status/PRIORITIES.md](../status/PRIORITIES.md) — current execution queue.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [ARCH-016](../reference/index.md#finding-arch-016), [COM-013](../reference/index.md#finding-com-013)
- Corrections with this document as canonical home: [CORR-108](../reference/index.md#correction-corr-108)
<!-- knowledge-cross-references:end -->
