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


## 13. Post-restart continuation: corrected EB13 parser and first exact lateral decode

After the vehicle restart, passive health was normal and stationary:

- Brake DID `0x1042` Vehicle Speed (Control Value): `0.0 km/h`
- 2 s passive chassis-bus census: `0x030=330`, `0x081=111`, `0x08A=132`

The saved `AB13 2818 0100` response was re-parsed offline. Important parser correction: after the six-byte `EB13 || behavior_be16 || record_be16` header, the next byte is the **block count**. In this response it is `0x5C = 92`; the DID stream begins at byte 7, not byte 6. Parsing exactly 92 `data_id_be16 || length_u8 || data[length]` blocks consumes the response with no trailing bytes.

Critical lateral blocks in behavior `0x2818` record `0x0100`:

- `0x5265`, len 14: `8000800080008000800080008000`
  - current PCS bit assignments place the seven under-control flags at byte positions 2,4,...,14 bit7 (1-based positions); all are clear here, including **Active steering under-control flag = 0**.
- `0x560D`, len 7: `020001ffc70000`
  - Driver Steering Control Detection Status = `0x02`
  - LTA Driver Steering Control prohibited = `0x00`
  - LTA DDR Control State = `0x01`
  - EPS Pinion Angle raw `0xFFC7` = `-57`, physical `-0.057` at the recovered 0.001 scale
  - following flags = `0,0`
- `0x5631`, len 5: `0000000000`
  - LTA Lateral ID = `0`
  - LTA Control Request Pinion Angle = `0`
  - LTA Steering Assist Gain = `0`
  - LTA Damping Control Gain = `0`
- `0x5282`, `0x5285`, `0x57DE`: not present in this particular stored record.

Interpretation for this snapshot only: the stored steering-angle-speed event records a nonzero EPS pinion angle, but no active LTA feature request and no active-steering grant at the sampled instant. This is internally coherent and is not evidence against active LTA in other records.

Next read-only target: existing `0x2844` (**Lane Departure Warning Operation under LTA**) records, especially the `0x0100..0x0109` series, searching for `5282/5285/57DE/5265/560D/5631` together.

## 14. `0x2844` stored LDA-under-LTA records: feature request follows EPS pinion

Four representative stored records from behavior `0x2844` (**Lane Departure Warning Operation under LTA**) were fetched and parsed with the corrected EB13 block-count rule.

All four contain:

- `0x5531` LDA request tuple active as lateral ID 11;
- `0x5631` LTA request tuple all zero;
- `0x5265` under-control family with all seven recovered flags clear at the snapshot instant;
- `0x560D` EPS Pinion Angle numerically very close to the LDA requested pinion angle;
- no `0x5282`, `0x5285`, or `0x57DE` in this record family sample.

| record | `5531` raw | LDA ID | requested pinion | assist | damping | `560D` EPS pinion |
|---|---|---:|---:|---:|---:|---:|
| `0100` | `0b006e6400` | 11 | +0.110 | 1.00 | 0.00 | +0.111 |
| `0109` | `0b00876400` | 11 | +0.135 | 1.00 | 0.00 | +0.115 |
| `0200` | `0b00556400` | 11 | +0.085 | 1.00 | 0.00 | +0.101 |
| `0209` | `0b00496400` | 11 | +0.073 | 1.00 | 0.00 | +0.071 |

Important distinction: this trigger name contains “under LTA”, but Toyota's own stored feature request is `5531` **LDA**, not `5631` LTA. ID11 is a lateral request identity used across feature/arbitration layers; it must not be casually equated with one feature-local recorder tuple.

## 15. Sparse live Operation-FFD family census: generic request and arbitration result

To avoid brute-forcing hundreds of stored FFD frames, one existing record was sampled from each of the 15 currently enumerated behavior families. The lateral-bearing families split cleanly.

Representative feature-state families:

- `20DC/0001`: `5531=0b00496400`, `560D` pinion `+0.121`; no `5282/5285`.
- `2818/0001`: `5531=00fe726400`, `560D` pinion `-0.398`; no `5282/5285`.
- `2844/0001`: `5531=0b006e6400`, `560D` pinion `+0.100`; no `5282/5285`.
- `2847/0001`: `5531=0400416400`, `560D` pinion `+0.063`; no `5282/5285`.

Generic/arbitration-bearing families:

- `22B1/0001`: `5285=00`; no `5282` in this sampled record.
- `2279/0001`: `5282=00ffc96400`, `5285=00`
  - generic request ID 0, pinion `-0.055`, assist `1.00`, damping `0.00`
  - arbitration-result lateral ID 0
- `2292/0001`: `5282=0006b70000`, `5285=00`
  - generic request ID 0, pinion `+1.719`, assist/damping 0
  - arbitration-result lateral ID 0
- `2294/0001`: `5282=1200173200`, `5285=12`
  - generic request ID **18 (SDG)**, pinion `+0.023`, assist `0.50`, damping `0.00`
  - arbitration-result lateral ID **18 (SDG)**

The `2294/0001` snapshot is the first direct same-record live-car witness that the FRC-hosted Operation FFD contains both a generic lateral request and a matching arbitration-result lateral ID. It establishes the request/result distinction as active recorder data on this car, not merely a static PCS schema distinction.

Far-end samples of those same generic/arbitration families (`22B1/0195`, `2279/0159`, `2292/0245`, `2294/0122`) also contain `5285` and where applicable `5282`, but still no `57DE`. Across the one-per-family census, no currently stored behavior sample contains `57DE`. Working interpretation: the present stored trigger set logs arbitration-result ID but not the separate arbitration-result pinion-angle datum; do not brute-force all records unless another reason emerges.

## 16. Central Gateway middlebox check started

Current GTS+ resolves category **443 = Central Gateway**, database `CentralGW_P5.ddb`, generation 20. Its current plugin surface is ordinary diagnostics/monitor/RoB support and does not expose steering/lateral routing vocabulary. The next middlebox task is to recover/resolve its live diagnostic address or otherwise identify whether the CGW can be independently CommunicationControl-isolated. FRC-source dependence of `0x08A` does not by itself prove that the FRC CAN controller physically emits the protected Bus-4 PDU.

## 17. Post-restart FRC health with replacement `0x08A` still active

After restart, with the current openpilot `0x08A` replacement path still installed and emitting inactive ID0 replacements, the FRC diagnostic state returned to healthy/enabled:

- `10AF = 00`: ECU Security Key Registered Incomplete Flag = OFF
- `1501 = 01 00`: LDA Customize ON, **LDA Enabled**
- `1601 = 01 00 00 00`: LTA switch ON, **LTA Enabled**, Hands-Off control enabled
- `1703 = F0 00`: PCS Availability Flag Output Signal = **Enabled**
- `1705 = FF 00`: PCS AES Invalid Flag = OFF; the other decoded PCS invalid flags are also OFF
- `1681` is unsupported on this exact calibration in the tested session (NRC requestOutOfRange)

This sharply weakens the earlier simple model “replacement `0x08A` with a non-stock trailer is continuously rejected and therefore keeps ADAS faulted.” The same replacement remains present after restart while FRC lateral/PCS conditions are enabled. A failure that appears only on an active ID11 steer attempt, request/result mismatch, freshness transition, or another transient supervision condition remains plausible.

The pre-restart disabled state is retained as a real observation but not attributed solely to the inactive replacement frame.

## 18. Important correction: direct-Panda state, split mirroring, and post-restart health attribution

Two interpretations made during the continuation were corrected immediately after checking the actual comma transport state and doing a simultaneous all-bus capture.

