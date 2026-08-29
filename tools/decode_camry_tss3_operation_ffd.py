#!/usr/bin/env python3
"""Decode a reassembled Camry TSS3 Operation-FFD EB13 response.

Input is the diagnostic PDU after ISO-TP reassembly, beginning with EB 13.
This tool is offline only; it does not contact the vehicle.
"""
from __future__ import annotations

import argparse
import json
import struct
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SEMANTICS_PATH = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
EXPECTED_SCHEMA = "gtsplus-pcs-data-viewer-tss3-managed-semantics-v1"


def parse_eb13(pdu: bytes) -> dict[str, Any]:
    """Parse EB13 header and repeated [DID16][length8][data] blocks."""
    if len(pdu) < 6:
        raise ValueError(f"EB13 response is {len(pdu)} bytes; need at least 6")
    if pdu[:2] != b"\xEB\x13":
        raise ValueError(f"expected EB13 response, got {pdu[:2].hex().upper()}")

    blocks = []
    offset = 6
    while offset < len(pdu):
        if len(pdu) - offset < 3:
            raise ValueError(f"truncated EB13 block header at offset {offset}")
        data_id = int.from_bytes(pdu[offset:offset + 2], "big")
        length = pdu[offset + 2]
        data_start = offset + 3
        data_end = data_start + length
        if data_end > len(pdu):
            raise ValueError(
                f"DID {data_id:04X} declares {length} bytes at offset {offset}, "
                f"but only {len(pdu) - data_start} remain"
            )
        blocks.append({
            "data_id": f"{data_id:04X}",
            "length": length,
            "data": pdu[data_start:data_end],
            "offset": offset,
        })
        offset = data_end

    return {
        "service": "EB13",
        "behavior": f"0x{int.from_bytes(pdu[2:4], 'big'):04X}",
        "record": f"0x{int.from_bytes(pdu[4:6], 'big'):04X}",
        "blocks": blocks,
    }


def load_semantics(path: Path = SEMANTICS_PATH) -> dict[str, list[dict[str, Any]]]:
    artifact = json.loads(path.read_text())
    if artifact.get("schema") != EXPECTED_SCHEMA:
        raise ValueError(f"unsupported semantics schema {artifact.get('schema')!r}")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in artifact["operation_ffd"]["detail_rows"]:
        grouped[row["DataID"].upper()].append(row)
    return dict(grouped)


def _extract_raw(payload: bytes, row: dict[str, Any]) -> int:
    bit_length = int(row["BitLength"])
    start = (int(row["BytePosition"]) - 1) * 8 + (7 - int(row["BitPosition"]))
    end = start + bit_length
    if start < 0 or end > len(payload) * 8:
        raise ValueError(
            f"field {row['DataName']!r} bits {start}..{end - 1} exceed "
            f"{len(payload)}-byte DID {row['DataID']}"
        )
    value = int.from_bytes(payload, "big")
    shift = len(payload) * 8 - end
    return (value >> shift) & ((1 << bit_length) - 1)


def _integer_value(raw: int, width: int, signed: bool) -> int:
    if signed and raw & (1 << (width - 1)):
        return raw - (1 << width)
    return raw


def decode_field(payload: bytes, row: dict[str, Any]) -> dict[str, Any]:
    raw = _extract_raw(payload, row)
    width = int(row["BitLength"])
    field_type = row["Type"]
    invalid_values = {int(value, 0) for value in row.get("InvalidValueList", [])}
    invalid = raw in invalid_values

    if field_type in {"u", "s"}:
        logical = _integer_value(raw, width, field_type == "s")
        physical_decimal = Decimal(logical) * Decimal(row["Lsb"]) + Decimal(row["Offset"])
        point = int(row["Point"])
        display = f"{physical_decimal:.{point}f}"
        physical: int | float = int(physical_decimal) if point == 0 else float(physical_decimal)
    elif field_type == "f":
        if width != 32 or int(row["BitPosition"]) != 7:
            raise ValueError(f"unsupported packed float field {row['DataID']}:{row['DataName']}")
        logical = struct.unpack(">f", raw.to_bytes(4, "big"))[0]
        physical = logical * float(row["Lsb"]) + float(row["Offset"])
        display = f"{physical:.{int(row['Point'])}f}"
    else:
        raise ValueError(f"unsupported recorder field type {field_type!r}")

    return {
        "name": row["DataName"],
        "raw": raw,
        "physical": physical,
        "display": display,
        "invalid": invalid,
        "type": field_type,
        "bit_length": width,
        "byte_position": int(row["BytePosition"]),
        "bit_position": int(row["BitPosition"]),
        "lsb": row["Lsb"],
        "offset": row["Offset"],
    }


def decode_eb13(
    pdu: bytes,
    semantics: dict[str, list[dict[str, Any]]] | None = None,
    only: set[str] | None = None,
) -> dict[str, Any]:
    parsed = parse_eb13(pdu)
    semantics = semantics if semantics is not None else load_semantics()
    wanted = {item.upper().removeprefix("0X") for item in only} if only else None
    decoded_blocks = []
    for block in parsed["blocks"]:
        data_id = block["data_id"]
        if wanted is not None and data_id not in wanted:
            continue
        payload = block["data"]
        fields = []
        errors = []
        for row in semantics.get(data_id, []):
            try:
                fields.append(decode_field(payload, row))
            except ValueError as exc:
                errors.append(str(exc))
        decoded_blocks.append({
            "data_id": data_id,
            "length": block["length"],
            "raw": payload.hex(),
            "known": data_id in semantics,
            "fields": fields,
            "errors": errors,
        })
    return {
        "schema": "camry-tss3-operation-ffd-eb13-decode-v1",
        "service": parsed["service"],
        "behavior": parsed["behavior"],
        "record": parsed["record"],
        "blocks": decoded_blocks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--hex", help="reassembled EB13 PDU as hexadecimal")
    source.add_argument("--file", type=Path, help="file containing raw bytes or ASCII hex")
    parser.add_argument("--only", action="append", default=[], help="decode only this recorder DID (repeatable)")
    parser.add_argument("--out", type=Path, help="write JSON here instead of stdout")
    args = parser.parse_args()

    if args.hex is not None:
        pdu = bytes.fromhex(args.hex)
    else:
        raw = args.file.read_bytes()
        try:
            pdu = bytes.fromhex(raw.decode().strip())
        except (UnicodeDecodeError, ValueError):
            pdu = raw

    result = decode_eb13(pdu, only=set(args.only) if args.only else None)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
