# Toyota Techstream diagnostic software

> **Scope:** Toyota Techstream V18.00.003 (DENSO) — internal module version
> from `VerApp.ini`/`VerCmd.ini` (dated 2022-11-22 / 2022-12-08). The
> installer filename says V18.00.008, but the "008" is the Flexera IS
> wrapper build number, not the application version. DDB files are dated
> 2022-12-07/08. Model-year coverage extends to 2022 (VehicleData.ini last
> modified 2022/10/07).
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

3. **No direct SecOC runtime interaction, but useful steering-command diagnostic vocabulary.**
   Techstream operates through UDS diagnostics and neither sends nor receives
   SecOC-secured runtime frames. However, the conventional `EMPS_P5.ddb`
   diagnostic corpus contains a master-routed 16-bit `Command Value Torque`
   monitor whose physical-data/unit chain resolves to `Nm`. That is strong
   independent corroboration for the already-recovered authenticated steering-
   command domain, while remaining distinct from direct observation or control
   of CAN `0x2E4`, SecOC verification, or the downstream d/q actuation path.

## 1. Pinned source

The analyzed distribution identifies itself as:

```text
Toyota Techstream
version V18.00.003 (internal module version)
installer PE product version 18.0.8.0
vendor DENSO CORPORATION
installer InstallScript Setup Launcher Unicode (Flexera IS 22.0.330)
app module build date 2022-11-22 (VerApp.ini)
cmd module build date 2022-12-08 (VerCmd.ini)
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
├─ CalibrationFile KindOfECU/ContactType/CPUType selects an encoded
│  parameter INI; TCUWParameterForVC decodes it, then
│  TCUWControlCommPhase reads DLLFileNameForPrepareWrite/FlashWrite and
│  resolves StartPrepareWrite/StartFlashWrite with LoadLibrary/GetProcAddress.
│
├─ Example recovered factory rows:
│   P5-Unified04        → ReproStdPrepare + ReproStdFlash
│   P5-Unified10        → UnifiedPrepare + UnifiedFlashEachArea
│   P5-Unified          → UnifiedPrepare + UnifiedFlash
│   0P5-CAN(SECURITY)302 → P5SecurityPowerTrainPrepare + SecurityVFORESTFlash
│
└─ Exact 8965B4512000 row: unresolved (no .cuw/.cal payload in V18 tree)
```

**Key implication for the Sienna EPS:** the `FUKUMORIYOSIYAMA` key in
`CSecurityAccessAES128` (§4.1) is for runtime ADS/PCS FFD access, not for EPS
reflashing. CUW prepare writers obtain service-auth material through
`CalibrationFile::GetServiceAuthKey()` (and unified prepare also supplies
`GetECUAuthKey()` in the seed request). Unified flash separately obtains
`GetSeedKey()`, `GetNonce()`, and `GetOffsetAddress()` for its predownload DID
writes. Those getters establish calibration-file provenance, but this V18 tree
contains no `.cuw` or `.cal` payload and therefore does not reveal which route
or values apply to `8965B4512000`.

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
> This means either (a) Techstream V18.00.003 targets a different ECU
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
| No ECU-family SA root in `Cuw.exe` | Family-specific credential material comes from the calibration file; the common prepare DLL separately carries a host-side wrapping-key table |
| `FUKUMORIYOSIYAMA` not present | CUW does not use the `CommandCommon.dll` AES key |
| `SEED_KEY_SECRET` (`f05f36b7...`) not present | Firmware secret is not embedded in CUW |

#### 4.5.0 Real legacy case: `T-0087-17` four-byte SecurityAccess

The external `T-0087-17.cuw` specimen closes the older integrated CAN writer
path that precedes the modern SecurityUp construction below. Its validated
`attach.att` selects `KindOfECU=0`, `ContactType=CAN`, `CPUType=70`; the pinned
export tables resolve these to ENG/ECT and Renesas SH72544R (2560-K class),
and decoded `Parameter.ini` has exactly one `0CAN70` row. Crucially that row
sets `FlagToUseCIDGetterAndFlashWriterDLL=0`, so it remains in `Cuw.exe`'s
legacy `CCanFlashWriter` rather than loading a modern prepare/flash DLL pair.

`CCanFlashWriter::CollateSeedKey @ 0x463E80` sends bare `27 01`, expects
`67 01 || seed[4]`, invokes `CalcSeedKey`, sends `27 02 || key[4]`, and expects
`67 02`. The concrete legacy writer initializes round words `A441`, `2172`,
`A421`, `4172` at `0x47F0C4..0x47F112`. `BasicConversion @ 0x45A388` maps
`[s0,s1,s2,s3] -> [s2,s3,s0^round_hi,s1^round_lo]`. Four rounds therefore
simplify exactly to:

```text
key = seed XOR 00 60 60 00
```

This is independent of the calibration software-password handshake. The
`TargetData` fields encode the **old/source** passwords: `0x4B3880` hex-decodes
eight bytes and subtracts output-byte indices `0..7`, then the uint-reader path
(`0x4B3F34` / `0x402380`) parses the resulting eight ASCII hex digits. The
three real targets decode as `302U1000 -> A5CD46B3`, `302U1100 -> AC8C4F0D`,
and `302U1200 -> 727D3713`.

Separately, the selected `0CAN70` row sets `PasswordAddress=001FFF00`,
`ByteOrder=1`; the reconstructed **new** 2-MiB S-record image has `79 EF 38 FF`
at `0x1FFF00`. `CalibArchivedFile::GetPassword @ 0x10002EF0` reads that value,
and `CalibrationFile::GetNewPassword @ 0x10003090` falls back to it because
this descriptor has no `NewPassword` override. Thus `0x79EF38FF` is the
**new-image** software password for `302U1300`, not the first-attempt/source
password and not the `27 02` SecurityAccess key.

`CFlashWriter::SelectRetryPassword @ 0x46CAB0` controls old/new selection at
object `+0x8C`: explicit true selects new; false with status `+0x78 == 7`
toggles; other false cases select old. The status-7 semantic name remains
unclaimed. The consumer is now exact:
`CCanCommonFlashWriter::CheckIDWithWaitOfSFs @ 0x45C86C` sends five raw frames
after the four-byte CAN/J2534 prefix. With `LocationID=0002000100030720`, the
new-password payloads are `00`, `00`, `200701000200`, `0300`, `FF38EF79`; the
last frame is the selected uint32 password in little-endian wire order. This is
a proprietary CheckID exchange, separate from UDS SecurityAccess. This old
two-control design is useful architectural precedent but does not transfer
either value/algorithm to RH850 EPS. Canonical specimen analysis:
[historical T-0087-17 CUW analysis](../history/2026-08/T0087_17_CUW_ANALYSIS_2026-08-22.md).

#### 4.5.1 `CalcSeedKeyForSecurityUp`: exact modern CUW construction

The previously unresolved modern path is implemented by
`TCUWCanCommonPrepareWriter.dll!CCanCommonPrepareWriter::CalcSeedKeyForSecurityUp`
at RVA `0x1310`. It is standard **AES-128-ECB in two stages**. The function
hardcodes selector `0` into a 17-record wrapping-key table and obtains the
32-character hex string:

```text
B45B26D6344FD60E80BC01D63C7584A0
```

It invokes callback `+0x58` first and callback `+0x54` second. Tracing those
callbacks through `Cuw.exe` reaches `CAES::GetDecryptedData` / `CryptDecrypt`
and `CAES::GetEncryptedData` / `CryptEncrypt`, respectively. `CAES::ImportKey`
imports `CALG_AES_128` (`0x660E`), and `CAES::SetEncryptionMode` calls
`CryptSetKeyParam(KP_MODE=4, CRYPT_MODE_ECB=2)`. The resulting algorithm is:

```text
Kwrap = B45B26D6344FD60E80BC01D63C7584A0
Kwork = AES-128-ECB-DEC(Kwrap, ServiceAuthKey[0:16])
key_response = AES-128-ECB-ENC(Kwork, ecu_seed[0:16])
```

The intermediate `Kwork` is formatted as 32 uppercase hex characters with
`%02X` before the second callback, whose string-to-byte wrapper decodes it
back to the same 16 bytes. This formatting round trip does not alter the key.

The CUW text parser also resolves the apparent 64-character-key ambiguity.
`CBytes(string)` performs ordinary two-hex-digits-per-byte conversion; the
calibration parser then copies exactly **16 decoded bytes** into the fixed
`ECUAuthKey`, `ServiceAuthKey`, `SeedKey`, and `Nonce` fields. Thus a
64-character value such as the public `8966312R1100` example is not
nibble-packed: V18 consumes its first 16 decoded bytes on these paths. For that
example:

```text
ServiceAuthKey text:
4247354845484A394D40414D4E505040544749494757475C505C515351635152

consumed ServiceAuthKey:
4247354845484A394D40414D4E505040

Kwork after selector-0 unwrap:
140FF15B66E1F32564BC64C927C3334F
```

Unified prepare sends `27 01 || ECUAuthKey[16]`, so the host construction now
lines up algebraically with the independently recovered RH850 bootloader
construction:

```text
firmware: Kwork = AES-DEC(SEED_KEY_SECRET, ECUAuthKey)
firmware: response = AES-ENC(Kwork, ecu_seed)

host:     Kwork = AES-DEC(Kwrap, ServiceAuthKey)
host:     response = AES-ENC(Kwork, ecu_seed)
```

For a matching ECU/CUW pair, the natural provisioning relation is therefore
that both wrapped credentials decode to the same `Kwork`. Equivalently, a
factory system that knows both roots can produce a pair as
`ECUAuthKey = AES-ENC(SEED_KEY_SECRET, Kwork)` and
`ServiceAuthKey = AES-ENC(Kwrap, Kwork)`. **That provisioning equation is an
architecture inference, not yet a proved Sienna factory transcript**, because
the matching `8965B4512000` CUW is still absent. It does, however, rule out the
need for Techstream to derive the ECU-family root from a family string at
runtime: this exact path receives no family identifier and always selects
wrapping-key record 0. Family separation can instead be embodied in the
factory-provisioned `ECUAuthKey`/`ServiceAuthKey` pair and the root already
inside the ECU.

This also bounds what a purchased matching CUW can reveal. Its credential pair
is sufficient for Techstream-style SecurityAccess without exposing
`SEED_KEY_SECRET`; a known AES plaintext/ciphertext relationship does not make
the 128-bit ECU root invertible.

The executable reproducer is `tools/techstream/cuw_security_up.py`; the raw-PE
proof is `tests/verify_techstream_cuw_security_up.py`.

The reproducible representation-aware census now enumerates all 6,620 files
(670 PE candidates) in the extracted distribution. It finds nine exact AES
S-box byte sequences: seven across the six diagnostic DLL implementations
(`CommandCommon.dll` contains two) and two incidental copies in reporting
libraries. An S-box is implementation evidence, never key evidence. `Cuw.exe`
has no static S-box and delegates its Borland `Caes` path to Windows CryptoAPI.

Constant/reference tracing recovers three previously known 16-byte key values,
but their representations and host mappings are not uniform:

| Key (hex) | ASCII | DLLs | SA path |
|---|---|---|---|
| `46554B554D4F5249594F534959414D41` | `FUKUMORIYOSIYAMA` | CommandCommon (constructed inverted bytes), UtilityEx2TY (plaintext), **IT3ACNK (hex-ASCII, direct `EncryptAds` reference)** | ADS/PCS/IT3 ADS crypto paths |
| `5622E4993876DE4F15F2E166E7CD24C6` | (binary) | CommandCommon (inverted), DS2ComNK, UtilityExNK2, UtilityEx2TY (all plaintext) | Central Gateway SA |
| `6243566141516E4133664E644467646C` | `bCVaAQnA3fNdDgdl` | IT3UtilityNeoNK (direct references); **IT3ACNK (raw at `0x8020`, no direct reference)** | IT3 Neo key use recovered; IT3ACNK role bounded |

None of these keys match the firmware bootloader secret `SEED_KEY_SECRET`
(`f05f36b7...`) or the application secret at `0x20840`. Their recovered uses
are in ADS, PCS, Central Gateway, and IT3 paths. The CUW prepare-writer SA
material is read through calibration-file getters; the missing matching
payload prevents identification of the Sienna value.

