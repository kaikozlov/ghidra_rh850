"""Indexed runtime database projection of the canonical Toyota diagnostic bundle."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import zlib
from typing import Any

from tools import REPO_ROOT
from tools.techstream.diag_bundle import DEFAULT_BUNDLE, DiagnosticBundle

DEFAULT_OUTPUT = REPO_ROOT / "build/out/toyota_diag.sqlite"
# Supplements are repository artifacts, independent of candidate bundle location.
DEFAULT_SUPPLEMENTAL_ROOT = DEFAULT_BUNDLE.parent
SUPPLEMENTAL_FILES = ("pcs_data_viewer_tss3_managed_semantics.json", "pcs_data_viewer_adu_semantics.json")
SCHEMA = "toyota-diagnostics-sqlite-v2"
SOURCE_SCHEMA = "toyota-diagnostics-bundle-v4"

ALIASES = {
    372: "engine", 395: "motor_generator", 397: "hybrid", 398: "hv_battery",
    405: "eps", 409: "meter", 435: "brake", 450: "air_conditioner", 498: "frc",
}

DDL = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE vehicles (
  region TEXT NOT NULL, vehicle_type INTEGER NOT NULL, name TEXT NOT NULL,
  install_set_ids TEXT NOT NULL,
  PRIMARY KEY(region, vehicle_type)
) WITHOUT ROWID;
CREATE INDEX vehicles_name ON vehicles(region, name COLLATE NOCASE);
CREATE TABLE vehicle_ecus (
  region TEXT NOT NULL, vehicle_type INTEGER NOT NULL, install_set_id INTEGER NOT NULL,
  category_id INTEGER NOT NULL, route_selector INTEGER NOT NULL,
  connection_frame_id INTEGER NOT NULL, route_key TEXT,
  request_address INTEGER, address_extension INTEGER, transport_kind TEXT,
  PRIMARY KEY(region, vehicle_type, install_set_id, category_id, route_selector, connection_frame_id)
) WITHOUT ROWID;
CREATE TABLE ecus (
  region TEXT NOT NULL, category_id INTEGER NOT NULL, key TEXT NOT NULL,
  name TEXT NOT NULL, database_name TEXT NOT NULL, generation INTEGER,
  support_mode TEXT, catalog_member TEXT, counts TEXT NOT NULL,
  PRIMARY KEY(region, category_id)
) WITHOUT ROWID;
CREATE INDEX ecus_key ON ecus(region, key COLLATE NOCASE);
CREATE TABLE items (
  id INTEGER PRIMARY KEY,
  region TEXT NOT NULL, category_id INTEGER NOT NULL, kind TEXT NOT NULL,
  identifier TEXT NOT NULL, name TEXT NOT NULL, detail TEXT NOT NULL
);
CREATE TABLE item_payloads (item_id INTEGER PRIMARY KEY REFERENCES items(id), data BLOB NOT NULL);
CREATE INDEX items_owner ON items(region, category_id, kind, identifier);
CREATE TABLE catalog_sources (
 region TEXT NOT NULL, category_id INTEGER NOT NULL, member TEXT NOT NULL,
 metadata TEXT NOT NULL, PRIMARY KEY(region, category_id, member)
) WITHOUT ROWID;
CREATE TABLE item_sources (
 item_id INTEGER PRIMARY KEY REFERENCES items(id), member TEXT NOT NULL, pointer TEXT NOT NULL
);
CREATE INDEX item_sources_member ON item_sources(member, pointer);
CREATE VIEW item_counts AS SELECT region, category_id, kind, count(*) AS count
 FROM items GROUP BY region, category_id, kind;
CREATE VIRTUAL TABLE items_fts USING fts5(
  name, detail, identifier, content='items', content_rowid='id',
  tokenize='unicode61', prefix='2 3 4'
);
"""


_REPO_PREFIX = re.compile(re.escape(str(REPO_ROOT)) + r"/?")


def _json(value: Any) -> str:
    # Defense in depth: artifacts from older generators may embed workstation
    # paths; exported runtime payloads must only carry repo-relative paths.
    return _REPO_PREFIX.sub("", json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True))


