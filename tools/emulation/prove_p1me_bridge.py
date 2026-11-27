#!/usr/bin/env python3
"""Prove UDS, SecurityAccess reset, and capture parity through the P1M-E bus."""
from __future__ import annotations

import argparse
import importlib
import json
import time
from pathlib import Path
from typing import Any, cast

from tools import REPO_ROOT
from tools.emulation.p1me_can_bridge import P1MEMachineBus
from tools.emulation.p1me_machine import capture_many
from tools.targets.camry.research import replay_camry_f33_capture_machine as replay

TX_ID = 0x7A1
RX_ID = 0x7A9
CAPTURE = REPO_ROOT / "build/out/camry_capture_replay/camry_ready_gear_20260826.scenario.json"
# The payload of this frame changes twice in the capture, at 17.5 s and 21.1 s.
GEAR_FRAME = 0x0D5
WINDOW_PERIODS = 100
COM_SNAPSHOT_ADDRESS = 0xFEBE8000
COM_SNAPSHOT_SIZE = 0xB0
MODE_CELLS = (
    ("live_mode", 0xFEBEB11A, 2),
    ("desired_mode", 0xFEBEE8CC, 4),
    ("active_mode", 0xFEBE8C06, 2),
)
SECURITY_CELLS = (
    ("attempt", 0xFEBE5DD0, 1),
    ("delay", 0xFEBE5DC8, 4),
    ("seed_ram", 0xFEBF495A, 16),
)
DELAY_MASK_ADDRESS = 0xFEBE5DC8
DELAY_TIMER_ADDRESS = 0xFEBE5EB4
LOCKOUT_TICKS = 10_004
CLEARED_SECURITY_STATE = {
    "attempt": "00",
    "delay": "03000000",
    "seed_ram": "00000000000000000000000000000000",
    "live_mode": "0207",
    "desired_mode": "02070000",
    "active_mode": "0207",
}
SCENARIO_RESPONSES = {
    "10 03": "5003003201f4",
    "22 F181": "62f181023839363546333330373030300000000038413331313333303331303000000000",
    "27 03": "6703bdcd5f4dce052555b348eebfa98c278c",
    "3E 00": "7e00",
}


def _is_positive_seed(response: str) -> bool:
    return len(response) == 36 and response.startswith("6703")


def _require_client() -> tuple[Any, ...]:
    try:
        isotp = importlib.import_module("isotp")
        Client = importlib.import_module("udsoncan.client").Client
        default_client_config = importlib.import_module(
            "udsoncan.configs",
        ).default_client_config
        PythonIsoTpConnection = importlib.import_module(
            "udsoncan.connections",
        ).PythonIsoTpConnection
        services = importlib.import_module("udsoncan.services")
        DiagnosticSessionControl = services.DiagnosticSessionControl
        ReadDataByIdentifier = services.ReadDataByIdentifier
        SecurityAccess = services.SecurityAccess
        TesterPresent = services.TesterPresent
        NegativeResponseException = importlib.import_module(
            "udsoncan.exceptions",
        ).NegativeResponseException
    except ImportError as exc:
        raise SystemExit(
            "run with: uv run --locked --with python-can --with can-isotp --with udsoncan "
            "python -m tools.emulation.prove_p1me_bridge"
        ) from exc
    return (
        isotp,
        Client,
        default_client_config,
        PythonIsoTpConnection,
        DiagnosticSessionControl,
        ReadDataByIdentifier,
        SecurityAccess,
        TesterPresent,
        NegativeResponseException,
    )


def _open_client(bus: Any, timeout: float) -> Any:
    """Open an udsoncan client over python-can ISO-TP on the diagnostic pair."""
    isotp, Client, default_client_config, PythonIsoTpConnection, *_ = _require_client()
    stack = isotp.CanStack(
        bus=bus,
        address=isotp.Address(
            isotp.AddressingMode.Normal_11bits, txid=TX_ID, rxid=RX_ID,
        ),
        params={
            "blocksize": 0,
            "stmin": 0,
            "tx_data_length": 8,
            "tx_padding": 0,
            "rx_flowcontrol_timeout": int(timeout * 1000),
            "rx_consecutive_frame_timeout": int(timeout * 1000),
        },
    )
    config = dict(default_client_config)
    config.update({
        "request_timeout": timeout,
        "p2_timeout": timeout,
        "p2_star_timeout": timeout,
    })
    return Client(PythonIsoTpConnection(stack), config=config)


