# Findings ledger

The canonical key-findings ledger for this repository. Every material claim
has exactly one canonical home in a subsystem report; other documents
summarize it in one sentence and link there. This ledger records the
**key** findings per subsystem — it is not an exhaustive per-function index
(for that see `data/semantic_coverage_ledger.csv`).

## Evidence model

Evidence has two dimensions: **source** (where the observation came from) and
**confidence** (how strongly it is established). Keep them separate — a
Corolla field observation is a real, direct observation (`observed`) that is
nonetheless not reproduced from firmware bytes.

### Evidence source

| Source | Meaning |
|---|---|
| **firmware-static** | Recovered from the committed firmware bytes |
| **dynamic-probe** | Observed on a live vehicle / bus |
| **generated-artifact** | Produced by a `data/` generator |
| **external-source** | From an outside document, report, or third party |

### Confidence grade

| Grade | Meaning |
|---|---|
| **verified** | Directly asserted by a deterministic test in `tests/` |
| **observed** | Directly observed (e.g. a field probe) but not reproduced by a repository test |
| **recovered** | Control/data flow substantially reconstructed; not claimed as behaviorally understood |
| **bounded** | Interpretation constrained, exact semantics unknown |
| **hypothesis** | Plausible, explicitly unverified |
| **disproved** | Retained only to prevent regression; see [CORRECTIONS.md](CORRECTIONS.md) |

### Mapping the variant CSV vocabulary

`data/tss3_eps_variant_matrix.csv` (and `tests/verify_tss3_variant_matrix.py`)
use a coarser per-row grade. The mapping onto this model is:

| CSV grade | Source | Confidence |
|---|---|---|
| `definitive` | firmware-static | verified |
| `inference` | dynamic-probe / external-source | observed → hypothesis (per field) |
| `none` | — | hypothesis (unobserved) |

The CSV grade is a row-level summary; individual fields within an `inference`
row carry their own confidence on the variant page (e.g. a directly observed
software ID is `observed`, an inferred MCU is `hypothesis`).


## Core architecture

| ID | Claim | Scope | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|
| ARCH-001 | Reset handler `0x1F2` sets `gp = 0xFEBF9800` | Sienna | verified | `verify_findings.py` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| ARCH-002 | Application vector/executable base `0x20000`; entry `0xFFDB8 → 0x20880`; `EBASE=0x20000`, `INTBP=0x20200`; foreground loop `0x64FCC` | Sienna | verified | `verify_architecture.py` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| ARCH-003 | Boot validity gate: `0x13B0 → 0x119E`; two retry-bounded phases; markers at `0x17E00`/`0xFFE00` hold `0x5AA5A55A` | Sienna | verified | `verify_boot_trust.py` | [../architecture/boot-validity-and-flash-lifecycle.md](../architecture/boot-validity-and-flash-lifecycle.md) |
| ARCH-004 | Application foreground loop polls TAUJ0 CH3 `EIRF136`; EIINT 133–135 (CH0–2), 187/188 (RSCAN CAN1), 292/293 (ICU-S callbacks) | Sienna | verified | `verify_architecture.py` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| ARCH-005 | EIINT 292/293 are active ICU-S crypto-driver callback paths despite generic hardware-table `Reserved` labels | Sienna | recovered | `verify_architecture.py` | [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) |
| ARCH-006 | 5,865 functions / 178,645 instructions / 37,650 symbols on the last annotated rebuild; most rows `evidence_grade=recovered` | Sienna | bounded | `make verify-processor` floors | [../tooling/processor-module-audit.md](../tooling/processor-module-audit.md) |

## Bootloader security

