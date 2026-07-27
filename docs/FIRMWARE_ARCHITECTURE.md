# Firmware Architecture

This document maps the broad control-flow architecture of the China-market Sienna EPS firmware `8965B4512000` for the RH850/P1M-E R7F701381. It covers the boot/application split, startup and handoff, foreground scheduling, interrupt routing, and the application-side CAN receive path.

The addresses below are CodeFlash virtual addresses. The independent raw-image checks are in `tests/verify_architecture.py`.

## 1. Executive summary

The 1 MiB CodeFlash is one dense image containing two execution domains:

| Domain/region | CodeFlash landmarks | Evidence |
|---|---|---|
| Boot/loader execution | reset/vector base `0x0`; handoff `0x13B0` | Hardware reset vector, boot GP/TP, boot UDS/flashing code, and the application handoff |
| Application execution | vector base `0x20000`; INTBP table `0x20200`; entry `0x20880` | Values installed into EBASE/INTBP and the entry selected by the boot pointer |
| Cross-region metadata/calibration | for example `0x181DC` and entry pointer `0xFFDB8` | Application code reads calibration below `0x20000`; boot code reads application metadata near the end of flash |

`0x20000` is therefore the verified **application vector/executable base**, not a strict ownership boundary for every constant. The low flash contains the boot execution image but also application-used calibration, while the final application-entry metadata is at `0xFFDB8`. These are logical domains inside the same split CodeFlash import, not separate firmware files. The application starts only after the boot checks at `0x13B0` succeed.

The high-level path is:

```text
hardware reset
  -> vector 0x00000000
  -> boot_reset_startup 0x1B0
  -> boot initialization / diagnostics / programming decision
  -> boot_application_handoff 0x13B0
  -> *(uint32_t *)0xFFDB8 = 0x20880
  -> application_entry 0x20880
  -> application_startup_coordinator 0x62758
  -> install application EBASE/INTBP/GP/TP/SP at 0x70524
  -> initialize modules
  -> enable EI interrupts
  -> application_foreground_cyclic_loop 0x64FCC
```

## 2. Boot startup and application handoff

### 2.1 Reset context

The reset vector begins with `syncp` and jumps to `0x1B0`. The startup code:

- disables interrupts;
- clears the general registers;
- sets boot `SP = 0xFEBE8000`;
- sets boot `GP = 0xFEBF9800` at `0x1F2`;
- sets boot `TP = 0x869C`, the address of the boot EIINT dispatch table;
- initializes system registers and boot hardware before reaching the loader logic.

The direct boot exception vectors occupy the low vector area. Most point to `0x1E1E`; offsets `0x20`, `0xB0`, and `0xD0` use `0x1E2A`; offset `0xE0` uses the fatal trap at `0x1E36`. The EIINT direct-vector prologue at `0x100` saves exception state and calls `boot_eiint_dispatch` at `0x748`.

### 2.2 Handoff gate

`boot_application_handoff` at `0x13B0` is the single gate between boot and
application execution. The four `jarl` call sites at `0x13B4`, `0x13B8`,
`0x13BC`, `0x13C0` encode a fixed setup order, and the validity-check `jarl`
is at `0x13C4` (these encodings are pinned in `tests/verify_boot_trust.py`).
The full decision tree is documented in
`docs/BOOT_VALIDITY_AND_FLASH_LIFECYCLE.md`; the summary below is the
statically verifiable structure.

#### Setup calls

The handoff invokes four setup functions before the validity check:

| Call site | Target | Role |
|---|---|---|
| `0x13B4` | `boot_peripheral_init` `0xC9A` | Initializes RSCFD CAN controller register windows (`0xFFC20000`/`0xFFC24000`/`0xFFC34000`) and CAN channel descriptors from the table at `0x87A0` |
| `0x13B8` | `boot_key_mirror_init` `0xE54` | Reads three DataFlash triple-copy values at `0xFFC0A000-A008`, checks XOR55/XORAA complements, and copies valid primaries into GP-relative mirrors at `0xFEBFFC00-C14` |
| `0x13BC` | `boot_flash_sequencer_init` `0xF80` | Configures flash sequencer protection registers (`0xFFD62000-28`) with enable key `0xA5`; sets blank/erase state for DataFlash banks at `0xFFD60000`/`0xFFD61000` |
| `0x13C0` | `boot_clock_init` `0x10C6` | Writes `0xFFF890C0=4`, polls `0xFFF890C8` for completion, then sets `0xFFF88818=0x50` (main PLL configuration) |

