# 2026 Camry TSS3 integration replay audit and upstream comparison (WP2)

**Scope:** work package 2 of the Camry openpilot completion plan
(REFERENCE/CAMRY_OPENPILOT_COMPLETION_PLAN.md): field-level vehicle-interface
contract, recorded-versus-proposed replay audit, and the explicit list of
unvalidated physical semantics. Everything here is offline software evidence;
no new vehicle claim is made.

| Role | Repository | Revision |
|---|---|---|
| Proposed (current fork) | kai-openpilot / opendbc `kai` / panda `kai` | `63e525b2f9500cc10bd9e7c9116010842f633f87` / opendbc `ca52a67fccb63317068b35d1b18c0af028122e0b` / panda `5236f3708bfd833942c0e0f79a7fc6d8255fbe60` |
| Upstream openpilot (design reference) | commaai/openpilot | `a4f7c50d2a52a5865a40da2ebc5004c82929a0ef` |
| Upstream opendbc (design reference) | commaai/opendbc | `3e92d112129507debe45364891954db70238997a` |
| Recorded (produced the 2026-09-04 routes) | kai-openpilot / opendbc `kai` | parent `d1914bbe7`… / opendbc `c7a62eaf` |

All three fork trees were clean at the final audit point. Upstream has **no** Toyota TSS3
platform, no `0x025/0x030/0x08A/0x0B6` Toyota CAN-FD messages, and no
angle-command `0x0B6` safety path, so the comparison baseline is upstream's
ordinary Toyota port *shape* (torque platforms), not a line-for-line
equivalent. The current upstream `openpilot/selfdrive` and `openpilot/cereal`
trees have no changes at all relative to the earlier `0ec3a082...` audit pin,
so the controlsd/DesireHelper conclusions below are unchanged after repinning
to `a4f7c50d...`. Reviewable diffs (regenerated 2026-09-05):
`build/out/camry-replay-audit-20260905/upstream-opendbc-toyota.diff`
(1,954 lines at the final pin: values/fingerprints/interface/carstate/carcontroller/tss3.py,
toyota_tss3_pt DBC, Toyota safety gates, tests) and
`upstream-openpilot-root.diff` (52 lines: the only current upstream-source deltas
outside the opendbc submodule, in `card.py` and offroad-alert metadata). The
standard upstream `SecOCKey` parameter path remains upstream code and is not a
Camry arming mechanism; this Camry advertises `secOcRequired=False`.

## Field-level contract table

Evidence keys: [FR] = real-frame replay test in
`opendbc/car/toyota/tests/test_tss3_camry.py`; [LS] = libsafety
`opendbc/safety/modes/toyota.h` + `safety/tests/test_toyota.py`; [EV] =
dynamic same-car evidence (live-baseline report); [ST] = firmware-static
(port report §1); [RP] = this replay audit.