| ID | Claim | Scope | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|
| SEC-BOOT-001 | `PAYLOAD_BUILD_SECRET` at CodeFlash `0xBFD8` (file `0x13FD8`), xref `0x7070` | Sienna | verified | `verify_findings.py` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| SEC-BOOT-002 | `SEED_KEY_SECRET` at CodeFlash `0xBFE8` (file `0x13FE8`), xref `0x6FF8` | Sienna | verified | `verify_findings.py` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| SEC-BOOT-003 | Bootloader SA: `expected = AES-ENC(AES-DEC(SEED_KEY_SECRET, data_record), ecu_seed)` | Sienna | verified | `verify_findings.py` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| SEC-BOOT-004 | UDS service table `0x8E54` (20 entries); SID `0x27` → handler `0x5516`; AES S-box `0x8FF1`, Rcon `0x8FE1` | Sienna | verified | `verify_findings.py` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| SEC-BOOT-005 | Payload gate: TransferData decrypts AES-CBC into `0xFEBF0000..0xFEBF0FFF`; routine `0x10F0` checks addr/len + CRC32 + CMAC; `0xFF00` erase path loads callback at RAM `0xFEBF0FD0` (CodeFlash `0x4350`, called `0x435E`) | Sienna | verified | `verify_payload_gate.py` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| SEC-BOOT-006 | `0xFF00` is not a direct execute-RAM routine; execution occurs by replacing the legitimate flash-driver callback inside the authenticated image | Sienna | verified | `verify_payload_gate.py` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| SEC-BOOT-007 | SecurityAccess is the mandatory gate (not merely the session) for download/write/reset: RequestDownload (`0x5D68`), WDBI (`0x49C6`), ECUReset (`0x610C`) each require SA-unlock byte `0xFEBF2B0F == 2` (else NRC `0x33`); the byte is set to `2` only by SA send_key success (`0x54DC`), while boot init (`0x5090`) and the session-change handler (`0x561E`) only write `1` — so `10 0x` alone never satisfies the gate | Sienna | verified | `verify_security_gate.py` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |
| SEC-BOOT-008 | Boot-time application trust is CRC32 descriptors plus fixed `0x5AA5A55A` markers, not an OEM signature. After authenticated RAM code execution, a durable CodeFlash write with recomputed CRC/markers can in principle persist an application-context hook; no persistent patch has been bench-tested | Sienna | recovered | `verify_boot_trust.py`, `verify_payload_gate.py` | [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) |

## Application security

| ID | Claim | Scope | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|
| SEC-APP-001 | Application SA level 2 (`03/04`) uses 16-byte secret at CodeFlash `0x20840` | Sienna | verified | `verify_application_diagnostics.py` | [../security/application-security-access.md](../security/application-security-access.md) |
| SEC-APP-002 | Application SA level 1 (`01/02`) is a compiled stub (`return 1`); only level 2 is functional | Sienna | verified | `verify_application_diagnostics.py` | [../security/application-security-access.md](../security/application-security-access.md) |
| SEC-APP-003 | Application keygen is deterministic and attacker-controlled: no request-length check on the seed path; data record is tester-controlled padding or stale/zero | Sienna | verified | `verify_application_diagnostics.py` | [../security/application-security-access.md](../security/application-security-access.md) |
| SEC-APP-004 | No configured SecurityAccess gating in this calibration: all 17 services `sec_count=0`, all 242 readable DIDs level ≤ 0, all 19 writable DIDs `level_count=0`, zero crypto refs in 13 `0xAB` RID callbacks | Sienna | verified | `verify_security_consumers.py`, `verify_ab_rid_callbacks.py` | [../security/application-security-access.md](../security/application-security-access.md) |
| SEC-APP-005 | Empty Dcm security policy exposes live session-only operations: CommunicationControl applies real communication-mode changes without a recovered speed gate; programming handoff is identity-unauthenticated but speed/supply/phase-gated; WDBI has no Dcm SA and its lower authorization hook is a success stub. DID `0x1010` remains package-authenticated inside ICU-S | Sienna | recovered | `verify_application_diagnostics.py`, `verify_security_consumers.py`, `verify_icus_key_update.py` | [../security/application-security-access.md](../security/application-security-access.md) |

## Diagnostics

