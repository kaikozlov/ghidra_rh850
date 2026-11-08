"""Runtime projection covers semantic records without duplicating nested payloads."""
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import zlib

from tools.techstream.diag_bundle import DiagnosticBundleWriter
from tools.techstream.diag_runtime_db import _category_key, _supplemental_rows, export_runtime_db


def restore_document(db, member):
    skeleton = json.loads(zlib.decompress(db.execute(
        "SELECT data FROM runtime_documents WHERE member=?", (member,)).fetchone()[0]))
    for pointer, packed in db.execute("""SELECT s.pointer,p.data FROM item_sources s
            JOIN item_payloads p ON p.item_id=s.item_id WHERE s.member=? ORDER BY s.item_id""", (member,)):
        if not pointer:
            continue
        parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:]]
        target = skeleton
        for part in parts[:-1]:
            target = target[int(part)] if isinstance(target, list) else target[part]
        key = int(parts[-1]) if isinstance(target, list) else parts[-1]
        target[key] = json.loads(zlib.decompress(packed))
    return skeleton


class RuntimeProjectionTests(unittest.TestCase):
    def test_all_semantic_collections_and_source_locations(self):
        catalog = {
            "source_identity": {"database": {"sha256": "fixture"}},
            "selection_boundary": "decoded fields only",
            "dids": {"0x1000": [{"name": "Speed", "unit": "km/h"}]},
            "dtcs": {"legacy:1234": [{"dtc_identifier16": 4660, "description": "Legacy fault"}]},
            "active_tests": [{"id": 1, "name": "Actuate", "frames": [{"bytes": [1, 2]}]}],
            "functions": [{"id": 1}], "plugins": [{"role": 1}], "utilities": [{"id": 1}],
            "data_list": {"rows": [{"did": "0x1000", "name": "Ordered speed"}]},
            "generic_ffd": {"signals": [{"snapshot_did": 1027, "name": "Snapshot speed"}]},
            "rob": {"behavior_codes": [{"signature": "X001", "name": "Behavior"}],
                    "signals": [{"did": 20529, "name": "ROB speed"}]},
            "commands": [{"kind": "dtc_clear", "execution": "plan_only"}],
            "selectors": [{"selector": "0x1", "frames": [{"bytes": [2]}]}],
            "active_test_groups": {"groups": [{"group_id": 1, "name": "Group"}]},
        }
        customize = {
            "groups": [{"group_id": 1, "body_type": 0, "name": "Door"}],
            "items": [{"group_id": 1, "item_id": 2, "target_category_id": 123,
                       "name": "Lock", "choices": [{"value": 0}, {"value": 1}]}],
            "body_type_probes": [{"body_type": 0, "lookup_key": 1, "target_category_id": 123}],
        }
        member = "catalogs/NA/123.json"
        custom_member = "customize/NA/0.json"
        index = {"schema": "toyota-diagnostics-bundle-v4", "regions": {"NA": {
            "vehicles": {}, "selected_categories": {"123": {"catalog_member": member}},
            "customize_member": custom_member,
        }}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bundle"
            writer = DiagnosticBundleWriter(root)
            sources = {"index.json": index, member: catalog, custom_member: customize}
            for name, value in sources.items():
                writer.add(name, io.BytesIO(json.dumps(value).encode()))
            writer.finish()
            out = Path(tmp) / "runtime.sqlite"
            with patch("tools.techstream.diag_runtime_db._supplemental_rows", return_value=[]):
                export_runtime_db(root, out)
            with sqlite3.connect(out) as db:
                kinds = dict(db.execute("SELECT kind,count FROM item_counts"))
                expected = {"did", "dtc", "active-test", "function", "plugin", "utility",
                            "data-list", "generic-ffd-signal", "rob-code", "rob-signal",
                            "command", "selector", "active-test-group",
                            "customize-group", "customize-item", "customize-probe", "ecu"}
                self.assertEqual(set(kinds), expected)
                self.assertTrue(all(value == 1 for value in kinds.values()))
                rows = db.execute("""SELECT s.member,s.pointer,p.data FROM item_sources s
                    JOIN item_payloads p ON p.item_id=s.item_id""").fetchall()
                self.assertEqual(len(rows), 16)
                for source, pointer, payload in rows:
                    value = sources[source]
                    for token in pointer.split("/")[1:]:
                        token = token.replace("~1", "/").replace("~0", "~")
                        value = value[int(token)] if isinstance(value, list) else value[token]
                    self.assertEqual(json.loads(zlib.decompress(payload)), value)
                self.assertEqual(db.execute("SELECT identifier FROM items WHERE kind='dtc'").fetchone()[0], "legacy:1234")
                self.assertEqual(db.execute("SELECT category_id FROM items WHERE kind='customize-item'").fetchone()[0], 123)
                counts = json.loads(db.execute("SELECT counts FROM ecus").fetchone()[0])
                self.assertEqual(sum(counts["items_by_kind"].values()), 13)
                self.assertEqual(db.execute("SELECT count(*) FROM items_fts WHERE items_fts MATCH 'Snapshot'").fetchone()[0], 1)
                metadata = json.loads(db.execute("SELECT metadata FROM catalog_sources WHERE member=?", (member,)).fetchone()[0])
                self.assertEqual(metadata["source_identity"], catalog["source_identity"])
                self.assertNotIn("dids", metadata)
                self.assertEqual(db.execute("SELECT count(*) FROM runtime_documents WHERE member NOT LIKE 'supplement://%'").fetchone()[0], 3)
                for name, original in sources.items():
                    self.assertEqual(restore_document(db, name), original)
                skeleton = json.loads(zlib.decompress(db.execute(
                    "SELECT data FROM runtime_documents WHERE member=?", (member,)).fetchone()[0]))
                self.assertEqual(skeleton["dids"]["0x1000"], [None])
                self.assertEqual(skeleton["active_tests"], [None])
                self.assertEqual(skeleton["source_identity"], catalog["source_identity"])

    def test_native_source_families_and_metadata(self):
        from tools.techstream.diag_runtime_db import SOURCE_COLLECTIONS, SOURCE_LISTS, _catalog_rows, _source_metadata
        self.assertEqual(set(SOURCE_LISTS), {"monitor_source", "dtc_source", "dynamic_lsb", "active_test_source"})
        expected_fields = {
            "p6_rob_source": 2, "native_ddr": 6, "ddr_behavior": 3, "trigger_catalog": 4,
            "active_test_support": 8, "variable_drive": 4, "obd_monitor": 15,
            "diagnostic_metadata": 5, "physical_catalog": 3, "ddr": 4, "work_factor": 9,
        }
        self.assertEqual({key:len(fields) for key,fields in SOURCE_COLLECTIONS.items()},expected_fields)
        catalog = {"source_identity":{"database":"fixture"}, "coverage":{"source_rows":123},
                   "source_tables":[{"table":46,"records":1}]}
        expected_pointers = set()
        for section, fields in SOURCE_COLLECTIONS.items():
            catalog[section] = {"runtime_boundary":"offline only"}
            for field in fields:
                # Equal IDs are separate source records, never INSERT OR IGNORE.
                catalog[section][field] = [
                    {"table":1,"record":ordinal,"key":7,"name":"needle","nested":[{"x":1}]}
                    for ordinal in range(2)]
                expected_pointers.update(f"/{section}/{field}/{ordinal}" for ordinal in range(2))
        for section in SOURCE_LISTS:
            catalog[section] = [{"table":2,"record":0,"raw":"ab"}]
            expected_pointers.add(f"/{section}/0")
        check = {"table":46,"record":0,"role":1}
        catalog["legacy_rob"] = {"signal_checks":[check],"families":[
            {"mode":mode,"transport":{"read_selector":189},
             "behavior_codes":[{"table":42,"record":0,"code":"X"}],
             "identifiers":[{"table":43,"record":0}],
             "support_queries":[{"table":44,"record":0}],
             "signals":[{"table":45,"record":0}],
             "signal_checks":[check]}
            for mode in (1,2)]}
        expected_pointers.add("/legacy_rob/signal_checks/0")
        for family in range(2):
            for field in ("behavior_codes","identifiers","support_queries","signals"):
                expected_pointers.add(f"/legacy_rob/families/{family}/{field}/0")
        rows = list(_catalog_rows("NA",123,catalog))
        self.assertEqual({row[7] for row in rows}, expected_pointers)
        self.assertEqual(len(rows),len(expected_pointers))
        self.assertEqual(sum(row[2]=="legacy-rob-signal-checks" for row in rows),1)
        for row in rows:
            original=catalog
            for token in row[7].split("/")[1:]:
                original=original[int(token)] if isinstance(original,list) else original[token]
            self.assertEqual(json.loads(row[6]),original)
        metadata=_source_metadata(catalog)
        self.assertEqual(metadata["coverage"],catalog["coverage"])
        self.assertEqual(metadata["source_tables"],catalog["source_tables"])
        self.assertEqual(metadata["sections"]["native_ddr"],{"runtime_boundary":"offline only"})
        self.assertEqual(metadata["sections"]["legacy_rob"]["families"],
                         [{"mode":mode,"transport":{"read_selector":189}} for mode in (1,2)])
        self.assertNotIn("monitor_source",metadata)

    def test_standard_value_search_summary_preserves_viewer_identity(self):
        from tools.techstream.diag_runtime_db import _catalog_rows, _source_metadata, DDL
        record={"table":18,"record":0,"standard_value_id":9,"help_id":123,
                "standard_value":"Ignition ON: 11 to 14 V","standard_value_status":"resolved"}
        identity={"viewer_help":{"database":{"sha256":"viewer"},"strings":{"sha256":"english"}}}
        catalog={"source_identity":identity,"work_factor":{"standard_info":[record]}}
        row=list(_catalog_rows("NA",123,catalog))[0]
        self.assertEqual(row[4],"Ignition ON: 11 to 14 V")
        self.assertEqual(row[5],"resolved")
        self.assertEqual(row[7],"/work_factor/standard_info/0")
        self.assertEqual(json.loads(row[6]),record)
        self.assertEqual(_source_metadata(catalog)["source_identity"],identity)
        with sqlite3.connect(":memory:") as db:
            db.executescript(DDL)
            db.execute("INSERT INTO items(region,category_id,kind,identifier,name,detail) VALUES (?,?,?,?,?,?)",row[:6])
            db.execute("INSERT INTO items_fts(items_fts) VALUES ('rebuild')")
            self.assertEqual(db.execute("SELECT count(*) FROM items_fts WHERE items_fts MATCH 'Ignition'").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT count(*) FROM items_fts WHERE items_fts MATCH 'resolved'").fetchone()[0],1)

    def test_partial_legacy_records_do_not_become_decoded_signals(self):
        from tools.techstream.diag_runtime_db import _catalog_rows
        record = {"source": "Engine_P3.ddb", "table": 7, "record": 3,
                  "kind": "did", "did_key": 12, "raw": "0000",
                  "semantic_status": "partial"}
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
            adu.write_text(json.dumps({"adu": {"rows": [{"DataID": "1234", "DataName": "ADU"}]}}))
            self.assertEqual([row[2] for row in _supplemental_rows({"regions": {"NA": {}}}, root)], ["adu-signal"])
            adu.unlink()
            (root / "pcs_data_viewer_tss3_managed_semantics.json").write_text(json.dumps({
                "operation_ffd": {"detail_rows": [{"DataID": "4321", "DataName": "FFD"}]},
                "rob_codes": {"rows": []},
            }))
            self.assertEqual([row[2] for row in _supplemental_rows({"regions": {"NA": {}}}, root)], ["ffd-signal"])

    def test_supplement_root_is_explicit_and_provenance_is_hashed(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            canonical=root/"generated"
            canonical.mkdir()
            filename="pcs_data_viewer_adu_semantics.json"
            document={"adu":{"rows":[{"DataID":"1234","DataName":"Canonical ADU"}]}}
            data=json.dumps(document).encode()
            (canonical/filename).write_bytes(data)
            candidate=root/"candidate"/"bundle"
            writer=DiagnosticBundleWriter(candidate)
            writer.add("index.json",io.BytesIO(json.dumps({
                "schema":"toyota-diagnostics-bundle-v4",
                "regions":{"NA":{"selected_categories":{},"vehicles":{}}}}).encode()))
            writer.finish()
            # Decoy next to candidate must not affect default source selection.
            (candidate.parent/filename).write_text("{}")
            out=root/"runtime.sqlite"
            with patch("tools.techstream.diag_runtime_db.DEFAULT_SUPPLEMENTAL_ROOT",canonical):
                export_runtime_db(candidate,out)
            with sqlite3.connect(out) as db:
                self.assertEqual(db.execute("SELECT name FROM items").fetchone()[0],"Canonical ADU")
                manifest=json.loads(db.execute("SELECT value FROM meta WHERE key='supplemental_sources'").fetchone()[0])
                loaded=[entry for entry in manifest if entry["status"]=="loaded"]
                self.assertEqual(loaded[0]["sha256"],hashlib.sha256(data).hexdigest())
                self.assertEqual(sum(entry["status"]=="missing" for entry in manifest),2)
                self.assertEqual(db.execute("SELECT member,pointer FROM item_sources").fetchone(),
                    ("supplement://" + filename,"/adu/rows/0"))
                self.assertEqual(restore_document(db, "supplement://" + filename), document)
            empty=root/"empty"
            empty.mkdir()
            export_runtime_db(candidate,out,supplemental_root=empty)
            with sqlite3.connect(out) as db:
                self.assertEqual(db.execute("SELECT count(*) FROM items").fetchone()[0],0)
                manifest=json.loads(db.execute("SELECT value FROM meta WHERE key='supplemental_sources'").fetchone()[0])
                self.assertTrue(all(entry["status"]=="missing" for entry in manifest))

    def test_shared_members_across_regions_and_escaped_pointers(self):
        member = "catalogs/shared.json"
        custom_member = "customize/shared.json"
        catalog = {"dids": {"odd/~key": [{"name": "Exact name", "nested": {"null": None}}]},
                   "metadata": {"opaque": [1, 2, 3]}}
        customize = {"groups": [{"group_id": 1, "name": "Shared group"}]}
        region = {"selected_categories": {"123": {"catalog_member": member}}, "vehicles": {},
                  "customize_member": custom_member}
        index = {"schema": "toyota-diagnostics-bundle-v4", "regions": {"NA": region, "EU": region}}
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
                self.assertEqual(db.execute("SELECT count(*) FROM runtime_documents").fetchone()[0], 3)
                self.assertEqual(db.execute("SELECT count(*) FROM items WHERE kind='did'").fetchone()[0], 2)
                for name, original in sources.items():
                    self.assertEqual(restore_document(db, name), original)
                self.assertEqual(set(row[0] for row in db.execute(
                    "SELECT pointer FROM item_sources WHERE member=?", (member,))), {"/dids/odd~1~0key/0"})

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
            writer.add("index.json", io.BytesIO(json.dumps({
                "schema": "toyota-diagnostics-bundle-v4",
                "regions": {"NA": {"selected_categories": {}, "vehicles": {}}}}).encode()))
            writer.finish()
            output = root / "runtime.sqlite"
            export_runtime_db(bundle, output, supplemental_root=supplemental)
            with sqlite3.connect(output) as db:
                self.assertEqual(restore_document(db, "supplement://" + filename), document)
                self.assertEqual(db.execute("SELECT count(*) FROM items").fetchone()[0], 0)

    def test_legacy_category_alias(self):
        self.assertEqual(_category_key(1, {"database": "Engine_P3.ddb"}), "engine")


if __name__ == "__main__":
    unittest.main()
