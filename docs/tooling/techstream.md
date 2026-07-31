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

## 4. SecurityAccess dispatch — which path each ECU uses

Techstream V18 supports many ECU generations. The SA path is not uniform — it
is selected by a two-level dispatch:

### 4.0 Decision tree

```text
RUNTIME DIAGNOSTICS (DTC read, data monitor, FFD access):
│
├─ DS2/KW protocol ECUs (older Denso):
│   CPubEFI  → SecurityAccess  (Feistel cipher, §4.2)
│   CPubIMB  → SecurityAccess  (Feistel cipher)
│   CPubKFS  → SecurityAccess  (Feistel cipher)
│   CPubEPS  → NO SecurityAccess  ← EPS has no SA in the DS2 path
│
├─ UDS Phase-4/5 CAN ECUs (UtilityExNK2.dll dispatch by ECU abbreviation):
│   Ex2ADS_11_*  → CSecurityAccessAES128  (key="FUKUMORIYOSIYAMA", §4.1)
│   Ex2CSP_06_*  → CSecurityAccess
│   Ex2PCM_01/02/03_*  → CSecurityAccess
│   Ex2SSU_08_*  → CSecurityAccessSUBARU
│   Ex2SVI_01_*  → CSecurityAccessAES128
│   Ex2_PSAVC_*  → CSecurityAccess
│   (no EPS entry — EPS does not require SA for runtime diagnostics)
│
└─ Central Gateway:
    Ex2ComSecurityAccessCGW → CSecurityAccessCGW_DK (§4.3)

REFLASHING (CUW / Calibration Update Wizard):
│
├─ Flash writer class selected by calibration file metadata:
│
│   EPS (V850E)  → CCanEMPS_V850E_PS2FlashWriter
│                   └─ CollateSeedKey uses CalibrationFile::GetSeedKey()
│                      (key embedded in .cuw file, NOT hardcoded in DLL)
│
│   EPS (older)  → CSilEMPS_V850E_PS1_2FlashWriter
│   Airbag       → CCanAirbagFlashWriter
│   Body         → CCanBodyFlashWriter
│   Chassis      → CCanChassisShrinkFlashWriter
│   EPB          → CCanEPBFlashWriter
│   FOREST/RH850 → CCanVFORESTFlashWriter (no SA — direct write/erase)
│   P5 CAN       → CP5CanFlashWriter
│   EPC          → CCanElectricPowerControlFlashWriter
│   ...          → (20+ writer classes total)
```

**Key implication for the Sienna EPS:** the `FUKUMORIYOSIYAMA` key in
`CSecurityAccessAES128` (§4.1) is for runtime ADS/PCS FFD access, not for EPS
reflashing. The EPS reflash seed/key pair is embedded in the calibration file
downloaded from Toyota's TechInfo portal and consumed at runtime by
`CalibrationFile::GetSeedKey()`. It is not hardcoded in any DLL.

`CommandCommon.dll` contains four independent SA implementations. All were
decompiled with the vendored Ghidra CLI against the imported PE (project
`pe_dlls` in `build/pe-project/`). The full algorithms follow.

### 4.1 CSecurityAccessAES128 (TSS 3.0) — ★ matches firmware SA

**Algorithm:** `key_response = AES-128-ECB-encrypt(seed, KEY)`

| Step | Function | Address |
|---|---|---|
| 1. Request seed | `GetSeedData` (`0x10090E30`) → extracts 16 bytes from UDS response (frame ID `0x109`) | |
| 2. Check seed non-zero | All 16 seed bytes must not be `0x00` | |
| 3. Derive key | `~local_50` → inverts the hardcoded obfuscated key bytes | |
| 4. AES encrypt | `FUN_100914B0` (key schedule `0x10091580`, block cipher `0x100918D0`) | |
| 5. Send key | `SndKeyData` (`0x10091180`) → sends 16-byte response (frame ID `0x10A`) | |

The SA subfunctions are `27 03` (request seed) / `27 04` (send key) — SA
level 2 in UDS numbering, matching SEC-APP-001.

**Hardcoded key** (stored bitwise-inverted in the binary at `0x10090C40`):

```text
Obfuscated bytes:  B9 AA B4 AA B2 B0 AD B6 A6 B0 AC B6 A6 BE B2 BE
Inverted (~):       46 55 4B 55 4D 4F 52 49 59 4F 53 49 59 41 4D 41
ASCII:              F U K U M O R I Y O S I Y A M A
```

