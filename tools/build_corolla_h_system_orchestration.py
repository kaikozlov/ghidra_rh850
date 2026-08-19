#!/usr/bin/env python3
"""Build the target-native Corolla H system/orchestration comparison report."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/generated/corolla_8965H1202000_system_orchestration_decompiler_evidence.json"
SIENNA_CORPUS = ROOT / "data/generated/decompilations.jsonl"
H_RAW = ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
SIENNA_IMAGE = ROOT / "firmware/RH850_P1M-E_CodeFlash.bin"
DEFAULT_OUT = ROOT / "data/generated/corolla_8965H1202000_system_orchestration.json"

CLOSURE = [
    (0x000001F2, "boot_reset_startup", 0x000001F2, "target-native non-contiguous reset decision"),
    (0x00058404, "autosar_os_task_signal_dispatch", 0x0005389C, "regenerated periodic signal-processing task"),
    (0x00062758, "application_startup_coordinator", 0x0005CAAC, "startup coordinator ending in IRQ enable + foreground loop"),
    (0x000B0518, "system_mode_coordinator", 0x000B05D0, "event-driven mode coordinator"),
    (0x000B28AC, "application_system_transition_phase_init", 0x000B2692, "generated four-argument transition-state initializer"),
    (0x000BA43A, "system_mode_telemetry_snapshot", 0x000B8EE4, "regenerated telemetry/state snapshot"),
    (0x000BD10E, "eps_subsystem_init_orchestrator", 0x000BBFE6, "one-shot EPS subsystem initialization orchestrator"),
    (0x000BEC4C, "system_mode_per_tick_dispatcher", 0x000BD954, "full old/new-mode per-tick dispatcher"),
]
SUPPORT = [
    (0x000BF17E, "reduced/current-mode per-tick companion", 0x000BDE28),
    (0x00057BFE, "application RAM default initializer", 0x0005316C),
    (0x00056FC2, "canonical monolithic Rx-signal consumer; H role is fragmented", 0x000524B8),
    (0x0005B9C4, "RTE staging bank C family", 0x00056970),
    (0x0005C0B6, "RTE staging bank B family", 0x0005701E),
    (0x0005C666, "RTE staging bank A family", 0x0005722E),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_sienna(wanted: set[int]) -> dict[int, dict]:
    out = {}
    for line in SIENNA_CORPUS.read_text().splitlines():
        row = json.loads(line)
        if row.get("entry_addr"):
            entry = int(row["entry_addr"], 16)
            if entry in wanted:
                out[entry] = row
    missing = wanted - out.keys()
    if missing:
        raise ValueError("missing canonical functions: " + ", ".join(hex(x) for x in sorted(missing)))
    return out


def direct_calls(code: str) -> list[str]:
    # Keep only explicit firmware function calls, not language constructs.
    return re.findall(r"\b(?:FUN_[0-9a-fA-F]{8}|[a-zA-Z_][a-zA-Z0-9_]*)\(", code)


def metrics(row: dict) -> dict:
    code = row["decompiled_c"]
    calls = [x[:-1] for x in direct_calls(code)]
    # Drop the function's own signature token if it was matched.
    if calls and calls[0] == row.get("name"):
        calls = calls[1:]
    return {
        "body_size": int(row["body_size"]),
        "direct_call_count": len(calls),
        "unique_direct_call_count": len(set(calls)),
        "if_count": len(re.findall(r"\bif\s*\(", code)),
        "switch_count": len(re.findall(r"\bswitch\s*\(", code)),
        "loop_count": len(re.findall(r"\b(?:for|while|do)\b", code)),
    }


def helper_args(code: str, helper: str) -> list[int]:
    values = []
    pattern = re.compile(re.escape(helper) + r"\((0x[0-9a-fA-F]+|\d+)\)")
    for m in pattern.finditer(code):
        values.append(int(m.group(1), 0))
    return values


def guards(code: str) -> list[str]:
    out = []
    for raw in code.splitlines():
        line = raw.strip()
        if line.startswith("if (") or line.startswith("else if ("):
            line = line.removeprefix("else ")
            line = re.sub(r"uVar\d+", "uVar", line)
            out.append(line)
    return out


def diff_guards(a: list[str], b: list[str]) -> list[dict]:
    rows = []
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            rows.append({
                "opcode": tag,
                "sienna_range": [i1, i2],
                "h_range": [j1, j2],
                "sienna_guards": a[i1:i2],
                "h_guards": b[j1:j2],
            })
    return rows


def call_names(code: str) -> list[str]:
    vals = re.findall(r"\b(FUN_[0-9a-fA-F]{8}|[a-zA-Z_][a-zA-Z0-9_]*)\(", code)
    return [v for v in vals if v not in {"if", "while", "for", "switch"}]


def callers(h: dict[int, dict], target: int) -> list[str]:
    needle = f"FUN_{target:08x}(".lower()
    out = []
    for entry, row in h.items():
        if entry == target:
            continue
        if needle in row["decompiled_c"].lower():
            out.append(f"0x{entry:08X}")
    return sorted(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    ev = json.loads(EVIDENCE.read_text())
    h = {int(r["entry"], 16): r for r in ev["functions"]}
    wanted_s = {x[0] for x in CLOSURE if x[0] != 0x1F2} | {x[0] for x in SUPPORT}
    s = load_sienna(wanted_s)
    h_image = H_RAW.read_bytes()[:0x100000]
    s_image = SIENNA_IMAGE.read_bytes()

    if sha(h_image) != ev["image"]["codeflash_sha256"]:
        raise ValueError("H image/evidence hash drift")

    closure = []
    reset_ev = ev["reset_0x1f2"]
    for s_entry, name, h_entry, role in CLOSURE:
        row = {
            "reference_entry": f"0x{s_entry:08X}",
            "reference_name": name,
            "target_entry": f"0x{h_entry:08X}",
            "role": role,
            "classification": "target-native-role-recovered",
        }
        if s_entry == 0x1F2:
            code = reset_ev["decompiled_c"]
            row["target_evidence"] = {
                "non_contiguous": True,
                "decompiled_c_sha256": reset_ev["decompiled_c_sha256"],
                "raw_windows": reset_ev["raw_windows"],
                "static_markers": {
                    "ffc0a_marker_constants": all(x in code for x in (
                        "0x55555555", "0xaaaaaaaa", "0x5a5a5a5a", "0xf0f0f0f", "0xf0f0f0f0", "0x5a000000"
                    )),
                    "fcu_command_constants": all(x in code for x in ("0x80000", "0xfff7ffff", "0x8000000", "0xf7ffffff")),
                    "fcu_key_literal": "= 0xa5" in code,
                    "terminal_infinite_loop": "while( true )" in code,
                },
            }
        else:
            row["reference_metrics"] = metrics(s[s_entry])
            row["target_metrics"] = metrics(h[h_entry])
        closure.append(row)

    # Mode coordinator: exact generated event schedule is the strongest role anchor.
    s_mode = s[0xB0518]["decompiled_c"]
    h_mode = h[0xB05D0]["decompiled_c"]
    s_query = helper_args(s_mode, "FUN_000b03cc")
    h_query = helper_args(h_mode, "FUN_000b0484")
    s_clear = helper_args(s_mode, "FUN_000b0448")
    h_clear = helper_args(h_mode, "FUN_000b0500")
    if s_query != h_query or s_clear != h_clear:
        raise ValueError("mode event schedule diverged unexpectedly")

    # Full per-tick dispatcher: preserve guard order and record the one contiguous deletion.
    s_tick = s[0xBEC4C]["decompiled_c"]
    h_tick = h[0xBD954]["decompiled_c"]
    s_guards, h_guards = guards(s_tick), guards(h_tick)
    guard_diff = diff_guards(s_guards, h_guards)

    # Calls in the Sienna-only block immediately following system_mode_coordinator.
    start = s_tick.index("system_mode_coordinator();") + len("system_mode_coordinator();")
    end = s_tick.index("if (0x101 < param_2)", start)
    removed_block = s_tick[start:end]
    removed_calls = call_names(removed_block)

    key_h_calls = ["FUN_000b8ee4", "FUN_000b05d0", "FUN_000bba48"]
    h_positions = {name: h_tick.index(name + "()") for name in key_h_calls}
    if not (h_positions[key_h_calls[0]] < h_positions[key_h_calls[1]] < h_positions[key_h_calls[2]]):
        raise ValueError("H per-tick major call ordering drifted")

    support = []
    for s_entry, role, h_entry in SUPPORT:
        support.append({
            "reference_entry": f"0x{s_entry:08X}",
            "reference_name": s[s_entry].get("name", role),
            "target_entry": f"0x{h_entry:08X}",
            "role": role,
            "reference_metrics": metrics(s[s_entry]),
            "target_metrics": metrics(h[h_entry]),
            "boundary": (
                "supporting role analogue; not promoted to an exact one-to-one semantic transfer"
                if s_entry in {0x56FC2, 0x5B9C4, 0x5C0B6, 0x5C666}
                else "target-native supporting analogue"
            ),
        })

    payload = {
        "schema": "corolla-h-system-orchestration-v1",
        "software_id": "8965H1202000",
        "images": {
            "corolla_h_sha256": sha(h_image),
            "sienna_sha256": sha(s_image),
        },
        "evidence": {
            "decompiler_evidence": str(EVIDENCE.relative_to(ROOT)),
            "canonical_corpus": str(SIENNA_CORPUS.relative_to(ROOT)),
        },
        "scheduler_system_closure": closure,
        "scheduler_system_closure_count": len(closure),
        "mode_coordinator": {
            "sienna_entry": "0x000B0518",
            "h_entry": "0x000B05D0",
            "sienna_metrics": metrics(s[0xB0518]),
            "h_metrics": metrics(h[0xB05D0]),
            "event_query_sequence": s_query,
            "event_clear_sequence": s_clear,
            "query_sequences_identical": s_query == h_query,
            "clear_sequences_identical": s_clear == h_clear,
            "mode_comparison_literals": [0x100, 0x200, 0x300, 0x400, 0x500, 0x700],
            "interpretation": "same generated event-driven mode policy; helper addresses and surrounding application wiring moved",
        },
        "per_tick_dispatch": {
            "sienna_entry": "0x000BEC4C",
            "h_entry": "0x000BD954",
            "sienna_metrics": metrics(s[0xBEC4C]),
            "h_metrics": metrics(h[0xBD954]),
            "sienna_guard_count": len(s_guards),
            "h_guard_count": len(h_guards),
            "guard_diff": guard_diff,
            "sienna_only_post_coordinator_calls": removed_calls,
            "h_major_call_order": key_h_calls,
            "h_major_call_positions": h_positions,
            "h_has_0x520_guard": "0x520" in h_tick,
            "sienna_has_0x520_guard": "0x520" in s_tick,
            "boundary": "guard-level wiring comparison; removed helper calls are not assigned OEM semantics solely from location",
        },
        "reduced_per_tick_companion": {
            "sienna_entry": "0x000BF17E",
            "h_entry": "0x000BDE28",
            "sienna_metrics": metrics(s[0xBF17E]),
            "h_metrics": metrics(h[0xBDE28]),
            "h_calls": [x for x in call_names(h[0xBDE28]["decompiled_c"]) if x in key_h_calls],
        },
        "startup_and_wrappers": {
            "startup": {
                "h_entry": "0x0005CAAC",
                "metrics": metrics(h[0x5CAAC]),
                "enables_irq": "__enable_irq();" in h[0x5CAAC]["decompiled_c"],
                "last_explicit_fun_call": [x for x in call_names(h[0x5CAAC]["decompiled_c"]) if x.startswith("FUN_")][-1],
            },
            "subsystem_init_wrapper": {
                "wrapper": "0x000FDC14",
                "target": "0x000BBFE6",
                "wrapper_code": h[0xFDC14]["decompiled_c"],
            },
            "per_tick_wrapper": {
                "wrapper": "0x000FDD40",
                "target": "0x000BD954",
                "wrapper_code": h[0xFDD40]["decompiled_c"],
            },
            "transition_phase_init": {
                "h_entry": "0x000B2692",
                "body_size": h[0xB2692]["body_size"],
                "code": h[0xB2692]["decompiled_c"],
            },
        },
        "regenerated_com_rte_surface": {
            "shared_h_rx_consumer_fragment": "0x000524B8",
            "consumer_fragment_callers_within_evidence": callers(h, 0x524B8),
            "rte_copy_banks": [
                {"target": "0x00056970", "wrapper": "0x00052E4C"},
                {"target": "0x0005701E", "wrapper": "0x00052EEE"},
                {"target": "0x0005722E", "wrapper": "0x00052FEC"},
            ],
            "ram_default_init": {"target": "0x0005316C", "caller": "0x00052CFA"},
            "task_wrapper": {"target": "0x0005389C", "caller": "0x00052CE6"},
            "boundary": "H split/restructured these generated copy/dispatch surfaces; do not infer canonical one-to-one function identity from the representative fragments",
        },
        "supporting_analogues": support,
        "static_conclusion": {
            "scheduler_system_residue_closed": len(closure) == 8,
            "mode_policy_preserved": s_query == h_query and s_clear == h_clear,
            "per_tick_wiring_regenerated": bool(guard_diff),
            "com_rte_surface_regenerated": True,
            "remaining_boundary": "lower helper semantics inside changed wiring remain independently auditable; this report closes the named high-level scheduler/system roles, not every generated COM helper",
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(closure)} scheduler/system roles")


if __name__ == "__main__":
    main()
