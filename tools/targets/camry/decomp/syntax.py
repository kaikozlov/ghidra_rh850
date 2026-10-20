"""Low-level C text parsing and scalar syntax helpers."""
from __future__ import annotations

import re

from . import c_text
from .conversion import rewrite_pointer



_CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_SKIP_CALLS = {
    "if", "for", "while", "switch", "return", "sizeof", "offsetof",
    "camry_host_ptr", "camry_host_addr", "camry_indirect", "__synchronize",
}
_BLOCK = re.compile(
    r"->|\.[A-Za-z]|\bcode\s*\*|"
    r"\((?:unsigned int|int|uint|undefined4|ulong|long)\)\s*\(\s*&|"
    r"\b(?:unaff_|extraout_|in_r\d+|in_E|in_PSW|in_FPEC|"
    r"CONCAT|SUB4|SBORROW|OVERFLOW)"
)
_INT_CAST = re.compile(r"\((unsigned int|int|uint|undefined4|ulong|long|uint32_t|int32_t)\)")
_IDIOM = re.compile(
    r"(\w+)\s*<\s*0\s*!=\s*\(\s*(\w+)\s*<\s*0\s*&&\s*-1\s*<\s*\1\s*\)"
)
_PRIMITIVE_TYPES = {
    "byte", "uchar", "undefined", "undefined1", "undefined2", "undefined4",
    "undefined8", "ushort", "uint", "ulong", "ulonglong", "longlong", "bool",
    "int", "char", "short", "long", "void", "float", "double", "signed",
    "unsigned", "const", "volatile", "struct",
}


def _strip_comments(code: str) -> str:
    return re.sub(r"/\*.*?\*/", "", code, flags=re.S)


def _opening_brace(code: str) -> int:
    """Body brace. Comments may contain `{lp}` before the function itself."""
    index = 0
    while index < len(code):
        if code.startswith("/*", index):
            end = code.find("*/", index + 2)
            if end < 0:
                return -1
            index = end + 2
            continue
        if code[index] == "{":
            return index
        index += 1
    return -1


def _c_signature(code: str) -> str:
    stripped = _strip_comments(code).strip()
    return " ".join(stripped.split("{", 1)[0].split())


def _pointer_names(signature: str, code: str) -> set[str]:
    names: set[str] = set()
    opening = signature.find("(")
    closing = signature.rfind(")")
    if 0 <= opening < closing:
        body = signature[opening + 1:closing].strip()
        if body and body != "void":
            for part in c_text._split_args(body):
                if "*" not in part:
                    continue
                match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", part.strip())
                if match:
                    names.add(match.group(1))
    names.update(re.findall(
        r"^[ \t]*(?!(?:return|goto)\b)[A-Za-z_][A-Za-z0-9_]*[ \t]+"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*\d+\s*\]\s*;",
        code, re.M,
    ))
    for line in code.splitlines():
        text = line.strip()
        if not text.endswith(";") or "(" in text or "*" not in text or text.startswith("/*"):
            continue
        first = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text)
        first_word = first.group(0) if first else ""
        # `DAT_x = a * b;` is a store, not `type *name`. A capital symbol is
        # not a struct type, and the `*` is multiplication.
        is_decl = first_word in _PRIMITIVE_TYPES | _INT_TYPES | {"code", "enum", "sbyte"} or (
            re.fullmatch(r"[A-Z][A-Za-z0-9_]*", first_word) is not None
            and not first_word.startswith(("DAT_", "UNK_", "PTR_", "LAB_", "Ram", "uRam"))
        )
        if is_decl:
            for match in re.finditer(r"\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:;|,|=)", text):
                names.add(match.group(1))
            continue
        # `a * b` is multiplication. `*b` and `= *b` are dereferences.
        for match in re.finditer(r"\*\s*([A-Za-z_][A-Za-z0-9_]*)", text):
            prev = match.start() - 1
            while prev >= 0 and text[prev] in " \t":
                prev -= 1
            if prev >= 0 and (text[prev].isalnum() or text[prev] in "_)\\]"):
                continue
            names.add(match.group(1))
    return names


def _looks_like_type(inner: str) -> bool:
    text = inner.strip()
    while text.endswith("*"):
        text = text[:-1].strip()
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ ]*", text) is not None


