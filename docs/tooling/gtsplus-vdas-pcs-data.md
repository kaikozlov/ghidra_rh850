# GTS+ PCS Vehicle Data Analysis (`.vdas`) persistence

Current GTS+ has a second first-class persistence/export path for PCS recorder data in
addition to TSE/GTSE: **PCS Vehicle Data Analysis** files with extension `.vdas`.
Recovered same-release managed bodies close the container and payload-selection contract.

The important TSS3 result is direct: `GTSPlusDiagAdaptMng.dll` reads
**`TSS3OperationFFD.log`** into JSON model field **`Gts.Tss3Ffd.Data`** and
**`ImageFFD.log`** into **`Gts.PcsImg.Data`**, then packages that JSON as `json.log` in a
standard ZIP archive named `.vdas`. This means VDAS preserves exactly the PCS evidence
that the current TSE->GTSE converter is configured to skip.

Canonical machine-readable evidence is
`data/generated/gtsplus_2026/vdas_semantics.json`; `tests/verify_gtsplus_vdas_semantics.py`
regenerates it from the exact same-release installer plaintext twins.

## 1. Exact current components

The current 2026.03.002.02 installer provides exact unprotected twins for the two managed
components used here:

| Component | Size | SHA-256 |
|---|---:|---|
| `GTSPlus/bin/GTSPlusDiagAdaptMng.dll` | 57,360 | `7a56cc6488ad0f982b3b8ed531d5da0677d04f58c92b4b4ea3d0ac6508f27f9e` |
| `GTSPlus/bin/GTSPlusArchiver.dll` | 19,472 | `ce3c56ada831ea0b7164435fec8bc47184ea97c16b67469404a163fc1fedd7a2` |

The verifier recovers these from Toyota's installer `GTSPlus`/`GTSPlusCP` twin groups;
it does not depend on a pre-existing `build/` reconstruction.

## 2. VDAS creation

`DiagAdaptationManager::CreateVdasFile` implements this exact host pipeline:

```text
PCS/Image/DDR per-function *.log files
        |
        v
MakeImgOpeDdrJsonData(...)
        |
        v
JsonConvert.SerializeObject
        |
        v
UTF-8 json.log
        |
        v
GTSPlusArchiver.ZipFile::CompressFileToFile(..., 6)
        |
        v
{sanitized_VIN}_{yyyyMMddHHmmss}.vdas
```

The VIN is sanitized with `[^A-Za-z0-9-]+ -> _`. The JSON model format version is
**`001`**. Source log files are read as complete UTF-8 text. After Json.NET serialization,
the creator normalizes escaped newline text before writing `json.log` with a UTF-8
`StreamWriter` configured without a BOM.

### 2.1 Exact log -> JSON model bindings

The current body contains 30 file bindings. The recorder-relevant subset is:

| Source file | JSON model target |
|---|---|
| `DDR.log` | `Gts.Ddr.Data` |
| `ADUDDR.log` | `Gts.AduDdr.Data` |
| `OperationFFD.log` | `Gts.PcsFfd.Data` |
| `LCSOperationFFD.log` | `Gts.LcsFfd.Data` |
| **`TSS3OperationFFD.log`** | **`Gts.Tss3Ffd.Data`** |
| `ADSOperationFFD.log` | `Gts.AdsFfd.Data` |
| `ADSOperationFFD_Eng.log` | `Gts.AdsEng.Data` |
| `ADUOperationFFD.log` | `Gts.AduFfd.Data` |
| **`ImageFFD.log`** | **`Gts.PcsImg.Data`** |
| `PVMImageFFD.log` | `Gts.PvmImg.Data` |
| `ADSImageFFD.log` | `Gts.AdsImg.Data` |
| `RCImageFFD.log` | `Gts.RcImg.Data` |
| `DMCImageFFD.log` | `Gts.DmcImg.Data` |
| `AbsoluteTimeStamp.log` | `Gts.AbsoluteTime.Data` |

The remaining bindings carry VIN, trip/odometer metadata and Airbag/ADU/CSP/PCS/FCM
maker/part/software/serial identity. The generated artifact retains all 30 exact bindings.

