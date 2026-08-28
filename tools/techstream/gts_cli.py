#!/usr/bin/env python3
"""Fast, read-only query surface over Toyota GTS+/Techstream evidence.

This command is for discovery, not proof generation. It exposes the shared
mechanics already recovered by the repository (DDB parsing/string resolution,
CUW descriptor parsing + writer-route resolution, and PE metadata/string
inspection) without merging the subsystem-specific deterministic generators.
"""
from __future__ import annotations

import argparse
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
from ddb_semantics import monitor_rows as semantic_monitor_rows
from ddb_strings import load_string_db as cached_string_db
from diagnostic_role_model import plugin_operation_signature, role_operation_catalog
from parse_cuw_container import first_member_payload, read_first_member
from parse_cuw_container import parse as parse_cuw_container
from parse_ddb import ECU_TABLE_CLASS_NAMES, DDBParser, StringDataBase
from pe_utils import binary_strings as pe_binary_strings
from pe_utils import exports as pe_exports
from pe_utils import imports as pe_imports
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
    return _without_raw(semantic_monitor_rows(db, strings, source, deduplicate=True))


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
        return f"did\t{row['source']}\t0x{did:04X}{alt_text}\t{row.get('name') or ''}"
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


def _execution_plugin_profiles() -> dict[str, dict[str, Any]]:
    data = json.loads(EXECUTION_MODEL.read_text())
    return data["gtsplus_continuity"]["dll_role_schema"]["plugin_semantics"]


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


def _master_command_plan(
    parser: DDBParser,
    master: Any,
    category: dict[str, Any],
    role: int,
    bin_root: Path,
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
        "boundary": (
            "Frames/timers are resolved from the selected category. Executable semantics are attached only "
            "when the selected plugin SHA-256 exactly matches a recovered profile."
        ),
    }
    if profile is None:
        return result

    if profile_name == "role_0x52_generic_cid":
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
    try:
        payload = _master_command_plan(parser, master, category, role, gts / "bin")
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

    p = sub.add_parser("command", help="resolve one category+role into plugin, wire frames, timers, and recovered semantics")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("role", help="DLL role ID (decimal or 0x-prefixed hex)")
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

    return ap


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
