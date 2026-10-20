"""Target metadata, C layouts, and instruction-backed access widths."""
from __future__ import annotations

from tools import REPO_ROOT
import json
import re

from . import syntax, tree



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


def _hand_param_types() -> dict[str, list[str]]:
    header = syntax._strip_comments((tree.ROOT / "include" / "camry.h").read_text(encoding="utf-8"))
    header = re.sub(r"static inline\b.*?\{.*?\n\}", "", header, flags=re.S)
    flat = re.sub(r"\s+", " ", header)
    found: dict[str, list[str]] = {}
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(([^()]*)\)\s*;", flat):
        found[match.group(1)] = syntax._param_type_list(match.group(2))
    found["camry_host_addr"] = ["const void *"]
    return found


_GHIDRA_GP = 0xFEBF9800
_RUNTIME_GP = 0xFEBEB800
_GP_DELTA = (_GHIDRA_GP - _RUNTIME_GP) & 0xFFFFFFFF


# Application r5 differs from Ghidra's boot-table context below 0x20000.
_GHIDRA_TP = 0x869C
_RUNTIME_TP = 0x23DFC


_NAMED_MACROS: list[tuple[str, int, str]] | None = None


def _named_macros() -> list[tuple[str, int, str]]:
    """Curated address declarations, with generated declarations for unnamed data."""
    global _NAMED_MACROS
    if _NAMED_MACROS is not None:
        return _NAMED_MACROS
    header = tree.COMMON_HEADER
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
    curated = {}
    for name, (address, ctype, is_array) in _data_layouts().items():
        expansion = (
            _array_macro(name, address, ctype).split(None, 2)[2]
            if is_array else f"(*((volatile {ctype} *)camry_host_ptr(0x{address:x}u)))"
        )
        curated[name] = (name, address, expansion)
    found = [row for row in found if row[0] not in curated]
    found.extend(curated.values())
    _NAMED_MACROS = found
    return found


_STACK_LOCAL = re.compile(r"^(?:local|[A-Za-z_]\w*Stack)_([0-9A-Fa-f]+)$")
_STACK_WIDTH = {
    "undefined1": 1, "uchar": 1, "byte": 1, "char": 1, "bool": 1,
    "uint8_t": 1, "int8_t": 1,
    "undefined2": 2, "ushort": 2, "short": 2, "uint16_t": 2, "int16_t": 2,
    "undefined3": 3, "uint3": 3,
    "undefined4": 4, "uint": 4, "int": 4, "undefined": 4,
    "uint32_t": 4, "int32_t": 4, "float": 4,
    "undefined8": 8, "uint64_t": 8, "double": 8,
}
_STACK_CTYPE = {
    "char": "int8_t", "short": "int16_t", "int": "int32_t",
    "undefined1": "uint8_t", "uchar": "uint8_t", "byte": "uint8_t", "bool": "uint8_t",
    "undefined2": "uint16_t", "ushort": "uint16_t",
    "undefined4": "uint32_t", "uint": "uint32_t", "undefined": "uint32_t",
    "float": "uint32_t",
}
_SCALAR_STRIDE = {
    "uint8_t": 1, "int8_t": 1, "uchar": 1, "char": 1, "byte": 1, "undefined1": 1,
    "undefined": 1,
    "uint16_t": 2, "int16_t": 2, "ushort": 2, "short": 2, "undefined2": 2,
    "uint32_t": 4, "int32_t": 4, "uint": 4, "int": 4, "undefined4": 4,
}


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
    rows = list(tree._load_jsonl(tree.ROOT / "data.jsonl"))
    by_addr = {tree._address(row["addr"]): row for row in rows}

    def concrete_type(type_name: str, seen: set[int]) -> str:
        """`@0xADDR` is the type of the object already defined at that address."""
        type_name = type_name.replace(" ", "")
        if not type_name.startswith("@"):
            return type_name
        try:
            addr = tree._address(type_name[1:])
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
        addr = tree._address(row["addr"])
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
    for name, row in tree._machine_registers().items():
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

        code = re.sub(r"return\s+&([A-Za-z_][A-Za-z0-9_]*)\b(?!\s*\.)", returned, code)
    # `&queue.field` is the field's address. Replacing only the object drops the offset.
    return re.sub(r"&([A-Za-z_][A-Za-z0-9_]*)\b(?!\s*\.)", replace, code)