def _is_pointer_expr(expr: str, pointers: set[str]) -> bool:
    expr = expr.strip()
    if not expr:
        return False
    if expr.startswith("camry_host_ptr") or expr.startswith("camry_host_addr"):
        return expr.startswith("camry_host_ptr")
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", expr)
    if match:
        return match.group(0) in pointers
    if expr[0] != "(":
        return False
    end = c_text._match_delimiter(expr, 0)
    inner = expr[1:end].strip()
    rest = expr[end + 1:].strip()
    if _looks_like_type(inner):
        return inner.rstrip().endswith("*")
    grouped = _is_pointer_expr(inner, pointers)
    if not rest:
        return grouped
    if rest[0] in "+-" or rest.startswith("<<") or rest.startswith(">>"):
        return grouped
    return False


def _is_null_expr(expr: str) -> bool:
    text = expr.strip()
    while text.startswith("("):
        try:
            end = c_text._match_delimiter(text, 0)
        except ValueError:
            return False
        if end != len(text) - 1:
            return False
        text = text[1:-1].strip()
    return text in {"0", "0x0", "0x00", "0u", "0U", "NULL"}


_NULL_POINTER = re.compile(
    r"^\(\s*[A-Za-z_][A-Za-z0-9_ \t]*\*\s*\)\s*(?:0x0+|0+)\s*$"
)


def _is_null_pointer_expr(expr: str) -> bool:
    """`(void *)0x0` is a null pointer constant, not a firmware address."""
    text = expr.strip()
    while text.startswith("(") and text.endswith(")"):
        try:
            end = c_text._match_delimiter(text, 0)
        except ValueError:
            return False
        if end != len(text) - 1:
            return False
        inner = text[1:-1].strip()
        if _NULL_POINTER.fullmatch(inner):
            return True
        if _looks_like_type(inner):
            return False
        text = inner
    return _NULL_POINTER.fullmatch(text) is not None


def _enclosing_call(code: str, pos: int, name: str) -> bool:
    """True when `pos` sits inside a call to `name`."""
    depth = 0
    index = pos
    while index >= 0:
        char = code[index]
        if char == ")":
            depth += 1
        elif char == "(":
            if depth == 0:
                cursor = index - 1
                while cursor >= 0 and code[cursor] in " \t\n\r":
                    cursor -= 1
                end = cursor
                while cursor >= 0 and (code[cursor].isalnum() or code[cursor] == "_"):
                    cursor -= 1
                if code[cursor + 1:end + 1] == name:
                    return True
            else:
                depth -= 1
        index -= 1
    return False


def _volatile_at(address_expr: str, ctype: str) -> str:
    return f"(*((volatile {ctype} *)camry_host_ptr((uint32_t)({address_expr}))))"


def _compare_after(code: str, index: int) -> tuple[str | None, int]:
    index = c_text._skip_space(code, index)
    for op in ("<=", ">=", "==", "!="):
        if code.startswith(op, index):
            return op, index
    if index < len(code) and code[index] in "<>":
        nxt = code[index + 1] if index + 1 < len(code) else ""
        if nxt not in "<=>":
            return code[index], index
    return None, index


def _compare_before(code: str, index: int) -> tuple[str | None, int]:
    index -= 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    if index < 0:
        return None, index
    if index >= 1 and code[index - 1:index + 1] in ("<=", ">=", "==", "!="):
        return code[index - 1:index + 1], index - 1
    if code[index] in "<>" and (index == 0 or code[index - 1] not in "<>"):
        return code[index], index
    return None, index


def _expr_end_bound(code: str, start: int) -> int:
    depth = 0
    index = c_text._skip_space(code, start)
    while index < len(code):
        if code.startswith(("<<", ">>"), index):
            index += 2
            continue
        char = code[index]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            if depth == 0:
                break
            depth -= 1
        elif depth == 0 and char == ">" and index > 0 and code[index - 1] == "-":
            pass
        elif depth == 0 and (
            char in ";,?:<>"
            or code.startswith("||", index)
            or code.startswith("&&", index)
            or code.startswith("==", index)
            or code.startswith("!=", index)
        ):
            break
        index += 1
    return index


