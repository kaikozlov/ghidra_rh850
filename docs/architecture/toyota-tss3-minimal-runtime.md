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

The resident signer is a target prerequisite, not a replacement openpilot
controller or permission system. Full EPS power loss removes it.

## Minimum by repository

| repository | required for the demonstrated lateral path | not required by that path |
|---|---|---|
| openpilot | After CarParams identifies the F33 safety profile, disable Panda `canfd_auto` on Toyota-B buses 0 and 2. No controls/model changes. | direct-Panda lease; `CanData.fd` schema/logging; SecOC-key Params; controller arming Params; changes to `card.py` or `controlsd` |
| opendbc | F33 platform identity and DBC; TSS3 state decoding; F33 CarParams; direct C7 angle encoder; Toyota F33 safety RX state, angle checks, TX whitelist, and normal relay blocking | host construction or signing of B6; host freshness/MAC state; diagnostic/oracle arming; controller-side permission vetoes; Corolla actuation assumptions |
| Panda | Preserve the received FDF and BRS attributes when software-forwarding across the relay; sanitize the queue-private forwarding markers on host input and validate the original host checksum | relay-close/debug exceptions; F33-specific safety state outside opendbc; global 70% data sample point; global EFBI; logging the per-frame FDF bit to cereal |

## Existing longitudinal seed

[`camry_frc_request_poc.py`](../../tools/targets/camry/live/camry_frc_request_poc.py)
is already the bare message-generation primitive for the observed Camry
Toyota-B request family. It starts from a valid 32-byte `0x160` frame, changes
only the B2 alive counter and candidate signed-7 B12 request, and recomputes the
recovered AUTOSAR E2E Profile-5 CRC. The reusable integrity implementation is
[`toyota_e2e_p05.py`](../../tools/toyota_support/toyota_e2e_p05.py).

`tools/test camry_frc_request_poc` verifies fixed retained witnesses, more than
20,000 direct retained B2/B12 frame pairs, byte-exact reconstruction, counter
behavior, request bounds, and fail-closed template validation. The tool is
deliberately offline and transmits nothing. This proves that the minimum wire
encoder exists; it does not by itself prove Camry request scaling or receiver
ownership.

The native openpilot-shaped driving layer should therefore add only:

1. opendbc target configuration enabling openpilot longitudinal control;
2. a `CarController` adapter from ordinary `CC.actuators.accel` to the proved
   target request semantics, using the existing Profile-5 encoder and the
   required cadence/counter ownership;
3. the exact `0x160`, 32-byte, Toyota-B TX entry plus ordinary acceleration
   bounds in Toyota safety; and
4. target validation of scaling, companion fields, source ownership, release,
   and standstill behavior.

No longitudinal planner, `controlsd`, or second permission-system change is
indicated. The Corolla field result establishes that a TSS3 target can use the
unprotected `0x160` command on stock Toyota-B without the Camry lateral repin.
Its exact opendbc/sunnypilot revision and raw rlog are still external, so its
field mapping must not be silently substituted for the Camry B12 hypothesis.

For the maintainer Camry, the prior session also closed the intended harness
shape. The successful lateral drive used a development CAN0/CAN1 repin. Undoing
that repin returns Toyota Bus-1 and `0x160` to Panda's CAN0/CAN2 relay pair, so
the stock frame can be blocked and replaced. Toyota Bus-4/EPS returns to the
unsplit Panda bus 1, which had already reached the EPS directly before the
repin; the F33 C7 signer sideband should move there. The combined candidate is
therefore ordinary Toyota-B hardware, with `0x160` replacement on bus 0 and C7
lateral control on bus 1. This remapping still needs a parked transport check
before it replaces the post-repin road-proven configuration.

### Why one openpilot transport exception remains

The successful route contains only Classical host TX:

- C7 `0x1FDC0002`, bus 0, 8 bytes;
- HUD `0x412`, bus 0, 8 bytes;
- cancel `0x101`, bus 2, 8 bytes.

The same network carries 32-byte FD `0x08A`. Route 45 directly showed that
upstream's sticky bus-global `canfd_auto` promoted native-Classical replacement
frames to FD. C7 is also an 8-byte Classical PDU and must not inherit that
format. The post-repin lateral-only candidate therefore disables auto promotion
on buses 0 and 2 after the F33 Toyota safety parameter is known. In the intended
stock-harness combined topology, the short Classical C7 sideband moves to bus
1, so the same target-scoped exception moves with it; buses 0 and 2 must retain
FD transport for the 32-byte `0x160` replacement. Neither form alters
fingerprinting or unrelated cars.

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

## First cleanup checkpoints

- `opendbc@4b41113d` removes 168 lines of retired host B6/SecOC construction;
  the controller now emits C7 directly from the limited angle and
  `CC.latActive` sequence.
- `opendbc@9140dd13` separates generic TSS3 state from exact-F33 safety.
- `kai-openpilot@7cde01353` advances the known-working branch to those opendbc
  cleanups.
- upstream-based `openpilot` branch `tss3-minimal` at `17e8a6557` contains one
  runtime-file change: the F33-scoped `canfd_auto` setting.
- upstream-based `Panda` branch `tss3-minimal` at `cafc5fe6` contains three
  runtime-file changes for exact software-forwarded frame format and safe host
  ingestion.

The two upstream-based branches are reduced candidates, not road-verified
replacements for the successful stack. Panda's focused USB protocol suite
passes (8 tests / 199 subtests), and the openpilot source passes a standalone
C++ syntax check against the current generated cereal headers. The opendbc
Camry plus F33 safety selection passes 29 focused tests.

## Build-up order

1. Reconstruct the F33 opendbc port on current upstream with only the state,
   interface, C7 controller, DBC, fingerprint, and F33 safety contract.
2. Replay the retained route and prove expected CarState, C7 cadence, inactive
   sequence behavior, safety acceptance/rejection, and no controller-side
   permission layer.
3. Restore the normal Toyota-B pin mapping and remap the C7 controller and
   safety entry from bus 0 to unsplit bus 1. Prove parked that EPS/C7 remains
   reachable and that Toyota Bus-1 is split across CAN0/CAN2.
4. Promote the existing offline `0x160` builder into the normal opendbc
   controller/safety path only after binding its request semantics to the
   target. Import the Corolla field revision and reduce its rlog when they are
   available. Emit the replacement on bus 0 and block the stock bus-2 copy
   through normal relay ownership. This path is independent of the
   SecOC-protected B6 lateral carrier and must remain separately reviewable.
5. Run a parked/bench transport check, then a controlled road A/B using the
   upstream Panda timing before deleting the matched-timing override from the
   deployment stack.
6. Add native cancellation and HUD replacement as separate reviewable layers.

The direct-Panda lease and installer remain deployment tooling until the signer
load can be expressed without modifying openpilot runtime. They must not become
an engagement gate or a second permission system.
