#!/usr/bin/env python3
"""Reduce normal loggerd rlogs to the Camry FRC operating-state capture format.

This is the preferred companion to kai-openpilot's DEVELOPMENT_ONLY
``ToyotaTSS3FrcOracleCapture`` path. The live car keeps normal ``pandad`` ownership;
``card`` emits only fixed FRC SID-0x22 reads through its existing ``sendcan``
publisher, and loggerd records both the requests and incoming responses.

The reducer writes the same ``can.bin`` / ``oracle.ndjson`` / ``metadata.json``
shape consumed by :mod:`tools.analyze_camry_frc_lta_capture`, without retaining
GPS, video, route names, or unrelated logged services.

Each input is explicit ``SEGMENT=PATH`` so source identities are deterministic,
e.g.::

  tools/extract_camry_frc_lta_rlog.py build/tmp/camry-lta \
    26=/tmp/26-rlog.zst 27=/tmp/27-rlog.zst

Run in an openpilot Python environment that provides ``LogReader``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.camry_frc_lta_capture import (
    ACC_OPERATION_DID,
    ACC_OPERATION_RDBI_REQUEST,
    FRC_DID,
    FRC_RX,
    FRC_TX,
    UDS_RDBI_REQUEST,
    parse_frc_response,
    write_canbin_header,
    write_canbin_record,
)

FRC_BUS = 0
KNOWN_REQUESTS = {
    UDS_RDBI_REQUEST: FRC_DID,
    ACC_OPERATION_RDBI_REQUEST: ACC_OPERATION_DID,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_input(spec: str) -> tuple[int, Path]:
    segment_s, sep, path_s = spec.partition("=")
    if not sep:
        raise ValueError(f"input must be SEGMENT=PATH, got {spec!r}")
    segment = int(segment_s, 10)
    if segment < 0:
        raise ValueError(f"segment must be non-negative, got {segment}")
    path = Path(path_s)
    return segment, path


def _oracle_write(stream, row: dict[str, Any]) -> None:
    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def reduce_events(events: Iterable[tuple[int, Any]], out_dir: Path, *, sources: list[dict[str, Any]]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=False)
    can_path = out_dir / "can.bin"
    oracle_path = out_dir / "oracle.ndjson"
    meta_path = out_dir / "metadata.json"

    frames_by_bus = Counter({"0": 0, "1": 0, "2": 0})
    b6_by_bus = Counter({"0": 0, "1": 0, "2": 0})
    request_counts = Counter()
    response_counts = Counter()
    min_t: int | None = None
    max_t: int | None = None

    with can_path.open("wb", buffering=1024 * 1024) as can_stream, oracle_path.open("w") as oracle_stream:
        write_canbin_header(can_stream)
        for segment, event in events:
            which = event.which()
            if which not in {"can", "sendcan"}:
                continue
            t_ns = int(event.logMonoTime)
            min_t = t_ns if min_t is None else min(min_t, t_ns)
            max_t = t_ns if max_t is None else max(max_t, t_ns)

            frames = event.can if which == "can" else event.sendcan
            for frame in frames:
                bus = int(frame.src)
                address = int(frame.address)
                data = bytes(frame.dat)

                if which == "sendcan":
                    did = KNOWN_REQUESTS.get(data) if bus == FRC_BUS and address == FRC_TX else None
                    if did is None:
                        continue
                    request_counts[f"0x{did:04X}"] += 1
                    _oracle_write(oracle_stream, {
                        "type": "query",
                        "phase": "loggerd",
                        "segment": segment,
                        "t_ns": t_ns,
                        "bus": bus,
                        "address": f"0x{address:03X}",
                        "did": f"0x{did:04X}",
                        "request": data.hex(),
                    })
                    continue

                # Keep only actual incoming vehicle buses. TX echoes/rejections
                # use src>=128 and are not independent vehicle evidence.
                if not 0 <= bus <= 2:
                    continue
                write_canbin_record(can_stream, t_ns, bus, address, data)
                frames_by_bus[str(bus)] += 1
                if address == 0x0B6:
                    b6_by_bus[str(bus)] += 1

                if bus == FRC_BUS and address == FRC_RX:
                    parsed = parse_frc_response(data)
                    if parsed is None:
                        continue
                    did = parsed.get("did")
                    if did is not None:
                        response_counts[did] += 1
                    _oracle_write(oracle_stream, {
                        "type": "response",
                        "segment": segment,
                        "t_ns": t_ns,
                        "bus": bus,
                        "address": f"0x{address:03X}",
                        **parsed,
                    })

    duration_s = 0.0 if min_t is None or max_t is None else (max_t - min_t) / 1e9
    metadata = {
        "schema": "camry-frc-lta-rlog-capture-v1",
        "backend": "normal-loggerd-rlog",
        "diag_bus": FRC_BUS,
        "duration_s": duration_s,
        "source_segments": sources,
        "frames_by_bus": dict(frames_by_bus),
        "b6_by_bus": dict(b6_by_bus),
        "oracle_query_by_did": dict(sorted(request_counts.items())),
        "oracle_positive_by_did": dict(sorted(response_counts.items())),
        "privacy_boundary": "CAN+matching FRC sendcan only; no GPS/video/route-name/other loggerd services retained",
        "files": {"can": can_path.name, "oracle": oracle_path.name},
    }
    meta_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return metadata


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("inputs", nargs="+", help="one or more SEGMENT=/path/to/rlog.zst inputs")
    args = ap.parse_args()

    specs = [parse_input(spec) for spec in args.inputs]
    seen_segments = set()
    sources = []
    for segment, path in specs:
        if segment in seen_segments:
            ap.error(f"duplicate segment {segment}")
        seen_segments.add(segment)
        if not path.is_file():
            ap.error(f"missing rlog for segment {segment}: {path}")
        sources.append({"segment": segment, "size": path.stat().st_size, "sha256": sha256_file(path)})

    try:
        from openpilot.tools.lib.logreader import (
            LogReader,  # type: ignore[import-not-found]
        )
    except ModuleNotFoundError as exc:
        raise SystemExit("LogReader unavailable; run this reducer in a compatible openpilot Python environment") from exc

    def events():
        for segment, path in specs:
            for event in LogReader(str(path), sort_by_time=True):
                yield segment, event

    metadata = reduce_events(events(), args.out_dir, sources=sources)
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
