#!/usr/bin/env python3
"""Census compiler fingerprints in every registered RH850 CodeFlash image."""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from tools import REPO_ROOT

REGISTRY = REPO_ROOT / "data" / "analysis_targets.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "generated" / "compiler_fingerprint_census.json"
INSN_RE = re.compile(
    r"^\s*([0-9a-fA-F]+):\s+((?:[0-9a-fA-F]{2}\s+)+)"
    r"\s*([A-Za-z][A-Za-z0-9.]*)\s*(.*?)\s*$"
)
HELPER_RE = re.compile(
    r"(?:^|::|_)(?:stkchk|stack_chk_fail|stack_chk_guard|ghs_checksum)(?:$|_)",
    re.IGNORECASE,
)
COND_BRANCHES = {
    "bc", "be", "bge", "bgt", "bh", "bl", "ble", "blt", "bn", "bnc",
    "bne", "bnh", "bnl", "bnv", "bnz", "bp", "br", "bsa", "bv", "bz",
}


@dataclass(frozen=True)
class Instruction:
    address: int
    mnemonic: str
    operands: str


@dataclass(frozen=True)
class Function:
    entry: int
    name: str
    ranges: tuple[tuple[int, int], ...]
    calling_convention: str


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def parse_listing(path: Path) -> tuple[list[int], dict[int, Instruction]]:
    instructions: dict[int, Instruction] = {}
    with path.open(encoding="utf-8", errors="strict") as stream:
        for line in stream:
            match = INSN_RE.match(line)
            if match is None:
                continue
            address = int(match.group(1), 16)
            if address in instructions:
                raise ValueError(f"{path}: duplicate instruction address 0x{address:x}")
            instructions[address] = Instruction(
                address, match.group(3).lower(), match.group(4).strip().lower()
            )
    if not instructions:
        raise ValueError(f"{path}: no instructions")
    return sorted(instructions), instructions


def parse_inventory(path: Path) -> tuple[list[Function], list[tuple[int, str]]]:
    functions: list[Function] = []
    symbols: list[tuple[int, str]] = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("record") == "function":
                entry = row["entry"]
                if entry.get("space") != "ram" or row.get("is_external"):
                    continue
                offset = int(entry["offset"], 16)
                ranges = tuple(
                    (int(item["min"]["offset"], 16), int(item["max"]["offset"], 16))
                    for item in row["body_ranges"]
                    if item["min"].get("space") == "ram" and item["max"].get("space") == "ram"
                )
                if not ranges:
                    continue
                name = row.get("user_name") or f"FUN_{offset:08x}"
                functions.append(Function(offset, name, ranges, row.get("calling_convention", "")))
            elif row.get("record") == "user_symbol":
                address = row["address"]
                if address.get("space") == "ram":
                    symbols.append((int(address["offset"], 16), row["qualified_name"]))
    if not functions:
        raise ValueError(f"{path}: no CodeFlash functions")
    return functions, symbols


def function_instructions(
    function: Function, addresses: list[int], instructions: dict[int, Instruction]
) -> list[Instruction]:
    result: list[Instruction] = []
    for start, end in function.ranges:
        left = bisect.bisect_left(addresses, start)
        right = bisect.bisect_right(addresses, end)
        result.extend(instructions[address] for address in addresses[left:right])
    result.sort(key=lambda item: item.address)
    return result


def examples(entries: Iterable[int]) -> list[str]:
    return [f"0x{entry:08x}" for entry in sorted(set(entries))[:3]]


def fingerprint_row(instruction_count: int, function_entries: set[int]) -> dict[str, object]:
    return {
        "instruction_count": instruction_count,
        "function_count": len(function_entries),
        "examples": examples(function_entries),
    }


def stack_offset(operands: str) -> str | None:
    match = re.search(r"(-?(?:0x)?[0-9a-f]+)\[(?:sp|r3)\]", operands)
    return match.group(1) if match else None


def has_fixed_canary_shape(insns: list[Instruction]) -> bool:
    # CC-RH V2.08 -Xstack_protector[_all]=NUM: materialize NUM, store it on
    # the stack, reload the same slot, rematerialize NUM, compare, and branch.
    for index, store in enumerate(insns[:10]):
        if store.mnemonic != "st.w":
            continue
        offset = stack_offset(store.operands)
        if offset is None or index == 0:
            continue
        materialize = insns[index - 1]
        if materialize.mnemonic not in {"movea", "mov"}:
            continue
        value = materialize.operands.split(",", 1)[0].strip()
        for load_index in range(index + 1, len(insns)):
            load = insns[load_index]
            if load.mnemonic != "ld.w" or stack_offset(load.operands) != offset:
                continue
            window = insns[load_index + 1:load_index + 5]
            if len(window) < 3:
                continue
            same_value = value in window[0].operands and window[0].mnemonic in {"movea", "mov"}
            compared = window[1].mnemonic == "cmp"
            branched = window[2].mnemonic in COND_BRANCHES
            if same_value and compared and branched:
                return True
    return False


def has_generic_canary_shape(insns: list[Instruction]) -> bool:
    # A prologue stack store, followed by a reload, compare, conditional branch,
    # and nearby control transfer.
    stores = {
        offset
        for insn in insns[:12]
        if insn.mnemonic == "st.w" and (offset := stack_offset(insn.operands)) is not None
    }
    if not stores:
        return False
    for index, insn in enumerate(insns):
        if insn.mnemonic != "ld.w" or stack_offset(insn.operands) not in stores:
            continue
        window = insns[index + 1:index + 7]
        cmp_index = next((i for i, item in enumerate(window) if item.mnemonic == "cmp"), None)
        if cmp_index is None or cmp_index + 1 >= len(window):
            continue
        branch = window[cmp_index + 1]
        if branch.mnemonic not in COND_BRANCHES:
            continue
        if any(item.mnemonic in {"dispose", "jmp", "jr", "jarl"} for item in window[cmp_index + 2:]):
            return True
    return False


