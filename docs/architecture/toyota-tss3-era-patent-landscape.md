# Toyota TSS3-era patent landscape (2019-2026)

**Status:** external-source architecture/research index, researched 2026-09-18.

This note catalogs Toyota and Toyota-affiliated patent families published in the
TSS3 development/deployment era that expose useful architecture vocabulary for
the current reverse-engineering work. It is intentionally narrower than a
general ADAS patent survey: entries are included only when they disclose a
control, network, failure, steering, security, or driver-monitoring mechanism
that maps to an existing TSS3 question.

The original high-value architecture source remains Toyota
**US20200070849A1, "Information Processing Apparatus"** (priority 2018-08-30,
published 2020-03-05), already analyzed in
[toyota-tss3-vehicle-movement-arbitration.md](toyota-tss3-vehicle-movement-arbitration.md).

## Evidence boundary

A patent proves that Toyota or a co-assignee disclosed a design and provides
Toyota-authored terminology. It does **not** prove that the exact 2026 Camry F33
implements that embodiment, assigns its blocks to the same ECUs, uses the same
wire encoding, or uses the example numeric values shown in a figure.

Accordingly:

- a semantic match to exact GTS terminology is a strong search oracle, not an
  automatic CAN-field rename;
- a later patent can explain Toyota architecture vocabulary without proving
  that an earlier TSS3 calibration implements the later mechanism;
- example priorities, bit widths, enum values, and state codes remain examples
  until joined to exact firmware, GTS, or dynamic evidence;
- co-assignee patents from ADVICS, JTEKT, and Denso are included where the
  disclosed subsystem is directly relevant.

## 1. Highest-value control/arbitration families

| Publication / family | Priority | Assignee | Disclosed mechanism | Current TSS3 use |
|---|---:|---|---|---|
| **US20230082947A1**, Motion manager, vehicle, vehicle control method... | 2021-09-15 | Toyota | Actuator systems report reliability to the motion manager; steering state includes reliability, driver grip, steering torque and steering-wheel angle. The manager generates named fail classes, including **lateral control system fail class**, with semantic states normal / protective-control / abnormal-but-not-confirmed-and-invalid / confirmed failure. Additional failure information can describe influenced vehicle-speed range, malfunctioning portion, and operation mode; a malfunctioning portion can be inter-actuator communication. | Exceptional semantic hit for GTS recorder **5283_1 Lateral control system fail class status** and the current X2400 investigation. Gives companion vocabulary to search in GTS and a state model to test dynamically without assuming numeric encodings. |
| **US20220219711A1 / US12071145B2**, Control device for vehicle, manager... | 2021-01-14 | Toyota + ADVICS | ADAS applications send **application IDs** with kinematic requests; priority is stored by application ID and may change with vehicle, driver, or availability state. Explicit examples include PCS, ACC, LKA/LTA, AEB, LDA and steering guidance. EPS is an example actuator for a steered-angle request. | Strong follow-on support that Toyota TSS request/result IDs are IDs of software applications/clients rather than CAN identifiers. Useful for interpreting 5280/5281/5282 and 5284/5285. |
| **US20200070873A1 / US11643089B2**, Vehicle control system | 2018-08-29; pub. 2020 | Toyota | Applications put request values plus payload-level application IDs directly on the network; the patent explicitly distinguishes those IDs from `CAN_ID`. The manager selects an application ID, while the actuator waits for the selection and then consumes the **newest matching request received after that selection event**. The arbitration sample and the actuated sample may therefore be different. Claim 4 explicitly covers EPS/lateral motion. | Critical alternative physical realization: arbitration can be a selected-source plane separate from the request-value data plane. Exact F33 does **not** instantiate the claimed direct-request EPS boundary on its recovered external CAN surface because it receives neither `0x08A` nor `0x081`; B6 remains its recovered target-bearing ingress. See the dedicated close read. |
| **US20200070802A1 / US11161496B2 / US12005882B2**, Control device | 2018-08-30; pub. 2020 | Toyota | Brake control ECU contains request arbitration, command distribution, feedback control, and optionally vehicle-motion control. It feeds measured **control record values** and summarized actuator operation/soundness information back to requesting applications; direct wheel-speed inputs and preferential stability control are explicit. | Reinforces Brake/VMM ownership and gives a reason for the rich result/status plane: applications need realized motion plus actuator soundness, not only the selected request. |
| **US20200094835A1 / US11285952B2 / JP7067386B2**, Braking and driving force control device | 2018-09-21; pub. 2020 | Toyota | Defines the driving device's lower limit of available braking/driving force as the fully-closed baseline. At speed that floor can represent engine-braking/deceleration; below roughly 8--10 km/h, **creep torque becomes dominant and raises the lower limit into positive driving force**. The controller changes filtering/feedback so this low-speed creep transition is reflected promptly. | Strong physical semantic corroboration for the Camry `0x08A` idle lower package: ID4's acceleration is positive near zero speed, declines through zero with speed, and is reduced by low-speed brake input. This does not expose numeric request ID4, but supports a **closed-accelerator baseline / creep-coast lower-bound** attribution rather than `ID4 = creep` as a literal enum name. |
| **US20220315018A1 / US12280788B2**, Control apparatus, manager... | 2021-04-06 | Toyota + ADVICS | Applications supply information about whether a kinematic plan remains an **arbitration target**. A request that is about to terminate can be excluded or handled specially so a new request is not delayed. | Concrete vocabulary for handoff/disengagement and source-suppression RE: search for arbitration-target, termination, low-priority, degeneration and handoff state rather than modeling every request as simply present/absent. |
| **US20230166772A1 / US12534110B2**, Motion manager, autonomous driving apparatus... | 2021-11-30 | Toyota | A manager can intentionally invalidate a PCS/other ADAS request and return **request rejection information** so the suppressed application does not diagnose an abnormal condition merely because its plan is not selected. The disclosed invalidation target can also be AEB, ACC, ASL, or another application. | High-value vocabulary for the **downstream VMM arbitration-policy boundary**: a still-present request can be intentionally excluded/de-prioritized after reception, with explicit feedback toward the requester. On exact Camry this is conceptually downstream of FRC `0x08A` egress; do not conflate it with the separate FRC-internal feature-owner state machine. |
| **US20220274616A1 / US12060069B2**, Manager, control method... | 2021-03-01 | Toyota + ADVICS | Manager accepts application IDs plus kinematic plans and outputs the motion request to an actuator system **corresponding to the application ID**, preventing an inappropriate actuator from being used for an unexpected application request. | Supports treating application ID as policy/routing metadata, not merely a display label. |
| **US11780500B2**, Control device, manager, method... | 2020-02-05 | Toyota | Manager converts/arbitrates requests and sends **actual steering angle** back to the driver-assistance system. | Useful for the 0x081/result-plane interpretation and for distinguishing requested pinion angle, selected target, and realized steering state. |
| **US11834037B2**, Control device, method... | 2020-03-18 | Toyota | Manager distributes converted motion requests and returns steering-actuator **middle-point / neutral-point** information to applications; updates are coordinated so clients do not disagree across handoffs. | Search oracle for steering center/middle-point synchronization, calibration, and discontinuity handling. |
| **US20240101086A1 / US12344222B2**, Motion manager, control device of brake device... | 2022-09-27 | Toyota + ADVICS | Explicit later topology has ADAS applications, engine ECU, steering ECU and a **brake ECU containing the motion manager**. The manager converts normalized motion requests into actuator-type-specific instruction values using stored actuator type information. | Later-generation confirmation of the brake-hosted VMM/request-generation model and useful vocabulary for the transformation between application requests and actuator-specific targets. |
| **US20240262354A1 / US12311936B2**, Vehicle motion manager... | 2023-02-07 | Toyota + ADVICS | Failure information plus application ID selects whether a request requires **degeneration**; the manager can replace a request with a time-varying value that approaches an end value, with degeneration state/status returned to the commanding ECU. | Later-generation clue for graceful failover/fade-out behavior. Search logs/GTS for degeneration-like ramps at application failure/disengagement, but do not project its exact longitudinal algorithm onto F33. |

