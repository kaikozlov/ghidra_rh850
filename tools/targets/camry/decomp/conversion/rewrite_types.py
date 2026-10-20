"""Host-C local storage, structure, and field typing passes."""
from __future__ import annotations

import re

from tools.targets.camry.decomp import abi, c_text, layout, syntax, tree
from tools.targets.camry.decomp.conversion import expressions, rewrite_memory



_INTEGER_PTR_DECL = re.compile(
    r"^([ \t]*)((?:unsigned[ \t]+|signed[ \t]+)?"
    r"(?:undefined[1248]|undefined|byte|uchar|char|code|uint|int|ulong|long|ushort|short))"
    r"[ \t]*\*[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*;[ \t]*$",
    re.M,
)
_OUT_POINTEE = {
    "int": "int",
    "uint": "uint",
    "undefined4": "uint32_t",
    "uint32_t": "uint32_t",
    "int32_t": "int32_t",
    "long": "long",
    "ulong": "ulong",
    "unsigned": "uint",
    "unsigned int": "uint",
}
_HEADER_PARAM_TYPES: dict[str, list[str]] | None = None


def _committed_param_types() -> dict[str, list[str]]:
    """Prototypes already in common.h. Hand declarations in camry.h win."""
    global _HEADER_PARAM_TYPES
    if _HEADER_PARAM_TYPES is None:
        header = tree.COMMON_HEADER
        found: dict[str, list[str]] = {}
        if header.exists():
            flat = re.sub(r"\s+", " ", syntax._strip_comments(header.read_text(encoding="utf-8")))
            for match in re.finditer(
                r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(([^()]*)\)\s*;", flat,
            ):
                found[match.group(1)] = syntax._param_type_list(match.group(2))
        found.update(layout._hand_param_types())
        _HEADER_PARAM_TYPES = found
    return _HEADER_PARAM_TYPES


def _deref_wraps(code: str, index: int) -> bool:
    """True when `*(...)` applies to an expression that contains this index."""
    if re.search(r"\*\(\s*[A-Za-z_][\w \t]*\*+\s*\)\s*$", code[:index]):
        return True
    depth = 0
    cursor = index
    while cursor > 0:
        cursor -= 1
        char = code[cursor]
        if char == ")":
            depth += 1
            continue
        if char == "(":
            if depth:
                depth -= 1
                continue
            star = cursor - 1
            while star >= 0 and code[star] in " \t\n":
                star -= 1
            if star >= 0 and code[star] == "*":
                before = star - 1
                while before >= 0 and code[before] in " \t\n":
                    before -= 1
                if before < 0 or not (code[before].isalnum() or code[before] in "_)\\]"):
                    return True
            continue
        if depth == 0 and char in ";{}":
            return False
    return False


def _call_argument(code: str, start: int, end: int) -> tuple[str, int] | None:
    """Callee and argument index when [start, end) sits inside a call argument."""
    depth = 0
    cursor = start
    arg_index = 0
    while cursor > 0:
        cursor -= 1
        char = code[cursor]
        if char == ")":
            depth += 1
        elif char == "(":
            if depth:
                depth -= 1
                continue
            name_end = cursor
            while name_end > 0 and code[name_end - 1] in " \t\n":
                name_end -= 1
            name_at = name_end
            while name_at > 0 and (code[name_at - 1].isalnum() or code[name_at - 1] == "_"):
                name_at -= 1
            name = code[name_at:name_end]
            if not name:
                continue
            if name in {"if", "while", "for", "switch", "return", "sizeof"}:
                return None
            return name, arg_index
        elif depth == 0 and char == ",":
            arg_index += 1
    return None


def _out_parameter_type(code: str, start: int, end: int) -> str | None:
    """`&name` passed to an `int *` (or other integer pointer) parameter."""
    if start < 1 or code[start - 1] != "&":
        return None
    found = _call_argument(code, start - 1, end)
    if found is None:
        return None
    callee, index = found
    types = _committed_param_types().get(callee)
    if types is None or index >= len(types):
        return None
    text = " ".join(types[index].replace("*", " * ").split())
    if text.count("*") != 1:
        return None
    base = text.replace("*", "").strip()
    return _OUT_POINTEE.get(base)


def _integer_temporary_type(
    code: str, name: str, decl: tuple[int, int], *, uses_from: int = 0,
) -> str | None:
    """A pointer local the bytes only add, compare, or receive as an integer.

    `undefined *puVar5 = (undefined *)(sum)` is the sum, compared with a
    calibration word. An out-parameter written through `int *` is that int.
    A local that is loaded through, subscripted, or holds `&label` stays a pointer.
    """
    out_type: str | None = None
    saw = False
    assigned = False
    signature = syntax._c_signature(code)
    if syntax._returns_pointer(signature) and re.search(rf"\breturn\b[^;]*\b{re.escape(name)}\b", code):
        return None
    pointer_sources = syntax._pointer_names(signature, code) - {name}
    kind = expressions._kind_context(signature, code)
    comments = c_text._comment_spans(code)
    for match in re.finditer(rf"\b{re.escape(name)}\b", code):
        if match.start() < uses_from or c_text._span_contains(comments, match.start()):
            continue
        if decl[0] <= match.start() < decl[1]:
            continue
        saw = True
        start, end = match.start(), match.end()
        prev = start - 1
        while prev >= 0 and code[prev] in " \t\n":
            prev -= 1
        nxt = c_text._skip_space(code, end)
        if prev >= 0 and code[prev] == "&" and (prev == 0 or code[prev - 1] != "&"):
            pointee = _out_parameter_type(code, start, end)
            if pointee is None or (out_type is not None and out_type != pointee):
                return None
            out_type = pointee
            continue
        if nxt < len(code) and (code[nxt] in "[." or code.startswith("->", nxt)):
            return None
        if prev >= 0 and syntax._is_deref_star(code, prev):
            return None
        if nxt < len(code) and code[nxt] == "=" and not code.startswith(("==", "!="), nxt):
            assigned = True
            after = c_text._skip_space(code, nxt + 1)
            if after < len(code) and code[after] == "&":
                return None
            # An explicit integer calculation using a pointer's word is not a
            # pointer copy, even if Ghidra casts the result back to a pointer.
            rhs_end = syntax._rhs_end(code, after)
            rhs = _integer_pointer_value(code[after:rhs_end])
            if any(re.search(rf"\b{re.escape(source)}\b", rhs) for source in pointer_sources):
                if kind(rhs) != "integer":
                    return None
        if _deref_wraps(code, start):
            return None
        found = _call_argument(code, start, end)
        if found is not None:
            if re.search(r"\([A-Za-z_][\w \t]*\*+\s*\)\s*\(*\s*$", code[:start]):
                return None
            callee, index = found
            if callee == "camry_host_addr":
                continue
            # Ghidra's SUBxy reads register bits, not memory through a pointer.
            if index == 0 and re.fullmatch(r"SUB[1-9][1-9]", callee):
                continue
            # `(int)name` inside a call is the integer. The bare name is the pointer.
            cast_at = prev
            if not (cast_at >= 0 and code[cast_at] == ")"):
                arg_text_start = start
                while arg_text_start > 0 and code[arg_text_start - 1] not in "(,":
                    arg_text_start -= 1
                if code[arg_text_start:end].strip() == name:
                    return None
    if not saw or (not assigned and out_type is None):
        return None
    return out_type or "uint32_t"


def _integer_pointer_value(expr: str) -> str:
    """Remove pointer spelling around a register word, including retained C."""
    text = expr.strip()
    while text:
        if syntax._fully_wrapped(text):
            text = text[1:-1].strip()
            continue
        if text.startswith("("):
            close = c_text._match_delimiter(text, 0)
            cast = " ".join(text[1:close].split())
            if cast.endswith("*") and cast[:-1].strip() in syntax._INT_TYPES | {"void"}:
                text = text[close + 1:].strip()
                continue
        call = re.match(r"camry_host_ptr\s*\(", text)
        if call:
            close = c_text._match_delimiter(text, call.end() - 1)
            if close == len(text) - 1:
                text = text[call.end():close].strip()
                continue
        break
    return text


def _strip_assigned_pointer_casts(code: str, names: set[str]) -> str:
    """Recover scalar assignments and address wrappers for proven integers."""
    spans: list[tuple[int, int, str]] = []
    comments = c_text._comment_spans(code)
    for name in names:
        for match in re.finditer(rf"\b{re.escape(name)}\s*=(?!=)", code):
            if c_text._span_contains(comments, match.start()):
                continue
            start = c_text._skip_space(code, match.end())
            end = syntax._rhs_end(code, start)
            rhs = code[start:end].strip()
            value = _integer_pointer_value(rhs)
            if value != rhs:
                spans.append((start, end, f"({value})"))
    code = syntax._apply_spans(code, spans)
    kind = expressions._kind_context(syntax._c_signature(code), code)
    spans = []
    comments = c_text._comment_spans(code)
    for match in re.finditer(r"\bcamry_host_addr\s*\(", code):
        if c_text._span_contains(comments, match.start()):
            continue
        close = c_text._match_delimiter(code, match.end() - 1)
        expr = code[match.end():close].strip()
        value = _integer_pointer_value(expr)
        if value != expr and kind(value) == "integer":
            # A raw pointer cast of an integer is not a mapped host pointer.
            spans.append((match.start(), close + 1, f"((uint32_t)({value}))"))
        elif kind(expr) == "integer":
            spans.append((match.start(), close + 1, f"({expr})"))
    return syntax._apply_spans(code, spans)


