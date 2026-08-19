#!/usr/bin/env python3
"""Verify the 8965H1202000 FD/control-interface comparison."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
EVIDENCE = REPO / "data/generated/corolla_8965H1202000_fd_control_decompiler_evidence.json"
REFS = REPO / "data/generated/corolla_8965H1202000_fd_control_reference_census.json"
TOOL = REPO / "tools/build_corolla_h_fd_control_interface.py"
passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "fd.json"
    subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO, check=True,
                   stdout=subprocess.DEVNULL)
    check("tracked FD/control report regenerates exactly", out.read_bytes() == ART.read_bytes())

d = json.loads(ART.read_text())
print("\n== FD receive generation ==")
fd = d["fd_receive_generation"]
check("Sienna FD Rx set is 025/090/D7", [x["can_id"] for x in fd["sienna_fd_rx"]] == ["0x025", "0x090", "0x0D7"])
check("H FD Rx set adds only B6", [x["can_id"] for x in fd["corolla_h_fd_rx"]] == ["0x025", "0x090", "0x0D7", "0x0B6"])
check("025 is explicitly classified as shared rather than H replacement",
      fd["shared_0x025_boundary"]["classification"] == "shared-preexisting-fd-interface-not-h-replacement")
check("025 unpacker/producer/4A3 packer all have unique complete-shape transfers",
      len(fd["shared_0x025_boundary"]["unique_instruction_shape_pairs"]) == 3)
check("H 025 signed12 field is still mirrored into 4A3 B1/B2",
      fd["shared_0x025_boundary"]["corolla_h_signed12_signal_184"]["directly_repacked_to_can_0x4A3_bytes"] == [1, 2])

print("\n== secured FD B6 field roles ==")
b6 = d["secured_fd_0x0b6"]
check("B6 has 16 configured IDs but 12 scalar extracts",
      (len(b6["configured_signal_ids"]), len(b6["scalar_extracted_signal_ids"])) == (16, 12))
check("B6 configured non-scalar IDs are 252/253/266/267",
      b6["configured_without_recovered_scalar_extract"] == [252, 253, 266, 267])
by = {row["signal_id"]: row for row in b6["fields"]}
check("B6 signal255 is signed16 at wire byte4", by[255]["signed"] and by[255]["bit_length"] == 16 and by[255]["wire_byte"] == 4)
check("B6 signed16 field is staged-only under direct-xref census",
      by[255]["role"] == "signed16-staged-only-direct-xref-negative" and by[255]["direct_consumers"] == [])
check("B6 signals254/259 are also staged-only", by[254]["snapshot_destination"] is None and by[259]["snapshot_destination"] is None)
check("B6 signals256/257 reach snapshots but no recovered runtime consumer",
      all(by[x]["role"] == "snapshot-only-direct-xref-negative" for x in (256, 257)))
check("B6 signal260 selects/ramp-controls mode tables", by[260]["role"] == "mode-table-selector" and "0xC89D2" in by[260]["direct_consumers"])
check("B6 signal261 is a modulo/sequence delta input", by[261]["role"] == "modulo-sequence-delta" and by[261]["direct_consumers"] == ["0xCB246"])
check("B6 8-bit signals262/263 are percentage-scaling inputs", by[262]["role"] == by[263]["role"] == "percentage-scaling")
check("B6 signal264 is a validity/reset gate", by[264]["role"] == "validity-reset-gate")
check("B6 signal265 is validity-gated mode/status", by[265]["role"] == "validity-gated-mode-status")
check("active B6 consumers have target-native CEDAE paths where expected",
      all(by[x]["paths_from_0xCEDAE"][next(iter(by[x]["paths_from_0xCEDAE"]))] is not None for x in (258, 261, 262, 263, 264, 265)))

print("\n== Sienna-shaped steering-branch corrections ==")
corr = d["sienna_shaped_branch_corrections"]
check("AE20 is classified as internal-fed monitor/status branch", "monitor/status" in corr["old_2e4_monitor_branch"]["classification"])
clamp = corr["retained_torque_clamp_branch"]
check("retained H clamp input is AE12", clamp["input"] == "0xFEBEAE12")
check("H clamp staging source is F166", clamp["upstream_staging"] == "0xFEBEF166")
check("both recovered direct writers zero the clamp staging cell", len(clamp["direct_writer_census"]) == 2 and all("writes zero" in x for x in clamp["direct_writer_census"]))
check("clamp branch is bounded as zero-source retained framework", "zero source" in clamp["classification"])

print("\n== FD030 transmit generation ==")
tx = d["fd_0x030_transmit"]
check("H Tx replaces 260/262 with FD030", tx["sienna_tx_ids"][:2] == ["0x260", "0x262"] and tx["corolla_h_tx_ids"][0] == "0x030")
check("FD030 is 32-byte cycle/tick 2", tx["pdu0_descriptor"] == {"cycle_or_timeout": 2, "flags": 3, "length": 32})
check("FD030 owns configured signal IDs 0..36", tx["configured_signal_ids"] == list(range(37)))
check("packer directly writes only signals 0..34", tx["direct_packer_signal_ids"] == list(range(35)))
check("configured signals35/36 have no recovered direct pack call", tx["configured_without_recovered_direct_pack_call"] == [35, 36])
check("signal9 is exact first-seven-byte additive field plus 0x38",
      tx["checksum_like_signal_9"]["formula"] == "sum(payload_bytes_0_through_6) + 0x38, low byte")
classes = {row["writer_class"] for row in tx["fields"]}
check("FD030 writer census distinguishes runtime/default/constant-zero/computed fields",
      {"runtime-produced", "default-init-only-direct-writer-census", "runtime-constant-zero-direct-writer-census", "computed-first-seven-byte-additive-field-plus-0x38"} <= classes)

print("\n== compact evidence binding ==")
e = json.loads(EVIDENCE.read_text()); r = json.loads(REFS.read_text())
check("FD/control evidence is exact H image-bound", e["software_id"] == "8965H1202000" and e["image"]["sha256"] == d["images"]["corolla_h_sha256"])
check("compact function evidence contains 56 target-native functions", e["function_count"] == 56)
check("direct-reference census records its computed-pointer boundary", "computed-pointer" in r["evidence_boundary"])
check("reference census covers at least 70 explicit terms", len(r["terms"]) >= 70)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