def _category_key(category_id: int, category: dict[str, Any]) -> str:
    if category_id in ALIASES:
        return ALIASES[category_id]
    source = str(category.get("short_name") or Path(str(category.get("database") or "")).stem or f"category_{category_id}")
    source = re.sub(r"_P[3456].*$", "", source, flags=re.IGNORECASE)
    return re.sub(r"[^0-9A-Za-z]+", "_", source).strip("_").casefold() or f"category_{category_id}"


def _category_keys(categories: dict[str, dict[str, Any]]) -> dict[int, str]:
    counts: dict[str, int] = {}
    keys: dict[int, str] = {}
    for raw_id, category in sorted(categories.items(), key=lambda pair: int(pair[0])):
        category_id = int(raw_id)
        key = _category_key(category_id, category)
        keys[category_id] = key
        counts[key] = counts.get(key, 0) + 1
    reserved = set(ALIASES.values())
    for category_id, key in list(keys.items()):
        if category_id not in ALIASES and (key in reserved or counts[key] > 1):
            keys[category_id] = f"{key}_{category_id}"
    return keys


def _pointer(*parts: Any) -> str:
    return "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in parts)


# Explicit source collection registry: no recursive JSON-to-item guessing.
# Row payloads remain exact canonical objects; identities include source ordinals.
SOURCE_COLLECTIONS = {
    "p6_rob_source": ("behavior_codes", "signals"),
    "native_ddr": ("monitors", "triggers", "addresses", "invalid_conditions", "header_data_ids", "case_data_ids"),
    "ddr_behavior": ("codes", "signals", "invalid_conditions"),
    "trigger_catalog": ("trigger_items", "trigger_retrieval", "dtc_group_retrieval", "predictive_ffd_vehicle_dids"),
    "active_test_support": ("data_id_definitions", "support_conditions", "panel_support", "routine_status",
                            "display_patterns", "description_patterns", "result_patterns", "routine_support_conditions"),
    "variable_drive": ("active_tests", "communication_data", "pid_addition_frames", "active_test_communication_modes"),
    "obd_monitor": ("statuses", "detail_links", "results", "scalings", "legacy_statuses",
                    "legacy_detail_links", "legacy_results", "legacy_scalings", "iso_results",
                    "oxygen_sensors", "multi_pid_dependencies", "mode05_tests", "mode06_tests",
                    "mode06_mids", "test_monitors"),
    "diagnostic_metadata": ("details", "highlights", "expanded_dtcs", "pending_freeze", "operation_freeze"),
    "physical_catalog": ("physical", "patterns", "units"),
    "ddr": ("triggers", "data_ids", "signals", "invalid_conditions"),
    "work_factor": ("standard_info", "work_factor_patterns", "work_factor_items", "work_factor_signals",
                    "work_factor_rob_items", "work_factor_operation_codes", "work_factor_network_status",
                    "factor_data", "work_factor_p5_signals"),
}
SOURCE_LISTS = ("monitor_source", "dtc_source", "dynamic_lsb", "active_test_source")
ROB_COLLECTIONS = ("behavior_codes", "identifiers", "support_queries", "signals", "signal_checks")


def _source_collection_rows(region: str, category_id: int, catalog: dict[str, Any]):
    def emit(kind, path, rows):
        if not isinstance(rows, list):
            raise ValueError(f"source collection {_pointer(*path)} must be a list")
        for ordinal, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(f"source record {_pointer(*path, ordinal)} must be an object")
            identifier = f"{row['table']}:{row['record']}" if "table" in row and "record" in row else str(ordinal)
            name = str(row.get("name") or row.get("description") or row.get("standard_value") or row.get("code") or identifier)
            detail = " ".join(str(row[key]) for key in ("family", "semantics", "execution", "decoder", "standard_value_status")
                              if row.get(key) is not None)
            yield region, category_id, kind, identifier, name, detail, _json(row), _pointer(*path, ordinal)

    for section, fields in SOURCE_COLLECTIONS.items():
        for field in fields:
            yield from emit((section + "-" + field).replace("_", "-"), (section, field),
                            catalog.get(section, {}).get(field, []))
    for field in SOURCE_LISTS:
        yield from emit(field.replace("_", "-"), (field,), catalog.get(field, []))
    rob = catalog.get("legacy_rob", {})
    if "signal_checks" in rob:
        yield from emit("legacy-rob-signal-checks", ("legacy_rob", "signal_checks"), rob["signal_checks"])
    for family_index, family in enumerate(rob.get("families", [])):
        for field in ROB_COLLECTIONS:
            if field == "signal_checks" and "signal_checks" in rob:
                continue
            yield from emit("legacy-rob-" + field.replace("_", "-"),
                            ("legacy_rob", "families", family_index, field), family.get(field, []))


