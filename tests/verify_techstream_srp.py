#!/usr/bin/env python3
"""Verify Techstream V18 UtilityNeo SRP decryption and diagnostic surface."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream/CONF"
sys.path.insert(0, str(REPO / "tools/techstream"))
from decode_srp import SRP_AES_KEY, SRP_WRAPPER, decrypt_srp  # noqa: E402

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


if not ROOT.is_dir():
    print("[SKIP] pinned Techstream V18 tree is unavailable")
    raise SystemExit(77)

files = sorted(ROOT.glob("*.srp"))
check("pinned V18 tree contains exactly 18 SRP utility scripts", len(files) == 18, str(len(files)))
check("EntranceDLL SRP AES key is the recovered 32-byte value", len(SRP_AES_KEY) == 32)
check("SRP wrapper is the recovered four-byte marker", SRP_WRAPPER == b"H\x02H\x02")

service_counts: Counter[int] = Counter()
for path in files:
    text = decrypt_srp(path)
    check(f"{path.name}: decrypts to UtilityNeo XML", text.lstrip().startswith("<?xml"))
    check(f"{path.name}: contains a Utility root", "<UTILITY>" in text.upper())
    for match in re.finditer(r"<FRAME>\$([0-9A-Fa-f]{2})", text):
        service_counts[int(match.group(1), 16)] += 1

expected = {
    0x10: 4, 0x11: 1, 0x14: 1, 0x21: 4, 0x22: 5, 0x2E: 1, 0x2F: 1,
    0x31: 8, 0x3B: 13, 0x50: 1, 0x51: 1, 0x54: 1, 0x61: 4, 0x62: 13,
    0x6E: 2, 0x6F: 1, 0x71: 12, 0x7B: 13, 0x7F: 86, 0xA8: 7, 0xE8: 7,
}
check("literal SRP FRAME service-byte census is exact", dict(service_counts) == expected, repr(dict(service_counts)))
check("SRP scripts contain no literal SecurityAccess SID 0x27", service_counts[0x27] == 0)
check("SRP scripts contain no literal RequestDownload SID 0x34", service_counts[0x34] == 0)
check("SRP scripts contain no literal TransferData SID 0x36", service_counts[0x36] == 0)
check("SRP scripts contain no literal RequestTransferExit SID 0x37", service_counts[0x37] == 0)

all_text = "\n".join(decrypt_srp(path) for path in files).lower()
check("decoded SRPs contain no SecurityAccess/auth-key vocabulary",
      all(token not in all_text for token in ("securityaccess", "seedkey", "serviceauthkey", "ecuauthkey")))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
