#!/usr/bin/env python3
"""Shared decoders for Toyota Calibration Update Wizard parameter files."""
from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
from typing import Any


def decode_parameter_ini(data: bytes) -> bytes:
    """Decode the CUW parameter-INI nibble transform recovered from Techstream.

    The transform is derived from TCUWParameterForVC.dll RVA 0x10001000 and is
    shared by deterministic writer generators and the interactive GTS+ query
    surface.
    """
    if len(data) % 2:
        raise ValueError("encoded CUW parameter file has odd length")
    decoded = bytes(
        (((((a & 0xF) >> 2) + (a >> 4) * 4) * 4 + (b >> 4) + 0x1E) * 4 + ((b & 0xF) >> 2)) & 0xFF
        for a, b in zip(data[::2], data[1::2])
    )
    return decoded.rstrip(b"\xff")


def factory_routes_from_ini_root(ini_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Decode CUW route INIs into one stable, implementation-neutral row shape."""
    routes: list[dict[str, Any]] = []
    decoded_files = 0
    for path in sorted(ini_root.glob("*.ini"), key=lambda p: p.name.lower()):
        encoded = path.read_bytes()
        try:
            decoded = decode_parameter_ini(encoded)
            rows = list(csv.reader(io.StringIO(decoded.decode("latin1"))))
        except (ValueError, UnicodeError, csv.Error):
            continue
        decoded_files += 1
        if len(rows) < 2 or "DLLFileNameForPrepareWrite" not in rows[0]:
            continue
        header = rows[0]
        for row_index, raw_row in enumerate(rows[1:], 1):
            row = raw_row + [""] * (len(header) - len(raw_row))
            item = dict(zip(header, row))
            routes.append({
                "parameter_file": path.name,
                "encoded_sha256": hashlib.sha256(encoded).hexdigest(),
                "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                "row_index": row_index,
                "factory_identifier": item.get("ParamFileKeySystemProtocolMicon", ""),
                "cid_getter": item.get("DLLFileNameForGetCID", ""),
                "prepare_writer": item.get("DLLFileNameForPrepareWrite", ""),
                "flash_writer": item.get("DLLFileNameForFlashWrite", ""),
                "get_can_id_cid": item.get("GetCANIDFunctionNameForGetCID", ""),
                "get_can_id_prepare": item.get("GetCANIDFunctionNameForPrepareWrite", ""),
                "get_can_id_flash": item.get("GetCANIDFunctionNameForFlashWrite", ""),
                "version_contract": item.get("EnableDLLVersionInformation", ""),
                "prepare_retry": item.get("PrepareRetryFlag", ""),
                "raw": item,
            })
    routes.sort(key=lambda item: (item["factory_identifier"], item["parameter_file"], item["row_index"]))
    return routes, {"encoded_ini_files_decoded": decoded_files, "factory_rows": len(routes)}
