#!/usr/bin/env python3
"""Lift Camry RH850 functions whose bytes decode onto the symbol range.

Generated C is register-transfer code: one function per firmware function, with
the decoded operations as statements. Already-matched hand-written C stays the
checked entry for those symbols. A lifted function is listed only after every
full-return original-byte oracle passes.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from tools import REPO_ROOT
from tools.camry_decomp import ROOT, load_matched, load_symbols
from tools.project.analysis_target import target as resolve_target

LIFTED_C = ROOT / "src" / "lifted.c"

PUSH_BITS = (
    (27, 20), (26, 21), (25, 22), (24, 23),
    (31, 24), (30, 25), (29, 26), (28, 27),
    (23, 28), (22, 29), (0, 30), (21, 31),
)
PREPARE_SUB = {0x01, 0x03, 0x0B, 0x13, 0x1B}
CONTROL = {
    "b", "br", "jarl", "jarl_ind", "jr", "jmp", "jmpdisp", "loop", "switch", "dispose", "callt", "abort",
}


def sext(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    value &= (1 << bits) - 1
    return value - (sign << 1) if value & sign else value


def u16(image: bytes, addr: int) -> int:
    return image[addr] | (image[addr + 1] << 8)


def list_mask(hw0: int, hw1: int) -> int:
    word = hw0 | (hw1 << 16)
    mask = 0
    for bit, reg in PUSH_BITS:
        if (word >> bit) & 1:
            mask |= 1 << reg
    return mask


@dataclass
class Inst:
    addr: int
    size: int
    kind: str
    stmt: str = ""
    cc: int = 0
    target: int = 0
    link: int = 0
    reg: int = 0
    mask: int = 0
    slots: int = 0
    ret: int = 0
    imm: int = 0
    base: int = 0
    text: str = ""


def _need(image: bytes, addr: int, size: int) -> bool:
    return addr >= 0 and addr + size <= len(image)


def decode_at(image: bytes, addr: int) -> Inst | None:
    if not _need(image, addr, 2):
        return None
    hw0 = u16(image, addr)
    if hw0 == 0:
        return Inst(addr, 2, "nop", "/* nop */", text="nop")
    if hw0 in (0x001D, 0x001E, 0x001F):
        return Inst(addr, 2, "nop", "/* sync */", text="sync")
    if hw0 == 0x0040:
        return Inst(addr, 2, "abort", text="rie")
    if (hw0 >> 6) & 0x3FF == 0x008:
        return Inst(addr, 2, "callt", imm=hw0 & 0x3F, text=f"callt {hw0 & 0x3F}")
    if (hw0 & 0x87FF) == 0x0040 and ((hw0 >> 11) & 0xF) != 0:
        return Inst(addr, 2, "abort", text="fetrap")

    op0610 = (hw0 >> 6) & 0x1F
    op0615 = (hw0 >> 6) & 0x3FF
    if op0615 == 0x19 or op0610 == 0x1E:
        return _decode_group_1e(image, addr, hw0, op0615)

    op0515 = (hw0 >> 5) & 0x7FF
    op0510 = (hw0 >> 5) & 0x3F
    if op0515 in (0x017, 0x031, 0x037) or hw0 == 0x02E0 or op0510 >= 0x18:
        if not _need(image, addr, 4):
            return None
        hw1 = u16(image, addr + 2)
        if hw0 == 0x02E0 and (hw1 & 1) == 0:
            return _disp32(image, addr, hw0, hw1, "jr", 0)
        if op0515 == 0x017 and (hw1 & 1) == 0:
            return _disp32(image, addr, hw0, hw1, "jarl", hw0 & 0x1F)
        if op0515 == 0x031:
            return _mov32(image, addr, hw0)
        if op0515 == 0x037 and (hw1 & 1) == 0:
            return _jmp_disp32(image, addr, hw0, hw1)
        if op0515 == 0x037 and (hw1 & 1) == 1:
            return _loop(addr, hw0, hw1)
        if op0515 == 0x03F and (hw1 & 1) == 1:
            return _bcond17(addr, hw0, hw1)
        if op0510 >= 0x30:
            return _decode_fmt4(image, addr, hw0, hw1, op0510)
        if op0510 >= 0x18:
            return _decode_fmt2(addr, hw0)
    return _decode_fmt1(addr, hw0)


def _disp32(image: bytes, addr: int, hw0: int, hw1: int, kind: str, link: int) -> Inst | None:
    if not _need(image, addr, 6) or (hw1 & 1):
        return None
    hw2 = u16(image, addr + 4)
    rel = (hw2 << 16) | hw1
    target = (addr + rel) & 0xFFFFFFFF
    if kind == "jr":
        return Inst(addr, 6, "jr", target=target, text=f"jr {target:#x}")
    return Inst(addr, 6, "jarl", target=target, link=link, text=f"jarl {target:#x}, r{link}")


def _mov32(image: bytes, addr: int, hw0: int) -> Inst | None:
    if not _need(image, addr, 6):
        return None
    hw1 = u16(image, addr + 2)
    hw2 = u16(image, addr + 4)
    reg = hw0 & 0x1F
    imm = (hw2 << 16) | hw1
    return Inst(
        addr, 6, "alu",
        stmt=f"camry_movi({reg}, 0x{imm:x}u);",
        text=f"mov {imm:#x}, r{reg}",
    )


def _jmp_disp32(image: bytes, addr: int, hw0: int, hw1: int) -> Inst | None:
    if not _need(image, addr, 6):
        return None
    hw2 = u16(image, addr + 4)
    base = (hw2 << 16) | (hw1 & ~1)
    reg = hw0 & 0x1F
    return Inst(addr, 6, "jmpdisp", reg=reg, base=base, text=f"jmp {base:#x}[r{reg}]")


def _loop(addr: int, hw0: int, hw1: int) -> Inst:
    reg = hw0 & 0x1F
    rel = (hw1 >> 1) << 1
    target = (addr - rel) & 0xFFFFFFFF
    return Inst(addr, 4, "loop", reg=reg, target=target, text=f"loop r{reg}, {target:#x}")


def _bcond17(addr: int, hw0: int, hw1: int) -> Inst:
    cc = hw0 & 0xF
    sign = -1 if (hw0 >> 4) & 1 else 0
    rel = (sign << 16) | (hw1 & ~1)
    target = (addr + rel) & 0xFFFFFFFF
    kind = "br" if cc == 5 else "b"
    return Inst(addr, 4, kind, cc=cc, target=target, text=f"b{cc} {target:#x}")


def _decode_group_1e(image: bytes, addr: int, hw0: int, op0615: int) -> Inst | None:
    if not _need(image, addr, 4):
        return None
    hw1 = u16(image, addr + 2)
    if op0615 == 0x19:
        slots = (hw0 >> 1) & 0x1F
        ret = hw1 & 0x1F
        mask = list_mask(hw0, hw1)
        return Inst(
            addr, 4, "dispose", mask=mask, slots=slots, ret=ret,
            text=f"dispose {slots}, {mask:#x}, r{ret}",
        )
    sub = hw1 & 0x1F
    reg2 = (hw0 >> 11) & 0x1F
    if op0615 == 0x1E and sub in PREPARE_SUB:
        return _prepare(image, addr, hw0, hw1, sub)
    if (hw1 & 1) == 0 and reg2 == 0 and op0615 == 0x1E:
        rel = (sext(hw0 & 0x3F, 6) << 16) | hw1
        target = (addr + rel) & 0xFFFFFFFF
        return Inst(addr, 4, "jr", target=target, text=f"jr {target:#x}")
    if (hw1 & 1) == 0:
        rel = (sext(hw0 & 0x3F, 6) << 16) | hw1
        target = (addr + rel) & 0xFFFFFFFF
        link = reg2
        return Inst(addr, 4, "jarl", target=target, link=link, text=f"jarl {target:#x}, r{link}")
    disp23 = _try_disp23(image, addr, hw0, hw1)
    if disp23 is not None:
        return disp23
    disp = (sext(hw1 >> 1, 15) << 1) | ((hw0 >> 5) & 1)
    base = hw0 & 0x1F
    return Inst(
        addr, 4, "alu",
        stmt=f"camry_ld8u({reg2}, {base}, {disp});",
        text=f"ld.bu {disp}[r{base}], r{reg2}",
    )


def _prepare(image: bytes, addr: int, hw0: int, hw1: int, sub: int) -> Inst | None:
    slots = (hw0 >> 1) & 0x1F
    mask = list_mask(hw0, hw1)
    size = 4
    mode = 0
    imm = 0
    if sub == 0x03:
        mode = 1
    elif sub in (0x0B, 0x13):
        if not _need(image, addr, 6):
            return None
        size = 6
        imm = sext(u16(image, addr + 4), 16) & 0xFFFFFFFF
        mode = 2 if sub == 0x0B else 3
    elif sub == 0x1B:
        if not _need(image, addr, 8):
            return None
        size = 8
        imm = u16(image, addr + 4) | (u16(image, addr + 6) << 16)
        mode = 4
    return Inst(
        addr, size, "alu",
        stmt=f"camry_prepare(0x{mask:x}u, {slots}, {mode}, 0x{imm:x}u);",
        text=f"prepare {mask:#x}, {slots}, mode {mode}",
    )


def _try_disp23(image: bytes, addr: int, hw0: int, hw1: int) -> Inst | None:
    if (hw0 >> 6) & 0x3FF != 0x1E:
        return None
    if not _need(image, addr, 6):
        return None
    op0515 = (hw0 >> 5) & 0x7FF
    if op0515 not in (0x03C, 0x03D):
        return None
    hw2 = u16(image, addr + 4)
    op1620 = hw1 & 0x1F
    op1619 = hw1 & 0xF
    op2126 = (hw1 >> 5) & 0x3F
    op2026 = (hw1 >> 4) & 0x7F
    reg3 = (hw1 >> 11) & 0x1F
    reg1 = hw0 & 0x1F
    simm = sext(hw2, 16)
    if op0515 == 0x03C and op1620 == 7:
        disp = (simm << 7) | (op2126 << 1)
        stmt = f"camry_ld16s({reg3}, {reg1}, {disp});"
        text = "ld.h"
    elif op0515 == 0x03C and op1620 == 9:
        disp = (simm << 7) | (op2126 << 1)
        stmt = f"camry_ld32({reg3}, {reg1}, {disp});"
        text = "ld.w"
    elif op0515 == 0x03C and op1620 == 0xF:
        disp = (simm << 7) | (op2126 << 1)
        stmt = f"camry_st32({reg3}, {reg1}, {disp});"
        text = "st.w"
    elif op0515 == 0x03C and op1619 == 5:
        disp = (simm << 7) | op2026
        stmt = f"camry_ld8s({reg3}, {reg1}, {disp});"
        text = "ld.b"
    elif op0515 == 0x03C and op1619 == 0xD:
        disp = (simm << 7) | op2026
        stmt = f"camry_st8({reg3}, {reg1}, {disp});"
        text = "st.b"
    elif op0515 == 0x03D and op1619 == 5:
        disp = (simm << 7) | op2026
        stmt = f"camry_ld8u({reg3}, {reg1}, {disp});"
        text = "ld.bu"
    elif op0515 == 0x03D and op1619 == 7:
        disp = (simm << 7) | op2026
        stmt = f"camry_ld16u({reg3}, {reg1}, {disp});"
        text = "ld.hu"
    elif op0515 == 0x03D and op1620 == 0xD:
        disp = (simm << 7) | (op2126 << 1)
        stmt = f"camry_st16({reg3}, {reg1}, {disp});"
        text = "st.h"
    else:
        return None
    return Inst(addr, 6, "alu", stmt=stmt, text=f"{text} {disp}[r{reg1}], r{reg3}")


def _decode_fmt2(addr: int, hw0: int) -> Inst | None:
    op = (hw0 >> 7) & 0xF
    reg = (hw0 >> 11) & 0x1F
    low7 = hw0 & 0x7F
    if op == 0x6:
        return Inst(addr, 2, "alu", stmt=f"camry_ld8s({reg}, 30, {low7});", text=f"sld.b {low7}[ep], r{reg}")
    if op == 0x7:
        return Inst(addr, 2, "alu", stmt=f"camry_st8({reg}, 30, {low7});", text=f"sst.b {low7}[ep], r{reg}")
    if op == 0x8:
        return Inst(addr, 2, "alu", stmt=f"camry_ld16s({reg}, 30, {low7 * 2});", text=f"sld.h {low7 * 2}[ep], r{reg}")
    if op == 0x9:
        return Inst(addr, 2, "alu", stmt=f"camry_st16({reg}, 30, {low7 * 2});", text=f"sst.h {low7 * 2}[ep], r{reg}")
    if op == 0xA:
        disp = ((hw0 >> 1) & 0x3F) * 4
        if hw0 & 1:
            return Inst(addr, 2, "alu", stmt=f"camry_st32({reg}, 30, {disp});", text=f"sst.w {disp}[ep], r{reg}")
        return Inst(addr, 2, "alu", stmt=f"camry_ld32({reg}, 30, {disp});", text=f"sld.w {disp}[ep], r{reg}")
    if op == 0xB:
        rel = (sext((hw0 >> 11) & 0x1F, 5) << 4) | (((hw0 >> 4) & 7) << 1)
        target = (addr + rel) & 0xFFFFFFFF
        cc = hw0 & 0xF
        kind = "br" if cc == 5 else "b"
        return Inst(addr, 2, kind, cc=cc, target=target, text=f"b{cc:x} {target:#x}")
    return None


def _decode_fmt1(addr: int, hw0: int) -> Inst | None:
    reg1 = hw0 & 0x1F
    reg2 = (hw0 >> 11) & 0x1F
    op = (hw0 >> 5) & 0x3F
    bit4 = (hw0 >> 4) & 1
    imm5 = sext(reg1, 5)
    if op == 2 and reg2 == 0:
        return Inst(addr, 2, "switch", reg=reg1, text=f"switch r{reg1}")
    if op == 3 and reg2 == 0:
        return Inst(addr, 2, "jmp", reg=reg1, text=f"jmp [r{reg1}]")
    if op == 3 and reg2 != 0 and bit4 == 0:
        return Inst(addr, 2, "alu", stmt=f"camry_ld8u({reg2}, 30, {reg1 & 0xF});", text=f"sld.bu {reg1 & 0xF}[ep], r{reg2}")
    if op == 3 and reg2 != 0 and bit4 == 1:
        return Inst(addr, 2, "alu", stmt=f"camry_ld16u({reg2}, 30, {(reg1 & 0xF) * 2});", text=f"sld.hu {(reg1 & 0xF) * 2}[ep], r{reg2}")
    if op == 4 and reg2 == 0:
        return Inst(addr, 2, "alu", stmt=f"camry_zxb({reg1});", text=f"zxb r{reg1}")
    if op == 5 and reg2 == 0:
        return Inst(addr, 2, "alu", stmt=f"camry_sxb({reg1});", text=f"sxb r{reg1}")
    if op == 6 and reg2 == 0:
        return Inst(addr, 2, "alu", stmt=f"camry_zxh({reg1});", text=f"zxh r{reg1}")
    if op == 7 and reg2 == 0:
        return Inst(addr, 2, "alu", stmt=f"camry_sxh({reg1});", text=f"sxh r{reg1}")
    stmt = _fmt1_stmt(op, reg1, reg2, imm5)
    if stmt is None:
        return None
    return Inst(addr, 2, "alu", stmt=stmt, text=stmt)


def _fmt1_stmt(op: int, reg1: int, reg2: int, imm5: int) -> str | None:
    if op == 0x00:
        return f"camry_mov({reg2}, {reg1});"
    if op == 0x01:
        return f"camry_not({reg2}, {reg1});"
    if op == 0x02:
        return f"camry_divh2({reg2}, {reg1});"
    if op == 0x04:
        return f"camry_satsubr({reg2}, {reg1});"
    if op == 0x05:
        return f"camry_satsub({reg2}, {reg1});"
    if op == 0x06:
        return f"camry_satadd({reg2}, {reg1});"
    if op == 0x07:
        return f"camry_mulh({reg2}, {reg1});"
    if op == 0x08:
        return f"camry_or({reg2}, {reg1});"
    if op == 0x09:
        return f"camry_xor({reg2}, {reg1});"
    if op == 0x0A:
        return f"camry_and({reg2}, {reg1});"
    if op == 0x0B:
        return f"camry_tst({reg2}, {reg1});"
    if op == 0x0C:
        return f"camry_subr({reg2}, {reg1});"
    if op == 0x0D:
        return f"camry_sub({reg2}, {reg1});"
    if op == 0x0E:
        return f"camry_add({reg2}, {reg1});"
    if op == 0x0F:
        return f"camry_cmp({reg2}, {reg1});"
    if op == 0x10:
        return f"camry_movi({reg2}, {imm5 & 0xFFFFFFFF:#x}u);"
    if op == 0x11 and reg2 != 0:
        return f"camry_sataddi({reg2}, {imm5});"
    if op == 0x12:
        return f"camry_addi_imm5({reg2}, {imm5});"
    if op == 0x13:
        return f"camry_cmpi({reg2}, {imm5});"
    if op == 0x14:
        return f"camry_shr({reg2}, rr_amount({reg1}));".replace(f"rr_amount({reg1})", str(reg1))
    if op == 0x15:
        return f"camry_sar_imm({reg2}, {reg1});"
    if op == 0x16:
        return f"camry_shl_imm({reg2}, {reg1});"
    if op == 0x17:
        return f"camry_mulhi5({reg2}, {imm5});"
    if op == 0x14:
        return None
    return None


def _decode_fmt4(image: bytes, addr: int, hw0: int, hw1: int, op: int) -> Inst | None:
    reg1 = hw0 & 0x1F
    reg2 = (hw0 >> 11) & 0x1F
    reg3 = (hw1 >> 11) & 0x1F
    simm = sext(hw1, 16)
    if op == 0x30:
        return Inst(addr, 4, "alu", stmt=f"camry_addi({reg2}, {reg1}, {simm});", text=f"addi {simm}, r{reg1}, r{reg2}")
    if op == 0x31 and reg2 != 0:
        return Inst(addr, 4, "alu", stmt=f"camry_movea({reg2}, {reg1}, {simm});", text=f"movea {simm}, r{reg1}, r{reg2}")
    if op == 0x32 and reg2 != 0:
        return Inst(addr, 4, "alu", stmt=f"camry_movhi({reg2}, {reg1}, {simm});", text=f"movhi {simm}, r{reg1}, r{reg2}")
    if op == 0x33 and reg2 != 0:
        return Inst(addr, 4, "alu", stmt=f"camry_satsubi({reg2}, {reg1}, {simm});", text="satsubi")
    if op == 0x34:
        return Inst(addr, 4, "alu", stmt=f"camry_ori({reg2}, {reg1}, 0x{hw1:x}u);", text=f"ori {hw1:#x}, r{reg1}, r{reg2}")
    if op == 0x35:
        return Inst(addr, 4, "alu", stmt=f"camry_xori({reg2}, {reg1}, 0x{hw1:x}u);", text=f"xori {hw1:#x}, r{reg1}, r{reg2}")
    if op == 0x36:
        return Inst(addr, 4, "alu", stmt=f"camry_andi({reg2}, {reg1}, 0x{hw1:x}u);", text=f"andi {hw1:#x}, r{reg1}, r{reg2}")
    if op == 0x37 and reg2 != 0:
        return Inst(addr, 4, "alu", stmt=f"camry_mulhi({reg2}, {reg1}, {simm});", text=f"mulhi {simm}, r{reg1}, r{reg2}")
    if op == 0x38:
        return Inst(addr, 4, "alu", stmt=f"camry_ld8s({reg2}, {reg1}, {simm});", text=f"ld.b {simm}[r{reg1}], r{reg2}")
    if op == 0x39 and (hw1 & 1) == 0:
        return Inst(addr, 4, "alu", stmt=f"camry_ld16s({reg2}, {reg1}, {simm});", text=f"ld.h {simm}[r{reg1}], r{reg2}")
    if op == 0x39 and (hw1 & 1) == 1:
        disp = sext(hw1 >> 1, 15) << 1
        return Inst(addr, 4, "alu", stmt=f"camry_ld32({reg2}, {reg1}, {disp});", text=f"ld.w {disp}[r{reg1}], r{reg2}")
    if op == 0x3A:
        return Inst(addr, 4, "alu", stmt=f"camry_st8({reg2}, {reg1}, {simm});", text=f"st.b r{reg2}, {simm}[r{reg1}]")
    if op == 0x3B and (hw1 & 1) == 0:
        return Inst(addr, 4, "alu", stmt=f"camry_st16({reg2}, {reg1}, {simm});", text=f"st.h r{reg2}, {simm}[r{reg1}]")
    if op == 0x3B and (hw1 & 1) == 1:
        disp = sext(hw1 >> 1, 15) << 1
        return Inst(addr, 4, "alu", stmt=f"camry_st32({reg2}, {reg1}, {disp});", text=f"st.w r{reg2}, {disp}[r{reg1}]")
    if op == 0x3E:
        return _decode_bit(addr, hw0, hw1, reg1, simm)
    if op == 0x3F:
        return _decode_3f(addr, hw0, hw1, reg1, reg2, reg3)
    return None


def _decode_bit(addr: int, hw0: int, hw1: int, reg1: int, simm: int) -> Inst | None:
    sub = (hw0 >> 14) & 3
    bit = (hw0 >> 11) & 7
    names = ("camry_set1", "camry_not1", "camry_clr1", "camry_tst1")
    return Inst(addr, 4, "alu", stmt=f"{names[sub]}({reg1}, {simm}, {bit});", text=f"bit{sub} {bit}, {simm}[r{reg1}]")


def _decode_3f(addr: int, hw0: int, hw1: int, reg1: int, reg2: int, reg3: int) -> Inst | None:
    op0515 = (hw0 >> 5) & 0x7FF
    if (hw1 & 0x7FF) == 0x160 and op0515 == 0x63F:
        return Inst(addr, 4, "jarl_ind", reg=reg1, link=reg3, text=f"jarl [r{reg1}], r{reg3}")
    if (hw1 & 0x7FF) == 0x160 and op0515 == 0x23F:
        return Inst(addr, 4, "alu", stmt=f"camry_pushsp({reg1}, {reg3});", text=f"pushsp r{reg1}, r{reg3}")
    if (hw1 & 0x7FF) == 0x160 and op0515 == 0x33F:
        return Inst(addr, 4, "alu", stmt=f"camry_popsp({reg1}, {reg3});", text=f"popsp r{reg1}, r{reg3}")
    if (hw1 & 0x7FF) == 0x160 and ((hw0 >> 13) & 7) == 7:
        return Inst(addr, 4, "nop", "/* cache */", text="cache")
    if op0515 == 0x6FF and (hw1 & 0x7FF) == 0x160:
        return Inst(addr, 4, "nop", "/* pref */", text="pref")
    if ((hw0 >> 4) & 0x7F) == 0x7E and hw1 == 0:
        return Inst(addr, 4, "alu", stmt=f"camry_setf({reg2}, {hw0 & 0xF});", text=f"setf {hw0 & 0xF}, r{reg2}")
    if ((hw0 >> 4) & 0x7F) == 0x7E and hw1 == 0x0200:
        return Inst(addr, 4, "alu", stmt=f"camry_sasf({reg2}, {hw0 & 0xF});", text=f"sasf {hw0 & 0xF}, r{reg2}")
    if hw0 in (0x07E0, 0x87E0) and hw1 == 0x0160:
        return Inst(addr, 4, "nop", "/* ei/di */", text="ei" if hw0 == 0x87E0 else "di")
    if (hw1 & 1) == 1:
        disp = sext(hw1 >> 1, 15) << 1
        return Inst(addr, 4, "alu", stmt=f"camry_ld16u({reg2}, {reg1}, {disp});", text=f"ld.hu {disp}[r{reg1}], r{reg2}")
    op2126 = (hw1 >> 5) & 0x3F
    op2226 = (hw1 >> 6) & 0x1F
    op1626 = hw1 & 0x7FF
    cc = (hw1 >> 1) & 0xF
    if (hw0 & 0x7FF) == 0x7E0 and op1626 in (0x340, 0x342, 0x344, 0x346, 0x360, 0x362, 0x364, 0x366):
        name = {
            0x340: "camry_bsw", 0x342: "camry_bsh", 0x344: "camry_hsw", 0x346: "camry_hsh",
            0x360: "camry_sch0r", 0x362: "camry_sch1r", 0x364: "camry_sch0l", 0x366: "camry_sch1l",
        }[op1626]
        return Inst(addr, 4, "alu", stmt=f"{name}({reg2}, {reg3});", text=name)
    if op2126 == 0x18 and (hw1 & 1) == 0:
        imm = sext(reg1, 5)
        return Inst(addr, 4, "alu", stmt=f"camry_cmovi({reg3}, {reg2}, {imm}, {cc});", text=f"cmov {cc}, {imm}, r{reg2}, r{reg3}")
    if op2126 == 0x19 and (hw1 & 1) == 0:
        return Inst(addr, 4, "alu", stmt=f"camry_cmov({reg3}, {reg2}, {reg1}, {cc});", text=f"cmov {cc}, r{reg1}, r{reg2}, r{reg3}")
    if op2126 == 0x1C and (hw1 & 1) == 0:
        return Inst(addr, 4, "alu", stmt=f"camry_sbf({reg3}, {reg1}, {reg2}, {cc});", text="sbf")
    if op2126 == 0x1D and (hw1 & 1) == 0:
        return Inst(addr, 4, "alu", stmt=f"camry_adf({reg3}, {reg1}, {reg2}, {cc});", text="adf")
    if op2226 == 9 and (hw1 & 3) == 0:
        imm = (sext((hw1 >> 2) & 0xF, 4) << 5) | reg1
        return Inst(addr, 4, "alu", stmt=f"camry_muli({reg2}, {reg3}, {imm});", text=f"mul {imm}, r{reg2}, r{reg3}")
    if op2226 == 9 and (hw1 & 3) == 2:
        imm = (((hw1 >> 2) & 0xF) << 5) | reg1
        return Inst(addr, 4, "alu", stmt=f"camry_mului({reg2}, {reg3}, {imm});", text=f"mulu {imm}, r{reg2}, r{reg3}")
    simple = {
        0x020: f"camry_ldsr({reg1}, {reg2}, 0);",
        0x040: f"camry_stsr({reg2}, {reg1}, 0);",
        0x080: f"camry_shr_reg({reg2}, {reg2}, {reg1});",
        0x0A0: f"camry_sar_reg({reg2}, {reg2}, {reg1});",
        0x0C0: f"camry_shl_reg({reg2}, {reg2}, {reg1});",
        0x0E0: f"camry_set1r({reg1}, {reg2});",
        0x0E2: f"camry_not1r({reg1}, {reg2});",
        0x0E4: f"camry_clr1r({reg1}, {reg2});",
        0x0E6: f"camry_tst1r({reg1}, {reg2});",
        0x082: f"camry_shr_reg({reg3}, {reg2}, {reg1});",
        0x0A2: f"camry_sar_reg({reg3}, {reg2}, {reg1});",
        0x0C2: f"camry_shl_reg({reg3}, {reg2}, {reg1});",
        0x220: f"camry_mul({reg2}, {reg3}, {reg2}, {reg1}, 1);",
        0x222: f"camry_mul({reg2}, {reg3}, {reg2}, {reg1}, 0);",
        0x280: f"camry_div3({reg2}, {reg1}, {reg3}, 1, 1);",
        0x282: f"camry_div3({reg2}, {reg1}, {reg3}, 0, 1);",
        0x2C0: f"camry_div3({reg2}, {reg1}, {reg3}, 1, 0);",
        0x2C2: f"camry_div3({reg2}, {reg1}, {reg3}, 0, 0);",
        0x2FC: f"camry_div3({reg2}, {reg1}, {reg3}, 1, 0);",
        0x2FE: f"camry_div3({reg2}, {reg1}, {reg3}, 0, 0);",
        0x39A: f"camry_satsub3({reg3}, {reg2}, {reg1});",
        0x3BA: f"camry_satadd3({reg3}, {reg2}, {reg1});",
    }
    if hw1 in simple and op1626 == hw1:
        return Inst(addr, 4, "alu", stmt=simple[hw1], text=f"op3f {hw1:#x}")
    if op1626 == 0x20:
        return Inst(addr, 4, "alu", stmt=f"camry_ldsr({reg1}, {reg2}, {reg3});", text=f"ldsr r{reg1}, sr{reg2}, {reg3}")
    if op1626 == 0x40:
        return Inst(addr, 4, "alu", stmt=f"camry_stsr({reg2}, {reg1}, {reg3});", text=f"stsr sr{reg1}, r{reg2}, {reg3}")
    if op1626 in (0x220, 0x222, 0x280, 0x282, 0x2C0, 0x2C2, 0x2FC, 0x2FE, 0x082, 0x0A2, 0x0C2, 0x39A, 0x3BA):
        return Inst(addr, 4, "alu", stmt=simple[op1626], text=f"op3f {op1626:#x}")
    return None


def walk_range(image: bytes, start: int, end: int) -> list[Inst] | None:
    pc = start
    insts: list[Inst] = []
    while pc <= end:
        inst = decode_at(image, pc)
        if inst is None or pc + inst.size - 1 > end:
            return None
        insts.append(inst)
        pc += inst.size
    if pc != end + 1:
        return None
    return insts


@dataclass
class LiftedFn:
    entry: int
    name: str
    ranges: list[tuple[int, int]]
    insts: list[Inst]
    calls: set[int] = field(default_factory=set)
    sites: set[int] = field(default_factory=set)


def walk_symbol(image: bytes, row: dict) -> LiftedFn | None:
    entry = int(row["addr"], 16)
    ranges = [(start, end) for start, end in row["ranges"]]
    if not ranges or any(start >= len(image) or end >= len(image) for start, end in ranges):
        return None
    insts: list[Inst] = []
    for start, end in ranges:
        walked = walk_range(image, start, end)
        if walked is None:
            return None
        insts.extend(walked)
    sites = {inst.addr for inst in insts}
    if entry not in sites:
        return None
    return LiftedFn(entry, row["name"], ranges, insts, sites=sites)


def direct_targets(fn: LiftedFn) -> set[int]:
    targets = set()
    for inst in fn.insts:
        if inst.kind in {"jarl", "jr", "b", "br"} and inst.target not in fn.sites:
            targets.add(inst.target)
    return targets


def load_image() -> bytes:
    metadata = resolve_target("camry-8965F3307000")[1]
    image = (REPO_ROOT / metadata["codeflash"]).read_bytes()
    return image


def first_failure(image: bytes, row: dict) -> tuple[int, int, int, int] | None:
    for start, end in row["ranges"]:
        if start >= len(image) or end >= len(image):
            return None
        pc = start
        while pc <= end:
            inst = decode_at(image, pc)
            if inst is None or pc + inst.size - 1 > end:
                hw0 = u16(image, pc) if pc + 2 <= len(image) else 0
                hw1 = u16(image, pc + 2) if pc + 4 <= len(image) else 0
                return pc, hw0, hw1, (hw0 >> 5) & 0x3F
            pc += inst.size
    return None


def decode_all(image: bytes, symbols: list[dict]) -> tuple[dict[int, LiftedFn], Counter]:
    decoded: dict[int, LiftedFn] = {}
    unknown: Counter = Counter()
    for row in symbols:
        fn = walk_symbol(image, row)
        if fn is None:
            failed = first_failure(image, row)
            if failed is not None:
                _pc, hw0, hw1, op = failed
                unknown[(hw0, hw1, op)] += 1
            continue
        fn.calls = direct_targets(fn)
        decoded[fn.entry] = fn
    return decoded, unknown


def liftable_set(decoded: dict[int, LiftedFn]) -> set[int]:
    entries = set(decoded)
    changed = True
    while changed:
        changed = False
        for entry, fn in list(decoded.items()):
            if entry not in entries:
                continue
            if any(target not in entries for target in fn.calls):
                entries.remove(entry)
                changed = True
    return entries


def useful_oracle(scenario: dict) -> bool:
    checks = scenario.get("checks") or []
    has_r10 = any(check.get("kind") == "register" and check.get("register") == "r10" for check in checks)
    has_memory = any(check.get("kind") == "memory" for check in checks)
    has_event = any(check.get("kind") == "event-count" for check in checks)
    if has_event and not has_r10:
        return False
    return has_memory or has_r10


def oracle_blocked(scenario: dict) -> bool:
    registers = scenario.get("registers") or {}
    lp = int(registers.get("lp", "0"), 16)
    stops = {int(value, 16) for value in scenario.get("stop_addresses") or []}
    if stops != {lp}:
        return True
    for check in scenario.get("checks") or []:
        if check.get("kind") != "register":
            continue
        register = check.get("register")
        if register in {"r10", "sp", "PC"}:
            continue
        expected = int(check["equals"], 16)
        actual = int(registers.get(register, "0"), 16)
        if actual != expected:
            return True
    return False


def candidate_entries(oracles: list[dict], matched: set[int], liftable: set[int]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = {}
    for scenario in oracles:
        entry = scenario.get("entry") or {}
        if entry.get("scope") != "resolved-address":
            continue
        address = int(entry["address"], 16)
        grouped.setdefault(address, []).append(scenario)
    chosen: dict[int, list[dict]] = {}
    for address, scenarios in grouped.items():
        if address in matched or address not in liftable:
            continue
        useful = [scenario for scenario in scenarios if useful_oracle(scenario)]
        if not useful or any(oracle_blocked(scenario) for scenario in useful):
            continue
        chosen[address] = useful
    return chosen


def closure_of(seeds: set[int], decoded: dict[int, LiftedFn], liftable: set[int]) -> set[int]:
    seen = set()
    stack = [seed for seed in seeds if seed in liftable]
    while stack:
        entry = stack.pop()
        if entry in seen:
            continue
        seen.add(entry)
        for target in decoded[entry].calls:
            if target in liftable and target not in seen:
                stack.append(target)
    return seen


def fn_symbol(entry: int) -> str:
    return f"camry_fn_{entry:08x}"


RUNTIME = r"""
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "camry.h"

