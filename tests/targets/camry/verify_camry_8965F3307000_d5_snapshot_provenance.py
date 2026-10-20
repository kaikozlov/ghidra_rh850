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
expected_groups = [
    [f"0x{destination + i * 2:08X}", f"0x{source + i * 2:08X}"]
    for destination, source in (
        (0xFEBE8238, 0xFEBE5EC8), (0xFEBE822C, 0xFEBE5ED4),
        (0xFEBE823E, 0xFEBE5ECE), (0xFEBE8232, 0xFEBE5EDA),
    )
    for i in range(3)
]
check("group-input staging preserves both reference/measured bank permutations",
      sorted(edges["0x00050b6a"]) == sorted(expected_groups))
expected_serial = [
    [f"0xFEBE{dst:04X}", f"0xFEBE{src:04X}"]
    for dst, src in (
        (0x824C, 0x5F12), (0x824E, 0x5F14), (0x8254, 0x5F16),
        (0x8250, 0x5F1C), (0x8252, 0x5F1E), (0x8256, 0x5F20),
        (0x8258, 0x5F18), (0x825A, 0x5F1A), (0x825C, 0x5F22), (0x825E, 0x5F24),
    )
] + [
    [f"0x{0xFEBE8244 + channel + counter * 2:08X}",
     f"0x{0xFEBE5F29 + channel * 4 + counter:08X}"]
    for channel in range(2) for counter in range(4)
]
check("serial staging separates numeric fields, interleaved byte counters and masks",
      sorted(edges["0x00050bbc"]) == sorted(expected_serial))
check("only the four 14-bit serial fields are scaled by four",
      st["scaled_cells_0x50bbc"] == {
          f"0xFEBE{address:04X}": "x4" for address in (0x824C, 0x824E, 0x8250, 0x8252)
      })


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
