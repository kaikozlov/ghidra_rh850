"""Firmware runtime GP/TP, signed-load, and system-register recovery."""
from __future__ import annotations

import re

from tools.targets.camry.decomp import c_text, layout, syntax, tree
from tools.targets.camry.decomp.conversion import rewrite_context



def _rewrite_eimk_stores(code: str) -> str:
    """`ptr->EIMK = bit` clears bit 7 of the low byte, then ORs the new bit back."""
    pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*->\s*EIMK\s*=")
    pieces: list[str] = []
    cursor = 0
    for match in pattern.finditer(code):
        if match.start() < cursor:
            continue
        depth = 0
        end = match.end()
        while end < len(code):
            char = code[end]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif char == ";" and depth == 0:
                break
            end += 1
        expr = code[match.end():end].strip()
        if not expr:
            continue
        byte = f"(*((volatile uint8_t *)({match.group(1)})))"
        pieces.append(code[cursor:match.start()])
        pieces.append(
            f"{byte} = ({byte} & 0x7fu)"
            f" | (uint8_t)(((uint32_t)({expr}) & 1u) << 7)"
        )
        cursor = end
    pieces.append(code[cursor:])
    return "".join(pieces)


def _rewrite_eic(code: str) -> str:
    """An EIC register is one halfword. EIRF is bit 12; EIMK is bit 7 of the low byte."""
    code = re.sub(
        r"\bEIC_Register\s+([A-Za-z_][A-Za-z0-9_]*)\s*;",
        r"uint16_t \1;",
        code,
    )
    code = re.sub(r"\(EIC_Register\)(?!\s*\*)", "(uint16_t)", code)
    code = re.sub(
        r"\b([A-Za-z_][A-Za-z0-9_]*)\.EIRF\b",
        r"((\1 >> 12) & 1u)",
        code,
    )
    return _rewrite_eimk_stores(code)


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
    header = tree.COMMON_HEADER
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
    from .lifting.graph import load_image, walk_symbol

    image = load_image()
    found: dict[str, dict[int, int]] = {}
    hits: dict[str, set[int]] = {}
    for row in tree.load_symbols():
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
            parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
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
            ghidra = (layout._GHIDRA_GP + disp) & 0xFFFFFFFF
            runtime = (layout._RUNTIME_GP + disp) & 0xFFFFFFFF
            if ghidra not in immediates:
                pairs[ghidra] = runtime
                touched.add(ghidra)
        # The decompiler materializes gp as this immediate even when the bytes
        # only copy r4 into another register before the access.
        if layout._GHIDRA_GP not in immediates:
            pairs[layout._GHIDRA_GP] = layout._RUNTIME_GP
        if int(row["addr"], 16) < 0x20000 and accesses:
            runtime_hits = [(layout._RUNTIME_GP + disp) & 0xffffffff for disp in accesses]
            for addr, size in _object_sizes().values():
                disp = (addr - layout._GHIDRA_GP + 0x80000000) % 0x100000000 - 0x80000000
                runtime = (addr - layout._GP_DELTA) & 0xffffffff
                if (
                    -0x8000 <= disp < 0x8000
                    and addr not in immediates
                    and runtime not in immediates
                    and any(runtime <= hit < runtime + size for hit in runtime_hits)
                ):
                    # A typed member can hide the GP-relative containing object.
                    pairs.setdefault(addr, runtime)
                    pairs.setdefault(runtime, runtime)
        if pairs:
            found[row["name"]] = pairs
            if touched:
                hits[row["name"]] = touched
    _GP_PAIRS = found
    _GP_HITS = hits
    return found
_TP_PAIRS: dict[str, dict[int, int]] | None = None


