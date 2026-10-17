#!/usr/bin/env python3
"""Link the Camry CodeFlash image from its symbol map and report decomp status."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tools import REPO_ROOT
from tools.project.analysis_target import target as resolve_target

TARGET = "camry-8965F3307000"
ROOT = REPO_ROOT / "decomp" / TARGET


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            text = line.strip()
            if not text:
                continue
            try:
                row = json.loads(text)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise SystemExit(f"{path}:{line_number}: expected an object")
            rows.append(row)
    return rows


def load_symbols() -> list[dict]:
    return _load_jsonl(ROOT / "symbols.jsonl")


def load_matched() -> list[dict]:
    return _load_jsonl(ROOT / "matched.jsonl")


def _address(value: str) -> int:
    return int(value, 16)


def function_ranges(symbols: list[dict]) -> list[tuple[int, int, str]]:
    ranges: list[tuple[int, int, str]] = []
    for row in symbols:
        name = row["name"]
        for start, end in row["ranges"]:
            if end < start:
                raise SystemExit(f"{name}: range end {end:#x} precedes start {start:#x}")
            ranges.append((start, end, name))
    ranges.sort()
    previous_end = -1
    previous_name = ""
    for start, end, name in ranges:
        if start <= previous_end:
            raise SystemExit(
                f"overlapping function bytes: {previous_name} through {previous_end:#x} "
                f"and {name} at {start:#x}"
            )
        previous_end = end
        previous_name = name
    return ranges


def identity_image(symbols: list[dict] | None = None) -> tuple[bytes, dict]:
    """Rebuild CodeFlash by placing each symbol's original bytes back at its address."""
    metadata = resolve_target(TARGET)[1]
    image_path = REPO_ROOT / metadata["codeflash"]
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != metadata["codeflash_sha256"]:
        raise SystemExit(f"CodeFlash hash drift: {digest}")
    if len(image) != metadata["codeflash_size"]:
        raise SystemExit(
            f"CodeFlash size {len(image)} != registered {metadata['codeflash_size']}"
        )
    ranges = function_ranges(symbols if symbols is not None else load_symbols())
    rebuilt = bytearray(image)
    covered = 0
    outside = 0
    for start, end, name in ranges:
        if start >= len(image):
            outside += 1
            continue
        if end >= len(image):
            raise SystemExit(f"{name}: range {start:#x}..{end:#x} crosses the end of CodeFlash")
        rebuilt[start : end + 1] = image[start : end + 1]
        covered += end - start + 1
    if bytes(rebuilt) != image:
        raise SystemExit("identity link diverged from CodeFlash")
    report = {
        "target": TARGET,
        "codeflash_sha256": digest,
        "image_bytes": len(image),
        "functions": len(symbols if symbols is not None else load_symbols()),
        "function_bytes": covered,
        "gap_bytes": len(image) - covered,
        "ranges_outside_codeflash": outside,
        "matched": [
            {"addr": row["addr"], "name": row["name"], "status": row["status"]}
            for row in load_matched()
        ],
    }
    return bytes(rebuilt), report


def cmd_identity(args: argparse.Namespace) -> int:
    image, report = identity_image()
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(image)
        report["output"] = str(destination)
    report.pop("matched", None)
    print(json.dumps(report, indent=2))
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    _, report = identity_image()
    rows = report.pop("matched")
    named = sum(1 for row in load_symbols() if not row["name"].startswith("FUN_"))
    report["named_functions"] = named
    report["equivalent_functions"] = sum(1 for row in rows if row["status"] == "equivalent")
    report["byte_matched_functions"] = sum(1 for row in rows if row["status"] == "byte-matched")
    report["converted_functions"] = sum(1 for row in rows if row["status"] == "converted")
    report["unconvertible_functions"] = sum(1 for row in rows if row["status"] == "unconvertible")
    print(json.dumps(report, indent=2))
    return 0


_CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_SKIP_CALLS = {
    "if", "for", "while", "switch", "return", "sizeof",
    "camry_host_ptr", "camry_host_addr", "__synchronize",
}
_BLOCK = re.compile(
    r"->|\.[A-Za-z]|\bcode\s*\*|"
    r"\((?:unsigned int|int|uint|undefined4|ulong|long)\)\s*\(\s*&|"
    r"\b(?:unaff_|extraout_|in_r\d+|in_E|in_PSW|in_FPEC|"
    r"CONCAT|SUB4|SBORROW|OVERFLOW)"
)
_INT_CAST = re.compile(r"\((unsigned int|int|uint|undefined4|ulong|long)\)")
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


def _match_paren(code: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(code)):
        if code[index] == "(":
            depth += 1
        elif code[index] == ")":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unbalanced parenthesis")


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
            depth = 0
            start = 0
            parts: list[str] = []
            for index, char in enumerate(body):
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                elif char == "," and depth == 0:
                    parts.append(body[start:index])
                    start = index + 1
            parts.append(body[start:])
            for part in parts:
                if "*" not in part:
                    continue
                match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", part.strip())
                if match:
                    names.add(match.group(1))
    for line in code.splitlines():
        text = line.strip()
        if not text.endswith(";") or "(" in text or "*" not in text:
            continue
        for match in re.finditer(r"\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:;|,)", text):
            names.add(match.group(1))
    return names


def _looks_like_type(inner: str) -> bool:
    text = inner.strip()
    if text.endswith("*"):
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
    end = _match_paren(expr, 0)
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
            end = _match_paren(text, 0)
        except ValueError:
            return False
        if end != len(text) - 1:
            return False
        text = text[1:-1].strip()
    return text in {"0", "0x0", "0x00", "0u", "0U", "NULL"}


