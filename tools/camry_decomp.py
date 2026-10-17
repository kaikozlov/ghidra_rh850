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
        if not text.endswith(";") or "(" in text or "*" not in text or text.startswith("/*"):
            continue
        first = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text)
        first_word = first.group(0) if first else ""
        is_decl = first_word in _PRIMITIVE_TYPES | {"code", "enum", "sbyte"} or (
            re.fullmatch(r"[A-Z][A-Za-z0-9_]*", first_word) is not None
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


_NULL_POINTER = re.compile(
    r"^\(\s*[A-Za-z_][A-Za-z0-9_ \t]*\*\s*\)\s*(?:0x0+|0+)\s*$"
)


def _is_null_pointer_expr(expr: str) -> bool:
    """`(void *)0x0` is a null pointer constant, not a firmware address."""
    text = expr.strip()
    while text.startswith("(") and text.endswith(")"):
        try:
            end = _match_paren(text, 0)
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


def _match_bracket_back(code: str, closing: int) -> int:
    depth = 0
    for index in range(closing, -1, -1):
        if code[index] == "]":
            depth += 1
        elif code[index] == "[":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unbalanced bracket")


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


# Peripheral windows whose Ghidra type is wider than the machine-register scalar.
# Field offsets are the committed ApplyP1MSfrTypes layouts (stride 0x20 message
# slots, CFSTS bit 3). Spelling the field name would expand the SFR macro.
_DEVICE_FIELDS: dict[int, tuple[int, dict[str, tuple[int, str]]]] = {
    0xFFD24000: (0x20, {
        "CFDTMID": (0, "uint32_t"),
        "CFDTMPTR": (4, "uint32_t"),
        "CFDTMFDCTR": (8, "uint32_t"),
        "CFDTMDF0": (12, "uint32_t"),
        "CFDTMDF1": (16, "uint32_t"),
    }),
    0xFFD24200: (0x20, {
        "CFDTMID": (0, "uint32_t"),
        "CFDTMPTR": (4, "uint32_t"),
        "CFDTMFDCTR": (8, "uint32_t"),
        "CFDTMDF0": (12, "uint32_t"),
        "CFDTMDF1": (16, "uint32_t"),
    }),
    0xFFD23400: (0x20, {
        "CFID": (0, "uint32_t"),
        "CFPTR": (4, "uint32_t"),
        "CFFDCSTS": (8, "uint32_t"),
        "CFDF0": (12, "uint32_t"),
        "CFDF1": (16, "uint32_t"),
    }),
    0xFFD23580: (0x20, {
        "CFID": (0, "uint32_t"),
        "CFPTR": (4, "uint32_t"),
        "CFFDCSTS": (8, "uint32_t"),
        "CFDF0": (12, "uint32_t"),
        "CFDF1": (16, "uint32_t"),
    }),
}
_DEVICE_BITS: dict[int, tuple[int, dict[str, int]]] = {
    0xFFD20178: (4, {"status_b3": 3}),
    0xFFD20184: (4, {"status_b3": 3}),
}
# C type and element stride for `&label + index` on a recovered peripheral struct.
_DEVICE_TYPES: dict[int, tuple[str, int]] = {
    0xFFD24000: ("RSCFD_TxMessageBuffer", 0x20),
    0xFFD24200: ("RSCFD_TxMessageBuffer", 0x20),
    0xFFD23400: ("RSCFD_CommonFifoFrame", 0x20),
    0xFFD23580: ("RSCFD_CommonFifoFrame", 0x20),
    0xFFD20178: ("RSCFD_CFSTS", 4),
    0xFFD20184: ("RSCFD_CFSTS", 4),
}
_DEVICE_STRUCT_TEXT = """
typedef struct RSCFD_TxMessageBuffer RSCFD_TxMessageBuffer;
struct RSCFD_TxMessageBuffer {
    uint32_t word0;
    uint32_t word1;
    uint32_t word2;
    uint32_t word3;
    uint32_t word4;
    uint8_t reserved_14_1f[12];
};
typedef struct RSCFD_CommonFifoFrame RSCFD_CommonFifoFrame;
struct RSCFD_CommonFifoFrame {
    uint32_t word0;
    uint32_t word1;
    uint32_t word2;
    uint32_t word3;
    uint32_t word4;
    uint8_t reserved_14_1f[12];
};
typedef struct RSCFD_CFSTS RSCFD_CFSTS;
struct RSCFD_CFSTS {
    uint32_t reserved_0_2 : 3;
    uint32_t status_b3 : 1;
    uint32_t reserved_4_31 : 28;
};
"""
_DEVICE_STRUCT_NAMES = {
    "RSCFD_TxMessageBuffer", "RSCFD_CommonFifoFrame", "RSCFD_CFSTS",
}
_SCALAR_WIDTHS = {
    "uint8_t": 1, "int8_t": 1, "uint16_t": 2, "int16_t": 2,
    "uint32_t": 4, "int32_t": 4, "uint64_t": 8,
}
_WIDTH_CTYPES = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t", 8: "uint64_t"}


def _symbol_address(name: str) -> int | None:
    found = _absolute_names().get(name)
    if found is not None:
        return found
    match = re.fullmatch(r"(?:DAT|UNK)_([0-9A-Fa-f]+)", name)
    if match:
        return int(match.group(1), 16)
    return None


def _volatile_at(address_expr: str, ctype: str) -> str:
    return f"(*((volatile {ctype} *)camry_host_ptr((uint32_t)({address_expr}))))"


def _scaled_address(base: int, index: str, stride: int, offset: int) -> str:
    expr = f"0x{base:x}u + (uint32_t)({index}) * {stride}u"
    if offset:
        expr += f" + {offset}u"
    return expr


def _trailing_field(code: str, end: int) -> tuple[str | None, int]:
    nxt = _skip_space(code, end + 1)
    match = re.match(r"\.\s*([A-Za-z_][A-Za-z0-9_]*)", code[nxt:])
    if match is None:
        return None, end
    return match.group(1), nxt + match.end()


def _symbol_element(name: str) -> tuple[str, int] | None:
    """Scalar width of a data symbol or machine register. Structs are separate."""
    layout = _data_layouts().get(name)
    if layout is not None:
        _addr, ctype, _array = layout
        if ctype in _struct_rows():
            return None
        width = _SCALAR_WIDTHS.get(ctype)
        if width is None:
            return None
        return _WIDTH_CTYPES[width], width
    row = _machine_registers().get(name)
    if row is None:
        return None
    width = int(row.get("size") or 0)
    ctype = _WIDTH_CTYPES.get(width)
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
        spec = _DEVICE_TYPES.get(address) if address is not None else None
        if spec is None:
            continue
        expr_end = _scan_side(code, match.end(), 1, ",;)")
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
    structs = _struct_rows()
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        name = match.group(1)
        try:
            end = _match_bracket(code, match.end() - 1)
        except ValueError:
            continue
        index = _rewrite_symbol_indexes(code[match.end():end])
        address = _symbol_address(name)
        if address is None:
            continue
        field, field_end = _trailing_field(code, end)
        device = _DEVICE_FIELDS.get(address)
        bits = _DEVICE_BITS.get(address)
        replacement = None
        consumed = end + 1
        if device is not None and field is not None and field in device[1]:
            offset, ctype = device[1][field]
            replacement = _volatile_at(
                _scaled_address(address, index, device[0], offset), ctype,
            )
            consumed = field_end
        elif bits is not None and field is not None and field in bits[1]:
            word = _volatile_at(_scaled_address(address, index, bits[0], 0), "uint32_t")
            bit = bits[1][field]
            replacement = f"((({word}) >> {bit}) & 1u)"
            consumed = field_end
        elif device is not None and field is not None:
            continue
        elif bits is not None and field is not None:
            continue
        else:
            layout = _data_layouts().get(name)
            if layout is not None and layout[1] in structs:
                replacement = (
                    f"((volatile {layout[1]} *)camry_host_ptr(0x{address:x}u))[{index}]"
                )
            else:
                element = _symbol_element(name)
                if element is None or field is not None:
                    continue
                ctype, width = element
                replacement = _volatile_at(
                    _scaled_address(address, index, width, 0), ctype,
                )
        pieces.append(code[cursor:match.start()])
        pieces.append(replacement)
        cursor = consumed
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


_INT_TYPES = {
    "unsigned int", "int", "uint", "undefined4", "ulong", "long", "uint32_t",
    "uint16_t", "uint8_t", "int32_t", "int16_t", "int8_t", "undefined2",
    "undefined1", "undefined", "ushort", "byte", "uchar", "short", "char",
    "unsigned", "signed", "bool", "code",
}
_DATA_ARRAYS: set[str] | None = None
_DATA_SCALARS: set[str] | None = None


def _data_name_kinds() -> tuple[set[str], set[str]]:
    global _DATA_ARRAYS, _DATA_SCALARS
    if _DATA_ARRAYS is None or _DATA_SCALARS is None:
        arrays: set[str] = set()
        scalars: set[str] = set()
        for name, (_addr, _ctype, is_array) in _data_layouts().items():
            (arrays if is_array else scalars).add(name)
        scalars.update(_machine_registers())
        _DATA_ARRAYS = arrays
        _DATA_SCALARS = scalars
    return _DATA_ARRAYS, _DATA_SCALARS


def _declared_integers(signature: str, code: str) -> set[str]:
    names: set[str] = set()
    opening = signature.find("(")
    closing = signature.rfind(")")
    if 0 <= opening < closing:
        body = signature[opening + 1:closing].strip()
        if body and body != "void":
            for part in _split_args(body):
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
        for part in _split_args(type_match.group(1)):
            if "*" in part or "[" in part:
                continue
            left = part.split("=", 1)[0].strip()
            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)", left)
            if match:
                names.add(match.group(1))
    return names


def _kind_context(signature: str, code: str, pointers: set[str] | None = None):
    """Classify an expression as pointer, integer, null, or unknown."""
    pointers = _pointer_names(signature, code) if pointers is None else pointers
    arrays = set(re.findall(
        r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\[", signature + "\n" + code,
    ))
    data_arrays, data_scalars = _data_name_kinds()
    arrays |= data_arrays
    doubles = set(re.findall(
        r"\*\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)", signature + "\n" + code,
    ))
    integers = (_declared_integers(signature, code) | data_scalars) - pointers - arrays - doubles
    functions = set(_function_entries())
    var_structs = _struct_var_types(signature + "\n" + code)
    field_kinds = _scalar_field_kinds()

    def kind(expr: str) -> str:
        return _expr_kind(
            expr.strip(),
            pointers=pointers,
            arrays=arrays,
            integers=integers,
            functions=functions,
            doubles=doubles,
            var_structs=var_structs,
            field_kinds=field_kinds,
        )

    return kind


def _fully_wrapped(text: str) -> bool:
    if not text.startswith("(") or not text.endswith(")"):
        return False
    try:
        return _match_paren(text, 0) == len(text) - 1
    except ValueError:
        return False


def _is_int_type(text: str) -> bool:
    collapsed = " ".join(text.replace("*", " ").split())
    return collapsed in _INT_TYPES or collapsed in {"unsigned int", "signed int", "unsigned long", "signed long"}


def _is_pointer_type(text: str) -> bool:
    return text.rstrip().endswith("*") and _looks_like_type(text)


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
                ops.append((index, char))
        index += 1
    return ops


def _expr_kind(
    text: str,
    *,
    pointers: set[str],
    arrays: set[str],
    integers: set[str],
    functions: set[str],
    doubles: set[str],
    var_structs: dict[str, str] | None = None,
    field_kinds: dict[tuple[str, str], str] | None = None,
) -> str:
    text = text.strip()
    if not text:
        return "unknown"
    while _fully_wrapped(text):
        inner = text[1:-1].strip()
        if _is_pointer_type(inner) or _is_int_type(inner):
            break
        text = inner
    ops = _binary_ops(text)
    if ops:
        parts = [text[:ops[0][0]]]
        for (start, _op), (end, _next) in zip(ops, ops[1:] + [(len(text), "")]):
            parts.append(text[start + len(_op):end])
        kinds = [
            _expr_kind(
                part,
                pointers=pointers,
                arrays=arrays,
                integers=integers,
                functions=functions,
                doubles=doubles,
                var_structs=var_structs,
                field_kinds=field_kinds,
            )
            for part in parts
        ]
        folded = kinds[0]
        for (_start, op), right in zip(ops, kinds[1:]):
            folded = _fold_kind(op, folded, right)
        return folded
    if text[:1] in "-+~!":
        inner = _expr_kind(
            text[1:],
            pointers=pointers,
            arrays=arrays,
            integers=integers,
            functions=functions,
            doubles=doubles,
            var_structs=var_structs,
            field_kinds=field_kinds,
        )
        if text[0] == "!":
            return "integer" if inner != "unknown" else "unknown"
        if inner == "pointer":
            return "unknown"
        return "integer" if inner == "null" else inner
    if re.fullmatch(r"0x0+u?|0u?|NULL", text):
        return "null"
    if re.fullmatch(r"0x[0-9A-Fa-f]+u?|\d+u?", text):
        return "integer"
    if text.startswith("&"):
        return "pointer"
    if text.startswith("camry_host_ptr"):
        return "pointer"
    if text.startswith("camry_host_addr"):
        return "integer"
    if text.startswith("*"):
        inner = text[1:].strip()
        if _fully_wrapped(inner):
            inner = inner[1:-1].strip()
        if inner.startswith("("):
            try:
                end = _match_paren(inner, 0)
            except ValueError:
                return "unknown"
            stars = inner[1:end].count("*")
            if stars >= 2:
                return "pointer"
            if stars == 1:
                return "integer"
        return "unknown"
    if text.startswith("("):
        try:
            end = _match_paren(text, 0)
        except ValueError:
            return "unknown"
        inner = " ".join(text[1:end].split())
        if _is_pointer_type(inner):
            return "pointer"
        if _is_int_type(inner):
            return "integer"
        return "unknown"
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text)
    if match is None:
        return "unknown"
    name = match.group(0)
    rest = text[match.end():].lstrip()
    field_kind = _scalar_field_kind(name, rest, var_structs, field_kinds)
    if field_kind is not None:
        return field_kind
    if name in functions and name not in pointers and name not in integers:
        return "pointer" if not rest else "unknown"
    # A uint32 slot macro is the firmware pointer word, even when the
    # decompiler also subscripts it. `(int)DAT` is that word, not a host pointer.
    if not rest and name in _uint32_slot_names():
        return "integer"
    if name in pointers or name in arrays or name in integers or name.startswith(("DAT_", "UNK_", "PTR_")):
        if not rest:
            if name in pointers or name in arrays:
                return "pointer"
            return "integer"
        if rest.startswith((".", "->")):
            return "unknown"
        if re.fullmatch(r"(?:\s*\[[^\[\]]*\])+", rest):
            if name in doubles:
                return "pointer" if rest.count("[") == 1 else "integer"
            if name in arrays and name not in pointers:
                return "unknown"
            return "integer"
        return "unknown"
    return "unknown"


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
    for part in _split_args(body):
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


def _hand_param_types() -> dict[str, list[str]]:
    header = _strip_comments((ROOT / "include" / "camry.h").read_text(encoding="utf-8"))
    header = re.sub(r"static inline\b.*?\{.*?\n\}", "", header, flags=re.S)
    flat = re.sub(r"\s+", " ", header)
    found: dict[str, list[str]] = {}
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(([^()]*)\)\s*;", flat):
        found[match.group(1)] = _param_type_list(match.group(2))
    found["camry_host_addr"] = ["const void *"]
    return found


def _rewrite_pointer_arguments(code: str, param_types: dict[str, list[str]]) -> str:
    """Pass a firmware integer to a pointer parameter as a host pointer."""
    brace = _opening_brace(code)
    if brace < 0:
        return code
    signature = _c_signature(code)
    kind = _kind_context(signature, code)

    def rewrite(text: str) -> str:
        pieces: list[str] = []
        cursor = 0
        for match in _CALL.finditer(text):
            if match.start() < cursor or match.group(1) in _SKIP_CALLS:
                continue
            try:
                close = _match_paren(text, match.end() - 1)
            except ValueError:
                continue
            inner = rewrite(text[match.end():close])
            types = param_types.get(match.group(1))
            if types is not None:
                args = _split_args(inner)
                if len(args) == 1 and not args[0].strip():
                    args = []
                extra = [arg for arg in args[len(types):] if arg.strip()]
                args = args[:len(types)]
                rewritten_args: list[str] = []
                wrapped = False
                for index, arg in enumerate(args):
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
    kind = _kind_context(_c_signature(code), code, pointers)
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
        # `(uint)pdu->length` casts the field. The base alone is not the operand.
        while True:
            arrow = _skip_space(code, end)
            if code.startswith("->", arrow):
                step = 2
            elif arrow < len(code) and code[arrow] == ".":
                step = 1
            else:
                break
            field_at = _skip_space(code, arrow + step)
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
            end = _match_bracket(code, match.end() - 1)
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


def _is_type_cast(inner: str) -> bool:
    parts = [
        part for part in inner.replace("*", " ").split()
        if part not in {"const", "volatile", "unsigned", "signed", "struct"}
    ]
    return len(parts) == 1 and parts[0] in _INT_TYPES


