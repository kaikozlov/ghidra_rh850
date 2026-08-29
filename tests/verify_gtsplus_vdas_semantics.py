#!/usr/bin/env python3
"""Verify current GTS+ PCS Vehicle Data Analysis (.vdas) persistence semantics."""
from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_vdas_semantics import build
from vdas import json_path, load_vdas

ART = REPO / "data/generated/gtsplus_2026/vdas_semantics.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    stored = json.loads(ART.read_text(encoding="utf-8"))
    current = build()
    check("artifact regenerates from exact same-release installer plaintext twins", stored == current)
    check("schema", stored["schema"] == "gtsplus-vdas-semantics-v1")

    sources = stored["sources"]
    check(
        "exact current managed assembly identities",
        sources["GTSPlusDiagAdaptMng.dll"] == {
            "size": 57360,
            "sha256": "7a56cc6488ad0f982b3b8ed531d5da0677d04f58c92b4b4ea3d0ac6508f27f9e",
        }
        and sources["GTSPlusArchiver.dll"] == {
            "size": 19472,
            "sha256": "ce3c56ada831ea0b7164435fec8bc47184ea97c16b67469404a163fc1fedd7a2",
        },
    )
    check("current release pinned", sources["installer_recovery"]["gtsplus_version"] == "2026.03.002.02")

    create = stored["create_and_export"]
    check("VDAS filename is VIN/timestamp derived", create["file_naming"]["pattern"] == "{sanitized_vin}_{yyyyMMddHHmmss}.vdas")
    entry = create["json_entry"]
    check("VDAS carries one UTF-8 JSON source file", entry["archive_entry"] == "json.log" and entry["text_encoding"] == "UTF-8 without BOM")
    check("VDAS model format version", entry["format_version"] == "001")
    check("30 exact input-log bindings", len(entry["bindings"]) == 30)
    by_file = {row["file"]: row["json_model_target"] for row in entry["bindings"]}
    check("TSS3 Operation FFD is first-class VDAS payload", by_file["TSS3OperationFFD.log"] == "Tss3Ffd.Data")
    check("PCS Image FFD is first-class VDAS payload", by_file["ImageFFD.log"] == "PcsImg.Data")
    check("ordinary PCS/LCS/ADS/ADU recorder logs retained", all(name in by_file for name in ["OperationFFD.log", "LCSOperationFFD.log", "ADSOperationFFD.log", "ADUOperationFFD.log"]))
    check("DDR and absolute-time logs retained", by_file["DDR.log"] == "Ddr.Data" and by_file["AbsoluteTimeStamp.log"] == "AbsoluteTime.Data")

    archive = stored["archive"]
    check("VDAS outer container is standard ZIP", archive["container"] == "standard ZIP archive" and archive["create_mode"] == "ZipArchiveMode.Create")
    check("VDAS ZIP entry keeps source basename", archive["entry_name_rule"] == "Path.GetFileName(source_file)")
    check("VDAS call's literal level 6 resolves to .NET Optimal", archive["vdas_call_argument"] == 6 and "Optimal" in archive["vdas_effective_compression_level"])
    check("VDAS extraction overwrites the extracted json.log", "ExtractToFile(overwrite=true)" in archive["read_mode"])

    csv = create["csv_export"]
    check("VDAS reverse path is JSON-to-CSV", csv["output_extension"] == ".csv" and "decompress VDAS" in csv["flow"])
    check("CSV integrity text is produced by Toyota file-crypto helper", csv["hash_import"] == "GTSPlusFileCryptographic.dll!CalculateImgOpeDdrHash")

    witnesses = stored["tss3_pcs_witnesses"]
    check("TSS3 witnesses agree with full binding map", witnesses["operation_ffd"] == {"file": "TSS3OperationFFD.log", "json_model_target": "Tss3Ffd.Data"} and witnesses["image_ffd"] == {"file": "ImageFFD.log", "json_model_target": "PcsImg.Data"})
    check("host-only boundary retained", "does not prove" in stored["boundary"])

    with tempfile.TemporaryDirectory(prefix="gts-vdas-fixture-") as td:
        fixture = Path(td) / "fixture.vdas"
        document = {
            "Gts": {
                "FormatVersion": {"Version": "001"},
                "Tss3Ffd": {"Data": "EB11\nEB12"},
                "PcsImg": {"Data": "6001"},
            }
        }
        with zipfile.ZipFile(fixture, "w") as archive:
            archive.writestr("json.log", json.dumps(document).encode("utf-8"))
        decoded = load_vdas(fixture)
        check("clean CLI decoder opens ZIP-backed VDAS without Toyota code", decoded["archive_entries"] == ["json.log"] and decoded["document"] == document)
        check("CLI dotted path exposes TSS3 payload", json_path(decoded["document"], "gts.tss3ffd.data") == "EB11\nEB12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
