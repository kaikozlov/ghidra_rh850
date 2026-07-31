# Toyota Techstream diagnostic software

> **Scope:** Toyota Techstream V18.00.008 (DENSO)
>
> **Document type:** external-source reverse engineering
>
> **Status:** active
>
> **Evidence source:** external-source
>
> **Evidence profile:** recovered/bounded — each claim is scoped to the pinned
> Techstream distribution, not the Sienna firmware or a live vehicle session
>
> **Canonical artifacts:** `techstream.lock.json`,
> `Techstream/unpacked.7z`
>
> **Verification:** lock-file hash comparison (future: `make verify-techstream`)
>
> **Related:** [workflow](../WORKFLOW.md),
> [Application SecurityAccess](../security/application-security-access.md),
> [Bootloader payload gate](../security/bootloader-payload-gate.md),
> [SecOC key lifecycle](../security/secoc/key-storage-and-lifecycle.md)

## Executive conclusion

Techstream is the Toyota factory diagnostic tool — a Windows application that
communicates with vehicle ECUs through a J2534 pass-thru VCI (Vehicle
Communication Interface) over standard UDS/ISO-TP. It performs diagnostic
reads (DTCs, data monitors, freeze frames), active tests, configuration
writes, and ECU reflashing (Calibration Update Wizard).

The analysis yields three categories of finding relative to the Sienna EPS
firmware:

1. **Independent corroboration** of our SA model: Techstream's
   `CSecurityAccessAES128` class confirms the AES-128-ECB seed/key
   construction recovered from firmware (SEC-BOOT-003, SEC-APP-001).

2. **A CAN traffic capture tool** (`ptshim32.dll`) — a J2534 API
   interceptor/logger that transparently records every UDS message between
   Techstream and the VCI. This is the highest-value practical artifact for
   bench validation of firmware findings.

3. **No new SecOC or motor-control information.** Techstream operates entirely
   through UDS diagnostics; it neither sends nor receives SecOC-secured
   runtime frames. The torque-command control path (CAN `0x2E4` → SecOC →
   motor actuation) is invisible to Techstream.

## 1. Pinned source

The analyzed distribution identifies itself as:

```text
Toyota Techstream
version V18.00.008
vendor DENSO CORPORATION
installer InstallScript Setup Launcher Unicode (Flexera IS 22.0.330)
build date 2015-09-14
product version 18.0.8.0
```

The installer (`Techstream_Setup_V18.00.008.exe`, 259 MiB) is an InstallScript
archive. The unpacked tree (`Techstream/unpacked.7z`, 6703 files, 580 MiB
uncompressed) contains the full installation:

```text
Toyota Diagnostics/
  Techstream/              # Main diagnostic application
    bin/                   # DLLs, communication configs
    DB/                    # .ddb diagnostic databases (per ECU)
    Env/                   # Configuration INIs
    NA/ EU/ JP/ OT/        # Regional databases and configs
  Calibration Update Wizard/  # CUW reflash toolchain
  Driver/                  # VCI USB drivers
```

Exact hashes, sizes, and descriptions for all analyzed artifacts are in
`techstream.lock.json`.

## 2. Communication architecture

Techstream communicates through a layered J2534 stack:

```text
Techstream.exe
  │
  ├─ CommandAPI.dll          # High-level diagnostic commands
  │    ├─ CommandCommon.dll  # UDS service implementations (SA, DTC, DID, ...)
  │    └─ CommandDataLib.dll # Serialization for diagnostic data
  │
  ├─ J2534Ctrl.dll           # J2534 device management
  │    └─ ptshim32.dll       # PassThru API interceptor/logger
  │         └─ [physical VCI DLL]  # e.g. MongoosePro, Mini-VCI
  │
  └─ COMM_INFO_*.ini         # CAN transport configuration
```

The CAN transport is configured by decoded INI files. The standard UDS-over-CAN
profile (from `COMM_INFO_EFI_P4CAN_FUNC.ini`) is:

| Parameter | Value |
|---|---|
| ProtocolID | 6 (ISO 15765 / UDS over CAN) |
| Data rate | 500 kbps |
| Physical request | `0x07E0` |
| Physical response | `0x07E8` |
| Functional request | `0x07DF` |
| Tester present | `0x3E` every 3000 ms |
| CAN DLC | 8 |
| Flow control | `0x300004` (BS=0, STmin=4) |

> These are gateway-facing OBD addresses, not the EPS bootloader's direct
> physical `0x7A1` / functional `0x777`. The gateway routes diagnostic
> requests to the target ECU.

## 3. INI obfuscation

All `.ini` configuration files in the Techstream tree are obfuscated with a
trivial byte-complement encoding:

```
decoded[i] = 0xFF − encoded[i]
```

This is not encryption — it is byte-level inversion. Files whose first bytes
are printable ASCII (`;`, `[`, etc.) are stored in plaintext and do not
require decoding. The decoded INIs are stored under `Techstream/decoded/`
during analysis.

The obfuscation was identified by matching encoded byte `0xF2` to plaintext
`\r` (0x0D), confirming `0xFF − 0x0D = 0xF2`.

## 4. SecurityAccess implementations

`CommandCommon.dll` (source: `SecurityAccess*.cpp` from the KGProject tree)
contains four independent SA implementations:

### 4.1 CSecurityAccess (legacy)

The base class for non-security ECUs. Key methods:

| Method | C++ symbol | Role |
|---|---|---|
| `GetSeedData` | `?GetKey@CSecurityAccess@@IAEKKGPAV?$CCmdList@@PAE@Z` | Request seed (UDS `27 01`) |
| `GetKey` | `?GetKey@CSecurityAccess@@IAEKKGPAV...PAE@Z` | Compute key from seed |
| `Encrypt` | `?Encrypt@CSecurityAccess@@IAEXPAK0@Z` | Key derivation transform |
| `F` | `?F@CSecurityAccess@@IAEKK@Z` | Internal round function |
| `SndKeyData` | (inlined into `GetKey`) | Send key (UDS `27 02`) |
| `SetCommonKey` | `?SetCommonKey@CSecurityAccess@@IAEKKG@Z` | Load the shared secret |

Uses a custom (non-AES) transform with internal `Encrypt` and `F` round
functions. Applied to older Denso ECUs.

### 4.2 CSecurityAccessAES128 (TSS 3.0 family)

**This is the implementation that matches our firmware findings.** Key methods:

| Method | C++ symbol | Role |
|---|---|---|
| `GetSeedData` | `?GetSeedData@CSecurityAccessAES128@@IAEK...` | Request seed (UDS `27 01`) |
| `AES_128_ECB` | `?AES_128_ECB@CSecurityAccessAES128@@QAEKPAE00@Z` | Single-block AES-128-ECB |
| `SndKeyData` | `?SndKeyData@CSecurityAccessAES128@@IAEK...` | Send computed key (UDS `27 02`) |
| `CancelSecurity` | `?CancelSecurity@CSecurityAccessAES128@@QAEK...PAVCCommCachePlusP5@@K@Z` | SA teardown |

This class uses AES-128-ECB for the seed/key derivation, matching the
construction recovered from both bootloader firmware (SEC-BOOT-003:
`expected = AES-ENC(AES-DEC(SEED_KEY_SECRET, data_record), ecu_seed)`) and
application firmware (SEC-APP-001: 16-byte secret at CodeFlash `0x20840`).

Techstream must compute the same key the firmware expects, which means the
AES-128 secret is either embedded in the calibration/ECU-definition data or
fetched from Toyota's online portal. The `CSecurityAccessAES128` class is used
by ADS (advanced driving) and PCS (pre-collision system) operations — the TSS
3.0 family that includes the Sienna EPS.

### 4.3 CSecurityAccessCGW_DK