def _skip_space(code: str, index: int) -> int:
    while index < len(code) and code[index] in " \t\n\r":
        index += 1
    return index


def _match_bracket(code: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(code)):
        if code[index] == "[":
            depth += 1
        elif code[index] == "]":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unbalanced bracket")


def _rewrite_indexed(code: str) -> str:
    pieces: list[str] = []
    cursor = 0
    pattern = re.compile(r"\(&(DAT|UNK|LAB)_([0-9A-Fa-f]+)\)\s*\[")
    widths = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        try:
            end = _match_bracket(code, match.end() - 1)
        except ValueError:
            continue
        index = _rewrite_indexed(code[match.end():end])
        addr = int(match.group(2), 16)
        scale = _access_widths().get(addr, 1)
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


_ADDR_TOKEN = re.compile(r"&(?:LAB|DAT|UNK)_([0-9A-Fa-f]+)")


def _compare_after(code: str, index: int) -> tuple[str | None, int]:
    index = _skip_space(code, index)
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
    index = _skip_space(code, start)
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
        elif depth == 0 and (
            char in ";,?:<>"
            or (index > 0 and code.startswith(("||", "&&", "==", "!="), index - 1))
        ):
            start = index + 1
            break
        start = index
    return code[start:op_index]


def _address_compared_as_integer(code: str, match: re.Match[str], pointers: set[str]) -> bool:
    _op, op_at = _compare_after(code, match.end())
    if _op is not None:
        end = _expr_end_bound(code, op_at + len(_op))
        operand = code[op_at + len(_op):end].strip()
        if operand and not _is_pointer_expr(operand, pointers):
            return True
    _op, op_at = _compare_before(code, match.start())
    if _op is not None:
        operand = _expr_before(code, op_at).strip()
        if operand and not _is_pointer_expr(operand, pointers):
            return True
    return False


def _rewrite_address_compares(code: str, pointers: set[str]) -> str:
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
        r"\((unsigned int|int|uint|undefined4|ulong|long)\)\s*"
        r"&(?:LAB|DAT|UNK)_([0-9A-Fa-f]+)",
        integer_cast,
        code,
    )
    return re.sub(
        r"&(?:LAB|DAT|UNK)_([0-9A-Fa-f]+)",
        lambda match: f"((undefined *)camry_host_ptr(0x{int(match.group(1), 16):x}u))",
        code,
    )


def _operand_end(code: str, start: int) -> int:
    if code[start] == "(":
        return _match_paren(code, start) + 1
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[start:])
    if match is None:
        return start
    return start + match.end()


def _rewrite_pointer_to_int(code: str, pointers: set[str]) -> str:
    pieces: list[str] = []
    cursor = 0
    for match in _INT_CAST.finditer(code):
        if match.start() < cursor:
            continue
        begin = _skip_space(code, match.end())
        if begin >= len(code) or code[begin] not in "(ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_":
            continue
        end = _operand_end(code, begin)
        if end == begin:
            continue
        operand = code[begin:end]
        if end < len(code) and code[end] == "[":
            continue
        if not _is_pointer_expr(operand, pointers):
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(f"({match.group(1)})camry_host_addr({operand})")
        cursor = end
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_int_to_pointer(code: str, pointers: set[str]) -> str:
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
        while type_start > 0 and (code[type_start - 1].isalnum() or code[type_start - 1] in "_ \t"):
            type_start -= 1
        if type_start <= 0 or code[type_start - 1] != "(":
            search = star + 2
            continue
        type_name = " ".join(code[type_start:type_end].split())
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ ]*", type_name):
            search = star + 2
            continue
        after = _skip_space(code, star + 2)
        if after >= len(code):
            pieces.append(code[cursor:])
            break
        if code[after] == "(":
            end = _match_paren(code, after) + 1
            expr = code[after + 1:end - 1]
        elif code[after].isalpha() or code[after] == "_":
            end = _operand_end(code, after)
            expr = code[after:end]
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
        if _is_pointer_expr(expr, pointers) or _is_null_expr(expr):
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
        pieces.append(code[cursor:replace_at])
        cast = f"({type_name} *)camry_host_ptr((uint32_t)({expr}))"
        pieces.append(f"(*({cast}))" if deref else f"({cast})")
        cursor = end
        search = end
    return "".join(pieces)


def _returns_pointer(signature: str) -> bool:
    return "*" in signature.split("(", 1)[0]


def _rewrite_pointer_calls(code: str, pointers: set[str]) -> str:
    returns = _pointer_return_names()
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
            close = _match_paren(code, match.end() - 1)
        except ValueError:
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(f"{lhs} = camry_host_addr({callee}{code[match.end() - 1:close + 1]})")
        cursor = close + 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _negative_byte_constant(expr: str) -> int | None:
    text = expr.strip()
    while text.startswith("(") and text.endswith(")"):
        try:
            if _match_paren(text, 0) != len(text) - 1:
                break
        except ValueError:
            break
        text = text[1:-1].strip()
    if re.fullmatch(r"-0x[0-9A-Fa-f]+|-\d+", text) is None:
        return None
    value = int(text, 0)
    if -128 <= value <= -1:
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


def _is_byte_deref(text: str) -> bool:
    if not (text.startswith("(*") and text.endswith(")")):
        return False
    try:
        if _match_paren(text, 0) != len(text) - 1:
            return False
    except ValueError:
        return False
    inner = text[1:-1].strip()
    return re.match(
        r"^\*\(\((?:volatile\s+)?(?:byte|uchar|undefined1|undefined|uint8_t|char|code)\s*\*\)",
        inner,
    ) is not None