| Area | Replay case | Behavior / evidence | Completion evidence boundary |
|---|---|---|---|
| Identification | exact F181 `02‖8965F3307000‖8A3113303100` on `0x7A1`; READY-state CAN census fallback; FRC `8646F3315000` + ABS `F152633K0000` corroborating | `FW_VERSIONS` + exact Camry and provisional Corolla entries in `FINGERPRINTS` [FR `test_identity_uses_standard_firmware_and_can_tables`; Corolla `test_provisional_census_does_not_identify_as_camry`, `test_camry_identifies_after_shared_startup_traffic`] | Corolla's observed census is a strict subset of Camry and has no F181 join, so it is deliberately retained as a **competing ambiguity guard**, not a uniquely identifying platform: subset-only traffic returns no candidate; Camry-only IDs eliminate Corolla and identify exact Camry. Explicit Corolla remains `dashcamOnly`/no-output (CORR-170). |
| Measured state | `0x025` angle+fraction (1.5 deg + 0.1 deg) and signed steering-rate field (1 deg/s), `0x0AA` four wheel speeds → standard `vEgo`, retained `0x610.UI_SPEED` → `vEgoCluster`, `0x030` torque (0.1 + 0.01 N.m), `0x127` gear P/R/N/D/B, `0x51E B0[7]` READY | [FR `test_carstate_uses_fixed_relay_topology...`, `test_carstate_uses_source_real_cluster_speed`, `test_carstate_replays_real_september_2026_0904_eps_frames`; ST: exact-F33 signal189/DID1036 Steering Angle Velocity] real September bytes decode to 4.23 / −2.86 N.m; invalid bit zeroes torque and sets `vehicleSensorsInvalid` | Angle/rate geometry is target-native and wheel-speed parsing keeps ordinary upstream Toyota state handling. Route 2c independently preserves the legacy physical cluster-speed carrier, so exact Camry uses `0x610.UI_SPEED` rather than a guessed 1.5% Toyota fudge while `CarInterfaceBase` retains its normal 0.5-km/h hysteresis (VAR-109). Torque magnitude is cross-checked vs exact-F33 packer [ST §1.3] and logged corpus [RP `decode_equal`]; post-fix same-car lane-change starts validate left-positive/right-negative torque semantics (VAR-139). |
| Parser liveness | all 18 checked Camry TSS3 sources on their established native sides; source-real cadence/gap census across routes 3d/3e/3f | [EV VAR-141; FR per-source disappearance/recovery] every configured Hz is a conservative nominal floor and every worst same-segment gap remains inside the normal ten-period CANParser timeout | The earlier synthetic helper was mislabeled as capture replay and `0x127` was mislabeled 60 Hz; it is ~51 Hz in all three long routes and is now configured/tested at 50 Hz. `0x610` remains variable but worst observed gap is ~1.006 s vs 3.333-s timeout; `0x412` worst is ~1.759 s vs 10-s timeout. |
| Cruise UI | `0x0FE` momentary MAIN/RES+/SET−/CANCEL active-low bits; `0x251 B1[4]` persistent cruise-main/availability; `0x08A B3[3]` (**overall CAN bit 27**, not byte 27) cruise-operating latch + B10 internal set speed + B7 `0x66/0x67` delayed ACC standstill/hold state; `0x251` B2 UI set speed; metric/imperial via `BODY_CONTROL_STATE_2` | [FR `test_carstate_exposes_stock_cruise_button_events`, availability/set-speed/standstill assertions] | `available` vs `enabled` is independently closed by VAR-137. VAR-140 adds `cruiseState.standstill`: 198 source-real hold frames across three episodes are exact-zero, enter >5 s after stopping, and clear on accelerator before motion; moving B7=`0x65` proves this is an exact byte-state mapping rather than a bit5 shortcut. Set-speed mirrors remain state, not writable-command proof. |
| Driver interaction | `abs(physical torque) >= 0.6 N.m` ⇒ `steeringPressed`; invalid torque ⇒ sensor-invalid; torque feeds DesireHelper nudge semantics | [FR; RP: 1,001 native `0x030` frames from route 3d seg 1 replayed: recorded revision 0 pressed, current 797 pressed] | Same-car routes 3e/3f join exact-F33 torque to Toyota's native `0x371 B20[4]` driver-steering state: median detector assertion 0.67 N.m on both drives; 0.6 N.m yields ~94–95% specificity and ~75–77% sensitivity to the slower hysteretic Toyota state. The policy is an upstream-style single threshold, not a claim that Toyota itself uses one static comparator (VAR-139). |
| Lifecycle / HUD | controlsd owns engagement/latActive; controller sends ID11 while `CC.latActive`, ID0 otherwise; brake-cancel clones stock `0x101` shape to bus 2; `0x08A` never synthesized; camera-owned `0x412` is replaced at its native ~1 Hz heartbeat with <=10 Hz event updates, recovered lane visibility, and openpilot `steerRequired` on the recovered B1[3:2] steering-warning visual; Toyota's later B2[6] escalation remains suppressed | [FR `test_controller_sends_clean_b6...`, `test_controller_inactive_b6_tracks_measured_angle`, `test_controller_brake_cancel_clones_stock_101`, `test_controller_renders_tss3_lane_visibility_on_stock_hud`, HUD heartbeat/alert test; LS TX allow-list/replacement rules] | No controller-side permission/veto; no arming Params. HUD rendering uses only observed states 1/2/4; lane-departure and audible/chime semantics remain deliberately unmapped (VAR-138) |
| Fault handling | exact-F33 `0x030 DRIVER_TORQUE_INVALID` → `vehicleSensorsInvalid`; `STEERING_FAULT_INHIBIT_STATUS` remains decoded but policy-neutral; missing-message detection uses normal parser/libsafety liveness on the established periodic state set | [FR `test_carstate_driver_intervention_and_sensor_validity`, liveness tests; LS `toyota_tss3_rx_checks`] | `steerFaultTemporary`/`steerFaultPermanent` remain neutral: neither the selected `0x030` aggregate nor `0x351/0x394` has a same-car asserted/recovery classification |

