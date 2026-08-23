#!/usr/bin/env python3
"""Inspect legacy Toyota CUW packages using recovered Techstream V18 semantics.

This is intentionally conservative.  It understands the Format-Version-4
archive framing, Motorola S-record payloads, the legacy Parameter.ini route
key, and the package-derived four-byte flash password.  It does not treat
those legacy values as modern Unified/RH850 credentials.
"""
from __future__ import annotations

import argparse
import configparser
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import pefile

from parse_cuw_container import FIRST_MEMBER_OFFSET, parse as parse_container
from generate_cuw_writer_inventory import decode_parameter_ini

REPO = Path(__file__).resolve().parents[2]
DEFAULT_TECHSTREAM_ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def first_member_payload(data: bytes, parsed: dict[str, Any]) -> bytes:
    end = int(parsed["first_member_end"])
    return data[end - int(parsed["payload_length"]):end]


def parse_attach_bytes(raw: bytes) -> dict[str, dict[str, str]]:
    cp = configparser.RawConfigParser(interpolation=None, strict=False, delimiters=("=",))
    cp.optionxform = str
    cp.read_string(raw.decode("latin1"))
    return {section: dict(cp.items(section, raw=True)) for section in cp.sections()}


def srec_record(line: bytes) -> tuple[str, int | None, bytes, int | None]:
    """Return (kind, address, data, entry) and validate count/checksum."""
    line = line.strip()
    if len(line) < 4 or line[:1] != b"S" or line[1:2] not in b"0123456789":
        raise ValueError(f"not an S-record: {line[:32]!r}")
    kind = line[1:2].decode("ascii")
    try:
        count = int(line[2:4], 16)
        body = bytes.fromhex(line[4:].decode("ascii"))
    except ValueError as e:
        raise ValueError(f"invalid hex in S{kind} record") from e
    if len(body) != count:
        raise ValueError(f"S{kind} count={count} but body has {len(body)} bytes")
    if (sum(body) + count) & 0xFF != 0xFF:
        raise ValueError(f"S{kind} checksum mismatch")
    addr_len = {"0": 2, "1": 2, "2": 3, "3": 4, "5": 2, "6": 3, "7": 4, "8": 3, "9": 2}[kind]
    if count < addr_len + 1:
        raise ValueError(f"S{kind} record too short")
    addr = int.from_bytes(body[:addr_len], "big")
    payload = body[addr_len:-1]
    entry = addr if kind in {"7", "8", "9"} else None
    return kind, addr, payload, entry


def summarize_srec(payload: bytes) -> tuple[dict[str, Any], dict[int, int]]:
    lines = [line for line in payload.splitlines() if line]
    counts = {str(i): 0 for i in range(10)}
    data_bytes: dict[int, int] = {}
    header = None
    entry = None
    data_records = 0
    for lineno, line in enumerate(lines, 1):
        kind, addr, chunk, term = srec_record(line)
        counts[kind] += 1
        if kind == "0" and header is None:
            header = {"address": addr, "data_hex": chunk.hex(), "data_latin1": chunk.decode("latin1")}
        if kind in {"1", "2", "3"}:
            data_records += 1
            assert addr is not None
            for i, b in enumerate(chunk):
                a = addr + i
                old = data_bytes.get(a)
                if old is not None and old != b:
                    raise ValueError(f"conflicting S-record data at 0x{a:x}")
                data_bytes[a] = b
        if term is not None:
            entry = term

    addresses = sorted(data_bytes)
    ranges: list[dict[str, Any]] = []
    if addresses:
        start = prev = addresses[0]
        for a in addresses[1:]:
            if a != prev + 1:
                ranges.append(_range_summary(start, prev + 1, data_bytes))
                start = a
            prev = a
        ranges.append(_range_summary(start, prev + 1, data_bytes))

    return ({
        "line_count": len(lines),
        "record_counts": {k: v for k, v in counts.items() if v},
        "data_record_count": data_records,
        "unique_data_bytes": len(data_bytes),
        "ranges": ranges,
        "header": header,
        "entry_address": entry,
    }, data_bytes)


def _range_summary(start: int, end: int, data: dict[int, int]) -> dict[str, Any]:
    raw = bytes(data[a] for a in range(start, end))
    return {"start": start, "end_exclusive": end, "length": end - start, "sha256": sha256(raw)}


def decode_parameter_rows(root: Path) -> list[dict[str, str]]:
    path = root / "Ini/Parameter.ini"
    text = decode_parameter_ini(path.read_bytes()).decode("latin1")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return []
    header = rows[0]
    out = []
    for row in rows[1:]:
        row += [""] * (len(header) - len(row))
        out.append(dict(zip(header, row)))
    return out


def exported_value_labels(path: Path, marker: str) -> dict[str, str]:
    """Resolve exported glptr* variables to their pointed ASCII values."""
    pe = pefile.PE(str(path)); raw = path.read_bytes(); base = pe.OPTIONAL_HEADER.ImageBase
    result: dict[str, str] = {}
    for sym in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        name = (sym.name or b"").decode("latin1")
        if marker not in name:
            continue
        try:
            off = pe.get_offset_from_rva(sym.address)
            ptr = int.from_bytes(raw[off:off + 4], "little")
            poff = pe.get_offset_from_rva(ptr - base)
            end = raw.index(0, poff)
            value = raw[poff:end].decode("latin1")
        except (ValueError, pefile.PEFormatError):
            continue
        result[value] = name
    return result