def _tp_address_map() -> dict[str, dict[int, int]]:
    """Ghidra tp+disp addresses whose bytes actually use r5, the harness tp."""
    global _TP_PAIRS
    if _TP_PAIRS is not None:
        return _TP_PAIRS
    from .lifting.graph import load_image, walk_symbol

    image = load_image()
    found: dict[str, dict[int, int]] = {}
    for row in tree.load_symbols():
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        pairs: dict[int, int] = {}
        immediates: set[int] = set()
        accesses: list[int] = []
        holds = {5}
        shifted: dict[int, int] = {}
        for inst in fn.insts:
            parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
            if parsed is None:
                continue
            name, args = parsed
            for arg in args:
                if isinstance(arg, int) and (arg > 0xFFFF or arg == layout._GHIDRA_TP):
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
                name in {"movea", "addi"}
                and len(args) >= 3
                and isinstance(args[0], int)
                and isinstance(args[2], int)
                and (args[1] in holds or args[1] in shifted)
            ):
                shifted[args[0]] = shifted.get(args[1], 0) + args[2]
                accesses.append(shifted[args[0]])
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
        if accesses:
            # A typed table alias may hide TP itself behind an indexed global.
            accesses.append(0)
        for disp in accesses:
            ghidra = (layout._GHIDRA_TP + disp) & 0xFFFFFFFF
            runtime = (layout._RUNTIME_TP + disp) & 0xFFFFFFFF
            if ghidra not in immediates:
                pairs[ghidra] = runtime
        if pairs:
            found[row["name"]] = pairs
    _TP_PAIRS = found
    return found


def _rewrite_runtime_tp(code: str) -> str:
    """Use the harness tp for an address the bytes form as r5+disp."""
    signature = syntax._c_signature(code)
    try:
        name = syntax._signature_name(signature)
    except (AssertionError, ValueError):
        return code
    pairs = _tp_address_map().get(name)
    if not pairs:
        return code
    code = _rewrite_addressed_macros(_apply_gp_pairs(code, pairs), pairs)
    if layout._function_entries().get(name, 0x20000) < 0x20000:
        for address in set(pairs.values()):
            offset = (address - layout._RUNTIME_TP) & 0xffffffff
            code = re.sub(rf"\b0x{address:x}u?\b", f"(camry_tp + 0x{offset:x}u)", code, flags=re.I)
    return code


def _rewrite_addressed_macros(code: str, pairs: dict[int, int]) -> str:
    """A named symbol hides the address `_apply_gp_pairs` would retarget."""
    def replace_unnamed(match: re.Match[str]) -> str:
        address = int(match.group(1), 16)
        runtime = pairs.get(address)
        if runtime is None:
            return match.group(0)
        return syntax._volatile_at(f"0x{runtime:x}u", layout._scalar_type(address))

    code = re.sub(r"\b(?:DAT|UNK)_([0-9a-fA-F]+)\b", replace_unnamed, code)
    for name, address, expansion in layout._named_macros():
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
    header = tree.COMMON_HEADER
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
        name = syntax._signature_name(syntax._c_signature(code))
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
            closing = c_text._match_delimiter(code, call + len("camry_host_ptr"))
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
    structs = layout._struct_rows()
    found: dict[str, tuple[int, int]] = {}
    for row in tree._load_jsonl(tree.ROOT / "data.jsonl"):
        type_name = row["type"].replace(" ", "")
        if type_name.startswith("@"):
            continue
        base = type_name.split("[", 1)[0]
        dims = [int(item) for item in re.findall(r"\[(\d+)\]", type_name)]
        if base in structs:
            elem = int(structs[base]["size"])
        elif base in layout._ARRAY_ELEMENTS:
            elem = layout._ARRAY_ELEMENTS[base][1]
        elif base in layout._SCALAR_TYPES:
            elem = widths.get(layout._SCALAR_TYPES[base], 1)
        else:
            elem = 1
        size = elem
        for dim in dims:
            size *= dim
        found[row["name"]] = (tree._address(row["addr"]), max(size, 1))
    _object_sizes.cached = found
    return found


def _gp_objects() -> list[tuple[str, int, int, str]]:
    """Named common.h objects in the Ghidra gp window: name, address, size, expression."""
    global _GP_OBJECTS
    if _GP_OBJECTS is not None:
        return _GP_OBJECTS
    sizes = _object_sizes()
    found: list[tuple[str, int, int, str]] = []
    header = tree.COMMON_HEADER
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
            disp = (addr - layout._GHIDRA_GP) & 0xFFFFFFFF
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
            runtime = (addr - layout._GP_DELTA) & 0xFFFFFFFF
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
    from .lifting.graph import load_image, walk_symbol

    image = load_image()
    found: dict[str, dict[int, int]] = {}
    for row in tree.load_symbols():
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        signed: dict[int, int] = {}
        unsigned: set[int] = set()
        holds_gp = {4}
        shifted: dict[int, int] = {}
        for inst in fn.insts:
            parsed = syntax._stmt_parts(inst.stmt) if inst.stmt else None
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
                    addr = (layout._RUNTIME_GP + disp) & 0xFFFFFFFF
                elif base in shifted:
                    addr = (layout._RUNTIME_GP + shifted[base] + disp) & 0xFFFFFFFF
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


