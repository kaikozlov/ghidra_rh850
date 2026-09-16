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
- alpha-long `0x160`, bus 0, 32-byte CAN-FD.

The former HUD `0x412`/brake-cancel `0x101` transmissions are removed: they
did not replace their stock unsplit-bus sources.

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

### Cross-variant resident control ingress

The Crown bring-up closed a second stock host-to-resident transport that is
present on all four tracked TSS3 EPS images. Exact Camry F33, Corolla H,
Corolla F, and Crown F30 each configure classic functional request `0x777` as
DCM request type 1. Their functional service set is identically
`10,14,28,31,3E,85`; `C6` and `C7` are absent. The common service lookup
therefore assigns NRC `0x11` to either control SID, and each exact response
selector suppresses that NRC for a functional request. CanTp/PduR delivers the
complete seven-byte N-SDU to the target's channel-1 DCM buffer before the
resident's existing post-receive hook:

| target | functional DCM buffer | dedicated family-5 ingress | dedicated staging |
|---|---:|---|---:|
| Camry `8965F3307000` | `FEBE5751` | `0x1FDC0002` enabled | `FEBE4C34` |
| Corolla `8965H1202000` | `FEBE563D` | `0x1FDC0002` enabled | `FEBE4B20` |
| Corolla `8965F1208000` | `FEBE563D` | `0x1FDC0002` enabled | `FEBE4B20` |
| Crown `8965F3012000` | `FEBE527D` | family 5 disabled | — |

The Crown vehicle first dynamically proved the functional transport with
`07 C7 A5 00 12 34 00 00`: the DCM mailbox tail matched and no `0x7A9` NRC was
emitted. Follow-up showed stock DCM teardown may clear N-SDU B0, so the active
Crown signer duplicates its C6/C7 tag into durable B1. The unified runtime adopts
that corrected tail-tag shape on every target. Camry and Corolla functional
ingress are firmware-closed but have not yet been separately live-qualified. The
deterministic matrix is
[`tss3_resident_control_ingress_matrix.json`](../../data/generated/tss3_resident_control_ingress_matrix.json).

This means **Corolla does not need an unoccupied CAN mailbox hunt**. Both H and
F already carry the same configured dedicated extended-CAN family as F33; the
current Corolla signer uses `0x1FDC0002 -> FEBE4B20`. The functional `0x777`
route is available as a second stock-firmware ingress if a future calibration
compiles family 5 out, as Crown does.

For F33 there is likewise no present reason to replace the road-proven
`0x1FDC0002 -> FEBE4C34` runtime with functional diagnostics. `0x777` is a
functional diagnostic endpoint, not a dedicated signer transport, so a normal
driving integration would have to grant only the exact C7 envelope rather than
arbitrary diagnostic TX. It would also still be an 8-byte Classical PDU on the
same mixed/FD bus, so switching carriers would **not** remove the bus-1
Classical-TX/`canfd_auto` requirement. The smaller architecture is therefore:
use the dedicated family-5 carrier where the target already configures it, and
use the stock functional-Diagnostic C6/C7 path as the no-CodeFlash fallback
where that carrier is absent.

#### Parallel unified functional runtime

The cross-variant closure is strong enough to test a second architecture directly
instead of continuing to reason about it abstractly. A new **parallel** runtime now
uses the stock functional `0x777` path on all four exact targets while leaving the
existing Camry/Corolla/Crown implementations in the tree unchanged. Its common
wire contract is:

```text
helper loader (where needed):  07 C6 C6 index word_le32
runtime control:               07 C7 C7 seq target_hi target_lo 00 00
```

`build_tss3_unified_b6_signer.py` emits exact-target bundles for Camry F33,
Corolla H/F, and Crown F30; `tss3_unified_b6_signer.py` provides the common
preflight/install/qualify/control harness. The resident and helper are now **one
maintained source pair**, with SHA-bound compile macros selecting the exact F3 or
Corolla scheduler/RAM geometry. This is intentionally not one byte-identical
multi-calibration binary: exact call/RAM addresses differ, and Corolla's two-byte
high-tail headroom requires its existing embedded-helper startup strategy. Camry
and Crown retain their post-startup split-helper load geometry; Corolla retains
its embedded-helper install geometry. Target-specific B6 mutation tuples, freshness
cells, command-5 addresses, and scheduler replay remain target-local.

