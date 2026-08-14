# Application RoutineControl surface

This note characterizes the 19 configured application `RoutineControl`
(`SID 0x31`) RIDs in `8965B4512000`. The table was previously misclassified as
a WriteDataByIdentifier surface because the application service-object parser
started eight bytes late. Runtime dispatch from `0x25E28` instead binds
`application_routine_control_callback @ 0x95DCE` to SID `0x31`.

Canonical generated table: `data/application_routine_control_surface.csv`.

## 1. Access-control result

All 19 RoutineControl RID records are enabled and all 19 have a configured
SecurityAccess level count of zero.

Eighteen records use policy index 0. That policy permits diagnostic sessions
`1,2,3`, and the corrected outer SID-`0x31` service object also permits
**default, programming, and extended sessions (`1,2,3`)**. RID `0x1010` is the
sole policy-index-1 record and remains extended-session-only (`3`).

This is a Dcm authentication result, not a claim that every routine succeeds
unconditionally. Individual RIDs still contain runtime precondition logic.
RID `0x1010` additionally authenticates its SHE-compatible key-update package
inside ICU-S, independent of the empty Dcm SecurityAccess table.

The practical consequence for policy-0 records is stronger than previously
documented: no `10 03` session transition and no successful `27 xx`
SecurityAccess exchange are required merely to reach their configured
precondition/action machinery from the default diagnostic session.

## 2. Control type and wire shape

The control type checks are recovered from
`application_routine_control_type_supported @ 0x955DC`; exact request-size validation
is recovered from `application_routine_control_input_length_invalid @ 0x95624`.

- every configured RoutineControl supports control type `01`;
- only `0x110A` and `0x110D` support control type `02`;
- only crypto-test activation RIDs `0x100E` and `0x100F` lack control type `03`;
- control-type-1 input data is zero bytes for 17 of 19 RIDs;
- `0x1004` consumes two control-type-1 input bytes;
- `0x1010` consumes 64 control-type-1 input bytes and returns 49 bytes on control types `01`/`03`.

Thus many stateful control requests have only the control type/RID header on the
wire after SID, for example the already-proven bank-1 activation request
`31 01 10 0F`.

## 3. Callback table

The 19x12-byte table at CodeFlash `0x25804` binds each RID to a precondition and
action callback. Its SHA-256 is
`bb72da6fb416c6fc47cb87cf2c060bb99f6bdb95499254bfbbfe960f1ccc979c`.
Both callback columns are seeded as dispatch-proven function tables so these
edges survive clean Ghidra rebuilds.

Important recovered effects include:

| RID | Action | Bounded interpretation |
|---|---:|---|
| `1000` | `0x4F060` | builds 32-byte supported-`0x10xx` RoutineControl bitmap |
| `1004` | `0x4F170` | fixed maintenance trigger: control type 1 requires input `FF FF`, then queues internal operation 5 without consuming a tester-chosen value |
| `1007` | `0x4F1EA` | one-shot live lifecycle reinitialization of groups `FEBEB454/455`; no local speed/mode gate |
| `1008` | `0x4F25C` | one-shot diagnostic-only live lifecycle reinitialization of group `FEBEB456`; no local speed/mode gate |
| `1009` | `0x4F2C2` | state-gated live lifecycle reinitialization: fixed-enabled feature byte, aggregate-health-zero admission, forces `FEBEB2D5=0x11` |
| `100E` | `0x8A774` | calls crypto-test bank-0 activator `0x68F92` |
| `100F` | `0x8A782` | calls crypto-test bank-1 activator `0x69018` |
| `1010` | dedicated path | ICU-S command-8 authenticated key update |
| `1100` | `0x4F32E` | builds 32-byte supported-`0x11xx` RoutineControl bitmap |
| `110A` | `0x4F630` | service-mode control, internal mode 2; control type 2 termination |
| `110C` | `0x4F702` | service-mode control, internal mode 3 |
| `110D` | `0x4F7B8` | service-mode control, internal mode 4; control type 2 termination |

Several other callbacks are demonstrably stateful but their OEM test names are
not assigned. The generated CSV records their recovered callees and leaves the
semantics bounded rather than inventing names from behavior alone.

