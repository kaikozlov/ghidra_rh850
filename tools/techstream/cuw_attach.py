#!/usr/bin/env python3
"""Canonical parser for Toyota CUW ``attach.att`` descriptors."""
from __future__ import annotations

import configparser
from pathlib import Path


def parse_attach_bytes(raw: bytes) -> dict[str, dict[str, str]]:
    """Parse descriptor bytes into a section -> exact-field mapping.

    Toyota V18 is native ANSI. latin-1 is intentionally reversible for unknown
    regional bytes; interpolation is disabled and key case is preserved.
    """
    cp = configparser.RawConfigParser(interpolation=None, strict=False, delimiters=("=",))
    cp.optionxform = str
    cp.read_string(raw.decode("latin1"))
    return {section: dict(cp.items(section, raw=True)) for section in cp.sections()}


def parse_attach(path: Path) -> dict[str, dict[str, str]]:
    return parse_attach_bytes(path.read_bytes())


def capture_shape(path: Path) -> dict:
    """Preserve the historical parse_cuw_attach.py JSON capture shape."""
    raw = path.read_bytes()
    parsed = parse_attach_bytes(raw)
    return {
        "source": str(path),
        "size": len(raw),
        "sections": [
            {"name": section, "fields": [{"name": key, "value": value} for key, value in fields.items()]}
            for section, fields in parsed.items()
        ],
    }