def _cast_value_reads(code: str, name: str, cast: str) -> str:
    """Sign-extend reads of an unsigned lvalue. Leave stores and existing signed casts."""
    spans = c_text._comment_spans(code)
    signed_casts = {
        "int8_t": "int8_t|signed char",
        "int16_t": "int16_t|short",
        "int32_t": "int32_t|int|long",
    }[cast]

    def replace(match: re.Match[str]) -> str:
        if c_text._span_contains(spans, match.start()):
            return match.group(0)
        before = code[:match.start()]
        after = code[match.end():]
        if re.search(
            rf"(?:(?<!&)&|\((?:{signed_casts})\))\s*$", before
        ):
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


def _rewrite_signed_word_reads(code: str) -> str:
    """Keep signed word uses signed without changing the shared storage type."""
    text = syntax._strip_comments(code)
    for name in sorted(_unsigned32_names(code)):
        if not name.startswith("DAT_"):
            continue
        token = rf"\b{re.escape(name)}\b"
        if re.search(
            rf"(?:{token}\s*<\s*0\b|-1\s*<\s*{token}|"
            rf"\(longlong\)\s*{token})",
            text,
        ):
            code = _cast_value_reads(code, name, "int32_t")
    return code


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


_SIGNED_DIVISIONS: set[str] | None = None


def _signed_division_names() -> set[str]:
    """Functions whose divides are signed in the bytes, with no unsigned divide beside them."""
    global _SIGNED_DIVISIONS
    if _SIGNED_DIVISIONS is not None:
        return _SIGNED_DIVISIONS
    from .lifting.graph import load_image, walk_symbol

    image = load_image()
    found: set[str] = set()
    for row in tree.load_symbols():
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        signed = unsigned = 0
        for inst in fn.insts:
            stmt = inst.stmt or ""
            if "camry_div3" not in stmt and "camry_divh2" not in stmt:
                continue
            if re.search(r",\s*1\s*[,)]", stmt):
                signed += 1
            else:
                unsigned += 1
        if signed and not unsigned:
            found.add(row["name"])
    _SIGNED_DIVISIONS = found
    return found


def _rewrite_signed_divides(code: str) -> str:
    """`int / uint32_t` is an unsigned divide. The bytes used a signed one."""
    signature = syntax._c_signature(code)
    try:
        name = syntax._signature_name(signature)
    except (AssertionError, ValueError):
        return code
    if name not in _signed_division_names():
        return code
    pattern = re.compile(
        r"(?<![\w.)])([A-Za-z_][A-Za-z0-9_]*)\s*([/%])\s*([A-Za-z_][A-Za-z0-9_]*)"
    )

    def replace(match: re.Match[str]) -> str:
        line = code[:match.start()].rsplit("\n", 1)[-1]
        if line.lstrip().startswith(("*", "//")):
            return match.group(0)
        left, op, right = match.groups()
        return f"(int){left} {op} (int){right}"

    code = pattern.sub(replace, code)
    unsigned = _unsigned32_names(code)
    divisions = re.compile(r"([/%])\s*(0x[0-9a-fA-F]+|[0-9]+)\b")
    cursor = 0
    while (match := divisions.search(code, cursor)) is not None:
        cursor = match.end()
        if c_text._span_contains(c_text._comment_spans(code), match.start()):
            continue
        start = syntax._scan_side(code, match.start() - 1, -1, "+-<>=!&|^?:;,{}")
        returned = re.match(r"\s*return\b\s*", code[start:match.start()])
        if returned:
            start += returned.end()
        numerator = code[start:match.start()].strip()
        if not numerator or not any(
            re.search(rf"\b{re.escape(value)}\b", numerator) for value in unsigned
        ):
            continue
        if re.search(r"\b(?:longlong|ulonglong|int64_t|uint64_t)\b", numerator):
            continue
        subject = numerator
        while syntax._fully_wrapped(subject):
            subject = subject[1:-1].strip()
        signed_cast = re.match(r"\((?:int|int32_t)\)", subject)
        if signed_cast and syntax._unary_operand_end(subject, signed_cast.end()) == len(subject):
            continue
        replacement = f" (int)({numerator}) {match.group(1)} (int){match.group(2)}"
        code = code[:start] + replacement + code[match.end():]
        cursor = start + len(replacement)
    return code


