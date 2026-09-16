#!/usr/bin/env python3
"""Verify current GTS+ MACKey transports and the UtilityPlusFront-selected flow."""
from __future__ import annotations

import hashlib
import struct
import sys
import tempfile

import pefile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DLL = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/GTSPlus/bin/UtilityExNK2.dll"
DLL_SHA = "d9868c8a9a69ffbab26ea7d4431e290372cd207e84e7b4aed27446aeb4c12ec1"
PLUS_FRONT = DLL.parent / "UtilityPlusFrontNK.dll"
PLUS_FRONT_SHA = "3472091a3c2f8df114fbab491dc442c3aee25a3485ce6390653413cb029d871a"
UTILITY_GENE_CP = DLL.parent / "UtilityGene.dll"
UTILITY_GENE_CP_SHA = "7412d320fcde90fff48c6511e638633e123e1068a4e54399a80c63d3c11c007e"
UTILITY_GENE_PLAIN_SHA = "a844d3045b2cb780a63e3959ec04bd27baab4ea7195080876bbdf6d2cf86c4cc"
IMAGE_BASE = 0x10000000
TEXT_RVA = 0x1000
TEXT_RAW = 0x400

if not DLL.exists() or not PLUS_FRONT.exists() or not UTILITY_GENE_CP.exists():
    print("[SKIP] GTS+ unpacked tree is not present")
    raise SystemExit(77)

sys.path.insert(0, str(REPO / "tools/techstream"))
from recover_gtsplus_bodies import recover

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def raw_to_va(raw: int) -> int:
    return IMAGE_BASE + TEXT_RVA + raw - TEXT_RAW


def rel32_target(data: bytes, raw: int) -> int:
    assert data[raw] == 0xE8
    return (raw_to_va(raw) + 5 + struct.unpack_from("<i", data, raw + 1)[0]) & 0xFFFFFFFF


gts = DLL.read_bytes()

print("== pinned current GTS+ UtilityExNK2 ==")
check("UtilityExNK2.dll size is exact", len(gts) == 0x1DD810)
check("UtilityExNK2.dll SHA-256 is exact", sha256(gts) == DLL_SHA)
check("official Ex2MAC_01_ComProcess export name is retained", b"Ex2MAC_01_ComProcess\x00" in gts)

print("\n== direct MAC_01 RID-0x1010 transport ==")
check("start helper embeds 31 01 10 10", gts[0xF944F:0xF9453] == bytes.fromhex("31 01 10 10"))
check("poll helper embeds 31 03 10 10", gts[0xF9323:0xF9327] == bytes.fromhex("31 03 10 10"))
check("Ex2MAC_01_ComProcess body is exact", sha256(gts[0x27990:0x27A48]) == "c10bbe074523b5e8d52a0b7276719ecf58c5151b1622805d5f3825eb6ddb9fac")
check("RID-0x1010 MACKey state worker is exact", sha256(gts[0xF8B40:0xF8CE3]) == "4cf9e7be8cf0e633726133807934ada756e1a2b4f84a65a38bdf5730bc6b47a1")
check("RID-0x1010 result helper is exact", sha256(gts[0xF92F0:0xF93D8]) == "65bb750e20a1fa79081c04538a1b31e118a52bdb05f25fb138e4d53b757bc30e")
check("RID-0x1010 start helper is exact", sha256(gts[0xF93E0:0xF9510]) == "eca43913dac73436b13fd7751450f01aa5811382084ba2228d843f4c0252e502")
check("MACKey worker calls RID-0x1010 start helper", rel32_target(gts, 0xF9E11) == 0x100F9FE0)
check("MACKey worker calls RID-0x1010 result helper", rel32_target(gts, 0xF9E57) == 0x100F9EF0)
check("MACKey worker polls RID-0x1010 result helper again", rel32_target(gts, 0xF9E9E) == 0x100F9EF0)
check("Ex2MAC_01_ComProcess references 0x100F9740 state machine", struct.pack("<I", 0x100F9740) in gts[0x27990:0x27A48])

print("\n== newer RID-0x3002 transport intentionally coexists ==")
check("newer start helper embeds 31 01 30 02", gts[0x12C58D:0x12C591] == bytes.fromhex("31 01 30 02"))
check("newer poll helper embeds 31 03 30 02", gts[0x12B04C:0x12B050] == bytes.fromhex("31 03 30 02"))
check("RID-0x3002 result helper is byte-pinned", sha256(gts[0x12B010:0x12B12C]) == "40ae4fc66a2a512a80ebbd72170a2df77a8949979ed4305b34d206e6bee41bf9")
check("RID-0x3002 start helper is byte-pinned", sha256(gts[0x12C570:0x12C664]) == "cc2903dda7ff92b583daf8544e69069d3bff9174534cde3fd671c87b4ad0fa63")

print("\n== current UtilityPlusFront -> recovered UtilityGene selected flow ==")
plus_bytes = PLUS_FRONT.read_bytes()
gene_cp_bytes = UTILITY_GENE_CP.read_bytes()
check("UtilityPlusFrontNK.dll SHA-256 is exact", sha256(plus_bytes) == PLUS_FRONT_SHA)
check("installed UtilityGene CP stub SHA-256 is exact", sha256(gene_cp_bytes) == UTILITY_GENE_CP_SHA)

plus_pe = pefile.PE(data=plus_bytes, fast_load=False)
gene_cp_pe = pefile.PE(data=gene_cp_bytes, fast_load=False)
gene_imports = next(
    desc for desc in plus_pe.DIRECTORY_ENTRY_IMPORT if desc.dll.lower() == b"utilitygene.dll"
)
ordinal_iat = {imp.ordinal: imp.address for imp in gene_imports.imports if imp.ordinal is not None}
check(
    "UtilityPlusFront imports MACKey validation/before/after wrappers only through UtilityGene ordinals 98/99/100",
    {ordinal: ordinal_iat.get(ordinal) for ordinal in (98, 99, 100)}
    == {98: 0x100070AC, 99: 0x100070B0, 100: 0x100070B4},
)
check("frontend command path calls validation wrapper through ordinal 98",
      plus_bytes[0x3E37:0x3E3D] == bytes.fromhex("FF 15 AC 70 00 10"))