Public sources:

- https://patents.google.com/patent/US20230082947A1/en
- https://patents.google.com/patent/US20220219711A1/en
- https://patents.google.com/patent/US20200070873A1/en
- https://patents.google.com/patent/US20200070802A1/en
- https://patents.google.com/patent/US11285952B2/en
- https://patents.google.com/patent/US20220315018A1/en
- https://patents.google.com/patent/US20230166772A1/en
- https://patents.google.com/patent/US20220274616A1/en
- https://patents.google.com/patent/US11780500B2/en
- https://patents.google.com/patent/US11834037B2/en
- https://patents.google.com/patent/US20240101086A1/en
- https://patents.google.com/patent/US20240262354A1/en

## 2. Exact joins to the current Camry/GTS work

### 2.1 GTS 5283 is no longer an isolated string

The current TSS3 recorder exposes:

- 5283_1 = Lateral control system fail class status;
- 5283_2/_3 = drivetrain fail-class convenience/safety;
- 5283_4..7 = autonomous-brake main/sub convenience/safety;
- 5283_8 = parking-brake fail class;
- 5283_9 = driver-brake fail class;
- 5283_10 = stand-still-control fail class.

US20230082947A1 independently describes a Toyota motion-manager fail-class
structure with a **lateral control system fail class**, driver-brake-input fail
class, autonomous-braking main/sub fail classes, driving-system fail class, and
shift-control fail class. Its lateral class represents four semantic states:

1. normal;
2. protective control / restricted operation;
3. abnormality detected but failure not confirmed, with control invalid;
4. confirmed failure.

The close reading materially sharpens the architecture. Raw actuator
reliability and application-facing fail class are **different interfaces**.
Powertrain/brake/steering send `ACL2`/`BRK2`/`STR2` state to the motion manager;
`STR2` explicitly includes steering-system reliability, driver grip,
steering-wheel operating torque, and steering-wheel angle. The motion manager's
generation unit then synthesizes `PLN2` back to the driver-assistance
applications, including the fail classes. In other words, the lateral fail
class is manager-produced application status, not simply a raw EPS diagnostic
bit.

For steering reliability the embodiment distinguishes four semantic states:
normal, protective control, abnormality detected but failure not yet confirmed
with control invalid, and confirmed failure. The patent allows a two-bit
numerical representation but does **not** assign those four meanings to
particular `00/01/10/11` values. Current TSS3 GTS stores `5283_1` as an 8-bit
recorder item, so the exact F33 encoding still requires a wire/recorder join.

There is, however, an important independent Toyota diagnostic clue:
`DRS_P5.ddb` DID `0x100A` **DRS Fail Class** is an 8-bit diagnostic field whose
valid values are only `0..3` and whose display mapping is `0 = Steering control
request is executable`, `1 = Reserved`, `2 = Steering control request is not
executable (temporary)`, `3 = Steering control request is not executable (with
failure decided)`. The same `0..3` mapping survives in rear-steering P6/P6F.
That does not prove the F33 lateral fail-class encoding, but it gives strong
Toyota-family evidence that values `2` and `3` mean temporary invalidity versus
confirmed failure.

The same patent says the information for setting application behavior after an
abnormality can include **influenced vehicle velocity range**,
**malfunctioning portion**, and **operation mode after the abnormality**. The
example malfunctioning-portion namespace explicitly includes communication
between powertrain and brake and communication between steering and brake. This
is directly relevant to the EPS outage -> Brake/FRC X2400 path and makes
inter-actuator communication failure a first-class candidate cause rather than
a side effect.

The current `0x081` evidence now supports a stronger, still-unproved packing
hypothesis. `B13[5:0]` is already joined to `5285` arbitration-result lateral
ID; healthy traffic uses `00`/`0B` with only rare `80`, while dead-EPS and
post-bootstrap faulted traffic progresses to or remains at `C0`. A compact
interpretation consistent with both the patent and the independent DRS enum is
therefore **`B13[7:6]` as a two-bit lateral fail-class candidate**, with `10`
matching a temporary/not-executable state and `11` matching
failure-decided/confirmed. `01` would remain an unresolved protective/degraded
state if F33 uses it. This is a hypothesis, not a rename: it must be joined
against `5283_1` or an exact decoder before being promoted to wire truth.

### 2.2 Request/result IDs really are first-class application identifiers

The original US20200070849A1 already says the request IDs identify
applications. US20220219711A1 is a direct follow-on to JP2020-032894 and makes
the identity/priority split much more explicit:

- each driving-assistance application emits its **kinematic-plan request plus a
  preset application ID that uniquely identifies the requesting application**
  (paragraph 23);
- a single ECU may host multiple applications -- the patent explicitly gives
  ACC, LKA and AEB in one ADAS ECU as an example (paragraph 24);
- the manager (`ADAS-MGR`, `Vehicle-MGR`, etc.) receives both the request and
  the application ID, looks the ID up in a separately stored priority table,
  and arbitrates from that result (paragraphs 25-31);
- application priority can change with vehicle state, driver state or
  availability without changing the application identity (paragraph 30,
  claims 1/5);
- the embodiment is primarily lateral and names a steered-angle request with
  EPS as the actuator, but the patent expressly extends the same priority
  scheme to longitudinal-acceleration and shift-position arbitration
  (paragraphs 42-44).

The figures make one critical boundary visually explicit: **application ID and
priority level are different columns/namespaces**. Figure 2 assigns priority
levels 1..11 while leaving the application-ID column undisclosed. Figure 5 then
changes parking/autonomous-driving priorities while the application identities
remain conceptually the same. Therefore an observed Toyota ID value must never
be read as an ordinal priority.

That matters because current GTS+ independently supplies the numeric
generation-20 `EMPS_P5 0x1CEE Target Lateral ID` dictionary. Its labels line
up unusually well with the patent's Figure-2 application set even though the
patent itself does not reveal the numeric IDs:

| Patent application/function | GTS Target Lateral ID | Join |
|---|---:|---|
| collision avoidance assistance (the text explicitly gives PCS as the example) | `1 = PCS` | direct semantic match |
| autonomous driving Lv.4, AD | `41 = AD (Lv.4)` | exact label/function match |
| autonomous driving Lv.4, EM | `43 = EM (Lv.4)` | exact label/function match |
| autonomous driving Lv.3, AD | `35 = AD (Lv.3)` | exact label/function match |
| autonomous driving Lv.3, EM | `37 = EM (Lv.3)` | exact label/function match |
| automatic parking | `25 = AP`, `27 = Remote Parking` | direct family match; GTS splits variants |
| lane deviation warning / LDA | `4 = LDA` | direct acronym/semantic match |
| lane keeping assistance / LKA-LTA | `10 = Hands Off LTA`, `11 = LTA/LCA` | direct family match; GTS splits modes |
| pedestrian risk avoidance | `19 = PDA` | strong functional candidate, abbreviation not expanded by this patent |
| steering-wheel operation guidance | `18 = SDG` | strong role candidate, acronym not expanded by this patent |
| self-traveling transport | `49 = Self-Propelled Transport` | near-literal translation match |

The remaining exact GTS values (`13/15` DESA modes, `39/45` DES modes,
`63` Driver Operation and `0` No Request) are extensions/sentinels not
enumerated in the patent's example priority table.

The crosswalk is more important than any one label. The patent's priority order
puts Lv.4 **EM before AD**, while GTS uses IDs `43` and `41`; it puts Lv.3
**EM before AD**, while GTS uses `37` and `35`; LDA is priority 7 but GTS
ID 4. So numeric ID ordering demonstrably does not encode priority. Toyota's
actual implementation is much more naturally modeled as:

```text
preset application identity
        |
        v
{ application ID, kinematic request }
        |
        v
manager lookup: application ID -> current priority/policy
        |
        v
arbitration
```

This also explains why the six-bit Camry wire field is so compelling. GTS
defines the target-ID range as `0..63`, the current Camry `0x08A B21[5:0]`
carries values such as `11 = LTA/LCA` and `18 = SDG`, and the returning
`0x081 B13[5:0]` is already joined to the arbitration-result lateral ID. The
patent does not specify a six-bit wire encoding, but the semantic model, exact
GTS range and observed wire width now triangulate cleanly.

A second useful nuance is that Toyota's "application" is not synonymous with an
ECU or necessarily with one user-facing feature. The patent allows several
applications in one ECU and separately prioritizes multiple functions of an
autonomous-driving application (EM versus AD). The GTS dictionary's distinct
Lv.3/Lv.4 AD/EM/DES IDs are strongly consistent with that finer-grained
arbitration-client model.

The patent's arbitration policy is also not simply "smallest ID wins" or even
"highest static priority always wins." Figure 3 first groups functions by
safety/operational role, then breaks conflicts by control-range velocity and
safety phase; for one application with multiple functions it uses safety
response and controllability. Paragraph 39 additionally permits ASIL to guide
priority. Applied Example 2 shows longitudinal arbitration where the physical
request value (minimum requested acceleration) is primary and application
priority can stabilize selection when candidate accelerations are nearly equal.
That is a useful model for the current `5280/5281` upper/lower-bound work:
application identity is policy metadata layered on top of the kinematic
request, not a replacement for request-value arbitration itself.

That strengthens the working semantic join:

| GTS / wire surface | Best current interpretation |
|---|---|
| 5280_1, 5281_1 | longitudinal application/request IDs |
| 5282_1 | lateral application/request ID |
| 5284, 5285 | longitudinal/lateral arbitration-result application IDs |
| 57DB, 57DE | realized/selected result quantities |
| 0x08A | request-side TSS package |
| 0x081 | result/status package |
| B6 / EMPS target surface | post-arbitration steering-controller target/instruction |

The patent still does **not** disclose Toyota's numeric application-ID table.
The numeric mapping above comes from current GTS+ and dynamic Camry evidence,
not from US20220219711A1 itself.

#### Retained Camry logs show the FRC-internal application handoff on egress

A re-check against the retained road corpus makes this patent materially more
useful than a static naming crosswalk. The existing 12-route / 513-segment
lateral-family reduction contains **1,219,584 native `0x08A` request frames**:

- `512,847` ID0 (No Request);
- `653,586` ID11 (LTA/LCA);
- `52,853` ID18 (SDG);
- `298` ID4 (LDA).

Across those routes there are **473 request-ID transitions**. The directed
transition graph is not random:

| request transition | count |
|---|---:|
| `0 -> 11` | 136 |
| `11 -> 0` | 164 |
| `0 -> 18` | 81 |
| `18 -> 0` | 52 |
| **`18 -> 11`** | **28** |
| **`11 -> 18`** | **0** |
| **`11 -> 4`** | **2** |
| **`18 -> 4`** | **1** |
| `4 -> 11` | 2 |
| `4 -> 0` | 4 |
| `0 -> 4` | 3 |

The shape is strikingly consistent with an **FRC-internal feature priority/
eligibility state machine**: LDA/lane-deviation can temporarily replace LTA,
and LTA can replace SDG/PDA-SA when its operating conditions become active.
Toyota's follow-on patent supplies useful priority terminology, but these edges
are not Brake choosing among separate network clients. LTA, LDA, LCA,
PDA/SDG and PCS are functions inside the FRC application, and `0x08A` is the
external expression of whichever FRC lateral function currently owns the
generic request.

The downstream arbitration-result plane independently shows that these are real
request/result handoffs rather than display-only ID changes. Across **1,016,141**
`0x081` samples paired with a fresh `0x08A` request, **1,015,978 (99.9839589%)**
carry the same lateral ID. All **163** mismatches are transition-shaped: every
`(new request ID -> old result ID)` mismatch has the reverse edge in the actual
request-transition graph. No retained stable interval shows the Brake/VMM result
persistently disagreeing with the current `0x08A` request. This high match rate
means the FRC request usually survives downstream arbitration; it does **not**
move the arbiter upstream of `0x08A`.

Three raw-log witnesses make the ordering concrete:

1. **Route 27, segment 2, 227.534515 s:** native `0x08A` changes
   `18 SDG -> 11 LTA/LCA`, simultaneously changing the cruise/request regime.
   `0x081` still reports lateral result 18 in the transition batch, reports 11
   about **30 ms** later, while its longitudinal result remains 63
   (`Driver Operation`) until about **90 ms** after the request transition and
   then becomes 11. Lateral and longitudinal employed-source state therefore
   change independently.
2. **Route 3c, segment 40, 9912.166062 s:** while cruise remains enabled at
   about 21.36 m/s with neither blinker active, `0x08A` changes
   **`11 LTA/LCA -> 4 LDA`**. `0x081` remains result 11 for the first
   post-transition sample and changes to result 4 about **40 ms** later; the
   longitudinal result remains 11. The ID4 request persists for **2.530639 s**
   and then `4 -> 11`, with `0x081` returning to 11 about **40 ms** later.
