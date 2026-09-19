# Toyota TSS3 vehicle-movement arbitration architecture

**Status:** architecture oracle joined to current Camry/TSS3 evidence.  This document
uses Toyota patent application **US 2020/0070849 A1, “Information Processing
Apparatus”** as an external architecture source and then keeps the exact-Camry wire,
firmware and GTS joins separate.  The retained source PDF is local-only at
`REFERENCE/patents/toyota_vehicle_movement_arbitration_patent/US20200070849A1.pdf`;
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

The current Camry evidence maps naturally onto those layers, but the patent's
logical `applications -> arbiter` drawing must not be mistaken for the Camry's external
network topology. **LTA, LDA, LCA, PDA/SDG, PCS and the other TSS features are
applications inside the FRC application software. They can be enabled simultaneously;
the FRC state machine selects which one currently owns the generic lateral request.**
The first external representation of that selected request is protected `0x08A`.

The strongest exact-Camry crosswalk is therefore **FRC feature-local state -> FRC
internal feature-owner selection -> `5282` / protected `0x08A` request egress ->
Brake/VMM request arbitration -> `0x081` arbitration-result/status feedback +
post-arbitration request generation -> B6 steering-controller target/instruction**.
`0x08A` is therefore *feature-selected by the FRC*, but it is **not yet the VMM
arbitration result**. B6 is the final recovered steering-controller target/instruction
interface at EPS. Exact FRC selector code, internal security ownership, and the downstream
Brake arbitration/request-generation transform remain separate questions; the location
of the LTA/LDA/LCA/PDA feature-owner decision does not.

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

The exact Camry implementation is now clearer than the patent's conceptual
per-application drawing.  **LTA, LDA, LCA, PDA/SDG, PCS and the other TSS functions are
applications inside the FRC application software, not separate network clients arriving
at Brake.**  Their enable/configuration states can coexist.  The FRC's own application
logic decides which feature currently supplies the generic lateral request, and `5282`
records that feature-selected generic request inside the FRC-hosted Operation FFD.
Protected `0x08A` is the first externally observable publication of that FRC-selected
request on the intercepted chassis network (apart from feature settings/configuration
inputs themselves).

The retained direct ID18->ID11 and ID11<->ID4 transitions are therefore **FRC-internal
application-owner changes expressed on egress**, not evidence that Brake is choosing
between simultaneous LTA/LDA/PDA network requests.  The same point applies to the two
longitudinal bound slots: the FRC may synthesize each bound from different internal
applications before publishing the generic TSS request package.  `0x08A` must not be
over-described as an untouched output of one feature, but neither should it be described
as the bus on which those FRC-resident features compete.

The current exact-Camry model is:

```text
FRC application software
  LTA      LDA      LCA      PDA/SDG      PCS ...
   |        |        |          |          |
   +--------+--------+----------+----------+
                    |
         feature-local state machines
         settings / perception / driver / vehicle state
                    |
                    v
       FRC internal request-owner selection
                    |
          generic TSS request objects
          5280 / 5281 / 5282
                    |
                    v
                 0x08A
             FRC secured egress
                    |
                    v
            Brake / VMM boundary
            request arbitration
                    |
        +-----------+-----------+
        |                       |
        v                       v
     0x081                request generation
 arbitration result/             |
 status back to FRC              v
                                B6
                         EPS target/instruction
```

Feature enablement is therefore distinct from current request ownership: LTA, LDA and
PDA can all be enabled while only one lateral application ID appears in the generic
`5282`/`0x08A` slot at a given instant.

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

## 3. Patent arbitration semantics versus the exact Camry's FRC-internal application selection

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

The retained road logs now expose the **FRC's selected lateral application changing on
egress**. Across the 12-route / 513-segment lateral census, `0x08A` changes
`18 SDG -> 11 LTA/LCA` 28 times and never directly `11 -> 18`; it changes
`11 LTA/LCA -> 4 LDA` twice and `18 SDG -> 4 LDA` once. Two clean cruise-active ID4
episodes show `11 -> 4 -> 11` while cruise remains enabled, with `0x081 B13` following
the new FRC request after a separate publication interval. One route-3c witness holds ID4
for 2.530639 s and one route-3e witness for 1.225830 s.

These transitions are not evidence that Brake sees separate simultaneous LTA/LDA/PDA
network senders and chooses among them. Those features are simultaneously available
FRC-resident functions; the current feature owner is chosen by the FRC application state
machine from feature settings, perception, driver and vehicle state, and feature-local
inhibition/priority conditions. The resulting generic request is then published as
`5282`/`0x08A`. **That request still enters the downstream Brake/VMM request-arbitration
unit.** The two decisions are different: FRC feature-owner selection chooses what request
the FRC submits; VMM arbitration decides the downstream result from the submitted request
and the manager's other arbitration inputs. Toyota's patent priority/eligibility language
is relevant to both layers, but the exact F33 implementation of either policy remains
unrecovered.