The peripheral, key-mirror, flash-sequencer, and clock roles are bounded to
the register windows they touch; the exact clock tree and CAN bit timing are
not fully decoded and are not claimed here.

#### Validity check (`0x119E`)

`boot_validity_check` at `0x119E` runs two retry-bounded phases, each with a
ceiling of three attempts (loop counter compared against `2`):

1. **Phase 1 — CRC descriptor verification.** Calls
   `memory_crc_verify_descriptors` for both CodeFlash regions (region 1 then
   region 0), then `boot_flash_status_check` at `0x115A`. It breaks only when
   both CRCs pass and the flash status is idle; otherwise it retries up to
   three times and returns `1` (failure) on exhaustion.
2. **Phase 2 — validity-marker comparison.** Calls
   `boot_validity_marker_check` at `0x6C5A` with `0xFFE00` (region 1) and
   `0x17E00` (region 0). It breaks only when both markers are present,
   otherwise retries up to three times and returns `1`.

The function returns `0` only when both phases pass. The flash status helper
at `0x115A` polls the flash sequencer command window at `0xFFD62034`, checks
error bits 0 and 2 of the status snapshot, issues the `0xA5` examine-code
sequence, and returns non-zero on error — a non-zero return forces the CRC
phase to retry.

#### Region table and markers

Three 28-byte region descriptors at `0x8E00` define the validity-checked
ranges:

| Region | Data range | Marker addr | Marker value |
|---|---|---|---|
| 0 (low CodeFlash) | `0x10000..0x17DFF` | `0x17E00` | `0x5AA5A55A` |
| 1 (high CodeFlash) | `0x18000..0xFFDFF` | `0xFFE00` | `0x5AA5A55A` |
| 2 (RAM payload) | `0xFEBF0000..0xFEBF0FFF` | `0` (null) | n/a |

Each CodeFlash region also has a CRC descriptor (base `0x8DD0`/`0x8DE0`)
recording data base, length, and embedded address/length fields. The
application vector base `0x20000` falls inside region 1 only, so the
application image is covered by the high-flash CRC and marker. Region 2 is
the authenticated RAM payload window managed by the payload gate
(`docs/PAYLOAD_GATE_ANALYSIS.md`); it has a null marker field and is not
marker-checked.

The validity marker value is `0x5AA5A55A`. `boot_validity_marker_check`
(`0x6C5A`) is a one-line predicate that returns true when the 32-bit value at
its parameter address is **not** equal to `0x5AA5A55A` — a true return means
the marker is invalid or erased. The literal is embedded at `0x6C60` inside
the predicate.

#### Success path

If the validity check returns `0`, the handoff reads the 32-bit entry pointer
at CodeFlash `0xFFDB8` (obtaining `0x00020880`) and calls it indirectly at
`0x13FE`. The application then runs as described in section 2.3.

#### Failure path

If the validity check returns non-zero, the handoff calls
`boot_failure_trap` at `0x1206`, which zeroes diagnostic state at
`0xFFFEE980-988`, then enters `boot_failure_main_loop` at `0x1398` — a
non-returning loop. The loop body `boot_failure_periodic` at `0x137A` sets
state `0xFEBF2904=2` and runs `flash_operation_task` (`0x4428`), bootloader
operation release, and `memory_crc_verify_task`. Keeping these tasks alive
allows a diagnostic re-flash session (UDS `0x34`/`0x37`, RID `0x10F2`) to
program a new image. The handoff function itself ends in an unconditional
`do { } while(true)`, so neither path can return to its caller.

#### Marker programming

The validity markers are written by `program_region_validity_marker` at
`0x5286`, reached via UDS RID `0x10F2`. The write path embeds the
`0x5AA5A55A` immediate at `0x5286` (verified in
`tests/verify_bootloader_diagnostics.py` and `tests/verify_boot_trust.py`).
After a successful re-flash, the next reset re-runs the validity gate, which
succeeds if both CRCs verify and both markers are present.

#### Static-analysis scope

Both marker domains (`0x17E00` and `0xFFE00`) currently hold `0x5AA5A55A` in
this committed calibration, so this is a static analysis of a **valid image**.
The decision tree above describes what the firmware checks at runtime; it does
not exercise the failure path against a tampered image. The full flash
lifecycle and the bounded object-15 negative are documented in
`docs/BOOT_VALIDITY_AND_FLASH_LIFECYCLE.md`.