The former `IT3ACNK.dll` “no recoverable key” statement is disproved.
`EncryptAds @ RVA 0x2BB0` directly pushes `0x1000834C` at RVA `0x2BE1`;
that object is the 32-character hex encoding of `FUKUMORIYOSIYAMA`. The export
hex-decodes it and passes the resulting 16-byte value into the software block-
cipher helper at RVA `0x3070`. `bCVaAQnA3fNdDgdl` is separately present raw at
file offset/RVA `0x8020`, adjacent to `s2Cjar5er8iwP4Xz`, but neither constant
has a recovered direct code reference in this DLL. Presence is therefore
recorded without promoting either one to an IT3ACNK key.

In `IT3UtilityNeoNK.dll` the constant is live key material rather than
incidental data: the EntranceDLL AES-ECB wrapper loads the NUL-terminated
literal directly (immediate `0x1003A7D4` at `0x10023F3B`, pushed at
`0x10023F5A`) and derives its length with `strlen`. The resulting length is 32
for the full `bCVaAQnA3fNdDgdls2Cjar5er8iwP4Xz` literal (raw bytes verified at
file offset `0x3A7D4`). The key-schedule dispatcher at `0x10024050` maps
lengths 16/24/32 to AES-128/192/256 respectively, so this literal selects the
AES-256 path. The wrapper shifts the input length by four and calls the block
cipher at `0x10024460` once per 16-byte block, establishing ECB composition.

The adjacent tail-handling code was previously mislabeled as a PKCS#7 gate.
`0x10023F26` is only the pre-decrypt `length & 0x0F == 0` block-alignment
check. Optional post-decrypt trimming starts at `0x10024001`: it reads the last
plaintext byte as a count, bounds that count against the plaintext length, and
zeros that many trailing bytes. No loop compares every trailing byte to the
count, so this is **not a strict PKCS#7 padding validator**. The live IT3 Neo
cipher is nevertheless AES-256-ECB keyed by the full 32-character string, not
AES-128 keyed by the 16-character prefix. See CORR-091.

That key also closes the formerly opaque `CONF/*.srp` UtilityNeo scripts. All
18 pinned V18 SRPs decrypt under the recovered AES-256-ECB key; after the
four-byte `48 02 48 02` wrapper the plaintext is BOM-marked UTF-16 XML.
`tools/techstream/decode_srp.py` implements the decoder and
`tests/verify_techstream_srp.py` proves every pinned file decodes plus pins the
literal diagnostic-frame census. The decoded scripts contain service bytes
`10/11/14/21/22/2E/2F/31/3B/50/51/54/61/62/6E/6F/71/7B/7F/A8/E8`; there is no
literal `27`, `34`, `36`, or `37`, and no `SecurityAccess`, `SeedKey`,
`ServiceAuthKey`, or `ECUAuthKey` vocabulary. These SRPs are therefore not a
hidden modern reflash/boot-credential implementation in the pinned corpus.
This is a literal decoded-script closure, not a claim that arbitrary future
UtilityNeo scripts could never synthesize a request byte dynamically.

All twelve IT3ACNK crypto exports are classified and extent-hashed in
`data/generated/techstream_v18/crypto_inventory.json`. Besides `EncryptAds`,
the direct constant consumers are `EncryptSecretKeyC` (`EnerGizerreLayXT`),
`EncryptSecretKeyN` (`WgvbMXxN3pHsSndg`), and TD3 encrypt/decrypt (hex material
at RVA `0x8324`). Version-1/version-2 and six-byte generators remain bounded to
their concrete helper paths; the report does not relabel their table material
as AES keys without data-flow proof.

**EMPS V850E PS2** uses a **static password** SA (key bytes `5A 5A 00 00`,
no seed/key derivation). This is an older EPS generation on V850E, not RH850.

**VFOREST is a writer-family label, not an RH850 proof.** The dynamic
VFOREST flash-writer classes have no `CollateSeedKey` or `CalcSeedKey` in their
own methods; security is supplied by the selected prepare/orchestration route.
A real legacy VFOREST package now proves that this qualifier matters:
`T-0011-21 / 304C21` selects `0P5-CAN86`, `FORESTTypeFlag=1`, and
`FlagToUseCIDGetterAndFlashWriterDLL=0`, so `Cuw.exe` dispatches its integrated
`CCanVFORESTFlashWriter` from the common `CCanFlashWriter::Execute` body. That
common Execute path calls `ChangeReprogrammingForECU @ 0x464254` first and thus
uses the legacy four-byte `27 01/02` SecurityAccess recovered in §4.5.0. By
contrast, the separate dynamic Security-VFOREST family discussed in §4.6 uses
the newer prepare+flash architecture and its calibration-file nonce/seed-key
transfer. Do not transfer the security behavior of one factory family to the
other merely because both contain `VFOREST` in the class name.

Techstream's CPU export for the real package is `CPUType=86 ->
VFOREST_2_0M`; its same export table separately names explicit V850 families.
Independent tuning-tool data places `89663-04C21 / 304C2100` in Toyota Denso
Gen2/newGen D76F0xxx 2-MiB support. The CUW does not establish an exact MCU
suffix or ISA/core, so earlier shorthand `FOREST/RH850` was too broad
(CORR-103).

#### 4.5.2 Real VFOREST/LZF case: `T-0011-21 / 304C21`

External `T-0011-21 - 04C21.cuw` is a 2020–2021 Tacoma GRN305/GRN310,
2GR-FKS ENG&ECT package. It updates `8966304C2000 -> 8966304C2100`; the Toyota
TIS calibration list independently associates that transition with
T-SB-0045-21, `Reduced Crawl Control Functionality`.

The CPU archive `8966304C2100.txt` is ASCII hex rather than S-record. After
whitespace removal and hex decoding it is a 1,329,128-byte stream (SHA-256
`37b832f7899776c27d64483365ac83d9144cf590ba81483320afd5f3313d47db`).
`Cuw.exe:0x43F4CC` calls the format **`LZF-Format data`** and recognizes `5A5600`
and `5A5601`; the VFOREST walker `0x587D8C` closes the binary grammar as:

```text
ZV 00 || storedLength:u16be || raw[storedLength]
ZV 01 || storedLength:u16be || expandedLength:u16be || lzf[storedLength]
```

The real stream has 512 records: 6 raw and 506 compressed. Every record
represents exactly `0x1000` expanded bytes. Standard LZF expansion succeeds for
all 506 compressed records and reconstructs an exact 2-MiB logical image:

```text
length  0x200000
sha256  feb1e7ff00f7268ece3f043a56ac39a33bd22dffbe4f7f23fad1286b53db8e04
```

The image contains `89663-04C21` at `0x100C`. Records 396..510 all expand to
repeated `E203F133`, so **LZF compression is closed but native firmware
interpretation is not**: the two-megabyte representation has not been proven to
be direct plaintext CPU code.

The host writer does not perform that expansion. Integrated VFOREST
`FlashWrite @ 0x587AD4` parses the stored ZV records, then `WriteWithErase @
0x587F5C` / `VerifyCompData @ 0x58827C` feed stored chunks to sender `0x58859C`;
`0x58861A -> 0x5AA540` is a direct copy into the J2534 TX buffer. Therefore the
ECU receives the raw/compressed VFOREST representation. Exact ECU-side LZF and
final storage semantics remain bounded.

This package also closes a route-dependent `PasswordAddress` subtlety. Its
selected row is `PasswordAddress=0000100E`, `ByteOrder=0`; that address indexes
the **hex-decoded ZV archive buffer**, not the LZF-expanded image. Bytes
`FF 0C EF 56` at stream offset `0x100E` become host uint32 password
`0x56EF0CFF` under `GetPassword`, and shared CheckID emits them little-endian as
`FF 0C EF 56`. The old/source `TargetData=3532323734463D4A` decodes to
`0x51040A7C` (wire `7C 0A 04 51`). With
`LocationID=0002000100070720`, the new-password CheckID payloads after the
four-byte CAN/J2534 prefix are `00 / 00 / 200701000200 / 0700 / FF0CEF56`.
The software password is independent of the shared legacy `27` SecurityAccess.

Canonical evidence:
`tools/techstream/inspect_cuw_vforest.py`,
`tests/verify_techstream_cuw_vforest.py`,
`data/generated/techstream_v18/cuw_t0011_21_04c21_specimen.json`, and the
[historical analysis](../history/2026-08/T0011_21_04C21_CUW_ANALYSIS_2026-08-23.md).

The recovered standard and unified prepare writers both derive the `27 02`
response from `CalibrationFile::GetServiceAuthKey()` and the 16-byte ECU seed;
the modern `CalcSeedKeyForSecurityUp` implementation is now recovered exactly
above. Unified prepare additionally prefixes the `27 01` request with
`GetECUAuthKey()[16]`. This proves the host-side cipher and credential flow but
still does not prove the exact Sienna factory row or its calibration-specific
credential values.

### 4.6 SendNonce / SendSeedKey — VFOREST flash-writer key-material transfer

Decompiling the native `CCanCommonFlashWriter` methods resolves the role of
the routines the FOREST writer imports. (Ghidra's first auto-analysis missed
the `.text` cascade in these C++Builder PEs; a fresh import disassembled
cleanly and yielded typed `PASSTHRU_MSG` locals, and the two called IAT
entries were resolved: `[0x100050e8]` = `TCUWJ2534DeviceIF.dll!CJ2534IF::WriteMsgs`,
`[0x10005038]` = `KERNEL32!Sleep`.)

`TCUWCanSecurityVFORESTFlashWriter.dll` imports
`CCanCommonFlashWriter::SendNonceAndSeedKey` (delegates; has no
`CalcSeedKey`/`CollateSeedKey` of its own). These routines are **not
SecurityAccess** — they are the VFOREST **flash key-material transfer**:

| Routine | Addr | Transfers | Block-seq bytes |
|---|---|---|---|
| `SendNonce` | `0x100014c0` | one 16-byte key (arg3), 3 frames | `0x37, 0x38, 0x39` |
| `SendSeedKey` | `0x10001670` | one 16-byte key (arg3), 3 frames | `0x3a, 0x3b, 0x3c` |
| `SendNonceAndSeedKey` | `0x10001820` | two 16-byte keys (arg3 + arg4), 6 frames | `0x37 → 0x3c` |

Each frame is a J2534 `PASSTHRU_MSG` (`ProtocolID=1`, `DataSize` 11; the final
chunk of each key is 9) transmitted via `CJ2534IF::WriteMsgs`, followed by
`Sleep`, and the sequence ends with `ReceiveAck`. The on-wire `Data[]` layout
is `[4-byte nonce prefix][1-byte block-seq][6-byte key chunk]` (a 4-byte chunk
in the final frame of each key).

**The `0x37`–`0x3c` bytes are a per-frame block sequence stored at
`Data[4]`, not UDS service IDs** — they increment monotonically across the
six frames, and `0x39`–`0x3c` are not UDS services at all. This routine
therefore does **not** conflict with firmware SEC-BOOT-003 (UDS `27 01/02`):
it is a different operation entirely. At the VFOREST call site, the two blobs
come from `CalibrationFile::GetNonce(int)` and `GetSeedKey(int)`, verbatim.
Their semantic relationship to any Sienna payload-gate state is unproven
because VFOREST is a different factory route. The SA itself is a separate
prepare-writer operation.

**No AES in the FlashWriter path.** A full tree scan finds the AES forward
S-box (`63 7c 77 7b f2 6b 6f c5`) in zero CUW DLLs/EXEs; it appears only in
the *diagnostic*-app binaries (the six of TMS-008). `Cuw.exe` alone uses
Windows CryptoAPI (`CryptEncrypt`/`CryptDecrypt`/`CryptImportKey`/
`CryptAcquireContextA` from `ADVAPI32.DLL`, independently verified) — the
§4.5 `CalcSeedKey` cipher object. The FlashWriter merely frames and ships key
bytes; it does no cryptography.

> **Resolved (firmware-side, CORR-021).** The Sienna `8965B4512000` bootloader
> speaks **standard UDS only**: its 20-entry service table at `0x8E54` implements
> `0x10/0x11/0x22/0x27/0x28/0x2E/0x31/0x34/0x36/0x37/0x3E/0x85` and maps
> `0x14/0x19/0x23/0x2C/0x2F/0xAB/0xBA/0xBB` to `uds_unsupported_service_handler`
> (`0x69B0`); every other SID returns NRC `0x11` (`uds_service_dispatch` @
> `0x5222`). There is **no proprietary / VFOREST SID handler**, and the
> payload-gate key storage (`DID 0x201` @ `0xFEBF2D08`, `DID 0x202` @
> `0xFEBF2CF8`) is written **only** by `bootloader_did_direct_ram_copy @ 0x6D3A`
> (the `0x2E` path) — sole writer confirmed by x-ref. Therefore the CUW VFOREST
> `SendNonceAndSeedKey` path (`0x37`–`0x3c` proprietary frames) **does not apply
> to the Sienna** — those frames would be rejected (NRC 0x11). The firmware
> therefore constrains any matching Sienna host route to its implemented UDS
> vocabulary. A later byte-level join (CORR-079/TMS-029) sharpens this further:
> the standard writer is **not** compatible despite using familiar UDS SIDs,
> because its request-seed is only `27 01` while this bootloader requires exact
> length `0x12` (`27 01 || 16 bytes`), and its wire RIDs `10F5/10F6` are absent.
> The unified builder sends the required 16-byte `ECUAuthKey`, writes
> calibration-derived values to DIDs `0x0203`, `0x0201`, and `0x0202`, and uses
> the target's `10F0/FF00/10F1/10F2` routine family. TMS-029 now closes the
> remaining writer census: **194/196 factory rows have an exact static mismatch**,
> while the two rows pairing `TCUWCanUnifiedPrepareWriter` with either normal
> UnifiedFlashWriter or UnifiedFlashWriterEachArea are byte-compatible. The
> absent matching calibration payload still prevents choosing between those two
> compatible rows or recovering their actual values. The CUW-side structural
> finding (key-material transfer, not SA; `0x37`–`0x3c` are block-seq bytes, not
> SIDs; `arg3=GetNonce`, `arg4=GetSeedKey`) stands, but its target ECU is not
> `8965B4512000`.

## 5. Calibration Update Wizard (CUW)

The CUW (`Calibration Update Wizard/Cuw.exe`) is the ECU reflashing tool. A
reproducible inventory decodes all 201 parameter INIs into 196 factory rows.
`TCUWControlCommPhase.dll` selects the row from calibration metadata, loads the
named DLLs, and resolves the two phase entry points dynamically. The full
route table, PE identities, pinned method bodies, command templates, and
blocker are in `data/generated/techstream_v18/cuw_writer_inventory.json`.

| Factory identifier | Prepare writer | Flash writer |
|---|---|---|
| `P5-Unified04` | `TCUWCanReproStdPrepareWriter.dll` | `TCUWCanReproStdFlashWriter.dll` |
| `P5-Unified10` | `TCUWCanUnifiedPrepareWriter.dll` | `TCUWCanUnifiedFlashWriterEachArea.dll` |
| `P5-Unified` | `TCUWCanUnifiedPrepareWriter.dll` | `TCUWCanUnifiedFlashWriter.dll` |
| `0P5-CAN(SECURITY)302` | `TCUWP5CanSecurityPowerTrainPrepareWriter.dll` | `TCUWCanSecurityVFORESTFlashWriter.dll` |

These examples prove that “P5,” “unified,” and “VFOREST” are factory choices,
not sufficient identifiers for this EPS. Exact selection requires the missing
matching Sienna `.cuw`/`.cal` payload.

### 5.1 Prepare-write phase

The standard and unified prepare writers expose `StartPrepareWrite` and
execute the pre-flash authentication and mode transition. Their exact UDS
builders recover:

1. **Programming session** — `10 02`, requiring `50 02`.
2. **Standard SecurityAccess** — a **2-byte** `27 01`, require `67 01 || seed[16]`, then
   `27 02 || CalcSeedKey(GetServiceAuthKey(node), seed)` and require `67 02`.
3. **Unified SecurityAccess** — an **18-byte** seed request
   `27 01 || GetECUAuthKey(node)[16]`, then the same derived-key send. This
   request shape exactly matches the tracked Sienna/H boot policy; the standard
   2-byte request does not.
4. **Route-specific transitions** — communication, gateway, and timing steps
   remain selected by the parameter/calibration data.

Timing parameters come from the encoded CUW parameter tables shared across the
controller/writers. `TCUWControlCommPhase.dll` itself consumes only the retry/
IG-off subset; writer DLLs and `Cuw.exe` consume the remaining timing keys. The
parameter model includes:

- `WaitTimeAfterSeedData` — delay between seed request and key send
- `WaitTimeAfterSeedKey` — delay after SA completion
- `SecurityKey` / `SecurityAccessPassword` — embedded key material
- `FlagToCalcKeyLogicForEncrypt` — selects encrypt vs. decrypt key path
- `CANCommunicationSpeedAddress` — CPU-image byte offset used to select bus/speed mode (not a hardware register address)
- `PasswordCheckIDAddress` / `PasswordAddress` — ECU-specific addresses

The SA input comes from `CalibrationFile::GetServiceAuthKey()`; unified prepare
also reads `GetECUAuthKey()`. This is *Layer B* (the per-ECU cryptographic
unlock, §5.3). It is
distinct from *Layer A*, the TIS portal's reprogramming-key authorization
(RKS / `ReproKey`), which gates CUW's *permission* to reflash a given VIN but
does not supply the ECU crypto key. The full RKS flow is documented in §5.3;
it is **not** an immobilizer path (this installer contains no immobilizer
code).

### 5.2 Flash-write phase

The standard writer and both Unified flash variants expose `StartFlashWrite`.
Their exact builders cover:

1. **Predownload data** — standard uses calibration-selected WDBI tables;
   unified sends `2E 02 03 || OffsetAddress[5]`, `2E 02 01 || SeedKey[16]`,
   and `2E 02 02 || Nonce[16]`, requiring the corresponding `6E` responses.
2. **RequestDownload** — standard builds `34 || dataFormat || 44 ||
   address[4] || size[4]`; both Unified variants build
   `34 || dataFormatIdentifier || 46 || addressSpaceByte ||
   (offset[5]+areaAddress) || areaLength`. `dataFormatIdentifier` is bit 3 of
   the first decoded byte of `SecurityProperty2` (§5.2.3); `addressSpaceByte`
   is 1 for area tags 0/1/2 and 0 for tag 3. The EachArea body is independently
   pinned at `0x10001420`; it parses `74`, caps the negotiated block length at
   `0x0FFF`, and subtracts two header bytes; the area Length field bytes are
   transmitted verbatim rather than as a parsed integer (CORR-082).
3. **TransferData / TransferExit** — `36 || counter || data` / `76 || counter`,
   then `37` / `77`.
4. **RoutineControl** — standard writes wire RIDs `10F5`, `FF00`, and `10F6`;
   unified writes `10F0`, `FF00`, `10F1`, and `10F2`, with calibration-derived
   range/hash or offset-adjusted area fields. Earlier `F510/00FF/...` labels
   incorrectly read x86 little-endian immediate values as wire order
   (CORR-079).
5. **ECUReset** — `11 01`, requiring `51 01` (180 ms reset timeout).

For the Sienna bootloader, the unified predownload field names also line up
with the independently recovered payload gate, without implying that the
unified writer is definitely the missing Sienna factory row:

```text
CUW SeedKey[16] -> DID 0x0201
CUW Nonce[16]   -> DID 0x0202

