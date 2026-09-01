# PCS Data Viewer TSS3 recorder dictionary

> **Scope:** the current GTS+ `PCS Data Viewer` 12.00.005 executable,
> English/Japanese satellite resources, and the native `FRC_P5` TSS3
> Operation/Image FFD plugins.
>
> **Status:** recovered host-side dictionary/model surface with exact Operation-FFD
> bit/scaling/RoB tables and the current FCM TSS3 Image-FFD payload transform.
>
> **Artifact:**
> `data/generated/gtsplus_2026/pcs_data_viewer_tss3_dictionary.json`, generated
> by `tools/techstream/extract_pcs_data_viewer_tss3_dictionary.py` and verified
> by `tests/verify_gtsplus_pcs_data_viewer_tss3_dictionary.py`.

## 1. Executive result

PCS Data Viewer is not merely a report formatter. Toyota ships it with a large,
explicit **TSS3 recorder dictionary** and an object model for decoding TSS3
Operation FFD and Image FFD records.

The English satellite contains **15,640 .NET resource entries**. The TSS3
families include:

| Resource family | Entries |
|---|---:|
| `FFD_TSS3_ID_*` | **1,131** |
| `FFD_TSS3_TRIGGER_ID_*` | **49** |
| `IMGFFD_TSS3_ID_*` | **13** |
| `IMGFFD_TSS3_TRIGGER_ID_*` | **18** |
| `INFO_TSS3FFD_*` | **19** |
| `INFO_FCMIMGFFD_TSS3_*` | **14** |
| legacy `FFD_TRIGGER_ID_*` | 35 |
| `IMGFFD_TSS3_CSV_*` | 4 |

These are OEM names for recorder-internal signals and triggers. They are a
separate semantic surface from ordinary FRC_P5 Data Monitor / UDS SID-22 DIDs.

## 2. The TSS3 control/arbitration model is explicit

The most important contiguous dictionary block is `0x5280..0x5285`:

| Recorder ID | OEM meaning |
|---|---|
| `5280_1` | TSS required longitudinal ID (lower limit) |
| `5280_2` | TSS required acceleration (lower limit) |
| `5280_3` | TSS braking/driving force distribution method (lower limit) |
| `5280_4` | TSS shift range request |
| `5280_5` | TSS EPB request |
| `5280_6` | TSS accelerator override prohibition flag |
| `5280_7` | TSS acceleration request low priority flag |
| `5281_1` | TSS request longitudinal ID (upper limit) |
| `5281_2` | TSS request acceleration (upper limit) |
| `5281_3` | TSS braking/driving force distribution method instruction (upper limit) |
| `5282_1` | **TSS request - lateral ID** |
| `5282_2` | **TSS request - pinion angle** |
| `5282_3` | Steering assist gain |
| `5282_4` | Damping control gain |
| `5284` | **Arbitration result_longitudinal ID** |
| `5285` | **Arbitration result_lateral ID** |

This is direct Toyota terminology for a **multi-client control arbitration
layer**. Longitudinal requests have independent lower/upper-limit sources and
carry a requester/control ID plus acceleration and brake/drivetrain policy.
Lateral requests carry a lateral requester ID, requested pinion angle, steering
assist gain, and damping gain. Separate recorder fields hold the arbitration
winner/result for each axis.

The same recorder exposes the arbitration outputs themselves:

- `57DB` = `Arbitration result Acceleration`
- `57DE` = `Arbitration result Pinion angle`
- `57D3` = `Arbitration result_Acceleration valid flag`

This does **not** identify a CAN arbitration ID or prove which ECU performs the
arbitration. It identifies Toyota's software/control abstraction and the values
its diagnostic recorder preserves.

## 3. Feature clients use the same lateral contract

The recorder names feature-specific request fields with the same shape:

| Feature | ID | Request fields |
|---|---:|---|
| LDA | `5531` | Lateral ID, Control Request Pinion Angle, Steering Assist Gain, Damping Control Gain |
| LTA | `5631` | Lateral ID, Control Request Pinion Angle, Steering Assist Gain, Damping Control Gain |
| PDA (OAA) | `5A09/5A0A` | ID Request Lateral ID, request pinion angle |

This strongly explains why the EPS-side `Target Lateral ID` namespace is
portable across functions: Toyota's recorder models LDA/LTA/PDA and the generic
TSS request with the same `lateral ID + pinion-angle request` abstraction, then
records a final arbitration result.