extern uint32_t camry_sp;

uint32_t camry_R[32];
uint32_t camry_CY, camry_Z, camry_S, camry_OV, camry_SAT;
uint32_t camry_step_limit = 2000000;
uint32_t camry_steps;
static uint32_t camry_SR[8][32];

static uint32_t rr(int reg) {
    return reg ? camry_R[reg] : 0;
}

static void wr(int reg, uint32_t value) {
    if (reg)
        camry_R[reg] = value;
}

static void set_sz_keep_cy(uint32_t value) {
    camry_OV = 0;
    camry_S = value >> 31;
    camry_Z = value == 0;
}

static void flags_add(uint32_t left, uint32_t right) {
    uint64_t wide = (uint64_t)left + right;
    uint32_t result = (uint32_t)wide;
    uint32_t sign_l = left >> 31;
    uint32_t sign_r = right >> 31;
    uint32_t sign_o = result >> 31;
    camry_OV = (sign_l == sign_r) && (sign_r != sign_o);
    camry_CY = (uint32_t)(wide >> 32);
    camry_S = sign_o;
    camry_Z = result == 0;
}

static void flags_sub(uint32_t left, uint32_t right) {
    uint32_t result = left - right;
    uint32_t sign_l = left >> 31;
    uint32_t sign_r = right >> 31;
    uint32_t sign_o = result >> 31;
    camry_OV = (sign_l != sign_r) && (sign_r == sign_o);
    camry_CY = left < right;
    camry_S = sign_o;
    camry_Z = result == 0;
}

