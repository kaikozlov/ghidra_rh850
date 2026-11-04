"""Emit the C form of the two primitive-only P1MEFaci Java routines.

Supported syntax: fixed void signatures, signed int/long locals, primitive array
access, if/for/return/break, integer literals, assignments, comparisons, arithmetic,
bitwise AND/OR and conditional expressions. The sole narrowing cast is the
bounded physical-cell index. No calls, shifts, allocation, fields, strings,
floating point, unsigned arithmetic or raw backslash-u sequences.
Method bodies are copied; only primitive types, null and function names change.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

from tools import REPO_ROOT

SOURCE = REPO_ROOT / "ghidra/scripts/emulate/P1MEFaci.java"
OUTPUT = REPO_ROOT / "data/generated/p1me_faci.h"
SIGNATURES = (
    "static void blankCheck(byte[] cells, long start, long end, long size, int decrement, long[] result)",
    "static void complete(long previousStatus, long access, int operation, long firstDirty, long[] result)",
)
TOKEN = re.compile(r"\s+|0[xX][0-9a-fA-F]+|[0-9]+|[A-Za-z_]\w*|>>>|>>|<<|\+\+|--|->|==|!=|<=|>=|&&|\|\||\+=|\|=|[{}()\[\];,?:=+*/%&|<>-]|.")
KEYWORDS = {"static", "void", "byte", "long", "int", "if", "for", "return", "break", "null"}
OPERATORS = set("{}()[];,?:=+*/%&|<>-") | {"==", "!=", "<=", ">=", "&&", "||", "+=", "|="}


def render(source: str) -> str:
    # Java expands Unicode escapes before recognizing comments.
    if "\\u" in source:
        raise ValueError("FACI raw Java Unicode escapes are unsupported")
    # The envelope and token vocabulary fail closed; javac and cc type-check both forms.
    plain = re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)
    match = re.fullmatch(r"\s*public final class P1MEFaci\s*\{(.*)\}\s*", plain, re.S)
    if match is None:
        raise ValueError("FACI source must contain only the P1MEFaci class")
    body = match[1]
    signatures = re.findall(r"static\s+void\s+\w+\s*\([^)]*\)", body)
    if tuple(" ".join(s.split()) for s in signatures) != SIGNATURES:
        raise ValueError("FACI source has an unsupported method signature")
    cursor = 0
    for signature in signatures:
        start = body.index(signature, cursor)
        if body[cursor:start].strip():
            raise ValueError("FACI fields and additional declarations are unsupported")
        cursor = start + len(signature)
        while body[cursor].isspace():
            cursor += 1
        if body[cursor] != "{":
            raise ValueError("FACI method body is required")
        depth = 1
        cursor += 1
        while cursor < len(body) and depth:
            depth += (body[cursor] == "{") - (body[cursor] == "}")
            cursor += 1
        if depth:
            raise ValueError("unbalanced FACI method body")
    if body[cursor:].strip():
        raise ValueError("FACI trailing declarations are unsupported")
    names = set(re.findall(r"\b(?:long|int|byte)(?:\[\])?\s+(\w+)", body))
    names |= {"blankCheck", "complete"}
    tokens = [m.group() for m in TOKEN.finditer(body) if not m.group().isspace()]
    for index, token in enumerate(tokens):
        if re.fullmatch(r"0[xX][0-9a-fA-F]+|[0-9]+", token):
            if int(token, 16 if token.lower().startswith("0x") else 10) > 0x7fffffff:
                raise ValueError("FACI literals must fit a positive signed int in both languages")
        if token in KEYWORDS | names | OPERATORS or re.fullmatch(r"0[xX][0-9a-fA-F]+|[0-9]+", token):
            pass
        else:
            raise ValueError(f"unsupported FACI token: {token}")
        if index + 1 < len(tokens) and tokens[index + 1] == "(" and token in names:
            if index < 2 or tokens[index - 2:index] != ["static", "void"]:
                raise ValueError("FACI function calls are unsupported")
    # Cells are an input; only the result array may be written. No pointer aliases.
    if re.search(r"cells\s*\[[^;{}]*?\]\s*(?:=|\+=|\|=)", body):
        raise ValueError("FACI physical cells are read-only")
    if re.search(r"\b(?:cells|result)\s*=", body.replace("==", "")):
        raise ValueError("FACI array reassignment is unsupported")
    if re.search(r"(?:byte|long)\[\]\s+(?!cells\b|result\b)\w+", body):
        raise ValueError("FACI array aliases are unsupported")
    statements = body
    for signature in signatures:
        statements = statements.replace(signature, "", 1)
    if re.search(r"\bbyte\b|\b(?:long|int)\s*\[|\b(?:long|int)\s+\w+\s*\[", statements):
        raise ValueError("FACI array declarations and byte locals are unsupported")
    without_index_cast = re.sub(r"\(int\)\s*\(offset\s*/\s*4\)", "", statements)
    if re.search(r"\(\s*(?:int|long)\s*\)", without_index_cast):
        raise ValueError("FACI casts require the bounded physical-cell index")
    c = re.sub(r"\bbyte\[\]\s+(\w+)", r"const uint8_t *\1", body)
    c = re.sub(r"\blong\[\]\s+(\w+)", r"int64_t *\1", c)
    c = re.sub(r"\blong\b", "int64_t", c)
    c = re.sub(r"\bint\b", "int32_t", c)
    c = re.sub(r"\bnull\b", "NULL", c)
    for name in ("blankCheck", "complete"):
        c = re.sub(rf"\b{name}\b", f"p1me_faci_{name}", c)
    digest = hashlib.sha256(source.encode()).hexdigest()
    return (f"/* Generated by tools/emulation/generate_p1me_faci.py; source SHA-256 {digest}. */\n"
            "#ifndef P1ME_FACI_H\n#define P1ME_FACI_H\n#include <stdint.h>\n#include <stddef.h>\n"
            + "\n".join(line.rstrip() for line in c.strip().splitlines()) + "\n#endif\n")


def generate(*, check: bool) -> bool:
    expected = render(SOURCE.read_text(encoding="utf-8"))
    if OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == expected:
        return False
    if check:
        raise RuntimeError("generated FACI behavior is stale; run tools/rh850 model update")
    OUTPUT.write_text(expected, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generate(check=args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