Other lateral-control recorder fields include `PCS steering output phase`,
PCS measurement/feedback lateral position and velocity, steering-angle/rate
signals, steering overrides, and control-target geometry.

## 4. Longitudinal/ACC recorder vocabulary

The TSS3 dictionary contains substantially more longitudinal vocabulary than
the ordinary FRC Data List surface. Examples include:

- `590A` — `ACC target acceleration for DDR`
- `590C_2` — ACC control vehicle distance for DDR
- `590C_3` — lateral position of controlled object
- `590C_4` — **ACC control target lateral position for DDR**
- `590C_5` — target relative speed of controlled object
- `590C_6` — ACC controlled lateral relative velocity for DDR
- `590C_7/8` — target number / ACC control target number for DDR
- `590C_9/10` — camera/radar recognition for the ACC control target
- `5A14` — ACC control state

This is useful as an OEM vocabulary oracle for the still-open TSS3
longitudinal producer/ownership problem. It is recorder semantics, not yet a
wire-format join.

## 5. Trigger dictionary: the recorder is an ADAS incident flight recorder

All 49 `FFD_TSS3_TRIGGER_ID_*` entries are decoded. Representative triggers:

- `2090` — ALM Request Flag
- `2093` — Prefill Request Flag
- `2095/2096/2097/2098` — LPB/PB/PBH/PBA request flags
- `209A` — PCS STR Request Flag
- `209C/209D/209E` — LCS warning / steer override / brake override
- `20DA/20DB/20DC` — LDA switch-on / switch-off / lane-departure-warning
- `2276..227B` — PDA(OAA) driver steering/acceleration/braking and collision events
- `2290..2294` — PDA(DA) driver cancellation/brake/steering/acceleration events
- `229B..229F` — hands-off approach/hands-on/deceleration/end-of-control events
- `22B3` — cut-in during hands-off control
- `240E/240F` — LCA reject / cancel
- `2809` — PCS STR Control Request Flag
- `2818` — Steering Angle Speed Threshold Exceeded
- `2844` — Lane Departure Warning Operation under LTA
- `2845` — LTA Hands Free Cancel
- `2846` — CSF Hands Free Warning Operation
- `2862` — ABK Request Flag

This makes the TSS3 Operation FFD surface substantially more valuable than a
normal freeze frame: Toyota intentionally records feature transitions,
overrides, request boundaries, and hands-off state around events.

## 6. How PCS Data Viewer models Operation FFD

The shipped `PCS Data Viewer.exe` intentionally has protected/zero-filled managed
method bodies, but that is now only an **input representation**, not an analysis
boundary. The generic CP recovery materializes **22,447/22,447** nonzero-RVA
`MethodDef` bodies from the installed stub + sidecar and rebuilds a clean CLR PE
(entry `0x66FB8E`). The recovered type/model surface includes:

- `TSS3OperationFFDExtractor`
  - `Extract`, `Output`
  - first-trigger and non-first-trigger file splitting
  - multi-trigger/time-series trigger checks
  - `GetDetailDataByRoBCode`
  - `AnalyzeRoBParameter`
  - `CreateCsvDetailData`
- `LogAnalyserEB12`
  - RoB code extraction and trigger-type analysis
- `LogAnalyserEB13`
  - RoB code, frame number, DID-data extraction, DID-list construction
- `FirstTriggerInfo`
  - RoB code, frame number, trip counter, time counter, data set,
    absolute time, multi-trigger list
- `MeasuredValue`
  - support checking and physical-value conversion

Most importantly, `DetailBitAssignInfo` explicitly carries the fields needed
for a full physical decoder:

`DataName, DataID, DataSize, SupportDID, BytePosition, BitPosition,
BitLength, InvalidValueList, Type, Lsb, Offset, Point`.

`RoBCodeDetailInfo` similarly models:

`DataName, SystemType, Group, Sampling, PreTriggerNumber,
PostTriggerNumber, IsMultiTrigger, UniqueRoBCodeDID`.

The concrete initialized instances are now recovered as well.
`tools/techstream/extract_pcs_data_viewer_tss3_managed_semantics.py` interprets
the restored straight-line `DIDDataDefine::.cctor` and `RoBCodeDefine::.cctor`
and writes
`data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json`.
The current artifact contains **1,130 exact `DetailBitAssignInfo` rows across 623
recorder DIDs** and **47 exact RoB/trigger definitions**. The recovered
`MeasuredValue` methods prove the common engineering conversion
**`physical = raw * Lsb + Offset`**, followed by fixed-point presentation using
`Point` decimal places; `f`/`d` reinterpret IEEE-754 single/double payloads,
while `u`/`s` use the integer path.

