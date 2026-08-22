#!/usr/bin/env python3
"""Verify the persisted Span 2025 Corolla memory corpus and XCP-retention transfer."""
from __future__ import annotations

import hashlib
import itertools
import json
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COMMUNITY = REPO / "community/spanconstant"
ZIP = COMMUNITY / "spanconstant_tsk.zip"
RAW = COMMUNITY / "raw-20260821"
SESSION = RAW / "span-corolla-2025.20260821-1511"
MANIFEST = RAW / "MANIFEST.txt"
CODEFLASH = SESSION / "dump_codeflash_00000000_00200000_20260821-152033.bin"
H_CODEFLASH = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"

ZIP_SHA = "a5744b4c4627d3e5c20d590bb882d25b9b40c0679cbc3e9660140c7f2ef5262b"
CODEFLASH_SHA = "b8fa3d951f59fb75c190ce1b2c73164adb952f871650cfcd3b7656f08a9c448d"
NORMALIZED_SHA = "fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6"

MEMBERS = {
    "dump_codeflash_00000000_00200000_20260821-152033.bin": (2097152, CODEFLASH_SHA, "tsk/range-dumps/dump_codeflash_00000000_00200000_20260821-152033.bin"),
    "dump_dataflash_ff200000_ff210000_20260821-151200.bin": (65536, "85d76a96436e99e246b0695938e2dd046b8878e7d0e68f2ba7cd79f285f468a2", "tsk/range-dumps/dump_dataflash_ff200000_ff210000_20260821-151200.bin"),
    "dump_dataflash_ff200000_ff210000_20260821-151612.bin": (65536, "7f64ae2e66af7d8367e1926a7f2137f8255e0b92b82a77e55cedde4eee418137", "tsk/range-dumps/dump_dataflash_ff200000_ff210000_20260821-151612.bin"),
    "dump_dataflash_ff200000_ff210000_20260821-151743.bin": (65536, "c90903073c483d6743e35ff4ab6aa6bbcb78756b0a025c620027f910568cd271", "tsk/range-dumps/dump_dataflash_ff200000_ff210000_20260821-151743.bin"),
    "dump_extended_codeflash_01000000_0100c000_20260821-151952.bin": (49152, "90cc7b3d88e0c8b7ef330160ecb792134f5fbf9b9d8219c80d038a5451a15cc7", "tsk/range-dumps/dump_extended_codeflash_01000000_0100c000_20260821-151952.bin"),
    "dump_global_ram_feef8000_fef08000_20260821-151923.bin": (65536, "aedfa4def81ca249cc93154f04c8c017d75d5cf45b8e4a707399266f3c4e0713", "tsk/range-dumps/dump_global_ram_feef8000_fef08000_20260821-151923.bin"),
    "dump_local_ram_pe1_febe0000_fec00000_20260821-151834.bin": (131072, "255e167643e297fcc6e7458d3372e3df53eed08bd21e2b55714451aac4ee4e38", "tsk/range-dumps/dump_local_ram_pe1_febe0000_fec00000_20260821-151834.bin"),
    "dump_local_ram_self_fede0000_fee00000_20260821-152418.bin": (131072, "7668da24f9baceb6329221be8ad0fabae16650df80a234e6ef76decc4f6c0e44", "tsk/range-dumps/dump_local_ram_self_fede0000_fee00000_20260821-152418.bin"),
    "preflight_8965012N50E12H030731_20260821-151149.json": (3436, "a069f155695dd10a19834afb2a3f7b35daaac52d52fc0be66f56d213cda57285", "tsk/preflight/preflight_8965012N50E12H030731_20260821-151149.json"),
    "route.json": (159, "c6fcb2b72b9ce447f6d62af119e93de7ca3ee6f10affa95ea98a15d2e435d4aa", "tsk/preflight/route.json"),
    "security_access_log.json": (2173, "9db9eaf86eb3faf524c550dc8628f14b8f2ecea40920dc9b18c0779d32760c35", "tsk/security_access_log.json"),
}

passed = failed = 0

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")

print("== source ZIP and deterministic extraction ==")
check("source ZIP is retained", ZIP.is_file())
zip_bytes = ZIP.read_bytes()
check("source ZIP SHA-256 is pinned", sha(zip_bytes) == ZIP_SHA)
check("normalization manifest is retained", MANIFEST.is_file())
with zipfile.ZipFile(ZIP) as zf:
    names = set(zf.namelist())
    check("source ZIP retains original macOS metadata", any(n.startswith("__MACOSX/") for n in names))
    for name, (size, expected_sha, source_member) in MEMBERS.items():
        path = SESSION / name
        check(f"normalized {name} exists", path.is_file())
        if not path.is_file():
            continue
        data = path.read_bytes()
        check(f"normalized {name} size is pinned", len(data) == size)
        check(f"normalized {name} SHA-256 is pinned", sha(data) == expected_sha)
        check(f"normalized {name} is exact ZIP member", source_member in names and data == zf.read(source_member))
check("normalization excludes macOS resource forks", not any("__MACOSX" in str(p) for p in RAW.rglob("*")))
check("normalization excludes large UDS sweep duplication", not any("uds-sweep" in str(p) for p in RAW.rglob("*")))