def _source_metadata(catalog: dict[str, Any]) -> dict[str, Any]:
    metadata = {key: value for key, value in catalog.items() if key in (
        "schema", "source_identity", "selection_boundary", "boundary",
        "semantics", "coverage", "decode_status", "source_tables",
    )}
    # Retain per-decoder runtime boundaries and request defaults without copying
    # entire source-row arrays into metadata a second time.
    sections = {}
    for section, row_fields in SOURCE_COLLECTIONS.items():
        if section in catalog:
            extra = {key: value for key, value in catalog[section].items() if key not in row_fields}
            if extra:
                sections[section] = extra
    rob = catalog.get("legacy_rob", {})
    if rob.get("families"):
        sections["legacy_rob"] = {"families": [
            {key: value for key, value in family.items() if key not in ROB_COLLECTIONS}
            for family in rob["families"]
        ]}
    if sections:
        metadata["sections"] = sections
    return metadata


def _semantic_rows(region: str, category_id: int, catalog: dict[str, Any]):
    # Distinct presentation, snapshot and ROB semantics may share a DID.
    # Nested frames and choices stay with their owner, not duplicate items.
    collections = (
        ("data-list", ("data_list", "rows"), ("did", "monitor_key"), ("unit",)),
        ("generic-ffd-signal", ("generic_ffd", "signals"), ("snapshot_did", "primary_did", "monitor_key"), ()),
        ("rob-code", ("rob", "behavior_codes"), ("signature", "behavior_code"), ("comment",)),
        ("rob-signal", ("rob", "signals"), ("did", "record_key"), ()),
        ("command", ("commands",), ("kind", "role"), ("execution",)),
        ("selector", ("selectors",), ("selector",), ()),
        ("active-test-group", ("active_test_groups", "groups"), ("group_id", "id"), ("execution",)),
        ("signal-group", ("support_catalog", "signal_groups"), ("group_id",), ()),
        ("signal-membership", ("support_catalog", "signal_memberships"), ("list_key", "identifier"), ()),
        ("support-query", ("support_catalog", "support_queries"), ("query_id",), ("kind",)),
        ("freeze-frame-query", ("support_catalog", "freeze_frame_queries"), ("freeze_frame_number",), ()),
    )
    for kind, path, identifiers, details in collections:
        rows: Any = catalog
        for part in path:
            rows = rows.get(part, {}) if isinstance(rows, dict) else {}
        for ordinal, row in enumerate(rows if isinstance(rows, list) else []):
            identifier = next((str(row[key]) for key in identifiers if row.get(key) is not None), str(ordinal))
            name = str(row.get("name") or row.get("kind") or identifier)
            detail = " ".join(str(row[key]) for key in details if row.get(key) is not None)
            yield region, category_id, kind, identifier, name, detail, _json(row), _pointer(*path, ordinal)


def _customize_rows(region: str, catalog: dict[str, Any]):
    for field, kind, keys in (
        ("groups", "customize-group", ("group_id", "body_type")),
        ("items", "customize-item", ("group_id", "item_id")),
        ("body_type_probes", "customize-probe", ("body_type", "lookup_key")),
    ):
        for ordinal, row in enumerate(catalog.get(field, [])):
            identifier = "/".join(str(row[key]) for key in keys if row.get(key) is not None)
            owner = int(row.get("target_category_id") or 0)
            yield region, owner, kind, identifier, str(row.get("name") or identifier), "", _json(row), _pointer(field, ordinal)