## 4. `0x1007/0x1008` ungated live lifecycle reinitialization

RIDs `0x1007` and `0x1008` expose a distinct availability/control-state surface
that is weaker-gated than several neighboring RoutineControl RIDs.

Both are policy-0, control-type-1, zero-payload requests. Their preconditions call
shared lifecycle-readiness helper `FUN_B79F8` and then check a dedicated
one-shot flag (`FEBE8157` or `FEBE8158`). Neither precondition reads
`application_vehicle_speed_raw @ FEBEE892`, alternate-handoff state, or system
mode. This is not merely because speed is enforced at a common RoutineControl layer:
`0x1002` and `0x1106` explicitly read `FEBEE892` and compare it against the same
calibration threshold in their own precondition callbacks.

The corrected outer service object is itself available in sessions `1,2,3`,
so no session transition restores a stationary condition before these routines
are reachable. The statically recovered requests from the default session are
therefore simply:

- `31 01 10 07` — start RoutineControl RID `0x1007`; or
- `31 01 10 08` — start RoutineControl RID `0x1008`.

`0x1007` reaches `FUN_B7A36(0)`. That helper forces lifecycle groups
`FEBEB454/455` to transition state `0x11` and calls dedicated reinitialization
helpers for subordinate components. `FUN_B7A36` is also used by one internal
fault/lifecycle-recovery path, so the bounded interpretation is that the RoutineControl
exposes a live recovery/reinitialization operation rather than a unique actuator
primitive.

`0x1008` reaches `FUN_B7AAE`. That helper forces `FEBEB456` to state `0x11` and
calls five subordinate reinitializers. Its only recovered caller is the
RoutineControl-owned thunk at `0xFDEA8`, making this particular group reset
diagnostic-only in the recovered static graph.

The resulting lifecycle workers (`B7794/B7872/B792A`) are not confined to a
diagnostic task. Wrapper `B79E8` is called from `system_mode_per_tick_dispatcher`
whenever current mode is greater than `0x102`; this includes the normal
operational `0x300/0x400/0x500` mode families. State `0x11` is an in-progress
transition: the workers wait for subordinate states to converge to `0x22`, or
resolve to error state `0x44` on failure/timeout.

The requests are **one-shot per application boot**, not an unlimited diagnostic
DoS loop. `0x1007` writes `FEBE8157=1` and `0x1008` writes `FEBE8158=1`; exact
xref censuses recover no other writer that clears either byte during runtime.
Subsequent control-type-1 attempts therefore fail their busy check until reset.

This supports a bounded finding: an unauthenticated diagnostic client can,
subject to lifecycle-readiness conditions but without a local or outer
stationary gate, inject one live subsystem reinitialization into the operational
scheduler. Static evidence does **not** show these lifecycle states joining the
proved d/q current/PWM producer cone, so this is an availability/control-state
primitive rather than arbitrary steering actuation.

### `0x1009`: state-gated live lifecycle reinitialization

RID `0x1009` extends the same lifecycle-reinitialization class but with a
stronger runtime admission condition than `0x1007/0x1008`. It is still a
policy-0, zero-payload control-type-1 action reachable from the unauthenticated default
session, and its precondition contains no explicit vehicle-speed or system-mode
read. In this calibration its feature byte at CodeFlash `0xAEC5D` is fixed to
`0x20`, so the feature gate is enabled.

The action reads `FEBEE958`, a snapshot of aggregate state `FEBEB220`, and only
calls the diagnostic thunk `0xFE0B0 -> B55E2` when that snapshot is zero.
`B55E2` invokes two recovery helpers and forces lifecycle state `FEBEB2D5` to
`0x11`. Worker `B5254` is serviced through wrapper `B5526`, which is called by
`system_mode_per_tick_dispatcher` in the same `mode > 0x102` operational
scheduler region as the other lifecycle workers.

The repeatability boundary differs from `0x1007/0x1008`. Control type 1 writes
latch `FEBE8159=1`, but control type 3 can clear that latch if the feature becomes
disabled or the aggregate-health snapshot becomes nonzero. Static evidence
therefore supports a **state-dependent**, not strictly one-shot-per-boot,
reinitialization primitive. It remains bounded by the aggregate-health-zero
condition and, like the other lifecycle paths, has no recovered static join into
the d/q/PWM producer cone.