### 18.1 `pandad` is stopped; post-restart FRC health was not observed with CarController replacing `0x08A`

`./tools/toyota transport status` reports:

- `pandad: stopped`
- mode `direct-panda`

In this mode the Toyota CLI claims Panda directly and `transport.connect()` sets ELM327 safety for diagnostics. The normal openpilot `pandad`/`sendcan` path is therefore not running, so the normal CarController replacement sender is not actively emitting `0x08A` during these diagnostic observations.

Therefore §17's initial wording that the healthy post-restart FRC state was observed “while the replacement `0x08A` remained actively emitted” was wrong. The correct fact is narrower: after restart, in direct diagnostic Panda state, FRC LDA/LTA/PCS state is healthy/enabled.

This also means the pre-restart fault cannot yet be attributed by comparing that healthy state against a supposedly still-running replacement sender.

### 18.2 Sequential bus0/bus2 trailer differences were a time-pairing artifact, not re-signing

Sequential one-second captures of `0x08A` on bus0 then bus2 naturally contained the same recurring application states at different freshness/MAC publications. Comparing equal modulo-64 sequence values across those non-simultaneous windows produced different trailers and briefly suggested a re-authentication stage at the Panda split. That inference was wrong.

A single receive-only simultaneous all-bus capture through the Toyota transport layer settles the boundary exactly. Ordered bus0/bus2 streams are 1:1 identical at zero index shift:

- `0x08A`: 139 bus0 / 139 bus2; **139/139 full 32-byte frames identical**
- `0x081`: 115 / 115; **115/115 full 32-byte frames identical**
- `0x00F`: 35 / 35; **35/35 full 8-byte frames identical**

No +/-1..3 frame offset reproduces equality for `0x08A`; zero shift alone is exact. `0x081` application bytes are static in the parked sample, but only zero shift gives full trailer equality. `0x00F` likewise aligns exactly at zero shift.

Correct interpretation: **the Panda bus0/bus2 boundary forwards these protected frames byte-for-byte; it is not the signer/re-signer boundary.** This matches the earlier relay-open direction finding:

- protected `0x08A` is native upstream/bus2 and forwarded unchanged to bus0;
- protected `0x081` is native chassis/bus0 and forwarded unchanged to bus2;
- `0x00F` is likewise mirrored unchanged across the split in the current state.

The physical SecOC generation point for `0x08A` is therefore **upstream of the accessible Panda split**. FRC CommunicationControl still proves that `0x08A` publication depends on FRC normal Tx, but because GTS+ places FRC on Toyota Bus 1 and recovered FRC-side periodic traffic is E2E-P05 rather than SecOC, that dependency does not by itself prove the FRC CPU/HSM physically signs or emits the protected Bus-4 `0x08A` frame.

The working graph remains: FRC source/request logic -> unresolved upstream proxy/signer -> protected `0x08A` -> byte-for-byte Panda relay -> Brake/chassis consumer; Brake publishes protected `0x081` in the reverse direction and its B11[4] missing-request state responds when the `0x08A` source stream disappears.

## 19. Direct Bus-1 transmitter attribution: only four frequent periodic streams are FRC Tx

The direct diagnostic state initially left Panda in ELM327 param0, whose board behavior multiplexes bus1 to OBD and therefore made `toyota can sniff --bus 1` empty. Panda source confirms:

- ELM327 `param==0` -> `CAN_MODE_OBD_CAN2`
- ELM327 `param!=0` -> `CAN_MODE_NORMAL`
- both remain no-output diagnostic safety and do not enable normal control TX.

A single direct-Panda process therefore used the already-established ELM327 param1 normal-CAN observation mode, captured one second of Bus 1, entered FRC extended session, applied UDS CommunicationControl `28 01 01` (normal Rx enabled / normal Tx disabled), captured one second, restored `28 00 01`, returned FRC to default session, captured again, and finally restored Panda ELM327 param0.

The result is exact at the one-second rate scale:

| ID | baseline | FRC Tx disabled | restored | attribution |
|---|---:|---:|---:|---|
| `0x020` | 20 | **0** | 20 | **FRC normal Tx** |
| `0x160` | 40 | **0** | 40 | **FRC normal Tx** |
| `0x230` | 20 | **0** | 20 | **FRC normal Tx** |
| `0x440` | 2 | **0** | 2 | **FRC normal Tx** |
| `0x123` | 10 | 10 | 10 | non-FRC |
| `0x180..0x18A` | ~20 each | ~20 each | ~20 each | non-FRC |
| `0x18B/0x18C/0x1A0` | ~19-20 | ~20 | 20 | non-FRC |
| `0x200/0x201` | 10 | 10 | 10 | non-FRC |
| `0x450` | 2 | 2 | 2 | non-FRC |

Sparse baseline-only `0x45A` (2 frames) and `0x4E0` (1 frame) vanished during FRC-off but also did not recur in the one-second restored window, so they are **not** assigned from this short sample.

Consequences:

1. The former 22-stream Bus-1 candidate set collapses to **four frequent FRC-origin E2E-P05 PDUs**: `0x020/12`, `0x160/32`, `0x230/64`, `0x440/32`.
2. The object-track family `0x180..0x18C` is positively **not** transmitted by the FRC under CommunicationControl. This resolves the earlier FRC-vs-radar ownership ambiguity for the frequent family at least at the FRC/non-FRC split.
3. `0x160` is now directly isolated as an FRC normal-Tx PDU. Its previously recovered longitudinal relationship to protected chassis `0x0CA` is therefore much stronger architectural evidence for an FRC-source -> downstream protected-publication path.
4. The unknown lateral handoff, if it uses a frequent ordinary Bus-1 FRC PDU, is now constrained to `0x020`, `0x160`, `0x230`, or `0x440` rather than all 22 frequent streams. Prior single-field sweeps still say no simple scalar copy of downstream `0x08A` was found; this attribution does not change that negative, but it radically narrows multivariate/multiplexed/state-machine work.

## 20. FRC CommunicationControl owns an entire protected upstream Bus-4 publication domain

A two-second all-bus census under ELM327 param1 compared baseline, FRC normal-Tx disabled (`10 03`, `28 01 01`), and restored (`28 00 01`, `10 01`). On bus0/bus2, **47 recurring ID/DLC streams drop to zero while FRC normal Tx is disabled and return on restore**. This includes:

`08A/32, 0C9/32, 13F/8, 159/8, 15A/8, 198/8, 19C/8, 19F/1, 1B1/8, 1B2/32, 1BC/8, 1D9/8, 1DE/8, 1DF/8, 20F/8, 251/8, 252/8, 261/8, 274/32, 275/8, 276/8, 277/8, 27B/8, 27C/8, 28A/8, 28B/8, 28C/8, 28D/8, 317/8, 36D/8, 371/32, 411/8, 412/8, 414/8, 489/8, 48A/8, 48B/8, 494/8, 4D3/8, 5AE/32, 5AF/32, 5F1/8, 5F6/8, 5F7/8, 5F9/8, 608/8, 68D/8`.

The existing relay-open route `0000002d--4a4806c524` was then re-read directly from all six local rlogs. **Every one of these FRC-suppressed streams has the same physical direction:** overwhelmingly native Panda bus2 RX, with the corresponding bus0 copy present as returned software-forwarding TX echo. A few bus0 RX frames occur around startup only.

Representative route counts:

