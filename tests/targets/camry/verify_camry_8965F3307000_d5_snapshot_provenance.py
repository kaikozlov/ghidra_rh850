#!/usr/bin/env python3
"""Verify exact-F33 D5/snapshot/group-input provenance closure (VAR-073)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
ART = REPO / "data/generated/camry_8965F3307000_d5_snapshot_provenance.json"
BUILD = REPO / "tools/targets/camry/builders/build_camry_8965F3307000_d5_snapshot_provenance.py"

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
    "serial-sensor staging has four scaled fields",
    len(edges["0x00050bbc"]) == 18
    and sorted(st["scaled_cells_0x50bbc"]) == ["0xFEBE824C", "0xFEBE824E", "0xFEBE8250", "0xFEBE8252"],
)


rp = art["ring_producers"]
check(
    "no runtime application-code producer posts ring/FIFO payloads",
    rp["application_code_writers"] == ["0x0005fa3a", "0x0005fa84", "0x00060aa8"]
    and rp["runtime_application_producers"] == [],
)

tables = art["serial_sensor_records"]["config_tables"]
check(
    "firmware config tables exact",
    tables["chan_fifo_ptrs_0x313fc"] == ["0xFEEF8050", "0xFEEF8078"]
    and tables["chan_fifo_len_0x31411"] == [20, 20]
    and tables["desc_channel_0x31676"] == ["0x02", "0x0A"]
    and tables["sensor_type_0x31678"] == ["0x00", "0x11"],
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


print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
