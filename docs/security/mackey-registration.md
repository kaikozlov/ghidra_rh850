# Techstream MACKey Registration

## Scope and confidence

This report covers the MACKey Registration utility shipped in the pinned
Techstream V18.00.003 distribution. The primary artifacts are
`Techstream.exe`, native `IT3UtilityNK.dll`, managed `IT3UtilityRevNK.dll`, and
`eVbBroker.dll` under the gitignored unpacked Techstream tree. The deterministic
checks are in `tests/verify_techstream_mackey.py`.

The online request/response flow and request XML construction are **recovered**
from managed IL and native imports/exports. The final ECU write protocol remains
**bounded**: the native utility clearly parses returned exchange-key XML and has
24 `CMAC_01_*` procedure classes, but the exact CAN/UDS command transcript has
not yet been reconstructed or captured dynamically.

## What the subsystem is

`Techstream.exe` exposes a MACKey Registration utility and passes configuration
and session data through the EVB broker interface. The executable dynamically
loads `evbbroker.dll` and resolves the `EbStart`, `EbOpenPara`, `EbSetPara`,
`EbSetString`, `EbSetData`, `EbGetPara`, `EbReadPara`, `EbWritePara`,
`EbClosePara`, `EbEnd`, and `EbKill` exports. The concrete file in the pinned
installation is `eVbBroker.dll` (Windows filename matching is case-insensitive).

This is not the ordinary UDS `SecurityAccess` seed/key implementation. It is an
online ECU exchange-key provisioning workflow. It may provision material used
by another authentication domain, but the static artifacts do **not** prove
that its keys are the Sienna or Corolla SecOC slot keys. Keep that relationship
as a hypothesis until the native write procedure or a vehicle transcript joins
them.

## Request data recovered from shared memory

Managed `CS_MODULE.SharedMemory::read_xmldata_MAC01` reads this packed payload:

| Offset | Size | Meaning |
|---:|---:|---|
| `0x00` | 2 | process type (`uint16`) |
| `0x02` | 17 | VIN |
| `0x13` | 16 | master `SafekeyNumber` |
| `0x23` | 16 | `MACM1` |
| `0x33` | 32 | `MACM2` |
| `0x53` | 16 | `MACM3` |
| `0x63` | 2 | slave ECU count (`uint16`) |
| `0x65` | `16 × count` | slave `SafekeyNumber` values |

`MAC_01_CommonProcess::MAC_01_CreateXML` serializes those fields into an
`ECUExchangeKey` request:

- `X-Version = 1`
- `GTS/{SoftwareID, SoftwareVersion, LicenseKey}`
- optional `ServicePlantFlag` for user type 2
- `HashValue`
- `VehicleIdentificationNumber`
- `MasterECU SafekeyNumber=.../{MACM1, MACM2, MACM3}`
- `SlaveECUList/SlaveECU SafekeyNumber=...`

The request hash is SHA-256 over the concatenation of:

1. the raw 17 VIN bytes;
2. uppercase ASCII hex for the 16-byte master safe key;
3. uppercase ASCII hex for `MACM1` (16 bytes), `MACM2` (32 bytes), and
   `MACM3` (16 bytes);
4. uppercase ASCII hex for every 16-byte slave safe key.

The preimage is therefore `177 + 32 × slave_count` bytes. The resulting digest
is rendered as uppercase hex without separators. A timestamped copy of the
request is written beneath `Techstream/ECUSecurityKey/`.

`LicenseKey` is not a secret recovered from the ECU in this method. The request
writes one of two 46-character sentinel strings (`00…00` or `11…11`) according
to the process type.

## Online flow

`IT3UtilityRevNK.dll` contains two user-mode branches in
`MAC_01_020_Load`.

### User type 1

`MAC_01_020_bgDoWork_UserType1` opens the configured MACKey URL in Internet
Explorer. `MAC_01_IEThreadFuncLow` / `MAC_01_IEThreadFuncMed` locate an HTML
element named `ECUExchangeKey` and set its value to the formatted request XML.
The code then waits for a non-empty field value or a five-minute timeout.

