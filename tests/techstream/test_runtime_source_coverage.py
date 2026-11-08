"""Original-source coverage must not inherit omissions from the projector."""

import copy
import unittest

from tests.techstream.verify_runtime_candidate import assert_original_source_coverage


class OriginalSourceCoverageTests(unittest.TestCase):
    def source(self):
        return {
            "monitor_source": [
                {
                    "record": 0,
                    "table": 6,
                    "enabled": True,
                    "raw": "dead",
                    "unassigned_fields": {"at_4": 7},
                }
            ],
            "physical_catalog": {
                "units": [{"record": 1, "unit": "V", "scaling": 0.5}],
                "patterns": [],
            },
            "native_ddr": {
                "monitors": [{"record": 2, "width": 16, "offset": 4, "scaling": 0.25}],
                "addresses": [],
            },
            "dtc_source": [
                {
                    "code": "P0001",
                    "enabled": True,
                    "enabled_value": 1,
                    "exception_handler_flag": 2,
                    "exception_handler_id": 7,
                    "detail_table": 47,
                    "detail_lookup_key": 4,
                }
            ],
            "p6_rob_source": {
                "signals": [{"record": 3, "bit_length": 8}],
                "behavior_codes": [],
            },
            "work_factor": {
                "standard_info": [{"uninterpreted_bytes": {"offset_2": "0100"}}]
            },
        }

    def check(self, a, b):
        assert_original_source_coverage(a, b, "catalogs/NA/1.json")

    def test_complete_and_raw_exclusion(self):
        source = self.source()
        actual = copy.deepcopy(source)
        del actual["monitor_source"][0]["raw"]
        self.check(source, actual)

    def test_every_decoded_root_required_even_empty(self):
        for root in [
            "monitor_source",
            "physical_catalog",
            "native_ddr",
            "dtc_source",
            "p6_rob_source",
        ]:
            with self.subTest(root=root):
                source = self.source()
                actual = copy.deepcopy(source)
                del actual[root]
                with self.assertRaises(AssertionError):
                    self.check(source, actual)

    def test_dtc_enabled_exception_and_detail_fields(self):
        for key in [
            "enabled",
            "enabled_value",
            "exception_handler_flag",
            "exception_handler_id",
            "detail_table",
            "detail_lookup_key",
        ]:
            source = self.source()
            actual = copy.deepcopy(source)
            del actual["dtc_source"][0][key]
            with self.subTest(key=key), self.assertRaises(AssertionError):
                self.check(source, actual)

    def test_geometry_and_order_and_types(self):
        for mutate in [
            lambda a: a["native_ddr"]["monitors"][0].update(width=8),
            lambda a: a["dtc_source"][0].update(enabled=1),
            lambda a: a["p6_rob_source"]["signals"].clear(),
            lambda a: a["physical_catalog"]["units"][0].update(scaling=1),
        ]:
            source = self.source()
            actual = copy.deepcopy(source)
            mutate(actual)
            with self.assertRaises(AssertionError):
                self.check(source, actual)

    def test_nonzero_unknowns_outside_and_inside_roots(self):
        for root in ["monitor_source", "work_factor"]:
            source = self.source()
            actual = copy.deepcopy(source)
            if root == "monitor_source":
                del actual[root][0]["unassigned_fields"]
            else:
                del actual[root]["standard_info"][0]["uninterpreted_bytes"]
            with self.assertRaises(AssertionError):
                self.check(source, actual)

    def test_category_decoded_fields(self):
        source = {
            "category": {
                "category_id": 5,
                "handling_flag": 3,
                "handling_id": 7,
                "name_string_index": 9,
                "raw": "beef",
            }
        }
        for key in ("category_id", "handling_flag", "handling_id", "name_string_index"):
            actual = copy.deepcopy(source)
            del actual["category"][key]
            with self.subTest(key=key), self.assertRaises(AssertionError):
                self.check(source, actual)

    def test_exact_generation_low5_derivation_only(self):
        source = {"category": {"generation": 39, "generation_low5": 7}}
        self.check(source, {"category": {"generation": 39}})
        for actual in ({"category": {"generation": 7}}, {"category": {}}):
            with self.assertRaises(AssertionError):
                self.check(source, actual)
        source["category"]["generation_low5"] = 8
        with self.assertRaises(AssertionError):
            self.check(source, {"category": {"generation": 39}})

    def test_overlay_scope_and_activation_are_source_facts(self):
        source = [
            {
                "source_scope": {
                    "region": "NA",
                    "family": "Spe",
                    "database": "ABS.ddb",
                },
                "activation": {"status": "unresolved"},
                "operation_freeze": [{"freeze_frame_number": 15}],
            }
        ]
        member = "index.json#/regions/NA/ecu_overlays"
        counts = assert_original_source_coverage(source, copy.deepcopy(source), member)
        self.assertEqual(counts["overlay_rows"], 1)
        for key in ("source_scope", "activation", "operation_freeze"):
            actual = copy.deepcopy(source)
            del actual[0][key]
            with self.assertRaises(AssertionError):
                assert_original_source_coverage(source, actual, member)

    def test_raw_integer_names_not_vendor_blobs(self):
        source = {"native_ddr": {"raw_u16": 9}}
        with self.assertRaises(AssertionError):
            self.check(source, {"native_ddr": {}})


if __name__ == "__main__":
    unittest.main()