def _capture_window(source: dict[str, Any]) -> list[Any]:
    """Return the periods of steady traffic before the gear frame first changes."""
    periods = replay.capture_periods(source)
    previous = None
    for period in periods:
        for row in period.receive:
            if int(row["can_id"], 16) != GEAR_FRAME:
                continue
            if previous is not None and row["data_hex"] != previous:
                return periods[period.index - WINDOW_PERIODS:period.index]
            previous = row["data_hex"]
    raise RuntimeError("the capture holds no gear-frame payload change")


def _snapshot_ranges() -> tuple[tuple[str, int, int], ...]:
    return (
        ("com-signal-destinations", COM_SNAPSHOT_ADDRESS, COM_SNAPSHOT_SIZE),
        *((f"mode-{address:08x}", address, size) for _, address, size in MODE_CELLS),
    )


def _read_snapshot(bus: Any, timeout: float) -> dict[str, str]:
    return {
        name: bus.read_memory(address, size, timeout=timeout).hex()
        for name, address, size in _snapshot_ranges()
    }


def _snapshot_map(report: dict[str, Any]) -> dict[str, str]:
    return {
        Path(row["path"]).stem: Path(row["path"]).read_bytes().hex()
        for row in report["snapshot_outputs"]
    }


def _differences(harness: dict[str, str], bridge: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in harness:
        left = bytes.fromhex(harness[name])
        right = bytes.fromhex(bridge[name])
        rows.extend(
            {"range": name, "offset": hex(index), "harness": left[index], "bridge": right[index]}
            for index in range(len(left)) if left[index] != right[index]
        )
    return rows


def _run_scenario(output_dir: Path, scenario: dict[str, Any], name: str) -> dict[str, Any]:
    scenario["snapshot_outputs"] = [
        {
            "path": str(output_dir / name / f"{range_name}.bin"),
            "address": hex(address),
            "size": size,
            "evidence": "Scenario-driven reference for the python-can bridge proof",
        }
        for range_name, address, size in _snapshot_ranges()
    ]
    scenario_path = output_dir / f"{name}.scenario.json"
    scenario_path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    return capture_many(replay.TARGET, [scenario_path], output_dir / name)[0]


def _bus_timed_replay(
    output_dir: Path, source: dict[str, Any], frames: list[dict[str, Any]],
    transmits: list[dict[str, Any]], ready_instruction: int, cycles: int,
) -> dict[str, Any]:
    """Run the scenario harness with the bus's events at the bus's instructions."""
    scenario = replay.build_replay_scenario(source, [], "camry-f33-bridge-gear-twin")
    # The harness reaches its checkpoint at the foreground wait, one instruction
    # past the completed-cycle branch where the bus run starts.
    base = ready_instruction + 1
    events: list[dict[str, Any]] = []
    for row in frames:
        event: dict[str, Any] = {
            "kind": "can-rx",
            "fifo": row["fifo"],
            "boundary": row["boundary"],
            "can_id": row["can_id"],
            "data_hex": row["data_hex"],
            "label": row["label"],
            "after_instructions": row["scheduler_tick"] - base,
            "evidence": "Instruction tick at which the python-can bus delivered this frame",
        }
        for flag in ("extended", "fd"):
            if row.get(flag):
                event[flag] = True
        events.append(event)
    for row in transmits:
        events.append({
            "kind": "can-tx-complete",
            "buffer": row["buffer"],
            "after_instructions": row["completed_instruction"] - base,
            "evidence": "Instruction tick at which the python-can bus completed this transmit",
        })
    scenario["steps"].append({
        "kind": "trial",
        "name": "bus-capture-window",
        "max_instructions": scenario["max_instructions"],
        "stop_addresses": [],
        "stop_after_arrivals": [{"address": hex(replay.FOREGROUND_COMPLETE), "count": cycles}],
        "events": events,
        "checks": [],
    })
    report = _run_scenario(output_dir, scenario, "gear-twin")
    device = report["device_events"]
    return {
        "snapshot": _snapshot_map(report),
        "boundary": report["instruction_count"],
        "frame_ticks_equal": [row["scheduler_tick"] for row in device if row["kind"] == "can-rx"]
        == [row["scheduler_tick"] for row in frames],
    }


def _advance_level2_delay(
    client: Any, bus: Any, timeout: float, ticks: int = LOCKOUT_TICKS,
) -> dict[str, Any]:
    """Run foreground cycles until the firmware drops the level-2 delay bit."""
    # The firmware counts the delay in 1 ms ticks: five per 5 ms foreground period.
    # A TesterPresent every 500 cycles keeps the non-default session from lapsing.
    foreground_cycles = 0
    while int.from_bytes(bus.read_memory(DELAY_MASK_ADDRESS, 4, timeout), "little") & 2:
        if foreground_cycles > ticks // 5 + 20:
            raise TimeoutError(f"level-2 delay remained active after {ticks} firmware ticks")
        if foreground_cycles % 250 == 0:
            print(f"level-2 delay: {foreground_cycles} foreground cycles", flush=True)
        if foreground_cycles % 500 == 0:
            response = client.send_request(_require_client()[7].make_request())
            if bytes(response.original_payload) != bytes.fromhex(SCENARIO_RESPONSES["3E 00"]):
                raise RuntimeError(
                    f"TesterPresent answered {bytes(response.original_payload).hex()}",
                )
        bus.wait_foreground_cycles(1, timeout=timeout)
        foreground_cycles += 1
    return {
        "firmware_ticks": ticks,
        "foreground_cycles_waited": foreground_cycles,
    }


def _standard_client(client: Any, bus: Any, timeout: float) -> dict[str, Any]:
    *_, DiagnosticSessionControl, ReadDataByIdentifier, SecurityAccess, TesterPresent, NegativeResponseException = (
        _require_client()
    )
    requests = (
        ("10 03", DiagnosticSessionControl.make_request(3)),
        ("22 F181", ReadDataByIdentifier.make_request(0xF181, None)),
        (
            "27 03",
            SecurityAccess.make_request(
                3, SecurityAccess.Mode.RequestSeed, data=b"\x00" * 16,
            ),
        ),
        ("3E 00", TesterPresent.make_request()),
    )
    observed: dict[str, str] = {}
    elapsed: dict[str, float] = {}
    startup_delay: dict[str, Any] = {}
    for index, (name, request) in enumerate(requests):
        if name == "27 03":
            # Every boot rearms the level-2 startup delay; a seed is refused until it lapses.
            startup_delay = _advance_level2_delay(client, bus, timeout)
        print(f"UDS request {name}", flush=True)
        started = time.monotonic()
        try:
            response = client.send_request(request)
        except NegativeResponseException as refused:
            response = refused.response
        elapsed[name] = time.monotonic() - started
        observed[name] = bytes(response.original_payload).hex()
        print(f"UDS response {name}: {observed[name]}", flush=True)
        if index + 1 < len(requests):
            bus.wait_foreground_cycles(2, timeout=max(timeout, 120.0))
    seed = observed["27 03"]
    return {
        "responses": observed,
        "scenario_responses": SCENARIO_RESPONSES,
        "equal": (
            _is_positive_seed(seed)
            and all(
                observed[name] == response
                for name, response in SCENARIO_RESPONSES.items()
                if name != "27 03"
            )
        ),
        "seed": seed[4:] if _is_positive_seed(seed) else None,
        "seed_matches_retained_scenario": seed == SCENARIO_RESPONSES["27 03"],
        "elapsed_seconds": elapsed,
        "startup_delay": startup_delay,
    }


def _security_exchange(
    client: Any, bus: Any, timeout: float, actions: tuple[str, ...],
) -> list[dict[str, Any]]:
    *_, DiagnosticSessionControl, _ReadDataByIdentifier, SecurityAccess, _TesterPresent, NegativeResponseException = (
        _require_client()
    )
    requests = {
        "session": lambda: DiagnosticSessionControl.make_request(3),
        "seed": lambda: SecurityAccess.make_request(
            3, SecurityAccess.Mode.RequestSeed, data=b"\x00" * 16,
        ),
        "zero-key": lambda: SecurityAccess.make_request(
            4, SecurityAccess.Mode.SendKey, data=b"\x00" * 16,
        ),
    }
    rows: list[dict[str, Any]] = []
    for action in actions:
        try:
            response = client.send_request(requests[action]())
        # This udsoncan raises every negative response except 0x78.
        except NegativeResponseException as refused:
            response = refused.response
        payload = bytes(response.original_payload)
        rows.append({
            "action": action,
            "response": payload.hex(),
            "positive": bool(response.positive),
            "seed": payload[2:].hex()
            if response.positive and payload[:2] == b"\x67\x03"
            else None,
        })
        bus.wait_foreground_cycles(2, timeout=timeout)
    return rows


def _security_reset_proof(
    client: Any, bus: Any, timeout: float, reset_count: int,
) -> dict[str, Any]:
    pre_reset = _security_exchange(client, bus, timeout, ("zero-key", "seed", "zero-key", "seed"))
    timer_remaining_before_wait = int.from_bytes(
        bus.read_memory(DELAY_TIMER_ADDRESS, 4, timeout), "little",
    )
    expiry = _advance_level2_delay(client, bus, timeout)
    after_delay = _security_exchange(client, bus, timeout, ("seed",))
    resets: list[dict[str, Any]] = []
    for reset_index in range(reset_count):
        reset = bus.reset(timeout=max(timeout, 600.0))
        before = {
            name: bus.read_memory(address, size, timeout).hex()
            for name, address, size in (*SECURITY_CELLS, *MODE_CELLS)
        }
        delayed = _security_exchange(client, bus, timeout, ("session", "seed"))
        startup_delay = _advance_level2_delay(client, bus, timeout)
        actions = ("seed", "zero-key", "seed", "zero-key") if reset_index == 0 else (
            "seed",
        )
        resets.append({
            "index": reset_index + 1,
            "reset": reset,
            "before_requests": before,
            "startup_delay": startup_delay,
            "delayed_exchange": delayed,
            "exchange": _security_exchange(client, bus, timeout, actions),
        })
    seeds_by_reset = [
        [
            row["seed"] for row in reset["exchange"]
            if row["action"] == "seed" and row["seed"] is not None
        ]
        for reset in resets
    ]
    seeds = [seed for reset_seeds in seeds_by_reset for seed in reset_seeds]
    pre_reset_seeds = [
        row["seed"] for row in pre_reset if row["seed"] is not None
    ]
    expected_seed_count = reset_count + 1
    return {
        "pre_reset": pre_reset,
        "reset_count": reset_count,
        "pre_reset_seeds": pre_reset_seeds,
        "lockout": {
            "configured_ticks": LOCKOUT_TICKS,
            "remaining_before_wait": timer_remaining_before_wait,
            "ticks_elapsed_before_wait": LOCKOUT_TICKS - timer_remaining_before_wait,
            **expiry,
            "seed_response": after_delay[0]["response"],
            "seed": after_delay[0]["seed"],
            "accepted": after_delay[0]["positive"],
        },
        "resets": resets,
        "post_reset_seeds_by_reset": seeds_by_reset,
        "all_post_reset_seeds_equal": (
            len(seeds) == expected_seed_count and len(set(seeds)) == 1
        ),
        "all_post_reset_seeds_match_pre_reset": (
            len(seeds) == expected_seed_count
            and len(pre_reset_seeds) == 1
            and all(seed == pre_reset_seeds[0] for seed in seeds)
        ),
    }


def _bridge_replay(
    bus: Any, periods: list[Any], timeout: float,
) -> tuple[dict[str, str], list[dict[str, Any]], list[dict[str, Any]], int]:
    """Deliver each period at its held arrival, then run its foreground cycle.

    Returns the snapshot, the accepted frames and the firmware transmits with their
    instruction ticks, and the last cycle boundary. The machine remains held there
    until the caller resumes it.
    """
    can = importlib.import_module("can")

    if not bus._held:
        raise RuntimeError("gear replay requires a machine held at its readiness boundary")
    first_row = len(bus.receive_rows)
    first_transmit = len(bus.transmit_rows)
    for period in periods:
        for row in period.receive:
            data = bytes.fromhex(row["data_hex"])
            bus.send(can.Message(
                arbitration_id=int(row["can_id"], 0),
                data=data,
                is_extended_id=False,
                is_fd=len(data) > 8,
                bitrate_switch=False,
            ))
        bus.resume(timeout=timeout)
        boundary = bus.wait_foreground_cycles(1, timeout=timeout, hold=True)[-1]["instruction"]
    return (
        _read_snapshot(bus, timeout),
        [row for row in bus.receive_rows[first_row:] if row["kind"] == "can-rx"],
        [row for row in bus.transmit_rows[first_transmit:] if row["kind"] == "can-tx"],
        boundary,
    )


def _security_verdict(security: dict[str, Any]) -> bool:
    resets = security["resets"]
    pre_reset = security["pre_reset"]
    if not resets or len(pre_reset) != 4:
        return False
    first_reset_exchange = resets[0]["exchange"]
    later_reset_exchanges = [reset["exchange"] for reset in resets[1:]]
    if len(first_reset_exchange) != 4:
        return False
    lockout = security["lockout"]
    elapsed = lockout["ticks_elapsed_before_wait"]
    return (
        pre_reset[0]["response"] == "7f2735"
        and _is_positive_seed(pre_reset[1]["response"])
        and pre_reset[2]["response"] == "7f2736"
        and pre_reset[3]["response"] == "7f2737"
        and lockout["configured_ticks"] == LOCKOUT_TICKS
        and 0 <= elapsed <= 100
        and lockout["remaining_before_wait"] == LOCKOUT_TICKS - elapsed
        and lockout["accepted"]
        and _is_positive_seed(lockout["seed_response"])
        and all(reset["before_requests"] == CLEARED_SECURITY_STATE for reset in resets)
        and all(
            [row["response"] for row in reset["delayed_exchange"]]
            == [SCENARIO_RESPONSES["10 03"], "7f2737"]
            for reset in resets
        )
        and _is_positive_seed(first_reset_exchange[0]["response"])
        and first_reset_exchange[1]["response"] == "7f2735"
        and _is_positive_seed(first_reset_exchange[2]["response"])
        and first_reset_exchange[3]["response"] == "7f2736"
        and all(
            len(exchange) == 1 and _is_positive_seed(exchange[0]["response"])
            for exchange in later_reset_exchanges
        )
        and all(
            1_800 <= waited <= LOCKOUT_TICKS // 5 + 20
            for waited in (
                lockout["foreground_cycles_waited"],
                *(reset["startup_delay"]["foreground_cycles_waited"] for reset in resets),
            )
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "build/out/p1me-bridge-proof")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--timing-cycles", type=int, default=12)
    parser.add_argument(
        "--reset-count", type=int, choices=(1, 3), default=1,
        help="RESET-pin boots to prove; use 3 for the full seed-comparison soak",
    )
    args = parser.parse_args()
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    source = replay.load_capture_scenario(CAPTURE)
    periods = _capture_window(source)
    Bus = cast(Any, P1MEMachineBus)
    with Bus(
        output_dir=args.output_dir / "gear-bridge",
        startup_timeout=max(args.timeout, 600.0),
        start_held=True,
    ) as bus:
        ready_instruction = bus.ready_instruction
        bridge_snapshot, frames, transmits, boundary = _bridge_replay(bus, periods, args.timeout)
        bus.resume()
    twin = _bus_timed_replay(
        args.output_dir, source, frames, transmits, ready_instruction, len(periods),
    )
    waited = _snapshot_map(_run_scenario(
        args.output_dir,
        replay.build_replay_scenario(
            source, periods, "camry-f33-bridge-gear-foreground-wait", checks=(),
        ),
        "gear-foreground-wait",
    ))
    with Bus(
        output_dir=args.output_dir / "bridge",
        startup_timeout=max(args.timeout, 600.0),
    ) as bus:
        started = time.monotonic()
        bus.wait_foreground_cycles(args.timing_cycles, timeout=args.timeout)
        timing_wall = time.monotonic() - started
        with _open_client(bus, args.timeout) as client:
            uds = _standard_client(client, bus, args.timeout)
            security = _security_reset_proof(client, bus, args.timeout, args.reset_count)
    security_ok = _security_verdict(security)
    result = {
        "schema": "p1me-python-can-bridge-proof-v1",
        "engine": "jit",
        "timing": {
            "foreground_cycles": args.timing_cycles,
            "firmware_seconds": args.timing_cycles * 0.005,
            "wall_seconds": timing_wall,
            "slower_than_real_time": timing_wall / (args.timing_cycles * 0.005),
        },
        "standard_uds": uds,
        "security_reset": security,
        "security_ok": security_ok,
        "gear_replay": {
            "first_period": periods[0].index,
            "period_count": len(periods),
            "receive_frames": len(frames),
            "bus_boundary": boundary,
            "harness_boundary": twin["boundary"],
            "boundaries_equal": twin["boundary"] == boundary,
            "frame_ticks_equal": twin["frame_ticks_equal"],
            "firmware_transmits": len(transmits),
            "harness_snapshot": twin["snapshot"],
            "bridge_snapshot": bridge_snapshot,
            "equal": twin["snapshot"] == bridge_snapshot,
            # The retained harness queues a period's frames at the foreground wait
            # instead of on the bus; the firmware's receive status flags track that.
            "foreground_wait_harness_differences": _differences(waited, bridge_snapshot),
        },
    }
    output_path = args.output_dir / "proof.json"
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    gear_ok = (
        result["gear_replay"]["equal"]
        and result["gear_replay"]["boundaries_equal"]
        and result["gear_replay"]["frame_ticks_equal"]
    )
    return 0 if result["standard_uds"]["equal"] and gear_ok and security_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
