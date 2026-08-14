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
| `1001` | `0x4F00A` | 32-byte support/capability bitmap query; no application state machine |
| `1002` | `0x4F0EA` | vehicle-speed-gated lifecycle normalization/reinitialization via request `FEBEAF47=0x44` |
| `1004` | `0x4F170` | **no-speed-gate persistent event-log/history maintenance rewrite**: fixed `FF FF` starts queue operation 5 and rewrites objects 17/18/19/20/21/23 |
| `1007` | `0x4F1EA` | one-shot live lifecycle reinitialization of groups `FEBEB454/455`; no local speed/mode gate |
| `1008` | `0x4F25C` | one-shot diagnostic-only live lifecycle reinitialization of group `FEBEB456`; no local speed/mode gate |
| `1009` | `0x4F2C2` | state-gated live lifecycle reinitialization: fixed-enabled feature byte, aggregate-health-zero admission, forces `FEBEB2D5=0x11` |
| `100E` | `0x8A774` | calls crypto-test bank-0 activator `0x68F92` |
| `100F` | `0x8A782` | calls crypto-test bank-1 activator `0x69018` |
| `1010` | dedicated path | ICU-S command-8 authenticated key update |
| `1100` | `0x4F32E` | builds 32-byte supported-`0x11xx` RoutineControl bitmap |
| `1103` | `0x4F3C0` | runtime-gated internal mode-1 service request |
| `1106` | `0x4F43E` | vehicle-speed-gated three-group lifecycle reinitialization |
| `1108` | `0x4F4BC` | **no-speed-gate persistent checkpoint reset** through queue operation 2 |
| `1109` | `0x4F570` | vehicle-speed/state-gated redundant namespace-`0x100` object-0 update |
| `110A` | `0x4F630` | service-mode control, internal mode 2; control type 2 termination |
| `110C` | `0x4F702` | service-mode control, internal mode 3 |
| `110D` | `0x4F7B8` | service-mode control, internal mode 4; control type 2 termination |

The remaining policy-0 callback semantics are now bounded as well. The evidence
names above describe recovered behavior rather than inferred Toyota factory-test
labels; no OEM display names are assigned where the firmware does not retain them.

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

## 5. Remaining query/lifecycle/persistence controls

### `0x1004`: repeatable event-log/history persistent rewrite

RID `0x1004` is another policy-0 persistent maintenance surface whose gating is
weaker than its generic label previously suggested. Control type 1 requires the
fixed two-byte payload `FF FF`; the action never consumes a tester-selected
numeric value. Its precondition reads only alternate-handoff state and selector-3
busy byte `FEBE8156`. It has **no recovered vehicle-speed reference**, and policy
0 plus the outer SID-`0x31` object permit sessions `1/2/3`. The default-session
start request is therefore **`31 01 10 04 FF FF`**.

Type 1 calls `0x50864`, the queue-operation-5 starter. If idle it records state
`5`, invokes `0x50858 -> 0x5449E`, then sets the active bit (`0x85`). Operation
5 and operation 6 are intentionally coalesced: `0x50864` suppresses duplicate
5/6 requests while that family is active or queued, and operation-6 completion
helper `0x4C474` updates selector 3 whenever `FEBE8156` is pending.

The dedicated initializer `0x5449E` brackets setup with event-state
`FEBE897C = 0xAA -> 0xA5`, invokes bank initializer `0x5436E`, and initializes
history groups `0`, `3`, and `2` through `0x54416`. Those initializers set dirty
bit 2 in both alternating event-log bank flags (`FEBE8988/8989`) and in history
flags `FEBE898A[0/3/2]`. The normal worker wrapper `0x54140` runs status worker
`0x53DAC` followed by `checkpoint_event_log_banks_persist @ 0x53FC4`. The dirty
bits necessarily satisfy `0x53FC4`'s persistence gate and force the following
checkpoint rewrite set:

| Object | Bounded checkpoint meaning |
|---:|---|
| `17` | event-log control state |
| `18` | event-log snapshot bank A |
| `19` | event-log snapshot bank B |
| `20` | event-history group 0 |
| `21` | event-history group 1 |
| `23` | event-history group 2 |

Object `17` is submitted directly; bank mapper `0x53EF2` returns the complementary
`18/19` pair, so both dirty bank flags rewrite both banks; history mapper
`0x53B70` maps initialized groups `0/3/2` to `20/21/23`. Object `22` is disabled
in this calibration and is not part of the workflow.

