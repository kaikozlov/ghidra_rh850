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

The production observations below come from three 2026 RAV4 EWD extracts
supplied for this investigation:

- `ADAS-U.pdf`
- `EPS-U.pdf`
- `MPX-CAN-HEV-U.pdf`

Those source files are not committed here. Pin names and topology are EWD facts.
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
- left and right blind-spot monitor sensors;
- front and rear ultrasonic sensor chains;
- driver-monitor camera;
- front/rear/left/right panoramic-view cameras;
- light parking-assist circuitry and mirror-related park/BSM interfaces;
- radio/display receiver through a separate shielded interface.

The exact payload transported by the direct `FCM` connection is not established
by the EWD. In particular, the drawing alone does not distinguish raw video from
a processed camera data interface.

### Vehicle-network attachment

The vehicle-wide CAN EWD places the ADAS Domain Controller on the global CAN
network through connector `J83(C)`.

One side of the controller (`CA1H/CA1L`) joins No. 6 Global CAN Junction
Connector `J94`, which in turn connects to Network Gateway ECU `D101`.
A second controller interface (`CA9H/CA9L`) continues toward No. 11 Global CAN
Junction Connector `J99`.

This makes the ADAS Domain Controller a networked vehicle ECU, not merely a
camera module.

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
reaction-force, and cooperative/Advanced-Drive diagnostic block
`0x1CCB..0x1CF3`. In particular, the P5 fields `Advanced Drive Target Steering
Angle`, `Target Lateral ID`, and `Cooperative Control in Progress Flag` have
no P6 Data List counterpart.

The table schema is likewise evolutionary. Sixteen table types are shared.
P6 drops the old P5 behavior-record tables 87/88/153 and adds the P6
`CDbRoBDiagCodeTable` / `CDbRoBFreezeFrameTable` pair 163/164. The common
signal-group, trigger, DTC-status-mask, and behavior-signal-check records are
largely or completely inherited. `PSCM_A_P6.ddb` and `PSCM_A_P6F.ddb` are
byte-identical in the current NA corpus.

This makes `PSCM_A_P6` look like a pruned and revised successor to the P5
steering definition, with a new P6 diagnostic/recorder ABI and a narrower
exposed ADAS/cooperative-control surface rather than a clean-sheet EPS
diagnostic model.

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

A working TSS4 model is therefore:

```text
camera / center radar / side radars / BSM / ultrasonics / DMC / park cameras
                                  |
                                  v
                     ADAS Domain Controller
               perception + ADAS applications
             + ADAS-side request/arbitration state
                                  |
                           vehicle networks
                                  |
                       likely Brake / VMM
                                  |
                    brake / EPS / powertrain ECUs
```

Current GTS+ gives a useful boundary on that model. The P6 ADAS-controller
database `ADCU_P6.ddb` directly exposes:

- DID `0x3486`: `Longitudinal Powertrain Arbitration ID`,
  `Longitudinal Brake Arbitration ID`, and `Lateral Arbitration ID`;
- DID `0x1E19`: `Lateral Control Request Pinion Angle`,
  `EDSS Lateral Control Request ID`, and `Pinion Angle Of Arbitrated Result`;
- DID `0x1ED3`: `Lateral Control ID of Arbitrated Result`.

That proves the ADAS Domain Controller participates in and observes the
request/arbitration plane. It does **not** by itself prove that the final Vehicle
Movement Manager is resident there, because an ECU Data List can expose values
received back from another ECU as well as locally computed state.

The later Toyota/ADVICS VMM family still gives the brake ECU as its concrete
implementation. US20240101086A1 places the motion manager, including reception,
arbitration, and request generation, in the brake ECU. The same family expressly
allows the manager to be moved into an advanced-safety ECU or a separate
management ECU. Toyota's 2026 US20260125083A1 continuation again uses a brake ECU
containing the motion manager as its embodiment.

Therefore the strongest current RAV4/TSS4 hypothesis is **not** that the entire
VMM definitely moved into the ADAS Domain Controller. The ADAS controller now
owns the ADAS applications and substantial request/arbitration state, while the
final cross-system Vehicle Movement Manager is still most likely in the
Brake/Skid domain. The exact RAV4 manager location remains to be established
from its brake-side diagnostics, network traffic, or software.

The exact RAV4 request path, message IDs, SecOC boundary, and gateway behavior
still require captures or software evidence.

## 6. Porting consequences

The windshield camera is no longer the obvious interception boundary.

The highest-value next steps are to identify the ADAS Domain Controller in
GTS+/Techstream, recover its part/software identities and diagnostic address,
then log both of its global-CAN-facing interfaces while exercising LTA, DRCC,
PCS, and parking functions. That should tell us whether TSS4 preserves the
request/result/target planes seen on TSS3 and where the authenticated
application-request boundary moved.

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
