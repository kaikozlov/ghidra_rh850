# 2026 Camry TSS3 integration replay audit and upstream comparison (WP2)

**Scope:** work package 2 of the Camry openpilot completion plan
(REFERENCE/CAMRY_OPENPILOT_COMPLETION_PLAN.md): field-level vehicle-interface
contract, recorded-versus-proposed replay audit, and the explicit list of
unvalidated physical semantics. Everything here is offline software evidence;
no new vehicle claim is made.

| Role | Repository | Revision |
|---|---|---|
| Proposed (current fork) | kai-openpilot / opendbc `kai` / panda `kai` | `45b57159ed004405004f95403dbd9912d26ace90` / opendbc `8c1124fe37f146e2282ba68676ffa82cac4902f8` / panda `5236f3708bfd833942c0e0f79a7fc6d8255fbe60` |
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
| Identification | exact F181 `02‖8965F3307000‖8A3113303100` on `0x7A1`; READY-state CAN census fallback; FRC `8646F3315000` + ABS `F152633K0000` corroborating | `FW_VERSIONS` + `FINGERPRINTS[TOYOTA_CAMRY_TSS3][0] = TSS3_CAN_CENSUS` [FR `test_identity_uses_standard_firmware_and_can_tables`] | Census-based fallback keeps exact Camry identification deterministic without an EPS reply. The provisional Corolla TSS3 census is retained only in `TSS3_CAN_CENSUS`, not FPv1, because it is a strict subset of Camry and has no F181 join; Corolla remains `dashcamOnly`/no-output rather than being ambiguously auto-identified [FR + full fingerprint suite]. |
| Measured state | `0x025` angle+fraction (1.5 deg + 0.1 deg) and signed steering-rate field (1 deg/s), `0x0AA` four wheel speeds → standard `vEgo`, `0x030` torque (0.1 + 0.01 N.m), `0x127` gear P/R/N/D/B, `0x51E B0[7]` READY | [FR `test_carstate_uses_fixed_relay_topology...`, `test_carstate_replays_real_september_2026_0904_eps_frames`; ST: exact-F33 signal189/DID1036 Steering Angle Velocity] real September bytes decode to 4.23 / −2.86 N.m; invalid bit zeroes torque and sets `vehicleSensorsInvalid` | Angle/rate geometry is target-native and wheel-speed parsing keeps ordinary upstream Toyota state handling; torque magnitude is cross-checked vs exact-F33 packer [ST §1.3] and logged corpus [RP `decode_equal`]. **Torque direction/sign vs steering input and the physical driver threshold remain dynamically unconfirmed.** |
| Cruise UI | `0x0FE` momentary MAIN/RES+/SET−/CANCEL active-low bits; `0x08A B3[3]` (**overall CAN bit 27**, not byte 27) cruise-operating latch + B10 internal set speed; `0x251` B2 UI set speed; metric/imperial via `BODY_CONTROL_STATE_2` | [FR `test_carstate_exposes_stock_cruise_button_events`, set-speed assertions] | MAIN/CANCEL→latch timing is same-car dynamically established (VAR-067); set-speed mirrors are state, not writable-command proof |
| Driver interaction | physical torque above 1.2 N.m ⇒ `steeringPressed`; invalid torque ⇒ sensor-invalid; torque feeds DesireHelper nudge semantics | [FR; RP: 1,001 native `0x030` frames from route 3d seg 1 replayed: recorded revision 0 pressed, proposed 171 pressed] | threshold provisional (route-3d no-blinker p90 1.14 vs preLaneChange median 1.30 N.m; VAR-125); **sign convention and final value need on-vehicle confirmation** |
| Lifecycle | controlsd owns engagement/latActive; controller sends ID11 while `CC.latActive`, ID0 otherwise; brake-cancel clones stock `0x101` shape to bus 2; `0x08A` never synthesized | [FR `test_controller_sends_clean_b6...`, `test_controller_inactive_b6_tracks_measured_angle`, `test_controller_brake_cancel_clones_stock_101`; LS TX allow-list `{0x0B6 bus0, 0x101 bus2}`] | No controller-side permission/veto; no arming Params (removed scaffolding confirmed absent from trees) |
| Fault handling | `steerFaultTemporary/Permanent` neutral; `DRIVER_TORQUE_INVALID` → `vehicleSensorsInvalid`; missing-message detection via libsafety RX checks (`0x025/0x0AA/0x116/0x101` bus0, `0x08A` bus2) | [FR; LS `toyota_tss3_rx_checks`] | Fault mapping intentionally neutral until a same-car asserted/recovery transition exists [port report §3.2] — unmapped, not invented |