def _split_integer_pointer_lifetimes(code: str) -> str:
    """Keep table dereferences, but split a later straight-line numeric lifetime."""
    # Textual suffix renaming is only sound without a back edge into the old
    # pointer lifetime. Conditional uses after the dominating assignment are OK.
    if re.search(r"\b(?:goto|for|while|do)\b", syntax._strip_comments(code)):
        return code
    names: set[str] = set()
    for name in [match.group(3) for match in _INTEGER_PTR_DECL.finditer(code)]:
        decl = next(
            match for match in _INTEGER_PTR_DECL.finditer(code) if match.group(3) == name
        )
        kind = expressions._kind_context(syntax._c_signature(code), code)
        pattern = re.compile(rf"^([ \t]*){re.escape(name)}\s*=(?!=)", re.M)
        comments = c_text._comment_spans(code)
        for match in pattern.finditer(code):
            if c_text._span_contains(comments, match.start()):
                continue
            prefix = syntax._strip_comments(code[:match.start()])
            if prefix.count("{") - prefix.count("}") != 1:
                continue
            if not prefix.rstrip().endswith(("{", "}", ";")):
                continue
            start = c_text._skip_space(code, match.end())
            end = syntax._rhs_end(code, start)
            if end >= len(code) or code[end] != ";":
                continue
            value = _integer_pointer_value(code[start:end])
            if kind(value) != "integer":
                continue
            arithmetic = value
            while arithmetic.startswith("("):
                if syntax._fully_wrapped(arithmetic):
                    arithmetic = arithmetic[1:-1].strip()
                    continue
                close = c_text._match_delimiter(arithmetic, 0)
                if syntax._is_int_type(arithmetic[1:close]):
                    arithmetic = arithmetic[close + 1:].strip()
                    continue
                break
            if not any(op in {"*", "/", "%", "<<", ">>"} for _at, op in syntax._binary_ops(arithmetic)):
                continue
            # This is a split, not blanket pointer demotion: require actual
            # dereferences before the overwrite, and no pointer use afterward.
            if not any(
                _deref_wraps(code, use.start())
                or code[c_text._skip_space(code, use.end()):].startswith(("[", "->"))
                for use in re.finditer(rf"\b{re.escape(name)}\b", code[:match.start()])
                if use.start() >= decl.end()
            ):
                continue
            if _integer_temporary_type(code, name, decl.span(), uses_from=end + 1) is None:
                continue
            scalar = f"{name}_value"
            while re.search(rf"\b{re.escape(scalar)}\b", code):
                scalar += "_value"
            tail = re.sub(rf"\b{re.escape(name)}\b", scalar, code[end + 1:])
            assignment = f"{match.group(1)}{scalar} = {value};"
            code = code[:match.start()] + assignment + tail
            code = code[:decl.end()] + f"\n{decl.group(1)}uint32_t {scalar};" + code[decl.end():]
            names.add(scalar)
            break
    return _strip_assigned_pointer_casts(code, names) if names else code


def _rewrite_integer_temporaries(code: str) -> str:
    """Keep an integer register integer when Ghidra gave it a pointer type."""
    code = _split_integer_pointer_lifetimes(code)
    selected: list[tuple[int, int, str, str]] = []
    for match in _INTEGER_PTR_DECL.finditer(code):
        name = match.group(3)
        replacement = _integer_temporary_type(code, name, match.span())
        if replacement is None:
            continue
        selected.append((match.start(2), match.end(3), name, replacement))
    if not selected:
        return _strip_assigned_pointer_casts(code, set())
    pieces: list[str] = []
    cursor = 0
    names: set[str] = set()
    for start, end, name, replacement in selected:
        pieces.append(code[cursor:start])
        pieces.append(replacement)
        pieces.append(" ")
        pieces.append(name)
        cursor = end
        names.add(name)
    pieces.append(code[cursor:])
    # Removing one pointer declaration can expose a scalar copied from it.
    return _rewrite_integer_temporaries(_strip_assigned_pointer_casts("".join(pieces), names))


def _rewrite_integer_address_derefs(code: str, *, _kind=None) -> str:
    """`*(int *)(gp + disp)` loads the word at that firmware address.

    A cast of the address to a host pointer is not the `ld.w`. A byte store
    through that word is `ld.w` then `st.b` at the loaded address.
    """
    kind = _kind or expressions._kind_context(syntax._c_signature(code), code)
    spans = c_text._comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    # `*(int *)(addr)` and `*((volatile uint32_t *)(addr + offset))`. The
    # second form is a firmware pointer loaded from a table, plus a field.
    pattern = re.compile(
        r"\*\(\s*(\()?\s*(?:volatile\s+)?("
        + "|".join(sorted(syntax._NARROW_DEREF_CTYPE, key=len, reverse=True))
        + r")\s*\*\s*\)\s*\("
    )
    for match in pattern.finditer(code):
        if match.start() < cursor or c_text._span_contains(spans, match.start()):
            continue
        if not syntax._is_deref_star(code, match.start()):
            continue
        try:
            close = c_text._match_delimiter(code, match.end() - 1)
        except ValueError:
            continue
        end = close + 1
        if match.group(1):
            nxt = c_text._skip_space(code, end)
            if nxt >= len(code) or code[nxt] != ")":
                continue
            end = nxt + 1
        expr = code[match.end():close].strip()
        if not expr or kind(expr) != "integer":
            continue
        expr = _rewrite_integer_address_derefs(expr, _kind=kind)
        pieces.append(code[cursor:match.start()])
        pieces.append(syntax._typed_load(expr, syntax._NARROW_DEREF_CTYPE[match.group(2)]))
        cursor = end
    pieces.append(code[cursor:])
    code = "".join(pieces)
    spans = c_text._comment_spans(code)
    pieces = []
    cursor = 0
    stores = re.compile(
        r"\*\*\(\s*(undefined1|uchar|byte|char|undefined)\s*\*\s*\*\s*\)\s*\("
    )
    for match in stores.finditer(code):
        if match.start() < cursor or c_text._span_contains(spans, match.start()):
            continue
        if not syntax._is_deref_star(code, match.start()):
            continue
        try:
            close = c_text._match_delimiter(code, match.end() - 1)
        except ValueError:
            continue
        expr = code[match.end():close].strip()
        if not expr or kind(expr) != "integer":
            continue
        nxt = c_text._skip_space(code, close + 1)
        if nxt >= len(code) or code[nxt] != "=" or (nxt + 1 < len(code) and code[nxt + 1] == "="):
            continue
        expr = _rewrite_integer_address_derefs(expr, _kind=kind)
        word = syntax._typed_load(expr, "uint32_t")
        pieces.append(code[cursor:match.start()])
        pieces.append(f"(*((volatile uint8_t *)camry_host_ptr((uint32_t)({word}))))")
        cursor = close + 1
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_loaded_pointer_words(code: str) -> str:
    """`(uint *)*slot` uses the integer word at `slot` as a firmware address.

    The slot is a pointer to that word. The word is not itself a host pointer.
    """
    kind = expressions._kind_context(syntax._c_signature(code), code)
    spans = c_text._comment_spans(code)
    pattern = re.compile(
        r"\(\s*((?:volatile\s+)?[A-Za-z_][A-Za-z0-9_]*(?:\s+[A-Za-z_][A-Za-z0-9_]*)*)\s*\*\s*\)\s*\*"
    )
    pieces: list[str] = []
    cursor = 0
    for match in pattern.finditer(code):
        if match.start() < cursor or c_text._span_contains(spans, match.start()):
            continue
        operand = syntax._deref_operand(code, match.end())
        if operand is None:
            continue
        text, end = operand
        if kind(f"*{text}") != "integer":
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(
            f"(({match.group(1).strip()} *)camry_host_ptr((uint32_t)(*{text})))"
        )
        cursor = end
    pieces.append(code[cursor:])
    return "".join(pieces)


def _retype_struct_address_words(code: str) -> str:
    """`(Struct *)uint32_table[index]` is the address word, and `+ 1` is one struct.

    The table element is the firmware address. The next curve is that word plus
    the struct size. Both stay 4-byte words: the callee reads them through
    stack slots, and the later stores are `st.w` of those words.
    """
    rows = layout._struct_rows()
    arrays = expressions._uint32_array_names()
    declarations = list(re.finditer(
        r"^([ \t]*)([A-Za-z_][A-Za-z0-9_]*)[ \t]*\*[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*;[ \t]*$",
        code,
        re.M,
    ))
    candidates: dict[str, tuple[re.Match[str], str, int]] = {}
    for match in declarations:
        struct = match.group(2)
        name = match.group(3)
        row = rows.get(struct)
        if row is None:
            continue
        size = int(row.get("size") or 0)
        if size <= 0:
            continue
        if re.search(rf"\b{re.escape(name)}\s*(?:->|\[|\()", code):
            continue
        candidates[name] = (match, struct, size)
    if not candidates:
        return code
    chosen: dict[str, tuple[str, int]] = {}
    pending = set(candidates)
    progress = True
    while progress:
        progress = False
        for name in list(pending):
            _match, struct, size = candidates[name]
            assigns = list(re.finditer(
                rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*=\s*([^;]*);",
                code,
            ))
            if len(assigns) != 1:
                continue
            rhs = " ".join(assigns[0].group(1).split())
            table = re.fullmatch(
                r"\(\(([A-Za-z_][A-Za-z0-9_]*) \*\)camry_host_ptr\(\(uint32_t\)\(([A-Za-z_][A-Za-z0-9_]*)\[(.*)\]\)\)\)",
                rhs,
            )
            if (
                table
                and table.group(1) == struct
                and table.group(2) in arrays
            ):
                chosen[name] = (f"{table.group(2)}[{table.group(3)}]", size)
                pending.remove(name)
                progress = True
                continue
            added = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*) \+ (\d+)", rhs)
            if added and added.group(1) in chosen and int(added.group(2)) < 8:
                base = added.group(1)
                count = int(added.group(2))
                chosen[name] = (f"{base} + {count * chosen[base][1]}u", size)
                pending.remove(name)
                progress = True
    if not chosen:
        return code
    for name, (rhs, _size) in chosen.items():
        code = re.sub(
            rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*=\s*[^;]*;",
            f"{name} = {rhs};",
            code,
            count=1,
        )
    for match in reversed(declarations):
        name = match.group(3)
        if name not in chosen:
            continue
        code = (
            code[:match.start()]
            + f"{match.group(1)}uint32_t {name};"
            + code[match.end():]
        )
    for name, (_rhs, _size) in chosen.items():
        struct = candidates[name][1]
        code = re.sub(
            rf"\*\(\s*{re.escape(struct)}\s*\*\*\s*\)\s*\(([^()]*)\)\s*=\s*{re.escape(name)}\s*;",
            lambda item, name=name: (
                "(*((volatile uint32_t *)camry_host_ptr((uint32_t)("
                f"{item.group(1)})))) = {name};"
            ),
            code,
        )
        code = re.sub(
            rf"\bcamry_host_addr\(\s*{re.escape(name)}\s*\)", name, code,
        )
    return code


