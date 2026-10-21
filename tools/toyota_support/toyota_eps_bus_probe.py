#!/usr/bin/env python3
"""Non-destructive Toyota EPS diagnostic-bus discovery helper.

The default mode is a dry-run plan. ``--execute`` performs only ReadDataByIdentifier
0xF181 (Application Software Identification) against 0x7A1 -> 0x7A9 on the
selected Panda logical buses. It does not enter extended/programming sessions,
request SecurityAccess, write DIDs, download code, or change ECU state.

The default ELM327 safety parameter is 1, which the pinned Panda firmware treats
as normal CAN routing. Parameter 0 selects ``CAN_MODE_OBD_CAN2`` and multiplexes
logical bus 1 to the OBD-II CAN pair; use it only when that physical route is
intentionally desired.
"""

from __future__ import annotations

import argparse
import importlib
import json
from dataclasses import dataclass, asdict
from typing import Any

TX_ADDR = 0x7A1
RX_ADDR = 0x7A9
APPLICATION_SOFTWARE_ID_DID = 0xF181
ELM327_SAFETY_MODE = 3
DEFAULT_ELM327_PARAM = 1  # nonzero -> CAN_MODE_NORMAL in pinned Panda firmware
DEFAULT_BUSES = (0, 1, 2)
OPEN_RELAY_BUSES = (0, 2)
ALLOUTPUT_SAFETY_MODE = 17
ALLOUTPUT_PASSTHROUGH_PARAM = 1
TOYOTA_B_REPIN_CANDIDATE_BUS = 1


@dataclass(frozen=True)
class Fdcan2Route:
    """Pinned Cuatro/Tres FDCAN2 physical-route model.

    Panda logical bus 1 always targets MCU FDCAN2.  The ELM327 safety parameter
    selects NORMAL versus OBD_CAN2 board mode; detected harness orientation then
    decides which FDCAN2 GPIO bank/transceiver implements that semantic route.
    """

    elm327_param: int
    harness_flipped: bool
    logical_bus: int
    mcu_controller: str
    can_mode: str
    semantic_path: str
    gpio_pair: str
    transceiver: int


@dataclass(frozen=True)
class ProbePlan:
    tx_addr: int
    rx_addr: int
    did: int
    buses: tuple[int, ...]
    elm327_safety_mode: int
    elm327_param: int
    mutating_services: tuple[str, ...] = ()


def fdcan2_route(elm327_param: int, harness_flipped: bool) -> Fdcan2Route:
    """Model ``tres_set_can_mode`` as inherited by comma 4/Cuatro."""
    if not 0 <= elm327_param <= 0xFFFF:
        raise ValueError("ELM327 safety parameter must fit uint16")

    normal_mode = elm327_param != 0
    use_pb5_pb6 = normal_mode != harness_flipped
    return Fdcan2Route(
        elm327_param=elm327_param,
        harness_flipped=harness_flipped,
        logical_bus=1,
        mcu_controller="FDCAN2",
        can_mode="CAN_MODE_NORMAL" if normal_mode else "CAN_MODE_OBD_CAN2",
        semantic_path="normal-harness" if normal_mode else "obd",
        gpio_pair="PB5/PB6" if use_pb5_pb6 else "PB12/PB13",
        transceiver=2 if use_pb5_pb6 else 4,
    )


def build_plan(buses: tuple[int, ...], elm327_param: int) -> ProbePlan:
    if not buses:
        raise ValueError("at least one bus is required")
    if any(bus not in (0, 1, 2) for bus in buses):
        raise ValueError("Panda logical bus must be 0, 1, or 2")
    if not 0 <= elm327_param <= 0xFFFF:
        raise ValueError("ELM327 safety parameter must fit uint16")
    return ProbePlan(
        tx_addr=TX_ADDR,
        rx_addr=RX_ADDR,
        did=APPLICATION_SOFTWARE_ID_DID,
        buses=buses,
        elm327_safety_mode=ELM327_SAFETY_MODE,
        elm327_param=elm327_param,
    )


def _import_uds() -> Any:
    for module_name in ("opendbc.car.uds", "panda.python.uds", "panda.uds"):
        try:
            return importlib.import_module(module_name)
        except ImportError:
            continue
    raise RuntimeError("cannot import a supported UDS module")


def _probe_buses(panda: Any, uds_mod: Any, buses: tuple[int, ...], timeout: float) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for bus in buses:
        result: dict[str, object] = {"bus": bus, "status": "no-response"}
        try:
            panda.can_clear(0xFFFF)
            uds = uds_mod.UdsClient(
                panda,
                TX_ADDR,
                RX_ADDR,
                bus,
                timeout=timeout,
            )
            payload = uds.read_data_by_identifier(APPLICATION_SOFTWARE_ID_DID)
        except Exception as error:  # execution helper must record each bus independently.
            result["error"] = f"{type(error).__name__}: {error}"
        else:
            result["status"] = "response"
            result["f181_hex"] = bytes(payload).hex()
            try:
                text = bytes(payload).rstrip(b"\x00").decode("ascii")
            except UnicodeDecodeError:
                text = ""
            if text:
                result["f181_ascii"] = text
        results.append(result)
    return results


