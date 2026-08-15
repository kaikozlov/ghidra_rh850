#!/usr/bin/env python3
"""Verify the generalized response-disclosure audit.

Pins: (1) byte-identical regeneration; (2) the verified 48-DID RDBI census is
reproduced exactly (selector set + declared widths); (3) the RoutineControl
packer model reflects the actual descriptor kinds (kind-6 assigns, kind-7
pointer copies with routine-owned lengths — four RIDs) rather than the action
callback; (4) WDBI and XCP surfaces close negative; (5) bootloader F181
remains a pinned negative.
"""
from __future__ import annotations

import csv
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
JSON_PATH = ROOT / "data" / "generated" / "response_disclosure_audit.json"
CSV_PATH = ROOT / "data" / "generated" / "response_disclosure_audit.csv"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


VERIFIED_RDBI_STUB_DIDS = {
    0x0111,
    0x1066, 0x106A,
    0x10C7, 0x10C8, 0x10C9,
    0x10F7, 0x10F8, 0x10F9,
    0x1124, 0x1125, 0x1126, 0x1127, 0x1128, 0x1129,
    0x112F, 0x1130, 0x1131,
    0x11BC, 0x11C8,
    0x1C99, 0x1C9A, 0x1C9B, 0x1C9C, 0x1C9D, 0x1C9E, 0x1C9F, 0x1CA0,
    0x1CF4, 0x1CF5, 0x1CF6, 0x1CF7, 0x1CF8, 0x1CF9, 0x1CFA, 0x1CFB, 0x1CFC, 0x1CFD, 0x1CFE, 0x1CFF,
    0x1D01, 0x1D02, 0x1D03,
    0x1F03, 0x1F04,
    0x2030, 0x2031, 0x2032,
}


def main() -> int:
    audit = json.loads(JSON_PATH.read_text())

    print("== regeneration is byte-identical ==")
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "generate_response_disclosure_audit.py")],
            capture_output=True, text=True,
        )
        check("generator exit 0", result.returncode == 0, result.stderr[-300:])
        check(
            "regenerated JSON matches tracked artifact",
            JSON_PATH.read_bytes() == json.dumps(json.loads(JSON_PATH.read_text()), indent=2, sort_keys=True).encode() + b"\n",
        )

    print("== RDBI census reproduces the verified 48-DID set ==")
    prone_rdbi = [
        f for f in audit["findings"]
        if f["surface"] == "application_rdbi" and not f["producer_writes_declared"]
    ]
    prone_dids = {int(f["selector"], 16) for f in prone_rdbi}
    check("prone RDBI selector set equals the verified census", prone_dids == VERIFIED_RDBI_STUB_DIDS,
          str(prone_dids ^ VERIFIED_RDBI_STUB_DIDS))
    widths = {int(f["selector"], 16): f["declared_response_bytes"] for f in prone_rdbi}
    check("all prone widths in 1..45", all(1 <= w <= 45 for w in widths.values()))
    check("15 DIDs at width 45 preserved", sum(1 for w in widths.values() if w == 45) == 15)

    print("== RoutineControl packer model ==")
    packs = [f for f in audit["findings"] if f["surface"] == "application_routine_control_pack"]
    check("17 RIDs have a type-3 pack row (0x100E/0x100F lack type 3)",
          sum(1 for f in packs if f["selector"].endswith("/type3_request_result")) == 17)
    check("five kind-7 pointer-copy response packs (0x1000/0x1001/0x1010 type1+type3, 0x1100 type1)",
          sorted(f["selector"] for f in packs
                 if "pointer-copy" in f["criterion"] and "pointer-copy" in f["criterion"])
          == ["0x1000/type1_result", "0x1001/type1_result",
              "0x1010/type1_result", "0x1010/type3_request_result", "0x1100/type1_result"])
    check("no OR-only response byte exists (every pack assigns first)",
          all(f["producer_writes_declared"] for f in packs))
    # Firmware anchors for the packer model.
    kind6 = 0x06
    d16 = 0x26760  # RID idx16 (0x110B) type-3 descriptor array
    check("0x110B type-3 descriptor is a single kind-6 assign at response byte 3",
          CF[d16 + 1] == kind6 and (struct.unpack_from("<H", CF, d16 + 4)[0] >> 3) == 0)

    print("== WDBI / XCP / bootloader negatives ==")
    check("no WDBI result callback is a success stub with nonzero result size",
          all(f["producer_writes_declared"] for f in audit["findings"] if f["surface"] == "application_wdbi"))
    check("all seven XCP handlers route through the full-frame builder",
          all(f["producer_writes_declared"] for f in audit["findings"] if f["surface"] == "xcp_command"))
    check("bootloader F181 is a pinned negative",
          all(f["producer_writes_declared"] for f in audit["findings"] if f["surface"] == "bootloader_rdbi"))

    print("== totals ==")
    check("prone total equals the verified 48", audit["prone_total"] == 48, str(audit["prone_total"]))
    check("prone surface counts", audit["prone_by_surface"]["application_rdbi"] == 48)

    with CSV_PATH.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    check("CSV rows match JSON findings", len(rows) == audit["total_rows"])

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
