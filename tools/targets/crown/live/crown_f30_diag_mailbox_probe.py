#!/usr/bin/env python3
"""Live proof of the stock Crown functional-diagnostic resident mailbox.

This does not install RAM code and does not modify CodeFlash. It binds the exact
8965F3012000 application over physical UDS, snapshots DCM channel1 with SID23,
then sends one classic functional ISO-TP single frame on 0x777:

    07 C7 C7 A5 12 34 00 00

Exact Crown firmware routes the seven-byte N-SDU to FEBE527D. SID C7 is absent
from the configured service table, and functional NRC 0x11 is suppressed. The
probe therefore expects no 0x7A9 response and verifies the persistent trailing
six mailbox bytes through the independent physical SID23 path.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from exploit.common.ram_exec import (  # noqa: E402
    ELM327_SAFETY_MODE,
    _import_uds,
    _make_uds_client,
    _read_f181,
    ensure_boardd_stopped,
)
from exploit.ephemeral_runtime import camry_f33_runtime_monitor as monitor  # noqa: E402
from exploit.ephemeral_runtime.camry_f33_runtime_replay_discriminator import _read_memory  # noqa: E402
from exploit.ephemeral_runtime.crown_f30_b6_inline_signer import (  # noqa: E402
    CONTROL_BUS,
    CONTROL_CAN_ID,
    EXPECTED_F181_HEX,
    FUNCTIONAL_DCM_BUFFER_BASE,
    ROUTE,
)

PROBE_FRAME = bytes.fromhex("07c7c7a512340000")
MAILBOX_LENGTH = 7
OBSERVE_SECONDS = 0.080
SETTLE_SECONDS = 0.020


class MailboxProbeError(RuntimeError):
    pass


def mailbox_tail_matches(raw: bytes, frame: bytes = PROBE_FRAME) -> bool:
    """DCM reset clears byte0 only; bytes1..6 are the durable receive witness."""
    if len(raw) != MAILBOX_LENGTH or len(frame) != 8:
        return False
    return raw[1:] == frame[2:]


def run() -> dict[str, Any]:
    ensure_boardd_stopped()
    try:
        from panda import Panda
    except ImportError as exc:
        raise MailboxProbeError("panda module unavailable") from exc

    uds_mod = _import_uds()
    panda = monitor.PandaTap(Panda())
    # Stock ELM327 safety already permits 8-byte classic diagnostic addresses
    # across 0x700..0x7FF, including both 0x7A1 and functional 0x777.
    panda.set_safety_mode(ELM327_SAFETY_MODE, ROUTE.elm327_param)
    panda.set_canfd_auto(CONTROL_BUS, False)
    client = _make_uds_client(panda, uds_mod, ROUTE, timeout=0.3, response_pending_timeout=1.0)

    f181_hex, f181_ascii = _read_f181(client, uds_mod)
    if f181_hex is None or f181_hex.lower() != EXPECTED_F181_HEX:
        raise MailboxProbeError(f"exact Crown F181 unavailable: {f181_hex}")
    client.diagnostic_session_control(uds_mod.SESSION_TYPE.EXTENDED_DIAGNOSTIC)
    before = _read_memory(client, uds_mod, FUNCTIONAL_DCM_BUFFER_BASE, MAILBOX_LENGTH)

    # Drain any stale transport echoes/responses before the only probe frame.
    drain_deadline = time.monotonic() + 0.010
    while time.monotonic() < drain_deadline:
        panda.can_recv()
        time.sleep(0.001)

    sent_at = time.monotonic_ns()
    panda.can_send(CONTROL_CAN_ID, PROBE_FRAME, CONTROL_BUS)
    responses: list[dict[str, Any]] = []
    deadline = time.monotonic() + OBSERVE_SECONDS
    while time.monotonic() < deadline:
        for address, data, bus in panda.can_recv():
            address_i, bus_i = int(address), int(bus)
            if bus_i == CONTROL_BUS and address_i == 0x7A9:
                responses.append({"address": "0x7A9", "bus": bus_i, "data_hex": bytes(data).hex()})
        time.sleep(0.001)

    time.sleep(SETTLE_SECONDS)
    after = _read_memory(client, uds_mod, FUNCTIONAL_DCM_BUFFER_BASE, MAILBOX_LENGTH)
    tail_match = mailbox_tail_matches(after)
    full_match = after == PROBE_FRAME[1:]
    no_functional_response = not responses
    qualified = tail_match and no_functional_response
    return {
        "schema": "crown-f30-functional-diagnostic-mailbox-probe-v1",
        "target": {"f181_hex": f181_hex, "f181_ascii": f181_ascii},
        "route": {
            "bus": ROUTE.bus,
            "elm327_param": ROUTE.elm327_param,
            "functional_can_id": f"0x{CONTROL_CAN_ID:X}",
            "physical_request": "0x7A1",
            "physical_response": "0x7A9",
        },
        "probe": {
            "frame_hex": PROBE_FRAME.hex(),
            "sent_monotonic_ns": sent_at,
            "meaning": "ISO-TP SF len7; unsupported functional SID C7; durable tail tag C7; sequence A5; sentinel 12340000",
        },
        "mailbox": {
            "address": f"0x{FUNCTIONAL_DCM_BUFFER_BASE:08X}",
            "length": MAILBOX_LENGTH,
            "before_hex": before.hex(),
            "after_hex": after.hex(),
            "expected_full_hex": PROBE_FRAME[1:].hex(),
            "expected_tail_hex": PROBE_FRAME[2:].hex(),
            "full_match": full_match,
            "tail_match": tail_match,
            "first_byte_may_be_cleared_by_dcm_reset": True,
        },
        "functional_response": {
            "expected": "suppressed NRC11",
            "observed_0x7a9_frames": responses,
            "none_observed": no_functional_response,
        },
        "qualified": qualified,
        "verdict": "stock_functional_mailbox_live" if qualified else "mailbox_probe_failed",
        "mutation_boundary": {
            "firmware_patch": False,
            "ram_exec": False,
            "flash_write": False,
            "actuation_request": False,
            "volatile_receive_buffer_write": True,
            "can_transmit": ["one classic 0x777 functional diagnostic single frame"],
            "diagnostic_reads": ["F181", "EXTENDED session", "SID23 FEBE527D..FEBE5283 before/after"],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    try:
        result = run()
    except (MailboxProbeError, OSError, ValueError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["qualified"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