### 2.3 Application CPU context

`application_entry` at `0x20880` calls `application_startup_coordinator` at `0x62758`. Its first call, `application_cpu_context_init` at `0x70524`, installs the application execution context directly in assembly:

| Register | Application value | Meaning |
|---|---:|---|
| `INTBP` | `0x00020200` | EIINT channel pointer table |
| `EBASE` | `0x00020000` | Direct exception-vector base |
| `GP` | `0xFEBEB800` | Application global-pointer base |
| `TP` | `0x00023EE4` | Application text/configuration base |
| `SP` | `0xFEBE2000` | Application stack pointer |

The startup coordinator then invokes a long ordered set of generated initialization functions, enables EI interrupts, and calls the non-returning foreground loop at `0x64FCC`.

## 3. Application startup and task map

The firmware uses a generated, cooperative foreground scheduler plus interrupt handlers. It is not an RTOS task table with independently scheduled stacks.

### 3.1 Foreground tick

The loop at `0x64FCC` polls bit 12 of the 16-bit interrupt-control register at `0xFFFFB110`. That address is `EIC136`; bit 12 is `EIRF136`. RH850/P1M-E interrupt channel 136 is `INTTAUJ0I3`, the TAUJ0 channel-3 interrupt.

The loop waits for `EIRF136`, clears it in software, and executes one foreground cycle. Channel 136 remains mapped to the default pointer-table handler because the firmware consumes this timer event by polling rather than by an ISR.

This establishes the tick **source**. The exact foreground-tick period remains `unsupported`: the TAUJ0 prescaler and reload (TDR) registers are not referenced via 32-bit absolute addresses in CodeFlash (the setup likely uses register-indirect or 16-bit-displacement addressing the decompiler does not resolve), and the RH850/P1M-E datasheet (`REFERENCE/r01ds0505ed0100-rh850p1m-e.pdf`) is a 72-page brief that documents TAUJ0 pin assignments and AC timing but not the register-level layout. The **PLL CPU clock is proven at 160 MHz** (16 MHz main oscillator × 10; REFERENCE PDF Sec 1.3 Table 1.1, Sec 3.4, Sec 3.6), but converting that to a TAUJ0 CH3 tick still requires the prescaler+TDR. All timing in `data/scheduler_periods.csv` is therefore expressed in foreground ticks, with microsecond periods marked `unsupported`. This is documented in `tests/verify_scheduler_timing.py`.

### 3.2 Foreground cycle

One cycle calls the following major groups in order:

| Order | Address | Role supported by current evidence |
|---:|---:|---|
| 1 | `0x643AC` | Cycle/overrun and safety bookkeeping |
| 2 | `0x702E8` | Enter generated protected/timing wrapper |
| 3 | `0x65F5C` | NvM/CSM asynchronous service group; reaches `csm_mainfunction` at `0x730D4` |
| 4 | `0x70308` | Exit generated protected/timing wrapper |
| 5 | `0x65750` | Main application component group; calls six large subsystem cyclic functions including the COM dispatch chain |

Order 5 expands as:

```
0x65750 → 0x57AC2 (E2E config-management cyclic)
  ├→ autosar_os_task_signal_dispatch (0x58404) — generated Os task body,
  │   352 sequential signal-processing calls, zero forward conditional branches.
  │   Called both here and at boot via 0x65626 → 0x57768 → 0x57778.
  ├→ autosar_com_rx_dispatch_group_a (0x5DB6E) — 269 COM signal unpackers.
  └→ rte_input_staging_copy_a/b (0x5C666/0x5C0B6) — AUTOSAR RTE input staging.

Separately, TAUJ0 CH2 ISR path:
  0x64F90 → 0x65720 → 0x579B4
    ├→ autosar_com_rx_dispatch_group_b (0x5D3CE) — 146 COM signal unpackers.
    └→ rte_input_staging_copy_c (0x5B9C4) — RTE input staging.
```

