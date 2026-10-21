"""Host-C firmware memory and pointer-word rewrite passes."""
from __future__ import annotations

import re

from tools.targets.camry.decomp import c_text, layout, syntax, tree
from tools.targets.camry.decomp.conversion import expressions



_INDIRECT_CALL = "(*(int (*)())camry_host_ptr("


def _rewrite_indirect_dispatch(code: str) -> str:
    """Call a firmware address through the host dispatch table.

    `camry_host_ptr` returns bytes. The call wants the compiled function at
    that address.
    """
    pieces: list[str] = []
    index = 0
    while True:
        found = code.find(_INDIRECT_CALL, index)
        if found < 0:
            pieces.append(code[index:])
            break
        opening = found + len(_INDIRECT_CALL) - 1
        try:
            closing = c_text._match_delimiter(code, opening)
        except ValueError:
            pieces.append(code[index:found + len(_INDIRECT_CALL)])
            index = found + len(_INDIRECT_CALL)
            continue
        expr = code[opening + 1:closing]
        pieces.append(code[index:found])
        pieces.append(f"(*(int (*)())camry_indirect({expr})")
        index = closing + 1
    return "".join(pieces)


def _rewrite_indirect_arguments(code: str) -> str:
    """Pass host pointer arguments to indirect bindings as firmware words."""
    if "camry_indirect" not in code:
        return code
    # Keep offsets and literal contents while hiding comment punctuation from
    # the existing balanced-parenthesis and argument parsers.
    masked = list(code)
    literals: list[tuple[int, int]] = []
    for token in re.finditer(
        r"""'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|/\*.*?\*/|//[^\n]*""",
        code, re.S,
    ):
        if token.group(0).startswith(("/*", "//")):
            masked[token.start():token.end()] = " " * (token.end() - token.start())
        else:
            literals.append(token.span())
    text = "".join(masked)
    kind = expressions._kind_context(syntax._c_signature(code), code)
    pattern = re.compile(
        r"(?P<cast>\(\s*\*\s*\(\s*int\s*\(\s*\*\s*\)\s*\(\s*\)\s*\)\s*)?"
        r"\bcamry_indirect\s*\("
    )
    insertions: list[tuple[int, int, str]] = []
    for match in pattern.finditer(text):
        if c_text._span_contains(literals, match.start()):
            continue
        target_end = c_text._match_delimiter(text, match.end() - 1)
        opening = c_text._skip_space(text, target_end + 1)
        if match.group("cast") is not None:
            if opening >= len(text) or text[opening] != ")":
                continue
            opening = c_text._skip_space(text, opening + 1)
        if opening >= len(text) or text[opening] != "(":
            continue
        closing = c_text._match_delimiter(text, opening)
        start = opening + 1
        for argument in c_text._split_args(text[start:closing]):
            end = start + len(argument)
            if kind(argument) == "pointer":
                first = start + len(argument) - len(argument.lstrip())
                last = end - len(argument) + len(argument.rstrip())
                insertions.append((first, first, "camry_host_addr("))
                insertions.append((last, last, ")"))
            start = end + 1
    return syntax._apply_spans(code, insertions)


def _pointer_macro_names() -> set[str]:
    """Object macros that expand directly to a host pointer."""
    cached = getattr(_pointer_macro_names, "cached", None)
    if cached is not None:
        return cached
    found: set[str] = set()
    header = tree.COMMON_HEADER
    if header.exists():
        for line in header.read_text(encoding="utf-8").splitlines():
            match = re.match(r"#define\s+([A-Za-z_]\w*)\s+(.+)$", line.strip())
            if match is None or "(" in match.group(1):
                continue
            expr = match.group(2).lstrip()
            if "camry_host_ptr" in expr and expr.startswith("(") and not expr.startswith("(*"):
                found.add(match.group(1))
    _pointer_macro_names.cached = found
    return found


def _scalar_names(code: str) -> set[str]:
    """Locals and parameters whose values are integers, including firmware addresses."""
    pointers = syntax._pointer_names(syntax._c_signature(code), code)
    pattern = re.compile(
        r"\b(?:volatile\s+)?(?:unsigned\s+|signed\s+)?"
        r"(?:int|uint|short|ushort|char|byte|uchar|bool|long|ulong|ulonglong|longlong|"
        r"undefined[1248]?|uint(?:8|16|32|64)_t|int(?:8|16|32|64)_t|uintptr_t|size_t)"
        r"\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:;|,|\))"
    )
    return ({match.group(1) for match in pattern.finditer(code)} | syntax._ARCHITECTURAL_SCALARS) - pointers


def _is_integer_address(expr: str, scalars: set[str], pointers: set[str], pointer_macros: set[str]) -> bool:
    """True when `expr` is an integer address in the firmware address space."""
    text = expr.strip()
    while syntax._fully_wrapped(text):
        text = text[1:-1].strip()
    if text.startswith("(*((volatile uint32_t *)") or text.startswith("*((volatile uint32_t *)"):
        return True
    if re.match(r"^(?:0x[0-9A-Fa-f]+|\d+)", text):
        return True
    cast = re.match(
        r"^\(\s*(?:unsigned\s+|signed\s+)?(?:int|uint|short|ushort|char|byte|uchar|"
        r"long|ulong|ulonglong|longlong|undefined[1248]?|uint(?:8|16|32|64)_t|"
        r"int(?:8|16|32|64)_t)\s*\)\s*",
        text,
    )
    if cast:
        return _is_integer_address(text[cast.end():], scalars, pointers, pointer_macros)
    if text.startswith("("):
        return False
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text)
    if match is None:
        return False
    base = match.group(0)
    if base in pointers or base in pointer_macros:
        return False
    return base in scalars


def _split_address_of(text: str) -> tuple[str, str] | None:
    """Split `&designator + byte_offset` into the designator (with `&`) and the offset."""
    if not text.startswith("&"):
        return None
    index = 1
    if index >= len(text) or not (text[index].isalpha() or text[index] == "_"):
        return None
    while index < len(text) and (text[index].isalnum() or text[index] == "_"):
        index += 1
    while index < len(text):
        if text[index].isspace():
            if text[index:].lstrip().startswith(("+", "-")):
                break
            index += 1
            continue
        if text[index] == "[":
            try:
                index = c_text._match_delimiter(text, index, "[]", quoted=False) + 1
            except ValueError:
                return None
            continue
        if text[index] == ".":
            index += 1
            while index < len(text) and (text[index].isalnum() or text[index] == "_"):
                index += 1
            continue
        break
    base = text[:index].rstrip()
    offset = text[index:].strip()
    if offset.startswith("+"):
        offset = offset[1:].strip()
    elif offset and not offset.startswith("-"):
        return None
    return base, offset


def _rewrite_host_rewrap(code: str) -> str:
    """`camry_host_ptr` of a host pointer's low 32 bits is not a firmware address.

    `&object + byte_offset` is already inside the mapped region. Casting it
    through `int` and back aborts in `camry_host_ptr`.
    """
    needle = "camry_host_ptr((uint32_t)((int)&"
    pieces: list[str] = []
    index = 0
    while True:
        found = code.find(needle, index)
        if found < 0:
            pieces.append(code[index:])
            break
        opening = found + len("camry_host_ptr")
        try:
            closing = c_text._match_delimiter(code, opening)
        except ValueError:
            pieces.append(code[index:found + 1])
            index = found + 1
            continue
        inner = code[opening + 1:closing].strip()
        arith = inner[len("(uint32_t)"):].strip() if inner.startswith("(uint32_t)(") else ""
        if syntax._fully_wrapped(arith):
            arith = arith[1:-1].strip()
        split = _split_address_of(arith[len("(int)"):]) if arith.startswith("(int)&") else None
        if split is None:
            pieces.append(code[index:closing + 1])
            index = closing + 1
            continue
        base, offset = split
        pieces.append(code[index:found])
        if offset:
            pieces.append(f"((uint8_t *){base} + ({offset}))")
        else:
            pieces.append(f"((uint8_t *){base})")
        index = closing + 1
    return "".join(pieces)


def _firmware_word(expr: str, scalars: set[str], pointers: set[str], pointer_macros: set[str]) -> str:
    """The 32-bit firmware address an expression was trying to use as a code pointer."""
    text = expr.strip()
    while syntax._fully_wrapped(text):
        text = text[1:-1].strip()
    cast = re.match(r"^\(\s*(?:(?:const|volatile)\s+)*code\s*\*\s*\)\s*", text)
    if cast:
        text = text[cast.end():].strip()
        while syntax._fully_wrapped(text):
            text = text[1:-1].strip()
        mapped_operand = syntax._pointer_cast_operand(text)
        if mapped_operand is not None and mapped_operand.startswith("camry_host_ptr("):
            text = mapped_operand
        if text.startswith("camry_host_ptr("):
            try:
                closing = c_text._match_delimiter(text, len("camry_host_ptr"))
            except ValueError:
                return text
            if closing != len(text) - 1:
                return text
            argument = text[len("camry_host_ptr") + 1:closing].strip()
            if argument.startswith("(uint32_t)(") and argument.endswith(")"):
                argument = argument[len("(uint32_t)"):].strip()
                if syntax._fully_wrapped(argument):
                    argument = argument[1:-1].strip()
            return argument
        return text
    if text.startswith("*(code **)("):
        try:
            closing = c_text._match_delimiter(text, len("*(code **)(") - 1)
        except ValueError:
            return text
        address = text[len("*(code **)("):closing]
        return _memory_word(address, scalars, pointers, pointer_macros)
    return text


def _memory_word(expr: str, scalars: set[str], pointers: set[str], pointer_macros: set[str]) -> str:
    if _is_integer_address(expr, scalars, pointers, pointer_macros):
        return f"(*((volatile uint32_t *)camry_host_ptr((uint32_t)({expr}))))"
    return f"(*((volatile uint32_t *)({expr})))"