def execute_probe(plan: ProbePlan, timeout: float) -> list[dict[str, object]]:
    try:
        from panda import Panda
    except ImportError as error:
        raise RuntimeError("cannot import panda; run this on a comma/openpilot environment") from error

    uds_mod = _import_uds()
    panda = Panda()
    try:
        panda.set_safety_mode(plan.elm327_safety_mode, plan.elm327_param)
        return _probe_buses(panda, uds_mod, plan.buses, timeout)
    finally:
        panda.close()


def execute_open_relay_probe(buses: tuple[int, ...], timeout: float) -> dict[str, object]:
    """Identify the EPS side of the CAN0/CAN2 intercept pair without mutating the ECU.

    allOutput parameter 1 opens the harness relay while preserving software
    forwarding. Host-originated frames are not forwarding inputs, so an F181
    request sent on one logical bus reaches only that physical relay side.
    """
    try:
        from panda import Panda
    except ImportError as error:
        raise RuntimeError("cannot import panda; run this on a comma/openpilot environment") from error

    uds_mod = _import_uds()
    panda = Panda()
    try:
        for bus in OPEN_RELAY_BUSES:
            panda.set_canfd_auto(bus, False)
        panda.set_safety_mode(ALLOUTPUT_SAFETY_MODE, ALLOUTPUT_PASSTHROUGH_PARAM)
        health = panda.health()
        if (
            int(health.get("safety_mode", -1)) != ALLOUTPUT_SAFETY_MODE
            or int(health.get("safety_param", -1)) != ALLOUTPUT_PASSTHROUGH_PARAM
        ):
            raise RuntimeError(
                "Panda did not enter allOutput passthrough; "
                f"observed safety_mode={health.get('safety_mode')} safety_param={health.get('safety_param')}"
            )
        return {
            "health": {
                key: health.get(key)
                for key in ("safety_mode", "safety_param", "car_harness_status", "spi_error_count", "safety_tx_blocked")
            },
            "results": _probe_buses(panda, uds_mod, buses, timeout),
        }
    finally:
        # Restore the physical relay bypass before releasing a direct-Panda
        # handle. Panda() disables heartbeat checks, so handle close alone does
        # not guarantee an automatic return to a non-intercepting mode.
        try:
            panda.set_safety_mode(ELM327_SAFETY_MODE, DEFAULT_ELM327_PARAM)
        finally:
            panda.close()


def parse_bus(value: str) -> int:
    try:
        bus = int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid bus: {value}") from error
    if bus not in (0, 1, 2):
        raise argparse.ArgumentTypeError("bus must be 0, 1, or 2")
    return bus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bus",
        action="append",
        type=parse_bus,
        dest="buses",
        help="logical Panda bus to probe; repeatable; defaults to 0,1,2",
    )
    parser.add_argument(
        "--elm327-param",
        type=lambda value: int(value, 0),
        default=DEFAULT_ELM327_PARAM,
        help="ELM327 safety parameter (default 1 = normal CAN routing; 0 = OBD CAN2 mux)",
    )
    parser.add_argument("--timeout", type=float, default=0.25)
    parser.add_argument(
        "--open-relay",
        action="store_true",
        help=(
            "open the CAN0/CAN2 intercept relay with allOutput passthrough and probe F181 on the selected side(s); "
            "requires a debug/ALLOW_DEBUG Panda and defaults to buses 0 and 2"
        ),
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="perform the read-only F181 probes; without this flag only print the plan",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    buses = tuple(dict.fromkeys(args.buses or (OPEN_RELAY_BUSES if args.open_relay else DEFAULT_BUSES)))
    if args.open_relay and any(bus not in OPEN_RELAY_BUSES for bus in buses):
        raise SystemExit("--open-relay probes only logical buses 0 and 2")
    try:
        plan = build_plan(buses, args.elm327_param)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    output: dict[str, object] = {
        "plan": asdict(plan),
        "fdcan2_routes": [
            asdict(fdcan2_route(plan.elm327_param, harness_flipped=False)),
            asdict(fdcan2_route(plan.elm327_param, harness_flipped=True)),
        ],
        "routing_note": (
            "elm327_param=0 selects the OBD physical path for logical bus 1/FDCAN2; "
            "nonzero selects the normal-harness physical path. Harness orientation "
            "changes which GPIO/transceiver implements that semantic path while preserving the logical bus."
        ),
        "toyota_b_repin_candidate": {
            "elm327_param": 1,
            "bus": TOYOTA_B_REPIN_CANDIDATE_BUS,
            "scope": "direct-diagnostic-route",
            "relay_topology_equivalent": False,
            "status": (
                "static direct-diagnostic-route candidate; not equivalent to moving the vehicle "
                "network onto the CAN0/CAN2 intercept-relay pair; programming-transition confirmation required"
            ),
        },
        "mode": "execute" if args.execute else "dry-run",
        "relay": {
            "state": "open-software-passthrough" if args.open_relay else "closed-bypass",
            "safety_mode": ALLOUTPUT_SAFETY_MODE if args.open_relay else ELM327_SAFETY_MODE,
            "safety_param": ALLOUTPUT_PASSTHROUGH_PARAM if args.open_relay else plan.elm327_param,
        },
    }
    if args.execute:
        if args.open_relay:
            output["open_relay_probe"] = execute_open_relay_probe(plan.buses, args.timeout)
        else:
            output["results"] = execute_probe(plan, args.timeout)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
