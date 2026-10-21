"""Instruction-backed native ABI and register-origin dataflow recovery."""
from __future__ import annotations

from tools import REPO_ROOT
import re

from tools.targets.camry.decomp import c_text, layout, syntax, tree



_FAIL = ("fail",)
# r1–r31. r6–r9 enter as the incoming arguments; the rest start unknown.
_TRACKED = tuple(range(1, 32))
# GHS RH850: r3–r5 (sp/gp/tp) and r20–r29 survive a call. r6–r9 survive only
# when this particular callee never writes them. r10 is then the return value.
_CALLER_KILLED = {1, 2, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 30, 31}
_ARG_CLOBBERS: dict[int, set[int]] | None = None
_R10_PRESERVE: set[int] = set()
_CONTEXT_SAVED: dict[int, set[int]] = {}
_STATIC_CALL_TARGETS: dict[int, int] = {}
# Callees that return with one immediate in r4. The caller keeps that global pointer.
_R4_SETTERS: dict[int, int] = {}
_NO_WRITE = {
    "cmp", "tst", "cmpi", "st8", "st16", "st32", "set1", "not1", "clr1", "tst1",
    "set1r", "not1r", "clr1r", "tst1r", "ldsr",
}
_DEST0 = {
    "mov", "movi", "not", "or", "xor", "and", "add", "sub", "subr", "addi",
    "addi_imm5", "ori", "xori", "andi", "movea", "movhi", "satadd", "satsub",
    "satsubr", "sataddi", "satsubi", "mulh", "divh2", "shl_imm", "shr", "sar_imm",
    "zxb", "zxh", "sxb", "sxh", "mulhi", "mulhi5", "setf", "sasf", "ld8s", "ld8u",
    "ld16s", "ld16u", "ld32", "cmov", "cmovi", "sbf", "adf", "shl_reg", "shr_reg",
    "sar_reg", "satadd3", "satsub3", "stsr", "pop",
}
_NARROW = {"zxb": "byte", "zxh": "ushort", "sxb": "sbyte", "sxh": "short"}
_CALL_FACTS: dict | None = None


def _narrow(origin: tuple, cast: str) -> tuple:
    if origin[0] == "imm":
        value = origin[1] & 0xFFFFFFFF
        if cast in {"byte", "sbyte"}:
            value &= 0xFF
            if cast == "sbyte" and value >= 0x80:
                value -= 0x100
        else:
            value &= 0xFFFF
            if cast == "short" and value >= 0x8000:
                value -= 0x10000
        return ("imm", value & 0xFFFFFFFF)
    if origin[0] == "entry":
        previous = origin[2]
        if previous == "byte" and cast == "ushort":
            cast = "byte"
        elif previous == "sbyte" and cast == "short":
            cast = "sbyte"
        return ("entry", origin[1], cast)
    if origin[0] == "mem" and not origin[3]:
        width = origin[1]
        if cast == "byte" and width == 1 or cast == "ushort" and width <= 2:
            return origin
    return _FAIL


def _write_origin(state: dict[int, set], reg: int | None, origin: tuple) -> None:
    if reg in state:
        state[reg] = {origin}


def _entry_state(gp: int | None = None) -> dict[int, set]:
    state = {reg: {_FAIL} for reg in _TRACKED}
    for reg in (6, 7, 8, 9):
        state[reg] = {("entry", reg, "")}
    # r3 is the stack pointer. Its displacement is from the value at entry.
    state[3] = {("sp", 0)}
    # Startup fixes tp; callback slots reached through it are in CodeFlash.
    state[5] = {("imm", layout._RUNTIME_TP)}
    # r4 is the global pointer. Callers that agree pass one immediate.
    if gp is not None:
        state[4] = {("imm", gp & 0xFFFFFFFF)}
    return state


def _shift_sp(origin: set, delta: int) -> set | None:
    if len(origin) != 1:
        return None
    item = next(iter(origin))
    if item[0] != "sp":
        return None
    return {("sp", item[1] + delta)}


def _codeflash_image() -> bytes:
    cached = getattr(_codeflash_image, "cached", None)
    if cached is None:
        from .lifting.graph import load_image
        cached = load_image()
        _codeflash_image.cached = cached
    return cached


def _rom_immediate(item: tuple) -> int | None:
    """A codeflash load has one value. RAM and signed loads stay memory origins."""
    if len(item) < 4 or item[0] != "mem" or item[3]:
        return None
    width = item[1]
    addr = item[2] & 0xFFFFFFFF
    if width not in (1, 2, 4):
        return None
    image = _codeflash_image()
    if addr + width > len(image):
        return None
    return int.from_bytes(image[addr:addr + width], "little")


def _fold_imm(name: str, base: int, imm: int) -> int | None:
    base &= 0xFFFFFFFF
    if name == "movhi":
        return (base + ((imm & 0xFFFFFFFF) << 16)) & 0xFFFFFFFF
    if name == "andi":
        return base & (imm & 0xFFFFFFFF)
    if name == "ori":
        return base | (imm & 0xFFFFFFFF)
    if name == "xori":
        return base ^ (imm & 0xFFFFFFFF)
    if name in {"addi", "movea"}:
        return (base + imm) & 0xFFFFFFFF
    return None

def _argument_origin(state: dict, index: int) -> set:
    """GHS passes four words in r6-r9, then words at the caller's SP."""
    if index < 4:
        return state.get(6 + index, {_FAIL})
    sp = state.get(3, set())
    if len(sp) != 1 or next(iter(sp))[0] != "sp":
        return {_FAIL}
    offset = next(iter(sp))[1] + 4 * (index - 4)
    return state.get(("stack", offset), {_FAIL})



