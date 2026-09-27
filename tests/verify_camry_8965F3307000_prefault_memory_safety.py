#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_8965F3307000_prefault_memory_safety.json"
BUILD = ROOT / "tools/targets/camry/builders/build_camry_8965F3307000_prefault_memory_safety.py"

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

art = json.loads(ART.read_text())

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "prefault.json"
    proc = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out)],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT)},
        capture_output=True, text=True, check=False,
    )
    check("builder succeeds", proc.returncode == 0, proc.stderr[-300:])
    check("artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

active = art["active_rscfd_configuration"]
check(
    "application GCFG provenance is startup-bound",
    active["application_chain"] == ["0x000666BC","0x0007A132","0x00079DFA","0x00083F3E","0x00084652","0x00084570","0xFFD20084"]
    and active["application_gcfg"] == "0xFFFF0020"
    and active["bootloader_gcfg"] == "0xFFFF0000",
)

rx = art["rscfd_oversized_fd"]
check("exact GCFG", rx["gcfg"] == "0xFFFF0020" and rx["manual_decode"] == {"CMPOC":1,"DCE":0,"DRE":0})
check("standard FD DLC decode", rx["dlc_table"] == [0,1,2,3,4,5,6,7,8,12,16,20,24,32,48,64])
check("RFIFO1 stale-byte geometry", rx["rfifo1"] == {"max_reported_bytes":64,"max_stale_bytes":32,"payload_words":8,"physical_bytes":32})
check("diagnostic CFIFO stale-byte geometry", rx["diagnostic_cfifo"] == {"max_reported_bytes":64,"max_stale_bytes":56,"payload_words":2,"physical_bytes":8})

route = art["acceptance_routing"]
check("diagnostic CFIFO route", [(x["rule"],x["can_id"],x["gaflp1"]) for x in route["diagnostic_rules"]] == [(43,"0x7A1","0x00002000"),(44,"0x777","0x00002000"),(45,"0x7A0","0x00002000")])
check("XCP RFIFO1 route", route["xcp_rule"] == {"can_id":"0x1FDC0002","gaflp1":"0x00000002","raw_gaflid":"0x9FDC0002","rule":46})

norm = art["fd_length_normalization"]
check(
    "FD length normalization covers full RX domain",
    len(norm["length_to_dlc"]) == 65
    and len(norm["rounded_copy_bytes"]) == 65
    and norm["max_copy_bytes"] == norm["local_buffer_bytes"] == 64
    and norm["rounded_copy_bytes"][64] == 64,
)

sel = art["callback_selector_provenance"]
check(
    "RX callback mask is fixed per acceptance label",
    sel["mask_count"] == 47
    and sel["masks"][:43] == [1] * 43
    and sel["masks"][43:46] == [4,4,4]
    and sel["masks"][46] == 32,
)
check(
    "six-way callback vector is fixed CodeFlash",
    sel["callback_vector"] == ["0x000810F2","0x00081072","0x00081200","0x00081072","0x00081072","0x00081072"],
)

cl = art["consumer_closure"]
check("COM cap closes RFIFO phantom tail", cl["class0_com"]["pdu_count"] == 48 and cl["class0_com"]["max_configured_length"] == 32)
check("XCP cap closes phantom tail", cl["xcp"]["staging_cap"] == 8)
check(
    "transport record indices are fixed configuration",
    art["transport_state_provenance"]["state_indices"] == [0,2]
    and art["transport_state_provenance"]["state_slot_count"] == 3,
)
check(
    "route-manager indices are fixed 0..4",
    art["route_manager_provenance"]["state_indices"] == [0,1,2,3,4]
    and art["route_manager_provenance"]["route_byte_state_base"] == "0xFEBE3E94",
)
check(
    "software queue backing range exact",
    art["software_queue"]["base"] == "0xFEBE4038"
    and art["software_queue"]["end_inclusive"] == "0xFEBE48D7"
    and art["software_queue"]["capacity_words"] == 0x228
    and art["software_queue"]["fd_record_words_for_len64"] == 19,
)

cs = art["computed_store_audit"]
check(
    "critical-cell candidate denominator",
    cs["whole_image_critical_candidate_rows"] == 62
    and cs["critical_cells"] == [
        "0xFEBE3DF0","0xFEBE3DF1","0xFEBE3DF2","0xFEBE3DF3","0xFEBE3DF4","0xFEBE3DF5",
        "0xFEBE5628","0xFEBF0FD0","0xFEBF117C","0xFEBF1180","0xFEBF1194","0xFEBF1198",
        "0xFEBF131C","0xFEBF1320","0xFEBF1324","0xFEBF6B04",
    ],
)
check("critical range intersection is exactly 8E7BA", cs["prefault_critical_intersection_functions"] == ["0x0008E7BA"])
check("no known-range store overlaps saved-context stack", all(x["known_range_store_count"] == 0 for x in cs["stack_ranges"]))
check("communication channel dimensions forbid index2 guard hit", cs["communication_dimensions"] == {"DAT_2183C":1,"DAT_2183D":0,"DAT_21864":2,"DAT_21865":1,"DAT_21BE1":1})
check("route-slot writers remain above guard", cs["route_slot_writer_range"] == {"base":"0xFEBE3E80","max_if_slot_is_full_u8":"0xFEBE407E"})
check("RSCFD pointer row is MMIO-only", len(cs["rscfd_pointer_row"]) == 28 and all(x.startswith("0xFFD2") for x in cs["rscfd_pointer_row"]))

buffers = art["dcm_copy"]["buffers"]
check("DCM destinations fixed to three 0x100 buffers", [(x["route"],x["capacity"],x["start"]) for x in buffers] == [(2,"0x100","0xFEBE5651"),(3,"0x100","0xFEBE5751"),(4,"0x100","0xFEBE5851")])

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
