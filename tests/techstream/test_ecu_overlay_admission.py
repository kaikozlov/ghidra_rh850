"""Spe ECU facts are admitted separately, never overlaid onto Gen selection."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tools.techstream.gts.bundle import _bundle_ecu_overlays


class ECUOverlayAdmissionTests(unittest.TestCase):
    def fixture(self, tables):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        directory = root / "NA" / "DB" / "Spe"
        directory.mkdir(parents=True)
        (directory / "ABS_P4.ddb").write_bytes(b"fixture")
        (directory / "Toyota.ddb").write_bytes(b"master")
        parser = Mock()
        parser.parse_ecu_db.return_value = SimpleNamespace(
            sections={
                t: SimpleNamespace(header=SimpleNamespace(record_count=n))
                for t, n in tables.items()
            }
        )
        return root, parser

    def test_source_qualified_ordered_unknown_values(self):
        root, parser = self.fixture({54: 4})
        rows = [
            {
                "source": "ABS_P4.ddb",
                "table": 54,
                "record": i,
                "group_selector": 1,
                "freeze_frame_number": 15 - i,
                "exception_handler_id": 0,
                "exception_handler_flag": 0,
                "unassigned_bytes_2_4": f"{i + 1:02x}0000",
            }
            for i in range(4)
        ]
        with patch(
            "tools.techstream.gts.bundle.diagnostic_metadata",
            return_value={"operation_freeze": rows},
        ):
            value = _bundle_ecu_overlays(root, "NA", parser, None)
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0]["operation_freeze"], rows)
        self.assertEqual(
            value[0]["source_scope"],
            {"region": "NA", "family": "Spe", "database": "ABS_P4.ddb"},
        )
        self.assertEqual(value[0]["source_identity"]["path"], "NA/DB/Spe/ABS_P4.ddb")
        self.assertEqual(value[0]["activation"], {
            "status": "unresolved",
            "reason": "Vehicle-specific plugin selection, support gates and live activation are not established.",
        })
        self.assertEqual(value[0]["native_query"], {
            "ecu_loading": "lazy_same_family_selected_category_filename",
            "family_order": ["Gen", "Spe"],
            "merge": "concatenate_without_replacement_or_deduplication",
            "missing_family": "allowed_if_other_family_query_succeeds",
            "evidence": "docs/tooling/gts-query-cli.md#spe-ecu-operation-freeze-selection",
        })
        parser.parse_ecu_db.assert_called_once_with(root / "NA/DB/Spe/ABS_P4.ddb")

    def test_future_nonempty_table_cannot_disappear(self):
        root, parser = self.fixture({54: 4, 99: 1})
        with self.assertRaisesRegex(ValueError, "unadmitted"):
            _bundle_ecu_overlays(root, "NA", parser, None)

    def test_partial_decode_cannot_disappear(self):
        root, parser = self.fixture({54: 4})
        with (
            patch(
                "tools.techstream.gts.bundle.diagnostic_metadata",
                return_value={"operation_freeze": []},
            ),
            self.assertRaisesRegex(ValueError, "incomplete"),
        ):
            _bundle_ecu_overlays(root, "NA", parser, None)


if __name__ == "__main__":
    unittest.main()
