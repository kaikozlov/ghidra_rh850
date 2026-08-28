#!/usr/bin/env python3
"""Fast, read-only query surface over Toyota GTS+/Techstream evidence.

This command is for discovery, not proof generation. It exposes the shared
mechanics already recovered by the repository (DDB parsing/string resolution,
CUW descriptor parsing + writer-route resolution, and PE metadata/string
inspection) without merging the subsystem-specific deterministic generators.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import re
import struct
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pefile

ROOT = Path(__file__).resolve().parents[2]
TECHSTREAM_TOOLS = ROOT / "tools" / "techstream"
sys.path.insert(0, str(TECHSTREAM_TOOLS))

from cuw_attach import parse_attach_bytes
from cuw_parameter import factory_routes_from_ini_root
from ddb_semantics import behavior_rows as semantic_behavior_rows
from ddb_semantics import dtc_rows as semantic_dtc_rows
from ddb_semantics import extract_monitor_records
from ddb_semantics import monitor_rows as semantic_monitor_rows
from ddb_semantics import records as ddb_records
from ddb_strings import load_string_db as cached_string_db
from diagnostic_role_model import plugin_operation_signature, role_operation_catalog
from parse_cuw_container import first_member_payload, read_first_member
from parse_cuw_container import parse as parse_cuw_container
from parse_ddb import ECU_TABLE_CLASS_NAMES, DDBParser, StringDataBase
from pe_utils import binary_strings as pe_binary_strings
from pe_utils import exports as pe_exports
from pe_utils import imports as pe_imports
from recover_gtsplus_bodies import DEFAULT_ARCHIVE as GTSPLUS_BODY_ARCHIVE
from recover_gtsplus_bodies import DEFAULT_OUTPUT as GTSPLUS_BODY_OUTPUT
from recover_gtsplus_bodies import recover as recover_gtsplus_bodies
from techstream_paths import (
    CUW_CORPUS_ROOT,
    GTSPLUS_EXTERNAL_ROOT,
    gts_db_root,
    resolve_cuw_corpus,
    resolve_cuwplus_root,
    resolve_gts_root,
)

DEFAULT_GTS_EXTERNAL = GTSPLUS_EXTERNAL_ROOT
DEFAULT_CUW_CORPUS = CUW_CORPUS_ROOT
EXECUTION_MODEL = ROOT / "data/generated/techstream_v18/diagnostic_execution_model.json"


def _resolve_gts_root(value: str | Path | None = None) -> Path:
    return resolve_gts_root(value)


def _resolve_cuwplus_root(gts_root: Path, value: str | Path | None = None) -> Path:
    return resolve_cuwplus_root(gts_root, value)


def _resolve_cuw_corpus(value: str | Path | None = None) -> Path:
    return resolve_cuw_corpus(value)


def _db_root(gts_root: Path, region: str = "NA", family: str = "Gen") -> Path:
    return gts_db_root(gts_root, region, family)


def _normalize_did(value: str) -> int | None:
    text = value.strip().lower()
    try:
        if text.startswith("0x"):
            return int(text, 16)
        if re.fullmatch(r"[0-9a-f]{4}", text):
            return int(text, 16)
    except ValueError:
        return None
    return None


def _fold_match(query: str, *values: Any) -> bool:
    needle = query.casefold()
    return any(value is not None and needle in str(value).casefold() for value in values)


def _load_string_db(parser: DDBParser, path: Path) -> StringDataBase:
    return cached_string_db(parser, path)


def _english_strings(parser: DDBParser, db_root: Path):
    path = db_root / "M_English.ddb"
    if not path.is_file():
        raise SystemExit(f"missing GTS+ OEM string database: {path}")
    return _load_string_db(parser, path)


def _english_string_dbs(parser: DDBParser, db_root: Path, m_strings: StringDataBase | None = None) -> dict[str, Any]:
    out = {}
    for name in ("M_English.ddb", "V_English.ddb", "U_English.ddb"):
        path = db_root / name
        if path.is_file():
            out[name] = m_strings if name == "M_English.ddb" and m_strings is not None else _load_string_db(parser, path)
    if "M_English.ddb" not in out:
        raise SystemExit(f"missing GTS+ OEM string database: {db_root / 'M_English.ddb'}")
    return out


def _resolve_ecu(db_root: Path, query: str) -> Path:
    direct = Path(query)
    if direct.is_file():
        return direct.resolve()
    files = sorted(
        (p for p in db_root.glob("*.ddb") if p.name not in {"M_English.ddb", "V_English.ddb", "U_English.ddb", "Toyota.ddb"}),
        key=lambda p: p.name.casefold(),
    )
    exact = [p for p in files if p.name.casefold() == query.casefold() or p.stem.casefold() == query.casefold()]
    if len(exact) == 1:
        return exact[0]
    matches = [p for p in files if query.casefold() in p.name.casefold()]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"no GTS+ ECU database matches {query!r} under {db_root}")
    raise SystemExit("ambiguous ECU database; matches:\n" + "\n".join(f"  {p.name}" for p in matches[:40]))


def _without_raw(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: value for key, value in row.items() if key != "raw"} for row in rows]


def _monitor_rows(db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    return _without_raw(
        semantic_monitor_rows(db, strings, source, deduplicate=True, include_signal_info=True)
    )


def _dtc_rows(parser: DDBParser, db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    return _without_raw(semantic_dtc_rows(parser, db, strings, source))


def _behavior_rows(db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    return _without_raw(semantic_behavior_rows(db, strings, source))


def _format_row(row: dict[str, Any]) -> str:
    kind = row.get("kind", "?")
    if kind == "did":
        did = row.get("primary_did")
        alt = row.get("alternate_did")
        alt_text = f" alt=0x{alt:04X}" if isinstance(alt, int) and alt not in {0, did} else ""
        info = row.get("signal_info")
        info_text = ""
        if isinstance(info, dict):
            unit = info.get("unit") or "-"
            info_text = (
                f"\tconv={info['mul']}/{info['div']} offset={info['offset']} "
                f"dec={info['decimal_point_count']} signed={int(info['signed'])} "
                f"bits={info['bit_width']} unit={unit}"
            )
            if info.get("pattern_display"):
                info_text += f" patterns={len(info['pattern_display'])}"
        return f"did\t{row['source']}\t0x{did:04X}{alt_text}\t{row.get('name') or ''}{info_text}"
    if kind == "dtc":
        return f"dtc\t{row['source']}\t{row.get('code') or row.get('packed_dtc')}\t{row.get('description') or ''}\t{row.get('failure') or ''}"
    if kind == "behavior":
        return f"behavior\t{row['source']}\t{row.get('signature') or ''}\t{row.get('name') or ''}\t{row.get('comment') or ''}"
    if kind == "string":
        return f"string\t{row['source']}\t@0x{row['offset']:X}\t{row['text']}"
    if kind == "file":
        return f"file\t{row['source']}"
    if kind == "route":
        return (
            f"route\t{row.get('contact_type','')}\t{row.get('cid_getter','')}\t"
            f"{row.get('prepare_writer','')}\t{row.get('flash_writer','')}\t{row.get('parameter_file','')}"
        )
    if kind == "frame":
        return (
            f"frame\tcategory={row['category_id']}\tselector={row['selector']}\t"
            f"comm_set={row['comm_set']}\tframe={row['comm_frame_id']}\t"
            f"rcv_timeout={row['comm_set_metadata']['receive_timeout']}\t"
            f"retries={row['comm_set_metadata']['retry_count']}\t"
            f"send={row['send']['bytes']}\tmask={row['receive_mask']['bytes']}\tcheck={row['receive_check']['bytes']}"
        )
    if kind == "cuw":
        return f"cuw\t{row.get('source','')}\t{row.get('vehicle','')}\t{row.get('contact_type','')}\t{row.get('new_cids','')}"
    return json.dumps(row, sort_keys=True)


def _print_rows(rows: list[dict[str, Any]], *, as_json: bool, limit: int | None = None) -> None:
    shown = rows if limit is None else rows[:limit]
    if as_json:
        print(json.dumps(shown, indent=2, sort_keys=True))
    else:
        for row in shown:
            print(_format_row(row))
        if limit is not None and len(rows) > limit:
            print(f"... {len(rows) - limit} more result(s); use --limit to raise the cap", file=sys.stderr)


def _route_rows(cuwplus_root: Path) -> list[dict[str, Any]]:
    ini_root = cuwplus_root / "Ini"
    if not ini_root.is_dir():
        return []
    shared, _ = factory_routes_from_ini_root(ini_root)
    return [
        {
            **row,
            "kind": "route",
            "row": row["row_index"],
            "contact_type": row["factory_identifier"],
        }
        for row in shared
    ]


def cmd_status(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    cuwplus = _resolve_cuwplus_root(gts, args.cuwplus_root)
    corpus = _resolve_cuw_corpus(args.cuw_root)
    db = _db_root(gts, args.region, args.family)
    payload = {
        "gtsplus_root": str(gts),
        "ddb_root": str(db),
        "ddb_files": len(list(db.glob("*.ddb"))) if db.is_dir() else 0,
        "gtsplus_bin": str(gts / "bin"),
        "pe_files": len(list((gts / "bin").glob("*.dll"))) + len(list((gts / "bin").glob("*.exe"))) if (gts / "bin").is_dir() else 0,
        "cuwplus_root": str(cuwplus),
        "route_ini_files": len(list((cuwplus / "Ini").glob("*.ini"))) if (cuwplus / "Ini").is_dir() else 0,
        "cuw_corpus": str(corpus),
        "cuw_files": len(list(corpus.glob("*.cuw"))) if corpus.is_dir() else 0,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for key, value in payload.items():
            print(f"{key}\t{value}")
    return 0


def cmd_ecu(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    path = _resolve_ecu(db_root, args.ecu)
    parser = DDBParser()
    db = parser.parse_ecu_db(path)
    rows = [
        {
            "table": table_id,
            "class": ECU_TABLE_CLASS_NAMES.get(table_id, "unknown"),
            "records": section.header.record_count,
            "record_size": section.decoded_record_size,
        }
        for table_id, section in sorted(db.sections.items())
    ]
    payload = {"path": str(path), "sections": rows}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(path)
        for row in rows:
            print(f"{row['table']:>3}\t{row['class']}\tcount={row['records']}\tsize={row['record_size']}")
    return 0


def cmd_did(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    path = _resolve_ecu(db_root, args.ecu)
    parser = DDBParser()
    db = parser.parse_ecu_db(path)
    strings = _english_strings(parser, db_root)
    rows = _monitor_rows(db, strings, path.name)
    if args.query:
        did = _normalize_did(args.query)
        if did is not None:
            rows = [r for r in rows if did in {r["primary_did"], r["alternate_did"]}]
        else:
            rows = [r for r in rows if _fold_match(args.query, r.get("name"), r.get("monitor_key"), r.get("physical_data_key"))]
    _print_rows(rows, as_json=args.json, limit=args.limit)
    return 0


def cmd_dtc(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    path = _resolve_ecu(db_root, args.ecu)
    parser = DDBParser()
    db = parser.parse_ecu_db(path)
    strings = _english_strings(parser, db_root)
    rows = _dtc_rows(parser, db, strings, path.name)
    if args.query:
        rows = [r for r in rows if _fold_match(args.query, r.get("code"), r.get("packed_dtc"), r.get("description"), r.get("failure"))]
    _print_rows(rows, as_json=args.json, limit=args.limit)
    return 0


def _search_ddbs(
    query: str,
    db_root: Path,
    *,
    ecu_filter: str | None,
    kinds: set[str],
    all_string_dbs: bool = False,
) -> list[dict[str, Any]]:
    parser = DDBParser()
    semantic_kinds = kinds.intersection({"did", "dtc", "behavior", "string"})
    strings = _english_strings(parser, db_root) if semantic_kinds else None
    results: list[dict[str, Any]] = []
    files = sorted(db_root.glob("*.ddb"), key=lambda p: p.name.casefold())
    if ecu_filter:
        files = [p for p in files if ecu_filter.casefold() in p.name.casefold()]
    for path in files:
        if path.name in {"M_English.ddb", "V_English.ddb", "U_English.ddb", "Toyota.ddb"} or re.match(r"^[MVU]_[A-Za-z]+\.ddb$", path.name):
            continue
        if "file" in kinds and _fold_match(query, path.name):
            results.append({"kind": "file", "source": str(path.relative_to(db_root))})
        if not kinds.intersection({"did", "dtc", "behavior"}):
            continue
        assert strings is not None
        try:
            db = parser.parse_ecu_db(path)
        except (ValueError, OSError):
            continue
        if "did" in kinds:
            for row in _monitor_rows(db, strings, path.name):
                if _fold_match(query, row.get("name"), f"0x{row['primary_did']:04X}", f"0x{row['alternate_did']:04X}"):
                    results.append(row)
        if "dtc" in kinds:
            for row in _dtc_rows(parser, db, strings, path.name):
                if _fold_match(query, row.get("code"), row.get("packed_dtc"), row.get("description"), row.get("failure")):
                    results.append(row)
        if "behavior" in kinds:
            for row in _behavior_rows(db, strings, path.name):
                if _fold_match(query, row.get("signature"), row.get("name"), row.get("comment")):
                    results.append(row)
    if "string" in kinds and not ecu_filter:
        assert strings is not None
        string_dbs = _english_string_dbs(parser, db_root, strings) if all_string_dbs else {"M_English.ddb": strings}
        for source, string_db in string_dbs.items():
            for offset, text in string_db.search(query, limit=500):
                results.append({"kind": "string", "source": source, "offset": offset, "text": text})
    return results


def _iter_pe_candidates(gts_root: Path, cuwplus_root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for root in (gts_root / "bin", cuwplus_root, cuwplus_root / "unpack"):
        if not root.is_dir():
            continue
        for pattern in ("*.dll", "*.exe", "*.dll._", "*.exe._"):
            for path in root.glob(pattern):
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield resolved


def _route_match(query: str, row: dict[str, Any]) -> bool:
    return _fold_match(
        query,
        row.get("contact_type"),
        row.get("parameter_file"),
        row.get("cid_getter"),
        row.get("prepare_writer"),
        row.get("flash_writer"),
        row.get("get_can_id_cid"),
        row.get("get_can_id_prepare"),
        row.get("get_can_id_flash"),
        row.get("version_contract"),
        row.get("prepare_retry"),
    )


def cmd_search(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    cuwplus = _resolve_cuwplus_root(gts, args.cuwplus_root)
    db_root = _db_root(gts, args.region, args.family)
    kinds = set(args.kind or ["did", "dtc", "behavior", "string", "file", "route", "cuw"])
    results = _search_ddbs(
        args.query,
        db_root,
        ecu_filter=args.ecu,
        kinds=kinds,
        all_string_dbs=args.all_string_dbs,
    )
    if "file" in kinds:
        for path in _iter_pe_candidates(gts, cuwplus):
            if _fold_match(args.query, path.name):
                try:
                    rel = path.relative_to(ROOT)
                except ValueError:
                    rel = path
                results.append({"kind": "file", "source": str(rel)})
    if "route" in kinds:
        results.extend(row for row in _route_rows(cuwplus) if _route_match(args.query, row))
    if "cuw" in kinds:
        results.extend(_search_cuw_corpus(args.query, _resolve_cuw_corpus(args.cuw_root)))
    _print_rows(results, as_json=args.json, limit=args.limit)
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    rows = _route_rows(_resolve_cuwplus_root(gts, args.cuwplus_root))
    if args.query:
        rows = [row for row in rows if _route_match(args.query, row)]
    _print_rows(rows, as_json=args.json, limit=args.limit)
    return 0



def _parse_master_key(value: str) -> int | None:
    try:
        return int(value, 0)
    except ValueError:
        return None


def _master_category_rows(parser: DDBParser, master: Any, strings: StringDataBase) -> list[dict[str, Any]]:
    return [
        {
            "category_id": entry.category_id,
            "generation": entry.generation,
            "database": entry.database_name,
            "short_name": entry.ecu_short_name,
            "name": strings.get_string(entry.ecu_name_string_index) or "",
        }
        for entry in parser.extract_master_ecu_categories(master.sections[16])
    ]


def _resolve_master_category(parser: DDBParser, master: Any, strings: StringDataBase, query: str) -> dict[str, Any]:
    rows = _master_category_rows(parser, master, strings)
    numeric = _parse_master_key(query)
    if numeric is not None:
        matches = [row for row in rows if row["category_id"] == numeric]
    else:
        exact = [
            row for row in rows
            if query.casefold() in {
                row["database"].casefold(),
                Path(row["database"]).stem.casefold(),
                row["short_name"].casefold(),
                row["name"].casefold(),
            }
        ]
        matches = exact or [
            row for row in rows
            if _fold_match(query, row["database"], row["short_name"], row["name"])
        ]
    if not matches:
        raise SystemExit(f"no Toyota master ECU category matches {query!r}")
    category_ids = {row["category_id"] for row in matches}
    if len(category_ids) != 1:
        summary = "\n".join(
            f"  {row['category_id']}\t{row['database']}\t{row['name']}"
            for row in matches[:40]
        )
        raise SystemExit(f"ambiguous Toyota master ECU category {query!r}; matches:\n{summary}")
    return matches[0]


def _master_role_catalog(parser: DDBParser, master: Any, bin_root: Path | None = None) -> list[dict[str, Any]]:
    if bin_root is not None:
        return role_operation_catalog(parser, master, bin_root)["roles"]
    by_role: dict[int, list[Any]] = {}
    for entry in parser.extract_master_dlls(master.sections[19]):
        by_role.setdefault(entry.dll_role_id, []).append(entry)
    rows = []
    for role, entries in by_role.items():
        plugin_counts: dict[str, int] = {}
        for entry in entries:
            plugin_counts[entry.dll_name] = plugin_counts.get(entry.dll_name, 0) + 1
        plugins = [
            {"dll": dll, "binding_count": count}
            for dll, count in sorted(plugin_counts.items(), key=lambda item: (-item[1], item[0].casefold()))
        ]
        rows.append({
            "role": role,
            "role_hex": f"0x{role:X}",
            "binding_count": len(entries),
            "category_count": len({entry.category_id for entry in entries}),
            "plugins": plugins,
        })
    return sorted(rows, key=lambda row: (-row["binding_count"], row["role"]))

def _master_plugins(parser: DDBParser, master: Any, category_id: int) -> list[dict[str, Any]]:
    return [
        {"role": entry.dll_role_id, "role_hex": f"0x{entry.dll_role_id:X}", "dll": entry.dll_name}
        for entry in sorted(
            (row for row in parser.extract_master_dlls(master.sections[19]) if row.category_id == category_id),
            key=lambda row: (row.dll_role_id, row.dll_name.casefold()),
        )
    ]


def _master_functions(parser: DDBParser, master: Any, strings: StringDataBase, category_id: int) -> list[dict[str, Any]]:
    return [
        {
            "function_id": entry.function_id,
            "function_hex": f"0x{entry.function_id:X}",
            "sort_key": entry.sort_key,
            "name": strings.get_string(entry.name_string_index) or "",
            "description": strings.get_string(entry.description_string_index) or "",
        }
        for entry in parser.extract_master_functions(master.sections[26])
        if entry.category_id == category_id
    ]


def _master_variable(master: Any, variable_id: int) -> dict[str, Any]:
    if variable_id == 0:
        return {"id": "0x0", "normalized_id": "0x0", "bytes": ""}
    # Current GTS+ CDbVariableTable::GetVariable namespaces references above
    # decimal 10000 (0x2710); subtract before the unchanged 1-based table lookup.
    normalized = variable_id - 0x2710 if variable_id > 0x2710 else variable_id
    section = master.sections[0]
    count = section.header.record_count
    if not 1 <= normalized <= count:
        raise ValueError(
            f"variable 0x{variable_id:X} normalizes to 0x{normalized:X}, outside 1..{count}"
        )
    data = section.decoded_data
    table_end = count * 6
    rel, length = struct.unpack_from("<IH", data, (normalized - 1) * 6)
    start = table_end + rel
    end = start + length
    if end > len(data):
        raise ValueError(f"variable 0x{variable_id:X} overruns variable pool")
    return {
        "id": f"0x{variable_id:X}",
        "normalized_id": f"0x{normalized:X}",
        "bytes": data[start:end].hex(),
    }


def _master_timer_rows(parser: DDBParser, master: Any, category_id: int | None = None) -> list[dict[str, Any]]:
    rows = [
        {
            "category_id": entry.category_id,
            "timer_id": entry.timer_id,
            "delay_ms": entry.delay_ms,
            "unknown_dword_08": entry.unknown_dword_08,
            "raw": entry.raw.hex(),
        }
        for entry in parser.extract_master_timers(master.sections[25])
        if category_id is None or entry.category_id == category_id
    ]
    return sorted(rows, key=lambda row: (row["category_id"], row["timer_id"]))


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@functools.lru_cache(maxsize=1)
def _execution_model() -> dict[str, Any]:
    return json.loads(EXECUTION_MODEL.read_text())


def _execution_plugin_profiles() -> dict[str, dict[str, Any]]:
    return _execution_model()["gtsplus_continuity"]["dll_role_schema"]["plugin_semantics"]


def _master_command_binding(parser: DDBParser, master: Any, category_id: int, role: int) -> Any:
    matches = [
        entry for entry in parser.extract_master_dlls(master.sections[19])
        if entry.category_id == category_id and entry.dll_role_id == role
    ]
    if len(matches) != 1:
        raise ValueError(f"category {category_id} role 0x{role:X} resolved {len(matches)} plugin bindings")
    return matches[0]


def _semantic_profile_for_plugin(plugin_path: Path, role: int) -> tuple[str | None, dict[str, Any] | None, str]:
    if not plugin_path.is_file():
        return None, None, "plugin_file_missing"
    actual_sha = _file_sha256(plugin_path)
    for name, profile in _execution_plugin_profiles().items():
        binding = profile.get("example_binding", {})
        plugin = profile.get("plugin", {})
        if binding.get("dll_role_id") == role and plugin.get("sha256") == actual_sha:
            return name, profile, "exact_plugin_identity"
    return None, None, "plugin_semantics_unrecovered_for_identity"


def _active_test_list_category_plan(parser: DDBParser, category: dict[str, Any], db_root: Path) -> dict[str, Any]:
    mode = int(category["generation"]) & 0xE0
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    direct = db.sections.get(68)
    routine = db.sections.get(71)
    multi = db.sections.get(33)
    if direct is not None and direct.decoded_record_size != 64:
        raise ValueError(f"{db_path.name}: type-68 record size {direct.decoded_record_size}, expected 64")
    if routine is not None and routine.decoded_record_size != 72:
        raise ValueError(f"{db_path.name}: type-71 record size {routine.decoded_record_size}, expected 72")
    direct_count = 0 if direct is None else direct.header.record_count
    routine_count = 0 if routine is None else routine.header.record_count
    return {
        "generation": int(category["generation"]),
        "generation_mode": f"0x{mode:X}",
        "direct_table": 68,
        "direct_table_class": ECU_TABLE_CLASS_NAMES[68],
        "direct_candidate_count": direct_count,
        "routine_table": 71,
        "routine_table_class": ECU_TABLE_CLASS_NAMES[71],
        "routine_candidate_count": routine_count,
        "multi_did_table_present": multi is not None,
        "multi_did_count": 0 if multi is None else multi.header.record_count,
        "support_builders": (
            ["CreateEnableDataIdListForSubaruCheckDID", "CreateEnableRIdListforSUBARU"]
            if mode == 0x20
            else ["CreateEnableDataIdList", "CreateEnableRIdList"]
        ),
        "direct_support_helper": (
            "CheckSupportDidForSUBARU" if mode == 0x20 else "CheckSupportDid"
        ),
        "routine_support_helper": (
            "CheckSupportRidForSUBARU" if mode == 0x20 else "CheckSupportRid"
        ),
        "runtime_support_required": direct_count > 0 or routine_count > 0,
        "runtime_boundary": (
            "candidate counts are static; direct tests require DID support evaluation and routine tests require "
            "RID support evaluation before Techstream's final Active Test list is known"
        ),
    }


def _direct_active_test_selected_row(
    parser: DDBParser,
    category: dict[str, Any],
    db_root: Path,
    active_test_id: int,
    strings: StringDataBase | None = None,
) -> tuple[Any, Path, dict[str, Any]]:
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(68)
    if section is None:
        raise ValueError(f"{db_path.name}: selected direct Active Test table 68 is absent")
    if section.decoded_record_size != 64:
        raise ValueError(f"{db_path.name}: type-68 record size {section.decoded_record_size}, expected 64")
    matches = []
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * 64 : (index + 1) * 64]
        if struct.unpack_from("<H", raw, 0x20)[0] == active_test_id:
            matches.append((index, raw))
    if len(matches) != 1:
        raise ValueError(
            f"{db_path.name}: direct Active Test ID 0x{active_test_id:X} resolved {len(matches)} type-68 rows"
        )
    index, raw = matches[0]
    name_index = struct.unpack_from("<I", raw, 0x0C)[0]
    selected = {
        "record": index,
        "active_test_id": active_test_id,
        "active_test_id_hex": f"0x{active_test_id:X}",
        "name_string_index": name_index,
        "name": (strings.get_string(name_index) or "") if strings is not None else None,
        "physical_data_key": struct.unpack_from("<H", raw, 0x24)[0],
        "active_test_pattern_key": struct.unpack_from("<H", raw, 0x26)[0],
        "bit_start": struct.unpack_from("<H", raw, 0x28)[0],
        "bit_end": struct.unpack_from("<H", raw, 0x2A)[0],
        "sort_key": struct.unpack_from("<H", raw, 0x2C)[0],
        "exception_id": struct.unpack_from("<H", raw, 0x2E)[0],
        "panel_key_0": struct.unpack_from("<H", raw, 0x30)[0],
        "panel_key_1": struct.unpack_from("<H", raw, 0x32)[0],
        "initial_read_did": struct.unpack_from("<H", raw, 0x34)[0],
        "direct_monitor_key": struct.unpack_from("<H", raw, 0x36)[0],
        "initial_read_mode": raw[0x39],
        "pattern": raw[0x3A],
        "exception_flag": raw[0x3B],
        "panel_check_mode": raw[0x3C],
        "monitor_link_mode": raw[0x3D],
        "raw": raw.hex(),
    }
    return db, db_path, selected


def _routine_active_test_selected_row(
    parser: DDBParser,
    category: dict[str, Any],
    db_root: Path,
    active_test_id: int,
    strings: StringDataBase | None = None,
) -> tuple[Any, Path, dict[str, Any]]:
    """Resolve one current 72-byte type-71 P5 routine Active-Test row."""
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(71)
    if section is None:
        raise ValueError(f"{db_path.name}: selected routine Active Test table 71 is absent")
    if section.decoded_record_size != 72:
        raise ValueError(
            f"{db_path.name}: current type-71 record size {section.decoded_record_size}, expected 72"
        )
    matches = []
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * 72 : (index + 1) * 72]
        if struct.unpack_from("<H", raw, 0x1E)[0] == active_test_id:
            matches.append((index, raw))
    if len(matches) != 1:
        raise ValueError(
            f"{db_path.name}: routine Active Test ID 0x{active_test_id:X} resolved {len(matches)} type-71 rows"
        )
    index, raw = matches[0]
    name_index = struct.unpack_from("<I", raw, 0x08)[0]
    selected = {
        "record": index,
        "active_test_id": active_test_id,
        "active_test_id_hex": f"0x{active_test_id:X}",
        "name_string_index": name_index,
        "name": (strings.get_string(name_index) or "") if strings is not None else None,
        "routine_id": struct.unpack_from("<H", raw, 0x1C)[0],
        "routine_id_hex": f"0x{struct.unpack_from('<H', raw, 0x1C)[0]:04X}",
        "active_test_pattern_key": struct.unpack_from("<H", raw, 0x24)[0],
        "routine_command_variable": struct.unpack_from("<H", raw, 0x28)[0],
        "routine_stop_command_variable": struct.unpack_from("<H", raw, 0x2A)[0],
        "output_mask_value_variable": struct.unpack_from("<H", raw, 0x2C)[0],
        "output_mask_button_variable": struct.unpack_from("<H", raw, 0x2E)[0],
        "routine_status_key": struct.unpack_from("<H", raw, 0x30)[0],
        "pattern_display_variable_key": struct.unpack_from("<H", raw, 0x3C)[0],
        "sort_key": struct.unpack_from("<H", raw, 0x40)[0],
        "raw": raw.hex(),
    }
    return db, db_path, selected


def _routine_active_test_executor_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    selected: dict[str, Any],
) -> dict[str, Any]:
    """Materialize the current GTS+ P5 UDS RoutineControl contract."""
    category_id = int(category["category_id"])
    rid = int(selected["routine_id"])

    def phase(selector: int, subfunction: int, variable_field: str | None) -> dict[str, Any]:
        rows = _master_frame_rows(parser, master, category_id, selector)
        if len(rows) != 1:
            raise ValueError(
                f"category {category_id}: routine selector 0x{selector:X} resolved {len(rows)} frames"
            )
        frame = rows[0]
        expected = bytes((0x31, subfunction, 0xFF, 0xFF))
        send = bytes.fromhex(frame["send"]["bytes"])
        if send != expected:
            raise ValueError(
                f"category {category_id}: selector 0x{selector:X} base request {send.hex()} != {expected.hex()}"
            )
        expected_reply = bytes((0x71, subfunction)).hex()
        if frame["receive_check"]["bytes"] != expected_reply:
            raise ValueError(
                f"category {category_id}: selector 0x{selector:X} positive check "
                f"{frame['receive_check']['bytes']} != {expected_reply}"
            )
        request = bytearray(send)
        request[2] = (rid >> 8) & 0xFF
        request[3] = rid & 0xFF
        variable = None
        if variable_field is not None:
            variable_id = int(selected[variable_field])
            variable = _master_variable(master, variable_id)
            if variable_id:
                request.extend(bytes.fromhex(variable["bytes"]))
        return {
            "selector": f"0x{selector:X}",
            "subfunction": f"0x{subfunction:02X}",
            "base_frame": frame,
            "static_command_variable": variable,
            "materialized_static_request": request.hex(),
        }

    start = phase(0xD5, 0x01, "routine_command_variable")
    stop = phase(0xD6, 0x02, "routine_stop_command_variable")
    result = phase(0xD7, 0x03, None)
    value_mask = _master_variable(master, int(selected["output_mask_value_variable"]))
    button_mask = _master_variable(master, int(selected["output_mask_button_variable"]))
    fixed = not any(
        int(selected[field])
        for field in (
            "routine_command_variable",
            "routine_stop_command_variable",
            "output_mask_value_variable",
            "output_mask_button_variable",
        )
    )
    return {
        "service": "0x31",
        "service_name": "RoutineControl",
        "positive_response": "0x71",
        "routine_id": rid,
        "routine_id_hex": f"0x{rid:04X}",
        "start": start,
        "stop": stop,
        "result": result,
        "output_mask_value": value_mask,
        "output_mask_button": button_mask,
        "fixed_request": fixed,
        "parameterization": (
            "fixed: no routine command, stop-command, value-mask, or button-mask variable is referenced"
            if fixed
            else "parameterized: static command bytes and/or runtime value/button bytes are merged through explicit type-71 variable masks"
        ),
        "transport": (
            "DataMonitorPhase5 passes buffer+1/length-1 to the shared active_test_start interface with "
            "ActiveTestType=1; DataListIF re-prepends 0x31, queues/replaces by RID, accepts 0x71, "
            "and the common P5 J2534 worker sends the queued frame via SendIntExt"
        ),
        "boundary": "static plan only; does not execute RoutineControl or prove outer session/authentication requirements",
    }


def _direct_active_test_executor_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db: Any,
    db_path: Path,
    selected: dict[str, Any],
) -> dict[str, Any]:
    """Materialize the static P5 direct Active-Test executor contract.

    The total DID data length is intentionally left symbolic because the
    current DataMonitorPhase5 runtime reads it from CCmdDataIdLengthList.
    """
    section = db.sections.get(67)
    if section is None:
        raise ValueError(f"{db_path.name}: direct Active-Test table 67 is absent")
    if section.decoded_record_size != 18:
        raise ValueError(f"{db_path.name}: type-67 record size {section.decoded_record_size}, expected 18")
    did = selected["initial_read_did"]
    matches = []
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * 18 : (index + 1) * 18]
        if struct.unpack_from("<H", raw, 0x02)[0] == did:
            matches.append((index, raw))
    if len(matches) != 1:
        raise ValueError(f"{db_path.name}: DID 0x{did:04X} resolved {len(matches)} type-67 rows")
    record_index, raw = matches[0]
    encoding_mode = raw[0x0A]

    def frame(selector: int, expected: bytes) -> dict[str, Any]:
        rows = _master_frame_rows(parser, master, int(category["category_id"]), selector)
        if len(rows) != 1:
            raise ValueError(
                f"category {category['category_id']}: Active-Test selector 0x{selector:X} resolved {len(rows)} frames"
            )
        row = rows[0]
        send = bytes.fromhex(row["send"]["bytes"])
        if send != expected:
            raise ValueError(
                f"category {category['category_id']}: selector 0x{selector:X} base request {send.hex()} != {expected.hex()}"
            )
        return row

    start_frame = frame(0x9D, bytes.fromhex("2fffff03"))
    stop_frame = frame(0x64, bytes.fromhex("2fffff00"))
    if start_frame["receive_check"]["bytes"] != "6f" or stop_frame["receive_check"]["bytes"] != "6f":
        raise ValueError(f"category {category['category_id']}: Active-Test positive response is no longer 0x6F")

    start_prefix = bytearray.fromhex(start_frame["send"]["bytes"])
    stop_prefix = bytearray.fromhex(stop_frame["send"]["bytes"])
    for buf in (start_prefix, stop_prefix):
        buf[1] = (did >> 8) & 0xFF
        buf[2] = did & 0xFF
    bit_start = selected["bit_start"]
    bit_end = selected["bit_end"]
    minimum_length = bit_end // 8 + 1
    plan: dict[str, Any] = {
        "service": "0x2F",
        "service_name": "InputOutputControlByIdentifier",
        "positive_response": "0x6F",
        "data_id_for_act": {
            "table": 67,
            "table_class": ECU_TABLE_CLASS_NAMES[67],
            "record": record_index,
            "did": did,
            "did_hex": f"0x{did:04X}",
            "encoding_mode": encoding_mode,
            "raw": raw.hex(),
        },
        "start": {
            "selector": "0x9D",
            "control_parameter": "0x03",
            "control_name": "shortTermAdjustment",
            "base_frame": start_frame,
            "materialized_prefix": start_prefix.hex(),
            "formula": f"{start_prefix.hex()} || N-byte value payload",
        },
        "stop": {
            "selector": "0x64",
            "control_parameter": "0x00",
            "control_name": "returnControlToECU",
            "base_frame": stop_frame,
            "materialized_prefix": stop_prefix.hex(),
            "formula": f"{stop_prefix.hex()} || N-byte control-enable mask",
        },
        "runtime_data_length": {
            "symbol": "N",
            "source": "CCmdDataIdLengthList runtime support cache",
            "minimum_from_bit_geometry": minimum_length,
            "boundary": "static DDB geometry does not prove the runtime cached Data-ID length",
        },
        "bit_range": {"start": bit_start, "end": bit_end},
        "encoding": (
            "mode 1 zero-fills N bytes, then uses raw CStartActTstSnd +0x24 with byte=bit_end>>3 "
            "and shift=7-(bit_end&7); stop appends the N-byte bit-range control-enable mask"
            if encoding_mode == 1
            else f"encoding mode {encoding_mode} is selected by type-67 +0x0A; this CLI currently exposes exact mode-1 packing only"
        ),
        "transport": (
            "DataMonitorPhase5 strips the existing SID for its interface call; DataListIF CCommEventPhase5AT "
            "re-prepends 0x2F, GetSndFrame copies the queued bytes unchanged, and the P5 J2534 thread sends them via SendIntExt"
        ),
    }
    if encoding_mode == 1 and bit_start == bit_end:
        byte_index = bit_end // 8
        shift = 7 - (bit_end & 7)
        off = bytearray(minimum_length)
        on = bytearray(minimum_length)
        mask = bytearray(minimum_length)
        on[byte_index] = 1 << shift
        mask[byte_index] = 1 << shift
        plan["minimum_length_examples"] = {
            "raw_0": (start_prefix + off).hex(),
            "raw_1": (start_prefix + on).hex(),
            "return_control": (stop_prefix + mask).hex(),
            "qualification": (
                f"uses N={minimum_length}, the static minimum required by bit {bit_end}; "
                "not proof that the runtime DataIdLengthList entry has that length"
            ),
        }
    return plan

def _active_test_init_selected_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db_root: Path,
    active_test_id: int,
    strings: StringDataBase | None = None,
) -> dict[str, Any]:
    db, db_path, selected = _direct_active_test_selected_row(
        parser, category, db_root, active_test_id, strings
    )

    mode = selected["initial_read_mode"]
    transaction: dict[str, Any] = {"mode": mode, "performed": False}
    if mode == 0:
        frames = _master_frame_rows(parser, master, int(category["category_id"]), 0xCA)
        if len(frames) != 1:
            raise ValueError(
                f"category {category['category_id']}: role-0x08 selector 0xCA resolved {len(frames)} frames"
            )
        frame = frames[0]
        base = bytearray.fromhex(frame["send"]["bytes"])
        if len(base) < 3 or base[0] != 0x22:
            raise ValueError(
                f"category {category['category_id']}: selector 0xCA base request is not 22xxxx: {base.hex()}"
            )
        did = selected["initial_read_did"]
        base[1] = (did >> 8) & 0xFF
        base[2] = did & 0xFF
        transaction = {
            "mode": mode,
            "performed": True,
            "selector": "0xCA",
            "base_frame": frame,
            "materialized_send": base.hex(),
            "receive_check": frame["receive_check"]["bytes"],
            "bit_start": selected["bit_start"],
            "bit_end": selected["bit_end"],
        }
    elif mode == 1:
        transaction["reason"] = "type-68 initial_read_mode == 1"
    else:
        transaction["reason"] = "plugin rejects modes other than 0/1 as C0040102"

    mode_generation = int(category["generation"]) & 0xE0
    monitor_table = 157 if mode_generation == 0x60 else 62
    linked: dict[str, Any] = {
        "mode": selected["monitor_link_mode"],
        "table": monitor_table,
        "monitor_key": None,
        "resolution": None,
    }
    if selected["monitor_link_mode"] == 1:
        linked["monitor_key"] = selected["direct_monitor_key"]
        linked["resolution"] = "direct type-68 +0x36"
    else:
        monitor = db.sections.get(monitor_table)
        if monitor is None:
            linked["resolution"] = "generation-selected monitor table absent"
        elif monitor.decoded_record_size < 0x48:
            raise ValueError(
                f"{db_path.name}: monitor table {monitor_table} record size 0x{monitor.decoded_record_size:X} too small"
            )
        else:
            candidates = []
            size = monitor.decoded_record_size
            for monitor_index in range(monitor.header.record_count):
                mon = monitor.decoded_data[monitor_index * size : (monitor_index + 1) * size]
                if not (struct.unpack_from("<I", mon, 0x30)[0] & 0x40):
                    continue
                if struct.unpack_from("<H", mon, 0x46)[0] != selected["initial_read_did"]:
                    continue
                if struct.unpack_from("<H", mon, 0x3C)[0] != selected["bit_start"]:
                    continue
                if struct.unpack_from("<H", mon, 0x3E)[0] != selected["bit_end"]:
                    continue
                candidates.append({
                    "record": monitor_index,
                    "monitor_key": struct.unpack_from("<H", mon, 0x34)[0],
                })
            linked["candidates"] = candidates
            if len(candidates) == 1:
                linked["monitor_key"] = candidates[0]["monitor_key"]
                linked["resolution"] = "unique DID/bit-range match from plugin scan"
            else:
                linked["resolution"] = f"plugin scan produced {len(candidates)} matches"

    if strings is not None and linked["monitor_key"] is not None:
        semantic = [
            row for row in _monitor_rows(db, strings, db_path.name)
            if row.get("monitor_key") == linked["monitor_key"]
        ]
        if len(semantic) == 1:
            linked["monitor"] = semantic[0]

    executor = _direct_active_test_executor_plan(parser, master, category, db, db_path, selected)

    return {
        "selected_test": selected,
        "initial_transaction": transaction,
        "linked_monitor": linked,
        "executor": executor,
        "runtime_boundary": (
            "selected-row and initial-request materialization are offline deterministic; whether the test is offered "
            "and panel entries are supported still depends on role-0x06/live support state"
        ),
    }


def _active_test_signal_info_selected_plan(
    parser: DDBParser,
    category: dict[str, Any],
    db_root: Path,
    active_test_id: int,
    strings: StringDataBase,
) -> dict[str, Any]:
    db, db_path, selected = _direct_active_test_selected_row(
        parser, category, db_root, active_test_id, strings
    )

    def unique_record(table: int, key_offset: int, key: int) -> tuple[int, bytes]:
        section = db.sections.get(table)
        if section is None:
            raise ValueError(f"{db_path.name}: required role-0x70 table {table} is absent")
        size = section.decoded_record_size
        matches = []
        for index in range(section.header.record_count):
            raw = section.decoded_data[index * size : (index + 1) * size]
            if len(raw) >= key_offset + 2 and struct.unpack_from("<H", raw, key_offset)[0] == key:
                matches.append((index, raw))
        if len(matches) != 1:
            raise ValueError(
                f"{db_path.name}: table {table} key 0x{key:X} resolved {len(matches)} rows"
            )
        return matches[0]

    pattern_index, pattern = unique_record(12, 0x00, selected["active_test_pattern_key"])
    physical_index, physical = unique_record(13, 0x0C, selected["physical_data_key"])
    unit_key = struct.unpack_from("<H", physical, 0x0E)[0]
    unit_index, unit = unique_record(15, 0x04, unit_key)
    pattern_display_key = struct.unpack_from("<H", pattern, 0x0A)[0]
    display = []
    section14 = db.sections.get(14)
    if section14 is None:
        raise ValueError(f"{db_path.name}: required role-0x70 table 14 is absent")
    for index in range(section14.header.record_count):
        size = section14.decoded_record_size
        raw = section14.decoded_data[index * size : (index + 1) * size]
        if len(raw) >= 0x0E and struct.unpack_from("<H", raw, 0x0C)[0] == pattern_display_key:
            display.append({
                "record": index,
                "value": struct.unpack_from("<I", raw, 0x04)[0],
                "text": strings.get_string(struct.unpack_from("<I", raw, 0x00)[0]),
                "raw": raw.hex(),
            })

    return {
        "selected_test": selected,
        "active_test_pattern": {
            "record": pattern_index,
            "key": selected["active_test_pattern_key"],
            "button_size": pattern[0x15],
            "key_operation_pattern": pattern[0x13],
            "key_invalid_flag": pattern[0x12],
            "maintenance_time": struct.unpack_from("<H", pattern, 0x04)[0],
            "auto_continue_time": struct.unpack_from("<H", pattern, 0x06)[0],
            "lock_time": struct.unpack_from("<H", pattern, 0x0C)[0],
            "pattern_display_key": pattern_display_key,
            "raw": pattern.hex(),
        },
        "physical": {
            "record": physical_index,
            "key": selected["physical_data_key"],
            "mul": struct.unpack_from("<i", physical, 0x00)[0],
            "div": struct.unpack_from("<i", physical, 0x04)[0],
            "offset": struct.unpack_from("<i", physical, 0x08)[0],
            "signed": bool(physical[0x14]),
            "decimal_point_count": physical[0x15],
            "unit_key": unit_key,
            "unit_record": unit_index,
            "unit": strings.get_string(struct.unpack_from("<I", unit, 0x00)[0]),
            "unit_genre_id": struct.unpack_from("<H", unit, 0x06)[0],
            "raw": physical.hex(),
        },
        "display_info": display,
        "runtime_boundary": (
            "role-0x70 is metadata-only for the exact plugin identity; this selected-item plan does not execute "
            "transport or prove role-0x06 live availability"
        ),
    }


def _multi_active_test_category_plan(
    parser: DDBParser, category: dict[str, Any], db_root: Path
) -> dict[str, Any]:
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(33)
    if section is None:
        return {
            "group_table": 33,
            "group_table_class": ECU_TABLE_CLASS_NAMES.get(33, "unknown"),
            "group_count": 0,
            "membership_count": 0,
            "groups": [],
            "boundary": "category binds role 0x63 but has no type-33 multi-control membership table",
        }
    if section.decoded_record_size != 12:
        raise ValueError(f"{db_path.name}: type-33 record size {section.decoded_record_size}, expected 12")
    groups: dict[int, list[dict[str, Any]]] = {}
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * 12 : (index + 1) * 12]
        group_id = struct.unpack_from("<H", raw, 0x00)[0]
        groups.setdefault(group_id, []).append({
            "record": index,
            "member_active_test_id": struct.unpack_from("<H", raw, 0x02)[0],
            "sort_order": struct.unpack_from("<I", raw, 0x06)[0],
            "auxiliary_byte": raw[0x0B],
            "raw": raw.hex(),
        })
    rows = [
        {
            "group_id": group_id,
            "group_id_hex": f"0x{group_id:X}",
            "members": sorted(members, key=lambda row: (row["sort_order"], row["member_active_test_id"])),
        }
        for group_id, members in sorted(groups.items())
    ]
    return {
        "group_table": 33,
        "group_table_class": ECU_TABLE_CLASS_NAMES.get(33, "unknown"),
        "record_size": 12,
        "group_count": len(rows),
        "membership_count": section.header.record_count,
        "groups": rows,
        "boundary": "type-33 rows are static multi-control expansion; each member still follows its type-68 initialization path",
    }


def _multi_active_test_group_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db_root: Path,
    group_id: int,
    strings: StringDataBase,
) -> dict[str, Any]:
    census = _multi_active_test_category_plan(parser, category, db_root)
    matches = [group for group in census["groups"] if group["group_id"] == group_id]
    if len(matches) != 1:
        raise ValueError(
            f"{category['database']}: multi Active Test group 0x{group_id:X} resolved {len(matches)} type-33 groups"
        )
    group = matches[0]
    _, _, parent = _direct_active_test_selected_row(parser, category, db_root, group_id, strings)
    frames = _master_frame_rows(parser, master, int(category["category_id"]), 0xCA)
    if len(frames) != 1:
        raise ValueError(
            f"category {category['category_id']}: role-0x63 selector 0xCA resolved {len(frames)} frames"
        )
    frame = frames[0]
    members = []
    for membership in group["members"]:
        _, _, selected = _direct_active_test_selected_row(
            parser, category, db_root, membership["member_active_test_id"], strings
        )
        mode = selected["initial_read_mode"]
        transaction: dict[str, Any] = {"mode": mode, "performed": False}
        if mode == 0:
            send = bytearray.fromhex(frame["send"]["bytes"] )
            if len(send) < 3 or send[0] != 0x22:
                raise ValueError(
                    f"category {category['category_id']}: selector 0xCA base request is not 22xxxx: {send.hex()}"
                )
            did = selected["initial_read_did"]
            send[1] = (did >> 8) & 0xFF
            send[2] = did & 0xFF
            transaction = {
                "mode": 0,
                "performed": True,
                "selector": "0xCA",
                "materialized_send": send.hex(),
                "receive_check": frame["receive_check"]["bytes"],
                "bit_start": selected["bit_start"],
                "bit_end": selected["bit_end"],
            }
        elif mode == 1:
            transaction["reason"] = "type-68 initial_read_mode == 1"
        else:
            transaction["reason"] = "plugin rejects modes other than 0/1 as C0040102"
        members.append({
            **membership,
            "selected_test": selected,
            "initial_transaction": transaction,
        })
    return {
        "group": {
            "group_id": group_id,
            "group_id_hex": f"0x{group_id:X}",
            "name": parent["name"],
            "selected_test": parent,
            "member_count": len(members),
        },
        "base_frame": frame,
        "members": members,
        "runtime_boundary": (
            "group expansion, ordering, type-68 member fields, and initial request materialization are static; "
            "the role does not imply that every category binding has type-33 groups"
        ),
    }


def _active_test_monitor_category_plan(
    parser: DDBParser, category: dict[str, Any], db_root: Path
) -> dict[str, Any]:
    mode = int(category["generation"]) & 0xE0
    table = 157 if mode == 0x60 else 62
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(table)
    if section is None:
        raise ValueError(f"{db_path.name}: role-0xAD selected monitor table {table}, but it is absent")
    size = section.decoded_record_size
    if size < 0x36:
        raise ValueError(f"{db_path.name}: monitor table {table} record size 0x{size:X} too small")
    counts = {
        "active_direct_include": 0,
        "active_runtime_check_support_pid": 0,
        "nonmember_direct_exclude": 0,
        "nonmember_runtime_probe_then_filter": 0,
    }
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * size : (index + 1) * size]
        flag = raw[0x30]
        active_member = bool(flag & 0x40)
        direct_decision = bool(flag & 0x10)
        if active_member and direct_decision:
            counts["active_direct_include"] += 1
        elif active_member:
            counts["active_runtime_check_support_pid"] += 1
        elif direct_decision:
            counts["nonmember_direct_exclude"] += 1
        else:
            counts["nonmember_runtime_probe_then_filter"] += 1
    active_count = counts["active_direct_include"] + counts["active_runtime_check_support_pid"]
    nonmember_count = counts["nonmember_direct_exclude"] + counts["nonmember_runtime_probe_then_filter"]
    return {
        "generation": int(category["generation"]),
        "generation_mode": f"0x{mode:X}",
        "candidate_table": table,
        "candidate_table_class": ECU_TABLE_CLASS_NAMES.get(table, "unknown"),
        "candidate_count": section.header.record_count,
        "record_size": size,
        "active_test_membership_bit": "0x40",
        "active_test_candidate_count": active_count,
        "nonmember_count": nonmember_count,
        "support_list_builder": (
            "CreateEnableDataIdListForSubaruCheckDID" if mode == 0x20 else "CreateEnableDataIdList"
        ),
        "candidate_partition": counts,
        "runtime_support_required": (
            counts["active_runtime_check_support_pid"] > 0
            or counts["nonmember_runtime_probe_then_filter"] > 0
        ),
        "runtime_boundary": (
            "bit-0x40 membership is static, but CheckSupportPid outcomes remain runtime/cache dependent; "
            "nonmember rows with bit4 clear are still support-probed by the plugin before the final 0x40 filter"
        ),
    }


def _monitor_list_category_plan(parser: DDBParser, category: dict[str, Any], db_root: Path) -> dict[str, Any]:
    mode = int(category["generation"]) & 0xE0
    table = 157 if mode == 0x60 else 62
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    section = db.sections.get(table)
    if section is None:
        raise ValueError(f"{db_path.name}: role-0x05 selected monitor table {table}, but it is absent")
    counts = {"direct_include": 0, "direct_exclude": 0, "runtime_check_support_pid": 0}
    size = section.decoded_record_size
    if size < 0x36:
        raise ValueError(f"{db_path.name}: monitor table {table} record size 0x{size:X} too small")
    for index in range(section.header.record_count):
        raw = section.decoded_data[index * size : (index + 1) * size]
        flag = raw[0x30]
        if flag & 0x10:
            counts["direct_include" if flag & 0x01 else "direct_exclude"] += 1
        else:
            counts["runtime_check_support_pid"] += 1
    return {
        "generation": int(category["generation"]),
        "generation_mode": f"0x{mode:X}",
        "candidate_table": table,
        "candidate_table_class": ECU_TABLE_CLASS_NAMES.get(table, "unknown"),
        "candidate_count": section.header.record_count,
        "record_size": size,
        "support_list_builder": (
            "CreateEnableDataIdListForSubaruCheckDID" if mode == 0x20 else "CreateEnableDataIdList"
        ),
        "candidate_partition": counts,
        "runtime_support_required": counts["runtime_check_support_pid"] > 0,
        "runtime_boundary": (
            "candidate partition is static; records in runtime_check_support_pid require support-cache/live ECU "
            "CheckSupportPid results before Techstream's final presented list is known"
        ),
    }


def _master_command_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    role: int,
    bin_root: Path,
    db_root: Path | None = None,
    selected_item: int | None = None,
    strings: StringDataBase | None = None,
) -> dict[str, Any]:
    category_id = int(category["category_id"])
    binding = _master_command_binding(parser, master, category_id, role)
    plugin_path = bin_root / binding.dll_name
    if plugin_path.is_file():
        try:
            operation = plugin_operation_signature(plugin_path)
        except pefile.PEFormatError:
            operation = {"surface": "plugin_pe_unparseable"}
        identity = {
            "path": plugin_path.name,
            "size": plugin_path.stat().st_size,
            "sha256": _file_sha256(plugin_path),
        }
    else:
        operation = {"surface": "plugin_file_missing"}
        identity = {"path": plugin_path.name, "size": None, "sha256": None}

    profile_name, profile, semantic_status = _semantic_profile_for_plugin(plugin_path, role)
    result: dict[str, Any] = {
        "category": category,
        "role": role,
        "role_hex": f"0x{role:X}",
        "plugin": binding.dll_name,
        "plugin_identity": identity,
        "operation_surface": operation["surface"],
        "semantic_status": semantic_status,
        "semantic_profile": profile_name,
        "frames": {},
        "timers": [],
        "response_model": None,
        "control_flow": None,
        "metadata_model": None,
        "list_model": None,
        "active_test_model": None,
        "active_test_init_model": None,
        "active_test_signal_info_model": None,
        "active_test_monitor_model": None,
        "multi_active_test_init_model": None,
        "boundary": (
            "Frames/timers are resolved from the selected category. Executable semantics are attached only "
            "when the selected plugin SHA-256 exactly matches a recovered profile."
        ),
    }
    if selected_item is not None and role not in {0x08, 0x63, 0x70}:
        raise ValueError("--item is currently supported only for Active Test roles 0x08, 0x63, and 0x70")
    if profile is None:
        return result

    if profile_name == "role_0x63_p5_multi_active_test_init":
        result["multi_active_test_init_model"] = dict(profile["init_model"])
        if db_root is not None:
            result["multi_active_test_init_model"]["category_plan"] = _multi_active_test_category_plan(
                parser, category, db_root
            )
            result["semantic_status"] = "exact_plugin_identity_and_category_multi_active_test_census"
        if selected_item is not None:
            if db_root is None or strings is None:
                raise ValueError("role-0x63 selected-group planning requires the category ECU database and strings")
            result["multi_active_test_init_model"]["selected_plan"] = _multi_active_test_group_plan(
                parser, master, category, db_root, selected_item, strings
            )
            result["semantic_status"] = "exact_plugin_identity_and_selected_multi_active_test_plan"
    elif profile_name == "role_0xad_p5_monitor_list_for_active_test":
        result["active_test_monitor_model"] = dict(profile["list_model"])
        if db_root is not None:
            result["active_test_monitor_model"]["category_plan"] = _active_test_monitor_category_plan(
                parser, category, db_root
            )
            result["semantic_status"] = "exact_plugin_identity_and_category_active_test_monitor_partition"
        else:
            result["semantic_status"] = "exact_plugin_identity_active_test_monitor_semantics"
    elif profile_name == "role_0x70_p5_active_test_signal_info":
        result["active_test_signal_info_model"] = dict(profile["metadata_model"])
        if selected_item is not None:
            if db_root is None or strings is None:
                raise ValueError("role-0x70 selected-item planning requires the category ECU database and strings")
            result["active_test_signal_info_model"]["selected_plan"] = _active_test_signal_info_selected_plan(
                parser, category, db_root, selected_item, strings
            )
            result["semantic_status"] = "exact_plugin_identity_and_selected_active_test_signal_info"
        else:
            result["semantic_status"] = "exact_plugin_identity_requires_selected_active_test"
    elif profile_name == "role_0x08_p5_active_test_init":
        result["active_test_init_model"] = dict(profile["init_model"])
        if selected_item is not None:
            if db_root is None:
                raise ValueError("role-0x08 selected-item planning requires the category ECU database")
            result["active_test_init_model"]["selected_plan"] = _active_test_init_selected_plan(
                parser, master, category, db_root, selected_item, strings
            )
            result["semantic_status"] = "exact_plugin_identity_and_selected_active_test_plan"
        else:
            result["semantic_status"] = "exact_plugin_identity_requires_selected_active_test"
    elif profile_name == "role_0x06_p5_active_test_list":
        result["active_test_model"] = dict(profile["list_model"])
        if db_root is not None:
            result["active_test_model"]["category_plan"] = _active_test_list_category_plan(parser, category, db_root)
            result["semantic_status"] = "exact_plugin_identity_and_category_active_test_partition"
        else:
            result["semantic_status"] = "exact_plugin_identity_active_test_list_semantics"
    elif profile_name == "role_0x05_p5_monitor_list":
        result["list_model"] = dict(profile["list_model"])
        if db_root is not None:
            result["list_model"]["category_plan"] = _monitor_list_category_plan(parser, category, db_root)
            result["semantic_status"] = "exact_plugin_identity_and_category_candidate_partition"
        else:
            result["semantic_status"] = "exact_plugin_identity_monitor_list_semantics"
    elif profile_name == "role_0x41_p5_signal_info":
        result["metadata_model"] = profile["metadata_model"]
        result["semantic_status"] = "exact_plugin_identity_metadata_only"
    elif profile_name == "role_0x52_generic_cid":
        rows = _master_frame_rows(parser, master, category_id, 0xDC)
        result["frames"]["request"] = rows[0] if len(rows) == 1 else None
        result["response_model"] = profile["response_model"]
        result["semantic_status"] = (
            "exact_plugin_identity_and_category_frame"
            if len(rows) == 1
            else "exact_plugin_identity_but_category_selector_0xDC_missing"
        )
    elif profile_name == "role_0x19_dtc_clear":
        primary = _master_frame_rows(parser, master, category_id, 0x01)
        fallback = _master_frame_rows(parser, master, category_id, 0x102)
        result["frames"]["primary"] = primary[0] if len(primary) == 1 else None
        result["frames"]["fallback"] = fallback[0] if len(fallback) == 1 else None
        result["timers"] = [row for row in _master_timer_rows(parser, master, category_id) if row["timer_id"] == 1]
        result["control_flow"] = profile["control_flow"]
        result["semantic_status"] = (
            "exact_plugin_identity_and_primary_frame"
            if len(primary) == 1
            else "exact_plugin_identity_but_primary_selector_0x1_missing"
        )
    return result


def _master_comm_set_rows(parser: DDBParser, master: Any) -> list[dict[str, Any]]:
    return [
        {
            "comm_set_id": entry.comm_set_id,
            "send_parameter": entry.send_parameter,
            "receive_timeout": entry.receive_timeout,
            "exception_handler_id": entry.exception_handler_id,
            "unknown_word_0c": entry.unknown_word_0c,
            "retry_count": entry.retry_count,
            "exception_handler_flag": entry.exception_handler_flag,
            "raw": entry.raw.hex(),
        }
        for entry in parser.extract_master_comm_sets(master.sections[29])
    ]


def _master_comm_set(parser: DDBParser, master: Any, comm_set_id: int) -> dict[str, Any]:
    matches = [row for row in _master_comm_set_rows(parser, master) if row["comm_set_id"] == comm_set_id]
    if len(matches) != 1:
        raise ValueError(f"master CommSet {comm_set_id} resolved {len(matches)} rows")
    return matches[0]


def _master_frame_rows(parser: DDBParser, master: Any, category_id: int, selector: int | None = None) -> list[dict[str, Any]]:
    func = master.sections[18]
    frame_table = master.sections[17]
    func_size = func.decoded_record_size
    frame_size = frame_table.decoded_record_size
    frames = {
        struct.unpack_from("<H", raw, 0)[0]: raw
        for raw in (
            frame_table.decoded_data[i * frame_size : (i + 1) * frame_size]
            for i in range(frame_table.header.record_count)
        )
    }
    rows = []
    for i in range(func.header.record_count):
        raw = func.decoded_data[i * func_size : (i + 1) * func_size]
        category, row_selector, comm_set, frame_id = struct.unpack_from("<HHHH", raw, 0)
        if category != category_id or (selector is not None and row_selector != selector):
            continue
        frame = frames.get(frame_id)
        if frame is None:
            raise ValueError(f"category {category_id} selector 0x{row_selector:X}: missing frame 0x{frame_id:X}")
        send_var, mask_var, check_var = struct.unpack_from("<HHH", frame, 2)
        rows.append({
            "kind": "frame",
            "category_id": category_id,
            "selector": f"0x{row_selector:X}",
            "comm_set": comm_set,
            "comm_set_metadata": _master_comm_set(parser, master, comm_set),
            "comm_frame_id": f"0x{frame_id:X}",
            "send": _master_variable(master, send_var),
            "receive_mask": _master_variable(master, mask_var),
            "receive_check": _master_variable(master, check_var),
            "func_comm_frame_raw": raw.hex(),
            "comm_frame_raw": frame.hex(),
        })
    return rows


def cmd_active_test(args: argparse.Namespace) -> int:
    """Resolve one direct or routine P5 Active Test into its static wire plan."""
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = _english_strings(parser, db_root)
    category = _resolve_master_category(parser, master, strings, args.category)
    active_test_id = _parse_master_key(args.item)
    if active_test_id is None:
        raise SystemExit(f"invalid Active Test ID {args.item!r}; use decimal or 0x-prefixed hex")

    db = parser.parse_ecu_db(db_root / str(category["database"]))
    kinds = []
    if 68 in db.sections and db.sections[68].decoded_record_size == 64:
        size = db.sections[68].decoded_record_size
        if any(
            struct.unpack_from("<H", db.sections[68].decoded_data, index * size + 0x20)[0] == active_test_id
            for index in range(db.sections[68].header.record_count)
        ):
            kinds.append("direct")
    if 71 in db.sections and db.sections[71].decoded_record_size == 72:
        size = db.sections[71].decoded_record_size
        if any(
            struct.unpack_from("<H", db.sections[71].decoded_data, index * size + 0x1E)[0] == active_test_id
            for index in range(db.sections[71].header.record_count)
        ):
            kinds.append("routine")

    if args.kind is not None:
        if args.kind not in kinds:
            raise SystemExit(
                f"{category['database']}: Active Test 0x{active_test_id:X} is not a {args.kind} candidate"
            )
        kind = args.kind
    elif len(kinds) == 1:
        kind = kinds[0]
    elif not kinds:
        raise SystemExit(
            f"{category['database']}: Active Test 0x{active_test_id:X} was not found in current type-68/type-71 tables"
        )
    else:
        raise SystemExit(
            f"{category['database']}: Active Test 0x{active_test_id:X} exists as both {', '.join(kinds)}; use --kind"
        )

    if kind == "direct":
        _, _, selected = _direct_active_test_selected_row(
            parser, category, db_root, active_test_id, strings
        )
        selected_plan = _active_test_init_selected_plan(
            parser, master, category, db_root, active_test_id, strings
        )
        payload = {
            "category": category,
            "kind": kind,
            "selected_test": selected,
            "executor": selected_plan["executor"],
            "initial_transaction": selected_plan["initial_transaction"],
            "linked_monitor": selected_plan["linked_monitor"],
            "boundary": "read-only static planning; no Active Test request is sent",
        }
    else:
        _, _, selected = _routine_active_test_selected_row(
            parser, category, db_root, active_test_id, strings
        )
        payload = {
            "category": category,
            "kind": kind,
            "selected_test": selected,
            "executor": _routine_active_test_executor_plan(parser, master, category, selected),
            "boundary": "read-only static planning; no RoutineControl request is sent",
        }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    selected = payload["selected_test"]
    executor = payload["executor"]
    print(
        f"active-test\tcategory={category['category_id']}\t{category['name']}\tkind={kind}\t"
        f"id={selected['active_test_id_hex']}\tname={selected['name'] or '-'}"
    )
    if kind == "direct":
        length = executor["runtime_data_length"]
        print(
            f"wire\tservice={executor['service']}\tdid={executor['data_id_for_act']['did_hex']}\t"
            f"start={executor['start']['materialized_prefix']}+N\tstop={executor['stop']['materialized_prefix']}+N\t"
            f"runtime_length=N\tminimum={length['minimum_from_bit_geometry']}"
        )
        examples = executor.get("minimum_length_examples")
        if examples is not None:
            print(
                f"minimum-example\traw0={examples['raw_0']}\traw1={examples['raw_1']}\t"
                f"return={examples['return_control']}"
            )
    else:
        refs = selected
        if executor["fixed_request"]:
            print(
                f"wire\tservice={executor['service']}\trid={executor['routine_id_hex']}\t"
                f"start={executor['start']['materialized_static_request']}\t"
                f"stop={executor['stop']['materialized_static_request']}\t"
                f"result={executor['result']['materialized_static_request']}\tfixed=1"
            )
        else:
            print(
                f"wire\tservice={executor['service']}\trid={executor['routine_id_hex']}\t"
                f"start_static={executor['start']['materialized_static_request']}\t"
                f"stop_static={executor['stop']['materialized_static_request']}\t"
                f"result={executor['result']['materialized_static_request']}\tfixed=0\tdynamic=masked"
            )
        print(
            f"routine-vars\tstart=0x{refs['routine_command_variable']:X}\t"
            f"stop=0x{refs['routine_stop_command_variable']:X}\t"
            f"value_mask=0x{refs['output_mask_value_variable']:X}\t"
            f"button_mask=0x{refs['output_mask_button_variable']:X}\t"
            f"status_key=0x{refs['routine_status_key']:X}"
        )
    return 0


def cmd_command(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = _english_strings(parser, db_root)
    category = _resolve_master_category(parser, master, strings, args.category)
    role = _parse_master_key(args.role)
    if role is None:
        raise SystemExit(f"invalid role {args.role!r}; use decimal or 0x-prefixed hex")
    selected_item = _parse_master_key(args.item) if args.item is not None else None
    if args.item is not None and selected_item is None:
        raise SystemExit(f"invalid item {args.item!r}; use decimal or 0x-prefixed hex")
    try:
        payload = _master_command_plan(
            parser, master, category, role, gts / "bin", db_root, selected_item, strings
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(
        f"command	category={category['category_id']}	{category['name']}	role={payload['role_hex']}	"
        f"plugin={payload['plugin']}	surface={payload['operation_surface']}	semantics={payload['semantic_status']}"
    )
    for name, frame in payload["frames"].items():
        if frame is None:
            print(f"{name}	selector=missing")
            continue
        print(
            f"{name}	selector={frame['selector']}	send={frame['send']['bytes']}	"
            f"expect={frame['receive_check']['bytes']}	commset={frame['comm_set']}	"
            f"timeout={frame['comm_set_metadata']['receive_timeout']}	retries={frame['comm_set_metadata']['retry_count']}"
        )
    for timer in payload["timers"]:
        print(f"timer	id={timer['timer_id']}	delay_ms={timer['delay_ms']}")
    multi_active = payload["multi_active_test_init_model"]
    if multi_active is not None:
        category_plan = multi_active.get("category_plan")
        if category_plan is not None:
            print(
                f"multi-active-test-census\tgroups={category_plan['group_count']}\t"
                f"memberships={category_plan['membership_count']}\ttable={category_plan['group_table']}"
            )
        selected_plan = multi_active.get("selected_plan")
        if selected_plan is not None:
            group = selected_plan["group"]
            print(
                f"multi-active-test\tgroup={group['group_id_hex']}\tname={group['name'] or '-'}\t"
                f"members={group['member_count']}"
            )
            for member in selected_plan["members"]:
                selected = member["selected_test"]
                tx = member["initial_transaction"]
                send = tx.get("materialized_send", "-")
                print(
                    f"member\torder={member['sort_order']}\tid={selected['active_test_id_hex']}\t"
                    f"name={selected['name'] or '-'}\tdid=0x{selected['initial_read_did']:04X}\t"
                    f"bits={selected['bit_start']}..{selected['bit_end']}\tsend={send}"
                )
    active_test_monitor = payload["active_test_monitor_model"]
    if active_test_monitor is not None:
        category_plan = active_test_monitor.get("category_plan")
        if category_plan is None:
            print("active-test-monitors\tcategory_partition=unresolved")
        else:
            part = category_plan["candidate_partition"]
            print(
                f"active-test-monitors\ttable={category_plan['candidate_table']}\t"
                f"total={category_plan['candidate_count']}\tactive={category_plan['active_test_candidate_count']}\t"
                f"nonmember={category_plan['nonmember_count']}\t"
                f"direct={part['active_direct_include']}\t"
                f"runtime_active={part['active_runtime_check_support_pid']}\t"
                f"runtime_nonmember={part['nonmember_runtime_probe_then_filter']}\t"
                f"builder={category_plan['support_list_builder']}"
            )
    active_test_signal_info = payload["active_test_signal_info_model"]
    if active_test_signal_info is not None:
        selected_plan = active_test_signal_info.get("selected_plan")
        if selected_plan is None:
            print("active-test-signal-info\tselected_item=required")
        else:
            selected = selected_plan["selected_test"]
            pattern = selected_plan["active_test_pattern"]
            physical = selected_plan["physical"]
            display = selected_plan["display_info"]
            display_text = ",".join(f"{row['value']}={row['text'] or '-'}" for row in display) or "-"
            print(
                f"active-test-signal-info\tid={selected['active_test_id_hex']}\tname={selected['name'] or '-'}\t"
                f"pattern_key={pattern['key']}\tphysical_key={physical['key']}\t"
                f"conv={physical['mul']}/{physical['div']} offset={physical['offset']}\t"
                f"dec={physical['decimal_point_count']}\tsigned={int(physical['signed'])}\t"
                f"unit={physical['unit'] or '-'}"
            )
            print(
                f"active-test-display\tpattern={selected['pattern']}\tbutton_size={pattern['button_size']}\t"
                f"key_op={pattern['key_operation_pattern']}\tkey_invalid={pattern['key_invalid_flag']}\t"
                f"values={display_text}"
            )
    active_test_init = payload["active_test_init_model"]
    if active_test_init is not None:
        selected_plan = active_test_init.get("selected_plan")
        if selected_plan is None:
            print("active-test-init\tselected_item=required")
        else:
            selected = selected_plan["selected_test"]
            tx = selected_plan["initial_transaction"]
            linked = selected_plan["linked_monitor"]
            print(
                f"active-test-init\tid={selected['active_test_id_hex']}\tname={selected['name'] or '-'}\t"
                f"did=0x{selected['initial_read_did']:04X}\tbits={selected['bit_start']}..{selected['bit_end']}\t"
                f"init_mode={selected['initial_read_mode']}\tmonitor_link_mode={selected['monitor_link_mode']}"
            )
            if tx["performed"]:
                print(
                    f"initial-read\tselector={tx['selector']}\tsend={tx['materialized_send']}\t"
                    f"expect={tx['receive_check']}\tbits={tx['bit_start']}..{tx['bit_end']}"
                )
            monitor = linked.get("monitor")
            print(
                f"linked-monitor\tkey={linked['monitor_key']}\tresolution={linked['resolution']}\t"
                f"name={(monitor or {}).get('name') or '-'}"
            )
            executor = selected_plan["executor"]
            length = executor["runtime_data_length"]
            print(
                f"active-test-executor\tservice={executor['service']}\tdid={executor['data_id_for_act']['did_hex']}\t"
                f"encoding_mode={executor['data_id_for_act']['encoding_mode']}\t"
                f"start={executor['start']['materialized_prefix']}+N\tstop={executor['stop']['materialized_prefix']}+N\t"
                f"runtime_length=N\tminimum={length['minimum_from_bit_geometry']}"
            )
            examples = executor.get("minimum_length_examples")
            if examples is not None:
                print(
                    f"active-test-wire-minimum\traw0={examples['raw_0']}\traw1={examples['raw_1']}\t"
                    f"return={examples['return_control']}\tqualification={examples['qualification']}"
                )
    active_test_model = payload["active_test_model"]
    if active_test_model is not None:
        category_plan = active_test_model.get("category_plan")
        if category_plan is None:
            print("active-tests\tcategory_partition=unresolved")
        else:
            print(
                f"active-tests\tdirect={category_plan['direct_candidate_count']}\t"
                f"routine={category_plan['routine_candidate_count']}\t"
                f"multi_did={category_plan['multi_did_count']}\t"
                f"did_helper={category_plan['direct_support_helper']}\t"
                f"rid_helper={category_plan['routine_support_helper']}"
            )
    list_model = payload["list_model"]
    if list_model is not None:
        category_plan = list_model.get("category_plan")
        if category_plan is None:
            print("list\tcategory_partition=unresolved")
        else:
            part = category_plan["candidate_partition"]
            print(
                f"list\ttable={category_plan['candidate_table']}\tcandidates={category_plan['candidate_count']}\t"
                f"direct_include={part['direct_include']}\tdirect_exclude={part['direct_exclude']}\t"
                f"runtime_probe={part['runtime_check_support_pid']}\t"
                f"builder={category_plan['support_list_builder']}"
            )
    metadata = payload["metadata_model"]
    if metadata is not None:
        fields = metadata["conversion_fields"]
        print(
            f"metadata\tphysical=table{metadata['physical_data_table']}\tunit=table{metadata['unit_table']}\t"
            f"patterns=table{metadata['pattern_display_table']}\tfields={len(fields)}"
        )
    response = payload["response_model"]
    if response is not None:
        print(
            f"response	payload_offset={response['payload_offset']}	record_size={response['record_size']}	"
            f"names={response['entry_name_prefix']}1...	conversion=CP_ACP"
        )
    flow = payload["control_flow"]
    if flow is not None:
        print(
            f"flow	primary={flow['primary_selector']}	fallback={flow['fallback_selector']}	"
            f"fallback_errors={len(flow['fallback_error_codes_when_function_gate_set'])}"
        )
    return 0


def cmd_timer(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = _english_strings(parser, db_root)
    category = _resolve_master_category(parser, master, strings, args.category)
    rows = _master_timer_rows(parser, master, category["category_id"])
    if args.timer is not None:
        timer_id = _parse_master_key(args.timer)
        if timer_id is None:
            raise SystemExit(f"invalid timer {args.timer!r}; use decimal or 0x-prefixed hex")
        rows = [row for row in rows if row["timer_id"] == timer_id]
    if not rows:
        raise SystemExit(f"category {category['category_id']} has no matching timer rows")
    shown = rows[: args.limit]
    if args.json:
        print(json.dumps({"category": category, "timers": shown}, indent=2, sort_keys=True))
        return 0
    for row in shown:
        print(
            f"timer	category={row['category_id']}	id={row['timer_id']}	"
            f"delay_ms={row['delay_ms']}	unknown_08={row['unknown_dword_08']}"
        )
    return 0


def cmd_commset(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    rows = _master_comm_set_rows(parser, master)
    if args.comm_set is not None:
        comm_set_id = _parse_master_key(args.comm_set)
        if comm_set_id is None:
            raise SystemExit(f"invalid CommSet {args.comm_set!r}; use decimal or 0x-prefixed hex")
        rows = [row for row in rows if row["comm_set_id"] == comm_set_id]
        if not rows:
            raise SystemExit(f"no Toyota master CommSet {comm_set_id}")
    shown = rows[: args.limit]
    if args.json:
        print(json.dumps(shown, indent=2, sort_keys=True))
        return 0
    for row in shown:
        send_value = "FFFFFFFF" if row["send_parameter"] == 0xFFFFFFFF else str(row["send_parameter"])
        receive_value = "FFFFFFFF" if row["receive_timeout"] == 0xFFFFFFFF else str(row["receive_timeout"])
        print(
            f"commset\t{row['comm_set_id']}\tsend_parameter={send_value}\t"
            f"receive_timeout={receive_value}\tretries={row['retry_count']}\t"
            f"exception_id={row['exception_handler_id']}\texception_flag={row['exception_handler_flag']}\t"
            f"unknown_0c={row['unknown_word_0c']}"
        )
    return 0


def cmd_role(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    rows = _master_role_catalog(parser, master, gts / "bin")
    if args.role is not None:
        role = _parse_master_key(args.role)
        if role is None:
            raise SystemExit(f"invalid role {args.role!r}; use decimal or 0x-prefixed hex")
        rows = [row for row in rows if row["role"] == role]
        if not rows:
            raise SystemExit(f"no Toyota master DLL role 0x{role:X}")
    shown = rows[: args.limit]
    if args.json:
        print(json.dumps(shown, indent=2, sort_keys=True))
        return 0
    for row in shown:
        plugins = "; ".join(
            f"{item['dll']}({item['binding_count']})"
            for item in row["plugins"][: args.plugin_limit]
        )
        surface_counts = row.get("binding_surface_counts", {})
        surfaces = ",".join(f"{name}:{count}" for name, count in surface_counts.items())
        surface_text = f"\tsurfaces={surfaces}" if surfaces else ""
        print(
            f"role\t{row['role_hex']}\tbindings={row['binding_count']}\t"
            f"categories={row['category_count']}{surface_text}\t{plugins}"
        )
    return 0


def cmd_category(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = _english_strings(parser, db_root)
    category = _resolve_master_category(parser, master, strings, args.category)
    payload = {
        "category": category,
        "plugins": _master_plugins(parser, master, category["category_id"]),
        "functions": _master_functions(parser, master, strings, category["category_id"]),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(
        f"category\t{category['category_id']}\t{category['name']}\t"
        f"db={category['database']}\tshort={category['short_name']}\tgeneration={category['generation']}"
    )
    print("plugins")
    for row in payload["plugins"][: args.limit]:
        print(f"{row['role_hex']}\t{row['dll']}")
    print("functions")
    for row in payload["functions"][: args.limit]:
        print(f"{row['function_hex']}\t{row['name']}\t{row['description']}")
    return 0


def _master_canbus_topology_rows(parser: DDBParser, master: Any, strings: Any, query: str) -> list[dict[str, Any]]:
    """Resolve Toyota master CAN Bus Check topology for a vehicle type/name."""
    required = (55, 75, 76, 77, 78, 79)
    missing = [table_id for table_id in required if table_id not in master.sections]
    if missing:
        raise SystemExit(f"master database lacks CAN Bus Check tables: {missing}")

    vehicle_names = {
        struct.unpack_from("<I", raw, 4)[0]: strings.get_string(struct.unpack_from("<I", raw, 0)[0])
        for raw in ddb_records(master.sections[43])
    }
    try:
        vehicle_type = int(query, 0)
    except ValueError:
        vehicle_type = None
    if vehicle_type is not None:
        matches = [vehicle_type] if vehicle_type in vehicle_names else []
    else:
        matches = sorted(
            vehicle_type for vehicle_type, name in vehicle_names.items()
            if name and query.casefold() in name.casefold()
        )
    if not matches:
        raise SystemExit(f"no Toyota master vehicle type/name matches {query!r}")

    car_rows = list(ddb_records(master.sections[75]))
    option_rows = list(ddb_records(master.sections[77]))
    component_rows = list(ddb_records(master.sections[78]))
    subbus_names = {
        struct.unpack_from("<I", raw, 0)[0]: strings.get_string(struct.unpack_from("<I", raw, 4)[0])
        for raw in ddb_records(master.sections[76])
    }
    bus_names = {
        struct.unpack_from("<I", raw, 8)[0]: strings.get_string(struct.unpack_from("<I", raw, 4)[0])
        for raw in ddb_records(master.sections[79])
    }
    gateway_names: dict[int, set[str]] = {}
    for raw in ddb_records(master.sections[55]):
        bus_index = struct.unpack_from("<H", raw, 8)[0]
        gateway_names.setdefault(bus_index, set()).add(strings.get_string(struct.unpack_from("<I", raw, 4)[0]))

    out = []
    for vehicle_type in matches:
        vehicle_car_rows = [raw for raw in car_rows if struct.unpack_from("<I", raw, 4)[0] == vehicle_type]
        for car_raw in vehicle_car_rows:
            car_id = struct.unpack_from("<I", car_raw, 0)[0]
            options = [raw for raw in option_rows if struct.unpack_from("<I", raw, 0)[0] == car_id]
            placement_variants: dict[tuple, dict[str, Any]] = {}
            for option in options:
                group = struct.unpack_from("<I", option, 44)[0]
                rows = [raw for raw in component_rows if struct.unpack_from("<I", raw, 0)[0] == group]
                placements = []
                shape = []
                for raw in sorted(rows, key=lambda item: (struct.unpack_from("<H", item, 8)[0], item[14])):
                    bus_index = struct.unpack_from("<H", raw, 8)[0]
                    component_index = raw[14]
                    domain = subbus_names.get(component_index + 1, "")
                    row = {
                        "component_index": component_index,
                        "component_hex": f"0x{component_index:02X}",
                        "ecu_domain": domain,
                        "bus_index": bus_index,
                        "bus_name": bus_names.get(bus_index, f"BusIndex {bus_index}"),
                        "gateway_names": sorted(x for x in gateway_names.get(bus_index, set()) if x),
                        "junction_name": strings.get_string(struct.unpack_from("<I", raw, 4)[0]),
                    }
                    placements.append(row)
                    shape.append((component_index, domain, bus_index, row["bus_name"]))
                shape_key = tuple(shape)
                existing = placement_variants.get(shape_key)
                if existing is None:
                    placement_variants[shape_key] = {
                        "component_groups": [f"0x{group:08X}"],
                        "placements": placements,
                    }
                else:
                    existing["component_groups"].append(f"0x{group:08X}")
            out.append({
                "vehicle_type": vehicle_type,
                "vehicle_name": vehicle_names[vehicle_type],
                "can_bus_car_id": f"0x{car_id:08X}",
                "option_count": len(options),
                "placement_variant_count": len(placement_variants),
                "placement_variants": list(placement_variants.values()),
            })
    if not out:
        raise SystemExit(f"vehicle match {query!r} has no CAN Bus Check topology row")
    return out


def cmd_canbus(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    parser = DDBParser()
    strings = _english_strings(parser, db_root)
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    rows = _master_canbus_topology_rows(parser, master, strings, args.vehicle)
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    for index, row in enumerate(rows):
        if index:
            print()
        print(
            f"vehicle={row['vehicle_type']} name={row['vehicle_name']} "
            f"can_bus_car_id={row['can_bus_car_id']} options={row['option_count']} "
            f"placement_variants={row['placement_variant_count']}"
        )
        for variant_index, variant in enumerate(row["placement_variants"], 1):
            if row["placement_variant_count"] > 1:
                print(f"  variant {variant_index}: groups={','.join(variant['component_groups'])}")
            by_bus: dict[tuple[int, str, tuple[str, ...]], list[dict[str, Any]]] = {}
            for placement in variant["placements"]:
                key = (
                    placement["bus_index"],
                    placement["bus_name"],
                    tuple(placement["gateway_names"]),
                )
                by_bus.setdefault(key, []).append(placement)
            for (bus_index, bus_name, gateways), placements in sorted(by_bus.items()):
                gateway = ", ".join(gateways) if gateways else "-"
                print(f"  {bus_name} index={bus_index} gateway={gateway}")
                for placement in placements:
                    junction = placement["junction_name"]
                    suffix = f" via {junction}" if junction and junction != "-" else ""
                    print(f"    {placement['component_hex']} {placement['ecu_domain']}{suffix}")
    return 0


def cmd_frame(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    db_root = _db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = _english_strings(parser, db_root)
    category = _resolve_master_category(parser, master, strings, args.category)
    selector = _parse_master_key(args.selector) if args.selector is not None else None
    if args.selector is not None and selector is None:
        raise SystemExit(f"invalid selector {args.selector!r}; use decimal or 0x-prefixed hex")
    rows = _master_frame_rows(parser, master, category["category_id"], selector)
    if selector is not None and not rows:
        raise SystemExit(f"category {category['category_id']} has no selector 0x{selector:X}")
    _print_rows(rows, as_json=args.json, limit=args.limit)
    return 0


def _cuw_files(corpus: Path) -> list[Path]:
    return sorted(corpus.glob("*.cuw"), key=lambda p: p.name.casefold()) if corpus.is_dir() else []


def _resolve_cuw(corpus: Path, query: str) -> Path | None:
    direct = Path(query)
    if direct.is_file():
        return direct.resolve()
    exact = [p for p in _cuw_files(corpus) if p.name.casefold() == query.casefold() or p.stem.casefold() == query.casefold()]
    return exact[0] if len(exact) == 1 else None


def _cuw_descriptor(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    """Fully validate a CUW before returning its first attach descriptor."""
    raw = path.read_bytes()
    outer = parse_cuw_container(raw)
    if outer["errors"]:
        raise ValueError("; ".join(outer["errors"]))
    outer["validation"] = "full-container"
    payload = first_member_payload(raw, outer)
    descriptor = parse_attach_bytes(payload)
    return outer, descriptor


def _cuw_first_member_fast(path: Path) -> tuple[dict[str, Any], bytes]:
    return read_first_member(path)

def _cuw_descriptor_fast(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    """Read only the CUW header + first attach member for interactive lookup.

    Large format-0x67 CUWs can be hundreds of MiB while attach.att is only a
    few KiB. Discovery should not stream/hash the flash payload merely to learn
    vehicle, contact type, DiagID, or calibration IDs. Use ``--validate`` when
    the full container integrity gate is desired.
    """
    outer, payload = _cuw_first_member_fast(path)
    return outer, parse_attach_bytes(payload)


def _new_cids(descriptor: dict[str, dict[str, str]]) -> list[str]:
    values = []
    for section, fields in descriptor.items():
        if section.startswith(("Node", "CPU", "LogicalBlock")) and fields.get("NewCID"):
            values.append(fields["NewCID"])
    return sorted(set(values))


def _target_calibrations(descriptor: dict[str, dict[str, str]]) -> list[str]:
    values = []
    for section, fields in descriptor.items():
        if not section.startswith("LogicalBlock"):
            continue
        values.extend(value for key, value in fields.items() if key.endswith("_TargetCalibration") and value)
    return sorted(set(values))


def _node_summary(descriptor: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for section, fields in descriptor.items():
        if not section.startswith("Node"):
            continue
        rows.append({
            "section": section,
            "diag_id": fields.get("DiagID", ""),
            "required_spec_repro_ver": fields.get("RequiredSpecReproVer", ""),
            "logical_blocks": fields.get("NumberOfLogicalBlock", ""),
        })
    return rows


def _search_cuw_corpus(query: str, corpus: Path) -> list[dict[str, Any]]:
    out = []
    needle = query.casefold()
    for path in _cuw_files(corpus):
        try:
            _, payload = _cuw_first_member_fast(path)
        except (ValueError, KeyError, struct.error):
            continue
        # Prefilter on the raw ANSI attach text. Parsing every descriptor is
        # disproportionately expensive compared with reading their few KiB.
        if needle not in path.name.casefold() and needle not in payload.decode("latin1").casefold():
            continue
        descriptor = parse_attach_bytes(payload)
        vehicle = descriptor.get("Vehicle", {})
        out.append({
            "kind": "cuw",
            "source": path.name,
            "vehicle": vehicle.get("VehicleName", ""),
            "contact_type": vehicle.get("ContactType", ""),
            "new_cids": ",".join(_new_cids(descriptor)),
        })
    return out


def cmd_cuw(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    cuwplus = _resolve_cuwplus_root(gts, args.cuwplus_root)
    corpus = _resolve_cuw_corpus(args.cuw_root)
    if args.query == "list":
        rows = [{"kind": "cuw", "source": p.name, "vehicle": "", "contact_type": "", "new_cids": ""} for p in _cuw_files(corpus)]
        _print_rows(rows, as_json=args.json, limit=args.limit)
        return 0
    path = _resolve_cuw(corpus, args.query)
    if path is None:
        rows = _search_cuw_corpus(args.query, corpus)
        _print_rows(rows, as_json=args.json, limit=args.limit)
        return 0
    outer, descriptor = _cuw_descriptor(path) if args.validate else _cuw_descriptor_fast(path)
    vehicle = descriptor.get("Vehicle", {})
    contact = vehicle.get("ContactType", "")
    routes = [row for row in _route_rows(cuwplus) if row.get("contact_type", "").casefold() == contact.casefold()]
    payload = {
        "path": str(path),
        "outer": {key: outer.get(key) for key in ("format_type", "file_size", "name", "payload_length", "format67_member_count", "format4_archive_count", "validation")},
        "vehicle": vehicle,
        "new_cids": _new_cids(descriptor),
        "target_calibrations": _target_calibrations(descriptor),
        "nodes": _node_summary(descriptor),
        "sections": descriptor,
        "gtsplus_routes": routes,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(path)
    print(f"format\t0x{outer['format_type']:02X}\tfirst_member={outer.get('name')}\tpayload={outer.get('payload_length')}\tvalidation={outer.get('validation')}")
    for key in ("VehicleName", "ModelYear", "ContactType", "KindOfECU", "RequiredSpecReproVer", "ReproMethod"):
        if vehicle.get(key):
            print(f"vehicle.{key}\t{vehicle[key]}")
    for node in payload["nodes"]:
        print(
            f"{node['section']}\tdiag_id={node['diag_id']}\t"
            f"required_spec={node['required_spec_repro_ver']}\tlogical_blocks={node['logical_blocks']}"
        )
    if payload["new_cids"]:
        print("new_cids\t" + ", ".join(payload["new_cids"]))
    if payload["target_calibrations"]:
        print("target_calibrations\t" + ", ".join(payload["target_calibrations"]))
    if routes:
        print("gtsplus_route")
        for route in routes:
            print(_format_row(route))
    else:
        print(f"gtsplus_route\t(no current route row for {contact!r})")
    if args.verbose:
        for section, fields in descriptor.items():
            print(f"[{section}]")
            for key, value in fields.items():
                print(f"{key}={value}")
    return 0


def _resolve_pe(gts_root: Path, cuwplus_root: Path, query: str) -> Path:
    direct = Path(query)
    if direct.is_file():
        return direct.resolve()
    candidates = list(_iter_pe_candidates(gts_root, cuwplus_root))
    exact = [p for p in candidates if p.name.casefold() == query.casefold()]
    if len(exact) == 1:
        return exact[0]
    matches = [p for p in candidates if query.casefold() in p.name.casefold()]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"no GTS+/CUWPlus PE matches {query!r}")
    raise SystemExit("ambiguous PE; matches:\n" + "\n".join(f"  {p}" for p in matches[:60]))


def _binary_strings(data: bytes, minimum: int = 5) -> list[str]:
    return pe_binary_strings(data, minimum)


def cmd_pe(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    cuwplus = _resolve_cuwplus_root(gts, args.cuwplus_root)
    path = _resolve_pe(gts, cuwplus, args.binary)
    data = path.read_bytes()
    try:
        pe = pefile.PE(data=data, fast_load=False)
    except pefile.PEFormatError as exc:
        raise SystemExit(f"not a parseable PE: {path}: {exc}") from exc
    exports = pe_exports(pe)
    imports = pe_imports(pe)
    strings = _binary_strings(data, args.min_string)
    if args.query:
        exports = [e for e in exports if _fold_match(args.query, e["name"])]
        imports = [i for i in imports if _fold_match(args.query, i["dll"], i["name"])]
        strings = [s for s in strings if _fold_match(args.query, s)]
    exports = exports[: args.limit]
    imports = imports[: args.limit]
    strings = strings[: args.limit]
    payload = {
        "path": str(path),
        "image_base": pe.OPTIONAL_HEADER.ImageBase,
        "machine": f"0x{pe.FILE_HEADER.Machine:04X}",
        "exports": exports,
        "imports": imports,
        "strings": strings,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(path)
    print(f"image_base\t0x{payload['image_base']:X}\tmachine={payload['machine']}\tsize={len(data)}")
    if exports:
        print("exports")
        for item in exports[: args.limit]:
            print(f"0x{item['rva']:08X}\t{item['name']}")
    if imports:
        print("imports")
        for item in imports[: args.limit]:
            print(f"{item['dll']}!{item['name']}")
    if strings:
        print("strings")
        for value in strings:
            print(value)
    return 0


def cmd_recover_bodies(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    manifest = recover_gtsplus_bodies(
        archive=args.archive,
        output=args.output,
        installed_root=gts,
        keep_workspace=args.keep_workspace,
    )
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        count = manifest["recovered_plaintext_body_count"]
        installed = manifest["installed_protected_body_count"]
        print(f"GTS+ {manifest['gtsplus_version']}: recovered {count}/{installed} protected PE bodies")
        print(f"output\t{manifest['output_root']}")
        print(f"manifest\t{Path(manifest['output_root']) / 'manifest.json'}")
    return 0


CAMRY_2026_DIAG_PROFILE = {
    "profile": "camry-2026-f33",
    "vehicle": "2026 Toyota Camry Hybrid",
    "panda_bus": 0,
    "fault_status_mask": 0xAF,
    "identity_guard": {
        "ecu": "eps",
        "did": 0xF181,
        "contains_ascii": "8965F3307000",
    },
    "ecus": [
        {"key": "engine", "name": "Engine", "address": 0x700, "category_id": 372, "functional_response": 0x7E8},
        {"key": "ect", "name": "ECT", "address": 0x701},
        {"key": "motor_generator", "name": "Motor Generator", "address": 0x724, "category_id": 395, "functional_response": 0x7EE},
        {"key": "hybrid", "name": "Hybrid Control", "address": 0x7D2, "category_id": 397, "functional_response": 0x7EA},
        {"key": "hv_battery", "name": "HV Battery", "address": 0x747, "category_id": 398, "functional_response": 0x7EB},
        {"key": "plug_in", "name": "Plug-in Control", "address": 0x745},
        {"key": "ecu_707", "name": "ECU 0x707", "address": 0x707},
        {"key": "ecu_703", "name": "ECU 0x703", "address": 0x703},
        {"key": "eps", "name": "Power Steering", "address": 0x7A1, "category_id": 405},
        {"key": "brake", "name": "Brake/EPB", "address": 0x7B0, "category_id": 435, "functional_response": 0x7ED},
        {"key": "ecu_750", "name": "ECU 0x750", "address": 0x750},
        {"key": "ecu_7b3", "name": "ECU 0x7B3", "address": 0x7B3},
        {"key": "air_conditioner", "name": "Air Conditioner", "address": 0x7C4, "category_id": 450},
        {"key": "ecu_7d1", "name": "ECU 0x7D1", "address": 0x7D1},
        {"key": "ecu_7d0", "name": "ECU 0x7D0", "address": 0x7D0},
        {"key": "frc", "name": "Front Recognition Camera", "address": 0x792, "category_id": 498},
        {"key": "ecu_7a2", "name": "ECU 0x7A2", "address": 0x7A2},
    ],
}


def _registry_signal_row(row: dict[str, Any]) -> dict[str, Any]:
    info = row.get("signal_info") or {}
    return {
        "decoder": "p5-linear-msb0-v1",
        "monitor_key": row.get("monitor_key"),
        "alternate_did": row.get("alternate_did"),
        "name": row.get("name") or "",
        "bit_start": row.get("bit_start"),
        "bit_end": row.get("bit_end"),
        "mul": info.get("mul", 1),
        "div": info.get("div", 1),
        "offset": info.get("offset", 0),
        "decimal_point_count": info.get("decimal_point_count", 0),
        "signed": bool(info.get("signed", False)),
        "unit": info.get("unit"),
        "data_range": info.get("data_range"),
        "graph_range": info.get("graph_range"),
        "patterns": {str(key): value for key, value in (info.get("pattern_display") or {}).items()},
    }


def _registry_did_catalog(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        did = int(row["primary_did"])
        grouped.setdefault(f"0x{did:04X}", []).append(_registry_signal_row(row))
    return grouped


def _registry_eps_observed_identity(capture: dict[str, Any]) -> dict[str, Any]:
    route = capture["route"]
    if int(route["eps_tx"], 16) != 0x7A1:
        raise ValueError("Camry EPS identity TX drift")
    if route["eps_bus"] != 1 or route["elm327_param"] != 1:
        raise ValueError("Camry EPS pre-repin route drift")
    rows = {row["name"]: row for row in capture["identity"]}
    f181 = bytes.fromhex(rows["app_sw_id"]["hex"])
    if not f181 or f181[0] != 2 or len(f181) != 33:
        raise ValueError("Camry EPS F181 two-ID layout drift")
    software_ids = [f181[1 + 16 * index : 1 + 16 * (index + 1)].rstrip(b"\0").decode("ascii") for index in range(2)]
    serial = bytes.fromhex(rows["ecu_serial"]["hex"]).rstrip(b"\0").decode("ascii")
    return {
        "observation": "2026-08-26 pre-repin normal-harness NRTD",
        "panda_bus_at_observation": 1,
        "elm327_param": 1,
        "f181_software_ids": software_ids,
        "f18c_serial": serial,
        "route_note": "historical pre-repin Panda bus; current profile diagnostic route is post-repin Panda bus0",
    }


def _registry_nrtd_observed_identities(nrtd: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modules = nrtd["module_identity"]
    if modules["elm327_param"] != 1:
        raise ValueError("Camry NRTD module identity ELM327 param drift")
    out: dict[str, dict[str, Any]] = {}
    for key, source_key in (("frc", "FRC_P5"), ("brake", "Brake_EPB_category_435")):
        row = modules[source_key]
        if row["bus"] != 1:
            raise ValueError(f"{source_key} pre-repin observation bus drift")
        out[key] = {
            "observation": "2026-08-26 pre-repin NRTD",
            "panda_bus_at_observation": 1,
            "elm327_param": 1,
            "f181_software_ids": [row["f181"]],
            "f18c_serial": row["f18c_serial"],
            "ecu_part_0105": row["ecu_part_0105"],
            "route_note": "historical pre-repin Panda bus; current profile diagnostic route is post-repin Panda bus0",
        }
    return out


def _registry_dtc_catalog(parser: DDBParser, db: Any, strings: StringDataBase, source: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in _dtc_rows(parser, db, strings, source):
        packed = str(row.get("packed_dtc") or "").removeprefix("0x").upper()
        if not packed:
            continue
        grouped.setdefault(packed, []).append({
            "code": row.get("code") or "",
            "description": row.get("description") or "",
            "failure": row.get("failure") or "",
        })
    return grouped


def _compact_direct_active_test(
    selected: dict[str, Any],
    executor: dict[str, Any],
    monitor_rows: list[dict[str, Any]],
    init_frame: dict[str, Any] | None = None,
) -> dict[str, Any]:
    linked = [
        row for row in monitor_rows
        if row.get("primary_did") == selected["initial_read_did"]
        and row.get("bit_start") == selected["bit_start"]
        and row.get("bit_end") == selected["bit_end"]
    ]
    monitor = linked[0] if len(linked) == 1 else {}
    return {
        "id": selected["active_test_id"],
        "name": selected.get("name") or "",
        "kind": "direct",
        "service": 0x2F,
        "positive_response": 0x6F,
        "did": executor["data_id_for_act"]["did"],
        "encoding_mode": executor["data_id_for_act"]["encoding_mode"],
        "bit_start": executor["bit_range"]["start"],
        "bit_end": executor["bit_range"]["end"],
        "start_prefix": executor["start"]["materialized_prefix"],
        "stop_prefix": executor["stop"]["materialized_prefix"],
        "runtime_length_minimum": executor["runtime_data_length"]["minimum_from_bit_geometry"],
        "minimum_examples": executor.get("minimum_length_examples"),
        "initial_read": _direct_initial_read_plan(selected, init_frame),
        "monitor_key": monitor.get("monitor_key"),
        "monitor_name": monitor.get("name") or "",
        "session_requirement": _session_requirement(executor["start"]["materialized_prefix"]),
        "execution": "plan_only",
    }


def _direct_initial_read_plan(selected: dict[str, Any], init_frame: dict[str, Any] | None) -> dict[str, Any]:
    """Compact role-0x08 selector-0xCA initial-read request for one direct test."""
    plan: dict[str, Any] = {"mode": selected["initial_read_mode"]}
    if selected["initial_read_mode"] != 0 or init_frame is None:
        return plan
    did = int(selected["initial_read_did"])
    request = bytearray.fromhex(init_frame["send"]["bytes"])
    if len(request) < 3 or request[0] != 0x22:
        raise ValueError("selector 0xCA base request is no longer 22xxxx")
    request[1] = (did >> 8) & 0xFF
    request[2] = did & 0xFF
    plan.update({
        "selector": "0xCA",
        "request": request.hex(),
        "check": init_frame["receive_check"]["bytes"],
    })
    return plan


def _compact_routine_active_test(selected: dict[str, Any], executor: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": selected["active_test_id"],
        "name": selected.get("name") or "",
        "kind": "routine",
        "service": 0x31,
        "positive_response": 0x71,
        "routine_id": selected["routine_id"],
        "start_static": executor["start"]["materialized_static_request"],
        "stop_static": executor["stop"]["materialized_static_request"],
        "result_static": executor["result"]["materialized_static_request"],
        "fixed_request": executor["fixed_request"],
        "routine_command_variable": selected["routine_command_variable"],
        "routine_stop_command_variable": selected["routine_stop_command_variable"],
        "output_mask_value_variable": selected["output_mask_value_variable"],
        "output_mask_button_variable": selected["output_mask_button_variable"],
        "routine_status_key": selected["routine_status_key"],
        "session_requirement": _session_requirement(executor["start"]["materialized_static_request"]),
        "execution": "executable" if executor["fixed_request"] else "plan_only",
    }


def _registry_active_tests(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    db_root: Path,
    strings: StringDataBase,
    monitor_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    db_path = db_root / str(category["database"])
    db = parser.parse_ecu_db(db_path)
    init_frames = _master_frame_rows(parser, master, int(category["category_id"]), 0xCA)
    init_frame = init_frames[0] if len(init_frames) == 1 else None
    rows: list[dict[str, Any]] = []
    direct = db.sections.get(68)
    if direct is not None:
        if direct.decoded_record_size != 64:
            raise ValueError(f"{db_path.name}: type-68 record size {direct.decoded_record_size}, expected 64")
        direct_ids = [
            struct.unpack_from("<H", direct.decoded_data, index * 64 + 0x20)[0]
            for index in range(direct.header.record_count)
        ]
        direct_counts = {value: direct_ids.count(value) for value in set(direct_ids)}
        for index, active_test_id in enumerate(direct_ids):
            raw = direct.decoded_data[index * 64 : (index + 1) * 64]
            name_index = struct.unpack_from("<I", raw, 0x0C)[0]
            name = strings.get_string(name_index) or ""
            if direct_counts[active_test_id] != 1:
                rows.append({
                    "id": active_test_id,
                    "record": index,
                    "name": name,
                    "kind": "direct",
                    "execution": "unresolved_static_plan",
                    "error": f"duplicate direct Active Test ID resolves {direct_counts[active_test_id]} rows",
                })
                continue
            try:
                db_obj, selected_db_path, selected = _direct_active_test_selected_row(
                    parser, category, db_root, active_test_id, strings
                )
                executor = _direct_active_test_executor_plan(
                    parser, master, category, db_obj, selected_db_path, selected
                )
                rows.append(_compact_direct_active_test(selected, executor, monitor_rows, init_frame))
            except ValueError as exc:
                rows.append({
                    "id": active_test_id,
                    "record": index,
                    "name": name,
                    "kind": "direct",
                    "execution": "unresolved_static_plan",
                    "error": str(exc),
                })
    routine = db.sections.get(71)
    if routine is not None:
        if routine.decoded_record_size != 72:
            raise ValueError(f"{db_path.name}: type-71 record size {routine.decoded_record_size}, expected 72")
        routine_ids = [
            struct.unpack_from("<H", routine.decoded_data, index * 72 + 0x1E)[0]
            for index in range(routine.header.record_count)
        ]
        routine_counts = {value: routine_ids.count(value) for value in set(routine_ids)}
        for index, active_test_id in enumerate(routine_ids):
            raw = routine.decoded_data[index * 72 : (index + 1) * 72]
            name_index = struct.unpack_from("<I", raw, 0x08)[0]
            name = strings.get_string(name_index) or ""
            routine_id = struct.unpack_from("<H", raw, 0x1C)[0]
            if routine_counts[active_test_id] != 1:
                rows.append({
                    "id": active_test_id,
                    "record": index,
                    "name": name,
                    "kind": "routine",
                    "routine_id": routine_id,
                    "execution": "unresolved_static_plan",
                    "error": f"duplicate routine Active Test ID resolves {routine_counts[active_test_id]} rows",
                })
                continue
            _, _, selected = _routine_active_test_selected_row(parser, category, db_root, active_test_id, strings)
            try:
                executor = _routine_active_test_executor_plan(parser, master, category, selected)
                rows.append(_compact_routine_active_test(selected, executor))
            except ValueError as exc:
                rows.append({
                    "id": active_test_id,
                    "record": index,
                    "name": name,
                    "kind": "routine",
                    "routine_id": routine_id,
                    "execution": "unresolved_static_plan",
                    "error": str(exc),
                })
    return sorted(rows, key=lambda row: (int(row["id"]), row["kind"]))


def _registry_source_key(path: Path, gts_root: Path) -> str:
    """Return a checkout-independent logical identity for a registry source."""
    resolved = path.resolve()
    normalized_gts = gts_root.resolve()
    normalized_repo = ROOT.resolve()
    if resolved.is_relative_to(normalized_gts):
        return f"gtsplus/{resolved.relative_to(normalized_gts).as_posix()}"
    if resolved.is_relative_to(normalized_repo):
        return resolved.relative_to(normalized_repo).as_posix()
    raise ValueError(f"registry source is outside the repository/GTS+ roots: {resolved}")


REGISTRY_FUNCTION_NAME_BOUNDARY = (
    "current master type-26/type-27 rows for the Camry P5 categories carry string index 0: "
    "function/detail keys, ordering, and membership are recovered, OEM function names are not"
)

# Recovered semantic kinds for the generic (category-0) command-plugin families
# the runtime utility surface needs.  The six lifecycle wrappers are cross-checked
# at build time against the pinned execution model; the four routine Active-Test
# wrappers are the recovered shared P5 routine executors (TMS-073).  Every other
# generic role stays opaque and is not classified here.
GENERIC_UTILITY_ROLE_KINDS = {
    0x3A: "test_present_start",
    0x3B: "test_present_stop",
    0x61: "check_mode_frame_get",
    0x62: "check_mode_frame_confirm",
    0xB0: "active_test_start",
    0xAE: "routine_active_test_init",
    0xAF: "routine_active_test_signal_info",
    0xBF: "set_default_session",
    0xCA: "move_session_cgwd",
    0xD4: "single_routine_active_test",
}

_SEMANTIC_KIND_PATTERN = re.compile(r"^role_0x[0-9A-Fa-f]+_(?P<kind>.+)$")


def _semantic_kind_for_profile(profile_name: str | None) -> str | None:
    if profile_name is None:
        return None
    match = _SEMANTIC_KIND_PATTERN.match(profile_name)
    return match.group("kind") if match else None


def _registry_role_bindings(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    bin_root: Path,
) -> list[dict[str, Any]]:
    """Category plugin bindings; semantic kind only where the exact plugin identity is recovered."""
    category_id = int(category["category_id"])
    bindings = []
    for entry in sorted(
        (row for row in parser.extract_master_dlls(master.sections[19]) if row.category_id == category_id),
        key=lambda row: (row.dll_role_id, row.dll_name.casefold()),
    ):
        profile_name, _, status = _semantic_profile_for_plugin(bin_root / entry.dll_name, entry.dll_role_id)
        bindings.append({
            "role": entry.dll_role_id,
            "dll": entry.dll_name,
            "semantic_kind": _semantic_kind_for_profile(profile_name),
            "semantic_status": status,
        })
    return bindings


def _registry_selector_rows(parser: DDBParser, master: Any, category_id: int) -> list[dict[str, Any]]:
    """Every resolved (selector -> CommSet/CommFrame/send/mask/check) row for one category."""
    rows = _master_frame_rows(parser, master, category_id)
    return [
        {
            "selector": row["selector"],
            "frame": row["comm_frame_id"],
            "comm_set": row["comm_set"],
            "send": row["send"]["bytes"],
            "mask": row["receive_mask"]["bytes"],
            "check": row["receive_check"]["bytes"],
        }
        for row in sorted(rows, key=lambda row: (int(row["selector"], 16), row["comm_frame_id"]))
    ]


def _registry_function_hierarchy(
    parser: DDBParser,
    master: Any,
    strings: StringDataBase,
    category_id: int,
) -> list[dict[str, Any]]:
    """Master type-26 function rows joined with type-27 detail keys per category."""
    detail_ids: dict[int, list[int]] = {}
    for entry in parser.extract_master_function_details(master.sections[27]):
        if entry.category_id == category_id:
            detail_ids.setdefault(entry.function_id, []).append(entry.detail_id)
    return [
        {
            "function_id": entry.function_id,
            "sort_key": entry.sort_key,
            "name": strings.get_string(entry.name_string_index),
            "description": strings.get_string(entry.description_string_index),
            "detail_ids": sorted(detail_ids.get(entry.function_id, [])),
        }
        for entry in sorted(
            (row for row in parser.extract_master_functions(master.sections[26]) if row.category_id == category_id),
            key=lambda row: (row.sort_key, row.function_id),
        )
    ]


def _registry_data_list(db: Any, strings: StringDataBase) -> dict[str, Any]:
    """Data List display order from the consumer-pinned monitor sort key."""
    records: list[Any] = []
    for table in (62, 157):
        section = db.sections.get(table)
        if section is not None:
            records.extend(extract_monitor_records(section))
    def identity(record: Any) -> tuple[Any, ...]:
        return (
            strings.get_string(record.name_string_index),
            record.primary_did,
            record.alternate_did,
            record.bit_start,
            record.bit_end,
        )

    by_identity: dict[tuple[Any, ...], Any] = {}
    for record in sorted(records, key=lambda record: (record.sort_key, record.table, record.index)):
        by_identity.setdefault(identity(record), record)
    ordered = sorted(by_identity.values(), key=lambda record: (record.sort_key, record.table, record.index))
    return {
        "tables": sorted({record.table for record in records}),
        "record_counts": {
            str(table): sum(1 for record in records if record.table == table)
            for table in sorted({record.table for record in records})
        },
        "row_count": len(ordered),
        "display_order": (
            "type-62/157 sort key (u16 record +0x30, +0x10 on 80-byte rows), then table/record; "
            "rows deduplicated by (name, did, alternate did, bit range), lowest ordering wins"
        ),
        "rows": [
            {
                "monitor_key": record.monitor_key,
                "sort_key": record.sort_key,
                "did": f"0x{record.primary_did:04X}",
                "bit_start": record.bit_start,
                "bit_end": record.bit_end,
                "name": strings.get_string(record.name_string_index) or "",
            }
            for record in ordered
        ],
    }


def _registry_active_test_groups(parser: DDBParser, category: dict[str, Any], db_root: Path) -> dict[str, Any]:
    """Compact type-33 multi-control Active-Test group geometry."""
    plan = _multi_active_test_category_plan(parser, category, db_root)
    return {
        "group_count": plan["group_count"],
        "membership_count": plan["membership_count"],
        "groups": [
            {
                "group_id": group["group_id"],
                "members": [member["member_active_test_id"] for member in group["members"]],
            }
            for group in plan["groups"]
        ],
        "boundary": (
            "type-33 rows are static multi-control expansion; each member still follows its type-68 "
            "initialization path via role 0x63"
            if plan["group_count"]
            else "category has no type-33 multi-control membership rows"
        ),
    }


def _registry_request_row(
    parser: DDBParser,
    master: Any,
    category_id: int,
    selector: int,
    name: str,
) -> dict[str, Any]:
    matches = _master_frame_rows(parser, master, category_id, selector)
    if len(matches) != 1:
        return {"name": name, "selector": f"0x{selector:X}", "resolved": False}
    row = matches[0]
    comm_set = row["comm_set_metadata"]
    return {
        "name": name,
        "selector": row["selector"],
        "send": row["send"]["bytes"],
        "mask": row["receive_mask"]["bytes"],
        "check": row["receive_check"]["bytes"],
        "comm_set": row["comm_set"],
        "receive_timeout": comm_set["receive_timeout"],
        "retry_count": comm_set["retry_count"],
        "session_requirement": _session_requirement(row["send"]["bytes"]),
        "resolved": True,
    }


def _registry_command_rows(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    bin_root: Path,
    bindings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Wire-request command plans for roles whose exact plugin semantics are recovered."""
    category_id = int(category["category_id"])
    rows: list[dict[str, Any]] = []
    for binding in bindings:
        kind = binding["semantic_kind"]
        if kind is None:
            continue
        _, profile, _ = _semantic_profile_for_plugin(bin_root / binding["dll"], binding["role"])
        if kind == "dtc_clear":
            control_flow = profile["control_flow"]
            timers = [row for row in _master_timer_rows(parser, master, category_id) if row["timer_id"] == 1]
            rows.append({
                "role": binding["role"],
                "kind": kind,
                "requests": [
                    _registry_request_row(parser, master, category_id, 0x1, "primary"),
                    _registry_request_row(parser, master, category_id, 0x102, "fallback"),
                ],
                "timer": {"timer_id": 1, "delay_ms": timers[0]["delay_ms"]} if len(timers) == 1 else None,
                "flow": {
                    "primary_selector": control_flow["primary_selector"],
                    "fallback_selector": control_flow["fallback_selector"],
                    "fallback_error_codes_when_function_gate_set": control_flow["fallback_error_codes_when_function_gate_set"],
                    "success": control_flow["success"],
                },
                "execution": "plan_only",
            })
        elif kind == "generic_cid":
            rows.append({
                "role": binding["role"],
                "kind": kind,
                "requests": [_registry_request_row(parser, master, category_id, 0xDC, "request")],
                "response_model": profile["response_model"],
                "execution": "plan_only",
            })
        elif kind == "p5_active_test_init":
            initial_read = profile["init_model"]["initial_read"]
            rows.append({
                "role": binding["role"],
                "kind": kind,
                "initial_read": {
                    "selector": initial_read["selector"],
                    "base_request": initial_read["base_request"],
                    "did_substitution": (
                        "request bytes 1/2 take the selected type-68 initial-read DID before send; "
                        "per-test requests are on each direct active-test row"
                    ),
                    "positive_check": initial_read["base_positive_check"],
                },
                "execution": "plan_only",
            })
    return sorted(rows, key=lambda row: row["role"])


