#!/usr/bin/env python3
"""Fast query and recovery surface over Toyota GTS+/Techstream evidence.

Most commands are read-only discovery helpers over already recovered repository
mechanics. The recover-* commands are the explicit exception: they materialize
validated analysis PEs and provenance manifests under their selected output root.

Schema-first discovery:
  tools/gts ecu FRC_P5                 DDB tables and record classes
  tools/gts did FRC_P5 0x1B06 --json    Data List / alternate snapshot DIDs
  tools/gts recorder 0x5A08 --json      PCS recorder field definitions
  tools/gts recorder 0x1F06 --schema adu
  tools/gts category FRC_P5            ECU/plugin routing

Guide: docs/tooling/gts-query-cli.md#schema-first-workflow
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from tools.techstream.gts.active_tests import resolve_active_test
from tools.techstream.gts.bundle import TOYOTA_DIAG_BUNDLE_PROFILE, TOYOTA_DIAG_BUNDLE_REGIONS, write_toyota_diag_bundle
from tools.techstream.diag_bundle import DEFAULT_BUNDLE, DEFAULT_BUNDLE_ZIP, DiagnosticBundle
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
from tools.techstream.ddb_semantics import NativeSelectionError, UnresolvedNativeContext, select_for_consumer
from tools.techstream.gts import render
from tools.techstream.gts.render import _print_rows
from tools.techstream.gts.master import (
    _master_category_rows,
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
    _cuw_route_selection,
    dtc_rows,
    did_rows,
    ecu_payload,
    native_selection_context,
    pe_payload,
    recorder_payload,
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
from tools.techstream.gts.registry import build_toyota_diag_registry, write_toyota_diag_registry
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
    parser.add_argument("--cuwplus-root", help="explicit CUWPlus product root or flat INI corpus (default: installed CUWPlus sibling of selected GTS+ tree; override: GTSPLUS_CUW_ROOT)")
    parser.add_argument("--region", default="NA", help="GTS+ region (default: NA)")
    parser.add_argument("--family", default="Gen", help="raw ECU/string DB family (default: Gen); native master queries load Gen and Spe")
    parser.add_argument("--json", action="store_true", help="emit JSON")


def _native_common(parser: argparse.ArgumentParser, *, raw: bool = False) -> None:
    _common(parser)
    parser.add_argument(
        "--native-context", choices=("initial", "unknown"), default="initial",
        help="explicit offline initial snapshot (default), or unknown preexisting native history",
    )
    parser.add_argument(
        "--native-history", type=Path,
        help="ordered JSON load/reflection event array; registry export with history/unknown uses --region only",
    )
    if raw:
        parser.add_argument("--raw", action="store_true", help="show every matching physical catalog occurrence, not native selection")


def _native_context(args: argparse.Namespace, gts: Path):
    context = native_selection_context(
        gts, args.region, history=args.native_history,
        history_known=args.native_context != "unknown",
    )
    args.native_selection = context
    return context


def _category_catalog_rows(parser, master, strings, query: str) -> list[dict]:
    numeric = _parse_master_key(query)
    rows = _master_category_rows(parser, master, strings)
    if numeric is not None:
        return [row for row in rows if row["category_id"] == numeric]
    exact = [
        row for row in rows
        if query.casefold() in {
            row["database"].casefold(), Path(row["database"]).stem.casefold(),
            row["short_name"].casefold(), (row["name"] or "").casefold(),
        }
    ]
    return exact or [
        row for row in rows
        if any(query.casefold() in (row[field] or "").casefold() for field in ("database", "short_name", "name"))
    ]


def _raw_category_id(parser, master, strings, query: str) -> int:
    rows = _category_catalog_rows(parser, master, strings, query)
    ids = {int(row["category_id"]) for row in rows}
    if len(ids) != 1:
        raise ValueError(f"raw category {query!r} identifies {len(ids)} category keys; use an exact numeric key")
    return ids.pop()


def _print_native_catalog(context, rows: list, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps({
            "selection": "raw-catalog", "native_context": context.as_dict(), "rows": rows,
        }, indent=2, sort_keys=True))
    else:
        print("selection\traw-catalog")
        _print_rows(rows, as_json=False)


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
    render.did(rows, as_json=args.json, limit=args.limit)
    return 0


def cmd_recorder(args: argparse.Namespace) -> int:
    payload = recorder_payload(args.schema, args.query)
    render.recorder(payload, as_json=args.json, limit=args.limit)
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
    master = _native_context(args, gts)
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
    master = _native_context(args, gts)
    strings = _english_strings(parser, db_root)
    category = _resolve_master_category(parser, master, strings, args.category)
    role = _parse_master_key(args.role)
    if role is None:
        raise SystemExit(f"invalid role {args.role!r}; use decimal or 0x-prefixed hex")
    selected_item = _parse_master_key(args.item) if args.item is not None else None
    if args.item is not None and selected_item is None:
        raise SystemExit(f"invalid item {args.item!r}; use decimal or 0x-prefixed hex")
    payload = _master_command_plan(
        parser, master, category, role, gts / "bin", db_root, selected_item, strings
    )
    render.command(payload, category, as_json=args.json)
    return 0


def cmd_timer(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = _native_context(args, gts)
    strings = _english_strings(parser, db_root)
    if args.raw:
        category_id = _raw_category_id(parser, master, strings, args.category)
        timer_id = _parse_master_key(args.timer) if args.timer is not None else None
        if args.timer is not None and timer_id is None:
            raise SystemExit(f"invalid timer {args.timer!r}; use decimal or 0x-prefixed hex")
        rows = [
            row.as_dict() for row in master.raw_records(25)
            if row.category_id == category_id and (timer_id is None or row.u16(6) == timer_id)
        ]
        _print_native_catalog(master, rows[:args.limit], as_json=args.json)
        return 0
    category = _resolve_master_category(parser, master, strings, args.category)
    rows = _master_timer_rows(parser, master, category["category_id"])
    if args.timer is not None:
        timer_id = _parse_master_key(args.timer)
        if timer_id is None:
            raise SystemExit(f"invalid timer {args.timer!r}; use decimal or 0x-prefixed hex")
        rows = [row for row in rows if row["timer_id"] == timer_id]
    if not rows:
        raise SystemExit(f"category {category['category_id']} has no matching timer rows")
    render.timers(category, rows[: args.limit], native_context=master.as_dict(), as_json=args.json)
    return 0


def cmd_commset(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    parser = DDBParser()
    master = _native_context(args, gts)
    if args.raw:
        comm_set_id = _parse_master_key(args.comm_set) if args.comm_set is not None else None
        if args.comm_set is not None and comm_set_id is None:
            raise SystemExit(f"invalid CommSet {args.comm_set!r}; use decimal or 0x-prefixed hex")
        rows = [
            row.as_dict() for row in master.raw_records(29)
            if comm_set_id is None or row.u16(10) == comm_set_id
        ]
        _print_native_catalog(master, rows[:args.limit], as_json=args.json)
        return 0
    query = None
    rows = _master_comm_set_rows(parser, master)
    if args.comm_set is not None:
        comm_set_id = _parse_master_key(args.comm_set)
        if comm_set_id is None:
            raise SystemExit(f"invalid CommSet {args.comm_set!r}; use decimal or 0x-prefixed hex")
        rows = [row for row in rows if row["comm_set_id"] == comm_set_id]
        query = master.query(29, comm_set_id)
        select_for_consumer(query, "commset")
        if not rows:
            raise SystemExit(f"no Toyota master CommSet {comm_set_id}")
    render.commsets(
        rows[: args.limit], native_context=master.as_dict(),
        query=query.as_dict() if query is not None else None, as_json=args.json,
    )
    return 0


def cmd_role(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    parser = DDBParser()
    master = _native_context(args, gts)
    if args.raw:
        role = _parse_master_key(args.role) if args.role is not None else None
        if args.role is not None and role is None:
            raise SystemExit(f"invalid role {args.role!r}; use decimal or 0x-prefixed hex")
        rows = [
            row.as_dict() for row in master.raw_records(19)
            if role is None or row.dll_role_id == role
        ]
        _print_native_catalog(master, rows[:args.limit], as_json=args.json)
        return 0
    rows = _master_role_catalog(parser, master, gts / "bin")
    if args.role is not None:
        role = _parse_master_key(args.role)
        if role is None:
            raise SystemExit(f"invalid role {args.role!r}; use decimal or 0x-prefixed hex")
        rows = [row for row in rows if row["role"] == role]
        if not rows:
            raise SystemExit(f"no Toyota master DLL role 0x{role:X}")
    render.roles(rows[: args.limit], args.plugin_limit, native_context=master.as_dict(), as_json=args.json)
    return 0


def cmd_category(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = _native_context(args, gts)
    strings = _english_strings(parser, db_root)
    if args.raw:
        rows = _category_catalog_rows(parser, master, strings, args.category)
        _print_native_catalog(master, rows[:args.limit], as_json=args.json)
        return 0
    category = _resolve_master_category(parser, master, strings, args.category)
    payload = {
        "native_context": master.as_dict(),
        "raw_plugin_bindings": [
            row.as_dict() for row in master.raw_records(19) if row.category_id == category["category_id"]
        ],
        "functions_selection": "raw-catalog; function-table comparator not inferred",
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
    master = _native_context(args, gts)
    rows = _master_canbus_topology_rows(parser, master, strings, args.vehicle)
    for row in rows:
        row["selection"] = "raw-catalog"
        row["native_context"] = master.as_dict()
    render.canbus(rows, as_json=args.json)
    return 0


def cmd_frame(args: argparse.Namespace) -> int:
    gts = resolve_gts_root(args.gtsplus_root)
    db_root = gts_db_root(gts, args.region, args.family)
    parser = DDBParser()
    master = _native_context(args, gts)
    strings = _english_strings(parser, db_root)
    selector = _parse_master_key(args.selector) if args.selector is not None else None
    if args.selector is not None and selector is None:
        raise SystemExit(f"invalid selector {args.selector!r}; use decimal or 0x-prefixed hex")
    if args.raw:
        category_id = _raw_category_id(parser, master, strings, args.category)
        rows = [
            row.as_dict() for row in master.raw_records(18)
            if row.category_id == category_id and (selector is None or row.u16(2) == selector)
        ]
        _print_native_catalog(master, rows[:args.limit], as_json=args.json)
        return 0
    category = _resolve_master_category(parser, master, strings, args.category)
    rows = _master_frame_rows(parser, master, category["category_id"], selector)
    if selector is not None and not rows:
        raise SystemExit(f"category {category['category_id']} has no selector 0x{selector:X}")
    if not args.json:
        print(f"native-context\t{master.as_dict()['resolution']}")
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
    selection = _cuw_route_selection(cuwplus, descriptor)
    routes = selection.pop("routes")
    payload = {
        "path": str(path),
        "outer": {key: outer.get(key) for key in ("format_type", "file_size", "name", "payload_length", "format67_member_count", "format4_archive_count", "validation")},
        "vehicle": vehicle,
        "new_cids": _new_cids(descriptor),
        "target_calibrations": _target_calibrations(descriptor),
        "nodes": _node_summary(descriptor),
        "sections": descriptor,
        "gtsplus_routes": routes,
        "gtsplus_selection": selection,
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
        out = Path(args.out) if args.out else DEFAULT_BUNDLE
        payload = write_toyota_diag_bundle(
            gts, out, family=args.family,
            regions=(args.region,) if args.native_history or args.native_context == "unknown" else TOYOTA_DIAG_BUNDLE_REGIONS,
            native_history=args.native_history, history_known=args.native_context != "unknown",
        )
        render.registry_bundle(out, payload, as_json=args.json)
        return 0
    if args.profile != "camry-2026-f33":
        raise SystemExit(f"unsupported derived registry profile {args.profile!r}")
    payload = build_toyota_diag_registry(
        gts, args.region, args.family,
        native_history=args.native_history, history_known=args.native_context != "unknown",
    )
    if args.out:
        out = Path(args.out)
        write_toyota_diag_registry(payload, out, compact=args.compact)
        print(out)
    else:
        sys.stdout.write(render.registry_json_text(payload, compact=args.compact))
    return 0

def cmd_bundle(args: argparse.Namespace) -> int:
    bundle = DiagnosticBundle(args.bundle)
    if args.bundle_action == "list":
        if args.json:
            print(json.dumps(bundle.manifest, indent=2))
        else:
            for member in bundle.members:
                print(f"{member['name']}\t{member['bytes']}\t{member['sha256']}")
    elif args.bundle_action == "read":
        if args.path:
            selected = vdas_json_path(bundle.json(args.member), args.path)
            render.vdas_value(selected, as_json=True)
        else:
            with bundle.open(args.member) as source:
                shutil.copyfileobj(source, sys.stdout.buffer, length=1024 * 1024)
    elif args.bundle_action == "export":
        bundle.export_zip(args.out)
        print(args.out)
    elif args.bundle_action == "verify":
        bundle.verify()
        if args.compare_zip:
            bundle.compare_zip(args.compare_zip)
        print(f"{len(bundle.members)} members verified" + ("; ZIP member bytes/order match" if args.compare_zip else ""))
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
    _native_common(p)
    p.set_defaults(func=cmd_active_test)

    p = sub.add_parser("command", help="resolve one category+role into plugin, wire frames, timers, and recovered semantics")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("role", help="DLL role ID (decimal or 0x-prefixed hex)")
    p.add_argument("--item", help="selected direct Active Test ID for role 0x08 (decimal or 0x-prefixed hex)")
    _native_common(p)
    p.set_defaults(func=cmd_command)

    p = sub.add_parser("timer", help="decode Toyota master per-category command timers")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("timer", nargs="?", help="timer ID (decimal or 0x-prefixed hex); omit to list category timers")
    p.add_argument("--limit", type=int, default=100)
    _native_common(p, raw=True)
    p.set_defaults(func=cmd_timer)

    p = sub.add_parser("commset", help="decode Toyota master communication-set timeout/retry metadata")
    p.add_argument("comm_set", nargs="?", help="CommSet ID (decimal or 0x-prefixed hex); omit to list all")
    p.add_argument("--limit", type=int, default=100)
    _native_common(p, raw=True)
    p.set_defaults(func=cmd_commset)

    p = sub.add_parser("role", help="summarize Toyota master DLL roles and their plugin families")
    p.add_argument("role", nargs="?", help="DLL role ID (decimal or 0x-prefixed hex); omit for census")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--plugin-limit", type=int, default=8)
    _native_common(p, raw=True)
    p.set_defaults(func=cmd_role)

    p = sub.add_parser("category", help="resolve a Toyota master ECU category, its command plugins, and functions")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("--limit", type=int, default=100)
    _native_common(p, raw=True)
    p.set_defaults(func=cmd_category)

    p = sub.add_parser("registry", help="derive a clean Toyota diagnostic registry/bundle for Comma-side tooling")
    p.add_argument(
        "profile", nargs="?", default="camry-2026-f33",
        choices=("camry-2026-f33", TOYOTA_DIAG_BUNDLE_PROFILE),
        help="camry-2026-f33 legacy single-vehicle JSON or toyota-current canonical regional bundle directory",
    )
    p.add_argument("--out", help="write registry JSON (.gz for deterministic gzip) or bundle to this path")
    p.add_argument("--compact", action="store_true", help="omit JSON whitespace (independent of gzip output)")
    _native_common(p)
    p.set_defaults(func=cmd_registry)

    p = sub.add_parser("bundle", help="read, verify, or export tracked diagnostic members without GTS+")
    p.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE, help="canonical gzip-member directory")
    actions = p.add_subparsers(dest="bundle_action", required=True)
    action = actions.add_parser("list", help="list exact member names, sizes, and SHA-256 hashes")
    action.add_argument("--json", action="store_true")
    action = actions.add_parser("read", help="stream one original member or inspect its JSON path")
    action.add_argument("member")
    action.add_argument("--path", help="case-insensitive dotted JSON path")
    action = actions.add_parser("export", help="generate a portable distribution ZIP on demand")
    action.add_argument("--out", type=Path, default=DEFAULT_BUNDLE_ZIP)
    action = actions.add_parser("verify", help="verify all canonical members, optionally against an original ZIP")
    action.add_argument("--compare-zip", type=Path)
    p.set_defaults(func=cmd_bundle)

    p = sub.add_parser("canbus", help="resolve Toyota master CAN Bus Check topology for a vehicle type/name")
    p.add_argument("vehicle", help="vehicle type ID (decimal/0x) or OEM vehicle-name substring")
    _native_common(p)
    p.set_defaults(func=cmd_canbus)

    p = sub.add_parser("frame", help="resolve master FuncCommFrame selector(s) to current send/mask/check bytes")
    p.add_argument("category", help="category ID, database/short name, or OEM ECU name")
    p.add_argument("selector", nargs="?", help="selector ID (decimal or 0x-prefixed hex); omit to list all")
    p.add_argument("--limit", type=int, default=100)
    _native_common(p, raw=True)
    p.set_defaults(func=cmd_frame)

    p = sub.add_parser(
        "did", help="resolve ECU Data List / alternate snapshot DIDs (not PCS recorder IDs)",
        description="Resolve DDB monitor rows and reference keys. Use --json for full scaling and enum labels. "
                    "PCS recorder fields use the separate 'recorder' command.",
    )
    p.add_argument("ecu")
    p.add_argument("query", nargs="?", help="primary/alternate DID (hex) or OEM-name substring")
    p.add_argument("--limit", type=int, default=100)
    _common(p)
    p.set_defaults(func=cmd_did)

    p = sub.add_parser(
        "recorder", help="inspect recovered PCS recorder field schemas (TSS3 or ADU)",
        description="Read tracked PCS viewer field definitions; no external GTS installation is needed. "
                    "Byte/bit positions belong to recorder records.",
    )
    p.add_argument("query", nargs="?", help="record ID (four hex digits or 0x-prefixed) or field-name substring")
    p.add_argument("--schema", choices=("tss3", "adu"), default="tss3", help="recorder schema, kept separate (default: tss3)")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--json", action="store_true", help="emit source identities and complete field definitions")
    p.set_defaults(func=cmd_recorder)

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
    try:
        return int(args.func(args))
    except (NativeSelectionError, UnresolvedNativeContext) as exc:
        result = getattr(exc, "result", None)
        payload = {
            "error": type(exc).__name__, "message": str(exc),
            "status": getattr(exc, "status", None),
            "query": result.as_dict() if result is not None else None,
            "native_context": args.native_selection.as_dict() if hasattr(args, "native_selection") else None,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 2
        raise SystemExit(f"{type(exc).__name__}: {exc}") from exc
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc



if __name__ == "__main__":
    raise SystemExit(main())