def _rewrite_packed_stack(code: str) -> str:
    """Locals the bytes address as one record are one array, not separate slots.

    Ghidra names each stack byte. -O2 then stores them apart, so a pointer to
    the first slot does not cover the rest.
    """
    if syntax._signature_name(syntax._c_signature(code)) == "run_three_icus_sequence_steps_returns_failure_883e8":
        # 883EE..883FC builds four firmware words, and 88400/88412/88426
        # pass the word at SP+8. Separate host pointer locals lose both the
        # adjacent ROM descriptor at SP+4 and the four-byte frame pointer.
        return (
            "bool run_three_icus_sequence_steps_returns_failure_883e8(void)\n{\n"
            "  uint32_t record[4];\n"
            "  int result;\n"
            "  record[0] = 0;\n"
            "  record[1] = camry_tp + 0x3f70u;\n"
            "  record[2] = camry_host_addr(record);\n"
            "  record[3] = 0;\n"
            "  result = submit_icus_sequence_step_and_poll_up_to_2500_883cc(camry_host_addr(record + 2));\n"
            "  if (result != 1) return true;\n"
            "  record[0] = 1;\n"
            "  record[2] = camry_host_addr(record);\n"
            "  result = submit_icus_sequence_step_and_poll_up_to_2500_883cc(camry_host_addr(record + 2));\n"
            "  if (result != 1) return true;\n"
            "  record[0] = 2;\n"
            "  record[2] = camry_host_addr(record);\n"
            "  result = submit_icus_sequence_step_and_poll_up_to_2500_883cc(camry_host_addr(record + 2));\n"
            "  return result != 1;\n}\n"
        )
    if syntax._signature_name(syntax._c_signature(code)) in {
        "cantp_copy_upper_transmit_bytes", "cantp_copy_upper_receive_bytes",
        "cantp_start_upper_receive",
    }:
        # Each adapter stores a four-byte firmware data address followed by
        # its ushort length. Host pointer locals cannot represent that PDU
        # or live outside the packed record containing the available output.
        source = "first_chunk" if "first_chunk->data" in code else "chunk"
        code = re.sub(r"\buchar\s*\*\s*puStack_10\s*;", "uint32_t puStack_10;", code)
        code = re.sub(
            rf"\bpuStack_10\s*=\s*(?:{source}->data|"
            rf"\(\(void\s*\*\)\s*camry_host_ptr\(\(uint32_t\)\({source}->data\)\)\))\s*;",
            f"puStack_10 = {source}->data;", code,
        )
        if re.search(r"\buint8_t\s+stack_record_12\s*\[", code):
            # Retained C already packed the adjacent ushort locals.
            code = re.sub(r"^[ \t]*uint32_t\s+puStack_10\s*;\s*\n", "", code, flags=re.M)
            code = re.sub(
                r"(?<!&)&(?!&)\s*puStack_10\b",
                "((uint32_t *)(stack_record_12 + 2))", code,
            )
            code = re.sub(
                r"\bpuStack_10\b", "(*((uint32_t *)(stack_record_12 + 2)))", code,
            )
    if (
        syntax._signature_name(syntax._c_signature(code)) == "copy_payload_and_append_queue_slot_8e9c6"
        and re.search(r"\buint8_t\s+stack_record_34\s*\[", code)
    ):
        # Retained output packed the scalar slots but left SP+12's array
        # separate. 8E862 writes its four-word descriptor through that array,
        # including iStack_20/uStack_1c, which the copy reads from the record.
        code = re.sub(r"^[ \t]*int\s+aiStack_28\s*\[\s*2\s*\]\s*;\s*\n", "", code, flags=re.M)
        code = re.sub(r"^[ \t]*camry_fill_bytes\(aiStack_28,\s*sizeof aiStack_28\);\s*\n", "", code, flags=re.M)
        code = re.sub(r"\baiStack_28\b", "((int *)(stack_record_34 + 12))", code)
    code = re.sub(
        r"\b(uint8_t stack_record_([0-9a-fA-F]+)\[)(\d+)(\];)",
        lambda match: match[1] + str(max(int(match[2], 16), int(match[3]))) + match[4],
        code,
    )
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    body = code[brace + 1:]
    decls: list[tuple[int, int, str, int, int, int, str]] = []
    arrays: set[str] = set()
    for match in re.finditer(
        r"^([ \t]*)([A-Za-z_][A-Za-z0-9_ \t]*?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(\[[^\]]*\])?\s*;[ \t]*$",
        body,
        flags=re.M,
    ):
        name = match.group(3)
        offset_match = layout._STACK_LOCAL.fullmatch(name)
        if offset_match is None:
            continue
        token = match.group(2).split()[-1]
        width = layout._STACK_WIDTH.get(token)
        if width is None:
            continue
        count = 1
        if match.group(4):
            arrays.add(name)
            for number in re.findall(r"\d+", match.group(4)):
                count *= int(number)
        offset = int(offset_match.group(1), 16)
        decls.append((match.start(), match.end(), name, offset, width, count, token))
    if len(decls) < 2:
        return code
    # Indexed arrays address the frame too: Ghidra can split their trailing
    # elements into scalar locals. Look past the declaration so an unused
    # array alone does not select a packed region.
    addressed = [
        row for row in decls
        if re.search(rf"(?<!&)&(?!&)\s*{re.escape(row[2])}\b", body)
        or (
            row[2] in arrays
            and re.search(rf"\b{re.escape(row[2])}\b", body[row[1]:])
        )
    ]
    if not addressed:
        return code
    base = max(row[3] for row in addressed)
    floor = min(row[3] for row in decls)
    if base - floor > 256:
        floor = base - 256
    members = [row for row in decls if floor <= row[3] <= base]
    # An array can start before an addressed scalar and overlap it. Include
    # every such alias before choosing the byte region's origin and extent.
    while members:
        start = -max(row[3] for row in members)
        end = max(-row[3] + row[4] * row[5] for row in members)
        overlapping = [
            row for row in decls
            if -row[3] < end and -row[3] + row[4] * row[5] > start
        ]
        if overlapping == members:
            break
        members = overlapping
    if len(members) < 2:
        return code
    base = max(row[3] for row in members)
    size = max(base - row[3] + row[4] * row[5] for row in members)
    # An escaping local can start a copy whose unused trailing slots Ghidra
    # omitted. Preserve the remaining negative frame offsets as storage too.
    size = max(size, base)
    size = (size + 3) & ~3
    if size <= 0 or size > 256:
        return code
    record = f"stack_record_{base:x}"
    index_of = {row[2]: base - row[3] for row in members}
    width_of = {row[2]: row[4] for row in members}
    ctype = {row[2]: layout._STACK_CTYPE.get(row[6], row[6]) for row in members}
    # Remove only the declarations we parsed, never a statement such as
    # `return iStack_8;` that also happens to be two identifiers and a semicolon.
    declaration_lines = {body[start:end] for start, end, *_rest in members}
    text = "\n".join(line for line in body.split("\n") if line not in declaration_lines)
    for name, index in sorted(index_of.items(), key=lambda item: -len(item[0])):
        width = width_of[name]
        is_array = name in arrays
        cast = ctype[name]
        if width == 1 and index + 4 <= size:
            text = re.sub(
                rf"\b_{re.escape(name)}\b",
                f"(*((uint32_t *)({record} + {index})))",
                text,
            )

        def use(
            match: re.Match[str],
            index: int = index,
            width: int = width,
            is_array: bool = is_array,
            cast: str = cast,
        ) -> str:
            slot = record if index == 0 else f"({record} + {index})"
            if is_array:
                return f"(({cast} *)({slot}))"
            if match.group(0).startswith("&"):
                # The byte record replaces storage, not the local's pointee
                # type: (&uStack_24)[i] must still load and stride in halfwords.
                return f"(({cast} *)({slot}))"
            if width == 1:
                return f"{record}[{index}]"
            if width == 3:
                return (
                    f"((uint32_t){record}[{index}]"
                    f" | ((uint32_t){record}[{index + 1}] << 8)"
                    f" | ((uint32_t){record}[{index + 2}] << 16))"
                )
            return f"(*(({cast} *)({record} + {index})))"

        text = re.sub(rf"(?<![\w])(?:(?<!&)&(?!&)\s*)?{re.escape(name)}\b", use, text)
    text = f"\n  uint8_t {record}[{size}];" + text
    return code[:brace + 1] + text


def _pointer_macro_bases() -> dict[str, tuple[str, str]]:
    """Pointer macros as (element type, firmware address). Value macros are omitted."""
    cached = getattr(_pointer_macro_bases, "cached", None)
    if cached is not None:
        return cached
    cached = {
        name: (ctype, f"0x{address:x}u")
        for name, (address, ctype, array) in layout._data_layouts().items()
        if array and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ctype)
    }
    _pointer_macro_bases.cached = cached
    return cached


def _rewrite_pointer_macro_indexes(code: str) -> str:
    """Named pointer indexing and addition must use the firmware base.

    The macro is already a host pointer. A large slot walks off that mapping.
    Spell the cast so the firmware-address indexer can scale it.
    """
    bases = _pointer_macro_bases()
    if not bases or not any(name in code for name in bases):
        return code
    names = sorted(bases, key=len, reverse=True)
    alternatives = "|".join(re.escape(name) for name in names)
    comments = c_text._comment_spans(code)
    code = re.sub(
        r"\b(" + alternatives + r")\b(?=\s*\+(?![+=]))",
        lambda match: (
            f"((volatile {bases[match.group(1)][0]} *)camry_host_ptr({bases[match.group(1)][1]}))"
            if not c_text._span_contains(comments, match.start()) else match.group(0)
        ),
        code,
    )
    pattern = re.compile(r"\b(" + alternatives + r")\s*\[")
    for _ in range(256):
        comments = c_text._comment_spans(code)
        chosen: tuple[int, int, str, str] | None = None
        for match in pattern.finditer(code):
            if c_text._span_contains(comments, match.start()):
                continue
            try:
                end = c_text._match_delimiter(code, match.end() - 1, "[]", quoted=False)
            except ValueError:
                continue
            if chosen is None or match.start() > chosen[0]:
                chosen = (match.start(), end, match.group(1), code[match.end():end])
        if chosen is None:
            break
        start, end, name, index = chosen
        ctype, address = bases[name]
        replacement = f"((volatile {ctype} *)camry_host_ptr({address}))[{index}]"
        code = code[:start] + replacement + code[end + 1:]
    return code


_HOST_INDEX = re.compile(
    r"\(\(\s*(volatile\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*\)\s*camry_host_ptr\("
)


def _host_index_span(code: str, match: re.Match[str]) -> tuple[int, int, str] | None:
    """Closing paren of camry_host_ptr, end of the subscript, and its index."""
    try:
        arg_close = c_text._match_delimiter(code, match.end() - 1)
    except ValueError:
        return None
    nxt = arg_close + 1
    if nxt >= len(code) or code[nxt] != ")":
        return None
    nxt += 1
    while nxt < len(code) and code[nxt] in " \t\n":
        nxt += 1
    if nxt >= len(code) or code[nxt] != "[":
        return None
    try:
        end = c_text._match_delimiter(code, nxt, "[]", quoted=False)
    except ValueError:
        return None
    index = code[nxt + 1:end].strip()
    if index == "0":
        member = re.match(r"\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)", code[end + 1:])
        field = (
            rewrite_memory._find_field(layout._struct_rows().get(match.group(2)), member.group(1))
            if member is not None else None
        )
        if field is None:
            return None
        field_type, array = layout._field_c(field["type"], field["size"], set(layout._struct_rows()))
        if array or field_type not in layout._SCALAR_STRIDE:
            return None
    return arg_close, end, index


