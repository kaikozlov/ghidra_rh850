# 2026 Camry openpilot capability matrix and qualification handoff

**Current checkpoint: September 16, 2026, after the shared request-plane audit and unified signer migration.**
This incorporates the retained-evidence review, the correction that removes `0x160`
from the native-long actuator contract on both Camry and Corolla, and the move from
target-specific extended C7 ingress to the common functional-`0x777` C7 contract. Detailed
reasoning and reproducible sources are in
[the port evidence review](camry-2026-port-evidence-review.md) and the
[TSS3 vehicle-movement arbitration note](../architecture/toyota-tss3-vehicle-movement-arbitration.md).

The exact target remains EPS `8965F3307000 / 8A3113303100`. No vehicle commands,
RAM installation, or persistent firmware writes were performed during this audit.
Openpilot `fa3ee6b85` pins opendbc `82bbbf57`; ordinary openpilot engagement,
CarState/CarController ownership, and Toyota Panda safety remain the architecture.

## Current capability matrix

| Capability | Implemented / demonstrated | Actual remaining boundary |
|---|---|---|
| Identity and vehicle state | Exact F181 table/resolver; target-native angle/rate, driver torque, wheels, READY, gear, cruise state, body/BSM; conventional `0x251=0x88/0x90` exposed through `cruiseState.nonAdaptive` | Other firmware needs its own identity/compatibility evidence; exact-F33 current fault reporting is described separately below |
| Steering faults | Current `0x030 B6[2]`, cooperative command inhibit B16[0], and angle inhibit B19[0] feed normal temporary-unavailability reporting; 144 stock-instruction assertions cover sources, RTE/wire binding, readiness and recovery | Lossy command-inhibit projection merges a self-clearing failure and a latched failure. Do not invent a permanent-fault classification or transfer F33-specific bits to another calibration |
| Driver interaction | Same-car torque sign and 0.6 N·m steering-pressed policy retained | Physical override/release on the final runtime still needs qualification; this threshold is not an OEM single-comparator claim |
| Vehicle model | Absolute steering-ratio default 15.3; **tire-stiffness baseline remains 0.7933** because paramsd's ~1.0 is a multiplier of CP stiffness; actuator-delay default remains 0.18 s | Identical cached lagd estimates on two routes are not independent delay measurements |
| Historical lateral authority | September-10 C7/resident/native-B6 configuration physically steered on routes `8d` and `93` | Temporary repin and historical helper/image; selected working intervals use conventional cruise, not demonstrated adaptive cruise |
| Host-command loss | Unified functional-`0x777` split helper is 572 bytes in the existing 600-byte transfer image; changed C7 generation renews seven nominal 5-ms foreground ticks; unchanged generation expires; zero releases immediately | Lease semantics transfer from the road-proven supervised helper, but the new functional-`0x777` binary/transport combination is **not yet live-qualified** |
| Stock harness | Source-pinned September-11 logs put Toyota Bus-1 FRC `0x020/0x160/0x230/0x440` on camera/source bus2, radar objects downstream on bus0, and Toyota Bus-4 `0x08A/0x0C9/0x0CA` plus chassis `0x025/0x101/0x412` on unsplit bus1; unified C7 uses classic functional `0x777` on Panda bus1 | These incident-era logs establish placement, not healthy steering. Raw Panda bus numbers from the temporary repin must not be compared without network-role normalization; the functional-C7 runtime still needs healthy-rack qualification |
| HUD and automatic cruise cancel | Native unsplit-bus messages are preserved; read-only HUD state uses bus1. Wrong-bus `0x412`/`0x101` transmissions and safety permissions removed | **A genuine automatic-cancel command remains unresolved.** Full three-bus analysis recovers `0x1B2` switch-event mirrors, not receiver acceptance; all 58 historical host-cancel episodes are confounded by physical driver input. A separate 77-native-release scan finds three edges without decoded driver assertions, but none contains a host cancel request or establishes a sender contract. The same-generation factory circuit identifies Hybrid Control as the primary cruise-switch owner; the retained Camry MG update is a different ECU. HUD replacement is also unqualified; neither is solved by a wrong-bus duplicate |
| Stock-ACC coexistence / recovery | Packaged recovery preserves pre-clear DTC evidence, validates ISO-TP/DID lengths, requires distance-control mode plus genuine FRC permission and clear ACC-unavailable state | Same-cycle DRCC restoration with RAM signer retained is not observed; historical lateral proof does not close this combination |
| Native longitudinal | **Not advertised on Camry after the September-16 role audit.** The former `0x160` encoder is historical/RE code. `0x08A` is the established TSS request-side plane; B8:B9/B11:B12 form the indistinguishable signed16 ×0.001 upper/lower acceleration-request pair. Brake-owned `0x081` adds employed-source longitudinal ID B6[5:0] and result acceleration B20:B21 candidates, giving the first coherent selected-request→employed-result layout | Exact upper/lower A/B ordering remains unresolved. B6/B7 now strongly fit the two packed request-ID/allocation bytes (ID bits7:2, allocation bits1:0); shift/EPB/override/priority metadata and `57D3` validity remain unresolved. Stock Toyota-B leaves `0x08A` unsplit, so a clean source-suppression/sole-emitter boundary is still required before native long. Do not revive `0x160` or compete with stock `0x08A` |
| Stock longitudinal ownership | Native `0x160` is retained for evidence/state only; Camry and Corolla both keep Toyota `STOCK_LONGITUDINAL` even when the Alpha Long toggle is requested | The former modified-`0x160` handoff is historical on both platforms. Native long now depends on obtaining clean ownership of the shared `0x08A` request plane, not reviving the old encoder |
| Radar decoder and lifecycle | Normal bus0 radar path enabled for exact Camry: independently anchored units/sign; source start/end flags, raw-state-zero rejection, complete-cycle assembly and track retirement on data loss. 20,323 held-out updates with zero reported CAN errors | On-vehicle fusion/control qualification remains; individual nonzero state names and optional confidence/class metadata are unassigned; signed13/14 velocity widths remain indistinguishable |
| Panda enforcement | Absolute ±1745-raw C7 limit is enforced in addition to rate limits; the TSS3 host TX surface is exactly classic `0x777/8` on bus1 with `07 C7 C7 seq target_hi target_lo 00 00`, and rejects arbitrary functional diagnostics plus host `0x08A`/32-byte `0x160` replacement; unsplit HUD/brake TX remains rejected | Unit/replay validation is not an on-car safety qualification |
| Deployment | Unified TSS3 signer kit now builds exact Camry/Crown split-loader and Corolla embedded-helper variants around one functional-`0x777` C7 host contract; no persistent patch or SecOC-result bypass is required by its intended contract | Exact stock-CodeFlash combination, functional mailbox, native-MAC oracle, cadence, command loss and recovery must be qualified together; older per-target kits remain historical/recovery artifacts |

