#!/usr/bin/env python3
"""Build and execute modeled RH850 CodeFlash images at their real addresses."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA = "rh850-codeflash-sim-v1"
SIMULATION_PROOF_BOUNDARY = {
    "observed": "modeled CPU execution along the exercised path",
    "hardware_validated": False,
    "unverified": [
        "diagnostic upload and trigger",
        "live RAM retention and MPU state",
        "interrupts, watchdogs, and peripherals",
        "hardware-service permission and timing",
        "vehicle behavior",
    ],
}
_SECTION_RE = re.compile(r"\.[A-Za-z0-9_.-]+\Z")


class CodeFlashSimError(RuntimeError):
    pass


@dataclass(frozen=True)
class Overlay:
    section: str
    address: int
    expected: bytes


@dataclass(frozen=True)
class LoadSlot:
    address: int
    max_size: int
    accepted_sha256: frozenset[str]


@dataclass(frozen=True)
class Scenario:
    name: str
    codeflash_size: int
    accepted_image_sha256: frozenset[str]
    assembly: Path
    harness_address: int
    harness_size_limit: int
    entry_symbol: str
    stop_symbol: str | None
    memory_regions: tuple[str, ...]
    gdb_setup: tuple[str, ...]
    gdb_execution: tuple[str, ...]
    gdb_results: tuple[str, ...]
    overlays: tuple[Overlay, ...]
    loads: tuple[LoadSlot, ...]


@dataclass(frozen=True)
class SimulationResult:
    output: str
    input_sha256: str
    modeled_sha256: str
    elf: Path | None


def _integer(value: object, field: str) -> int:
    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        try:
            result = int(value, 0)
        except ValueError as exc:
            raise CodeFlashSimError(f"{field} is not an integer: {value!r}") from exc
    else:
        raise CodeFlashSimError(f"{field} is not an integer")
    if not 0 <= result <= 0xFFFFFFFF:
        raise CodeFlashSimError(f"{field} is outside the 32-bit address space")
    return result


def _repo_path(root: Path, value: object, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise CodeFlashSimError(f"{field} must be a repository-relative path")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise CodeFlashSimError(f"{field} escapes the repository: {value}") from exc
    if not path.is_file():
        raise CodeFlashSimError(f"{field} does not exist: {value}")
    return path


def _strings(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise CodeFlashSimError(f"{field} must be a list of non-empty strings")
    return tuple(value)


def _digests(value: object, field: str) -> frozenset[str]:
    if not isinstance(value, list) or not value:
        raise CodeFlashSimError(f"{field} must contain at least one digest")
    accepted: set[str] = set()
    for digest in value:
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise CodeFlashSimError(f"{field} contains an invalid digest")
        accepted.add(digest)
    return frozenset(accepted)


def load_scenario(root: Path, path: Path) -> Scenario:
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CodeFlashSimError(f"cannot load scenario {path}: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema") != SCHEMA:
        raise CodeFlashSimError(f"scenario schema must be {SCHEMA!r}")

    accepted = _digests(raw.get("accepted_image_sha256"), "accepted_image_sha256")

    overlay_rows = raw.get("overlays", [])
    if not isinstance(overlay_rows, list):
        raise CodeFlashSimError("overlays must be a list")
    overlays: list[Overlay] = []
    for index, row in enumerate(overlay_rows):
        if not isinstance(row, dict):
            raise CodeFlashSimError(f"overlays[{index}] must be an object")
        section = row.get("section")
        if not isinstance(section, str) or _SECTION_RE.fullmatch(section) is None:
            raise CodeFlashSimError(f"overlays[{index}].section is invalid")
        expected_hex = row.get("expected")
        if not isinstance(expected_hex, str):
            raise CodeFlashSimError(f"overlays[{index}].expected must be hexadecimal")
        try:
            expected = bytes.fromhex(expected_hex)
        except ValueError as exc:
            raise CodeFlashSimError(f"overlays[{index}].expected is invalid hexadecimal") from exc
        if not expected:
            raise CodeFlashSimError(f"overlays[{index}].expected cannot be empty")
        overlays.append(Overlay(
            section=section,
            address=_integer(row.get("address"), f"overlays[{index}].address"),
            expected=expected,
        ))

    load_rows = raw.get("loads", [])
    if not isinstance(load_rows, list):
        raise CodeFlashSimError("loads must be a list")
    loads: list[LoadSlot] = []
    load_addresses: set[int] = set()
    for index, row in enumerate(load_rows):
        if not isinstance(row, dict):
            raise CodeFlashSimError(f"loads[{index}] must be an object")
        address = _integer(row.get("address"), f"loads[{index}].address")
        if address in load_addresses:
            raise CodeFlashSimError(f"duplicate load address 0x{address:08X}")
        load_addresses.add(address)
        max_size = _integer(row.get("max_size"), f"loads[{index}].max_size")
        if max_size == 0:
            raise CodeFlashSimError(f"loads[{index}].max_size cannot be zero")
        loads.append(LoadSlot(
            address=address,
            max_size=max_size,
            accepted_sha256=_digests(
                row.get("accepted_sha256"),
                f"loads[{index}].accepted_sha256",
            ),
        ))

    name = raw.get("name")
    entry_symbol = raw.get("entry_symbol")
    for field, value in (("name", name), ("entry_symbol", entry_symbol)):
        if not isinstance(value, str) or not value:
            raise CodeFlashSimError(f"{field} must be a non-empty string")
    gdb_execution = _strings(raw.get("gdb_execution", []), "gdb_execution")
    stop_symbol = raw.get("stop_symbol")
    if stop_symbol is not None and (not isinstance(stop_symbol, str) or not stop_symbol):
        raise CodeFlashSimError("stop_symbol must be a non-empty string")
    if not gdb_execution and stop_symbol is None:
        raise CodeFlashSimError("scenario requires stop_symbol or gdb_execution")

    return Scenario(
        name=name,
        codeflash_size=_integer(raw.get("codeflash_size"), "codeflash_size"),
        accepted_image_sha256=accepted,
        assembly=_repo_path(root, raw.get("assembly"), "assembly"),
        harness_address=_integer(raw.get("harness_address"), "harness_address"),
        harness_size_limit=_integer(
            raw.get("harness_size_limit", 0x1000),
            "harness_size_limit",
        ),
        entry_symbol=entry_symbol,
        stop_symbol=stop_symbol,
        memory_regions=_strings(raw.get("memory_regions"), "memory_regions"),
        gdb_setup=_strings(raw.get("gdb_setup"), "gdb_setup"),
        gdb_execution=gdb_execution,
        gdb_results=_strings(raw.get("gdb_results"), "gdb_results"),
        overlays=tuple(overlays),
        loads=tuple(loads),
    )


def _run_tool(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [str(root / "tools" / "rh850"), *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        command = " ".join(args)
        raise CodeFlashSimError(
            f"tools/rh850 {command} failed ({proc.returncode})\n{proc.stdout}{proc.stderr}"
        )
    return proc


def _compile_scenario(root: Path, work: Path, scenario: Scenario) -> None:
    source = scenario.assembly.relative_to(root).as_posix()
    _run_tool(root, (
        "exec", "--work-dir", str(work),
        "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-ffreestanding",
        "-fno-builtin", "-Os", "-nostdlib", "-Wa,-mv850e3v5,-mextension",
        "-c", f"/src/{source}", "-o", "/out/scenario.o",
    ))
    _run_tool(root, (
        "exec", "--work-dir", str(work), "v850-elf-objcopy",
        "--dump-section", ".sim.harness=/out/harness.bin",
        "/out/scenario.o",
    ))
    for index, overlay in enumerate(scenario.overlays):
        _run_tool(root, (
            "exec", "--work-dir", str(work), "v850-elf-objcopy",
            "--dump-section", f"{overlay.section}=/out/overlay-{index}.bin",
            "/out/scenario.o",
        ))


def _apply_overlays(image: bytes, work: Path, scenario: Scenario) -> tuple[bytes, list[dict[str, object]]]:
    modeled = bytearray(image)
    occupied: list[tuple[int, int]] = []
    audit: list[dict[str, object]] = []
    for index, overlay in enumerate(scenario.overlays):
        replacement = (work / f"overlay-{index}.bin").read_bytes()
        if len(replacement) != len(overlay.expected):
            raise CodeFlashSimError(
                f"overlay {overlay.section} is {len(replacement)} bytes; expected {len(overlay.expected)}"
            )
        end = overlay.address + len(replacement)
        if end > len(modeled):
            raise CodeFlashSimError(f"overlay {overlay.section} escapes CodeFlash")
        if any(overlay.address < old_end and old_start < end for old_start, old_end in occupied):
            raise CodeFlashSimError(f"overlay {overlay.section} overlaps another overlay")
        observed = bytes(modeled[overlay.address:end])
        if observed != overlay.expected:
            raise CodeFlashSimError(
                f"overlay {overlay.section} preimage mismatch at 0x{overlay.address:08X}: "
                f"expected {overlay.expected.hex()}, got {observed.hex()}"
            )
        modeled[overlay.address:end] = replacement
        occupied.append((overlay.address, end))
        audit.append({
            "section": overlay.section,
            "address": f"0x{overlay.address:08X}",
            "original": overlay.expected.hex(),
            "replacement": replacement.hex(),
        })
    return bytes(modeled), audit


def _overlaps(start: int, end: int, other_start: int, other_end: int) -> bool:
    return start < other_end and other_start < end


def _prepare_loads(
    root: Path,
    work: Path,
    scenario: Scenario,
    load_paths: dict[int, Path],
) -> list[dict[str, object]]:
    required = {slot.address for slot in scenario.loads}
    supplied = set(load_paths)
    if supplied != required:
        missing = [f"0x{address:08X}" for address in sorted(required - supplied)]
        unexpected = [f"0x{address:08X}" for address in sorted(supplied - required)]
        raise CodeFlashSimError(
            f"RAM loads do not match scenario: missing={missing}, unexpected={unexpected}"
        )

    harness_size = (work / "harness.bin").stat().st_size
    if harness_size == 0 or harness_size > scenario.harness_size_limit:
        raise CodeFlashSimError(
            f"harness size {harness_size} exceeds limit {scenario.harness_size_limit}"
        )
    harness_end = scenario.harness_address + scenario.harness_size_limit
    if harness_end > 0x100000000:
        raise CodeFlashSimError("harness range wraps the address space")

    occupied: list[tuple[int, int, str]] = [
        (0, scenario.codeflash_size, "CodeFlash"),
        (scenario.harness_address, harness_end, "harness"),
    ]
    audit: list[dict[str, object]] = []
    for index, slot in enumerate(scenario.loads):
        path = load_paths[slot.address]
        try:
            blob = path.read_bytes()
        except OSError as exc:
            raise CodeFlashSimError(
                f"cannot read RAM load at 0x{slot.address:08X}: {exc}"
            ) from exc
        if not blob or len(blob) > slot.max_size:
            raise CodeFlashSimError(
                f"RAM load at 0x{slot.address:08X} size {len(blob)} "
                f"is outside 1..{slot.max_size}"
            )
        digest = hashlib.sha256(blob).hexdigest()
        if digest not in slot.accepted_sha256:
            raise CodeFlashSimError(
                f"RAM load at 0x{slot.address:08X} rejects SHA-256 {digest}"
            )
        end = slot.address + len(blob)
        if end > 0x100000000:
            raise CodeFlashSimError(
                f"RAM load at 0x{slot.address:08X} wraps the address space"
            )
        for old_start, old_end, old_name in occupied:
            if _overlaps(slot.address, end, old_start, old_end):
                raise CodeFlashSimError(
                    f"RAM load at 0x{slot.address:08X} overlaps {old_name} "
                    f"at 0x{slot.address:08X}..0x{end:08X}"
                )
        occupied.append((slot.address, end, f"RAM load 0x{slot.address:08X}"))
        binary = work / f"load-{index}.bin"
        binary.write_bytes(blob)
        section = f".sim.load.{index}"
        _run_tool(root, (
            "exec", "--work-dir", str(work), "v850-elf-objcopy",
            "-I", "binary", "-O", "elf32-v850-rh850", "-B", "v850:rh850",
            "--rename-section", f".data={section},alloc,load,code,contents",
            f"/out/{binary.name}", f"/out/load-{index}.o",
        ))
        audit.append({
            "path": str(path),
            "address": f"0x{slot.address:08X}",
            "size": len(blob),
            "sha256": digest,
        })
    return audit


def _link_model(root: Path, work: Path, scenario: Scenario) -> Path:
    linker = work / "scenario.ld"
    lines = [
        "SECTIONS {",
        "  .codeflash 0x00000000 : { *(.codeflash) }",
        f"  .sim_harness 0x{scenario.harness_address:08X} : {{ *(.sim.harness) }}",
    ]
    for index, slot in enumerate(scenario.loads):
        lines.append(
            f"  .sim_load_{index} 0x{slot.address:08X} : {{ *(.sim.load.{index}) }}"
        )
    lines.extend([
        "  /DISCARD/ : { *(.sim.overlay.*) }",
        "}",
        f"ENTRY({scenario.entry_symbol})",
        "",
    ])
    linker.write_text("\n".join(lines), encoding="utf-8")
    _run_tool(root, (
        "exec", "--work-dir", str(work), "v850-elf-objcopy",
        "-I", "binary", "-O", "elf32-v850-rh850", "-B", "v850:rh850",
        "--rename-section", ".data=.codeflash,alloc,load,readonly,code,contents",
        "/out/model.bin", "/out/model.o",
    ))
    objects = ["/out/scenario.o", "/out/model.o"]
    objects.extend(f"/out/load-{index}.o" for index in range(len(scenario.loads)))
    _run_tool(root, (
        "exec", "--work-dir", str(work), "v850-elf-gcc", "-nostdlib",
        "-Wl,--no-warn-mismatch", "-Wl,-T,/out/scenario.ld", "-Wl,--build-id=none",
        *objects, "-o", "/out/scenario.elf",
    ))
    return work / "scenario.elf"


def _execute(
    root: Path,
    elf: Path,
    scenario: Scenario,
    *,
    extra_memory_regions: Sequence[str] = (),
    gdb_commands: Sequence[str] = (),
) -> str:
    args: list[str] = ["sim", str(elf)]
    for region in (*scenario.memory_regions, *extra_memory_regions):
        args += ["--memory-region", region]
    for command in scenario.gdb_setup:
        args += ["-ex", command]
    if gdb_commands:
        for command in gdb_commands:
            args += ["-ex", command]
    elif scenario.gdb_execution:
        for command in scenario.gdb_execution:
            args += ["-ex", command]
    else:
        assert scenario.stop_symbol is not None
        args += ["-ex", f"break {scenario.stop_symbol}", "-ex", "run"]
    for command in scenario.gdb_results:
        args += ["-ex", command]
    proc = _run_tool(root, args)
    return proc.stdout + proc.stderr


def run_scenario(
    *,
    root: Path,
    image_path: Path,
    scenario_path: Path,
    output_dir: Path | None = None,
    expected_output: Sequence[str] = (),
    load_paths: dict[int, Path] | None = None,
    extra_memory_regions: Sequence[str] = (),
    gdb_commands: Sequence[str] = (),
) -> SimulationResult:
    root = root.resolve()
    image_path = image_path.resolve()
    scenario_path = scenario_path.resolve()
    scenario = load_scenario(root, scenario_path)
    resolved_loads = {
        address: (path if path.is_absolute() else root / path).resolve()
        for address, path in (load_paths or {}).items()
    }
    image = image_path.read_bytes()
    if len(image) != scenario.codeflash_size:
        raise CodeFlashSimError(
            f"CodeFlash size mismatch: expected 0x{scenario.codeflash_size:X}, got 0x{len(image):X}"
        )
    input_sha = hashlib.sha256(image).hexdigest()
    if input_sha not in scenario.accepted_image_sha256:
        raise CodeFlashSimError(f"scenario {scenario.name!r} rejects image SHA-256 {input_sha}")

    tmp_parent = root / "build" / "tmp"
    tmp_parent.mkdir(parents=True, exist_ok=True)
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if output_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="rh850-codeflash-", dir=tmp_parent)
        work = Path(temporary.name)
    else:
        work = output_dir.resolve()
        try:
            work.relative_to(root)
        except ValueError as exc:
            raise CodeFlashSimError("output directory must be inside the repository") from exc
        work.mkdir(parents=True, exist_ok=True)

    try:
        _compile_scenario(root, work, scenario)
        loads = _prepare_loads(root, work, scenario, resolved_loads)
        modeled, overlays = _apply_overlays(image, work, scenario)
        model_path = work / "model.bin"
        model_path.write_bytes(modeled)
        elf = _link_model(root, work, scenario)
        output = _execute(
            root,
            elf,
            scenario,
            extra_memory_regions=extra_memory_regions,
            gdb_commands=gdb_commands,
        )
        for expected in expected_output:
            if expected not in output:
                raise CodeFlashSimError(
                    f"simulation output lacks {expected!r}\n{output}"
                )
        modeled_sha = hashlib.sha256(modeled).hexdigest()
        (work / "simulation.json").write_text(json.dumps({
            "schema": "rh850-codeflash-sim-result-v1",
            "scenario": scenario.name,
            "input": {"path": str(image_path), "sha256": input_sha, "size": len(image)},
            "modeled_sha256": modeled_sha,
            "overlays": overlays,
            "loads": loads,
            "proof_boundary": SIMULATION_PROOF_BOUNDARY,
            "output": output,
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result_elf = None if temporary is not None else elf
        return SimulationResult(output, input_sha, modeled_sha, result_elf)
    finally:
        if temporary is not None:
            temporary.cleanup()


def run_raw_image(
    *,
    root: Path,
    image_path: Path,
    image_base: int = 0,
    entry: int | None = None,
    memory_regions: Sequence[str] = (),
    gdb_commands: Sequence[str] = (),
    ram_loads: Sequence[tuple[int, Path]] = (),
    output_dir: Path | None = None,
    expected_output: Sequence[str] = (),
) -> SimulationResult:
    """Execute an unrecognized raw image without a target-specific scenario."""
    root = root.resolve()
    image_path = image_path.resolve()
    image = image_path.read_bytes()
    if not image:
        raise CodeFlashSimError("CodeFlash image cannot be empty")
    image_end = image_base + len(image)
    if not 0 <= image_base <= 0xFFFFFFFF or image_end > 0x100000000:
        raise CodeFlashSimError("CodeFlash range wraps the address space")
    if entry is None:
        entry = image_base
    if not 0 <= entry <= 0xFFFFFFFF:
        raise CodeFlashSimError("entry is outside the 32-bit address space")

    normalized_loads: list[tuple[int, Path, bytes, str]] = []
    occupied: list[tuple[int, int, str]] = [(image_base, image_end, "CodeFlash")]
    for index, (address, supplied_path) in enumerate(ram_loads):
        path = (supplied_path if supplied_path.is_absolute() else root / supplied_path).resolve()
        try:
            blob = path.read_bytes()
        except OSError as exc:
            raise CodeFlashSimError(f"cannot read RAM load {path}: {exc}") from exc
        if not blob:
            raise CodeFlashSimError(f"RAM load {path} cannot be empty")
        end = address + len(blob)
        if not 0 <= address <= 0xFFFFFFFF or end > 0x100000000:
            raise CodeFlashSimError(f"RAM load {path} wraps the address space")
        for old_start, old_end, old_name in occupied:
            if _overlaps(address, end, old_start, old_end):
                raise CodeFlashSimError(
                    f"RAM load {index} overlaps {old_name} "
                    f"at 0x{address:08X}..0x{end:08X}"
                )
        occupied.append((address, end, f"RAM load {index}"))
        normalized_loads.append((address, path, blob, hashlib.sha256(blob).hexdigest()))

    executable_ranges = [(image_base, image_end)]
    executable_ranges.extend(
        (address, address + len(blob))
        for address, _, blob, _ in normalized_loads
    )
    if not any(start <= entry < end for start, end in executable_ranges):
        raise CodeFlashSimError(
            f"entry 0x{entry:08X} is outside CodeFlash and all --load ranges"
        )

    input_sha = hashlib.sha256(image).hexdigest()
    tmp_parent = root / "build" / "tmp"
    tmp_parent.mkdir(parents=True, exist_ok=True)
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if output_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="rh850-raw-codeflash-", dir=tmp_parent)
        work = Path(temporary.name)
    else:
        work = output_dir.resolve()
        try:
            work.relative_to(root)
        except ValueError as exc:
            raise CodeFlashSimError("output directory must be inside the repository") from exc
        work.mkdir(parents=True, exist_ok=True)

    try:
        (work / "model.bin").write_bytes(image)
        _run_tool(root, (
            "exec", "--work-dir", str(work), "v850-elf-objcopy",
            "-I", "binary", "-O", "elf32-v850-rh850", "-B", "v850:rh850",
            "--rename-section", ".data=.codeflash,alloc,load,readonly,code,contents",
            "/out/model.bin", "/out/model.o",
        ))

        load_audit: list[dict[str, object]] = []
        for index, (address, path, blob, digest) in enumerate(normalized_loads):
            binary = work / f"load-{index}.bin"
            binary.write_bytes(blob)
            section = f".raw.load.{index}"
            _run_tool(root, (
                "exec", "--work-dir", str(work), "v850-elf-objcopy",
                "-I", "binary", "-O", "elf32-v850-rh850", "-B", "v850:rh850",
                "--rename-section", f".data={section},alloc,load,code,contents",
                f"/out/{binary.name}", f"/out/load-{index}.o",
            ))
            load_audit.append({
                "address": f"0x{address:08X}",
                "path": str(path),
                "sha256": digest,
                "size": len(blob),
            })

        linker_lines = [
            "SECTIONS {",
            f"  .codeflash 0x{image_base:08X} : {{ *(.codeflash) }}",
        ]
        for index, (address, _, _, _) in enumerate(normalized_loads):
            linker_lines.append(
                f"  .raw_load_{index} 0x{address:08X} : {{ *(.raw.load.{index}) }}"
            )
        linker_lines.extend([
            "}",
            f"_generic_entry = 0x{entry:08X};",
            "ENTRY(_generic_entry)",
            "",
        ])
        (work / "generic.ld").write_text("\n".join(linker_lines), encoding="utf-8")
        objects = ["/out/model.o"]
        objects.extend(f"/out/load-{index}.o" for index in range(len(normalized_loads)))
        _run_tool(root, (
            "exec", "--work-dir", str(work), "v850-elf-ld", "--no-warn-mismatch",
            "-T", "/out/generic.ld", *objects, "-o", "/out/generic.elf",
        ))
        elf = work / "generic.elf"

        args: list[str] = ["sim", str(elf)]
        for region in memory_regions:
            args += ["--memory-region", region]
        commands = tuple(gdb_commands) or (
            "starti",
            "x/8i $pc",
            "info registers pc",
        )
        for command in commands:
            args += ["-ex", command]
        proc = _run_tool(root, args)
        output = proc.stdout + proc.stderr
        for expected in expected_output:
            if expected not in output:
                raise CodeFlashSimError(
                    f"simulation output lacks {expected!r}\n{output}"
                )

        (work / "simulation.json").write_text(json.dumps({
            "schema": "rh850-raw-codeflash-sim-result-v1",
            "input": {
                "path": str(image_path),
                "sha256": input_sha,
                "size": len(image),
                "base": f"0x{image_base:08X}",
                "entry": f"0x{entry:08X}",
            },
            "loads": load_audit,
            "proof_boundary": SIMULATION_PROOF_BOUNDARY,
            "output": output,
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result_elf = None if temporary is not None else elf
        return SimulationResult(output, input_sha, input_sha, result_elf)
    finally:
        if temporary is not None:
            temporary.cleanup()