def _rewrite_scalar_host_indexes(code: str) -> str:
    """Index a firmware address, not the host pointer of its base.

    `((volatile uint16_t *)camry_host_ptr(base))[index]` adds `index` in the
    host mapping. A large or negative index leaves that mapping. The bytes add
    it to the firmware address and map the sum. A struct subscript uses the
    record size the cast already used.
    """
    for _ in range(64):
        chosen: tuple[re.Match[str], int, int, str] | None = None
        for match in _HOST_INDEX.finditer(code):
            span = _host_index_span(code, match)
            if span is None:
                continue
            if chosen is None or match.start() > chosen[0].start():
                chosen = (match, *span)
        if chosen is None:
            break
        match, arg_close, end, index = chosen
        ctype = match.group(2)
        base = code[match.end():arg_close].strip()
        if ctype in layout._SCALAR_STRIDE:
            stride = f"{layout._SCALAR_STRIDE[ctype]}u"
            replacement = (
                f"(*((volatile {ctype} *)camry_host_ptr((uint32_t)({base} + "
                f"(uint32_t)({index}) * {stride}))))"
            )
        else:
            member = re.match(r"\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)", code[end + 1:])
            field = (
                rewrite_memory._find_field(layout._struct_rows().get(ctype), member.group(1))
                if member is not None else None
            )
            if field is not None:
                field_type, array = layout._field_c(field["type"], field["size"], set(layout._struct_rows()))
                if not array and field_type in layout._SCALAR_STRIDE:
                    replacement = (
                        f"(*((volatile {field_type} *)camry_host_ptr((uint32_t)({base} + "
                        f"(uint32_t)({index}) * (uint32_t)sizeof({ctype}) + "
                        f"(uint32_t)offsetof({ctype}, {member.group(1)})))))"
                    )
                    code = code[:match.start()] + replacement + code[end + 1 + member.end():]
                    continue
            volatile = match.group(1) or ""
            replacement = (
                f"(({volatile}{ctype} *)camry_host_ptr((uint32_t)({base} + "
                f"(uint32_t)({index}) * (uint32_t)sizeof({ctype}))))[0]"
            )
        code = code[:match.start()] + replacement + code[end + 1:]
    return code


def _rewrite_host_pointer_adds(code: str) -> str:
    """`((scalar *)camry_host_ptr(base)) + index` adds in the host mapping.

    The bytes add the scaled index to the firmware address. A large index
    leaves the host page and faults. The sum is mapped instead.
    """
    pattern = re.compile(
        r"\(\(\s*(volatile\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\*\s*\)\s*camry_host_ptr\("
    )
    pieces: list[str] = []
    cursor = 0
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        prev = match.start() - 1
        while prev >= 0 and code[prev] in " \t\n":
            prev -= 1
        if prev >= 0 and code[prev] == "*":
            continue
        try:
            arg_close = c_text._match_delimiter(code, match.end() - 1)
        except ValueError:
            continue
        if arg_close + 1 >= len(code) or code[arg_close + 1] != ")":
            continue
        nxt = arg_close + 2
        while nxt < len(code) and code[nxt] in " \t\n":
            nxt += 1
        if (
            nxt >= len(code)
            or code[nxt] not in "+-"
            or code.startswith(("++", "--", "+=", "-=", "->"), nxt)
        ):
            continue
        end = c_text._additive_end(code, nxt)
        index = code[nxt:end].strip()
        if index.startswith("+"):
            index = index[1:].strip()
        if not index:
            continue
        arg = code[match.end():arg_close].strip()
        ctype = match.group(2)
        volatile = match.group(1) or ""
        if ctype in layout._SCALAR_STRIDE:
            stride = f"{layout._SCALAR_STRIDE[ctype]}u"
        else:
            stride = f"(uint32_t)sizeof({ctype})"
        pieces.append(code[cursor:match.start()])
        pieces.append(
            f"(({volatile}{ctype} *)camry_host_ptr((uint32_t)({arg} + "
            f"(uint32_t)({index}) * {stride})))"
        )
        cursor = end
    pieces.append(code[cursor:])
    return "".join(pieces)


_MULHI_SCALE = re.compile(
    r"\(uint32_t\)\(([A-Za-z_][A-Za-z0-9_]*)\)\s*\*\s*"
    r"(?:\(uint32_t\)\s*)?"
    r"(?:sizeof\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)"
    r"|(-?(?:0x[0-9A-Fa-f]+|\d+)[uU]?))"
)


def _symbols_by_name() -> dict[str, list[dict]]:
    cached = getattr(_symbols_by_name, "cached", None)
    if cached is None:
        cached = {}
        for row in tree.load_symbols():
            cached.setdefault(row["name"], []).append(row)
        _symbols_by_name.cached = cached
    return cached


def _gpr_writes(name: str, args: list[int]) -> set[int]:
    from tools.targets.camry.decomp.lifting.graph import _GAP_WRITES

    known = _GAP_WRITES.get(name)
    if known is not None:
        return {args[index] for index in known if index < len(args) and args[index]}
    op = name.removeprefix("camry_")
    if op.startswith("st") or op in abi._NO_GPR_WRITE:
        return set()
    if args and args[0]:
        return {args[0]}
    return set()


def _entry_mulhi_immediates(row: dict) -> dict[int, set[int]]:
    """mulhi/mulhi5 of r6-r9 while those registers are still the incoming arguments."""
    from tools.targets.camry.decomp.lifting.graph import _stmt_call
    from tools.targets.camry.decomp.lifting.decode import decode_at

    image = abi._codeflash_image()
    entry = int(row["addr"], 16)
    live = {6, 7, 8, 9}
    found: dict[int, set[int]] = {reg: set() for reg in live}
    for start, end in row["ranges"]:
        if not start <= entry <= end:
            continue
        pc = entry
        while pc <= end and live:
            inst = decode_at(image, pc)
            if inst is None or pc + inst.size - 1 > end:
                break
            if inst.kind in {"jarl", "jarl_ind", "callt"}:
                break
            parsed = _stmt_call(inst.stmt) if inst.stmt else None
            if parsed is not None and parsed[0] in {"camry_mulhi", "camry_mulhi5"}:
                op, args = parsed
                if op == "camry_mulhi" and len(args) == 3:
                    dst, src, imm = args
                    if src in live:
                        found[src].add(imm)
                    live.discard(dst)
                elif op == "camry_mulhi5" and len(args) == 2 and args[0] in live:
                    found[args[0]].add(args[1])
                    live.discard(args[0])
            elif parsed is not None:
                live -= _gpr_writes(parsed[0], parsed[1])
            pc += inst.size
        break
    return {reg: imms for reg, imms in found.items() if imms}


def _integer_argument_registers(signature: str) -> dict[int, str]:
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening:
        return {}
    found: dict[int, str] = {}
    register = 6
    for part in c_text._split_args(signature[opening + 1:closing]):
        if register > 9:
            break
        text = " ".join(part.split()).strip()
        if not text or text == "void":
            continue
        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", text)
        if match and "*" not in text and "[" not in text:
            found[register] = match.group(1)
        register += 1
    return found


def _agreed_mulhi_scales(name: str, signature: str) -> dict[str, set[int]]:
    rows = _symbols_by_name().get(name) or []
    per_row = [_entry_mulhi_immediates(row) for row in rows]
    per_row = [item for item in per_row if item]
    if not per_row:
        return {}
    registers = set(per_row[0])
    for item in per_row[1:]:
        registers &= set(item)
    names = _integer_argument_registers(signature)
    agreed: dict[str, set[int]] = {}
    for register in registers:
        param = names.get(register)
        if param is None:
            continue
        common = set.intersection(*(item[register] for item in per_row))
        if common:
            agreed[param] = common
    return agreed


def _rewrite_mulhi_scales(code: str) -> str:
    """Scale an incoming argument the way mulhi does.

    mulhi sign-extends the low 16 bits. `(uint32_t)(param)` zero-extends a
    ushort, so a filled slot such as 0xa5a5 indexes the wrong record. The
    parameter stays the width the caller passed; only the multiply changes.
    """
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    signature = syntax._c_signature(code)
    opening = signature.find("(")
    if opening < 0:
        return code
    name = signature[:opening].split()[-1].lstrip("*")
    scales = _agreed_mulhi_scales(name, signature)
    if not scales:
        return code
    layouts = layout._struct_rows()

    def replace(match: re.Match[str]) -> str:
        param = match.group(1)
        immediates = scales.get(param)
        if not immediates:
            return match.group(0)
        if match.group(2):
            width = layouts.get(match.group(2), {}).get("size")
        else:
            width = int(match.group(3).rstrip("uU"), 0)
        if width not in immediates:
            return match.group(0)
        scale = match.group(0).split("*", 1)[1]
        return f"(int32_t)(int16_t){param} *{scale}"

    return _MULHI_SCALE.sub(replace, code)


def _host_ptr_assignment(code: str, name: str) -> tuple[int, int, str] | None:
    """`name = ((type *)camry_host_ptr(expr))`, or None when the statement is not that."""
    match = re.match(
        rf"{re.escape(name)}\s*=\s*\(\(\s*(?:volatile\s+)?"
        rf"[A-Za-z_][A-Za-z0-9_]*\s*\*\)\s*camry_host_ptr\(",
        code,
    )
    if match is None:
        return None
    try:
        close = c_text._match_delimiter(code, match.end() - 1)
    except ValueError:
        return None
    end = close + 1
    while end < len(code) and code[end] == ")":
        end += 1
    if end >= len(code) or code[end] != ";":
        return None
    expr = code[match.end():close].strip()
    if not expr:
        return None
    return match.start(), end + 1, expr


def _rewrite_address_roundtrip(code: str) -> str:
    """A pointer created only so camry_host_addr can recover it is the integer.

    The bytes return 0xffff0000. camry_host_ptr faults because that constant is
    not a mapped scenario address.
    """
    names = re.findall(r"camry_host_addr\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)", code)
    for name in dict.fromkeys(names):
        uses = list(re.finditer(rf"\b{re.escape(name)}\b", code))
        if len(uses) < 2:
            continue
        declaration = re.search(
            rf"^[ \t]*(?:undefined|undefined1|byte|uchar|char|code|void)\s*\*\s*{re.escape(name)}\s*;",
            code, re.M,
        )
        if declaration is None:
            continue
        assignments: list[tuple[int, int, str]] = []
        ok = True
        for use in uses:
            if declaration.start() <= use.start() < declaration.end():
                continue
            if code.startswith("camry_host_addr(", max(0, use.start() - len("camry_host_addr("))):
                continue
            parsed = _host_ptr_assignment(code[use.start():], name)
            if parsed is None:
                ok = False
                break
            start, end, expr = parsed
            assignments.append((use.start() + start, use.start() + end, expr))
        if not ok or not assignments:
            continue
        for start, end, expr in reversed(assignments):
            code = code[:start] + f"{name} = (uint32_t)({expr});" + code[end:]
        code = re.sub(
            rf"camry_host_addr\(\s*{re.escape(name)}\s*\)",
            name,
            code,
        )
        code = re.sub(
            rf"\b(?:undefined|undefined1|byte|uchar|char|code|void)\s*\*\s*{re.escape(name)}\b",
            f"uint32_t {name}",
            code,
            count=1,
        )
    return code