## Independent radar evidence

The previous range and range-rate correlation was insufficient: both quantities
were scaled too large by the same factor. Current reconstruction uses an
independent raw-object-byte fixture with 17 SHA-256-pinned rlog segments:

| Independent observation | Result |
|---|---|
| Range versus vision lead, 1,953 selected associations | r=0.998518; slope=1.029071; median absolute error 0.799 m |
| Relative speed versus vision speed minus ego speed | slope=0.992347; median absolute error 0.260 m/s |
| Off-center lateral position, held out of association scoring, 240 observations | slope=0.982563; median error 0.451 m versus 1.798 m with the sign inverted |
| Calibrated gyro versus stationary-object lateral derivative, 27,602 continuity-qualified pairs | r=0.843106; implied 0.038909 m/count, supporting 0.04 rather than 0.05 |

Object associations and stationary classification remain inferred, not OEM
validity/identity labels. See `data/generated/camry_2026_radar_anchors.json` and
`tests/verify_camry_2026_radar_anchors.py`. All source radar frames are checked
against native Profile-5 integrity during extraction. The corrected full August
join consumes repeated counter occurrences rather than overwriting them:
30,532 / 35,994 complete four-record bank bursts.

## Validation checkpoint

The combined Toyota state/controller tests, CAN tests, Toyota safety tests,
generic car interfaces, docs, platform configurations and vehicle-model tests
pass **617 tests with 3,186 subtests**; 262 existing tests are skipped by that
selection. Toyota Python lint passes. The dedicated Camry firmware/package,
compiled-helper liveness, independent radar anchors, full object reconstruction,
recovery transport, and original-log topology checks also pass. The exact
commands and final evidence identities are recorded in the review document.

## What still constitutes completion

**Lateral authority is demonstrated, but lateral plus stock adaptive cruise on
the final installation is not.** A healthy, exact-identity rack on stock
CodeFlash and stock Toyota-B must establish the supervised RAM lifecycle,
untouched-native-MAC equality, command-loss/zero release, and genuine DRCC
coexistence. An automatic cruise-cancel mechanism still needs a supported
implementation; the earlier fake replacement is not a qualification candidate.

**Camry native longitudinal is no longer advertised as alpha.** The retained
role audit invalidates the implemented F33 `0x160` field mapping as a demonstrated
actuator interface, so the platform stays stock-longitudinal even when the Alpha
Long toggle is requested. Protected `0x08A` is the already-established TSS request-side
request plane and now also supplies the strongest longitudinal acceleration
candidates; the unresolved problem is clean physical source ownership/suppression
on the stock harness, not a different upstream semantic command. The same correction
now applies to Corolla: its historical `0x160` modify-and-forward result is retained as
field evidence, but the port no longer treats that PDU as authoritative longitudinal
command ingress.

**Radar source lifecycle and the available live fault projection are now
implemented.** The source-driven radar decoder is enabled for Camry, with
separate held-out replay and adversarial tests; vehicle-level fusion/control
qualification is not claimed. Current hardware and cooperative-control inhibits drive the normal
`steerFaultTemporary` interface after exact stock-code assertion/recovery proof.
These lossy current-state projections cannot identify every fault or manufacture
a restart-required `steerFaultPermanent` classification.

The port is still classified **Custom**, not plug-and-play or production-ready.
These boundaries preserve the real steering result without conflating a working
experiment, correct software construction, and a completed vehicle port.
