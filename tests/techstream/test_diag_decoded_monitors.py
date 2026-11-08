"""Lossless decoded fact schemas, including unresolved fields."""

import copy
import json
import sqlite3
import unittest
from tools.techstream.diag_decoded_monitors import Store, restore, SPECS
from tools.techstream.diag_freeze_physical import SCHEMA

SAMPLES = json.loads(
    r"""{"pattern": {"exception_handler_flag": 0, "exception_handler_id": 0, "key": 28, "name": "OFF", "name_string_index": 28783, "record": 58, "source": "Engine_P5.ddb", "table": 14, "unassigned_fields": {"14_15": "0100", "18_22": "0000000001", "8_11": "00000000"}, "value": 0}, "physical": {"decimal_point_count": 0, "div": 1, "exception_handler_flag": 0, "exception_handler_id": 0, "key": 3, "mul": 1, "offset": 0, "record": 2, "sign_mode": 0, "source": "Engine_P5.ddb", "table": 13, "unassigned_fields": {"18_19": "0000", "23": 0}, "unit_key": 0}, "unit": {"exception_handler_flag": 0, "exception_handler_id": 0, "genre_id": 0, "key": 0, "name": null, "name_string_index": 0, "record": 0, "source": "Engine_P5.ddb", "table": 15, "unassigned_fields": {"11": 0}}, "pcs_ffd": {"kind": "pcs_operation_ffd_pid", "pid": 129, "record": 0, "request": {"function_selector": 17, "pid_byte_offset": 3}, "retrieval_group": 1, "source": "PCS2_P4.ddb", "table": 86, "unassigned_word0": 1}, "data_id": {"did": 257, "exception_handler_flag": 0, "exception_handler_id": 0, "fixed_length": 0, "kind": "data_id", "record": 0, "source": "Engine_P5.ddb", "support_mode": 1, "table": 61}, "monitor": {"bit_end": 15, "bit_start": 15, "data_range_max": 1, "data_range_min": 0, "extraction_mode": 1, "ffd_support_condition_key": 0, "flags": 67, "graph_max": 1, "graph_min": 0, "kind": "monitor", "live_support_condition_key": 0, "monitor_key": 1, "name": "Immobiliser Communication", "name_string_index": 66295, "pattern_display_key": 28, "pattern_records": [{"exception_handler_flag": 0, "exception_handler_id": 0, "key": 28, "name": "OFF", "name_string_index": 28783, "record": 58, "source": "Engine_P5.ddb", "table": 14, "unassigned_fields": {"14_15": "0100", "18_22": "0000000001", "8_11": "00000000"}, "value": 0}, {"exception_handler_flag": 0, "exception_handler_id": 0, "key": 28, "name": "ON", "name_string_index": 28784, "record": 59, "source": "Engine_P5.ddb", "table": 14, "unassigned_fields": {"14_15": "0200", "18_22": "0000000001", "8_11": "00000000"}, "value": 1}], "physical_data_key": 3, "physical_max": 1.0, "physical_min": 0.0, "physical_records": [{"decimal_point_count": 0, "div": 1, "exception_handler_flag": 0, "exception_handler_id": 0, "key": 3, "mul": 1, "offset": 0, "record": 2, "sign_mode": 0, "source": "Engine_P5.ddb", "table": 13, "unassigned_fields": {"18_19": "0000", "23": 0}, "unit_key": 0}], "primary_did": 5631, "record": 0, "snapshot_did": 13823, "sort_key": 6180, "source": "Engine_P5.ddb", "table": 62, "unassigned_ranges": {"10_27": "000000000100000000000000010000000000000000000000", "2c_2f": "22bd0000", "44_45": "0000", "4c_4f": "00000000"}, "unit_records": [{"exception_handler_flag": 0, "exception_handler_id": 0, "genre_id": 0, "key": 0, "name": null, "name_string_index": 0, "record": 0, "source": "Engine_P5.ddb", "table": 15, "unassigned_fields": {"11": 0}}], "visibility_override": 0}, "condition": {"bit_end": 0, "bit_start": 0, "comparison_mode": 0, "comparison_value": 0, "condition_type": 7, "exception_handler_flag": 0, "exception_handler_id": 0, "key": 1, "kind": "support_condition", "record": 0, "referenced_did": 7936, "source": "Engine_P5.ddb", "table": 63, "unassigned_tail": 0, "variable_bytes": "1f00", "variable_id": 11278}, "condition_compact": {"bit_end": 7, "bit_start": 7, "condition_type": 7, "exception_handler_flag": 0, "exception_handler_id": 0, "key": 1, "kind": "support_condition", "record": 0, "referenced_did": 1027, "source": "Engine_P5.ddb", "table": 80, "variable_bytes": "0403", "variable_id": 11290}, "dtc_status": {"comparison_value": 1, "exception_handler_flag": 0, "exception_handler_id": 0, "key": 1, "kind": "dtc_status", "record": 0, "source": "Engine_P5.ddb", "status_mask": 1, "table": 66, "unassigned_fields": {"byte11": 0, "word4": 1}}, "dynamic_did": {"did": 62209, "exception_handler_flag": 0, "exception_handler_id": 0, "kind": "dynamic_did", "maximum_payload_length": 40, "record": 0, "source": "Engine_P5.ddb", "table": 81, "unassigned_tail": 0}, "behavior": {"behavior_code": 1280, "comment": null, "comment_string_index": 0, "kind": "behavior_code", "name": "Shift P Operation during Running", "name_string_index": 95820, "record": 0, "signature": "X0500", "source": "Engine_P5.ddb", "table": 87, "unassigned_tail": "000000010100"}, "rob_signal": {"bit_end": 31, "bit_start": 8, "did": 1282, "exception_handler_flag": 0, "exception_handler_id": 0, "extraction_mode": 2, "kind": "rob_signal", "name": "Total Distance Traveled", "name_string_index": 95989, "pattern_display_key": 0, "pattern_records": [], "physical_data_key": 3, "physical_records": [{"decimal_point_count": 0, "div": 1, "exception_handler_flag": 0, "exception_handler_id": 0, "key": 3, "mul": 1, "offset": 0, "record": 2, "sign_mode": 0, "source": "Engine_P5.ddb", "table": 13, "unassigned_fields": {"18_19": "0000", "23": 0}, "unit_key": 0}], "presentation_mode": 0, "record": 0, "record_key": 1, "sort_key": 1, "source": "Engine_P5.ddb", "support_condition_key": 0, "table": 88, "unassigned_ranges": {"0_1f": "0000000000000000000000000000000000000000000000000000000000000000", "24_2b": "a215010000000000", "40_41": "0000", "43_47": "0000000000"}, "unit_records": [{"exception_handler_flag": 0, "exception_handler_id": 0, "genre_id": 0, "key": 0, "name": null, "name_string_index": 0, "record": 0, "source": "Engine_P5.ddb", "table": 15, "unassigned_fields": {"11": 0}}]}, "rob_special": {"exception_handler_flag": 0, "exception_handler_id": 0, "key": 1, "kind": "rob_special_signal", "record": 0, "signal_key": 9900, "source": "Engine_P5.ddb", "table": 91, "unassigned_fields": {"tail9": "000000", "word6": 1}}}"""
)


class DecodedMonitorTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(
            "CREATE TABLE text_values(id INTEGER PRIMARY KEY,value TEXT UNIQUE);"
            + SCHEMA
        )
        self.store = Store(self.db)

    def expand(self, v):
        if isinstance(v, dict):
            if len(v) == 1 and next(iter(v)).startswith("$decoded_"):
                key = next(iter(v))
                return self.expand(restore(self.db, key[9:], v[key]))
            return {k: self.expand(x) for k, x in v.items()}
        if isinstance(v, list):
            return [self.expand(x) for x in v]
        return v

    def test_every_domain_exact_unknowns_and_reopen(self):
        for name, row in SAMPLES.items():
            marker = self.store.row(name, row)
            self.assertEqual(self.expand(marker), row)
            from tools.techstream.diag_metadata import restore as restore_product

            self.assertEqual(restore_product(self.db, marker), row)
            self.assertEqual(Store(self.db).row(name, row), marker)

    def test_future_nested_shape_makes_no_partial_writes(self):
        row = copy.deepcopy(SAMPLES["monitor"])
        row["pattern_records"][0]["future"] = 1
        before = self.db.total_changes
        self.assertEqual(self.store.row("monitor", row), row)
        self.assertEqual(self.db.total_changes, before)

    def test_order_duplicates_and_null_names(self):
        row = copy.deepcopy(SAMPLES["monitor"])
        row["name"] = None
        row["pattern_records"] *= 2
        row["physical_records"] *= 2
        marker = self.store.row("monitor", row)
        self.assertEqual(self.expand(marker), row)

    def test_nonzero_exception_and_unassigned_facts_preserved(self):
        row = copy.deepcopy(SAMPLES["physical"])
        row["exception_handler_flag"] = 3
        row["exception_handler_id"] = 987
        row["unassigned_fields"] = {"18_19": "A1b2", "23": 255}
        self.assertEqual(self.expand(self.store.row("physical", row)), row)

    def test_missing_child_rejected(self):
        marker = self.store.row("monitor", SAMPLES["monitor"])
        self.db.execute("DELETE FROM decoded_monitor_pattern_records WHERE position=0")
        with self.assertRaisesRegex(ValueError, "order"):
            self.expand(marker)

    def test_sources_never_coalesced(self):
        row = copy.deepcopy(SAMPLES["physical"])
        first = self.store.row("physical", row)
        row["source"] = "another.ddb"
        second = self.store.row("physical", row)
        self.assertNotEqual(first, second)
        self.assertEqual(self.expand(second), row)
