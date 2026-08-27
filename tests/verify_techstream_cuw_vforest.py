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

print("== immutable T-0011-21 specimen metadata ==")
check("external specimen identity pinned", ev["source"] == {
    "filename": "T-0011-21 - 04C21.cuw",
    "size": 2825257,
    "sha256": "e0525b4fe0224772a3dde68d16bf2fb7a808d6d937fa32a337db34d95f5ba61d",
})
outer = ev["outer_container"]
check("Format-4 outer CRC validates", outer["format_type"] == 4 and outer["stored_crc32"] == outer["computed_crc32"] == "2615F236" and outer["declared_total_size"] == ev["source"]["size"])
check("attach member identity pinned", outer["first_member_name"] == "attach.att" and outer["first_member_length"] == 410 and outer["first_member_crc32"] == "DE1824C4" and outer["first_member_sha256"] == "a1edd8a8767ade5b30f5795a3d71d005212c146426ddb600d61589c50f43032e")
ar = ev["format4_archive"]
check("sole CPU archive exact", ar["count"] == 1 and ar["name"] == "8966304C2100.txt" and ar["payload_length"] == 2824778 and ar["payload_crc32"] == ar["computed_payload_crc32"] == "2BD15E25" and ar["payload_sha256"] == "c6dec16cafe641d66a1f4c7a0628b405ac4178f251483ae87177ef19278af9a7" and ar["record_consumes_tail_exactly"])

d = ev["descriptor"]
check("descriptor identifies 2020-21 Tacoma 2GR-FKS", d["Vehicle"]["VehicleName"] == "Tacoma" and d["Vehicle"]["ModelYear"] == "20-21" and d["Vehicle"]["VehicleType"] == "GRN305/GRN310" and d["Vehicle"]["EngineType"] == "2GR-FKS")
check("descriptor calibration transition exact", d["CPU01"]["CPUImageName"] == "304C21.xxz" and d["CPU01"]["NewCID"] == "8966304C2100" and d["CPU01"]["01_TargetCalibration"] == "8966304C2000" and d["CPU01"]["01_TargetData"] == "3532323734463D4A")
check("descriptor VFOREST selectors exact", d["Vehicle"]["KindOfECU"] == "0" and d["Vehicle"]["ContactType"] == "P5-CAN" and d["CPU01"]["CPUType"] == "86" and d["CPU01"]["LocationID"] == "0002000100070720")

print("\n== Techstream V18 route join ==")
r = ev["techstream_v18_route"]
check("route key exact", r["parameter_key"] == "0P5-CAN86" and len(r["parameter_rows"]) == 1)
row = r["parameter_rows"][0]
check("route selects integrated VFOREST writer", row["FORESTTypeFlag"] == "1" and row["M16CTypeFlag"] == "0" and row["FlagToUseCIDGetterAndFlashWriterDLL"] == "0" and row["CalibrationType"] == "2")
check("password address and byte order exact", row["PasswordAddress"] == "0000100E" and row["ByteOrder"] == "0")
check("CPUType 86 export is VFOREST_2_0M", r["cpu_type_export"] == "?glptrCPUType_VFOREST_2_0M@@3PBDB")
check("KindOfECU 0 export is ENG&ECT", r["kind_of_ecu_export"] == "?glptrKindOfECU_ENGAndECT@@3PBDB")

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

print("\n== real LZF stream and reconstructed logical image ==")
lzf = ev["lzf_stream"]
check("decoded ZV stream identity pinned", lzf["decoded_length"] == 1329128 and lzf["decoded_sha256"] == "37b832f7899776c27d64483365ac83d9144cf590ba81483320afd5f3313d47db")
check("Techstream names format LZF", lzf["format_name_from_cuw_exe"] == "LZF-Format data")
check("all 512 logical blocks accounted for", lzf["record_count"] == 512 and lzf["type_counts"] == {"0": 6, "1": 506} and lzf["expanded_length_counts"] == {"4096": 512} and lzf["stream_consumed_exactly"])
check("six raw block indices exact", lzf["raw_record_indices"] == [0, 1, 149, 150, 168, 181])
check("compressed size range pinned", lzf["compressed_stored_length_min"] == 57 and lzf["compressed_stored_length_max"] == 4093)
fill = lzf["repeated_fill_block"]
check("115 compressed fill blocks expand identically", fill["word_hex"] == "E203F133" and fill["record_count"] == 115 and fill["expanded_block_sha256"] == "4e1da2228f2acfec26fbd1054db55e95b393986119bde211ccabb0f182ab479e" and fill["record_indices"] == list(range(396, 511)))
img = ev["reconstructed_image"]
check("LZF layer reconstructs exact 2 MiB", img["length"] == 0x200000 and img["sha256"] == "feb1e7ff00f7268ece3f043a56ac39a33bd22dffbe4f7f23fad1286b53db8e04")
check("reconstructed image contains expected part identity", img["cpu_image_name_offset"] == 0x100C and img["cpu_image_name_ascii"] == "89663-04C21")
check("native-code interpretation remains bounded", "native plaintext CPU code" in img["boundary"] and "unproven" in img["boundary"])