def _byte_lvalues(code: str) -> tuple[set[str], dict[str, int]]:
    scalars: set[str] = set()
    elements = {
        name: width
        for name, width in _pointer_element_widths(code).items()
        if width == 1
    }
    for match in re.finditer(r"\b((?:DAT|UNK)_[0-9A-Fa-f]+)\b", code):
        address = int(match.group(1).split("_", 1)[1], 16)
        if _access_widths().get(address) == 1:
            scalars.add(match.group(1))
    for name, (_addr, ctype, is_array) in _data_layouts().items():
        if ctype != "uint8_t":
            continue
        if is_array:
            elements[name] = 1
        else:
            scalars.add(name)
    return scalars, elements


def _is_unsigned_byte_lvalue(text: str, scalars: set[str], elements: dict[str, int]) -> bool:
    if re.match(r"^\(\s*int8_t\s*\)", text):
        return False
    if text in scalars:
        return True
    match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[(.*)\]", text, flags=re.S)
    if match and elements.get(match.group(1)) == 1:
        return True
    return _is_byte_deref(text)


def _cast_unsigned_byte(raw: str, scalars: set[str], elements: dict[str, int]) -> str | None:
    text = raw.strip()
    if _negative_byte_constant(text) is not None:
        return None
    if not _is_unsigned_byte_lvalue(text, scalars, elements):
        return None
    prefix = raw[:len(raw) - len(raw.lstrip())]
    suffix = raw[len(raw.rstrip()):]
    return f"{prefix}((int8_t){text}){suffix}"


def _rewrite_signed_byte_compares(code: str) -> str:
    """Ghidra spells an 8-bit compare against 0xAA as `!= -0x56`.

    A uint8 lvalue promotes to a non-negative int, so that compare is
    tautological. Casting the byte to int8_t keeps the bit-pattern test.
    """
    scalars, elements = _byte_lvalues(code)
    pieces: list[str] = []
    cursor = 0
    index = 0
    while index < len(code):
        if code.startswith(("<<", ">>"), index):
            index += 2
            continue
        op = next(
            (item for item in ("<=", ">=", "==", "!=", "<", ">") if code.startswith(item, index)),
            None,
        )
        if op is None:
            index += 1
            continue
        raw_left = _expr_before(code, index)
        left_at = index - len(raw_left)
        if left_at < cursor:
            index += len(op)
            continue
        right_end = _expr_end_bound(code, index + len(op))
        raw_right = code[index + len(op):right_end]
        left_constant = _negative_byte_constant(raw_left.strip())
        right_constant = _negative_byte_constant(raw_right.strip())
        if right_constant is not None:
            cast = _cast_unsigned_byte(raw_left, scalars, elements)
            if cast is not None:
                pieces.append(code[cursor:left_at])
                pieces.append(cast)
                cursor = index
                index += len(op)
                continue
        if left_constant is not None:
            cast = _cast_unsigned_byte(raw_right, scalars, elements)
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
    """A function designator used in address arithmetic is its entry address.

    `movea 19852, gp` is `gp + entry`, which Ghidra spells as
    `function_name + (int)pointer`.
    """
    entries = _function_entries()

    def replace(match: re.Match[str]) -> str:
        address = entries.get(match.group(1))
        if address is None:
            return match.group(0)
        return f"0x{address:x}u"

    return re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\b(?=\s*[+\-][^=+\-])", replace, code)


def _rewrite_function_indexes(code: str) -> str:
    entries = _function_entries()
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
            end = _match_bracket(code, match.end() - 1)
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


_BITFIELD = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\._(\d+)_(\d+)_")
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


def _rewrite_bitfields(code: str) -> str:
    """Ghidra `name._offset_size_` is a byte overlay, not a struct field."""
    addresses = _absolute_names()
    locals = _local_sizes(code)

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        offset = int(match.group(2))
        size = int(match.group(3))
        ctype = _BIT_WIDTHS.get(size)
        if ctype is None:
            return match.group(0)
        address = addresses.get(name)
        if address is not None:
            target = (address + offset) & 0xFFFFFFFF
            return f"(*((volatile {ctype} *)camry_host_ptr(0x{target:x}u)))"
        if locals.get(name, -1) < offset + size:
            return match.group(0)
        return f"(*(({ctype} *)((uint8_t *)&{name} + {offset}u)))"

    return _BITFIELD.sub(replace, code)