RoutineControl completion waits on the persistent workflow. On the first tick,
`FEBE897C=0xA5` remains nonterminal while `0x53FC4` submits NVM updates and marks
per-object status bytes pending. Later `0x53DAC` polls those statuses and changes
`FEBE897C` only to `0` (success) or `0x55` (failure) after pending states clear.
Queue monitor `0x50A1C` recognizes active state `0x85`, reports selector `3` with
result `0` or `0x20`, and advances the queue. Generic selector helper `0x4F864`
turns those into terminal RoutineControl states `2/3`. Since the start
precondition rejects only state `1`, **RID `1004` is repeatable after completion**,
not one-shot.

The firmware proves a persistent event-log/history rewrite but does not retain an
OEM service name that would justify calling this “ClearDTC.” Exact static/live
graph audits across the recovered op5/event-history cone find no direct reference
to conditioned steering-command or d/q-current/PWM state. The bounded consequence
is repeatable persistent diagnostic/history integrity and maintenance-state
perturbation, not arbitrary steering-current injection. A routine bench probe is
intentionally omitted because the request deliberately rewrites persistent event
history.

The formerly generic `1001/1002/1103/1106/1108/1109` rows are now closed through
their application workers and completion states.

- **`0x1001` is a query, not a state-changing routine.** Control type 1 passes a
  fixed `0x20`-byte output to `0x4C5AE`, which clears the buffer and builds a
  support bitmap from the configured RoutineControl records, then marks its
  status complete.
- **`0x1002` is a speed-gated lifecycle reinitializer.** Its precondition reads
  `application_vehicle_speed_raw @ FEBEE892`, alternate-handoff state, and its
  busy byte. Type 1 calls `0x35582`, requests `FEBEAF47=0x44`, and marks selector
  2 pending. The normal `B7E6E` worker handles request `0x44` without changing
  the object-7 mode latch; it normalizes companion state `FEBEAF46=0x5A` and can
  invoke `B79F8(1) -> B7A36(1)` to reinitialize the associated lifecycle group
  before reporting completion.
- **`0x1103` is a gated internal mode-1 service request.** Eligibility helper
  `0x354E6` includes vehicle-speed and state/health conditions. Type 1 sets
  `FEBE6ABA=0x11`; per-tick worker `0x352A0` later calls the same `B1F34` mode
  arbiter used by `110A/110C/110D`, but with selector `1`, and selector 8 carries
  the diagnostic completion state.
- **`0x1106` is a speed-gated three-group reinitializer.** When its additional
  `FEBEE958==0` condition is satisfied, `B3974` starts lifecycle states
  `FEBEB25A/FEBEB325` and companion marker `FEBEB48D`. `B38C0` reports selector
  9 success only after all three reach `0x44`; intermediate states remain
  pending and failures report `0x20`.
- **`0x1109` is a speed/state-gated persistent update.** Type 1 calls
  `B7D26(0x22,1)`. When the underlying state requires persistence, helper
  `0x3547E` submits redundant namespace-`0x100` object 0 and the RoutineControl
  status becomes pending; `B7CC6/B7C4A` later resolves selector 11 success or
  failure. This report deliberately does not invent a stronger object name.

### `0x1108`: repeatable no-speed-gate persistent checkpoint reset

RID `0x1108` is materially weaker-gated than the neighboring persistent/reset
controls. It is policy 0, zero-payload, and therefore reachable from the default
diagnostic session as the four-byte request **`31 01 11 08`**. Its precondition
reads the alternate-handoff flag and selector-10 busy byte `FEBE815D`, but has
**no reference to `FEBEE892` or another recovered vehicle-speed quantity**.
No outer session transition restores a stationary check because SID `0x31` and
policy 0 already allow sessions `1/2/3`.

Type 1 calls `0x50760`. If the shared queue is idle, that function records
operation `2`, immediately invokes initializer `0x5070C`, and sets the active
bit, yielding queue state `0x82`. Otherwise it queues operation 2 unless an
operation 2 or operation 6 is already active/pending. The initializer resets or
reinitializes the shared checkpoint/runtime families and the recovered persistence
join includes objects **9, 11, 12, 14, and 15**:

| Object | Bounded checkpoint meaning |
|---:|---|
| `9` | runtime-condition snapshot |
| `11` | two-channel u16 state |
| `12` | dual-incident snapshot |
| `14` | three-entry condition history |
| `15` | operating-state snapshot |

