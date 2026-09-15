# Toyota TSS3 minimal openpilot runtime

This note separates the code that made the exact-F33 Camry lateral drive work
from the scaffolding and instrumentation that happened to be present in the
same checkout. The successful-drive evidence is in
[the bounty evidence report](../variants/toyota-tss3-openpilot-bounty-evidence.md).

The first target is deliberately narrower than a complete Toyota TSS3 port:
reproduce the demonstrated lateral path on the exact F33 with the smallest
upstream-shaped runtime. Features can be added only after that baseline is
understood and preserved.

Longitudinal is a separate build-up layer, but message generation is not
missing: this repository already contains a deterministic offline Camry
`0x160` request constructor, and the independent Corolla field report records
a live controller using that native command on stock Toyota-B.

## Runtime boundary

The active path is:

1. upstream `controlsd` owns engagement and `CC.latActive`;
2. opendbc `CarState` decodes ordinary vehicle and stock-cruise state;
3. opendbc `CarController` applies the normal angle limits and emits an 8-byte
   C7 sideband containing only an active sequence and target angle;
4. Panda's normal Toyota safety model checks the C7 angle command and TX
   whitelist;
5. the exact-F33 EPS-resident signer consumes C7, edits the native B6
   application fields, and lets the stock EPS SecOC path produce the trailer.

The exact-F33 signer is a target prerequisite, not a replacement openpilot
controller or permission system. The production-shaped candidate is now the
**volatile continuous RAM signer**: it generates a native-valid FV4+CMAC28
trailer with the EPS's own ICU-S path and therefore does not require the
historical stage-5 receiver bypass or any persistent CodeFlash change. Full EPS
power loss removes it and requires the bounded NRTD -> READY install/load-arm
lifecycle again. The old persistent signer remains historical development
material, not the intended deployment architecture.

## Minimum by repository

| repository | required for the demonstrated lateral path | not required by that path |
|---|---|---|
| openpilot | After CarParams identifies the F33 safety profile, disable Panda `canfd_auto` on unsplit Toyota-B bus 1. No controls/model changes. | direct-Panda lease; `CanData.fd` schema/logging; SecOC-key Params; controller arming Params; changes to `card.py` or `controlsd` |
| opendbc | F33 platform identity and DBC; TSS3 state decoding; F33 CarParams; direct C7 angle encoder; native 20 Hz TSS3 RadarInterface from recovered `0x180..0x185` geometry/motion fields; Toyota F33 safety RX state, angle checks, TX whitelist, and normal relay blocking | host construction or signing of B6; host freshness/MAC state; diagnostic/oracle arming; controller-side permission vetoes; unmapped object-class/reliability metadata |
| Panda | Preserve the received FDF and BRS attributes when software-forwarding across the relay; sanitize the queue-private forwarding markers on host input and validate the original host checksum | relay-close/debug exceptions; F33-specific safety state outside opendbc; global 70% data sample point; global EFBI; logging the per-frame FDF bit to cereal |

## Current longitudinal layer

[`camry_frc_request_poc.py`](../../tools/targets/camry/live/camry_frc_request_poc.py)
was the bare message-generation primitive for the observed Camry Toyota-B
request family. That wire contract is now integrated into the normal opendbc
controller as an **alpha longitudinal** path: `CarState` retains the live
camera `0x160` template/counter, `CarController` owns the frame while stock
cruise is engaged, applies the exact Camry B4:B5 signed-15 request plus the
inverted signed-7 B12 companion, and recomputes AUTOSAR E2E Profile-5 CRC/Data
ID `0x444A`. Panda blocks the stock bus-2 copy only while longitudinal control
is allowed and accepts the bus-0 replacement under the exact target range
`-1.5..+1.3 m/s²`.

Below the retained low-speed override boundary the controller relays Toyota's
live request unchanged rather than claiming standstill/hold ownership. This is
why `autoResumeSng` is deliberately false: short-stop restart is observed, but
release from Toyota's delayed long-stop hold is not proved. Full physical DRCC
acceleration authority and PCS/AEB coexistence also remain vehicle-validation
items, so release-default operation continues to use stock ACC.

