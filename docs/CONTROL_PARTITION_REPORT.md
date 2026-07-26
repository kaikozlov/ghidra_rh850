# Control and Safety Cyclic Partition

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
`docs/FIRMWARE_ARCHITECTURE.md` section 3.2.

## 1. Summary table

| Addr | Inferred subsystem | State root(s) | Key outputs | Evidence grade |
|---:|---|---|---|---|
| `0x68c0c` | Motor control state machine | `0xFEBE508D`, `0xFEBE508E` | RAM state flags; calls 6 sub-handlers | bounded |
| `0x791c4` | Communication manager | `0xFEBE3DF2` | CAN TX via `application_com_tx_main`; ~20 COM calls | bounded |
| `0x96bac` | Safety diagnostics | `0xFEBE5E28` | calls 3 diagnostic handlers | bounded |
| `0x68de6` | Motor control continuation | `0xFEBE5085` | calls 4 sub-handlers | bounded |
| `0x57ac2` | Configuration and parameter management | `0xFEBE8BBA` | RAM validity/E2E state; reconciliation | bounded |
| `0x6547c` | Timer and PWM reload | none | MMIO writes to `0xFFE20000`/`0xFFE21000`/`0xFFE50000` | recovered |

A seventh row covers the `0x7F7` special receive callback:

| Addr | Inferred subsystem | Role | Evidence grade |
|---:|---|---|---|
| `0x7ff86` | Application CAN special RX demux | Separate receive callback for acceptance rule 50 / CAN ID `0x7F7` | bounded |

## 2. Motor control state machine — `0x68c0c`

### Input flags and state roots

The primary state byte is at `0xFEBE508D` (`DAT_febe508d`, GP `-0x6773`). A
secondary state byte at `0xFEBE508E` (`DAT_febe508e`, GP `-0x6772`) drives an
alternative branch. Four flag bytes gate the sub-handlers:

| Flag | GP offset | Absolute | Meaning (bounded) |
|---|---|---|---|
| gate flag | `-0x677b` | `0xFEBE5085` | nonzero → invoke `FUN_000682f8` |
| phase flag | `-0x6777` | `0xFEBE5089` | `'Z'` (0x5A) → complete phase and clear |
| mode flag | `-0x6776` | `0xFEBE508A` | `0x01` → invoke `FUN_000686ea` |
| mode flag | `-0x6771` | `0xFEBE508F` | `0x01` → invoke `FUN_00068bc2` |

### Dispatch

When `0xFEBE508D == 0xA5` (`-0x5b` as signed byte), the function calls
`FUN_00067fce`; when `0xFEBE508E == 0xA5`, it calls `FUN_000680d4`.
`FUN_00068198` is called unconditionally. The four flag-gated handlers
(`FUN_000682f8`, `FUN_000686ea`, `FUN_00068bc2`, and a phase-completion path via
`FUN_00067f14`) run based on their respective flags. On phase completion, the
function clears flags at `0xFEBE5085`, `0xFEBE5086`, `0xFEBE5086+2`, and
`0xFEBE5089`.

### Output effects

RAM state writes to the GP `-0x677x` flag cluster; the current state byte is
latched to `0xFEBE508E` (`*(char*)(GP-0x6772) = cVar1`) at function exit. No
direct MMIO or CAN TX writes are visible in this function body; all physical
effects are mediated through the sub-handlers.

### Cross-rate interfaces

The flag at `0xFEBE5085` (GP `-0x677b`) is also the state root consumed by
`0x68de6` (the motor control continuation), establishing a producer-consumer
link between the two motor-control cyclics. The sub-handlers
(`FUN_00067fce`, `FUN_000680d4`, `FUN_00068198`, `FUN_000682f8`, `FUN_000686ea`,
`FUN_00068bc2`) are not decomposed further in this report.

### Evidence grade: bounded

The state-machine structure, flag locations, and dispatch tree are recovered
from decompilation. The OEM-level meaning of each state value (beyond the
`0xA5`/`0x5A` markers) and the physical motor-control behavior of each
sub-handler are not claimed.

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
six COM transmit I-PDUs documented in `docs/APPLICATION_TRANSMIT_MAP.md`. The
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

## 5. Motor control continuation — `0x68de6`

### Input flags and state roots

Consumes the flag at `0xFEBE5085` (`DAT_febe5085`, GP `-0x677b`) — the same
flag produced by `0x68c0c` — as its primary gate. Two additional flags at
GP `-0x6776` (`0xFEBE508A`) and `-0x6771` (`0xFEBE508F`) gate conditional calls.

### Dispatch

- `0xFEBE5085 == 0x01` → `FUN_00068c86`
- `GP-0x6776 == 0x01` → `FUN_00068cd2`
- `GP-0x6771 == 0x01` → `FUN_00068d0e`
- `FUN_00068d3c` called unconditionally

### Cross-rate interfaces

This is the continuation half of the motor-control cyclic pair (`0x68c0c` →
`0x68de6`). It reads flags written by `0x68c0c` and is therefore strictly
downstream in execution order within the same foreground cycle.