_FUNCTION_ENTRIES: dict[str, int] | None = None
_POINTER_RETURNS: set[str] | None = None


def _corpus_functions() -> list[dict]:
    from tools.project.analysis_target import target as resolve_target
    from tools.project.pseudo import load_corpus

    metadata = resolve_target(tree.TARGET)[1]
    _meta, functions = load_corpus(REPO_ROOT / metadata["decompiler_corpus"])
    names = {int(row["addr"], 16): row["name"] for row in tree.load_symbols()}
    return [{**row, "name": names[int(row["entry_addr"], 16)]} for row in functions]


def _function_entries() -> dict[str, int]:
    global _FUNCTION_ENTRIES
    if _FUNCTION_ENTRIES is None:
        _FUNCTION_ENTRIES = {
            row["name"]: int(row["entry_addr"], 16) for row in _corpus_functions()
        }
    return _FUNCTION_ENTRIES


def _header_pointer_returns() -> set[str]:
    """Prototypes in common.h win over a void corpus signature.

    Equivalent bodies such as `nvm_write_marker_for_current_descriptor_slot_75bfe` return `undefined *`. The corpus
    text still says void, and the caller compares r10 as an integer.
    """
    header = tree.COMMON_HEADER
    found: set[str] = set()
    if not header.exists():
        return found
    for line in header.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text.endswith(";") or "(" not in text or not syntax._returns_pointer(text[:-1]):
            continue
        name = text.split("(", 1)[0].split()[-1].lstrip("*")
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            found.add(name)
    return found


def _hand_integer_returns() -> set[str]:
    """camry.h owns these returns. A corpus `void *` is not a host pointer."""
    header = syntax._strip_comments((tree.ROOT / "include" / "camry.h").read_text(encoding="utf-8"))
    found: set[str] = set()
    for line in header.splitlines():
        text = line.strip()
        if not text.endswith(";") or "(" not in text:
            continue
        head = text.split("(", 1)[0]
        if "*" in head:
            continue
        name = head.split()[-1]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            found.add(name)
    return found


def _pointer_return_names() -> set[str]:
    global _POINTER_RETURNS
    if _POINTER_RETURNS is None:
        _POINTER_RETURNS = {
            row["name"]
            for row in _corpus_functions()
            if syntax._returns_pointer(syntax._c_signature(row["decompiled_c"]))
        }
        _POINTER_RETURNS.update(_header_pointer_returns())
        _POINTER_RETURNS.difference_update(_hand_integer_returns())
        from .sources import load_c_bodies, retained_paths

        retained, _duplicates = load_c_bodies(retained_paths())
        for row in tree.load_matched():
            name = row["name"]
            if row.get("status") not in tree._CHECKED_STATUS or name not in retained:
                continue
            if syntax._returns_pointer(syntax._c_signature(retained[name])):
                _POINTER_RETURNS.add(name)
            else:
                _POINTER_RETURNS.discard(name)
    return _POINTER_RETURNS


_ACCESS_WIDTHS: dict[int, int] | None = None