def _catalog_rows(region: str, category_id: int, catalog: dict[str, Any]):
    yield from _semantic_rows(region, category_id, catalog)
    yield from _source_collection_rows(region, category_id, catalog)
    for ordinal, row in enumerate(catalog.get("legacy_records", [])):
        # Legacy protocol-specific schemas stay distinct from P5 DID signals.
        # Parameter/request metadata does not authorize actuator execution.
        kind = "legacy-" + str(row["kind"]).replace("_", "-")
        identifier = f"{row['table']}:{row['record']}"
        detail = str(row.get("semantic_status") or row.get("native_status")
                     or row.get("execution") or row.get("layout") or "")
        yield region, category_id, kind, identifier, str(row.get("name") or identifier), detail, _json(row), _pointer("legacy_records", ordinal)
    for did, signals in sorted(catalog.get("dids", {}).items()):
        for ordinal, signal in enumerate(signals):
            yield region, category_id, "did", did, str(signal.get("name") or did), str(signal.get("unit") or ""), _json(signal), _pointer("dids", did, ordinal)
    for packed, dtcs in sorted(catalog.get("dtcs", {}).items()):
        for ordinal, dtc in enumerate(dtcs):
            ident = str(dtc.get("code") or packed)
            yield region, category_id, "dtc", ident, str(dtc.get("description") or ident), str(dtc.get("failure") or ""), _json(dtc), _pointer("dtcs", packed, ordinal)
    for ordinal, row in enumerate(catalog.get("active_tests", [])):
        ident = f"0x{int(row.get('id', 0)):04X}"
        detail = f"{row.get('kind') or ''} {row.get('execution') or ''}".strip()
        yield region, category_id, "active-test", ident, str(row.get("name") or ident), detail, _json(row), _pointer("active_tests", ordinal)
    for ordinal, row in enumerate(catalog.get("functions", [])):
        ident = str(row.get("id") or row.get("function_id") or "")
        if row.get("detail_id") is not None:
            ident += f"/{row['detail_id']}"
        name = str(row.get("name") or row.get("detail_name") or ident)
        yield region, category_id, "function", ident, name, str(row.get("semantic_kind") or ""), _json(row), _pointer("functions", ordinal)
    for ordinal, row in enumerate(catalog.get("plugins", [])):
        role = row.get("role") or row.get("id") or 0
        ident = f"0x{role:02X}" if isinstance(role, int) else str(role)
        name = str(row.get("dll") or row.get("plugin") or ident)
        yield region, category_id, "plugin", ident, name, str(row.get("semantic_kind") or ""), _json(row), _pointer("plugins", ordinal)
    for ordinal, row in enumerate(catalog.get("utilities", [])):
        ident = str(row.get("id") or row.get("routine_id") or "")
        yield region, category_id, "utility", ident, str(row.get("name") or ident), str(row.get("execution") or ""), _json(row), _pointer("utilities", ordinal)


def _supplemental_source(path: Path) -> dict[str, str]:
    """Stable source identity without leaking workstation directories."""
    try:
        relative = path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        return {"path":relative, "uri":"repo://" + relative, "path_scope":"repository"}
    except ValueError:
        return {"path":path.name, "uri":"supplement://" + path.name, "path_scope":"supplemental_root"}


