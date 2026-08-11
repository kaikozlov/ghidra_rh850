# Techstream .ddb diagnostic database pipeline

> **Scope:** Parsing Techstream `.ddb` files to extract OEM diagnostic
> vocabulary for firmware annotation.
>
> **Document type:** tooling documentation
>
> **Status:** active — DDB parser and catalog extractor implemented
>
> **Evidence source:** external-source (Techstream V18.00.003 DLL decompilation)
>
> **Verification:** deterministic catalog generation
> (`tools/techstream/extract_catalog.py`)
>
> **Related:** [techstream.md](techstream.md),
> [Application diagnostics](../diagnostics/application.md)

## Executive summary

The `.ddb` corpus functions as an OEM semantic symbol server for the firmware.
It lacks code addresses, but contains diagnostic vocabulary useful for naming
services, DTCs, and freeze-data monitor values. Table identity comes from the
runtime factory, not from numeric-pattern guesses.

Three new tools implement the extraction pipeline:

| Tool | Purpose |
|---|---|
| `tools/techstream/parse_ddb.py` | Parse `.ddb` binary format: sections, LZSS decompression, string resolution |
| `tools/techstream/extract_catalog.py` | Build `diagnostic_annotations.json` from DDB corpus |
| `tools/techstream/extract_factory_table_map.py` | Derive both table-class maps from PE switch targets and constructor exports |
| `tools/techstream/extract_toyota_master_routes.py` | Join priority master categories to regional DLL/function/detail rows |
| `tools/techstream/extract_priority_ddb_semantics.py` | Emit consumer-proven priority fields while retaining all raw bytes |
| `tools/pe` (modified) | Fixed `import` to use `analyzeHeadless` for full PE analysis |

Calibration-focused output:
`data/generated/<firmware-sha>/diagnostic_annotations.json` — 354 entries
(54 DTCs with descriptions, 12 supported-PID records, 111 freeze-data
monitors, 177 steering-anchored
`U_English` strings). The complete regional output is
`data/generated/techstream_v18/steering_diagnostic_corpus.json`: 35 source
files, 25 structural payload variants, 129 unique DTC IDs, one actual
`CDbDidTable` record, 146 `CDbSupPidTable` records with 16 unique raw keys, and
1,257 freeze-data monitor records.

Section 14 (24-byte records) is PID display-option configuration (value
enums per PID group), not active test definitions. Dealer wizard/dialog text
lives in `U_English.ddb`, extracted separately with
its parallel resource identifiers. Those identifiers group UI resources but do
not by themselves bind a string to this ECU or to a firmware routine.

## .ddb file format

Modern formats 1–5 share the six-byte prefix `40 00 0C 16 0C 08`; bytes 6–7
vary by region. Format 6 uses the seven-byte prefix
`39 00 0C 16 0B 15 0F`; byte 7 is a language tag (`0x16` English through
`0x1A` Turkish in this corpus). Both families carry the null-terminated
signature `"DiagTool DataCtrl"`, and byte 8 encodes the format variant:

| Byte 8 | Type | Example files |
|---|---|---|
| `0x01` | Toyota master routing/enumeration database | `Toyota.ddb` |
| `0x02` | ECU database (uncompressed sections) | `EPS_P4DK3.ddb` |
| `0x04` | OEM description string database | `M_English.ddb` |
| `0x05` | UI string database | `V_English.ddb` |
| `0x06` | Dealer wizard/dialog string database (different header) | `U_English.ddb` |

Coverage is explicit rather than silent: `parse_master_db()` structurally
parses all three regional `Toyota.ddb` directories (67 NA, 67 EU, and 76 JP
sections), `parse_ecu_db()` handles all 1,368
format-`0x02` ECU databases (25,361 sections), and `load_string_db()` handles
the modern sectioned format-`0x04/05/06` string databases. Type-`0x03`
`Viewer.ddb` and nine legacy type-`0x04` files have distinct schemas and are
rejected rather than misrepresented as parsed ECU/string content.

