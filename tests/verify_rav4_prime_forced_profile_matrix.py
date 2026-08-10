#!/usr/bin/env python3
"""Verify the exhaustive forced RAV4 Prime stock-longitudinal message matrix."""

from __future__ import annotations

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MATRIX = REPO / "data/rav4_prime_forced_profile_matrix.csv"
RX_MAP = REPO / "data/application_rx_map.csv"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


with MATRIX.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
by_id = {int(row["can_id"], 0): row for row in rows}

print("== matrix scope ==")
expected = {0x00F, 0x116, 0x131, 0x183, 0x191, 0x1D2, 0x2E4, 0x343, 0x344, 0x412}
check("matrix has exactly ten relevant message families", set(by_id) == expected, str(sorted(hex(x) for x in by_id)))
check("stock camera replacement set is exact", {can_id for can_id,row in by_id.items() if row["stock_bus2_to_bus0"] == "blocked-and-replaced"} == {0x191,0x412,0x2E4,0x131})
check("reported stock-long SecOC signing set is exact", {can_id for can_id,row in by_id.items() if row["openpilot_tx_stock_long"] == "yes" and "AES-CMAC" in row["secoc_behavior"]} == {0x2E4,0x131})
check("ACC_CONTROL_2 is excluded from stock-long", by_id[0x183]["openpilot_tx_stock_long"].startswith("no in stock-long"))
check("PRE_COLLISION_2 is forwarded rather than replaced", by_id[0x344]["stock_bus2_to_bus0"] == "forwarded" and by_id[0x344]["openpilot_tx_stock_long"] == "none")
check("sync is consumed but not transmitted", by_id[0x00F]["openpilot_tx_stock_long"] == "none" and "TRIP/RESET" in by_id[0x00F]["secoc_behavior"])

print("\n== cadence/shape ==")
check("STEERING_LKA is generated every control frame", by_id[0x2E4]["tx_cadence"] == "every control frame")
check("STEERING_LTA and LTA_2 are half-rate", by_id[0x191]["tx_cadence"] == "every 2 control frames" and by_id[0x131]["tx_cadence"] == "every 2 control frames")
check("LKAS_HUD is 20-frame/UI-edge", "every 20 control frames" in by_id[0x412]["tx_cadence"])
check("SecOC steering wire shapes are 8-byte classic", by_id[0x2E4]["wire_shape"] == "8-byte classic SecOC" and by_id[0x131]["wire_shape"] == "8-byte classic SecOC")
check("ACC_CONTROL_2 notes three-frame openpilot-long cadence", "every 3 control frames" in by_id[0x183]["tx_cadence"])

print("\n== comparative Sienna EPS ownership boundary ==")
with RX_MAP.open(newline="", encoding="utf-8") as stream:
    rx_rows = list(csv.DictReader(stream))
rx_ids = {int(row["can_id"], 0) for row in rx_rows if row.get("can_id", "").startswith("0x")}
for can_id in (0x191, 0x2E4, 0x131):
    check(f"Sienna EPS application RX contains 0x{can_id:03X}", can_id in rx_ids)
for can_id in (0x412, 0x183, 0x344):
    check(f"Sienna EPS application RX excludes 0x{can_id:03X}", can_id not in rx_ids)
check("matrix marks 0x2E4 receiver as protected EPS", by_id[0x2E4]["comparative_receiver_domain"] == "Sienna EPS protected RX")
check("matrix marks 0x131 receiver as protected EPS", by_id[0x131]["comparative_receiver_domain"] == "Sienna EPS protected RX")
check("matrix keeps 0x183 external to Sienna EPS", "external receiving ECU" in by_id[0x183]["comparative_receiver_domain"])
check("matrix keeps 0x344 absent from Sienna EPS", "absent from Sienna EPS RX" in by_id[0x344]["comparative_receiver_domain"])

print("\n== no overclaim ==")
check("matrix receiver column is explicitly comparative", "comparative_receiver_domain" in rows[0])
check("0x412 owner is not invented", by_id[0x412]["comparative_receiver_domain"] == "not recovered as Sienna EPS RX")
check("0x116 is treated as external input rather than camera replacement", by_id[0x116]["stock_bus2_to_bus0"] == "forwarded" and by_id[0x116]["openpilot_tx_stock_long"] == "none")

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
