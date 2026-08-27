#!/usr/bin/env python3
"""Rebuild the current-GTS+ -> exact-F33 semantic join from pinned external bytes."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
GTS_ROOT = REPO / "software/Techstream/gtsplus"
GTS_ARCHIVE = GTS_ROOT / "gtsplus.7z"
GTS_LOCK = REPO / "software/locks/gtsplus.json"
V18_ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream"
ART = REPO / "data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json"
GEN = REPO / "tools/techstream/extract_gtsplus_camry_emps_semantics.py"
PARSER_DIR = REPO / "tools/techstream"
sys.path.insert(0, str(PARSER_DIR))
from parse_ddb import ECU_TABLE_CLASS_NAMES  # noqa: E402

ARCHIVE_MEMBERS = [
    "gtsplus/Toyota Diagnostics/GTSPlus/NA/DB/Gen/EMPS_P5.ddb",
    "gtsplus/Toyota Diagnostics/GTSPlus/NA/DB/Gen/M_English.ddb",
    "gtsplus/Toyota Diagnostics/GTSPlus/NA/DB/Gen/Toyota.ddb",
    "gtsplus/Toyota Diagnostics/GTSPlus/bin/KgpDataCtrl.dll",
]
CURRENT_FACTORY_CLASSES = {
    151: "CDbDataIdForRobTable",
    152: "CDbBehaviorSignalCheckTable",
    153: "CDbBehaviorDataRecordP5Table",
    154: "CDbSignalGroupTable",
    155: "CDbSignalCheckTable",
    156: "CDbDataIdForDmTable",
    157: "CDbDatamonitorP5Table",
    158: "CDbTableBase",
    159: "CDbTableBase",
    160: "CDbMonitorStatus_J1979_2_3_Table",
    161: "CDbMonitorResultCan_J1979_2_3_Table",
    162: "CDbDetailLink_J1979_2_3_Table",
    163: "CDbRoBDiagCodeTable",
    164: "CDbRoBFreezeFrameTable",
    165: "CDbDDRDiagCodeTable",
    166: "CDbDataIdForDdrTable",
    167: "CDbDDRFreezeFrameTable",
    168: "CDbDDRInvalidConditionTable",
    169: "CDbTableBase",
    170: "CDbScaling_J1979_2_3_Table",
    171: "CDbPreFFDVehicleTypePIDIDTable",
}
JUMP_TABLE_VA = 0x10088DCC

passed = failed = 0

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}" + (f" ({detail})" if detail else ""))

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def current_factory_map(path: Path) -> dict[int, str]:
    pe = pefile.PE(str(path), fast_load=False)
    image_base = pe.OPTIONAL_HEADER.ImageBase
    exports: dict[int, str] = {}
    rx = re.compile(r"^\?__autoclassinit2@([^@]+)@@QAEXI@Z$")
    for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if not symbol.name:
            continue
        name = symbol.name.decode("ascii", "strict")
        m = rx.match(name)
        if m:
            exports[image_base + symbol.address] = m.group(1)
    raw = pe.get_data(JUMP_TABLE_VA - image_base, (max(CURRENT_FACTORY_CLASSES) + 1) * 4)
    out: dict[int, str] = {}
    for table_id in CURRENT_FACTORY_CLASSES:
        case_va = struct.unpack_from("<I", raw, table_id * 4)[0]
        body = pe.get_data(case_va - image_base, 0x80)
        hits = []
        for off, opcode in enumerate(body[:-4]):
            if opcode != 0xE8:
                continue
            target = case_va + off + 5 + struct.unpack_from("<i", body, off + 1)[0]
            if target in exports:
                hits.append(exports[target])
        if hits:
            out[table_id] = hits[0]
    return out

lock = json.loads(GTS_LOCK.read_text(encoding="utf-8"))
source = lock["distribution"]["source_archive"]
check("GTS+ archive exists", GTS_ARCHIVE.is_file(), str(GTS_ARCHIVE))
check("GTS+ archive size is lock-pinned", GTS_ARCHIVE.is_file() and GTS_ARCHIVE.stat().st_size == source["size"])
check("GTS+ archive SHA-256 is lock-pinned", GTS_ARCHIVE.is_file() and sha256(GTS_ARCHIVE) == source["sha256"])
check("V18 reconstructed database root exists", V18_ROOT.is_dir(), str(V18_ROOT))

if not GTS_ARCHIVE.is_file() or not V18_ROOT.is_dir():
    raise SystemExit(1)

committed = json.loads(ART.read_text(encoding="utf-8"))
with tempfile.TemporaryDirectory(prefix="gtsplus-f33-external-") as td:
    temp = Path(td)
    proc = subprocess.run(
        ["7z", "x", "-y", f"-o{temp}", str(GTS_ARCHIVE), *ARCHIVE_MEMBERS],
        cwd=REPO, capture_output=True, text=True,
    )
    check("selective GTS+ archive extraction succeeds", proc.returncode == 0, proc.stderr[-300:])
    root = temp / "gtsplus/Toyota Diagnostics/GTSPlus"
    extracted = [temp / member for member in ARCHIVE_MEMBERS]
    check("all four required current GTS+ members extracted", all(path.is_file() for path in extracted))

    if proc.returncode == 0 and all(path.is_file() for path in extracted):
        kgp = root / "bin/KgpDataCtrl.dll"
        factory = current_factory_map(kgp)
        check("current Kgp format-2 IDs 151..171 resolve independently", factory == CURRENT_FACTORY_CLASSES, str(factory))
        check("parser current IDs 151..171 match current factory", {k: ECU_TABLE_CLASS_NAMES[k] for k in CURRENT_FACTORY_CLASSES} == CURRENT_FACTORY_CLASSES)
        check("current Kgp identity matches promoted source", sha256(kgp) == committed["sources"]["gts_kgp"]["sha256"])

        rebuilt_path = temp / "rebuilt.json"
        gen = subprocess.run(
            [sys.executable, str(GEN), "--gtsplus-root", str(root), "--v18-root", str(V18_ROOT), "--out", str(rebuilt_path)],
            cwd=REPO, capture_output=True, text=True,
        )
        check("GTS+ Camry semantic generator succeeds from selective external corpus", gen.returncode == 0, gen.stderr[-500:])
        if gen.returncode == 0 and rebuilt_path.is_file():
            rebuilt = json.loads(rebuilt_path.read_text(encoding="utf-8"))
            check("rebuilt source hashes/sizes equal promoted artifact", all(
                rebuilt["sources"][name]["sha256"] == committed["sources"][name]["sha256"]
                and rebuilt["sources"][name]["size"] == committed["sources"][name]["size"]
                for name in committed["sources"]
            ))
            # Temporary extraction changes only provenance display paths. Normalize those
            # labels back to the committed canonical paths before strict object equality.
            for name in rebuilt["sources"]:
                rebuilt["sources"][name]["path"] = committed["sources"][name]["path"]
            check("external regeneration is semantically byte-equivalent after path normalization", rebuilt == committed)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
