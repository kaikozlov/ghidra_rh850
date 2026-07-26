#!/usr/bin/env python3
"""Generate the application receive I-PDU / COM signal map as CSV.

Raw-table facts (acceptance rules, normal Rx descriptors, COM PDU descriptors,
buffer offsets, signal-to-PDU map, signal properties, timeout/update RAM roots,
SecOC record IDs) are derived only from the committed CodeFlash image.

Recovered extraction columns come from the companion evidence artifact
`data/application_rx_signal_evidence.csv` produced by the read-only Ghidra
exporter ExportApplicationRxSignalEvidence.java. Signals absent from that
artifact remain configured-unresolved. No OEM/DBC names are invented.
"""
from __future__ import annotations

import argparse
import csv
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
EVIDENCE_PATH = REPO / "data" / "application_rx_signal_evidence.csv"

ACCEPTANCE = 0x231A0
RX_DESC = 0x22018
COM_PDU = 0x2273C
BUF_OFF = 0x228E4
SIG2PDU = 0x224E4
SIGPROP = 0x223B8
SECOC_RECORDS = 0x25970
SECOC_RECORD_SIZE = 0x50
SECOC_COUNT = 6
COM_BUF_RAM = 0xFEBE4A49
VALIDITY_RAM = 0xFEBE52CC
UPDATE_COUNTER_RAM = 0xFEBE532C
RX_INDICATION = 0x7C640

PDU = struct.Struct("<HBBHBB")
RULE = struct.Struct("<IIII")
DESC = struct.Struct("<II")

NORMAL_COUNT = 47
COM_PDU_COUNT = 53
TX_PDU_COUNT = 6
SIGNAL_COUNT = 300
RX_SIGNAL_FIRST = 58

DIAG_CAN_IDS = (0x7A1, 0x777, 0x7A0, 0x7F7)

FIELDNAMES = [
    "row_kind",
    "rx_pdu_id",
    "acceptance_index",
    "can_id",
    "can_format",
    "frame_length",
    "com_length",
    "timeout_ticks",
    "com_flags",
    "com_buf_off",
    "com_buf_ram",
    "acceptance_filter_route",
    "rx_callback",
    "unpacker",
    "validity_state_ram",
    "update_counter_ram",
    "pdu_first_consumer",
    "secoc_envelope",
    "signal_id",
    "signal_property",
    "wire_field",
    "endianness",
    "bit_length",
    "start_arg",
    "signed",
    "dest_kind",
    "dest",
    "dest_width",
    "signal_update_state",
    "first_consumer",
    "evidence_status",
    "call_site",
    "notes",
]


def u16(offset: int) -> int:
    return struct.unpack_from("<H", CF, offset)[0]


def u32(offset: int) -> int:
    return struct.unpack_from("<I", CF, offset)[0]


def normal_descriptors():
    return [DESC.unpack_from(CF, RX_DESC + DESC.size * i) for i in range(NORMAL_COUNT)]


def acceptance_rules():
    return [RULE.unpack_from(CF, ACCEPTANCE + RULE.size * i) for i in range(51)]


def com_pdu_rows():
    return [PDU.unpack_from(CF, COM_PDU + PDU.size * i) for i in range(COM_PDU_COUNT)]


def buffer_offsets():
    return [u16(BUF_OFF + 2 * i) for i in range(COM_PDU_COUNT)]


def signal_to_pdu():
    return [u16(SIG2PDU + 2 * i) for i in range(SIGNAL_COUNT)]


def signal_properties():
    return list(CF[SIGPROP:SIGPROP + SIGNAL_COUNT])


def secoc_can_ids() -> set[int]:
    return {u16(SECOC_RECORDS + i * SECOC_RECORD_SIZE + 0x0A) for i in range(SECOC_COUNT)}


def can_format(software_id: int) -> str:
    return "fd" if (software_id & 0x40000000) else "classic"


def std_can_id(software_id: int) -> int:
    return software_id & 0x7FF


def wire_field(pdu: int, abs_buf_off: int, bit_len: int, start_arg: int, kind: str, offs: list[int]) -> str:
    plen = com_pdu_rows()[pdu][3]
    if kind == "opaque_pdu_bytes":
        return f"B0..B{plen - 1} opaque"
    rel = abs_buf_off - offs[pdu]
    if bit_len == 1:
        return f"B{rel}[{start_arg}]"
    if start_arg == 0 and bit_len % 8 == 0:
        nbytes = bit_len // 8
        return f"B{rel}" if nbytes == 1 else f"B{rel}..B{rel + nbytes - 1} BE{bit_len}"
    if start_arg + bit_len <= 8:
        msb = start_arg + bit_len - 1
        lsb = start_arg
        return f"B{rel}[{msb}]" if msb == lsb else f"B{rel}[{msb}:{lsb}]"
    return f"B{rel}/start{start_arg}/len{bit_len}"


def load_evidence(path: Path) -> dict[int, dict]:
    if not path.is_file():
        raise FileNotFoundError(
            f"missing evidence artifact {path}; run tools/generate_application_rx_signal_evidence.sh"
        )
    out: dict[int, dict] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            sid = int(row["signal_id"])
            out[sid] = {
                "extract_kind": row["extract_kind"],
                "unpacker": row["unpacker"],
                "body_size": int(row["body_size"]),
                "body_sha256": row["body_sha256"],
                "call_site": row["call_site"],
                "buf_off": int(row["buf_off"]),
                "bit_len": int(row["bit_len"]),
                "start_arg": int(row["start_arg"]),
                "signed": int(row["signed"]),
                "dest": row["dest"],
                "dest_width": int(row["dest_width"]),
                "first_consumer": row["first_consumer"],
                "window_lo": row["window_lo"],
                "window_hi": row["window_hi"],
            }
    return out