| ID | native bus2 RX | forwarded bus0 TX echo | native bus0 RX |
|---|---:|---:|---:|
| `0x08A` | 12,960 | 12,486 | 473 |
| `0x0C9` | 10,128 | 9,755 | 372 |
| `0x13F` | 6,482 | 6,243 | 237 |
| `0x371` | 1,719 | 1,658 | 61 |
| `0x5AE` | 1,697 | 1,636 | 61 |
| `0x5AF` | 1,621 | 1,561 | 59 |

The full 47-ID list reproduces this same direction.

### Architectural consequence

This materially supersedes the weaker “FRC request -> unknown external proxy -> protected `0x08A`” working model.

The live FRC diagnostic endpoint's standard UDS CommunicationControl governs **both**:

1. four frequent native Bus-1 E2E-P05 FRC Tx streams (`020/160/230/440`), and
2. a large native-upstream/bus2 Bus-4 publication domain that includes protected `0x08A` and many ADAS/cruise/state PDUs.

The most natural hardware interpretation is a **multi-interface FRC ECU/assembly**: perception/control-side traffic is exposed on Toyota Bus 1 with ordinary AUTOSAR E2E P05, while a chassis-facing network/security side of the same diagnostic ECU boundary publishes the protected Bus-4 family. This network/security side can contain the SecOC/TSK capability even if the previously considered main FRC compute silicon does not.

This interpretation also resolves why `0x08A` disappears immediately under FRC CommunicationControl without requiring a separately diagnosed downstream proxy ECU to honor that command.

Keep one distinction: UDS CommunicationControl proves the protected bus2 transmitter lies under the FRC diagnostic/ECU boundary; it does not yet identify the exact internal MCU/HSM within the camera assembly. For integration purposes, however, **stock protected `0x08A` is an FRC-owned output domain**, not an independently controlled Brake/gateway output.

## 21. Symmetric Brake/EPB transmitter attribution: 15 native chassis/bus0 publications

The same two-second CommunicationControl census was run against category-435 Brake/EPB (`0x7B0`) under ELM327 param1. Brake normal-Tx disable removes exactly these recurring bus0/bus2 streams and restore brings them back:

`081/32, 090/32, 0AA/8, 0C6/8, 0D5/8, 0D7/32, 0D8/8, 101/8, 129/8, 13B/8, 13C/8, 1D5/8, 3B7/8, 420/8, 427/8`.

The relay-open route `0000002d--4a4806c524` shows the exact opposite direction from the FRC-owned family: every Brake-suppressed stream is overwhelmingly **native Panda bus0 RX**, with its bus2 copy present as returned forwarding TX echo.

Representative counts:

| ID | native bus0 RX | forwarded bus2 TX echo | native bus2 RX |
|---|---:|---:|---:|
| `0x081` | 10,802 | 10,406 | 398 |
| `0x090` | 32,408 | 31,217 | 1,197 |
| `0x0AA` | 32,406 | 31,218 | 1,194 |
| `0x0D7` | 16,204 | 15,609 | 598 |
| `0x101` | 16,204 | 15,610 | 599 |
| `0x13B` | 10,804 | 10,406 | 399 |

This gives a direct two-domain topology rather than an inferred one:

```text
FRC diagnostic/ECU boundary
  native upstream bus2 -> chassis:
    47-ID protected/state domain, including 0x08A

                [Panda relay split]

Brake/EPB diagnostic/ECU boundary
  native chassis bus0 -> upstream:
    15-ID domain, including 0x081, 0x090, 0x0D7, 0x101

EPS
  native chassis bus0 -> upstream:
    separate EPS domain, including 0x030
```

The previously observed `0x081 B11[4]` change when FRC Tx disappears is therefore a Brake-owned upstream return/supervision state reacting to loss of the FRC-owned downstream request domain. It is not an EPS echo.

## 22. `0x081 B11[4]` is a dedicated FRC-request supervision state, not ordinary Brake comm-open status

A before / FRC-normal-Tx-off / restored modal-byte comparison was run over the major Brake-owned return PDUs while parked. Among:

`081, 090, 0AA, 0C6, 0D5, 0D7, 0D8, 101, 129, 13B, 13C`

the only stable dominant application-byte transition that asserted under FRC silence and cleared after FRC restore was:

- **`0x081 B11: 0x04 -> 0x14 -> 0x04`**
  - baseline dominance: 100%
  - FRC-off dominance: 96%
  - restored dominance: 100%
  - exact changed bit: **B11[4]**

The other inspected Brake-owned PDUs retained their dominant parked application state. This makes `0x081 B11[4]` a very specific supervision/validity response to loss of the FRC-owned publication domain rather than a generic Brake failsafe mode.

Current ABS_P5 ordinary Data List vocabulary contains many communication-open diagnostics in DID `0x102F`, but no explicit FRC/TSS communication-open item. A live exact check confirms the distinction: Brake DID `0x102F` is exactly `f700fd007c00a9000000` before FRC Tx suppression, during FRC Tx suppression, and after restore, with every decoded communication/open item still `Normal` (including Steering Open, Brake ECU Communication Open, and EPS/Steering Control Actuator ECU Communication Open).

Therefore `0x081 B11[4]` is **not** the ordinary Brake `0x102F` communication-open bitmap. Keep it structurally named for now as the FRC/request-domain supervision/validity bit until a direct OEM name is found.

## 23. Reciprocal Brake-off check became intentionally contaminated; stop live suppression here

A reciprocal experiment was attempted: with the vehicle confirmed at `0.0 km/h`, read FRC `1501/1601/1703/1705`, suppress Brake normal Tx, wait two seconds, read the same FRC DIDs, restore Brake, and read again.

The experiment cannot distinguish the effect of losing `0x081`, because **before Brake suppression began** the FRC had already returned to the communication-faulted state after the preceding sequence of intentional ECU Tx-suppression fingerprints:

- `1501 = 01 01`: LDA Disabled
- `1601 = 01 01 00 00`: LTA switch ON, LTA Disabled
- `1703 = F0 20`: PCS Availability Disabled
- `1705 = FF 3A`: PCS PB / ESA / AES / PAS-A Invalid flags asserted; PCS AES Invalid Flag = ON

These values remained the same during and after the short Brake-Tx suppression, so the reciprocal test is **inconclusive**, not negative.

Brake was returned to default session; an explicit `28 00 01` attempted after the diagnostic session had already dropped returned NRC `0x7F`, but returning to default succeeded and a subsequent passive check confirmed `0x081` is again flowing normally (5/5 requested frames observed immediately).

A final read-only DTC snapshot records the expected consequence of the characterization campaign: **31 fault-status communication records** are now active across the vehicle. These are dominated by `Uxxxx87` lost-communication faults and were induced by deliberately suppressing normal Tx from FRC, Brake, EPS, and other candidate ECUs while mapping transmitter ownership / the `0x00F` owner. Examples include:

- FRC: U029387, U010087, U110687, U013187, U012687, U012987 (`status 0x28`, confirmed / failed-since-clear)
- EPS: U012987 Lost Communication with Brake System Control Module (`0x28`)
- Brake: U010087, U012687, U029300, U111A87, U012987, U029387, U115087, U013187 (mostly `0xAC`, warning requested)
- Engine/Hybrid/powertrain peers similarly record expected missing-message faults from the earlier ownership fingerprints.

This DTC storm means the current FRC disabled/AES-invalid state must **not** be attributed to the openpilot `0x08A` steering experiment. The live characterization itself intentionally removed whole ECU Tx domains and is now the immediate confounder.

