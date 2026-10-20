"""Pure C source scanning for the Camry host workflow."""
from __future__ import annotations

import re
from typing import Literal, overload


_CALL_WORDS = {
    "if", "for", "while", "switch", "return", "sizeof", "defined", "offsetof",
    "static_assert", "_Generic",
}


def _function_heads(text: str) -> dict[str, str]:
    """Externally linked definitions, including wrapped and pointer declarators."""
    heads: dict[str, str] = {}
    lines = text.splitlines()
    index = 0
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
            # Return types can stand alone; after '(' a continuation is indented.
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
        if match and match.group(1) not in _CALL_WORDS:
            heads[match.group(1)] = head.strip()
    # An earlier static declaration also gives a later definition internal linkage.
    private = set(re.findall(
        r"^static\b[^;{}]*?\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, re.M,
    ))
    return {name: head for name, head in heads.items() if name not in private}


def _c_calls(body: str) -> set[str]:
    return {
        name for name in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\)\s*)?\(", body)
        if name not in _CALL_WORDS
    }


_C_TOKEN = re.compile(
    r"""//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'"""
    r"|\w+|>>=|<<=|\.\.\.|\+\+|--|->|<<|>>|&&|\|\||##|[+\-*/%&|^!<>=]=|[^\s]",
    re.S,
)


def _c_tokens(text: str) -> tuple[str, ...]:
    return tuple(token for token in _C_TOKEN.findall(text)
                 if not token.startswith(("//", "/*")))


def _c_contains(text: str, expected: str) -> bool:
    """Match C tokens without depending on Ghidra's line wrapping."""
    needle = _c_tokens(expected)
    if not needle:
        return True
    tokens = _c_tokens(text)
    width = len(needle)
    return any(tokens[index:index + width] == needle
               for index, token in enumerate(tokens) if token == needle[0])


def _mask_comments(text: str) -> str:
    def spaces(match: re.Match[str]) -> str:
        return re.sub(r"\S", " ", match.group(0))

    text = re.sub(r"/\*.*?\*/", spaces, text, flags=re.S)
    return re.sub(r"//[^\n]*", spaces, text)


def _skip_space(
    code: str, index: int, step: int = 1, *, chars: str | None = " \t\n\r",
) -> int:
    while 0 <= index < len(code) and (
        code[index].isspace() if chars is None else code[index] in chars
    ):
        index += step
    return index


def _skip_quoted(code: str, index: int) -> int:
    """Index just after a character or string literal that starts at `index`."""
    quote = code[index]
    if quote not in "'\"":
        return index
    cursor = index + 1
    while cursor < len(code):
        if code[cursor] == "\\":
            cursor += 2
            continue
        if code[cursor] == quote:
            return cursor + 1
        cursor += 1
    return index


def _quoted_open(code: str, closing: int) -> int | None:
    """Opening quote of the literal whose closing quote is at `closing`."""
    quote = code[closing]
    if quote not in "'\"":
        return None
    index = closing - 1
    while index >= 0:
        if code[index] != quote:
            index -= 1
            continue
        slashes = 0
        cursor = index - 1
        while cursor >= 0 and code[cursor] == "\\":
            slashes += 1
            cursor -= 1
        if slashes % 2 == 0:
            return index
        index -= 1
    return None


def _split_args(arguments: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    index = 0
    while index < len(arguments):
        char = arguments[index]
        if char in "'\"":
            nxt = _skip_quoted(arguments, index)
            index = index + 1 if nxt == index else nxt
            continue
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(arguments[start:index])
            start = index + 1
        index += 1
    parts.append(arguments[start:])
    return parts


def _direct_calls(code: str, skip: set[str]) -> list[tuple[str, int, int]]:
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
        if char in "'\"":
            nxt = _skip_quoted(code, index)
            index = index + 1 if nxt == index else nxt
            continue
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
        nxt = _skip_space(code, nxt)
        if nxt < len(code) and code[nxt] == "(" and name not in skip:
            depth += 1
            stack.append((name, depth, nxt))
            index = nxt + 1
            continue
        index = index + match.end()
    return events


def _indirect_calls(code: str) -> list[tuple[int, int]]:
    """Argument spans of parenthesized function-pointer calls, in call order."""
    events: list[tuple[int, int]] = []
    comments = _comment_spans(code)
    index = 0
    while index < len(code):
        if _span_contains(comments, index):
            index += 1
            continue
        if code[index] in "'\"":
            index = _skip_quoted(code, index)
            continue
        if code[index] != "(":
            index += 1
            continue
        star = _skip_space(code, index + 1)
        if star >= len(code) or code[star] != "*":
            index += 1
            continue
        try:
            close = _match_delimiter(code, index)
            if not code[star + 1:close].strip():
                index = close + 1
                continue
            opening = _skip_space(code, close + 1)
            if opening < len(code) and code[opening] == "(":
                events.append((opening, _match_delimiter(code, opening)))
        except ValueError:
            pass
        index += 1
    return sorted(events, key=lambda event: event[1])


def _comment_spans(code: str) -> list[tuple[int, int]]:
    return [match.span() for match in re.finditer(r"/\*.*?\*/|//.*?$", code, re.S | re.M)]


def _span_contains(spans: list[tuple[int, int]], pos: int) -> bool:
    for start, end in spans:
        if start <= pos < end:
            return True
        if start > pos:
            return False
    return False


@overload
def _match_delimiter(
    code: str, at: int, pair: str = "()", step: int = 1, *,
    quoted: bool = True, required: Literal[True] = True,
) -> int: ...


@overload
def _match_delimiter(
    code: str, at: int, pair: str = "()", step: int = 1, *,
    quoted: bool = True, required: Literal[False],
) -> int | None: ...


def _match_delimiter(
    code: str, at: int, pair: str = "()", step: int = 1, *,
    quoted: bool = True, required: bool = True,
) -> int | None:
    """Match one delimiter kind, retaining source offsets in either direction.

    Masked-source callers can disable literal handling and request ``None`` for
    an incomplete span; expression callers retain the ValueError boundary.
    """
    opener, closer = pair if step > 0 else pair[::-1]
    depth = 0
    index = at
    while 0 <= index < len(code):
        char = code[index]
        if quoted and char in "'\"":
            if step > 0:
                end = _skip_quoted(code, index)
                index = index + 1 if end == index else end
                continue
            opening = _quoted_open(code, index)
            if opening is not None:
                index = opening - 1
                continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return index
        index += step
    if required:
        kind = {"()": "parenthesis", "[]": "bracket", "{}": "brace"}[pair]
        raise ValueError(f"unbalanced {kind}")
    return None


def _assignment_rhs(code: str, eq: int) -> str | None:
    depth = 0
    end = eq
    while end < len(code):
        char = code[end]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == ";" and depth == 0:
            return code[eq:end]
        end += 1
    return None


def _additive_end(code: str, start: int) -> int:
    depth = 0
    brackets = 0
    end = start
    while end < len(code):
        char = code[end]
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
        elif char == "[":
            brackets += 1
        elif char == "]":
            if brackets == 0:
                break
            brackets -= 1
        elif depth == 0 and brackets == 0 and char in ",;<>=!&|^?":
            break
        end += 1
    return end
