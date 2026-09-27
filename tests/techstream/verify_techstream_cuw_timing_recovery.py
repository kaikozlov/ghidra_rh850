#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import pefile

from tools import REPO_ROOT
REPO = REPO_ROOT
CUW = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"
ART = REPO / "data/generated/techstream_v18/cuw_timing_recovery.json"

passed = failed = 0
oracle = "raw_bytes"


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


if not CUW.is_dir():
    print("[SKIP] pinned Techstream V18 corpus unavailable")
    raise SystemExit(77)

obj = json.loads(ART.read_text())

print("\n== timing-key code-reference attribution ==")
def absolute_refs(binary: str, text: str) -> list[int]:
    data = (CUW / binary).read_bytes()
    pe = pefile.PE(data=data)
    off = data.find(text.encode("ascii"))
    assert off >= 0
    va = pe.OPTIONAL_HEADER.ImageBase + pe.get_rva_from_offset(off)
    pat = struct.pack("<I", va)
    out = []
    for sec in pe.sections:
        if not (sec.Characteristics & 0x20000000):
            continue
        raw = sec.get_data()
        start = sec.VirtualAddress
        for i in range(0, len(raw) - 3):
            if raw[i:i + 4] == pat:
                out.append(pe.OPTIONAL_HEADER.ImageBase + start + i)
    return out

check("P4/P5 prepare references WaitTimeAfterSeedData", 0x100019F0 in absolute_refs("TCUWP4P5CanPowerTrainPrepareWriter.dll", "WaitTimeAfterSeedData"))
check("P4/P5 prepare references WaitTimeAfterSeedKey", 0x10001F2F in absolute_refs("TCUWP4P5CanPowerTrainPrepareWriter.dll", "WaitTimeAfterSeedKey"))
check("ControlCommPhase has no code ref to WaitTimeAfterSeedData", absolute_refs("TCUWControlCommPhase.dll", "WaitTimeAfterSeedData") == [])
check("ControlCommPhase has no code ref to WaitTimeAfterSeedKey", absolute_refs("TCUWControlCommPhase.dll", "WaitTimeAfterSeedKey") == [])
check("ControlCommPhase consumes PrepareRetryFlag", 0x10007953 in absolute_refs("TCUWControlCommPhase.dll", "PrepareRetryFlag"))
check("ControlCommPhase consumes IGOffRetriableFlag", 0x100077C7 in absolute_refs("TCUWControlCommPhase.dll", "IGOffRetriableFlag"))
check("ControlCommPhase consumes ReceiveTimeoutBeforePrepareRetry", 0x100079B5 in absolute_refs("TCUWControlCommPhase.dll", "ReceiveTimeoutBeforePrepareRetry"))
check("CANCommunicationSpeedAddress consumed by common prepare", 0x1000166B in absolute_refs("TCUWCanCommonPrepareWriter.dll", "CANCommunicationSpeedAddress"))

print("\n== byte-pinned controller/writer/recovery bodies ==")
for rec in obj["function_identities"]:
    data = (CUW / rec["binary"]).read_bytes()
    pe = pefile.PE(data=data)
    body = pe.get_data(rec["va"] - pe.OPTIONAL_HEADER.ImageBase, rec["size"])
    check(rec["role"], hashlib.sha256(body).hexdigest() == rec["sha256"])

print("\n== target-compatible Unified recovery does not bypass SecurityAccess ==")
tr = obj["target_unified_recovery"]
for binary, expected in tr["exports"].items():
    pe = pefile.PE(str(CUW / binary))
    actual = sorted(s.name.decode("ascii", "replace") for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name)
    check(f"{binary} export set", actual == expected, repr(actual))
print("\n== Flash Recovery schema and identity binding ==")
cuw_data = (CUW / "Cuw.exe").read_bytes()
cuw_pe = pefile.PE(data=cuw_data)
cuw_base = cuw_pe.OPTIONAL_HEADER.ImageBase
for rec in obj["flash_recovery"]["string_records"]:
    raw = cuw_pe.get_data(rec["va"] - cuw_base, len(rec["text"]) + 1)
    check(f"Recovery string {rec['text']}", raw == rec["text"].encode() + b"\x00")
for text in [
    b"Flash Calibration Update in Process - 1st retry",
    b"Flash Calibration Update in Process - 2nd retry",
    b"Flash Calibration Update in Process - 3rd retry",
    b"CUW made three unsuccessful attempts to reprogram the ECU.",
]:
    check("modern CUW retry UI: " + text.decode(), text in cuw_data)

print("\n== legacy iQ-EMPS bounded comparative vocabulary ==")
iq_data = (CUW / "Cuw_iQ_EMPS.exe").read_bytes()
check("iQ binary identity", hashlib.sha256(iq_data).hexdigest() == obj["legacy_iq_emps"]["sha256"])
for rec in obj["legacy_iq_emps"]["strings"]:
    check("iQ string: " + rec["text"], rec["file_offset"] >= 0 and iq_data[rec["file_offset"]:rec["file_offset"] + len(rec["text"])] == rec["text"].encode())

print("\n== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "x.json"
    r = subprocess.run([sys.executable, str(REPO / "tools/techstream/generate_cuw_timing_recovery.py"), "--output", str(out)], check=False)
    check("generator exits", r.returncode == 0)
    check("byte-identical regeneration", out.read_bytes() == ART.read_bytes())

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
