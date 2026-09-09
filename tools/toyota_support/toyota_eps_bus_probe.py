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


def execute_probe(plan: ProbePlan, timeout: float) -> list[dict[str, object]]:
    try:
        from panda import Panda
    except ImportError as error:
        raise RuntimeError("cannot import panda; run this on a comma/openpilot environment") from error

    uds_mod = _import_uds()
    panda = Panda()
    panda.set_safety_mode(plan.elm327_safety_mode, plan.elm327_param)

    results: list[dict[str, object]] = []
    for bus in plan.buses:
        result: dict[str, object] = {"bus": bus, "status": "no-response"}
        try:
            uds = uds_mod.UdsClient(
                panda,
                plan.tx_addr,
                plan.rx_addr,
                bus,
                timeout=timeout,
            )
            payload = uds.read_data_by_identifier(plan.did)
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
        "--execute",
        action="store_true",
        help="perform the read-only F181 probes; without this flag only print the plan",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    buses = tuple(dict.fromkeys(args.buses or DEFAULT_BUSES))
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
            "changes which GPIO/transceiver implements that semantic path, not the logical bus."
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
    }
    if args.execute:
        output["results"] = execute_probe(plan, args.timeout)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
