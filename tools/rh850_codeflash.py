#!/usr/bin/env python3
"""Execute RH850 CodeFlash images at their real addresses in the GDB simulator.

Two modes share one pipeline:

- Spec-less: any raw image, an explicit entry, and optional RAM loads. This is
  the fast viability check for a newly acquired binary.
- Spec: a target model — an assembly harness (stock context, startup-order
  stubs), byte-pinned instruction overlays, RAM-load pockets, and a GDB script.
  Overlay preimages bind the model to the exact image; any byte drift at a
  modeled site aborts before execution.

What this proves is modeled CPU execution along the exercised path. It cannot
prove upload, retention, interrupts, peripherals, timing, or vehicle behavior —
that boundary lives in docs/tooling/rh850-build-and-sim.md, not in this code.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_ENTRY_SYMBOL = "codeflash_sim_start"
_HARNESS_REGION_SIZE = 0x1000


class CodeFlashSimError(RuntimeError):
    pass


@dataclass(frozen=True)
class Overlay:
    section: str
    address: int
    expected: bytes


@dataclass(frozen=True)
class Spec:
    assembly: Path
    codeflash_size: int
    harness_address: int
    image_sha256: frozenset[str] = field(default_factory=frozenset)
    entry_symbol: str = DEFAULT_ENTRY_SYMBOL
    memory_regions: tuple[str, ...] = ()
    gdb: tuple[str, ...] = ()
    loads: tuple[tuple[int, int], ...] = ()  # (address, max_size)
    overlays: tuple[Overlay, ...] = ()


def _address(value: Any, label: str) -> int:
    try:
        parsed = int(value, 0) if isinstance(value, str) else int(value)
    except (TypeError, ValueError) as exc:
        raise CodeFlashSimError(f"{label} is not an address: {value!r}") from exc
    if not 0 <= parsed <= 0xFFFFFFFF:
        raise CodeFlashSimError(f"{label} is outside the 32-bit address space")
    return parsed


def load_spec(root: Path, path: Path) -> Spec:
    """Load a target model. Specs are repo-authored; malformed fields fail loudly."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CodeFlashSimError(f"cannot load spec {path}: {exc}") from exc
    try:
        assembly = Path(raw["assembly"])
        codeflash_size = int(raw["codeflash_size"])
        harness_address = _address(raw["harness_address"], "harness_address")
    except (KeyError, TypeError, ValueError) as exc:
        raise CodeFlashSimError(f"spec {path} lacks a valid {exc}") from exc
    return Spec(
        assembly=assembly if assembly.is_absolute() else root / assembly,
        codeflash_size=codeflash_size,
        harness_address=harness_address,
        image_sha256=frozenset(raw.get("image_sha256", ())),
        entry_symbol=raw.get("entry_symbol", DEFAULT_ENTRY_SYMBOL),
        memory_regions=tuple(raw.get("memory_regions", ())),
        gdb=tuple(raw.get("gdb", ())),
        loads=tuple(
            (_address(row["address"], "loads[].address"), int(row["max_size"]))
            for row in raw.get("loads", ())
        ),
        overlays=tuple(
            Overlay(
                section=row["section"],
                address=_address(row["address"], "overlays[].address"),
                expected=bytes.fromhex(row["expected"]),
            )
            for row in raw.get("overlays", ())
        ),
    )


