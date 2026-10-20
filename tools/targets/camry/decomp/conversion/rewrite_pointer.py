"""Host-C pointer, call, and integer conversion passes."""
from __future__ import annotations

import re

from tools.targets.camry.decomp import c_text, layout, syntax, tree
from tools.targets.camry.decomp.conversion import expressions



def _rewrite_indexed(code: str) -> str:
    pieces: list[str] = []
    cursor = 0
    pattern = re.compile(r"\(&(DAT|UNK|LAB)_([0-9A-Fa-f]+)\)\s*\[")
    widths = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        try:
            end = c_text._match_delimiter(code, match.end() - 1, "[]", quoted=False)
        except ValueError:
            continue
        index = _rewrite_indexed(code[match.end():end])
        addr = int(match.group(2), 16)
        scale = layout._access_widths().get(addr, 1)
        if scale not in widths:
            scale = 1
        pieces.append(code[cursor:match.start()])
        pieces.append(
            f"(*((volatile {widths[scale]} *)camry_host_ptr((uint32_t)"
            f"(0x{addr:x}u + (uint32_t)({index}) * {scale}u))))"
        )
        cursor = end + 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _symbol_address(name: str) -> int | None:
    found = layout._absolute_names().get(name)
    if found is not None:
        return found
    match = re.fullmatch(r"(?:DAT|UNK)_([0-9A-Fa-f]+)", name)
    if match:
        return int(match.group(1), 16)
    return None


def _scaled_address(base: int, index: str, stride: int, offset: int) -> str:
    expr = f"0x{base:x}u + (uint32_t)({index}) * {stride}u"
    if offset:
        expr += f" + {offset}u"
    return expr


def _trailing_field(code: str, end: int) -> tuple[str | None, int]:
    nxt = c_text._skip_space(code, end + 1)
    match = re.match(r"\.\s*([A-Za-z_][A-Za-z0-9_]*)", code[nxt:])
    if match is None:
        return None, end
    return match.group(1), nxt + match.end()


def _symbol_element(name: str) -> tuple[str, int] | None:
    """Scalar width of a data symbol or machine register. Structs are separate."""
    object_layout = layout._data_layouts().get(name)
    if object_layout is not None:
        _addr, ctype, _array = object_layout
        if ctype in layout._struct_rows():
            return None
        width = layout._SCALAR_WIDTHS.get(ctype)
        if width is None:
            return None
        return layout._WIDTH_CTYPES[width], width
    row = tree._machine_registers().get(name)
    if row is None:
        return None
    width = int(row.get("size") or 0)
    ctype = layout._WIDTH_CTYPES.get(width)
    if ctype is None:
        return None
    return ctype, width


def _rewrite_device_pointer_add(code: str) -> str:
    """`&label + index` on a peripheral struct advances by the struct size."""
    pieces: list[str] = []
    cursor = 0
    pattern = re.compile(r"&([A-Za-z_][A-Za-z0-9_]*)\s*\+")
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        address = _symbol_address(match.group(1))
        spec = layout._DEVICE_TYPES.get(address) if address is not None else None
        if spec is None:
            continue
        expr_end = syntax._scan_side(code, match.end(), 1, ",;)")
        expr = code[match.end():expr_end].strip()
        if not expr:
            continue
        ctype, stride = spec
        pieces.append(code[cursor:match.start()])
        pieces.append(
            f"(({ctype} *)camry_host_ptr((uint32_t)"
            f"(0x{address:x}u + (uint32_t)({expr}) * {stride}u)))"
        )
        cursor = expr_end
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_symbol_indexes(code: str) -> str:
    """`(&symbol)[index]` keeps the symbol's element stride.

    A struct-typed object is an array of that struct. A peripheral label
    indexed through a recovered device field uses that field's byte offset.
    Replacing `&symbol` with a bare integer drops both.
    """
    pieces: list[str] = []
    cursor = 0
    pattern = re.compile(r"\(&([A-Za-z_][A-Za-z0-9_]*)\)\s*\[")
    structs = layout._struct_rows()
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        name = match.group(1)
        try:
            end = c_text._match_delimiter(code, match.end() - 1, "[]", quoted=False)
        except ValueError:
            continue
        index = _rewrite_symbol_indexes(code[match.end():end])
        address = _symbol_address(name)
        if address is None:
            continue
        field, field_end = _trailing_field(code, end)
        device = layout._DEVICE_FIELDS.get(address)
        bits = layout._DEVICE_BITS.get(address)
        replacement = None
        consumed = end + 1
        if device is not None and field is not None and field in device[1]:
            offset, ctype = device[1][field]
            replacement = syntax._volatile_at(
                _scaled_address(address, index, device[0], offset), ctype,
            )
            consumed = field_end
        elif bits is not None and field is not None and field in bits[1]:
            word = syntax._volatile_at(_scaled_address(address, index, bits[0], 0), "uint32_t")
            bit = bits[1][field]
            replacement = f"((({word}) >> {bit}) & 1u)"
            consumed = field_end
        elif device is not None and field is not None:
            continue
        elif bits is not None and field is not None:
            continue
        else:
            object_layout = layout._data_layouts().get(name)
            if object_layout is not None and object_layout[1] in structs:
                replacement = (
                    f"((volatile {object_layout[1]} *)camry_host_ptr(0x{address:x}u))[{index}]"
                )
            else:
                element = _symbol_element(name)
                if element is None or field is not None:
                    continue
                ctype, width = element
                replacement = syntax._volatile_at(
                    _scaled_address(address, index, width, 0), ctype,
                )
        pieces.append(code[cursor:match.start()])
        pieces.append(replacement)
        cursor = consumed
    pieces.append(code[cursor:])
    return "".join(pieces)