High-value lateral rows are no longer inferred from names alone:

| Recorder DID | Toyota field | byte/bit contract | type / conversion |
|---|---|---|---|
| `5282` | TSS request - lateral ID | byte 1, bit pos 7, length 8 | unsigned, LSB 1 |
| `5282` | TSS request - pinion angle | byte 2, bit pos 7, length 16 | signed, **LSB 0.001**, offset 0, point 3 |
| `5282` | Steering assist gain | byte 4, bit pos 7, length 8 | unsigned, **LSB 0.01**, point 2 |
| `5282` | Damping control gain | byte 5, bit pos 7, length 8 | unsigned, **LSB 0.01**, point 2 |
| `5285` | Arbitration result_lateral ID | byte 1, bit pos 7, length 8 | unsigned, LSB 1 |
| `5531` | LDA Control Request Pinion Angle | byte 2, bit pos 7, length 16 | signed, **LSB 0.001**, point 3 |
| `560D` | EPS Pinion Angle | byte 4, bit pos 7, length 16 | signed, **LSB 0.001**, point 3 |
| `5631` | LTA Control Request Pinion Angle | byte 2, bit pos 7, length 16 | signed, **LSB 0.001**, point 3 |
| `57DE` | Arbitration result Pinion angle | byte 1, bit pos 7, length 16 | signed, **LSB 0.001**, point 3 |

`5531` and `5631` also have the same byte-1 lateral ID, byte-4 steering-assist
gain (`0.01`), and byte-5 damping gain (`0.01`) layout as `5282`. The recovered
managed enum `SYSTEM_TYPE` is exact Toyota terminology: **0=None, 1=AHBAHS,
2=LDA, 3=PCS, 4=IDA, 5=URSM, 6=SDG**. The 47 RoBs split as 1 AHBAHS, 20 LDA,
14 PCS, 6 IDA, 5 URSM, and 1 SDG. In particular, `209D` **LCS Steer Override**,
`2818` **Steering Angle Speed Threshold Exceeded**, `2845` **LTA Hands Free
Cancel**, and `240F` **LCA Cancel** are all explicitly `SystemType=2` = **LDA**.
Their sampling windows are respectively 0.2 s with 36/8 pre/post, 0.4 with
10/11, 1.0 with 3/7, and 0.2 with 20/5.

This is a useful **recorder-domain** attribution: Toyota groups the LTA/LCA/LCS
trigger family under its LDA system type. Recovered control flow makes the boundary
explicit: `CheckMultiTriggerInfo` compares `RoBCodeInfo.SystemType` and `Group`, while
`AnalyzeRoBParameter` iterates the **global** DID definition table (`GetDataCount` /
`GetDetailBitAssignInfo` / `GetValue`) and never reads `SystemType`. Therefore the enum
classifies RoB trigger families; it is not a per-DID ECU/producer label and does not by
itself prove which ECU constructs `5282` or the vehicle-network lateral command.

The request schema itself adds a second bounded result. Generic `5282`, LDA
`5531`, and LTA `5631` are not merely similar by name: the recovered table gives
all three the **same four-field byte/bit/scaling geometry** — byte1 lateral ID,
bytes2-3 signed pinion-angle request at `0.001`, byte4 steering-assist gain at
`0.01`, and byte5 damping gain at `0.01`. PDA(OAA) carries the same semantic
ingredients but splits them across `5A09` (6-bit lateral ID), `5A0A` (signed
pinion-angle request at `0.001`) and `5A0D` (assist/damping gains at `0.01`).
Generic arbitration outputs are separately recorded as `5285` lateral ID and
`57DE` signed pinion angle at `0.001`.

**LCA is the notable negative.** `5202` explicitly contains `LCA presence
information`, and the viewer has extensive LCA state/DDR/display fields, but
across all 1,130 current bit-assignment rows there is **no LCA-named lateral-ID,
pinion-angle, steering-assist-gain or damping-gain request tuple**. That schema
shape is consistent with the independently recovered `EMPS_P5` Target Lateral
ID dictionary using one shared profile value **11 = LTA/LCA**. It does **not**
prove that `5631` is the runtime LCA carrier, establish copy direction between
`5631` and `5282`, or identify the ECU/network producer. Those require dynamic
Operation-FFD data or producer firmware/dataflow.

## 7. Join to the current FRC_P5 proprietary protocol

