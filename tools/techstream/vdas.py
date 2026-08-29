#!/usr/bin/env python3
"""Clean reader for Toyota GTS+ PCS Vehicle Data Analysis (.vdas) files."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any


def load_vdas(path: Path) -> dict[str, Any]:
    """Load one standard-ZIP VDAS and parse its UTF-8 ``json.log`` payload."""
    path = path.expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"VDAS file not found: {path}")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = archive.namelist()
            if "json.log" not in names:
                raise ValueError(f"VDAS archive lacks json.log: {path}")
            raw = archive.read("json.log")
    except zipfile.BadZipFile as exc:
        raise ValueError(f"not a ZIP-backed GTS+ VDAS file: {path}") from exc
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"VDAS json.log is not UTF-8: {path}") from exc
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"VDAS json.log is not valid JSON: {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"VDAS json.log root is not an object: {path}")
    return {
        "path": str(path),
        "archive_entries": names,
        "json_entry": "json.log",
        "json_bytes": len(raw),
        "document": document,
    }


def json_path(value: Any, path: str) -> Any:
    """Resolve a case-insensitive dotted path through a VDAS JSON object."""
    current = value
    for part in path.split("."):
        if not isinstance(current, dict):
            raise ValueError(f"VDAS JSON path {path!r} crosses non-object at {part!r}")
        matches = [key for key in current if str(key).casefold() == part.casefold()]
        if len(matches) != 1:
            raise ValueError(
                f"VDAS JSON path component {part!r} not found uniquely; "
                f"available={sorted(map(str, current))}"
            )
        current = current[matches[0]]
    return current