def _rewrite_thunk_calls(code: str) -> str:
    signature = _c_signature(code)
    match = re.search(r"\b(thunk_[A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
    if match is None:
        return code
    name = match.group(1)
    target = name[len("thunk_"):]
    head, sep, body = code.partition("{")
    if not sep:
        return code
    body = re.sub(rf"\b{name}\b", target, body)
    return head + sep + body


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
            end = _match_bracket(code, match.end() - 1)
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
            if _match_paren(text, 0) != len(text) - 1:
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


def _split_args(arguments: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(arguments):
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(arguments[start:index])
            start = index + 1
    parts.append(arguments[start:])
    return parts


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
        for match in _CALL.finditer(text):
            if match.start() < cursor or match.group(1) in _SKIP_CALLS:
                continue
            try:
                close = _match_paren(text, match.end() - 1)
            except ValueError:
                continue
            inner = wrap_calls(text[match.end():close])
            args = _split_args(inner)
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


def _rewrite_body(code: str) -> str:
    code = _rewrite_firmware_bases(code)
    signature = _c_signature(code)
    pointers = _pointer_names(signature, code)
    code = _rewrite_bitfields(code)
    code = _rewrite_thunk_calls(code)
    code = _IDIOM.sub(r"((\1 < 0) || (\2 < 0))", code)
    code = _rewrite_indexed(code)
    code = _rewrite_addresses(code, pointers)
    code = _rewrite_named_addresses(code, pointer_return=_returns_pointer(signature))
    code = _rewrite_pointer_to_int(code, pointers)
    code = _rewrite_int_to_pointer(code, pointers)
    code = _rewrite_pointer_calls(code, pointers)
    code = _rewrite_function_indexes(code)
    code = _rewrite_function_values(code)
    code = _rewrite_signed_byte_compares(code)
    return code


def _eligible(code: str) -> bool:
    return _BLOCK.search(_strip_comments(code)) is None


def _callees(code: str) -> set[str]:
    return {
        match.group(1)
        for match in _CALL.finditer(_strip_comments(code))
    } - _SKIP_CALLS


def _machine_registers() -> dict[str, dict]:
    payload = json.loads(
        (REPO_ROOT / "data" / "generated" / "p1me_machine.json").read_text(encoding="utf-8")
    )
    found: dict[str, dict] = {}
    for value in payload.values():
        if isinstance(value, dict):
            for row in value.get("registers") or []:
                if isinstance(row, dict) and "name" in row and "address" in row:
                    found[row["name"]] = row
    return found


_SCALAR_TYPES = {
    "u8": "uint8_t", "byte": "uint8_t", "uchar": "uint8_t", "s8": "int8_t",
    "u16": "uint16_t", "ushort": "uint16_t", "s16": "int16_t",
    "u32": "uint32_t", "uint": "uint32_t", "s32": "int32_t",
    "u8*": "uint32_t", "void*": "uint32_t",
}
_ARRAY_ELEMENTS = {
    "u8": ("uint8_t", 1), "s8": ("int8_t", 1),
    "u16": ("uint16_t", 2), "s16": ("int16_t", 2),
    "u32": ("uint32_t", 4), "s32": ("int32_t", 4),
    "u8*": ("uint32_t", 4),
}


def _data_symbols() -> dict[str, int]:
    return {name: addr for name, (addr, _ctype, _array) in _data_layouts().items()}


def _data_layouts() -> dict[str, tuple[int, str, bool]]:
    found: dict[str, tuple[int, str, bool]] = {}
    for row in _load_jsonl(ROOT / "data.jsonl"):
        addr = _address(row["addr"])
        type_name = row["type"].replace(" ", "")
        if "[" in type_name:
            element = type_name.split("[", 1)[0]
            if element in _ARRAY_ELEMENTS:
                ctype, _scale = _ARRAY_ELEMENTS[element]
                found[row["name"]] = (addr, ctype, True)
            elif re.fullmatch(r"[A-Z][A-Za-z0-9_]*", element):
                found[row["name"]] = (addr, element, True)
            else:
                found[row["name"]] = (addr, "uint8_t", False)
            continue
        ctype = _SCALAR_TYPES.get(type_name) or _scalar_type(addr, "uint8_t")
        found[row["name"]] = (addr, ctype, False)
    return found


def _absolute_names() -> dict[str, int]:
    names = _data_symbols()
    for name, row in _machine_registers().items():
        names[name] = int(row["address"])
    return names


def _rewrite_named_addresses(code: str, *, pointer_return: bool = False) -> str:
    names = _absolute_names()

    def replace(match: re.Match[str]) -> str:
        addr = names.get(match.group(1))
        if addr is None:
            return match.group(0)
        return f"(0x{addr:x}u)"

    if pointer_return:
        def returned(match: re.Match[str]) -> str:
            addr = names.get(match.group(1))
            if addr is None:
                return match.group(0)
            return f"return ((undefined *)camry_host_ptr(0x{addr:x}u))"

        code = re.sub(r"return\s+&([A-Za-z_][A-Za-z0-9_]*)\b", returned, code)
    return re.sub(r"&([A-Za-z_][A-Za-z0-9_]*)\b", replace, code)


_FUNCTION_ENTRIES: dict[str, int] | None = None
_POINTER_RETURNS: set[str] | None = None


def _corpus_functions() -> list[dict]:
    from tools.project.analysis_target import target as resolve_target
    from tools.project.pseudo import load_corpus

    metadata = resolve_target(TARGET)[1]
    _meta, functions = load_corpus(REPO_ROOT / metadata["decompiler_corpus"])
    return functions


def _function_entries() -> dict[str, int]:
    global _FUNCTION_ENTRIES
    if _FUNCTION_ENTRIES is None:
        _FUNCTION_ENTRIES = {
            row["name"]: int(row["entry_addr"], 16) for row in _corpus_functions()
        }
    return _FUNCTION_ENTRIES


def _pointer_return_names() -> set[str]:
    global _POINTER_RETURNS
    if _POINTER_RETURNS is None:
        _POINTER_RETURNS = {
            row["name"]
            for row in _corpus_functions()
            if _returns_pointer(_c_signature(row["decompiled_c"]))
        }
    return _POINTER_RETURNS


_ACCESS_WIDTHS: dict[int, int] | None = None


def _access_widths() -> dict[int, int]:
    """Majority load/store width at each data address the decompiler references."""
    global _ACCESS_WIDTHS
    if _ACCESS_WIDTHS is not None:
        return _ACCESS_WIDTHS
    from tools.camry_lift import decode_at
    from tools.project.analysis_target import target as resolve_target
    from tools.project.pseudo import load_corpus

    metadata = resolve_target(TARGET)[1]
    image = (REPO_ROOT / metadata["codeflash"]).read_bytes()
    _meta, functions = load_corpus(REPO_ROOT / metadata["decompiler_corpus"])
    sizes = {
        "ld.b": 1, "ld.bu": 1, "sld.b": 1, "sld.bu": 1, "st.b": 1, "sst.b": 1,
        "ld.h": 2, "ld.hu": 2, "sld.h": 2, "sld.hu": 2, "st.h": 2, "sst.h": 2,
        "ld.w": 4, "sld.w": 4, "st.w": 4, "sst.w": 4,
    }
    counts: dict[int, dict[int, int]] = {}
    for row in functions:
        for ref in row.get("data_references") or []:
            origin = int(ref["from_addr"], 16)
            if origin >= len(image):
                continue
            inst = decode_at(image, origin)
            if inst is None or not inst.text:
                continue
            width = sizes.get(inst.text.split()[0])
            if width is None:
                continue
            dest = int(ref["to_addr"], 16)
            bucket = counts.setdefault(dest, {})
            bucket[width] = bucket.get(width, 0) + 1
    _ACCESS_WIDTHS = {
        addr: max(bucket, key=bucket.get)
        for addr, bucket in counts.items()
    }
    return _ACCESS_WIDTHS


def _scalar_type(address: int, default: str = "uint32_t") -> str:
    return {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}.get(
        _access_widths().get(address, 0), default,
    )


def _oracle_addresses() -> set[int]:
    found: set[int] = set()
    for scenario in _load_jsonl(ROOT / "oracles.jsonl"):
        entry = scenario.get("entry") or {}
        if entry.get("scope") != "resolved-address":
            continue
        checks = scenario.get("checks") or []
        has_r10 = any(
            check.get("kind") == "register" and check.get("register") == "r10"
            for check in checks
        )
        has_memory = any(check.get("kind") == "memory" for check in checks)
        has_event = any(check.get("kind") == "event-count" for check in checks)
        if has_event and not has_r10:
            continue
        if has_memory or has_r10:
            found.add(_address(entry["address"]))
    return found


def _prototype_names() -> set[str]:
    header = (ROOT / "include" / "camry.h").read_text(encoding="utf-8")
    return set(re.findall(
        r"^[A-Za-z_][A-Za-z0-9_ \t\*]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        header,
        flags=re.M,
    ))


def _self_call_count(row: dict) -> int:
    return sum(
        1
        for match in _CALL.finditer(_strip_comments(row["decompiled_c"]))
        if match.group(1) == row["name"]
    )


def _select_corpus(
    functions: list[dict],
    defined: set[str],
    banned: set[str],
    roots: set[int] | None = None,
) -> dict[int, dict]:
    by_addr = {int(row["entry_addr"], 16): row for row in functions}
    eligible: dict[str, dict] = {}
    for row in functions:
        if row["name"] in defined or row["name"] in banned or not _eligible(row["decompiled_c"]):
            continue
        current = eligible.get(row["name"])
        # Same-name tail calls are `mov target; jmp [r12]` and decompile as a self-call.
        # Keep the body that does not call itself.
        if current is not None and _self_call_count(row) > _self_call_count(current):
            continue
        eligible[row["name"]] = row
    changed = True
    while changed:
        changed = False
        for name in list(eligible):
            for callee in _callees(eligible[name]["decompiled_c"]):
                if callee in defined or callee in _SKIP_CALLS:
                    continue
                if callee not in eligible:
                    del eligible[name]
                    changed = True
                    break
    origin = _oracle_addresses() if roots is None else roots
    stack = [
        by_addr[addr]["name"]
        for addr in sorted(origin)
        if addr in by_addr and by_addr[addr]["name"] in eligible
    ]
    reachable: set[str] = set()
    while stack:
        name = stack.pop()
        if name in reachable or name not in eligible:
            continue
        reachable.add(name)
        for callee in _callees(eligible[name]["decompiled_c"]):
            if callee in eligible and callee not in reachable:
                stack.append(callee)
    return {
        int(eligible[name]["entry_addr"], 16): eligible[name]
        for name in reachable
    }


def _render_corpus(selected: dict[int, dict]) -> str:
    bodies = {addr: _rewrite_body(row["decompiled_c"]) for addr, row in selected.items()}
    text = "\n".join(bodies.values())
    registers = _machine_registers()
    data = _data_symbols()
    lines = [
        "/* Corpus C from the Ghidra decompiler. Generated by tools/decomp corpus. */",
        '#include "camry.h"',
        '#include "ghidra_types.h"',
        "",
    ]
    types = set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\*", text))
    for _name, (_addr, ctype, _is_array) in _data_layouts().items():
        if re.fullmatch(r"[A-Z][A-Za-z0-9_]*", ctype):
            types.add(ctype)
    for name in sorted(types):
        if name in _PRIMITIVE_TYPES or name in registers or name in data:
            continue
        lines.append(f"typedef struct {name} {name};")
    if types:
        lines.append("")
    widths = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}
    for name, row in sorted(registers.items()):
        if re.search(rf"\b{name}\b", text) is None:
            continue
        ctype = widths.get(int(row.get("size") or 4), "uint32_t")
        lines.append(
            f"#define {name} (*((volatile {ctype} *)camry_host_ptr(0x{int(row['address']):x}u)))"
        )
    for name, (addr, ctype, is_array) in sorted(_data_layouts().items()):
        if name in registers or re.search(rf"\b{name}\b", text) is None:
            continue
        if any(row["name"] == name for row in selected.values()):
            continue
        if is_array:
            lines.append(
                f"#define {name} ((volatile {ctype} *)camry_host_ptr(0x{addr:x}u))"
            )
        else:
            lines.append(
                f"#define {name} (*((volatile {ctype} *)camry_host_ptr(0x{addr:x}u)))"
            )
    for match in sorted(set(re.findall(r"\b((?:DAT|UNK)_[0-9A-Fa-f]+)\b", text))):
        addr = int(match.split("_", 1)[1], 16)
        lines.append(
            f"#define {match} (*((volatile {_scalar_type(addr)} *)camry_host_ptr(0x{addr:x}u)))"
        )
    for match, addr_text in sorted(set(re.findall(
        r"\b(PTR_[A-Za-z0-9_]*_([0-9A-Fa-f]+))\b", text,
    ))):
        lines.append(
            f"#define {match} (*((volatile uint32_t *)camry_host_ptr(0x{int(addr_text, 16):x}u)))"
        )
    lines.append("")
    for addr in sorted(selected):
        lines.append(_c_signature(selected[addr]["decompiled_c"]) + ";")
    lines.append("")
    for addr in sorted(bodies):
        lines.append(bodies[addr])
        if not bodies[addr].endswith("\n"):
            lines.append("")
    return "\n".join(lines) + "\n"


def _function_at_line(selected: dict[int, dict], rendered: str, line_number: int) -> str | None:
    lines = rendered.splitlines()
    owners: list[tuple[int, str]] = []
    for row in selected.values():
        needle = row["name"] + "("
        for index, line in enumerate(lines, 1):
            if needle in line and not line.endswith(";"):
                owners.append((index, row["name"]))
                break
    owners.sort()
    found = None
    for start, name in owners:
        if start <= line_number:
            found = name
        else:
            break
    return found


def _compile_corpus(destination: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "cc", "-std=c11", "-c", "-O2", "-Wall", "-Wextra", "-Werror", "-fwrapv",
            "-Wno-unused-variable", "-Wno-unused-parameter",
            "-Wno-unused-function", "-Wno-unused-label",
            "-Wno-pointer-to-int-cast", "-Wno-int-to-pointer-cast",
            "-Wno-bitwise-op-parentheses",             "-Wno-sign-compare", "-Wno-parentheses",
            "-Wno-pointer-sign", "-Wno-incompatible-pointer-types",
            "-Wno-unused-but-set-variable",
            "-DCAMRY_HOST", "-I", str(ROOT / "include"),
            "-o", "/dev/null", str(destination),
        ],
        text=True,
        capture_output=True,
    )


