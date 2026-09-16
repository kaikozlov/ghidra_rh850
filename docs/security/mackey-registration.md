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
**bounded** at the Toyota transport-selection layer: both sides carry the same
standard SHE M1--M5 memory-update object, but Techstream V18's recovered carrier
is RID `0x3002` while the Sienna application exposes RID `0x1010`.

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

## Protocol identity: AUTOSAR SHE Memory Update Protocol

The `M1..M5` update object delivered to an ECU in Toyota's ECU Security Key
workflow is **not a Toyota-defined cryptographic envelope**. It is the standard
Secure Hardware Extensions (SHE) memory-update protocol used by `CMD_LOAD_KEY`. AUTOSAR FO
R22-11, *Specification of Secure Hardware Extensions*, §4.7.7 and §4.9/§4.9.1
define the same parameter widths and roles recovered here:

| SHE field | Width | Direction | Standard role |
|---|---:|---|---|
| `M1` | 128 bits / 16 bytes | in | addressed SHE `UID' || ID || AuthID` |
| `M2` | 256 bits / 32 bytes | in | encrypted new counter, flags, and new key |
| `M3` | 128 bits / 16 bytes | in | `CMAC_K2(M1 || M2)` request authenticator |
| `M4` | 256 bits / 32 bytes | out | successful-update verification material |
| `M5` | 128 bits / 16 bytes | out | successful-update verification authenticator |

The standard authorization construction is also important for interpreting the
Toyota backend. The external issuer knows the existing authentication secret
`KEY_AuthID`, derives `K1 = KDF(KEY_AuthID, KEY_UPDATE_ENC_C)` and
`K2 = KDF(KEY_AuthID, KEY_UPDATE_MAC_C)`, encrypts the replacement key/counter/
flags into `M2`, and authenticates `M1 || M2` as `M3`. The secure module checks
write policy, `AuthID`, UID/wildcard policy, `M3`, and the monotonic update
counter before storing the new key and returning `M4/M5`. The vehicle
application CPU therefore need only relay the opaque package; neither the
replacement key nor `KEY_AuthID` needs to appear in plaintext in the ECU's UDS/
application path. The external provisioning backend necessarily knows the
material required to construct the package.

Toyota's proprietary layer is the **orchestration around that standard SHE
object**: vehicle/topology discovery, VIN and `SafekeyNumber` collection, the
online Toyota exchange-key service, mapping an ECU identity to the backend's
SHE UID/AuthID/counter/key state, and the UDS RoutineControl carrier
(`0x1010` or `0x3002`). In particular, the recovered 16-byte Toyota
`SafekeyNumber` is an association value supplied to the backend; no retained
artifact proves that it is byte-for-byte the SHE UID field used inside `M1`.
The independently reported Toyota “MCU ID” requirement is therefore highly
relevant to standard SHE package construction, but the exact
`MCU ID -> SHE UID -> SafekeyNumber` relation remains open.

External specification:
[AUTOSAR FO R22-11 — Specification of Secure Hardware Extensions](https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_TR_SecureHardwareExtensions.pdf),
§4.7.7 and §4.9/§4.9.1.

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

## Comparison with firmware RID `0x1010` and current GTS+

The original V18 recovery remains valid but is no longer the whole host picture.
Techstream V18's recovered online MACKey workflow writes selected ECUs through
Routine `0x3002`. Independently, current 2026 GTS+ `UtilityExNK2.dll` contains a
second first-class `MAC_01` transport that uses RoutineControl RID `0x1010`.

The current GTS+ binary is SHA-256
`d9868c8a9a69ffbab26ea7d4431e290372cd207e84e7b4aed27446aeb4c12ec1`.
Its `MAC_01` helpers are exact:

- VA `0x100F9FE0` builds `31 01 10 10 || M1[16] || M2[32] || M3[16]` and sends
  exactly `0x44` bytes;
