"""Adapt recovered C to the native machine-memory and register ABI."""
from __future__ import annotations

from tools.targets.camry.decomp import c_text, syntax
from tools.targets.camry.decomp.tree import COMMON_HEADER
from tools.targets.camry.decomp.tree import SYSTEM_REGISTERS
from tools.targets.camry.decomp.syntax import _c_signature
from tools.targets.camry.decomp.syntax import _stmt_parts
from tools.targets.camry.decomp.lifting.decode import decode_at
from collections import defaultdict
from tools.targets.camry.decomp.lifting.graph import load_image
from tools.targets.camry.decomp.tree import load_symbols
from tools.targets.camry.decomp.execution.calls import parse_signature
import re
from tools.targets.camry.decomp.lifting.graph import walk_symbol
from tools.targets.camry.decomp.c_text import _c_calls, _mask_comments
from tools.targets.camry.decomp.execution.model import STOP, _space
from tools.targets.camry.decomp.sources import _load_bodies


_INCOMING_LOCAL = re.compile(
    r"^(?P<indent>[ \t]+)"
    r"(?P<type>undefined[1248]|uint32_t|uint|int|int32_t)"
    r"[ \t]+(?P<name>in_ep|(?:in|unaff)_r\d+)\s*;\s*$"
)


_LOCAL_ARRAY = re.compile(
    r"^(?P<indent>[ \t]+)"
    r"(?P<prefix>(?:(?:static|const|volatile|unsigned|signed|struct|enum|union)[ \t]+)*)"
    r"(?P<type>[A-Za-z_][A-Za-z0-9_]*)[ \t*]+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)[ \t]*"
    r"(?P<array>(?:\[[ \t]*[^\]]+\])+)?\s*;\s*$"
)


_TRUE_LOOP = re.compile(r"while\s*\(\s*true\s*\)")


_LOOP_EXIT = re.compile(r"\b(?:break|return|goto)\b")


_SYMBOL_BY_NAME: dict[str, dict] | None = None


_HALT_IMAGE: bytes | None = None


_HALT_CACHE: dict[str, bool] = {}


_REACHES_HALT: set[str] | None = None


def _function_self_halts(name: str) -> bool:
    """The bytes branch to the same address and do not leave that instruction."""
    cached = _HALT_CACHE.get(name)
    if cached is not None:
        return cached
    global _SYMBOL_BY_NAME, _HALT_IMAGE
    if _SYMBOL_BY_NAME is None:
        _SYMBOL_BY_NAME = {row["name"]: row for row in load_symbols()}
        _HALT_IMAGE = load_image()
    row = _SYMBOL_BY_NAME.get(name)
    halts = False
    if row is not None and _HALT_IMAGE is not None:
        fn = walk_symbol(_HALT_IMAGE, row)
        halts = fn is not None and any(
            inst.kind == "br" and inst.target == inst.addr for inst in fn.insts
        )
    _HALT_CACHE[name] = halts
    return halts


def _reaches_halt() -> set[str]:
    """Halting bodies, requested stop owners, and every caller that reaches them."""
    global _REACHES_HALT
    _native_retained_stops()
    if _REACHES_HALT is not None:
        return _REACHES_HALT
    bodies, _duplicates = _load_bodies()
    callers: dict[str, set[str]] = defaultdict(set)
    indirect: set[str] = set()
    for name, body in bodies.items():
        callees = _c_calls(body)
        for callee in callees:
            callers[callee].add(name)
        if "camry_indirect" in callees:
            indirect.add(name)
    reach = indirect | {
        name for name, body in bodies.items()
        if _TRUE_LOOP.search(body) and _function_self_halts(name)
    } | {_NATIVE_STOP_SITES[pc][0] for pc in _NATIVE_WORKFLOW_REQUESTS}
    pending = list(reach)
    while pending:
        name = pending.pop()
        for caller in callers.get(name, ()):
            if caller not in reach:
                reach.add(caller)
                pending.append(caller)
    _REACHES_HALT = reach
    return reach


def _return_when_halted(text: str, value: str | None = None) -> str:
    """After a call that can halt, leave the caller too.

    An unbraced if/else or do/while keeps its following token. The check goes
    on the statement only when that token is not else or while. A non-void
    caller returns zero; the bytes stopped inside the callee, so that zero is
    not compared with r10.
    """
    reach = _reaches_halt()
    masked = _mask_comments(text)
    depth = 0
    inserts: list[int] = []
    index = masked.find("{") + 1
    indirect = False
    ident = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    while index < len(masked):
        char = masked[index]
        if char == "(":
            depth += 1
            index += 1
            continue
        if char == ")":
            depth = max(0, depth - 1)
            index += 1
            continue
        if char.isalpha() or char == "_":
            found = ident.match(masked, index)
            if found and (found.group(0) == "camry_indirect" or found.group(0) in reach):
                indirect = True
            if depth == 0 and found and found.group(0) in reach:
                nxt = c_text._skip_space(masked, found.end(), 1, chars=None)
                if nxt < len(masked) and masked[nxt] == "(":
                    close = c_text._match_delimiter(masked, nxt, quoted=False, required=False)
                    if close is not None:
                        semi = c_text._skip_space(masked, close + 1, 1, chars=None)
                        if semi < len(masked) and masked[semi] == ";":
                            after = c_text._skip_space(masked, semi + 1, 1, chars=None)
                            token = ident.match(masked, after)
                            word = token.group(0) if token else ""
                            if word not in {"else", "while"}:
                                inserts.append(semi + 1)
            index = found.end() if found else index + 1
            continue
        if char == ";" and depth == 0 and indirect:
            after = c_text._skip_space(masked, index + 1, 1, chars=None)
            token = ident.match(masked, after)
            if token is None or token.group(0) not in {"else", "while"}:
                inserts.append(index + 1)
                indirect = False
        index += 1
    piece = " if (camry_halt_propagate && camry_halted) return;"
    if value is not None:
        piece = f" if (camry_halt_propagate && camry_halted) return {value};"
    for at in reversed(dict.fromkeys(inserts)):
        text = text[:at] + piece + text[at:]
    return text


def _first_infinite_loop(
    text: str, halt: bool = False, value: str | None = None,
) -> tuple[int, int, str] | None:
    """Replace the first while(true) that has no break, return, or goto."""
    leave = "return;" if value is None else f"return {value};"
    if halt:
        leave = "camry_host_halt();" if value is None else f"camry_halted = 1; {leave}"
    masked = _mask_comments(text)
    for match in _TRUE_LOOP.finditer(masked):
        before = c_text._skip_space(masked, match.start() - 1, -1, chars=None)
        if before >= 0 and masked[before] == "}":
            open_at = c_text._match_delimiter(masked, before, "{}", step=-1, quoted=False, required=False)
            if open_at is None:
                continue
            do_at = c_text._skip_space(masked, open_at - 1, -1, chars=None)
            if do_at < 1 or masked[do_at - 1:do_at + 1] != "do":
                continue
            if do_at >= 2 and (masked[do_at - 2].isalnum() or masked[do_at - 2] == "_"):
                continue
            end = c_text._skip_space(masked, match.end(), 1, chars=None)
            if end >= len(masked) or masked[end] != ";":
                continue
            body = text[open_at + 1:before]
            if _LOOP_EXIT.search(_mask_comments(body)):
                continue
            start = do_at - 1
            return start, end + 1, "{\n" + body + "\n  " + leave + "\n}"
        after = c_text._skip_space(masked, match.end(), 1, chars=None)
        if after >= len(masked) or masked[after] != "{":
            continue
        close_at = c_text._match_delimiter(masked, after, "{}", quoted=False, required=False)
        if close_at is None:
            continue
        body = text[after + 1:close_at]
        if _LOOP_EXIT.search(_mask_comments(body)):
            continue
        return match.start(), close_at + 1, "{\n" + body + "\n  " + leave + "\n}"
    return None


