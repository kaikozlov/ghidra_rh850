# Techstream .ddb diagnostic database pipeline

> **Scope:** Parsing Techstream `.ddb` files to extract OEM diagnostic
> vocabulary for firmware annotation.
>
> **Document type:** tooling documentation
>
> **Status:** active — DDB parser and catalog extractor implemented
>
> **Evidence source:** external-source (Techstream V18.00.008 DLL decompilation)
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

Output: `data/generated/<firmware-sha>/diagnostic_annotations.json` — 213
entries (54 DTCs with descriptions, 12 DIDs, 111 monitors, 36 active tests).

## .ddb file format

All `.ddb` files share the magic `40 00 0C 16 0C 08 00 39` followed by the
null-terminated signature `"DiagTool DataCtrl"`. Byte 8 encodes the format
variant:

| Byte 8 | Type | Example files |
|---|---|---|
| `0x02` | ECU database (uncompressed sections) | `EPS_P4DK3.ddb` |
| `0x04` | OEM description string database | `M_English.ddb` |
| `0x05` | UI/active-test string database | `V_English.ddb` |
| `0x06` | Utility string database (different header) | `U_English.ddb` |

### ECU databases

ECU `.ddb` files store diagnostic tables as sequential sections. Each section
begins with a 10-byte `TABLE_DATA_HEAD`:

```
[u8 table_type] [u8 compression] [u32 record_count] [u32 payload_size]
```

A section directory at file offset `0x24` lists `u32` offsets to each section.
Additional sections may be appended after the directory-listed ones (sequential
scan from the end of the last listed section).

Section types observed in EPS databases:

| Type | Records | Size/rec | Content |
|---|---|---|---|
| 0 | 11 | 12 B | PID/monitor lookup table |
| 1 | 11 | 8 B | PID/monitor index pairs |
| 3 | 4 | 8 B | DID identifiers |
| 5 | 24 | 28 B | DTCs (code + name index + identifier) |
| 6 | 29 | 8 B | Sub-function definitions |
| 10 | 36 | 84 B | Data monitors (PID name + scaling) |
| 13 | 17 | 24 B | Active test definitions |
| 14 | 15 | 24 B | Active test descriptions |
| 15–16 | — | — | Additional monitor/test metadata |

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
  "techstream_distribution": "V18.00.008",
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
- **12 DIDs** — all within firmware DID table range (0x0100–0xF18C)
- **111 monitors** — names like "Torque Sensor 1 Output", "Motor Actual
  Current", "Steering Angle Velocity", "Thermistor Temperature"
- **36 active tests** — test descriptions and subfunction IDs

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

Every mapping carries a confidence grade. Only `exact` and `structural` trigger
symbol renames in Ghidra. `family` adds comment-only annotations.

| Grade | Meaning | Annotation action |
|---|---|---|
| `exact` | Identifier exists in both firmware and an EPS database | Rename function / label data |
| `structural` | Identifier + payload/session/service context match | Rename function / label data |
| `family` | Identifier matches an EPS database for the same protocol generation | Comment only |
| `candidate` | Identifier matches but descriptions conflict across databases | Comment with conflict warning |
| `rejected` | Techstream constraints contradict firmware evidence | Skip |

### Correlation results

Current output (230 mappings):

| Kind | Count | Exact | Candidate | Family |
|---|---|---|---|---|
| DIDs | 12 | 12 | — | — |
| DTCs | 54 | 16 | 18 | 20 |
| Monitors | 111 | — | — | 111 |
| Active tests | 36 | — | — | 36 |
| Services | 17 | 5 | — | 12 |

DID correlation is exact by construction: every Techstream DID is looked up
in the 242-entry firmware DID table, and the firmware callback address is
attached. DTC correlation finds the 2-byte little-endian representation of
each DTC identifier in CodeFlash — 42 of 54 DTCs have at least one firmware
location. Monitors are recorded as family-grade vocabulary for future callback
analysis.

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

Stage 4, after analysis:
  run AnnotateApplicationDiagnostics.java (firmware-recovered names)
  run ApplyDiagnosticVocabulary.java      (OEM vocabulary layer)

Verification:
  tests/verify_diagnostic_vocabulary.py (144 checks against raw firmware)
```

## tools/pe fix

`tools/pe import` previously used the Ghidra CLI bridge's built-in import,
which runs a shallow analysis pass that resolves 0 functions and 0 instructions
in MSVC-compiled C++ PEs. The fix routes `import` through `analyzeHeadless`
directly (the same approach `tools/rebuild_project.sh` uses for the RH850
project), then all other subcommands use the bridge for interactive queries.

Before: `DataCompress_DT.DLL` — 0 functions, 0 instructions.
After: 157 functions, 6,848 instructions.

## RE provenance

| Finding | Source DLL | Function | Method |
|---|---|---|---|
| LZSS algorithm | `DataCompress_DT.DLL` | `_DataDecode@12` → vtable[1] @ `0x1BD0` | Ghidra decompile |
| String index resolution | `KgpDataCtrl.dll` | `CDbVariableTable::GetVariable` @ `0x50383` | Ghidra decompile |
| File format / section loading | `KgpDataCtrl.dll` | `CDbTableRead::CreateTable` @ `0x4D0D3` | Ghidra decompile |
| DTC record → name mapping | `KgpDataCtrl.dll` | `CDbDiagCodeResRecords::SetRecString` @ `0x2EC9D` | Ghidra decompile |
| String table selection | Empirical | `0x5E36` resolves differently in V/M English | Index comparison |