_CC_FLAGS = [
    "-std=c11", "-c", "-O2", "-Wall", "-Wextra", "-Werror", "-fwrapv",
    "-Wno-unused-variable", "-Wno-unused-parameter",
    "-Wno-unused-function", "-Wno-unused-label",
    "-Wno-pointer-to-int-cast", "-Wno-int-to-pointer-cast",
    "-Wno-bitwise-op-parentheses", "-Wno-sign-compare", "-Wno-parentheses",
    "-Wno-pointer-sign", "-Wno-incompatible-pointer-types",
    "-Wno-unused-but-set-variable",
    "-ferror-limit=0",
    "-DCAMRY_HOST",
]
_CHECKED_STATUS = {"equivalent", "byte-matched"}
_TREE = ROOT / "src" / "all"


def _prefer_bodies(functions: list[dict]) -> dict[str, dict]:
    chosen: dict[str, dict] = {}
    for row in functions:
        current = chosen.get(row["name"])
        if current is not None and _self_call_count(row) > _self_call_count(current):
            continue
        chosen[row["name"]] = row
    return chosen


def _failure_class(message: str) -> str:
    match = re.search(r"use of undeclared identifier '([^']+)'", message)
    if match:
        ident = match.group(1)
        if re.fullmatch(r"unaff_\w+", ident):
            shape = "unaff_*"
        elif re.fullmatch(r"extraout_\w+", ident):
            shape = "extraout_*"
        elif re.fullmatch(r"in_r\d+", ident):
            shape = "in_r*"
        elif ident.startswith("Ram"):
            shape = "Ram*"
        elif ident.startswith(("CONCAT", "SUB", "SBORROW", "OVERFLOW")):
            shape = ident.split("_", 1)[0] + "*"
        elif ident.startswith("in_"):
            shape = ident
        else:
            shape = ident
        return f"undeclared identifier {shape}"
    text = re.sub(r"\(aka '[^']*'\)", "", message)
    text = re.sub(r"'[^']*'", "'…'", text)
    text = re.sub(r"\b0x[0-9A-Fa-f]+\b", "N", text)
    text = re.sub(r"\b\d+\b", "N", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:200]


