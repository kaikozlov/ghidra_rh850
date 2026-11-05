"""Lossless, directly readable Toyota diagnostic bundle members.

The tracked representation is a directory of deterministic gzip members and an
ordered size/SHA-256 manifest. ZIP is a portable export, not a runtime input.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from tools import REPO_ROOT

DEFAULT_BUNDLE = REPO_ROOT / "data/generated/gtsplus_2026/toyota_diag_bundle_current"
DEFAULT_BUNDLE_ZIP = REPO_ROOT / "build/out/toyota_diag_bundle_current.zip"
STORAGE_SCHEMA = "toyota-diagnostics-gzip-members-v1"


def _member_path(root: Path, name: str) -> Path:
    member = PurePosixPath(name)
    if not name or member.is_absolute() or ".." in member.parts or str(member) != name:
        raise ValueError(f"invalid bundle member name: {name!r}")
    return root / (name + ".gz")


class DiagnosticBundleWriter:
    """Write exact member bytes, recording their original enumeration order."""

    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True)
        self.members: list[dict[str, object]] = []
        self.names: set[str] = set()

    def add(self, name: str, source: BinaryIO) -> None:
        if name in self.names:
            raise ValueError(f"duplicate bundle member: {name}")
        path = _member_path(self.root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        with path.open("wb") as compressed:
            with gzip.GzipFile(filename="", fileobj=compressed, mode="wb", compresslevel=9, mtime=0) as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
        self.members.append({"name": name, "bytes": size, "sha256": digest.hexdigest()})
        self.names.add(name)

    def finish(self) -> None:
        manifest = {"schema": STORAGE_SCHEMA, "members": self.members}
        (self.root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


class DiagnosticBundle:
    """Open canonical data without Toyota distributions or a ZIP extraction cache."""

    def __init__(self, root: Path = DEFAULT_BUNDLE):
        self.root = root
        self.manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        if self.manifest.get("schema") != STORAGE_SCHEMA:
            raise ValueError(f"unsupported diagnostic bundle storage: {root}")
        self.members = self.manifest["members"]
        self._members = {}
        for member in self.members:
            name = member["name"]
            _member_path(root, name)
            if name in self._members:
                raise ValueError(f"duplicate bundle member: {name}")
            self._members[name] = member

    def namelist(self) -> list[str]:
        return list(self._members)

    def open(self, name: str) -> BinaryIO:
        if name not in self._members:
            raise KeyError(name)
        return gzip.open(_member_path(self.root, name), "rb")

    def read(self, name: str) -> bytes:
        with self.open(name) as source:
            return source.read()

    def json(self, name: str):
        with self.open(name) as source:
            return json.load(source)

    def verify(self) -> None:
        """Check every member's gzip CRC, byte count, hash, and file inventory."""
        expected = {_member_path(self.root, name).relative_to(self.root).as_posix() for name in self._members}
        actual = {path.relative_to(self.root).as_posix() for path in self.root.rglob("*") if path.is_file()}
        if actual != expected | {"manifest.json"}:
            raise ValueError("diagnostic bundle member inventory differs from manifest")
        for member in self.members:
            digest = hashlib.sha256()
            size = 0
            with self.open(member["name"]) as source:
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
                    size += len(chunk)
            if size != member["bytes"] or digest.hexdigest() != member["sha256"]:
                raise ValueError(f"diagnostic bundle member differs from manifest: {member['name']}")

    def compare_zip(self, path: Path) -> None:
        """Prove every original ZIP member restores byte-for-byte, in order."""
        with zipfile.ZipFile(path) as archive:
            if archive.namelist() != self.namelist():
                raise ValueError("ZIP member names/order differ from canonical bundle")
            for member in self.members:
                with archive.open(member["name"]) as original, self.open(member["name"]) as restored:
                    while True:
                        before = original.read(1024 * 1024)
                        after = restored.read(1024 * 1024)
                        if before != after:
                            raise ValueError(f"ZIP member bytes differ: {member['name']}")
                        if not before:
                            break

    def export_zip(self, out: Path = DEFAULT_BUNDLE_ZIP) -> None:
        """Export a deterministic portable ZIP, streaming even the large index."""
        out.parent.mkdir(parents=True, exist_ok=True)
        temporary = out.with_name(f".{out.name}.tmp")
        try:
            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
                for member in self.members:
                    info = zipfile.ZipInfo(member["name"], date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o644 << 16
                    info.file_size = member["bytes"]
                    with self.open(member["name"]) as source, archive.open(info, "w") as target:
                        shutil.copyfileobj(source, target, length=1024 * 1024)
            temporary.replace(out)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
