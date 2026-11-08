import sqlite3
import unittest

from tools.techstream.diag_signal_records import SCHEMA, Writer, Reader


def legacy():
    return dict(
        alternate_did=1026,
        bit_end=15,
        bit_start=0,
        data_range=[0, 65535],
        decimal_point_count=0,
        decoder="p5-linear-msb0-v1",
        div=1,
        graph_range=[0, 65535],
        monitor_key=9007199254740993,
        mul=1,
        name="Key Cycle",
        offset=0,
        patterns={"0": "No", "1": "Yes"},
        signed=False,
        unit=None,
    )


def modern():
    info = dict(
        bit_width=16,
        decimal_point_count=3,
        div=512,
        mul=625,
        offset=0,
        pattern_display={},
        physical_data_key=115,
        sign_mode=0,
        unit="V",
        unit_key=7,
    )
    support = dict(
        did=4098,
        fixed_length=2,
        record=0,
        snapshot_length_encoding="fixed",
        support_mode=0,
        table=61,
    )
    support["additional_records"] = [dict(support)]
    core = dict(
        alternate_did=4098,
        bit_end=15,
        bit_start=0,
        did_support=support,
        extraction_mode=2,
        flags=67,
        graph_range=[0, 79997],
        list_member=True,
        monitor_key=1,
        name="BATT Voltage",
        pattern_display_key=0,
        physical_data_key=115,
        physical_range=[0.0, 79.998],
        primary_did=4098,
        record=0,
        signal_info=info,
        sort_key=210,
        source="Engine_CM_P6.ddb",
        support_condition=None,
        table=62,
        visibility_override=0,
    )
    signal = {**core, **info, "decoder": "p6-native-msb0-u32-v1", "signal_info": info}
    display = {**core, "composite_records": [], "did": "0x1002", "wire_field": True}
    return signal, display


class SignalRecordTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(SCHEMA)
        self.writer = Writer(self.db)
        self.reader = Reader(self.db)
        self.addCleanup(self.db.close)

    def test_legacy_exact_and_large_integer(self):
        source = legacy()
        encoded = self.writer.transform(source)
        self.assertEqual(self.reader.definition(encoded["$signal_definition"]), source)
        self.assertEqual(self.writer.transform(source), encoded)
        display = {
            k: source[k] for k in ("bit_end", "bit_start", "monitor_key", "name")
        }
        display.update(did="0x0102", sort_key=0)
        ref = self.writer.transform(display)
        self.assertEqual(self.reader.display(ref["$data_list_row"]), display)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM signal_labels").fetchone()[0], 1
        )

    def test_modern_views_share_canonical_monitor(self):
        signal, display = modern()
        a = self.writer.transform(signal)
        b = self.writer.transform(display)
        self.assertEqual(self.reader.definition(a["$signal_definition"]), signal)
        self.assertEqual(self.reader.display(b["$data_list_row"]), display)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM signal_monitors").fetchone()[0], 1
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM signal_infos").fetchone()[0], 1
        )
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_unknown_shapes_and_values_remain_inline_without_orphans(self):
        cases = []
        for key, value in (
            ("monitor_key", True),
            ("div", 1 << 64),
            ("patterns", {"0": 123}),
            ("unit", 7),
        ):
            row = legacy()
            row[key] = value
            cases.append(row)
        row = legacy()
        row["future_field"] = 7
        cases.append(row)
        signal, display = modern()
        signal["mul"] = 99
        cases.append(signal)
        display["composite_records"] = [{"unknown": True}]
        cases.append(display)
        for row in cases:
            self.assertEqual(self.writer.transform(row), row)
        for table in (
            "signal_labels",
            "signal_infos",
            "signal_definitions",
            "data_list_rows",
            "text_values",
        ):
            self.assertEqual(
                self.db.execute(f"SELECT count(*) FROM {table}").fetchone()[0], 0, table
            )

    def test_standalone_semantics_reuse_the_same_entities(self):
        signal, _ = modern()
        self.writer.transform(signal)
        info = self.writer.transform(signal["signal_info"])
        support = self.writer.transform(signal["did_support"])
        self.assertEqual(self.reader.info(info["$signal_info"]), signal["signal_info"])
        self.assertEqual(
            self.reader.support(support["$did_support"]), signal["did_support"]
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM signal_infos").fetchone()[0], 1
        )
        condition = dict(
            bit_end=176,
            bit_start=176,
            comparison_mode=0,
            comparison_value=0,
            condition_type=7,
            key=4497,
            record=4496,
            referenced_did=4617,
            table=63,
            variable_bytes="00001209",
            variable_id=13534,
        )
        ref = self.writer.transform(condition)
        self.assertEqual(self.reader.condition(ref["$support_condition"]), condition)

    def test_legacy_info_null_labels_and_reopened_writer(self):
        signal, _ = modern()
        info = dict(signal["signal_info"])
        info["signed"] = True
        del info["sign_mode"]
        info["pattern_display"] = {"0": None, "1": "On"}
        ref = self.writer.transform(info)
        self.assertEqual(self.reader.info(ref["$signal_info"]), info)
        self.db.executescript(SCHEMA)
        reopened = Writer(self.db)
        self.assertEqual(reopened.transform(info), ref)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM signal_infos").fetchone()[0], 1
        )

    def test_all_condition_projection_shapes(self):
        full = dict(
            bit_end=7,
            bit_start=7,
            comparison_mode=0,
            comparison_value=0,
            condition_type=7,
            key=1,
            record=0,
            referenced_did=1027,
            table=63,
            variable_bytes="0403",
            variable_id=11290,
        )
        short = {
            k: v
            for k, v in full.items()
            if k not in ("comparison_mode", "comparison_value")
        }
        short["table"] = 80
        compact = {
            k: v
            for k, v in short.items()
            if k not in ("record", "table", "variable_bytes")
        }
        for condition in (full, short, compact):
            ref = self.writer.transform(condition)
            self.assertEqual(
                self.reader.condition(ref["$support_condition"]), condition
            )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM signal_conditions").fetchone()[0], 3
        )

    def test_shared_text_interleaved_writer(self):
        self.db.execute("INSERT INTO text_values(value) VALUES ('unrelated')")
        ref = self.writer.transform(legacy())
        self.assertEqual(self.reader.definition(ref["$signal_definition"]), legacy())

    def test_missing_and_noncontiguous_support_fail(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            self.reader.definition(99)
        signal, _ = modern()
        self.writer.transform(signal)
        self.db.execute("UPDATE signal_support_additional SET position=7")
        with self.assertRaisesRegex(ValueError, "noncontiguous"):
            self.reader.definition(1)

    def test_deleted_relation_rows_fail_instead_of_changing_output(self):
        self.writer.transform(legacy())
        self.db.execute(
            "DELETE FROM signal_pattern_entries WHERE key_id=(SELECT id FROM text_values WHERE value='0')"
        )
        with self.assertRaisesRegex(ValueError, "missing signal pattern"):
            self.reader.definition(1)
        signal, _ = modern()
        ref = self.writer.transform(signal)
        self.db.execute("DELETE FROM signal_support_additional")
        with self.assertRaisesRegex(ValueError, "missing additional"):
            self.reader.definition(ref["$signal_definition"])

    def test_source_mutation_does_not_affect_reconstruction(self):
        source = legacy()
        ref = self.writer.transform(source)
        first = self.reader.definition(ref["$signal_definition"])
        first["patterns"]["0"] = "mutated"
        self.assertEqual(self.reader.definition(ref["$signal_definition"]), source)


if __name__ == "__main__":
    unittest.main()