def _run_tool(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [str(root / "tools/rh850"), *args],
        cwd=root, text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        raise CodeFlashSimError(
            f"command failed ({' '.join(args[:3])}…):\n{proc.stdout}{proc.stderr}"
        )
    return proc


def _compile_harness(root: Path, work: Path, spec: Spec) -> None:
    source = spec.assembly.relative_to(root).as_posix()
    _run_tool(root, (
        "exec", "--work-dir", str(work),
        "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-ffreestanding",
        "-fno-builtin", "-Os", "-nostdlib", "-Wa,-mv850e3v5,-mextension",
        "-c", f"/src/{source}", "-o", "/out/harness.o",
    ))
    dump_args = ["exec", "--work-dir", str(work), "v850-elf-objcopy"]
    for index, overlay in enumerate(spec.overlays):
        dump_args += [
            "--dump-section", f"{overlay.section}=/out/overlay-{index}.bin",
        ]
    dump_args.append("/out/harness.o")
    _run_tool(root, dump_args)


def _apply_overlays(image: bytes, work: Path, spec: Spec) -> bytes:
    modeled = bytearray(image)
    occupied: list[tuple[int, int]] = []
    for index, overlay in enumerate(spec.overlays):
        replacement = (work / f"overlay-{index}.bin").read_bytes()
        end = overlay.address + len(replacement)
        if len(replacement) != len(overlay.expected):
            raise CodeFlashSimError(
                f"overlay {overlay.section} is {len(replacement)} bytes; "
                f"preimage pins {len(overlay.expected)}"
            )
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
    return bytes(modeled)


def _link(
    root: Path,
    work: Path,
    *,
    image_base: int,
    harness_address: int | None,
    load_addresses: Sequence[int],
    entry_symbol: str | None,
    entry_address: int | None,
) -> Path:
    lines = ["SECTIONS {"]
    if harness_address is not None:
        lines.append(f"  .codeflash 0x{image_base:08X} : {{ *(.codeflash) }}")
        lines.append(f"  .sim_harness 0x{harness_address:08X} : {{ *(.sim.harness) }}")
        for index, address in enumerate(load_addresses):
            lines.append(f"  .sim_load_{index} 0x{address:08X} : {{ *(.sim.load.{index}) }}")
        lines.append("  /DISCARD/ : { *(.sim.overlay.*) }")
        entry = f"ENTRY({entry_symbol})"
    else:
        lines.append(f"  .codeflash 0x{image_base:08X} : {{ *(.codeflash) }}")
        for index, address in enumerate(load_addresses):
            lines.append(f"  .raw_load_{index} 0x{address:08X} : {{ *(.raw.load.{index}) }}")
        entry = f"_generic_entry = 0x{entry_address:08X};\nENTRY(_generic_entry)"
    lines += ["}", entry, ""]
    (work / "sim.ld").write_text("\n".join(lines), encoding="utf-8")

    _run_tool(root, (
        "exec", "--work-dir", str(work), "v850-elf-objcopy",
        "-I", "binary", "-O", "elf32-v850-rh850", "-B", "v850:rh850",
        "--rename-section", ".data=.codeflash,alloc,load,readonly,code,contents",
        "/out/model.bin", "/out/model.o",
    ))
    objects = ["/out/model.o"]
    for index in range(len(load_addresses)):
        objects.append(f"/out/load-{index}.o")
    if harness_address is not None:
        objects.insert(0, "/out/harness.o")
    _run_tool(root, (
        "exec", "--work-dir", str(work), "v850-elf-gcc", "-nostdlib",
        "-Wl,--no-warn-mismatch", "-Wl,-T,/out/sim.ld", "-Wl,--build-id=none",
        *objects, "-o", "/out/sim.elf",
    ))
    return work / "sim.elf"


def run(
    *,
    root: Path,
    image_path: Path,
    spec: Spec | None = None,
    image_base: int = 0,
    entry: int | None = None,
    ram_loads: Sequence[tuple[int, Path]] = (),
    memory_regions: Sequence[str] = (),
    gdb_commands: Sequence[str] = (),
    expected_output: Sequence[str] = (),
    output_dir: Path | None = None,
) -> tuple[str, Path | None]:
    """Execute the image; return (simulator output, retained ELF or None)."""
    root = root.resolve()
    image_path = image_path if image_path.is_absolute() else root / image_path
    image = image_path.read_bytes()
    if not image:
        raise CodeFlashSimError("CodeFlash image cannot be empty")
    if spec is not None:
        image_base = 0
        if len(image) != spec.codeflash_size:
            raise CodeFlashSimError(
                f"CodeFlash size mismatch: spec pins 0x{spec.codeflash_size:X}, got 0x{len(image):X}"
            )
        digest = hashlib.sha256(image).hexdigest()
        if spec.image_sha256 and digest not in spec.image_sha256:
            raise CodeFlashSimError(f"spec rejects image SHA-256 {digest}")
    image_end = image_base + len(image)
    if image_end > 0x100000000:
        raise CodeFlashSimError("CodeFlash range wraps the address space")

    # Resolve RAM loads against the spec contract and every other occupant.
    supplied: dict[int, Path] = {}
    for address, path in ram_loads:
        resolved = path if path.is_absolute() else root / path
        if address in supplied:
            raise CodeFlashSimError(f"duplicate RAM load at 0x{address:08X}")
        supplied[address] = resolved
    allowed = {slot_address: max_size for slot_address, max_size in (spec.loads if spec else ())}
    if spec is not None and set(supplied) != set(allowed):
        raise CodeFlashSimError(
            f"RAM loads do not match spec: missing="
            f"[{', '.join(f'0x{a:08X}' for a in sorted(set(allowed) - set(supplied)))}], "
            f"unexpected=[{', '.join(f'0x{a:08X}' for a in sorted(set(supplied) - set(allowed)))}]"
        )

    harness = spec.harness_address if spec is not None else None
    occupied: list[tuple[int, int, str]] = [(image_base, image_end, "CodeFlash")]
    if harness is not None:
        occupied.append((harness, harness + _HARNESS_REGION_SIZE, "harness"))
    load_blobs: list[tuple[int, bytes]] = []
    for address in sorted(supplied):
        path = supplied[address]
        try:
            blob = path.read_bytes()
        except OSError as exc:
            raise CodeFlashSimError(f"cannot read RAM load {path}: {exc}") from exc
        if not blob:
            raise CodeFlashSimError(f"RAM load {path} cannot be empty")
        max_size = allowed.get(address)
        if max_size is not None and len(blob) > max_size:
            raise CodeFlashSimError(
                f"RAM load at 0x{address:08X} is {len(blob)} bytes; pocket holds {max_size}"
            )
        end = address + len(blob)
        if end > 0x100000000:
            raise CodeFlashSimError(f"RAM load at 0x{address:08X} wraps the address space")
        for old_start, old_end, name in occupied:
            if address < old_end and old_start < end:
                raise CodeFlashSimError(
                    f"RAM load at 0x{address:08X} overlaps {name} (0x{old_start:08X}..0x{old_end:08X})"
                )
        occupied.append((address, end, f"RAM load 0x{address:08X}"))
        load_blobs.append((address, blob))

    executable = [(image_base, image_end), *[(a, a + len(b)) for a, b in load_blobs]]
    entry_address = image_base if entry is None else entry
    if spec is None and not any(start <= entry_address < stop for start, stop in executable):
        raise CodeFlashSimError(
            f"entry 0x{entry_address:08X} is outside CodeFlash and all RAM loads"
        )

    tmp_parent = root / "build/tmp"
    tmp_parent.mkdir(parents=True, exist_ok=True)
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if output_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="rh850-codeflash-sim-", dir=tmp_parent)
        work = Path(temporary.name)
    else:
        work = output_dir.resolve()
        try:
            work.relative_to(root)
        except ValueError as exc:
            raise CodeFlashSimError("output directory must be inside the repository") from exc
        work.mkdir(parents=True, exist_ok=True)

    try:
        if spec is not None:
            _compile_harness(root, work, spec)
        (work / "model.bin").write_bytes(
            _apply_overlays(image, work, spec) if spec is not None else image
        )
        for index, (_, blob) in enumerate(load_blobs):
            (work / f"load-{index}.bin").write_bytes(blob)
            section = f".sim.load.{index}" if spec is not None else f".raw.load.{index}"
            _run_tool(root, (
                "exec", "--work-dir", str(work), "v850-elf-objcopy",
                "-I", "binary", "-O", "elf32-v850-rh850", "-B", "v850:rh850",
                "--rename-section", f".data={section},alloc,load,code,contents",
                f"/out/load-{index}.bin", f"/out/load-{index}.o",
            ))
        elf = _link(
            root, work,
            image_base=image_base,
            harness_address=spec.harness_address if spec else None,
            load_addresses=[address for address, _ in load_blobs],
            entry_symbol=spec.entry_symbol if spec else None,
            entry_address=entry_address,
        )

        args: list[str] = ["sim", str(elf)]
        regions = tuple(memory_regions) + (spec.memory_regions if spec else ())
        for region in regions:
            args += ["--memory-region", region]
        script: tuple[str, ...]
        if gdb_commands:
            script = tuple(gdb_commands)
        elif spec is not None and spec.gdb:
            script = spec.gdb
        else:
            script = ("starti", "x/8i $pc", "info registers pc")
        for command in script:
            args += ["-ex", command]
        proc = _run_tool(root, args)
        output = proc.stdout + proc.stderr
        for expected in expected_output:
            if expected not in output:
                raise CodeFlashSimError(f"simulation output lacks {expected!r}\n{output}")

        (work / "output.txt").write_text(output, encoding="utf-8")
        return output, (None if temporary is not None else elf)
    finally:
        if temporary is not None:
            temporary.cleanup()
