# 2026-09-01 Camry live communication characterization — working notebook

**Status:** live working notes. Deliberately not promoted into canonical findings yet. No verification suite is attached to this notebook.

**Vehicle state during probes:** attached to maintainer 2026 Camry; stationary when mutation probes were performed. Brake DID `0x1042 Vehicle Speed (Control Value)` returned `0.0 km/h` immediately before CommunicationControl experiments. Existing openpilot `0x08A` replacement behavior was intentionally left unchanged; this session did not remove/block `0x08A`.

**Stop point:** live probing stopped when rear-speaker white noise appeared and the operator restarted the car. Resume only after operator confirms restart.

## Objective

Characterize the actual lateral-control communication graph first-principles: who originates/supervises the request plane, what returns from the chassis side, which ECU owns surrounding state publications, and how Toyota's TSS3 Operation FFD internal request/arbitration/grant records relate to CAN.

The important distinction used below is:

- **source / normal-Tx dependency:** disabling an ECU's normal communication causes a frame to disappear;
- **physical CAN transmitter:** the ECU whose CAN controller actually emits that frame on the observed bus.

`CommunicationControl` proves the first directly. It proves the second only where topology independently puts that ECU on the native observed bus. In particular, FRC is GTS Bus 1 while the protected request appears on the accessible relay/bus-4 plane, so `FRC CommControl -> 0x08A disappears` must not by itself be called proof that the FRC CAN controller physically signs/transmits `0x08A`.

## 1. Live diagnostic anchors before source isolation

### FRC

FRC DID `0x1601` returned:

- `LTA Switch Condition Flag = ON`
- `LTA Control Condition = LTA Disabled`
- `Hands-Off Customize Condition Flag = OFF`
- `Hands-Off Control Condition = Hands-Off Enabled`

Other lateral functions were likewise disabled in the current faulted/bring-up state:

- DID `0x1501`: `LDA Customize Condition Flag = ON`, `LDA Control Condition = LDA Disabled`
- DID `0x1C81`: `PDA (SA) Customize Status = ON`, `PDA (SA) Control Status = Disabled`

PCS was not globally switched off; DID `0x1703` showed the PCS switch itself ON, although its availability bit was disabled at this point.

Interpretation for this notebook only: current problem is a lateral-control inhibition/supervision state rather than loss of the whole FRC or EPS diagnostic path.

### Brake / EPS

Brake DID `0x102F` showed `EPS/Steering Control Actuator ECU Communication = Normal`.

EPS remained responsive and steering-angle diagnostic reads worked.

Generic GTS catalog entries `Brake 0x107E ADS Control EPS Pinion Angle2` and `EPS 0x1CEE/0x1CEF` do **not** transfer to these exact live calibrations: the tested DIDs returned request-out-of-range / unsupported even after the applicable extended-session attempt. Do not use those generic monitor rows as live Camry F33 or F152 oracles.

## 2. Current stationary request/reference state on `0x08A` and `0x081`

Short simultaneous reads of the relay pair gave, in the current no-request state:

- `0x08A` B21 low6 Target Lateral ID = `0`
- `0x08A` B18:B19 signed BE steering-reference word = `59`
- `0x081` B13 Target Lateral ID mirror = `0`
- `0x081` B16:B17 signed BE steering-reference word = `59`

Thus the current upstream request/reference and chassis-side return/reference agree exactly in this stationary state.

This is consistent with retained-drive evidence that `0x081` carries the same state/reference family as `0x08A`, but this live observation alone does not decide whether `0x081` is an arbitration result, acknowledgement, or another chassis state publication.

## 3. `CommunicationControl` source-attribution method

UDS packing was checked against `tools/toyota_diag/cli.py` before use.

For each tested ECU:

1. enter extended session: `10 03`
2. disable normal Tx while retaining normal Rx: `28 01 01`
3. passively count/inspect target CAN IDs for about one second
4. restore normal communication: `28 00 01`
5. return to default session: `10 01`

In default session, FRC `28 01 01` returned `7F 28 7F`; after `10 03`, the same request returned positive `68 01`. This is why the extended-session step is required.

### Stationary precondition

Immediately before the first mutating source-isolation test:

`Brake DID 0x1042 = 0000 = 0.0 km/h`.

## 4. FRC normal-Tx dependency of `0x08A`

Baseline native upstream-side `0x08A` rate was approximately 98 frames/s during the one-second count.

FRC sequence:

