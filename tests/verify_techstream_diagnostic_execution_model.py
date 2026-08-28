#!/usr/bin/env python3
"""Verify Techstream's DB -> plugin -> frame -> transport execution spine."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/techstream_v18/diagnostic_execution_model.json"
TOOL = REPO / "tools/techstream/extract_diagnostic_execution_model.py"


def resolve_v18() -> Path:
    base = Path(os.environ.get(
        "TECHSTREAM_UNPACKED_ROOT",
        REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics",
    ))
    for candidate in (base, base / "Techstream"):
        if (candidate / "bin/CommandCommon.dll").is_file():
            return candidate
    return base


def resolve_gts() -> Path:
    base = Path(os.environ.get("GTSPLUS_ROOT", REPO / "software/Techstream/gtsplus"))
    for candidate in (
        base,
        base / "unpacked/gtsplus/Toyota Diagnostics/GTSPlus",
        base / "Toyota Diagnostics/GTSPlus",
    ):
        if (candidate / "bin/CommandCommon.dll").is_file():
            return candidate
    return base


V18 = resolve_v18()
GTS = resolve_gts()
if not (V18 / "NA/DB/Toyota.ddb").is_file() or not (GTS / "NA/DB/Gen/Toyota.ddb").is_file():
    print("[SKIP] pinned Techstream V18 + GTS+ trees are unavailable")
    raise SystemExit(77)

passed = failed = 0
oracle = "instruction_semantics"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}{suffix}")


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "model.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--techstream-root",
            str(V18),
            "--gts-root",
            str(GTS),
            "--out",
            str(out),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    check("execution-model extractor succeeds", proc.returncode == 0, proc.stderr[-400:])
    check("execution-model artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

data = json.loads(ART.read_text())
check("schema is v1", data["schema"] == "techstream-diagnostic-execution-model-v1")

v18 = data["v18"]
gts = data["gtsplus_continuity"]
check(
    "V18 command-plugin population is dominated by Execute-only modules",
    v18["plugin_census"]["dll_count"] == 419
    and v18["plugin_census"]["parsed_pe_count"] == 419
    and v18["plugin_census"]["execute_only_export_count"] == 310
    and v18["plugin_census"]["command_common_importer_count"] == 289,
)
check(
    "GTS+ preserves and expands the same plugin architecture",
    gts["plugin_census"]["dll_count"] == 480
    and gts["plugin_census"]["parsed_pe_count"] == 480
    and gts["plugin_census"]["execute_only_export_count"] == 374
    and gts["plugin_census"]["command_common_importer_count"] == 339,
)
check(
    "GTS+ type-19 DLL role moved to u16 +0x54 but remains logical role 0x19",
    gts["dll_role_schema"]["hybrid_clear_binding"]["dll_role_id"] == 25
    and gts["dll_role_schema"]["hybrid_clear_binding"]["dll_name"] == "DelDiagCodeP4.dll"
    and gts["dll_role_schema"]["role_layout"]["gtsplus_role_anchor"]["bytes"] == "0fb742548945ec837df40075"
    and gts["dll_role_schema"]["role_layout"]["gtsplus_category_anchor"]["bytes"] == "0fb742508945ec837df40075",
)
role_catalog = gts["dll_role_schema"]["role_catalog"]
role19 = next(row for row in role_catalog["roles"] if row["role"] == 25)
check(
    "current GTS+ collapses 6194 category/plugin bindings into 191 logical command roles",
    role_catalog["binding_count"] == 6194
    and role_catalog["role_count"] == 191
    and role19["binding_count"] == 536
    and role19["category_count"] == 536
    and role19["plugins"][0] == {"dll": "DelDiagCodeP4.dll", "binding_count": 424, "surface": "direct_transport"},
)

role_ops = role_catalog
role5_ops = next(row for row in role_ops["roles"] if row["role"] == 0x05)
role6_ops = next(row for row in role_ops["roles"] if row["role"] == 0x06)
role19_ops = next(row for row in role_ops["roles"] if row["role"] == 0x19)
role41_ops = next(row for row in role_ops["roles"] if row["role"] == 0x41)
check(
    "current role-operation census separates direct, delegated, cached, and unresolved shared-runtime edges",
    role_ops["binding_count"] == 6194
    and role_ops["role_count"] == 191
    and role_ops["binding_surface_counts"] == {
        "delegated_transport_v18_proven": 1139,
        "direct_transport": 2643,
        "no_recovered_shared_transport_edge": 1323,
        "plugin_file_missing": 59,
        "support_cache_v18_proven": 790,
        "support_orchestration_unclosed": 240,
    },
)
check(
    "Data Monitor list role 0x05 spans cached P4 support and delegated P5/P6 support discovery",
    role5_ops["binding_surface_counts"] == {
        "delegated_transport_v18_proven": 318,
        "no_recovered_shared_transport_edge": 5,
        "support_cache_v18_proven": 233,
        "support_orchestration_unclosed": 6,
    }
    and role5_ops["plugins"][0]["dll"] == "GetDatMonListP4.dll"
    and role5_ops["plugins"][0]["surface"] == "support_cache_v18_proven"
    and role5_ops["plugins"][1]["dll"] == "GetDatMonListP5_DT.dll"
    and role5_ops["plugins"][1]["surface"] == "delegated_transport_v18_proven",
)
check(
    "Active Test list role 0x06 has the same P4-cache versus P5/P6-delegated split",
    role6_ops["plugins"][0]["dll"] == "GetActTstListP4.dll"
    and role6_ops["plugins"][0]["surface"] == "support_cache_v18_proven"
    and role6_ops["plugins"][1]["dll"] == "GetActTstListP5_DT.dll"
    and role6_ops["plugins"][1]["surface"] == "delegated_transport_v18_proven",
)
check(
    "DTC clear role 0x19 is direct transport for every current binding",
    role19_ops["binding_surface_counts"] == {"direct_transport": 536},
)
check(
    "Data Monitor signal-info role 0x41 has no recovered shared transport edge",
    role41_ops["binding_surface_counts"] == {"no_recovered_shared_transport_edge": 283},
)
current_cc = gts["dll_role_schema"]["command_common_surface"]
check(
    "current GTS+ preserves support-helper exports but not their materialized on-disk bodies",
    current_cc["text_raw_size"] == 4096
    and current_cc["text_virtual_size"] == 868352
    and all(current_cc["helper_exports_present"].values()),
)

plugin_semantics = gts["dll_role_schema"]["plugin_semantics"]
cid = plugin_semantics["role_0x52_generic_cid"]
clear = plugin_semantics["role_0x19_dtc_clear"]
check(
    "current generic role 0x52 EMPS CID route is exact F181 and current plugin identity is pinned",
    cid["plugin"]["sha256"] == "775aa63b75d8918c07a467b5e685ccae7ab3eb6c069ac9c0d5110463dd15f9c2"
    and cid["example_binding"]["category_id"] == 405
    and cid["example_binding"]["dll_role_id"] == 0x52
    and cid["example_binding"]["dll_name"] == "GetCID_SID22_DT.dll"
    and cid["example_frame"]["selector"] == "0xDC"
    and cid["example_frame"]["variables"]["send"]["bytes"] == "22f181"
    and cid["example_frame"]["variables"]["receive_check"]["bytes"] == "62f181",
)
check(
    "current role 0x52 response parser strips four bytes and emits 16-byte CID strings",
    cid["response_model"]["echoed_did_receive_indexes"] == [1, 2]
    and cid["response_model"]["payload_offset"] == 4
    and cid["response_model"]["record_size"] == 16
    and cid["response_model"]["value_capacity_chars"] == 17
    and cid["response_model"]["entry_name_prefix"] == "CID"
    and cid["response_model"]["entry_name_format"] == "%s%d"
    and "byte 3 is skipped" in cid["response_model"]["record_count_source"]
    and "code page 0" in cid["response_model"]["string_conversion"],
)
check(
    "current role 0x52 parser semantics are instruction-pinned",
    cid["anchors"]["response_count_minus_4"]["bytes"] == "ffd38b406883e804898564fcffff"
    and cid["anchors"]["did_echo_index_1"]["bytes"] == "6a018d7858ffd66a018bcf8a5808ffd63a58"
    and cid["anchors"]["payload_copy_from_4"]["bytes"] == "6a008d8de8fcffffffd78d48588d460450ffd3508d8dc0fcffffff153840"
    and cid["anchors"]["chunk_size_16"]["bytes"] == "8b8564fcffffbe100000003bf87d1d578d8dc0fc"
    and cid["anchors"]["cid_literal"]["bytes"] == "4300490044000000"
    and cid["anchors"]["cid_format_literal"]["bytes"] == "25007300250064000000",
)
check(
    "current role 0x19 clear state machine and timer table are exact",
    clear["plugin"]["sha256"] == "8e52d52f860b5fbddcaf178bdbbfcf1e310c1a57e418cee840725f95d18d4e00"
    and clear["timer"]["db_record_class"] == "0x119"
    and clear["timer"]["master_table_type"] == 25
    and clear["timer"]["table"] == "CDbTimerTable"
    and clear["timer"]["record_size"] == 12
    and clear["timer"]["record_count"] == 664
    and clear["timer"]["hybrid_timer_1"] == {
        "category_id": 397,
        "delay_ms": 0,
        "raw": "000000008d01010000000000",
        "timer_id": 1,
        "unknown_dword_08": 0,
    },
)
check(
    "current role 0x19 fallback policy is explicitly bounded by plugin error branches",
    clear["control_flow"]["fallback_error_codes_when_function_gate_set"] == [
        "0x91010009", "0x90020321", "0x90020323", "0xA0040201", "0xC0040001",
        "0xA0040202", "0x90020327", "0x91020320", "0x91020310", "0x91020322",
    ]
    and clear["control_flow"]["fallback_when_function_gate_clear"] == "only 0x91010009 (logged as first-message TIMEOUT)"
    and "FunctionAddress only when bus ID == 0x22" in clear["control_flow"]["fallback_addressing"]
    and "restore/return primary error" in clear["control_flow"]["fallback_c0040101_behavior"]
    and clear["anchors"]["fallback_error_set"]["bytes"].startswith("81fe09000191744c")
    and clear["anchors"]["success_sleep_and_flag"]["bytes"].startswith("85f67534")
    and clear["anchors"]["timer_record_pointer"]["bytes"] == "8b45fc8b4dfc8b510c8950108be55d",
)

check(
    "GTS+ variable references normalize by 0x2710 before the V18-style table lookup",
    gts["dll_role_schema"]["variable_layout"]["gtsplus_namespace_base"] == "0x2710"
    and gts["dll_role_schema"]["variable_layout"]["compare_anchor"]["bytes"] == "0fb74d0881f9102700007e0e0fb75508"
    and gts["dll_role_schema"]["variable_layout"]["subtract_anchor"]["bytes"] == "0fb7550881ea10270000668955088b45",
)
check(
    "current GTS+ Hybrid selectors resolve through the namespace to the same clear bytes",
    gts["dll_role_schema"]["hybrid_clear_primary"]["variables"]["send"] == {"bytes": "04", "id": "0x2743", "normalized_id": "0x33"}
    and gts["dll_role_schema"]["hybrid_clear_primary"]["variables"]["receive_check"] == {"bytes": "44", "id": "0x28F7", "normalized_id": "0x1E7"}
    and gts["dll_role_schema"]["hybrid_clear_fallback"]["variables"]["send"] == {"bytes": "14ffffff", "id": "0x2D28", "normalized_id": "0x618"}
    and gts["dll_role_schema"]["hybrid_clear_fallback"]["variables"]["receive_check"] == {"bytes": "54", "id": "0x28E4", "normalized_id": "0x1D4"},
)

v18_commset = v18["comm_set_table"]
gts_commset = gts["dll_role_schema"]["comm_set_table"]
check(
    "master type 29 is the stable 16-byte CDbComSetTable transport-policy table",
    v18_commset["master_table_type"] == 29
    and v18_commset["record_size"] == 16
    and v18_commset["record_count"] == 12
    and gts_commset["master_table_type"] == 29
    and gts_commset["record_size"] == 16
    and gts_commset["record_count"] == 13,
)
check(
    "CommSet 1 is byte-identical across V18/current and carries receive timeout 1020 plus one retry",
    v18_commset["comm_set_1"] == gts_commset["comm_set_1"]
    and v18_commset["comm_set_1"]["raw"] == "e8030000fc0300000000010000000100"
    and v18_commset["comm_set_1"]["receive_timeout"] == 1020
    and v18_commset["comm_set_1"]["retry_count"] == 1,
)

counts = v18["plugin_census"]["selected_command_common_import_counts"]
check("GetCommFrmInfo is a high-frequency shared primitive", counts["?GetCommFrmInfo@CCommCachePlus@@QAEKGPAUtagCOMMAND_DATA@@PAV?$CCmdList@VCCommFrameData@@@@K@Z"] == 120)
check("shared send/receive primitive is reused broadly", counts["?CommFrameSendReceive@CCommCachePlus@@QAEKPAVCCommFrameData@@G@Z"] == 49)
check("shared function-support gate is reused broadly", counts["?CheckEcuFunc@CFuncInfoCache@@QAEHPAVCDataCtrl@@KGGGPAK@Z"] == 56)
check("shared bus resolver is reused broadly", counts["?GetBusId@CEcuConnectBufferList@@QAEGK@Z"] == 49)

classes = v18["db_record_classes"]
expected_classes = {
    "0x113": (19, "CDbDllTable"),
    "0x11A": (26, "CDbEcuFuncInfoTable"),
    "0x11B": (27, "CDbEcuFuncDetailsTable"),
    "0x119": (25, "CDbTimerTable"),
    "0x112": (18, "CDbFuncCommFrameTable"),
    "0x111": (17, "CDbCommFrameTable"),
    "0x11D": (29, "CDbComSetTable"),
}
for key, (table_type, table_name) in expected_classes.items():
    check(
        f"DB record class {key} is pinned to {table_name}",
        classes[key]["master_table_type"] == table_type and classes[key]["table"] == table_name,
    )

core = v18["core_binaries"]
check(
    "dispatcher pins DLL DB lookup and dynamic plugin loader",
    core["DiagCommCtrlMain.dll"]["sha256"] == "b37720ffee312d81fb1e06f68c6920c5be9898c18d23989e98141d4ede0b096d"
    and core["DiagCommCtrlMain.dll"]["anchors"]["plugin_db_class_0x113"]["bytes"] == "578d4424146a0a5068130100"
    and any(x["name"] == "LoadLibraryA" for x in core["DiagCommCtrlMain.dll"]["imports_selected"])
    and any(x["name"] == "GetProcAddress" for x in core["DiagCommCtrlMain.dll"]["imports_selected"]),
)
check(
    "CommandCommon pins selector/frame/comset DB classes and transport sinks",
    core["CommandCommon.dll"]["sha256"] == "07547a9e47378d37c3ef7d96c2f33f6c62c4151626d98d3f3ff03b7c74909de7"
    and core["CommandCommon.dll"]["anchors"]["func_comm_frame_db_class_0x112"]["bytes"] == "50565168120100008d8fbc00"
    and core["CommandCommon.dll"]["anchors"]["comm_frame_db_class_0x111"]["bytes"] == "50518b4e10681101000081c1"
    and core["CommandCommon.dll"]["anchors"]["comm_set_db_class_0x11d"]["bytes"] == "50518b4e10681d01000081c1"
    and core["CommandCommon.dll"]["anchors"]["comm_set_field_copy"]["bytes"] == "8b4424148b108b0a894e188b108b4a04894e1c8b1033c08a420e894620"
    and core["CommandCommon.dll"]["anchors"]["comm_set_retry_bound"]["bytes"] == "8b5e40894424508b46203bdd8944241c"
    and core["CommandCommon.dll"]["anchors"]["comm_set_receive_timeout_convert"]["bytes"] == "8b5424508d6e1c8bc88b461455518b4e10525051e8c2e80000"
    and core["CommandCommon.dll"]["anchors"]["comm_set_retry_loop"]["bytes"] == "8b4424188b4c241c403bc1894424187f7b"
    and core["KgpDataCtrl.dll"]["anchors"]["comm_set_lookup_key"]["bytes"] == "8b148133c0668b420a8945e8"
    and core["CommandCommon.dll"]["anchors"]["transport_send_sink"]["bytes"] == "8b4e0c52ff1540040b10eb4a"
    and core["CommandCommon.dll"]["anchors"]["transport_receive_sink"]["bytes"] == "ff1550040b108bf881ff2303"
    and core["CommandCommon.dll"]["anchors"]["p5_support_pid_frame_lookup"]["bytes"] == "68ca000000e8deadffff"
    and core["CommandCommon.dll"]["anchors"]["p5_support_pid_transport"]["bytes"] == "e86da6ffff"
    and core["CommandCommon.dll"]["anchors"]["p4_support_bit_frame_lookup"]["bytes"] == "e87feeffff"
    and core["CommandCommon.dll"]["anchors"]["p4_support_bit_transport"]["bytes"] == "e8e4e5ffff"
    and core["CommandCommon.dll"]["anchors"]["enable_data_id_frame_lookup"]["bytes"] == "e87a750000"
    and core["CommandCommon.dll"]["anchors"]["enable_data_id_transport"]["bytes"] == "e837720000"
    and core["CommandCommon.dll"]["anchors"]["enable_rid_frame_lookup"]["bytes"] == "e8de6d0000"
    and core["CommandCommon.dll"]["anchors"]["enable_rid_transport"]["bytes"] == "e8986a0000",
)
check(
    "GetEcuFuncList pins function-info/detail DB record classes",
    core["GetEcuFuncList.dll"]["sha256"] == "93d809bf8f3e11174ab2607a19a2e5dacc514bb9a794c89abc18b0f31193bd6c"
    and core["GetEcuFuncList.dll"]["anchors"]["ecu_func_info_db_class_0x11a"]["bytes"] == "518b4e14681a01000081c1bc"
    and core["GetEcuFuncList.dll"]["anchors"]["ecu_func_detail_db_class_0x11b"]["bytes"] == "8b4e1452681b01000081c1bc",
)

routes = v18["representative_routes"]
hybrid = routes["hybrid_clear"]
check(
    "V18 Hybrid clear DLL binding is role 0x19",
    hybrid["binding"]["category_id"] == 397
    and hybrid["binding"]["dll_role_id"] == 25
    and hybrid["binding"]["dll_name"] == "DelDiagCodeP4.dll",
)
check(
    "Hybrid clear selectors materialize the two observed wire contracts",
    hybrid["primary"]["selector"] == "0x1"
    and hybrid["primary"]["variables"]["send"]["bytes"] == "04"
    and hybrid["primary"]["variables"]["receive_check"]["bytes"] == "44"
    and hybrid["fallback"]["selector"] == "0x102"
    and hybrid["fallback"]["variables"]["send"]["bytes"] == "14ffffff"
    and hybrid["fallback"]["comm_set_metadata"]["receive_timeout"] == 1020
    and hybrid["fallback"]["comm_set_metadata"]["retry_count"] == 1
    and hybrid["fallback"]["variables"]["receive_check"]["bytes"] == "54",
)
brake = routes["brake_current_cid"]
check(
    "Brake CID path traverses role 0x52 and selector 0xDC",
    brake["binding"]["category_id"] == 435
    and brake["binding"]["dll_role_id"] == 82
    and brake["binding"]["dll_name"] == "GetCID_SID22_SAS_DT.dll"
    and brake["frame"]["selector"] == "0xDC",
)
check(
    "Brake selector materializes F181 RDBI send/mask/check bytes",
    brake["frame"]["variables"]["send"]["bytes"] == "22f181"
    and brake["frame"]["variables"]["receive_mask"]["bytes"] == "ffffff"
    and brake["frame"]["variables"]["receive_check"]["bytes"] == "62f181",
)

check(
    "execution spine terminates in KGP_CommFrameCtrl transport",
    v18["execution_spine"][-1] == "CCommCachePlus::CommFrameSendReceive -> KGP_CommFrameCtrl::SendInt* / Receive*",
)
check("scope boundary retains executable plugin semantics", "Specialized parsing" in data["boundary"] and "state machines" in data["boundary"])

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
