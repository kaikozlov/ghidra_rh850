"""Scenario address spaces, memory backing, and native model installation."""
from __future__ import annotations

import ctypes

from tools import REPO_ROOT
from tools.emulation.p1me_machine import _load_model
from tools.project.analysis_target import target as resolve_target

from ..tree import _machine_registers


MAX_SPAN = 2_000_000


MEMORY_MODEL, MEMORY_MODEL_SHA256 = _load_model()


MACHINE_REGISTERS = _machine_registers()


FLMD_RESETS = {
    int(row["address"]): int(row["reset"]).to_bytes(int(row["size"]), "little")
    for row in MACHINE_REGISTERS.values()
    if row.get("behavior") == "flmd"
}


DCRA1_BASE = 0xFFD51000


DCRA1_SIZE = 0x24


DCRA_CALLS = {
    "dcra1_crc_raw_words",
    "nvm_check_family2_rom_crc",
    "nvm_get_family2_rom_record",
    "nvm_refresh_family2_record_status",
    "nvm_step_acquisition_pass",
}


def _overlay_regions(
    regions: list[tuple[int, bytearray]], address: int, payload: bytearray,
) -> None:
    # Update owned storage rather than hiding a bank behind a second buffer.
    # In particular, both local-RAM views share this same bytearray.
    for base, data in reversed(regions):
        if covers(base, len(data), address, len(payload)):
            offset = address - base
            data[offset:offset + len(payload)] = payload
            return
    regions.append((address, payload))


def _memory_rows(regions: list[tuple[int, bytearray]], rows: list[dict]) -> None:
    for row in rows:
        address = int(row["address"], 16)
        if "hex" in row:
            payload = bytearray.fromhex(row["hex"])
        else:
            payload = bytearray([row["fill"] & 0xFF]) * row["size"]
        _overlay_regions(regions, address, payload)


def _model_regions(scenario: dict) -> list[tuple[int, bytearray]]:
    metadata = resolve_target("camry-8965F3307000")[1]
    regions = [(int(metadata["dataflash_base"], 16), bytearray(dataflash_view()))]
    aliases: dict[str, bytearray] = {}
    ram = [
        row for row in MEMORY_MODEL["manual"]["regions"]
        if row["executable"] and row["access"] == "rw"
    ]
    for row in ram:
        group = row.get("alias_group")
        if group and group in aliases:
            data = aliases[group]
        else:
            data = bytearray(row["size"])
            if group:
                aliases[group] = data
        regions.append((row["start"], data))

    # Page-local backing keeps typed C pointers and the snapshot reader on the
    # same storage without a giant buffer spanning unrelated peripheral banks.
    registers = MACHINE_REGISTERS
    pages: dict[int, bytearray] = {}
    for row in registers.values():
        if row.get("reset") is None:
            continue
        address, size = int(row["address"]), int(row["size"])
        page = address & ~0xFFF
        if page not in pages:
            pages[page] = bytearray(0x1000)
        offset = address - page
        pages[page][offset:offset + size] = int(row["reset"]).to_bytes(size, "little")
    regions.extend(sorted(pages.items()))
    _memory_rows(regions, scenario.get("pre_reset_memory", []))

    reset = scenario.get("reset", "none")
    if reset != "none":
        for row in ram:
            for rule in row.get("reset_rules", []):
                if rule["reset_class"] != reset:
                    continue
                control = registers[row["reset_control"]]
                address, size = int(control["address"]), int(control["size"])
                if rule["mode"] == "force":
                    _overlay_regions(regions, address, bytearray((3).to_bytes(size, "little")))
                elif int.from_bytes(read_regions(regions, address, size), "little") & 3 != 3:
                    continue
                _overlay_regions(regions, row["start"], bytearray(row["size"]))
    return regions


def scenario_regions(scenario: dict) -> list[tuple[int, bytearray]]:
    if not scenario.get("peripheral_file", False):
        regions = _model_regions(scenario)
        _memory_rows(regions, scenario.get("memory", []))
        return regions
    # Generated raw-peripheral cases deliberately retain their sparse fill
    # windows; model reset state must not replace that established mode.
    regions = []
    addresses = {
        int(row["address"], 16)
        for row in [*scenario.get("memory", []), *scenario.get("checks", [])]
        if "address" in row
    }
    if addresses & FLMD_RESETS.keys():
        regions.extend((address, bytearray(value)) for address, value in FLMD_RESETS.items())
    for row in scenario.get("memory", []):
        address = int(row["address"], 16)
        if "hex" in row:
            payload = bytearray.fromhex(row["hex"])
        else:
            payload = bytearray([row["fill"] & 0xFF]) * row["size"]
        regions.append((address, payload))
    return regions


def read_regions(regions: list[tuple[int, bytearray]], address: int, size: int) -> bytes:
    actual = bytearray(size)
    seen = bytearray(size)
    for base, data in regions:
        start = max(address, base)
        end = min(address + size, base + len(data))
        if start >= end:
            continue
        for cursor in range(start, end):
            actual[cursor - address] = data[cursor - base]
            seen[cursor - address] = 1
    if any(flag == 0 for flag in seen):
        raise AssertionError(f"address {address:#x} size {size} is outside the oracle regions")
    return bytes(actual)