The `autosar_os_task_signal_dispatch` at `0x58404` (12,894 bytes) is the
largest function in the image. Full disassembly confirms it is a flat
sequential call sequence: 352 unique `jarl` calls, zero forward conditional
branches, zero `switch`. It is a generated Os task body that calls each
configured signal-processing runnable in declaration order. 241 of its 352
callees are 2-byte empty stubs. It is NOT the foreground loop itself — it is
a callee reached from the periodic dispatcher `0x57778`, which also calls
`eps_subsystem_init_orchestrator` (0xBD10E, boot only) and a RAM snapshot
copy (0x5B662).
| 6 | `0x702E8` | Enter the second protected/timing wrapper |
| 7 | `0x65C60` | `secoc_nvm_cyclic_task`; services the corrected SecOC-related NvM object lifecycle |
| 8 | `0x70308` | Exit wrapper |
| 9 | `0x64080` | Optional instrumentation/safety tail when the runtime marker is enabled |

The increment at the end of the loop updates a cycle counter at application `GP - 0x7E25`.

### 3.3 Interrupt-driven periodic groups

TAUJ0 channels 0, 1, and 2 are handled through the application pointer table:

| EIINT | ISR | Body | Observation |
|---:|---:|---:|---|
| 133 | `0x70320` | `0x64F18` | Generated context wrapper, periodic body, event counter increment |
| 134 | `0x703CA` | `0x64F54` | Generated context wrapper, periodic body, event counter increment |
| 135 | `0x70476` | `0x64F90` | Generated context wrapper, periodic body, event counter increment |
| 136 | default entry | polled at `0x64FCC` | Foreground-cycle trigger; `EIRF136` is cleared by the loop |

This gives four timer-driven execution lanes, but it does not by itself prove their periods or AUTOSAR runnable names.

## 4. Interrupt architecture

### 4.1 Boot interrupt dispatch

The boot environment uses the common direct EIINT prologue at `0x100`. It passes the exception source code to `boot_eiint_dispatch` at `0x748`, which linearly searches eight-byte records at `0x869C`:

| EIIC code | EIINT | Hardware source | Wrapper |
|---:|---:|---|---:|
| `0x1087` | 135 | TAUJ0 channel 2 | `0x1E44` |
| `0x10B8` | 184 | RSCAN CAN0 receive | `0x1E50` |
| `0x10B9` | 185 | RSCAN CAN0 transmit | `0x1E5E` |
| `0x10BB` | 187 | RSCAN CAN1 receive | `0x1E6C` |
| `0x10BC` | 188 | RSCAN CAN1 transmit | `0x1E7A` |
| `0x10C0` | 192 | RSCAN CAN2 receive | `0x1E88` |
| `0x10C1` | 193 | RSCAN CAN2 transmit | `0x1E96` |
| `0xFFFFFFFF` | default | no match | `0x1EA4` fatal trap |

The table describes supported wrappers. It does not prove that every CAN channel is enabled in every boot mode.

### 4.2 Application direct vectors

The application installs `EBASE = 0x20000`. Most direct exception slots jump to the default handler at `0x61D88`. Direct-vector offset `0x90` instead jumps to `0x64B3E`, which saves fault context, records a fault, and enters recovery/reset handling. The region `0x20100..0x201FF` consists of `syncp; eiret` stubs.

### 4.3 Application EIINT pointer table

`INTBP = 0x20200`. The `0x600`-byte region through `0x207FF` contains 384 little-endian entries. Its raw distribution is:

- `0x61D88`: 373 entries;
- nine explicit CodeFlash handlers listed below;
- `0x00400040`: final entries 382 and 383.

The last value is outside the mapped CodeFlash image and remains unresolved. Channel 382 is reserved in the hardware manual and channel 383 is the flash sequencer-end error interrupt. Do not silently reinterpret `0x00400040` as a normal CodeFlash function.

| EIINT | Hardware-manual source | Pointer | Firmware behavior |
|---:|---|---:|---|
| 8 | Maskable Error Control Module (`INTECM`) | `0x70A54` | ECM status/recovery and hard-reset path |
| 133 | TAUJ0 CH0 | `0x70320` | Generated wrapper -> `0x64F18` |
| 134 | TAUJ0 CH1 | `0x703CA` | Generated wrapper -> `0x64F54` |
| 135 | TAUJ0 CH2 | `0x70476` | Generated wrapper -> `0x64F90` |
| 187 | RSCAN CAN1 receive | `0x6506A` | Context wrapper -> CAN1 RX body `0x82E40` |
| 188 | RSCAN CAN1 transmit | `0x65028` | Context wrapper -> CAN1 TX confirmation body `0x8474E` |
| 292 | Reserved in generic P1M-E table | `0x650AC` | ICU-S crypto-driver callback interrupt path via `0x87610` |
| 293 | Reserved in generic P1M-E table | `0x650EE` | ICU-S crypto-driver callback interrupt path via `0x87636` |
| 379 | Flash sequencer end | `0x65130` | Flash service completion path via `0x78286` |

