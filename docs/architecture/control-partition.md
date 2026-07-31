# Control and Safety Cyclic Partition

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS ARCH-004, COM-003 (cyclic partition + TX)
>
> **Canonical artifacts:** `data/control_partition.csv`, `data/motor_actuation_path.csv`
>
> **Verification:** `tests/verify_architecture.py`, `tests/verify_control_partition.py`, `tests/verify_motor_actuation_boundary.py`, `ghidra/scripts/verify/AssertMotorActuationBoundary.java`
>
> **Related:** [firmware-architecture](firmware-architecture.md), [application-tx](../communications/application-tx.md)

This report partitions the six cyclic subsystem functions dispatched by the
foreground loop's main application component group (`FUN_00065750` at `0x65750`)
into evidence-bounded control/safety subsystems. It also documents the separate
CAN `0x7F7` special receive callback class and closes the Tx-signal producer
investigation for signals 9, 37, and 57.

Addresses are CodeFlash virtual addresses unless they begin with `0xFEBE` (local
RAM) or `0xFFE2`/`0xFFE5`/`0xFFE7` (peripheral MMIO). The application GP base is
`0xFEBEB800`. The machine-readable partition table is
`data/control_partition.csv`; the self-contained verification is in
`tests/verify_control_partition.py`.

The six callees are invoked unconditionally and in fixed order from `0x65750`,
which is itself step 5 of the foreground cycle documented in
`../architecture/firmware-architecture.md` section 3.2.

## 1. Summary table

| Addr | Inferred subsystem | State root(s) | Key outputs | Evidence grade |
|---:|---|---|---|---|
| `0x68c0c` | Dormant crypto-test bank scheduler | `0xFEBE508D`..`0xFEBE508F` | Calls three CAN-controlled test-bank state machines | recovered |
| `0x791c4` | Communication manager | `0xFEBE3DF2` | CAN TX via `application_com_tx_main`; ~20 COM calls | bounded |
| `0x96bac` | Safety diagnostics | `0xFEBE5E28` | calls 3 diagnostic handlers | bounded |
| `0x68de6` | Dormant crypto-test continuation | `0xFEBE5085`, `0xFEBE508A`, `0xFEBE508F` | Test-bank result/finalization handlers | recovered |
| `0x57ac2` | System-mode and control dispatcher | `0xFEBE8BBA`, `0xFEBEACEE` | Full/reduced control pipelines | recovered |
| `0x6547c` | Timer/peripheral reload | none | MMIO writes to `0xFFE20000`/`0xFFE21000`/`0xFFE50000` | recovered |

A seventh row covers the `0x7F7` special receive callback:

| Addr | Inferred subsystem | Role | Evidence grade |
|---:|---|---|---|
| `0x7ff86` | Application CAN special RX demux | Separate receive callback for acceptance rule 50 / CAN ID `0x7F7` | bounded |

## 2. Dormant crypto-test bank scheduler — `0x68c0c`

The earlier “motor control state machine” label was wrong. Decompiling the
descendants identifies the `0xFEBE5085..0xFEBE508F` cluster as the three dormant
CAN-controlled crypto-test banks documented in
`../security/secoc/application-chain.md`, not torque state.

`0x68c0c` dispatches the bank state machines in fixed order. The last gated
branch calls `crypto_test_bank1_state_step` at `0x68bc2`, whose command-5 path
uses the ICU-S wrapper. The preceding handlers at `0x67fce`, `0x680d4`,
`0x68198`, `0x682f8`, and `0x686ea` belong to the neighboring test banks and
their state transitions. The `0xA5` and `0x5A` markers are state-machine
sentinels; they are not motor-mode values.

The function has no direct actuator or timer write. Its output is the same RAM
test-bank state consumed by `0x68de6` later in the foreground group.

### Evidence grade: recovered

The dispatch targets and shared state are directly reconstructed from firmware.
No motor or torque semantics are assigned to this branch.

## 3. Communication manager — `0x791c4`