def _transfer(state: dict[int, set], inst) -> dict[int, set]:
    cur = {reg: set(values) for reg, values in state.items()}
    if inst.kind in {"jarl", "jarl_ind"}:
        target = inst.target if inst.kind == "jarl" else _STATIC_CALL_TARGETS.get(inst.addr)
        killed = set(_CALLER_KILLED)
        clobbers = _ARG_CLOBBERS
        if clobbers is not None and target in clobbers:
            killed |= clobbers[target]
        else:
            killed.update((6, 7, 8, 9))
        # A callee that never writes r10 leaves the caller's return register alone.
        if target in _R10_PRESERVE:
            killed.discard(10)
        killed.difference_update(_CONTEXT_SAVED.get(target, ()))
        if inst.link:
            killed.add(inst.link)
        for reg in killed:
            if reg in cur:
                cur[reg] = {_FAIL}
        if 10 in killed and inst.link != 10 and 10 in cur:
            cur[10] = {("call", target, inst.addr)}
        elif 10 in killed and 10 in cur:
            cur[10] = {_FAIL}
        left = _R4_SETTERS.get(target)
        if left is not None and 4 in cur:
            cur[4] = {("imm", left)}
        # Pointers passed to a callee can expose any local stack slot.
        for key in list(cur):
            if isinstance(key, tuple) and key[0] == "stack":
                del cur[key]
        return cur
    if inst.kind == "callt":
        for reg in _CALLER_KILLED | {6, 7, 8, 9}:
            if reg in cur:
                cur[reg] = {_FAIL}
        for key in list(cur):
            if isinstance(key, tuple) and key[0] == "stack":
                del cur[key]
        return cur
    if inst.kind == "loop" and inst.reg in cur:
        cur[inst.reg] = {_FAIL}
        return cur
    if inst.kind == "dispose":
        mask = inst.mask
        bit = 0
        while mask:
            if mask & 1 and bit in cur:
                cur[bit] = {_FAIL}
            mask >>= 1
            bit += 1
        if 3 in cur:
            cur[3] = {_FAIL}
        return cur
    parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
    if parsed is None:
        return cur
    name, args = parsed
    if name == "prepare" and len(args) >= 2 and args[0] is not None and args[1] is not None and 3 in cur:
        saved = sum(1 for reg in range(20, 32) if args[0] & (1 << reg))
        shifted = _shift_sp(cur[3], -4 * (saved + args[1]))
        if shifted is not None:
            cur[3] = shifted
            mode = args[2] if len(args) > 2 else 0
            if mode == 1 and 30 in cur:
                cur[30] = set(shifted)
            elif mode in {2, 3, 4} and 30 in cur:
                imm = args[3] if len(args) > 3 and args[3] is not None else 0
                if mode == 3:
                    imm = (imm & 0xFFFFFFFF) << 16
                cur[30] = {("imm", imm & 0xFFFFFFFF)}
        return cur
    if name == "pushsp" and len(args) >= 2 and args[0] is not None and args[1] is not None and 3 in cur:
        if args[0] <= args[1]:
            shifted = _shift_sp(cur[3], -4 * (args[1] - args[0] + 1))
            if shifted is not None:
                if inst.addr in _CONTEXT_SAVED:
                    for reg in _CONTEXT_SAVED[inst.addr] - {3}:
                        cur[("saved", reg)] = set(cur.get(reg, {_FAIL}))
                cur[3] = shifted
        return cur
    if name == "popsp" and len(args) >= 2 and args[0] is not None and args[1] is not None:
        if 0 <= args[0] <= args[1] <= 31:
            for reg in range(args[0], args[1] + 1):
                if reg in cur and reg != 3:
                    cur[reg] = cur.pop(("saved", reg), {_FAIL})
            if 3 in cur:
                shifted = _shift_sp(cur[3], 4 * (args[1] - args[0] + 1))
                if shifted is not None:
                    cur[3] = shifted
        return cur
    if name in {"st8", "st16", "st32"} and len(args) >= 3:
        base = cur.get(args[1], set())
        if len(base) == 1 and next(iter(base))[0] == "sp" and args[2] is not None:
            offset = next(iter(base))[1] + args[2]
            width = {"st8": 1, "st16": 2, "st32": 4}[name]
            for key in list(cur):
                if isinstance(key, tuple) and key[0] == "stack" and offset < key[1] + 4 and key[1] < offset + width:
                    cur[key] = {_FAIL}
            value = {("imm", 0)} if args[0] == 0 else cur.get(args[0], {_FAIL})
            cur[("stack", offset)] = set(value) if width == 4 else {_FAIL}
        return cur
    if name in _NO_GPR_WRITE:
        return cur
    if name in _NO_WRITE:
        return cur
    if name == "mov" and args:
        src = args[1] if len(args) > 1 else None
        if src == 0:
            _write_origin(cur, args[0], ("imm", 0))
        elif src in cur:
            cur[args[0]] = set(cur[src])
        else:
            _write_origin(cur, args[0], _FAIL)
        return cur
    if name == "movi" and args and args[1] is not None:
        _write_origin(cur, args[0], ("imm", args[1] & 0xFFFFFFFF))
        return cur
    if name in {"ori", "xori", "addi", "movea", "movhi", "andi"} and len(args) >= 3:
        dst, src, imm = args[0], args[1], args[2]
        if src == 0 and imm is not None and dst in cur:
            value = imm & 0xFFFFFFFF
            if name == "movhi":
                value = (imm << 16) & 0xFFFFFFFF
            if name == "andi":
                value = 0
            cur[dst] = {("imm", value)}
            return cur
        if src in cur and imm is not None and len(cur[src]) == 1 and dst in cur:
            item = next(iter(cur[src]))
            if item[0] == "imm":
                folded = _fold_imm(name, item[1], imm)
                if folded is not None:
                    cur[dst] = {("imm", folded)}
                    return cur
            if item[0] == "sp" and name in {"addi", "movea"}:
                cur[dst] = {("sp", item[1] + imm)}
                return cur
        if name == "andi" and dst == src and dst in cur and imm in {0xFF, 0xFFFF} and len(cur[dst]) == 1:
            cur[dst] = {_narrow(next(iter(cur[dst])), "byte" if imm == 0xFF else "ushort")}
            return cur
        _write_origin(cur, dst, _FAIL)
        return cur
    if name == "stsr" and len(args) >= 3 and args[1] == 11 and args[2] == 2:
        # stsr sr11, rN, 2 reads PMR. The value is the register's new origin.
        _write_origin(cur, args[0], ("sreg", 11, 2))
        return cur
    if name in {"cmov", "cmovi"} and len(args) >= 3 and args[0] in cur:
        dst, fallback, taken = args[:3]
        left = {("imm", 0)} if fallback == 0 else cur.get(fallback, {_FAIL})
        right = (
            {("imm", taken & 0xffffffff)} if name == "cmovi" and taken is not None
            else {("imm", 0)} if taken == 0 else cur.get(taken, {_FAIL})
        )
        cur[dst] = set(left) | set(right)
        return cur
    if name in {"ld8s", "ld8u", "ld16s", "ld16u", "ld32"} and len(args) >= 3 and args[2] is not None:
        loaded = {"ld8s": (1, True), "ld8u": (1, False), "ld16s": (2, True), "ld16u": (2, False), "ld32": (4, False)}
        base = cur.get(args[1]) if args[1] is not None else None
        if base is not None and len(base) == 1 and next(iter(base))[0] == "sp":
            offset = next(iter(base))[1] + args[2]
            if offset >= 0 and offset % 4 == 0:
                cast = {"ld8s": "sbyte", "ld8u": "byte", "ld16s": "short", "ld16u": "ushort", "ld32": ""}[name]
                _write_origin(cur, args[0], ("entry", 10 + offset // 4, cast))
                return cur
            held = cur.get(("stack", offset))
            if held is not None and name == "ld32":
                cur[args[0]] = set(held)
                return cur
            width, signed = loaded[name]
            _write_origin(cur, args[0], ("stackload", offset, width, signed))
            return cur
        if base is not None and len(base) == 1 and next(iter(base))[0] == "imm":
            addr = (next(iter(base))[1] + args[2]) & 0xFFFFFFFF
            width, signed = loaded[name]
            _write_origin(cur, args[0], ("mem", width, addr, signed))
            return cur
        if base is not None and len(base) == 1 and next(iter(base))[0] == "entry":
            width, signed = loaded[name]
            held = next(iter(base))
            _write_origin(cur, args[0], ("deref", held[1], args[2], width, signed))
            return cur
        # A load writes its destination only. The base register stays live.
        _write_origin(cur, args[0], _FAIL)
        return cur
    if name in {"add", "sub", "subr"} and len(args) >= 2 and args[0] in cur:
        # `sub r6, r1` where r1 is a codeflash zero leaves the argument live.
        # The following indirect jarl still passes that register.
        dst, src = args[0], args[1]
        right = {("imm", 0)} if src == 0 else set(cur.get(src, {_FAIL}))
        if len(right) == 1 and next(iter(right))[0] == "mem":
            folded = _rom_immediate(next(iter(right)))
            if folded is not None:
                right = {("imm", folded & 0xFFFFFFFF)}
        left = cur.get(dst, {_FAIL})
        if len(left) == 1 and len(right) == 1 and next(iter(right))[0] == "imm":
            imm = next(iter(right))[1] & 0xFFFFFFFF
            if imm == 0 and name in {"add", "sub"}:
                return cur
            if next(iter(left))[0] == "imm":
                base = next(iter(left))[1] & 0xFFFFFFFF
                if name == "add":
                    cur[dst] = {("imm", (base + imm) & 0xFFFFFFFF)}
                elif name == "sub":
                    cur[dst] = {("imm", (base - imm) & 0xFFFFFFFF)}
                else:
                    cur[dst] = {("imm", (imm - base) & 0xFFFFFFFF)}
                return cur
    if name in _NARROW and args and args[0] in cur and len(cur[args[0]]) == 1:
        cur[args[0]] = {_narrow(next(iter(cur[args[0]])), _NARROW[name])}
        return cur
    if name in _DEST0 and args:
        _write_origin(cur, args[0], _FAIL)
        return cur
    if name in {"bsw", "bsh", "hsw", "hsh", "sch0r", "sch1r", "sch0l", "sch1l"} and len(args) > 1:
        _write_origin(cur, args[1], _FAIL)
        return cur
    if name in {"muli", "mului", "mul"}:
        _write_origin(cur, args[0] if args else None, _FAIL)
        if len(args) > 1:
            _write_origin(cur, args[1], _FAIL)
        return cur
    if name == "div3":
        _write_origin(cur, args[0] if args else None, _FAIL)
        if len(args) > 2:
            _write_origin(cur, args[2], _FAIL)
        return cur
    for reg in list(cur):
        if reg in args:
            cur[reg] = {_FAIL}
    return cur


def _function_origins(fn, gp: int | None = None) -> dict[int, dict[int, set]]:
    incoming: dict[int, dict[int, set]] = {fn.entry: _entry_state(gp)}
    work = [fn.entry]
    index_of = {inst.addr: index for index, inst in enumerate(fn.insts)}
    while work:
        addr = work.pop()
        inst = fn.insts[index_of[addr]]
        cur = _transfer(incoming[addr], inst)
        nxt = None
        index = index_of[addr]
        if index + 1 < len(fn.insts) and fn.insts[index + 1].addr == addr + inst.size:
            nxt = fn.insts[index + 1].addr
        if inst.kind == "b":
            succs = [item for item in (inst.target, nxt) if item is not None and (item == nxt or item in fn.sites)]
            is_ret = False
        elif inst.kind in {"br", "jr"}:
            if inst.target in fn.sites:
                succs = [inst.target]
                is_ret = False
            else:
                succs = []
                is_ret = True
        elif inst.kind == "loop":
            succs = [item for item in (inst.target, nxt) if item is not None and (item == nxt or item in fn.sites)]
            is_ret = False
        elif inst.kind in {"jmp", "jmpdisp", "switch", "dispose", "abort"}:
            succs = []
            is_ret = True
        else:
            succs = [nxt] if nxt is not None else []
            is_ret = False
        if is_ret:
            incoming.setdefault(("ret", addr), incoming[addr])
        for succ in succs:
            if succ not in index_of:
                continue
            old = incoming.get(succ)
            if old is None:
                incoming[succ] = {reg: set(values) for reg, values in cur.items()}
                work.append(succ)
                continue
            changed = False
            for reg in old.keys() | cur.keys():
                merged = old.get(reg, {_FAIL}) | cur.get(reg, {_FAIL})
                if merged != old.get(reg):
                    old[reg] = merged
                    changed = True
            if changed:
                work.append(succ)
    return incoming


def _emit_origin(origin: set, params: list[str], types: list[str]) -> str | None:
    if len(origin) != 1:
        return None
    item = next(iter(origin))
    if item[0] == "imm":
        value = item[1] & 0xFFFFFFFF
        if value >= 0x80000000:
            return f"(int)0x{value:x}"
        return f"0x{value:x}"
    if item[0] == "mem":
        width, addr, signed = item[1], item[2] & 0xFFFFFFFF, item[3]
        ctype = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}[width]
        expr = f"(*((volatile {ctype} *)camry_host_ptr(0x{addr:x}u)))"
        if signed and width == 1:
            return f"(int)(int8_t){expr}"
        if signed and width == 2:
            return f"(int)(int16_t){expr}"
        return expr
    if item[0] == "deref":
        reg, disp, width, signed = item[1], item[2], item[3], item[4]
        index = reg - 6
        if index < 0 or index >= len(params) or not params[index]:
            return None
        ctype = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}[width]
        expr = (
            f"(*((volatile {ctype} *)((uint8_t *)({params[index]}) + ({int(disp)}))))"
        )
        if signed and width == 1:
            return f"(int)(int8_t){expr}"
        if signed and width == 2:
            return f"(int)(int16_t){expr}"
        return expr
    if item[0] != "entry":
        return None
    index = item[1] - 6
    if index < 0 or index >= len(params) or not params[index]:
        return None
    if item[2] and index < len(types) and "*" in types[index]:
        return None
    name = params[index]
    cast = item[2]
    if cast == "byte":
        return f"(uint)(byte){name}"
    if cast == "ushort":
        return f"(uint)(ushort){name}"
    if cast == "sbyte":
        return f"(int)(char){name}"
    if cast == "short":
        return f"(int)(short){name}"
    return name


