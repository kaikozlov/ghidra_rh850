"""Differential oracle command workflow for converted Camry functions."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from tools import REPO_ROOT
from tools.targets.camry.decomp.tree import CANDIDATES, COMMON_HEADER, ROOT
from tools.targets.camry.decomp.syntax import _c_signature
from tools.targets.camry.decomp.abi import _walk_boot_relocated_abi
import ctypes
from collections import defaultdict
from tools.targets.camry.decomp.lifting.graph import gap_thunks
import json
from tools.targets.camry.decomp.lifting.graph import load_image
from tools.targets.camry.decomp.tree import load_matched
from tools.targets.camry.decomp.tree import load_symbols
from tools.targets.camry.decomp.execution.calls import parse_signature
import re
from tools.project.analysis_target import target as resolve_target
import tempfile
from tools.targets.camry.decomp.execution.checks import useful_oracle
from tools.targets.camry.decomp.lifting.graph import walk_symbol
from tools.targets.camry.decomp.execution import scenario as scenario_state
from tools.targets.camry.decomp.c_text import _mask_comments
from tools.targets.camry.decomp.execution.host_rewrite import (
    _fill_local_arrays,
    _halt_nonvoid,
    _seed_incoming_locals,
    _unsigned_zero_extended_params,
    rewrite_host_body,
)
from tools.targets.camry.decomp.execution.link import (
    _compile,
    _diagnostic,
    _drop_unlinked,
    _error_names,
    _linkable,
    _macro_names,
    _prototypes,
    _undefined_symbols,
)
from tools.targets.camry.decomp.execution.machine import _Machine, _can_return
from tools.targets.camry.decomp.execution.model import (
    FAIL_KINDS,
    Harness,
    MAX_BODY,
    Planned,
    REASONS,
    Run,
)
from tools.targets.camry.decomp.execution.native import _host_compare
from tools.targets.camry.decomp.promotion import _keep_verified, _promote, _restore, _with_indirect_support
from tools.targets.camry.decomp.execution.scenario import (
    _bounded_edges,
    _finalize,
    _judge,
    _note_mmio_bases,
    _params_of,
    _place_harness,
    _pointer_bases,
    _returns_read_by_callers,
    _scenario,
    _scenario_windows,
    _sim_chunks,
)
from tools.targets.camry.decomp.sources import _load_bodies, _src_definitions, retained_paths
from tools.targets.camry.decomp.tree import TARGET


_HOST_INTRINSICS = ("__disable_irq", "__enable_irq", "__synchronize")


def _unmodeled_intrinsic(body: str) -> bool:
    calls = re.findall(r"\b(__[A-Za-z_]\w*)\s*\(", _mask_comments(body))
    return any(name not in _HOST_INTRINSICS for name in calls)


def run_oracles() -> int:
    metadata = resolve_target(TARGET)[1]
    code = load_image()
    data_base = int(metadata["dataflash_base"], 16)
    data = (REPO_ROOT / metadata["dataflash"]).read_bytes()
    symbols = load_symbols()
    status = {int(row["addr"], 16): row for row in load_matched()}
    bodies, duplicates = _load_bodies(candidates=True)
    addresses = {row["name"]: int(row["addr"], 16) for row in symbols}
    bounded_names: set[str] = set()
    host_bodies = {
        name: rewrite_host_body(
            text, addresses, zero_extend=False, halt_return=False, bounded=bounded_names,
        )
        for name, text in bodies.items()
    }
    host_bodies = {
        name: _halt_nonvoid(_fill_local_arrays(_seed_incoming_locals(
            _unsigned_zero_extended_params(text, addresses),
        )))
        for name, text in host_bodies.items()
    }
    linked = set(_src_definitions())
    functions = {}
    for row in symbols:
        fn = walk_symbol(code, row) or _walk_boot_relocated_abi(code, row)
        if fn is not None:
            functions[fn.entry] = fn
    occupied = {inst.addr for fn in functions.values() for inst in fn.insts}
    for thunk in gap_thunks(code, symbols):
        if thunk.entry in functions or any(inst.addr in occupied for inst in thunk.insts):
            continue
        functions[thunk.entry] = thunk
        occupied.update(inst.addr for inst in thunk.insts)
        linked.add(thunk.name)
    scenario_state._CONSUMED_RETURNS = _returns_read_by_callers(functions)
    machine = _Machine(code, data, data_base, functions)
    machine.bounded_entries = {
        addresses[name] for name in bounded_names if name in addresses
    }
    counts: Counter[str] = Counter()
    examples: dict[str, str] = {}
    planned: list[Planned] = []
    seen: set[object] = set()
    focus = {"addr": None}

    def reject(kind: str, name: str, detail: str = "", address: int | None = None) -> None:
        key = address if address is not None else focus["addr"]
        if key is None:
            key = name
        if key in seen:
            return
        seen.add(key)
        if detail and kind in {"unmodeled", "simulator"}:
            label = f"{kind} {detail}".strip()
        else:
            label = kind
        counts[label] += 1
        examples.setdefault(label, name)

    verified = converted = unconvertible = 0
    for row in symbols:
        address = int(row["addr"], 16)
        state = status.get(address, {})
        kind = state.get("status")
        if kind == "equivalent":
            verified += 1
            continue
        if kind == "unconvertible":
            unconvertible += 1
            continue
        converted += 1
        name = row["name"]
        focus["addr"] = address
        if address >= len(code) and address not in machine.boot_copies:
            reject("outside-codeflash", name)
            continue
        if row["size"] > MAX_BODY:
            reject("large", name)
            continue
        if name in duplicates:
            reject("duplicate-body", name)
            continue
        if name not in bodies:
            reject("no-converted-body", name)
            continue
        body = bodies[name]
        if _unmodeled_intrinsic(body):
            reject("host-intrinsic", name)
            continue
        fn = functions.get(address)
        if fn is None:
            reject("undecoded", name)
            continue
        try:
            signature = _c_signature(body)
            pointers = _pointer_bases(fn, _params_of(signature, name))
        except (AssertionError, Harness, ValueError) as exc:
            reject(getattr(exc, "kind", "stack-arguments"), name, getattr(exc, "detail", ""))
            continue
        texts = [body]
        for inst in fn.insts:
            if inst.kind != "jarl":
                continue
            callee = functions.get(inst.target)
            if callee is not None and callee.name in bodies and bodies[callee.name] not in texts:
                texts.append(bodies[callee.name])
        (
            machine.stack_lo,
            machine.stack_hi,
            machine.entry_sp,
            machine.arg_base,
            machine.arg_slots,
            machine.relocated,
        ) = _place_harness(texts, len(pointers))
        runs = []
        failed = False
        skipped = "instruction-budget"
        root_returns = _can_return(fn)
        for index, fill in ((0, 0), (1, 0xA5)):
            params = [
                (pointer, 0 if index == 0 or pointer else index + ordinal)
                for ordinal, pointer in enumerate(pointers)
            ]
            # Integer scenario B uses 1, 2, 3, 4. Pointers stay at the buffers.
            if index == 1:
                params = [
                    (pointer, ordinal + 1)
                    for ordinal, pointer in enumerate(pointers)
                ]
            if address == 0x76B6:
                params[1] = (False, 0xC4 if index else 0)
            # Real caller tables (0x34ca2/0x34cac and 0x3207c), not
            # unterminated scratch. Fill B walks to the ROM 0x7fff sentinel.
            if address == 0x70208:
                params[:2] = [(False, 0x30F0C), (False, 1280 if index else 832)]
            elif address == 0x7025C:
                params[:2] = [(False, 0x30E78), (False, 25600 if index else 0)]
            elif address == 0x73A5C:
                params[:3] = [(False, 2 if index else 0), (False, 0xFFFFFFFF), (False, 0x2758C)]
            elif address == 0x78212:
                # 78304 selects these two immutable state-machine records
                # through 27cc0/27cc4. Their (state 0, event 0) entries both
                # select callback 0; scratch is not a callback-table record.
                params[0] = (False, 0x27C0C if index else 0x27BA4)
                params[3:] = [(False, 0), (False, 0)]
            elif address == 0x7F444:
                # 813e4 maps logical handles starting at 21a48's value 5
                # through 21a68/21fe8. Handles 0/1 return the invalid 0xff
                # route, which 7f444 cannot use as its callback-table index.
                params[0] = (False, 5 + index)
            elif address == 0xD0768:
                params[:2] = [(False, 0xB001A), (False, 153 if index else 0)]
            elif address == 0xD07BA:
                params[:2] = [(False, 0xB1356), (False, 10000 if index else 0)]
            elif address == 0xD07F2:
                params[:2] = [(False, 0xB0518), (False, 0x7FFF if index else 0)]
            elif address == 0xD1DE4:
                params[:2] = [(False, 0xAEE7C), (False, 0x7FFF if index else 0)]
            # DAT_21970 configures only controller 0; 21938 is adjacent code,
            # not a second controller slot. Keep both RAM fills in-domain.
            elif address == 0x7CC60:
                # 7ce24 passes a boolean fault-bit test as the second argument.
                params[:2] = [(False, 0), (False, index)]
            elif address == 0x8015C:
                # 8025a/803b0 pass route and its matching ten-byte ROM row.
                route = 4 if index else 0
                params[:3] = [(False, 0), (False, route), (False, 0x21ACC + route * 10)]
            try:
                runs.append(machine.execute(fn, params, fill, bound=name in bounded_names))
            except Harness as exc:
                # A non-returning fill that never reaches its back-edge stays
                # uncompared. The fill that does stop is still checked.
                if exc.kind == "instruction-budget" and (not root_returns or name in bounded_names):
                    if exc.detail:
                        skipped = f"instruction-budget {exc.detail}"
                    continue
                if exc.kind == "fill-target":
                    skipped = "external-branch"
                    continue
                # A store into the vector page is a null or integer element
                # pointer. That fill is not comparable. A real const-table
                # store, such as 0x80f64, still rejects the function.
                if exc.kind == "code-write":
                    try:
                        written = int(exc.detail, 16)
                    except ValueError:
                        written = 0x100
                    if written < 0x100:
                        skipped = "code-write"
                        continue
                label = exc.kind
                if exc.kind == "instruction-budget" and exc.detail:
                    label = f"instruction-budget {exc.detail}"
                reject(label, name, exc.detail)
                failed = True
                break
        if failed:
            continue
        if not runs:
            reject(skipped, name)
            continue
        texts = [body]
        for target in set().union(*(run.calls for run in runs)):
            callee = functions.get(target)
            if callee is not None and callee.name in bodies:
                texts.append(bodies[callee.name])
        _note_mmio_bases(runs, texts)
        # The bytes address gp+disp. The C holds camry_host_ptr(gp) and indexes it.
        cover = (
            [runs[0].gp]
            if any(f"camry_host_ptr(0x{runs[0].gp:x}u)" in text for text in texts)
            else None
        )
        try:
            try:
                return_type, _ignored = parse_signature(signature, name)
            except (AssertionError, ValueError):
                return_type = ""
            windows = _scenario_windows(
                runs, pointers, cover, void_return=return_type == "void",
            )
        except Harness as exc:
            reject(exc.kind, name, exc.detail)
            continue
        calls = set().union(*(run.calls for run in runs))
        if any(
            functions[target].name not in bodies and functions[target].name not in linked
            for target in calls
            if target in functions
        ):
            reject("no-converted-body", name)
            continue
        planned.append(Planned(
            address, name, signature, body, runs, calls, windows, pointers,
            bounded=name in bounded_names,
        ))

    focus["addr"] = None
    print(f"harnessed {len(planned)}", flush=True)
    # A function-pointer target is not a textual call. Link every converted
    # body so camry_indirect can reach it. Names already defined in src/*.c
    # are skipped by the compiler.
    needed = list(bodies)
    # Keep only roots whose whole executed closure is in the compiled set.
    dropped: set[str] = set()
    stubs: dict[str, str] = {}
    header = CANDIDATES / "common.h"
    if not header.is_file():
        header = COMMON_HEADER
    prototypes = _prototypes(header)
    provided: set[str] = set()
    failed_states: set[tuple[frozenset[str], frozenset[str], frozenset[str]]] = set()
    with tempfile.TemporaryDirectory(prefix="camry-oracle-") as directory:
        directory_path = Path(directory)
        def state_of(names: list[str]) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
            return (frozenset(names), frozenset(stubs), frozenset(provided))

        def fit(names: list[str]) -> tuple[ctypes.CDLL | None, list[str]]:
            names = list(dict.fromkeys(name for name in names if name not in dropped))
            if not names:
                return None, []
            state = state_of(names)
            if state in failed_states:
                for name in names:
                    dropped.add(name)
                    reject("host-compile", name)
                return None, []
            compiled, log = _compile(
                directory_path, names, host_bodies, stubs, provided, header=header,
            )
            if compiled is not None:
                return compiled, names
            failed_states.add(state)
            errors = re.findall(r"^(.+?):\d+:\d+: (?:fatal )?error:", log, re.M)
            if any(Path(path).name != "candidates.c" for path in errors):
                raise RuntimeError(f"shared host compilation failed: {_diagnostic(log)}")
            missing = _undefined_symbols(log)
            defined_now = _src_definitions() | provided
            extra = [
                name for name in missing
                if name in bodies and name not in defined_now
                and name not in dropped and name not in names
            ]
            if extra:
                grown = list(dict.fromkeys(names + extra))
                if state_of(grown) not in failed_states:
                    return fit(grown)
                # The real bodies recreate a set that already failed. Stub the
                # callees so this slice can link, and keep going.
                for name in extra:
                    if name in prototypes and name not in stubs:
                        stubs[name] = prototypes[name]
                        dropped.add(name)
                        reject("host-link", name)
                if any(name in stubs for name in extra):
                    return fit(names)
            fresh = {
                name: prototypes[name]
                for name in missing
                if name not in bodies and name not in defined_now
                and name not in stubs and name in prototypes
            }
            if fresh:
                stubs.update(fresh)
                return fit(names)
            dupes: list[str] = []
            for name in re.findall(
                r"(?:duplicate symbol '_|redefinition of ')([A-Za-z_][A-Za-z0-9_]*)",
                log,
            ):
                if name not in dupes:
                    dupes.append(name)
            if dupes:
                acted = False
                for name in dupes:
                    if name in stubs:
                        del stubs[name]
                        acted = True
                    if name not in provided:
                        provided.add(name)
                        acted = True
                if acted:
                    return fit(names)
            linked = _drop_unlinked(names, bodies, log)
            if linked:
                for name in linked:
                    dropped.add(name)
                    reject("host-link", name)
                return fit(names)
            bad = _error_names(log, names, host_bodies, provided)
            removed = [name for name in bad if name in names and name not in dropped]
            if removed:
                for name in removed:
                    dropped.add(name)
                    reject("host-compile", name)
                print(f"compile drop {len(names)} {_diagnostic(log)}", flush=True)
                return fit([name for name in names if name not in dropped])
            if len(names) == 1:
                print(_diagnostic(log), flush=True)
                dropped.add(names[0])
                reject("host-compile", names[0])
                return None, []
            mid = len(names) // 2
            print(f"compile split {len(names)} {_diagnostic(log)}", flush=True)
            left_lib, left = fit(names[:mid])
            right_lib, right = fit(names[mid:])
            del left_lib, right_lib
            union = list(dict.fromkeys(left + right))
            remaining = [name for name in names if name not in dropped]
            if len(union) == len(remaining) or state_of(union) in failed_states:
                prefer, discard = (left, right) if len(left) >= len(right) else (right, left)
                for name in discard:
                    if name not in prefer and name not in dropped:
                        dropped.add(name)
                        reject("host-compile", name)
                if not prefer:
                    return None, []
                return fit(prefer)
            return fit(union)

        library, _kept = fit([name for name in needed if name not in dropped])
        if library is None:
            for item in planned:
                reject("host-compile", item.name, address=item.address)
            _print_summary(verified, converted, unconvertible, counts, examples, 0, 0)
            return 0
        runnable = []
        for item in planned:
            closure = {functions[address].name for address in item.calls if address in functions}
            closure.add(item.name)
            if closure & dropped:
                if item.name not in dropped:
                    reject("host-link", item.name, address=item.address)
                continue
            runnable.append(item)
        if not runnable:
            _print_summary(verified, converted, unconvertible, counts, examples, 0, 0)
            return 0

        work = REPO_ROOT / "build" / "tmp" / "camry-oracle"
        if work.exists():
            for child in work.glob("*"):
                child.unlink()
        work.mkdir(parents=True, exist_ok=True)
        scenarios = []
        owners = []
        bounded_entries = [hex(entry) for entry in sorted(machine.bounded_entries)]
        bounded_edges = _bounded_edges(machine)
        for item in runnable:
            # The bytes decide which arguments are pointers. The C signature
            # omits that for a plain integer that is later used as an address,
            # and the machine would then store through 0 or 1 into CodeFlash.
            pointers = item.pointers
            windows = item.windows
            for run in item.runs:
                fill = run.fill
                index = 0 if fill == 0 else 1
                params = [
                    (pointer, 0 if index == 0 or pointer else ordinal + 1)
                    for ordinal, pointer in enumerate(pointers)
                ]
                if index == 1:
                    params = [(pointer, ordinal + 1) for ordinal, pointer in enumerate(pointers)]
                if item.address == 0x76B6:
                    params[1] = (False, 0xC4 if index else 0)
                # Match the caller-bound inputs used for the initial execution.
                if item.address == 0x70208:
                    params[:2] = [(False, 0x30F0C), (False, 1280 if index else 832)]
                elif item.address == 0x7025C:
                    params[:2] = [(False, 0x30E78), (False, 25600 if index else 0)]
                elif item.address == 0x73A5C:
                    params[:3] = [(False, 2 if index else 0), (False, 0xFFFFFFFF), (False, 0x2758C)]
                elif item.address == 0x78212:
                    params[0] = (False, 0x27C0C if index else 0x27BA4)
                    params[3:] = [(False, 0), (False, 0)]
                elif item.address == 0x7F444:
                    params[0] = (False, 5 + index)
                elif item.address == 0xD0768:
                    params[:2] = [(False, 0xB001A), (False, 153 if index else 0)]
                elif item.address == 0xD07BA:
                    params[:2] = [(False, 0xB1356), (False, 10000 if index else 0)]
                elif item.address == 0xD07F2:
                    params[:2] = [(False, 0xB0518), (False, 0x7FFF if index else 0)]
                elif item.address == 0xD1DE4:
                    params[:2] = [(False, 0xAEE7C), (False, 0x7FFF if index else 0)]
                elif item.address == 0x7CC60:
                    params[:2] = [(False, 0), (False, index)]
                elif item.address == 0x8015C:
                    route = 4 if index else 0
                    params[:3] = [(False, 0), (False, route), (False, 0x21ACC + route * 10)]
                scenario = _scenario(
                    f"camry_diff_{item.address:x}_{index}",
                    item.address,
                    run,
                    fill,
                    params,
                    windows,
                    bounded_entries,
                    bounded_edges,
                )
                path = work / f"{scenario['name']}.json"
                path.write_text(json.dumps(scenario), encoding="utf-8")
                scenarios.append(path)
                owners.append((item, run, scenario))
        reports = _sim_chunks(scenarios)
        by_scenario = {}
        for report in reports:
            by_scenario[report.get("scenario") or Path(report.get("report_path", "")).stem] = report

        passed: list[tuple[Planned, list[dict]]] = []
        fail = 0
        grouped: dict[int, list[tuple[Run, dict, dict]]] = defaultdict(list)
        for item, run, scenario in owners:
            grouped[item.address].append((run, scenario, by_scenario.get(scenario["name"], {})))
        for item in runnable:
            rows = grouped[item.address]
            ok = True
            saved = []
            for run, scenario, report in rows:
                kind = _judge(item, run, scenario, report)
                judge_detail = ""
                if kind == "simulator":
                    judge_detail = (report.get("simulator_message") or "")[:120]
                    kind = "simulator"
                if kind is None:
                    final = _finalize(item, run, scenario, report)
                    kind = _host_compare(library, item, final, code)
                    if kind is None and useful_oracle(final):
                        saved.append(final)
                if kind is not None:
                    if kind == "dropped-return":
                        print(f"disagree dropped-return {item.name} {item.address:#x}", flush=True)
                    reject(kind, item.name, judge_detail, address=item.address)
                    if kind in FAIL_KINDS:
                        fail += 1
                    ok = False
                    break
            if ok and saved:
                passed.append((item, saved))
            elif ok:
                reject("no-observable", item.name, address=item.address)
        del library

    if not passed:
        _print_summary(verified, converted, unconvertible, counts, examples, 0, fail)
        return 0

    snapshots = {
        path: path.read_text(encoding="utf-8") if path.exists() else None
        for path in (ROOT / "matched.jsonl", ROOT / "oracles.jsonl", COMMON_HEADER, *retained_paths())
    }
    defined = _src_definitions() | set(stubs)
    symbols_names = {row["name"] for row in symbols}
    macros = _macro_names(header)
    linked_indirect: list[str] = []
    final = _keep_verified(
        passed, snapshots, bodies, defined, symbols_names, macros, reject, examples, stubs,
        linked=linked_indirect,
    )
    _restore(snapshots)
    if not final:
        _print_summary(verified, converted, unconvertible, counts, examples, 0, fail)
        return 0
    kept, support = _linkable(
        [item.name for item, _rows in final], bodies, defined, symbols_names, macros,
    )
    for item, _rows in final:
        if item.name not in kept:
            reject("host-link", item.name, address=item.address)
    final = [(item, rows) for item, rows in final if item.name in kept]
    # The chunk verifier linked these targets. Promoting without them aborts
    # the combined library on the same camry_indirect addresses.
    support = _with_indirect_support(
        [item.name for item, _rows in final], support, bodies,
    )
    support.extend(name for name in linked_indirect if name not in support)
    # _keep_verified already ran the retained suite once for this batch.
    _promote(final, support, bodies, stubs)
    _print_summary(
        verified + len(final),
        converted - len(final),
        unconvertible,
        counts,
        examples,
        len(final),
        fail,
    )
    return 0


def _print_summary(
    verified: int,
    converted: int,
    unconvertible: int,
    counts: Counter[str],
    examples: dict[str, str],
    passed: int,
    failed: int,
) -> None:
    not_runnable = sum(
        count for kind, count in counts.items()
        if kind.split()[0] not in FAIL_KINDS | {"verifier"}
    )
    print(f"functions {verified + converted + unconvertible}")
    print(f"oracle-verified {verified}")
    print(f"converted-unverified {converted}")
    print(f"unconvertible {unconvertible}")
    print(f"pass {passed}")
    print(f"fail {failed}")
    print(f"not-runnable {not_runnable}")
    print("failure classes:")
    for kind, count in counts.most_common(30):
        base = kind.split()[0]
        reason = REASONS.get(base, REASONS.get(kind, ""))
        example = examples.get(kind, "")
        extra = (
            f" ({kind.split(' ', 1)[1][:100]})"
            if base in {"unmodeled", "simulator", "harness-drift", "host-fault", "instruction-budget"} and " " in kind
            else ""
        )
        print(f"  {count:5d}  {base}{extra}  {example}")
        if reason:
            print(f"         {reason}")

