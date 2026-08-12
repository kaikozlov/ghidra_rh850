#!/usr/bin/env python3
"""Join Ghidra Tx staging references to the generated application Tx signal map.

The Ghidra exporter discovers the source-address set from the six packer bodies.
This script only attaches existing structural signal metadata and classifies each
reference by role. It does not assign semantic field names.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_MAP = REPO / "data" / "application_tx_map.csv"
DEFAULT_REFS = REPO / "build" / "application_tx_producer_refs.csv"
DEFAULT_OUT = REPO / "data" / "application_tx_producer_evidence.csv"

FIELDS = [
    "tx_pdu_id",
    "can_id",
    "message_name",
    "signal_id",
    "wire_field",
    "source_ram",
    "ref_from",
    "ref_type",
    "ref_role",
    "owner_entry",
    "owner_name",
    "owner_body_size",
    "owner_body_sha256",
]


def parse_int(value: str) -> int:
    return int(value, 0)


def ref_role(signal: dict[str, str], ref: dict[str, str]) -> str:
    owner = ref["owner_name"]
    ref_type = ref["ref_type"].upper()
    packer = parse_int(signal["packer"])
    owner_entry = parse_int(ref["owner_entry"])

    if ref_type == "READ" and owner_entry == packer:
        return "packer-read"
    if ref_type == "WRITE" and owner == "application_ram_default_init":
        return "default-init-write"
    if ref_type == "WRITE":
        return "producer-write"
    if ref_type == "READ":
        return "other-read"
    if ref_type == "DATA":
        return "data-reference"
    return "other-reference"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", type=Path, default=DEFAULT_MAP)
    ap.add_argument("--refs", type=Path, default=DEFAULT_REFS)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    with args.map.open(newline="", encoding="utf-8") as stream:
        signals = [row for row in csv.DictReader(stream) if row["source_kind"] == "ram"]
    with args.refs.open(newline="", encoding="utf-8") as stream:
        refs = list(csv.DictReader(stream))

    refs_by_source: dict[int, list[dict[str, str]]] = {}
    for row in refs:
        refs_by_source.setdefault(parse_int(row["source_ram"]), []).append(row)

    rows: list[dict[str, str]] = []
    missing: list[str] = []
    for signal in signals:
        source = parse_int(signal["source"])
        source_refs = refs_by_source.get(source, [])
        if not source_refs:
            missing.append(signal["source"])
            continue
        for ref in source_refs:
            rows.append(
                {
                    "tx_pdu_id": signal["tx_pdu_id"],
                    "can_id": signal["can_id"],
                    "message_name": signal["message_name"],
                    "signal_id": signal["signal_id"],
                    "wire_field": signal["wire_field"],
                    "source_ram": signal["source"],
                    "ref_from": ref["ref_from"],
                    "ref_type": ref["ref_type"],
                    "ref_role": ref_role(signal, ref),
                    "owner_entry": ref["owner_entry"],
                    "owner_name": ref["owner_name"],
                    "owner_body_size": ref["owner_body_size"],
                    "owner_body_sha256": ref["owner_body_sha256"],
                }
            )

    if missing:
        raise SystemExit(f"RAM-backed Tx signals missing Ghidra refs: {sorted(set(missing))}")

    rows.sort(
        key=lambda row: (
            int(row["signal_id"]),
            parse_int(row["ref_from"]),
            row["ref_type"],
        )
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    sources = {parse_int(row["source_ram"]) for row in rows}
    producers = {
        parse_int(row["owner_entry"])
        for row in rows
        if row["ref_role"] == "producer-write"
    }
    print(
        f"application Tx producer evidence: signals={len(signals)} "
        f"sources={len(sources)} refs={len(rows)} producers={len(producers)}"
    )


if __name__ == "__main__":
    main()
