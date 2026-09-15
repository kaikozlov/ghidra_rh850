#!/usr/bin/env python3
"""Historical read-only check for the rejected Crown classic-0x1DA sideband candidate.

This probe sends no CAN application/control frame. It uses only stock-wire EPS
UDS on Panda bus1/ELM param1 to bind F181, enter EXTENDED for SID23, and compare
the EPS-local 0x1DA generation byte before/after a passive CAN observation.
Any native bus1 0x1DA or internal generation movement rejects the candidate.
Diagnostic keepalives preserve the session; receive accounting includes frames
consumed by the UDS client as well as the outer observation loop.
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
    _import_uds,
    _make_uds_client,
    _read_f181,
    ensure_boardd_stopped,
)
from exploit.ephemeral_runtime import camry_f33_runtime_monitor as monitor  # noqa: E402
from exploit.ephemeral_runtime.camry_f33_runtime_replay_discriminator import _read_memory  # noqa: E402
from exploit.ephemeral_runtime.crown_f30_b6_inline_signer import (  # noqa: E402
    CONTROL_BUS,
    LEGACY_SIDEBAND_CAN_ID,
    EXPECTED_F181_HEX,
    ROUTE,
    LEGACY_SIDEBAND_GENERATION_BASE,
)


# Historical rejected-candidate aliases retained for the standalone evidence test.
CONTROL_CAN_ID = LEGACY_SIDEBAND_CAN_ID
SIDEBAND_GENERATION_BASE = LEGACY_SIDEBAND_GENERATION_BASE
HEARTBEAT_PERIOD_S = 2.0


class PreflightError(RuntimeError):
    pass


class PreflightTap(monitor.PandaTap):
    """Count at the shared RX boundary, before UDS can filter or drain frames."""

    def __init__(self, panda: Any):
        super().__init__(panda)
        self.observing = False
        self.counts: dict[int, int] = {}
        self.all_counts: dict[int, int] = {}
        self.samples: list[dict[str, Any]] = []

    def begin_observation(self) -> None:
        self.counts.clear()
        self.all_counts.clear()
        self.samples.clear()
        self.observing = True

    def can_recv(self):
        rows = super().can_recv()
        if self.observing:
            for address, data, bus in rows:
                address, bus = int(address), int(bus)
                self.all_counts[bus] = self.all_counts.get(bus, 0) + 1
                if address != LEGACY_SIDEBAND_CAN_ID:
                    continue
                self.counts[bus] = self.counts.get(bus, 0) + 1
                if len(self.samples) < 32:
                    self.samples.append({"bus": bus, "data_hex": bytes(data).hex()})
        return rows


def run(duration: float) -> dict[str, Any]:
    if not 0.1 <= duration <= 30.0:
        raise PreflightError("duration must be in [0.1, 30] seconds")
    ensure_boardd_stopped()
    try:
        from panda import Panda
    except ImportError as exc:
        raise PreflightError("panda module unavailable") from exc
    uds_mod = _import_uds()
    panda = PreflightTap(Panda())
    monitor._alloutput_mode(panda)
    panda.set_canfd_auto(CONTROL_BUS, False)
    client = _make_uds_client(panda, uds_mod, ROUTE, timeout=0.3, response_pending_timeout=1.0)
    f181_hex, f181_ascii = _read_f181(client, uds_mod)
    if f181_hex is None or f181_hex.lower() != EXPECTED_F181_HEX:
        raise PreflightError(f"exact Crown F181 unavailable: {f181_hex}")
    client.diagnostic_session_control(uds_mod.SESSION_TYPE.EXTENDED_DIAGNOSTIC)
    # Include the opening read: the ECU samples the byte before its response
    # reaches the host, and application traffic can arrive in that interval.
    panda.begin_observation()
    observation_start = time.monotonic()
    generation_before = _read_memory(client, uds_mod, LEGACY_SIDEBAND_GENERATION_BASE, 1)[0]
    last_heartbeat = time.monotonic()
    deadline = last_heartbeat + duration
    heartbeats_sent = 0
    while time.monotonic() < deadline:
        panda.can_recv()
        if time.monotonic() - last_heartbeat >= HEARTBEAT_PERIOD_S:
            client.tester_present()
            last_heartbeat = time.monotonic()
            heartbeats_sent += 1
        time.sleep(0.001)

    # Preserve EXTENDED through the closing read. The tap also records frames
    # drained by this request and by every periodic TesterPresent above.
    client.tester_present()
    heartbeats_sent += 1
    generation_after = _read_memory(client, uds_mod, LEGACY_SIDEBAND_GENERATION_BASE, 1)[0]
    observed_elapsed = time.monotonic() - observation_start
    panda.observing = False
    counts, samples = panda.counts, panda.samples
    bus1_count = counts.get(CONTROL_BUS, 0)
    generation_stable = generation_before == generation_after
    safe_to_experiment = bus1_count == 0 and generation_stable
    return {
        "schema": "crown-f30-sideband-preflight-v1",
        "target": {"f181_hex": f181_hex, "f181_ascii": f181_ascii},
        "route": {"bus": ROUTE.bus, "elm327_param": ROUTE.elm327_param},
        "candidate": {"can_id": f"0x{LEGACY_SIDEBAND_CAN_ID:X}", "bus": CONTROL_BUS, "format": "classic", "dlc": 8},
        "duration_s": duration,
        "observed_elapsed_s": observed_elapsed,
        "heartbeats_sent": heartbeats_sent,
        "receive_accounting": "shared Panda RX, including UDS drains and closing read",
        "observed_counts_by_bus": {str(k): v for k, v in sorted(panda.all_counts.items())},
        "observed_1da_counts_by_bus": {str(k): v for k, v in sorted(counts.items())},
        "samples": samples,
        "eps_generation": {
            "address": f"0x{LEGACY_SIDEBAND_GENERATION_BASE:08X}",
            "before": generation_before,
            "after": generation_after,
            "stable": generation_stable,
            "delta_modulo_256": (generation_after - generation_before) & 0xFF,
        },
        "safe_to_experiment": safe_to_experiment,
        "verdict": "candidate_idle" if safe_to_experiment else "candidate_in_use",
        "mutation_boundary": {
            "can_application_transmit": False,
            "ram_write": False,
            "flash_write": False,
            "diagnostic_actions": ["F181 read", "EXTENDED session", "SID23 generation-byte reads", "TesterPresent heartbeat"],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--duration", type=float, default=5.0)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    try:
        result = run(args.duration)
    except (PreflightError, OSError, ValueError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["safe_to_experiment"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