def _direct_arg_writes(fn) -> tuple[set[int], list[int], bool]:
    """r6–r9 this function writes itself, and the direct calls it makes."""
    written: set[int] = set()
    calls: list[int] = []
    has_callt = False
    blank = {reg: {("live",)} for reg in (6, 7, 8, 9)}
    for inst in fn.insts:
        if inst.kind == "callt" or inst.kind == "jarl_ind" and inst.addr not in _STATIC_CALL_TARGETS:
            has_callt = True
            continue
        if inst.kind == "jarl" or inst.addr in _STATIC_CALL_TARGETS:
            calls.append(inst.target if inst.kind == "jarl" else _STATIC_CALL_TARGETS[inst.addr])
            continue
        if inst.kind in {"jr", "br"} and inst.target not in fn.sites:
            calls.append(inst.target)
            continue
        after = _transfer(blank, inst)
        for reg in (6, 7, 8, 9):
            if after.get(reg) != blank[reg]:
                written.add(reg)
    return written, calls, has_callt


def _arg_clobber_map(
    writes: dict[int, set[int]],
    calls: dict[int, list[int]],
    callt: set[int],
) -> dict[int, set[int]]:
    """r6–r9 a function kills, including through the calls it makes."""
    cache: dict[int, set[int]] = {}

    def clobber(addr: int, stack: set[int]) -> set[int]:
        if addr in cache:
            return cache[addr]
        if addr in stack or addr not in writes or addr in callt:
            return {6, 7, 8, 9}
        stack.add(addr)
        found = set(writes[addr])
        for target in calls.get(addr, ()):
            found |= clobber(target, stack)
        stack.remove(addr)
        cache[addr] = found
        return found

    for addr in writes:
        clobber(addr, set())
    return cache


def _value_of_call(body: str, pos: int, callee: str) -> str | None:
    """Variable that still holds the latest `var = callee(...)` before pos."""
    assign = None
    pattern = re.compile(
        rf"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
        rf"(?:\([A-Za-z_][A-Za-z0-9_ \t*]*\)\s*)*{re.escape(callee)}\s*\("
    )
    for match in pattern.finditer(body, 0, pos):
        assign = match
    if assign is None:
        return None
    try:
        close = c_text._match_delimiter(body, assign.end() - 1)
    except ValueError:
        return None
    if not body[close + 1:pos].lstrip().startswith(";"):
        return None
    if re.search(rf"\b{re.escape(callee)}\s*\(", body[close:pos]):
        return None
    name = assign.group(1)
    if re.search(rf"\b{re.escape(name)}\s*=(?!=)", body[close:pos]):
        return None
    return name