The AES S-box is at `DAT_100B3B7C` (standard FIPS-197 S-box). The cipher is a
standard AES-128 block encryption: key expansion → AddRoundKey → 9×
(SubBytes/ShiftRows/MixColumns/AddRoundKey) → final round
(SubBytes/ShiftRows/AddRoundKey).

> **Important discrepancy.** This Techstream key `FUKUMORIYOSIYAMA` is NOT the
> same as the firmware bootloader secret `SEED_KEY_SECRET` at CodeFlash `0xBFE8`
> (`f05f36b7...`) or the application secret at `0x20840`. The firmware SA
> construction (SEC-BOOT-003) is a two-stage AES:
> `expected = AES-ENC(AES-DEC(SEED_KEY_SECRET, data_record), ecu_seed)`.
> Techstream's AES128 class does a single-stage:
> `response = AES-ENC(KEY="FUKUMORIYOSIYAMA", seed)`.
>
> This means either (a) Techstream V18.00.008 targets a different ECU
> generation or calibration than the `8965B4512000` Sienna, or (b) the
> `CSecurityAccessAES128` class is used for a subset of ECUs (ADS/PCS) and a
> different path handles the EPS specifically. The CUW's `CalcSeedKey` (§5.1)
> may use the calibration-file-provided key rather than this hardcoded one.
> Resolving this requires a live capture or matching against a known seed/key
> pair from the Sienna EPS.

### 4.2 CSecurityAccess (base / legacy) — custom Feistel cipher

**Algorithm:** 16-round Feistel network with S-box round function

| Step | Function | Address |
|---|---|---|
| 1. Request seed | Uses `CommCacheSndRcv` with frame ID `0xEB`/`0xED` (level 3/0x14) | |
| 2. Load ECU keys | `SetCommonKey(ecu_id, level)` (`0x1008EE30`) | |
| 3. Encrypt seed | `Encrypt` (`0x1008F020`) — 16-round Feistel | |
| 4. Send key | `CommCacheSndRcv` with frame ID `0xEC`/`0xEE` | |

The seed is 8 bytes (two 32-bit big-endian words). The Feistel round function
`F(x)` at `0x1008F080`:

```text
F(x) = (S[x >> 24] + S[(x >> 16) & 0xFF] ^ S[(x >> 8) & 0xFF]) + S[x & 0xFF]
```

where `S` is a 256-entry (×4-byte) lookup table loaded per ECU. The cipher:

```text
for round in 0..15:
    temp = hi ^ round_key[round]
    f    = F(temp)
    hi   = f ^ lo
    lo   = temp
response_hi = whitening_key[0] ^ lo
response_lo = whitening_key[1] ^ hi
```

`SetCommonKey` selects from 7 ECU-specific key sets by `ecu_id` (`0x353`–`0x359`)
and `level` (`3` or `0x14`). Each set has 18 DWORDs (round keys + whitening)
plus 256 DWORDs (S-box table), loaded from `DAT_100B1CE8` through
`DAT_100B3AE0`.

### 4.3 CSecurityAccessCGW_DK — Central Gateway AES-128

**Algorithm:** `key_response = AES-128-ECB-encrypt(seed, KEY)` with session
management wrapper.

Uses its own AES code copy (S-box at `DAT_100B0760` — also standard FIPS-197)
and a separate hardcoded key:

```text
Obfuscated:  A9 DD 1B 66 C7 89 21 B0 EA 0D 1E 99 18 32 DB 39
Inverted:    56 22 E4 99 38 76 DE 4F 15 F2 E1 66 E7 CD 24 C6
```

The wrapper (`CancelSecurity` at `0x10091FB0`) adds:
- `EndDiagSession` → `StartDiagSession` session cycling before SA
- 3 retry attempts with 10-second sleep between
- 2 key-send attempts per seed

### 4.4 CSecurityAccessSUBARU — dual-path (AES or custom)

Two key derivation paths selected by a version field (`this+4`):

**Path A (version == 2):** AES-128-ECB
- `GetConversionKey(ecu_id, b, c)` → looks up a 16-byte key from a 6-entry
  table at `DAT_100B3AE8` (each entry: 4-byte ecu_id + 2 bytes params + 16-byte key)
- `response = AES-128-ECB-encrypt(seed, ~conversion_key)`

