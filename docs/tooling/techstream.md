# Toyota Techstream / GTS+ diagnostic software

> **Scope:** Toyota Techstream V18.00.003 (DENSO) plus the 2026-06-18 GTS+
> distribution used for current-generation P5/CUWPlus analysis. V18's internal
> module version comes from `VerApp.ini`/`VerCmd.ini` (dated 2022-11-22 /
> 2022-12-08); its installer filename says V18.00.008, but the "008" is the
> Flexera IS wrapper build number, not the application version. V18 DDB files
> are dated 2022-12-07/08 and its VehicleData coverage extends through 2022.
>
> **Document type:** external-source reverse engineering
>
> **Status:** active
>
> **Evidence source:** external-source
>
> **Evidence profile:** recovered/bounded — each claim is scoped to its pinned
> Techstream/GTS+ source corpus, not the Sienna firmware or a live vehicle session
>
> **Canonical tracked artifacts:** `software/locks/techstream-v18.json`,
> `software/locks/gtsplus.json`, `software/locks/toyota-cuw-corpus.json`, and
> derived evidence under `data/generated/techstream_v18/`
>
> **Ignored source corpora:** `software/Techstream/v18/`,
> `software/Techstream/gtsplus/`, and `software/Techstream/cuw/`
>
> **Verification:** external-source lock/hash gates plus deterministic generated-artifact tests
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
archive. The unpacked tree (`software/Techstream/v18/unpacked.7z`, 6703 files, 580 MiB
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
`software/locks/techstream-v18.json`.

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
require decoding. The decoded INIs are stored under `software/Techstream/v18/decoded/`
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
`pe_dlls` in `build/work/pe-project/`). The full algorithms follow.

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

#### 4.5.3 Real Tacoma VFOREST corpus: 11 packages / 16 CPU images

The broader local Tacoma corpus generalizes the `04C21` result instead of
leaving it as a one-package observation. Eleven real `P5-CAN` ENG&ECT CUWs
contain 16 CPU images across three Techstream size classes: CPUType86 =
`VFOREST_2_0M` (`0x200000`, nine images), CPUType87 = `VFOREST_1_5M`
(`0x180000`, two images), and CPUType89 = `VFOREST_1_25M` (`0x140000`, five
images). Every member decodes completely as ASCII-hex `ZV00/ZV01` plus standard
LZF, with no residual transport layer.

Five packages are dual-CPU. Both archive members in one such package use the
same compound filename `<CPU01NewCID>_<CPU02NewCID>.txt`, so member names do
not identify the CPU. Archive order does: member 1 maps to `CPU01` / CPUType89
and member 2 maps to `CPU02` / CPUType86 or 87. The mapping is byte-validated by
each reconstructed image's part identity at logical `0x100C`, image size, and
cross-package password closure.

The selected `0P5-CAN86`, `0P5-CAN87`, and `0P5-CAN89` rows are identical in
the relevant legacy security/orchestration fields: `PasswordAddress=0x100E`,
`ByteOrder=0`, `FORESTTypeFlag=1`, `M16CTypeFlag=0`, dynamic writer flag 0,
`WaitTimeAfterIGOn=10000`, and `WaitTimeForIGOFFON=10`. Thus the real size
classes expose no separate credential schema. Source passwords remain encoded
in `TargetData`; each image's new password is at decoded-ZV `0x100E` and also
appears at logical image `0x1004`. Two update chains close independently:
`04A71`'s new password `74B53E44` becomes `04A72`'s source password for
`8966304A7100`, and `04B81`'s new password `59CF08BF` becomes `04B82`'s source
password for `8966304B8100`.

All 16 expanded images share an exact `0x1004`-byte prefix. At logical
`0x1004` the per-image password begins; `0x1008` is the stable marker
`9E5D123A`; `0x100C` is the plaintext Toyota part identity. Every image ends in
one common 52-byte footer grammar:

```text
B270AD78E88F32B558FEEB58D03B3B1D || 00000000 || image[0x1004:0x1024]
```

Unused logical space immediately before that footer is a word-aligned run of
`E203F133`. Across all nine CPUType86 images, the 4-KiB blocks common to every
version are exactly block 0 and blocks 396..510.

The strongest differential is the direct `04B81 -> 04B82` update. Both packages
carry the exact same CPUType89 `896650410100` member byte-for-byte, while the
CPUType86 image advances from `8966304B8100` to `8966304B8200`. Those two 2-MiB
images differ in 135,465 bytes across 73 blocks: many low/mid-image blocks have
only 1–15 changed bytes, while blocks 362..395 form a densely rewritten region.
This locality proves the expanded representation is strongly structured and is
not behaving as one whole-image cryptographic ciphertext. It still does not
prove direct native CPU plaintext; an ECU-side Denso/VFOREST storage/coding
transform remains bounded.

Canonical corpus evidence:
`tools/techstream/inspect_cuw_vforest_corpus.py`,
`tests/verify_techstream_cuw_vforest_corpus.py`,
`data/generated/techstream_v18/cuw_tacoma_vforest_corpus.json`, and the
[corpus analysis](../history/2026-08/TACOMA_VFOREST_CUW_CORPUS_ANALYSIS_2026-08-23.md).
The complete artifact pins all package/image hashes, source/new passwords,
member order, fill boundaries, and pairwise CPUType86 block-diff counts.

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

#### 5.2.4 Real format-0x67 FRC delta corpus: six `ReproMethod=07` packages and the modern unpacked GTS+ host

The external corpus now includes six **format-`0x67` FRC packages** (front
recognition camera, DiagID `0792`, Corolla-family; TMS-040/041 category-498
counterpart on the ECU side): `T-0058-23` (`8646F1204300→8646F1204500`),
`T-0060-23` (`…04400→…04500`), `T-0061-23` (`8646F1606200→…6300`),
`T-0062-23` (`8646F4206200→…6400`), `T-0149-24` (`…6400→…6700`), and
`T-0150-24` (`8646F1606300→…11200`).  `inspect_cuw_frc_corpus.py` +
`verify_techstream_cuw_frc_corpus.py` close the container, descriptor, framing,
and cross-package evidence; the generated artifact is
`data/generated/techstream_v18/cuw_frc_corpus.json`.

**Container (verified).** Format `0x67` is a membership-table member whose
tail is the same `count:u8 || member[count]` grammar as Version 4 (TMS-034):
`u16-BE namelen || name || u32-BE len || u32-BE crc32(zlib) || payload`,
three members, both outer and all member CRCs valid, consumed bytes ==
declared total exactly on all six files (`parse_cuw_container.py` implements
the branch).  Members are exactly `01-<NewCID>.xx`,
`Delta-01-<src>-<new>-write.datx`, and `Delta-01-<src>-<new>-routine.xx`.

**Descriptor (verified).** `[Format] Version=105, VersionForCFM2=1`;
`[Vehicle] ContactType=P5-Unified` (`VehicleName "COROLLA Series"`);
`[Node01] RequiredSpecReproVer=04`, `DiagID=0792`, gateway
`01_GatewayDiagID=07505F`; `[KindOfCal] IsControlledBySCC=1, IsBlankECU=0`;
`[LogicalBlock101] ReproMethod=07, SecurityProperty2=9C`, one source target.
All six carry the **same** index-subtraction-obfuscated `ServiceAuthKey`
(Node section; decodes to ASCII `3A8A90AE0ED81B6C37E21C1C5179A93E`) and
`Nonce` (LogicalBlock section; `5587BF845F3FF525E610A8A5EC9BD6E5`).  Area
descriptors: `ReproData`/`DeltaReproData` share one 512-byte
`DigitalSignature` (flash area `08E80000/05180000`),
`EraseAndReproRoutine`/`DeltaEraseAndReproRoutine` share another
(`008F6C00/00000570`); CRC/CMAC empty.  The whole/delta entries for each
target area share the same 512-byte `DigitalSignature`, so it is **not a direct
signature of the differing serialized member bytes**; the exact signed object remains bounded.

**2023 Corolla campaign/package correlation (TMS-052).** Toyota's official
23TC01 technical instructions independently publish the Corolla/Corolla
Hatchback/Corolla Hybrid FRC transitions `8646F1204300→8646F1204500` and
`8646F1204400→8646F1204500` (NHTSA mirror `MC-10242522-9999`, SHA-256
`3c275694…92bea`). Those two published edges match the raw descriptors of
**`T-0058-23.cuw` and `T-0060-23.cuw` exactly**: both are `DiagID=0792`,
`ContactType=P5-Unified`, `RequiredSpecReproVer=04`, `ReproMethod=07`,
`VehicleName=COROLLA Series`, NA model year `23`, and both converge on the same
`8646F1204500` stored target image (`04b07fb4…c8dd3`). Thus a model/year-
generation-matched 2023 Corolla FRC package family is already present locally;
the missing FRC problem is **decoding/exact target identity**, not finding any
2023 Corolla `0792` CUW. This still is not a VIN-level join to the albinoelephant
or Span specimens.

**Payload boundary (verified/bounded).** The `01-….xx` members are plain
Motorola S-record **framing** (5,341,273 records, zero invalid, two ranges:
the `0x8F6C00` routine slot and flash `0x08E80000..0x0E000000` = 85,458,944
B); the **decoded data is high-entropy with unknown encoding** — T-0058
global entropy 7.9999977 bits/byte, minimum complete 4-KiB window 7.93098
(no plaintext island), printable/00/FF fractions random-like; the same
holds on all six.  The `Delta-…-routine.xx` member is byte-identical in all
six packages (sha256 `5baa1feb…430f`), decodes to exactly the same 1,392 B
(`161fd56d…cedb`) that every whole image embeds at `0x8F6C00`, and is itself
high-entropy (7.8798) — a byte-identical deterministic encoded
representation whose interpretation/transform is unknown.  The `write.datx`
members are 16-byte
multiples, share exactly one leading 16-byte block
(`0a4aba7f300a8745e2acb15b5b59a046`), and have **zero** interior block
collisions across packages; sizes scale with version distance
(8,272–1,503,040 B).  Consecutive-version stored images are statistically
independent: both corpus-internal chains (`T-0062→T-0149`, `T-0061→T-0150`)
show byte identity 0.00390–0.00391 (chance is 0.003906), zero shared
16-byte blocks beyond the 32-byte constant image prefix
(`8b273e82…d23dfc`), and no identical run ≥ 8 beyond it — the stored
representation changes globally rather than as localized edits; the exact
transform remains bounded.  Five further format-`0x67` camera
packages (Tundra/Crown/Camry/GH, DiagID `07D2/07506D/07500F/0724`) carry
`ReproMethod=01`/`SecurityProperty2=98`/`IsControlledBySCC=0` and no delta
sections — the pinned whole-repro contrast set.

**Modern host (recovered, from the statically unpacked GTS+ CUWPlus
binaries in `software/Techstream/gtsplus/cuwplus`; provenance and SHA-256 pins are
tracked in `software/locks/gtsplus.json`).**  The shipped 2026-06-18 native DLLs are Crackproof-style stubs;
the evidence images are statically reconstructed (adapted Senbei PE32
unpacker) and every anchor below is byte-checked by the test against those
pinned images (image base `0x10000000`):

- **Route**: decoded CUWPlus `Ini/P5-Unified04.ini` (per-nibble
  `enc = 0x23 + 4*nibble` obfuscation) selects
  `TCUWCanUnifiedCIDGetter.dll` + `TCUWCanReproStdPrepareWriter.dll` +
  `TCUWCanReproStdFlashWriter.dll`, `PrepareRetryFlag=0` — the ReproStd
  pair serves `P5-Unified04`, so these FRC packages use the standard
  ReproStd route, not the Unified flash writers of TMS-032.
- **Descriptor parser (modern `CUW.dll`)**: the `[LogicalBlock]` section
  names map to `CLogicalBlockInfo` area objects through `FUN_1000DD60`'s
  store sequence — `ReproDatanxx→+0x24`, `EraseAndReproRoutinenxx→+0xCC`,
  `DeltaReproDatanxx→+0x174`, `DeltaEraseAndReproRoutinenxx→+0x21C`,
  `Compression…→+0x2C4/+0x36C`, plus `+0x414/+0x4BC` and an `0xA8`-stride
  `ReproDataSegment0nxx..2nxx` loop — and the `CLogicalBlockInfo`
  constructor (`TCUWCalibrationFile.unpack.dll @0x10001400`, symbol
  present) builds area objects at exactly those offsets minus `0x1C`
  (`+0x08/+0xB0/+0x158/+0x200/+0x2A8/+0x350`), so the `+0x158/+0x200`
  area names are **recovered, not inferred**.  `IsControlledBySCC` is
  compared against `[KindOfCal]` and stored at calibration `+0x24`
  (`0x1000CF89`); when SCC is set and `IsBlankECU` clear, the parser calls
  `FUN_100115E0`, which consumes `VehicleForNA`/`VehicleForEUOT` sections.
  **`IsControlledBySCC` does not select the RKS flow.**
- **ReproMethod enum (modern `TCUWCalibrationFile.dll`)**: method-code slot
  array `0x10009100` embeds the classic six `01/05/07/08/09/0A` plus Phase-6
  `00/02/03`; exported `mlptrReproMethod_*` slots at `0xE000..0xE020`;
  strings pin `DeltaReproRoutinePackageDLType` (`0x1000D5C4`) and
  `Compression/Delta/Whole…Phase6` (`0x1000D540/0x1000D460`).  `07` =
  DeltaReproRoutinePackageDLType as in V18.
- **Writer wire grammar (modern `TCUWCanReproStdFlashWriter.dll`)**:
  RequestDownload builder `0x10002810` emits `34 || DFI || 44 ||
  StartAddress[4] || Length[4]`, expected `74`, `74`-length capped at
  `0x0FFF` minus two; the DFI selector (`0x100031E0` region, jump table at
  `0x10003410`) maps method-family tags `0/1→0x01`, `2→0x21`, `3→0x11`.
  The FRC delta route therefore downloads the `write.datx` member with
  **DFI `0x21`**.  The recovered `ReproMethod==2` (delta) worker sequence
  (`0x10001B40`) is: select the PackageDL **routine** area `+0x200`
  (`0x10002171`, tag `0` at `0x10002186` → DFI `0x01`) and close it with
  StartRoutine SID `31 01` + RID `10 F5` (selector dword `0x4D` at
  `0x10002BE9`; `31 01` at `0x10002CA1`, `44` at `0x10002CAD`); then select
  the **DeltaReproData** area `+0x158` (`0x100022A8`, tag `2` at
  `0x100022B5` → DFI `0x21`) and close it with RID `10 F6` (dword `0x45` at
  `0x10002C03`).  `FF00` exists in the builder's selector-1 slot (dword
  `0x56` at `0x10002C16`) but is not used by this delta sequence.  These are
  **pre-data/post-data routine-control steps only** — the host does not
  execute or jump to the `0x8F6C00` bytes; it downloads them and invokes the
  ECU via RoutineControl.  No erase/verify semantics are claimed for
  `10F5`/`10F6` without ECU firmware.
- **DFI semantics are named by host code (not ISO nibble speculation)**:
  `TCUWP6CanReprostdFlashWriter.dll` compares the ReproMethod string
  against imported `mlptrReproMethod_CompressionReproPhase6` → DFI `0x11`
  (`0x10004063`), `mlptrReproMethod_DeltaReproPhase6` → DFI `0x21`
  (`0x10004086`, `cmovne`), default/Whole Phase6 → `0x01` (`0x10004043`).
  Toyota's own code names `0x21` the delta-data DFI and `0x11` the
  compression-data DFI; the ReproStd FRC matrix is routine-PackageDL
  tag0→`0x01`, whole-data tag1→`0x01`, delta-data tag2→`0x21`,
  compression-data tag3→`0x11`.  No high/low nibble meaning is claimed
  beyond what these code paths name.