_ADDR_TOKEN = re.compile(r"&(?:LAB|DAT|UNK)_(?:[A-Za-z_][A-Za-z0-9_]*__)?([0-9A-Fa-f]+)\b")


def _address_compared_as_integer(code: str, match: re.Match[str], pointers: set[str]) -> bool:
    _op, op_at = syntax._compare_after(code, match.end())
    if _op is not None:
        end = syntax._expr_end_bound(code, op_at + len(_op))
        operand = code[op_at + len(_op):end].strip()
        if operand and not syntax._is_pointer_expr(operand, pointers):
            return True
    _op, op_at = syntax._compare_before(code, match.start())
    if _op is not None:
        operand = syntax._expr_before(code, op_at).strip()
        if operand and not syntax._is_pointer_expr(operand, pointers):
            return True
    return False


def _rewrite_host_pointer_limits(code: str) -> str:
    """`camry_host_ptr(limit) < pointer` compares firmware addresses.

    The bytes compare the address word with the immediate. Host pointer
    order is not that numeric order.
    """
    return re.sub(
        r"\(uintptr_t\)\(\(\(undefined \*\)camry_host_ptr\(0x([0-9a-fA-F]+)u\)\)\)"
        r"<\(uintptr_t\)\(([^()]+)\)",
        lambda match: f"0x{match.group(1)}u < camry_host_addr({match.group(2)})",
        code,
    )


def _rewrite_address_compares(code: str, pointers: set[str]) -> str:
    code = _rewrite_host_pointer_limits(code)
    pieces: list[str] = []
    cursor = 0
    for match in _ADDR_TOKEN.finditer(code):
        if match.start() < cursor:
            continue
        try:
            integer = _address_compared_as_integer(code, match, pointers)
        except ValueError:
            integer = False
        if not integer:
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(f"0x{int(match.group(1), 16):x}u")
        cursor = match.end()
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_addresses(code: str, pointers: set[str]) -> str:
    def integer_cast(match: re.Match[str]) -> str:
        return f"({match.group(1)})0x{int(match.group(2), 16):x}u"

    code = _rewrite_address_compares(code, pointers)
    code = re.sub(
        r"\((unsigned int|int|uint|undefined4|ulong|long)\)\s*" + _ADDR_TOKEN.pattern,
        integer_cast,
        code,
    )
    return _ADDR_TOKEN.sub(
        lambda match: f"((undefined *)camry_host_ptr(0x{int(match.group(1), 16):x}u))",
        code,
    )


def _rewrite_pointer_arguments(code: str, param_types: dict[str, list[str]]) -> str:
    """Pass a firmware integer to a pointer parameter as a host pointer."""
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    signature = syntax._c_signature(code)
    kind = expressions._kind_context(signature, code)
    calls = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\)\s*)?\(")

    def rewrite(text: str) -> str:
        pieces: list[str] = []
        cursor = 0
        for match in calls.finditer(text):
            if match.start() < cursor or match.group(1) in syntax._SKIP_CALLS:
                continue
            try:
                close = c_text._match_delimiter(text, match.end() - 1)
            except ValueError:
                continue
            inner = rewrite(text[match.end():close])
            types = param_types.get(match.group(1))
            if types is not None:
                args = c_text._split_args(inner)
                if len(args) == 1 and not args[0].strip():
                    args = []
                extra = [arg for arg in args[len(types):] if arg.strip()]
                args = args[:len(types)]
                rewritten_args: list[str] = []
                wrapped = False
                for index, arg in enumerate(args):
                    # `(uchar *)*slot` passed to a uint32 parameter is the loaded
                    # address word. A host pointer of that cast is a different value.
                    operand = syntax._pointer_cast_operand(arg)
                    if (
                        "*" not in types[index]
                        and operand is not None
                        and kind(operand) == "integer"
                    ):
                        wrapped = True
                        rewritten_args.append(f"(uint32_t)({operand})")
                        continue
                    if "*" in types[index] and kind(arg) == "integer":
                        wrapped = True
                        rewritten_args.append(
                            f"(({types[index]})camry_host_ptr((uint32_t)({arg.strip()})))"
                        )
                        continue
                    if "*" not in types[index] and kind(arg) == "pointer":
                        wrapped = True
                        rewritten_args.append(f"camry_host_addr({arg.strip()})")
                        continue
                    rewritten_args.append(arg)
                if extra:
                    # The callee signature does not read these. Keep their side effects.
                    discarded = ", ".join(f"(void)({arg.strip()})" for arg in extra)
                    kept = ", ".join(rewritten_args)
                    pieces.append(text[cursor:match.start()])
                    pieces.append(f"({discarded}, {match.group(1)}({kept}))")
                    cursor = close + 1
                    continue
                if wrapped:
                    inner = ", ".join(rewritten_args)
            pieces.append(text[cursor:match.end()])
            pieces.append(inner)
            cursor = close
        pieces.append(text[cursor:])
        return "".join(pieces)

    return code[:brace] + rewrite(code[brace:])


def _rewrite_pointer_to_int(code: str, pointers: set[str]) -> str:
    code = _rewrite_function_values(code)
    kind = expressions._kind_context(syntax._c_signature(code), code, pointers)
    pieces: list[str] = []
    cursor = 0
    for match in syntax._INT_CAST.finditer(code):
        if match.start() < cursor:
            continue
        begin = c_text._skip_space(code, match.end())
        if begin >= len(code) or code[begin] not in "(ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_":
            continue
        end = syntax._operand_end(code, begin)
        if end == begin:
            continue
        # `(uint)pdu->length` casts the field. The base alone is not the operand.
        while True:
            arrow = c_text._skip_space(code, end)
            if code.startswith("->", arrow):
                step = 2
            elif arrow < len(code) and code[arrow] == ".":
                step = 1
            else:
                break
            field_at = c_text._skip_space(code, arrow + step)
            field = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[field_at:])
            if field is None:
                break
            end = field_at + field.end()
        if end < len(code) and code[end] == "[":
            continue
        operand = code[begin:end]
        if kind(operand) != "pointer":
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(f"({match.group(1)})camry_host_addr({operand})")
        cursor = end
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_explicit_fields(code: str) -> str:
    """`&label.field_0xN` is the byte at that label plus N, not a C member."""
    def replace(match: re.Match[str]) -> str:
        address = _symbol_address(match.group(1))
        if address is None:
            return match.group(0)
        target = (address + int(match.group(2), 16)) & 0xFFFFFFFF
        return f"(0x{target:x}u)"

    return re.sub(
        r"&([A-Za-z_][A-Za-z0-9_]*)\.field_0x([0-9A-Fa-f]+)",
        replace,
        code,
    )


