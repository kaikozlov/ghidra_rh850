# Toyota selected-ID / direct-request arbitration architecture

**Source:** Toyota US20200070873A1, *Vehicle Control System*, priority
2018-08-29, published 2020-03-05.

**Status:** external-source architecture analysis joined conservatively to the
current TSS3 evidence. The retained source PDF is local-only at
`REFERENCE/patents/US20200070873A1.pdf`.

This patent is a close contemporary of US20200070849A1 but it solves a
different problem. US20200070849A1 describes the logical Vehicle Movement
Manager split into application request, arbitration/result, and
post-arbitration controller instruction layers. US20200070873A1 describes a
latency-optimized physical realization in which the actuator can receive the
application request stream directly and the manager can arbitrate primarily by
selecting **which application stream the actuator should currently follow**.

That distinction is important. The patent is not evidence that the exact Camry
F33 EPS receives `0x08A`, and it is not a reason to reinterpret Brake/VMM
`0x081` as an EPS selector. Exact F33 receives neither `0x08A` nor
`0x081`; its recovered external target-bearing steering ingress remains B6.
The value of this patent is that it exposes Toyota's alternate **data-plane +
selection-plane** architecture and several timing/freshness rules that can be
searched for on other Toyota boundaries.

## 1. The problem Toyota is solving

The conventional architecture described as the comparative example is:

~~~text
driving-assistance application
        |
        | request value
        v
movement manager
        |
        | arbitration
        | selected request value
        v
actuator controller
~~~

That costs:

~~~text
application -> manager network delay       t1
manager arbitration processing             t2
manager -> actuator network delay           t3
------------------------------------------------
age of the request value at the actuator   t1+t2+t3
~~~

The patent's embodiment separates **authority selection** from **request-value
transport**:

~~~text
                 request(id, value)
application -------------------------------> actuator
     |                                           ^
     | request(id, value)                        |
     v                                           |
movement manager                                 |
     |                                           |
     +---------- control(selected id) -----------+
~~~

The manager still sees the request streams and decides which application wins,
but the actuator does not need the manager to relay every selected request
sample.

This is not "arbitration disappears." Initial control still waits for the
manager's selection result. What changes is the **age of the request sample
used after the grant**: once a source is selected, the actuator can consume a
newer direct request sample with only one network-hop delay.

## 2. There are two independent identifiers

Paragraphs 28 and 35-39 make a distinction that matters directly to TSS3
reverse engineering.

Every CAN signal already has a **CAN_ID** that can identify the sending device.
Separately, each application request contains an **identifier `id` of the
driving-assistance device/application**. The patent explicitly says this
application identifier is attached separately from CAN_ID and may have a
different value.

Therefore:

- the arbitration/request ID is payload-level policy metadata;
- it is not a CAN arbitration identifier;
- several application IDs can logically share one ECU/network transmitter;
- one application identity can survive repacking, gatewaying, or a change in
  CAN ID;
- a numeric request ID such as Toyota's TSS IDs must not be interpreted by
  comparing it to a CAN identifier.

This is independent support for treating the GTS `5280/5281/5282` and
`5284/5285` IDs as application identities rather than bus addresses.

## 3. Figure 2 is a grant/stream-selection protocol, not packet forwarding

Figure 2 is the most important part of the patent.

The sequence is:

1. application 1 publishes `(id=1, request=delta_11)`;
2. application 2 publishes `(id=2, request=delta_21)`;
3. the movement manager receives those samples and selects one source;
4. the manager sends a **control signal containing at least the selected ID**;
5. **after that control signal**, both applications publish newer samples
   `delta_12` and `delta_22`;
6. the actuator chooses the latest post-control-signal request whose application
   ID matches the selected ID;
7. the actuator uses that newer request value.

The request sample that caused the manager to choose a source is therefore
allowed to be **different from the request sample the actuator actually
executes**.

That is much stronger than the shorthand "manager sends the winner ID." A useful
RE interpretation is that the selected ID behaves like a source grant over
subsequent request samples; **grant/lease is our shorthand, not Toyota patent
terminology**. Once the manager chooses an application stream, the actuator
follows a later sample from that stream.

The patent is explicit that if the actuator cannot obtain a request with the
selected ID **after** receiving the control signal, steering need not be
executed.