The aggregate request/result join is stronger: 1,015,978 of 1,016,141 fresh `0x081`
pairings (99.9839589%) carry the current `0x08A` lateral ID. Every one of the 163
mismatches is transition-shaped: the FRC egress request has already changed while the
Brake/chassis result still carries the immediately previous ID. No retained stable
interval shows the downstream result persistently disagreeing with the current FRC
request. This makes `0x081 B13` a useful **downstream VMM arbitration-result oracle for
the feature-selected FRC request**, not evidence of where LTA/LDA/PDA feature ownership
is chosen. Logger batching keeps the observed ~10-40 ms raw examples from being promoted
to an exact ECU deadline.

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

The retained raw logs nevertheless make the hypothesis substantially stronger.
Across healthy routes `37/3b/3c/3d/3e/3f/45`, 871,888 logged `0x081`
observations use high2=`00` except for 246 observations in four cold-start
episodes at high2=`10`; high2=`01` and `11` are never observed healthy.
Those cold-start `0x80` episodes recover to `0x00` after roughly 0.87--0.95 s.
Dead-EPS route `d4`, by contrast, starts at `0x80`, has no EPS `0x030`,
then transitions after 3.725304 s to `0xC0` and remains there. The immediately
adjacent application payloads differ only at B13. Dead-EPS routes `d0/d1/d2`
begin already at `0xC0`.

Four healthy cold starts add an actuator-state timing join: `0x030 B6[0]`, the
recovered driver-torque-invalid gate, clears 19.856--40.711 ms before B13 clears
from `0x80` to the ordinary healthy result. That ordering is highly repeatable,
but it does not prove B6[0] is the sole reliability input. The existing stale
`0x030` bridge does not close that question because the exact frame it repeated
has B6=`0x01`: it preserved the invalid gate as well as stale SecOC freshness.
Its negative result therefore rules out message presence alone, not
fresh/accepted/semantically healthy EPS-status continuity.

The detailed retained chronology is
`targets/camry-2026/raw-20260917/brake-frc-081-fault-status/startup-fail-class-analysis.json`.

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

A September-19 independent private-endpoint discriminator now reproduces the same boundary
without using B6. Exact F33 rule46's extended `0x1FDC0002` endpoint accepts a classic
8-byte host marker and exposes it in the application software RX ring (`control nibble 0x9`,
callback selector `0x20`, length `8`). Changing only the link format to CAN-FD makes the
frame disappear before that boundary. This remains true with BRS disabled and the FD data
phase held at the nominal 500-kbit/s rate, excluding the obvious 2-Mbit/s timing explanation.
Panda reports no transmit-error growth.

Do **not** generalize that result into “all EPS FD is hidden behind the VMC/EBU domain.” B6 is
special because its native producer is inside the Brake/VMC-to-EPS path and it is absent from
comma logs. Exact F33 also receives native **unprotected** FD32 PDUs `0x025` (PDU35) and
`0x090` (PDU40), and both are visible in retained Panda/comma captures. `0x025` is especially
clear: after the repin it is overwhelmingly native on Panda bus0 and forwarded to bus2, while
F33 consumes that same FD32 PDU as measured steering angle. `0x090` likewise appears natively
in retained captures and enters F33's direct-COM path with only the ordinary additive-checksum
gate. Therefore the open problem is not a blanket “Panda-visible path cannot carry FD” rule;
it is why **Panda-generated** FD fails where native Panda-visible FD succeeds.


### 8.1 Native-FD versus Panda-created-FD differential audit

The direct-FD failure now has a much smaller candidate set.  Exact F33, the retained
Camry captures, and the current Panda implementation give the following comparison:

| property | native F33-received / Toyota FD | Panda-created failed private FD | status |
|---|---|---|---|
| CAN identifier form | all four exact-F33 normal FD Rx PDUs are **standard 11-bit**: `0x025/0x090/0x0D7/0x0B6` | private carrier was extended, then a native-shaped standard `0x090` was also tested | **identifier width disproved as sufficient cause** |
| native extended-FD precedent | retained Sep road fixture census has **zero** `addr>=0x800 && DLC>8` frames | extended + FDF was explicitly requested | **no Toyota precedent recovered** |
| FDF | present on native FD; F33 CanIf words are `0x400000ID` | explicitly set by Panda host packet and M_CAN Tx element | matched |
| DLC | native accepted examples are 32 bytes; camera family also uses 48/64 | FD32 failed, and FD8 also failed | **DLC ruled out as sole cause** |
| protection | F33 locally routes `0x025/0x090` outside its SecOC verifier, but both carry P5-shaped FV4/MAC28 tails on the wire; Sienna independently defines `0x090` as an ordinary SecOC FD profile | host test frames changed application/checksum but had no valid native MAC28 | **upstream authentication is now a leading open discriminator** |
| BRS | Toyota's own F33 FD Tx writer supports explicit FDF/BRS; retained node-1 state `FEBE5027=0x3C` selects its `0x6 = FDF|BRS` form | test Panda sent both BRS-on and host-forced BRS-off FD32 with exact TX returns | **BRS ruled out as sufficient cause** |
| nominal timing | F33 500 kbit/s, 80% sample point | deployed Panda 500 kbit/s, 80% sample point | matched |
| 2-Mbit/s data timing | F33 70% sample point, TSEG1=13/TSEG2=6/SJW6 | test Panda `54369098+` reproduced that exact timing and still failed the route-40 validator discriminator | **timing mismatch disproved as sufficient cause** |
| receive-edge filtering | F33 `REFE=1` | deployed Panda lacks the older `53ad20d0` M_CAN `EFBI` match | real controller-config difference; not a frame-format explanation for the no-BRS result |
| ISO / non-ISO FD | F33 evidence and Toyota tooling use ordinary ISO CAN-FD | Panda health reports `canfd_non_iso=0` | matched |
| ESI | healthy Toyota transmitters are expected error-active; exact per-frame ESI is not retained in comma logs | Panda was error-active with TEC=0; M_CAN supplies ESI from controller error state and Panda exposes no host ESI override | no positive mismatch recovered |
| per-frame BRS representation | Panda RX hardware sees native BRS and the internal forwarder preserves it | test-only Panda `f8f5a8f6` forced host BRS from manual/auto FD policy while keeping DBTP fixed | **both host BRS states live-tested** |
| RSCFD rule filtering | F33 GAFL matching compares ID/IDE/RTR through `GAFLID/GAFLM`; no FDF/BRS filter is recovered | rule46 accepts the same extended ID in classic form | no exact-F33 software/hardware rule explains classic-pass/FD-drop |
| physical/source route | `0x025` is overwhelmingly native on the Panda-visible chassis side and F33 consumes it; B6 is separately local/hidden | Panda injects from the intercepted host side | **route/port policy remains open** |

Toyota's observed Camry traffic still uses **standard IDs for application CAN-FD** and
extended IDs for the classic diagnostic/XCP-style surface, but the standard-ID `0x090`
discriminator disproves identifier width as the missing condition. The exact F33 RSCFD itself
is capable of both extended identifiers and CAN-FD and its GAFL rules expose no source-node
predicate. The remaining distinction is upstream of F33 admission: source/port/routing policy
and, critically, the protection envelope carried by native FD traffic.

The clean discriminator is therefore a **known native standard-ID FD route**, not another
extended private-ID experiment.  `0x090/32` is the preferred parked probe because exact
F33 routes it through an ordinary additive-checksum gate rather than SecOC.

The September-19 live discriminator now closes that branch. A current native `0x090/32`
was captured on Panda bus0 and its first 8-byte Toyota additive check was verified exactly:
`B7 = sum(B0..B6) + CAN-ID(0x90) + length(8) (mod 256)`. The host flipped only B0 bit0
and left B7 unchanged, making the frame deterministically invalid while retaining the native
32-byte shape. Panda transmitted that **standard-ID CAN-FD** frame and returned the exact
payload; TEC, REC, total-error count and bus-off state were unchanged. Exact F33 route-40's
validator-failure counter at `FEBE53C0` remained **0 -> 0**. Therefore the host frame did not
reach the existing route-40 integrity validator. This disproves **extended-ID FD versus
standard-ID FD** as a sufficient explanation for the earlier private-endpoint failure.

The timing/BRS follow-up closes the remaining obvious transmitter-format knobs. Test Panda
`54369098` changed 2-Mbit/s DBTP from upstream 80% to exact-F33 70%
(TSEG1=13/TSEG2=6/SJW6). Test Panda `f8f5a8f6` additionally allowed back-to-back host
BRS-on and host-forced-BRS-off FD32 sends while holding that timing fixed. In both cases the
exact invalid `0x090` payload had a Panda TX return, zero safety blocks and zero TEC/REC/error
growth, while the F33 route-40 validation-failure byte did not move. Thus **ID width, BRS,
nominal/data timing, ISO mode, DLC and the local additive-checksum construction are not
sufficient explanations**. Source/port/routing regeneration and an upstream authentication
gate remain.

