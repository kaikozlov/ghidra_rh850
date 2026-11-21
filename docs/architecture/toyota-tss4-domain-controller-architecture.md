# 2026 RAV4 / TSS4 ADAS-domain-controller architecture

**Status:** production-EWD + GTS+ + external-source architecture note, researched through 2026-11-21.

The 2026 RAV4 introduces a materially different ADAS hardware boundary from the
TSS3 vehicles analyzed in this repository. Toyota's production EWD names a
standalone **ADAS Domain Controller ECU Assembly** and wires the forward camera,
millimeter-wave radars, side radars, blind-spot sensors, ultrasonic sensors,
driver-monitor camera, and parking-view cameras into or through that controller.
The EPS and brake actuator remain separate vehicle-motion ECUs.

This is a **functional-domain consolidation**, not evidence that the whole
vehicle has become a zonal architecture or a single central computer.

## Evidence boundary

The production observations below come from three 2026 RAV4 EWD extracts and a
Toyota/Chilton vehicle-wide CAN system diagram supplied for this investigation:

- `ADAS-U.pdf`
- `EPS-U.pdf`
- `MPX-CAN-HEV-U.pdf`
- Chilton `Repair content for 2026 Toyota RAV4.pdf` (2026-11-21 capture)

Those source files are not committed here. Pin names and topology are EWD/repair-
manual facts.
The division of perception, planning, and request generation comes from the
patent sources below and is an architecture match, not a recovered RAV4 software
implementation.

Toyota publicly identifies the 2026 RAV4 as the first Toyota to use Toyota
Safety Sense 4.0 and Arene. Toyota says TSS4 updates hardware and detection
capability and that Arene underpins the RAV4 safety software.

## 1. Production RAV4 topology

The ADAS EWD identifies:

`D85(A), D87(B), J83(C), J84(D), J85(E), J113(F), J114(G)`
**ADAS Domain Controller ECU Assembly**.

The controller has multiple independent CAN interfaces and a large set of
direct sensor/peripheral interfaces.

### Sensor and peripheral fan-in

The ADAS Domain Controller is directly joined to the following systems in the
ADAS EWD:

- forward sensing camera (`FCM`);
- front millimeter-wave radar;
- left and right front-side radars;
- left and right rear-side radars / BSM sensors;
- front and rear ultrasonic sensor chains;
- driver-monitor camera;
- front/rear/left/right panoramic-view cameras;
- light parking-assist circuitry and mirror-related park/BSM interfaces;
- radio/display receiver through a separate shielded interface.

The radar links are explicitly **ADU-local CAN**, not Global CAN. The ADAS EWD
closes the exact `J83(C)` pin map:

| ADU local CAN | J83(C) pins | Sensor endpoint |
|---|---|---|
| `CA2H/CA2L` | 13/12 | A95 front millimeter-wave radar, `CA1P/CA1N` pins 3/4 |
| `CA3H/CA3L` | 15/14 | M6 blind-spot / rear-side radar LH, `CA1P/CA1N` pins 6/2 |
| `CA4H/CA4L` | 9/8 | M5 blind-spot / rear-side radar RH, `CA1P/CA1N` pins 6/2 |
| `CA5H/CA5L` | 17/16 | A68 front-side radar LH, `CA1P/CA1N` pins 6/2 |
| `CA6H/CA6L` | 11/10 | A69 front-side radar RH, `CA1P/CA1N` pins 6/2 |

Each radar is therefore on a dedicated point-to-point ADU CAN pair; the
front-side and rear-side hardware-fault reporting groups the corresponding LH/RH
links. The paired sensor definitions are strongly symmetric: after normalizing
LH/RH wording, `CCFDRSF_A/B_P6` share all 113 Data List rows and
`SODCM_A/B_P6` likewise share all 113. This makes physical-port identity and
reuse of a common sensor/message schema across left/right positions a natural
fit for the dedicated-link topology. The separate links also isolate radar-bus
faults and avoid arbitration between independent high-rate sensor streams.

The same `J83(C)` connector also carries the ADU's two global vehicle CAN
interfaces: `CA1H/CA1L` on pins 2/1 and `CA9H/CA9L` on pins 4/3.

`ADCU_P6` has independent hardware-fault DTCs for:

- `C1C9849 ADAS Domain Controller Local CAN Circuit (Front Millimeter Wave)`;
- `C1C9649 ... Local CAN Circuit (Front Side Millimeter Wave)`;
- `C1C9749 ... Local CAN Circuit (Rear Side Millimeter Wave)`.

The radar-side databases independently name their ADU communication dependency:
front radar `FDRS_P6` carries `U010487 Advanced Driver Assistance System /
Missing Message`; the front-side radar databases carry
`C1A6D87/C1A6E87 ADAS Domain Controller to Front Side Radar LH/RH / Missing
Message`; and the rear-side radar databases carry
`C1A7A87/C1A7B87 ADAS Domain Controller to Rear Side Radar LH/RH / Missing
Message`. The side-radar databases also expose `0x9007 ADAS Domain Controller
Generation Information`.

The forward camera is not on one of those CAN pairs. The EWD draws a dedicated
point-to-point `FCM` line from ADU connector `D85(A)` pin 2 directly to the
one-pin `L21 Forward Sensing Camera` connector. It likewise draws dedicated
single signal links `PVFR/PVRR/PVLH/PVRH` from the ADU to each panoramic-view
camera, while the driver-monitor camera has dedicated `DMC`, `DLED`, and
`GND3` connections. The ultrasonic sensors are grouped into four direct
three-wire chains (`S1/E1/B1` through `S4/E4/B4`) rooted at the ADU.

The exact payload transported by the direct `FCM` connection is not established
by the EWD. The single named conductor is enough to exclude ordinary two-wire
CAN at that interface, but it does not identify the camera transport or how much
processing remains in the camera head.

### Vehicle-network attachment

The vehicle-wide CAN EWD places the ADAS Domain Controller on the global CAN
network through connector `J83(C)`.

One side of the controller (`CA1H/CA1L`) joins No. 6 Global CAN Junction
Connector `J94`, which in turn connects to Network Gateway ECU `D101`.
A second controller interface (`CA9H/CA9L`) continues toward No. 11 Global CAN
Junction Connector `J99`.

The Toyota/Chilton vehicle-wide system diagram supplied on 2026-11-21 resolves
those attachments to **Global Bus 1** and **Global Bus 8** respectively. The
same diagram places the rack EPS together with both brake controllers on
**Global Bus 4**: `BRK1` is the master-cylinder brake-booster assembly,
`BRK2` is the brake-actuator assembly, and `EPS` is the rack-and-pinion power-
steering gear. `BRK1` and `BRK2` are additionally attached to the separate
Powertrain Local Bus with the hybrid/powertrain controllers.

Thus the ADAS Domain Controller is not physically attached to the EPS/brake
Global Bus 4. An ADU-originated final steering PDU would have to cross the
Network Gateway, whereas the brake/VMM candidates and EPS are already peers on
the same global chassis bus.

This makes the ADAS Domain Controller a networked vehicle ECU, not merely a
camera module.

### `ZN` is the integrated body / zone-controller assembly, not VMM

The vehicle-wide diagram repeats code `ZN` on Global Buses 1, 3, and 5 and names
it **Integrated Body Control ECU Assembly**. Its GTS display expands that one
physical assembly into `Integrated Body No1` and `Integrated Body No2`. GTS+ maps
those logical controllers to generation-22 `Zone_ECU_A_P6.ddb` (category 6033)
and `Zone_ECU_B_P6.ddb` (6034).

Their diagnostic vocabulary is body/zone control: steering-wheel switches,
lighting, mirrors, wipers, brake-hold/parking-brake switches, stop-lamp state,
steering heater, power/OTA/body operating state, and related I/O. They monitor
both Brake and EPS (`U012987` / `U013187`), but expose no Vehicle Movement,
Vehicle Motion Control, lateral/longitudinal arbitration, or Dynamic Domain
Controller surface. `ZN` is therefore the P6 body/zone-control domain, not the
Vehicle Movement Manager.

### Actuators remain separate

The EPS EWD still shows a standalone Rack & Pinion Power Steering Gear Assembly
`B52(A), z9(B)` with its own CANH/CANL and steering-torque sensor.

The vehicle-wide CAN EWD likewise shows the rack EPS and brake actuator as
separate ECUs on the motion-control networks.

