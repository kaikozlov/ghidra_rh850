#!/usr/bin/env python3
"""Verify the dump-resolved universal TSS3 RAM-resident request signer."""
from __future__ import annotations

import copy
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from exploit.ephemeral_runtime import build_tss3_request_signer as build
from exploit.ephemeral_runtime import tss3_request_signer as host
from exploit.ephemeral_runtime import tss3_request_signer_compact as compact_host
from exploit.ram_runtime.target_profiles import registered_specs, spec_from_codeflash
from exploit.ram_runtime.tss3_request_signer_contract import (
    ContractError,
    probe_request_signer_contract,
    resolve_request_signer_contract,
)
from tools import REPO_ROOT

ROOT = REPO_ROOT

CAMRY_TARGET = "camry-8965F3307000"
SPECS = registered_specs()
BUILD_TEMP = tempfile.TemporaryDirectory(prefix="verify-tss3-request-signer-")
BUILD_ROOT = Path(BUILD_TEMP.name)
OUT = BUILD_ROOT / "default"
COMPACT_OUT = BUILD_ROOT / "compact"

meta = build.build_request_signer(target=CAMRY_TARGET, output_dir=OUT)
compact_meta = build.build_request_signer(target=CAMRY_TARGET, codec="compact", output_dir=COMPACT_OUT)
meta_path = OUT / "camry_8965F3307000_request_signer.json"


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


synthetic_image = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
old_selector = SPECS[CAMRY_TARGET]["runtime_software_id"].encode("ascii")
new_selector = b"8965F3307999"
if synthetic_image.count(old_selector) != 1:
    raise AssertionError("Camry selector identity is not unique")
selector_offset = synthetic_image.find(old_selector)
synthetic_image[selector_offset:selector_offset + len(old_selector)] = new_selector
synthetic_path = BUILD_ROOT / "synthetic-new-profile-CodeFlash.bin"
synthetic_path.write_bytes(synthetic_image)
synthetic_spec = spec_from_codeflash(synthetic_path, known_specs=SPECS)
current_profiles = build.runtime_profiles(SPECS)
synthetic_compatibility = build.profile_status(synthetic_spec, current_profiles)
synthetic_profiles = build.runtime_profiles({
    **SPECS,
    synthetic_spec["name"]: synthetic_spec,
})


def run_core_simulator() -> None:
    import subprocess

    with tempfile.TemporaryDirectory(prefix="request-signer-core-sim-") as td:
        subprocess.run([
            str(ROOT / "tools/rh850"), "test", "payload",
            "tests/fixtures/rh850/tss3_request_signer_core_sim.S",
            "tests/fixtures/rh850/tss3_request_signer_core_sim.c",
            "--linker-script", "tests/fixtures/rh850/tss3_request_signer_core_sim.ld",
            "--output-dir", td,
            "--memory-region", "0xFEBF0000,0x10000",
            "--stop", "rh850_sim_stop",
            "--assert", "*(unsigned int *)&oracle_sim_result == 0x8a0c0de",
            "--assert", "*(unsigned int *)&oracle_sim_failure == 0",
            "--assert", "*(unsigned int *)&oracle_sim_passes == 36",
        ], cwd=ROOT, check=True, text=True, timeout=150)


run_core_simulator()
print("PASS production pure-core macros execute and satisfy result checks")


application = bytes(range(28))
four_frames = host.build_request(application, 0xA7)
check("host default codec transports all application bytes in four exact frames",
      four_frames == (
          bytes.fromhex("8700010203040506"),
          bytes.fromhex("9a0708090a0b0c0d"),
          bytes.fromhex("a70e0f1011121314"),
          bytes.fromhex("ba15161718191a1b"),
      ) and
      b"".join(frame[1:] for frame in four_frames) == application and
      host.build_request_frames(application, 0xA7) == four_frames)

compact_app = bytearray(host.SAFE_APPLICATION)
compact_app[18], compact_app[19], compact_app[26] = 0x34, 0x12, 0x21
compact_frame = compact_host.build_compact_frame(bytes(compact_app), 0xA1)
check("optional compact module retains its bounded reconstruction contract",
      compact_frame == bytes.fromhex("c0000000341200a1") and
      compact_host.compact_reconstruction(compact_frame)[2:] == bytes(compact_app) and
      compact_host.build_compact_frame(host.SAFE_APPLICATION, 0x40) ==
          bytes.fromhex("c000000000000040"))
