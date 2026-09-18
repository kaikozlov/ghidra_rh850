# Toyota US20230166772A1: selective request invalidation and rejection feedback

**Status:** external-source architecture analysis, researched 2026-09-18.

**Primary source:** Toyota Motor Corporation, US20230166772A1, *Motion
manager, autonomous driving apparatus, and control system*, filed 2022-10-31,
Japanese priority 2021-194275 (2021-11-30), published 2023-06-01. A convenience
copy is retained locally at
`REFERENCE/patents/US20230166772A1.pdf` and intentionally remains untracked.

This patent is unusually relevant to the current TSS3 takeover/fault-state work
because it describes a **healthy, intentional non-selection path** for one ADAS
client. The important mechanism is more specific than "block a request and tell
the client it lost":

1. the suppressed application continues generating its kinematic plan;
2. a *different* application asks the motion manager to invalidate or
   de-prioritize that plan;
3. the motion manager latches that policy state and removes only the selected
   plan from ordinary arbitration;
4. other plans remain eligible;
5. the manager separately informs the suppressed client that its non-selection
   is intentional so the client can avoid treating repeated non-selection as a
   system abnormality;
6. a distinct cancellation request restores ordinary arbitration.

That is an architecture for **selective arbitration policy**, not transport
failure. It is therefore a much closer model for clean coexistence than cutting
the complete FRC request publication.

## Evidence boundary

The patent proves Toyota disclosed this architecture and gives Toyota-authored
names for its interfaces. It does **not** prove that the exact 2026 Camry F33
implements this embodiment, that its policy input is externally accessible, or
that any named patent signal has a one-to-one CAN/CAN-FD encoding.

In particular:

- the patent supplies no CAN ID, SecOC DataID, PDU layout, freshness rule, or
  byte/bit assignment;
- "invalidation request" and "request rejection information" are two different
  directions and must not be conflated;
- Toyota explicitly allows the policy request to be implemented as a
  **priority request rather than literal invalidation**;
- the exact F33/P5 diagnostic corpus currently exposes priority and arbitration
  vocabulary, but no field has yet been recovered as this patent's
  manager-to-client rejection feedback;
- later P6 diagnostic surfaces provide strong cross-generation vocabulary, not
  proof of the P5/F33 wire realization.

## 1. Physical/function architecture

Figures 1 and 2 place the disclosed functions as follows:

```text
                        central ECU
                            |
              +-------------+-------------+
              |                           |
          ADAS ECU                       ADK
   driver-assistance system              |
  AEB LKA ACC ASL PCS ISA ...            ADS
              \                         /
               \       PLN1            /
                +----------------------+
                           |
                           v
                    +-------------+
                    | motion      |
                    | manager 200 |
                    +-------------+
                    | reception   | 202
                    | arbitration | 204
                    | calculation | 206
                    | distribution| 208
                    +-------------+
                      |    |    |
                   ACL1  BRK1  STR1
                      |    |    |
                  power  brake steering
                  train  system  system
                      \    |    /
                   ACL2 BRK2 STR2
                         |
                       VSS2
                         ^
                    sensor group
```

The embodiment places motion manager 200 in Brake ECU 20. The patent also says
the manager may be a separate ECU or located elsewhere; the functional graph is
the important part, not universal Brake-ECU placement.

The driver-assistance system includes AEB 102, LKA 104, ACC 106, ASL 108,
PCS 110, ISA 112, and other applications. ADS 122, running in the removable ADK
120 in the illustrated embodiment, supplies autonomous-driving application
124. See paragraphs [0049]-[0064].

### Control interfaces

The application side sends `PLN1`: kinematic plans plus identification. The
examples include target acceleration/deceleration from longitudinal clients
and steering angle from LKA/AD. The manager distributes actuator-oriented
requests as `ACL1`, `BRK1`, and `STR1`.

Actuator state returns as `ACL2`, `BRK2`, and `STR2`; the steering-state
example includes reliability, driver-grip state, steering-wheel operating
torque, and steering-wheel angle. Sensor state returns as `VSS2`. The manager
returns application-facing state as `PLN2`.

This fits the broader Toyota VMM family already joined to the current TSS3
request/result/target split, but this patent's novel contribution is the policy
placed **inside arbitration**.

## 2. The two arrows that must not be conflated

Figure 3 is the key architectural picture. It shows AD 124, PCS 110, and ISA
112 supplying acceleration/deceleration requests and IDs to reception unit 202.

