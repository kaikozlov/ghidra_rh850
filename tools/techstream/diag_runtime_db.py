"""Indexed runtime database projection of the canonical Toyota diagnostic bundle."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Any

from tools import REPO_ROOT
from tools.techstream.diag_bundle import DEFAULT_BUNDLE, DiagnosticBundle

DEFAULT_OUTPUT = REPO_ROOT / "build/out/toyota_diag.sqlite"
SCHEMA = "toyota-diagnostics-sqlite-v1"
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
CREATE INDEX items_owner ON items(region, category_id, kind, identifier);
CREATE VIRTUAL TABLE items_fts USING fts5(
  name, detail, identifier, content='items', content_rowid='id',
  tokenize='unicode61', prefix='2 3 4'
);
"""


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _category_key(category_id: int, category: dict[str, Any]) -> str:
    if category_id in ALIASES:
        return ALIASES[category_id]
    source = str(category.get("short_name") or Path(str(category.get("database") or "")).stem or f"category_{category_id}")
    source = re.sub(r"_P[456].*$", "", source, flags=re.IGNORECASE)
    return re.sub(r"[^0-9A-Za-z]+", "_", source).strip("_").casefold() or f"category_{category_id}"


def _category_keys(categories: dict[str, dict[str, Any]]) -> dict[int, str]:
    counts: dict[str, int] = {}
    keys: dict[int, str] = {}
    for raw_id, category in categories.items():
        category_id = int(raw_id)
        key = _category_key(category_id, category)
        keys[category_id] = key
        counts[key] = counts.get(key, 0) + 1
    reserved = set(ALIASES.values())
    for category_id, key in list(keys.items()):
        if category_id not in ALIASES and (key in reserved or counts[key] > 1):
            keys[category_id] = f"{key}_{category_id}"
    return keys


def _catalog_rows(region: str, category_id: int, catalog: dict[str, Any]):
    for did, signals in catalog.get("dids", {}).items():
        for signal in signals:
            yield region, category_id, "did", did, str(signal.get("name") or did), ""
    for packed, dtcs in catalog.get("dtcs", {}).items():
        for dtc in dtcs:
            ident = str(dtc.get("code") or packed)
            yield region, category_id, "dtc", ident, str(dtc.get("description") or ident), str(dtc.get("failure") or "")
    for row in catalog.get("active_tests", []):
        ident = f"0x{int(row.get('id', 0)):04X}"
        detail = f"{row.get('kind') or ''} {row.get('execution') or ''}".strip()
        yield region, category_id, "active-test", ident, str(row.get("name") or ident), detail
    for row in catalog.get("functions", []):
        ident = str(row.get("id") or row.get("function_id") or "")
        if row.get("detail_id") is not None:
            ident += f"/{row['detail_id']}"
        name = str(row.get("name") or row.get("detail_name") or ident)
        yield region, category_id, "function", ident, name, str(row.get("semantic_kind") or "")
    for row in catalog.get("plugins", []):
        role = row.get("role") or row.get("id") or 0
        ident = f"0x{role:02X}" if isinstance(role, int) else str(role)
        name = str(row.get("dll") or row.get("plugin") or ident)
        yield region, category_id, "plugin", ident, name, str(row.get("semantic_kind") or "")
    for row in catalog.get("utilities", []):
        ident = str(row.get("id") or row.get("routine_id") or "")
        yield region, category_id, "utility", ident, str(row.get("name") or ident), str(row.get("execution") or "")