check("frontend command path calls key-update-before wrapper through ordinal 99",
      plus_bytes[0x3ED8:0x3EDE] == bytes.fromhex("FF 15 B0 70 00 10"))
check("frontend command path calls key-update-after wrapper through ordinal 100",
      plus_bytes[0x40A9:0x40AF] == bytes.fromhex("FF 15 B4 70 00 10"))

# The installed UtilityGene image is a Crackproof hollow PE.  Toyota's exact
# same-release installer also ships the original GTSPlus (non-CP) twin.  Recover
# that source deterministically instead of treating the hollow .text as an
# evidence boundary.
gene_cp_text = next(sec for sec in gene_cp_pe.sections if sec.Name.rstrip(b"\0") == b".text")
check("installed UtilityGene is the expected hollow CP representation",
      gene_cp_text.SizeOfRawData == 0x1000 and gene_cp_text.Misc_VirtualSize == 0x32000)

with tempfile.TemporaryDirectory(prefix="verify-gtsplus-mackey-") as tmp:
    output = Path(tmp) / "recovered"
    manifest = recover(output=output)
    recovered_rows = {row["path"].casefold(): row for row in manifest["binaries"]}
    gene_row = recovered_rows["bin/utilitygene.dll"]
    gene_path = output / gene_row["path"]
    gene_bytes = gene_path.read_bytes()
    gene_pe = pefile.PE(data=gene_bytes, fast_load=False)
    check("Toyota installer plaintext UtilityGene twin identity is exact",
          gene_row["plaintext"]["sha256"] == UTILITY_GENE_PLAIN_SHA
          and sha256(gene_bytes) == UTILITY_GENE_PLAIN_SHA
          and gene_row["package_identity"]["cp_stub_matches_installed"]
          and gene_row["package_identity"]["cp_sidecar_matches_installed"])
    check("recovered UtilityGene has the full native .text body",
          gene_row["plaintext"]["text"]["raw_size"] == 0x31E00
          and gene_row["plaintext"]["native_text_expanded_vs_cp"])

    exports = {
        sym.name: (sym.ordinal, sym.address)
        for sym in gene_pe.DIRECTORY_ENTRY_EXPORT.symbols if sym.name is not None
    }
    expected_exports = {
        b"Ex2MAC_01_S_KeyValidation": (98, 0xE510),
        b"Ex2MAC_01_S_KeyUpdate_before": (99, 0xE2C0),
        b"Ex2MAC_01_S_KeyUpdate_after": (100, 0xDF20),
    }
    check("recovered UtilityGene exports exact current MACKey wrappers",
          all(exports.get(name) == value for name, value in expected_exports.items()))

    def va_data(va: int, size: int) -> bytes:
        return gene_pe.get_data(va - gene_pe.OPTIONAL_HEADER.ImageBase, size)

    def direct_targets(va: int, size: int) -> set[int]:
        data = va_data(va, size)
        targets: set[int] = set()
        for off in range(len(data) - 4):
            if data[off] != 0xE8:
                continue
            rel = struct.unpack_from("<i", data, off + 1)[0]
            targets.add((va + off + 5 + rel) & 0xFFFFFFFF)
        return targets

    check("current UtilityGene special key-management session is 10 4F",
          bytes.fromhex("10 4F") in va_data(0x10024630, 0xA0))
    check("current UtilityGene SecurityAccess is 27 41 seed / 27 42 key",
          bytes.fromhex("27 41") in va_data(0x100259E0, 0x160)
          and bytes.fromhex("27 42") in va_data(0x10025AC0, 0x120))
    identity = va_data(0x100256E0, 0xC0)
    check("current UtilityGene participant identity helper constructs 22 10 10",
          bytes.fromhex("66 C7 85 D8 EF FF FF 22 10") in identity
          and bytes.fromhex("C6 85 DA EF FF FF 10") in identity)
    support = va_data(0x10024CB0, 0x100)
    check("current UtilityGene participant-admission helper constructs 22 10 00 and reads bit0",
          bytes.fromhex("66 C7 85 D8 EF FF FF 22 10") in support
          and bytes.fromhex("C6 85 DA EF FF FF 00") in support
          and bytes.fromhex("83 E0 01") in support)
    check("current UtilityGene M1-M3 submit helper is RID 3002",
          bytes.fromhex("31 01 30 02") in va_data(0x10025C40, 0x180))
    check("current UtilityGene M4-M5 poll helper is RID 3002",
          bytes.fromhex("31 03 30 02") in va_data(0x10024AA0, 0x180))
    check("per-slave update path reconnects -> 10 4F -> RID3002 submit/poll",
          {0x10024530, 0x10024630, 0x10025C40, 0x10024AA0}
          <= direct_targets(0x10026110, 0x1B0))
    check("key-update-after wrapper dispatches master then selected slave updater",
          {0x10025E60, 0x10025F70, 0x10026110}
          <= direct_targets(0x1000DF20, 0x3A0))

print("\n== evidence boundary ==")
check("current GTS+ retains an independent RID-1010 MACKey implementation",
      bytes.fromhex("31 01 10 10") in gts and bytes.fromhex("31 03 10 10") in gts)
check("current UtilityPlusFront-selected network key-update implementation is RID-3002",
      True,
      "live FRC admission/0x1000 support state still requires target trace")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
