#!/usr/bin/env python3
"""Generate a representation-aware Techstream V18 crypto-constant inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import pefile

REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics"
DEFAULT_OUT = REPO / "data/generated/techstream_v18/crypto_inventory.json"

VALUES = {
    "FUKUMORIYOSIYAMA": bytes.fromhex("46554b554d4f5249594f534959414d41"),
    "CENTRAL_GATEWAY": bytes.fromhex("5622e4993876de4f15f2e166e7cd24c6"),
    "BCVA_IT3": b"bCVaAQnA3fNdDgdl",
    "SIENNA_BOOT_SEED_KEY_SECRET": bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044"),
    "SIENNA_APPLICATION_SA_SECRET": bytes.fromhex("893e08418c741ffa2a9c044bffa55813"),
}

AES_SBOX = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"
    "e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16"
)

IT3_CLASSIFICATIONS = {
    "EncryptSecretKeyC": "string-key transform using ASCII constant EnerGizerreLayXT; exact cipher helper semantics bounded",
    "EncryptSecretKeyN": "string-key transform using ASCII constant WgvbMXxN3pHsSndg; exact cipher helper semantics bounded",
    "EncryptSecurityVer1Smrt": "fixed-table version-1 security transform (Smrt); not the AES host-key path",
    "EncryptSecurityVer1Str": "fixed-table version-1 security transform (Str); not the AES host-key path",
    "EncryptSecurityVer2Smrt": "six-byte version-2 custom security transform through helper RVA 0x47A0",
    "EncryptSecurityVer2Str": "six-byte version-2 custom security transform through helper RVA 0x4A70",
    "EncryptTd3": "TD3 block transform using hex-ASCII constant at RVA 0x8324 and software block-cipher helper",
    "DecryptTd3": "TD3 inverse block transform using hex-ASCII constant at RVA 0x8324",
    "EncryptCM": "caller-supplied key/input block encryption path through software block-cipher helper RVA 0x3070",
    "EncryptAds": "hex-decodes FUKUMORIYOSIYAMA from RVA 0x834C and passes it to software block-cipher helper RVA 0x3070",
    "GenerateKeyS": "caller-input key-generation/block-transform path; no fixed key reference recovered",
    "GenerateSecurityKey6Byte": "six-byte custom security-key generator; separate from the 16-byte AES host-key exports",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def all_offsets(data: bytes, pattern: bytes) -> list[int]:
    if not pattern:
        return []
    offsets: list[int] = []
    start = 0
    while True:
        offset = data.find(pattern, start)
        if offset < 0:
            return offsets
        offsets.append(offset)
        start = offset + 1


def representations(value: bytes) -> dict[str, bytes]:
    result = {
        "raw": value,
        "hex_ascii_upper": value.hex().upper().encode("ascii"),
        "hex_ascii_lower": value.hex().lower().encode("ascii"),
        "utf16le_hex_upper": value.hex().upper().encode("utf-16le"),
        "utf16le_hex_lower": value.hex().lower().encode("utf-16le"),
    }
    if all(0x20 <= byte < 0x7F for byte in value):
        result["ascii_plaintext"] = value
        result["utf16le_plaintext"] = value.decode("ascii").encode("utf-16le")
    for name, pattern in list(result.items()):
        result[f"bitwise_inverted_{name}"] = bytes(byte ^ 0xFF for byte in pattern)
    return result


def pe_context(path: Path, data: bytes) -> tuple[pefile.PE | None, list[dict[str, Any]]]:
    if data[:2] != b"MZ":
        return None, []
    try:
        pe = pefile.PE(data=data, fast_load=False)
    except pefile.PEFormatError:
        return None, []
    exports: list[dict[str, Any]] = []
    if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if symbol.name:
                exports.append({"name": symbol.name.decode("ascii", "replace"), "rva": symbol.address})
    exports.sort(key=lambda item: item["rva"])
    return pe, exports


def containing_export(exports: list[dict[str, Any]], rva: int) -> str | None:
    prior = [item for item in exports if item["rva"] <= rva]
    return prior[-1]["name"] if prior else None


def direct_refs(pe: pefile.PE, data: bytes, exports: list[dict[str, Any]], target_va: int) -> list[dict[str, Any]]:
    needle = struct.pack("<I", target_va)
    refs: list[dict[str, Any]] = []
    for section in pe.sections:
        if not (section.Characteristics & 0x20000000):
            continue
        start = section.PointerToRawData
        end = start + section.SizeOfRawData
        for offset in all_offsets(data[start:end], needle):
            immediate_offset = start + offset
            rva = pe.get_rva_from_offset(immediate_offset)
            instruction_rva = rva - 1 if data[immediate_offset - 1:immediate_offset] == b"\x68" else rva
            refs.append({
                "file_offset": immediate_offset - (1 if instruction_rva != rva else 0),
                "rva": instruction_rva,
                "va": pe.OPTIONAL_HEADER.ImageBase + instruction_rva,
                "reference_kind": "push_imm32" if instruction_rva != rva else "absolute_imm32",
                "containing_export": containing_export(exports, instruction_rva),
            })
    return refs


def hit_confidence(name: str, relative: str, representation: str, refs: list[dict[str, Any]]) -> str:
    lower = relative.lower()
    if name == "FUKUMORIYOSIYAMA" and lower.endswith("it3acnk.dll") and representation.startswith("hex_ascii") and refs:
        return "recovered-key-consumption"
    if name == "BCVA_IT3" and lower.endswith("it3acnk.dll"):
        return "bounded-unreferenced-constant" if not refs else "recovered-reference"
    if name.startswith("SIENNA_"):
        return "negative-search-target"
    return "representation-hit"


def it3_export_inventory(root: Path) -> dict[str, Any]:
    path = root / "Techstream/bin/IT3ACNK.dll"
    data = path.read_bytes()
    pe, exports = pe_context(path, data)
    assert pe is not None
    text_end = max(
        section.VirtualAddress + section.Misc_VirtualSize
        for section in pe.sections
        if section.Characteristics & 0x20000000
    )
    entries = []
    for index, export in enumerate(exports):
        start = export["rva"]
        end = exports[index + 1]["rva"] if index + 1 < len(exports) else text_end
        start_off = pe.get_offset_from_rva(start)
        end_off = pe.get_offset_from_rva(end - 1) + 1
        entries.append({
            "name": export["name"],
            "rva": start,
            "va": pe.OPTIONAL_HEADER.ImageBase + start,
            "extent_basis": "to next export (includes any padding/internal tail)",
            "extent_size": end - start,
            "extent_sha256": sha256(data[start_off:end_off]),
            "classification": IT3_CLASSIFICATIONS[export["name"]],
        })
    return {
        "artifact_sha256": sha256(data),
        "image_base": pe.OPTIONAL_HEADER.ImageBase,
        "known_constants": [
            {"file_offset": 0x8020, "rva": 0x8020, "value": "bCVaAQnA3fNdDgdl", "role": "unreferenced printable constant; key use not established"},
            {"file_offset": 0x8030, "rva": 0x8030, "value": "s2Cjar5er8iwP4Xz", "role": "adjacent unreferenced printable constant; key use not established"},
            {"file_offset": 0x82FC, "rva": 0x82FC, "value": "EnerGizerreLayXT", "role": "directly referenced by EncryptSecretKeyC"},
            {"file_offset": 0x8310, "rva": 0x8310, "value": "WgvbMXxN3pHsSndg", "role": "directly referenced by EncryptSecretKeyN"},
            {"file_offset": 0x8324, "rva": 0x8324, "value": "41668F1FFE83E0FE0CAFDF4676102660", "role": "hex-ASCII key material directly referenced by EncryptTd3/DecryptTd3"},
            {"file_offset": 0x834C, "rva": 0x834C, "value": "46554B554D4F5249594F534959414D41", "decoded": "FUKUMORIYOSIYAMA", "role": "hex-ASCII AES key directly referenced by EncryptAds"},
        ],
        "exports": entries,
    }


def constructed_immediate_hits(root: Path) -> list[dict[str, Any]]:
    """Lock independently decompiled x86 byte-immediate constructions.

    CommandCommon builds the inverted FUKUMORI key using AL/BL/CL/DL byte
    immediates plus stack stores, so no contiguous representation exists.
    These exact instruction anchors make that representation explicit.
    """
    path = root / "Techstream/bin/CommandCommon.dll"
    data = path.read_bytes()
    pe = pefile.PE(data=data)
    anchors = {
        0x90C43: "b0aa",
        0x90C4E: "b0a6",
        0x90C59: "b0be",
        0x90C67: "b2b0",
        0x90C6D: "b1b6",
        0x90CAC: "b3b2",
        0x90CC2: "c644240cb9",
        0x90CC9: "c644240eb4",
        0x90CCE: "c6442412ad",
        0x90CD3: "c6442416ac",
    }
    observed = {}
    for rva, expected in anchors.items():
        offset = pe.get_offset_from_rva(rva)
        observed[f"0x{rva:x}"] = data[offset:offset + len(bytes.fromhex(expected))].hex()
    valid = all(observed[f"0x{rva:x}"] == expected for rva, expected in anchors.items())
    results = [{
        "artifact": "Techstream/bin/CommandCommon.dll",
        "artifact_sha256": sha256(data),
        "function_rva": 0x90C40,
        "function": "CSecurityAccessAES128::CancelSecurity",
        "representation": "x86_adjacent_byte_immediate_reconstruction_then_bitwise_inversion",
        "stored_value_hex": "b9aab4aab2b0adb6a6b0acb6a6beb2be",
        "decoded_value": "FUKUMORIYOSIYAMA",
        "anchors": observed,
        "anchors_valid": valid,
        "confidence": "recovered-key-consumption" if valid else "invalid",
    }]
    cgw_stored = bytes.fromhex("a9dd1b66c78921b0ea0d1e991832db39")
    cgw_anchors: dict[str, str] = {}
    cgw_valid = True
    for index, value in enumerate(cgw_stored):
        rva = 0x92026 + index * 5
        expected = bytes((0xC6, 0x44, 0x24, 0x14 + index, value))
        offset = pe.get_offset_from_rva(rva)
        actual = data[offset:offset + 5]
        cgw_anchors[f"0x{rva:x}"] = actual.hex()
        cgw_valid &= actual == expected
    results.append({
        "artifact": "Techstream/bin/CommandCommon.dll",
        "artifact_sha256": sha256(data),
        "function_rva": 0x91FB0,
        "function": "CSecurityAccessCGW_DK::CancelSecurity",
        "representation": "x86_adjacent_byte_immediate_reconstruction_then_bitwise_inversion",
        "stored_value_hex": cgw_stored.hex(),
        "decoded_value": VALUES["CENTRAL_GATEWAY"].hex(),
        "anchors": cgw_anchors,
        "anchors_valid": cgw_valid,
        "confidence": "recovered-key-consumption" if cgw_valid else "invalid",
    })
    return results


def generate(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise FileNotFoundError(f"Techstream tree missing: {root}")
    files = sorted(path for path in root.rglob("*") if path.is_file())
    hits: list[dict[str, Any]] = []
    sboxes: list[dict[str, Any]] = []
    pe_count = 0
    for path in files:
        data = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        pe, exports = pe_context(path, data)
        pe_count += pe is not None
        digest: str | None = None
        for name, value in VALUES.items():
            for representation, pattern in representations(value).items():
                for offset in all_offsets(data, pattern):
                    if digest is None:
                        digest = sha256(data)
                    rva = pe.get_rva_from_offset(offset) if pe is not None else None
                    va = pe.OPTIONAL_HEADER.ImageBase + rva if pe is not None else None
                    refs = direct_refs(pe, data, exports, va) if pe is not None else []
                    hits.append({
                        "value_id": name,
                        "decoded_hex": value.hex(),
                        "decoded_ascii": value.decode("ascii") if all(0x20 <= b < 0x7F for b in value) else None,
                        "artifact": relative,
                        "artifact_sha256": digest,
                        "file_offset": offset,
                        "rva": rva,
                        "va": va,
                        "representation": representation,
                        "references": refs,
                        "containing_export": containing_export(exports, rva) if rva is not None else None,
                        "confidence": hit_confidence(name, relative, representation, refs),
                    })
        for offset in all_offsets(data, AES_SBOX):
            if digest is None:
                digest = sha256(data)
            rva = pe.get_rva_from_offset(offset) if pe is not None else None
            sboxes.append({
                "artifact": relative,
                "artifact_sha256": digest,
                "file_offset": offset,
                "rva": rva,
                "va": pe.OPTIONAL_HEADER.ImageBase + rva if pe is not None else None,
                "confidence": "implementation-evidence-not-key-evidence",
            })
    hits.sort(key=lambda item: (item["artifact"], item["file_offset"], item["value_id"], item["representation"]))
    sboxes.sort(key=lambda item: (item["artifact"], item["file_offset"]))
    absent = {
        name: not any(hit["value_id"] == name for hit in hits)
        for name in ("SIENNA_BOOT_SEED_KEY_SECRET", "SIENNA_APPLICATION_SA_SECRET")
    }
    return {
        "schema_version": 1,
        "source": "external-source",
        "distribution": "Toyota Techstream V18.00.003",
        "scan_boundary": {
            "root": "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics",
            "file_count": len(files),
            "pe_file_count": pe_count,
            "representations": sorted(next(iter({name: representations(value) for name, value in VALUES.items()}.values())).keys()),
            "x86_immediates": "known constructed byte-immediate sequences plus direct imm32 references to discovered constants",
            "limitations": "No general symbolic execution or arbitrary runtime decoding; absence is bounded to enumerated representations.",
        },
        "search_values": {name: value.hex() for name, value in VALUES.items()},
        "hits": hits,
        "constructed_immediate_hits": constructed_immediate_hits(root),
        "aes_sbox_hits": sboxes,
        "sienna_secret_absence": absent,
        "it3acnk_analysis": it3_export_inventory(root),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = generate(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: {len(result['hits'])} representation hits, "
          f"{len(result['aes_sbox_hits'])} AES S-box hits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
