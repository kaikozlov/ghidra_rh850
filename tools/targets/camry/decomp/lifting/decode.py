"""RH850 instruction decoding into register-transfer operations."""
from __future__ import annotations

from dataclasses import dataclass


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
    # Each return uses its own saved PC/PSW pair.
    if hw0 == 0x07E0 and hw1 in (0x0144, 0x0148, 0x014A):
        name = {0x0144: "ctret", 0x0148: "eiret", 0x014A: "feret"}[hw1]
        return Inst(addr, 4, "eiret", text=name)
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
    bins = _bins_fields(hw1)
    if bins is not None:
        pos, width = bins
        return Inst(
            addr, 4, "alu",
            stmt=f"camry_bins({reg2}, {reg1}, {pos}, {width});",
            text=f"bins r{reg1}, {pos:#x}, {width:#x}, r{reg2}",
        )
    if op2126 in (0x1E, 0x1F) and (hw1 & 1) == 0 and (reg3 & 1) == 0 and (hw1 & 0x1F & 1) == 0:
        reg4 = hw1 & 0x1F
        name = "mac" if op2126 == 0x1E else "macu"
        return Inst(
            addr, 4, "alu",
            stmt=f"camry_{name}({reg1}, {reg2}, {reg3}, {reg4});",
            text=f"{name} r{reg1}, r{reg2}, r{reg3}, r{reg4}",
        )
    return None


def _bins_fields(hw1: int) -> tuple[int, int] | None:
    """Position and width of a bins instruction, or None when hw1 is not one.

    The three forms cover a field that starts below bit 16, starts at bit 16
    or above, or crosses bit 16. The inserted field stays inside the word.
    """
    if hw1 & 1:
        return None
    form = (hw1 >> 4) & 0x7F
    if form not in (0x09, 0x0B, 0x0D):
        return None
    low = (((hw1 >> 11) & 1) << 3) | ((hw1 >> 1) & 7)
    high = (hw1 >> 12) & 0xF
    if form == 0x09:
        pos = 0x10 | low
        width = high + 1 - low
    elif form == 0x0B:
        pos = low
        width = high + 0x11 - low
    else:
        pos = low
        width = high + 1 - low
    if width <= 0 or pos + width > 32:
        return None
    return pos, width