`0x50A1C` monitors the active queue operation. Once its four status groups leave
pending/error transitional values, the operation-2 branch reports selector
`10` with result `0` or `0x20` through `0x4C430`; selector 10 is exactly
`FEBE815D`, so RoutineControl requestResults observes success/failure. This path
is **repeatable after completion**, unlike the one-shot-per-boot `1007/1008`
controls: the start precondition rejects only `FEBE815D==1`, while terminal
selector states are `2/3`.

Operation 6 is intentionally coalesced into the same completion family.
`0x50760` suppresses a duplicate operation-2 insertion while 6 is active or
queued; operation-6 monitor `0x50A1C` calls `0x4C474`, which updates selector 10
whenever `FEBE815D` is pending. Thus a `1108` request concurrent with operation
6 does not depend on a narrow race or remain permanently pending.

This is a stronger availability/persistence exposure than the previously
documented one-shot lifecycle routines: an unauthenticated default-session
tester can repeatedly request a workflow that deliberately clears/reinitializes
runtime state and persists multiple checkpoint objects, without a recovered
vehicle-speed gate. Exact raw/live graph audits still find **no direct reference
to the conditioned steering-command state or the d/q-current/PWM producer cone**.
The supported interpretation is therefore persistent maintenance/reset and
availability-state perturbation, not arbitrary steering-current injection. A
normal bench probe is intentionally omitted because the routine modifies
persistent state; dynamic characterization requires a disposable/matching ECU
with NVM backup/restore and recovery planning.

## 6. `0x110A/0x110C/0x110D` service-mode chain

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

## 7. Motor-actuation boundary

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

## 8. Security interpretation

The significant issue is broader than the previously recovered crypto-test
activation: a calibration with a fully implemented SecurityAccess mechanism has
left the entire 19-entry RoutineControl set at SecurityAccess level count zero, including
state-changing factory/service controls.

The strongest recovered consequences are related availability/control-state
paths: `0x1007/0x1008` can inject one-shot live lifecycle reinitialization into
normal operational scheduling without the explicit speed gate used by other
RoutineControl RIDs; `0x1009` exposes a state-gated variant that forces
`FEBEB2D5=0x11` when aggregate health is zero; **`0x1108` is a repeatable,
default-session, no-speed-gate trigger for persistent checkpoint reset operation
2**; and `0x110A/0x110C/0x110D` can request special EPS service modes under their
own runtime gates. These are authentication/safety-policy weaknesses, not
evidence of a clean steering-control primitive.

For comma/openpilot work these RoutineControl RIDs should not be treated as a production
control interface. Their semantics are factory/service-oriented, their runtime
conditions are heterogeneous, and the proven motor-current path remains
separate.

## 9. Verification

- `tests/verify_application_routine_control_surface.py` pins the 19-entry policy, control type,
  descriptor-width, callback, corrected outer SID-0x31 session gate, contrasting
  per-RID speed gates, live lifecycle-reinit bodies, one-shot writes, scheduler
  gate, service-mode chain, and termination structure directly from firmware
  bytes.
- `tests/verify_application_routine_control_1004_event_history.py` pins the
  no-speed `FF FF` request, operation-5 coalescing, forced dirty flags, exact
  persistent object set `17/18/19/20/21/23`, completion ordering, repeatability,
  and direct-actuation negative.
- `tests/verify_application_routine_control_1004_event_history_live.py` runs
  `AssertApplicationRoutine1004EventHistory.java` against the accepted project
  to pin op5/event-persistence ownership, selector-3 topology, and the live
  direct-state boundary.
- `tests/verify_application_routine_control_remaining_controls.py` pins the
  generated classifications and the `1001/1002/1103/1106/1108/1109` bodies,
  start gates, completion selectors, operation-2 checkpoint set, operation-6
  coalescing, and bounded direct-actuation negative.
- `tests/verify_application_routine_control_remaining_controls_live.py` runs
  `AssertApplicationRoutineRemainingControls.java` against the accepted project
  to pin exact operation-2/mode/thunk ownership and the direct-state boundary.
- `ghidra/scripts/verify/AssertMotorActuationBoundary.java` pins the exact
  service-state reference censuses alongside the independent d/q-current
  reference censuses.
- `tools/generate_application_routine_control_surface.py` deterministically regenerates
  `data/application_routine_control_surface.csv` from the committed CodeFlash image.
