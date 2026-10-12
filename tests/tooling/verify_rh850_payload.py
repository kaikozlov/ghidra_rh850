#!/usr/bin/env python3
"""Exercise source-to-verified-result behavior through the public RH850 CLI."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from tools import REPO_ROOT

CLI = REPO_ROOT / "tools/rh850"


def invoke(cwd: Path, *args: str, success: bool = True, error: str = "") -> str:
    proc = subprocess.run(
        [str(CLI), "test", "payload", *args], cwd=cwd,
        text=True, capture_output=True, timeout=150, check=False,
    )
    output = proc.stdout + proc.stderr
    if (proc.returncode == 0) != success:
        raise AssertionError(f"unexpected exit {proc.returncode}: {args}\n{output}")
    if error and error not in output:
        raise AssertionError(f"missing diagnostic {error!r}\n{output}")
    if not success and "Payload test: PASS" in output:
        raise AssertionError(f"failed run reported success\n{output}")
    return output


def verify_bswap(work: Path) -> None:
    """Protect native lowering, flag clobbers, and freestanding execution."""
    (work / "bswap.c").write_text(
        r"""
unsigned __attribute__((noinline, noclone)) swap32(unsigned value) {
    return __builtin_bswap32(value);
}

unsigned __attribute__((noinline, noclone))
swap_compare(unsigned value, unsigned limit) {
    unsigned less = value < limit;
    unsigned swapped = __builtin_bswap32(value);
    return swapped ^ (less ? 0x13579bdfu : 0x2468ace0u);
}

unsigned check_bswap(void) {
    static const unsigned cases[][3] = {
        {0x12345678u, 0x78563412u, 0x12345679u},
        {0x01020304u, 0x04030201u, 0x01020304u},
        {0x00000000u, 0x00000000u, 0x00000001u},
        {0xffffffffu, 0xffffffffu, 0xffffffffu},
        {0x80000000u, 0x00000080u, 0x7fffffffu},
        {0x00000080u, 0x80000000u, 0x00000081u},
        {0xff00aa55u, 0x55aa00ffu, 0xff00aa56u},
        {0x00ff00ffu, 0xff00ff00u, 0x00000000u},
    };
    for (unsigned i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i) {
        volatile unsigned input = cases[i][0];
        unsigned value = input;
        unsigned expected = cases[i][1];
        unsigned limit = cases[i][2];
        if (swap32(value) != expected)
            return 1u + i;
        unsigned mask = value < limit ? 0x13579bdfu : 0x2468ace0u;
        if (swap_compare(value, limit) != (expected ^ mask))
            return 0x100u + i;
    }
    return 0xb5a03201u;
}
""",
        encoding="utf-8",
    )
    (work / "bswap_entry.S").write_text(
        "    .section .text.entry\n    .global _start\n_start:\n"
        "    mov 0x8000, sp\n    jarl _check_bswap, lp\n"
        "    mov 0x2000, r11\n    st.w r10, 0[r11]\n"
        "    .global bswap_stop\nbswap_stop:\n    br bswap_stop\n",
        encoding="utf-8",
    )
    (work / "bswap.ld").write_text(
        "ENTRY(_start)\nSECTIONS { . = 0x100; "
        ".text : { *(.text.entry) *(.text) } .rodata : { *(.rodata*) } }\n",
        encoding="utf-8",
    )
    invoke(
        work, "bswap_entry.S", "bswap.c", "--linker-script", "bswap.ld",
        "--stop", "bswap_stop", "--output-dir", "bswap-result",
        "--assert", "*(unsigned int *)0x2000 == 0xb5a03201",
    )
    dump = subprocess.run(
        [str(REPO_ROOT / "tools/rh850"), "toolchain", "run", "--work-dir", str(work),
         "v850-elf-objdump", "-d", "--disassemble=_swap32",
         "/out/bswap-result/payload.elf"],
        text=True, capture_output=True, timeout=30, check=True,
    ).stdout
    instructions = [
        line.split("\t")[2].split()[0]
        for line in dump.splitlines()
        if len(line.split("\t")) >= 3
    ]
    # A call or shifts/masks instead of BSW break the small freestanding payload.
    assert instructions == ["bsw", "jmp"], dump
    print("PASS native byte swap, unsigned comparison flags, and no runtime helper")

    for architecture, native in (
        ("v850", False), ("v850e1", False), ("v850e2", True),
        ("v850e2v3", True), ("v850e3v5", True),
    ):
        command = [
            str(REPO_ROOT / "tools/rh850"), "toolchain", "run",
            "--work-dir", str(work),
        ]
        subprocess.run(
            [*command, "v850-elf-gcc", f"-m{architecture}", "-Os", "-ffreestanding",
             "-fno-builtin", "-c", "/out/bswap.c", "-o", "/out/bswap.o"],
            text=True, capture_output=True, timeout=60, check=True,
        )
        dump = subprocess.run(
            [*command, "v850-elf-objdump", "-d", "--disassemble=_swap32",
             "/out/bswap.o"],
            text=True, capture_output=True, timeout=30, check=True,
        ).stdout
        instructions = [
            line.split("\t")[2].split()[0]
            for line in dump.splitlines()
            if len(line.split("\t")) >= 3
        ]
        assert ("bsw" in instructions) == native, (architecture, dump)
    print("PASS BSW enabled only on V850E2 and later")

def verify_bit_tests(work: Path) -> None:
    """Protect native TST1 selection, its volatile access rules, and execution."""
    (work / "bits.c").write_text(
        r"""
