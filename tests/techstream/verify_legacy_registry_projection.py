#!/usr/bin/env python3
"""Regression coverage for generation-neutral registry projection."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tools.techstream.gts.registry import _registry_active_test_groups, _registry_dtc_catalog

source_rows = [
    {"table": 5, "record": 0, "dtc_identifier": 0x1234, "code": "P1234",
     "description": "Legacy description", "comment": "OEM comment", "raw": b"\x12\x34"},
    {"table": 5, "record": 1, "dtc_identifier": "0x1234", "code": "P1234",
     "description": "Second variant", "raw": b"\x56"},
    {"table": 65, "record": 2, "packed_dtc": "0x123400", "code": "P123400",
     "description": "Modern description", "failure": "General failure", "raw": b"\x78"},
]
with patch("tools.techstream.gts.registry._dtc_rows", return_value=source_rows):
    catalog = _registry_dtc_catalog(None, None, None, "test")
assert set(catalog) == {"legacy:1234", "123400"}
assert len(catalog["legacy:1234"]) == 2
assert catalog["legacy:1234"][0]["dtc_identifier"] == 0x1234
assert catalog["legacy:1234"][0]["comment"] == "OEM comment"
assert catalog["legacy:1234"][0]["raw"] == "1234"
assert "packed_dtc" not in catalog["legacy:1234"][0]
assert "failure" not in catalog["legacy:1234"][0]
assert catalog["123400"][0]["packed_dtc"] == "0x123400"
assert json.loads(json.dumps(catalog)) == catalog
assert source_rows[0]["raw"] == b"\x12\x34"
with patch("tools.techstream.gts.registry._dtc_rows", return_value=[{"code": "unknown"}]):
    try:
        _registry_dtc_catalog(None, None, None, "test")
    except ValueError:
        pass
    else:
        raise AssertionError("identifier-less DTC silently discarded")

plan = {"group_count": 1, "membership_count": 2, "groups": [
    {"group_id": 17, "members": [
        {"member_active_test_id": 21, "input_slot": 1},
        {"member_active_test_id": 22, "input_slot": 2},
    ]}
]}
before = deepcopy(plan)
parser = SimpleNamespace(parse_ecu_db=Mock(return_value=SimpleNamespace(sections={33: object()})))
with patch("tools.techstream.gts.registry._multi_active_test_category_plan", return_value=plan), \
     patch("tools.techstream.gts.registry._direct_active_test_selected_row", side_effect=AssertionError("must not invent P5 materializer")):
    result = _registry_active_test_groups(parser, {"database": "legacy.ddb"}, Path("/db"), None)
assert plan == before
assert result["group_count"] == 1 and result["membership_count"] == 2
assert result["materializable_group_count"] == 0 and result["blocked_group_count"] == 1
assert result["groups"][0]["members"] == plan["groups"][0]["members"]
assert result["groups"][0]["execution"] == "unresolved_static_plan"
assert "type-68" in result["groups"][0]["reason"]
assert not any(k in result["groups"][0] for k in ("start_frame", "stop_frame", "did"))
assert json.loads(json.dumps(result)) == result
parser.parse_ecu_db.assert_called_once_with(Path("/db/legacy.ddb"))
print("[PASS] registry preserves distinct legacy/packed DTC identities, variants and JSON-safe provenance")
print("[PASS] type-33 legacy membership survives absent type-68 without fabricated execution")