3. **Route 3e, segment 54:** an independent cruise-active witness repeats the
   same `11 -> 4 -> 11` sequence at about 33.1 m/s, with the result plane
   following in roughly **31 ms** on entry and **10 ms** on release. The LDA
   episode lasts **1.225830 s**. A separate route-3b witness shows
   `18 SDG -> 4 LDA` for a 0.280962-s request while longitudinal result remains
   63.

The two cruise-active ID4 episodes are especially useful: the ordinary cruise
state remains alive while one lateral application temporarily replaces another.
That is a much cleaner natural model for application arbitration than an
ignition, cruise-cancel, or fault transition.

The September-7 hands-off-cancel route supplies a different but complementary
handoff. Immediately before the native withdrawal, `0x08A` carries lateral
ID11 plus longitudinal request IDs 11/17. The FRC then changes lateral ID
`11 -> 0`, the longitudinal request slots to `0/4`, clears the cruise operating
latch/set speed, and does so without a physical brake/gas input or an
openpilot/native brake-cancel frame. About **20.84 ms** later `0x081` has
already moved its lateral result to 0 while the longitudinal result is still
11; about **50.64 ms** after the withdrawal the longitudinal result becomes
**63 = Driver Operation**. The `0x081` request-loss bit remains clear. This is
direct dynamic evidence that normal Toyota source withdrawal and result
handoff are distinct from request-loss supervision.

These observations sharpen the physical model:

- `0x08A` is the **FRC feature-selected generic TSS request egress**. It is not a
  bus on which separate LTA/LDA/PDA network senders compete; those applications
  coexist inside the FRC software and the FRC state machine selects which one
  populates the request before publication. That selection does **not** make
  `0x08A` the final VMM arbitration result;
- `0x08A` then enters the downstream **Brake/VMM request-arbitration unit**.
  `0x081 B13[5:0]` behaves as its arbitration-result identity with a separate
  update cadence, not as a bit-for-bit echo;
- the current exact-Camry layering is therefore FRC feature-local state -> FRC
  feature-owner selection -> generic `5282`/`0x08A` request -> Brake/VMM request
  arbitration -> `0x081` result/status + post-arbitration request generation ->
  B6 target/instruction;
- the healthy native handoff oracle is not merely physical steering response:
  an FRC request-owner change is followed by the corresponding downstream
  result-ID change while request-loss stays clear.

This suggests a concrete acceptance criterion for future non-invasive takeover
work: after an intentional request-source transition, observe whether
`0x081 B13` follows the requested application identity in the same shape as the
native `18 -> 11`, `11 -> 4`, and withdrawal transitions. Logger batching
prevents treating the observed 10-40 ms examples as an exact ECU deadline, but
a result that remains on the old ID or enters request-loss is qualitatively
different from every healthy native handoff above.

The missing discriminator is now very specific. The old road logs contain the
generic request/result planes but not synchronized Operation-FFD feature-local
objects. A future natural **ID4/LDA-over-ID11/LTA** event should capture
`5531` (LDA request), `5631` (LTA request), their enable/inhibition states,
generic `5282`, result `5285/57DE`, raw `0x08A`, and raw `0x081`. If both
features remain enabled while one feature-local request becomes preferred and
`5282`/`0x08A` changes from ID11 to ID4, that would directly expose the **FRC
application selector** rather than merely its output. The following
`5285`/`0x081` transition would then expose the *separate downstream VMM
arbitration result*. It would not mean Brake received simultaneous raw LDA and
LTA network requests; it would mean Brake arbitrated the generic request the
FRC submitted.

### 2.3 A missing forwarded value does not imply a missing arbitration stage

US20200070873A1 is especially important for physical-topology reasoning, but a
close read makes its scope narrower and more interesting than "the manager sends
the winner ID." Toyota explicitly distinguishes the payload-level
application/request ID from the frame `CAN_ID`. The manager arbitrates an older
set of request samples, sends a control signal containing at least the selected
application ID, and the actuator then selects the latest matching request
**received after that control signal**. The request that caused the arbitration
winner and the request actually actuated can therefore be different samples.

The resulting architecture is a **request-value data plane plus a source-selection
plane**. It still pays the initial request -> manager -> selection delay before a
new source may actuate, but subsequent request values from the selected source
reach the actuator with only the direct network-hop age. Toyota explicitly says
this is especially useful for steering and separately describes actuator-side
rate/gradient limiting to smooth a source handoff.

That architecture is an important alternative realization of the same logical
request/arbitration problem, not a direct map of exact F33. Exact F33 receives
neither `0x08A` nor `0x081`, while B6 is its recovered external target-bearing
cooperative-steering ingress. Therefore `0x081` must not be reinterpreted as
this patent's manager->EPS selected-ID signal and B6 must not be demoted to an
ID-only selector without a separately recovered direct request stream.

The broader lesson remains: the logical application-request -> arbitration ->
actuator-realization graph does not require the manager to relay every exact
physical request sample. Recover the physical realization per actuator and per
platform. Detailed analysis:
[toyota-selected-id-direct-request-arbitration.md](toyota-selected-id-direct-request-arbitration.md).

### 2.4 Clean source suppression is an arbitration-policy operation

A close read of US20230166772A1 sharpens the earlier source-suppression model.
Toyota does **not** make PCS disappear from the network. PCS continues supplying
its kinematic plan and application ID to the motion manager. A different client
(the autonomous-driving application in the main embodiment) sends a separate
**invalidation request**. The manager latches that state, receives the PCS plan
normally, then excludes only PCS from the downstream arbitration input while
other clients remain eligible.

A second signal runs in the opposite direction: while PCS is intentionally
excluded, the manager outputs **request rejection information** to PCS.
Paragraph [0106] says this lets PCS restrict a determination that an
abnormality has occurred merely because its plan was not selected. A separate
cancellation request clears the manager's invalidation flag. Toyota later
generalizes the policy input from literal invalidation to a request giving the
first application's plan **higher priority** than the second.

For the exact Camry, this patent's direct functional analogue belongs at the
**downstream Brake/VMM request-arbitration boundary**, after the FRC has emitted
its feature-selected `0x08A` request. Complete protected-`0x08A` loss is much
lower-level than the patented healthy policy path: it removes the request before
the manager can receive/arbitrate it and can legitimately trigger communication/
request-loss supervision. The relevant search target is therefore a downstream
priority/invalidation state that can reject or de-prioritize a still-present
`0x08A` request, plus whatever result/rejection feedback is returned toward the
FRC/requesting application.

The FRC's own LTA/LDA/LCA/PDA/PCS feature-owner state machine remains a separate
upstream recovery target. It determines which feature populates `5282`/`0x08A`,
but this patent does not prove that FRC-local selection uses the same
invalidation protocol.

The patent also explicitly generalizes the mechanism from acceleration to
steering-angle plans and names LKA/LTA as example steering clients, so the
architecture is directly relevant to lateral takeover rather than merely a
PCS/longitudinal curiosity.

The GTS vocabulary is now more tightly bounded than the first survey suggested:

- **PCS Rejection Request Determination Based On Functional Safety** is not an
  orphan master string. It is referenced only by current `ADCU_P6/P6F`
  table 167 (`CDbDDRFreezeFrameTable`) and resolves to
  `DID$20D4-byte16-bit$FF`. The next row is
  **Arbitration Result (Vertical ID Value)** at
  `DID$20D4-byte25-bit$FF`. Its wording is conceptually closer to the
  patent's requester->manager invalidation/priority decision than to the
  manager->PCS rejection-feedback signal.
- **Driving Force Lower Limit Request Rejection Factors** and
  **Driving Force Upper Limit Request Rejection Factors** are referenced by
  current `HE_PCM_A_P6` RoB freeze-frame rows immediately after
  **Required Driving Force Lower/Upper Limit ID**. The four rows occupy
  successive 8-bit ranges in one recorder group. This is strong P6 evidence
  that requester identity and rejection cause are paired status, but it is not
  an exact P5/F33 mapping.
- Exact P5/TSS3 already exposes priority vocabulary:
  `5280_7 TSS acceleration request low priority flag`, multiple PDA
  priority-request fields, and FRC_P5
  `0x1B06 ISA Speed Change Priority Request (Upper Limit)`. No equivalent
  lateral invalidation/priority field or manager->suppressed-client rejection
  feedback has yet been recovered.
- `240E LCA Reject` is an Operation-FFD feature-event trigger, not evidence
  that it carries the patent's request-rejection feedback.

The two patent directions therefore remain separate recovery problems at the
**downstream manager boundary**: requester/system -> VMM priority/invalidation
policy, and VMM -> suppressed requester intentional-non-selection feedback. Do
not infer one from finding the other, and do not assume either has already been
identified in `0x08A` or `0x081`. Separately recover the FRC feature-owner state
machine that decides which feature authors `0x08A`; that is an upstream problem,
not the patent's manager-side arbitration mechanism.

Detailed close read and cross-generation GTS joins:
[toyota-request-invalidation-us20230166772.md](toyota-request-invalidation-us20230166772.md).

The same vocabulary pass also finds the FRC behavior **X2351 PDA (DA) Brake
Control Invalid Condition**, providing another concrete control-invalid state
to compare with the fail-class model.

### 2.5 Bootstrap fault persistence: FRC eligibility versus Brake/VMM fail state

The post-programming bootstrap problem should now be split into **failure
generation** and **failure persistence**.  The retained evidence does not support
treating persistent DRCC unavailability as identical to a persistent
Brake/VMM lateral fail class.

The strongest current discriminator is September-10 route
`00000093--4066e7ae51`.  That same-ignition drive followed the EPS programming
transition and used conventional cruise because Toyota TSS/DRCC remained
unavailable.  Nevertheless all **14,355/14,355** retained Brake-owned `0x081`
frames have B13=`0x00`: the recovered arbitration-result lateral ID is zero and
the candidate B13[7:6] fail class is also zero.  Native `0x251` simultaneously
contains unavailable (`0xE0`) and conventional-cruise (`0x90`) states.  This
does **not** prove every Brake/VMM eligibility input was healthy, but it does
show that the persistent DRCC restriction can outlive the specific
`0x081 B13[7:6]` failure indication.

The September-17 valid stale-`0x030` bridge supplies the complementary FRC-side
observation.  Before the bootstrap handoff, FRC `0x1903` reported DRCC
all-speed, `0x1905` reported cruise allowed, and `0x1906` had the ACC-not-
available icon clear.  After the approximately **1.293-s** interruption,
`0x1903` and `0x1905` were unchanged while `0x1906` asserted
ACC-not-available.  The resident was unarmed and no DTC clear occurred.  That
experiment proves that bootstrap alone can leave an FRC-visible unavailable
state even after EPS application publication returns; it does not yet identify
whether the retained state is FRC-local or is another peer status latched by
the FRC.

The leading lifecycle hypothesis is therefore:

```text
EPS service interruption
    -> Brake/VMM sees steering reliability loss
    -> temporary/confirmed lateral fail classification
    -> FRC receives/records an unavailable condition

EPS application returns
    -> Brake/VMM fail class may recover
    -> FRC / cruise-eligibility state can remain unavailable for the ignition cycle
```

The decisive next capture is same-ignition and synchronized.  Observe
`0x030` validity/inhibit state, raw `0x081` B13[7:6] and request-loss,
Operation-FFD `5283_1` and `5285`, FRC `0x1905/0x1906`, Brake
`0x102D/0x102F`, and native `0x251` from interruption through stable EPS
application return.  The outcomes separate the domains:

- if raw `0x081`, `5283_1`, and the Brake status surface recover while FRC
  availability remains restricted, persistence is upstream of the live
  Brake/VMM fail classification and an FRC/eligibility latch becomes the
  primary target;
- if `0x081 B13[7:6]` remains at the failure-decided candidate state, the
  arbitration domain itself has not requalified;
- if raw `0x081` clears but `5283_1` remains failed, the FRC is retaining a
  manager-result/fail-class copy rather than merely reflecting the current
  Brake publication.

This distinction has a direct openpilot architecture consequence.  The Panda
relay already sits electrically between the FRC-side and chassis/Brake-side
Toyota Bus-4 endpoints.  If the downstream Brake/VMM domain has requalified
while only the FRC/requester domain remains restricted, openpilot can in
principle take ownership **downstream of the FRC and upstream of Brake/VMM**:
suppress the native FRC copy of `0x08A`, preserve its cadence/freshness as the
initial transport template, modify only the intended application-request
fields, re-authenticate the modified frame, and let Toyota's ordinary
Brake/VMM arbitration/result/request-generation path remain intact.

The cryptographic prerequisite is already stronger than a shared-key
hypothesis.  On the exact Camry, EPS ICU-S selector 4 reproduced **3/3** captured
native FRC `0x08A` trailers byte-exact using live `0x00F` synchronization,
while the separate B6 work proves selector-4 command 5 can generate a distinct
MAC over modified application content.  A modified `0x08A` has not yet been
transmitted/accepted, so receiver acceptance and real-time oracle latency remain
dynamic gates.  For the first takeover discriminator, reuse each intercepted
native `0x08A` freshness/cadence rather than inventing an independent sender
epoch.

A safe stationary acceptance probe can therefore be narrower than a steering
test: with EPS and Brake status recovered but FRC DRCC still unavailable,
replace a short run of native `0x08A` one-for-one with a validly authenticated
ID11 request whose target equals the measured current steering angle, while
preserving the native longitudinal/request metadata.  Success is not physical
motion; it is the downstream result plane following the injected application
identity in the normal native shape — `0x081 B13[5:0]` / `5285` moves to the
requested ID without request-loss or fail-class assertion.  That would directly
prove that the FRC's persistent unavailability is bypassable at the request
boundary.

This does not automatically restore **stock** DRCC.  If the faulted FRC no
longer supplies a usable longitudinal request, lateral-only `0x08A`
replacement can recover lateral request authority while stock ACC remains
unavailable.  Full comma authority would then require separately qualifying the
already-recovered `0x08A` longitudinal request fields and Toyota's
longitudinal arbitration/hold/release semantics.  Avoiding the FRC latch remains
preferable if stock-longitudinal coexistence is the objective.

