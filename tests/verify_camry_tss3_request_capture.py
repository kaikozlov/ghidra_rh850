#!/usr/bin/env python3
"""Verify the turnkey OQ-052 read-only Brake/FRC TSS3-request capture tooling.

Everything here is deterministic and vehicle-free: the pinned request table,
the registry-driven decode contract, the single-frame and multiframe response
paths, the pandad guard reuse, the offline analyzer over a synthetic capture
directory, and the plan-only CLI. No live result is claimed or fabricated.
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import tools.analyze_camry_tss3_request_capture as analyze_mod
import tools.camry_frc_lta_capture as lta
import tools.camry_tss3_request_capture as cap

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][camry_tss3_request_capture] {name}" + (f" ({detail})" if detail else ""))


print("== pinned read-only request table from the tracked registry ==")
targets = cap.build_did_table(cap.load_registry())
check("exactly nine pinned (ECU, DID) targets",
      len(targets) == 9
      and [t.ecu for t in targets] == ["brake"] * 4 + ["frc"] * 5)
check("routes are the pinned physical pairs on one bus",
      all(t.tx == 0x7B0 and t.rx == 0x7B8 for t in targets if t.ecu == "brake")
      and all(t.tx == 0x792 and t.rx == 0x79A for t in targets if t.ecu == "frc"))
check("DIDs are exactly the OQ-052 sets",
      [t.did for t in targets] == [0x10A1, 0x10A2, 0x10A3, 0x10A4,
                                   0x1B03, 0x1B04, 0x1B05, 0x1B06, 0x1B07])
check("every request is the fixed read-only single-frame 03 22 DID in the default session",
      all(t.request == bytes((0x03, 0x22, t.did >> 8, t.did & 0xFF)) + bytes(4) for t in targets))
check("Toyota names come from the registry, brake observers named 'from Toyota Safety Sense'",
      {t.signals[0].name for t in targets if t.ecu == "brake"} == {
          "Request Acceleration of Upper Limit from Toyota Safety Sense",
          "Request Acceleration of Lower Limit from Toyota Safety Sense",
          "Request Acceleration and Deceleration ID of Upper Limit from Toyota Safety Sense",
          "Request Acceleration and Deceleration ID of Lower Limit from Toyota Safety Sense"})
check("FRC names are the ISA request vocabulary including the multiframe 0x1B05 pair",
      {s.name for t in targets if t.did == 0x1B05 for s in t.signals} == {
          "ISA Requesting Vehicle Speed (Upper Limit)",
          "ISA Request Acceleration (Upper Limit) (Variation No Limit)"})
with tempfile.TemporaryDirectory() as td:
    wrong = Path(td) / "wrong_registry.json"
    wrong.write_text(json.dumps({
        "schema": "toyota-diagnostics-registry-v4",
        "profile": {"profile": "camry-2026-f33", "panda_bus": 0,
                    "ecus": [{"key": "brake", "address": 0x7B0}, {"key": "frc", "address": 0x7FF}]},
        "catalogs": {},
    }))
    try:
        cap.load_registry(wrong)
        check("registry address drift fails closed", False, "load_registry accepted a wrong ECU address")
    except SystemExit as exc:
        check("registry address drift fails closed", "refusing to guess routes" in str(exc))
    wrong.write_text(json.dumps({
        "schema": "toyota-diagnostics-registry-v4",
        "profile": {"profile": "some-other-car", "panda_bus": 0, "ecus": []},
        "catalogs": {},
    }))
    try:
        cap.load_registry(wrong)
        check("foreign registry profile fails closed", False, "load_registry accepted a foreign profile")
    except SystemExit as exc:
        check("foreign registry profile fails closed",
              "not toyota-diagnostics-registry-v4/camry-2026-f33" in str(exc))

plan = cap.plan(targets)
check("plan pins both routes and the live-proven bus-0 route source",
      plan["diag_bus"] == 0
      and "FRC 0x792 live-proven" in plan["route_source"]
      and "Brake 0x7B0 live-reached" in plan["route_source"]
      and "0x7B0->0x7B8 pinned by VAR-069" in plan["route_source"])
check("plan is observation-only with no session escalation",
      plan["session_control"] is False and plan["security_access"] is False
      and plan["routine_control"] is False and plan["vehicle_control_tx"] is False
      and plan["flash_write"] is False
      and "flow-control frame" in plan["transport"])
check("plan states the unmeasured-live-support boundary",
      "live PID support on the exact Camry is unmeasured" in plan["boundary"])
check("plan decoder contract is the tracked registry decoder",
      plan["decoder"]["contract"] == "p5-linear-msb0-v1"
      and plan["decoder"]["source"].endswith("toyota_diag_registry_camry_2026.json")
      and plan["decoder"]["implementation"].endswith("decode_p5_signal"))

print("\n== registry decode contract on synthetic response PDUs ==")
brake_targets = tuple(t for t in targets if t.rx == 0x7B8)
frc_targets = tuple(t for t in targets if t.rx == 0x79A)
parsed = cap.parse_response_pdu(bytes.fromhex("6210A1FC18"), brake_targets)
check("brake 0x10A1 signed upper-limit request decodes to -1.000 m/s^2",
      parsed["ecu"] == "brake" and parsed["did"] == "0x10A1"
      and parsed["signals"][0]["converted_integer"] == -1000
      and parsed["signals"][0]["value"] == "-1.000")
parsed = cap.parse_response_pdu(bytes.fromhex("621B033F"), frc_targets)
check("FRC 0x1B03 raw 63 renders the OEM 'Driver Operation' pattern",
      parsed["signals"][0]["raw"] == 63 and parsed["signals"][0]["pattern"] == "Driver Operation")
parsed = cap.parse_response_pdu(bytes.fromhex("621B06020103"), frc_targets)
check("FRC 0x1B06 decodes all three request bytes with OEM patterns",
      [s["pattern"] for s in parsed["signals"]] == [
          "Engine and Brake 2",
          "Brake Coordination Down Shifting Request Exists",
          "FB Control Low Gain"])
parsed = cap.parse_response_pdu(bytes.fromhex("621B0700E0"), frc_targets)
check("FRC 0x1B07 bits 8..10 decode to the three permission flags",
      [s["pattern"] for s in parsed["signals"]] == ["Not Allowed", "Allowed", "Allowed"])
parsed = cap.parse_response_pdu(bytes.fromhex("7F2231"), frc_targets)
check("negative response retains NRC 0x31 with per-ECU attribution only",
      parsed["status"] == "negative" and parsed["nrc"] == "0x31" and parsed["did"] is None)
parsed = cap.parse_response_pdu(bytes.fromhex("621B04" + "00000FA0"), frc_targets)
check("FRC 0x1B04 signed 32-bit accel applies the registry mul=1000 scale",
      parsed["signals"][0]["raw"] == 4000 and parsed["signals"][0]["value"] == "4000.000")
parsed = cap.parse_response_pdu(bytes.fromhex("6210A1FC"), brake_targets)
check("short positive payload retains a decode error instead of guessing",
      parsed["status"] == "positive" and "decode_error" in parsed["signals"][0])
check("foreign DID echo from a responder is not attributed",
      cap.parse_response_pdu(bytes.fromhex("621B033F"), brake_targets) is None)

print("\n== capture loop: single-frame, multiframe, negative, timeout ==")


class FakePanda:
    def __init__(self, batches):
        self.batches = list(batches)
        self.sent = []

    def can_recv(self):
        return self.batches.pop(0) if self.batches else []

    def can_send(self, addr, data, bus):
        self.sent.append((addr, bytes(data).hex(), bus))


by_rx = {}
for t in targets:
    by_rx.setdefault(t.rx, tuple(x for x in targets if x.rx == t.rx))


def run_capture(batches, batch_times=None, outstanding_targets=(), outstanding_t0_ns=None):
    panda = FakePanda(batches)
    oracle = io.StringIO()
    canbuf = io.BytesIO()
    stats = {"frames_by_bus": Counter({"0": 0, "1": 0, "2": 0}),
             "responses": {ecu: {"positive_by_did": Counter(), "negative": 0, "nrc": Counter(),
                                  "query_timeout": 0, "assembly_error": 0, "protocol_error": 0,
                                  "response_pending": 0}
                           for ecu in ("brake", "frc")},
             "rx_ecu": {0x7B8: "brake", 0x79A: "frc"}}
    pending = {}
    base_ns = (outstanding_t0_ns if outstanding_t0_ns is not None else
               (batch_times[0] if batch_times else cap.time.monotonic_ns()))
    outstanding = {target.rx: cap.OutstandingQuery(target=target, t0_ns=base_ns)
                   for target in outstanding_targets}
    quarantined = set()
    cap.write_canbin_header(canbuf)
    calls = max(len(batches) + 2, 8)
    for index in range(calls):
        now_ns = batch_times[index] if batch_times and index < len(batch_times) else None
        cap._capture_messages(panda, canbuf, oracle, by_rx, stats=stats, pending=pending,
                              outstanding=outstanding, quarantined=quarantined, now_ns=now_ns)
    rows = [json.loads(line) for line in oracle.getvalue().splitlines() if line]
    return panda, rows, canbuf, stats, outstanding, quarantined


brake_a1 = next(t for t in targets if t.ecu == "brake" and t.did == 0x10A1)
frc_1b03 = next(t for t in targets if t.ecu == "frc" and t.did == 0x1B03)
frc_1b05 = next(t for t in targets if t.ecu == "frc" and t.did == 0x1B05)
poll_targets = cap._interleave_targets(targets)
check("poll order alternates Brake/FRC responders while preserving each ECU DID order",
      [target.key for target in poll_targets] == [
          "brake/0x10A1", "frc/0x1B03", "brake/0x10A2", "frc/0x1B04",
          "brake/0x10A3", "frc/0x1B05", "brake/0x10A4", "frc/0x1B06", "frc/0x1B07",
      ])

panda, rows, canbuf, stats, outstanding, quarantined = run_capture([
    [(0x7B8, bytes.fromhex("056210A1FC180000"), 0)],
    [(0x79A, bytes.fromhex("1008621B05500000"), 0)],
    [(0x79A, bytes.fromhex("210FA00000000000"), 0)],
    [(0x18A, bytes(64), 1)],
], outstanding_targets=(brake_a1, frc_1b05))
positive_rows = [r for r in rows if r.get("status") == "positive"]
check("single-frame brake positive retained with decoded value and request association",
      any(r["did"] == "0x10A1" and r["request_did"] == "0x10A1"
          and r["transport"] == "single-frame" and r["signals"][0]["value"] == "-1.000"
          for r in positive_rows))
mf = next(r for r in positive_rows if r["did"] == "0x1B05")
check("multiframe 0x1B05 assembled, associated, decoded, and frames retained",
      mf["transport"] == "multiframe" and mf["request_did"] == "0x1B05"
      and mf["raw"] == "5000000fa0"
      and mf["frames"] == ["1008621b05500000", "210fa00000000000"]
      and [sig["value"] for sig in mf["signals"]] == ["80", "4000.000"])
check("exactly one flow-control frame sent for the expected FRC multiframe response",
      panda.sent == [(0x792, "3000000000000000", 0)])
check("resolved responses clear both outstanding responder slots", outstanding == {})
check("passive capture retains every incoming bus-0/1 frame including 64-byte FD",
      stats["frames_by_bus"] == Counter({"0": 3, "1": 1, "2": 0})
      and len(list(lta.iter_canbin_records(io.BytesIO(canbuf.getvalue())))) == 4)

panda, rows, _canbuf, stats, outstanding, quarantined = run_capture(
    [[(0x79A, bytes.fromhex("037F223100000000"), 0)]],
    outstanding_targets=(frc_1b03,))
negative = next(r for r in rows if r.get("status") == "negative")
check("negative NRC is associated to the sole outstanding DID without claiming an echoed DID",
      negative["did"] is None and negative["request_did"] == "0x1B03" and negative["nrc"] == "0x31"
      and outstanding == {} and stats["responses"]["frc"]["nrc"] == Counter({"0x31": 1}))

base = 1_500_000_000
panda, rows, _canbuf, stats, outstanding, quarantined = run_capture(
    [[(0x79A, bytes.fromhex("037F227800000000"), 0)],
     [(0x79A, bytes.fromhex("04621B033F000000"), 0)]],
    batch_times=[base + 400_000_000, base + 700_000_000],
    outstanding_targets=(frc_1b03,), outstanding_t0_ns=base)
check("NRC 0x78 keeps the request outstanding and refreshes its deadline until final response",
      [row["status"] for row in rows if row.get("ecu") == "frc"] == ["response_pending", "positive"]
      and rows[0]["request_did"] == "0x1B03"
      and outstanding == {} and quarantined == set()
      and stats["responses"]["frc"]["response_pending"] == 1
      and stats["responses"]["frc"]["nrc"] == Counter({"0x78": 1}))

base = 1_800_000_000
panda, rows, _canbuf, _stats, outstanding, quarantined = run_capture(
    [[(0x79A, bytes.fromhex("04621B033F000000"), 0)]],
    batch_times=[base + cap.QUERY_TIMEOUT_NS + 1],
    outstanding_targets=(frc_1b03,), outstanding_t0_ns=base)
check("terminal response already in the drained batch wins over the local query-timeout boundary",
      any(row.get("status") == "positive" and row.get("request_did") == "0x1B03" for row in rows)
      and not any(row.get("status") == "query_timeout" for row in rows)
      and outstanding == {} and quarantined == set())

panda, rows, _canbuf, stats, outstanding, quarantined = run_capture(
    [[(0x79A, bytes.fromhex("04621B9901000000"), 0)]],
    outstanding_targets=(frc_1b03,))
unparsed = next(r for r in rows if r.get("status") == "unparsed_response")
check("complete but unparseable target response is retained and quarantined instead of becoming a false timeout",
      unparsed["raw_pdu"] == "621b9901" and unparsed["request_did"] == "0x1B03"
      and outstanding == {} and quarantined == {0x79A}
      and stats["responses"]["frc"]["protocol_error"] == 1
      and not any(r.get("status") == "query_timeout" for r in rows))

panda, rows, _canbuf, _stats, outstanding, quarantined = run_capture(
    [[(0x79A, bytes.fromhex("1008621B05500000"), 0)]],
    batch_times=[1_000_000_000, 1_000_000_000 + cap.ASSEMBLY_TIMEOUT_NS + 1],
    outstanding_targets=(frc_1b05,))
check("stale partial assembly expires with retained frames and request association",
      any(r.get("status") == "assembly_timeout" and r["request_did"] == "0x1B05"
          and r["frames"] == ["1008621b05500000"] for r in rows)
      and outstanding == {} and quarantined == {0x79A})

panda, rows, _canbuf, stats, outstanding, quarantined = run_capture([
    [(0x79A, bytes.fromhex("1008621B05500000"), 0)],
    [(0x79A, bytes.fromhex("220FA00000000000"), 0)],
], outstanding_targets=(frc_1b05,))
check("wrong consecutive-frame sequence number clears the request as an assembly error",
      any(r.get("status") == "assembly_sequence_error" and r["request_did"] == "0x1B05" for r in rows)
      and outstanding == {} and quarantined == {0x79A}
      and stats["responses"]["frc"]["assembly_error"] == 1)

base = 2_000_000_000
panda, rows, _canbuf, _stats, outstanding, quarantined = run_capture(
    [[(0x79A, bytes.fromhex("1008621B05500000"), 0)],
     [(0x79A, bytes.fromhex("210FA00000000000"), 0)]],
    batch_times=[base + cap.QUERY_TIMEOUT_NS - 10_000_000,
                 base + cap.QUERY_TIMEOUT_NS + 10_000_000],
    outstanding_targets=(frc_1b05,), outstanding_t0_ns=base)
check("active multiframe assembly owns its 200-ms deadline across the 500-ms query boundary",
      any(r.get("status") == "positive" and r.get("did") == "0x1B05" for r in rows)
      and not any(r.get("status") == "query_timeout" for r in rows)
      and outstanding == {} and quarantined == set())

print("\n== scheduler association: at most one unresolved query per ECU ==")
outstanding = {brake_a1.rx: cap.OutstandingQuery(target=brake_a1, t0_ns=1_000_000_000)}
quarantined = set()
due = {target.key: 1_000_000_000 for target in poll_targets}
next_index, selected = cap._next_query_target(
    poll_targets, 0, outstanding, quarantined, due, now_ns=1_000_000_000)
check("busy Brake responder is skipped in favor of FRC rather than overlapping same-ECU RDBI",
      selected is frc_1b03 and next_index == 2)
outstanding[frc_1b03.rx] = cap.OutstandingQuery(target=frc_1b03, t0_ns=1_000_000_000)
unchanged_index, selected = cap._next_query_target(
    poll_targets, next_index, outstanding, quarantined, due, now_ns=1_000_000_000)
check("no request is selected while both responder slots are unresolved",
      selected is None and unchanged_index == next_index)

single_due = {frc_1b03.key: 2_000_000_000}
_, early = cap._next_query_target((frc_1b03,), 0, {}, set(), single_due,
                                  now_ns=1_999_999_999)
_, on_time = cap._next_query_target((frc_1b03,), 0, {}, set(), single_due,
                                    now_ns=2_000_000_000)
check("per-DID due time prevents an idle target from consuming another target's skipped rate",
      early is None and on_time is frc_1b03)

oracle = io.StringIO()
stats = {"responses": {ecu: {"positive_by_did": Counter(), "negative": 0, "nrc": Counter(),
                              "query_timeout": 0, "assembly_error": 0}
                       for ecu in ("brake", "frc")}}
cap._expire_query_timeouts(outstanding, {}, quarantined, oracle, stats,
                           now_ns=1_000_000_000 + cap.QUERY_TIMEOUT_NS + 1)
timeout_rows = [json.loads(line) for line in oracle.getvalue().splitlines()]
check("query timeout records exact DID and quarantines both responder slots",
      outstanding == {} and quarantined == {0x7B8, 0x79A}
      and {(row["ecu"], row["request_did"], row["status"]) for row in timeout_rows} == {
          ("brake", "0x10A1", "query_timeout"), ("frc", "0x1B03", "query_timeout")}
      and stats["responses"]["brake"]["query_timeout"] == 1
      and stats["responses"]["frc"]["query_timeout"] == 1)
retry_index, retry_target = cap._next_query_target(
    poll_targets, next_index, outstanding, quarantined, due, now_ns=2_000_000_000)
check("quarantined responders are never retried, preventing late-negative misassociation",
      retry_target is None and retry_index == next_index)

# A first frame without an outstanding query is retained as anomalous metadata
# but must never cause a flow-control transmit.
panda, rows, _canbuf, _stats, _outstanding, _quarantined = run_capture([
    [(0x79A, bytes.fromhex("1008621B05500000"), 0)],
])
check("unsolicited multiframe response never triggers flow control",
      panda.sent == [] and any(row.get("status") == "unsolicited_first_frame" for row in rows))

panda, rows, _canbuf, stats, outstanding, quarantined = run_capture(
    [[(0x79A, bytes.fromhex("210FA00000000000"), 0)]],
    outstanding_targets=(frc_1b05,))
check("consecutive frame without an assembly is retained as a protocol error and quarantines the responder",
      any(row.get("status") == "unexpected_consecutive_frame"
          and row.get("request_did") == "0x1B05" for row in rows)
      and outstanding == {} and quarantined == {0x79A}
      and stats["responses"]["frc"]["protocol_error"] == 1)


print("\n== shared plumbing: no duplicated stack ==")
check("canbin writer and pandad guard are reused from the LTA capture tool",
      cap.write_canbin_header is lta.write_canbin_header
      and cap.write_canbin_record is lta.write_canbin_record
      and analyze_mod.iter_canbin_records is lta.iter_canbin_records
      and cap.find_pandad_processes is lta.find_pandad_processes
      and cap.load_panda_class is lta.load_panda_class
      and cap.ELM327_SAFETY_MODEL == lta.ELM327_SAFETY_MODEL)
check("decode path is the canonical ddb_semantics decoder",
      analyze_mod.build_did_table is cap.build_did_table)
source = (REPO / "tools/camry_tss3_request_capture.py").read_text()
check("capture tool hard-refuses pandad USB contention",
      "refusing Panda USB collision: pandad is running" in source
      and "pandad appeared during capture; aborting" in source)
check("the only non-request transmit constant is the flow-control frame",
      cap.FLOW_CONTROL_FRAME[0] == 0x30
      and all(t.request[:2] == b"\x03\x22" for t in targets)
      and source.count("panda.can_send(") == 2)

print("\n== offline analyzer over a synthetic capture directory ==")
with tempfile.TemporaryDirectory() as td:
    capture = Path(td) / "capture"
    capture.mkdir()
    (capture / "metadata.json").write_text(json.dumps({
        "schema": "camry-tss3-request-capture-v1", "diag_bus": 0, "duration_s": 2.0,
        "error": None, "files": {"can": "can.bin", "oracle": "oracle.ndjson"}}))
    rows = []
    t0 = 1_000_000_000
    for cycle in range(3):
        base = t0 + cycle * 500_000_000
        rows += [
            {"type": "query", "ecu": "brake", "did": "0x10A1", "t_ns": base},
            {"type": "response", "ecu": "brake", "did": "0x10A1", "status": "positive",
             "t_ns": base + 8_000_000, "raw": "fc18",
             "signals": [{"name": "Request Acceleration of Upper Limit from Toyota Safety Sense",
                          "converted_integer": -1000, "value": "-1.000"}]},
            {"type": "query", "ecu": "frc", "did": "0x1B03", "t_ns": base + 60_000_000},
            {"type": "response", "ecu": "frc", "did": "0x1B03", "status": "positive",
             "t_ns": base + 70_000_000, "raw": "0b",
             "signals": [{"name": "ISA Requesting Vertical ID (Upper Limit)",
                          "converted_integer": 11, "value": "11"}]},
            {"type": "query", "ecu": "brake", "did": "0x10A3", "t_ns": base + 120_000_000},
            {"type": "response", "ecu": "brake", "did": None, "request_did": "0x10A3",
             "status": "negative", "nrc": "0x31", "t_ns": base + 128_000_000},
        ]
    # one out-of-gap FRC 0x1B05 sample to prove pair-gap filtering
    rows.append({"type": "response", "ecu": "frc", "did": "0x1B05", "status": "positive",
                 "t_ns": t0 + 5_000_000_000, "raw": "5000000fa0",
                 "signals": [
                     {"name": "ISA Requesting Vehicle Speed (Upper Limit)",
                      "converted_integer": 80, "value": "80"},
                     {"name": "ISA Request Acceleration (Upper Limit) (Variation No Limit)",
                      "converted_integer": 4000000, "value": "4000.000"}]})
    (capture / "oracle.ndjson").write_text("".join(json.dumps(r) + "\n" for r in rows))
    with (capture / "can.bin").open("wb") as stream:
        cap.write_canbin_header(stream)
        cap.write_canbin_record(stream, t0 + 30_000_000, 0, 0x0AA,
                                bytes.fromhex("1e571e571e571e57"))
        cap.write_canbin_record(stream, t0 + 40_000_000, 1, 0x18A, bytes(64))
    summary = analyze_mod.analyze(capture)
    check("per-DID census is exact for positives, raw values, and cadence",
          summary["oracle"]["brake/0x10A1"]["query_count"] == 3
          and summary["oracle"]["brake/0x10A1"]["positive_count"] == 3
          and summary["oracle"]["brake/0x10A1"]["raw_counts"] == {"fc18": 3}
          and summary["oracle"]["brake/0x10A1"]["positive_interval_median_ns"] == 500_000_000)
    check("negative responses are safely associated per DID and also summarized per ECU",
          summary["oracle_per_ecu_negatives"]["brake"] == {
              "negative_count": 3, "response_pending_count": 0, "nrc_counts": {"0x31": 3}}
          and summary["oracle"]["brake/0x10A3"]["negative_count"] == 3
          and summary["oracle"]["brake/0x10A3"]["nrc_counts"] == {"0x31": 3})
    check("unpolled DID reports not-polled and zero-positive DID reports unmeasured",
          summary["oracle"]["frc/0x1B06"]["live_support"] == "not polled"
          and summary["oracle"]["brake/0x10A3"]["live_support"] == "unmeasured: no positive response recorded")
    join = summary["cross_ecu_joins"]["request_acceleration_upper_vs_variation_no_limit"]
    check("out-of-gap FRC samples are excluded from cross-ECU pairing",
          join["brake_positive_count"] == 3 and join["frc_positive_count"] == 1
          and join["paired_count"] == 0)
    check("passive CAN context counts buses and the exact 0x0AA wheel-speed geometry",
          summary["can"]["frames_by_bus"] == {"0": 1, "1": 1}
          and summary["can"]["wheel_speed_context"]["sample_count"] == 1
          and summary["can"]["wheel_speed_context"]["moving_over_2kph_sample_count"] == 1)
    check("interpretation keeps the OQ-052 proof boundary",
          "not a transform proof" in json.dumps(summary) or
          "SecOC/integrity ownership remain open" in summary["interpretation"]["proof_boundary"])
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools/analyze_camry_tss3_request_capture.py"), str(capture)],
        capture_output=True, text=True, check=False)
    check("analyzer CLI reproduces the library summary byte-for-byte",
          proc.returncode == 0 and json.loads(proc.stdout) == json.loads(json.dumps(summary)))

print("\n== capture CLI is turnkey without a vehicle ==")
proc = subprocess.run([sys.executable, str(REPO / "tools/camry_tss3_request_capture.py")],
                      capture_output=True, text=True, check=False)
plan_only = json.loads(proc.stdout) if proc.returncode == 0 else {}
check("plan-only CLI prints the validated plan and exits zero",
      proc.returncode == 0 and plan_only.get("schema") == "camry-tss3-request-capture-v1"
      and plan_only.get("vehicle_control_tx") is False
      and "at most one unresolved RDBI" in plan_only.get("synchronization", "")
      and plan_only.get("poll_order", []) == [target.key for target in poll_targets]
      and "cannot donate its slot" in plan_only.get("pacing", "")
      and len(plan_only.get("requests", [])) == 9)
proc = subprocess.run([sys.executable, str(REPO / "tools/camry_tss3_request_capture.py"), "--execute"],
                      capture_output=True, text=True, check=False)
check("--execute without --out fails fast", proc.returncode != 0 and "--out is required" in proc.stderr)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