- **What the `0x21` bytes are**: the compact **delta representation** the
  ECU consumes as its delta input.  The exact transform (decryption,
  decompression, patch grammar) is **unknown** — "decrypted ECU-side" is not claimed, and
  no host-side decryption exists in the pinned writer anchors.
- **The host treats `.datx` as opaque bytes end-to-end (bounded closure)**:
  format-`0x67` members are raw length+CRC32 payloads (T-0058 `write.datx`:
  offset 256,387,015, length 9,184, stored CRC == computed, sha256
  `f9bf53cd…8465`); the CUW.dll read path is a chunked
  `fread(dst,1,0xFFF)` loop (reader `0x1002BEB0`, push site `0x1002BF83`)
  behind a whole-file CRC32 gate (`0x1002A3B0`, called from loader
  `0x10031A20` at `0x10031C0C`; mismatch → "Error FileCRC"); S-record
  grammar parsing applies only to `.xx` members, while `.datx`/`.binx` are
  length-delimited binary.  `CDeltaReproArchiveCtrlr` (RTTI `0x1008A9A0`,
  vtable `0x1007C918`, single deleting-dtor virtual `0x10066DC0`, global
  instance `0x1008CA0C`) is **orchestration-only**: its `0xAC`-stride
  entries hold extracted-file paths, node/area names, and block counts —
  no payload pointer or byte fields — and its methods are path/map/list
  bookkeeping (`0x10066E20` map getter, `0x10067240` release,
  `0x100674A0` ownership transfer, `0x100679D0` chain assembly,
  `0x10067EC0` growth).  CAES encrypt/decrypt are called only by the INI
  parameter decode and SecurityUp seed-key helpers
  (`0x1001B9B2`/`0x1005AC52`/`0x1005AD02`), never the member path, and
  `TCUWCalibrationFile.dll` + `TCUWCanReproStdFlashWriter.dll` have **no
  crypto or compression imports at all**.  The host's last action is
  handing the untouched buffer + declared lengths to RequestDownload
  DFI `0x21`.
- **RKS selection is runtime**: `TCUWCanCommonPrepareWriter.dll` exports
  `CCanCommonPrepareWriter::JudgeReproGWNodeForP4AndP5 @0x10001820`
  (plus `CalcSeedKeyForSecurityUp @0x100014A0`); it probes the gateway
  with TesterPresent templates against strings `000007505F`/`000007585F`
  and returns the node class; modern prepare consumes that result at the
  `CollateSeedKeyFor*CentralGW` dispatch.  In modern `CUW.dll` the RKS
  SecurityAccess sink is byte-pinned: `27 21` request (`0x1001C102`,
  expected `67 21`) → 16-byte seed → 256-byte token → `27 22 || token[256]`
  (request length `0x107` at `0x1001C2C5`, expected `67 22`) via
  `rep movsd ecx=0x40` (`0x1001C5D4`).
- **Matching-camera software identity is directly queryable before acquisition**
  (V18 Unified CID path, byte-pinned by TMS-042):
  `TCUWCanUnifiedCIDGetter.dll` contains separate `0105` and `F18C` reads
  (positive prefixes `62 01 05` and `62 F1 8C`) and an explicit global
  discriminator string `0792`.  In its mode-2 `0792` branch it waits until
  5000 ms have elapsed and calls `CUnifiedUtils::GetSWINForFCM`.
  `TCUWUnifiedUtils.dll`'s generic `ReadSoftwareID` is independently
  `22 F1 81` / `62 F1 81`; **GetSWINForFCM is not that F181 path**.  The FCM
  helper binds direct CAN request/response strings `00000792` / `0000079A`
  and builds `22 1F FF`, expecting `62 1F FF`.  Therefore a live acquisition
  should retain the direct `0x792→0x79A` DID-`1FFF` response alongside F181,
  F18C, and the package CID.  This is an identity/provenance bridge for
  selecting the matching FRC firmware; it does not decode the camera image or
  prove that every vehicle exposes all auxiliary identity reads on the same
  route.

Boundary: this closes the host-side container/descriptor/route/writer
grammar, the payload *representation* facts, and the host-side opaque-byte
handling of `.datx` (raw read + CRC + verbatim pass, orchestration-only
archive controller); it does **not** recover the `.datx`/image decoding,
the routine blob's transform/format, `10F5`/`10F6` ECU-side semantics, or any
other ECU behavior, and none of it is EPS-specific (Corolla front camera,
not the tracked Sienna/Corolla-H EPS Unified routes of TMS-032/TMS-036).

#### 5.2.2 Retained Toyota F340 manufacturer erase/program payload

The canonical CUW corpus now also closes a previously external-only EPS flash
control reference. `T-0035-22.cuw` is pinned at SHA-256
`9882b1b6dd6acda2d142a2825eda396b0a425e41c13f822b9a18e022d4c43e81`
(5,725,237 bytes). Its descriptor is MY22 Tundra, `ContactType=P5-Unified`,
`Node01/DiagID=07A1`, with two CPU records targeting/new IDs
`8965F3401100→8965F3401200` and `8965F3402100→8965F3402200`. Both use
`ReproMethod=00`, `SecurityProperty2=98`; both declare a 4-KiB
`EraseRoutine` at `FEBF0000`.

`tools/techstream/analyze_t0035_faci_backend.py` performs a secret-free
reproduction of the retained extractor grammar: it derives the package working
key from the already-recovered payload-build root, decrypts CPUImage and
EraseRoutine regions in memory, validates CMAC, and emits only source/plaintext
hashes plus Ghidra-reviewed function-body identities. It never records SeedKey,
Nonce, the derived key, or plaintext payload bytes. Both CPU body and erase
regions validate.

`ghidra/scripts/investigate/SeedLoadedImageDirectCalls.java` closes the direct-call
graph inside each disposable loaded-RAM import before review. Disposable RH850
imports of the two CMAC-valid erase routines recover the same
manufacturer FACI contract: FRDY=`FSTATR&0x8000`, FASTAT command-lock `0x10`,
FSTATR error family `0x7040`, `FENTRYR=AA01/AA00`,
`FHVE15/FHVE3`, `FAREASELC=3B00`, `FPROTR=5501/5500`, erase `20,D0`, and
page program `E8,80`, 128 halfwords, `D0`. Crucially, each halfword is written
first and then the routine tests/waits while **FSTATR `0x400` (bit10 / DBFULL)**
is nonzero. The manufacturer payload does not use bit11/`0x800` as the
per-halfword pacing condition. It uses Forced Stop `B3`; its extracted cleanup
does not itself issue FCMD Status Clear `50`.

Exact Camry `8965F3307000` boot code independently corroborates the same
post-write `0x400` program condition at `0x78E2A` and supplies stock Status
Clear `0x50` / Forced Stop `0xB3` helpers. This is why the generic patcher now
uses bounded post-write DBFULL polling while retaining `0x50` as exact-target
recovery behavior. T-0035 remains a Tundra F340 package, not an exact F33 Camry
CUW and not an OEM full-image restore package for `8965F3307000`. Canonical
evidence: `data/generated/techstream_v18/t0035_faci_backend_evidence.json`;
SECOC-074/CORR-121.

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

#### 6.2.0 Diagnostic execution model: database -> plugin -> frame -> transport

A means-first pass over the command framework closes the ordinary diagnostic
execution spine instead of one endpoint at a time. The result is much more
regular than the screen-oriented Techstream UI suggests. In the pinned V18
`bin/` corpus, **310 of 419 DLLs export only `Execute`**, and **289** import the
shared `CommandCommon.dll` runtime. Current GTS+ preserves and expands the same
shape: **374 of 480** DLLs are `Execute`-only and **339** import
`CommandCommon`. V18 command plugins reuse `CCommCachePlus::GetCommFrmInfo` in
120 DLLs, `CommFrameSendReceive` in 49, `CFuncInfoCache::CheckEcuFunc` in 56,
and `CEcuConnectBufferList::GetBusId` in 49. These are not isolated protocol
implementations; most command DLLs are small strategy modules over one common
execution engine.

The recovered control path is:

1. `CommandAPI.dll` exposes typed host APIs and hands a command object to
   `DiagCommCtrlMain::CCommCtrlMain::CommandExecute`.
2. `DiagCommCtrlMain` constructs `CDbDllResRecords` and asks the DB for record
   class **`0x113`**. The corresponding master table is type 19
   **`CDbDllTable`**: `(ECU/category, DLL-role) -> plugin filename`.
   V18 uses `LoadLibraryA`; current GTS+ uses `LoadLibraryExW(..., flags=8)`.
   Both resolve the single exported **`Execute`** and call it under the shared
   communication critical section.
3. ECU feature discovery follows the same model. `GetEcuFuncList.dll` first
   consults `CFuncInfoCache`; on a miss it reads record classes **`0x11A`**
   (`CDbEcuFuncInfoTable`, master type 26) and **`0x11B`**
   (`CDbEcuFuncDetailsTable`, master type 27), support-gates the resulting
   functions/details, and installs the tree in the shared cache.
4. An executing plugin chooses one or more **selector IDs** and calls
   `CCommCachePlus::GetCommFrmInfo`. Record class **`0x112`** is master type 18
   **`CDbFuncCommFrameTable`**, mapping `(ECU/category, selector)` to a
   communication-set and communication-frame ID.
5. `CCommFrameData::SetCommFrame` resolves record class **`0x111`** / master
   type 17 **`CDbCommFrameTable`**. That row points into master
   `CDbVariableTable` blobs for the actual **send bytes, receive mask, and
   receive-check bytes**. `SetCommSet` separately resolves class **`0x11D`** /
   master type 29 **`CDbComSetTable`** transport metadata.
6. `CDbComSetTable` is a stable 16-byte master table: V18 has 12 rows and current
   GTS+ has 13, with the original 12 byte-identical. `FindDbItem1` keys on u16
   `+0x0A`. For ordinary `CommSet=1`, `SetCommSet` copies dword `+0x00` to the
   send-side parameter, dword `+0x04` to the receive-timeout input, and byte
   `+0x0E` to the retry bound. `CommFrameSendReceive` passes `+0x04` through
   `CheckAndConvertRcvTimeOut` before `Receive` and increments attempts until the
   `+0x0E` bound is exceeded. `+0x08`/`+0x0F` are the table's exception-handler
   ID/flag. The `+0x00` value is passed as `SendInt` argument 4 but the shared
   CAN `SendProc` does not consume that argument, so it remains deliberately
   named only `send_parameter`. CommSet 1 is `1000 / 1020 / retry=1` in both
   releases.
7. `CCommCachePlus::CommFrameSendReceive` consumes the materialized frame and
   terminates in `KGP_CommFrameCtrl::SendInt*` / `Receive*`, selecting ordinary,
   extended, or no-session variants from the frame/transport state.

The current GTS+ **outer command/session lifecycle is now instruction-closed** as
well. `CCommandCtrl::CommandExecute @ 0x1000F060` passes command `m_dwCmd`
(`+0x08`) and `m_dwEcuId` (`+0x1C`) to its role/category resolver, loads the
selected plugin, resolves `Execute`, clears the controller-owned cancel flag,
and invokes the plugin with one six-dword context containing command, response,
`CDataCtrl`, `CCommFrameCtrl`, `CDataMonitorCtrl`, and cancel-flag pointers.
`CCommFrameCtrl::LineCriticalSection(1)` is taken immediately before execution
and `(2)` releases it afterward. This is the host-side serialization contract:
one selected command plugin independently owns the J2534 line while another
plugin is executing.

Current `KGP_CommFrameCtrl.dll` then closes the transport boundary below those
plugins. `SendInt`/`SendIntExt` converge on `SendProc @ 0x10037F10`, `Receive @
0x100375B0` is the paired receive path, and `LoadDeviceDll @ 0x100363E0`
explicitly loads **`J2534Ctrl.dll`** with `LoadLibraryExW`. The framework also
owns persistent diagnostic-session state rather than requiring each plugin to
implement keepalive independently. `SendTestPresentThread @ 0x10038A20` runs on
an approximately **2,000-ms** cadence and updates `CCommFrameCtrl +0x29` from
its response; `WatchIdleThread @ 0x1003A250` separately handles roughly
3-second line-idle state.

The name `TestPresentStart` is slightly misleading for the current Camry P5
categories. `TestPresentStart @ 0x10039E70` calls DB class `0x112` with two keys,
**K1 = ECU/category and K2 = `0xDD`**. Current `CDbFuncCommFrameTable` proves the
first key is row u16 `+0x00` and the second is u16 `+0x02`. Hybrid397, Brake435,
and FRC498 therefore all resolve selector `0xDD` to CommSet1/frame `0x2B55`:
**`22 F1 86`**, receive mask `FF`, positive-SID check `62`. The keepalive thread
validates `62 F1 86 xx` and stores response byte 3 as its current-session byte.
Thus current GTS+ periodically **reads the active diagnostic session while also
refreshing diagnostic activity**. The master separately contains selector
`0x66` = `3E 00` and selector `0x67` = `3E 00` with positive check `7E`; those
frames are real but are not the request buffered by this current
`TestPresentStart` path for 397/435/498.

The same three categories share explicit session-control operands:
selector `0xD1` = **`10 01`** (default session) and selector `0xD2` = **`10 03`**
(extended session), both CommSet1. The actual wire owner is not the Data Monitor
wrapper: it is **`KGP_CommFrameCtrl::SendProc @ 0x10037F10`**. SendProc reads
master class `0x110` / `CDbEcuCategoryTable` byte `+0x48`, masks the low five
bits, and selects the P5-family session machinery for values `0x14/0x15/0x16`.
Hybrid397 (`HV_P5.ddb`), Brake435 (`ABS_P5.ddb`), and FRC498 (`FRC_P5.ddb`) all
have exact value **`0x14`**. The Phase5 request classifier at vtable `+0x100`
(`0x100292F0`) returns class 2 for service bytes `>=0x10`. When class 2 is
selected and `CCommFrameCtrl +0x29` is not already session 3, the normal path
invokes the Phase5 vtable `+0x50` sender first with `0xD1`, then `0xD2`, and
records software session 3. That sender is `0x10028490`: argument 1 is the
target ECU/category key, argument 5 is the selector, and the function performs
`GetDbRecord(0x112, category, selector)`, follows the resulting class-`0x111`
CommFrame, materializes its send bytes, and dispatches through the protocol
object. For these Camry categories the automatic wire sequence is therefore
exactly **`10 01` -> `10 03`**. Class-1 requests (`0x01..0x0F`) instead use the
DB-backed `0xD1` path and record software session 0.

There is one narrow exception to that normal session-judgment path.
`SetSessionJudgmentFlg @ 0x10039690` writes `1` to `CCommFrameCtrl +0x398`;
`ClearSessionJudgmentFlg @ 0x100326C0` writes `0`. In the SendProc branch that
checks this flag, value 1 routes both `0xD1` and `0xD2` through Phase5 vtable
`+0x54`. The Phase5 implementation at `0x100143A0` is exactly `xor eax,eax;
ret 0x18`, so no session-control frame is transmitted; SendProc then clears the
flag and still advances its software session byte to 3 on the no-op success
path. A current-bin import census finds external use of these Set/Clear APIs
only in `NoConfGenComRes_DT.dll`, around `SendIntForced`; ordinary P5 Data
Monitor/Active-Test code does not import them. This exception must therefore not
be generalized into the ordinary P5 monitor lifecycle.