## 3. Network/gateway families

### US20220055556A1 — In-vehicle network system

Priority 2019-07-09, Toyota.

Discloses a tree network with:

- a high-function **upper ECU**;
- **intermediate ECUs** acting as gateways;
- specialized **lower ECUs** controlling individual sensors/actuators;
- Ethernet as an example upper/intermediate transport and CAN as an example
  intermediate/lower transport;
- intermediate-ECU ownership of lower-ECU communication management and power
  state;
- wake/startup messages that move lower ECUs from power-off -> standby ->
  startup.

The startup sequence is a particularly strong match to the question here. The
intermediate ECU itself can remain in standby while its lower-ECU group is
physically unpowered. An upper-ECU message wakes the intermediate ECU; the
intermediate ECU closes a relay to power the lower group; the lower ECUs first
enter standby; and a relayed network-management message then moves them into
their operational startup state. The patent explicitly notes that the requested
operation need not be limited to conventional ACC/IG states and can instead be
defined around particular vehicle functions. Its related-art section also
describes the conventional Toyota split of constant +B plus switched ACC/IG
rails under a power-supply-management ECU.

Source:
https://patents.google.com/patent/US20220055556A1/en

### US20210014082A1 / US11477047B2 — In-vehicle network system

Priority 2019-07-09, Toyota.

Uses the same upper/intermediate/lower hierarchy but concentrates on redundant
communication/power management. Intermediate ECUs hold a **routing map** and a
healthy intermediate ECU can take over subordinate lower ECUs of a failed
intermediate ECU.

Source:
https://patents.google.com/patent/US20210014082A1/en

These patents are useful architectural vocabulary for EBU/Central
Gateway/junction questions, especially when one logical participant is not
visible on the same physical bus as another. They do not identify the exact
Camry EBU attachment or prove that the patent upper/intermediate/lower placement
matches the F33 harness.

### WO2025084013A1 — selective target-device startup by power or communication

Priority 2023-10-20, Toyota; published 2025-04-24.

This later family is unusually explicit about the distinction between a vehicle
being globally "off" and individual devices being selectively started. A
management device receives a startup request from another ECU and chooses, **per
target device**, between two mechanisms:

1. **power-control startup** — assert a power-control line so the target begins
   receiving power; or
2. **communication startup** — request startup over the in-vehicle network for
   a target already capable of receiving the request.

The disclosed selection logic can use the request source, current vehicle state,
network topology, and a per-function startup-time requirement. The concrete door
example is especially relevant to pre-IG behavior: a door ECU reports that a
door opened while the vehicle is after IG-OFF, the manager interprets the
source+state as a vehicle event, and it starts only the device group needed for
that event.

This patent is **contemporary Toyota architecture evidence**, not proof that
F33 implements this exact manager/database or its target mapping. Its 2023
priority is fully compatible with a 2026-model Camry and could reflect design
work that reached this vehicle generation. The evidentiary limitation is
implementation proof, not chronology: until the exact F33 wiring, firmware, or
live state transitions join to it, use the patent as a strong architectural
oracle rather than as an exact block assignment. It is strong Toyota evidence
that "OFF" is intentionally decomposed into event-driven selective device
startup, and that Toyota distinguishes physical power-control wake from
network/communication wake.

Source:
https://patents.google.com/patent/WO2025084013A1/en

### 3.1 Pre-power-switch wake: public Toyota behavior + current GTS vocabulary

The patent model now joins cleanly to both public Toyota documentation and the
current recovered GTS+ catalog.

The **2025 Camry Hybrid owner's manual** documents a pre-button state directly:

- opening either front door illuminates the power switch;
- with the power switch still OFF, depressing the brake while carrying the
  electronic key makes the power-switch illumination blink; and
- depressing the brake produces a start-related message in the
  multi-information display before the driver presses the power switch.

That is sufficient to say that the current Camry platform performs key/brake/UI
work before the explicit power-button event. It does **not** by itself identify
which ECU wakes which peer or which rail changes state.

Source:
https://assets.sia.toyota.com/publications/en/om-s/OM06266U/pdf/OM06266U.pdf
(page 179)

Toyota/Lexus service literature independently makes the brake-domain behavior
physical rather than merely cosmetic. Lexus bulletin **L-SB-0032-23** warns
that, while the auxiliary battery is connected, the brake control system
activates with the power switch OFF when either the brake pedal is depressed or
**any door courtesy switch** is turned on. The same warning appears across
older Toyota hybrid repair procedures, so this is a long-lived Toyota behavior,
not a one-off UI convention.

Source:
https://static.nhtsa.gov/odi/tsbs/2023/MC-10245447-9999.pdf
(page 9; superseding Lexus brake bulletin)

The current recovered P5 GTS+ databases expose the state split more explicitly:

- PSC_P5.ddb (**Power Source Control**)
  - DID 0x1001: Push Start Switch 1/2/3, Shift P Signal,
    Stop Light Switch, and Starter Drive Request Signal;
  - DID 0x1003: inside/outside IGP and IGR relay-circuit monitors,
    IGP Hold Circuit Monitor, ACC Relay Monitor, and IGB Relay Monitor;
  - DID 0x1005: Power Supply Condition with distinct values
    OFF, ACC ON, IGR ON, IGP ON, and Starter ON;
  - DID 0x2001: Accessory Mode (ACC) Transition.
- CentralGW_P5.ddb (**Central Gateway**) DID 0x1001 independently exposes
  IG2 SW/IGR SW, IG1 SW/IGP SW, ACC SW, and +B Voltage.
- PowIntegr_4_P5.ddb (**Power Distribution Box**) DID 0x5011 exposes
  Power Supply Management Request Signal.
- SMART_P5.ddb (**Entry&Start**) exposes
  Start SW Light Power Supply (0x2803), Steering Lock Sleep Condition,
  Steering Lock Start Condition, ID-BOX Sleep Condition, and
  ID-BOX Start Condition.
- HV_P5.ddb (**Hybrid Control**) exposes an independently named wake plane:
  - DID 0x1456: WAKE Signal Status for the Gear Shift Control Module,
    module B, and sub-CPU variants;
  - DID 0x1417: a sub-battery backup request whose value 1 is
    Backup Stop Request / Wake Up/Sleep Permission;
  - DID 0x1460: Gear Shift Control Module Backup Signal Status value 1
    = Wake Up Request, and a companion request value 1
    = Wake Up/Sleep Permission.

The important architectural point is that Toyota's own diagnostic model does
**not** collapse wake into ACC/IG. The current catalog has distinct wake/sleep
state, start-function state, physical/relay power state, and button/brake input
state.

There is also a useful service-manual continuity check on the input side. Modern
Toyota smart-key diagnostics expose a certification ECU with constant +B in
ignition-off and a direct stop-light/brake input, while older Toyota push-button
start manuals explicitly route the stop-light switch and power switch into the
power-source controller. Those older wiring examples should be used only as
topology vocabulary; the current PSC_P5/SMART_P5 records above are the better
search oracle for F33.

