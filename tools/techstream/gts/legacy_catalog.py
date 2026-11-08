"""Compose decoded legacy source records without P5 protocol substitutions."""
from __future__ import annotations

from typing import Any, Callable

from tools.techstream.gts.legacy_active import legacy_active_patterns, legacy_active_tests
from tools.techstream.gts.legacy_freeze import legacy_freeze_rows
from tools.techstream.gts.legacy_signals import response_definitions, support_conditions


def _json_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def legacy_catalog_rows(
    db: Any, strings: Any, source: str, resolve_variable: Callable[[int], bytes],
) -> list[dict[str, Any]]:
    conditions = support_conditions(db, resolve_variable, source)
    rows = response_definitions(db, source)
    rows.extend({**row, "kind": "pid_bit" if row["table"] == 8 else "did_bit"}
                for row in conditions)
    rows.extend(legacy_freeze_rows(db, strings, source, conditions=conditions))
    rows.extend({**row, "kind": "active_test"} for row in legacy_active_tests(db, strings, source))
    rows.extend({**row, "kind": "active_test_pattern"} for row in legacy_active_patterns(db, source))
    return _json_value(sorted(rows, key=lambda row: (row["table"], row["record"])))
