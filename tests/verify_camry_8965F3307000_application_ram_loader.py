#!/usr/bin/env python3
"""Verify the exact-F33 non-persistent application-mode RAM-loader assessment."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_8965F3307000_application_ram_loader_assessment.json"
BUILD = ROOT / "tools/build_camry_8965F3307000_application_ram_loader_assessment.py"
IMAGE = ROOT / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
RAW = ROOT / "community/kai/camry-2026/raw-20260826"
RAMREQ = ROOT / "data/variant_ram_exec_requirements.json"

passed = failed = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def find_ldsr_writers(image: bytes, system_register: int, selector: int) -> list[tuple[int,int,bytes]]:
    out=[]
    for off in range(0,len(image)-3,2):
        word=struct.unpack_from("<I",image,off)[0]
        if (((word >> 5) & 0x3F) == 0x3F and
            ((word >> 11) & 0x1F) == system_register and
            ((word >> 16) & 0x7FF) == 0x20 and
            ((word >> 27) & 0x1F) == selector):
            out.append((off,word & 0x1F,image[off:off+4]))
    return out


a = json.loads(ART.read_text())
img = IMAGE.read_bytes()
print("== deterministic target/evidence binding ==")
check("assessment schema exact", a["schema"] == "camry-8965f3307000-application-ram-loader-assessment-v1")
check("exact F33 image pinned", len(img) == 0x100000 and sha(img) == a["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
with tempfile.TemporaryDirectory(prefix="f33-app-loader-") as td:
    out = Path(td) / "assessment.json"
    r = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
    check("builder exits cleanly", r.returncode == 0, r.stderr.strip())
    check("builder reproduces tracked artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())
for name, digest in a["live_runtime_carrier"]["source_files"].items():
    check(f"live evidence hash pinned: {name}", sha((RAW / name).read_bytes()) == digest)

print("\n== live carrier correction ==")
h = a["live_runtime_carrier"]
check("high tail is exact 524-byte retained executable carrier", h["base"] == "0xFEBFF9F0" and h["end_inclusive"] == "0xFEBFFBFB" and h["size"] == 524 and h["retained_sha256"] == "89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c" and h["exact_after_stock_startup"] and h["executed_live"])
check("stock application returned with no Panda TX block delta", h["stock_application_reappeared"] and h["safety_tx_blocked_delta"] == 0)
check("low FEBF0000 carrier is rejected", h["low_febf0000_carrier_rejected"] is True)
check("failed poststartup canary is preserved as a negative probe", "negative/no application reappearance" in h["poststartup_direct_canary_result"])

print("\n== application XCP arbitrary writer ==")
x = a["application_xcp"]
check("packed request descriptors are exact", x["request_can_id"] == "0x7F7" and x["packed_descriptor_hits"]["request"] == ["0x021F50", "0x023398"] and struct.unpack_from("<I", img, 0x21F50)[0] == 0x9FDC0002 and struct.unpack_from("<I", img, 0x23398)[0] == 0x9FDC0002)
check("packed response descriptor is exact", x["response_can_id"] == "0x7F8" and x["packed_descriptor_hits"]["response"] == ["0x021F48"] and struct.unpack_from("<I", img, 0x21F48)[0] == 0x9FE00002)
opmap = img[0x22B24:0x22B24 + 41]
callbacks = [struct.unpack_from("<I", img, 0x22B50 + 4*i)[0] for i in range(18)]
check("GET_SEED/UNLOCK are unconfigured", x["get_seed_configured"] is False and x["unlock_configured"] is False and opmap[0xFF-0xF8] == 0 and opmap[0xFF-0xF7] == 0)
check("SET_MTA maps to exact F33 callback", x["set_mta"] == "0x00082C62" and callbacks[opmap[0xFF-0xF6]] == 0x82C62)
check("DOWNLOAD maps to exact F33 callback", x["download"] == "0x00081FFE" and callbacks[opmap[0xFF-0xF0]] == 0x81FFE)
check("MODIFY_BITS/SHORT_UPLOAD remain configured", x["modify_bits"] == "0x000820C4" and x["short_upload"] == "0x00082B1A" and callbacks[opmap[0xFF-0xEC]] == 0x820C4 and callbacks[opmap[0xFF-0xF4]] == 0x82B1A)
check("software write window exactly covers high tail", x["software_write_window"] == ["0xFEBF7C00", "0xFEBFFBFF"] and struct.unpack_from("<II", img, 0x2B21C) == (0xFEBF7C00, 0xFEBFFBFF) and x["high_tail_fully_inside_write_window"])
check("normal bus1/ELM1 route is only a reachability negative", x["normal_route_live_result"]["status"] == "no_response_timeout" and x["normal_route_live_result"]["tested_bus"] == 1 and x["normal_route_live_result"]["elm327_param"] == 1 and "only" in x["reachability_boundary"])

print("\n== calibration-page shadow is not an execution overlay ==")
cx = a["custom_xcp"]
raw = a["raw_range_evidence"]
check("custom paging selectors carry standard calibration-page roles", cx["semantic_roles"] == {"0xE4":"COPY_CAL_PAGE","0xEA":"GET_CAL_PAGE","0xEB":"SET_CAL_PAGE","0xF3":"BUILD_CHECKSUM"} and cx["calibration_page_state"] == ["0xFEBE5EC4","0xFEBE5EC5"] and cx["page_translator"] == "0x000991D2")
check("startup and XCP copy loops are byte-identical", cx["startup_copy"]["callsite"] == "0x00063822" and cx["startup_copy"]["same_copy_loop_as_xcp"] is True and img[0x636D4:0x636F8] == img[0x993F0:0x99414] and img[0x63822:0x63826] == bytes.fromhex("bfffb2fe"))
check("calibration source/shadow geometry is exact", cx["e4_copy"]["source"] == ["0x00010000","0x00017DEF"] and cx["e4_copy"]["destination"] == ["0xFEBF7C00","0xFEBFF9EF"] and sha(img[0x10000:0x17DF0]) == cx["calibration_shadow_classification"]["source_sha256"] == "675e9f5f360277c6eb27ef73bb021e40861a88d99dd283adb2d7062506d246b6" and cx["residual_tail_starts_exactly_after_e4_copy"])
check("recovered calibration shadow has no code-flow consumer", cx["calibration_shadow_classification"]["recovered_function_entries_in_source_range"] == 0 and cx["calibration_shadow_classification"]["recovered_function_owned_flow_edges_into_source_range"] == 0 and cx["calibration_shadow_classification"]["recovered_flow_edges_into_ram_shadow"] == 0 and cx["calibration_shadow_classification"]["page_state_application_consumers_recovered"] == 0 and cx["calibration_shadow_classification"]["instruction_fetch_or_branch_remap_recovered"] is False)
for name,row in raw.items():
    base=int(row["address"],16); size=row["size"]
    check(f"raw evidence range pinned: {name}", sha(img[base:base+size]) == row["sha256"])

print("\n== ordinary application UDS negatives ==")
u = a["application_uds"]
check("SID 0x3D WriteMemoryByAddress is absent", u["write_memory_by_address_0x3d_configured"] is False and "0x3D" not in u["configured_sids"])
check("SID 0x23 is read-only application RMBA surface", u["read_memory_by_address"] == {"sid":"0x23","callback":"0x000965C0","sessions":[3]})
check("SID 0x2E is DID-bounded rather than arbitrary memory writer", u["write_data_by_identifier"]["callback"] == "0x00095978" and u["write_data_by_identifier"]["arbitrary_memory_writer"] is False)
for sid, key in [(0x34,"request_download"),(0x36,"transfer_data"),(0x37,"request_transfer_exit")]:
    row = u[key]
    check(f"SID 0x{sid:02X} has no application transfer callback and requires session 2", row["callback"] is None and row["sessions"] == [2] and row[[k for k in row if k.endswith("context_recovered")][0]] is False)
check("programming session remains the disruptive handoff", u["programming_session_is_disruptive_handoff"] is True)

print("\n== stock command-5 routine ==")
c = a["stock_command5_routine"]
check("RID 0x100F exact table/callback chain", c["rid"] == "0x100F" and c["routine_table"] == "0x00026918" and c["callback_table"] == "0x000256DC" and c["precondition"] == "0x0008B858" and c["action"] == "0x0008B872" and c["chain"] == ["0x0008B872","0x0006A0AE","0x00069C58","0x00069BD8","0x00089440"])
check("RID 0x100F is fixed-16/private-result not direct SecOC signing API", c["input_length"] == 16 and c["input"] == "0xFEBE5186" and c["output"] == "0xFEBE51B6" and c["output_exposed_to_tester"] is False and c["xcp_can_rewrite_input_or_output"] is False)

print("\n== control-transfer boundary ==")
ct = a["control_transfer_audit"]
check("all recovered computed calls were reviewed with application split", ct["computed_call_sites_reviewed_total"] == 312 and ct["computed_call_sites_reviewed_application"] == 305)
check("only fixed LocalRAM call target is boot FEBF0FD0", ct["only_recovered_computed_call_with_fixed_localram_pointer"] == "0xFEBF0FD0" and ct["fixed_pointer_is_boot_region"] and not ct["fixed_pointer_inside_xcp_write_window"])
check("no raw CodeFlash u32 pointer lands in high tail", ct["raw_codeflash_u32_pointers_into_high_tail"] == [])
dma = ct["fixed_dmac_descriptor_audit"]
check("F33 fixed DMAC descriptor families are target-natively enumerated", dma["fixed_descriptor_paths_closed"] is True and dma["descriptor_apply"] == "0x00060A6A" and dma["recovered_fixed_table_callers"] == ["0x00060462","0x00060C20","0x00061B90","0x000628B2"] and len(dma["tables"]) == 7)
raw_dma_endpoints=[]
for table in dma["tables"]:
    base=int(table["base"],16); count=table["count"]
    check(f"DMAC table {table['base']} raw hash/pointer provenance", sha(img[base:base+count*0x28]) == table["sha256"] and [f"0x{x:06X}" for x in [i for i in range(len(img)-3) if img[i:i+4] == struct.pack('<I',base)]] == table["raw_pointer_hits"])
    for i in range(count):
        off=base+i*0x28
        raw_dma_endpoints.extend(struct.unpack_from("<IIII", img, off+8)[:2])
        raw_dma_endpoints.extend(struct.unpack_from("<II", img, off+0x18))
check("fixed DMAC endpoint census is 88 fields with zero XCP-window hits", len(raw_dma_endpoints) == dma["endpoint_count"] == 88 and dma["endpoints_in_xcp_window"] == [] and all(not (0xFEBF7C00 <= x <= 0xFEBFFBFF) for x in raw_dma_endpoints))
residual=ct["residual_computed_calls"]
check("four residual computed calls resolve below the XCP window", residual["sites"] == ["0x0008863E","0x0008AF7A","0x0008AF88","0x0008AFAA"] and all(int(x,16) < 0xFEBF7C00 for x in residual["callback_cells"]) and residual["all_cells_below_xcp_write_window"] and residual["writers_install_fixed_codeflash_targets"] and residual["bitwise_complement_guards"])
exc=ct["exception_saved_pc_audit"]
check("exception/saved-PC route is confined to lower stacks", exc["exception_return_count"] == len(exc["exception_return_sites"]) == 8 and exc["application_initial_sp"] == "0xFEBE2000" and exc["temporary_isr_stacks"] == ["0xFEBE0800","0xFEBE1000","0xFEBE1800","0xFEBE2800"] and exc["eipc_saved_on_interrupted_stack"] and exc["all_recovered_saved_pc_stacks_below_xcp_write_window"] and exc["direct_flow_edges_into_xcp_write_window"] == 0)
check("only one recovered application DMAC channel programmer remains", dma["recovered_channel_programmers"] == ["0x00060A6A"] and dma["fixed_global_setup"] == "0x00060A10" and dma["recovered_channel_register_accessors"] == ["0x0006091E","0x00060934","0x00060940","0x000609B0","0x00060A6A"])
ctbp=ct["ctbp_writer_census"]
raw_ctbp=find_ldsr_writers(img,20,0)
check("whole-image CTBP writer census closes CALLT-base retargeting", raw_ctbp == [(0x25E,0,bytes.fromhex("e0a72000"))] and ctbp["writers"] == [{"address":"0x0000025E","bytes":"e0a72000","source_register":"r0"}] and ctbp["all_ctbp_writers_census_closed"] and ctbp["only_writer_sets_zero"])
check("negative is explicitly bounded after residual closure", all(word in ct["bounded_negative"].lower() for word in ("computed", "dma", "ctbp", "undiscovered")))
check("no complete non-disruptive loader+exec path claimed", a["implementation_readiness"]["complete_non_disruptive_loader_and_execution_path"] is False and a["implementation_readiness"]["safe_inert_vehicle_poc_built"] is False)
arch = a["architectures"]
check("ranked architecture disposition is complete", [row["rank"] for row in arch] == [1,2,3] and "0x00081FFE" in arch[0]["exact_surface"].values() and arch[0]["lifetime"].startswith("volatile") and "PROGRAMMING" in arch[2]["network_visibility"] and arch[2]["remaining_unknowns"] == [])

print("\n== verified geometry promotion ==")
rows = {row["id"]: row for row in json.loads(RAMREQ.read_text())["variants"]}
camry = rows["camry-2026-8965f3307000-high-tail"]
check("variant table promotes only verified high tail", camry["evidence"] == "dynamic-probe-verified" and camry["retained_application_rwx_base"] == "0xFEBFF9F0" and camry["retained_application_rwx_end_exclusive"] == "0xFEBFFBFC" and camry["retained_application_rwx_size"] == "0x20C")
check("production command5 mailbox remains unassigned", camry["command5_mailbox_address"] is None and camry["command5_mailbox_size"] is None)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
