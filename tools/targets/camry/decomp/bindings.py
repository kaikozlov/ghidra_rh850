"""Firmware-address call tables and gap-thunk translation units for native builds."""
from __future__ import annotations

from pathlib import Path
import re

from . import c_text, syntax, tree
from .declarations import _common_header


def _indirect_binding(name: str, signature: str) -> tuple[str, list[str]]:
    """Adapt C pointers at the firmware-word indirect-call boundary."""
    types = syntax._signature_param_types(signature)
    opening = signature.find("(")
    closing = signature.rfind(")")
    for index, part in enumerate(c_text._split_args(signature[opening + 1:closing])):
        array = re.search(r"((?:\s*\[\s*\d*\s*\])+)\s*$", part)
        if array is not None:
            element = syntax._param_type_list(part[:array.start()])[0]
            dimensions = re.findall(r"\[\s*\d*\s*\]", array.group(1))
            types[index] = (
                f"{element} *" if len(dimensions) == 1
                else f"{element} (*){''.join(dimensions[1:])}"
            )
    pointer_return = syntax._returns_pointer(signature)
    if not pointer_return and not any("*" in ctype for ctype in types):
        return name, []
    binding = f"camry_indirect_bind_{name}"
    result_type = "uint32_t" if pointer_return else syntax._return_type_of(signature, name)
    params: list[str] = []
    args: list[str] = []
    for index, ctype in enumerate(types, 1):
        arg = f"arg_{index}"
        if "*" in ctype:
            params.append(f"uint32_t {arg}")
            args.append(f"({ctype})camry_host_ptr({arg})")
        else:
            params.append(f"{ctype} {arg}")
            args.append(arg)
    call = f"{name}({', '.join(args)})"
    if pointer_return:
        statement = f"return camry_host_addr({call});"
    elif result_type == "void":
        statement = f"{call};"
    else:
        statement = f"return {call};"
    return binding, [
        f"static {result_type} {binding}({', '.join(params) or 'void'})",
        "{",
        f"    {statement}",
        "}",
    ]


def write_indirect_table(path: Path, sources: list[Path]) -> None:
    """Map linked addresses to bodies with a firmware-word pointer ABI."""
    addresses: dict[str, int] = {}
    for row in tree.load_symbols():
        addresses.setdefault(row["name"], int(row["addr"], 16))
    chosen: dict[int, tuple[str, str]] = {}
    for source in sources:
        for name, head in c_text._function_heads(source.read_text(encoding="utf-8")).items():
            addr = addresses.get(name)
            if addr is None or addr in chosen:
                continue
            chosen[addr] = name, syntax._c_signature(head)
    signatures = {name: signature for name, signature in chosen.values()}
    lines = _common_header(
        "\n".join(signatures.values()), signatures, types_only=True,
    ).splitlines()
    bindings: dict[int, str] = {}
    for addr, (name, signature) in sorted(chosen.items()):
        lines.append(signature + ";")
        binding, adapter = _indirect_binding(name, signature)
        bindings[addr] = binding
        lines.extend(adapter)
    lines.append("const camry_indirect_slot camry_indirect_slots[] = {")
    if not chosen:
        lines.append("    {0u, 0},")
    for addr in sorted(chosen):
        lines.append(f"    {{0x{addr:x}u, (void *){bindings[addr]}}},")
    lines.append("};")
    lines.append(f"const uint32_t camry_indirect_count = {len(chosen)}u;")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gap_thunks(path: Path) -> None:
    """Bodies for indirect calls that land between defined functions."""
    from .lifting.emit import emit_gap_thunks
    from .lifting.graph import gap_thunks, load_image
    thunks = sorted(gap_thunks(load_image(), tree.load_symbols()), key=lambda item: item.entry)
    lines = ['#include "host_cpu.h"', emit_gap_thunks(thunks), "const camry_indirect_slot camry_gap_slots[] = {"]
    if not thunks:
        lines.append("    {0u, 0},")
    for thunk in thunks:
        lines.append(f"    {{0x{thunk.entry:x}u, (void *){thunk.name}}},")
    lines.append("};")
    lines.append(f"const uint32_t camry_gap_count = {len(thunks)}u;")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
