#!/usr/bin/env python3
"""One gate for generic CodeFlash execution, F33 Gate-2 differential,
registered RAM canaries, and the dump-generated universal signer model."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest import mock

from exploit.common.rh850_build import CJob, compile_c_batch, nm_symbol
import tools.targets.tss3.builders.build_tss3_request_signer as signer_builder
from exploit.patcher.build_payload import simulate_apply
from exploit.patcher.patch_config import config_from_manifest
from exploit.ram_runtime.target_profiles import supported_targets, target_spec
from tools import REPO_ROOT
from tools.rh850_codeflash import CodeFlashSimError, Overlay, Spec
from tools.rh850_codeflash import run as run_codeflash
from tools.rh850_codeflash import run_elf
from tools.security.build_secoc_patch_manifest import crc32
from tools.targets.camry.builders import (
    build_camry_f33_gate2_root_result_patch as gate2_builder,
)
from tools.targets.tss3.onboard_ram_signer import simulate_candidate

ROOT = REPO_ROOT

GATE2_SPEC = ROOT / "tests/fixtures/rh850/camry_f33_gate2_codeflash_sim.json"
F33_SPEC = ROOT / "tests/fixtures/rh850/camry_f33_runtime_canary_sim.json"
COROLLA_SPEC = ROOT / "tests/fixtures/rh850/corolla_hf_runtime_canary_sim.json"
CRC_START = 0x18000
CRC_FIXUP = 0xFFDEC
CRC_END = 0xFFDF0


UNWIND_HARNESS_ADDRESS = 0xFEF00000
UNWIND_STACK_TOP = 0xFEF00C00
UNWIND_SCRATCH = 0xFEF00A00
UNWIND_MEMORY_REGION = f"0x{UNWIND_HARNESS_ADDRESS:X},0x2000"

UNWIND_RAW_SOURCE = """\
    .section .text
    .global _start
_start:
    mov 0xFEBF0700, sp
    mov 0xFEBF0100, r1
    mov 1, r6
    jarl raw_leaf, lp
ret_raw1:
    st.w r10, 0[r1]
    mov 0xFEBF0200, r29
    mov 2, r6
    jarl raw_leaf2, lp
ret_raw2:
    st.w r10, 4[r1]
    .global raw_stop
raw_stop:
    br raw_stop
    .global raw_leaf
raw_leaf:
    addi 0x1000, r6, r10
    jmp [lp]
    .global raw_leaf2
raw_leaf2:
    addi 0x2000, r6, r10
    jmp [lp]
"""

# Every V850 frame shape the prologue unwinder must reconstruct, using the
# exact instruction sequences GCC emits: "prepare {r20, r29, lp}, 8" reserves
# 8 words (32 bytes) of stack beyond the saved registers; fp_fn mirrors the
# -O0 add/st.w/addi/mov sequence; movi_fn mirrors the -Os shape where a
# 32-bit "mov imm,reg" (two-byte instruction plus four-byte immediate)
# precedes the stack adjustment; far_fn calls through the six-byte jarl32
# (the long-call form) with a displacement whose low halfword decodes as
# "add -4,sp"; ind_fn calls through "jarl [reg]" and hides never-executed
# stack manipulation behind the call that the scan must not read past. The
# caller plants distinct junk in r29 before each call so a frameless leaf,
# a zeroed frame pointer, and a scratch-used frame pointer are all exercised.
UNWIND_HARNESS_SOURCE = """\
    .section .sim.harness,"ax"
    .global codeflash_sim_start
    .type codeflash_sim_start, @function
codeflash_sim_start:
    movhi 0xFEF0, r0, sp
    movea 0x0C00, sp, sp
    movhi 0xFEF0, r0, r1
    movea 0x0A00, r1, r1
    mov 0x13572468, r20
    mov 0x11112222, r29
    mov 6, r6
    jarl prep_fn, lp
ret_from_prep:
    st.w r10, 0[r1]
    mov 0x33334444, r29
    mov 7, r6
    jarl fp_fn, lp
ret_from_fp:
    st.w r10, 4[r1]
    mov 0, r29
    mov 9, r6
    jarl zero_fp_fn, lp
ret_from_zero_fp:
    st.w r10, 8[r1]
    mov 0x55556666, r29
    mov 8, r6
    jarl frameless_fn, lp
ret_from_frameless:
    st.w r10, 12[r1]
    mov 0x77778888, r29
    mov 10, r6
    jarl movi_fn, lp
ret_from_movi:
    st.w r10, 16[r1]
    mov 0x99AABBCC, r20
    mov 11, r6
    jarl far_fn, lp
ret_from_far:
    st.w r10, 20[r1]
    mov 0xDDCCBBAA, r20
    mov 12, r6
    jarl ind_fn, lp
ret_from_ind:
    st.w r10, 24[r1]
    .type codeflash_sim_stop, @function
codeflash_sim_stop:
    br codeflash_sim_stop
    .size codeflash_sim_stop, . - codeflash_sim_stop
    .size codeflash_sim_start, . - codeflash_sim_start

    .global prep_fn
    .type prep_fn, @function
prep_fn:
    prepare {r20, r29, lp}, 8
    mov 0xAAAAAAAA, r20
    mov 0xBBBBBBBB, r29
    st.w r6, 0[sp]
    ld.w 0[sp], r6
    addi 0x100, r6, r10
    dispose 8, {r20, r29, lp}, lp
    .size prep_fn, . - prep_fn

    .global fp_fn
    .type fp_fn, @function
fp_fn:
    add -4, sp
    st.w r29, 0[sp]
    addi -44, sp, sp
    mov sp, r29
    st.w r6, 0[r29]
    ld.w 0[r29], r6
    addi 0x200, r6, r10
    mov r29, sp
    ld.w 44[sp], r29
    addi 48, sp, sp
    jmp [lp]
    .size fp_fn, . - fp_fn

    .global zero_fp_fn
    .type zero_fp_fn, @function
