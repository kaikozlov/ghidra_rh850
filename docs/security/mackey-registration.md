# Techstream MACKey Registration

## Scope and evidence

This report covers the MACKey Registration workflow in pinned Techstream
V18.00.003. The primary artifacts are `Techstream.exe`, `IT3UtilityNK.dll`,
`IT3UtilityRevNK.dll`, `eVbBroker.dll`, `td3webapi.dll`, and the newly joined
native companion `UtilityExNK2.dll`. The last file has SHA-256
`8d9623f028f23876f69cb02baa10e1881c01fa01a4f906013bd36266f7e0fb33`.

The end-to-end vehicle/server/vehicle data flow is **recovered** from managed
IL, native PE bytes, imports/exports, RTTI, parser bodies, and diagnostic helper
bodies. It is verified deterministically by
`tests/verify_techstream_mackey.py`; generated evidence lives in
`data/generated/techstream_v18/mackey_vehicle_protocol.json` and
`mackey_state_machine.csv`. Applicability to the Sienna `8965B4512000` EPS is
**bounded**: the cryptographic envelope matches, but the diagnostic service and
procedure do not.

## End-to-end flow

```text
master ECU 0x763
  22 F1 90 -> VIN[17]
  22 10 2E -> MACM1[16] || MACM2[32] || MACM3[16]
  22 10 10 -> master SafekeyNumber[16]
  topology discovery -> slave ECU addresses
each slave
  22 10 10 -> slave SafekeyNumber[16]
        |
        v
shared memory -> ECUExchangeKey XML -> Toyota MACKey service
        |
        v
ExchangeKeyList XML -> identity match by SafekeyNumber
        |
        v
each selected master/slave ECU
  31 01 30 02 || M1[16] || M2[32] || M3[16]
  31 03 30 02 -> state[2] and, when complete, M4[32] || M5[16]
```

The vehicle-facing layer is in `UtilityExNK2.dll`, reached through twelve named
`Ex2MAC_01_*` imports in `IT3UtilityNK.dll`. This closes the former unnamed
companion-DLL boundary.

## Vehicle request producers

The exact diagnostic operations are:

| Purpose | Request | Required response | Output |
|---|---|---:|---|
| VIN | `22 F1 90` | at least 20 bytes | bytes 3–19, 17-byte VIN |
| master MAC tuple | `22 10 2E` | at least 67 bytes | bytes 3–66 as 16+32+16 |
| safe-key identity | `22 10 10` | at least 19 bytes | bytes 3–18, 16 bytes |
| update SA seed | `27 41` | 18 bytes | 16-byte seed |
| update SA key | `27 42 || key[16]` | positive `67 42` | unlock result |
| read topology | `22 10 33` | at least 28 bytes | 25-byte topology |
| write topology | `2E 10 35 || topology[25]` | positive `6E 10 35` | acknowledgement |
| start update | `31 01 30 02 || M1 || M2 || M3` | positive prefix | accepted package |
| poll update | `31 03 30 02` | at least 6 bytes; 54 when complete | 16-bit state, M4/M5 |

Additional setup/status helpers issue `10 4F`, `22 10 3A`, and `22 10 3B`.
The master connection helper selects request ID `0x763`; a related gateway
check uses `0x7A2`. The connection wrapper accepts discovered slave addresses,
so slave operations are not hard-coded to one CAN identifier.

Techstream forwards the VIN, MAC tuple, and safe-key bytes without endian or
cryptographic transformation. It validates positive service/DID prefixes and
minimum lengths. The master MAC tuple comes only from DID `0x102E`; each
`SafekeyNumber` comes only from DID `0x1010`.

## Master/slave discovery and association

The native discovery routine starts at the master, reads topology DID `0x1033`
and DID groups `0x1100`–`0x1105`, `0x1107`, and `0x1108`, then resolves the
reported endpoints. It supports eight in-memory ECU records. Record order is
assigned from the recovered topology bitmap; record 0 is the master and later
records are slaves.

