#!/usr/bin/env python3
"""Verify target-evidence schema, redacted example, and capture contract."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "docs/variants/target-artifact-manifest.schema.json"
EXAMPLE = REPO / "docs/variants/target-artifact-manifest.example.json"
VARIANT = REPO / "docs/variants/newer-tsk-target-evidence.md"
CAPTURE = REPO / "docs/tooling/techstream-capture-procedure.md"
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

capture_text = CAPTURE.read_text()
capture_words = " ".join(capture_text.split())
check("procedure names every operation", all(f"`{name}`" in capture_text for name in CAPTURES))
check("procedure retains decisive transport dimensions",
      all(token in capture_words for token in [
          "Tx/Rx direction", "elapsed timing", "ChannelID", "J2534 protocol",
          "four address bytes", "exact payload bytes",
      ]))
check("procedure requires hashing and redaction",
      "Hash the normalized JSON" in capture_text
      and "Raw Techstream logs and proprietary artifacts are never committed" in capture_text)
check("procedure uses locked parser command",
      "uv run --locked python tools/techstream/parse_ptshim_log.py" in capture_text)
check("runtime SecOC claim remains bounded",
      "no named/static `SecOC` or `VehSec` path was recovered" in capture_text)

variant_text = VARIANT.read_text()
check("variant report preserves hypothesis transfer grade",
      variant_text.count("| hypothesis |") >= 8)
check("variant report records zero exact artifacts/captures",
      "No exact newer-TSK part number" in variant_text
      and "labeled official Techstream capture is present" in variant_text)

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
