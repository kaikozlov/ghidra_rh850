"""Disposable, per-ECU semantic row snapshots for GTS search."""

from __future__ import annotations

import hashlib
import json
import os
from contextlib import suppress
from functools import cache
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from tools import REPO_ROOT
from tools.project.build_paths import for_repo

_DIGEST_SIZE = hashlib.sha256().digest_size


@cache
def _implementation_fingerprint() -> bytes:
    here = Path(__file__)
    digest = hashlib.sha256()
    for source in (
        here, here.with_name("query.py"), here.with_name("ddb.py"),
        *(here.parent.parent / name for name in ("parse_ddb.py", "ddb_semantics.py", "ddb_strings.py")),
    ):
        digest.update(hashlib.sha256(source.read_bytes()).digest())
    return digest.digest()


class _SearchCache:
    def __init__(self, gts_root: Path, db_root: Path, dictionary_sha256: str) -> None:
        scope = hashlib.sha256(os.fsencode(gts_root.absolute()) + b"\0" + os.fsencode(db_root.absolute()))
        self._directory = for_repo(REPO_ROOT).cache / "gts/search-rows" / scope.hexdigest()
        self._identity = _implementation_fingerprint() + bytes.fromhex(dictionary_sha256)

    def _entry(self, path: Path, kind: str) -> Path:
        filename = hashlib.sha256(os.fsencode(path.name)).hexdigest()
        return self._directory / f"{filename}-{kind}.rows"

    def read(self, path: Path, kind: str, source_sha256: str) -> list[dict[str, Any]] | None:
        identity = self._identity + bytes.fromhex(source_sha256)
        try:
            with self._entry(path, kind).open("rb") as stream:
                if stream.read(len(identity)) != identity:
                    return None
                checksum = stream.read(_DIGEST_SIZE)
                payload = stream.read()
            if hashlib.sha256(payload).digest() != checksum:
                return None
            rows = json.loads(payload)
            if not isinstance(rows, list):
                return None
            if kind == "did":
                # Renderers sort enum keys numerically, even though JSON makes them strings.
                for row in rows:
                    if (info := row["signal_info"]) is not None:
                        info["pattern_display"] = {int(key): label for key, label in info["pattern_display"].items()}
            return rows
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            return None

    def write(self, path: Path, kind: str, source_sha256: str, rows: list[dict[str, Any]]) -> None:
        entry = self._entry(path, kind)
        identity = self._identity + bytes.fromhex(source_sha256)
        payload = json.dumps(rows, separators=(",", ":")).encode("ascii")
        temporary = None
        try:
            entry.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=entry.parent, prefix=".", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(identity)
                stream.write(hashlib.sha256(payload).digest())
                stream.write(payload)
            os.replace(temporary, entry)
            temporary = None
        except OSError:
            # On a read-only or unavailable cache, the fresh rows are still usable.
            pass
        finally:
            if temporary is not None:
                with suppress(OSError):
                    temporary.unlink(missing_ok=True)