static int camry_take(int cc) {
    uint32_t z = camry_Z, s = camry_S, ov = camry_OV, cy = camry_CY;
    switch (cc & 0xF) {
    case 0x0: return ov;
    case 0x1: return cy;
    case 0x2: return z;
    case 0x3: return cy || z;
    case 0x4: return s;
    case 0x5: return 1;
    case 0x6: return s ^ ov;
    case 0x7: return (s ^ ov) || z;
    case 0x8: return !ov;
    case 0x9: return !cy;
    case 0xA: return !z;
    case 0xB: return !(cy || z);
    case 0xC: return !s;
    case 0xD: return camry_SAT;
    case 0xE: return !(s ^ ov);
    default: return !((s ^ ov) || z);
    }
}

static void camry_step(void) {
    if (++camry_steps > camry_step_limit) {
        fprintf(stderr, "camry lift step limit at r10=%#x\n", camry_R[10]);
        abort();
    }
}

static uint32_t clamp_sat(int64_t value) {
    if (value > 0x7fffffffLL) {
        camry_SAT = 1;
        return 0x7fffffffu;
    }
    if (value < -0x80000000LL) {
        camry_SAT = 1;
        return 0x80000000u;
    }
    if (camry_OV)
        camry_SAT = 1;
    return (uint32_t)value;
}

