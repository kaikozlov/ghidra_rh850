"""Oracle-gated instruction-lift reporting, emission, and promotion workflow."""
from __future__ import annotations

from tools import REPO_ROOT
import json
from tools.project.analysis_target import target as resolve_target

from .. import tree
from .emit import LIFTED_C, emit_c
from .graph import closure_of, decode_all, liftable_set, load_image



def useful_oracle(scenario: dict) -> bool:
    checks = scenario.get("checks") or []
    has_r10 = any(check.get("kind") == "register" and check.get("register") == "r10" for check in checks)
    has_state = any(
        check.get("kind") == "register" and (
            check.get("register") in tree.SYSTEM_REGISTERS
            or check.get("register") in ("PSW", "PMR", "CDBCR", "ICCTRL")
        ) for check in checks
    )
    has_memory = any(check.get("kind") == "memory" for check in checks)
    has_event = any(check.get("kind") == "event-count" for check in checks)
    if has_event and not has_r10:
        return False
    return has_memory or has_r10 or has_state


def oracle_blocked(scenario: dict) -> bool:
    registers = scenario.get("registers") or {}
    lp = int(registers.get("lp", "0"), 16)
    stops = {int(value, 16) for value in scenario.get("stop_addresses") or []}
    if stops != {lp}:
        return True
    for check in scenario.get("checks") or []:
        if check.get("kind") != "register":
            continue
        register = check.get("register")
        if register in {"r10", "sp", "PC"}:
            continue
        expected = int(check["equals"], 16)
        actual = int(registers.get(register, "0"), 16)
        if actual != expected:
            return True
    return False


