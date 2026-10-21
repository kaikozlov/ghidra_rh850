"""Planning, capturing, and judging original-byte machine scenarios."""
from __future__ import annotations

from tools.targets.camry.decomp.lifting.decode import Inst
from tools.emulation.p1me_machine import P1MEMachineError
from pathlib import Path
from tools import REPO_ROOT
from tools.targets.camry.decomp.syntax import _c_signature
from tools.targets.camry.decomp.syntax import _stmt_parts
from tools.targets.camry.decomp.lifting.graph import load_image
from tools.targets.camry.decomp.tree import load_symbols
from tools.targets.camry.decomp.execution.calls import parse_signature
import re
from tools.targets.camry.decomp.lifting.graph import walk_symbol
from tools.targets.camry.decomp.execution.machine import _Machine, _direct_target
from tools.targets.camry.decomp.execution.model import (
    ARG_BASE,
    ARG_COUNT,
    ARG_STRIDE,
    DATA_REGIONS,
    ENTRY_SP,
    Harness,
    POLL_STEP_LIMIT,
    Planned,
    REASONS,
    Run,
    SCRATCH,
    SCRATCH_SIZE,
    SENTINEL,
    SIM_CHUNK,
    STACK_HI,
    STACK_LO,
    STOP,
    _HOST_PTR,
    _covers_mapped,
    _space,
)
from tools.targets.camry.decomp.sources import _load_bodies
from tools.targets.camry.decomp.tree import TARGET


def _params_of(signature: str, name: str) -> list[bool]:
    _return_type, params = parse_signature(signature, name)
    # r6-r9 plus the 0x200 bytes above the entry SP.
    if len(params) > 32:
        raise Harness("stack-arguments")
    return ["*" in param for param in params]


_POINTER_MAP: dict[int, list[bool]] | None = None


def _param_source(origin: set) -> int | None:
    if len(origin) != 1:
        return None
    item = next(iter(origin))
    if item[0] == "entry" and item[1] >= 6:
        return item[1] - 6
    return None


def _local_pointer_bases(fn, pointers: list[bool]) -> tuple[list[bool], list[tuple[int, list[int | None]]]]:
    """Pointer parameters used locally or forwarded to recovered callees."""
    from tools.targets.camry.decomp.abi import _argument_origin, _call_facts

    facts = _call_facts()
    # These are _function_origins instruction-entry states, including stack
    # arguments and the callee-specific register clobbers.
    states = facts["origins"][fn.name]
    width = max(4, len(pointers), facts["params"].get(fn.name, 0))
    pointed = list(pointers) + [False] * (width - len(pointers))
    calls: list[tuple[int, list[int | None]]] = []
    memory = {"ld8s", "ld8u", "ld16s", "ld16u", "ld32", "st8", "st16", "st32"}
    for inst in fn.insts:
        state = states.get(inst.addr)
        if state is None:
            continue
        parsed = _stmt_parts(inst.stmt) if inst.stmt else None
        if parsed is None:
            continue
        name, args = parsed
        base = None
        if name in memory and len(args) >= 2 and isinstance(args[1], int):
            base = args[1]
        elif name in {"set1", "not1", "clr1", "tst1"} and args and isinstance(args[0], int):
            base = args[0]
        if base is not None:
            source = _param_source(state.get(base, set()))
            if source is not None and source < len(pointed):
                pointed[source] = True
    # The shared call facts resolve immutable indirect calls and tail jumps.
    for target, addresses in facts["sites"].get(fn.name, {}).items():
        count = facts["params"].get(facts["names"][target], 0)
        for address in addresses:
            state = states.get(address, {})
            calls.append((target, [
                _param_source(_argument_origin(state, index))
                for index in range(count)
            ]))
    return pointed, calls