def _prepared_body(code: str) -> tuple[str, str, list[tuple[str, int, int]]] | None:
    code = syntax._strip_calling_convention(code)
    code = syntax._rewrite_thunk_calls(code)
    brace = syntax._opening_brace(code)
    if brace < 0:
        return None
    signature = syntax._c_signature(code)
    body = code[brace:]
    return signature, body, c_text._direct_calls(body, syntax._SKIP_CALLS)


def _forwarded_param_counts(
    corpus: dict[str, dict],
    origins: dict[str, dict],
    sites: dict[str, dict[int, list[int]]],
    entries: dict[str, int],
    arity: dict[str, int],
    params: dict[str, int],
    hand: set[str],
) -> dict[str, int]:
    """How many parameters a function needs so a forwarded entry register has a name.

    The count grows only when every compiled caller can already pass the new
    registers, from an immediate or from a parameter that caller already has.
    """
    prepared: dict[str, tuple[str, str, list[tuple[str, int, int]]]] = {}
    wanted: dict[str, int] = {}
    for name, row in corpus.items():
        if name in hand:
            continue
        parsed = _prepared_body(row["decompiled_c"])
        if parsed is None:
            continue
        prepared[name] = parsed
        if name not in origins:
            continue
        signature, body, events = parsed
        stripped = syntax._strip_calling_convention(row["decompiled_c"])
        brace = syntax._opening_brace(stripped)
        if brace < 0 or syntax._last_declarator(stripped[:brace], name) is None:
            continue
        nparams = params.get(name, len(syntax._param_names(signature)))
        state = origins[name]
        grouped = sites.get(name) or {}
        counts: dict[int, int] = {}
        usable_events = []
        for callee, open_at, close in events:
            entry = entries.get(callee)
            if entry is None:
                continue
            counts[entry] = counts.get(entry, 0) + 1
            usable_events.append((callee, open_at, close, entry))
        highest = nparams
        cursor: dict[int, int] = {}
        for callee, open_at, close, entry in usable_events:
            existing = c_text._split_args(body[open_at + 1:close])
            if len(existing) == 1 and not existing[0].strip():
                existing = []
            slot = cursor.get(entry, 0)
            cursor[entry] = slot + 1
            if counts[entry] != len(grouped.get(entry, ())):
                continue
            if slot >= len(grouped.get(entry, ())):
                continue
            addr = grouped[entry][slot]
            need = params.get(callee, 0)
            if len(existing) >= need:
                continue
            for index in range(len(existing), need):
                origin = _argument_origin(state.get(addr, {}), index)
                if len(origin) != 1:
                    continue
                item = next(iter(origin))
                if item[0] == "entry" and item[1] - 6 >= nparams:
                    highest = max(highest, item[1] - 5)
        if highest > nparams:
            wanted[name] = highest
    blocked: set[str] = set()
    for name, (signature, body, events) in prepared.items():
        params_here = syntax._param_names(signature)
        types_here = syntax._signature_param_types(signature)
        state = origins.get(name) or {}
        grouped = sites.get(name) or {}
        counts = {}
        usable_events = []
        for callee, open_at, close in events:
            if callee not in wanted:
                continue
            entry = entries.get(callee)
            if entry is None:
                continue
            counts[entry] = counts.get(entry, 0) + 1
            usable_events.append((callee, open_at, close, entry))
        cursor = {}
        for callee, open_at, close, entry in usable_events:
            if callee in blocked:
                continue
            existing = c_text._split_args(body[open_at + 1:close])
            if len(existing) == 1 and not existing[0].strip():
                existing = []
            slot = cursor.get(entry, 0)
            cursor[entry] = slot + 1
            if counts[entry] != len(grouped.get(entry, ())):
                blocked.add(callee)
                continue
            if slot >= len(grouped.get(entry, ())):
                blocked.add(callee)
                continue
            addr = grouped[entry][slot]
            old_count = params.get(callee, 0)
            for index in range(old_count, wanted[callee]):
                if index < len(existing):
                    continue
                if _emit_origin(_argument_origin(state.get(addr, {}), index), params_here, types_here) is None:
                    blocked.add(callee)
                    break
    return {name: count for name, count in wanted.items() if name not in blocked}


def _widen_signature(code: str) -> str:
    """Give a forwarded incoming register the parameter the bytes already pass."""
    if syntax._signature_name(syntax._c_signature(code)) == "boot_diagnostic_replay_handoff_session":
        # 6508 keeps incoming r6 in ep; the caller supplies its copied record.
        code = code.replace(
            "boot_diagnostic_replay_handoff_session(void)",
            "boot_diagnostic_replay_handoff_session(uint in_r6)",
        )
        return re.sub(
            r"^[ \t]*int in_r6(?:\s*=\s*0x11111111)?;[ \t]*\n",
            "", code, flags=re.M,
        )
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    signature = syntax._c_signature(code)
    name = syntax._signature_name(signature)
    facts = _call_facts()
    if name in facts["hand"]:
        return code
    target = facts["params"].get(name, 0)
    current = syntax._param_names(signature)
    if target <= len(current):
        return code
    found = syntax._last_declarator(code[:brace], name)
    if found is None:
        return code
    open_at, close = found
    inside = code[open_at + 1:close]
    stripped = syntax._strip_comments(inside).strip()
    names = set(current)
    added: list[str] = []
    for index in range(len(current), target):
        param = f"param_{index + 1}"
        if param in names:
            param = f"param_{index + 1}_in"
        names.add(param)
        ctype = "byte" if name == "count_nonzero_dtcs_matching_status_mask_526cc" and index == 0 else "undefined4"
        added.append(f"{ctype} {param}")
    extra = ", ".join(added)
    replacement = extra if not stripped or stripped == "void" else inside.rstrip() + ", " + extra
    return code[:open_at + 1] + replacement + code[close:]


def _saved_context_regs(fn) -> set[int]:
    """A straight-line, unexposed push/pop frame restores its saved GPRs."""
    if len(fn.insts) < 3 or fn.insts[0].addr != fn.entry:
        return set()
    first, restore, last = fn.insts[0], fn.insts[-2], fn.insts[-1]
    pushed = syntax._stmt_parts(first.stmt) if first.stmt else None
    popped = syntax._stmt_parts(restore.stmt) if restore.stmt else None
    if (
        pushed is None or popped is None or pushed[0] != "pushsp"
        or popped[0] != "popsp" or pushed[1] != popped[1]
        or len(pushed[1]) != 2 or any(reg is None for reg in pushed[1])
        or not 1 <= pushed[1][0] <= pushed[1][1] == 31
        or last.kind != "jmp" or last.reg != 31
    ):
        return set()
    if any(left.addr + left.size != right.addr for left, right in zip(fn.insts, fn.insts[1:])):
        return set()
    # No body instruction may expose or change SP. Stores must address the
    # fixed global bases, never a pointer that could alias the saved frame.
    state = {3: {("sp", 0)}, 4: {("global", 4)}, 5: {("global", 5)}}
    for inst in fn.insts[1:-2]:
        if inst.kind == "jarl" and inst.link == 31:
            continue
        if inst.kind == "nop":
            continue
        parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
        if inst.kind != "alu" or parsed is None:
            return set()
        op, args = parsed
        if op in {"prepare", "pushsp", "popsp"} or _reads_reg(inst, 3):
            return set()
        if op in {"st8", "st16", "st32"}:
            if len(args) != 3 or (
                args[1] != 0 and state.get(args[1]) != {("global", args[1])}
            ):
                return set()
        elif op in {"set1", "not1", "clr1", "set1r", "not1r", "clr1r"}:
            return set()
        state = _transfer(state, inst)
        if state.get(3) != {("sp", 0)}:
            return set()
    return set(range(pushed[1][0], pushed[1][1] + 1))