def _postfix_end(code: str, index: int) -> int:
    while True:
        index = _skip_space(code, index)
        if index >= len(code):
            return index
        if code[index] == "(":
            index = _match_paren(code, index) + 1
            continue
        if code[index] == "[":
            index = _match_bracket(code, index) + 1
            continue
        arrow = code.startswith("->", index)
        if arrow or (code[index] == "." and not code.startswith("..", index)):
            start = _skip_space(code, index + (2 if arrow else 1))
            if start < len(code) and (code[start].isalpha() or code[start] == "_"):
                index = _operand_end(code, start)
                continue
        return index


def _unary_operand_end(code: str, index: int) -> int | None:
    """End of the operand after a `(integer-type)` cast."""
    index = _skip_space(code, index)
    if index >= len(code):
        return None
    if code[index] in "*&":
        return _unary_operand_end(code, index + 1)
    if code[index] == "(":
        end = _match_paren(code, index) + 1
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


def _rewrite_int_to_pointer(code: str, pointers: set[str]) -> str:
    # `*(int *)SLOT` is the word at that firmware address. Folding it first
    # keeps an outer `(char *)(word + index)` from hiding the load.
    code = _rewrite_slot_word_derefs(code)
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
            inner = code[after + 1:end - 1]
            if _is_type_cast(inner):
                operand_end = _unary_operand_end(code, end)
                if operand_end is None or operand_end <= end:
                    search = star + 2
                    continue
                expr = code[after:operand_end].strip()
                end = operand_end
            else:
                expr = inner
        elif code[after].isalpha() or code[after] == "_":
            end = _operand_end(code, after)
            # `(undefined *)name()` casts the return value. The call binds tighter
            # than the cast, so the name is not a firmware address.
            if _skip_space(code, end) < len(code) and code[_skip_space(code, end)] == "(":
                search = star + 2
                continue
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
        # `(undefined *)0xffffffff` beside a signed divide is the divisor word
        # compared with -1. A host pointer of that constant is not the cmp.
        literal = None if deref else _integer_constant_bits(expr)
        if literal is not None and _is_compare_operand(code, open_paren, end):
            pieces.append(code[cursor:open_paren])
            pieces.append(literal)
            cursor = end
            search = end
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


def _negative_constant(expr: str) -> int | None:
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
        if _match_paren(text, 0) != len(text) - 1:
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


def _narrow_lvalues(code: str) -> tuple[dict[str, int], dict[str, int]]:
    """Unsigned 8- and 16-bit lvalues. Wider unsigned values do not promote."""
    scalars: dict[str, int] = {}
    elements = {
        name: width
        for name, width in _pointer_element_widths(code).items()
        if width in (1, 2)
    }
    local = re.compile(
        r"\b(undefined1|undefined2|undefined|byte|uchar|ushort|char|code|bool)\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*;"
    )
    for match in local.finditer(code):
        scalars[match.group(2)] = 1 if match.group(1) not in {"undefined2", "ushort"} else 2
    for name, (_addr, ctype, is_array) in _data_layouts().items():
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
        width = _access_widths().get(int(match.group(1), 16))
        return width if width in (1, 2) else None
    match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[(.*)\]", text, flags=re.S)
    if match and elements.get(match.group(1)) in (1, 2):
        return elements[match.group(1)]
    return _deref_width(text)


def _cast_unsigned_narrow(
    raw: str, scalars: dict[str, int], elements: dict[str, int], constant: int,
) -> str | None:
    text = raw.strip()
    if _negative_constant(text) is not None:
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
        raw_left = _expr_before(code, index)
        left_at = index - len(raw_left)
        if left_at < cursor:
            index += len(op)
            continue
        right_end = _expr_end_bound(code, index + len(op))
        raw_right = code[index + len(op):right_end]
        left_constant = _negative_constant(raw_left.strip())
        right_constant = _negative_constant(raw_right.strip())
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
    rows = _struct_rows()
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
        base, stars, _array = _ghidra_base(found["type"])
        if stars or base not in rows:
            return None
        current = base
    return None


def _assignment_rhs(code: str, end: int) -> tuple[str, int] | None:
    nxt = _skip_space(code, end)
    if nxt >= len(code) or code[nxt] != "=" or code.startswith("==", nxt):
        return None
    rhs_at = nxt + 1
    semi = _scan_side(code, rhs_at, 1, ";")
    if semi >= len(code) or code[semi] != ";":
        return None
    return code[rhs_at:semi].strip(), semi


def _rewrite_bitfields(code: str) -> str:
    """Ghidra `name._offset_size_` is a byte overlay, not a struct field."""
    locals = _local_sizes(code)
    var_structs = _struct_var_types(code)
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
            stride = _struct_rows().get(struct, {}).get("size") if struct else None
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
                replacement = _volatile_at(expr, ctype)
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
                assigned = _assignment_rhs(code, match.end())
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


def _function_address(operand: str) -> str:
    """The address expression inside a Ghidra `*(code *)address` call."""
    text = operand.strip()
    while _fully_wrapped(text):
        inner = text[1:-1].strip()
        if _is_pointer_type(inner) or _is_int_type(inner):
            break
        text = inner
    match = re.match(r"^\(\s*code\s*\*\s*\)\s*", text)
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
        star = _skip_space(code, index + 1)
        if star >= len(code) or code[star] != "*":
            pieces.append(code[index])
            index += 1
            continue
        try:
            close = _match_paren(code, index)
        except ValueError:
            pieces.append(code[index])
            index += 1
            continue
        call = _skip_space(code, close + 1)
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
                call = _skip_space(code, close + 2)
                replace_at = index - 1
            if call >= len(code) or code[call] != "(":
                pieces.append(code[index])
                index += 1
                continue
        try:
            arg_end = _match_paren(code, call)
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
                end = _match_paren(inner, 0)
            except ValueError:
                return False
            if inner[1:end].count("*") >= 2:
                return True
        return False
    return _is_pointer_expr(text, pointers)


def _rewrite_pointer_compares(code: str, pointers: set[str]) -> str:
    """Compare unlike pointer types as host addresses.

    A stored routine compared with `f33_reset_vector`, and a RAM walk
    compared with a differently typed end pointer, are address compares.
    """
    entry_addresses = _function_entries()
    entries = set(entry_addresses)
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
        raw_left = _expr_before(code, index)
        left_at = index - len(raw_left)
        if left_at < cursor:
            index += len(op)
            continue
        right_end = _expr_end_bound(code, index + len(op))
        raw_right = code[index + len(op):right_end]
        left_pointer = _comparison_operand_is_pointer(raw_left, pointers, entries)
        right_pointer = _comparison_operand_is_pointer(raw_right, pointers, entries)
        if left_pointer and right_pointer:
            pieces.append(code[cursor:left_at])
            pieces.append(f"(uintptr_t)({raw_left.strip()})")
            pieces.append(op)
            pieces.append(f"(uintptr_t)({raw_right.strip()})")
            cursor = right_end
            index = right_end
            continue
        # A pointer slot holds a firmware address. Comparing that word with
        # `(void *)0x0` is the `cmp r0` in the bytes, not a host-pointer test.
        if left_pointer and not right_pointer and _is_null_pointer_expr(raw_left):
            pieces.append(code[cursor:left_at])
            pieces.append("0")
            cursor = index
            index += len(op)
            continue
        if right_pointer and not left_pointer and _is_null_pointer_expr(raw_right):
            pieces.append(code[cursor:index + len(op)])
            pieces.append(" 0")
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
        for match in _CALL.finditer(text):
            if match.start() < cursor:
                continue
            try:
                close = _match_paren(text, match.end() - 1)
            except ValueError:
                continue
            inner = rewrite(text[match.end():close])
            arguments = _split_args(inner)
            rewritten_args: list[str] = []
            for arg in arguments:
                stripped = arg.strip()
                if re.fullmatch(r"0x[0-9A-Fa-f]+", stripped) and int(stripped, 16) > 0x7FFFFFFF:
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


_FAIL = ("fail",)
_NO_GPR_WRITE = {
    "cmp", "cmpi", "tst", "tst1", "tst1r",
    "st8", "st16", "st32",
    "set1", "not1", "clr1", "set1r", "not1r", "clr1r",
}
# r1–r31. r6–r9 enter as the incoming arguments; the rest start unknown.
_TRACKED = tuple(range(1, 32))
# GHS RH850: r3–r5 (sp/gp/tp) and r20–r29 survive a call. r6–r9 survive only
# when this particular callee never writes them. r10 is then the return value.
_CALLER_KILLED = {1, 2, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 30, 31}
_ARG_CLOBBERS: dict[int, set[int]] | None = None
_R10_PRESERVE: set[int] = set()
# Callees that return with one immediate in r4. The caller keeps that global pointer.
_R4_SETTERS: dict[int, int] = {}
_CHECKED_NAMES: set[str] | None = None
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


def _transfer(state: dict[int, set], inst) -> dict[int, set]:
    cur = {reg: set(values) for reg, values in state.items()}
    if inst.kind == "jarl":
        killed = set(_CALLER_KILLED)
        clobbers = _ARG_CLOBBERS
        if clobbers is not None and inst.target in clobbers:
            killed |= clobbers[inst.target]
        else:
            killed.update((6, 7, 8, 9))
        if inst.link:
            killed.add(inst.link)
        # A callee that never writes r10 leaves the caller's return register alone.
        if inst.target in _R10_PRESERVE:
            killed.discard(10)
        for reg in killed:
            if reg in cur:
                cur[reg] = {_FAIL}
        if 10 in killed and inst.link != 10 and 10 in cur:
            cur[10] = {("call", inst.target)}
        elif 10 in killed and 10 in cur:
            cur[10] = {_FAIL}
        left = _R4_SETTERS.get(inst.target)
        if left is not None and 4 in cur:
            cur[4] = {("imm", left)}
        return cur
    if inst.kind == "callt":
        for reg in _CALLER_KILLED | {6, 7, 8, 9}:
            if reg in cur:
                cur[reg] = {_FAIL}
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
    parsed = _stmt_parts(inst.stmt) if inst.stmt else None
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
                cur[3] = shifted
        return cur
    if name == "popsp" and len(args) >= 2 and args[0] is not None and args[1] is not None:
        if 0 <= args[0] <= args[1] <= 31:
            for reg in range(args[0], args[1] + 1):
                if reg in cur and reg != 3:
                    cur[reg] = {_FAIL}
            if 3 in cur:
                shifted = _shift_sp(cur[3], 4 * (args[1] - args[0] + 1))
                if shifted is not None:
                    cur[3] = shifted
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
    if name in {"ld8s", "ld8u", "ld16s", "ld16u", "ld32"} and len(args) >= 3 and args[2] is not None:
        loaded = {"ld8s": (1, True), "ld8u": (1, False), "ld16s": (2, True), "ld16u": (2, False), "ld32": (4, False)}
        base = cur.get(args[1]) if args[1] is not None else None
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
            for reg in _TRACKED:
                merged = old[reg] | cur[reg]
                if merged != old[reg]:
                    old[reg] = merged
                    changed = True
            if changed:
                work.append(succ)
    return incoming


def _param_names(signature: str) -> list[str]:
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening:
        return []
    body = signature[opening + 1:closing].strip()
    if not body or body == "void":
        return []
    names = []
    for part in _split_args(body):
        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", part.strip())
        names.append(match.group(1) if match else "")
    return names


def _signature_name(signature: str) -> str:
    match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
    return match.group(1) if match else ""


def _return_type_of(signature: str, name: str) -> str:
    index = signature.find(name + "(")
    if index < 0:
        return ""
    return " ".join(signature[:index].split())


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
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)", statement, flags=re.S):
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


def _direct_arg_writes(fn) -> tuple[set[int], list[int], bool]:
    """r6–r9 this function writes itself, and the direct calls it makes."""
    written: set[int] = set()
    calls: list[int] = []
    has_callt = False
    blank = {reg: {("live",)} for reg in (6, 7, 8, 9)}
    for inst in fn.insts:
        if inst.kind == "callt":
            has_callt = True
            continue
        if inst.kind == "jarl":
            if inst.target:
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
    pattern = re.compile(rf"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*{re.escape(callee)}\s*\(")
    for match in pattern.finditer(body, 0, pos):
        assign = match
    if assign is None:
        return None
    try:
        close = _match_paren(body, assign.end() - 1)
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
        return open_at, _match_paren(head, open_at)
    except ValueError:
        return None


def _prepared_body(code: str) -> tuple[str, str, list[tuple[str, int, int]]] | None:
    code = _strip_calling_convention(code)
    brace = _opening_brace(code)
    if brace < 0:
        return None
    signature = _c_signature(code)
    body = code[brace:]
    return signature, body, _direct_calls(body)


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
        stripped = _strip_calling_convention(row["decompiled_c"])
        brace = _opening_brace(stripped)
        if brace < 0 or _last_declarator(stripped[:brace], name) is None:
            continue
        nparams = params.get(name, len(_param_names(signature)))
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
            existing = _split_args(body[open_at + 1:close])
            if len(existing) == 1 and not existing[0].strip():
                existing = []
            slot = cursor.get(entry, 0)
            cursor[entry] = slot + 1
            if counts[entry] != len(grouped.get(entry, ())):
                continue
            if slot >= len(grouped.get(entry, ())):
                continue
            addr = grouped[entry][slot]
            # Same cap the call rewrite uses: a register the callee does not
            # read is not an argument we can recover.
            need = min(arity.get(callee, 0), params.get(callee, 0))
            if len(existing) >= need:
                continue
            for reg in range(6 + len(existing), 6 + need):
                origin = state.get(addr, {}).get(reg, set())
                if len(origin) != 1:
                    continue
                item = next(iter(origin))
                if item[0] == "entry" and item[1] - 6 >= nparams:
                    highest = max(highest, item[1] - 5)
        if highest > nparams:
            wanted[name] = highest
    blocked: set[str] = set()
    for name, (signature, body, events) in prepared.items():
        params_here = _param_names(signature)
        types_here = _signature_param_types(signature)
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
            existing = _split_args(body[open_at + 1:close])
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
            for reg in range(6 + old_count, 6 + wanted[callee]):
                if reg - 6 < len(existing):
                    continue
                if _emit_origin(state.get(addr, {}).get(reg, set()), params_here, types_here) is None:
                    blocked.add(callee)
                    break
    return {name: count for name, count in wanted.items() if name not in blocked}


def _widen_signature(code: str) -> str:
    """Give a forwarded incoming register the parameter the bytes already pass."""
    brace = _opening_brace(code)
    if brace < 0:
        return code
    signature = _c_signature(code)
    name = _signature_name(signature)
    facts = _call_facts()
    if name in facts["hand"]:
        return code
    target = facts["params"].get(name, 0)
    current = _param_names(signature)
    if target <= len(current):
        return code
    found = _last_declarator(code[:brace], name)
    if found is None:
        return code
    open_at, close = found
    inside = code[open_at + 1:close]
    stripped = _strip_comments(inside).strip()
    names = set(current)
    added: list[str] = []
    for index in range(len(current), target):
        param = f"param_{index + 1}"
        if param in names:
            param = f"param_{index + 1}_in"
        names.add(param)
        added.append(f"undefined4 {param}")
    extra = ", ".join(added)
    replacement = extra if not stripped or stripped == "void" else inside.rstrip() + ", " + extra
    return code[:open_at + 1] + replacement + code[close:]


def _writes_r10(fn) -> bool:
    """True when an instruction in this function, not one of its callees, writes r10."""
    for inst in fn.insts:
        if inst.kind in {"jarl", "jr", "callt", "jmp", "br", "b", "dispose"}:
            continue
        parsed = _stmt_parts(inst.stmt) if inst.stmt else None
        if parsed is None:
            continue
        name, args = parsed
        if not args or name in _NO_GPR_WRITE or name in {"prepare", "pushsp", "popsp"}:
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


def _counter_imms(fn) -> set[int] | None:
    """Immediates written into r10 when the only later updates are in place.

    A loop that counts in r10 (`movi` then `addi_imm5` and a narrow) leaves
    `fail` in the origin lattice because the add is not folded across the
    back edge. The immediate is still the counter's start value.
    """
    imms: set[int] = set()
    saw_add = False
    for inst in fn.insts:
        if inst.kind in {"jarl", "jr", "callt"}:
            return None
        parsed = _stmt_parts(inst.stmt) if inst.stmt else None
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
    preserve = {addr for addr in calls if addr not in direct and addr not in callt}
    changed = True
    while changed:
        changed = False
        for addr in list(preserve):
            if any(target not in preserve for target in calls.get(addr, ())):
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


