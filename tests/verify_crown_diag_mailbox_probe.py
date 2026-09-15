#!/usr/bin/env python3
"""Offline behavioral fixtures for the Crown stock functional mailbox probe."""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.targets.crown.live import crown_f30_diag_mailbox_probe as probe


def check(label: str, condition: object) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[PASS] {label}")


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        self.now += 0.001
        return self.now

    def monotonic_ns(self) -> int:
        return int(self.monotonic() * 1_000_000_000)

    def sleep(self, seconds: float) -> None:
        self.now += max(float(seconds), 0.001)


class FakePanda:
    def __init__(self, responses: list[tuple[int, bytes, int]] | None = None) -> None:
        self.responses = list(responses or [])
        self.sent: list[tuple[int, bytes, int, bool, int]] = []
        self.safety: list[tuple[int, int]] = []
        self.canfd_auto: list[tuple[int, bool]] = []
        self.delivered = False

    def set_safety_mode(self, mode: int, param: int = 0) -> None:
        self.safety.append((int(mode), int(param)))

    def set_canfd_auto(self, bus: int, enabled: bool) -> None:
        self.canfd_auto.append((int(bus), bool(enabled)))

    def can_send(self, addr: int, dat: bytes, bus: int, *, fd: bool = False, timeout: int = 10) -> None:
        self.sent.append((int(addr), bytes(dat), int(bus), bool(fd), int(timeout)))

    def can_recv(self):
        if self.sent and not self.delivered:
            self.delivered = True
            return list(self.responses)
        return []


class FakeUds:
    class SESSION_TYPE:
        EXTENDED_DIAGNOSTIC = 3


class FakeClient:
    def __init__(self) -> None:
        self.sessions: list[int] = []

    def diagnostic_session_control(self, session: int) -> None:
        self.sessions.append(int(session))


def simulate(*, after: bytes, responses: list[tuple[int, bytes, int]] | None = None):
    panda = FakePanda(responses)
    client = FakeClient()
    panda_module = types.ModuleType("panda")
    panda_module.Panda = lambda: panda  # type: ignore[attr-defined]
    clock = FakeClock()
    reads = iter((b"\x00" * probe.MAILBOX_LENGTH, after))
    with (
        mock.patch.dict(sys.modules, {"panda": panda_module}),
        mock.patch.object(probe, "ensure_boardd_stopped") as stopped,
        mock.patch.object(probe, "_import_uds", return_value=FakeUds),
        mock.patch.object(probe, "_make_uds_client", return_value=client),
        mock.patch.object(probe, "_read_f181", return_value=(probe.EXPECTED_F181_HEX, "8965F3012000")),
        mock.patch.object(probe, "_read_memory", side_effect=lambda *a, **k: next(reads)),
        mock.patch.object(probe.time, "monotonic", side_effect=clock.monotonic),
        mock.patch.object(probe.time, "monotonic_ns", side_effect=clock.monotonic_ns),
        mock.patch.object(probe.time, "sleep", side_effect=clock.sleep),
    ):
        result = probe.run()
    return result, panda, client, stopped


check("probe frame is exact classic ISO-TP SF", probe.PROBE_FRAME == bytes.fromhex("07c7a50012340000"))
check("mailbox tail accepts either retained or DCM-cleared service byte",
      probe.mailbox_tail_matches(bytes.fromhex("c7a50012340000")) and
      probe.mailbox_tail_matches(bytes.fromhex("00a50012340000")))

result, panda, client, stopped = simulate(after=bytes.fromhex("00a50012340000"))
check("successful probe qualifies only the durable tail witness and no response",
      result["qualified"] is True and result["verdict"] == "stock_functional_mailbox_live" and
      result["mailbox"]["tail_match"] is True and result["mailbox"]["full_match"] is False and
      result["functional_response"]["none_observed"] is True)
check("probe uses ordinary ELM327 param1 and disables bus1 auto-FD",
      panda.safety == [(3, 1)] and panda.canfd_auto == [(1, False)])
check("probe transmits exactly one classic 0x777 frame",
      panda.sent == [(0x777, probe.PROBE_FRAME, 1, False, 10)])
check("probe binds EXTENDED and quiesces the Panda owner", client.sessions == [3] and stopped.call_count == 1)
check("probe mutation boundary excludes RAM execution, flash and actuation",
      result["mutation_boundary"]["ram_exec"] is False and
      result["mutation_boundary"]["flash_write"] is False and
      result["mutation_boundary"]["firmware_patch"] is False and
      result["mutation_boundary"]["actuation_request"] is False)

response_result, _, _, _ = simulate(
    after=bytes.fromhex("c7a50012340000"),
    responses=[(0x7A9, bytes.fromhex("037f c7 11 00000000".replace(" ", "")), 1)],
)
check("unexpected Crown diagnostic response rejects the mailbox proof",
      response_result["qualified"] is False and response_result["functional_response"]["none_observed"] is False)

mismatch_result, _, _, _ = simulate(after=bytes.fromhex("00110022334455"))
check("wrong DCM tail rejects the mailbox proof",
      mismatch_result["qualified"] is False and mismatch_result["mailbox"]["tail_match"] is False)

print("Crown functional diagnostic mailbox probe verification passed.")
