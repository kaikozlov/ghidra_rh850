#!/usr/bin/env python3
"""Verify the exact-F33 GTS+ passive witness is receive-only and bounded."""

from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.targets.camry.live import camry_f33_eps_gts_passive_capture as capture
from tools.targets.camry.analysis import analyze_camry_f33_eps_gts_passive_capture as analyzer


passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


class TextSink(io.StringIO):
    def flush(self) -> None:
        return None


class FakePanda:
    def __init__(self, batches=None, health=None):
        self.batches = list(batches or [])
        self.health_value = health or {
            "safety_mode": capture.NOOUTPUT_SAFETY_MODE,
            "safety_param": 0,
            "controls_allowed": False,
            "heartbeat_lost": False,
            "voltage": 13_100,
            "rx_buffer_overflow": 0,
            "tx_buffer_overflow": 0,
        }
        self.safety_calls = []
        self.heartbeats = []
        self.clear_calls = []
        self.data_speed_calls = []
        self.non_iso_calls = []
        self.can_rx_overflow_buffer = b""

    def set_safety_mode(self, mode, param=0):
        self.safety_calls.append((int(mode), int(param)))

    def health(self):
        return dict(self.health_value)

    def can_recv(self):
        return self.batches.pop(0) if self.batches else []

    def can_clear(self, selector):
        self.clear_calls.append(int(selector))

    def set_can_data_speed_kbps(self, bus, speed):
        self.data_speed_calls.append((int(bus), int(speed)))

    def set_canfd_non_iso(self, bus, non_iso):
        self.non_iso_calls.append((int(bus), bool(non_iso)))

    def can_health(self, _bus):
        return {
            "bus_off": 0,
            "bus_off_cnt": 0,
            "total_error_cnt": 0,
            "total_rx_lost_cnt": 0,
            "total_tx_lost_cnt": 0,
            "total_tx_cnt": 0,
            "total_rx_cnt": 0,
            "can_core_reset_count": 0,
            "can_speed": capture.EXPECTED_CAN_SPEED_KBPS,
            "can_data_speed": capture.EXPECTED_CAN_DATA_SPEED_KBPS,
            "canfd_non_iso": 0,
        }

    def send_heartbeat(self, engaged=False):
        self.heartbeats.append(bool(engaged))

    def can_send(self, *_args, **_kwargs):
        raise AssertionError("passive witness must never transmit")


print("== immutable dry-run contract ==")
plan = capture.build_plan(900, None)
check("schema pins exact passive-capture contract", plan["schema"] == "camry-f33-eps-gts-passive-capture-v1")
check("plan declares zero CAN transmissions and no UDS requests",
      plan["can_transmit_calls"] == 0 and plan["flow_control_frames"] == 0 and plan["uds_requests"] == [])
check("plan requires GTS on a separate VCI",
      "separate VIM/J2534" in plan["active_client"])
check("Panda is forced to NOOUTPUT on normal routing",
      plan["panda"]["safety_mode"] == {"name": "NOOUTPUT", "numeric": 19}
      and plan["panda"]["exit_safety_mode"] == {"name": "SILENT", "numeric": 0}
      and plan["panda"]["routing"] == "normal harness CAN mode; no OBD mux selection")
check("capture pins exact 500/2000 kbps ISO CAN-FD controller format",
      plan["panda"]["can_format"]
      == {"nominal_kbps": 500, "data_kbps": 2000, "can_fd_non_iso": False})
check("all three physical Panda buses are retained", plan["panda"]["physical_buses_recorded"] == [0, 1, 2])
capture_tree = ast.parse(Path(capture.__file__).read_text())
can_transmit_calls = [
    node for node in ast.walk(capture_tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute)
    and node.func.attr in {"can_send", "can_send_many"}
]
check("capture implementation contains no Panda CAN transmit call", not can_transmit_calls)