def _session_requirement(send_hex: str) -> str:
    """Classify a request against the recovered P5 first-byte session classifier.

    Request byte 0x01..0x0F is class 1 (default-session path); byte >= 0x10 is
    class 2, which the current-P5 host serves from extended session.
    """
    return "extended" if send_hex[:2].ljust(2, "0") >= "10" else "default"


def _registry_session_control(
    parser: DDBParser,
    master: Any,
    categories: list[dict[str, Any]],
) -> dict[str, Any]:
    """Current-P5 session lifecycle (TMS-077) with per-category resolved frames."""
    lifecycle = _execution_model()["gtsplus_continuity"]["dll_role_schema"]["execution_lifecycle"]
    transport = lifecycle["transport_and_session"]
    auto = transport["p5_automatic_session_judgment"]
    uds2 = auto["uds_class_2"]

    def frame_row(category_id: int, selector: int) -> dict[str, Any] | None:
        matches = _master_frame_rows(parser, master, category_id, selector)
        if len(matches) != 1:
            return None
        row = matches[0]
        return {
            "selector": row["selector"],
            "frame": row["comm_frame_id"],
            "send": row["send"]["bytes"],
            "mask": row["receive_mask"]["bytes"],
            "check": row["receive_check"]["bytes"],
            "comm_set": row["comm_set"],
        }

    per_category = {}
    for category in categories:
        category_id = int(category["category_id"])
        default = frame_row(category_id, 0xD1)
        extended = frame_row(category_id, 0xD2)
        keepalive = frame_row(category_id, 0xDD)
        for row, expected in ((default, "1001"), (extended, "1003"), (keepalive, "22f186")):
            if row is not None and row["send"] != expected:
                raise ValueError(
                    f"category {category_id} session frame {row['selector']} drift: {row['send']} != {expected}"
                )
        per_category[str(category_id)] = {
            "generation_low5": f"0x{int(category['generation']) & 0x1F:02X}",
            "default_session": default,
            "extended_session": extended,
            "keepalive": keepalive,
        }

    judgment = uds2["session_judgment_flag"]
    test_present = transport["test_present"]
    if uds2["phase5_session_sender"]["current_camry_wire_sequence"] != ["10 01", "10 03"]:
        raise ValueError("current-P5 session enter sequence drifted from the pinned wire proof")
    wire_sequence = ["1001", "1003"]
    return {
        "generation": "current-p5",
        "default_session": 1,
        "extended_session": 3,
        "enter_sequence": wire_sequence,
        "return_default": "1001",
        "keepalive": {
            "kind": "session_did_poll",
            "did": "0xF186",
            "request": "22f186",
            "positive_prefix": "62f186",
            "interval_s": round(test_present["cadence_ms"] / 1000, 3),
            "selector": "0xDD",
            "mask": "ff",
            "check": "62",
            "meaning": test_present["meaning"],
            "session_state": transport["session_state"],
        },
        "category_gate": auto["category_gate"],
        "request_classifier": auto["classifier"]["rule"],
        "class_1_default": auto["class_1_default"],
        "class_2_normal_path": uds2["normal_path"],
        "session_judgment_exception": {
            "role": "documentation",
            "runtime_default": False,
            "flag": judgment["field"],
            "setter": judgment["setter"],
            "clearer": judgment["clearer"],
            "behavior": judgment["phase5_alternate_behavior"],
            "external_importers": judgment["external_importers"],
        },
        "wire_proven_categories": sorted(int(key) for key in auto["categories"]),
        "per_category": per_category,
        "boundary": (
            "frames are resolved per category from the current master; the host lifecycle behavior "
            "(generation gate, classifier, cadence, session-judgment exception) is instruction-proven "
            "for the wire-proven categories only; session_judgment_exception is documentation, "
            "not a runtime default"
        ),
    }