zero_fp_fn:
    addi 0x400, r6, r10
    jmp [lp]
    .size zero_fp_fn, . - zero_fp_fn

    .global frameless_fn
    .type frameless_fn, @function
frameless_fn:
    addi 0x300, r6, r10
    jmp [lp]
    .size frameless_fn, . - frameless_fn

    .global movi_fn
    .type movi_fn, @function
movi_fn:
    prepare {r29, lp}, 0
    mov 0xFEBF0A50, r29
    add -4, sp
    st.w r6, 0[sp]
    ld.w 0[sp], r6
    addi 0x500, r6, r10
    add 4, sp
    dispose 0, {r29, lp}, lp
    .size movi_fn, . - movi_fn

# far_fn: JARL32 call whose 32-bit displacement has the halfword 0x1a5c
# ("add -4,sp") as its low half.  A scanner that consumes only the first
# halfword of the six-byte instruction decodes the displacement as a stack
# adjustment and reconstructs the caller SP four bytes low.
    .global far_fn
    .type far_fn, @function
far_fn:
    prepare {r20, lp}, 0
far32_site:
    jarl32 far32_leaf, lp
    .global far_mid
far_mid:
    dispose 0, {r20, lp}, lp
    .size far_fn, . - far_fn

# far32_leaf sits exactly 0x1a5c bytes after the JARL32, so the encoded
# displacement is 0x00001a5c.
    .space (far32_site + 0x1a5c) - .
    .global far32_leaf
    .type far32_leaf, @function
far32_leaf:
    addi 0x600, r6, r10
    jmp [lp]
    .size far32_leaf, . - far32_leaf

# ind_fn: indirect JARL.  The leaf jumps back past the trap block, so the
# "addi -64,sp" and the "st.w r20,0[sp]" after the call never execute;
# they exist only for a scanner that fails to stop at the call and would
# fold them into the prologue.
    .global ind_fn
    .type ind_fn, @function
ind_fn:
    prepare {r20, lp}, 0
    movhi hi(ind_leaf), r0, r10
    movea lo(ind_leaf), r10, r10
    jarl [r10], lp
    addi -64, sp, sp
    st.w r20, 0[sp]
    .global ind_cont
ind_cont:
    dispose 0, {r20, lp}, lp
    .size ind_fn, . - ind_fn

    .global ind_leaf
    .type ind_leaf, @function
ind_leaf:
    addi 0x700, r6, r10
    jr ind_cont
    .size ind_leaf, . - ind_leaf
"""


# Compiled-C twins of the harness shapes above: prep_user (-Os) lowers to a
# PREPARE/DISPOSE frame with a stack-array body, fp_user (-O0) to the
# st.w/addi/mov frame-pointer shape with r20 kept live across a call. GCC's
# V850 backend emits .debug_frame unconditionally (DWARF2_FRAME_INFO), and GDB
# prefers DWARF CFI over the prologue scanner whenever a frame entry exists, so
# the CFI must describe the caller truthfully at every stop: mid-body, after
# the epilogue stack release, and after the dispose. Every expectation is
# expressed relative to captured entry registers or planted register sentinels, never
# to a pinned frame size, so the checks track the frame contract itself.
UNWIND_CFI_OS_SOURCE = """\
#define RESULTS (*(volatile unsigned int *)0xFEBF0100)
#define RES2 (*(volatile unsigned int *)0xFEBF0104)

static unsigned int __attribute__((noinline)) sink_os(unsigned int x)
{
    volatile unsigned int i;
    unsigned int s = 0;
    for (i = 0; i < 3; i++)
        s += x + i;
    return s;
}

void __attribute__((noinline)) prep_user(int a)
{
    int b[4];
    int i;
    unsigned int s = (unsigned int)a;
    for (i = 0; i < 4; i++)
        b[i] = a + i;
    asm volatile(".global prep_mid\\nprep_mid:");
    s += sink_os((unsigned int)b[(s ^ (unsigned int)a) & 3]);
    asm volatile("mov 0xAAAAAAA1, r20\\n\\tmov 0xAAAAAAA2, r29" ::: "r20", "r29");
    s += sink_os((unsigned int)b[(s ^ (unsigned int)a) & 3]);
    RESULTS = s;
    asm volatile(".global prep_done\\nprep_done:");
}

void fp_user(int a);

static void __attribute__((noinline)) driver(void)
{
    asm volatile("mov 0x13572468, r20\\n\\tmov 0x11112222, r29" ::: "r20", "r29");
    prep_user(5);
    asm volatile(".global ret_from_prep\\nret_from_prep:");
    RESULTS = 0xC0DE0001;
    fp_user(6);
    asm volatile(".global ret_from_fp\\nret_from_fp:");
    RES2 = 0xC0DE0002;
}

void __attribute__((noreturn)) _start(void)
{
    asm volatile("mov 0xFEBF0700, sp");
    driver();
    asm volatile(".global cfi_stop\\ncfi_stop: br cfi_stop");
    __builtin_unreachable();
}
"""

UNWIND_CFI_O0_SOURCE = """\
#define RES2 (*(volatile unsigned int *)0xFEBF0104)
#define KEEP20 (*(volatile unsigned int *)0xFEBF0108)

static unsigned int __attribute__((noinline)) sink_o0(unsigned int x)
{
    volatile unsigned int i;
    unsigned int s = 0;
    for (i = 0; i < 3; i++)
        s += x + i;
    return s;
}

