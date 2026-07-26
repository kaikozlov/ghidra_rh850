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

`boot_application_handoff` at `0x13B0` runs four setup/check functions and evaluates the result from `0x119E`. If the result is zero, it:

1. reads the 32-bit pointer at CodeFlash `0xFFDB8`;
2. obtains `0x00020880`;
3. calls that address indirectly at `0x13FE`.

If the check fails, it follows a boot failure path and never enters the application. The application entry pointer is therefore executable handoff metadata, not merely an incidental reference near the end of flash.

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

This establishes the tick **source**. The exact time period should not be claimed until the TAUJ0 clock and reload configuration are fully decoded.

### 3.2 Foreground cycle

One cycle calls the following major groups in order:

| Order | Address | Role supported by current evidence |
|---:|---:|---|
| 1 | `0x643AC` | Cycle/overrun and safety bookkeeping |
| 2 | `0x702E8` | Enter generated protected/timing wrapper |
| 3 | `0x65F5C` | NvM/CSM asynchronous service group; reaches `csm_mainfunction` at `0x730D4` |
| 4 | `0x70308` | Exit generated protected/timing wrapper |
| 5 | `0x65750` | Main application component group; calls six large subsystem cyclic functions |
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
| 292 | Reserved | `0x650AC` | Wrapper invokes callback adapter `0x87610`; source semantics unresolved |
| 293 | Reserved | `0x650EE` | Wrapper invokes callback adapter `0x87636`; source semantics unresolved |
| 379 | Flash sequencer end | `0x65130` | Flash service completion path via `0x78286` |

The discrepancy at reserved channels 292/293 is preserved rather than assigned a guessed peripheral name. It may reflect a generated cross-variant vector layout.

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
- `docs/SECOC_RUNTIME_KEY_LIFECYCLE.md` for the corrected SecOC-related NvM object model;
- `docs/APPLICATION_DIAGNOSTICS.md` for application/boot diagnostic distinctions;
- `docs/DATAFLASH_LAYOUT.md` for persistent storage architecture.