The 2026-08-10 high-value residual audit further narrows the security-relevant
unknowns. All 35 regional `EPS*`/`EMPS*` type-2 files are structurally covered
through their complete section-type union (up to type 91). In
`Security_P4.ddb`, type 35 resolves to `Security Alarm Operation` and type 37
is a 50-record alarm-condition table (`Battery Desorption`, `Hood Open`,
`Luggage Open`, `Door Open`, etc.), so those previously opaque sections are not
promoted as SecurityAccess/key-provisioning structures merely because of the
filename. KgpDataCtrl's two pinned table factories now identify the relevant
type-1/type-2 section classes. All three regional type-1 `Toyota.ddb`
directories are fully covered structurally and expose, among others, CAN communication, ECU
category/function/description, DLL, communication-DID, and communication-RID
tables. The generated factory map independently resolves all 89 format-1 and
151 format-2 cases from executable switch targets to constructor exports.
Priority master routing is decoded further: section-16 record 294 maps category
317 to `EPS_P4DK3.ddb`, while record 496 maps category 581 to
`EPS_CAN_P4DK.ddb`; category IDs join to type-19 DLL and type-26/27
function/detail rows across the regions where those databases exist. Exact
source bytes and unresolved communication-DID/RID category edges remain in
`toyota_master_routes.json`. Its exact bytes still contain no
`8965B4512000` identifier, so the result is a family route, not a calibration
identity match.

### ECU databases

ECU `.ddb` files expose a type-indexed directory of little-endian `u32` section
offsets beginning at `0x24` and ending at the first section payload. Every
nonzero directory slot points to a section beginning with a 10-byte
`TABLE_DATA_HEAD`; section payloads are not discovered by assuming they were
appended in type order:

```
[u8 table_type] [u8 compression] [u32 record_count] [u32 payload_size]
```

A section directory at file offset `0x24` lists `u32` offsets indexed by
section type and extends to the first section payload (`0x280` in the V18 ECU
files). The former parser stopped at slot 16 and silently dropped 10,659 of
25,361 sections across the type-2 corpus. The parser now follows the complete
directory and checks that each pointed header's type equals its slot.

Section types observed in EPS databases:

| Type | Records | Size/rec | Content |
|---|---|---|---|
| 0 | 11 | 12 B | `CDbSignalGroupTable` |
| 1 | 11 | 8 B | `CDbSignalCheckTable` |
| 3 | 4 | 8 B | `CDbSupPidTable` (supported-PID metadata) |
| 5 | 24 | 28 B | `CDbDiagCodeTable` (DTCs) |
| 6 | 29 | 8 B | `CDbPidTable` (PID records; not subfunctions) |
| 7 | varies | 8 B | `CDbDidTable` (only one steering row, in EU `EPS_PSA`) |
| 10 | 36 | 84 B | `CDbFreezeTable`; names exposed by `GetDataMonitorName` |
| 13 | 17 | 24 B | `CDbPhyDataTable` |
| 14 | 15 | 24 B | `CDbPatDispTable` (display options/value enums) |
| 15–16 | — | — | `CDbUnitTable` / `CDbTriggerListTable` |
| 18–91 (steering corpus) | — | — | Factory-classified and structurally inventoried; field semantics selectively bounded |

The selective decode is reproducible rather than label-only. Exported
KgpDataCtrl lookup, string-resolution, variable-resolution, and sort methods
prove field offsets for types 6/11/12/61/62/63/80/87/88/90/91. The generated
priority artifact covers 32 steering files, 76 section instances, and 6,521
records. Each named field carries its consumer RVA and method-prefix hash, and
each record retains complete `raw_hex`; unknown bytes remain unknown. See
`data/generated/techstream_v18/priority_steering_ddb_semantics.json` and
`tests/verify_techstream_priority_ddb_semantics.py`.

### DTC record format (section type 5, 28 bytes)