### Input flags and state roots

The entire body is gated by `DAT_febe3df2 == 0xFE01` (i.e. the 16-bit value at
`0xFEBE3DF2`, GP `-0x7A0E`, equals `-0x1FF` as unsigned = `0xFE01`). When the
flag does not match, the function returns immediately.

### Dispatch

When enabled, the function calls approximately twenty sub-functions in fixed
order. The recovered call sequence is:

```
FUN_0007adac, FUN_0007ab32, FUN_0007b3ac, FUN_00078e4e, FUN_0007aed0,
FUN_0007bf8a, FUN_0007c5d6, FUN_0007c5b2, FUN_0007adc2, FUN_0007c440,
FUN_0007ada8, FUN_0007adaa, FUN_0007adb0, FUN_0007dd96, FUN_0007da46,
FUN_00078e86, application_com_tx_main, FUN_00069380, FUN_00081d46,
FUN_00078ea6, FUN_0007adae
```

### Output effects

The dominant output is CAN TX via `application_com_tx_main()`, which drives the
six COM transmit I-PDUs documented in `../communications/application-tx.md`. The
other callees handle COM signal processing, PDU routing, and confirmation. No
direct MMIO writes appear in this function.

### Cross-rate interfaces

This is the sole cyclic consumer of the application output staging area
(`0xFEBE8094..0xFEBE8110`) populated by the motor-control and
safety/configuration subsystems. The COM packers (`0x4BCEE` etc.) read those
staging bytes and write them into the COM transmit buffers, which are then
queued by `application_com_tx_main`.

### Evidence grade: bounded

The enable flag, call sequence, and TX path are recovered. The individual roles
of the ~20 callees (beyond `application_com_tx_main`) are not decomposed here.

## 4. Safety diagnostics — `0x96bac`

### Input flags and state roots

Gated by `DAT_febe5e28 == 0xA5` (`0xFEBE5E28`, GP `-0x59D8`, equal to `-0x5b`
as signed byte). When the flag does not match, the function returns immediately.

### Dispatch

When enabled, calls three handlers: `FUN_000902a8`, `FUN_00096dce`,
`FUN_00096c30`.

### Output effects

No direct MMIO or CAN TX writes in the body. All effects are mediated through
the three callees, which are not further decomposed here.

### Cross-rate interfaces

The safety enable flag `0xFEBE5E28` is set by another runtime path not in these
six cyclics. This subsystem is a consumer of diagnostic state but does not
directly feed the communication manager's TX path.

### Evidence grade: bounded

The enable flag and call set are recovered. The diagnostic checks performed by
the three handlers are not claimed.

## 5. Dormant crypto-test continuation — `0x68de6`

This is the result/finalization half of the same dormant crypto-test cluster as
`0x68c0c`. It consumes state bytes at `0xFEBE5085`, `0xFEBE508A`, and
`0xFEBE508F`, conditionally calls `0x68c86`, `0x68cd2`, and `0x68d0e`, then
always calls `0x68d3c`. The `0x68d0e` descendant is the recovered bank-1
command-5 finalizer.

### Evidence grade: recovered

The function is not a motor-control continuation. Its state and descendants are
the crypto-test harness; no actuator semantics are claimed.

## 6. Foreground system-mode and control dispatcher — `0x57ac2`

`0x57ac2` does validate an E2E-protected version/state block, but treating it as
mere “configuration management” hid the real control path. Once the `0xA55A`
marker and version/complement checks pass, it selects one of two system-mode
pipelines:

```text
changed/full path:    0x57AC2 -> 0xFDD40 -> 0xBEC4C
unchanged/reduced:    0x57AC2 -> 0xFDD54 -> 0xBF17E
```

The full dispatcher reaches `system_mode_telemetry_snapshot` at `0xBA43A`.
That function snapshots and scales runtime inputs, then calls `0xCBA72`, whose
callee `0xCB86E` executes a large control pipeline. This is the first
firmware-backed route from the six-function foreground group into the recovered
steering-command conditioner described below.

