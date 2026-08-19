#!/usr/bin/env python3
"""Join Techstream P5 steering vocabulary to Corolla 8965H1202000 diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TECH = REPO / "data/generated/techstream_v18/priority_steering_ddb_semantics.json"
APP = REPO / "data/generated/techstream_v18/application_interface_correlations.json"
DIAG = REPO / "data/generated/corolla_8965H1202000_application_diagnostics_diff.json"
EVID = REPO / "data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json"
RAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
DEFAULT_OUT = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def did_map(diag: dict) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for row in diag["readable_dids"]["corolla_h_rdbi_output_audit"]["producers"]:
        for did in row["dids"]:
            out[int(did, 16)] = {
                "callback": row["callback"],
                "classification": row["classification"],
                "declared_length": row["declared_length"],
                "max_write_extent": row["max_write_extent"],
            }
    return out


def source(tech: dict, name: str) -> dict:
    return next(x for x in tech["sources"] if x["relative_path"] == name)


def type61_ids(src: dict) -> set[int]:
    return {x["fields"]["data_id_u16"] for x in src["sections"]["61"]["records"]}


def monitor_rows(src: dict, h_dids: dict[int, dict]) -> list[dict]:
    rows = []
    for rec in src["sections"]["62"]["records"]:
        raw = bytes.fromhex(rec["raw_hex"])
        primary = struct.unpack_from("<H", raw, 0x36)[0]
        alternate = struct.unpack_from("<H", raw, 0x38)[0]
        h = h_dids.get(primary)
        if h is None:
            continue
        rows.append({
            "monitor_key": rec["fields"]["monitor_key_u16"],
            "name": rec["fields"].get("resolved_name"),
            "primary_data_id": f"0x{primary:04X}",
            "alternate_data_id": f"0x{alternate:04X}" if alternate else None,
            "h_callback": h["callback"],
            "h_callback_classification": h["classification"],
            "h_declared_length": h["declared_length"],
            "h_max_write_extent": h["max_write_extent"],
            "ddb_record_index": rec["record_index"],
            "ddb_record_sha256": sha(raw),
        })
    return rows


def get_func(evid: dict, entry: int) -> dict:
    target = f"0x{entry:08X}"
    return next(x for x in evid["functions"] if x["entry"] == target)


def require(text: str, *needles: str) -> bool:
    return all(n in text for n in needles)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    tech, app, diag, evid = map(load, (TECH, APP, DIAG, EVID))
    h_dids = did_map(diag)
    emps = source(tech, "NA/DB/EMPS_P5.ddb")
    emps2 = source(tech, "NA/DB/EMPS2_P5.ddb")
    emps_ids, emps2_ids = type61_ids(emps), type61_ids(emps2)
    emps_rows = monitor_rows(emps, h_dids)
    emps2_rows = monitor_rows(emps2, h_dids)

    # The type-62 +0x36/+0x38 words behave as the monitor's primary/alternate
    # data-ID pair: apart from the FFFE sentinel, every nonzero +0x36 value and
    # every nonzero +0x38 value resolves in the same DDB's type-61 DataIdForDm
    # table. GetDatMonListP5_DT.dll independently filters monitor exposure via
    # the ECU support-PID/data-ID list. Keep that recovered layout claim separate
    # from the stronger exact target DID callback join below.
    def data_id_field_stats(src: dict) -> dict:
        ids = type61_ids(src)
        a, b = [], []
        for rec in src["sections"]["62"]["records"]:
            raw = bytes.fromhex(rec["raw_hex"])
            a.append(struct.unpack_from("<H", raw, 0x36)[0])
            b.append(struct.unpack_from("<H", raw, 0x38)[0])
        anz = [x for x in a if x]
        bnz = [x for x in b if x]
        return {
            "type62_record_count": len(a),
            "primary_offset": "0x36",
            "alternate_offset": "0x38",
            "primary_nonzero_count": len(anz),
            "primary_resolves_in_type61_or_fffe": sum(x in ids or x == 0xFFFE for x in anz),
            "alternate_nonzero_count": len(bnz),
            "alternate_resolves_in_type61": sum(x in ids for x in bnz),
        }

    m402 = next(x for x in emps_rows if x["monitor_key"] == 402)
    unit402 = app["monitors"]["402"][0]
    f495 = get_func(evid, 0x495A0)["decompiled_c"]
    f568 = get_func(evid, 0x56892)["decompiled_c"]
    f576 = get_func(evid, 0x57692)["decompiled_c"]
    fbb9 = get_func(evid, 0xBB9E8)["decompiled_c"]
    fcd55 = get_func(evid, 0xCD55A)["decompiled_c"]
    fcd5d = get_func(evid, 0xCD5DC)["decompiled_c"]
    fce92 = get_func(evid, 0xCE928)["decompiled_c"]
    fce97 = get_func(evid, 0xCE974)["decompiled_c"]

    command_chain = {
        "techstream": {
            "monitor_key": 402,
            "name": m402["name"],
            "bit_width": unit402["monitor"]["bit_width"],
            "unit": unit402["unit"]["text"],
            "primary_data_id": m402["primary_data_id"],
            "alternate_data_id": m402["alternate_data_id"],
        },
        "corolla_h_rdbi": {
            "did": "0x1C02",
            "callback": "0x000495A0",
            "callback_classification": m402["h_callback_classification"],
            "declared_length": m402["h_declared_length"],
            "source": "0xFEBE65F2",
            "scale_factor": "0xFEBEE8A6",
            "formula_shape": "source * scale / 0x2000 * 100 / 0x100; clamp to +/-20000; emit signed16",
            "formula_recovered": require(f495, "sRamfebe65f2", "uRamfebee8a6", "/ 0x2000", "* 100", "20000", "FUN_0006385c"),
        },
        "target_native_producer_chain": [
            {"entry": "0x00056892", "relation": "FEBEE40A -> FEBE65F2", "recovered": require(f568, "uRamfebe65f2 = uRamfebee40a")},
            {"entry": "0x00057692", "relation": "FEBEE40A -> FEBE65F2 (alternate snapshot bank)", "recovered": require(f576, "uRamfebe65f2 = uRamfebee40a")},
            {"entry": "0x000BB9E8", "relation": "FEBEAC56 -> FEBEE40A", "recovered": require(fbb9, "uRamfebee40a = uRamfebeac56")},
            {"entry": "0x000CE928", "relation": "FEBEC3D2 -> FEBEAC56", "recovered": require(fce92, "uRamfebeac56 = uRamfebec3d2")},
            {"entry": "0x000CD5DC", "relation": "FEBEC3C0 * FEBEAC5A / 0x400 -> FEBEC3D2", "recovered": require(fcd5d, "sRamfebec3d2", "sRamfebec3c0", "uRamfebeac5a", "/ 0x400")},
            {"entry": "0x000CD55A", "relation": "compose and bound FEBEC3C0 from H-local steering terms", "recovered": require(fcd55, "FUN_000c84f2()", "FUN_000c850c()", "*(short *)(iVar3 + 0xbc0)")},
            {"entry": "0x000CE974", "relation": "active steering pipeline calls CD55A -> CD5DC -> CE928 in order", "recovered": fce97.index("FUN_000cd55a();") < fce97.index("FUN_000cd5dc();") < fce97.index("FUN_000ce928();")},
        ],
        "interpretation": (
            "8965H1202000 exposes Techstream EMPS_P5 Command Value Torque through a live "
            "target-native steering-state producer chain even though its configured CAN/SecOC "
            "ingress has no 0x2E4/0x131 records. Monitor 402 therefore names an internal "
            "commanded-torque observable; it must not be equated with one specific external CAN field."
        ),
    }

    modern_angle = []
    for key in range(2069, 2077):
        rec = next(x for x in emps["sections"]["62"]["records"] if x["fields"]["monitor_key_u16"] == key)
        raw = bytes.fromhex(rec["raw_hex"])
        did = struct.unpack_from("<H", raw, 0x36)[0]
        modern_angle.append({
            "monitor_key": key,
            "name": rec["fields"].get("resolved_name"),
            "primary_data_id": f"0x{did:04X}",
            "corolla_h_rdbi_supported": did in h_dids,
        })

    raw = RAW.read_bytes()
    payload = {
        "schema": "corolla-8965H1202000-techstream-correlations-v1",
        "software_id": "8965H1202000",
        "sources": {
            "corolla_codeflash": {"path": str(RAW.relative_to(REPO)), "sha256": sha(raw), "size": len(raw)},
            "techstream_semantics": {"path": str(TECH.relative_to(REPO)), "sha256": sha(TECH.read_bytes())},
            "techstream_application_correlations": {"path": str(APP.relative_to(REPO)), "sha256": sha(APP.read_bytes())},
            "corolla_diagnostics": {"path": str(DIAG.relative_to(REPO)), "sha256": sha(DIAG.read_bytes())},
            "target_native_evidence": {"path": str(EVID.relative_to(REPO)), "sha256": sha(EVID.read_bytes())},
            "na_emps_p5": {"relative_path": emps["relative_path"], "sha256": emps["sha256"]},
            "na_emps2_p5": {"relative_path": emps2["relative_path"], "sha256": emps2["sha256"]},
        },
        "data_id_layout_recovery": {
            "emps_p5": data_id_field_stats(emps),
            "emps2_p5": data_id_field_stats(emps2),
            "host_consumer": "GetDatMonListP5_DT.dll builds enabled/support data-ID lists and calls CheckSupportPid while enumerating CDbDatamonitorP5 records",
            "boundary": "Recovered DDB layout/support-selection semantics; exact ECU-to-DDB selection remains route/category dependent rather than inferred from overlap alone.",
        },
        "ddb_overlap": {
            "h_readable_did_count": len(h_dids),
            "emps_p5": {
                "type61_data_id_count": len(emps_ids),
                "h_type61_overlap_count": len(set(h_dids) & emps_ids),
                "h_supported_monitor_rows": len(emps_rows),
                "h_supported_monitor_primary_dids": len({x["primary_data_id"] for x in emps_rows}),
                "monitor_rows": emps_rows,
            },
            "emps2_p5": {
                "type61_data_id_count": len(emps2_ids),
                "h_type61_overlap_count": len(set(h_dids) & emps2_ids),
                "h_supported_monitor_rows": len(emps2_rows),
                "h_supported_monitor_primary_dids": len({x["primary_data_id"] for x in emps2_rows}),
                "monitor_rows": emps2_rows,
            },
            "interpretation": (
                "EMPS_P5 has the stronger static DID-vocabulary fit for this H image (124 versus 112 type61 IDs) "
                "and uniquely maps H-supported DID 0x1C02 to Command Value Torque; this is evidence for using "
                "EMPS_P5 vocabulary, not proof that a particular vehicle session selected category 405."
            ),
        },
        "command_value_torque": command_chain,
        "modern_angle_domain": {
            "rows": modern_angle,
            "primary_data_ids": sorted({x["primary_data_id"] for x in modern_angle}),
            "corolla_h_supports_any": any(x["corolla_h_rdbi_supported"] for x in modern_angle),
            "interpretation": "The EMPS_P5 2069..2076 target-lateral/target-steering-angle vocabulary is grouped under DIDs 0x1CEE/0x1CEF; neither DID exists in H RDBI.",
        },
        "static_conclusion": {
            "techstream_corolla_join_previously_missing": True,
            "command_value_torque_exact_did_join": True,
            "command_value_torque_live_internal_pipeline": all(x["recovered"] for x in command_chain["target_native_producer_chain"]),
            "external_can_field_equivalence": False,
            "next_use": "Use the recovered Techstream DID vocabulary as labels/observers for H target-native control-state tracing and live XCP/RDBI correlation, rather than guessing replacement CAN fields from Sienna names.",
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