def _rewrite_signed_values(code: str) -> str:
    code = _rewrite_signed_word_reads(code)
    code = _rewrite_unsigned_saturation(code)
    signature = syntax._c_signature(code)
    try:
        name = syntax._signature_name(signature)
    except (AssertionError, ValueError):
        return code
    if name == "condition_measured_phase_currents":
        # 4897a/4897e and 48c92/48c96 load signed raw phases; 48986/48c9e
        # sign-extend the third. Ghidra forwards them through 7e46..7e50,
        # whose shared uint16 storage must not zero-extend reconstruction sums.
        for addr in range(0xFEBE7E46, 0xFEBE7E52, 2):
            code = _cast_value_reads(code, f"DAT_{addr:x}", "int16_t")
    code = _rewrite_signed_loads(code, _signed_load_map().get(name, {}))
    return _rewrite_signed_divides(code)


def _rewrite_runtime_gp(code: str) -> str:
    """Use the runtime gp for an address the bytes form as r4+disp.

    Application accesses use the calibrated application base. Boot helpers keep
    their incoming register so a caller's execution context is not discarded.
    """
    signature = syntax._c_signature(code)
    try:
        name = syntax._signature_name(signature)
    except (AssertionError, ValueError):
        return code
    pairs = _gp_address_map().get(name)
    if not pairs:
        return code
    if layout._function_entries().get(name, 0x20000) < 0x20000:
        # r4 is the boot gp. Folding the displacement through the application
        # base stores at 0xfebe.... The harness gp register already holds the
        # boot base for these entries.
        code = _rewrite_addressed_macros(code, pairs)
        for symbol, address, expansion in layout._named_macros():
            if address in pairs and pairs[address] == address:
                code = re.sub(rf"\b{re.escape(symbol)}\b", lambda _match: expansion, code)
        staged: list[tuple[str, str]] = []
        for index, (ghidra, runtime) in enumerate(pairs.items()):
            offset = (int(runtime) - layout._RUNTIME_GP) & 0xFFFFFFFF
            token = f"__CAMRY_GP_{index}__"
            staged.append((token, f"(camry_gp + 0x{offset:x}u)"))
            for address in (int(ghidra), int(runtime)):
                code = re.sub(
                    rf"(?i)\b0x0*{address:x}(?![0-9A-Fa-f])u?\b",
                    token,
                    code,
                )
        for token, replacement in staged:
            code = code.replace(token, replacement)
        return code
    code = _rewrite_addressed_macros(
        _apply_gp_pairs(code, pairs, (_GP_HITS or {}).get(name)), pairs,
    )
    return code


