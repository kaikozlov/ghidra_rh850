#!/usr/bin/env python3
"""Narrow transport/decoder checks for the parked Camry FRC DRCC gate probe."""
from __future__ import annotations

from tools.targets.camry.live.camry_frc_drcc_gate_probe import (
  FLOW_CONTROL,
  FRC_TX,
  decode_frc_pdu,
  isotp_request,
  single_frame,
)


class FakePanda:
  def __init__(self, batches):
    self.batches = list(batches)
    self.sent = []

  def can_send(self, address, data, bus, **kwargs):
    self.sent.append((address, bytes(data), bus, kwargs))

  def can_recv(self):
    return self.batches.pop(0) if self.batches else []


assert single_frame(bytes.fromhex("221905")) == bytes.fromhex("0322190500000000")

single = FakePanda([[(0x79A, bytes.fromhex("0562190500800000"), 1)]])
pdu = isotp_request(single, bytes.fromhex("221905"), 1)
assert pdu == bytes.fromhex("6219050080")
assert single.sent[0][:3] == (FRC_TX, bytes.fromhex("0322190500000000"), 1)
assert decode_frc_pdu(pdu)["cruise_control_allowed"] is True

multi = FakePanda([
  [(0x79A, bytes.fromhex("1009621906008000"), 1)],
  [(0x79A, bytes.fromhex("2100008000000000"), 1)],
])
pdu = isotp_request(multi, bytes.fromhex("221906"), 1)
assert pdu == bytes.fromhex("621906008000000080")
assert multi.sent[1][:3] == (FRC_TX, FLOW_CONTROL, 1)
decoded = decode_frc_pdu(pdu)
assert decoded["main_switch_recognized"] is True
assert decoded["acc_not_available_icon"] is True

print("[PASS][camry_frc_drcc_gate_probe] ISO-TP and FRC oracle decoding")
