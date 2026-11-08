"""Indexed runtime database projection of the canonical Toyota diagnostic bundle."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import tempfile
import zlib
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.techstream import diag_codec as codec
from tools.techstream.diag_bundle import DEFAULT_BUNDLE, DiagnosticBundle
from tools.techstream.diag_customize_semantics import normalize as normalize_customize
from tools.techstream.diag_decoded_monitors import Store as DecodedMonitorStore
from tools.techstream.diag_ecu_configurations import (
    normalize as normalize_ecu_configurations,
)
from tools.techstream.diag_freeze_physical import normalize as normalize_freeze_physical
from tools.techstream.diag_operation_plans import PlanStore
from tools.techstream.diag_native_recorder import Store as NativeRecorderStore
from tools.techstream.diag_product_active import normalize as normalize_product_active
from tools.techstream.diag_product_behavior_codes import BehaviorCodeStore
from tools.techstream.diag_product_dtcs import DTCStore
from tools.techstream.diag_product_dtc_sources import SourceDTCStore
from tools.techstream.diag_product_freeze_signals import FreezeStore
from tools.techstream.diag_product_legacy_conditions import ConditionStore
from tools.techstream.diag_product_legacy_operations import OperationStore
from tools.techstream.diag_product_legacy_rob import Store as LegacyROBStore
from tools.techstream.diag_product_memberships import normalize as normalize_memberships
from tools.techstream.diag_product_projection import project_document
from tools.techstream.diag_product_recorder import Store as RecorderStore
from tools.techstream.diag_signal_observations import ObservationStore
from tools.techstream.diag_signal_records import normalize as normalize_signals
from tools.techstream.diag_support_semantics import SupportStore
from tools.techstream.diag_topology import normalize as normalize_topology
from tools.techstream.diag_vehicle_index import normalize as normalize_vehicle_index
from tools.techstream.diag_work_semantics import normalize as normalize_work_semantics

DEFAULT_OUTPUT = REPO_ROOT / "build/out/toyota_diag.sqlite"
# Supplements are repository artifacts, independent of candidate bundle location.
DEFAULT_SUPPLEMENTAL_ROOT = DEFAULT_BUNDLE.parent
SUPPLEMENTAL_FILES = (
    "pcs_data_viewer_tss3_managed_semantics.json",
    "pcs_data_viewer_adu_semantics.json",
    "tss3_native_recorder_protocol.json",
)
SCHEMA = "toyota-diagnostics-sqlite-v6"
SOURCE_SCHEMA = "toyota-diagnostics-bundle-v4"

ALIASES = {
    372: "engine",
    395: "motor_generator",
    397: "hybrid",
    398: "hv_battery",
    405: "eps",
    409: "meter",
    435: "brake",
    450: "air_conditioner",
    498: "frc",
}

DDL = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE vehicles (
  region TEXT NOT NULL, vehicle_type INTEGER NOT NULL, name TEXT NOT NULL,
  install_set_ids TEXT NOT NULL,
  PRIMARY KEY(region, vehicle_type)
) WITHOUT ROWID;
CREATE INDEX vehicles_name ON vehicles(region, name COLLATE NOCASE);
CREATE TABLE vehicle_install_sets (
 id INTEGER PRIMARY KEY,region_id INTEGER NOT NULL REFERENCES search_regions(id),
 vehicle_type INTEGER NOT NULL,install_set_id INTEGER NOT NULL,
 UNIQUE(region_id,vehicle_type,install_set_id)
);
CREATE TABLE transport_routes (
 id INTEGER PRIMARY KEY,route_key TEXT,request_address INTEGER,
 address_extension INTEGER,transport_kind TEXT
);
CREATE TABLE installed_ecus (
 install_id INTEGER NOT NULL REFERENCES vehicle_install_sets(id),
 category_id INTEGER NOT NULL,route_selector INTEGER NOT NULL,
 connection_frame_id INTEGER NOT NULL,route_id INTEGER NOT NULL REFERENCES transport_routes(id),
 PRIMARY KEY(install_id,category_id,route_selector,connection_frame_id)
) WITHOUT ROWID;
CREATE VIEW vehicle_ecus AS
 SELECT g.name AS region,s.vehicle_type,s.install_set_id,e.category_id,e.route_selector,
 e.connection_frame_id,r.route_key,r.request_address,r.address_extension,r.transport_kind
 FROM vehicle_install_sets s JOIN search_regions g ON g.id=s.region_id
 JOIN installed_ecus e ON e.install_id=s.id JOIN transport_routes r ON r.id=e.route_id;
CREATE TABLE ecus (
  region TEXT NOT NULL, category_id INTEGER NOT NULL, key TEXT NOT NULL,
  name TEXT NOT NULL, database_name TEXT NOT NULL, generation INTEGER,
  support_mode TEXT, catalog_member TEXT, counts TEXT NOT NULL,
  PRIMARY KEY(region, category_id)
) WITHOUT ROWID;
CREATE INDEX ecus_key ON ecus(region, key COLLATE NOCASE);
CREATE TABLE search_regions (id INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE);
CREATE TABLE search_kinds (id INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE);
CREATE TABLE text_values (id INTEGER PRIMARY KEY,value TEXT NOT NULL UNIQUE);
CREATE VIEW search_text AS SELECT id,value FROM text_values;
CREATE TABLE search_records (
 id INTEGER PRIMARY KEY,kind_id INTEGER NOT NULL REFERENCES search_kinds(id),
 identifier_id INTEGER NOT NULL REFERENCES text_values(id),
 name_id INTEGER NOT NULL REFERENCES text_values(id),
 detail_id INTEGER NOT NULL REFERENCES text_values(id)
);
CREATE UNIQUE INDEX search_records_value ON search_records(kind_id,identifier_id,name_id,detail_id);
CREATE TABLE item_occurrences (
 id INTEGER PRIMARY KEY,region_id INTEGER NOT NULL REFERENCES search_regions(id),
 category_id INTEGER NOT NULL,record_id INTEGER NOT NULL REFERENCES search_records(id),
 document_id INTEGER NOT NULL REFERENCES source_documents(id),
 pointer_id INTEGER NOT NULL REFERENCES source_pointers(id)
);
CREATE TABLE owner_ranges (
 region_id INTEGER NOT NULL REFERENCES search_regions(id),category_id INTEGER NOT NULL,
 first_id INTEGER NOT NULL,last_id INTEGER NOT NULL CHECK(last_id>=first_id),
 PRIMARY KEY(region_id,category_id,first_id)
) WITHOUT ROWID;
CREATE VIEW items AS SELECT o.id,g.name AS region,o.category_id,k.name AS kind,
 x.value AS identifier,n.value AS name,t.value AS detail
 FROM search_regions g CROSS JOIN item_occurrences o ON g.id=o.region_id
 JOIN search_records r ON r.id=o.record_id JOIN search_kinds k ON k.id=r.kind_id
 JOIN search_text x ON x.id=r.identifier_id JOIN search_text n ON n.id=r.name_id
 JOIN search_text t ON t.id=r.detail_id;
CREATE VIEW owner_items AS SELECT o.id,g.name AS region,r.category_id,k.name AS kind,
 x.value AS identifier,n.value AS name,t.value AS detail
 FROM search_regions g CROSS JOIN owner_ranges r ON r.region_id=g.id
 CROSS JOIN item_occurrences o NOT INDEXED ON o.id BETWEEN r.first_id AND r.last_id
 AND o.region_id=r.region_id AND o.category_id=r.category_id
 JOIN search_records s ON s.id=o.record_id JOIN search_kinds k ON k.id=s.kind_id
 JOIN search_text x ON x.id=s.identifier_id JOIN search_text n ON n.id=s.name_id
 JOIN search_text t ON t.id=s.detail_id;
CREATE TABLE source_documents (id INTEGER PRIMARY KEY, member TEXT NOT NULL UNIQUE, data BLOB NOT NULL);
CREATE VIEW runtime_documents AS SELECT member,data FROM source_documents;
CREATE VIEW source_members AS SELECT id,member FROM source_documents;
CREATE TABLE source_pointers (id INTEGER PRIMARY KEY, pointer TEXT NOT NULL UNIQUE);
CREATE TABLE source_document_parts (
 document_id INTEGER NOT NULL REFERENCES source_documents(id),
 pointer_id INTEGER NOT NULL REFERENCES source_pointers(id),
 data BLOB NOT NULL,
 PRIMARY KEY(document_id,pointer_id)
) WITHOUT ROWID;
CREATE VIEW item_source_refs AS SELECT id AS item_id,document_id AS member_id,pointer_id FROM item_occurrences;
CREATE VIEW item_sources AS SELECT o.id AS item_id,d.member,p.pointer
 FROM item_occurrences o JOIN source_documents d ON d.id=o.document_id
 JOIN source_pointers p ON p.id=o.pointer_id;
CREATE TABLE item_count_rows (
 region_id INTEGER NOT NULL REFERENCES search_regions(id),category_id INTEGER NOT NULL,
 kind_id INTEGER NOT NULL REFERENCES search_kinds(id),count INTEGER NOT NULL,
 PRIMARY KEY(region_id,category_id,kind_id)
) WITHOUT ROWID;
CREATE VIEW item_counts AS SELECT g.name AS region,c.category_id,k.name AS kind,c.count
 FROM item_count_rows c JOIN search_regions g ON g.id=c.region_id
 JOIN search_kinds k ON k.id=c.kind_id;
CREATE VIRTUAL TABLE items_fts USING fts5(
  name, detail, identifier, content='items', content_rowid='id',
  tokenize='unicode61'
);
"""


