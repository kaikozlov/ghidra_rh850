#!/usr/bin/env python3
"""Verify exact-F33 0x394 DEM/classifier fault-status recovery.

Standalone section of the exact-F33 portable family; assertions are carried over verbatim.
"""
from __future__ import annotations

from tools import REPO_ROOT
def section_fault_status() -> int:
    """Verify exact-F33 0x394 DEM/classifier fault-status recovery."""

    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    ROOT = REPO_ROOT
    IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
    EVID = ROOT / "data/generated/camry_8965F3307000_fault_status_decompiler_evidence.json"
    ART = ROOT / "data/generated/camry_8965F3307000_fault_status.json"
    BUILD = ROOT / "tools/targets/camry/builders/build_camry_8965F3307000_fault_status.py"

    passed = failed = 0


    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()


    def check(name: str, condition: object) -> None:
        nonlocal passed, failed
        ok = bool(condition)
        passed += int(ok)
        failed += int(not ok)
        print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}")


    img = IMAGE.read_bytes()
    evid = json.loads(EVID.read_text(encoding="utf-8"))
    art = json.loads(ART.read_text(encoding="utf-8"))
    funcs = {int(row["entry"], 16): row for row in evid["functions"]}

    print("== exact target/evidence identity ==")
    check("image hash", sha(img) == evid["image"]["sha256"] == art["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
    for entry, row in sorted(funcs.items()):
        check(f"0x{entry:08X} body hash", sha(img[entry:entry + row["body_size"]]) == row["body_sha256"])
    with tempfile.TemporaryDirectory(prefix="camry-f33-fault-status-") as td:
        out = Path(td) / "fault-status.json"
        proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
        check("builder exits cleanly", proc.returncode == 0)
        check("builder reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

    print("\n== target-native 0x394 classifier ==")
    c = art["classifier"]
    check("classifier entry exact", c["entry"] == "0x000512E4" and c["class_accumulator"] == "0x00050FC8")
    check("state table exact address", c["state_table"] == "0x0002A19C")
    check("state table has 17 rows", len(c["state_table_rows"]) == 17)
    check("state table exact bytes", img[0x2A19C:0x2A19C + 85].hex() == "00000000000403000000040700000005030000000403000000010100000003030201020303020100060303000206030300000307010101030704010106070700010607060001060705000102020000000407000000")

    print("\n== exact wire projection ==")
    w = art["wire"]
    proj = {tuple(row["wire"]): tuple(row["states"]) for row in w["projection_to_state_candidates"]}
    check("0x394 exact carrier", w["can_id"] == "0x394" and w["length"] == 3)
    check("unique state0 projection", proj[(0, 0, 0, 0)] == (0,))
    check("class02 unique projection", proj[(2, 3, 2, 1)] == (6,))
    check("class10 unique projection", proj[(1, 7, 1, 1)] == (10,))
    check("first lossy projection exact", proj[(0, 3, 0, 0)] == (1, 3, 4))
    check("second lossy projection exact", proj[(0, 7, 0, 0)] == (2, 16))

    print("\n== target-native aging/calibration ==")
    a = art["aging"]
    check("calibration address exact", a["calibration_address"] == "0x00030E40")
    check("raw calibration words exact", a["raw_u16"] == [200, 200, 600, 22170, 200, 200, 1000])
    check("primary/aggregate/secondary ages exact", (a["primary_latch_bank_355d_age"], a["aggregate_latch_bank_355c_age"], a["class2_class4_secondary_latch_age"]) == (200, 200, 600))
    check("F33 clear-enable age is target-specific", a["primary_clear_enable_age"] == 22170 and a["comparison_to_h"] == {"h_primary_clear_enable_age": 17736, "f33_primary_clear_enable_age": 22170})

    print("\n== target-native DEM/DTC census ==")
    d = art["dem"]
    check("event table geometry exact", d["event_table"] == "0x0002FC50" and d["event_count"] == 0x180 and d["record_size"] == 8)
    check("class histogram exact", d["class_counts"] == {"0x01":8,"0x02":34,"0x04":1,"0x08":1,"0x0F":1,"0x10":171,"0x20":16,"0x40":1,"0x80":7})
    check("240 classified events", sum(d["class_counts"].values()) == 240)
    comp = d["comparison_to_h"]
    check("31 H/F event records differ", comp["changed_record_count"] == 31 and len(comp["changed_records"]) == 31)
    check("only thermal events leave class10", comp["class_removed_events"] == ["0x0085", "0x0088"])
    check("only event0AC loses DTC index", comp["dtc_index_removed_events"] == ["0x00AC"])
    thermal = comp["thermal_dtcs_removed_from_class_0x10"]
    check("thermal A/B DTC names exact", [(x["event"], x["dtc"]["techstream_code"], x["dtc"]["techstream_description"]) for x in thermal] == [
        ("0x0085", "C10051C", 'Control Module Internal Temperature Sensor "B"'),
        ("0x0088", "C10001C", 'Control Module Internal Temperature Sensor "A"'),
    ])
    check("DTC table exact relocation", art["dtc"]["table"] == "0x00030850")
    check("80 referenced DTC rows remain byte-identical", art["dtc"]["referenced_index_count"] == 80 and art["dtc"]["referenced_rows_identical_to_h"] is True)
    check("DTC index120 exact disable", art["dtc"]["index_120_disabled"] == {"h_raw":"8710d10001000000", "f33_raw":"8710d10000000000"})

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(section_fault_status())