Central Gateway variant using Denso/KW protocol. Has its own
`StartDiagSession`, `EndDiagSession`, `GetCurrentLevel`, `ConnectChk`, and
`CancelSecurityMain_DK` methods. Not directly relevant to the EPS.

### 4.4 CSecurityAccessSUBARU

Separate implementation for Subaru-shared platform vehicles. Has `GenerateKey`,
`GetConversionKey`, `ChangeKeyData`, `ChangeSeedData`, and DES-based
derivation (`CalcSeedKeyForDES`). Not relevant to Toyota EPS.

## 5. Calibration Update Wizard (CUW)

The CUW (`Calibration Update Wizard/Cuw.exe`) is the ECU reflashing tool. It
implements a two-phase write sequence through a family of ECU-specific DLLs.

### 5.1 Prepare-write phase

`CCanCommonPrepareWriter` (base) and its P4/P5/unified subclasses execute the
pre-flash authentication and mode transition:

1. **Diagnostic session control** — enter extended/programming session
2. **SecurityAccess** — `CalcSeedKey(seed)` computes the key from the seed
   using the calibration file's embedded seed/key pair
3. **CommunicationControl** — suppress normal ECU traffic
4. **RoutineControl** — enter programming mode (on central gateway ECUs)

Timing parameters are configured through `TCUWControlCommPhase.dll` using a
calibration file that specifies:

- `WaitTimeAfterSeedData` — delay between seed request and key send
- `WaitTimeAfterSeedKey` — delay after SA completion
- `SecurityKey` / `SecurityAccessPassword` — embedded key material
- `FlagToCalcKeyLogicForEncrypt` — selects encrypt vs. decrypt key path
- `CANCommunicationSpeedAddress` — baud rate register address
- `PasswordCheckIDAddress` / `PasswordAddress` — ECU-specific addresses

The seed/key comes from `CalibrationFile::GetSeedKey()` and
`CalibrationFile::GetServiceAuthKey()` — **embedded in the calibration file
itself, not fetched online**. The online portal (`ReprogrammingSecurity` URL)
is only invoked for immobilizer resets and MAC key management, not for
routine ECU reflashing.

### 5.2 Flash-write phase

`CUnifiedUtils` and ECU-specific flash writers execute:

1. **RequestDownload** (UDS `0x34`) — negotiate transfer with address/length
2. **TransferData** (UDS `0x36`) — stream flash data blocks
3. **RoutineControl** (UDS `0x31`) — erase and verify
4. **TransferExit** (UDS `0x37`) — end transfer
5. **ECUReset** (UDS `0x11`) — reboot into new firmware

ECU-specific flash writers include:
`TCUWCanReproStdFlashWriter` (standard CAN), `TCUWCanUnifiedFlashWriter`
(unified), `TCUWCanSecurityVFORESTFlashWriter` (FOREST/RH850 security),
`TCUWCanPowerTrainFlashWriter`, and variants for airbag, chassis, body, HINO,
M16C, MMC, PSA, and SBR ECUs.

## 6. ptshim32.dll — J2534 traffic logger

`ptshim32.dll` is a J2534 PassThru API interceptor. Its PDB path is
`C:\kgproject\Control\J2534Logger\ptshim32\Release\ptshim32.pdb`. It exports
the full J2534 v04.04 API surface plus logging extensions:

| Extension | Role |
|---|---|
| `PassThruLoadLibrary` | Load the real VCI driver DLL |
| `PassThruSaveLog` | Flush captured traffic to file |
| `PassThruWriteToLogA/W` | Write log entries (ASCII/Unicode) |
| `PassThruUnloadLibrary` | Unload the real VCI driver |

When installed as the system J2534 DLL (by placing it in the DLL search path
before the real VCI driver), it transparently proxies all `PassThruOpen`,
`PassThruConnect`, `PassThruReadMsgs`, `PassThruWriteMsgs`, etc. calls while
recording every CAN message.

A v05.00 API variant (`ptshim32_0500.dll`, 18 MiB) supports the newer J2534
v05.00 API surface including `PassThruLogicalConnect`,
`PassThruQueueMsgs_v0500`, and `PassThruSelect_v0500`.

