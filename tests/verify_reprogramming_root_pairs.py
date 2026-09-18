#!/usr/bin/env python3
"""Verify the committed cross-family reprogramming-root analysis artifact."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from analyze_reprogramming_root_pairs import DEFAULT_OUT, build


def main() -> int:
    expected = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    actual = build()
    assert actual == expected, "reprogramming-root analysis artifact drifted; regenerate it"
    assert actual["tracked_eps_reuse"]["matching_target_count"] == 5
    assert actual["cross_family_relationship_tests"]["shared_simple_fingerprints"] == []
    tests = actual["current_gtsplus"]["secret_info_relation_tests"]
    assert tests["one_step_root_pair_hits"] == []
    assert tests["pairwise_table_to_root_hits"] == []
    print("verify_reprogramming_root_pairs: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
