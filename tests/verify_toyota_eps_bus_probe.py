#!/usr/bin/env python3
"""Verify the non-destructive Toyota EPS Panda-bus discovery helper."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_eps_bus_probe import (
    APPLICATION_SOFTWARE_ID_DID,
    DEFAULT_BUSES,
    DEFAULT_ELM327_PARAM,
    ELM327_SAFETY_MODE,
    RX_ADDR,
    TX_ADDR,
    build_plan,
)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


print("== static safety contract ==")
plan = build_plan(DEFAULT_BUSES, DEFAULT_ELM327_PARAM)
check("probe uses EPS diagnostic TX 0x7A1", plan.tx_addr == TX_ADDR == 0x7A1)
check("probe uses EPS diagnostic RX 0x7A9", plan.rx_addr == RX_ADDR == 0x7A9)
check("probe reads only application software ID F181", plan.did == APPLICATION_SOFTWARE_ID_DID == 0xF181)
check("probe defaults to all three logical Panda buses", plan.buses == (0, 1, 2))
check("probe uses ELM327 safety mode", plan.elm327_safety_mode == ELM327_SAFETY_MODE == 3)
check("probe defaults to nonzero ELM327 param", plan.elm327_param == DEFAULT_ELM327_PARAM == 1)
check("probe declares no mutating services", plan.mutating_services == ())

print("\n== CLI dry-run ==")
script = REPO / "tools" / "toyota_eps_bus_probe.py"
run = subprocess.run(
    [sys.executable, str(script)],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("default CLI dry-run succeeds", run.returncode == 0, run.stderr.strip())
output = json.loads(run.stdout)
check("default CLI does not execute hardware", output["mode"] == "dry-run")
check("dry-run reports buses 0/1/2", output["plan"]["buses"] == [0, 1, 2])
check("dry-run reports F181", output["plan"]["did"] == 0xF181)
check("dry-run reports normal-routing ELM327 param", output["plan"]["elm327_param"] == 1)
check("routing note distinguishes OBD mux", "param=0" in output["routing_note"] and "logical bus 1" in output["routing_note"])

custom = subprocess.run(
    [sys.executable, str(script), "--bus", "1", "--elm327-param", "0"],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("explicit OBD-mux dry-run succeeds", custom.returncode == 0, custom.stderr.strip())
custom_output = json.loads(custom.stdout)
check("explicit bus selection is preserved", custom_output["plan"]["buses"] == [1])
check("explicit ELM327 param 0 is preserved", custom_output["plan"]["elm327_param"] == 0)

invalid = subprocess.run(
    [sys.executable, str(script), "--bus", "3"],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("invalid logical bus is rejected", invalid.returncode != 0)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