The common first vehicle test is deliberately transport-only: bind exact F181,
enter EXTENDED over physical `0x7A1`, snapshot the target-specific functional DCM
buffer with SID23, send one `07 C7 C7 A5 12 34 00 00` frame on `0x777`, and
require the durable mailbox tail plus suppressed NRC11 behavior. Only after that
does the harness install RAM and attempt the native-MAC oracle. This makes the
unified carrier falsifiable on Camry/Corolla without discarding the road-proven
dedicated F33 path or the current Corolla family-5 implementation.

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
dedicated `0x1FDC0002` C7 transport has now transferred exactly to Corolla H/F,
but actuator field semantics, scaling, limits, signer RAM locations, and the EPS
payload remain exact-target facts and must not transfer merely from the shared
carrier.

## Current Camry audit checkpoint

The September-15 retained-evidence audit supersedes the preceding “essentially
complete” assessment. The maintained C7 architecture is unchanged, but its
implementation and evidence boundaries are corrected:

- Stock Toyota-B radar objects originate on bus0, FRC `0x160` on bus2, and
  `0x025/0x101/0x412` on unsplit bus1. HUD/brake duplicates on the ADAS relay
  therefore did not replace the stock source. Those transmissions are removed;
  automatic cruise cancellation remains a genuine integration gap.
- The 15.3 absolute learned steering ratio is retained. Tire stiffness returns
  to 0.7933 because paramsd's learned ~1.0 multiplies the configured CP
  stiffnesses. Identical cached lagd values do not constitute new independent
  delay estimates; the 0.18-s default is left unchanged.
- The Camry v17 kit uses a 598-byte supervised helper with seven-foreground-tick
  host-command loss supervision. The existing resident/staging/authenticated
  payload are unchanged. 86 compiled-instruction assertions cover liveness and
  differential/error behavior; this new helper is not vehicle-qualified.
- Camry radar now uses independently anchored 0.005-m range, 0.04-m
  left-positive lateral, and 0.025-m/s low14 velocity plus source-driven
  new/end-track flags and raw-state-zero rejection. Complete-cycle handling,
  loss/duplicate recovery and held-out replay are tested; the normal Camry
  radar interface is enabled. No other TSS3 radar platform is inferred.
- Exact F33 current hardware and cooperative-control inhibits feed ordinary
  `steerFaultTemporary`. Their assertion, RTE/wire binding, readiness and
  recovery are tested through stock instructions. A one-bit aggregate that
  merges transient and latched causes cannot supply a permanent-fault class.
- Planner, controller and Panda share the Camry −1.5..+1.3-m/s² host envelope.
  A CRC-valid byte-exact native handback is preserved without clipping Toyota's
  own request. This does not establish native longitudinal authority.

The historical successful steering samples used conventional cruise. They do
not prove the final supervised runtime plus adaptive cruise. The revised
`recover-drcc` preserves its pre-clear evidence before mutation, rejects short
DID/ISO-TP responses, and requires distance-control mode **and** genuine cruise
permission with ACC-not-available clear. Its same-cycle vehicle result remains
unobserved.

Current status and reproducible validation are centralized in the
[capability matrix](../variants/camry-2026-capability-matrix.md) and
[port evidence review](../variants/camry-2026-port-evidence-review.md). A new
transport alone does not solve command lifetime, native cruise cancellation,
object validity, or physical actuator qualification. The parallel unified
functional runtime described above remains a separate workstream; its carrier
closure must not silently transfer the old Camry helper's road qualification.

The direct-Panda lease and installer remain deployment tooling. They must not
become a second engagement policy in openpilot. No proved nondisruptive stock
READY-mode RAM placement-plus-execution path has replaced the exact NRTD
bootstrap; the earlier XCP/callback audit remains a bounded recovered-surface
negative, not a proof that no alternative could exist.