- `10 03 -> 50 03 00 32 01 F4`
- `28 01 01 -> 68 01`
- during suppression: **0 `0x08A` frames observed** in the one-second native-side sniff
- `28 00 01 -> 68 00`
- `10 01 -> 50 01 00 32 01 F4`
- after restore: approximately 99 `0x08A` frames/s

**Direct conclusion:** `0x08A` is dependent on FRC normal Tx. The FRC is upstream source/owner of the information flow necessary for `0x08A` publication.

**Do not overstate:** because current GTS topology puts FRC on Bus 1 while protected `0x08A` is on the relay/bus-4 plane and FRC is not a TSK key-holder, this experiment does **not** by itself prove that the FRC CAN controller physically emits/signs `0x08A`. A downstream gateway/proxy can stop its publication when FRC source traffic is disabled.

## 5. Brake normal-Tx dependency of `0x081`

Baseline native chassis-side `0x081` rate was about 82 frames/s.

Brake sequence:

- `10 03 -> 50 03 00 32 01 F4`
- `28 01 01 -> 68 01`
- during suppression: effectively zero `0x081` (1 frame at the transition boundary)
- restore communication and default session
- after restore: about 80 `0x081` frames/s

**Direct conclusion:** `0x081` is dependent on Brake/EPB normal Tx. Since Brake is itself a native chassis/bus-4 participant, this is strong live evidence that Brake owns the chassis-side `0x081` publication path. Physical-CAN-driver language can be tightened later with topology/firmware if desired.

## 6. Brake actively supervises loss of FRC request traffic

A second experiment disabled FRC normal Tx for roughly two seconds while leaving Brake active and recording native chassis-side `0x081`.

Before FRC suppression:

- 83 `0x081` frames
- B13 state: all `0`
- B16:B17 reference: all `59`
- B11: all `0x04`

During FRC suppression:

- Brake **continued publishing** `0x081` (113 frames in the captured interval)
- B13 state remained `0`
- B16:B17 reference remained `59`
- **B11 changed from `0x04` to `0x14`** after two transition frames

After FRC traffic returned:

- `0x081` continued normally
- B13 remained `0`
- B16:B17 remained `59`
- **B11 returned to `0x04`**

The only clean request-loss-specific application change found in this short stationary interval was B11 `+0x10`.

**Direct conclusion:** Brake is not merely relaying/echoing `0x08A`. It continues its own `0x081` publication when the FRC request stream is absent and sets `0x081 B11[4]` in direct response to that loss. This is a live chassis supervision/validity/failsafe indicator. OEM name remains unknown.

This is currently one of the strongest concrete communication-graph results:

`FRC-source request flow -> protected 0x08A publication -> Brake consumes/supervises -> Brake-owned 0x081 return publication`

with `0x081 B11[4]` acting as a request-loss response in the tested stationary state.

## 7. Reciprocal loss of Brake `0x081`

Brake normal Tx was briefly suppressed and FRC DIDs `0x1501`, `0x1601`, `0x1703`, and `0x1C81` were read before/during/after.

Those four high-level FRC Data List states did not change during the short suppression interval; they were already in the same disabled lateral state before the test.

This is **not** evidence that FRC does not supervise `0x081`; the chosen high-level DIDs may be too coarse, latched, already-disabled, or not the relevant return-channel diagnostic. Operation FFD / DTC / raw-state observation is the better next discriminator.

## 8. Surrounding Bus-4 publication ownership fingerprints

A one-second normal-Tx suppression fingerprint was run for FRC, Brake, and EPS while counting:

`0x00F, 0x081, 0x08A, 0x090, 0x0D7, 0x371, 0x412, 0x030`.

Representative baseline counts:

- `0x00F`: 23
- `0x081`: 76
- `0x08A`: 92
- `0x090`: 231
- `0x0D7`: 116
- `0x371`: 11
- `0x412`: 2
- `0x030`: 229

With **FRC normal Tx suppressed**:

- `0x08A`: 0
- `0x371`: 0
- `0x412`: 0
- `0x081`, `0x090`, `0x0D7`, `0x030`, `0x00F`: continue

With **Brake normal Tx suppressed**:

- `0x081`: 0
- `0x090`: 0
- `0x0D7`: effectively 0 (one transition-boundary frame)
- `0x08A`, `0x371`, `0x412`, `0x030`, `0x00F`: continue

With **EPS normal Tx suppressed**:

- `0x030`: 0
- all of `0x08A`, `0x371`, `0x412`, `0x081`, `0x090`, `0x0D7`, `0x00F`: continue