The generic hardware table's `Reserved` label does not make these vectors dead.
Both wrappers are installed and dispatch through the same callback pointer and
bitwise-complement guard at GP `+0x5994/+0x5998`; a failed guard sets driver error
byte GP `+0x5991`. Driver initialization at `0x8735E` initializes those exact
fields and calls `0x8913C`, which masks/unmasks EIC registers `0xFFFFB248` and
`0xFFFFB24A`—the channel-292/293 control words. The same driver family accesses
the ICU-S command/status register bank at `0xFFC5D000` used by the verified CMAC
path. Thus **firmware role** (ICU-S crypto completion/error callbacks) is
definitive even though the generic manual does not publish peripheral names for
these channel numbers. The two adapters are byte-identical and static analysis
does not distinguish which one is completion versus error.

## 5. Application CAN-routing overview

### 5.1 Physical channel and interrupt path

The application RSCFD register-address map starts at `0x22FE0` and contains three `0x74`-byte channel records. The active application vector wrappers are for RSCAN **CAN1**:

```text
EIINT 187 / CAN1 RX
  0x6506A application_can1_rx_isr
  -> 0x6577C adapter
  -> 0x82E40 application_can1_rx_interrupt_body
  -> 0x82E02 RSCFD channel-1 dispatch
  -> 0x82C50 / 0x82D1C read queued hardware frames
  -> 0x82C24 map hardware label
  -> 0x7FA56 application_can_rx_queue_ingress
  -> foreground receive queue
  -> normal, diagnostic, or special receive demultiplexer
  -> 0x80C44 configuration-driven upper PDU router

EIINT 188 / CAN1 TX
  0x65028 application_can1_tx_isr
  -> 0x65770 adapter
  -> 0x8474E application_can1_tx_interrupt_body
  -> 0x84710 RSCFD channel-1 confirmation dispatch
```

The ISR copies frames into software queues. Higher-layer PDU dispatch occurs through generated routing tables rather than by a direct switch on CAN ID inside the ISR.

### 5.2 Hardware acceptance rules

The application acceptance-rule table starts at `0x231A0`. It contains 51 sixteen-byte rules followed by a `0xFFFFFFFF` terminator:

- rules 0..46 mirror the 47 normal receive descriptors at `0x22018`;
- rules 47..50 are standard IDs `0x7A1`, `0x777`, `0x7A0`, and `0x7F7`.

The 47 normal standard IDs are:

```text
2E4 3B0 63B 624 63D 00F 013 014 015 016 017 018 019 01A 01B 01C
01D 01E 01F 191 131 2FD 0D0 3BF 127 115 1C5 294 51E 132 611 2D1
675 2E8 025 423 0AA 101 0D5 13B 090 0D7 64F 020 403 490 1DA
```

Most descriptors request eight-byte frames. Three entries carry the software CAN-FD marker (`0x40000025`, `0x40000090`, and `0x400000D7`) with 32-byte lengths; their hardware-rule ID fields contain the underlying 11-bit standard IDs. IDs `0x423` and `0x490` use length 1.

The normal demultiplexer at `0x80006` maps acceptance-rule index `n` to application PDU ID `6+n`. Therefore:

| CAN ID | Acceptance index | Application PDU ID | Static conclusion |
|---:|---:|---:|---|
| `0x2E4` | 0 | 6 | Explicit application RX route |
| `0x0F` | 5 | 11 | Explicit application RX route; synchronization traffic in external captures |
| `0x131` | 20 | 26 | Explicit application RX route |

The externally discussed `0x344` does **not** appear in this application's RSCAN receive acceptance list. That does not disprove its appearance in vehicle captures or its use by another transmitter; it means only that this firmware image does not statically accept `0x344` through this CAN1 RX rule table. The four-ID CAN-oracle interpretation must not be projected onto the RX configuration without this distinction.

### 5.3 Diagnostic receive classes

The acceptance tail uses three callback classes:

- `0x7A1`, `0x777`, and `0x7A0` go through `application_can_diagnostic_rx_demux` at `0x80114`;
- `0x7F7` goes through the separate callback class at `0x7FF86`;
- the 47 normal IDs go through `application_can_normal_rx_demux` at `0x80006`.