def _rewrite_narrow_storage(code: str) -> str:
    """Represent a 24-bit value without widening a three-byte memory access."""
    pointer_names = re.findall(r"\b(?:uint3|undefined3)\s*\*\s*(\w+)\s*;", code)
    for name in pointer_names:
        code = re.sub(
            rf"\b(?:uint3|undefined3)\s*\*\s*{re.escape(name)}\b",
            f"uint8_t *{name}", code,
        )
        code = re.sub(r"\((?:uint3|undefined3)\s*\*\)", "(uint8_t *)", code)
        code = re.sub(
            rf"\((?:byte|uchar|uint8_t)\)\s*\*\s*{re.escape(name)}\b",
            f"{name}[0]", code,
        )
        code = re.sub(
            rf"(^[ \t]*uint8_t \*{re.escape(name)}\s*;)|(?<![\w])\*\s*{re.escape(name)}\b",
            lambda match: match.group(0) if match.group(1) else (
                f"((uint32_t){name}[0] | ((uint32_t){name}[1] << 8) | ((uint32_t){name}[2] << 16))"
            ),
            code, flags=re.M,
        )
    pieces: list[str] = []
    cursor = 0
    for match in re.finditer(r"\((?:uint3|undefined3)\)\s*", code):
        end = syntax._unary_operand_end(code, match.end())
        if end is None:
            continue
        pieces.append(code[cursor:match.start()])
        pieces.append(f"((uint32_t)({code[match.end():end]}) & 0xffffffu)")
        cursor = end
    pieces.append(code[cursor:])
    return re.sub(r"\b(?:uint3|undefined3)(?=\s+\w+\s*;)", "uint32_t", "".join(pieces))


def _rewrite_numeric_record_types(code: str) -> str:
    """Undo type propagation into registers used as numeric words in the bytes."""
    name = syntax._signature_name(syntax._c_signature(code))
    if name == "restore_dual_capture_records_and_select_newer_generation_54ce2":
        before, call, after = code.partition("  uVar5 = nvm_get_record(0x13,&local_c8);\n")
        if call:
            code = (
                before.replace("  ushort uStack_82;", "  ushort uStack_82;\n  ushort record_counter;")
                + call + "  record_counter = uStack_82;\n"
                + re.sub(r"\buStack_82\b", "record_counter", after)
            )
    if name == "nvm_route_application_result":
        # 68eba is ld.hu from 2b010 + logical_handle*2, not a struct value.
        code = code.replace("F33NvmApplicationRoute FVar1;", "ushort FVar1;")
        code = code.replace(
            "FVar1 = nvm_logical_application_routes[logical_handle];",
            f"FVar1 = {syntax._typed_load('0x2b010u + (uint32_t)logical_handle * 2u', 'uint16_t')};",
        )
    elif name == "prepare_tag_verification_request_and_bit_lengths_88fc0":
        # 89002 forms gp+23224 = FEBF12B8, a memcpy destination, not code.
        code = code.replace(
            "memcpy_forward(boot_relocated_8628,",
            "memcpy_forward(&DAT_febf12b8,",
        )
    if name == "boot_clear_flash_block_skip_flags":
        # 3520 shifts the interval index by 2; 3528/352e load numeric bounds.
        code = code.replace("F33BootInterruptCallback *", "uint ")
    elif name == "boot_security_generate_challenge":
        # 6f82 loads a pointer word; 6f8a/6f8c compare bytes, never callbacks.
        code = code.replace("F33BootInterruptCallback", "uchar")
        code = code.replace(
            "pFVar11 = (&pFVar4->handler)[iVar5];",
            "pFVar11 = (uchar *)camry_host_ptr(((uint32_t *)pFVar4)[iVar5]);",
        )
        code = code.replace("*(byte *)(&pFVar4->handler + 3)", "*((byte *)pFVar4 + 12)")
    elif name == "compute_q15_sine_cosine_turn_angle_70e32":
        # 70e58/70e74/70e8c are subtraction, not MonitorCurrentRecord loads.
        for old, new in (
            ("pFVar6[-0x19a].bank1_bias", "(pFVar6 - 0x4000)"),
            ("pFVar6[-0x4cd].bank1_negative_gain + 2", "(pFVar6 - 0xc000)"),
            ("pFVar6[-0x334].bank0_nonnegative_gain + 2", "(pFVar6 - 0x8000)"),
            ("&monitor_current_rom_record", "0xa000u"),
            ("(F33MonitorCurrentRecord *)&UNK_0000bfff", "0xbfffu"),
            ("(F33MonitorCurrentRecord *)&UNK_0000dfff", "0xdfffu"),
            ("(F33MonitorCurrentRecord *)&UNK_00009fff", "0x9fffu"),
        ):
            code = code.replace(old, new)
        code = code.replace("F33MonitorCurrentRecord *", "uint ")
    elif name == "select_calibration_table_pointer_pair_c28fc":
        # MOV constants at c2980/c298e/c299c/c29a4 were printed as "".
        for address in (0xd2e44, 0xd2e88, 0xd2ecc, 0xd2e00):
            code = code.replace('puVar3 = "";', f"puVar3 = (uchar *)0x{address:x};", 1)
    elif name == "translate_memory_cursor_between_image_and_snapshot_991d2":
        # 99206 subtracts 10000 from FEBF7C00, then 99208 adds r10.
        code = code.replace("&shared_snapshot_monitor_0.packed_status", "0xfebe7c00u")
    elif name in {"dispatch_pending_type0_tx_buffer_events_3ef2", "dispatch_pending_type3_fifo_frames_4048"}:
        # 3f00..3f06 / 4056..405c extract bits 4..6 of (param_1 & 7)<<4.
        callee = "read_combined_channel_tx_pending_bits_3e1c" if name == "dispatch_pending_type0_tx_buffer_events_3ef2" else "read_channel_three_fifo_status_bits_3f4a"
        code = code.replace(callee + "()", callee + "(param_1 & 7)")
    elif name == "restore_valid_five_entry_bank_and_cursor_from_nvm_54c0a":
        # 54c54..54c58 leave r7 = entry SP record + record_index*32.
        code = re.sub(
            r"__v850_copy_words_8\(([^;]+)\);",
            r"__v850_copy_words_8(\1, (uint8_t *)&local_bc + uVar3 * 32);",
            code,
        )
    elif name == "validate_routine_buffers_build_header_and_execute_97912":
        # 9793e loads r8; 97942 copies the record index into r7.
        code = code.replace("reject_routine_response_capacity_shortage_973dc()", "reject_routine_response_capacity_shortage_973dc(param_1,uVar5,puVar1[-0x59ea])")
    elif name == "validate_cursor_crc_request_and_build_reply_99266":
        # 992c8 loads r7 and 992ce copies uVar4 into r6. 9907a writes neither.
        code = code.replace("compute_inverted_dcra1_crc_and_advance_cursor_99226()", "compute_inverted_dcra1_crc_and_advance_cursor_99226(uVar4,local_20)")
    elif name == "read_memory_cursor_bytes_and_build_reply_99152":
        # 9907a preserves r6/r7; 99198 points r8 at entry-SP-0x1b.
        code = code.replace("copy_u8_length_bytes_and_advance_memory_cursor_99126()", "copy_u8_length_bytes_and_advance_memory_cursor_99126(uVar4,bVar3,local_1c + 1)")
    elif name == "initialize_configured_channels_buffers_and_filter_routes_3b3c":
        # 3bc8 clears r7; 3bd2..3bf4 count type-3 records for this channel.
        code = code.replace("  uint uVar14;", "  uint uVar14;\n  uint camry_type3_count;")
        code = code.replace(
            "      iVar11 = 0;\n      do {\n        iVar3 = iVar11 + 1;",
            "      iVar11 = 0;\n      camry_type3_count = 0;\n      do {\n"
            "        if (*(byte *)(((iVar7 << 4) | (iVar11 & 15)) * 12 +\n"
            "            *(int *)((int)((ulonglong)uVar6 >> 32) + 0x2d4)) >> 5 == 3) {\n"
            "          camry_type3_count = (camry_type3_count + 1) & 0xff;\n"
            "        }\n        iVar3 = iVar11 + 1;",
        )
        code = code.replace("store_reverse_indexed_rule_count_byte_3998()", "store_reverse_indexed_rule_count_byte_3998(iVar7,camry_type3_count)")
        code = code.replace("update_filter_selector_low_bits_39c0()", "update_filter_selector_low_bits_39c0(uVar9 >> 4)")
        code = code.replace("enable_indexed_fifo_control_bit0_3b20()", "enable_indexed_fifo_control_bit0_3b20(uVar14 >> 4,uVar14 & 15)")
    elif name in {"process_masked_can_transmit_completions_85714", "process_cancelled_can_fifo_and_buffer_routes_8584c"}:
        # 85748/85878 load r7 from tp-3918; 85788/858c0 reload from
        # tp-3915 after 85240/8043c have clobbered it. Never reuse that output.
        code = code.replace(
            "consume_channel_buffer_route_and_complete_can_tx_85240(param_1);",
            "consume_channel_buffer_route_and_complete_can_tx_85240(param_1,(byte)(&DAT_00022eae)[param_1]);", 1,
        )
        code = code.replace(
            "consume_channel_buffer_route_and_complete_can_tx_85240(param_1);",
            "consume_channel_buffer_route_and_complete_can_tx_85240(param_1,(byte)puVar4[param_1 - 0xf4b]);", 1,
        )
    elif name in {"dispatch_freshness_export_by_configured_id_902e4", "dispatch_freshness_import_by_configured_id_90342"}:
        # r8 survives 90248 and is saved in r26 on the fallback branch.
        code = re.sub(r"^\s*undefined4 extraout_r8;\n", "\n", code, flags=re.M)
        code = code.replace("extraout_r8", "param_3")
        for callee, first in (
            ("encode_current_receive_freshness_46bit_9063c", "uStack_1a"), ("encode_primary_trip_reset_36bit_906e2", "local_1c"),
            ("decode_and_store_receive_freshness_46bit_907ea", "uStack_1a"), ("decode_primary_trip_reset_and_refresh_complements_90874", "local_1c"),
        ):
            code = code.replace(f"{callee}({first},param_2)", f"{callee}({first},param_2,param_3)")
    elif name == "dispatch_routine_result_callbacks_by_row_982e4":
        # 983cc leaves r9 untouched: it is the incoming fourth argument.
        code = code.replace(
            "request_routine_payload_service31_or_reset_97c98(param_3,param_2[5],param_2 + 6)",
            "request_routine_payload_service31_or_reset_97c98(param_3,param_2[5],param_2 + 6,param_4)",
        )
    elif name == "dispatch_routine_start_callbacks_by_row_9847a":
        # 984c0/984ce/98538 likewise retain incoming r9 across the switch.
        for callee in (
            "diag_routine_class01_97e96", "diag_routine_class01_97ec2",
            "diag_routine_class01_98094",
        ):
            code = code.replace(
                f"{callee}(param_3,*(undefined4 *)(param_2 + 10),param_2 + 0xc)",
                f"{callee}(param_3,*(undefined4 *)(param_2 + 10),param_2 + 0xc,param_4)",
            )
    elif name in {"filter_two_c6b0_transition_targets_ca72a", "filter_two_c7bf_transition_targets_cb82c"}:
        # ca832/cb934 leave the first clamped quotient in r7; the second
        # quotient goes in r6, not in the overwritten C temporary's r7.
        first, first_scale, second, second_scale, callee = (
            ("DAT_febec68e", "DAT_febec6a2", "DAT_febec690", "DAT_febec6a3", "store_c68c_c6a8_with_ones_complements_ca312")
            if name == "filter_two_c6b0_transition_targets_ca72a" else
            ("DAT_febec7a2", "DAT_febec7b6", "DAT_febec7a4", "DAT_febec7b7", "store_c7a0_c7bc_with_ones_complements_cb516")
        )
        code = code.replace("  uint uVar5;", "  uint uVar5;\n  uint camry_first_quotient;")
        for value, scale in ((first, first_scale), (second, second_scale)):
            code = code.replace(
                f"    {value} = uVar3 * {scale};",
                f"    uVar4 = uVar3;\n    {value} = uVar3 * {scale};",
            )
        code = code.replace(
            f"  uVar5 = (uint){second_scale};",
            f"  camry_first_quotient = uVar4;\n  uVar5 = (uint){second_scale};",
        )
        code = code.replace(f"{callee}()", f"{callee}(uVar4,camry_first_quotient)")
    elif name in {"repair_c68e_c690_filter_residuals_ca8e0", "repair_c7a2_c7a4_filter_residuals_cb9e2"}:
        # r6/r7 retain current values unless their respective reset bit is set.
        current_first, reset_first, current_second, reset_second, callee = (
            ("DAT_febec68c", "DAT_febec692", "DAT_febec6a8", "DAT_febec694", "store_c68c_c6a8_with_ones_complements_ca312")
            if name == "repair_c68e_c690_filter_residuals_ca8e0" else
            ("DAT_febec7a0", "DAT_febec7a6", "DAT_febec7bc", "DAT_febec7a8", "store_c7a0_c7bc_with_ones_complements_cb516")
        )
        code = code.replace(
            f"{callee}()",
            f"{callee}((uVar5 & 2) ? {reset_second} : {current_second},"
            f"(uVar5 & 1) ? {reset_first} : {current_first})",
        )
    elif name == "serialize_event_and_merge_selected_output_8e074":
        # 8e1da stores the live r10 byte; the early path stores/returns 10.
        code = code.replace("void serialize_event_and_merge_selected_output_8e074(", "uint serialize_event_and_merge_selected_output_8e074(")
        code = re.sub(r"\breturn\s*;", "return DAT_febf45e3;", code)
    elif name == "nvm_write_copy_header_from_source_slot_77170":
        # 771b0's early exit retains 776fa's numeric status in r10; the
        # final path returns 74c54's status. Neither exit is a void return.
        code = code.replace("void nvm_write_copy_header_from_source_slot_77170(", "uint nvm_write_copy_header_from_source_slot_77170(")
        code = code.replace("      return;", "      return (uint)iVar4;")
        code = code.replace(
            "  nvm_stage_and_submit_program_with_optional_deferral_74c54(DAT_febf6c24,4,uVar3,9,0);\n  return;",
            "  return nvm_stage_and_submit_program_with_optional_deferral_74c54(DAT_febf6c24,4,uVar3,9,0);",
        )
    elif name == "dcm_refresh_response_copy_cursor_from_head_92bd8":
        # 92bc2 never writes r6: extraout_r6 is the queue passed on entry.
        code = code.replace("  int extraout_r6;\n", "")
        code = code.replace("extraout_r6", "param_1")
    elif name == "dcm_replace_response_queue_head_93276":
        # Both calls leave r6/r7 unchanged; append the incoming queue/node.
        code = code.replace("  F33DcmResponseQueue *queue;\n", "")
        code = code.replace("  F33DcmResponseNode *node;\n", "")
        code = code.replace("dcm_pop_response_queue_node_92b98()", "dcm_pop_response_queue_node_92b98(param_1)")
        code = code.replace(
            "dcm_append_response_node(queue,node)",
            "dcm_append_response_node(param_1,param_2)",
        )
    elif name == "request_published_mode200_phase":
        # 32016/3201a pass the low byte of the published phase plus 21.
        code = code.replace("thunk_set_indexed_request_and_clear_complement_b15ac()", "thunk_set_indexed_request_and_clear_complement_b15ac((uVar2 + 0x15) & 0xff)")
    elif name == "dcm_enqueue_general_reject":
        # 9336a's first removed node survives in r7 through the second pop
        # at 93370; both appends still use the queue held in r28.
        for declaration in (
            "  F33DcmResponseQueue *queue;\n", "  F33DcmResponseQueue *queue_00;\n",
            "  F33DcmResponseNode *node;\n",
        ):
            code = code.replace(declaration, "")
        code = code.replace(
            "  F33DcmResponseNode *node_00;",
            "  F33DcmResponseNode *node_00;\n  F33DcmResponseNode *camry_displaced_node;",
        )
        code = code.replace(
            "dcm_pop_response_queue_node_92b98(queue_01);",
            "camry_displaced_node = (F33DcmResponseNode *)dcm_pop_response_queue_node_92b98(queue_01);",
        )
        code = code.replace("dcm_pop_response_queue_node_92b98()", "dcm_pop_response_queue_node_92b98(queue_01)")
        code = code.replace(
            "dcm_append_response_node(queue,node)",
            "dcm_append_response_node(queue_01,camry_displaced_node)",
        )
        code = code.replace(
            "dcm_append_response_node(queue_00,node_00)",
            "dcm_append_response_node(queue_01,node_00)",
        )
        code = code.replace("dcm_replace_response_queue_head_93276()", "dcm_replace_response_queue_head_93276(queue_01,node_00)")
        code = code.replace("dcm_refresh_response_copy_cursor_from_head_92bd8()", "dcm_refresh_response_copy_cursor_from_head_92bd8(queue_01)")
    elif name == "dispatch_ecm_status_exception_71ae4":
        # This handler tail-transfers to 7162e or exits with EIRET. r10 is
        # restored CPU context, not an ordinary C return value.
        code = code.replace("undefined4 dispatch_ecm_status_exception_71ae4(", "void dispatch_ecm_status_exception_71ae4(")
        code = code.replace("  undefined4 in_r10;\n", "")
        code = code.replace("  undefined4 uVar2;\n", "")
        code = code.replace("uVar2 = clear_ecm_error_latches_once_or_terminate_7162e();\n    return uVar2;", "clear_ecm_error_latches_once_or_terminate_7162e();\n    return;")
        code = code.replace("in_r10 = (*(code *)", "(*(code *)")
        code = code.replace("return in_r10;", "return;")
    return code