for rejected_application, rejected_seq in (
    (bytes(range(28)), 0xA7),
    (host.SAFE_APPLICATION, 0x41),
    (bytes(bytearray(compact_app[:24]) + bytearray([100]) + bytes(compact_app[25:])), 0xA1),
):
    try:
        compact_host.build_compact_frame(rejected_application, rejected_seq)
    except ValueError:
        pass
    else:
        raise AssertionError("optional compact codec accepted a nonrepresentable application")
print("PASS optional compact codec rejects every nonrepresentable application")

check("registered dump is already covered by the universal build",
      meta["compatibility"]["status"] == "covered-by-current-build")
check("missing selector extends the universal profile table without compilation",
      synthetic_compatibility["status"] == "compatible-profile-missing" and
      len(synthetic_profiles) == len(current_profiles) + 1 and
      any(
          row["software_id"] == new_selector.decode("ascii")
          for row in synthetic_profiles
      ))

conflicting_spec = copy.deepcopy(SPECS[CAMRY_TARGET])
conflicting_spec["runtime_config"]["app_context"] += 4
try:
    build.runtime_profiles({**SPECS, "conflict": conflicting_spec})
except RuntimeError:
    pass
else:
    raise AssertionError("universal profile table accepted an ambiguous selector")
print("PASS universal profile table rejects an ambiguous selector")
for target, spec in SPECS.items():
    probe = probe_request_signer_contract(spec["image"].read_bytes())
    check(
        f"{target} exposes every dynamically required signer component",
        probe["compatible"]
        and probe["contract"]["codeflash_sha256"] == spec["sha256"]
        and all(
            row["status"] == "resolved"
            for row in probe["components"].values()
        ),
    )


damaged_image = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
camry_contract = SPECS[CAMRY_TARGET]["contract"]
freshness_address = camry_contract["signer_abi"]["freshness_encode"]
damaged_image[freshness_address:freshness_address + 16] = b"\0" * 16
damaged_probe = probe_request_signer_contract(bytes(damaged_image))
check(
    "capability probe preserves independent results after signer ABI damage",
    not damaged_probe["compatible"]
    and damaged_probe["components"]["identity"]["status"] == "resolved"
    and damaged_probe["components"]["request"]["status"] == "resolved"
    and damaged_probe["components"]["signer_abi"]["status"] == "missing-or-ambiguous"
    and damaged_probe["components"]["memory"]["status"] == "blocked",
)
try:
    resolve_request_signer_contract(bytes(damaged_image))
except ContractError:
    pass
else:
    raise AssertionError("dump resolver accepted firmware without the signer freshness primitive")
print("PASS dump resolver rejects firmware with an unresolved signer ABI")

check("generated transports satisfy the host metadata contract",
      host.meta_transport(meta)["codec"] == "four-frame" and
      host.meta_transport(compact_meta)["codec"] == "compact")
try:
    host.meta_transport({
        "request": {"can_id": "0x1FDC0002", "bus": 0, "carrier": "raw-extended"},
        "response": {"can_id": "0x1FE00002", "bus": 0},
    })
except host.RequestSignerError:
    pass
else:
    raise AssertionError("host accepted the retired second carrier")
print("PASS host rejects the retired extended-XCP carrier")
resp = host.parse_response(bytes.fromhex("c90700f8d64e2a5e"), expected_seq=0x07)
check("host response decoder matches resident layout",
      resp.seq == 0x07 and resp.status == 0 and resp.trailer == bytes.fromhex("d64e2a5e"))
summary = host.latency_summary([4.0, 1.0, 3.0, 2.0])
check("parked benchmark reports deterministic distribution statistics",
      {name: round(value, 3) for name, value in summary.items()} == {
          "mean_ms": 2.5, "median_ms": 2.5, "p95_ms": 3.85, "p99_ms": 3.97, "max_ms": 4.0,
      })


def _recorded_send(index: int, seq: int, *, lateness_ms: float, started_ns: int) -> dict:
    application = host.safe_application(seq)
    frames = host.build_request_frames(application, seq, host.REQUEST_CARRIER)
    return {
        "index": index,
        "seq": seq,
        "codec": host.FOUR_FRAME_CODEC,
        "request_sequence": application[26],
        "scheduled_start_lateness_ms": round(max(0.0, lateness_ms), 3),
        "started_ns": started_ns,
        "submit_ms": 0.15,
        "frames_hex": [frame.hex() for frame in frames],
    }