def _common_header(text: str, signatures: dict[str, str]) -> str:
    registers = _machine_registers()
    data = _data_symbols()
    function_names = set(signatures)
    lines = [
        "/* Generated by tools/decomp corpus. */",
        '#include "camry.h"',
        '#include "ghidra_types.h"',
        "",
    ]
    types = set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\*", text))
    for _name, (_addr, ctype, _is_array) in _data_layouts().items():
        if re.fullmatch(r"[A-Z][A-Za-z0-9_]*", ctype):
            types.add(ctype)
    emitted = False
    for name in sorted(types):
        if name in _PRIMITIVE_TYPES or name in registers or name in data or name in function_names:
            continue
        lines.append(f"typedef struct {name} {name};")
        emitted = True
    if emitted:
        lines.append("")
    widths = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}
    for name, row in sorted(registers.items()):
        if name in function_names or re.search(rf"\b{name}\b", text) is None:
            continue
        ctype = widths.get(int(row.get("size") or 4), "uint32_t")
        lines.append(
            f"#define {name} (*((volatile {ctype} *)camry_host_ptr(0x{int(row['address']):x}u)))"
        )
    for name, (addr, ctype, is_array) in sorted(_data_layouts().items()):
        if name in registers or name in function_names or re.search(rf"\b{name}\b", text) is None:
            continue
        if is_array:
            lines.append(f"#define {name} ((volatile {ctype} *)camry_host_ptr(0x{addr:x}u))")
        else:
            lines.append(
                f"#define {name} (*((volatile {ctype} *)camry_host_ptr(0x{addr:x}u)))"
            )
    for match in sorted(set(re.findall(r"\b((?:DAT|UNK)_[0-9A-Fa-f]+)\b", text))):
        addr = int(match.split("_", 1)[1], 16)
        lines.append(
            f"#define {match} (*((volatile {_scalar_type(addr)} *)camry_host_ptr(0x{addr:x}u)))"
        )
    for match, addr_text in sorted(set(re.findall(
        r"\b(PTR_[A-Za-z0-9_]*_([0-9A-Fa-f]+))\b", text,
    ))):
        lines.append(
            f"#define {match} (*((volatile uint32_t *)camry_host_ptr(0x{int(addr_text, 16):x}u)))"
        )
    lines.append("")
    for name in sorted(signatures):
        lines.append(signatures[name] + ";")
    lines.append("")
    return "\n".join(lines) + "\n"