def _registry_utilities(parser: DDBParser, master: Any) -> dict[str, Any]:
    """Compact runtime utility surface over the already-recovered generic families."""
    generic_roles = _execution_model()["gtsplus_continuity"]["dll_role_schema"]["execution_lifecycle"][
        "transport_and_session"
    ]["generic_roles"]
    bindings = []
    by_role: dict[int, list[str]] = {}
    for entry in parser.extract_master_dlls(master.sections[19]):
        if entry.category_id == 0:
            by_role.setdefault(entry.dll_role_id, []).append(entry.dll_name)
    for role in sorted(GENERIC_UTILITY_ROLE_KINDS):
        dlls = sorted(set(by_role.get(role, [])))
        if len(dlls) != 1:
            raise ValueError(f"generic utility role 0x{role:X} resolved {len(dlls)} master bindings: {dlls}")
        pinned = generic_roles.get(f"0x{role:X}")
        if pinned is not None and pinned["plugin"] != dlls[0]:
            raise ValueError(
                f"generic utility role 0x{role:X} drift: master {dlls[0]} vs execution model {pinned['plugin']}"
            )
        bindings.append({"role": role, "dll": dlls[0], "semantic_kind": GENERIC_UTILITY_ROLE_KINDS[role]})
    return {
        "scope": (
            "recovered generic (category-0) command families only; every other generic role is "
            "intentionally absent rather than classified"
        ),
        "bindings": bindings,
        "routine_control": {
            "service": "0x31",
            "positive_response": "0x71",
            "start_selector": "0xD5",
            "stop_selector": "0xD6",
            "result_selector": "0xD7",
            "session_requirement": "extended",
            "request_template": (
                "31 <01 start|02 stop|03 result> FF FF; template bytes 2/3 are replaced by the "
                "selected type-71 routine ID; per-category frames are in catalogs.<id>.selectors"
            ),
        },
        "io_control": {
            "service": "0x2F",
            "positive_response": "0x6F",
            "start_selector": "0x9D",
            "stop_selector": "0x64",
            "session_requirement": "extended",
            "request_template": (
                "2F FF FF <03 shortTermAdjustment|00 returnControlToECU>; template bytes 1/2 are "
                "replaced by the control DID; the trailing value/control-enable payload length is "
                "runtime DataIdLengthList state"
            ),
        },
        "utility_list_source": (
            "per-ECU supported-function menu is catalogs.<id>.functions (master type-26/27 via "
            "GetEcuFuncList role 0x4); names are not recovered for these categories"
        ),
        "boundary": (
            "list/plan surface only; no execution authorization, SecurityAccess, session escalation, "
            "flash, or write workflow is included"
        ),
    }


