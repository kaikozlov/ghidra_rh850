# Toyota US20220001874A1: hands-on, touch sensing, and driver-monitor attention

**Source:** Toyota Jidosha Kabushiki Kaisha, US20220001874A1,
"Driver Monitoring System and Driver Monitoring Method", priority 2020-07-01,
published 2022-01-06.

**Evidence grade:** external-source architecture/terminology. This patent is a
semantic and design oracle, not proof that the exact 2026 Camry F33 implements
the illustrated embodiment or physical ECU topology.

## Executive finding

This patent is useful primarily because it separates three concepts that are
easy to collapse when reverse-engineering Toyota driver-attention behavior:

1. **automated-driving state** -- whether hands-off automated steering is active;
2. **steering holding state** -- a hands-on/hands-off judgment produced from a
   dedicated steering touch sensor in the disclosed embodiment;
3. **driver-attention state** -- a separate driver monitor that can infer whether
   the driver visually performs a requested surrounding-confirmation action.

The patent does **not** disclose a steering-torque sensor or a torque threshold.
Its hands-on embodiment is touch-sensor based. Toyota's later P5/P6 diagnostic
corpus independently proves torque and touch are separate, combinable hands-on
inputs; that conclusion does not come from this patent alone.

The patent is also not a close behavioral match for the exact maintainer Camry's
ordinary LTA nag. Its core scenario explicitly allows hands-off automated
steering and gives illustrative notification/reset intervals on the order of
minutes and seconds, whereas the exact F33 road corpus shows the ordinary ID11
LTA hands-off warning begins about 13 seconds after the FRC's low-sensitivity
driver-steering detector releases. The exact Camry retained TSS3 recorder also
has Hands-Off Exist=0 and LTA Driver Monitor Camera Collaboration Exist=0.

The best use of this patent for F33 is therefore **architecture vocabulary and
feature separation**, not copying its timer or assuming its touch sensor is the
source of the ordinary LTA nag.

## 1. What the patent actually claims

The independent system claim is deliberately broad. It requires:

- an automated-driving controller that allows a hands-off operation while
  automatically steering; and
- a request-notification controller that periodically reissues either a
  **hands-on request** or a **surrounding confirmation request** after a
  criterion time expires.

The steering touch sensor is only added by dependent claim 2. The driver monitor
is separately added by dependent claim 3. Claims 4-9 add context-dependent
criterion-time control based on surrounding information, a preceding vehicle,
roadside alert information, map alert sections, and an existing driver warning.

Consequences for RE:

- the patent does not make touch sensing mandatory for the base invention;
- the patent does not make a driver-monitor camera mandatory for the base
  invention;
- the patent explicitly treats hands-on confirmation and visual-attention
  confirmation as different mechanisms that can satisfy different requests.

## 2. Figure 2: the logical architecture

Figure 2 is a functional block diagram:

~~~text
camera -----------\
radar -------------\
communication ------\
navigation ----------> Vehicle ECU
vehicle-state ------/      |
driver monitor -----/      +-- Automated Driving Controller
steering touch ----/       +-- Request Notification Controller
                              |
                              +--> HMI: speaker / HUD / MID
                              |
                              +--> Traveling Device:
                                   steering / driving / braking
~~~

The detailed description says the input side of the vehicle ECU includes a
camera, radar, communication device, navigation device, vehicle-state sensor,
driver monitor, and steering touch sensor. It separately says the travel device
contains steering, driving, and braking devices, with EPS as an example of the
steering device.

This should be read as **logical ownership**, not a literal TSS3 wiring diagram.
The current TSS3 evidence places the steering-touch hardware behind a
steering-wheel/CXPI subnetwork and Combination Meter before FRC/SRS consumers;
the patent does not expose that transport.

## 3. Steering touch is a first-class state, not inferred attention

The patent defines the touch sensor's output as **steering holding information**
indicating whether the driver is hands-on or hands-off. That information is sent
to the vehicle ECU and stored independently from automated-driving information.

This matters because it gives Toyota-authored semantics for a clean binary
contact/holding state. It is not described as gaze, attentiveness, steering
override, or driver torque.

The request-notification logic then uses that steering-holding state to decide
whether the driver's hands-on operation has occurred and whether the request can
be withdrawn/reset.

### Important negative: no torque sensor is disclosed

A full-text search of this patent produces no occurrence of "torque". The
phrasing "steering wheel has been steered by driver" in the flow description is
still evaluated from the patent's steering holding information, which the
specification says originates at the steering touch sensor.

