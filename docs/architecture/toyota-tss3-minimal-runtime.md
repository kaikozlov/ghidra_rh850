# Toyota TSS3 minimal openpilot runtime

This report records successive runtime architecture checkpoints. The
September-21 request-plane design supersedes the earlier C7/B6 design below;
later host/reporting reviews are recorded in
[the port report](../variants/camry-2026-tss3-opendbc-port.md#8-host-bring-up-result-reporting-audit-2026-09-26).
Transport sizes, source pins, and deployment notes belong to their checkpoint,
not an evergreen wire specification.

The [capability matrix](../variants/camry-2026-capability-matrix.md) separates
retained qualification evidence from later implementation changes. In
particular, the [September-18 road witness](../variants/toyota-tss3-openpilot-bounty-evidence.md)
does not by itself qualify the superseding request-plane configuration.

## Current shared request-signer contract

The maintained RAM runtime is the request signer exposed by
`tools/toyota ram`. Openpilot owns the complete 28-byte `0x08A` application and
its publication cadence. It sends that application to the EPS resident in four
ordered classic-CAN `0x777` frames:

```text
8s || application[0:7]
9S || application[7:14]
As || application[14:21]
BS || application[21:28]
```

`s` and `S` are the low and high nibbles of one 8-bit transaction sequence.
Fragment zero restarts assembly; missing, repeated, reordered, or
mixed-sequence continuations are rejected. The host sends no trip, reset,
message counter, native B26, or native FV4.

The EPS resident reads Toyota's authenticated trip/reset epoch, advances a
private volatile `0x08A` message counter, calls the target's stock freshness
encoder and ICU-S command 5, and returns one standard classic-CAN `0x7A9`
response containing status plus `FV4||MAC28`. Openpilot appends that trailer
without reconstructing or interpreting freshness.

The transport, host interface, resident, helper, staging image, and
authenticated payload are shared by every registered Camry, Crown, and Corolla
H/F target. The staging shell selects one verified 108-byte runtime config from
the application software ID at CodeFlash `0x20860`; unknown IDs stop before
application handoff. Target metadata remains separate for F181, CodeFlash hash,
Panda bus, and installation routing.

Panda checks the complete application shape and ordinary angle/acceleration
limits, blocks native FRC `0x08A` only while host ownership is active, and
fails open after 100 ms. It does not queue native generations or compare
B26/FV4. Native FRC `0x08A` remains an engagement/presence input and Brake
`0x081` continues normally.

On F3 targets, the resident's 36-byte state remains at
`FEBF025C..FEBF027F`, below the application SID23 exclusion beginning at
`FEBF0288`; command-5 scratch occupies `FEBF0280..FEBF02E7`. Corolla H/F uses
its registered resident and scratch locations. A full EPS power cycle removes
the runtime.

The Panda firmware image is part of this runtime contract. Any nested-opendbc
safety change that alters the Toyota TX whitelist or hooks requires rebuilding
and deploying `panda_h7.bin.signed`; updating only openpilot/opendbc source is
insufficient.

The remainder of this note retains earlier C7/B6 architecture and field
evidence where useful. It is historical, not the maintained RAM-runtime
contract.

At the earlier C7/B6 checkpoint, the initial integration goal was narrower
than a complete TSS3 port: reproduce the demonstrated lateral result on exact
F33 with an upstream-shaped runtime. The paragraphs below preserve that
checkpoint, not a restriction on the later request-plane implementation.

At that checkpoint, longitudinal was a separate layer and remained stock-owned.
The September-16 request-plane audit supersedes the former `0x160` actuator
interpretation: `0x08A` is the shared TSS3 application-request carrier for both
lateral and longitudinal requests, while `0x160` is retained only as FRC-origin
state/evidence.

## Runtime boundary (superseded C7/B6 bring-up state)

The boundary below is the pre-2026-09-21 C7/B6 bring-up path, retained as
historical architecture; the supersession above replaces it:

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

The table records the superseded C7/B6 bring-up baseline. After the
2026-09-21 supersession the host emits the complete `0x08A` application
instead of the C7 sideband; the Panda relay/transport and vehicle-state
decoding rows are retained here unchanged from that baseline.

| repository | required for the demonstrated lateral path | not required by that path |
|---|---|---|
| openpilot | After CarParams identifies the F33 safety profile, disable Panda `canfd_auto` on unsplit Toyota-B bus 1. No controls/model changes. | direct-Panda lease; `CanData.fd` schema/logging; SecOC-key Params; controller arming Params; changes to `card.py` or `controlsd` |
| opendbc | F33 platform identity and DBC; TSS3 state decoding; F33 CarParams; direct C7 angle encoder; native 20 Hz TSS3 RadarInterface from recovered `0x180..0x185` geometry/motion fields; Toyota F33 safety RX state, angle checks, TX whitelist, and normal relay blocking | host construction or signing of B6; host freshness/MAC state; diagnostic/oracle arming; controller-side permission vetoes; unmapped object-class/reliability metadata |
| Panda | Preserve the received FDF and BRS attributes when software-forwarding across the relay; sanitize the queue-private forwarding markers on host input and validate the original host checksum | relay-close/debug exceptions; F33-specific safety state outside opendbc; global 70% data sample point; global EFBI; logging the per-frame FDF bit to cereal |

## Longitudinal layer (pre-supersession baseline)

This section records the longitudinal boundary as it stood before the
2026-09-21 request-plane supersession above; native-longitudinal authority
remains open in [../status/OPEN_QUESTIONS.md](../status/OPEN_QUESTIONS.md)
(OQ-052). At this baseline, native longitudinal was deliberately **not
advertised** on the TSS3 platforms. The recovered request/result split places
the TSS application
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
Brake/PCS/AEB coexistence validation. At this baseline, stock Toyota
longitudinal was the only runtime path.

### Why the openpilot transport exception was lateral-only at this baseline

The TSS3 host-control PDU at this baseline was the 8-byte Classical functional
frame `0x777` on stock Toyota-B Panda bus 1:

```text
07 C7 C7 seq target_hi target_lo 00 00
```

The first `07` is the ISO-TP single-frame PCI length. CanTp removes it and
places the seven-byte N-SDU `C7 C7 seq target_hi target_lo 00 00` in the EPS
functional DCM buffer. Panda permits only this exact bounded C7 envelope; it
does **not** expose arbitrary functional diagnostics while driving. The former
HUD `0x412`, brake-cancel `0x101`, longitudinal `0x160`, and historical
extended-family-5 `0x1FDC0002` steering transmissions were not part of the
openpilot runtime surface at this baseline.

The same physical network carries native CAN-FD traffic including `0x08A`.
Route 45 showed that sticky bus-global `canfd_auto` can promote a short
Classical host frame to FD, so functional C7 still needed the target-scoped
Classical transport treatment on bus 1. At this baseline no equivalent host
transport exception was needed for longitudinal because openpilot emitted
neither `0x08A` nor `0x160`.

Adding `CanData.fd` remains useful for exact logging and arbitrary short FD
host TX, but the demonstrated controller sends no short FD PDU. It is a
transport enhancement, not a dependency of this lateral baseline.

### Cross-variant resident control ingress

Exact Camry F33, Corolla H, Corolla F, and Crown F30 expose the same physical
request contract: four classic standard-`0x777` records accepted by the stock
functional CAN rule. The helper reads those records through a private cursor
over the software RX ring; it does not depend on or modify the stock consumer.
Header nibbles `8..B` are intentionally invalid ISO-TP PCI types, so no CanTp
reassembly, PduR copying, DCM buffer, service lookup, or diagnostic response
state is part of the recurring request path.

The resident executes the target's stock foreground calls unchanged and invokes
the helper only after the complete foreground body and stock tick-counter
update. The older request signer inherited a target-specific mid-receive splice
from the B6 replacement experiments; that splice and its copied aggregate/Rx
call graphs are no longer part of the maintained runtime.

#### Shared P1M-E RAM-execution invariant

This runtime does not depend on a Camry-only processor feature. Camry F33 and
Crown F30 use the 1-MiB `R7F701381`; Corolla H/F use the 1-MiB `R7F701383`.
Both are RH850/P1M-E DPS variants with the same 160-MHz core, 16 MPU channels,
128 KiB PE1 Local RAM, and 64 KiB Global RAM.

The manual's architectural instruction-fetch map names the self Local-RAM view
`FEDE0000..FEDFFFFF` and Global RAM. Exact firmware control flow and retained
live payloads independently prove instruction fetch through Toyota's PE1 view
`FEBE0000..FEBFFFFF`; the Ghidra profile therefore maps the self view as a byte
alias of the PE1 backing and marks both views executable. Execution permission
still depends on the active MPU region: the recovered payload regions use
`MPAT=0xB8` for supervisor read/write/execute or `0xA8` for supervisor
read/execute.

Publishing newly written RAM code requires the G3M ordering from the CPU
manual: complete the stores, perform a dummy read from the written region,
execute `SYNCP`, execute `SYNCI`, then branch to it. The processor can
speculatively fetch up to 48 bytes beyond the code body, so that trailing range
must also be initialized and access-permitted. Every maintained RAM-code
builder now validates the assembled dummy-read/`SYNCP`/`SYNCI` sequence; images
whose destination lacks existing safe tail bytes carry a 48-byte zero guard.
Global-RAM data writes are hardware-coherent/write-through on P1M-E, but that
does not replace instruction-cache publication.

RAM clearing is reset-class-specific. `STAC_LM0` controls local-RAM
initialization for the reset classes listed by the device manual; it is not a
blanket promise that every reset clears every local-RAM view. Target builders
must continue to prove the exact boot/reset path and startup write survival
from firmware.

What remains target-specific is a small signer/I/O ABI: RX ring and producer,
authenticated trip/reset cells, state/scratch placement, freshness encoder,
command-5 wrapper/globals, lower CAN writer and transmit handle. Startup and
foreground addresses are not curated profile data: the builder resolves the
unique coordinator and common 92-byte foreground machine shape from each exact
CodeFlash image, then emits its decoded startup span and ten stock calls into
the selected runtime config. Exact CodeFlash hashes still bind that derivation.

The shared binary currently contains three runtime configs for four targets;
Corolla H/F resolve to the same application software ID and ABI:

| exact target | Panda bus | RX ring / producer | resident state | response lower handle | signer scratch | command-5 globals |
|---|---:|---|---|---:|---|---|
| Camry `8965F3307000` | 0 | `FEBE4038` / `FEBE48F8` | `FEBF025C` | 53 | `FEBF0280` | `FEBF13A0` |
| Crown `8965F3012000` | 1 | `FEBE3E98` / `FEBE475A` | `FEBF025C` | 51 | `FEBF0280` | `FEBF13A0` |
| Corolla `8965H1202000` | 1 | `FEBE3F4C` / `FEBE480C` | `FEBFF9F0` | 50 | `FEF07F98` | `FEBF1264` |
| Corolla `8965F1208000` | 1 | `FEBE3F4C` / `FEBE480C` | `FEBFF9F0` | 50 | `FEF07F98` | `FEBF1264` |

All four default to the same four-message classic standard-`0x777` request
codec, standard-`0x7A9` response, and 36-byte command-5 authentication domain.
Headers `8s`, `9S`, `As`, and `BS` encode ordered fragments 0..3 while
repeating the low/high nibbles of the complete 8-bit transaction sequence. Each
message contributes seven consecutive bytes, so the helper reconstructs all 28
application bytes verbatim.

The common resident code is bounded below the runtime-config block in
`FEBFF9F0..FEBFFBFB`. The helper remains bounded to 920 bytes (`0x398`) because
Corolla scratch begins at `FEF07F98`; zero relocations and the common bound are
checked from linked artifacts. The runtime config fixes an earlier portability
defect in which the shared helper used F3 command-5 globals on Corolla.

The one-message canonical-reconstruction codec is retained only as an explicit
experiment. Its stock-TSS3 steering experiment was reported broken, so it is
not a default or a fallback. `--codec compact` on `tools/toyota ram build` or
`tools/toyota ram kit` emits a compact-only helper and includes its optional
Python codec module. Default kits omit that module. The reported result selects
the safe default but is not promoted here to identity-bound vehicle
qualification without its capture.

#### Historical C7/B6 installation checkpoint

At the superseded C7/B6 checkpoint, recurring steering control was unified C7
but field installation remained target-shaped. Camry/Crown used functional C6 only as a
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
application contexts, so the high resident can read it after startup. For the
exact supported boot path, firmware startup clears GlobalRAM before the
authenticated payload writes this transit buffer. That ordering is an
exact-image firmware fact, not a universal consequence of all P1M-E reset
classes. The transit buffer is used only until the selected resident installs
its helper into the target-native low-RAM pocket.

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

For current builds and tester packages, use only the registry-backed public
surface:

```bash
tools/toyota ram list
tools/toyota ram build corolla-8965F1208000 --out build/out/corolla-f-request-signer
tools/toyota ram kit crown-8965F3012000 --out EMPTY_KIT_DIRECTORY
tools/toyota ram kit all --out EMPTY_KIT_SET_DIRECTORY
```

Every kit contains one target-bound request signer, its metadata, the common
runtime host, peer recovery, and one launcher:

```bash
./tss3-request-signer doctor
# NRTD / READY=0 / Park / stationary
./tss3-request-signer install /tmp/tss3-request-signer-install.json
# transition directly to READY/Park without powering EPS off
./tss3-request-signer status /tmp/tss3-request-signer-status.json
./tss3-request-signer self-test /tmp/tss3-request-signer-self-test.json
./tss3-request-signer benchmark-100hz 200 /tmp/tss3-request-signer-100hz.json
# exact-F33 Camry startup-catcher integration only
./tss3-request-signer ui-bringup /tmp/tss3-request-signer-ui-run
```

If the programming transition leaves peer state unhealthy, `recover-peers`
uses the same Brake/EPB then FRC recovery on every supported TSS3 kit. The
launcher derives the EPS F181 and diagnostic bus from that kit's request-signer
metadata; recovery is not a Camry-only package path.

The hardware qualification remains intentionally short:

1. Bind the bundle to its application F181 and CodeFlash hash; never substitute
   a related calibration.
2. With the vehicle stationary in Park and READY low, install only the volatile
   payload. The one pre-helper F181 response proves the application handoff.
3. Transition directly to READY without powering the EPS off. Require `status`
   to receive a successful fresh signer response on `0x7A9`.
4. Require `self-test` to return one independently fresh native-MAC `0x08A`,
   then require the 200-request 100-Hz benchmark to receive one successful
   signer response for every request with no timing or transport errors.
5. A full EPS power cycle removes the resident; repeat installation afterward.

Post-activation EPS F181 and SID23/RMBA are not signer-liveness gates. The
resident can continue signing while the stock diagnostic endpoint is
unavailable; installation, status, self-test, and throughput qualification
therefore use the signer's actual `0x777` request / `0x7A9` response path.

This proves RAM survival, exact target calls, command-5 signing, and the
classic-CAN request/response rate on that ECU. It does not transfer road
qualification between targets, prove steering authority, or authorize driving.

The former direct-B6/C7 builders and target-specific kit packagers are
research-only. They are not alternate current installation paths and are not
packaged by `tools/toyota ram kit`.

### Exact-Camry startup-catcher integration

A 2026-09-20 exact-Camry experiment armed the request signer while the vehicle
was fully OFF, repeatedly offered application EXTENDED, waited for the first
completed `50 03`, sent one `10 02`, and installed from the caught bootloader.
After application return it required READY/Park/stationary, checked peer health
without resetting either peer, and ran one fresh-signing self-test. Those runs
showed that this startup-caught path could preserve healthy Brake/FRC state. The
current exact-F33 Camry kit packages this backend as `ui-bringup`, `ui-resume`,
`ui-worker`, and `ui-resume-warm`; other target kits do not carry it.

FRC `0x1905` **Cruise Control Permission Flag** and `0x1906` **Main Switch
Recognition Flag** are operational cruise state, not persistent health latches. In a
verified healthy startup run they were initially false (`1905=8000`,
`1906=e000e0008000`) and later became true (`8080` / `e080e0008000`) after a normal
drive with **no ECU reset**. Therefore startup success does not require those bits to
already be asserted. They remain telemetry. The startup peer-health gate instead uses
the pre-helper exact EPS F181, exact FRC/Brake identities, Brake `0x102D`
fail-status/fail-control clear, and `0x102F` EPS-communication-open clear; the
succeeding signer self-test supplies the functional post-activation EPS proof.
No DTC clear, peer reset, EPS reset, or EPS power cycle is part of a healthy
`ui-bringup` run.

The experiment used a native `pandad` startup catcher plus the openpilot-side
`Tss3OracleAutoArm` watcher.
The original catcher waited for a Panda ignition false->true edge before
transmitting. The 2026-09-22 deep-sleep/proximity experiment closes a better
pre-start trigger on exact F33: from a verified zero-CAN state, ordinary approach
with the normal key produced bus0/bus2 `0x45A` as the first mirrored wake frame,
with the rest of the wake-active OFF set and `0x00F` following immediately.

The experimental catcher preloaded ELM327 while OFF and remained in normal
Panda power-save. Logical bus0 is already the always-awake main bus, so observing
native bus0 `0x45A` starts a **low-rate prewarm** without waking the other Panda
CAN transceivers: `10 03` is offered at 10 Hz on bus0 while the vehicle is already
wake-active. A later native ignition edge promotes the same attempt to the
existing 50-Hz startup catch, disables Panda power-save at the same point as
before, and sends `10 02` only after an exact `50 03`. Ignition remains a full
fallback if the proximity wake frame is ever missed.

The prewarm does not run indefinitely. If native bus0 traffic goes quiet for
three seconds it re-arms immediately. If wake-active traffic persists without an
ignition edge, prewarm transmission stops after 60 seconds and waits for either
ignition or a real return to sleep before another proximity-triggered prewarm can
start. Thus true deep sleep retains the same Panda power-save behavior and zero
CAN traffic; the only added traffic occurs after Toyota itself has already woken
the visible network.

After the native catcher reached PROGRAMMING it published a cooperative handoff
marker and the warm uploader acquired the direct-Panda lease. Its evidence
recorded wake-relative and ignition-relative timing, including wake to first
`10 03`, wake to ignition, `50 03`, and `10 02`. This remains exact-Camry
historical evidence, not another maintained kit workflow.

The former direct-C7 mutation test required READY/stationary state, derived a
target from measured angle, sent one C7 generation, observed a signed
replacement, then sent sequence zero to release. Those C7/B6 lifecycle and
topology details belong to the superseded runtime and do not apply to
`tss3-request-signer`.

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
contract. The maintained host transport is the four-frame functional `0x777`
request described above. Target identity determines exact EPS scaling, RX
requirements, resident/scratch placement, diagnostic bus, transmit handle,
firmware calls, and payload identity.

The reusable architecture is the normal openpilot division of ownership.
Shared transport does not make target-local actuator semantics, scaling,
limits, freshness cells, or firmware addresses transferable.

## Camry audit checkpoints (historical snapshots)

The September-15 retained-evidence audit superseded the preceding “essentially
complete” assessment. At that checkpoint the maintained architecture was still
C7; the 2026-09-21 supersession above replaced it. The audit corrected the
implementation and evidence boundaries as follows:

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
operator-paced field run reached the same final healthy FRC state after Brake
and then FRC were restarted with long quiet intervals. The current
`recover-peers` command exposes those Brake and FRC stages on every supported
TSS3 kit, preserves the field-proven Brake reset-and-return procedure, and
keeps one cooperative Panda lease throughout. The subsequent route
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
become a second engagement policy in openpilot. Although EPS, Brake/EPB, and FRC
can enter and leave programming while the car remains READY, that does not make
the authenticated EPS RAM-payload bootstrap a READY-mode install path. The
maintained installer therefore retains the exact NRTD prerequisite and direct
NRTD-to-READY transition without EPS power loss.
