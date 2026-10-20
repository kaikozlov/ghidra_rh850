#!/usr/bin/env python3
"""Camry image, ROM, and retained original-byte scenario assertions."""
from __future__ import annotations

import ctypes
import os
import signal
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.project.analysis_target import target as resolve_target
from tools.targets.camry.decomp.tree import image_summary, load_matched, load_oracles, load_symbols
from tools.targets.camry.decomp.execution.build import bind, compile_sources
from tools.targets.camry.decomp.execution.calls import call_matched, corpus_returns, with_registers
from tools.targets.camry.decomp.execution.checks import check_call_sequence, check_results, useful_oracle
from tools.targets.camry.decomp.execution.memory import (
    attach_dcra,
    attach_dcra_window,
    install_address_space,
    install_regions,
    materialize,
    scenario_regions,
    view_of,
)


ROM_TABLES = (
    ("nvm_descriptors", 0x27634, 123 * 6),
    ("nvm_logical_descriptors", 0x26C0C, 124 * 16),
)


ROM_BYTES = (
    ("nvm_family0_request_cell_count", 0x2AD8A),
    ("nvm_family1_request_cell_count", 0x2AD8B),
)


def check_rom(library: ctypes.CDLL) -> None:
    metadata = resolve_target("camry-8965F3307000")[1]
    image = (REPO_ROOT / metadata["codeflash"]).read_bytes()
    for name, address, size in ROM_TABLES:
        actual = bytes((ctypes.c_uint8 * size).in_dll(library, name))
        if actual != image[address : address + size]:
            raise SystemExit(f"{name} drifted from CodeFlash {address:#x}")
    for name, address in ROM_BYTES:
        actual = ctypes.c_uint8.in_dll(library, name).value
        if actual != image[address]:
            raise SystemExit(f"{name} drifted from CodeFlash {address:#x}")


def _only_names(argv: list[str]) -> set[str] | None:
    """Names from ``--only-file=PATH``, or None when the whole retained suite runs."""
    for arg in argv[1:]:
        if not arg.startswith("--only-file="):
            continue
        path = Path(arg.split("=", 1)[1])
        return {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
    return None


def main() -> int:
    only = _only_names(sys.argv)
    symbols = load_symbols()
    report = image_summary(symbols)
    print(
        f"PASS image: {report['functions']} functions, "
        f"{report['function_bytes']} function bytes, "
        f"{report['gap_bytes']} gap bytes"
    )
    matched = {int(row["addr"], 16): row for row in load_matched()}
    symbol_names = {int(row["addr"], 16): row["name"] for row in symbols}
    checked_status = {"equivalent", "byte-matched"}
    for address, row in matched.items():
        if symbol_names.get(address) != row["name"]:
            raise SystemExit(f"matched name drift at {row['addr']}")
        if row["status"] not in checked_status | {"converted", "unconvertible"}:
            raise SystemExit(f"unknown match status {row['status']}")
    checked = {
        address: row for address, row in matched.items() if row["status"] in checked_status
    }
    executed = {address: 0 for address in checked}
    metadata = resolve_target("camry-8965F3307000")[1]
    codeflash = bytearray((REPO_ROOT / metadata["codeflash"]).read_bytes())
    lifted_source = None
    if any(row.get("form") == "lifted" for row in checked.values()):
        from tools.targets.camry.decomp.lifting.emit import LIFTED_C
        from tools.targets.camry.decomp.lifting.workflow import run

        run("emit")
        lifted_source = LIFTED_C
    with tempfile.TemporaryDirectory(prefix="camry-decomp-") as directory:
        library = compile_sources(Path(directory), lifted=lifted_source)
        bind(library, lifted=lifted_source is not None)
        check_rom(library)
        print("PASS rom tables match CodeFlash")
        code_view = view_of(codeflash)
        failed = False
        for scenario in load_oracles():
            entry = scenario.get("entry", {})
            if entry.get("scope") != "resolved-address":
                continue
            address = int(entry["address"], 16)
            if address not in checked or not useful_oracle(scenario):
                continue
            name = checked[address]["name"]
            if only is not None and name not in only:
                continue
            form = checked[address].get("form")
            signature = checked[address].get("signature")
            lifted = form == "lifted"
            corpus = form == "corpus"
            registers = scenario.get("registers", {})
            mapped = materialize(scenario)
            limit = int(scenario.get("max_instructions") or 200000)
            if mapped is not None:
                memory, base = mapped

            def attempt() -> None:
                if mapped is None:
                    regions = scenario_regions(scenario)
                    held = install_regions(library, code_view, len(codeflash), regions)
                    dcra, dcra_view = attach_dcra(library, name)
                    if lifted and dcra is None and 1 + len(regions) < 64:
                        dcra, dcra_view = attach_dcra_window(library)
                    returned = call_matched(
                        library, form, address, name, registers, limit, signature, scenario,
                    )
                    check_call_sequence(library, scenario)
                    check_results(
                        scenario, name, None, 0, with_registers(library, registers), returned, regions, codeflash, dcra,
                        value_return=corpus_returns(form, name, signature) if corpus or lifted else None,
                    )
                    del held, dcra_view
                else:
                    view = view_of(memory) if memory else view_of(bytearray(b"\x00"))
                    install_address_space(library, code_view, len(codeflash), view, base, memory)
                    dcra, dcra_view = attach_dcra(library, name)
                    if lifted and dcra is None:
                        dcra, dcra_view = attach_dcra_window(library)
                    returned = call_matched(
                        library, form, address, name, registers, limit, signature, scenario,
                    )
                    check_call_sequence(library, scenario)
                    check_results(
                        scenario, name, memory, base, with_registers(library, registers), returned, codeflash=codeflash, dcra=dcra,
                        value_return=corpus_returns(form, name, signature) if corpus or lifted else None,
                    )
                    del dcra_view

            read_fd, write_fd = os.pipe()
            pid = os.fork()
            if pid == 0:
                os.close(read_fd)
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                signal.alarm(30)
                try:
                    attempt()
                except BaseException as exc:
                    try:
                        os.write(write_fd, str(exc).encode()[:400])
                    except OSError:
                        pass
                    os._exit(1)
                os._exit(0)
            os.close(write_fd)
            _pid, status = os.waitpid(pid, 0)
            detail = os.read(read_fd, 400).decode(errors="replace")
            os.close(read_fd)
            if not (os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0):
                failed = True
                print(f"FAIL {name} {scenario['name']} {detail or 'aborted'}", flush=True)
                continue
            executed[address] += 1
            print(f"PASS {name} {scenario['name']}", flush=True)
    missing = [
        row["name"] for address, row in checked.items()
        if executed[address] == 0 and (only is None or row["name"] in only)
    ]
    if failed or missing:
        detail = "matched functions with no executed oracle: " + ", ".join(missing) if missing else "oracle mismatches"
        raise SystemExit(detail)
    print(f"PASS matched functions: {len(checked)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