def _call_facts() -> dict:
    """Argument registers and r10 at each direct call, from the function bytes."""
    global _CALL_FACTS, _ARG_CLOBBERS, _R10_PRESERVE
    if _CALL_FACTS is not None:
        return _CALL_FACTS
    from tools.camry_lift import decode_at, load_image, walk_symbol
    from tools.project.pseudo import load_corpus

    image = load_image()
    symbols = load_symbols()
    entries = {row["name"]: int(row["addr"], 16) for row in symbols}
    names_at = {addr: name for name, addr in entries.items()}
    origins: dict[str, dict] = {}
    sites: dict[str, dict[int, list[int]]] = {}
    ret_target: dict[str, int] = {}
    ret_r10: dict[str, list[set]] = {}
    saved_pmr: set[str] = set()
    stored_r10: set[str] = set()
    counters: dict[str, set[int]] = {}
    arity: dict[str, int] = {}
    walked = []
    direct_writes: dict[int, set[int]] = {}
    direct_calls: dict[int, list[int]] = {}
    callt: set[int] = set()
    direct_r10: set[int] = set()
    for row in symbols:
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        walked.append((row, fn))
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
    _ARG_CLOBBERS = _arg_clobber_map(direct_writes, direct_calls, callt)
    _R10_PRESERVE = _r10_preservers(direct_r10, direct_calls, callt)
    states = _entry_gps(walked, names_at)
    for row, fn in walked:
        state = states[row["name"]]
        origins[row["name"]] = state
        grouped: dict[int, list[int]] = {}
        for inst in fn.insts:
            if inst.kind in {"jarl", "jr"} and inst.target in names_at:
                grouped.setdefault(inst.target, []).append(inst.addr)
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
                parsed = _stmt_parts(prev.stmt) if prev.stmt else None
                if (
                    prev.addr + prev.size == ret_at
                    and parsed is not None
                    and parsed[0] in {"st8", "st16", "st32"}
                    and parsed[1]
                    and parsed[1][0] == 10
                ):
                    stored_r10.add(row["name"])
    _meta, functions = load_corpus(
        REPO_ROOT / "data" / "generated" / TARGET / "decompilations.jsonl"
    )
    corpus: dict[str, dict] = {}
    for row in functions:
        corpus.setdefault(row["name"], row)
    hand_types = _hand_param_types()
    hand_names = set(hand_types)
    params: dict[str, int] = {}
    returns: dict[str, str] = {}
    for name, row in corpus.items():
        signature = _c_signature(_strip_calling_convention(row["decompiled_c"]))
        if name in hand_types:
            params[name] = len(hand_types[name])
        else:
            params[name] = len(_signature_param_types(signature))
        returns[name] = _return_type_of(signature, name)
    header = _strip_comments((ROOT / "include" / "camry.h").read_text(encoding="utf-8"))
    for match in re.finditer(
        r"^([A-Za-z_][A-Za-z0-9_ \t\*]*?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        header,
        flags=re.M,
    ):
        returns[match.group(2)] = " ".join(match.group(1).split())
    trailing: dict[str, str] = {}
    for name, row in corpus.items():
        if name in hand_names or returns.get(name) != "void":
            continue
        statement = _trailing_call(_strip_calling_convention(row["decompiled_c"]))
        if statement is None:
            continue
        callee = re.match(r"[A-Za-z_][A-Za-z0-9_]*", statement)
        if callee is None or callee.group(0) not in entries:
            continue
        if ret_target.get(name) != entries[callee.group(0)]:
            continue
        trailing[name] = callee.group(0)
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
    widened = _forwarded_param_counts(
        corpus, origins, sites, entries, arity, params, hand_names
    )
    need = {
        name: min(arity.get(name, 0), count)
        for name, count in params.items()
    }
    for name, count in widened.items():
        params[name] = count
        need[name] = count
    ram: dict[int, set[int]] = {}
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
            width = _access_width(inst.text)
            if width is None:
                continue
            ram.setdefault(address, set()).add(width)
    _CALL_FACTS = {
        "entries": entries,
        "names": names_at,
        "origins": origins,
        "sites": sites,
        "arity": arity,
        "params": params,
        "need": need,
        "hand": hand_names,
        "planned": planned,
        "saved_pmr": saved_pmr,
        "preserves": {names_at[addr] for addr in _R10_PRESERVE if addr in names_at},
        "returns": returns,
        "ret_r10": ret_r10,
        "counters": counters,
        "stored_r10": stored_r10,
        "ram": {addr: next(iter(widths)) for addr, widths in ram.items() if len(widths) == 1},
    }
    return _CALL_FACTS


def _argument_arity(fn, state: dict) -> int:
    """Highest r6-r9 whose incoming value reaches a read."""
    index_of = {inst.addr: index for index, inst in enumerate(fn.insts)}
    read: set[int] = set()
    for addr, regs in state.items():
        if not isinstance(addr, int) or addr not in index_of:
            continue
        inst = fn.insts[index_of[addr]]
        for reg in (6, 7, 8, 9):
            origin = regs.get(reg, ())
            if not any(item[0] == "entry" and item[1] == reg for item in origin):
                continue
            if _reads_reg(inst, reg):
                read.add(reg)
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
    parsed = _stmt_parts(inst.stmt) if inst.stmt else None
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


def _direct_calls(code: str) -> list[tuple[str, int, int]]:
    """Calls in execution order: a nested call closes before the call around it."""
    events: list[tuple[str, int, int]] = []
    stack: list[tuple[str, int, int]] = []
    depth = 0
    index = 0
    while index < len(code):
        if code.startswith("/*", index):
            end = code.find("*/", index + 2)
            index = len(code) if end < 0 else end + 2
            continue
        char = code[index]
        if char == "(":
            depth += 1
            index += 1
            continue
        if char == ")":
            if stack and stack[-1][1] == depth:
                name, _depth, open_at = stack.pop()
                events.append((name, open_at, index))
            depth = max(0, depth - 1)
            index += 1
            continue
        match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[index:])
        if match is None:
            index += 1
            continue
        name = match.group(0)
        nxt = index + match.end()
        while nxt < len(code) and code[nxt] in " \t\n\r":
            nxt += 1
        if nxt < len(code) and code[nxt] == "(" and name not in _SKIP_CALLS:
            depth += 1
            stack.append((name, depth, nxt))
            index = nxt + 1
            continue
        index = index + match.end()
    return events


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
    if not var or var in _PRIMITIVE_TYPES or var in _INT_TYPES:
        return None
    return var, cursor, name_start


def _produced_type(facts: dict, name: str) -> str:
    if name in facts["saved_pmr"]:
        return "uint"
    planned = facts["planned"].get(name)
    if planned:
        return planned
    return facts["returns"].get(name, "void")


def _rewrite_preserved_results(code: str) -> str:
    """An assignment of a call that leaves r10 alone belongs to the earlier call."""
    brace = _opening_brace(code)
    if brace < 0:
        return code
    caller = _signature_name(_c_signature(code))
    facts = _call_facts()
    grouped = facts["sites"].get(caller)
    state = facts["origins"].get(caller)
    if not grouped or state is None:
        return code
    body = code[brace:]
    events = [
        (name, open_at, close)
        for name, open_at, close in _direct_calls(body)
        if facts["entries"].get(name) is not None
    ]
    counts: dict[int, int] = {}
    for name, _open_at, _close in events:
        entry = facts["entries"][name]
        counts[entry] = counts.get(entry, 0) + 1
    usable = {
        entry for entry, count in counts.items()
        if count == len(grouped.get(entry, ()))
    }
    cursor_at = {entry: 0 for entry in usable}
    paired: list[tuple[str, int, int, int | None]] = []
    for name, open_at, close in events:
        entry = facts["entries"][name]
        addr = None
        if entry in usable:
            slot = cursor_at[entry]
            cursor_at[entry] = slot + 1
            sites = grouped.get(entry, ())
            if slot < len(sites):
                addr = sites[slot]
        paired.append((name, open_at, close, addr))
    edits: list[tuple[int, int, str]] = []
    claimed: set[int] = set()
    for index, (name, open_at, close, addr) in enumerate(paired):
        if name not in facts["preserves"] or addr is None:
            continue
        assigned = _assignment_prefix(body, open_at)
        if assigned is None or not body[close + 1:].lstrip().startswith(";"):
            continue
        var, prefix_start, prefix_end = assigned
        origin = state.get(addr, {}).get(10, set())
        if len(origin) != 1 or next(iter(origin))[0] != "call":
            continue
        producer = facts["names"].get(next(iter(origin))[1])
        if not producer:
            continue
        earlier = None
        for previous in paired[:index]:
            if previous[0] == producer and previous[3] is not None:
                earlier = previous
        if earlier is None:
            continue
        between = body[earlier[2]:prefix_start]
        killed = False
        for found in re.finditer(rf"\b{re.escape(var)}\s*=(?!=)\s*([A-Za-z_][A-Za-z0-9_]*)?", between):
            rhs = found.group(1)
            if rhs is None or rhs not in facts["preserves"]:
                killed = True
                break
        if killed:
            continue
        earlier_assigned = _assignment_prefix(body, earlier[1])
        if earlier_assigned is not None and earlier_assigned[0] == var:
            edits.append((prefix_start, prefix_end, ""))
            continue
        if earlier_assigned is not None or _produced_type(facts, producer) == "void":
            continue
        if not body[earlier[2] + 1:].lstrip().startswith(";"):
            continue
        # A cast or dereference on the left is already an assignment.
        statement_start = earlier[2]
        while statement_start > 0 and body[statement_start - 1] not in ";{}":
            statement_start -= 1
        if "=" in body[statement_start:earlier[1]]:
            continue
        name_start = earlier[1]
        while name_start > 0 and body[name_start - 1] in " \t\n\r":
            name_start -= 1
        name_start -= len(producer)
        if body[name_start:name_start + len(producer)] != producer or name_start in claimed:
            continue
        claimed.add(name_start)
        edits.append((name_start, name_start, f"{var} = "))
        edits.append((prefix_start, prefix_end, ""))
    if not edits:
        return code
    pieces: list[str] = []
    cursor = 0
    for start, end, text in sorted(edits):
        if start < cursor:
            return code
        pieces.append(body[cursor:start])
        pieces.append(text)
        cursor = end
    pieces.append(body[cursor:])
    return code[:brace] + "".join(pieces)


def _rewrite_recovered_arguments(code: str) -> str:
    """A call that omits a register the callee reads gets that register's value."""
    brace = _opening_brace(code)
    if brace < 0:
        return code
    signature = _c_signature(code)
    caller = _signature_name(signature)
    facts = _call_facts()
    grouped = facts["sites"].get(caller)
    state = facts["origins"].get(caller)
    if not grouped or state is None:
        return code
    params = _param_names(signature)
    types = _signature_param_types(signature)
    body = code[brace:]
    events = [
        (name, open_at, close)
        for name, open_at, close in _direct_calls(body)
        if facts["entries"].get(name) is not None
    ]
    counts: dict[int, int] = {}
    for name, _open_at, _close in events:
        entry = facts["entries"][name]
        counts[entry] = counts.get(entry, 0) + 1
    usable = {
        entry for entry, count in counts.items()
        if count == len(grouped.get(entry, ()))
    }
    cursor_at = {entry: 0 for entry in usable}
    edits: list[tuple[int, str]] = []
    for name, open_at, close in events:
        entry = facts["entries"][name]
        if entry not in usable:
            continue
        existing = _split_args(body[open_at + 1:close])
        if len(existing) == 1 and not existing[0].strip():
            existing = []
        need = facts["need"].get(name, 0)
        slot = cursor_at[entry]
        cursor_at[entry] = slot + 1
        if len(existing) >= need:
            continue
        addr = grouped[entry][slot]
        recovered: list[str] = []
        for reg in range(6 + len(existing), 6 + need):
            origin = state.get(addr, {}).get(reg, set())
            expr = _emit_origin(origin, params, types)
            if expr is None and len(origin) == 1 and next(iter(origin))[0] == "sp":
                expr = _stack_local(code, next(iter(origin))[1])
            if expr is None and len(origin) == 1 and next(iter(origin))[0] == "call":
                callee = facts["names"].get(next(iter(origin))[1])
                if callee:
                    expr = _value_of_call(body, open_at, callee)
            if expr is None:
                recovered = []
                break
            recovered.append(expr)
        if not recovered:
            continue
        joiner = "" if not existing else ", "
        edits.append((close, joiner + ", ".join(recovered)))
    if not edits:
        return code
    pieces: list[str] = []
    cursor = 0
    for close, text in sorted(edits):
        pieces.append(body[cursor:close])
        pieces.append(text)
        cursor = close
    pieces.append(body[cursor:])
    return code[:brace] + "".join(pieces)


def _rewrite_returned_call(code: str) -> str:
    """A void function whose r10 at every return is one call returns that call."""
    signature = _c_signature(code)
    name = _signature_name(signature)
    new_type = _call_facts()["planned"].get(name)
    span = _trailing_call_span(code)
    if not new_type or span is None or _return_type_of(signature, name) != "void":
        return code
    statement, start, ret_end = span
    brace = _opening_brace(code)
    head, body = code[:brace], code[brace:]
    declarator = list(re.finditer(rf"\bvoid(\s+{re.escape(name)}\s*\()", head))
    if not declarator:
        return code
    for found in reversed(declarator):
        head = head[:found.start()] + new_type + found.group(1) + head[found.end():]
    body = body[:start] + "\n  return " + statement + ";" + body[ret_end:]
    return head + body


def _saved_pmr_variable(body: str) -> str | None:
    """The variable holding the PMR read that the bytes return in r10."""
    found = None
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*PMR\s*;", body):
        found = match
        break
    if found is None:
        return None
    name = found.group(1)
    if re.search(r"\breturn\b", body[:found.start()]):
        return None
    if re.search(rf"\b{re.escape(name)}\s*=(?!=)", body[found.end():]):
        return None
    if not re.search(r"\breturn\s*;", body[found.end():]):
        return None
    return name


def _rewrite_stored_result(code: str) -> str:
    """A void function that stores r10 and returns it yields that stored object."""
    signature = _c_signature(code)
    name = _signature_name(signature)
    facts = _call_facts()
    if (
        name not in facts["stored_r10"]
        or name in facts["hand"]
        or name in facts["saved_pmr"]
        or facts["planned"].get(name)
        or _return_type_of(signature, name) != "void"
    ):
        return code
    brace = _opening_brace(code)
    if brace < 0:
        return code
    head, body = code[:brace], code[brace:]
    lhss = list(dict.fromkeys(re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)",
        body,
        flags=re.M,
    )))
    returns = list(re.finditer(r"\breturn\s*;", body))
    declarator = list(re.finditer(rf"\bvoid(\s+{re.escape(name)}\s*\()", head))
    if len(lhss) != 1 or len(returns) != 1 or not declarator:
        return code
    for found in reversed(declarator):
        head = head[:found.start()] + "uint" + found.group(1) + head[found.end():]
    ret = returns[0]
    body = body[:ret.start()] + f"return {lhss[0]};" + body[ret.end():]
    return head + body


_HELD_TYPES = {
    "int", "uint", "long", "ulong", "short", "ushort", "char", "uchar", "byte",
    "sbyte", "undefined", "undefined1", "undefined2", "undefined4", "bool",
}


def _const_value(text: str) -> int | None:
    match = re.fullmatch(r"(0x[0-9A-Fa-f]+|-?\d+)[uUlL]*", text.strip())
    if match is None:
        return None
    token = match.group(1)
    value = int(token, 16) if token.lower().startswith("0x") else int(token)
    return value & 0xFFFFFFFF


def _held_assignments(body: str, var: str) -> list[str]:
    found: list[str] = []
    for match in re.finditer(rf"(?<![\w.]){re.escape(var)}\s*=(?!=)", body):
        if match.start() and body[match.start() - 1] in ".>":
            continue
        found.append(body[match.end():_rhs_end(body, match.end())].strip())
    return found


def _declared_scalar(body: str, var: str) -> str | None:
    """The function-scope scalar type of `var`, when it has one declaration."""
    types: list[str] = []
    depth = 0
    index = 0
    while index < len(body):
        if body.startswith("/*", index):
            end = body.find("*/", index + 2)
            index = len(body) if end < 0 else end + 2
            continue
        char = body[index]
        if char == "{":
            depth += 1
            index += 1
            continue
        if char == "}":
            depth = max(0, depth - 1)
            index += 1
            continue
        if depth == 1:
            match = re.match(
                rf"([A-Za-z_][A-Za-z0-9_]*)\s+{re.escape(var)}\s*;",
                body[index:],
            )
            if match and (index == 0 or body[index - 1] in " \t\n\r{(;"):
                types.append(match.group(1))
                index += match.end()
                continue
        index += 1
    if len(types) != 1 or types[0] not in _HELD_TYPES:
        return None
    return types[0]


def _assignment_token(rhs: str, var: str) -> tuple:
    value = _const_value(rhs)
    if value is not None:
        return ("imm", value)
    if re.match(rf"(?:\([^)]*\)\s*)*{re.escape(var)}\b", rhs):
        return ("self",)
    call = re.fullmatch(
        r"(?:\([^)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\(.*\)",
        rhs,
        flags=re.S,
    )
    if call and call.group(1) not in {"if", "for", "while", "switch", "return", "sizeof"}:
        return ("call", call.group(1))
    return ("other",)


def _held_local(body: str, needed: set[tuple]) -> tuple[str, str] | None:
    """The one local whose assignments are exactly `needed`, and nothing else."""
    if not needed:
        return None
    names = {
        match.group(1)
        for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)", body)
    }
    found: list[tuple[str, str]] = []
    for var in names:
        tokens = {_assignment_token(rhs, var) for rhs in _held_assignments(body, var)}
        if tokens != needed:
            continue
        typ = _declared_scalar(body, var)
        if typ is None:
            continue
        found.append((var, typ))
    if len(found) != 1:
        return None
    var = found[0][0]
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", body):
        callee = match.group(1)
        if ("call", callee) not in needed:
            continue
        prev = max(
            body.rfind(";", 0, match.start()),
            body.rfind("{", 0, match.start()),
            body.rfind("}", 0, match.start()),
        )
        if not re.search(r"(?<![=<>!])=(?!=)", body[prev + 1:match.start()]):
            return None
    return found[0]


