#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
CUW = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"
ART = REPO / "data/generated/techstream_v18/cuw_timing_recovery.json"
DDB_ART = REPO / "data/generated/techstream_v18/priority_steering_ddb_semantics.json"

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

print("== decoded CUW timing/retry tables ==")
f = obj["factory_parameter_table"]["timing_retry_distributions"]
check("196 factory rows", obj["factory_parameter_table"]["rows"] == 196)
check("factory schema has 85 columns", obj["factory_parameter_table"]["columns"] == 85)
check("WaitTimeAfterSeedData 100ms x162, blank x34", f["WaitTimeAfterSeedData"] == {"": 34, "100": 162})
check("WaitTimeAfterSeedKey 100ms x162, blank x34", f["WaitTimeAfterSeedKey"] == {"": 34, "100": 162})
check("IGOffRetriableFlag exact", f["IGOffRetriableFlag"] == {"0": 21, "1": 175})
check("PrepareRetryFlag exact", f["PrepareRetryFlag"] == {"": 4, "0": 179, "1": 13})
check("single 120s WaitTimeAfterIGOnAtRetry", f["WaitTimeAfterIGOnAtRetry"] == {"": 195, "120000": 1})
check("single 200ms ReceveTimeoutSumCheck", f["ReceveTimeoutSumCheck"] == {"": 195, "200": 1})
check("RequestCANIDAllowingTimeout exact", f["RequestCANIDAllowingTimeout"] == {"": 190, "0705": 1, "07E1": 5})
check("reprogramming-mode wait distribution", f["WaitTimeAfterReprogrammingMode"] == {"": 30, "1500": 103, "2000": 1, "500": 62})

s = obj["system_parameter_table"]["host_ig_recovery_distributions"]
check("380 system rows", obj["system_parameter_table"]["rows"] == 380)
check("system schema has 30 columns", obj["system_parameter_table"]["columns"] == 30)
check("WaitTimeForIGOFFON exact", s["WaitTimeForIGOFFON"] == {"10": 368, "15": 2, "30": 10})
check("WaitTimeAfterIGOn exact", s["WaitTimeAfterIGOn"] == {"": 33, "1000": 6, "10000": 44, "15000": 3, "2000": 5, "3000": 1, "500": 3, "6000": 277, "7000": 8})
check("battery disconnect wait only two rows", s["WaitTimeAfterBatteryDisconnected"] == {"": 378, "10": 2})
check("battery connect wait only two rows", s["WaitTimeAfterBatteryConnected"] == {"": 378, "5": 2})
check("modern CID/writer host flag exact", s["FlagToUseCIDGetterAndFlashWriterDLL"] == {"0": 200, "1": 180})
check("three modern EPS route rows", [r["factory_identifier"] for r in obj["system_parameter_table"]["eps_rows"] if r["use_cid_getter_flash_writer"] == "1"] == ["13CAN161", "13CAN213", "13CAN(SECURITY)213"])

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
rows = tr["target_compatible_rows"]
check("exactly two target-compatible Unified recovery rows", [r["parameter_file"] for r in rows] == ["P5-Unified.ini", "P5-Unified10.ini"])
check("both target-compatible rows disable PrepareRetry", all(r["prepare_retry_flag"] == "0" for r in rows))
check("both target-compatible rows use the same Unified prepare writer", {r["prepare_writer"] for r in rows} == {"TCUWCanUnifiedPrepareWriter.dll"})
check("Unified rows retain host IG-off retry capability", all(r["ig_off_retriable_flag"] == "1" for r in rows))
for binary, expected in tr["exports"].items():
    pe = pefile.PE(str(CUW / binary))
    actual = sorted(s.name.decode("ascii", "replace") for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name)
    check(f"{binary} export set", actual == expected, repr(actual))
check("Unified prepare exports StartPrepareWrite only", tr["exports"]["TCUWCanUnifiedPrepareWriter.dll"] == ["StartPrepareWrite"])
check("no target-compatible Unified writer exports a retry entrypoint", all(not x for x in tr["prepare_retry_entrypoints"].values()))
check("normal Unified prepare grammar requires 18-byte 27 01", tr["normal_prepare_security_access"]["request_seed"] == "27 01 || 16 tester bytes; exact request length 0x12")
check("normal Unified prepare grammar requires 16-byte 27 02 key", tr["normal_prepare_security_access"]["send_key"] == "27 02 || 16-byte key")

print("\n== Flash Recovery schema and identity binding ==")
cuw_data = (CUW / "Cuw.exe").read_bytes()
cuw_pe = pefile.PE(data=cuw_data)
cuw_base = cuw_pe.OPTIONAL_HEADER.ImageBase
for rec in obj["flash_recovery"]["string_records"]:
    raw = cuw_pe.get_data(rec["va"] - cuw_base, len(rec["text"]) + 1)
    check(f"Recovery string {rec['text']}", raw == rec["text"].encode() + b"\x00")
fields = {r["name"]: r["offset"] for r in obj["flash_recovery"]["persisted_fields"]}
check("VIN persisted at +0x28", fields["VIN"] == 0x28)
check("WriteCpuIndex persisted at +0x54", fields["WriteCpuIndex"] == 0x54)
check("Writing/UseNewSoftwarePassword/WritingEndBlock contiguous", [fields[x] for x in ["Writing", "UseNewSoftwarePassword", "WritingEndBlock"]] == [0x58, 0x59, 0x5A])
check("AssyNo identity vector at +0x88", fields["AssyNo"] == 0x88)
check("vehicle update flags at +0xB8", fields["VehicleInfoForUpdateAvailableFlag"] == 0xB8)
for text in [
    b"Flash Calibration Update in Process - 1st retry",
    b"Flash Calibration Update in Process - 2nd retry",
    b"Flash Calibration Update in Process - 3rd retry",
    b"CUW made three unsuccessful attempts to reprogram the ECU.",
]:
    check("modern CUW retry UI: " + text.decode(), text in cuw_data)

print("\n== targeted EMPS_P5 recovery observables ==")
ddb = json.loads(DDB_ART.read_text())
source_map = {x["relative_path"]: x for x in ddb["sources"]}
for rec in obj["capture_observables"]["emsp5_power_cycle_data_ids"]:
    data_id = int(rec["data_id"], 16)
    check(f"capture observable has stable name {rec['data_id']}", bool(rec["name"]))
    for src in rec["sources"]:
        source = source_map[src["relative_path"]]
        row = source["sections"]["62"]["records"][src["record_index"]]
        check(
            f"{src['relative_path']} {rec['data_id']} raw record",
            row["fields"]["monitor_key_u16"] == data_id
            and row["fields"]["resolved_name"] == rec["name"]
            and hashlib.sha256(bytes.fromhex(row["raw_hex"])).hexdigest() == src["record_sha256"],
        )

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
