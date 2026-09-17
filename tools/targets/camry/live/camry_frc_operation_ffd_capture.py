#!/usr/bin/env python3
"""Read-only exact-Camry TSS3 Operation-FFD acquisition.

This tool targets the current FRC_P5 proprietary recorder interface recovered
from GTS+ ``GetTSS3OperationFFDP5_DT.dll``.  It uses only:

* ``22 F181`` to bind the run to the exact Camry FRC software family;
* ``10 03`` / ``10 01`` to enter/leave the ordinary P5 extended session;
* ``AB 11`` to enumerate Operation-FFD behavior/RoB codes;
* ``AB 12 <behavior:be16>`` to enumerate stored records;
* ``AB 13 <behavior:be16> <record:be16>`` to fetch a record; and
* ISO-TP flow-control frames required to receive multi-frame responses.

It performs no SecurityAccess, RoutineControl, WDBI, flash operation, Active
Test, or vehicle-control transmission.  All incoming vehicle CAN on Panda buses
0..2 is retained on the same monotonic clock, making a parked recorder read
suitable for later correlation with 0x08A/0x081 and the native FRC bus-1 plane.

The EB13 parser follows the current Toyota host exactly: byte 6 is the block
count (zero means derive the count by scanning), blocks start at byte 7, and
each block is ``data_id:be16 || length:u8 || data[length]``.  Recorder signal
names/scaling are loaded from the tracked, current PCS Data Viewer semantics
artifact rather than copied into this live tool.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, BinaryIO

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.targets.camry.live.camry_frc_lta_capture import (
    ELM327_PARAM,
    ELM327_SAFETY_MODEL,
    find_pandad_processes,
    load_panda_class,
    write_canbin_header,
    write_canbin_record,
)

SEMANTICS = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
FRC_TX = 0x792
FRC_RX = 0x79A
DIAG_BUS = 0
SILENT_SAFETY_MODEL = 0
EXPECTED_F181 = b"8646F3315000"
MAX_ISOTP_PDU = 4095
REQUEST_TIMEOUT_S = 1.5
PENDING_TIMEOUT_S = 5.0

# The default read is deliberately narrow: these are current PCS Data Viewer
# lateral/driver-control events whose snapshots are useful for request ->
# arbitration -> plant-state reconstruction. --all-robs remains read-only.
DEFAULT_ROBS = (
    0x209D,  # LCS Steer Override
    0x2818,  # Steering Angle Speed Threshold Exceeded
    0x2844,  # Lane Departure Warning Operation under LTA
    0x2845,  # LTA Hands Free Cancel
    0x2846,  # CSF Hands Free Warning Operation
    0x240E,  # LCA Reject
    0x240F,  # LCA Cancel
    0x229B, 0x229C, 0x229D, 0x229E, 0x229F,  # hands-off family
    0x22B3,  # Detection of Cut-in During Hands-off control
)

# Request/arbitration/plant-state fields called out in the acquisition report.
FOCUS_DIDS = {
    0x0501, 0x0502, 0x0507, 0x0511,  # recorder trip/time metadata
    0x5202, 0x5265,
    0x5280, 0x5281, 0x5282, 0x5284, 0x5285,
    0x550D, 0x5531, 0x560D, 0x5631,
    0x5774, 0x5776, 0x57DB, 0x57DE,
    0x5271, 0x5A04, 0x5B07,
}


class ProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class RecorderBlock:
    data_id: int
    data: bytes

    def as_json(self) -> dict[str, Any]:
        return {
            "data_id": f"0x{self.data_id:04X}",
            "length": len(self.data),
            "data": self.data.hex(),
        }


def _sf(pdu: bytes) -> bytes:
    if not 1 <= len(pdu) <= 7:
        raise ValueError(f"classic-CAN diagnostic request must be 1..7 bytes, got {len(pdu)}")
    return bytes((len(pdu),)) + pdu + bytes(7 - len(pdu))


def build_ab11() -> bytes:
    return bytes.fromhex("ab11")


def build_ab12(behavior_id: int) -> bytes:
    if not 0 <= behavior_id <= 0xFFFF:
        raise ValueError("behavior_id must fit u16")
    return bytes.fromhex("ab12") + behavior_id.to_bytes(2, "big")


def build_ab13(behavior_id: int, record_id: int) -> bytes:
    if not 0 <= behavior_id <= 0xFFFF or not 0 <= record_id <= 0xFFFF:
        raise ValueError("behavior_id/record_id must fit u16")
    return bytes.fromhex("ab13") + behavior_id.to_bytes(2, "big") + record_id.to_bytes(2, "big")


def _parse_be16_list(data: bytes, *, label: str) -> list[int]:
    if len(data) % 2:
        raise ProtocolError(f"{label}: odd-length BE16 list ({len(data)} bytes)")
    return [int.from_bytes(data[i:i + 2], "big") for i in range(0, len(data), 2)]


def parse_eb11(pdu: bytes) -> list[int]:
    if len(pdu) < 2 or pdu[:2] != bytes.fromhex("eb11"):
        raise ProtocolError(f"expected EB11 response, got {pdu.hex()}")
    return _parse_be16_list(pdu[2:], label="EB11")


def parse_eb12(pdu: bytes, behavior_id: int) -> list[int]:
    if len(pdu) < 4 or pdu[:2] != bytes.fromhex("eb12"):
        raise ProtocolError(f"expected EB12 response, got {pdu.hex()}")
    echoed = int.from_bytes(pdu[2:4], "big")
    if echoed != behavior_id:
        raise ProtocolError(f"EB12 behavior echo mismatch: expected 0x{behavior_id:04X}, got 0x{echoed:04X}")
    return _parse_be16_list(pdu[4:], label="EB12")


def _scan_blocks(buf: bytes, count: int | None) -> list[RecorderBlock]:
    blocks: list[RecorderBlock] = []
    pos = 0
    while pos < len(buf) and (count is None or len(blocks) < count):
        if len(buf) - pos < 3:
            raise ProtocolError(f"EB13 truncated block header at +0x{pos:X}")
        data_id = int.from_bytes(buf[pos:pos + 2], "big")
        length = buf[pos + 2]
        pos += 3
        end = pos + length
        if end > len(buf):
            raise ProtocolError(
                f"EB13 DID 0x{data_id:04X} length {length} overruns record: {end}>{len(buf)}")
        blocks.append(RecorderBlock(data_id=data_id, data=buf[pos:end]))
        pos = end
    if count is not None and len(blocks) != count:
        raise ProtocolError(f"EB13 block count says {count}, parsed {len(blocks)}")
    if pos != len(buf):
        raise ProtocolError(f"EB13 has {len(buf) - pos} trailing bytes after block stream")
    return blocks


def parse_eb13(pdu: bytes, behavior_id: int, record_id: int) -> tuple[int, list[RecorderBlock]]:
    if len(pdu) < 7 or pdu[:2] != bytes.fromhex("eb13"):
        raise ProtocolError(f"expected EB13 response, got {pdu.hex()}")
    echoed_behavior = int.from_bytes(pdu[2:4], "big")
    echoed_record = int.from_bytes(pdu[4:6], "big")
    if (echoed_behavior, echoed_record) != (behavior_id, record_id):
        raise ProtocolError(
            "EB13 echo mismatch: "
            f"expected 0x{behavior_id:04X}/0x{record_id:04X}, "
            f"got 0x{echoed_behavior:04X}/0x{echoed_record:04X}")
    declared_count = pdu[6]
    # Current GetTSS3OperationFFDP5_DT behavior: zero count is not "no data";
    # the parser derives a count by scanning complete blocks from byte 7.
    blocks = _scan_blocks(pdu[7:], declared_count or None)
    return declared_count, blocks


def negative_response(pdu: bytes) -> dict[str, Any] | None:
    if len(pdu) >= 3 and pdu[0] == 0x7F:
        return {"request_sid": f"0x{pdu[1]:02X}", "nrc": f"0x{pdu[2]:02X}", "raw": pdu.hex()}
    return None


def load_recorder_semantics(path: Path = SEMANTICS) -> dict[int, list[dict[str, Any]]]:
    obj = json.loads(path.read_text())
    if obj.get("schema") != "gtsplus-pcs-data-viewer-tss3-managed-semantics-v1":
        raise ValueError(f"unexpected recorder semantics schema in {path}")
    out: dict[int, list[dict[str, Any]]] = {}
    for row in obj["operation_ffd"]["detail_rows"]:
        did = str(row.get("DataID", ""))
        if len(did) != 4:
            continue
        try:
            value = int(did, 16)
        except ValueError:
            continue
        if value in FOCUS_DIDS:
            out.setdefault(value, []).append(row)
    return out


def _extract_bits_msb0(data: bytes, byte_position: int, bit_position: int, bit_length: int) -> int:
    if byte_position < 1 or not 0 <= bit_position <= 7 or bit_length <= 0:
        raise ValueError("invalid PCS Data Viewer bit geometry")
    # Toyota metadata is byte-position 1-based and bit-position 7=MSB.
    start = (byte_position - 1) * 8 + (7 - bit_position)
    end = start + bit_length
    if end > len(data) * 8:
        raise ValueError(f"signal bits {start}..{end - 1} exceed {len(data)}-byte DID payload")
    whole = int.from_bytes(data, "big")
    shift = len(data) * 8 - end
    return (whole >> shift) & ((1 << bit_length) - 1)


def _support_data_id_present(data: bytes, row: dict[str, Any]) -> bool:
    """Mirror PCS Viewer TSS3 MeasuredValue.CheckSupportDataID.

    SupportDID==1 is a record-local support-bit gate, not a UDS ReadDataByIdentifier
    capability declaration.  The host reads the byte immediately preceding the
    field byte and tests the same numeric bit position.
    """
    if int(row.get("SupportDID", 0)) != 1:
        return True
    byte_position = int(row["BytePosition"])
    bit_position = int(row["BitPosition"])
    support_index = byte_position - 2
    if support_index < 0 or support_index >= len(data) or not 0 <= bit_position <= 7:
        raise ValueError("support-DID bit geometry exceeds recorder payload")
    return bool((data[support_index] >> bit_position) & 1)


def decode_signal(data: bytes, row: dict[str, Any]) -> dict[str, Any]:
    supported = _support_data_id_present(data, row)
    if not supported:
        return {
            "name": row["DataName"],
            "supported": False,
            "support_did": int(row.get("SupportDID", 0)),
        }

    bit_length = int(row["BitLength"])
    raw_unsigned = _extract_bits_msb0(
        data, int(row["BytePosition"]), int(row["BitPosition"]), bit_length)
    kind = str(row["Type"])
    if kind == "s":
        raw: int | float = (
            raw_unsigned - (1 << bit_length)
            if raw_unsigned & (1 << (bit_length - 1))
            else raw_unsigned
        )
    elif kind == "u":
        raw = raw_unsigned
    else:
        # Every focus field currently used for request/arbitration work is u/s.
        return {
            "name": row["DataName"],
            "raw_bits": raw_unsigned,
            "decode_error": f"unsupported focus-field type {kind!r}",
        }

    try:
        physical = Decimal(str(raw)) * Decimal(str(row["Lsb"])) + Decimal(str(row["Offset"]))
        point = int(row["Point"])
        physical_text = f"{physical:.{point}f}" if point else format(physical, "f")
    except (InvalidOperation, ValueError):
        physical_text = None

    invalid = False
    for item in row.get("InvalidValueList", []):
        try:
            invalid |= raw_unsigned == int(str(item), 0)
        except ValueError:
            pass
    return {
        "name": row["DataName"],
        "raw": raw,
        "physical": physical_text,
        "invalid": invalid,
        "supported": True,
        "geometry": {
            "byte_position": row["BytePosition"],
            "bit_position": row["BitPosition"],
            "bit_length": row["BitLength"],
            "type": kind,
            "lsb": row["Lsb"],
            "offset": row["Offset"],
            "support_did": int(row.get("SupportDID", 0)),
        },
    }


def decode_blocks(blocks: list[RecorderBlock], semantics: dict[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for block in blocks:
        row = block.as_json()
        definitions = semantics.get(block.data_id, [])
        if definitions:
            decoded = []
            for definition in definitions:
                try:
                    decoded.append(decode_signal(block.data, definition))
                except ValueError as exc:
                    decoded.append({"name": definition["DataName"], "decode_error": str(exc)})
            row["decoded"] = decoded
        out.append(row)
    return out


def plan() -> dict[str, Any]:
    return {
        "schema": "camry-frc-operation-ffd-capture-v1",
        "target": {"tx": "0x792", "rx": "0x79A", "panda_bus": DIAG_BUS, "f181_contains": EXPECTED_F181.decode()},
        "session": {"enter": "10 03", "leave": "10 01"},
        "requests": {
            "identity": "22 F1 81",
            "enumerate_behavior_codes": "AB 11",
            "enumerate_records": "AB 12 || behavior_id_be16",
            "fetch_record": "AB 13 || behavior_id_be16 || record_id_be16",
        },
        "record_layout": "EB 13 || behavior_be16 || record_be16 || count_u8 || repeated(data_id_be16 || len_u8 || data)",
        "count_zero_policy": "derive the block count by scanning complete blocks from byte 7",
        "default_robs": [f"0x{x:04X}" for x in DEFAULT_ROBS],
        "focus_dids": [f"0x{x:04X}" for x in sorted(FOCUS_DIDS)],
        "can_capture": "all incoming Panda buses 0..2 on the same monotonic clock",
        "safety": {"model": "ELM327", "numeric": ELM327_SAFETY_MODEL, "param": ELM327_PARAM},
        "security_access": False,
        "routine_control": False,
        "write_data_by_identifier": False,
        "flash_write": False,
        "active_test": False,
        "vehicle_control_tx": False,
    }


class Transport:
    def __init__(self, panda, can_stream: BinaryIO) -> None:
        self.panda = panda
        self.can_stream = can_stream
        self.frames_by_bus = {"0": 0, "1": 0, "2": 0}

    def _drain(self) -> list[tuple[int, bytes, int, int]]:
        now = time.monotonic_ns()
        out = []
        for address, data, bus in self.panda.can_recv() or []:
            payload = bytes(data)
            if 0 <= bus <= 2:
                write_canbin_record(self.can_stream, now, bus, int(address), payload)
                self.frames_by_bus[str(bus)] += 1
                out.append((int(address), payload, int(bus), now))
        return out

    def request(self, pdu: bytes, *, timeout_s: float = REQUEST_TIMEOUT_S) -> bytes:
        self.panda.can_send(FRC_TX, _sf(pdu), DIAG_BUS)
        deadline = time.monotonic() + timeout_s
        assembly: bytearray | None = None
        total = 0
        next_sn = 1
        while time.monotonic() < deadline:
            for address, frame, bus, _t_ns in self._drain():
                if address != FRC_RX or bus != DIAG_BUS or not frame:
                    continue
                pci = frame[0] >> 4
                if pci == 0:
                    length = frame[0] & 0x0F
                    if not 1 <= length <= 7 or 1 + length > len(frame):
                        raise ProtocolError(f"invalid ISO-TP single frame: {frame.hex()}")
                    response = frame[1:1 + length]
                    if response[:3] == bytes((0x7F, pdu[0], 0x78)):
                        deadline = time.monotonic() + PENDING_TIMEOUT_S
                        continue
                    return response
                if pci == 1:
                    if len(frame) < 8:
                        raise ProtocolError(f"short ISO-TP first frame: {frame.hex()}")
                    total = ((frame[0] & 0x0F) << 8) | frame[1]
                    if total <= 7 or total > MAX_ISOTP_PDU:
                        raise ProtocolError(f"unsupported ISO-TP response length {total}")
                    assembly = bytearray(frame[2:])
                    next_sn = 1
                    self.panda.can_send(FRC_TX, bytes.fromhex("3000000000000000"), DIAG_BUS)
                    if len(assembly) >= total:
                        return bytes(assembly[:total])
                    continue
                if pci == 2 and assembly is not None:
                    sn = frame[0] & 0x0F
                    if sn != next_sn:
                        raise ProtocolError(f"ISO-TP sequence mismatch: expected {next_sn}, got {sn}")
                    assembly.extend(frame[1:])
                    next_sn = (next_sn + 1) & 0x0F
                    if len(assembly) >= total:
                        response = bytes(assembly[:total])
                        if response[:3] == bytes((0x7F, pdu[0], 0x78)):
                            assembly = None
                            deadline = time.monotonic() + PENDING_TIMEOUT_S
                            continue
                        return response
            time.sleep(0.001)
        raise TimeoutError(f"FRC request timed out: {pdu.hex()}")

    def settle(self, duration_s: float = 0.05) -> None:
        end = time.monotonic() + duration_s
        while time.monotonic() < end:
            self._drain()
            time.sleep(0.001)


def _require_positive(response: bytes, prefix: bytes, label: str) -> None:
    neg = negative_response(response)
    if neg is not None:
        raise ProtocolError(f"{label}: negative response {neg}")
    if not response.startswith(prefix):
        raise ProtocolError(f"{label}: expected {prefix.hex()}, got {response.hex()}")


def _write_jsonl(stream, row: dict[str, Any]) -> None:
    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    stream.flush()


def execute(out_dir: Path, *, requested_robs: list[int], all_robs: bool,
            max_records_per_rob: int) -> int:
    if max_records_per_rob <= 0:
        raise SystemExit("--max-records-per-rob must be positive")
    running = find_pandad_processes()
    if running:
        details = "; ".join(f"pid={pid} {cmd}" for pid, cmd in running)
        raise SystemExit(f"refusing Panda USB collision: pandad is running ({details})")

    Panda = load_panda_class()
    serials = Panda.list()
    if len(serials) != 1:
        raise SystemExit(f"expected exactly one Panda, found {len(serials)}: {serials}")

    semantics = load_recorder_semantics()
    out_dir.mkdir(parents=True, exist_ok=False)
    can_path = out_dir / "can.bin"
    records_path = out_dir / "records.ndjson"
    result_path = out_dir / "operation_ffd.json"
    started_ns = time.monotonic_ns()
    result: dict[str, Any] = {
        "schema": "camry-frc-operation-ffd-capture-v1",
        "started_monotonic_ns": started_ns,
        "plan": plan(),
        "available_robs": [],
        "selected_robs": [],
        "robs": {},
        "error": None,
    }

    panda = Panda(serials[0])
    entered_extended = False
    transport: Transport | None = None
    try:
        panda.set_safety_mode(ELM327_SAFETY_MODEL, ELM327_PARAM)
        with can_path.open("wb", buffering=1024 * 1024) as can_stream, records_path.open("w", buffering=1) as records_stream:
            write_canbin_header(can_stream)
            transport = Transport(panda, can_stream)
            transport.settle()

            identity = transport.request(bytes.fromhex("22f181"))
            _require_positive(identity, bytes.fromhex("62f181"), "F181")
            if EXPECTED_F181 not in identity[3:]:
                raise ProtocolError(
                    f"wrong FRC software identity; expected {EXPECTED_F181.decode()} in {identity[3:].hex()}")
            result["identity_response"] = identity.hex()

            session = transport.request(bytes.fromhex("1003"))
            _require_positive(session, bytes.fromhex("5003"), "extended session")
            entered_extended = True
            result["extended_session_response"] = session.hex()

            response = transport.request(build_ab11())
            neg = negative_response(response)
            if neg is not None:
                result["ab11_negative_response"] = neg
                raise ProtocolError(f"AB11 rejected: {neg}")
            available = parse_eb11(response)
            result["ab11_response"] = response.hex()
            result["available_robs"] = [f"0x{x:04X}" for x in available]

            if requested_robs:
                wanted = requested_robs
            elif all_robs:
                wanted = available
            else:
                wanted = [x for x in DEFAULT_ROBS if x in set(available)]
            selected = [x for x in wanted if x in set(available)]
            result["selected_robs"] = [f"0x{x:04X}" for x in selected]
            result["requested_but_absent"] = [f"0x{x:04X}" for x in wanted if x not in set(available)]

            for behavior_id in selected:
                key = f"0x{behavior_id:04X}"
                b12 = transport.request(build_ab12(behavior_id))
                neg = negative_response(b12)
                if neg is not None:
                    result["robs"][key] = {"ab12_negative_response": neg, "records": []}
                    continue
                record_ids = parse_eb12(b12, behavior_id)
                row: dict[str, Any] = {
                    "ab12_response": b12.hex(),
                    "record_ids": [f"0x{x:04X}" for x in record_ids],
                    "truncated": len(record_ids) > max_records_per_rob,
                    "records": [],
                }
                result["robs"][key] = row
                for record_id in record_ids[:max_records_per_rob]:
                    b13 = transport.request(build_ab13(behavior_id, record_id))
                    neg = negative_response(b13)
                    if neg is not None:
                        record = {
                            "behavior_id": key,
                            "record_id": f"0x{record_id:04X}",
                            "negative_response": neg,
                        }
                    else:
                        declared_count, blocks = parse_eb13(b13, behavior_id, record_id)
                        record = {
                            "behavior_id": key,
                            "record_id": f"0x{record_id:04X}",
                            "raw_response": b13.hex(),
                            "declared_block_count": declared_count,
                            "parsed_block_count": len(blocks),
                            "blocks": decode_blocks(blocks, semantics),
                            "focus_data_ids_present": [
                                f"0x{b.data_id:04X}" for b in blocks if b.data_id in FOCUS_DIDS
                            ],
                        }
                    row["records"].append(record)
                    _write_jsonl(records_stream, record)

            transport.settle()
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        if transport is not None and entered_extended:
            try:
                reset = transport.request(bytes.fromhex("1001"), timeout_s=0.75)
                result["default_session_response"] = reset.hex()
            except Exception as exc:  # preserve the primary failure; report cleanup separately
                result["default_session_error"] = f"{type(exc).__name__}: {exc}"
        if transport is not None:
            result["frames_by_bus"] = transport.frames_by_bus
            try:
                transport.settle()
            except Exception:
                pass
        try:
            panda.set_safety_mode(SILENT_SAFETY_MODEL)
        finally:
            result["finished_monotonic_ns"] = time.monotonic_ns()
            result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "out_dir": str(out_dir),
        "available_robs": result["available_robs"],
        "selected_robs": result["selected_robs"],
        "frames_by_bus": result.get("frames_by_bus", {}),
    }, indent=2))
    return 0


def _parse_u16(text: str) -> int:
    value = int(text, 0)
    if not 0 <= value <= 0xFFFF:
        raise argparse.ArgumentTypeError("value must fit u16")
    return value


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", type=Path, metavar="OUT_DIR", help="perform the read-only capture")
    ap.add_argument("--rob", action="append", type=_parse_u16, default=[], help="behavior/RoB code to fetch (repeatable)")
    ap.add_argument("--all-robs", action="store_true", help="fetch every behavior code returned by AB11")
    ap.add_argument("--max-records-per-rob", type=int, default=128)
    args = ap.parse_args()
    if args.rob and args.all_robs:
        ap.error("--rob and --all-robs are mutually exclusive")
    if args.execute is None:
        print(json.dumps(plan(), indent=2, sort_keys=True))
        return 0
    return execute(args.execute, requested_robs=args.rob, all_robs=args.all_robs,
                   max_records_per_rob=args.max_records_per_rob)


if __name__ == "__main__":
    raise SystemExit(main())