Current NA GTS+ independently identifies the new steering controller as
category `6006`, `PSCM_A_P6.ddb`, Toyota name **EMPS (P6)**, generation 22.
The `Rav4 HEV` vehicle type 12887 mounts it in install set 8669 alongside
`BSCM_A/B_P6`, `ADCU_P6/P6F`, and the P6 front/side/rear radar families. Across
the current NA master, every `ADCU_P6` install row also contains
`PSCM_A_P6`; the production-style architecture covers both `Rav4 HEV` and
`Rav4 PHEV`. This is a new P6 EPS diagnostic family rather than reuse of
`EMPS_P5`.

Therefore the architectural change is not "ADAS controller contains the EPS."
The centralized controller owns a large part of the ADAS compute/application
domain while motion actuation remains distributed. The GTS category establishes
the new EPS software/diagnostic generation, not its MCU ISA or ICU-S/ICU-M
implementation.

### P5 -> P6 EPS database continuity

The P6 rename is much larger than the underlying semantic change.
`EMPS_P5.ddb` is 85,846 bytes and `PSCM_A_P6.ddb` is 62,108 bytes, but the
P6 database retains most of the P5 steering vocabulary:

- all **166** P5 DTC codes survive in P6; P6 adds seven codes, and 160/166
  retained codes keep the same description and failure text;
- P6 has 117 unique primary Data List DIDs, **108 (92.3%)** of which already
  exist in P5;
- of 144 P6 Data List rows, **118 (81.9%)** retain the same primary DID and
  Toyota field name as P5;
- every one of those 118 retained rows keeps the same bit geometry, and
  **105/118** keep the same scaling, signedness, unit, ranges, and enum
  semantics.

The seven added P6 DTCs are two torque-sensor supply faults, one turn-counter
fault, and four main/sub-bus communication faults naming a **Dynamic Domain
Controller ECU**. If the seven additions are removed, the remaining P6 DTC
codes appear in exactly the P5 order.

The new P6 primary DIDs are the standardized `0xA002/0xA003/0xA007..0xA00C`
and `0xA800` housekeeping/time/vehicle-state family. P6 removes 71 P5 primary
DIDs, heavily concentrated in the older backup-power, steer-by-wire,
reaction-force, and Advanced-Drive diagnostic block `0x1CCB..0x1CF3`. The
specific P5 `0x1CEE/0x1CEF` target-value group—`Target Lateral ID`,
`Target Steering Angle After Output Compensation`, and
`Advanced Drive Target Steering Angle`—has no P6 EPS Data List counterpart.
The coarse EPS-side state did not disappear: P6 retains `0x106A Cooperation
Control State` with the same `0=Cooperation Control, 1=Other than Cooperation
Control` dictionary as P5, and the field also survives in the P6 EPS FFD/RoB
surfaces.

The table schema is likewise evolutionary. Sixteen table types are shared.
P6 drops the old P5 behavior-record tables 87/88/153 and adds the P6
`CDbRoBDiagCodeTable` / `CDbRoBFreezeFrameTable` pair 163/164. The common
signal-group, trigger, DTC-status-mask, and behavior-signal-check records are
largely or completely inherited. `PSCM_A_P6.ddb` and `PSCM_A_P6F.ddb` are
byte-identical in the current NA corpus.

This makes `PSCM_A_P6` look like a pruned and revised successor to the P5
steering definition, with a new P6 diagnostic/recorder ABI and a narrower
EPS-local target-value surface rather than a clean-sheet EPS diagnostic model.

### P6 lateral request and arbitration state moved into the ADAS recorder

The detailed lateral-control state did not disappear with `0x1CEE/0x1CEF`.
Toyota moved the rich request/result observability into the P6 ADU/ADAS-domain
recorder. The recovered PCS Data Viewer P6 schema exposes several distinct
stages:

- `1B40` is the LTA client record: `LTA lateral control request ID`, separate
  signed 0.001-angle fields named `LTA steering angle request (ADU)` and
  `LTA steering angle request (EPS)`, plus steering-assist and damping gains and
  LTA coordination/mode fields. `1C48` carries the analogous LCA-labelled
  fields.
