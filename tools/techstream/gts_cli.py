#!/usr/bin/env python3
"""Fast, read-only query surface over Toyota GTS+/Techstream evidence.

This command is for discovery, not proof generation. It exposes the shared
mechanics already recovered by the repository (DDB parsing/string resolution,
CUW descriptor parsing + writer-route resolution, and PE metadata/string
inspection) without merging the subsystem-specific deterministic generators.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any, Iterable

import pefile

ROOT = Path(__file__).resolve().parents[2]
TECHSTREAM_TOOLS = ROOT / "tools" / "techstream"
sys.path.insert(0, str(TECHSTREAM_TOOLS))

from cuw_parameter import factory_routes_from_ini_root  # noqa: E402
from cuw_attach import parse_attach_bytes  # noqa: E402
from parse_cuw_container import first_member_payload, parse as parse_cuw_container, read_first_member  # noqa: E402
from parse_ddb import DDBParser, ECU_TABLE_CLASS_NAMES, StringDataBase  # noqa: E402
from ddb_semantics import behavior_rows as semantic_behavior_rows, dtc_rows as semantic_dtc_rows, monitor_rows as semantic_monitor_rows  # noqa: E402
from ddb_strings import load_string_db as cached_string_db  # noqa: E402
from pe_utils import binary_strings as pe_binary_strings, exports as pe_exports, imports as pe_imports  # noqa: E402
from techstream_paths import (  # noqa: E402
    GTSPLUS_EXTERNAL_ROOT, CUW_CORPUS_ROOT, gts_db_root,
    resolve_cuw_corpus, resolve_cuwplus_root, resolve_gts_root,
)

DEFAULT_GTS_EXTERNAL = GTSPLUS_EXTERNAL_ROOT
DEFAULT_CUW_CORPUS = CUW_CORPUS_ROOT


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
