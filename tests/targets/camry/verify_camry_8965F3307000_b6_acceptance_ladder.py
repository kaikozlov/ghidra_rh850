#!/usr/bin/env python3
"""Verify the exact-F33 B6 delivery/receive-health/controller-selection ladder.

Standalone section of the exact-F33 portable family; assertions are carried over verbatim.
"""
from __future__ import annotations

from tools import REPO_ROOT
def section_b6_acceptance_ladder() -> int:
    """Verify the exact-F33 B6 delivery/receive-health/controller-selection ladder."""

    import json
    import struct

    ROOT = REPO_ROOT
    IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
    CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"

    passed = failed = 0

    def check(name: str, condition: object, detail: str = "") -> None:
        nonlocal passed, failed
        ok = bool(condition)
        passed += int(ok)
        failed += int(not ok)
        print(f"[{'PASS' if ok else 'FAIL'}][b6_acceptance] {name}" + (f" ({detail})" if detail else ""))

    image = IMAGE.read_bytes()
    wanted = {
        0x4975C, 0x498E0, 0x4BD46, 0x58074, 0x8E772,
        0x90A48, 0x90B8A, 0x90D6A, 0xBCD62, 0xCEFA4, 0xCEFFC,
    }
    funcs: dict[int, dict] = {}
    with CORPUS.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("record") != "function":
                continue
            entry = int(rec["entry_addr"], 16)
            if entry in wanted:
                funcs[entry] = rec

    def refs(entry: int) -> set[tuple[str, str]]:
        return {(r["ref_type"], r["to_addr"].lower()) for r in funcs[entry].get("data_references", [])}

    def u16(off: int) -> int:
        return struct.unpack_from("<H", image, off)[0]

    def u32(off: int) -> int:
        return struct.unpack_from("<I", image, off)[0]

    print("== protected B6 / Gate-2 identity ==")
    check("SecOC record2 is CAN 0x0B6", u16(0x258F2) == 0x0B6)
    check("SecOC record2 is callback profile type2 with callback 0x90448",
          u16(0x25914) == 2 and u32(0x25918) == 0x00090448)
    check("stock Gate-2 terminal predicate is exact", image[0x8F952:0x8F956] == bytes.fromhex("e0d19a0d"))

    print("\n== failed-auth freshness history remains distinct from forced delivery ==")
    c90d6a = funcs[0x90D6A]["decompiled_c"]
    check("failure-marked callback condition is explicit",
          "param_2 == '\\x01'" in c90d6a)
    check("failure callback copies committed slot over pending slot",
          "-0x6224" in c90d6a and "-0x620c" in c90d6a and "FUN_00089f2e" in c90d6a)
    check("freshness reconstruction reads committed slot FEBE55DC",
          ("DATA", "0xfebe55dc") in refs(0x90A48))
    check("freshness candidate builder writes pending slot FEBE55F4",
          ("DATA", "0xfebe55f4") in refs(0x90B8A))

    print("\n== PDU44 receive-health provenance ==")
    check("status-map slot 0x1A points to PDU44",
          image[0x290B4:0x290BC] == bytes.fromhex("2c00000bb8010200"))
    check("status getter reads the monitored status array",
          ("DATA", "0xfebe7f0e") in refs(0x498E0))
    check("timeout/status helper is PDU-state backed",
          ("DATA", "0xfebe52d8") in refs(0x4975C))
    check("normal PDU receive indication clears the same PDU-state family",
          ("DATA", "0xfebe52d8") in refs(0x8E772) and
          "= 0;" in funcs[0x8E772]["decompiled_c"])
    check("B6 unpacker publishes status at FEBE80C9",
          ("WRITE", "0xfebe80c9") in refs(0x4BD46) and
          "FUN_000498e0(0x1a)" in funcs[0x4BD46]["decompiled_c"])
    check("B6 status stages FEBE80C9 -> FEBEF13E",
          ("READ", "0xfebe80c9") in refs(0x58074) and
          ("WRITE", "0xfebef13e") in refs(0x58074))
    check("B6 snapshot copies status and application target fields",
          ("READ", "0xfebef13e") in refs(0xBCD62) and
          ("WRITE", "0xfebeadb9") in refs(0xBCD62) and
          ("WRITE", "0xfebeadb0") in refs(0xBCD62) and
          ("WRITE", "0xfebeae90") in refs(0xBCD62))

    print("\n== controller-enable and ID11 bank selection ==")
    cefa4 = funcs[0xCEFA4]["decompiled_c"]
    check("CEFA4 reads B6 status snapshot and writes CAFF",
          ("READ", "0xfebeadb9") in refs(0xCEFA4) and
          ("WRITE", "0xfebecaff") in refs(0xCEFA4) and
          "puVar2[-0xa47] == '\\0'" in cefa4)
    ceff = funcs[0xCEFFC]["decompiled_c"]
    check("CEFFC requires ACBD=0 and CAFF=1",
          ("READ", "0xfebeacbd") in refs(0xCEFFC) and
          ("READ", "0xfebecaff") in refs(0xCEFFC) and
          "DAT_febeacbd == '\\0'" in ceff and "DAT_febecaff == '\\x01'" in ceff)
    check("CEFFC maps numeric Target Lateral ID 11 to bank2",
          "DAT_febeadb0 == '\\v'" in ceff and "DAT_febecb00 = 2;" in ceff and
          ("WRITE", "0xfebecb00") in refs(0xCEFFC))

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(section_b6_acceptance_ladder())