def materialize(scenario: dict) -> tuple[bytearray, int] | None:
    if not scenario.get("peripheral_file", False):
        # Flattening banks would lose alias identity and map the intervening
        # address holes. Keep model-backed state in its declared local regions.
        return None
    cells: dict[int, int] = {}
    for address, payload in scenario_regions(scenario):
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


def pointer(library: ctypes.CDLL, address: int, kind: type):
    if address == 0:
        return kind()
    return ctypes.cast(library.camry_host_ptr(address & 0xFFFFFFFF), kind)


def covers(base: int, size: int, address: int, length: int) -> bool:
    if length == 0:
        return True
    offset = address - base
    return 0 <= offset and offset + length <= size


_DATAFLASH_BYTES: bytes | None = None


_DATAFLASH_VIEW = None


def dataflash_view():
    global _DATAFLASH_BYTES, _DATAFLASH_VIEW
    if _DATAFLASH_BYTES is None:
        metadata = resolve_target("camry-8965F3307000")[1]
        _DATAFLASH_BYTES = (REPO_ROOT / metadata["dataflash"]).read_bytes()
    # FACI may modify this backing. Each scenario starts from the registered
    # nonvolatile image, not a preceding native call's mutable view.
    _DATAFLASH_VIEW = view_of(bytearray(_DATAFLASH_BYTES))
    return _DATAFLASH_VIEW


def install_dataflash(library: ctypes.CDLL) -> None:
    metadata = resolve_target("camry-8965F3307000")[1]
    u8p = ctypes.POINTER(ctypes.c_uint8)
    library.camry_host_add(
        int(metadata["dataflash_base"], 16),
        ctypes.cast(dataflash_view(), u8p),
        len(_DATAFLASH_BYTES),
    )


def install_address_space(library: ctypes.CDLL, code_view, code_size: int, view, base: int, memory: bytearray) -> None:
    u8p = ctypes.POINTER(ctypes.c_uint8)
    library._camry_model_configured = False
    library.camry_host_reset()
    library.camry_host_add(0, ctypes.cast(code_view, u8p), code_size)
    install_dataflash(library)
    if memory:
        library.camry_host_add(base & 0xFFFFFFFF, ctypes.cast(view, u8p), len(memory))
    library._camry_memory_views = [code_view, _DATAFLASH_VIEW, view]


def install_regions(library: ctypes.CDLL, code_view, code_size: int, regions: list[tuple[int, bytearray]]) -> list:
    u8p = ctypes.POINTER(ctypes.c_uint8)
    views = [code_view]
    library._camry_model_configured = False
    library.camry_host_reset()
    library.camry_host_add(0, ctypes.cast(code_view, u8p), code_size)
    install_dataflash(library)
    views.append(_DATAFLASH_VIEW)
    for base, data in regions:
        view = view_of(data)
        views.append(view)
        library.camry_host_add(base & 0xFFFFFFFF, ctypes.cast(view, u8p), len(data))
    # ctypes argument conversion does not retain pointers after camry_host_add.
    # Keep every backing alive even when the caller does not retain our return.
    library._camry_memory_views = views
    return views


def configure_native_model(library: ctypes.CDLL, scenario: dict | None) -> None:
    if scenario is None or scenario.get("peripheral_file", False):
        return
    if getattr(library, "_camry_model_configured", False):
        return
    u32 = ctypes.c_uint32
    library.camry_host_add_register.argtypes = [u32, u32, u32, u32, u32]
    library.camry_host_add_register.restype = None
    rows = [*scenario.get("pre_reset_memory", []), *scenario.get("memory", [])]
    for register in MACHINE_REGISTERS.values():
        address, size = int(register["address"]), int(register["size"])
        initialized = (1 << size) - 1 if register.get("reset") is not None else 0
        for row in rows:
            start = int(row["address"], 16)
            length = len(bytes.fromhex(row["hex"])) if "hex" in row else row["size"]
            for offset in range(size):
                if start <= address + offset < start + length:
                    initialized |= 1 << offset
        widths = sum(1 << width for width in register["access_widths"])
        access = (1 if "r" in register["access"] else 0) | (2 if "w" in register["access"] else 0)
        library.camry_host_add_register(address, size, widths, access, initialized)
    library._camry_model_configured = True


def attach_dcra_window(library: ctypes.CDLL):
    window = bytearray(DCRA1_SIZE)
    view = view_of(window)
    library.camry_host_add(
        DCRA1_BASE,
        ctypes.cast(view, ctypes.POINTER(ctypes.c_uint8)),
        DCRA1_SIZE,
    )
    return window, view


def attach_dcra(library: ctypes.CDLL, name: str):
    if name not in DCRA_CALLS:
        return None, None
    return attach_dcra_window(library)