Public reference example:
https://lemon.dogeware.me/Toyota/2023/Sienna%20XSE%2C%202.5L%20Eng%20VIN%20R/Repair%20and%20Diagnosis%20%28Single%20Page%29/Body%20%26%20Frame/Door%20Locks/Smart%20Key%20System%20%28For%20Start%20Function%29%20-%20Diagnostics%20-%20Introduction/SMART%20KEY%20SYSTEM%20%28for%20Start%20Function%29/Terminals%20Of%20Ecu%20%5B11%2F2020%20-%2009%2F2022%5D/Terminals%20Of%20Ecu%20%5B11%2F2020%20-%2009%2F2022%5D/

### 3.2 What this means for the exact F33 wake investigation

The best current model is a **layered power-state machine**, not a binary
OFF/ON model:

1. **quiescent / always-powered observers** remain capable of detecting at
   least selected entry/start/network events;
2. a **pre-IG event wake** can start selected ECU functions or whole power
   groups in response to door, key, brake, timer, remote, or other events;
3. **ACC / IGR / IGP** are broader named power-source states with their own
   relay/request monitoring; and
4. **READY** adds the hybrid/drivetrain start state.

This fits the retained F33 dynamic evidence, now with a true deep-sleep control.
On 2026-09-22 the vehicle had not been entered during the day; with Panda's
power-save disabled solely to expose all receive paths, a 60.002-s direct-Panda
NOOUTPUT capture observed **zero CAN frames and zero RX-counter movement on all
three controllers**. By contrast, the September-20 pre-start brake-wake capture
already had 648 native frames / 58 `(bus,address)` streams in its first
3170.505 ms before the brake instruction, including 27 native `0x00F` frames on
each of buses 0 and 2. Therefore `0x00F` is not a continuously running
true-deep-sleep stream: the older capture was already in a wake-active OFF
state. The brake/meter event is **not** the origin of that visible freshness
epoch; some earlier entry/key/door/setup event had already awakened the relevant
network domain.

Do not yet assign the patent's abstract "management device", "upper ECU", or
"intermediate ECU" to F33 Central Gateway, Power Source Control, Power
Distribution Box, EBU, Main Body, or Entry&Start. Current GTS gives all of those
useful observables, but an exact ownership map still requires live transitions,
wiring/EWD evidence, or firmware.

A 2026-09-22 binary proximity probe now closes the first boundary. Starting
from verified zero-CAN deep sleep, the operator approached and stood next to the
driver's door carrying the normal Toyota key without touching the car. The
network stayed silent for 32.244 s after arming, then woke abruptly; `0x45A`
was first and `0x00F` followed about 303.5 ms later. Within one second 28 native
IDs / 56 mirrored bus0/bus2 streams were active. Therefore ordinary approach
while carrying the normal key is sufficient to move the comma-visible network
from deep sleep into wake-active OFF.

The remaining sequence can now start from that established state rather than
treating proximity as an unknown:

key-proximity wake -> door unlock/open -> key in cabin -> brake down
-> brake up -> power-button press -> READY -> power OFF -> door close -> sleep

For each later boundary, record per-bus first/last frame time and newly appearing
IDs, and concurrently sample the read-only GTS observables above when practical.
Particularly useful joins are PSC 0x1001/0x1003/0x1005,
Central Gateway 0x1001, PDB 0x5011, and the SMART_P5 sleep/start fields.
A true deep-sleep baseline must begin **before approaching with the normal key**,
not merely before touching a door.

## 4. Security and reprogramming families

### US20250300993A1 / US12615265B2 — secured CAN / SecOC

Priority 2024-03-22, Toyota.

This is later than the initial TSS3 launch, but its 2024 priority is still
temporally compatible with a 2026-model F33 Camry. It must therefore be treated
as **contemporary Toyota security vocabulary**, not dismissed as too new; the
remaining limitation is that a patent does not prove this exact calibration
uses its new dynamic-key scheme.

Its description explicitly calls the related architecture **AUTOSAR SecOC**:
sender and receiver ECUs share a secret key, the sender appends a MAC to the
PDU, and the receiver recomputes the MAC and rejects/discards a PDU on
verification failure. The disclosed newer design additionally discusses a
monotonic counter/freshness value, startup synchronization to avoid initial
counter rejection, and truncating the MAC and counter when payload space is
limited.

The invention's new contribution is dynamic per-ignition key derivation from
pre-provisioned material. Do not assign that mechanism to the Camry merely from
the patent: exact firmware/dynamic evidence remains authoritative for its
key/profile behavior. Chronology does not exclude it on a 2026 vehicle.

The patent is intentionally broad about how the derived key becomes usable by
the ECU. Do **not** infer a programmable-HSM KDF or a new HSM firmware path from
it. Exact F33 already proves Toyota uses the standard AUTOSAR SHE Memory Update
Protocol (`M1/M2/M3 -> CMD_LOAD_KEY -> M4/M5`) for ECU Security Key provisioning,
and AUTOSAR explicitly permits that secure update protocol to target the
volatile `RAM_KEY` slot while clearing the plain-key flag.

That does **not** automatically make per-ignition rotation stronger. AUTOSAR's
own SHE specification warns that keys loaded into `RAM_KEY` from outside SHE
are not fully under SHE control and are vulnerable to replay and denial-of-
service attacks. For `RAM_KEY` secure updates, the update counter and flags are
fixed/ignored rather than providing the monotonic anti-replay state used by
nonvolatile key slots. Therefore a captured UID-specific `M1/M2/M3` transcript
for a volatile session key can be a replay/rollback artifact if an attacker can
reach the corresponding `CMD_LOAD_KEY` path; the envelope still protects the
plaintext key cryptographically, but it adds persistent protocol material and
state that do not exist when the operational SecOC key simply remains in a
non-exportable hardware slot.

The patent's literal per-ECU derivation embodiment has a different tradeoff: it
avoids distributing a session-key envelope, but requires every participant to
possess enough common long-term material and boot-context/OTP logic to derive
the same key independently. The patent expressly allows the passcode generator
and key-derivation module to be implemented as ordinary processor-executed
software/firmware and allows the master seed to reside in ECU memory or
firmware. If realized that way, it expands the trusted/reverse-engineerable
CodeFlash surface around a root secret whose compromise still defeats all
future rotations. Neither implementation should be described as an inherent
security improvement over a well-contained static HSM key without identifying
the narrower threat model it actually improves.

Source:
https://patents.google.com/patent/US20250300993A1/en

A dedicated claim/threat-model/F33 comparison is in
[`../security/secoc/us20250300993-dynamic-key-patent.md`](../security/secoc/us20250300993-dynamic-key-patent.md).

For the existing F33 work the useful part is Toyota-authored terminology around
MAC verification, freshness, truncated security fields, receiver rejection,
and startup synchronization. It is a conceptual cross-check for the recovered
SecOC-shaped traffic, not a substitute for the exact EPS/FRC implementation.

### US20230143921A1 / US12504961B2 — electronic control system for vehicle firmware

