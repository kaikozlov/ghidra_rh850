#!/usr/bin/env python3
"""Protect retained-bank boundaries and rollback after promotion changes windows."""
from __future__ import annotations

import ctypes
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from tools.targets.camry.decomp import promotion, sources, tree
from tools.targets.camry.decomp.c_text import (
    _c_contains, _direct_calls, _function_heads, _match_delimiter, _split_args,
)
from tools.targets.camry.decomp.execution import calls, link, memory


def check_source_lookup() -> None:
    symbol = {"name": "subject", "addr": "0x1000"}
    missing = {"name": "missing", "addr": "0x2000"}
    with tempfile.TemporaryDirectory(prefix="camry-source-") as directory:
        root = Path(directory)
        candidates = root / "build/candidates"
        candidate = candidates / "000.c"
        retained = root / "src/retained/00001000.c"
        curated = root / "src/recovered.c"
        candidate.parent.mkdir(parents=True)
        retained.parent.mkdir(parents=True)
        candidate.write_text("int subject(void)\n{\n  return 1;\n}\n", encoding="utf-8")
        retained.write_text("int subject(void)\n{\n  return 2;\n}\n", encoding="utf-8")
        matched = [{"name": "subject", "status": "converted"}]
        with (
            patch.object(sources, "ROOT", root),
            patch.object(sources, "CANDIDATES", candidates),
            patch.object(sources, "load_symbols", return_value=[symbol, missing]),
            patch.object(sources, "load_matched", return_value=matched),
        ):
            # Source lookup never opts into a stale candidate cache, regardless
            # of the status assigned to the canonical retained implementation.
            for status in ("converted", "equivalent", "byte-matched"):
                matched[0]["status"] = status
                assert sources.locate_source("0x1000") == (
                    symbol, retained, retained.read_text(encoding="utf-8"),
                )
                bodies, duplicates = sources._load_bodies(candidates=True)
                expected = candidate if status == "converted" else retained
                assert bodies["subject"] == expected.read_text(encoding="utf-8")
                assert not duplicates
            curated.write_text("int subject(void)\n{\n  return 3;\n}\n", encoding="utf-8")
            assert sources.locate_source("1000") == (
                symbol, curated, curated.read_text(encoding="utf-8"),
            )
            locations = {}
            bodies, duplicates = sources._load_bodies(candidates=True, locations=locations)
            assert bodies["subject"] == curated.read_text(encoding="utf-8")
            assert locations["subject"] == curated and not duplicates
            # Retained-only implementations remain discoverable without candidates.
            curated.unlink()
            candidate.unlink()
            matched[0]["status"] = "converted"
            assert sources.locate_source("subject") == (
                symbol, retained, retained.read_text(encoding="utf-8"),
            )
            for query, message in (
                ("unknown", "unknown reconstructed function"),
                ("0x3000", "unknown reconstructed function"),
                ("missing", "no reconstructed C body"),
            ):
                try:
                    sources.locate_source(query)
                except ValueError as exc:
                    assert message in str(exc)
                else:
                    raise AssertionError(f"{query}: expected lookup failure")
    print("PASS source lookup: cache-independent canonical bodies and explicit unchecked candidates")


def check_c_token_matching() -> None:
    assert _c_contains("emit_value\n (1,\n 2);", "emit_value(1,2);")
    assert _c_contains("emit_value(/* source */ 1, 2);", "emit_value(1,2);")
    assert not _c_contains("other_emit_value(1,2);", "emit_value(1,2);")
    assert not _c_contains('emit_value("a b");', 'emit_value("ab");')
    assert not _c_contains("value + +increment;", "value++increment;")
    assert not _c_contains("// emit_value(1,2);\nother();", "emit_value(1,2);")
    assert _split_args('f(1,2), "a,b", (int[]){1,2}') == [
        "f(1,2)", ' "a,b"', " (int[]){1,2}",
    ]
    code = '(f(")"), g())'
    assert _match_delimiter(code, 0) == len(code) - 1
    assert _match_delimiter(code, len(code) - 1, step=-1) == 0
    assert _match_delimiter("(", 0, required=False) is None
    try:
        _match_delimiter("(", 0)
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete delimiter must fail")
    assert _match_delimiter('(")")', 0) == 4
    assert _match_delimiter('(")")', 0, quoted=False) == 2
    assert [name for name, _open, _close in _direct_calls("f(g(), h())", set())] == ["g", "h", "f"]
    assert [name for name, _open, _close in _direct_calls("f(g(), h())", {"h"})] == ["g", "f"]
    heads = _function_heads(
        "static unsigned internal(void);\n"
        "unsigned internal(void) { return 0; }\n"
        "unsigned visible(void) { return 2; }\n"
        "void\n"
        "*wrapped(\n"
        "  unsigned value)\n"
        "{ return 0; }\n"
        "unsigned declaration(void);\n"
    )
    assert set(heads) == {"visible", "wrapped"}
    print("PASS C-token matching: wrapped calls, identifiers, literals, operators, comments")