```
[0:12]  DTC code (UTF-16LE, e.g. "C1511\0\0")
[12:16] u32 name_string_index (1-based index into M_English)
[16:20] u32 comment_string_index (0 = none)
[20:22] u16 DTC identifier (e.g. 0x5511)
[22:28] additional flags
```

### P5 DTC failure-type record format (section type 65, 68 bytes)

Techstream's P5 databases carry a second, richer DTC table in section type 65.
Across 131 pinned V18 databases this section has a stable 68-byte record shape:

```text
[0x00:0x2C] UTF-16LE full code, e.g. "U023A87"
[0x2C:0x30] u32 packed_dtc = (base_dtc << 8) | failure_type
[0x30:0x34] u32 base-description string index in M_English
[0x34:0x38] u32 failure-type string index in M_English
[0x38:0x40] additional fields, semantics not yet assigned
[0x40:0x44] u32 tail word (extracted; semantics not attributed)
```

`tools/techstream/generate_dtc_failure_types.py` scans all such records and
emits `data/generated/techstream_v18/dtc_failure_types.json`. The corpus gives a
direct Toyota/Techstream mapping for standard failure-type bytes:

| failure byte | dominant Techstream text |
|---:|---|
| `0x81` | Invalid Serial Data Received |
| `0x82` | Alive / Sequence Counter Incorrect / Not Updated |
| `0x83` | Value of Signal Protection Calculation Incorrect |
| `0x84` | Signal Below Allowable Range |
| `0x85` | Signal Above Allowable Range |
| `0x86` | Signal Invalid |
| **`0x87`** | **Missing Message** |
| `0x88` | Bus Off |

The `0x87` mapping is especially strong: 1,519 section-65 records point to
`M_English` index 64829, exactly `Missing Message`; another 27 records use the
same text with alternate string indices/case, while the remaining 130 records
carry only raw `87`/`$87` labels. For `U023A87` specifically, all 20 records
whose `+0x40` tail word is nonzero resolve the failure text to `Missing Message`.
No pinned accessor names that word as an enable flag. `EMPS_P5.ddb` record 125
is an exact example: packed `0xC23A87`, base description `Lost Communication
with Image Processing Module "A"`, failure string `Missing Message`.

This closes the earlier ambiguity around the field-reported RAV4 Prime code:
Techstream itself statically defines the `0x87` suffix as **Missing Message**;
it is not an inferred UI paraphrase. The verifier independently walks the raw
directory, matches an immutable 68-byte fixture, and pins the exported consumer
extents proving `+0x2C`, `+0x30`, and `+0x34`; swapping the parser string-index
offsets therefore fails independently.

### String databases

String databases (`M_English.ddb`, `V_English.ddb`) store one LZSS-compressed
block. The section header at offset `0x28` specifies `compression=1`.

**Critical:** ECU databases reference three separate string databases with the
same index space but different content. DTC names and monitor names resolve
through `M_English.ddb`, not `V_English.ddb`:

| String index | `V_English` | `M_English` |
|---|---|---|
| `0x5E36` | "Cancel" | **"Torque Sensor"** |
| `0x5E37` | "Input" | **"Torque Sensor Power Supply"** |
| `0x5E3E` | "B" | **"IG Power Supply Voltage"** |

## LZSS compression (DataCompress_DT.DLL)

Recovered by decompiling `_DataDecode@12` (export ordinal 1) in
`DataCompress_DT.DLL` via the vendored Ghidra CLI PE project.

Block format: `[u32 decompressed_size][u8 checksum][LZSS stream]`.

Algorithm (from vtable[1] at RVA `0x1BD0`):

- 0x1000-byte sliding window, initial write position `0xFEE`
- Flag-byte-driven: read one flag byte, process 8 bits (LSB first)
  - bit 1 = literal: copy 1 byte to output and window
  - bit 0 = match: read 2 bytes `(b1, b2)`, copy `(b2 & 0xF) + 3` bytes from
    window position `(b1 | ((b2 & 0xF0) << 4)) & 0xFFF`

## String index resolution

