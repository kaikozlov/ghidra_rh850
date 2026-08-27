#!/usr/bin/env python3
"""Shared PE metadata/string walkers for Techstream/GTS reverse engineering."""
from __future__ import annotations

import re
from typing import Any


def exports(pe: Any, *, unnamed_none: bool = False) -> list[dict]:
    out = []
    if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            out.append({
                "name": symbol.name.decode("latin1", errors="replace") if symbol.name else (None if unnamed_none else f"ordinal:{symbol.ordinal}"),
                "rva": symbol.address,
            })
    return out


def imports(pe: Any, *, include_iat: bool = False) -> list[dict]:
    out = []
    for library in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
        dll = library.dll.decode("latin1", errors="replace")
        for symbol in library.imports:
            row = {
                "dll": dll,
                "name": symbol.name.decode("latin1", errors="replace") if symbol.name else f"ordinal:{symbol.ordinal}",
            }
            if include_iat:
                row["iat_va"] = symbol.address
            out.append(row)
    return out


def binary_strings(data: bytes, minimum: int = 5, *, include_wide: bool = True) -> list[str]:
    ascii_strings = [m.group().decode("latin1") for m in re.finditer(rb"[ -~]{%d,}" % minimum, data)]
    if not include_wide:
        return ascii_strings
    wide_re = re.compile(rb"(?:[ -~]\x00){%d,}" % minimum)
    wide_strings = [m.group().decode("utf-16-le", errors="replace") for m in wide_re.finditer(data)]
    return ascii_strings + wide_strings