def _rewrite_pointer_tables(code: str) -> str:
    """`(&PTR_...)[index]` loads a firmware pointer from a 4-byte slot.

    The disassembly scales the decompiler's index by 4 (`shl 2`, or a multiply
    that already includes that 4). The value in the slot is the pointee address.
    """
    pieces: list[str] = []
    cursor = 0
    pattern = re.compile(r"\(&(PTR_[A-Za-z0-9_]*_([0-9A-Fa-f]+))\)\s*\[")
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        try:
            end = c_text._match_delimiter(code, match.end() - 1, "[]", quoted=False)
        except ValueError:
            continue
        index = _rewrite_pointer_tables(code[match.end():end])
        address = int(match.group(2), 16)
        pieces.append(code[cursor:match.start()])
        pieces.append(
            "(*((volatile uint32_t *)camry_host_ptr((uint32_t)"
            f"(0x{address:x}u + (uint32_t)({index}) * 4u))))"
        )
        cursor = end + 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_int_to_pointer(
    code: str, pointers: set[str], *, nested_only: bool = False, known_only: bool = False,
) -> str:
    # `*(int *)SLOT` is the word at that firmware address. Folding it first
    # keeps an outer `(char *)(word + index)` from hiding the load.
    if not nested_only:
        code = _rewrite_slot_word_derefs(code)
    kind = expressions._kind_context(syntax._c_signature(code), code, pointers)
    pieces: list[str] = []
    cursor = 0
    search = 0
    while True:
        star = code.find("*)", search)
        if star < 0:
            pieces.append(code[cursor:])
            break
        type_end = star
        while type_end > 0 and code[type_end - 1] in " \t\n":
            type_end -= 1
        type_start = type_end
        while type_start > 0 and (code[type_start - 1].isalnum() or code[type_start - 1] in "_* \t"):
            type_start -= 1
        if type_start <= 0 or code[type_start - 1] != "(":
            search = star + 2
            continue
        type_name = " ".join(code[type_start:type_end].split())
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ *]*", type_name):
            search = star + 2
            continue
        after = c_text._skip_space(code, star + 2)
        if type_name == "code":
            # _rewrite_code_loads marks firmware function words with uintptr_t.
            # They go to camry_indirect, never through the data-memory mapper.
            if code.startswith("(uintptr_t)", after):
                search = star + 2
                continue
            mapped = re.match(r"camry_host_ptr\s*\(", code[after:])
            if mapped:
                opening = after + mapped.end() - 1
                closing = c_text._match_delimiter(code, opening)
                word = code[opening + 1:closing].strip()
                if re.match(r"\(uint32_t\)\s*\(\s*\(uintptr_t\)", word):
                    # Repair retained output emitted before this distinction.
                    pieces.append(code[cursor:type_start - 1])
                    pieces.append(f"((code *)(uintptr_t)({word}))")
                    cursor = closing + 1
                    search = cursor
                    continue
        if after >= len(code):
            pieces.append(code[cursor:])
            break
        if code[after] == "(":
            end = c_text._match_delimiter(code, after) + 1
            inner = code[after + 1:end - 1]
            if syntax._is_type_cast(inner):
                operand_end = syntax._unary_operand_end(code, end)
                if operand_end is None or operand_end <= end:
                    search = star + 2
                    continue
                expr = code[after:operand_end].strip()
                end = operand_end
            else:
                expr = inner
        elif code[after].isalpha() or code[after] == "_":
            end = syntax._operand_end(code, after)
            # A pointer-returning call already returns a host pointer. A scalar
            # return cast to a data pointer instead holds a firmware address
            # (for example 778D8 returns the NVM trailer scratch address).
            if c_text._skip_space(code, end) < len(code) and code[c_text._skip_space(code, end)] == "(":
                callee = code[after:end]
                if callee not in layout._function_entries() or callee in layout._pointer_return_names():
                    search = star + 2
                    continue
            end = syntax._postfix_end(code, end)
            expr = code[after:end]
        elif code[after] == "*":
            end = syntax._unary_operand_end(code, after)
            if end is None:
                search = star + 2
                continue
            expr = code[after:end]
            if kind(expr) != "integer":
                search = star + 2
                continue
        elif code[after] == "0":
            number = re.match(r"0x[0-9A-Fa-f]+|0", code[after:])
            if number is None:
                search = star + 2
                continue
            expr = number.group(0)
            end = after + number.end()
        else:
            search = star + 2
            continue
        if nested_only:
            loaded = expr.strip()
            while syntax._fully_wrapped(loaded):
                loaded = loaded[1:-1].strip()
            if not loaded.startswith("*") or kind(expr) != "integer":
                search = star + 2
                continue
        if kind(expr) == "pointer" or syntax._is_null_expr(expr):
            search = star + 2
            continue
        if known_only and kind(expr) != "integer":
            search = star + 2
            continue
        open_paren = type_start - 1
        deref_at = open_paren - 1
        while deref_at >= cursor and code[deref_at] in " \t":
            deref_at -= 1
        deref = deref_at >= cursor and code[deref_at] == "*" and (
            deref_at == open_paren - 1 or code[deref_at + 1:open_paren].strip() == ""
        )
        # A newline between * and ( is still a dereference. A space is multiplication.
        if deref and deref_at != open_paren - 1 and "\n" not in code[deref_at + 1:open_paren]:
            deref = False
        replace_at = deref_at if deref else open_paren
        if replace_at < cursor:
            search = star + 2
            continue
        # `(undefined *)0xffffffff` beside a signed divide is the divisor word
        # compared with -1. A host pointer of that constant is not the cmp.
        # `(undefined *)(0xfec00000 - length)` is the same: the cmp is on the
        # address bits, and a host pointer of the sum is a different value.
        literal = None if deref else syntax._integer_constant_bits(expr)
        if not deref and syntax._is_compare_operand(code, open_paren, end):
            pieces.append(code[cursor:open_paren])
            pieces.append(literal if literal is not None else f"(uint32_t)({expr})")
            cursor = end
            search = end
            continue
        pieces.append(code[cursor:replace_at])
        cast = f"({type_name} *)camry_host_ptr((uint32_t)({expr}))"
        pieces.append(f"(*({cast}))" if deref else f"({cast})")
        cursor = end
        search = end
    return "".join(pieces)


