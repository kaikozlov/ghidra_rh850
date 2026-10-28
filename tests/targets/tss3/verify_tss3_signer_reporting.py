#!/usr/bin/env python3
"""Verify signer benchmark report reduction without firmware or a toolchain."""
from __future__ import annotations

import copy
import statistics

from tsk.ram_runtime import tss3_request_signer as host


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


summary = host.latency_summary([4.0, 1.0, 3.0, 2.0])
check("parked benchmark reports deterministic distribution statistics",
      {name: round(value, 3) for name, value in summary.items()} == {
          "mean_ms": 2.5, "median_ms": 2.5, "p95_ms": 3.85, "p99_ms": 3.97, "max_ms": 4.0,
      })


def _recorded_send(index: int, seq: int, *, lateness_ms: float, started_ns: int) -> dict:
    application = host.safe_application(seq)
    frames = host.build_request(application, seq)
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

for samples in ([2.0], [4.0, 1.0, 3.0], [0.1, 0.2], [4.0, 4.0, 4.0, 4.0]):
    original = list(samples)
    distribution = host.latency_summary(samples)
    check(
        f"summary preserves median arithmetic and input order for {samples}",
        distribution["median_ms"] == statistics.median(samples) and samples == original,
    )
try:
    host.latency_summary([])
except ValueError as exc:
    check("empty summaries keep their explicit error", str(exc) == "latency summary requires at least one sample")
else:
    raise AssertionError("empty summary accepted")

empty_run = _recorded_run(4, 10.0, lateness_ms=[], rtt_ms=[], sent=0)
check(
    "empty transcript has no distributions or completion verdict",
    empty_run["rows"] == [] and empty_run["success_count"] == 0
    and empty_run["request_start_to_response_ms"] is None
    and empty_run["scheduled_start_lateness_ms"] is None
    and empty_run["response_interarrival_ms"] is None
    and empty_run["effective_success_response_rate_hz"] is None
    and empty_run["complete_target_rate_run"] is False,
)
failed_run = _recorded_run(2, 10.0, lateness_ms=[0.0, 1.0], rtt_ms=[2.0, 3.0], statuses=[1, 1])
check(
    "error replies contribute no successful-response statistics",
    failed_run["responses_received"] == 2 and failed_run["success_count"] == 0
    and failed_run["request_start_to_response_ms"] is None
    and failed_run["response_interarrival_ms"] is None
    and failed_run["complete_target_rate_run"] is False,
)
single_run = _recorded_run(1, 10.0, lateness_ms=[0.0], rtt_ms=[2.0])
check(
    "one successful reply has a latency but no interarrival distribution",
    single_run["complete_target_rate_run"] is True
    and single_run["request_start_to_response_ms"]["median_ms"] == 2.0
    and single_run["response_interarrival_ms"] is None
    and single_run["effective_success_response_rate_hz"] is None,
)
tied_run = _recorded_run(2, 10.0, lateness_ms=[0.0, 0.0], rtt_ms=[12.0, 2.0])
check(
    "simultaneous replies keep zero intervals and an undefined effective rate",
    tied_run["response_interarrival_ms"]["max_ms"] == 0.0
    and tied_run["effective_success_response_rate_hz"] is None,
)

sends = [_recorded_send(0, 1, lateness_ms=0.1, started_ns=1_000_000_000)]
responses = {0: _recorded_response(1, 0, 1_000_000_000, rtt_ms=2.0, counter=1)}
before = copy.deepcopy((sends, responses))
host._reduce_pipelined_benchmark(
    1, 10.0, sends, responses, unsolicited_count=0, rx_errors=[],
    outstanding_after_drain=0, max_outstanding=1, sequence_window_exhausted=False,
)
check("report reduction does not modify the transcript", (sends, responses) == before)