### Consequence for reverse engineering

A Toyota interface implementing this design should expose two logically
different things:

~~~text
request stream:
    application ID + continuously refreshed request value

selection stream:
    currently admitted application ID
~~~

A request value existing on the network is not enough. It becomes actionable
only when the selection state names the same application.

Likewise, the exact sample used for arbitration is not necessarily the exact
sample used for actuation. Correlating one manager-side sample to one
actuator-side sample byte-for-byte can therefore fail even when the architecture
is working exactly as intended.

## 4. The manager control signal may still contain an old request value

Paragraph 45 says the manager control signal needs to contain **at least** the
selected identifier, and gives an example where the selected request signal can
also be attached to the control signal.

Figure 2 shows exactly this: the control signal can carry the old selected
sample `delta_11` or `delta_21`, but after the grant the actuator later uses
`delta_12` or `delta_22` received directly from the selected application.

This creates a subtle but important diagnostic rule:

> Seeing a physical value inside a manager-to-actuator control PDU does not by
> itself prove that this value is the actuator's live command sample.

On an implementation matching this patent, that value can be an
arbitration-time snapshot while the actuator actually follows a newer
application-side request.

The exact F33 B6 path does **not** currently fit this pattern: F33 has no
recovered separate direct TSS request stream and consumes B6's target fields as
its external target-bearing cooperative-control input. This patent therefore
must not be used to demote B6 into an ID-only selector on F33.

## 5. The freshness rule is relative to the selector event

The claim is more specific than "use the latest matching request."

The actuator selects the latest matching request **among request signals
acquired after acquisition of the control signal**.

That ordering prevents a newly selected source from immediately actuating an
arbitrarily old cached request.

Conceptually:

~~~text
old request from A
old request from B
       |
       | manager says "B wins"
       v
control(selected=B)
       |
       +-- old cached B request is not the intended sample
       |
new request from A
new request from B  <---- first eligible B sample
       |
       v
actuate from new B request
~~~

This is a freshness/admission rule even though the patent does not discuss
SecOC freshness counters. The freshness is **protocol ordering**, not
cryptographic freshness.

Do not infer from this patent:

- a particular timeout;
- a modulo counter;
- a SecOC freshness value;
- a MAC;
- a failure code when a selected request is missing.

Those mechanisms are outside this disclosure.

## 6. The latency claim is narrower than "the manager is bypassed"

Figures 4A-4D make the timing point precisely.

The actuator cannot begin the new application's control until the manager's
control signal arrives, so **control start** is still delayed by
`t1+t2+t3`.

But once the selection exists, the direct request value available at the
actuator is only `t1` old. In Figure 4C the direct request curve is the fresh
solid line and the manager-relayed value is the older dotted line. The heavy
portion shows the actuator starting late, after the selection arrives, but then
using the fresh direct-request trajectory.

Toyota's claimed advantage is therefore:

- not lower initial arbitration/grant latency;
- lower **request-sample age** after the source has been admitted;
- consequently less dead time in the actuator feedback loop and potentially
  higher usable control gain.

That is why paragraph 87 says the architecture is particularly useful for
steering, where response performance matters more than for ordinary
longitudinal force control.

## 7. Source switches create a discontinuity problem

The direct-request architecture has a natural transition hazard.

By the time the manager's grant arrives, the selected application's request may
have advanced substantially beyond the actuator's pre-grant state. Figure 5A
shows the resulting step/discontinuity.

The patent explicitly places the mitigation in the **actuator controller**.
Examples include:

- limiting the gradient/rate of change;
- gradually bringing the actuator control value toward the request;
- following the request with a time offset and shrinking the offset;
- storing the recent request history and replaying/compressing its shape to
  join the current request smoothly.

This is useful RE vocabulary. A source-selection edge can legitimately produce
an actuator-side ramp even if the upstream request jumps immediately. That ramp
does not necessarily mean the request itself was filtered upstream.

The patent does not specify exact gradients, time constants, or steering-angle
limits.

## 8. The architecture is explicitly allowed to be mixed by actuator

Paragraph 87 says the embodiment is especially useful for lateral/steering, but
may also be applied to braking or drive power. It also explicitly allows the
patented direct-request architecture to be used for only **part** of the
vehicle's actuators while the conventional manager-forwarded architecture is
used for others.

