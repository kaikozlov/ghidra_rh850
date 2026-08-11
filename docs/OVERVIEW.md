# Firmware overview

Ten-minute orientation to the China-market Sienna EPS firmware
(`8965B4512000`, RH850/P1M-E R7F701381). Everything here is expanded in the
linked subsystem reports.

## What this firmware is

A single `0x108000`-byte dump containing the MCU's two flash regions:

| File range | Size | Virtual range | Region |
|---|---:|---|---|
| `0x000000–0x007fff` | 32 KiB | `0xFF200000–0xFF207FFF` | DataFlash |
| `0x008000–0x107fff` | 1 MiB | `0x00000000–0x000FFFFF` | CodeFlash |

CodeFlash VA = file offset − `0x8000`. The original flat import was invalid;
details and evidence are in the root `README.md` and
[storage/dataflash.md](storage/dataflash.md).

The image contains a **bootloader** (low CodeFlash) and an **application**
(base `0x20000`, entry `0x20880`). The bootloader handles reprogramming; the
application runs the EPS.

## Boot and trust

`boot_application_handoff` (`0x13B0`) runs `boot_validity_check` (`0x119E`):
CRC verification of two CodeFlash regions plus a validity-marker comparison
(`0x5AA5A55A`). Failure drops into a non-returning diagnostic-reflash loop.
See [architecture/boot-validity-and-flash-lifecycle.md](architecture/boot-validity-and-flash-lifecycle.md).

## Diagnostics

Two independent UDS stacks:

- **Bootloader** — physical `0x7A1` / functional `0x777`. Four-DID table
  (`F181` placeholder only), strict `0203→0201→0202` write sequence, payload
  download via RequestDownload/TransferData/TransferExit. See
  [diagnostics/bootloader.md](diagnostics/bootloader.md) and
  [diagnostics/bootloader-dids.md](diagnostics/bootloader-dids.md).
- **Application** — 17 services (`10/11/14/19/22/23/27/28/2E/31/34/36/37/3E/85/AB/BA`),
  242 readable DIDs, 19 writable DIDs, real `F181`/`F186`/`F18C`. Programming
  handoff is gated on session, vehicle speed, supply voltage, and a
  system-transition phase snapshot. See
  [diagnostics/application.md](diagnostics/application.md).

## Security

Three independent domains — do not conflate them:

- **Bootloader SecurityAccess** — AES-128-ECB two-stage construction
  (`expected = AES-ENC(AES-DEC(SEED_KEY_SECRET, data_record), ecu_seed)`).
  Secrets `SEED_KEY_SECRET` (`0xBFE8`) and `PAYLOAD_BUILD_SECRET` (`0xBFD8`)
  recovered. The full payload gate is in
  [security/bootloader-payload-gate.md](security/bootloader-payload-gate.md).
- **Application SecurityAccess** — only level 2 (`03/04`) is functional; level
  1 is a compiled stub. Same AES construction shape, different secret
  (`0x20840`) and handlers. See
  [security/application-security-access.md](security/application-security-access.md).
- **SecOC** — runtime CAN authentication on six RX PDUs through ICU-S slot 4.
  The apparent `FF*16` KAT is compiled out and does not reveal the live key.
  Command 5 is recovered as the paired MAC-generation primitive and accepts
  selector 4 in software. Its sole configured stock caller is a dormant CAN-fed
  test harness whose activator is now a whole-image bounded static negative; the
  stock graph still has no production SecOC transmit path. Classic sender
  construction and freshness are resolved, and Stage 7 specifies a minimum
  foreground application-context signing proxy through the serialized ICU
  driver. Remaining questions are dynamic: live slot-4 command-5 permission,
  latency/jitter/contention, and bench validation. See
  [security/secoc/README.md](security/secoc/README.md) and
  [security/secoc/sender-implementation.md](security/secoc/sender-implementation.md).

## Communications

CAN1: 47 normal Rx I-PDUs + diagnostic IDs, 11 active Tx routes. SecOC
envelopes stay inside the normal Rx set. See
[communications/README.md](communications/README.md).

## Storage

32 KiB DataFlash: 122 physical NvM records in pages 256–479 (48-record
triplicate bank + 74-record checkpoint ring), pages 432–479 are the 16-object
SecOC triplicate bank, pages 0–255 unallocated with undefined erased readback.
See [storage/dataflash.md](storage/dataflash.md).

## Execution architecture

Application foreground loop at `0x64FCC` polls TAUJ0 CH3; EIINT table at
`0x20200`; 6,037 structurally discovered functions, of which 5,928 remain
unreviewed and only 21 currently carry a semantic evidence grade. See
[architecture/firmware-architecture.md](architecture/firmware-architecture.md)
and [tooling/processor-module-audit.md](tooling/processor-module-audit.md).

## Variants

The Corolla (`8965F1208000`) is tracked as a related Toyota EPS variant.
Field probes establish its software IDs and diagnostic behavior, but MCU/family,
algorithm-template, secret-location, and SecOC-mechanism transfer remain
hypotheses until its firmware bytes are acquired. See [variants/README.md](variants/README.md).

## External tooling

External tooling has been analyzed for its relationship to the firmware:

- **Renesas Flash Programmer (RFP)** — host-side serial-programming protocol.
  See [tooling/renesas-rfp-rv40f.md](tooling/renesas-rfp-rv40f.md).
- **Toyota Techstream** — factory diagnostic software. Confirms our
  SecurityAccess model, provides a CAN traffic logger (`ptshim32.dll`), but
  does not interact with SecOC or the motor-control path.
  See [tooling/techstream.md](tooling/techstream.md).
- **Community Toyota/SecOC tooling** — authenticated RAM-exec, DataFlash
  extraction/oracle, Panda routing, and persistent-patch workflows are pinned
  and audited separately. See [tooling/README.md](tooling/README.md).
