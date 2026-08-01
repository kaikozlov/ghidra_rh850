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
It lacks code addresses, but contains the identifiers and human meaning needed
to turn recovered diagnostic tables into named services, DTCs, monitor values,
and active tests.

Three new tools implement the extraction pipeline:

| Tool | Purpose |
|---|---|
| `tools/techstream/parse_ddb.py` | Parse `.ddb` binary format: sections, LZSS decompression, string resolution |
| `tools/techstream/extract_catalog.py` | Build `diagnostic_annotations.json` from DDB corpus |
| `tools/pe` (modified) | Fixed `import` to use `analyzeHeadless` for full PE analysis |

Calibration-focused output:
`data/generated/<firmware-sha>/diagnostic_annotations.json` — 353 entries
(54 DTCs with descriptions, 11 DIDs, 111 monitors, 177 steering-anchored
`U_English` strings). The complete regional output is
`data/generated/techstream_v18/steering_diagnostic_corpus.json`: 35 source
files, 25 full-section semantic variants, 129 unique DTC IDs, 16 unique DIDs, and 1257
monitor records.

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
| `0x02` | ECU database (uncompressed sections) | `EPS_P4DK3.ddb` |
| `0x04` | OEM description string database | `M_English.ddb` |
| `0x05` | UI string database | `V_English.ddb` |
| `0x06` | Dealer wizard/dialog string database (different header) | `U_English.ddb` |

Coverage is explicit rather than silent: `parse_ecu_db()` handles all 1,368
format-`0x02` ECU databases (25,361 sections), and `load_string_db()` handles
the modern sectioned format-`0x04/05/06` string databases. Type-`0x01`
`Toyota.ddb`, type-`0x03` `Viewer.ddb`, and nine legacy type-`0x04` files have
distinct schemas and are rejected by these APIs; they are inventoried but not
misrepresented as parsed ECU/string content.

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
| 0 | 11 | 12 B | PID/monitor lookup table |
| 1 | 11 | 8 B | PID/monitor index pairs |
| 3 | 4 | 8 B | DID identifiers |
| 5 | 24 | 28 B | DTCs (code + name index + identifier) |
| 6 | 29 | 8 B | Sub-function definitions |
| 10 | 36 | 84 B | Data monitors (PID name + scaling) |
| 13 | 17 | 24 B | PID group metadata |
| 14 | 15 | 24 B | PID display-option configuration (value enums) |
| 15–16 | — | — | Additional monitor/test metadata |
| 18–91 (steering corpus) | — | — | Additional schema tables; preserved and inventoried, semantics mostly bounded |

### DTC record format (section type 5, 28 bytes)

```
[0:12]  DTC code (UTF-16LE, e.g. "C1511\0\0")
[12:16] u32 name_string_index (1-based index into M_English)
[16:20] u32 comment_string_index (0 = none)
[20:22] u16 DTC identifier (e.g. 0x5511)
[22:28] additional flags
```

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
- **11 DIDs** — all within firmware DID table range (0x0100–0xF18C),
  deduplicated by identifier across DDB variants
- **111 monitors** — names like "Torque Sensor 1 Output", "Motor Actual
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

Current output (356 mappings):

| Kind | Count | Exact | Structural | Family |
|---|---:|---:|---:|---:|
| DIDs | 11 | 1 | — | 10 |
| DTCs | 54 | 12 | — | 42 |
| Monitors | 97 | — | 7 | 90 |
| Services | 17 | 17 | — | — |
| Utility strings | 177 | — | — | 177 |

DID correlation uses actual membership in the sparse 242-entry firmware DID
table. Only one catalog DID is present; the other ten remain family-level.
The neutral catalog no longer infers membership merely because an identifier
falls between the table's minimum and maximum values.
DTC correlation structurally scans all `0xA0` 8-byte records used by
`FUN_0005159e`/`FUN_000517b4`, at `0x309DC`–`0x30EDC`; blind byte matches elsewhere in
CodeFlash are rejected. Twelve of 54 Techstream DTC records match enabled
firmware entries, including five CAN-communication records (`U0100`, `U0126`,
`U023A`, `U0293`, `U1103`) beyond the old truncated `0x30C40` bound. The
remaining 42 are diagnostic-only or cross-generation. Monitors whose
seq-derived DID is actually present bridge to firmware callbacks; the rest
remain family vocabulary.

### Monitor→DID bridge

The key structural discovery: monitor record field at offset 56 (the "seq"
number) maps to firmware DIDs via **DID = 0x0100 + seq**.  This is not in the
.ddb section 0/1 lookup tables — those use proprietary PIDs (0x2711+).

For nine monitors with seq < 100, `DID = 0x0100 + seq` hits the firmware DID
table exactly. The EPS_CAN_P4DK variant (UDS/CAN) supplies the selected family
name; EPS_P4DK3 (KWP) uses different naming for the same DIDs.

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
subfunction definitions. It is a JP-market diagnostic variant, not a later
release — the Techstream V18.00.003 distribution is dated December 2022 and
predates both the 2023 Sienna and the 2025 Corolla. P4DK4's larger monitor
count proves a vocabulary/configuration difference (e.g. torque sensor 3,
backup power supply), not a temporal or hardware-generation gap. It is a useful
supplementary
vocabulary source because its 13 extra bridged DIDs cover EPS state variables
absent from the NA database, giving the correlation engine more matches to
work with when Corolla firmware arrives.

### Corpus comparison

| Database | Region | DTCs | DIDs | Monitors | Subfns |
|---|---|---|---|---|---|
| `EPS_CAN_P4DK` | NA | 30 | 8 | 75 | 32 |
| `EPS_P4DK3` | NA | 24 | 4 | 36 | 29 |
| `EPS_P4DK4` | JP | 26 (45 records) | 8 | 89 | 85 |

P4DK4's 45 DTC records carry dual naming (formal + alternate name per DTC),
yielding 26 unique DTC identifiers. Its 89 monitors include 78 with seq < 100
(bridged to firmware DIDs via `DID = 0x0100 + seq`), compared to 64 in NA.

### New monitors not in the NA template

P4DK4 adds 13 bridged DIDs absent from the NA database:

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