This is the application configuration, distinct from the bootloader's already-documented physical `0x7A1`, functional `0x777`, and response `0x7A9` transport route.

### 5.4 Application transmit map

`APPLICATION_TRANSMIT_MAP.md` completes the application transmit side. It proves 11 active CanIf routes, including six COM I-PDUs on CAN IDs `0x260`, `0x262`, `0x351`, `0x394`, `0x4A3`, and `0x4C8`. Those six I-PDUs contain 58 generated COM signal IDs with exact wire fields, RAM sources where statically recoverable, cyclic counts, and the channel-1 confirmation path. Unsupported OEM field names and three configured signals without recovered runtime producers remain explicitly unresolved.

## 6. Evidence boundaries

The following are checked directly from the committed CodeFlash image:

- partition landmarks and application entry pointer;
- startup register constants;
- boot EIINT dispatch records;
- application 384-entry pointer table and handler distribution;
- RSCFD acceptance rules and normal receive descriptors;
- the specific `0x2E4`, `0x0F`, and `0x131` receive indexes;
- absence of `0x344` from the receive-rule IDs.

Peripheral names and EIINT-channel identities use Renesas **RH850/P1M-E User's Manual: Hardware**, R01UH0585EJ0120 Rev.1.20 (March 23, 2018). The firmware bytes establish the channel numbers; the hardware manual supplies the peripheral names.

See also:

- `docs/CAN_TRANSPORT_ANALYSIS.md` for the bootloader CAN/ISO-TP path;
- `docs/APPLICATION_TRANSMIT_MAP.md` for the complete application Tx-PDU/CAN-ID/COM-signal map;
- `docs/APPLICATION_RECEIVE_MAP.md` for the complete application Rx-PDU/CAN-ID/COM-signal map;
- `docs/SECOC_RUNTIME_KEY_LIFECYCLE.md` for the corrected SecOC-related NvM object model;
- `docs/APPLICATION_DIAGNOSTICS.md` for application/boot diagnostic distinctions;

## 7. Boot shutdown/reset path

`boot_shutdown_reset_path` at `0x7059E` (1200 bytes) is a non-returning
reset/shutdown sequence reached from `application_ecm_maskable_isr`. It checks
the boot-state marker at `FEBF3401`, writes watchdog/reset registers, and
calls `system_hard_reset`. 18 SFR references.

## 8. Application peripheral initialization

`application_peripheral_init` at `0x61DD4` (1096 bytes) is called by
`application_startup_coordinator`. It writes 233 hardware registers (SFRs)
to configure clock, timer, ADC, port, and communication peripherals, including
port configuration bytes (0xCF) to multiple `FFFEEAxx` registers.

## 9. Large unnamed function reference

The 24 largest functions (≥1024 bytes) that were initially `FUN_*` are now
fully classified and labeled. Their findings are distributed across domain
docs rather than duplicated here:

| Domain | Functions | Documented in |
|---|---|---|
| Application AES primitives | `0x853EE`, `0x8496C` | This doc §2.3 and `APPLICATION_SECURITY_ACCESS.md` |
| Generated Os/RTE/COM | `0x58404`, `0x5DB6E`, `0x5D3CE` | This doc §3.2 and `APPLICATION_RECEIVE_MAP.md` |
| COM deadline monitors | `0x69824`, `0x6AD24`, `0x69DEC`, `0x6A28A` | `APPLICATION_RECEIVE_MAP.md` |
| RTE staging copies | `0x5C666`, `0x5C0B6`, `0x5B9C4` | `APPLICATION_RECEIVE_MAP.md` |
| Boot/shutdown/init | `0xBD10E`, `0x57BFE`, `0x61DD4`, `0x7059E` | This doc §7-8 and `SYSTEM_MODE_CLUSTER_ANALYSIS.md` |
| Motor control (OEM) | `0x47C3C`, `0x32B80`, `0xB98BC` | `APPLICATION_RECEIVE_MAP.md` (calibration handlers) |
| System mode | `0xBA43A`, `0xBEC4C`, `0xCBCC8` | `SYSTEM_MODE_CLUSTER_ANALYSIS.md` |
| Hardware | `0x1F2`, `0x48312` | This doc §2 and `APPLICATION_RECEIVE_MAP.md` |
- `docs/DATAFLASH_LAYOUT.md` for persistent storage architecture.