def _access_widths() -> dict[int, int]:
    """Majority load/store width at each data address the decompiler references."""
    global _ACCESS_WIDTHS, _ACCESS_SIGNED
    if _ACCESS_WIDTHS is not None:
        return _ACCESS_WIDTHS
    from .lifting.decode import decode_at
    from tools.project.analysis_target import target as resolve_target
    from tools.project.pseudo import load_corpus

    metadata = resolve_target(tree.TARGET)[1]
    image = (REPO_ROOT / metadata["codeflash"]).read_bytes()
    _meta, functions = load_corpus(REPO_ROOT / metadata["decompiler_corpus"])
    sizes = {
        "ld.b": 1, "ld.bu": 1, "sld.b": 1, "sld.bu": 1, "st.b": 1, "sst.b": 1,
        "ld.h": 2, "ld.hu": 2, "sld.h": 2, "sld.hu": 2, "st.h": 2, "sst.h": 2,
        "ld.w": 4, "sld.w": 4, "st.w": 4, "sst.w": 4,
    }
    signed_ops = {"ld.b", "sld.b", "ld.h", "sld.h"}
    unsigned_ops = {"ld.bu", "sld.bu", "ld.hu", "sld.hu"}
    counts: dict[int, dict[int, int]] = {}
    signed_counts: dict[int, int] = {}
    unsigned_counts: dict[int, int] = {}
    for row in functions:
        for ref in row.get("data_references") or []:
            origin = int(ref["from_addr"], 16)
            if origin >= len(image):
                continue
            inst = decode_at(image, origin)
            if inst is None or not inst.text:
                continue
            mnemonic = inst.text.split()[0]
            width = sizes.get(mnemonic)
            if width is None:
                continue
            dest = int(ref["to_addr"], 16)
            bucket = counts.setdefault(dest, {})
            bucket[width] = bucket.get(width, 0) + 1
            if mnemonic in signed_ops:
                signed_counts[dest] = signed_counts.get(dest, 0) + 1
            elif mnemonic in unsigned_ops:
                unsigned_counts[dest] = unsigned_counts.get(dest, 0) + 1
    _ACCESS_WIDTHS = {
        addr: max(bucket, key=bucket.get)
        for addr, bucket in counts.items()
    }
    _ACCESS_SIGNED = {
        addr
        for addr, count in signed_counts.items()
        if count and not unsigned_counts.get(addr)
    }
    return _ACCESS_WIDTHS


_ACCESS_SIGNED: set[int] | None = None


def _access_signed() -> set[int]:
    """ROM addresses whose byte or halfword loads are exclusively sign-extending."""
    if _ACCESS_SIGNED is None:
        _access_widths()
    return _ACCESS_SIGNED or set()


def _scalar_type(address: int, default: str = "uint32_t") -> str:
    """ROM words are signed. A byte or halfword is signed only when every load sign-extends.

    `ld.w` has no unsigned form. An unsigned DAT_ type makes `int / DAT_` an
    unsigned divide. `ld.bu` and `ld.hu` stay unsigned so a table compare keeps
    the byte the instruction zero-extended.
    """
    width = _access_widths().get(address, 0)
    if address < 0x100000:
        if width == 4 or width == 0:
            return "int32_t"
        if address in _access_signed():
            return {1: "int8_t", 2: "int16_t"}.get(width, "int32_t")
        return {1: "uint8_t", 2: "uint16_t"}.get(width, "int32_t")
    return {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}.get(width, default)


def _oracle_addresses() -> set[int]:
    found: set[int] = set()
    for scenario in tree._load_jsonl(tree.ROOT / "oracles.jsonl"):
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
            found.add(tree._address(entry["address"]))
    return found


def _prototype_names() -> set[str]:
    header = (tree.ROOT / "include" / "camry.h").read_text(encoding="utf-8")
    return set(re.findall(
        r"^[A-Za-z_][A-Za-z0-9_ \t\*]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        header,
        flags=re.M,
    ))


def _self_call_count(row: dict) -> int:
    return sum(
        1
        for match in syntax._CALL.finditer(syntax._strip_comments(row["decompiled_c"]))
        if match.group(1) == row["name"]
    )


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
        path = tree.ROOT / "struct_layouts.json"
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