| ID | Claim | Scope | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|
| DIAG-BOOT-001 | Bootloader DID table `0x8F14` has exactly 4 descriptors; `F181` sole readable, returns `02 ‖ 32*0x21` placeholder; `0201/0202/0203` only writable, strict order `0203→0201→0202` | Sienna | verified | `verify_did_model.py` | [../diagnostics/bootloader-dids.md](../diagnostics/bootloader-dids.md) |
| DIAG-BOOT-002 | Bootloader SIDs `10/11/28/3E/85` and routines `10F1–10F3` fully characterized; functional ID is `0x777`, not generic OBD `0x7DF` | Sienna | verified | `verify_bootloader_diagnostics.py` | [../diagnostics/bootloader.md](../diagnostics/bootloader.md) |
| DIAG-APP-001 | Application service table `0x25E30`: 17 SIDs `10/11/14/19/22/23/27/28/2E/31/34/36/37/3E/85/AB/BA`; DID table `0x2941C` (242 read) / `0x26AEC` (19 write); RID table `0x25768` (32 pairs) | Sienna | verified | `verify_application_diagnostics.py` | [../diagnostics/application.md](../diagnostics/application.md) |
| DIAG-APP-002 | Application `F181`/`F186`/`F18C` return real values via callbacks `0x4E8E4/0x4E90A/0x4E918` | Sienna | verified | `verify_application_diagnostics.py` | [../diagnostics/application.md](../diagnostics/application.md) |
| DIAG-APP-003 | PROGRAMMING handoff: allowed only from session 2/3, rejects speed > `0x0180` (NRC `0x88`), requires phase snapshot `0xFEBEE81F != 0x11`, supply ≥ `0x0A00`, clear handoff flag; success queues event 9, shutdown `0x900`, hard reset | Sienna | verified | `verify_application_diagnostics.py` | [../diagnostics/application.md](../diagnostics/application.md) |
| DIAG-APP-004 | First `10 02` in extraction tooling is an application reset/handoff, not a call to bootloader handler `0x614A` | Sienna | verified | `verify_application_diagnostics.py` | [../diagnostics/application.md](../diagnostics/application.md) |
| DIAG-APP-005 | `0xAB` is an asynchronous control service; 13 RID callbacks contain no identified direct references to AES/CMAC, ICU-S, NvM R/W, security-state reader, or SecOC key material; 'calibration/flash control' remains a hypothesis | Sienna | bounded | `verify_ab_rid_callbacks.py` | [../diagnostics/application.md](../diagnostics/application.md) |
| DIAG-APP-006 | SIDs `14/23/31/34/36/37/BA` have null callbacks; generated Dcm DSP start-phase is globally disabled (flag `@0x25DCC=0x00`) — simple positive responses only | Sienna | verified | `verify_application_diagnostics.py` | [../diagnostics/application.md](../diagnostics/application.md) |

## SecOC

