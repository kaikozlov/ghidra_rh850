import copy
import sqlite3
import unittest

from tools.techstream.diag_support_semantics import SupportStore, restore


def member(record, identifier):
    return dict(
        identifier=identifier,
        list_key=7,
        exception_handler_flag=0,
        exception_handler_id=0,
        source="ECU.ddb",
        table=1,
        record=record,
    )


def group():
    return dict(
        group_id=3,
        list_key=7,
        member_table=1,
        name="Data",
        name_string_index=9,
        exception_handler_flag=0,
        exception_handler_id=0,
        source="ECU.ddb",
        table=0,
        record=0,
        member_records=[1, 0, 1],
        members=[2**53 + 1, 10, 2**53 + 1],
    )


def catalog():
    return {
        "support_catalog": {
            "signal_groups": [group()],
            "signal_memberships": [member(0, 10), member(1, 2**53 + 1)],
        }
    }


class SupportTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.store = SupportStore(self.db)

    def test_order_duplicates_and_shared_members(self):
        original = catalog()
        before = copy.deepcopy(original)
        out = self.store.normalize(original)["support_catalog"]
        identity = out["signal_groups"][0]["$support_group_facts"]
        self.assertEqual(restore(self.db, "$support_group_facts", identity), group())
        self.assertEqual(original, before)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM support_member_origins").fetchone()[
                0
            ],
            2,
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM support_group_links").fetchone()[0], 3
        )

    def test_query_rules_and_freeze_policy_exact(self):
        query = dict(
            query_id=7,
            policy=1,
            exception_handler_flag=0,
            exception_handler_id=0,
            kind="did",
            requires_previously_supported_query_id_in_p4=True,
            source="ECU.ddb",
            table=3,
            record=2,
        )
        freeze = dict(
            freeze_frame_number=2,
            exception_handler_flag=0,
            exception_handler_id=0,
            request_variable_byte_by_frame_length={"3": 2, "4": 1},
            source="ECU.ddb",
            table=2,
            record=0,
        )
        out = self.store.normalize(
            {
                "support_catalog": {
                    "support_queries": [query],
                    "freeze_frame_queries": [freeze],
                }
            }
        )["support_catalog"]
        for field, row in (
            ("support_queries", query),
            ("freeze_frame_queries", freeze),
        ):
            ref = out[field][0]
            marker = next(iter(ref))
            self.assertEqual(restore(self.db, marker, ref[marker]), row)

    def test_unknown_and_unresolved_groups_stay_inline(self):
        original = catalog()
        original["support_catalog"]["signal_groups"][0]["members"][0] = 99
        out = self.store.normalize(original)
        self.assertEqual(
            out["support_catalog"]["signal_groups"],
            original["support_catalog"]["signal_groups"],
        )
        original = catalog()
        original["support_catalog"]["signal_groups"][0]["new_semantics"] = True
        self.assertEqual(
            self.store.normalize(original)["support_catalog"]["signal_groups"],
            original["support_catalog"]["signal_groups"],
        )

    def test_missing_tail_and_wrong_member_origin_fail(self):
        ref = self.store.normalize(catalog())["support_catalog"]["signal_groups"][0]
        identity = ref["$support_group_facts"]
        self.db.execute("DELETE FROM support_group_links WHERE position=2")
        with self.assertRaisesRegex(ValueError, "incomplete support group"):
            restore(self.db, "$support_group_facts", identity)

    def test_cross_context_link_fails(self):
        ref = self.store.normalize(catalog())["support_catalog"]["signal_groups"][0]
        identity = ref["$support_group_facts"]
        self.db.execute("UPDATE support_member_origins SET table_number=99")
        with self.assertRaisesRegex(ValueError, "inconsistent support group origin"):
            restore(self.db, "$support_group_facts", identity)


if __name__ == "__main__":
    unittest.main()