def legacy_seed_key(seed: bytes) -> bytes:
    """CCanFlashWriter legacy four-round BasicConversion, simplified."""
    if len(seed) != 4:
        raise ValueError("legacy seed must be exactly four bytes")
    state = bytearray(seed)
    for word in (0xA441, 0x2172, 0xA421, 0x4172):
        hi, lo = word >> 8, word & 0xFF
        state[:] = bytes((state[2], state[3], state[0] ^ hi, state[1] ^ lo))
    return bytes(state)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--techstream-root", type=Path, default=DEFAULT_TECHSTREAM_ROOT)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--image-out", type=Path, help="write the sole contiguous S-record data range")
    args = ap.parse_args()

    data = args.input.read_bytes()
    c = parse_container(data)
    if c["errors"]:
        raise SystemExit("container error: " + "; ".join(c["errors"]))
    attach_raw = first_member_payload(data, c)
    attach = parse_attach_bytes(attach_raw)
    vehicle = attach.get("Vehicle", {})
    cpu = attach.get("CPU01", {})

    result: dict[str, Any] = {
        "source": {"name": args.input.name, "size": len(data), "sha256": sha256(data)},
        "outer_container": {k: c[k] for k in (
            "format_type", "stored_crc32", "computed_outer_crc32", "declared_total_size",
            "name", "payload_length", "payload_crc32", "payload_sha256", "first_member_end",
            "tail_length", "tail_sha256", "format4_archive_count", "format4_archives",
            "format4_archive_bytes_consumed")},
        "attach": attach,
    }

    root = args.techstream_root
    route_key = f"{vehicle.get('KindOfECU', '')}{vehicle.get('ContactType', '')}{cpu.get('CPUType', '')}"
    route: dict[str, Any] = {"parameter_key": route_key}
    if root.is_dir():
        matches = [r for r in decode_parameter_rows(root) if r.get("ParamFileKeySystemProtocolMicon") == route_key]
        route["parameter_rows"] = matches
        labels = exported_value_labels(root / "TCUWCalibrationFile.dll", "glptrCPUType_")
        kinds = exported_value_labels(root / "TCUWCalibrationFile.dll", "glptrKindOfECU_")
        route["cpu_type_export"] = labels.get(cpu.get("CPUType", ""))
        route["kind_of_ecu_export"] = kinds.get(vehicle.get("KindOfECU", ""))
    result["techstream_route"] = route

    if c["format4_archive_count"]:
        archives = []
        for a in c["format4_archives"]:
            start = int(a["payload_offset"]); end = start + int(a["payload_length"])
            payload = data[start:end]
            entry: dict[str, Any] = dict(a)
            try:
                srec, bytes_by_addr = summarize_srec(payload)
            except ValueError as e:
                entry["srec_error"] = str(e)
                archives.append(entry)
                continue
            entry["srec"] = srec
            archives.append(entry)
            # The legacy package has one CPU archive; password extraction is
            # intentionally tied to the exact selected Parameter.ini row.
            rows = route.get("parameter_rows", [])
            if len(rows) == 1 and rows[0].get("PasswordAddress"):
                addr = int(rows[0]["PasswordAddress"], 16)
                raw_pw = bytes(bytes_by_addr.get(addr + i, 0) for i in range(4))
                if all((addr + i) in bytes_by_addr for i in range(4)):
                    byte_order = int(rows[0].get("ByteOrder", "0") or 0)
                    ordered = raw_pw if byte_order != 0 else raw_pw[::-1]
                    result["legacy_flash_password"] = {
                        "address": addr,
                        "byte_order_parameter": byte_order,
                        "raw_image_bytes_hex": raw_pw.hex(),
                        "password_hex": ordered.hex().upper(),
                        "source": "TCUWCalibrationFile.dll CalibArchivedFile::GetPassword @ 0x10002EF0",
                    }
            if args.image_out is not None and len(srec["ranges"]) == 1:
                r = srec["ranges"][0]
                args.image_out.write_bytes(bytes(bytes_by_addr[x] for x in range(r["start"], r["end_exclusive"])))
        result["archives"] = archives

    # This is the exact compiled CCanFlashWriter SecurityAccess transform.
    result["legacy_security_access"] = {
        "request_seed": "27 01",
        "positive_seed": "67 01 || seed[4]",
        "send_key": "27 02 || key[4]",
        "positive_key": "67 02",
        "round_words": ["A441", "2172", "A421", "4172"],
        "basic_conversion": "[s2, s3, s0^round_hi, s1^round_lo]",
        "simplified": "key = seed XOR 00 60 60 00",
        "self_test_seed": "00000000",
        "self_test_key": legacy_seed_key(bytes(4)).hex().upper(),
        "evidence": {
            "collate_seed_key_va": "0x00463E80",
            "calc_seed_key_va": "0x0045A1B0",
            "basic_conversion_va": "0x0045A388",
            "round_initializer_va": "0x0047F098",
        },
        "boundary": "this legacy four-byte SA path is distinct from modern Unified 16-byte ECUAuthKey/ServiceAuthKey SecurityUp",
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
