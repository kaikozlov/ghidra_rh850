"""Runtime projection covers semantic records without duplicating nested payloads."""

import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.techstream import diag_codec as codec
from tools.techstream.diag_bundle import DiagnosticBundleWriter
from tools.techstream.diag_metadata import restore
from tools.techstream.diag_product_projection import project_document
from tools.techstream.diag_runtime_db import (
    _category_key,
    _supplemental_rows,
    export_runtime_db,
)


def restore_document(db, member):
    document = restore(
        db,
        json.loads(
            codec.decompress(
                db.execute(
                    "SELECT data FROM runtime_documents WHERE member=?", (member,)
                ).fetchone()[0]
            )
        ),
    )
    for pointer, packed in db.execute(
        """SELECT p.pointer,s.data FROM source_document_parts s
            JOIN source_documents d ON d.id=s.document_id JOIN source_pointers p ON p.id=s.pointer_id
            WHERE d.member=?""",
        (member,),
    ):
        parts = [
            p.replace("~1", "/").replace("~0", "~") for p in pointer.split("/")[1:]
        ]
        target = document
        for part in parts[:-1]:
            target = target[int(part)] if isinstance(target, list) else target[part]
        key = int(parts[-1]) if isinstance(target, list) else parts[-1]
        target[key] = restore(db, json.loads(codec.decompress(packed)))
    return document