So the live **source-dependency groups** are:

- **FRC-dependent group:** `0x08A`, `0x371`, `0x412`
- **Brake-dependent group:** `0x081`, `0x090`, `0x0D7`
- **EPS-owned group:** `0x030`
- **none of those three:** `0x00F`

Again, the FRC-dependent group should not yet be labeled as physically transmitted by the FRC on Bus 4; it may be a downstream proxy publication of FRC-owned state.

### Other responding ECU candidates

The same `CommunicationControl` experiment against these responding endpoints did **not** suppress `0x08A` or `0x00F`:

- `ecu_7a2` — F181 payload identifies `867BF0601001`; DID0105 `867B006210B0`
- `ecu_7b3` — F181 payload identifies `8924G0401000`; F18C `892450401000262J260D`; DID0105 `8924504010`
- `ecu_7d0` — F18C `86100AQ010CBAABLRQNM`; DID0105 `86100AQ010`
- Engine
- Motor/Generator
- Hybrid Control
- HV Battery
- Air Conditioner

Therefore the still-running `0x00F` synchronization source and any distinct physical Bus-4 proxy for the FRC-dependent group were not identified among the CommunicationControl-capable responding ECUs tested here. Central Gateway / a non-addressed proxy remains a leading physical-publication candidate, but that is not yet proven by this experiment.

## 9. Live TSS3 Operation FFD access works

This is a major live tooling result.

Current recovered native protocol was exercised directly against FRC `0x792`:

### Behavior/RoB enumeration

Request:

`AB 11`

Response:

`EB11 20DC 2818 2844 2847 2090 2098 22B1 2279 2292 2294 227C 2272 2273 2274 2033`

So the live FRC currently has 15 Operation-FFD behavior/RoB codes available.

Known names from the recovered PCS Data Viewer dictionary include:

- `0x20DC` — Lane Departure Warning Operation
- `0x2818` — Steering Angle Speed Threshold Exceeded
- `0x2844` — Lane Departure Warning Operation under LTA
- `0x2847` — BSM-LDA Combination Operation
- `0x2090` — ALM Request Flag
- `0x2098` — PBA Request Flag
- `0x2279` — PDA(OAA) Large longitudinal acceleration
- `0x2292` — PDA(DA) sudden-steering RoB memory trigger
- `0x2294` — PDA(DA) additional-brake-by-driver RoB trigger
- `0x2033` — AHBAHS Manual Override Trigger

The special-behavior codes `0x2272/0x2273/0x2274/0x227C/0x22B1` are present as expected from the recovered current plugin's special-behavior family even where a concise English trigger name has not yet been pulled into this notebook.

### Record enumeration

`AB12 || behavior_be16` successfully enumerated record IDs for all tested behaviors. Examples:

- `20DC -> records 0001,0002,0003`
- `2818 -> 0001,0002,0003, then 0100..0114, 0300..0314`
- `2844 -> 0001,0002, 0100..0109, 0200..0209`
- `2847 -> 0001`
- `2090 -> 0001,0002, 0100..0131, 0200..0231`
- `2098 -> 0001`
- `22B1 -> 0001, 0100..0195`
- `2279 -> 0001, 0100..0159`
- `2292 -> 0001,0002, 0100..0145, 0200..0245`
- `2294 -> 0001, 0100..0122`
- `227C -> 0001,0100`
- `2272 -> 0001..0006`
- `2273 -> 0001..0003`
- `2274 -> 0001..000A`
- `2033 -> 0001..0008 plus 0100..010B through 0800..080B`

This confirms the recovered `AB11/AB12/AB13 -> EB11/EB12/EB13` protocol is directly usable on the actual car.

## 10. First fetched live lateral Operation-FFD record

A representative lateral record was fetched:

- behavior `0x2818` = **Steering Angle Speed Threshold Exceeded**
- record `0x0100`
- request: `AB 13 2818 0100`
- positive response: `EB 13 2818 0100 ...`

The EB13 payload parsed according to the recovered contract (`data_id_be16 || length_u8 || data[length]`) and visibly contains the critical lateral Data IDs, including:

- `0x5265` — active-steering/grant family
- `0x560D` — EPS Pinion Angle
- `0x5631` — LTA request tuple

The same response also contains many surrounding TSS3/vehicle-state Data IDs (`52xx`, `55xx`, `56xx`, etc.). Full semantic decode of this fetched record was the task in progress when live probing was stopped for the vehicle restart.