`DataMonitorPhase5_DT.dll` does still reference `0xD1`/`0xD2`, but those
references are **DRS journaling, not transport**. The `+0x1DC` sink is the DRS writer path; the D1 callsite creates `CDrsChangDefaultSession` and the D2
callsite creates `CDrsChangExtendedSession`, mirroring a session change already
owned by KGP. The worker itself remains command-driven: command 9 starts Data
Monitor, 10 stops it, `0x0B` launches the direct Active-Test path, and `0x0C`
handles Active-Test initialization. Low-level `DataListIF` polling can use
no-init/no-session send variants because the outer session judgment belongs to
KGP `SendProc`, not because the session transition is absent.

Security is now narrower than the earlier generic caveat too. During current P5
monitor setup, `DataMonitorPhase5_DT.dll @ 0x10013DB2` calls
`CheckEcuFunc(dataCtrl, ecu, 3, 0x50, 0, nullptr)` before arming the phase5
security-release interface. The materialized V18 `CheckEcuFunc` implementation
confirms that this API walks the cached ECU -> function -> detail capability
hierarchy, and current master type27 `CDbEcuFuncDetailsTable` has **no function
3 / detail `0x50` row for Hybrid397, Brake435, or FRC498**. The current ordinary
P5 monitor plan therefore does not statically advertise that security-release
capability for those three categories. Teardown still contains conditional
`CancelSecurity` support for Toyota/Subaru/Suzuki mode families, so this is a
category/operation-specific negative, not a blanket claim that every Toyota
utility is authentication-free.

Finally, Toyota **check mode is a different state machine**. Hybrid397 alone
binds roles `0x17` `ConfCheckModeP5_DT.dll` and `0x18`
`ChangeCheckModeP5_DT.dll`; Brake435/FRC498 do not. Those Hybrid plugins use
RoutineControl RID `0x1002`: selector3 `31 01 10 02`, selector4 `31 02 10 02`,
and selector5 `31 03 10 02` with result check `71 03 10 02 01`. They are
maintenance/check-mode operations, not aliases for UDS DiagnosticSessionControl.

This makes the selector numbers used throughout Toyota's command DLLs effectively
**operands into a diagnostic database VM**. The DLL contributes sequencing,
fallbacks, conditionals, and specialized response parsing; the master DDB often
supplies the wire contract itself. Current GTS+ makes the reuse measurable:
**6,194 `CDbDllTable` bindings collapse to only 191 logical DLL roles**. The
highest-coverage roles are coherent command families rather than ECU identities:
`0x05` Data Monitor list (562 bindings), `0x19` DTC clear (536), `0xAD` Data
Monitor-for-Active-Test (433), `0x52` CID/software identity (359), `0x06` Active
Test list (346), and `0x08` Active Test initialization (342). `tools/gts role`
now exposes this role census directly.

The role census is now operation-aware rather than name-only. Across the same
6,194 bindings, recovered shared-runtime edges classify 2,643 as direct
transport, 1,139 as delegated transport through V18-proven support helpers,
790 as V18-proven support-cache consumers, 240 as support orchestration whose
transport edge remains unclosed, 1,323 with no recovered shared-transport edge,
and 59 whose referenced plugin file is absent from the current `bin` corpus.
These labels are deliberately scoped to the **shared runtime edge**: an
`unclosed` or `no_recovered...` result is not proof that a plugin can never perform
vehicle I/O by another route.

The generation split is especially useful. Current role `0x05` is led by
`GetDatMonListP4.dll` (227 bindings), whose V18-compatible
`CCmdSupportEcu::CheckSupportBitP4 -> CheckSupportBit` path reads an already
populated support cache. `GetDatMonListP5_DT.dll` (178) instead imports
`CCommCachePlusP5::CheckSupportPid`; the executable V18 body performs
`GetCommFrmInfo -> CommCacheSndRcvExt` when support discovery is needed. Role
`0x06` Active Test list has the same P4-cache/P5-delegated shape, and
`CreateEnableDataIdList` / `CreateEnableRIdList` independently materialize
frames and call `CommCacheEverSndRcvExt`. In contrast, role `0x19` is direct
transport for all 536 current bindings, while role `0x41` Data Monitor
signal-info has no recovered shared transport edge across all 283 bindings and
is therefore a strong metadata/conversion candidate.

Current GTS+ preserves the relevant `CommandCommon` helper exports, while the
**installed CP representation** materializes only 4,096 bytes of an 868,352-byte
virtual `.text` section. That is no longer a corpus-level body limitation. The
AgentLite-downloaded `Setup_PF.exe` contains both `GTSPlusCP\bin\CommandCommon.dll`
(the installed 356,368-byte hollow PE) plus its 792,048-byte `.dll._` sidecar and
`GTSPlus\bin\CommandCommon.dll` (the complete 1,280,016-byte original). The CP
stub and sidecar hash byte-for-byte to the installed pair, while the original
has SHA-256 `98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3`
and a materialized `0xD3600`-byte raw `.text`.

This is complete across the installed current GTS+ tree, not a one-file special
case: `Setup_PF.exe` supplies 45 protected-body twins and
`Setup_InfoCenter.exe` supplies the remaining 9, for **54/54 installed
`.dll._`/`.exe._` pairs**. `tools/gts recover-bodies` now extracts the original
same-release PEs under `build/out/gtsplus-unprotected/`, proves each installer
`GTSPlusCP` stub/sidecar is byte-identical to the installed representation, and
writes a provenance manifest. Thus V18 transfer remains useful historical
context, but current `CommandCommon` and every other protected GTS+ body can now
be analyzed directly. The main-GTS+ installer-twin evidence is documented in
[gtsplus-body-recovery.md](gtsplus-body-recovery.md). CUWPlus does not have that
plaintext-installer shortcut, but its CP loader is now independently decoded:
`tools/gts recover-cuw-bodies` restores **143/143** current protected CUWPlus
PEs (127 native, 16 CLR-labeled) under `build/out/cuwplus-unprotected/`. The same
decoder restores **52/52** auxiliary protected bodies (18 native, 34 CLR-labeled)
with `tools/gts recover-aux-bodies`, closing the full current `Toyota Diagnostics`
protected-body census at **249/249** when combined with the 54 exact main-GTSPlus
installer twins. `tools/gts recover-all-bodies` materializes all three component
corpora plus an aggregate manifest. The protector-emulation path, import/section
reconstruction, managed-image handling, product census, and six runtime-unpack
`.text` oracles are documented in [cuwplus-body-recovery.md](cuwplus-body-recovery.md).

The next interpreter layer is now closed for two representative **current GTS+ plugin bodies**, rather than transferred from V18. Current category 405 `EMPS_P5` binds role `0x52` to `GetCID_SID22_DT.dll` (SHA-256 `775aa63b…5f9c2`), and selector `0xDC` materializes `22 F1 81` / mask `FF FF FF` / check `62 F1 81`. After `CommFrameSendReceiveExt`, the plugin compares receive indexes 1 and 2 with the requested DID, computes `received_count - 4`, skips indexes 0..3, and copies index 4 onward. The payload is chunked in fixed **16-byte** records, copied into a pre-zeroed buffer, converted by `MultiByteToWideChar` with code page 0 (`CP_ACP`), and emitted as 17-character-capacity `CCmdStringName` values named `CID1`, `CID2`, … from the literal `CID` and format `%s%d`. Receive byte 3 is deliberately skipped and is **not** the record count; iteration terminates from response length. This independently reproduces the older Brake-specific role-`0x52` geometry in TMS-047 without claiming every `0x52` plugin variant has identical parsing.

Current `DelDiagCodeP4.dll` (role `0x19`, SHA-256 `8e52d52f…84c2`) also closes the sequencing around the already-decoded clear frames. It resolves selector `1` first, choosing normal versus `DifferentAddress` transport from ECU-detail metadata. When the relevant function gate is set, ten exact first-request return codes enter the fallback path: `91010009`, `90020321`, `90020323`, `A0040201`, `C0040001`, `A0040202`, `90020327`, `91020320`, `91020310`, and `91020322`; with that gate clear, only `91010009` enters fallback and is logged as the first-message timeout. Fallback selector `0x102` uses `FunctionAddress` only for bus ID `0x22`, otherwise normal addressing. If fallback returns `C0040101`, the plugin restores the original primary error (or `91010009` in the timeout-only branch) rather than replacing it. On success it sleeps for a DB timer and sets command-output `m_bDelDiagCode=1` at `+0x20`.

That sleep exposes one more master table required by a generic interpreter: record class **`0x119`** is master type **25 `CDbTimerTable`**, with 12-byte records `[delay_ms:u32, category_id:u16, timer_id:u16, unresolved:u32]`. Current `FindDbItem1` keys the category field, `ComparativeKey` adds the timer ID, and `CDbTimerResRecords::SetOriginalTable` exposes the selected raw record whose first dword is passed directly to `Sleep`. Current Hybrid category 397 timer 1 is exactly `00000000 8d01 0100 00000000`, therefore **0 ms**. `tools/gts timer HV_P5 1` exposes the same table interactively.

Current role `0x06` closes the analogous Active Test catalog layer. Current Hybrid category397 binds `GetActTstListP5_DT.dll` (33,296 B; SHA-256 `16e3a6f9…4d844`). The current plugin uses type68 `CDbActTestP5Table` (64-byte records) for direct tests and type71 `CDbRoutineActTestP5Table` (72-byte records) for routine tests; optional type33 `CDbMultiDidIdTable` expands direct tests that require multiple DIDs. Normal categories build both `CreateEnableDataIdList` and `CreateEnableRIdList`; generation-mode `0x20` switches to `CreateEnableDataIdListForSubaruCheckDID` and `CreateEnableRIdListforSUBARU`. Direct type68 rows use u16 `+0x20` as the primary DID key and are filtered through `CheckSupportDid` (or Subaru variant); when a type33 association exists, the additional DIDs are individually support-checked before emission. Routine type71 rows use u16 `+0x1E` as the RID key and are filtered through `CheckSupportRid` (or Subaru variant). Supported entries are normalized/sorted into `CCmdActTstData` (`id`, name, short name, help id). Current Hybrid generation20 takes the normal path; its DDB contains **29 type68 direct candidates and 10 type71 routine candidates**, with no type33 MultiDID table. Those are candidate counts only—the final Techstream Active Test list still depends on runtime DID/RID support state. `tools/gts command HV_P5 0x06` now reports that split explicitly.

Current role `0x08` closes the next layer for a **selected direct Active Test**. Hybrid category397 binds `GetActTstInitP5_DT.dll` (37,392 B; SHA-256 `36baa624…9d55`). The current body looks up the selected type68 row by u16 `+0x20`, then interprets `+0x39` as its initial-read mode. Mode 0 resolves master selector `0xCA` (`22FFFF`, mask `FF`, positive check `62`, CommSet1), copies type68 `+0x34` into request bytes 1/2, sends through `CommCacheSndRcvExt`, and extracts the initial value from the row's `+0x28/+0x2A` bit range; mode 1 skips that transaction, while other values return `C0040102`. Byte `+0x3C` selects the panel-key path (`+0x30` for modes 1/3, `+0x32` for mode 2), and byte `+0x3D` controls linked-monitor recovery: mode 1 copies type68 `+0x36`; otherwise the plugin scans generation-selected type62/type157 monitor rows for flag `+0x30 & 0x40` and exact DID/bit-range equality (`+0x46`, `+0x3C`, `+0x3E`), then copies monitor key `+0x34`. Final initialization joins type12 Active-Test pattern, type13 physical conversion, type14 display pattern, and type15 unit records, with `CheckSupportPanel` governing applicable display entries. Exact current witness: Hybrid direct test `0x0001` **Activate the Inverter Water Pump** has DID `0x2801`, bits 15..15, read mode 0, and therefore materializes selector `0xCA` as **`22 28 01 -> 62`**; the monitor scan uniquely resolves key30 **Inverter Water Pump**, whose typed metadata is OFF/ON. `tools/gts command HV_P5 0x08 --item 0x1` reproduces that plan offline. Boundary: role `0x08` initialization does not prove role `0x06` runtime availability, and panel support may still depend on live/cache state; `tools/gts` does not execute the Active Test.

The shared **P5 direct Active-Test runtime executor** below role `0x08` is now closed as well. It is not another category DLL role: `CommandDataLib.dll` `CStartActTstSnd::SetValue` normalizes the engineering value through the selected physical conversion and stores the normal raw value at `+0x24`; `DataMonitorPhase5_DT.dll` `CDataMonitorThreadP5::virtual_104` then combines the selected type68 row with type67 `CDbDataIdForActTable`. Type67 u16 `+0x02` is the DID key and u8 `+0x0A` selects the encoding mode. For ordinary mode 1, the executor resolves selector `0x9D` as **`2F FF FF 03`** / mask `FF` / check `6F`, substitutes the type68 DID, zero-fills the runtime DID-data length `N`, and places the raw value into the type68 `+0x28/+0x2A` bit range. It separately resolves selector `0x64` as **`2F FF FF 00`** / mask `FF` / check `6F` and appends the `N`-byte control-enable mask for return-control. `N` is deliberately not inferred from DDB geometry: the executable calls `GetSupportEcuDataIdLengthListCache -> GetDataIdLengthList -> CCmdDataIdLengthList::Search(DID)`, so only the minimum required by the selected bit range is static. The current Hybrid `0x0001` water-pump test joins type67 row `000001280000000000000100000000000000`, encoding mode1, DID `0x2801`, bit15, and raw OFF/ON `0/1`; therefore the exact formulas are `2F 28 01 03 || N-byte value` with byte1 bit0 carrying the value and `2F 28 01 00 || N-byte control-enable mask` with byte1 bit0 set. Bit15 proves only `N >= 2`; for the **minimum** `N=2`, the corresponding examples are OFF `2F2801030000`, ON `2F2801030001`, and return-control `2F2801000001`, not a claim that the live cache entry is length2. The handoff is also instruction-closed: `CDataMonitorThreadP5::virtual_20` passes `buffer+1,length-1` through `CDataMonitorPhase5Interface` vtable `+0x2C`; `DataListIF` `CCommEventPhase5AT::ActiveTestStart` re-prepends `0x2F` for direct `ActiveTestType=0`, queues start/return-control frames, `GetSndFrame` copies the queued bytes unchanged, `CheckRcvFrame` requires `0x6F` and at least three response bytes, and `p5diag_tf::J2534DiagInterface::ThreadMain` sends the frame through `KGP_CommFrameCtrl::CCommFrameCtrl::SendIntExt`. No Active Test was executed to establish this model. `tools/gts command HV_P5 0x08 --item 0x1` now exposes the executor formula and the qualified minimum-length examples alongside the existing initialization plan.