def _rewrite_held_result(code: str) -> str:
    """A void function whose r10 is one local at every return returns that local."""
    signature = _c_signature(code)
    name = _signature_name(signature)
    facts = _call_facts()
    if (
        name in facts["hand"]
        or name in _checked_names()
        or name in facts["saved_pmr"]
        or name in facts["stored_r10"]
        or facts["planned"].get(name)
        or _return_type_of(signature, name) != "void"
    ):
        return code
    brace = _opening_brace(code)
    if brace < 0:
        return code
    head, body = code[:brace], code[brace:]
    if not re.search(r"\breturn\s*;", body) or re.search(r"\breturn\b(?!\s*;)", body):
        return code
    origins = facts["ret_r10"].get(name) or []
    flat: set = set()
    for origin in origins:
        flat |= origin
    held = None
    if flat and all(item[0] in {"imm", "call"} for item in flat):
        needed = set()
        for item in flat:
            if item[0] == "imm":
                needed.add(("imm", item[1] & 0xFFFFFFFF))
                continue
            callee = facts["names"].get(item[1])
            if not callee:
                needed = set()
                break
            needed.add(("call", callee))
        held = _held_local(body, needed)
    elif name in facts["counters"]:
        imms = facts["counters"][name]
        if flat and all(
            item[0] == "fail" or (item[0] == "imm" and (item[1] & 0xFFFFFFFF) in imms)
            for item in flat
        ):
            held = _held_local(body, {("imm", value) for value in imms} | {("self",)})
    if held is None:
        return code
    var, typ = held
    declarator = list(re.finditer(rf"\bvoid(\s+{re.escape(name)}\s*\()", head))
    if not declarator:
        return code
    for found in reversed(declarator):
        head = head[:found.start()] + typ + found.group(1) + head[found.end():]
    body = re.sub(r"\breturn\s*;", f"return {var};", body)
    return head + body


def _checked_names() -> set[str]:
    global _CHECKED_NAMES
    if _CHECKED_NAMES is None:
        _CHECKED_NAMES = {
            row["name"]
            for row in load_matched()
            if row.get("status") in {"equivalent", "byte-matched"}
        }
    return _CHECKED_NAMES


def _rewrite_saved_pmr(code: str) -> str:
    """A void function whose r10 is the PMR it read returns that saved value."""
    signature = _c_signature(code)
    name = _signature_name(signature)
    facts = _call_facts()
    if name in facts["hand"] or name not in facts["saved_pmr"]:
        return code
    if _return_type_of(signature, name) != "void":
        return code
    brace = _opening_brace(code)
    if brace < 0:
        return code
    head, body = code[:brace], code[brace:]
    saved = _saved_pmr_variable(body)
    declarator = list(re.finditer(rf"\bvoid(\s+{re.escape(name)}\s*\()", head))
    if saved is None or not declarator:
        return code
    for found in reversed(declarator):
        head = head[:found.start()] + "uint" + found.group(1) + head[found.end():]
    body = re.sub(r"\breturn\s*;", f"return {saved};", body, count=1)
    return head + body


def _rewrite_icus(code: str) -> str:
    """The status word's low bit is BUSY. The command word is CMD, bits 8–15, then the slot."""
    declared = {
        match.group(1)
        for match in re.finditer(
            r"\bICUS_(?:Status|Command)\s+([A-Za-z_][A-Za-z0-9_]*)\s*;",
            code,
        )
    }
    code = re.sub(r"\bICUSCMD\s*=\s*\(ICUS_Command\)", "ICUSCMD = (uint32_t)", code)
    for name in sorted(declared, key=len, reverse=True):
        code = re.sub(
            rf"\bICUSCMD\s*=\s*{re.escape(name)}\s*;",
            f"ICUSCMD = {name}.raw;",
            code,
        )
        code = re.sub(rf"\(\s*uint\s*\)\s*{re.escape(name)}\b", f"{name}.raw", code)
        code = re.sub(rf"\b{re.escape(name)}\s*=(?!=)", f"{name}.raw =", code)
    return code


_GHIDRA_GP = 0xFEBF9800
_RUNTIME_GP = 0xFEBEB800
_GP_DELTA = (_GHIDRA_GP - _RUNTIME_GP) & 0xFFFFFFFF
_GP_MEMORY = {
    "ld8s", "ld8u", "ld16s", "ld16u", "ld32",
    "st8", "st16", "st32", "movea",
}
_GP_PAIRS: dict[str, dict[int, int]] | None = None
_GP_HITS: dict[str, set[int]] | None = None
_DAT_TYPES: dict[int, str] | None = None
_GP_OBJECTS: list[tuple[str, int, int, str]] | None = None
_SIGNED_LOADS: dict[str, dict[int, int]] | None = None


def _dat_types() -> dict[int, str]:
    global _DAT_TYPES
    if _DAT_TYPES is not None:
        return _DAT_TYPES
    found: dict[int, str] = {}
    header = ROOT / "src" / "all" / "common.h"
    pattern = re.compile(
        r"#define\s+DAT_([0-9A-Fa-f]+)\s+"
        r"\(\*\(\(volatile\s+([A-Za-z0-9_]+)\s+\*\)camry_host_ptr\(0x[0-9A-Fa-f]+u\)\)\)"
    )
    if header.exists():
        for match in pattern.finditer(header.read_text(encoding="utf-8")):
            found[int(match.group(1), 16)] = match.group(2)
    _DAT_TYPES = found
    return found


def _gp_address_map() -> dict[str, dict[int, int]]:
    """Ghidra gp+disp addresses whose bytes actually use r4, the runtime gp."""
    global _GP_PAIRS, _GP_HITS
    if _GP_PAIRS is not None:
        return _GP_PAIRS
    from tools.camry_lift import load_image, walk_symbol

    image = load_image()
    found: dict[str, dict[int, int]] = {}
    hits: dict[str, set[int]] = {}
    for row in load_symbols():
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        pairs: dict[int, int] = {}
        touched: set[int] = set()
        immediates: set[int] = set()
        accesses: list[int] = []
        holds_gp = {4}
        # gp plus an index. The displacement is still gp-relative.
        indexed: set[int] = set()
        # movea rd, gp, imm leaves rd = gp+imm. Later stores add their own disp.
        shifted: dict[int, int] = {}
        for inst in fn.insts:
            parsed = _stmt_parts(inst.stmt) if inst.stmt else None
            if parsed is None:
                continue
            name, args = parsed
            for arg in args:
                if isinstance(arg, int) and arg > 0xFFFF:
                    immediates.add(arg & 0xFFFFFFFF)
            if name == "mov" and len(args) >= 2 and isinstance(args[0], int):
                dst, src = args[0], args[1]
                if src in holds_gp:
                    holds_gp.add(dst)
                    indexed.discard(dst)
                elif src in indexed:
                    indexed.add(dst)
                    holds_gp.discard(dst)
                else:
                    holds_gp.discard(dst)
                    indexed.discard(dst)
                    shifted.pop(dst, None)
                continue
            if (
                name == "movea"
                and len(args) >= 3
                and isinstance(args[0], int)
                and isinstance(args[2], int)
                and args[1] in holds_gp
            ):
                shifted[args[0]] = args[2]
                accesses.append(args[2])
                holds_gp.discard(args[0])
                indexed.discard(args[0])
                continue
            if name == "add" and len(args) >= 2 and isinstance(args[0], int):
                dst, src = args[0], args[1]
                if src in holds_gp or src in indexed:
                    indexed.add(dst)
                    holds_gp.discard(dst)
                    shifted.pop(dst, None)
                    continue
                if dst in holds_gp or dst in indexed:
                    indexed.add(dst)
                    holds_gp.discard(dst)
                    shifted.pop(dst, None)
                    continue
            gp_base = holds_gp | indexed
            if (
                name in _GP_MEMORY
                and len(args) >= 3
                and args[1] in gp_base
                and isinstance(args[2], int)
            ):
                accesses.append(args[2])
            elif (
                name in _GP_MEMORY
                and len(args) >= 3
                and args[1] in shifted
                and isinstance(args[2], int)
            ):
                accesses.append(shifted[args[1]] + args[2])
            elif (
                name in {"set1", "not1", "clr1", "tst1"}
                and len(args) >= 2
                and args[0] in gp_base
                and isinstance(args[1], int)
            ):
                accesses.append(args[1])
            if (
                args
                and isinstance(args[0], int)
                and name not in {"st8", "st16", "st32", "cmp", "cmpi"}
            ):
                holds_gp.discard(args[0])
                indexed.discard(args[0])
                shifted.pop(args[0], None)
        for disp in accesses:
            ghidra = (_GHIDRA_GP + disp) & 0xFFFFFFFF
            runtime = (_RUNTIME_GP + disp) & 0xFFFFFFFF
            if ghidra not in immediates:
                pairs[ghidra] = runtime
                touched.add(ghidra)
        # The decompiler materializes gp as this immediate even when the bytes
        # only copy r4 into another register before the access.
        if _GHIDRA_GP not in immediates:
            pairs[_GHIDRA_GP] = _RUNTIME_GP
        if pairs:
            found[row["name"]] = pairs
            if touched:
                hits[row["name"]] = touched
    _GP_PAIRS = found
    _GP_HITS = hits
    return found


# Ghidra folds r5 against the boot table. The harness r5 is the application tp.
_GHIDRA_TP = 0x869C
_RUNTIME_TP = 0x23DFC
_TP_PAIRS: dict[str, dict[int, int]] | None = None


def _tp_address_map() -> dict[str, dict[int, int]]:
    """Ghidra tp+disp addresses whose bytes actually use r5, the harness tp."""
    global _TP_PAIRS
    if _TP_PAIRS is not None:
        return _TP_PAIRS
    from tools.camry_lift import load_image, walk_symbol

    image = load_image()
    found: dict[str, dict[int, int]] = {}
    for row in load_symbols():
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        pairs: dict[int, int] = {}
        immediates: set[int] = set()
        accesses: list[int] = []
        holds = {5}
        shifted: dict[int, int] = {}
        for inst in fn.insts:
            parsed = _stmt_parts(inst.stmt) if inst.stmt else None
            if parsed is None:
                continue
            name, args = parsed
            for arg in args:
                if isinstance(arg, int) and arg > 0xFFFF:
                    immediates.add(arg & 0xFFFFFFFF)
            if name == "mov" and len(args) >= 2 and isinstance(args[0], int):
                dst, src = args[0], args[1]
                if src in holds:
                    holds.add(dst)
                    shifted.pop(dst, None)
                elif src in shifted:
                    shifted[dst] = shifted[src]
                    holds.discard(dst)
                else:
                    holds.discard(dst)
                    shifted.pop(dst, None)
                continue
            if (
                name == "movea"
                and len(args) >= 3
                and isinstance(args[0], int)
                and isinstance(args[2], int)
                and args[1] in holds
            ):
                shifted[args[0]] = args[2]
                holds.discard(args[0])
                continue
            if name == "add" and len(args) >= 2 and isinstance(args[0], int):
                dst, src = args[0], args[1]
                if src in shifted and dst not in holds:
                    shifted[dst] = shifted[src]
                    holds.discard(dst)
                    continue
                if dst in shifted and src not in holds:
                    continue
                if src in holds or dst in holds:
                    holds.add(dst)
                    shifted.pop(dst, None)
                    continue
            if (
                name in _GP_MEMORY
                and len(args) >= 3
                and isinstance(args[2], int)
            ):
                if args[1] in holds:
                    accesses.append(args[2])
                elif args[1] in shifted:
                    accesses.append(shifted[args[1]] + args[2])
            elif (
                name in {"set1", "not1", "clr1", "tst1"}
                and len(args) >= 2
                and isinstance(args[1], int)
                and args[0] in holds
            ):
                accesses.append(args[1])
            if (
                args
                and isinstance(args[0], int)
                and name not in {
                    "st8", "st16", "st32", "cmp", "cmpi",
                    "ld8s", "ld8u", "ld16s", "ld16u", "ld32",
                    "add", "movea", "mov",
                }
            ):
                holds.discard(args[0])
                shifted.pop(args[0], None)
        for disp in accesses:
            ghidra = (_GHIDRA_TP + disp) & 0xFFFFFFFF
            runtime = (_RUNTIME_TP + disp) & 0xFFFFFFFF
            if ghidra not in immediates:
                pairs[ghidra] = runtime
        if pairs:
            found[row["name"]] = pairs
    _TP_PAIRS = found
    return found


def _rewrite_runtime_tp(code: str) -> str:
    """Use the harness tp for an address the bytes form as r5+disp."""
    signature = _c_signature(code)
    try:
        name = _signature_name(signature)
    except (AssertionError, ValueError):
        return code
    pairs = _tp_address_map().get(name)
    if not pairs:
        return code
    return _rewrite_addressed_macros(_apply_gp_pairs(code, pairs), pairs)


_NAMED_MACROS: list[tuple[str, int, str]] | None = None


def _named_macros() -> list[tuple[str, int, str]]:
    """common.h symbols whose replacement is a firmware address."""
    global _NAMED_MACROS
    if _NAMED_MACROS is not None:
        return _NAMED_MACROS
    header = ROOT / "src" / "all" / "common.h"
    found: list[tuple[str, int, str]] = []
    if header.exists():
        pattern = re.compile(
            r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\s+"
            r"(\(\*\(\(volatile\s+.+?\s+\*\)\s*camry_host_ptr\(0x([0-9A-Fa-f]+)u\)\)\)"
            r"|\(\(volatile\s+.+?\s+\*\)\s*camry_host_ptr\(0x([0-9A-Fa-f]+)u\)\))\s*$"
        )
        for line in header.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line.strip())
            if match is None:
                continue
            address = int(match.group(3) or match.group(4), 16)
            found.append((match.group(1), address, match.group(0).split(None, 2)[2]))
    _NAMED_MACROS = found
    return found


def _rewrite_addressed_macros(code: str, pairs: dict[int, int]) -> str:
    """A named symbol hides the address `_apply_gp_pairs` would retarget."""
    for name, address, expansion in _named_macros():
        runtime = pairs.get(address)
        if runtime is None or runtime == address:
            continue
        if re.search(rf"\b{re.escape(name)}\b", code) is None:
            continue
        updated, count = re.subn(
            rf"0x{address:x}u",
            f"0x{runtime:x}u",
            expansion,
            count=1,
            flags=re.IGNORECASE,
        )
        if count != 1:
            continue
        code = re.sub(rf"\b{re.escape(name)}\b", lambda _match: updated, code)
    return code


_PTR_SCALES: dict[int, int] | None = None
_PTR_WIDTH = {
    "uint8_t": 1, "int8_t": 1, "uchar": 1, "char": 1, "undefined1": 1,
    "uint16_t": 2, "int16_t": 2, "ushort": 2, "short": 2, "undefined2": 2,
    "uint32_t": 4, "int32_t": 4, "uint": 4, "int": 4, "undefined4": 4,
}


def _ptr_dat_scales() -> dict[int, int]:
    """Element size of each PTR_DAT macro. Pointer addition scales by this."""
    global _PTR_SCALES
    if _PTR_SCALES is not None:
        return _PTR_SCALES
    header = ROOT / "src" / "all" / "common.h"
    found: dict[int, int] = {}
    if header.exists():
        for match in re.finditer(
            r"#define\s+PTR_DAT_([0-9A-Fa-f]+)\s+\(\*\(\(volatile\s+(\w+)\s+\*\)",
            header.read_text(encoding="utf-8"),
        ):
            width = _PTR_WIDTH.get(match.group(2))
            if width:
                found[int(match.group(1), 16)] = width
    _PTR_SCALES = found
    return found


def _rewrite_scaled_table(code: str) -> str:
    """`&PTR_DAT + index` is a typed pointer add. Pass the firmware byte address.

    The cast through uint32 keeps only the low half of the host pointer.
    The element count in the C is not the byte stride.
    """
    try:
        name = _signature_name(_c_signature(code))
    except (AssertionError, ValueError):
        return code
    pairs = dict(_gp_address_map().get(name, {}))
    pairs.update(_tp_address_map().get(name, {}))
    if not pairs:
        return code
    scales = _ptr_dat_scales()
    needle = "(&PTR_DAT_"
    prefix = "camry_host_ptr((uint32_t)"
    pieces: list[str] = []
    index = 0
    while True:
        found = code.find(needle, index)
        if found < 0:
            pieces.append(code[index:])
            break
        if code[max(0, found - len(prefix)):found] != prefix:
            pieces.append(code[index:found + 1])
            index = found + 1
            continue
        call = found - len(prefix)
        try:
            closing = _match_paren(code, call + len("camry_host_ptr"))
        except ValueError:
            pieces.append(code[index:found + 1])
            index = found + 1
            continue
        inner = code[call + len("camry_host_ptr") + 1:closing].strip()
        wrapped = re.match(r"\(uint32_t\)\s*\((.*)\)\s*$", inner, re.S)
        if wrapped is None:
            pieces.append(code[index:closing + 1])
            index = closing + 1
            continue
        body = wrapped.group(1).strip()
        named = re.match(r"&PTR_DAT_([0-9A-Fa-f]+)\s*(.*)\s*$", body, re.S)
        if named is None:
            pieces.append(code[index:closing + 1])
            index = closing + 1
            continue
        address = int(named.group(1), 16)
        rest = named.group(2).strip()
        scale = scales.get(address)
        runtime = pairs.get(address)
        if scale is None or runtime is None or (rest and not rest.startswith("+")):
            pieces.append(code[index:closing + 1])
            index = closing + 1
            continue
        if rest:
            expr = rest[1:].strip()
            replacement = (
                f"camry_host_ptr((uint32_t)(0x{runtime:x}u + "
                f"(uint32_t)({expr}) * {scale}u))"
            )
        else:
            replacement = f"camry_host_ptr(0x{runtime:x}u)"
        pieces.append(code[index:call])
        pieces.append(replacement)
        index = closing + 1
    return "".join(pieces)