def _rewrite_protected_registers(code: str) -> str:
    """Protected register stores must reach the host memory model, not a raw lvalue."""
    registers = {
        name: row for name, row in tree._machine_registers().items()
        if row.get("behavior") == "flmd" and re.search(rf"\b{name}\b", code)
    }
    for name, row in registers.items():
        address = int(row["address"])
        width = int(row["size"]) * 8
        code = re.sub(
            rf"\b{name}\s*=(?!=)\s*([^;]+);",
            lambda match: f"camry_write{width}(0x{address:x}u, {match.group(1)});",
            code,
        )
        code = re.sub(rf"\b{name}\b", f"camry_read{width}(0x{address:x}u)", code)
    return code


def _rewrite_inlined_mmio(code: str) -> str:
    """Keep the width of inlined accesses where a global macro is ambiguous."""
    name = syntax._signature_name(syntax._c_signature(code))
    accesses: dict[int, str] = {}
    if name == "reset_context_and_startup":
        # 3fe/6aa ld.w; 40e st.b; 418 ld.b.
        accesses = {0xffd62044: "uint32_t", 0xfff82c1c: "uint8_t", 0xfff82c04: "int8_t"}
    elif name in {"faci_force_stop_in_dataflash_mode_and_exit_78d3e", "faci_submit_program_halfwords_78e2a", "faci_read_command_area_twice_then_force_stop_78f7a"}:
        # Inlined load_u16 / store_u16. FACI also accepts byte commands.
        accesses = {0xffa20000: "uint16_t"}
    elif name == "load_tp_configuration_into_ffc1_ffc2_ffc3_banks_c9a":
        # DF0/DF8/E00/E2A/E30 store bytes, not the global label's word type.
        accesses = {address: "uint8_t" for address in (
            0xffc2400c, 0xffc24010, 0xffc2402c, 0xffc2001c, 0xffc20000,
        )}
    for address, ctype in accesses.items():
        code = re.sub(rf"\b(?:Ram|DAT_){address:08x}\b", syntax._volatile_at(f"0x{address:x}u", ctype), code)
    if name == "advance_snapshot_record_local_and_side_sources_8d15e":
        # 8d280/8d28c/8d292 are byte loads at 0,1,2, not function values.
        code = code.replace("uStack_37 = reset_vector;", f"uStack_37 = {syntax._typed_load('0u', 'uint8_t')};")
        for address in (1, 2):
            code = code.replace(f"uRam{address:08x}", syntax._typed_load(f"{address}u", "uint8_t"))
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    prefix, code = code[:brace], code[brace:]
    boot_words = []
    if name in {"configure_ffc654_registers_and_poll_7b6", "configure_ffc5b0_registers_and_poll_zero_880", "configure_ffc640_registers_and_poll_8c8", "configure_and_poll_multiple_register_banks_96e"}:
        # These reset helpers use only ld.w/st.w and sld.w/sst.w for MMIO.
        # Raw lvalues would count a store's pointer conversion as a poll read.
        boot_words = [
            (match.group(0), int(match.group(1), 16), 32)
            for match in re.finditer(r"\b(?:Ram|DAT_)(ff[0-9a-f]{6})\b", code)
        ]
    for operand, address, bits in (
        *boot_words,
        ("DCRA1CTL", 0xffd51020, 8),
        ("DCRA1COUT", 0xffd51004, 32),
        ("DCRA1CIN", 0xffd51000, 32),
        ("EEPRDCYCL", 0xffc59810, 8),
        ("DFERSTC", 0xffc5b008, 32),
        ("DFTSTCTL", 0xffc5b01c, 32),
        ("DFECCCTL", 0xffc5b000, 32),
        ("DFERRINT", 0xffc5b014, 32),
        ("FHVE15", 0xfff8a430, 32),
        ("FHVE3", 0xfff82410, 32),
        ("FSUINITR", 0xffa1008c, 16),
        ("FECCTMD", 0xffa10104, 16),
        ("FLEMU", 0xffa100f0, 8),
        ("FPCKAR", 0xffa100e4, 16),
        ("FSTATR", 0xffa10080, 32),
        ("FASTAT", 0xffa10010, 8),
        ("FAEINT", 0xffa10014, 8),
        ("FRTEINT", 0xffa1009c, 8),
        ("FPMON", 0xffa10000, 8),
        ("FACI_COMMAND_AREA", 0xffa20000, 8),
        ("FENTRYR", 0xffa10084, 16),
        ("FSADDR", 0xffa10030, 32),
        ("FEADDR", 0xffa10034, 32),
        ("UCFSERSTCLR", 0xffc62004, 32),
        ("UCFDERSTCLR", 0xffc62008, 32),
        ("CFSTSTCTL_VCI2CFBA", 0xffc622f0, 32),
        ("CFSTSTCTL_PE1", 0xffc624f0, 32),
        ("CFAPCTL", 0xffc62100, 32),
        ("CFECCCTL_VCI2CFBA", 0xffc62200, 32),
        ("CFECCCTL_PE1", 0xffc62400, 32),
        ("UCFERRINT", 0xffc62000, 32),
        (syntax._volatile_at("0xffffb2f6u", "uint8_t"), 0xffffb2f6, 8),
        (syntax._volatile_at("0xffffb2f7u", "uint8_t"), 0xffffb2f7, 8),
    ):
        pattern = rf"(?<![\w&]){re.escape(operand)}(?!\w)"
        cast = re.escape(f"(uint32_t)(0x{address:x}u)")
        pattern = pattern.replace(cast, rf"(?:{cast}|0x{address:x}u)")
        code = re.sub(
            pattern + r"\s*=(?!=)\s*([^;\n]+);",
            lambda match: f"camry_write{bits}(0x{address:x}u, {match.group(1)});",
            code,
        )
        code = re.sub(pattern, f"camry_read{bits}(0x{address:x}u)", code)
    return prefix + code


