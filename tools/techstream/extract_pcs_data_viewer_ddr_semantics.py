#!/usr/bin/env python3
"""Extract legacy and Phase-5 DDR field semantics from PCS Data Viewer."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import dnfile

from extract_pcs_data_viewer_tss3_dictionary import load_culture
from extract_pcs_data_viewer_tss3_managed_semantics import (
    Collection,
    _call_names,
    _interpret_collection,
    _method_instructions,
    _normalize,
    sha256_file,
)
from techstream_paths import resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_ddr_semantics.json"
DDR_DEFINE = "PCSDataViewer.DDRDetailInfo"
DDR_RECORD = "PCSDataViewer.DetailBitAssignInfo"
DDR_DECODER = "PCSDataViewer.MemoryAreaCommon"
DDR_FIELDS = (
    "DataName", "ByteCount", "BitCount", "InvalidValueList", "Type",
    "Lsb", "Offset", "Point", "IndexFlg", "RightShiftCount",
)
DDR_DEFAULTS = {
    "DataName": "",
    "ByteCount": 0,
    "BitCount": 0,
    "InvalidValueList": Collection("list", []),
    "Type": "",
    "Lsb": Decimal(0),
    "Offset": Decimal(0),
    "Point": 0,
    "IndexFlg": 0,
    "RightShiftCount": 0,
}


def _table(
    pe: dnfile.dnPE,
    english: dict[str, str | bytes],
    static_field: str,
) -> tuple[int, list[dict[str, Any]]]:
    rva, records = _interpret_collection(
        pe,
        english,
        define_type=DDR_DEFINE,
        record_type=DDR_RECORD,
        record_fields=DDR_FIELDS,
        resource_prefix="DDR_ID_",
        target_static_field=static_field,
        capture_resource_keys=True,
        default_record_values=DDR_DEFAULTS,
    )
    rows = []
    for enum_value, record in records:
        normalized = _normalize(record)
        resource_key = normalized.pop("DataNameResourceKey", None)
        rows.append({"EnumValue": enum_value, "ResourceKey": resource_key, **normalized})
    return rva, rows


def _selected(rows: list[dict[str, Any]], *keys: str) -> list[dict[str, Any]]:
    wanted = set(keys)
    return [row for row in rows if row["ResourceKey"] in wanted]


def extract(assembly: Path, *, gtsplus_root: Path | None = None) -> dict[str, Any]:
    assembly = assembly.expanduser().resolve()
    gts = resolve_gts_root(gtsplus_root)
    diagnostics = gts.parent
    pcs = diagnostics / "PCS Data Viewer"
    protected = pcs / "PCS Data Viewer.exe"
    sidecar = Path(str(protected) + "._")
    en_us = pcs / "en-US/PCS Data Viewer.resources.dll"

    with contextlib.redirect_stderr(io.StringIO()):
        pe = dnfile.dnPE(str(assembly))
    method_rows = list(pe.net.mdtables.MethodDef.rows)
    raw = assembly.read_bytes()
    body_rvas = [int(row.Rva or 0) for row in method_rows if int(row.Rva or 0)]
    materialized = sum(
        bool((offset := pe.get_offset_from_rva(rva)) is not None and any(raw[offset : offset + 16]))
        for rva in body_rvas
    )
    if materialized != len(body_rvas):
        raise ValueError(f"incomplete CP recovery: {materialized}/{len(body_rvas)} method bodies")

    _resource_meta, english = load_culture(en_us)
    table_rva, legacy = _table(pe, english, "DetailInfoList")
    phase5_rva, phase5 = _table(pe, english, "DetailInfoListPhase5")
    if phase5_rva != table_rva:
        raise ValueError("DDR tables unexpectedly use different static constructors")

    get_value_rva, get_value = _method_instructions(pe, DDR_DECODER, "GetValueStr")
    convert_rva, convert = _method_instructions(pe, DDR_DECODER, "ConvertDetailValue")
    get_value_ops = [str(ins.opcode) for ins in get_value]
    get_value_calls = [name for _owner, name in _call_names(pe, get_value)]
    convert_calls = [name for _owner, name in _call_names(pe, convert)]
    if not {"get_ByteCount", "get_BitCount", "get_RightShiftCount"}.issubset(get_value_calls) or not {"and", "shr"}.issubset(get_value_ops):
        raise ValueError("DDR mask/shift decoder shape drift")
    if not {"get_Lsb", "get_Offset", "get_Point", "ConvertValue", "Floor"}.issubset(convert_calls):
        raise ValueError("DDR physical conversion shape drift")

    resume_keys = ("DDR_ID_P5_5493", "DDR_ID_P5_5494")
    resume = _selected(phase5, *resume_keys)
    if [row["ResourceKey"] for row in resume] != list(resume_keys):
        raise ValueError("ACC resume definitions missing or reordered")

    return {
        "schema": "gtsplus-pcs-data-viewer-ddr-semantics-v1",
        "title": "GTS+ PCS Data Viewer legacy and Phase-5 DDR field semantics",
        "sources": {
            "protected_exe": {"path": str(protected.relative_to(diagnostics)), "size": protected.stat().st_size, "sha256": sha256_file(protected)},
            "protected_sidecar": {"path": str(sidecar.relative_to(diagnostics)), "size": sidecar.stat().st_size, "sha256": sha256_file(sidecar)},
            "english_resources": {"path": str(en_us.relative_to(diagnostics)), "size": en_us.stat().st_size, "sha256": sha256_file(en_us)},
            "recovered_analysis_pe_sha256": sha256_file(assembly),
        },
        "recovery_proof": {
            "method_def_count": len(method_rows),
            "method_body_rva_count": len(body_rvas),
            "method_body_materialized_count": materialized,
        },
        "decoder": {
            "table_cctor_rva": table_rva,
            "get_value_str_rva": get_value_rva,
            "convert_detail_value_rva": convert_rva,
            "raw_contract": "read ByteCount bytes; decoded_raw = (raw & BitCount) >> RightShiftCount",
            "physical_contract": "physical = decoded_raw * Lsb + Offset; render with Point decimal places",
            "field_note": "BitCount is the integer bit mask despite its name; RightShiftCount aligns the masked value.",
        },
        "legacy": {"row_count": len(legacy), "rows": legacy},
        "phase5": {
            "row_count": len(phase5),
            "resource_backed_row_count": sum(row["ResourceKey"] is not None for row in phase5),
            "rows": phase5,
        },
        "stop_resume": {
            "acc_resume_trigger_signal": resume,
            "nearby_phase5_fields": _selected(
                phase5,
                "DDR_ID_P5_5489", "DDR_ID_P5_5490", "DDR_ID_P5_5491", "DDR_ID_P5_5492",
                "DDR_ID_P5_5493", "DDR_ID_P5_5494", "DDR_ID_P5_5495", "DDR_ID_P5_5496", "DDR_ID_P5_5497",
            ),
            "interpretation": (
                "5493 and 5494 are separate one-bit masks sharing the same display name. The viewer does not "
                "identify either bit as an authorization policy or recover the ACC resume state machine."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assembly", type=Path, required=True, help="CP-recovered PCS Data Viewer.exe")
    parser.add_argument("--gtsplus-root", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = extract(args.assembly, gtsplus_root=args.gtsplus_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")
    print(f"legacy={artifact['legacy']['row_count']} phase5={artifact['phase5']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
