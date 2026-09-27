"""Shared readers for retained passive Toyota CAN captures.

Exact file-format readers only: route NDJSON logs (plain or gzip), JSON
snapshots, and streaming digests. Analysis-specific time/bus/filter decisions
stay at the call sites; nothing here eagerly materializes a whole capture.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator


def sha256_file(path: Path) -> str:
    """Stream a file through SHA-256 without loading it fully into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_jsonl(path: Path, *, gz: bool = False) -> Iterator[Any]:
    """Yield one parsed JSON document per line, in file order."""
    opener = gzip.open if gz else open
    with opener(path, "rt", encoding="utf-8") as stream:  # type: ignore[operator]
        for line in stream:
            yield json.loads(line)


def iter_route_can(path: Path) -> Iterator[tuple[int, int, int, int, bytes]]:
    """Yield (segment, t_ns, bus, address, payload) from retained route NDJSON gzip logs.

    Blank lines are skipped; every other line is a five-element JSON array.
    """
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            seg, t, bus, addr, data = json.loads(line)
            yield int(seg), int(t), int(bus), int(addr), bytes.fromhex(data)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip_json(path: Path) -> Any:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)
