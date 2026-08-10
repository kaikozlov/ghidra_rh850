#!/usr/bin/env python3
"""Analyze Toyota classic-CAN SecOC captures and DataFlash candidates.

This tool is intentionally vehicle-agnostic within the classic Toyota SecOC
format recovered from the Sienna firmware and independently present in pinned
opendbc. It does not assume that steering IDs are present, and it does not
assume a particular Panda bus number.

Capture input is newline-delimited JSON with at least:

    {"addr": 278, "bus": 1, "data": "0011..."}

The synchronization frame (default CAN 0x00F) establishes trip/reset freshness
state per observed bus. Protected messages are associated with the most recent
sync frame on the same bus. Known classic protected IDs are loaded from
``data/toyota_classic_secoc_profile.csv``; callers may restrict them.

The ``scan`` command tests every sliding 16-byte DataFlash window against one
or more synchronization samples first, then fully verifies surviving candidates
against synchronization and protected traffic. Raw keys are never printed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_secoc_signer import (
    AES_128_KEY_BYTES,
    build_normal_authenticated_input,
    build_sync_authenticated_input,
)
from Crypto.Cipher import AES
from Crypto.Hash import CMAC

PROFILE_PATH = REPO / "data" / "toyota_classic_secoc_profile.csv"
SYNC_CAN_ID = 0x00F


@dataclass(frozen=True)
class ProfileEntry:
    can_id: int
    name: str
    kind: str
    wire_bytes: int
    authenticator_bits: int
    reset_flag_bits: int
    msg_counter_flag_bits: int


@dataclass(frozen=True)
class SyncSample:
    bus: int
    trip: int
    reset: int
    authenticator: int


@dataclass(frozen=True)
class ProtectedSample:
    bus: int
    can_id: int
    payload4: bytes
    transmitted_freshness_nibble: int
    authenticator: int
    trip: int
    reset: int


def load_profile(path: Path = PROFILE_PATH) -> list[ProfileEntry]:
    rows: list[ProfileEntry] = []
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            rows.append(
                ProfileEntry(
                    can_id=int(row["can_id"], 0),
                    name=row["name"],
                    kind=row["kind"],
                    wire_bytes=int(row["wire_bytes"]),
                    authenticator_bits=int(row["authenticator_bits"]),
                    reset_flag_bits=int(row["reset_flag_bits"]),
                    msg_counter_flag_bits=int(row["msg_counter_flag_bits"]),
                )
            )
    return rows


def known_protected_ids() -> set[int]:
    return {entry.can_id for entry in load_profile() if entry.kind == "protected"}


def cmac_msb28(key: bytes, authenticated_input: bytes) -> int:
    if len(key) != AES_128_KEY_BYTES:
        raise ValueError("key must be exactly 16 bytes")
    cmac = CMAC.new(key, ciphermod=AES)
    cmac.update(authenticated_input)
    return int.from_bytes(cmac.digest()[:4], "big") >> 4


def decode_sync_frame(data: bytes) -> tuple[int, int, int]:
    if len(data) != 8:
        raise ValueError("classic synchronization frame must be exactly 8 bytes")
    raw = int.from_bytes(data, "big")
    authenticator = raw & 0x0FFFFFFF
    freshness = raw >> 28
    trip = freshness >> 20
    reset = freshness & 0xFFFFF
    return trip, reset, authenticator


def decode_protected_frame(data: bytes) -> tuple[bytes, int, int]:
    if len(data) != 8:
        raise ValueError("classic protected frame must be exactly 8 bytes")
    trailer = int.from_bytes(data[4:8], "big")
    return data[:4], trailer >> 28, trailer & 0x0FFFFFFF


def iter_capture(path: Path) -> Iterable[tuple[int, int, bytes]]:
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                can_id = int(row["addr"])
                bus = int(row["bus"])
                data = bytes.fromhex(str(row["data"]))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                raise ValueError(f"invalid capture row {line_no}: {error}") from error
            yield can_id, bus, data


def load_capture(
    path: Path,
    *,
    protected_ids: set[int] | None = None,
    buses: set[int] | None = None,
    sync_can_id: int = SYNC_CAN_ID,
) -> tuple[list[SyncSample], list[ProtectedSample], dict[str, object]]:
    if protected_ids is None:
        protected_ids = known_protected_ids()

    latest_sync: dict[int, SyncSample] = {}
    sync_samples: list[SyncSample] = []
    protected_samples: list[ProtectedSample] = []
    counts: Counter[tuple[int, int]] = Counter()
    orphan_protected: Counter[tuple[int, int]] = Counter()

    for can_id, bus, data in iter_capture(path):
        if buses is not None and bus not in buses:
            continue
        counts[(bus, can_id)] += 1
        if can_id == sync_can_id:
            if len(data) != 8:
                continue
            trip, reset, authenticator = decode_sync_frame(data)
            sample = SyncSample(bus, trip, reset, authenticator)
            latest_sync[bus] = sample
            sync_samples.append(sample)
        elif can_id in protected_ids:
            if len(data) != 8:
                continue
            current = latest_sync.get(bus)
            if current is None:
                orphan_protected[(bus, can_id)] += 1
                continue
            payload4, nibble, authenticator = decode_protected_frame(data)
            protected_samples.append(
                ProtectedSample(
                    bus=bus,
                    can_id=can_id,
                    payload4=payload4,
                    transmitted_freshness_nibble=nibble,
                    authenticator=authenticator,
                    trip=current.trip,
                    reset=current.reset,
                )
            )

    summary = {
        "counts": {
            f"bus{bus}:0x{can_id:03X}": count
            for (bus, can_id), count in sorted(counts.items())
            if can_id == sync_can_id or can_id in protected_ids
        },
        "orphan_protected": {
            f"bus{bus}:0x{can_id:03X}": count
            for (bus, can_id), count in sorted(orphan_protected.items())
        },
        "buses_with_sync": sorted(latest_sync),
    }
    return sync_samples, protected_samples, summary


def verify_sync_sample(key: bytes, sample: SyncSample, sync_can_id: int = SYNC_CAN_ID) -> bool:
    return cmac_msb28(
        key,
        build_sync_authenticated_input(sample.trip, sample.reset, sync_can_id),
    ) == sample.authenticator


def candidate_message_counters(sample: ProtectedSample) -> Iterable[int]:
    reset_flag = sample.transmitted_freshness_nibble & 0x3
    if reset_flag != (sample.reset & 0x3):
        return ()
    low2 = sample.transmitted_freshness_nibble >> 2
    return range(low2, 256, 4)


def verify_protected_sample(key: bytes, sample: ProtectedSample) -> tuple[bool, int | None]:
    for message_counter in candidate_message_counters(sample):
        authenticated_input = build_normal_authenticated_input(
            sample.can_id,
            sample.payload4,
            sample.trip,
            sample.reset,
            message_counter,
        )
        if cmac_msb28(key, authenticated_input) == sample.authenticator:
            return True, message_counter
    return False, None


def verify_key(
    key: bytes,
    sync_samples: list[SyncSample],
    protected_samples: list[ProtectedSample],
) -> dict[str, object]:
    sync_matches = sum(verify_sync_sample(key, sample) for sample in sync_samples)
    by_id: dict[int, list[ProtectedSample]] = defaultdict(list)
    for sample in protected_samples:
        by_id[sample.can_id].append(sample)

    protected: dict[str, dict[str, int]] = {}
    for can_id, samples in sorted(by_id.items()):
        matches = sum(verify_protected_sample(key, sample)[0] for sample in samples)
        protected[f"0x{can_id:03X}"] = {"matches": matches, "total": len(samples)}

    return {
        "sync": {"matches": sync_matches, "total": len(sync_samples)},
        "protected": protected,
    }


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def iter_key_windows(blob: bytes, *, min_entropy: float = 0.0) -> Iterable[tuple[int, bytes, float]]:
    seen: set[bytes] = set()
    for offset in range(0, len(blob) - AES_128_KEY_BYTES + 1):
        key = blob[offset : offset + AES_128_KEY_BYTES]
        if key in seen:
            continue
        seen.add(key)
        entropy = shannon_entropy(key)
        if entropy >= min_entropy:
            yield offset, key, entropy


def scan_dump(
    dump: bytes,
    sync_samples: list[SyncSample],
    protected_samples: list[ProtectedSample],
    *,
    min_entropy: float = 3.0,
    sync_probes: int = 3,
) -> list[dict[str, object]]:
    if not sync_samples:
        raise ValueError("at least one synchronization sample is required for dump scanning")
    probes = sync_samples[: max(1, sync_probes)]
    matches: list[dict[str, object]] = []
    for offset, key, entropy in iter_key_windows(dump, min_entropy=min_entropy):
        if not all(verify_sync_sample(key, sample) for sample in probes):
            continue
        result = verify_key(key, sync_samples, protected_samples)
        matches.append(
            {
                "offset": offset,
                "sha256": hashlib.sha256(key).hexdigest(),
                "entropy": entropy,
                "verification": result,
            }
        )
    return matches


def parse_can_ids(values: list[str] | None) -> set[int] | None:
    if not values:
        return None
    return {int(value, 0) for value in values}


def parse_buses(values: list[str] | None) -> set[int] | None:
    if not values:
        return None
    return {int(value, 0) for value in values}


def parse_key(value: str) -> bytes:
    try:
        key = bytes.fromhex(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("key must be hexadecimal") from error
    if len(key) != AES_128_KEY_BYTES:
        raise argparse.ArgumentTypeError("key must encode exactly 16 bytes")
    return key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("profile", help="emit the known classic Toyota SecOC profile")

    verify = sub.add_parser("verify", help="verify a candidate key against a capture")
    verify.add_argument("--capture", required=True, type=Path)
    verify.add_argument("--key", required=True, type=parse_key)
    verify.add_argument("--protected-id", action="append", dest="protected_ids")
    verify.add_argument("--bus", action="append", dest="buses")

    scan = sub.add_parser("scan", help="scan a DataFlash dump using capture synchronization")
    scan.add_argument("--capture", required=True, type=Path)
    scan.add_argument("--dump", required=True, type=Path)
    scan.add_argument("--protected-id", action="append", dest="protected_ids")
    scan.add_argument("--bus", action="append", dest="buses")
    scan.add_argument("--base-address", type=lambda value: int(value, 0), default=0xFF200000)
    scan.add_argument("--min-entropy", type=float, default=3.0)
    scan.add_argument("--sync-probes", type=int, default=3)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "profile":
        print(json.dumps([entry.__dict__ for entry in load_profile()], indent=2))
        return 0

    protected_ids = parse_can_ids(args.protected_ids)
    buses = parse_buses(args.buses)
    sync_samples, protected_samples, summary = load_capture(
        args.capture,
        protected_ids=protected_ids,
        buses=buses,
    )

    output: dict[str, object] = {
        "capture": str(args.capture),
        "summary": summary,
        "sync_samples": len(sync_samples),
        "protected_samples": len(protected_samples),
    }

    if args.command == "verify":
        output["verification"] = verify_key(args.key, sync_samples, protected_samples)
    else:
        dump = args.dump.read_bytes()
        found = scan_dump(
            dump,
            sync_samples,
            protected_samples,
            min_entropy=args.min_entropy,
            sync_probes=args.sync_probes,
        )
        for candidate in found:
            candidate["address"] = args.base_address + int(candidate["offset"])
        output["dump"] = str(args.dump)
        output["candidates"] = found

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