def _recorded_response(seq: int, status_value: int, started_ns: int, *, rtt_ms: float, counter: int) -> dict:
    frame = bytes((host.RESPONSE_MAGIC, seq, status_value, seq ^ 0xFF)) + bytes(
        (0x10 | (counter & 0x0F), seq, 0xA5, 0x5A))
    parsed = host.parse_response(frame)
    return {
        "monotonic_ns": started_ns + round(rtt_ms * 1e6),
        "frame_hex": frame.hex(),
        "seq": parsed.seq,
        "status": parsed.status,
        "trailer": parsed.trailer.hex(),
        "fv4": parsed.trailer[0] >> 4,
    }


def _recorded_run(count: int, period_ms: float, *, lateness_ms: list[float], rtt_ms: list[float],
                  statuses: list[int] | None = None, sent: int | None = None, answered: int | None = None,
                  rx_errors: tuple[str, ...] = (), max_outstanding: int = 1,
                  sequence_window_exhausted: bool = False,
                  outstanding_after_drain: int | None = None) -> dict:
    """Rebuild a pipelined transcript in the exact shape benchmark_pipelined records."""
    sent = count if sent is None else sent
    answered = sent if answered is None else answered
    sends: list[dict] = []
    responses: dict[int, dict] = {}
    started_ns = 1_000_000_000
    for index in range(sent):
        seq = index + 1
        sends.append(_recorded_send(index, seq, lateness_ms=lateness_ms[index], started_ns=started_ns))
        if index < answered:
            status_value = statuses[index] if statuses is not None else 0
            responses[index] = _recorded_response(
                seq, status_value, started_ns, rtt_ms=rtt_ms[index], counter=index + 1)
        started_ns += round(period_ms * 1e6)
    return host._reduce_pipelined_benchmark(
        count, period_ms, sends, responses,
        unsolicited_count=0,
        rx_errors=list(rx_errors),
        outstanding_after_drain=sent - answered if outstanding_after_drain is None else outstanding_after_drain,
        max_outstanding=max_outstanding,
        sequence_window_exhausted=sequence_window_exhausted,
    )


boundary_run = _recorded_run(
    4, 10.0,
    lateness_ms=[0.0, 1.25, 6.0, 9.999],
    rtt_ms=[2.0, 45.0, 12.5, 90.0],
    max_outstanding=host.RUNTIME_MAX_PENDING_GENERATIONS,
)
check("pipelined completion verdict accepts a recorded run at every inclusive boundary",
      boundary_run["complete_target_rate_run"] is True and
      boundary_run["count_sent"] == boundary_run["success_count"] == boundary_run["responses_received"] == 4 and
      boundary_run["success_rate"] == 1.0 and boundary_run["outstanding_after_drain"] == 0 and
      boundary_run["sequence_window_exhausted"] is False and
      boundary_run["scheduled_start_lateness_ms"]["max_ms"] == 9.999 and
      boundary_run["request_start_to_response_ms"]["max_ms"] == 90.0 and
      boundary_run["rows"][3]["request_start_to_response_ms"] == 90.0 and
      boundary_run["response_interarrival_ms"]["max_ms"] == 65.0 and
      boundary_run["effective_success_response_rate_hz"] == 25.424)

clean_lateness = [0.0, 0.5, 1.0, 1.5]
clean_rtt = [2.0, 3.0, 4.0, 5.0]

missing_reply = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=clean_rtt, answered=3)
check("pipelined completion verdict rejects a run whose last reply never arrives",
      missing_reply["complete_target_rate_run"] is False and
      missing_reply["success_count"] == 3 and missing_reply["responses_received"] == 3 and
      missing_reply["outstanding_after_drain"] == 1 and missing_reply["success_rate"] == 0.75 and
      missing_reply["rows"][3]["error"] == "missing_response" and
      "status" not in missing_reply["rows"][3])

error_status = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=clean_rtt,
                             statuses=[0, 0, 0, 0x21])
check("pipelined completion verdict rejects a delivered nonzero signer status",
      error_status["complete_target_rate_run"] is False and
      error_status["success_count"] == 3 and error_status["responses_received"] == 4 and
      error_status["outstanding_after_drain"] == 0 and
      error_status["rows"][3]["status"] == 0x21 and "error" not in error_status["rows"][3] and
      error_status["rows"][3]["request_start_to_response_ms"] == 5.0)

rx_failure = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=clean_rtt,
                           rx_errors=("OSError: can recv failed",))
check("pipelined completion verdict rejects a run whose receiver thread died",
      rx_failure["complete_target_rate_run"] is False and
      rx_failure["success_count"] == 4 and
      rx_failure["rx_errors"] == ["OSError: can recv failed"])