_REPO_PREFIX = re.compile(re.escape(str(REPO_ROOT)) + r"/?")


def _json(value: Any) -> str:
    # Defense in depth: artifacts from older generators may embed workstation
    # paths; exported runtime payloads must only carry repo-relative paths.
    return _REPO_PREFIX.sub(
        "", json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    )


def _category_key(category_id: int, category: dict[str, Any]) -> str:
    if category_id in ALIASES:
        return ALIASES[category_id]
    source = str(
        category.get("short_name")
        or Path(str(category.get("database") or "")).stem
        or f"category_{category_id}"
    )
    source = re.sub(r"_P[3456].*$", "", source, flags=re.IGNORECASE)
    return (
        re.sub(r"[^0-9A-Za-z]+", "_", source).strip("_").casefold()
        or f"category_{category_id}"
    )


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
    return "/" + "/".join(
        str(part).replace("~", "~0").replace("/", "~1") for part in parts
    )


# Explicit source collection registry: no recursive JSON-to-item guessing.
# Row payloads remain exact canonical objects; identities include source ordinals.
SOURCE_COLLECTIONS = {
    "p6_rob_source": ("behavior_codes", "signals"),
    "native_ddr": (
        "monitors",
        "triggers",
        "addresses",
        "invalid_conditions",
        "header_data_ids",
        "case_data_ids",
    ),
    "ddr_behavior": ("codes", "signals", "invalid_conditions"),
    "trigger_catalog": (
        "trigger_items",
        "trigger_retrieval",
        "dtc_group_retrieval",
        "predictive_ffd_vehicle_dids",
    ),
    "active_test_support": (
        "data_id_definitions",
        "support_conditions",
        "panel_support",
        "routine_status",
        "display_patterns",
        "description_patterns",
        "result_patterns",
        "routine_support_conditions",
    ),
    "variable_drive": (
        "active_tests",
        "communication_data",
        "pid_addition_frames",
        "active_test_communication_modes",
    ),
    "obd_monitor": (
        "statuses",
        "detail_links",
        "results",
        "scalings",
        "legacy_statuses",
        "legacy_detail_links",
        "legacy_results",
        "legacy_scalings",
        "iso_results",
        "oxygen_sensors",
        "multi_pid_dependencies",
        "mode05_tests",
        "mode06_tests",
        "mode06_mids",
        "test_monitors",
    ),
    "diagnostic_metadata": (
        "details",
        "highlights",
        "expanded_dtcs",
        "pending_freeze",
        "operation_freeze",
    ),
    "physical_catalog": ("physical", "patterns", "units"),
    "ddr": ("triggers", "data_ids", "signals", "invalid_conditions"),
    "work_factor": (
        "standard_info",
        "work_factor_patterns",
        "work_factor_items",
        "work_factor_signals",
        "work_factor_rob_items",
        "work_factor_operation_codes",
        "work_factor_network_status",
        "factor_data",
        "work_factor_p5_signals",
    ),
}
SOURCE_LISTS = ("monitor_source", "dtc_source", "dynamic_lsb", "active_test_source")
ROB_COLLECTIONS = (
    "behavior_codes",
    "identifiers",
    "support_queries",
    "signals",
    "signal_checks",
)


