#!/usr/bin/env python3
"""Canonical parser for Toyota CUW ``attach.att`` descriptors."""
from __future__ import annotations

import configparser
import re
from pathlib import Path


def parse_attach_bytes(raw: bytes, *, native_current: bool = False) -> dict[str, dict[str, str]]:
    """Read a descriptor, optionally using the current CUW native profile rules.

    The default preserves historical V18 inventory captures. ``native_current``
    models a fresh CUW.dll profile (5BEE0/2CDD0): ANSI, first-NUL termination,
    CR/LF token separators, literal whitespace/comments, first ``=``, last key,
    and whole-section replacement. It does not imply native file admission.
    """
    if native_current:
        lines = [line for line in re.split(r"[\r\n]", raw.split(b"\0", 1)[0].decode("latin1")) if line]
        result: dict[str, dict[str, str]] = {}
        section = ""
        pending: dict[str, str] = {}
        for index, line in enumerate(lines):
            if len(line) >= 2 and line[0] == "[" and line[-1] == "]":
                if section and pending:
                    result[section] = pending
                    pending = {}
                section = line[1:-1]
            else:
                key, separator, value = line.partition("=")
                if separator and value:
                    pending[key] = value
                if index == len(lines) - 1 and section and pending:
                    result[section] = pending
        return result
    cp = configparser.RawConfigParser(interpolation=None, strict=False, delimiters=("=",))
    cp.optionxform = str
    cp.read_string(raw.decode("latin1"))
    return {section: dict(cp.items(section, raw=True)) for section in cp.sections()}


def current_profile_int(value: str, default: int = 0) -> int:
    """CUW 2D540 decimal-i32: prefixes accepted; no digits/ERANGE catch to default."""
    match = re.match(r"^[ \t\r\n\v\f]*([+-]?[0-9]+)", value)
    if match is None:
        return default
    try:
        number = int(match[1], 10)
    except ValueError:
        return default
    return number if -(1 << 31) <= number < (1 << 31) else default


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