def _supplemental_rows(index: dict[str, Any], generated_root: Path):
    regions = tuple(index["regions"])
    tss3_path = generated_root / "pcs_data_viewer_tss3_managed_semantics.json"
    adu_path = generated_root / "pcs_data_viewer_adu_semantics.json"
    if not tss3_path.is_file() or not adu_path.is_file():
        return
    tss3 = json.loads(tss3_path.read_text())
    for row in tss3["operation_ffd"]["detail_rows"]:
        data_id = str(row.get("DataID") or "")
        if data_id in ("", "-"):
            continue
        for region in regions:
            yield region, 498, "ffd-signal", f"0x{data_id.upper()}", str(row.get("DataName") or ""), "TSS3 Operation FFD"
    for row in tss3["rob_codes"]["rows"]:
        rob = str(row.get("rob_code") or "")
        for region in regions:
            yield region, 498, "ffd-rob", f"0x{rob.upper()}", str(row.get("DataName") or ""), f"{row.get('SystemName') or ''} Operation FFD trigger".strip()
    adu = json.loads(adu_path.read_text())
    for row in adu["adu"]["rows"]:
        data_id = str(row.get("DataID") or "")
        if data_id in ("", "-"):
            continue
        for region in regions:
            yield region, 0, "adu-signal", f"0x{data_id.upper()}", str(row.get("DataName") or ""), "ADAS Domain Controller recorder"


def export_runtime_db(bundle_path: Path = DEFAULT_BUNDLE, out: Path = DEFAULT_OUTPUT) -> dict[str, int | str]:
    bundle = DiagnosticBundle(bundle_path)
    bundle.verify()
    index = bundle.json("index.json")
    if index.get("schema") != SOURCE_SCHEMA:
        raise ValueError(f"unsupported diagnostic source schema {index.get('schema')!r}")

    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = out.with_name(f".{out.name}.tmp")
    temporary.unlink(missing_ok=True)
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

        insert_item = "INSERT INTO items(region,category_id,kind,identifier,name,detail) VALUES (?,?,?,?,?,?)"
        item_count = 0
        for region, region_index in index["regions"].items():
            categories = region_index["selected_categories"]
            keys = _category_keys(categories)
            for binding in (region_index.get("utilities") or {}).get("bindings", []):
                role = int(binding["role"])
                name = str(binding.get("semantic_kind") or binding.get("dll") or "")
                db.execute(insert_item, (region, 0, "utility-family", f"0x{role:02X}", name, str(binding.get("dll") or "")))
                item_count += 1
            for vehicle in region_index["vehicles"].values():
                vehicle_type = int(vehicle["vehicle_type"])
                db.execute("INSERT INTO vehicles VALUES (?,?,?,?)", (
                    region, vehicle_type, str(vehicle.get("name") or ""), _json(vehicle.get("install_set_ids") or [])))
                db.execute(insert_item, (region, 0, "vehicle", str(vehicle_type), str(vehicle.get("name") or f"Vehicle {vehicle_type}"), ""))
                item_count += 1
                for set_id in vehicle.get("install_set_ids") or []:
                    for install in region_index["install_sets"].get(str(set_id), []):
                        route = region_index["routes"].get(str(install.get("route_key"))) or {}
                        db.execute("INSERT OR IGNORE INTO vehicle_ecus VALUES (?,?,?,?,?,?,?,?,?,?)", (
                            region, vehicle_type, int(set_id), int(install["category_id"]),
                            int(install["connection_route_selector"]), int(install["connection_frame_id"]),
                            install.get("route_key"), route.get("physical_request_address"),
                            route.get("address_extension"), route.get("transport_kind")))
            for raw_id, category in categories.items():
                category_id = int(raw_id)
                member = category.get("catalog_member")
                counts = {"dids": 0, "signals": 0, "dtcs": 0, "active_tests": 0, "functions": 0, "plugins": 0, "utilities": 0}
                if member:
                    catalog = bundle.json(str(member))
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
                    db.executemany(insert_item, rows)
                    item_count += len(rows)
                key = keys[category_id]
                name = str(category.get("name") or category.get("short_name") or f"Category {category_id}")
                db.execute("INSERT INTO ecus VALUES (?,?,?,?,?,?,?,?,?)", (
                    region, category_id, key, name, str(category.get("database") or ""),
                    category.get("generation"), category.get("support_mode"), member, _json(counts)))
                db.execute(insert_item, (region, category_id, "ecu", str(category_id), name,
                                         f"{key} {category.get('database') or ''}".strip()))
                item_count += 1

        supplemental = list(_supplemental_rows(index, bundle_path.parent))
        db.executemany(insert_item, supplemental)
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