def _source_collection_rows(region: str, category_id: int, catalog: dict[str, Any]):
    def emit(kind, path, rows):
        if not isinstance(rows, list):
            raise ValueError(f"source collection {_pointer(*path)} must be a list")
        for ordinal, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(
                    f"source record {_pointer(*path, ordinal)} must be an object"
                )
            identifier = (
                f"{row['table']}:{row['record']}"
                if "table" in row and "record" in row
                else str(ordinal)
            )
            name = str(
                row.get("name")
                or row.get("description")
                or row.get("standard_value")
                or row.get("code")
                or identifier
            )
            detail = " ".join(
                str(row[key])
                for key in (
                    "family",
                    "semantics",
                    "execution",
                    "decoder",
                    "standard_value_status",
                )
                if row.get(key) is not None
            )
            yield (
                region,
                category_id,
                kind,
                identifier,
                name,
                detail,
                _json(row),
                _pointer(*path, ordinal),
            )

    for section, fields in SOURCE_COLLECTIONS.items():
        for field in fields:
            yield from emit(
                (section + "-" + field).replace("_", "-"),
                (section, field),
                catalog.get(section, {}).get(field, []),
            )
    for field in SOURCE_LISTS:
        yield from emit(field.replace("_", "-"), (field,), catalog.get(field, []))
    rob = catalog.get("legacy_rob", {})
    if "signal_checks" in rob:
        yield from emit(
            "legacy-rob-signal-checks",
            ("legacy_rob", "signal_checks"),
            rob["signal_checks"],
        )
    for family_index, family in enumerate(rob.get("families", [])):
        for field in ROB_COLLECTIONS:
            if field == "signal_checks" and "signal_checks" in rob:
                continue
            yield from emit(
                "legacy-rob-" + field.replace("_", "-"),
                ("legacy_rob", "families", family_index, field),
                family.get(field, []),
            )