overloaded = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=clean_rtt,
                           max_outstanding=host.RUNTIME_MAX_PENDING_GENERATIONS + 1)
check("pipelined completion verdict rejects backlog past the pending-generation limit",
      overloaded["complete_target_rate_run"] is False and
      overloaded["success_count"] == 4 and
      overloaded["max_outstanding"] == host.RUNTIME_MAX_PENDING_GENERATIONS + 1)

late_publication = _recorded_run(4, 10.0, lateness_ms=[0.0, 0.5, 1.0, 10.0], rtt_ms=clean_rtt)
check("pipelined completion verdict rejects a publication that slipped a full period",
      late_publication["complete_target_rate_run"] is False and
      late_publication["rows"][3]["scheduled_start_lateness_ms"] == 10.0)

slow_reply = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=[2.0, 3.0, 4.0, 90.001])
check("pipelined completion verdict rejects a reply past the publication deadline",
      slow_reply["complete_target_rate_run"] is False and
      slow_reply["rows"][3]["request_start_to_response_ms"] == 90.001 and
      slow_reply["request_start_to_response_ms"]["max_ms"] == 90.001)

wedged = _recorded_run(300, 10.0, lateness_ms=[0.5] * host.SEQUENCE_MAX, rtt_ms=[3.0] * host.SEQUENCE_MAX,
                       sent=host.SEQUENCE_MAX, answered=3, sequence_window_exhausted=True,
                       max_outstanding=host.SEQUENCE_MAX)
check("pipelined completion verdict rejects a wedged signer that exhausted the sequence window",
      wedged["complete_target_rate_run"] is False and
      wedged["count_sent"] == host.SEQUENCE_MAX and wedged["count_requested"] == 300 and
      wedged["sequence_window_exhausted"] is True and
      wedged["outstanding_after_drain"] == host.SEQUENCE_MAX - 3 and
      wedged["responses_received"] == 3 and wedged["success_rate"] == 3 / 300 and
      len(wedged["rows"]) == host.SEQUENCE_MAX and
      [row.get("error") for row in wedged["rows"][3:]] == ["missing_response"] * (host.SEQUENCE_MAX - 3))




class _FakeProbePanda:
    def __init__(self):
        self.request_count = 0
        self.rx: list[tuple[int, bytes, int]] = []

    def set_safety_mode(self, *_args):
        pass

    def can_send_many(self, frames):
        self.request_count += 1
        data = [bytes(frame[1]) for frame in frames]
        seq = (data[0][0] & 0x0F) | ((data[1][0] & 0x0F) << 4)
        self.rx.append((0x7A9, bytes((0xC9, seq, 0x00, seq ^ 0xFF, 0x10 | (self.request_count & 0x0F), seq, 0xA5, 0x5A)), 0))

    def can_recv(self):
        rows, self.rx = self.rx, []
        return rows

    def close(self):
        pass


fake_probe_panda = _FakeProbePanda()
with (mock.patch.object(host, "load_security_secret", return_value=(b"\x00" * 16, "test")),
      mock.patch.object(host, "execute_ram_payload", return_value={"direct_bootloader": True}) as execute,
      mock.patch.object(host, "wait_for_f181", return_value={"ok": True}) as wait_for_application,
      mock.patch.object(host, "set_alloutput_mode")):
    direct = host.install(
        OUT / meta["authenticated_payload"]["path"], meta_path,
        direct_boot=True, panda=fake_probe_panda,
    )
check("post-activation install success is proved by the signer response, not a second F181 check",
      direct["entry_condition"] == "exact_bootloader_f181" and
      direct["verdict"] == "request_signer_live_probe_pass" and
      fake_probe_panda.request_count == 1 and
      execute.call_args.kwargs["allow_direct_boot"] is True and
      execute.call_args.kwargs["programming_already_requested"] is True and
      wait_for_application.call_count == 1 and
      wait_for_application.call_args.kwargs["expected_f181_hex"] == meta["target"]["application_f181_hex"])

fake_self_test_panda = _FakeProbePanda()
with (mock.patch.dict("sys.modules", {"panda": SimpleNamespace(Panda=lambda *_a, **_k: fake_self_test_panda)}),
      mock.patch.object(host, "set_alloutput_mode")):
    signer_self_test = host.self_test(meta_path, panda=fake_self_test_panda)
check("fresh signer self-test needs no post-activation diagnostic transport",
      signer_self_test["passed"] is True and signer_self_test["response"]["status"] == 0 and
      fake_self_test_panda.request_count == 1)

BUILD_TEMP.cleanup()
print("PASS TSS3 request signer behavior")
