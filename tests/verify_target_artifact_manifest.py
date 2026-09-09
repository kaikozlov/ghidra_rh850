#!/usr/bin/env python3
"""Verify the machine-readable target-evidence schema and redacted example."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "docs/variants/target-artifact-manifest.schema.json"
EXAMPLE = REPO / "docs/variants/target-artifact-manifest.example.json"
CAPTURES = {
    "health_check", "data_list", "active_test_customization",
    "mackey_registration", "cuw_preparation",
    "reflash_authorization_programming",
}
ARTIFACTS = {"codeflash", "dataflash", "techstream", "regional_ddb_set", "cuw"}
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


schema = json.loads(SCHEMA.read_text())
example = json.loads(EXAMPLE.read_text())
check("schema version pinned", schema["properties"]["schema_version"]["const"] == 1
      and example["schema_version"] == 1)
check("required target artifacts exact", set(schema["properties"]["artifacts"]["required"])
      == ARTIFACTS == set(example["artifacts"]))
check("required capture operations exact", set(schema["properties"]["captures"]["required"])
      == CAPTURES == set(example["captures"]))
check("example honestly records missing target artifacts",
      all(row["status"] == "missing" and row["sha256"] is None
          for row in example["artifacts"].values()))
check("example honestly records missing live captures",
      all(row["status"] == "missing" and row["raw_log_sha256"] is None
          and row["normalized_sha256"] is None
          for row in example["captures"].values()))
check("committed privacy flags fail closed",
      example["privacy"] and not any(example["privacy"].values()))
check("example contains no VIN/account/server fields",
      not ({"vin", "account_id", "server_session_id", "license_key"}
           & set(example["target"])))

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