void camry_mov(int dst, int src) { wr(dst, rr(src)); }
void camry_movi(int dst, uint32_t imm) { wr(dst, imm); }
void camry_movea(int dst, int src, int32_t imm) { wr(dst, rr(src) + (uint32_t)imm); }
void camry_movhi(int dst, int src, int32_t imm) { wr(dst, rr(src) + ((uint32_t)imm << 16)); }
void camry_not(int dst, int src) { uint32_t value = ~rr(src); set_sz_keep_cy(value); wr(dst, value); }
void camry_or(int dst, int src) { uint32_t value = rr(dst) | rr(src); set_sz_keep_cy(value); wr(dst, value); }
void camry_xor(int dst, int src) { uint32_t value = rr(dst) ^ rr(src); set_sz_keep_cy(value); wr(dst, value); }
void camry_and(int dst, int src) { uint32_t value = rr(dst) & rr(src); set_sz_keep_cy(value); wr(dst, value); }
void camry_tst(int dst, int src) { set_sz_keep_cy(rr(dst) & rr(src)); }
void camry_add(int dst, int src) { uint32_t left = rr(dst), right = rr(src); flags_add(left, right); wr(dst, left + right); }
void camry_sub(int dst, int src) { uint32_t left = rr(dst), right = rr(src); flags_sub(left, right); wr(dst, left - right); }
void camry_subr(int dst, int src) { uint32_t left = rr(src), right = rr(dst); flags_sub(left, right); wr(dst, left - right); }
void camry_cmp(int dst, int src) { flags_sub(rr(dst), rr(src)); }
void camry_addi(int dst, int src, int32_t imm) { uint32_t left = rr(src), right = (uint32_t)imm; flags_add(left, right); wr(dst, left + right); }
void camry_addi_imm5(int dst, int32_t imm) { camry_addi(dst, dst, imm); }
void camry_cmpi(int dst, int32_t imm) { flags_sub(rr(dst), (uint32_t)imm); }
void camry_ori(int dst, int src, uint32_t imm) { uint32_t value = rr(src) | imm; set_sz_keep_cy(value); wr(dst, value); }
void camry_xori(int dst, int src, uint32_t imm) { uint32_t value = rr(src) ^ imm; set_sz_keep_cy(value); wr(dst, value); }
void camry_andi(int dst, int src, uint32_t imm) { uint32_t value = rr(src) & imm; set_sz_keep_cy(value); wr(dst, value); }