def _writes_r10(fn) -> bool:
    """True when this function writes r10 without a proven context restore."""
    if 10 in _CONTEXT_SAVED.get(fn.entry, ()):
        return False
    for inst in fn.insts:
        if inst.kind in {"jarl", "jarl_ind", "jr", "callt", "jmp", "br", "b", "dispose"}:
            continue
        parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
        if parsed is None:
            continue
        name, args = parsed
        if name == "popsp":
            if len(args) >= 2 and args[0] is not None and args[1] is not None and args[0] <= 10 <= args[1]:
                return True
            continue
        if not args or name in _NO_GPR_WRITE or name in {"prepare", "pushsp"}:
            continue
        if name in {"bsw", "bsh", "hsw", "hsh", "sch0r", "sch1r", "sch0l", "sch1l"}:
            dests = [args[1] if len(args) > 1 else None]
        elif name == "mul" and len(args) >= 2:
            dests = args[:2]
        elif name == "div3" and len(args) >= 3:
            dests = [args[0], args[2]]
        else:
            dests = [args[0]]
        if 10 in dests:
            return True
    return False


def _initial_r10(fn) -> int | None:
    """One entry r10 immediate, followed only by call-produced r10 values."""
    live = {10: {("live",)}}
    initial = None
    for inst in fn.insts:
        if inst.kind in {"b", "br", "jr", "jarl", "jarl_ind", "callt", "jmp", "switch", "loop", "dispose"}:
            if initial is None:
                return None
            continue
        changed = _transfer(live, inst).get(10)
        if changed != live[10]:
            if initial is None and changed is not None and len(changed) == 1 and next(iter(changed))[0] == "imm":
                initial = next(iter(changed))[1]
                continue
            return None
    return initial


def _counter_imms(fn) -> set[int] | None:
    """Immediates written into r10 when the only later updates are in place.

    A loop that counts in r10 (`movi` then `addi_imm5` and a narrow) leaves
    `fail` in the origin lattice because the add is not folded across the
    back edge. The immediate is still the counter's start value.
    """
    imms: set[int] = set()
    saw_add = False
    for inst in fn.insts:
        if inst.kind in {"jarl", "jarl_ind", "jr", "callt"}:
            return None
        parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
        if parsed is None:
            continue
        name, args = parsed
        if not args or name in _NO_GPR_WRITE or name in {"prepare", "pushsp", "popsp"}:
            continue
        if name in {"bsw", "bsh", "hsw", "hsh", "sch0r", "sch1r", "sch0l", "sch1l"}:
            dest = args[1] if len(args) > 1 else None
        elif name == "mul" and len(args) >= 2:
            dest = None if 10 in args[:2] else args[0]
            if 10 in args[:2]:
                return None
        elif name == "div3" and len(args) >= 3 and 10 in {args[0], args[2]}:
            return None
        else:
            dest = args[0]
        if dest != 10:
            continue
        if name == "movi" and len(args) > 1 and args[1] is not None:
            imms.add(args[1] & 0xFFFFFFFF)
            continue
        if name == "mov" and len(args) > 1 and args[1] == 0:
            imms.add(0)
            continue
        if name == "addi_imm5":
            saw_add = True
            continue
        if name in _NARROW:
            continue
        return None
    if not saw_add or not imms:
        return None
    return imms


def _r10_preservers(
    direct: set[int], calls: dict[int, list[int]], callt: set[int],
) -> set[int]:
    """Functions whose own bytes and callees leave the caller's r10 unchanged."""
    restored = {addr for addr, regs in _CONTEXT_SAVED.items() if 10 in regs}
    preserve = restored | {addr for addr in calls if addr not in direct and addr not in callt}
    changed = True
    while changed:
        changed = False
        for addr in list(preserve):
            if addr not in restored and any(target not in preserve for target in calls.get(addr, ())):
                preserve.discard(addr)
                changed = True
    return preserve


def _passed_gps(fn, state: dict, names_at: dict[int, str]) -> list[tuple[str, set]]:
    """r4 at each direct call. r4 is callee-saved, so this is the callee's gp."""
    found: list[tuple[str, set]] = []
    for inst in fn.insts:
        if inst.kind in {"jarl", "jr"} and inst.target in names_at:
            found.append((names_at[inst.target], set(state.get(inst.addr, {}).get(4, {_FAIL}))))
            continue
        if inst.kind != "jmp" or not inst.reg or inst.addr not in state:
            continue
        held = state[inst.addr].get(inst.reg, set())
        if len(held) == 1 and next(iter(held))[0] == "imm" and next(iter(held))[1] in names_at:
            found.append((names_at[next(iter(held))[1]], set(state[inst.addr].get(4, {_FAIL}))))
    return found


def _returned_r4(fn, state: dict) -> int | None:
    """The immediate left in r4 when every return agrees."""
    imms: list[int] = []
    for inst in fn.insts:
        key = ("ret", inst.addr)
        if key not in state:
            continue
        origin = state[key].get(4, set())
        if len(origin) != 1 or next(iter(origin))[0] != "imm":
            return None
        imms.append(next(iter(origin))[1] & 0xFFFFFFFF)
    if not imms or len(set(imms)) != 1:
        return None
    return imms[0]


def _entry_gps(walked: list[tuple[dict, object]], names_at: dict[int, str]) -> dict[str, dict]:
    """Origins after r4 is the one global pointer every caller passes."""
    global _R4_SETTERS
    by_name = {row["name"]: fn for row, fn in walked}
    entry: dict[str, int] = {}
    state_of: dict[str, dict] = {}
    wave = list(by_name)
    setters_done = False
    for _round in range(len(by_name) + 1):
        if not wave:
            break
        for name in wave:
            state_of[name] = _function_origins(by_name[name], entry.get(name))
        if not setters_done:
            found: dict[int, int] = {}
            for row, fn in walked:
                left = _returned_r4(fn, state_of[row["name"]])
                if left is not None:
                    found[int(row["addr"], 16)] = left
            setters_done = True
            if found:
                _R4_SETTERS = found
                state_of.clear()
                entry = {}
                wave = list(by_name)
                continue
        incoming: dict[str, list[set]] = {}
        for name, state in state_of.items():
            for callee, origin in _passed_gps(by_name[name], state, names_at):
                incoming.setdefault(callee, []).append(origin)
        new_entry: dict[str, int] = {}
        for name, origins in incoming.items():
            imms = []
            agreed = True
            for origin in origins:
                if len(origin) == 1 and next(iter(origin))[0] == "imm":
                    imms.append(next(iter(origin))[1] & 0xFFFFFFFF)
                    continue
                agreed = False
                break
            if agreed and imms and len(set(imms)) == 1:
                new_entry[name] = imms[0]
        wave = [
            name for name in set(new_entry) | set(entry)
            if new_entry.get(name) != entry.get(name) and name in by_name
        ]
        entry = new_entry
    return state_of