def _semantic_rows(region: str, category_id: int, catalog: dict[str, Any]):
    # Distinct presentation, snapshot and ROB semantics may share a DID.
    # Nested frames and choices stay with their owner, not duplicate items.
    collections = (
        ("data-list", ("data_list", "rows"), ("did", "monitor_key"), ("unit",)),
        (
            "generic-ffd-signal",
            ("generic_ffd", "signals"),
            ("snapshot_did", "primary_did", "monitor_key"),
            (),
        ),
        (
            "rob-code",
            ("rob", "behavior_codes"),
            ("signature", "behavior_code"),
            ("comment",),
        ),
        ("rob-signal", ("rob", "signals"), ("did", "record_key"), ()),
        ("command", ("commands",), ("kind", "role"), ("execution",)),
        ("selector", ("selectors",), ("selector",), ()),
        (
            "active-test-group",
            ("active_test_groups", "groups"),
            ("group_id", "id"),
            ("execution",),
        ),
        ("signal-group", ("support_catalog", "signal_groups"), ("group_id",), ()),
        (
            "signal-membership",
            ("support_catalog", "signal_memberships"),
            ("list_key", "identifier"),
            (),
        ),
        (
            "support-query",
            ("support_catalog", "support_queries"),
            ("query_id",),
            ("kind",),
        ),
        (
            "freeze-frame-query",
            ("support_catalog", "freeze_frame_queries"),
            ("freeze_frame_number",),
            (),
        ),
    )
    for kind, path, identifiers, details in collections:
        rows: Any = catalog
        for part in path:
            rows = rows.get(part, {}) if isinstance(rows, dict) else {}
        for ordinal, row in enumerate(rows if isinstance(rows, list) else []):
            identifier = next(
                (str(row[key]) for key in identifiers if row.get(key) is not None),
                str(ordinal),
            )
            name = str(row.get("name") or row.get("kind") or identifier)
            detail = " ".join(
                str(row[key]) for key in details if row.get(key) is not None
            )
            yield (
                region,
                category_id,
                kind,
                identifier,
                name,
                detail,
                _json(row),
                _pointer(*path, ordinal),
            )


def _customize_rows(region: str, catalog: dict[str, Any]):
    for field, kind, keys in (
        ("groups", "customize-group", ("group_id", "body_type")),
        ("items", "customize-item", ("group_id", "item_id")),
        ("body_type_probes", "customize-probe", ("body_type", "lookup_key")),
    ):
        for ordinal, row in enumerate(catalog.get(field, [])):
            identifier = "/".join(
                str(row[key]) for key in keys if row.get(key) is not None
            )
            owner = int(row.get("target_category_id") or 0)
            yield (
                region,
                owner,
                kind,
                identifier,
                str(row.get("name") or identifier),
                "",
                _json(row),
                _pointer(field, ordinal),
            )


def _catalog_rows(region: str, category_id: int, catalog: dict[str, Any]):
    yield from _semantic_rows(region, category_id, catalog)
    yield from _source_collection_rows(region, category_id, catalog)
    for ordinal, row in enumerate(catalog.get("legacy_records", [])):
        # Legacy protocol-specific schemas stay distinct from P5 DID signals.
        # Parameter/request metadata does not authorize actuator execution.
        kind = "legacy-" + str(row["kind"]).replace("_", "-")
        identifier = f"{row['table']}:{row['record']}"
        detail = str(
            row.get("semantic_status")
            or row.get("native_status")
            or row.get("execution")
            or row.get("layout")
            or ""
        )
        yield (
            region,
            category_id,
            kind,
            identifier,
            str(row.get("name") or identifier),
            detail,
            _json(row),
            _pointer("legacy_records", ordinal),
        )
    for did, signals in sorted(catalog.get("dids", {}).items()):
        for ordinal, signal in enumerate(signals):
            yield (
                region,
                category_id,
                "did",
                did,
                str(signal.get("name") or did),
                str(signal.get("unit") or ""),
                _json(signal),
                _pointer("dids", did, ordinal),
            )
    for packed, dtcs in sorted(catalog.get("dtcs", {}).items()):
        for ordinal, dtc in enumerate(dtcs):
            ident = str(dtc.get("code") or packed)
            yield (
                region,
                category_id,
                "dtc",
                ident,
                str(dtc.get("description") or ident),
                str(dtc.get("failure") or ""),
                _json(dtc),
                _pointer("dtcs", packed, ordinal),
            )
    for ordinal, row in enumerate(catalog.get("active_tests", [])):
        ident = f"0x{int(row.get('id', 0)):04X}"
        detail = f"{row.get('kind') or ''} {row.get('execution') or ''}".strip()
        yield (
            region,
            category_id,
            "active-test",
            ident,
            str(row.get("name") or ident),
            detail,
            _json(row),
            _pointer("active_tests", ordinal),
        )
    for ordinal, row in enumerate(catalog.get("functions", [])):
        ident = str(row.get("id") or row.get("function_id") or "")
        if row.get("detail_id") is not None:
            ident += f"/{row['detail_id']}"
        name = str(row.get("name") or row.get("detail_name") or ident)
        yield (
            region,
            category_id,
            "function",
            ident,
            name,
            str(row.get("semantic_kind") or ""),
            _json(row),
            _pointer("functions", ordinal),
        )
    for ordinal, row in enumerate(catalog.get("plugins", [])):
        role = row.get("role") or row.get("id") or 0
        ident = f"0x{role:02X}" if isinstance(role, int) else str(role)
        name = str(row.get("dll") or row.get("plugin") or ident)
        yield (
            region,
            category_id,
            "plugin",
            ident,
            name,
            str(row.get("semantic_kind") or ""),
            _json(row),
            _pointer("plugins", ordinal),
        )
    for ordinal, row in enumerate(catalog.get("utilities", [])):
        ident = str(row.get("id") or row.get("routine_id") or "")
        yield (
            region,
            category_id,
            "utility",
            ident,
            str(row.get("name") or ident),
            str(row.get("execution") or ""),
            _json(row),
            _pointer("utilities", ordinal),
        )