### User types 2 and 3

`MAC_01_020_bgDoWork_UserType2_3` dynamically loads `IT3UtilityNK.dll` and
resolves these native exports:

- `CallTisSendMacKey_FromRev`
- `CallTisGetMacKeyInfo_FromRev`
- `GetMacKeyResId_FromRev`
- `GetMacKeyResFile_FromRev`
- `GetMacKeyResResult_FromRev`
- the corresponding length accessors and `GetSoapFault_FromRev`

The native bridge imports
`CWebService::TisServiceSendMacKey` and
`CWebService::TisServiceGetMacKeyInfo` from `td3webapi.dll`.

The recovered sequence is:

1. Call `TisSendMacKey` with the request XML file path, an explicit UTC
   timestamp (`yyyy/MM/dd HH:mm:ss:fffffff`), and the GTS software ID.
2. Require bridge result string `"0"` and read the returned request ID through
   `GetMacKeyResId_FromRev`.
3. Replace the literal `$36` token in the configured login URL with that
   returned request ID, then launch the URL.
4. Compute uppercase `SHA256(request_id)`.
5. Poll `TisGetMacKeyInfo(request_id, sha256_hex)`. Result values `2` and `3`
   continue polling; `0` is success; `1` and `4` terminate as errors. The loop
   has a five-minute timeout.
6. Read the response file through `GetMacKeyResFile_FromRev` and write it as
   `Memg/MAC_01_WriteData.xml`. The subsequent reader/call edge from that path
   into a particular native procedure has not yet been recovered.

### The `$36` correction

`$36` is **not DID `0x0036`**. Managed IL proves that it is replaced with the
server-returned request ID immediately after `GetMacKeyResId_FromRev`. Earlier
documentation inferred DID semantics from the digits and from an untracked URL
example; that inference was wrong. The exact query-parameter name is not
recoverable from the currently pinned artifacts, so this report does not repeat
the former `ecuMacId` claim as fact.

## Response and native procedure layer

`IT3UtilityNK.dll` contains 24 MSVC RTTI classes in the `CMAC_01_*` family and
response-parser vocabulary including:

- `ExchangeKeyList`, `ExchangeKey`, `ECUExchangeKey`
- `VehicleIdentificationNumber`, `HashValue`, `ResultCode`, `X-RequestID`,
  `X-Version`
- `MACK4`, `MACM1`, `MACM2`, `MACM3`, and `SafekeyNumber`

The managed layer obtains and stores the response XML. The native library also
contains `CMAC_01_*` state/procedure classes associated with the vehicle-facing
workflow. Their class census and vtables are reproducible from the MSVC RTTI,
but the direct response-file consumer and the diagnostic operations represented
by each state (`S324-00` through `S324-43`) still need method-by-method
decompilation.

## What this establishes—and what it does not

Established:

- Techstream collects VIN plus master/slave safe-key and MAC fields from a
  vehicle-facing shared-memory procedure.
- It hashes that request deterministically, submits it through Toyota's web API
  bridge, polls by a returned request ID, and receives exchange-key XML.
- The response is stored as `Memg/MAC_01_WriteData.xml`; native `CMAC_01_*`
  procedures coexist in the same subsystem, but the direct handoff is not yet
  proven.

Not yet established:

- the exact DID/routine/service IDs used to read `SafekeyNumber` and
  `MACM1/2/3`;
- the exact ECU write command and location for `MACK4`/exchange keys;
- whether this subsystem provisions SecOC, immobilizer, another MAC domain, or
  several product-specific domains;
- whether the Sienna `8965B4512000` or Corolla `8965F1208000` calibration uses
  this exact utility path.

The next useful static step is to label the `CMAC_01_*` RTTI vtables and
decompile the handful of overridden methods per state. The decisive dynamic
step is a `ptshim32.dll` capture of a real MACKey Registration session.