_BOOT_RELOCATED_COPIES = {
    "boot_relocated_8370": (0x8370, 0xFEBF1000, 42),
    "boot_relocated_84f8": (0x84F8, 0xFEBF1188, 36),
    "boot_relocated_851c": (0x851C, 0xFEBF11AC, 38),
    "boot_relocated_8542": (0x8542, 0xFEBF11D2, 30),
    "boot_relocated_8560": (0x8560, 0xFEBF11F0, 200),
    "boot_relocated_8628": (0x8628, 0xFEBF12B8, 116),
}


def _walk_boot_relocated_abi(image: bytes, row: dict):
    """Decode the six recovered boot-copy bodies to recover ABI facts."""
    from dataclasses import replace
    from .lifting.graph import LiftedFn, walk_symbol

    copy = _BOOT_RELOCATED_COPIES.get(row["name"])
    if copy is None:
        return None
    source, entry, size = copy
    ranges = [(entry, entry + size - 1)]
    if int(row["addr"], 16) != entry or [tuple(span) for span in row["ranges"]] != ranges:
        return None
    fn = walk_symbol(image, {
        **row, "addr": hex(source), "ranges": [(source, source + size - 1)],
    })
    if fn is None:
        return None
    delta = entry - source
    # Only PC-relative control-flow operands move with the copied bytes.
    # Absolute immediates (RAM tables, vectors and MMIO) retain their values.
    insts = [
        replace(
            inst, addr=inst.addr + delta,
            target=inst.target + delta if inst.kind in {"b", "br", "jr", "jarl", "loop"} else inst.target,
        )
        for inst in fn.insts
    ]
    return LiftedFn(entry, row["name"], ranges, insts, sites={inst.addr for inst in insts})


