# Toyota TSS3 minimal openpilot runtime

This note separates the code that made the exact-F33 Camry lateral drive work
from the scaffolding and instrumentation that happened to be present in the
same checkout. The successful-drive evidence is in
[the bounty evidence report](../variants/toyota-tss3-openpilot-bounty-evidence.md).

The first target is deliberately narrower than a complete Toyota TSS3 port:
reproduce the demonstrated lateral path on the exact F33 with the smallest
upstream-shaped runtime. Features can be added only after that baseline is
understood and preserved.

Longitudinal is a separate build-up layer and remains stock-owned. The
September-16 request-plane audit supersedes the former `0x160` actuator
interpretation: `0x08A` is the shared TSS3 application-request carrier for both
lateral and longitudinal requests, while `0x160` is retained only as FRC-origin
state/evidence.

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

Native longitudinal is deliberately **not advertised** on the current TSS3
platforms. The recovered request/result split places the TSS application
request in `0x08A`: B6/B7 carry the two request-ID/allocation tuples and
B8:B9/B11:B12 carry the two signed16 ×0.001 m/s² acceleration requests. The
same PDU also carries the lateral request tuple. Brake-owned `0x081` is the
corresponding chassis-side result/reference family.

The earlier `camry_frc_request_poc.py` and contributor Corolla `0x160`
modify-and-forward work remain historical RE/field evidence, not the current
actuator contract. `0x160` is still useful as an FRC-origin Profile-5
state/evidence PDU, but opendbc no longer parses it as a live command template,
constructs it, blocks it, or whitelists it for host replacement. Both Camry and
Corolla therefore keep Toyota `STOCK_LONGITUDINAL` even when Alpha Long is
requested.

The remaining blocker is source ownership, not planner math. On stock Toyota-B
the `0x08A` request family is visible on the unsplit chassis network, so the
normal CAN0/CAN2 relay cannot simply make openpilot the sole emitter. A future
native-long implementation needs a qualified suppression/sole-emitter boundary
or an equivalent pre-signing/request-generation handoff, followed by normal
Brake/PCS/AEB coexistence validation. Until then stock Toyota longitudinal is
the only runtime path.

### Why the remaining openpilot transport exception is lateral-only

The current TSS3 host-control PDU is the 8-byte Classical functional frame
`0x777` on stock Toyota-B Panda bus 1:

```text
07 C7 C7 seq target_hi target_lo 00 00
```

The first `07` is the ISO-TP single-frame PCI length. CanTp removes it and
places the seven-byte N-SDU `C7 C7 seq target_hi target_lo 00 00` in the EPS
functional DCM buffer. Panda permits only this exact bounded C7 envelope; it
does **not** expose arbitrary functional diagnostics while driving. The former
HUD `0x412`, brake-cancel `0x101`, longitudinal `0x160`, and historical
extended-family-5 `0x1FDC0002` steering transmissions are not part of the
current openpilot runtime surface.

The same physical network carries native CAN-FD traffic including `0x08A`.
Route 45 showed that sticky bus-global `canfd_auto` can promote a short
Classical host frame to FD, so functional C7 still needs the target-scoped
Classical transport treatment on bus 1. No equivalent host transport exception
is currently needed for longitudinal because openpilot emits neither `0x08A`
nor `0x160`.

Adding `CanData.fd` remains useful for exact logging and arbitrary short FD
host TX, but the demonstrated controller sends no short FD PDU. It is a
transport enhancement, not a dependency of this lateral baseline.

### Cross-variant resident control ingress

The Crown bring-up closed a stock host-to-resident transport that is present on
all four tracked TSS3 EPS images. Exact Camry F33, Corolla H, Corolla F, and
Crown F30 each configure classic functional request `0x777` as DCM request type
1. Their functional service set is identically `10,14,28,31,3E,85`; `C6` and
`C7` are absent. The common service lookup therefore assigns NRC `0x11` to
either control SID, and each exact response selector suppresses that NRC for a
functional request. CanTp/PduR delivers the complete seven-byte N-SDU to the
target's channel-1 DCM buffer before the resident's existing post-receive hook:

| target | functional DCM buffer | historical dedicated family-5 ingress | install strategy |
|---|---:|---|---|
| Camry `8965F3307000` | `FEBE5751` | `0x1FDC0002` enabled | split helper, loaded with C6 |
| Corolla `8965H1202000` | `FEBE563D` | `0x1FDC0002` enabled | helper embedded before application startup |
| Corolla `8965F1208000` | `FEBE563D` | `0x1FDC0002` enabled | helper embedded before application startup |
| Crown `8965F3012000` | `FEBE527D` | family 5 disabled | split helper, loaded with C6 |

The Crown vehicle first dynamically proved the functional transport. Follow-up
showed stock DCM teardown may clear N-SDU B0, so the maintained wire format
duplicates the private tag into durable B1. Thus loader traffic is
`07 C6 C6 index word_le32` and steering control is
`07 C7 C7 seq target_hi target_lo 00 00`. **C6 is never the recurring steering
command**; it exists only to transfer/arm the split helper on Camry and Crown.
The deterministic firmware matrix is
[`tss3_resident_control_ingress_matrix.json`](../../data/generated/tss3_resident_control_ingress_matrix.json).

The historical family-5 paths remain valuable evidence and recovery tooling,
but they are no longer the cross-variant openpilot contract. Crown production
firmware compiles family 5 out entirely, while functional `0x777` exists on all
four exact targets. Keeping one host wire/API therefore removes a gratuitous
Camry/Corolla-versus-Crown split without changing any target-local B6,
freshness, command-5, or RAM facts.