Current GTS+ binds category 498 `FRC_P5` to native
`GetTSS3OperationFFDP5_DT.dll` and `GetTSS3ImageFFDP5_DT.dll`. The separately
byte-anchored P5 lateral artifact recovers the Operation FFD transport:

- `AB 11` -> `EB 11`: enumerate behavior/RoB codes
- `AB 12 <behavior_id BE16>` -> `EB 12`: enumerate subordinate frames/records
- `AB 13 <behavior_id BE16><record_id BE16>` -> `EB 13`: fetch data record
- EB13 payload decoder: `[recorder-DID BE16][length u8][data...]` blocks

PCS Data Viewer's metadata independently names `LogAnalyserEB12` and
`LogAnalyserEB13` with precisely the corresponding RoB/frame/DID concepts.
That is the host-side semantic consumer for the proprietary FRC Operation FFD
record stream.

**Important namespace boundary:** `FFD_TSS3_ID_5282`, `5285`, `5531`, `5631`,
`57DE`, `590A`, etc. are **recorder data IDs inside this AB/EB record system**.
They are not ordinary `FRC_P5` ReadDataByIdentifier IDs; direct `tools/gts did
FRC_P5 0x....` lookups for these IDs have no Data-Monitor match.

## 8. Image FFD

The exact nested FCM TSS3 image data-ID enum is:

`0501, 0502, 0507, 0511, 5101, 6001`.

The first five have `IMGFFD_TSS3_ID_*` display-name resources. `6001` is the
raw image payload DID and intentionally has no display-name resource. Viewer
metadata also exposes TSS3 FCM image analyzers for `EB33`, `621103`, and
`622081`, plus frame/set/trigger/split-number models, timestamps, encryption,
and image-table geometry.

The resource messages explicitly reference `SID$EB$23`, `SID$EB$33`, and
`DID$6001`.

The restored Image-FFD static constructors also close several formerly hidden
layout constants. `FCMDataTableDIDData` requires minimum lengths `5101:2`,
`0501:7`, `0502:4`, `0507:6`, `0511:4`, while `6001` is variable (`-1`).
`FCMDataTableHeaderData` contains 13 header fields, including trigger ID
(`5101`, byte1, 16 bits, invalid `FFFE`), trip (`0501`, byte1, 16 bits, invalid
`FFFF`), time counter (`0501`, byte3, 32 bits, invalid `FFFFFFFF`), odometer
units/info (`0502`, byte1/byte2, 8/24 bits), six date/time bytes under `0507`,
and `0511` unique-counter/add-time fields. The add-time counter starts at byte1
bit4, spans 29 bits, uses LSB 100, and marks `00FFFFFF` invalid.

`FCMDataTableRoBCode` likewise materializes the image event table. Its first
spec group contains `2822,2824,2821,2825,2820,2827,2826,2823,2828,2861`; the
second adds `282F`. The recovered constructor pins pre/post record times such as
`2826 = 3.6/0`, `2823 = 2.4/0`, `2828 = 3.6/3.6`, `2861 = 6.0/1.2`, and
`282F = 6.0/2.4` seconds/record-window units as represented by the viewer.

## 9. Current native acquisition stack is now release-local

The protected-body recovery closes the remaining cross-version weakness on the
**native acquisition side**. Current 2026.03.002.02 can now be analyzed as one
release using:

- recovered-original `CommandCommon.dll` (1,280,016 B, SHA-256
  `98e313d1…638d3`);
- recovered-original `GetTSS3ImageFFDP5_DT.dll` (117,776 B, SHA-256
  `07cfb84e…5ecd8`); and
- already-materialized current `GetTSS3OperationFFDP5_DT.dll` (38,928 B,
  SHA-256 `67257cf5…93414`).

`data/generated/gtsplus_2026/tss3_native_recorder_protocol.json` pins their
current code/constant identities and the following current-body semantics.

### Operation FFD

The proprietary acquisition chain is directly current-body proven:

- selector `0x66`;
- `AB 11 -> EB 11`: enumerate BE16 behavior/RoB codes;
- `AB 12 || behavior_be16 -> EB 12`: enumerate BE16 record/frame IDs, then
  sort/deduplicate them;
- `AB 13 || behavior_be16 || record_be16 -> EB 13`: fetch the record;
- EB13 parsing begins at response offset **6** and consumes
  `data_id_be16 || length_u8 || data[length]` blocks, deduplicating Data IDs;
