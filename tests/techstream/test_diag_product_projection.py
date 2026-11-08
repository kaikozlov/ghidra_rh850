import unittest

from tools.techstream.diag_product_projection import project_document, retained_pointer


class ProductProjectionTests(unittest.TestCase):
    def test_command_contract_and_wire_bytes(self):
        command = {
            "execution": "unsupported",
            "reason": "binding unavailable",
            "plugin_binding": {
                "dll": "GetRoBP5_DT.dll",
                "exact_category_binding": False,
                "plugin_identity": {"sha256": "x", "path": "private.dll"},
                "native": {"context": {}, "status": 7},
            },
            "frames": [
                {
                    "send": "22f190",
                    "check": "62",
                    "mask": "ff",
                    "raw": "live-wire-example",
                    "bit_start": 8,
                    "byte_offset": 2,
                    "native": {"context": {}, "query": {}, "status": 7},
                }
            ],
        }
        result = project_document(
            "catalogs/NA/1.json",
            {"commands": [command], "selected_plugins": [{}], "source_tables": [{}]},
        )
        self.assertNotIn("selected_plugins", result)
        self.assertNotIn("source_tables", result)
        row = result["commands"][0]
        self.assertEqual(row["execution"], "unsupported")
        self.assertEqual(
            row["plugin_binding"],
            {"dll": "GetRoBP5_DT.dll", "exact_category_binding": False},
        )
        self.assertNotIn("native", row["frames"][0])
        self.assertEqual(row["frames"][0]["raw"], "live-wire-example")
        self.assertEqual(row["frames"][0]["send"], "22f190")
        self.assertEqual(row["frames"][0]["byte_offset"], 2)

    def test_dtc_and_signal_semantics(self):
        signal = {
            "decoder": "p5-linear-msb0-v1",
            "offset": -40,
            "div": 10,
            "patterns": {"1": "On"},
            "bit_end": 15,
            "bit_start": 0,
            "source": "A.ddb",
            "table": 10,
            "record": 1,
            "raw": "abcd",
        }
        out = project_document(
            "catalogs/NA/1.json",
            {
                "dids": {"1": [signal]},
                "dtcs": [
                    {
                        "code": "P0001",
                        "description": "Open",
                        "failure": "unsupported",
                        "source": "A.ddb",
                        "table": 11,
                        "record": 0,
                        "raw": "aa",
                    }
                ],
            },
        )
        self.assertEqual(
            out["dids"]["1"][0], {k: v for k, v in signal.items() if k != "raw"}
        )
        self.assertEqual(out["dtcs"][0]["failure"], "unsupported")
        self.assertNotIn("raw", out["dtcs"][0])

    def test_query_is_not_a_blanket_deleted_name(self):
        query = {"request_selector": 16, "variable_length": 1, "response_offset": 2}
        self.assertEqual(
            project_document("catalogs/NA/1.json", {"support": {"query": query}})[
                "support"
            ]["query"],
            query,
        )

    def test_index_and_supplement_scopes(self):
        index = {
            "regions": {
                "NA": {
                    "routes": {"1": [{"request": 123}]},
                    "raw_role_bindings": [{}],
                    "selected_categories": {
                        "1": {
                            "catalog_member": "catalogs/NA/1.json",
                            "catalog_context": {"query": {}},
                            "name": "Engine",
                        }
                    },
                }
            }
        }
        out = project_document("index.json", index)
        self.assertNotIn("raw_role_bindings", out["regions"]["NA"])
        self.assertEqual(
            out["regions"]["NA"]["routes"], index["regions"]["NA"]["routes"]
        )
        self.assertFalse(
            retained_pointer("index.json", "/regions/NA/raw_role_bindings/0")
        )
        self.assertEqual(
            project_document(
                "supplement://x",
                {"managed_identities": [{}], "image_ffd": {"status": "unsupported"}},
            ),
            {"image_ffd": {"status": "unsupported"}},
        )

    def test_unresolved_native_status_survives_projection(self):
        value = {
            "selectors": [
                {
                    "selector": "0x99",
                    "resolved": False,
                    "frames": [],
                    "native": {"context": {}, "query": {}, "status": 3221487873},
                }
            ]
        }
        row = project_document("catalogs/NA/1.json", value)["selectors"][0]
        self.assertEqual(row["resolution_status"], 3221487873)
        self.assertFalse(row["resolved"])
        self.assertNotIn("native", row)

    def test_research_traces_removed_but_unknown_source_values_retained(self):
        value = {
            "plugins": [{"dll": "Inventory.dll"}],
            "legacy_records": [
                {
                    "kind": "freeze_frame",
                    "table": 10,
                    "record": 1,
                    "bit_start": 5,
                    "native_consumers": ["RecoveredFunction"],
                    "unassigned_fields": {"padding": "ffff"},
                    "uninterpreted_fields": {"offset_7": 0},
                    "unassigned_bytes": {"offset_8": "ff"},
                    "unassigned_words": {"offset_10": 0},
                    "uninterpreted_words": {"offset_12": 0},
                    "physical_records": [{"mul": 2, "offset": -40}],
                }
            ],
            "commands": [
                {
                    "execution": "unsupported",
                    "native": {
                        "status": "unavailable",
                        "reason": "not supported",
                        "detail": "x" * 1000,
                    },
                    "unknown_semantic_field": 42,
                }
            ],
        }
        result = project_document("catalogs/NA/1.json", value)
        self.assertNotIn("plugins", result)
        row = result["legacy_records"][0]
        for key in (
            "unassigned_fields",
            "uninterpreted_fields",
            "unassigned_bytes",
            "unassigned_words",
            "uninterpreted_words",
        ):
            self.assertEqual(row[key], value["legacy_records"][0][key])
        self.assertNotIn("native_consumers", row)
        self.assertEqual(row["bit_start"], 5)
        self.assertEqual(row["physical_records"][0]["offset"], -40)
        command = result["commands"][0]
        self.assertNotIn("native", command)
        self.assertEqual(command["resolution_status"], "unavailable")
        self.assertEqual(command["resolution_reason"], "not supported")
        self.assertEqual(command["unknown_semantic_field"], 42)

    def test_uninterpreted_source_bytes_are_not_wire_data(self):
        value = {
            "work_factor": {
                "standard_info": [
                    {
                        "table": 18,
                        "record": 1,
                        "uninterpreted_bytes": {"11": "00"},
                        "byte_offset": 3,
                        "bit_start": 2,
                        "standard_value": "CLOSED",
                    }
                ]
            },
            "commands": [
                {
                    "send": "220123",
                    "raw": "62ff",
                    "uninterpreted_bytes": {"future_semantics": "preserved"},
                }
            ],
        }
        out = project_document("catalogs/NA/1.json", value)
        row = out["work_factor"]["standard_info"][0]
        self.assertEqual(row["uninterpreted_bytes"], {"11": "00"})
        self.assertEqual(row["byte_offset"], 3)
        self.assertEqual(row["bit_start"], 2)
        self.assertEqual(row["standard_value"], "CLOSED")
        self.assertEqual(out["commands"], value["commands"])

    def test_category_research_fields_and_derived_generation(self):
        row = {
            "raw": "abcdef",
            "handling_flag": 0,
            "handling_id": 0,
            "name_string_index": 55,
            "generation": 35,
            "generation_low5": 3,
            "support_plugin_single": {"dll": "Research.dll"},
            "support_plugin_multi": {"dll": "ResearchMulti.dll"},
            "name": "Engine",
            "support_family": "p3",
            "support_mode": "p3",
            "catalog_available": False,
        }
        value = {
            "regions": {"NA": {"selected_categories": {"1": row}}},
            "wire": {"raw": "abcdef", "generation_low5": 99},
        }
        out = project_document("index.json", value)
        category = out["regions"]["NA"]["selected_categories"]["1"]
        self.assertEqual(
            category,
            {
                k: row[k]
                for k in (
                    "generation",
                    "name",
                    "support_family",
                    "support_mode",
                    "catalog_available",
                    "handling_flag",
                    "handling_id",
                    "name_string_index",
                )
            },
        )
        self.assertEqual(out["wire"], value["wire"])
        row["catalog_database_path"] = "/private/research/source.ddb"
        owner = project_document("catalogs/NA/1.json", {"category": row})["category"]
        self.assertEqual(owner, category)
        self.assertEqual(
            project_document("supplement://other", {"category": row})["category"][
                "raw"
            ],
            "abcdef",
        )
        row["generation_low5"] = 7
        self.assertEqual(
            project_document("index.json", value)["regions"]["NA"][
                "selected_categories"
            ]["1"]["generation_low5"],
            7,
        )

    def test_customize_source_rows_preserve_decoded_fields_and_failure(self):
        row = {
            "source_ordinal": 7,
            "raw": "0011",
            "raw_u16_1e": 1,
            "write_bit_start": 7,
            "write_did": 123,
            "target_native_query": {"status": 9, "reason": "unresolved"},
            "choices": [{"source_ordinal": 0, "raw": "ff", "value": 1}],
        }
        source = {"items": [row], "wire": {"raw": "220123"}}
        result = project_document("customize/NA.json", source)
        item = result["items"][0]
        self.assertNotIn("raw", item)
        self.assertNotIn("target_native_query", item)
        self.assertEqual(item["raw_u16_1e"], 1)
        self.assertEqual(item["write_bit_start"], 7)
        self.assertEqual(item["target_resolution_status"], 9)
        self.assertEqual(item["target_resolution_reason"], "unresolved")
        self.assertEqual(item["choices"], [{"source_ordinal": 0, "value": 1}])
        self.assertEqual(result["wire"], source["wire"])
        self.assertEqual(project_document("supplement://unknown", source), source)

    def test_initial_categories_and_group_members_keep_semantics_not_records(self):
        value = {
            "regions": {
                "NA": {
                    "initial_categories": {
                        "1": {
                            "raw": "00",
                            "handling_flag": 0,
                            "name_string_index": 7,
                            "category_id": 1,
                            "name": "Engine",
                            "generation": 3,
                        }
                    }
                }
            }
        }
        self.assertEqual(
            project_document("index.json", value)["regions"]["NA"][
                "initial_categories"
            ]["1"],
            {
                "category_id": 1,
                "name": "Engine",
                "generation": 3,
                "handling_flag": 0,
                "name_string_index": 7,
            },
        )
        groups = {
            "active_test_groups": {
                "groups": [
                    {
                        "execution": "unresolved_static_plan",
                        "reason": "no materializer",
                        "members": [
                            {
                                "record": 0,
                                "raw": "0011",
                                "member_active_test_id": 2,
                                "input_slot": 1,
                                "unknown_word_04": 0,
                            }
                        ],
                    }
                ]
            }
        }
        result = project_document("catalogs/NA/1.json", groups)
        group = result["active_test_groups"]["groups"][0]
        self.assertEqual(group["execution"], "unresolved_static_plan")
        self.assertEqual(group["reason"], "no materializer")
        self.assertEqual(
            group["members"],
            [
                {
                    "record": 0,
                    "member_active_test_id": 2,
                    "input_slot": 1,
                    "unknown_word_04": 0,
                }
            ],
        )

    def test_source_only_diagnostics_survive_without_primary_counterparts(self):
        source = {
            "ddr": {"signals": [], "triggers": []},
            "native_ddr": {
                "monitors": [
                    {
                        "source": "A_B_CAN_P4.ddb",
                        "table": 50,
                        "record": 0,
                        "name": "Trigger ID",
                        "bit_start": 0,
                        "bit_end": 7,
                        "signal_info": {"mul": 1, "div": 1, "offset": 0},
                        "unassigned_words": {"10": 796},
                        "raw": "0011",
                    }
                ]
            },
            "monitor_source": [
                {
                    "source": "ECU.ddb",
                    "table": 61,
                    "record": 2,
                    "monitor_key": 77,
                    "exception_flag": 3,
                    "raw": "00",
                }
            ],
            "physical_catalog": {
                "units": [
                    {
                        "source": "ECU.ddb",
                        "table": 15,
                        "record": 9,
                        "text": "V",
                        "genre_id": 2,
                        "raw": "00",
                    }
                ]
            },
            "p6_rob_source": {
                "signals": [
                    {
                        "source": "ECU.ddb",
                        "table": 164,
                        "record": 3,
                        "signal_key": 7,
                        "visibility": 2,
                        "raw": "00",
                    }
                ]
            },
        }
        result = project_document("catalogs/EU/188.json", source)
        self.assertEqual(result["ddr"], {"signals": [], "triggers": []})
        self.assertEqual(
            result["native_ddr"]["monitors"],
            [
                {
                    "source": "A_B_CAN_P4.ddb",
                    "table": 50,
                    "record": 0,
                    "name": "Trigger ID",
                    "bit_start": 0,
                    "bit_end": 7,
                    "signal_info": {"mul": 1, "div": 1, "offset": 0},
                    "unassigned_words": {"10": 796},
                }
            ],
        )
        self.assertEqual(result["monitor_source"][0]["exception_flag"], 3)
        self.assertEqual(result["physical_catalog"]["units"][0]["text"], "V")
        self.assertEqual(result["p6_rob_source"]["signals"][0]["visibility"], 2)
        for root in (
            "native_ddr",
            "monitor_source",
            "physical_catalog",
            "p6_rob_source",
            "dtc_source",
        ):
            self.assertTrue(retained_pointer("catalogs/EU/188.json", "/" + root + "/0"))

    def test_dtc_source_admission_and_detail_links_are_diagnostic_facts(self):
        row = {
            "source": "Engine_P3.ddb",
            "table": 5,
            "record": 0,
            "code": "P0001",
            "enabled": False,
            "enabled_value": 2,
            "exception_handler_flag": 4,
            "exception_handler_id": 73,
            "detail_lookup_key": 1,
            "detail_table": 47,
            "unconsumed_descriptor_offsets": [24, 25],
            "uninterpreted_bytes": {"24": "ab"},
            "raw": "ab00",
        }
        result = project_document("catalogs/NA/1.json", {"dtc_source": [row]})
        self.assertEqual(
            result["dtc_source"],
            [
                {
                    "source": "Engine_P3.ddb",
                    "table": 5,
                    "record": 0,
                    "code": "P0001",
                    "enabled": False,
                    "enabled_value": 2,
                    "exception_handler_flag": 4,
                    "exception_handler_id": 73,
                    "detail_lookup_key": 1,
                    "detail_table": 47,
                    "unconsumed_descriptor_offsets": [24, 25],
                    "uninterpreted_bytes": {"24": "ab"},
                }
            ],
        )

    def test_input_not_mutated(self):
        value = {"monitor_source": [1], "dids": {"1": [{"name": "one"}]}}
        project_document("catalogs/NA/1.json", value)
        self.assertIn("monitor_source", value)


if __name__ == "__main__":
    unittest.main()
