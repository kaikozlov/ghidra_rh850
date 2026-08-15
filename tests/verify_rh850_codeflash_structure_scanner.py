#!/usr/bin/env python3
"""Verify the offline RH850 CodeFlash structural triage scanner.

The scanner is candidate-only: every anchor it reports on a future calibration
must be treated as triage, not transfer proof. This suite pins
  - the exact report shape and triage labeling,
  - deterministic anchor counts against the committed Sienna image,
  - negative behavior on truncated, concatenated, and content-free images,
  - the deliberate absence of a per-calibration software-ID offset fallback.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.analyze_rh850_codeflash_structure import analyze  # noqa: E402

cf_path = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
dataflash_path = REPO / "firmware" / "RH850_P1M-E_DataFlash.bin"
cf = cf_path.read_bytes()
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


report = analyze(cf, max_vas=200)
prefilter = report["semantic_resolver_prefilter"]
xcp = report["xcp_command_surface"]
boot = report["boot_trust"]
ram_exec = report["ram_exec_gate"]

print("== report shape and triage labeling ==")
check("schema is pinned", report["schema"] == "rh850-codeflash-structure-triage-v1")
check("top-level classification is triage", report["classification"] == "triage")
check("disclaimer explicitly denies transfer proof", "not transfer proof" in report["disclaimer"])
for section in ("boot_trust", "ram_exec_gate", "xcp_command_surface", "semantic_resolver_prefilter"):
    check(f"{section} self-labels as candidate", report[section]["classification"] == "triage-candidate")
    check(f"{section} carries a candidate-only interpretation", "candidate" in report[section]["interpretation"].lower())

print("\n== Sienna image geometry and identity ==")
check("committed image classifies as bare 1 MiB CodeFlash", report["image"]["geometry"]["classification"] == "bare-codeflash-1m")
check("report binds the committed image SHA-256", report["image"]["sha256"] == hashlib.sha256(cf).hexdigest())
check("no software-ID offset fallback table is emitted", report["image"]["software_id_offsets"] is None)
scanner_source = (REPO / "tools" / "analyze_rh850_codeflash_structure.py").read_text(encoding="utf-8").lower()
check("scanner source contains no software-ID offset table", "software_id_offsets = {" not in scanner_source and "f181" not in scanner_source)

print("\n== deterministic Sienna anchor counts ==")
check("boot trust finds exactly two self-describing CRC descriptors", boot["crc_descriptor_count"] == 2)
check("exactly one descriptor validates the terminal-fixup scheme", boot["terminal_valid_descriptor_count"] == 1)
check("high CRC region starts at the structural 0x18000 anchor",
      any(d["start"] == "0x18000" for d in boot["crc_descriptors"]))
check("boot-validity marker word appears exactly 23 times", boot["validity_marker_word"]["count"] == 23)
check("RAM-exec download-window base immediates present", ram_exec["download_window_base_immediates"]["count"] >= 1)
check("post-link package descriptor pair appears exactly once", ram_exec["package_descriptor_pair_count"] == 1)
check("paired XCP CAN route constants are present",
      xcp["request_can_id_immediates"]["count"] == 2 and xcp["response_can_id_immediates"]["count"] == 1)
check("page-copy window-end and shadow constants are present",
      xcp["page_copy_window_end_immediates"]["count"] == 6 and xcp["page_copy_shadow_base_immediates"]["count"] == 6)
maps = {w["va"]: w for w in xcp["command_map_windows"]}
check("command-map scan includes the recovered seven-entry map at 0x2B3F0", "0x2B3F0" in maps)
if "0x2B3F0" in maps:
    sienna_map = maps["0x2B3F0"]
    check("0x2B3F0 map has the exact recovered selector sequence",
          sienna_map["selectors"] == [f"0x{s:02X}" for s in (0xFB, 0xFA, 0xF5, 0xF3, 0xEB, 0xEA, 0xE4)],
          repr(sienna_map["selectors"]))
    check("0x2B3F0 map callbacks start at the recovered response builder", sienna_map["callbacks"][0] == "0x9729A")
    check("0x2B3F0 map is fully distinct selectors", sienna_map["distinct_selectors"] == 7)
check("command-map scan stays candidate-sized", xcp["command_map_window_count"] <= 32, str(xcp["command_map_window_count"]))
check("prefilter counts are pinned for the committed image",
      prefilter["ld_bu_disp32_halfword_count"] == 3182
      and prefilter["cmov_family_halfword_count"] == 1812
      and prefilter["byte_load_then_cmov_site_count"] == 101,
      f"ld={prefilter['ld_bu_disp32_halfword_count']} cmov={prefilter['cmov_family_halfword_count']} pairs={prefilter['byte_load_then_cmov_site_count']}")
check("known Gate-2 site 0x8E69E is among prefilter pair candidates", "0x8E69E" in prefilter["byte_load_then_cmov_first_vas"])

print("\n== negative fixtures ==")
truncated = analyze(cf[: 0x20000])
check("half image is classified as truncated/foreign", truncated["image"]["geometry"]["classification"] == "truncated-or-foreign")
check("truncated image reports geometry mismatch", truncated["image"]["geometry"]["geometry_matches_bare_codeflash"] is False)
check("truncated image loses the high CRC descriptor anchor", truncated["boot_trust"]["crc_descriptor_count"] < 2)
check("truncated image loses the paired XCP CAN route anchors",
      truncated["xcp_command_surface"]["request_can_id_immediates"]["count"] == 0
      and truncated["xcp_command_surface"]["response_can_id_immediates"]["count"] == 0,
      "route constants past the truncation point must disappear")
check("truncated image loses all but the early page-copy constants",
      truncated["xcp_command_surface"]["page_copy_shadow_base_immediates"]["count"] == 1,
      str(truncated["xcp_command_surface"]["page_copy_shadow_base_immediates"]["count"]))
check("truncated image drops the seven-entry command map", "0x2B3F0" not in {w["va"] for w in truncated["xcp_command_surface"]["command_map_windows"]})

concat_blob = dataflash_path.read_bytes() + cf
concat = analyze(concat_blob)
check("0x108000 dump classifies as DataFlash+CodeFlash concatenation",
      concat["image"]["geometry"]["classification"] == "dataflash-codeflash-concat")
check("concat geometry note explains the 0x8000 VA shift", "0x8000" in concat["image"]["geometry"]["note"])
check("concat report does not claim bare-CodeFlash geometry", concat["image"]["geometry"]["geometry_matches_bare_codeflash"] is False)

zeros = analyze(b"\x00" * (1 << 20))
check("content-free 1 MiB image has correct geometry but zero anchors",
      zeros["image"]["geometry"]["classification"] == "bare-codeflash-1m"
      and zeros["boot_trust"]["crc_descriptor_count"] == 0
      and zeros["boot_trust"]["validity_marker_word"]["count"] == 0
      and zeros["ram_exec_gate"]["download_window_base_immediates"]["count"] == 0
      and zeros["xcp_command_surface"]["request_can_id_immediates"]["count"] == 0
      and zeros["xcp_command_surface"]["command_map_window_count"] == 0
      and zeros["semantic_resolver_prefilter"]["byte_load_then_cmov_site_count"] == 0,
      "scanner output tracks content, not just size")

print("\n== determinism and CLI ==")
check("analysis is deterministic", analyze(cf, max_vas=200) == report)
cli = subprocess.run(
    [sys.executable, str(REPO / "tools" / "analyze_rh850_codeflash_structure.py"), str(cf_path)],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("CLI emits valid JSON report", cli.returncode == 0 and json.loads(cli.stdout)["schema"] == "rh850-codeflash-structure-triage-v1")

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
