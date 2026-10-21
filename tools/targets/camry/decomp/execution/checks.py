"""Retained-scenario comparison and observable native execution checks."""
from __future__ import annotations

import ctypes
import re

from ..tree import SYSTEM_REGISTERS
from .calls import POINTER_RETURN, VALUE_RETURN
from .memory import DCRA1_BASE, read_regions


def useful_oracle(scenario: dict) -> bool:
    if scenario.get("expected_fault"):
        return True
    checks = scenario.get("checks") or []
    has_r10 = any(
        check.get("kind") == "register" and check.get("register") == "r10"
        for check in checks
    )
    has_state = any(
        check.get("kind") == "register" and (
            check.get("register") in SYSTEM_REGISTERS
            or check.get("register") in ("PSW", "PMR", "CDBCR", "ICCTRL")
        ) for check in checks
    )
    has_memory = any(check.get("kind") == "memory" for check in checks)
    has_event = any(check.get("kind") == "event-count" for check in checks)
    if has_event and not has_r10:
        return False
    return has_memory or has_r10 or has_state


def check_call_sequence(library: ctypes.CDLL, scenario: dict) -> None:
    if "call_sequence" not in scenario:
        return
    from .native import _check_call_sequence

    _check_call_sequence(library, scenario)


def check_results(
    scenario: dict,
    name: str,
    image: bytearray | None,
    base: int,
    registers: dict,
    returned: int | None,
    regions: list[tuple[int, bytearray]] | None = None,
    codeflash: bytes | None = None,
    dcra: bytearray | None = None,
    value_return: bool | None = None,
) -> None:
    memory_checks = 0
    r10_checks = 0
    for check in scenario["checks"]:
        kind = check["kind"]
        if kind == "register":
            register = check["register"]
            expected = int(check["equals"], 16)
            if register == "PC":
                continue
            # C entry points expose only their return, memory, modeled system
            # state, and preserved registers. Incidental argument/scratch registers are excluded.
            if (
                value_return is not None
                and re.fullmatch(r"r\d+", register)
                and not re.fullmatch(r"r(?:2|2[0-9])", register)
            ):
                if register != "r10" or not value_return:
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
            r10_is_return = name in VALUE_RETURN if value_return is None else value_return
            if register == "r10" and r10_is_return:
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
        if kind not in {"memory", "memory-equal"}:
            continue
        memory_checks += 1
        address = int(check["address"], 16)
        size = check["size"]
        if dcra is not None and DCRA1_BASE <= address and address + size <= DCRA1_BASE + len(dcra):
            actual = bytes(dcra[address - DCRA1_BASE : address - DCRA1_BASE + size])
        elif regions is not None:
            try:
                actual = read_regions(regions, address, size)
            except AssertionError:
                # A store onto a return stub is checked against CodeFlash.
                # The scenario does not overlay that image with a fill window.
                if codeflash is None or address < 0 or address + size > len(codeflash):
                    raise
                actual = bytes(codeflash[address:address + size])
        elif (
            codeflash is not None
            and 0 <= address
            and address + size <= len(codeflash)
            and not (image is not None and base <= address and address + size <= base + len(image))
        ):
            actual = bytes(codeflash[address:address + size])
        else:
            actual = bytes(image[address - base : address - base + size])
        if kind == "memory-equal":
            source = int(check["source_address"], 16)
            if codeflash is not None and source + size <= len(codeflash):
                expected = codeflash[source : source + size]
            elif regions is not None:
                expected = read_regions(regions, source, size)
            else:
                expected = bytes(image[source - base : source - base + size])
        else:
            expected = bytes.fromhex(check["equals_hex"])
        if actual != expected:
            raise AssertionError(f"{scenario['name']}: {check['name']} mismatch")
    if memory_checks == 0 and r10_checks == 0 and not useful_oracle(scenario):
        raise AssertionError(f"{scenario['name']}: no observable state check")