void __attribute__((noinline)) fp_user(int a)
{
    register unsigned int keep __asm__("r20") = 0x2468ACE0;
    int b[4];
    unsigned int s = (unsigned int)a;
    b[0] = (int)keep;
    asm volatile(".global fp_mid\\nfp_mid:");
    s += sink_o0((unsigned int)a);
    asm volatile("" : "+r"(keep));
    KEEP20 = keep;
    b[(s ^ keep) & 3] = a;
    RES2 = s;
    asm volatile(".global fp_done\\nfp_done:");
}
"""

def check_unwind_raw(work: Path) -> None:
    """Symbol-less RAM code: stepi and target-memory writes at raw frames.

    The first leaf runs with r29 still zero (the simulator's initial
    state); the second inherits caller junk in r29. Both leaves leave lp
    and sp untouched, so the caller is exactly recoverable and stepping
    or assigning at either frame must neither assert nor disturb the run.
    """
    source = work / "unwind-raw.S"
    source.write_text(UNWIND_RAW_SOURCE)
    rel_source = source.relative_to(ROOT)
    rel_elf = (work / "unwind-raw.elf").relative_to(ROOT)
    rel_bin = (work / "unwind-raw.bin").relative_to(ROOT)
    run([
        str(ROOT / "tools/rh850"), "toolchain", "run",
        "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-ffreestanding",
        "-fno-builtin", "-Os", "-nostdlib", "-Wa,-mv850e3v5,-mextension",
        "-Wl,-Ttext=0xFEBF0200", "-Wl,--entry=_start", "-Wl,--build-id=none",
        str(rel_source), "-o", str(rel_elf),
    ])
    run([
        str(ROOT / "tools/rh850"), "toolchain", "run",
        "v850-elf-objcopy", "-O", "binary", "-j", ".text", str(rel_elf), str(rel_bin),
    ])
    symbols = run([
        str(ROOT / "tools/rh850"), "toolchain", "run", "v850-elf-nm", "-n", str(rel_elf),
    ]).stdout
    names = ("_start", "ret_raw1", "ret_raw2", "raw_stop", "raw_leaf", "raw_leaf2")
    addrs = {name: nm_symbol(symbols, name) for name in names}
    missing = sorted(name for name, value in addrs.items() if value is None)
    if missing:
        raise AssertionError(f"raw unwind ELF lacks symbols: {', '.join(missing)}")
    leaf, leaf2, stop = addrs["raw_leaf"], addrs["raw_leaf2"], addrs["raw_stop"]
    script = (
        f"break *0x{leaf:X}",
        f"break *0x{leaf2:X}",
        f"break *0x{stop:X}",
        "run",
        'printf "RAW1_FP=0x%x RAW1_LP_OK=%d\\n", $r29, '
        f"$r31 == 0x{addrs['ret_raw1']:X}",
        "stepi",
        f'printf "RAW1_STEP_OK=%d\\n", $pc == 0x{leaf + 4:X}',
        "set {unsigned int}0xFEBF0120 = 0x600DF00D",
        'printf "RAW1_WRITE_OK=%d\\n", *(unsigned int *)0xFEBF0120 == 0x600DF00D',
        "bt",
        "continue",
        'printf "RAW2_FP_OK=%d RAW2_LP_OK=%d\\n", '
        f"$r29 == 0xFEBF0200, $r31 == 0x{addrs['ret_raw2']:X}",
        "stepi",
        f'printf "RAW2_STEP_OK=%d\\n", $pc == 0x{leaf2 + 4:X}',
        "set {unsigned int}0xFEBF0124 = 0xF00D600D",
        'printf "RAW2_WRITE_OK=%d\\n", *(unsigned int *)0xFEBF0124 == 0xF00D600D',
        "bt",
        "continue",
        'printf "RAW_RESULTS_OK=%d RAW_R0=0x%x RAW_R4=0x%x\\n", '
        '(*(unsigned int *)0xFEBF0100 == 0x1001) && (*(unsigned int *)0xFEBF0104 == 0x2002), '
        '*(unsigned int *)0xFEBF0100, *(unsigned int *)0xFEBF0104',
    )
    image = work / "unwind-raw-CodeFlash.bin"
    image.write_bytes(b"\xFF" * 0x60000)
    run_codeflash(
        root=ROOT, image_path=image, entry=0xFEBF0200,
        ram_loads=[(0xFEBF0200, work / "unwind-raw.bin")],
        memory_regions=("0xFEBF0000,0x1000",),
        stop=f"0x{stop:X}",
        gdb_commands=script,
        expected_output=(
            "RAW1_FP=0x0 RAW1_LP_OK=1",
            "RAW1_STEP_OK=1",
            "RAW1_WRITE_OK=1",
            "RAW2_FP_OK=1 RAW2_LP_OK=1",
            "RAW2_STEP_OK=1",
            "RAW2_WRITE_OK=1",
            "RAW_RESULTS_OK=1 RAW_R0=0x1001 RAW_R4=0x2002",
        ),
        timeout=60.0,
    )
    print("PASS raw RAM unwind: stepi, target writes, zero and junk frame pointer")


def check_unwind_frames(work: Path) -> None:
    """Reconstructed caller SP and PC for every V850 frame shape.

    Stops land after each prologue and at a function entry, stepi walks
    the FP prologue instruction by instruction, and target memory is
    assigned mid-run; frame 1 must then report the caller's exact stack
    pointer, return address, and stack-saved registers every time. The
    jarl32 and indirect-jarl frames pin the scan terminators: the 32-bit
    displacement halfwords and the never-executed trap block after the
    call must never be folded into the prologue.
    """
    source = work / "unwind-harness.S"
    source.write_text(UNWIND_HARNESS_SOURCE)
    spec = Spec(
        assembly=source,
        codeflash_size=0x400,
        harness_address=UNWIND_HARNESS_ADDRESS,
        stop="codeflash_sim_stop",
        memory_regions=(UNWIND_MEMORY_REGION,),
    )
    stack = UNWIND_STACK_TOP
    script = (
        "break *prep_fn + 16",
        "break *fp_fn",
        "break *zero_fp_fn",
        "break *frameless_fn",
        "break *movi_fn + 16",
        "break far_mid",
        "break ind_cont",
        "break codeflash_sim_stop",
        "run",
        'printf "PREP_SP_OK=%d PREP_R20_CLOBBERED_OK=%d PREP_R29_CLOBBERED_OK=%d\\n", '
        f"$sp == 0x{stack - 44:X}, $r20 == 0xAAAAAAAA, $r29 == 0xBBBBBBBB",
        "frame 1",
        'printf "PREP_CALLER_SP_OK=%d PREP_CALLER_PC_OK=%d PREP_SAVED_R20_OK=%d '
        f'PREP_SAVED_FP_OK=%d\\n", $sp == 0x{stack:X}, '
        '$pc == (unsigned long)&ret_from_prep, $r20 == 0x13572468, $r29 == 0x11112222',
        "frame 0",
        "continue",
        f'printf "FPENTRY_SP_OK=%d FPENTRY_FP_JUNK_OK=%d\\n", '
        f"$sp == 0x{stack:X}, $r29 == 0x33334444",
        "frame 1",
        f'printf "FPENTRY_CALLER_SP_OK=%d FPENTRY_CALLER_PC_OK=%d\\n", '
        f"$sp == 0x{stack:X}, $pc == (unsigned long)&ret_from_fp",
        "frame 0",
        "stepi",
        "stepi",
        "stepi",
        "stepi",
        f'printf "FPMID_SP_OK=%d FPMID_FP_OK=%d\\n", '
        f"$sp == 0x{stack - 48:X}, $r29 == 0x{stack - 48:X}",
        "frame 1",
        f'printf "FPMID_CALLER_SP_OK=%d FPMID_CALLER_PC_OK=%d FPMID_SAVED_FP_OK=%d\\n", '
        f"$sp == 0x{stack:X}, $pc == (unsigned long)&ret_from_fp, $r29 == 0x33334444",
        "frame 0",
        "continue",
        'printf "ZFP_SP_OK=%d ZFP_FP_IS_ZERO=%d\\n", '
        f"$sp == 0x{stack:X}, $r29 == 0",
        "frame 1",
        f'printf "ZFP_CALLER_SP_OK=%d ZFP_CALLER_PC_OK=%d\\n", '
        f"$sp == 0x{stack:X}, $pc == (unsigned long)&ret_from_zero_fp",
        "frame 0",
        "stepi",
        f"set {{unsigned int}}0x{UNWIND_SCRATCH + 0x40:X} = 0x600DF00D",
        f'printf "SYM_WRITE_OK=%d\\n", '
        f"*(unsigned int *)0x{UNWIND_SCRATCH + 0x40:X} == 0x600DF00D",
        "continue",
        'printf "LEAF_SP_OK=%d LEAF_FP_JUNK_OK=%d\\n", '
        f"$sp == 0x{stack:X}, $r29 == 0x55556666",
        "frame 1",
        f'printf "LEAF_CALLER_SP_OK=%d LEAF_CALLER_PC_OK=%d\\n", '
        f"$sp == 0x{stack:X}, $pc == (unsigned long)&ret_from_frameless",
        "frame 0",
        "continue",
        'printf "MOVI_SP_OK=%d MOVI_R29_SCRATCH_OK=%d\\n", '
        f"$sp == 0x{stack - 12:X}, $r29 == 0xFEBF0A50",
        "stepi",
        f"set {{unsigned int}}0x{UNWIND_SCRATCH + 0x44:X} = 0xF00D600D",
        f'printf "MOVI_WRITE_OK=%d\\n", '
        f"*(unsigned int *)0x{UNWIND_SCRATCH + 0x44:X} == 0xF00D600D",
        "frame 1",
        'printf "MOVI_CALLER_SP_OK=%d MOVI_CALLER_PC_OK=%d MOVI_SAVED_FP_OK=%d\\n", '
        f"$sp == 0x{stack:X}, $pc == (unsigned long)&ret_from_movi, $r29 == 0x77778888",
        "frame 0",
        "continue",
        f'printf "FAR_SP_OK=%d\\n", $sp == 0x{stack - 8:X}',
        "frame 1",
        'printf "FAR_CALLER_SP_OK=%d FAR_CALLER_PC_OK=%d FAR_SAVED_R20_OK=%d\\n", '
        f'$sp == 0x{stack:X}, $pc == (unsigned long)&ret_from_far, $r20 == 0x99AABBCC',
        "frame 0",
        "continue",
        f'printf "IND_SP_OK=%d\\n", $sp == 0x{stack - 8:X}',
        "frame 1",
        'printf "IND_CALLER_SP_OK=%d IND_CALLER_PC_OK=%d IND_SAVED_R20_OK=%d\\n", '
        f'$sp == 0x{stack:X}, $pc == (unsigned long)&ret_from_ind, $r20 == 0xDDCCBBAA',
        "frame 0",
        "bt",
        "continue",
        'printf "UNWIND_RESULTS_OK=%d\\n", '
        f"(*(unsigned int *)0x{UNWIND_SCRATCH:X} == 0x106) && "
        f"(*(unsigned int *)0x{UNWIND_SCRATCH + 4:X} == 0x207) && "
        f"(*(unsigned int *)0x{UNWIND_SCRATCH + 8:X} == 0x409) && "
        f"(*(unsigned int *)0x{UNWIND_SCRATCH + 12:X} == 0x308) && "
        f"(*(unsigned int *)0x{UNWIND_SCRATCH + 16:X} == 0x50A) && "
        f"(*(unsigned int *)0x{UNWIND_SCRATCH + 20:X} == 0x60B) && "
        f"(*(unsigned int *)0x{UNWIND_SCRATCH + 24:X} == 0x70C)",
    )
    image = work / "unwind-frames-CodeFlash.bin"
    image.write_bytes(b"\xFF" * 0x400)
    run_codeflash(
        root=ROOT, image_path=image, spec=spec,
        gdb_commands=script,
        expected_output=(
            "PREP_SP_OK=1 PREP_R20_CLOBBERED_OK=1 PREP_R29_CLOBBERED_OK=1",
            "PREP_CALLER_SP_OK=1 PREP_CALLER_PC_OK=1 PREP_SAVED_R20_OK=1 PREP_SAVED_FP_OK=1",
            "FPENTRY_SP_OK=1 FPENTRY_FP_JUNK_OK=1",
            "FPENTRY_CALLER_SP_OK=1 FPENTRY_CALLER_PC_OK=1",
            "FPMID_SP_OK=1 FPMID_FP_OK=1",
            "FPMID_CALLER_SP_OK=1 FPMID_CALLER_PC_OK=1 FPMID_SAVED_FP_OK=1",
            "ZFP_SP_OK=1 ZFP_FP_IS_ZERO=1",
            "ZFP_CALLER_SP_OK=1 ZFP_CALLER_PC_OK=1",
            "SYM_WRITE_OK=1",
            "LEAF_SP_OK=1 LEAF_FP_JUNK_OK=1",
            "LEAF_CALLER_SP_OK=1 LEAF_CALLER_PC_OK=1",
            "MOVI_SP_OK=1 MOVI_R29_SCRATCH_OK=1",
            "MOVI_WRITE_OK=1",
            "MOVI_CALLER_SP_OK=1 MOVI_CALLER_PC_OK=1 MOVI_SAVED_FP_OK=1",
            "FAR_SP_OK=1",
            "FAR_CALLER_SP_OK=1 FAR_CALLER_PC_OK=1 FAR_SAVED_R20_OK=1",
            "IND_SP_OK=1",
            "IND_CALLER_SP_OK=1 IND_CALLER_PC_OK=1 IND_SAVED_R20_OK=1",
            "UNWIND_RESULTS_OK=1",
        ),
        timeout=60.0,
    )
    print("PASS symbolized unwind: PREPARE, FP, partial prologue, zero-FP, frameless, imm32 mov, jarl32, indirect jarl")


def check_unwind_cfi(work: Path) -> None:
    """Compiled C: DWARF CFI must carry PREPARE/DISPOSE and FP frames.

    GCC always emits .debug_frame for v850 and GDB unwinds through it in
    preference to the prologue scanner, so a lying FDE poisons every frame
    above it. Stops at function entry, mid-body, before the epilogue, one
    instruction into the epilogue (the stack release), and back in the caller
    pin the caller SP/PC and the stack-saved r20/r29 for the -Os PREPARE shape
    and the -O0 frame-pointer shape, without hardcoding frame sizes: caller SP
    is compared against the captured entry SP, saved registers against planted
    sentinels. Never write a marker at SP: that can overwrite the return address.
    """
    os_source = work / "unwind-cfi-os.c"
    o0_source = work / "unwind-cfi-o0.c"
    os_source.write_text(UNWIND_CFI_OS_SOURCE)
    o0_source.write_text(UNWIND_CFI_O0_SOURCE)
    rel_os = os_source.relative_to(ROOT)
    rel_o0 = o0_source.relative_to(ROOT)
    rel_os_obj = (work / "unwind-cfi-os.o").relative_to(ROOT)
    rel_o0_obj = (work / "unwind-cfi-o0.o").relative_to(ROOT)
    rel_elf = (work / "unwind-cfi.elf").relative_to(ROOT)
    base_flags = (
        "-mv850e3v5", "-mno-app-regs", "-ffreestanding", "-fno-builtin",
        "-nostdlib", "-Wa,-mv850e3v5,-mextension",
    )
    run([
        str(ROOT / "tools/rh850"), "toolchain", "run",
        "v850-elf-gcc", *base_flags, "-Os", "-c", str(rel_os), "-o", str(rel_os_obj),
    ])
    run([
        str(ROOT / "tools/rh850"), "toolchain", "run",
        "v850-elf-gcc", *base_flags, "-O0", "-c", str(rel_o0), "-o", str(rel_o0_obj),
    ])
    run([
        str(ROOT / "tools/rh850"), "toolchain", "run",
        "v850-elf-gcc", *base_flags,
        "-Wl,-Ttext=0xFEBF0200", "-Wl,--entry=__start", "-Wl,--build-id=none",
        str(rel_os_obj), str(rel_o0_obj), "-o", str(rel_elf),
    ])
    symbols = run([
        str(ROOT / "tools/rh850"), "toolchain", "run", "v850-elf-nm", "-n", str(rel_elf),
    ]).stdout
    names = ("_start", "_prep_user", "prep_mid", "prep_done", "ret_from_prep",
             "_fp_user", "fp_mid", "fp_done", "ret_from_fp", "cfi_stop")
    addrs = {name: nm_symbol(symbols, name) for name in names}
    missing = sorted(name for name, value in addrs.items() if value is None)
    if missing:
        raise AssertionError(f"compiled CFI ELF lacks symbols: {', '.join(missing)}")

    # Numeric entry breakpoints: a plain "break FUNC" would consult the
    # architecture prologue skipper and land past the PREPARE we are testing.
    script = (
        f"break *0x{addrs['_prep_user']:X}",
        "break prep_mid",
        "break prep_done",
        f"break *0x{addrs['_fp_user']:X}",
        "break fp_mid",
        "break fp_done",
        "break cfi_stop",
        "run",
        'printf "PENTRY_R29_OK=%d PENTRY_LP_OK=%d\\n", '
        '$r29 == 0x11112222, $r31 == (unsigned long)&ret_from_prep',
        "set $ENTRY = $sp",
        "continue",
        'printf "PMID_SP_LOWERED_OK=%d\\n", $sp < $ENTRY',
        "frame 1",
        'printf "PMID_CALLER_SP_OK=%d PMID_PC_OK=%d '
        'PMID_R20_OK=%d PMID_R29_OK=%d\\n", '
        '$sp == $ENTRY, '
        '$pc == (unsigned long)&ret_from_prep, '
        '$r20 == 0x13572468, $r29 == 0x11112222',
        "frame 0",
        "continue",
        "set $EP0 = $sp",
        "stepi",
        'printf "PEPI_SP_RELEASED_OK=%d\\n", $sp > $EP0',
        "frame 1",
        'printf "PEPI_CALLER_SP_OK=%d PEPI_PC_OK=%d\\n", '
        '$sp == $ENTRY, '
        '$pc == (unsigned long)&ret_from_prep',
        "frame 0",
        f"tbreak *0x{addrs['ret_from_prep']:X}",
        "continue",
        'printf "PEPI_RET_PC_OK=%d PEPI_RET_SP_OK=%d PEPI_R20_OK=%d PEPI_R29_OK=%d\\n", '
        '$pc == (unsigned long)&ret_from_prep, $sp == $ENTRY, '
        '$r20 == 0x13572468, $r29 == 0x11112222',
        "continue",
        'printf "FENTRY_R29_OK=%d FENTRY_LP_OK=%d\\n", '
        '$r29 == 0x11112222, $r31 == (unsigned long)&ret_from_fp',
        "set $ENTRY2 = $sp",
        "continue",
        "frame 1",
        'printf "FMID_CALLER_SP_OK=%d FMID_PC_OK=%d '
        'FMID_R20_OK=%d FMID_R29_OK=%d\\n", '
        '$sp == $ENTRY2, '
        '$pc == (unsigned long)&ret_from_fp, '
        '$r20 == 0x13572468, $r29 == 0x11112222',
        "frame 0",
        "continue",
        # The -O0 epilogue (nop; mov r29,sp; ld.w restores; addi; jmp [lp])
        # releases SP only at its final addi, so skip instruction stepping and
        # land at the return site: every saved register must be back.
        f"tbreak *0x{addrs['ret_from_fp']:X}",
        "continue",
        'printf "FEPI_RET_PC_OK=%d FEPI_RET_SP_OK=%d FEPI_R20_OK=%d FEPI_R29_OK=%d\\n", '
        '$pc == (unsigned long)&ret_from_fp, $sp == $ENTRY2, '
        '$r20 == 0x13572468, $r29 == 0x11112222',
        "continue",
        'printf "CFI_RESULTS_OK=%d\\n", '
        '(*(unsigned int *)0xFEBF0100 == 0xC0DE0001) && '
        '(*(unsigned int *)0xFEBF0104 == 0xC0DE0002) && '
        '(*(unsigned int *)0xFEBF0108 == 0x2468ACE0)',
    )
    run_elf(
        root=ROOT, elf_path=rel_elf, stop="cfi_stop",
        memory_regions=("0xFEBF0000,0x1000",),
        gdb_commands=script,
        expected_output=(
            "PENTRY_R29_OK=1 PENTRY_LP_OK=1",
            "PMID_SP_LOWERED_OK=1",
            "PMID_CALLER_SP_OK=1 PMID_PC_OK=1 PMID_R20_OK=1 PMID_R29_OK=1",
            "PEPI_SP_RELEASED_OK=1",
            "PEPI_CALLER_SP_OK=1 PEPI_PC_OK=1",
            "PEPI_RET_PC_OK=1 PEPI_RET_SP_OK=1 PEPI_R20_OK=1 PEPI_R29_OK=1",
            "FENTRY_R29_OK=1 FENTRY_LP_OK=1",
            "FMID_CALLER_SP_OK=1 FMID_PC_OK=1 FMID_R20_OK=1 FMID_R29_OK=1",
            "FEPI_RET_PC_OK=1 FEPI_RET_SP_OK=1 FEPI_R20_OK=1 FEPI_R29_OK=1",
            "CFI_RESULTS_OK=1",
        ),
        timeout=60.0,
    )
    print("PASS compiled-C unwind: PREPARE/DISPOSE and FP frames via .debug_frame CFI")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise AssertionError(f"command failed: {command}\n{proc.stdout}{proc.stderr}")
    return proc


def simulate(image: Path, expected: str, *, spec: Path | None = None, load: str | None = None,
             entry: str | None = None, memory_region: str | None = None,
             stop: str | None = None, script: tuple[str, ...] = ()) -> None:
    command = [
        str(ROOT / "tools/rh850"),
        "test",
        "codeflash",
        str(image),
        "--expect",
        expected,
    ]
    if spec is not None:
        command += ["--spec", str(spec)]
    if entry is not None:
        command += ["--entry", entry]
    if load is not None:
        command += ["--load", load]
    if memory_region is not None:
        command += ["--memory-region", memory_region]
    if stop is not None:
        command += ["--stop", stop]
    for gdb_command in script:
        command += ["-ex", gdb_command]
    output = run(command).stdout
    if expected not in output:
        raise AssertionError(f"simulation omitted {expected!r}\n{output}")


def build_generic(work: Path) -> tuple[Path, int]:
    """Compile a synthetic resident and its synthetic CodeFlash image for spec-less checks."""
    source = work / "program.S"
    source.write_text(
        "    .section .text\n"
        "    .global _start\n"
        "_start:\n"
        "    ld.w 0x200[r0], r10\n"
        "    mov 0xfebf0100, r11\n"
        "    st.w r10, 0[r11]\n"
        "    .global generic_stop\n"
        "generic_stop:\n"
        "    br generic_stop\n"
    )
    rel_source = source.relative_to(ROOT)
    rel_elf = (work / "program.elf").relative_to(ROOT)
    run([
        str(ROOT / "tools/rh850"), "toolchain", "run",
        "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-ffreestanding",
        "-fno-builtin", "-Os", "-nostdlib", "-Wa,-mv850e3v5,-mextension",
        "-Wl,-Ttext=0xFEBF0200", "-Wl,--entry=_start", "-Wl,--build-id=none",
        str(rel_source), "-o", str(rel_elf),
    ])
    run([
        str(ROOT / "tools/rh850"), "toolchain", "run",
        "v850-elf-objcopy", "-O", "binary", "-j", ".text",
        str(rel_elf), str((work / "program.bin").relative_to(ROOT)),
    ])

    image = bytearray(b"\xFF" * 0x60000)
    struct.pack_into("<I", image, 0x200, 0x13579BDF)
    image_path = work / "new-target-CodeFlash.bin"
    image_path.write_bytes(image)
    symbols = run([
        str(ROOT / "tools/rh850"), "toolchain", "run", "v850-elf-nm", "-n", str(rel_elf),
    ]).stdout
    resident_end = nm_symbol(symbols, "generic_stop")
    if resident_end is None:
        raise AssertionError("linked generic stop symbol is missing")
    return image_path, resident_end


def generic_script(resident_end: int) -> tuple[str, ...]:
    return (
        f"break *0x{resident_end:X}",
        "run",
        'printf "GENERIC_RESULT=0x%x\\n", *(unsigned int *)0xFEBF0100',
    )


def check_generic(image: Path, resident_end: int) -> None:
    """A synthetic resident against a synthetic image: no spec, no target knowledge."""
    simulate(
        image,
        "GENERIC_RESULT=0x13579bdf",
        entry="0xFEBF0200",
        load=f"0xFEBF0200={image.parent / 'program.bin'}",
        memory_region="0xFEBF0000,0x1000",
        stop=f"0x{resident_end:X}",
        script=generic_script(resident_end),
    )
    print("PASS generic resident on synthetic image (spec-less + -ex script)")


def check_contract(work: Path, image: Path, resident_end: int) -> None:
    """A green result must prove execution: postcondition, stop point, pinned bytes."""
    spec_less: dict[str, Any] = {
        "entry": 0xFEBF0200,
        "ram_loads": ((0xFEBF0200, work / "program.bin"),),
        "memory_regions": ("0xFEBF0000,0x1000",),
        "gdb_commands": generic_script(resident_end),
    }

    def expect_rejection(what: str, diagnostic: str, **kwargs: Any) -> None:
        try:
            run_codeflash(root=ROOT, **kwargs)
        except CodeFlashSimError as exc:
            if diagnostic not in str(exc):
                raise AssertionError(f"{what}: wrong rejection: {exc}") from exc
            print(f"PASS rejects {what}")
        else:
            raise AssertionError(f"simulation must reject {what}")

    expect_rejection(
        "a run without a postcondition", "requires a postcondition",
        image_path=image, stop=f"0x{resident_end:X}", **spec_less,
    )
    expect_rejection(
        "a stop the resident never reaches", "unexpected stop",
        image_path=image, stop="0xFEBF0000",
        expected_output=("GENERIC_RESULT=0x13579bdf",), **spec_less,
    )
    expect_rejection(
        "a GDB command supplied as the stop", "stop must be",
        image_path=image, stop=f"*0x{resident_end:X}",
        expected_output=("GENERIC_RESULT=0x13579bdf",), **spec_less,
    )
    expect_rejection(
        "an expected output the resident does not print", "postcondition output lacks",
        image_path=image, stop=f"0x{resident_end:X}",
        expected_output=("GENERIC_RESULT=0x0badf00d",), **spec_less,
    )

    harness = work / "overlay_harness.S"
    harness.write_text(
        "    .section .sim.harness,\"ax\"\n"
        "    .global codeflash_sim_start\n"
        "codeflash_sim_start:\n"
        "    br codeflash_sim_start\n\n"
        "    .global codeflash_sim_stop\n"
        "codeflash_sim_stop:\n"
        "    br codeflash_sim_stop\n"
        "    .section .sim.overlay.drift,\"ax\"\n"
        "    .byte 0, 0, 0, 0\n"
    )
    overlay_image = work / "overlay-drift-CodeFlash.bin"
    overlay_image.write_bytes(bytes(0x400))
    overlay_spec = Spec(
        assembly=harness,
        codeflash_size=0x400,
        harness_address=0xFEF00000,
        stop="codeflash_sim_stop",
        overlays=(
            Overlay(section=".sim.overlay.drift", address=0x100, expected=b"\x11\x22\x33\x44"),
        ),
    )
    try:
        run_codeflash(
            root=ROOT, image_path=overlay_image, spec=overlay_spec,
            expected_output=("OVERLAY_PROBE_RESULT=1",),
        )
    except CodeFlashSimError as exc:
        # Name the cause so a compile failure cannot masquerade as this rejection.
        if "preimage" not in str(exc):
            raise AssertionError(f"overlay drift must fail on the pinned preimage: {exc}") from exc
        print("PASS rejects byte-pinned overlay drift")
    else:
        raise AssertionError("simulation must reject byte-pinned overlay drift")


def check_gate2(work: Path) -> None:
    """Stock, root-only, stage-2, and stage-3 Gate-2 images differ behaviorally."""
    stock = gate2_builder.STOCK_IMAGE.read_bytes()
    if sha256(stock) != gate2_builder.EXPECTED_STOCK_SHA256:
        raise AssertionError("stock image identity drift")

    root_only = bytearray(stock)
    root_only[gate2_builder.ROOT_RESULT_VA:gate2_builder.ROOT_RESULT_VA + 4] = (
        gate2_builder.ROOT_RESULT_REPLACEMENT
    )
    struct.pack_into("<I", root_only, CRC_FIXUP, crc32(bytes(root_only[CRC_START:CRC_FIXUP])) ^ 0xFFFFFFFF)
    if crc32(bytes(root_only[CRC_START:CRC_END])) != 0xFFFFFFFF:
        raise AssertionError("root-only image CRC repair failed")

    stage2, stage2_manifest = gate2_builder.reconstruct_stage2(stock)
    stage3_manifest = gate2_builder.build_stage3_manifest(stage2, stage2_manifest)
    stage3, _, stage3_residue = simulate_apply(stage2, config_from_manifest(stage3_manifest, mode="apply"))
    if sha256(stage3) != gate2_builder.EXPECTED_FINAL_SHA256 or stage3_residue != 0xFFFFFFFF:
        raise AssertionError("stage-3 image construction drift")

    for name, image, expected in (
        ("stock", stock, "GATE2_RESULT=0x222 FRESHNESS_ARG=1 ROOT_BOOL=1"),
        ("root-only", bytes(root_only), "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=0"),
        ("stage2", stage2, "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=1"),
        ("stage3", stage3, "GATE2_RESULT=0x333 FRESHNESS_ARG=0 ROOT_BOOL=0"),
    ):
        image_path = work / f"gate2-{name}.bin"
        image_path.write_bytes(image)
        simulate(image_path, expected, spec=GATE2_SPEC)
        print(f"PASS gate2 {name}: {expected}")


def check_built_resident(work: Path, *, builder: Path, binary_name: str, pocket: int,
                         spec: Path, images: tuple[Path, ...], expected: str) -> None:
    """Build the audited resident, bind it to its build metadata, execute it."""
    build_dir = work / binary_name
    run([sys.executable, str(builder), "--output-dir", str(build_dir)])
    resident = build_dir / f"{binary_name}.bin"
    metadata = json.loads((build_dir / f"{binary_name}.json").read_text(encoding="utf-8"))
    blob = resident.read_bytes()
    if metadata["compile_contract"]["candidate_base"] != "0xFEBF0000":
        raise AssertionError("resident base drift")
    if metadata["compile_contract"]["relocations"] != 0:
        raise AssertionError("resident contains relocations")
    if metadata["shellcode"] != {"headroom": pocket - len(blob), "sha256": sha256(blob), "size": len(blob)}:
        raise AssertionError("resident metadata does not bind the generated binary")

    # Locate the canary's inline TST1 4,-20207[r0] (0xFFFFB111 tick flag).
    # Stop on its second visit: one complete foreground cycle, irrespective
    # of compiler layout changes. Do not pin a generated instruction address.
    tick_wait = bytes.fromhex("c0e711b1")
    offsets = [
        offset for offset in range(0, len(blob) - len(tick_wait) + 1, 2)
        if blob[offset:offset + len(tick_wait)] == tick_wait
    ]
    if len(offsets) != 1:
        raise AssertionError("cannot locate an unambiguous canary tick wait")
    stop = f"0x{0xFEBF0000 + offsets[0]:08X}"
    scenario = json.loads(spec.read_text(encoding="utf-8"))
    scenario["stop"] = stop
    scenario["gdb"][-1:-1] = [f"break *{stop}", "ignore $bpnum 1", "run"]
    resolved_spec = build_dir / "simulation.json"
    resolved_spec.write_text(json.dumps(scenario), encoding="utf-8")

    for image in images:
        simulate(image, expected, spec=resolved_spec, load=f"0xFEBF0000={resident}")
    print(f"PASS {binary_name}: {expected} ({len(images)} image(s))")

def check_request_signer(work: Path) -> None:
    build_dir = work / "tss3-request-signer"
    metadata = signer_builder.build_request_signer(
        target="camry-8965F3307000", output_dir=build_dir,
    )
    staging = build_dir / metadata["staging"]["path"]

    for target in supported_targets():
        spec = target_spec(target)
        simulate_candidate(
            image_path=spec["image"],
            contract=spec["contract"],
            metadata=metadata,
            staging_path=staging,
            output_dir=work / "request-signer-sim" / target,
        )
        print(f"PASS universal request signer {target}")

    # -O2 duplicates the poll loop. A named assembler label inside that loop
    # used to fail assembly; its replacement must also identify a usable poll
    # boundary for the idle-fast path, not merely compile successfully.
    optimized_dir = work / "tss3-request-signer-o2"

    def compile_optimized_resident(work_dir: Path, jobs: tuple[CJob, ...]):
        return compile_c_batch(work_dir, tuple(
            replace(job, extra_cflags=(*job.extra_cflags, "-O2"))
            if job.stem == "resident" else job
            for job in jobs
        ))

    with mock.patch.object(signer_builder, "compile_c_batch", compile_optimized_resident):
        optimized = signer_builder.build_request_signer(
            target="camry-8965F3307000", output_dir=optimized_dir,
        )
    spec = target_spec("camry-8965F3307000")
    simulate_candidate(
        image_path=spec["image"], contract=spec["contract"], metadata=optimized,
        staging_path=optimized_dir / optimized["staging"]["path"],
        output_dir=work / "request-signer-sim-o2",
    )
    print("PASS optimized resident poll marker: fallback and idle-fast execution")


def check_unwind(work: Path) -> None:
    """GDB must reconstruct V850 frames instead of crashing or guessing."""
    check_unwind_raw(work)
    check_unwind_frames(work)
    check_unwind_cfi(work)


def main() -> int:
    tmp_root = ROOT / "build/tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codeflash-sim-", dir=tmp_root) as td:
        work = Path(td)
        image_path, resident_end = build_generic(work)
        check_generic(image_path, resident_end)
        check_contract(work, image_path, resident_end)
        check_unwind(work)
        check_gate2(work)
        check_built_resident(
            work,
            builder=ROOT / "tools/targets/camry/research/ram_runtime/bootstrap/build_camry_f33_command5_carrier.py",
            binary_name="camry_f33_runtime_canary",
            pocket=776,
            spec=F33_SPEC,
            images=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin",),
            expected=(
                "RAM_HEARTBEAT=0x45504844 TICK=1 FLAG=0x0 "
                "CONTEXT=0x43545831 STARTUP=0x53544152 "
                "FOREGROUND=0x46475231 STOCK_ZERO=0x0"
            ),
        )
        check_built_resident(
            work,
            builder=ROOT / "tools/targets/corolla/research/ram_runtime/build_corolla_hf_command5_carrier.py",
            binary_name="corolla_hf_runtime_canary",
            pocket=464,
            spec=COROLLA_SPEC,
            images=(
                ROOT / "firmware/corolla-8965H1202000/CodeFlash.bin",
                ROOT / "firmware/corolla-8965F1208000/CodeFlash.bin",
            ),
            expected=(
                "COROLLA_RAM_HEARTBEAT=0x45504844 TICK=1 "
                "CONTEXT=0x43545848 STARTUP=0x53544152 FOREGROUND=0x46475248"
            ),
        )
        check_request_signer(work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
