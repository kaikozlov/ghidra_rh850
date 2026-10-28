#!/usr/bin/env python3
"""Resolve a TSS3 CodeFlash contract and build the universal 0x08A request signer."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, cast

from tools import REPO_ROOT as REPO
from tools.targets.tss3.console import render_build
from tsk.common.payload_package import inspect_payload, package_shellcode
from tsk.common.ram_exec import TOYOTA_P1ME_PAYLOAD_BUILD_SECRET
from tsk.common.rh850_build import (
    CJob,
    compile_c_batch,
    jarl_targets,
    nm_symbol,
    sha_bytes,
    validate_toolchain,
)
from tsk.ram_runtime.target_profiles import (
    BOOT_F181_HEX,
    spec_from_codeflash,
    supported_targets,
    target_spec,
)
from tsk.ram_runtime.tss3_request_signer_contract import (
    HELPER_CODE_LIMIT,
    HELPER_TRANSIT_BASE,
    RESIDENT_BASE,
    STATE_SIZE,
)

BUILDER = Path(__file__).resolve()
SCHEMA = "tss3-request-signer-build-v2"
REQUEST_CODEC = "four-frame"
REQUEST_CARRIER = "functional-nibble4"
REQUEST_FRAME_COUNT = 4

RESIDENT_SOURCE = REPO / "tsk/ram_runtime/request_signer/tss3_request_signer_resident.c"
RESIDENT_ENTRY_SOURCE = REPO / "tsk/ram_runtime/request_signer/tss3_request_signer_resident.S"
HELPER_SOURCE = REPO / "tsk/ram_runtime/request_signer/tss3_request_signer_helper.c"
ABI_HEADER = REPO / "tsk/ram_runtime/request_signer/tss3_request_signer.h"
RESOLVER_SOURCE = REPO / "tsk/ram_runtime/request_signer/tss3_request_signer_resolver.c"
STAGE_ENTRY_SOURCE = REPO / "tsk/ram_runtime/request_signer/tss3_request_signer_stage.S"
STATE_MAGIC = 0x4C433841  # little-endian "A8CL"
STATE_VERSION = 3
UNIVERSAL_SIGNER_HELPER_CODE_LIMIT = HELPER_CODE_LIMIT
TARGETS = supported_targets()
SPECULATIVE_FETCH_GUARD_SIZE = 48
# Own C frames only; stock firmware callees and interrupts are not included.
RESIDENT_STACK_BUDGET = 0
HELPER_STACK_BUDGET = 24
CACHE_PUBLICATION_SEQUENCE = bytes.fromhex("1f001c00")  # syncp; synci
CMP_IMMEDIATE_RE = re.compile(
    r"\bcmp\s+(-?(?:0x[0-9a-fA-F]+|[0-9]+))\s*,"
)


def output_stem(target: str) -> str:
    return f"{target.replace('-', '_')}_request_signer"


def default_output_dir(target: str) -> Path:
    return REPO / "build/out/ram-runtime" / target / "tss3-request-signer"


STAGING_BASE = 0xFEBF0000
STAGING_LIMIT = 0xFD0
RESIDENT_STAGING_OFFSET = 0xB50
RESOLVER_OUTPUT_BASE = 0xFEBFFB78

# The resolver writes five boot-transition targets followed immediately by the
# resident's 28-word configuration. The retained resident and helper consume
# only this fixed ABI; no software ID or target profile enters the payload.
CONFIG_FIELDS = (
    "app_context",
    "startup_first",
    "startup_after",
    "startup_final",
    "timing_flag",
    "tick_counter",
    "fg_timing_begin",
    "fg_pre_0",
    "fg_pre_1",
    "fg_pre_2",
    "fg_pre_3",
    "fg_aggregate",
    "fg_post_0",
    "fg_post_1",
    "fg_post_2",
    "fg_timing_end",
    "state_base",
    "scratch_base",
    "ring_base",
    "ring_producer",
    "auth_reset",
    "auth_trip",
    "freshness_encode",
    "command5_sync",
    "lower_can_write",
    "command5_globals",
    "response_handle",
    "ring_words",
)
CONFIG_OFFSETS = {name: index * 4 for index, name in enumerate(CONFIG_FIELDS)}
CONFIG_SIZE = len(CONFIG_FIELDS) * 4
CONFIG_BASE = 0xFEBFFBFC - CONFIG_SIZE
RESIDENT_CODE_LIMIT = CONFIG_BASE - RESIDENT_BASE
RESOLVER_STACK_BUDGET = 256
if RESOLVER_OUTPUT_BASE + 5 * 4 != CONFIG_BASE:
    raise AssertionError("resolver output/config ABI drift")


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def validate_cmp_immediates(source: str, *, label: str) -> None:
    """Reject GNU-as truncation of RH850's signed five-bit compare immediate."""
    for lineno, line in enumerate(source.splitlines(), 1):
        match = CMP_IMMEDIATE_RE.search(line)
        if match is None:
            continue
        value = int(match.group(1), 0)
        need(
            -16 <= value <= 15,
            f"{label} line {lineno} uses out-of-range cmp imm5 {match.group(1)}",
        )