Therefore:

- do not cite this patent as evidence that Toyota's hands-on detector is
  torque-based;
- do not infer a torque threshold from the illustrative "4 seconds" dwell;
- use current GTS/vehicle evidence for the F33 torque path instead.

## 4. Driver monitor is a separate attention channel

The driver monitor is explicitly separate from the steering touch sensor.
Examples of monitored driver state include:

- line of sight, using a camera;
- heartbeat, potentially through steering-wheel electrodes;
- breathing, potentially through a seat load sensor.

In the modified first embodiment, driver-monitor information is used to verify
that the driver visually looked at requested surrounding-confirmation points
such as the road ahead, meter, mirrors, or blind spot.

The patent therefore supports a very useful architectural distinction:

~~~text
wheel contact / holding        !=        visual attention / awareness
steering touch sensor                    driver monitor
~~~

The request-notification controller may use a hands-on request, a surrounding
confirmation request, or alternate between them. A visual confirmation can
therefore refresh the attention timer without being represented as steering
wheel contact.

That distinction is consistent with current Toyota diagnostic vocabulary:

- TSS3/P5 has explicit steering-touch configuration/fault vocabulary;
- predecessor P5 has separate torque-sensor and touch-sensor "not holding"
  judgments;
- P6 has a combined Steering Wheel Hold Detection enum whose values distinguish
  touch, torque, and touch+torque;
- current FRC/TSS3 separately exposes driver-monitor-camera capability and
  warning-reason fields.

## 5. The timer is an attention budget, not a lateral-control timeout

The first embodiment's state machine is:

~~~text
hands-off automated steering begins
        |
        v
start elapsed timer T
        |
        v
T > criterion Tth ?
        |
       yes
        |
        v
issue hands-on request
        |
        v
hands-on/holding confirmed for dwell
        |
        v
withdraw request + reset T
~~~

The example values are approximately 10 minutes for Tth and approximately
4 seconds for the hands-on confirmation dwell. They are explicitly examples,
not invariant calibration values.

The second embodiment adds **voluntary hands-on**: a driver who touches/holds
the wheel before a request is issued resets the attention interval, and the next
timer begins after returning to hands-off.

This is conceptually similar to the exact F33 observation that a driver-detection
event resets a countdown, but the timescale and feature mode are completely
different. It is better interpreted as a family resemblance in state-machine
shape than as the same state machine.

## 6. Context changes the allowed hands-off interval

Embodiments 3-6 vary the criterion time rather than treating it as a universal
constant.

The patent gives these examples:

- **preceding vehicle present:** shorter interval / more frequent request;
- **roadside/VICS alert present:** shorter interval;
- **vehicle in a map-defined alert section:** shorter interval;
- **driver warning already issued for decreased attention:** shorter interval.

That is a useful Toyota design pattern: driver-attention enforcement can be
**risk/context dependent**, and the thing being varied is the time budget before
the next acknowledgement request.

For TSS3 RE, this suggests searching recorder/GTS surfaces for:

- hands-off duration;
- criterion/reference time;
- warning-stage state;
- driver-warning state;
- road/environment-dependent hands-off policy;
- separate "attention" versus "wheel holding" state.

It does **not** imply the exact F33 ordinary LTA 13-second timer varies in this
way. That needs dynamic evidence.

## 7. Relation to the exact 2026 Camry

### What transfers cleanly

The patent reinforces several current F33/TSS3 conclusions:

- Toyota treats steering-wheel holding/contact as a first-class input;
- driver-monitor attention is a separate input from wheel holding;
- HMI warning state can be downstream of an internal timer/judgment state;
- a hands-on event can reset a timer independently of changing lateral-control
  authority;
- the displayed request is not itself the timer.

Those points fit the exact F33 chain already recovered from September road data:

~~~text
EPS 0x030 driver torque/state
    -> FRC low-sensitivity driver-steering judgment
    -> FRC hands-off duration/judgment
    -> 0x371 warning state
    -> 0x412 warning/escalation presentation
~~~

### What does not transfer

The exact maintainer Camry has retained TSS3 recorder evidence:

- LTA Exist=1;
- Hands-Off Exist=0;
- LTA Driver Monitor Camera Collaboration Exist=0.

Its ordinary LTA nag occurs in Target Lateral ID 11 (LTA/LCA), not ID 10
(Hands Off LTA). The warning begins about 13 seconds after the FRC
driver-steering-detected candidate releases, not after a multi-minute hands-off
window.