## Replay audit (recorded `c7a62eaf` vs proposed `8c1124fe`)

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
consequence only; it does not validate the physical Camry torque sign or 1.2 N.m
threshold. The resulting review aids live under
`build/out/camry-replay-audit-20260905/`; `replay_summary.json` records full
revision IDs, fixture provenance, and the DesireHelper result.

| Fixture | `0x030` frames | decode equal | pressed (recorded) | pressed (proposed) |
|---|---:|---|---:|---:|
| 3c seg 43 witness window (reducer qualified-sample max 0.46 N.m; replayed raw samples peak 0.83 N.m, below the 1.2 N.m threshold) | 90 | yes | 0 | 0 |
| 3d seg 1 high-torque window | 1,001 | yes | **0** | **171** |

Decoded steering angle/torque `CarState` is identical between revisions where
the proposed torque measurement is valid; the intentional behavioral delta is
the driver-state contract. Downstream separation:
`DesireHelper` (unchanged upstream code) requires `steeringPressed` plus
directional torque to leave `preLaneChange`; under the recorded revision that
transition is unreachable on every sample (VAR-125), which the September
routes express as zero `laneChange` events against thousands of
`preLaneChange` samples and the repeatable `steerSaturated` alert. The
proposed revision restores the normal upstream path; the physical threshold
itself is provisional (below).

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
4. `cruiseState.available == enabled` derived from the `0x08A B3[3]` cruise
   latch (overall bit 27; observed dynamically by MAIN/CANCEL joins in VAR-067).
   This is the stock-ACC engagement state used by ordinary `pcm_cruise_check`,
   not the `0x08A B21` lateral request ID and not a lateral-authority gate.

Unvalidated physical semantics (no runtime guard should be invented for
these; they stay provisional by code comment and here):

- `0x030` torque **sign/direction** and the final 1.2 N.m threshold
  (`values.py TSS3_STEER_DRIVER_TORQUE_THRESHOLD`).
- EPS fault classification (`0x351`/`0x394` shapes are presence-bounded
  internal inputs only).
- `0x081 B16:B17` propagation direction and command-versus-feedback role
  (VAR-129: reference mirror only).
- B6 receiver admission/ingress semantics — §4.4/§4.5 of the port report
  stand: 751,664 well-formed frames produced no measurable wheel response or
  observable receiver objection; the wire-geometry divergence from the stock
  protected sender (first-in-epoch message-low2 phase) remains the one cheap
  A/B variable for the next stationary run.

Final integration-side verification at opendbc `8c1124fe…`: `./test.sh`
passes ruff, ty, codespell, cpplint, MISRA and all **4,006** unit tests
(**710** skipped by the ordinary suite). The full gate exposed and fixed one
identification regression that focused Camry tests missed: the provisional
Corolla TSS3 census was a strict subset of the exact Camry census and therefore
could not safely remain registered as FPv1 identity. Its observed topology is
retained in `TSS3_CAN_CENSUS`, while only exact Camry is CAN-identifying; the
read-only Corolla platform remains `dashcamOnly`/`noOutput`. `car_diff.py
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
- Corrections with this document as canonical home: [CORR-164](../reference/index.md#correction-corr-164)
<!-- knowledge-cross-references:end -->