The E2E helpers (`0x6f71c`, `0x6f6a6`, `0x6f97a`), version reconciliation, and
rolling state at `0xFEBE8BC9/0xFEBE8BCB` remain valid structural observations.
They are gate/setup logic around the control dispatch, not the torque algorithm
itself.

### Evidence grade: recovered

The call graph and version gates are deterministic. The exact semantics of the
full versus reduced system modes remain bounded.

## 7. Timer and peripheral reload — `0x6547c`

### Input flags and state roots

No state flag gates this function; it runs unconditionally every foreground
cycle.

### Output effects — MMIO writes

Writes three timer/peripheral register blocks from calibration tables, with
interrupts disabled. The interrupt-disable wrapper is `FUN_0006f134(0xFFC0)` /
`FUN_0006f15a(restore)`.

| MMIO region | Registers written | Calibration source |
|---|---|---|
| `0xFFE20000` | `+0x00, +0x04, +0x0C, +0x14, +0x20, +0x38, +0x58, +0x5C` | `0x30F9C`, `0x30FA0/4/8/C` |
| `0xFFE21000` | `+0x00, +0x04, +0x0C, +0x14, +0x58, +0x5C` | `0x30FA0/4/8/C` |
| `0xFFE50000` | `+0x00, +0x04, +0x08, +0x0C, +0x5C, +0x60` | `0x30F7C/84/8C/94` |

The `+0x5C` and `+0x58` registers are masked with `0xBED4`/`0xFFD0`/`0xF0`
(preserving specific control bits) rather than overwritten outright. The
calibration values are loaded as `table_value - 1` (reload registers are
typically `count - 1`).

### Calibration table references

| Address | Used for |
|---:|---|
| `0x30F9C` | TAU reload (TAUJ0); also drives `0xFFE20020`/`0xFFE20038` |
| `0x30FA0` | period/reload value for `0xFFE20004`/`0xFFE21004` |
| `0x30FA4` | paired reload value for `0xFFE2000C`/`0xFFE2100C` |
| `0x30FA8` | reload value for `+0x0C` |
| `0x30FAC` | reload value for `+0x14` |
| `0x30F7C/84/8C/94` | values for the `0xFFE50000` block |

### Cross-rate interfaces

This is a leaf cyclic: it reads calibration tables and writes MMIO. It does not
consume flags from other cyclics or produce RAM state for them. It establishes
the hardware timer period that governs the overall foreground tick rate.

### Evidence grade: recovered

The MMIO addresses, calibration table addresses, interrupt-disable wrapper, and
`-1` reload encoding are all directly recovered from the decompiled body. This
this is the highest-confidence subsystem in the partition. The exact peripheral
channel ownership and any motor-PWM role remain unproven.

## 8. Protected steering-command ingress and conditioning

This is the first defensible torque-path handoff recovered from firmware. The
static producer/consumer chain is:

```text
authenticated CAN 0x2E4 / PDU 6
  -> application_unpack_can_2e4 @ 0x4A244
  -> signal 61: signed BE16 B1..B2 @ 0xFEBE7F94
  -> application_rx_signal_consumer_56fc2
  -> 0xFEBEF184
  -> system_mode_telemetry_snapshot @ 0xBA43A
       scale by 0x100 / 100
  -> 0xFEBEAE20
  -> 0xC853A clamp + mode-indexed gain
  -> 0xFEBEBF80
  -> 0xC85B6 signed saturation + rate limit
  -> 0xFEBEBF9A and 0xFEBEBF84
```

### Firmware-static evidence

- `0x4A244` extracts signal 61 into `0xFEBE7F94`; the generated RX map records
  it as signed big-endian B1..B2 under protected PDU 6.
- `0x57138` loads `0xFEBE7F94`, and `0x57148` stores the same halfword to
  `0xFEBEF184`.