def config_macros() -> dict[str, int]:
    return {
        "ORACLE_CONFIG_BASE": CONFIG_BASE,
        "RESOLVER_OUTPUT_BASE": RESOLVER_OUTPUT_BASE,
        **{f"CFG_{name.upper()}": offset for name, offset in CONFIG_OFFSETS.items()},
    }


def config_header_source() -> str:
    defines = "\n".join(f"#define {name} 0x{value:X}" for name, value in config_macros().items())
    offsets = "\n".join(
        f'_Static_assert(offsetof(SignerConfig, {name}) == {offset}, "config {name} ABI");'
        for name, offset in CONFIG_OFFSETS.items()
    )
    return (
        defines + "\n#ifndef __ASSEMBLER__\n"
        f'#include "/src/{ABI_HEADER.relative_to(REPO)}"\n'
        + offsets + f'\n_Static_assert(sizeof(SignerConfig) == {CONFIG_SIZE}, "config size ABI");\n'
        "#endif\n"
    )


def build_request_signer(
    *,
    target: str | None = None,
    codeflash: Path | None = None,
    output_dir: Path | None = None,
    stem: str | None = None,
) -> dict[str, Any]:
    """Resolve one exact CodeFlash contract and emit the universal signer build.

    Returns the build metadata dict. Raises on any identity, ABI, placement,
    relocation, or size failure; partial outputs are never reported as success.
    """
    if target is not None and codeflash is not None:
        raise ValueError("pass exactly one of target or codeflash")
    if stem is not None and re.fullmatch(r"[A-Za-z0-9_.-]+", stem) is None:
        raise ValueError("output stem must be a filename stem without path separators")

    selected = (
        spec_from_codeflash(codeflash)
        if codeflash is not None
        else target_spec(target if target is not None else TARGETS[0])
    )
    compatibility = {
        "status": "self-resolved-compatible",
        "resolver": "on-device-codeflash",
        "codeflash_sha256": selected["sha256"],
    }
    out = output_dir if output_dir is not None else default_output_dir(selected["name"])
    out.mkdir(parents=True, exist_ok=True)
    file_stem = stem if stem is not None else output_stem(selected["name"])
    contract_path = out / f"{file_stem}_contract.json"
    contract_path.write_text(
        json.dumps(selected["contract"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    validate_cmp_immediates(
        RESIDENT_ENTRY_SOURCE.read_text(encoding="utf-8"), label=str(RESIDENT_ENTRY_SOURCE),
    )

    with tempfile.TemporaryDirectory(prefix="tss3-request-signer-") as td:
        work = Path(td)
        (work / "signer_config.h").write_text(config_header_source(), encoding="utf-8")
        helper, resident = compile_c_batch(work, (
            CJob(
                sources=(str(HELPER_SOURCE.relative_to(REPO)),),
                stem="helper", vma=HELPER_TRANSIT_BASE, entry="_helper_entry",
                symbols={}, defines={}, preinclude="signer_config.h",
                stack_budget=HELPER_STACK_BUDGET,
                # In the four-frame build, hoisting saves four code bytes but
                # adds twelve stack bytes. Keep the original helper footprint.
                extra_cflags=("-fno-move-loop-invariants",),
            ),
            CJob(
                sources=(
                    str(RESIDENT_ENTRY_SOURCE.relative_to(REPO)),
                    str(RESIDENT_SOURCE.relative_to(REPO)),
                ),
                stem="resident", vma=RESIDENT_BASE, entry="_resident_entry",
                symbols={"_helper_entry": HELPER_TRANSIT_BASE},
                defines={}, preinclude="signer_config.h",
                stack_budget=RESIDENT_STACK_BUDGET,
            ),
        ))
        helper_blob = helper["blob"]; assert isinstance(helper_blob, bytes)
        resident_blob = resident["blob"]; assert isinstance(resident_blob, bytes)
        helper_code_size = len(helper_blob)
        resident_code_size = len(resident_blob)
        need(nm_symbol(str(helper["nm"]), "helper_entry") == HELPER_TRANSIT_BASE,
             "helper entry drift")
        need(not helper["relocations"], "helper retains relocations")
        need(jarl_targets(str(helper["disasm"])) == [],
             "helper retained a target-specific direct call")
        helper_blob += b"\0" * (-len(helper_blob) % 4)
        helper_blob += b"\0" * SPECULATIVE_FETCH_GUARD_SIZE
        need(len(helper_blob) <= UNIVERSAL_SIGNER_HELPER_CODE_LIMIT,
             "helper plus speculative-fetch guard exceeds universal layout: "
             f"{len(helper_blob)} > {UNIVERSAL_SIGNER_HELPER_CODE_LIMIT}")

        need(nm_symbol(str(resident["nm"]), "resident_entry") == RESIDENT_BASE,
             "resident entry drift")
        resident_tick_wait = nm_symbol(str(resident["nm"]), "resident_tick_wait")
        if resident_tick_wait is None:
            raise RuntimeError("resident tick-wait symbol missing")
        need(not resident["relocations"], "resident retains relocations")
        resident_base = RESIDENT_BASE
        need(resident_tick_wait >= resident_base + STATE_SIZE,
             "live scheduler overlaps the reclaimed state prefix")
        for symbol in ("resident_state_clear", "resident_forever"):
            address = nm_symbol(str(resident["nm"]), symbol)
            need(address is not None and address >= resident_base + STATE_SIZE,
                 f"{symbol} overlaps the reclaimed state prefix")
        resident_calls = jarl_targets(str(resident["disasm"]))
        need(all(
            target == HELPER_TRANSIT_BASE
            or resident_base + STATE_SIZE <= target < resident_base + resident_code_size
            for target in resident_calls
        ), f"resident retained a target-specific direct call: {resident_calls}")
        resident_blob += b"\0" * (-len(resident_blob) % 4)
        resident_blob += b"\0" * SPECULATIVE_FETCH_GUARD_SIZE
        need(len(resident_blob) <= RESIDENT_CODE_LIMIT,
             f"resident plus speculative-fetch guard overlaps runtime config: "
             f"{len(resident_blob)} > {RESIDENT_CODE_LIMIT}")

        resident_offset = RESIDENT_STAGING_OFFSET
        helper_offset = STAGING_LIMIT - len(helper_blob)
        resident_embedded = resident_blob[:-SPECULATIVE_FETCH_GUARD_SIZE]
        helper_embedded = helper_blob[:-SPECULATIVE_FETCH_GUARD_SIZE]
        need(
            resident_offset + len(resident_embedded) <= helper_offset,
            "resident overlaps the staged helper: "
            f"0x{resident_offset + len(resident_embedded):X} > 0x{helper_offset:X}",
        )
        need(helper_offset + len(helper_blob) == STAGING_LIMIT,
             "helper source guard no longer ends at the authenticated callback boundary")
        stage = compile_c_batch(work, (
            CJob(
                sources=(
                    str(STAGE_ENTRY_SOURCE.relative_to(REPO)),
                    str(RESOLVER_SOURCE.relative_to(REPO)),
                ),
                stem="resolver", vma=STAGING_BASE, entry="_exploit",
                symbols={},
                defines={
                    "STAGED_RESIDENT_BASE": STAGING_BASE + resident_offset,
                    "STAGED_HELPER_BASE": STAGING_BASE + helper_offset,
                    "INSTALL_RESIDENT_BASE": RESIDENT_BASE,
                    "RESIDENT_SIZE": len(resident_embedded),
                    "INSTALL_HELPER_BASE": HELPER_TRANSIT_BASE,
                    "RESIDENT_GUARD_SIZE": SPECULATIVE_FETCH_GUARD_SIZE,
                    "HELPER_SIZE": len(helper_blob),
                },
                preinclude="signer_config.h",
                stack_budget=RESOLVER_STACK_BUDGET,
            ),
        ))[0]
        stage_code = stage["blob"]; assert isinstance(stage_code, bytes)
        need(nm_symbol(str(stage["nm"]), "exploit") == STAGING_BASE,
             "resolver staging entry drift")
        need(not stage["relocations"], "resolver staging retains relocations")
        need(len(stage_code) <= resident_offset,
             f"resolver staging exceeds its budget: {len(stage_code)} > {resident_offset}")
        resolver_calls = jarl_targets(str(stage["disasm"]))
        need(all(STAGING_BASE <= address < STAGING_BASE + len(stage_code)
                 for address in resolver_calls),
             f"resolver staging retained an external direct call: {resolver_calls}")
        need(stage_code.count(CACHE_PUBLICATION_SEQUENCE) == 2,
             "staging must publish both copied executable regions")
        resident_handoff = nm_symbol(
            str(stage["nm"]), "request_signer_resident_handoff",
        )
        need(resident_handoff is not None, "staging resident-handoff symbol missing")
        stage_blob = stage_code.ljust(resident_offset, b"\0") + resident_embedded
        stage_blob = stage_blob.ljust(helper_offset, b"\0") + helper_embedded
        stage_blob = stage_blob.ljust(STAGING_LIMIT, b"\0")
        need(len(stage_blob) == STAGING_LIMIT, "staging size drift")
        need(stage_blob[resident_offset:resident_offset + len(resident_embedded)] == resident_embedded,
             "resident embedding drift")
        need(stage_blob[helper_offset:helper_offset + len(helper_embedded)] == helper_embedded,
             "helper embedding drift")

        payload = package_shellcode(stage_blob, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
        need(len(payload) == 0x1000, "authenticated payload is not exact 4 KiB")
        shellcode_region = inspect_payload(
            payload, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET,
        ).shellcode_region
        helper_guard_start = helper_offset + len(helper_embedded)
        need(
            shellcode_region[
                helper_guard_start:helper_guard_start + SPECULATIVE_FETCH_GUARD_SIZE
            ] == bytes(SPECULATIVE_FETCH_GUARD_SIZE),
            "authenticated shell padding does not supply the helper fetch guard",
        )
        (out / f"{file_stem}.bin").write_bytes(stage_blob)
        (out / f"{file_stem}_resident.bin").write_bytes(resident_blob)
        (out / f"{file_stem}_helper.bin").write_bytes(helper_blob)
        (out / f"{file_stem}_payload.bin").write_bytes(payload)

        debug_dir = out / f"{file_stem}_debug"
        debug_dir.mkdir(exist_ok=True)
        shutil.copy2(work / "signer_config.h", debug_dir / "signer_config.h")
        debug_units = {}
        for name, compiled in (("resolver", stage), ("resident", resident), ("helper", helper)):
            files = cast(list[Path], compiled["files"])
            for path in files:
                shutil.copy2(path, debug_dir / path.name)
            debug_units[name] = {
                "elf": f"{name}.elf",
                "disassembly": f"{name}.disasm",
                "stack_reports": [
                    path.name for path in files if path.suffix == ".su"
                ],
                "compile_command": compiled["compile_command"],
            }

        meta: dict[str, Any] = {
            "schema": SCHEMA,
            "toolchain": validate_toolchain(),
            "debug": {
                "directory": debug_dir.name,
                "units": debug_units,
            },
            "target": {
                "name": selected["name"],
                "application_f181_hex": selected["application_f181_hex"],
                "boot_f181_hex": BOOT_F181_HEX,
            },
            "compatibility": compatibility,
            "request": {
                "bus": selected["request"]["request_bus"],
                "can_id": f"0x{selected['request']['request_id']:08X}",
                "codec": REQUEST_CODEC,
                "carrier": REQUEST_CARRIER,
                "frame_count": REQUEST_FRAME_COUNT,
            },
            "response": {
                "bus": selected["request"]["response_bus"],
                "can_id": f"0x{selected['request']['response_id']:08X}",
            },
            "state": {
                "version": STATE_VERSION,
                "base": f"0x{int(selected['contract']['memory']['state_base']):08X}",
                "size": STATE_SIZE,
                "layout": selected["contract"]["memory"]["layout"],
            },
            "resident": {
                "path": f"{file_stem}_resident.bin",
                "base": f"0x{RESIDENT_BASE:08X}",
                "size": len(resident_blob),
                "code_size": resident_code_size,
                "guard_size": SPECULATIVE_FETCH_GUARD_SIZE,
                "sha256": sha_bytes(resident_blob),
                "tick_wait": f"0x{resident_tick_wait:08X}",
                "stack_frames": resident["stack_usage"],
            },
            "helper": {
                "path": f"{file_stem}_helper.bin",
                "base": f"0x{HELPER_TRANSIT_BASE:08X}",
                "size": len(helper_blob),
                "code_size": helper_code_size,
                "guard_size": SPECULATIVE_FETCH_GUARD_SIZE,
                "sha256": sha_bytes(helper_blob),
                "staging_offset": helper_offset,
                "stack_frames": helper["stack_usage"],
            },
            "resolver": {
                "source": str(RESOLVER_SOURCE.relative_to(REPO)),
                "output_base": f"0x{RESOLVER_OUTPUT_BASE:08X}",
                "config_base": f"0x{CONFIG_BASE:08X}",
                "code_size": len(stage_code),
                "stack_frames": stage["stack_usage"],
            },
            "staging": {
                "path": f"{file_stem}.bin",
                "resident_offset": resident_offset,
                "helper_offset": helper_offset,
                "resident_handoff": f"0x{resident_handoff:08X}",
            },
            "authenticated_payload": {
                "path": f"{file_stem}_payload.bin",
                "sha256": sha_bytes(payload),
            },
        }
        (out / f"{file_stem}.json").write_text(
            json.dumps(meta, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return meta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    source = ap.add_mutually_exclusive_group()
    source.add_argument("--target", choices=TARGETS)
    source.add_argument("--codeflash", type=Path, help="resolve and include one arbitrary CodeFlash dump")
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--output-stem")
    ap.add_argument("--json", action="store_true", help="print the full JSON metadata instead of the human summary")
    args = ap.parse_args()
    try:
        meta = build_request_signer(
            target=args.target,
            codeflash=args.codeflash,
            output_dir=args.output_dir,
            stem=args.output_stem,
        )
    except (OSError, RuntimeError, subprocess.CalledProcessError, UnicodeDecodeError, ValueError) as exc:
        ap.error(str(exc))
    if args.json:
        print(json.dumps(meta, indent=2, sort_keys=True))
    else:
        out = args.output_dir if args.output_dir is not None else default_output_dir(meta["target"]["name"])
        print(render_build(meta, str(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