def _call_facts() -> dict:
    """Argument registers and r10 at native call sites, from the function bytes."""
    from tools.targets.camry.decomp.conversion import rewrite_abi, rewrite_types

    global _CALL_FACTS, _ARG_CLOBBERS, _R10_PRESERVE
    if _CALL_FACTS is not None:
        return _CALL_FACTS
    from .lifting.decode import decode_at
    from .lifting.graph import load_image, walk_symbol
    from tools.project.pseudo import load_corpus

    image = load_image()
    symbols = tree.load_symbols()
    entries = {row["name"]: int(row["addr"], 16) for row in symbols}
    names_at = {addr: name for name, addr in entries.items()}
    origins: dict[str, dict] = {}
    sites: dict[str, dict[int, list[int]]] = {}
    ret_target: dict[str, int] = {}
    ret_r10: dict[str, list[set]] = {}
    saved_pmr: set[str] = set()
    stored_r10: set[str] = set()
    counters: dict[str, set[int]] = {}
    initial_r10: dict[str, int] = {}
    arity: dict[str, int] = {}
    walked = []
    direct_writes: dict[int, set[int]] = {}
    direct_calls: dict[int, list[int]] = {}
    callt: set[int] = set()
    direct_r10: set[int] = set()
    for row in symbols:
        fn = walk_symbol(image, row)
        if fn is None:
            fn = _walk_boot_relocated_abi(image, row)
        if fn is None:
            continue
        walked.append((row, fn))
        saved = _saved_context_regs(fn)
        if saved:
            _CONTEXT_SAVED[fn.entry] = saved
        # Resolve immutable callback words from native register origins.
        # The decompiler corpus's pointer labels are stale.
        state = _function_origins(fn)
        for inst in fn.insts:
            if inst.kind not in {"jarl_ind", "jmp"}:
                continue
            held = state.get(inst.addr, {}).get(inst.reg, set())
            if len(held) != 1:
                continue
            item = next(iter(held))
            if item[0] == "imm" and item[1] in names_at:
                _STATIC_CALL_TARGETS[inst.addr] = item[1]
            elif item[0] == "mem" and item[1] == 4 and 0 <= item[2] <= len(image) - 4:
                target = int.from_bytes(image[item[2]:item[2] + 4], "little")
                if target in names_at:
                    _STATIC_CALL_TARGETS[inst.addr] = target
        addr = int(row["addr"], 16)
        written, calls, has_callt = _direct_arg_writes(fn)
        direct_writes[addr] = written
        direct_calls[addr] = calls
        if has_callt:
            callt.add(addr)
        if _writes_r10(fn):
            direct_r10.add(addr)
        imms = _counter_imms(fn)
        if imms is not None:
            counters[row["name"]] = imms
        initial = _initial_r10(fn)
        if initial is not None:
            initial_r10[row["name"]] = initial
    _ARG_CLOBBERS = _arg_clobber_map(direct_writes, direct_calls, callt)
    _R10_PRESERVE = _r10_preservers(direct_r10, direct_calls, callt)
    states = _entry_gps(walked, names_at)
    ram: dict[int, set[int]] = {}
    for row, fn in walked:
        state = states[row["name"]]
        origins[row["name"]] = state
        for inst in fn.insts:
            parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
            if parsed is None:
                continue
            op, operands = parsed
            if op not in {"ld8s", "ld8u", "ld16s", "ld16u", "ld32", "st8", "st16", "st32"}:
                continue
            if len(operands) < 3 or not isinstance(operands[2], int):
                continue
            base = {("imm", 0)} if operands[1] == 0 else state.get(inst.addr, {}).get(operands[1], set())
            if len(base) == 1 and next(iter(base))[0] == "imm":
                address = (next(iter(base))[1] + operands[2]) & 0xffffffff
                width = syntax._access_width(inst.text)
                if width is not None:
                    ram.setdefault(address, set()).add(width)
        grouped: dict[int, list[int]] = {}
        for inst in fn.insts:
            target = inst.target if inst.kind in {"jarl", "jr"} else _STATIC_CALL_TARGETS.get(inst.addr)
            if target in names_at:
                grouped.setdefault(target, []).append(inst.addr)
        # mov imm, reg; jmp [reg] is a tail call. Pair it only when this
        # function does not also call that target with jarl/jr, so an existing
        # match does not become a count mismatch.
        for inst in fn.insts:
            if inst.kind != "jmp" or not inst.reg or inst.addr not in state:
                continue
            held = state[inst.addr].get(inst.reg, set())
            if len(held) != 1 or next(iter(held))[0] != "imm":
                continue
            target = next(iter(held))[1]
            if target in names_at and target not in grouped:
                grouped.setdefault(target, []).append(inst.addr)
        sites[row["name"]] = grouped
        targets = []
        pmr_origins: list[set] = []
        for inst in fn.insts:
            key = ("ret", inst.addr)
            if key not in state:
                continue
            origin = state[key].get(10, set())
            if inst.kind in {"jr", "br"} and inst.target not in fn.sites:
                origin = {("call", inst.target)}
            if inst.kind == "jmp" and inst.reg:
                held = state[key].get(inst.reg, set())
                if len(held) == 1 and next(iter(held))[0] == "imm" and next(iter(held))[1] in names_at:
                    origin = {("call", next(iter(held))[1])}
            targets.append(origin)
            pmr_origins.append(origin)
        ret_r10[row["name"]] = targets
        if targets and all(len(item) == 1 and next(iter(item))[0] == "call" for item in targets):
            called = {next(iter(item))[1] for item in targets}
            if len(called) == 1 and None not in called:
                ret_target[row["name"]] = next(iter(called))
        if pmr_origins and all(len(item) == 1 and next(iter(item)) == ("sreg", 11, 2) for item in pmr_origins):
            saved_pmr.add(row["name"])
        arity[row["name"]] = _argument_arity(fn, state)
        ret_addrs = [key[1] for key in state if isinstance(key, tuple) and key[0] == "ret"]
        if len(ret_addrs) == 1:
            ret_at = ret_addrs[0]
            index = next((i for i, inst in enumerate(fn.insts) if inst.addr == ret_at), None)
            if index:
                prev = fn.insts[index - 1]
                parsed = syntax._stmt_parts(prev.stmt) if prev.stmt else None
                if (
                    prev.addr + prev.size == ret_at
                    and parsed is not None
                    and parsed[0] in {"st8", "st16", "st32"}
                    and parsed[1]
                    and parsed[1][0] == 10
                ):
                    stored_r10.add(row["name"])
    _meta, functions = load_corpus(
        REPO_ROOT / "data" / "generated" / tree.TARGET / "decompilations.jsonl"
    )
    corpus: dict[str, dict] = {}
    for row in functions:
        corpus.setdefault(row["name"], row)
    hand_types = layout._hand_param_types()
    hand_names = set(hand_types)
    params: dict[str, int] = {}
    returns: dict[str, str] = {}
    for name, row in corpus.items():
        signature = syntax._c_signature(syntax._strip_calling_convention(row["decompiled_c"]))
        if name in hand_types:
            params[name] = len(hand_types[name])
        else:
            params[name] = len(syntax._signature_param_types(signature))
        returns[name] = syntax._return_type_of(signature, name)
    from .sources import load_c_bodies, retained_paths

    retained, _duplicates = load_c_bodies(retained_paths())
    verified = {
        row["name"] for row in tree.load_matched() if row.get("status") in tree._CHECKED_STATUS
    }
    for name in verified & retained.keys():
        signature = syntax._c_signature(retained[name])
        params[name] = len(syntax._signature_param_types(signature))
        returns[name] = syntax._return_type_of(signature, name)
    header = syntax._strip_comments((tree.ROOT / "include" / "camry.h").read_text(encoding="utf-8"))
    for match in re.finditer(
        r"^([A-Za-z_][A-Za-z0-9_ \t\*]*?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        header,
        flags=re.M,
    ):
        returns[match.group(2)] = " ".join(match.group(1).split())
    context_saved = {
        names_at[addr]: regs for addr, regs in _CONTEXT_SAVED.items() if addr in names_at
    }
    # A saved incoming register pair is not a produced 64-bit C result.
    # Normalize this interface before planning any forwarding wrappers.
    for name, saved in context_saved.items():
        if name not in corpus or name in hand_names:
            continue
        raw = syntax._strip_calling_convention(corpus[name]["decompiled_c"])
        normalized = rewrite_abi._rewrite_returned_call(raw, saved_context=saved)
        if normalized != raw:
            returns[name] = syntax._return_type_of(syntax._c_signature(normalized), name)
    # 90304/90362 save incoming r8 after 90248/9022a, which preserve it.
    # Their 8ee44/8ee60 veneers forward the same three incoming registers.
    for name in ("dispatch_freshness_export_by_configured_id_902e4", "dispatch_freshness_import_by_configured_id_90342", "get_configured_freshness_when_ready_8ee44", "set_configured_freshness_when_ready_8ee60"):
        params[name] = 3
        arity[name] = max(arity.get(name, 0), 3)
    # 92bc2/92b98 preserve the queue register; 93276 also forwards r7.
    # FDFFC is a jump veneer to B15AC's incoming r6.
    # 7b540 passes PDU/retry/available in r7-r9. The immutable callback
    # chain 81a66 -> 81990 -> 7be7e -> 926d2 forwards all three unchanged.
    # 929EC supplies the PDU in r7; 92A52 -> 81B92 -> immutable 81BC6
    # forwards it unchanged to 81C1A's lower transmit callback.
    # 81A1A/81886/7BE58 forward the start-receive PDU, total length and
    # available output; 81A34/818E0/7BE6C forward the copy PDU and output.
    for name, count in (
        ("dcm_refresh_response_copy_cursor_from_head_92bd8", 1), ("dcm_replace_response_queue_head_93276", 2), ("thunk_set_indexed_request_and_clear_complement_b15ac", 1),
        ("call_21cf0_with_masked_u16_81a66", 4), ("query_packed_id_slot20_81990", 4), ("dispatch_dcm_copy_transmit_data_callback_7be7e", 4),
        ("invoke_prefixed_id_callback_21ccc_92a52", 2), ("call_21ccc_with_prefixed_u16_81b92", 2), ("query_22962_mapped_id_slot0_81bc6", 2),
        ("call_21ce8_with_masked_u16_and_two_values_81a1a", 4), ("query_packed_id_slot12_with_buffer_and_u16_81886", 4), ("dispatch_dcm_start_of_reception_callback_7be58", 4),
        ("call_21cec_with_masked_u16_81a34", 3), ("query_packed_id_slot16_818e0", 3), ("dispatch_dcm_copy_receive_data_callback_7be6c", 3),
    ):
        params[name] = count
        arity[name] = max(arity.get(name, 0), count)
    # 526d4 saves the incoming status mask before passing the stack snapshot.
    params["count_nonzero_dtcs_matching_status_mask_526cc"] = 1
    arity["count_nonzero_dtcs_matching_status_mask_526cc"] = 1
    returns["serialize_event_and_merge_selected_output_8e074"] = "uint"
    returns["nvm_write_copy_header_from_source_slot_77170"] = "uint"
    returns["dispatch_ecm_status_exception_71ae4"] = "void"
    trailing: dict[str, str] = {}
    for name, row in corpus.items():
        if name in hand_names or name in verified or returns.get(name) != "void":
            continue
        statement = syntax._trailing_call(syntax._strip_calling_convention(row["decompiled_c"]))
        if statement is None:
            continue
        callee = re.match(r"[A-Za-z_][A-Za-z0-9_]*", statement)
        callee_name = callee.group(0) if callee is not None else names_at.get(ret_target.get(name))
        if callee_name not in entries or ret_target.get(name) != entries[callee_name]:
            continue
        trailing[name] = callee_name
    planned: dict[str, str] = {}

    def resolve(name: str, stack: set[str]) -> str:
        if name in planned:
            return planned[name]
        current = returns.get(name, "void")
        if name in hand_names or current != "void" or name not in trailing:
            return current or "void"
        if name in stack:
            return "undefined4"
        inner = resolve(trailing[name], stack | {name})
        if not inner or inner == "void" or "(" in inner:
            return "void"
        planned[name] = inner
        return inner

    for name in list(trailing):
        resolve(name, set())
    # A forwarding wrapper reads every incoming register its callee reads.
    changed = True
    while changed:
        changed = False
        for caller, grouped in sites.items():
            count = arity.get(caller, 0)
            for target, addresses in grouped.items():
                callee = names_at.get(target)
                required = params.get(callee, 0)
                for address in addresses:
                    state = origins[caller].get(address, {})
                    for index in range(required):
                        for item in _argument_origin(state, index):
                            if item[0] == "entry":
                                count = max(count, item[1] - 5)
            if count > arity.get(caller, 0):
                arity[caller] = count
                changed = True
    widened = _forwarded_param_counts(
        corpus, origins, sites, entries, arity, params, hand_names
    )
    need = {
        name: count
        for name, count in params.items()
    }
    for name, count in widened.items():
        params[name] = count
        need[name] = count
    for row in functions:
        for ref in row.get("data_references") or []:
            try:
                address = int(ref["to_addr"], 16)
                origin = int(ref["from_addr"], 16)
            except (KeyError, TypeError, ValueError):
                continue
            inst = decode_at(image, origin)
            if inst is None:
                continue
            width = syntax._access_width(inst.text)
            if width is None:
                continue
            ram.setdefault(address, set()).add(width)
    _CALL_FACTS = {
        "entries": entries,
        "names": names_at,
        "origins": origins,
        "sites": sites,
        "indirect_sites": {
            row["name"]: [inst.addr for inst in fn.insts if inst.kind == "jarl_ind"]
            for row, fn in walked
        },
        "arity": arity,
        "params": params,
        "need": need,
        "hand": hand_names,
        "planned": planned,
        "saved_pmr": saved_pmr,
        "preserves": {names_at[addr] for addr in _R10_PRESERVE if addr in names_at},
        "context_saved": context_saved,
        "returns": returns,
        "ret_r10": ret_r10,
        "counters": counters,
        "initial_r10": initial_r10,
        "stored_r10": stored_r10,
        "ram": {addr: next(iter(widths)) for addr, widths in ram.items() if len(widths) == 1},
    }
    # Publish recovered producer interfaces before rewriting their callers.
    # The body rewriters use this same cache; do not maintain a second set
    # of prototypes based only on Ghidra's original void declarations.
    changed = True
    while changed:
        changed = False
        for name, row in corpus.items():
            if name in hand_names or name in verified or returns.get(name) != "void":
                continue
            code = syntax._strip_calling_convention(row["decompiled_c"])
            if syntax._return_type_of(syntax._c_signature(code), name) != "void":
                continue
            for rewrite in (
                rewrite_abi._rewrite_saved_pmr, rewrite_abi._rewrite_stored_result, rewrite_abi._rewrite_held_result,
                rewrite_abi._rewrite_returned_call, rewrite_types._rewrite_merged_call_results,
            ):
                code = rewrite(code)
            recovered = syntax._return_type_of(syntax._c_signature(code), name)
            if recovered and recovered != "void":
                returns[name] = recovered
                changed = True
        for name in trailing:
            if name not in planned:
                resolve(name, set())
    return _CALL_FACTS


