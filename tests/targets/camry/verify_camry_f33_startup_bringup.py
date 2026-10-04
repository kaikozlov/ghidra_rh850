#!/usr/bin/env python3
"""Verify the exact-F33 startup race and native catch-marker bringup contract."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from exploit.ephemeral_runtime import (
    camry_f33_request_signer_ui_bringup as ui_bringup,
)
from exploit.ephemeral_runtime import (
    camry_f33_startup_programming as startup_programming,
)
from tools import REPO_ROOT

ROOT = REPO_ROOT


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


class _FakeStartupRacePanda:
    def __init__(self):
        self.sent: list[tuple[int, bytes, int]] = []
        self.recv_calls = 0

    def set_safety_mode(self, *_args):
        pass

    def can_recv(self):
        self.recv_calls += 1
        if self.recv_calls == 2:
            return [(startup_programming.RX_ADDR, startup_programming.POSITIVE_EXTENDED_FRAME, startup_programming.BUS)]
        return []

    def can_send(self, address, data, bus):
        self.sent.append((address, bytes(data), bus))

    def close(self):
        pass


fake_race_panda = _FakeStartupRacePanda()
cancel_checks = iter((False, True))
with (mock.patch.object(startup_programming, "ensure_boardd_stopped"),
      mock.patch.dict(sys.modules, {"panda": SimpleNamespace(Panda=lambda *_a, **_k: fake_race_panda)})):
    try:
        startup_programming.race_to_bootloader(
            timeout=0.2, cancel_requested=lambda: next(cancel_checks),
        )
    except startup_programming.StartupProgrammingError as exc:
        cancel_error = str(exc)
    else:
        raise AssertionError("cooperative cancel crossed the PROGRAMMING boundary")
check("manual cancellation is honored after 50 03 but before the one-way 10 02 send",
      cancel_error == "startup race cancelled before PROGRAMMING" and
      any(data == startup_programming.EXTENDED_FRAME for _, data, _ in fake_race_panda.sent) and
      all(data != startup_programming.PROGRAMMING_FRAME for _, data, _ in fake_race_panda.sent))

native_marker = {
    "schema": "tss3-oracle-native-catch-v1",
    "target": "TOYOTA_CAMRY_TSS3",
    "pandad_wrapper_pid": 1234,
    "ignition_monotonic_ns": 100,
    "first_extended_tx_monotonic_ns": 110,
    "positive_extended_monotonic_ns": 300,
    "programming_tx_monotonic_ns": 310,
    "verdict": "programming_request_sent_after_exact_50_03",
}
with tempfile.TemporaryDirectory() as td:
    marker_path = Path(td) / "native-catch.json"
    marker_path.write_text(json.dumps(native_marker), encoding="utf-8")
    check("UI resume accepts only an ordered exact-F33 native startup catch",
          ui_bringup.load_native_catch(marker_path) == native_marker)
    marker_path.write_text(json.dumps({**native_marker, "target": "TOYOTA_COROLLA_TSS3"}), encoding="utf-8")
    try:
        ui_bringup.load_native_catch(marker_path)
    except ui_bringup.UiBringupError:
        pass
    else:
        raise AssertionError("UI resume accepted a non-F33 native startup catch")

print("PASS Camry F33 startup bringup")
