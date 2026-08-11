#!/usr/bin/env python3
"""Verify the non-destructive Toyota EPS Panda-bus discovery helper."""

from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_eps_bus_probe import (
    APPLICATION_SOFTWARE_ID_DID,
    DEFAULT_BUSES,
    DEFAULT_ELM327_PARAM,
    ELM327_SAFETY_MODE,
    RX_ADDR,
    TX_ADDR,
    build_plan,
)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


print("== static safety contract ==")
plan = build_plan(DEFAULT_BUSES, DEFAULT_ELM327_PARAM)
check("probe uses EPS diagnostic TX 0x7A1", plan.tx_addr == TX_ADDR == 0x7A1)
check("probe uses EPS diagnostic RX 0x7A9", plan.rx_addr == RX_ADDR == 0x7A9)
check("probe reads only application software ID F181", plan.did == APPLICATION_SOFTWARE_ID_DID == 0xF181)
check("probe defaults to all three logical Panda buses", plan.buses == (0, 1, 2))
check("probe uses ELM327 safety mode", plan.elm327_safety_mode == ELM327_SAFETY_MODE == 3)
check("probe defaults to nonzero ELM327 param", plan.elm327_param == DEFAULT_ELM327_PARAM == 1)
check("probe declares no mutating services", plan.mutating_services == ())

print("\n== CLI dry-run ==")
script = REPO / "tools" / "toyota_eps_bus_probe.py"
run = subprocess.run(
    [sys.executable, str(script)],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("default CLI dry-run succeeds", run.returncode == 0, run.stderr.strip())
output = json.loads(run.stdout)
check("default CLI does not execute hardware", output["mode"] == "dry-run")
check("dry-run reports buses 0/1/2", output["plan"]["buses"] == [0, 1, 2])
check("dry-run reports F181", output["plan"]["did"] == 0xF181)
check("dry-run reports normal-routing ELM327 param", output["plan"]["elm327_param"] == 1)
check("routing note distinguishes OBD mux", "param=0" in output["routing_note"] and "logical bus 1" in output["routing_note"])

custom = subprocess.run(
    [sys.executable, str(script), "--bus", "1", "--elm327-param", "0"],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("explicit OBD-mux dry-run succeeds", custom.returncode == 0, custom.stderr.strip())
custom_output = json.loads(custom.stdout)
check("explicit bus selection is preserved", custom_output["plan"]["buses"] == [1])
check("explicit ELM327 param 0 is preserved", custom_output["plan"]["elm327_param"] == 0)

invalid = subprocess.run(
    [sys.executable, str(script), "--bus", "3"],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("invalid logical bus is rejected", invalid.returncode != 0)

print("\n== Sienna firmware diagnostic-controller continuity ==")
codeflash = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

# Boot CanIf configuration recovered from the firmware:
#   0x8920: two 12-byte receive software-filter entries
#   0x8944: Tx-PDU count
#   0x8948: one 12-byte Tx-PDU config
#   0x898C: 48 eight-byte HRH routes (3 RSCFD channels x 16 FIFOs)
rx_filter_ids = [struct.unpack_from("<I", codeflash, 0x8920 + i * 12 + 4)[0] for i in range(2)]
tx_pdu_count = struct.unpack_from("<I", codeflash, 0x8944)[0]
tx_can_id = struct.unpack_from("<I", codeflash, 0x894C)[0]
tx_hth = struct.unpack_from("<H", codeflash, 0x8952)[0]

check("boot receive filter 0 is EPS request 0x7A1", rx_filter_ids[0] == 0x7A1)
check("boot receive filter 1 is secondary request 0x777", rx_filter_ids[1] == 0x777)
check("boot has exactly one configured diagnostic Tx PDU", tx_pdu_count == 1)
check("boot diagnostic reply CAN ID is 0x7A9", tx_can_id == 0x7A9)
check("boot diagnostic Tx HTH is 0x13", tx_hth == 0x13)
check("boot diagnostic Tx HTH selects RSCFD channel 1", ((tx_hth & 0x7F) >> 4) == 1)

hrh_routes: list[tuple[int, int, int, int]] = []
for hrh in range(0x30):
    callback, filter_start, filter_count, flags = struct.unpack_from(
        "<IHBB", codeflash, 0x898C + hrh * 8
    )
    hrh_routes.append((callback, filter_start, filter_count, flags))

filter0_hrhs = [
    hrh
    for hrh, (_callback, filter_start, filter_count, _flags) in enumerate(hrh_routes)
    if filter_count and filter_start == 0
]
check("boot EPS 0x7A1 filter is routed only through HRHs 0x10 and 0x13", filter0_hrhs == [0x10, 0x13], str(filter0_hrhs))
check("both boot EPS request HRHs select RSCFD channel 1", all(((hrh >> 4) & 0x7) == 1 for hrh in filter0_hrhs))
check("boot RSCFD channel 0 has no active receive filter", all(route[2] == 0 for route in hrh_routes[0x00:0x10]))
check("boot RSCFD channel 2 has no active receive filter", all(route[2] == 0 for route in hrh_routes[0x20:0x30]))

# Application EIINT table lives at 0x20200.  The same Renesas RSCAN source
# numbering used by the boot table is CAN0 RX/TX=184/185, CAN1 RX/TX=187/188,
# CAN2 RX/TX=192/193.  Only the CAN1 pair is installed in the application.
app_vector_base = 0x20200
app_vectors = {
    irq: struct.unpack_from("<I", codeflash, app_vector_base + irq * 4)[0]
    for irq in (184, 185, 187, 188, 192, 193)
}
check("application CAN1 RX vector targets 0x6506A", app_vectors[187] == 0x6506A)
check("application CAN1 TX vector targets 0x65028", app_vectors[188] == 0x65028)
check(
    "application CAN0 and CAN2 vectors remain on the default handler",
    len({app_vectors[184], app_vectors[185], app_vectors[192], app_vectors[193]}) == 1
    and app_vectors[184] == 0x61D88,
    str(app_vectors),
)
check(
    "application CAN1 RX/TX bodies hard-code channel 1",
    codeflash[0x82E40:0x82E46] == bytes.fromhex("800721000132")
    and codeflash[0x8474E:0x84754] == bytes.fromhex("800721000132"),
)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