## Replay audit (recorded `c7a62eaf` vs proposed `ca52a67f`)

Method: identical native-CAN fixture input (tracked
`tests/fixtures/camry_20260904/3c-seg43.jsonl` witness window and tracked
`tests/fixtures/camry_20260904/3d-seg1-torque.jsonl`, source SHA-256
`1437f8c6...e54ddc3`, 4.0–14.0 s) replayed through `CarInterface.update()`
from both opendbc revisions. `tools/replay_camry_tss3_carstate_revisions.py`
materializes the recorded revision in a temporary clean git worktree and refuses
a caller-pinned proposed-revision mismatch. It also executes the current fork's
actual `DesireHelper` implementation as a downstream semantic check: with an
otherwise identical left-lane-change input, `steeringPressed=False` remains in
`preLaneChange`, while `steeringPressed=True` plus positive steering torque enters
`laneChangeStarting` and produces `laneChangeLeft`. This verifies the software
consequence only; independent same-car route evidence now validates the torque
sign and selects the 0.6 N.m policy threshold (VAR-139). The resulting review aids live under
`build/out/camry-replay-audit-20260905/`; `replay_summary.json` records full
revision IDs, fixture provenance, and the DesireHelper result.

| Fixture | `0x030` frames | decode equal | pressed (recorded) | pressed (proposed) |
|---|---:|---|---:|---:|
| 3c seg 43 witness window | 90 | yes | 0 | **6** |
| 3d seg 1 high-torque window | 1,001 | yes | **0** | **797** |

Decoded steering angle/torque `CarState` is identical between revisions where
the proposed torque measurement is valid; the intentional behavioral delta is
the driver-state contract. Downstream separation:
`DesireHelper` (unchanged upstream code) requires `steeringPressed` plus
directional torque to leave `preLaneChange`; under the recorded revision that
transition is unreachable on every sample (VAR-125), which the September
routes express as zero `laneChange` events against thousands of
`preLaneChange` samples and the repeatable `steerSaturated` alert. The
proposed revision restores the normal upstream path. VAR-139 then validates the
sign on 45/45 post-fix lane-change starts and replaces the original 1.2 N.m
bring-up heuristic with the cross-route 0.6 N.m policy.

Established software defects fixed and regression-pinned:

- **VAR-125** hardcoded `steeringPressed=False` — fixed by opendbc `e37bab6c`;
  pinned against real September wire bytes by
  `test_carstate_replays_real_september_2026_0904_eps_frames` (fails on the
  recorded revision, passes on the proposal).
- **Invalid-torque propagation** — opendbc `a13c9ee9` zeroes `steeringTorque`
  and raises `vehicleSensorsInvalid` on `DRIVER_TORQUE_INVALID`; pinned in the
  same test.

## Deviations kept, and unvalidated physical semantics

Bounded, deliberate deviations from upstream shape (all reviewable in the
upstream diff):