Two dashed paths are different signals:

```text
                         A: policy request
                 AD -----------------------+
                                            |
                                            v
 AD request + ID ----\             +--------------------+
 PCS request + ID ----> reception ->| invalidation       |
 ISA request + ID ----/              | processing 204a    |
                                    +--------------------+
                                             |
                            PCS excluded      | remaining requests
                                             v
                                    +--------------------+
                                    | accel/decel        |
                                    | arbitration 204b   |
                                    +--------------------+

                                    |
                    B: explanation | request-rejection information
                                    v
                                   PCS
```

### Arrow A — requester -> motion manager

Paragraph [0098] says autonomous-driving application 124 may output a request
for invalidating the PCS kinematic plan and a separate cancellation request in
addition to its own kinematic plan, request value, and ID.

This is the **takeover/policy input**.

### Arrow B — motion manager -> suppressed application

Paragraph [0104] says that when the PCS plan is invalidated, invalidation
processing unit 204a outputs **request rejection information** to PCS indicating
that the PCS kinematic plan is invalidated.

Paragraph [0106] supplies the reason: after receiving that information, PCS can
restrict a determination that an abnormality occurred merely because the
kinematic plan it set was not selected.

This is the **intentional-non-selection feedback**.

The distinction matters directly to our GTS interpretation. A diagnostic field
named "PCS Rejection Request Determination..." sounds like a decision/request
to reject PCS and is therefore conceptually closer to arrow **A** than arrow
**B**. It must not be cited as proof that we have found the manager-to-PCS
feedback channel.

## 3. The manager excludes PCS *inside* arbitration

Paragraphs [0099]-[0103] make the placement explicit.

The manager receives:

- kinematic plans and IDs from the applications; and
- the invalidation request from AD.

Arbitration unit 204 is divided into:

- invalidation processing unit 204a; then
- acceleration/deceleration arbitration unit 204b.

With invalidation active, 204a does **not** forward the PCS plan to 204b. It
continues forwarding the AD and ISA plans. With invalidation inactive, all of
them are forwarded.

Thus the patent does **not** describe making PCS disappear from the network.
The PCS request is still received by the manager. Its eligibility is changed
after reception.

That is a major distinction from the current blunt F33 experiment:

```text
patented healthy suppression:

PCS request remains alive
       |
       v
manager receives it
       |
       X  policy excludes it from arbitration
       |
other valid clients continue
       |
PCS gets explicit intentional-rejection feedback


our complete-source blocking experiment:

FRC/TSS request publication disappears
       |
       X  receiver sees request/communication loss
       |
Brake/FRC supervision and fail-state machinery can activate
```

A clean F33 takeover mechanism, if the platform exposes one, is therefore more
likely to preserve the native request/result communication contract while
changing **eligibility/priority**, rather than simulate absence of the source.

## 4. Invalidation is stateful, not merely a per-cycle request bit

Figures 4 and 5 expose two cooperating state machines.

### ADS/requester state machine — Figure 4

When autonomous driving is executing:

1. test whether invalidation has already been requested;
2. if not, output the invalidation request;
3. set a local request flag ON.

When autonomous driving is no longer executing:

1. test whether cancellation has already been requested;
2. if not, output invalidation cancellation;
3. set the request flag OFF.

The requester therefore treats invalidation/cancellation as **transition
commands**, not as a requirement to resend an "invalidate PCS" bit forever.

### Motion-manager state machine — Figure 5

The manager independently maintains an invalidation flag:

1. receive invalidation request -> set invalidation flag ON;
2. receive cancellation -> set invalidation flag OFF;
3. while flag is ON:
   - output request values other than the PCS request to the ordinary
     acceleration/deceleration arbiter;
   - output request rejection information to PCS;
4. while flag is OFF:
   - output all request values to the ordinary arbiter.

The example runtime in paragraphs [0129]-[0138] follows exactly that sequence:
manual driving starts with both flags OFF; autonomous-driving entry sends the
one-time invalidation request; the manager remains in the invalidated state;
autonomous-driving exit sends cancellation; normal eligibility returns.

### Why this matters to TSS3 RE

This gives us a new class of thing to search for: **state-changing policy
commands and latched manager state**.

If F33 uses a related realization, the clean handoff signal may not be a value
that continuously mirrors "openpilot owns lateral." It could be a one-shot
transition, a state/authority request, or an application-mode change that
causes the manager to latch a different eligibility configuration until a
cancel/release transition.