print("\n== passive batch retention and bounded UDS hints ==")
frames = [
    (0x7A1, bytes.fromhex("023e000000000000"), 0),
    (0x7A9, bytes.fromhex("027e000000000000"), 0),
    (0x750, bytes.fromhex("5f02100200000000"), 1),
    (0x758, bytes.fromhex("5f037f1078000000"), 1),
    (0x7A9, bytes.fromhex("100a62f181022121"), 0),
    (0x7A1, bytes.fromhex("3000000000000000"), 0),
    (0x08A, bytes(range(32)), 0),
    (0x123, b"receipt", 128),
]
fake = FakePanda([frames])
can_stream = io.BytesIO()
diagnostic_stream = TextSink()
capture.write_canbin_header(can_stream)
stats = capture._new_stats()
retained = capture.capture_batch(fake, can_stream, diagnostic_stream, stats, now_ns=123456)
events = [json.loads(line) for line in diagnostic_stream.getvalue().splitlines()]
check("physical frames retained and synthetic TX receipt excluded", retained == 7 and stats["nonphysical_rows"] == 1)
check("binary capture uses its own format and includes non-diagnostic CAN",
      can_stream.getvalue().startswith(capture.CANBIN_MAGIC) and stats["frames_total"] == 7
      and stats["frames_by_address"]["0x8A"] == 1)
check("normal primary request/response receive UDS hints",
      events[0]["route"] == "eps-primary-request" and events[0]["uds_service"] == "0x3E"
      and events[1]["route"] == "eps-primary-response" and events[1]["uds_service"] == "0x7E")
check("gateway address extension 5F is preserved",
      events[2]["address_extension"] == "0x5F" and events[2]["uds_service"] == "0x10")
check("negative response retains requested SID, NRC, and extension",
      events[3]["negative_for_service"] == "0x10"
      and events[3]["negative_response_code"] == "0x78"
      and events[3]["address_extension"] == "0x5F")
check("first-frame and flow-control are observed without participation",
      events[4]["transport"] == "isotp-first" and events[4]["uds_service"] == "0x62"
      and events[5]["transport"] == "isotp-flow-control")


print("\n== NOOUTPUT setup and finite loop ==")
setup_fake = FakePanda()
setup = capture.configure_passive_panda(setup_fake, sleep_fn=lambda _seconds: None)
check("passive setup sets NOOUTPUT and re-enables a disengaged heartbeat",
      setup_fake.safety_calls == [(19, 0)] and setup_fake.heartbeats == [False] and setup["verified"])
silent_fake = FakePanda(health={
    "safety_mode": capture.SILENT_SAFETY_MODE,
    "controls_allowed": False,
    "heartbeat_lost": False,
})
silent_setup = capture.configure_silent_panda(silent_fake, sleep_fn=lambda _seconds: None)
check("exit setup explicitly selects and verifies SILENT",
      silent_fake.safety_calls == [(0, 0)] and silent_fake.heartbeats == [False]
      and silent_setup["verified"])
format_fake = FakePanda()
format_setup = capture.configure_capture_can(format_fake)
check("capture setup replaces persistent data-rate/non-ISO state on every bus",
      format_setup["verified"]
      and format_fake.data_speed_calls == [(0, 2000), (1, 2000), (2, 2000)]
      and format_fake.non_iso_calls == [(0, False), (1, False), (2, False)])
bad_setup = capture.configure_passive_panda(
    FakePanda(health={"safety_mode": 3, "controls_allowed": False, "heartbeat_lost": False}),
    sleep_fn=lambda _seconds: None,
)
check("mismatched safety health fails closed", not bad_setup["verified"] and bad_setup["issues"])

