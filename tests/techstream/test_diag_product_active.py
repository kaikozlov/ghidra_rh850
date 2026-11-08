import sqlite3
import unittest

from tools.techstream.diag_product_active import (
    CONVERSION,
    DDL,
    ENCODING,
    MASK,
    OperationStore,
    restore,
)


class ProductActiveTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(DDL)
        self.store = OperationStore(self.db)

    def tearDown(self):
        self.db.close()

    def test_frames_share_wire_facts_preserve_empty_and_identifiers(self):
        base = dict(
            category_id=1,
            comm_frame_id="0x12",
            comm_set=2,
            selector="0x9D",
            kind="frame",
            send={"bytes": "2f123400", "id": "0x10", "normalized_id": "0x10"},
            receive_mask={"bytes": "", "id": "0x0", "normalized_id": "0x0"},
            receive_check={"bytes": "6f", "id": "0x20", "normalized_id": "0x20"},
            comm_set_metadata=dict(
                comm_set_id=2,
                receive_timeout=4294967295,
                retry_count=3,
                send_parameter=1000,
                unknown_word_0c=0,
                exception_handler_id=0,
                exception_handler_flag=0,
            ),
        )
        named = dict(
            selector="0x9D",
            frame="0x12",
            comm_set=2,
            send="2f123400",
            mask="",
            check="6f",
            receive_timeout=4294967295,
            retry_count=3,
            name="start",
            session_requirement="extended",
        )
        for row in (base, named):
            ref = self.store.normalize(row)
            marker, identity = next(iter(ref.items()))
            self.assertEqual(restore(self.db, marker, identity), row)
        self.assertEqual(
            self.db.execute("select count(*) from operation_wire_frames").fetchone()[0],
            1,
        )

    def test_policy_types_and_refusals(self):
        enc = dict(
            zip(
                ENCODING,
                (True, False, "not-supported", "source", "input", "adapter", "engine"),
            )
        )
        root = {
            "execution": "plan_only",
            "resolution_status": 3221487873,
            "encoding_requirements": enc,
            "control_enable_mask": dict(zip(MASK, ("start", "stop", "rule"))),
            "engineering_to_raw": dict(zip(CONVERSION, ("formula", "source", "input"))),
        }
        out = self.store.normalize(root)
        for field in (
            "encoding_requirements",
            "control_enable_mask",
            "engineering_to_raw",
        ):
            marker, identity = next(iter(out[field].items()))
            self.assertEqual(restore(self.db, marker, identity), root[field])
        self.assertEqual(out["execution"], "plan_only")
        self.assertEqual(out["resolution_status"], 3221487873)
        invalid = dict(enc, p5_supported=1)
        self.assertEqual(
            self.store.normalize(invalid, "encoding_requirements"), invalid
        )

    def test_unknown_semantics_remain_inline(self):
        row = dict(zip(MASK, ("start", "stop", "rule")))
        row["future_safety_gate"] = True
        self.assertEqual(self.store.normalize(row, "control_enable_mask"), row)

    def test_bad_references_fail(self):
        for marker, identity in (
            ("$operation_frame", True),
            ("$operation_frame", 0),
            ("$operation_frame", 99),
            ("$bad", 1),
        ):
            with self.assertRaises(ValueError):
                restore(self.db, marker, identity)


if __name__ == "__main__":
    unittest.main()