- `2A04` is a generic five-byte ADAS lateral request: u8 request ID, signed
  16-bit pinion-angle request at 0.001, steering-support gain at 0.01, and
  damping gain at 0.01. Its field geometry is exactly the same as the TSS3
  `5282` request record (`TSS request - lateral ID`, pinion angle, assist gain,
  damping gain), which is the recorder-side request family joined to TSS3
  `0x08A`.
- `2A06` is the compact post-arbitration pair: u8 `Lateral control ID of
  arbitrated result` plus signed 16-bit `Pinion angle of arbitrated result` at
  0.001. The same result quantities also appear independently as ADU records
  `1593` and `1620`.
- ADCU P6 SID-22/recorder state provides higher-level mirrors: `0x1E19`
  contains `Lateral Control Request Pinion Angle`, `EDSS Lateral Control Request
  ID`, and `Pinion Angle Of Arbitrated Result`; `0x1ED3` contains `Lateral
  Control ID of Arbitrated Result`; alternate snapshot `0x3486` contains the
  `Lateral Arbitration ID`. Feature-local records such as `0x1B10` additionally
  expose LTA active state and `LTA EPS Pinion Angle Estimated Value`.

These are diagnostic/recorder data IDs, not vehicle-network CAN IDs. They prove
that P6 preserves the same logical sequence—feature request -> normalized ADAS
lateral request -> arbitration result—even though the final request values are
no longer exposed by the EPS Data List itself.

The downstream endpoint has a new clue. `PSCM_A_P6` adds four DTCs that do not
exist in `EMPS_P5`: missing communication with a **Dynamic Domain Controller
ECU** on main and sub buses, separately naming Control Module No.1 and No.2.
The P6 EPS simultaneously retains `0x106A Cooperation Control State`. This makes
the Dynamic Domain Controller the strongest current candidate for the immediate
logical source/supervisor of the P6 EPS cooperative-control ingress.

The RAV4 install set contains no standalone Dynamic Domain Controller diagnostic
category, and the Toyota/Chilton network diagram likewise shows no separately
named DDC ECU. On Global Bus 4 it shows only the brake-booster assembly `BRK1`,
brake actuator `BRK2`, SRS, EPS, and the junction/gateway connection. GTS maps
`BSCM_B_P6` to **Brake Booster** (`BRK1`) and `BSCM_A_P6` to **Brake/EPB**
(`BRK2`).

`BSCM_A_P6` is therefore the leading physical-owner candidate. It is a Bus-4
peer of the EPS, it is also attached to the Powertrain Local Bus, and its Data
List explicitly shows Toyota-Safety-Sense upper/lower longitudinal requests
being transformed into `Vehicle Motion Control` target acceleration/IDs. It
alone among the two P6 brake databases retains `0x107E ADS Control EPS Pinion
Angle2`. That field already exists in P5 and is an observer rather than proof of
the final steering PDU, but in the production topology it sits in exactly the
ECU/domain expected for a brake-hosted Vehicle Movement Manager / Dynamic Domain
Controller function.

The brake-to-EPS supervision relationship itself is not new and did not vanish
in P6. Both P5 brake databases (`ABS_P5` and `Brk_Bst_P5`) and both P6 brake
databases (`BSCM_A_P6` and `BSCM_B_P6`) carry the same core records:
`U013187 Lost Communication with Power Steering Control Module`, `U11B187 Lost
Communication with Power Steering Control Module "A" (ch2)`, `U032057 Software
Incompatibility with Power Steering Control Module`, and Data List bit `0x102F`
`EPS/Steering Control Actuator ECU Communication Open`. P6 drops some P5-only
programming/rear-steer compatibility variants, but preserves the ordinary
message-loss and compatibility supervision.

The Bus-4 drawing is physically ordered, not merely decorative. The main line
leaves the Central Gateway and enters `BRK1`; a second main-line leg exits
`BRK1` and continues to **J/C Global CAN No. 1**, where `BRK2` and SRS branch and
EPS terminates the downstream leg. Toyota does not mark `BRK1` with the diagram's
gateway-function `*`, so the drawing alone does not classify the internal
CA1<->downstream implementation as an active CAN gateway rather than a physical
daisy-chain continuation. It does, however, place the brake-booster assembly
physically between the upstream Bus-4 leg and the BRK2/EPS junction segment.

