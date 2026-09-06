#!/usr/bin/env python3
"""Verify the tracked 2026-09-06 Camry hands-off warning reduction."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
report = json.loads((REPO / "data/generated/camry_20260906_hands_off_warning_audit.json").read_text())
routes = report["routes"]


def check(name: str, condition: bool) -> None:
  if not condition:
    raise AssertionError(name)
  print(f"[PASS] {name}")


for short, expected in (("3e", 43), ("3f", 63)):
  w = routes[short]["warning_candidate"]
  state = w["onset_openpilot_state"]
  check(f"{short} warning onset count", w["rising_edges"] == expected)
  check(f"{short} onset while latActive", state["lat_active_true"] == expected)
  check(f"{short} onset while selfdrive enabled", state["selfdrive_enabled_true"] == expected)
  check(f"{short} onset before steeringPressed", state["steering_pressed_true"] == 0)
  check(f"{short} onset with active B6 ID11", state["b6_id11"] == expected)
  check(f"{short} Toyota timer median ~16 s", 15.0 <= w["onset_time_since_touch_s"]["p50"] <= 17.0)

hud3e = routes["3e"]["hud_companion_candidate"]
hud3f = routes["3f"]["hud_companion_candidate"]
check("3e normal HUD payload observed", hud3e["payload_counts"].get("1400004401ee9307", 0) > 1000)
check("3e warning HUD payload observed", hud3e["payload_counts"].get("140c004401ee9307", 0) > 100)
check("3f normal HUD payload observed", hud3f["payload_counts"].get("1400004401ee9307", 0) > 1000)
check("3f warning HUD payload observed", hud3f["payload_counts"].get("140c004401ee9307", 0) > 100)
check("3f escalation payload observed exactly six times", hud3f["payload_counts"].get("140c404401ee9307") == 6)
check("all B2[6] escalation frames occur during 0x371 warning state",
      hud3f["b2_bit6_frames"] == 6 and hud3f["b2_bit6_frames_while_0x371_active"] == 6)
check("3e all qualified 0x371 rises have paired HUD edges",
      hud3e["rise_edges_paired_to_0x371_within_2s"] == routes["3e"]["warning_candidate"]["rising_edges"])
check("3f all qualified 0x371 rises have paired HUD edges",
      hud3f["rise_edges_paired_to_0x371_within_2s"] == routes["3f"]["warning_candidate"]["rising_edges"])