def build_rows(evidence: dict[int, dict]) -> list[dict[str, str]]:
    descs = normal_descriptors()
    rules = acceptance_rules()
    pdus = com_pdu_rows()
    offs = buffer_offsets()
    s2p = signal_to_pdu()
    props = signal_properties()
    secoc_ids = secoc_can_ids()

    pdu_unpacker: dict[int, str] = {}
    for sid, info in evidence.items():
        pdu_unpacker.setdefault(s2p[sid], info["unpacker"])

    rows: list[dict[str, str]] = []
    for index in range(NORMAL_COUNT):
        pdu_id = TX_PDU_COUNT + index
        soft_id, hw_len = descs[index]
        can_id = std_can_id(soft_id)
        cycle, _b1, _b2, com_len, _b4, flags = pdus[pdu_id]
        off = offs[pdu_id]
        rule = rules[index]
        secoc = "yes" if can_id in secoc_ids else "no"
        unpacker = pdu_unpacker.get(pdu_id, "none")
        if unpacker == "none":
            pdu_consumer = (
                "configured-unresolved; bound=no generated COM unpacker watching "
                f"update counter FEBE532C[{pdu_id}]; frame still copied by RxIndication"
            )
        else:
            pdu_consumer = unpacker

        sigs = [sid for sid in range(RX_SIGNAL_FIRST, SIGNAL_COUNT) if s2p[sid] == pdu_id]
        for sid in sigs:
            info = evidence.get(sid)
            base = {
                "row_kind": "signal",
                "rx_pdu_id": str(pdu_id),
                "acceptance_index": str(index),
                "can_id": f"0x{can_id:X}",
                "can_format": can_format(soft_id),
                "frame_length": str(hw_len),
                "com_length": str(com_len),
                "timeout_ticks": str(cycle),
                "com_flags": f"0x{flags:02X}",
                "com_buf_off": str(off),
                "com_buf_ram": f"0x{COM_BUF_RAM + off:X}",
                "acceptance_filter_route": (
                    f"rule[{index}] hw_label={rule[1] >> 16} route={rule[2]}"
                ),
                "rx_callback": f"0x{RX_INDICATION:X}",
                "unpacker": unpacker,
                "validity_state_ram": f"0x{VALIDITY_RAM + pdu_id:X}",
                "update_counter_ram": f"0x{UPDATE_COUNTER_RAM + pdu_id:X}",
                "pdu_first_consumer": pdu_consumer,
                "secoc_envelope": secoc,
                "signal_id": str(sid),
                "signal_property": str(props[sid]),
                "signal_update_state": (
                    f"shares PDU update counter 0x{UPDATE_COUNTER_RAM + pdu_id:X}"
                ),
            }
            if info is None:
                base.update({
                    "wire_field": "configured-unresolved",
                    "endianness": "configured-unresolved",
                    "bit_length": "configured-unresolved",
                    "start_arg": "configured-unresolved",
                    "signed": "configured-unresolved",
                    "dest_kind": "configured-unresolved",
                    "dest": "configured-unresolved",
                    "dest_width": "configured-unresolved",
                    "first_consumer": (
                        "configured-unresolved; bound=absent from "
                        "application_rx_signal_evidence.csv "
                        "(no parseable 0x7C03E call / opaque table row)"
                    ),
                    "evidence_status": "configured-unresolved",
                    "call_site": "",
                    "notes": (
                        "Signal present in 0x224E4 map and property table; "
                        "no committed extraction evidence row"
                    ),
                })
            else:
                dest = info["dest"]
                if dest.startswith("0x"):
                    dest_kind = "ram"
                elif dest.startswith("COM+"):
                    dest_kind = "com_opaque"
                else:
                    dest_kind = "other"
                endian = "big" if info["extract_kind"] == "bitfield" else "opaque"
                base.update({
                    "unpacker": info["unpacker"],
                    "wire_field": wire_field(
                        pdu_id, info["buf_off"], info["bit_len"], info["start_arg"],
                        info["extract_kind"], offs,
                    ),
                    "endianness": endian,
                    "bit_length": str(info["bit_len"]),
                    "start_arg": str(info["start_arg"]),
                    "signed": str(info["signed"]),
                    "dest_kind": dest_kind,
                    "dest": dest,
                    "dest_width": str(info["dest_width"]),
                    "first_consumer": info["first_consumer"],
                    "evidence_status": "recovered",
                    "call_site": info["call_site"],
                    "notes": (
                        f"extract={info['extract_kind']}; buf_off={info['buf_off']}; "
                        f"evidence_window={info['window_lo']}-{info['window_hi']}; "
                        f"body_sha256={info['body_sha256'][:16]}…"
                    ),
                })
            rows.append(base)
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO / "data" / "application_rx_map.csv",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=EVIDENCE_PATH,
        help="companion evidence CSV from ExportApplicationRxSignalEvidence",
    )
    args = parser.parse_args()
    evidence = load_evidence(args.evidence)
    rows = build_rows(evidence)
    write_csv(args.output, rows)
    n_sig = sum(1 for r in rows if r["row_kind"] == "signal")
    n_pdu = len({int(r["rx_pdu_id"]) for r in rows})
    n_rec = sum(1 for r in rows if r["evidence_status"] == "recovered")
    n_unres = sum(1 for r in rows if r["evidence_status"] == "configured-unresolved")
    print(
        f"Wrote {args.output} rows={len(rows)} pdus={n_pdu} signals={n_sig} "
        f"recovered={n_rec} configured-unresolved={n_unres} "
        f"evidence={len(evidence)}"
    )


if __name__ == "__main__":
    main()