def _rewrite_system_inputs(code: str) -> str:
    """Restore system-register inputs and writes omitted by the decompiler."""
    code = rewrite_context._rewrite_exception_context(code)
    brace = syntax._opening_brace(code)
    if brace >= 0:
        code = code[:brace] + re.sub(
            r"\bICCTRL\b(?!\s*=(?!=))", "camry_sample_icctrl()", code[brace:],
        )
    if syntax._signature_name(syntax._c_signature(code)) == "load_u32":
        code = code.replace(
            "return *source;",
            "#ifdef CAMRY_HOST\n"
            "  if (!camry_peripheral_file)\n"
            "    return camry_read32(camry_host_addr(source));\n"
            "#endif\n"
            "  return *(const volatile uint32_t *)source;",
        )
    if syntax._signature_name(syntax._c_signature(code)) == "boot_hardware_ram_init_and_select_image":
        # 1426..1466 keeps the clear cursor in r30, incrementing its firmware
        # address by four. A host cursor crossing a mapped RAM window instead
        # becomes an unrelated alias when the loop compares its one-past value.
        ranges = iter((
            (0xFEBF7C00, 0xFEBE7000),
            (0xFEBE8000, 0xFEC00000),
            (0xFEEF8000, 0xFEF08000),
        ))

        def clear_loop(match: re.Match[str]) -> str:
            start, end = next(ranges)
            return (
                f"for (puVar1 = 0x{start:x}u; puVar1 < 0x{end:x}u; puVar1 += 4u)"
            )

        code = re.sub(
            r"for \(puVar1 = [^;]+;[^;]+; puVar1 = puVar1 \+ 1\)",
            clear_loop, code,
        )
        code = code.replace("undefined4 *puVar1;", "uint32_t puVar1;")
        code = code.replace("*puVar1 = 0;", "camry_write32(puVar1, 0);")
    code = re.sub(r"^[ \t]*uint in_PSW;[ \t]*\n", "", code, flags=re.M)
    code = re.sub(r"\bin_PSW\b", "camry_psw", code)
    if (
        syntax._signature_name(syntax._c_signature(code)) == "reset_context_and_startup"
        and "camry_gpr[3] = 0xfebe8000u;" not in code
    ):
        initial = [
            "  camry_gpr[1] = camry_gpr[2] = 0;",
            "  for (uint32_t reg = 6; reg < 32; ++reg) camry_gpr[reg] = 0;",
            "  camry_gpr[3] = 0xfebe8000u;",
            "  camry_gpr[4] = 0xfebf9800u;",
            "  camry_gpr[5] = 0x869cu;",
            "  camry_gpr_export_aliases();",
            "  camry_psw = 0x18020u;",
            *[
                f"  camry_SR[{selector}][{register}] = 0;"
                for selector, register in (
                    (0, 0), (0, 2), (0, 13), (0, 14), (0, 16), (0, 17),
                    (0, 20), (0, 28), (0, 29), (1, 4), (1, 11), (1, 12),
                    (2, 6), (2, 7), (2, 8), (5, 0),
                )
            ],
            "  camry_SR[0][1] = camry_SR[0][3] = 0x18020u;",
            "  camry_SR[1][0] = 0x20004u;",
            "  camry_SR[1][5] = 0x80000002u;",
        ]
        code = code[:brace + 1] + "\n" + "\n".join(initial) + code[brace + 1:]
    for name, (selector, register) in tree.SYSTEM_REGISTERS.items():
        code = re.sub(
            rf"^([ \t]*uint in_{name});[ \t]*$",
            rf"\1 = camry_SR[{selector}][{register}];",
            code,
            flags=re.M,
        )
        code = re.sub(rf"\b{name}\b", f"camry_SR[{selector}][{register}]", code)
    if syntax._signature_name(syntax._c_signature(code)) == "application_context_init":
        # 715B4..715DE initializes both register banks, including GP/TP/SP.
        code = (
            "void application_context_init(void)\n{\n"
            "  camry_SR[1][4] = 0x20200u;\n"
            "  camry_SR[1][3] = 0x20000u;\n"
            "  camry_gp = camry_gpr[4] = 0xfebeb800u;\n"
            "  camry_tp = camry_gpr[5] = 0x23dfcu;\n"
            "  camry_sp = camry_gpr[3] = 0xfebe2000u;\n"
            "  camry_gpr[11] = 0x20000u;\n"
            "  return;\n}\n"
        )
    if (
        syntax._signature_name(syntax._c_signature(code)) == "application_transfer_to_boot_context"
        and "camry_gp = camry_gpr[4] = 0xfebf9800u;" not in code
    ):
        # 9F22..9F5C resets the boot execution context before calling 148E.
        # In particular, boot helpers must not inherit the application GP.
        code = code.replace(
            "  boot_resident_enter_with_record(handoff_record);",
            "  camry_psw = 0x18020u;\n"
            "  camry_SR[1][4] = 0;\n"
            "  camry_sp = camry_gpr[3] = 0xfebe8000u;\n"
            "  camry_gp = camry_gpr[4] = 0xfebf9800u;\n"
            "  camry_tp = camry_gpr[5] = 0x869cu;\n"
            "  camry_SR[5][0] = 0;\n"
            "  boot_resident_enter_with_record(handoff_record);",
        )
    if (
        syntax._signature_name(syntax._c_signature(code)) == "application_transfer_to_boot_context"
        and "camry_gpr[31] = 0x9f62u;" not in code
    ):
        code = code.replace(
            "  boot_resident_enter_with_record(handoff_record);",
            "  camry_gpr[31] = 0x9f62u;\n"
            "  boot_resident_enter_with_record(handoff_record);",
        )
    if (
        syntax._signature_name(syntax._c_signature(code)) == "boot_resident_enter_with_record"
        and "camry_sp -= 4u;" not in code
    ):
        # 148E saves LP before either call. Its terminal 14A0 loop has no
        # DISPOSE: the frame remains live after the resident boot work.
        brace = syntax._opening_brace(code)
        code = code[:brace + 1] + (
            "\n  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);\n"
            "  camry_sp -= 4u;\n"
            "  camry_gpr[3] = camry_sp;"
        ) + code[brace + 1:]
        code = code.replace(
            "  copy_positive_count_words_forward_1478(",
            "  camry_gpr[31] = 0x149cu;\n  copy_positive_count_words_forward_1478(", 1,
        )
        code = code.replace(
            "  boot_resident_main();",
            "  camry_gpr[31] = 0x14a0u;\n  boot_resident_main();", 1,
        )
    if (
        syntax._signature_name(syntax._c_signature(code)) == "set_ebase_with_low_bit_one_preserving_irq_state_84f8"
        and re.search(r"camry_SR\[1\]\[3\]\s*=", code) is None
    ):
        # 84F8 tags EBASE with bit zero, then writes it before SYNCI on both paths.
        code = code.replace(
            "__synchronize();",
            "camry_SR[1][3] = param_1 | 1u;\n    __synchronize();",
        )
    if (
        syntax._signature_name(syntax._c_signature(code)) in {
            "clear_ecm_error_latches_once_or_terminate_7162e", "dispatch_ecm_status_exception_71ae4", "boot_eiint_context",
        }
        and "camry_SR[2][10] = in_ISPR;" not in code
    ):
        prefix = ""
        if syntax._signature_name(syntax._c_signature(code)) == "boot_eiint_context":
            prefix, separator, code = code.partition("  __disable_irq();")
            prefix = prefix.replace(
                "{", "{\n  uint camry_saved_eipc = camry_SR[0][0];", 1,
            )
            prefix += (
                separator + "\n  camry_SR[0][0] = camry_saved_eipc;"
                "\n  camry_SR[0][1] = in_EIPSW;"
            )
        # The exception epilogue pops ISPR. FPIPR clamping and EBASE selection
        # below it affect only decompiler temporaries.
        code = code.replace(
            "in_ISPR = in_ISPR & in_ISPR - 1;",
            "in_ISPR = in_ISPR & in_ISPR - 1;\n    camry_SR[2][10] = in_ISPR;",
        )
        # EIRET restores PSW before acknowledging a pending FPI. The vector
        # body must observe that restored context, then the EI-entry state.
        code = code.replace(
            "  if ((in_FPEC & 1) != 0) {",
            "  camry_psw = in_EIPSW;\n"
            "  camry_SR[2][12] &= ~2u;\n"
            "  if ((in_FPEC & 1) != 0) {\n"
            "    uint camry_fpi_priority = in_FPIPR & 31u;\n"
            "    if (camry_fpi_priority > 15u) camry_fpi_priority = 15u;\n"
            "    camry_SR[2][12] |= ((camry_pmr >> camry_fpi_priority) & 1u) << 1;",
        )
        code = re.sub(
            r"^([ \t]*)(?=\(\*\(code \*\)\(\(in_EBASE & 0xfffffe00\) \+ 0x70\)\))",
            r"\1camry_SR[0][11] = 0;\n"
            r"\1camry_SR[0][1] = camry_psw;\n"
            r"\1camry_SR[0][13] = 0x72;\n"
            r"\1camry_psw = (camry_psw & 0xbfffffffu) | 0x60u;\n\1",
            code, flags=re.M,
        )
        code = re.sub(
            r"\breturn\s*;",
            "camry_psw = camry_SR[0][1];\n    return;",
            code,
        )
        # 71ae4's early exit tail-transfers and leaves EIRET to its destination.
        code = code.replace(
            "clear_ecm_error_latches_once_or_terminate_7162e();\n    camry_psw = camry_SR[0][1];\n    return;",
            "clear_ecm_error_latches_once_or_terminate_7162e();\n    return;",
        )
        code = prefix + code
    return code