volatile unsigned char *const VP = (volatile unsigned char *)0x2100;
volatile unsigned int *const VW = (volatile unsigned int *)0x2110;
volatile unsigned char *const PB = (volatile unsigned char *)0x7000;
volatile unsigned char *const FAR = (volatile unsigned char *)0xFFFF8123;
volatile unsigned char *const BOUND = (volatile unsigned char *)0x9000;

/* Codegen targets; never called. Wait loop, bit 0..7, boolean forms. */
void bits_wait(void) { while ((*VP & 16u) == 0) ; }
void bits_wait_bit7(void) { while ((*VP & 128u) == 0) ; }
unsigned bits_bool_eq0(void) { return (*VP & 32u) == 0; }
unsigned bits_bool_bit0(void) { return (*VP & 1u) != 0; }
/* Two volatile reads must stay two reads. */
unsigned bits_two_reads(void) { return (*VP & 16u) && (*VP & 32u); }
/* A volatile word access must not be narrowed to a byte test. */
unsigned bits_wide(void) { return (*VW & 0x10000u) != 0; }
/* A live loaded byte must keep its load. */
unsigned bits_live(void) { unsigned char c = *VP; if (c & 16u) return c; return 0u; }
/* Format VIII computes sign-extend(disp16), so 0xFFFF8123 encodes as -32477. */
unsigned bits_far(void) { return (*FAR & 1u) != 0; }
/* 0x9000 has no sign-extended 16-bit encoding from r0: keep materializing. */
unsigned bits_boundary(void) { return (*BOUND & 2u) != 0; }

static unsigned one_bit(unsigned char v, unsigned b) {
    return (unsigned)((v >> b) & 1u);
}

/* Every access uses p[-4], a negative displacement from a base register. */
static unsigned __attribute__((noinline, noclone))
neg_check(volatile unsigned char *p) {
    static const unsigned char vs[] = {0x00, 0x0f, 0x70, 0xff, 0x2b};
    unsigned acc = 0;
    for (unsigned i = 0; i < sizeof(vs); ++i) {
        unsigned char v = vs[i];
        unsigned e0 = one_bit(v, 0), e3 = one_bit(v, 3), e5 = one_bit(v, 5), e7 = one_bit(v, 7);
        unsigned spins;
        p[-4] = v;
        if (((p[-4] & 0x80u) == 0) != (e7 ^ 1u)) return 0x1000u + i;
        if (((p[-4] & 0x08u) != 0) != e3) return 0x2000u + i;
        if (((p[-4] & 0x01u) != 0) != e0) return 0x3000u + i;
        spins = 0;
        while ((p[-4] & 0x20u) == 0) { p[-4] = (unsigned char)(v | 0x20u); spins++; }
        if (spins != (e5 ? 0u : 1u)) return 0x4000u + i;
        acc = acc * 7u + (unsigned)v + e0 + e3 + e5 + e7;
    }
    return acc;
}