- `0xBA4B8` loads `0xFEBEF184`, invokes signed scaling helper `0xCBB74` with
  numerator `0x100` and denominator `100`, and `0xBA808` commits the result to
  `0xFEBEAE20`.
- `0xC853A` clamps that signed value to calibration `+/-0x1BD80`, chooses a gain
  from tables at `0xD603C`/`0xD607C`, and writes the adjusted command to
  `0xFEBEBF80`.
- `0xC85B6` converts `0xFEBEBF80` to signed 16-bit range, rate-limits it against
  prior value `0xFEBEBF9A` using calibration `0x1BD8E`, and writes conditioned
  values at `0xFEBEBF9A` and `0xFEBEBF84`.

The conditioning stages execute under the CH3-polled foreground domain, not in
the TAUJ0 CH0/CH2 ISR bodies:

```text
foreground loop 0x64FCC polls TAUJ0 CH3 EIRF136
  -> 0x65750
  -> 0x57AC2
  -> 0xFDD40 -> 0xBEC4C -> 0xBA43A
  -> 0xCBA72 -> 0xCB86E -> 0xC853A / 0xC85B6
```

TAUJ0 CH0 and CH2 are separate interrupt domains:

```text
CH0 ISR 0x64F18 -> 0x6424C -> 0x656F0
CH2 ISR 0x64F90 -> 0x64376 -> 0x65720
```

### External-source corroboration

The pinned opendbc `toyota_secoc_pt.dbc` names CAN decimal 740 (`0x2E4`)
`STEERING_LKA` and names bits `15|16@0-` — the same B1..B2 signed field —
`STEER_TORQUE_CMD`. This label is external evidence; the RAM and call chain
above are firmware-static evidence.

### Boundary

The chain proves authenticated steering-torque-command ingress and bounded
conditioning. `0xC85B6` also derives `0xFEBEBFA2`; `0xCB700` scales that state
into application export `0xFEBEAE16`. Snapshot and transport functions copy it
to `0xFEBEE8CA`, `0xFEBEEB1C`, and `0xFEBEEBA4`.

The expanded reader/writer census does **not** turn any of those locations into
a motor-current command:

- `0xFEBEBF84` has writes only;
- `0xFEBEBF9A` is read only by `0xC85B6` as its own prior rate-limit state;
- `0xFEBEAE16` is read by `0xBAFB2`, `0xBCB3A`, `0xFD49E`, and `0xFD562`, which
  perform initialization/snapshot/export movement rather than the high-rate
  current-control computation;
- the three `0xFEBEE8CA/0xFEBEEB1C/0xFEBEEBA4` destinations have no recovered
  readers.

The processor audit locks those exact direct-reference sets. Whole-program
decompiler-text, high-p-code, and GP-displacement/scalar scans were also used to
look for indirect consumers. They found no recovered path into the proved d/q
current references at `0xFEBE6D28/0xFEBE6D2A`. This is a bounded static negative,
not proof that no table-driven, computed, or runtime-only handoff can exist.

### Evidence grade: recovered

The producer/consumer addresses and arithmetic are deterministically checked by
`tests/verify_control_partition.py`; the expanded stopping-boundary census is
checked by `AssertMotorActuationBoundary.java`; the OEM field label is checked
separately against the pinned external DBC.

## 9. Independent phase-current control to physical PWM boundary

Reverse-slicing from firmware-used hardware registers establishes a separate,
high-rate motor-control chain under TAUJ0 CH0:

```text
indexed peripheral result windows FEEF81E0 / FEEF8A20
  -> 0x61068 / 0x610A8 -> CH0 sample snapshot 0x6578E
  -> phase-sample publish 0x4FB02
  -> dual U/V/W phase-current conditioning 0x47C3C
  -> dual Clarke/Park-like feedback transform 0x35960
  -> feedback filtering/combination 0x37FB6 / 0x37644
  -> d/q current references 0x37712 at FEBE6D28 / FEBE6D2A
  -> PI-like current loops 0x36902 / 0x36A44
  -> bounded rotating-frame command preparation 0x36200 / 0x3650C / 0x36742
  -> inverse rotating-frame transforms 0x38464 / 0x38554
  -> phase-command limiting and publication 0x35F6C / 0x3601A / 0x3802A / 0x38134 / 0x3875A
  -> output slot 0 via 0x56B18
  -> phase-duty slot selection 0x569A8
  -> TSG3 compare conversion 0x56D3E / 0x60BFA
  -> staged compare RAM FEBE38A2..FEBE38AE
  -> TSG3 commit 0x60DDC
  -> TSG30/31 CMPWE/CMPVE/CMPUE
```

