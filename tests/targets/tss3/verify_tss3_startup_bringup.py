#!/usr/bin/env python3
"""Verify the TSS3 startup race and native catch-marker bringup contract."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from exploit.ephemeral_runtime import (
    tss3_request_signer_ui_bringup as ui_bringup,
)
from exploit.ephemeral_runtime import (
    tss3_startup_programming as startup_programming,
)
from tools.targets.tss3.builders import (
    build_tss3_ram_kit as kit_builder,
)


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


class _FakeStartupRacePanda:
    def __init__(self, positive_frame: bytes):
        self.positive_frame = positive_frame
        self.sent: list[tuple[int, bytes, int]] = []
        self.recv_calls = 0

    def set_safety_mode(self, *_args):
        pass

    def can_recv(self):
        self.recv_calls += 1
        if self.recv_calls == 2:
            return [(startup_programming.RX_ADDR, self.positive_frame, startup_programming.BUS)]
        return []

    def can_send(self, address, data, bus):
        self.sent.append((address, bytes(data), bus))

    def close(self):
        pass


def run_cancelled_race(positive_frame: bytes) -> tuple[list[tuple[int, bytes, int]], str]:
    fake = _FakeStartupRacePanda(positive_frame)
    checks = iter((False, True))
    with (mock.patch.object(startup_programming, "ensure_boardd_stopped"),
          mock.patch.dict(sys.modules, {"panda": SimpleNamespace(Panda=lambda *_a, **_k: fake)})):
        try:
            startup_programming.race_to_bootloader(
                timeout=0.2, cancel_requested=lambda: next(checks),
            )
        except startup_programming.StartupProgrammingError as exc:
            return fake.sent, str(exc)
    raise AssertionError("race crossed the cancel boundary unexpectedly")


sent, cancel_error = run_cancelled_race(startup_programming.POSITIVE_EXTENDED_FRAME)
check("the exact response shared by all registered targets arms the one-way boundary",
      cancel_error == "startup race cancelled before PROGRAMMING" and
      any(data == startup_programming.EXTENDED_FRAME for _, data, _ in sent) and
      all(data != startup_programming.PROGRAMMING_FRAME for _, data, _ in sent))

for rejected_hex, label in (
    ("065003006401f400", "alternate P2 timing"),
    ("037f030111", "negative session response"),
):
    rejected_panda = _FakeStartupRacePanda(bytes.fromhex(rejected_hex))
    with (mock.patch.object(startup_programming, "ensure_boardd_stopped"),
          mock.patch.dict(sys.modules, {"panda": SimpleNamespace(
              Panda=lambda *_a, _panda=rejected_panda, **_k: _panda,
          )})):
        try:
            startup_programming.race_to_bootloader(timeout=0.1)
        except startup_programming.StartupProgrammingError as exc:
            check(f"{label} never arms PROGRAMMING", "no exact 50 03 response" in str(exc))
        else:
            raise AssertionError(f"race accepted {label}")

native_marker = {
    "schema": "tss3-oracle-native-catch-v1",
    "target": "TOYOTA_CAMRY_TSS3",
    "pandad_wrapper_pid": 1234,
    "ignition_monotonic_ns": 100,
    "first_extended_tx_monotonic_ns": 110,
    "positive_extended_monotonic_ns": 300,
    "positive_extended_frame_hex": "065003003201f400",
    "programming_tx_monotonic_ns": 310,
    "verdict": "programming_request_sent_after_exact_50_03",
}
with tempfile.TemporaryDirectory() as td:
    marker_path = Path(td) / "native-catch.json"
    marker_path.write_text(json.dumps(native_marker), encoding="utf-8")
    check("UI resume accepts an ordered native startup catch from any TSS3 platform",
          ui_bringup.load_native_catch(marker_path) == native_marker)
    marker_path.write_text(json.dumps({**native_marker, "target": "TOYOTA_COROLLA_TSS3"}), encoding="utf-8")
    check("UI resume does not re-derive the platform gate pandad already enforced",
          ui_bringup.load_native_catch(marker_path)["target"] == "TOYOTA_COROLLA_TSS3")
    for bad in (
        {"target": ""},
        {"verdict": "other"},
        {"programming_tx_monotonic_ns": 200},
        {"positive_extended_frame_hex": "065003006401f400"},
        {"positive_extended_frame_hex": "065002003201f400"},
        {"positive_extended_frame_hex": None},
    ):
        marker_path.write_text(json.dumps({**native_marker, **bad}), encoding="utf-8")
        try:
            ui_bringup.load_native_catch(marker_path)
        except ui_bringup.UiBringupError:
            pass
        else:
            raise AssertionError(f"UI resume accepted an invalid native startup catch: {bad}")

    check("status protocol is target-neutral",
          ui_bringup.STATUS_SCHEMA == "tss3-request-signer-ui-status-v1" and
          ui_bringup.WORKER_RESULT_SCHEMA == "tss3-request-signer-warm-worker-result-v1" and
          startup_programming.__name__.endswith("tss3_startup_programming"))

    for target in ("camry-8965F3307000", "crown-8965F3012000", "corolla-8965F1208000"):
        kit_meta = Path(td) / f"{target}.json"
        kit_meta.write_text(
            json.dumps({
                "target": {"name": target},
                # Stock-vehicle observation that must never select a runtime bus.
                "request": {"bus": 1},
            }), encoding="utf-8",
        )
        with mock.patch.object(
            ui_bringup, "race_to_bootloader", return_value={"schema": "tss3-startup-programming-v1"},
        ) as race:
            ui_bringup.manual_startup_race(kit_meta, cancel_requested=lambda: False)
        check(f"manual arm on {target} uses the shared repinned bus, not stock topology",
              "bus" not in race.call_args.kwargs and race.call_args.kwargs["target"] == target)

    record = {
        "name": "crown-8965F3012000",
        "ram_runtime": {"application_f181_hex": "ab", "request_bus": 1, "response_bus": 1},
    }
    base = {"schema": "tss3-request-signer-build-v1", "request": {}, "response": {},
            "state": {}, "authenticated_payload": {"sha256": "x"}}
    bound = kit_builder._bound_metadata(base, record)
    check("kit metadata binds the repinned runtime bus even for stock-bus-1 targets",
          bound["request"]["bus"] == 0 and bound["response"]["bus"] == 0 and
          bound["target"]["name"] == "crown-8965F3012000")

print("PASS TSS3 startup bringup")