def _compile_file(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["cc", *_CC_FLAGS, "-I", str(ROOT / "include"), "-o", "/dev/null", str(path)],
        text=True,
        capture_output=True,
    )


def _isolate_errors(name: str, body: str, directory: Path) -> list[str]:
    path = directory / f"one-{name}.c"
    path.write_text('#include "common.h"\n\n' + body, encoding="utf-8")
    result = _compile_file(path)
    path.unlink(missing_ok=True)
    if result.returncode == 0:
        return []
    messages = [
        line.split("error:", 1)[1].strip()
        for line in (result.stderr or "").splitlines()
        if "error:" in line
    ]
    return messages or [(result.stderr or "compile failed")[:300]]


def _shard_errors(
    path: Path, selected: dict[int, dict], rendered: str,
) -> dict[str, list[str]]:
    result = _compile_file(path)
    found: dict[str, list[str]] = {}
    if result.returncode == 0:
        return found
    for line in (result.stderr or "").splitlines():
        if "error:" not in line:
            continue
        match = re.search(rf"{re.escape(path.name)}:(\d+):", line)
        if match is None:
            found.setdefault("", []).append(line.split("error:", 1)[1].strip())
            continue
        name = _function_at_line(selected, rendered, int(match.group(1)))
        message = line.split("error:", 1)[1].strip()
        found.setdefault(name or "", []).append(message)
    if result.returncode != 0 and not found:
        found[""] = [(result.stderr or "compile failed")[:500]]
    return found


def _write_statuses(compiled_names: set[str]) -> tuple[int, int, int]:
    path = ROOT / "matched.jsonl"
    kept: list[str] = []
    kept_addrs: set[int] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") in _CHECKED_STATUS:
            kept.append(line)
            kept_addrs.add(_address(row["addr"]))
    hand = _prototype_names()
    extra: list[dict] = []
    converted = 0
    unconvertible = 0
    for symbol in load_symbols():
        addr = _address(symbol["addr"])
        if addr in kept_addrs:
            continue
        status = "converted" if symbol["name"] in compiled_names or symbol["name"] in hand else "unconvertible"
        if status == "converted":
            converted += 1
        else:
            unconvertible += 1
        extra.append({
            "addr": hex(addr),
            "name": symbol["name"],
            "status": status,
        })
    extra.sort(key=lambda row: int(row["addr"], 16))
    payload = kept + [
        json.dumps(row, separators=(", ", ": "))
        for row in extra
    ]
    path.write_text("\n".join(payload) + "\n", encoding="utf-8")
    return len(kept), converted, unconvertible