### 4.5 CalcSeedKey analysis (CUW reflash cipher)

The CUW's `CalcSeedKey` (at `0x45A1B0` in `Cuw.exe`) is a generic cipher
dispatch function. Decompiled from the Borland Delphi binary via forced
function creation:

```text
CalcSeedKey(cipher_obj, key_material, seed, output):
    copy 64 DWORDs from key_material to local CBytes object
    copy count and flags from key_material+0x104
    for i in 0..3:
        block_ptr = seed + i * 0x10c
        cipher_obj->vtable[4](cipher_obj, local_obj, block_ptr, temp_output)
        log(temp_output)
    copy result to output
```

The actual cipher is a **virtual dispatch** — it depends on which cipher
object the caller passes. Key findings from the binary:

| Evidence | Finding |
|---|---|
| No AES S-box in `Cuw.exe` (findcrypt scan) | AES table is not statically linked |
| `Cuw.exe` Borland exports `@@Caes@Initialize`/`@@Caes@Finalize` | Delphi AES wrapper class present |
| `Cuw.exe` Borland exports `@@Csha256@Initialize`/`@@Csha256@Finalize` | SHA-256 for firmware verification |
| `Cuw.exe` imports `CryptEncrypt`, `CryptDecrypt`, `CryptImportKey` | Windows CryptoAPI (Wincrypt) used for AES |
| No hardcoded SA key in `Cuw.exe` | Key material comes from calibration file at runtime |
| `FUKUMORIYOSIYAMA` not present | CUW does not use the `CommandCommon.dll` AES key |
| `SEED_KEY_SECRET` (`f05f36b7...`) not present | Firmware secret is not embedded in CUW |

findcrypt also discovered **six independent AES-128 implementations** across the
Techstream DLL tree (each with its own static S-box): `CommandCommon.dll`,
`DS2ComNK.dll`, `IT3ACNK.dll`, `IT3UtilityNeoNK.dll`, `UtilityEx2TY.dll`, and
`UtilityExNK2.dll`. `Cuw.exe` is the only crypto-using binary without a static
S-box — it delegates to Windows CryptoAPI via its Borland `Caes` class.

Tracing the callers of each AES implementation recovered **three unique
hardcoded AES-128 keys** across the diagnostic tree:

| Key (hex) | ASCII | DLLs | SA path |
|---|---|---|---|
| `46554B554D4F5249594F534959414D41` | `FUKUMORIYOSIYAMA` | CommandCommon (inverted), UtilityEx2TY (plaintext) | ADS/PCS runtime SA |
| `5622E4993876DE4F15F2E166E7CD24C6` | (binary) | CommandCommon (inverted), DS2ComNK, UtilityExNK2, UtilityEx2TY (all plaintext) | Central Gateway SA |
| `6243566141516E4133664E644467646C` | `bCVaAQnA3fNdDgdl` | IT3UtilityNeoNK only | IT3 Neo utility SA |

None of these keys match the firmware bootloader secret `SEED_KEY_SECRET`
(`f05f36b7...`) or the application secret at `0x20840`. All three serve
non-EPS SA paths (ADS, PCS, Central Gateway, IT3 Neo). The EPS reflash SA
key remains calibration-file-only.

`IT3ACNK.dll` has an AES S-box but no recoverable key — it may use a
different calling convention or serve a non-SA purpose (e.g., certificate
validation).

**EMPS V850E PS2** uses a **static password** SA (key bytes `5A 5A 00 00`,
no seed/key derivation). This is an older EPS generation on V850E, not RH850.

