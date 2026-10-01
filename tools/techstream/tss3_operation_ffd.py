"""TSS3 Operation-FFD framing and PCS Data Viewer field decoding.

Input is an EB13 diagnostic PDU, after ISO-TP reassembly. This module performs
no acquisition. Both the offline command and live recorder use this decoder.
"""
from __future__ import annotations

import json
import math
import struct
from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.techstream.ddb_semantics import extract_msb0

SEMANTICS_PATH = REPO_ROOT / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
EXPECTED_SCHEMA = "gtsplus-pcs-data-viewer-tss3-managed-semantics-v1"


@dataclass(frozen=True)
class RecorderBlock:
    data_id: int
    data: bytes


@dataclass(frozen=True)
class RecorderRecord:
    behavior_id: int
    record_id: int
    declared_count: int
    blocks: list[RecorderBlock]


def parse_eb13(pdu: bytes, *, expected: tuple[int, int] | None = None) -> RecorderRecord:
    """Validate echoes and the complete block stream, including zero-count scans."""
    if len(pdu) < 7 or pdu[:2] != b"\xeb\x13":
        raise ValueError("expected EB13 response with a seven-byte header")
    behavior_id = int.from_bytes(pdu[2:4], "big")
    record_id = int.from_bytes(pdu[4:6], "big")
    if expected is not None and (behavior_id, record_id) != expected:
        raise ValueError(
            f"EB13 echo mismatch: expected {expected[0]:04X}/{expected[1]:04X}, "
            f"got {behavior_id:04X}/{record_id:04X}")
    count = pdu[6]
    blocks = []
    pos = 7
    # GetTSS3OperationFFDP5_DT: zero means derive count, not an empty record.
    while pos < len(pdu) and (count == 0 or len(blocks) < count):
        if len(pdu) - pos < 3:
            raise ValueError(f"EB13 truncated block header at offset {pos}")
        data_id = int.from_bytes(pdu[pos:pos + 2], "big")
        length = pdu[pos + 2]
        pos += 3
        end = pos + length
        if end > len(pdu):
            raise ValueError(f"EB13 DID {data_id:04X} length {length} overruns record")
        blocks.append(RecorderBlock(data_id, pdu[pos:end]))
        pos = end
    if count and len(blocks) != count:
        raise ValueError(f"EB13 block count says {count}, parsed {len(blocks)}")
    if pos != len(pdu):
        raise ValueError(f"EB13 has {len(pdu) - pos} trailing bytes after block stream")
    return RecorderRecord(behavior_id, record_id, count, blocks)


def load_semantics(path: Path = SEMANTICS_PATH) -> dict[int, list[dict[str, Any]]]:
    artifact = json.loads(path.read_text())
    if artifact.get("schema") != EXPECTED_SCHEMA:
        raise ValueError(f"unexpected recorder semantics schema in {path}")
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in artifact["operation_ffd"]["detail_rows"]:
        if row["DataID"] != "-":  # Viewer metadata, not a recorder data block.
            grouped.setdefault(int(row["DataID"], 16), []).append(row)
    return grouped


def _floor_text(value: Decimal, point: int) -> str:
    # ValueConverter.Floor precedes fixed-point formatting, including negatives.
    with localcontext() as context:
        context.prec = max(28, value.adjusted() + point + 1, len(value.as_tuple().digits))
        value = value.quantize(Decimal(1).scaleb(-point), rounding=ROUND_FLOOR)
    return f"{value:.{point}f}"