def _rewrite_reset_compares(code: str) -> str:
    """A stored callback compared with the reset vector is a firmware address compared with zero.

    `reset_vector` is address 0. The converted C was comparing a host pointer
    with the compiled function.
    """
    scalars = _scalar_names(code)
    pointers = syntax._pointer_names(syntax._c_signature(code), code)
    pointer_macros = _pointer_macro_names()
    marker = "(uintptr_t)(reset_vector)"
    pieces: list[str] = []
    index = 0
    while True:
        found = code.find(marker, index)
        if found < 0:
            pieces.append(code[index:])
            break
        cursor = found - 1
        while cursor >= 0 and code[cursor] in " \t":
            cursor -= 1
        if cursor < 1 or code[cursor] != "=" or code[cursor - 1] not in {"=", "!"}:
            pieces.append(code[index:found + len(marker)])
            index = found + len(marker)
            continue
        operator = "!=" if code[cursor - 1] == "!" else "=="
        close = cursor - 2
        while close >= 0 and code[close] in " \t":
            close -= 1
        if close < 0 or code[close] != ")":
            pieces.append(code[index:found + len(marker)])
            index = found + len(marker)
            continue
        try:
            opening = c_text._match_delimiter(code, close, step=-1)
        except ValueError:
            pieces.append(code[index:found + len(marker)])
            index = found + len(marker)
            continue
        prefix = "(uintptr_t)"
        if code[max(0, opening - len(prefix)):opening] != prefix:
            pieces.append(code[index:found + len(marker)])
            index = found + len(marker)
            continue
        inner = code[opening + 1:close]
        word = _firmware_word(inner, scalars, pointers, pointer_macros)
        pieces.append(code[index:opening - len(prefix)])
        pieces.append(f"(uint32_t)({word}) {operator} 0u")
        index = found + len(marker)
    return "".join(pieces)


def _rewrite_code_loads(code: str) -> str:
    """`*(code **)(firmware_address)` reads a word. It is not a host dereference."""
    scalars = _scalar_names(code)
    pointers = syntax._pointer_names(syntax._c_signature(code), code)
    pointer_macros = _pointer_macro_names()
    needle = "*(code **)("
    pieces: list[str] = []
    index = 0
    while True:
        found = code.find(needle, index)
        if found < 0:
            pieces.append(code[index:])
            break
        opening = found + len(needle) - 1
        try:
            closing = c_text._match_delimiter(code, opening)
        except ValueError:
            pieces.append(code[index:found + 1])
            index = found + 1
            continue
        expr = code[opening + 1:closing]
        word = _memory_word(expr, scalars, pointers, pointer_macros)
        after = closing + 1
        while after < len(code) and code[after] in " \t\n":
            after += 1
        if after < len(code) and code[after] == "=" and not code.startswith("==", after):
            rhs_text = c_text._assignment_rhs(code, after + 1)
            if rhs_text is None:
                pieces.append(code[index:closing + 1])
                index = closing + 1
                continue
            end = after + 1 + len(rhs_text)
            rhs = rhs_text.strip()
            entry = layout._function_entries().get(rhs)
            value = f"0x{entry:x}u" if entry is not None else f"(uint32_t)({rhs})"
            pieces.append(code[index:found])
            pieces.append(f"{word} = {value}")
            index = end
            continue
        pieces.append(code[index:found])
        pieces.append(f"((code *)(uintptr_t){word})")
        index = closing + 1
    code = "".join(pieces)
    # Code pointers and named callback pointers carry an RH850 address word.
    # Keep that word until camry_indirect resolves the actual call target.
    callback_types = {"code", *layout._function_types()}
    declarations = [
        match for match in re.finditer(
            r"^[ \t]*([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*;",
            code, re.M,
        ) if match.group(1) in callback_types
    ]
    names = {match.group(2) for match in declarations}
    kind = expressions._kind_context(syntax._c_signature(code), code)
    changes: list[tuple[int, int, str]] = []
    retyped: list[str] = []
    for declaration in declarations:
        name = declaration.group(2)
        uses = code[:declaration.start()] + code[declaration.end():]
        if syntax._returns_pointer(syntax._c_signature(code)) and re.search(
            rf"\breturn\s+{re.escape(name)}\s*;", uses,
        ):
            continue
        if re.search(rf"\*\s*{re.escape(name)}\b|\b{re.escape(name)}\s*(?:\[|->|\()", uses):
            continue
        assignments: list[tuple[int, int, str]] = []
        for match in re.finditer(rf"\b{re.escape(name)}\s*=(?!=)", code):
            start = c_text._skip_space(code, match.end())
            end = syntax._scan_side(code, start, 1, ",;")
            rhs = code[start:end].strip()
            entry = layout._function_entries().get(rhs)
            value = _firmware_word(rhs, scalars, pointers, pointer_macros)
            mapped = _host_ptr_cast(rhs)
            if entry is not None:
                value = f"0x{entry:x}u"
            elif mapped is not None:
                value = mapped[1]
            elif value == rhs and rhs not in names and kind(rhs) not in {"integer", "null"}:
                break
            call = syntax._CALL.match(value)
            if kind(value) == "pointer" or (
                call is not None
                and call.group(1) in layout._pointer_return_names()
                and c_text._match_delimiter(value, call.end() - 1) == len(value) - 1
            ):
                value = f"camry_host_addr({value})"
            assignments.append((start, end, f"(uint32_t)({value})"))
        else:
            if assignments:
                changes.extend(assignments)
                changes.append((declaration.start(), declaration.end(), f"  uint32_t {name};"))
                retyped.append(name)
    code = syntax._apply_spans(code, changes)
    for name in retyped:
        code = re.sub(
            rf"\bcamry_host_addr\(\s*{re.escape(name)}\s*\)", name, code,
        )
    return code


_FIRMWARE_CALL = "(*(int (*)())"


def _rewrite_firmware_call_wrap(code: str) -> str:
    """Call the compiled function named by a firmware address.

    The address is a `uint32_t` field, a table word, or a `code *` that still
    holds that word. It is not a host function pointer.
    """
    def framed_resolver(expr: str) -> str | None:
        # Frame instrumentation wraps the resolver callee in a comma expression.
        # Its result is already a resolved host function pointer.
        if not expr.startswith("("):
            return None
        close = c_text._match_delimiter(expr, 0)
        callee = expr[1:close].rstrip()
        suffix = ", camry_indirect"
        if not callee.endswith(suffix):
            return None
        opening = c_text._skip_space(expr, close + 1)
        if opening >= len(expr) or expr[opening] != "(":
            return None
        end = c_text._match_delimiter(expr, opening)
        if end != len(expr) - 1:
            return None
        updates = callee[:-len(suffix)]
        argument = expr[opening + 1:end]
        return f"camry_indirect(({updates}, {argument}))"

    pieces: list[str] = []
    index = 0
    while True:
        found = code.find(_FIRMWARE_CALL, index)
        if found < 0:
            pieces.append(code[index:])
            break
        start = found + len(_FIRMWARE_CALL)
        end = c_text._match_delimiter(code, found, quoted=False, required=False)
        if end is None:
            pieces.append(code[index:found + 1])
            index = found + 1
            continue
        expr = code[start:end].strip()
        resolved = framed_resolver(expr)
        if expr.startswith("camry_indirect("):
            # Migrate retained output that resolved this framed call twice,
            # truncating the first resolver's host pointer to uint32_t.
            argument = expr[len("camry_indirect("):-1].strip()
            if argument.startswith("(uint32_t)"):
                argument = argument[len("(uint32_t)"):].strip()
            while syntax._fully_wrapped(argument):
                argument = argument[1:-1].strip()
            resolved = framed_resolver(argument) or expr
        if resolved is not None:
            pieces.append(code[index:found] + _FIRMWARE_CALL + resolved + ")")
            index = end + 1
            continue
        pieces.append(code[index:found])
        pieces.append(f"(*(int (*)())camry_indirect((uint32_t)({expr}))")
        index = end
    return "".join(pieces)


def _rewrite_firmware_pointers(code: str) -> str:
    code = _rewrite_host_rewrap(code)
    code = _rewrite_reset_compares(code)
    code = _rewrite_code_loads(code)
    code = _rewrite_indirect_dispatch(code)
    return _rewrite_firmware_call_wrap(code)


def _host_ptr_cast(rhs: str) -> tuple[str, str] | None:
    match = re.match(
        r"\s*\(\(\s*(?:volatile\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\*\)\s*camry_host_ptr\(",
        rhs,
    )
    if match is None:
        return None
    try:
        close = c_text._match_delimiter(rhs, match.end() - 1)
    except ValueError:
        return None
    if rhs[close + 1:].strip() != ")":
        return None
    return match.group(1), rhs[match.end():close].strip()


def _address_value(text: str, ints: dict[str, int]) -> int | None:
    value = text.strip()
    wrapped = re.fullmatch(r"\(uint32_t\)\s*\(\s*(.*)\s*\)", value, flags=re.S)
    if wrapped:
        value = wrapped.group(1).strip()
    number = re.fullmatch(r"(0x[0-9A-Fa-f]+)u?", value)
    if number:
        parsed = int(number.group(1), 16)
        return parsed if parsed >= 0x10000 else None
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        return ints.get(value)
    return None