loop_fake = FakePanda([
    [(0x7B0, bytes.fromhex("0322102f00000000"), 0)],
])
ticks = iter((0, 0, 1_000_000_000, 1_000_000_000, 1_000_000_000))
loop_can = io.BytesIO()
loop_diag = TextSink()
capture.write_canbin_header(loop_can)
loop_result = capture.run_capture_loop(
    loop_fake,
    loop_can,
    loop_diag,
    duration_seconds=1,
    monotonic_ns_fn=lambda: next(ticks),
    sleep_fn=lambda _seconds: None,
)
check("finite loop clears the complete board RX queue at the evidence boundary",
      loop_result["receive_boundary"]
      == {"method": "panda.can_clear", "queue": "global-rx", "selector": 0xFFFF}
      and loop_fake.clear_calls == [0xFFFF])
check("finite loop records one Brake request without a transmit call",
      loop_result["stats"]["known_route_frames"] == {"brake-request": 1}
      and loop_result["stats"]["uds_service_hints"] == {"0x22": 1})
check("finite loop verifies no board/controller loss while observing absence",
      loop_result["loss_monitor"]["valid_for_absence_claims"]
      and loop_result["loss_monitor"]["issues"] == [])
check("heartbeat is active but never reports engagement",
      loop_fake.heartbeats and not any(loop_fake.heartbeats))

interrupt_fake = FakePanda([
    [(0x7A9, bytes.fromhex("027e000000000000"), 0)],
])
interrupt_ticks = iter((0, 0, 100_000_000, 100_000_000))
sleep_calls = 0


def interrupting_sleep(_seconds):
    global sleep_calls
    sleep_calls += 1
    if sleep_calls == 2:
        raise capture.CaptureInterrupted("SIGINT")


interrupt_can = io.BytesIO()
interrupt_diag = TextSink()
capture.write_canbin_header(interrupt_can)
interrupt_result = capture.run_capture_loop(
    interrupt_fake,
    interrupt_can,
    interrupt_diag,
    duration_seconds=1,
    monotonic_ns_fn=lambda: next(interrupt_ticks),
    sleep_fn=interrupting_sleep,
)
check("interrupt preserves already captured diagnostic evidence",
      interrupt_result["interrupted"] == "CaptureInterrupted: SIGINT"
      and interrupt_result["stats"]["known_route_frames"] == {"eps-primary-response": 1})


class EndingInterruptPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.can_health_calls = 0

    def can_health(self, bus):
        self.can_health_calls += 1
        if self.can_health_calls == 4:
            raise capture.CaptureInterrupted("SIGTERM")
        return super().can_health(bus)


ending_interrupt_ticks = iter((0, 0, 1_000_000_000, 1_000_000_000))
ending_interrupt_result = capture.run_capture_loop(
    EndingInterruptPanda(),
    io.BytesIO(),
    TextSink(),
    duration_seconds=1,
    monotonic_ns_fn=lambda: next(ending_interrupt_ticks),
    sleep_fn=lambda _seconds: None,
)
check("interrupt during ending health remains interrupted and invalidates absence",
      ending_interrupt_result["interrupted"] == "CaptureInterrupted: SIGTERM"
      and not ending_interrupt_result["loss_monitor"]["valid_for_absence_claims"])


print("\n== ownership guard and routed dry run ==")
check("pandad module process title is recognized",
      bool(capture.PANDA_OWNER_COMMAND_PATTERN.search("python -m openpilot.selfdrive.pandad.pandad")))
check("unrelated text is not recognized as Panda owner",
      not capture.PANDA_OWNER_COMMAND_PATTERN.search("editor notes/pandad-analysis.md"))
completed = subprocess.run(
    [
        str(ROOT / "tools/toyota"), "target", "run", "camry",
        "capture/f33-eps-gts-passive-capture", "--", "--duration-seconds", "30",
    ],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=False,
)
try:
    routed_plan = json.loads(completed.stdout)
except json.JSONDecodeError:
    routed_plan = {}
check("target runner exposes the capture capability", completed.returncode == 0 and routed_plan.get("duration_seconds") == 30,
      completed.stderr.strip())
