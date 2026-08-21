#!/usr/bin/env python3
"""Verify the generated, representation-bounded Techstream crypto inventory."""
from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TREE = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics"
ARTIFACT = REPO / "data/generated/techstream_v18/crypto_inventory.json"
inventory = json.loads(ARTIFACT.read_text(encoding="utf-8"))
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    passed += bool(condition)
    failed += not condition
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


print("== search boundary and negative semantics ==")
required_representations = {
    "raw", "ascii_plaintext", "hex_ascii_upper", "hex_ascii_lower",
    "utf16le_plaintext", "utf16le_hex_upper", "utf16le_hex_lower",
    "bitwise_inverted_raw", "bitwise_inverted_ascii_plaintext",
}
boundary = inventory["scan_boundary"]
check("whole extracted distribution is enumerated", boundary["file_count"] == 6620)
check("all required representation classes are declared",
      required_representations <= set(boundary["representations"]))
check("absence language declares symbolic-execution limitation",
      "No general symbolic execution" in boundary["limitations"])
check("both Sienna secrets absent in enumerated representations",
      inventory["sienna_secret_absence"] == {
          "SIENNA_APPLICATION_SA_SECRET": True,
          "SIENNA_BOOT_SEED_KEY_SECRET": True,
      })


print("\n== IT3ACNK regression anchors ==")
hits = inventory["hits"]


def select(value_id: str, artifact_suffix: str, representation: str | None = None):
    return [hit for hit in hits
            if hit["value_id"] == value_id
            and hit["artifact"].endswith(artifact_suffix)
            and (representation is None or hit["representation"] == representation)]


bcva_it3 = select("BCVA_IT3", "IT3ACNK.dll", "raw")
check("IT3ACNK raw bCVa constant is at file offset/RVA 0x8020",
      len(bcva_it3) == 1 and bcva_it3[0]["file_offset"] == 0x8020
      and bcva_it3[0]["rva"] == 0x8020)
check("IT3ACNK bCVa constant is not promoted to a key without a reference",
      bcva_it3[0]["confidence"] == "bounded-unreferenced-constant"
      and bcva_it3[0]["references"] == [])
fuku_it3 = select("FUKUMORIYOSIYAMA", "IT3ACNK.dll", "hex_ascii_upper")
check("IT3ACNK hex FUKUMORI constant is at 0x834C",
      len(fuku_it3) == 1 and fuku_it3[0]["file_offset"] == 0x834C)
check("EncryptAds directly pushes the FUKUMORI constant at RVA 0x2BE1",
      fuku_it3[0]["references"] == [{
          "containing_export": "EncryptAds",
          "file_offset": 0x2BE1,
          "reference_kind": "push_imm32",
          "rva": 0x2BE1,
          "va": 0x10002BE1,
      }])
check("IT3ACNK FUKUMORI use is classified as recovered key consumption",
      fuku_it3[0]["confidence"] == "recovered-key-consumption")


print("\n== corrected host mappings ==")
fuku_artifacts = {hit["artifact"] for hit in hits if hit["value_id"] == "FUKUMORIYOSIYAMA"}
bcva_artifacts = {hit["artifact"] for hit in hits if hit["value_id"] == "BCVA_IT3"}
check("FUKUMORI host map includes IT3ACNK and UtilityEx2TY",
      {"Techstream/bin/IT3ACNK.dll", "Techstream/bin/UtilityEx2TY.dll"} <= fuku_artifacts)
check("bCVa host map includes IT3ACNK and IT3UtilityNeoNK",
      {"Techstream/bin/IT3ACNK.dll", "Techstream/bin/IT3UtilityNeoNK.dll"} <= bcva_artifacts)
constructed = inventory["constructed_immediate_hits"]
constructed_by_function = {item["function"]: item for item in constructed}
check("CommandCommon constructed/inverted FUKUMORI path is locked",
      constructed_by_function["CSecurityAccessAES128::CancelSecurity"]["anchors_valid"]
      and constructed_by_function["CSecurityAccessAES128::CancelSecurity"]["decoded_value"]
      == "FUKUMORIYOSIYAMA")
check("CommandCommon constructed/inverted gateway path is locked",
      constructed_by_function["CSecurityAccessCGW_DK::CancelSecurity"]["anchors_valid"]
      and constructed_by_function["CSecurityAccessCGW_DK::CancelSecurity"]["decoded_value"]
      == "5622e4993876de4f15f2e166e7cd24c6")