This matters for Toyota because a single vehicle need not have one universal
transport pattern:

~~~text
steering:       direct request + selected-source control
braking:        manager-generated/forwarded request
drive power:    manager-generated/forwarded request
~~~

or another combination can exist.

Therefore a direct-selector finding on one axis must not automatically be
projected onto longitudinal or onto another vehicle generation.

## 9. The manager may be integrated with an actuator ECU

Paragraph 88 says the movement manager may be integrated with any actuator
control device. When it is integrated, there is no inter-ECU network delay
between the manager and that actuator, so the latency advantage of this patent
largely disappears for that local actuator and either architecture may be used.

This fits naturally with the broader Toyota/ADVICS portfolio where the
Vehicle Movement Manager is hosted in the Brake/Skid domain:

~~~text
                    +-----------------------------+
applications ------>| Brake ECU / movement manager|
                    |     local brake control      |
                    +-----------------------------+
                           |
                           | network
                           v
                          EPS
~~~

For a Brake-hosted manager, there is little reason to optimize the local brake
path using a direct-request bypass, while a remote high-bandwidth steering
actuator is exactly where the selected-ID/direct-request pattern could be
attractive.

That is an architectural compatibility statement, not proof that exact F33
uses this steering realization.

## 10. Exact Camry F33: what matches and what does not

The current Camry evidence establishes the observable loop as:

~~~text
FRC assembly
    |
    | protected 0x08A request-side TSS package
    v
Brake / Vehicle Movement Manager domain
    |
    | request arbitration
    |
    +---- protected 0x081 arbitration result/status ----> FRC
    |
    +---- post-arbitration request generation
               |
               +---- B6 final steering target ----------> exact F33 EPS
~~~

Exact F33's recovered receive surface accepts B6/profile2 but excludes both
`0x08A` and `0x081`.

That is decisive for the interpretation of this patent.

### What matches

- payload-level application IDs distinct from CAN IDs;
- simultaneous/overlapping assistance applications;
- arbitration based on vehicle state, priority, and request content;
- steering as a high-response actuator where latency matters;
- manager placement potentially inside another actuator ECU;
- an actuator-side smooth transition when authority changes.

### What does not match the recovered F33 EPS boundary

The patent's claimed lateral embodiment requires the steering actuator
controller to receive:

1. the application request stream; and
2. the manager's selected-ID control stream.

Exact F33 has no recovered `0x08A` or `0x081` receive path. Its only recovered
external target-bearing cooperative steering ingress is B6.

Therefore the current evidence does **not** support a direct
`0x08A -> F33` request path plus a separate manager-selected-ID path, and it
specifically rejects identifying Camry `0x081` with this patent's
manager-to-actuator selector. `0x081` is Brake/VMM-owned result/status traffic
returning toward the TSS applications, and F33 does not receive it.

### B6 is not merely the selector described here

B6 contains a Target Lateral ID plus a target steering quantity, which can look
superficially like paragraph 45's manager control signal carrying both selected
ID and selected request snapshot.

But the key feature of this patent is that the actuator subsequently consumes a
**separate newer direct request**. No such external F33 request stream is
recovered.

The exact F33 firmware instead consumes the B6 target/mode fields themselves.
Thus the current F33 evidence remains much closer to US20200070849A1's
post-arbitration **steering request-generation / controller-instruction**
interface than to US20200070873A1's direct-request optimization.

## 11. What this changes in the current TSS3 model

The patent does not overturn the recovered Camry request/result/target split.
It sharpens the boundary.

### A. "Logical stage" does not imply "one physical forwarded value"

Toyota explicitly designed a system where arbitration can select **a source
stream** without relaying the final live value. A future Toyota target can
therefore implement either a direct-request + selector design or a
manager-generated target design. The architecture has to be recovered per
actuator and per platform.

### B. Application ID can be authority, not merely telemetry

A selected ID can operate as a persistent authority/grant over subsequent
samples. That gives stronger meaning to Toyota's request/result ID surfaces:
the ID can define **whose stream is admissible**, while the continuously
changing physical value is transported separately.

This is relevant when interpreting source suppression and source replacement.
Injecting a correct-looking request with a valid ID is not enough in an
implementation matching this patent unless the manager also selects that ID.

