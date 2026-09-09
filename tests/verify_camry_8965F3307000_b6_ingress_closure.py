#!/usr/bin/env python3
"""Verify the exact-F33 B6 ingress/publication closure from raw bytes and corpus."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
INVENTORY = ROOT / "data/targets/camry-8965F3307000/ghidra_project_inventory.baseline.jsonl"
ART = ROOT / "data/generated/camry_8965F3307000_b6_ingress_closure.json"
BUILD = ROOT / "tools/analyze_camry_8965F3307000_b6_ingress_closure.py"
IMAGE_SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
INVENTORY_SHA = "ccbf09df3807942b67f21789c1068b2be2bc2eb12d71bc2bf349f06b8386496d"

passed = failed = 0


def check(name: str, value: object) -> None:
    global passed, failed
    ok = bool(value)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][f33_b6_ingress] {name}")


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "closure.json"
    proc = subprocess.run([sys.executable, str(BUILD), "--output", str(out)],
                          cwd=ROOT, capture_output=True, text=True, check=False)
    check("analyzer exits cleanly", proc.returncode == 0)
    check("artifact regenerates byte-exact", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

image = IMAGE.read_bytes()
art = json.loads(ART.read_text())
metadata = None
functions: dict[int, dict] = {}
for line in CORPUS.read_text().splitlines():
    row = json.loads(line)
    if row.get("record") == "metadata":
        metadata = row
    elif row.get("record") == "function":
        functions[int(row["entry_addr"], 16)] = row

check("exact CodeFlash and repaired canonical inventory are pinned",
      hashlib.sha256(image).hexdigest() == IMAGE_SHA
      and hashlib.sha256(INVENTORY.read_bytes()).hexdigest() == INVENTORY_SHA
      and metadata is not None and metadata["project_inventory_sha256"] == INVENTORY_SHA
      and len(functions) == metadata["function_count"] == 6065)
check("three previously omitted real entries have complete bodies",
      {entry: functions[entry]["body_size"] for entry in (0x71508, 0x7D72C, 0x810F2)}
      == {0x71508: 170, 0x7D72C: 212, 0x810F2: 204})

# Independent raw-table decoding: rule39 and descriptor39 are both B6, while
# the lower and upper callback tables select the recovered normal path.
rule39 = struct.unpack_from("<IIII", image, 0x230B8 + 39 * 16)
descriptor39 = struct.unpack_from("<II", image, 0x21FE8 + 39 * 8)
check("controller-1 rule39 accepts B6 into FIFO2", rule39 == (0xB6, 0x00300000, 2, 0))
check("CanIf descriptor39 is 32-byte FD B6/PDU44",
      descriptor39 == (0x400000B6, 32) and 5 + 39 == 44)
check("PduR lower and generated-COM upper callbacks are exact",
      struct.unpack_from("<I", image, 0x21CE4)[0] == 0x81D30
      and struct.unpack_from("<I", image, 0x21E08)[0] == 0x7D72C)
check("route44 generated-COM record is exact",
      image[0x226C0 + 44 * 8:0x226C0 + 45 * 8].hex() == "060000002000000c")

check("artifact pins the one configured B6 chain",
      art["physical_ingress"]["b6_rule_index"] == 39
      and art["physical_ingress"]["b6_descriptor"] == {
          "index": 39, "raw": 0x400000B6, "can_id": 0xB6,
          "fd": True, "length": 32, "pdu": 44,
      }
      and art["canif_pdur"]["lower_route44"] == [44, 44]
      and art["canif_pdur"]["secured_ingress_callback"] == "0x0008EE7C")
check("profile2 receive queue geometry is exact",
      art["secoc_receive"]["b6_profile"] == 2
      and art["secoc_receive"]["queue_family"] == 1
      and art["secoc_receive"]["queue_record"] == "0xFEBE547A"
      and art["secoc_receive"]["secured_buffer"] == "0xFEBE54D4"
      and art["secoc_receive"]["payload_copy_precedes_length_publication"] is True)
check("same-invocation queue timing is explicit",
      art["scheduler"]["ring_drain_call_site"] == "0x0007A26E"
      and art["scheduler"]["secoc_consumer_call_site"] == "0x0007A2B4"
      and art["scheduler"]["same_invocation_order"] == "ring drain/enqueue precedes SecOC consumer")
publication = art["route44_publication"]
check("successful receive is the only recovered route44 publication root",
      publication["generation_helper_direct_callers"] == ["0x0007D72C"]
      and publication["com_callback_direct_callers"] == []
      and publication["upper_caller_census"]["0x00090204"] == ["0x0008F546"]
      and publication["autonomous_software_route44_ticker_recovered"] is False)
check("family0 insertion cannot fabricate the family1 B6 receive queue",
      art["secoc_receive"]["opposite_family_insert_path"]
      == ["0x0008ED8E", "0x0008FABA", "0x0008E9C6(family0)"])
check("static/runtime boundary rejects TX-echo overclaim",
      any("Panda TX echo proves local transmission" in x for x in art["runtime_only_boundaries"])
      and any("No autonomous software route44 generation path" in x for x in art["static_conclusions"]))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