Priority 2021-11-10, Toyota + Denso.

Discloses a master controller receiving an update program plus update
information, transferring them to a sub-controller, and the sub-controller
writing the update program into memory, including handling for another/specific
memory region.

Source:
https://patents.google.com/patent/US20230143921A1/en

This is relevant as an OTA/reprogramming architecture family, but the current
pass did **not** find a comparably strong Toyota patent exposing the exact GTS
Security Key / repair-time SecOC rekey procedure. Service/GTS evidence remains
the better source for that path.

## 5. Driver attention / steering-state families

### US20220001874A1 / US11485367B2 — Driver monitoring system and method

Priority 2020-07-01, Toyota.

Discloses hands-off automated steering with distinct state channels for
steering-wheel holding/contact and driver attention. A dependent embodiment
uses a **steering touch sensor** to produce hands-on/hands-off "steering holding
information"; a separate driver monitor can verify surrounding-confirmation
behavior. The request controller periodically asks for hands-on or a surrounding
check and can vary that interval with traffic/environment/map/driver-warning
context.

The patent itself contains **no torque-sensor disclosure and no torque
threshold**. The touch-vs-torque fusion conclusion comes from Toyota's diagnostic
corpus, not from this document. Its illustrative ~10-minute hands-off interval
and ~4-second confirmation dwell are also not a behavioral match for the exact
F33 ordinary-LTA ~13-second torque-backed nag.

Source:
https://patents.google.com/patent/US20220001874A1/en

Deep review:
[toyota-driver-monitoring-us20220001874.md](toyota-driver-monitoring-us20220001874.md)

For TSS3 this is strongest as architecture vocabulary: wheel holding/contact,
driver-monitor attention, the attention timer, and HMI request are separate
concepts. It does not prove which TSS3 trims implement touch sensing, and the
exact maintainer Camry's retained 5609 state says its LTA driver-monitor-camera
collaboration and Toyota hands-off capability are absent.

US20230082947A1 independently places **whether the driver grips the steering
wheel**, steering-wheel operating torque, steering-wheel rotation angle, and
steering reliability in the steering-system state returned to the motion
manager. That gives us a concrete place in the architecture to look for
hands-on state even on a vehicle where the physical detector is torque-based.

### US20240149940A1 / US12344341B2 — Steering control device and method

Priority 2022-11-09, Toyota + JTEKT.

A later steering-family source centered on target/actual pinion-angle control,
turning torque, and steering protection behavior. It is useful terminology for
searching a TSS3 EPS because the Toyota request interface already names
**pinion angle**, but its disclosed steering architecture should not be assumed
to be the conventional F33 EPS.

Source:
https://patents.google.com/patent/US20240149940A1/en

## 6. Immediate experiment/search queue

These patents suggest concrete next steps that can be tested without assuming
any patent embodiment is exact-F33 truth.

### A. Decode 5283_1 dynamically

Capture the already-planned failure onset with at least:

- 5283_1;
- 5285;
- 57DE;
- raw Brake 0x081;
- FRC 0x1905/0x1906;
- Brake 0x102D/0x102F.

Induce or observe transitions that separately distinguish healthy, restricted
but still functioning, invalid-before-confirmed-failure, and confirmed failure.
Then map **observed transitions** onto the patent semantic states. Do not assign
the patent example two-bit numeric codes to the GTS byte in advance.

### B. Search the GTS corpus using patent vocabulary

High-value strings and near-synonyms:

- influenced vehicle velocity range
- malfunctioning portion
- operation mode
- reliability
- protective control
- control invalid
- fail class
- request rejection
- invalidation
- arbitration target
- scheduled to terminate
- degeneration
- application ID
- actual steering angle
- middle point
- steering grip
- steering touch
- routing map
- communication management

The first cluster is especially likely to extend the current 5283 fail-class
dictionary into a richer failure-cause/status surface.

### C. Recover the FRC application-owner table/state machine empirically

Create controlled captures where the FRC's current feature owner changes while
other features remain enabled: LTA, LDA, LCA, PDA/OAA/SA, PCS where safely
observable, and longitudinal ACC/DRCC clients separately. Correlate
feature-local FRC request/state -> generic `5280/5281/5282` owner -> protected
`0x08A` egress -> downstream `5284/5285` / `57DB/57DE` result -> `0x081` ->
B6/final actuator instruction where observable.

US20220219711A1 makes this useful because Toyota explicitly treats application
identity and priority/eligibility as separate concepts. On the exact Camry, the
lateral feature-owner decision should be recovered in the **FRC application**,
not by looking for simultaneous LTA/LDA/PDA request PDUs at Brake.

### D. Separate healthy FRC feature preemption from downstream policy rejection

First recover the FRC-local sequence where one feature remains enabled/alive ->
its local eligibility/inhibition state changes -> another feature becomes the
generic `5282` owner -> protected `0x08A` expresses the new owner -> downstream
`5285`/`0x081` follows without request-loss or fail-class transition. That
characterizes the normal **feature-owner handoff**.

Separately hunt for the stronger US20230166772A1 signature at the Brake/VMM
boundary: a feature-selected `0x08A` request remains present, but downstream
arbitration intentionally does not select it (or explicitly reports rejection),
while request-loss and fail class remain healthy and feedback toward the FRC/
requester explains the non-selection. No retained healthy road interval shows
that state yet.

This separation also explains why blocking the whole `0x08A` egress is the
wrong abstraction: it removes the request before the downstream arbiter can
perform a healthy policy decision and instead exercises communication-loss
supervision.

### E. Check hands-on state at the manager boundary

When steering torque changes and/or any capacitive-wheel-equipped comparison
vehicle is available, search Brake/FRC/GTS data for a compact grip/touch state
that changes independently from raw steering torque. The patents make driver
grip an explicit steering-state signal into the motion manager, so the detector
does not need to live in the FRC itself.

### F. Keep SecOC startup behavior separate from the new key proposal

Use the 2025 publication only to guide terminology/tests around freshness
synchronization at startup, counter/freshness rejection, truncated
freshness/MAC fields, and reject/discard behavior. Do not import its
per-ignition dynamic-key design into the F33 model unless exact firmware or
dynamic evidence independently shows it.

## 7. Patent-search heuristic for future passes

The productive cluster is not the generic phrase "Toyota Safety Sense." The
best search graph starts from the Japanese source cited by many later families:

**JP2020-032894 / US20200070849A1**.

Useful recurring vocabulary:

- motion manager
- kinematic plan
- application ID
- arbitration target
- fail class
- PLN2, BRK2, STR2
- request rejection
- degeneration
- control record value
- vehicle motion controller

Recurring Toyota/ADVICS inventors in this cluster include Kazuki Miyake, Wataru
Kanda, Hideki Ohashi, Shota Higashi, Yoshihisa Yamada, and others. Citation and
similar-document graphs around these families are much higher-signal than a
broad ADAS search.

The current landscape should be treated as the beginning of a repeatable
source-mining path: every new GTS term or unresolved wire behavior can be
searched against this family graph before inventing names from scratch.