def census_one(target: str, row: dict[str, object], listing: Path) -> dict[str, object]:
    inventory = REPO_ROOT / str(row["inventory_baseline"])
    image = REPO_ROOT / str(row["codeflash"])
    addresses, decoded = parse_listing(listing)
    functions, symbols = parse_inventory(inventory)

    instruction_counts = {name: 0 for name in ("callt", "prepare", "dispose")}
    instruction_functions = {name: set() for name in instruction_counts}
    prepare_prologues: set[int] = set()
    interrupt_fingerprints: set[int] = set()
    fixed_canaries: set[int] = set()
    generic_canaries: set[int] = set()
    named_stack_checks: set[int] = set()
    decoded_functions = 0

    helpers = [(address, name) for address, name in symbols if HELPER_RE.search(name)]
    helper_addresses = {address for address, _ in helpers}
    helper_names = sorted({name for _, name in helpers})

    for function in functions:
        insns = function_instructions(function, addresses, decoded)
        if not insns or insns[0].address != function.entry:
            continue
        decoded_functions += 1
        if insns[0].mnemonic == "prepare":
            prepare_prologues.add(function.entry)
        mnemonics = Counter(insn.mnemonic for insn in insns)
        for name in instruction_counts:
            count = mnemonics[name]
            instruction_counts[name] += count
            if count:
                instruction_functions[name].add(function.entry)
        saves_callt_state = any(
            insn.mnemonic == "stsr" and re.search(r"\b(?:ctpc|ctpsw)\b", insn.operands)
            for insn in insns
        )
        if saves_callt_state and "eiret" in mnemonics:
            interrupt_fingerprints.add(function.entry)
        helper_transfers = [
            insn for insn in insns
            if insn.mnemonic in {"jarl", "jr", "callt"}
            and any(re.search(rf"\b0x0*{address:x}\b", insn.operands) for address in helper_addresses)
        ]
        if has_fixed_canary_shape(insns):
            fixed_canaries.add(function.entry)
        elif helper_transfers and has_generic_canary_shape(insns):
            generic_canaries.add(function.entry)
        if any(insn in insns[:8] for insn in helper_transfers):
            named_stack_checks.add(function.entry)

    canaries = fixed_canaries | generic_canaries
    result = {
        "codeflash_sha256": sha256(image),
        "inventory_sha256": sha256(inventory),
        "decoded_function_count": decoded_functions,
        "instruction_fingerprints": {
            name: fingerprint_row(instruction_counts[name], instruction_functions[name])
            for name in instruction_counts
        },
        "prepare_prologues": {
            "function_count": len(prepare_prologues),
            "decoded_function_count": decoded_functions,
            "share": round(len(prepare_prologues) / decoded_functions, 6) if decoded_functions else 0,
            "examples": examples(prepare_prologues),
        },
        "interrupt_callt_state_save_eiret": {
            "function_count": len(interrupt_fingerprints),
            "examples": examples(interrupt_fingerprints),
        },
        "stack_limit_check": {
            "function_count": len(named_stack_checks),
            "examples": examples(named_stack_checks),
        },
        "stack_protector": {
            "function_count": len(canaries),
            "fixed_canary_function_count": len(fixed_canaries),
            "generic_canary_function_count": len(generic_canaries),
            "examples": examples(canaries),
        },
        "named_helpers": helper_names,
    }
    checksum_names = [name for name in helper_names if "ghs_checksum" in name.lower()]
    result["ghs_checksum"] = {
        "symbol_count": len(checksum_names),
        "names": checksum_names,
        "examples": examples(address for address, name in symbols if name in checksum_names),
    }
    return result


def listing_paths(overrides: list[str], targets: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in overrides:
        if "=" not in value:
            raise ValueError(f"listing override must be TARGET=PATH: {value}")
        target, raw_path = value.split("=", 1)
        if target in result:
            raise ValueError(f"duplicate listing override: {target}")
        result[target] = Path(raw_path).resolve()
    for target in targets:
        if target in result:
            continue
        proc = subprocess.run(
            [str(REPO_ROOT / "tools/rh850"), "toolchain", "listing", target],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True,
        )
        result[target] = Path(proc.stdout.strip()).resolve()
    return result


def generate(overrides: list[str]) -> dict[str, object]:
    registry = json.loads(REGISTRY.read_text())
    targets = registry["targets"]
    listings = listing_paths(overrides, list(targets))
    return {
        "schema": "rh850-compiler-fingerprint-census-v1",
        "decoder": "pinned v850-elf-objdump -D -z -b binary -m v850e3v5",
        "registry_sha256": sha256(REGISTRY),
        "targets": {
            target: census_one(target, row, listings[target])
            for target, row in targets.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--listing", action="append", default=[], metavar="TARGET=PATH",
        help="Use an existing trusted linear listing instead of invoking tools/rh850",
    )
    args = parser.parse_args()
    try:
        result = generate(args.listing)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"census_compiler_fingerprints: {exc}\n")
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            parser.exit(1, f"stale compiler fingerprint census: {args.output}\n")
        print(f"compiler fingerprint census matches {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(f"wrote compiler fingerprint census: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
