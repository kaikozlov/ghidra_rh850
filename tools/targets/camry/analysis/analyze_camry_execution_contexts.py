#!/usr/bin/env python3
"""Generate the exact-Camry foreground, interrupt, and receive-context catalog."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many
from tools.firmware.rh850_instructions import is_jarl22, jarl22_target
from tools.targets.camry.research.audit_camry_f33_definedness_boundaries import (
    STACK_FINDING_MARGIN,
    stack_watermark,
)

TARGET = "camry-8965F3307000"
IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
EXPECTED_IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
SYMBOLS = REPO_ROOT / "decomp/camry-8965F3307000/symbols.jsonl"
INVENTORY = REPO_ROOT / "data/targets/camry-8965F3307000/ghidra_project_inventory.baseline.jsonl"
RX_MAP = REPO_ROOT / "data/generated/camry_f33_application_rx/application_rx_map.csv"
RX_SIGNALS = REPO_ROOT / "data/generated/camry_f33_application_rx/application_rx_signal_evidence.csv"
RX_TABLES = REPO_ROOT / "data/generated/camry_f33_application_rx/tables.json"
TX_ARTIFACT = REPO_ROOT / "data/generated/camry_8965F3307000_eps_tx.json"
EXECUTION_COVERAGE = REPO_ROOT / "data/generated/camry_8965F3307000_execution_coverage.json"
OUTPUT = Path("data/generated/camry_8965F3307000_execution_contexts.json")
TRACE_OUTPUT_DIR = REPO_ROOT / "build/out/targets/camry-8965F3307000/execution-contexts"
FOREGROUND_STACK_SCENARIO = (
    REPO_ROOT / "tests/fixtures/rh850/machine/camry-8965F3307000"
    / "camry_f33_scheduler_publication_native_ch1_single_request_returns.json"
)

CLOCK_HZ = 80_000_000
INTBP = 0x20200
STARTUP_FIRST_CALL = 0x637F6
STARTUP_CALL_COUNT = 21

TIMER_CONTEXTS = (
    {
        "key": "tauj0_ch0",
        "timer_channel": 0,
        "eic_channel": 133,
        "eic_address": 0xFFFFB10A,
        "eic_control": 0x0046,
        "vector_entry": 0x713B0,
        "task_entry": 0x65FAE,
        "compare_address": 0x30DF0,
        "initial_offset_address": 0x30DF4,
        "probe_stop": 0x713F6,
        "role": "phase-current, diagnostic, and motor-input acquisition cycle",
        "writes": ["acquisition snapshots", "diagnostic input latches", "motor input latches"],
        "consumed_by": ["tauj0_ch1", "foreground"],
    },
    {
        "key": "tauj0_ch1",
        "timer_channel": 1,
        "eic_channel": 134,
        "eic_address": 0xFFFFB10C,
        "eic_control": 0x0047,
        "vector_entry": 0x7145A,
        "task_entry": 0x65FEA,
        "compare_address": 0x30DF8,
        "initial_offset_address": 0x30DFC,
        "probe_stop": 0x65FEA,
        "role": "assist-source, command-generation, and publication cycle",
        "writes": ["assist-source snapshots", "command/current publication banks", "observer inputs"],
        "consumed_by": ["tauj0_ch2", "foreground"],
    },
    {
        "key": "tauj0_ch2",
        "timer_channel": 2,
        "eic_channel": 135,
        "eic_address": 0xFFFFB10E,
        "eic_control": 0x0049,
        "vector_entry": 0x71506,
        "task_entry": 0x66026,
        "compare_address": 0x30E00,
        "initial_offset_address": 0x30E04,
        "probe_stop": 0x66026,
        "role": "monitor, observer-scaling, and observer-publication cycle",
        "writes": ["monitor state", "scaled observer state", "observer publication bank"],
        "consumed_by": ["foreground"],
    },
    {
        "key": "foreground",
        "timer_channel": 3,
        "eic_channel": 136,
        "eic_address": 0xFFFFB110,
        "eic_control": 0x00CF,
        "vector_entry": 0x62E1E,
        "task_entry": 0x66062,
        "compare_address": 0x30E08,
        "initial_offset_address": 0x30E0C,
        "probe_stop": 0x10000,
        "role": "polled communication, application, diagnostic, crypto, and NVM foreground cycle",
        "writes": ["COM and diagnostic state", "foreground output projections", "NVM state"],
        "consumed_by": [],
    },
)

ISR_ROWS = (
    (8, 0xFFFEEA10, 0x0040, 0x71AE4, "ECM error dispatch", ["ECM error latches", "fault counters", "clear registers"], []),
    (133, 0xFFFFB10A, 0x0046, 0x713B0, "TAUJ0 channel-0 periodic acquisition", ["diagnostic and motor input latches", "acquisition snapshots"], [0x65FEA, 0x66062]),
    (134, 0xFFFFB10C, 0x0047, 0x7145A, "TAUJ0 channel-1 command/publication cycle", ["assist-source snapshots", "command/current publication banks"], [0x66026, 0x66062]),
    (135, 0xFFFFB10E, 0x0049, 0x71506, "TAUJ0 channel-2 observer cycle", ["monitor state", "observer publication bank"], [0x66062]),
    (187, 0xFFFFB176, 0x8048, 0x66100, "RSCFD channel-1 receive", ["software receive ring at 0xFEBE4038", "ring indices and count"], [0x7A254, 0x7A408, 0x988C2]),
    (188, 0xFFFFB178, 0x8048, 0x660BE, "RSCFD channel-1 transmit completion", ["RSCFD completion status", "software transmit-route completion state"], [0x667E6]),
    (292, 0xFFFFB248, 0x0048, 0x66142, "ICU-S completion path A", ["guarded crypto callback and job state"], [0x88EC0]),
    (293, 0xFFFFB24A, 0x0048, 0x66184, "ICU-S completion path B", ["guarded crypto callback and job state"], [0x88EC0]),
    (379, 0xFFFFB2F6, 0x0048, 0x661C6, "DataFlash suspend-ready completion", ["flash-operation completion state"], [0x66CF6]),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hx(value: int, width: int = 8) -> str:
    return f"0x{value:0{width}X}"


def u32(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address)[0]


def load_symbols() -> dict[int, str]:
    symbols: dict[int, str] = {}
    for line in SYMBOLS.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        symbols[int(row["addr"], 16)] = row["name"]
    return symbols


def load_function_starts() -> set[int]:
    starts: set[int] = set()
    with INVENTORY.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("record") == "function":
                starts.add(int(row["entry"]["offset"], 16))
    return starts


def function_ref(address: int, symbols: dict[int, str]) -> dict[str, Any]:
    return {"address": hx(address), "name": symbols.get(address, f"unrecovered_{address:08x}")}


def startup_calls(image: bytes, symbols: dict[int, str]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for index in range(STARTUP_CALL_COUNT):
        site = STARTUP_FIRST_CALL + index * 4
        if not is_jarl22(image, site):
            raise ValueError(f"startup call {index + 1} is not JARL at {site:#x}")
        target = jarl22_target(image, site)
        calls.append({"number": index + 1, "call_site": hx(site), **function_ref(target, symbols)})
    if calls[10]["address"] != hx(0x62E6A) or calls[18]["address"] != hx(0x666BC) or calls[20]["address"] != hx(0x665F2):
        raise ValueError("startup interrupt/timer call positions drifted")
    return calls


def timer_probe(context: dict[str, Any], period_ticks: int) -> dict[str, Any]:
    channel = context["timer_channel"]
    registers: dict[str, str] = {
        "sp": "0xfebe2000", "gp": "0xfebeb800", "tp": "0x23dfc", "lp": "0x10000",
        "r6": "0xffe50054", "r7": hex(1 << channel), "PSW": "0", "PMR": "0",
    }
    if channel != 3:
        registers.update({
            "INTBP": hex(INTBP), "RBASE": "0", "EBASE": "0x20000", "EIWR": "0",
            "CTPC": "0", "CTPSW": "0", **{f"MPAT{i}": "0" for i in range(16)},
        })
    checks: list[dict[str, Any]] = [{
        "name": "one-underflow-request", "kind": "event-count",
        "operation": "interrupt-request", "equals": "1",
    }]
    if channel != 3:
        checks.insert(0, {
            "name": f"ch{channel}-vector-body", "kind": "register", "register": "PC",
            "equals": hex(context["probe_stop"]),
        })
    return {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": f"camry-execution-context-tauj0-ch{channel}-period",
        "entry": {
            "role": "p1me-byte-store-primitive", "scope": "resolved-address",
            "address": "0x78AE6",
        },
        "max_instructions": 2000 if channel in (1, 2) else 64,
        "stop_addresses": [hex(context["probe_stop"])],
        "gpr_fill": "0",
        "registers": registers,
        "memory": [
            {"address": "0xffe50090", "hex": "0000", "evidence": "Firmware writes TAUJ0TPS=0 and BRS=0."},
            {
                "address": hex(0xFFE50000 + channel * 4),
                "hex": struct.pack("<I", period_ticks - 1).hex(),
                "evidence": f"Firmware steady TAUJ0CDR{channel}=period-1.",
            },
            {
                "address": hex(context["eic_address"]),
                "hex": struct.pack("<H", context["eic_control"]).hex(),
                "evidence": f"Firmware startup EIC{context['eic_channel']} control.",
            },
        ],
        "checks": checks,
        "events": [{
            "kind": "clock", "after_instructions": 2, "p_bus_cycles": period_ticks + 2,
            "evidence": "Exact steady compare plus modeled start-load boundary.",
        }],
    }


def run_timer_probes(periods: dict[str, int]) -> dict[str, dict[str, Any]]:
    TRACE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "build/tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="camry-execution-contexts-", dir=REPO_ROOT / "build/tmp") as tmp:
        tmp_path = Path(tmp)
        scenario_paths: list[Path] = []
        for context in TIMER_CONTEXTS:
            scenario = timer_probe(context, periods[context["key"]])
            path = tmp_path / f"{context['key']}.json"
            path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
            scenario_paths.append(path)
        scenario_paths.append(FOREGROUND_STACK_SCENARIO)
        reports = capture_many(TARGET, scenario_paths, TRACE_OUTPUT_DIR, instruction_trace=True)
    timer_reports = reports[:len(TIMER_CONTEXTS)]
    foreground_report = reports[-1]
    if not foreground_report.get("passed"):
        raise ValueError(
            f"foreground stack probe failed: {foreground_report.get('termination_reason')}"
        )
    foreground_trace = foreground_report["instruction_trace"]
    foreground_start = next(
        index for index, row in enumerate(foreground_trace)
        if int(row["pc"], 16) == 0x66062
    )
    foreground_watermark = stack_watermark(
        foreground_trace[foreground_start:], IMAGE.read_bytes(), 0xFEBE7800,
        band=(0xFEBE7000, 0xFEBE7800),
    ).row()
    foreground_watermark.update({
        "status": "observed",
        "evidence_kind": "exact-image simulation from the native foreground PREPARE at 0x66062",
        "scenario": foreground_report["scenario"],
    })

    image = IMAGE.read_bytes()
    out: dict[str, dict[str, Any]] = {}
    for context, report in zip(TIMER_CONTEXTS, timer_reports, strict=True):
        if not report.get("passed"):
            raise ValueError(f"timer probe {context['key']} failed: {report.get('termination_reason')}")
        clocks = [event for event in report["device_events"] if event.get("kind") == "tauj-clock" and event.get("underflows") == 1]
        requests = [event for event in report["device_events"] if event.get("kind") == "interrupt-request"]
        if len(clocks) != 1 or len(requests) != 1:
            raise ValueError(f"timer probe {context['key']} did not produce exactly one underflow/request")
        trace_addresses = {int(row["pc"], 16) for row in report["instruction_trace"]}
        if context["timer_channel"] == 3:
            watermark = foreground_watermark
        else:
            trace = report["instruction_trace"]
            start = next(
                index for index, row in enumerate(trace)
                if int(row["pc"], 16) == context["vector_entry"]
            )
            watermark = stack_watermark(trace[start:], image, 0xFEBE2000).row()
            watermark.update({
                "status": "observed",
                "evidence_kind": "exact-image simulation from interrupt vector entry",
                "scenario": report["scenario"],
            })
        out[context["key"]] = {
            "scenario": report["scenario"],
            "evidence_kind": "exact-image simulation",
            "model_sha256": report["model_sha256"],
            "underflow_hsb_cycles": clocks[0]["hsb_cycles"],
            "underflows": clocks[0]["underflows"],
            "interrupt_request_channel": requests[0]["channel"],
            "scheduler_tick": requests[0]["scheduler_tick"],
            "vector_entry_observed": context["vector_entry"] in trace_addresses,
            "agreement": clocks[0]["hsb_cycles"] == periods[context["key"]],
            "stack_watermark": watermark,
            "note": "scheduler_tick marks the instruction boundary where the explicit clock event was applied; elapsed cadence is the modeled P-Bus cycle count",
        }
    return out


def capture_crosscheck() -> dict[str, Any]:
    artifact = json.loads(TX_ARTIFACT.read_text(encoding="utf-8"))
    rows = artifact["dynamic_observations"]["saved_log_positive_native_frames"]
    row = next(item for item in rows if item["address"] == "0x030")
    pdu = next(item for item in artifact["normal_messages"] if item["can_id"] == "0x030")
    intervals = row["count"] - 1
    observed_frame_ms = row["duration_s"] * 1000 / intervals
    inferred_foreground_ms = observed_frame_ms / pdu["cycle_ticks"]
    return {
        "evidence_kind": "observed in a retained capture; foreground period inferred from the firmware's two-activation PDU cycle",
        "source_artifact": str(TX_ARTIFACT.relative_to(REPO_ROOT)),
        "capture_source": row["path"],
        "can_id": row["address"],
        "frame_count": row["count"],
        "interval_count": intervals,
        "duration_s": row["duration_s"],
        "firmware_cycle_activations": pdu["cycle_ticks"],
        "observed_frame_period_ms": observed_frame_ms,
        "inferred_foreground_period_ms": inferred_foreground_ms,
        "firmware_foreground_period_ms": 5.0,
        "difference_percent": (inferred_foreground_ms - 5.0) / 5.0 * 100,
        "agreement": abs(inferred_foreground_ms - 5.0) <= 0.01,
    }


def load_receive_routes(symbols: dict[int, str]) -> tuple[list[dict[str, Any]], Counter[str]]:
    table_meta = json.loads(RX_TABLES.read_text(encoding="utf-8"))
    if table_meta["image_sha256"] != EXPECTED_IMAGE_SHA256:
        raise ValueError("receive-map image identity drifted")
    with RX_SIGNALS.open(encoding="utf-8", newline="") as stream:
        signal_rows = list(csv.DictReader(stream))
    by_pdu: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in signal_rows:
        by_pdu[int(row["com_pdu"])].append(row)
    classification_counts: Counter[str] = Counter(row["classification"] for row in signal_rows)

    routes: list[dict[str, Any]] = []
    with RX_MAP.open(encoding="utf-8", newline="") as stream:
        raw_routes = sorted(csv.DictReader(stream), key=lambda row: int(row["rule_index"]))
    for row in raw_routes:
        pdu_text = row["com_pdu_id"]
        sources: list[dict[str, Any]] = []
        if pdu_text.isdecimal():
            for signal in by_pdu[int(pdu_text)]:
                extracted = signal["extract_kind"] != "none"
                consumers = [int(value, 16) for value in signal["consumers"].split()]
                source: dict[str, Any] = {
                    "configured_signal_id": int(signal["signal_id"]),
                    "classification": signal["classification"],
                    "wire_field": signal["wire_field"] if extracted else None,
                    "bit_length": int(signal["bit_len"]) if extracted else None,
                    "destination": None,
                    "consumer_functions": [function_ref(address, symbols) for address in consumers],
                }
                if extracted:
                    source["destination"] = {
                        "address": signal["dest"], "width_bytes": int(signal["dest_width"]),
                        "object": f"COM signal {signal['signal_id']} destination",
                        "ram_path": signal["ram_path"] or None,
                    }
                sources.append(source)
        elif row["demux_class"].startswith("diagnostic"):
            sources.append({
                "configured_signal_id": None, "classification": "transport_payload",
                "wire_field": "B0..B7", "bit_length": 64,
                "destination": {"address": None, "width_bytes": 8, "object": "CanTp/DCM receive buffers", "ram_path": None},
                "consumer_functions": [function_ref(address, symbols) for address in (0x7A57A, 0x7A4E4, 0x921D2)],
            })
        else:
            sources.append({
                "configured_signal_id": None, "classification": "xcp_staging_payload",
                "wire_field": "B0..B7", "bit_length": 64,
                "destination": {"address": "0xFEBE4C34", "width_bytes": 64, "object": "XCP staging buffer", "ram_path": None},
                "consumer_functions": [function_ref(address, symbols) for address in (0x830C0, 0x98E80)],
            })
        routes.append({
            "receive_eic_channel": 187,
            "rule_index": int(row["rule_index"]),
            "rule_address": row["rule_address"],
            "can_id": row["can_id"],
            "id_format": row["id_format"],
            "label": row["gafl_label"],
            "fifo": row["rscfd_fifo"],
            "descriptor_length": int(row["canif_length"]),
            "demux_class": row["demux_class"],
            "acceptance_constraints": row["acceptance_constraints"],
            "destination_summary": row["memory_semantics"],
            "payload_sources": sources,
        })
    if len(routes) != 47 or len(signal_rows) != 225:
        raise ValueError("receive route/signal count drifted")
    return routes, classification_counts


def build() -> dict[str, Any]:
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("exact Camry CodeFlash identity drifted")
    symbols = load_symbols()
    function_starts = load_function_starts()
    calls = startup_calls(image, symbols)

    periods = {context["key"]: u32(image, context["compare_address"]) for context in TIMER_CONTEXTS}
    machine = run_timer_probes(periods)
    retained_capture = capture_crosscheck()

    foreground: list[dict[str, Any]] = []
    for context in TIMER_CONTEXTS:
        period = periods[context["key"]]
        offset = u32(image, context["initial_offset_address"])
        foreground.append({
            "context": context["key"],
            "timer": f"TAUJ0 channel {context['timer_channel']}",
            "clock": {"name": "P-Bus CK0", "frequency_hz": CLOCK_HZ, "TAUJ0TPS": 0, "TAUJ0CMOR": 0, "CKS": 0, "CCS": 0},
            "compare": {"constant_address": hx(context["compare_address"]), "period_ticks": period, "steady_CDR": period - 1, "initial_offset_ticks": offset, "initial_CDR": period + offset - 1},
            "period_ticks": period,
            "period_ms": period * 1000 / CLOCK_HZ,
            "initial_period_ms": (period + offset) * 1000 / CLOCK_HZ,
            "activation_entry": function_ref(context["vector_entry"] if context["timer_channel"] != 3 else context["task_entry"], symbols),
            "hardware_vector_entry": function_ref(context["vector_entry"], symbols),
            "hardware_vector_is_function_in_database": context["vector_entry"] in function_starts,
            "task_entry": function_ref(context["task_entry"], symbols),
            "activation": "unmasked EIINT" if context["timer_channel"] != 3 else "EIC136 EIRF polled and cleared by the foreground loop; EIMK remains set",
            "startup_calls": [
                {"number": 19, "call_site": hx(0x6383E), "address": hx(0x666BC), "effect": "initializes TAUJ0 TPS/CMOR and first compare values through 0x664F6 -> 0x6639C"},
                {"number": 21, "call_site": hx(0x63846), "address": hx(0x665F2), "effect": "loads steady CDR values before EI"},
            ],
            "role": context["role"],
            "writes": context["writes"],
            "consumed_by_contexts": context["consumed_by"],
            "machine_crosscheck": machine[context["key"]],
            "stack_watermark": machine[context["key"]]["stack_watermark"],
            "capture_crosscheck": retained_capture if context["key"] == "foreground" else {"status": "no retained capture reports an internal activation timestamp for this high-rate ISR"},
        })

    isrs: list[dict[str, Any]] = []
    coverage = json.loads(EXECUTION_COVERAGE.read_text(encoding="utf-8"))
    coverage_by_entry = {int(row["address"], 16): row for row in coverage["intbp_entries"]}
    timer_context_by_eic = {
        context["eic_channel"]: context["key"]
        for context in TIMER_CONTEXTS
        if context["timer_channel"] != 3
    }
    for channel, eic_address, control, entry, role, writes, consumers in ISR_ROWS:
        vector_word = u32(image, INTBP + channel * 4)
        if vector_word != entry:
            raise ValueError(f"INTBP[{channel}] drifted")
        coverage_row = coverage_by_entry.get(entry, {})
        isrs.append({
            "eic_channel": channel,
            "eic_address": hx(eic_address),
            "eic_control": hx(control, 4),
            "vector_index": channel,
            "vector_word_address": hx(INTBP + channel * 4),
            "entry": function_ref(entry, symbols),
            "is_function_in_database": entry in function_starts,
            "role": role,
            "writes": writes,
            "foreground_consumers": [function_ref(address, symbols) for address in consumers],
            "tracked_machine_execution_count": coverage_row.get("execution_count", 0),
            "tracked_machine_scenarios": coverage_row.get("scenario_ids", []),
            "stack_watermark": (
                machine[timer_context_by_eic[channel]]["stack_watermark"]
                if channel in timer_context_by_eic
                else {
                    "status": "not observed in the execution-context producer trace",
                    "finding_margin": STACK_FINDING_MARGIN,
                }
            ),
            "evidence_kind": "firmware EIC/INTBP tables and raw handler disassembly; tracked exact-image simulation count where nonzero",
        })

    receive_routes, receive_counts = load_receive_routes(symbols)
    extracted = sum(count for name, count in receive_counts.items() if name.startswith("extracted_"))
    return {
        "schema": "camry-8965f3307000-execution-contexts-v1",
        "target": TARGET,
        "image": {"path": str(IMAGE.relative_to(REPO_ROOT)), "sha256": EXPECTED_IMAGE_SHA256, "size": len(image)},
        "evidence_boundary": "Timer and EIC constants, vector words, startup calls, and receive tables are read from exact firmware. Timer underflow checks are exact-image simulation. The 0x030 cadence is observed in a retained capture; its foreground period is inferred using the firmware cycle count.",
        "startup": {
            "coordinator": function_ref(0x637EE, symbols),
            "startup_calls": calls,
            "after_calls": [
                {"call_site": hx(0x6384C), **function_ref(0x701EA, symbols), "argument": 0, "effect": "restore priority mask"},
                {"instruction": hx(0x63850), "effect": "EI"},
                {"call_site": hx(0x63854), **function_ref(0x66062, symbols), "effect": "enter foreground loop"},
            ],
        },
        "foreground_cycles": foreground,
        "isr_catalog": isrs,
        "receive_interrupts": [{
            "eic_channel": 187,
            "entry": function_ref(0x66100, symbols),
            "delegate_chain": [function_ref(address, symbols) for address in (0x66812, 0x83F30)],
            "stack_watermark": {
                "status": "not observed in the execution-context producer trace",
                "finding_margin": STACK_FINDING_MARGIN,
            },
            "routes": receive_routes,
        }],
        "crosschecks": {
            "timer_machine": {
                "p_bus_cycle_cadence_agreement": all(row["machine_crosscheck"]["agreement"] for row in foreground),
                "contexts": len(foreground),
                "scheduler_tick_cadence": {
                    "status": "not comparable to elapsed timer cadence",
                    "observed_request_ticks": [row["machine_crosscheck"]["scheduler_tick"] for row in foreground],
                    "reason": "each probe applies one explicit P-Bus clock event at scheduler tick 2; scheduler ticks order external events and are not elapsed-time units",
                },
            },
            "retained_capture": retained_capture,
        },
        "summary": {
            "startup_call_count": len(calls),
            "foreground_context_count": len(foreground),
            "enabled_isr_count": len(isrs),
            "isr_entries_missing_as_functions": sum(not row["is_function_in_database"] for row in isrs),
            "nondefault_eic_entries_missing_as_functions": (
                sum(not row["is_function_in_database"] for row in isrs)
                + int(0x62E1E not in function_starts)
            ),
            "receive_interrupt_count": 1,
            "receive_route_count": len(receive_routes),
            "configured_receive_signal_count": sum(receive_counts.values()),
            "extracted_receive_source_count": extracted,
            "stack_watermark_observed_contexts": sum(
                row["stack_watermark"]["status"] == "observed"
                for row in foreground
            ),
            "stack_watermark_findings": sum(
                bool(row["stack_watermark"].get("finding"))
                for row in foreground
            ),
            "receive_signal_classifications": dict(sorted(receive_counts.items())),
        },
        "search_methods": [
            {
                "claim": "The startup EIC initializer unmasks these nine channels.",
                "image": f"8965F3307000 CodeFlash SHA-256 {EXPECTED_IMAGE_SHA256}",
                "pattern": "stores to EIC control words with EIMK bit 7 clear in startup initializer 0x62E6A, followed by INTBP[channel] lookup",
                "tool": "tools/toyota decomp source 0x62e6a plus raw little-endian INTBP reads",
                "matches": 9,
                "true_positives": 9,
                "false_positives": 0,
                "exact_query": "tools/toyota decomp source 0x62e6a; select EIC stores whose written halfword & 0x0080 == 0; read u32(CodeFlash, 0x20200 + channel*4)",
            },
            {
                "claim": "Eight startup-enabled ISR entries are not functions; channel 8 and the masked/polled EIC136 vector are recovered functions.",
                "image": f"8965F3307000 CodeFlash SHA-256 {EXPECTED_IMAGE_SHA256}",
                "pattern": "exact INTBP targets for the nine startup-unmasked channels plus EIC136, joined to function-entry records",
                "tool": "data/targets/camry-8965F3307000/ghidra_project_inventory.baseline.jsonl",
                "matches": 10,
                "true_positives": 8,
                "false_positives": 2,
                "exact_query": "read u32(CodeFlash, 0x20200 + channel*4) for channels 8,133,134,135,136,187,188,292,293,379; exact-match each target against inventory records whose record == function",
            },
            {
                "claim": "Configured signal rows with no payload bit source retain the bounded no-extraction classification from the application-RX census.",
                "image": f"8965F3307000 CodeFlash SHA-256 {EXPECTED_IMAGE_SHA256}",
                "pattern": "configured RX signal-to-PDU rows joined to literal generated bitfield/group extraction call sites and table-driven extractor rows",
                "tool": "tools/targets/camry/analysis/analyze_camry_f33_application_rx_map.py",
                "matches": 95,
                "true_positives": 95,
                "false_positives": 0,
                "exact_query": "tools/artifact regen application_rx_signal_evidence.csv",
            },
        ],
        "variant_record": {
            "scope": "exact 2026 Camry Hybrid EPS 8965F3307000 CodeFlash",
            "why": "Execution-aware fuzzing and dataflow review need the real foreground and interrupt entry set rather than a single main function.",
            "cross_variant_evidence": "Sienna data/scheduler_periods.csv establishes the TAUJ constant-to-period convention. Addresses, EIC channels, timer constants, receive rules, and consumers here are decoded again from the exact Camry image; no Sienna address or signal mapping is transferred.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build()
    output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **result["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