The machine-readable stage map is `data/motor_actuation_path.csv`.

### Phase feedback and current control

`0x47C3C` was previously mislabeled a calibration-only handler. Its complete
caller census proves both a version-transition path (`0x5CC08`) and a steady
path (`0x5CE0C`) beneath the TAUJ0 CH0 worker. It conditions two three-phase
sample sets at `0xFEBE81E4..0xFEBE81FA`, applying per-phase offset/gain,
saturation, and missing-phase reconstruction into `0xFEBE7DE6..0xFEBE7DF0`.

`0x35960` applies two three-phase-to-rotating-frame transforms using angle
coefficient pairs `0xFEBE7CEE/0xFEBE7CF0` and
`0xFEBE7CFA/0xFEBE7CFC`. Its fixed-point constants `0x3441` and `0x5A82`, the
three-input structure, and the downstream reference-minus-feedback loops
support the bounded Clarke/Park classification. `0x37FB6` and `0x37644`
filter/combine the result into feedback at `0xFEBE6D18/0xFEBE6D1C`.

`0x37712` independently constructs d/q current-reference state at
`0xFEBE6D28/0xFEBE6D2A`. `0x36902` computes
`0xFEBE6D2A - 0xFEBE6D1C`; `0x36A44` computes
`0xFEBE6D28 - 0xFEBE6D18`. Both contain gain selection, accumulated state,
signed saturation, and calibrated output limits: PI-like current-control
structure rather than a bare diagnostic comparison. Their outputs pass through
the bounded command/limit stages and into rotating-frame command pairs at
`0xFEBE6BE8..0xFEBE6BEE`.

`0x38464` and `0x38554` rotate those two command pairs back into two bounded
three-phase command triplets. Subsequent common-mode/limit stages publish two
three-phase banks through arbitration slot 0 and `0x569A8` selects the active
bank for each motor output.

### TSG3 physical output

The P1M-E User's Manual supplies the hardware names:

- section 25.1.2: `TSG30_base = 0xFFE70000`,
  `TSG31_base = 0xFFE71000`;
- sections 25.3.48–50: 32-bit extended HT-PWM W/V/U compare registers at
  offsets `0x180`, `0x184`, and `0x188`.

| Address | Register | Firmware writer |
|---:|---|---:|
| `0xFFE70180` | `TSG30CMPWE` | `0x60DDC` |
| `0xFFE70184` | `TSG30CMPVE` | `0x60DDC` |
| `0xFFE70188` | `TSG30CMPUE` | `0x60DDC` |
| `0xFFE71180` | `TSG31CMPWE` | `0x60DDC` |
| `0xFFE71184` | `TSG31CMPVE` | `0x60DDC` |
| `0xFFE71188` | `TSG31CMPUE` | `0x60DDC` |

The manual states that one extended-compare write updates the paired compare
state used for symmetric triangular HT-PWM generation. The exact store bytes
at `0x60DFE/0x60E06/0x60E0E` are asserted by
`tests/verify_motor_actuation_boundary.py`.

Scheduling order matters: `0x656F0` calls `0x60DDC` before dispatching
`0x5784C`, so each CH0 invocation commits the previously staged compare bank
and then computes the next current-control/compare state. The result-window
addresses `0xFEEF81E0/0xFEEF8A20` are firmware-static observations; their exact
peripheral-module/register names remain unresolved and are not labeled as ADC
SFRs.

