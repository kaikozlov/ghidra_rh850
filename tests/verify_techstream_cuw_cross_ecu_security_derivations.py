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

print("CUW cross-ECU SecurityAccess derivations: PASS")