This is the same topology class already recovered on the 2026 Camry: its inline
brake-booster/master-cylinder assembly has upstream `CA1H/CA1L` and downstream
`DC1H/DC1L` daisy-chain pairs. Toyota's diagram alone allowed passive
continuation, while exact-car traffic later located an admission/segmentation
boundary inside that assembly. The RAV4 currently has the topology and P6
semantic clues but not yet the corresponding terminal-page/runtime proof.

The remaining alternatives are a DDC function hosted elsewhere and routed onto
Bus 4 by the Network Gateway, or a separate logical node hidden inside one of
the named assemblies. The final controller-to-EPS wire PDU and its SecOC
boundary still require a TSS4 capture or firmware.

## 2. What "ADAS Domain Controller" means here

The best direct architecture match is Denso
**US20240336271A1**, *Method, processing system, and recording device*
(priority 2021-12-21; published 2024-10-10), and its family including
**WO2023120505A1** and the 2026 Japanese divisional **JP2026041847A**.

Its fourth embodiment explicitly describes a **domain-based architecture for
driving assistance up to Level 2**. The physical architecture contains:

- ADAS domain controller `451`;
- powertrain domain controller `452`;
- cockpit domain controller `453`;
- connectivity domain controller `454`;
- external/internal environment sensors;
- motion actuators and HMI devices.

Denso says the ADAS domain controller aggregates ADAS functions and can combine:

- perception/fusion;
- environment judgment;
- driving planning;
- the portion of motion control that **generates request information for motion
  actuators**.

The examples include lane keeping, distance keeping, collision-mitigation
braking, and automatic steering avoidance.

That is an unusually close conceptual match to the RAV4 EWD: sensors feed a
central ADAS computer, while steering/braking remain separate actuators that
receive requests.

The 2026 publication is a divisional of the older family, so it is not evidence
that Toyota invented the architecture in 2026. It is evidence that Denso kept
prosecuting the same domain-controller architecture while Toyota deployed TSS4.

## 3. Toyota itself uses A-DC / C-DC terminology

Toyota **US20250360935A1**, *System, method, and computer program for vehicle
software development* (priority 2024-05-24; published 2025-11-27), gives a
second strong architecture clue.

Figure 7's example vehicle contains an **Advanced Driver Assistance System
(ADAS) Domain Controller (A-DC) ECU** and a **Cockpit Domain Controller (C-DC)
ECU**. In that example both may run QNX, and the two domain controllers are
connected by PCI Express, Ethernet, and CAN FD.

The patent is about a vehicle-software development configuration rather than
TSS4 control itself. Its QNX/PCIe/Ethernet details therefore must not be
projected onto the production RAV4 without independent evidence. What it does
establish is that Toyota was explicitly designing around an `A-DC` / `C-DC`
domain-controller vehicle architecture by 2024.

## 4. Toyota + Denso radar/application consolidation

Toyota and Denso co-assigned **JP2024053450A / JP7852455B2**, *Processing
system* (priority 2022-10-03; application published 2024-04-15; grant published
2026-04-28).

The main embodiment splits processing between a radar ECU and a center ECU. The
center ECU communicates with other vehicle ECUs, executes applications, and can
control vehicle motion through driving actuators.

The patent then explicitly says that the **radar ECU and center ECU may be
replaced by an ADAS domain controller**, with HMI control moved to a separate
HMI domain controller.

This is useful production-era lineage for the RAV4 topology because the RAV4
ADAS Domain Controller sits at the center of several radar/camera interfaces
while HMI and actuator ECUs remain separate.

## 5. TSS3 -> TSS4 interpretation

For TSS3, the forward-recognition-camera side was a natural place to look for
the ADAS application owner and the request-generation boundary.

The 2026 RAV4 EWD no longer supports that default model. The forward sensing
camera is a peripheral of a larger ADAS Domain Controller, and the controller
has its own vehicle-network attachment.

The leading TSS4 model is therefore:

```text
camera / center radar / side radars / BSM / ultrasonics / DMC / park cameras
                                  |
                                  v
                     ADAS Domain Controller
               perception + ADAS applications
                                  |
                     normalized motion requests
                                  |
                               CGW / Bus 4
                                  |
                     BRK1 / BSCM_B_P6
                      inline EPS-side path
                                  |
                      downstream Bus-4 leg
                         /              \
                        v                v
             BRK2 / BSCM_A_P6          EPS
             DDC / VMM candidate    steering actuator
             request arbitration
             actuator targets
                    |
                    +---------- powertrain local bus
```