After the server response is parsed, `decode_exchange_records` matches each
returned record to an active vehicle record by the raw 16-byte
`SafekeyNumber`. The update loop reconnects to the corresponding endpoint and
performs routine `0x3002`; one Toyota transaction can therefore supply packages
for one master and several slaves. Static evidence does not identify those
ECUs as a Sienna SecOC domain.

## Shared memory and online request

Managed `SharedMemory::read_xmldata_MAC01` reads:

| Offset | Size | Meaning |
|---:|---:|---|
| `0x00` | 2 | process type |
| `0x02` | 17 | VIN |
| `0x13` | 16 | master `SafekeyNumber` |
| `0x23` | 16 | `MACM1` |
| `0x33` | 32 | `MACM2` |
| `0x53` | 16 | `MACM3` |
| `0x63` | 2 | slave count |
| `0x65` | `16 × count` | slave safe-key identities |

`MAC_01_CreateXML` serializes `ECUExchangeKey` with VIN, one master, and a
slave list. `HashValue` is SHA-256 over raw VIN followed by uppercase ASCII hex
for master safe key, M1, M2, M3, and every slave safe key. The preimage is
`177 + 32 × slave_count` bytes.

For online user types 2/3, Techstream sends this document through
`TisServiceSendMacKey`, receives a request ID, substitutes that ID for `$36` in
the login URL, and polls `TisServiceGetMacKeyInfo(request_id,
SHA256(request_id))`. `$36` is not a diagnostic identifier. Successful output
is saved to `Memg/MAC_01_WriteData.xml`.

## Response parser and vehicle write

Native parsers at `0x10238B60` and `0x1023B660` parse standard and shorter
product variants, bounded to 28 and 8 exchange records respectively. Each
`ExchangeKey` requires a 32-character safe-key identity and carries `MACM1`,
`MACM2`, `MACM3`, and `MACK4`. The parser removes spaces, hex-decodes the
fields, and associates them by `SafekeyNumber`; it does not associate records
by XML position alone.

The selected record's M1/M2/M3 values become the 64-byte payload of Routine
Control `31 01 30 02`. Techstream polls with `31 03 30 02`; completion state 2
requires a 54-byte response and copies a 32-byte M4 plus 16-byte M5 proof. The
server-side `MACK4` field is retained in the native exchange record at struct
offset `+0x18f0`, read by `decode_exchange_records` on `SafekeyNumber` match
(same path as M1/M2/M3), but **never reaches any diagnostic wire operation**.
The `start_key_update_3002` frame is exactly 68 bytes: the 4-byte `31 01 30 02`
header plus M1/M2/M3. The `MACK4` string is absent from `UtilityExNK2.dll` and
the managed layer entirely; all other `+0x18f0` code references in the native
DLL are `std::string` destructors. MACK4 is a dead-stored server field,
retained for potential host-side validation that this binary does not
implement (TMS-014).

## `SafekeyNumber` versus MCU identity

Exact recovered equivalence is:

```text
SafekeyNumber = the unmodified 16-byte positive-response payload of DID 0x1010
```

The pinned Techstream tree contains no `MCUID`, `MCU ID`, or transformation
edge that names those bytes as a silicon identifier. Techstream validates only
service/DID/length before forwarding and later uses the value as the response
association key. Therefore equivalence to a physical MCU ID is **bounded**, not
established.

Stage 8 adds one independently pinned external observation without collapsing
that boundary. `optskug/docs @ 2c7184122d3f1644dfc9f32e98daaa45df653098`
records a July 2026 official-key-configuration experiment in which Toyota's
server-side flow reportedly requires **both MCU ID and VIN** and rejects a
VIN-only key-update request. This establishes that an MCU identity is a distinct
required input in the observed official rekey workflow, but it does not identify
which vehicle diagnostic field supplies that value. No retained transcript
labels the response to `22 10 10` as `MCU ID`.