Therefore this patent most likely describes a **hands-off-capable Toyota
automated-steering feature family** rather than the exact ordinary-LTA nag
behavior on this car.

This distinction is important: Hands-Off Control Condition, Target Lateral ID10,
and driver-monitor-camera collaboration should not be used as knobs for the
exact Camry's ordinary nag merely because this patent uses similar English.

## 8. Relation to current Toyota GTS evidence

The current corpus makes the patent much more useful than it would be in
isolation.

### Touch hardware/configuration

TSS3 recorder vocabulary has:

- 5222 = Touch sensor presence (タッチセンサ有無);
- FRC_P5 DTC C1A7796 = Steering Touch Sensor / Component Internal Failure.

This is strong fleet-level evidence that the touch-sensor embodiment in the
patent corresponds to a real TSS3 hardware/configuration dimension.

### Touch vs torque

Predecessor P5 diagnostics expose independently:

- DID 0x1044: Not Holding Steering Wheel Judgment Status (Torque Sensor);
- DID 0x1045: Not Holding Steering Wheel Judgment Status (Touch Sensor).

P6 successor diagnostics make the fusion model explicit at DID 0x1B10
Steering Wheel Hold Detection:

- 0 = Release Detection;
- 1 = Hold Detection (Steering Touch Sensor);
- 2 = Hold Detection (Torque Sensor);
- 3 = Hold Detection (Steering Touch Sensor and Torque Sensor).

That is the evidence that Toyota models touch and torque as separate,
combinable sources. The 2022 patent itself only supplies the touch side.

### Driver-monitor collaboration

Current TSS3/FRC surfaces separately name:

- Drive Monitor Equipped;
- PCS Drive Monitor Early Warning Function;
- LDA Driver Monitor Camera Collaboration Exist;
- LTA Driver Monitor Camera Collaboration Exist;
- Driver Monitor Camera Warning Reasons.

That separation closely mirrors the patent's design: wheel-holding information
and driver-monitor information enter the notification policy as distinct state
objects.

## 9. What the patent changes for the nag investigation

It mostly **narrows** the problem.

For the exact maintainer Camry's ordinary ID11 LTA:

- chasing the driver-monitor camera is probably the wrong branch because the
  exact car says LTA-DMC collaboration is absent;
- chasing Hands Off LTA/ID10 is also the wrong branch because the warning was
  captured entirely under ID11;
- the current primary path remains authenticated EPS 0x030 torque/state -> FRC
  low-sensitivity driver-steering judgment -> roughly 13-second timer;
- replacing 0x412 can remove the presentation, but this patent reinforces the
  general design separation between an internal attention timer and its HMI
  request, so it gives no reason to believe HUD replacement resets the timer.

The touch-sensor branch becomes useful only if we establish that this particular
wheel/configuration has touch hardware, or when analyzing another TSS3 vehicle
that does.

## 10. Best next measurements

### Exact maintainer Camry

1. Capture/read TSS3 recorder 5222 if possible to answer the exact-car
   **touch-sensor presence** question directly.
2. Continue the synchronized native 0x030 / 0x371 / 0x412 plus FRC Operation-FFD
   capture around a complete hands-off warning/escalation/cancel sequence.
3. Prioritize 560D, 5601, 5612, 5615, 5632, 550D, 5774, and 5776 to separate
   hands-on detection, timer/judgment, presentation, and override.
4. If a driver-monitor-equipped Toyota comparison vehicle is available, record
   DMC collaboration/warning state independently from wheel contact.

### Touch-equipped TSS3 comparison vehicle

Use a stationary low-torque four-state touch test:

- neither hand;
- left only;
- right only;
- both.

Capture FRC-side traffic, native EPS torque/state, and the Toyota grip/touch
diagnostic surfaces. The target is a field that follows left/right touch while
EPS driver torque stays near zero. That cleanly separates capacitive hands-on
from torque-based hands-on.

## Bottom line

US20220001874A1 is not the patent that explains the exact Camry's 13-second
ordinary-LTA nudge timer.

It is valuable because it gives Toyota's own clean conceptual decomposition:

~~~text
automated-steering mode
        +
steering holding/contact
        +
driver visual/physiological attention
        +
context-dependent attention timer
        ->
hands-on / surrounding-confirmation HMI request
~~~

That decomposition matches the way the GTS corpus is now falling apart into
separate touch, torque, driver-monitor, timer/judgment, and HMI surfaces. The
patent therefore strengthens the architecture model while simultaneously
warning us not to collapse those surfaces into one "driver attention" bit.