### C. The grant/sample ordering is a testable discriminator

For any candidate platform suspected of using this architecture, the strongest
dynamic signature would be:

1. source A/B both publish continuously;
2. manager selection changes from A to B;
3. the actuator does **not** use an old cached B value;
4. the first post-selection B request becomes actionable;
5. subsequent B request samples affect the actuator without waiting for their
   exact values to be relayed by the manager.

That timing signature is much stronger than merely observing two frames with
matching IDs.

## 12. Practical search/RE checklist

For another TSS3 target, or for matched Brake/FRC firmware, search for the
following structure before assuming a request-generation design.

### Wire / COM

Look for:

- a cyclic request PDU carrying an application ID plus steering/curvature
  request;
- a second PDU carrying a selected/current application ID;
- both PDUs received by the same actuator controller;
- selection changes that gate which request stream affects the actuator;
- a post-selection freshness rule: only request samples newer than the selector
  event become eligible.

### Firmware

High-value code shape:

~~~c
on_selection(selected_id):
    selected = selected_id;
    selection_epoch++;

on_request(app_id, value):
    if (app_id == selected && request_is_after_selection_epoch):
        accepted_target = value;
~~~

The actual implementation need not literally use an epoch counter, but a
selector state plus a freshness/order check should exist.

### Transition control

At a source switch, search for:

- rate/gradient limiting;
- target catch-up;
- state reset on selected-ID change;
- request-history replay/interpolation;
- a "no matching request after grant" no-control/fallback path.

### GTS vocabulary

Current GTS provides strong generic target-side vocabulary such as
`Target Lateral ID` on EMPS. A search for the patent's generic words
`request signal` and `control signal` produces many unrelated systems and
does not currently identify an exact F33 DID representing this patent's
selector. Treat the architectural match as a code/wire-shape question rather
than expecting the patent's generic names to appear verbatim in diagnostics.

## 13. Relationship to US20200070849A1

These patents are better read as two contemporaneous architecture branches,
not as one superseding the other.

US20200070849A1 centralizes the post-arbitration actuator target:

~~~text
application request
    -> request arbitration
    -> request generation
    -> controller-specific target
    -> actuator controller
~~~

US20200070873A1 separates request data from source selection:

~~~text
application request --------------------------> actuator controller
       |
       +-> movement manager -> selected ID ----^
~~~

Toyota filed the Japanese priorities one day apart (2018-08-29 vs 2018-08-30).
That timing is consistent with a coordinated architecture portfolio covering
multiple physical realizations rather than a later correction to the VMM model.

For exact F33 lateral control, the current evidence favors the
US20200070849A1-style request-generation/controller-instruction boundary.
US20200070873A1 remains highly valuable for:

- interpreting application IDs;
- recognizing selected-source/grant designs on other targets;
- avoiding the assumption that arbitration requires forwarding each exact
  request sample;
- designing timing experiments that distinguish a selector plane from a target
  plane.

## 14. Evidence boundary

**Patent-proved external-source facts:**

- application ID is distinct from CAN_ID and can differ numerically;
- the manager can arbitrate by selected application ID;
- the actuator can receive the requests independently of the manager;
- the actuator can use a request generated *after* the arbitration sample;
- selection can depend on vehicle state, application priority, or request
  content;
- EPS/lateral control is explicitly claimed;
- actuator-side smoothing is explicitly allowed;
- mixed per-actuator realization and manager/actuator integration are
  explicitly allowed.

**Exact-Camry facts from current repository evidence:**

- `0x08A` is the FRC-side request publication toward Brake/VMM;
- `0x081` is Brake/VMM result/status back toward FRC;
- exact F33 receives neither `0x08A` nor `0x081`;
- exact F33 receives native B6/profile2 and B6 carries the recovered external
  target-bearing steering interface.

**Still open:**

- exact Brake firmware implementation of arbitration/request generation;
- whether any hidden/private TSS3 boundary uses a direct-request + selector
  pattern internally;
- which other TSS3 platforms use this patent's claimed EPS realization;
- exact selected-ID handoff semantics on those platforms.

The principal correction is therefore: **this patent is a strong Toyota
architecture clue, but it is not a direct physical map of the Camry
`0x08A/0x081/B6` chain.**
