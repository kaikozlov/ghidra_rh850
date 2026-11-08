import unittest

from tools.techstream.gts.obd_monitor import (
    match_non_can_mode06_metadata, parse_non_can_mode06_result,
)


class NonCanMode06Test(unittest.TestCase):
    def test_maximum_limit_and_network_byte_order(self):
        result = parse_non_can_mode06_result(bytes.fromhex("4601011234abcd"))
        self.assertEqual(result, {
            "test_id": 1, "component_id": 1, "limit_type": "maximum",
            "raw_value": 0x1234, "raw_limit": 0xABCD,
            "raw_response": "4601011234abcd",
        })
        self.assertNotIn("passed", result)
        self.assertNotIn("unit", result)

    def test_minimum_limit_flag_is_not_part_of_component_id(self):
        result = parse_non_can_mode06_result(bytes.fromhex("4605810001ffff"))
        self.assertEqual(result["component_id"], 1)
        self.assertEqual(result["limit_type"], "minimum")
        self.assertEqual(result["raw_value"], 1)
        self.assertEqual(result["raw_limit"], 65535)
        self.assertEqual(parse_non_can_mode06_result(bytes.fromhex("4605ff00000000"))["component_id"], 127)

    def test_reject_other_formats_and_malformed_messages(self):
        for value in ("", "460100000000", "4601010000000000",
                      "4601010000000046010100000000", "41010100000000",
                      "46000100000000", "4621010100000000ffff"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_non_can_mode06_result(bytes.fromhex(value))

    def test_native_metadata_predicates_and_duplicate_variants(self):
        old = {"test_id": 1, "component_id": 1, "condition_ignore_mask": 13,
               "conditions": [{"value": 0, "operator": 0}, {"value": 99, "operator": 4},
                              {"value": 0, "operator": 0}, {"value": 0, "operator": 0}]}
        new = {**old, "conditions": [old["conditions"][0], {"value": 100, "operator": 3},
                                    *old["conditions"][2:]]}
        catalog = {"iso_results": [old, new, dict(new)]}
        frame = bytes.fromhex("46018100010002")
        self.assertEqual(match_non_can_mode06_metadata(catalog, frame, bytes([0,99,0,0])), [old])
        self.assertEqual(match_non_can_mode06_metadata(catalog, frame, bytes([0,100,0,0])), [new, new])
        with self.assertRaises(ValueError):
            match_non_can_mode06_metadata(catalog, frame, b"")