def check_promotion_declarations() -> None:
    original, _duplicates = sources._load_bodies()
    probe = "int cleanup_probe(void)\n{\n  return 37;\n}\n"
    with tempfile.TemporaryDirectory(prefix="camry-promotion-") as directory:
        root = Path(directory) / "canonical"
        shutil.copytree(tree.ROOT, root)
        header = root / "include" / "common.h"
        with (
            patch.object(tree, "ROOT", root),
            patch.object(sources, "ROOT", root),
            patch.object(sources, "COMMON_HEADER", header),
            patch.object(promotion, "ROOT", root),
            patch.object(promotion, "COMMON_HEADER", header),
        ):
            paths = [header, *sources.retained_paths()]
            snapshots = {path: path.read_text(encoding="utf-8") for path in paths}
            with (root / "src" / "retained" / "support.c").open("a", encoding="utf-8") as handle:
                handle.write("\n" + probe)
            with header.open("a", encoding="utf-8") as handle:
                handle.write("\nint cleanup_probe(int argument);\n")
            promotion._promote([], [], {})
            assert link._prototypes(header)["cleanup_probe"] == "int cleanup_probe(void)"
            actual, duplicates = sources._load_bodies()
            assert actual == {**original, "cleanup_probe": probe} and not duplicates
            result = subprocess.run(
                [
                    "cc", "-std=c11", "-Werror", "-DCAMRY_HOST",
                    "-I", str(header.parent), "-fsyntax-only", "-x", "c", "-",
                ],
                input='#include "common.h"\nint caller(void) { return cleanup_probe(); }\n',
                text=True, capture_output=True,
            )
            assert result.returncode == 0, result.stderr
            promotion._restore(snapshots)
            assert {path: path.read_text(encoding="utf-8") for path in paths} == snapshots
            restored, duplicates = sources._load_bodies()
            assert restored == original and not duplicates
    print("PASS promotion declarations: retained ABI compiles and header/source rollback is exact")


