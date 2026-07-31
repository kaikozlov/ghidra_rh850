#!/usr/bin/env python3
"""Verify the recovered motor-control/PWM path and command stopping boundary."""
from __future__ import annotations

import csv
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "motor_actuation_path.csv"
REPORT_PATH = ROOT / "docs" / "architecture" / "control-partition.md"
CODEFLASH_PATH = ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin"
SFR_PATH = ROOT / "data" / "p1m_sfr_labels.csv"

EXPECTED_STAGES = {
    "phase_result_window_read",
    "ch0_sample_snapshot",
    "phase_sample_publish",
    "phase_current_conditioning",
    "clarke_park_feedback",
    "dq_feedback_combine",
    "dq_current_reference",
    "dq_current_pi_axis_a",
    "dq_current_pi_axis_b",
    "inverse_park_phase_command",
    "phase_duty_publish",
    "phase_duty_select",
    "tsg3_compare_stage",
    "tsg3_pwm_commit",
    "conditioned_2e4_boundary",
    "conditioned_2e4_export",
    "command_to_current_gap",
}

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{suffix}")


def decode_branch(addr: int, codeflash: bytes) -> tuple[str, int] | None:
    if addr + 4 > len(codeflash):
        return None
    w0 = struct.unpack_from("<H", codeflash, addr)[0]
    if (w0 >> 6) & 0x1F != 0x1E:
        return None
    w1 = struct.unpack_from("<H", codeflash, addr + 2)[0]
    if w1 & 1:
        return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    return ("jarl" if reg2 else "jr"), addr + (high << 16) + w1


def branch_targets(codeflash: bytes, start: int, end: int) -> set[int]:
    targets: set[int] = set()
    for addr in range(start, end, 2):
        decoded = decode_branch(addr, codeflash)
        if decoded is not None:
            targets.add(decoded[1])
    return targets


