# 2026 Camry openpilot capability matrix and qualification handoff

**Scope:** current integration/qualification status for the maintainer's exact
2026 Camry Hybrid F33. This matrix tracks the production-shaped openpilot port,
not historical receiver-bypass or recovery experiments.

Evidence grades follow `docs/status/FINDINGS.md`. The architectural standard is
current upstream openpilot/opendbc/Panda: `controlsd` owns engagement,
`CarState` decodes, `CarController` encodes, Panda enforces the ordinary safety
contract, and exact-F33 machinery exists only where the vehicle actually differs.

## Current capability matrix — 2026-09-15

| Capability | Current status | Evidence / implementation | Remaining boundary |
|---|---|---|---|
| Exact platform identification | **reviewable** | exact EPS application F181 `8965F3307000 / 8A3113303100`; GTS resolver; exact firmware table; `match_fw_to_car_exact` test | none for this calibration; transfer to other F33 firmware remains evidence-bound |
| Physical vehicle state | **reviewable** | target-native `0x025` angle/rate, `0x030` driver torque, four wheel speeds, gear, READY, doors/belt, brake/hold/parking brake, BSM, source-real cluster speed | exact temporary/permanent EPS fault-state mapping is still deliberately unmapped |
| Cruise/engagement state | **reviewable** | source-real `0x251` availability/set speed, real `0x08A` cruise latch, exact delayed standstill states `0x66/0x67`; no synthesized authority bit | none for ordinary stock-ACC engagement; long-stop release remains separate |
| Driver interaction | **reviewable** | same-car `0x030`/`0x371` join; 0.6 N·m `steeringPressed` threshold; left/right torque sign fixed; normal openpilot nudge semantics | Toyota's own hysteretic detector is not modeled as a second permission system |
| Lateral command contract | **road-observed** | C7 `0x1FDC0002` -> EPS-resident continuous signer -> native B6; route `0000008d--a9f348691a` plus corroborating `00000093--4066e7ae51`; clean segment r=0.9888 / 0.873° MAE at tested 400 ms lag | road proof used temporary repin/C7 bus0; current stock Toyota-B C7 bus1 mapping still needs parked + short-road revalidation |
| Lateral authentication | **road-observed / production-shaped candidate** | exact continuous helper `b417e12d…159a`; native command-5/selector-4 FV4+CMAC28 generation; native-trailer equality oracle before arming | same-car stock-CodeFlash + volatile-resident combination not yet live-qualified |
| Persistent EPS modification | **not required by intended runtime** | continuous helper signs before the untouched native SecOC consumer; stage-5 receiver bypass is not part of the v16 runtime contract | validate on replacement rack's stock CodeFlash; historical stage-5/persistent artifacts remain provenance only |
| Stock-harness topology | **implemented, vehicle check pending** | ordinary Toyota-B: `0x160` relay pair on Panda bus0/bus2; EPS/Brake + C7 on unsplit bus1; target-scoped short-Classical C7 format handling | parked transport check after rack replacement, then controlled road A/B |
| HUD / lane display | **implemented + replay-tested** | clone live camera `0x412`; normal ~1 Hz heartbeat / <=10 Hz event updates; recovered symmetric lane states; `steerRequired` uses B1[3:2]; later Toyota escalation suppressed only on canonical road frame | field-check stock-harness display; B3 left/right nibble orientation remains unproved, so asymmetric requests preserve stock orientation |
| Cruise cancel | **implemented + safety-tested** | clone live `0x101`, assert source-real brake-cancel bit, preserve dynamic fields, recompute Toyota checksum, bus2; Panda constrains stock shape/checksum | field-check cancel behavior/chime on stock harness |
| Release-default longitudinal | **stock ACC** | ordinary openpilot release shape; no custom planner or engagement state | signer bootstrap historically disabled DRCC for that ignition cycle; same-cycle restoration is the remaining Milestone-A integration question |
| Same-cycle DRCC recovery after signer install | **ready for one bounded vehicle test** | v16 `f33-secoc recover-drcc`: exact EPS identity guard, pre-clear SID19 snapshot, proven six-ECU physical SID14 clear, proven five-responder functional Mode04, post-clear `status&0xAF` sweep, FRC DID1903/1905/1906 oracle | execute after volatile install/load-arm and require FRC cruise permission while signer remains resident |
| Native openpilot longitudinal | **implemented as alpha; physical qualification in progress** | live camera `0x160` template/counter ownership; B4:B5 signed15 0.001 m/s² + Camry inverted signed7 B12; Profile-5 CRC/Data ID `0x444A`; bus0 replacement + bus2 suppression; target safety range -1.5..+1.3 m/s² | prove normal-DRCC physical accel authority, gas/brake handoff, delayed-hold behavior, and PCS/AEB coexistence |
| Stop-and-go metadata | **bounded conservatively** | short 3–4 s native restart observed; >~5 s Toyota hold requires accelerator in retained drive | `autoResumeSng=False` until openpilot can release delayed hold without driver input |
| Radar/perception | **reviewable for current support mode** | `radarUnavailable=True` with model lead path; stock ACC owns longitudinal in release mode | raw TSS3 object/radar parsing is optional improvement, not a blocker for current stock-ACC port |
| Panda safety | **reviewable / unit-tested** | exact F33 C7 angle checks; source-real RX state; HUD/cancel whitelist; dynamic `0x160` replacement; Camry-specific longitudinal bounds; no debug safety mode or controller-side arming | stock-topology on-car transport confirmation |
| Reproducible passive evidence | **accepted** | retained September corpus, generated reports/manifests, firmware/GTS evidence, deterministic verifiers | private original logs needed only to regenerate already-pinned full-corpus products |
| Car-kit deployment | **reviewable v16 candidate** | defaults to the byte-exact road-proven continuous helper; stock bus1 diagnostic/C7 route; historical persistent patch labeled non-runtime; post-install DRCC recovery included | same-cycle field execution on replacement rack |
| Controlled vehicle validation | **in progress** | lateral actuation already observed on two routes; current software now removes recovery-only policy and restores normal HUD/cancel surfaces | stock-harness/stock-CodeFlash revalidation, DRCC recovery result, then alpha-long validation |