- recorder Data ID `0x0501`, when at least two bytes long, is additionally
  surfaced as BE16 metadata.

The current 15-entry special-behavior table is exactly
`2270,2271,2272,2273,2274,2296,2297,2298,2299,227C,227D,229A,22B0,22B1,22B2`.
This removes the old need to transfer executable semantics from V18 for the
Operation-FFD parser.

### Image FFD

Current `CCmdImgOpeDdr::GetTSS3ImageFFDInfo` directly calls, in order, the
spec-information path, the spec-dependent availability path, **six-byte
`SecurityUnlock`**, then the encryption-method path. The current wire templates
are:

| Purpose | Request | Positive |
|---|---|---|
| spec information | `22 11 03` | `62 11 03` |
| image availability | `22 11 01` | `62 11 01` |
| SecurityAccess seed | `27 03` | `67 03 + 6-byte seed` |
| SecurityAccess key | `27 04 + 6-byte key` | `67 04` |
| encryption method | `22 20 81` | `62 20 81` |

The security key is generated by the **current**
`CCmdImgOpeDdr::CalculateKeyDataSecLv49` body; current-body vectors reproduce
`010203040506 -> 04070a0d1a64`, `123456789abc -> 9e6a50252409`,
`deadbeefcafe -> cbd8b6970cba`, and zero -> zero. A separate
`SecurityUnlock16Byte`/`CalculateKeyDataSecLv2` implementation exists in the
same DLL but is **not** the direct path called by `GetTSS3ImageFFDInfo`.

Image spec values **5** and **7** are explicitly accepted. Availability byte
value **2** marks memorized image slots: 1..10 for spec 5 and 1..11 for spec 7.
This is host acquisition/authentication semantics; it still does not identify
the ECU-side recorder producer, CAN/CAN-FD arbitration IDs, or SecOC owner. The
former PCS managed-initializer boundary is closed above: the recovered viewer
supplies exact Operation-FFD bit/scaling/RoB tables and also makes the Image-FFD
initializers executable.

The current native Image plugin and recovered viewer now join at the record
transport as well. `GetTSS3ImageFFDP5_DT.dll` byte-anchors **`AB31 -> EB31`**
for BE16 RoB-code enumeration and **`AB33 || rob_code_be16 || frame_number_be32
-> EB33`** for record fetch. The raw EB33 response is:

```text
EB33 || rob_code_be16 || frame_number_be32 || block_count_u8 || blocks...
```

The count is byte 8 and blocks begin at byte 9. Each block is
`data_id_be16 || length || data[length]`; `6xxx` image DIDs use a **BE32** length,
while other DIDs use a one-byte length. If the count byte is zero the native
parser derives the count by scanning valid blocks from byte 9. It deduplicates
Data IDs and retains the same special `0501` BE16 metadata behavior seen in the
Operation path. Current frame-number helpers use `0x200`-wide split groups and
the acquisition loops cover split numbers **1..22**.

The recovered viewer independently parses the logged EB33 text with the exact
same geometry: RoB at hex offset 4/length 4, frame number at offset 8/length 8,
and DID blocks at hex offset **18** (= byte 9). Its split-image table is exactly
`6002..6017` (22 DIDs). For each split group it appends the first present split
DID in that order and publishes the concatenation as synthetic raw-image DID
**`6001`**; group 1 removes `6002` from the copied metadata before publishing.
The viewer detects `EB21` as the unsplit discriminator and `EB31` as split, but
the current `Extract` implementation rejects the EB21 branch and proceeds via
`EB31/EB33`. Frame-number encoding is also closed in both directions. A value
whose high 16 bits are zero is an occurrence selector:
`split*0x200 + set*10 + trigger - 10`. A nonzero high half is the time-series
form: `high16 = split*0x200 + set*10 - 9`, while the low half is one less than
the viewer's recovered trigger number. The managed decoder independently
recovers split/set/trigger/type from those fields, providing a round-trip check
on the native helper semantics rather than relying on function-name inference.

The restored FCM TSS3 image bodies close the payload transform too.
`LogAnalyser622081::GetEncryption` reads the two hex characters immediately
after positive-response prefix `622081` and `FFImage::JudgeEncryption` treats
exact value **`01` as unencrypted**; any other value selects the decryption
branch in `FFImage::Create`. Specs 5 and 7 both index the same image-table row:
**360×180**, filename format **`{0:D3}.jpg`**, encryption key **`0xAA`**. For
each ciphertext byte the viewer reverses all eight bit positions and then XORs
the result with `0xAA`:

```text
plain_byte = reverse_bits8(cipher_byte) XOR 0xAA
```

The generated managed-semantics artifact pins the method RVAs, status-field
substring geometry, table constants and bit-transform opcode pattern, and the
verification suite exercises independent byte vectors. This is the exact
current host decode algorithm; it is not a claim about how the FCM internally
forms or protects image data before the diagnostic readout.

## 10. Shipped FFD parameter help adds plain-language semantics

The viewer also ships `Help/ParameterHelp.chm`. Its `FFD.htm` page is an
independent OEM-authored help table with **28 parameter names and descriptions**.
A deterministic extractor now preserves that table and exact normalized joins
back into the recovered resource dictionary:

`data/generated/gtsplus_2026/pcs_data_viewer_parameter_help.json`

High-value descriptions include:

| Help parameter | OEM description |
|---|---|
| PCS control status | `3:PCS operation`, `0:PCS non-operation` |
| Deceleration Request Output Value | PCS deceleration request |
| Target Object Number | Object number of PCS control target |
| Relative acceleration for control target | Relative acceleration of PCS control target |
| Distance for control target | Following distance of PCS control target |
| Relative speed for control target | Relative speed of PCS control target |
| **Lateral position for control target** | **Lateral position of PCS control target** |
| Steering angle | Steering angle |

Twelve help names join exactly (case/punctuation normalized) to resource keys,
including `PBA Request Status -> FFD_TSS3_ID_5792`, `Target Object Number ->
FFD_TSS3_ID_573E`, and `Steering angle -> FFD_TSS3_ID_523D`. The remaining
help rows are retained as descriptions without guessed recorder IDs.

The PBA help is especially useful because it documents value semantics across
Toyota system families: for TSS P/LSS+A it enumerates `00 No assist / 01 PBA1 /
10 PBA2 / 11 PBA3`, while the TSS C interpretation collapses the states to
request/no-request behavior. This is host documentation, not a claim that every
TSS3 generation uses the same raw field or network encoding.

## 11. What remains bounded

1. **Recorder ID -> CAN frame.** The managed table now closes recorder
   byte/bit/scaling semantics, but recorder IDs remain an internal AB/EB record
   namespace rather than network arbitration IDs. Firmware/dynamic correlation
   is still required to map a recorder field to a bus frame/producer.
2. **Producer/auth ownership.** The host acquisition and viewer decode paths do
   not by themselves identify which ECU constructs each recorder field on the
   vehicle network, nor the relevant CAN-FD/SecOC ownership boundary.
3. **Runtime trigger occurrence.** The 47 RoB definitions recover configured
   sampling/pre/post policy; they do not prove a particular vehicle actually
   emitted a given RoB event in a retained drive.
4. **Arbitration execution owner.** The existence of generic TSS request and
   arbitration-result fields proves the software abstraction, not which ECU
   executes the arbitration on every TSS3 architecture.

The immediate practical use is to treat PCS Data Viewer as a second Rosetta
stone alongside GTS+ DDBs: search the full generated dictionary for a firmware
or dynamic concept first, then use the OEM recorder name to drive targeted
firmware/CAN correlation.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-082](../reference/index.md#finding-tms-082), [TMS-084](../reference/index.md#finding-tms-084)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->

### Exact Camry live confirmation (2026-09-01)

The release-local Image-FFD protocol above has now been exercised read-only against the exact
2026 Camry `FRC_P5` endpoint `0x792 -> 0x79A` (F181 `8646F3315000`). Extended session plus
level-49 SecurityAccess succeeded exactly as recovered: live seed
`69 0F 82 16 37 10` produced key `E1 FF 87 91 DB 01`, accepted by `27 04` with `67 04`.
The vehicle reports `22 20 81 -> 62 20 81 01`, so its current stored image payload is in the
viewer's unencrypted mode.

After unlock, `AB31` enumerated exact stored RoB codes
`2822,2821,2826,2823,2861`. `AB33 2822 00000201` (occurrence selector
split1/set1/trigger1) returned a populated `EB33` with six blocks:
`5101/2`, `0501/7`, `0502/4`, `0507/6`, `0511/4`, and first split-image DID
`6002/0x00000BCB`. This dynamically confirms the recovered
`AB33 || RoB_BE16 || frame_BE32` request, byte-8 block count, byte-9 block stream,
and BE32 `6xxx` length grammar. The live work remained read-only; no RoB deletion or
vehicle-control routine was invoked.