def _based_pointers(code: str) -> tuple[dict[str, int], dict[str, tuple[int, str, int | None]]]:
    """Locals that hold one firmware address, or a host pointer to one address."""
    spans = c_text._comment_spans(code)
    grouped: dict[str, list[str]] = {}
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)", code):
        if c_text._span_contains(spans, match.start()):
            continue
        rhs = c_text._assignment_rhs(code, match.end())
        if rhs is None:
            continue
        grouped.setdefault(match.group(1), []).append(rhs)
    ints: dict[str, int] = {}
    for name, rhss in grouped.items():
        values: list[int] = []
        for rhs in rhss:
            number = re.fullmatch(r"\s*(0x[0-9A-Fa-f]+)u?\s*", rhs)
            if number is None:
                values = []
                break
            values.append(int(number.group(1), 16))
        if values and min(values) >= 0x10000 and len(set(values)) == 1:
            ints[name] = values[0]
    pointers: dict[str, tuple[int, str, int | None]] = {}
    for name, rhss in grouped.items():
        if name in ints:
            continue
        found: list[tuple[int, str]] = []
        for rhs in rhss:
            cast = _host_ptr_cast(rhs)
            if cast is None:
                found = []
                break
            pointee, arg = cast
            base = _address_value(arg, ints)
            if base is None:
                found = []
                break
            found.append((base, pointee))
        if not found or len({item[0] for item in found}) != 1 or len({item[1] for item in found}) != 1:
            continue
        base, pointee = found[0]
        pointers[name] = (base, pointee, layout._SCALAR_STRIDE.get(pointee))
    return ints, pointers


def _expression_is_host_pointer(expr: str) -> bool:
    """True when an additive term is a pointer into the host mapping."""
    depth = 0
    start = 0
    terms: list[str] = []
    for index, char in enumerate(expr):
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        elif depth == 0 and char in "+-" and index > start:
            terms.append(expr[start:index])
            start = index + 1
    terms.append(expr[start:])
    for term in terms:
        text = term.strip()
        while text.startswith("("):
            try:
                close = c_text._match_delimiter(text, 0)
            except ValueError:
                break
            if close != len(text) - 1:
                break
            text = text[1:-1].strip()
        cast = re.match(
            r"^\(\s*(?:volatile\s+)?[A-Za-z_][A-Za-z0-9_]*\s*\*+\s*\)\s*",
            text,
        )
        if cast:
            text = text[cast.end():].strip()
            while text.startswith("("):
                try:
                    close = c_text._match_delimiter(text, 0)
                except ValueError:
                    break
                if close != len(text) - 1:
                    break
                text = text[1:-1].strip()
        if text.startswith("camry_host_ptr("):
            return True
    return False


def _firmware_pointer_word(rhs: str) -> str:
    text = rhs.strip()
    if text in {"0", "NULL", "(void *)0", "(void *)0x0"}:
        return "0"
    if text.startswith("camry_host_addr("):
        return text
    return f"camry_host_addr({text})"


def _rewrite_double_indirect(code: str) -> str:
    """Load ``**(T **)(address)`` through the pointer word at that address."""
    comments = c_text._comment_spans(code)
    kind = expressions._kind_context(syntax._c_signature(code), code)
    callbacks = {"code", *layout._function_types()}
    spans: list[tuple[int, int, str]] = []
    pattern = re.compile(r"(\*\*)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*\*\s*\)\s*\(")
    for match in pattern.finditer(code):
        if c_text._span_contains(comments, match.start()) or match.group(2) in callbacks:
            continue
        try:
            close = c_text._match_delimiter(code, match.end() - 1)
        except ValueError:
            continue
        expr = code[match.end():close].strip()
        address_kind = kind(expr)
        if address_kind == "unknown" and "camry_host_ptr" not in expr:
            continue
        if address_kind == "pointer" or _expression_is_host_pointer(expr):
            loaded = f"(*((volatile uint32_t *)({expr})))"
        else:
            loaded = (
                "(*((volatile uint32_t *)camry_host_ptr((uint32_t)("
                f"{expr}))))"
            )
        spans.append((
            match.start(), close + 1,
            f"(*((volatile {match.group(2)} *)camry_host_ptr({loaded})))",
        ))
    # Retained bodies may already have mapped the slot, but still load a
    # host-sized pointer from it: `*((T **)camry_host_ptr(address))`.
    mapped = re.compile(
        r"\*\s*\(\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*\*\s*\)\s*"
        r"camry_host_ptr\s*\("
    )
    for match in mapped.finditer(code):
        if c_text._span_contains(comments, match.start()) or match.group(1) in callbacks:
            continue
        try:
            close = c_text._match_delimiter(code, match.end() - 1)
        except ValueError:
            continue
        end = c_text._skip_space(code, close + 1)
        if end >= len(code) or code[end] != ")":
            continue
        after = c_text._skip_space(code, end + 1)
        if after < len(code) and code[after] == "=" and not code.startswith("==", after):
            continue
        address = code[match.end():close]
        loaded = f"(*((volatile uint32_t *)camry_host_ptr({address})))"
        spans.append((
            match.start(), end + 1,
            f"(({match.group(1)} *)camry_host_ptr({loaded}))",
        ))
    return syntax._apply_spans(code, spans)


def _rewrite_pointer_slot_stores(code: str, ints: dict[str, int]) -> str:
    """Convert the host pointer with ``camry_host_addr`` before storing its firmware word."""
    if not ints:
        return code
    comments = c_text._comment_spans(code)
    spans: list[tuple[int, int, str]] = []
    for name, base in ints.items():
        pattern = re.compile(
            rf"(\*+)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*(\*+)\s*\)\s*"
            rf"\(\s*(?:\(int\)\s*)?{re.escape(name)}\s*([+\-])"
        )
        for match in pattern.finditer(code):
            if c_text._span_contains(comments, match.start()):
                continue
            if len(match.group(1)) != 1 or len(match.group(3)) < 2:
                continue
            cast_close = match.group(0).find(")")
            open_addr = match.start() + match.group(0).find("(", cast_close)
            try:
                close_addr = c_text._match_delimiter(code, open_addr)
            except ValueError:
                continue
            nxt = c_text._skip_space(code, close_addr + 1)
            if nxt >= len(code) or code[nxt] != "=" or code.startswith("==", nxt):
                continue
            rhs = c_text._assignment_rhs(code, nxt + 1)
            if rhs is None:
                continue
            index = code[match.end():close_addr].strip()
            if match.group(4) == "-":
                index = f"-({index})" if index else ""
            addr = syntax._displacement(base, index, 1, "uint8_t")
            spans.append((
                match.start(), nxt + 1 + len(rhs),
                "(*((volatile uint32_t *)camry_host_ptr((uint32_t)("
                f"{addr})))) = {_firmware_pointer_word(rhs)}",
            ))
    return syntax._apply_spans(code, spans)


def _rewrite_based_pointer_uses(code: str) -> str:
    """Add a gp displacement to the firmware address, then map that address.

    ``((undefined *)camry_host_ptr(gp))[disp]`` and ``*(T *)((int)gp + disp)``
    use the host pointer as the base. The bytes add disp to the firmware address.
    """
    ints, pointers = _based_pointers(code)
    if not ints and not pointers:
        return _rewrite_pointer_word_stores(_rewrite_double_indirect(code))
    comments = c_text._comment_spans(code)
    spans: list[tuple[int, int, str]] = []
    for name, (base, pointee, scale) in pointers.items():
        for match in re.finditer(rf"\b{re.escape(name)}\b", code):
            if c_text._span_contains(comments, match.start()):
                continue
            nxt = c_text._skip_space(code, match.end())
            prev = match.start() - 1
            while prev >= 0 and code[prev] in " \t\n":
                prev -= 1
            if prev >= 0 and code[prev] == ".":
                continue
            if prev >= 0 and code[prev] == "&" and (nxt >= len(code) or code[nxt] not in "[+-"):
                continue
            if nxt >= len(code) or code.startswith(("++", "--", "+=", "-=", "->"), nxt):
                continue
            if code[nxt] == "[":
                try:
                    end = c_text._match_delimiter(code.replace("[", "(").replace("]", ")"), nxt)
                except ValueError:
                    continue
                # The replaced text uses the original brackets, so map the close back.
                end = nxt + (end - nxt)
                index = code[nxt + 1:end].strip()
                if not index:
                    continue
                spans.append((
                    match.start(), end + 1,
                    syntax._volatile_at(syntax._displacement(base, index, scale, pointee), pointee),
                ))
                continue
            if code[nxt] not in "+-":
                continue
            end = c_text._additive_end(code, nxt)
            index = code[nxt:end].strip()
            if index.startswith("+"):
                index = index[1:].strip()
            if not index or re.search(rf"\b{re.escape(name)}\b", index):
                continue
            spans.append((
                match.start(), end,
                f"(({pointee} *)camry_host_ptr((uint32_t)("
                f"{syntax._displacement(base, index, scale, pointee)})))",
            ))
    for name, base in ints.items():
        pattern = re.compile(
            rf"(\*+)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*(\*+)\s*\)\s*"
            rf"\(\s*(?:\(int\)\s*)?{re.escape(name)}\s*([+\-])"
        )
        for match in pattern.finditer(code):
            if c_text._span_contains(comments, match.start()):
                continue
            cast_close = match.group(0).find(")")
            open_addr = match.start() + match.group(0).find("(", cast_close)
            try:
                close_addr = c_text._match_delimiter(code, open_addr)
            except ValueError:
                continue
            index = code[match.end():close_addr].strip()
            if match.group(4) == "-":
                index = f"-({index})" if index else ""
            addr = syntax._displacement(base, index, 1, "uint8_t")
            outer, ctype, inner = len(match.group(1)), match.group(2), len(match.group(3))
            loaded = f"(*((volatile uint32_t *)camry_host_ptr((uint32_t)({addr}))))"
            nxt = c_text._skip_space(code, close_addr + 1)
            storing = nxt < len(code) and code[nxt] == "=" and not code.startswith("==", nxt)
            # A pointer word is stored in a later pass so the right-hand side
            # can be rewritten first, then recovered with camry_host_addr.
            if outer == 1 and inner >= 2 and storing:
                continue
            if outer == 1 and inner == 1:
                text = syntax._volatile_at(addr, ctype)
            elif outer == 1 and inner >= 2:
                text = f"(({ctype} *)camry_host_ptr({loaded}))"
            elif outer >= 2 and inner >= 2:
                text = f"(*((volatile {ctype} *)camry_host_ptr({loaded})))"
            else:
                continue
            spans.append((match.start(), close_addr + 1, text))
    code = _rewrite_double_indirect(syntax._apply_spans(code, spans))
    return _rewrite_pointer_word_stores(_rewrite_pointer_slot_stores(code, ints))


