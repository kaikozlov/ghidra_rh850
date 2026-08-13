# Application WDBI control surface

This note characterizes the 19 configured application `WriteDataByIdentifier`
(`SID 0x2E`) records in `8965B4512000`. It separates raw Dcm access policy from
callback effects so an empty SecurityAccess configuration is not mistaken for
arbitrary motor actuation.

Canonical generated table: `data/application_wdbi_surface.csv`.

## 1. Access-control result

All 19 WDBI records are enabled and all 19 have a configured SecurityAccess
level count of zero.

Eighteen records use policy index 0. That policy permits diagnostic sessions
`1,2,3`; intersecting it with the outer SID-`0x2E` service gate leaves
**programming and extended sessions (`2,3`)**. DID `0x1010` is the sole policy
index-1 record and is extended-session-only (`3`).

This is a Dcm authentication result, not a claim that every callback succeeds
unconditionally. Individual WDBIs still contain runtime precondition logic.
DID `0x1010` additionally authenticates its SHE-compatible key-update package
inside ICU-S, independent of the empty Dcm SecurityAccess table.

The practical consequence for policy-0 records is that an unauthenticated
extended-session transition (`10 03`) is sufficient to reach the per-DID
precondition/action machinery. No successful `27 xx` SecurityAccess exchange is
required by the configured Dcm policy.

## 2. Selector and wire shape

The selector checks are recovered from
`application_wdbi_selector_supported @ 0x955DC`; exact request-size validation
is recovered from `application_wdbi_input_length_invalid @ 0x95624`.

- every configured WDBI supports selector `01`;
- only `0x110A` and `0x110D` support selector `02`;
- only crypto-test activation DIDs `0x100E` and `0x100F` lack selector `03`;
- selector-1 input data is zero bytes for 17 of 19 DIDs;
- `0x1004` consumes two selector-1 input bytes;
- `0x1010` consumes 64 selector-1 input bytes and returns 49 bytes on selectors
  `01`/`03`.

Thus many stateful control requests have only the selector/DID header on the
wire after SID, for example the already-proven bank-1 activation request
`2E 01 10 0F`.

## 3. Callback table

The 19x12-byte table at CodeFlash `0x25804` binds each DID to a precondition and
action callback. Its SHA-256 is
`bb72da6fb416c6fc47cb87cf2c060bb99f6bdb95499254bfbbfe960f1ccc979c`.
Both callback columns are seeded as dispatch-proven function tables so these
edges survive clean Ghidra rebuilds.

Important recovered effects include:

| DID | Action | Bounded interpretation |
|---|---:|---|
| `1000` | `0x4F060` | builds 32-byte supported-`0x10xx` WDBI bitmap |
| `1004` | `0x4F170` | fixed maintenance trigger: selector 1 requires input `FF FF`, then queues internal operation 5 without consuming a tester-chosen value |
| `1007` | `0x4F1EA` | one-shot live lifecycle reinitialization of groups `FEBEB454/455`; no local speed/mode gate |
| `1008` | `0x4F25C` | one-shot diagnostic-only live lifecycle reinitialization of group `FEBEB456`; no local speed/mode gate |
| `100E` | `0x8A774` | calls crypto-test bank-0 activator `0x68F92` |
| `100F` | `0x8A782` | calls crypto-test bank-1 activator `0x69018` |
| `1010` | dedicated path | ICU-S command-8 authenticated key update |
| `1100` | `0x4F32E` | builds 32-byte supported-`0x11xx` WDBI bitmap |
| `110A` | `0x4F630` | service-mode control, internal mode 2; selector 2 termination |
| `110C` | `0x4F702` | service-mode control, internal mode 3 |
| `110D` | `0x4F7B8` | service-mode control, internal mode 4; selector 2 termination |

Several other callbacks are demonstrably stateful but their OEM test names are
not assigned. The generated CSV records their recovered callees and leaves the
semantics bounded rather than inventing names from behavior alone.

## 4. `0x1007/0x1008` ungated live lifecycle reinitialization

DIDs `0x1007` and `0x1008` expose a distinct availability/control-state surface
that is weaker-gated than several neighboring WDBIs.