No longitudinal planner, `controlsd`, or second permission-system change is
indicated. The Corolla field result establishes that a TSS3 target can use the
unprotected `0x160` command on stock Toyota-B without the Camry lateral repin.
The contributor's now-retained
[`PORT_ARCHITECTURE`](../../community/albinoelephant/albinoelephant_discord_PORT_ARCHITECTURE.md)
reference reports the concrete Corolla mapping: signed 15-bit B4:B5 at
0.001 m/s²/count, B2 counter, CRC-16/CCITT Data ID `0x444A`, camera template on
bus 2, replacement on bus 0, and a frame-for-frame/camera-counter handoff with
stock relay below roughly 1 mph. The exact source checkout/patch and road rlog
remain external. More importantly, these Corolla wire details differ from the
retained Camry B12/Data-ID contract, so they are evidence for the reusable
ownership pattern, not values to substitute into the Camry encoder.

For the maintainer Camry, the prior session also closed the intended harness
shape. The successful lateral drive used a development CAN0/CAN1 repin. Undoing
that repin returns Toyota Bus-1 and `0x160` to Panda's CAN0/CAN2 relay pair, so
the stock frame can be blocked and replaced. Toyota Bus-4/EPS returns to the
unsplit Panda bus 1, which had already reached the EPS directly before the
repin; the F33 C7 signer sideband now moves there. The combined candidate is
therefore ordinary Toyota-B hardware, with `0x160` replacement on bus 0 and C7
lateral control on bus 1. This software remapping is implemented; it still
needs a parked transport check before it replaces the post-repin road-proven
configuration.

### Why one openpilot transport exception remains

The road-proven temporary-repin route contained only Classical host TX and put
C7 on bus 0. The **current stock-Toyota-B candidate** is:

- C7 `0x1FDC0002`, **bus 1**, 8 bytes;
- HUD `0x412`, bus 0, 8 bytes;
- cancel `0x101`, bus 2, 8 bytes;
- alpha-long `0x160`, bus 0, 32-byte CAN-FD.

The same network carries 32-byte FD `0x08A`. Route 45 directly showed that
upstream's sticky bus-global `canfd_auto` promoted native-Classical replacement
frames to FD. C7 is also an 8-byte Classical PDU and must not inherit that
format. The old post-repin lateral-only candidate disabled auto promotion on the buses
used by that experiment. In the intended stock-harness topology, the short
Classical C7 sideband is on bus 1, so the target-scoped exception is now only
there; buses 0 and 2 retain normal mixed/FD transport for the 32-byte `0x160`
path and forwarded vehicle traffic. Neither form alters fingerprinting or
unrelated cars.

Adding `CanData.fd` remains useful for exact logging and arbitrary short FD
host TX, but the demonstrated controller sends no short FD PDU. It is a
transport enhancement, not a dependency of this lateral baseline.

### Why Panda still needs a generic fix

The Toyota-B relay remains open in the normal comma topology. Stock traffic is
software-forwarded in both directions. Upstream Panda copies received FDF into
the queued packet, but while `canfd_auto` is active its TX path ignores the
per-frame value and uses sticky bus state; BRS is likewise bus-global.

The minimum Panda candidate marks internally forwarded packets and preserves
their received FDF/BRS. Because the marker reuses wire-header bits, USB host
input must be validated first and those private bits cleared before the packet
enters the TX queue. This is transport correctness, not Toyota policy.

The exact F33 uses a 70% 2-Mbit data sample point and receive-edge filtering,
but retained routes already received its FD traffic at Panda's upstream 80%
setting without driving-time protocol-error growth. The successful drive used
the matched settings, so removing them still needs a vehicle A/B; current
evidence does not justify treating either global change as a minimum runtime
dependency.

## Generic and target-specific axes

`ToyotaFlags.TSS3` describes the state/network generation. It does not grant
actuation and does not imply one authentication scheme.

