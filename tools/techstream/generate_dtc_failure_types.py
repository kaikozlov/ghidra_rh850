#!/usr/bin/env python3
"""Generate the Techstream V18 P5 DTC failure-type vocabulary.

The generator scans section type 65 in every parseable P5 ECU database under
the unpacked Techstream V18 NA/DB directory. P5 section 65 uses 68-byte records
with a full textual DTC code, packed base+failure byte, a base-description
M_English string index, and a failure-type M_English string index.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "techstream"))

from parse_ddb import DDBParser  # noqa: E402

DEFAULT_DB_ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB"
DEFAULT_OUTPUT = REPO / "data/generated/techstream_v18/dtc_failure_types.json"


def build(db_root: Path) -> dict:
    parser = DDBParser()
    strings = parser.load_string_db(db_root / "M_English.ddb")
    suffix_map: dict[int, Counter[tuple[int, str | None]]] = defaultdict(Counter)
    u023a_records: list[dict] = []
    databases = records = nonzero_tail_records = 0

    for path in sorted(db_root.glob("*.ddb"), key=lambda p: p.name.lower()):
        try:
            db = parser.parse_ecu_db(path)
        except ValueError:
            continue
        section = db.sections.get(65)
        if section is None or section.record_size != 68:
            continue
        databases += 1
        for index, entry in enumerate(parser.extract_dtc_failure_entries(section)):
            if not entry.code:
                continue
            records += 1
            nonzero_tail_records += int(entry.tail_word != 0)
            failure_text = strings.get_string(entry.failure_string_index)
            suffix_map[entry.failure_type][(entry.failure_string_index, failure_text)] += 1
            if entry.code.upper().startswith("U023A"):
                u023a_records.append({
                    "database": path.name,
                    "record_index": index,
                    "code": entry.code,
                    "packed_dtc": f"0x{entry.packed_dtc:06X}",
                    "base_dtc": f"0x{entry.base_dtc:04X}",
                    "failure_type": f"0x{entry.failure_type:02X}",
                    "description_string_index": entry.description_string_index,
                    "description": strings.get_string(entry.description_string_index),
                    "failure_string_index": entry.failure_string_index,
                    "failure_text": failure_text,
                    "tail_word": entry.tail_word,
                    "raw_sha256": __import__("hashlib").sha256(entry.raw).hexdigest(),
                })

    suffixes = {}
    for suffix, variants in sorted(suffix_map.items()):
        suffixes[f"0x{suffix:02X}"] = [
            {
                "string_index": index,
                "text": text,
                "record_count": count,
            }
            for (index, text), count in sorted(
                variants.items(), key=lambda item: (-item[1], item[0][0], item[0][1] or "")
            )
        ]

    return {
        "schema_version": 2,
        "source": {
            "db_root": "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB",
            "string_database": "M_English.ddb",
            "section_type": 65,
            "record_size": 68,
            "field_offsets": {
                "code_utf16": "0x00..0x2B",
                "packed_dtc": "0x2C",
                "description_string_index": "0x30",
                "failure_string_index": "0x34",
                "tail_word": "0x40 (deterministic extraction; semantic attribution bounded)",
            },
        },
        "counts": {
            "databases_with_section65_68": databases,
            "nonempty_records": records,
            "nonzero_tail_records": nonzero_tail_records,
        },
        "failure_types": suffixes,
        "u023a_records": u023a_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-root", type=Path, default=DEFAULT_DB_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = build(args.db_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