def _compile_tree(functions: list[dict]) -> tuple[set[str], Counter[str], list[str]]:
    hand = _prototype_names()
    chosen = _prefer_bodies(functions)
    rewritten: dict[str, str] = {}
    signatures: dict[str, str] = {}
    rows_by_name: dict[str, dict] = {}
    failed_rewrite: list[str] = []
    for name, row in chosen.items():
        if name in hand:
            continue
        try:
            body = _rewrite_body(row["decompiled_c"])
            signatures[name] = _c_signature(body)
        except (ValueError, IndexError, KeyError) as exc:
            failed_rewrite.append(f"{name} {type(exc).__name__}")
            continue
        rewritten[name] = body
        rows_by_name[name] = row
    if not rewritten:
        return set(), Counter({"rewrite failed": len(failed_rewrite)}), failed_rewrite

    def shards_of(names: set[str]) -> dict[str, dict[int, dict]]:
        grouped: dict[str, dict[int, dict]] = {}
        for name in names:
            row = rows_by_name[name]
            addr = int(row["entry_addr"], 16)
            grouped.setdefault(f"{addr >> 14:03x}", {})[addr] = row
        return grouped

    def prototype_at(header: str, line_number: int) -> str | None:
        rows = header.splitlines()
        if line_number < 1 or line_number > len(rows):
            return None
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", rows[line_number - 1])
        if match is None or match.group(1) not in active:
            return None
        return match.group(1)

    with tempfile.TemporaryDirectory(prefix="camry-tree-") as tmp:
        root = Path(tmp)
        active = set(rewritten)
        hidden: set[str] = set()
        blame: dict[str, list[str]] = {}
        header_errors: list[str] = []
        text = "\n".join(rewritten[name] for name in sorted(rewritten))
        for _round in range(8):
            header_errors = []
            print(f"compile {_round + 1} {len(active)}")
            header = _common_header(
                text, {name: signatures[name] for name in signatures if name not in hidden},
            )
            (root / "common.h").write_text(header, encoding="utf-8")
            probe = root / "probe.c"
            probe.write_text('#include "common.h"\n', encoding="utf-8")
            probe_result = _compile_file(probe)
            dropped: set[str] = set()
            if probe_result.returncode != 0:
                header_errors = []
                for line in (probe_result.stderr or "").splitlines():
                    if "error:" not in line:
                        continue
                    message = line.split("error:", 1)[1].strip()
                    match = re.search(r"common\.h:(\d+):", line)
                    name = prototype_at(header, int(match.group(1))) if match else None
                    if name:
                        dropped.add(name)
                        hidden.add(name)
                        blame[name] = [message]
                    else:
                        header_errors.append(message)
                if dropped:
                    active -= dropped
                    print(f"dropped {len(dropped)}")
                    continue
                break
            grouped = shards_of(active - dropped)
            rendered_shards: dict[str, tuple[Path, dict[int, dict], str]] = {}
            for shard, selected in grouped.items():
                parts = ['#include "common.h"', ""]
                for addr in sorted(selected):
                    parts.append(rewritten[selected[addr]["name"]])
                    if not rewritten[selected[addr]["name"]].endswith("\n"):
                        parts.append("")
                rendered = "\n".join(parts) + "\n"
                path = root / f"{shard}.c"
                path.write_text(rendered, encoding="utf-8")
                rendered_shards[shard] = (path, selected, rendered)
            suspects: list[tuple[str, str]] = []
            shard_blame: dict[str, list[str]] = {}
            with ThreadPoolExecutor(max_workers=8) as pool:
                compiled = pool.map(
                    lambda item: (item[0], _shard_errors(*item[1])),
                    rendered_shards.items(),
                )
                for shard, errors in compiled:
                    selected = rendered_shards[shard][1]
                    if not errors:
                        continue
                    if set(errors) == {""}:
                        header_errors.extend(errors[""])
                        continue
                    for name, messages in errors.items():
                        if name:
                            shard_blame.setdefault(name, []).extend(messages)
                    for row in selected.values():
                        suspects.append((row["name"], rewritten[row["name"]]))
            if header_errors and not suspects and not dropped:
                break
            print(f"isolate {len(suspects)}")
            with ThreadPoolExecutor(max_workers=8) as pool:
                isolated = pool.map(
                    lambda item: (item[0], _isolate_errors(item[0], item[1], root)),
                    suspects,
                )
                for name, messages in isolated:
                    if messages:
                        dropped.add(name)
                        blame[name] = messages
            if not dropped:
                for name, messages in shard_blame.items():
                    if name in active:
                        dropped.add(name)
                        blame[name] = messages
            header_errors = []
            if not dropped:
                break
            active -= dropped
            print(f"dropped {len(dropped)}")
        else:
            header_errors.append("compile did not converge")
        classes: Counter[str] = Counter()
        if failed_rewrite:
            classes["rewrite failed"] = len(failed_rewrite)
        for name, messages in blame.items():
            if name in active or not messages:
                continue
            for kind in {_failure_class(message) for message in messages}:
                classes[kind] += 1
        if header_errors:
            for message in header_errors[:12]:
                print(f"header {message}")
            return set(), classes, failed_rewrite + [f"header {message}" for message in header_errors[:12]]
        _TREE.mkdir(parents=True, exist_ok=True)
        for stale in _TREE.glob("*"):
            stale.unlink()
        (_TREE / "common.h").write_text(
            _common_header(
                text, {name: signatures[name] for name in signatures if name not in hidden},
            ),
            encoding="utf-8",
        )
        for shard, selected in shards_of(active).items():
            parts = ['#include "common.h"', ""]
            for addr in sorted(selected):
                parts.append(rewritten[selected[addr]["name"]])
            (_TREE / f"{shard}.c").write_text("\n".join(parts) + "\n", encoding="utf-8")
        return active, classes, failed_rewrite


def cmd_corpus(_args: argparse.Namespace) -> int:
    from tools.project.pseudo import load_corpus

    metadata = resolve_target(TARGET)[1]
    _meta, functions = load_corpus(REPO_ROOT / metadata["decompiler_corpus"])
    print(f"functions {len(functions)}")
    compiled, classes, failures = _compile_tree(functions)
    header_failed = any(item.startswith("header ") for item in failures)
    if header_failed:
        verified = converted = unconvertible = 0
    else:
        verified, converted, unconvertible = _write_statuses(compiled)
    print(f"compiled {len(compiled)}")
    print(f"oracle-verified {verified}")
    print(f"converted-unverified {converted}")
    print(f"unconvertible {unconvertible}")
    if failures:
        print(f"rewrite-failed {len(failures)}")
    print("failure classes:")
    for kind, count in classes.most_common(30):
        print(f"  {count:5d}  {kind}")
    return 0 if not failures or compiled else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    identity = sub.add_parser("identity", help="link an image identical to CodeFlash")
    identity.add_argument("--output", help="write the linked image here")
    identity.set_defaults(func=cmd_identity)
    status = sub.add_parser("status", help="print image and matched-function counts")
    status.set_defaults(func=cmd_status)
    corpus = sub.add_parser("corpus", help="compile every decompiler body and rank the failures")
    corpus.set_defaults(func=cmd_corpus)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