firmware payload key = AES-128-ECB-ENC(PAYLOAD_BUILD_SECRET, DID_0201)
firmware CBC IV      = DID_0202
```

`DID_0202` is also prepended to the encrypted body for the bootloader's CMAC
check. Techstream does **not** need `PAYLOAD_BUILD_SECRET` in this flash path:
it transmits the calibration-provided KDF input/nonce and then transfers an
already-built calibration image. Consequently, a matching CUW gives a known
`SeedKey`/`Nonce`/ciphertext tuple but does not by itself reveal the 128-bit
payload-build root. This is distinct from §4.5.1, where the matching
`ECUAuthKey`/`ServiceAuthKey` pair is enough to execute SecurityAccess without
recovering the ECU's SecurityAccess root.

`SecurityProperty2` is separate from both of these KDFs. It is not imported by
`TCUWCanCommonPrepareWriter.dll`, so it cannot select or alter the recovered
`CalcSeedKeyForSecurityUp` construction. It is read by the unified **flash**
writers and passed into their transfer/image-format orchestration; those DLLs
have no `CryptEncrypt`/`CryptDecrypt`/`CryptImportKey` edge. For the public
`8966312R1100` example, `SecurityProperty2=98` is therefore flash metadata, not
a selector for the SecurityAccess wrapping key or the firmware payload-build
root. Its exact transfer semantics are now pinned: `CBytes(const char*)`
hex-decodes the string, and bit 3 of the first decoded byte becomes the
Unified RequestDownload `dataFormatIdentifier` (public example `98` → byte
`0x98` → 1). The decoded byte is key-material semantics, not a character
code; do not reinterpret the ASCII character value (CORR-083).

ECU-specific flash writers include:
`TCUWCanReproStdFlashWriter` (standard CAN), `TCUWCanUnifiedFlashWriter`
(unified), `TCUWCanSecurityVFORESTFlashWriter` (Security-VFOREST family),
`TCUWCanPowerTrainFlashWriter`, and variants for airbag, chassis, body, HINO,
M16C, MMC, PSA, and SBR ECUs.

The local V18 distribution contains zero `.cuw` and zero `.cal` files. It can
therefore prove the factory mechanism and request builders, but not the exact
`8965B4512000` factory identifier, keys/nonces, address ranges, data-format
values, or routine choices.

#### 5.2.1 Calibration target-integrity metadata — separate `DigitalSignature` field

A deeper pass over `Cuw.exe` recovers a second signature-bearing structure that
must not be conflated with the TIS/RKS `Signature` in §5.3. The logical-block
parser `FUN_0040B63C` (3045 bytes) walks up to 16 block records and parses
`NewCID`, `SecurityProperty2`, `Nonce`, `ReproMethod`, `P4ServerMaxTime`, and
`NumberOfTargets`. For each target it invokes `FUN_0040C224` six times, once for
each of these target families:

- `ReproData`;
- `EraseAndReproRoutine`;
- `DeltaReproData`;
- `DeltaEraseAndReproRoutine`;
- `CompressionReproData`;
- `CompressionEraseAndReproRoutine`.

The shared target parser reads five named fields in order:

```text
StartAddress
Length
CRC
CMAC
DigitalSignature
```

The six calls are at `0x40BFEA`, `0x40C03E`, `0x40C092`, `0x40C0E6`,
`0x40C13A`, and `0x40C18E`; the helper begins at `0x40C224`. The downstream
`TCUWCalibrationFile.dll` model is now recovered exactly enough to remove the
old ambiguity. `CLogicalBlockAreaInfo` is `0x8C` bytes and consists of five
consecutive `0x1C` MSVC-string objects:

```text
+0x00 StartAddress
+0x1C Length
+0x38 CRC
+0x54 CMAC
+0x70 DigitalSignature
```

`CLogicalBlockInfo` is `0x39C` bytes. It begins with a target-array pointer/count
and embeds six `CLogicalBlockAreaInfo` objects at `+0x008/+0x094/+0x120/+0x1AC/
+0x238/+0x2C4`, corresponding in order to ReproData, EraseAndReproRoutine,
DeltaReproData, DeltaEraseAndReproRoutine, CompressionReproData, and
CompressionEraseAndReproRoutine. The source logical-block record is `0x98`
bytes. `TargetData` is `0x20` bytes. These layouts are independently closed by
the import/copy constructors, assignment operators, destructor, and
`ImportDataForLogicalBlock*` methods rather than inferred from field spacing.

The standard flash writer also closes the **ECU-facing consumer**. Its
byte-pinned RoutineControl builder at `0x100025F0` receives one of those exact
area objects and constructs `31 01 || RID || 44 || StartAddress || Length ||
integrity`. It uses wire RIDs `10F5`, `FF00`, and `10F6`. A nonempty CRC is carried
with an explicit four-byte selector/length form; `RequiredSpecReproVer03`
selects a `00 10 || CMAC` form, while the alternate required-spec path selects
`01 00 || DigitalSignature`. The caller at `0x10002A50` routes the whole,
delta, and compression target families through the matching area objects and
expects `71 01 || RID`. Thus `DigitalSignature` is not merely dormant metadata
in the standard package-download route: CUW can transmit it to the ECU as part
of a RoutineControl request. The signer/private-key/verification algorithm and
whether a particular EPS calibration selects that branch remain unproven.

The recovered Unified path is structurally different from standard. Normal
Unified and UnifiedEachArea both use `10F0/10F1/10F2/FF00`, derive the effective
five-byte address by adding calibration `OffsetAddress` to an area start, and
append the area length/range from the `CFileHeaderInfo`-shape area object. The
EachArea routine builder at `0x10001F80` reads the two consecutive string fields
at `+0x00/+0x1C`, then constructs `31 01 || RID || 45 || adjustedAddress[5] ||
length`; its RequestDownload path uses the same area start/length pair. This is
separate from the standard `CLogicalBlockAreaInfo` CRC/CMAC/DigitalSignature
request builder. Because TMS-029 now rejects every non-Unified route, the
signature-bearing standard target-integrity transfer is **not part of either
statically compatible Sienna/H route**. Schema-v2 of
`cuw_calibration_schema.json` records this field-flow/target-relevance result for
all 32 route pairs: standard has the exact CRC/CMAC/DigitalSignature transfer,
the two compatible Unified rows have the separate area start/length path, and
the remaining 29 route pairs are target-rejected before any target-integrity
semantic can affect the Sienna/H disposition. No static edge joins either
integrity path to the independent TIS/RKS permission token in §5.3.

The same pass recovers the calibration metadata object grammar. `Cuw.exe`
initializes an embedded descriptor named **`attach.att`**, imports the Win32
profile APIs, and its parser at `0x00404708` reads the exact vehicle/node/
logical-block vocabulary including `ECUAuthKey`, `ServiceAuthKey`, `SeedKey`,
`Nonce`, `OffsetAddress`, `SecurityProperty2`, file/range/data-format fields,
and the integrity fields above. `CalibrationFile::ImportData @ 0x10004320`
pins the top-level array/count geometry and object strides. The generated schema
is `data/generated/techstream_v18/cuw_calibration_schema.json`; an extracted
descriptor can be losslessly normalized with
`tools/techstream/parse_cuw_attach.py`, which deliberately preserves unknown
keys for a future newer calibration.

The outer `.cuw` envelope framing is statically recovered from `Cuw.exe`
(container parser `0x413BF0`, first-member reader `0x412F9C`, zlib-CRC32
helper `0x412C98`) and is now independently validated by the external
`T-0087-17.cuw` specimen:
`magic "\0CALIBRATION\0"[13] || formatType:u8 || crc32:u32BE ||
totalSize:u32BE || { nameLen:u16BE || name || payloadLen:u32BE ||
payloadCrc32:u32BE || payload } || format-specific tail`. The type byte is
membership-checked against an 11-entry table
(`{01,03,04,05,06,07,08,09,65,66,67}`; only `{01,03,04}` are additionally
`gbytFORMAT_VERSIONS`). Stored CRC32 covers `[18, declaredTotal)`, and parsed
bytes must equal the declared total.

The specimen specifically closes **Format Version 4**. Static code at
`0x413E74` reads a one-byte CPU-image count; the loop at `0x413F42` dispatches
the same member reader through vtable slot `0x5D5E30 -> 0x412F9C`. Therefore
the Version-4 tail is `imageCount:u8 || member[imageCount]`. The real package
contains one `302U1300.txt` member (`5,111,858` bytes, CRC32 `5CACED62`) and
consumes its declared tail exactly. Its payload is a valid S-record stream with
65,536 S2 records covering `0x000000..0x1FFFFF`, S8 entry `0x014B00`, and
reconstructed-image SHA-256
`2b2db1d9766405d74706e56fc1baea544e2a00bbaf09ee36f5994f1617852735`.
The image contains 70,726 aligned `A1DFE103` words, including complete 64-KiB
regions `0x050000..0x05FFFF` and `0x1E0000..0x1EFFFF`. The selected legacy
S-record parser/materializer (`0x4A9A9C`/`0x4AB2D4`) and sender `0x45C700`
pass the materialized image bytes unchanged into the J2534 transmit path; there
is no host-side coding transform on this route. The semantic meaning or
ECU-side interpretation of that encoded-looking representation remains bounded.
Toyota bulletin T-SB-0336-17 independently corroborates the package's
2015–2016 Corolla / 2ZR-FAE / CVT-Gate Main ECM transition from the three
`302U1x00` calibrations to `302U1300`.

`tools/techstream/parse_cuw_container.py` now decodes/validates this Version-4
archive grammar; `tools/techstream/inspect_cuw_legacy.py` adds S-record, route,
legacy-password, and four-byte SecurityAccess interpretation. Tail layouts for
other format values remain unclaimed. Most importantly, this old engine package
does **not** satisfy the still-open target-specific need for a matching modern
Sienna/H EPS package and its actual `ECUAuthKey`/`ServiceAuthKey`/`SeedKey`/
`Nonce`/range values. `tests/verify_techstream_cuw_calibration_schema.py` and
`tests/verify_techstream_cuw_legacy.py` pin both the static grammar and specimen
join.

#### 5.2.2 Complete decoded-route writer census

The decoded parameter corpus is now exhaustively joined to the writer modules it
can select. All 201 encoded INIs decode to 196 factory rows and reference exactly
**47 writer DLLs present in the installation: 22 prepare writers and 25 flash
writers**. `data/generated/techstream_v18/cuw_writer_family_matrix.json` records,
for every one of those 47 modules, its SHA-256, route/factory provenance, exports,
imported `CalibrationFile` getters, imported common writer/transport operations,
and bounded protocol-family tags.

The writer matrix deliberately keeps **imports/tags structural**: a dependency
such as `GetNonce`, `CalcSeedKeyForSecurityUp`, or a common flash helper still
is not promoted to wire semantics merely because it is imported. Exact target
classification lives at the **prepare+flash route-pair** level in
`cuw_writer_protocol_grammar.json`, and schema-v2 of the matrix mirrors those
route dispositions in `target_route_dispositions`.

The one major shared implementation behind the specialized writers is now
recovered directly rather than left as an import-name hint. **15 of the 25 flash
writer modules import `TCUWCanCommonFlashWriter.dll`**, whose 19 exported
protocol bodies are all byte-hash-pinned in the route-grammar artifact. This is
a proprietary command protocol after the caller-supplied CAN-address prefix,
not UDS service numbering:

| Common-flash operation | Recovered command grammar |
|---|---|
| ack | exact 5-byte response, command/status byte `0x3C` |
| finish check / finish | `0x3E` / `0x80` |
| nonce / seed-key material | nonce `0x37→0x38→0x39`; seed-key `0x3A→0x3B→0x3C` (6/6/4-byte chunks) |
| memory/status/CPU | memory info `0x76` then fallback `0x75`; status `0x50`; next CPU `0x65` |
| blank / erase | `0x35/0x36`; `0x25/0x26` for short/extended range |
| write | `0x41` block start, `0x45` continuation; parameter-selected 0x100/0x80/0x20-byte data classes |
| in-verify / verify | `0x47/0x48`; `0x15/0x16`; alternate verifier `0x18` with 0x80-byte chunks |
| falsify check | `0x47`, then status polling |

The same helper bodies recover the corresponding status-poll waits
(`WaitTimeBeforeStatusCheckForBlankCheck/EraseBlock/WriteBlock/InVerify/Verify`).
That common grammar covers the body/chassis/powertrain/security/M16C/VFOREST
flash families that delegate to it. The remaining direct flash families
(MMC, SBR, HINO, PSA, ReproStd, Unified, Ethernet variants) are represented by
their own raw template/decompilation evidence. Thus the family census no longer
uses “imports common flash helper” as a substitute for the shared wire grammar.

A focused Ghidra pass closes every class that the first census left bounded:

| Family / former residue | Exact decisive grammar | Sienna/H disposition |
|---|---|---|
| P5 PowerTrain | bare `27 01`, 4-byte seed/key | rejected: target requires 18-byte request-seed |
| P4/P5 PowerTrain | bare `27 01`, 4-byte seed/key; parameter-timed | rejected: same exact-length mismatch |
| P5 BodyMicon | bare `27 01`, 6-byte seed/key | rejected: same exact-length mismatch |
| P5 Solar | bare `27 01`, 4-byte seed/key | rejected: same exact-length mismatch |
| SecurityChassisShrink | `27 01 || selector[1] || ECUAuthKey[16]` | rejected: 19-byte application request vs exact 18-byte target policy |
| MMC | `27 41/42`; RIDs `0301/0304` plus `FF00`; `11 81` | rejected: unsupported SA subfunctions/RIDs |
| CentralGW + P4 BodyFlash | prepare host callback; legacy common-flash raw framing, finish byte `0x80` | rejected: not target UDS boot grammar |
| UnifiedEachArea | `0203→0201→0202`; `34 .. 46 ..`; RIDs `10F0/FF00/10F1/10F2`; `11 01` | **byte-compatible** |

Together with the previously exact families, this produces the final static
census: **194 rejected rows + 2 byte-compatible Unified rows, zero unresolved or
bounded route rows**. The generated route records also carry the complete
factory-row timing/retry profile for 12 high-value parameters plus recovered UDS
reset templates; this preserves timing/retry/reset behavior per route rather than
leaving it as prose. The surviving pair differs only in normal-vs-per-area
Unified flash orchestration and both have blank legacy seed-delay fields,
`IGOffRetriableFlag=1`, and `11 01` reset. Static V18 cannot choose which one
Toyota selected for `8965B4512000`/`8965H1202000`; that requires the matching
calibration package or a retained live CUW session.

The matrix and its independent decoder/import verifier are generated by
`tools/techstream/generate_cuw_writer_family_matrix.py` and
`tests/verify_techstream_cuw_writer_family_matrix.py`; the exact second-stage
body pins and route classifier are generated by
`tools/techstream/generate_cuw_writer_protocol_grammar.py` and verified by
`tests/verify_techstream_cuw_writer_protocol_grammar.py`.

#### 5.2.3 Surviving-Unified closure: exact per-route image/area sequencing

The two byte-compatible Unified rows are now closed at body level
(`unified_survivor_closure` in the route-grammar artifact; all bodies
sha-pinned in the generator and re-hashed by the test):

- **Normal `TCUWCanUnifiedFlashWriter.dll`** — per node CPU image:
  predownload `2E 02 03‖OffsetAddress[5]` → `2E 02 01‖SeedKey[16]` →
  `2E 02 02‖Nonce[16]` once, one `10F0` (tag 0) pair, then per area
  `FF00` (tag 1) always, `10F1` (tag 2) and `10F2` (tag 3) pairs;
  last CPU image stores `GetWakeUpTimeAfterReset`, `StopSyncPeriodicMsg`,
  `11 01` (180 ms) and raw J2534 tail frames.
- **EachArea `TCUWCanUnifiedFlashWriterEachArea.dll`** — predownload is
  **re-sent inside the per-area loop** before every area group; tag-0 `10F0`
  and tag-2 `10F1` pairs are conditional on non-empty area tables
  (`+0xB4`/`+0x90`), tag-1 `FF00` and tag-3 `10F2` always; area objects are
  stride-`0x38` `{std::string StartAddress@+0, Length@+0x1C}`.
- **`CUnifiedUtils::MakeSendData @ 0x10002c40`** copies the prebuilt
  S-format payload bytes (`typSFormatRecord`, stride `0x10`) verbatim into the
  `36` block; it performs **no** host encryption, compression, or hash
  transform, and neither surviving writer imports any CRC/CMAC/signature or
  `GetReproMethod`/`GetDataFormat` facility — host-side image verification for
  the surviving routes is none; integrity is ECU-internal.
- **`CUnifiedUtils` SecurityAccess cipher** (`CalcSeedKey @ 0x10002b50`) is
  the same two-stage AES-128-ECB construction as §4.5.1, resolving wrap keys
  through a 17-record selector table at `0x100051b0` (stride `0x208`, selector
  dword `@+0x204`). Record 0 is the selector-0 key shared with the common
  prepare writer; **records 1–16 are present in the shipped binary but not
  proven reachable by any pinned V18 caller** — both known callers hardcode
  selector 0 (`6a 00` at `0x10002b6e`). No type-table or unused-record meaning
  is claimed.

The last-CPU-image tail of the EachArea writer additionally emits two raw
J2534 frames after reset — CAN `0x777‖10 81` (len 6) and `0x7F7‖FE 10 81`
(len 7, TxFlag `0x80`) — preserved as capture observables; their target-side
interpretation is bounded.

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

The native→managed layout is now recovered end-to-end. Native request storage
starts at `CReproKeyServerAccessCtrlr + 0x215`; the wrapper copies these exact
offsets into the managed fields:

| Managed field | Wrapper offset | Native object offset | Native source |
|---|---:|---:|---|
| `XVersion` | `+00` | `+215` | RKS client-config object `+00` |
| `GTSSoftwareID` | `+03` | `+218` | config `+04` |
| `GTSSoftwareVersion` | `+24` | `+239` | config `+08` |
| `GTSLicenseKey` | `+2E` | `+243` | config `+0C/+10`, selected by host mode |
| `VIN` | `+5D` | `+272` | current-vehicle object `+7C` |
| `RequesterKind` | `+6F` | `+284` | config `+18` |
| `KeypairID` | `+71` | `+286` | config `+1C` |
| `SeedValue` | `+78` | `+28D` | 16-byte callback argument, rendered as 32 uppercase hex chars |

`CUWAccessRKSWrapper.SetDataForReproKey` sets `IsStored=true` immediately
before copying those fields. This is a managed request-data-validity flag, not
evidence that a previously issued server token is cached or reusable. The
config object is the `0x38`-byte structure returned by `FUN_0043DFBC`; its
accessors at `43F034/3C/48/54/60/6C/78` expose the offsets above. The request
builder `FUN_0049BCFE` obtains that object, reads VIN from the current vehicle,
then passes the native request block to `FUN_0047FB24`.

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
  `CReproKeyServerAccessCtrlr::CheckReproKeyFormat`). The native format checker
  at `0x0047FFF0` requires the imported token length to be exactly `0x200`
  characters (`cmp edx,0x200` at `0x00480021`). Together with the managed
  alphanumeric regex below, this pins a fixed-width 512-character client format;
  it does not identify the server-side signing primitive.
- **Paperwork fallback:** *"If the operation using the computer connected to the
  internet is not possible, process implementation report will be required."*

The native wizard state machine is also closed at the client boundary. Delphi's
method table binds `Button_StartRequestReproKey_NextClick` to `0x49C62C`, the
Offline button to `0x49C83C`, online `ImportReproKey` Next to `0x49C2C0`, and
offline `ImportReproKey` Next to `0x49CD24`. Both file-reading pages converge on
shared importer `0x49C304`; the pasted-signature page at `0x49D3BA` uses the
same fixed-width checker. Success writes RKS controller state `1`, failure/
abort writes `2`, and the network/signature Retry buttons use their separate UI
state value `4`. Empty VIN branches to the `S701-94` VIN-required page.

The offline path is not a second signing algorithm. `0x49C83C -> 0x47FD5C ->
0x49D250` exports the same request XML to a file/path and later rejoins the
shared Signature importer. Managed `ImportReproKey` requires an XML
`<Signature>` element, length exactly `0x200`, then the alphanumeric regex.
The native checker independently enforces the same fixed width.

One earlier open policy question can now be narrowed substantially. The shipped
regional UI catalogs explicitly instruct the technician to *refer to the repair
manual whether the target vehicle needs Signature Request* and, when the
browser/.NET prerequisite path is unavailable, to choose **No** to continue
reprogramming if Signature Request is not necessary. No RKS-required field is
present in the recovered `attach.att` calibration schema and no RKS token reaches
a flash writer. Therefore V18 does **not** support treating RKS as universally
mandatory for every ECU/EPS reflash. What remains external is the Toyota policy
for a particular target/region/calibration, not another hidden client-side
cryptographic predicate.

`SeedValue` is fully closed inside the native client. The reprogram flow
registers `FUN_0049BCF8/FUN_0049BCFE` as a callback when host flow mode is `3`;
the callback receives the exact 16-byte seed returned by the Central Gateway
`27 21` SecurityAccess request, and the request builder performs no RNG/time/hash
derivation before hex serialization. The 512-character RKS response is later
decoded to 256 bytes and returned to the Central Gateway as `27 22 || token[256]`.
This is gateway-facing Layer-A authorization and remains separate from the EPS
flash-writer Layer-B SecurityAccess path.

Canonical generated state artifact:
`data/generated/techstream_v18/rks_client_state.json`; verifier:
`tests/verify_techstream_rks_client_state.py`.

A separate **Flash Recovery** subsystem stores vehicle/ECU-specific state to
resume an interrupted reflash. Its persistence schema, retry timing, and later
capture implications are canonical in §5.4; it is unrelated to the portal
`Signature`.

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
certificate, and no embedded public key. Client-side validation is format-only:
the managed layer requires `^[0-9a-zA-Z]+$`, and native
`CReproKeyServerAccessCtrlr::CheckReproKeyFormat` requires exactly 512
characters. Signing is entirely server-side; the client trusts the `Signature`
purely on receipt through the authenticated IE session. `KeypairID` is a
selector for the portal's signing key, not a client key. The fixed width is
compatible with several possible server token/signature encodings and is not
sufficient evidence to name one.

**Layer A↔B independence (verified):** the `Signature` never reaches any flash
writer — `TCUWCanSecurityVFORESTFlashWriter`, `TCUWCanUnifiedFlashWriter`, and
`TCUWCanCommonPrepareWriter` contain zero `reprokey`/`tagrepro`/`setrepro`
references (ASCII and UTF-16). Layer A is nevertheless vehicle-facing: CUW
decodes the server token and returns its 256 bytes to the Central Gateway in
`27 22`. That gateway authorization does not enter the EPS flash-writer crypto
or any of the three firmware-secret paths. The firmware secrets remain
calibration-file Layer-B material, not installer-resident RKS material.

**`SeedValue` boundary (native path now recovered).**
`CUWAccessRKSWrapper.SetDataForReproKey` maps native request-buffer offset
`+0x78` to managed `mstrSeedValue`. Native `Cuw.exe` request builder
`FUN_0049BCFE` preserves its second argument, passes it as the fourth argument
to `FUN_0047FB24`, and that routine copies **exactly 16 input bytes** before
`FUN_0041A01C` renders them as **32 uppercase hexadecimal characters plus
NUL** into the `+0x78` field. Thus `SeedValue` is not generated by the managed
RKS layer and there is no RNG/time transform in the request-construction edge;
it is a textual serialization of a pre-existing 16-byte native input.

The former "one edge upstream" boundary is now closed inside `Cuw.exe`: the
whole SeedValue producer is static code (CORR-084). The chain is
`CCentralGWModeChanger::CollateSeedKeyForP5CentralGW @ 0x590320` → CentralGW
P5-CAN SecurityAccess **`27 21`** (expected `67 21`; NRC gate `7F 27` with
`13/35/36`) → 16-byte response seed copied at `0x5903F6` → seed bridge
`0x5907EC` into global `0x629CDC` → callback invoker thunk `0x590858`
(`call [0x629CD0]`) → registered request-builder callback `0x49BCF8` → hex
serialization into the `ReproKeyRequest` SeedValue. The returned 512-char
portal token is stored by `0x48013C` and **256 decoded bytes are transmitted
as `27 22 || token[256]`** (request length `0x107`, expected `67 22`). The
request-field provenance for `RequesterKind`/`KeypairID` is the shipped
obfuscated `Ini/RKS.ini` `[ReproKeyRequest]` (per-nibble ASCII `0x20+4n`,
loader `0x43E0C0`). What remains external is only the live gateway seed value
and the server-side signing algorithm/private key. All anchors, call targets,
and strings are raw-byte asserted in `verify_techstream_rks_client_state.py`.

> **Correction of an earlier characterization.** This section previously
> (and §8.3) described the online portal as "immobilizer resets and MAC key
> management." That is inaccurate for this installer: there is no immobilizer
> code path, and the portal is the RKS reprogramming-key authorization
> described here. The portal does not supply the ECU crypto key (Layer B's key
> remains in the calibration file). Recorded in `docs/status/CORRECTIONS.md`.


### 5.4 Timing, retry, reconnect, and Flash Recovery

The V18 CUW timing model is now statically closed far enough to make a later
GTS+/J2534 session a measurement exercise rather than exploratory reverse
engineering. The generated evidence is
`data/generated/techstream_v18/cuw_timing_recovery.json`; verifier:
`tests/verify_techstream_cuw_timing_recovery.py`.

#### 5.4.1 Two parameter tables and who consumes them

The encoded CUW corpus contains two distinct parameter layers:

- **196 factory/protocol rows** in the per-factory INIs. Their 85-column schema
  carries writer-facing timing/retry fields such as `WaitTimeAfterSeedData`,
  `WaitTimeAfterSeedKey`, `WaitTimeAfterReprogrammingMode`, status-poll waits,
  `PrepareRetryFlag`, `IGOffRetriableFlag`, and transport timeout fields.
- **380 host/system rows** in `Ini/Parameter.ini`. Its 30-column schema carries
  host-side IG/battery/gateway behavior such as `WaitTimeForIGOFFON`,
  `WaitTimeAfterIGOn`, `FlagToCancelAutomaticIGOFF`,
  `FlagToDoIGOFFONAtCPUTypeChange`, and
  `FlagToChangeToReprogGWModeForCentralGW`.

The important attribution correction is that `TCUWControlCommPhase.dll` is not
the generic owner of every timing key merely because it contains the strings.
Raw absolute-reference checks show **no executable reference** there to
`WaitTimeAfterSeedData` or `WaitTimeAfterSeedKey`. The P4/P5 prepare family does
reference those keys at `0x100019F0` / `0x10001F2F`. The controller instead
references the retry subset (`PrepareRetryFlag`, `IGOffRetriableFlag`, and
`ReceiveTimeoutBeforePrepareRetry`) and coordinates transport/host callbacks.

The V18 distributions are useful route fingerprints. `WaitTimeAfterSeedData`
and `WaitTimeAfterSeedKey` are both exactly `100 ms` for 162/196 factory rows
and blank for 34 modern rows. `IGOffRetriableFlag=1` on 175/196 rows;
`PrepareRetryFlag=1` on only 13. `WaitTimeAfterReprogrammingMode` is mostly
500/1500 ms. On the system side, `WaitTimeForIGOFFON` is 10 s on 368/380 rows,
30 s on 10, and 15 s on 2; `WaitTimeAfterIGOn` is usually 6000 ms (277/380) but
varies by family. The three modern EPS host rows `13CAN161`, `13CAN213`, and
`13CAN(SECURITY)213` all use the newer CID/flash-writer route flag.

Recovered code semantics sharpen those tables:

- `TCUWP4P5CanPowerTrainPrepareWriter.dll` uses the two seed timing keys around
  its SecurityAccess seed/key phases. Modern ReproStd/Unified prepare paths do
  not consume those keys, so a later Unified transcript must not be forced into
  the legacy 100-ms assumption.
- `TCUWControlCommPhase.dll` `retry_driver @ 0x10007750` owns the retry/reconnect
  loop. It reads the IG-off/retry fields, can apply
  `ReceiveTimeoutBeforePrepareRetry`, invokes the writer retry entry, and has a
  hardcoded 5000-ms post-completion wait in the confirmed-flash path.
- `reconnect_transport @ 0x10002090` distinguishes normal CAN `Connect(6)` from
  the Ethernet `Connect0500(0x800f)` path.
- Security-VFOREST `0x10001200` consumes
  `WaitTimeAfterReprogrammingMode`/`WaitTimeBetweenSF` around its
  mode-change/status-poll machinery; that is comparative route evidence only
  because the tracked Sienna bootloader rejects VFOREST framing.
- `TCUWCanCommonPrepareWriter::GetBusTypeFromCPUImage @ 0x10001630` proves
  `CANCommunicationSpeedAddress` is a **CPU-image byte location used to choose a
  bus/speed mode**, not a hardware baud-rate register address.

All of those bodies are SHA-pinned in the generated artifact so the decompiled
semantics cannot silently drift from the installed V18 binaries.

#### 5.4.2 Flash Recovery persistence and resume state

`CFlashRecoveryInfo` persists interrupted jobs under
`Save/RecoveryInfo.ini`, section `RecoveryInfo`. The exact key block begins at
`Cuw.exe` VA `0x005D8D10` and includes:

| State | Object offset | Role |
|---|---:|---|
| `SavedCalibrationFilePath` | `+0x00` | saved calibration payload used by recovery |
| `SelectedJ2534Device` | `+0x04` | pass-thru-device identity |
| `CID[]` | `+0x18` | calibration IDs for the interrupted job |
| `VIN` | `+0x28` | vehicle identity |
| `CIDNode[]` | `+0x40` | per-node CIDs |
| `ReproCheckResult` | `+0x50` | prior repro/RKS-check state |
| `IsCentralGWExist` | `+0x51` | topology state |
| `WriteCpuIndex` | `+0x54` | CPU-image resume index |
| `Writing` | `+0x58` | reprogramming in progress |
| `UseNewSoftwarePassword` | `+0x59` | retry/password-generation state |
| `WritingEndBlock` | `+0x5A` | current area/block completion state |
| `PassThruErrorCode` | `+0x74` | last J2534 error |
| `AssyNo[]` | `+0x88` | ECU identity list shown by recovery UI |
| update-availability flags | `+0xB8` | per-ECU update status |

Internal state also keeps a resume-armed byte at `+0x5B`, recovery-disabled at
`+0x5C`, a backup path at `+0x60`, persistence-active at `+0x6C`, and the INI
path at `+0x70`.

The lifecycle is recovered and byte-pinned: `0x00429FF4` creates/activates the
recovery record; `0x0042A0BC` loads it; setters at `0x0042ECBC..0x0042EDC8`
persist progress; `0x0042EEDC` writes the record; `0x0042EDF0` restores a
backup; `0x0044F568` performs startup recovery eligibility/UI handling; and
`0x0042DE54` deletes both the saved calibration payload and recovery INI on
final success/deletion. `WriteCpuIndex` chooses the CPU-image restart point;
`Writing`, `WritingEndBlock`, and `UseNewSoftwarePassword` constrain the resumed
phase.

The persisted VIN plus AssyNo/CID lists provide a strong **procedural identity
binding** and the UI warns against recovering a different vehicle. No
cryptographic binding is recovered in this client path; do not describe the
recovery file as cryptographically vehicle-bound.

#### 5.4.3 Capture-ready power-cycle observables

The DDB pass for this task was deliberately targeted rather than another broad
census. Exact NA `EMPS_P5`/`EMPS2_P5` section-62 rows identify ordinary
monitor/Data IDs that should be timestamped during any CUW retry/recovery run:

| Data ID | OEM name |
|---:|---|
| `0016..0019` | `Status of Vehicle Power` IGP/IGR variants |
| `0033` / `0034` / `0036` | `IG Power Supply` / `PIG Power Supply` / `Power Source` |
| `0421` / `0422` | System-2 IG/PIG supply |
| `07D1` / `07D2` | backup IG/PIG supply inputs |
| `26AC` | `Key Cycle` |
| `26AD`, `26C1`, `26C3` | `IG-ON Elapsed Time` |
| `26C0` | `Clock Type` |
| `0167` | `Engine Stall/READY OFF Control History` |

Each row is raw-record-hashed in `cuw_timing_recovery.json`. This is exactly the
kind of DDB residue worth decoding before GTS+: it converts a future power-cycle
experiment into synchronized named observables.

For the short paid session, preserve the original calibration package and
extracted `attach.att`; snapshot `Save/RecoveryInfo.ini` plus the saved
calibration payload before/after an intentional interruption; retain raw J2534
API timestamps across `10 02`, `27 01/02`, reset, disconnect/reconnect and IG
OFF/ON; log the power-cycle Data IDs above; and record the selected
factory/contact/CPU metadata. SecurityAccess spacing should be compared with the
static writer fingerprint rather than assumed from the legacy 100-ms table.

#### 5.4.4 Bounded iQ-EMPS ancestry

`Cuw_iQ_EMPS.exe` is useful only as a naming/ancestry source. Its exact binary
contains the same 1st/2nd/3rd retry captions and terminal three-attempt error as
modern CUW, `CFlashWriter::SelectRetryPassword`, `CCanFlashWriter::ChangeReprogrammingMode`,
`CSilVinReader::FiveBaudInit`, `CSilFlashWriter::{SetBaudRateOfECU,TweakBaudRate}`,
`PrepareWrite1_iQ_EMPS`/`2`/`3`, `CTechVim_iQ_EPS_FlashWriter`, `CTester2IF`, and
EPS-specific `Verify Calibration ID` / interrupted-reprogramming recovery text.

The useful interpretation is historical: `SelectRetryPassword` is consistent
with the modern `UseNewSoftwarePassword` recovery state; the three PrepareWrite
pages expose operator-driven IG-OFF → start → IG-ON ancestry; VIM/Tester2 names
explain older Denso/Toyota tool vocabulary. The K-line/M16C/V850-era baud and
password machinery is **not** promoted onto the RH850 Sienna/Corolla firmware.
Every comparative string and the whole iQ binary identity are pinned by
`verify_techstream_cuw_timing_recovery.py`.

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


#### 5.4.5 Target-compatible Unified retry is not a SecurityAccess bypass

The recovery pass now distinguishes generic CUW retry machinery from the two
writer rows that are actually byte-compatible with the tracked EPS boot
grammar. `P5-Unified.ini` and `P5-Unified10.ini` both select
`TCUWCanUnifiedPrepareWriter.dll`, both set `PrepareRetryFlag=0`, and both retain
`IGOffRetriableFlag=1`. Direct PE export enumeration shows that the prepare DLL
exports only `StartPrepareWrite`; `TCUWCanUnifiedFlashWriter.dll` and
`TCUWCanUnifiedFlashWriterEachArea.dll` each export only `StartFlashWrite`.
There is no separate `PrepareRetry` export in this target-compatible set.

The normal Unified prepare grammar independently recovered in §5.2.2 starts
with exact 18-byte SecurityAccess (`27 01 || testerData[16]`, then
`27 02 || key[16]`). Therefore the shipped V18 target-compatible recovery rows
do not expose a second no-SA preparation entrypoint. `RecoveryInfo.ini` and
`UseNewSoftwarePassword` remain host-side persistence facts; they do not by
themselves imply ECU authentication state survives a fresh boot.

This is **TMS-036**. The generated `target_unified_recovery` record in
`cuw_timing_recovery.json` pins both parameter rows, export sets, and the joined
SecurityAccess grammar. The boundary is explicit: this result does not claim
anything about future Techstream versions, undocumented ECU ROM/bootstrap
modes, or an unobserved dynamically supplied plugin.

### 6.1 Recovered log format and save lifecycle

The logger format is now statically recovered for both shipped variants and
implemented by `tools/techstream/parse_ptshim_log.py`. The important fields are
line-oriented rather than a proprietary binary container:

| Field | v04.04 | v05.00 |
|---|---|---|
| API record | elapsed seconds + `<<`/`>>`/`++` + `PT...(...)` | same |
| Tx API | `PTWriteMsgs` | `PTQueueMsgs` |
| Message header | index, protocol, length, Tx/Rx flags | same plus decimal per-message `Handle` |
| Rx timestamp | decimal seconds | decimal seconds |
| Raw bytes | `\\__` followed by hex bytes | same |
| Summary/status | read/sent counts + J2534 status/error | same |
| Final saved encoding | UTF-8 text | UTF-8 text |
| Explicit `PassThruSaveLog` mode | append (`a, ccs=UTF-8`) | truncate/write (`w, ccs=UTF-8`) |

Both shim versions derive the decimal elapsed timestamps from
`QueryPerformanceCounter` divided by `QueryPerformanceFrequency`, relative to
the logger's first initialized counter. The internal ring is wide-character
text; `PassThruSaveLog` drains that ring through the CRT UTF-8 text mode and
closes the file. The parser additionally accepts UTF-16LE ring dumps so an
in-memory/pre-conversion recovery can be analyzed with the same code; that is
not the normal final SaveLog encoding.

For CAN/ISO15765 records, the logged raw message begins with the four J2534
address bytes followed by payload bytes. The parser preserves the complete raw
message, exposes those first four bytes separately as `address_hex`, retains
reported versus actual lengths, and keeps bytes beyond the reported actual Rx
length as `extra_data_hex` rather than silently discarding them.

`J2534Ctrl.dll`, rather than the shim itself, owns Techstream's normal filename
policy. Its save worker uses `GetLocalTime`, CSIDL `0x2E`, and the exact format:

```text
%s\Techstream\ErrorReport\j2534_%02d%02d%04d%02d%02d%02d.log
```

that is, a timestamped `j2534_MMDDYYYYhhmmss.log` below the selected special
folder's `Techstream\ErrorReport` directory. The controller creates named
`SAVE_J2534_LOG_FILE_EVENT` and `FINISH_J2534_LOG_FILE_EVENT` objects; a worker
waits for the save event, invokes the shim's save method, signals completion,
and returns to the wait loop. No size-based rotation grammar or separate
session-record marker was recovered: the controller creates a new timestamped
path when it requests a save, while the shim records ordinary API/message
lines.

Synthetic cross-version fixtures plus pinned body windows in both shims and
`J2534Ctrl.dll` are verified by `tests/verify_techstream_ptshim.py`.

**Practical use:** Install Techstream on a Windows machine with a bench EPS
ECU, replace the VCI driver with `ptshim32.dll`, and perform a diagnostic or
reflash session. Parse the resulting file with:

```bash
uv run python tools/techstream/parse_ptshim_log.py j2534_....log -o session.json
```

The normalized transcript can then be diffed against the static firmware
analysis for SA seed/key exchange, DID reads, session transitions, and
programming handoff. The six-operation evidence and privacy procedure is
[techstream-capture-procedure.md](techstream-capture-procedure.md).

### 6.2 Diagnostic databases (.ddb)

Techstream ships ECU-specific diagnostic databases in a proprietary binary
format (`DiagTool DataCtrl` magic). The EPS-relevant databases:

| Database | Region | Size | Content |
|---|---|---|---|
| `EPS_P4DK3.ddb` | NA | 6.6 KiB | EPS Phase-4 CAN DK3 diagnostic table |
| `EPS_CAN_P4DK.ddb` | NA | 10.5 KiB | EPS Phase-4 CAN functional diagnostics |
| `EPS_CAN_P4DK.ddb` | EU/JP | 10.5+ KiB | Same, regional variant |
| `EMPS_P5.ddb` | NA/EU/JP | 47.9 KiB | Conventional Phase-5 EMPS diagnostics; master category 405 / generation 20 |
| `Security_P4.ddb` | NA/EU/JP | 13 KiB | Phase-4 security-system diagnostics; not itself proof of a SecurityAccess/key table |
| `Toyota.ddb` | all | 13.0 MiB | Master routing/ECU enumeration corpus; type-1 directory structurally parsed separately |

The Stage-3 residual audit removes the older blanket statement that the DDB
record structures are unknown. Every one of the **35 steering `EPS*`/`EMPS*`
type-2 databases** is structurally parsed through its complete directory, with
an explicit observed section-type union through type 91. The remaining issue is
field semantics for selected section classes, not record discovery.

A targeted pass over `Security_P4.ddb` also prevents its filename from being
overread as cryptographic evidence. Section type 35 is one 28-byte record whose
leading string resolves to **`Security Alarm Operation`**; section type 37 is
50 20-byte records beginning with alarm-condition vocabulary such as
`Battery Desorption`, `Hood Open`, `Luggage Open`, and `Door Open`, with alarm
explanations in the companion string field. This high-signal residual is
therefore vehicle-security/alarm diagnostic vocabulary, not a recovered
Safekey/MCU-ID/MACKey provisioning table. Other section classes retain their
factory-derived names. The factory map is now itself generated from executable
evidence: both x86 switch tables are walked from case target to direct
constructor export, yielding all 89 format-1 and 151 format-2 identities.
Parser constants are checked against that independent map rather than against a
duplicated hand-maintained table.

`Toyota.ddb` is a distinct format-type-1 master schema, but it is no longer an
unknown directory. `parse_master_db()` covers all three regional directories
(67 NA, 67 EU, and 76 JP sections), and the
pinned KgpDataCtrl type-1 factory identifies CAN communication, ECU
category/function/description, DLL, communication-DID, and communication-RID
tables. Consumer-derived record layouts then close the priority category join:

| Region | section-16 record | Database | category ID | DLL / function / detail rows |
|---|---:|---|---:|---:|
| NA, EU | 294 | `EPS_P4DK3.ddb` | 317 | 9 / 3 / 6 |
| NA, EU, JP | 374 | `EMPS_P5.ddb` | 405 | 8 / 4 / 7 |
| NA, EU, JP | 496 | `EPS_CAN_P4DK.ddb` | 581 | 10 / 5 / 6 |

Every joined row retains its exact decoded bytes, record index, logical offset,
on-disk offset where uncompressed, regional source hash, string indices, and
resolved names. Types 62/88 are also decoded to their consumer-proven primary
and secondary lookup keys, but expose no category-ID field; their onward
category join remains explicitly unresolved. Exact Sienna identifier
`8965B4512000` is absent, which does not erase the independently proven family
routing above. `toyota_master_routes.json` and
`verify_techstream_master_routes.py` pin the join across NA/EU/JP.

The highest-value steering residuals are likewise decoded only to fields used
by exported consumers. Across 32 files / 76 section instances / 6,521 records,
the artifact covers classic PID and active-test types 6/11/12 plus P5 types
61/62/63/80/87/88/90/91. For example, type 62 proves its name index at `+0x18`,
monitor lookup key at `+0x24`, and sort key at `+0x30`; type 88 proves its name
index at `+0x18`, behavior key at `+0x24`, and sort key at `+0x2E`. Complete
`raw_hex` is retained for every record, so unnamed bytes are not silently
promoted to semantics.

#### 6.2.1 EMPS_P5 application-interface correlation

A targeted pass now closes one previously useful-but-unproven diagnostic
vocabulary join without projecting names from text alone. The `EMPS_P5.ddb`
master route is section-16 record **374**, category **405**, generation **20**,
identical in NA/EU/JP. Its eight DLL roles include
`GetDatMonListP5_DT.dll` and `GetDatMonSignalInfoP5_DT.dll`. The latter provides
the consumer proof for additional type-62 monitor metadata: physical-data key
at `+0x2A`, bit range at `+0x2C/+0x2E`, and pattern-display key at `+0x32`.
The physical-data record then selects a unit-table record.

Three steering monitors were tested against the recovered firmware state, with
explicit dispositions in
`data/generated/techstream_v18/application_interface_correlations.json`:

| Key | Techstream monitor | P5 shape | Disposition against Sienna firmware |
|---:|---|---|---|
| 402 | `Command Value Torque` | 16-bit; physical-data/unit chain resolves to **`Nm`** | **accepted corroboration** for the authenticated steering-command domain |
| 60 | `Cooperation Control State` | 8-bit; pattern 22 maps `0 → Cooperation Control`, `1 → Other than Cooperation Control` | **ambiguous** relative to the externally visible `0x262` LTA/LKA state bits |
| 403 | `Control State Information` | 16-bit, unitless | **rejected as a direct name** for any specific `0x262` field/bit |

Monitor 402 is materially stronger than a lexical match. The same metadata is
byte-identical across NA/EU/JP; on Sienna the firmware independently receives
authenticated CAN `0x2E4` signal 61 as a signed 16-bit value and carries it
through the recovered steering-command conditioning chain; and the pinned public
Toyota DBC independently calls that exact `0x2E4` 16-bit field
`STEER_TORQUE_CMD`. Techstream's diagnostic monitor is therefore accepted as
external vocabulary and dimensional corroboration for the **command domain**.
It is **not** proof that monitor 402 reads the COM destination directly, and it
does not expose the SecOC MAC, freshness state, or downstream d/q current
reference.

The later `8965H1202000` Corolla comparison makes that boundary decisive rather
than merely cautious. `GetDatMonListP5_DT.dll` builds the ECU support-data-ID
list and filters P5 monitor exposure through `CheckSupportPid`. In the raw
`EMPS_P5` type-62 records, the previously unnamed words at `+0x36/+0x38` behave
as primary/alternate Data IDs: all 222 nonzero primary words resolve through the
same database's type-61 `DataIdForDm` table except the single `0xFFFE` sentinel,
and all 166 nonzero alternate words resolve there. Monitor 402 carries primary
`0x1C02` and alternate `0x3C02`.

Corolla H independently implements **RDBI DID `0x1C02`** with live 2-byte
callback `0x495A0`. Its target-native producer chain is recovered as:

```text
CD55A (compose/bound H-local command precursor)
  -> FEBEC3C0
