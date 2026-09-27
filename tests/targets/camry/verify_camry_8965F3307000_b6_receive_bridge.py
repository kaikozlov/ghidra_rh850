#!/usr/bin/env python3
"""Verify the exact-F33 ABI-preserving protected-B6 receive bridge.

Standalone section of the exact-F33 portable family; assertions are carried over verbatim.
"""
from __future__ import annotations

from tools import REPO_ROOT
def section_b6_receive_bridge() -> int:
    """Verify the exact-F33 ABI-preserving protected-B6 receive bridge."""
    import hashlib, json, struct

    ROOT = REPO_ROOT
    from exploit.ephemeral_runtime import build_camry_f33_b6_bridge as bridge_builder
    BRIDGE_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_bridge.bin"
    BRIDGE_AUDIT = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_b6_bridge_build.json"
    BRIDGE_SOURCE = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_bridge.S"
    IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
    p = f = 0

    def sha(b: bytes) -> str:
        return hashlib.sha256(b).hexdigest()

    def check(name: str, cond: object) -> None:
        nonlocal p, f
        ok = bool(cond); p += int(ok); f += int(not ok); print(f"[{'PASS' if ok else 'FAIL'}] {name}")

    audit = json.loads(BRIDGE_AUDIT.read_text())
    img = IMAGE.read_bytes()
    blob = BRIDGE_BIN.read_bytes()

    print("== audited ABI-preserving bridge ==")
    check("audited bridge source identity exact",
          audit["source"]["sha256"] == sha(BRIDGE_SOURCE.read_bytes()))
    check("staging/resident fit exact retained geometry",
          audit["staging"]["size"] == len(blob) == 648 and
          audit["staging"]["sha256"] == sha(blob) and audit["staging"]["relocations"] == 0 and
          audit["resident"]["base"] == "0xFEBFF9F0" and audit["resident"]["size"] == 520 and
          audit["resident"]["headroom"] == 4 and audit["resident"]["relocations"] == 0 and
          audit["resident"]["end_limit"] == "0xFEBFFBFC")
    expected_targets = [
        *bridge_builder.EXPECTED_RESIDENT_JARL_TARGETS[:29],
        bridge_builder.B6_COM_RX_CALLBACK,
        *bridge_builder.EXPECTED_RESIDENT_JARL_TARGETS[29:],
    ]
    check("direct JARL sequence preserves ABI and inserts route44 after aggregate",
          audit["resident"]["jarl_targets"] == [f"0x{x:08X}" for x in expected_targets] and
          audit["resident"]["jarl_targets"][28:31] == ["0x000667E6", "0x0007D72C", "0x00071378"])
    check("mailbox is low-RAM v3",
          audit["mailbox"]["base"] == "0xFEBF0000" and audit["mailbox"]["size"] == 0x30 and
          audit["mailbox"]["magic"] == "0x42364252" and audit["mailbox"]["version"] == 3)

    print("== static pins re-derived from firmware ==")
    def u16(va: int) -> int:
        return struct.unpack_from("<H", img, va)[0]
    def u32(va: int) -> int:
        return struct.unpack_from("<I", img, va)[0]
    pins = {k: int(v, 16) for k, v in audit["static_pins"].items()}
    check("builder re-derives every audited pin", bridge_builder.verify_static_pins(img) == pins)
    check("PDU44 COM window exact",
          u16(0x22840 + 44 * 2) == 0x1B7 and pins["B6_COM_WINDOW"] == 0xFEBE4BFF)
    check("B6 secured buffer/profile geometry exact",
          u32(0x2586C + 2 * 0x50) == 32 and u32(0x25870 + 2 * 0x50) == 40 and
          (u32(0x25874 + 2 * 0x50) & 0xFFFF) == 2 and pins["B6_SECURED_BUFFER"] == 0xFEBE54D4)
    check("B6 queue and native route44 callback exact",
          pins["B6_QUEUE_RECORD"] == 0xFEBE547A and pins["B6_IPDU_FLAG"] == 0xFEBE5364 and
          pins["B6_COM_RX_CALLBACK"] == 0x0007D72C and u32(0x21E08) == 0x0007D72C)

    print("== physical ingress through protected route ==")
    d7_rule = img[0x230B8 + 36 * 16:0x230B8 + 37 * 16]
    b6_rule = img[0x230B8 + 39 * 16:0x230B8 + 40 * 16]
    check("RSCFD rule39 is exact B6 peer of protected D7 rule36",
          d7_rule == bytes.fromhex("d700000000002d000200000000000000") and
          b6_rule == bytes.fromhex("b6000000000030000200000000000000") and d7_rule[8:] == b6_rule[8:])
    check("CanIf descriptor39 is FD B6/32 and maps route 44",
          img[0x21FE8 + 39 * 8:0x21FE8 + 40 * 8] == bytes.fromhex("b600004020000000") and
          img[0x21A48] == 5 and 5 + 39 == 44 and img[0x21FB8 + 44] == 0x10)
    check("normal RX descriptors share the same CanIf path",
          img[0x219DC:0x219DC + 43] == b"\x01" * 43)
    check("protected routes 9/41/44 pass through SecOC while route40 is direct COM",
          [(u16(0x229CE + route * 4), u16(0x229D0 + route * 4)) for route in (9, 41, 44)] ==
          [(9, 9), (41, 41), (44, 44)] and
          (u16(0x229CE + 40 * 4), u16(0x229D0 + 40 * 4)) == (40, 0xFFFF) and
          u32(0x21E48) == 0x8EE7C and u32(0x21E08) == 0x7D72C)

    print(f"\nResults: {p} passed, {f} failed")
    return 1 if f else 0


if __name__ == "__main__":
    raise SystemExit(section_b6_receive_bridge())
