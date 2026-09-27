#!/usr/bin/env python3
"""Deterministic verification of the T-0011-21 Tacoma VFOREST/LZF CUW finding."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"
EVIDENCE = REPO / "data/generated/techstream_v18/cuw_t0011_21_04c21_specimen.json"
PACKAGE = REPO / "software/Techstream/cuw/T-0011-21 - 04C21.cuw"
sys.path.insert(0, str(REPO / "tools/techstream"))

from inspect_cuw_legacy import decode_legacy_target_data, legacy_check_id_payloads
from inspect_cuw_vforest import decode_ascii_hex_payload, lzf_decompress, parse_zv_lzf_stream
from parse_cuw_container import parse as parse_container

p = f = 0
oracle = "raw_bytes+independent_external_artifact"


def check(name: str, cond: object, detail: str = "") -> None:
    global p, f
    ok = bool(cond)
    p += int(ok); f += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


if not ROOT.is_dir():
    print("[SKIP] V18 unavailable")
    raise SystemExit(77)

ev = json.loads(EVIDENCE.read_text())

print("\n== independent LZF/ZV parser fixtures ==")
check("ASCII-hex decoder removes whitespace only", decode_ascii_hex_payload(b"5A56\r\n3031\t") == b"ZV01")
try:
    decode_ascii_hex_payload(b"5A5")
except ValueError:
    odd_rejected = True
else:
    odd_rejected = False
check("odd ASCII-hex payload rejected", odd_rejected)

# Standard LZF: literal 'abc', then a six-byte back-reference to output offset 0.
compressed = b"\x02abc\x80\x02"
check("standard LZF literal+backref fixture expands", lzf_decompress(compressed, 9) == b"abcabcabc")
raw_record = b"ZV\x00" + struct.pack(">H", 5) + b"HELLO"
comp_record = b"ZV\x01" + struct.pack(">HH", len(compressed), 9) + compressed
records, fixture_image = parse_zv_lzf_stream(raw_record + comp_record)
check("ZV00 raw record grammar exact", records[0]["type"] == 0 and records[0]["header_length"] == 5 and records[0]["stored_length"] == records[0]["expanded_length"] == 5)
check("ZV01 compressed record grammar exact", records[1]["type"] == 1 and records[1]["header_length"] == 7 and records[1]["stored_length"] == len(compressed) and records[1]["expanded_length"] == 9)
check("mixed ZV fixture reconstructs exact image", fixture_image == b"HELLOabcabcabc")
try:
    parse_zv_lzf_stream(b"ZV\x02\x00\x00")
except ValueError:
    unknown_rejected = True
else:
    unknown_rejected = False
check("unknown ZV record type rejected", unknown_rejected)

lzf = ev["lzf_stream"]
img = ev["reconstructed_image"]

print("\n== old/new software passwords ==")
old = decode_legacy_target_data("3532323734463D4A")
loc = bytes.fromhex("0002000100070720")
check("TargetData source password decodes exact", old == 0x51040A7C)
check("source CheckID transcript exact", [x.hex().upper() for x in legacy_check_id_payloads(loc, old)] == ["00", "00", "200701000200", "0700", "7C0A0451"])

print("\n== raw PE identities and host transfer path ==")
cuw = pefile.PE(str(ROOT / "Cuw.exe")); cbase = cuw.OPTIONAL_HEADER.ImageBase
def at(va: int, n: int) -> bytes:
    return cuw.get_data(va - cbase, n)
for key, va, size, digest in [
    ("ascii_lzf_parser", 0x43F4CC, 0x262, "f80f34dd9ea7d8892c8a84afa119ac5a96c81a3e828374370900655f0bade55e"),
    ("ascii_hex_decode_helper", 0x43F730, 0x70, "a52fd347fdc75c426e8612e551b055336ea1994493a94181f6f5a61008307c0e"),
    ("vforest_flashwrite", 0x587AD4, 0x2B8, "ca32c157f997ac78c5a1762f400a1b2650aec3cf55c97ddbdf957fa8dcb8108e"),
    ("zv_record_parser", 0x587D8C, 0x1D0, "0c1016b9a7ef845b5a2d6ba75530b5cad8ded6431dcf9f54daaaa1cb7902f2cb"),
    ("write_with_erase", 0x587F5C, 0x320, "3254e7b5cead2622b0527b4d453069c4f111ce8efad2949052ea2be614c7b0f6"),
    ("verify_comp_data", 0x58827C, 0x320, "62ef0ac3dcfdb29ddcb3834765b8262431d2059e00e553d52ab2242eda4d51fc"),
    ("data_sender", 0x58859C, 0x130, "1c59cc8f403569796e2e5fe1e839db0f6f3b3b51c0aba513d84e780bc8076829"),
]:
    check(f"{key} PE body pinned", hashlib.sha256(at(va, size)).hexdigest() == digest)
check("LZF parser strings exist in pinned Cuw.exe", all(x.encode() in (ROOT / "Cuw.exe").read_bytes() for x in ["5A5600", "5A5601", "LZF-Format data"]))
check("shared Execute enters legacy reprogramming/security path", at(0x45E8FF,5).hex().upper() == "E850590000")
check("shared Execute dispatches VFOREST FlashWrite", at(0x461F42,5).hex().upper() == "E88D5B1200")
check("factory constructs integrated VFOREST writer", at(0x477B13,5).hex().upper() == "E8D40B1100")
check("VFOREST sender directly copies stored chunk into TX buffer", at(0x58861A,5).hex().upper() == "E8211F0200")

cal = pefile.PE(str(ROOT / "TCUWCalibrationFile.dll")); kbase = cal.OPTIONAL_HEADER.ImageBase
def cat(va: int, n: int) -> bytes:
    return cal.get_data(va - kbase, n)
check("GetPassword byte-order consumer body pinned", hashlib.sha256(cat(0x10002EF0,0x15F)).hexdigest() == "13cd12218291ebbe2d147d2ea9c2cdecd020bf73d4c9f1505c6cdbbeae799164")
check("GetNewPassword fallback body pinned", hashlib.sha256(cat(0x10003090,0x3C)).hexdigest() == "efe7a275c16909454cfe40418c22da35e5cf7a2ba5d2cb134ed7c6cae08c46fc")


if PACKAGE.is_file():
    print("\n== optional local raw-specimen cross-check ==")
    package = PACKAGE.read_bytes()
    check("local CUW hash matches generated evidence", hashlib.sha256(package).hexdigest() == ev["source"]["sha256"] and len(package) == ev["source"]["size"])
    obj = parse_container(package)
    a = obj["format4_archives"][0]
    text = package[int(a["payload_offset"]):int(a["payload_offset"]) + int(a["payload_length"])]
    raw = decode_ascii_hex_payload(text)
    real_records, real_image = parse_zv_lzf_stream(raw)
    check("local ZV stream hash matches", hashlib.sha256(raw).hexdigest() == lzf["decoded_sha256"] and len(real_records) == 512)
    check("local LZF-expanded image hash matches", hashlib.sha256(real_image).hexdigest() == img["sha256"] and len(real_image) == 0x200000)
    check("PasswordAddress indexes decoded stream exactly", raw[0x100E:0x1012].hex().upper() == "FF0CEF56" and real_image[0x100E:0x1012].hex().upper() != "FF0CEF56")

print(f"\nResults: {p} passed, {f} failed")
raise SystemExit(1 if f else 0)