### Evidence grade: bounded

The flag consumption and call set are recovered. The roles of the four callees
are not claimed.

## 6. Configuration and parameter management — `0x57ac2`

### Input flags and state roots

Validates a calibration block using the marker `0xA55A` (i.e.
`*(short*)(GP-0x2C46) == 0x5AA5` after complement) stored at `0xFEBE8BBA`
(GP `-0x2C46`). Uses an object pointer at GP `-0xB11` (`0xFEBEACEF`) and
complement at GP `-0xB0F` (`0xFEBEACF1`).

### E2E protection

Invokes three E2E (end-to-end) protection functions on the calibration data:
`FUN_0006f71c` (validate), `FUN_0006f6a6` (check), `FUN_0006f97a` (protect/
propagate). These guard the parameter block against corruption.

### Dispatch

On successful E2E validation (`iVar4 == 0` and marker re-check passes), calls
five handlers: `FUN_000577d0`, `FUN_000578de`, `FUN_00057980`, `FUN_00057a7e`,
`FUN_000fdd68`.

### Output effects

Performs parameter reconciliation: compares a current version (`GP-0xB12`) with
its complement (`GP-0xB0F`); on mismatch, copies the candidate (`GP+0xC33`)
and writes a new version via `thunk_FUN_000b0974`. On version change, calls
`FUN_0005db6e`/`FUN_000fdd40`/`FUN_0005e3c6` with the new parameters; otherwise
calls `FUN_0005e572`/`FUN_000fdd54`/`FUN_0005e886`.

Maintains a rolling byte counter at GP `-0x2C37` (`0xFEBE8BC9`) and writes a
derived state byte to GP `-0x2C35` (`0xFEBE8BCB`).

### Cross-rate interfaces

Produces calibrated parameters consumed by the motor-control and safety
subsystems. The E2E-protected parameter block is the cross-rate bridge between
configuration validity and runtime motor behavior.

### Evidence grade: bounded

The calibration marker, E2E validation chain, reconciliation logic, and handler
call set are recovered from decompilation. The specific parameter semantics are
not claimed.

## 7. Timer and PWM reload — `0x6547c`

### Input flags and state roots

No state flag gates this function; it runs unconditionally every foreground
cycle.

### Output effects — MMIO writes

Writes motor PWM/timer register blocks from calibration tables, with interrupts
disabled. The interrupt-disable wrapper is `FUN_0006f134(0xFFC0)` /
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
| `0x30FA0` | PWM period/reload for `0xFFE20004`/`0xFFE21004` |
| `0x30FA4` | PWM value for `0xFFE20004+8`/`0xFFE21004+8` |
| `0x30FA8` | PWM value for `+0x0C` |
| `0x30FAC` | PWM value for `+0x14` |
| `0x30F7C/84/8C/94` | Timer function pointers for `0xFFE50000` block |

### Cross-rate interfaces

This is a leaf cyclic: it reads calibration tables and writes MMIO. It does not
consume flags from other cyclics or produce RAM state for them. It establishes
the hardware timer period that governs the overall foreground tick rate.

### Evidence grade: recovered

The MMIO addresses, calibration table addresses, interrupt-disable wrapper, and
`-1` reload encoding are all directly recovered from the decompiled body. This
is the highest-confidence subsystem in the partition.

## 8. CAN 0x7F7 special receive callback — `0x7ff86`

### Structure

`application_can_special_rx_demux` at `0x7ff86` is a separate receive callback
class registered for acceptance rule 50 / standard CAN ID `0x7F7`. It is
distinct from both the 47-PDU normal demux (`0x80006`) and the diagnostic demux
(`0x80114`) documented in `docs/FIRMWARE_ARCHITECTURE.md` section 5.3.

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
`docs/APPLICATION_TRANSMIT_MAP.md`) is a separate endpoint and is not claimed to
be the response pair without further evidence.

## 9. Tx signal producer closure — signals 9, 37, 57

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

## 10. Evidence boundaries

Core conclusions — function addresses, call sequences, GP-relative flag
locations, MMIO register writes, calibration table references, packer signal
coverage, and the `0x7F7` dispatch structure — come from decompilation of the
committed Ghidra project.

The following are **not** claimed:

- OEM-level names for the motor-control states or diagnostic checks;
- The physical motor-control behavior of the individual sub-handlers;
- The specific parameter semantics managed by `0x57ac2`;
- The upper-protocol identity of CAN `0x7F7`;
- A response-pairing between `0x7F7` (RX) and `0x7F8` (TX);
- Runtime producers for signals 9, 37, and 57 beyond the packer exclusion.

See also:

- `docs/FIRMWARE_ARCHITECTURE.md` for the foreground cycle and interrupt map;
- `docs/APPLICATION_TRANSMIT_MAP.md` for the complete TX PDU and signal map;
- `docs/APPLICATION_RECEIVE_MAP.md` for the normal and diagnostic RX paths.
