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

Exact Camry F33, Corolla H, Corolla F, and Crown F30 all expose the same normal
runtime control ingress: classic functional request `0x777`, DCM request type 1.
Their configured functional service set is identically `10,14,28,31,3E,85`;
private C7 is therefore staged into the target's channel-1 DCM buffer, assigned
NRC `0x11`, and suppressed on the functional response path. CanTp/PduR still
performs the complete seven-byte N-SDU copy before the resident's exact
post-receive hook.

| exact target | functional DCM buffer | unified runtime profile | field installation |
|---|---:|---|---|
| Camry `8965F3307000` | `FEBE5751` | `camry-f33` | exact-F181 high-tail resident + post-startup functional C6 helper load |
| Corolla `8965H1202000` | `FEBE563D` | `corolla-hf` | exact-F181 resident + helper embedded in authenticated LocalRAM payload |
| Corolla `8965F1208000` | `FEBE563D` | `corolla-hf` | exact-F181 resident + helper embedded in authenticated LocalRAM payload |
| Crown `8965F3012000` | `FEBE527D` | `crown-f30` | exact-F181 high-tail resident + post-startup functional C6 helper load |

The recurring steering-control contract is unified C7, but the field installation
path is deliberately target-shaped. Camry/Crown use functional C6 only as a
post-startup helper transport: the authenticated boot callback installs the
high-tail resident, the resident reaches the qualified count-224 boundary, and
the host then transfers the padded helper as `07 C6 C6 index word_le32` before
arming it. C7 remains the only recurring steering-control tag. Corolla H/F keep
their earlier embedded-helper shape because the exact low helper pocket survives
startup. No packaged field target writes the helper to GlobalRAM from the boot
callback.

This boundary was restored after two 2026-09-17 healthy-F33 one-shot attempts
returned to stock application with `FEBFF9F0` cleared. A direct A/B on the same
replacement rack then ran the exact previously live-qualified 4-KiB F33 replay
payload (`48f269ae...`) and recovered its 406-byte resident byte-exact with
`verdict=abi_preserving_runtime_and_source_terms_live`; retained raw record: `targets/camry-2026/raw-20260917/replacement-rack-old-replay/run.json`. That proves the
replacement rack, exact F33 boot calls, and high-tail retention still work. It
does **not** by itself distinguish a fault in the newer resident from a fault in
the subsequent boot-context helper staging, but it invalidates the field design's
GlobalRAM justification: `FEF07C00` had only been proven under recovered
**application** MPU contexts, not the active boot callback context. The
self-dispatching/GlobalRAM payload remains an experimental artifact, not a field
install path.

The selected resident is copied to the common retained high tail
`FEBFF9F0..FEBFFBFB`. The selected helper is temporarily parked at
`FEF07C00..FEF07FFF`, the final 1 KiB of GlobalRAM. Exact supported images have
zero aligned CodeFlash pointer literals and zero recovered application data
references into that transit span. Their byte-identical MPU table places the
span in region 12 (`FEC00000..FFFFFFFC`) with MPAT `0xB8` in both recovered
application contexts, so the high resident can read it after startup. Cold-reset
initialization clears all GlobalRAM before the authenticated payload runs, so it
precedes rather than clobbers this staging write. The transit buffer is used only
until the selected resident installs its helper into the target-native low-RAM
pocket.

Corolla can install its 458-byte helper into `FEBF0000..FEBF01C9` before
application startup because exact H/F startup-survival analysis excludes that
range from startup writes. Camry/Crown instead use the restored split field path: the high resident reaches
count 224 first, then the host transfers the helper over functional C6 and arms
it. This keeps helper installation out of the boot callback while preserving C7
as the recurring steering-control wire. The runtime backends now deliberately
diverge after that common install boundary. Crown retains the pre-SecOC command-5
signer. Exact Camry F33 uses the post-authenticated route44 backend described
below and does **not** invoke command 5 during lateral control.

For F33/F30, `install` therefore proves only resident survival/initialization and
`qualify` performs the C6 helper transfer plus byte-exact readback/arm. Crown then
qualifies its native command-5 MAC oracle. Camry instead waits for an ordinary
Toyota B6 to pass stock SecOC and reach route44 while C7 is released, proving the
post-auth hook is observing native authenticated publication without mutating it.