print("\n== target identity and acquisition route ==")
cf = CODEFLASH.read_bytes()
check("CodeFlash range is exactly 2 MiB", len(cf) == 0x200000)
check("CodeFlash source hash is exact", sha(cf) == CODEFLASH_SHA)
check("upper 1 MiB is acquisition padding", cf[0x100000:] == b"\xff" * 0x100000)
check("normalized first 1 MiB hash is pinned", sha(cf[:0x100000]) == NORMALIZED_SHA)
check("boot-info identifies R7F701383", cf[0x180:0x1A8] == b"BOOT INFO AREA  R7F701383       72114350")
check("ECU serial is exact", cf[0xA4DC:0xA4F0] == b"8965012N50E12H030731")
check("raw 0x17D80 ID is 8965H1213000", cf[0x17D80:0x17D8C] == b"8965H1213000")
check("raw 0x17DC0 ID is 8A3111213000", cf[0x17DC0:0x17DCC] == b"8A3111213000")
check("raw 0x20860 ID is 8965F1208000", cf[0x20860:0x2086C] == b"8965F1208000")
preflight = json.loads((SESSION / "preflight_8965012N50E12H030731_20260821-151149.json").read_text())
route = json.loads((SESSION / "route.json").read_text())
sa = json.loads((SESSION / "security_access_log.json").read_text())
check("preflight observed exact F181 pair", preflight["identity"]["app_sw_id"] == "8965F12080008A3111213000")
check("preflight observed exact ECU serial", preflight["identity"]["ecu_serial"] == "8965012N50E12H030731")
check("corrected route is bus1/param1", route["bus"] == 1 and route["param"] == 1 and preflight["route"] == {"bus": 1, "param": 1})
check("corrected direct route opened programming", preflight["stages"]["programming"] == "opened")
check("corrected direct route got seed and unlocked", preflight["stages"]["seed"] == "received" and preflight["stages"]["unlock"] == "accepted")
attempts = sa["ecus"]["8965012N50E12H030731"]["attempts"]
check("SecurityAccess log includes accepted CodeFlash acquisition", any(a["caller"] == "dump_range:codeflash" and a["outcome"] == "accepted" for a in attempts))
check("SecurityAccess log includes both LocalRAM views", {a["caller"] for a in attempts} >= {"dump_range:local_ram_pe1", "dump_range:local_ram_self"})

print("\n== independent third-specimen XCP/handoff recurrence ==")
h = H_CODEFLASH.read_bytes()
check("comparison image is exact albino 2-MiB range", len(h) == 0x200000 and sha(h) == "97f9d42d936b97a99e7ab3d3ef20c6fb4c1fc3cc2ba199f6b158675a1709aee6")
same = sum(a == b for a, b in zip(cf, h))
check("same-address H-family equality count is exact", same == 2_094_962, f"{same}/2097152")
critical = {
    "generic XCP opcode map": (0x22A48, 41),
    "18 XCP callback words": (0x22A74, 18 * 4),
    "XCP LocalRAM bounds": (0x229C4, 16),
    "XCP five exclusion intervals": (0x28F0C, 5 * 8),
    "XCP shadow geometry": (0x2AE00, 12),
    "application programming handoff": (0x5F208, 48),
    "boot entry stub": (0x9F00, 100),
    "retained-state copier": (0x1472, 20),
    "reset-only initializer": (0x13E8, 116),
}
for label, (off, size) in critical.items():
    check(f"{label} is byte-identical to tracked H image", cf[off:off+size] == h[off:off+size])
check("XCP GET_SEED and UNLOCK commands remain unconfigured", cf[0x22A48 + (0xFF - 0xF8)] == 0 and cf[0x22A48 + (0xFF - 0xF7)] == 0)
check("boot stub still establishes SP FEBE8000 / GP FEBF9800", cf[0x9F44:0x9F50] == bytes.fromhex("23060080befe24060098bffe"))
check("boot stub still loads TP 867C and clears MPM", cf[0x9F50:0x9F5A] == bytes.fromhex("25067c860000e0072028"))
check("boot entry reaches retained-state copier directly", cf[0x9F5E:0x9F62] == bytes.fromhex("bfff1475"))

print("\n== acquisition repeatability preserved ==")
dfs = [(SESSION / n).read_bytes() for n in MEMBERS if n.startswith("dump_dataflash_")]
physical_diffs = []
for a, b in itertools.combinations(dfs, 2):
    physical_diffs.append(sum(x != y for x, y in zip(a[:0x8000], b[:0x8000])))
check("all three DataFlash reads are distinct", len({sha(x) for x in dfs}) == 3)
check("first-32KiB DataFlash pairwise diffs are pinned", physical_diffs == [2860, 3017, 2934], repr(physical_diffs))
pe = (SESSION / "dump_local_ram_pe1_febe0000_fec00000_20260821-151834.bin").read_bytes()
self_view = (SESSION / "dump_local_ram_self_fede0000_fee00000_20260821-152418.bin").read_bytes()
local_diff = sum(a != b for a, b in zip(pe, self_view))
check("PE1/self LocalRAM captures are complete 128-KiB views", len(pe) == len(self_view) == 0x20000)
check("different-time LocalRAM views retain exact observed diff", local_diff == 3678, str(local_diff))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