def _expr_before(code: str, op_index: int) -> str:
    depth = 0
    start = op_index
    index = op_index
    while index > 0:
        index -= 1
        if code.startswith(("<<", ">>"), index):
            start = index
            continue
        char = code[index]
        if char in ")]}":
            depth += 1
        elif char in "([{":
            if depth == 0:
                start = index + 1
                break
            depth -= 1
        elif depth == 0 and char == ">" and index > 0 and code[index - 1] == "-":
            pass
        elif depth == 0 and char == "=":
            prev = code[index - 1] if index else ""
            nxt = code[index + 1] if index + 1 < len(code) else ""
            if prev not in "=!<>" and nxt != "=":
                start = index + 1
                break
        elif depth == 0 and (
            char in ";,?:<>"
            or (index > 0 and code.startswith(("||", "&&", "==", "!="), index - 1))
        ):
            start = index + 1
            break
        start = index
    operand = code[start:op_index]
    returned = re.match(r"\s*return\b\s*", operand)
    return operand[returned.end():] if returned else operand


def _operand_end(code: str, start: int) -> int:
    if code[start] == "(":
        return c_text._match_delimiter(code, start) + 1
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[start:])
    if match is None:
        return start
    return start + match.end()


_INT_TYPES = {
    "unsigned int", "int", "uint", "undefined4", "ulong", "long", "uint32_t",
    "uint16_t", "uint8_t", "int32_t", "int16_t", "int8_t", "undefined2",
    "undefined1", "undefined", "ushort", "byte", "uchar", "short", "char",
    "unsigned", "signed", "bool", "code", "uintptr_t",
}


def _declared_integers(signature: str, code: str) -> set[str]:
    names: set[str] = set()
    opening = signature.find("(")
    closing = signature.rfind(")")
    if 0 <= opening < closing:
        body = signature[opening + 1:closing].strip()
        if body and body != "void":
            for part in c_text._split_args(body):
                if "*" in part or "[" in part:
                    continue
                match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", part.strip())
                if match and match.group(1) not in _PRIMITIVE_TYPES:
                    names.add(match.group(1))
    for line in code.splitlines():
        text = line.strip()
        if not text.endswith(";") or "(" in text:
            continue
        text = text[:-1].strip()
        type_match = re.match(
            r"^(?:(?:extern|static|const|volatile|unsigned|signed|struct)\s+)*"
            r"[A-Za-z_][A-Za-z0-9_]*\s+(.*)$",
            text,
        )
        if type_match is None:
            continue
        for part in c_text._split_args(type_match.group(1)):
            if "*" in part or "[" in part:
                continue
            left = part.split("=", 1)[0].strip()
            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)", left)
            if match:
                names.add(match.group(1))
    return names


_ARCHITECTURAL_SCALARS = {"camry_gp", "camry_tp", "camry_sp", "camry_pmr", "camry_psw"}


def _fully_wrapped(text: str) -> bool:
    if not text.startswith("(") or not text.endswith(")"):
        return False
    try:
        return c_text._match_delimiter(text, 0) == len(text) - 1
    except ValueError:
        return False


def _is_int_type(text: str) -> bool:
    collapsed = " ".join(text.replace("*", " ").split())
    return collapsed in _INT_TYPES or collapsed in {"unsigned int", "signed int", "unsigned long", "signed long"}


def _is_pointer_type(text: str) -> bool:
    return text.rstrip().endswith("*") and _looks_like_type(text)


def _paren_closes_cast(text: str, close: int) -> bool:
    """True when `)` closes `(type)`, so a following `*` is a dereference."""
    depth = 0
    for index in range(close, -1, -1):
        char = text[index]
        if char == ")":
            depth += 1
        elif char == "(":
            depth -= 1
            if depth == 0:
                inner = " ".join(text[index + 1:close].split())
                return _is_int_type(inner) or _is_pointer_type(inner)
    return False