#### Unified C7 runtime with target-shaped field installation

The experimental all-target payload remains retained for research. The field
path is target-shaped. Current field component sizes are:

- Camry F33: 522-byte resident + 218-byte post-auth helper, padded to 600 bytes for C6;
- Crown F30: 522-byte resident + 594-byte command-5 helper, padded to 600 bytes for C6;
- Corolla H/F: 522-byte resident + 458-byte embedded helper.

The recurring host API is consequently only:

```text
runtime steering control:  07 C7 C7 seq target_hi target_lo 00 00
inactive / explicit release: 07 C7 C7 00  00        00        00 00
```

While `CC.latActive`, openpilot emits a changed nonzero C7 generation at the
native 100-Hz car-control cadence. When lateral control is inactive it emits
sequence zero. Every profile uses the same seven-nominal-5-ms supervised lease:
changed nonzero generations renew it, repeated mailbox contents do not, and
expiry or sequence zero leaves native B6 untouched. Corolla's compiled helper
continues to have the emulator regression covering the 100-Hz host / 200-Hz
foreground schedule, seventh-tick expiry, zero release, wrap, and empty-queue
aging.

`build_tss3_unified_b6_signer.py --target all` emits one universal staging image,
one 4-KiB authenticated payload, and thin exact-target metadata wrappers used
only for F181/DCM-buffer attestation and tester presentation. All four wrappers
pin the same staging SHA and the same payload SHA. Legacy target-specific and C6
loader implementations remain in the tree only as historical/recovery tooling.

The field qualification ladder remains conservative: bind exact F181, prove
functional mailbox delivery, and install only volatile RAM. Crown/Corolla retain
their command-5 native-MAC qualification. Camry F33 instead proves a native B6
has completed stock SecOC and route44 publication while C7 is released. Only
then may C7 own the application target. The old target-specific extended-family-5
signers remain in the tree as historical and recovery artifacts.

#### Camry F33 post-authenticated B6 ownership

The Sep-17 road trace exposed the remaining flaw in the pre-SecOC signer model:
an occasional command-5 miss left one Toyota-native B6 target untouched, and the
next openpilot replacement crossed F33's 78-raw/effective-sequence target-step
plausibility limit. The replacement-rack route recorded 11 recoverable
`CEE7C -> CAFB -> CAFC -> 0x030 B16[0]` events while C7 itself remained smooth
(maximum observed recent step 3 raw). Historical route `8d` contains the same raw
inhibit four times; the older CarState simply did not report it.

The field Camry backend therefore removes per-frame signing from runtime. Stock
B6 now runs unchanged through the exact native receive/SecOC path:

```text
native B6 -> profile-2 queue -> stock freshness/MAC verification
          -> 8F906/8F546 -> 7D72C -> route44 raw COM at FEBE4BFF
          -> [volatile post-auth helper: B3/B4:B5/B6.bit2/B8/B9 only]
          -> 4BD46 generated-COM unpack -> 58074 stage -> BCD62 snapshot
          -> ordinary F33 cooperative controller
```

A changed nonzero C7 generation caches its target for the complete supervised
lease, so later C6/other DCM traffic cannot leak one native target. While that
lease is live, the helper preserves native B3 high bits, selects Target Lateral
ID11, copies the cached C7 target byte-exact into raw B4:B5,
clears signal265, and sets contributions B8/B9 to 100. Native B7 application
sequence, B28..B31 SecOC trailer, secured queue bytes, freshness records, and
ICU-S result are never modified. With C7 zero/expired, the raw route44 payload is
left stock. Consequently there is no command-5 latency/failure path capable of
letting a different native target appear between openpilot targets. This backend was then road-qualified on exact F33 route
`000000ee--65bdece411`: 57,437 active C7 frames over ~574 s of active lateral and
101,809 `0x030` frames produced **zero** B16 command-inhibit assertions, versus
11 moving B16 rises in ~147 s on the immediately preceding pre-fix route. The fix
therefore remains at the native ~100-Hz C7 cadence and is live-demonstrated for
the continuity failure it was designed to remove.