def check_host_memory_tables() -> None:
    harness = r"""
#include <assert.h>
#include "host_memory.c"

uint8_t camry_fill;
uint32_t camry_SR[14][32];
int camry_code_address(const void *pointer, uint32_t *address) {
    (void)pointer;
    (void)address;
    return 0;
}

static void probe_read(uintptr_t address, uintptr_t width) {
    if (width == 1)
        (void)camry_read8((uint32_t)address);
    else if (width == 2)
        (void)camry_read16((uint32_t)address);
    else
        (void)camry_read32((uint32_t)address);
}

static void probe_write(uintptr_t address, uintptr_t width) {
    if (width == 1)
        camry_write8((uint32_t)address, 0x5a);
    else if (width == 2)
        camry_write16((uint32_t)address, 0x5a5a);
    else
        camry_write32((uint32_t)address, 0x5a5a5a5a);
}

static void expect_fault(const char *kind, uint32_t address,
                         uint32_t width, uint32_t write) {
    uintptr_t args[] = {address, width};
    camry_host_fault_call(write ? (void *)probe_write : (void *)probe_read, args, 2);
    assert(camry_host_fault_kind != NULL);
    assert(strcmp(camry_host_fault_kind, kind) == 0);
    assert(camry_host_fault_address == address);
    assert(camry_host_fault_width == width);
    assert(camry_host_fault_write == write);
}

int main(void) {
    uint32_t sparse[160];
    uint32_t local[] = {0x11223344, 0x55667788, 0x99aabbcc, 0xddeeff00};
    uint32_t overlay;
    CamryHostRegion *regions;
    CamryHostRegister *registers;
    int pass, index, region_capacity, register_capacity;
    camry_host_reset();
    for (pass = 0; pass < 2; pass += 1) {
        overlay = 0xa0b0c0d0u + (uint32_t)pass;
        /* The earliest entries survive several reallocations. */
        camry_host_add(0xfebe4000u, (uint8_t *)local, sizeof(local));
        for (index = 0; index < 160; index += 1) {
            sparse[index] = 0x12340000u + (uint32_t)(index + pass);
            camry_host_add(0x01000000u + (uint32_t)index * 0x10000u,
                (uint8_t *)&sparse[index], sizeof(sparse[index]));
        }
        assert(camry_read32(0xfede4004u) == local[1]);
        camry_host_add(0xfede4004u, (uint8_t *)&overlay, sizeof(overlay));
        for (index = 0; index < 160; index += 1)
            assert(camry_read32(0x01000000u + (uint32_t)index * 0x10000u)
                == sparse[index]);
        assert(camry_read32(0xfebe4000u) == local[0]);
        assert(camry_read32(0xfede4004u) == overlay);
        assert(camry_read32(0xfebe4004u) == overlay);
        assert(camry_read32(0xfebe4008u) == local[2]);
        camry_write16(0xfede4004u, 0x9876u);
        assert(camry_read32(0xfebe4004u) == 0xa0b09876u);
        assert(local[1] == 0x55667788u);
        assert(camry_host_ptr(0xfede4004u) == (uint8_t *)&overlay);
        assert(camry_host_addr(&sparse[159]) == 0x019f0000u);
        assert(camry_host_find(0x01000004u, 1) == NULL);
        assert(camry_host_find(0x01000002u, 4) == NULL);
        for (index = 0; index < 600; index += 1) {
            uint32_t address = 0xff000000u + (uint32_t)index * 0x100u;
            camry_host_add_register(address, 4, (1u << 2) | (1u << 4), 3, 15);
        }
        assert(camry_read32(0xff000000u) == 0);
        assert(camry_read32(0xff025700u) == 0);
        /* Exercise both ends, not just the allocated count. */
        camry_write32(0xff000000u, 0x87654321u + (uint32_t)pass);
        camry_write32(0xff025700u, 0xabcdef01u);
        camry_write16(0xff025702u, 0x1234u);
        assert(camry_read32(0xff000000u) == 0x87654321u + (uint32_t)pass);
        assert(camry_read32(0xff025700u) == 0x1234ef01u);
        assert(camry_read16(0xff025702u) == 0x1234u);
        assert(camry_host_addr(camry_host_ptr(0xff025702u)) == 0xff025702u);
        expect_fault("mmio-width", 0xff025700u, 1, 0);
        expect_fault("misaligned-read", 0xff025701u, 2, 0);
        expect_fault("unmapped-read", 0xff025704u, 4, 0);
        expect_fault("unmapped-write", 0xff025704u, 4, 1);
        camry_host_add_register(0xff080000u, 4, 1u << 4, 1, 15);
        camry_host_add_register(0xff080100u, 4, 1u << 4, 2, 15);
        camry_host_add_register(0xff080200u, 4, (1u << 2) | (1u << 4), 3, 0);
        expect_fault("write-prohibited", 0xff080000u, 4, 1);
        expect_fault("read-prohibited", 0xff080100u, 4, 0);
        expect_fault("uninitialized-read", 0xff080200u, 4, 0);
        camry_write16(0xff080202u, 0x4321u);
        assert(camry_read16(0xff080202u) == 0x4321u);
        expect_fault("uninitialized-read", 0xff080200u, 4, 0);
        expect_fault("unmapped-write", 0xffd51004u, 4, 1);
        camry_host_add_register(0xffd51004u, 4, 1u << 4, 3, 15);
        camry_write32(0xffd51004u, 0);
        assert(camry_read32(0xffd51004u) == 0xffffffffu);
        regions = camry_host_regions;
        registers = camry_host_registers;
        region_capacity = camry_host_region_capacity;
        register_capacity = camry_host_register_capacity;
        camry_host_reset();
        assert(camry_host_regions == regions);
        assert(camry_host_registers == registers);
        assert(camry_host_region_capacity == region_capacity);
        assert(camry_host_register_capacity == register_capacity);
        assert(camry_host_find(0x01000000u, 4) == NULL);
        assert(camry_host_find(0xfebe4004u, 4) == NULL);
        assert(camry_host_find(0xff025700u, 4) == NULL);
        assert(camry_read32(0xffd51004u) == 0);
        assert(camry_dcra1_seeded == 0);
    }
    return 0;
}
"""
    with tempfile.TemporaryDirectory(prefix="camry-host-tables-") as directory:
        executable = Path(directory) / "host-tables"
        result = subprocess.run(
            [
                "cc", "-std=c11", "-Werror", "-I", str(Path(link.__file__).parent),
                "-x", "c", "-", "-o", str(executable),
            ],
            input=harness, text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stderr
        result = subprocess.run([str(executable)], text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
    print("PASS host tables: sparse growth, overlays, aliases, register guards, reset/reuse")


def check_native_faci() -> None:
    harness = r"""
#include "host_memory.c"
uint8_t camry_fill;
uint32_t camry_SR[14][32];
int camry_code_address(const void *pointer, uint32_t *address) {
    (void)pointer;
    (void)address;
    return 0;
}
static void confirm(void) { camry_write8(0xffa20000u, 0xd0u); }
const char *confirm_fault(void) {
    camry_host_fault_call((void *)confirm, NULL, 0);
    return camry_host_fault_kind;
}
static void read_command(void) { (void)camry_read16(0xffa20000u); }
const char *command_read_fault(void) {
    camry_host_fault_call((void *)read_command, NULL, 0);
    return camry_host_fault_kind;
}
"""
    registers = memory.MACHINE_REGISTERS
    command = int(registers["FACI_COMMAND_AREA"]["address"])
    status = int(registers["FSTATR"]["address"])
    ready = 0x8000

    def scenario(quantum=1, state="erased", decrement=False):
        values = {
            "FENTRYR": 0x80, "FSTATR": ready, "FASTAT": 0, "FCMDR": 0,
            "FBCCNT": int(decrement), "FLEMU": 0, "FHVE3": 1, "FHVE15": 1,
            "FSADDR": 4 if decrement else 0, "FEADDR": 0 if decrement else 4,
            "FBCSTAT": 1, "FPSADDR": 0x1234,
        }
        return {
            "name": "native_faci_boundary",
            "entry": {"role": "test", "scope": "resolved-address", "address": "0x0"},
            "registers": {}, "max_instructions": 20000, "stop_addresses": ["0x2"],
            "memory": [
                {
                    "address": hex(int(registers[name]["address"])),
                    "hex": value.to_bytes(int(registers[name]["size"]), "little").hex(),
                    "evidence": "Synthetic FACI register setup",
                }
                for name, value in values.items()
            ],
            **({"hsb_cycles_per_instruction": quantum} if quantum is not None else {}),
            "dataflash_cells": [] if state is None else [{
                "address": "0xff200000", "size": 8, "state": state,
                "evidence": "Synthetic physical cells, independent of payload",
            }],
        }

    with tempfile.TemporaryDirectory(prefix="camry-native-faci-") as directory:
        root = Path(directory)
        shared = root / "host.so"
        result = subprocess.run(
            [
                "cc", "-std=c11", "-Werror", "-shared", "-fPIC",
                "-I", str(Path(link.__file__).parent), "-x", "c", "-", "-o", str(shared),
            ],
            input=harness, text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stderr
        library = ctypes.CDLL(str(shared))
        u32 = ctypes.c_uint32
        library.camry_host_add.argtypes = [u32, ctypes.POINTER(ctypes.c_uint8), u32]
        library.camry_host_add.restype = None
        for width, kind in ((8, ctypes.c_uint8), (16, ctypes.c_uint16), (32, u32)):
            read = getattr(library, f"camry_read{width}")
            read.argtypes, read.restype = [u32], kind
        library.camry_write8.argtypes = [u32, ctypes.c_uint8]
        library.camry_write8.restype = None
        library.camry_native_advance.argtypes = [u32]
        library.camry_native_advance.restype = None
        library.confirm_fault.restype = ctypes.c_char_p
        library.command_read_fault.restype = ctypes.c_char_p

        def install(case):
            empty = (ctypes.c_uint8 * 0)()
            memory.install_regions(library, empty, 0, memory.scenario_regions(case))
            memory.configure_native_model(library, case)

        def read_register(name):
            register = registers[name]
            return getattr(library, f"camry_read{int(register['size']) * 8}")(
                int(register["address"]),
            )

        def schedule(rows):
            view = (calls.NativeAccess * len(rows))(*[
                calls.NativeAccess(tick, address, width, write)
                for tick, address, width, write in rows
            ])
            library.camry_native_set_inputs.argtypes = [ctypes.POINTER(calls.NativeInput), u32]
            library.camry_native_set_accesses.argtypes = [ctypes.POINTER(calls.NativeAccess), u32]
            library.camry_native_finish.argtypes = [u32]
            library.camry_native_set_inputs(None, 0)
            library.camry_native_set_accesses(view, len(view))
            return view

        # No external events: the bridge must still install the original bus clock.
        case = scenario()
        metadata = calls.resolve_target("camry-8965F3307000")[1]
        code = calls.REPO_ROOT / metadata["codeflash"]
        code_link = root / metadata["codeflash"]
        code_link.parent.mkdir(parents=True, exist_ok=True)
        code_link.symlink_to(code)
        identity = calls._native_timing_identity(case, hashlib.sha256(code.read_bytes()).hexdigest())
        digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()
        cache = root / "build" / "tmp" / f"{case['name']}.{digest}.timing-report.json"
        cache.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "schema": "rh850-p1me-machine-report-v2", "target": "camry-8965F3307000",
            "scenario": case["name"], "codeflash_sha256": identity["codeflash_sha256"],
            "model_sha256": memory.MEMORY_MODEL_SHA256, "executable_overlays": False,
            "passed": True, "trace_lost_address": False, "instruction_count": 1601,
            "resolved_run_contract": {
                "entry": {"resolved_address": "0x0"}, "max_instructions": 20000,
                "stop_addresses": ["0x2"], "reset": "none", "hsb_cycles_per_instruction": 1,
                "events": [],
            },
            "memory_accesses": [
                {"instruction": tick, "address": hex(address), "size": width,
                 "kind": "write" if write else "read", "value": "0xdeadbeef"}
                for tick, address, width, write in (
                    (0, command, 1, True), (1599, status, 4, False), (1600, status, 4, False),
                )
            ],
        }
        cache.write_text(json.dumps({"native_timing_identity": identity, "report": report}))
        # A name-only cache from obsolete injected scenarios is never a timing source.
        (cache.parent / f"{case['name']}.timing-report.json").write_text('{"obsolete":true}')
        install(case)
        with patch.object(calls, "REPO_ROOT", root), patch.object(calls, "load_oracles", return_value=[case]):
            timing = calls._native_timing(library, case)
            assert timing is not None and timing[2] == 1601
            library.camry_write8(command, 0xB3)
            assert library.camry_read32(status) & ready == 0       # 1599 cycles
            assert library.camry_read32(status) & ready == ready   # 1600 cycles
            library.camry_native_finish(timing[2])
            for field, value in (
                ("hsb_cycles_per_instruction", 2), ("dataflash_cells", []),
                ("memory", []), ("registers", {"r6": "0x4"}),
            ):
                changed = {**case, field: value}
                try:
                    calls._native_timing(library, changed)
                except AssertionError as exc:
                    assert "original retained inputs" in str(exc)
                else:
                    raise AssertionError(f"changed {field} accepted retained timing")
                changed_identity = calls._native_timing_identity(changed, identity["codeflash_sha256"])
                try:
                    calls._cached_native_timing(cache, changed_identity)
                except AssertionError as exc:
                    assert "identity mismatch" in str(exc)
                else:
                    raise AssertionError(f"stale {field} cache was accepted")
        for changed_identity in (
            {**identity, "model_sha256": "0" * 64},
            {**identity, "codeflash_sha256": "0" * 64},
            {**identity, "primary_sha256": "0" * 64},
        ):
            try:
                calls._cached_native_timing(cache, changed_identity)
            except AssertionError:
                pass
            else:
                raise AssertionError("stale code/model/primary identity accepted")

        # New installations reset both elapsed time and the declared clock.
        for quantum, before, deadline in (
            (800, 1, 2), (1, 1599, 1600), (None, 1599, 1600), (0x80000000, 0, 2),
        ):
            install(scenario(quantum))
            view = schedule([
                (0, command, 1, True), (before, status, 4, False), (deadline, status, 4, False),
            ])
            library.camry_write8(command, 0xB3)
            assert library.camry_read32(status) & ready == 0
            assert library.camry_read32(status) & ready == (ready if quantum else 0)
            library.camry_native_finish(deadline + 1)

        install(scenario(800))
        view = schedule([(0, command, 1, True), (1, status, 4, False)])
        fhve = int(registers["FHVE3"]["address"])
        terminal_input = (calls.NativeInput * 1)(calls.NativeInput(2, fhve, 0, 4))
        library.camry_native_set_inputs(terminal_input, 1)
        library.camry_write8(command, 0xB3)
        assert library.camry_read32(status) & ready == 0
        library.camry_native_finish(2)
        assert library.camry_read32(status) & ready == ready
        assert read_register("FHVE3") == 1  # Terminal events were not dispatched.

        install(scenario())
        view = schedule([
            (0, command, 1, True), (1000, command, 1, True),
            (1600, status, 4, False), (2599, status, 4, False), (2600, status, 4, False),
        ])
        library.camry_write8(command, 0xB3)
        library.camry_write8(command, 0xB3)
        assert library.camry_read32(status) & ready == 0
        assert library.camry_read32(status) & ready == 0
        assert library.camry_read32(status) & ready == ready
        library.camry_native_finish(2601)

        # Read data are independent of command writes. Locking or an early
        # status clear must not move the in-flight forced-stop deadline.
        for width in (1, 2, 4):
            install(scenario())
            view = schedule([
                (0, command, 1, True), (100, command, width, False),
                (101, command, 1, True), (1599, status, 4, False),
                (1600, status, 4, False),
            ])
            bus_input = (calls.NativeInput * 1)(calls.NativeInput(0, command, 0x12345678, 4))
            library.camry_native_set_inputs(bus_input, 1)
            library.camry_write8(command, 0xB3)
            assert getattr(library, f"camry_read{width * 8}")(command) == (
                0x12345678 & ((1 << (width * 8)) - 1)
            )
            library.camry_write8(command, 0x50)
            assert library.camry_read32(status) & (ready | 0x4000) == 0x4000
            assert library.camry_read32(status) & ready == ready
            library.camry_native_finish(1601)
            assert read_register("FASTAT") & 0x10 == 0x10
            library.camry_write8(command, 0x50)
            assert library.camry_read32(status) & 0x4000 == 0
            assert read_register("FASTAT") & 0x10 == 0

        install(scenario())
        assert library.command_read_fault() == b"missing-read-input"
        library.camry_write16.argtypes = [u32, ctypes.c_uint16]
        library.camry_write16(int(registers["FENTRYR"]["address"]), 0xAA00)
        assert library.command_read_fault() == b"read-prohibited"

        # Physical state, not immutable payload bytes, selects blankness.
        for state, expected in (("erased", 0), ("programmed", 1), ("erased", 0), (None, None)):
            install(scenario(1, state))
            library.camry_write8(command, 0x71)
            if state is None:
                assert library.confirm_fault() == b"missing-dataflash-cell-state"
                assert u32.in_dll(library, "camry_host_fault_address").value == 0xFF200000
                assert u32.in_dll(library, "camry_host_fault_width").value == 4
                continue
            library.camry_write8(command, 0xD0)
            library.camry_native_advance(2399 if expected else 7999)
            assert read_register("FSTATR") & ready == 0
            library.camry_native_advance(2400 if expected else 8000)
            assert read_register("FSTATR") & ready == ready
            assert read_register("FBCSTAT") == expected
            assert read_register("FPSADDR") == (0 if expected else 0x1234)

        for decrement in (False, True):
            case = scenario(1, "programmed", decrement)
            # Unknown cells beyond the first programmed word are never scanned.
            if not decrement:
                case["dataflash_cells"][0]["size"] = 4
            install(case)
            library.camry_write8(command, 0x71)
            assert library.confirm_fault() is None
            library.camry_native_advance(2400)
            assert read_register("FSTATR") & ready == ready
            assert read_register("FBCSTAT") == 1
            assert read_register("FPSADDR") == (4 if decrement else 0)

        # Exact word/group latency and the final physical cell in both directions.
        for first, last, dirty, deadline, expected in (
            (0, 0, None, 2400, None),
            (0, 60, None, 8000, None),
            (0, 64, None, 10400, None),
            (0, 68, None, 16000, None),
            (0, 68, 64, 10400, 64),
            (68, 0, 4, 10400, 4),
            (0x7FFC, 0x7FFC, None, 2400, None),
            (0x7FFC, 0x7FF8, 0x7FF8, 8000, 0x7FF8),
        ):
            case = scenario(1, None, first > last)
            values = {"FSADDR": first, "FEADDR": last}
            for row in case["memory"]:
                for name, value in values.items():
                    if int(row["address"], 0) == int(registers[name]["address"]):
                        row["hex"] = value.to_bytes(4, "little").hex()
            case["dataflash_cells"] = [
                {"address": hex(0xFF200000 + offset), "size": 4,
                 "state": "programmed" if offset == dirty else "erased", "evidence": "Synthetic boundary cells"}
                for offset in range(min(first, last), max(first, last) + 4, 4)
            ]
            install(case)
            library.camry_write8(command, 0x71)
            assert library.confirm_fault() is None
            library.camry_native_advance(deadline - 1)
            assert read_register("FSTATR") & ready == 0
            library.camry_native_advance(deadline)
            assert read_register("FSTATR") & ready == ready
            assert read_register("FBCSTAT") == int(expected is not None)
            assert read_register("FPSADDR") == (0x1234 if expected is None else expected)

        for quantum in (0, -1, True, 0x100000000):
            try:
                memory.native_model_inputs(scenario(quantum))
            except AssertionError:
                pass
            else:
                raise AssertionError("invalid or overflowing native clock accepted")
        invalid_cells = (
            [{"address": "0xff1ffffc", "size": 4, "state": "erased", "evidence": "test"}],
            [{"address": "0xff200000", "size": 0x100000000, "state": "erased", "evidence": "test"}],
            [{"address": "0xff200000", "size": 4, "state": "erased", "evidence": ""}],
            scenario()["dataflash_cells"] * 2,
        )
        from tools.emulation.p1me_machine import P1MEMachineError
        for cells in invalid_cells:
            try:
                memory.native_model_inputs({**scenario(), "dataflash_cells": cells})
            except (AssertionError, P1MEMachineError):
                pass
            else:
                raise AssertionError("invalid physical-cell declaration accepted")
    print("PASS native FACI: physical blankness, exact stop deadline, clocks/reset, input-bound timing cache")


def main() -> int:
    check_source_lookup()
    check_c_token_matching()
    check_promotion_declarations()
    check_host_memory_tables()
    check_native_faci()
    symbols = [
        {"name": "lower", "addr": "0xfff"},
        {"name": "upper", "addr": "0x1000"},
        {"name": "later", "addr": "0x2000"},
    ]
    bodies = {
        "lower": "int lower(void)\n{\n  return 1;\n}\n",
        "upper": "int upper(void)\n{\n  return 2;\n}\n",
        "helper": "int helper(void)\n{\n  __builtin_trap();\n}\n",
    }
    with tempfile.TemporaryDirectory(prefix="camry-retained-") as directory:
        root = Path(directory)
        header = root / "include" / "common.h"
        header.parent.mkdir()
        header.write_text("int lower(void);\nint upper(void);\n", encoding="utf-8")
        with (
            patch.object(sources, "ROOT", root),
            patch.object(sources, "load_symbols", return_value=symbols),
            patch.object(sources, "_object_definitions", return_value=[]),
        ):
            sources.write_retained(bodies)
            paths = sources.retained_paths()
            assert [path.name for path in paths] == [
                "00000000.c", "00001000.c", "support.c",
            ]
            recovered, duplicates = sources.load_c_bodies(paths)
            assert recovered == bodies and not duplicates
            snapshots = {path: path.read_text(encoding="utf-8") for path in [*paths, header]}

            # A failed promotion can remove windows and helper stubs, change
            # bodies and declarations, and introduce a previously absent window.
            sources.write_retained({
                "lower": "int lower(void)\n{\n  return 99;\n}\n",
                "later": "int later(void)\n{\n  return 3;\n}\n",
            })
            header.write_text("int lower(int argument);\nint later(void);\n", encoding="utf-8")
            assert not (root / "src/retained/00001000.c").exists()
            assert not (root / "src/retained/support.c").exists()
            assert (root / "src/retained/00002000.c").exists()
            promotion._restore(snapshots)
            restored = {
                path: path.read_text(encoding="utf-8")
                for path in [*sources.retained_paths(), header]
            }
            assert restored == snapshots
    print("PASS retained boundaries, helper definitions, and whole-bank/header rollback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
