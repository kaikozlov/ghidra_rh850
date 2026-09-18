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
| **US20200070873A1 / US11643089B2**, Vehicle control system | 2018-08-29; pub. 2020 | Toyota | Applications put request values plus unique IDs directly on the in-vehicle network. The movement manager selects an **ID** and sends a control signal carrying at least that ID. The actuator controller receives application requests independently and uses the latest request matching the selected ID. Claim 4 explicitly covers EPS/lateral motion. | Critical alternative physical realization: the manager does not necessarily forward the selected physical value. This cautions against inferring the logical request-to-target architecture solely from which intermediate value is visible on one bus. |
| **US20200070802A1 / US11161496B2 / US12005882B2**, Control device | 2018-08-30; pub. 2020 | Toyota | Brake control ECU contains request arbitration, command distribution, feedback control, and optionally vehicle-motion control. It feeds measured **control record values** and summarized actuator operation/soundness information back to requesting applications; direct wheel-speed inputs and preferential stability control are explicit. | Reinforces Brake/VMM ownership and gives a reason for the rich result/status plane: applications need realized motion plus actuator soundness, not only the selected request. |
| **US20220315018A1 / US12280788B2**, Control apparatus, manager... | 2021-04-06 | Toyota + ADVICS | Applications supply information about whether a kinematic plan remains an **arbitration target**. A request that is about to terminate can be excluded or handled specially so a new request is not delayed. | Concrete vocabulary for handoff/disengagement and source-suppression RE: search for arbitration-target, termination, low-priority, degeneration and handoff state rather than modeling every request as simply present/absent. |
| **US20230166772A1 / US12534110B2**, Motion manager, autonomous driving apparatus... | 2021-11-30 | Toyota | A manager can intentionally invalidate a PCS/other ADAS request and return **request rejection information** so the suppressed application does not diagnose an abnormal condition merely because its plan is not selected. The disclosed invalidation target can also be AEB, ACC, ASL, or another application. | High-value conceptual clue for the persistent TSS3 fault-state problem. Clean source replacement may require a result/rejection/status contract in addition to suppressing the source request. Do not assume exact Camry has this exact ADS embodiment. |
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

### 2.3 A missing forwarded value does not imply a missing arbitration stage

US20200070873A1 is especially important for physical-topology reasoning. In its
disclosed architecture, applications transmit their requests to the network,
the movement manager chooses an application **identifier**, and the actuator
controller independently consumes the application request that matches the
chosen identifier. This arrangement is explicitly meant to avoid the latency
of receiving and retransmitting the entire chosen request through the manager.

Therefore the logical application-request -> arbitration -> actuator-realization
graph does not imply a physical graph in which the request value itself must be
visible on every manager-to-actuator link. This family should stay in mind when
interpreting hidden/local Brake/VMM routing and the apparent absence of some
intermediate target values at the Panda-visible junction.

### 2.4 Clean source suppression probably has a status half

US20230166772A1 is the strongest patent clue for the current "disable one native
control source and the system faults" problem. In the disclosed
autonomous-driving embodiment, the manager intentionally rejects the PCS
kinematic plan and tells PCS that its request was **rejected/invalidated**.
Receiving that information prevents PCS from deciding that its own request is
being ignored due to a system abnormality.

The exact F33 mechanism may differ, but the architecture tells us to look for
two coupled operations:

1. stop/admit/replace the native application request;
2. provide whatever arbitration-result/rejection/status feedback tells the
   source that non-selection is intentional and healthy.

That makes 0x081, 5284/5285, and any request-rejection/invalidation state more
important to the source-suppression experiment than a simple CAN block.

A patent-guided GTS search on 2026-09-18 immediately produced three important
master-vocabulary hits:

- **Driving Force Lower Limit Request Rejection Factors**;
- **Driving Force Upper Limit Request Rejection Factors**;
- **PCS Rejection Request Determination Based On Functional Safety**.

At present these three are recovered as strings in M_English.ddb, not resolved
to an exact F33 ECU/DID/recorder field. They therefore do not yet prove the
wire mechanism, but they materially strengthen the hypothesis that request
rejection is an explicit Toyota control-state concept rather than wording that
exists only in the patent. The next GTS task is to recover the owning table or
consumer for these strings and look for a lateral counterpart.

The same vocabulary pass also finds the FRC behavior **X2351 PDA (DA) Brake
Control Invalid Condition**, providing another concrete control-invalid state
to compare with the fail-class model.

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

## 4. Security and reprogramming families

### US20250300993A1 / US12615265B2 — secured CAN / SecOC

Priority 2024-03-22, Toyota.

This is later than TSS3 launch and must be treated as **downstream Toyota
security vocabulary**, not evidence that F33 uses its new dynamic-key scheme.

Its description explicitly calls the related architecture **AUTOSAR SecOC**:
sender and receiver ECUs share a secret key, the sender appends a MAC to the
PDU, and the receiver recomputes the MAC and rejects/discards a PDU on
verification failure. The disclosed newer design additionally discusses a
monotonic counter/freshness value, startup synchronization to avoid initial
counter rejection, and truncating the MAC and counter when payload space is
limited.

The invention's new contribution is dynamic per-ignition key derivation from
pre-provisioned material. **Do not project that part backward** into the Camry:
exact firmware/dynamic evidence remains authoritative for its key/profile
behavior.

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

### C. Recover the application-ID table empirically

Create controlled captures where only one relevant factory client changes at a
time: LTA, LDA, ACC/DRCC, PCS where safely observable, PDA/OAA, and driver
operation. Correlate feature-local request ID -> 5280/5281/5282 request ID ->
5284/5285 arbitration-result ID -> 57DB/57DE selected result -> 0x081
result/status -> B6/final actuator instruction where observable.

US20220219711A1 makes this a much more promising exercise because Toyota
explicitly treats these IDs as application identities used by arbitration
policy.

### D. Examine healthy source suppression, not only frame blocking

Search for a native sequence with request active -> request marked non-target
or invalidated -> result/rejection returned to source -> alternate application
wins -> source does not enter abnormal state.

This is the patent-guided experiment most directly relevant to avoiding the
current FRC/Brake fault state while taking control.

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