**Practical use:** Install Techstream on a Windows machine with a bench EPS
ECU, replace the VCI driver with `ptshim32.dll`, and perform a diagnostic or
reflash session. The resulting log captures the complete UDS transcript — SA
seed/key exchange, DID reads, session transitions, and programming handoff —
which can be diffed against our static firmware analysis to validate or
correct recovered claims.

## 7. Diagnostic databases (.ddb)

Techstream ships ECU-specific diagnostic databases in a proprietary binary
format (`DiagTool DataCtrl` magic). The EPS-relevant databases:

| Database | Region | Size | Content |
|---|---|---|---|
| `EPS_P4DK3.ddb` | NA | 6.6 KiB | EPS Phase-4 CAN DK3 diagnostic table |
| `EPS_CAN_P4DK.ddb` | NA | 10.5 KiB | EPS Phase-4 CAN functional diagnostics |
| `EPS_CAN_P4DK.ddb` | EU/JP | 10.5+ KiB | Same, regional variant |
| `Security_P4.ddb` | NA/EU | 13 KiB | Phase-4 SecurityAccess definitions |
| `Toyota.ddb` | all | 13.0 MiB | Master ECU enumeration (part numbers, calibrations) |

The binary format uses a 32-byte header (`40 00 0c 16 0c 08 00 39 02 97` +
`"DiagTool DataCtrl\0"`) followed by offset tables and structured diagnostic
records. The format is not yet fully decoded; the records are consumed at
runtime by the `CommandDataLib` / `CommandAPI` DLL layer.

## 8. Relationship to firmware findings

### 8.1 Corroborated

| Firmware finding | Techstream corroboration |
|---|---|
| SEC-BOOT-003: AES-128-ECB SA construction | `CSecurityAccessAES128::AES_128_ECB` implements the same cipher |
| SEC-APP-001: Application SA level 2 with AES-128 | `CSecurityAccessAES128` is the TSS 3.0 SA class |
| DIAG-APP-003: Programming handoff gates | CUW prepare-write implements the same session/speed/phase sequence |
| Bootloader diagnostic `0x7A1` / `0x777` | Gateway routing (`07E0`/`07DF` → ECU-specific physical address) |

### 8.2 Not addressed

| Open question | Techstream relevance |
|---|---|
| SecOC slot-4 key extraction | None — Techstream does not interact with SecOC |
| Motor actuation join (`0x2E4` → d/q current) | None — Techstream uses UDS diagnostics, not runtime control |
| Runtime RAM key-slot mirror | None — Techstream reads DIDs, not raw RAM |
| ICU-S command 5/13 characterization | None — Techstream does not issue ICU-S commands |

### 8.3 New leads

| Lead | Value |
|---|---|
| `ptshim32.dll` CAN logger | Capture a real Techstream↔EPS session for transcript validation |
| `CSecurityAccessAES128` source paths | PDB/source-tree context for the KGProject diagnostic framework |
| `ReprogrammingSecurity` / `MACKey_Login` URLs | Toyota online portals for SA authorization (immobilizer/MAC only) |
| `TCUWControlCommPhase.dll` parameters | Exact timing values for SA seed/key exchange during reflash |
| `[ISTA_T3_Login]` credentials | Hardcoded hex credentials in `uspublic.ini` for Toyota ISTA portal |

## 9. Limitations

This analysis is static — extracted from the installer without executing
Techstream on a vehicle or bench. The findings describe the *capability* and
*design* of the toolchain, not observed runtime behavior. Specifically:

- The SA key computation in `CSecurityAccessAES128` was identified by symbol
  analysis, not by executing the cipher against a known seed/key pair.
- The `.ddb` binary format is structurally identified but its diagnostic
  record contents are not fully decoded.
- The `ptshim32.dll` logger is described by export/PDB analysis; its actual
  log format and capture behavior are untested.
- No live UDS transcript has been captured to validate against firmware
  findings.