CD5DC: FEBEC3C0 * FEBEAC5A / 0x400
  -> FEBEC3D2
CE928: FEBEC3D2 -> FEBEAC56
BB9E8: FEBEAC56 -> FEBEE40A
56892/57692: FEBEE40A -> FEBE65F2
495A0: FEBE65F2 * FEBEE8A6 / 0x2000 * 100 / 0x100
  -> clamp +/-20000 -> signed16 DID 1C02
```

The active H steering pipeline `0xCE974` invokes `CD55A -> CD5DC -> CE928` in
that order. Yet the same exact H image has no configured SecOC or normal-COM
`0x2E4/0x131` ingress. Thus monitor 402 is best understood as an **internal EPS command-value-torque
observable**; association with one external CAN field
is calibration-specific and must be independently proved. This corrects any
stronger reading of the earlier Sienna correlation.

The same join produces a much larger semantic dictionary: H's 226 readable RDBI
DIDs overlap 124 `EMPS_P5` type-61 IDs and support 137 named monitor rows across
121 primary Data IDs. The most important current-domain rows are exact H joins:

| Techstream monitor | H DID | unit | Target-native role |
|---|---:|---|---|
| `Motor Actual Current (Q Axis)` | `1151` | A | `FEBE6BAE -> FEBE6592 -> 4915E` |
| `Command Value Current (Q Axis)` | `1152` | A | `FEBE6BC0 -> FEBE65A4 -> 4919A` |
| `Motor Actual Current 2 (D Axis)` | `1153` | A | `FEBE6BAC -> FEBE6590 -> 491D6` |
| `Command Value Current 2 (D Axis)` | `1154` | A | `FEBE6BC2 -> FEBE65A6 -> 49212` |
| `Motor Rotation Angle` | `1155` | deg | live 2-byte callback `4924E` |
| `Final Motor Current Limited (Q Axis)` | `1156` | A | `FEBEE414 -> FEBE65FC -> 49298` |

This closes the previously missing downstream bridge from monitor 402's internal
command-value state into the closed-loop motor controller. `FEBEC3D2` (the source
ultimately read by `1C02`) is bounded/gated by `CD5DC` into `FEBEC3D6`; `CD644`
normally copies that to `FEBEC3D4`; `CE928 -> BB9E8` publishes it as `FEBEE40C`;
and motor setup `312F0` negates `FEBEE40C` into `FEBE6964`. `336EE` publishes
that as `FEBE6C1A`. At `3322E`, the same term has two independently useful roles:
`FEBE6BC0 = FEBE6C1A` is the **Techstream-visible base Q-current command** behind
DID `1152`, while `FEBE6BB8 = saturate(FEBE6BE4 + FEBE6C1A)` is the compensated
Q command. `33160` publishes raw Q feedback aggregate `FEBE6BB4`; `32934`
computes the bounded command-error `6BB8 - 6BB4`; `32958/329A0` drive the Q-axis
PI/integrator in high-rate motor worker `58226`, which continues through the
already-mapped transform/duty/PWM path. This prevents a misleading shortcut:
Techstream's `Command Value Current (Q Axis)` is a real command observer, but its
RAM cell is not itself the final PI-error variable.

The selected bound in `FEBEC3D8` is independently published through `FEBEE414`
and exposed by DID `1156` as `Final Motor Current Limited (Q Axis)`. `33160`
supplies the saturated Q/D diagnostic feedback pair observed by `1151/1153`.
The D-axis command `1154` is generated through a separate motor-internal
`3364E -> 335EE/33622 -> 3322E` path rather than from the recovered `1C02`
command-torque chain.

Thus Techstream now supplies both the OEM vocabulary **and** an independent
firmware-static semantic bridge from H's general internal torque command through
the Q-current PI loop. That command is not LTA-specific. The separate provenance
census in the Corolla variant report shows the retained Sienna-homolog LTA
contribution is direct-write inactive in this calibration and B6 has no recovered
opaque/group/full-PDU command consumer.

The same exact Data-ID vocabulary now also closes the corresponding **Sienna
`8965B4512000` observer semantics target-natively**, rather than borrowing H RAM
addresses. Sienna's own 242-row RDBI table contains these exact live 2-byte DIDs:

| DID | Techstream name | Sienna target-native source |
|---:|---|---|
| `1151` | `Motor Actual Current (Q Axis)` | `FEBE66E6 <- FEBE6D1A` |
| `1152` | `Command Value Current (Q Axis)` | `FEBE66FC <- FEBE6D2C <- FEBE6D7E` |
| `1153` | `Motor Actual Current 2 (D Axis)` | `FEBE66E4 <- FEBE6D18` |
| `1154` | `Command Value Current 2 (D Axis)` | `FEBE66FE <- FEBE6D2E <- FEBE6D70` |
| `1155` | `Motor Rotation Angle` | `FEBE665C <- FEBE7D14 <- FEBE7D34` |
| `1156` | `Final Motor Current Limited (Q Axis)` | `FEBE6764 <- FEBEE608 <- FEBEAF40` |
| `1185` | `CAN Vehicle Speed (SP1)` | `FEBE8070` |
| `1C02` | `Command Value Torque` | `FEBE674A <- FEBEE40A <- FEBEAC56 <- FEBEC1D2` |

The current names are stronger than same-number guesswork. `dual_motor_dq_feedback_combine
@ 0x37644` is the direct writer of `6D18/6D1A`; `dual_motor_dq_current_reference
@ 0x37712` directly publishes `6D2C=6D7E` and `6D2E=6D70`; the Sienna RTE staging
worker `0x5C0B6` copies those four values to the exact RDBI source cells. For
`1C02`, `0xCB454` publishes `FEBEC1D2 -> FEBEAC56`, `0xBCACE` publishes that to
`FEBEE40A`, and the callback applies the same dimensional scaling/clamp shape
already recovered for H. For `1156`, `0xBCA88` publishes `FEBEAF40 -> FEBEE608`
before the diagnostic staging copy. The firmware bodies and exact DID table are
SHA/raw-byte pinned in `verify_sienna_8965B4512000_techstream_did_semantics.py`.

The producer pass is now closed far enough to state what each observer means in
the motor-control loop, rather than only naming its source cell:

- `1151` emits the staged dual-motor **Q actual** sum at `0.01 A/LSB`;
  `1153` is the corresponding **D actual** sum. Their producer
  `dual_motor_dq_feedback_combine @ 0x37644` feeds the current-loop state.
- `1152` emits the **base Q-current command** at `0.01 A/LSB`. The motor path is
  `FEBEE40C -> -FEBE6ACC -> FEBE6DB2 -> q-current magnitude/sign map ->
  FEBE6D7E -> FEBE6D2C`. The PI does not consume that DID cell directly: its
  compensated reference is `FEBE6D24 = clamp(FEBE6D50 + FEBE6D7E)`.
- `1154` likewise exposes the **base D-current command** while the compensated
  D reference is `FEBE6D28 = clamp(FEBE6D4E + FEBE6D70)`. The recovered
  magnitude-indexed map becomes negative at high command magnitude, a useful
  field-axis/field-weakening discriminator; the exact calibration-table meaning
  remains bounded.
- `1156` exposes the selected non-negative Q-current-limit magnitude
  `FEBEAF40 -> FEBEE608 -> FEBE6764` at `0.01 A/LSB`. Companion DID `1065`
  (one byte, callback `0x4D084`) is exactly `FEBE6764 > 0`; it is a structural
  companion and is not assigned a separate OEM P5 name here.
- `1155` scales motor/resolver angle as `raw * 0x465 >> 11`, capped at 36000
  (`0.01 deg/LSB`). If internal Dem event `0x52` is set, the callback returns
  `0xFFFF`; that makes it a useful validity canary. The producer/meaning of
  event `0x52` itself remains unresolved.
- `1185` is the 16-bit SP1 field from protected CAN-FD `0x0D7`, capped at
  30000 (`0.01 km/h/LSB`). It should be paired with DID `0102`, whose Sienna
  source is a different vehicle-speed acquisition, to detect source/timing
  differences.
- `1C02` scales `FEBE674A` with `FEBEE8A6` and clamps to ±20000
  (`0.01 Nm/LSB`). Its chain is `FEBEC1D2 -> FEBEAC56 -> FEBEE40A ->
  FEBE674A`. The limited sibling `FEBEC1D4` is what proceeds through
  `FEBEAC54/FEBEE40C` into the Q/D-current path. Thus `1C02` is a genuine
  **general internal command-value-torque observer upstream of motor control**,
  but it is still not intrinsically the authenticated external `0x2E4` command
  or an LTA-specific quantity.

This gives a capture-ready ordinary-UDS observer card. Preferred sequence:
`1C02` (internal torque), `1152` (base Q command), `1151` (Q actual), `1156` +
`1065` (current limit + validity companion), `1154` (D command), `1153` (D
actual), `1185` (protected SP1 speed, paired with `0102`), and `1155` (motor
angle/invalid canary). The generated artifact includes exact `22` request bytes,
engineering-unit encodings, alternate P5 Data IDs, all eight raw DDB record
hashes, 35 byte-pinned supporting functions, and a read-only XCP candidate set.

The remaining static boundaries are explicit: the producer/meaning of Dem event
`0x52`; exact semantic ownership of the individual contributors summed by
`steering_command_secondary_select_stage`; the exact authenticated `0x2E4` ->
general-command contribution; direct sin/cos-table naming behind the
cross-consistent D/Q assignment; and the meaning of each candidate feeding the
selected current limit. Those are not silently promoted from control-shape
inference.

Canonical generated artifact:
`data/generated/sienna_8965B4512000_techstream_did_semantics.json`; verifier:
`tests/verify_sienna_8965B4512000_techstream_did_semantics.py`.

The same exact H join closes protected `0x0D7` at field level. Its regenerated
PDU40 unpacker reads only signal 240 (1 bit), signal 243 (16 bits), and signal
246 (4 bits). Signal 243 is stored at `FEBE7D82`; DID `0x1185` reads that cell
and `EMPS_P5` names it **`CAN Vehicle Speed (SP1)`**. D7's nonscalar configured
rows have no recovered group/full-PDU consumer. Its only command-sized scalar is
therefore OEM-identified vehicle speed, not a hidden steering magnitude.

The P5 DTC path strengthens that B6 conclusion with an OEM source label. H's
six-row communication-monitor scheduler maps receive-status slot `0x18` to the
B6 unpacker/PDU42. Failure of that row selects Dem event `0x0143`; H's event
and DTC tables resolve it to packed `0xC12987`, and the exact `EMPS_P5` type-65
record names it **U012987 `Lost Communication with Brake System Control Module`
/ `Missing Message`**. `0x0D7` and `0x0D5` share the same DTC. This is an exact
firmware→Techstream join and makes B6 a brake-system-originated protected message
in Toyota's own diagnostic model, not a plausible hidden camera/IPM-A steering
command merely because it is H-only.

Conversely, the old Image Processing Module A diagnostic remains only as disabled
residue. H DTC index 93 is packed `0xC23A87`, exactly the `EMPS_P5` U023A87
`Lost Communication with Image Processing Module "A" / Missing Message` row, but
H's DTC enable word is zero. The Sienna comparison had active communication-
monitor rows joining that DTC to `2E4`, `131`, `191`, and `2FD`; H retains those
four Dem event records pointing to index93 but none is present in H's active
six-row monitor table. This is strong calibration-specific evidence that the
classic direct camera/IPM-A interface was disabled/removed rather than renumbered
to B6. It does not identify where the vehicle's replacement LTA architecture
lives.

The attractive newer target-angle group (`Target Lateral ID`, `Target Steering
Angle After Output Compensation`, `Advanced Drive Target Steering Angle`, plus
System-2 variants) is grouped under primary DIDs `0x1CEE/0x1CEF`; neither DID is
implemented by H RDBI. Category-405 `EMPS_P5` is also observation-oriented rather
than an obvious command surface: its parsed section set is exactly
`61/62/63/80/87/88/90/91`, with no classic type-11/type-12 Active Test table, and
its eight master-routed DLLs contain no Active-Test- or Routine-named role. The
nominal `Cooperation Control State` DID `0x106A` is a success stub in H. These are
bounded negatives for this Techstream package/calibration, not proof that Toyota
has no separate utility or server-mediated procedure.

Machine-readable ownership is
`data/generated/corolla_8965H1202000_techstream_correlations.json` with compact
image-bound target evidence in
`corolla_8965H1202000_techstream_steering_decompiler_evidence.json`.

The state-monitor candidates do not meet that bar. Key 60's binary cooperation
encoding is real in the DDB and the same key/name also occurs once in P5
behavior-data section 88, but exact H DID `106A` returns success without writing
its declared byte. Key 403 is a generic 16-bit state word with no recovered route
to a specific external steering aggregate. Those names therefore remain
diagnostic vocabulary, not proof of a live autonomous-control interface.
Consumer-proven P5 tables 61/63/80/88/90/91 contain no key-402 or key-403 join.
This is a bounded search, not a whole-diagnostic-system absence claim.

The repository parser now decodes section directories, DTC records,
factory-identified supported-PID/PID/DID table classes, freeze-data monitor
vocabulary, and all three OEM string databases. Section 3 is
`CDbSupPidTable`, not a DID table; the two selected P4 EPS databases therefore
provide no direct database-DID correlation. Run
`make generate-diagnostic-vocabulary` to rebuild the calibration-focused
annotations plus the complete regional steering corpus.

The calibration-focused correlation still uses `EPS_P4DK3.ddb` and
`EPS_CAN_P4DK.ddb` as bounded family vocabulary for the Sienna. A separate
artifact, `data/generated/techstream_v18/steering_diagnostic_corpus.json`,
prevents that selection from hiding the rest of the distribution: it discovers
all **35** regional `EPS*`/`EMPS*` files, groups them into **25** byte-identical
structural payload variants, and recovers **129** unique DTC identifiers, one actual
`CDbDidTable` record, 146 supported-PID records with 16 unique raw keys, and
**1,257** freeze-data monitor records. The former parser stopped at directory slot 16 and
silently omitted 10,659 of 25,361 type-2 sections.

The generated artifacts are deterministic. Tests compare committed JSON to a
fresh in-memory rebuild, reject malformed LZSS streams, wrong format dispatch,
bad format-6 magic, and fractional record layouts, and independently verify all
raw section-directory entries. `U_English.ddb` also carries 25,957 aligned
resource identifiers; those group UI text but do not encode ECU ownership or
firmware routine linkage. Its former 122
"utility procedure" records were produced by substring search (including
`eps` inside `steps`) and per-term truncation. They are now explicitly labeled
steering-anchored `utility_string` vocabulary, never recovered procedures.

## 7. MACKey Registration — ECU authentication key provisioning

The canonical report is
[security/mackey-registration.md](../security/mackey-registration.md). Managed
IL plus native `IT3UtilityNK.dll`/`UtilityExNK2.dll` now recover the complete
online and vehicle-facing flow:

- the request XML contains VIN, master/slave `SafekeyNumber`, `MACM1`,
  `MACM2`, `MACM3`, and a deterministic SHA-256 `HashValue`;
- native `IT3UtilityNK.dll` bridges to
  `CWebService::TisServiceSendMacKey` / `TisServiceGetMacKeyInfo`;
- the returned request ID replaces `$36` in the configured login URL, then the
  client polls by `request_id` plus `SHA256(request_id)` and stores the returned
  exchange-key XML as `Memg/MAC_01_WriteData.xml`;
- `$36` is therefore **not DID `0x0036`**. The former `ecuMacId` URL claim came
  from an untracked configuration example and is not repeated as pinned fact;
- `UtilityExNK2.dll` reads VIN with `22 F1 90`, the 16+32+16-byte MAC tuple
  with `22 10 2E`, and master/slave 16-byte `SafekeyNumber` values with
  `22 10 10`;
- the response parser matches returned records by raw `SafekeyNumber`, then
  writes each selected ECU through `31 01 30 02 || M1 || M2 || M3` and polls
  with `31 03 30 02` for state plus `M4[32] || M5[16]`;
- all 24 `CMAC_01_*` RTTI classes, vtables, 51 embedded `S324-*` procedure
  codes, critical body hashes, and command shapes are pinned in generated
  evidence. Cross-class UI successors remain caller-selected and bounded.

This remains distinct from ordinary UDS SecurityAccess. It uses the same
M1–M5 cryptographic architecture as the Sienna command-8 path, but it is not an
exact diagnostic join: Techstream uses Routine `0x3002`, while the Sienna uses
RoutineControl RID `0x1010` control types `01/03`. A relationship to that EPS or its SecOC
slot 4 is therefore **not proven**.

### 7.1 Representation-bounded secret census

The generated census searches each of 6,620 files for raw bytes, printable
ASCII, upper/lower hex ASCII, UTF-16LE plaintext/hex, and the bitwise inversion
of every applicable representation. It additionally resolves direct x86
imm32 references to discovered PE constants and pins the two known
CommandCommon byte-immediate constructions. Within those explicit classes it
finds neither the Sienna bootloader SecurityAccess secret
`f05f36b7d78c03e24ab4faef2a57d044` nor the application secret
`893e08418c741ffa2a9c044bffa55813`.

This is a representation-bounded negative, not proof of complete absence:
there is no general constant propagation, symbolic execution, encrypted-blob
recovery, or arbitrary runtime decoding. The same artifact corrects the host
maps above and records every hit with artifact SHA-256, file offset, RVA/VA,
representation, direct references, containing export where recoverable, and
confidence.

## 8. Relationship to firmware findings

### 8.1 Corroborated

| Firmware finding | Techstream corroboration |
|---|---|
| SEC-BOOT-003: AES-128-ECB SA construction | `CSecurityAccessAES128::AES_128_ECB` implements the same cipher |
| SEC-APP-001: Application SA level 2 with AES-128 | Shape only: `CSecurityAccessAES128` shares the AES-128 / level-03-04 / 16-byte *form*, but its key `FUKUMORIYOSIYAMA` and single-stage construction differ from the EPS two-stage + per-calibration secret (§4.0 resolves the routing: FUKU serves ADS/PCS runtime, not EPS) |
| DIAG-APP-003: Programming handoff gates | CUW prepare-write implements the same session/speed/phase sequence |
| ARCH-007 / authenticated steering-command domain | `EMPS_P5` monitor 402 `Command Value Torque` is master-routed, 16-bit, and resolves to `Nm`; public Toyota DBC independently names CAN `0x2E4`'s signed 16-bit field `STEER_TORQUE_CMD` |
| Bootloader diagnostic `0x7A1` / `0x777` | Gateway routing (`07E0`/`07DF` → ECU-specific physical address) |

### 8.2 Not addressed

| Open question | Techstream relevance |
|---|---|
| SecOC slot-4 key extraction | None — Techstream does not interact with SecOC runtime verification/key slots |
| Motor actuation join (`0x2E4` → d/q current) | Techstream now corroborates the **steering-command domain** through monitor 402, but still provides no direct SecOC or d/q-current join |
| Runtime RAM key-slot mirror | None — Techstream reads diagnostic values, not raw RAM |
| ICU-S command 5/13 characterization | None — Techstream does not issue ICU-S commands |

### 8.3 New leads

| Lead | Value |
|---|---|
| `ptshim32.dll` CAN logger | Capture a real Techstream↔EPS session for transcript validation |
| `CSecurityAccessAES128` source paths | PDB/source-tree context for the KGProject diagnostic framework |
| TIS portal RKS flow (`CUWAccessRKS.dll`, §5.3) | OEM reprogramming-key authorization (Layer A) — VIN+license bound, IE-automated, no client crypto; independent of the cal-file crypto key (Layer B). Not immobilizer. |
| MACKey Registration (§7) | Recovered exchange-key provisioning path: `22 F190/102E/1010` vehicle reads → VIN + master/slave safe-key/MAC fields → hashed `ECUExchangeKey` XML → native TIS bridge → identity-matched response → per-ECU Routine `0x3002` M1–M3 write and M4/M5 poll. `$36` is the server request ID. This shares the Sienna command-8 envelope but is not its RoutineControl RID-`0x1010` service. |
| `TCUWControlCommPhase.dll` parameters | Exact timing values for SA seed/key exchange during reflash |
| `[ISTA_T3_Login]` credentials | Hardcoded hex credentials in `uspublic.ini` for Toyota ISTA portal |

## 9. Limitations

This analysis is static — extracted from the installer without executing
Techstream on a vehicle or bench. The findings describe the *capability* and
*design* of the toolchain, not observed runtime behavior. Specifically:

- The SA key computation in `CSecurityAccessAES128` was identified by symbol
  analysis, not by executing the cipher against a known seed/key pair.
- The `.ddb` pipeline decodes DTC, DID, and monitor records but not every
  section type. The complete steering corpus prevents source-file omission;
  unknown sections remain explicitly inventoried rather than interpreted.
- The `ptshim32.dll`/`ptshim32_0500.dll` log formats and Techstream save
  orchestration are statically recovered and parser-tested (TMS-005); actual
  capture behavior against a live vehicle/bench remains unobserved.
- No live UDS transcript has been captured to validate against firmware
  findings.
