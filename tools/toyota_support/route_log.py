"""Decode local openpilot rlog segments with an explicitly selected Cereal schema."""
from __future__ import annotations

import bz2
import warnings
from pathlib import Path

import zstandard

# pycapnp exposes these names from its untyped compiled extension.
from capnp import KjException, SchemaParser  # ty: ignore[missing-module-member]


def _load_cereal(openpilot_root: Path):
    root = openpilot_root.resolve()
    for package in (root, root / "openpilot"):
        schema = package / "cereal/log.capnp"
        if schema.is_file():
            break
    else:
        raise FileNotFoundError(f"no cereal/log.capnp under {openpilot_root}")

    cereal = schema.parent
    # Old checkouts keep car.capnp in Cereal. New ones import it from opendbc.
    # The supplied path can also be the inner openpilot package of a checkout.
    checkout = package.parent if package.name == "openpilot" else package
    imports = [cereal]
    for base in dict.fromkeys((package, checkout)):
        imports.extend((base / "opendbc_repo/opendbc/car", base / "opendbc/car"))
    if '"/car.capnp"' in schema.read_text(encoding="utf-8") and not any(
        (directory / "car.capnp").is_file() for directory in imports
    ):
        raise FileNotFoundError(f"no car.capnp for {schema}; populate the checkout's opendbc sources")
    # A separate parser permits selecting different checkouts in one process.
    return SchemaParser().load(str(schema), imports=[str(directory) for directory in imports])


def _read_segment(path: Path) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(f"not a local rlog file: {path}")
    with path.open("rb") as stream:
        magic = stream.read(4)
        stream.seek(0)
        if magic == b"\x28\xb5\x2f\xfd" or path.suffix == ".zst":
            with zstandard.ZstdDecompressor().stream_reader(stream) as decompressed:
                return decompressed.read()
        if magic.startswith(b"BZh") or path.suffix == ".bz2":
            with bz2.BZ2File(stream) as decompressed:
                return decompressed.read()
        return stream.read()


class RouteLogReader:
    """Callable local segment reader (plain, zstd, or bzip2 Cap'n Proto messages)."""

    def __init__(self, openpilot_root: Path):
        self._cereal = _load_cereal(openpilot_root)

    @property
    def event_schema(self):
        return self._cereal.Event.schema

    def __call__(self, path: str | Path, *, only_union_types: bool = False, sort_by_time: bool = False):
        events = self._read_events(Path(path))
        ordered = sorted(events, key=lambda event: event.logMonoTime) if sort_by_time else events
        for event in ordered:
            if only_union_types:
                try:
                    event.which()
                except KjException:
                    continue
            yield event

    def _read_events(self, path: Path):
        events = self._cereal.Event.read_multiple_bytes(_read_segment(path))
        try:
            yield from events
        except KjException:
            warnings.warn("Corrupted events detected", RuntimeWarning, stacklevel=1)


def load_logreader(openpilot_root: Path) -> RouteLogReader:
    """Load the offline log reader against the caller's Cereal schema."""
    return RouteLogReader(openpilot_root)