This preserves the TSS3 functional split while moving the former FRC
perception/application compute into the ADAS Domain Controller. The brake-domain
Vehicle Movement Manager/request-generation role remains the leading P6 model,
with `BSCM_A_P6` as the software-owner candidate and inline `BSCM_B_P6` as a
separate physical admission/segmentation candidate.

Current GTS+ and the recovered P6 ADU recorder give a much tighter boundary on
that model. `ADCU_P6.ddb` directly exposes `0x1E19` request pinion plus
arbitrated-result pinion, `0x1ED3` arbitrated-result lateral ID, and snapshot
`0x3486` lateral arbitration ID. The separate ADU recorder exposes the normalized
five-byte request `2A04` and three-byte arbitration result `2A06`; feature-local
LTA/LCA records `1B40`/`1C48` additionally distinguish requested steering angles
labelled `(ADU)` and `(EPS)` alongside the generic request/result layer.

That proves the ADAS Domain Controller owns the feature-side request state and
observes the selected lateral result. It does not identify the final physical
manager merely from the recorder: diagnostic records can contain outgoing,
incoming, and internal values.

The actuator side adds the missing downstream clue. `PSCM_A_P6` newly monitors a
**Dynamic Domain Controller ECU** on redundant main/sub buses and still exposes
`0x106A Cooperation Control State`. The RAV4 install set has no standalone DDC
diagnostic category, so the current evidence establishes an EPS communication
dependency on that logical controller without locating the function in a
separate box.

The later Toyota/ADVICS VMM family gives the brake ECU as its concrete motion-
manager implementation. Production `BSCM_A_P6` also explicitly exposes
Toyota-Safety-Sense longitudinal requests being converted into `Vehicle Motion
Control` targets, while retaining the lateral `ADS Control EPS Pinion Angle2`
observer. The leading physical-owner hypothesis is therefore a DDC/VMM function
in the Brake/Skid domain, but the RAV4 software or traffic must establish that
placement.

The exact RAV4 wire PDU carrying the final lateral instruction, its SecOC
boundary, and the relationship between the recorder values and that PDU still
require a TSS4 capture or firmware.

## 6. Porting consequences

The windshield camera is no longer the obvious interception boundary.

The highest-value next step is to log the ADAS-controller, Brake/VMM, and EPS
network edges while exercising LTA/LCA/PDA. The diagnostic schema already
establishes the P6 request/result stages; synchronized traffic should bind
`1B40/1C48`, generic `2A04`, result `2A06`, and EPS cooperation state to the
actual vehicle-network PDUs and identify the authenticated final-instruction
boundary.

The actuator side can be investigated independently. GTS routes `PSCM_A_P6`
through ISO 15765-2 29-bit normal-fixed addressing at physical request
`0x18DA13F1` and response `0x18DAF113`, and binds the P6 Calibration-ID role
`0x52` to `GetCID_SID22_P6_DT.dll`. A live P6 RAV4 can therefore be used to
fingerprint the EPS directly. The resulting software identity is the cleanest
lead for obtaining an update image and determining the processor family from
the firmware; a physical rack teardown is the independent hardware route.
Until one of those establishes the silicon, do not project the P5 RH850/ICU-S
implementation onto `PSCM_A_P6`.

The direct forward-camera interface should be treated as a separate reverse-
engineering target. Its physical/protocol semantics are not given by the EWD.

## Public sources

- Toyota, 2026 RAV4 / TSS4 / Arene:
  https://pressroom.toyota.com/the-next-adventure-begins-2026-rav4-arrives-this-winter/
- Toyota Global, new RAV4 / Arene:
  https://global.toyota/en/newsroom/toyota/42758168.html
- Denso US20240336271A1:
  https://patents.google.com/patent/US20240336271A1/en
- Denso JP2026041847A:
  https://patents.google.com/patent/JP2026041847A/en
- Toyota US20250360935A1:
  https://patents.google.com/patent/US20250360935A1/en
- Toyota + Denso JP7852455B2:
  https://patents.google.com/patent/JP7852455B2/en
