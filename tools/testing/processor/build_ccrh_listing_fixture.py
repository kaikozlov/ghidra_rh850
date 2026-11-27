#!/usr/bin/env python3
"""Build/check the CC-RH listing-oracle fixture from the compiler's .prn file."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

from tools import REPO_ROOT

FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "processor"
SOURCE = FIXTURE_DIR / "ccrh_listing_fixture.c"
BINARY = FIXTURE_DIR / "ccrh_listing_fixture.bin"
EXPECTED = FIXTURE_DIR / "ccrh_listing_fixture.expected.tsv"
COMPILER = "CC-RH V2.08.00 [26 Jun 2026]"
OPTIONS = "-Xcpu=g3m -Osize -Oinline=0 -Xep=callee -c"
LABEL_RE = re.compile(r"^([0-9A-F]{8})\s+\d+\s+([.$A-Za-z_][.$A-Za-z0-9_]*):")
INSN_RE = re.compile(
    r"^([0-9A-F]{8})\s+([0-9A-F]{4,12})\s+\d+\s+"
    r"([a-z][a-z0-9.]*)\s*(.*?)\s*$",
    re.IGNORECASE,
)
ALIASES = {"bz9": "be", "bnz9": "bne", "bl9": "bc"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_prn(path: Path) -> tuple[bytes, list[tuple[int, bytes, str, str, str, str, str, str]]]:
    lines = path.read_text(encoding="ascii").splitlines()
    labels: dict[str, int] = {}
    for line in lines:
        match = LABEL_RE.match(line)
        if match:
            labels[match.group(2)] = int(match.group(1), 16)

    rows: list[tuple[int, bytes, str, str, str, str, str, str]] = []
    end = 0
    for line in lines:
        match = INSN_RE.match(line)
        if not match:
            continue
        address = int(match.group(1), 16)
        code = bytes.fromhex(match.group(2))
        mnemonic = match.group(3).lower()
        operands = match.group(4).strip()
        oracle_mnemonic = ALIASES.get(mnemonic, mnemonic[:-1] if mnemonic.endswith("9") else mnemonic)
        oracle_operands = operands
        for label, target in sorted(labels.items(), key=lambda item: -len(item[0])):
            oracle_operands = re.sub(
                rf"(?<![.$A-Za-z0-9_]){re.escape(label)}(?![.$A-Za-z0-9_])",
                f"0x{target:x}", oracle_operands,
            )
        comparison_class = ""
        comparison_rule = ""
        if mnemonic.endswith("9"):
            comparison_class = "rendering-convention"
            comparison_rule = "apply-r-v850-pc9-and-condition-alias"
        elif mnemonic.startswith(("ld.", "st.")) and "[" in operands:
            comparison_class = "rendering-convention"
            comparison_rule = "memory-displacement-base-operands"
        elif mnemonic == "jmp" and operands == "[r31]":
            comparison_class = "rendering-convention"
            comparison_rule = "indirect-lp-register"
        elif mnemonic == "dispose":
            comparison_class = "rendering-convention"
            comparison_rule = "dispose-byte-count-mask-list"
        rows.append((
            address, code, mnemonic, operands, oracle_mnemonic, oracle_operands,
            comparison_class, comparison_rule,
        ))
        end = max(end, address + len(code))
    if not rows:
        raise ValueError(f"{path}: no listed instructions")
    blob = bytearray(end)
    occupied = bytearray(end)
    for address, code, *_ in rows:
        for index, value in enumerate(code, address):
            if occupied[index]:
                raise ValueError(f"{path}: overlapping code at 0x{index:x}")
            occupied[index] = 1
            blob[index] = value
    if not all(occupied):
        first = occupied.index(0)
        raise ValueError(f"{path}: unlisted byte gap at 0x{first:x}")
    return bytes(blob), rows


def apply_linked_bytes(
    blob: bytes,
    rows: list[tuple[int, bytes, str, str, str, str, str, str]],
    binary: Path,
) -> tuple[bytes, list[tuple[int, bytes, str, str, str, str, str, str]]]:
    linked = binary.read_bytes()
    if len(linked) != len(blob):
        raise ValueError(f"{binary}: linked text size {len(linked)} != listing size {len(blob)}")
    relocated = [
        (address, linked[address:address + len(code)], *fields)
        for address, code, *fields in rows
    ]
    return linked, relocated


def render(
    blob: bytes,
    rows: list[tuple[int, bytes, str, str, str, str, str, str]],
) -> bytes:
    header = [
        "# rh850-ccrh-listing-oracle-v2",
        f"# compiler: {COMPILER}",
        f"# options: {OPTIONS}",
        f"# source_sha256: {digest(SOURCE.read_bytes())}",
        f"# text_sha256: {digest(blob)}",
        "# address\tbytes\tlisting_mnemonic\tlisting_operands\toracle_mnemonic\toracle_operands\tcomparison_class\tcomparison_rule",
    ]
    body = [
        f"{address:08x}\t{code.hex()}\t{mnemonic}\t{operands}\t{oracle_mnemonic}\t{oracle_operands}\t{comparison_class}\t{comparison_rule}"
        for address, code, mnemonic, operands, oracle_mnemonic, oracle_operands, comparison_class, comparison_rule in rows
    ]
    return ("\n".join([*header, *body]) + "\n").encode()


def parse_expected(path: Path) -> tuple[bytes, bytes]:
    text = path.read_text(encoding="utf-8")
    source_line = next((line for line in text.splitlines() if line.startswith("# source_sha256: ")), None)
    if source_line != f"# source_sha256: {digest(SOURCE.read_bytes())}":
        raise ValueError(f"{path}: source identity drift")
    rows = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) != 8:
            raise ValueError(f"{path}: malformed row: {line}")
        address = int(fields[0], 16)
        code = bytes.fromhex(fields[1])
        rows.append((address, code))
    end = max(address + len(code) for address, code in rows)
    blob = bytearray(end)
    occupied = bytearray(end)
    for address, code in rows:
        for index, value in enumerate(code, address):
            if occupied[index]:
                raise ValueError(f"{path}: overlapping byte at 0x{index:x}")
            occupied[index] = 1
            blob[index] = value
    if not all(occupied):
        raise ValueError(f"{path}: fixture has byte gaps")
    text_line = next((line for line in text.splitlines() if line.startswith("# text_sha256: ")), None)
    if text_line != f"# text_sha256: {digest(bytes(blob))}":
        raise ValueError(f"{path}: text identity drift")
    return bytes(blob), text.encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prn", type=Path, help="CC-RH assembler list used to refresh the fixture")
    parser.add_argument(
        "--binary", type=Path,
        help="linked .text binary whose applied relocations supply fixture bytes",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.prn:
            if args.binary is None:
                raise ValueError("--binary is required with --prn")
            blob, rows = parse_prn(args.prn)
            blob, rows = apply_linked_bytes(blob, rows, args.binary)
            expected = render(blob, rows)
        else:
            blob, expected = parse_expected(EXPECTED)
    except (OSError, ValueError, StopIteration) as exc:
        parser.exit(1, f"build_ccrh_listing_fixture: {exc}\n")
    if args.check:
        if not BINARY.is_file() or BINARY.read_bytes() != blob:
            parser.exit(1, f"stale CC-RH listing fixture: {BINARY}\n")
        if args.prn is not None and (not EXPECTED.is_file() or EXPECTED.read_bytes() != expected):
            parser.exit(1, f"stale CC-RH listing oracle: {EXPECTED}\n")
        print(f"checked CC-RH listing fixture: {len(blob)} bytes")
        return 0
    BINARY.write_bytes(blob)
    EXPECTED.write_bytes(expected)
    print(f"wrote CC-RH listing fixture: {len(blob)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