def _supplemental_rows(index: dict[str, Any], generated_root: Path, *, documents: dict[str, Any] | None = None):
    regions = tuple(sorted(index["regions"]))
    tss3_path = generated_root / "pcs_data_viewer_tss3_managed_semantics.json"
    adu_path = generated_root / "pcs_data_viewer_adu_semantics.json"
    documents = documents if documents is not None else {
        name: json.loads((generated_root / name).read_bytes())
        for name in SUPPLEMENTAL_FILES if (generated_root / name).is_file()
    }
    tss3 = documents.get(tss3_path.name, {})
    for ordinal, row in enumerate(tss3.get("operation_ffd", {}).get("detail_rows", [])):
        data_id = str(row.get("DataID") or "")
        if data_id in ("", "-"):
            continue
        for region in regions:
            yield region, 498, "ffd-signal", f"0x{data_id.upper()}", str(row.get("DataName") or ""), "TSS3 Operation FFD", _json(row), _pointer("operation_ffd", "detail_rows", ordinal), _supplemental_source(tss3_path)["uri"]
    for ordinal, row in enumerate(tss3.get("rob_codes", {}).get("rows", [])):
        rob = str(row.get("rob_code") or "")
        for region in regions:
            yield region, 498, "ffd-rob", f"0x{rob.upper()}", str(row.get("DataName") or ""), f"{row.get('SystemName') or ''} Operation FFD trigger".strip(), _json(row), _pointer("rob_codes", "rows", ordinal), _supplemental_source(tss3_path)["uri"]
    adu = documents.get(adu_path.name, {})
    for ordinal, row in enumerate(adu.get("adu", {}).get("rows", [])):
        data_id = str(row.get("DataID") or "")
        if data_id in ("", "-"):
            continue
        for region in regions:
            yield region, 0, "adu-signal", f"0x{data_id.upper()}", str(row.get("DataName") or ""), "ADAS Domain Controller recorder", _json(row), _pointer("adu", "rows", ordinal), _supplemental_source(adu_path)["uri"]