The shared **current P5 routine Active-Test executor** is now closed alongside the direct path. Its wrapper roles are deliberately generic rather than category-local: current master roles `0xB0` (`StartActTst.dll`), `0xAE` (`GetRoutineActTstInitP5_DT.dll`), `0xAF` (`GetRoutineActTstSignalInfoP5_DT.dll`), and `0xD4` (`SingleRoutineActTstP5_DT.dll`) have a category-0 P5 row. The selection mechanism is now instruction-pinned rather than inferred from that census. `DiagCommCtrlMain::CommandExecute` passes command `m_dwCmd` (`+0x08`) and the actual target `m_dwEcuId` (`+0x1C`) into the type19 `CDbDllTable` lookup. `CDbDllTable::GetQuery` first narrows by role (`+0x54`), then tries the exact ECU/category (`+0x50`); when the category stage returns no rows but the role stage is nonempty, it deliberately supplies the **first role match**. For current `0xAE/0xAF`, that first/default row is category 0/P5, followed by category-6000+ P6 rows, so category 0 is the generic P5 **fallback/default**, not the caller's target category. The selected P5 init plugin still reads the original command `m_dwEcuId` when it opens the target ECU database, preserving the real target category across dispatch. Current GTS+ type71 records are 72 bytes and must not be parsed with the older V18 offsets: `KgpDataCtrl::CDbRoutineActTestP5ResRecords::SetRecVariableData` pins RID `u16 +0x1C`, Active-Test key `+0x1E`, routine-command variable `+0x28`, routine-stop variable `+0x2A`, output-value mask `+0x2C`, output-button mask `+0x2E`; the one-shot status consumer pins `+0x30` as the type72 routine-status key, and `SortInOrder` uses `+0x40`.

`DataMonitorPhase5_DT.dll` `CDataMonitorThreadBase::virtual_108 @ 0x1000E710` is the current routine materializer. Selector `0xD5` is **`31 01 FF FF`** / mask `FF FF` / check `71 01`; selector `0xD6` is **`31 02 FF FF`** / check `71 02`; selector `0xD7` is **`31 03 FF FF`** / check `71 03`. The builder replaces bytes 2/3 with the selected type71 RID. Start appends `GetRoutineCommand` bytes and merges runtime value/button bytes only where `GetOutputMaskValue` / `GetOutputMaskButtonData` explicitly authorize them; stop analogously appends `GetRoutineStopCommand`. `CDataMonitorThreadP5::virtual_28` calls that builder through vtable `+0x6C`, then uses the same phase5 interface `+0x2C` as direct tests with `ActiveTestType=1`. `DataListIF::CCommEventPhase5AT::ActiveTestStart` therefore re-prepends **`0x31`**, de-duplicates/replaces routine queue entries by RID, and `CheckRcvFrame` requires **`0x71`**. The queued bytes reach the same P5 J2534 `SendIntExt` sink as the direct executor. Independent role `0xD4` `SingleRoutineActTstP5_DT.dll` corroborates the sequence as D5 start -> 200 ms -> D7 result request -> 5000 ms on success -> D6 stop.

The steering-relevant current witness stays deliberately narrow and strong. `FRC_P5` Active-Test key `0xA429` is **LTA Steering Vibration**, RID `0x1588`; its routine-command, stop-command, value-mask, and button-mask variable refs are all zero, while status key `+0x30` is `2`. There is therefore no hidden type71 parameter/setpoint source in the recovered current executor. Its exact current requests are **`31 01 15 88`** (start), **`31 02 15 88`** (stop), and **`31 03 15 88`** (request results). This does not mean the downstream FRC->vehicle-network effect is known. The shared current-P5 session/keepalive wrapper is closed above; live ECU state and operation success remain separate from the fixed routine payload. It also does not overwrite TMS-041: the pinned V18 `SingleRoutineActTstP5_DT.dll` family used proprietary `21 E2` / `61 E2` framing, so the two observations are retained as a versioned transport change. `tools/gts active-test FRC_P5 0xA429` exposes the current fixed request plan, and `tools/gts active-test HV_P5 0x1` provides the analogous direct-test plan; both commands are offline/read-only and send nothing to a vehicle.

Current role `0x63` closes **multi-control Active Test initialization** through `GetMultiActInitP5_DT.dll` (42,512 B; SHA-256 `ada49114…d1fc7`). The generic current body first queries type33 `CDbMultiDidIdTable` with the requested group ID: type33 u16 `+0x00` is the group key, `+0x02` is a member direct Active Test ID, unaligned u32 `+0x06` is copied into the internal `CSortData` ordering field, and u8 `+0x0B` is copied as auxiliary member metadata. It sorts those members, looks each up as type68 u16 `+0x20`, then applies the same direct-member initialization state machine as role `0x08`: type68 `+0x39` selects initial-read mode; mode0 resolves selector `0xCA` (`22FFFF -> 62`) and replaces request bytes1/2 with type68 DID `+0x34`, using `+0x28/+0x2A` as the bit slice; `+0x3C` drives panel-key handling; final member output joins type12/13/14/15 metadata into `CCmdActTstSignalDataInit`. In the current generic P5 corpus, only category372 `Engine_P5` among the 87 `GetMultiActInitP5_DT.dll` bindings contains type33 rows: 10 memberships forming five two-member groups. Exact witness group `0x004C` **Pilot Injection Volume** expands in order to `0x004D` **Pilot Injection Volume Select Cylinder** (DID `0x284A`, bits0..7) and `0x004E` **Pilot Injection Volume Value** (same DID, bits8..15), so both initial reads materialize as `22 28 4A -> 62`. Hybrid category397 binds role `0x63` but has no type33 table and therefore no static multi-control group. `tools/gts command Engine_P5 0x63 --item 0x4C` reproduces the expansion. Boundary: this is initialization/decomposition; it does not by itself recover the later value-write execution request.

Current role `0xAD` closes the Data Monitor list used by the Active Test UI as a **category-wide membership filter**, not a selected-test mapping. Hybrid category397 binds `GetDatMonListP5ForActTest_DT.dll` (39,440 B; SHA-256 `a9f96403…3abff`). Its current body preserves role `0x05`'s category-generation selection (type157 only for mode `0x60`, otherwise type62), Subaru/normal enable-list builders, candidate key u16 `+0x34`, `CheckSupportPid`, MultiPID handling, and final physical/unit `ChangeSignalLSB` conversion. The semantic difference is monitor flag bit `0x40`: when flag bit4 is set, `0x40` directly determines include/exclude; when bit4 is clear, the plugin probes PID support first and then re-tests `0x40` before final emission. Current Hybrid generation20 uses type62 and normal `CreateEnableDataIdList`; among 1,464 monitor rows, **1,411 carry Active-Test membership bit `0x40` and 53 do not**. None set bit4, so all 1,411 members require `CheckSupportPid`, and the 53 nonmembers are also runtime-probed before the final `0x40` filter removes them. `tools/gts command HV_P5 0xAD` exposes these exact counts. Boundary: membership is offline-deterministic; final support remains cache/live-ECU dependent, and role `0xAD` does not identify which one selected Active Test caused a monitor to be displayed because the plugin accepts no selected-test ID.

Current role `0x70` closes the selected direct Active Test's **signal/presentation metadata** without adding another transport edge. Hybrid category397 binds `GetATSignalInfoP5_DT.dll` (27,664 B; SHA-256 `0544b446…41b7b`). The current body iterates requested `CCmdWordId` values, looks each up as type68 u16 `+0x20`, then maps type68 pattern key `+0x26` through type12 `CDbActTestPatternTable` and physical key `+0x24` through type13 `CDbPhyDataTable`. Current consumers pin type12 `+0x15` button size, `+0x13` key-operation pattern, `+0x12` key-invalid flag, `+0x04/+0x06/+0x0C` maintenance/auto-continue/lock values, and `+0x0A` as the type14 pattern-display key. Type13 `+0/+4/+8` become Mul/Div/Offset, `+0x14/+0x15` signedness/decimal count, and `+0x0E` selects type15 unit/default text; matching type14 rows contribute value/string display entries. The plugin imports no `CommandCommon` send/support primitive and emits one `CCmdActTstSignalInfoItem` per selected ID. Exact witness `HV_P5` test `0x0001` **Activate the Inverter Water Pump** resolves pattern key10, physical key6, `Mul=1, Div=1, Offset=0`, unsigned/0 decimals, and type14 display `1 -> ON`. `tools/gts command HV_P5 0x70 --item 0x1` reproduces that metadata. Boundary: this does not prove role `0x06` live availability or execute an Active Test.

Current role `0x05` now closes the list-selection layer immediately before that metadata family. Category405 `EMPS_P5` binds current `GetDatMonListP5_DT.dll` (39,440 B; SHA-256 `8db35a64…3a07c`). The plugin masks the low byte of the master category generation field (`raw +0x48`) with `0xE0`: mode `0x60` selects current type157 `CDbDatamonitorP5Table`, otherwise type62; mode `0x20` builds support state with `CreateEnableDataIdListForSubaruCheckDID`, otherwise `CreateEnableDataIdList`. For each current 80-byte monitor record, u16 `+0x34` is the candidate ID and byte `+0x30` controls support handling without requiring speculative bit names: if bit4 is clear, the plugin calls `CCommCachePlusP5::CheckSupportPid(command, candidate_id, &supported, enable_data_id_list, 1)` and includes only a successful `supported==1`; if bit4 is set, bit0 directly includes (1) or excludes (0) the candidate without that probe. Surviving candidates pass MultiPID validation/merge and final `CCmdDatMonData` construction, including physical/unit conversion and `ChangeSignalLSB`. Thus the DDB alone can enumerate and partition candidates, but not determine runtime-probed support outcomes. Current EMPS generation20 (`0x14`) selects type62 and ordinary `CreateEnableDataIdList`; all **230/230** type62 records have bit4 clear, so every candidate requires `CheckSupportPid` before Techstream's final presented list is known. `tools/gts command EMPS_P5 0x05` exposes this partition explicitly rather than mislabeling all DDB rows as live-supported.

Current role `0x41` is now closed as the complementary metadata-only family. Category 405 `EMPS_P5` binds `GetDatMonSignalInfoP5_DT.dll` (28,176 B; SHA-256 `3bb9b8f2…20587`). Its current materialized helper resolves monitor physical-data key `+0x3A` through class `0x20D` / ECU type-13 `CDbPhyDataTable`, then copies physical `+0/+4/+8` to `CCmdDatMonSignalInfo` Mul/Div/Offset, physical `+0x14/+0x15` to signedness/decimal count, and computes bit length from current 80-byte monitor bit-end `+0x3E` minus bit-start `+0x3C` plus one. Physical `+0x0E` resolves class `0x20F` / type-15 unit metadata and default-unit text; monitor `+0x42` resolves class `0x20E` / type-14 pattern-display value/string records into the output display-info list. No frame/send primitive is imported by this plugin: it constructs the typed `CCmdDatMonSignalInfo` metadata consumed by Data Monitor. The canonical DDB semantic layer now performs that same consumer-proven join for interactive `tools/gts did` results while leaving its default API unchanged for deterministic extractors. Current EMPS witnesses are `0x1037 Steering Angle` → physical key 3, `15/1`, offset 0, signed, one decimal, `deg`, raw `-2048..2047`, graph integer `-30720..30705`; and `0x106A Cooperation Control State` → type-14 dictionary `0=Cooperation Control`, `1=Other than Cooperation Control`.

Two already-proven endpoints illustrate the same machinery. Category 397 Hybrid Control + DLL role `0x19`
`DelDiagCodeP4.dll` selects `0x01`, which materializes `04 -> 44`, and fallback
`0x102`, which materializes `14 FF FF FF -> 54`. Category 435 Brake/EPB + DLL
role `0x52` `GetCID_SID22_SAS_DT.dll` selects `0xDC`, which materializes
`22 F1 81`, mask `FF FF FF`, and check `62 F1 81`. Both routes use CommSet 1,
so the same master query also recovers raw receive timeout `1020` and one retry.

The means-first pass also found a real **V18 -> GTS+ schema migration** in
`CDbDllTable`. V18 `FindDbItem1` consumes the DLL-role key as **u8 `+0x56`**;
all V18 type-19 rows have u16 `+0x54 == 0`. Current GTS+ `FindDbItem1` instead
consumes the role as **u16 `+0x54`**, while `+0x56` is a separate field/flag.
The old shared parser treated `+0x56` as the role in both generations and thus
misreported current GTS+ `DelDiagCodeP4.dll` as role 0. The corrected parser is
version-aware; the logical role is **`0x19` (25) in both generations**. This is
recorded as CORR-125. The live Camry DTC-clear transport/result is unchanged;
only the plugin-role attribution was wrong.

Current GTS+ also namespaces master-variable references without changing the
underlying variable table. `CDbVariableTable::GetVariable` checks a base-table
state flag and, for IDs **greater than `0x2710` (10,000)**, subtracts `0x2710`
before performing the same 1-based 6-byte `[u32 relative offset][u16 length]`
lookup used by V18. This closes the apparently out-of-range current CommFrame
references directly: `0x2743 -> 0x33 -> 04`, `0x28F7 -> 0x1E7 -> 44`, and
`0x2D28 -> 0x618 -> 14 FF FF FF`. The current `tools/gts frame` command applies
that exact normalization, so selectors can now be resolved interactively from
current GTS+ all the way to send/mask/check bytes.

The architectural implication for a portable Toyota diagnostic runtime is now
concrete: implement this shared DB interpreter and a growing library of plugin
semantics rather than reproducing individual Techstream screens or hard-coding
one DID/service at a time. `tools/gts command <category> <role>` is the joined
read-only view over that model: it resolves the selected category's own plugin,
frames, CommSets and timers, then attaches executable semantics only when the
selected plugin SHA-256 exactly matches a recovered profile. A filename/role
match with changed bytes deliberately returns an unrecovered semantic state and
no inferred parser/selector plan. Specialized parsers, retries, session
transitions, security algorithms, and state machines still live in executable
plugins and must be recovered honestly; the common interpreter does not make
those behaviors declarative. The deterministic architecture artifact is
`data/generated/techstream_v18/diagnostic_execution_model.json`, produced by
`tools/techstream/extract_diagnostic_execution_model.py` and verified by
`tests/verify_techstream_diagnostic_execution_model.py`.

#### 6.2.1 EMPS_P5 application-interface correlation

A targeted pass now closes one previously useful-but-unproven diagnostic
vocabulary join without projecting names from text alone. The `EMPS_P5.ddb`
master route is section-16 record **374**, category **405**, generation **20**,
identical in NA/EU/JP. Its eight DLL roles include
`GetDatMonListP5_DT.dll` and `GetDatMonSignalInfoP5_DT.dll`. The latter provides
the consumer proof for additional type-62 monitor metadata: physical-data key
at `+0x2A`, bit range at `+0x2C/+0x2E`, and pattern-display key at `+0x32`.
The physical-data record then selects a unit-table record. The same plugin now
also closes the numeric conversion layout: exact machine-code copies
`CDbPhyData +0/+4/+8` into `CCmdConversionTbl` Mul/Div/Offset and carries
`+0x14/+0x15` into signed/decimal-point metadata. For monitor 17 `Steering
Angle`, physical-data key 3 is identical across NA/EU/JP: Mul `15`, Div `1`,
Offset `0`, signed, decimal-point count `1`, unit `deg`, raw range
`-2048..2047`, graph range `-30720..30705`. Therefore the displayed raw H DID
`0x1037` count is exactly **1.5 degrees/count**. Monitor 305 `CAN Vehicle Speed
(SP1)` independently pins conversion direction (`0..30000`, Mul/Div `1/10` ->
graph `0..3000`, one decimal place -> `0.0..300.0 km/h`).

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
the Q-current PI loop. That command is not LTA-specific. The corrected
fixed-map provenance in the Corolla variant report goes further: the retained
Sienna-homolog conditioner is live under GP-relative writers; B6 signals262/263
percentage-modulate contributors; and B6 signal255 is recovered as the signed16
target-steering-angle command through `FEBE7D94 -> FEBEF1CC -> FEBEAE82`.
Its target-vs-measured controller conditionally feeds the same general torque/Q-
current chain observed here. Physical B6 scaling and upstream producer semantics
remain separate from these Techstream observer names.

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