def _rewrite_pointer_word_stores(code: str) -> str:
    """A stored pointer word is the firmware address, and the slot is the lvalue.

    ``*(T **)(gp + disp) = host_pointer`` became a cast of the loaded word.
    That cast is not assignable. The bytes store the address into the slot.

    ``*(undefined1 **)(slot) = camry_host_ptr(imm)`` is the same store: the
    word is the firmware address, and a host pointer does not fit in it.
    """
    code = re.sub(
        r"\*\(undefined1 \*\*\)\(([^;\n]+)\) = "
        r"\(\(undefined \*\)camry_host_ptr\(0x([0-9a-fA-F]+)u\)\);",
        lambda match: (
            f"*((uint32_t *)({match.group(1)})) = 0x{match.group(2)}u;"
        ),
        code,
    )
    kind = expressions._kind_context(syntax._c_signature(code), code)
    slot_spans: list[tuple[int, int, str]] = []
    slots = re.compile(
        r"(\*\*?)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*\*\s*\)\s*"
    )
    for match in slots.finditer(code):
        operand = syntax._deref_operand(code, match.end())
        if operand is None or not syntax._is_deref_star(code, match.start()):
            continue
        address, end = operand
        if kind(address) == "integer":
            word = syntax._typed_load(address, "uint32_t")
        elif "camry_host_ptr" in address:
            word = f"(*((volatile uint32_t *)({address})))"
        else:
            continue
        if match.group(1) == "**":
            replacement = syntax._typed_load(word, match.group(2))
        else:
            after = c_text._skip_space(code, end)
            stored = after < len(code) and code[after] == "=" and not code.startswith("==", after)
            replacement = word if stored else (
                f"(({match.group(2)} *)camry_host_ptr((uint32_t)({word})))"
            )
        slot_spans.append((match.start(), end, replacement))
    code = syntax._apply_spans(code, slot_spans)
    pattern = re.compile(
        r"\(\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\*\)\s*camry_host_ptr\(\s*"
        r"\(\*\(\(volatile uint32_t \*\)camry_host_ptr\("
    )
    spans: list[tuple[int, int, str]] = []
    for match in pattern.finditer(code):
        try:
            inner_close = c_text._match_delimiter(code, match.end() - 1)
        except ValueError:
            continue
        addr = code[match.end():inner_close].strip()
        start = match.start()
        end = c_text._match_delimiter(code, start) + 1
        while True:
            previous = start - 1
            while previous >= 0 and code[previous] in " \t\n":
                previous -= 1
            following = c_text._skip_space(code, end)
            if (
                previous < 0 or code[previous] != "("
                or following >= len(code) or code[following] != ")"
                or c_text._match_delimiter(code, previous) != following
            ):
                break
            start, end = previous, following + 1
        cursor = c_text._skip_space(code, end)
        if cursor >= len(code) or code[cursor] != "=" or code.startswith("==", cursor):
            continue
        rhs_at = c_text._skip_space(code, cursor + 1)
        rhs = c_text._assignment_rhs(code, rhs_at)
        if rhs is None:
            continue
        spans.append((
            start, rhs_at + len(rhs),
            f"(*((volatile uint32_t *)camry_host_ptr({addr}))) = camry_host_addr({rhs.strip()})",
        ))
    return syntax._apply_spans(code, spans)


def _pointer_macro_types() -> tuple[dict[str, str], dict[tuple[str, str], tuple[str, str]]]:
    """Pointer macros and struct fields. A scalar value macro is not included."""
    cached = getattr(_pointer_macro_types, "cached", None)
    if cached is not None:
        return cached
    header = (tree.COMMON_HEADER).read_text(encoding="utf-8")
    macros = {
        name: pointee
        for name, pointee in re.findall(
            r"#define\s+([A-Za-z_][A-Za-z0-9_]*)\s+"
            r"\(\(\s*volatile\s+([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*\)\s*camry_host_ptr\(",
            header,
        )
    }
    fields: dict[tuple[str, str], tuple[str, str]] = {}
    for match in re.finditer(r"struct\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{(.*?)\n\};", header, re.S):
        struct = match.group(1)
        for line in match.group(2).splitlines():
            field = re.match(
                r"\s*(?:volatile\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(\**)\s*"
                r"([A-Za-z_][A-Za-z0-9_]*)\s*(\[[^\]]*\])?\s*;",
                line,
            )
            if field is None:
                continue
            base, stars, name, array = field.groups()
            if array:
                kind = "array"
            elif stars:
                kind = "pointer"
            elif f"struct {base} " in header or re.search(rf"\bstruct {base}\b", header):
                kind = "struct"
            else:
                kind = "scalar"
            fields[(struct, name)] = (kind, base)
    cached = (macros, fields)
    _pointer_macro_types.cached = cached
    return cached


def _strip_term(text: str) -> str:
    """Remove wrapping parentheses and a non-pointer cast."""
    macros, _fields = _pointer_macro_types()
    while True:
        text = text.strip()
        if not text.startswith("("):
            return text
        try:
            close = c_text._match_delimiter(text, 0)
        except ValueError:
            return text
        if close == len(text) - 1:
            text = text[1:-1]
            continue
        cast = re.match(r"^\(\s*[^()*\[\].]+\s*\)\s*", text)
        if cast is None or any(re.search(rf"\b{re.escape(name)}\b", cast.group(0)) for name in macros):
            return text
        text = text[cast.end():]


def _term_is_host_pointer(term: str) -> bool:
    """True when the term retains a pointer macro's host-pointer representation."""
    macros, fields = _pointer_macro_types()
    text = _strip_term(term)
    match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)", text)
    if match is None or match.group(1) not in macros:
        return False
    kind = ("pointer", macros[match.group(1)])
    rest = text[match.end():]
    while rest.strip():
        rest = rest.lstrip()
        if rest.startswith("["):
            try:
                close = c_text._match_delimiter(rest, 0, "[]", quoted=False)
            except ValueError:
                return False
            rest = rest[close + 1:]
            if kind[0] == "pointer":
                target = kind[1]
                kind = ("struct", target) if (target, ) and any(
                    struct == target for struct, _name in fields
                ) else ("scalar", target)
            elif kind[0] == "array":
                kind = ("scalar", kind[1])
            else:
                return False
            continue
        field = re.match(r"\.\s*([A-Za-z_][A-Za-z0-9_]*)", rest)
        if field is None or kind[0] != "struct":
            return False
        info = fields.get((kind[1], field.group(1)))
        if info is None:
            return False
        kind = info
        rest = rest[field.end():]
    return kind[0] in {"pointer", "array"}


def _rewrite_truncated_host_pointers(code: str) -> str:
    """A pointer macro cast to uint32_t keeps the low half of a host address.

    ``camry_host_ptr((uint32_t)(slots[1].bytes + offset))`` must add ``offset``
    to the firmware address ``camry_host_addr`` recovers. A loaded scalar field
    is already that kind of integer and stays as it is.
    """
    macros, _fields = _pointer_macro_types()
    if not any(name in code for name in macros):
        return code
    needle = "camry_host_ptr((uint32_t)("
    pieces: list[str] = []
    cursor = 0
    start = 0
    while True:
        at = code.find(needle, start)
        if at < 0:
            pieces.append(code[cursor:])
            break
        open_paren = at + len("camry_host_ptr")
        try:
            close = c_text._match_delimiter(code, open_paren)
        except ValueError:
            start = at + len(needle)
            continue
        inner = code[open_paren + 1:close].strip()
        wrapped = re.fullmatch(r"\(uint32_t\)\s*\((.*)\)", inner, re.S)
        if wrapped is None:
            start = at + len(needle)
            continue
        expr = wrapped.group(1).strip()
        depth = 0
        terms: list[tuple[str, str]] = []
        term_at = 0
        op = ""
        index = 0
        while index < len(expr):
            char = expr[index]
            if char in "([{":
                depth += 1
            elif char in ")]}":
                depth -= 1
            elif depth == 0 and char in "+-" and index > term_at:
                terms.append((op, expr[term_at:index]))
                op = char
                term_at = index + 1
            index += 1
        terms.append((op, expr[term_at:]))
        changed = False
        rebuilt: list[str] = []
        for sign, term in terms:
            body = term.strip()
            if body and not body.startswith("camry_host_addr(") and _term_is_host_pointer(body):
                body = f"camry_host_addr({body})"
                changed = True
            rebuilt.append(f"{sign} {body}" if sign else body)
        if not changed:
            start = close + 1
            continue
        pieces.append(code[cursor:at])
        pieces.append("camry_host_ptr((uint32_t)(" + " ".join(rebuilt) + "))")
        cursor = close + 1
        start = cursor
    return "".join(pieces)


def _address_sum(expr: str) -> bool:
    """True when expr adds or subtracts at the top level, ignoring `->`."""
    depth = 0
    index = 0
    while index < len(expr):
        char = expr[index]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif depth == 0 and char in "+-" and index > 0 and expr[index - 1] not in "+-<>(":
            return True
        index += 1
    return False


def _leading_byte_cast(code: str, index: int) -> int | None:
    """Start of a `(byte)` / `(char)` cast whose operand begins at `index`."""
    cursor = index - 1
    while cursor >= 0 and code[cursor] in " \t\n\r":
        cursor -= 1
    if cursor < 0 or code[cursor] != ")":
        return None
    start = c_text._match_delimiter(code, cursor, step=-1, quoted=False, required=False)
    if start is None:
        return None
    inner = " ".join(code[start + 1:cursor].split())
    width = _POINTEE_WIDTH.get(inner)
    return start if "*" not in inner and width is not None and width[1] == 1 else None