static void shift_left(int dst, uint32_t value, uint32_t amount) {
    amount &= 31u;
    uint32_t result = value << amount;
    camry_OV = 0;
    camry_S = result >> 31;
    camry_Z = result == 0;
    camry_CY = amount == 0 ? 0 : (value >> (32u - amount)) & 1u;
    wr(dst, result);
}

static void shift_right(int dst, uint32_t value, uint32_t amount, int arithmetic) {
    amount &= 31u;
    uint32_t result = amount == 0 ? value : (arithmetic ? (uint32_t)((int32_t)value >> amount) : value >> amount);
    camry_OV = 0;
    camry_S = result >> 31;
    camry_Z = result == 0;
    camry_CY = amount == 0 ? 0 : (value >> (amount - 1u)) & 1u;
    wr(dst, result);
}

void camry_shl_imm(int dst, uint32_t amount) { shift_left(dst, rr(dst), amount); }
void camry_shr(int dst, uint32_t amount) { shift_right(dst, rr(dst), amount, 0); }
void camry_sar_imm(int dst, uint32_t amount) { shift_right(dst, rr(dst), amount, 1); }
void camry_shl_reg(int dst, int src, int amount) { shift_left(dst, rr(src), rr(amount)); }
void camry_shr_reg(int dst, int src, int amount) { shift_right(dst, rr(src), rr(amount), 0); }
void camry_sar_reg(int dst, int src, int amount) { shift_right(dst, rr(src), rr(amount), 1); }
void camry_zxb(int reg) { wr(reg, rr(reg) & 0xffu); }
void camry_zxh(int reg) { wr(reg, rr(reg) & 0xffffu); }
void camry_sxb(int reg) { wr(reg, (uint32_t)(int32_t)(int8_t)rr(reg)); }
void camry_sxh(int reg) { wr(reg, (uint32_t)(int32_t)(int16_t)rr(reg)); }
void camry_setf(int dst, int cc) { wr(dst, camry_take(cc) ? 1u : 0u); }
void camry_sasf(int dst, int cc) { wr(dst, (rr(dst) << 1) | (camry_take(cc) ? 1u : 0u)); }
void camry_cmovi(int dst, int fallback, int32_t imm, int cc) { wr(dst, camry_take(cc) ? (uint32_t)imm : rr(fallback)); }
void camry_cmov(int dst, int fallback, int taken, int cc) { wr(dst, camry_take(cc) ? rr(taken) : rr(fallback)); }

void camry_sbf(int dst, int src, int other, int cc) {
    uint32_t lsb = camry_take(cc) ? 1u : 0u;
    uint32_t left = rr(other);
    uint32_t right = rr(src);
    uint32_t result = left - right - lsb;
    camry_S = result >> 31;
    camry_Z = result == 0;
    camry_OV = ((right >> 31) != (left >> 31)) && ((left >> 31) == (result >> 31));
    camry_CY = left < right + lsb;
    wr(dst, result);
}

void camry_adf(int dst, int src, int other, int cc) {
    uint32_t lsb = camry_take(cc) ? 1u : 0u;
    uint32_t left = rr(other);
    uint32_t right = rr(src);
    uint64_t wide = (uint64_t)left + right + lsb;
    uint32_t result = (uint32_t)wide;
    camry_S = result >> 31;
    camry_Z = result == 0;
    camry_CY = wide >> 32 ? 1u : 0u;
    camry_OV = ((right >> 31) == (left >> 31)) && ((left >> 31) != (result >> 31));
    wr(dst, result);
}

static uint32_t addr_of(int base, int32_t disp) { return rr(base) + (uint32_t)disp; }
void camry_ld8s(int dst, int base, int32_t disp) { wr(dst, (uint32_t)(int32_t)(int8_t)camry_read8(addr_of(base, disp))); }
void camry_ld8u(int dst, int base, int32_t disp) { wr(dst, camry_read8(addr_of(base, disp))); }
void camry_ld16s(int dst, int base, int32_t disp) { wr(dst, (uint32_t)(int32_t)(int16_t)camry_read16(addr_of(base, disp))); }
void camry_ld16u(int dst, int base, int32_t disp) { wr(dst, camry_read16(addr_of(base, disp))); }
void camry_ld32(int dst, int base, int32_t disp) { wr(dst, camry_read32(addr_of(base, disp))); }
void camry_st8(int src, int base, int32_t disp) { camry_write8(addr_of(base, disp), rr(src)); }
void camry_st16(int src, int base, int32_t disp) { camry_write16(addr_of(base, disp), rr(src)); }
void camry_st32(int src, int base, int32_t disp) { camry_write32(addr_of(base, disp), rr(src)); }