def _object_sizes() -> dict[str, tuple[int, int]]:
    """Byte span of each named data object, from its declared type."""
    cached = getattr(_object_sizes, "cached", None)
    if cached is not None:
        return cached
    widths = {
        "uint8_t": 1, "int8_t": 1, "uint16_t": 2, "int16_t": 2,
        "uint32_t": 4, "int32_t": 4,
    }
    structs = _struct_rows()
    found: dict[str, tuple[int, int]] = {}
    for row in _load_jsonl(ROOT / "data.jsonl"):
        type_name = row["type"].replace(" ", "")
        if type_name.startswith("@"):
            continue
        base = type_name.split("[", 1)[0]
        dims = [int(item) for item in re.findall(r"\[(\d+)\]", type_name)]
        if base in structs:
            elem = int(structs[base]["size"])
        elif base in _ARRAY_ELEMENTS:
            elem = _ARRAY_ELEMENTS[base][1]
        elif base in _SCALAR_TYPES:
            elem = widths.get(_SCALAR_TYPES[base], 1)
        else:
            elem = 1
        size = elem
        for dim in dims:
            size *= dim
        found[row["name"]] = (_address(row["addr"]), max(size, 1))
    _object_sizes.cached = found
    return found


def _gp_objects() -> list[tuple[str, int, int, str]]:
    """Named common.h objects in the Ghidra gp window: name, address, size, expression."""
    global _GP_OBJECTS
    if _GP_OBJECTS is not None:
        return _GP_OBJECTS
    sizes = _object_sizes()
    found: list[tuple[str, int, int, str]] = []
    header = ROOT / "src" / "all" / "common.h"
    pattern = re.compile(
        r"^#define\s+([A-Za-z_]\w*)\s+(.*camry_host_ptr\(0x([0-9A-Fa-f]+)u\).*)$"
    )
    if header.exists():
        for line in header.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line.strip())
            if match is None:
                continue
            name, expr, hex_addr = match.group(1), match.group(2), match.group(3)
            addr = int(hex_addr, 16)
            if name not in sizes or sizes[name][0] != addr:
                continue
            # A 16-bit displacement from the Ghidra gp reaches this object.
            disp = (addr - _GHIDRA_GP) & 0xFFFFFFFF
            if disp >= 0x80000000:
                disp -= 0x100000000
            if not -0x8000 <= disp < 0x8000:
                continue
            found.append((name, addr, sizes[name][1], expr))
    _GP_OBJECTS = found
    return found


def _apply_gp_pairs(code: str, pairs: dict[int, int], hits: set[int] | None = None) -> str:
    types = _dat_types()
    for ghidra in sorted(pairs, key=lambda addr: -len(f"{addr:x}")):
        runtime = pairs[ghidra]
        if ghidra == runtime:
            continue
        hex_g = f"{ghidra:x}"
        code = re.sub(
            rf"(?i)0x0*{hex_g}(?![0-9A-Fa-f])",
            f"0x{runtime:x}",
            code,
        )
        # A wider literal whose low half is this address, such as the
        # decompiler packing gp into a 64-bit constant.
        if len(hex_g) == 8:
            def widen(match: re.Match[str], source: int = ghidra, dest: int = runtime) -> str:
                value = int(match.group(0), 16)
                if value <= 0xFFFFFFFF or (value & 0xFFFFFFFF) != source:
                    return match.group(0)
                return hex((value & ~0xFFFFFFFF) | dest)

            code = re.sub(rf"(?i)\b0x[0-9a-f]*{hex_g}\b", widen, code)
        ctype = types.get(ghidra)
        if ctype is None:
            continue
        expr = f"(*((volatile {ctype} *)camry_host_ptr(0x{runtime:x}u)))"
        code = re.sub(rf"\bDAT_{hex_g}\b", expr, code)
    if hits:
        for name, addr, size, expr in _gp_objects():
            if not any(addr <= hit < addr + size for hit in hits):
                continue
            if not re.search(rf"\b{re.escape(name)}\b", code):
                continue
            runtime = (addr - _GP_DELTA) & 0xFFFFFFFF
            replacement = re.sub(
                rf"0x0*{addr:x}u",
                f"0x{runtime:x}u",
                expr,
                count=1,
                flags=re.IGNORECASE,
            )
            code = re.sub(rf"\b{re.escape(name)}\b", replacement, code)
    return code


_LOAD_WIDTH = {"ld8s": 1, "ld8u": 1, "ld16s": 2, "ld16u": 2}
_SIGN_EXTENDING = {"ld8s", "ld16s"}


def _signed_load_map() -> dict[str, dict[int, int]]:
    """Runtime addresses each function loads with a sign-extending byte or halfword.

    An address also loaded zero-extended in that function is left alone.
    """
    global _SIGNED_LOADS
    if _SIGNED_LOADS is not None:
        return _SIGNED_LOADS
    from tools.camry_lift import load_image, walk_symbol

    image = load_image()
    found: dict[str, dict[int, int]] = {}
    for row in load_symbols():
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        signed: dict[int, int] = {}
        unsigned: set[int] = set()
        holds_gp = {4}
        shifted: dict[int, int] = {}
        for inst in fn.insts:
            parsed = _stmt_parts(inst.stmt) if inst.stmt else None
            if parsed is None:
                continue
            name, args = parsed
            if name == "mov" and len(args) >= 2 and isinstance(args[0], int):
                dst, src = args[0], args[1]
                if src in holds_gp:
                    holds_gp.add(dst)
                    shifted.pop(dst, None)
                elif src in shifted:
                    shifted[dst] = shifted[src]
                    holds_gp.discard(dst)
                else:
                    holds_gp.discard(dst)
                    shifted.pop(dst, None)
                continue
            if (
                name == "movea"
                and len(args) >= 3
                and isinstance(args[0], int)
                and isinstance(args[2], int)
                and args[1] in holds_gp
            ):
                shifted[args[0]] = args[2]
                holds_gp.discard(args[0])
                continue
            if name in _LOAD_WIDTH and len(args) >= 3 and isinstance(args[2], int):
                base, disp = args[1], args[2]
                addr = None
                if base in holds_gp:
                    addr = (_RUNTIME_GP + disp) & 0xFFFFFFFF
                elif base in shifted:
                    addr = (_RUNTIME_GP + shifted[base] + disp) & 0xFFFFFFFF
                if addr is not None:
                    if name in _SIGN_EXTENDING:
                        signed[addr] = _LOAD_WIDTH[name]
                    else:
                        unsigned.add(addr)
            if (
                args
                and isinstance(args[0], int)
                and name not in {"st8", "st16", "st32", "cmp", "cmpi", "mov", "movea"}
            ):
                holds_gp.discard(args[0])
                shifted.pop(args[0], None)
        kept = {
            addr: width for addr, width in signed.items() if addr not in unsigned
        }
        if kept:
            found[row["name"]] = kept
    _SIGNED_LOADS = found
    return found


