#!/usr/bin/env python3
"""Verify the bounded asynchronous/persistent WDBI DID 0x0204 maintenance cone."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = ROOT / "data/generated/decompilations.jsonl"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def sha(addr: int, size: int) -> str:
    return hashlib.sha256(CF[addr:addr + size]).hexdigest()


def branch(addr: int) -> tuple[str, int] | None:
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    hi = w0 & 0x3F
    if hi & 0x20:
        hi -= 0x40
    return ("jarl" if reg2 else "jr", addr + (hi << 16) + w1)


records: dict[int, dict] = {}
for line in CORPUS.open():
    record = json.loads(line)
    if record.get("record") == "function":
        records[int(record["entry_addr"], 16)] = record


def direct_refs(addr: int) -> set[int]:
    out: set[int] = set()
    for ref in records[addr].get("data_references", []):
        target = ref.get("to_addr", "")
        if target.startswith("0x"):
            out.add(int(target, 16))
    return out


print("== WDBI 0204 membership and request split ==")
rows = {row["did"]: row for row in csv.DictReader((ROOT / "data/application_wdbi_surface.csv").open(newline=""))}
row = rows["0x0204"]
check("0204 is the two-byte WDBI member", row["payload_len"] == "2" and row["start_callback"] == "0x4EC16" and row["result_callback"] == "0x4EC2A")
check("0204 is sessions 2/3, SecurityAccess-free, vehicle-speed gated", row["sessions"] == "2,3" and row["security_access_required"] == "0" and row["speed_gate"] == "1")
check("0204 start gate body is pinned", sha(0x4EC16, 20) == "bb3ee890414c93d5d48fe96fd1151c95e507740e32eb0d00a75c2f2a1e08ac23")
check("0204 result body is pinned", sha(0x4EC2A, 28) == "400a129b2f6e6cb6de1df28868ce698dcebabd462de098d7b5b26a3a9c1282ce")
check("result defaults to state 0x21 and tests payload-byte-1 bit 7", CF[0x4EC2A:0x4EC34] == bytes.fromhex("200e2100c6ff0100a205"))
check("set bit converts 0x21 to 0x11", CF[0x4EC34:0x4EC36] == bytes.fromhex("500a"))
check("result stores state and shared pending tag 0x2E10", CF[0x4EC36:0x4EC44] == bytes.fromhex("24f64cc902529b0b200e102e8f0c"))
check("result returns Dcm pending status 2", CF[0x4EC3A:0x4EC3C] == bytes.fromhex("0252"))

print("\n== Dcm pending worker and two application modes ==")
check("shared 0x2E pending dispatcher is pinned", sha(0x4C3CA, 86) == "63aa7e4748748ccac6d46030ab58825e5e9b67e3117baa978e5ed6e01a6bb754")
check("0204 pending worker body is pinned", sha(0x4EBBC, 58) == "b3913138d8a22bd61e26233cca962ff81841bcff8d978ed7a3f3d1b6eccacc1e")
check("state 0x11 calls 35582", branch(0x4EBCA) == ("jarl", 0x35582))
check("state 0x11 writes application mode 0x11 through FDE08", CF[0x4EBCE:0x4EBD6] == bytes.fromhex("203611008aff36f2") and branch(0x4EBD2) == ("jarl", 0xFDE08))
check("state 0x11 advances Dcm state to 0x12", CF[0x4EBD6:0x4EBDA] == bytes.fromhex("200e1200"))
check("state 0x21 writes application mode 0x22 through FDE08", CF[0x4EBE2:0x4EBEA] == bytes.fromhex("203622008aff22f2") and branch(0x4EBE6) == ("jarl", 0xFDE08))
check("state 0x21 advances Dcm state to 0x22", CF[0x4EBEA:0x4EBEE] == bytes.fromhex("200e2200"))
check("mode helper 35582 is pinned", sha(0x35582, 52) == "2c2a4fb92de73ac8d7b2178beeced784c17f54add185c08d205524f493991dce")
check("FDE08 thunk is pinned", sha(0xFDE08, 8) == "68bfb2e96f05cec57e51d4d1b8e0c08b27b83e128b7c6d5584c0d98b9b580b5e")
check("FDE08 thunk targets B7F7C", CF[0xFDE08:0xFDE10] == bytes.fromhex("2c067c7f0b006c00"))
check("B7F7C is a six-byte FEBEAF47 setter", sha(0xB7F7C, 6) == "bf8c503dc3d081353476e18e7826bdffc9424689dd9d4ca6552a8167a401043a")

print("\n== object-7 mode-latch persistence handshake ==")
check("operational mode worker is pinned", sha(0xB7E6E, 182) == "bf7950266f1d10f78fc58f7fee440f858576f5a366843d7b40ab5706d0940dc1")
check("object-7 persistence helper is pinned", sha(0xB7E4A, 36) == "a2a3731ecac0740853ff44e414cd5cd3dc5580bdd5042c3a27e04c6cca8d2d22")
check("B7E4A submits literal object 7 through FF09C", CF[0xB7E5C:0xB7E66] == bytes.fromhex("07320305800b84ff3a72") and branch(0xB7E62) == ("jarl", 0xFF09C))
check("NvM status worker is pinned", sha(0xB7F4C, 48) == "b44d7baf3a6e2bce8997a14eca5a7eb1670702392a771952ba44b5cc7e537faa")
check("B7F4C polls literal object 7 status", CF[0xB7F5C:0xB7F62] == bytes.fromhex("073284ff6671") and branch(0xB7F5E) == ("jarl", 0xFF0C4))
check("completion helper is pinned", sha(0xB7F24, 40) == "a72d66663456e5d78e09d821e1c0e556cb238ab867e65723379293bbbb661d5f")
check("completion helper reports selector 0x12 through C430", CF[0xB7F40:0xB7F48] == bytes.fromhex("2036120084ffbc6c") and branch(0xB7F44) == ("jarl", 0xFEC00))

persist_rows = list(csv.DictReader((ROOT / "data/object15_reachability.csv").open(newline="")))
def persisted(caller: str, obj: int) -> bool:
    return any(r["caller_addr"] == caller and r["object_index"] == str(obj) and r["async_persist_behavior"] == "checkpoint_persist" for r in persist_rows)
check("B7E4A is independently classified as checkpoint object 7 persistence", persisted("0xB7E4A", 7))

print("\n== branch-specific post-response queue operation 6 ==")
check("Dcm completion dispatcher is pinned", sha(0x4EBF6, 32) == "a7542561f3b8a22053950c5784e1c0cc794a123d1c80d3bb0c4a116224a67675")
check("state 0x12 clears without queue operation", CF[0x4EBFE:0x4EC04] == bytes.fromhex("0106eeffe205"))
check("state 0x22 uniquely calls queue starter 50922 before clearing", CF[0x4EC04:0x4EC12] == bytes.fromhex("0106deffda0580ff181d440767c9") and branch(0x4EC0A) == ("jarl", 0x50922))
check("queue starter body is pinned", sha(0x50922, 116) == "72008c7894efd52ba593be71718a362347ac7d8dd9081211572bc997ea7f5b64")
check("idle queue starter sets operation 6 then calls initializer", CF[0x5092E:0x5093C] == bytes.fromhex("060a440f8cca bfffb2ff c43f8cca".replace(" ", "")) and branch(0x50934) == ("jarl", 0x508E6))
check("operation-6 initializer is pinned", sha(0x508E6, 60) == "42961c51463fa34a1645d7daf2aeb181a0bf6821ca12bbc813bddd3680966e38")
expected_calls = [0xFDFE8,0x539A8,0x390E6,0x453A2,0xFDDF4,0xFDDE0,0x546E2,0x505F8,0x51524,0x52016,0x53626,0x5062A]
call_sites = [0x508EA,0x508EE,0x508F2,0x508F6,0x508FA,0x508FE,0x50902,0x50908,0x5090C,0x50910,0x50914,0x5091A]
actual_calls = [branch(site)[1] if branch(site) else None for site in call_sites]
check("operation-6 initializer has exact 12-callee fan-out", actual_calls == expected_calls, repr([hex(x) if x else None for x in actual_calls]))
check("normal queue scheduler body is pinned", sha(0x50B22, 24) == "44666d287fbc50489cf37b72a9452b1987da05fe742ec259ddd18ab051db2d1a")
check("operation-6 completion monitor is pinned", sha(0x50A1C, 204) == "89683a882b55a0255bf1e379ac3ad1c18c7e4d377bad600a711e1258a0159dbb")

print("\n== queue operation 6 resets/persists checkpoint groups ==")
for caller, obj, label in [
    ("0xBAFB2", 9, "runtime-condition snapshot"),
    ("0xBB3C6", 11, "two-channel state"),
    ("0x453A2", 12, "dual-incident snapshot"),
    ("0x539A8", 14, "condition-history"),
    ("0xBB5EC", 15, "operating-state snapshot"),
]:
    check(f"operation-6 fan-out persists checkpoint object {obj} ({label})", persisted(caller, obj))
check("operation-6 live-state clear helper 390E6 is pinned", sha(0x390E6, 14) == "a4d8238da30f44a19cd69f4974774492048b0b719ff4cbe714acdd24612ef99c")

print("\n== bounded separation from direct steering-current/PWM actuation ==")
command_states = {
    0xFEBE7F94,0xFEBEF184,0xFEBEAE20,0xFEBEBF80,0xFEBEBF84,0xFEBEBF9A,0xFEBEBFA2,0xFEBEACFF,
    0xFEBEAE60,0xFEBEBFF0,0xFEBEC0BE,0xFEBEC0C8,0xFEBEC0D6,0xFEBEC144,0xFEBEC170,0xFEBEC1B8,
    0xFEBEC1B4,0xFEBEC1BC,0xFEBEC1D4,0xFEBEB788,0xFEBEB87E,0xFEBEAE16,0xFEBEAE6E,
    0xFEBE6D18,0xFEBE6D1C,0xFEBE6D28,0xFEBE6D2A,
}
audit_functions = [
    0x4EC2A,0x4EBBC,0x35582,0xB7F7C,0xB7E6E,0xB7E4A,0xB7F4C,0xB7F24,0x4EBF6,0x50922,0x508E6,
    0xBB210,0x539A8,0x390E6,0x453A2,0xBB5EC,0xBB3C6,0x546E2,0x505F8,0x51524,0x52016,0x53626,0x5062A,
]
missing = [hex(a) for a in audit_functions if a not in records]
check("all recovered 0204/operation-6 boundary functions exist in corpus", not missing, repr(missing))
hits: list[str] = []
for addr in audit_functions:
    for target in sorted(direct_refs(addr) & command_states):
        hits.append(f"{addr:06X}->{target:08X}")
check("0204 + operation-6 direct data refs do not join conditioned command or d/q state", not hits, repr(hits))
check("independent motor actuation oracle is present", (ROOT / "tests/verify_motor_actuation_boundary.py").is_file())
check("surface matrix classifies 0204 as persistent maintenance/reset", row["side_effect_class"] == "persistent_maintenance_reset")

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
