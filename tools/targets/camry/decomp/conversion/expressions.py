"""C expression kinds and host-pointer classification."""
from __future__ import annotations

import re

from tools.targets.camry.decomp import c_text, layout, syntax, tree

_DATA_ARRAYS: set[str] | None = None
_DATA_SCALARS: set[str] | None = None


def _data_name_kinds() -> tuple[set[str], set[str]]:
    global _DATA_ARRAYS, _DATA_SCALARS
    if _DATA_ARRAYS is None or _DATA_SCALARS is None:
        arrays: set[str] = set()
        scalars: set[str] = set()
        for name, (_addr, _ctype, is_array) in layout._data_layouts().items():
            (arrays if is_array else scalars).add(name)
        scalars.update(tree._machine_registers())
        _DATA_ARRAYS = arrays
        _DATA_SCALARS = scalars
    return _DATA_ARRAYS, _DATA_SCALARS


def _kind_context(signature: str, code: str, pointers: set[str] | None = None):
    """Classify an expression as pointer, integer, null, or unknown."""
    pointers = syntax._pointer_names(signature, code) if pointers is None else pointers
    arrays = set(re.findall(
        r"^[ \t]*(?!(?:return|goto)\b)(?:[A-Za-z_][A-Za-z0-9_]*[ \t]+)+"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\])+\s*;",
        signature + "\n" + code, re.M,
    ))
    data_arrays, data_scalars = _data_name_kinds()
    arrays |= data_arrays
    doubles = set(re.findall(
        r"\*\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)", signature + "\n" + code,
    ))
    integers = (
        syntax._declared_integers(signature, code) | data_scalars
        | set(re.findall(r"\b(?:Ram|uRam)[0-9a-fA-F]+\b", code))
        | syntax._ARCHITECTURAL_SCALARS
    ) - pointers - arrays - doubles
    functions = set(layout._function_entries())
    var_structs = layout._struct_var_types(signature + "\n" + code)
    field_kinds = layout._scalar_field_kinds()
    integer_pointers = _integer_pointer_targets(signature, code)

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
            integer_pointers=integer_pointers,
        )

    return kind


_STRUCT_POINTER_MACROS: dict[str, str] | None = None


def _struct_pointer_macros() -> dict[str, str]:
    """Macros that are `camry_host_ptr` of a struct array."""
    global _STRUCT_POINTER_MACROS
    if _STRUCT_POINTER_MACROS is None:
        found: dict[str, str] = {}
        structs = set(layout._struct_rows())
        for name, _address, expansion in layout._named_macros():
            match = re.match(
                r"\(\(volatile ([A-Za-z_][A-Za-z0-9_]*) \*\)camry_host_ptr\(",
                expansion,
            )
            if match and match.group(1) in structs:
                found[name] = match.group(1)
        _STRUCT_POINTER_MACROS = found
    return _STRUCT_POINTER_MACROS