It also provides a plausible architectural reason that takeover-related state
can outlive restoration of the raw request stream: policy/fail-state machines
can be latched independently from transport state. That is a hypothesis for
F33, not proof that the current persistent DRCC/FRC latch is this patent's
invalidation flag.

## 5. The claims are broader than literal "PCS invalidation"

The specification deliberately generalizes the implementation.

### Priority can replace explicit invalidation

Paragraph [0140] says the request information does not have to literally ask to
invalidate the second plan. It may instead indicate that the first kinematic
plan is to have **higher priority** than the second.

Claims 2 and 3 preserve both forms:

- claim 2: request information includes a request to invalidate the second
  kinematic plan;
- claim 3: request information includes a request to make the first plan higher
  priority than the second.

This is important for TSS3 because the P5 recorder already exposes several
priority-oriented fields even though we have not found an "invalidation
request" field by name.

### Feedback can carry the request information itself

Paragraph [0141] says the manager need not use the exact "request rejection
information" embodiment. It may output information corresponding to the
invalidation request to PCS; that information can serve the same purpose of
preventing PCS from diagnosing an abnormality because its plan was not
selected.

Claim 5 similarly claims outputting information on the received request
information to the second system.

So the semantic contract is stronger than the literal signal name:

> the suppressed client is informed that its non-selection is intentional.

The physical realization is intentionally left broad.

### The target need not be PCS

Paragraph [0142] says the second application may be AEB, ACC, ASL, or another
application.

Paragraph [0145] says the requesting first system need not be ADS; another
driver-assistance application can issue the request.

Thus the architecture is a general **client-vs-client arbitration policy
mechanism**, not solely an autonomous-driving special case.

## 6. Lateral/steering is explicitly in scope

This patent is not only useful for longitudinal PCS.

Paragraph [0143] explicitly says that, instead of the acceleration/deceleration
example, the arbitration/invalidation processing may arbitrate **steering-angle
kinematic plans**. It names LKA and LTA as examples of applications that set
steering-related plans.

Therefore the useful lateral abstraction is:

```text
LTA/LKA/other lateral client supplies plan + application ID
                       |
                       v
                 motion manager
                       |
        +--------------+--------------+
        | policy / eligibility state  |
        +--------------+--------------+
                       |
                lateral arbitration
                       |
                  steering target

suppressed lateral client <--- intentional rejection/status information
```

The patent does not tell us which exact TSS3 field carries such a policy, or
whether P5 F33 implemented this branch at all. But it removes any reason to
treat the concept as "longitudinal-only."

## 7. Selective priority preserves other constraints

The summary and claims also describe a **third system** whose kinematic plan the
first system does not necessarily outrank. Claims 6-10 cover a first, second,
and third system, and include an embodiment where the third system performs
control to comply with law.

That is architecturally important. The disclosed takeover is not "autonomous
driver gets absolute control." It is selective:

```text
first system     > second system
first system     !> protected third system
```

This is consistent with Toyota separating ordinary application arbitration
from independent stability/safety paths elsewhere in the VMM patent family.
For our openpilot work, the useful conceptual target is therefore not to erase
Toyota's whole control stack. It is to replace/supersede the intended native
continuous-driving client while retaining independent constraints and actuator
protections.

Again, this is an architecture lesson, not evidence of a user-accessible F33
priority API.

## 8. Stronger GTS joins from this close read

A second pass over current GTS+ resolves the previously loose patent-vocabulary
hits much more precisely.

### 8.1 P6 ADCU: PCS rejection decision is a real recorder field

The master English string:

`PCS Rejection Request Determination Based On Functional Safety`

is string index **223144**. Across the current Gen ECU databases, that exact
index is referenced only by:

- `ADCU_P6.ddb`;
- `ADCU_P6F.ddb`.

In both, it is row 797 of table 167,
`CDbDDRFreezeFrameTable`, and its recovered source descriptor is:

```text
DID$20D4-byte16-bit$FF
```

The immediately following row 798 is:

```text
Arbitration Result (Vertical ID Value)
DID$20D4-byte25-bit$FF
```

and row 799 is:

```text
Radar Axis Offset ON Flag
DID$20D4-byte34-bit$FF
```

So later P6 ADCU diagnostic snapshots put a PCS-rejection determination and an
arbitration-result ID inside the **same packed 0x20D4 snapshot**.