def _comment_spans(code: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    index = 0
    while index < len(code):
        if code.startswith("/*", index):
            end = code.find("*/", index + 2)
            if end < 0:
                spans.append((index, len(code)))
                break
            spans.append((index, end + 2))
            index = end + 2
            continue
        if code.startswith("//", index):
            end = code.find("\n", index)
            end = len(code) if end < 0 else end
            spans.append((index, end))
            index = end
            continue
        index += 1
    return spans


def _in_comment(index: int, spans: list[tuple[int, int]]) -> bool:
    for start, end in spans:
        if start <= index < end:
            return True
        if start > index:
            return False
    return False


def _cast_value_reads(code: str, name: str, cast: str) -> str:
    """Sign-extend reads of an unsigned lvalue. Leave stores and existing signed casts."""
    spans = _comment_spans(code)

    def replace(match: re.Match[str]) -> str:
        if _in_comment(match.start(), spans):
            return match.group(0)
        before = code[:match.start()]
        after = code[match.end():]
        if re.search(r"(?:&|\((?:int8_t|int16_t|short|char)\))\s*$", before):
            return match.group(0)
        if re.match(r"\s*(?:\+\+|--)", after):
            return match.group(0)
        if re.match(r"\s*[+\-*/%&|^]?=", after) and not re.match(
            r"\s*(?:==|!=|<=|>=)", after
        ):
            return match.group(0)
        return f"((int)({cast}){name})"

    return re.sub(rf"\b{re.escape(name)}\b", replace, code)


def _rewrite_signed_loads(code: str, signed: dict[int, int]) -> str:
    if not signed:
        return code
    types = _dat_types()
    for addr, width in sorted(signed.items()):
        cast = "int8_t" if width == 1 else "int16_t"
        macro = f"DAT_{addr:x}"
        if types.get(addr) in {"uint8_t", "uint16_t"} and re.search(rf"\b{macro}\b", code):
            code = _cast_value_reads(code, macro, cast)
        ctype = "uint8_t" if width == 1 else "uint16_t"
        pattern = (
            rf"\(\*\(\(volatile\s+{ctype}\s+\*\)\s*camry_host_ptr\(0x0*{addr:x}u\)\)\)"
        )
        code = re.sub(
            pattern,
            f"(*((volatile {cast} *)camry_host_ptr(0x{addr:x}u)))",
            code,
            flags=re.IGNORECASE,
        )
    return code


def _unsigned32_names(code: str) -> set[str]:
    types = _dat_types()
    names = {
        match.group(0)
        for match in re.finditer(r"\bDAT_([0-9A-Fa-f]+)\b", code)
        if types.get(int(match.group(1), 16)) == "uint32_t"
    }
    names.update(
        match.group(1)
        for match in re.finditer(
            r"\b(?:uint|uint32_t|unsigned(?:\s+int)?)\s+([A-Za-z_]\w*)\s*(?:=|;)",
            code,
        )
    )
    return names


def _rewrite_unsigned_saturation(code: str) -> str:
    """The 0x7fff clamp is a signed compare. A uint32 subject makes `< 0` false."""
    if "0x7fff" not in code:
        return code
    names = _unsigned32_names(code)
    if not names:
        return code
    ordered = sorted(names, key=len, reverse=True)

    def rewrite_line(line: str) -> str:
        if (
            "0x7fff" not in line
            or not re.search(r"[<>]", line)
            or line.lstrip().startswith(("*", "/"))
        ):
            return line
        for name in ordered:
            def replace(match: re.Match[str], name: str = name) -> str:
                before = line[:match.start()]
                after = line[match.end():]
                if before.rstrip().endswith("(int)"):
                    return match.group(0)
                if re.match(r"\s*[+\-*/%&|^]?=", after) and not re.match(
                    r"\s*(?:==|!=|<=|>=)", after
                ):
                    return match.group(0)
                return f"(int){name}"

            line = re.sub(rf"\b{re.escape(name)}\b", replace, line)
        return line

    return "\n".join(rewrite_line(line) for line in code.split("\n"))


def _rewrite_signed_values(code: str) -> str:
    code = _rewrite_unsigned_saturation(code)
    signature = _c_signature(code)
    try:
        name = _signature_name(signature)
    except (AssertionError, ValueError):
        return code
    return _rewrite_signed_loads(code, _signed_load_map().get(name, {}))


def _rewrite_runtime_gp(code: str) -> str:
    """Use the runtime gp for an address the bytes form as r4+disp.

    Ghidra folds that access against gp 0xfebf9800. The firmware's gp is
    0xfebeb800, so the folded immediate is 0xE000 high.
    """
    signature = _c_signature(code)
    try:
        name = _signature_name(signature)
    except (AssertionError, ValueError):
        return code
    pairs = _gp_address_map().get(name)
    if not pairs:
        return code
    return _rewrite_addressed_macros(
        _apply_gp_pairs(code, pairs, (_GP_HITS or {}).get(name)),
        pairs,
    )


def apply_runtime_gp() -> tuple[int, int]:
    """Retarget converted bodies. Equivalent functions keep the text they passed with."""
    blocked: set[str] = set()
    allowed: set[str] = set()
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    for name, statuses in by_name.items():
        if statuses & {"equivalent", "byte-matched"}:
            blocked.add(name)
        elif "converted" in statuses:
            allowed.add(name)
    pairs = _gp_address_map()
    functions = 0
    files = 0
    for path in sorted((ROOT / "src" / "all").glob("*.c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        index = 0
        changed = False
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith((" ", "\t", "/*", "//"))
            ):
                out.append(line)
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
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
            chunk = "\n".join(lines[start:index])
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            name = match.group(1) if match else ""
            if name in allowed and name not in blocked and pairs.get(name):
                updated = _apply_gp_pairs(chunk, pairs[name], (_GP_HITS or {}).get(name))
                if updated != chunk:
                    functions += 1
                    changed = True
                    chunk = updated
            out.extend(chunk.split("\n"))
        if changed:
            path.write_text("\n".join(out) + "\n", encoding="utf-8")
            files += 1
    return functions, files


def apply_signed_values() -> tuple[int, int]:
    """Sign-extend loads the bytes sign-extend, and clamp uint32 values as signed.

    Equivalent functions keep the text they passed with.
    """
    blocked: set[str] = set()
    allowed: set[str] = set()
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    for name, statuses in by_name.items():
        if statuses & {"equivalent", "byte-matched"}:
            blocked.add(name)
        elif "converted" in statuses:
            allowed.add(name)
    loads = _signed_load_map()
    functions = 0
    files = 0
    for path in sorted((ROOT / "src" / "all").glob("*.c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        index = 0
        changed = False
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith((" ", "\t", "/*", "//"))
            ):
                out.append(line)
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
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
            chunk = "\n".join(lines[start:index])
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            name = match.group(1) if match else ""
            if name in allowed and name not in blocked:
                updated = _rewrite_unsigned_saturation(chunk)
                updated = _rewrite_signed_loads(updated, loads.get(name, {}))
                if updated != chunk:
                    functions += 1
                    changed = True
                    chunk = updated
            out.extend(chunk.split("\n"))
        if changed:
            path.write_text("\n".join(out) + "\n", encoding="utf-8")
            files += 1
    return functions, files


_SYSREG_INPUTS = (
    "in_FPEC", "in_EBASE", "in_RBASE", "in_FPIPR", "in_ISPR", "in_INTCFG",
    "in_EIPSW", "in_EIIC", "in_FEPSW", "in_CTPC", "in_CTPSW",
)


def _rewrite_system_inputs(code: str) -> str:
    """Read PSW from the host register, and zero Ghidra's other sysreg inputs.

    Those locals are not arguments. The bytes read the system-register file,
    which this scenario resets to zero except PSW.ID.
    """
    code = re.sub(r"^[ \t]*uint in_PSW;[ \t]*\n", "", code, flags=re.M)
    code = re.sub(r"\bin_PSW\b", "camry_psw", code)
    for name in _SYSREG_INPUTS:
        code = re.sub(
            rf"^([ \t]*uint {name});[ \t]*$",
            rf"\1 = 0;",
            code,
            flags=re.M,
        )
    return code


def apply_system_inputs() -> tuple[int, int]:
    """Point converted PSW reads at camry_psw. Equivalent bodies stay as they passed."""
    blocked: set[str] = set()
    allowed: set[str] = set()
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    for name, statuses in by_name.items():
        if statuses & {"equivalent", "byte-matched"}:
            blocked.add(name)
        elif "converted" in statuses:
            allowed.add(name)
    functions = 0
    files = 0
    for path in sorted((ROOT / "src" / "all").glob("*.c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        index = 0
        changed = False
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith((" ", "\t", "/*", "//"))
            ):
                out.append(line)
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
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
            chunk = "\n".join(lines[start:index])
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            name = match.group(1) if match else ""
            if name in allowed and name not in blocked:
                updated = _rewrite_system_inputs(chunk)
                if updated != chunk:
                    functions += 1
                    changed = True
                    chunk = updated
            out.extend(chunk.split("\n"))
        if changed:
            path.write_text("\n".join(out) + "\n", encoding="utf-8")
            files += 1
    return functions, files


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
            closing = _match_paren(code, opening)
        except ValueError:
            pieces.append(code[index:found + len(_INDIRECT_CALL)])
            index = found + len(_INDIRECT_CALL)
            continue
        expr = code[opening + 1:closing]
        pieces.append(code[index:found])
        pieces.append(f"(*(int (*)())camry_indirect({expr})")
        index = closing + 1
    return "".join(pieces)


def _pointer_macro_names() -> set[str]:
    """Object macros that expand to a host pointer, not a loaded word."""
    cached = getattr(_pointer_macro_names, "cached", None)
    if cached is not None:
        return cached
    found: set[str] = set()
    header = ROOT / "src" / "all" / "common.h"
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
    pointers = _pointer_names(_c_signature(code), code)
    pattern = re.compile(
        r"\b(?:volatile\s+)?(?:unsigned\s+|signed\s+)?"
        r"(?:int|uint|short|ushort|char|byte|uchar|bool|long|ulong|ulonglong|longlong|"
        r"undefined[1248]?|uint(?:8|16|32|64)_t|int(?:8|16|32|64)_t|uintptr_t|size_t)"
        r"\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:;|,|\))"
    )
    return {match.group(1) for match in pattern.finditer(code)} - pointers


def _is_integer_address(expr: str, scalars: set[str], pointers: set[str], pointer_macros: set[str]) -> bool:
    """True when `expr` is a firmware address, not a pointer into the host mapping."""
    text = expr.strip()
    while _fully_wrapped(text):
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
                index = _match_bracket(text, index) + 1
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
            closing = _match_paren(code, opening)
        except ValueError:
            pieces.append(code[index:found + 1])
            index = found + 1
            continue
        inner = code[opening + 1:closing].strip()
        arith = inner[len("(uint32_t)"):].strip() if inner.startswith("(uint32_t)(") else ""
        if _fully_wrapped(arith):
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


def _match_paren_back(code: str, closing: int) -> int:
    depth = 0
    for index in range(closing, -1, -1):
        if code[index] == ")":
            depth += 1
        elif code[index] == "(":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unbalanced parenthesis")


def _firmware_word(expr: str, scalars: set[str], pointers: set[str], pointer_macros: set[str]) -> str:
    """The 32-bit firmware address an expression was trying to use as a code pointer."""
    text = expr.strip()
    while _fully_wrapped(text):
        text = text[1:-1].strip()
    cast = re.match(r"^\(\s*code\s*\*\s*\)\s*", text)
    if cast:
        text = text[cast.end():].strip()
        while _fully_wrapped(text):
            text = text[1:-1].strip()
        if text.startswith("camry_host_ptr("):
            try:
                closing = _match_paren(text, len("camry_host_ptr"))
            except ValueError:
                return text
            argument = text[len("camry_host_ptr") + 1:closing].strip()
            if argument.startswith("(uint32_t)(") and argument.endswith(")"):
                argument = argument[len("(uint32_t)"):].strip()
                if _fully_wrapped(argument):
                    argument = argument[1:-1].strip()
            return argument
        return text
    if text.startswith("*(code **)("):
        try:
            closing = _match_paren(text, len("*(code **)(") - 1)
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

    `f33_reset_vector` is address 0. The converted C was comparing a host pointer
    with the compiled function.
    """
    scalars = _scalar_names(code)
    pointers = _pointer_names(_c_signature(code), code)
    pointer_macros = _pointer_macro_names()
    marker = "(uintptr_t)(f33_reset_vector)"
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
            opening = _match_paren_back(code, close)
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
    pointers = _pointer_names(_c_signature(code), code)
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
            closing = _match_paren(code, opening)
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
            depth = 0
            end = None
            for cursor in range(after + 1, len(code)):
                char = code[cursor]
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                elif char == ";" and depth == 0:
                    end = cursor
                    break
            if end is None:
                pieces.append(code[index:closing + 1])
                index = closing + 1
                continue
            rhs = code[after + 1:end].strip()
            entry = _function_entries().get(rhs)
            value = f"0x{entry:x}u" if entry is not None else f"(uint32_t)({rhs})"
            pieces.append(code[index:found])
            pieces.append(f"{word} = {value}")
            index = end
            continue
        pieces.append(code[index:found])
        pieces.append(f"((code *)(uintptr_t){word})")
        index = closing + 1
    return "".join(pieces)


_FIRMWARE_CALL = "(*(int (*)())"


def _rewrite_firmware_call_wrap(code: str) -> str:
    """Call the compiled function named by a firmware address.

    The address is a `uint32_t` field, a table word, or a `code *` that still
    holds that word. It is not a host function pointer.
    """
    pieces: list[str] = []
    index = 0
    while True:
        found = code.find(_FIRMWARE_CALL, index)
        if found < 0:
            pieces.append(code[index:])
            break
        start = found + len(_FIRMWARE_CALL)
        depth = 0
        end = None
        for cursor in range(start, len(code)):
            char = code[cursor]
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    end = cursor
                    break
                depth -= 1
        if end is None:
            pieces.append(code[index:found + 1])
            index = found + 1
            continue
        expr = code[start:end].strip()
        if expr.startswith("camry_indirect("):
            pieces.append(code[index:end + 1])
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


def apply_firmware_pointers() -> tuple[int, int]:
    """Retarget converted calls and host-pointer rewraps. Equivalent bodies stay."""
    blocked: set[str] = set()
    allowed: set[str] = set()
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    for name, statuses in by_name.items():
        if statuses & {"equivalent", "byte-matched"}:
            blocked.add(name)
        elif "converted" in statuses:
            allowed.add(name)
    functions = 0
    files = 0
    for path in sorted((ROOT / "src" / "all").glob("*.c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        index = 0
        changed = False
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith((" ", "\t", "/*", "//"))
            ):
                out.append(line)
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
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
            chunk = "\n".join(lines[start:index])
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            name = match.group(1) if match else ""
            if name in allowed and name not in blocked:
                updated = _rewrite_firmware_pointers(chunk)
                if updated != chunk:
                    functions += 1
                    changed = True
                    chunk = updated
            out.extend(chunk.split("\n"))
        if changed:
            path.write_text("\n".join(out) + "\n", encoding="utf-8")
            files += 1
    return functions, files


def apply_runtime_tp() -> tuple[int, int]:
    """Retarget converted tp-relative addresses. Equivalent bodies stay."""
    blocked: set[str] = set()
    allowed: set[str] = set()
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    for name, statuses in by_name.items():
        if statuses & {"equivalent", "byte-matched"}:
            blocked.add(name)
        elif "converted" in statuses:
            allowed.add(name)
    functions = 0
    files = 0
    for path in sorted((ROOT / "src" / "all").glob("*.c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        index = 0
        changed = False
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith((" ", "\t", "/*", "//"))
            ):
                out.append(line)
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
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
            chunk = "\n".join(lines[start:index])
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            name = match.group(1) if match else ""
            if name in allowed and name not in blocked:
                updated = _rewrite_runtime_tp(chunk)
                if updated != chunk:
                    functions += 1
                    changed = True
                    chunk = updated
            out.extend(chunk.split("\n"))
        if changed:
            path.write_text("\n".join(out) + "\n", encoding="utf-8")
            files += 1
    return functions, files


def apply_scaled_tables() -> tuple[int, int]:
    """Retarget converted `&PTR_DAT + index` uses. Equivalent bodies stay."""
    blocked: set[str] = set()
    allowed: set[str] = set()
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    for name, statuses in by_name.items():
        if statuses & {"equivalent", "byte-matched"}:
            blocked.add(name)
        elif "converted" in statuses:
            allowed.add(name)
    functions = 0
    files = 0
    for path in sorted((ROOT / "src" / "all").glob("*.c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        index = 0
        changed = False
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith((" ", "\t", "/*", "//"))
            ):
                out.append(line)
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
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
            chunk = "\n".join(lines[start:index])
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            name = match.group(1) if match else ""
            if name in allowed and name not in blocked:
                updated = _rewrite_scaled_table(chunk)
                if updated != chunk:
                    functions += 1
                    changed = True
                    chunk = updated
            out.extend(chunk.split("\n"))
        if changed:
            path.write_text("\n".join(out) + "\n", encoding="utf-8")
            files += 1
    return functions, files


def apply_indirect_dispatch() -> tuple[int, int]:
    """Point converted firmware-address calls at camry_indirect. Equivalent bodies stay."""
    blocked: set[str] = set()
    allowed: set[str] = set()
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    for name, statuses in by_name.items():
        if statuses & {"equivalent", "byte-matched"}:
            blocked.add(name)
        elif "converted" in statuses:
            allowed.add(name)
    functions = 0
    files = 0
    for path in sorted((ROOT / "src" / "all").glob("*.c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        index = 0
        changed = False
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith((" ", "\t", "/*", "//"))
            ):
                out.append(line)
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
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
            chunk = "\n".join(lines[start:index])
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            name = match.group(1) if match else ""
            if name in allowed and name not in blocked:
                updated = _rewrite_indirect_dispatch(chunk)
                if updated != chunk:
                    functions += 1
                    changed = True
                    chunk = updated
            out.extend(chunk.split("\n"))
        if changed:
            path.write_text("\n".join(out) + "\n", encoding="utf-8")
            files += 1
    return functions, files


def _defined_function_names(text: str) -> set[str]:
    names: set[str] = set()
    lines = text.splitlines()
    index = 0
    skip = {"if", "for", "while", "switch", "return", "sizeof"}
    while index < len(lines):
        raw = lines[index]
        index += 1
        if not raw or raw[0] in " \t#/*}" or raw.startswith("static"):
            continue
        buf = raw.strip()
        while index < len(lines) and "{" not in buf and ";" not in buf:
            nxt = lines[index]
            if not nxt.strip() or nxt.startswith(("/*", " *", " */", "//")):
                index += 1
                continue
            if "(" in buf and nxt[0] not in " \t{":
                break
            buf += " " + nxt.strip()
            index += 1
            if len(buf) > 1500:
                break
        head = buf.split("{", 1)[0]
        if "{" not in buf or ";" in head:
            continue
        paren = head.find("(")
        if paren < 0:
            continue
        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", head[:paren])
        if match and match.group(1) not in skip:
            names.add(match.group(1))
    return names


def write_indirect_table(path: Path, sources: list[Path]) -> None:
    """Map linked function addresses to their compiled bodies."""
    addresses: dict[str, int] = {}
    for row in load_symbols():
        addresses.setdefault(row["name"], int(row["addr"], 16))
    chosen: dict[int, str] = {}
    for source in sources:
        for name in _defined_function_names(source.read_text(encoding="utf-8")):
            addr = addresses.get(name)
            if addr is None or addr in chosen:
                continue
            chosen[addr] = name
    lines = [
        "#include <stdint.h>",
        "typedef struct { uint32_t address; void *function; } camry_indirect_slot;",
    ]
    for addr in sorted(chosen):
        lines.append(f"extern void {chosen[addr]}();")
    lines.append("const camry_indirect_slot camry_indirect_slots[] = {")
    if not chosen:
        lines.append("    {0u, 0},")
    for addr in sorted(chosen):
        lines.append(f"    {{0x{addr:x}u, (void *){chosen[addr]}}},")
    lines.append("};")
    lines.append(f"const uint32_t camry_indirect_count = {len(chosen)}u;")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def _matching_open_paren(code: str, close: int) -> int | None:
    depth = 0
    index = close
    while index >= 0:
        char = code[index]
        if char == ")":
            depth += 1
        elif char == "(":
            depth -= 1
            if depth == 0:
                return index
        index -= 1
    return None


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
    slots = _uint32_slot_names()
    spans = _comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    for match in _SLOT_WORD_DEREF.finditer(code):
        if match.start() < cursor or _span_contains(spans, match.start()):
            continue
        if match.group(2) not in slots or not _is_deref_star(code, match.start()):
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(_typed_load(match.group(2), _SLOT_WORD_CTYPE[match.group(1)]))
        cursor = match.end()
    pieces.append(code[cursor:])
    return "".join(pieces)


def _leading_byte_cast(code: str, index: int) -> int | None:
    """Start of a `(byte)` / `(char)` cast whose operand begins at `index`."""
    cursor = index - 1
    while cursor >= 0 and code[cursor] in " \t\n\r":
        cursor -= 1
    if cursor < 0 or code[cursor] != ")":
        return None
    depth = 0
    start = cursor
    while start >= 0:
        if code[start] == ")":
            depth += 1
        elif code[start] == "(":
            depth -= 1
            if depth == 0:
                inner = " ".join(code[start + 1:cursor].split())
                width = _POINTEE_WIDTH.get(inner)
                if "*" in inner or width is None or width[1] != 1:
                    return None
                return start
        start -= 1
    return None


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
    """The value at [start, end) is a byte load, not a word."""
    if _leading_byte_cast(code, start) is not None:
        return True
    assigned = _assigned_byte(code, start, destinations)
    if assigned is not None and assigned[1] == 1:
        return True
    nxt = _skip_space(code, end)
    if code.startswith(("==", "!="), nxt):
        rhs_end = _scan_side(code, nxt + 2, 1, ",;)")
        return _expr_is_byte(code[nxt + 2:rhs_end], destinations)
    op, op_at = _compare_before(code, start)
    if op in {"==", "!="}:
        lhs_at = _scan_side(code, op_at - 1, -1, ",;(")
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
            index = _match_bracket_back(code, index) - 1
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
    for row in _struct_rows().values():
        for field in row["fields"]:
            base, stars, array = _ghidra_base(field["type"])
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
    functions = _function_types()
    found: dict[str, set[str | None]] = {}
    for row in _struct_rows().values():
        for field in row["fields"]:
            base, stars, array = _ghidra_base(field["type"])
            kind: str | None = base if stars == 2 and not array and base not in functions else None
            found.setdefault(field["name"], set()).add(kind)
    _DOUBLE_POINTERS = {
        name: next(iter(kinds))
        for name, kinds in found.items()
        if len(kinds) == 1 and None not in kinds
    }
    return _DOUBLE_POINTERS


def _rewrite_loaded_word_indexes(code: str) -> str:
    """`(byte)SLOT[index]` is the byte at the loaded pointer plus the index.

    The slot macro is the pointer word. A word-scaled `SLOT[1]` has no byte
    cast and stays a subscript.
    """
    slots = _uint32_slot_names()
    spans = _comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\[", code):
        if match.start() < cursor or _span_contains(spans, match.start()):
            continue
        if match.group(1) not in slots:
            continue
        cast_at = _leading_byte_cast(code, match.start())
        if cast_at is None or cast_at < cursor:
            continue
        try:
            end = _match_bracket(code, match.end() - 1)
        except ValueError:
            continue
        nxt = _skip_space(code, end + 1)
        if nxt < len(code) and code[nxt] == "[":
            continue
        index = code[match.end():end]
        pieces.append(code[cursor:cast_at])
        pieces.append(_typed_load(
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
    tables = _uint32_array_names()
    spans = _comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    start = 0
    while True:
        bracket = code.find("[", start)
        if bracket < 0:
            pieces.append(code[cursor:])
            break
        if bracket < cursor or _span_contains(spans, bracket):
            start = bracket + 1
            continue
        close = bracket - 1
        while close >= cursor and code[close] in " \t\n":
            close -= 1
        inner_open = None
        if close >= cursor and code[close] == "]":
            try:
                inner_open = _match_bracket_back(code, close)
            except ValueError:
                inner_open = None
        if inner_open is not None and inner_open >= cursor:
            field = _ident_before(code, inner_open)
            base_start = _subscript_expr_start(code, inner_open)
            try:
                end = _match_bracket(code, bracket)
            except ValueError:
                start = bracket + 1
                continue
            nxt = _skip_space(code, end + 1)
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
                pieces.append(_typed_load(
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
            end = _match_bracket(code, bracket)
        except ValueError:
            start = bracket + 1
            continue
        index = code[bracket + 1:end]
        field_expr = code[receiver:field_at].strip()
        pieces.append(code[cursor:receiver])
        pieces.append(_host_pointer(
            _typed_load(
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
    kind = _kind_context(_c_signature(code), code)
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
        open_paren = _matching_open_paren(code, close)
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
        if _is_pointer_type(collapsed) or _is_int_type(collapsed) or not _address_sum(inner):
            start = bracket + 1
            continue
        if kind(inner) != "integer":
            start = bracket + 1
            continue
        try:
            end = _match_bracket(code, bracket)
        except ValueError:
            start = bracket + 1
            continue
        index = _rewrite_integer_subscripts(code[bracket + 1:end])
        address = _rewrite_integer_subscripts(inner)
        pieces.append(code[cursor:open_paren])
        pieces.append(_typed_load(f"({address}) + (uint32_t)({index})", "uint8_t"))
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
            close = _match_paren(code, open_paren)
        except ValueError:
            start = at + len(needle)
            continue
        if not code.startswith("))", close + 1):
            start = close + 1
            continue
        bracket = _skip_space(code, close + 3)
        if bracket >= len(code) or code[bracket] != "[":
            start = close + 1
            continue
        try:
            end = _match_bracket(code, bracket)
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
    return code[prev] in "\n;{}(,=*&!~?:["


def _stored_pointer_pointees(code: str) -> dict[str, tuple[str, int]]:
    """`(char *)` / `(int *)` on a uint32 slot is the width of `*slot`."""
    slots = _uint32_slot_names()
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
    for name, _address, expansion in _named_macros():
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
    depth = 0
    cursor = index
    while cursor >= 0:
        if code[cursor] == ")":
            depth += 1
        elif code[cursor] == "(":
            depth -= 1
            if depth == 0:
                inner = " ".join(code[cursor + 1:index].split())
                if "*" in inner:
                    return None
                width = _POINTEE_WIDTH.get(inner)
                if width is not None and width[1] <= 2:
                    return width
                return None
        cursor -= 1
    return None


def _compared_with_char(code: str, end: int) -> bool:
    nxt = _skip_space(code, end)
    if not code.startswith(("==", "!="), nxt):
        return False
    rhs = _skip_space(code, nxt + 2)
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
    nxt = _skip_space(code, end)
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


def _typed_load(addr: str, ctype: str) -> str:
    return f"(*((volatile {ctype} *)camry_host_ptr((uint32_t)({addr}))))"


def _slot_deref(code: str, star: int, slots: set[str]) -> tuple[str, int] | None:
    at = _skip_space(code, star + 1)
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[at:])
    if match is None or match.group(0) not in slots:
        return None
    end = at + match.end()
    nxt = _skip_space(code, end)
    if nxt < len(code) and code[nxt] == "[":
        return None
    return match.group(0), end


def _word_deref(code: str, star: int) -> int | None:
    at = _skip_space(code, star + 1)
    if at >= len(code) or code[at] != "(":
        return None
    try:
        end = _match_paren(code, at)
    except ValueError:
        return None
    if _is_word_load(code[at:end + 1]):
        return end + 1
    return None


def _slot_widths(
    code: str,
    pointees: dict[str, tuple[str, int]],
    destinations: dict[str, tuple[str, int]],
) -> dict[str, tuple[str, int]]:
    slots = _uint32_slot_names()
    widths = {name: width for name, width in pointees.items() if name in slots}
    conflicts: set[str] = set()
    index = 0
    while index < len(code):
        if not _is_deref_star(code, index):
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
    spans = _comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    index = 0
    while index < len(code):
        if _span_contains(spans, index):
            index += 1
            continue
        if _is_deref_star(code, index):
            parsed = _slot_deref(code, index, slots)
            if parsed is not None:
                name, end = parsed
                pieces.append(code[cursor:index])
                pieces.append(_typed_load(name, widths[name][0]))
                cursor = end
                index = end
                continue
            word_end = _word_deref(code, index)
            if word_end is not None:
                width = _anon_load_width(code, index, word_end, destinations)
                if width is not None:
                    at = _skip_space(code, index + 1)
                    pieces.append(code[cursor:index])
                    pieces.append(_typed_load(code[at:word_end], width[0]))
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
                nxt = _skip_space(code, index + len(name))
                if nxt < len(code) and code[nxt] == "[":
                    try:
                        end = _match_bracket(code, nxt)
                    except ValueError:
                        end = -1
                    if end >= 0:
                        inner = _rewrite_stored_pointer_loads(code[nxt + 1:end], pointees)
                        ctype, size = widths[name]
                        pieces.append(code[cursor:index])
                        pieces.append(_typed_load(
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
        base, stars, array = _ghidra_base(field["type"])
        if stars or array or base not in structs:
            return None
        current = base
        current_ptr = False
    if current_ptr:
        return None
    return current


def _rewrite_nested_pointer_fields(code: str) -> str:
    """`obj.nested.pointer_field[i]` uses the layout pointee, one field past a struct."""
    pointed = _pointer_field_types()
    if not pointed:
        return code
    by_field: dict[str, dict[str, str]] = {}
    for (struct, field), element in pointed.items():
        by_field.setdefault(field, {})[struct] = element
    var_types, struct_pointers = _struct_bindings(code)
    if not var_types:
        return code
    structs = _struct_rows()
    pattern = re.compile(
        r"(?:->|\.)\s*("
        + "|".join(re.escape(name) for name in sorted(by_field, key=len, reverse=True))
        + r")\b"
    )
    spans = _comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    for match in pattern.finditer(code):
        if match.start() < cursor or _span_contains(spans, match.start()):
            continue
        if _enclosing_call(code, match.start(), "camry_host_ptr"):
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
        nxt = _skip_space(code, match.end())
        star = start - 1
        while star >= 0 and code[star] in " \t\n\r":
            star -= 1
        deref = star >= 0 and _is_deref_star(code, star)
        arithmetic = (
            nxt < len(code)
            and code[nxt] in "+-"
            and not (nxt + 1 < len(code) and code[nxt + 1] in "=+-")
        )
        if not (deref or arithmetic or (nxt < len(code) and code[nxt] == "[")):
            continue
        pieces.append(code[cursor:start])
        pieces.append(_host_pointer(code[start:match.end()], element))
        cursor = match.end()
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_body(code: str) -> str:
    code = _strip_calling_convention(code)
    code = _widen_signature(code)
    code = _rewrite_preserved_results(code)
    code = _rewrite_recovered_arguments(code)
    code = _rewrite_returned_call(code)
    code = _rewrite_saved_pmr(code)
    code = _rewrite_stored_result(code)
    code = _rewrite_held_result(code)
    code = _rewrite_firmware_bases(code)
    signature = _c_signature(code)
    pointers = _pointer_names(signature, code)
    code = _rewrite_bitfields(code)
    code = _rewrite_thunk_calls(code)
    code = _IDIOM.sub(r"((\1 < 0) || (\2 < 0))", code)
    code = _rewrite_indexed(code)
    code = _rewrite_addresses(code, pointers)
    code = _rewrite_device_pointer_add(code)
    code = _rewrite_symbol_indexes(code)
    code = _rewrite_explicit_fields(code)
    code = _rewrite_named_addresses(code, pointer_return=_returns_pointer(signature))
    code = _rewrite_pointer_tables(code)
    code = _rewrite_pointer_to_int(code, pointers)
    code = _rewrite_int_to_pointer(code, pointers)
    code = _rewrite_pointer_calls(code, pointers)
    code = _rewrite_function_indexes(code)
    code = _rewrite_function_values(code)
    code = _rewrite_signed_byte_compares(code)
    code = _rewrite_struct_fields(code)
    code = _rewrite_pointer_assignments(code)
    code = _rewrite_indirect_calls(code)
    pointees = _stored_pointer_pointees(code)
    code = _rewrite_pointer_compares(code, pointers)
    code = _rewrite_wide_call_constants(code)
    code = _rewrite_icus(code)
    code = _rewrite_nested_pointer_fields(code)
    code = _rewrite_stored_pointer_loads(code, pointees)
    code = _rewrite_runtime_gp(code)
    code = _rewrite_signed_values(code)
    code = _rewrite_system_inputs(code)
    code = _rewrite_firmware_pointers(code)
    code = _rewrite_runtime_tp(code)
    code = _rewrite_scaled_table(code)
    code = _rewrite_loaded_pointer_subscripts(code)
    code = _rewrite_integer_subscripts(code)
    code = _rewrite_loaded_word_indexes(code)
    code = _rewrite_pointer_word_indexes(code)
    code = _rewrite_late_pointer_fields(code)
    code = _rewrite_pointer_assignments(code, firmware=True)
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


def _array_macro(name: str, addr: int, ctype: str) -> str:
    """A two-dimensional table is a pointer to its inner row."""
    row = re.fullmatch(r"(.+) \[(\d+)\]", ctype)
    if row:
        return (
            f"#define {name} ((volatile {row.group(1)} (*)[{row.group(2)}])"
            f"camry_host_ptr(0x{addr:x}u))"
        )
    return f"#define {name} ((volatile {ctype} *)camry_host_ptr(0x{addr:x}u))"


def _data_symbols() -> dict[str, int]:
    return {name: addr for name, (addr, _ctype, _array) in _data_layouts().items()}


_DATA_LAYOUTS: dict[str, tuple[int, str, bool]] | None = None


def _data_layouts() -> dict[str, tuple[int, str, bool]]:
    global _DATA_LAYOUTS
    if _DATA_LAYOUTS is not None:
        return _DATA_LAYOUTS
    rows = list(_load_jsonl(ROOT / "data.jsonl"))
    by_addr = {_address(row["addr"]): row for row in rows}

    def concrete_type(type_name: str, seen: set[int]) -> str:
        """`@0xADDR` is the type of the object already defined at that address."""
        type_name = type_name.replace(" ", "")
        if not type_name.startswith("@"):
            return type_name
        try:
            addr = _address(type_name[1:])
        except ValueError:
            return type_name
        if addr in seen:
            return type_name
        dest = by_addr.get(addr)
        if dest is None:
            return type_name
        return concrete_type(dest["type"], seen | {addr})

    found: dict[str, tuple[int, str, bool]] = {}
    for row in rows:
        addr = _address(row["addr"])
        type_name = concrete_type(row["type"], set())
        if "[" in type_name:
            element = type_name.split("[", 1)[0]
            dims = [int(item) for item in re.findall(r"\[(\d+)\]", type_name)]
            if element in _ARRAY_ELEMENTS:
                ctype, _scale = _ARRAY_ELEMENTS[element]
                # element[inner][outer] is C outer rows of inner elements.
                if len(dims) == 2:
                    ctype = f"{ctype} [{dims[0]}]"
                found[row["name"]] = (addr, ctype, True)
            elif re.fullmatch(r"[A-Z][A-Za-z0-9_]*", element):
                found[row["name"]] = (addr, element, True)
            else:
                found[row["name"]] = (addr, "uint8_t", False)
            continue
        if re.fullmatch(r"[A-Z][A-Za-z0-9_]*", type_name) and type_name in _struct_rows():
            found[row["name"]] = (addr, type_name, False)
            continue
        ctype = _SCALAR_TYPES.get(type_name) or _scalar_type(addr, "uint8_t")
        found[row["name"]] = (addr, ctype, False)
    _DATA_LAYOUTS = found
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


def _header_pointer_returns() -> set[str]:
    """Prototypes in common.h win over a void corpus signature.

    Equivalent bodies such as `FUN_00075bfe` return `undefined *`. The corpus
    text still says void, and the caller compares r10 as an integer.
    """
    header = ROOT / "src" / "all" / "common.h"
    found: set[str] = set()
    if not header.exists():
        return found
    for line in header.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text.endswith(";") or "(" not in text or not _returns_pointer(text[:-1]):
            continue
        name = text.split("(", 1)[0].split()[-1].lstrip("*")
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            found.add(name)
    return found


def _pointer_return_names() -> set[str]:
    global _POINTER_RETURNS
    if _POINTER_RETURNS is None:
        _POINTER_RETURNS = {
            row["name"]
            for row in _corpus_functions()
            if _returns_pointer(_c_signature(row["decompiled_c"]))
        }
        _POINTER_RETURNS.update(_header_pointer_returns())
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
            lines.append(_array_macro(name, addr, ctype))
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
    "-Wno-uninitialized",
    "-Wno-deprecated-non-prototype",
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


_TYPE_LAYOUTS: dict | None = None
_SCALAR_FIELDS: dict[tuple[str, str], str] | None = None
_POINTER_FIELDS: dict[tuple[str, str], str] | None = None
_FIELD_C = {
    "byte": "uint8_t", "uchar": "uint8_t", "char": "uint8_t",
    "undefined": "uint8_t", "undefined1": "uint8_t", "code": "uint8_t",
    "sbyte": "int8_t",
    "ushort": "uint16_t", "undefined2": "uint16_t",
    "short": "int16_t",
    "uint": "uint32_t", "dword": "uint32_t", "ulong": "uint32_t", "undefined4": "uint32_t",
    "int": "int32_t",
    "undefined8": "uint64_t",
    "float": "float", "double": "double",
}
_FIELD_ACCESS = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)(\s*\[[^\[\]]*\])?\s*(->|\.)\s*([A-Za-z_][A-Za-z0-9_]*)"
)


def _type_layouts() -> dict:
    global _TYPE_LAYOUTS
    if _TYPE_LAYOUTS is None:
        path = ROOT / "struct_layouts.json"
        if path.exists():
            _TYPE_LAYOUTS = json.loads(path.read_text(encoding="utf-8"))
        else:
            _TYPE_LAYOUTS = {"structs": [], "functions": [], "enums": []}
    return _TYPE_LAYOUTS


def _struct_rows() -> dict[str, dict]:
    return {row["name"]: row for row in _type_layouts().get("structs") or []}


def _function_types() -> set[str]:
    return set(_type_layouts().get("functions") or [])


def _ghidra_base(type_name: str) -> tuple[str, int, str]:
    text = type_name.strip()
    array = ""
    match = re.search(r"\[(\d+)\]$", text)
    if match:
        array = f"[{match.group(1)}]"
        text = text[:match.start()].strip()
    base = " ".join(text.replace("*32", " ").replace("*", " ").split())
    return base, text.count("*"), array


def _field_c(type_name: str, size: int, structs: set[str]) -> tuple[str, str]:
    """A firmware pointer is four bytes on this target, including inside a struct."""
    base, stars, array = _ghidra_base(type_name)
    if stars:
        return "uint32_t", array
    if base in _FIELD_C:
        return _FIELD_C[base], array
    if base in structs:
        return base, array
    fallback = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t", 8: "uint64_t"}.get(size)
    if fallback and not array:
        return fallback, ""
    return "uint8_t", array or f"[{size}]"


def _pointed_c_type(type_name: str) -> str | None:
    base, stars, array = _ghidra_base(type_name)
    if stars != 1 or array or base in _function_types():
        return None
    if base in _FIELD_C:
        return _FIELD_C[base]
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", base):
        return base
    return None


def _scalar_field_kinds() -> dict[tuple[str, str], str]:
    global _SCALAR_FIELDS
    if _SCALAR_FIELDS is not None:
        return _SCALAR_FIELDS
    found: dict[tuple[str, str], str] = {}
    rows = _struct_rows()
    for name, row in rows.items():
        for field in row["fields"]:
            base, stars, array = _ghidra_base(field["type"])
            if array and not stars:
                continue
            if not stars and base in rows:
                continue
            found[(name, field["name"])] = "integer"
    _SCALAR_FIELDS = found
    return found


def _pointer_field_types() -> dict[tuple[str, str], str]:
    global _POINTER_FIELDS
    if _POINTER_FIELDS is not None:
        return _POINTER_FIELDS
    found: dict[tuple[str, str], str] = {}
    for name, row in _struct_rows().items():
        for field in row["fields"]:
            pointed = _pointed_c_type(field["type"])
            if pointed is not None:
                found[(name, field["name"])] = pointed
    _POINTER_FIELDS = found
    return found


def _struct_bindings(code: str) -> tuple[dict[str, str], set[str]]:
    structs = set(_struct_rows())
    found: dict[str, str] = {}
    pointers: set[str] = set()
    for name, (_addr, ctype, is_array) in _data_layouts().items():
        if ctype in structs:
            found[name] = ctype
            if is_array:
                pointers.add(name)
    for match in re.finditer(
        r"\b([A-Z][A-Za-z0-9_]*)\s*(\*+)?\s*([A-Za-z_][A-Za-z0-9_]*)\s*[,;=)]",
        code,
    ):
        if match.group(1) not in structs:
            continue
        found[match.group(3)] = match.group(1)
        if match.group(2):
            pointers.add(match.group(3))
        else:
            pointers.discard(match.group(3))
    return found, pointers


def _struct_var_types(code: str) -> dict[str, str]:
    names, _pointers = _struct_bindings(code)
    return names


def _scalar_field_kind(
    name: str,
    rest: str,
    var_structs: dict[str, str] | None,
    field_kinds: dict[tuple[str, str], str] | None,
) -> str | None:
    if not var_structs or not field_kinds or not rest:
        return None
    match = re.fullmatch(
        r"(?:\[[^\[\]]*\])?\s*(?:->|\.)\s*([A-Za-z_][A-Za-z0-9_]*)",
        rest,
    )
    if match is None:
        return None
    struct = var_structs.get(name)
    if struct is None:
        return None
    return field_kinds.get((struct, match.group(1)))


def _byvalue_deps(row: dict, structs: dict[str, dict]) -> list[str]:
    deps: list[str] = []
    for field in row["fields"]:
        base, stars, _array = _ghidra_base(field["type"])
        if stars == 0 and base in structs:
            deps.append(base)
    return deps


def _one_struct(row: dict, structs: set[str]) -> list[str]:
    lines = [f"struct {row['name']} {{"]
    cursor = 0
    for field in row["fields"]:
        if field["offset"] > cursor:
            lines.append(f"    uint8_t _pad_{cursor}[{field['offset'] - cursor}];")
        ctype, array = _field_c(field["type"], field["size"], structs)
        lines.append(f"    {ctype} {field['name']}{array};")
        cursor = field["offset"] + field["size"]
    if row["size"] > cursor:
        lines.append(f"    uint8_t _pad_{cursor}[{row['size'] - cursor}];")
    lines.append("};")
    lines.append(
        f'_Static_assert(sizeof(struct {row["name"]}) == {row["size"]}, "{row["name"]}");'
    )
    return lines


def _struct_definitions(structs: dict[str, dict]) -> list[str]:
    pending = set(structs)
    lines: list[str] = []
    while pending:
        ready = [
            name for name in sorted(pending)
            if all(dep not in pending for dep in _byvalue_deps(structs[name], structs))
        ]
        if not ready:
            break
        for name in ready:
            lines.extend(_one_struct(structs[name], set(structs)))
            pending.remove(name)
    return lines


def _comment_spans(code: str) -> list[tuple[int, int]]:
    return [match.span() for match in re.finditer(r"/\*.*?\*/|//.*?$", code, re.S | re.M)]


def _span_contains(spans: list[tuple[int, int]], pos: int) -> bool:
    for start, end in spans:
        if start <= pos < end:
            return True
        if start > pos:
            return False
    return False


def _next_code(code: str, index: int) -> int:
    while index < len(code) and code[index] in " \t\r\n":
        index += 1
    return index


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
    spans = _comment_spans(code)
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
            and not _span_contains(spans, index)
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


def _integer_pointer_targets(signature: str, code: str) -> set[str]:
    """Names declared as one pointer to an integer, such as `undefined4 *slot`."""
    pattern = re.compile(
        r"\b(?:unsigned\s+int|unsigned\s+long|signed\s+int|undefined[1248]?|"
        r"uint|ulong|ushort|byte|uchar|char|short|int|long|bool|code|"
        r"uint32_t|uint16_t|uint8_t|int32_t|int16_t|int8_t)\s*\*\s*"
        r"([A-Za-z_][A-Za-z0-9_]*)"
    )
    return set(pattern.findall(signature + "\n" + code))


def _uint32_array_names() -> set[str]:
    """common.h macros that are a `uint32_t` table, so a subscript loads one word."""
    return {
        name
        for name, _address, expansion in _named_macros()
        if expansion.startswith("((volatile uint32_t *)camry_host_ptr(")
    }


_UINT32_SLOTS: set[str] | None = None


def _uint32_slot_names() -> set[str]:
    """common.h macros that load one stored pointer word."""
    global _UINT32_SLOTS
    if _UINT32_SLOTS is None:
        _UINT32_SLOTS = {
            name
            for name, _address, expansion in _named_macros()
            if expansion.startswith("(*((volatile uint32_t *)camry_host_ptr(")
        }
    return _UINT32_SLOTS


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
        close = _match_paren(text, open_paren)
    except ValueError:
        return False
    return text[close + 1:].strip() == "))"


def _is_uint32_subscript(text: str, arrays: set[str]) -> bool:
    match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[", text)
    if match is None or match.group(1) not in arrays:
        return False
    try:
        end = _match_bracket(text, match.end() - 1)
    except ValueError:
        return False
    return text[end + 1:].strip() == ""


def _is_firmware_address(expr: str, arrays: set[str], kind) -> bool:
    """One loaded firmware word, plus integer byte offsets."""
    parts = _split_additive(expr.strip())
    if not parts or any(not part for part in parts):
        return False
    words = 0
    for part in parts:
        if _is_word_load(part) or _is_uint32_subscript(part, arrays):
            words += 1
        elif kind(part) != "integer":
            return False
    return words == 1


def _used_as_firmware_bits(code: str, name: str) -> bool:
    """The name is added inside `camry_host_ptr`, so it still holds an address word."""
    for match in re.finditer(rf"\b{re.escape(name)}\b", code):
        if _enclosing_call(code, match.start(), "camry_host_addr"):
            continue
        if _enclosing_call(code, match.start(), "camry_host_ptr"):
            return True
    return False


def _cast_struct_access(code: str, op_at: int) -> tuple[int, str] | None:
    """`((Struct *)expr)[index].field` starts at the outer paren."""
    index = op_at - 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    while index >= 0 and code[index] == "]":
        try:
            index = _match_bracket_back(code, index) - 1
        except ValueError:
            return None
        while index >= 0 and code[index] in " \t\n\r":
            index -= 1
    if index < 0 or code[index] != ")":
        return None
    try:
        open_paren = _match_paren_back(code, index)
    except ValueError:
        return None
    inner = code[open_paren + 1:index].strip()
    if not inner.startswith("("):
        return None
    try:
        cast_end = _match_paren(inner, 0)
    except ValueError:
        return None
    cast = " ".join(inner[1:cast_end].split())
    if not cast.endswith("*"):
        return None
    struct = " ".join(
        cast[:-1].replace("volatile", " ").replace("const", " ").replace("struct", " ").split()
    )
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", struct) is None:
        return None
    return open_paren, struct


def _rewrite_late_pointer_fields(code: str) -> str:
    """A cast row's pointer field is a firmware address indexed in elements.

    `((Channel *)base)[i].receive_rows + n` is the bytes' `shl` by the row size.
    The field is a uint32 in the C struct, so the add would otherwise be a byte add.
    """
    pointed = _pointer_field_types()
    if not pointed:
        return code
    by_field: dict[str, dict[str, str]] = {}
    for (struct, field), element in pointed.items():
        by_field.setdefault(field, {})[struct] = element
    pattern = re.compile(
        r"(?:->|\.)\s*(" + "|".join(re.escape(name) for name in sorted(by_field, key=len, reverse=True)) + r")\b"
    )
    pieces: list[str] = []
    cursor = 0
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        if _enclosing_call(code, match.start(), "camry_host_ptr"):
            continue
        found = _cast_struct_access(code, match.start())
        if found is None:
            continue
        start, struct = found
        element = by_field[match.group(1)].get(struct)
        if element is None:
            continue
        nxt = _skip_space(code, match.end())
        if nxt >= len(code) or code[nxt] not in "+-,;)[":
            continue
        if code[nxt] in "+-" and nxt + 1 < len(code) and code[nxt + 1] in "=+-":
            continue
        pieces.append(code[cursor:start])
        pieces.append(_host_pointer(code[start:match.end()], element))
        cursor = match.end()
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_pointer_assignments(code: str, *, firmware: bool = False) -> str:
    """Store a firmware address in a pointer, and a pointer into an integer."""
    brace = _opening_brace(code)
    if brace < 0:
        return code
    signature = _c_signature(code)
    kind = _kind_context(signature, code)
    integer_targets = _integer_pointer_targets(signature, code)
    arrays = _uint32_array_names() if firmware else set()
    body = code[brace:]
    replacements: list[tuple[int, int, str]] = []
    lhs_stops = ",;{}:" if firmware else ",;{}"
    for site in _assignment_sites(body, nested=firmware):
        lhs_at = _scan_side(body, site - 1, -1, lhs_stops)
        rhs_at = _scan_side(body, site + 1, 1, ",;")
        lhs = body[lhs_at:site].strip()
        rhs = body[site + 1:rhs_at].strip()
        if not lhs or not rhs or replacements and lhs_at < replacements[-1][1]:
            continue
        lhs_kind = kind(lhs)
        rhs_kind = kind(rhs)
        deref = re.fullmatch(r"\*\s*([A-Za-z_][A-Za-z0-9_]*)", lhs)
        if lhs_kind == "unknown" and deref and deref.group(1) in integer_targets:
            lhs_kind = "integer"
        if (
            firmware
            and lhs_kind == "pointer"
            and _is_firmware_address(rhs, arrays, kind)
        ):
            ident = re.search(r"[A-Za-z_][A-Za-z0-9_]*", lhs)
            if ident and _used_as_firmware_bits(body, ident.group(0)):
                continue
            replacements.append((
                site + 1,
                rhs_at,
                f" ((void *)camry_host_ptr((uint32_t)({rhs})))",
            ))
            continue
        if firmware:
            continue
        if lhs_kind == "pointer" and rhs_kind == "integer":
            replacements.append((
                site + 1,
                rhs_at,
                f" ((void *)camry_host_ptr((uint32_t)({rhs})))",
            ))
            continue
        if lhs_kind == "integer" and rhs_kind == "pointer":
            stored = "0" if _null_pointer(rhs) else f"camry_host_addr({rhs})"
            replacements.append((site + 1, rhs_at, f" {stored}"))
    if not replacements:
        return code
    pieces: list[str] = []
    cursor = 0
    for start, end, text in replacements:
        pieces.append(body[cursor:start])
        pieces.append(text)
        cursor = end
    pieces.append(body[cursor:])
    return code[:brace] + "".join(pieces)


def _rewrite_struct_fields(code: str) -> str:
    """Use a firmware pointer stored in a struct as a host pointer at the use site."""
    brace = _opening_brace(code)
    if brace < 0:
        return code
    structs = _struct_rows()
    pointed = _pointer_field_types()
    if not structs or not pointed:
        return code
    var_types, struct_pointers = _struct_bindings(code)
    if not var_types:
        return code
    signature = _c_signature(code)
    pointers = _pointer_names(signature, code)
    kind = _kind_context(signature, code, pointers)
    body = code[brace:]
    spans = _comment_spans(body)
    struct_names = set(structs)
    replacements: list[tuple[int, int, str]] = []
    for match in _FIELD_ACCESS.finditer(body):
        if _span_contains(spans, match.start()):
            continue
        var, subscript, op, field = match.groups()
        struct = var_types.get(var)
        element = pointed.get((struct, field)) if struct else None
        if struct is None or element is None:
            continue
        is_pointer = var in struct_pointers
        if subscript:
            if not is_pointer or op != ".":
                continue
        elif is_pointer:
            if op != "->":
                continue
        elif op != ".":
            continue
        if replacements and match.start() < replacements[-1][1]:
            continue
        access = match.group(0)
        nxt = _next_code(body, match.end())
        char = body[nxt] if nxt < len(body) else ""
        if char == "[":
            replacements.append((match.start(), match.end(), _host_pointer(access, element)))
            continue
        if body.startswith("->", nxt) and element in struct_names:
            replacements.append((match.start(), match.end(), _host_pointer(access, element)))
            continue
        if match.start() > 0 and body[match.start() - 1] == "*":
            prev = body[match.start() - 2] if match.start() > 1 else ""
            if prev not in "*&/=" and not (prev.isalnum() or prev == "_"):
                replacements.append((
                    match.start() - 1,
                    match.end(),
                    f"*{_host_pointer(access, element)}",
                ))
                continue
        if char == "=" and not body.startswith("==", nxt):
            rhs_at = _rhs_end(body, nxt + 1)
            rhs = body[nxt + 1:rhs_at].strip()
            if not rhs:
                continue
            stored = "0" if _null_pointer(rhs) else (
                f"camry_host_addr({rhs})" if kind(rhs) == "pointer" else ""
            )
            if stored:
                replacements.append((match.start(), rhs_at, f"{access} = {stored}"))
            continue
        boundary = char
        if boundary in ",;)" and body[match.end():nxt].strip() == "":
            prefix = body[:match.start()].rstrip()
            lhs = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*=$", prefix)
            if lhs and lhs.group(1) in pointers and not prefix.endswith("=="):
                replacements.append((
                    match.start(),
                    match.end(),
                    f"((void *)camry_host_ptr((uint32_t)({access})))",
                ))
    if not replacements:
        return code
    pieces: list[str] = []
    cursor = 0
    for start, end, text in replacements:
        pieces.append(body[cursor:start])
        pieces.append(text)
        cursor = end
    pieces.append(body[cursor:])
    return code[:brace] + "".join(pieces)


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
    structs = _struct_rows()
    function_types = _function_types()
    enums = {row["name"]: row for row in _type_layouts().get("enums") or []}
    forbidden = (
        _PRIMITIVE_TYPES | set(registers) | set(data) | function_names
        | function_types | set(enums) | _DEVICE_STRUCT_NAMES
    )
    for name in sorted(function_types):
        if name in function_names or name in registers or name in data:
            continue
        lines.append(f"typedef int {name}();")
    for name, row in sorted(enums.items()):
        if name in function_names:
            continue
        width = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}.get(int(row["size"]), "uint16_t")
        lines.append(f"typedef {width} {name};")
    emitted = False
    for name in sorted(structs):
        if name in forbidden:
            continue
        lines.append(f"typedef struct {name} {name};")
        emitted = True
    for name in sorted(types):
        if name in structs or name in forbidden:
            continue
        lines.append(f"typedef struct {name} {name};")
        emitted = True
    visible = {name: row for name, row in structs.items() if name not in forbidden}
    if visible:
        lines.extend(_struct_definitions(visible))
        emitted = True
    if _DEVICE_STRUCT_NAMES & types:
        lines.append(_DEVICE_STRUCT_TEXT.strip())
        lines.append("_Static_assert(sizeof(RSCFD_TxMessageBuffer) == 32, \"tx buffer\");")
        lines.append("_Static_assert(sizeof(RSCFD_CommonFifoFrame) == 32, \"fifo frame\");")
        lines.append("_Static_assert(sizeof(RSCFD_CFSTS) == 4, \"cfsts\");")
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
            lines.append(_array_macro(name, addr, ctype))
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
    if re.search(r"\bPMR\b", text):
        lines.append("#define PMR camry_pmr")
    # sr24, sel 13 and sr24, sel 4. These are system registers, like PMR.
    for name in ("CDBCR", "ICCTRL"):
        if re.search(rf"\b{name}\b", text):
            lines.append(f"extern volatile uint32_t {name};")
    # Halfwords stored into f33_driver_channel_software_states. The compares
    # against the same slot use these immediates in the same order.
    for name, value in (
        ("start_pending", 0x3BC4),
        ("recovery_pending", 0x3DC2),
        ("stop_pending", 0x3EC1),
        ("running_software_state", 0x57A8),
        ("stopped_software_state", 0x6B94),
        ("initialized", 0x6D92),
        ("uninitialized", 0x6E91),
    ):
        if name not in function_names and re.search(rf"\b{name}\b", text):
            lines.append(f"#define {name} 0x{value:x}")
    if re.search(r"\bICUS_Status\b", text):
        lines.append(
            "typedef union { uint32_t raw; struct { uint32_t BUSY:1; uint32_t _pad:31; }; } ICUS_Status;"
        )
    if re.search(r"\bICUS_Command\b", text):
        lines.append(
            "typedef union { uint32_t raw; struct { uint32_t CMD:8;"
            " uint32_t reserved_8_15:8; uint32_t KEY_SLOT:16; }; } ICUS_Command;"
        )
    ram_widths = _call_facts()["ram"]
    ram_types = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}
    for name in sorted(set(re.findall(r"\b(Ram[0-9A-Fa-f]+)\b", text))):
        if name in function_names or name in registers or name in data:
            continue
        address = int(name[3:], 16)
        width = ram_widths.get(address)
        if width not in ram_types:
            continue
        lines.append(
            f"#define {name} (*((volatile {ram_types[width]} *)camry_host_ptr(0x{address:x}u)))"
        )
    lines.append("")
    for name in sorted(signatures):
        lines.append(signatures[name] + ";")
    lines.extend(_loose_declarations(
        text,
        set(signatures) | _prototype_names() | function_types | set(enums) | set(structs),
    ))
    lines.append("")
    return "\n".join(lines) + "\n"


_PSEUDO_MACROS = {
    "__disable_irq": "#define __disable_irq() (camry_psw |= 0x20u)",
    "__enable_irq": "#define __enable_irq() (camry_psw &= ~0x20u)",
    "halt_baddata": "#define halt_baddata() ((void)0)",
    "builtin_memcpy": "#define builtin_memcpy(dst, src, count) __builtin_memcpy((dst), (src), (count))",
    "CONCAT11": "#define CONCAT11(hi, lo) ((uint32_t)(((uint32_t)(hi) & 0xffu) << 8) | ((uint32_t)(lo) & 0xffu))",
    "CONCAT12": "#define CONCAT12(hi, lo) ((uint32_t)(((uint32_t)(hi) & 0xffu) << 16) | ((uint32_t)(lo) & 0xffffu))",
    "CONCAT13": "#define CONCAT13(hi, lo) ((uint32_t)(((uint32_t)(hi) & 0xffu) << 24) | ((uint32_t)(lo) & 0xffffffu))",
    "CONCAT21": "#define CONCAT21(hi, lo) ((uint32_t)(((uint32_t)(hi) & 0xffffu) << 8) | ((uint32_t)(lo) & 0xffu))",
    "CONCAT22": "#define CONCAT22(hi, lo) ((uint32_t)(((uint32_t)(hi) & 0xffffu) << 16) | ((uint32_t)(lo) & 0xffffu))",
    "CONCAT31": "#define CONCAT31(hi, lo) ((uint32_t)(((uint32_t)(hi) & 0xffffffu) << 8) | ((uint32_t)(lo) & 0xffu))",
    "CONCAT44": "#define CONCAT44(hi, lo) (((uint64_t)(hi) << 32) | (uint32_t)(lo))",
    "SUB41": "#define SUB41(left, right) ((uint32_t)(left) - (uint32_t)(right))",
    "SUB42": "#define SUB42(left, right) ((uint32_t)(left) - (uint32_t)(right))",
    "SUB51": "#define SUB51(left, right) ((uint32_t)(left) - (uint32_t)(right))",
}


_NOT_FUNCTIONS = _PRIMITIVE_TYPES | _INT_TYPES | {
    "floor", "trunc", "ceil", "fabs", "sqrt", "memset", "memcpy", "memcmp",
    "malloc", "free", "abs", "labs",
}


def _loose_declarations(text: str, declared: set[str]) -> list[str]:
    """A call with no prototype is still compiled; pseudo-ops expand, the rest are declared."""
    text = _strip_comments(text)
    called = {
        match.group(1)
        for match in _CALL.finditer(text)
    } - declared - _SKIP_CALLS - _NOT_FUNCTIONS
    if not called:
        return []
    lines = [""]
    for name in sorted(name for name in called if name in _PSEUDO_MACROS):
        lines.append(_PSEUDO_MACROS[name])
        called.remove(name)
    arities: dict[str, set[int]] = {}
    for match in _CALL.finditer(text):
        name = match.group(1)
        if name not in called:
            continue
        try:
            close = _match_paren(text, match.end() - 1)
        except ValueError:
            continue
        parts = _split_args(text[match.end():close])
        count = 0 if len(parts) == 1 and not parts[0].strip() else len(parts)
        arities.setdefault(name, set()).add(count)
    for name in sorted(called):
        if name.startswith(("DAT_", "UNK_", "PTR_", "LAB_")):
            continue
        counts = arities.get(name) or {0}
        if counts == {0}:
            lines.append(f"int {name}(void);")
        else:
            width = max(counts)
            formals = ", ".join(["int"] * width)
            lines.append(f"int {name}({formals});")
    return lines


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
    param_types = {
        name: _signature_param_types(signature) for name, signature in signatures.items()
    }
    param_types.update(_hand_param_types())
    for name in list(rewritten):
        try:
            rewritten[name] = _rewrite_pointer_arguments(rewritten[name], param_types)
        except (ValueError, IndexError, KeyError) as exc:
            failed_rewrite.append(f"{name} {type(exc).__name__}")
            del rewritten[name]
            signatures.pop(name, None)
            rows_by_name.pop(name, None)

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


def cmd_oracle(_args: argparse.Namespace) -> int:
    from tools.camry_oracle import run_oracles

    return run_oracles()


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
    oracle = sub.add_parser(
        "oracle",
        help="compare converted leaves with original bytes and mark only agreements",
    )
    oracle.set_defaults(func=cmd_oracle)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
