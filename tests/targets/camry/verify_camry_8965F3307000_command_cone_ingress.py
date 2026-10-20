#!/usr/bin/env python3
"""Verify exact-F33 command-cone ingress census (pipeline + composition provenance)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.targets.camry.builders.build_camry_8965F3307000_command_cone_ingress import (
    _CODE_SYMBOLS,
    cell_tokens,
    exact_pairs,
)

REPO = REPO_ROOT
ART = REPO / "data/generated/camry_8965F3307000_command_cone_ingress.json"
BUILD = REPO / "tools/targets/camry/builders/build_camry_8965F3307000_command_cone_ingress.py"
PRIOR = REPO / "data/generated/camry_8965F3307000_external_lateral_ingress.json"

passed = failed = 0
code_names = {address: name for name, address in _CODE_SYMBOLS.items()}


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][command_cone] {name}" + (f" ({detail})" if detail else ""))


check("overlapping global views retain their byte offsets",
      cell_tokens("DAT_febe8000 + DAT_febe8000._2_1_", {}) == {0xFEBE8000, 0xFEBE8002})
check("copy edges resolve source and destination subfields",
      exact_pairs(0x58074, {0x58074: {"decompiled_c":
          "DAT_febef0b8._2_1_ = DAT_febe8000._2_1_; "
          "DAT_febef02d = DAT_febe7ff0;"}}) ==
      [(0xFEBE8002, 0xFEBEF0BA), (0xFEBE7FF0, 0xFEBEF02D)])
check("code-symbol aliases resolve the complete GP-relative byte address",
      cell_tokens(f"{code_names[0x3942]}[(int)(puVar7 + 3)]", {"puVar7": 0xFEBEB800}) == {0xFEBEF145}
      and cell_tokens(f"*(short *)({code_names[0x3998]} + (int)puVar7)", {"puVar7": 0xFEBEB800}) == {0xFEBEF198}
      and cell_tokens(f"{code_names[0x3942]}[(int)(puVar7 + -0x2)]", {"puVar7": 0xFEBEB800}) == {0xFEBEF140})
check("unresolved code-symbol base does not invent a copy source",
      cell_tokens(f"{code_names[0x3942]}[(int)(puVar9 + 3)]", {"puVar7": 0xFEBEB800}) == set())
check("named scalar views resolve addresses and byte offsets",
      cell_tokens("sample + sample._2_1_", {}, {"sample": 0xFEBE8000})
      == {0xFEBE8000, 0xFEBE8002})
check("unresolved named members and array elements do not invent scalar edges",
      cell_tokens("sample.member + sample[2] + sample [3] + missing", {},
                  {"sample": 0xFEBE8000}) == set())


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "cone.json"
    p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], capture_output=True, text=True, check=False)
    check("builder exits clean", p.returncode == 0, p.stderr[-200:] if p.returncode else "")
    check("artifact regenerates byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
den = art["ingress_denominator"]
check("extract denominator is 116 literal + 14 table-driven",
      den["literal_scalar_extracts"] == 116 and den["table_driven_extracts"] == 14)
check("table-driven extracts resolve to the 0x013..0x01F family",
      {x["can_id"] for x in den["table_driven"]} == set(range(0x13, 0x20))
      and [x["signal"] for x in den["table_driven"]] == list(range(90, 104)))
check("extract API geometry is pinned",
      den["extract_api_geometry"]["frame_block_base"] == "0xFEBE4A48"
      and den["extract_api_geometry"]["pdu_status_base"] == "0xFEBE493E")
check("0x090 10-bit transforms are the only transform helper family",
      den["transform_helpers"][0]["form"] == "s16(raw10 - 0x200)"
      and den["transform_helpers"][0]["signals"] == {"229": "0xFEBE808A", "232": "0xFEBE808C", "235": "0xFEBE808E"})

pipe = art["pipeline"]
check("L1 raw census is 116 with stack-RMW signal243",
      pipe["L1_raw_cells"]["count"] == 116 and "0x4BB62" in pipe["L1_raw_cells"]["signal243_path"])
census = pipe["L3_stage_reader_census"]
check("no C/D-family compute reads stages directly",
      all(int(r, 16) <= 0xBF0EC for r in census["readers"]))
check("group API callers are exactly the two qualifiers",
      pipe["group_api_callers"] == ["0x693FE", "0x697F4"])
check("L2 init-only stage cells have no runtime writer",
      pipe["L2_stage"]["init_only_stage_cells"] == {
          "0xFEBEF098": 0, "0xFEBEF099": 0, "0xFEBEF09C": 1, "0xFEBEF0AA": 0, "0xFEBEF1C0": 0})

blk = art["command_block_map"]
check("command block writer is 0xBF33E with 17 statement-mapped bytes",
      blk["writer"] == "0x000BF33E" and len(blk["bytes"]) == 17)
check("command-torque byte FEBEE40A comes from FEBEAC56 (FEBECC62 path)",
      blk["bytes"]["FEBEE40A"] == ["0xFEBEAC56"] and blk["via_D0AAE"]["FEBEAC56"] == "FEBECC62 (command torque)")
check("peripheral-fed byte and constants are pinned",
      blk["bytes"]["FEBEE408"] == ["0xFEBEAC58"] and blk["bytes"]["FEBEE401"] == []
      and blk["bytes"]["FEBEE402"] == [] and blk["bytes"]["FEBEE404"] == [])

pos = {x["can_id"]: x for x in art["positive_non_b6_cluster_inputs"]}
check("positive non-B6 set is exactly 0x090/0x0D7/0x675/0x13B",
      set(pos) == {"0x090", "0x0D7", "0x675", "0x13B"})
check("0x090 geometry is the 3x(flag+10-bit)+byte28 family",
      [g["signal"] for g in pos["0x090"]["geometry"]] == [227, 228, 229, 230, 231, 232, 233, 234, 235, 241]
      and [(g["signal"], g["byte"]) for g in pos["0x090"]["geometry"] if g["signal"] in (229,232,235,241)]
          == [(229,0),(232,2),(235,4),(241,28)])
check("0x0D7 sig246 geometry is B1:B2 u16",
      pos["0x0D7"]["geometry"][1] == {"signal": 246, "byte": 1, "bits": 16, "bit": 0, "signed": False})
base = art["baseline_internal_assist_path"]
check("D0382 limit table is exactly 0x2B4D/0x3A75/0x569A",
      set(base["limit_table"]) == {"0x2B4D", "0x3A75", "0x569A"})
check("D0218 direct internal value cells and runtime writers are pinned",
      base["direct_D0218_value_cells"] == ["FEBECB38", "FEBEC5EE", "FEBEC43C", "FEBEC4C0",
                                                "FEBEC3BA", "FEBECC2C", "FEBEBF3C", "FEBECBE8"]
      and base["direct_value_runtime_writers"] == {
          "FEBECB38":"0xCF2B2", "FEBEC5EE":"0xC9A84", "FEBEC43C":"0xC7E36", "FEBEC4C0":"0xC8678",
          "FEBEC3BA":"0xC74AC", "FEBECC2C":"0xD0162", "FEBEBF3C":"0xC2B64", "FEBECBE8":"0xCFCD4"})
codeflash = (REPO / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()

def _camry_u16(addr: int) -> int:
    return int.from_bytes(codeflash[addr:addr + 2], "little")

check("stock pass-through and fallback calibration words",
      _camry_u16(0xB04C2) == 0x100 and _camry_u16(0xB04C4) == 0x100
      and _camry_u16(0xB04C6) == 0x100 and _camry_u16(0xB04D4) == 0x0)
check("pulse window and magnitude calibration words",
      _camry_u16(0xB04B4) == 0x280 and _camry_u16(0xB04B6) == 5
      and _camry_u16(0xB04C0) == 0x12C)

sel = art["baseline_selector_machinery"]
check("baseline parameter-bank selector ordinary-COM inputs are exact and finite",
      [(x["signal"], x["can_id"], x["byte"], x["bits"], x["bit_offset"], x["stage_cell"])
       for x in sel["generated_com_inputs"]] == [
          (160,"0x51E",0,4,0,"0xFEBEF050"), (163,"0x51E",1,4,0,"0xFEBEF14A"),
          (166,"0x51E",5,2,6,"0xFEBEF141"), (224,"0x13B",2,4,0,"0xFEBEF14B"),
          (280,"0x490",0,3,4,"0xFEBEF168"), (281,"0x490",0,4,0,"0xFEBEF0A1"),
          (282,"0x1DA",0,4,0,"0xFEBEF156")])
valid = sel["com_receive_validity_companions"]
check("selector COM-receive validity companions are pinned",
      {k:(v["source"],v["pdu"],v["unpacker"]) for k,v in valid.items() if k.startswith("FEBEF")} == {
          "FEBEF0C2": ("FEBE8081",0x15,"0x4B8F4"),
          "FEBEF0A0": ("FEBE80D5",0x1C,"0x4BF4E"),
          "FEBEF157": ("FEBE80D8",0x1D,"0x4BFB2"),
          "FEBEF000": ("FEBE7F68",None,"shared COM gate"),
      })

mir = art["non_com_internal_mirrors"]
check("internal mirrors retain their source cells",
      mir["0x000FCC00"]["FEBEEF8E"] == "FEBE71F2"
      and mir["0x00057F00"]["FEBEEE02"] == "FEBE686C")
live = art["live_context"]
check("B6 remains absent in retained drives",
      live["b6_frames_in_retained_drives"] == 0)

prior = json.loads(PRIOR.read_text())
check("prior VAR-065 artifact chain for signal243 stays consistent",
      {c["signal"] for c in prior["scalar_command_cone_census"]["chains"]} >= {243, 261, 262})

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