**Stop point:** do not perform additional CommunicationControl / Tx-suppression experiments in this ignition cycle. The communication graph is sufficiently characterized to move back to offline reasoning and targeted implementation work. A vehicle restart/normal communication recovery should precede any later active-steering experiment; DTC clearing is a separate maintenance action and was not performed here.

## 24. Working communication model after live characterization

The combined source isolation, relay-open direction, and Operation-FFD data now support a much simpler working model than the previous external-proxy picture:

```text
                    FRC / Front Recognition Camera 2
                    diagnostic boundary: 0x792

      feature planners / TSS3 recorder state
      5531 LDA request
      5631 LTA request
               |
               v
      5282 generic lateral request
               |
        arbitration state
      5285 result lateral ID
      57DE result angle (schema present; not in current stored records)
               |
               v
    +-----------------------------------------+
    | FRC assembly has at least two CAN planes|
    |                                         |
    | Bus 1 normal/E2E-P05 Tx:                |
    |   0x020, 0x160, 0x230, 0x440            |
    |                                         |
    | chassis-facing protected Tx domain:     |
    |   47 recurring PDUs                     |
    |   including protected 0x08A             |
    +-----------------------------------------+
               |
               | 0x08A lateral request/reference
               | native upstream Panda bus2
               v
        [accessible Panda relay split]
               |
               v
                    Brake / ABS / VSC domain
                    diagnostic boundary: 0x7B0
               |
        consumes/supervises FRC request plane
               |
               +----> local chassis steering-authority handoff -> EPS internals
               |          (exact final transport remains unresolved)
               |
               +----> 0x081 protected return/reference/supervision
               |     native chassis Panda bus0 -> upstream
               |     B13 mirrors lateral ID family
               |     B16:B17 mirrors steering-reference family
               |     B11[4] asserts when FRC Tx/request domain disappears
               |
               +----> Brake-owned 15-PDU return/state domain

                    EPS / F33
                    diagnostic boundary: 0x7A1
               |
               +----> native chassis telemetry 0x030
               +----> Operation FFD observation 560D EPS Pinion Angle
               +----> exact firmware still does not receive 0x08A or 0x081
```

### What changed conceptually

The prior standing model treated the FRC as only the request-compute side and required an externally diagnosed Brake/Skid/CGW proxy to turn that request into protected `0x08A`. The live CommunicationControl census no longer supports that separation as the primary model. Standard FRC normal-Tx suppression removes the entire native-upstream protected `0x08A` publication family as well as the four Bus-1 FRC PDUs. The protected publisher is therefore inside the **FRC ECU/assembly diagnostic boundary**.

This does not require the main vision/control MCU itself to contain the Toyota TSK key/HSM. A multi-MCU FRC assembly with a separate network/security controller is entirely consistent with all observed facts and is now the leading hardware model. The old categorical statement “FRC cannot sign SecOC, therefore an external Brake/gateway proxy must sign `0x08A`” should be retired; at most, it applies to the previously considered main compute silicon, not the complete FRC assembly.

### `0x081` role

`0x081` is now best treated as **Brake-owned chassis result/reference/supervision feedback to the FRC side**:

- Brake CommunicationControl removes it;
- relay-open direction is chassis bus0 -> upstream bus2;
- its lateral ID and steering-reference word closely mirror `0x08A` during stock operation;
- it continues publishing when the FRC Tx domain is suppressed;
- its B11[4] status asserts specifically when the FRC request domain disappears;
- ordinary Brake communication-open DID `0x102F` remains normal during that condition.

That is exactly the shape expected from a receiver-owned result/validity publication rather than an EPS echo.

### Operation FFD fits the same loop

Toyota's own FRC-hosted recorder separates:

1. feature-local request (`5531`/`5631`),
2. generic lateral request (`5282`),
3. arbitration-result lateral ID (`5285`) and schema for result pinion (`57DE`),
4. active-steering under-control state (`5265`),
5. EPS pinion observation (`560D`).

The live stored data provides concrete examples of these stages, notably `2294/0001` where generic request ID18/SDG and arbitration-result ID18 coexist, and the `2844` records where LDA ID11 request pinion closely follows the EPS pinion snapshot.

The recorder host alone still cannot tell whether every result/grant field is computed locally or sampled from Brake/chassis return traffic. The newly identified `0x081` feedback loop makes the latter entirely plausible for result/validity state.

### Implication for the current openpilot steering experiment

The accessible relay split is **after stock `0x08A` has already been protected**. Blocking stock `0x08A` there and transmitting a modified replacement therefore bypasses the FRC assembly's normal SecOC-generation path. The existing EPS B6 acceptance patch is irrelevant to `0x08A`, because F33 receives neither `0x08A` nor `0x081`.

The highest-value next steering discriminator is no longer “find the external `0x08A` proxy.” It is one of:

- recover/use the FRC assembly's own protected `0x08A` generation/signing path;
- identify the exact Brake-side `0x08A` verification boundary and patch/satisfy it;
- or find an upstream controllable FRC-internal/request input that causes the FRC assembly itself to generate the desired signed `0x08A`.

The return-side `0x081` consistency loop should be watched on the first clean steering attempt because Brake clearly reports request-domain validity there.

### Current unresolved pieces

- exact internal FRC network/security MCU/HSM and the `0x08A` CMAC key/profile implementation;
- exact `0x00F` synchronization publisher (none of the 11 directly tested diagnostic ECUs owns it under CommunicationControl; category-443 Central Gateway has no normal phase-5 physical diagnostic address in the V18 table);
- exact Brake/chassis -> F33 local authority handoff that turns accepted lateral reference into the B6-independent EPS motor-control path;
- semantic OEM name for `0x081 B11[4]`;
- live active-LTA Operation-FFD snapshot containing `5265=active` and/or `57DE` result angle.

## Brake authenticated-execution characterization — initial SecurityAccess fingerprint

The exact Camry Brake/EPB endpoint remains category 435 `ABS_P5`, physical `0x7B0 -> 0x7B8`, F181 `F152633K0000`. Before attempting programming mode, the application diagnostic context was fingerprinted with request-seed operations only; **no `27 02` key was submitted**.

Car speed at the Brake oracle was `0.0 km/h`.

Observed wire results:

```text
default:  27 01                                      -> 7F 27 7F
default:  27 01 || 16*00                             -> 7F 27 7F
extended: 10 03                                      -> 50 03 00 32 01 F4
extended: 27 01                                      -> 7F 27 12
extended: 27 01 || 16*00                             -> 7F 27 12
default:  10 01                                      -> 50 01 00 32 01 F4
```

Interpretation for the next live step: application/default does not expose SecurityAccess in the active session (`0x7F`), and application/extended explicitly rejects subfunction 1 (`0x12`) independent of bare-vs-16-byte request shape. This does **not** determine the Brake bootloader SecurityAccess grammar. The directed next probe is `10 02` programming transition followed by boot-context identity/session/SecurityAccess/DID fingerprinting, mirroring the exact-F33 EPS methodology without assuming the EPS secret or RAM geometry transfers.

## Brake bootloader / ReproStd characterization checkpoint

The category-435 Brake/EPB application does not expose SA level 1, but programming session does:

```text
10 02 -> 50 02 00 32 01 F4
22 F1 81 -> 62 F1 81 01 || 16*21
27 01 -> 67 01 || seed[16]
27 01 || 16*00 -> 7F 27 13
```

This is the recovered CUW **ReproStd** SecurityAccess grammar, not the exact-F33 EPS Unified grammar. Techstream's recovered host construction is:

```text
Kwork = AES-128-ECB-DEC(B45B26D6344FD60E80BC01D63C7584A0, ServiceAuthKey[16])
27 02 payload = AES-128-ECB-ENC(Kwork, ECU_seed[16])
```

