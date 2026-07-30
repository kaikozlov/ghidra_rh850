# Control and Safety Cyclic Partition

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS ARCH-004, COM-003 (cyclic partition + TX)
>
> **Canonical artifacts:** `data/control_partition.csv`
>
> **Verification:** `tests/verify_architecture.py`, `tests/verify_control_partition.py`
>
> **Related:** [firmware-architecture](firmware-architecture.md), [application-tx](../communications/application-tx.md)

This report partitions the six cyclic subsystem functions dispatched by the
foreground loop's main application component group (`FUN_00065750` at `0x65750`)
into evidence-bounded control/safety subsystems. It also documents the separate
CAN `0x7F7` special receive callback class and closes the Tx-signal producer
investigation for signals 9, 37, and 57.

Addresses are CodeFlash virtual addresses unless they begin with `0xFEBE` (local
RAM) or `0xFFE2`/`0xFFE5` (peripheral MMIO). The application GP base is
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
conditioning. It does **not** yet prove which downstream state becomes phase
current, PWM duty, or gate-driver output. `0xFEBEBF84/0xFEBEBF9A` are the first
recovered conditioned torque-command handoff, not a claimed motor-current
command.

### Evidence grade: recovered

The producer/consumer addresses and arithmetic are deterministically checked by
`tests/verify_control_partition.py`; the OEM field label is checked separately
against the pinned external DBC.

## 9. CAN 0x7F7 special receive callback — `0x7ff86`

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

## 10. Tx signal producer closure — signals 9, 37, 57

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

## 11. Evidence boundaries

Core conclusions — function addresses, call sequences, GP-relative flag
locations, MMIO register writes, calibration table references, packer signal
coverage, and the `0x7F7` dispatch structure — come from decompilation of the
committed Ghidra project.

The following are **not** claimed:

- A downstream mapping from conditioned command state to phase current, duty,
  PWM compare, or gate-driver output;
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