## 5. `0x110A/0x110C/0x110D` service-mode chain

These three RoutineControl RIDs are the strongest state-changing entries recovered in this
pass.

Control type `01` loads internal mode `2`, `3`, or `4` respectively and reaches the
shared service-mode dispatcher `FUN_B1F34` through thunk `0xFE038`.
`FUN_B1F34` records the corresponding activity bit and can post system-mode
event `6`. In the `0x500` system-mode family, the coordinator converts those
activity bits to event `0x2E`; `FUN_B1DAC` then initializes the selected service
subtype and commits **system submode `0x520`**.

The `0x520` initializer `FUN_B7054` creates a dedicated service-state island,
latches subtype `1/2/3`, and clears paired subsystem command slots 0 and 1 by
calling fixed-slot writer `FUN_562C8` through thunk `0xFED2C`.

`0x110A` and `0x110D` expose control type `02` termination. Their stop callbacks set
the service state to terminal value `3`; the `0x520` coordinator emits event
`0x2F`, performs cleanup, and returns to parent mode `0x500`. `0x110C` has no
control-type-2 entry and instead relies on its internal state progression.

The service callbacks contain additional runtime preconditions. This report
therefore does **not** claim that an arbitrary request succeeds at arbitrary
vehicle speed/state; it establishes the authentication/session boundary and the
reachable control-state graph when those preconditions are satisfied.

## 6. Motor-actuation boundary

The `0x520` service pipeline computes signed/saturated values, so those values
were traced separately from the authentication analysis rather than being
assumed to be steering commands.

Exact Ghidra reference censuses are now pinned for representative service-state
outputs/snapshots:

- `FEBEB3E0`
- `FEBEB448`
- `FEBEB44C`
- `FEBEB452`
- `FEBEB000`
- `FEBEB002`
- `FEBEB004`
- `FEBEB006`

Their references remain inside service-mode producers/consumers,
initialization, and snapshot/telemetry functions. None joins the independently
proved d/q current-reference state at `FEBE6D28/FEBE6D2A` or the known PWM
producer cone.

Therefore the current static evidence supports **diagnostic service-mode and
control-state exposure with bounded availability implications**, not arbitrary
steering torque/current actuation. Hardware-only effects and indirect physical
behavior of the service routines remain dynamic questions.

## 7. Security interpretation

The significant issue is broader than the previously recovered crypto-test
activation: a calibration with a fully implemented SecurityAccess mechanism has
left the entire 19-entry RoutineControl set at SecurityAccess level count zero, including
state-changing factory/service controls.

The strongest recovered consequences are related availability/control-state
paths: `0x1007/0x1008` can inject one-shot live lifecycle reinitialization into
normal operational scheduling without the explicit speed gate used by other
RoutineControl RIDs; `0x1009` exposes a state-gated variant that forces `FEBEB2D5=0x11` when
aggregate health is zero; and `0x110A/0x110C/0x110D` can request special EPS
service modes under their own runtime gates. These are authentication/safety-policy weaknesses, not
evidence of a clean steering-control primitive.

For comma/openpilot work these RoutineControl RIDs should not be treated as a production
control interface. Their semantics are factory/service-oriented, their runtime
conditions are heterogeneous, and the proven motor-current path remains
separate.

## 8. Verification

- `tests/verify_application_routine_control_surface.py` pins the 19-entry policy, control type,
  descriptor-width, callback, corrected outer SID-0x31 session gate, contrasting
  per-RID speed gates, live lifecycle-reinit bodies, one-shot writes, scheduler
  gate, service-mode chain, and termination structure directly from firmware
  bytes.
- `ghidra/scripts/verify/AssertMotorActuationBoundary.java` pins the exact
  service-state reference censuses alongside the independent d/q-current
  reference censuses.
- `tools/generate_application_routine_control_surface.py` deterministically regenerates
  `data/application_routine_control_surface.csv` from the committed CodeFlash image.