> **Tester-handoff audit, 2026-09-16:** the audit found real host-side defects in
> post-startup resident attestation, sensor freshness/validity, Park enforcement,
> retry/preflight phase handling, explicit release, and failure evidence. Those
> host defects are now fixed and regression-tested. Exact H/F
> `EPS_FAULT_INHIBIT` is also reported as an ordinary temporary steering fault in
> opendbc. This makes the kit suitable for the bounded **stationary signer
> qualification** below; it is still not an install-then-drive all-clear.
> Corolla now implements software-requested stock-ACC cancellation in the normal
> openpilot shape by cloning native bus-1 `0x101`, asserting only
> `BRAKE_PRESSED`, and recomputing the Toyota checksum. That receiver behavior is
> not yet live-qualified on Corolla; cruise-main availability also remains
> evidence-bounded, and physical steering/coexistence behavior is untested. See
> [the audit](../variants/corolla-tss3-tester-handoff-audit-2026-09-16.md).

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
preflight, exact-F181 NRTD install, then READY runtime qualification. On exact
Camry, peer recovery is deliberately **operator paced** rather than chained:
`bringup` keeps one cooperative Panda lease across the complete guided command and
waits for the operator before restarting Brake/EPB only. The Brake stage is intentionally kept identical
to the field-proven standalone UdsClient procedure: `10 02` with a 1.0/2.0 s client,
then up to two `11 01` attempts using fresh 0.35/0.35 s clients with a 50-ms pause
after the first exception, followed by a 2-s quiet wait and bounded F181 polling using
fresh 0.25/0.25 s clients every 250 ms for up to 6 s. No additional EPS/F181 pre-reads,
custom ISO-TP helper, CAN-FD-auto changes, or other diagnostics are inserted. The operator waits as long as needed before restarting FRC only;
after exact `8646F3315000` returns the launcher simply waits before final
DRCC-state verification; Panda ownership remains unchanged until the command exits.
The operator can wait arbitrarily long between stages. No DTC clear, SecurityAccess,
EPS reset, or EPS power cycle is part of this guided recovery. Final FRC
`0x1903/0x1905/0x1906` must show distance-control mode, Cruise Control Permission
allowed, and ACC-not-available clear before the guided command succeeds.
Non-Camry targets skip this lifecycle step. `replace-current` is the first mutation test: it requires READY plus stationary
`0x0AA`, derives the current measured angle from `0x025`, converts that angle to
the common B6 target domain, sends one fresh C7 generation, observes a signed
replacement, then sends sequence zero to release. On Corolla the guard also
requires a fresh decoded Park state from `0x127` or the retained `0x3BF` fallback
carrier; wheel-fault flags and stale motion/angle samples are rejected. A full
EPS power cycle removes the resident and requires
`bringup` again. The launcher cooperatively hands Panda ownership back to the managed `pandad` when
the command exits. A guided `bringup` deliberately keeps the same lease across its
operator-paced stages; lease ownership is not part of Toyota recovery semantics.

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

The September-10 steering samples used conventional cruise, but that boundary is
now superseded by the September-18 exact-car recovery and road qualification.
DTC clear alone still does **not** recover DRCC after the EPS programming
transition. The first successful recovery session's chronology was FRC reset,
then Brake/EPB reset, then FRC reset again; that chronology proves the relevant
state is volatile and dependency-sensitive, but it did not isolate the minimum
reset set because the initial FRC probe was part of the same session. A later
operator-paced field run reached the same final healthy FRC state after Brake and
then FRC were restarted with long quiet intervals. The maintained launcher therefore
stops trying to infer a fixed automatic cadence: it exposes/operator-prompts the
Brake and FRC stages separately, preserves the exact field-proven Brake reset-and-return
procedure, keeps one cooperative Panda lease throughout, and lets the operator decide
when the network has settled before continuing. The subsequent route
`0000010c--506d7277c7` demonstrates 919.572 s / 19.772 km of stock adaptive cruise
overlapping openpilot lateral with factory lateral request/result IDs at 0 and
openpilot `longActive` false. The historical `recover-drcc` command remains for
DTC evidence only.

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