def _physical_value(raw: int, row: dict[str, Any]) -> tuple[bool, str | None]:
    kind = row["Type"]
    width = int(row["BitLength"])
    invalid_values = [int(value, 16) for value in row.get("InvalidValueList", [])]
    if row["DataID"] == "0507":
        # GetSeparatedDateTime reads decimal digit pairs (BCD), not binary u8.
        # Return stored components, without the viewer's PC-local timezone shift.
        index = int(row["BytePosition"]) - 1
        text = f"{raw:02X}"
        minimum = (0, 1, 1, 0, 0, 0)
        maximum = (38, 12, 31, 23, 59, 59)
        if not 0 <= index < 6 or width != 8:
            raise ValueError("invalid 0507 timestamp geometry")
        invalid = not text.isdecimal() or not minimum[index] <= int(text) <= maximum[index]
        return invalid, None if invalid else text
    if kind in ("u", "s"):
        logical = raw - (1 << width) if kind == "s" and raw & (1 << (width - 1)) else raw
        # The viewer parses signed invalid constants as Int64, not field-width integers.
        if kind == "s":
            invalid_values = [value - (1 << 64) if value & (1 << 63) else value for value in invalid_values]
        if logical in invalid_values:
            return True, None
        physical = Decimal(logical) * Decimal(row["Lsb"]) + Decimal(row["Offset"])
    elif kind in ("f", "d"):
        size = 4 if kind == "f" else 8
        if width != size * 8 or int(row["BitPosition"]) != 7:
            raise ValueError(f"unsupported packed {kind!r} field")
        fmt = ">f" if kind == "f" else ">d"
        value = struct.unpack(fmt, raw.to_bytes(size, "big"))[0]
        if math.isnan(value):
            return True, None
        if math.isinf(value):
            return False, "-Infinity" if value < 0 else "Infinity"
        if any(value == struct.unpack(fmt, sentinel.to_bytes(size, "big"))[0] for sentinel in invalid_values):
            return True, None
        if kind == "f":
            # ConvertValue(Single) stores a Single then converts its G7 text to Double.
            lsb = struct.unpack(">f", struct.pack(">f", float(row["Lsb"])))[0]
            offset = struct.unpack(">f", struct.pack(">f", float(row["Offset"])))[0]
            scaled = struct.unpack(">f", struct.pack(">f", value * lsb + offset))[0]
            physical = Decimal(format(scaled, ".7g"))
        else:
            # The double Floor overload converts to Decimal (15 significant digits).
            physical = Decimal(format(value * float(row["Lsb"]) + float(row["Offset"]), ".15g"))
    else:
        raise ValueError(f"unsupported recorder field type {kind!r}")
    return False, _floor_text(physical, int(row["Point"]))


def decode_signal(data: bytes, row: dict[str, Any]) -> dict[str, Any]:
    """Decode one field; raw is always the unsigned wire bit pattern."""
    byte = int(row["BytePosition"])
    bit = int(row["BitPosition"])
    width = int(row["BitLength"])
    support = int(row.get("SupportDID", 0))
    if byte < 1 or not 0 <= bit <= 7 or width <= 0:
        raise ValueError("invalid PCS Data Viewer bit geometry")
    if support == 1:
        # CheckSupportDataID: same bit in the byte preceding the field byte.
        index = byte - 2
        if not 0 <= index < len(data):
            raise ValueError("support-DID bit geometry exceeds recorder payload")
        if not (data[index] >> bit) & 1:
            return {"name": row["DataName"], "supported": False, "support_did": support}
    start = (byte - 1) * 8 + 7 - bit
    raw = extract_msb0(data, start, start + width - 1)
    invalid, physical = _physical_value(raw, row)
    return {
        "name": row["DataName"],
        "raw": raw,
        "physical": physical,
        "invalid": invalid,
        "supported": True,
        "geometry": {
            "byte_position": byte, "bit_position": bit, "bit_length": width,
            "type": row["Type"], "lsb": row["Lsb"], "offset": row["Offset"],
            "point": int(row["Point"]), "support_did": support,
        },
    }


def decode_blocks(blocks: list[RecorderBlock], semantics: dict[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    result = []
    for block in blocks:
        decoded = []
        for definition in semantics.get(block.data_id, []):
            try:
                decoded.append(decode_signal(block.data, definition))
            except (ValueError, InvalidOperation, OverflowError) as exc:
                decoded.append({"name": definition["DataName"], "decode_error": str(exc)})
        result.append({
            "data_id": f"0x{block.data_id:04X}",
            "length": len(block.data),
            "data": block.data.hex(),
            "decoded": decoded,
        })
    return result


def decode_eb13(
    pdu: bytes,
    semantics: dict[int, list[dict[str, Any]]] | None = None,
    *,
    expected: tuple[int, int] | None = None,
    only: set[int] | None = None,
) -> dict[str, Any]:
    parsed = parse_eb13(pdu, expected=expected)
    if semantics is None:
        semantics = load_semantics()
    blocks = parsed.blocks if only is None else [block for block in parsed.blocks if block.data_id in only]
    return {
        "schema": "tss3-operation-ffd-decode-v1",
        "behavior_id": f"0x{parsed.behavior_id:04X}",
        "record_id": f"0x{parsed.record_id:04X}",
        "raw_response": pdu.hex(),
        "declared_block_count": parsed.declared_count,
        "parsed_block_count": len(parsed.blocks),
        "blocks": decode_blocks(blocks, semantics),
    }