#### Unified functional runtime

The maintained runtime now uses functional `0x777` on all four exact targets.
Its common wire contract is:

```text
helper loader (Camry/Crown only): 07 C6 C6 index word_le32
runtime steering control:         07 C7 C7 seq target_hi target_lo 00 00
inactive / explicit release:      07 C7 C7 00  00        00        00 00
```

`build_tss3_unified_b6_signer.py` emits exact-target bundles for Camry F33,
Corolla H/F, and Crown F30; `tss3_unified_b6_signer.py` provides the common
preflight/install/qualify/control harness. The resident and helper are one
maintained source pair with SHA-bound compile macros selecting exact target
addresses. It is intentionally not one byte-identical multi-calibration binary:
exact call/RAM addresses and the installation geometry differ.

The recurring host API is nevertheless identical. While `CC.latActive`,
openpilot emits a changed nonzero C7 generation at the native 100-Hz
car-control cadence. When lateral control is inactive it emits sequence zero.
Receiver behavior is target-local:

- **Camry F33 / Crown F30:** the 596-byte split helper uses the road-proven
  supervised shape. A changed nonzero generation grants seven nominal 5-ms
  foreground ticks; repeated mailbox contents do not renew the lease; expiry
  or sequence zero leaves the native B6 untouched. The 600-byte transfer image
  still fits the exact 604-byte low-RAM slot.
- **Corolla H/F:** the exact low helper is now 458 bytes in its 464-byte
  target-native pocket after compacting state access and freshness arithmetic.
  It uses the same seven-nominal-5-ms host lease as Camry/Crown: a changed
  nonzero C7 generation snapshots the target and grants seven foreground ticks,
  repeated mailbox contents cannot renew the lease, and sequence zero releases
  immediately. Lease aging occurs before the native-B6 queue gate, so a stale
  command expires after nominal 35 ms even when no B6 is queued; a later B6
  cannot resurrect it. The compiled exact-H helper is emulator-regression-tested
  against a 100-Hz host / 200-Hz foreground schedule.

The common qualification ladder remains conservative: bind exact F181, prove
functional mailbox delivery, install only volatile RAM, reproduce one untouched
native B6 MAC with Toyota command 5, and only then permit C7 replacement. The
old target-specific extended-family-5 signers remain in the tree as historical
and recovery artifacts, not as the normal openpilot control transport.

> **Tester-handoff audit, 2026-09-16:** the following is the intended flow,
> not a qualified install-then-drive procedure. The current Corolla kit has
> unresolved post-startup identity-check, sensor-validation and failure-path
> defects; the port also has incomplete steering-fault/cancel handling. See
> [the offline audit](../variants/corolla-tss3-tester-handoff-audit-2026-09-16.md).

For a tester using the maintained `kai-openpilot` TSS3 branch, the portable kit
packages that ladder behind a guided launcher. Build the exact target on the
analysis checkout, copy the output directory to comma hardware, and run:

```bash
uv run --locked python tools/targets/tss3/builders/build_tss3_unified_b6_signer_kit.py \
  --target corolla-8965F1208000 --out EMPTY_KIT_DIRECTORY

# on comma, with Kai's TSS3 openpilot checkout at /data/openpilot
./tss3-unified-signer doctor
# vehicle already in NRTD / READY=0 / Park:
./tss3-unified-signer bringup /tmp/tss3-bringup
# after the command prompts: transition directly to READY/Park without OFF,
# remain stationary, then press Enter
./tss3-unified-signer replace-current /tmp/tss3-replace-current.json
```

`bringup` retains the individual fail-closed gates: stock functional-mailbox
preflight, exact-F181 NRTD install, then the READY native-MAC oracle. It merely
holds the cooperative Panda lease across the operator's NRTD-to-READY transition.
`replace-current` is the first mutation test: it requires READY plus stationary
`0x0AA`, derives the current measured angle from `0x025`, converts that angle to
the common B6 target domain, sends one fresh C7 generation, observes a signed
replacement, then sends sequence zero to release. Park remains an explicit
operator confirmation. A full EPS power cycle removes the resident and requires
`bringup` again. The launcher cooperatively hands Panda ownership back to the
managed `pandad` from the maintained openpilot branch when each command exits.

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

`ToyotaSafetyFlags.TSS3_SIGNER` selects the bounded resident-signer actuator
contract; `F33` remains its source-compatible alias. The host transport is the
common functional `0x777` C7 envelope, while target identity still determines
exact EPS scaling, RX requirements, resident placement, and signer image.

The reusable architecture is the normal openpilot division of ownership.
Functional `0x777` is the shared host carrier; actuator field semantics,
scaling, limits, signer RAM locations, freshness cells, and the EPS payload
remain target-local facts and must not transfer merely from that shared carrier.

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
object validity, or physical actuator qualification. The unified functional
runtime described above is now the maintained host transport; that transport
migration does not silently transfer the historical Camry helper's road
qualification to the new `0x777` runtime or to Corolla/Crown.

The direct-Panda lease and installer remain deployment tooling. They must not
become a second engagement policy in openpilot. No proved nondisruptive stock
READY-mode RAM placement-plus-execution path has replaced the exact NRTD
bootstrap; the earlier XCP/callback audit remains a bounded recovered-surface
negative, not a proof that no alternative could exist.