def candidate_entries(oracles: list[dict], matched: set[int], liftable: set[int]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = {}
    for scenario in oracles:
        entry = scenario.get("entry") or {}
        if entry.get("scope") != "resolved-address":
            continue
        address = int(entry["address"], 16)
        grouped.setdefault(address, []).append(scenario)
    chosen: dict[int, list[dict]] = {}
    for address, scenarios in grouped.items():
        if address in matched or address not in liftable:
            continue
        useful = [scenario for scenario in scenarios if useful_oracle(scenario)]
        if not useful or any(oracle_blocked(scenario) for scenario in useful):
            continue
        chosen[address] = useful
    return chosen


def run(operation: str) -> int:
    image = load_image()
    symbols = tree.load_symbols()
    decoded, unknown = decode_all(image, symbols)
    liftable = liftable_set(decoded)
    matched = {
        int(row["addr"], 16)
        for row in tree.load_matched()
        if row.get("status") in {"equivalent", "byte-matched"}
    }
    oracles = tree.load_oracles()
    candidates = candidate_entries(oracles, matched, liftable)
    seeds = set(candidates) | (matched & liftable)
    closed = closure_of(seeds, decoded, liftable)
    if operation == "report":
        print(f"decoded {len(decoded)} / {len(symbols)}")
        print(f"liftable {len(liftable)}")
        print(f"full-return candidates {len(candidates)}")
        print(f"matched liftable {len(matched & liftable)} / {len(matched)}")
        print(f"closure {len(closed)}")
        print("unknown heads:")
        for (hw0, hw1, op), count in unknown.most_common(12):
            print(f"  {count:5d}  hw0={hw0:04x} hw1={hw1:04x} op0510={op:02x}")
        return 0
    emit_c(decoded, closed, LIFTED_C)
    print(f"emitted {len(closed)} functions ({len(candidates)} candidates) to {LIFTED_C}")
    if operation == "emit":
        return 0
    names = {int(row["addr"], 16): row["name"] for row in symbols}
    return run_check(candidates, names, matched & liftable, oracles)


def run_check(candidates: dict[int, list[dict]], names: dict[int, str], validate: set[int], oracles: list[dict]) -> int:
    import ctypes
    import tempfile
    from pathlib import Path

    from ..execution.build import bind, compile_sources
    from ..execution.calls import call_lifted
    from ..execution.checks import check_results
    from ..execution.memory import (
        DCRA1_BASE,
        DCRA1_SIZE,
        install_address_space,
        install_regions,
        materialize,
        scenario_regions,
        view_of,
    )

    metadata = resolve_target(tree.TARGET)[1]
    codeflash = bytearray((REPO_ROOT / metadata["codeflash"]).read_bytes())
    by_entry: dict[int, list[dict]] = {}
    for scenario in oracles:
        entry = scenario.get("entry") or {}
        if entry.get("scope") != "resolved-address":
            continue
        by_entry.setdefault(int(entry["address"], 16), []).append(scenario)

    import os

    failures = 0
    passed_new = []
    with tempfile.TemporaryDirectory(prefix="camry-lift-") as directory:
        library = compile_sources(Path(directory), optimize="-O1", lifted=LIFTED_C)
        bind(library, lifted=True)
        code_view = view_of(codeflash)

        def run_scenario(address: int, name: str, scenario: dict) -> str | None:
            if not useful_oracle(scenario) or oracle_blocked(scenario):
                return None
            registers = scenario.get("registers") or {}
            limit = int(scenario.get("max_instructions") or 200000)
            mapped = materialize(scenario)
            try:
                if mapped is None:
                    regions = scenario_regions(scenario)
                    if 1 + len(regions) + 1 > 8:
                        return "region cap"
                    held = install_regions(library, code_view, len(codeflash), regions)
                    dcra, dcra_view = attach_dcra_force(library)
                    returned = call_lifted(library, address, registers, limit)
                    check_results(scenario, name, None, 0, registers, returned, regions, codeflash, dcra, value_return=True)
                    del held, dcra_view
                else:
                    memory, base = mapped
                    view = view_of(memory) if memory else view_of(bytearray(b"\x00"))
                    install_address_space(library, code_view, len(codeflash), view, base, memory)
                    dcra, dcra_view = attach_dcra_force(library)
                    returned = call_lifted(library, address, registers, limit)
                    check_results(scenario, name, memory, base, registers, returned, codeflash=codeflash, dcra=dcra, value_return=True)
                    del dcra_view
            except AssertionError as exc:
                return str(exc)
            return None

        def attach_dcra_force(library):
            window = bytearray(DCRA1_SIZE)
            view = view_of(window)
            library.camry_host_add(DCRA1_BASE, ctypes.cast(view, ctypes.POINTER(ctypes.c_uint8)), DCRA1_SIZE)
            return window, view

        def isolated(address: int, name: str, scenario: dict) -> str | None:
            pid = os.fork()
            if pid == 0:
                try:
                    message = run_scenario(address, name, scenario)
                except Exception as exc:
                    print(f"EXC {name} {scenario['name']}: {exc}", flush=True)
                    os._exit(3)
                if message:
                    print(f"FAIL {name} {scenario['name']}: {message}", flush=True)
                    os._exit(2)
                os._exit(0)
            _pid, status = os.waitpid(pid, 0)
            if os.WIFSIGNALED(status):
                return f"signal {os.WTERMSIG(status)}"
            if os.WEXITSTATUS(status) == 0:
                return None
            return "failed"

        print(f"validating {len(validate)} matched functions", flush=True)
        for address in sorted(validate):
            name = names[address]
            print(f"validate {name}", flush=True)
            for scenario in by_entry.get(address, []):
                message = isolated(address, name, scenario)
                if message:
                    failures += 1
                    if message != "failed":
                        print(f"FAIL matched {name} {scenario['name']}: {message}", flush=True)
                    if failures > 12:
                        print("stopping after 12 validation failures")
                        return 1
        if failures:
            return 1
        print("matched liftable oracles passed", flush=True)
        for address, scenarios in sorted(candidates.items()):
            name = names[address]
            print(f"candidate {name}", flush=True)
            ok = True
            for scenario in scenarios:
                message = isolated(address, name, scenario)
                if message:
                    ok = False
                    if message != "failed":
                        print(f"FAIL new {name} {scenario['name']}: {message}", flush=True)
                    break
            if ok:
                passed_new.append((address, name))
        print(f"new passes {len(passed_new)} / {len(candidates)}")
    if not passed_new:
        return 0
    path = tree.ROOT / "matched.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        for address, name in passed_new:
            handle.write(json.dumps({"addr": f"0x{address:x}", "name": name, "status": "equivalent", "form": "lifted"}) + "\n")
    print(f"recorded {len(passed_new)} lifted functions")
    return 0

