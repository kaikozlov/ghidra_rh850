#!/usr/bin/env python3
"""Fast query and recovery surface over Toyota GTS+/Techstream evidence.

Most commands are read-only discovery helpers over already recovered repository
mechanics. The recover-* commands are the explicit exception: they materialize
validated analysis PEs and provenance manifests under their selected output root.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.techstream.gts.active_tests import resolve_active_test
from tools.techstream.gts.bundle import TOYOTA_DIAG_BUNDLE_PROFILE, write_toyota_diag_bundle
from tools.techstream.gts.commands import _master_command_plan
from tools.techstream.gts.cuw import (
    _cuw_descriptor,
    _cuw_descriptor_fast,
    _cuw_files,
    _new_cids,
    _node_summary,
    _resolve_cuw,
    _search_cuw_corpus,
    _target_calibrations,
)
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts import render
from tools.techstream.gts.render import _print_rows
from tools.techstream.gts.master import (
    _master_canbus_topology_rows,
    _master_comm_set_rows,
    _master_frame_rows,
    _master_functions,
    _master_plugins,
    _master_role_catalog,
    _master_timer_rows,
    _parse_master_key,
    _resolve_master_category,
)
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.gts.query import (
    _resolve_pe,
    _route_match,
    _route_rows,
    dtc_rows,
    did_rows,
    ecu_payload,
    pe_payload,
    search_rows,
    status_payload,
)
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT as GTS_ALL_BODY_OUTPUT
from tools.techstream.recover_all_gtsplus_bodies import recover as recover_all_gtsplus_bodies
from tools.techstream.recover_cp_bodies import DEFAULT_AUX_OUTPUT as GTS_AUX_BODY_OUTPUT
from tools.techstream.recover_cp_bodies import DEFAULT_OUTPUT as CUWPLUS_BODY_OUTPUT
from tools.techstream.recover_cp_bodies import recover as recover_cp_bodies
from tools.techstream.recover_cp_bodies import recover_auxiliary as recover_gts_aux_bodies
from tools.techstream.recover_gtsplus_bodies import DEFAULT_ARCHIVE as GTSPLUS_BODY_ARCHIVE
from tools.techstream.recover_gtsplus_bodies import DEFAULT_OUTPUT as GTSPLUS_BODY_OUTPUT
from tools.techstream.recover_gtsplus_bodies import recover as recover_gtsplus_bodies
from tools.techstream.gts.registry import build_toyota_diag_registry
from tools.techstream.techstream_paths import (
    gts_db_root,
    resolve_cuw_corpus,
    resolve_cuwplus_root,
    resolve_gts_root,
)
from tools.techstream.vdas import json_path as vdas_json_path
from tools.techstream.vdas import load_vdas


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--gtsplus-root", help="GTS+ external root or .../Toyota Diagnostics/GTSPlus (default: GTSPLUS_ROOT/repo pin)")
    parser.add_argument("--cuw-root", help="CUW corpus root (default: TOYOTA_CUW_CORPUS_ROOT/repo pin)")
    parser.add_argument("--cuwplus-root", help="CUWPlus root containing Ini/ and writer DLLs (default: adjacent to selected GTS+ tree or GTSPLUS_CUW_ROOT)")
    parser.add_argument("--region", default="NA", help="GTS+ region (default: NA)")
    parser.add_argument("--family", default="Gen", help="GTS+ DB family (default: Gen)")
    parser.add_argument("--json", action="store_true", help="emit JSON")


def _recovery_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--gtsplus-root", help="GTS+ external root or .../Toyota Diagnostics/GTSPlus (default: GTSPLUS_ROOT/repo pin)")
    parser.add_argument("--json", action="store_true", help="emit JSON; progress remains on stderr")


def cmd_status(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    cuwplus = resolve_cuwplus_root(gts, args.cuwplus_root)
    corpus = resolve_cuw_corpus(args.cuw_root)
    db = gts_db_root(gts, args.region, args.family)
    render.status(status_payload(gts, cuwplus, corpus, db), as_json=args.json)
    return 0


def cmd_ecu(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    render.ecu(ecu_payload(db_root, args.ecu), as_json=args.json)
    return 0


def cmd_did(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    rows = did_rows(db_root, args.ecu, args.query)
    _print_rows(rows, as_json=args.json, limit=args.limit)
    return 0


def cmd_dtc(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    rows = dtc_rows(db_root, args.ecu, args.query)
    _print_rows(rows, as_json=args.json, limit=args.limit)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    cuwplus = resolve_cuwplus_root(gts, args.cuwplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    kinds = set(args.kind or ["did", "dtc", "behavior", "string", "file", "route", "cuw"])
    results = search_rows(
        args.query,
        gts,
        cuwplus,
        db_root,
        resolve_cuw_corpus(args.cuw_root),
        kinds=kinds,
        ecu_filter=args.ecu,
        all_string_dbs=args.all_string_dbs,
    )
    _print_rows(results, as_json=args.json, limit=args.limit)
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    rows = _route_rows(resolve_cuwplus_root(gts, args.cuwplus_root))
    if args.query:
        rows = [row for row in rows if _route_match(args.query, row)]
    _print_rows(rows, as_json=args.json, limit=args.limit)
    return 0


def cmd_active_test(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = _english_strings(parser, db_root)
    category = _resolve_master_category(parser, master, strings, args.category)
    active_test_id = _parse_master_key(args.item)
    if active_test_id is None:
        raise SystemExit(f"invalid Active Test ID {args.item!r}; use decimal or 0x-prefixed hex")
    kind, payload = resolve_active_test(parser, master, category, db_root, strings, active_test_id, args.kind)
    render.active_test(payload, kind, category, as_json=args.json)
    return 0


def cmd_command(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
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
    render.command(payload, category, as_json=args.json)
    return 0


def cmd_timer(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
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
    render.timers(category, rows[: args.limit], as_json=args.json)
    return 0


def cmd_commset(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
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
    render.commsets(rows[: args.limit], as_json=args.json)
    return 0


def cmd_role(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
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
    render.roles(rows[: args.limit], args.plugin_limit, as_json=args.json)
    return 0


def cmd_category(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = _english_strings(parser, db_root)
    category = _resolve_master_category(parser, master, strings, args.category)
    payload = {
        "category": category,
        "plugins": _master_plugins(parser, master, category["category_id"]),
        "functions": _master_functions(parser, master, strings, category["category_id"]),
    }
    render.category(payload, args.limit, as_json=args.json)
    return 0


def cmd_canbus(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    parser = DDBParser()
    strings = _english_strings(parser, db_root)
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    rows = _master_canbus_topology_rows(parser, master, strings, args.vehicle)
    render.canbus(rows, as_json=args.json)
    return 0


def cmd_frame(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
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


def cmd_cuw(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    cuwplus = resolve_cuwplus_root(gts, args.cuwplus_root)
    corpus = resolve_cuw_corpus(args.cuw_root)
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
    render.cuw(payload, outer, vehicle, routes, contact, descriptor, verbose=args.verbose, as_json=args.json)
    return 0


def cmd_pe(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    cuwplus = resolve_cuwplus_root(gts, args.cuwplus_root)
    path = _resolve_pe(gts, cuwplus, args.binary)
    payload = pe_payload(path, args.query, args.min_string, args.limit)
    render.pe(payload, path.read_bytes(), path, limit=args.limit, as_json=args.json)
    return 0



def cmd_recover_bodies(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    manifest = recover_gtsplus_bodies(
        archive=args.archive,
        output=args.output,
        installed_root=gts,
        keep_workspace=args.keep_workspace,
    )
    render.recover_bodies(manifest, as_json=args.json)
    return 0


def cmd_recover_cuw_bodies(args: argparse.Namespace) -> int:
    manifest = recover_cp_bodies(
        gtsplus_root=Path(args.gtsplus_root).expanduser() if args.gtsplus_root else None,
        source=args.source,
        output=args.output,
        workers=args.workers,
        only=args.only,
        keep_workspace=args.keep_workspace,
        progress=render._recovery_progress("CUWPlus"),
    )
    render.recover_cuw_bodies(manifest, as_json=args.json)
    return 0


def cmd_recover_aux_bodies(args: argparse.Namespace) -> int:
    manifest = recover_gts_aux_bodies(
        gtsplus_root=Path(args.gtsplus_root).expanduser() if args.gtsplus_root else None,
        output=args.output,
        workers=args.workers,
        only=args.only,
        keep_workspace=args.keep_workspace,
        progress=render._recovery_progress("Auxiliary"),
    )
    render.recover_aux_bodies(manifest, as_json=args.json)
    return 0


def cmd_recover_all_bodies(args: argparse.Namespace) -> int:
    manifest = recover_all_gtsplus_bodies(
        gtsplus_root=Path(args.gtsplus_root).expanduser() if args.gtsplus_root else None,
        output=args.output,
        workers=args.workers,
        keep_workspace=args.keep_workspace,
        progress=render._aggregate_recovery_progress,
    )
    render.recover_all_bodies(manifest, as_json=args.json)
    return 0


def cmd_registry(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    if args.profile == TOYOTA_DIAG_BUNDLE_PROFILE:
        if not args.out:
            raise SystemExit("toyota-current is a sharded ZIP bundle; pass --out FILE.zip")
        out = Path(args.out)
        payload = write_toyota_diag_bundle(gts, out, family=args.family)
        render.registry_bundle(out, payload, as_json=args.json)
        return 0
    if args.profile != "camry-2026-f33":
        raise SystemExit(f"unsupported derived registry profile {args.profile!r}")
    payload = build_toyota_diag_registry(gts, args.region, args.family)
    text = render.registry_json_text(payload, compact=args.compact)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(out)
    else:
        sys.stdout.write(text)
    return 0

def cmd_vdas(args: argparse.Namespace) -> int:
    try:
        payload = load_vdas(Path(args.file))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.path:
        try:
            selected = vdas_json_path(payload["document"], args.path)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        render.vdas_value(selected, as_json=args.json)
        return 0
    render.vdas_document(payload, as_json=args.json)
    return 0



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

    p = sub.add_parser("registry", help="derive a clean Toyota diagnostic registry/bundle for Comma-side tooling")
    p.add_argument(
        "profile", nargs="?", default="camry-2026-f33",
        choices=("camry-2026-f33", TOYOTA_DIAG_BUNDLE_PROFILE),
        help="camry-2026-f33 legacy single-vehicle JSON or toyota-current universal regional ZIP bundle",
    )
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

    p = sub.add_parser("vdas", help="inspect a PCS Vehicle Data Analysis .vdas file (standard ZIP + UTF-8 json.log)")
    p.add_argument("file", help="path to .vdas file")
    p.add_argument("--path", help="case-insensitive dotted JSON path, e.g. Gts.Tss3Ffd.Data")
    p.add_argument("--json", action="store_true", help="emit parsed JSON / selected value as JSON")
    p.set_defaults(func=cmd_vdas)

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
    _recovery_common(p)
    p.set_defaults(func=cmd_recover_bodies)

    p = sub.add_parser(
        "recover-cuw-bodies",
        help="decode CP-protected CUWPlus PE bodies by emulating the protector handoff",
    )
    p.add_argument("--source", type=Path, help="protected CUWPlus directory (default: sibling of selected GTSPlus tree)")
    p.add_argument("--output", type=Path, default=CUWPLUS_BODY_OUTPUT, help="clean recovered output root")
    p.add_argument("--workers", type=int, help="parallel decoder workers (default: up to 8)")
    p.add_argument("--only", action="append", help="recover only a filename or filename substring (repeatable)")
    p.add_argument("--keep-workspace", action="store_true", help="keep decoder memory/log workspace under build/tmp")
    _recovery_common(p)
    p.set_defaults(func=cmd_recover_cuw_bodies)

    p = sub.add_parser(
        "recover-aux-bodies",
        help="decode CP-protected PE bodies outside the main GTSPlus and CUWPlus trees",
    )
    p.add_argument("--output", type=Path, default=GTS_AUX_BODY_OUTPUT, help="clean recovered auxiliary output root")
    p.add_argument("--workers", type=int, help="parallel decoder workers (default: up to 8)")
    p.add_argument("--only", action="append", help="recover only a filename or relative-path substring (repeatable)")
    p.add_argument("--keep-workspace", action="store_true", help="keep decoder memory/log workspace under build/tmp")
    _recovery_common(p)
    p.set_defaults(func=cmd_recover_aux_bodies)

    p = sub.add_parser(
        "recover-all-bodies",
        help="recover all 249 CP-protected PE bodies across GTSPlus, CUWPlus, and auxiliary products",
    )
    p.add_argument("--output", type=Path, default=GTS_ALL_BODY_OUTPUT, help="complete recovered suite output root")
    p.add_argument("--workers", type=int, help="parallel CP decoder workers (default: up to 8)")
    p.add_argument("--keep-workspace", action="store_true", help="keep installer/decoder workspaces under build/tmp")
    _recovery_common(p)
    p.set_defaults(func=cmd_recover_all_bodies)

    return ap



def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))



if __name__ == "__main__":
    raise SystemExit(main())