def _binary_ops(text: str) -> list[tuple[int, str]]:
    ops: list[tuple[int, str]] = []
    depth = 0
    index = 0
    while index < len(text):
        if text.startswith("->", index):
            index += 2
            continue
        if text.startswith(("<<", ">>"), index):
            if depth == 0:
                ops.append((index, text[index:index + 2]))
            index += 2
            continue
        char = text[index]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif depth == 0 and char in "+-*/%&|^" and index > 0:
            previous = index - 1
            while previous >= 0 and text[previous] in " \t":
                previous -= 1
            if previous >= 0 and text[previous] not in "+-*/%&|^<>=!({[,:":
                # `(uint)*(expr)` is a cast of a dereference, not a product.
                if (
                    char in "*&"
                    and text[previous] == ")"
                    and _paren_closes_cast(text, previous)
                ):
                    index += 1
                    continue
                ops.append((index, char))
        index += 1
    return ops


_KIND_PREC = (
    {"|"},
    {"^"},
    {"&"},
    {"<<", ">>"},
    {"+", "-"},
    {"*", "/", "%"},
)


def _fold_kind(op: str, left: str, right: str) -> str:
    left = "integer" if left == "null" else left
    right = "integer" if right == "null" else right
    if left == "unknown" or right == "unknown":
        return "unknown"
    if op in {"+", "-"} and left == "pointer" and right == "integer":
        return "pointer"
    if op == "+" and right == "pointer" and left == "integer":
        return "pointer"
    if op == "-" and left == "pointer" and right == "pointer":
        return "integer"
    if left == "integer" and right == "integer":
        return "integer"
    return "unknown"


def _param_type_list(params: str) -> list[str]:
    body = " ".join(params.split()).strip()
    if not body or body == "void":
        return []
    types: list[str] = []
    for part in c_text._split_args(body):
        text = " ".join(part.split()).strip()
        text = re.sub(r"\s*\[\s*\d*\s*\]", " *", text).strip()
        match = re.fullmatch(r"(.*\W)([A-Za-z_][A-Za-z0-9_]*)$", text)
        if match and match.group(2) not in _PRIMITIVE_TYPES and match.group(2) not in _INT_TYPES:
            text = match.group(1).strip()
        types.append(text)
    return types


def _signature_param_types(signature: str) -> list[str]:
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening:
        return []
    return _param_type_list(signature[opening + 1:closing])


def _pointer_cast_operand(arg: str) -> str | None:
    """The expression under a pointer cast, when the argument is only that cast."""
    text = arg.strip()
    if not text.startswith("("):
        return None
    try:
        end = c_text._match_delimiter(text, 0)
    except ValueError:
        return None
    inner = " ".join(text[1:end].split())
    if not _is_pointer_type(inner):
        return None
    operand = text[end + 1:].strip()
    return operand or None


def _is_type_cast(inner: str) -> bool:
    return _is_int_type(inner) or _is_pointer_type(inner)


def _postfix_end(code: str, index: int) -> int:
    while True:
        index = c_text._skip_space(code, index)
        if index >= len(code):
            return index
        if code[index] == "(":
            index = c_text._match_delimiter(code, index) + 1
            continue
        if code[index] == "[":
            index = c_text._match_delimiter(code, index, "[]", quoted=False) + 1
            continue
        arrow = code.startswith("->", index)
        if arrow or (code[index] == "." and not code.startswith("..", index)):
            start = c_text._skip_space(code, index + (2 if arrow else 1))
            if start < len(code) and (code[start].isalpha() or code[start] == "_"):
                index = _operand_end(code, start)
                continue
        return index


def _unary_operand_end(code: str, index: int) -> int | None:
    """End of the operand after a `(integer-type)` cast."""
    index = c_text._skip_space(code, index)
    if index >= len(code):
        return None
    if code[index] in "*&":
        return _unary_operand_end(code, index + 1)
    if code[index] == "(":
        end = c_text._match_delimiter(code, index) + 1
        if _is_type_cast(code[index + 1:end - 1]):
            return _unary_operand_end(code, end)
        return _postfix_end(code, end)
    if code[index].isalpha() or code[index] == "_":
        return _postfix_end(code, _operand_end(code, index))
    number = re.match(r"0x[0-9A-Fa-f]+u?|\d+", code[index:])
    if number is None:
        return None
    return index + number.end()