This is materially stronger evidence than an orphan master string, but the
direction matters: the wording is "Rejection **Request Determination**." It is
consistent with a decision to request PCS suppression/priority policy (the
patent's arrow A). It is **not** direct evidence for the manager-to-PCS
"request rejection information" feedback (arrow B).

Also, `0x20D4` is recovered here through a DDR freeze-frame descriptor, not
as an ordinary ADCU P6 Data Monitor/RDBI item. The current `tools/gts did`
surface does not expose it as a normal monitor.

### 8.2 P6 Hybrid/EV PCM: request IDs and rejection factors are adjacent

The two master strings:

- `Driving Force Lower Limit Request Rejection Factors`;
- `Driving Force Upper Limit Request Rejection Factors`;

are indices **206092** and **206093**. Their exact current ECU references are
rows 867/868 of `HE_PCM_A_P6.ddb` table 164,
`CDbRoBFreezeFrameTable`.

The adjacent four rows are:

```text
865  Required Driving Force Lower Limit ID
866  Required Driving Force Upper Limit ID
867  Driving Force Lower Limit Request Rejection Factors
868  Driving Force Upper Limit Request Rejection Factors
```

Their recovered layout metadata places those four items in successive
8-bit ranges 0..7, 8..15, 16..23, and 24..31 of the same recorder group.

That is strong cross-generation evidence that Toyota treats **who requested a
bound** and **why that request was rejected** as paired result/status data.

It still does not prove the exact PCS feedback mechanism in F33, and this P6
powertrain-domain result should not be back-projected onto the P5 lateral wire
without a direct join.

## 9. Exact P5/TSS3 evidence: priority exists, feedback remains open

The exact P5/TSS3 Operation FFD already contains request/arbitration vocabulary
that fits the patent's broader priority embodiment:

- `5280_7 = TSS acceleration request low priority flag`;
- `5284 = Arbitration result_longitudinal ID`;
- `5285 = Arbitration result_lateral ID`;
- `57DB = Arbitration result Acceleration`;
- `57DE = Arbitration result Pinion angle`;
- PDA(OAA) records include **Shift Priority Request** and **Response Priority
  Request**;
- PDA(DA) records include **Brake Priority Request of Lower Limit**,
  **Shift Priority Request of Lower Limit**, and an **acceleration request low
  priority flag**;
- FRC_P5 ordinary diagnostics expose
  `0x1B06 ISA Speed Change Priority Request (Upper Limit)`.

This proves that "priority request" is native Toyota/TSS3 vocabulary on P5,
particularly on the longitudinal side. It does **not** recover an equivalent
lateral priority/invalidation field.

A full current TSS3 Operation-FFD name search finds only one item containing
"reject" or "invalidation": the event trigger **`240E LCA Reject`** (with
`240F LCA Cancel`). That trigger records an LCA feature event; it should not
be equated to the patent's manager-to-client request-rejection feedback.

Thus the evidence state is:

| Mechanism | Patent | P6 diagnostics | P5/F33 |
|---|---|---|---|
| application plans + IDs | explicit | explicit successor vocabulary | **recovered** 5280/5281/5282 |
| per-client priority/invalidation request | explicit | **PCS rejection request determination** | priority vocabulary recovered longitudinally; lateral control unknown |
| manager latches policy until cancel | explicit | not yet mapped | **functional analogue belongs inside FRC application state** |
| client excluded inside arbitration | explicit | consistent with FRC feature-local state + generic request egress | **internal FRC selection, exact implementation unrecovered** |
| arbitration result ID | explicit VMM-family concept | 0x20D4 byte25 vertical result | **recovered downstream 5284/5285 result surface** |
| result physical value | explicit VMM-family concept | successor data exists | **recovered downstream 57DB/57DE result surface** |
| rejection reason/factors | explicit semantic concept | **recovered** longitudinal P6 RoB fields | exact P5 internal/external realization not mapped |
| manager -> suppressed-client intentional-rejection feedback | **explicit** | no exact directional join yet | **if present for lateral feature competition, likely internal to FRC rather than an FRC<->Brake wire field** |

## 10. What this changes about the current F33 fault-state hypothesis

### Strong conclusion: complete 0x08A loss is the wrong shape for a healthy handoff

Current exact-car evidence says protected `0x08A` is the FRC/TSS request-side
publication and Brake continues supervising request loss when FRC normal Tx is
suppressed.

This patent's takeover architecture does the opposite: keep the suppressed
client present, receive its request normally, and change only its arbitration
eligibility.

Therefore a complete `0x08A` drop should not be expected to look like a
healthy version of this mechanism. It removes much more than one client's
eligibility and can legitimately activate communication/request-loss
supervision.

### Exact-Camry correction: the lateral eligibility/priority control plane is inside the FRC application

The earlier wording treated the patent as though an external FRC->Brake policy
signal might decide which of LTA/LDA/LCA/PDA wins. That is the wrong exact-Camry
model.

These functions are **simultaneously enableable applications inside the FRC
application software**. LTA continuously centers, LDA can intervene on a lane
departure, LCA handles lane-change assistance, PDA/SDG provides proactive
steering, PCS has its own steering path, and so on. Their enable/configuration
state is not their current ownership state. The FRC's internal state machine
selects which feature currently supplies the generic lateral request.

The first external representation of that decision is protected `0x08A`:

```text
FRC internal applications
  LTA / LDA / LCA / PDA / PCS / ...
          |
          | feature settings + perception + driver + vehicle state
          v
  FRC internal eligibility / priority / owner selection
          |
          v
  5282 generic TSS lateral request
          |
          v
       0x08A egress
          |
          v
      Brake / VMM
```

Therefore the relevant search target is **the FRC application state and code that
produces `5282`/`0x08A`**, not a new external policy PDU between FRC and Brake.
The patent's invalidation-vs-priority distinction remains useful for naming the
internal selection semantics. It does not imply that its Arrow A must exist on
vehicle CAN in this implementation.

### Separate question: how does the FRC represent a losing feature internally?

The patent says a suppressed application can be told that non-selection is
intentional so it does not diagnose an abnormality. On the exact Camry, that
feature-to-feature relationship is inside the FRC application. Any equivalent
rejection acknowledgment can therefore be an internal software state, return
value, shared object, or recorder-visible field; it does **not** need to cross
the FRC<->Brake network boundary.

`5284/5285`, `57DB/57DE`, and Brake-owned `0x081` remain downstream
result/status surfaces for the generic request. They can feed FRC application
state, but they should no longer be presented as the leading location for the
patent's manager->suppressed-client Arrow B. Finding Arrow B, if an equivalent
exists, now means tracing the FRC's feature-local state machines and their
selection/rejection bookkeeping.

## 11. Smallest discriminating experiments/searches

The patent suggests better experiments than another all-or-nothing source
block.

### A. Observe FRC-internal feature handoffs at the recorder/egress boundary

Collect synchronized FRC Operation FFD / raw CAN around native state transitions
that change the current lateral owner without an ECU outage:

- LTA on -> off;
- LCA request -> reject/cancel;
- LTA <-> LDA interaction;
- DRCC set/cancel;
- PDA intervention where safely reproducible;
- driver override.

Correlate the FRC's feature-local objects with its generic request egress and the
downstream Brake result:

```text
feature-local FRC state/request
  550D/5531  LDA
  560D/5631  LTA
  568x       LCA
  5Axx/5D8D  PDA/SDG
      |
      v
FRC internal owner / eligibility selection
      |
      v
5282 generic lateral request -> 0x08A
      |
      v
5285 / 57DE downstream result -> 0x081
```

The key signature is a feature-local requester that remains enabled or active
while the FRC's generic `5282` owner changes to another application, with no
request-loss or fail-class transition. That is the exact-car analogue of the
patent's client invalidation/priority behavior.

### B. Search state-change semantics, not just value carriers

Patent-guided terms:

- priority request;
- low priority;
- invalid / invalidation;
- rejection request;
- rejection factors;
- arbitration target;
- permitted / prohibited;
- application state;
- autonomous-driving execution state;
- cancellation request.

The exact P5 corpus already justifies "priority" as a high-value search term.

### C. Treat Arrow A and Arrow B as separate **FRC-internal** recovery problems

Do not infer one from the other, and do not assume either arrow is a vehicle-CAN
signal on this car.

**Arrow A question:** what FRC-local setting/state/policy makes one feature
ineligible or lower priority than another?

**Arrow B question:** what FRC-local state tells the losing feature that its
non-selection is intentional rather than a broken downstream actuator path?

The external `0x08A`/`0x081` pair brackets this internal state machine: `0x08A`
is its selected-request egress and `0x081` is downstream result/status feedback.
The feature-selection arrows themselves can remain entirely inside the FRC
application.

### D. Look for a latched transition

If a candidate FRC-local policy/state transition is found, determine whether it is:

- continuously evaluated from feature state;
- edge-triggered / one-shot;
- latched until explicit cancellation;
- automatically cleared by mode/ignition/fault.

The patent's Figure-4/Figure-5 design specifically predicts a **set/cancel
latch**, but the exact Camry may realize the same semantics as ordinary FRC
application state rather than an explicit externally commanded latch.

## 12. Retained Camry logs: the generic request/result boundary is now much tighter

The retained healthy road corpus gives a useful answer to where the patent's
"losing application continues to request" behavior is **not** visible.

A fresh transition-aligned scan over the repository's 12 selected Camry road
routes (1c/27/29/2a/2c/2d/37/3b/3c/3d/3e/3f) compared native FRC-side
0x08A B21[5:0] request IDs with Brake-side 0x081 B13[5:0] result IDs.

There are **473 request-ID transitions** in those routes:

| request transition | count | result-transition median lag | maximum lag |
|---|---:|---:|---:|
| 0 -> 4 | 3 | 29.819 ms | 39.779 ms |
| 0 -> 11 | 136 | 29.756 ms | 40.819 ms |
| 0 -> 18 | 81 | 29.711 ms | 42.893 ms |
| 4 -> 0 | 4 | 24.911 ms | 30.365 ms |
| 4 -> 11 | 2 | 24.684 ms | 39.484 ms |
| 11 -> 0 | 164 | 21.074 ms | 42.577 ms |
| 11 -> 4 | 2 | 35.315 ms | 39.773 ms |
| 18 -> 0 | 52 | 29.373 ms | 40.485 ms |
| 18 -> 4 | 1 | 10.777 ms | 10.777 ms |
| 18 -> 11 | 28 | 24.727 ms | 39.669 ms |

Every one of the 473 request transitions has the **same old-ID -> new-ID result
transition within 100 ms**; there are zero unmatched transitions. The maximum
observed lag is 42.893 ms. In the high-volume 27/3b/3c/3d/3e/3f subset, no
request/result-ID disagreement episode lasts 50 ms.

This is consistent with the different publication cadences. Across routes 3b
and 3c, 0x08A is roughly a 40-Hz-class publication (median observed interval
about 22.8 ms with rlog batching/jitter) while 0x081 is tightly about 30 ms
(about 33-Hz-class). The short old-ID/new-ID mismatch is therefore a normal
request->result pipeline delay, not evidence that a request is being rejected.

The angle values reinforce that interpretation. When request/result IDs match,
0x081 B16:B17 tracks the newest 0x08A B18:B19 request extremely tightly. For
active ID11 in routes 27/3b/3c/3d/3e/3f, the median absolute raw-word
difference is zero and the latest nearest-sample scan gives p90 = 1 raw count
on every one of those routes.

### 12.1 Direct application-to-application handoff exists with no ID0 gap

The most patent-relevant natural events are the nonzero-to-nonzero transitions.

There are 28 direct **ID18 SDG/PDA-SA -> ID11 LTA/LCA** transitions. A
representative route-27 event changes request ID18 -> ID11 at time zero while
the Brake result remains ID18 for one result cycle and then becomes ID11
30.025 ms later. 0x081 B11 stays 0x04; there is no request-loss state. The
result angle changes from the old ID18 value to the new ID11 request family at
the same result update.

Route 3b shows the same handoff with a 12.995-ms result lag. Across all 28
events the result follows in <=39.669 ms.

The cleaner isolation is the rare **ID11 <-> ID4** handoff. In a route-3c
ID11 -> ID4 event:

    time       0x08A request                  0x081 result
    ---------  -----------------------------  --------------------------
    -19.7 ms   ID11, angle -48               ID11, angle -48
      0.0 ms   ID4,  angle -48               -
     +9.8 ms                                  ID11, angle -48
    +30.1 ms   ID4,  angle -39               -
    +39.8 ms                                  ID4,  angle -39

Within request bytes B20:B24 that event changes
40 0B 10 20 64 -> 40 04 10 20 64: in that five-byte slice only the recovered
application ID changes. Cruise state and request level remain unchanged. The
result then publishes the new application ID and the **latest** ID4 angle at its
own cadence.

This is direct dynamic evidence for the GTS distinction between request
application ID (5282) and arbitration-result application ID (5285), while also
showing that normal Toyota handoff does not require a no-request interval.

### 12.2 What the healthy logs do *not* show

Healthy retained CAN never shows a generic 0x08A lateral request continuing for
a meaningful interval while a different 0x081 application ID wins. The only
disagreements are the one-result-cycle transition delays above.

That is expected once the ECU ownership is stated correctly. LTA, LDA, LCA,
PDA/SDG and PCS are FRC-resident functions. Their competition is resolved by the
**FRC application state machine before `5282`/`0x08A` is published**. The patent's
interesting state -- one application remaining enabled/alive while another has
priority -- can therefore exist entirely inside the FRC while the external wire
shows only the currently selected generic request.

Brake receives that already-selected FRC lateral request. It can still validate
it, combine it with vehicle-motion/stability constraints, generate downstream
actuator targets, and return result/status; what the retained Camry evidence does
not support is treating Brake as the place where LTA versus LDA versus PDA is
chosen.

Current GTS exposes exactly the FRC-local state we should inspect around that
selection boundary:

- 5531 -- LDA lateral ID / request pinion / assist / damping;
- 5631 -- LTA lateral ID / request pinion / assist / damping;
- 5A09/5A0A/5A0D -- PDA(OAA) lateral ID / pinion / gains;
- 550D -- LDA inhibition/control-state information;
- 560D -- driver-steering detection, **LTA Driver Steering Control
  prohibited**, LTA DDR control state;
- 5681/5685/568E -- LCA control/fail/cancel-condition state;
- 5A0F -- PDA(OAA) invalid flags for sensor, control-continue,
  brake/powertrain, and EPS conditions;
- 5D8D -- PDA(SA) DDR control state.

The generic `5282` object and protected `0x08A` egress sit after those
feature-local objects. Downstream `5285/57DE` and `0x081` then report the
Brake/VMM result of the FRC-selected generic request.

Same-car stored Operation FFD already proves the layers are real. The
`2844 Lane Departure Warning Operation under LTA` records contain an active
feature-local `5531` request while `5631` is zero and EPS pinion follows the
`5531` request, but those records do not include generic `5282/5285`. Conversely
`2294/0001` contains generic request ID18 in `5282` and matching downstream
result ID18 in `5285`. What is still missing is one synchronized record that
shows the **FRC-internal handoff itself**: multiple feature states enabled, one
feature-local request becoming preferred/inhibited, and `5282` changing owner.
That is an FRC application RE problem, not a search for simultaneous external
lateral requests at Brake.

### 12.3 A still-unresolved request-side bit looks driver-steering-related, not like the policy latch

The transition review also gives one useful bound on unresolved 0x08A metadata.
Across the existing 12-route lateral census, request byte B23 has only values
0x00 and 0x20 for the known active lateral clients:

| request ID | B23=0x00 | B23=0x20 |
|---|---:|---:|
| 4 LDA | 208 | 90 |
| 11 LTA/LCA | 560,161 | 93,425 |
| 18 SDG/PDA-SA | 0 | 52,853 |

For ID11 specifically, a synchronized scan against exact-FRC-side
0x371 B20[4] (the recovered low-sensitivity driver-steering/hands-on candidate)
and exact-EPS steering torque shows B23[5] is strongly steering-related:

- B23[5]=0: low detector asserted on 23.3% of matched frames; median
  |steering torque| = 0.28 N.m;
- B23[5]=1: low detector asserted on 79.0% of matched frames; median
  |steering torque| = 0.86 N.m and p90 = 1.33 N.m;
- when the low detector is clear, B23[5] is set only 4.9% of the time;
- when the low detector is set, B23[5] is set 38.8% of the time.

B23 edges tend to occur hundreds of milliseconds after the nearest same-direction
low-detector edge, and nine retained direct ID11->ID0 withdrawal events all have
B23=0 despite spanning both lower and higher driver-torque conditions. Therefore
B23[5] is **not** a simple lateral-request withdrawal/invalidation bit.

This is interesting in the broader Toyota VMM family because US20200070849A1
defines a one-bit **driver steering flag** inside the lateral request package and
copies the selected flag into the post-arbitration steering instruction. B23[5]
is now a plausible wire candidate for a driver-steering/override-related request
attribute, especially because PDA-SA/SDG (ID18) has it permanently asserted in
the retained corpus. It remains a hypothesis: exact OEM naming still requires a
GTS/firmware/dynamic join, and it should not be repurposed as the
US20230166772A1 eligibility/priority input.

### 12.4 Faulted September-17 drives separate communication health from fail class

The post-bootstrap routes e9, ec, and ee provide an important negative control
against conflating request loss, arbitration loss, and actuator/fail state.

With the restored stock harness topology, all three routes continue carrying
native 0x08A and 0x081 on logical bus1:

| route | 0x08A frames | request ID | 0x081 frames | B11 | B13 |
|---|---:|---:|---:|---:|---:|
| e9 | 14,890 | 0 | 12,407 | 0x04 throughout | 0xC0 throughout |
| ec | 44,330 | 0 | 36,943 | 0x04 throughout | 0xC0 throughout |
| ee | 40,720 | 0 | 33,936 | 0x04 throughout | 0xC0 throughout |

Interpreting the already recovered/candidate fields:

- B11 does **not** enter the 0x14 request-loss state;
- B13 low six bits remain result ID0;
- B13 high two bits remain candidate fail class 3;
- the result/reference angle still tracks the latest request/reference with
  median raw difference zero (p90 33/9/6 counts on e9/ec/ee).

So Toyota can maintain a healthy request/result transport relationship while
the lateral system is in a failure-decided state. That is distinct from the
separate FRC-normal-Tx suppression experiment, where complete request loss sets
0x081 B11 from 0x04 to 0x14 while B13's fail-class candidate remains healthy.

The current evidence therefore separates three observable states:

| state | request publication | B11 request-loss | B13 fail class | request/result IDs |
|---|---|---|---|---|
| healthy handoff | alive | clear | healthy | differ only for one result cycle |
| complete FRC request loss | absent | asserted | can remain healthy | no normal request/result handoff |
| EPS/lateral failure-decided | alive | clear | candidate 3 | ID0 -> ID0 in retained routes |

The patent predicts a fourth state worth hunting: a healthy policy rejection
where the losing feature remains alive internally, request-loss stays clear,
the fail class stays healthy, another application intentionally wins, and the
losing client receives rejection/status feedback.

### 12.5 Best next passive capture

The highest-value experiment is no longer another whole-frame block. It is a
**natural client handoff** with synchronized FRC Operation FFD and CAN.

The best candidates are:

1. direct ID18 -> ID11 (PDA-SA/SDG -> LTA/LCA), already seen 28 times;
2. ID11 <-> ID4, because the request profile can remain otherwise unchanged;
3. 240E LCA Reject / 240F LCA Cancel, whose Toyota recorder definition already
   retains 20 pre-trigger and 5 post-trigger samples at 0.2 s.

For those events capture, if the record family permits:

    feature-local:
      550D  LDA inhibition/control state
      5531  LDA request tuple
      560D  LTA driver-steering/prohibition/control state
      5631  LTA request tuple
      5681  LCA control state
      5685  LCA fail state
      568E  LCA cancel condition
      5A09/5A0A/5A0D/5A0F  PDA(OAA) request + invalid state
      5D8D  PDA(SA) state

    generic/result:
      5282  generic lateral request
      5283  lateral fail class
      5285  arbitration-result lateral ID
      57DE  arbitration-result pinion angle
      57D4  PCS->BRK request logical error

    wire:
      0x08A
      0x081

The patent-signature observation would be:

1. multiple FRC features remain enabled/available;
2. one feature-local request/state remains alive while an inhibition/priority or
   trigger condition changes;
3. the FRC's generic `5282` owner changes to another application and `0x08A`
   immediately expresses that new owner;
4. downstream `5285`/`0x081` follows the new FRC-selected request while
   `5283_1` stays healthy and `0x081 B11` stays out of request-loss;
5. ideally an FRC-local rejection/cancel/reason state explains why the losing
   feature did not own `5282`.

That would distinguish intentional **FRC application selection** from ordinary
request withdrawal, communication loss, downstream Brake rejection, and actuator
failure.

## 13. Bottom line

US20230166772A1 changes the most useful question from:

> "Which native command do we have to block?"

to:

> "How does the FRC application decide which simultaneously enabled TSS feature
> owns the generic request, and how does it represent intentional non-selection
> to the losing feature?"

The patent supplies Toyota's vocabulary for that kind of eligibility/priority
state machine. The exact Camry supplies the placement: LTA/LDA/LCA/PDA/PCS are
FRC-resident applications; feature-local recorder objects precede the generic
`5282` request; protected `0x08A` is the first external egress of the selected
request; Brake-owned `0x081` is downstream result/status.

What remains unrecovered is the **FRC application implementation** of that
selection: the exact state variables, priority/inhibition rules, transition
functions, and any internal intentional-rejection feedback. We should not keep
searching for a separate external lateral-client arbitration control plane at
Brake unless new evidence requires one.
