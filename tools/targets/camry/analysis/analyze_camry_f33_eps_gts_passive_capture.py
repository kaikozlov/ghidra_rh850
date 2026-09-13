#!/usr/bin/env python3
"""Classify one exact-F33 passive GTS+/CUW witness capture offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any, BinaryIO


SCHEMA = "camry-f33-eps-gts-passive-analysis-v1"
CAPTURE_SCHEMA = "camry-f33-eps-gts-passive-capture-v1"
CANBIN_MAGIC = b"CAMGTS1\0"
CANBIN_HEADER = struct.Struct("<QIBB")
NORMAL_EPS_BUS = 0
# This is a conservative evidence-correlation ceiling shared with the active
# exact-target triage, not a claim about every OEM package's protocol timeout.
PROGRAMMING_PAIR_MAX_NS = 3_000_000_000
KNOWN_ROUTES = {
    0x750: "central-gateway-request",
    0x758: "central-gateway-response",
    0x751: "gateway-0751-request",
    0x759: "gateway-0751-response",
    0x786: "dh-central-gateway-request",
    0x78E: "dh-central-gateway-response",
    0x7A0: "eps-secondary-request",
    0x7A8: "eps-secondary-response",
    0x7A1: "eps-primary-request",
    0x7A9: "eps-primary-response",
    0x7B0: "brake-request",
    0x7B8: "brake-response",
    0x777: "toyota-functional-request",
    0x7DF: "obd-functional-request",
}
SERVICE_NAMES = {
    0x10: "DiagnosticSessionControl",
    0x22: "ReadDataByIdentifier",
    0x3E: "TesterPresent",
    0x50: "DiagnosticSessionControlPositive",
    0x62: "ReadDataByIdentifierPositive",
    0x7E: "TesterPresentPositive",
    0x7F: "NegativeResponse",
}


class AnalysisError(RuntimeError):
    """Malformed or identity-incompatible capture evidence."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canbin_census(stream: BinaryIO) -> dict[str, object]:
    if stream.read(len(CANBIN_MAGIC)) != CANBIN_MAGIC:
        raise AnalysisError("can.bin has the wrong magic; expected exact GTS passive capture")
    count = 0
    buses: Counter[str] = Counter()
    addresses: Counter[str] = Counter()
    first_ns: int | None = None
    last_ns: int | None = None
    diagnostic_records: list[tuple[int, int, int, str]] = []
    while True:
        header = stream.read(CANBIN_HEADER.size)
        if not header:
            break
        if len(header) != CANBIN_HEADER.size:
            raise AnalysisError("can.bin has a truncated record header")
        t_ns, address, bus, dlc = CANBIN_HEADER.unpack(header)
        payload = stream.read(dlc)
        if len(payload) != dlc:
            raise AnalysisError("can.bin has a truncated record payload")
        if bus > 2 or address > 0x1FFFFFFF or dlc > 64:
            raise AnalysisError("can.bin contains an invalid physical CAN record")
        count += 1
        buses[str(bus)] += 1
        addresses[f"0x{address:X}"] += 1
        if 0x700 <= address <= 0x7FF:
            diagnostic_records.append((t_ns, bus, address, payload.hex()))
        first_ns = t_ns if first_ns is None else min(first_ns, t_ns)
        last_ns = t_ns if last_ns is None else max(last_ns, t_ns)
    return {
        "records": count,
        "buses": dict(sorted(buses.items())),
        "addresses": dict(sorted(addresses.items())),
        "first_monotonic_ns": first_ns,
        "last_monotonic_ns": last_ns,
        "_diagnostic_records": diagnostic_records,
    }


