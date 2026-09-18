# Toyota TSS3 vehicle-movement arbitration architecture

**Status:** architecture oracle joined to current Camry/TSS3 evidence.  This document
uses Toyota patent application **US 2020/0070849 A1, “Information Processing
Apparatus”** as an external architecture source and then keeps the exact-Camry wire,
firmware and GTS joins separate.  The retained source PDF is local-only at
`REFERENCE/toyota_vehicle_movement_arbitration_patent/US20200070849A1.pdf`;
`REFERENCE/` is intentionally untracked.

This source resolves a long-standing conceptual error in the TSS3 work: Toyota does
**not** expose one flat “ADAS command” interface.  The disclosed architecture has at
least three semantically different interfaces, plus an independent stability-control
path:

1. applications -> request arbitration (**request IF**);
2. request arbitration -> applications (**result/status IF**);
3. request generation -> actuator controllers (**target/instruction IF**); and
4. Vehicle Movement Controller -> actuator controllers (**priority stability IF**),
   bypassing ordinary application-request arbitration.

The current Camry evidence maps naturally onto those layers.  The strongest working
crosswalk is **`0x08A` = request-side TSS package, `0x081` = result/status package,
B6 = final steering-controller target/instruction**.  The logical architecture is now
strongly constrained; exact Camry physical placement, security ownership and the
wire/private-link transformation between these layers remain separate questions.

## 1. Toyota's disclosed control graph

Patent Figures 1–2 and paragraphs 27–55 describe the following functional graph:

```text
 driving-assistance applications / execution units
   (ACC, LKA, PCS, parking, autonomous driving, ...)
                       |
                       | standardized request dataset
                       v
              +---------------------+
              | request arbitration |
              +---------------------+
                 |       |       |
        selected |       |       | selected lateral
        long IF  |       |       v
                 |       |   steering request-generation
                 |       |             |
                 |       |             v
                 |       |      steering controller -> EPS actuator
                 |       |
                 |       +-> brake request-generation -> brake controller
                 |
                 +---------> powertrain request-generation -> powertrain controller
                       ^
                       |
        controller/actuator state + employed-control feedback
                       |
              +---------------------+
              | result/status output| ----> applications
              +---------------------+

 driver accelerator/brake/steering
       |              |
       +--------------+----> request-generation/controller arbitration

 Vehicle Movement Controller (stability / slip / emergency path)
       +------------------> powertrain / brake / steering controllers
                            (priority over ordinary requests)
```

Toyota calls the aggregate request-arbitration/request-generation/VMC function an
**information processing apparatus** with a function as a **vehicle movement
manager**.  In the disclosed embodiment it is housed in the **same ECU as the brake
controller**, while communication with applications, powertrain and steering occurs
over the in-vehicle network.  When the manager and brake controller are co-located,
the manager->brake instruction need not appear on CAN at all.

The stated reason for placing the manager in the brake ECU is not incidental.  Toyota
explicitly prefers the brake ECU for fail-safe behavior because it can generate friction
braking and has direct wheel-speed inputs even if inter-ECU communication is lost.
That is a strong architectural explanation for why a steering-controller instruction
can legitimately be monitored as traffic from the **Brake System Control Module**.

## 2. Interface A: application request dataset

Patent Figure 3 and paragraphs 56–82 define the request dataset received from the
applications.

### Longitudinal lower-limit package

- request longitudinal ID (lower): **identifier of the application** supplying it;
- requested acceleration (lower): minimum acceleration requested by that application;
- brake-permission flag;
- gear-shift-priority request;
- responsiveness request;
- accelerator-override-prohibition flag.

### Longitudinal upper-limit package

- request longitudinal ID (upper): **identifier of the application** supplying it;
- requested acceleration (upper): maximum acceleration permitted by that application;
- brake-permission flag;
- gear-shift-priority request;
- responsiveness request.

### Lateral package

- request lateral ID: **identifier of the application** supplying it;
- requested steering angle / yaw rate / rotation radius;
- quantity-selection flag;
- driver-steering flag;
- responsiveness request.