unsigned check_bits(unsigned char *p4) {
    static const unsigned char vals[] = {0x00, 0x01, 0x10, 0x2a, 0x55, 0x80, 0xf0, 0xff, 0x7c, 0x83};
    unsigned acc = 0;
    for (unsigned i = 0; i < sizeof(vals); ++i) {
        unsigned char v = vals[i];
        unsigned e0 = one_bit(v, 0), e1 = one_bit(v, 1), e2 = one_bit(v, 2), e3 = one_bit(v, 3);
        unsigned e4 = one_bit(v, 4), e5 = one_bit(v, 5), e6 = one_bit(v, 6), e7 = one_bit(v, 7);
        unsigned char o;
        unsigned spins;

        *VP = v;
        if (((*VP & 0x01) != 0) != e0) return 0x100u + i;
        if (((*VP & 0x02) != 0) != e1) return 0x200u + i;
        if (((*VP & 0x04) == 0) != (e2 ^ 1u)) return 0x300u + i;
        if (((*VP & 0x08) == 0) != (e3 ^ 1u)) return 0x400u + i;
        if (((*VP & 0x10) != 0) != e4) return 0x500u + i;
        if (((*VP & 0x20) == 0) != (e5 ^ 1u)) return 0x600u + i;
        if (((*VP & 0x40) != 0) != e6) return 0x700u + i;
        if (((*VP & 0x80) == 0) != (e7 ^ 1u)) return 0x800u + i;
        *PB = v;
        if (((*PB & 0x40) != 0) != e6) return 0xc00u + i;

        /* Interleave plain register comparisons with tst1 bit tests:
         * correct flag modeling keeps every result right. */
        unsigned char v2 = *VP;
        acc += (v2 < 0x40u) ? 1u : 0u;
        acc += ((*VP & 0x04) != 0) ? 2u : 0u;
        acc += (v2 >= 0x80u) ? 4u : 0u;
        acc += ((*VP & 0x10) == 0) ? 8u : 0u;

        o = (*VP & 0x80) ? 0xa5u : 0x5au;
        if (o != (e7 ? 0xa5u : 0x5au)) return 0x900u + i;

        spins = 0;
        while ((*VP & 0x80) == 0) { *VP = (unsigned char)(v | 0x80u); spins++; }
        if (spins != (e7 ? 0u : 1u)) return 0xa00u + i;
        spins = 0;
        while ((*VP & 0x10) != 0) { *VP = (unsigned char)(v & ~0x10u); spins++; }
        if (spins != (e4 ? 1u : 0u)) return 0xb00u + i;

        acc = acc * 31u + (e0 ^ e1 ^ e2 ^ e3 ^ e4 ^ e5 ^ e6 ^ e7) + v;
    }
    acc ^= neg_check(p4);
    return acc ^ 0x5a5a1234u;
}
""",
        encoding="utf-8",
    )
    (work / "bits_entry.S").write_text(
        "    .section .text.entry\n    .global _start\n_start:\n"
        "    mov 0x8000, sp\n    movea 0x2124, r0, r6\n    jarl _check_bits, lp\n"
        "    mov 0x2000, r11\n    st.w r10, 0[r11]\n"
        "    .global bits_stop\nbits_stop:\n    br bits_stop\n",
        encoding="utf-8",
    )
    (work / "bits.ld").write_text(
        "ENTRY(_start)\nSECTIONS { . = 0x100; "
        ".text : { *(.text.entry) *(.text) } .rodata : { *(.rodata*) } }\n",
        encoding="utf-8",
    )
    invoke(
        work, "bits_entry.S", "bits.c", "--linker-script", "bits.ld",
        "--stop", "bits_stop", "--output-dir", "bits-result",
        "--assert", "*(unsigned int *)0x2000 == 0x4c555dff",
    )

    def function_mnemonics(elf_or_obj, function: str) -> list[str]:
        dump = subprocess.run(
            [str(REPO_ROOT / "tools/rh850"), "toolchain", "run", "--work-dir", str(work),
             "v850-elf-objdump", "-d", "--disassemble=" + function, str(elf_or_obj)],
            text=True, capture_output=True, timeout=30, check=True,
        ).stdout
        return [
            line.split("\t")[2].split()[0]
            for line in dump.splitlines()
            if len(line.split("\t")) >= 3
        ]

    elf = "/out/bits-result/payload.elf"
    wait = function_mnemonics(elf, "_bits_wait")
    assert "tst1" in wait and "andi" not in wait and not any(
        m.startswith("ld.") for m in wait), wait
    wait7 = function_mnemonics(elf, "_bits_wait_bit7")
    assert "tst1" in wait7 and "andi" not in wait7, wait7
    for name in ("_bits_bool_eq0", "_bits_bool_bit0"):
        body = function_mnemonics(elf, name)
        assert "tst1" in body and "setf" in body and "andi" not in body, (name, body)
    two = function_mnemonics(elf, "_bits_two_reads")
    assert two.count("tst1") == 2 and not any(m.startswith("ld.") for m in two), two
    wide = function_mnemonics(elf, "_bits_wide")
    assert "tst1" not in wide and any(m.startswith("ld.w") for m in wide), wide
    live = function_mnemonics(elf, "_bits_live")
    assert "tst1" not in live and any(m.startswith("ld.b") for m in live), live
    far = function_mnemonics(elf, "_bits_far")
    assert "tst1" in far, far
    boundary = function_mnemonics(elf, "_bits_boundary")
    assert "tst1" in boundary and "andi" not in boundary and not any(
        m.startswith("ld.") for m in boundary), boundary
    neg = function_mnemonics(elf, "_neg_check")
    assert "tst1" in neg, neg
    print("PASS native memory bit tests with volatile reads, widths, and liveness preserved")

    # Older ISAs may use different extension sequences; none may receive an
    # unsupported instruction (in particular, CMOV on the original V850).
    for architecture in ("v850", "v850e1", "v850e2", "v850e2v3", "v850e3v5"):
        command = [
            str(REPO_ROOT / "tools/rh850"), "toolchain", "run",
            "--work-dir", str(work),
        ]
        compiled = subprocess.run(
            [*command, "v850-elf-gcc", f"-m{architecture}", "-Os", "-ffreestanding",
             "-fno-builtin", "-c", "/out/bits.c", "-o", "/out/bits.o"],
            text=True, capture_output=True, timeout=60, check=False,
        )
        assert compiled.returncode == 0, (architecture, compiled.stdout, compiled.stderr)
    print("PASS bit-test lowering assembles for every supported V850 variant")


def verify_far_calls(work: Path) -> None:
    """Far calls cross both directions; near and indirect calls stay compact."""
    import re

    (work / "far_calls.c").write_text(r"""