def _supplemental_source(path: Path) -> dict[str, str]:
    """Stable source identity without leaking workstation directories."""
    try:
        relative = path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        return {
            "path": relative,
            "uri": "supplement://" + path.name,
            "path_scope": "repository",
        }
    except ValueError:
        return {
            "path": path.name,
            "uri": "supplement://" + path.name,
            "path_scope": "supplemental_root",
        }


def _supplemental_rows(
    index: dict[str, Any],
    generated_root: Path,
    *,
    documents: dict[str, Any] | None = None,
):
    regions = tuple(sorted(index["regions"]))
    tss3_path = generated_root / "pcs_data_viewer_tss3_managed_semantics.json"
    adu_path = generated_root / "pcs_data_viewer_adu_semantics.json"
    documents = (
        documents
        if documents is not None
        else {
            name: json.loads((generated_root / name).read_bytes())
            for name in SUPPLEMENTAL_FILES
            if (generated_root / name).is_file()
        }
    )
    tss3 = documents.get(tss3_path.name, {})
    for ordinal, row in enumerate(tss3.get("operation_ffd", {}).get("detail_rows", [])):
        data_id = str(row.get("DataID") or "")
        if data_id in ("", "-"):
            continue
        for region in regions:
            yield (
                region,
                498,
                "ffd-signal",
                f"0x{data_id.upper()}",
                str(row.get("DataName") or ""),
                "TSS3 Operation FFD",
                _json(row),
                _pointer("operation_ffd", "detail_rows", ordinal),
                _supplemental_source(tss3_path)["uri"],
            )
    for ordinal, row in enumerate(tss3.get("rob_codes", {}).get("rows", [])):
        rob = str(row.get("rob_code") or "")
        for region in regions:
            yield (
                region,
                498,
                "ffd-rob",
                f"0x{rob.upper()}",
                str(row.get("DataName") or ""),
                f"{row.get('SystemName') or ''} Operation FFD trigger".strip(),
                _json(row),
                _pointer("rob_codes", "rows", ordinal),
                _supplemental_source(tss3_path)["uri"],
            )
    adu = documents.get(adu_path.name, {})
    for ordinal, row in enumerate(adu.get("adu", {}).get("rows", [])):
        data_id = str(row.get("DataID") or "")
        if data_id in ("", "-"):
            continue
        for region in regions:
            yield (
                region,
                0,
                "adu-signal",
                f"0x{data_id.upper()}",
                str(row.get("DataName") or ""),
                "ADAS Domain Controller recorder",
                _json(row),
                _pointer("adu", "rows", ordinal),
                _supplemental_source(adu_path)["uri"],
            )