**FOREST/RH850** (`CCanVFORESTFlashWriter`) has no `CollateSeedKey` or
`CalcSeedKey` in its own methods — it only implements `FlashWrite`,
`WriteWithErase`, and `VerifyCompData`. SA is handled by its companion
`PrepareWriter` (separate object in the CUW's two-phase architecture).

The FOREST PrepareWriter presumably calls the generic `CalcSeedKey`
with an AES cipher object backed by Windows CryptoAPI, using key material
from `CalibrationFile::GetSeedKey()`. This would match the firmware
bootloader SA construction (SEC-BOOT-003:
`expected = AES-ENC(AES-DEC(SEED_KEY_SECRET, data_record), ecu_seed)`).

> **Residual uncertainty.** The virtual dispatch through `vtable[4]` cannot
> be statically resolved in the Borland binary without full RTTI analysis.
> The cipher identity (AES-128 vs. custom) is inferred from the CryptoAPI
> import and the firmware match, not directly confirmed by decompilation.
> A live capture or calibration file analysis would confirm definitively.

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
itself**. This is *Layer B* (the per-ECU cryptographic unlock, §5.3). It is
distinct from *Layer A*, the TIS portal's reprogramming-key authorization
(RKS / `ReproKey`), which gates CUW's *permission* to reflash a given VIN but
does not supply the ECU crypto key. The full RKS flow is documented in §5.3;
it is **not** an immobilizer path (this installer contains no immobilizer
code).

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

### 5.3 Reprogramming-key authorization (RKS / TIS portal) — Layer A

The reflash passes through two independent authorization layers that never
exchange material:

| | Layer A — TIS portal (RKS) | Layer B — per-ECU SecurityAccess |
|---|---|---|
| What it gates | CUW's *permission* to reflash this VIN | The ECU's cryptographic unlock |
| Lives in | `Cuw.exe` + .NET RKS components (this section) | Flash writers (§4.5, §5.1) |
| Binding | VIN + GTS license + registration | ECU seed/key (calibration file) |
| Client-side crypto | **None** (regex only) | AES (maps to SEC-BOOT-003) |
| Reaches the ECU? | No | Yes |

Layer B is the cryptographic gate (writer `CalcSeedKey`/`CollateSeedKey`,
§4.5). This section documents Layer A — CUW's online permission gate.

**Components** (CLR-header check + .NET metadata of `CUWAccessRKS.dll` and
`CUWAccessRKSWrapper.dll`; `Cuw.exe` is native x86):

- `Cuw.exe` — orchestrator; runs the `StartRequestReproKey` →
  `RequestingReproKey` → `ImportReproKey` wizard, plus an
  `OfflineImportReproKey` path.
- `CUWAccessRKSWrapper.dll` (.NET; exported to native via C++ name mangling) —
  `SetDataForReproKey`, `ExportDataForReproKey`, `RequestReproKey`,
  `GetWatchingResult`, `ImportReproKey`.
- `CUWAccessRKS.dll` (.NET) — `AccessRKS` class + `DataForReproKey` data class.

**Request data** (`DataForReproKey`, exact fields from .NET metadata):
`IsStored, XVersion, GTSSoftwareID, GTSSoftwareVersion, GTSLicenseKey, VIN,
RequesterKind, KeypairID, SeedValue`.

**XML payload** (exact, from the .NET `#US` string heap):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ReproKeyRequest X-Version="…">
  <TerminalInfo>
    <SoftwareID/><SoftwareVersion/><LicenseKey/>
    <VehicleIdentificationNumber/><RequesterKind/>
  </TerminalInfo>
  <KeypairID/><SeedValue/>
</ReproKeyRequest>
```

**Mechanism (online):** `GetInstanceOfIEMatchingProtectMode` launches/finds an
Internet Explorer via CLSID `0002DF01-0000-0000-C000-000000000046`
(`InternetExplorer.Application`) or `Shell.Application`/`Windows`; `Navigate`
to the TIS page; poll `ReadyState` → `READYSTATE_COMPLETE`; `PasteSeedData`
fills form fields via `document.getElementsByTagName("textarea")` → `.name` /
`.set_value()`; the portal signs server-side (keypair selected by `KeypairID`);
`GetWatchingResult` polls until `result_code == "0"`; `ImportReproKey` scrapes
the returned **`Signature`** textarea and validates it with
`Regex.IsMatch("^[0-9a-zA-Z]+$")`.

**Three authorization modes** (from the English UI source strings in
`locale/en/LC_MESSAGES/default.mo`), chosen at reprogramming start:

- **Online (default):** the reprogramming PC is internet-connected → embedded
  IE → TIS portal → "Signature Request" → download `Signature`. Requires IE
  installed, the account holds *"Signature Request is allowed in used account
  for communication,"* and *"Browser is not closed before downloading Signature."*
- **Offline:** *"Press 'Offline' to perform Signature Request offline"* opens a
  dedicated **"Read Signature (offline)"** page. The procedure string is *"Following
  Signature file retrieve sequence in offline environment, retrieve Signature
  file,"* then *"Press 'Next' to display the Signature file reading dialog."* The
  model is sneaker-net: a **Signature file** is produced by the retrieve sequence
  on a separate internet-connected computer and then read/imported on the
  offline reprogramming PC (`pstrImportFilePath`,
  `CReproKeyServerAccessCtrlr::CheckReproKeyFormat`).
- **Paperwork fallback:** *"If the operation using the computer connected to the
  internet is not possible, process implementation report will be required."*

A separate **Flash Recovery** subsystem (`CFlashRecoveryInfo`, *"A recovery
file for the previous vehicle has been created"*) stores vehicle/ECU-specific
state to resume an interrupted reflash (*"ECU is at risk of being broken if
Flash Recovery is performed for ECU other than the above"*) — unrelated to the
portal `Signature`.

**VIN — six uses (the identity spine):** (1) **mandatory gate** — *"VIN is
required to perform ECU reprogramming"*; (2) **read from the vehicle** via
`CSilVinReader::GetVIN`/`GetVIN_OBD2`, `ER_GetVinCode`; (3) **format-validated** —
must be 17 chars (*"The VIN input does not have 17 characters"*) with a valid
**check digit** (*"Check the check digit of the entered VIN"*); (4) **cross-ECU
consistency** — the `ErrorVINMismatch` page (`StringGrid_ErrorVINMismatch_VINList`)
reads the VIN from every ECU/system and requires agreement (*"Check the stored
VINs in each System"*); (5) **written to the vehicle** — the `RequestWriteVINForRKS`
wizard (*"write a VIN to the vehicle using TD3 or GTS"*) writes the VIN to the
reflashed ECU (anti-theft VIN binding); (6) **sent to the portal** as
`<VehicleIdentificationNumber>` in the `<ReproKeyRequest>` XML. Separately, CUW
must be registered (`ApplicationRegistration`,
`CRegistration::GetGtsExpirationDate`).

**No client-side cryptography.** The `MemberRef` table of `CUWAccessRKS.dll`
contains no `RSACryptoServiceProvider`, no signature-verify call, no
certificate, and no embedded public key. The only check on the returned
`Signature` is the alphanumeric regex. Signing is entirely server-side; the
client trusts the `Signature` purely on receipt through the authenticated IE
session. `KeypairID` is a selector for the portal's signing key, not a client
key.

**Layer A↔B independence (verified):** the `Signature` never reaches any flash
writer — `TCUWCanSecurityVFORESTFlashWriter`, `TCUWCanUnifiedFlashWriter`, and
`TCUWCanCommonPrepareWriter` contain zero `reprokey`/`tagrepro`/`setrepro`
references (ASCII and UTF-16). Layer A is a CUW-side permission token; it does
not touch the ECU, the writer crypto, or any of the three firmware secrets.
This is why none of the firmware secrets appear anywhere in the 6,826-file
installer tree — they live in the calibration file (Layer B), not the installer.

> **Bounded.** The exact generation of `SeedValue` lives in native `Cuw.exe`
> (not decompiled here; CodeGear C++Builder 2007 binary — `CodeGear C++ - Copyright 2007 CodeGear`). Its independence from the ECU
> SA seed is established — the `GetSeed`/`CalcSeedKey` symbols are all in the
> per-ECU-utils context, not the ReproKey path — but the precise source
> (registration seed vs. random nonce) is unconfirmed. Low priority: it never
> reaches the ECU.

> **Correction of an earlier characterization.** This section previously
> (and §8.3) described the online portal as "immobilizer resets and MAC key
> management." That is inaccurate for this installer: there is no immobilizer
> code path, and the portal is the RKS reprogramming-key authorization
> described here. The portal does not supply the ECU crypto key (Layer B's key
> remains in the calibration file). Recorded in `docs/status/CORRECTIONS.md`.

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
| SEC-APP-001: Application SA level 2 with AES-128 | Shape only: `CSecurityAccessAES128` shares the AES-128 / level-03-04 / 16-byte *form*, but its key `FUKUMORIYOSIYAMA` and single-stage construction differ from the EPS two-stage + per-calibration secret (§4.0 resolves the routing: FUKU serves ADS/PCS runtime, not EPS) |
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
| TIS portal RKS flow (`CUWAccessRKS.dll`, §5.3) | OEM reprogramming-key authorization (Layer A) — VIN+license bound, IE-automated, no client crypto; independent of the cal-file crypto key (Layer B). Not immobilizer. |
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