volatile unsigned observed;

__attribute__((long_call, noipa, section(".text.low")))
unsigned low_value(unsigned value) { return value ^ 0x55aa55aau; }

__attribute__((long_call, noipa, section(".text.far_value")))
unsigned far_value(unsigned a, unsigned b, unsigned c, unsigned d, unsigned e) {
  if (observed != a) return 0u;
  return low_value(a) + b + c + d + e;
}

__attribute__((long_call, noipa, section(".text.far_void")))
void far_void(unsigned value) { observed = value; }

__attribute__((noipa, section(".text.near")))
unsigned near_value(unsigned value) { return value + 7u; }

__attribute__((noipa, section(".text.caller")))
unsigned call_cases(unsigned value, void (*indirect)(unsigned)) {
  unsigned a = near_value(value);
  far_void(a);
  unsigned b = far_value(a, 2u, 3u, 4u, 5u);
  indirect(b);
  return b ^ 0xa5a5a5a5u;
}
""", encoding="utf-8")
    (work / "far_calls.S").write_text(
        "    .section .text.entry\n    .global _start\n_start:\n"
        "    mov 0xfec00000, sp\n    mov 0x12345678, r6\n"
        "    mov hilo(_far_void), r7\n"
        "    jarl _call_cases, lp\n    mov 0xfebf9000, r11\n"
        "    st.w r10, 0[r11]\n    .global far_calls_stop\n"
        "far_calls_stop:\n    br far_calls_stop\n", encoding="utf-8",
    )
    (work / "far_calls.ld").write_text(
        "ENTRY(_start)\nSECTIONS {\n"
        "  .entry 0xFEBF0000 : { *(.text.entry) }\n"
        "  .near 0xFEBF0200 : { *(.text.near) }\n"
        "  .caller 0xFEBF0300 : { *(.text.caller) }\n"
        "  .low 0xFEBF1000 : { *(.text.low) }\n"
        "  .data 0xFEBF8100 : { *(.data*) *(.sdata*) }\n"
        "  .bss 0xFEBF8000 : { *(.bss*) *(.sbss*) *(COMMON) }\n"
        "  .far_value 0xFEF07C00 : { *(.text.far_value) }\n"
        "  .far_void 0xFEF07D00 : { *(.text.far_void) }\n"
        "}\n", encoding="utf-8",
    )
    signed = ((0x12345678 + 7) ^ 0x55AA55AA) + 2 + 3 + 4 + 5
    invoke(
        work, "far_calls.S", "far_calls.c", "--linker-script", "far_calls.ld",
        "--stop", "far_calls_stop", "--output-dir", "far-call-result",
        "--memory-region", "0xFEBF0000,0x20000",
        "--memory-region", "0xFEF00000,0x10000",
        "--assert", f"*(unsigned int *)0xFEBF9000 == {signed ^ 0xA5A5A5A5}",
        "--assert", f"*(unsigned int *)0xFEBF8000 == {signed}",
        "--assert", "$sp == 0xFEC00000",
    )
    command = [str(CLI), "toolchain", "run", "--work-dir", str(work)]
    dump = subprocess.run(
        [*command, "v850-elf-objdump", "-d", "--insn-width=8",
         "/out/far-call-result/payload.elf"],
        text=True, capture_output=True, timeout=30, check=True,
    ).stdout
    calls: dict[int, list[int]] = {}
    indirect_widths = []
    for line in dump.splitlines():
        fields = line.split("\t")
        if len(fields) < 4 or fields[2].strip() != "jarl":
            continue
        width = len(fields[1].split())
        destination = re.match(r"([0-9a-f]+)\s", fields[3])
        if destination:
            calls.setdefault(int(destination[1], 16), []).append(width)
        elif fields[3].startswith("["):
            indirect_widths.append(width)
    for target in (0xFEF07C00, 0xFEF07D00, 0xFEBF1000):
        assert calls.get(target) == [6], (hex(target), calls, dump)
    assert calls.get(0xFEBF0200) == [4], dump
    assert indirect_widths == [4], dump
    print("PASS positive/negative native far calls, fifth argument, near and indirect calls")

    # Legacy ISAs must never receive the six-byte format; global -mlong-calls
    # must retain its documented prohibition of PC-relative calls.
    for architecture, flags, native in (
        ("v850", (), False), ("v850e1", (), False),
        ("v850e2", (), True), ("v850e2v3", (), True),
        ("v850e3v5", (), True), ("v850e3v5", ("-mlong-calls",), False),
    ):
        compiled = subprocess.run(
            [*command, "v850-elf-gcc", f"-m{architecture}", "-mno-app-regs",
             "-Os", "-ffreestanding", "-fno-builtin", "-Werror", *flags,
             "-c", "/out/far_calls.c", "-o", "/out/far_calls.o"],
            text=True, capture_output=True, timeout=60, check=False,
        )
        assert compiled.returncode == 0, (architecture, flags, compiled.stdout, compiled.stderr)
        relocs = subprocess.run(
            [*command, "v850-elf-readelf", "-r", "/out/far_calls.o"],
            text=True, capture_output=True, timeout=30, check=True,
        ).stdout
        assert ("R_V850_PC32" in relocs) == native, (architecture, flags, relocs)
        if flags:
            assert "R_V850_PCR22" not in relocs, relocs
    print("PASS native far-call ISA gating and global long-call policy")


def main() -> int:
    # Outside the repository, including spaces, to exercise caller-relative inputs.
    with tempfile.TemporaryDirectory(prefix="rh850 payload ") as td:
        work = Path(td)
        (work / "offset.h").write_text("#define OFFSET 8u\n", encoding="utf-8")
        (work / "compute.c").write_text(
            '#include "offset.h"\nunsigned compute(unsigned x) { return x + OFFSET; }\n',
            encoding="utf-8",
        )
        (work / "entry.S").write_text(
            "    .section .text\n    .global _start\n_start:\n"
            "    mov 0x12345670, r6\n    jarl _compute, lp\n"
            "    mov 0x200, r11\n    st.w r10, 0[r11]\n"
            "    .global payload_stop\npayload_stop:\n    add 1, r12\n    br payload_stop\n"
            "    .global unreachable_stop\nunreachable_stop:\n    br unreachable_stop\n"
            '    .section .result,"aw"\n    .long 0\n', encoding="utf-8",
        )
        (work / "layout.ld").write_text(
            "SECTIONS { . = 0x100; .text : { *(.text) } "
            ". = 0x200; .result : { *(.result) } }\nENTRY(_start)\n", encoding="utf-8",
        )
        predicate = "*(unsigned int *)0x200 == 0x12345678"
        contract = ("--stop", "payload_stop", "--assert", predicate)
        invoke(
            work, "entry.S", "compute.c", "--linker-script", "layout.ld",
            "--output-dir", "result", *contract,
        )
        report = json.loads((work / "result/report.json").read_text())
        elf = work / "result/payload.elf"
        assert report["status"] == "passed"
        assert report["elf_sha256"] == hashlib.sha256(elf.read_bytes()).hexdigest()
        assert "RH850_CHECK_1=1" in (work / "result/output.txt").read_text()
        print("PASS caller-relative C/assembly build, exact ELF execution, and checked result")

        retained = ("result/payload.elf", "--output-dir", "rerun")
        invoke(work, *retained, success=False, error="requires --stop")
        invoke(work, *retained, "--stop", "payload_stop", success=False, error="requires a postcondition")
        invoke(work, *retained, "--stop", "0x100", "--assert", predicate,
               success=False, error="stop equals entry")
        invoke(work, *retained, "--stop", "payload_stop", "--assert", "*(unsigned int *)0x200 == 7",
               success=False, error="postcondition 1 failed")
        assert json.loads((work / "rerun/report.json").read_text())["status"] == "failed"
        invoke(work, *retained, *contract, "-ex", "starti",
               success=False, error="must execute run or continue")
        invoke(work, *retained, *contract, "-ex", "break *0x100", "-ex", "run",
               success=False, error="unexpected stop")
        invoke(work, *retained, "--stop", "unreachable_stop", "--assert", predicate,
               "--timeout", "0.2", success=False, error="timed out")
        print("PASS load-only, entry-only, false predicate, wrong stop, and nonterminating execution rejected")

        # A failed rebuild must not test the previous successful ELF or retain its verdict.
        (work / "compute.c").write_text("not valid C\n", encoding="utf-8")
        invoke(
            work, "entry.S", "compute.c", "--linker-script", "layout.ld",
            "--output-dir", "result", *contract, success=False, error="payload build failed",
        )
        failed = json.loads((work / "result/report.json").read_text())
        assert failed["status"] == "failed" and "elf_sha256" not in failed
        print("PASS failed rebuild cannot reuse a previous passing result")
        verify_bswap(work)
        verify_bit_tests(work)
        verify_far_calls(work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