The upper/lower longitudinal requests are **bounds**, not redundant copies.  Toyota
uses them to describe an allowed longitudinal range.  An ACC application is explicitly
given as an example of a function that sets both lower and upper packages.

### Camry/GTS join

The FRC-hosted TSS3 Operation-FFD dictionary mirrors this request vocabulary:

| Patent request concept | Toyota GTS/FFD | Current Camry wire join |
|---|---|---|
| lower longitudinal application ID | `5280 TSS required longitudinal ID (lower limit)` | one of `0x08A B6[7:2]` / `B7[7:2]`; order unresolved |
| lower acceleration | `5280 ... acceleration (lower limit)`, s16 x0.001 | one of `B8:B9` / `B11:B12` |
| lower distribution/policy | `5280` distribution, shift, EPB, override, priority | only ID/allocation core mapped so far |
| upper longitudinal application ID | `5281 TSS request longitudinal ID (upper limit)` | other of B6/B7 upper-six fields |
| upper acceleration | `5281 ... acceleration (upper limit)`, s16 x0.001 | other of B8:B9/B11:B12 |
| request lateral ID | `5282 TSS request - lateral ID` | `0x08A B21[5:0]` |
| requested pinion angle | `5282 TSS request - pinion angle`, s16 x0.001 | `0x08A B18:B19` (~0.00100012 rad/count) |
| lateral responsiveness/gains | `5282 Steering assist gain` / `Damping control gain` | `0x08A B24/B25` |

This is why `0x08A` should be described as the **TSS request-side package**, not the
final EPS command.  Exact F33 does not receive `0x08A`.

One implementation detail remains important: patent Figure 3 is the conceptual
per-application interface.  The Camry's `0x08A` can carry different IDs in its two
longitudinal bound slots (for example 11 and 17).  Therefore the exact Toyota
implementation may already aggregate/select internal TSS application packages before
publishing `0x08A`; `0x08A` must not be over-described as the untouched output of one
single application.

There is also **no proved unsigned/pre-protection injection point before `0x08A`**. The
September repin/direction experiment closes more of the physical source than the older
GTS-only topology model did. With the Toyota-B relay open, `0x08A` is native on the
**FRC/camera-side electrical endpoint** of the intercepted pair (Panda bus2) and is
forwarded byte-for-byte toward the chassis side (bus0); `0x081` is native in the reverse
direction on the **Brake/chassis-side endpoint**. The intercepted pair is the repinned
Toyota Bus-4 chassis network; Panda bus1 is the separate Toyota Bus-1 camera/radar family.
Standard FRC CommunicationControl normal-Tx suppression removes the protected `0x08A`
publication, while Brake CommunicationControl removes `0x081` and Brake continues
`0x081` with request-loss supervision when FRC request traffic disappears.

Therefore the protected `0x08A` publisher is inside the **FRC ECU/assembly diagnostic
boundary**, and the frame is already authenticated before it reaches the accessible
relay split. The exact FRC-internal signer remains open: it may be the main TSS compute
SoC/HSM or another network/security controller inside the FRC module. This does **not**
leave an external Brake/CGW `0x08A` signer as the leading model. It also does not prove
an accessible unsigned request API before the FRC's signing step.

## 3. Request arbitration is per package, not per ECU

Patent paragraphs 148–152 explicitly arbitrate three objects independently:

- longitudinal lower-limit package;
- longitudinal upper-limit package;
- lateral package.

The selected lower package and selected upper package can therefore originate from
different applications.  The numeric IDs identify the **applications/request sources**,
not ECUs and not ordinal priorities.  Selection can be based on magnitude and other
predefined rules; the patent gives minimum-value selection as one example rather than a
mandatory Toyota calibration rule.

Toyota/ADVICS follow-on US20220219711A1 makes the ID/priority distinction explicit.
Each application emits a preset ID that uniquely identifies the requesting application;
a single ADAS ECU may host multiple applications (ACC, LKA and AEB are the patent's
example), and the manager looks the ID up in a separately stored priority table.  Figures
2/5 deliberately show **Application ID** and **Priority Level** as different columns, and
the priority order can change with vehicle/driver state or availability without changing
the application identity.  The patent leaves its application-ID column blank, so its
priority numbers 1..11 are not Toyota ID values.

