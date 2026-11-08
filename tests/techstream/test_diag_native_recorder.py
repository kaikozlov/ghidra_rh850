import copy
import json
import sqlite3
import unittest
from tools.techstream.diag_native_recorder import Store, restore

SAMPLES = json.loads(
    r"""{"addresses": {"address": 0, "exception_flag": 0, "exception_id": 0, "family": "native-ddr-50", "header_member": true, "monitor_key": 1, "monitor_records": [{"record": 0, "table": 50}], "record": 0, "record_class": "CDbDDRAddressTable", "record_length": 0, "section_kind": 1, "source": "A_B_CAN_P4.ddb", "table": 52, "trigger_id": 2, "uninterpreted_bytes": {"13_15": "a5a5a5"}}, "invalid_conditions": {"combination_mode": 0, "comparison": "equal", "comparison_mode": 1, "comparison_value": 254, "condition_order": 1, "exception_flag": 0, "exception_id": 0, "family": "native-ddr-50", "record": 0, "record_class": "CDbDDRInvalidConditionTable", "referenced_signal_key": 3, "signal_key": 3, "source": "A_B_CAN_P4.ddb", "table": 53, "uninterpreted_bytes": {"15": "a5"}}, "monitors": {"bit_end": 7, "bit_start": 0, "data_max": 255, "data_min": 0, "exception_flag": 0, "exception_id": 0, "family": "native-ddr-50", "graph_max": 0, "graph_min": 0, "history_bit_end": 7, "history_bit_start": 0, "invalid_condition_records": [], "monitor_key": 1, "name": "Trigger ID", "name_string_index": 54695, "pattern_display_key": 0, "physical_data_key": 1, "presentation_mode": 2, "record": 0, "record_class": "CDbDDRMonitorTable", "signal_info": {"$signal_info": 147}, "sort_key": 10, "source": "A_B_CAN_P4.ddb", "table": 50, "uninterpreted_bytes": {"8_11": "a5a5a5a5", "42_43": "a5a5", "46_47": "a5a5"}}, "triggers": {"dependent_data_0": 500, "dependent_data_1": 1, "exception_flag": 0, "exception_id": 0, "family": "native-ddr-50", "header_parameters": [15, 16, 1, 0, 0, 0], "memo": "Accelerator pedal opening angle signal is high during low speed", "memo_string_index": 73442, "name": "Accelerator pedal opening angle signal is high during low speed", "name_string_index": 54881, "record": 0, "record_class": "CDbDDRTriggerTable", "source": "A_B_CAN_P4.ddb", "table": 51, "trigger_id": 2, "trigger_variant": 0, "uninterpreted_bytes": {"33_35": "a5a5a5"}}, "case_data_ids": {"case_did": 5377, "case_parameter": 36, "case_selector": 1, "exception_flag": 0, "exception_id": 0, "family": "native-ddr-110", "header_did": 5136, "record": 0, "record_class": "CDbDDRCaseInfoDataIdTable", "source": "A_B_CAN_P5.ddb", "table": 109, "uninterpreted_bytes": {"9": "a5", "11": "a5"}}, "header_data_ids": {"exception_flag": 0, "exception_id": 0, "family": "native-ddr-110", "header_did": 5136, "header_parameter": 62, "record": 0, "record_class": "CDbDDRHeaderInfoDataIdTable", "source": "A_B_CAN_P5.ddb", "table": 108, "uninterpreted_bytes": {"7": "a5"}}}"""
)


class NativeRecorderTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(
            "CREATE TABLE text_values(id INTEGER PRIMARY KEY,value TEXT UNIQUE);CREATE TABLE signal_infos(id INTEGER PRIMARY KEY);"
        )
        self.store = Store(self.db)

    def test_all_six_domains_and_reopen(self):
        for kind, row in SAMPLES.items():
            marker = self.store.row(kind, row)
            self.assertEqual(
                restore(self.db, kind, marker["$native_recorder_" + kind]), row
            )
            self.assertEqual(Store(self.db).row(kind, row), marker)

    def test_unknown_nested_field_writes_nothing(self):
        row = copy.deepcopy(SAMPLES["addresses"])
        row["monitor_records"][0]["future"] = 1
        before = self.db.total_changes
        self.assertEqual(self.store.row("addresses", row), row)
        self.assertEqual(self.db.total_changes, before)

    def test_order_duplicates_and_explicit_empty(self):
        row = copy.deepcopy(SAMPLES["addresses"])
        row["monitor_records"] *= 3
        marker = self.store.row("addresses", row)
        self.assertEqual(
            restore(self.db, "addresses", marker["$native_recorder_addresses"]), row
        )
        row["monitor_records"] = []
        marker = self.store.row("addresses", row)
        self.assertEqual(
            restore(self.db, "addresses", marker["$native_recorder_addresses"]), row
        )

    def test_source_binding_not_collapsed(self):
        row = copy.deepcopy(SAMPLES["case_data_ids"])
        first = self.store.row("case_data_ids", row)
        row["source"] = "other.ddb"
        second = self.store.row("case_data_ids", row)
        self.assertNotEqual(first, second)
        self.assertEqual(
            self.db.execute(
                "SELECT count(*) FROM native_recorder_case_data_ids_defs"
            ).fetchone()[0],
            1,
        )

    def test_unknown_ranges_preserve_presence_and_fail_closed(self):
        row = copy.deepcopy(SAMPLES["monitors"])
        row.pop("uninterpreted_bytes")
        marker = self.store.row("monitors", row)
        self.assertEqual(
            restore(self.db, "monitors", marker["$native_recorder_monitors"]), row
        )
        row["uninterpreted_bytes"] = {"future_range": "a1b2"}
        before = self.db.total_changes
        self.assertEqual(self.store.row("monitors", row), row)
        self.assertEqual(self.db.total_changes, before)
        known = copy.deepcopy(SAMPLES["monitors"])
        marker = self.store.row("monitors", known)
        self.db.execute(
            "UPDATE native_recorder_monitors_defs SET unknown_42_43_id=999999 WHERE uninterpreted_present=1"
        )
        with self.assertRaisesRegex(ValueError, "missing uninterpreted"):
            restore(self.db, "monitors", marker["$native_recorder_monitors"])

    def test_missing_link_rejected(self):
        self.store.row("addresses", SAMPLES["addresses"])
        self.db.execute("DELETE FROM native_recorder_addresses_links")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            restore(self.db, "addresses", 1)