- VA `0x100F9EF0` builds `31 03 10 10`, validates the positive response, and
  copies `M4[32] || M5[16]`;
- worker `0x100FA9C0` starts the update and polls the paired result helper;
- exported `Ex2MAC_01_ComProcess @ 0x10028590` selects the `0x100F9740` state
  machine containing that worker for one supported MACKey protocol family.

The same GTS+ DLL still carries the newer `0x3002` start/result helpers, so this
is deliberate multi-generation support rather than a replacement of one
protocol by the other.

The remaining live-family selector is hidden one layer higher. Current
`UtilityPlusFrontNK.dll` (SHA-256
`3472091a3c2f8df114fbab491dc442c3aee25a3485ce6390653413cb029d871a`)
imports and calls the generic `UtilityGene.dll` MACKey wrappers by ordinals
98/99/100: `Ex2MAC_01_S_KeyValidation`, `...KeyUpdate_before`, and
`...KeyUpdate_after`. The corresponding exports in `UtilityGene.dll` (SHA-256
`7412d320fcde90fff48c6511e638633e123e1068a4e54399a80c63d3c11c007e`)
are RVAs `0xE510`, `0xE2C0`, and `0xDF20`. All three lie inside virtual `.text`
but beyond that image's raw-backed `.text` prefix (`RVA 0x1000..0x1FFF`; virtual
extent through `0x32FFF`). The shipped file therefore does not contain the
wrapper bodies needed to statically join a specific selected ECU/family to the
RID-`0x1010` versus RID-`0x3002` backend. This is a packaging/static-evidence
boundary, not evidence that either route is unreachable.

The firmware comparison is now:

| Property | Techstream V18 recovered path | GTS+ 2026 `MAC_01` alternate path | Sienna `8965B4512000` | yc Venza SRS `89170-48E30` |
|---|---|---|---|---|
| Start | `31 01 30 02 || M1 || M2 || M3` | `31 01 10 10 || M1 || M2 || M3` | `31 01 10 10 || M1 || M2 || M3` | `31 01 10 10 || M1 || M2 || M3` |
| Poll | `31 03 30 02` | `31 03 10 10` | `31 03 10 10` | `31 03 10 10` |
| Result | state + `M4[32] || M5[16]` | `M4[32] || M5[16]` | status + `M4[32] || M5[16]` | status + `M4[32] || M5[16]` |
| Secure engine evidence | target implementation not joined | host transport only | literal ICU-S command 8 at `0x8997A` | secure-service opcode `0x31` via `0xBE0CC -> 0xBD69E` |

The yc airbag is especially useful because its 64-byte RID-`0x1010` start path
and 48-byte result path are independently visible in the ECU firmware, while
the application SecOC implementation reaches the same local secure subsystem by
key selector. This closes the architectural meaning of Toyota's “ECU Security
Key” write for that ECU family: it is an authenticated HSM-backed network-key
provisioning operation, distinct from ordinary UDS SecurityAccess and from
RPRG/reflash authorization.

The `22 10 10` `SafekeyNumber` read remains a separate 16-byte identity read. A
shared numeric `0x1010` does not make that DID the RoutineControl payload. What
has changed is that current Toyota tooling now proves a genuine RoutineControl
RID-`0x1010` MACKey transport exists.

## Front Recognition Camera applicability

The current Toyota/GTS+ camera evidence now closes a distinction that was left
too broad in earlier TSS3 architecture notes. Category 498 `FRC_P5` exposes DID
`0x10AF` (alternate `0x30AF`) as **ECU Security Key Registered Incomplete Flag**
with the OEM `OFF / ON / Not Fixed` state domain, and the same database exposes
`XF01B ECU Security Key Not Registered`. The older `Fr_Camera_P5` family exposes
DID `0x1119` (alternate `0x3119`) as **ECU Security Key Registered Status**.
Toyota service documentation independently requires **Update ECU Security Key**
after forward-recognition-camera replacement and describes the security key as
the credential required for a replacement ECU to communicate on the vehicle
network. The front-camera key state is therefore the camera ECU's own
provisioning state; it is not merely an observer of another ECU's registration.

