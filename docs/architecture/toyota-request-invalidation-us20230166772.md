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
| manager latches policy until cancel | explicit | not yet mapped | **unknown** |
| client excluded inside arbitration | explicit | consistent with result/rejection records | exact F33 implementation unknown |
| arbitration result ID | explicit VMM-family concept | 0x20D4 byte25 vertical result | **recovered** 5284/5285 |
| result physical value | explicit VMM-family concept | successor data exists | **recovered** 57DB/57DE |
| rejection reason/factors | explicit semantic concept | **recovered** longitudinal P6 RoB fields | not mapped |
| manager -> suppressed-client intentional-rejection feedback | **explicit** | no exact directional join yet | **not recovered** |

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

### Strong hypothesis: look for an eligibility/priority control plane

The next search target should be a mechanism that changes **which application
ID can win** while leaving:

- FRC publication alive;
- Brake/VMM result/status publication alive;
- the other native applications alive;
- EPS/Brake communication healthy.

Possible realizations, ordered only by conceptual fit rather than confidence,
include:

- a priority field already carried alongside a request;
- a manager state transition or application-mode command;
- a source-specific eligibility/invalidity flag;
- an internal native application handoff that can be reproduced through an
  existing control interface.

The patent specifically warns us not to demand a signal literally named
"invalidation": priority is an equivalent claimed realization.

### Separate question: what keeps the losing client healthy?

Even if we find the policy input, the patent says the suppressed client may
need an explanation for repeated non-selection.

For F33 the current result/status candidates remain:

- arbitration result IDs `5284/5285`;
- selected/result quantities `57DB/57DE`;
- Brake-owned `0x081` result/status publication;
- any as-yet-unresolved source-specific rejection/eligibility status.

But there is currently **no proof** that `0x081` contains the patent's arrow-B
feedback. Its established result-ID and fail-class candidates are not
automatically "request rejection information."

## 11. Smallest discriminating experiments/searches

The patent suggests better experiments than another all-or-nothing source
block.

### A. Observe native transitions where one client legitimately loses

Collect synchronized Operation FFD / raw CAN around native state transitions
that change eligibility without an ECU outage:

- LTA on -> off;
- LCA request -> reject/cancel;
- LTA <-> LDA interaction;
- DRCC set/cancel;
- PDA intervention where safely reproducible;
- driver override.

Correlate request IDs, result IDs, and result values:

```text
5280/5281/5282 request IDs
      |
      v
priority / eligibility clues
      |
      v
5284/5285 result IDs
      |
      v
57DB/57DE result values
      |
      v
raw 0x081 / final target plane
```

The key signature is a requester that **continues to exist** while its result ID
loses, with no fault transition.

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

### C. Treat arrow A and arrow B as separate recovery problems

Do not infer one from the other.

**Arrow A question:** what input tells the manager a client is no longer
eligible or lower priority?

**Arrow B question:** what result/status tells the client that repeated
non-selection is intentional rather than a broken actuator/manager?

A clean takeover may need both; the wire realization may combine them with
already-existing application/result IDs rather than expose two obviously named
signals.

### D. Look for a latched transition

If a candidate policy command is found, determine whether it is:

- continuously sampled;
- edge-triggered / one-shot;
- latched until explicit cancellation;
- automatically cleared by mode/ignition/fault.

The patent's Figure-4/Figure-5 design specifically predicts a **set/cancel
latch**.

## 12. Bottom line

US20230166772A1 changes the most useful question from:

> "Which native command do we have to block?"

to:

> "How does Toyota intentionally make one application ineligible while keeping
> the request/result contract healthy?"

The disclosed answer is a separate arbitration-policy path plus explicit
client-facing non-selection information. Exact F33 already shows enough of the
surrounding abstraction—application request IDs, priority metadata,
arbitration-result IDs, selected quantities, and a result/status publication—
that this is a credible search model.

What remains unproved is precisely the useful part: whether P5/F33 exposes an
input equivalent to the patent's invalidation/priority request and, if so,
where the corresponding healthy-rejection feedback is encoded.