def _read_diagnostic(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise AnalysisError(f"diagnostic.ndjson line {line_number} is invalid JSON: {error}") from error
        if row.get("schema") != CAPTURE_SCHEMA:
            raise AnalysisError(
                f"diagnostic.ndjson line {line_number} has schema {row.get('schema')!r}, "
                f"expected {CAPTURE_SCHEMA!r}"
            )
        rows.append(row)
    return rows


def _rows_from_canbin(records: list[tuple[int, int, int, str]]) -> list[dict[str, Any]]:
    """Rebuild the classifier's rows from authoritative can.bin bytes."""
    rows: list[dict[str, Any]] = []
    for t_ns, bus, address, data_hex in records:
        data = bytes.fromhex(data_hex)
        offset = 0
        extension: int | None = None
        if address in {0x750, 0x758} and len(data) >= 2 and data[0] in {0x0F, 0x5F, 0x6D}:
            extension = data[0]
            offset = 1

        view: dict[str, Any] = {"transport": "empty"}
        if data:
            pci = data[offset]
            frame_type = pci >> 4
            view["transport"] = {
                0: "isotp-single",
                1: "isotp-first",
                2: "isotp-consecutive",
                3: "isotp-flow-control",
            }.get(frame_type, "unknown")
            pdu_prefix = b""
            if frame_type == 0:
                length = pci & 0x0F
                start = offset + 1
                if length == 0 and len(data) > start:
                    length = data[start]
                    start += 1
                pdu_prefix = data[start:start + length]
                view["declared_pdu_length"] = length
            elif frame_type == 1 and len(data) >= offset + 2:
                length = ((pci & 0x0F) << 8) | data[offset + 1]
                pdu_prefix = data[offset + 2:]
                view["declared_pdu_length"] = length
            elif frame_type == 2:
                view["sequence_number"] = pci & 0x0F
            elif frame_type == 3:
                view["flow_status"] = pci & 0x0F
            if pdu_prefix:
                sid = pdu_prefix[0]
                view["uds_service"] = f"0x{sid:02X}"
                view["uds_service_name"] = SERVICE_NAMES.get(sid, "unknown")
                view["pdu_prefix_hex"] = pdu_prefix.hex()
                if sid == 0x7F and len(pdu_prefix) >= 3:
                    view["negative_for_service"] = f"0x{pdu_prefix[1]:02X}"
                    view["negative_response_code"] = f"0x{pdu_prefix[2]:02X}"
        if extension is not None:
            view["address_extension"] = f"0x{extension:02X}"
        rows.append({
            "schema": CAPTURE_SCHEMA,
            "t_ns": t_ns,
            "bus": bus,
            "address": f"0x{address:03X}",
            "route": KNOWN_ROUTES.get(address),
            "data_hex": data_hex,
            **view,
        })
    return rows


def _row_evidence_key(row: dict[str, Any]) -> tuple[object, ...]:
    return (
        int(row["t_ns"]),
        int(row["bus"]),
        int(str(row["address"]), 0),
        bytes.fromhex(str(row["data_hex"])).hex(),
        row.get("route"),
        row.get("address_extension"),
        row.get("transport"),
        row.get("uds_service"),
        row.get("pdu_prefix_hex"),
    )


def _prefix(row: dict[str, Any], value: str) -> bool:
    return str(row.get("pdu_prefix_hex", "")).lower().startswith(value.lower())


def _select(rows: list[dict[str, Any]], *, address: str | None = None,
            route: str | None = None, extension: str | None = None,
            bus: int | None = None) -> list[dict[str, Any]]:
    selected = []
    for row in rows:
        if address is not None and row.get("address") != address:
            continue
        if route is not None and row.get("route") != route:
            continue
        if extension is not None and row.get("address_extension") != extension:
            continue
        if bus is not None and int(row.get("bus", -1)) != bus:
            continue
        selected.append(row)
    return selected


def _ordered_programming_pairs(rows: list[dict[str, Any]]) -> list[dict[str, object]]:
    """Pair 10 02 requests with later 50 02 responses on the same captured bus.

    A bare positive-response-shaped frame is EPS-origin activity, but it is not
    enough to claim that this capture observed the session transition.  Panda
    returns several frames with one batch timestamp, so row order is retained
    as a second ordering key.
    """
    pending: dict[int, list[tuple[int, dict[str, Any]]]] = {}
    pairs: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        bus = int(row.get("bus", -1))
        if bus != NORMAL_EPS_BUS:
            continue
        if (
            row.get("route") == "eps-primary-request"
            and row.get("uds_service") == "0x10"
            and _prefix(row, "1002")
        ):
            pending.setdefault(bus, []).append((index, row))
            continue
        if not (
            row.get("route") == "eps-primary-response"
            and row.get("uds_service") == "0x50"
            and _prefix(row, "5002")
        ):
            continue
        requests = pending.get(bus, [])
        if not requests:
            continue
        # Use the nearest prior request and discard older candidates.  A
        # response outside the finite triage ceiling remains visible EPS-origin
        # activity, but is not promoted to a captured request/response pair.
        request_index, request = requests[-1]
        request_ns = int(request["t_ns"])
        response_ns = int(row["t_ns"])
        delta_ns = response_ns - request_ns
        pending[bus] = []
        if not 0 <= delta_ns <= PROGRAMMING_PAIR_MAX_NS:
            continue
        pairs.append({
            "bus": bus,
            "request_row": request_index,
            "response_row": index,
            "request_monotonic_ns": request_ns,
            "response_monotonic_ns": response_ns,
            "delta_ms": delta_ns / 1_000_000,
        })
    return pairs


def _timeline(rows: list[dict[str, Any]]) -> list[dict[str, object]]:
    interesting = []
    origin = min((int(row["t_ns"]) for row in rows), default=0)
    for row in rows:
        if row.get("route") is None and row.get("uds_service") is None:
            continue
        interesting.append({
            "t_offset_ms": (int(row["t_ns"]) - origin) / 1_000_000,
            "bus": row.get("bus"),
            "address": row.get("address"),
            "route": row.get("route"),
            "address_extension": row.get("address_extension"),
            "transport": row.get("transport"),
            "uds_service": row.get("uds_service"),
            "uds_service_name": row.get("uds_service_name"),
            "negative_for_service": row.get("negative_for_service"),
            "negative_response_code": row.get("negative_response_code"),
            "pdu_prefix_hex": row.get("pdu_prefix_hex"),
            "data_hex": row.get("data_hex"),
        })
    return interesting


def analyze(capture_dir: Path) -> dict[str, object]:
    capture_dir = capture_dir.resolve()
    can_path = capture_dir / "can.bin"
    diagnostic_path = capture_dir / "diagnostic.ndjson"
    summary_path = capture_dir / "summary.json"
    for path in (can_path, diagnostic_path):
        if not path.is_file():
            raise AnalysisError(f"required capture file is missing: {path}")

    summary: dict[str, Any] = {}
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text())
        if summary.get("schema") != CAPTURE_SCHEMA:
            raise AnalysisError(
                f"summary schema {summary.get('schema')!r} does not match {CAPTURE_SCHEMA!r}"
            )

    with can_path.open("rb") as stream:
        can_census = _canbin_census(stream)
    diagnostic_records = can_census.pop("_diagnostic_records")
    rows = _rows_from_canbin(diagnostic_records)
    indexed_rows = _read_diagnostic(diagnostic_path)
    integrity_issues: list[str] = []
    try:
        raw_keys = [_row_evidence_key(row) for row in rows]
        indexed_keys = [_row_evidence_key(row) for row in indexed_rows]
    except (KeyError, TypeError, ValueError) as error:
        indexed_keys = []
        raw_keys = [_row_evidence_key(row) for row in rows]
        integrity_issues.append(f"diagnostic.ndjson has malformed evidence fields: {error}")
    if indexed_keys != raw_keys:
        integrity_issues.append(
            "diagnostic.ndjson does not exactly reproduce the ordered diagnostic-range records and "
            "derived framing fields in can.bin"
        )

    by_address = Counter(str(row.get("address")) for row in rows)
    by_route = Counter(str(row.get("route")) for row in rows if row.get("route") is not None)
    by_service = Counter(str(row.get("uds_service")) for row in rows if row.get("uds_service") is not None)

    primary_requests = _select(rows, route="eps-primary-request", bus=NORMAL_EPS_BUS)
    primary_responses = _select(rows, route="eps-primary-response", bus=NORMAL_EPS_BUS)
    secondary_requests = _select(rows, route="eps-secondary-request", bus=NORMAL_EPS_BUS)
    secondary_responses = _select(rows, route="eps-secondary-response", bus=NORMAL_EPS_BUS)
    gateway_5f_requests = _select(rows, route="central-gateway-request", extension="0x5F")
    gateway_5f_responses = _select(rows, route="central-gateway-response", extension="0x5F")

    target_programming_requests = [
        row for row in primary_requests
        if row.get("uds_service") == "0x10" and _prefix(row, "1002")
    ]
    target_programming_positives = [
        row for row in primary_responses
        if row.get("uds_service") == "0x50" and _prefix(row, "5002")
    ]
    programming_pairs = _ordered_programming_pairs(rows)
    gateway_indices = [
        index for index, row in enumerate(rows)
        if row.get("route") in {"central-gateway-request", "central-gateway-response"}
        and row.get("address_extension") == "0x5F"
    ]
    primary_request_indices = [
        index for index, row in enumerate(rows)
        if row.get("route") == "eps-primary-request" and int(row.get("bus", -1)) == NORMAL_EPS_BUS
    ]
    primary_requests_with_prior_node_5f = sum(
        any(gateway_index < primary_index for gateway_index in gateway_indices)
        for primary_index in primary_request_indices
    )
    target_activity = bool(primary_responses)
    secondary_activity = bool(secondary_responses)
    gateway_activity = bool(gateway_5f_requests or gateway_5f_responses)

    if programming_pairs:
        outcome = "eps-programming-session-positive"
        next_action = (
            "Stop the OEM job before erase unless the exact VIN-selected package acceptance gate is complete; "
            "the primary EPS executor is alive in programming session."
        )
    elif target_activity:
        outcome = "eps-origin-response-observed"
        next_action = (
            "Classify the EPS identity/application-versus-boot response and use only the identity-gated exact "
            "inverse-restore path or the accepted OEM package."
        )
    elif secondary_activity:
        outcome = "secondary-application-response-observed"
        next_action = (
            "The application executes, but the secondary endpoint is not a programming handoff; preserve the "
            "capture and proceed through exact-VIN OEM package discovery."
        )
    elif primary_requests:
        outcome = "primary-eps-request-observed-no-response"
        next_action = (
            "The target request reached the current normal-harness bus but no EPS response was captured; preserve "
            "the GTS frontend stage and exact package-selection state. Incidental node-5F-shaped traffic on this "
            "witness does not prove the separate OBD exchange or gateway preparation."
        )
    elif gateway_activity:
        outcome = "incidental-node-5f-shaped-traffic-no-primary-eps-request"
        next_action = (
            "Preserve the frames, but do not attribute them to the Mini-VCI/GTS exchange: this Panda remained on "
            "the normal harness and did not directly witness the separate OBD-mux segment."
        )
    elif rows:
        outcome = "diagnostic-range-traffic-seen-no-current-bus-eps-route"
        next_action = "Reconcile GTS vehicle selection, capture timing, and the actual target-side route."
    else:
        outcome = "no-diagnostic-traffic-observed"
        next_action = "The capture does not overlap an active GTS diagnostic exchange; repeat only the passive witness."

    summary_frames = summary.get("capture", {}).get("stats", {}).get("frames_total")
    if not summary:
        integrity_issues.append("summary.json is missing; capture completion and RX-loss state are unverified")
    if summary_frames is not None and int(summary_frames) != can_census["records"]:
        integrity_issues.append(
            f"summary frames_total={summary_frames} but can.bin contains {can_census['records']} records"
        )
    nonphysical = summary.get("capture", {}).get("stats", {}).get("nonphysical_rows", 0)
    if nonphysical:
        integrity_issues.append(
            f"{nonphysical} synthetic Panda receipt/rejection rows appeared despite passive ownership"
        )
    loss_monitor = summary.get("capture", {}).get("loss_monitor")
    if summary and not isinstance(loss_monitor, dict):
        integrity_issues.append("summary lacks the Panda/CAN loss monitor")
    elif isinstance(loss_monitor, dict) and not loss_monitor.get("valid_for_absence_claims", False):
        issues = loss_monitor.get("issues", [])
        integrity_issues.append("Panda/CAN loss monitor invalidates absence claims: " + "; ".join(map(str, issues)))

    final_silent = summary.get("final_silent")
    if summary and not isinstance(final_silent, dict):
        integrity_issues.append("summary lacks final Panda SILENT verification")
    elif isinstance(final_silent, dict) and not final_silent.get("verified", False):
        integrity_issues.append("final Panda SILENT safety was not verified")

    capture_status = summary.get("status", "summary-missing")
    coverage_issues = []
    if capture_status != "capture-complete":
        coverage_issues.append(f"capture status is {capture_status!r}, not 'capture-complete'")

    if integrity_issues:
        outcome = "capture-integrity-failed"
        next_action = (
            "Do not use this capture for a liveness or silence conclusion. Preserve it for diagnosis, correct the "
            "reported loss/index issue, and repeat only the data-frame-transmit-disabled witness."
        )
    elif coverage_issues and outcome not in {
        "eps-programming-session-positive",
        "eps-origin-response-observed",
        "secondary-application-response-observed",
    }:
        outcome = "capture-incomplete-no-absence-conclusion"
        next_action = (
            "The retained bytes may show traffic, but an incomplete capture cannot prove target silence. "
            "Repeat only the data-frame-transmit-disabled witness for the full bounded interval."
        )

    return {
        "schema": SCHEMA,
        "capture_directory": str(capture_dir),
        "capture_status": capture_status,
        "source_hashes": {
            "can.bin": _sha256(can_path),
            "diagnostic.ndjson": _sha256(diagnostic_path),
            "summary.json": _sha256(summary_path) if summary_path.is_file() else None,
        },
        "integrity": {
            "valid": not integrity_issues,
            "issues": integrity_issues,
            "can": can_census,
        },
        "coverage": {
            "complete": not coverage_issues,
            "valid_for_absence_claims": not integrity_issues and not coverage_issues,
            "issues": coverage_issues,
        },
        "diagnostic_census": {
            "rows": len(rows),
            "by_address": dict(sorted(by_address.items())),
            "by_route": dict(sorted(by_route.items())),
            "by_service": dict(sorted(by_service.items())),
        },
        "recovery_discriminators": {
            "gateway_5f_request_frames": len(gateway_5f_requests),
            "gateway_5f_response_frames": len(gateway_5f_responses),
            "primary_eps_request_frames": len(primary_requests),
            "primary_eps_response_frames": len(primary_responses),
            "secondary_eps_request_frames": len(secondary_requests),
            "secondary_eps_response_frames": len(secondary_responses),
            "target_10_02_requests": len(target_programming_requests),
            "target_50_02_positives": len(target_programming_positives),
            "ordered_target_10_02_50_02_pairs": len(programming_pairs),
            "primary_requests_with_prior_incidental_node_5f_frames": primary_requests_with_prior_node_5f,
        },
        "ordered_programming_pairs": programming_pairs,
        "outcome": outcome,
        "next_action": next_action,
        "repair_proved": False,
        "timeline": _timeline(rows),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = analyze(args.capture_dir)
    except (AnalysisError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
        print(args.output)
    return 0 if result["integrity"]["valid"] and result["coverage"]["complete"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