def _rewrite_merged_call_results(code: str) -> str:
    """Return the last integer call result, including calls discarded by the C."""
    signature = syntax._c_signature(code)
    name = syntax._signature_name(signature)
    facts = abi._call_facts()
    exits = facts["ret_r10"].get(name, [])
    shadowed = bool(re.search(r"\buint32_t\s+camry_r10_result\s*;", code))
    if (not shadowed and syntax._return_type_of(signature, name) != "void") or name in facts["hand"] or not exits:
        return code
    origins = set().union(*exits)
    if not origins or any(item[0] != "call" for item in origins):
        return code
    callees = {facts["names"].get(item[1]) for item in origins}
    if None in callees:
        return code
    for callee in callees:
        ctype = facts["planned"].get(callee, facts["returns"].get(callee, "void"))
        if not syntax._is_int_type(ctype):
            return code
    brace = syntax._opening_brace(code)
    head, body = code[:brace], code[brace:]
    captured = []
    for assignment in re.finditer(r"\bcamry_r10_result\s*=\s*\(", body):
        try:
            captured.append((assignment.end() - 1, c_text._match_delimiter(body, assignment.end() - 1)))
        except ValueError:
            continue
    edits: list[tuple[int, str]] = []
    found: set[str] = set()
    for callee, opening, closing in c_text._direct_calls(body, syntax._SKIP_CALLS):
        if callee in facts["preserves"]:
            continue
        ctype = facts["planned"].get(callee, facts["returns"].get(callee, "void"))
        if callee not in callees and not syntax._is_int_type(ctype):
            continue
        if (shadowed or callee not in callees) and callee in layout._pointer_return_names():
            continue
        start = opening
        while start and body[start - 1].isspace():
            start -= 1
        start -= len(callee)
        if not re.search(r"\bcamry_r10_result\s*=\s*$", body[:start]) and not any(
            left < start < right for left, right in captured
        ):
            edits.extend(((start, "(camry_r10_result = "), (closing + 1, ")")))
        found.add(callee)
    if not shadowed and not callees.issubset(found):
        return code
    for at, text in sorted(edits, reverse=True):
        body = body[:at] + text + body[at:]
    if not shadowed:
        body = re.sub(r"\breturn\s*;", "return camry_r10_result;", body)
        body = body[:1] + "\n  uint32_t camry_r10_result;" + body[1:]
        head = re.sub(rf"\bvoid(?=\s+{re.escape(name)}\s*\()", "uint32_t", head)
    return head + body


def _rewrite_firmware_pointer_arrays(code: str) -> str:
    """Stack pointer arrays are firmware address words, four bytes apart.

    The next named pointer sits COUNT*4 bytes below the array. A host pointer
    is eight bytes, so a callee that reads word COUNT sees another pointer.
    """
    match = re.search(
        r"^([ \t]*)\w[\w \t]*\*\s*"
        r"([A-Za-z_][A-Za-z0-9_]*_([0-9a-fA-F]+))\s*\[\s*(\d+)\s*\]\s*;[ \t]*\n"
        r"[ \t]*\w[\w \t]*\*\s*"
        r"([A-Za-z_][A-Za-z0-9_]*_([0-9a-fA-F]+))\s*;[ \t]*$",
        code,
        re.M,
    )
    if match is None:
        return code
    indent, name, base_text, count_text, tail, tail_text = match.group(1, 2, 3, 4, 5, 6)
    count = int(count_text)
    if int(base_text, 16) - int(tail_text, 16) != count * 4:
        return code
    if len(re.findall(rf"\b{re.escape(tail)}\b", code)) != 2:
        return code
    code = code[:match.start()] + f"{indent}uint32_t {name}[{count + 1}];" + code[match.end():]

    def store(expr: str) -> str:
        expr = expr.strip()
        if expr.startswith("camry_host_addr("):
            return expr
        return f"camry_host_addr({expr})"

    code = re.sub(
        rf"\b{re.escape(name)}\s*\[\s*(\d+)\s*\]\s*=\s*([^;]+);",
        lambda found: f"{name}[{found.group(1)}] = {store(found.group(2))};",
        code,
    )
    code = re.sub(
        rf"\b{re.escape(tail)}\s*=\s*([^;]+);",
        lambda found, name=name, count=count: f"{name}[{count}] = {store(found.group(1))};",
        code,
        count=1,
    )
    return code


def _rewrite_firmware_pointer_records(code: str) -> str:
    """A pointer local and the halfword four bytes above it are one record.

    Ghidra splits `uint32 data; uint16 length` into a host pointer and a
    separate local. The callee reads the length at offset 4. On the host the
    pointer is eight bytes, so that offset is the pointer's high half.
    """
    while True:
        match = re.search(
            r"^([ \t]*)(?:undefined1|byte|uchar|char|uint8_t)\s*\*\s*"
            r"(local_([0-9a-fA-F]+))\s*;[ \t]*$",
            code,
            re.M,
        )
        if match is None:
            return code
        indent, pointer, offset_text = match.group(1), match.group(2), match.group(3)
        half_name = f"uStack_{int(offset_text, 16) - 4:x}"
        half = re.search(
            rf"^[ \t]*(?:undefined2|ushort|uint16_t)\s+{re.escape(half_name)}\s*;[ \t]*\n",
            code,
            re.M,
        )
        assignments = re.findall(rf"\b{re.escape(pointer)}\s*=", code)
        addresses = re.findall(rf"&{re.escape(pointer)}\b", code)
        pointer_uses = re.findall(rf"\b{re.escape(pointer)}\b", code)
        half_uses = re.findall(rf"\b{re.escape(half_name)}\b", code)
        if (
            half is None
            or len(assignments) != 1
            or not addresses
            or len(pointer_uses) != 2 + len(addresses)
            or len(half_uses) != 2
        ):
            return code
        code = code[:match.start()] + f"{indent}F33BootPduInfo {pointer};" + code[match.end():]
        code = re.sub(
            rf"^[ \t]*(?:undefined2|ushort|uint16_t)\s+{re.escape(half_name)}\s*;[ \t]*\n",
            "",
            code,
            count=1,
            flags=re.M,
        )
        code = re.sub(
            rf"\b{re.escape(half_name)}\s*=\s*([^;]+);",
            rf"{pointer}.length = \1;",
            code,
            count=1,
        )

        def assign(found: re.Match[str], name: str = pointer) -> str:
            expr = found.group(1).strip()
            if not expr.startswith("camry_host_addr("):
                expr = f"camry_host_addr({expr})"
            return f"{name}.data = {expr};"

        code = re.sub(
            rf"\b{re.escape(pointer)}\s*=\s*([^;]+);",
            assign,
            code,
            count=1,
        )