Both are policy-0, selector-1, zero-payload requests. Their preconditions call
shared lifecycle-readiness helper `FUN_B79F8` and then check a dedicated
one-shot flag (`FEBE8157` or `FEBE8158`). Neither precondition reads
`application_vehicle_speed_raw @ FEBEE892`, alternate-handoff state, or system
mode. This is not merely because speed is enforced at a common WDBI layer:
`0x1002` and `0x1106` explicitly read `FEBEE892` and compare it against the same
calibration threshold in their own precondition callbacks.

The outer session path does not restore that missing condition. Application
session policy `0x4C942` applies the vehicle-speed rejection only when the
requested session is **2** (programming). Requested session **3** (extended)
returns success through that policy without the speed comparison. Consequently
the statically recovered wire sequence is:

- `10 03` — enter unauthenticated extended session;
- `2E 01 10 07` — request the `0x1007` reinitializer; or
- `2E 01 10 08` — request the `0x1008` reinitializer.

`0x1007` reaches `FUN_B7A36(0)`. That helper forces lifecycle groups
`FEBEB454/455` to transition state `0x11` and calls dedicated reinitialization
helpers for subordinate components. `FUN_B7A36` is also used by one internal
fault/lifecycle-recovery path, so the bounded interpretation is that the WDBI
exposes a live recovery/reinitialization operation rather than a unique actuator
primitive.

`0x1008` reaches `FUN_B7AAE`. That helper forces `FEBEB456` to state `0x11` and
calls five subordinate reinitializers. Its only recovered caller is the
WDBI-owned thunk at `0xFDEA8`, making this particular group reset
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
Subsequent selector-1 attempts therefore fail their busy check until reset.

This supports a bounded finding: an unauthenticated extended-session client can,
subject to lifecycle-readiness conditions but without a local or outer
stationary gate, inject one live subsystem reinitialization into the operational
scheduler. Static evidence does **not** show these lifecycle states joining the
proved d/q current/PWM producer cone, so this is an availability/control-state
primitive rather than arbitrary steering actuation.

## 5. `0x110A/0x110C/0x110D` service-mode chain

These three WDBIs are the strongest state-changing entries recovered in this
pass.

Selector `01` loads internal mode `2`, `3`, or `4` respectively and reaches the
shared service-mode dispatcher `FUN_B1F34` through thunk `0xFE038`.
`FUN_B1F34` records the corresponding activity bit and can post system-mode
event `6`. In the `0x500` system-mode family, the coordinator converts those
activity bits to event `0x2E`; `FUN_B1DAC` then initializes the selected service
subtype and commits **system submode `0x520`**.

The `0x520` initializer `FUN_B7054` creates a dedicated service-state island,
latches subtype `1/2/3`, and clears paired subsystem command slots 0 and 1 by
calling fixed-slot writer `FUN_562C8` through thunk `0xFED2C`.

`0x110A` and `0x110D` expose selector `02` termination. Their stop callbacks set
the service state to terminal value `3`; the `0x520` coordinator emits event
`0x2F`, performs cleanup, and returns to parent mode `0x500`. `0x110C` has no
selector-2 entry and instead relies on its internal state progression.

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
left the entire 19-entry WDBI set at SecurityAccess level count zero, including
state-changing factory/service controls.

The strongest recovered consequences are two related availability/control-state
paths: `0x1007/0x1008` can inject one-shot live lifecycle reinitialization into
normal operational scheduling without the explicit speed gate used by other
WDBIs, and `0x110A/0x110C/0x110D` can request special EPS service modes under
their own runtime gates. These are authentication/safety-policy weaknesses, not
evidence of a clean steering-control primitive.

For comma/openpilot work these WDBIs should not be treated as a production
control interface. Their semantics are factory/service-oriented, their runtime
conditions are heterogeneous, and the proven motor-current path remains
separate.

## 8. Verification

- `tests/verify_application_wdbi_surface.py` pins the 19-entry policy, selector,
  descriptor-width, callback, programming-only session speed gate, contrasting
  per-DID speed gates, live lifecycle-reinit bodies, one-shot writes, scheduler
  gate, service-mode chain, and termination structure directly from firmware
  bytes.
- `ghidra/scripts/verify/AssertMotorActuationBoundary.java` pins the exact
  service-state reference censuses alongside the independent d/q-current
  reference censuses.
- `tools/generate_application_wdbi_surface.py` deterministically regenerates
  `data/application_wdbi_surface.csv` from the committed CodeFlash image.