The earlier `f33-fd-ingress` transient-ring observer is superseded by the simpler stock
validator/counter analysis. Exact route construction is descriptor index35 + base5 = **route
40**. Route byte `0x21FB8[40]=0x10` enables the generic integrity callback. Global gates
`0x28FD6/0x28FD7` are both `0x5A`, and integrity record22 at `0x28FE4+22*8` is
`28 00 00 0B B8 01 02 5A`, enabling `0x6A3BE -> 0x6A32C` for route40.
`0x6A32C` reads only payload B0..B7 and accepts exactly
`B7 == (sum(B0..B6) + low8(CAN-ID) + ID[10:8] + 8) mod 256`; on mismatch it calls
`0x8E7BA(40)`, which increments **`FEBE5398+40 = FEBE53C0`**. That counter bank is
cleared only by startup initializer `0x8E74E`; normal valid frames do not clear it. Therefore
a post-send `FEBE53C0` delta is a valid sticky witness for a frame that reaches the local
route-40 checksum validator.

Native Camry `0x090` has a second, independent protection layer on the wire. Across the
retained Sep-1 capture, B28[7:4] reset-low2 matches preceding authenticated `0x00F` on
**364/364** eligible frames and message-low2 advances `+1 mod4` on **355/355** same-reset
pairs; the first `0x090` in each of 12 inspected reset epochs has message-low2=1. The
remaining 28 trailer bits are effectively frame-unique. This is the ordinary Toyota-P5
`FV4 || MAC28` shape. Sienna P1M-E independently defines CAN-FD `0x090` as an ordinary
SecOC profile authenticating `DataID 0x0090 || payload[28] || full freshness[6]` and
transmitting the upper 28 CMAC bits. Exact F33 does **not** run its local SecOC verifier on
route40, so the natural next discriminator is whether an upstream Brake/EBU boundary validates
that P5 envelope before the frame reaches F33. The generic `f33-sign` tooling now includes
`verify-native-090` to ask exact-F33 selector-4 command5 whether its slot4 key reproduces a
captured native `0x090` MAC28 without transmitting `0x090`.

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

- the exact FRC functions/state variables implementing feature eligibility, priority and
  current request ownership before `5282`;
- the internal FRC packer/security-core/HSM split that turns the selected generic request
  into protected `0x08A`;
- the exact Brake/VMM verification, request-arbitration, result, and request-generation transform from the
  feature-selected but pre-VMM-arbitration `0x08A` request to `0x081` and B6 (without assuming a
  byte/value-preserving transform);
- the exact physical/security implementation of native B6 delivery from Brake to EPS;
- which internal node owns each SecOC freshness/signing operation and the clean external
  replacement/suppression boundary;
- B6 secondary-field OEM names;
- longitudinal A/B upper-versus-lower ordering and remaining policy bits.

The patent is an architecture source, not proof that every block is placed in exactly the
same ECU on F33.  Those exact-Camry conclusions continue to require firmware/dynamic
joins.

## 11. Openpilot design consequence

The preferred native integration target is no longer “find a CAN command that moves the
actuator.” On this exact Camry, openpilot is **not** naturally another Brake-visible
lateral application beside LTA/LDA/PDA; those applications live inside the FRC. The
architecture-preserving choices are therefore:

```text
(A) join/replace the FRC's internal selected-request stage, if an internal interface is
    recovered

or

(B) replace the feature-selected protected 0x08A generic request egress while preserving
    the downstream Brake/VMM arbitration, result, stability, availability and actuator-target contracts
```

Either approach respects the actual placement of Toyota's feature selector. The
successful EPS-resident B6 signer remains a development fallback because it enters much
farther downstream at the actuator-target layer.

Accordingly:

- do not revive Camry `0x160` longitudinal output;
- do not send `0x08A` directly to EPS;
- do not treat `0x081` as an EPS command;
- do not require B6 to become exclusive EPS authority;
- do not infer “stock LTA uses no B6” from Panda-visible absence—the later internal
  capture proves native B6 delivery exists at F33;
- recover the FRC feature-owner selector and `5282` -> protected-`0x08A` pack/sign path;
- separately recover the Brake/VMM verification/request-arbitration/result/request-generation boundary,
  including the exact relation of the feature-selected `0x08A` request to native B6 and
  the Vehicle Motion Control `0x10A5..0x10AA` target surface.

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