def _argument_arity(fn, state: dict) -> int:
    """Highest incoming register or stack word whose value reaches a read."""
    index_of = {inst.addr: index for index, inst in enumerate(fn.insts)}
    read: set[int] = set()
    for addr, regs in state.items():
        if not isinstance(addr, int) or addr not in index_of:
            continue
        inst = fn.insts[index_of[addr]]
        for reg in _TRACKED:
            if _reads_reg(inst, reg):
                read.update(item[1] for item in regs.get(reg, ()) if item[0] == "entry")
    if not read:
        return 0
    return max(read) - 5


def _reads_reg(inst, reg: int) -> bool:
    if inst.kind in {"jmp", "switch", "jmpdisp"} and inst.reg == reg:
        return True
    if inst.kind == "loop" and inst.reg == reg:
        return True
    if inst.kind == "dispose" and inst.ret == reg:
        return True
    parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
    if parsed is None:
        return False
    name, args = parsed
    if name in {"mov", "not", "addi", "movea", "movhi", "ori", "xori", "andi", "mulhi", "satsubi"}:
        return len(args) > 1 and args[1] == reg
    if name in {"or", "xor", "and", "add", "sub", "subr", "cmp", "tst", "satadd", "satsub", "satsubr", "mulh", "divh2"}:
        return reg in args[:2]
    if name in _NARROW or name in {"addi_imm5", "cmpi", "shl_imm", "shr", "sar_imm", "mulhi5", "sataddi", "sasf"}:
        return args and args[0] == reg
    if name in {"ld8s", "ld8u", "ld16s", "ld16u", "ld32"}:
        return len(args) > 1 and args[1] == reg
    if name in {"st8", "st16", "st32", "set1r", "not1r", "clr1r", "tst1r"}:
        return reg in args[:2]
    if name in {"set1", "not1", "clr1", "tst1", "ldsr"}:
        return args and args[0] == reg
    if name == "cmovi":
        return len(args) > 1 and args[1] == reg
    if name == "cmov":
        return reg in args[1:3]
    if name in {"sbf", "adf"}:
        return reg in args[1:3]
    if name in {"shl_reg", "shr_reg", "sar_reg"}:
        return reg in args[1:3]
    if name in {"muli", "mului"}:
        return args and args[0] == reg
    if name == "mul":
        return reg in args[2:4]
    if name == "div3":
        return reg in args[:2]
    if name in {"pushsp", "popsp"}:
        return len(args) >= 2 and args[0] is not None and args[1] is not None and args[0] <= reg <= args[1]
    return False


def _stack_local(code: str, delta: int) -> str | None:
    """The Ghidra local whose address is entry-SP + delta."""
    if delta >= 0:
        return None
    suffix = format(-delta, "x")
    names: list[str] = []
    for match in re.finditer(
        rf"\b([A-Za-z_][A-Za-z0-9_]*Stack_{suffix}|local_{suffix})\b",
        code,
    ):
        name = match.group(1)
        if name in names:
            continue
        if re.search(rf"\b{re.escape(name)}\s*(?:\[[^\]]*\])?\s*;", code):
            names.append(name)
    if len(names) != 1:
        candidates: list[tuple[int, str]] = []
        structs = layout._struct_rows()
        for found in re.finditer(
            r"^\s*(\w+)\s+((?:local|[A-Za-z_]\w*Stack|stack_record)_([0-9a-fA-F]+))"
            r"\s*(?:\[(\d+)\])?\s*;", code, re.M,
        ):
            ctype, name, offset, count = found.groups()
            width = layout._STACK_WIDTH.get(ctype, structs.get(ctype, {}).get("size"))
            if width is None:
                continue
            size = int(width) * int(count or 1)
            displacement = delta + int(offset, 16)
            if 0 <= displacement <= size:
                base = name if count else f"&{name}"
                candidates.append((size, f"((uint8_t *){base} + {displacement})"))
        if candidates:
            return min(candidates)[1]
        return None
    name = names[0]
    if re.search(rf"\b{re.escape(name)}\s*\[", code):
        return name
    return f"&{name}"


def _assignment_prefix(body: str, open_at: int) -> tuple[str, int, int] | None:
    """`var = ` immediately before the call whose '(' is open_at."""
    cursor = open_at
    while cursor > 0 and body[cursor - 1] in " \t\n\r":
        cursor -= 1
    while cursor > 0 and (body[cursor - 1].isalnum() or body[cursor - 1] == "_"):
        cursor -= 1
    name_start = cursor
    while cursor > 0 and body[cursor - 1] in " \t\n\r":
        cursor -= 1
    while cursor > 0 and body[cursor - 1] == ")":
        opening = body.rfind("(", 0, cursor)
        if opening < 0 or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ \t*]*", body[opening + 1:cursor - 1]):
            return None
        cursor = opening
        while cursor > 0 and body[cursor - 1] in " \t\n\r":
            cursor -= 1
    while cursor > 0 and body[cursor - 1] in " \t\n\r":
        cursor -= 1
    if cursor == 0 or body[cursor - 1] != "=":
        return None
    equals = cursor - 1
    if equals > 0 and body[equals - 1] in "=<>!":
        return None
    cursor = equals
    while cursor > 0 and body[cursor - 1] in " \t\n\r":
        cursor -= 1
    var_end = cursor
    while cursor > 0 and (body[cursor - 1].isalnum() or body[cursor - 1] == "_"):
        cursor -= 1
    var = body[cursor:var_end]
    if not var or var in syntax._PRIMITIVE_TYPES or var in syntax._INT_TYPES:
        return None
    return var, cursor, name_start
_NO_GPR_WRITE = {"st8", "st16", "st32", "cmp", "cmpi", "tst", "prepare"}
