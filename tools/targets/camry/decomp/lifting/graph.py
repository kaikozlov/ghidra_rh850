"""Byte walking, function graphs, gap discovery, and lift closure."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import re

from tools import REPO_ROOT
from tools.project.analysis_target import target as resolve_target

from .. import tree
from .decode import Inst, decode_at, u16


def walk_range(image: bytes, start: int, end: int) -> list[Inst] | None:
    pc = start
    insts: list[Inst] = []
    while pc <= end:
        inst = decode_at(image, pc)
        if inst is None or pc + inst.size - 1 > end:
            return None
        insts.append(inst)
        pc += inst.size
    if pc != end + 1:
        return None
    return insts


@dataclass
class LiftedFn:
    entry: int
    name: str
    ranges: list[tuple[int, int]]
    insts: list[Inst]
    calls: set[int] = field(default_factory=set)
    sites: set[int] = field(default_factory=set)


_GAP_READS: dict[str, tuple[int, ...]] = {
    "camry_movi": (),
    "camry_mov": (1,),
    "camry_movea": (1,),
    "camry_movhi": (1,),
    "camry_zxb": (0,),
    "camry_zxh": (0,),
    "camry_add": (0, 1),
    "camry_addi": (1,),
    "camry_addi_imm5": (0,),
    "camry_shl_imm": (0,),
    "camry_shr": (0,),
    "camry_sar_reg": (1, 2),
    "camry_ld8u": (1,),
    "camry_ld8s": (1,),
    "camry_ld16u": (1,),
    "camry_ld16s": (1,),
    "camry_ld32": (1,),
    "camry_st8": (0, 1),
    "camry_st16": (0, 1),
    "camry_st32": (0, 1),
    "camry_cmovi": (1,),
    "camry_cmov": (1, 2),
    "camry_cmpi": (0,),
    "camry_cmp": (0, 1),
    "camry_andi": (1,),
    "camry_ori": (1,),
    "camry_setf": (),
    "camry_not": (1,),
    "camry_and": (0, 1),
    "camry_mulhi": (1,),
    "camry_satsubi": (1,),
    "camry_clr1r": (0, 1),
    "camry_sch1r": (0,),
}
_GAP_WRITES: dict[str, tuple[int, ...]] = {
    "camry_movi": (0,),
    "camry_mov": (0,),
    "camry_movea": (0,),
    "camry_movhi": (0,),
    "camry_zxb": (0,),
    "camry_zxh": (0,),
    "camry_add": (0,),
    "camry_addi": (0,),
    "camry_addi_imm5": (0,),
    "camry_shl_imm": (0,),
    "camry_shr": (0,),
    "camry_sar_reg": (0,),
    "camry_ld8u": (0,),
    "camry_ld8s": (0,),
    "camry_ld16u": (0,),
    "camry_ld16s": (0,),
    "camry_ld32": (0,),
    "camry_st8": (),
    "camry_st16": (),
    "camry_st32": (),
    "camry_cmovi": (0,),
    "camry_cmov": (0,),
    "camry_cmpi": (),
    "camry_cmp": (),
    "camry_andi": (0,),
    "camry_ori": (0,),
    "camry_setf": (0,),
    "camry_not": (0,),
    "camry_and": (0,),
    "camry_mulhi": (0,),
    "camry_satsubi": (0,),
    "camry_clr1r": (),
    "camry_sch1r": (1,),
}
_GAP_FLAG_READ = {"camry_cmovi", "camry_cmov", "camry_setf"}
_GAP_FLAG_WRITE = {
    "camry_add", "camry_addi", "camry_addi_imm5", "camry_cmp", "camry_cmpi",
    "camry_shl_imm", "camry_shr", "camry_sar_reg", "camry_and", "camry_andi",
    "camry_ori", "camry_not", "camry_satsubi", "camry_sch1r", "camry_clr1r",
}


def _stmt_call(stmt: str) -> tuple[str, list[int]] | None:
    match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\s*;\s*", stmt, flags=re.S)
    if match is None:
        return None
    args: list[int] = []
    body = match.group(2).strip()
    if body:
        for part in body.split(","):
            args.append(int(part.strip().rstrip("uU"), 0))
    return match.group(1), args


def _closed_gap(insts: list[Inst]) -> bool:
    """The thunk uses only gp, tp, and the four argument registers."""
    defined = {0, 4, 5, 6, 7, 8, 9}
    flags = False
    for inst in insts[:-1]:
        parsed = _stmt_call(inst.stmt)
        if parsed is None or inst.kind != "alu":
            return False
        name, args = parsed
        reads = _GAP_READS.get(name)
        writes = _GAP_WRITES.get(name)
        if reads is None or writes is None:
            return False
        if name in _GAP_FLAG_READ and not flags:
            return False
        for index in reads:
            if index >= len(args) or args[index] not in defined:
                return False
        for index in writes:
            if index < len(args) and args[index] != 0:
                defined.add(args[index])
        if name in _GAP_FLAG_WRITE:
            flags = True
    last = insts[-1]
    return last.kind == "jmp" and last.reg == 31


def gap_thunks(image: bytes, symbols: list[dict]) -> list[LiftedFn]:
    """Straight-line returns that sit between defined functions.

    An indirect call lands on these addresses. They are real instructions, and
    they are not symbols, so the harness otherwise stops.
    """
    spans: list[tuple[int, int]] = []
    for row in symbols:
        for start, end in row["ranges"]:
            spans.append((start, end))
    spans.sort()
    merged: list[list[int]] = []
    for start, end in spans:
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
            continue
        merged.append([start, end])
    found: list[LiftedFn] = []
    for index, (start, end) in enumerate(merged[:-1]):
        nxt = merged[index + 1][0]
        gap = end + 1
        if nxt <= gap or nxt - gap > 96 or gap >= len(image):
            continue
        covered: set[int] = set()
        pc = gap
        while pc + 2 <= nxt and pc not in covered:
            insts: list[Inst] = []
            cursor = pc
            while cursor + 2 <= nxt and len(insts) < 24:
                inst = decode_at(image, cursor)
                if inst is None or cursor + inst.size > nxt:
                    break
                insts.append(inst)
                cursor += inst.size
                if inst.kind == "jmp":
                    break
                if inst.kind != "alu":
                    insts = []
                    break
            if not insts or not _closed_gap(insts):
                pc += 2
                continue
            entry = insts[0].addr
            found.append(LiftedFn(
                entry,
                f"camry_gap_{entry:08x}",
                [(entry, insts[-1].addr + insts[-1].size - 1)],
                insts,
                sites={inst.addr for inst in insts},
            ))
            covered.update(inst.addr for inst in insts)
            pc = cursor
    found.extend(_gap_control(image, merged, found))
    return found


def _gap_effect(inst: Inst) -> tuple[set[int], set[int], bool, bool] | None:
    if inst.kind in {"b", "br", "jmp", "nop"}:
        return set(), set(), False, inst.kind == "b" and inst.cc != 5
    parsed = _stmt_call(inst.stmt) if inst.stmt else None
    if parsed is None or inst.kind != "alu":
        return None
    name, args = parsed
    reads = _GAP_READS.get(name)
    writes = _GAP_WRITES.get(name)
    if reads is None or writes is None:
        return None
    read_regs = {args[index] for index in reads if index < len(args)}
    write_regs = {args[index] for index in writes if index < len(args) and args[index] != 0}
    return read_regs, write_regs, name in _GAP_FLAG_WRITE, name in _GAP_FLAG_READ


def _gap_successors(inst: Inst) -> list[int]:
    if inst.kind == "jmp":
        return []
    if inst.kind == "br" or (inst.kind == "b" and inst.cc == 5):
        return [inst.target]
    if inst.kind == "b":
        return [inst.target, inst.addr + inst.size]
    return [inst.addr + inst.size]


def _gap_closed_cfg(insts: list[Inst], entry: int, tails: set[int]) -> bool:
    """Every path reads only gp, tp, the arguments, or a register it wrote."""
    by = {inst.addr: inst for inst in insts}
    defined: dict[int, frozenset[int]] = {entry: frozenset({0, 4, 5, 6, 7, 8, 9})}
    flags: dict[int, bool] = {entry: False}
    changed = True
    while changed:
        changed = False
        for addr, inst in by.items():
            if addr not in defined:
                continue
            info = _gap_effect(inst)
            if info is None:
                return False
            _reads, write_regs, writes_flags, _reads_flags = info
            out = defined[addr] | frozenset(write_regs)
            out_flags = flags[addr] or writes_flags
            for succ in _gap_successors(inst):
                if succ not in by:
                    if succ not in tails:
                        return False
                    continue
                if succ not in defined:
                    defined[succ] = out
                    flags[succ] = out_flags
                    changed = True
                    continue
                shrunk = defined[succ] & out
                fl = flags[succ] and out_flags
                if shrunk != defined[succ] or fl != flags[succ]:
                    defined[succ] = shrunk
                    flags[succ] = fl
                    changed = True
    for addr, inst in by.items():
        if addr not in defined:
            return False
        info = _gap_effect(inst)
        if info is None:
            return False
        read_regs, _writes, _writes_flags, reads_flags = info
        if not read_regs <= defined[addr]:
            return False
        if reads_flags and not flags[addr]:
            return False
        if 3 in _writes:
            return False
    if not _gap_can_return(by, tails):
        return False
    return True


def _gap_can_return(by: dict[int, Inst], tails: set[int]) -> bool:
    """Every instruction can reach a return or a straight-line thunk."""
    terminators = set()
    reverse: dict[int, list[int]] = {addr: [] for addr in by}
    for addr, inst in by.items():
        exits = False
        for succ in _gap_successors(inst):
            if succ in by:
                reverse[succ].append(addr)
            elif succ in tails or inst.kind == "jmp":
                exits = True
        if inst.kind == "jmp" or exits:
            terminators.add(addr)
    seen = set(terminators)
    stack = list(terminators)
    while stack:
        addr = stack.pop()
        for pred in reverse[addr]:
            if pred not in seen:
                seen.add(pred)
                stack.append(pred)
    return seen == set(by)


def _lift_gap_control(image: bytes, entry: int, limit: int, occupied: set[int], tails: set[int]) -> list[Inst] | None:
    """One branched gap function. A branch may land on a straight-line thunk."""
    insts: dict[int, Inst] = {}
    queue = [entry]
    while queue:
        addr = queue.pop()
        if addr in insts:
            continue
        if addr in occupied or len(insts) >= 48:
            return None
        inst = decode_at(image, addr)
        if inst is None or addr + inst.size > limit:
            return None
        if any(byte in occupied for byte in range(addr, addr + inst.size)):
            return None
        if inst.kind == "jmp":
            if inst.reg != 31:
                return None
            insts[addr] = inst
            continue
        if inst.kind in {"b", "br"}:
            for target in _gap_successors(inst):
                if target in tails:
                    continue
                if target < entry or target >= limit or target in occupied:
                    return None
                queue.append(target)
            insts[addr] = inst
            continue
        if inst.kind not in {"alu", "nop"}:
            return None
        fall = addr + inst.size
        if fall not in tails:
            if fall >= limit or fall in occupied:
                return None
            queue.append(fall)
        insts[addr] = inst
    if not insts or not any(inst.kind in {"b", "br"} for inst in insts.values()):
        return None
    ordered = [insts[addr] for addr in sorted(insts)]
    if not _gap_closed_cfg(ordered, entry, tails):
        return None
    return ordered


def _gap_control(image: bytes, merged: list[list[int]], straight: list[LiftedFn]) -> list[LiftedFn]:
    """Branched returns between symbols, including a branch into a straight thunk.

    The straight-line pass stops at the first branch, so the bytes before that
    branch stay unowned and an indirect call there leaves the image.
    """
    occupied = {inst.addr for fn in straight for inst in fn.insts}
    for fn in straight:
        for inst in fn.insts:
            occupied.update(range(inst.addr, inst.addr + inst.size))
    tails = {fn.entry for fn in straight}
    found: list[LiftedFn] = []
    for index, (start, end) in enumerate(merged[:-1]):
        nxt = merged[index + 1][0]
        gap = end + 1
        if nxt <= gap or nxt - gap > 160 or gap >= len(image):
            continue
        pc = gap
        while pc + 2 <= nxt:
            if pc in occupied:
                pc += 2
                continue
            insts = _lift_gap_control(image, pc, nxt, occupied, tails)
            if insts is None:
                pc += 2
                continue
            entry = insts[0].addr
            found.append(LiftedFn(
                entry,
                f"camry_gap_{entry:08x}",
                [(entry, insts[-1].addr + insts[-1].size - 1)],
                insts,
                sites={inst.addr for inst in insts},
            ))
            for inst in insts:
                occupied.update(range(inst.addr, inst.addr + inst.size))
            pc = max(inst.addr + inst.size for inst in insts)
    return found


def walk_symbol(image: bytes, row: dict) -> LiftedFn | None:
    entry = int(row["addr"], 16)
    ranges = [(start, end) for start, end in row["ranges"]]
    if not ranges or any(start >= len(image) or end >= len(image) for start, end in ranges):
        return None
    insts: list[Inst] = []
    for start, end in ranges:
        walked = walk_range(image, start, end)
        if walked is None:
            return None
        insts.extend(walked)
    sites = {inst.addr for inst in insts}
    if entry not in sites:
        return None
    return LiftedFn(entry, row["name"], ranges, insts, sites=sites)


def direct_targets(fn: LiftedFn) -> set[int]:
    targets = set()
    for inst in fn.insts:
        if inst.kind in {"jarl", "jr", "b", "br"} and inst.target not in fn.sites:
            targets.add(inst.target)
    return targets


def load_image() -> bytes:
    metadata = resolve_target(tree.TARGET)[1]
    image = (REPO_ROOT / metadata["codeflash"]).read_bytes()
    return image


def first_failure(image: bytes, row: dict) -> tuple[int, int, int, int] | None:
    for start, end in row["ranges"]:
        if start >= len(image) or end >= len(image):
            return None
        pc = start
        while pc <= end:
            inst = decode_at(image, pc)
            if inst is None or pc + inst.size - 1 > end:
                hw0 = u16(image, pc) if pc + 2 <= len(image) else 0
                hw1 = u16(image, pc + 2) if pc + 4 <= len(image) else 0
                return pc, hw0, hw1, (hw0 >> 5) & 0x3F
            pc += inst.size
    return None


def decode_all(image: bytes, symbols: list[dict]) -> tuple[dict[int, LiftedFn], Counter]:
    decoded: dict[int, LiftedFn] = {}
    unknown: Counter = Counter()
    for row in symbols:
        fn = walk_symbol(image, row)
        if fn is None:
            failed = first_failure(image, row)
            if failed is not None:
                _pc, hw0, hw1, op = failed
                unknown[(hw0, hw1, op)] += 1
            continue
        fn.calls = direct_targets(fn)
        decoded[fn.entry] = fn
    return decoded, unknown


def liftable_set(decoded: dict[int, LiftedFn]) -> set[int]:
    entries = set(decoded)
    changed = True
    while changed:
        changed = False
        for entry, fn in list(decoded.items()):
            if entry not in entries:
                continue
            if any(target not in entries for target in fn.calls):
                entries.remove(entry)
                changed = True
    return entries


def closure_of(seeds: set[int], decoded: dict[int, LiftedFn], liftable: set[int]) -> set[int]:
    seen = set()
    stack = [seed for seed in seeds if seed in liftable]
    while stack:
        entry = stack.pop()
        if entry in seen:
            continue
        seen.add(entry)
        for target in decoded[entry].calls:
            if target in liftable and target not in seen:
                stack.append(target)
    return seen