def _expr_is_byte(expr: str, destinations: dict[str, tuple[str, int]]) -> bool:
    text = " ".join(expr.split())
    if re.fullmatch(r"'(?:\\.|[^'\\])'", text):
        return True
    name = re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text)
    if name is not None:
        found = destinations.get(name.group(0))
        return found is not None and found[1] == 1
    return re.match(
        r"^\(?\*\(\((?:volatile )?(?:uchar|byte|char|undefined1|undefined|uint8_t|int8_t) \*\)",
        text,
    ) is not None


def _used_as_byte(
    code: str, start: int, end: int, destinations: dict[str, tuple[str, int]],
) -> bool:
    """The value at [start, end) is a single-byte load."""
    if _leading_byte_cast(code, start) is not None:
        return True
    assigned = _assigned_byte(code, start, destinations)
    if assigned is not None and assigned[1] == 1:
        return True
    nxt = c_text._skip_space(code, end)
    if code.startswith(("==", "!="), nxt):
        rhs_end = syntax._scan_side(code, nxt + 2, 1, ",;)")
        return _expr_is_byte(code[nxt + 2:rhs_end], destinations)
    op, op_at = syntax._compare_before(code, start)
    if op in {"==", "!="}:
        lhs_at = syntax._scan_side(code, op_at - 1, -1, ",;(")
        return _expr_is_byte(code[lhs_at:op_at], destinations)
    return False


def _ident_before(code: str, pos: int) -> str | None:
    index = pos - 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    end = index + 1
    while index >= 0 and (code[index].isalnum() or code[index] == "_"):
        index -= 1
    name = code[index + 1:end]
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return name
    return None


def _receiver_start(code: str, op_at: int) -> int | None:
    """Object before `.field` or `->field` at `op_at`."""
    index = op_at - 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    if index >= 0 and code[index] == "]":
        try:
            index = c_text._match_delimiter(code, index, "[]", step=-1, quoted=False) - 1
        except ValueError:
            return None
        while index >= 0 and code[index] in " \t\n\r":
            index -= 1
    end = index + 1
    while index >= 0 and (code[index].isalnum() or code[index] == "_"):
        index -= 1
    if end == index + 1:
        return None
    return index + 1


_POINTER_ARRAYS: dict[str, tuple[str, int]] | None = None
_DOUBLE_POINTERS: dict[str, str] | None = None


def _subscript_expr_start(code: str, bracket: int) -> int | None:
    """Start of `object->field` or `name` immediately before `[`."""
    index = bracket - 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    if index < 0:
        return None
    start = None
    while index >= 0:
        end = index + 1
        while index >= 0 and (code[index].isalnum() or code[index] == "_"):
            index -= 1
        if end == index + 1:
            return start
        start = index + 1
        while index >= 0 and code[index] in " \t\n\r":
            index -= 1
        if index >= 1 and code.startswith("->", index - 1):
            index -= 2
        elif index >= 0 and code[index] == ".":
            index -= 1
        else:
            return start
        while index >= 0 and code[index] in " \t\n\r":
            index -= 1
    return start


def _pointer_array_pointees() -> dict[str, tuple[str, int]]:
    """`field[i][j]` on `uchar *32[N]` is the byte at the loaded pointer."""
    global _POINTER_ARRAYS
    if _POINTER_ARRAYS is not None:
        return _POINTER_ARRAYS
    scalars = {
        "uchar": ("uint8_t", 1),
        "byte": ("uint8_t", 1),
        "char": ("uint8_t", 1),
        "undefined1": ("uint8_t", 1),
        "undefined": ("uint8_t", 1),
    }
    found: dict[str, tuple[str, int] | None] = {}
    for row in layout._struct_rows().values():
        for field in row["fields"]:
            base, stars, array = layout._ghidra_base(field["type"])
            if stars != 1 or not array:
                continue
            width = scalars.get(base)
            previous = found.get(field["name"], width)
            found[field["name"]] = width if previous == width else None
    _POINTER_ARRAYS = {
        name: width for name, width in found.items() if width is not None
    }
    return _POINTER_ARRAYS


def _double_pointer_fields() -> dict[str, str]:
    """`field[index]` on `T *32 *32` loads one pointer to T."""
    global _DOUBLE_POINTERS
    if _DOUBLE_POINTERS is not None:
        return _DOUBLE_POINTERS
    functions = layout._function_types()
    found: dict[str, set[str | None]] = {}
    for row in layout._struct_rows().values():
        for field in row["fields"]:
            base, stars, array = layout._ghidra_base(field["type"])
            kind: str | None = base if stars == 2 and not array and base not in functions else None
            found.setdefault(field["name"], set()).add(kind)
    _DOUBLE_POINTERS = {
        name: next(iter(kinds))
        for name, kinds in found.items()
        if len(kinds) == 1 and None not in kinds
    }
    return _DOUBLE_POINTERS