def build_toyota_diag_registry(gts_root: Path, region: str = "NA", family: str = "Gen") -> dict[str, Any]:
    gts_root = _resolve_gts_root(gts_root)
    db_root = _db_root(gts_root, region, family)
    parser = DDBParser()
    master_path = db_root / "Toyota.ddb"
    master = parser.parse_master_db(master_path)
    strings_path = db_root / "M_English.ddb"
    strings = _english_strings(parser, db_root)
    dtc_clear_path = ROOT / "data/generated/camry_2026_dtc_clear.json"
    dtc_clear = json.loads(dtc_clear_path.read_text())
    nrtd_p5_path = ROOT / "data/generated/camry_2026_nrtd_p5.json"
    nrtd_p5 = json.loads(nrtd_p5_path.read_text())
    eps_identity_path = ROOT / "targets/camry-2026/raw-20260826/identity.json"
    eps_identity = json.loads(eps_identity_path.read_text())

    profile = json.loads(json.dumps(CAMRY_2026_DIAG_PROFILE))
    known_categories = sorted({
        int(ecu["category_id"])
        for ecu in profile["ecus"]
        if "category_id" in ecu
    })
    catalogs: dict[str, Any] = {}
    source_files = [master_path, strings_path, dtc_clear_path, nrtd_p5_path, eps_identity_path, EXECUTION_MODEL]
    bin_root = gts_root / "bin"
    resolved_categories = []
    for category_id in known_categories:
        category = _resolve_master_category(parser, master, strings, str(category_id))
        resolved_categories.append(category)
        db_path = db_root / str(category["database"])
        db = parser.parse_ecu_db(db_path)
        source_files.append(db_path)
        monitor_rows = _monitor_rows(db, strings, db_path.name)
        bindings = _registry_role_bindings(parser, master, category, bin_root)
        catalogs[str(category_id)] = {
            "category": category,
            "dids": _registry_did_catalog(monitor_rows),
            "dtcs": _registry_dtc_catalog(parser, db, strings, db_path.name),
            "active_tests": _registry_active_tests(parser, master, category, db_root, strings, monitor_rows),
            "functions": _registry_function_hierarchy(parser, master, strings, category_id),
            "plugins": bindings,
            "commands": _registry_command_rows(parser, master, category, bin_root, bindings),
            "selectors": _registry_selector_rows(parser, master, category_id),
            "data_list": _registry_data_list(db, strings),
            "active_test_groups": _registry_active_test_groups(parser, category, db_root),
        }
    profile["catalog_category_ids"] = known_categories
    profile["session_control"] = _registry_session_control(parser, master, resolved_categories)

    referenced_comm_sets = {
        int(row["comm_set"])
        for catalog in catalogs.values()
        for row in catalog["selectors"]
    }
    for session_row in profile["session_control"]["per_category"].values():
        for frame_key in ("default_session", "extended_session", "keepalive"):
            frame = session_row[frame_key]
            if frame is not None:
                referenced_comm_sets.add(int(frame["comm_set"]))
    referenced_comm_sets = sorted(referenced_comm_sets)
    commsets = {}
    for row in _master_comm_set_rows(parser, master):
        if row["comm_set_id"] not in referenced_comm_sets:
            continue
        commsets[str(row["comm_set_id"])] = {
            "send_parameter": row["send_parameter"],
            "receive_timeout": row["receive_timeout"],
            "retry_count": row["retry_count"],
            "exception_handler_id": row["exception_handler_id"],
            "exception_handler_flag": row["exception_handler_flag"],
        }
    if sorted(int(key) for key in commsets) != referenced_comm_sets:
        raise ValueError("referenced CommSet ids did not all resolve in the master table")

    mode04 = dtc_clear["legislated_obd"]
    profile["dtc_clear"] = {
        "physical_uds14": dtc_clear["physical_uds14"],
        "functional_obd": {
            "request_id": int(mode04["request_id"], 16),
            "mode04_request": mode04["mode04_clear_request_frame"],
            "positive_prefix": "0144",
            "expected_responders": sorted(int(value, 16) for value in mode04["mode04_positive_responses"]),
        },
        "boundary": dtc_clear["boundary"],
    }
    profile["catalog_category_ids"] = known_categories

    topology_rows = _master_canbus_topology_rows(parser, master, strings, "12704")
    if len(topology_rows) != 1:
        raise ValueError("Camry HV CAN topology cardinality drift")
    topology = topology_rows[0]
    if topology["vehicle_name"] != "Camry HV":
        raise ValueError("Camry HV CAN topology name drift")
    if topology["option_count"] != 18 or topology["placement_variant_count"] != 1:
        raise ValueError("Camry HV CAN topology option/variant drift")
    profile["gts_can_topology"] = {
        **topology,
        "namespace_boundary": "Toyota GTS Bus N names are vehicle-network domains, not Panda logical bus numbers; current post-repin diagnostics use Panda bus0",
    }

    observed_identities = _registry_nrtd_observed_identities(nrtd_p5)
    observed_identities["eps"] = _registry_eps_observed_identity(eps_identity)
    for ecu in profile["ecus"]:
        identity = observed_identities.get(ecu["key"])
        if identity is not None:
            ecu["observed_identity"] = identity

    return {
        "schema": "toyota-diagnostics-registry-v4",
        "profile": profile,
        "decoders": {
            "p5-linear-msb0-v1": {
                "payload_origin": "UDS DID value bytes (positive SID/DID echo excluded)",
                "bit_numbering": "msb0",
                "byte_order": "big-endian",
                "bit_range": "inclusive",
                "sign": "unsigned unless signal.signed; signed values use two's-complement at signal bit width",
                "integer_formula": "trunc_toward_zero(signed_raw * mul / div) + offset",
                "display_formula": "converted_integer / 10^decimal_point_count",
                "pattern_lookup": "match converted_integer before decimal rendering",
            }
        },
        "commsets": {
            "boundary": (
                "receive_timeout feeds CheckAndConvertRcvTimeOut before Receive; retry_count bounds "
                "retransmission attempts; send_parameter reaches SendInt argument 4, which the common "
                "CAN SendProc does not consume"
            ),
            "rows": commsets,
        },
        "utilities": _registry_utilities(parser, master),
        "function_names": REGISTRY_FUNCTION_NAME_BOUNDARY,
        "catalogs": catalogs,
        "source_identity": {
            key: {
                "bytes": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
            for key, path in sorted(
                ((_registry_source_key(path, gts_root), path) for path in set(source_files)),
                key=lambda item: item[0],
            )
        },
        "boundary": (
            "Clean derived diagnostic metadata only: no Toyota binaries are embedded. Active Tests are static plans; "
            "execution=executable only means the fixed request geometry is complete, not that the registry authorizes "
            "execution: it intentionally contains no execution authorization, session escalation, SecurityAccess, "
            "flash, or write workflow."
        ),
    }


def cmd_registry(args: argparse.Namespace) -> int:
    gts = _resolve_gts_root(args.gtsplus_root)
    if args.profile != "camry-2026-f33":
        raise SystemExit(f"unsupported derived registry profile {args.profile!r}")
    payload = build_toyota_diag_registry(gts, args.region, args.family)
    text = json.dumps(payload, indent=None if args.compact else 2, sort_keys=True, separators=(",", ":") if args.compact else None) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(out)
    else:
        sys.stdout.write(text)
    return 0

def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--gtsplus-root", help="GTS+ external root or .../Toyota Diagnostics/GTSPlus (default: GTSPLUS_ROOT/repo pin)")
    parser.add_argument("--cuw-root", help="CUW corpus root (default: TOYOTA_CUW_CORPUS_ROOT/repo pin)")
    parser.add_argument("--cuwplus-root", help="CUWPlus root containing Ini/ and writer DLLs (default: adjacent to selected GTS+ tree or GTSPLUS_CUW_ROOT)")
    parser.add_argument("--region", default="NA", help="GTS+ region (default: NA)")
    parser.add_argument("--family", default="Gen", help="GTS+ DB family (default: Gen)")
    parser.add_argument("--json", action="store_true", help="emit JSON")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status", help="show resolved evidence roots and corpus sizes")
    _common(p)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("search", help="search OEM names + resolved DIDs/DTCs/behaviors/routes/CUWs")
    p.add_argument("query")
    p.add_argument("--ecu", help="limit DDB semantic search to ECU filename substring")
    p.add_argument("--kind", action="append", choices=("did", "dtc", "behavior", "string", "file", "route", "cuw"), help="limit result kind; repeatable")
    p.add_argument("--all-string-dbs", action="store_true", help="also search V_English/U_English; default M_English keeps common lookup fast")
    p.add_argument("--limit", type=int, default=80)
    _common(p)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("ecu", help="show table inventory for one ECU .ddb")
    p.add_argument("ecu", help="ECU .ddb name/stem/substr or path")
    _common(p)
    p.set_defaults(func=cmd_ecu)

    p = sub.add_parser("active-test", help="resolve one current P5 Active Test into a read-only static wire plan")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("item", help="Active Test lookup ID (decimal or 0x-prefixed hex)")
    p.add_argument("--kind", choices=("direct", "routine"), help="disambiguate a key present in both type-68 and type-71")
    _common(p)
    p.set_defaults(func=cmd_active_test)

    p = sub.add_parser("command", help="resolve one category+role into plugin, wire frames, timers, and recovered semantics")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("role", help="DLL role ID (decimal or 0x-prefixed hex)")
    p.add_argument("--item", help="selected direct Active Test ID for role 0x08 (decimal or 0x-prefixed hex)")
    _common(p)
    p.set_defaults(func=cmd_command)

    p = sub.add_parser("timer", help="decode Toyota master per-category command timers")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("timer", nargs="?", help="timer ID (decimal or 0x-prefixed hex); omit to list category timers")
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_timer)

    p = sub.add_parser("commset", help="decode Toyota master communication-set timeout/retry metadata")
    p.add_argument("comm_set", nargs="?", help="CommSet ID (decimal or 0x-prefixed hex); omit to list all")
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_commset)

    p = sub.add_parser("role", help="summarize Toyota master DLL roles and their plugin families")
    p.add_argument("role", nargs="?", help="DLL role ID (decimal or 0x-prefixed hex); omit for census")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--plugin-limit", type=int, default=8)
    _common(p)
    p.set_defaults(func=cmd_role)

    p = sub.add_parser("category", help="resolve a Toyota master ECU category, its command plugins, and functions")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_category)

    p = sub.add_parser("registry", help="derive a clean Toyota diagnostic registry for Comma-side tooling")
    p.add_argument("profile", nargs="?", default="camry-2026-f33", choices=("camry-2026-f33",))
    p.add_argument("--out", help="write registry JSON to this path instead of stdout")
    p.add_argument("--compact", action="store_true", help="emit compact JSON for runtime vendoring")
    _common(p)
    p.set_defaults(func=cmd_registry)

    p = sub.add_parser("canbus", help="resolve Toyota master CAN Bus Check topology for a vehicle type/name")
    p.add_argument("vehicle", help="vehicle type ID (decimal/0x) or OEM vehicle-name substring")
    _common(p)
    p.set_defaults(func=cmd_canbus)

    p = sub.add_parser("frame", help="resolve master FuncCommFrame selector(s) to current send/mask/check bytes")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("selector", nargs="?", help="selector ID (decimal or 0x-prefixed hex); omit to list all")
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_frame)

    p = sub.add_parser("did", help="resolve GTS+ Data List DIDs for one ECU")
    p.add_argument("ecu")
    p.add_argument("query", nargs="?", help="DID (hex) or OEM-name substring")
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_did)

    p = sub.add_parser("dtc", help="resolve GTS+ DTC descriptions/failure types for one ECU")
    p.add_argument("ecu")
    p.add_argument("query", nargs="?", help="DTC/name/failure substring")
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_dtc)

    p = sub.add_parser("route", help="decode current CUWPlus contact-type -> writer DLL routes")
    p.add_argument("query", nargs="?", help="contact type / writer / CID getter substring")
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_route)

    p = sub.add_parser("cuw", help="inspect one CUW and resolve its current GTS+ writer route; otherwise search corpus")
    p.add_argument("query", help="CUW filename/path, 'list', or descriptor substring")
    p.add_argument("--verbose", action="store_true", help="print complete attach descriptor")
    p.add_argument("--validate", action="store_true", help="fully validate/hash the entire CUW container (slower for large packages)")
    p.add_argument("--limit", type=int, default=80)
    _common(p)
    p.set_defaults(func=cmd_cuw)

    p = sub.add_parser("pe", help="inspect GTS+/CUWPlus PE imports/exports/strings")
    p.add_argument("binary", help="DLL/EXE filename, substring, or path")
    p.add_argument("query", nargs="?", help="filter imports/exports/strings")
    p.add_argument("--min-string", type=int, default=5)
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_pe)

    p = sub.add_parser(
        "recover-bodies",
        help="recover original GTS+ PE bodies from the installer GTSPlus/GTSPlusCP twin groups",
    )
    p.add_argument("--archive", type=Path, default=GTSPLUS_BODY_ARCHIVE, help="gtsplus_msi.7z archive")
    p.add_argument("--output", type=Path, default=GTSPLUS_BODY_OUTPUT, help="recovered plaintext output root")
    p.add_argument("--keep-workspace", action="store_true", help="keep carved installer workspace under build/tmp")
    _common(p)
    p.set_defaults(func=cmd_recover_bodies)

    return ap


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