The recovered `MAC_01` host model is deliberately multi-ECU: it discovers a
master plus slave endpoints, reads a 16-byte `SafekeyNumber` from each selected
endpoint, matches the Toyota-server `ExchangeKey` record by that identity, then
writes that ECU's `M1[16] || M2[32] || M3[16]` package and polls `M4[32] ||
M5[16]`. Current GTS+ contains both wire transports for that same logical
M1--M5 exchange-key family:

```text
31 01 30 02 || M1 || M2 || M3    / 31 03 30 02
31 01 10 10 || M1 || M2 || M3    / 31 03 10 10
```

Consequently the best current model is that a P5 FRC receives the **standard
AUTOSAR SHE `CMD_LOAD_KEY` memory-update package**, carried inside a
Toyota-selected RoutineControl transport and terminated by a target-local
secure-key backend. We do **not** yet have a retained `0x792` key-write trace or
decoded FRC application implementation, so the exact camera selector (`0x1010`
versus `0x3002`), its local SHE/HSM implementation, and the relation among
`SafekeyNumber`, Toyota's server-side MCU ID, and the SHE UID remain unproved.
The `UtilityPlusFrontNK -> UtilityGene` static pass above exhausts the obvious
current-GTS host join: the family-selector wrappers are imported and invoked,
but their shipped `UtilityGene` bodies are not raw-backed, so the FRC RID cannot
be recovered honestly from this package alone.

Nothing in that conclusion requires Renesas hardware. `M1..M5` are the
hardware-neutral **SHE protocol contract**; Renesas ICU-S is only one concrete
implementation of that contract. The yc Venza SRS specimen is the useful
control: it accepts the same standard RID-`0x1010` `M1/M2/M3 -> M4/M5` memory
update while reaching its secure subsystem through a different local
secure-service ABI than the tracked EPS. A non-Renesas FRC can therefore
implement the same SHE semantics in another HSM/security engine or equivalent
protected subsystem. The exact FRC SoC/HSM remains outside the decoded corpus.

This provisioning result must remain separate from **runtime protected-message
signing**. The captured native FRC-side Bus-1 periodic family is exact AUTOSAR
E2E Profile 5 and carries no Toyota `FV4 || MAC28` SecOC authenticator. That
proves only that the observed native Bus-1 PDUs are not the protected chassis
publication. Because the FRC is a real ECU-Security-Key participant, an unseen
private handoff carrying an FRC-generated authenticator, or some other use of
that provisioned key, can no longer be rejected merely from the camera's silicon
vendor or the plaintext/E2E shape of its public Bus-1 traffic. A downstream
Bus-4 participant is still required to proxy/physically publish `0x08A`, but the
location of CMAC generation/key selection is open until producer firmware or a
key-update/runtime trace joins it. Provisioning membership, physical
transmission, and cryptographic signing ownership are three different claims.

The FRC CUW/ReproStd SecurityAccess path is separate again. Its retained
`0x0792` packages use a stable family SecurityAccess working key and a bare
`27 01` seed request, which independently demonstrates ECU-local persistent
cryptographic state but does not identify the network-key M1--M5 backend or the
SecOC key slot.

## Remaining dynamic questions

- Is the raw DID `0x1010` `SafekeyNumber` the same MCU ID that the pinned
  external rekey report says Toyota requires alongside VIN? A labeled official
  transcript or target implementation is still required.
- Which current-GTS MACKey family selector is chosen by a live 2021 Venza SRS
  `89170-48E30`, and does the resulting trace use the statically matching
  RID-`0x1010` path?
- What exact server-produced `M1/M2/M3` package and counter/authorization state
  are used for that SRS key write?
- What timing/retry behavior appears on a live master/slave network?

Those require a live target capture. They no longer block the recovered
Toyota host-protocol model.