print("\n== IT3UtilityNeoNK AES-256 live-use anchors ==")
neo_path = TREE / "Techstream/bin/IT3UtilityNeoNK.dll"
if neo_path.is_file():
    neo = neo_path.read_bytes()
    neo_key = b"bCVaAQnA3fNdDgdls2Cjar5er8iwP4Xz"
    check("NeoNK full 32-byte key literal plus NUL is exact at 0x3A7D4",
          neo[0x3A7D4:0x3A7D4 + 33] == neo_key + b"\x00")
    check("NeoNK wrapper strlen-loads and pushes the same key VA",
          neo[0x23F3B:0x23F40] == bytes.fromhex("bfd4a70310")
          and neo[0x23F47:0x23F4C] == bytes.fromhex("f2aef7d149")
          and neo[0x23F5A:0x23F5F] == bytes.fromhex("68d4a70310"))
    # 0x10024050 dispatches on key_length-16. The selector table maps offsets
    # 0,8,16 (lengths 16,24,32) to the AES-128/192/256 setup arms.
    key_dispatch = struct.unpack_from("<4I", neo, 0x24254)
    key_selectors = neo[0x24264:0x24264 + 17]
    check("NeoNK key schedule arms are 16/24/32-byte selectors",
          key_dispatch[:3] == (0x1002407A, 0x10024082, 0x10024089)
          and [key_selectors[i] for i in (0, 8, 16)] == [0, 1, 2])
    check("NeoNK 32-byte strlen result selects AES-256 setup arm",
          len(neo_key) == 32 and key_selectors[len(neo_key) - 16] == 2)
    check("NeoNK decrypt wrapper iterates one 0x10024460 call per 16-byte block",
          neo[0x23F6B:0x23F82] == bytes.fromhex(
              "c1eb048bfb74488d5424248d442414525056e8de040000"))
    check("0x10023F26 is only the pre-decrypt 16-byte alignment test",
          neo[0x23F26:0x23F2B] == bytes.fromhex("f6c30f740e"))
    check("post-decrypt tail trim uses only final-byte count, not strict PKCS7 validation",
          neo[0x24001:0x24035] == bytes.fromhex(
              "8a4437ff884424108b4c241081e1ff0000003bce77238bc62bc13bc67316"
              "8bce03f82bc833c08bf1c1e902f3ab8bce83e103f3aa"))
else:
    print("[SKIP] IT3UtilityNeoNK.dll unavailable; live-use byte anchors not executed")


print("\n== IT3ACNK export classification ==")
analysis = inventory["it3acnk_analysis"]
expected_exports = {
    "DecryptTd3", "EncryptAds", "EncryptCM", "EncryptSecretKeyC",
    "EncryptSecretKeyN", "EncryptSecurityVer1Smrt", "EncryptSecurityVer1Str",
    "EncryptSecurityVer2Smrt", "EncryptSecurityVer2Str", "EncryptTd3",
    "GenerateKeyS", "GenerateSecurityKey6Byte",
}
by_export = {entry["name"]: entry for entry in analysis["exports"]}
check("all twelve crypto exports are classified", set(by_export) == expected_exports)
check("every export has a pinned nonempty extent hash",
      all(entry["extent_size"] > 0 and len(entry["extent_sha256"]) == 64
          and entry["classification"] for entry in by_export.values()))
check("EncryptAds classification identifies FUKUMORI and block helper",
      "FUKUMORIYOSIYAMA" in by_export["EncryptAds"]["classification"]
      and "0x3070" in by_export["EncryptAds"]["classification"])
known = {item["rva"]: item for item in analysis["known_constants"]}
check("IT3ACNK constant inventory distinguishes all direct/unreferenced pools",
      set(known) == {0x8020, 0x8030, 0x82FC, 0x8310, 0x8324, 0x834C})

print("\n== publication regression language ==")
report = (REPO / "docs/tooling/techstream.md").read_text(encoding="utf-8")
findings = (REPO / "docs/status/FINDINGS.md").read_text(encoding="utf-8")
check("keyless IT3ACNK claim is absent",
      "IT3ACNK.dll` has an AES S-box but no recoverable key" not in report)
check("report names direct EncryptAds reference",
      "RVA `0x2BE1`" in report and "representation-bounded" in report.lower())
check("NeoNK report keeps AES-256 result and rejects old PKCS7-gate wording",
      "AES-256-ECB keyed by the full 32-character string" in report
      and "not a strict PKCS#7 padding validator" in report
      and "with PKCS#7 gating at `0x10023F26`" not in report)
check("TMS-012 no longer claims complete absence or exhaustive search",
      "TMS-012 | Full-tree binary sweep" not in findings
      and "recovered (bounded negative)" in findings)


if TREE.is_dir():
    print("\n== byte-identical live regeneration ==")
    with tempfile.TemporaryDirectory(prefix="crypto-inventory-") as directory:
        output = Path(directory) / "crypto_inventory.json"
        completed = subprocess.run(
            [sys.executable, str(REPO / "tools/techstream/generate_crypto_inventory.py"),
             "--root", str(TREE), "--output", str(output)],
            cwd=REPO, text=True, capture_output=True,
        )
        check("generator exits successfully", completed.returncode == 0, completed.stderr.strip())
        check("live regeneration is byte-identical", output.read_bytes() == ARTIFACT.read_bytes())
else:
    print("\n[SKIP] external Techstream tree unavailable; committed artifact checks still ran")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else (0 if TREE.is_dir() else 77))