The P5 DTC path supplies an OEM **immediate sender relationship** for B6. H's
six-row communication-monitor scheduler maps receive-status slot `0x18` to the
B6 unpacker/PDU42. Failure of that row selects Dem event `0x0143`; H's event
and DTC tables resolve it to packed `0xC12987`, and the exact `EMPS_P5` type-65
record names it **U012987 `Lost Communication with Brake System Control Module`
/ `Missing Message`**. `0x0D7` and `0x0D5` share the same DTC. This exact
firmware→Techstream join means EPS monitors B6 as Brake-System-Control-Module
traffic. It does **not** classify each B6 field as a brake quantity: the independent
H control-dataflow proof now shows signal255 is target steering angle. What remains
unresolved is how FRC/gateway state reaches the brake-side producer and how that
protected command is sourced/authenticated.

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

#### 6.2.2 True-TSS3 lateral control: Front Recognition Camera 2 (`FRC_P5`) and its read-only FFD capture path

A directed follow-up to the newer-Toyota lateral-control gap, closed at schema
v2 from the raw corpus (not from the earlier ADS/LDA framing). Toyota's master
database maps generation-20 categories identically in NA/EU/JP:
`EMPS_P5.ddb` = **EMPS** (405), `LDA_P5.ddb` = **Lane Departure Alert** (418),
`Fr_Camera_P5.ddb` = **Front Recognition Camera** (430), `ADS_Eth_P5.ddb` =
**Advanced Drive Control** (476), `ADeU_Eth_P5.ddb` = **Advanced Drive eXtension
Control** (477), **`FRC_P5.ddb` = `Front Recognition Camera 2` (498)**, and
`EMPS2_P5.ddb` = **Steering Actuator** (499). `FRC_P5` is a distinct category
from the old `Fr_Camera_P5` and from `ADS_Eth_P5`; its exact file identities
are pinned per region (NA 49,806 bytes / SHA-256 `63307a9b…46fe42`, EU and JP
49,662 bytes / `b35ca0ac…84e1cc` and `89db9903…7bba5e`).

**Dedicated plugin roles.** The master type-19 DLL table assigns role 233
`GetTSS3ImageFFDP5_DT.dll` and role 234 `GetTSS3OperationFFDP5_DT.dll`
both to category 498; roles 224/225 (`GetADSOperationFFDP5_DT.dll` /
`GetADSImageFFDP5_DT.dll`) are bound to `ADS_Eth_P5` category 476, and role
229 (`GetADSDDRInfoP5_DT.dll`) is a **category-0/global** entry, not an
ADS-category binding. This is the strongest role-association signal for the
diagnostic domain: the true-TSS3 lateral-control diagnostic domain has its
own capture-plugin roles bound to category 498, separate from the Advanced
Drive Ethernet stack's category-476 roles. It is a diagnostic-domain/role
association, not a claim of physical or control-path ownership.

**Installation join (model-resolved, region-local).** The master type-44 table
is `CDbInstallingEcuListTable` (format-1 factory `0x1001C9D0`); records are 24
bytes with display-name string index `u32 +0x00`, **install-set ID `u16 +0x04`
(the `FindDbItem1` lookup key)**, and ECU category `u16 +0x06`. The install-set
ID resolves deterministically to model names through type-5 `CDbEcuGroupTable`
(VehicleId `u16 +0x04` → install-set ID `u16 +0x06`) and type-43
`CDbVehicleNameTable` (VehicleId `u16 +0x04` → name `u32 +0x00`); 2480/2481 NA,
4924/4925 EU, 1627/1628 JP type-5 VehicleIds resolve to type-43 names (one
sentinel each). In the **NA** master, categories 498 and 499 co-occur at
exactly install sets `0x1967`, `0x1B1A`, `0x1D54`, `0x1E6E`. Those sets also
contain 405 (EMPS), 418 (display name **`Lane Control`**), 430 (Front
Recognition Camera), 476/477 (Advanced Drive Control / eXtension Control) plus
brake/steering-angle/camera neighbors; `0x1D54`/`0x1E6E` resolve the steering
trio as `EMPS / Steering Control Actuator` (405), `Front Recognition Camera`
(498), and `Steering Torque Actuator` (499). The NA keys resolve by name to
**MAC (0x1967/0x1B1A), RZ450e (0x1D54), bZ4X (0x1E6E)**; install-set
numbering is **region-local — the numeric NA keys `0x1967/0x1B1A/0x1D54/0x1E6E`
also exist in the EU/JP masters but resolve different category sets there and
never carry the 498+499 pair**; each region has its own distinct 498+499 keys
(EU nine: MAC×2, bZ4X×6, RZ450e; JP four: MAC×2, RZ450e, e-Palette). The 498+499 co-occurrence sets are **not Corolla
evidence**. The direct Corolla-family evidence is separate: exact NA
VehicleId/install-set rows 0x30E0/0x1D78, 0x30E1/0x1D7B, 0x30E4/0x1D84,
0x30FE/0x1DD2, 0x30FF/0x1DD5 (Corolla), 0x30E2/0x1D7E, 0x30E3/0x1D81
(Corolla HV), 0x311F/0x1E35, 0x3120/0x1E38 (Corolla Cross), 0x3121/0x1E3B
(Corolla Cross HEV) all carry **FRC 498 + EMPS 405 and no EMPS2 499**;
GR Corolla 0x3082/0x1C5E instead pairs 498 with **EMPS_P4 142**.

**`FRC_P5` lateral-control surface (exact rows).** DID `0x1202` bits 12/13
are `LDA`/`LTA Installation Availability`; DID `0x1501` carries `LDA Customize
Condition Flag` (bits 0–7) and `LDA Control Condition` (bits 8–15); DID
`0x1601` carries `LTA Switch Condition Flag` (0–7), `LTA Control Condition`
(8–15), `Hands-Off Customize Condition Flag` (16–23), and `Hands-Off Control
Condition` (24–31). Current GTS+ also resolves the exact PatternDisplay values:
**LTA Switch 0=OFF / 1=ON; LTA Control 0=LTA Enabled / 1=LTA Disabled;
Hands-Off Customize 0=OFF / 1=ON; Hands-Off Control 0=Hands-Off Enabled /
1=Hands-off Disabled**. Thus a synchronized read returning switch `1` plus LTA
control `0` is an OEM-named **LTA-enabled diagnostic-state oracle**; it still does
not, by itself, prove continuous steering-torque output. `Steering Wheel Information` is DID `0x1308`; `Control
Target Type (For DDR)` is `0x1806`; `Control Mode` is `0x1903`; `Forward
Vehicle Lateral Position` is `0x1909` bits 0–31; and the control-target
distance/side DDR values are `0x1804`/`0x1805` bits 0–31. Type 87 additionally
carries `Lateral Control System Malfunction` (X2400), `Steering Angle Sensor
Malfunction` (X2001), `Power Steering Control System for Steering Assist
Steering Angle Malfunction` (X2082), and `Communication Error by ECU Security
Key Not Registered (Power Steering Control Module "A")` (X2166). A verified
negative: `FRC_P5` has **no** named `Target Steering Angle` monitor in the
type-62 `CDbDatamonitorP5Table` or the type-88 `CDbBehaviorDataRecordP5Table`
in any region — the target-angle observer text lives on the steering side, not
the camera side.

**Read-only proprietary Operation FFD protocol** (`GetTSS3OperationFFDP5_DT.dll`,
SHA-256 `8d8461cf…38f86`, all claims anchored to exact machine-code bytes
pinned by the independent test, no Ghidra required): the behavior-code query
at `0x100010E0` builds request `AB 11` and expects `EB 11`; the behavior-frame
query at `0x100021D0` builds `AB 12 <behavior_id BE16>`, expects `EB 12`, and
parses subordinate BE16 IDs after offset 4; the data-record query at
`0x100015A0` builds `AB 13 <behavior_id BE16><record_id BE16>` and expects
`EB 13`. Its parser at `0x10001A70` starts data at offset 6 and parses
`[DID BE16][len u8][len bytes]` blocks, using the first data byte as a block
count when nonzero and deduplicating by DID; `0x10001F90` special-cases DID
`0x0501`. `Execute` at `0x100032F0` obtains comm-frame info with selector
`0x66` and runs through `CCommCachePlus::CommFrameSendReceiveExt`. A fixed
special/excluded ID table at VA `0x100091D4` holds 15 LE u16s (`0x2270`,
`0x2271`, `0x2272`, `0x2273`, `0x2274`, `0x2296`, `0x2297`, `0x2298`, `0x2299`,
`0x227C`, `0x227D`, `0x229A`, `0x22B0`, `0x22B1`, `0x22B2`) — these are
proprietary operation/behavior IDs, **not** UDS DIDs, unless independently
resolved. This is observation/capture infrastructure only; the repository
deliberately builds no live writer against it.

**Image FFD plugin** (`GetTSS3ImageFFDP5_DT.dll`, SHA-256 `787f88b5…63e4`):
the support probe at `0x10004420` issues `GetDataNoEnableList` for DID `0x1402`
selector 1 then selector 2, and DID `0x1401` selector 2 — both DIDs exist in
`FRC_P5` as `AHB Control ON Information` and `AHB/AHS Information`. The main
capture path is `CCmdImgOpeDdr::GetTSS3ImageFFDInfo`. The immediate `0x1CE4`
seen elsewhere in this DLL is an allocation size passed to the `0x1000C62E`
allocator, **not** a DID.

**ADS remains useful but secondary.** `ADS_Eth_P5` type-134 rows 406/407 name
`Advanced Drive Control Target Steering Angle Speed Order Value` and
`…Target Steering Angle Order Value` (row 143 = `Lateral Control Switch
Status`). `GetADSDDRInfoP5_DT.dll` (SHA-256 `28a4474c…46df`) reads the row
fields `+0x28` (PhysicalData key), `+0x2A`/`+0x2C` (bit start/end), and `+0x30`
(PatternDisplay key); the unit chain row `+0x28` → CDbPhyData key `+0x0C` →
PhyData `+0x0E` unit key → CDbUnit key `+0x04` → `GetDefaultUnitStr` resolves
row 406 to bits 0–31 **rad/s** and row 407 to bits 0–31 **rad**. These are
Operation-FFD/DDR recorded snapshot fields, **not** proven live wire command
fields. The ADS Operation plugin probes its own plugin-specific DID `0x1C08`
with selectors 1 and 6; that probe is not joined to rows 406/407 without
further proof.

**Steering-side observer domain.** Both `EMPS_P5` and `EMPS2_P5` carry the
2069..2076 monitor family (`Target Lateral ID`, `Cooperative Control in
Progress Flag`, `Target Steering Angle After Output Compensation`, `Advanced
Drive Target Steering Angle`, plus System-2 variants) under DIDs
`0x1CEE`/`0x1CEF`. A full corpus scan (402 P5 databases, NA/EU/JP) verifies
these two DIDs are declared as **type-62 primary Data-IDs only** in
`EMPS_P5` and `EMPS2_P5`. Exact Corolla H
`8965H1202000` implements neither DID.

`LDA_P5` still contributes the ownership vocabulary — `Steering Assist Request
Invalid` and the exact Toyota text `Communication Error from Lane Control
Module to Power Steering Control System` — without proving that `LDA_P5` is
itself a physical Lane Control Module.

This evidence deliberately stops short of a wire mapping: no CAN/CAN-FD
arbitration ID, wire layout, producer ECU, or authentication is identified for
any target-angle value, and the community `NEW_MSG_8A_LAT_CONTROL` lead
remains unjoined to `FRC_P5`. The Reference screenshot corpus
(REFERENCE/CorollaExp_Screenshots.md) pins exactly one fact — `0x18A` appears
among the 22 CAN-FD 64-byte IDs observed on buses 0 and 2 — and nothing more;
do not encode a DBC from it. Protocol claims in the artifact are graded:
subtypes/markers/parser offsets/table bytes are byte-anchored, while
response-layout wording and block-count/dedup semantics are recovered
interpretation. The AB/EB FFD protocol is read-only capture infrastructure,
Category 498 also exposes an **Active-Test surface**, and that branch is now
closed far enough to classify it. `FRC_P5` contains **no type-68
`CDbActTestP5Table`** in NA/EU/JP; its steering-related entries live in the
type-71 `CDbRoutineActTestP5Table`. Exact routine IDs are `0x1508` **LDA
Steering Vibration**, `0x1588` **LTA Steering Vibration**, `0x15C8` **LCA
Steering Vibration**, and `0x160B` **AES Automatic Steering in Control
Notification**. For all four rows, the type-71 routine-command, output-mask,
and output-mask-button variable references (`+0x28/+0x2A/+0x2C`) are zero.
The three vibration rows use routine-status key 2; type-72 resolves that key
through master variable `0x0054` to the single status byte `02`.

The generic executor `SingleRoutineActTstP5_DT.dll` performs an exact
`D5 -> 200 ms -> D7 -> 5 s -> D6` sequence. Raw master type-17 comm-frame
records resolve all three selectors to send prefix `21 E2` and response prefix
`61 E2`, with receive masks `00 00 00 08 00`, `00 00 00 04 00`, and
`00 00 00 02 00` respectively. The executor writes the routine ID big-endian
into request bytes 2/3; only the D5 phase can append `GetRoutineCommand()`
bytes, and the steering-vibration records have none. Their fixed requests are
therefore `21 E2 15 08`, `21 E2 15 88`, and `21 E2 15 C8`. This is **not** a
parameterized steering writer: Techstream exposes no angle, torque, vibration
amplitude, or continuous lateral setpoint through these records. No explicit
SecurityAccess/authentication/session-named import appears in the
SingleRoutine/Init/SignalInfo plugin chain, but that negative does **not** prove
the ECU accepts the routines without an outer session or authentication.

What remains bounded is the **downstream vehicle-network effect** of those
fixed FRC routines. In particular, `0x1588` is now a concrete high-information
probe: invoke LTA Steering Vibration while capturing FRC output, or locate its
handler in `FRC_P5` firmware and trace the network transmit path.

The P5 master/DTC corpus now narrows the upstream topology further. Across
NA/EU/JP, Toyota master category **435** is generation-20 **`ABS_P5.ddb` =
`Brake/EPB`**; it is not the separate category-485 `EPB_P5.ddb` (`Electric
Parking Brake`). Every Corolla-family install set in this artifact that carries
`FRC_P5` 498 plus `EMPS_P5` 405 also carries category 435. `FRC_P5` type-87
contains the exact directional behavior **X216E `Front Recognition Camera => BRK
Communication Invalid`**, while its DTC table independently carries U012987
`Lost Communication with Brake System Control Module "A" / Missing Message`,
U013187 `Lost Communication with Power Steering Control Module "A" / Missing
Message`, and U015E87 `Lost Communication with Automated Driving System Interface
Module "A" / Missing Message`. Category-435 `ABS_P5` in turn carries U013187 and
U11B187 power-steering missing-message records, U11A987 for the Automated Driving
System Interface module, and DID `0x102F` bit 74 `EPS/Steering Control Actuator ECU
Communication Open`.