| ID | Claim | Scope | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|
| SECOC-001 | Six records bind `0x0F/0x2E4/0x131/0x132/0x90/0xD7` to exact RX PDU routes; `0x344` has no receive filter or SecOC record | Sienna | verified | `verify_secoc_application.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-002 | Classic frames authenticate `DataID_be16 ‖ payload4 ‖ freshness48`; trailer = 4 freshness bits + first 28 CMAC bits; CMAC verify uses CryptoIf handle 0, ICU-S slot 4 | Sienna | verified | `verify_secoc_application.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-003 | Object 15 (SecOC key): len 32, base block 41, RAM `0xFEBF02E8`; raw `0xFF206E14`, XOR55 `0xFF206D14`, XORAA `0xFF206C14`; all three copies invalid in this snapshot | This exact dump | verified | `verify_dataflash_layout.py` | [../storage/dataflash.md](../storage/dataflash.md) |
| SECOC-004 | Both slot-4 KAT crypto bodies are compiled out by fixed gate `CodeFlash[0x30EF3]=0x00` (required `0x5A`); the latent `FF*16` vector asserts nothing about the live slot-4 key | This calibration | verified | `verify_secoc_application.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-005 | Object 15 has no static producer in this calibration (27 direct + 19 wrapper callsites, no AB/BA edge) | Sienna | verified | `generate_object15_reachability.py` census | [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md) |
| SECOC-006 | ICU-S command 5 is substantially recovered as the MAC-generation twin of command-7 verify: runtime selector, input pointer/length, caller output pointer/length, 16-byte result copy, paired driver records, and software acceptance of selectors `0..14`; physical slot-4 generation permission remains unobserved | Sienna | recovered | `verify_secoc_application.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-007 | The sole configured command-5 caller is a dormant crypto-test bank: CAN `0x01B..0x01F` provide selector/mode, chosen 16-byte input, and expected 16-byte result after activation and three stable updates; the only recovered activator has no caller/function-pointer edge, and completion compares locally rather than returning the MAC | Sienna | recovered | `verify_secoc_application.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-008 | The configured SecOC graph is receive-only: command-5 has no production caller beyond the crypto-test harness, and none of the six ordinary COM Tx routes uses SecOC or command 5; an application-resident signing proxy still requires an application-context hook, output route, sender freshness, and dynamic latency/slot-policy validation. The constructible bootloader callback is an execution bridge, not proof of initialized application-context behavior | Sienna | recovered | `verify_secoc_application.py`, `verify_application_transmit.py`, `verify_icus_software_paths.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-009 | Enabled WDBI DID `0x1010` (extended session, no Dcm SA level) reaches literal ICU-S command 8 with a `16+32+16`-byte request and `32+16`-byte result, recovering a SHE-compatible M1/M2/M3 → M4/M5 authenticated key-update path. MainPE treats the package opaquely; package target/AuthID/counter and actual dealer use remain unobserved | Sienna | recovered | `verify_icus_key_update.py` | [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md) |
| SECOC-010 | DID `0x1010` uses OEM selector `01` to start (`2E 01 1010` + 64 bytes) and selector `03` to read results (`2E 03 1010`); status `01/02/FF` is pending/complete/failed, only `02` exposes the 48-byte proof, and either terminal read clears the diagnostic banks | Sienna | verified | `verify_icus_key_update.py`, `verify_icus_trace_decoder.py` | [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md) |
| SECOC-011 | The recovered receive chain fails closed: ICU verify false neither commits freshness nor delivers the authentic PDU; no simple result-code inversion bypass is present | Sienna | verified | `verify_secoc_security_properties.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-012 | SecOC initialization zeroes current/pending sync and all ordinary receive windows; authenticated sync accepts any forward trip/reset jump with no maximum delta. A captured positive sync is structurally forward after reset, but practical replay requires a startup race/suppression experiment | Sienna | recovered | `verify_secoc_security_properties.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-013 | All profiles expose 28 CMAC bits; failed verification leaves freshness unchanged and no per-source/PDU failure lockout is recovered, while the wrapper polls up to `0xE07` iterations. This bounds an online forgery/ICU-availability surface; practical throughput is unobserved | Sienna | recovered | `verify_secoc_security_properties.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-014 | Classic secured routes require exact DLC 8, disproving a short-classic stale-tail bypass. FD routes accept DLC 32..64 then clamp to 32 before SecOC, creating ignored-suffix aliases whose cross-ECU impact is bounded | Sienna | verified | `verify_secoc_security_properties.py` | [../security/secoc/application-chain.md](../security/secoc/application-chain.md) |
| SECOC-015 | All nine direct `ICUSCMD` writers are accounted for. Dynamic low commands are constrained to command 1/3, 5, 7, and literal 8; no **stock application** writer invokes command 13 or another recovered persistent-slot plaintext export. This census does not constrain a direct custom command word or undocumented ICU-S behavior. Command 1/3 accepts software selectors `0..14`, but slot-4 hardware permission remains unknown | Sienna | verified | `verify_icus_key_recovery_surface.py` | [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md) |
| SECOC-016 | Protected FD IDs `0x090`/`0x0D7` authenticate 36 bytes as `DataID_be16 || payload[28] || freshness[6]`, giving 14 chosen payload bytes in CMAC's first AES block. Recovering the corresponding 14 key bytes leaves a `2^16` completion search; one 28-bit stock tag has about `0.000244` expected false candidates | Sienna | verified | `verify_icus_key_recovery_surface.py` | [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md) |
| SECOC-017 | Renesas classifies `R7F701381` as a 1 MiB DPS part with an external 1.25 V core rail; the 100-pin table names VDD at pins 11/66/98. A public report naming the same part instead describes VCL/eVR pins 11/66, so the physical target's marking, voltage, and rail topology must be measured before copying a power/glitch setup | P1M-E hardware lead | bounded | external datasheet/report | [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md) |
| SECOC-018 | The unavailable restricted ICU-S/ICUSE manual prevents assigning definitive Renesas semantics to direct command 13. Selector-4 handling, output format, lifecycle-dependent behavior, and a possible slot-4-to-`RAM_KEY` copy/alias are untested; public SHE behavior does not disprove the proposed copy-then-export experiment | P1M-E ICU-S | bounded | firmware-static boundary plus external public SHE only | [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md) |
| SECOC-019 | Repository-known bootloader gate material constructs authenticated 4 KiB RAM callbacks; the payload-controlled word at `FEBF0FD0` is called by the flash engine, and both pinned CAN-dump payloads leave more than `0xE00` bytes before the trailer. This provides a software-only, non-persistent direct-ICU experiment; bootloader lifecycle results do not automatically transfer to initialized application context | Sienna | verified | `verify_payload_gate.py`, `verify_icus_software_paths.py` | [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md) |
| SECOC-020 | Application transport caps each diagnostic route at 256 bytes; SIDs `0x23/0x34/0x36/0x37` have null service callbacks; WDBI enforces descriptor-derived exact input size and its largest configured request is 67 bytes. No obvious application memory/download or WDBI length-overwrite foothold is recovered from these paths | Sienna | verified | `verify_icus_software_paths.py` | [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md) |
| SECOC-021 | Existing paths can template command-13 characterization but are not drop-in exports: command 5 preserves selectors `0..14` and one output block but lacks stock byte transport; DID `0x1010` returns 48 bytes but has no command-word selector and fixes four input/three output blocks. Both low-level engines track the command ID and reject a submitted/tracked mismatch | Sienna | verified structure; hardware untested | `verify_icus_software_paths.py` | [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md) |

## Storage

| ID | Claim | Scope | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|
| STORE-001 | 122 physical records occupy pages 256–479; owner table `0x2B1B0` maps blocks 2–49 (triplicate bank) and 50–123 (74-record checkpoint ring, 24 enabled / 8 disabled slots) | Sienna | verified | `verify_dataflash_layout.py` | [../storage/dataflash.md](../storage/dataflash.md) |
| STORE-002 | Pages 432–479 are the full 16-object SecOC triplicate bank | Sienna | verified | `verify_dataflash_layout.py` | [../storage/dataflash.md](../storage/dataflash.md) |
| STORE-003 | Pages 0–255 unallocated, outside both configured classes, erased-compatible undefined readback; prior use indeterminable | Sienna | bounded | `verify_dataflash_semantics.py` | [../storage/dataflash.md](../storage/dataflash.md) |
| STORE-004 | `0x4EAD8` rejects accesses overlapping pages 480–511 and optional-object pages 432–443; dumped 00/FF tail does not reveal protected contents | Sienna | verified | `verify_dataflash_layout.py` | [../storage/dataflash.md](../storage/dataflash.md) |
| STORE-005 | DIDs `0x201/0x202/0x203` are volatile bootloader inputs, not DataFlash-backed | Sienna | verified | `verify_did_model.py` | [../diagnostics/bootloader-dids.md](../diagnostics/bootloader-dids.md) |

## Communications

| ID | Claim | Scope | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|
| COM-001 | CAN1 acceptance table `0x231A0`: 47 normal Rx I-PDUs + `0x7A1/0x777/0x7A0/0x7F7`; `0x2E4/0x0F/0x131` explicit RX routes; `0x344` absent | Sienna | verified | `verify_architecture.py`, `verify_application_receive.py` | [../communications/application-rx.md](../communications/application-rx.md) |
| COM-002 | 47 normal Rx I-PDUs, 242 COM signals (58..299); six SecOC envelopes stay inside the 47; 145 signals recovered, 97 configured-unresolved | Sienna | verified | `verify_application_receive.py` | [../communications/application-rx.md](../communications/application-rx.md) |
| COM-003 | 11 active CanIf TX routes; 6 COM I-PDUs on CAN IDs `0x260/0x262/0x351/0x394/0x4A3/0x4C8`; 58 generated COM signal IDs | Sienna | verified | `verify_application_transmit.py` | [../communications/application-tx.md](../communications/application-tx.md) |

## Variants

| ID | Claim | Scope | Source | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|---|
| VAR-001 | Corolla field probes directly observe: software IDs `8965F1208000`/`8A3111213000`, CAN-FD bus, physical `0x7A1→0x7A9`, `F181/F186/F18C`, 13 answering SIDs, level-`0x03` seed behavior, SecOC sync `0x0F`, secured IDs `0x2E4/0x131/0x344` | Corolla | dynamic-probe | observed | `verify_tss3_variant_matrix.py` | [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md) |
| VAR-002 | Corolla MCU, SA algorithm template, application secret, bootloader payload gate, bootloader secrets, and complete SecOC implementation are hypotheses to check against firmware, not confirmed facts | Corolla | — | hypothesis | — | [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md) |
| VAR-003 | Corolla `10 02` programming timeout is inconclusive (reset vs. silent rejection unresolved; discriminating bus capture missing) | Corolla | dynamic-probe | bounded | `verify_tss3_variant_matrix.py` | [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md) |

## Renesas programming interface

| ID | Claim | Scope | Source | Grade | Checked by | Canonical report |
|---|---|---|---|---|---|---|
| RFP-001 | Pinned RFP V3.24.00 retains separate `BootRV40F` and `BootRH850Gen2` host-protocol implementations; RV40F request framing is `01 ‖ length_be16 ‖ command ‖ payload ‖ checksum ‖ 03`, with responses beginning `0x81` | RFP host library | external-source | recovered | `verify_renesas_rfp.py` | [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md) |
| RFP-002 | RV40F ICU-related commands recovered so far are `0x6E/0x6F/0x70/0x71/0x74/0x75`; they implement four-byte ICU-S options, validation/mode probes, and a structured legacy extended-option record | RFP host library | external-source | recovered | `verify_renesas_rfp.py` | [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md) |
| RFP-003 | `SetICUM` sends a four-byte auxiliary field plus a 15-byte record made from three 32-bit fields and three flag-like bytes; it is not shaped as `slot ‖ AES-128 key` and has no recovered slot selector | RFP host library | external-source | recovered | `verify_renesas_rfp.py` body lock | [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md) |
| RFP-004 | No named `BootRV40F` key-load/key-update API exists in the retained symbol table; applicability to P1M-E and the actual Toyota/Denso slot-4 provisioning mechanism remain unobserved | RFP host library / Sienna transfer | external-source | bounded | `verify_renesas_rfp.py` symbol census | [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md) |
| RFP-005 | All 68 packaged `Firmwares/*.bin` images identify as SEGGER probe firmware; explicit target resources are DA/RA-only, the sole provisioning payload is RA6B1-only, and no RH850/RV40F/P1M/ICU resource or `BootRV40F::DownloadImage` path is present | RFP package | external-source | recovered | `verify_renesas_rfp.py` package/symbol census | [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md) |
| RFP-006 | The documented `-fo flags icus` high-level task represents ICU-S enable as flag `0x00010000` and reaches payload-free `ValidateICU_S`; exported four-byte `SetICUSOptionByte` has no internal `libRFP` code caller and is not the recovered standard enable path | RFP host library | external-source | recovered | `verify_renesas_rfp.py` body lock / CLI fixture | [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md) |
