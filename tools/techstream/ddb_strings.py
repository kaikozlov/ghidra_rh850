#!/usr/bin/env python3
"""Cached loading for expensive M/V English Toyota DDB string databases."""
from __future__ import annotations

import hashlib
import os
import struct
from pathlib import Path

from parse_ddb import DDBParser, StringDataBase

REPO = Path(__file__).resolve().parents[2]
CACHE_MAGIC = b"GTSSTR1\0"
CACHE_ROOT = REPO / "build/cache/gts/string-dbs"
CACHE_GENERATIONS_TO_KEEP = 4


def _prune(cache_path: Path, keep: int = CACHE_GENERATIONS_TO_KEEP) -> None:
    prefix = cache_path.stem.rsplit("-", 1)[0]
    others = [p for p in cache_path.parent.glob(f"{prefix}-*.bin") if p != cache_path]
    others.sort(key=lambda p: p.stat().st_mtime_ns if p.exists() else 0, reverse=True)
    for old in others[max(keep - 1, 0):]:
        old.unlink(missing_ok=True)


def load_string_db(parser: DDBParser, path: Path, *, cache_root: Path = CACHE_ROOT) -> StringDataBase:
    if path.name.startswith("U_"):
        return parser.load_string_db(path)
    source = path.read_bytes()
    identity = hashlib.sha256()
    identity.update(CACHE_MAGIC)
    identity.update(source)
    identity.update((Path(__file__).with_name("parse_ddb.py")).read_bytes())
    cache_path = cache_root / f"{path.stem}-{identity.hexdigest()}.bin"
    try:
        cached = cache_path.read_bytes()
        if len(cached) >= 16 and cached[:8] == CACHE_MAGIC:
            entry_count, pool_offset = struct.unpack_from("<II", cached, 8)
            decompressed = cached[16:]
            if pool_offset == entry_count * 6 and pool_offset <= len(decompressed):
                return StringDataBase(path, entry_count, decompressed, pool_offset, None)
    except OSError:
        pass
    db = parser.load_string_db(path)
    payload = CACHE_MAGIC + struct.pack("<II", db.entry_count, db.pool_offset) + db.decompressed
    temporary = cache_path.with_name(f".{cache_path.name}.tmp.{os.getpid()}")
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_bytes(payload)
        os.replace(temporary, cache_path)
        _prune(cache_path)
    except OSError:
        temporary.unlink(missing_ok=True)
    return db


def english(parser: DDBParser, db_root: Path, name: str = "M_English.ddb") -> StringDataBase:
    path = db_root / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return load_string_db(parser, path)
