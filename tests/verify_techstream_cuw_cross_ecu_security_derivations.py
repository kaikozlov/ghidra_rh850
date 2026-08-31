#!/usr/bin/env python3
"""Verify the deterministic CUW cross-ECU SecurityAccess derivation artifact."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/techstream"))

from analyze_cuw_cross_ecu_security_derivations import build

ART = ROOT / "data/generated/techstream_v18/cuw_cross_ecu_security_derivations.json"
expected = json.loads(ART.read_text())
actual = build()
assert actual == expected, "cross-ECU CUW derivation artifact drift"

control = actual["eps_control_specimen"]
assert control["eps_root_reproduces_actual_ecu_auth_key"] is True
assert control["actual_ecu_auth_key"] == "38adeef5ccae3f96d598d6fe9db14585"

pred = actual["high_value_non_eps_predictions"]
assert pred == {
    "0792": "5f1ca3df28378c808de34318288b056b",
    "07D2": "5693eea973333cf7a408bc86b1c98914",
    "0724": "192b8e45370251dff3b77f6bb069bf27",
}

groups = {(row["diag_id"], row["working_key"]): row for row in actual["credential_groups"]}
assert groups[("0792", "9318e0bfa4be96b787365ea2b5e26f3f")]["package_count"] == 6
assert groups[("07D2", "da4158ee9dd381cf7f9fc66da74682f3")]["package_count"] == 2
assert groups[("0724", "c178ed94d8dd00a65e520a536b7fa30c")]["package_count"] == 1
assert actual["simple_public_id_kdf_negative"]["matching_packages"] == []
assert all(trial["best_candidate"]["byte_identity_after_32"] < 0.01 for trial in actual["reprostd_image_key_trials"])

print("CUW cross-ECU SecurityAccess derivations: PASS")
