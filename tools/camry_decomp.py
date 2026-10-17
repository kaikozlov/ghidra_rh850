#!/usr/bin/env python3
"""Link the Camry CodeFlash image from its symbol map and report decomp status."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
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
    print(json.dumps(report, indent=2))
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    _, report = identity_image()
    named = sum(1 for row in load_symbols() if not row["name"].startswith("FUN_"))
    report["named_functions"] = named
    report["equivalent_functions"] = sum(
        1 for row in report["matched"] if row["status"] == "equivalent"
    )
    report["byte_matched_functions"] = sum(
        1 for row in report["matched"] if row["status"] == "byte-matched"
    )
    print(json.dumps(report, indent=2))
    return 0


_CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_SKIP_CALLS = {
    "if", "for", "while", "switch", "return", "sizeof",
    "camry_host_ptr", "camry_host_addr", "__synchronize",
}
_BLOCK = re.compile(
    r"->|\.[A-Za-z_]|\bcode\s*\*|"
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
        index = code[match.end():end]
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


def _rewrite_addresses(code: str) -> str:
    def integer_cast(match: re.Match[str]) -> str:
        return f"({match.group(1)})0x{int(match.group(2), 16):x}u"

    code = re.sub(
        r"\((unsigned int|int|uint|undefined4|ulong|long)\)\s*"
        r"&(?:LAB|DAT|UNK)_([0-9A-Fa-f]+)",
        integer_cast,
        code,
    )
    return re.sub(
        r"&(?:LAB|DAT|UNK)_([0-9A-Fa-f]+)",
        lambda match: f"((void *)camry_host_ptr(0x{int(match.group(1), 16):x}u))",
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


def _rewrite_body(code: str) -> str:
    signature = _c_signature(code)
    pointers = _pointer_names(signature, code)
    code = _IDIOM.sub(r"((\1 < 0) || (\2 < 0))", code)
    code = _rewrite_indexed(code)
    code = _rewrite_addresses(code)
    code = _rewrite_named_addresses(code)
    code = _rewrite_pointer_to_int(code, pointers)
    code = _rewrite_int_to_pointer(code, pointers)
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


def _rewrite_named_addresses(code: str) -> str:
    names = _absolute_names()

    def replace(match: re.Match[str]) -> str:
        addr = names.get(match.group(1))
        if addr is None:
            return match.group(0)
        return f"(0x{addr:x}u)"

    return re.sub(r"&([A-Za-z_][A-Za-z0-9_]*)\b", replace, code)


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


def _select_corpus(
    functions: list[dict],
    defined: set[str],
    banned: set[str],
    roots: set[int] | None = None,
) -> dict[int, dict]:
    by_addr = {int(row["entry_addr"], 16): row for row in functions}
    eligible = {
        row["name"]: row
        for row in functions
        if row["name"] not in defined
        and row["name"] not in banned
        and _eligible(row["decompiled_c"])
    }
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
            "-DCAMRY_HOST", "-I", str(ROOT / "include"),
            "-o", "/dev/null", str(destination),
        ],
        text=True,
        capture_output=True,
    )


def cmd_corpus(_args: argparse.Namespace) -> int:
    from tests.decomp.verify_camry_decomp import screen_corpus
    from tools.project.analysis_target import target as resolve_target
    from tools.project.pseudo import load_corpus

    metadata = resolve_target(TARGET)[1]
    _meta, functions = load_corpus(REPO_ROOT / metadata["decompiler_corpus"])
    matched_rows = load_matched()
    defined = {row["name"] for row in matched_rows if row.get("form") != "corpus"}
    previous = {_address(row["addr"]) for row in matched_rows if row.get("form") == "corpus"}
    banned: set[str] = set()
    selected = _select_corpus(functions, defined, banned)
    print(f"corpus candidates {len(selected)}")
    destination = ROOT / "src" / "corpus.c"
    if not selected:
        destination.unlink(missing_ok=True)
        print("compiled 0 corpus functions")
        return 0
    rendered = _render_corpus(selected)
    destination.write_text(rendered, encoding="utf-8")
    for _attempt in range(80):
        result = _compile_corpus(destination)
        if result.returncode == 0:
            break
        rendered = destination.read_text(encoding="utf-8")
        dropped = set()
        for line in (result.stderr or "").splitlines():
            match = re.search(r"corpus\.c:(\d+):", line)
            if match is None:
                continue
            name = _function_at_line(selected, rendered, int(match.group(1)))
            if name:
                dropped.add(name)
        if not dropped:
            sys.stderr.write(result.stderr or "")
            return 1
        banned |= dropped
        print(f"dropped {len(dropped)}")
        selected = _select_corpus(functions, defined, banned)
        rendered = _render_corpus(selected)
        destination.write_text(rendered, encoding="utf-8")
        if not selected:
            destination.unlink(missing_ok=True)
            print("compiled 0 corpus functions")
            return 0
    else:
        sys.stderr.write("corpus C did not compile\n")
        return 1
    print(f"compiled {len(selected)} corpus functions")
    rows = [
        {
            "addr": addr,
            "name": row["name"],
            "signature": _c_signature(row["decompiled_c"]),
        }
        for addr, row in selected.items()
        if addr in _oracle_addresses()
    ]
    passed = screen_corpus(rows)
    passed_addrs = {int(row["addr"]) for row in passed}
    lost = previous - passed_addrs
    if lost:
        restore = _select_corpus(functions, defined, banned, roots=previous)
        if restore:
            destination.write_text(_render_corpus(restore), encoding="utf-8")
        sys.stderr.write(
            "previously checked corpus functions failed: "
            + ", ".join(hex(addr) for addr in sorted(lost))
            + "\n"
        )
        return 1
    kept = _select_corpus(functions, defined, banned, roots=passed_addrs)
    if not kept:
        destination.unlink(missing_ok=True)
        print("oracle-checked 0 corpus functions")
        return 0
    destination.write_text(_render_corpus(kept), encoding="utf-8")
    result = _compile_corpus(destination)
    if result.returncode != 0:
        sys.stderr.write(result.stderr or "")
        return 1
    matched_path = ROOT / "matched.jsonl"
    existing = {_address(row["addr"]) for row in load_matched()}
    with matched_path.open("a", encoding="utf-8") as handle:
        for addr in sorted(passed_addrs & set(kept)):
            if addr in existing:
                continue
            handle.write(json.dumps(
                {
                    "addr": hex(addr),
                    "name": kept[addr]["name"],
                    "status": "equivalent",
                    "form": "corpus",
                },
                separators=(", ", ": "),
            ) + "\n")
    print(f"oracle-checked {len(passed_addrs & set(kept))} corpus functions")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    identity = sub.add_parser("identity", help="link an image identical to CodeFlash")
    identity.add_argument("--output", help="write the linked image here")
    identity.set_defaults(func=cmd_identity)
    status = sub.add_parser("status", help="print image and matched-function counts")
    status.set_defaults(func=cmd_status)
    corpus = sub.add_parser("corpus", help="compile decompiler bodies that close over existing C")
    corpus.set_defaults(func=cmd_corpus)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