The precise missing edge is therefore narrower: join a labeled MCU-ID value from
an official rekey transcript or target-ECU implementation to the raw DID
`0x1010` response. Until that join exists, `SafekeyNumber == MCU ID` remains a
plausible hypothesis rather than a recovered equivalence (TMS-016).

## `CMAC_01_*` classes and S324 procedure codes

The native DLL contains exactly 24 RTTI classes: base `CMAC_01` plus 23 product
variants. Their complete-object locators, vtable addresses, entry counts, and
vtable hashes are generated directly from PE bytes in
`mackey_vehicle_protocol.json`. The same artifact records the 51 distinct
embedded `S324-*` procedure/UI codes and every class/state association.
Class-wide `Ex2MAC_01_ComProcess` selector sets are retained as separately
scoped recovered evidence; they are **not** assigned to individual S324 codes.

The S324 strings are procedure/display labels distributed across variant
methods, not one serialized state-variable table and not one-handler-per-state
identifiers. The reference census contains 61 state-code/function associations
across 60 unique native functions. One function, `0x10241650`, references both
`S324-08` and `S324-19` and selects which label to display on different
branches. Conversely, some S324 codes are referenced by multiple functions.
That structure makes per-state diagnostic-operation ownership unsound.

A review patch briefly tried to infer per-handler `ComProcess` counts/selectors
from wider code regions; that attribution was invalid. For example,
`S324-41`'s actual reference function at `0x1023F900` contains exactly **one**
direct call to `mackey_com_process`, not 19. The generated CSV therefore no
longer has `handler_comprocess_calls` or `handler_operations` columns. It
carries `state_code_reference_rvas` (all native functions that reference that
label) and a deliberately separate `class_operations` column. The latter is
class-wide only and must not be read as state ownership (TMS-014).

Class-local operation calls and success/error branches remain recovered, but
the final cross-class successor is selected by the outer Techstream
UI/controller callback. Consequently predecessor/successor edges stay
**bounded** at that caller-selected boundary instead of inventing a linear
`00 -> 01 -> ...` graph. This UI transition boundary does not obscure the
vehicle request/response protocol recovered above.

## Comparison with Sienna firmware DID `0x1010`

The firmware was independently reopened through `tools/g`. Its application
RoutineControl RID `0x1010` routes a 64-byte request into ICU-S command 8 and returns a
48-byte M4/M5 result. The exact comparison is:

| Property | Techstream MACKey | Sienna `8965B4512000` |
|---|---|---|
| Start | `31 01 30 02 || M1[16] || M2[32] || M3[16]` | `31 01 10 10 || M1[16] || M2[32] || M3[16]` |
| Poll | `31 03 30 02` | `31 03 10 10` |
| Result | state plus `M4[32] || M5[16]` | status plus `M4[32] || M5[16]` |
| Engine evidence | ECU-side routine, implementation absent | literal ICU-S command 8 at `0x8997A` |

Conclusion: **same SHE-compatible cryptographic architecture, different
diagnostic service/procedure; no exact join**. The Techstream read of DID
`0x1010` is a separate 16-byte safe-key identity read, not the Sienna's
startRoutine 64-byte RoutineControl package. Static evidence does not prove that this
Techstream utility targets the analyzed EPS or provisions its slot 4.

## Remaining dynamic questions

- Is the raw DID `0x1010` `SafekeyNumber` the same MCU ID that the pinned
  external rekey report says Toyota requires alongside VIN? A labeled official
  transcript or target implementation is still required.
- Does a real Sienna provisioning session use application RoutineControl RID `0x1010`,
  Routine `0x3002`, or neither?
- What timing/retry behavior appears on a live master/slave network?

Those require target firmware or a capture. They no longer block the recovered
Techstream V18 vehicle protocol.