Current GTS+ fills in the otherwise-missing numeric side independently.  `EMPS_P5
0x1CEE Target Lateral ID` is a 0..63 enum whose labels closely mirror the follow-on
patent's application set: `1 PCS`, `4 LDA`, `10 Hands Off LTA`, `11 LTA/LCA`, `18 SDG`,
`19 PDA`, `25 AP`, `27 Remote Parking`, Lv.3 `35/37/39 = AD/EM/DES`, Lv.4 `41/43/45 =
AD/EM/DES`, `49 Self-Propelled Transport`, and `63 Driver Operation`.  The mismatch
between numeric order and the patent's priority order is itself decisive: for example,
the patent prioritizes Lv.4 EM above Lv.4 AD while GTS identifies them as 43 and 41.
The six-bit `0x08A B21[5:0]` / `0x081 B13[5:0]` request/result fields therefore fit a
preset application-identity namespace, not a rank or ECU address.

This materially changes how the Camry ID namespace should be interpreted.  Toyota uses
the same concept—an application identifier—for longitudinal and lateral IDs.  It is now
reasonable to treat numeric reuse as intentional until contradicted, while still avoiding
an unsupported claim that every generation/axis has one identical display-label table.
In particular:

- `0` is a common no-request/manual anchor;
- `63` is independently named **Driver Operation** on both recovered longitudinal and
  lateral surfaces;
- Camry longitudinal ID11 during ordinary DRCC and lateral ID11 `LTA/LCA` are a strong
  candidate for a shared TSS continuous-driving application identity;
- P6 longitudinal 41/45 “MaaS autonomous-driving request 1/2” need not contradict
  lateral 41/45 `AD (Lv.4)` / `DES (Lv.4)`; those labels may be two views of the same
  autonomous-driving application identities;
- longitudinal ID25 during delayed hold is an unresolved semantic clue, not proof that
  the namespaces are unrelated.  It may identify a low-speed/parking/hold application,
  a selected bound from another application, or expose a remaining field/order mistake.

## 4. Interface B: arbitration result and vehicle-state feedback

Patent Figure 4 and paragraphs 83–108 define a **result dataset sent back to the
applications**.  It is much richer than a mirror of the request.

### Result after arbitration/execution

- arbitration-result lateral ID;
- selected lateral quantity;
- lateral quantity-selection flag;
- arbitration-result longitudinal ID;
- selected acceleration.

The two result IDs have deliberately different semantics:

- lateral result ID identifies the application whose lateral request the **request
  arbiter selected**;
- longitudinal result ID identifies the source of acceleration **actually employed by
  the powertrain controller after it compares the arbitrated application request with
  driver demand**.  If the driver wins, a driver-discriminator value is returned.

This is a direct explanation for Camry `0x081` result ID63 even when neither `0x08A`
longitudinal bound slot contains 63: Toyota independently names ID63 `Driver Operation`.

### Result/state telemetry

The same result dataset can carry:

- estimated vehicle-body acceleration + validity;
- current shift range;
- brake-control-execution flag;
- stop-holding state;
- vehicle-speed-limit flag/value;
- braking/drive/lateral assistance levels;
- estimated ground acceleration with accelerator fully closed/open;
- driver accelerator-requested acceleration;
- driver brake-requested acceleration.

The current FRC-hosted Operation-FFD vocabulary contains striking counterparts:
`5252` brake-pedal driver acceleration, `5253` estimated vehicle acceleration/status,
`525D` cruise brake control in progress, `525E` stop holding status, `5261` estimated
on-ground acceleration with accelerator fully closed, `526A` current shift range,
`5284/5285` result IDs, `57D3` result-acceleration validity, `57DB` result acceleration,
and `57DE` result pinion angle.

### Camry wire join

`0x081` is therefore best modeled as the **Brake/VMM-owned result/reference/status
publication toward the TSS applications**, not as a dumb echo:

- `B13[5:0]` = recovered lateral result ID;
- `B16:B17` = recovered result/reference pinion quantity;
- `B6[5:0]` = strongest `5284` longitudinal employed-source-ID candidate;
- `B20:B21` = strongest `57DB` result-acceleration candidate;
- `B11[4]` = proven FRC-request-loss supervision state, not yet joined to `57D3`.

The remaining acceleration-like `0x081` fields should be investigated against the full
Figure-4/FFD state packet before assigning them ad-hoc names.

### Fault-state feedback is synthesized by the manager

Toyota's later US20230082947A1 refines the result/status side of this graph and
separates two layers that should not be conflated.

The actuator systems first report raw state to the motion manager. In that
embodiment, steering signal `STR2` includes steering-system reliability,
driver-grip state, steering-wheel operating torque, and steering-wheel angle.
Steering reliability distinguishes normal operation, protective control,
abnormality detected but failure not yet confirmed with control invalid, and a
confirmed failed state. Brake and powertrain have analogous reliability
information.

The motion manager then generates application-facing signal `PLN2`. That signal
contains **fail classes** synthesized from the actuator reliability/state rather
than simply forwarding a raw EPS bit. The named example classes include lateral
control, driver brake input, autonomous braking main/sub, driving system, and
shift control. The lateral class is two bits in the disclosed example.

When an abnormality exists, the manager can augment the fail class with
information for deciding how the application should behave:

- influenced vehicle-velocity range;
- malfunctioning portion; and
- post-abnormality operation mode.

The disclosed malfunctioning-portion namespace explicitly includes
powertrain<->brake and steering<->brake communication. This is important for the
exact Camry fault cascade: an EPS application/communication outage can be
interpreted inside Brake/VMM and converted into an application-facing lateral
fail class before the FRC decides that the lateral system is unavailable.

The current F33 wire evidence gives a strong packing hypothesis for that class.
`0x081 B13[5:0]` is already recovered as the lateral arbitration-result ID.
The two unused high bits behave as `00` in ordinary healthy states, occasionally
`10` transiently, and overwhelmingly `11` in dead-EPS/post-bootstrap fault
states. Independently, current Toyota `DRS_P5` diagnostics expose an 8-bit
`DRS Fail Class` with valid values only `0..3`: value 0 means steering control
is executable, 2 means not executable temporarily, and 3 means not executable
with failure decided (value 1 is reserved). This makes **`B13[7:6]` a strong
candidate two-bit lateral fail class**, with observed `10 -> 11` matching
temporary invalidity -> confirmed failure.

That mapping remains a hypothesis. The patent does not assign particular
`00/01/10/11` values to its four semantic states, and successor ADCU P6 exposes
the full result-ID byte without decomposing its high bits. A synchronous
`5283_1` + raw-`0x081` onset capture or exact decoder join is still required.

## 5. Interface C: post-arbitration controller instructions

After request arbitration, Toyota inserts a **request-generation** layer that converts
selected application requests into controller-specific instructions.  This is the layer
we had been missing when reasoning about B6.

### Powertrain instruction (Figure 5)

Contains upper/lower target drive power, target longitudinal IDs, target accelerations,
accelerator-override prohibition and gear-shift-priority flags.

### Brake instruction (Figure 7)

Contains upper/lower target braking force, target longitudinal IDs, target accelerations
and gear-shift-priority flags.  In the preferred embodiment this interface can be
internal to the Brake ECU and therefore invisible on CAN.

### Steering instruction (Figure 6)

Contains:

- **Target Lateral ID**;
- **Target Steering Angle / Target Yaw Rate / Target Rotation Radius**;
- quantity-selection flag;
- driver-steering flag;
- responsiveness request.

This is an exceptionally strong semantic match to the exact F33 B6 interface.  Current
GTS `EMPS_P5 0x1CEE` independently exposes **Target Lateral ID**, **Cooperative Control
in Progress Flag**, **Target Steering Angle After Output Compensation**, and
**Advanced Drive Target Steering Angle**.  Exact F33 B6 signal261 is the only recovered
external mode/application selector and signal262 is the only recovered external target
steering magnitude.

Therefore the current best model is:

```text
0x08A / FFD 5282        0x081 / FFD 5285,57DE       B6 / EMPS 1CEE
TSS request             request/result feedback      steering-controller target
(application-side)  ->  Vehicle Movement Manager -> (post-arbitration instruction)
                               / Brake domain
```

B6 is **not another peer application request**.  It is downstream of request
arbitration/request generation.

The exact names of B6 secondary fields remain open.  Patent Figure 6 makes switching,
driver-steering and responsiveness fields high-value hypotheses, but existing F33
consumer behavior must be joined before assigning those OEM names.  In particular,
B8/B9's recovered percentage-like behavior must not be renamed merely because a patent
field exists.

### Parallel Toyota realization: selected source ID + direct request stream

Toyota filed a closely related but materially different architecture one day earlier:
US20200070873A1.  In that embodiment each application puts an application ID plus its
request value on the network, the movement manager selects an **application ID**, and
the actuator receives both planes.  After the selection arrives, the actuator uses the
latest matching request received **after** the selection event.  The request sample the
manager arbitrated and the request sample the actuator executes may therefore differ.
The application ID is explicitly separate from `CAN_ID`.

This is a latency optimization, not the physical realization recovered at exact F33's
external EPS boundary.  F33 receives neither `0x08A` nor `0x081`; its recovered
external target-bearing cooperative-control ingress is B6.  There is no recovered
second direct application-request stream at F33 that would make B6 merely the selector
from US20200070873A1.  Therefore the current `0x08A` request -> Brake/VMM -> B6 target
model remains the better exact-F33 fit.

The parallel patent is nevertheless important for architecture reasoning: Toyota can
separate request-value transport from arbitration authority, and an application ID can
act as a grant over future samples rather than merely label the one sample that was
arbitrated.  Do not assume every Toyota actuator receives a manager-forwarded copy of
the exact winning request value.  Recover that physical choice per actuator/platform.
See [the selected-ID/direct-request close read](toyota-selected-id-direct-request-arbitration.md).

## 6. Why the Brake module arbitrates and why B6 comes from that domain

The patent answers the question that originally looked architecturally strange.
Brake/Skid is not merely acting as a brake actuator ECU; in this architecture it is a
**vehicle-movement manager**:

- it receives standardized requests from multiple assistance applications;
- independently arbitrates longitudinal lower, longitudinal upper and lateral packages;
- knows actuator availability and vehicle-motion state;
- distributes requested deceleration between powertrain and friction brake;
- can distribute lateral control between steering and individual-wheel braking;
- generates controller-specific instructions;
- feeds result/state/availability back to the applications; and
- provides the preferred fail-safe host because it retains friction-brake and direct
  wheel-speed authority when inter-ECU communication fails.

The exact F33 communication monitor independently says B6/PDU44 loss is
**U012987 Lost Communication with Brake System Control Module / Missing Message**.
That is no longer a mysterious source-domain coincidence: it is exactly where Toyota's
disclosed architecture places the steering request-generation output.

## 7. Vehicle Movement Controller: a second, higher-priority controller path

The patent's Vehicle Movement Controller is distinct from ordinary application
arbitration.  It can directly instruct powertrain, brake and steering controllers for
stability functions such as wheel-slip suppression, ABS-like control and emergency
braking.  The controllers give this path priority over driver/application requests.
The VMC also reports its state and reduced actuator availability back into the request
manager so applications can adapt.

This is important for interpreting exact F33.  We already proved accepted ID11 B6 is
**co-modulated inside the ordinary EPS assist/current composition**, not an exclusive
replacement writer.  That is architecturally unsurprising: the final steering controller
must coexist with local assist, driver input, stability intervention and other controller
constraints.  “B6 did not become sole authority” was never evidence that B6 was the wrong
OEM interface.

It also means openpilot should not invent a requirement that its final target replace all
other EPS terms.  The production goal is to enter Toyota's intended request-generation
pipeline with a valid application request and let the OEM movement/stability layers retain
their normal roles.

## 8. Why direct comma B6 did not reach F33, while the EPS-resident replacement worked

The Sep-10 direct marker experiment is now easier to place:

- Panda transmitted 121 distinctive ID63 B6 frames and received TX returns;
- exact-F33 same-scheduler positive controls saw D7 and native B6;
- **none of the Panda B6 markers appeared at F33's deterministic post-CanIf/pre-SecOC
  boundary**.

That failure is now localized more tightly than the original Sep-10 conclusion. Exact
F33 programs B6 as ordinary RSCFD acceptance **rule39**: standard data-frame CAN ID
`0x0B6`, mask selector 0 (`GAFLM=0xC00007FF`), the same receive-FIFO destination used by
neighboring `0x090` and `0x0D7`, followed by CanIf descriptor39
`0x400000B6 / DLC32`.  The recovered pre-SecOC path can distinguish CAN ID, standard vs
extended/data-frame state, CAN-FD format and length; its CanIf identity is exactly
`0x400000B6` under mask `0xFFFFFFFF`, and **BRS is not part of that software key**. It has **no transmitter-node
identity and no B6 application-field/Target-Lateral-ID/SecOC-tag filter before the
observer**.  PDU44's legacy Toyota-checksum hook is configured non-enforcing.

Therefore a 32-byte standard CAN-FD B6 that is successfully decoded by F33 controller1
would reach the Sep-10 post-ring/pre-SecOC observer.  The 121 host markers did not, while
native B6 advanced that same queue by 217 deliveries during the treatment and by 205
during the positive-control block.  The direct-Panda frame is consequently lost **before
successful F33 controller1 decode/CanIf admission**, not in EPS SecOC, PduR, generated
COM, or B6 application logic.  The only receiver-side residue is a physical/link decode
failure before GAFL matching; otherwise the loss is outside F33, between the
Panda-visible Bus-4 trunk and the EPS-local B6 delivery path.

Current GTS topology is more specific than a generic "EBU-domain boundary." In
`CDbCanBusComponentTable`, `EBU` is literally the **junction/attachment field on the
Power Steering (EPS) component row**. Across all 18 exact-Camry option rows, Brake
Booster `0x28` and Skid Control `0x29` are Bus 4 via `No. 2 Global CAN Junction
Connector`, while EPS `0x32` is Bus 4 via `EBU`. There is **no installed EBU ECU
component** in the exact-Camry component set; component `0x65`, which appears in some
other Toyota topology sets, is absent here. The current GTS English database also does
not spell the acronym out.