def _rewrite_slot_word_uses(code: str) -> str:
    """Uncast `*SLOT` and `SLOT[index]` load a word through the pointer word.

    The slot macro is that word. A byte cast was already rewritten as `ld.bu`.
    A bare subscript is the word at the pointer plus four times the index.
    """
    slots = expressions._uint32_slot_names()
    spans = c_text._comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    index = 0
    while index < len(code):
        if index < cursor or c_text._span_contains(spans, index):
            index += 1
            continue
        if syntax._is_deref_star(code, index):
            parsed = _slot_deref(code, index, slots)
            if parsed is not None and _leading_byte_cast(code, index) is None:
                name, end = parsed
                pieces.append(code[cursor:index])
                pieces.append(syntax._typed_load(name, "uint32_t"))
                cursor = end
                index = end
                continue
        if index == 0 or not (code[index - 1].isalnum() or code[index - 1] == "_"):
            match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[index:])
            if (
                match is not None
                and match.group(0) in slots
                and not _amp_before(code, index)
                and _leading_byte_cast(code, index) is None
            ):
                name = match.group(0)
                nxt = c_text._skip_space(code, index + len(name))
                if nxt < len(code) and code[nxt] == "[":
                    try:
                        end = c_text._match_delimiter(code, nxt, "[]", quoted=False)
                    except ValueError:
                        end = -1
                    further = c_text._skip_space(code, end + 1) if end >= 0 else -1
                    if end >= 0 and not (further < len(code) and code[further] == "["):
                        inner = code[nxt + 1:end]
                        pieces.append(code[cursor:index])
                        pieces.append(syntax._typed_load(
                            f"({name}) + (uint32_t)({inner}) * 4u",
                            "uint32_t",
                        ))
                        cursor = end + 1
                        index = cursor
                        continue
        index += 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_loaded_word_indexes(code: str) -> str:
    """`(byte)SLOT[index]` is the byte at the loaded pointer plus the index.

    The slot macro is the pointer word. A word-scaled `SLOT[1]` has no byte
    cast and stays a subscript.
    """
    slots = expressions._uint32_slot_names()
    spans = c_text._comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\[", code):
        if match.start() < cursor or c_text._span_contains(spans, match.start()):
            continue
        if match.group(1) not in slots:
            continue
        cast_at = _leading_byte_cast(code, match.start())
        if cast_at is None or cast_at < cursor:
            continue
        try:
            end = c_text._match_delimiter(code, match.end() - 1, "[]", quoted=False)
        except ValueError:
            continue
        nxt = c_text._skip_space(code, end + 1)
        if nxt < len(code) and code[nxt] == "[":
            continue
        index = code[match.end():end]
        pieces.append(code[cursor:cast_at])
        pieces.append(syntax._typed_load(
            f"{match.group(1)} + (uint32_t)({index})",
            "uint8_t",
        ))
        cursor = end + 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_pointer_word_indexes(code: str) -> str:
    """Index a loaded pointer word at the width of that load.

    `bases[slot][offset]` assigned to a byte is `ld.bu` at the selected base.
    `record->excluded_blocks[i][j]` is the byte at that pointer word.
    `configuration[n].connections[index]` loads one `F33DcmConnection` pointer
    (`shl 2`, then `ld.w`).
    """
    destinations = _byte_destinations(code)
    arrays = _pointer_array_pointees()
    doubles = _double_pointer_fields()
    tables = expressions._uint32_array_names()
    slots = expressions._uint32_slot_names()
    local_tables: dict[str, str] = {}
    for declaration in re.finditer(
        r"^[ \t]*([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*\*\s*"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*;", code, re.M,
    ):
        pointee, name = declaration.groups()
        assignments = list(re.finditer(rf"\b{re.escape(name)}\s*=(?!=)\s*([^;]+);", code))
        # An address of a firmware word table is not an array of host pointers.
        if assignments and all(
            (address := re.fullmatch(r"&\s*([A-Za-z_][A-Za-z0-9_]*)", item.group(1).strip()))
            is not None and address.group(1) in slots
            for item in assignments
        ):
            local_tables[name] = pointee
    spans = c_text._comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    start = 0
    while True:
        bracket = code.find("[", start)
        if bracket < 0:
            pieces.append(code[cursor:])
            break
        if bracket < cursor or c_text._span_contains(spans, bracket):
            start = bracket + 1
            continue
        close = bracket - 1
        while close >= cursor and code[close] in " \t\n":
            close -= 1
        inner_open = None
        if close >= cursor and code[close] == "]":
            try:
                inner_open = c_text._match_delimiter(code, close, "[]", step=-1, quoted=False)
            except ValueError:
                inner_open = None
        if inner_open is not None and inner_open >= cursor:
            field = _ident_before(code, inner_open)
            base_start = _subscript_expr_start(code, inner_open)
            try:
                end = c_text._match_delimiter(code, bracket, "[]", quoted=False)
            except ValueError:
                start = bracket + 1
                continue
            nxt = c_text._skip_space(code, end + 1)
            if nxt < len(code) and code[nxt] == "=" and not code.startswith("==", nxt):
                start = bracket + 1
                continue
            index = code[bracket + 1:end]
            pointee = arrays.get(field) if field else None
            root = code[base_start:inner_open].strip() if base_start is not None else ""
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", root):
                root = ""
            byte = (
                pointee is not None and pointee[1] == 1
            ) or (
                root in tables and base_start is not None and _used_as_byte(
                    code, base_start, end + 1, destinations,
                )
            )
            if byte and base_start is not None:
                inner = code[base_start:close + 1]
                pieces.append(code[cursor:base_start])
                pieces.append(syntax._typed_load(
                    f"({inner}) + (uint32_t)({index})",
                    "uint8_t",
                ))
                cursor = end + 1
                start = cursor
                continue
        field_at = bracket
        while field_at > cursor and code[field_at - 1] in " \t\n":
            field_at -= 1
        name = _ident_before(code, field_at)
        if name in local_tables:
            base_start = field_at - len(name)
            try:
                end = c_text._match_delimiter(code, bracket, "[]", quoted=False)
            except ValueError:
                start = bracket + 1
                continue
            nxt = c_text._skip_space(code, end + 1)
            if nxt < len(code) and code[nxt] == "=" and not code.startswith("==", nxt):
                start = bracket + 1
                continue
            index = code[bracket + 1:end]
            loaded = (
                f"(*((volatile uint32_t *)((uint8_t *){name} + "
                f"(uint32_t)({index}) * 4u)))"
            )
            pieces.append(code[cursor:base_start])
            pieces.append(syntax._host_pointer(loaded, local_tables[name]))
            cursor = end + 1
            start = cursor
            continue
        pointee_name = doubles.get(name) if name else None
        if pointee_name is None:
            start = bracket + 1
            continue
        op_at = field_at - len(name)
        while op_at > 0 and code[op_at - 1] in " \t\n":
            op_at -= 1
        if code.startswith("->", op_at - 2):
            op_at -= 2
        elif op_at > 0 and code[op_at - 1] == ".":
            op_at -= 1
        else:
            start = bracket + 1
            continue
        receiver = _receiver_start(code, op_at)
        if receiver is None or receiver < cursor:
            start = bracket + 1
            continue
        try:
            end = c_text._match_delimiter(code, bracket, "[]", quoted=False)
        except ValueError:
            start = bracket + 1
            continue
        index = code[bracket + 1:end]
        field_expr = code[receiver:field_at].strip()
        pieces.append(code[cursor:receiver])
        pieces.append(syntax._host_pointer(
            syntax._typed_load(
                f"({field_expr}) + (uint32_t)({index}) * 4u",
                "uint32_t",
            ),
            pointee_name,
        ))
        cursor = end + 1
        start = cursor
    return "".join(pieces)


def _rewrite_integer_subscripts(code: str) -> str:
    """`(firmware_address + offset)[index]` is the byte at that address.

    A byte-pointer local rewritten as a uint32, and a pointer word plus an
    offset, are indexed with `ld.bu`/`st.b`. A sum that is still a pointer
    type-checks and is left alone.
    """
    kind = expressions._kind_context(syntax._c_signature(code), code)
    pieces: list[str] = []
    cursor = 0
    start = 0
    while True:
        bracket = code.find("[", start)
        if bracket < 0:
            pieces.append(code[cursor:])
            break
        close = bracket - 1
        while close >= cursor and code[close] in " \t\n":
            close -= 1
        if close < cursor or code[close] != ")":
            start = bracket + 1
            continue
        open_paren = c_text._match_delimiter(code, close, step=-1, required=False)
        if open_paren is None or open_paren < cursor:
            start = bracket + 1
            continue
        before = open_paren - 1
        while before >= 0 and code[before] in " \t\n":
            before -= 1
        if before >= 0 and (code[before].isalnum() or code[before] == "_"):
            start = bracket + 1
            continue
        inner = code[open_paren + 1:close]
        collapsed = " ".join(inner.split())
        if syntax._is_pointer_type(collapsed) or syntax._is_int_type(collapsed) or not _address_sum(inner):
            start = bracket + 1
            continue
        if kind(inner) != "integer":
            start = bracket + 1
            continue
        try:
            end = c_text._match_delimiter(code, bracket, "[]", quoted=False)
        except ValueError:
            start = bracket + 1
            continue
        index = _rewrite_integer_subscripts(code[bracket + 1:end])
        address = _rewrite_integer_subscripts(inner)
        pieces.append(code[cursor:open_paren])
        pieces.append(syntax._typed_load(f"({address}) + (uint32_t)({index})", "uint8_t"))
        cursor = end + 1
        start = cursor
    return "".join(pieces)


def _rewrite_loaded_pointer_subscripts(code: str) -> str:
    """`(&PTR_...)[slot][index]` is the byte at the loaded pointer plus index.

    The slot load is a uint32. The bytes then add the index and use `ld.bu`/`st.b`.
    """
    needle = "(*((volatile uint32_t *)camry_host_ptr("
    pieces: list[str] = []
    cursor = 0
    start = 0
    while True:
        at = code.find(needle, start)
        if at < 0:
            pieces.append(code[cursor:])
            break
        open_paren = at + len(needle) - 1
        if open_paren >= len(code) or code[open_paren] != "(":
            start = at + len(needle)
            continue
        try:
            close = c_text._match_delimiter(code, open_paren)
        except ValueError:
            start = at + len(needle)
            continue
        if not code.startswith("))", close + 1):
            start = close + 1
            continue
        bracket = c_text._skip_space(code, close + 3)
        if bracket >= len(code) or code[bracket] != "[":
            start = close + 1
            continue
        try:
            end = c_text._match_delimiter(code, bracket, "[]", quoted=False)
        except ValueError:
            start = close + 1
            continue
        expr = _rewrite_loaded_pointer_subscripts(code[open_paren + 1:close])
        index = _rewrite_loaded_pointer_subscripts(code[bracket + 1:end])
        pieces.append(code[cursor:at])
        pieces.append(
            "(*((volatile uint8_t *)camry_host_ptr((uint32_t)("
            f"(*((volatile uint32_t *)camry_host_ptr({expr}))) + (uint32_t)({index})))))"
        )
        cursor = end + 1
        start = cursor
    return "".join(pieces)


_POINTEE_WIDTH = {
    "char": ("uint8_t", 1),
    "byte": ("uint8_t", 1),
    "uchar": ("uint8_t", 1),
    "undefined1": ("uint8_t", 1),
    "undefined": ("uint8_t", 1),
    "code": ("uint8_t", 1),
    "ushort": ("uint16_t", 2),
    "short": ("int16_t", 2),
    "undefined2": ("uint16_t", 2),
    "int": ("int32_t", 4),
    "uint": ("uint32_t", 4),
    "undefined4": ("uint32_t", 4),
    "ulong": ("uint32_t", 4),
    "long": ("int32_t", 4),
    "unsigned int": ("uint32_t", 4),
}
_POINTEE_ALT = (
    "undefined1|undefined2|undefined4|unsigned int|undefined|uchar|ushort|ulong|"
    "byte|char|code|short|uint|int|long"
)
_BYTE_DECL = re.compile(
    r"^(?:(?:static|const|volatile|extern|unsigned|signed)\s+)*"
    r"(char|byte|uchar|undefined1|undefined)\s+(.+)$"
)


def _stored_pointer_pointees(code: str) -> dict[str, tuple[str, int]]:
    """`(char *)` / `(int *)` on a uint32 slot is the width of `*slot`."""
    slots = expressions._uint32_slot_names()
    found: dict[str, tuple[str, int] | None] = {}

    def add(name: str, type_name: str) -> None:
        width = _POINTEE_WIDTH.get(type_name)
        if width is None or name not in slots:
            return
        previous = found.get(name, width)
        found[name] = width if previous == width else None

    compared = re.compile(
        rf"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:==|!=|<=|>=|<|>)\s*"
        rf"\(\s*({_POINTEE_ALT})\s*\*\s*\)\s*(?:0x0+|0+)\b"
    )
    compared_left = re.compile(
        rf"\(\s*({_POINTEE_ALT})\s*\*\s*\)\s*(?:0x0+|0+)\s*"
        rf"(?:==|!=|<=|>=|<|>)\s*([A-Za-z_][A-Za-z0-9_]*)\b"
    )
    cast = re.compile(
        rf"\(\s*({_POINTEE_ALT})\s*\*\s*\)\s*([A-Za-z_][A-Za-z0-9_]*)\b"
    )
    for match in compared.finditer(code):
        add(match.group(1), match.group(2))
    for match in compared_left.finditer(code):
        add(match.group(2), match.group(1))
    for match in cast.finditer(code):
        add(match.group(2), match.group(1))
    return {name: width for name, width in found.items() if width is not None}


def _byte_destinations(code: str) -> dict[str, tuple[str, int]]:
    found: dict[str, tuple[str, int]] = {}
    widths = {
        "char": ("uint8_t", 1),
        "byte": ("uint8_t", 1),
        "uchar": ("uint8_t", 1),
        "undefined1": ("uint8_t", 1),
        "undefined": ("uint8_t", 1),
    }
    for line in code.splitlines():
        text = line.strip()
        if not text.endswith(";") or "(" in text:
            continue
        match = _BYTE_DECL.match(text[:-1].strip())
        if match is None:
            continue
        width = widths[match.group(1)]
        for part in match.group(2).split(","):
            name = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", part.split("=", 1)[0])
            if name:
                found[name.group(1)] = width
    for name, _address, expansion in layout._named_macros():
        match = re.match(r"\(\*\(\(volatile\s+(uint8_t|int8_t)\s+\*\)", expansion)
        if match:
            found[name] = (match.group(1), 1)
    return found


def _value_cast_width(code: str, star: int) -> tuple[str, int] | None:
    """`(byte)*slot` names the load width. A widening `(uint)*` does not."""
    index = star - 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    if index < 0 or code[index] != ")":
        return None
    cursor = c_text._match_delimiter(code, index, step=-1, quoted=False, required=False)
    if cursor is None:
        return None
    inner = " ".join(code[cursor + 1:index].split())
    if "*" in inner:
        return None
    width = _POINTEE_WIDTH.get(inner)
    return width if width is not None and width[1] <= 2 else None


def _compared_with_char(code: str, end: int) -> bool:
    nxt = c_text._skip_space(code, end)
    if not code.startswith(("==", "!="), nxt):
        return False
    rhs = c_text._skip_space(code, nxt + 2)
    return re.match(r"'(?:\\.|[^'\\])'", code[rhs:]) is not None


def _assigned_byte(code: str, star: int, destinations: dict[str, tuple[str, int]]) -> tuple[str, int] | None:
    index = star - 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    if index < 1 or code[index] != "=" or code[index - 1] in "=!<>":
        return None
    cursor = index - 1
    while cursor >= 0 and code[cursor] in " \t\n\r":
        cursor -= 1
    end = cursor + 1
    while cursor >= 0 and (code[cursor].isalnum() or code[cursor] == "_"):
        cursor -= 1
    name = code[cursor + 1:end]
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return None
    bound = cursor
    while bound >= 0 and code[bound] in " \t\n\r":
        bound -= 1
    if bound >= 0 and code[bound] not in ";{},(":
        return None
    return destinations.get(name)


def _load_is_whole_rhs(code: str, end: int) -> bool:
    nxt = c_text._skip_space(code, end)
    return nxt >= len(code) or code[nxt] in ";,)"


def _anon_load_width(
    code: str, star: int, end: int, destinations: dict[str, tuple[str, int]],
) -> tuple[str, int] | None:
    cast = _value_cast_width(code, star)
    if cast is not None:
        return cast
    if _compared_with_char(code, end):
        return ("uint8_t", 1)
    if _load_is_whole_rhs(code, end):
        assigned = _assigned_byte(code, star, destinations)
        if assigned is not None and assigned[1] == 1:
            return assigned
    return None


def _slot_deref(code: str, star: int, slots: set[str]) -> tuple[str, int] | None:
    at = c_text._skip_space(code, star + 1)
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[at:])
    if match is None or match.group(0) not in slots:
        return None
    end = at + match.end()
    nxt = c_text._skip_space(code, end)
    if nxt < len(code) and code[nxt] == "[":
        return None
    return match.group(0), end