Recovered by decompiling `CDbVariableTable::GetVariable` at RVA `0x50383` in
`KgpDataCtrl.dll`.

Indices are **1-based** (0 = null). Each 6-byte entry in the offset table:

```
[u32 offset_in_pool][u16 byte_length]
```

String data lives at `pool_offset + entry.offset`, encoded UTF-16LE, for
`entry.byte_length` bytes. `pool_offset = entry_count × 6`.

Verification: `M_English.ddb` decompresses to 10,089,890 bytes (exact LZSS
match), 183,244 string entries.

## Generated catalog

`extract_catalog.py` produces `diagnostic_annotations.json`:

```json
{
  "firmware_sha256": "21140bbd...",
  "techstream_distribution": "V18.00.003",
  "ecu": { "family": "EPS", "software_id": "8965B4512000", "protocol": "P4CAN" },
  "entries": [
    {
      "kind": "dtc",
      "code": "C1511",
      "dtc_identifier": 21777,
      "name_string_index": 24118,
      "resolved_name": "Torque Sensor",
      "source_db": "EPS_P4DK3"
    }
  ]
}
```

### Catalog contents

- **54 DTCs** — all with OEM descriptions (e.g. "Torque sensor deviation
  excessive", "Motor relay failure", "CAN communication error (ABS/VSC)")
- **12 supported-PID records** — raw section-3 `CDbSupPidTable` rows from the
  two selected P4 databases; they are not DIDs and are not firmware-correlated
- **111 freeze-data monitors** — type-10 `CDbFreezeTable` names like "Torque Sensor 1 Output", "Motor Actual
  Current", "Steering Angle Velocity", "Thermistor Temperature"
- **177 `utility_string` entries** — exhaustive strings with explicit steering
  anchors from `U_English`; family vocabulary only. The parallel type-1 section
  supplies 25,957 stable resource identifiers aligned with the string indices,
  but does not encode ECU ownership or firmware routine linkage, so these are
  not recovered procedures.

### DTC cross-reference

EPS DTCs map directly to firmware diagnostic identifiers. The `EPS_CAN_P4DK`
variant provides the most detailed descriptions:

| Code | OEM name | System |
|---|---|---|
| C1511 | Torque sensor1 | Torque sensor |
| C1512 | Torque sensor2 | Torque sensor |
| C1513 | Torque sensor deviation excessive | Torque sensor |
| C1514 | Torque sensor power supply abnormal | Power supply |
| C1523 | Motor terminal abnormality 1 | Motor |
| C1531 | CPU malfunction | ECU |
| C1534 | EEPROM error | ECU |
| C1554 | Power supply relay failure | Power supply |
| C1555 | Motor relay failure | Motor relay |
| U0121 | CAN communication error (ABS/VSC) | CAN bus |

## Correlation engine

The catalog is the first layer. The second layer — `tools/diagnostics/correlate_vocabulary.py`
— correlates the Techstream vocabulary with firmware diagnostic tables extracted
by `tools/diagnostics/firmware_tables.py`, producing a richer artifact:
`diagnostic_vocabulary.json`.

### Pipeline architecture

```
Techstream .ddb → extract_catalog.py → diagnostic_annotations.json
                                                      ↓
firmware bytes  → firmware_tables.py → FirmwareTables
                                                      ↓
                                     correlate_vocabulary.py
                                                      ↓
                                       diagnostic_vocabulary.json
                                                      ↓
                                       ApplyDiagnosticVocabulary.java
                                                      ↓
                                           annotated Ghidra project
```

The key design choice is the neutral intermediate representation. The Ghidra
script does not understand `.ddb`; it consumes a deterministic generated artifact.

### New tools

| Tool | Purpose |
|---|---|
| `tools/diagnostics/firmware_tables.py` | Extract DID/service/routine/write-DID structures from raw CodeFlash |
| `tools/diagnostics/correlate_vocabulary.py` | Match Techstream catalog with firmware tables, emit graded vocabulary |
| `ghidra/scripts/annotate/ApplyDiagnosticVocabulary.java` | Apply OEM names/comments to Ghidra project |
| `tests/verify_diagnostic_vocabulary.py` | Deterministic verification of every correlation |

### Match grades

Every mapping carries a confidence grade. `exact` and `structural` mappings are
eligible for renaming only when the artifact explicitly emits
`annotation_action: name_callback`; a numeric DID match without a recovered
semantic name remains comment-only. `family` is always comment-only.

| Grade | Meaning | Annotation action |
|---|---|---|
| `exact` | Identifier exists in both firmware and an EPS database | Rename function / label data |
| `structural` | Identifier + payload/session/service context match | Rename function / label data |
| `family` | Identifier matches an EPS database for the same protocol generation | Comment only |
| `candidate` | Identifier matches but descriptions conflict across databases | Comment with conflict warning |
| `rejected` | Techstream constraints contradict firmware evidence | Skip |

### Correlation results

Current output (345 mappings):

| Kind | Count | Exact | Structural | Family |
|---|---:|---:|---:|---:|
| DTCs | 54 | 12 | — | 42 |
| Freeze-data monitors | 97 | — | 7 | 90 |
| Services | 17 | 17 | — | — |
| Utility strings | 177 | — | — | 177 |

No selected P4 database carries a type-7 `CDbDidTable`; consequently there are
no direct DDB→firmware DID correlations. The previous eleven were a disproved
reinterpretation of type-3 `CDbSupPidTable` bytes (CORR-030).
DTC correlation structurally scans all `0xA0` 8-byte records used by
`FUN_0005159e`/`FUN_000517b4`, at `0x309DC`–`0x30EDC`; blind byte matches elsewhere in
CodeFlash are rejected. The record's byte 0 is now preserved as the UDS
failure-type/subtype byte rather than collapsed into an opaque flag. The
correlator also follows the generated 0x180-entry Dem-event table at `0x2FDDC`,
whose byte 2 selects a DTC-table index. This exposes, for example, adjacent
enabled `U023A` (`0x00`) and **`U023A87`** (`0x87`) records: no configured event
maps directly to the base record, while events `0xB0`, `0xB3`, `0x138`, `0x13C`,
and `0x13D` map specifically to `U023A87`. Twelve of 54 Techstream DTC records
match enabled firmware entries, including five CAN-communication records
(`U0100`, `U0126`, `U023A`, `U0293`, `U1103`) beyond the old truncated
`0x30C40` bound. The remaining 42 are diagnostic-only or cross-generation. Monitors whose
seq-derived DID is actually present bridge to firmware callbacks; the rest
remain family vocabulary.

### Freeze-data monitor→firmware-DID bridge

The type-10 runtime class is `CDbFreezeTable`, and its record API explicitly
exposes `GetDataMonitorName`/`GetDataMonitorShortName`. A bounded structural
bridge uses the row field at offset 56 (the "seq" number) as
**candidate firmware DID = 0x0100 + seq**. This is not a `CDbDidTable` join;
confidence comes from the independent firmware callback/data-source recovery
and semantic agreement for the seven auto-named rows.

For nine monitors with seq < 100, `DID = 0x0100 + seq` hits the firmware DID
table exactly. The EPS_CAN_P4DK variant (UDS/CAN) supplies the selected family
name; EPS_P4DK3 (KWP) supplies alternate monitor vocabulary for the same
seq-derived candidate identifiers. This numerical coincidence alone remains
family-grade.

Nine monitors bridge to firmware DIDs. Seven have independently decompiled,
meaningful RAM sources and are structural/auto-named. DID `0x0101` lacks an
independent source recovery and DID `0x0111` is a stub; both remain family
comment-only. The CAN-family label is preferred over the KWP-family label as a
vocabulary choice, not as proof of calibration-specific semantics:

| DID | OEM name (CAN) | Callback | RAM source |
|---|---|---|---|
| 0x0101 | Diagnosis codes when FFD stored | 0x4E98E | — |
| 0x0102 | Vehicle speed | 0x4CBFC | FEBEE90C, FEBEE896, FEBEE815 |
| 0x0103 | Engine revolution speed | 0x4CC76 | FEBEE910, FEBEE814 |
| 0x0105 | **Motor instruction current** | 0x4CCC4 | checkpoint obj 0x204 |
| 0x0109 | **Steering torque** | 0x4CD38 | FEBEE867–86C (6B) |
| 0x010B | **Output of torque sensor 2** | 0x4CD74 | checkpoint obj 0x20A |
| 0x0110 | IG switch status | 0x4CDD4 | FUN_0006909A + GP[-0xB99] |
| 0x0111 | Torque sensor power supply | 0x4CDFC | stub (returns 0) |
| 0x0112 | No. of diagnosis codes | 0x4CE00 | FEBE8AB0 + FEBE89A4 |

The motor-current and torque-sensor values come from checkpoint objects —
persistent NvM-backed snapshots validated by a magic number (0xA55A5AA5).
This bridges OEM diagnostic vocabulary to specific firmware state variables,
enabling the "semantic recovery amplifier" described in the pipeline
architecture: a monitor name like "Motor instruction current" now resolves to a
specific DataFlash-backed 10-byte object in firmware.
`ghidra/scripts/verify/AssertDiagnosticVocabulary.java` independently asserts
the seven structural callbacks' RAM/checkpoint references and decompiler
landmarks; the generated source descriptions are not their own test oracle.

### Preserve two namespaces

OEM labels from Techstream are never conflated with recovered implementation
semantics. A function named by `AnnotateApplicationDiagnostics` keeps its
recovered-behavior name; the OEM label is appended as a comment. Only unnamed
functions (`FUN_*` / `LAB_*`) receive OEM-name renames from this pipeline.

### Entry into the rebuild

The vocabulary is generated before Stage 4 annotation and applied after
`AnnotateApplicationDiagnostics`:

```
Stage 4, before analysis:
  generate diagnostic_annotations.json (extract_catalog.py)
  generate diagnostic_vocabulary.json (correlate_vocabulary.py)
  seed all 196 unique callbacks referenced by the 242-row DID table

Clean-checkout fallback:
  if the ignored Techstream source tree is absent, consume the tracked
  firmware-SHA-keyed diagnostic_vocabulary.json instead

Stage 4, after analysis:
  run AnnotateApplicationDiagnostics.java (firmware-recovered names)
  run ApplyDiagnosticVocabulary.java      (OEM vocabulary layer)

Verification:
  tests/verify_diagnostic_vocabulary.py (190+ checks against raw artifacts)
```

The Java script (`ApplyDiagnosticVocabulary.java`) includes a self-contained
JSON parser (Ghidra does not ship Gson or javax.json).  The parser correctly
handles numeric fields (`identifier`, `sid`, `dtc_identifier` are JSON
numbers, not strings) and applies OEM names/comments to service and monitor
callbacks. Missing exact/structural callback functions now fail the rebuild;
actual rename/comment/already-applied effects are counted separately. The
vocabulary path is passed as a script argument — no hardcoded paths or firmware
SHA prefixes.

## tools/pe fix

`tools/pe import` previously used the Ghidra CLI bridge's built-in import,
which runs a shallow analysis pass that resolves 0 functions and 0 instructions
in MSVC-compiled C++ PEs. The fix routes `import` through `analyzeHeadless`
directly (the same approach `tools/rebuild_project.sh` uses for the RH850
project), then all other subcommands use the bridge for interactive queries.

Before: `DataCompress_DT.DLL` — 0 functions, 0 instructions.
After: 157 functions, 6,848 instructions.

## P4DK4 cross-variant template

`EPS_P4DK4.ddb` (JP region only) is the richest EPS database in the Techstream
V18 corpus: 26 unique DTCs (45 records with dual naming), 89 monitors, 85
raw `CDbPidTable` records. It is a JP-market diagnostic variant, not a later
release — the Techstream V18.00.003 distribution is dated December 2022 and
predates both the 2023 Sienna and the 2025 Corolla. P4DK4's larger freeze-data monitor
count proves a vocabulary/configuration difference (e.g. torque sensor 3,
backup power supply), not a temporal or hardware-generation gap. It is a useful
supplementary
vocabulary source because its 13 extra candidate bridges cover EPS state variables
absent from the NA database, giving the correlation engine more matches to
work with when Corolla firmware arrives.

### Corpus comparison

| Database | Region | DTCs | Supported-PID rows | Freeze-data monitors | PID rows |
|---|---|---|---|---|---|
| `EPS_CAN_P4DK` | NA | 30 | 8 | 75 | 32 |
| `EPS_P4DK3` | NA | 24 | 4 | 36 | 29 |
| `EPS_P4DK4` | JP | 26 (45 records) | 16 | 89 | 85 |

P4DK4's 45 DTC records carry dual naming (formal + alternate name per DTC),
yielding 26 unique DTC identifiers. Its 89 freeze-data monitors include 78 with
seq < 100 (candidate bridge `DID = 0x0100 + seq`), compared to 64 in NA.

### New freeze-data monitor candidates not in the NA template

P4DK4 adds 13 seq-derived candidate firmware-DID labels absent from the NA
database. These are structural correlation candidates, not `CDbDidTable`
records:

| seq | DID | OEM name |
|---|---|---|
| 19 | 0x0113 | (unnamed in M_English) |
| 20 | 0x0114 | (unnamed) |
| 21 | 0x0115 | (unnamed) |
| 49 | 0x0131 | DTC that caused FFD 2 |
| 56 | 0x0138 | Torque sensor 3 output |
| 64 | 0x0140 | Backup power supply voltage |
| 66 | 0x0142 | Torque sensor power supply |
| 67 | 0x0143 | Internal pressor power supply |
| 68 | 0x0144 | Power supply monitor value |
| 71 | 0x0147 | Assist. map state |
| 72 | 0x0148 | (unnamed) |
| 73 | 0x0149 | (unnamed) |
| 74 | 0x014A | (unnamed) |

The torque-sensor-3 and backup-power-supply labels are vocabulary present in
the JP diagnostic variant and absent from the NA one. That does not prove a
market-specific hardware feature in any firmware calibration.

### Extraction tool

`tools/techstream/extract_p4dk4_catalog.py` — produces
`data/generated/p4dk4_template/p4dk4_vocabulary.json`, a standalone
vocabulary artifact (not firmware-correlated). Intended for use as a search
template when Corolla firmware arrives. Its schema is intentionally not an
input to the Sienna-only `correlate_vocabulary.py`; a variant-specific adapter
must select and grade P4DK4 records against that firmware's own tables before
they can become annotation mappings.

### Regional DDB access

The DDB parser now accepts all regional variants (NA/JP/EU). Bytes 6–7 of the
file magic carry a region/version tag (NA: `00 39`, JP: `01 1b`, EU: `00 14`);
only the first 6 bytes and the `DiagTool DataCtrl` signature are constant.

## RE provenance

| Finding | Source DLL | Function | Method |
|---|---|---|---|
| LZSS algorithm | `DataCompress_DT.DLL` | `_DataDecode@12` → vtable[1] @ `0x1BD0` | Ghidra decompile |
| String index resolution | `KgpDataCtrl.dll` | `CDbVariableTable::GetVariable` @ `0x50383` | Ghidra decompile |
| File format / section loading | `KgpDataCtrl.dll` | `CDbTableRead::CreateTable` @ `0x4D0D3` | Ghidra decompile |
| DTC record → name mapping | `KgpDataCtrl.dll` | `CDbDiagCodeResRecords::SetRecString` @ `0x2EC9D` | Ghidra decompile |
| String table selection | Empirical | `0x5E36` resolves differently in V/M English | Index comparison |