static void bit_op(int base, int32_t disp, int bit, int kind) {
    uint32_t address = addr_of(base, disp);
    uint32_t value = camry_read8(address);
    uint32_t mask = 1u << (bit & 7);
    camry_Z = (value & mask) == 0;
    if (kind == 0) camry_write8(address, value | mask);
    else if (kind == 1) camry_write8(address, value ^ mask);
    else if (kind == 2) camry_write8(address, value & ~mask);
}
void camry_set1(int base, int32_t disp, int bit) { bit_op(base, disp, bit, 0); }
void camry_not1(int base, int32_t disp, int bit) { bit_op(base, disp, bit, 1); }
void camry_clr1(int base, int32_t disp, int bit) { bit_op(base, disp, bit, 2); }
void camry_tst1(int base, int32_t disp, int bit) { bit_op(base, disp, bit, 3); }
void camry_set1r(int base, int bitreg) { bit_op(base, 0, (int)(rr(bitreg) & 7u), 0); }
void camry_not1r(int base, int bitreg) { bit_op(base, 0, (int)(rr(bitreg) & 7u), 1); }
void camry_clr1r(int base, int bitreg) { bit_op(base, 0, (int)(rr(bitreg) & 7u), 2); }
void camry_tst1r(int base, int bitreg) { bit_op(base, 0, (int)(rr(bitreg) & 7u), 3); }

void camry_prepare(uint32_t regs, int slots, int mode, uint32_t imm) {
    static const int order[12] = {20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31};
    int index;
    for (index = 0; index < 12; index += 1) {
        if (regs & (1u << order[index])) {
            camry_R[3] -= 4u;
            camry_write32(camry_R[3], rr(order[index]));
        }
    }
    camry_R[3] -= (uint32_t)slots << 2;
    if (mode == 1) camry_R[30] = camry_R[3];
    else if (mode == 2) camry_R[30] = imm;
    else if (mode == 3) camry_R[30] = imm << 16;
    else if (mode == 4) camry_R[30] = imm;
}

void camry_sp_add(uint32_t bytes) { camry_R[3] += bytes; }
void camry_pop(int reg) { wr(reg, camry_read32(camry_R[3])); camry_R[3] += 4u; }

void camry_mul(int lo, int hi, int left_reg, int right_reg, int is_signed) {
    uint32_t left = rr(left_reg);
    uint32_t right = rr(right_reg);
    uint32_t low, high;
    if (is_signed) {
        int64_t product = (int64_t)(int32_t)left * (int64_t)(int32_t)right;
        low = (uint32_t)product;
        high = (uint32_t)((uint64_t)product >> 32);
    } else {
        uint64_t product = (uint64_t)left * right;
        low = (uint32_t)product;
        high = (uint32_t)(product >> 32);
    }
    wr(lo, low);
    wr(hi, high);
}

void camry_muli(int lo, int hi, int32_t imm) {
    int64_t product = (int64_t)(int32_t)rr(lo) * imm;
    uint32_t low = (uint32_t)product;
    uint32_t high = (uint32_t)((uint64_t)product >> 32);
    wr(lo, low);
    wr(hi, high);
}

void camry_mului(int lo, int hi, uint32_t imm) {
    uint64_t product = (uint64_t)rr(lo) * imm;
    uint32_t low = (uint32_t)product;
    uint32_t high = (uint32_t)(product >> 32);
    wr(lo, low);
    wr(hi, high);
}

void camry_mulh(int dst, int src) {
    wr(dst, (uint32_t)((int32_t)(int16_t)rr(src) * (int32_t)(int16_t)rr(dst)));
}
void camry_mulhi(int dst, int src, int32_t imm) { wr(dst, (uint32_t)((int32_t)(int16_t)rr(src) * imm)); }
void camry_mulhi5(int dst, int32_t imm) { wr(dst, (uint32_t)((int32_t)(int16_t)rr(dst) * imm)); }

void camry_div3(int quot, int divisor_reg, int rem, int is_signed, int half) {
    uint32_t dividend = rr(quot);
    uint32_t divisor = rr(divisor_reg);
    if (half) divisor = (uint32_t)(int32_t)(int16_t)divisor;
    if (divisor == 0) { camry_OV = 1; return; }
    if (is_signed && dividend == 0x80000000u && divisor == 0xffffffffu) {
        camry_OV = 1; camry_S = 1; camry_Z = 0;
        wr(quot, 0x80000000u);
        wr(rem, 0);
        return;
    }
    if (is_signed) {
        int32_t q = (int32_t)dividend / (int32_t)divisor;
        int32_t m = (int32_t)dividend % (int32_t)divisor;
        camry_OV = 0; camry_S = (uint32_t)q >> 31; camry_Z = q == 0;
        wr(quot, (uint32_t)q);
        wr(rem, (uint32_t)m);
    } else {
        uint32_t q = dividend / divisor;
        uint32_t m = dividend % divisor;
        camry_OV = 0; camry_S = q >> 31; camry_Z = q == 0;
        wr(quot, q);
        wr(rem, m);
    }
}

void camry_divh2(int dst, int src) {
    uint32_t dividend = rr(dst);
    uint32_t divisor = (uint32_t)(int32_t)(int16_t)rr(src);
    if (divisor == 0) { camry_OV = 1; return; }
    if (dividend == 0x80000000u && divisor == 0xffffffffu) {
        camry_OV = 1; camry_S = 1; camry_Z = 0; wr(dst, 0x80000000u); return;
    }
    int32_t q = (int32_t)dividend / (int32_t)divisor;
    camry_OV = 0; camry_S = (uint32_t)q >> 31; camry_Z = q == 0;
    wr(dst, (uint32_t)q);
}

void camry_satadd(int dst, int src) {
    uint32_t left = rr(src), right = rr(dst);
    flags_add(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left + (int64_t)(int32_t)right));
}
void camry_satsub(int dst, int src) {
    uint32_t left = rr(dst), right = rr(src);
    flags_sub(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left - (int64_t)(int32_t)right));
}
void camry_satsubr(int dst, int src) {
    uint32_t left = rr(src), right = rr(dst);
    flags_sub(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left - (int64_t)(int32_t)right));
}
void camry_sataddi(int dst, int32_t imm) {
    uint32_t left = rr(dst);
    flags_add(left, (uint32_t)imm);
    wr(dst, clamp_sat((int64_t)(int32_t)left + imm));
}
void camry_satsubi(int dst, int src, int32_t imm) {
    uint32_t left = rr(src);
    flags_sub(left, (uint32_t)imm);
    wr(dst, clamp_sat((int64_t)(int32_t)left - imm));
}
void camry_satadd3(int dst, int left_reg, int right_reg) {
    uint32_t left = rr(left_reg), right = rr(right_reg);
    flags_add(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left + (int64_t)(int32_t)right));
}
void camry_satsub3(int dst, int left_reg, int right_reg) {
    uint32_t left = rr(left_reg), right = rr(right_reg);
    flags_sub(left, right);
    wr(dst, clamp_sat((int64_t)(int32_t)left - (int64_t)(int32_t)right));
}

static void search_bits(int src, int dst, int pattern, int from_left) {
    uint32_t value = rr(src);
    uint32_t count = 0;
    uint32_t cursor = value;
    int found = 0;
    while (count < 32u) {
        uint32_t bit = from_left ? cursor >> 31 : cursor & 1u;
        if (bit == (uint32_t)pattern) { found = 1; break; }
        cursor = from_left ? cursor << 1 : cursor >> 1;
        count += 1u;
    }
    if (found) count += 1u;
    else count = 0;
    camry_OV = 0;
    camry_S = 0;
    camry_Z = count == 0;
    camry_CY = count == 32u;
    wr(dst, count);
}
void camry_sch0r(int src, int dst) { search_bits(src, dst, 0, 0); }
void camry_sch1r(int src, int dst) { search_bits(src, dst, 1, 0); }
void camry_sch0l(int src, int dst) { search_bits(src, dst, 0, 1); }
void camry_sch1l(int src, int dst) { search_bits(src, dst, 1, 1); }
void camry_bsw(int src, int dst) {
    uint32_t value = rr(src);
    uint32_t result = ((value & 0xffu) << 24) | ((value & 0xff00u) << 8) | ((value & 0xff0000u) >> 8) | (value >> 24);
    set_sz_keep_cy(result);
    camry_CY = !(value & 0xffu) || !((value >> 8) & 0xffu) || !((value >> 16) & 0xffu) || !(value >> 24);
    wr(dst, result);
}
void camry_bsh(int src, int dst) {
    uint32_t value = rr(src);
    uint32_t result = ((value & 0xff0000u) << 8) | ((value >> 24) << 16) | ((value & 0xffu) << 8) | ((value >> 8) & 0xffu);
    camry_OV = 0; camry_S = result >> 31; camry_Z = (result & 0xffffu) == 0;
    camry_CY = !(value & 0xffu) || !((value >> 8) & 0xffu);
    wr(dst, result);
}
void camry_hsw(int src, int dst) {
    uint32_t value = rr(src);
    uint32_t result = (value << 16) | (value >> 16);
    set_sz_keep_cy(result);
    camry_CY = !(value & 0xffffu) || !(value >> 16);
    wr(dst, result);
}
void camry_hsh(int src, int dst) {
    uint32_t value = rr(src);
    camry_OV = 0; camry_S = value >> 31; camry_Z = (value & 0xffffu) == 0; camry_CY = (value & 0xffffu) == 0;
    wr(dst, value);
}