All eight effective ReproStd working keys currently available in the local CUW corpus were tried against fresh live Brake seeds with the observed ~10 s retry interval. None authenticated (`7F 27 35` / `7F 27 36`). The tested families were 0724, 07500F, 07506D, 0792, three 07A1 credentials, and 07D2. Therefore the live F152633K0000 Brake uses another working key; the algorithm itself remains matched to ReproStd.

Boot SA exposes only level `01/02` in the sampled odd-subfunction census: `03/05/07/09/0B/11/21/31/33/41/61` all returned NRC `0x12`.

The bootloader has no obvious pre-auth read/dump service:

```text
22 0201 / 0202 / 0203 -> 7F 22 31
23 ReadMemoryByAddress -> 7F 23 11
35 RequestUpload       -> 7F 35 11
```

The write/download side is substantially more informative. `34 RequestDownload` is implemented; `37 TransferExit` exists; RID `10F5` is specifically security-gated pre-auth. ReproStd-style RequestDownload probing, with **no TransferData sent**, gives:

- required ALFI shape: `0x44`;
- DFI `0x01`, `0x11`, and `0x21` all recognize start `0xFEBF0000` and return `7F 34 33` (SecurityAccess denied);
- DFI `0x00` at the same start returns `7F 34 31`;
- coarse FE/FF address scan found only `0xFEBF0000` taking the valid-but-locked path;
- `FEBF1000..FEBFF000` individually return `0x31` when used as start addresses;
- requests beginning exactly at `FEBF0000` remain security-gated for lengths from 1 byte through at least `0x20000` bytes.

The working interpretation is an OEM-configured download/staging area whose accepted base is exactly `0xFEBF0000`, not a generic claim that arbitrary LocalRAM is writable. This is a high-value post-auth canary/payload candidate once SA is solved.

### Missing Brake credential / Toyota acquisition path

Exact live identity remains:

- physical diagnostic request `0x7B0` / response `0x7B8`;
- F181 `F152633K0000`;
- ECU part `8954147040`.

No current local CUW has `Node01/DiagID=07B0`. Upstream openpilot firmware fingerprints independently show `F152633...` is a broad Toyota Brake/ABS software family across Camry and Lexus ES generations, so acquisition of any same-family ReproStd Brake CUW remains useful for credential-family testing.

The North-American Techstream configuration and live Toyota service schema were additionally recovered:

```text
ECUSupplyChange_upload = https://t3services.toyota.com/t3webservices/service/ws1/scantool/ScantoolMilIService.jws
SOAP action             = http://www.openuri.org/sendSearchInfo
```

The endpoint currently publishes a WSDL/XSD. `sendSearchInfo` contains only `File`, `Filename`, `Filesize`, `Timestamp`, `SoftwareID`, and `ID`; `requestSearchInfo` contains `ID` + `HashValue`. No TIS username/password field is carried inside this SOAP method; Techstream's browser-login flow is separate. The next acquisition experiment should characterize this service with a dummy VIN before transmitting the real vehicle identity.

## Techstream V18 NA TIS ECU-supply SOAP path: PecuID client identity, sendSearchInfo fields, and Result semantics

Static recovery from the pinned V18 binaries plus dummy-payload live characterization of
`https://t3services.toyota.com/t3webservices/service/ws1/scantool/ScantoolMilIService.jws`.
All live probes in this session used the masked VIN `XXXXXXXXXXXXXXXXX` (or artifacts already
probed earlier today with a non-maintainer public sample VIN). No TIS credentials were sent and
no vehicle was touched. This is a working note; nothing here is promoted to a finding.

### `CTISCommon::GetPecID` — implementation and data source

`CTISCommon::GetPecID(CString* out)` is at **Techstream.exe VA `0xB95770`** (x86-32, pinned
`Techstream.exe` `e6b7ab88…5e54`):

- Reads a cached char buffer at **`this+0xDC`** and requires `strlen == 32` exactly
  (`cmp ecx,0x20` at `0xB957FA`); additionally requires a non-null result from a validity
  getter on the embedded machine-ID object at `this+0x14` (`call 0x990B80`). On failure it
  copies the literal `No Data!!` (`0x19F707C`) and the caller then skips the whole web call.
- On success it returns the raw 32-char buffer verbatim; the formatted string it builds in
  between is used **only for the log line** `[TI-AP(%s)] %s` + ` PecuID(N) %s `
  (literals `0x1A3C0F0`, `0x1A3DA1C`, `0x1A3DA34`). `CVehicleWizardDlg::GetPecID` logs the same
  `PecuID(N) %s` vocabulary, so this buffer is the client identity consumed everywhere.
- The `this+0x14` object is an embedded mirror of the standalone generator: same skeleton as
  the DLL below, with `CGetID::GetIdData` / `CGetID::GetBiosUUID` / `m_strUUID <- [ %s ] `
  strings and OS-name comparisons (`WinNT`, `WinXP`, `WinVista`, `Win7`).

**Data source: `GetPeculiarID.dll`** (45,056 B, SHA-256
`703fe9609ac6577efea525bc4fee96f1d130b9a329ac40004355e8ed27848ca3`), exports
`PecIdGetPeculiarID`, `PecIdGetBiosUUID`, `PecIdGetMacAddress`, `PecIdGetMachineGUID`,
`PecIdGetProductID`. The PecuID ("Peculiar ID") is a **synthetic 32-char machine fingerprint
composed only of non-user machine data**:

- `MachineGuid` from registry `HKLM\SOFTWARE\Microsoft\Cryptography`;
- `ProductId` from `SOFTWARE\Microsoft\Windows( NT)\CurrentVersion`;
- MAC address(es) via `GetAdaptersInfo` (`%02X%02X%02X%02X%02X%02X`);
- BIOS UUID / physical-disk serials via `DeviceIoControl` SMART/SCSI passes
  (`\\.\PhysicalDrive%d`, `\\.\Scsi%d:`, drive model/serial strings);
- an OS-version tag.

`PecIdGetPeculiarID` (`0x10003860`) gates on `strlen(synthetic)==32`, logs
`Before making software ID %s : strSyntheticID %s` / `NormalEnd %s : PecuID %s`, and on
failure emits `No Data!!`. Exact final composition of the 32 chars (prefix vs 30-char
truncation interplay) is bounded at the last copy step, but the wire-relevant fact is fixed:
**`SoftwareID` on this SOAP path is the 32-char PecuID — client/PC identity, never an ECU CID.**

### sendSearchInfo — field requirements

Wire grammar (pinned WSDL/XSD, `elementFormDefault=qualified`, ns `http://www.openuri.org/`,
`SOAPAction: http://www.openuri.org/sendSearchInfo`, request element `sendSearchInfo` with
`File` (base64), `Filename`, `Filesize` (int), `Timestamp`, `SoftwareID`, `ID` — all
`minOccurs=0`). Response element `resultofSearchInfoSend` = `ID` + `Result` (strings).

Caller `CEcuSupplyChange*` wrapper at **`0xB99863`** (delay-import slot `0xF533B8` =
`?TisServiceSendSearchInfo@CWebService@@…`):

1. `TisServiceSetServerAddr(0x15, URL)` — service index **21** = the
   `ECUSupplyChange_upload|URL` endpoint.
2. `strSoftwareId` = `CTISCommon::GetPecID()` output (empty ⇒ skip the call entirely).
3. `Timestamp` = `Format("%04u.%02u.%02u.%02u:%02u:%02u:%07lu", SYSTEMTIME)` — e.g.
   `2026.09.01.18:40:00:0000000`.