def _is_uint32_subscript(text: str, arrays: set[str]) -> bool:
    match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[", text)
    if match is None or match.group(1) not in arrays:
        return False
    try:
        end = c_text._match_delimiter(text, match.end() - 1, "[]", quoted=False)
    except ValueError:
        return False
    return text[end + 1:].strip() == ""


def _is_firmware_address(expr: str, arrays: set[str], kind) -> bool:
    """One loaded firmware word, plus integer byte offsets."""
    parts = syntax._split_additive(expr.strip())
    if not parts or any(not part for part in parts):
        return False
    words = 0
    for part in parts:
        if syntax._is_word_load(part) or _is_uint32_subscript(part, arrays):
            words += 1
        elif kind(part) != "integer":
            return False
    return words == 1


def _used_as_firmware_bits(code: str, name: str) -> bool:
    """The name is added inside `camry_host_ptr`, so it still holds an address word."""
    for match in re.finditer(rf"\b{re.escape(name)}\b", code):
        if syntax._enclosing_call(code, match.start(), "camry_host_addr"):
            continue
        if syntax._enclosing_call(code, match.start(), "camry_host_ptr"):
            return True
    return False


def _cast_struct_access(code: str, op_at: int) -> tuple[int, str] | None:
    """`((Struct *)expr)[index].field` starts at the outer paren."""
    index = op_at - 1
    while index >= 0 and code[index] in " \t\n\r":
        index -= 1
    while index >= 0 and code[index] == "]":
        try:
            index = c_text._match_delimiter(code, index, "[]", step=-1, quoted=False) - 1
        except ValueError:
            return None
        while index >= 0 and code[index] in " \t\n\r":
            index -= 1
    if index < 0 or code[index] != ")":
        return None
    try:
        open_paren = c_text._match_delimiter(code, index, step=-1)
    except ValueError:
        return None
    inner = code[open_paren + 1:index].strip()
    if not inner.startswith("("):
        return None
    try:
        cast_end = c_text._match_delimiter(inner, 0)
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


def _agreed_word_field(field: str) -> int | None:
    """Offset of a 4-byte field when every struct that has it agrees."""
    offsets: list[int] = []
    for row in layout._struct_rows().values():
        for item in row["fields"]:
            if item["name"] != field:
                continue
            if item["size"] != 4:
                return None
            offsets.append(item["offset"])
    if not offsets or len(set(offsets)) != 1:
        return None
    return offsets[0]


def _arrow_receiver_start(code: str, arrow: int) -> int | None:
    """Start of `object.field` or `(object.field)` before `->` at `arrow`."""
    prev = arrow - 1
    while prev >= 0 and code[prev] in " \t\n\r":
        prev -= 1
    if prev >= 0 and code[prev] == ")":
        try:
            return c_text._match_delimiter(code, prev, step=-1)
        except ValueError:
            return None
    index = arrow
    start = None
    while True:
        start = rewrite_memory._receiver_start(code, index)
        if start is None:
            return None
        prev = start - 1
        while prev >= 0 and code[prev] in " \t\n\r":
            prev -= 1
        if prev >= 1 and code.startswith("->", prev - 1):
            index = prev - 1
            continue
        if prev >= 0 and code[prev] == "." and not code.startswith("..", prev):
            index = prev
            continue
        return start


def _rewrite_integer_arrows(code: str) -> str:
    """`slot.subfunction->callback` loads the word at that firmware pointer.

    The selection field is the address word. Every struct agrees on the
    field's offset, and the bytes load that word.
    """
    kind = expressions._kind_context(syntax._c_signature(code), code)
    spans = c_text._comment_spans(code)
    pieces: list[str] = []
    cursor = 0
    index = 0
    while index < len(code) - 1:
        if index < cursor or c_text._span_contains(spans, index) or not code.startswith("->", index):
            index += 1
            continue
        field_at = c_text._skip_space(code, index + 2)
        field = re.match(r"[A-Za-z_][A-Za-z0-9_]*", code[field_at:])
        if field is None:
            index += 2
            continue
        offset = _agreed_word_field(field.group(0))
        start = _arrow_receiver_start(code, index)
        if offset is None or start is None or start < cursor:
            index += 2
            continue
        receiver = code[start:index].strip()
        if kind(receiver) != "integer":
            index += 2
            continue
        end = field_at + field.end()
        pieces.append(code[cursor:start])
        pieces.append(syntax._typed_load(
            f"({receiver}) + {offset}u" if offset else f"({receiver})",
            "uint32_t",
        ))
        cursor = end
        index = end
    pieces.append(code[cursor:])
    return _retype_callback_words("".join(pieces))


def _retype_callback_words(code: str) -> str:
    """A callback word loaded through a firmware pointer stays that word.

    Ghidra names it a function pointer. The store is `st.w` of the address,
    and the indirect call uses the same word.
    """
    functions = layout._function_types()
    declarations = list(re.finditer(
        r"^([ \t]*)([A-Za-z_][A-Za-z0-9_]*)[ \t]*\*[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*;[ \t]*$",
        code,
        re.M,
    ))
    for match in reversed(declarations):
        type_name, name = match.group(2), match.group(3)
        if type_name not in functions:
            continue
        if re.search(rf"\b{re.escape(name)}\s*\(", code):
            continue
        assigns = list(re.finditer(rf"\b{re.escape(name)}\s*=\s*([^;]+);", code))
        if not assigns or any(
            "(*((volatile uint32_t *)camry_host_ptr(" not in item.group(1)
            for item in assigns
        ):
            continue
        code = (
            code[:match.start()]
            + f"{match.group(1)}uint32_t {name};"
            + code[match.end():]
        )
        code = re.sub(
            rf"\*\(\s*{re.escape(type_name)}\s*\*\*\s*\)\s*\(([^()]*)\)\s*=\s*{re.escape(name)}\s*;",
            lambda item, name=name: (
                "(*((volatile uint32_t *)camry_host_ptr((uint32_t)("
                f"{item.group(1)})))) = {name};"
            ),
            code,
        )
        code = re.sub(
            rf"\bcamry_host_addr\(\s*{re.escape(name)}\s*\)", name, code,
        )
    return code


def _rewrite_late_pointer_fields(code: str) -> str:
    """A cast row's pointer field is a firmware address indexed in elements.

    `((Channel *)base)[i].receive_rows + n` is the bytes' `shl` by the row size.
    The field is a uint32 in the C struct, so the add would otherwise be a byte add.
    """
    pointed = layout._pointer_field_types()
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
        if syntax._enclosing_call(code, match.start(), "camry_host_ptr"):
            continue
        found = _cast_struct_access(code, match.start())
        if found is None:
            continue
        start, struct = found
        element = by_field[match.group(1)].get(struct)
        if element is None:
            continue
        nxt = c_text._skip_space(code, match.end())
        if nxt >= len(code) or code[nxt] not in "+-,;)[":
            continue
        if code[nxt] in "+-" and nxt + 1 < len(code) and code[nxt + 1] in "=+-":
            continue
        pieces.append(code[cursor:start])
        pieces.append(syntax._host_pointer(code[start:match.end()], element))
        cursor = match.end()
    pieces.append(code[cursor:])
    return "".join(pieces)


def _integer_field_store(lhs: str) -> bool:
    """A struct field the C layout stores as an integer, including a firmware pointer."""
    match = re.search(r"(?:->|\.)\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", lhs)
    if match is None:
        return False
    field = match.group(1)
    hits = [kind for (_struct, name), kind in layout._scalar_field_kinds().items() if name == field]
    return bool(hits) and set(hits) == {"integer"}


def _rewrite_pointer_assignments(code: str, *, firmware: bool = False) -> str:
    """Store a firmware address in a pointer, and a pointer into an integer."""
    code = rewrite_memory._rewrite_pointer_word_stores(code)
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    signature = syntax._c_signature(code)
    kind = expressions._kind_context(signature, code)
    integer_targets = expressions._integer_pointer_targets(signature, code)
    doubles = set(re.findall(
        r"\*\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)", signature + "\n" + code,
    ))
    arrays = expressions._uint32_array_names() if firmware else set()
    body = code[brace:]
    replacements: list[tuple[int, int, str]] = []
    lhs_stops = ",;{}:"
    for site in syntax._assignment_sites(body, nested=True):
        lhs_at = syntax._scan_side(body, site - 1, -1, lhs_stops)
        rhs_at = syntax._scan_side(body, site + 1, 1, ",;")
        lhs = body[lhs_at:site].strip()
        rhs = body[site + 1:rhs_at].strip()
        if not lhs or not rhs or replacements and lhs_at < replacements[-1][1]:
            continue
        lhs_kind = kind(lhs)
        rhs_kind = kind(rhs)
        deref = re.fullmatch(r"\*\s*([A-Za-z_][A-Za-z0-9_]*)", lhs)
        if lhs_kind == "unknown" and deref and deref.group(1) in integer_targets:
            lhs_kind = "integer"
        if lhs_kind == "unknown" and _integer_field_store(lhs):
            lhs_kind = "integer"
        # `**(undefined4 **)slot = &DAT_addr` stores the address word.
        if lhs_kind == "unknown" and re.match(
            r"\*\*\s*\(\s*(?:undefined4|uint|int|uint32_t)\s*\*\s*\*\s*\)", lhs,
        ):
            lhs_kind = "integer"
        # `*ppuVar` where ppuVar is `uchar **` aimed at a uint32 firmware
        # pointer. The bytes load that word; the host pointer type is the
        # decompiler's spelling of the same four bytes.
        word = re.fullmatch(r"\*\s*([A-Za-z_][A-Za-z0-9_]*)", rhs)
        if not firmware and lhs_kind == "integer" and word and word.group(1) in doubles:
            replacements.append((site + 1, rhs_at, f" *(uint32_t *){word.group(1)}"))
            continue
        if (
            firmware
            and lhs_kind == "pointer"
            and _is_firmware_address(rhs, arrays, kind)
        ):
            # `*(uchar **)(slot) = cursor + 16` stores the address word.
            # A host pointer in that slot is a different value.
            if lhs.startswith("*"):
                continue
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
            # `pcVar = tp + index * stride + disp` inside `while (pcVar = ..., ...)`
            # is the address the next byte load uses. A statement-level assignment
            # is already wrapped; this pass is the one that sees the nested store.
            if (
                lhs_kind == "pointer"
                and rhs_kind == "integer"
                and not lhs.startswith("*")
            ):
                ident = re.search(r"[A-Za-z_][A-Za-z0-9_]*", lhs)
                if not (ident and _used_as_firmware_bits(body, ident.group(0))):
                    replacements.append((
                        site + 1,
                        rhs_at,
                        f" ((void *)camry_host_ptr((uint32_t)({rhs})))",
                    ))
            continue
        if lhs_kind == "pointer" and rhs_kind == "integer":
            if lhs.startswith("*"):
                continue
            replacements.append((
                site + 1,
                rhs_at,
                f" ((void *)camry_host_ptr((uint32_t)({rhs})))",
            ))
            continue
        if lhs_kind == "integer" and rhs_kind == "pointer":
            stored = "0" if syntax._null_pointer(rhs) else f"camry_host_addr({rhs})"
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
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    structs = layout._struct_rows()
    pointed = layout._pointer_field_types()
    if not structs or not pointed:
        return code
    var_types, struct_pointers = layout._struct_bindings(code)
    if not var_types:
        return code
    signature = syntax._c_signature(code)
    pointers = syntax._pointer_names(signature, code)
    kind = expressions._kind_context(signature, code, pointers)
    body = code[brace:]
    spans = c_text._comment_spans(body)
    struct_names = set(structs)
    replacements: list[tuple[int, int, str]] = []
    for match in layout._FIELD_ACCESS.finditer(body):
        if c_text._span_contains(spans, match.start()):
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
        nxt = c_text._skip_space(body, match.end())
        char = body[nxt] if nxt < len(body) else ""
        if char == "[":
            replacements.append((match.start(), match.end(), syntax._host_pointer(access, element)))
            continue
        if body.startswith("->", nxt) and element in struct_names:
            replacements.append((match.start(), match.end(), syntax._host_pointer(access, element)))
            continue
        if match.start() > 0 and body[match.start() - 1] == "*":
            prev = body[match.start() - 2] if match.start() > 1 else ""
            if prev not in "*&/=" and not (prev.isalnum() or prev == "_"):
                replacements.append((
                    match.start() - 1,
                    match.end(),
                    f"*{syntax._host_pointer(access, element)}",
                ))
                continue
        if char == "=" and not body.startswith("==", nxt):
            rhs_at = syntax._rhs_end(body, nxt + 1)
            rhs = body[nxt + 1:rhs_at].strip()
            if not rhs:
                continue
            stored = "0" if syntax._null_pointer(rhs) else (
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