static uint32_t pack_psw(void) {
    uint32_t value = camry_SR[0][5] & ~0x1fu;
    value |= camry_Z | (camry_S << 1) | (camry_OV << 2) | (camry_CY << 3) | (camry_SAT << 4);
    return value;
}

void camry_ldsr(int src, int id, int sel) {
    uint32_t value = rr(src);
    if (sel == 0 && id == 5) {
        camry_Z = value & 1u;
        camry_S = (value >> 1) & 1u;
        camry_OV = (value >> 2) & 1u;
        camry_CY = (value >> 3) & 1u;
        camry_SAT = (value >> 4) & 1u;
    }
    if ((unsigned)sel < 8u && (unsigned)id < 32u)
        camry_SR[sel][id] = value;
}

void camry_stsr(int dst, int id, int sel) {
    uint32_t value = 0;
    if ((unsigned)sel < 8u && (unsigned)id < 32u)
        value = camry_SR[sel][id];
    if (sel == 0 && id == 5)
        value = pack_psw();
    wr(dst, value);
}

void camry_pushsp(int low, int high) {
    uint32_t pointer = camry_R[3];
    int reg;
    if (low > high)
        return;
    for (reg = low; reg <= high; reg += 1) {
        pointer -= 4u;
        camry_write32(pointer, rr(reg));
    }
    camry_R[3] = pointer;
}

void camry_popsp(int low, int high) {
    uint32_t pointer = camry_R[3];
    int reg;
    if (low > high)
        return;
    for (reg = high; reg >= low; reg -= 1) {
        if (reg != 3)
            wr(reg, camry_read32(pointer));
        pointer += 4u;
    }
    camry_R[3] = pointer;
}

static void apply_psw(uint32_t psw) {
    camry_SR[0][5] = psw;
    camry_Z = psw & 1u;
    camry_S = (psw >> 1) & 1u;
    camry_OV = (psw >> 2) & 1u;
    camry_CY = (psw >> 3) & 1u;
    camry_SAT = (psw >> 4) & 1u;
}

int camry_loop(int reg) {
    uint32_t current = rr(reg);
    flags_add(current, 0xffffffffu);
    uint32_t count = current - 1u;
    wr(reg, count);
    return count != 0;
}

uint32_t camry_switch_target(uint32_t next, int reg) {
    uint32_t slot = next + (rr(reg) << 1);
    int32_t disp = (int16_t)camry_read16(slot);
    return next + ((uint32_t)disp << 1);
}

uint32_t camry_callt_target(uint32_t next, uint32_t imm) {
    uint32_t ctbp = camry_SR[0][20];
    camry_SR[0][16] = next;
    camry_SR[0][17] = pack_psw() & 0x1fu;
    return ctbp + camry_read16(ctbp + (imm << 1));
}
"""


def emit_c(functions: dict[int, LiftedFn], selected: set[int], path: Path) -> None:
    ordered = [functions[entry] for entry in sorted(selected)]
    lines = [
        "/* Generated by tools/camry_lift.py. Do not hand-edit. */",
        RUNTIME,
        "static void camry_dispatch(uint32_t target, uint32_t return_to);",
    ]
    for fn in ordered:
        lines.append(f"static void {fn_symbol(fn.entry)}(uint32_t pc, uint32_t entry_lp);")
    for fn in ordered:
        lines.extend(emit_function(fn))
    spans = []
    for fn in ordered:
        for start, end in fn.ranges:
            spans.append((start, end + 1, fn.entry))
    spans.sort()
    lines.append("static const struct { uint32_t start; uint32_t end; void (*fn)(uint32_t, uint32_t); } camry_ranges[] = {")
    for start, end, entry in spans:
        lines.append(f"    {{0x{start:x}u, 0x{end:x}u, {fn_symbol(entry)}}},")
    lines.append("};")
    lines.append("static const uint32_t camry_range_count = sizeof camry_ranges / sizeof camry_ranges[0];")
    lines.append(DISPATCH)
    lines.append(RUNNER)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_function(fn: LiftedFn) -> list[str]:
    checks = " || ".join(
        f"(target >= 0x{start:x}u && target < 0x{end + 1:x}u)" for start, end in fn.ranges
    ) or "0"
    lines = [
        f"__attribute__((unused)) static int camry_in_{fn.entry:08x}(uint32_t target) {{ return {checks}; }}",
        f"static void {fn_symbol(fn.entry)}(uint32_t pc, uint32_t entry_lp) {{",
        "    (void)entry_lp;",
        "    for (;;) {",
        "        camry_step();",
        "        switch (pc) {",
    ]
    ordered = sorted(fn.insts, key=lambda inst: inst.addr)
    for index, inst in enumerate(ordered):
        fall = ordered[index + 1].addr if index + 1 < len(ordered) else None
        lines.append(f"        case 0x{inst.addr:x}u: {{")
        lines.extend("            " + line for line in emit_case(inst, fall, fn))
        lines.append("        }")
    lines.extend([
        "        default:",
        f'            fprintf(stderr, "lift bad pc %#x in {fn.name}\\n", pc);',
        "            abort();",
        "        }",
        "    }",
        "}",
    ])
    return lines


def emit_case(inst: Inst, fall: int | None, fn: LiftedFn) -> list[str]:
    fall_s = f"0x{fall:x}u" if fall is not None else None
    if inst.kind == "alu" or inst.kind == "nop":
        body = [inst.stmt] if inst.stmt else []
        if fall_s is None:
            body.append("return;")
            return body
        body.append(f"pc = {fall_s};")
        body.append("break;")
        return body
    if inst.kind == "abort":
        return [f'fprintf(stderr, "lift abort {inst.text} at {inst.addr:#x}\\n");', "abort();"]
    if inst.kind in {"b", "br"}:
        inside = inst.target in fn.sites
        if inst.kind == "br" or inst.cc == 5:
            return branch_lines(inst.target, inside, fall_s, None, fn)
        return branch_lines(inst.target, inside, fall_s, inst.cc, fn)
    if inst.kind in {"jarl", "jarl_ind"}:
        link_next = inst.addr + inst.size
        lines = []
        if inst.kind == "jarl_ind":
            lines.append(f"uint32_t target = rr({inst.reg});")
        if inst.link:
            lines.append(f"camry_R[{inst.link}] = 0x{link_next:x}u;")
        target = "target" if inst.kind == "jarl_ind" else f"0x{inst.target:x}u"
        lines.append(f"camry_dispatch({target}, 0x{link_next:x}u);")
        if fall is not None:
            lines.extend([f"pc = 0x{fall:x}u;", "break;"])
        else:
            lines.append("return;")
        return lines
    if inst.kind == "jr":
        inside = inst.target in fn.sites
        return branch_lines(inst.target, inside, None, None, fn)
    if inst.kind == "jmp":
        return transfer_lines(f"rr({inst.reg})", fn)
    if inst.kind == "jmpdisp":
        return transfer_lines(f"0x{inst.base:x}u + rr({inst.reg})", fn)
    if inst.kind == "loop":
        inside = inst.target in fn.sites
        if inside:
            taken = f"pc = 0x{inst.target:x}u; break;"
        else:
            taken = f"camry_dispatch(0x{inst.target:x}u, entry_lp); return;"
        lines = [f"if (camry_loop({inst.reg})) {{ {taken} }}"]
        if fall_s:
            lines.extend([f"pc = {fall_s};", "break;"])
        else:
            lines.append("return;")
        return lines
    if inst.kind == "switch":
        nxt = inst.addr + inst.size
        return transfer_lines(f"camry_switch_target(0x{nxt:x}u, {inst.reg})", fn)
    if inst.kind == "callt":
        nxt = fall if fall is not None else inst.addr + inst.size
        lines = [f"camry_dispatch(camry_callt_target(0x{nxt:x}u, {inst.imm}u), 0x{nxt:x}u);"]
        if fall is not None:
            lines.extend([f"pc = 0x{fall:x}u;", "break;"])
        else:
            lines.append("return;")
        return lines
    if inst.kind == "dispose":
        lines = [f"camry_sp_add({inst.slots}u << 2);"]
        for reg in (31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20):
            if inst.mask & (1 << reg):
                lines.append(f"camry_pop({reg});")
        if inst.ret:
            lines.extend(transfer_lines(f"rr({inst.ret})", fn))
        elif fall_s:
            lines.extend([f"pc = {fall_s};", "break;"])
        else:
            lines.append("return;")
        return lines
    raise SystemExit(f"unemitted {inst.kind} at {inst.addr:#x}")


def transfer_lines(expr: str, fn: LiftedFn) -> list[str]:
    return [
        f"uint32_t target = {expr};",
        "if (target == entry_lp) return;",
        f"if (camry_in_{fn.entry:08x}(target)) {{ pc = target; break; }}",
        "camry_dispatch(target, entry_lp);",
        "return;",
    ]


def branch_lines(target: int, inside: bool, fall_s: str | None, cc: int | None, fn: LiftedFn) -> list[str]:
    del fn
    if inside:
        taken = f"pc = 0x{target:x}u; break;"
    else:
        taken = f"camry_dispatch(0x{target:x}u, entry_lp); return;"
    if cc is None:
        return [taken]
    lines = [f"if (camry_take({cc})) {{ {taken} }}"]
    if fall_s:
        lines.extend([f"pc = {fall_s};", "break;"])
    else:
        lines.append("return;")
    return lines


DISPATCH = r"""
static void camry_dispatch(uint32_t target, uint32_t return_to) {
    uint32_t lo = 0;
    uint32_t hi = camry_range_count;
    while (lo < hi) {
        uint32_t mid = lo + (hi - lo) / 2u;
        if (target < camry_ranges[mid].start)
            hi = mid;
        else if (target >= camry_ranges[mid].end)
            lo = mid + 1u;
        else {
            camry_ranges[mid].fn(target, return_to);
            return;
        }
    }
    fprintf(stderr, "unlifted target %#x\n", target);
    abort();
}
"""

RUNNER = r"""
uint32_t camry_lift_psw = 0x20u;