4. `File` = base64 of the `reqData` XML written by `SaveEcuSupplyChangeSendXmlFile`
   (`vinNo` + `ecuInfo/ecuId, ecuAssyNo, writeFlg, baseSwNoLst/baseSwNo`); `Filesize` = its
   byte length; `Filename` = its name (`SC_*.xml`).
5. **`ID` = the constant string `"000000"`** — the orchestrator
   `CEcuSupplyChangeFuncProc::GetXmlDataSwSearch` (`0x52C6A3`) resets member `+0x1A4` to the
   literal `"000000"` (`0x11EA3BC`) immediately before the send and passes that member as the
   ID argument. The client job tag is therefore fixed, not a GUID/counter.

Log literals byte-pinned: `-- Send -- strFileNamePath[%s] strSoftwareId[%s] strTimeStamp[%s]`,
`-- Return -- bRet[%d]`, `-- Receive -- strId[%s] Result[%s]`,
`-- Receive -- Failed to get Result: strId[%s] Result[%s]`,
`-- Receive -- Soap.FaultMessage[%s]`.

Client acceptance rule for the send response (`0xB99ACF`): `bRet==1` **and** `Result=="0"`
are required; anything else ⇒ error `0x1000`, abort (no poll is started). A missing `Result`
with a fault string present takes the `Soap.FaultMessage` branch.

### requestSearchInfo — poll and HashValue

Poll wrapper at **`0xB99D03`** calls `TisServiceGetSearchInfo` (slot `0xF533BC`) with
`ID` = the same `"000000"` member string and
**`HashValue` = uppercase-hex SHA-256 of that ID string**, produced by
`CTISCommon::CreateHashValueSha256` (`0xB9AAD0`; `CryptAcquireContext(PROV_RSA_AES,
CRYPT_VERIFYCONTEXT)` → `CryptCreateHash(CALG_SHA_256=0x800C)` → `CryptHashData(input)` →
`CryptGetHashParam(HP_HASHVAL)` formatted with `"%02X"`). E.g. for `"000000"`:
`91B4D142823F7D20C5F08DF69122DE43F35F057A988D9619F6D3138485C9A203`.
Log: `-- Send -- a_strId[%s] strHashValue[%s]`; result log
`-- Receive -- strFileName[%s] strFileSize[%s] Result[%s]`.

Poll response `resultofSearchInfoRequest` = `File`, `Filename`, `Filesize`, `Result`. Client
decision tree (byte-pinned, `0xB99EF0`–`0xB99FE6`):

- `bRet==1 && Result=="0"` ⇒ success: copy `Filename`, `Filesize`, base64-decode `File` and
  write the `resData` XML to the response path (flow continues into `LoadEcuSupplyChangeDownloadXmlData`,
  TMS-050).
- `Result=="1"` or `Result=="4"` ⇒ **pending**: retry while `time() − t0 < 0x493E0` (300 s =
  5 minutes); pre-poll wait in the orchestrator is 15 s (`0x3A98`), or 3 s (`0xBB8`) when the
  fast-path member `+0x1B4 == 1`.
- any other non-empty `Result` ⇒ terminal failure; missing `Result` ⇒ `Failed to get Result`.

### Server Result semantics observed (live, 2026-09-01)

Endpoint is **anonymous at the transport level** (Apache/Servlet 2.5, plain SOAP 1.1, no auth
headers observed or required). Probes (masked/public VIN only, no credentials):

| probe | SoftwareID | ID | inner reqData VIN | sendSearchInfo response |
|---|---|---|---|---|
| prior: empty | empty | empty | `<reqData/>` junk | `<ID>0</ID><Result>2</Result>` |
| prior: fake | `FAKE-TECHSTREAM` | `FAKE` | masked `X*17` | `<ID>0</ID><Result>2</Result>` |
| prior: 32-hex | 32 hex chars | empty | masked `X*17` | `<ID>0</ID><Result>2</Result>` |
| prior: public | 32 hex chars | empty | public sample VIN | `<ID>0</ID><Result>2</Result>` |
| this session: Techstream-exact | 32 hex chars | `000000` | masked `X*17` | `<ID>0</ID><Result>2</Result>` |

Independent calls:

- `getConfiguration` with a minimal anonymous `milInput` ⇒ full `getConfigurationResult`
  (all capability flags `false`). The service responds normally without any session.
- `requestSearchInfo` with `ID=0` + all-zero hash ⇒ `<Result>1</Result>`, nil
  `File/Filename/Filesize` — **unknown/never-queued job reports the same `1` (pending) state**,
  and the dummy hash is not validated.
- `requestSearchInfo` in the exact Techstream shape (`ID=000000`,
  `HashValue=91B4D142…A203`) ⇒ same `<Result>1</Result>`.

**Interpretation.** The server echoes its own job id `0` regardless of the client `ID` value
(`""`, `FAKE`, `000000` all ⇒ `<ID>0</ID>`), so `ID` is not client-authoritative on the
response. `sendSearchInfo Result=2` is a server-side **rejection of the search submission
itself**, invariant across SoftwareID format (empty / 15-char / 32-hex), ID value, payload
well-formedness, and VIN (masked vs public sample). Under the client's own grammar `2` is
simply "not accepted" (terminal; `0` = accepted). The two remaining hypotheses are not
separable without a registered identity, which is out of scope:

1. **Unregistered PecuID** — the server likely expects `SoftwareID` to match a Techstream
   installation registered with TIS (`TisServiceRegistration` / the browser TIS-login flow
   binds the PecuID to a dealer/user session). All tested SoftwareIDs were synthetic.
2. **Entitlement/region gate** — the submission may be rejected before VIN matching for
   anonymous callers regardless of identity format.

Consequence for the Brake `07B0` acquisition plan: with `Result=2` the client aborts before
any polling, so the observed path cannot be turned into package retrieval by payload shaping
alone; a registered client identity (real Techstream + TIS login) is the missing prerequisite.
Also noted (bounded): `tiswebapi.dll` carries `180000` (ms, plausibly a 3-minute SOAP
conversation timeout) beside the ID fragment table, and HTTP-header vocabulary
`gts-guid`, `user-language`, `request-id`, `date`, `software-content` for the transport.

Safety record for this session's probes: masked VIN only, no TIS username/password, no vehicle
connection involved; the only state created server-side is the anonymous rejected-search
records already produced by the earlier same-day probes.

### 2026-09-01 targeted credential/package hunt: local + public boundary

A dedicated hunt for any additional ReproStd/`07B0`-relevant package or credential,
re-running the descriptor census independently of the VAR-069 artifact:

- **Local package discovery is exhausted.** A full-filesystem `*.cuw` sweep finds
  exactly 52 hits = the same 26 pinned packages (repo + one `herdr` worktree
  mirror); no undiscovered cache exists anywhere on this machine. A repo-wide
  `~/dev/inspect` content search for `F152633K0000` / `8954147040` matches only
  this repo's own generated artifacts and docs.
- **The 12 blank-DiagID format-4 packages are re-verified as non-Brake**: all are
  Tacoma `ENG & ECT` P5-CAN packages whose `LocationID` routes `...0720`
  (89663/89665-xxx CIDs); none carries a brake address or identity.
