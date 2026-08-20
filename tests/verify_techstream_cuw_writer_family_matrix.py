#!/usr/bin/env python3
"""Verify the complete decoded-route -> CUW writer-family census."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics"
CUW = ROOT / "Calibration Update Wizard"
MATRIX = REPO / "data/generated/techstream_v18/cuw_writer_family_matrix.json"
passed = failed = 0
oracle = "raw_bytes"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


if not ROOT.is_dir():
    print("[SKIP] pinned Techstream V18 tree is unavailable")
    raise SystemExit(77)


def decode(data: bytes) -> bytes:
    assert len(data) % 2 == 0
    out = bytearray()
    for a, b in zip(data[::2], data[1::2]):
        out.append((((((a & 0xF) >> 2) + (a >> 4) * 4) * 4 + (b >> 4) + 0x1E) * 4 + ((b & 0xF) >> 2)) & 0xFF)
    return bytes(out).rstrip(b"\xff")

print("== independent route census ==")
refs = Counter(); rows = 0; decoded_files = 0
for path in sorted((CUW / "Ini").glob("*.ini")):
    try:
        parsed = list(csv.reader(io.StringIO(decode(path.read_bytes()).decode("latin1"))))
    except Exception:
        continue
    decoded_files += 1
    if len(parsed) < 2 or "DLLFileNameForPrepareWrite" not in parsed[0]:
        continue
    header = parsed[0]
    for row in parsed[1:]:
        row += [""] * (len(header) - len(row))
        item = dict(zip(header, row)); rows += 1
        for key in ("DLLFileNameForPrepareWrite", "DLLFileNameForFlashWrite"):
            if item.get(key): refs[item[key]] += 1
check("all 201 encoded INIs decode", decoded_files == 201, str(decoded_files))
check("factory row count is 196", rows == 196, str(rows))
check("decoded rows reference exactly 47 writer DLLs", len(refs) == 47, str(len(refs)))
check("every referenced writer exists", all((CUW / name).is_file() for name in refs))

matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
writers = {row["name"]: row for row in matrix["writers"]}
check("tracked matrix covers exact raw writer set", set(writers) == set(refs))
check("matrix stats pin 22 prepare / 25 flash", matrix["writer_stats"]["prepare_writers"] == 22 and matrix["writer_stats"]["flash_writers"] == 25)
check("matrix has no missing referenced writer", matrix["writer_stats"]["missing_referenced_writers"] == [])
check("route-use counts reproduce decoded rows", sum(w["route_row_count"] for w in writers.values() if "prepare" in w["roles"]) == 196 and sum(w["route_row_count"] for w in writers.values() if "flash" in w["roles"]) == 196)

print("\n== raw PE import fingerprints ==")
oracle = "cfg_dataflow"
for name, row in writers.items():
    data = (CUW / name).read_bytes(); pe = pefile.PE(data=data)
    check(f"{name}: SHA pinned", hashlib.sha256(data).hexdigest() == row["sha256"])
    imported = {(lib.dll.decode("latin1"), sym.name.decode("latin1") if sym.name else f"ordinal:{sym.ordinal}")
                for lib in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []) for sym in lib.imports}
    raw_cal = {n for dll, n in imported if dll == "TCUWCalibrationFile.dll" and ("@CalibrationFile@@" in n or "@CalibArchivedFile@@" in n)}
    for getter in row["calibration_getters"]:
        check(f"{name}: getter {getter} has raw import", any(getter in n for n in raw_cal))

sec_vforest = writers["TCUWCanSecurityVFORESTFlashWriter.dll"]
check("security VFOREST imports nonce and seed-key material", {"GetNonce", "GetSeedKey"} <= set(sec_vforest["calibration_getters"]))
check("security VFOREST is tagged material-transfer", "nonce-seed-material-transfer" in sec_vforest["protocol_tags"])
check("security VFOREST route is target-rejected for Sienna", all(x["sienna_8965B4512000"] == "rejected" for x in sec_vforest["target_route_dispositions"]))
for name in ("TCUWP4CanSecurityAirbagPrepareWriter.dll", "TCUWP4CanSecurityChassisShrinkPrepareWriter.dll", "TCUWP5CanSecurityPowerTrainPrepareWriter.dll"):
    check(f"{name}: security-up wrapper is explicit import", "security-up-aes-wrapper" in writers[name]["protocol_tags"])
for name in ("TCUWCanReproStdPrepareWriter.dll", "TCUWCanUnifiedPrepareWriter.dll", "TCUWCanReproStdFlashWriter.dll", "TCUWCanUnifiedFlashWriter.dll"):
    check(f"{name}: exact recovered command list retained", bool(writers[name]["exact_recovered_commands"]))

print("\n== exact route-level target dispositions ==")
route_map = {}
for row in writers.values():
    for route in row["target_route_dispositions"]:
        key = (route["prepare_writer"], route["flash_writer"])
        if key in route_map:
            check(f"{key}: repeated route disposition identical", route_map[key] == route)
        else:
            route_map[key] = route
check("matrix carries all 32 exact route pairs", len(route_map) == 32)
counts = Counter()
for route in route_map.values():
    counts[route["sienna_8965B4512000"]] += route["factory_rows"]
check("all 196 rows statically closed 194 rejected / 2 compatible", counts == Counter({"rejected": 194, "byte-compatible": 2}), repr(counts))
check("Corolla-H route dispositions match transferred boot grammar", all(x["corolla_8965H1202000"] == x["sienna_8965B4512000"] for x in route_map.values()))
check("writer-level target_disposition is explicitly structural", all(x["target_disposition"]["sienna_8965B4512000"].startswith("structural-") for x in writers.values()))

print("\n== live deterministic regeneration ==")
oracle = "generated_self_check"
with tempfile.TemporaryDirectory(prefix="cuw-writer-matrix-") as td:
    out = Path(td) / "matrix.json"
    result = subprocess.run([sys.executable, str(REPO / "tools/techstream/generate_cuw_writer_family_matrix.py"), "--root", str(ROOT), "--output", str(out)], check=False)
    check("generator exits successfully", result.returncode == 0)
    check("regeneration is byte-identical", out.read_bytes() == MATRIX.read_bytes())

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