class _SearchWriter:
    """Store each search summary once; occurrences retain their original IDs."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.regions: dict[str, int] = {}
        self.kinds: dict[str, int] = {}
        self.text: dict[str, int] = {}
        self.records: dict[tuple[int, int, int, int], int] = {}
        self.ranges: dict[tuple[int, int], list[list[int]]] = {}

    def _intern(self, table: str, column: str, cache: dict, value: str) -> int:
        identity = cache.get(value)
        if identity is None:
            identity = len(cache) + 1
            self.db.execute(
                f"INSERT INTO {table}(id,{column}) VALUES (?,?)", (identity, value)
            )
            cache[value] = identity
        return identity

    def region(self, value: str) -> int:
        return self._intern("search_regions", "name", self.regions, value)

    def add(self, row: tuple, document_id: int, pointer_id: int) -> None:
        region, category, kind, identifier, name, detail = row[:6]
        kind_id = self._intern("search_kinds", "name", self.kinds, kind)
        fields = tuple(
            self._intern("text_values", "value", self.text, value)
            for value in (identifier, name, detail)
        )
        key = (kind_id, *fields)
        record_id = self.records.get(key)
        if record_id is None:
            record_id = len(self.records) + 1
            self.records[key] = record_id
            self.db.execute(
                "INSERT INTO search_records VALUES (?,?,?,?,?)", (record_id, *key)
            )
        region_id = self.region(region)
        cursor = self.db.execute(
            "INSERT INTO item_occurrences(region_id,category_id,record_id,document_id,pointer_id) VALUES (?,?,?,?,?)",
            (region_id, category, record_id, document_id, pointer_id),
        )
        identity = cursor.lastrowid
        ranges = self.ranges.setdefault((region_id, category), [])
        # Supplement rows interleave the three regions. Coalesce those tiny
        # gaps; the owner_items view still filters the exact region/category.
        if ranges and identity - ranges[-1][1] <= 3:
            ranges[-1][1] = identity
        else:
            ranges.append([identity, identity])

    def finish(self) -> None:
        self.db.executemany(
            "INSERT INTO owner_ranges VALUES (?,?,?,?)",
            (
                (region, category, first, last)
                for (region, category), ranges in sorted(self.ranges.items())
                for first, last in ranges
            ),
        )
        self.db.execute("""INSERT INTO item_count_rows
            SELECT o.region_id,o.category_id,r.kind_id,count(*)
            FROM item_occurrences o JOIN search_records r ON r.id=o.record_id
            GROUP BY o.region_id,o.category_id,r.kind_id""")


def _validate_source_references(value: Any) -> None:
    """Storage references cannot be supplied by source JSON."""
    pending = [value]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            if any(key.startswith("$") for key in node):
                raise ValueError("source JSON uses a reserved storage reference key")
            pending.extend(node.values())
        elif isinstance(node, list):
            pending.extend(node)


def _normalize_product_records(db: sqlite3.Connection) -> None:
    """Share diagnostic facts without retaining research reconstruction data."""
    dtcs = DTCStore(db)
    dtc_sources = SourceDTCStore(db, codes=dtcs)
    for identity, packed in db.execute(
        "SELECT id,data FROM source_documents WHERE member LIKE 'catalogs/%'"
    ):
        document = dtc_sources.normalize(
            dtcs.normalize(json.loads(codec.decompress(packed)))
        )
        db.execute(
            "UPDATE source_documents SET data=? WHERE id=?",
            (codec.compress(_json(document).encode("utf-8")), identity),
        )
    normalize_signals(db)
    observations = ObservationStore(db)
    for identity, packed in db.execute(
        "SELECT id,data FROM source_documents WHERE member LIKE 'catalogs/%'"
    ):
        document = observations.normalize(json.loads(codec.decompress(packed)))
        db.execute(
            "UPDATE source_documents SET data=? WHERE id=?",
            (codec.compress(_json(document).encode("utf-8")), identity),
        )
    normalize_freeze_physical(db)
    decoded_monitors = DecodedMonitorStore(db)
    native_recorders = NativeRecorderStore(db)
    for identity, packed in db.execute(
        "SELECT id,data FROM source_documents WHERE member LIKE 'catalogs/%'"
    ):
        document = native_recorders.normalize(
            decoded_monitors.normalize(json.loads(codec.decompress(packed)))
        )
        db.execute(
            "UPDATE source_documents SET data=? WHERE id=?",
            (codec.compress(_json(document).encode("utf-8")), identity),
        )
    conditions, freezes, operations = (
        ConditionStore(db),
        FreezeStore(db),
        OperationStore(db),
    )
    for identity, packed in db.execute(
        "SELECT id,data FROM source_documents WHERE member LIKE 'catalogs/%'"
    ):
        document = operations.normalize(
            freezes.normalize(
                conditions.normalize(json.loads(codec.decompress(packed)))
            )
        )
        db.execute(
            "UPDATE source_documents SET data=? WHERE id=?",
            (codec.compress(_json(document).encode("utf-8")), identity),
        )
    rob, recorder, behavior, support = (
        LegacyROBStore(db),
        RecorderStore(db),
        BehaviorCodeStore(db),
        SupportStore(db),
    )
    for identity, packed in db.execute(
        "SELECT id,data FROM source_documents WHERE member LIKE 'catalogs/%'"
    ):
        document = support.normalize(
            behavior.normalize(
                recorder.normalize(rob.normalize(json.loads(codec.decompress(packed))))
            )
        )
        db.execute(
            "UPDATE source_documents SET data=? WHERE id=?",
            (codec.compress(_json(document).encode("utf-8")), identity),
        )
    normalize_work_semantics(db)
    normalize_product_active(db)
    plans = PlanStore(db)
    for identity, packed in db.execute(
        "SELECT id,data FROM source_documents WHERE member LIKE 'catalogs/%'"
    ):
        document = plans.normalize(json.loads(codec.decompress(packed)))
        db.execute(
            "UPDATE source_documents SET data=? WHERE id=?",
            (codec.compress(_json(document).encode("utf-8")), identity),
        )
    normalize_memberships(db)
    normalize_customize(db)
    normalize_vehicle_index(db)
    normalize_topology(db)
    normalize_ecu_configurations(db)


def export_runtime_db(
    bundle_path: Path = DEFAULT_BUNDLE,
    out: Path = DEFAULT_OUTPUT,
    *,
    supplemental_root: Path | None = None,
) -> dict[str, int | str]:
    """Project a bundle plus pinned repository supplements.

    supplemental_root defaults to data/generated/gtsplus_2026, never the input
    bundle parent. Pass an explicit directory to select another supplement set.
    Missing files are recorded explicitly in meta.supplemental_sources.
    """
    supplemental_root = (
        Path(supplemental_root)
        if supplemental_root is not None
        else DEFAULT_SUPPLEMENTAL_ROOT
    )
    documents = {}
    supplemental_sources = []
    for name in SUPPLEMENTAL_FILES:
        path = (supplemental_root / name).resolve()
        source = {**_supplemental_source(path), "status": "missing"}
        if path.is_file():
            data = path.read_bytes()
            documents[name] = project_document("supplement://" + name, json.loads(data))
            source.update(
                status="loaded",
                sha256=hashlib.sha256(data).hexdigest(),
                bytes=len(data),
            )
        supplemental_sources.append(source)
    bundle = DiagnosticBundle(bundle_path)
    bundle.verify()
    index = bundle.json("index.json")
    if index.get("schema") != SOURCE_SCHEMA:
        raise ValueError(
            f"unsupported diagnostic source schema {index.get('schema')!r}"
        )

    index = project_document("index.json", index)

    out.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{out.name}.", suffix=".tmp", dir=out.parent
    )
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

        search = _SearchWriter(db)
        install_sets: dict[tuple, int] = {}
        transport_routes: dict[tuple, int] = {}
        source_members: dict[str, int] = {}
        source_pointers: dict[str, int] = {}

        def source_id(
            table: str, column: str, values: dict[str, int], value: str
        ) -> int:
            identity = values.get(value)
            if identity is None:
                identity = len(values) + 1
                db.execute(
                    f"INSERT INTO {table}(id,{column}) VALUES (?,?)", (identity, value)
                )
                values[value] = identity
            return identity

        def insert_item(row: tuple, member: str) -> None:
            pointer_id = source_id(
                "source_pointers", "pointer", source_pointers, row[7]
            )
            search.add(row, source_members[member], pointer_id)

        def insert_document(member: str, document: dict[str, Any]) -> None:
            _validate_source_references(document)
            # Region sections and category identities are independently addressable.
            # This avoids inflating the complete regional index to inspect one ECU.
            parts = []
            if member == "index.json":
                root = {
                    key: value for key, value in document.items() if key != "regions"
                }
                root["regions"] = {}
                for region, regional in document["regions"].items():
                    section = {}
                    root["regions"][region] = section
                    for key, value in regional.items():
                        if key == "selected_categories":
                            section[key] = {identity: None for identity in value}
                            for identity, category in value.items():
                                parts.append(
                                    (
                                        _pointer("regions", region, key, identity),
                                        category,
                                    )
                                )
                        else:
                            section[key] = None
                            parts.append((_pointer("regions", region, key), value))
            else:
                root = document
            prepared_parts = []
            for pointer, value in parts:
                pointer_id = source_id(
                    "source_pointers", "pointer", source_pointers, pointer
                )
                tokens = [
                    token.replace("~1", "/").replace("~0", "~")
                    for token in pointer.split("/")[1:]
                ]
                target = root
                for token in tokens[:-1]:
                    target = target[token]
                target[tokens[-1]] = {"$part": pointer_id}
                # Temporary source values can exceed the final decoded-blob bound.
                # Normalization below factors shared evidence and validates every
                # published Zstandard frame against the reader limit.
                prepared_parts.append(
                    (pointer_id, zlib.compress(_json(value).encode("utf-8")))
                )
            packed = zlib.compress(_json(root).encode("utf-8"))
            existing = db.execute(
                "SELECT data FROM source_documents WHERE member=?", (member,)
            ).fetchone()
            if existing is not None:
                if existing[0] != packed:
                    raise ValueError(f"inconsistent source document for {member}")
                return
            identity = len(source_members) + 1
            source_members[member] = identity
            db.execute(
                "INSERT INTO source_documents VALUES (?,?,?)",
                (identity, member, packed),
            )
            for pointer_id, packed_part in prepared_parts:
                db.execute(
                    "INSERT INTO source_document_parts VALUES (?,?,?)",
                    (identity, pointer_id, packed_part),
                )

        insert_document("index.json", index)
        item_count = 0
        for region, region_index in sorted(index["regions"].items()):
            search.region(region)
            categories = region_index["selected_categories"]
            keys = _category_keys(categories)
            # Overlay source facts have no inferred ECU/vehicle applicability.
            # Index the qualified definition, not isolated rows stripped of scope.
            for ordinal, overlay in enumerate(region_index.get("ecu_overlays", [])):
                scope = overlay["source_scope"]
                database = str(scope["database"])
                insert_item(
                    (
                        region,
                        0,
                        "ecu-overlay",
                        database,
                        f"{database} operation freeze definitions",
                        f"{scope['family']} source; activation unresolved",
                        _json(overlay),
                        _pointer("regions", region, "ecu_overlays", ordinal),
                    ),
                    "index.json",
                )
                item_count += 1
            customize_member = region_index.get("customize_member")
            if customize_member:
                customize = project_document(
                    str(customize_member), bundle.json(str(customize_member))
                )
                customize_rows = list(_customize_rows(region, customize))
                insert_document(str(customize_member), customize)
                for row in customize_rows:
                    insert_item(row, str(customize_member))
                    item_count += 1
            for binding_ordinal, binding in enumerate(
                (region_index.get("utilities") or {}).get("bindings", [])
            ):
                role = int(binding["role"])
                name = str(binding.get("semantic_kind") or binding.get("dll") or "")
                insert_item(
                    (
                        region,
                        0,
                        "utility-family",
                        f"0x{role:02X}",
                        name,
                        str(binding.get("dll") or ""),
                        _json(binding),
                        _pointer(
                            "regions", region, "utilities", "bindings", binding_ordinal
                        ),
                    ),
                    "index.json",
                )
                item_count += 1
            for vehicle_key, vehicle in sorted(
                region_index["vehicles"].items(),
                key=lambda pair: int(pair[1]["vehicle_type"]),
            ):
                vehicle_type = int(vehicle["vehicle_type"])
                db.execute(
                    "INSERT INTO vehicles VALUES (?,?,?,?)",
                    (
                        region,
                        vehicle_type,
                        str(vehicle.get("name") or ""),
                        _json(vehicle.get("install_set_ids") or []),
                    ),
                )
                insert_item(
                    (
                        region,
                        0,
                        "vehicle",
                        str(vehicle_type),
                        str(vehicle.get("name") or f"Vehicle {vehicle_type}"),
                        "",
                        _json(vehicle),
                        _pointer("regions", region, "vehicles", vehicle_key),
                    ),
                    "index.json",
                )
                item_count += 1
                for set_id in vehicle.get("install_set_ids") or []:
                    for install in region_index["install_sets"].get(str(set_id), []):
                        route = (
                            region_index["routes"].get(str(install.get("route_key")))
                            or {}
                        )
                        install_key = (search.region(region), vehicle_type, int(set_id))
                        if install_key not in install_sets:
                            install_sets[install_key] = len(install_sets) + 1
                            db.execute(
                                "INSERT INTO vehicle_install_sets VALUES (?,?,?,?)",
                                (install_sets[install_key], *install_key),
                            )
                        route_key = (
                            install.get("route_key"),
                            route.get("physical_request_address"),
                            route.get("address_extension"),
                            route.get("transport_kind"),
                        )
                        if route_key not in transport_routes:
                            transport_routes[route_key] = len(transport_routes) + 1
                            db.execute(
                                "INSERT INTO transport_routes VALUES (?,?,?,?,?)",
                                (transport_routes[route_key], *route_key),
                            )
                        db.execute(
                            "INSERT OR IGNORE INTO installed_ecus VALUES (?,?,?,?,?)",
                            (
                                install_sets[install_key],
                                int(install["category_id"]),
                                int(install["connection_route_selector"]),
                                int(install["connection_frame_id"]),
                                transport_routes[route_key],
                            ),
                        )
            for raw_id, category in sorted(
                categories.items(), key=lambda pair: int(pair[0])
            ):
                category_id = int(raw_id)
                member = category.get("catalog_member")
                counts = {
                    "dids": 0,
                    "signals": 0,
                    "dtcs": 0,
                    "active_tests": 0,
                    "functions": 0,
                    "plugins": 0,
                    "utilities": 0,
                }
                if member:
                    catalog = project_document(str(member), bundle.json(str(member)))
                    counts = {
                        "dids": len(catalog.get("dids", {})),
                        "signals": sum(
                            len(rows) for rows in catalog.get("dids", {}).values()
                        ),
                        "dtcs": sum(
                            len(rows) for rows in catalog.get("dtcs", {}).values()
                        ),
                        "active_tests": len(catalog.get("active_tests", [])),
                        "functions": len(catalog.get("functions", [])),
                        "plugins": len(catalog.get("plugins", [])),
                        "utilities": len(catalog.get("utilities", [])),
                    }
                    rows = list(_catalog_rows(region, category_id, catalog))
                    insert_document(str(member), catalog)
                    for row in rows:
                        insert_item(row, str(member))
                    counts["items_by_kind"] = {
                        kind: sum(row[2] == kind for row in rows)
                        for kind in sorted({row[2] for row in rows})
                    }
                    item_count += len(rows)
                key = keys[category_id]
                name = str(
                    category.get("name")
                    or category.get("short_name")
                    or f"Category {category_id}"
                )
                db.execute(
                    "INSERT INTO ecus VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        region,
                        category_id,
                        key,
                        name,
                        str(category.get("database") or ""),
                        category.get("generation"),
                        category.get("support_mode"),
                        member,
                        _json(counts),
                    ),
                )
                insert_item(
                    (
                        region,
                        category_id,
                        "ecu",
                        str(category_id),
                        name,
                        f"{key} {category.get('database') or ''}".strip(),
                        _json(category),
                        _pointer("regions", region, "selected_categories", raw_id),
                    ),
                    "index.json",
                )
                item_count += 1

        db.execute(
            "INSERT INTO meta VALUES (?,?)",
            ("supplemental_sources", _json(supplemental_sources)),
        )
        supplemental = list(
            _supplemental_rows(index, supplemental_root, documents=documents)
        )
        for name, document in documents.items():
            member = _supplemental_source(supplemental_root / name)["uri"]
            insert_document(member, document)
        for row in supplemental:
            insert_item(row, row[8])
        item_count += len(supplemental)
        search.finish()
        _normalize_product_records(db)
        db.execute("INSERT INTO items_fts(items_fts) VALUES ('rebuild')")
        db.execute("INSERT INTO items_fts(items_fts) VALUES ('optimize')")
        db.execute("PRAGMA optimize")
        # There is intentionally no per-occurrence owner B-tree. Analyze the
        # index-free table explicitly so immutable catalog stats stay O(1).
        db.execute("ANALYZE item_occurrences")
        db.commit()
        db.execute("VACUUM")
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("runtime SQLite integrity check failed")
    except BaseException:
        db.close()
        temporary.unlink(missing_ok=True)
        raise
    db.close()
    os.replace(temporary, out)
    return {
        "path": str(out),
        "bytes": out.stat().st_size,
        "members": len(bundle.members),
        "items": item_count,
    }