- **Public metadata has no exact hit and no campaign route**: `F152633K0000` /
  `89541-47040` appear nowhere public; no 2025–26 Camry Brake/EPB reflash
  campaign exists (the only 2025–26 Camry HV actions are the 25V869 inverter
  hardware recall and the 26V511 cluster-software recall — neither reflashes
  skid control). The one public CUW specimen (icanhack.nl) is the same
  `T-0015-20` RAV4 EPS package already in the corpus. Corolla 24TC01
  `F152612A5100..A5400` remains the only public brake-CID campaign family,
  Corolla-only.
- **P5-Unified04 decoded**: the current GTS+ `P5-Unified04.ini` route is
  ReproStd (`TCUWCanReproStdPrepareWriter`/`TCUWCanReproStdFlashWriter`) —
  consistent with the live boot grammar match above.

**Credential-family conclusion.** `cuw_security_up.py` was re-verified
end-to-end (all ten corpus `ServiceAuthKey`s re-derive their recorded `Kwork`
byte-for-byte). Across the corpus, credentials are scoped **per DiagID, not per
vehicle or per calibration**: 0792 shares one key across six
packages/vehicles/years (Corolla, Corolla Cross, bZ4X, 2023–24), and 07D2
shares one across Grand Highlander + Crown; but 07A1 rotates per generation
(three distinct keys), and no key is shared across different DiagIDs. The live
rejection of all eight local keys — including the same-vehicle-same-generation
Camry MG `0x724` key — is therefore consistent evidence that the Brake
credential is a distinct `0x7B0`-family secret. The one acquisition target that
could test this without Toyota/TIS is **any `DiagID=07B0` ReproStd package from
any vehicle/generation** (per the 0792/07D2 pattern such a key plausibly
transfers, though 07A1 shows generational rotation is possible); no such
package exists locally or publicly today. Exact-identity `F152633K0000`
firmware still requires the authenticated TIS `ECUSupplyChange` route above.

## 2026-09-01 clarification — Panda bus numbers vs Toyota GTS bus names

The relay-open direction evidence is electrically correct, but terminology must remain exact after the Toyota-B CAN0/CAN1 repin.

Official comma Toyota-B topology is:

```text
camera-side main pair -> harness CAN2 / Panda bus2
car-side main pair    -> harness CAN0 / Panda bus0
shared secondary pair -> harness CAN1 / Panda bus1 (unsplit)
```

The maintainer physically exchanged the Toyota-B CAN0/CAN1 vehicle pairs. After that repin, the formerly stock-CAN1 steering/chassis network is carried by the CAN2<->CAN0 intercept pair. Independent stream/GTS joins identify that repinned network as Toyota GTS **Bus 4** (Brake/EPS/SAS family), while Panda bus1 carries the distinct Toyota GTS **Bus 1** camera/radar family.

Therefore:

- `Panda bus2` means the **camera-connector side of the relay-intercepted Toyota Bus-4 pair** on this installed/repinned harness. It does **not** mean Toyota GTS Bus 1.
- `Panda bus0` means the **car/chassis side of that same Toyota Bus-4 pair**.
- `Panda bus1` is the separate unsplit pair and carries the Toyota GTS Bus-1 camera/radar family after repin.

With the relay open, native `0x08A` RX on Panda bus2 and native `0x081` RX on Panda bus0 remain decisive direction evidence at the physical harness boundary. Because the Toyota-B adapter is directly inline at the FRC/camera connector, bus2 is the FRC-side electrical endpoint of the intercepted pair. The earlier wording error was equating that physical **camera-side endpoint** with Toyota's logical **Bus 1** name; the bus numbers/direction themselves were not swapped.

## FRC TSS3 Image-FFD live SecurityAccess and record interface

The exact Camry FRC endpoint (`0x792 -> 0x79A`, F181 `8646F3315000`) implements the current GTS+ TSS3 Image-FFD interface recovered statically from `GetTSS3ImageFFDP5_DT.dll` / `CommandCommon.dll`. The interface was exercised **read-only** on 2026-09-01; no recorder deletion, Active Test, flash, or control command was issued.

### Setup / metadata

Live positive reads included:

```text
22 11 03 -> 62 11 03 07 12 00 02 00 00 00 00 01 00 00 00 00
22 11 07 -> 62 11 07 01 00 01 00 00 00 02 02 00 08 00
22 20 81 -> 62 20 81 01
```

`0x2081 = 01` is the current PCS Data Viewer value for **image payload unencrypted**. The viewer's `reverse_bits8(cipher) XOR 0xAA` transform is therefore not used for this vehicle's current stored record payloads.

### SecurityAccess

Image FFD requires extended diagnostic session plus SecurityAccess level `0x03/0x04`:

```text
10 03       -> positive extended session
AB 31       -> 7F AB 33            # before unlock: securityAccessDenied
27 03       -> 67 03 69 0F 82 16 37 10
27 04 E1 FF 87 91 DB 01
             -> 67 04
```

The six-byte key is generated by the current host `CCmdImgOpeDdr::CalculateKeyDataSecLv49` algorithm. It contains **no vehicle/package secret**. For seed `69 0F 82 16 37 10`, the recovered algorithm yields key `E1 FF 87 91 DB 01`, which the exact FRC accepted.

Algorithm, matching the release-local recovered implementation:

```text
rotation_table = [1,2,3,3,2,1]
for i in 0..5:
    v = seed[i]
    index = v & 7
    if index >= 6: index -= 6
    add = output[index] if index < i else seed[index]
    count = ((v >> rotation_table[i]) & 3) + 1
    output[i] = rol8(v, count) + add   (mod 256)
```

### RoB enumeration and record fetch

After level-49 unlock:

```text
AB 31 -> EB 31 28 22 28 21 28 26 28 23 28 61
```

So the exact vehicle currently reported five stored Image-FFD RoB codes:

```text
2822, 2821, 2826, 2823, 2861
```

Record request grammar is confirmed live as:

```text
AB 33 || rob_code_be16 || frame_number_be32
```

and the response grammar is:

```text
EB 33 || rob_code_be16 || frame_number_be32 || block_count_u8 || blocks...
```

where ordinary blocks are `data_id_be16 || len_u8 || data`, but `6xxx` image blocks use a BE32 length.

The first valid occurrence selector is not frame `1`. Toyota's recovered selector helper is:

```text
frame = split*0x200 + data_set*10 + trigger - 10
```

Thus split1/set1/trigger1 is `0x00000201`. Live request:

```text
AB 33 28 22 00 00 02 01
```

returned a populated `EB33` record with six blocks. Its header/block inventory is:

```text
EB33 2822 00000201 06
  5101 len=2
  0501 len=7
  0502 len=4
  0507 len=6
  0511 len=4
  6002 len=0x00000BCB
```

`6002` is the first split-image payload block; the recovered viewer joins split IDs `6002..6017` into synthetic raw-image DID `6001`.

### Relevance boundary

This interface is valuable FRC introspection and exact event timing/context, but the image bytes themselves are not currently the shortest path to lateral control. The steering-relevant internal-state recorder remains TSS3 **Operation FFD** (`AB11/12/13 -> EB11/12/13`), whose dictionary directly contains `5531/5631 -> 5282 -> 5285/57DE -> 5265/560D` lateral request/arbitration/plant objects.

## FRC recorder / FFD surface inventory

A current-GTS+ inventory was performed after the live Image-FFD unlock to determine whether category 498 exposes another recorder more useful than the image stream for lateral-control RE.

### 1. TSS3 Operation FFD — primary steering/control recorder

This remains the uniquely useful FRC-hosted recorder for the lateral pipeline:

```text
AB11                         -> EB11                    enumerate behavior/RoB codes
AB12 || behavior_be16        -> EB12                    enumerate records
AB13 || behavior_be16 || record_be16 -> EB13           fetch record
```