def _rewrite_pointer_calls(code: str, pointers: set[str]) -> str:
    returns = layout._pointer_return_names()
    pieces: list[str] = []
    cursor = 0
    pattern = re.compile(
        r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\("
    )
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        lhs, callee = match.group(1), match.group(2)
        if lhs in pointers or callee not in returns:
            continue
        equals = code.find("=", match.start())
        if equals > 0 and code[equals - 1] in "=!<>":
            continue
        try:
            close = c_text._match_delimiter(code, match.end() - 1)
        except ValueError:
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(f"{lhs} = camry_host_addr({callee}{code[match.end() - 1:close + 1]})")
        cursor = close + 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _narrow_lvalues(code: str) -> tuple[dict[str, int], dict[str, int]]:
    """Unsigned 8- and 16-bit lvalues. Wider unsigned values do not promote."""
    scalars: dict[str, int] = {}
    elements = {
        name: width
        for name, width in syntax._pointer_element_widths(code).items()
        if width in (1, 2)
    }
    local = re.compile(
        r"\b(undefined1|undefined2|undefined|byte|uchar|ushort|char|code|bool|uint8_t|uint16_t)\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*(\[[^\]]*\])?\s*;"
    )
    for match in local.finditer(code):
        width = 2 if match.group(1) in {"undefined2", "ushort", "uint16_t"} else 1
        (elements if match.group(3) else scalars)[match.group(2)] = width
    for name, (_addr, ctype, is_array) in layout._data_layouts().items():
        width = {"uint8_t": 1, "uint16_t": 2}.get(ctype)
        if width is None:
            continue
        if is_array:
            elements[name] = width
        else:
            scalars[name] = width
    return scalars, elements


def _narrow_width(text: str, scalars: dict[str, int], elements: dict[str, int]) -> int | None:
    if re.match(r"^\(\s*int(?:8|16)_t\s*\)", text):
        return None
    if text in scalars:
        return scalars[text]
    match = re.fullmatch(r"(?:DAT|UNK)_([0-9A-Fa-f]+)", text)
    if match:
        width = layout._access_widths().get(int(match.group(1), 16))
        return width if width in (1, 2) else None
    match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[(.*)\]", text, flags=re.S)
    if match and elements.get(match.group(1)) in (1, 2):
        return elements[match.group(1)]
    return syntax._deref_width(text)


def _cast_unsigned_narrow(
    raw: str, scalars: dict[str, int], elements: dict[str, int], constant: int,
) -> str | None:
    text = raw.strip()
    if syntax._negative_constant(text) is not None:
        return None
    width = _narrow_width(text, scalars, elements)
    if width not in (1, 2):
        return None
    if constant < (-128 if width == 1 else -32768):
        return None
    prefix = raw[:len(raw) - len(raw.lstrip())]
    suffix = raw[len(raw.rstrip()):]
    cast = "int8_t" if width == 1 else "int16_t"
    return f"{prefix}(({cast}){text}){suffix}"


def _rewrite_signed_byte_compares(code: str) -> str:
    """Ghidra spells a narrow unsigned compare against 0xAA as `!= -0x56`.

    A uint8 or uint16 lvalue promotes to a non-negative int, so a negative
    constant compare is tautological. Casting to the signed width keeps the
    bit-pattern test.
    """
    scalars, elements = _narrow_lvalues(code)
    pieces: list[str] = []
    cursor = 0
    index = 0
    while index < len(code):
        if code.startswith(("<<", ">>"), index):
            index += 2
            continue
        if code[index] == ">" and index > 0 and code[index - 1] == "-":
            index += 1
            continue
        op = next(
            (item for item in ("<=", ">=", "==", "!=", "<", ">") if code.startswith(item, index)),
            None,
        )
        if op is None:
            index += 1
            continue
        raw_left = syntax._expr_before(code, index)
        left_at = index - len(raw_left)
        if left_at < cursor:
            index += len(op)
            continue
        right_end = syntax._expr_end_bound(code, index + len(op))
        raw_right = code[index + len(op):right_end]
        left_constant = syntax._negative_constant(raw_left.strip())
        right_constant = syntax._negative_constant(raw_right.strip())
        if right_constant is not None:
            cast = _cast_unsigned_narrow(raw_left, scalars, elements, right_constant)
            if cast is not None:
                pieces.append(code[cursor:left_at])
                pieces.append(cast)
                cursor = index
                index += len(op)
                continue
        if left_constant is not None:
            cast = _cast_unsigned_narrow(raw_right, scalars, elements, left_constant)
            if cast is not None:
                pieces.append(code[cursor:index + len(op)])
                pieces.append(cast)
                cursor = right_end
                index = right_end
                continue
        index += len(op)
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_function_values(code: str) -> str:
    """A function designator used as data is its firmware entry address.

    `movea 19852, gp` is `gp + entry`, which Ghidra spells as
    `function_name + (int)pointer`.
    """
    entries = layout._function_entries()

    def replace(match: re.Match[str]) -> str:
        address = entries.get(match.group(1))
        if address is None:
            return match.group(0)
        return f"0x{address:x}u"

    code = re.sub(r"\bcamry_host_addr\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)", replace, code)
    code = re.sub(
        r"((?<![=!<>])=(?!=)\s*)([A-Za-z_][A-Za-z0-9_]*)(?=\s*;)",
        lambda match: (
            match.group(1) + f"0x{entries[match.group(2)]:x}u"
            if match.group(2) in entries else match.group(0)
        ),
        code,
    )
    return re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\b(?=\s*[+\-][^=+\-])", replace, code)


def _rewrite_function_indexes(code: str) -> str:
    entries = layout._function_entries()
    pieces: list[str] = []
    cursor = 0
    pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\[")
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        addr = entries.get(match.group(1))
        if addr is None:
            continue
        try:
            end = c_text._match_delimiter(code, match.end() - 1, "[]", quoted=False)
        except ValueError:
            continue
        index = code[match.end():end]
        pieces.append(code[cursor:match.start()])
        pieces.append(
            "(*((volatile uint8_t *)camry_host_ptr((uint32_t)"
            f"(0x{addr:x}u + (uint32_t)({index})))))"
        )
        cursor = end + 1
    pieces.append(code[cursor:])
    return "".join(pieces)


_OVERLAY = re.compile(
    r"\b(?P<head>[A-Za-z_][A-Za-z0-9_]*(?:\s*\[[^\[\]]*\])?(?:\s*\.\s*[A-Za-z_][A-Za-z0-9_]*)*)"
    r"\._(?P<off>\d+)_(?P<size>\d+)_"
)
_BIT_WIDTHS = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}
_LOCAL_SIZES = {
    "undefined1": 1, "byte": 1, "uchar": 1, "char": 1, "code": 1, "bool": 1,
    "undefined": 1,
    "undefined2": 2, "ushort": 2, "short": 2,
    "undefined4": 4, "uint": 4, "int": 4, "ulong": 4,
    "undefined8": 8, "ulonglong": 8, "longlong": 8,
}


def _local_sizes(code: str) -> dict[str, int]:
    sizes: dict[str, int] = {}
    pattern = re.compile(
        r"\b(undefined[1248]|undefined|byte|uchar|ushort|short|uint|ulong|ulonglong|"
        r"longlong|int|char|code|bool)\s+([A-Za-z_][A-Za-z0-9_]*)\s*;"
    )
    for match in pattern.finditer(code):
        width = _LOCAL_SIZES.get(match.group(1))
        if width is not None:
            sizes[match.group(2)] = width
    return sizes


def _split_overlay_head(head: str) -> tuple[str, str | None, list[str]] | None:
    match = re.fullmatch(
        r"([A-Za-z_][A-Za-z0-9_]*)(?:\s*\[([^\[\]]*)\])?\s*"
        r"((?:\.\s*[A-Za-z_][A-Za-z0-9_]*)*)",
        head,
    )
    if match is None:
        return None
    fields = re.findall(r"\.\s*([A-Za-z_][A-Za-z0-9_]*)", match.group(3))
    return match.group(1), match.group(2), fields


def _member_offset(struct_name: str, fields: list[str]) -> int | None:
    rows = layout._struct_rows()
    current = struct_name
    offset = 0
    for index, field_name in enumerate(fields):
        row = rows.get(current)
        if row is None:
            return None
        found = next((field for field in row["fields"] if field["name"] == field_name), None)
        if found is None:
            return None
        offset += int(found["offset"])
        if index + 1 == len(fields):
            return offset
        base, stars, _array = layout._ghidra_base(found["type"])
        if stars or base not in rows:
            return None
        current = base
    return None


def _bitfield_assignment_rhs(code: str, end: int) -> tuple[str, int] | None:
    nxt = c_text._skip_space(code, end)
    if nxt >= len(code) or code[nxt] != "=" or code.startswith("==", nxt):
        return None
    rhs_at = nxt + 1
    semi = syntax._scan_side(code, rhs_at, 1, ";")
    if semi >= len(code) or code[semi] != ";":
        return None
    return code[rhs_at:semi].strip(), semi


def _rewrite_bitfields(code: str) -> str:
    """Ghidra `name._offset_size_` is a byte overlay, not a struct field."""
    locals = _local_sizes(code)
    var_structs = layout._struct_var_types(code)
    pieces: list[str] = []
    cursor = 0
    for match in _OVERLAY.finditer(code):
        if match.start() < cursor:
            continue
        parsed = _split_overlay_head(match.group("head"))
        if parsed is None:
            continue
        name, index, fields = parsed
        offset = int(match.group("off"))
        size = int(match.group("size"))
        ctype = _BIT_WIDTHS.get(size)
        replacement = None
        consumed = match.end()
        if fields:
            struct = var_structs.get(name)
            member = _member_offset(struct, fields) if struct else None
            stride = layout._struct_rows().get(struct, {}).get("size") if struct else None
            if ctype is None or member is None or stride is None:
                continue
            total = member + offset
            address = _symbol_address(name)
            if address is not None:
                if index is None:
                    target = (address + total) & 0xFFFFFFFF
                    expr = f"0x{target:x}u"
                else:
                    expr = _scaled_address(address, index, int(stride), total)
                replacement = syntax._volatile_at(expr, ctype)
            else:
                disp = f"(uint8_t *)&{name} + {total}u"
                if index is not None:
                    disp = (
                        f"(uint8_t *)&{name} + (uint32_t)({index}) * {int(stride)}u"
                        f" + {total}u"
                    )
                replacement = f"(*(({ctype} *)({disp})))"
        else:
            address = _symbol_address(name)
            if ctype is not None and address is not None:
                target = (address + offset) & 0xFFFFFFFF
                replacement = f"(*((volatile {ctype} *)camry_host_ptr(0x{target:x}u)))"
            elif ctype is not None and locals.get(name, -1) >= offset + size:
                replacement = f"(*(({ctype} *)((uint8_t *)&{name} + {offset}u)))"
            elif (
                size == 3
                and index is None
                and 0 < locals.get(name, -1) >= offset + size
                and locals[name] <= 8
            ):
                mask = (1 << (size * 8)) - 1
                shift = offset * 8
                assigned = _bitfield_assignment_rhs(code, match.end())
                if assigned is not None:
                    rhs, consumed = assigned
                    kept = (
                        f"({name} & ~{mask:#x}u)"
                        if shift == 0
                        else f"({name} & ~({mask:#x}u << {shift}))"
                    )
                    stored = (
                        f"((uint32_t)({rhs}) & {mask:#x}u)"
                        if shift == 0
                        else f"(((uint32_t)({rhs}) & {mask:#x}u) << {shift})"
                    )
                    replacement = f"{name} = {kept} | {stored}"
                else:
                    replacement = (
                        f"((uint32_t)({name}) & {mask:#x}u)"
                        if shift == 0
                        else f"(((uint32_t)({name}) >> {shift}) & {mask:#x}u)"
                    )
        if replacement is None:
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(replacement)
        cursor = consumed
    pieces.append(code[cursor:])
    return "".join(pieces)


_BYTE_POINTER = r"(?:undefined1|undefined|byte|uchar|char|code|bool)"


def _firmware_base_locals(code: str) -> dict[str, int]:
    """Byte pointers assigned only from one `&LAB/DAT/UNK` hold that firmware address.

    `camry_host_ptr` of the base aborts when the scenario maps `base+disp` and
    not the base. Later reads and stores use the summed address.
    """
    declared = {
        match.group(1)
        for match in re.finditer(
            rf"^\s*{_BYTE_POINTER}\s+\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*;\s*$",
            code,
            flags=re.M,
        )
    }
    bases: dict[str, int] = {}
    for name in declared:
        addresses: list[int] = []
        bare = True
        for match in re.finditer(
            rf"(?<![=<>!])\b{name}\s*=(?!=)\s*([^;]*);",
            code,
        ):
            token = re.fullmatch(
                r"&(?:LAB|DAT|UNK)_([0-9A-Fa-f]+)",
                match.group(1).strip(),
            )
            if token is None:
                bare = False
                break
            addresses.append(int(token.group(1), 16))
        if bare and addresses and len(set(addresses)) == 1:
            bases[name] = addresses[0]
    return bases


def _rewrite_base_subscripts(code: str, names: set[str]) -> str:
    if not names:
        return code
    pattern = re.compile(
        r"\b(" + "|".join(sorted(names, key=len, reverse=True)) + r")\s*\["
    )
    pieces: list[str] = []
    cursor = 0
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        try:
            end = c_text._match_delimiter(code, match.end() - 1, "[]", quoted=False)
        except ValueError:
            continue
        index = _rewrite_base_subscripts(code[match.end():end], names)
        pieces.append(code[cursor:match.start()])
        pieces.append(
            "(*((volatile uint8_t *)camry_host_ptr((uint32_t)("
            f"{match.group(1)} + (uint32_t)({index})))))"
        )
        cursor = end + 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_base_address_sums(code: str, names: set[str]) -> str:
    if not names:
        return code
    name_alt = "|".join(sorted(names, key=len, reverse=True))
    pattern = re.compile(
        rf"&(?:LAB|DAT|UNK)_([0-9A-Fa-f]+)\s*\+\s*(\(int\))?\s*\b({name_alt})\b"
    )

    def replace(match: re.Match[str]) -> str:
        address = int(match.group(1), 16)
        cast = match.group(2) or ""
        name = match.group(3)
        return f"(0x{address:x}u + (uint32_t)({cast}{name}))"

    return pattern.sub(replace, code)


def _top_level_address(expr: str, names: set[str]) -> bool:
    """True when the expression is a firmware base or base+/-offset, not a compare."""
    text = expr.strip()
    if "camry_host_ptr" in text or not text:
        return False
    while text.startswith("(") and text.endswith(")"):
        try:
            if c_text._match_delimiter(text, 0) != len(text) - 1:
                break
        except ValueError:
            break
        text = text[1:-1].strip()
    if any(re.fullmatch(name, text) for name in names):
        return True
    depth = 0
    adds = False
    other = False
    for index, char in enumerate(text):
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif depth != 0 or index == 0:
            continue
        elif char in "+-" and text[index - 1] not in "+-<>(":
            adds = True
        elif char in "<>!&|=?":
            other = True
    if other or not adds:
        return False
    return any(re.search(rf"\b{name}\b", text) for name in names)


def _wrap_base_pointer_uses(code: str, names: set[str]) -> str:
    """A uint32 firmware base passed or stored as a pointer is that address."""
    if not names:
        return code
    pointers = {
        match.group(1)
        for match in re.finditer(
            r"^\s*[A-Za-z_][A-Za-z0-9_ \t]*\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*;\s*$",
            code,
            flags=re.M,
        )
    } - names

    def wrap(expr: str) -> str:
        return f"((undefined *)camry_host_ptr((uint32_t)({expr.strip()})))"

    def assign(match: re.Match[str]) -> str:
        lhs, rhs = match.group(1), match.group(2)
        if lhs not in pointers or not _top_level_address(rhs, names):
            return match.group(0)
        return f"{lhs} = {wrap(rhs)};"

    code = re.sub(
        r"(?<![=<>!])\b([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*([^;]*);",
        assign,
        code,
    )

    def wrap_calls(text: str) -> str:
        pieces: list[str] = []
        cursor = 0
        for match in syntax._CALL.finditer(text):
            if match.start() < cursor or match.group(1) in syntax._SKIP_CALLS:
                continue
            try:
                close = c_text._match_delimiter(text, match.end() - 1)
            except ValueError:
                continue
            inner = wrap_calls(text[match.end():close])
            args = c_text._split_args(inner)
            if any(_top_level_address(arg, names) for arg in args):
                inner = ", ".join(
                    wrap(arg) if _top_level_address(arg, names) else arg for arg in args
                )
            pieces.append(text[cursor:match.end()])
            pieces.append(inner)
            cursor = close
        pieces.append(text[cursor:])
        return "".join(pieces)

    return wrap_calls(code)


def _rewrite_firmware_bases(code: str) -> str:
    bases = _firmware_base_locals(code)
    if not bases:
        return code
    for name, address in bases.items():
        code = re.sub(
            rf"^(\s*){_BYTE_POINTER}\s+\*\s*{name}\s*;\s*$",
            rf"\1uint32_t {name};",
            code,
            count=1,
            flags=re.M,
        )
        code = re.sub(
            rf"(?<![=<>!])\b{name}\s*=\s*&(?:LAB|DAT|UNK)_[0-9A-Fa-f]+\s*;",
            f"{name} = 0x{address:x}u;",
            code,
        )
    names = set(bases)
    code = _rewrite_base_subscripts(code, names)
    code = _rewrite_base_address_sums(code, names)
    return _wrap_base_pointer_uses(code, names)


def _function_address(operand: str) -> str:
    """The address expression inside a Ghidra `*(code *)address` call."""
    text = operand.strip()
    while syntax._fully_wrapped(text):
        inner = text[1:-1].strip()
        if syntax._is_pointer_type(inner) or syntax._is_int_type(inner):
            break
        text = inner
    match = re.match(r"^\(\s*(?:(?:const|volatile)\s+)*code\s*\*\s*\)\s*", text)
    if match:
        return text[match.end():].strip()
    return text


def _rewrite_indirect_calls(code: str) -> str:
    """A call through `code *` is a call through a function pointer."""
    pieces: list[str] = []
    index = 0
    while index < len(code):
        if code[index] != "(":
            pieces.append(code[index])
            index += 1
            continue
        star = c_text._skip_space(code, index + 1)
        if star >= len(code) or code[star] != "*":
            pieces.append(code[index])
            index += 1
            continue
        try:
            close = c_text._match_delimiter(code, index)
        except ValueError:
            pieces.append(code[index])
            index += 1
            continue
        call = c_text._skip_space(code, close + 1)
        replace_at = index
        # `*(code *)addr` is rewritten to `(*((code *)camry_host_ptr(addr)))` before
        # this pass, leaving the call parentheses one level further out.
        if call >= len(code) or code[call] != "(":
            if (
                index > 0
                and code[index - 1] == "("
                and close + 1 < len(code)
                and code[close + 1] == ")"
                and "code" in code[star + 1:close]
            ):
                call = c_text._skip_space(code, close + 2)
                replace_at = index - 1
            if call >= len(code) or code[call] != "(":
                pieces.append(code[index])
                index += 1
                continue
        try:
            arg_end = c_text._match_delimiter(code, call)
        except ValueError:
            pieces.append(code[index])
            index += 1
            continue
        operand = _rewrite_indirect_calls(code[star + 1:close])
        arguments = _rewrite_indirect_calls(code[call + 1:arg_end])
        if replace_at < index and pieces:
            pieces.pop()
        pieces.append(f"(*(int (*)()){_function_address(operand)})({arguments})")
        index = arg_end + 1
    return "".join(pieces)


def _comparison_operand_is_pointer(expr: str, pointers: set[str], entries: set[str]) -> bool:
    text = expr.strip()
    while syntax._fully_wrapped(text):
        text = text[1:-1].strip()
    if not text:
        return False
    if text.startswith('"'):
        return True
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text) and text in entries:
        return True
    # `*(code **)slot` is a pointer. A single star yields the pointee.
    if text.startswith("*"):
        inner = text[1:].lstrip()
        if inner.startswith("("):
            try:
                end = c_text._match_delimiter(inner, 0)
            except ValueError:
                return False
            if inner[1:end].count("*") >= 2:
                return True
        return False
    return syntax._is_pointer_expr(text, pointers)