The same brake diagnostic family exposes one steering-target-like observer:
monitor key 314 / DID **`0x107E ADS Control EPS Pinion Angle2`**, bits 0..23. The
`ABS_P5` PhyData chain resolves it as signed `Mul=25`, `Div=1`, `Offset=0`, five
decimal places, unit `rad`: **0.00025 rad/count** over raw
`-131072..131071`. `Brk_Bst_P5` (466) and `EPB_P5` (485) use database-local
PhyData keys but independently resolve the same name, geometry, range, and
engineering conversion. This is shared brake-family diagnostic vocabulary, not
proof that category 435 computes the value or that `0x107E` is the B6 wire
scalar.

Joined to exact Corolla-H evidence—protected B6/PDU42 loss maps to U012987 `Lost
Communication with Brake System Control Module / Missing Message`—these records
**verify the FRC/Brake/EPS module-dependency topology**, but not a byte-level
FRC→Brake→B6 forwarding path. FRC also has a direct EPS communication dependency,
and both FRC and ABS reference an Automated Driving System Interface module.
A follow-up category-435 Active-Test pass also closes a host-side shortcut.
`ABS_P5` has 20 direct type-68 `CDbActTestP5Table` records and four type-71
`CDbRoutineActTestP5Table` records, byte-identical across NA/EU/JP. Consumer
anchors in `KgpDataCtrl.dll` pin type-68 record size 64, name string index
`u32+0x0C`, lookup key `u16+0x20`, sort key `u16+0x2C`, exception ID
`u16+0x2E`, and exception flag `u8+0x3B`. The direct catalog resolves only to
brake actuators: Motor/Solenoid/Stop-Lamp/ECB relays, EXO, Brake Booster Motor,
linear solenoids, and ABS/VSC/ECB solenoids. The four routines are `EBS Relay`,
`ABS Solenoid`, `VSC Solenoid`, and `ECB Solenoid`; all have zero routine-command,
output-mask, and button-data variables. No category-435 Active-Test catalog row
is named for steering, EPS, ADS, lateral control, or pinion angle. This is a
catalog/host-schema negative, not proof that brake actuator tests have no indirect
network effects, but it rules out a named Techstream Brake/EPB steering-setpoint
writer in the pinned corpus.

The acquisition discriminator for that brake-side firmware is now exact enough
to stop searching by vague ECU name. Raw `ECU_Setting_Table` rows in all three
P5 VDS regions map category **435** at phase 5 to first tagged diagnostic request
address **`7B0`**; the first 40 bytes are identical in NA/EU/JP (SHA-256
`09420f52…303b07`). The same row's second tagged ASCII token is **`7E5`**.
Techstream's own `CGetBigDataSettingInfo` SQL names the corresponding VDS
columns exactly `ECUSetting.Address AS Address` and
`ECUSetting.FuncAddress AS FuncAddress`. Across the raw NA phase-5 table, the
rows carrying both values form the complete standard functional-address family:
`700→7E0`, `701→7E1`, `7D2→7E2`, `747→7E3`, `7C4→7E4`, **`7B0→7E5`**,
`724→7E6`, and `745→7E7`. Category 435 is therefore exactly
**`Address=7B0`, `FuncAddress=7E5`**. Legacy
`SUW/InternalCF/Db/RpAppOsT.ini` FileVersion `17.0.13`
independently maps `SYSTEM9=8,VSC/ABS/ECB` to `CANID1=7B0` and EMPS to `7A1`;
its shared `SK1=63511974` is only a legacy configuration token and is **not**
transferred into P5 SecurityAccess or SecOC semantics.

Modern CUWPlus does not introduce a hard-coded FRC-only address in this route.
Decoded `P5-Unified04.ini` selects the Unified CID getter and ReproStd prepare/
flash writers while all three CAN-ID callbacks are `GetCanIDsFromCANIDTable`;
its explicit `CanIDForGetCID`/prepare fields are blank. The package descriptor's
`Node01/DiagID` is therefore the concrete local acquisition discriminator. A
complete identity/descriptor inventory of the **26** current `software/Techstream/cuw`
packages contains six `0792` FRC packages and three `07A1` EPS packages but
**zero `07B0` packages**. That is a local-corpus absence only; it does not prove
Toyota/TIS lacks a category-435 package.

V18 first narrows the software-identity lookup from the CUW side.
`TCUWCanUnifiedCIDGetter.dll` imports `CUnifiedUtils::ReadSoftwareID` and calls it
on the normal node path **before** its mode-specific dispatch; the imported
implementation is byte-pinned as UDS `22 F1 81` with expected `62 F1 81`. The
only recovered extra SWIN path is the unique mode-2 camera special case: a
single `0792` literal is constructed into the comparison object, and only that
branch calls `GetSWINForFCM`, which uses direct `0x792→0x79A` transport and DID
`0x1FFF`. The CID getter contains no `07B0` literal, so the camera's `1FFF` path
must not be transferred to Brake.

TMS-047 independently closes the **actual category-435 diagnostic CID reader**,
removing the remaining F181 ambiguity without assuming an absent CUW's contact
type. In every NA/EU/JP master, category 435 role **82** is exactly
`GetCID_SID22_SAS_DT.dll` (61,440 B, SHA-256 `d639ced3…e378`). Its primary
helper asks `CCommCachePlus::GetCommFrmInfo` for selector `0xDC`. Raw
`CDbFuncCommFrameTable` maps `(category=435, selector=0xDC)` identically to
`ComSet=1`, `CommFrame=0x444`; that frame's variable references are
`0x0581/0x009F/0x0583`, resolving from the master `CDbVariableTable` to exact
**send `22 F1 81`, receive mask `FF FF FF`, receive check `62 F1 81`**. Thus
Techstream's category-435 Brake/EPB diagnostic path itself reads F181 at the
already-closed physical `Address=7B0`.

The response parser is also byte-bounded. `CommFrameSendReceiveExt` validates
the positive service response and stores received bytes in `CCommFrameData`'s
runtime receive list. `GetCID_SID22_SAS_DT` checks received indexes 1/2 against
`F1/81`, computes `received_count - 4`, skips indexes 0..3, copies index 4 onward,
and groups the copied bytes into fixed **16-byte** entries emitted as `CID1`,
`CID2`, … through 17-byte C-string buffers. The byte immediately after the DID
(received index 3) is therefore excluded from the CID material; the plugin does
**not** use that byte to determine how many records to emit, instead terminating
from response length. A separate non-SAS helper contains selectors `0xAC/0xAD`,
but category 435 has no corresponding FuncCommFrame rows and `Execute` explicitly
clears a nonzero result from that helper. It is supplemental, not the Brake CID
transaction. This closes the live read protocol; the **actual CID value** still
requires a live target or a retained diagnostic capture.

TMS-048 closes the apparent offline resolver lead: V18 `SearchCal.dll` is a
**local CUW search/selection UI**, not a Toyota/TIS package catalog client. The
pinned 49,152-byte PE (`a47d859f…1f72b`) exports only
`ShowSearchCalDialog @ 0x100014F0`. Its import DLL set is exactly MFC42, MSVCRT,
KERNEL32, USER32, and SHELL32; it imports `GetPrivateProfileStringA`,
`GetPrivateProfileIntA`, string/memory helpers, UI calls, and `ShellExecuteA`, but
no WinINet/WinHTTP/URLMON/Winsock, database, or XML client. The export accepts one
C-string argument and copies it to a local path buffer with `strncpy(...,0xFF)`.
Pinned `Techstream.exe` dynamically loads the DLL, resolves `ShowSearchCalDialog`,
and calls it with a CString initialized from its global empty string, so no live
CID, vehicle object, hidden repository path, or server URL is supplied through the
API.

The candidate universe is then built from files already on disk. The scanner
appends the exact wildcard `\*.cuw` to the selected directory and uses the local
CUW/INI grammar. Its embedded keys include `[Vehicle]` metadata (`EngineType`,
`System`, `ModelYear`, `ContactType`), `NumberOfCalibration`, `CPU%02d`, `NewCID`,
`NumberOfTargets`, `%02d_TargetCalibration`, `NumberOfNode`, and `Node%02d`; it
recognizes `P5-Unified` and `Ethernet` contact-type prefixes and compares the
recovered descriptor strings locally. The exact semantic direction of every
`NewCID` versus target-calibration comparison remains bounded. When the operator
chooses a result, the only external-process action is `ShellExecuteA` with verb
`open` on the assembled selected local path. Therefore a Brake F181/CID learned
through TMS-047 can help **match an already-present CUW**, but SearchCal cannot
discover or download a missing `07B0` package by itself. Remote Toyota package
availability remains outside SearchCal itself; TMS-049 closes the separate
Toyota/TIS acquisition path that populates the local calibration store.

TMS-049 closes that **remote calibration-acquisition handoff and its ECU search
inputs**. Pinned `tiswebapi.dll` (565,248 B, SHA-256 `73d8251c…e55fe`) exports
`TisServiceSendSearchInfo`, `TisServiceGetSearchInfo`,
`TisServiceDownloadCalFile`, and `TisServiceGetCalFileURL`; its protocol
vocabulary includes `Filename`, `Filesize`, `CalibrationFile_URL`,
`CalibrationId`, `NewCalibrationId`, `ecuhardwareid`, and `ecusoftwareid`.
Techstream supplies the `ECUSupplyChange_upload|URL` / `ECUSupplyChange_Login|URL`
(and get-cal counterparts) configuration, submits a generated search XML, polls
for search results, requests the selected calibration file, and polls until the
download URL becomes available. The `strSoftwareId` logged beside the XML path is
**not** an ECU CID: the caller fills it through `CTISCommon::GetPecID` before
`TisServiceSendSearchInfo`, so it is Techstream/client PEC identity.

The uploaded search criteria are instead explicit in
`SaveEcuSupplyChangeSendXmlFile`. Its `reqData` document carries a 17-character
`vinNo` and repeated `ecuInfo` records containing `ecuId`, `ecuAssyNo`,
`writeFlg`, and `baseSwNoLst/baseSwNo`. `AddEcuSupplyChangeDataPerEcu` obtains
those identity values through `GetPartNumberAPI`: Toyota's own receive vocabulary
names `m_strEcuPartNum` and `m_cSoftPartNumArray`; the former is copied to
`ecuAssyNo`, while every non-empty software-part string is appended to the list
that becomes `baseSwNoLst`. The phase-5 `GetPartNumber_DT.dll` path is byte-pinned:
category 435 selector `0x66` resolves identically in NA/EU/JP, and the plugin
materializes two requests. **`22 01 05` / `62 01 05`** supplies the ECU part
number. **`22 F1 81` / `62 F1 81`** supplies the software-part-number array: the
plugin reads response byte 3 as the record count and parses fixed **16-byte
records starting at byte 4**. Thus the same Brake/EPB F181 record geometry closed
in TMS-047 is directly the Toyota/TIS **`baseSwNo` search input** at physical
`7B0`; `22 01 05` supplies the accompanying `ecuAssyNo`. This is a stronger join
than merely calling F181 a generic CID.

TMS-050 closes the previously bounded **search-result → selected get-cal request**
bridge. `LoadEcuSupplyChangeDownloadXmlData` parses the returned `resData` tree,
including `systemAssyInfo/improvementInfo` and `systemAssyInfo/restoreInfo`.
Each system-assembly record contains, in order, `systemAssyNo`, `displayVersion`,
`numberingType`, `canOTA`, `canWired`, `updateFlg`, and `comment`. The recovered
wired-choice control flow requires the first improvement record to have
`canWired == "1"`; with multiple records it walks subsequent records and marks
the **last entry in the leading contiguous `canWired == "1"` prefix** (with the
single-entry case selecting that first record). A later, independent eligibility
pass checks whether an improvement record has `updateFlg == "1"`. `canOTA` is
parsed, but no direct `canOTA` test occurs in the two byte-pinned wired/update
policy blocks; this is a bounded negative, not a claim that the field is unused
everywhere in Techstream.

Per-ECU `supplyInfo/selectSwInfo` candidates independently parse `swId`, `comment`,
`fileName`, and `downloadFlg`. The selection page carries the software identity,
filename, and download flag into hidden columns consumed by
`SetTargetCalFileInfo`. That routine accepts selected rows, derives `swType`
client-side from candidate kind/subtype, normalizes them into **0x64-byte target
records**, and deduplicates on target offsets `+0x18` / `+0x1C`. For the
`selectSwInfo` supply-candidate path, recovered dataflow identifies the server
`swId` as the value eventually serialized as get-cal **`swNo`**, while the
server `fileName` becomes get-cal **`fileName`**. `systemAssyNo` remains a
distinct assembly/policy identifier; no equality with `swId`/`swNo` is inferred.
`downloadFlg` is preserved as integer target metadata, but local-file presence is
checked separately.

Before the remote request, `FindCalFile` clears a dedicated remote-needed list,
walks the selected 0x64-byte target array, resolves each local calibration
filename against the `*.cuw` store, and appends only missing targets. The get-cal
serializer then walks that filtered list (`this+0x144`, count at `+0x14C`) and
writes repeated **`swNo` / `fileName` / `swType`** fields to
`SC_<id>_<timestamp>.xml`. `ExecuteEcuSupplyChangeGetCalFile` hands that request
to `DownloadCalFiles`; its wrappers call `TisServiceDownloadCalFile` and, while
the URL/result is pending, `TisServiceGetCalFileURL`.

The resulting calibration URL enters `CEcuSupplyChangeFuncProc::DownloadCalFiles`,
which dynamically loads `IT3TechstreamDotNetUtilityAPI.dll` and resolves
`EcuSupplyChangeAutoDownloadCalFileAPI`. That bridge calls managed
`IT3TechstreamDotNetUtility.dll::CEcuSupplyChange::EcuSupplyChangeAutoDownloadCalFile`.
The managed IL validates `strDownloadUrl` / `strDestinationDir`, creates a
timestamped temporary tree, executes `System.Net.WebClient::DownloadFile`,
uncompresses the downloaded archive, recursively expands nested `*.zip` files,
copies the extracted files into the destination with overwrite enabled, and
removes the temporary tree. The closed host path is therefore **vehicle ECU
identity → F181 `baseSwNo` + `0105` `ecuAssyNo` + VIN → Toyota/TIS search →
`resData` candidate/assembly policy → selected `swId`/`fileName` → local-presence
filter → get-cal `swNo`/`fileName`/`swType` → calibration URL → ZIP
download/extraction → local calibration store → SearchCal/CUW processing**.
Static analysis still does not prove that Toyota's current service will return a
package for any particular VIN/`baseSwNo`, does not recover the server-side
matching algorithm, and does not supply the missing live Brake values by itself.

TMS-052 also supplies a concrete public Brake acquisition family without
pretending it is the target car's identity. Toyota's official 24TC01 technical
instructions cover **certain 2023 Corolla** Brake/EPB software and publish
`F152612A5100`, `F152612A5200`, and `F152612A5300` as current CIDs converging on
**`F152612A5400`** (NHTSA mirror `MC-11005140-0001`, SHA-256
`b178aebd…2151`). The complete raw 26-CUW **descriptor census** contains neither `DiagID=07B0`
nor any of those published Brake CIDs. The historical Toyota calibration-link grammar supplies candidate path
`/t3Portal/calibration/F152612A5400`, but an anonymous 2026-08-25 falsification
check showed the TechInfo auth gateway preserves a nonsense calibration suffix in
`original_request_url` identically. The redirect therefore proves **neither CID
recognition nor package availability**; 24TC01 itself is the evidence for the CID. Machine-readable campaign/corpus correlation lives
in `data/generated/techstream_v18/corolla_2023_calibration_acquisition.json`.

