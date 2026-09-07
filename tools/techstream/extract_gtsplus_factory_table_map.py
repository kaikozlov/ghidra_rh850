#!/usr/bin/env python3
"""Derive current GTS+ DDB section identities from KgpDataCtrl factories.

This is the current-GTS+ companion to ``extract_factory_table_map.py``.  It is
kept separate so ``tools/artifact regen`` has one unambiguous default output
per producer.  The extractor does not import ``parse_ddb``: table identities
come directly from the current KgpDataCtrl.dll switch targets and exported
constructors, so the resulting artifact can independently audit parser names.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

import pefile
from techstream_paths import resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PE = resolve_gts_root() / "bin/KgpDataCtrl.dll"
DEFAULT_OUTPUT = REPO / "data/generated/gtsplus_2026/ddb_factory_table_map.json"

FACTORIES = (
    {
        "format_version": 1,
        "factory_va": 0x10081C80,
        "jump_table_va": 0x10084458,
        "maximum_type": 0x5D,
        "body_size": 0x27D8,
        "default_case_va": 0x100843D3,
    },
    {
        "format_version": 2,
        "factory_va": 0x100845D0,
        "jump_table_va": 0x10088DCC,
        "maximum_type": 0xAB,
        "body_size": 0x47FC,
        "default_case_va": 0x10088D48,
    },
)

CTOR_RE = re.compile(r"^\?\?0([^@]+)@@QAE@EE@Z$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def va_data(pe: pefile.PE, va: int, size: int) -> bytes:
    return pe.get_data(va - pe.OPTIONAL_HEADER.ImageBase, size)


def exported_constructors(pe: pefile.PE) -> dict[int, dict[str, str]]:
    pe.parse_data_directories()
    base = pe.OPTIONAL_HEADER.ImageBase
    out: dict[int, dict[str, str]] = {}
    for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if not symbol.name:
            continue
        decorated = symbol.name.decode("ascii", errors="strict")
        match = CTOR_RE.match(decorated)
        if match:
            out[base + symbol.address] = {
                "class_name": match.group(1),
                "decorated_export": decorated,
            }
    return out


def constructor_call(
    pe: pefile.PE, case_va: int, constructors: dict[int, dict[str, str]]
) -> tuple[int, int, dict[str, str]] | None:
    # Current cases are shorter than 0x80 bytes.  The first direct call whose
    # target is an exported (u8,u8) CDb constructor is the class constructor;
    # allocator/autoclassinit helpers do not match CTOR_RE.
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
    count = spec["maximum_type"] + 1
    table = va_data(pe, spec["jump_table_va"], count * 4)
    case_vas = struct.unpack("<" + "I" * count, table)
    records = []
    for table_type, case_va in enumerate(case_vas):
        call = constructor_call(pe, case_va, constructors)
        if call is None:
            raise RuntimeError(
                f"format {spec['format_version']} type {table_type}: "
                f"no exported constructor at case 0x{case_va:08X}"
            )
        call_va, target_va, constructor = call
        status = (
            "generic-base/default"
            if case_va == spec["default_case_va"]
            else "constructed"
        )
        records.append(
            {
                "table_type": table_type,
                "case_va": f"0x{case_va:08X}",
                "constructor_call_va": f"0x{call_va:08X}",
                "constructor_va": f"0x{target_va:08X}",
                "constructor_export": constructor["decorated_export"],
                "class_name": constructor["class_name"],
                "status": status,
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
        "generic_base_count": sum(r["status"] == "generic-base/default" for r in records),
        "records": records,
    }


def build(pe_path: Path) -> dict:
    pe_path = pe_path.resolve()
    pe_bytes = pe_path.read_bytes()
    pe = pefile.PE(data=pe_bytes, fast_load=False)
    return {
        "schema_version": 1,
        "source": "GTS+ 2026.03.002.02",
        "artifact": {
            "relative_path": pe_path.relative_to(REPO).as_posix(),
            "size": len(pe_bytes),
            "sha256": sha256(pe_bytes),
        },
        "method": (
            "x86 MakeTable switch target -> direct E8 constructor call -> exact "
            "PE constructor export; independent of parse_ddb constants"
        ),
        "make_table": {
            "va": "0x10081C10",
            "routing": {"1": "0x10081C80", "2": "0x100845D0", "4": "0x10089080"},
            "body_sha256": sha256(va_data(pe, 0x10081C10, 0x63)),
        },
        "factories": [extract_factory(pe, spec) for spec in FACTORIES],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pe", type=Path, default=DEFAULT_PE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    result = build(args.pe)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for factory in result["factories"]:
        print(
            f"format {factory['format_version']}: "
            f"{factory['constructed_count']} constructed, "
            f"{factory['generic_base_count']} generic-base/default"
        )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