### Command-to-current-reference gap

This chain proves phase feedback, d/q current control, inverse transforms,
three-phase duty staging, and writes to physical motor-control PWM registers.
It does **not** prove that authenticated CAN `0x2E4` controls those writes. The
two proved chains stop at:

```text
command side:  FEBEBF84 / FEBEBF9A -> FEBEBFA2 -> FEBEAE16 and snapshots
actuator side: independent d/q current references FEBE6D28 / FEBE6D2A -> PWM
```

No recovered static data-flow edge joins those endpoints. That exact
**command-to-current-reference gap** is the strongest defensible static
actuation boundary for this image.

The gap is now hardened, not merely open. The producer cone of
`0xFEBE6D28`/`0xFEBE6D2A` is enumerated and motor-internal:

- `dual_motor_dq_current_reference` at `0x37712` (entry `0x3770e`) builds both
  references from `0xFEBE6D4E`/`0xFEBE6D50`/`0xFEBE6D70`/`0xFEBE6D7E`
  (summed and saturated) plus `0xFEBE6D52`/`0xFEBE6D54` and calibration
  `0x1842C`/`0x1842E`. Every input lives in the `0xFEBE6D**` motor block.
- Those inputs are produced by `0x3795E`, `0x37B5A`, and `0x37CD4`, which
  reference only `0xFEBE5F**`/`0xFEBE6D**` addresses. No conditioned-command
  location (`0xFEBE7F94`/`0xFEBEF184`/`0xFEBEAE20`/`0xFEBEBF80`/
  `0xFEBEBF84`/`0xFEBEBF9A`/`0xFEBEBFA2`/`0xFEBEAE16`) appears anywhere in the
  producer cone.
- The apparent second writer, `autosar_os_task_signal_dispatch`
  (function entry `0x58404`), at instruction `0x5AE28`, is a buffer-clear
  idiom, not a producer: it sets `ep = 0xFEBE6D24`, stores zero (`r0`) to
  `0xFEBE6D24..0xFEBE6D2E`, then calls `0x3770e`. It does not copy command
  state.

This is still a bounded static negative — a table-driven, computed, or
runtime-only handoff (e.g. an AUTOSAR RTE outer-loop join not visible to the
static call graph) is not excluded. But the producer cone is now enumerated and
clean two levels deep, so the gap is materially stronger than "no edge found."

### Torque-limit and plausibility layers are command-disconnected

The SWEEP-004 torque-limit selector `0xB8C1A` (branches on a `0x55AAAA55`
calibration-profile marker between two table sets) does not gate the
conditioned `0x2E4` command. It operates on a separate `0xFEBEB5**` region
populated by the `0xB89CC`/`0xB8A12`/`0xB8B10` cluster, none of which read any
command-state location; that cluster is the EPS's internal assist-torque path,
not the external LKA command. The only torque limiting applied to the
authenticated command itself is inside its own conditioning chain: the
`0xC853A` clamp (`±0x1BD80`, gain tables `0xD603C`/`0xD607C`) and `0xC85B6`
rate limit (`0x1BD8E`), already documented in section 8.

The conditioned-command export `0xFEBEAE16` has only snapshot/transport
consumers: `0xBAFB2` packs it (with ~40 other state fields) into an event
record handed to `FUN_000FF09C` selector `9` (the `0xAB`/diagnostic snapshot
worker); `application_input_snapshot_update`; and `0xFD49E`/`0xFD562`
transport. No recovered reader forwards it into the high-rate motor loop.

Implication for an external signer: a correctly authenticated `0x2E4` frame is
SecOC-accepted (the receive chain fails closed otherwise) and conditioned, but
static analysis cannot prove it reaches motor actuation. Correct signing is
**necessary but not statically provable sufficient** for actuation; that must
be confirmed dynamically on a bench with a valid key.

### Evidence grade: recovered; physical register boundary verified

