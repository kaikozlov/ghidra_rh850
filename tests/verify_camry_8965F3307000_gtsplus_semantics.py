#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json"
EVID = REPO / "data/generated/camry_8965F3307000_gtsplus_decompiler_evidence.json"
IMAGE = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
RAM = REPO / "targets/camry-2026/raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"

p = f = 0
oracle = "generated_self_check"


def check(name: str, cond: bool, detail: str = "") -> None:
    global p, f
    ok = bool(cond)
    p += ok
    f += not ok
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


a = json.loads(ART.read_text())
e = json.loads(EVID.read_text())
img = IMAGE.read_bytes()
ram = RAM.read_bytes()

check("artifact schema/target", a["schema"] == "gtsplus-2026-camry-8965f3307000-emps-semantics-v1" and a["target"]["software_id"] == "8965F3307000")
check("exact F33 image hash", len(img) == 0x100000 and sha(IMAGE) == a["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
check("RDBI table geometry", a["target"]["rdbi_table_offset"] == "0x02928C" and a["target"]["rdbi_record_count"] == 241)
check("current master binds new Camry-HV types to EMPS_P5", a["current_master_join"]["category"] == {"category_id": 405, "database": "EMPS_P5.ddb", "ecu_name": "EMPS", "generation": 20} and [x["vehicle_type"] for x in a["current_master_join"]["new_camry_vehicle_types_using_emps_p5"]] == [12704, 12862, 12984])
check("GTS+ expands type62 222x64 -> 230x80", a["emps_p5_schema_delta"]["v18_type62"] == {"record_count": 222, "record_size": 64} and a["emps_p5_schema_delta"]["gtsplus_type62"] == {"record_count": 230, "record_size": 80})
check("current mirrored datamon tables named", [(x["table_id"], x["class_name"]) for x in a["emps_p5_schema_delta"]["mirrored_current_tables"]] == [(151, "CDbDataIdForRobTable"), (153, "CDbBehaviorDataRecordP5Table"), (156, "CDbDataIdForDmTable"), (157, "CDbDatamonitorP5Table")])
check("type157 is exact 214-key subset", a["emps_p5_schema_delta"]["type157_subset_of_type62"]["common_key_count"] == 214 and a["emps_p5_schema_delta"]["type157_subset_of_type62"]["type157_key_count"] == 214 and a["emps_p5_schema_delta"]["type157_subset_of_type62"]["type62_key_count"] == 230)
check("current-only monitor keys exact", [x["monitor_key"] for x in a["emps_p5_schema_delta"]["current_only_monitor_rows"]] == [223, 224, 225, 226, 227, 228, 410, 1413])
check("new behavior code exact", [(x["signature"], x["name"]) for x in a["emps_p5_schema_delta"]["current_only_behavior_codes"]] == [("X2436", "Beta Cooperative Control Transmission Counter Malfunction")])
check("P5 DTC table semantic set unchanged", a["emps_p5_schema_delta"]["type65_dtc_delta"].startswith("none; all 166"))
check("121/241 F33 DIDs current-named", a["f33_rdbi_join"]["f33_total_data_ids"] == 241 and a["f33_rdbi_join"]["gtsplus_named_f33_data_ids"] == 121)

named = {x["data_id"]: x for x in a["f33_rdbi_join"]["named_data_ids"]}
expected = {
    "0x1035": (2, "0x0004DB70", "Steering Wheel Torque"),
    "0x1036": (2, "0x0004DBBC", "Steering Angle Velocity"),
    "0x1037": (2, "0x0004DBF8", "Steering Angle"),
    "0x1151": (2, "0x0004E394", "Motor Actual Current (Q Axis)"),
    "0x1152": (2, "0x0004E3D0", "Command Value Current (Q Axis)"),
    "0x1185": (2, "0x0004E5A8", "CAN Vehicle Speed (SP1)"),
    "0x1C02": (2, "0x0004E7D6", "Command Value Torque"),
    "0x1C03": (2, "0x0004E81E", "Control State Information"),
}
check("high-value current names join exact F33 callbacks", all(did in named and named[did]["payload_size"] == size and named[did]["callback"] == cb and named[did]["signals"][0]["name"] == name for did, (size, cb, name) in expected.items()))
check("Target Lateral ID DIDs are absent from exact F33", "0x1CEE" not in named and "0x1CEF" not in named)
check("only current-only F33 additions are ASIC upper words", [(x["monitor_key"], x["name"]) for x in a["f33_rdbi_join"]["direct_current_improvements_on_f33_supported_dids"]] == [(410, "ASIC State Information 2"), (1413, "ASIC State Information 2 (System 2)")])

# Verify exact table records independently of the generated artifact.
def rdbi(did: int):
    for i in range(241):
        off = 0x2928C + i * 16
        rd, size, cb, aux, selector = struct.unpack_from("<HHIII", img, off)
        if rd == did:
            return off, size, cb, aux, selector
    return None

check("F33 DID 1C05 record", rdbi(0x1C05) == (0x29A6C, 8, 0x4E848, 0, 0), str(rdbi(0x1C05)))
check("F33 DID 1C0C record", rdbi(0x1C0C) == (0x29ABC, 8, 0x4E848, 0, 1), str(rdbi(0x1C0C)))
check("ASIC split names/bits exact", [(x["data_id"], x["name"], x["bit_range"], x["f33_selector"]) for x in a["asic_state_join"]["gtsplus_rows"]] == [("0x1C05", "ASIC State Information", [0, 31], 0), ("0x1C05", "ASIC State Information 2", [32, 63], 0), ("0x1C0C", "ASIC State Information (System 2)", [0, 31], 1), ("0x1C0C", "ASIC State Information 2 (System 2)", [32, 63], 1)])
check("F33 callback evidence hash-bound", a["asic_state_join"]["f33_callback_evidence"]["sha256"] == sha(EVID) and e["callback"]["entry"] == "0x0004E848" and e["callback"]["body_sha256"] == hashlib.sha256(img[0x4E848:0x4E848+34]).hexdigest())
check("F33 callback resolves exact LocalRAM words", e["callback"]["gp_value_from_exact_f33_runtime_model"] == "0xFEBEB800" and e["callback"]["resolved_sources"] == ["0xFEBE8298", "0xFEBE829C"] and {x["to_addr"].upper() for x in e["callback"]["data_references"]} >= {"0XFEBE8298", "0XFEBE829C"} and "param_1 + 4" in e["callback"]["decompiled_c"])
check("tracked handoff snapshot exact", ram[0x8298:0x82A0].hex() == a["asic_state_join"]["ram_snapshot"]["raw_hex"] == "4000c00000000000" and a["asic_state_join"]["ram_snapshot"]["low_u32_le"] == "0x00C00040" and a["asic_state_join"]["ram_snapshot"]["high_u32_le"] == "0x00000000")
check("bit-level ASIC meaning remains bounded", "not resolved" in a["asic_state_join"]["remaining_unknown"] and "does not establish READY-mode" in a["asic_state_join"]["ram_snapshot"]["state_boundary"])

print(f"\nResults: {p} passed, {f} failed")
raise SystemExit(1 if f else 0)