Therefore the next directed acquisition step is now external and exact: on the
target vehicle, read category-435 Brake/EPB at physical **`7B0`** with **F181**
(and preserve the `22 01 05` ECU-part-number response plus VIN), then submit the
normal ECU-supply-change search, preserve the returned `resData`, and retain the
returned `07B0` package if Toyota serves one. Once acquired, analyze that
category-435 firmware together with an exact-target identity/decode of the already-
owned 23TC01 `0792` Corolla FRC family (or a later matching family)—or capture
synchronized stock-LTA traffic—to recover the remaining
FRC/Brake→protected-B6 transformation and SecOC signer/key/freshness ownership.
The FRC and Brake/EPB Techstream Active-Test catalogs are exhausted as setpoint-
writer candidates.

TMS-051 additionally exhausts the **sender-attribution work possible from the
current CUW/P5 corpus** rather than leaving another broad binary search implied.
The exact-H EPS endpoint already labels B6 as Brake System Control Module traffic;
protected `0x0D7` shares that source-domain DTC, and `0x00F/0x0D7/0x0B6` all select
the same H SecOC config/job0 → ICU-S slot-4 authentication key. Joined to Corolla
P5 category 435 `ABS_P5 = Brake/EPB`, this identifies the immediate authenticated
B6 **source family** as Brake System Control / category-435 Brake/EPB. It does not
identify the code-level originator, forwarder, CMAC implementation, or freshness-
state owner: FRC has both FRC→Brake and direct FRC→EPS dependencies, ABS has
Brake→EPS and ADS-interface dependencies, all six local `0792` FRC packages are
ReproMethod07 high-entropy stored images whose runtime representation is still
opaque, and the current corpus contains zero `07B0` Brake packages. A literal
Tx-descriptor/SecOC-call scan over those six stored images would therefore treat
an unknown encoded representation as executable plaintext and is not admissible
evidence.

The same pass closes two numeric comparison surfaces without inventing a wire
transform. ADS DDR rows 406/407 (`Advanced Drive Control Target Steering Angle
Speed Order Value` / `…Target Steering Angle Order Value`) are signed 32-bit
snapshot values in **rad/s** and **rad**. Their raw PhyData records are identical
across NA/EU/JP and encode `mul=1000`, `div=1`, `offset=0`, signed=true, decimal-
point count 3, giving unity displayed-unit conversion. Brake-family DID `0x107E
ADS Control EPS Pinion Angle2` remains a separate signed-24 observer at
`0.00025 rad/count`; H's B6 controller-equivalent target scale is
`~0.001000121519 rad/count` (ratio `~4.000486075`). No producer dataflow joins
those domains, so the near-four ratio is a correlation lead, **not** evidence of
B6 packing. Likewise the seven-foreground-tick B6 loss cutoff is receiver policy;
TAUJ0-CH3's wall-clock period remains unresolved, so no sender cadence is inferred
from it or from unrelated CUW flashing timers.

Machine-readable sender-attribution evidence is
`data/generated/techstream_v18/tss3_b6_sender_attribution.json`, generated by
`tools/techstream/build_tss3_b6_sender_attribution.py` and checked by
`tests/verify_tss3_b6_sender_attribution.py`. TMS-052 refines the acquisition
boundary: the 23TC01 `8646F1204500` 2023-Corolla `0792` family is already local,
but encoded and not exact-specimen-joined. The next code-level target is therefore
the decoded category-435 `07B0` Brake application plus either a decoder/exact
identity join for the already-owned FRC family or synchronized stock-LTA traffic,
not another scan for an unspecified 2023 Corolla FRC CUW.

The same P5 signal-info path also closes the **Target Lateral ID** value
dictionary. `GetDatMonSignalInfoP5_DT.dll` consumes the type-62 monitor record's
`+0x32` pattern-display key, and byte-anchored `KgpDataCtrl.dll` accessors resolve
type-14 `CDbPatDispTable` records by key `+0x0C`, raw value `+0x04`, and display
string `+0x00`. `EMPS_P5` uses pattern key 39 and `EMPS2_P5` uses key 29, but the
OEM value dictionary is identical across NA/EU/JP and both System-1/System-2
monitors: `0=No Request (Manual Operation)`, `1=PCS`, `4=LDA`, `10=Hands Off LTA`,
`11=LTA/LCA`, `13=DESA (Slow Deceleration Control)`, `15=DESA (Deceleration Stop
Control)`, `18=SDG`, `19=PDA`, `25=AP`, `27=Remote Parking`, `35/37/39=AD/EM/DES
(Lv.3)`, `41/43/45=AD/EM/DES (Lv.4)`, `49=Self-Propelled Transport`, and
`63=Driver Operation`. This is the exact diagnostic value dictionary; a wire-field
join still requires target-firmware evidence, which the Corolla H B6 signal254
analysis supplies for values `1/4/10/11/19` and `25/27`.

Machine-readable evidence is
`data/generated/techstream_v18/p5_lateral_control_semantics.json` (schema v5),
generated by `tools/techstream/extract_p5_lateral_control_semantics.py` and
independently checked by `tests/verify_techstream_p5_lateral_control.py`.


#### 6.2.3 Current GTS+ CAN Bus Check topology tables

Current GTS+ carries Toyota's CAN Bus Check network model in the master `Toyota.ddb`,
not in the per-ECU Data List tables. The current class-backed surface used by the Camry
analysis is:

- type 55 `CDbCanBusListTable` — gateway/bus ownership metadata;
- type 75 `CDbCanBusCarIdTable` — vehicle type -> CAN-topology key;
- type 76 `CDbSubBusConfirmationCGWTable` — one-based ECU/sub-bus domain names;
- type 77 `CDbCanBusOptionTable` — topology-key option variants and component-set key;
- type 78 `CDbCanBusComponentTable` — component-set / bus-index / component membership;
- type 79 `CDbCanBusNameTable` — bus-index display names.