def _array_field_pointer(name: str, rest: str) -> bool:
    """`stages[index].raw` decays to the byte pointer at that array field."""
    struct = _struct_pointer_macros().get(name)
    if struct is None or not rest.startswith("["):
        return False
    try:
        end = c_text._match_delimiter(rest, 0, "[]", quoted=False)
    except ValueError:
        return False
    tail = rest[end + 1:].lstrip()
    field = re.match(r"\.([A-Za-z_][A-Za-z0-9_]*)", tail)
    if field is None or tail[field.end():].strip():
        return False
    for row in layout._struct_rows()[struct]["fields"]:
        if row["name"] == field.group(1) and "[" in row["type"]:
            return True
    return False


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
    integer_pointers: set[str] | None = None,
) -> str:
    text = text.strip()
    if not text:
        return "unknown"
    while syntax._fully_wrapped(text):
        inner = text[1:-1].strip()
        if syntax._is_pointer_type(inner) or syntax._is_int_type(inner):
            break
        text = inner
    parts = c_text._split_args(text)
    if len(parts) > 1:
        # A comma expression keeps side effects but has its final operand's type.
        return _expr_kind(
            parts[-1],
            pointers=pointers,
            arrays=arrays,
            integers=integers,
            functions=functions,
            doubles=doubles,
            var_structs=var_structs,
            field_kinds=field_kinds,
            integer_pointers=integer_pointers,
        )
    ops = syntax._binary_ops(text)
    if ops:
        # `pointer + index * scale` is a pointer plus a scaled integer.
        # Folding every operator left to right turns that into a multiply.
        for level in syntax._KIND_PREC:
            chosen = [item for item in ops if item[1] in level]
            if not chosen:
                continue
            index, op = chosen[-1]
            left = _expr_kind(
                text[:index],
                pointers=pointers,
                arrays=arrays,
                integers=integers,
                functions=functions,
                doubles=doubles,
                var_structs=var_structs,
                field_kinds=field_kinds,
                integer_pointers=integer_pointers,
            )
            right = _expr_kind(
                text[index + len(op):],
                pointers=pointers,
                arrays=arrays,
                integers=integers,
                functions=functions,
                doubles=doubles,
                var_structs=var_structs,
                field_kinds=field_kinds,
                integer_pointers=integer_pointers,
            )
            return syntax._fold_kind(op, left, right)
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
            integer_pointers=integer_pointers,
        )
        if text[0] == "!":
            return "integer" if inner != "unknown" else "unknown"
        if inner == "pointer":
            return "unknown"
        return "integer" if inner == "null" else inner
    if text.startswith('"'):
        end = c_text._skip_quoted(text, 0)
        rest = text[end:].strip()
        if not rest:
            return "pointer"
        if rest.startswith("["):
            try:
                close = c_text._match_delimiter(rest, 0, "[]", quoted=False)
            except ValueError:
                return "unknown"
            return "integer" if not rest[close + 1:].strip() else "unknown"
        return "unknown"
    if re.fullmatch(r"0x0+[uU]?|0[uU]?|NULL", text):
        return "null"
    if re.fullmatch(r"0x[0-9A-Fa-f]+[uU]?|\d+[uU]?", text):
        return "integer"
    if text.startswith("&"):
        return "pointer"
    if text.startswith("camry_host_ptr"):
        return "pointer"
    if text.startswith("camry_host_addr"):
        return "integer"
    if text.startswith("*"):
        inner = text[1:].strip()
        named = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)", inner)
        if named and named.group(1) in (integer_pointers or set()):
            return "integer"
        while syntax._fully_wrapped(inner):
            inner = inner[1:-1].strip()
        if inner.startswith("("):
            try:
                end = c_text._match_delimiter(inner, 0)
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
            end = c_text._match_delimiter(text, 0)
        except ValueError:
            return "unknown"
        inner = " ".join(text[1:end].split())
        if syntax._is_pointer_type(inner):
            return "pointer"
        if syntax._is_int_type(inner):
            return "integer"
        return "unknown"
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text)
    if match is None:
        return "unknown"
    name = match.group(0)
    rest = text[match.end():].lstrip()
    field_kind = layout._scalar_field_kind(name, rest, var_structs, field_kinds)
    if field_kind is not None:
        return field_kind
    if _array_field_pointer(name, rest):
        return "pointer"
    if name in functions and rest.startswith("("):
        try:
            close = c_text._match_delimiter(rest, 0)
        except ValueError:
            return "unknown"
        if close == len(rest) - 1:
            return "pointer" if name in layout._pointer_return_names() else "integer"
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
            # A uint32 table subscript is the loaded word, an integer address.
            if name in _uint32_array_names() or name in _uint32_slot_names():
                return "integer"
            if name in arrays and name not in pointers:
                return "unknown"
            return "integer"
        return "unknown"
    if _array_field_pointer(name, rest):
        return "pointer"
    return "unknown"


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
        for name, _address, expansion in layout._named_macros()
        if expansion.startswith("((volatile uint32_t *)camry_host_ptr(")
    }


_UINT32_SLOTS: set[str] | None = None


def _uint32_slot_names() -> set[str]:
    """common.h macros that load one stored pointer word."""
    global _UINT32_SLOTS
    if _UINT32_SLOTS is None:
        _UINT32_SLOTS = {
            name
            for name, _address, expansion in layout._named_macros()
            if expansion.startswith((
                "(*((volatile uint32_t *)camry_host_ptr(",
                "(*((volatile int32_t *)camry_host_ptr(",
            ))
        }
    return _UINT32_SLOTS