Its recovered PCS dictionary directly names the steering pipeline objects:

```text
5531 LDA request
5631 LTA request
5282 generic TSS lateral request
5285 arbitration result lateral ID
57DE arbitration result pinion angle
5265 Active steering under-control flag family
560D driver-steering/LTA state + EPS pinion observation
```

No other current P5/FRC recorder dictionary found below contains this request/arbitration-result vocabulary.

### 2. TSS3 Image FFD — deep event context, not the shortest lateral path

Current category-498 role `0xE9` is `GetTSS3ImageFFDP5_DT.dll`. Its live SecurityAccess and `AB31/AB33` protocol are documented in the preceding section. It provides timestamped camera-event metadata plus split image payload (`6002..6017 -> 6001`), but it does not expose the lateral request/arbitration object graph directly.

### 3. Generic P5 Record-on-Behavior — present, but materially poorer for lateral

Current category-498 also binds:

```text
role 0xA0  GetRoBP5_DT.dll
role 0xA1  DelRoBP5_DT.dll
```

The current FRC communication-set templates expose a parallel generic RoB family:

```text
AB01                         -> EB01
AB02 || behavior_be16        -> EB02
AB03 || behavior_be16 || record_be16 -> EB03
```

(`AB01/02/03` is distinct from TSS3 Operation FFD `AB11/12/13`.)

The FRC generic RoB dictionary contains 38 unique stored Data IDs. They are principally event/context state: key cycle/time/distance, IG voltage, camera temperature/voltage/weather/recognition validity, white-lane recognition, LDA/LTA/LCA customize/switch/control condition, PCS/PDA/RSA/ASL state, and related user/display state. A complete current-table name scan contains **no TSS request, lateral target/pinion request, steering-assist/damping request, or arbitration-result field**. Therefore generic RoB can supplement perception/feature context but is not a replacement for TSS3 Operation FFD in the `5631 -> 5282 -> 5285/57DE` investigation.

A live `AB01` probe was attempted after Image-FFD retrieval, but the Comma diagnostic transport simultaneously stopped returning even ordinary F181 reads. No conclusion is assigned to that non-response; the generic RoB wire grammar above is current GTS+ static evidence and should be retried when transport is healthy.

### 4. Standard P5 per-DTC Freeze Frame Data — present through global P5 role

The current master binds role `0xB5` at category 0 to `GetEachFrzFrmDatP5_DT.dll`. Thus ordinary current-P5 ECUs, including FRC unless specifically overridden, use the standard P5 per-DTC freeze-frame reader. FRC's current comm set contains the UDS snapshot request template:

```text
19 04 <DTC24> FF  -> 59 04 ...
```

The reader resolves returned Data IDs through the P5 Data Monitor tables and can therefore preserve a broader fault-time snapshot than the 38-field generic RoB set. The current FRC Data Monitor dictionary includes LDA/LTA/LCA installation/control states, steering-wheel information, control mode, lane/perception state and other ADAS context.

However, the same dictionary contains **no lateral target/pinion request or arbitration-result signal**. Consequently this path is worth sampling for fault/context analysis, but it is not expected to reveal the signed `0x08A` command construction directly.

`FRC_P5` contains two type-80 `CDbDataIdBitForFfdTable` rows:

```text
11271a2c0000070007000007
12271a2c0000060006000007
```

Their lookup keys are `0x2711/0x2712` and both reference master variable `0x2C1A`, which normalizes through the current GTS+ `-0x2710` variable namespace to entry `0x50A = 04 03`. A corpus census shows this exact pair in **126 P5 databases**. It is generic P5 FFD plumbing, not a hidden FRC-specific recorder channel.

### 5. Older generic Operation Freeze Frame — not bound to current FRC

Current master role `0xBA` binds `GetOperationFrzFrmDatP5_DT.dll` only to category 432 `PCS2_P5` (with the category-0 fallback being the P4 PCS implementation). It is **not** bound to category 498. This matches the generation migration: current FRC absorbs the older PCS/LDA/DSS roles and exposes the specialized TSS3 Operation/Image FFD pair instead.

Therefore there is no second legacy P5 Operation-FFD recorder hiding behind category 498 that is richer than `AB11/12/13`.

### 6. DDR / event-recorder and Vehicle Control History boundary

GTS+ ships generic `GetDDRInfo*` plugins and its TSE saved-session format has first-class `VehicleControlHistory`, `PredictiveFFD`, DTC/FFD, RoB, PCS Operation FFD and PCS Image FFD sections. These container/plugin families must not be mistaken for additional live FRC diagnostic recorders.

`FRC_P5.ddb` has **none** of the DDR model tables:

```text
165 CDbDDRDiagCodeTable
167 CDbDDRFreezeFrameTable
168 CDbDDRInvalidConditionTable
```

and current category 498 has no DDR-specific DLL binding. The richer DDR/event-recorder dictionary appears on other ECUs / the P6 ADAS-domain successor, not as a hidden P5 FRC surface. Vehicle Control History likewise remains a saved-session/report family here rather than a separately identified category-498 live request protocol.

### Practical priority

For the present lateral problem, recorder priority is therefore:

```text
1. TSS3 Operation FFD    request/arbitration/result internals      highest value
2. standard DTC FFD      broad fault-time FRC context              supplemental
3. generic RoB           feature/perception/event context          supplemental
4. Image FFD             visual/timestamp context                  optional
```

The highest-value next live specimen remains a clean stock-LTA event in which Operation FFD captures `5631`, `5282`, `5285`, ideally `57DE`, `5265`, and `560D`, synchronized with native `0x08A` and return `0x081` traffic.


## Stationary B6 admission run: stage-1 Gate-2 result

The car-ready discriminator was executed later on 2026-09-01 against exact EPS F181 `02 || 8965F3307000 || 8A3113303100`, current post-repin Panda bus 0, Park, and zero decoded wheel speed. The already-installed persistent development image had only the final Gate-2 compare neutralized (`0x8F952=E001`, known fixup `D9AF33AF`).

The ID11/current-angle phase sent **85 B6 frames and received 85 Panda TX echoes**. Three independent SID-0x23 ladder snapshots all reported healthy sampled status (`ADB9=0`, `CAFF=1`, `ACBD=0`) but retained the previous application value (`ADB0=0`, `AE90=64` while commanded raw target was 66) and `CB00=7`. The stationary probe therefore returned `payload_not_delivered`. No steering-offset phase ran. Raw evidence is retained under `targets/camry-2026/raw-20260901/f33-b6-admission/`.

Exact Gate-2 disassembly sharpens the next experiment. One pre-callback path already executes `8F944 003A = mov 0,r7`; the other executes `8F948 1A38 = mov r26,r7` before callback `8F94C`, and only later reaches the stage-1-patched compare at `8F952`. The next bounded persistent stage therefore changes only `8F948 1A38->003A` while preserving `8F952=E001`. The builder reconstructs the source from stock plus stage 1 and resigns the **combined** image: source SHA `272843a2…9f65`, source fixup `D9AF33AF`; two-patch prefix `2ED524FA`, final fixup `D12ADB05`, final residue `FFFFFFFF`, final SHA `6a371a2a…d59c`. The inverse recovery payload reverses stage 2 only.

This is a testable hypothesis, not a live success claim. The next car sequence is zero-write stage-2 preflight, APPLY only on exact preflight, full OFF->READY, zero-write persistence verification, then repeat the same admission-only ID0/ID11 ladder. A steering offset remains gated on `ADMITTED`.
