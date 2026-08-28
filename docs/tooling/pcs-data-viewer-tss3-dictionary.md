# PCS Data Viewer TSS3 recorder dictionary

> **Scope:** the current GTS+ `PCS Data Viewer` 12.00.005 executable,
> English/Japanese satellite resources, and the native `FRC_P5` TSS3
> Operation/Image FFD plugins.
>
> **Status:** recovered host-side dictionary/model surface; concrete per-field
> bit assignments/scalings remain bounded by protected managed initializers.
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

The shipped managed method bodies are protected/zero-filled, but .NET metadata
remains intact. The recovered type/model surface includes:

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

Therefore the viewer contains a data-driven map from recorder ID/bit placement
to physical values and RoB grouping/sampling policy. The concrete initialized
instances are in protected managed initializers in this shipped image, so this
pass does not claim their exact bit/LSB/offset table.

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

## 9. Shipped FFD parameter help adds plain-language semantics

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

## 10. What remains bounded

1. **Concrete bit assignments/scalings.** The schema is recovered, but the
   populated `DetailBitAssignInfo`/RoB tables are built in protected managed
   initializers. A runtime dump, an unprotected matching viewer, or another
   data source is needed for exact byte/bit/LSB/offset recovery.
2. **Recorder ID -> CAN frame.** The dictionary decodes the internal recorder
   namespace, not network arbitration IDs. Firmware/dynamic correlation is
   still required to map a recorder field to a bus frame.
3. **Arbitration execution owner.** The existence of generic TSS request and
   arbitration-result fields proves the software abstraction, not which ECU
   executes the arbitration on every TSS3 architecture.
4. **Image encryption details.** Metadata proves an encryption-aware image
   path, but key/algorithm behavior was not recovered from the protected
   managed bodies here.

The immediate practical use is to treat PCS Data Viewer as a second Rosetta
stone alongside GTS+ DDBs: search the full generated dictionary for a firmware
or dynamic concept first, then use the OEM recorder name to drive targeted
firmware/CAN correlation.