## What changed from the September 7 checkpoint

The previous matrix is obsolete in four important ways.

1. **Lateral actuation is no longer blocked on receiver discovery.** The
   September 10 continuous C7/RAM signer configuration physically steered the
   car on two retained routes with clean command TX returns and strong
   desired/measured-angle agreement.
2. **The desired runtime no longer depends on stage-5 receiver bypass.** The
   continuous helper obtains a native-valid B6 SecOC trailer through the EPS
   ICU-S command-5 path before the untouched receiver consumes the frame.
3. **Native longitudinal is no longer an offline hypothesis.** The exact Camry
   `0x160` encoder, camera-counter handoff, relay ownership, and Panda safety
   path are integrated as alpha longitudinal. What remains is physical
   authority/behavior qualification, not message construction.
4. **Normal openpilot lifecycle surfaces are restored.** The current controller
   owns recovered `0x412` HUD and `0x101` cancel behavior, exact EPS identity is
   the fingerprinting anchor, dead-rack diagnostic absence no longer masquerades
   as a vehicle capability, and `autoResumeSng` no longer overclaims long-stop
   restart.

## Software checkpoint

At the September 15 checkpoint, nested opendbc commit
`01b6d188` (`toyota: restore production Camry TSS3 surfaces`) carries the latest
Camry cleanup. Its focused Camry+Corolla TSS3 tests pass **27/27** and the full
Toyota unit set passes **45 tests / 205 subtests**. The generated support table
classifies Camry Hybrid 2026 as **Custom**, which is the correct current product
classification: the control integration is upstream-shaped, but volatile signer
bootstrap is not a normal plug-and-play comma installation.

The analysis car-kit v16 work packages the exact continuous helper from the
successful steering handoff and moves the host loader/diagnostic path to stock
Toyota-B bus1. The road proof itself remains explicitly labeled as the old
repinned/bus0 configuration; implementation equivalence is not substituted for
an on-car stock-topology result.

## Completion-plan work packages