def _integer_constant_bits(expr: str) -> str | None:
    """The bits of a Ghidra pointer cast of a literal, when that cast is a compare."""
    text = expr.strip()
    if re.fullmatch(r"0x[0-9A-Fa-f]+", text):
        value = int(text, 16)
    elif re.fullmatch(r"\d+", text):
        value = int(text, 10)
    else:
        return None
    if value > 0x7FFFFFFF:
        return f"0x{value:x}u"
    return text


def _is_compare_operand(code: str, start: int, end: int) -> bool:
    """True when [start, end) is the left or right side of a comparison."""
    left = start - 1
    while left >= 0 and code[left] in " \t\n":
        left -= 1
    if left >= 1 and code[left - 1:left + 1] in {"==", "!=", "<=", ">="}:
        return True
    if left >= 0 and code[left] in "<>" and code[left - 1:left + 1] not in {"->", ">>"}:
        return True
    right = end
    while right < len(code) and code[right] in " \t\n":
        right += 1
    if code.startswith(("==", "!=", "<=", ">="), right):
        return True
    return right < len(code) and code[right] in "<>"


def _returns_pointer(signature: str) -> bool:
    return "*" in signature.split("(", 1)[0]


def _negative_constant(expr: str) -> int | None:
    text = expr.strip()
    while text.startswith("(") and text.endswith(")"):
        try:
            if c_text._match_delimiter(text, 0) != len(text) - 1:
                break
        except ValueError:
            break
        text = text[1:-1].strip()
    if re.fullmatch(r"-0x[0-9A-Fa-f]+|-\d+", text) is None:
        return None
    value = int(text, 0)
    if -32768 <= value <= -1:
        return value
    return None


def _pointer_element_widths(code: str) -> dict[str, int]:
    sizes = {
        "undefined1": 1, "undefined": 1, "byte": 1, "uchar": 1, "char": 1, "code": 1,
        "undefined2": 2, "ushort": 2, "short": 2,
        "undefined4": 4, "uint": 4, "ulong": 4, "int": 4,
        "undefined8": 8,
    }
    found: dict[str, int] = {}
    pattern = re.compile(
        r"\b(undefined[1248]|undefined|byte|uchar|ushort|short|uint|ulong|int|char|code)\s*"
        r"\*\s*([A-Za-z_][A-Za-z0-9_]*)"
    )
    for match in pattern.finditer(code):
        width = sizes.get(match.group(1))
        if width is not None:
            found[match.group(2)] = width
    return found


def _deref_width(text: str) -> int | None:
    if not (text.startswith("(*") and text.endswith(")")):
        return None
    try:
        if c_text._match_delimiter(text, 0) != len(text) - 1:
            return None
    except ValueError:
        return None
    inner = text[1:-1].strip()
    match = re.match(
        r"^\*\(\((?:volatile\s+)?(byte|uchar|undefined1|undefined|uint8_t|char|code|"
        r"ushort|undefined2|uint16_t)\s*\*\)",
        inner,
    )
    if match is None:
        return None
    return 1 if match.group(1) in {
        "byte", "uchar", "undefined1", "undefined", "uint8_t", "char", "code",
    } else 2


