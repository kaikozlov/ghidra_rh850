#!/usr/bin/env python3
"""Verify the TSS3 startup race and native catch-marker bringup contract."""
from __future__ import annotations

import io
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import tsk.ram_runtime.tss3_request_signer_ui_bringup as ui_bringup
import tsk.ram_runtime.tss3_startup_programming as startup_programming


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
    prewarm_marker = {**native_marker, "ignition_monotonic_ns": 0}
    marker_path.write_text(json.dumps(prewarm_marker), encoding="utf-8")
    check("UI resume accepts a prewarm catch before ignition",
          ui_bringup.load_native_catch(marker_path) == prewarm_marker)
    for bad in (
        {"target": ""},
        {"verdict": "other"},
        {"ignition_monotonic_ns": -1},
        {"programming_tx_monotonic_ns": 0},
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
        check(f"manual arm on {target} uses the shared repinned bus",
              "bus" not in race.call_args.kwargs and race.call_args.kwargs["target"] == target)


class _Clock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def monotonic_ns(self):
        return int(self.now * 1e9)

    def sleep(self, seconds):
        self.now += seconds


class _AwakePanda:
    def __init__(self, clock, answer_after):
        self.clock = clock
        self.answer_after = answer_after
        self.sent = []
        self.closed = False
        self.power_changes = []

    def can_recv(self):
        self.clock.sleep(0.25)
        rows = [(0x101, b"vehicle", 0)]
        if self.clock.now >= self.answer_after:
            rows.append((0x7A9, startup_programming.POSITIVE_EXTENDED_FRAME, 0))
        return rows

    def can_send(self, address, data, bus):
        self.sent.append((address, data, bus))

    def set_safety_mode(self, *_args):
        pass

    def set_power_save(self, value):
        self.power_changes.append(value)

    def close(self):
        self.closed = True

    def health(self):
        return {"ignition_line": self.clock.now >= self.answer_after, "ignition_can": False}


for answer_after in (0.5, 80.0):
    clock = _Clock()
    panda = _AwakePanda(clock, answer_after)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        meta = root / "meta.json"
        meta.write_text(json.dumps({"target": {"name": "camry-8965F3307000"}}))
        marker = root / "native.json"
        marker.write_text(json.dumps(native_marker))
        output = io.StringIO()
        with (mock.patch.object(ui_bringup, "time", clock),
              mock.patch.object(startup_programming, "time", clock),
              mock.patch.object(ui_bringup, "_emit_stream", output),
              mock.patch.object(ui_bringup, "install", side_effect=[
                  ui_bringup.BootloaderNotReachedError("EPS did not enter boot"),
                  {"verdict": "request_signer_live_probe_pass"},
              ]) as installer,
              mock.patch.object(startup_programming, "ensure_boardd_stopped"),
              mock.patch.object(startup_programming, "_read_boot_identity", return_value=(
                  startup_programming.EXPECTED_BOOT_F181_HEX, [],
              )),
              mock.patch.dict(sys.modules, {"panda": SimpleNamespace(Panda=None)}),
              mock.patch.object(ui_bringup, "recovery_target", return_value="camry-8965F3307000"),
              mock.patch.object(ui_bringup, "control_domain_state", return_value={"peer_health": {"state": "healthy"}}),
              mock.patch.object(ui_bringup, "self_test", return_value={"passed": True})):
            result = ui_bringup.run(root / "payload", meta, root / "run", native_catch=marker, panda=panda)
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        check(f"automatic arming catches a start after {answer_after}s of awake bus",
              installer.call_count == 2 and any(data == startup_programming.PROGRAMMING_FRAME for _, data, _ in panda.sent)
              and result["verdict"] == "startup_caught_fresh_signer_peer_state_healthy_self_test_pass"
              and all(not row["error"] for row in rows))
        check("automatic re-arm retains its Panda connection and leaves power saving alone",
              not panda.closed and not panda.power_changes)


clock = _Clock()
raw = SimpleNamespace(can_recv=lambda: [(0x7A9, b"diagnostic", 0), (0x777, b"signer", 0), (0x101, b"echo", 128)])
with mock.patch.object(ui_bringup, "time", clock):
    observed = ui_bringup._BusActivityPanda(raw)
    clock.sleep(4.0)
    observed.can_recv()
    try:
        observed.check_awake()
    except ui_bringup._VehicleBusSleeping:
        pass
    else:
        raise AssertionError("diagnostics or Panda TX echoes kept a sleeping vehicle awake")
check("only vehicle traffic keeps automatic arming awake", True)


for installed_before_sleep in (False, True):
    clock = _Clock()
    raw = SimpleNamespace(can_recv=lambda: [], health=lambda: {"ignition_line": False, "ignition_can": False})
    def sleep_during_install(*_args, **_kwargs):
        clock.sleep(4.0)
        if not installed_before_sleep:
            raise ui_bringup.BootloaderNotReachedError("EPS powered down")
        return {"verdict": "request_signer_live_probe_pass"}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "meta").write_text(json.dumps({"target": {"name": "camry-8965F3307000"}}))
        marker = root / "native.json"
        marker.write_text(json.dumps(native_marker))
        output = io.StringIO()
        with (mock.patch.object(ui_bringup, "time", clock),
              mock.patch.object(ui_bringup, "_emit_stream", output),
              mock.patch.object(ui_bringup, "install", side_effect=sleep_during_install),
              mock.patch.object(ui_bringup, "control_domain_state") as peer_checks):
            result = ui_bringup.run(root / "payload", root / "meta", root / "run", native_catch=marker, panda=raw)
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        check(f"bus sleep is normal with installed={installed_before_sleep}",
              result["verdict"] == "vehicle_bus_asleep" and rows[-1]["stage"] == "sleeping"
              and all(not row["error"] and not row["done"] for row in rows) and not peer_checks.called)


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    marker = root / "native.json"
    marker.write_text(json.dumps(native_marker))
    with (mock.patch.object(ui_bringup, "_emit_stream", io.StringIO()),
          mock.patch.object(ui_bringup, "install", side_effect=ValueError("payload mismatch"))):
        try:
            ui_bringup.run(root / "payload", root / "meta", root / "run", native_catch=marker, panda=object())
        except ValueError as exc:
            check("automatic sleep handling does not hide installation faults", str(exc) == "payload mismatch")
        else:
            raise AssertionError("installation fault was hidden")


print("PASS TSS3 startup bringup")