1. `TOYOTA_CAMRY_TSS3` platform files (no upstream equivalent exists).
2. `secOcRequired=False` with zero-MAC28 B6: emission depends on the
   maintainer EPS's Gate-2 development patch; even with the patch, receiver
   admission is unproven (see B6 receiver semantics below). The upstream-shaped
   `build_b6_secoc_frame` exists but is unused until a real key path exists.
3. Corolla TSS3 read-only platform hardcodes `gearShifter=drive` and
   `pt_bus=1` (dashcam-only; bounded by `test_tss3_corolla.py` no-output case).
4. `0x251 B1[4]` is used as the persistent cruise-main/availability state while
   `0x08A B3[3]` remains actual cruise operation. Two same-car routes establish
   MAIN activation and CANCEL persistence (VAR-137), but no retained true MAIN-off
   edge or OEM CAN-bit name exists; the mapping is therefore wire-behavior-backed
   without pretending a stronger diagnostic join.

Unvalidated physical semantics (no runtime guard should be invented for
these; they stay provisional by code comment and here):

- EPS temporary/permanent classification remains unresolved across `0x030`, `0x351`,
  and `0x394`. `0x030 STEERING_FAULT_INHIBIT_STATUS` is a target-native selected
  fault/inhibit aggregate, but no retained asserted/recovery episode classifies it for
  openpilot policy.
- `cruiseState.nonAdaptive`, `accFaulted`, `carFaultedNonCritical`, `stockAeb`,
  and `stockFcw` intentionally remain at ordinary false/default values. Current
  FRC diagnostics expose semantically relevant names (`0x1903 Control Mode`,
  `0x1905 Cruise Control Permission Flag`, PCS invalid/availability fields and
  fail-safe factors), but no retained same-car road capture joins an asserted
  state to a normal runtime CAN field. Upstream Toyota maps these outputs only
  from explicit PCM/PCS state carriers, so transferring a nearby TSS3 byte or
  treating a diagnostic permission flag as a fault would invent policy.
- `steeringTorqueEps` remains zero on exact Camry because the TSS3 controller is
  angle-controlled and does not use motor torque for command limiting; no
  target-native motor-torque state is required by the current control path.
- `0x081 B16:B17` propagation direction and command-versus-feedback role
  (VAR-129: reference mirror only).
- B6 receiver admission/ingress semantics — §4.4/§4.5 of the port report
  stand: 751,664 well-formed frames produced no measurable wheel response or
  observable receiver objection; the wire-geometry divergence from the stock
  protected sender (first-in-epoch message-low2 phase) remains the one cheap
  A/B variable for the next stationary run.

Final integration-side verification at opendbc `ca52a67f…`: `./test.sh`
passes ruff, ty, codespell, cpplint, MISRA and all **4,011** unit tests
(**710** skipped by the ordinary suite). The full gate exposed and fixed one
identification regression that focused Camry tests missed: the provisional
Corolla TSS3 census is a strict subset of the exact Camry census and therefore
cannot uniquely identify Corolla. Current `f754d14c`/CORR-170 deliberately keeps
that subset as a competing FPv1 candidate so shared startup traffic remains
ambiguous instead of falsely identifying Camry; Camry-only IDs then eliminate it.
The read-only Corolla platform remains `dashcamOnly`/`noOutput`. `car_diff.py
--platform TOYOTA_CAMRY_TSS3` exits cleanly but has zero fetchable comma route
segments for this new platform, so the tracked same-car replay above is the
behavioral comparison surface rather than pretending that an empty car-diff is
validation.

**Exit status:** reviewable upstream diff produced; replay report complete
with the behavioral change explained; regression tests added; unvalidated
semantics listed. No custom arming Params, alternate engagement state
machine, or global Toyota change was introduced.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: —
- Corrections with this document as canonical home: [CORR-164](../reference/index.md#correction-corr-164), [CORR-170](../reference/index.md#correction-corr-170)
<!-- knowledge-cross-references:end -->
