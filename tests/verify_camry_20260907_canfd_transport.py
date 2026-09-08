#!/usr/bin/env python3
"""Verify the compact route-45 mixed CAN/CAN-FD transport evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/generated/camry_20260907_canfd_transport.json"


def rows_for(data: dict, addr: str) -> list[dict]:
  return data["matched_timing"]["special_frame_formats"].get(addr, [])


def main() -> int:
  data = json.loads(ARTIFACT.read_text())
  assert data["schema_version"] == 1
  scope = data["scope"]
  assert scope["matched_timing_route"] == "00000045--805b7ca6ab"
  assert scope["baseline_route"] == "0000003f--36e72f5fdc"
  assert scope["matched_openpilot_commit"] == "f8bd956a4b23eb4992c6abbe899e72b27cd91d80"

  matched = data["matched_timing"]
  assert len(matched["segments"]) == 15
  assert sum(s["bytes"] for s in matched["segments"]) == 149_376_764
  assert len({s["sha256"] for s in matched["segments"]}) == 15
  assert matched["harness_status_counts"] == {"flipped": 8714}

  # Native source PDUs are unambiguously Classical across the complete drive.
  r412 = rows_for(data, "0x412")
  assert sum(r["count"] for r in r412 if r["src"] < 3 and not r["fd"]) == 953
  assert sum(r["count"] for r in r412 if r["src"] < 3 and r["fd"]) == 0
  r101 = rows_for(data, "0x101")
  assert sum(r["count"] for r in r101 if r["src"] < 3 and not r["fd"]) == 44_242
  assert sum(r["count"] for r in r101 if r["src"] < 3 and r["fd"]) == 0

  # canfd_auto changed both short host replacements to FD on the wire.
  tx412 = matched["host_tx"]["0x412"]
  assert tx412["sendcan"] == [{"bus": 0, "count": 871, "fd": False, "length": 8}]
  assert tx412["returned"] == [{"bus": 0, "count": 870, "fd": True, "length": 8}]
  tx101 = matched["host_tx"]["0x101"]
  assert tx101["sendcan"] == [{"bus": 2, "count": 11, "fd": False, "length": 8}]
  assert {r["fd"]: r["count"] for r in tx101["returned"]} == {False: 43_272, True: 11}

  # B6 remains host-only under exact F33 timing; native stock traffic is still 08A.
  assert not any(r["src"] < 3 for r in rows_for(data, "0x0B6"))
  txb6 = matched["host_tx"]["0x0B6"]
  assert txb6["sendcan"] == [{"bus": 0, "count": 43_093, "fd": True, "length": 32}]
  assert txb6["returned"] == [{"bus": 0, "count": 43_083, "fd": True, "length": 32}]
  assert txb6["rejected"] == [{"bus": 0, "count": 9, "fd": True, "length": 32}]
  assert sum(r["count"] for r in rows_for(data, "0x08A") if r["src"] < 3 and r["fd"]) == 35_384

  # Matched 70% timing + EFBI exposed no new native address/DLC shape vs long route 3f.
  comparison = data["native_address_length_comparison"]
  assert all(not comparison[str(bus)]["new_only"] for bus in range(3))
  assert data["conclusions"]["matched_timing_new_native_address_length_signatures"] == 0

  # Split-network physical controllers (harness flipped: physical 0/2 = logical 2/0)
  # accumulated neither protocol errors, bus-off, nor FIFO loss during this route.
  health = {r["physical_can"]: r for r in matched["panda_health"]}
  for physical in (0, 2):
    assert health[physical]["total_error_growth"] == 0
    assert health[physical]["bus_off_growth"] == 0
    assert health[physical]["rx_lost_growth"] == 0
    assert health[physical]["tx_lost_growth"] == 0
  assert health[2]["max"]["receiveErrorCnt"] == 0

  assert data["conclusions"] == {
    "host_0x101_was_promoted_to_fd_by_canfd_auto": True,
    "host_0x412_was_promoted_to_fd_by_canfd_auto": True,
    "matched_timing_new_native_address_length_signatures": 0,
    "native_0x101_is_classical": True,
    "native_0x412_is_classical": True,
    "native_b6_frames": 0,
  }
  print("camry 2026-09-07 CAN-FD transport evidence: PASS")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