def _rewrite_thunk_calls(code: str) -> str:
    signature = _c_signature(code)
    match = re.search(r"\b(thunk_[A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
    if match is None:
        return code
    name = match.group(1)
    target = name[len("thunk_"):]
    brace = _opening_brace(code)
    if brace < 0:
        return code
    body = re.sub(rf"\b{name}\b", target, code[brace:])
    return code[:brace] + body


def _strip_calling_convention(code: str) -> str:
    """Drop a Ghidra convention token sitting between the return type and the name."""
    brace = _opening_brace(code)
    if brace < 0:
        return code
    return re.sub(r"\b__[A-Za-z_][A-Za-z0-9_]*\b", "", code[:brace]) + code[brace:]


def _stmt_parts(stmt: str) -> tuple[str, list[int | None]] | None:
    match = re.match(r"camry_([A-Za-z0-9_]+)\((.*)\)\s*;?$", stmt.strip())
    if match is None:
        return None
    args: list[int | None] = []
    for part in match.group(2).split(","):
        text = part.strip().rstrip("uU")
        if re.fullmatch(r"0x[0-9A-Fa-f]+", text):
            args.append(int(text, 16))
        elif re.fullmatch(r"-?\d+", text):
            args.append(int(text))
        else:
            args.append(None)
    return match.group(1), args


def _param_names(signature: str) -> list[str]:
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening:
        return []
    body = signature[opening + 1:closing].strip()
    if not body or body == "void":
        return []
    names = []
    for part in c_text._split_args(body):
        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", part.strip())
        names.append(match.group(1) if match else "")
    return names


def _signature_name(signature: str) -> str:
    match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
    return match.group(1) if match else ""


def _return_type_of(signature: str, name: str) -> str:
    found = re.search(rf"\b{re.escape(name)}\s*\(", signature)
    if found is None:
        return ""
    return " ".join(signature[:found.start()].split())


def _trailing_call_span(code: str) -> tuple[str, int, int] | None:
    """A lone `return;` whose previous statement is a call.

    The returned indexes are relative to the function body, including its brace.
    """
    brace = _opening_brace(code)
    if brace < 0:
        return None
    body = code[brace:]
    returns = list(re.finditer(r"\breturn\s*;", body))
    if len(returns) != 1:
        return None
    ret = returns[0]
    call_end = body.rfind(";", 0, ret.start())
    if call_end < 0:
        return None
    prev = call_end - 1
    while prev >= 0 and body[prev] not in ";{}":
        prev -= 1
    statement = _strip_comments(body[prev + 1:call_end]).strip()
    if re.search(r"(?<![=<>!])=(?!=)", statement):
        return None
    if not re.fullmatch(r"(?:[A-Za-z_][A-Za-z0-9_]*\s*|\(\*.*\))\(.*\)", statement, flags=re.S):
        return None
    return statement, prev + 1, ret.end()


def _trailing_call(code: str) -> str | None:
    span = _trailing_call_span(code)
    return None if span is None else span[0]


def _access_width(text: str) -> int | None:
    if re.search(r"\.(?:bu|b)\b", text):
        return 1
    if re.search(r"\.(?:hu|h)\b", text):
        return 2
    if re.search(r"\.w\b", text):
        return 4
    return None


def _last_declarator(head: str, name: str) -> tuple[int, int] | None:
    chars = list(head)
    index = 0
    while index < len(chars):
        if chars[index] == "/" and index + 1 < len(chars) and chars[index + 1] == "*":
            end = head.find("*/", index + 2)
            end = len(chars) if end < 0 else end + 2
            for cursor in range(index, end):
                chars[cursor] = " "
            index = end
            continue
        index += 1
    matches = list(re.finditer(rf"\b{re.escape(name)}\s*\(", "".join(chars)))
    if len(matches) != 1:
        return None
    open_at = matches[0].end() - 1
    try:
        return open_at, c_text._match_delimiter(head, open_at)
    except ValueError:
        return None


def _const_value(text: str) -> int | None:
    match = re.fullmatch(r"(0x[0-9A-Fa-f]+|-?\d+)[uUlL]*", text.strip())
    if match is None:
        return None
    token = match.group(1)
    value = int(token, 16) if token.lower().startswith("0x") else int(token)
    return value & 0xFFFFFFFF


def _displacement(base: int, index: str, scale: int | None, pointee: str) -> str:
    factor = f"{scale}u" if scale is not None else f"(uint32_t)sizeof({pointee})"
    return f"0x{base:x}u + (uint32_t)({index}) * {factor}"


def _apply_spans(code: str, spans: list[tuple[int, int, str]]) -> str:
    chosen: list[tuple[int, int, str]] = []
    for start, end, text in sorted(spans, key=lambda item: (item[0], -(item[1] - item[0]))):
        if any(not (end <= have_start or start >= have_end) for have_start, have_end, _text in chosen):
            continue
        chosen.append((start, end, text))
    for start, end, text in sorted(chosen, reverse=True):
        code = code[:start] + text + code[end:]
    return code


_NARROW_DEREF_CTYPE = {
    **rewrite_pointer._SLOT_WORD_CTYPE,
    "undefined1": "uint8_t",
    "uchar": "uint8_t",
    "byte": "uint8_t",
    "undefined": "uint8_t",
    "ushort": "uint16_t",
    "short": "int16_t",
    "undefined2": "uint16_t",
    "uint32_t": "uint32_t",
    "int32_t": "int32_t",
    "uint16_t": "uint16_t",
    "int16_t": "int16_t",
    "uint8_t": "uint8_t",
    "int8_t": "int8_t",
}


def _is_deref_star(code: str, index: int) -> bool:
    if index < 0 or index >= len(code) or code[index] != "*":
        return False
    prev = index - 1
    while prev >= 0 and code[prev] in " \t":
        prev -= 1
    if prev < 0:
        return True
    # `(byte)*slot` is a dereference. `) * slot` is multiplication.
    if code[prev] == ")":
        return code[index - 1] == ")"
    return code[prev] in "\n;{}(,=*&!~?:[+-/%|^<>"


def _typed_load(addr: str, ctype: str) -> str:
    return f"(*((volatile {ctype} *)camry_host_ptr((uint32_t)({addr}))))"


def _deref_operand(code: str, at: int) -> tuple[str, int] | None:
    at = c_text._skip_space(code, at)
    if at >= len(code):
        return None
    if code[at] == "(":
        try:
            close = c_text._match_delimiter(code, at)
        except ValueError:
            return None
        return code[at:close + 1], close + 1
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[at:])
    if match is None:
        return None
    return match.group(0), at + match.end()