This is stronger than a string census: the extractor requires each filename to flow through
`ReadLogFile` and then into the corresponding model setter.

## 3. Outer container: ordinary ZIP

`GTSPlusArchiver.ZipFile::CompressFileToFile` is not a proprietary compressor. It opens a
new `System.IO.Compression.ZipArchive` in create mode and calls
`CreateEntryFromFile(source, Path.GetFileName(source), level)`.

`CreateVdasFile` passes literal compression argument **6**. Toyota's
`CompressionLevelConversion` only special-cases `0 -> enum 2` and `1 -> enum 1`; every
other value, including 6, maps to enum **0 = `CompressionLevel.Optimal`**. Therefore a
VDAS produced by this path is simply:

```text
<name>.vdas          # standard ZIP bytes
└── json.log         # UTF-8 JSON
```

No Toyota executable, secret, password, encryption key or custom decompressor is required
to inspect the file.

## 4. VDAS -> CSV

`ConvertVdastoCsvFile` performs the inverse host path:

1. `ZipFile::DecompressFileToFile(vdas, ecu_data_folder)`;
2. read extracted `json.log` as UTF-8;
3. `MakeImgOpeDdrCsvData` converts the JSON-shaped text to Toyota's CSV presentation;
4. `CalculateImgOpeDdrHash` calls native
   `GTSPlusFileCryptographic.dll!CalculateImgOpeDdrHash` and appends the returned hash text;
5. write `{vdas_stem}.csv` as UTF-8.

The CSV is therefore a presentation/export derivative. **Preserve the original `.vdas` and
`json.log`** for reverse engineering.

## 5. Relationship to TSE/GTSE and PCS Data Viewer

The three host layers now form two parallel persistence paths:

```text
FRC_P5 AB/EB Operation/Image FFD acquisition
                 |
          per-feature *.log files
             /         \
            /           \
       TSE saved data    VDAS builder
            |               |
       TSE/GTSE path       json.log
            |               |
 PCS Data Viewer decoder   .vdas ZIP
```

For our TSS3 work, VDAS has an important practical advantage over **GTSE**. Current
`TSEConverter.exe.config` deliberately skips `RecordOnBehavior共通`,
`PCS時系列作動時FFD`, and `PCS画像FFD` while producing GTSE. VDAS creation, by contrast,
explicitly ingests `TSS3OperationFFD.log` and `ImageFFD.log`.

That does **not** make VDAS a replacement for a raw TSE when validating the current TSE FAT
and list traversal. It does make VDAS a potentially simpler source of the actual PCS
Operation/Image recorder payloads we want to correlate to CAN.

## 6. Clean inspection CLI

The unified tooling reads VDAS with Python's standard ZIP/JSON libraries only:

```bash
tools/gts vdas capture.vdas
tools/gts vdas capture.vdas --json
tools/gts vdas capture.vdas --path Gts.Tss3Ffd.Data
tools/gts vdas capture.vdas --path Gts.PcsImg.Data
```

The default view reports archive entries, format version, and which recorder payload
sections are populated. `--path` is case-insensitive and can return any dotted JSON field.

## 7. Evidence boundary and next specimen

The pinned Toyota distribution and repository corpus contain no `.vdas` sample. A public
GTS+ diagnostic discussion independently identifies `xxx.vdas` as files used by the
**GTS+ PCS Vehicle Data Analysis System**, but the indexed post does not expose a
reusable file specimen. Public exact searches for `TSS3OperationFFD.log` and the VDAS
payload names also returned no downloadable specimen during this pass.

So the code-analysis boundary is closed, but real population is still empirical: we need
one actual TSS3 VDAS (or the source `TSS3OperationFFD.log` / `ImageFFD.log`) to see the
concrete log text produced by a vehicle session. When available, retain the raw VDAS first;
`tools/gts vdas` can expose its JSON without invoking GTS+.

Nothing here identifies the ECU-side vehicle-network producer, B6 signer/freshness owner,
or arbitration executor. It is a host persistence/export contract.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-087](../reference/index.md#finding-tms-087)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