check("dry run does not create output or open hardware",
      routed_plan.get("mode") == "dry-run" and routed_plan.get("output_dir", "").endswith("<UTC timestamp>"))


print("\n== offline OEM-path verdict ==")


def write_timed_fixture(directory: Path, timed_batches):
    stats = capture._new_stats()
    with (directory / "can.bin").open("wb") as can_file, (directory / "diagnostic.ndjson").open("w") as diag_file:
        capture.write_canbin_header(can_file)
        for timestamp, fixture_frames in timed_batches:
            fixture_panda = FakePanda([fixture_frames])
            capture.capture_batch(fixture_panda, can_file, diag_file, stats, now_ns=timestamp)
    summary = {
        "schema": capture.SCHEMA,
        "status": "capture-complete",
        "final_silent": {"verified": True},
        "capture": {
            "stats": capture._jsonable_stats(stats),
            "loss_monitor": {"valid_for_absence_claims": True, "issues": []},
        },
    }
    (directory / "summary.json").write_text(json.dumps(summary) + "\n")


def write_fixture(directory: Path, fixture_frames):
    write_timed_fixture(directory, [(5_000_000, fixture_frames)])


with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_fixture(fixture_dir, [
        (0x750, bytes.fromhex("5f023e0000000000"), 1),
        (0x758, bytes.fromhex("5f027e0000000000"), 1),
        (0x7A1, bytes.fromhex("0210020000000000"), 0),
    ])
    silent_verdict = analyzer.analyze(fixture_dir)
    check("analyzer treats node-5F traffic as incidental while classifying target-side silence",
          silent_verdict["outcome"] == "primary-eps-request-observed-no-response"
          and silent_verdict["recovery_discriminators"]["target_10_02_requests"] == 1
          and silent_verdict["recovery_discriminators"][
              "primary_requests_with_prior_incidental_node_5f_frames"
          ] == 1
          and silent_verdict["recovery_discriminators"]["primary_eps_response_frames"] == 0)
    check("analyzer hashes and reconciles the complete capture",
          silent_verdict["integrity"]["valid"] and all(silent_verdict["source_hashes"].values()))

with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_fixture(fixture_dir, [
        (0x750, bytes.fromhex("5f023e0000000000"), 1),
        (0x758, bytes.fromhex("5f027e0000000000"), 1),
        (0x7A1, bytes.fromhex("0210020000000000"), 0),
        (0x7A9, bytes.fromhex("0250020000000000"), 0),
    ])
    positive_verdict = analyzer.analyze(fixture_dir)
    check("analyzer promotes exact 50 02 only to programming-session liveness",
          positive_verdict["outcome"] == "eps-programming-session-positive"
          and positive_verdict["recovery_discriminators"]["target_50_02_positives"] == 1
          and positive_verdict["recovery_discriminators"]["ordered_target_10_02_50_02_pairs"] == 1
          and positive_verdict["ordered_programming_pairs"][0]["request_row"] == 2
          and positive_verdict["ordered_programming_pairs"][0]["response_row"] == 3
          and positive_verdict["repair_proved"] is False)

with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_fixture(fixture_dir, [
        (0x7A9, bytes.fromhex("0250020000000000"), 0),
        (0x7A1, bytes.fromhex("0210020000000000"), 0),
    ])
    reversed_verdict = analyzer.analyze(fixture_dir)
    check("analyzer does not turn an unpaired or reversed 50 02 into a session transition",
          reversed_verdict["outcome"] == "eps-origin-response-observed"
          and reversed_verdict["recovery_discriminators"]["target_50_02_positives"] == 1
          and reversed_verdict["recovery_discriminators"]["ordered_target_10_02_50_02_pairs"] == 0)

