#!/usr/bin/env python3
"""Promote exact-F33 pre-fault call-cone store audit output.

Input is the JSON wrapper emitted by `tools/gtarget ... script run` for
AuditCallConeStores/AuditCallConeParamStores.  The promoted artifact keeps the
function denominator and cryptographic digests of the full STORE row set while
remaining compact enough to review and verify without Ghidra.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_IN = ROOT / "build/tmp/f33-prefault-param-store-census.raw.json"
DEFAULT_OUT = ROOT / "data/generated/camry_8965F3307000_prefault_store_audit.json"
ROOTS = [
    "0x0007BBC2", "0x0007C43C", "0x00079EDE", "0x0007A232",
    "0x00066806", "0x00066812", "0x00079DA2", "0x00083156",
    "0x000810F2",
]


def digest(lines: list[str]) -> str:
    payload = ("\n".join(sorted(lines)) + "\n").encode()
    return hashlib.sha256(payload).hexdigest()


def parse_stdout(path: Path) -> str:
    wrapper = json.loads(path.read_text())
    if not isinstance(wrapper, list) or not wrapper or "stdout" not in wrapper[0]:
        raise ValueError(f"unexpected gtarget script wrapper: {path}")
    return wrapper[0]["stdout"]


def build(path: Path) -> dict:
    stdout = parse_stdout(path)
    funcs = [line for line in stdout.splitlines() if line.startswith("FUNC|")]
    stores = [line for line in stdout.splitlines() if line.startswith("STORE|")]
    summaries = [line for line in stdout.splitlines() if line.startswith("SUMMARY|")]
    if len(summaries) != 1:
        raise ValueError("expected exactly one SUMMARY row")

    function_entries = sorted({"0x" + line.split("|")[1].upper() for line in funcs})
    ptr_param = [line for line in stores if "|ptrParam=true|" in line]
    ptr_param_functions = sorted({"0x" + line.split("|")[1].upper() for line in ptr_param})

    fields: dict[str, int] = {}
    for part in summaries[0].split("|")[1:]:
        k, v = part.split("=", 1)
        fields[k] = int(v, 0)

    if fields["functions"] != len(function_entries):
        raise ValueError("function denominator mismatch")
    if fields["computed"] != len(stores):
        raise ValueError("computed STORE row denominator mismatch")

    return {
        "schema": "camry-8965f3307000-prefault-store-audit-v1",
        "target": "camry-8965F3307000",
        "roots": ROOTS,
        "summary": fields,
        "function_entries": function_entries,
        "function_rows_sha256": digest(funcs),
        "store_rows_sha256": digest(stores),
        "pointer_parameter_dependent": {
            "store_count": len(ptr_param),
            "function_count": len(ptr_param_functions),
            "functions": ptr_param_functions,
            "rows_sha256": digest(ptr_param),
        },
        "scope": (
            "Direct-call closure rooted at the exact F33 pre-fault foreground receive path, "
            "RSCFD RX/error interrupt stubs, diagnostic adapter, class-0 CanIf callback, and "
            "class-5/XCP adapter. Parameter dependence is intraprocedural and is therefore an "
            "over-approximation: caller/configuration provenance must still be resolved."
        ),
        "ghidra_script": "ghidra/scripts/investigate/AuditCallConeStores.java",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_IN)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    out = build(args.input)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