def _pointer_map() -> dict[int, list[bool]]:
    """Parameters that are pointers here or in a recovered callee."""
    global _POINTER_MAP
    if _POINTER_MAP is not None:
        return _POINTER_MAP
    from tools.targets.camry.decomp.lifting.graph import load_image, walk_symbol

    image = load_image()
    bodies, _duplicates = _load_bodies()
    functions = {}
    signatures: dict[int, list[bool]] = {}
    for row in load_symbols():
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        functions[fn.entry] = fn
        body = bodies.get(row["name"])
        if body is None:
            signatures[fn.entry] = []
            continue
        try:
            signatures[fn.entry] = _params_of(_c_signature(body), row["name"])
        except (AssertionError, Harness, ValueError):
            signatures[fn.entry] = []
    local: dict[int, list[bool]] = {}
    calls: dict[int, list[tuple[int, list[int | None]]]] = {}
    for entry, fn in functions.items():
        seed = signatures.get(entry, [])
        pointed, sites = _local_pointer_bases(fn, seed)
        local[entry] = pointed
        calls[entry] = sites
    changed = True
    while changed:
        changed = False
        for entry, sites in calls.items():
            flags = local[entry]
            for target, args in sites:
                callee = local.get(target)
                if callee is None:
                    continue
                for index, source in enumerate(args):
                    if source is None or index >= len(callee) or source >= len(flags):
                        continue
                    if callee[index] and not flags[source]:
                        flags[source] = True
                        changed = True
    _POINTER_MAP = local
    return local


def _pointer_bases(fn, pointers: list[bool]) -> list[bool]:
    """An integer parameter the bytes use as an address still needs a mapped buffer."""
    pointed = list(pointers)
    extra = _pointer_map().get(fn.entry, [])
    for index, flag in enumerate(extra):
        if flag and index < len(pointed):
            pointed[index] = True
    return pointed


def _return_width(return_type: str) -> int:
    if "*" in return_type:
        return 32
    if return_type in {"byte", "uchar", "uint8_t", "undefined1", "char", "bool"}:
        return 8
    if return_type in {"ushort", "short", "uint16_t", "int16_t", "undefined2"}:
        return 16
    return 32


def _observable(run: Run, void_return: bool = False) -> bool:
    for addr, size in run.writes:
        if not (run.stack_lo <= addr and addr + size <= run.stack_hi):
            return True
    if run.system_outputs:
        return True
    # A void body does not expose r10. The scratch canary is the check.
    if void_return:
        return False
    # A write of the incoming sentinel is not distinguishable from r10 being untouched.
    return bool(run.r10_written and run.regs[10] != SENTINEL)


def _clusters(spans: list[tuple[int, int]], gap: int) -> list[tuple[int, int]]:
    if not spans:
        return []
    ordered = sorted(spans)
    start, end = ordered[0][0], ordered[0][0] + ordered[0][1]
    packed = []
    for addr, size in ordered[1:]:
        if addr <= end + gap:
            end = max(end, addr + size)
            continue
        packed.append((start, end - start))
        start, end = addr, addr + size
    packed.append((start, end - start))
    return packed


def _span(spans: list[tuple[int, int]]) -> tuple[int, int] | None:
    if not spans:
        return None
    start = min(addr for addr, _size in spans)
    end = max(addr + size for addr, size in spans)
    return start, end - start