def main() -> int:
    print("== motor actuation evidence table ==")
    check("motor actuation CSV exists", CSV_PATH.is_file(), str(CSV_PATH))
    if not CSV_PATH.is_file():
        return 1
    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    stages = {row["stage"] for row in rows}
    check("all required actuation and boundary stages are present",
          EXPECTED_STAGES.issubset(stages), str(sorted(EXPECTED_STAGES - stages)))
    check("TSG3 commit row is verified",
          any(row["stage"] == "tsg3_pwm_commit"
              and row["evidence_grade"] == "verified" for row in rows))
    check("command/current gap remains bounded",
          any(row["stage"] == "command_to_current_gap"
              and row["evidence_grade"] == "bounded"
              and "not" in row["hardware_or_calibration"] for row in rows))

    codeflash = CODEFLASH_PATH.read_bytes()
    print("\n== TAUJ0 CH0 execution order ==")
    ch0_targets = branch_targets(codeflash, 0x656F0, 0x65720)
    check("CH0 worker commits prior compares then runs current-control group",
          {0x60DDC, 0x5784C}.issubset(ch0_targets))
    steady_dispatch = branch_targets(codeflash, 0x5784C, 0x57902)
    check("steady CH0 dispatch reaches conditioning and motor-control workers",
          {0x5CE0C, 0x5CEA8, 0x5D18C}.issubset(steady_dispatch))
    check("steady conditioning dispatch reaches phase conditioning",
          0x47C3C in branch_targets(codeflash, 0x5CE0C, 0x5CEA8))
    check("steady transform dispatch reaches Clarke/Park stage",
          0x35960 in branch_targets(codeflash, 0x5CEA8, 0x5CEE4))

    print("\n== phase-current control pipeline ==")
    motor_targets = branch_targets(codeflash, 0x5D18C, 0x5D264)
    required_motor_targets = {
        0x37644, 0x37712, 0x36902, 0x36A44,
        0x38464, 0x38554, 0x3875A,
        0x569A8, 0x56D3E,
    }
    check("motor worker calls feedback, current PI, inverse transform, and duty stages",
          required_motor_targets.issubset(motor_targets),
          str(sorted(hex(x) for x in required_motor_targets - motor_targets)))
    check("Clarke/Park stage reads conditioned phase state",
          codeflash[0x35968:0x35974] == bytes.fromhex("150c80860080169c178c24f6"))
    check("axis A PI reads reference 0xFEBE6D2A and feedback 0xFEBE6D1C",
          codeflash[0x36930:0x3693C] == bytes.fromhex("240f2ab5249f1cb5b3090106"))
    check("axis B PI reads reference 0xFEBE6D28 and feedback 0xFEBE6D18",
          codeflash[0x36A74:0x36A80] == bytes.fromhex("240f28b5249f18b5b3090106"))
    check("final phase publisher reaches slot writer 0x56B18",
          0x56B18 in branch_targets(codeflash, 0x3875A, 0x38814))
    check("selected phase commands reach TSG3 compare calculator",
          0x60BFA in branch_targets(codeflash, 0x65944, 0x65998)
          and 0x60BFA in branch_targets(codeflash, 0x659AA, 0x659FE))

    print("\n== physical TSG3 PWM boundary ==")
    check("0x60DDC contains exact W/V/U extended-compare stores",
          codeflash[0x60DFE:0x60E14] == bytes.fromhex(
              "81074f9803ce739881070f9803ce719881078f9803ce"))
    with SFR_PATH.open(newline="", encoding="utf-8") as fh:
        sfr_rows = {row["address"].lower(): row for row in csv.DictReader(
            line for line in fh if not line.startswith("#"))}
    expected_sfrs = {
        "0xffe70180": "TSG30CMPWE",
        "0xffe70184": "TSG30CMPVE",
        "0xffe70188": "TSG30CMPUE",
        "0xffe71180": "TSG31CMPWE",
        "0xffe71184": "TSG31CMPVE",
        "0xffe71188": "TSG31CMPUE",
    }
    for address, name in expected_sfrs.items():
        row = sfr_rows.get(address)
        check(f"{address} labeled {name}", row is not None and row["name"] == name)

    print("\n== documented stopping boundary ==")
    report = REPORT_PATH.read_text(encoding="utf-8")
    for token in (
        "0x60DDC", "TSG30CMPWE", "0x35960", "0x36902", "0x36A44",
        "0xFEBEAE16", "0xFEBEE8CA", "command-to-current-reference gap",
        "data/motor_actuation_path.csv",
        "0x37712", "producer cone", "0xB8C1A", "command-disconnected",
    ):
        check(f"report contains {token}", token.lower() in report.lower())

    print("\n== d/q reference producer cone (command-to-current gap) ==")
    # The d/q current references FEBE6D28/FEBE6D2A are the FOC torque/flux
    # setpoints the PI loops (0x36902/0x36A44) track. Their sole producer is
    # dual_motor_dq_current_reference at 0x37712 (entry 0x3770e). The apparent
    # second writer in autosar_os_task_signal_dispatch (entry 0x58404) at
    # instruction 0x5ae28 is a buffer clear: it zeroes FEBE6D24..6D2E with r0
    # then calls the constructor. It is not a copy of conditioned command state.
    check("dispatch zeroes the d/q block then calls the constructor",
          codeflash[0x5ae28:0x5ae3c] == bytes.fromhex(
              "24f624b5"   # movea -0x4adc,gp,ep  -> ep = FEBE6D24
              "8004"       # sst.h 0x0,ep,r0       -> FEBE6D24 = 0
              "8104"       # sst.h 0x2,ep,r0       -> FEBE6D26 = 0
              "8204"       # sst.h 0x4,ep,r0       -> FEBE6D28 = 0  (x-ref WRITE)
              "8304"       # sst.h 0x6,ep,r0       -> FEBE6D2A = 0
              "8404"       # sst.h 0x8,ep,r0       -> FEBE6D2C = 0
              "8504"       # sst.h 0xa,ep,r0       -> FEBE6D2E = 0
              "bdffd6c8"))  # jarl 0x3770e        -> dual_motor_dq_current_reference
    check("the dispatch write site calls the constructor, not a command copy",
          decode_branch(0x5ae38, codeflash)[1] == 0x3770e)
    # Constructor 0x37712 reads only motor-block inputs. The two GP-relative
    # halfword loads below resolve to FEBE6D7E and FEBE6D70; later ep-relative
    # loads read FEBE6D4E/6D50/6D52/6D54. No conditioned-command location
    # (FEBE7F94/EF184/AE20/BF80/BF84/BF9A/BFA2/AE16) is read anywhere in the
    # producer cone (0x37712 + 0x3795e + 0x37b5a + 0x37cd4).
    check("constructor reads motor-block FEBE6D7E, not command state",
          codeflash[0x37712:0x37716] == bytes.fromhex("24977eb5"))  # ld.h -0x4a82,gp,r18
    check("constructor reads motor-block FEBE6D70, not command state",
          codeflash[0x3771a:0x3771e] == bytes.fromhex("249f70b5"))  # ld.h -0x4a90,gp,r19

    # Full negative: scan every gp-relative instruction in the producer cone
    # and assert none targets a conditioned-command location.  This closes the
    # gap between the spot-checks above and the doc claim that the cone is
    # "clean two levels deep" with no command-state access.
    GP = 0xFEBEB800
    COMMAND_STATE_LOCS = frozenset({
        0xFEBE7F94, 0xFEBEF184, 0xFEBEAE20, 0xFEBEBF80,
        0xFEBEBF84, 0xFEBEBF9A, 0xFEBEBFA2, 0xFEBEAE16,
    })
    PRODUCER_CONE_RANGES = [
        (0x37712, 0x3778A),   # dual_motor_dq_current_reference (120B)
        (0x3795E, 0x37B56),   # FUN_0003795e (504B)
        (0x37B5A, 0x37B8E),   # FUN_00037b5a (52B)
        (0x37CD4, 0x37CFA),   # FUN_00037cd4 (38B)
    ]
    cmd_hits: list[str] = []
    for fstart, fend in PRODUCER_CONE_RANGES:
        for off in range(fstart + 2, fend, 2):
            w1 = struct.unpack_from("<H", codeflash, off)[0]
            w0 = struct.unpack_from("<H", codeflash, off - 2)[0]
            reg1 = (w0 >> 11) & 0x1F
            if reg1 != 4:  # not gp-relative
                continue
            disp = w1 - 0x10000 if w1 >= 0x8000 else w1
            target = (GP + disp) & 0xFFFFFFFF
            if target in COMMAND_STATE_LOCS:
                cmd_hits.append(f"0x{target:08X} accessed at 0x{off:X}")
    check("no gp-relative access to conditioned-command state in producer cone",
          not cmd_hits, "; ".join(cmd_hits))
    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
