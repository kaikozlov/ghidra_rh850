#!/usr/bin/env python3
"""Promote exact-F33 expanded pre-fault control-flow Ghidra audits.

The expanded root set includes the original receive/interrupt cone plus all six
resolved diagnostic transport callbacks.  Two compact outputs preserve exact
function/operation denominators and row digests without checking large Ghidra
stdout blobs into the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ROOTS = [
    "0x0007BBC2", "0x0007C43C", "0x00079EDE", "0x0007A232",
    "0x00066806", "0x00066812", "0x00079DA2", "0x00083156",
    "0x000810F2",
    "0x000920BE", "0x00092152", "0x000926D2", "0x000921D2",
    "0x00092836", "0x00092946",
]
DEFAULT_STORE_IN = ROOT / "build/tmp/f33-prefault-control-flow-store.raw.json"
DEFAULT_OPS_IN = ROOT / "build/tmp/f33-prefault-control-flow-ops.raw.json"
DEFAULT_STORE_OUT = ROOT / "data/generated/camry_8965F3307000_prefault_control_flow_store_audit.json"
DEFAULT_OPS_OUT = ROOT / "data/generated/camry_8965F3307000_prefault_control_flow_ops.json"


def digest(lines: list[str]) -> str:
    return hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode()).hexdigest()


def stdout(path: Path) -> str:
    wrapper = json.loads(path.read_text())
    if not isinstance(wrapper, list) or not wrapper or "stdout" not in wrapper[0]:
        raise ValueError(f"unexpected Ghidra script wrapper: {path}")
    return wrapper[0]["stdout"]


def summary(line: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for field in line.split("|")[1:]:
        k, v = field.split("=", 1)
        out[k] = int(v, 0)
    return out


def build_store(path: Path) -> dict:
    lines = stdout(path).splitlines()
    funcs = [x for x in lines if x.startswith("FUNC|")]
    stores = [x for x in lines if x.startswith("STORE|")]
    sums = [x for x in lines if x.startswith("SUMMARY|")]
    if len(sums) != 1:
        raise ValueError("expected exactly one store SUMMARY row")
    fields = summary(sums[0])
    entries = sorted({"0x" + x.split("|")[1].upper() for x in funcs})
    ptr = [x for x in stores if "|ptrParam=true|" in x]
    ptr_funcs = sorted({"0x" + x.split("|")[1].upper() for x in ptr})
    if fields["functions"] != len(entries) or fields["computed"] != len(stores):
        raise ValueError("expanded store denominator mismatch")
    return {
        "schema": "camry-8965f3307000-prefault-control-flow-store-audit-v1",
        "target": "camry-8965F3307000",
        "roots": ROOTS,
        "summary": fields,
        "function_entries": entries,
        "function_rows_sha256": digest(funcs),
        "store_rows_sha256": digest(stores),
        "pointer_parameter_dependent": {
            "store_count": len(ptr),
            "function_count": len(ptr_funcs),
            "functions": ptr_funcs,
            "rows_sha256": digest(ptr),
        },
        "scope": (
            "Direct-call closure rooted at pre-fault normal/XCP receive, CAN1 RX/TX/periodic "
            "service, CanIf, and all six resolved DCM transport callbacks. Indirect callback "
            "targets are closed separately by exact route-table analysis."
        ),
        "ghidra_script": "ghidra/scripts/investigate/AuditCallConeStores.java",
    }


def build_ops(path: Path) -> dict:
    lines = stdout(path).splitlines()
    sums = [x for x in lines if x.startswith("SUMMARY|")]
    if len(sums) != 1:
        raise ValueError("expected exactly one memory-op SUMMARY row")
    fields = summary(sums[0])
    loads = [x for x in lines if x.startswith("LOAD|")]
    inds = [x for x in lines if x.startswith("IND|")]
    arith = [x for x in lines if x.startswith("ARITH|")]
    if fields["param_loads"] != len(loads) or fields["param_indirects"] != len(inds) or fields["param_arith"] != len(arith):
        raise ValueError("memory-op row denominator mismatch")
    return {
        "schema": "camry-8965f3307000-prefault-control-flow-ops-v1",
        "target": "camry-8965F3307000",
        "roots": ROOTS,
        "summary": fields,
        "parameter_dependent_load_rows_sha256": digest(loads),
        "parameter_dependent_indirect_rows_sha256": digest(inds),
        "parameter_dependent_arithmetic_rows_sha256": digest(arith),
        "parameter_dependent_indirect_rows": inds,
        "scope": (
            "Same expanded 15-root pre-fault cone. Intraprocedural parameter dependence is an "
            "over-approximation; the five indirect sites are resolved by exact configuration/route bounds."
        ),
        "ghidra_script": "ghidra/scripts/investigate/AuditCallConeMemoryOps.java",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--store-input", type=Path, default=DEFAULT_STORE_IN)
    ap.add_argument("--ops-input", type=Path, default=DEFAULT_OPS_IN)
    ap.add_argument("--store-out", type=Path, default=DEFAULT_STORE_OUT)
    ap.add_argument("--ops-out", type=Path, default=DEFAULT_OPS_OUT)
    args = ap.parse_args()
    store, ops = build_store(args.store_input), build_ops(args.ops_input)
    args.store_out.parent.mkdir(parents=True, exist_ok=True)
    args.store_out.write_text(json.dumps(store, indent=2, sort_keys=True) + "\n")
    args.ops_out.write_text(json.dumps(ops, indent=2, sort_keys=True) + "\n")
    print(args.store_out)
    print(args.ops_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
