#!/usr/bin/env python3
"""Shared fail-closed mechanics for image-bound decompiler evidence promotion.

Semantic selection and artifact schemas stay in subsystem tools. This module owns
only the invariant shared by those tools: a promoted decompilation must come from a
function record, be complete, and bind to exact body bytes/ranges in the selected
firmware image.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

REPO = Path(__file__).resolve().parents[1]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    root = REPO.resolve()
    return str(resolved.relative_to(root)) if resolved.is_relative_to(root) else str(path)


def body_bytes(image: bytes, row: Mapping, *, honor_ranges: bool = True) -> bytes:
    ranges = row.get("body_ranges") if honor_ranges else None
    if not ranges:
        key = "entry_addr" if "entry_addr" in row else "entry"
        entry = int(str(row[key]), 16)
        size = int(row["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise ValueError(f"body outside image: 0x{entry:X}+0x{size:X}")
        return body
    chunks: list[bytes] = []
    for item in ranges:
        if item.get("space", "ram") != "ram":
            raise ValueError(f"unsupported function body space {item.get('space')}")
        lo = int(item["min"], 16)
        hi = int(item["max"], 16)
        if lo < 0 or hi < lo or hi >= len(image):
            raise ValueError(f"body range outside image: {lo:#x}..{hi:#x}")
        chunks.append(image[lo:hi + 1])
    out = b"".join(chunks)
    if len(out) != int(row["body_size"]):
        raise ValueError(
            f"body-range size mismatch {row.get('entry_addr', row.get('entry'))}: "
            f"{len(out)} != {row['body_size']}"
        )
    return out


def load_function_corpus(path: Path) -> tuple[dict[int, dict], int]:
    rows: dict[int, dict] = {}
    total = 0
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("record") != "function":
                continue
            total += 1
            rows[int(row["entry_addr"], 16)] = row
    return rows, total


def require_function(rows: Mapping[int, dict], entry: int) -> dict:
    row = rows.get(entry)
    if not row or not row.get("decompile_completed") or not row.get("decompiled_c"):
        raise ValueError(f"missing complete decompile 0x{entry:08X}")
    return row


def bind_function(
    image: bytes,
    row: Mapping,
    *,
    role: str | None = None,
    include_data_references: bool = True,
    include_body_ranges: bool = True,
    honor_body_ranges: bool = True,
) -> dict:
    entry = int(str(row["entry_addr"]), 16)
    text = str(row["decompiled_c"])
    out = {
        "entry": f"0x{entry:08X}",
        "body_size": int(row["body_size"]),
        "body_sha256": sha256_bytes(body_bytes(image, row, honor_ranges=honor_body_ranges)),
        "decompiled_c_sha256": sha256_bytes(text.encode()),
        "decompiled_c": text,
    }
    if role is not None:
        out["role"] = role
    if include_body_ranges:
        out["body_ranges"] = row.get("body_ranges", [])
    if include_data_references:
        out["data_references"] = row.get("data_references", [])
    return out


def bind_entries(
    image: bytes,
    rows: Mapping[int, dict],
    entries: Iterable[int] | Mapping[int, str],
    *,
    include_data_references: bool = True,
    include_body_ranges: bool = True,
    honor_body_ranges: bool = True,
) -> list[dict]:
    roles = entries if isinstance(entries, Mapping) else None
    values = entries.keys() if roles is not None else entries
    out = []
    for entry in values:
        row = require_function(rows, int(entry))
        out.append(bind_function(
            image,
            row,
            role=roles[int(entry)] if roles is not None else None,
            include_data_references=include_data_references,
            include_body_ranges=include_body_ranges,
            honor_body_ranges=honor_body_ranges,
        ))
    return out
