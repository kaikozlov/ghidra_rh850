# Large unnamed functions (≥1024 bytes) — classification and evidence

This report documents the 24 largest functions that remained `FUN_*` after the
initial annotation pass. Each was decompiled, its call graph traced to known
entry points, and its internal structure analyzed (control flow, memory access
patterns, computation vs. data movement) to produce a confident classification.

The analysis corrects several initial heuristic misclassifications. All
findings below are verified against the actual decompiled code, not from
pattern matching.

`AnnotateLargeFunctions.java` applies the corrected names and comments to the
project. The old heuristic names are listed alongside the corrected ones.

## Executive result

| Category | Count | Description |
|---|---:|---|
| Already documented, now labeled | 3 | Known from prior analysis but unnamed in the project |
| Generated AUTOSAR Os/RTE/COM | 10 | Compiler-generated task bodies, dispatch tables, staging copies |
| Boot-time initialization | 3 | One-shot init orchestrators and RAM default-value setters |
| Hand-written OEM motor control | 3 | Real fixed-point math, only run on calibration version change |
| System mode coordination | 3 | Mode-transition dispatchers, telemetry, substate machine |
| Hardware / misc | 2 | Peripheral init, register access helper |

None of the 24 functions are security-relevant. They are all in the EPS motor
control, CAN signal processing, or system-mode domains. The security surface
(diagnostic stack, crypto, transport, boot trust, payload gate, SecOC,
DataFlash) is fully traced by the existing named functions.

## Call-graph architecture (proven)

The two periodic execution paths that invoke most of these functions:

```
application_startup_coordinator (0x62758)
  └→ FUN_00065626 (one-time COM/RTE init)
       └→ registers periodic dispatch callbacks
       └→ 0x57768 → 0x5778C → 0x57778
            ├→ autosar_os_task_signal_dispatch (0x58404) [367 callees]
            ├→ eps_subsystem_init_orchestrator (0xBD10E) [boot only]
            └→ FUN_0005B662 (RAM snapshot copy)

foreground_cyclic_loop (0x64FCC) [TAUJ0 CH3, EIRF EIC136]
  ├→ FUN_00065750 → 0x57AC2 →[CRC gate]→ autosar_com_rx_dispatch_group_a (0x5DB6E)
  └→ secoc_nvm_cyclic_task

TAUJ0 CH2 interrupt (0x64FB0 → 0x65720)
  └→ autosar_com_rx_dispatch_group_b (0x5D3CE)

TAUJ0 CH0 interrupt (0x64F18 → 0x656F0) [fast motor loop]
  └→ motor calibration-change handlers (0x47C3C, 0x32B80)
```

## 1. Already documented, now labeled

### `boot_reset_startup` (0x1F2, 1360 B)

Hardware reset entry point. Sets `gp=0xFEBF9800`, `tp=0x869C` (boot EIINT
table), `sp=0xFEBE8000`. The "unreachable block" warnings are intentional:
RAM-init code at `0x44C`/`0x460`/`0x670` is only reachable from the power-on
path.

### `app_aes128_ecb_decrypt_block` (0x853EE, 4582 B)

Application AES-128 single-block decrypt. Uses Td tables at `0x24628` and
inverse S-box at `0x25628`. Called only by app SA stage-1 (`0x8C7BC`). The
application has its own copy of the AES primitives at `0x84xxx`, separate
from the bootloader's at `0x73xx-0x76xx`.

### `app_aes128_encrypt_round` (0x8496C, 2372 B)

Application AES-128 encrypt round function. Uses Te tables at `0x23628` and
forward S-box at `0x8FF1`. Called only by app SA stage-2 wrapper (`0x852B0`).

## 2. Generated AUTOSAR Os/RTE/COM (10 functions)

### `autosar_os_task_signal_dispatch` (0x58404, 12894 B)

**Old heuristic name:** `foreground_cyclic_signal_dispatch`

The largest function in the image. Structure verified by full disassembly:
- 352 `jarl` call instructions, all to distinct targets
- 139 conditional branches, **all backward** (buffer-zeroing loops)
- **Zero forward conditional branches** — no if/else, no switch, no goto
- 241 of 352 callees are 2-byte empty stubs (`jmp lp`)

