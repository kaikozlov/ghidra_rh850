"""Independent full-record byte reconstruction for all original P6 ROB sources."""

import json
import struct
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from tools.techstream.gts.rob_source_catalog import rob_source_catalog
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.techstream_paths import resolve_gts_root


def reconstruct(row):
    if row["table"] == 163:
        raw = bytearray(68)
        signature = row["signature"].encode("utf-16le")
        if len(signature) > 44:
            raise ValueError("oversized ROB signature")
        raw[: len(signature)] = signature
        struct.pack_into(
            "<IIIIHBBB",
            raw,
            44,
            row["behavior_code"],
            row["name_string_index"],
            row["division_string_index"],
            row["comment_string_index"],
            row["exception_handler_id"],
            row["enabled"],
            row["memory_override"],
            row["exception_handler_flag"],
        )
        raw[65:68] = bytes.fromhex(row["uninterpreted_bytes"]["65_67"])
    elif row["table"] == 164:
        raw = bytearray(48)
        struct.pack_into("<dd", raw, 0, *reversed(row["physical_range"]))
        struct.pack_into("<I", raw, 16, row["name_string_index"])
        struct.pack_into(
            "<7H",
            raw,
            20,
            *(
                row[k]
                for k in (
                    "record_key",
                    "support_condition_key",
                    "physical_data_key",
                    "bit_start",
                    "bit_end",
                    "sort_key",
                    "pattern_display_key",
                )
            ),
        )
        struct.pack_into("<HH", raw, 34, row["exception_handler_id"], row["did"])
        raw[38:40] = bytes.fromhex(row["uninterpreted_bytes"]["38_39"])
        raw[40:43] = bytes(
            (
                row["extraction_mode"],
                row["presentation_mode"],
                row["exception_handler_flag"],
            )
        )
        raw[43:48] = bytes.fromhex(row["uninterpreted_bytes"]["43_47"])
    else:
        raise ValueError("unexpected ROB table")
    return bytes(raw)


def verify():
    root = Path(resolve_gts_root())
    counts = Counter()
    strings = SimpleNamespace(get_string=lambda key: None)
    for region in ("EU", "JP", "NA"):
        for path in sorted((root / region / "DB/Gen").glob("*.ddb")):
            if path.name in {"Toyota.ddb", "Viewer.ddb"} or path.name.startswith(
                ("M_", "U_", "V_")
            ):
                continue
            db = DDBParser().parse_ecu_db(path)
            if not any(
                db.sections.get(t) and db.sections[t].header.record_count
                for t in (163, 164)
            ):
                continue
            decoded = rob_source_catalog(
                db, strings, path.name, resolve_variable=lambda key: b"\x00\x00"
            )
            for table, field in ((163, "behavior_codes"), (164, "signals")):
                section = db.sections.get(table)
                originals = list(section.iter_records()) if section else []
                assert len(originals) == len(decoded[field]), (
                    path,
                    table,
                    "membership",
                )
                for record, row in zip(originals, decoded[field]):
                    assert reconstruct(row) == record.raw, (
                        path,
                        table,
                        record.index,
                        "byte coverage",
                    )
                    counts[str(table)] += 1
                    counts[f"{table}_width_{len(record.raw)}"] += 1
    return dict(counts)


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
