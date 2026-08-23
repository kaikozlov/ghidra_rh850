#!/usr/bin/env python3
"""Inspect Toyota legacy VFOREST/LZF CUW packages using Techstream V18 semantics.

The Format-4 archive member used by the VFOREST route is ASCII-hex text.  Once
line breaks are removed and hex-decoded, it is a stream of ZV00 (raw) and ZV01
(LZF-compressed) records.  This tool validates that framing, expands each record,
and reconstructs the logical image without treating that image as native CPU
plaintext unless independent evidence establishes that stronger claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pefile

from inspect_cuw_legacy import (
    decode_legacy_target_data,
    decode_parameter_rows,
    exported_value_labels,
    first_member_payload,
    legacy_check_id_payloads,
    parse_attach_bytes,
)
from parse_cuw_container import parse as parse_container

REPO = Path(__file__).resolve().parents[2]
DEFAULT_TECHSTREAM_ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_ascii_hex_payload(payload: bytes) -> bytes:
    compact = b"".join(payload.split())
    if len(compact) % 2:
        raise ValueError("ASCII-hex payload has odd nibble count")
    try:
        text = compact.decode("ascii")
        raw = bytes.fromhex(text)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("archive payload is not whitespace-separated ASCII hex") from exc
    if raw.hex().upper().encode("ascii") != compact.upper():
        raise ValueError("ASCII-hex payload does not round-trip exactly")
    return raw


def lzf_decompress(data: bytes, expected_length: int) -> bytes:
    """Expand standard liblzf/LZF data with exact output-size validation."""
    out = bytearray()
    ip = 0
    while ip < len(data):
        ctrl = data[ip]
        ip += 1
        if ctrl < 32:
            count = ctrl + 1
            if ip + count > len(data):
                raise ValueError("LZF literal run exceeds compressed input")
            out.extend(data[ip:ip + count])
            ip += count
        else:
            count = ctrl >> 5
            ref = len(out) - ((ctrl & 0x1F) << 8) - 1
            if count == 7:
                if ip >= len(data):
                    raise ValueError("LZF extended length exceeds compressed input")
                count += data[ip]
                ip += 1
            if ip >= len(data):
                raise ValueError("LZF back-reference offset exceeds compressed input")
            ref -= data[ip]
            ip += 1
            count += 2
            if ref < 0:
                raise ValueError("LZF back-reference precedes output buffer")
            for _ in range(count):
                if ref >= len(out):
                    raise ValueError("LZF back-reference exceeds produced output")
                out.append(out[ref])
                ref += 1
        if len(out) > expected_length:
            raise ValueError("LZF output exceeds declared expanded length")
    if len(out) != expected_length:
        raise ValueError(f"LZF output length {len(out)} != declared {expected_length}")
    return bytes(out)


def parse_zv_lzf_stream(raw: bytes) -> tuple[list[dict[str, Any]], bytes]:
    """Parse ZV00/raw and ZV01/LZF records and return logical image bytes."""
    records: list[dict[str, Any]] = []
    blocks: list[bytes] = []
    off = 0
    logical = 0
    while off < len(raw):
        if off + 5 > len(raw):
            raise ValueError(f"truncated ZV record header at 0x{off:X}")
        if raw[off:off + 2] != b"ZV":
            raise ValueError(f"bad ZV magic at 0x{off:X}: {raw[off:off+8].hex()}")
        record_type = raw[off + 2]
        stored_length = int.from_bytes(raw[off + 3:off + 5], "big")
        if record_type == 0:
            header_length = 5
            expanded_length = stored_length
        elif record_type == 1:
            if off + 7 > len(raw):
                raise ValueError(f"truncated ZV01 header at 0x{off:X}")
            header_length = 7
            expanded_length = int.from_bytes(raw[off + 5:off + 7], "big")
        else:
            raise ValueError(f"unsupported ZV record type 0x{record_type:02X} at 0x{off:X}")
        body_start = off + header_length
        body_end = body_start + stored_length
        if body_end > len(raw):
            raise ValueError(f"ZV record body overruns stream at 0x{off:X}")
        stored = raw[body_start:body_end]
        block = stored if record_type == 0 else lzf_decompress(stored, expanded_length)
        if len(block) != expanded_length:
            raise ValueError("expanded ZV block length mismatch")
        records.append({
            "index": len(records),
            "stream_offset": off,
            "logical_offset": logical,
            "type": record_type,
            "header_length": header_length,
            "stored_length": stored_length,
            "expanded_length": expanded_length,
            "stored_sha256": sha256(stored),
            "expanded_sha256": sha256(block),
        })
        blocks.append(block)
        logical += expanded_length
        off = body_end
    if off != len(raw):
        raise ValueError("ZV parser did not consume stream exactly")
    return records, b"".join(blocks)


def pe_body(root: Path, va: int, size: int) -> dict[str, Any]:
    pe = pefile.PE(str(root / "Cuw.exe"))
    body = pe.get_data(va - pe.OPTIONAL_HEADER.ImageBase, size)
    if len(body) != size:
        raise ValueError(f"could not read Cuw.exe body at 0x{va:08X}")
    return {"va": f"0x{va:08X}", "size": f"0x{size:X}", "sha256": sha256(body)}


def pe_bytes(root: Path, va: int, size: int) -> str:
    pe = pefile.PE(str(root / "Cuw.exe"))
    body = pe.get_data(va - pe.OPTIONAL_HEADER.ImageBase, size)
    if len(body) != size:
        raise ValueError(f"could not read Cuw.exe bytes at 0x{va:08X}")
    return body.hex().upper()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--techstream-root", type=Path, default=DEFAULT_TECHSTREAM_ROOT)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--image-out", type=Path, help="write reconstructed logical image (untracked build/reference output)")
    args = ap.parse_args()

    package = args.input.read_bytes()
    container = parse_container(package)
    if container["errors"]:
        raise SystemExit("container error: " + "; ".join(container["errors"]))
    attach_raw = first_member_payload(package, container)
    attach = parse_attach_bytes(attach_raw)
    vehicle = attach.get("Vehicle", {})
    cpu = attach.get("CPU01", {})
    archives = container.get("format4_archives", [])
    if len(archives) != 1:
        raise SystemExit(f"expected one Format-4 CPU archive, found {len(archives)}")
    ar = archives[0]
    start = int(ar["payload_offset"])
    payload = package[start:start + int(ar["payload_length"])]
    zv = decode_ascii_hex_payload(payload)
    records, image = parse_zv_lzf_stream(zv)

    route_key = f"{vehicle.get('KindOfECU','')}{vehicle.get('ContactType','')}{cpu.get('CPUType','')}"
    root = args.techstream_root
    route: dict[str, Any] = {"parameter_key": route_key}
    row: dict[str, str] | None = None
    if root.is_dir():
        matches = [x for x in decode_parameter_rows(root) if x.get("ParamFileKeySystemProtocolMicon") == route_key]
        route["parameter_rows"] = matches
        if len(matches) == 1:
            row = matches[0]
        route["cpu_type_export"] = exported_value_labels(root / "TCUWCalibrationFile.dll", "glptrCPUType_").get(cpu.get("CPUType", ""))
        route["kind_of_ecu_export"] = exported_value_labels(root / "TCUWCalibrationFile.dll", "glptrKindOfECU_").get(vehicle.get("KindOfECU", ""))

    location = bytes.fromhex(cpu.get("LocationID", ""))
    targets = []
    for index in range(1, int(cpu.get("NumberOfTargets", "0") or 0) + 1):
        target_data = cpu.get(f"{index:02d}_TargetData", "")
        password = decode_legacy_target_data(target_data)
        frames = legacy_check_id_payloads(location, password)
        targets.append({
            "calibration": cpu.get(f"{index:02d}_TargetCalibration", ""),
            "target_data": target_data,
            "password_hex": f"{password:08X}",
            "wire_password_hex": frames[-1].hex().upper(),
            "check_id_payloads_after_can_id": [x.hex().upper() for x in frames],
        })

    software_password = None
    if row and row.get("PasswordAddress"):
        address = int(row["PasswordAddress"], 16)
        if address + 4 > len(zv):
            raise SystemExit("PasswordAddress falls outside decoded ZV/LZF stream")
        raw_pw = zv[address:address + 4]
        byte_order = int(row.get("ByteOrder", "0") or 0)
        ordered = raw_pw if byte_order != 0 else raw_pw[::-1]
        value = int.from_bytes(ordered, "big")
        frames = legacy_check_id_payloads(location, value)
        software_password = {
            "source_address_in_decoded_zv_stream": f"0x{address:X}",
            "byte_order_parameter": byte_order,
            "raw_bytes_hex": raw_pw.hex().upper(),
            "password_hex": f"{value:08X}",
            "role": "new-image software password via CalibrationFile::GetNewPassword fallback when no descriptor override is present",
            "source": "TCUWCalibrationFile.dll CalibArchivedFile::GetPassword @ 0x10002EF0; GetNewPassword @ 0x10003090",
            "byte_order_semantics": "ByteOrder=0 reverses the four archived bytes when formatting the uint32 password; CheckID later emits that uint32 little-endian, reproducing the archived byte order on wire",
            "wire_password_hex": frames[-1].hex().upper(),
            "check_id_payloads_after_can_id": [x.hex().upper() for x in frames],
            "important_boundary": "PasswordAddress indexes Techstream's decoded ZV/LZF archive buffer, not the LZF-expanded 2-MiB logical image",
        }

    type_counts = {"0": 0, "1": 0}
    expanded_lengths: dict[str, int] = {}
    for rec in records:
        type_counts[str(rec["type"])] = type_counts.get(str(rec["type"]), 0) + 1
        ek = str(rec["expanded_length"])
        expanded_lengths[ek] = expanded_lengths.get(ek, 0) + 1
    raw_indices = [r["index"] for r in records if r["type"] == 0]
    record_manifest = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    compressed = [r for r in records if r["type"] == 1]
    fill_word = bytes.fromhex("E203F133")
    fill_block = fill_word * (0x1000 // len(fill_word))
    fill_hash = sha256(fill_block)
    fill_indices = [r["index"] for r in records if r["expanded_sha256"] == fill_hash]

    result: dict[str, Any] = {
        "source": {"filename": args.input.name, "size": len(package), "sha256": sha256(package)},
        "outer_container": {
            "format_type": container["format_type"],
            "stored_crc32": f"{int(container['stored_crc32']):08X}",
            "computed_crc32": f"{int(container['computed_outer_crc32']):08X}",
            "declared_total_size": container["declared_total_size"],
            "first_member_name": container["name"],
            "first_member_length": container["payload_length"],
            "first_member_crc32": f"{int(container['payload_crc32']):08X}",
            "first_member_sha256": container["payload_sha256"],
            "first_member_end": container["first_member_end"],
            "tail_length": container["tail_length"],
            "tail_sha256": container["tail_sha256"],
        },
        "descriptor": attach,
        "format4_archive": {
            "count": container["format4_archive_count"],
            "name": ar["name"],
            "name_length": ar["name_length"],
            "payload_length": ar["payload_length"],
            "payload_crc32": f"{int(ar['payload_crc32']):08X}",
            "computed_payload_crc32": f"{int(ar['computed_payload_crc32']):08X}",
            "payload_sha256": ar["payload_sha256"],
            "record_consumes_tail_exactly": int(ar["record_end"]) == len(package),
        },
        "techstream_v18_route": route,
        "lzf_stream": {
            "ascii_hex_payload": True,
            "decoded_length": len(zv),
            "decoded_sha256": sha256(zv),
            "format_name_from_cuw_exe": "LZF-Format data",
            "record_count": len(records),
            "type_counts": type_counts,
            "raw_record_indices": raw_indices,
            "expanded_length_counts": expanded_lengths,
            "compressed_stored_length_min": min(r["stored_length"] for r in compressed),
            "compressed_stored_length_max": max(r["stored_length"] for r in compressed),
            "record_manifest_sha256": sha256(record_manifest),
            "stream_consumed_exactly": sum(r["header_length"] + r["stored_length"] for r in records) == len(zv),
            "repeated_fill_block": {
                "word_hex": fill_word.hex().upper(),
                "expanded_block_sha256": fill_hash,
                "record_count": len(fill_indices),
                "record_indices": fill_indices,
            },
        },
        "reconstructed_image": {
            "length": len(image),
            "sha256": sha256(image),
            "cpu_image_name_offset": image.find(b"89663-04C21"),
            "cpu_image_name_ascii": "89663-04C21" if image.find(b"89663-04C21") >= 0 else None,
            "boundary": "LZF compression is fully decoded; whether the resulting 2-MiB representation is native plaintext CPU code or retains Denso/VFOREST coding remains unproven",
        },
        "legacy_security": {
            "source_passwords": targets,
            "new_image_password": software_password,
            "security_access": {
                "shared_integrated_writer": True,
                "grammar": "27 01 -> 67 01 || seed[4]; 27 02 || (seed XOR 00 60 60 00) -> 67 02",
                "boundary": "same integrated CCanFlashWriter SecurityAccess path as the legacy T-0087 route; independent from CheckID software password",
            },
        },
        "host_transfer_boundary": {
            "conclusion": "Techstream decodes ASCII hex into ZV/LZF records but sends each record's stored raw/compressed body through CCanVFORESTFlashWriter; it does not LZF-expand the image before J2534 transmission",
            "ecu_side": "LZF expansion / final image interpretation occurs downstream of this host writer; exact ECU-side implementation is not claimed from this package alone",
        },
        "modern_unified_boundary": {
            "descriptor_fields_absent": [x for x in ("ECUAuthKey", "ServiceAuthKey", "SeedKey", "Nonce", "OffsetAddress", "SecurityProperty2") if x not in cpu],
            "selected_route": "legacy integrated CCanFlashWriter / CCanVFORESTFlashWriter, not modern dynamic Unified prepare+flash",
        },
    }

    if root.is_dir():
        result["techstream_pe_evidence"] = {
            "ascii_lzf_parser": pe_body(root, 0x43F4CC, 0x262),
            "ascii_hex_decode_helper": pe_body(root, 0x43F730, 0x70),
            "vforest_flashwrite": pe_body(root, 0x587AD4, 0x2B8),
            "zv_record_parser": pe_body(root, 0x587D8C, 0x1D0),
            "write_with_erase": pe_body(root, 0x587F5C, 0x320),
            "verify_comp_data": pe_body(root, 0x58827C, 0x320),
            "data_sender": pe_body(root, 0x58859C, 0x130),
            "anchors": {
                "shared_execute_to_change_reprogramming": {"va": "0x0045E8FF", "bytes": pe_bytes(root, 0x45E8FF, 5), "target": "0x00464254"},
                "shared_execute_to_vforest_flashwrite": {"va": "0x00461F42", "bytes": pe_bytes(root, 0x461F42, 5), "target": "0x00587AD4"},
                "vforest_factory_constructor": {"va": "0x00477B13", "bytes": pe_bytes(root, 0x477B13, 5), "target": "0x005886EC"},
                "sender_direct_memcpy": {"va": "0x0058861A", "bytes": pe_bytes(root, 0x58861A, 5), "target": "0x005AA540"},
            },
            "literal_strings": ["5A5600", "5A5601", "LZF-Format data"],
        }

    if args.image_out is not None:
        args.image_out.parent.mkdir(parents=True, exist_ok=True)
        args.image_out.write_bytes(image)

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