It is a flat, linear, compiler-generated sequence of signal-processing calls
executed in fixed declaration order every foreground cycle. Called from
`0x57778`, which is reached both at startup and cyclically. It is NOT the
foreground loop itself.

### `autosar_com_rx_dispatch_group_a` / `_b` (0x5DB6E, 0x5D3CE)

**Old heuristic names:** `can_signal_unpack_dispatch_1` / `_2`

Generated COM receive dispatch groups. Group A (2136 B) calls 269 unique
sub-functions including `application_unpack_can_2e4`. Group B (1078 B) calls
146. Both are flat call sequences that unpack CAN signals from PDU groups and
route them to consumers.

### COM signal deadline monitors (0x69824, 0x6AD24, 0x69DEC, 0x6A28A)

**Old heuristic names:** `can_signal_consumer_handler` / `_worker` / etc. — **all wrong.**

These are AUTOSAR COM signal deadline/timeout monitors. They manage signal
lifecycle states through function-pointer tables:

| State | Meaning |
|---|---|
| `0x00` | init |
| `0x11` | signal received / alive |
| `0x22` | timeout / deadline expired |
| `0x33`/`0x44` | marked / replaced |

Each dispatches through a 15-slot function-pointer table
(`param_3[0]`..`param_3[0xe]`), which is why Ghidra's type propagation does
not settle. The four variants differ in signal class and callback count
(28–33 indirect calls each).

### RTE input staging copies (0x5C666, 0x5C0B6, 0x5B9C4)

**Old heuristic names:** `motor_torque_processor` / `motor_assist_processor` /
`motor_signal_processor` — **all wrong.**

Pure data-movement functions. Zero `if` statements, zero calls, zero
computation. Field-by-field struct copies from scattered Rte buffers into
contiguous runnable-local input structs. Called inside critical sections
(interrupt masks `0xFF00`/`0xFFC0`).

| Function | Size | Field copies | Destination |
|---|---:|---:|---|
| `rte_input_staging_copy_a` (0x5C666) | 1442 B | 220 | 0xFEBE6400–0xFEBE676F |
| `rte_input_staging_copy_b` (0x5C0B6) | 1204 B | 189 | 0xFEBE6400–0xFEBE6600 |
| `rte_input_staging_copy_c` (0x5B9C4) | 1250 B | 192 | 0xFEBE6200–0xFEBE6400 |

## 3. Boot-time initialization (3 functions)

### `eps_subsystem_init_orchestrator` (0xBD10E, 5404 B)

**Old heuristic name:** `motor_control_init_cycle` — **wrong.**

Boot-time one-shot init. Zero `if` statements, zero `switch`, 101 sequential
init-helper calls and 1773 RAM assignments. Likely AUTOSAR EcuM/BswM
InitRunnable or hand-written `Eps_Init()`.

### `application_ram_default_init` (0x57BFE, 2054 B)

**Old heuristic name:** `motor_control_state_machine` — **wrong.**

Boot-time one-shot. Zero `if` statements, zero calls. Pure assignment block
initializing 588 RAM locations (`0xFEBE6E50–0xFEBE8130`) with defaults.

### `application_peripheral_init` (0x61DD4, 1096 B)

Writes 233 SFRs to configure clock, timer, ADC, port, and communication
peripherals. Called by `application_startup_coordinator`.

## 4. Hand-written OEM motor control (3 functions)

These are the only functions in the set that contain real computation
(fixed-point math, saturations, calibration lookups). They are
**calibration-version-change handlers** — they only execute when the
E2E-protected calibration block version transitions, not every motor tick.
The actual per-tick fast-loop motor control lives in sibling callees of
`FUN_000656F0` and `FUN_00065720`.

### `motor_phase_conditioning_calib_handler` (0x47C3C, 1632 B)

**Old heuristic name:** `motor_control_helper` — partially correct domain, wrong role.

3-phase (u/v/w) signal conditioning with per-phase gain multiplication.
Verified: 60 `longlong` multiplies, 103 saturation checks (`0x7FFF`/`-0x7FFF`),
91 conditional branches. Calibration block at CodeFlash `0x1875x`. Runs from
TAUJ0 CH0 ISR on calibration version change.

