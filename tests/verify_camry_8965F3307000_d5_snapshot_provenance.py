#!/usr/bin/env python3
"""Verify exact-F33 D5/snapshot/group-input provenance closure (VAR-073)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_8965F3307000_d5_snapshot_provenance.json"
BUILD = REPO / "tools/build_camry_8965F3307000_d5_snapshot_provenance.py"

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][d5_snapshot_provenance] {name}" + (f" ({detail})" if detail else ""))


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "d5.json"
    p = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True
    )
    check("builder succeeds", p.returncode == 0, p.stderr[-300:])
    check(
        "artifact regenerates byte-exact",
        p.returncode == 0 and out.read_bytes() == ART.read_bytes(),
    )

art = json.loads(ART.read_text())

check(
    "schema/target exact",
    art["schema"] == "camry-8965f3307000-d5-snapshot-provenance-v1"
    and art["target"]["software_id"] == "8965F3307000"
    and art["target"]["corpus_function_count"] == 6065,
)

drv = art["driver"]
check(
    "driver/mirror structure exact",
    drv["periodic_task"] == "0x00058b5e"
    and drv["selector_driver"] == "0x00058b1a"
    and drv["mirrors"] == ["0x0005d12c", "0x0005d5e0", "0x0005d6dc"]
    and drv["selector_values"] == ["0xffc0", "0xff80", "0xff00"],
)

st = art["staging"]
check(
    "staging writer set exact",
    st["writers"] == ["0x00050b6a", "0x00050bbc", "0x00050c38", "0x00058c9a", "0x00059448"],
)
check("0x58c9a is init/marker-only (closes VAR-071 bound)", st["init_marker_only_0x58c9a"] is True)
edges = st["copy_edges"]
check(
    "0x50b6a copies exactly the 12 group-input halfwords",
    len(edges["0x00050b6a"]) == 12
    and all(d.startswith("0xFEBE82") for d, s in edges["0x00050b6a"])
    and all(s.startswith("0xFEBE5E") for d, s in edges["0x00050b6a"]),
)
check(
    "0x50bbc copies 18 torque-sensor halfwords with x4 on exactly four cells",
    len(edges["0x00050bbc"]) == 18
    and sorted(st["scaled_cells_0x50bbc"]) == ["0xFEBE824C", "0xFEBE824E", "0xFEBE8250", "0xFEBE8252"],
)

acq = art["acquisition_source_block"]["writers"]
check(
    "acquisition source-block writer set exact",
    sorted(acq) == ["0x00066824", "0x000668e2", "0x00066932", "0x00098f4c"],
)

gia = art["group_input_api"]
check(
    "group-input ring accessors exact",
    gia["accessors"]["0x00060630"] == {"table": "0xFEEF80A0", "entries": 0x50}
    and gia["accessors"]["0x00060676"] == {"table": "0xFEEF81E0", "entries": 0x1B0}
    and gia["accessors"]["0x000606da"] == {"table": "0xFEEF88A0", "entries": 0x60}
    and gia["accessors"]["0x00060720"] == {"table": "0xFEEF8A20", "entries": 0x1B0},
)

rp = art["ring_producers"]
check(
    "no runtime application-code producer posts ring/FIFO payloads",
    rp["application_code_writers"] == ["0x0005fa3a", "0x0005fa84", "0x00060aa8"]
    and rp["runtime_application_producers"] == [],
)
sfr = rp["sfr_evidence"]
check(
    "channel initializer programs DMAC trigger-select SFRs",
    sfr["0x0006082c"]["named_sfr"] == [
        "DMACTRGSEL0 (DMAC primary/secondary select 0)",
        "DMACTRGSEL1 (DMAC primary/secondary select 1)",
    ],
)
check(
    "same driver family carries ADCG/CSIH1/CRC config",
    any("ADCG0" in n for n in sfr["0x0005fafe"]["named_sfr"])
    and any("CSIH1" in n for n in sfr["0x00061260"]["named_sfr"])
    and any("CRC0" in n for n in sfr["0x000611fa"]["named_sfr"])
    and any("CRC1" in n for n in sfr["0x0006378c"]["named_sfr"]),
)

tables = art["torque_sensor_serial"]["config_tables"]
check(
    "firmware config tables exact",
    tables["chan_fifo_ptrs_0x313fc"] == ["0xFEEF8050", "0xFEEF8078"]
    and tables["chan_fifo_len_0x31411"] == [20, 20]
    and tables["desc_channel_0x31676"] == ["0x02", "0x0A"]
    and tables["sensor_type_0x31678"] == ["0x00", "0x11"],
)

dt = art["driver_torque_chain"]["steps"]
check(
    "driver-torque chain reaches DID 0x1035 from the four-sensor decode",
    any("0x00048684: FEBE7E0C" in s for s in dt)
    and any("0x0005d5e0 mirror: FEBE66A8 = FEBE7E0C" in s for s in dt)
    and any("DID 0x1035" in s for s in dt),
)
cc = art["command_current_chain"]["steps"]
check(
    "command-current chain mirrors FEBE6D84/6D86 into the DID 0x1152 cells",
    any("FEBE6724 = FEBE6D84" in s for s in cc) and any("FEBE6D84 = FEBE6DD6" in s for s in cc),
)
ct = art["command_torque_chain"]["steps"]
check(
    "command-torque terminal is the B6-selected cone via 0xBF33E",
    any("0x0005d5e0 mirror: FEBE6772 = FEBEE40A" in s for s in ct)
    and any("0x000bf33e: FEBEE40A = FEBEAC56" in s for s in ct),
)

guard = art["can_join_guard"]
read_hits = {
    ea: reads
    for ea, hits in guard["hits"].items()
    if (reads := [h for h in hits if h["kind"] == "READ"])
}
check(
    "CAN-join guard: only 0xBF33E READs the control-snapshot region",
    set(guard["hits"]) == {"0x00059448", "0x000bf33e"}
    and set(read_hits) == {"0x000bf33e"}
    and all(h["to"].startswith("0xfebeac") for h in read_hits["0x000bf33e"]),
)

scc = art["single_can_controller"]
check(
    "single-RSCFD hardware fact pinned",
    scc["rscfd0_base"] == "0xFFD20000" and "RSCFDn (n = 0)" in scc["source"],
)
check(
    "closure conclusion present",
    "No generated COM/CAN value" in art["conclusion"],
)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
