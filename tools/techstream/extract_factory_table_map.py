#!/usr/bin/env python3
"""Derive Techstream DDB section identities from the pinned PE factories.

This extractor deliberately does not import ``parse_ddb``.  It walks the two
x86 switch tables in KgpDataCtrl.dll, resolves each case's direct constructor
call against the PE export directory, and emits the executable provenance used
to check the parser's human-facing class names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

import pefile


REPO = Path(__file__).resolve().parents[2]
DEFAULT_PE = (
    REPO
    / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream/bin/KgpDataCtrl.dll"
)
DEFAULT_OUTPUT = REPO / "data/generated/techstream_v18/ddb_factory_table_map.json"

FACTORIES = (
    {
        "format_version": 1,
        "factory_va": 0x1001C9D0,
        "jump_table_va": 0x1001EB67,
        "maximum_type": 0x58,
        "body_size": 0x21F7,
    },
    {
        "format_version": 2,
        "factory_va": 0x1001ECCB,
        "jump_table_va": 0x100225A2,
        "maximum_type": 0x96,
        "body_size": 14551,
    },
)

CTOR_RE = re.compile(r"^\?\?0([^@]+)@@QAE@EE@Z$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def va_data(pe: pefile.PE, va: int, size: int) -> bytes:
    image_base = pe.OPTIONAL_HEADER.ImageBase
    return pe.get_data(va - image_base, size)


def exported_constructors(pe: pefile.PE) -> dict[int, dict[str, str]]:
    pe.parse_data_directories()
    image_base = pe.OPTIONAL_HEADER.ImageBase
    constructors: dict[int, dict[str, str]] = {}
    for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if not symbol.name:
            continue
        decorated = symbol.name.decode("ascii", errors="strict")
        match = CTOR_RE.match(decorated)
        if match:
            constructors[image_base + symbol.address] = {
                "class_name": match.group(1),
                "decorated_export": decorated,
            }
    return constructors


def constructor_call(
    pe: pefile.PE, case_va: int, constructors: dict[int, dict[str, str]]
) -> tuple[int, int, dict[str, str]] | None:
    """Return (call VA, target VA, constructor) for one switch case."""
    body = va_data(pe, case_va, 0x80)
    for offset in range(len(body) - 4):
        if body[offset] != 0xE8:
            continue
        displacement = struct.unpack_from("<i", body, offset + 1)[0]
        target = case_va + offset + 5 + displacement
        if target in constructors:
            return case_va + offset, target, constructors[target]
    return None


def extract_factory(pe: pefile.PE, spec: dict[str, int]) -> dict:
    constructors = exported_constructors(pe)
    table_size = (spec["maximum_type"] + 1) * 4
    table = va_data(pe, spec["jump_table_va"], table_size)
    case_vas = struct.unpack("<" + "I" * (spec["maximum_type"] + 1), table)
    records = []
    for table_type, case_va in enumerate(case_vas):
        call = constructor_call(pe, case_va, constructors)
        if call is None:
            records.append(
                {
                    "table_type": table_type,
                    "case_va": f"0x{case_va:08X}",
                    "status": "unsupported/default",
                }
            )
            continue
        call_va, target_va, constructor = call
        records.append(
            {
                "table_type": table_type,
                "case_va": f"0x{case_va:08X}",
                "constructor_call_va": f"0x{call_va:08X}",
                "constructor_va": f"0x{target_va:08X}",
                "constructor_export": constructor["decorated_export"],
                "class_name": constructor["class_name"],
                "status": "constructed",
            }
        )
    body = va_data(pe, spec["factory_va"], spec["body_size"])
    return {
        "format_version": spec["format_version"],
        "factory_va": f"0x{spec['factory_va']:08X}",
        "factory_body_size": spec["body_size"],
        "factory_body_sha256": sha256(body),
        "jump_table_va": f"0x{spec['jump_table_va']:08X}",
        "jump_table_sha256": sha256(table),
        "maximum_type": spec["maximum_type"],
        "constructed_count": sum(r["status"] == "constructed" for r in records),
        "records": records,
    }


def build(pe_path: Path) -> dict:
    pe_bytes = pe_path.read_bytes()
    pe = pefile.PE(data=pe_bytes, fast_load=False)
    return {
        "schema_version": 1,
        "source": "Techstream V18.00.003",
        "artifact": {
            "relative_path": pe_path.relative_to(REPO).as_posix(),
            "size": len(pe_bytes),
            "sha256": sha256(pe_bytes),
        },
        "method": (
            "x86 switch target -> direct E8 constructor call -> exact PE "
            "constructor export; independent of parse_ddb constants"
        ),
        "make_table": {
            "va": "0x100228D1",
            "routing": {"1": "0x1001C9D0", "2": "0x1001ECCB", "4": "0x100227FE"},
            "body_sha256": sha256(va_data(pe, 0x100228D1, 0x67)),
        },
        "factories": [extract_factory(pe, spec) for spec in FACTORIES],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pe", type=Path, default=DEFAULT_PE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build(args.pe.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for factory in result["factories"]:
        print(
            f"format {factory['format_version']}: "
            f"{factory['constructed_count']} constructed table types"
        )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