def _eligible(code: str) -> bool:
    return _BLOCK.search(_strip_comments(code)) is None


def _rhs_end(code: str, start: int) -> int:
    depth = 0
    index = start
    while index < len(code):
        char = code[index]
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                return index
            depth -= 1
        elif depth == 0 and char in ",;":
            return index
        index += 1
    return index


def _null_pointer(expr: str) -> bool:
    text = expr.strip()
    if _is_null_expr(text):
        return True
    return re.fullmatch(r"\([^()]*\*\s*\)\s*(?:0x0+|0+u?|NULL)", text) is not None


def _host_pointer(access: str, pointed: str) -> str:
    return f"(({pointed} *)camry_host_ptr((uint32_t)({access})))"


def _assignment_sites(code: str, *, nested: bool = False) -> list[int]:
    spans = c_text._comment_spans(code)
    sites: list[int] = []
    depth = 0
    index = 0
    while index < len(code):
        if code.startswith("/*", index):
            end = code.find("*/", index + 2)
            index = len(code) if end < 0 else end + 2
            continue
        if code.startswith("//", index):
            end = code.find("\n", index)
            index = len(code) if end < 0 else end + 1
            continue
        char = code[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif (
            (nested or depth == 0)
            and char == "="
            and not c_text._span_contains(spans, index)
            and (index == 0 or code[index - 1] not in "=!<>+-*/%&|^")
            and (index + 1 >= len(code) or code[index + 1] != "=")
        ):
            sites.append(index)
        index += 1
    return sites


def _scan_side(code: str, start: int, step: int, stops: str) -> int:
    depth = 0
    index = start
    while 0 <= index < len(code):
        char = code[index]
        if step < 0 and char == "}" and depth == 0:
            return index + 1
        if step < 0 and char in ")]}":
            depth += 1
        elif step < 0 and char in "([{":
            if depth == 0:
                return index + 1
            depth -= 1
        elif step > 0 and char == "(":
            depth += 1
        elif step > 0 and char == ")":
            if depth == 0:
                return index
            depth -= 1
        elif depth == 0 and char in stops:
            return index + (1 if step < 0 else 0)
        index += step
    return 0 if step < 0 else len(code)


def _split_additive(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif depth == 0 and char in "+-" and index > 0:
            previous = index - 1
            while previous >= 0 and text[previous] in " \t":
                previous -= 1
            if previous >= 0 and text[previous] not in "+-*/%&|^<>=!({[,:":
                parts.append(text[start:index].strip())
                start = index + 1
        index += 1
    parts.append(text[start:].strip())
    return parts


def _is_word_load(text: str) -> bool:
    needle = "(*((volatile uint32_t *)camry_host_ptr("
    if not text.startswith(needle):
        return False
    open_paren = len("(*((volatile uint32_t *)camry_host_ptr")
    try:
        close = c_text._match_delimiter(text, open_paren)
    except ValueError:
        return False
    return text[close + 1:].strip() == "))"