print("\n== old/new software passwords ==")
sec = ev["legacy_security"]
source = sec["source_passwords"][0]
old = decode_legacy_target_data("3532323734463D4A")
loc = bytes.fromhex("0002000100070720")
check("TargetData source password exact", old == 0x51040A7C and source["password_hex"] == "51040A7C" and source["wire_password_hex"] == "7C0A0451")
check("source CheckID transcript exact", [x.hex().upper() for x in legacy_check_id_payloads(loc, old)] == source["check_id_payloads_after_can_id"] == ["00", "00", "200701000200", "0700", "7C0A0451"])
new = sec["new_image_password"]
check("new password source is decoded ZV stream offset 0x100E", new["source_address_in_decoded_zv_stream"] == "0x100E" and new["raw_bytes_hex"] == "FF0CEF56")
check("ByteOrder=0 reverses host uint32 but CheckID restores archive order on wire", new["byte_order_parameter"] == 0 and new["password_hex"] == "56EF0CFF" and new["wire_password_hex"] == "FF0CEF56")
check("new CheckID transcript exact", new["check_id_payloads_after_can_id"] == ["00", "00", "200701000200", "0700", "FF0CEF56"])
check("PasswordAddress buffer boundary explicit", "decoded ZV/LZF archive buffer" in new["important_boundary"] and "not the LZF-expanded" in new["important_boundary"])
check("shared legacy SA remains separate", sec["security_access"]["shared_integrated_writer"] and "seed XOR 00 60 60 00" in sec["security_access"]["grammar"] and "independent from CheckID" in sec["security_access"]["boundary"])

print("\n== raw PE identities and host transfer path ==")
cuw = pefile.PE(str(ROOT / "Cuw.exe")); cbase = cuw.OPTIONAL_HEADER.ImageBase
def at(va: int, n: int) -> bytes:
    return cuw.get_data(va - cbase, n)
pe = ev["techstream_pe_evidence"]
for key, va, size, digest in [
    ("ascii_lzf_parser", 0x43F4CC, 0x262, "f80f34dd9ea7d8892c8a84afa119ac5a96c81a3e828374370900655f0bade55e"),
    ("ascii_hex_decode_helper", 0x43F730, 0x70, "a52fd347fdc75c426e8612e551b055336ea1994493a94181f6f5a61008307c0e"),
    ("vforest_flashwrite", 0x587AD4, 0x2B8, "ca32c157f997ac78c5a1762f400a1b2650aec3cf55c97ddbdf957fa8dcb8108e"),
    ("zv_record_parser", 0x587D8C, 0x1D0, "0c1016b9a7ef845b5a2d6ba75530b5cad8ded6431dcf9f54daaaa1cb7902f2cb"),
    ("write_with_erase", 0x587F5C, 0x320, "3254e7b5cead2622b0527b4d453069c4f111ce8efad2949052ea2be614c7b0f6"),
    ("verify_comp_data", 0x58827C, 0x320, "62ef0ac3dcfdb29ddcb3834765b8262431d2059e00e553d52ab2242eda4d51fc"),
    ("data_sender", 0x58859C, 0x130, "1c59cc8f403569796e2e5fe1e839db0f6f3b3b51c0aba513d84e780bc8076829"),
]:
    check(f"{key} PE body pinned", pe[key]["va"] == f"0x{va:08X}" and pe[key]["size"] == f"0x{size:X}" and hashlib.sha256(at(va, size)).hexdigest() == pe[key]["sha256"] == digest)
check("LZF parser strings exist in pinned Cuw.exe", all(x.encode() in (ROOT / "Cuw.exe").read_bytes() for x in ["5A5600", "5A5601", "LZF-Format data"]))
anchors = pe["anchors"]
check("shared Execute enters legacy reprogramming/security path", at(0x45E8FF,5).hex().upper() == anchors["shared_execute_to_change_reprogramming"]["bytes"] == "E850590000" and anchors["shared_execute_to_change_reprogramming"]["target"] == "0x00464254")
check("shared Execute dispatches VFOREST FlashWrite", at(0x461F42,5).hex().upper() == anchors["shared_execute_to_vforest_flashwrite"]["bytes"] == "E88D5B1200" and anchors["shared_execute_to_vforest_flashwrite"]["target"] == "0x00587AD4")
check("factory constructs integrated VFOREST writer", at(0x477B13,5).hex().upper() == anchors["vforest_factory_constructor"]["bytes"] == "E8D40B1100")
check("VFOREST sender directly copies stored chunk into TX buffer", at(0x58861A,5).hex().upper() == anchors["sender_direct_memcpy"]["bytes"] == "E8211F0200")
check("host-side LZF expansion is absent from writer boundary", "sends each record's stored raw/compressed body" in ev["host_transfer_boundary"]["conclusion"] and "does not LZF-expand" in ev["host_transfer_boundary"]["conclusion"])

cal = pefile.PE(str(ROOT / "TCUWCalibrationFile.dll")); kbase = cal.OPTIONAL_HEADER.ImageBase
def cat(va: int, n: int) -> bytes:
    return cal.get_data(va - kbase, n)
check("GetPassword byte-order consumer body pinned", hashlib.sha256(cat(0x10002EF0,0x15F)).hexdigest() == "13cd12218291ebbe2d147d2ea9c2cdecd020bf73d4c9f1505c6cdbbeae799164")
check("GetNewPassword fallback body pinned", hashlib.sha256(cat(0x10003090,0x3C)).hexdigest() == "efe7a275c16909454cfe40418c22da35e5cf7a2ba5d2cb134ed7c6cae08c46fc")

check("modern Unified credential fields absent", set(ev["modern_unified_boundary"]["descriptor_fields_absent"]) == {"ECUAuthKey","ServiceAuthKey","SeedKey","Nonce","OffsetAddress","SecurityProperty2"} and "not modern" in ev["modern_unified_boundary"]["selected_route"])

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
