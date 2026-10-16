#!/usr/bin/env python3
"""Camry identity link, and equivalent C checked against retained original-byte oracles."""
from __future__ import annotations

import ctypes
import json
import subprocess
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.camry_decomp import ROOT, identity_image, load_matched, load_symbols
from tools.project.analysis_target import target as resolve_target

ORACLES = ROOT / "oracles.jsonl"
INCLUDE = ROOT / "include"
SOURCES = sorted((ROOT / "src").glob("*.c"))
MAX_SPAN = 2_000_000

# r10 is the C return value. memcpy returns the destination pointer.
POINTER_RETURN = {"f33_memcpy_forward"}
VALUE_RETURN = {
    "f33_update_whole_words",
    "f33_load_u8",
    "f33_load_u16",
    "f33_nvm_sum_bytes",
    "f33_nvm_family0_chunk_cost",
    "f33_scale_u16_delta_s16_x4",
    "f33_nvm_payload_length",
    "f33_nvm_base_offset",
    "f33_nvm_payload_page_count",
    "f33_nvm_trailer_offset",
    "f33_nvm_storage_handle",
    "f33_nvm_advance_family0_request_index",
    "f33_nvm_advance_family1_request_index",
}

ROM_TABLES = (
    ("f33_nvm_descriptors", 0x27634, 123 * 6),
    ("f33_nvm_logical_descriptors", 0x26C0C, 124 * 16),
)
ROM_BYTES = (
    ("f33_nvm_family0_request_cell_count", 0x2AD8A),
    ("f33_nvm_family1_request_cell_count", 0x2AD8B),
)


