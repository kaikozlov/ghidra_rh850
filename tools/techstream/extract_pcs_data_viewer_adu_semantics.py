#!/usr/bin/env python3
"""Extract PCS Data Viewer's recovered ADU recorder schema.

The protected viewer ships the ADU/P6 field geometry in
``ADUDetailInfo::.cctor``.  A complete CP-recovered assembly makes that
initializer executable IL again.  This extractor interprets its straight-line
collection construction, joins every row to the English OEM resource name,
and publishes focused longitudinal, PCS, and stop/resume views alongside the
complete table.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
from pathlib import Path
from typing import Any

import dnfile

from extract_pcs_data_viewer_tss3_dictionary import load_culture, sha256_file
from extract_pcs_data_viewer_tss3_managed_semantics import _interpret_collection, _normalize
from techstream_paths import resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_adu_semantics.json"

ADU_DEFINE = "PCSDataViewer.ADUDetailInfo"
ADU_RECORD = "PCSDataViewer.P6DetailBitAssignInfo"
ADU_FIELDS = (
    "DataID",
    "DataSize",
    "SupportDID",
    "BytePosition",
    "BitPosition",
    "BitLength",
    "InvalidValueList",
    "Type",
    "Lsb",
    "Offset",
)


def _select(rows: list[dict[str, Any]], *data_ids: str) -> list[dict[str, Any]]:
    wanted = set(data_ids)
    return [row for row in rows if row["DataID"] in wanted]


def _named_resources(english: dict[str, str | bytes], keys: tuple[str, ...]) -> list[dict[str, str]]:
    out = []
    for key in keys:
        value = english.get(key)
        if not isinstance(value, str):
            raise ValueError(f"missing English resource {key}")
        out.append({"resource_key": key, "name": value})
    return out


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
        bool((off := pe.get_offset_from_rva(rva)) is not None and any(raw[off : off + 16]))
        for rva in body_rvas
    )
    if materialized != len(body_rvas):
        raise ValueError(
            f"assembly is not a complete CP recovery: {materialized}/{len(body_rvas)} method bodies materialized"
        )

    _resource_meta, english = load_culture(en_us)
    table_rva, records = _interpret_collection(
        pe,
        english,
        define_type=ADU_DEFINE,
        record_type=ADU_RECORD,
        record_fields=ADU_FIELDS,
        resource_prefix="ADU_ID_",
    )

    rows: list[dict[str, Any]] = []
    for key, record in records:
        resource_key = f"ADU_ID_{key}"
        name = english.get(resource_key)
        if not isinstance(name, str):
            if key not in {"Trigger", "UserDefinedDTC", "SSRNumber", "TimeStamp"}:
                raise ValueError(f"missing ADU display resource {resource_key}")
            resource_key = None
            name = key
        rows.append(_normalize({"Key": key, "ResourceKey": resource_key, "DataName": name, **record}))

    rows_per_did: dict[str, int] = {}
    for row in rows:
        rows_per_did[row["DataID"]] = rows_per_did.get(row["DataID"], 0) + 1

    longitudinal_id_fields = [
        {"resource_key": key, "name": value}
        for key, value in sorted(english.items())
        if isinstance(value, str)
        and re.search(r"(?:longitudinal|vertical).*\bID\b|\bID\b.*(?:longitudinal|vertical)", value, re.I)
    ]

    return {
        "schema": "gtsplus-pcs-data-viewer-adu-semantics-v1",
        "title": "GTS+ PCS Data Viewer ADU longitudinal, PCS, and stop/resume recorder semantics",
        "sources": {
            "protected_exe": {
                "path": str(protected.relative_to(diagnostics)),
                "size": protected.stat().st_size,
                "sha256": sha256_file(protected),
            },
            "protected_sidecar": {
                "path": str(sidecar.relative_to(diagnostics)),
                "size": sidecar.stat().st_size,
                "sha256": sha256_file(sidecar),
            },
            "english_resources": {
                "path": str(en_us.relative_to(diagnostics)),
                "size": en_us.stat().st_size,
                "sha256": sha256_file(en_us),
            },
            "recovered_analysis_pe_sha256": sha256_file(assembly),
        },
        "recovery_proof": {
            "method_def_count": len(method_rows),
            "method_body_rva_count": len(body_rvas),
            "method_body_materialized_count": materialized,
        },
        "adu": {
            "table_cctor_rva": table_rva,
            "row_count": len(rows),
            "did_count": len(rows_per_did),
            "rows_per_did": dict(sorted(rows_per_did.items())),
            "physical_value_contract": "physical = raw * Lsb + Offset",
            "rows": rows,
        },
        "longitudinal_arbitration": {
            "aggregate_lower_request": _select(rows, "2A02"),
            "aggregate_upper_request": _select(rows, "2A03"),
            "arbitration_results": _select(rows, "1592", "1617", "161D"),
            "pda_oaa_upper_request": _select(rows, "1F03", "1F04", "1F05", "1F06", "1F07"),
            "pda_da_lower_request_resources": _named_resources(
                english,
                (
                    "FFD_TSS3_ID_5B07",
                    "FFD_TSS3_ID_5B08",
                    "FFD_TSS3_ID_5B09",
                    "FFD_TSS3_ID_5B0A",
                    "FFD_TSS3_ID_5B0B",
                    "FFD_TSS3_ID_5B0C",
                    "FFD_TSS3_ID_5B0D",
                    "FFD_TSS3_ID_5B0E",
                    "FFD_TSS3_ID_5B0F",
                    "FFD_TSS3_ID_5B10_1",
                    "FFD_TSS3_ID_5B10_2",
                    "FFD_TSS3_ID_5B10_3",
                    "FFD_TSS3_ID_5B10_4",
                    "FFD_TSS3_ID_5B11",
                ),
            ),
            "interpretation": (
                "Toyota records PDA(OAA) as an upper-limit longitudinal client and PDA(DA) as a lower-limit client. "
                "A simultaneous upper/lower ID pair can therefore represent two cooperating PDA subfunctions."
            ),
            "boundary": (
                "The viewer stores requester/result IDs as raw integers and contains no value-to-client legend for "
                "observed values 13, 17, or 23. Slot, producer, and runtime state remain necessary context."
            ),
        },
        "pcs_pipeline": {
            "scene_and_target_judgment": _select(rows, "1572", "15AC", "15AD", "15AE"),
            "request_and_output": _select(rows, "153C", "153E", "15E5", "15E6", "15EE", "1607"),
            "enable_and_prohibit": _select(rows, "15D0", "15D1", "2C82", "2C83"),
            "arbitration_and_actuation": _select(rows, "1592", "1617", "161D", "1629"),
            "interpretation": (
                "PCS warning judgment, function gating, brake request, longitudinal arbitration, and brake "
                "pressurization are separately observable stages; an alert is not evidence that VMC received or "
                "executed the FRC request."
            ),
        },
        "stop_resume": {
            "hold_and_standstill": _select(rows, "158A", "1591", "15D0", "15D1", "2C82", "2C83"),
            "acc_record": _select(rows, "1770"),
            "pda_da_record": _select(rows, "1882", "1883", "1884", "1886", "1898"),
            "resume_resources": _named_resources(
                english,
                (
                    "DDR_ID_P5_5493",
                    "DDR_ID_P5_5494",
                    "DDR_TRIGGER_ID_P5_33_0",
                    "ADU_TRIGGER_ID_33",
                    "IMGFFD_TSS3_TRIGGER_ID_33_0",
                ),
            ),
            "boundary": (
                "These are recorder observables and event triggers, not a recovered ACC resume state machine or "
                "authorization policy."
            ),
        },
        "request_id_legend_search": {
            "longitudinal_or_vertical_id_field_count": len(longitudinal_id_fields),
            "fields": longitudinal_id_fields,
            "value_to_client_legend_found": False,
            "searched_surface": "all 15,640 English managed string resources plus ADUDetailInfo initialized geometry",
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
    print(
        f"adu_rows={artifact['adu']['row_count']} dids={artifact['adu']['did_count']} "
        f"materialized={artifact['recovery_proof']['method_body_materialized_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