### `motor_coord_transform_calib_handler` (0x32B80, 1560 B)

**Old heuristic name:** `motor_output_processor` — wrong role.

6-channel fixed-point matrix math with d/q axis decomposition pattern, Q15
rescale (`/ 0x8000`), low-pass filter. Calibration block at `0x3103x`.
Likely Park/Clarke transform + current-loop filter recomputation. Runs from
TAUJ0 CH0 ISR on calibration version change.

### `motor_rotor_observer_calib_handler` (0xB98BC, 1040 B)

**Old heuristic name:** `calibration_lookup_dispatch` — partially correct.

Rotor position/speed observer. ~20 calibration values from CodeFlash
`0x1A12x–0x1A15x` (thresholds, gains, filter coefficients, limits). Calls
atan2/sqrt (`0xCCCAx`), abs/clip (`0xCBABA`), interpolation (`0xCC638`), and
DTC setters. Runs from TAUJ0 CH2 ISR on calibration version change.

## 5. System mode coordination (3 functions)

### `system_mode_per_tick_dispatcher` (0xBEC4C, 1330 B)

**Old heuristic name:** `system_mode_transition_step`

Full per-tick subsystem dispatcher. Knows old+new mode and runs band-entry
init. Calls `application_input_snapshot_update`,
`application_system_transition_phase_step`, and tail-calls
`system_mode_coordinator`. Wiring only — does not decide transitions.

### `system_mode_telemetry_snapshot` (0xBA43A, 2732 B)

**Old heuristic name:** `system_mode_state_worker`

~200-field telemetry snapshot copier with one mode-0x400 conditional. Does
not decide mode transitions.

### `application_substate_machine` (0xCBCC8, 1182 B)

**Old heuristic name:** `application_state_machine_worker`

Table-driven substate machine using transition codes `0x11`/`0x22`/`0x33`/
`0x44`, independent of the system-mode enum. Reached only when dispatcher
flag bit `0x10` is set.

### System mode context

The actual mode state machine is `system_mode_coordinator` at `0xB0518`
(already named). It processes nine modes:

| Mode | Role |
|---|---|
| `0x100` | init |
| `0x200` | pre-operational |
| `0x300` | operational band A |
| `0x400` | operational band B |
| `0x500` | operational band C |
| `0x600` | transitional |
| `0x700` | pre-shutdown |
| `0x800` | reset sequencing |
| `0x900` | programming shutdown |

Event 9 (set by `application_programming_reset_request @ 0x4C98C`) is checked
in every operational mode and always targets `0x900`. Mode `0x900` entry
callback (`0xB20EA`) writes shutdown requests `0x70017001` and `0x00020002`.

## 6. Hardware / misc (2 functions)

### `boot_shutdown_reset_path` (0x7059E, 1200 B)

**Old heuristic name:** `boot_failure_shutdown_reset`

Non-returning reset/shutdown path. 18 SFR references. Calls
`system_hard_reset`.

### `hardware_register_access_helper` (0x48312, 2044 B)

12 SFR references. Called by CAN signal processing chain.

## Evidence grades

| Finding | Grade |
|---|---|
| 0x58404 is a flat generated dispatch (0 forward branches) | **Definitive** (full disassembly) |
| 0x69824 family are COM deadline monitors | **Definitive** (lifecycle states, FP table) |
| 0x5C666/0x5C0B6/0x5B9C4 are RTE staging copies | **Definitive** (0 ifs, pure field copies) |
| 0xBD10E is an init orchestrator | **Definitive** (0 ifs, 101 sequential calls) |
| 0x47C3C/0x32B80/0xB98BC are calib-change handlers | **Strong** (call-graph context + math content) |
| 0x47C3C is 3-phase conditioning | **Strong** (u/v/w pattern, gain selection) |
| 0x32B80 is Park/Clarke transform | **Inference** (d/q pattern, Q15 rescale) |
| 0xB98BC is rotor position observer | **Inference** (atan2/sqrt, observer state output) |
| Calibration blocks at 0x1875x/0x3103x/0x1A12x | **Definitive** (CodeFlash data refs verified) |