def load_oracles() -> list[dict]:
    rows = []
    with ORACLES.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def compile_sources(directory: Path) -> ctypes.CDLL:
    library = directory / "libcamry.dylib"
    subprocess.run(
        [
            "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(INCLUDE),
            "-dynamiclib", "-o", str(library),
            *[str(path) for path in SOURCES],
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return ctypes.CDLL(library)


def bind(library: ctypes.CDLL) -> None:
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32p = ctypes.POINTER(ctypes.c_uint32)
    u32 = ctypes.c_uint32
    library.f33_memcpy_forward.argtypes = [u8p, u8p, u32]
    library.f33_memcpy_forward.restype = u8p
    library.f33_memzero.argtypes = [u8p, u32]
    library.f33_memzero.restype = None
    library.f33_copy_whole_words.argtypes = [u32p, u32p, ctypes.c_uint16]
    library.f33_copy_whole_words.restype = None
    library.f33_update_whole_words.argtypes = [u32p, u32p, ctypes.c_uint16]
    library.f33_update_whole_words.restype = u32
    library.f33_load_u8.argtypes = [u8p]
    library.f33_load_u8.restype = u32
    library.f33_load_u16.argtypes = [u8p]
    library.f33_load_u16.restype = u32
    library.f33_store_u8.argtypes = [u8p, u32]
    library.f33_store_u8.restype = None
    library.f33_store_u16.argtypes = [u8p, u32]
    library.f33_store_u16.restype = None
    library.f33_store_u32.argtypes = [u8p, u32]
    library.f33_store_u32.restype = None
    library.f33_nvm_sum_bytes.argtypes = [u32, u8p]
    library.f33_nvm_sum_bytes.restype = u32
    library.f33_nvm_family0_chunk_cost.argtypes = [u32]
    library.f33_nvm_family0_chunk_cost.restype = u32
    library.f33_scale_u16_delta_s16_x4.argtypes = [u32, u32, u32]
    library.f33_scale_u16_delta_s16_x4.restype = u32
    for name in (
        "f33_nvm_payload_length",
        "f33_nvm_base_offset",
        "f33_nvm_payload_page_count",
        "f33_nvm_trailer_offset",
        "f33_nvm_storage_handle",
        "f33_nvm_advance_family0_request_index",
        "f33_nvm_advance_family1_request_index",
    ):
        getattr(library, name).argtypes = [u32]
        getattr(library, name).restype = u32


def materialize(scenario: dict) -> tuple[bytearray, int] | None:
    cells: dict[int, int] = {}
    for row in scenario.get("memory", []):
        address = int(row["address"], 16)
        if "hex" in row:
            payload = bytes.fromhex(row["hex"])
        else:
            payload = bytes([row["fill"] & 0xFF]) * row["size"]
        for offset, byte in enumerate(payload):
            cells[address + offset] = byte
    if not cells:
        return bytearray(), 0
    start = min(cells)
    end = max(cells)
    if end - start + 1 > MAX_SPAN:
        return None
    image = bytearray(b"\x00" * (end - start + 1))
    for address, byte in cells.items():
        image[address - start] = byte
    return image, start


def view_of(image: bytearray) -> ctypes.Array:
    return (ctypes.c_uint8 * len(image)).from_buffer(image)


def pointer(view: ctypes.Array, base: int, address: int, kind: type):
    offset = address - base
    if offset < 0 or offset >= len(view):
        raise AssertionError(f"address {address:#x} is outside the mapped oracle memory")
    return ctypes.cast(ctypes.addressof(view) + offset, kind)


def covers(base: int, size: int, address: int, length: int) -> bool:
    if length == 0:
        return True
    offset = address - base
    return 0 <= offset and offset + length <= size


def useful_oracle(scenario: dict) -> bool:
    checks = scenario.get("checks") or []
    if any(check.get("kind") == "event-count" for check in checks):
        return False
    return any(
        check.get("kind") == "memory"
        or (check.get("kind") == "register" and check.get("register") == "r10")
        for check in checks
    )


def accessed_ranges(name: str, registers: dict) -> list[tuple[int, int]]:
    r6 = int(registers.get("r6", "0"), 16)
    r7 = int(registers.get("r7", "0"), 16)
    r8 = int(registers.get("r8", "0"), 16)
    if name == "f33_load_u8" or name == "f33_store_u8":
        return [(r6, 1)]
    if name == "f33_load_u16" or name == "f33_store_u16":
        return [(r6, 2)]
    if name == "f33_store_u32":
        return [(r6, 4)]
    if name == "f33_nvm_sum_bytes":
        return [(r7, r6 & 0xFFFF)]
    if name == "f33_memcpy_forward":
        return [(r6, r8), (r7, r8)]
    if name == "f33_memzero":
        return [(r6, r7)]
    if name in {"f33_copy_whole_words", "f33_update_whole_words"}:
        words = (r8 & 0xFFFF) & ~3
        return [(r6, words), (r7, words)]
    return []


def call_function(library: ctypes.CDLL, name: str, view, base: int, registers: dict) -> int | None:
    r6 = int(registers.get("r6", "0"), 16)
    r7 = int(registers.get("r7", "0"), 16)
    r8 = int(registers.get("r8", "0"), 16)
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32p = ctypes.POINTER(ctypes.c_uint32)
    if name == "f33_memcpy_forward":
        dest_ptr = pointer(view, base, r6, u8p)
        result = library.f33_memcpy_forward(dest_ptr, pointer(view, base, r7, u8p), r8)
        return int(
            ctypes.cast(result, ctypes.c_void_p).value
            == ctypes.cast(dest_ptr, ctypes.c_void_p).value
        )
    if name == "f33_memzero":
        library.f33_memzero(pointer(view, base, r6, u8p), r7)
        return None
    if name == "f33_copy_whole_words":
        library.f33_copy_whole_words(
            pointer(view, base, r6, u32p),
            pointer(view, base, r7, u32p),
            r8 & 0xFFFF,
        )
        return None
    if name == "f33_update_whole_words":
        return int(library.f33_update_whole_words(
            pointer(view, base, r6, u32p),
            pointer(view, base, r7, u32p),
            r8 & 0xFFFF,
        ))
    if name == "f33_load_u8":
        return int(library.f33_load_u8(pointer(view, base, r6, u8p)))
    if name == "f33_load_u16":
        return int(library.f33_load_u16(pointer(view, base, r6, u8p)))
    if name == "f33_store_u8":
        library.f33_store_u8(pointer(view, base, r6, u8p), r7)
        return None
    if name == "f33_store_u16":
        library.f33_store_u16(pointer(view, base, r6, u8p), r7)
        return None
    if name == "f33_store_u32":
        library.f33_store_u32(pointer(view, base, r6, u8p), r7)
        return None
    if name == "f33_nvm_sum_bytes":
        source = pointer(view, base, r7, u8p) if (r6 & 0xFFFF) else None
        return int(library.f33_nvm_sum_bytes(r6, source))
    if name == "f33_nvm_family0_chunk_cost":
        return int(library.f33_nvm_family0_chunk_cost(r6))
    if name == "f33_scale_u16_delta_s16_x4":
        return int(library.f33_scale_u16_delta_s16_x4(r6, r7, r8)) & 0xFFFFFFFF
    if name in VALUE_RETURN:
        return int(getattr(library, name)(r6)) & 0xFFFFFFFF
    raise AssertionError(f"no C call for {name}")


def check_results(scenario: dict, name: str, image: bytearray, base: int, registers: dict, returned: int | None) -> None:
    memory_checks = 0
    r10_checks = 0
    for check in scenario["checks"]:
        kind = check["kind"]
        if kind == "register":
            register = check["register"]
            expected = int(check["equals"], 16)
            if register == "sp":
                continue
            if register == "r10" and name in POINTER_RETURN:
                r10_checks += 1
                destination = int(registers["r6"], 16)
                if expected == destination:
                    if returned != 1:
                        raise AssertionError(f"{scenario['name']}: memcpy did not return destination")
                elif expected <= 0xFFFF and returned != expected:
                    raise AssertionError(f"{scenario['name']}: r10 {returned} != {expected:#x}")
                continue
            if register == "r10" and name in VALUE_RETURN:
                r10_checks += 1
                if returned != expected:
                    raise AssertionError(f"{scenario['name']}: r10 {returned:#x} != {expected:#x}")
                continue
            actual = int(registers.get(register, "0"), 16)
            if actual != expected:
                raise AssertionError(
                    f"{scenario['name']}: preserved {register} {actual:#x} != {expected:#x}"
                )
            continue
        if kind != "memory":
            continue
        memory_checks += 1
        address = int(check["address"], 16)
        size = check["size"]
        expected = bytes.fromhex(check["equals_hex"])
        actual = bytes(image[address - base : address - base + size])
        if actual != expected:
            raise AssertionError(f"{scenario['name']}: {check['name']} mismatch")
    if memory_checks == 0 and r10_checks == 0:
        raise AssertionError(f"{scenario['name']}: no memory or r10 check")


def check_rom(library: ctypes.CDLL) -> None:
    metadata = resolve_target("camry-8965F3307000")[1]
    image = (REPO_ROOT / metadata["codeflash"]).read_bytes()
    for name, address, size in ROM_TABLES:
        actual = bytes((ctypes.c_uint8 * size).in_dll(library, name))
        if actual != image[address : address + size]:
            raise SystemExit(f"{name} drifted from CodeFlash {address:#x}")
    for name, address in ROM_BYTES:
        actual = ctypes.c_uint8.in_dll(library, name).value
        if actual != image[address]:
            raise SystemExit(f"{name} drifted from CodeFlash {address:#x}")


def main() -> int:
    image, report = identity_image(load_symbols())
    if hashlib_matches(image, report):
        print(
            f"PASS identity: {report['functions']} functions, "
            f"{report['function_bytes']} function bytes, "
            f"{report['gap_bytes']} gap bytes"
        )
    matched = {int(row["addr"], 16): row for row in load_matched()}
    symbol_names = {int(row["addr"], 16): row["name"] for row in load_symbols()}
    for address, row in matched.items():
        if symbol_names.get(address) != row["name"]:
            raise SystemExit(f"matched name drift at {row['addr']}")
        if row["status"] not in {"equivalent", "byte-matched"}:
            raise SystemExit(f"unknown match status {row['status']}")
    executed = {address: 0 for address in matched}
    with tempfile.TemporaryDirectory(prefix="camry-decomp-") as directory:
        library = compile_sources(Path(directory))
        bind(library)
        check_rom(library)
        print("PASS rom tables match CodeFlash")
        for scenario in load_oracles():
            entry = scenario.get("entry", {})
            if entry.get("scope") != "resolved-address":
                continue
            address = int(entry["address"], 16)
            if address not in matched or not useful_oracle(scenario):
                continue
            name = matched[address]["name"]
            mapped = materialize(scenario)
            if mapped is None:
                continue
            memory, base = mapped
            ranges = accessed_ranges(name, scenario.get("registers", {}))
            if any(not covers(base, len(memory), start, length) for start, length in ranges):
                continue
            view = view_of(memory) if memory else view_of(bytearray(b"\x00"))
            returned = call_function(library, name, view, base, scenario.get("registers", {}))
            check_results(scenario, name, memory, base, scenario.get("registers", {}), returned)
            executed[address] += 1
            print(f"PASS {name} {scenario['name']}")
    missing = [row["name"] for address, row in matched.items() if executed[address] == 0]
    if missing:
        raise SystemExit("matched functions with no executed oracle: " + ", ".join(missing))
    print(f"PASS matched functions: {len(matched)}")
    return 0


def hashlib_matches(image: bytes, report: dict) -> bool:
    import hashlib
    if hashlib.sha256(image).hexdigest() != report["codeflash_sha256"]:
        raise SystemExit("identity image hash drift")
    return True


if __name__ == "__main__":
    raise SystemExit(main())