def _word_deref(code: str, star: int) -> int | None:
    at = c_text._skip_space(code, star + 1)
    if at >= len(code) or code[at] != "(":
        return None
    try:
        end = c_text._match_delimiter(code, at)
    except ValueError:
        return None
    if syntax._is_word_load(code[at:end + 1]):
        return end + 1
    return None


def _slot_widths(
    code: str,
    pointees: dict[str, tuple[str, int]],
    destinations: dict[str, tuple[str, int]],
) -> dict[str, tuple[str, int]]:
    slots = expressions._uint32_slot_names()
    widths = {name: width for name, width in pointees.items() if name in slots}
    conflicts: set[str] = set()
    index = 0
    while index < len(code):
        if not syntax._is_deref_star(code, index):
            index += 1
            continue
        parsed = _slot_deref(code, index, slots)
        if parsed is None:
            index += 1
            continue
        name, end = parsed
        width = pointees.get(name) or _anon_load_width(code, index, end, destinations)
        if width is not None:
            previous = widths.get(name)
            if previous is not None and previous != width:
                conflicts.add(name)
            else:
                widths[name] = width
        index = end
    for name in conflicts:
        widths.pop(name, None)
    return widths


def _rewrite_stored_pointer_loads(code: str, pointees: dict[str, tuple[str, int]]) -> str:
    """`*DAT` and `*(&PTR)[i]` load through the pointer word those expressions are.

    The slot macro is already the firmware address. The width is the pointer
    cast, a `(byte)*` cast, a character compare, or a byte destination.
    """
    destinations = _byte_destinations(code)
    widths = _slot_widths(code, pointees, destinations)
    slots = set(widths)
    spans = c_text._comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    index = 0
    while index < len(code):
        if c_text._span_contains(spans, index):
            index += 1
            continue
        if syntax._is_deref_star(code, index):
            parsed = _slot_deref(code, index, slots)
            if parsed is not None:
                name, end = parsed
                pieces.append(code[cursor:index])
                pieces.append(syntax._typed_load(name, widths[name][0]))
                cursor = end
                index = end
                continue
            word_end = _word_deref(code, index)
            if word_end is not None:
                width = _anon_load_width(code, index, word_end, destinations)
                if width is not None:
                    at = c_text._skip_space(code, index + 1)
                    pieces.append(code[cursor:index])
                    pieces.append(syntax._typed_load(code[at:word_end], width[0]))
                    cursor = word_end
                    index = word_end
                    continue
        if index == 0 or not (code[index - 1].isalnum() or code[index - 1] == "_"):
            match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[index:])
            if (
                match is not None
                and match.group(0) in widths
                and not _amp_before(code, index)
            ):
                name = match.group(0)
                nxt = c_text._skip_space(code, index + len(name))
                if nxt < len(code) and code[nxt] == "[":
                    try:
                        end = c_text._match_delimiter(code, nxt, "[]", quoted=False)
                    except ValueError:
                        end = -1
                    if end >= 0:
                        inner = _rewrite_stored_pointer_loads(code[nxt + 1:end], pointees)
                        ctype, size = widths[name]
                        pieces.append(code[cursor:index])
                        pieces.append(syntax._typed_load(
                            f"({name}) + (uint32_t)({inner}) * {size}u",
                            ctype,
                        ))
                        cursor = end + 1
                        index = cursor
                        continue
        index += 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _amp_before(code: str, index: int) -> bool:
    cursor = index - 1
    while cursor >= 0 and code[cursor] in " \t\n\r":
        cursor -= 1
    return cursor >= 0 and code[cursor] == "&"


def _find_field(struct: dict | None, name: str) -> dict | None:
    if struct is None:
        return None
    for field in struct["fields"]:
        if field["name"] == name:
            return field
    return None


def _receiver_chain(code: str, op_at: int) -> tuple[int, list[tuple[str, str]]] | None:
    """Fields before the operator at `op_at`, root first."""
    index = op_at - 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    parts: list[tuple[str, str]] = []
    while index >= 0:
        end = index + 1
        while index >= 0 and (code[index].isalnum() or code[index] == "_"):
            index -= 1
        name = code[index + 1:end]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            return None
        cursor = index
        while cursor >= 0 and code[cursor] in " \t\n\r":
            cursor -= 1
        if cursor >= 1 and code.startswith("->", cursor - 1):
            parts.append(("->", name))
            index = cursor - 2
            while index >= 0 and code[index] in " \t\n\r":
                index -= 1
            continue
        if cursor >= 0 and code[cursor] == ".":
            parts.append((".", name))
            index = cursor - 1
            while index >= 0 and code[index] in " \t\n\r":
                index -= 1
            continue
        parts.append(("", name))
        parts.reverse()
        return index + 1, parts
    return None


def _chain_struct(
    parts: list[tuple[str, str]],
    var_types: dict[str, str],
    struct_pointers: set[str],
    structs: dict[str, dict],
) -> str | None:
    if not parts or parts[0][0] != "":
        return None
    current = var_types.get(parts[0][1])
    if current is None:
        return None
    current_ptr = parts[0][1] in struct_pointers
    for op, name in parts[1:]:
        if (current_ptr and op != "->") or (not current_ptr and op != "."):
            return None
        field = _find_field(structs.get(current), name)
        if field is None:
            return None
        base, stars, array = layout._ghidra_base(field["type"])
        if stars or array or base not in structs:
            return None
        current = base
        current_ptr = False
    if current_ptr:
        return None
    return current


def _rewrite_nested_pointer_fields(code: str) -> str:
    """`obj.nested.pointer_field[i]` uses the layout pointee, one field past a struct."""
    pointed = layout._pointer_field_types()
    if not pointed:
        return code
    by_field: dict[str, dict[str, str]] = {}
    for (struct, field), element in pointed.items():
        by_field.setdefault(field, {})[struct] = element
    var_types, struct_pointers = layout._struct_bindings(code)
    if not var_types:
        return code
    structs = layout._struct_rows()
    pattern = re.compile(
        r"(?:->|\.)\s*("
        + "|".join(re.escape(name) for name in sorted(by_field, key=len, reverse=True))
        + r")\b"
    )
    spans = c_text._comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    for match in pattern.finditer(code):
        if match.start() < cursor or c_text._span_contains(spans, match.start()):
            continue
        if syntax._enclosing_call(code, match.start(), "camry_host_ptr"):
            continue
        chain = _receiver_chain(code, match.start())
        if chain is None:
            continue
        start, parts = chain
        if len(parts) < 2:
            continue
        struct = _chain_struct(parts, var_types, struct_pointers, structs)
        element = by_field[match.group(1)].get(struct) if struct else None
        if element is None:
            continue
        nxt = c_text._skip_space(code, match.end())
        star = start - 1
        while star >= 0 and code[star] in " \t\n\r":
            star -= 1
        deref = star >= 0 and syntax._is_deref_star(code, star)
        arithmetic = (
            nxt < len(code)
            and code[nxt] in "+-"
            and not (nxt + 1 < len(code) and code[nxt + 1] in "=+-")
        )
        if not (deref or arithmetic or (nxt < len(code) and code[nxt] == "[")):
            continue
        pieces.append(code[cursor:start])
        pieces.append(syntax._host_pointer(code[start:match.end()], element))
        cursor = match.end()
    pieces.append(code[cursor:])
    return "".join(pieces)


