#!/usr/bin/env python3
"""Read EPS software identity around an explicit power-cycle boundary."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.project.analysis_target import target as resolve_target

TARGET = "camry-8965F3307000"
TX_ID = 0x7A1
RX_ID = 0x7A9
IDENTITY_DIDS = (0xF181, 0xF189)
BRIDGE_IDENTITY_DIDS = (0xF181,)


def _record(transport: str, bus: int | str, values: dict[int, bytes]) -> dict[str, Any]:
    name, reference = resolve_target(TARGET)
    return {
        "schema": "toyota-eps-software-identity-v2",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "transport": transport,
        "bus": bus,
        "reference_image": {
            "target": name,
            "software_id": reference["software_id"],
            "codeflash_sha256": reference["codeflash_sha256"],
        },
        "dids": {f"0x{did:04X}": value.hex() for did, value in values.items()},
    }


def _read_isotp(bus: Any, did: int, timeout: float) -> bytes:
    import can

    request = bytes((3, 0x22, did >> 8, did & 0xFF, 0, 0, 0, 0))
    bus.send(can.Message(arbitration_id=TX_ID, data=request, is_extended_id=False))
    first = bus.recv(timeout)
    if first is None or first.arbitration_id != RX_ID:
        raise TimeoutError(f"no 0x{RX_ID:03X} response for DID 0x{did:04X}")
    payload = bytes(first.data)
    pci = payload[0] >> 4
    if pci == 0:
        response = payload[1:1 + (payload[0] & 0x0F)]
    elif pci == 1:
        length = ((payload[0] & 0x0F) << 8) | payload[1]
        response = bytearray(payload[2:])
        bus.send(can.Message(
            arbitration_id=TX_ID,
            data=bytes((0x30, 0, 0, 0, 0, 0, 0, 0)),
            is_extended_id=False,
        ))
        sequence = 1
        while len(response) < length:
            frame = bus.recv(timeout)
            if frame is None or frame.arbitration_id != RX_ID:
                raise TimeoutError(f"incomplete DID 0x{did:04X} response")
            data = bytes(frame.data)
            if data[0] >> 4 != 2 or data[0] & 0x0F != sequence & 0x0F:
                raise RuntimeError(f"invalid ISO-TP consecutive frame for DID 0x{did:04X}")
            response.extend(data[1:])
            sequence += 1
        response = bytes(response[:length])
    else:
        raise RuntimeError(f"unsupported ISO-TP PCI 0x{payload[0]:02X}")
    if response[:1] == b"\x7f":
        raise RuntimeError(f"DID 0x{did:04X} negative response {response.hex()}")
    expected = bytes((0x62, did >> 8, did & 0xFF))
    if not response.startswith(expected):
        raise RuntimeError(f"DID 0x{did:04X} unexpected response {response.hex()}")
    return response[3:]


def _read_bridge(timeout: float, output_dir: Path) -> dict[int, bytes]:
    from tools.emulation.p1me_can_bridge import P1MEMachineBus

    with P1MEMachineBus(
        output_dir=output_dir, startup_timeout=max(timeout, 600.0),
    ) as bus:
        values = {
            did: _read_isotp(bus, did, timeout)
            for did in BRIDGE_IDENTITY_DIDS
        }
        return values

def _read_panda(bus_number: int, timeout: float) -> dict[int, bytes]:
    from panda import Panda
    from tools.toyota_support.toyota_eps_bus_probe import _import_uds

    panda = Panda()
    try:
        panda.set_safety_mode(3, 1)
        client = _import_uds().UdsClient(panda, TX_ID, RX_ID, bus_number, timeout=timeout)
        return {
            did: bytes(client.read_data_by_identifier(did))
            for did in IDENTITY_DIDS
        }
    finally:
        panda.close()


def _read(args: argparse.Namespace, suffix: str) -> dict[str, Any]:
    if args.transport == "bridge":
        values = _read_bridge(args.timeout, args.work_dir / suffix)
        return _record("p1me-python-can-bridge", "virtual", values)
    values = _read_panda(args.bus, args.timeout)
    return _record("panda", args.bus, values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=("panda", "bridge"), required=True)
    parser.add_argument("--bus", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, default=Path("build/out/eps-identity-control"))
    parser.add_argument(
        "--operator-power-cycle", action="store_true",
        help="after the first Panda read, wait for an operator power cycle and read identity again",
    )
    args = parser.parse_args()
    if args.operator_power_cycle and args.transport != "panda":
        parser.error("--operator-power-cycle is only for a physical Panda bench")

    result: dict[str, Any] = {
        "control": "operator power cycle" if args.operator_power_cycle else "identity read only",
        "before": _read(args, "before"),
    }
    if args.operator_power_cycle:
        input("Power-cycle the EPS supply, restore ignition, then press Enter to read identity again: ")
        result["after"] = _read(args, "after")
        result["identity_match"] = result["before"]["dids"] == result["after"]["dids"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    record = json.dumps(result, indent=2, sort_keys=True)
    args.output.write_text(record + "\n", encoding="utf-8")
    print(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