def _rewrite_pointer_compares(code: str, pointers: set[str]) -> str:
    """Compare pointer values as 32-bit firmware addresses."""
    entry_addresses = layout._function_entries()
    entries = set(entry_addresses)
    kind = expressions._kind_context(syntax._c_signature(code), code, pointers)

    def address(expr: str) -> str:
        expr = expr.strip()
        while syntax._fully_wrapped(expr):
            expr = expr[1:-1].strip()
        operand = syntax._pointer_cast_operand(expr)
        if operand is not None and kind(operand) == "integer":
            return f"(uint32_t)({operand})"
        return f"camry_host_addr({expr})"

    pieces: list[str] = []
    cursor = 0
    index = 0
    while index < len(code):
        if code.startswith(("<<", ">>"), index):
            index += 2
            continue
        # `->` is a member access, not a greater-than compare.
        if code[index] == ">" and index > 0 and code[index - 1] == "-":
            index += 1
            continue
        op = next(
            (item for item in ("<=", ">=", "==", "!=", "<", ">") if code.startswith(item, index)),
            None,
        )
        if op is None:
            index += 1
            continue
        raw_left = syntax._expr_before(code, index)
        left_at = index - len(raw_left)
        if left_at < cursor:
            index += len(op)
            continue
        right_end = syntax._expr_end_bound(code, index + len(op))
        raw_right = code[index + len(op):right_end]
        raw_left = re.sub(r"^\s*\(uintptr_t\)\s*", "", raw_left)
        raw_right = re.sub(r"^\s*\(uintptr_t\)\s*", "", raw_right)
        left_kind, right_kind = kind(raw_left), kind(raw_right)
        left_pointer = (
            left_kind != "integer"
            and _comparison_operand_is_pointer(raw_left, pointers, entries)
        )
        right_pointer = (
            right_kind != "integer"
            and _comparison_operand_is_pointer(raw_right, pointers, entries)
        )
        if left_pointer and right_pointer:
            # A cast integer is already a firmware word, not a mapped pointer.
            pieces.append(code[cursor:left_at])
            pieces.append(address(raw_left))
            pieces.append(op)
            pieces.append(address(raw_right))
            cursor = right_end
            index = right_end
            continue
        # A pointer slot holds a firmware address. Comparing that word with
        # `(void *)0x0` is the `cmp r0` in the bytes, not a host-pointer test.
        if left_pointer and not right_pointer and syntax._is_null_pointer_expr(raw_left):
            pieces.append(code[cursor:left_at])
            pieces.append("0")
            cursor = index
            index += len(op)
            continue
        if right_pointer and not left_pointer and syntax._is_null_pointer_expr(raw_right):
            pieces.append(code[cursor:index + len(op)])
            pieces.append(" 0")
            cursor = right_end
            index = right_end
            continue
        # Mixed host pointers and firmware words compare target addresses.
        if left_kind == "pointer" and right_kind in {"integer", "null"}:
            pieces.append(code[cursor:left_at])
            pieces.append(f"camry_host_addr({raw_left.strip()}){op}{raw_right}")
            cursor = right_end
            index = right_end
            continue
        if left_kind in {"integer", "null"} and right_kind == "pointer":
            pieces.append(code[cursor:left_at])
            pieces.append(f"{raw_left}{op}camry_host_addr({raw_right.strip()})")
            cursor = right_end
            index = right_end
            continue
        # A uint32 field compared with a function designator is the entry address.
        left_name = raw_left.strip()
        right_name = raw_right.strip()
        left_entry = entry_addresses.get(left_name) if re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*", left_name,
        ) else None
        right_entry = entry_addresses.get(right_name) if re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*", right_name,
        ) else None
        if left_entry is not None and not right_pointer:
            pieces.append(code[cursor:left_at])
            pieces.append(f"0x{left_entry:x}u ")
            cursor = index
            index += len(op)
            continue
        if right_entry is not None and not left_pointer:
            pieces.append(code[cursor:index + len(op)])
            pieces.append(f" 0x{right_entry:x}u")
            cursor = right_end
            index = right_end
            continue
        index += len(op)
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_wide_call_constants(code: str) -> str:
    """A hex literal above INT_MAX is unsigned, so passing it to short warns.

    `(int)0xfffff800` is the same bits and is the negative short Ghidra meant.
    """

    def rewrite(text: str) -> str:
        pieces: list[str] = []
        cursor = 0
        for match in syntax._CALL.finditer(text):
            if match.start() < cursor:
                continue
            try:
                close = c_text._match_delimiter(text, match.end() - 1)
            except ValueError:
                continue
            inner = rewrite(text[match.end():close])
            arguments = c_text._split_args(inner)
            rewritten_args: list[str] = []
            for arg in arguments:
                stripped = arg.strip()
                wrapped = re.fullmatch(r"\(\(uint32_t\)\((0x[0-9A-Fa-f]+)u\)\)", stripped)
                literal = wrapped.group(1) if wrapped else stripped
                if re.fullmatch(r"0x[0-9A-Fa-f]+", literal) and int(literal, 16) > 0x7FFFFFFF:
                    prefix = arg[:len(arg) - len(arg.lstrip())]
                    suffix = arg[len(arg.rstrip()):]
                    rewritten_args.append(f"{prefix}(int){stripped}{suffix}")
                else:
                    rewritten_args.append(arg)
            pieces.append(text[cursor:match.end()])
            pieces.append(",".join(rewritten_args))
            cursor = close
        pieces.append(text[cursor:])
        return "".join(pieces)

    return rewrite(code)


_SLOT_WORD_DEREF = re.compile(
    r"\*\s*\(\s*(int|uint|undefined4|ulong|long)\s*\*\s*\)\s*"
    r"([A-Za-z_][A-Za-z0-9_]*)\b"
)
_SLOT_WORD_CTYPE = {
    "int": "int32_t",
    "uint": "uint32_t",
    "undefined4": "uint32_t",
    "ulong": "uint32_t",
    "long": "int32_t",
}


def _rewrite_slot_word_derefs(code: str) -> str:
    """`*(int *)SLOT` loads the word stored at a pointer slot.

    The slot macro is already that firmware address. A host dereference of
    the integer is not the `ld.w`.
    """
    slots = expressions._uint32_slot_names()
    spans = c_text._comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    for match in _SLOT_WORD_DEREF.finditer(code):
        if match.start() < cursor or c_text._span_contains(spans, match.start()):
            continue
        if match.group(2) not in slots or not syntax._is_deref_star(code, match.start()):
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(syntax._typed_load(match.group(2), _SLOT_WORD_CTYPE[match.group(1)]))
        cursor = match.end()
    pieces.append(code[cursor:])
    return "".join(pieces)