def _note_root_calls(text: str, addresses: dict[str, int]) -> str:
    """Note calls by their firmware caller, independent of C return-expression shape."""
    from tools.targets.camry.decomp.syntax import _signature_name

    caller = addresses.get(_signature_name(_c_signature(text)))
    masked = _mask_comments(text)
    brace = masked.find("{")
    if caller is None or brace < 0:
        return text
    inserts: list[tuple[int, str]] = []
    for name, opening, _closing in c_text._direct_calls(masked[brace + 1:], syntax._SKIP_CALLS):
        addr = addresses.get(name)
        if addr is None:
            continue
        end_name = opening + brace + 1
        while masked[end_name - 1].isspace():
            end_name -= 1
        start = end_name - len(name)
        inserts.extend((
            (start, f"(camry_note_call(0x{caller:x}u, 0x{addr:x}u), "),
            (end_name, ")"),
        ))
    # A live frame calls through (register updates, callee)(arguments).
    # The callee is still direct; note it without resolving a function word.
    framed = re.compile(
        r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|,\s*([A-Za-z_]\w*)\s*\)\s*\(''',
        re.S,
    )
    for match in framed.finditer(masked[brace + 1:]):
        name = match.group(1)
        addr = addresses.get(name)
        if addr is None:
            continue
        inserts.extend((
            (brace + 1 + match.start(1), f"(camry_note_call(0x{caller:x}u, 0x{addr:x}u), "),
            (brace + 1 + match.end(1), ")"),
        ))
    for at, piece in sorted(inserts, reverse=True):
        text = text[:at] + piece + text[at:]
    return text


def _seed_incoming_locals(text: str) -> str:
    """Initialize incoming GPRs and ep with the scenario sentinel.

    r6-r9 are included. A parameter already carries the oracle argument; these
    locals are the registers Ghidra did not turn into parameters. An incoming
    system register is the reset value in camry_SR, same as the uint form.
    """
    for name, (selector, register) in SYSTEM_REGISTERS.items():
        text = re.sub(
            rf"^([ \t]*undefined4 in_{name});[ \t]*$",
            rf"\1 = camry_SR[{selector}][{register}];",
            text,
            flags=re.M,
        )
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        match = _INCOMING_LOCAL.match(line)
        if match is None:
            out.append(line)
            continue
        ending = "\n" if line.endswith("\n") else ""
        out.append(
            f"{match.group('indent')}{match.group('type')} {match.group('name')} = 0x11111111;{ending}"
        )
    return "".join(out)


def _fill_local_arrays(text: str) -> str:
    """Give host stack objects the scenario fill before the body reads them.

    A fresh host frame contains zero or leftover stack. Initialize it with the
    fill byte the byte machine returns for an address it has not written.
    """
    from tools.targets.camry.decomp.layout import _STACK_WIDTH

    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        out.append(line)
        match = _LOCAL_ARRAY.match(line)
        if match is None:
            continue
        if "static" in match.group("prefix") or "const" in match.group("prefix"):
            continue
        name = match.group("name")
        target = name
        if match.group("array") is None:
            if (
                "*" in line
                or match.group("type") not in _STACK_WIDTH
                or not re.fullmatch(r"(?:local|[A-Za-z_]\w*Stack)_[0-9A-Fa-f]+", name)
                or not re.search(rf"(?<!&)&(?!&)\s*{re.escape(name)}\b", text)
            ):
                continue
            target = f"&{name}"
        ending = "\n" if line.endswith("\n") else ""
        out.append(
            f"{match.group('indent')}camry_fill_bytes({target}, sizeof {name});{ending}"
        )
    return "".join(out)


def _scenario_fill(scenario: dict) -> int:
    for region in scenario.get("memory", []):
        if "fill" in region:
            return int(region["fill"]) & 0xFF
    return 0


def _rebuilt_indirect_r6(name: str, param: str) -> str | None:
    """r6 at an argument-less indirect call that the bytes rebuilt.

    `ld.hu` into r6, then `shl r7, 16; or r6, r7`, then `jarl [reg]`. The
    stored call passes nothing, so the callee reads whatever the host left in
    the argument register. r7 is the incoming register: one parameter, so the
    harness leaves the scenario fill there and a caller can overwrite it.
    """
    from tools.targets.camry.decomp.layout import _function_entries
    from tools.targets.camry.decomp.conversion.rewrite_memory import _symbols_by_addr
    from tools.targets.camry.decomp.lifting.graph import load_image, walk_symbol

    entry = _function_entries().get(name)
    row = _symbols_by_addr().get(entry) if entry is not None else None
    if row is None:
        return None
    fn = walk_symbol(load_image(), row)
    if fn is None:
        return None
    for index, inst in enumerate(fn.insts):
        if inst.kind != "jarl_ind":
            continue
        window = [item.stmt or "" for item in fn.insts[max(0, index - 12):index]]
        loaded = None
        for cursor, stmt in enumerate(window):
            match = re.fullmatch(r"camry_ld16u\(6, (\d+), (\d+)\);", stmt)
            if match is None:
                continue
            if (
                cursor + 2 < len(window)
                and window[cursor + 1] == "camry_shl_imm(7, 16);"
                and window[cursor + 2] == "camry_or(6, 7);"
            ):
                loaded = match
                break
        if loaded is None:
            continue
        base = int(loaded.group(1))
        disp = int(loaded.group(2))
        movea = None
        scale = None
        added_tp = False
        for stmt in window:
            moved = re.fullmatch(rf"camry_movea\({base}, {base}, (-?\d+)\);", stmt)
            if moved is not None:
                movea = int(moved.group(1))
            scaled = re.fullmatch(r"camry_mulhi\(\d+, 6, (\d+)\);", stmt)
            if scaled is not None:
                scale = int(scaled.group(1))
            if stmt == f"camry_add({base}, 5);":
                added_tp = True
        if movea is None or scale is None or not added_tp:
            continue
        origin = (movea + disp) & 0xFFFFFFFF
        return (
            f"((uint32_t)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x{origin:x}u)"
            f" + (uint32_t)({param}) * {scale}u)))) | (camry_r7 << 16)), "
            "0x11111111u << 16, 0x11111111u, 0x11111111u"
        )
    return None


def _incoming_r7_names() -> set[str]:
    """Functions whose empty indirect call shifts the incoming r7 into r6."""
    cached = getattr(_incoming_r7_names, "cached", None)
    if cached is not None:
        return cached
    from tools.targets.camry.decomp.layout import _function_entries

    found = {name for name in _function_entries() if _rebuilt_indirect_r6(name, "param_1")}
    _incoming_r7_names.cached = found
    return found


def _assign_incoming_r7(text: str) -> str:
    """A discarded live value before the call is the r7 the bytes reloaded.

    Ghidra keeps it as `((void)(value), callee(arg))` when the signature has
    no second parameter. The callee reads `camry_r7`, which the harness sets
    from the scenario and a caller overwrites with this value.
    """
    names = _incoming_r7_names()
    if not any(name in text for name in names):
        return text
    pieces: list[str] = []
    cursor = 0
    start = 0
    prefix = "((void)("
    while True:
        at = text.find(prefix, start)
        if at < 0:
            break
        expr_open = at + len("((void)")
        try:
            expr_close = c_text._match_delimiter(text, expr_open)
        except ValueError:
            return text
        nxt = c_text._skip_space(text, expr_close + 1)
        if nxt >= len(text) or text[nxt] != ",":
            start = expr_close + 1
            continue
        nxt = c_text._skip_space(text, nxt + 1)
        end_name = nxt
        while end_name < len(text) and (text[end_name].isalnum() or text[end_name] == "_"):
            end_name += 1
        name = text[nxt:end_name]
        after = c_text._skip_space(text, end_name)
        if name not in names or after >= len(text) or text[after] != "(":
            start = end_name
            continue
        expr = text[expr_open:expr_close + 1]
        pieces.append(text[cursor:at])
        pieces.append(f"(camry_r7 = (uint32_t){expr}, {name}(")
        cursor = after + 1
        start = cursor
    if not pieces:
        return text
    pieces.append(text[cursor:])
    return "".join(pieces)


def _declare_camry_r7(text: str) -> str:
    if "camry_r7" not in text or "extern uint32_t camry_r7" in text:
        return text
    brace = text.find("{")
    if brace < 0:
        return text
    return text[:brace + 1] + "\n  extern uint32_t camry_r7;" + text[brace + 1:]


def _pass_rebuilt_indirect_r6(text: str) -> str:
    """Give a gap thunk the r6 the bytes computed before `jarl [reg]`."""
    if "camry_indirect" not in text:
        return text
    try:
        signature = _c_signature(text)
    except (AssertionError, ValueError):
        return text
    match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
    if match is None:
        return text
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening:
        return text
    params = [part.strip() for part in signature[opening + 1:closing].split(",") if part.strip()]
    if len(params) != 1 or "*" in params[0]:
        return text
    param = params[0].split()[-1].lstrip("*")
    empty: list[tuple[int, int]] = []
    start = 0
    while True:
        at = text.find("camry_indirect(", start)
        if at < 0:
            break
        try:
            close = c_text._match_delimiter(text, at + len("camry_indirect"))
        except ValueError:
            return text
        nxt = c_text._skip_space(text, close + 1)
        while nxt < len(text) and text[nxt] == ")":
            nxt = c_text._skip_space(text, nxt + 1)
        if nxt < len(text) and text[nxt] == "(":
            try:
                arg_close = c_text._match_delimiter(text, nxt)
            except ValueError:
                return text
            if text[nxt + 1:arg_close].strip() == "":
                empty.append((nxt, arg_close))
            start = arg_close + 1
        else:
            start = close + 1
    if len(empty) != 1:
        return text
    arguments = _rebuilt_indirect_r6(match.group(1), param)
    if arguments is None:
        return text
    call, end = empty[0]
    return text[:call] + "(" + arguments + text[end:]


def _tp_relative_copy_pointers(text: str) -> str:
    """The copy recovery bakes in the application tp.

    Boot scenarios set tp to 0x869c. An absolute source then sits above the
    camry_tp end, the pointer never meets it, and the loop walks off the image.
    The movea displacement is the same either way, so the source and the end
    both add that displacement to the scenario tp.
    """
    from tools.targets.camry.decomp.layout import _RUNTIME_TP
    from tools.targets.camry.decomp.syntax import _c_signature
    from tools.targets.camry.decomp.layout import _function_entries
    from tools.targets.camry.decomp.conversion.rewrite_memory import _tp_word_copy

    try:
        name = _c_signature(text).split("(", 1)[0].split()[-1].lstrip("*")
    except (AssertionError, ValueError, IndexError):
        return text
    entry = _function_entries().get(name)
    if entry is None:
        return text
    found = _tp_word_copy(entry)
    if found is None:
        return text
    start, length = found
    for addr in (start, (start + length) & 0xFFFFFFFF):
        disp = (addr - _RUNTIME_TP) & 0xFFFFFFFF
        text = text.replace(
            f"camry_host_ptr(0x{addr:x}u)",
            f"camry_host_ptr((uint32_t)(camry_tp + 0x{disp:x}u))",
        )
    return text


def _frame_pointer_disp(name: str) -> int | None:
    """Displacement where the bytes store sp and pass sp plus that displacement.

    The callee reads that word as the firmware address of the frame. The
    converted C passes the address of a host pointer instead, so the peripheral
    write keeps the low half of that pointer.
    """
    from tools.targets.camry.decomp.layout import _function_entries
    from tools.targets.camry.decomp.conversion.rewrite_memory import _symbols_by_addr
    from tools.targets.camry.decomp.lifting.graph import load_image, walk_symbol

    entry = _function_entries().get(name)
    row = _symbols_by_addr().get(entry) if entry is not None else None
    if row is None:
        return None
    fn = walk_symbol(load_image(), row)
    if fn is None:
        return None
    stored: set[int] = set()
    passed: set[int] = set()
    for inst in fn.insts:
        stmt = inst.stmt or ""
        stored_at = re.fullmatch(r"camry_st32\(3, 30, (-?\d+)\);", stmt)
        if stored_at is not None:
            stored.add(int(stored_at.group(1)))
        moved = re.fullmatch(r"camry_movea\([6-9], 3, (-?\d+)\);", stmt)
        if moved is not None:
            passed.add(int(moved.group(1)))
    both = stored & passed
    if len(both) != 1:
        return None
    return next(iter(both))


def _pass_frame_slot(text: str) -> str:
    """Pass the frame slot the bytes pass, holding the frame's firmware address."""
    if "stack_record_" not in text or "&puStack_" not in text:
        return text
    try:
        signature = _c_signature(text)
    except (AssertionError, ValueError):
        return text
    match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
    if match is None:
        return text
    disp = _frame_pointer_disp(match.group(1))
    if disp is None:
        return text
    assigns = dict(re.findall(
        r"\b(puStack_\w+) = \(\(uint8_t \*\)\((stack_record_\w+)\)\);",
        text,
    ))
    if not assigns:
        return text
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        rewritten = line
        store = None
        for local, record in assigns.items():
            needle = f"&{local}"
            if needle not in rewritten or f"camry_host_addr({needle})" in rewritten:
                continue
            indent = re.match(r"[ \t]*", rewritten).group(0)
            ending = "\n" if rewritten.endswith("\n") else ""
            store = (
                f"{indent}*(uint32_t *)({record} + {disp}) = "
                f"camry_host_addr((uint8_t *)({record}));{ending}"
            )
            rewritten = rewritten.replace(needle, f"(int *)({record} + {disp})")
        if store is not None:
            out.append(store)
        out.append(rewritten)
    return "".join(out)


_FIND_CONNECTION = re.compile(
    r"(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"cantp_find_(?:receive|transmit)_connection\s*\((.*)\)\s*;\s*",
    re.S,
)


def _null_connection_is_address_zero(text: str) -> str:
    """A missed CanTp row leaves r10 at 0, and the bytes still load disp[r10].

    The host pointer 0 faults. camry_host_ptr(0) is that same address, and
    camry_host_addr of it is still 0, so an address check keeps its branch.
    """
    if (
        "cantp_find_receive_connection" not in text
        and "cantp_find_transmit_connection" not in text
    ):
        return text
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    index = 0
    while index < len(lines):
        start = index
        if (
            "cantp_find_receive_connection" not in lines[index]
            and "cantp_find_transmit_connection" not in lines[index]
        ):
            out.append(lines[index])
            index += 1
            continue
        stmt = lines[index]
        while ";" not in stmt and index + 1 < len(lines):
            index += 1
            stmt += lines[index]
        out.extend(lines[start:index + 1])
        match = _FIND_CONNECTION.fullmatch(stmt)
        if match:
            indent, name = match.group(1), match.group(2)
            if f"if ({name} == 0)" not in text:
                out.append(
                    f"{indent}if ({name} == 0) {name} = (void *)camry_host_ptr(0);\n"
                )
        index += 1
    return "".join(out)


_IDENTITY_ASSIGN = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"\((uchar|undefined|byte) \*\)"
    r"((?:thunk_)?return_argument_word_7490e\s*\(\s*(?:\(int\))?\(?0xfebf6b80u?\)?\s*\))"
)


def _returned_address_is_host_pointer(text: str) -> str:
    """return_argument_word_7490e returns its argument, and the bytes load through that address.

    The cast keeps the firmware integer. camry_host_ptr is the host pointer of
    the same address. A caller that passes that pointer into the read already
    agrees, and camry_host_addr of the real pointer would take another path.
    """
    if "0xfebf6b80" not in text or "return_argument_word_7490e" not in text:
        return text

    def replacer(match: re.Match[str]) -> str:
        name, kind, call = match.group(1), match.group(2), match.group(3)
        if re.search(rf"nvm_read_map_blank_and_failure_status_776fa\s*\([^;]*\b{name}\b", text):
            return match.group(0)
        return f"{name} = ({kind} *)camry_host_ptr((uint32_t){call})"

    return _IDENTITY_ASSIGN.sub(replacer, text)


_FRESHNESS_SLOT = re.compile(
    r"\(uint \*\)([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]"
)


def _freshness_slot_is_host_pointer(text: str) -> str:
    """A freshness length word is the firmware address of the byte count.

    The bytes load through it. The integer in the slot is that address, and
    casting it uses the integer as a host pointer.
    """
    if (
        "freshness" not in text
        and "F33Freshness" not in text
        and "*(uint *)param_4[" not in text
    ):
        return text
    return _FRESHNESS_SLOT.sub(
        r"(uint *)camry_host_ptr((uint32_t)\1[\2])",
        text,
    )


_EXPLICIT_REG_WRITES: dict[int, set[int]] = {}


def _explicit_reg_writes(entry: int) -> set[int]:
    """Registers a callee writes with its own instructions.

    A nested call is not a write: the caller's later use of the register is
    what shows the callee handed the entry value back.
    """
    cached = _EXPLICIT_REG_WRITES.get(entry)
    if cached is not None:
        return cached
    from tools.targets.camry.decomp.conversion.rewrite_memory import _symbols_by_addr
    from tools.targets.camry.decomp.abi import _transfer
    from tools.targets.camry.decomp.lifting.graph import load_image, walk_symbol

    wrote: set[int] = set()
    row = _symbols_by_addr().get(entry)
    fn = walk_symbol(load_image(), row) if row is not None else None
    if fn is not None:
        for inst in fn.insts:
            if inst.kind in {"jarl", "jarl_ind", "dispose", "prepare", "callt"}:
                continue
            before = {number: {("id", number)} for number in range(1, 32)}
            after = _transfer(before, inst)
            wrote.update(
                reg for reg in range(1, 32) if after.get(reg) != before.get(reg)
            )
    _EXPLICIT_REG_WRITES[entry] = wrote
    return wrote


def _entry_extraout_is_incoming(text: str) -> str:
    """A pointer extraout still holding its entry value is that incoming register.

    A parameter is the pointer the bytes kept across the call. Any other
    register is the scenario sentinel. The uninitialized local traps under -O2.
    """
    if "extraout_r" not in text:
        return text
    from tools.targets.camry.decomp.abi import _call_facts, _transfer
    from tools.targets.camry.decomp.syntax import _c_signature, _opening_brace, _param_names, _signature_name, _signature_param_types
    from tools.targets.camry.decomp.conversion.rewrite_abi import _cast_extraout
    from tools.targets.camry.decomp.tree import load_symbols
    from tools.targets.camry.decomp.lifting.decode import decode_at
    from tools.targets.camry.decomp.lifting.graph import load_image

    try:
        signature = _c_signature(text)
        caller = _signature_name(signature)
        params = _param_names(signature)
        param_types = _signature_param_types(signature)
    except (AssertionError, ValueError):
        return text
    facts = _call_facts()
    state = facts["origins"].get(caller)
    grouped = facts["sites"].get(caller, {})
    if not state:
        return text
    brace = _opening_brace(text)
    if brace < 0:
        return text
    body = text[brace:]
    raw_calls = [
        (name, open_at, close)
        for name, open_at, close in c_text._direct_calls(body, syntax._SKIP_CALLS)
        if facts["entries"].get(name) is not None
    ]
    counts: dict[int, int] = {}
    for _name, _open_at, _close in raw_calls:
        entry = facts["entries"][_name]
        counts[entry] = counts.get(entry, 0) + 1
    usable = {
        entry for entry, count in counts.items() if count == len(grouped.get(entry, ()))
    }
    cursor_at = {entry: 0 for entry in usable}
    located: list[tuple[int, int, int, int]] = []
    for name, open_at, close in raw_calls:
        entry = facts["entries"][name]
        if entry not in usable:
            continue
        slot = cursor_at[entry]
        cursor_at[entry] = slot + 1
        located.append((open_at, close, grouped[entry][slot], entry))
    if not located:
        return text
    image = load_image()
    function_end = next(
        (int(row["addr"], 16) + int(row["size"]) for row in load_symbols() if row["name"] == caller),
        0,
    )
    replacements: list[tuple[int, int, str]] = []
    for match in re.finditer(r"\b(extraout_r(\d+)(?:_\d+)?)\b", body):
        after = c_text._skip_space(body, match.end())
        before = match.start() - 1
        while before >= 0 and body[before] in " \t\n":
            before -= 1
        if (
            after < len(body)
            and body[after] == "="
            and not body.startswith("==", after)
            and (before < 0 or body[before] not in "*)]")
        ):
            continue
        reg = int(match.group(2))
        prior = [item for item in located if item[1] <= match.start()]
        if not prior:
            continue
        _open_at, close, addr, entry = prior[-1]
        if close > match.start() or reg in _explicit_reg_writes(entry):
            continue
        origin = state.get(addr, {}).get(reg, set())
        if origin != {("entry", reg, "")}:
            continue
        following = [item[2] for item in located if item[0] > match.start()]
        end = following[0] if following else function_end
        call = decode_at(image, addr)
        if call is None or end <= addr:
            continue
        cursor = addr + call.size
        saw_read = False
        survived = False
        while cursor < end:
            inst = decode_at(image, cursor)
            if inst is None:
                break
            alive = {number: {("id", number)} for number in range(1, 32)}
            wrote = _transfer(alive, inst).get(reg) != alive.get(reg)
            if re.search(rf"\br{reg}\b", inst.text):
                saw_read = True
            if wrote:
                break
            cursor += inst.size
        else:
            survived = True
        if not survived and not saw_read:
            continue
        # A compare or an added displacement reads the integer. Only a
        # dereference, or a copy of a pointer extraout, is the incoming pointer.
        # An integer parameter is the firmware address, so the host load goes
        # through camry_host_ptr. A pointer parameter is already that pointer.
        dereferenced = (before >= 0 and body[before] == "*") or body.startswith("->", after)
        copied = after < len(body) and body[after] in ";,"
        index = reg - 6
        incoming = params[index] if 0 <= index < len(params) and params[index] else ""
        host_pointer = "*" in param_types[index] if incoming and index < len(param_types) else False
        if copied and not dereferenced and incoming and before >= 0 and body[before] == "=":
            name_at = before - 1
            while name_at >= 0 and body[name_at] in " \t\n":
                name_at -= 1
            name_end = name_at + 1
            while name_at >= 0 and (body[name_at].isalnum() or body[name_at] == "_"):
                name_at -= 1
            if body[name_at + 1:name_end] == incoming:
                continue
        if not dereferenced and not copied:
            continue
        if not dereferenced:
            declared = _cast_extraout(body, match.group(1), "0")
            if declared is None or "*" not in declared:
                continue
        if incoming and host_pointer:
            expr = incoming
        else:
            arg = f"camry_host_ptr({incoming})" if incoming else "camry_host_ptr(0x11111111u)"
            expr = _cast_extraout(body, match.group(1), arg)
            if expr is None:
                continue
        replacements.append((match.start(), match.end(), expr))
    if not replacements:
        return text
    pieces: list[str] = []
    cursor = 0
    for start, end, expr in replacements:
        pieces.append(body[cursor:start])
        pieces.append(expr)
        cursor = end
    pieces.append(body[cursor:])
    return text[:brace] + "".join(pieces)


_CODE_POINTER_LOAD = "*((code * *)camry_host_ptr("


def _code_pointer_word_is_firmware_address(text: str) -> str:
    """Load a code slot in the image as one firmware address word.

    code * is eight bytes on the host, so the load concatenates the next word
    into the high half and the indirect call leaves the image. camry_host_addr
    of that value misses every region and invents an alias. The word is the
    address.
    """
    if _CODE_POINTER_LOAD not in text:
        return text
    pieces: list[str] = []
    cursor = 0
    while True:
        at = text.find(_CODE_POINTER_LOAD, cursor)
        if at < 0:
            pieces.append(text[cursor:])
            break
        expr_at = at + len(_CODE_POINTER_LOAD)
        depth = 1
        index = expr_at
        while index < len(text) and depth:
            if text[index] == "(":
                depth += 1
            elif text[index] == ")":
                depth -= 1
            index += 1
        if depth or index >= len(text) or text[index] != ")":
            pieces.append(text[cursor:expr_at])
            cursor = expr_at
            continue
        end = index + 1
        expr = _code_pointer_word_is_firmware_address(text[expr_at:index - 1])
        load = f"(*((volatile uint32_t *)camry_host_ptr({expr})))"
        prefix = "camry_host_addr("
        if at >= len(prefix) and text[at - len(prefix):at] == prefix and end < len(text) and text[end] == ")":
            pieces.append(text[cursor:at - len(prefix)])
            pieces.append(load)
            cursor = end + 1
        else:
            pieces.append(text[cursor:at])
            pieces.append(load)
            cursor = end
    return "".join(pieces)


def _pointer_table_word_is_host_pointer(text: str) -> str:
    """Load a PTR_ word using its firmware-address representation.

    &PTR_DAT is the address of a uint32 in the image. The variable that holds
    it is typed as a pointer to a host pointer, so the load reads eight bytes
    and treats the next word as the high half.
    """
    if "&PTR_" not in text:
        return text
    names = [
        match.group(1)
        for match in re.finditer(
            r"(\b[A-Za-z_][A-Za-z0-9_]*)\s*=\s*&PTR_[A-Za-z0-9_]+",
            text,
        )
    ]
    if not names:
        return text
    for name in dict.fromkeys(names):
        text = re.sub(
            rf"(?<![\w*])\*{re.escape(name)}\b",
            f"((undefined *)camry_host_ptr(*(volatile uint32_t *){name}))",
            text,
        )
    return text


_LAZY_BYTE_BASE = re.compile(
    r"(\b[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"\(\((?:volatile\s+)?"
    r"(undefined1|undefined|uchar|byte|char|uint8_t|int8_t)\s*\*\)\s*"
    r"camry_host_ptr\((0x[0-9a-fA-F]+u)\)\)"
)


_LAZY_PAGE = 0x1000


def _index_leaves_lazy_page(expr: str) -> bool:
    """A constant this large cannot stay inside the 4K page of the base."""
    return any(
        int(match.group(1), 16) >= _LAZY_PAGE
        for match in re.finditer(r"0x([0-9a-fA-F]+)", expr)
    )


def _lazy_index_is_firmware_address(text: str) -> str:
    """An index off a host pointer is a firmware displacement.

    Each untouched page is its own mapping, with a guard after it. Adding the
    displacement to that host pointer walks into the guard. The bytes add it
    to the firmware address, and camry_host_ptr of the sum is that page.
    """
    from tools.targets.camry.decomp.syntax import _pointer_element_widths
    from tools.targets.camry.decomp.conversion.rewrite_types import _rewrite_host_pointer_adds

    widths = _pointer_element_widths(text)

    def pointer_add(match: re.Match[str]) -> str:
        target, source, index = match.group(2, 3, 4)
        if target not in widths or source not in widths:
            return match.group(0)
        return (
            f"{match.group(1)}{target} = (void *)camry_host_ptr((uint32_t)("
            f"camry_host_addr({source}) + (uint32_t)({index}) * {widths[source]}u));"
        )

    text = re.sub(
        r"^([ \t]*)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*\+\s*([^;\n]+);",
        pointer_add, text, flags=re.M,
    )
    pointer_types = {
        match.group(2): match.group(1)
        for match in re.finditer(
            r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)",
            text,
        )
        if match.group(2) in widths
    }
    comments = c_text._comment_spans(text)

    def inline_base(match: re.Match[str]) -> str:
        name = match.group(2)
        if name not in pointer_types or c_text._span_contains(comments, match.start()):
            return match.group(0)
        return (
            f"{match.group(1)}(({pointer_types[name]} *)"
            f"camry_host_ptr(camry_host_addr({name})))"
        )

    inlined = re.sub(
        r"(\(\s*)([A-Za-z_][A-Za-z0-9_]*)(?=\s*\+(?![+=]))",
        inline_base, text,
    )
    if inlined != text:
        text = _rewrite_host_pointer_adds(inlined)
    if "camry_host_ptr(0x" not in text:
        return text
    replacements: list[tuple[int, int, str]] = []
    for base in _LAZY_BYTE_BASE.finditer(text):
        name, ctype, imm = base.group(1), base.group(2), base.group(3)
        window_end = len(text)
        for later in re.finditer(rf"\b{re.escape(name)}\s*=", text[base.end():]):
            eq = base.end() + later.end() - 1
            if text.startswith("==", eq):
                continue
            window_end = base.end() + later.start()
            break
        window = text[base.end():window_end]
        folded = f"camry_host_ptr((uint32_t)({imm} + (uint32_t)({{0}})))"
        for match in re.finditer(rf"\b{re.escape(name)}\[", window):
            open_at = match.end() - 1
            close = c_text._match_delimiter(window, open_at, "[]", quoted=False, required=False)
            if close is None:
                continue
            expr = window[open_at + 1:close]
            if not _index_leaves_lazy_page(expr):
                continue
            start = base.end() + match.start()
            end = base.end() + close + 1
            replacements.append((
                start,
                end,
                f"*(({ctype} *){folded.format(expr)})",
            ))
        for match in re.finditer(rf"\({re.escape(name)} \+", window):
            open_at = match.start()
            depth = 0
            close = -1
            comma = False
            for index in range(open_at, len(window)):
                char = window[index]
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        close = index
                        break
                elif char == "," and depth == 1:
                    comma = True
                    break
            if close < 0 or comma:
                continue
            expr = window[match.end():close].strip()
            if not expr or not _index_leaves_lazy_page(expr):
                continue
            start = base.end() + open_at
            end = base.end() + close + 1
            replacements.append((start, end, folded.format(expr)))
    if not replacements:
        return text
    pieces: list[str] = []
    cursor = 0
    for start, end, expr in sorted(replacements):
        if start < cursor:
            continue
        pieces.append(text[cursor:start])
        pieces.append(expr)
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


def _gp_host_pointer_offsets(text: str) -> str:
    """Index camry_host_ptr(gp) using the integer firmware displacement.

    `puVar = camry_host_ptr(gp); puVar[-disp]` leaves the mapped window when
    the scenario image contains the field but not gp. The field is gp - disp.
    """
    integer_gp = set(re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\(camry_gp \+ 0x0u\)\s*;\s*$",
        text,
        re.M,
    ))
    direct = "((undefined *)camry_host_ptr((camry_gp + 0x0u)))"
    via = re.compile(
        r"\(\(undefined \*\)camry_host_ptr\(\(uint32_t\)\(([A-Za-z_][A-Za-z0-9_]*)\)\)\)"
    )
    assigns: dict[str, list[str]] = {}
    for match in re.finditer(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+);\s*$",
        text,
        re.M,
    ):
        assigns.setdefault(match.group(1), []).append(match.group(2).strip())
    parent: dict[str, str] = {}

    def find(name: str) -> str:
        parent.setdefault(name, name)
        if parent[name] != name:
            parent[name] = find(parent[name])
        return parent[name]

    def union(left: str, right: str) -> None:
        parent[find(left)] = find(right)

    anchored: set[str] = set()
    blocked: set[str] = set()
    ident = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    for name, exprs in assigns.items():
        if name in integer_gp:
            continue
        for expr in exprs:
            if expr == direct:
                anchored.add(name)
                continue
            found = via.fullmatch(expr)
            if found and found.group(1) in integer_gp:
                anchored.add(name)
                continue
            if ident.fullmatch(expr):
                union(name, expr)
                continue
            blocked.add(name)
    qualified = {
        name for name in assigns
        if name not in integer_gp
        and name not in blocked
        and find(name) not in {find(item) for item in blocked}
        and any(find(name) == find(item) for item in anchored)
    }
    for name in sorted(qualified, key=len, reverse=True):
        text = re.sub(
            rf"\b{re.escape(name)}\[([^\]\n]*\+ -0x[0-9a-fA-F]+)\]",
            lambda match: (
                "(*camry_host_ptr((uint32_t)(camry_gp + (uint32_t)("
                + match.group(1)
                + "))))"
            ),
            text,
        )
        text = re.sub(
            rf"\b{re.escape(name)}\[-0x([0-9a-fA-F]+)\]",
            lambda match: (
                "(*camry_host_ptr((uint32_t)(camry_gp + -0x" + match.group(1) + ")))"
            ),
            text,
        )
        text = re.sub(
            rf"\({re.escape(name)} \+ -0x([0-9a-fA-F]+)\)",
            lambda match: (
                "(camry_host_ptr((uint32_t)(camry_gp + -0x" + match.group(1) + ")))"
            ),
            text,
        )
    return text


_ENTRY_STOP = {
    "b", "br", "jarl", "jarl_ind", "jr", "jmp", "jmpdisp", "loop", "switch",
    "dispose", "callt", "abort", "eiret",
}


# These name a source register in the first argument. They do not replace it.
_ENTRY_NO_WRITE = {
    "cmp", "cmpi", "st8", "st16", "st32", "tst1", "set1", "clr1", "not1", "prepare",
}


_ZXB_ARGS: dict[int, frozenset[int]] = {}


_ZXB_ROWS: dict[int, dict] | None = None


_ZXB_IMAGE: bytes | None = None


_U8_NAMES: set[str] | None = None


_S16_NAMES: set[str] | None = None


_U16_NAMES: set[str] | None = None


def _straight_line_zxb(fn) -> frozenset[int]:
    """Argument registers zero-extended before the prologue branches or overwrites them."""
    by_addr = {inst.addr: inst for inst in fn.insts}
    pc = fn.entry
    seen: set[int] = set()
    clobber: set[int] = set()
    found: set[int] = set()
    while pc in by_addr and pc not in seen:
        seen.add(pc)
        inst = by_addr[pc]
        parsed = _stmt_parts(inst.stmt) if inst.stmt else None
        if parsed is not None:
            name, args = parsed
            reg = args[0] if args and isinstance(args[0], int) else None
            if name == "zxb" and isinstance(reg, int) and reg not in clobber and 6 <= reg <= 9:
                found.add(reg)
            if isinstance(reg, int) and 6 <= reg <= 9 and (name == "zxb" or name not in _ENTRY_NO_WRITE):
                clobber.add(reg)
        if inst.kind in _ENTRY_STOP:
            break
        pc = inst.addr + inst.size
    return frozenset(found)


def _entry_zero_extended_args(addr: int) -> frozenset[int]:
    global _ZXB_ROWS, _ZXB_IMAGE
    cached = _ZXB_ARGS.get(addr)
    if cached is not None:
        return cached
    if _ZXB_ROWS is None:
        _ZXB_IMAGE = load_image()
        _ZXB_ROWS = {int(row["addr"], 16): row for row in load_symbols()}
    row = _ZXB_ROWS.get(addr)
    found: frozenset[int] = frozenset()
    if row is not None and _ZXB_IMAGE is not None:
        fn = walk_symbol(_ZXB_IMAGE, row)
        if fn is not None:
            found = _straight_line_zxb(fn)
    _ZXB_ARGS[addr] = found
    return found


def _uint8_names() -> set[str]:
    global _U8_NAMES
    if _U8_NAMES is None:
        header = (COMMON_HEADER).read_text(encoding="utf-8", errors="replace")
        _U8_NAMES = set(re.findall(
            r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\b[^\n]*\buint8_t\b",
            header,
            re.M,
        ))
    return _U8_NAMES


_U8_EXPR = re.compile(
    r"^(?:"
    r"\(\*\(\((?:volatile )?uint8_t \*\)"
    r"|\(\((?:volatile )?uint8_t \*\)"
    r"|\((?:uchar|byte|uint8_t|undefined1|unsigned char)\)"
    r")"
)


_U8_DEREF = r"(?:\(\*\(\((?:volatile )?uint8_t \*\)|\(\((?:volatile )?uint8_t \*\))"


def _uint8_expr(expr: str, names: set[str]) -> bool:
    expr = expr.strip()
    if _U8_EXPR.match(expr):
        return True
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", expr) and expr in names)


def _unsigned_loaded_char_compares(text: str) -> str:
    """A `char` copied from an unsigned byte still compares as a signed char.

    `c = *(uint8_t *)p; if (c != *(uint8_t *)q)` is -91 != 165 when both bytes
    are 0xa5, so the host takes the mismatch path. The load was unsigned.
    Compares with a negative constant stay on the signed local.
    """
    if not re.search(r"^\s*char\s+[A-Za-z_]", text, re.M):
        return text
    if "==" not in text and "!=" not in text:
        return text
    names = _uint8_names() | set(re.findall(
        r"^\s*(?:uchar|byte|uint8_t|undefined1|unsigned char)\s+([A-Za-z_][A-Za-z0-9_]*)\b",
        text,
        re.M,
    ))
    chosen: list[str] = []
    for name in re.findall(r"^\s*char\s+([A-Za-z_][A-Za-z0-9_]*)\s*;", text, re.M):
        assigned = re.findall(rf"^\s*{re.escape(name)}\s*=\s*(.+);\s*$", text, re.M)
        if assigned and all(_uint8_expr(expr, names) for expr in assigned):
            chosen.append(name)
    for name in chosen:
        text = re.sub(
            rf"(?<!\(unsigned char\))(\b{re.escape(name)}\b)(\s*(?:==|!=)\s*)({_U8_DEREF})",
            rf"(unsigned char)\1\2\3",
            text,
        )

        def repl_left(match: re.Match[str], name: str = name) -> str:
            if match.group(3) not in names:
                return match.group(0)
            return f"(unsigned char){match.group(1)} {match.group(2)} {match.group(3)}"

        def repl_right(match: re.Match[str], name: str = name) -> str:
            if match.group(1) not in names:
                return match.group(0)
            return f"{match.group(1)} {match.group(2)} (unsigned char){match.group(3)}"

        text = re.sub(
            rf"(?<!\(unsigned char\))(\b{re.escape(name)}\b)\s*(==|!=)\s*([A-Za-z_][A-Za-z0-9_]*)",
            repl_left,
            text,
        )
        text = re.sub(
            rf"\b([A-Za-z_][A-Za-z0-9_]*)\s*(==|!=)\s*(?<!\(unsigned char\))(\b{re.escape(name)}\b)",
            repl_right,
            text,
        )
    return text


def _unsigned_zero_extended_params(text: str, addresses: dict[str, int]) -> str:
    """Compare a `zxb`'d `char` argument with an unsigned byte as a byte.

    Darwin `char` is signed, so `0xa5 == DAT_u8` is -91 == 165 and the host
    takes the other branch. A compare with -1 stays on the signed parameter:
    the scenario arguments are 0..4, and an unsigned parameter makes that
    compare a tautology the host compiler rejects.
    """
    text = _unsigned_loaded_char_compares(text)
    if "char " not in text and "\tchar " not in text:
        return text
    if "==" not in text and "!=" not in text:
        return text
    try:
        signature = _c_signature(text)
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
        if match is None:
            return text
        name = match.group(1)
        _return_type, params = parse_signature(signature, name)
    except (AssertionError, ValueError):
        return text
    addr = addresses.get(name)
    if addr is None:
        return text
    regs = _entry_zero_extended_args(addr)
    if not regs:
        return text
    chosen: list[str] = []
    for index, param in enumerate(params):
        if index >= 4 or "*" in param or "[" in param:
            continue
        if (6 + index) not in regs:
            continue
        found = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", param)
        if found is None:
            continue
        typed = param[:found.start()].strip()
        if typed != "char":
            continue
        chosen.append(found.group(1))
    if not chosen:
        return text
    targets = _uint8_names() | set(re.findall(
        r"^\s*(?:uchar|byte|uint8_t|undefined1|unsigned char)\s+([A-Za-z_][A-Za-z0-9_]*)\b",
        text,
        re.M,
    ))
    for pname in chosen:
        def repl_left(match: re.Match[str], pname: str = pname) -> str:
            if match.group(3) not in targets:
                return match.group(0)
            return f"(unsigned char){match.group(1)} {match.group(2)} {match.group(3)}"

        def repl_right(match: re.Match[str], pname: str = pname) -> str:
            if match.group(1) not in targets:
                return match.group(0)
            return f"{match.group(1)} {match.group(2)} (unsigned char){match.group(3)}"

        text = re.sub(
            rf"(?<!\(unsigned char\))(\b{re.escape(pname)}\b)\s*(==|!=)\s*([A-Za-z_][A-Za-z0-9_]*)",
            repl_left,
            text,
        )
        text = re.sub(
            rf"\b([A-Za-z_][A-Za-z0-9_]*)\s*(==|!=)\s*(?<!\(unsigned char\))(\b{re.escape(pname)}\b)",
            repl_right,
            text,
        )
    return text


def _halfword_names() -> tuple[set[str], set[str]]:
    global _S16_NAMES, _U16_NAMES
    if _S16_NAMES is None or _U16_NAMES is None:
        header = (COMMON_HEADER).read_text(encoding="utf-8", errors="replace")
        _S16_NAMES = set(re.findall(
            r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\b[^\n]*\bint16_t\b",
            header,
            re.M,
        ))
        _U16_NAMES = set(re.findall(
            r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\b[^\n]*\buint16_t\b",
            header,
            re.M,
        ))
    return _S16_NAMES, _U16_NAMES


def _signed_halfword_reloads(text: str) -> str:
    """A uint16 copied from an int16 still has the sign the sld.h left in the register.

    `(int)DAT_u16` zero-extends 0xf380 to 62336, so the following shift saturates.
    The bytes shifted the signed halfword, -3200. A value below 0x8000 is unchanged.
    """
    if "(int)" not in text:
        return text
    signed, unsigned = _halfword_names()
    for name in set(re.findall(r"\(int\)([A-Za-z_][A-Za-z0-9_]*)\b", text)):
        if name not in unsigned:
            continue
        assigned = re.findall(
            rf"^\s*{re.escape(name)}\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*;",
            text,
            re.M,
        )
        if not assigned or any(expr not in signed for expr in assigned):
            continue
        first_assign = re.search(rf"^\s*{re.escape(name)}\s*=", text, re.M)
        first_use = re.search(rf"\(int\){re.escape(name)}\b", text)
        if first_assign is None or first_use is None or first_use.start() < first_assign.start():
            continue
        text = re.sub(rf"\(int\){re.escape(name)}\b", f"(int)(int16_t){name}", text)
    return text


def _halt_nonvoid(text: str) -> str:
    """Stop a non-void caller when a callee halts.

    Applied after the bounded-name snapshot. The inserted return is not a
    loop rewrite, so it must not make the byte machine stop at a back-edge.
    """
    try:
        signature = _c_signature(text)
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
        if match is None:
            return text
        return_type, _params = parse_signature(signature, match.group(1))
    except (AssertionError, ValueError):
        return text
    if return_type == "void":
        return text
    return _return_when_halted(text, "0")


_NATIVE_STOP_SITES: dict[int, tuple[str, int, str, bool] | None] = {}


_NATIVE_WORKFLOW_REQUESTS: set[int] = set()


_NATIVE_STOP_REJECTIONS: dict[int, str] = {}


_NATIVE_RETAINED_STOPS_LOADED = False


# These producer-owned chains execute their actual PREPARE/JARL/DISPOSE in C.
_NATIVE_LIVE_FRAME_STOPS = {
    0x1404: {0x10c4},
    0x65fae: {0x61940, 0x66786},
    0x687de: {0x6879c},
    0x6889a: {0x6879c},
    0x74164: {0x726c4, 0x7990e},
    0x7f4dc: {0x837d6},
    0x8cb1a: {0x95644, 0x95626},
    0x8ca8a: {0x95644, 0x95626},
    0x8c960: {0x95644, 0x95626},
    0x8cb7a: {0x95644},
    0x8e434: {0x8e6ba, 0x8e6d2},
    0x8e3a2: {0x8e6ba, 0x8e6d2},
    0x8e4aa: {0x8e6ba, 0x8e6d2},
    0x98946: {0x95644, 0x8e6ba, 0x8e6d2},
    0x5516: {0x674a},
    0x5222: {0x674a},
    0x2b8a: {0x64b8},
    0x20880: {0x637f6},
}


def _native_final_return(text: str) -> tuple[int, int] | None:
    masked = re.sub(
        r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
        lambda match: re.sub(r"\S", " ", match.group()), text, flags=re.S,
    )
    for match in re.finditer(r"\breturn\b[^;{}]*;", masked):
        before = masked[:match.start()]
        if (before.count("{") - before.count("}") == 1
                and masked[match.end():].strip() == "}"):
            return match.span()
    return None


def _native_stop_sites(addresses: set[int]) -> None:
    missing = addresses - _NATIVE_STOP_SITES.keys()
    if not missing:
        return
    from tools.targets.camry.decomp.layout import _corpus_functions
    from tools.targets.camry.decomp.syntax import _signature_name

    functions = _corpus_functions()
    renames = {_signature_name(_c_signature(row["decompiled_c"])): row["name"]
               for row in functions}
    tokens = re.compile(r"\b(?:" + "|".join(map(re.escape, renames)) + r")\b")
    sites: dict[int, dict[tuple[str, int, int, int], str]] = defaultdict(dict)
    entries: dict[int, list[dict]] = defaultdict(list)
    for row in functions:
        entry = int(row["entry_addr"], 16)
        if entry in missing:
            entries[entry].append(row)
        for location in row.get("c_locations", []):
            if location.get("kind") != "statement":
                continue
            pc = int(location["pc"], 16)
            if pc in missing:
                key = (row["name"], int(row["entry_addr"], 16),
                       location["start"], location["end"])
                sites[pc][key] = row["decompiled_c"]
    for pc in missing:
        candidates = sites[pc]
        _NATIVE_STOP_SITES[pc] = None
        if pc == 0x59cc:
            # BR 5A00 follows 59C4's state store and 59C8's cleanup JARL.
            # It has no corpus statement; the producer retains its real edge.
            image = load_image()
            if image[0x59c4:0x59ce] == bytes.fromhex("440f699380ff3c15a51d"):
                _NATIVE_STOP_SITES[pc] = (
                    "boot_advance_crc_authentication_routine_5936", 0x5936, "goto LAB_00005a00", False,
                )
            continue
        if pc == 0x3438c:
            # The corpus represents this MOVEA only as an argument token.
            # The producer spells the actual instruction before its stack stores.
            image = load_image()
            if (image[0x3438c:0x34390] == bytes.fromhex("230e1200")
                    and image[0x343ae:0x343b2] == bytes.fromhex("bfff28fc")):
                _NATIVE_STOP_SITES[pc] = (
                    "step_mode600_stimulus_fit", 0x34028,
                    "camry_gpr[1] = camry_sp + 0x12u", False,
                )
            continue
        if pc in entries:
            if len(entries[pc]) != 1:
                continue
            row = entries[pc][0]
            _NATIVE_STOP_SITES[pc] = (row["name"], pc, "", False)
            continue
        if len(candidates) > 1:
            _NATIVE_STOP_REJECTIONS[pc] = "ambiguous statement boundaries"
            continue
        if not candidates:
            continue
        (name, entry, start, end), source = next(iter(candidates.items()))
        statement = source[start:end].strip()
        statement = tokens.sub(lambda match: renames[match.group()], statement)
        if not statement or not source[end:].lstrip().startswith(";"):
            continue
        terminal = _native_final_return(source)
        is_return = re.match(r"return\b", statement) is not None
        if is_return:
            if terminal is None or terminal[0] != start:
                continue
        elif (re.match(r"(?:if|else|for|while|do|switch|case|default|break|continue|goto)\b", statement)
              or any(char in statement for char in ";{}")):
            continue
        before = c_text._skip_space(_mask_comments(source), start - 1, -1, chars=None)
        if before < 0 or source[before] not in "{};:":
            continue
        _NATIVE_STOP_SITES[pc] = (name, entry, statement, is_return)


def _native_entry_frame(entry: int, target: int) -> tuple[int, int] | None:
    row = next((row for row in load_symbols() if int(row["addr"], 16) == entry), None)
    if row is None:
        return None
    code = load_image()
    fn = walk_symbol(code, row)
    if fn is None or len(fn.insts) < 3 or code[entry:entry + 4] != b"\x80\x07\x21\x00":
        return None
    call, dispose = fn.insts[-2:]
    if (call.kind != "jarl" or call.link != 31 or call.target != target
            or dispose.kind != "dispose" or dispose.slots != 0
            or dispose.mask != 1 << 31 or dispose.ret != 31
            or any(re.search(r"\br3\b|camry_prepare\(", inst.stmt) for inst in fn.insts[1:-2])):
        return None
    return 4, call.addr + call.size


def _native_ram_continuation(scenario: dict) -> list[tuple[int, bytes]]:
    """Only literal RAM input containing the incoming LP is executable glue.

    In particular, RAM populated by a firmware copy is not a script region.
    Those bytes must dispatch through a separately supported native C entry.
    """
    registers = scenario.get("registers", {})
    raw_lp = registers.get("lp", registers.get("r31", STOP))
    lp = int(raw_lp, 0) if isinstance(raw_lp, str) else int(raw_lp)
    regions = scenario.get("memory") or []
    for index, region in enumerate(regions):
        if "hex" not in region:
            continue
        base = int(region["address"], 0)
        blob = bytes.fromhex(region["hex"])
        end = base + len(blob)
        if not (base <= lp < end) or _space(base, len(blob)) not in {"local", "global", "alias"}:
            continue
        # Do not execute a stale literal when a later input overwrites it.
        for later in regions[index + 1:]:
            address = int(later["address"], 0)
            size = len(bytes.fromhex(later["hex"])) if "hex" in later else int(later["size"])
            if address < end and base < address + size:
                return []
        return [(base, blob)]
    return []


def native_workflow_stops(scenario: dict) -> dict[int, tuple[str, int]]:
    """Precise native stops for a multi-call scenario, using only its inputs."""
    requested = {int(value, 0) if isinstance(value, str) else int(value)
                 for value in scenario.get("stop_addresses", [])}
    registers = scenario.get("registers", {})
    raw_lp = registers.get("lp", registers.get("r31", STOP))
    lp = int(raw_lp, 0) if isinstance(raw_lp, str) else int(raw_lp)
    requested.discard(lp)  # Returning to the incoming LP needs no C probe.
    if not requested:
        return {}
    scripts = _native_ram_continuation(scenario)
    ram = {pc for pc in requested
           if any(base <= pc <= base + len(blob) for base, blob in scripts)}
    firmware = requested - ram
    _native_stop_sites(firmware)
    if any(_NATIVE_STOP_SITES[pc] is None for pc in firmware):
        return {}
    entry = int(scenario["entry"]["address"], 16)
    boot_dispatch = entry in {0x8370, 0xFEBF1000} or (entry == 0x35E4 and lp == 0xFEBF1000)
    for pc in firmware:
        owner_entry = _NATIVE_STOP_SITES[pc][1]
        if pc == owner_entry and owner_entry != entry:
            if (not boot_dispatch and pc not in _NATIVE_LIVE_FRAME_STOPS.get(entry, ())
                    and (len(requested) != 1 or _native_entry_frame(entry, owner_entry) is None)):
                return {}
    _NATIVE_WORKFLOW_REQUESTS.update(firmware)
    return {**{pc: ("", pc) for pc in ram},
            **{pc: (_NATIVE_STOP_SITES[pc][0], _NATIVE_STOP_SITES[pc][1])
               for pc in firmware}}


def _native_retained_stops() -> None:
    """Resolve retained checkpoints before computing the caller halt closure."""
    global _NATIVE_RETAINED_STOPS_LOADED
    if not _NATIVE_RETAINED_STOPS_LOADED:
        from tools.targets.camry.decomp.tree import load_oracles

        scenarios = list(load_oracles())
        _native_stop_sites({
            int(pc, 0) for scenario in scenarios
            for pc in scenario.get("stop_addresses", [])
        })
        for scenario in scenarios:
            native_workflow_stops(scenario)
        _NATIVE_RETAINED_STOPS_LOADED = True


def _native_stop_probes(text: str, addresses: dict[str, int]) -> str:
    """Arm-gated probes at requested, source-proven statement boundaries."""
    _native_retained_stops()
    if not _NATIVE_WORKFLOW_REQUESTS:
        return text
    signature = _c_signature(text)
    name_match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
    if name_match is None:
        return text
    name = name_match.group(1)
    return_type, _params = parse_signature(signature, name)
    if name in {"boot_ram_dispatch", "boot_relocated_8370"}:
        # Stop at the actual callback transfer, after the native body has
        # executed PREPARE, table lookup and JARL's register updates.
        callback_entries = [
            pc for pc in sorted(_NATIVE_WORKFLOW_REQUESTS)
            if _NATIVE_STOP_SITES[pc][1] == pc
        ]
        marker = "  camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))"
        if callback_entries and text.count(marker) == 1:
            targets = " || ".join(f"camry_gpr[29] == 0x{pc:x}u" for pc in callback_entries)
            text = text.replace(marker, (
                "  if ((camry_stop_arm == camry_gpr[29] || camry_stop_arm == 0xffffffffu)\n"
                f"      && ({targets})) {{\n"
                "    camry_stop_pc = camry_gpr[29]; camry_halted = 1; return;\n"
                "  }\n" + marker
            ), 1)
    replacements: list[tuple[int, int, str]] = []
    for pc in sorted(_NATIVE_WORKFLOW_REQUESTS):
        owner, entry, statement, is_return = _NATIVE_STOP_SITES[pc]
        if owner != name or addresses.get(name) != entry:
            continue
        if f"camry_stop_pc = 0x{pc:x}u;" in text:
            continue
        if not statement:
            brace = text.find("{")
            matches = [] if brace < 0 else [(brace + 1, brace + 1)]
        elif is_return:
            boundary = _native_final_return(text)
            matches = [] if boundary is None else [boundary]
        else:
            masked = _mask_comments(text)
            matches = []
            for match in re.finditer(re.escape(statement) + r"\s*;", masked):
                before = c_text._skip_space(masked, match.start() - 1, -1, chars=None)
                if before >= 0 and masked[before] in "{};:":
                    matches.append(match.span())
        if len(matches) != 1:
            _NATIVE_STOP_REJECTIONS[pc] = f"{name}: ambiguous rewritten stop boundary"
            _NATIVE_STOP_SITES[pc] = None
            _NATIVE_WORKFLOW_REQUESTS.discard(pc)
            continue
        start, end = matches[0]
        leave = "return;" if return_type == "void" else "return 0;"
        probe = (f"{{ if (camry_stop_arm == 0x{pc:x}u || camry_stop_arm == 0xffffffffu) {{ "
                 f"camry_stop_pc = 0x{pc:x}u; camry_halted = 1; {leave} }} "
                 + text[start:end] + " }")
        replacements.append((start, end, probe))
    for start, end, probe in sorted(replacements, reverse=True):
        text = text[:start] + probe + text[end:]
    return text


def rewrite_host_body(
    text: str, addresses: dict[str, int], *, zero_extend: bool = True, halt_return: bool = True,
    bounded: set[str] | None = None,
) -> str:
    """Run one iteration of a non-returning loop, then return.

    The stored C keeps the infinite loop. Only the host check uses this copy,
    so stores, peripheral writes, and the call sequence can be compared
    without the function returning in the firmware image.
    Only a rewritten infinite loop marks its function as bounded.
    """
    if "stack_record_" in text:
        from tools.targets.camry.decomp.conversion.rewrite_types import _rewrite_packed_stack
        text = _rewrite_packed_stack(text)
    # Fill 0xa5 leaves bit 4 of 0xffffb111 clear, and a word flip would
    # clear a nonzero byte. The 4096th byte read is all-ones.
    text = text.replace(
        "bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xffffb111u)));\n"
        "    } while ((bVar1 & 0x10) == 0);",
        "bVar1 = (byte)camry_read8(0xffffb111u);\n"
        "    } while ((bVar1 & 0x10) == 0);",
    )
    if "camry_r10_result" in text:
        from tools.targets.camry.decomp.conversion.rewrite_types import _rewrite_merged_call_results
        text = _rewrite_merged_call_results(text)
    if "(uintptr_t)" in text:
        from tools.targets.camry.decomp.syntax import _pointer_names
        from tools.targets.camry.decomp.conversion.rewrite_pointer import _rewrite_pointer_compares
        text = _rewrite_pointer_compares(text, _pointer_names(_c_signature(text), text))
    if zero_extend:
        text = _unsigned_zero_extended_params(text, addresses)
    text = _gp_host_pointer_offsets(text)
    # Ghidra prints the source of a tp-relative copy as "". The compare then
    # walks that host literal until it faults. The firmware address comes from
    # the same movea/addi the corpus rewrite already recovers.
    if '= ""' in text or '(uintptr_t)("' in text:
        from tools.targets.camry.decomp.conversion.rewrite_memory import _rewrite_string_word_copies
        text = _tp_relative_copy_pointers(_rewrite_string_word_copies(text))
    if "camry_indirect" in text:
        from tools.targets.camry.decomp.conversion.rewrite_memory import _rewrite_firmware_call_wrap
        text = _rewrite_firmware_call_wrap(text)
        text = _pass_rebuilt_indirect_r6(text)
    text = _assign_incoming_r7(text)
    text = _declare_camry_r7(text)
    if "&puStack_" in text:
        text = _pass_frame_slot(text)
    # movea 0x904, tp is four bytes past entry 0x120 of the 8-byte table.
    # The struct index lands on the previous word, and that word is not an address.
    if "pFVar7 + 0x120" in text:
        text = text.replace(
            "pFVar7 + 0x120",
            "(F33BootInterruptEntry *)((uchar *)(pFVar7 + 0x120) + 4)",
        )
        text = text.replace(
            "pFVar7 + 0x122",
            "(F33BootInterruptEntry *)((uchar *)(pFVar7 + 0x122) + 4)",
        )
    # The bytes add 4 to the source until 0x17df0. The printed increment
    # reloads 0x10001, so the destination walks off the mapped page.
    text = text.replace(
        "puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0x10000u + (uint32_t)(1) * 1u)))",
        "puVar1 = (undefined4 *)((uint8_t *)puVar1 + 4)",
    )
    # cmp r1, r0 / b7 (signed <=) and bf (signed >). The object is uint32_t,
    # so a fill with the high bit set stays positive and the body returns early.
    text = text.replace("0 < DAT_febf6c20", "0 < (int32_t)DAT_febf6c20")
    text = _signed_halfword_reloads(text)
    text = _pointer_table_word_is_host_pointer(text)
    text = _code_pointer_word_is_firmware_address(text)
    text = _lazy_index_is_firmware_address(text)
    text = _null_connection_is_address_zero(text)
    text = _returned_address_is_host_pointer(text)
    text = _freshness_slot_is_host_pointer(text)
    # &LABEL is the host pointer of a camry_host_ptr() macro. Casting that to
    # uint32_t keeps the low half of the host pointer. camry_host_addr turns
    # the same pointer, after C pointer arithmetic, back into a firmware address.
    if "camry_host_ptr((uint32_t)(&" in text:
        text = text.replace(
            "camry_host_ptr((uint32_t)(&",
            "camry_host_ptr(camry_host_addr(&",
        )
    if "extraout_" in text:
        from tools.targets.camry.decomp.conversion.rewrite_abi import _rewrite_surviving_extraouts
        text = _rewrite_surviving_extraouts(text, traps_only=True)
        text = _entry_extraout_is_incoming(text)
    try:
        signature = _c_signature(text)
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
        if match is None:
            return text
        return_type, _params = parse_signature(signature, match.group(1))
    except (AssertionError, ValueError):
        return text
    name = match.group(1)
    halts = bool(_TRUE_LOOP.search(_mask_comments(text)) and _function_self_halts(name))
    value = None if return_type == "void" else (
        "camry_r10_result" if re.search(r"\buint32_t\s+camry_r10_result\s*;", text) else "0"
    )
    rewritten = False
    while (found := _first_infinite_loop(text, halt=halts, value=value)) is not None:
        start, end, replacement = found
        text = text[:start] + replacement + text[end:]
        rewritten = True
    if rewritten:
        brace = text.find("{")
        if brace < 0:
            return text
        if bounded is not None:
            bounded.add(name)
        addr = addresses.get(name)
        note = f"\n  camry_note_call(0x{addr:x}u, 0x{addr:x}u);" if addr is not None else ""
        text = text[:brace + 1] + note + text[brace + 1:]
    if return_type == "void" or halt_return:
        text = _return_when_halted(text, value)
    text = _native_stop_probes(text, addresses)
    if rewritten or name in _reaches_halt():
        text = _note_root_calls(text, addresses)
    return text


def rewrite_host_translation_unit(text: str, addresses: dict[str, int]) -> str:
    """Rewrite each function of a translation unit. Unchanged text is returned as-is."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    index = 0
    changed = False
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if (
            not stripped
            or line.startswith("#")
            or line.startswith(" ")
            or line.startswith("\t")
            or line.startswith("/*")
            or line.startswith("//")
        ):
            out.append(line)
            index += 1
            continue
        start = index
        while index < len(lines) and "{" not in lines[index]:
            if ";" in lines[index]:
                out.extend(lines[start:index + 1])
                start = index + 1
            index += 1
        if index >= len(lines):
            out.extend(lines[start:])
            break
        depth = 0
        while index < len(lines):
            depth += lines[index].count("{") - lines[index].count("}")
            index += 1
            if depth <= 0:
                break
        chunk = "".join(lines[start:index])
        rewritten = _halt_nonvoid(_fill_local_arrays(_seed_incoming_locals(
            rewrite_host_body(chunk, addresses),
        )))
        if rewritten != chunk:
            changed = True
            if not rewritten.endswith("\n"):
                rewritten += "\n"
            out.append(rewritten)
        else:
            out.append(chunk)
    if not changed:
        return text
    decl = "int camry_note_call(uint32_t caller, uint32_t address);\n"
    joined = "".join(out)
    if decl in joined:
        return joined
    include = joined.rfind("#include")
    if include < 0:
        return decl + joined
    line_end = joined.find("\n", include)
    if line_end < 0:
        return joined + "\n" + decl
    return joined[:line_end + 1] + decl + joined[line_end + 1:]