The call order, RAM transitions, transform/controller structure, and compare
pipeline are recovered from firmware-static evidence. The six TSG3 register
addresses and exact stores are verified against deterministic tests and the
P1M-E manual. The missing command bridge remains bounded.

## 10. CAN 0x7F7 special receive callback — `0x7ff86`

### Structure

`application_can_special_rx_demux` at `0x7ff86` is a separate receive callback
class registered for acceptance rule 50 / standard CAN ID `0x7F7`. It is
distinct from both the 47-PDU normal demux (`0x80006`) and the diagnostic demux
(`0x80114`) documented in `../architecture/firmware-architecture.md` section 5.3.

The function takes `(param_1, param_2, param_3)` where `param_3` selects an
entry from the pointer table at `0x21A2C`. It indexes into a four-word record:
`piVar3[0]` = match mask table, `piVar3[1]` = callback function pointer,
`piVar3[2]` = filter word table, `piVar3[3]` = range bounds. It iterates entries
and dispatches to `piVar3[1]` on a mask match, passing a computed PDU ID and the
frame data.

### Registration

The function is referenced from four data locations in the `0x21A48..0x21A58`
range (the pointer table entries), confirming it is a registered callback
rather than dead code.

### Evidence grade: bounded

The dispatch structure, pointer table, and registration are recovered. The
upper-protocol semantics of CAN `0x7F7` are **not** resolved — no OEM protocol
name is invented. CAN `0x7F8` (the single active special-class Tx route per
`../communications/application-tx.md`) is a separate endpoint and is not claimed to
be the response pair without further evidence.

## 11. Tx signal producer closure — signals 9, 37, 57

The three configured-but-unresolved Tx signals have been checked against their
respective packer decompilations:

| Signal | CAN ID | Wire | Packer | Packer evidence |
|---:|---:|---|---:|---|
| 9 | `0x260` | B7 | `0x4BCEE` | Packs signals 0..8 only via 9 `application_com_pack_big_endian_signal` calls; does not touch B7 |
| 37 | `0x262` | B7 | `0x4BE24` | Packs signals 10..36 only via 28 calls; does not touch B7 |
| 57 | `0x4C8` | B4..B7 | `0x4BC54` | Packs signals 54..56 only via 3 calls; does not touch B4..B7 |

**Conclusion:** All three packers are confirmed to leave their respective final
bytes untouched. No checksum or E2E computation exists inside any of the three
packer functions — each ends with a common `FUN_0007bffe`/`FUN_0007d526`/
`FUN_0007d37e`/`FUN_0007d5aa` COM-send-status sequence that operates on the PDU
state, not the signal bytes. The runtime producers (if any) for signals 9, 37,
and 57 must live outside the packer functions — either in a separate COM
callback, a different cyclic, or not at all in this calibration. The signals
remain **configured-unresolved** with packer evidence now recorded in
`data/application_tx_map.csv`.

## 12. Evidence boundaries

Core conclusions — function addresses, call sequences, GP-relative flag
locations, MMIO register writes, calibration table references, packer signal
coverage, and the `0x7F7` dispatch structure — come from decompilation of the
committed Ghidra project.

The following are **not** claimed:

- A static data-flow bridge from conditioned authenticated command state into
  the independently proved d/q current references or PWM pipeline;
- Physical inverter switch/gate-driver behavior beyond the TSG3 HT-PWM compare
  register writes;
- OEM-level names for the remaining system-mode states or diagnostic checks;
- Exact full/reduced mode semantics under `0x57ac2`;
- Motor/PWM ownership for every MMIO region written by `0x6547c`;
- The upper-protocol identity of CAN `0x7F7`;
- A response-pairing between `0x7F7` (RX) and `0x7F8` (TX);
- Runtime producers for signals 9, 37, and 57 beyond the packer exclusion.

See also:

- `../architecture/firmware-architecture.md` for the foreground cycle and interrupt map;
- `../communications/application-tx.md` for the complete TX PDU and signal map;
- `../communications/application-rx.md` for the normal and diagnostic RX paths.
