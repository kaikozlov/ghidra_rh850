# Address reference

Consolidated address lookup across all subsystems. Every entry links to its
canonical report; this page is an index, not an explanation. All addresses are
CodeFlash VAs unless marked RAM or DataFlash.

## Boot / architecture

| Item | Address | Canonical report |
|---|---|---|
| Reset handler | `0x1F2` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| `boot_application_handoff` | `0x13B0` | [../architecture/boot-validity-and-flash-lifecycle.md](../architecture/boot-validity-and-flash-lifecycle.md) |
| `boot_validity_check` | `0x119E` | [../architecture/boot-validity-and-flash-lifecycle.md](../architecture/boot-validity-and-flash-lifecycle.md) |
| Application entry pointer | `0xFFDB8 → 0x20880` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| Application base / EBASE | `0x20000` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| INTBP (EIINT table) | `0x20200` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| Application foreground loop | `0x64FCC` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| Region descriptors (3) | `0x8E00` | [../architecture/boot-validity-and-flash-lifecycle.md](../architecture/boot-validity-and-flash-lifecycle.md) |
| Validity markers | `0x17E00`, `0xFFE00` | [../architecture/boot-validity-and-flash-lifecycle.md](../architecture/boot-validity-and-flash-lifecycle.md) |

## Bootloader security

| Item | Address | Canonical report |
|---|---|---|
| UDS service table (20 entries) | `0x8E54` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| `uds_security_access` (SID `0x27`) | `0x5516` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| `SEED_KEY_SECRET` | `0xBFE8` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| `PAYLOAD_BUILD_SECRET` | `0xBFD8` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| `security_access_derive_stage1_key` | `0x6FEC` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| `security_access_compute_expected_key` | `0x704C` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| `payload_build_derive_key` | `0x7068` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| AES-128 S-box | `0x8FF1` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| AES Rcon | `0x8FE1` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| Payload RAM target | RAM `0xFEBF0000..0xFEBF0FFF` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| Flash-callback load / call | `0x4350` / `0x435E` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |

## Application security

| Item | Address | Canonical report |
|---|---|---|
| Application SA L2 secret (16 B) | `0x20840` | [../security/application-security-access.md](../security/application-security-access.md) |
| SA L1 getSeed stub | `0x94E0E` | [../security/application-security-access.md](../security/application-security-access.md) |
| SA L1 sendKey stub | `0x94E22` | [../security/application-security-access.md](../security/application-security-access.md) |
| Seed generation (crypto HW) | `0x8C65A` | [../security/application-security-access.md](../security/application-security-access.md) |
| Seed storage | RAM `0xFEBF495A` | [../security/application-security-access.md](../security/application-security-access.md) |
| Key verification | `0x8C82A` | [../security/application-security-access.md](../security/application-security-access.md) |
| AES encrypt / decrypt primitives | `0x852B0` / `0x853EE` | [../security/application-security-access.md](../security/application-security-access.md) |
| AES key expansion wrapper | `0x865D4` | [../security/application-security-access.md](../security/application-security-access.md) |
| Inverse S-box / Rcon / Te / Td | `0x25628` / `0x23615` / `0x23628` / `0x24628` | [../security/application-security-access.md](../security/application-security-access.md) |

## Diagnostics

| Item | Address | Canonical report |
|---|---|---|
| Bootloader DID descriptors (4) | `0x8F14` | [../diagnostics/bootloader-dids.md](../diagnostics/bootloader-dids.md) |
| Bootloader RDBI / WDBI handlers | `0x5FB8` / `0x4948` | [../diagnostics/bootloader-dids.md](../diagnostics/bootloader-dids.md) |
| Bootloader SessionControl handler | `0x614A` | [../diagnostics/bootloader.md](../diagnostics/bootloader.md) |
| Application service table (17 SIDs) | `0x25E30` | [../diagnostics/application.md](../diagnostics/application.md) |
| Application DID read table (242) | `0x2941C` | [../diagnostics/application.md](../diagnostics/application.md) |
| Application DID write table (19) | `0x26AEC` | [../diagnostics/application.md](../diagnostics/application.md) |
| Application DID records (F181/F186/F18C) | `0x2A30C` | [../diagnostics/application.md](../diagnostics/application.md) |
| Application routine-ID table (32 pairs) | `0x25768` | [../diagnostics/application.md](../diagnostics/application.md) |
| Session callbacks / state machine | `0x93FF6` / `0x94006` / `0x94016` / `0x93F3C` | [../diagnostics/application.md](../diagnostics/application.md) |
| Phase-snapshot (programming gate) | RAM `0xFEBEE81F` (`GP+0x301F`) | [../diagnostics/application.md](../diagnostics/application.md) |
| Non-Dcm transition phase source | RAM `0xFEBEB1A4` | [../diagnostics/application.md](../diagnostics/application.md) |

## SecOC / storage

| Item | Address | Canonical report |
|---|---|---|
| NvM `ReadBlock` / `WriteBlock` | `0x72F58` / `0x72F84` | [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md) |
| Triplicate restore / persist / reconcile | `0x67590` / `0x67608` / `0x67C34` | [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md) |
| Application-GP work-buffer root | RAM `0xFEBF0B08` | [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md) |
| Owner table (blocks 2–123) | `0x2B1B0` | [../storage/dataflash.md](../storage/dataflash.md) |
| Object-15 RAM mirror | RAM `0xFEBF02E8` | [../storage/dataflash.md](../storage/dataflash.md) |
| Object-15 key field (raw/XOR55/XORAA) | DataFlash `0xFF206E14` / `0xFF206D14` / `0xFF206C14` | [../storage/dataflash.md](../storage/dataflash.md) |
| `application_dataflash_range_allowed` | `0x4EAD8` | [../storage/dataflash.md](../storage/dataflash.md) |

## Communications

| Item | Address | Canonical report |
|---|---|---|
| CAN1 acceptance table (51 rules) | `0x231A0` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| SecOC record IDs source | `0x25970` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |

## CAN IDs

| ID | Role | Canonical report |
|---|---|---|
| `0x7A1` / `0x7A9` | Primary physical diagnostic request/response | [../diagnostics/application.md](../diagnostics/application.md) |
| `0x777` | Functional diagnostic | [../diagnostics/application.md](../diagnostics/application.md) |
| `0x7A0` / `0x7A8` | Limited secondary physical | [../diagnostics/application.md](../diagnostics/application.md) |
| `0x7F7` | Diagnostic response address | [../communications/application-rx.md](../communications/application-rx.md) |
| `0x0F` / `0x2E4` / `0x131` / `0x132` / `0x90` / `0xD7` | SecOC-bound RX PDUs | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| `0x260` / `0x262` / `0x351` / `0x394` / `0x4A3` / `0x4C8` | Application TX COM I-PDUs | [../communications/application-tx.md](../communications/application-tx.md) |
| `0x344` | **Absent** from this image — do not project | [../communications/application-rx.md](../communications/application-rx.md) |