Raw response retained here for lossless continuation:

```text
eb13281801005c05010700f60087b1670105020402000339050706260809002229520102c0805203028000522701005230044268624152310201015232044269ae14523301015234028000523504426eafad5236010152370101523804c006eb2652390101523a08beb4c195bea0ac13523b020101523d04c0400000523e0101523f04424800005240010152440100524604bd3c6a8052470a3ffeb852013eeb851f0152650e80008000800080008000800080005267020000526a020403526c03030000526d02f800527002000052710100527501005276010052770101530102c0c0534801005501020100550503010000550906ffdefffff810550d0b0000030000000000000000551102010055120200005513020000551403010102551503000000551604000000005517010055210201015522020000552303010001552403010200552502010155310500ffc764005532010055390100553a048a780101553b04000f0000553c0100553d0100553e0206005541020302554204b97f70a3554310000000007f7f81810000000081817f7f5549103e8116a1000000003c4612053a4c8c3056010401000000560503010000560902f8c0560d07020001ffc70000561101015612020000561302000056150200005621010156220400000000563105000000000056320400000000563309000000000000000000563401045639010056810200005685030000005689028000568d1e00000000030000fefefefffe00fe00fe00fe00fe00fe00fe00fe00010101568e01005691010056920200005693020000569405000000000056950300000056a102000056c1020f00
```

### Immediate decode anchors already known from the recovered PCS schema

Use the current PCS dictionary, not guesses:

- `5282`: generic TSS lateral request — byte1 lateral ID, bytes2:3 signed pinion request at 0.001, bytes4/5 assist+damping gains at 0.01
- `5631`: LTA request tuple — same 5-byte geometry as `5282`
- `5285`: arbitration-result lateral ID
- `57DE`: arbitration-result pinion angle, signed16 at 0.001
- `5265`: active-steering/grant record family
- `560D`: EPS Pinion Angle, signed bytes4:5 at 0.001

The fetched `2818/0100` record visibly contains `5265`, `560D`, and `5631`; next step is to parse all blocks programmatically and decode these exact fields plus search the same record/neighboring records for `5282`, `5285`, and `57DE`.

## 11. Working communication graph at stop point

The graph supported by this live session, keeping proof levels separate, is:

```text
FRC internal TSS3 logic
  |  (live Operation FFD serves request/result/grant/plant snapshots)
  |
  +-- FRC normal-Tx dependent request/state flow
          |
          +--> 0x08A protected request publication (physical proxy/signing point still unresolved)
          +--> 0x371 state publication (same FRC dependency)
          +--> 0x412 state publication (same FRC dependency)
                    |
                    v
              Brake/chassis domain
                    |
                    +-- consumes/supervises FRC request flow
                    |     `0x081 B11[4]` asserts when FRC 0x08A disappears
                    |
                    +--> 0x081 Brake-dependent return/reference publication
                    +--> 0x090 Brake-dependent publication
                    +--> 0x0D7 Brake-dependent protected publication

EPS
  +--> 0x030 native EPS telemetry/status publication

unknown/non-tested physical sync owner
  +--> 0x00F global SecOC synchronization
```

The major new fact is not merely correlation: **FRC source traffic and Brake return traffic can now be independently removed with positive UDS CommunicationControl responses, and the remaining ECU reacts.** This directly establishes a supervised FRC→chassis/Brake request relationship plus a Brake→upstream return publication.

## 12. Resume checklist after car restart

Do not repeat broad discovery. Resume exactly here:

1. Confirm car is stable and stationary; do a passive `0x08A/0x081/0x030` health check first.
2. Parse the already-fetched `2818/0100` EB13 response offline before sending anything else.
3. Decode exact values for `5265`, `560D`, `5631`; locate `5282`, `5285`, `57DE` in this or neighboring `2818` records.
4. Fetch a small number of **existing** recent LTA-relevant records (`2844` is especially valuable) and decode the same six Data IDs.
5. If we need live causal ordering, synchronize Operation-FFD reads with passive CAN only; avoid unnecessary mutation.
6. Investigate `0x081 B11[4]` OEM identity via Brake/GTS/firmware separately; its live behavior is already clear.
7. Physical `0x08A` signer/proxy remains unresolved. The source dependency points to FRC; tested FRC/Brake/EPS/three unknown responders/powertrain nodes do not identify a separate Bus-4 publisher. Central Gateway/non-addressed proxy remains a hypothesis, not a finding.