`ToyotaSafetyFlags.F33` selects the exact actuator/safety contract proven on
this calibration: the C7 sideband, its angle scaling, and the corresponding
RX/TX set. Keeping this flag target-specific prevents another TSS3 platform
from inheriting F33 behavior merely because it is newer Toyota hardware.

The reusable architecture is the normal openpilot division of ownership. The
C7 wire contract and EPS payload remain exact-F33 facts until transferred by
new evidence.

## Current cleanup checkpoint

The current upstream-shaped stock-harness port has moved beyond the original
`3c79d935` checkpoint. It now includes target-native Camry state, exact-EPS
fingerprinting, C7 bus-1 lateral control, normal Toyota HUD/cancel ownership,
alpha `0x160` longitudinal replacement, target-specific Panda limits, a
retained-route-tuned 15.3 steering-ratio default (with the existing 0.18 s
actuator delay independently consistent with `lagd`), and a native TSS3
RadarInterface. The retained Bus-1 family closes three banks of
eight objects: `0x180..0x182` provide u16×0.01 m range plus s12×0.05 m lateral
geometry and `0x183..0x185` provide s10×0.1 m/s relative speed. The latter is
independently validated against finite-difference range in both retained drives
(r=0.912/0.956, fitted slope ~0.99). The latest focused Camry+Corolla TSS3 suite
passes 28/28 and the full Toyota unit set passes 46 tests / 205 subtests; CAN/
DBC/docs/platform validation passes 56 tests / 2,959 subtests and the generic
car-interface suite passes 252 tests at the September 15 checkpoint.

The parent openpilot tree still has only the target-scoped transport exception
needed to keep short C7 Classical on exact-F33 bus 1. Panda retains the generic
forwarded-frame format corrections. The stock-topology software is therefore
reviewable as ordinary openpilot architecture; what remains is vehicle
qualification, not another control stack.

Deployment tooling now defaults to the byte-exact continuous helper from the
September 10 successful steering handoff. The car kit also contains a bounded
`f33-secoc recover-drcc` operation: after volatile signer bootstrap it preserves
DTC state, runs the exact physical-SID14 plus functional-Mode04 clear already
proved on the maintainer car, verifies no known responder retains
`status&0xAF`, and reads FRC DIDs `1903/1905/1906`. This is the explicit test of
whether stock DRCC can be restored in the same ignition cycle **without**
powering off the EPS and losing the RAM signer. The clear transport is proven;
DRCC restoration after signer bootstrap is not yet live-qualified.

## Remaining qualification order

1. On the replacement rack with **stock Toyota-B pinning and stock CodeFlash**,
   run the v16 car-kit volatile lifecycle: NRTD `install` -> direct READY
   `load-arm`. Require exact helper readback and native-trailer equality.
2. Run `f33-secoc recover-drcc`. A positive result must show zero post-clear
   `status&0xAF` records and FRC cruise permission restored while the resident
   remains alive. This closes the only known conflict between volatile signer
   bootstrap and release-default stock ACC.
3. Parked, verify C7 reaches the EPS on stock bus 1 and that sequence zero is a
   native-B6 no-op. Then perform a short controlled lateral A/B and compare it
   with the retained September 10 route.
4. Validate the current HUD/cancel replacement on the stock harness, including
   openpilot `steerRequired` presentation and stock-cruise cancellation.
5. Test alpha longitudinal separately: first parked/template ownership, then a
   bounded road acceleration/deceleration A/B. Require downstream vehicle
   response, source suppression, gas/brake disengagement behavior, and PCS/AEB
   coexistence. Keep release-default stock ACC until these are closed.
6. Capture one delayed (>5 s) stop/restart cycle. Do not set `autoResumeSng`
   unless openpilot can release Toyota's long-stop hold without driver input.
7. Keep `steerFaultTemporary`/`steerFaultPermanent` unmapped until a controlled
   asserted/recovery capture distinguishes the exact F33 native states; do not
   invent policy from static DTC classes.

The direct-Panda lease and installer remain deployment tooling until the signer
load can be expressed without modifying openpilot runtime. They must not become
an engagement gate or a second permission system.