uint32_t camry_lift_run(uint32_t entry, uint32_t r6, uint32_t r7, uint32_t r8, uint32_t r9, uint32_t lp) {
    int index;
    camry_steps = 0;
    for (index = 0; index < 32; index += 1)
        camry_R[index] = 0;
    for (index = 0; index < 8; index += 1) {
        int id;
        for (id = 0; id < 32; id += 1)
            camry_SR[index][id] = 0;
    }
    camry_R[3] = camry_sp;
    camry_R[4] = camry_gp;
    camry_R[5] = camry_tp;
    camry_R[6] = r6;
    camry_R[7] = r7;
    camry_R[8] = r8;
    camry_R[9] = r9;
    camry_R[31] = lp;
    apply_psw(camry_lift_psw);
    camry_dispatch(entry, lp);
    return camry_R[10];
}
"""


def fix_camry_lift_set_psw() -> None:
    """The generated setter is replaced after the template is known to compile."""


def report() -> None:
    image = load_image()
    symbols = load_symbols()
    decoded, unknown = decode_all(image, symbols)
    liftable = liftable_set(decoded)
    matched = {int(row["addr"], 16) for row in load_matched()}
    oracles = []
    with (ROOT / "oracles.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                oracles.append(json.loads(line))
    candidates = candidate_entries(oracles, matched, liftable)
    seeds = set(candidates) | (matched & liftable)
    closed = closure_of(seeds, decoded, liftable)
    print(f"decoded {len(decoded)} / {len(symbols)}")
    print(f"liftable {len(liftable)}")
    print(f"full-return candidates {len(candidates)}")
    print(f"matched liftable {len(matched & liftable)} / {len(matched)}")
    print(f"closure {len(closed)}")
    print("unknown heads:")
    for (hw0, hw1, op), count in unknown.most_common(12):
        print(f"  {count:5d}  hw0={hw0:04x} hw1={hw1:04x} op0510={op:02x}")
    for sample in (0x79044, 0x77982, 0x66D6E):
        fn = decoded.get(sample)
        print(f"sample {sample:#x}: {'decoded' if fn else 'FAILED'} {fn.name if fn else ''} insts={len(fn.insts) if fn else 0}")
        if fn:
            for inst in fn.insts[:12]:
                print(f"  {inst.addr:#x} {inst.text}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("report", "emit", "check"))
    args = parser.parse_args()
    if args.command == "report":
        report()
        return 0
    image = load_image()
    symbols = load_symbols()
    decoded, _unknown = decode_all(image, symbols)
    liftable = liftable_set(decoded)
    matched_rows = load_matched()
    matched = {int(row["addr"], 16) for row in matched_rows}
    oracles = []
    with (ROOT / "oracles.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                oracles.append(json.loads(line))
    candidates = candidate_entries(oracles, matched, liftable)
    names = {int(row["addr"], 16): row["name"] for row in symbols}
    seeds = set(candidates) | (matched & liftable)
    closed = closure_of(seeds, decoded, liftable)
    emit_c(decoded, closed, LIFTED_C)
    print(f"emitted {len(closed)} functions ({len(candidates)} candidates) to {LIFTED_C}")
    if args.command == "emit":
        return 0
    return run_check(candidates, names, matched & liftable, oracles)


def run_check(candidates: dict[int, list[dict]], names: dict[int, str], validate: set[int], oracles: list[dict]) -> int:
    import ctypes
    import tempfile
    from pathlib import Path

    from tests.decomp.verify_camry_decomp import (
        DCRA1_BASE,
        DCRA1_SIZE,
        bind,
        call_lifted,
        check_results,
        compile_sources,
        install_address_space,
        install_regions,
        materialize,
        scenario_regions,
        view_of,
    )

    metadata = resolve_target("camry-8965F3307000")[1]
    codeflash = bytearray((REPO_ROOT / metadata["codeflash"]).read_bytes())
    by_entry: dict[int, list[dict]] = {}
    for scenario in oracles:
        entry = scenario.get("entry") or {}
        if entry.get("scope") != "resolved-address":
            continue
        by_entry.setdefault(int(entry["address"], 16), []).append(scenario)

    import os
    import subprocess

    failures = 0
    passed_new = []
    with tempfile.TemporaryDirectory(prefix="camry-lift-") as directory:
        try:
            library = compile_sources(Path(directory), optimize="-O1")
        except subprocess.CalledProcessError as exc:
            sys.stderr.write(exc.stderr or "")
            sys.stderr.write(exc.stdout or "")
            return 1
        bind(library)
        code_view = view_of(codeflash)

        def run_scenario(address: int, name: str, scenario: dict) -> str | None:
            if not useful_oracle(scenario) or oracle_blocked(scenario):
                return None
            registers = scenario.get("registers") or {}
            limit = int(scenario.get("max_instructions") or 200000)
            mapped = materialize(scenario)
            try:
                if mapped is None:
                    regions = scenario_regions(scenario)
                    if 1 + len(regions) + 1 > 8:
                        return "region cap"
                    held = install_regions(library, code_view, len(codeflash), regions)
                    dcra, dcra_view = attach_dcra_force(library)
                    returned = call_lifted(library, address, registers, limit)
                    check_results(scenario, name, None, 0, registers, returned, regions, codeflash, dcra, value_return=True)
                    del held, dcra_view
                else:
                    memory, base = mapped
                    view = view_of(memory) if memory else view_of(bytearray(b"\x00"))
                    install_address_space(library, code_view, len(codeflash), view, base, memory)
                    dcra, dcra_view = attach_dcra_force(library)
                    returned = call_lifted(library, address, registers, limit)
                    check_results(scenario, name, memory, base, registers, returned, codeflash=codeflash, dcra=dcra, value_return=True)
                    del dcra_view
            except AssertionError as exc:
                return str(exc)
            return None

        def attach_dcra_force(library):
            window = bytearray(DCRA1_SIZE)
            view = view_of(window)
            library.camry_host_add(DCRA1_BASE, ctypes.cast(view, ctypes.POINTER(ctypes.c_uint8)), DCRA1_SIZE)
            return window, view

        def isolated(address: int, name: str, scenario: dict) -> str | None:
            pid = os.fork()
            if pid == 0:
                try:
                    message = run_scenario(address, name, scenario)
                except Exception as exc:
                    print(f"EXC {name} {scenario['name']}: {exc}", flush=True)
                    os._exit(3)
                if message:
                    print(f"FAIL {name} {scenario['name']}: {message}", flush=True)
                    os._exit(2)
                os._exit(0)
            _pid, status = os.waitpid(pid, 0)
            if os.WIFSIGNALED(status):
                return f"signal {os.WTERMSIG(status)}"
            if os.WEXITSTATUS(status) == 0:
                return None
            return "failed"

        print(f"validating {len(validate)} matched functions", flush=True)
        for address in sorted(validate):
            name = names[address]
            print(f"validate {name}", flush=True)
            for scenario in by_entry.get(address, []):
                message = isolated(address, name, scenario)
                if message:
                    failures += 1
                    if message != "failed":
                        print(f"FAIL matched {name} {scenario['name']}: {message}", flush=True)
                    if failures > 12:
                        print("stopping after 12 validation failures")
                        return 1
        if failures:
            return 1
        print("matched liftable oracles passed", flush=True)
        for address, scenarios in sorted(candidates.items()):
            name = names[address]
            print(f"candidate {name}", flush=True)
            ok = True
            for scenario in scenarios:
                message = isolated(address, name, scenario)
                if message:
                    ok = False
                    if message != "failed":
                        print(f"FAIL new {name} {scenario['name']}: {message}", flush=True)
                    break
            if ok:
                passed_new.append((address, name))
        print(f"new passes {len(passed_new)} / {len(candidates)}")
    if not passed_new:
        return 0
    path = ROOT / "matched.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        for address, name in passed_new:
            handle.write(json.dumps({"addr": f"0x{address:x}", "name": name, "status": "equivalent", "form": "lifted"}) + "\n")
    print(f"recorded {len(passed_new)} lifted functions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