with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_fixture(fixture_dir, [
        (0x7A1, bytes.fromhex("0210020000000000"), 0),
        (0x750, bytes.fromhex("5f023e0000000000"), 1),
        (0x758, bytes.fromhex("5f027e0000000000"), 1),
    ])
    late_gateway_verdict = analyzer.analyze(fixture_dir)
    check("later gateway traffic is not mislabeled as prior preparation",
          late_gateway_verdict["outcome"]
          == "primary-eps-request-observed-no-response"
          and late_gateway_verdict["recovery_discriminators"][
              "primary_requests_with_prior_incidental_node_5f_frames"
          ] == 0)

with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_fixture(fixture_dir, [
        (0x7A1, bytes.fromhex("0210020000000000"), 1),
        (0x7A9, bytes.fromhex("0250020000000000"), 1),
    ])
    stale_bus_verdict = analyzer.analyze(fixture_dir)
    check("stale bus-1 EPS-shaped traffic cannot become a current-route positive",
          stale_bus_verdict["outcome"] == "diagnostic-range-traffic-seen-no-current-bus-eps-route"
          and stale_bus_verdict["recovery_discriminators"]["target_10_02_requests"] == 0
          and stale_bus_verdict["recovery_discriminators"]["target_50_02_positives"] == 0)

with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_timed_fixture(fixture_dir, [
        (1_000_000_000, [(0x7A1, bytes.fromhex("0210020000000000"), 0)]),
        (5_000_000_001, [(0x7A9, bytes.fromhex("0250020000000000"), 0)]),
    ])
    delayed_verdict = analyzer.analyze(fixture_dir)
    check("a response beyond the three-second evidence ceiling remains unpaired activity",
          delayed_verdict["outcome"] == "eps-origin-response-observed"
          and delayed_verdict["recovery_discriminators"]["ordered_target_10_02_50_02_pairs"] == 0)

with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_fixture(fixture_dir, [(0x7A1, bytes.fromhex("0210020000000000"), 0)])
    index_path = fixture_dir / "diagnostic.ndjson"
    indexed = json.loads(index_path.read_text().splitlines()[0])
    indexed["pdu_prefix_hex"] = "5002"
    index_path.write_text(json.dumps(indexed) + "\n")
    tampered_verdict = analyzer.analyze(fixture_dir)
    check("sidecar-only framing cannot create a recovery verdict",
          tampered_verdict["outcome"] == "capture-integrity-failed"
          and not tampered_verdict["integrity"]["valid"])

with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_fixture(fixture_dir, [(0x7A1, bytes.fromhex("0210020000000000"), 0)])
    summary_path = fixture_dir / "summary.json"
    summary = json.loads(summary_path.read_text())
    summary["capture"]["loss_monitor"] = {
        "valid_for_absence_claims": False,
        "issues": ["CAN bus 0 total_rx_lost_cnt increased by 1"],
    }
    summary_path.write_text(json.dumps(summary) + "\n")
    loss_verdict = analyzer.analyze(fixture_dir)
    check("hardware receive loss invalidates a silence classification",
          loss_verdict["outcome"] == "capture-integrity-failed"
          and not loss_verdict["integrity"]["valid"])

with tempfile.TemporaryDirectory() as temp_name:
    fixture_dir = Path(temp_name)
    write_fixture(fixture_dir, [(0x7A1, bytes.fromhex("023e000000000000"), 0)])
    summary_path = fixture_dir / "summary.json"
    summary = json.loads(summary_path.read_text())
    summary["status"] = "interrupted"
    summary_path.write_text(json.dumps(summary) + "\n")
    interrupted_verdict = analyzer.analyze(fixture_dir)
    interrupted_cli = subprocess.run(
        [sys.executable, str(Path(analyzer.__file__)), str(fixture_dir)],
        text=True,
        capture_output=True,
        check=False,
    )
    check("interrupted capture cannot return a successful absence verdict",
          interrupted_verdict["outcome"] == "capture-incomplete-no-absence-conclusion"
          and not interrupted_verdict["coverage"]["complete"]
          and interrupted_cli.returncode == 3)


print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