def export_runtime_db(bundle_path: Path = DEFAULT_BUNDLE, out: Path = DEFAULT_OUTPUT, *,
                      supplemental_root: Path | None = None) -> dict[str, int | str]:
    """Project a bundle plus pinned repository supplements.

    supplemental_root defaults to data/generated/gtsplus_2026, never the input
    bundle parent. Pass an explicit directory to select another supplement set.
    Missing files are recorded explicitly in meta.supplemental_sources.
    """
    supplemental_root = Path(supplemental_root) if supplemental_root is not None else DEFAULT_SUPPLEMENTAL_ROOT
    documents = {}
    supplemental_sources = []
    for name in SUPPLEMENTAL_FILES:
        path = (supplemental_root / name).resolve()
        source = {**_supplemental_source(path), "status":"missing"}
        if path.is_file():
            data = path.read_bytes()
            documents[name] = json.loads(data)
            source.update(status="loaded", sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        supplemental_sources.append(source)
    bundle = DiagnosticBundle(bundle_path)
    bundle.verify()
    index = bundle.json("index.json")
    if index.get("schema") != SOURCE_SCHEMA:
        raise ValueError(f"unsupported diagnostic source schema {index.get('schema')!r}")

    out.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{out.name}.", suffix=".tmp", dir=out.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    db = sqlite3.connect(temporary)
    try:
        db.execute("PRAGMA journal_mode=OFF")
        db.execute("PRAGMA synchronous=OFF")
        db.execute("PRAGMA temp_store=MEMORY")
        db.executescript(DDL)
        for key, value in {
            "schema": SCHEMA,
            "source_schema": SOURCE_SCHEMA,
            "release": str(index.get("release") or ""),
            "default_region": str(index.get("default_region") or "NA"),
            "member_count": str(len(bundle.members)),
        }.items():
            db.execute("INSERT INTO meta VALUES (?, ?)", (key, value))

        def insert_item(row: tuple, member: str | None = None) -> None:
            cursor = db.execute("INSERT INTO items(region,category_id,kind,identifier,name,detail) VALUES (?,?,?,?,?,?)", row[:6])
            # Keep summaries compact; inflate one source record only when inspected.
            db.execute("INSERT INTO item_payloads VALUES (?, ?)",
                       (cursor.lastrowid, zlib.compress(row[6].encode("utf-8"))))
            if member is not None:
                db.execute("INSERT INTO item_sources VALUES (?,?,?)",
                           (cursor.lastrowid, member, row[7] if len(row) > 7 else ""))

        def insert_source(region: str, category_id: int, member: str, catalog: dict[str, Any]) -> None:
            # Retain boundaries and source identity, not another full catalog copy.
            metadata = _source_metadata(catalog)
            db.execute("INSERT INTO catalog_sources VALUES (?,?,?,?)",
                       (region, category_id, member, _json(metadata)))

        item_count = 0
        for region, region_index in sorted(index["regions"].items()):
            categories = region_index["selected_categories"]
            keys = _category_keys(categories)
            customize_member = region_index.get("customize_member")
            if customize_member:
                customize = bundle.json(str(customize_member))
                insert_source(region, 0, str(customize_member), customize)
                for row in _customize_rows(region, customize):
                    insert_item(row, str(customize_member))
                    item_count += 1
            for binding in (region_index.get("utilities") or {}).get("bindings", []):
                role = int(binding["role"])
                name = str(binding.get("semantic_kind") or binding.get("dll") or "")
                insert_item((region, 0, "utility-family", f"0x{role:02X}", name, str(binding.get("dll") or ""), _json(binding)))
                item_count += 1
            for vehicle in sorted(region_index["vehicles"].values(), key=lambda row: int(row["vehicle_type"])):
                vehicle_type = int(vehicle["vehicle_type"])
                db.execute("INSERT INTO vehicles VALUES (?,?,?,?)", (
                    region, vehicle_type, str(vehicle.get("name") or ""), _json(vehicle.get("install_set_ids") or [])))
                insert_item((region, 0, "vehicle", str(vehicle_type), str(vehicle.get("name") or f"Vehicle {vehicle_type}"), "", _json(vehicle)))
                item_count += 1
                for set_id in vehicle.get("install_set_ids") or []:
                    for install in region_index["install_sets"].get(str(set_id), []):
                        route = region_index["routes"].get(str(install.get("route_key"))) or {}
                        db.execute("INSERT OR IGNORE INTO vehicle_ecus VALUES (?,?,?,?,?,?,?,?,?,?)", (
                            region, vehicle_type, int(set_id), int(install["category_id"]),
                            int(install["connection_route_selector"]), int(install["connection_frame_id"]),
                            install.get("route_key"), route.get("physical_request_address"),
                            route.get("address_extension"), route.get("transport_kind")))
            for raw_id, category in sorted(categories.items(), key=lambda pair: int(pair[0])):
                category_id = int(raw_id)
                member = category.get("catalog_member")
                counts = {"dids": 0, "signals": 0, "dtcs": 0, "active_tests": 0, "functions": 0, "plugins": 0, "utilities": 0}
                if member:
                    catalog = bundle.json(str(member))
                    insert_source(region, category_id, str(member), catalog)
                    counts = {
                        "dids": len(catalog.get("dids", {})),
                        "signals": sum(len(rows) for rows in catalog.get("dids", {}).values()),
                        "dtcs": sum(len(rows) for rows in catalog.get("dtcs", {}).values()),
                        "active_tests": len(catalog.get("active_tests", [])),
                        "functions": len(catalog.get("functions", [])),
                        "plugins": len(catalog.get("plugins", [])),
                        "utilities": len(catalog.get("utilities", [])),
                    }
                    rows = list(_catalog_rows(region, category_id, catalog))
                    for row in rows:
                        insert_item(row, str(member))
                    counts["items_by_kind"] = {kind: sum(row[2] == kind for row in rows) for kind in sorted({row[2] for row in rows})}
                    item_count += len(rows)
                key = keys[category_id]
                name = str(category.get("name") or category.get("short_name") or f"Category {category_id}")
                db.execute("INSERT INTO ecus VALUES (?,?,?,?,?,?,?,?,?)", (
                    region, category_id, key, name, str(category.get("database") or ""),
                    category.get("generation"), category.get("support_mode"), member, _json(counts)))
                insert_item((region, category_id, "ecu", str(category_id), name,
                                         f"{key} {category.get('database') or ''}".strip(), _json(category)))
                item_count += 1

        db.execute("INSERT INTO meta VALUES (?,?)", ("supplemental_sources", _json(supplemental_sources)))
        supplemental = list(_supplemental_rows(index, supplemental_root, documents=documents))
        for row in supplemental:
            insert_item(row, row[8])
        item_count += len(supplemental)
        db.execute("INSERT INTO items_fts(items_fts) VALUES ('rebuild')")
        db.execute("PRAGMA optimize")
        db.commit()
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("runtime SQLite integrity check failed")
    except BaseException:
        db.close()
        temporary.unlink(missing_ok=True)
        raise
    db.close()
    os.replace(temporary, out)
    return {"path": str(out), "bytes": out.stat().st_size, "members": len(bundle.members), "items": item_count}
