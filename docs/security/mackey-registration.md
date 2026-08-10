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
server-side `MACK4` field is retained in the native exchange record, while the
wire start operation itself contains only M1/M2/M3. No raw AES key crosses this
interface.

## `SafekeyNumber` versus MCU identity

Exact recovered equivalence is:

```text
SafekeyNumber = the unmodified 16-byte positive-response payload of DID 0x1010
```

The pinned Techstream tree contains no `MCUID`, `MCU ID`, or transformation
edge that names those bytes as a silicon identifier. Techstream validates only
service/DID/length before forwarding and later uses the value as the response
association key. Therefore equivalence to a physical MCU ID is **bounded**, not
established. The precise missing edge is a target-ECU implementation or a
captured response that assigns semantics to DID `0x1010`; no unpinned community
claim is used as proof here.

## `CMAC_01_*` classes and S324 procedure codes

The native DLL contains exactly 24 RTTI classes: base `CMAC_01` plus 23 product
variants. Their complete-object locators, vtable addresses, entry counts,
vtable hashes, displayed S324 codes, and recovered operation selectors are
generated from PE bytes in `mackey_vehicle_protocol.json`. The CSV records all
51 distinct embedded `S324-*` procedure/UI codes and every class/state
association.

These strings are procedure/display codes distributed across variant virtual
methods, not one serialized state-variable table. Class-local operation calls
and success/error branches are recovered, but the final cross-class successor
is selected by the outer Techstream UI/controller callback. Consequently the
CSV marks predecessor/successor edges **bounded** at that caller-selected
boundary instead of inventing a linear `00 -> 01 -> ...` graph. This remaining
UI transition boundary does not obscure any vehicle request or response edge.

## Comparison with Sienna firmware DID `0x1010`

The firmware was independently reopened through `tools/g`. Its application
WDBI callback routes a 64-byte request into ICU-S command 8 and returns a
48-byte M4/M5 result. The exact comparison is:

| Property | Techstream MACKey | Sienna `8965B4512000` |
|---|---|---|
| Start | `31 01 30 02 || M1[16] || M2[32] || M3[16]` | `2E 01 10 10 || M1[16] || M2[32] || M3[16]` |
| Poll | `31 03 30 02` | `2E 03 10 10` |
| Result | state plus `M4[32] || M5[16]` | status plus `M4[32] || M5[16]` |
| Engine evidence | ECU-side routine, implementation absent | literal ICU-S command 8 at `0x8997A` |

Conclusion: **same SHE-compatible cryptographic architecture, different
diagnostic service/procedure; no exact join**. The Techstream read of DID
`0x1010` is a separate 16-byte safe-key identity read, not the Sienna's
selector-1 64-byte WDBI package. Static evidence does not prove that this
Techstream utility targets the analyzed EPS or provisions its slot 4.

## Remaining dynamic questions

- Which ECU families assign MCU-ID semantics to read DID `0x1010`?
- Does a real Sienna provisioning session use application WDBI `0x1010`,
  Routine `0x3002`, or neither?
- What timing/retry behavior appears on a live master/slave network?

Those require target firmware or a capture. They no longer block the recovered
Techstream V18 vehicle protocol.