def _span_is_bare_compare(code: str, start: int, end: int) -> bool:
    """True when [start, end) compares firmware addresses as integers.

    `param + (length - 1)` is still the address register: a byte pointer
    adds that many bytes. A dereference, call, or subscript is not.
    """
    right = end
    while right < len(code) and code[right] in " \t\n":
        right += 1
    if (
        right < len(code)
        and code[right] in "+-"
        and not code.startswith(("+=", "-=", "++", "--"), right)
    ):
        end = syntax._expr_end_bound(code, right)
    for _ in range(6):
        left = start - 1
        while left >= 0 and code[left] in " \t\n":
            left -= 1
        if left >= 0 and code[left] in "*&[.":
            return False
        if left >= 1 and code[left - 1:left + 1] == "->":
            return False
        right = end
        while right < len(code) and code[right] in " \t\n":
            right += 1
        if right < len(code) and code[right] in "[(":
            return False
        if syntax._is_compare_operand(code, start, end):
            return True
        if left < 0 or right >= len(code) or code[left] != "(" or code[right] != ")":
            return False
        start, end = left, right + 1
    return False


def _parameter_is_address_word(body: str, name: str) -> bool:
    """A byte-pointer parameter the bytes only compare, never load through."""
    found = False
    for match in re.finditer(rf"\b{re.escape(name)}\b", body):
        found = True
        if not _span_is_bare_compare(body, match.start(), match.end()):
            return False
    return found


def _rewrite_address_parameters(code: str) -> str:
    """`undefined *param` that is only compared is the address register.

    Callers pass `camry_host_ptr` of that register because the prototype is a
    pointer. The `cmp` is on the register, so the compare uses the firmware
    address `camry_host_addr` recovers. The prototype stays a pointer.
    """
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    signature, body = code[:brace], code[brace:]
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening:
        return code
    params = signature[opening + 1:closing]
    names = [
        match.group(1)
        for match in re.finditer(
            r"\b(?:undefined1|undefined|byte|uchar|char|code)\s*\*\s*"
            r"([A-Za-z_][A-Za-z0-9_]*)",
            params,
        )
        if _parameter_is_address_word(body, match.group(1))
    ]
    for name in names:
        pieces: list[str] = []
        cursor = 0
        for match in re.finditer(rf"\b{re.escape(name)}\b", body):
            if match.start() < cursor:
                continue
            if not _span_is_bare_compare(body, match.start(), match.end()):
                continue
            pieces.append(body[cursor:match.start()])
            pieces.append(f"(uint32_t)camry_host_addr({name})")
            cursor = match.end()
        pieces.append(body[cursor:])
        body = "".join(pieces)
    return signature + body


def _rewrite_dat_scalars(code: str) -> str:
    """Resolve `_DAT_ff300050` as the word stored at that address."""
    widths = layout._access_widths()
    # A word `_DAT_` is Ghidra's untyped scalar. Signed compares (`b6`/`lt`)
    # read it as int32; storing those bits into a uint32 register keeps them.
    types = {1: "uint8_t", 2: "uint16_t", 4: "int32_t"}

    def replace(match: re.Match[str]) -> str:
        address = int(match.group(1), 16)
        bucket = widths.get(address)
        ctype = types.get(bucket or 0)
        if ctype is None:
            return match.group(0)
        return f"(*((volatile {ctype} *)camry_host_ptr(0x{address:x}u)))"

    return re.sub(r"\b_DAT_([0-9A-Fa-f]+)\b", replace, code)


def _symbols_by_addr() -> dict[int, dict]:
    global _SYMBOLS_BY_ADDR
    if _SYMBOLS_BY_ADDR is None:
        _SYMBOLS_BY_ADDR = {int(row["addr"], 16): row for row in tree.load_symbols()}
    return _SYMBOLS_BY_ADDR


def _tp_word_copy(entry: int) -> tuple[int, int] | None:
    """Bytes of a dword copy from tp+disp for a whole number of words.

    Ghidra renders the end address as a string literal. The copy is `movea`
    from r5, then `addi length`.
    """
    from tools.targets.camry.decomp.lifting.graph import load_image, walk_symbol

    row = _symbols_by_addr().get(entry)
    if row is None:
        return None
    fn = walk_symbol(load_image(), row)
    if fn is None:
        return None
    for index, inst in enumerate(fn.insts):
        match = re.fullmatch(r"camry_movea\((\d+), 5, (-?\d+)\);", inst.stmt or "")
        if match is None:
            continue
        base = int(match.group(1))
        disp = int(match.group(2))
        for follow in fn.insts[index + 1:index + 8]:
            added = re.fullmatch(r"camry_addi\((\d+), (\d+), (\d+)\);", follow.stmt or "")
            if added is None or int(added.group(2)) != base:
                continue
            length = int(added.group(3))
            if length <= 0 or length % 4 or length > 0x400:
                return None
            return (layout._RUNTIME_TP + disp) & 0xFFFFFFFF, length
    return None


def _copy_end_is_present(code: str, end: int) -> bool:
    """The recovered end address is already the pointer the copy compares."""
    for match in re.finditer(r"camry_tp\s*\+\s*(0x[0-9a-fA-F]+|\d+)u?", code):
        if ((layout._RUNTIME_TP + int(match.group(1), 0)) & 0xFFFFFFFF) == end:
            return True
    for match in re.finditer(r"camry_host_ptr\(\s*(0x[0-9a-fA-F]+)u?", code):
        if int(match.group(1), 0) == end:
            return True
    return False


def _rewrite_string_word_copies(code: str) -> str:
    """A tp-relative copy whose source or end Ghidra printed as a string.

    The end is sometimes the string in the compare. The source is sometimes
    `= ""` while the compare already uses `camry_host_ptr` of the end. Either
    form incorrectly walks a host literal. The copy must read the firmware bytes.
    """
    string_end = '(uintptr_t)("' in code
    empty_source = re.search(r'=\s*""\s*;', code) is not None
    if not string_end and not empty_source:
        return code
    name = syntax._c_signature(code).split("(", 1)[0].split()[-1].lstrip("*")
    entry = layout._function_entries().get(name)
    if entry is None:
        return code
    found = _tp_word_copy(entry)
    if found is None:
        return code
    start, length = found
    end = (start + length) & 0xFFFFFFFF
    if empty_source and (string_end or _copy_end_is_present(code, end)):
        code = re.sub(
            r'=\s*""(?=\s*;)',
            f"= (undefined *)camry_host_ptr(0x{start:x}u)",
            code,
            count=1,
        )
    if not string_end:
        return code
    return re.sub(
        r'\(uintptr_t\)\("(?:[^"\\]|\\.)*"\)',
        f"(uintptr_t)((undefined *)camry_host_ptr(0x{end:x}u))",
        code,
        count=1,
    )


def _rewrite_pointer_result(code: str) -> str:
    """A pointer function returns the address word in r10 as a host pointer.

    The function declaration supplies the signature. Ignore `/*` in a preceding
    block comment when determining the return type.
    """
    signature = syntax._c_signature(code)
    if not signature or not syntax._returns_pointer(signature):
        return code
    kind = expressions._kind_context(signature, code)

    def replace(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        if not expr or expr in {"0", "NULL"} or "camry_host_ptr" in expr or "camry_host_addr" in expr:
            return match.group(0)
        if kind(expr) != "integer":
            return match.group(0)
        return f"return ((void *)camry_host_ptr((uint32_t)({expr})));"

    return re.sub(r"return\s+([^;]+);", replace, code)


def _rewrite_ghidra_strings(code: str) -> str:
    """`s_text_00020800[index]` is the byte at that address plus the index.

    The hex suffix is the address Ghidra gave the string.
    """
    # These literals are truncated byte tables. Use byte-table loads. The exact
    # ld.bu bases are 622b0/6231a/6235e/62592, 62118/62158, 63700,
    # 7ba28, 3b988/3b99c, and b94e0 in this target.
    literal_bases = {
        "stage_and_send_five_halfword_acquisition_frame_62274": {'""': 0x31674},
        "reset_acquisition_channel_with_repeated_e0_commands_6230e": {'""': 0x31674, r'"\x02\n"': 0x31676},
        "copy_64_bytes_after_app_info_header_636f8": {'"APP INFO AREA   PVSDKS5A@"': 0x20800},
        "copy_acquisition_group0_samples": {'""': 0x30F2C},
        "copy_acquisition_group8_samples": {'""': 0x30F34},
        "decode_serial_acquisition_frame": {r'"\x02\n"': 0x31676},
        "sample_serial_acquisition_channel": {'""': 0x31674},
        "apply_thermal_offset_and_following": {'""': 0x21258},
        "qualify_control_profile_observation": {'"ddddd"': 0xAED78},
    }
    name = syntax._signature_name(syntax._c_signature(code))
    bases = literal_bases.get(name, {})
    spans: list[tuple[int, int, str]] = []
    index = syntax._opening_brace(code) + 1
    while index < len(code):
        if code[index] not in "'\"":
            index += 1
            continue
        end = c_text._skip_quoted(code, index)
        if end <= index:
            index += 1
            continue
        literal = code[index:end]
        after = c_text._skip_space(code, end)
        address = bases.get(literal)
        if name == "cantp_capture_initial_flow_parameters" and code[index] == '"':
            address = 0x22C84
        if address is not None and after < len(code) and code[after] == "[":
            spans.append((
                index, end, f"((volatile uint8_t *)camry_host_ptr(0x{address:x}u))",
            ))
        index = end
    code = syntax._apply_spans(code, spans)

    def replace(match: re.Match[str]) -> str:
        address = int(match.group(1), 16)
        return f"((volatile uint8_t *)camry_host_ptr(0x{address:x}u))"

    return re.sub(r"\bs_[A-Za-z0-9_]*_([0-9A-Fa-f]{4,})\b", replace, code)


def _rewrite_terminal_labels(code: str) -> str:
    """A label as the last statement of a block needs an empty statement after it."""
    return re.sub(
        r"([A-Za-z_][A-Za-z0-9_]*\s*:)(\s*)(?=\})",
        r"\1;\2",
        code,
    )
_SYMBOLS_BY_ADDR: dict[int, dict] | None = None