Toyota-authored terminology supplies the expansion independently: Toyota Motor
Engineering & Manufacturing North America patent US20210323519A1 calls an EBU an
**"electronic brake module or unit"** and uses `EBU` for that brake-domain unit
(https://patents.google.com/patent/US20210323519A1/en). Thus **Electronic Brake Unit**
is the best Toyota-supported expansion for the GTS token, while the exact GTS table
itself proves only the literal `EBU` attachment label. Brake-family GTS vocabulary independently contains wheel-speed/G/yaw copies named
`(EBU node)` in `ABS_P5`, `Brk_Bst_P5`, `EPB_P5`, and successor `BSCM_B_P6`.
The successor split sharpens that: `BSCM_A_P6 = Brake/EPB` exposes native
`FR Wheel Speed` / `Lateral G`, while `BSCM_B_P6 = Brake Booster` exposes the
corresponding `...(EBU node)` copy. That strongly favors **the EBU node being the
Brake/EPB / skid-control side itself**, not a third ECU. `ABS_P5` additionally
distinguishes U013187 **Lost Communication with Power Steering Control Module** from
U11B187 **Lost Communication with Power Steering Control Module "A" (ch2)** and exposes
DID `0x102F` **EPS/Steering Control Actuator ECU Communication Open**. Together these are
strong static clues for a secondary/local Brake->EPS communication path; successor/DDB
capability alone still does not prove exact-Camry B6 uses `ch2`.

The resulting leading physical model is therefore **not**
`No.2 junction -> separate EBU filtering ECU -> EPS`. It is:

```text
Panda-visible / shared logical Bus-4 domain
             |
             +-- No.2 Global CAN Junction -- Brake Booster
             |                           \-- Skid Control / Brake actuator
             |                                (category 435)
             |                                VMM/request generation
             |                                B6 generation/auth/routing  [leading]
             |                                      |
             |                                      v
             +--------------------------- EBU-labelled EPS attachment
                                                    |
                                                    v
                                                F33 EPS
                                          one CAN receive path
```

The serial Skid->EPS arrow is the leading **inference**, not a literal route encoded by
the GTS rows. It is favored by three independent facts: Toyota places VMM request
generation in the Brake ECU; F33 diagnoses loss of B6 as loss of the Brake System
Control Module; and contemporary Toyota repair procedures require ECU-Security-Key
update when the skid-control ECU/brake-actuator assembly is replaced. A distinct,
serviceable EBU filter ECU is neither present in the exact Camry GTS component set nor
needed to explain the evidence. An integrated internal EBU sub-node inside the brake
assembly remains possible and would not require a separately serviceable ECU identity.

This model is completely compatible with exact F33 having only **one** application CAN
controller. The segmentation/selection happens upstream; EPS sees only its one local
CAN input. Ordinary diagnostics and selected Bus-4 traffic can be routed onto that leg
while externally injected B6 is withheld and locally generated Brake/VMM B6 is admitted.
**The exact bridge/filter routine is still unproved** until Camry category-435 Brake
application `F152633K0000` is acquired or equivalent physical tracing identifies the hop.
Machine-readable GTS-only evidence is `data/generated/camry_2026_ebu_topology.json`.

The successful development fallback proves the complementary point.  The EPS-resident
helper waits for an **already-admitted native B6**, replaces its target/application bytes,
re-signs it with the EPS ICU-S primitive, and lets the stock receive path continue.  The
vehicle then steered.  It succeeds precisely because it operates *after* the unresolved
physical/source-admission boundary.

This does not make the EPS-resident patch the preferred production architecture.  It is a
powerful development fallback and proof that the downstream B6 target interface is
sufficient once an instruction is admitted.

## 9. Longitudinal control: range arbitration, not a scalar command

The patent's longitudinal example is critical for openpilot integration.  The selected
lower and upper application limits define a range.  The powertrain controller then clips
driver-requested drive power into that range:

```text
stage 1: max(driver_request, target_lower)
stage 2: min(stage1, target_upper)
```

If driver demand lies inside the range, the **driver request is employed**.  Below the
lower bound the lower application target wins.  Above the upper bound the upper target
wins and brake/powertrain can cancel surplus drive power.  The longitudinal result ID
reports whichever source was actually employed.

Consequences for the Camry work:

- `0x08A`'s duplicated B8:B9/B11:B12 values are not conceptually “two copies of one
  acceleration command”; they occupy the two **bound-package slots**.  Equality in our
  retained DRCC captures means the bounds collapse to the same value in those states, or
  that a remaining wire-field/order assumption needs refinement.
- A result ID of 63 while application bounds are present is expected when driver demand
  is the employed value inside the allowed range.
- We should recover the upper/lower ordering and policy fields before attempting native
  longitudinal output; simply writing one scalar acceleration is not the complete OEM
  contract.

GTS supplies an independent request-generation boundary in the Brake domain:

| TSS/request side | Vehicle-Motion-Control target side |
|---|---|
| `0x10A1` request accel upper from Toyota Safety Sense | `0x10A5` target accel upper from Vehicle Motion Control |
| `0x10A2` request accel lower from Toyota Safety Sense | `0x10A6` target accel lower from Vehicle Motion Control |
| `0x10A3` TSS request ID upper | `0x10A7` VMC target ID upper |
| `0x10A4` TSS request ID lower | `0x10A8` VMC target ID lower |
| — | `0x10A9/0x10AA` VMC target driving force upper/lower |

These DIDs exist in the P5 brake/booster family and persist into P6 BSCM.  They are an
OEM diagnostic reflection of the same request->target distinction described in the
patent.

## 10. Current Camry/TSS3 architecture

The best current model is:

```text
FRC / TSS3 applications
  feature-local request objects (LTA/LCA, DRCC, PDA, PCS, ...)
             |
             v
  generic selected TSS request package
  FFD 5280/5281/5282
             |
             | observed chassis-facing representation: 0x08A
             v
+----------------------------------------------------------+
| Vehicle Movement Manager / request-generation domain     |
| strongly associated with Brake System Control Module     |
|                                                          |
| request arbitration: long lower / long upper / lateral   |
| information acquisition: driver + actuator + motion      |
| result output -------------------------------> 0x081     |
| request generation:                                       |
|   powertrain target -> powertrain controller              |
|   brake target ------> brake controller (possibly local)  |
|   steering target ---> B6 -----------------------> EPS     |
|                                                          |
| Vehicle Movement Controller ----priority-------------->   |
|                         powertrain/brake/steering          |
+----------------------------------------------------------+
             ^                                  |
             |                                  v
        driver inputs                    actuator/result state
```

### Evidence grades

**Strongly joined:**

- patent logical stages and field roles;
- GTS request/result/target vocabulary reproducing those stages;
- exact F33 B6 target fields and Brake-System-Control-Module source monitoring;
- `0x08A` request tuple and `0x081` result tuple field joins;
- native B6 actually reaches F33 internally;
- already-admitted B6 can be modified/re-signed to produce steering.

**Still unresolved on this exact Camry:**

- which exact ECU/core implements each VMM sub-block;
- whether `0x08A` is the raw per-application request or an already-aggregated TSS request;
- exact physical BSCM/CGW/FRC hop that puts `0x08A`, `0x081` and B6 on their observed
  segments;
- the exact relation/cadence between `0x08A`, Brake/VMM selection/request generation,
  and B6 (without assuming a byte/value-preserving transform);
- which node owns each SecOC signing operation and source suppression;
- B6 secondary-field OEM names;
- longitudinal A/B upper-versus-lower ordering and remaining policy bits.

The patent is an architecture source, not proof that every block is placed in exactly the
same ECU on F33.  Those exact-Camry conclusions continue to require firmware/dynamic
joins.

## 11. Openpilot design consequence

The preferred native integration target is no longer “find a CAN command that moves the
actuator.”  It is:

```text
openpilot as an application/request source
        -> Toyota request arbitration / Vehicle Movement Manager
        -> Toyota request-generation outputs
        -> Toyota powertrain/brake/steering controllers
```

That preserves Toyota's native arbitration, driver override, stability/VMC priority,
powertrain/brake allocation, actuator availability and result feedback.  The successful
EPS-resident B6 signer remains the development fallback because it bypasses the unknown
source-admission hop, but it is downstream of the architecture we should ideally join.

Accordingly:

- do not revive Camry `0x160` longitudinal output;
- do not send `0x08A` directly to EPS;
- do not treat `0x081` as an EPS command;
- do not require B6 to become exclusive EPS authority;
- do not infer “stock LTA uses no B6” from Panda-visible absence—the later internal
  capture proves native B6 delivery exists at F33;
- prioritize recovering the Brake/VMM request-generation and source-suppression boundary,
  including the exact relation of `0x08A` to native B6 and the Vehicle Motion Control
  `0x10A5..0x10AA` target surface.

## 12. Patent section map for future RE

| Patent material | Architecture meaning | Current RE use |
|---|---|---|
| Figs. 1–2; ¶27–55 | full VMM graph; preferred Brake-ECU placement | source/ownership model |
| Fig. 3; ¶56–82 | application request interface | `5280/5281/5282`, `0x08A` |
| Fig. 4; ¶83–108 | result/status interface | `5284/5285/57DB/57DE`, `0x081`, future state mapping |
| Figs. 5 & 7; ¶109–121, 130–142 | powertrain/brake instructions | `0x10A5..0x10AA`, future longitudinal wire recovery |
| Fig. 6; ¶122–129 | steering-controller instruction | B6 + EMPS `0x1CEE` |
| Fig. 8; ¶143–162 | complete repeated pipeline | ordering/source-suppression experiments |
| Fig. 9; ¶163–169 | upper/lower range + driver clipping | DRCC/longitudinal result interpretation |
| ¶32,36,40,99–103 | distribution, VMC priority, availability | explains nonexclusive EPS/control composition |

Public publication: <https://patents.google.com/patent/US20200070849A1/en>.