def _cover_objects(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Map the whole named object when a field access uses its base pointer.

    ``slots[i].armed`` calls ``camry_host_ptr`` on the object base, while the
    bytes only touch the field. The base is otherwise outside the write window.
    """
    from tools.targets.camry.decomp.layout import _GP_DELTA
    from tools.targets.camry.decomp.runtime import _gp_objects, _object_sizes

    objects = list(_object_sizes().values())
    objects.extend(
        ((base - _GP_DELTA) & 0xFFFFFFFF, size)
        for _name, base, size, _expr in _gp_objects()
    )
    covered = list(spans)
    for addr, size in spans:
        end = addr + size
        for runtime, obj_size in objects:
            if addr < runtime + obj_size and runtime < end:
                covered.append((runtime, obj_size))
    return covered


_LOCAL_CONST = re.compile(r"0x(fe[bB][eEfF][0-9A-Fa-f]{4})")


def _place_harness(texts: list[str], nparams: int) -> tuple[int, int, int, int, int, bool]:
    """Stack and argument windows in local RAM this function does not address.

    The fixed windows sit on firmware globals (the argument range covers
    0xfebe3894). Pointer buffers stay 4-byte aligned.
    """
    touched: list[tuple[int, int]] = []
    for text in texts:
        for match in _LOCAL_CONST.finditer(text):
            addr = int(match.group(1), 16)
            if 0xFEBE0000 <= addr < 0xFEC00000:
                touched.append((addr, addr + 4))
        # Only the destination base is a literal. The copy still stores every
        # word through 0xfebf7c00 + (0x17df0 - 0x10000). A stack in that span
        # is dropped from the checks and reported as an extra write.
        if "0xfebf7c00" in text and "0x10000" in text and "0x17df0" in text:
            touched.append((0xFEBF7C00, 0xFEBF7C00 + (0x17DF0 - 0x10000)))
    slots = max(nparams, 1)
    span = STACK_HI - STACK_LO
    sp_from_lo = ENTRY_SP - STACK_LO
    arg_bytes = slots * ARG_STRIDE
    need = 0x2000 + arg_bytes
    cursor = (0xFEC00000 - need) & ~0xFF
    while cursor >= 0xFEBE0000:
        stack_lo = cursor
        stack_hi = cursor + span
        entry_sp = cursor + sp_from_lo
        arg_base = (cursor + 0x2000) & ~3
        arg_end = arg_base + arg_bytes
        if arg_end <= 0xFEC00000 and not any(
            not (arg_end <= start or stack_lo >= end) for start, end in touched
        ):
            return stack_lo, stack_hi, entry_sp, arg_base, slots, True
        cursor -= 0x100
    return STACK_LO, STACK_HI, ENTRY_SP, ARG_BASE, max(ARG_COUNT, slots), False


def _windows(
    runs: list[Run],
    pointers: list[bool] | None = None,
    cover: list[int] | None = None,
) -> list[tuple[int, int]]:
    """One window per RAM bank. Separate clusters overflow the host's eight regions."""
    local: list[tuple[int, int]] = []
    glob: list[tuple[int, int]] = []
    other: list[tuple[int, int]] = []
    stack = False
    arg = False
    frame = runs[0] if runs else None
    stack_lo = frame.stack_lo if frame else STACK_LO
    stack_hi = frame.stack_hi if frame else STACK_HI
    arg_base = frame.arg_base if frame else ARG_BASE
    arg_slots = frame.arg_slots if frame else ARG_COUNT
    arg_end = arg_base + arg_slots * ARG_STRIDE
    for run in runs:
        for addr, size in run.reads | run.writes:
            if stack_lo <= addr and addr + size <= stack_hi:
                stack = True
            elif arg_base <= addr and addr + size <= arg_end:
                arg = True
            else:
                space = _space(addr, size)
                if space == "code":
                    # CodeFlash is already the image. A fill window would replace it.
                    continue
                if space == "local":
                    local.append((addr, size))
                elif space == "global":
                    glob.append((addr, size))
                else:
                    other.append((addr, size))
    for addr in cover or []:
        if _space(addr, 1) == "local":
            local.append((addr, 1))
        elif _space(addr, 1) == "global":
            glob.append((addr, 1))
        else:
            other.append((addr, 1))
    if stack:
        local.append((stack_lo, stack_hi - stack_lo))
    pointer_slots = [
        arg_base + index * ARG_STRIDE
        for index, is_pointer in enumerate(pointers or [])
        if is_pointer
    ]
    if arg or pointer_slots:
        touched = [
            addr
            for run in runs
            for addr, size in run.reads | run.writes
            if arg_base <= addr < arg_end
        ]
        touched.extend(pointer_slots)
        last = max(touched)
        slot = (last - arg_base) // ARG_STRIDE + 1
        local.append((arg_base, slot * ARG_STRIDE))
    local = _cover_objects(local)
    glob = _cover_objects(glob)
    other = _cover_objects(other)
    windows = [window for window in (_span(local), _span(glob)) if window is not None]
    packed = _clusters(other, 0x400)
    if len(windows) + len(packed) > DATA_REGIONS and packed:
        start = min(addr for addr, _size in other)
        end = max(addr + size for addr, size in other)
        # Peripheral stores of one init sequence can span a few megabytes of MMIO.
        if end - start <= 0x400000 and not _covers_mapped(start, end):
            packed = [(start, end - start)]
    if len(windows) + len(packed) > DATA_REGIONS:
        raise Harness("region-cap")
    windows.extend(packed)
    return windows


def _cover(windows: list[tuple[int, int]], addr: int, size: int) -> str:
    end = addr + size
    for base, span in windows:
        if base <= addr and end <= base + span:
            return "full"
        if not (end <= base or addr >= base + span):
            return "partial"
    return "none"


def _attach_scratch(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
    cover = _cover(windows, SCRATCH, SCRATCH_SIZE)
    if cover == "full":
        return windows
    if cover == "partial" or len(windows) >= DATA_REGIONS:
        raise Harness("no-observable")
    return [*windows, (SCRATCH, SCRATCH_SIZE)]


def _note_mmio_bases(runs: list[Run], texts: list[str]) -> None:
    """The bytes may touch a field while the C takes the object's base pointer."""
    for text in texts:
        for match in _HOST_PTR.finditer(text):
            addr = int(match.group(1), 16)
            if _space(addr, 1) != "mmio":
                continue
            for run in runs:
                run.reads.add((addr, 1))


def _scenario_windows(
    runs: list[Run],
    pointers: list[bool],
    cover: list[int] | None = None,
    void_return: bool = False,
) -> list[tuple[int, int]]:
    windows = _windows(runs, pointers, cover)
    if any(_observable(run, void_return) for run in runs):
        return windows
    return _attach_scratch(windows)


def _region_fill(scenario: dict, address: int) -> int | None:
    for region in scenario.get("memory", []):
        base = int(region["address"], 16)
        if base <= address < base + int(region["size"]):
            return int(region["fill"]) & 0xFF
    return None


def _write_spans(run: Run) -> list[tuple[int, int]]:
    spans = []
    frame_lo = run.regs[3]
    if run.stack_lo <= run.regs[2] < run.entry_sp:
        frame_lo = min(frame_lo, run.regs[2])
    switched = _clusters([(lo, hi - lo) for lo, hi in run.switch_spans], 0)
    for addr, size in run.writes:
        if run.stack_lo <= addr and addr + size <= run.stack_hi:
            # SP or the scheduler's r2 can retain a live frame across a return.
            if run.halt is None or run.stack_lo <= run.regs[2] < run.entry_sp:
                start = max(addr, frame_lo)
                end = min(addr + size, run.entry_sp)
                if start < end:
                    spans.append((start, end - start))
            continue
        pieces = [(addr, addr + size)]
        for lo, length in switched:
            hi = lo + length
            # Finalization closes the current switched stack too. Only a halt
            # makes its SP frame dead; r2 still escapes a saved context frame.
            live = hi
            if run.halt is None and lo <= run.regs[3] < hi:
                live = run.regs[3]
            if lo <= run.regs[2] < hi:
                live = min(live, run.regs[2])
            pieces = [
                part
                for start, end in pieces
                for part in ((start, min(end, lo)), (max(start, live), end))
                if part[0] < part[1]
            ]
        spans.extend((start, end - start) for start, end in pieces)
    return _clusters(spans, 0)


def _bounded_edges(machine: _Machine) -> list[dict[str, str]]:
    """Back-edges where a rewritten callee returns after one iteration.

    The host copy returns from that loop. The bytes branch back. Java
    restores the caller's frame there, matching this machine.
    """
    edges = []
    for entry in sorted(machine.bounded_entries):
        fn = machine.functions.get(entry)
        if fn is None:
            continue
        for inst in fn.insts:
            target = _direct_target(inst)
            if target is None or target == inst.addr or not target < inst.addr:
                continue
            if target not in fn.sites:
                continue
            edges.append({
                "pc": hex(inst.addr),
                "target": hex(target),
                "entry": hex(entry),
            })
    return edges


def _scenario(
    name: str,
    address: int,
    run: Run,
    fill: int,
    params: list[tuple[bool, int]],
    windows: list[tuple[int, int]],
    bounded_entries: list[str] | None = None,
    bounded_edges: list[dict[str, str]] | None = None,
) -> dict:
    registers = {
        "sp": hex(run.entry_sp),
        "gp": hex(run.gp),
        "tp": hex(run.tp),
        "lp": hex(STOP),
        "PSW": "0x20",
        "PMR": "0x0",
        "MCTL": "0x2",
    }
    registers.update({name: hex(value) for name, value in run.system_inputs.items()})
    for index, (pointer, ordinal) in enumerate(params):
        if index >= 4:
            break
        value = run.arg_base + index * ARG_STRIDE if pointer else ordinal
        if pointer:
            value &= ~3
        registers[f"r{6 + index}"] = hex(value)
    checks = [{
        "name": "r10",
        "kind": "register",
        "register": "r10",
        "equals": hex(run.regs[10]),
    }]
    checks.extend({
        "name": f"system-{name}", "kind": "register", "register": name, "equals": hex(value),
    } for name, value in run.system_outputs.items())
    for reg, label in ((2, "r2"), (3, "sp"), (4, "gp"), (5, "tp"), *((reg, f"r{reg}") for reg in range(20, 30))):
        checks.append({
            "name": label,
            "kind": "register",
            "register": label,
            "equals": hex(run.regs[reg]),
        })
    spans = _write_spans(run)
    for addr, size in spans:
        checks.append({
            "name": f"mem-{addr:x}",
            "kind": "memory",
            "address": hex(addr),
            "size": size,
            "equals_hex": bytes(run.memory[addr + offset] for offset in range(size)).hex(),
        })
    if not spans and _cover(windows, SCRATCH, SCRATCH_SIZE) == "full":
        checks.append({
            "name": f"mem-{SCRATCH:x}",
            "kind": "memory",
            "address": hex(SCRATCH),
            "size": SCRATCH_SIZE,
            "equals_hex": f"{fill:02x}" * SCRATCH_SIZE,
        })
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": name,
        "entry": {"role": "generated", "scope": "resolved-address", "address": hex(address)},
        "max_instructions": max(run.steps, 1) if run.halt is not None else max(run.steps, POLL_STEP_LIMIT),
        "reset": "none",
        "gpr_fill": hex(SENTINEL),
        "registers": registers,
        "stop_addresses": [hex(run.halt if run.halt is not None else STOP)],
        "peripheral_file": True,
        "memory": [
            {"address": hex(base), "size": size, "fill": fill, "evidence": "generated"}
            for base, size in windows
        ] + [
            {
                "address": hex(addr),
                "hex": (value & 0xFFFFFFFF).to_bytes(4, "little").hex(),
                "evidence": "generated",
            }
            for addr, value in run.stack_args
        ] + [
            # The bytes loaded the fill. The host load has to see the stub
            # the machine actually called, or it enters the reset vector.
            {
                "address": hex(addr),
                "hex": (0x798).to_bytes(4, "little").hex(),
                "evidence": "generated",
            }
            for addr in dict.fromkeys(run.stub_slots)
        ] + [
            {"address": hex(addr), "hex": payload.hex(), "evidence": "original boot-copy bytes"}
            for addr, payload in run.code_regions
        ],
        "checks": checks,
    }
    if bounded_entries:
        scenario["bounded_entries"] = bounded_entries
    if bounded_edges:
        scenario["bounded_edges"] = bounded_edges
    return scenario


def _hex_bytes(run: Run, addr: int, size: int) -> str:
    return "".join(f"{run.memory.get(addr + offset, 0):02x}" for offset in range(size))


def _report_map(report: dict) -> dict[str, dict]:
    return {row.get("name"): row for row in report.get("checks", [])}


def _sim_chunks(paths: list[Path]) -> list[dict]:
    from tools.emulation.p1me_machine import capture_many as capture

    reports: list[dict] = []

    def run(chunk: list[Path]) -> None:
        if not chunk:
            return
        try:
            reports.extend(capture(TARGET, chunk, REPO_ROOT / "build" / "tmp" / "camry-oracle"))
        except P1MEMachineError as exc:
            if len(chunk) == 1:
                message = " ".join(str(exc).split())[:180]
                print(f"simulator {chunk[0].stem} {message}", flush=True)
                reports.append({
                    "scenario": chunk[0].stem,
                    "passed": False,
                    "termination_reason": "simulator",
                    "simulator_message": message,
                    "checks": [],
                    "memory_accesses": [],
                })
                return
            mid = len(chunk) // 2
            run(chunk[:mid])
            run(chunk[mid:])

    for start in range(0, len(paths), SIM_CHUNK):
        batch = paths[start:start + SIM_CHUNK]
        print(f"simulate {start + len(batch)}/{len(paths)}", flush=True)
        run(batch)
    return reports


_R10_DEST = {
    "mov", "movi", "movea", "movhi", "add", "sub", "subr", "or", "xor", "and", "not",
    "addi", "addi_imm5", "ld8s", "ld8u", "ld16s", "ld16u", "ld32",
    "mul", "mulh", "mulhi", "muli", "mului", "div3", "divh2",
    "shl_imm", "shr", "sar", "shr_reg", "sar_reg", "shl_reg",
    "satadd", "satsub", "satsubr", "sataddi", "satsubi", "satadd3", "satsub3",
    "cmov", "adf", "sbf",
}


_R10_UPDATE = {"addi_imm5", "sxh", "zxh", "sxb", "zxb", "shr", "sar", "shl_imm"}


_CONSUMED_RETURNS: set[int] = set()


# Interpret the last operand as an immediate displacement: 10 means the value 10.
_IMM_TAIL = {
    "ld8s", "ld8u", "ld16s", "ld16u", "ld32",
    "st8", "st16", "st32",
    "addi", "cmpi", "movi", "movea", "movhi",
    "mulhi", "muli", "mului", "addi_imm5", "shl_imm", "shr", "sar",
    "sataddi", "satsubi",
}


def _reg_args(op: str, args: list) -> list:
    if op in _IMM_TAIL and args:
        return list(args[:-1])
    return list(args)


def _r10_effects(inst: Inst) -> tuple[bool, bool]:
    """Whether this instruction reads r10 and whether it writes r10."""
    if inst.kind in {"jarl", "jarl_ind"} and inst.link == 10:
        return False, True
    parsed = _stmt_parts(inst.stmt) if inst.stmt else None
    if parsed is None:
        return False, False
    op, args = parsed
    regs = [arg for arg in _reg_args(op, args) if arg is not None]
    if op in {"cmp", "cmpi", "tst"}:
        return 10 in regs, False
    if op in {"st8", "st16", "st32", "set1", "not1", "clr1", "tst1"}:
        return bool(regs) and regs[0] == 10, False
    if op in _R10_UPDATE and regs and regs[0] == 10:
        return True, True
    if op in _R10_DEST and regs and regs[0] == 10:
        return 10 in regs[1:], True
    if op in _R10_DEST:
        return 10 in regs[1:], False
    return False, False


def _returns_read_by_callers(functions: dict[int, object]) -> set[int]:
    """Entries whose r10 a direct caller reads before replacing it."""
    consumed: set[int] = set()
    for fn in functions.values():
        insts = fn.insts
        for index, inst in enumerate(insts):
            if inst.kind != "jarl":
                continue
            for nxt in insts[index + 1:index + 21]:
                reads, writes = _r10_effects(nxt)
                if reads:
                    consumed.add(inst.target)
                    break
                if writes or nxt.kind in {"jarl", "jarl_ind", "jmp", "dispose"}:
                    break
    return consumed


def _simulator_cause(report: dict) -> str:
    """Group a machine failure by its fault kind or runner error type."""
    fault = (report.get("fault") or {}).get("kind")
    if fault:
        return str(fault)
    error = report.get("error") or {}
    if error.get("type"):
        return str(error["type"])
    message = " ".join(str(report.get("simulator_message") or "").split())
    return message[:80]


def _judge(item: Planned, run: Run, scenario: dict, report: dict) -> str | None:
    if not report or report.get("termination_reason") in {None, "simulator"}:
        cause = _simulator_cause(report) if report else ""
        return f"simulator {cause}".strip() if cause else "simulator"
    if report.get("termination_reason") != "stop-address":
        reason = report.get("termination_reason") or "simulator"
        fault = (report.get("fault") or {}).get("kind")
        if reason == "instruction-budget":
            return "instruction-budget"
        if fault in REASONS:
            return fault
        cause = _simulator_cause(report) or reason
        return f"simulator {cause}".strip()
    accesses = report.get("memory_accesses") or []
    if len(accesses) >= 16384 and report.get("trace_lost_address", True):
        return "trace-cap"
    checks = _report_map(report)
    preserved = (("gp", run.regs[4]), ("tp", run.regs[5]))
    if run.halt is None:
        preserved = (
            ("sp", run.regs[3]), ("r2", run.regs[2]), *preserved,
            *((f"r{reg}", run.regs[reg]) for reg in range(20, 30)),
        )
    for label, expected in preserved:
        actual = checks.get(label, {}).get("actual")
        if actual is None or int(actual, 16) != expected:
            return "stack-imbalance" if label == "sp" else "callee-saved"
    sim_r10 = int(checks["r10"]["actual"], 16) if "r10" in checks else SENTINEL
    if run.regs[10] != sim_r10:
        return "harness-drift r10"
    for name, expected in run.system_outputs.items():
        actual = checks.get(f"system-{name}", {}).get("actual")
        if actual is None or int(actual, 16) != expected:
            return f"harness-drift {name}"
    writes = set()
    for row in report.get("memory_accesses") or []:
        if row.get("kind") != "write":
            continue
        addr = int(row["address"], 16)
        size = int(row["size"])
        if 0xFEDE0000 <= addr < 0xFEE00000 and size <= 0xFEE00000 - addr:
            addr -= 0x200000
        for offset in range(size):
            writes.add(addr + offset)
    interpreted = {addr + offset for addr, size in run.writes for offset in range(size)}
    if not writes <= interpreted:
        missing = min(writes - interpreted)
        return f"harness-drift write {missing:#x}"
    for addr, size in _write_spans(run):
        actual = checks.get(f"mem-{addr:x}", {}).get("actual")
        if not actual or actual == "unavailable" or len(actual) != size * 2:
            return "uninitialized-read"
        if actual != _hex_bytes(run, addr, size):
            return f"harness-drift mem {addr:#x}"
    scratch_name = f"mem-{SCRATCH:x}"
    if not _write_spans(run) and scratch_name in checks:
        actual = checks[scratch_name].get("actual")
        fill = _region_fill(scenario, SCRATCH)
        if fill is None or not actual or actual == "unavailable" or actual != f"{fill:02x}" * SCRATCH_SIZE:
            return f"harness-drift mem {SCRATCH:#x}"
    return_type, _params = parse_signature(item.signature, item.name)
    bytes_return = sim_r10 != SENTINEL
    if not bytes_return and return_type != "void":
        return "invented-return"
    if (
        run.halt is None
        and bytes_return
        and return_type == "void"
        and run.root_r10
        and item.address in _CONSUMED_RETURNS
    ):
        return "dropped-return"
    return None


def _finalize(item: Planned, run: Run, scenario: dict, report: dict) -> dict:
    checks = _report_map(report)
    return_type, _params = parse_signature(item.signature, item.name)
    saved = dict(scenario)
    saved_checks = []
    # A halt stop is inside a callee. r10 there is not this function's return.
    if return_type != "void" and run.halt is None and "r10" in checks:
        width = _return_width(return_type)
        value = int(checks["r10"]["actual"], 16) & ((1 << width) - 1)
        saved_checks.append({
            "name": "original r10",
            "kind": "register",
            "register": "r10",
            "equals": hex(value),
        })
    if run.halt is None:
        for label in ("r2", "sp", "gp", "tp", *(f"r{reg}" for reg in range(20, 30))):
            saved_checks.append({
                "name": f"original {label}",
                "kind": "register",
                "register": label,
                "equals": checks[label]["actual"],
            })
    for name in run.system_outputs:
        saved_checks.append({
            "name": f"original {name}",
            "kind": "register",
            "register": name,
            "equals": checks[f"system-{name}"]["actual"],
        })
    for addr, size in _write_spans(run):
        saved_checks.append({
            "name": f"write {addr:x}",
            "kind": "memory",
            "address": hex(addr),
            "size": size,
            "equals_hex": checks[f"mem-{addr:x}"]["actual"],
        })
    scratch = checks.get(f"mem-{SCRATCH:x}", {}).get("actual")
    if not _write_spans(run) and scratch and scratch != "unavailable":
        saved_checks.append({
            "name": f"write {SCRATCH:x}",
            "kind": "memory",
            "address": hex(SCRATCH),
            "size": SCRATCH_SIZE,
            "equals_hex": scratch,
        })
    saved["checks"] = saved_checks
    if item.bounded and run.halt is not None:
        saved["call_sequence"] = [hex(addr) for addr in run.call_seq]
    return saved