The table identities are consumer/factory-backed (`KgpDataCtrl.dll` exposes the matching
`CDbCanBus*`/`CDbSubBusConfirmation*` classes), and the shared parser now names these
master IDs directly. On the exact current Camry family, vehicle types
12704/12862/12984 all select topology key `0x00A7D910`; all 18 option variants have the
same 31 component placements. The high-value result is Front Camera Module -> Central
Gateway **Bus 1**, while Skid Control (ABS/VSC/TRAC) and Power Steering (EPS) are both
on **Bus 4**. This is Toyota network-topology evidence rather than inference from CAN
arbitration IDs. Vehicle-specific physical interpretation, including the Toyota-B repin
join and B6 consequence, is owned by
[the Camry baseline §19](../variants/camry-2026-live-baseline.md#19-current-gts-can-topology-closes-the-b6-bus-question).

`Bus 1`/`Bus 4` are Central-Gateway logical network identities. They must not be equated
numerically with Panda bus 1/4 or connector cavity numbers without a separate physical
join.

#### 6.2.4 Fleet-wide TSS3 architecture breadth and the offline recorder toolchain

The earlier `FRC_P5` work proved individual category/install-set joins, but it did not
persist the obvious fleet-level question: **does current GTS+ describe one TSS3 steering
architecture, or a family of architectures?** The current 2026.03.002.02 GTS+ master now
has a deterministic census in
`data/generated/gtsplus_2026/tss3_crossvehicle_surface.json`, generated by
`tools/techstream/extract_gtsplus_tss3_crossvehicle_surface.py` and checked against the
pinned local distribution by `tests/verify_gtsplus_tss3_crossvehicle_surface.py`.

The answer is unambiguously a **family**. Considering current install rows that contain
category 498 `FRC_P5 = Front Recognition Camera 2`, and clustering only the selected
steering/brake/ADAS categories needed to distinguish the architectures:

| Region | category-498 install rows | distinct model names | selected architecture patterns |
|---|---:|---:|---:|
| NA | 256 | 51 | 5 |
| EU | 460 | 93 | 9 |
| JP | 213 | 70 | 9 |

The NA distribution is especially clean: 117 rows are `405+435+466+498`
(`EMPS_P5 + Brake/EPB + Brake Booster + FRC_P5`), 98 are `405+435+498`, 36 are
`405+498`, four MAC rows carry the much larger
`405+418+430+435+466+476+477+498+499` set, and one synthetic/test row is 498-only.
Current category 499 `EMPS2_P5 = Steering Actuator` appears in only **4/256 NA**,
**9/460 EU**, and **12/213 JP** category-498 install rows. Therefore a separate
Steering Actuator is **not intrinsic to the TSS3/FRC_P5 diagnostic generation**. This
is a fleet-database statement; the command wire contract, signer, feedback path, and
suppression point still require target-native proof for each architecture.

The expanded fleet artifact now also joins Toyota CAN Bus Check topology. Across every
resolved category-498 placement shape that contains both **Power Steering (EPS)** and
**Skid Control**, those two chassis controllers are colocated on the same Toyota logical
network while **Front Camera Module is on a different logical network**: **114/114 NA**,
**328/328 EU**, and **99/99 JP** qualifying shapes. No qualifying shape splits EPS from
Skid. This generalizes the Camry's Toyota `Bus 4` EPS/Skid + `Bus 1` camera structure as a
fleet-level TSS3 topology pattern; it still does not equate Toyota bus names with Panda
bus indexes. The dedicated census and flat placement data live in
[gtsplus-tss3-fleet-map.md](gtsplus-tss3-fleet-map.md).

The same census records a useful negative that corrects a tempting broad-P5 inference.
Among current category-498 install rows, selected categories `PCS1_P5` 427,
`DSSystem_P5` 428, `Fr_RadSen_P5` 429, `RoadSign_P5` 431, and `PCS2_P5` 432 have
**zero co-occurrence in NA, EU, and JP**. Those databases remain legitimate Toyota P5
vocabulary, but generation-20 naming alone is not evidence that they belong to the
category-498 TSS3 architecture. Do not call them TSS3 longitudinal components without
another vehicle/install-set or firmware/dynamic join. Numeric install-set IDs remain
region-local, as documented above.

**PCS Data Viewer is a separate high-value TSS3 dictionary.** Current GTS+ ships
`PCS Data Viewer` **12.00.005**. Its managed resources have now been decoded as a
regenerable artifact rather than a string census: **1,131** `FFD_TSS3_ID_*` signal keys,
**49** `FFD_TSS3_TRIGGER_ID_*` event keys, 13 `IMGFFD_TSS3_ID_*` keys, 18 image-trigger
keys, 19 `INFO_TSS3FFD_*` and 14 `INFO_FCMIMGFFD_TSS3_*` messages, with English/Japanese
values and a metadata join back to the viewer's TSS3 extractor/model classes. Exact
control/arbitration witnesses are substantially stronger than the earlier report-heading
surface:

- `0x5280`: lower-limit longitudinal request ID / acceleration / brake-drive distribution,
  plus shift-range and EPB request;
- `0x5281`: upper-limit longitudinal request ID / acceleration / distribution;
- `0x5282`: **TSS request - lateral ID**, **TSS request - pinion angle**, steering-assist
  gain and damping-control gain;
- `0x5284/0x5285`: **Arbitration result_longitudinal ID** / **Arbitration result_lateral ID**;
- `0x5531`: LDA Lateral ID + LDA Control Request Pinion Angle;
- `0x5631`: LTA Lateral ID + LTA Control Request Pinion Angle;
- `0x57DB/0x57DE`: arbitration-result acceleration / pinion angle.

The shipped PCS executable still has protector-zeroed managed bodies, but the generic
CP decoder now recovers a clean analysis PE with **22,447/22,447 executable `MethodDef`
bodies materialized**. That closes the previously missing `DetailBitAssignInfo` and
`RoBCodeDetailInfo` initializers. The generated managed-semantics artifact contains
**1,130 exact Operation-FFD bit/scaling rows across 623 recorder DIDs** plus **47 exact
RoB/trigger definitions**, and the recovered `MeasuredValue` code proves
`physical = raw * Lsb + Offset` with `Point` decimal presentation.

The steering witnesses are now byte-level OEM contracts rather than name-only leads:
`5282` is byte1 lateral ID, bytes2-3 signed pinion-angle request at **0.001**, byte4
steering-assist gain at **0.01**, byte5 damping gain at **0.01**; `5531` LDA and `5631`
LTA use the same four-field layout/scales. `5285` is the byte1 arbitration-result lateral
ID, `560D` carries signed EPS pinion angle in bytes4-5 at **0.001**, and `57DE` is signed
arbitration-result pinion angle in bytes1-2 at **0.001**. RoB policy is concrete as well:
`209D` LCS Steer Override is 0.2 sampling with 36 pre/8 post records, `2818` Steering
Angle Speed Threshold Exceeded is 0.4 with 10/11, `2845` LTA Hands Free Cancel is 1.0
with 3/7, and `240F` LCA Cancel is 0.2 with 20/5.

The viewer also independently exposes `LogAnalyserEB12` (RoB code/trigger) and
`LogAnalyserEB13` (RoB code/frame/DID data), matching the already byte-anchored FRC
proprietary Operation-FFD `AB 12/13 -> EB 12/13` acquisition family. Image FFD is pinned
to front-camera recorder IDs `0501/0502/0507/0511/5101` plus variable raw-image DID
`6001`; its restored initializers now expose minimum lengths, 13 header-field bit layouts,
and image-RoB timing tables too. The same recovered FCM TSS3 bodies close the image
payload decoder: `622081` value `01` means unencrypted, otherwise each byte is decoded as
`reverse_bits8(cipher_byte) XOR 0xAA`; specs 5/7 share the 360×180 `{0:D3}.jpg` row. The
viewer also closes split reassembly: logged `EB33` blocks start at byte 9, `6xxx` DIDs use
BE32 lengths, split DIDs `6002..6017` are joined in order, and the result is exposed as raw
image DID `6001`. See
[pcs-data-viewer-tss3-dictionary.md](pcs-data-viewer-tss3-dictionary.md) and
`data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json`.

**The current native recorder acquisition stack is now release-local too.** The protected-body
recovery supplies the original current `CommandCommon.dll` and
`GetTSS3ImageFFDP5_DT.dll`; `GetTSS3OperationFFDP5_DT.dll` was already materialized.
`data/generated/gtsplus_2026/tss3_native_recorder_protocol.json` pins the exact current
PE identities, export-body hashes, direct-call edges and raw constants. Operation FFD is
now directly current-body proven as selector `0x66` plus `AB11/EB11`,
`AB12 + behavior_be16 / EB12`, and `AB13 + behavior_be16 + record_be16 / EB13`; EB13
parsing starts at offset 6 and consumes `data_id_be16 + length_u8 + data`. Image FFD now
has a current-body end-to-end setup chain: `22 11 03` spec -> `22 11 01` availability ->
**`27 03` six-byte seed / `27 04` six-byte level-49 key** -> `22 20 81` encryption method.
`GetTSS3ImageFFDInfo` directly calls the six-byte `SecurityUnlock` path, not the separate
16-byte/level-2 implementation. Accepted image specs are 5 and 7; availability value 2
marks slots 1..10 and 1..11 respectively. The same current Image plugin now closes the
record transport too: `AB31 -> EB31` enumerates BE16 RoB codes;
`AB33 || rob_code_be16 || frame_number_be32 -> EB33` fetches a record; EB33 is
`EB33 || RoB BE16 || frame BE32 || count u8 || blocks`, with blocks starting at byte 9 and
using BE32 lengths for `6xxx` DIDs versus u8 lengths otherwise. The current frame helpers
use `0x200` split groups and acquisition loops cover splits 1..22; `0000xxxx` frame numbers
are occurrence selectors, while nonzero high16 values encode the time-series split/set group
and the low16 value is trigger-minus-one. PCS Data Viewer independently implements the inverse
formulas. This removes the remaining V18 executable-body transfer from the native TSS3 recorder
acquisition path. The former managed PCS Data Viewer initializer boundary is now closed
independently by the CP-managed-EXE recovery above.

**The TSE/GTSE saved-session layer is now structurally recovered.** Current
`GTS+ TSEConverter` is **01.02.002** and selects `180_Template.csv`; the shipped 173 and
180 templates are byte-identical. Toyota's template is a 12,850-row binary-layout grammar
with an 8-byte file-extension/header region, **38** 12-byte FAT/search-key entries with
32-bit positions, nested list/size metadata, and first-class top-level sections for
RecordOnBehavior, CAN Bus, VehicleControlHistory, **PCS time-series Operation FFD**, and
**PCS Image FFD**. Native `GTSFileController.dll` independently exports add/get/count APIs
for both PCS FFD section families, closing the persistence side of the host pipeline.

The same template fully declares stored ring-buffer signal metadata: frame indexes/lengths,
signal/frame IDs, start/end bits, names/units, signedness, **MUL/DIV/OFFSET**, decimal
precision, display patterns, raw min/max, plus ring read/write positions and raw bytes.
The managed bodies are now executable after CP recovery rather than an analysis boundary.
`RingBufferParser::ParseRingBuffer` uses an 8-byte timestamp and record stride
**`8 + 2 * sum(frame lengths)`**. `ConvertNumericValue` handles signed 1/2/4/8-byte values
and unsigned bitmask/shift extraction, then computes
**`(raw * MUL / DIV + OFFSET) / 10^decimal_places`**. `Converter.BinaryRead` exposes the
actual saved-file typed-reader branches and signature resynchronization logic.

`TseCompression` closes the outer GTSE container too: it recursively inventories the
source tree, appends Toyota's static salt before SHA-256 hashing each file, writes a
Shift-JIS `list.txt` manifest headed `Target Folder`, creates a Shift-JIS-named ZIP with
`ZipFile.CreateFromDirectory`, and moves that ZIP to the requested `.GTSE` path. The
current protected `TSEConverter.exe` itself now recovers with **27/27** executable method
bodies and entry `0x6BAE`.

A critical preservation boundary remains explicit in the current config:
`BinarySkipDataNames` includes `RecordOnBehavior共通`, **`PCS時系列作動時FFD`** and
**`PCS画像FFD`**. Therefore original TSE files must be preserved for TSS3 recorder RE;
the current TSE->GTSE conversion is configured to skip exactly those PCS sections.
Canonical detail and the generated artifact are in
[gtsplus-tse-gtse-saved-session.md](gtsplus-tse-gtse-saved-session.md).

The host chain is therefore no longer merely a lead:

`FRC_P5 AB/EB recorder acquisition -> first-class TSE PCS FFD section -> PCS Data Viewer TSS3 dictionary`.

The concrete PCS Operation-FFD byte/bit/scaling table is now closed. What remains open at
this host layer is primarily recorder-ID -> vehicle-network producer/frame correlation and
validation of the saved-session traversal against a representative Toyota-generated TSE
sample, not the existence, purpose, or executable decoder semantics of the three host
layers.

**P6 is a successor oracle, not TSS3 evidence, and its migration boundary is now
explicit.** A dedicated cross-generation artifact joins `DSSystem_P5`, `Fr_RadSen_P5`,
`LDA_P5`, `PCS1_P5`, `PCS2_P5`, and `RoadSign_P5` into generation-22
`ADCU_P6 = ADAS Domain Controller`. The older P5 compute family is genuinely distributed:
for example, the LS500/LS500h/MIRAI install architecture is exactly
`PCS1 + DSSystem + Fr_RadSen + RoadSign + PCS2`; `PCS2_P5` owns named request outputs such
as LPB/PB/PBA/PBH/PBR, Warning Brake Request and **PCS Steering Request**, while radar/lane
peers retain their own perception and hands-off vocabularies.

`ADCU_P6` then consolidates a much larger diagnostic/recorder surface: **1,645 deduplicated
monitor signals** (1,647 raw primary monitor rows in the underlying table census),
183 DTCs, 22 routine Active Tests, **2,045 RoB Data IDs**, 501 RoB diagnostic codes,
717 RoB freeze-frame rows, and a separate DDR family with 445 Data IDs, 69 diagnostic
codes, **1,797** freeze-frame rows and 1,165 invalid-condition rows. Importantly, the
master preserves many P5 diagnostic **role IDs** while swapping in P6 implementations
(e.g. monitor list `0x05`, signal info `0x41`, RoB get/delete `0xA0/0xA1`, clear `0x19`,
CID `0x52`) and adds P6-only routine/image-FFD roles. That makes P6 a strong semantic
migration oracle without making it evidence about category-498 TSS3 ownership. See
[gtsplus-p5-adas-p6-migration.md](gtsplus-p5-adas-p6-migration.md).

### 6.3 Current GTS+ live transport for the selected FRC cruise Data IDs

The DDB-only uncertainty around the five highest-value FRC cruise oracles is now
closed at the current-GTS+ host layer. Exact `DataListIF.dll` (507,920 bytes,
SHA-256 `cce3ecd1...b54d651d`) implements `CCommEventPhase5DM::DataidSetup` at
`0x100393D0`: for every selected Data ID it allocates a three-byte request, writes
service byte `0x22`, then writes the Data ID high byte followed by the low byte.
`CCommEventPhase5DM::CheckRcvFrame` at `0x10038FD0` requires positive service
`0x62` for the queued `0x22` item, advances the response pointer by three bytes,
and copies `min(received_length-3, runtime_expected_data_id_length)` into the
monitor buffer. Both function bodies and the relevant x86 instruction anchors are
raw-byte pinned by the generated artifact.

For the exact cruise oracle set already recovered from `FRC_P5.ddb`, this yields
ordinary UDS ReadDataByIdentifier requests:

| Data ID | Direct request | Strict capture prefix | Diagnostic oracle |
|---:|---|---|---|
| `0x1901` | `22 19 01` | `62 19 01` | Current / Memory Vehicle Speed |
| `0x1905` | `22 19 05` | `62 19 05` | Cruise Control Permission Flag |
| `0x1906` | `22 19 06` | `62 19 06` | Main Switch / Set-Cancel / ACC Not Available |
| `0x1912` | `22 19 12` | `62 19 12` | Set Vehicle Interval Time |
| `0x1914` | `22 19 14` | `62 19 14` | ACC Control in Operation Flag |

Current GTS+ PatternDisplay resolves the `0x1914` bit-8 flag exactly as
**0=`Cruise Control Not in Operation`, 1=`Cruise Control in Operation`**.
Combined with the current `0x1601` dictionary above, the strongest read-only
Camry operating-context oracle is therefore stable `0x1601` **LTA Switch=1 / LTA
Control=0 (Enabled)** overlapping stable `0x1914` **ACC-in-operation=1**. This
proves Toyota's diagnostic operating context; it still does not directly measure
continuous EPS steering torque.

One host quirk is important for independent tooling: this receive worker checks the
`0x62` service byte but does not itself compare response bytes 1/2 against the queued
Data ID before stripping the first three bytes. A capture script should therefore be
**stricter than GTS+** and require `62 || requested_DID_hi || requested_DID_lo`
before decoding the payload with the DDB bit ranges.

This closes the live service mapping, not the CAN-field mapping. It also does not
prove a named outer UDS DiagnosticSessionControl or SecurityAccess prerequisite;
the Phase-5 monitor-internal state machine is insufficient evidence to infer
`10 01`, `10 03`, or a security level. The next vehicle capture can nevertheless
poll these five RDBIs directly and synchronize their exact Toyota semantics with
all-bus CAN without depending on the GTS+ GUI.

Machine-readable evidence is
`data/generated/techstream_v18/tss3_cruise_live_transport.json`, generated by
`tools/techstream/extract_tss3_cruise_live_transport.py` and independently checked
against the pinned local GTS+ archive by
`tests/verify_tss3_cruise_live_transport_external.py`.

### 6.4 P5 DTC clear routing: `DelDiagCodeP4`, Mode 04, and SID 14 fallback

The P4/P5 diagnostic clear path is explicitly represented in the Toyota host,
and it is not equivalent to blindly issuing UDS SID `0x14` to every physical
ECU address. Current GTS+ binds role `0x19` (25) `DelDiagCodeP4.dll` to at least the
legislated P5 categories exercised on the 2026 Camry: 372 Engine, 395 Motor
Generator, 397 Hybrid Control, 398 HV Battery, and 435 Brake/EPB. The plugin's
primary transaction asks the master for clear selector `0x01`; current master
`CDbFuncCommFrameTable` rows expose that selector for all five categories.
Hybrid and Brake additionally expose selector `0x102`, which the plugin uses as
a fallback on selected first-transaction communication errors.

V18 independently closes the wire payload behind those selector numbers because
its master variable table is directly decoded: selector `0x01` resolves to
request **`04`** with positive check **`44`**, while the Hybrid/Brake `0x102`
route resolves to **`14 FF FF FF`** with positive check **`54`**. This is a
Toyota-host fact; the CAN addressing mode still comes from the active diagnostic
transport rather than from the one-byte service template itself.

The exact maintainer 2026 Camry supplies the missing dynamic transport join.
Physical SID `14 FF FF FF` is accepted by several non-legislated controllers but
rejected by Engine/MG/Hybrid/HV-Battery/Brake. Physical raw `04` is rejected too.
The legislated OBD functional domain is, however, directly visible from the
Comma: `0x7DF` Mode 01 PID 00 elicits `0x7E8/7EA/7EB/7ED/7EE`, and a functional
`0x7DF` Mode 04 clear elicits positive `0x44` from all five. This exact-vehicle
probe therefore identifies Toyota's P4 clear transport for those controllers as
the standard functional OBD Mode-04 path. See the Camry report §17 and
`data/generated/camry_2026_dtc_clear.json` for the bounded live evidence and the
post-clear DTC-status acceptance check.

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

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-001](../reference/index.md#finding-tms-001), [TMS-002](../reference/index.md#finding-tms-002), [TMS-003](../reference/index.md#finding-tms-003), [TMS-004](../reference/index.md#finding-tms-004), [TMS-005](../reference/index.md#finding-tms-005), [TMS-006](../reference/index.md#finding-tms-006), [TMS-007](../reference/index.md#finding-tms-007), [TMS-008](../reference/index.md#finding-tms-008), [TMS-009](../reference/index.md#finding-tms-009), [TMS-010](../reference/index.md#finding-tms-010), [TMS-012](../reference/index.md#finding-tms-012), [TMS-013](../reference/index.md#finding-tms-013), [TMS-017](../reference/index.md#finding-tms-017), [TMS-019](../reference/index.md#finding-tms-019), [TMS-020](../reference/index.md#finding-tms-020), [TMS-021](../reference/index.md#finding-tms-021), [TMS-022](../reference/index.md#finding-tms-022), [TMS-023](../reference/index.md#finding-tms-023), [TMS-024](../reference/index.md#finding-tms-024), [TMS-025](../reference/index.md#finding-tms-025), [TMS-026](../reference/index.md#finding-tms-026), [TMS-027](../reference/index.md#finding-tms-027), [TMS-028](../reference/index.md#finding-tms-028), [TMS-029](../reference/index.md#finding-tms-029), [TMS-030](../reference/index.md#finding-tms-030), [TMS-031](../reference/index.md#finding-tms-031), [TMS-032](../reference/index.md#finding-tms-032), [TMS-033](../reference/index.md#finding-tms-033), [TMS-034](../reference/index.md#finding-tms-034), [TMS-035](../reference/index.md#finding-tms-035), [TMS-036](../reference/index.md#finding-tms-036), [TMS-037](../reference/index.md#finding-tms-037), [TMS-038](../reference/index.md#finding-tms-038), [TMS-039](../reference/index.md#finding-tms-039), [TMS-040](../reference/index.md#finding-tms-040), [TMS-041](../reference/index.md#finding-tms-041), [TMS-042](../reference/index.md#finding-tms-042), [TMS-043](../reference/index.md#finding-tms-043), [TMS-044](../reference/index.md#finding-tms-044), [TMS-045](../reference/index.md#finding-tms-045), [TMS-046](../reference/index.md#finding-tms-046), [TMS-047](../reference/index.md#finding-tms-047), [TMS-048](../reference/index.md#finding-tms-048), [TMS-049](../reference/index.md#finding-tms-049), [TMS-050](../reference/index.md#finding-tms-050), [TMS-051](../reference/index.md#finding-tms-051), [TMS-052](../reference/index.md#finding-tms-052), [TMS-057](../reference/index.md#finding-tms-057), [TMS-061](../reference/index.md#finding-tms-061), [TMS-062](../reference/index.md#finding-tms-062), [TMS-063](../reference/index.md#finding-tms-063), [TMS-065](../reference/index.md#finding-tms-065), [TMS-066](../reference/index.md#finding-tms-066), [TMS-067](../reference/index.md#finding-tms-067), [TMS-068](../reference/index.md#finding-tms-068), [TMS-069](../reference/index.md#finding-tms-069), [TMS-070](../reference/index.md#finding-tms-070), [TMS-071](../reference/index.md#finding-tms-071), [TMS-072](../reference/index.md#finding-tms-072), [TMS-073](../reference/index.md#finding-tms-073), [TMS-077](../reference/index.md#finding-tms-077), [TMS-079](../reference/index.md#finding-tms-079), [TMS-080](../reference/index.md#finding-tms-080), [TMS-082](../reference/index.md#finding-tms-082), [VAR-064](../reference/index.md#finding-var-064)
- Corrections with this document as canonical home: [CORR-018](../reference/index.md#correction-corr-018), [CORR-019](../reference/index.md#correction-corr-019), [CORR-020](../reference/index.md#correction-corr-020), [CORR-021](../reference/index.md#correction-corr-021), [CORR-022](../reference/index.md#correction-corr-022), [CORR-023](../reference/index.md#correction-corr-023), [CORR-027](../reference/index.md#correction-corr-027), [CORR-034](../reference/index.md#correction-corr-034), [CORR-035](../reference/index.md#correction-corr-035), [CORR-039](../reference/index.md#correction-corr-039), [CORR-079](../reference/index.md#correction-corr-079), [CORR-080](../reference/index.md#correction-corr-080), [CORR-081](../reference/index.md#correction-corr-081), [CORR-082](../reference/index.md#correction-corr-082), [CORR-083](../reference/index.md#correction-corr-083), [CORR-084](../reference/index.md#correction-corr-084), [CORR-085](../reference/index.md#correction-corr-085), [CORR-091](../reference/index.md#correction-corr-091), [CORR-102](../reference/index.md#correction-corr-102), [CORR-103](../reference/index.md#correction-corr-103), [CORR-104](../reference/index.md#correction-corr-104), [CORR-117](../reference/index.md#correction-corr-117), [CORR-125](../reference/index.md#correction-corr-125)
<!-- knowledge-cross-references:end -->