class RuntimeProjectionTests(unittest.TestCase):
    def test_overlay_search_keeps_qualified_unresolved_definition(self):
        overlay = {
            "source_scope": {
                "region": "JP",
                "family": "Spe",
                "database": "HEVBrake.ddb",
            },
            "activation": {
                "status": "unresolved",
                "reason": "Applicability not established",
            },
            "operation_freeze": [
                {
                    "table": 54,
                    "record": 0,
                    "group_selector": 1,
                    "freeze_frame_number": 15,
                    "unassigned_bytes_2_4": "010000",
                }
            ],
        }
        index = {
            "schema": "toyota-diagnostics-bundle-v4",
            "regions": {
                "JP": {
                    "vehicles": {},
                    "selected_categories": {},
                    "ecu_overlays": [overlay],
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bundle"
            writer = DiagnosticBundleWriter(root)
            writer.add("index.json", io.BytesIO(json.dumps(index).encode()))
            writer.finish()
            out = Path(tmp) / "catalog.sqlite"
            export_runtime_db(root, out, supplemental_root=Path(tmp) / "absent")
            with sqlite3.connect(out) as db:
                self.assertEqual(
                    db.execute(
                        "SELECT region,category_id,kind,identifier FROM items"
                    ).fetchall(),
                    [("JP", 0, "ecu-overlay", "HEVBrake.ddb")],
                )
                self.assertEqual(
                    db.execute("SELECT pointer FROM item_sources").fetchone()[0],
                    "/regions/JP/ecu_overlays/0",
                )
                self.assertEqual(
                    restore_document(db, "index.json")["regions"]["JP"]["ecu_overlays"],
                    [overlay],
                )

    def test_repeated_search_summary_keeps_distinct_occurrences(self):
        from tools.techstream.diag_runtime_db import DDL, _SearchWriter

        with sqlite3.connect(":memory:") as db:
            db.executescript(DDL)
            db.executemany(
                "INSERT INTO source_documents VALUES (?,?,?)",
                [
                    (1, "a.json", codec.compress(b"{}")),
                    (2, "b.json", codec.compress(b"{}")),
                ],
            )
            db.execute("INSERT INTO source_pointers VALUES (1,'/signal')")
            writer = _SearchWriter(db)
            writer.add(("NA", 123, "did", "0x1000", "Speed", "km/h"), 1, 1)
            writer.add(("EU", 456, "did", "0x1000", "Speed", "km/h"), 2, 1)
            writer.add(("NA", 123, "did", "0x1000", "Speed", "km/h"), 1, 1)
            writer.finish()
            self.assertEqual(
                db.execute("SELECT count(*) FROM search_records").fetchone()[0], 1
            )
            self.assertEqual(
                db.execute(
                    "SELECT id,region,category_id FROM items ORDER BY id"
                ).fetchall(),
                [(1, "NA", 123), (2, "EU", 456), (3, "NA", 123)],
            )
            self.assertEqual(
                db.execute(
                    "SELECT item_id,member FROM item_sources ORDER BY item_id"
                ).fetchall(),
                [(1, "a.json"), (2, "b.json"), (3, "a.json")],
            )
            self.assertEqual(
                db.execute(
                    "SELECT id FROM owner_items WHERE region='NA' AND category_id=123 ORDER BY id"
                ).fetchall(),
                [(1,), (3,)],
            )
            self.assertEqual(
                db.execute("SELECT * FROM owner_items ORDER BY id").fetchall(),
                db.execute("SELECT * FROM items ORDER BY id").fetchall(),
            )
            self.assertEqual(
                db.execute(
                    "SELECT count FROM item_counts WHERE region='NA'"
                ).fetchone()[0],
                2,
            )
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_reader_size_bound_applies_after_product_projection(self):
        evidence = {"status": "unavailable", "query": {"detail": "x" * 1000}}
        catalog = {
            "dids": {
                "0x1000": [
                    {"name": "A", "native": evidence},
                    {"name": "B", "native": evidence},
                ]
            }
        }
        member = "catalogs/NA/123.json"
        index = {
            "schema": "toyota-diagnostics-bundle-v4",
            "regions": {
                "NA": {
                    "vehicles": {},
                    "selected_categories": {"123": {"catalog_member": member}},
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bundle"
            writer = DiagnosticBundleWriter(root)
            for name, value in (("index.json", index), (member, catalog)):
                writer.add(name, io.BytesIO(json.dumps(value).encode()))
            writer.finish()
            out = Path(tmp) / "runtime.sqlite"
            with (
                patch("tools.techstream.diag_codec.MAX_DOCUMENT_BYTES", 1500),
                patch(
                    "tools.techstream.diag_runtime_db._supplemental_rows",
                    return_value=[],
                ),
            ):
                export_runtime_db(root, out, supplemental_root=Path(tmp) / "none")
            with sqlite3.connect(out) as db:
                self.assertEqual(
                    restore_document(db, member), project_document(member, catalog)
                )
                self.assertIsNone(
                    db.execute(
                        "SELECT name FROM sqlite_master WHERE name='shared_metadata'"
                    ).fetchone()
                )
                for table in ("source_documents", "source_document_parts"):
                    for (packed,) in db.execute(f"SELECT data FROM {table}"):
                        self.assertLessEqual(len(codec.decompress(packed)), 1500)

    def test_source_cannot_inject_storage_references(self):
        from tools.techstream.diag_runtime_db import _validate_source_references

        for key in ("$part", "$metadata", "$diagnostic_code"):
            with self.assertRaisesRegex(ValueError, "reserved"):
                _validate_source_references({"nested": [{key: 1}]})

    def test_all_semantic_collections_and_source_locations(self):
        catalog = {
            "source_identity": {"database": {"sha256": "fixture"}},
            "selection_boundary": "decoded fields only",
            "dids": {"0x1000": [{"name": "Speed", "unit": "km/h"}]},
            "dtcs": {
                "legacy:1234": [
                    {"dtc_identifier16": 4660, "description": "Legacy fault"}
                ]
            },
            "active_tests": [
                {"id": 1, "name": "Actuate", "frames": [{"bytes": [1, 2]}]}
            ],
            "functions": [{"id": 1}],
            "plugins": [{"role": 1}],
            "utilities": [{"id": 1}],
            "data_list": {"rows": [{"did": "0x1000", "name": "Ordered speed"}]},
            "generic_ffd": {
                "signals": [{"snapshot_did": 1027, "name": "Snapshot speed"}]
            },
            "rob": {
                "behavior_codes": [{"signature": "X001", "name": "Behavior"}],
                "signals": [{"did": 20529, "name": "ROB speed"}],
            },
            "commands": [{"kind": "dtc_clear", "execution": "plan_only"}],
            "selectors": [{"selector": "0x1", "frames": [{"bytes": [2]}]}],
            "active_test_groups": {"groups": [{"group_id": 1, "name": "Group"}]},
        }
        customize = {
            "groups": [{"group_id": 1, "body_type": 0, "name": "Door"}],
            "items": [
                {
                    "group_id": 1,
                    "item_id": 2,
                    "target_category_id": 123,
                    "name": "Lock",
                    "choices": [{"value": 0}, {"value": 1}],
                }
            ],
            "body_type_probes": [
                {"body_type": 0, "lookup_key": 1, "target_category_id": 123}
            ],
        }
        member = "catalogs/NA/123.json"
        custom_member = "customize/NA/0.json"
        index = {
            "schema": "toyota-diagnostics-bundle-v4",
            "regions": {
                "NA": {
                    "vehicles": {},
                    "selected_categories": {"123": {"catalog_member": member}},
                    "customize_member": custom_member,
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bundle"
            writer = DiagnosticBundleWriter(root)
            sources = {"index.json": index, member: catalog, custom_member: customize}
            for name, value in sources.items():
                writer.add(name, io.BytesIO(json.dumps(value).encode()))
            writer.finish()
            out = Path(tmp) / "runtime.sqlite"
            with patch(
                "tools.techstream.diag_runtime_db._supplemental_rows", return_value=[]
            ):
                export_runtime_db(root, out)
            with sqlite3.connect(out) as db:
                tables = {
                    row[0]
                    for row in db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                self.assertFalse(
                    tables
                    & {
                        "ecu_records",
                        "native_records",
                        "plugin_queries",
                        "shared_metadata",
                    }
                )
                kinds = dict(db.execute("SELECT kind,count FROM item_counts"))
                expected = {
                    "did",
                    "dtc",
                    "active-test",
                    "function",
                    "utility",
                    "data-list",
                    "generic-ffd-signal",
                    "rob-code",
                    "rob-signal",
                    "command",
                    "selector",
                    "active-test-group",
                    "customize-group",
                    "customize-item",
                    "customize-probe",
                    "ecu",
                }
                self.assertEqual(set(kinds), expected)
                self.assertTrue(all(value == 1 for value in kinds.values()))
                rows = db.execute("SELECT member,pointer FROM item_sources").fetchall()
                item_count = db.execute("SELECT count(*) FROM items").fetchone()[0]
                self.assertEqual(len(rows), item_count)
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertIsNone(
                    db.execute(
                        "SELECT name FROM sqlite_master WHERE name='payload_data'"
                    ).fetchone()
                )
                for source, pointer in rows:
                    value = project_document(source, sources[source])
                    actual = restore_document(db, source)
                    for token in pointer.split("/")[1:]:
                        token = token.replace("~1", "/").replace("~0", "~")
                        value = (
                            value[int(token)]
                            if isinstance(value, list)
                            else value[token]
                        )
                        actual = (
                            actual[int(token)]
                            if isinstance(actual, list)
                            else actual[token]
                        )
                    self.assertEqual(actual, value)
                self.assertEqual(
                    db.execute(
                        "SELECT identifier FROM items WHERE kind='dtc'"
                    ).fetchone()[0],
                    "legacy:1234",
                )
                self.assertEqual(
                    db.execute(
                        "SELECT category_id FROM items WHERE kind='customize-item'"
                    ).fetchone()[0],
                    123,
                )
                counts = json.loads(db.execute("SELECT counts FROM ecus").fetchone()[0])
                self.assertEqual(sum(counts["items_by_kind"].values()), 12)
                self.assertEqual(
                    db.execute(
                        "SELECT count(*) FROM items_fts WHERE items_fts MATCH 'Snapshot'"
                    ).fetchone()[0],
                    1,
                )
                self.assertIsNone(
                    db.execute(
                        "SELECT name FROM sqlite_master WHERE name='catalog_sources'"
                    ).fetchone()
                )
                self.assertEqual(
                    db.execute(
                        "SELECT count(*) FROM runtime_documents WHERE member NOT LIKE 'supplement://%'"
                    ).fetchone()[0],
                    3,
                )
                for name, original in sources.items():
                    self.assertEqual(
                        restore_document(db, name), project_document(name, original)
                    )
                skeleton = restore(
                    db,
                    json.loads(
                        codec.decompress(
                            db.execute(
                                "SELECT data FROM runtime_documents WHERE member=?",
                                (member,),
                            ).fetchone()[0]
                        )
                    ),
                )
                self.assertEqual(skeleton["dids"]["0x1000"], catalog["dids"]["0x1000"])
                self.assertEqual(skeleton["active_tests"], catalog["active_tests"])
                self.assertNotIn("source_identity", skeleton)
                self.assertNotIn("plugins", skeleton)

    def test_native_source_families_and_metadata(self):
        from tools.techstream.diag_runtime_db import (
            SOURCE_COLLECTIONS,
            SOURCE_LISTS,
            _catalog_rows,
        )

        self.assertEqual(
            set(SOURCE_LISTS),
            {"monitor_source", "dtc_source", "dynamic_lsb", "active_test_source"},
        )
        expected_fields = {
            "p6_rob_source": 2,
            "native_ddr": 6,
            "ddr_behavior": 3,
            "trigger_catalog": 4,
            "active_test_support": 8,
            "variable_drive": 4,
            "obd_monitor": 15,
            "diagnostic_metadata": 5,
            "physical_catalog": 3,
            "ddr": 4,
            "work_factor": 9,
        }
        self.assertEqual(
            {key: len(fields) for key, fields in SOURCE_COLLECTIONS.items()},
            expected_fields,
        )
        catalog = {
            "source_identity": {"database": "fixture"},
            "coverage": {"source_rows": 123},
            "source_tables": [{"table": 46, "records": 1}],
        }
        expected_pointers = set()
        for section, fields in SOURCE_COLLECTIONS.items():
            catalog[section] = {"runtime_boundary": "offline only"}
            for field in fields:
                # Equal IDs are separate source records, never INSERT OR IGNORE.
                catalog[section][field] = [
                    {
                        "table": 1,
                        "record": ordinal,
                        "key": 7,
                        "name": "needle",
                        "nested": [{"x": 1}],
                    }
                    for ordinal in range(2)
                ]
                expected_pointers.update(
                    f"/{section}/{field}/{ordinal}" for ordinal in range(2)
                )
        for section in SOURCE_LISTS:
            catalog[section] = [{"table": 2, "record": 0, "raw": "ab"}]
            expected_pointers.add(f"/{section}/0")
        check = {"table": 46, "record": 0, "role": 1}
        catalog["legacy_rob"] = {
            "signal_checks": [check],
            "families": [
                {
                    "mode": mode,
                    "transport": {"read_selector": 189},
                    "behavior_codes": [{"table": 42, "record": 0, "code": "X"}],
                    "identifiers": [{"table": 43, "record": 0}],
                    "support_queries": [{"table": 44, "record": 0}],
                    "signals": [{"table": 45, "record": 0}],
                    "signal_checks": [check],
                }
                for mode in (1, 2)
            ],
        }
        expected_pointers.add("/legacy_rob/signal_checks/0")
        for family in range(2):
            for field in (
                "behavior_codes",
                "identifiers",
                "support_queries",
                "signals",
            ):
                expected_pointers.add(f"/legacy_rob/families/{family}/{field}/0")
        rows = list(_catalog_rows("NA", 123, catalog))
        self.assertEqual({row[7] for row in rows}, expected_pointers)
        self.assertEqual(len(rows), len(expected_pointers))
        self.assertEqual(sum(row[2] == "legacy-rob-signal-checks" for row in rows), 1)
        for row in rows:
            original = catalog
            for token in row[7].split("/")[1:]:
                original = (
                    original[int(token)]
                    if isinstance(original, list)
                    else original[token]
                )
            self.assertEqual(json.loads(row[6]), original)

    def test_standard_value_search_summary_preserves_viewer_identity(self):
        from tools.techstream.diag_runtime_db import DDL, _catalog_rows, _SearchWriter

        record = {
            "table": 18,
            "record": 0,
            "standard_value_id": 9,
            "help_id": 123,
            "standard_value": "Ignition ON: 11 to 14 V",
            "standard_value_status": "resolved",
        }
        identity = {
            "viewer_help": {
                "database": {"sha256": "viewer"},
                "strings": {"sha256": "english"},
            }
        }
        catalog = {
            "source_identity": identity,
            "work_factor": {"standard_info": [record]},
        }
        row = list(_catalog_rows("NA", 123, catalog))[0]
        self.assertEqual(row[4], "Ignition ON: 11 to 14 V")
        self.assertEqual(row[5], "resolved")
        self.assertEqual(row[7], "/work_factor/standard_info/0")
        self.assertEqual(json.loads(row[6]), record)
        with sqlite3.connect(":memory:") as db:
            db.executescript(DDL)
            db.execute(
                "INSERT INTO source_documents VALUES (1,'fixture.json',?)",
                (codec.compress(json.dumps(catalog).encode()),),
            )
            db.execute("INSERT INTO source_pointers VALUES (1,?)", (row[7],))
            _SearchWriter(db).add(row, 1, 1)
            db.execute("INSERT INTO items_fts(items_fts) VALUES ('rebuild')")
            self.assertEqual(
                db.execute(
                    "SELECT count(*) FROM items_fts WHERE items_fts MATCH 'Ignition'"
                ).fetchone()[0],
                1,
            )
            self.assertEqual(
                db.execute(
                    "SELECT count(*) FROM items_fts WHERE items_fts MATCH 'resolved'"
                ).fetchone()[0],
                1,
            )

    def test_partial_legacy_records_do_not_become_decoded_signals(self):
        from tools.techstream.diag_runtime_db import _catalog_rows

        record = {
            "source": "Engine_P3.ddb",
            "table": 7,
            "record": 3,
            "kind": "did",
            "did_key": 12,
            "raw": "0000",
            "semantic_status": "partial",
        }
        rows = list(_catalog_rows("NA", 1, {"legacy_records": [record]}))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2:4], ("legacy-did", "7:3"))
        self.assertEqual(rows[0][5], "partial")
        self.assertEqual(json.loads(rows[0][6]), record)
        self.assertEqual(rows[0][7], "/legacy_records/0")

    def test_supplemental_sources_are_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adu = root / "pcs_data_viewer_adu_semantics.json"
            adu.write_text(
                json.dumps({"adu": {"rows": [{"DataID": "1234", "DataName": "ADU"}]}})
            )
            self.assertEqual(
                [row[2] for row in _supplemental_rows({"regions": {"NA": {}}}, root)],
                ["adu-signal"],
            )
            adu.unlink()
            (root / "pcs_data_viewer_tss3_managed_semantics.json").write_text(
                json.dumps(
                    {
                        "operation_ffd": {
                            "detail_rows": [{"DataID": "4321", "DataName": "FFD"}]
                        },
                        "rob_codes": {"rows": []},
                    }
                )
            )
            self.assertEqual(
                [row[2] for row in _supplemental_rows({"regions": {"NA": {}}}, root)],
                ["ffd-signal"],
            )

    def test_supplement_root_is_explicit_and_provenance_is_hashed(self):
        import hashlib

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = root / "generated"
            canonical.mkdir()
            filename = "pcs_data_viewer_adu_semantics.json"
            document = {
                "adu": {"rows": [{"DataID": "1234", "DataName": "Canonical ADU"}]}
            }
            data = json.dumps(document).encode()
            (canonical / filename).write_bytes(data)
            candidate = root / "candidate" / "bundle"
            writer = DiagnosticBundleWriter(candidate)
            writer.add(
                "index.json",
                io.BytesIO(
                    json.dumps(
                        {
                            "schema": "toyota-diagnostics-bundle-v4",
                            "regions": {
                                "NA": {"selected_categories": {}, "vehicles": {}}
                            },
                        }
                    ).encode()
                ),
            )
            writer.finish()
            # Decoy next to candidate must not affect default source selection.
            (candidate.parent / filename).write_text("{}")
            out = root / "runtime.sqlite"
            with patch(
                "tools.techstream.diag_runtime_db.DEFAULT_SUPPLEMENTAL_ROOT", canonical
            ):
                export_runtime_db(candidate, out)
            with sqlite3.connect(out) as db:
                self.assertEqual(
                    db.execute("SELECT name FROM items").fetchone()[0], "Canonical ADU"
                )
                manifest = json.loads(
                    db.execute(
                        "SELECT value FROM meta WHERE key='supplemental_sources'"
                    ).fetchone()[0]
                )
                loaded = [entry for entry in manifest if entry["status"] == "loaded"]
                self.assertEqual(loaded[0]["sha256"], hashlib.sha256(data).hexdigest())
                self.assertEqual(
                    sum(entry["status"] == "missing" for entry in manifest), 2
                )
                self.assertEqual(
                    db.execute("SELECT member,pointer FROM item_sources").fetchone(),
                    ("supplement://" + filename, "/adu/rows/0"),
                )
                self.assertEqual(
                    restore_document(db, "supplement://" + filename), document
                )
            empty = root / "empty"
            empty.mkdir()
            export_runtime_db(candidate, out, supplemental_root=empty)
            with sqlite3.connect(out) as db:
                self.assertEqual(
                    db.execute("SELECT count(*) FROM items").fetchone()[0], 0
                )
                manifest = json.loads(
                    db.execute(
                        "SELECT value FROM meta WHERE key='supplemental_sources'"
                    ).fetchone()[0]
                )
                self.assertTrue(all(entry["status"] == "missing" for entry in manifest))

    def test_shared_members_across_regions_and_escaped_pointers(self):
        member = "catalogs/shared.json"
        custom_member = "customize/shared.json"
        catalog = {
            "dids": {"odd/~key": [{"name": "Exact name", "nested": {"null": None}}]},
            "metadata": {"opaque": [1, 2, 3]},
        }
        customize = {"groups": [{"group_id": 1, "name": "Shared group"}]}
        region = {
            "selected_categories": {"123": {"catalog_member": member}},
            "vehicles": {},
            "customize_member": custom_member,
        }
        index = {
            "schema": "toyota-diagnostics-bundle-v4",
            "regions": {"NA": region, "EU": region},
        }
        sources = {"index.json": index, member: catalog, custom_member: customize}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bundle"
            writer = DiagnosticBundleWriter(root)
            for name, value in sources.items():
                writer.add(name, io.BytesIO(json.dumps(value).encode()))
            writer.finish()
            out = Path(tmp) / "runtime.sqlite"
            empty = Path(tmp) / "empty"
            empty.mkdir()
            export_runtime_db(root, out, supplemental_root=empty)
            with sqlite3.connect(out) as db:
                self.assertEqual(
                    db.execute("SELECT count(*) FROM runtime_documents").fetchone()[0],
                    3,
                )
                self.assertEqual(
                    db.execute(
                        "SELECT count(*) FROM items WHERE kind='did'"
                    ).fetchone()[0],
                    2,
                )
                for name, original in sources.items():
                    self.assertEqual(
                        restore_document(db, name), project_document(name, original)
                    )
                self.assertEqual(
                    set(
                        row[0]
                        for row in db.execute(
                            "SELECT pointer FROM item_sources WHERE member=?", (member,)
                        )
                    ),
                    {"/dids/odd~1~0key/0"},
                )

    def test_runtime_only_supplement_is_preserved_without_search_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            supplemental = root / "supplements"
            supplemental.mkdir()
            document = {"transport": {"request": "22"}, "opaque": [None, {"a": 1}]}
            filename = "tss3_native_recorder_protocol.json"
            (supplemental / filename).write_text(json.dumps(document))
            bundle = root / "bundle"
            writer = DiagnosticBundleWriter(bundle)
            writer.add(
                "index.json",
                io.BytesIO(
                    json.dumps(
                        {
                            "schema": "toyota-diagnostics-bundle-v4",
                            "regions": {
                                "NA": {"selected_categories": {}, "vehicles": {}}
                            },
                        }
                    ).encode()
                ),
            )
            writer.finish()
            output = root / "runtime.sqlite"
            export_runtime_db(bundle, output, supplemental_root=supplemental)
            with sqlite3.connect(output) as db:
                self.assertEqual(
                    restore_document(db, "supplement://" + filename), document
                )
                self.assertEqual(
                    db.execute("SELECT count(*) FROM items").fetchone()[0], 0
                )

    def test_legacy_category_alias(self):
        self.assertEqual(_category_key(1, {"database": "Engine_P3.ddb"}), "engine")


if __name__ == "__main__":
    unittest.main()