| Deliverable | Status | Current exit condition |
|---|---|---|
| WP1 — reproducible September evidence | **accepted** | retained route/fixture/manifests and deterministic reducers remain the evidence base |
| WP2 — native-shape interface review | **reviewable** | current Camry state/controller/safety code follows normal openpilot ownership; focused and full Toyota tests pass |
| WP3 — lateral control discovery | **closed as discovery; qualification continues** | exact C7 -> resident signer -> native B6 -> physical steering path is road-observed; no additional hidden steering carrier is required |
| WP4 — native longitudinal | **implemented alpha / qualification in progress** | software/wire ownership is integrated; close physical accel authority, handoff, hold-release, PCS/AEB before release-default consideration |
| WP5 — deployment packaging | **reviewable v16** | exact continuous helper is default; stock bus1 route encoded; post-install DTC/DRCC oracle packaged; persistent patch marked historical |
| WP6 — controlled qualification/handoff | **in progress** | execute the remaining stock-topology/DRCC recovery/lateral A/B and then alpha-long test sequence below |

## Remaining on-car qualification sequence

The next vehicle session should not be another open-ended RE session. The
remaining questions are already reduced to direct pass/fail observations:

1. Replacement rack on **stock CodeFlash**, stock Toyota-B harness, Park/NRTD:
   `f33-secoc install`; require exact F181 and resident identity.
2. Direct NRTD -> READY without OFF: `f33-secoc load-arm`; require exact
   continuous helper readback and native Toyota B6 trailer == locally generated
   command-5 trailer.
3. `f33-secoc recover-drcc`; require zero post-clear fault records and FRC DID
   `0x1905` cruise permission with DID `0x1906` ACC-not-available clear. A
   positive result closes the volatile-signer + stock-ACC lifecycle conflict.
4. Return Panda ownership to normal openpilot. Parked, confirm C7 TX on bus1 and
   sequence-zero/no-op behavior; then do a short controlled lateral A/B. Compare
   C7/angle/driver-torque behavior to routes `8d` and `93`.
5. Verify HUD lane/steer-required presentation and normal cruise cancel.
6. Separately enable alpha longitudinal. First verify camera-template handoff
   and source suppression parked, then perform bounded acceleration/deceleration
   tests while logging `0x160`, downstream longitudinal state, gas/brake events,
   PCS/AEB state, and vehicle response.
7. Include one delayed stop >5 s. Only if openpilot can release the Toyota hold
   without driver input should `autoResumeSng` be reconsidered.
8. If any steering fault is intentionally induced/observed during controlled
   validation, retain the exact source state/recovery transition; until then,
   keep openpilot temporary/permanent steering faults unmapped rather than
   inventing a classification from static DTC vocabulary.

## Honest support statement

### Milestone A — openpilot lateral + stock ACC

**Functionally demonstrated, production-topology qualification not quite
closed.** Lateral authority is no longer hypothetical: the exact C7/RAM signer
path steered the maintainer car on retained road routes. The remaining delta is
operational rather than architectural: reproduce that result on stock Toyota-B
bus1 with the replacement rack/stock CodeFlash, and prove that the packaged
same-cycle DTC clear restores stock DRCC without removing the volatile signer.

If that bounded sequence passes, the Camry has essentially the mature openpilot
shape for Milestone A: normal `controlsd` engagement, full-speed target-native
state, target-specific CarController encoding, ordinary Panda safety, stock ACC,
HUD/cancel ownership, and no persistent EPS patch.

### Milestone B — native openpilot longitudinal

**Software/wire integration exists; physical qualification is incomplete.** The
port owns the exact unprotected FRC `0x160` path in normal opendbc/Panda shape,
but retained evidence does not yet justify calling the Camry native-long path a
release capability. Until physical authority, delayed hold, and PCS/AEB
coexistence are closed, longitudinal stays alpha and `autoResumeSng` stays false.

### Product/support class

The current honest class is **Custom**, not ordinary Upstream plug-and-play.
Even with stock CodeFlash, full EPS power loss requires a volatile signer
bootstrap. That deployment limitation is separate from the quality of the
openpilot control integration itself.
