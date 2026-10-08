#!/usr/bin/env python3
"""Build a synthetic RH850 instruction fixture for SLEIGH semantic checks."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "tests" / "fixtures" / "processor"


def u16(value: int) -> bytes:
    return struct.pack("<H", value & 0xFFFF)


def u32(value: int) -> bytes:
    return struct.pack("<I", value & 0xFFFFFFFF)

def enc_ldsr(source_reg: int, system_reg: int, sel_id: int) -> bytes:
    word0 = ((system_reg & 0x1F) << 11) | (0x3F << 5) | (source_reg & 0x1F)
    word1 = ((sel_id & 0x1F) << 11) | 0x20
    return u16(word0) + u16(word1)


def enc_stsr(system_reg: int, dest_reg: int, sel_id: int) -> bytes:
    word0 = ((dest_reg & 0x1F) << 11) | (0x3F << 5) | (system_reg & 0x1F)
    word1 = ((sel_id & 0x1F) << 11) | 0x40
    return u16(word0) + u16(word1)


def enc_reg_reg(op0510: int, r1: int, r2: int) -> bytes:
    """16-bit format: bits[15:11]=r2, [10:5]=op, [4:0]=r1."""
    return u16(((r2 & 0x1F) << 11) | ((op0510 & 0x3F) << 5) | (r1 & 0x1F))


def enc_imm5_reg(op0510: int, imm5: int, r2: int) -> bytes:
    return u16(((r2 & 0x1F) << 11) | ((op0510 & 0x3F) << 5) | (imm5 & 0x1F))


def enc_ld_st16(op0510: int, r1: int, r2: int, imm16: int) -> bytes:
    return enc_reg_reg(op0510, r1, r2) + u16(imm16)


def enc_sld_b(disp7: int, r2: int) -> bytes:
    # op0710=0x06, bits[6:0]=disp, bits[15:11]=r2
    return u16(((r2 & 0x1F) << 11) | (0x6 << 7) | (disp7 & 0x7F))


def enc_sld_h(disp8_bytes: int, r2: int) -> bytes:
    # disp field is disp8/2 in bits[6:0], op0710=0x08
    return u16(((r2 & 0x1F) << 11) | (0x8 << 7) | ((disp8_bytes // 2) & 0x7F))


def enc_sld_bu(disp4: int, r2: int) -> bytes:
    # op0410=0x06, bits[3:0]=disp4, bits[15:11]=r2
    return u16(((r2 & 0x1F) << 11) | (0x06 << 4) | (disp4 & 0xF))


def enc_sld_hu(disp5: int, r2: int) -> bytes:
    # disp5/2 in bits[3:0], op0410=0x07
    return u16(((r2 & 0x1F) << 11) | (0x07 << 4) | ((disp5 // 2) & 0xF))


def enc_divh_rr(r1: int, r2: int) -> bytes:
    # DIVH reg1,reg2 : op0510=0x02
    return enc_reg_reg(0x02, r1, r2)


def enc_jarl_disp22(disp22: int, r2: int) -> bytes:
    # JARL disp22, reg2 : op0610=0x1E ... & addr22
    # addr22: rel = ((s0005 << 16) | op1631) + inst_start
    # Format: bits[15:11]=r2, [10:6]=0x1E? Wait op0610 means bits 6-10.
    # ::jarl addr22, r1115 is (op0610=0x1E & r1115) ... & addr22
    # Lower bit of displacement is always 0 (halfword aligned); stored in op1631 and s0005.
    # addr22 construction: rel = ((s0005 << 16) | op1631) + inst_start
    # where s0005 is bits 0-5 of first word? Looking at common.sinc:
    # addr22: rel is s0005; op1631 & op1616=0
    # So first word has s0005 in bits 0-5, and second word is the low 16 of displacement.
    disp = disp22 & 0x3FFFFF
    low16 = disp & 0xFFFF
    hi5 = (disp >> 16) & 0x1F
    word0 = ((r2 & 0x1F) << 11) | (0x1E << 6) | hi5
    # op1616 must be 0 — low bit of second word
    word1 = low16 & 0xFFFE
    return u16(word0) + u16(word1)


def enc_jarl_indirect(r1: int, r3: int) -> bytes:
    # RH850G3M Format XI:
    #   15..0  = 11000111111RRRRR
    #   31..16 = WWWWW00101100000
    return u16(0xC7E0 | (r1 & 0x1F)) + u16(((r3 & 0x1F) << 11) | 0x160)


def enc_jmp_lp() -> bytes:
    # JMP [reg1] with reg1=lp(31): op0515=0x003 & R0004 & op0004=31
    # bits[15:5]=0x003, bits[4:0]=31
    return u16((0x003 << 5) | 31)


def enc_prepare_list12_imm5(imm5: int) -> bytes:
    # PREPARE list12, imm5 : prep0615=0x1E & prep0105 & prep1620=0x01
    # Uses 32-bit prep token. This is complex; emit a minimal form saving {lp}.
    # From v850_func.sinc: prepare PrepList, prep0105 is prep0615=0x1E & prep0105 & prep1620=0x01
    # prep token is 32-bit little-endian.
    # bits 15:6 = 0x1E (prep0615), bits 5:1 = imm5 (prep0105), bit0 and bits for list...
    # For list with only lp: prep21=1, others 0.
    # Looking at PrepList definitions: prep21 is bit 21 of the 32-bit prep token.
    word = 0
    word |= (0x1E << 6)          # prep0615
    word |= ((imm5 & 0x1F) << 1)  # prep0105
    word |= (0x01 << 16)          # prep1620 = 0x01
    word |= (1 << 21)             # prep21 = lp
    return u32(word)


def enc_dispose_list12_imm5_lp(imm5: int) -> bytes:
    # DISPOSE imm5, list12, [lp] : prep0615=0x19, prep1620=lp=31
    word = 0
    word |= (0x19 << 6)
    word |= ((imm5 & 0x1F) << 1)
    word |= (31 << 16)  # prep1620r = lp
    word |= (1 << 21)   # restore lp in list
    return u32(word)


def enc_satadd_rr(r1: int, r2: int) -> bytes:
    # SATADD reg1, reg2 : op0510=0x06
    return enc_reg_reg(0x06, r1, r2)


def enc_ld_w(r1: int, r2: int, disp16: int) -> bytes:
    # LD.W disp16[reg1], reg2 : op0510=0x39, op1616=1, disp = s1731*2
    # Second halfword: bit0=1, bits[15:1]=disp/2
    return enc_reg_reg(0x39, r1, r2) + u16((((disp16 // 2) & 0x7FFF) << 1) | 1)


def enc_mov_imm5(imm5: int, r2: int) -> bytes:
    return enc_imm5_reg(0x10, imm5 & 0x1F, r2)


def enc_switch(reg: int) -> bytes:
    # SWITCH reg1 : op0515=0x002 & R0004
    return u16((0x002 << 5) | (reg & 0x1F))


def enc_callt(imm6: int) -> bytes:
    # CALLT imm6 : op0615=0x008 & op0005
    return u16((0x008 << 6) | (imm6 & 0x3F))


def enc_bins_low(r1: int, r2: int, pos: int, width: int) -> bytes:
    """BINS with msb/lsb both < 16 (op2026=0x0D)."""
    if not (0 <= pos < 16 and width >= 1 and pos + width <= 16):
        raise ValueError(f"bins low form requires pos+width <= 16, got {pos}+{width}")
    # width = op2831 + 1 - pos  =>  op2831 = width + pos - 1
    op2831 = width + pos - 1
    op1719 = pos & 0x7
    op2727 = (pos >> 3) & 0x1
    word0 = ((r2 & 0x1F) << 11) | (0x3F << 5) | (r1 & 0x1F)
    word1 = ((op2831 & 0xF) << 12) | (op2727 << 11) | (0x0D << 4) | ((op1719 & 0x7) << 1)
    return u16(word0) + u16(word1)


def enc_bit3_mem(op1415: int, bit: int, r1: int, disp16: int) -> bytes:
    # SET1/CLR1/TST1 bit3, disp16[reg1] : op0510=0x3E
    word0 = ((op1415 & 0x3) << 14) | ((bit & 0x7) << 11) | (0x3E << 5) | (r1 & 0x1F)
    return u16(word0) + u16(disp16 & 0xFFFF)


def enc_set1_bit3(bit: int, r1: int, disp16: int) -> bytes:
    return enc_bit3_mem(0, bit, r1, disp16)


def enc_clr1_bit3(bit: int, r1: int, disp16: int) -> bytes:
    return enc_bit3_mem(2, bit, r1, disp16)


def enc_tst1_bit3(bit: int, r1: int, disp16: int) -> bytes:
    return enc_bit3_mem(3, bit, r1, disp16)


def enc_cmov_rr(cc: int, r1: int, r2: int, r3: int) -> bytes:
    # CMOV cccc, reg1, reg2, reg3 : op2126=0x19, op1616=0, cc1720
    word0 = ((r2 & 0x1F) << 11) | (0x3F << 5) | (r1 & 0x1F)
    word1 = ((r3 & 0x1F) << 11) | (0x19 << 5) | ((cc & 0xF) << 1)
    return u16(word0) + u16(word1)


def enc_mulhi(imm16: int, r1: int, r2: int) -> bytes:
    # MULHI imm16, reg1, reg2 : op0510=0x37
    return enc_reg_reg(0x37, r1, r2) + u16(imm16 & 0xFFFF)


def enc_sar_imm5(imm5: int, r2: int) -> bytes:
    # SAR imm5, reg2 : op0510=0x15
    return enc_imm5_reg(0x15, imm5, r2)

def enc_caxi(r1: int, r2: int, r3: int) -> bytes:
    word0 = ((r2 & 0x1F) << 11) | (0x3F << 5) | (r1 & 0x1F)
    word1 = ((r3 & 0x1F) << 11) | 0x00EE
    return u16(word0) + u16(word1)

def enc_xi(op1626: int, r1: int, r2: int, r3: int) -> bytes:
    """RH850 Format XI register-register-register encoding."""
    word0 = ((r2 & 0x1F) << 11) | (0x3F << 5) | (r1 & 0x1F)
    word1 = ((r3 & 0x1F) << 11) | (op1626 & 0x7FF)
    return u16(word0) + u16(word1)


def enc_loop(r1: int, disp16: int) -> bytes:
    return u16(0x06E0 | (r1 & 0x1F)) + u16((disp16 & 0xFFFE) | 1)


def enc_search(op1626: int, r2: int, r3: int) -> bytes:
    return u16(((r2 & 0x1F) << 11) | 0x07E0) + u16(
        ((r3 & 0x1F) << 11) | op1626
    )


def enc_reg_bit(op1631: int, r1: int, r2: int) -> bytes:
    return enc_reg_reg(0x3F, r1, r2) + u16(op1631)


def enc_rotl_imm(imm5: int, r2: int, r3: int) -> bytes:
    return enc_reg_reg(0x3F, imm5, r2) + u16(((r3 & 0x1F) << 11) | 0x0C4)


def enc_fpu(op0004: int, r2: int, r3: int, op2126: int,
            op1620: int, *, op2020: int = 0) -> bytes:
    word0 = ((r2 & 0x1F) << 11) | (0x3F << 5) | (op0004 & 0x1F)
    word1 = ((r3 & 0x1F) << 11) | ((op2126 & 0x3F) << 5)
    word1 |= ((op2020 & 1) << 4) | (op1620 & 0x1F)
    return u16(word0) + u16(word1)


def enc_cmovf_s(fcbit: int, r1: int, r2: int, r3: int) -> bytes:
    return enc_fpu(r1, r2, r3, 0x20, (fcbit & 0x7) << 1)

def enc_cmpf_s(fcond: int, r2: int, r1: int, fcbit: int) -> bytes:
    word0 = ((r2 & 0x1F) << 11) | (0x3F << 5) | (r1 & 0x1F)
    word1 = ((fcond & 0xF) << 11) | (0x21 << 5) | ((fcbit & 0x7) << 1)
    return u16(word0) + u16(word1)




def enc_cache(cacheop: int, r1: int) -> bytes:
    word0 = 0xE7E0 | (((cacheop >> 5) & 0x3) << 11) | (r1 & 0x1F)
    word1 = ((cacheop & 0x1F) << 11) | 0x0160
    return u16(word0) + u16(word1)


def enc_pref(prefop: int, r1: int) -> bytes:
    return u16(0xDFE0 | (r1 & 0x1F)) + u16(
        ((prefop & 0x1F) << 11) | 0x0160
    )



def build() -> tuple[bytes, list[dict]]:
    cases: list[dict] = []
    blob = bytearray()

    def add(name: str, encoding: bytes, expect: dict, *,
            insn_size: int | None = None) -> None:
        addr = len(blob)
        blob.extend(encoding)
        # Pad to 4-byte alignment between cases for clarity.
        while len(blob) % 4:
            blob.extend(b"\x00\x00")  # NOP is 0x0000
            # If we added NOP, that's fine for padding; keep case size exact in expect.
        cases.append({
            "name": name,
            "addr": addr,
            "size": insn_size if insn_size is not None else len(encoding),
            "bytes": encoding[:insn_size if insn_size is not None else len(encoding)].hex(),
            **expect,
        })

    # Signed short loads via ep — semantic focus of Milestone 2.
    add("sld.b", enc_sld_b(0x10, 10), {
        "mnemonic_prefix": "sld.b",
        "must_pcode_ops": ["INT_SEXT", "LOAD"],
        "forbid_pcode_ops": [],
        "load_size": 1,
        "sign_extend": True,
    })
    add("sld.h", enc_sld_h(0x20, 11), {
        "mnemonic_prefix": "sld.h",
        "must_pcode_ops": ["INT_SEXT", "LOAD"],
        "load_size": 2,
        "sign_extend": True,
    })
    add("sld.bu", enc_sld_bu(0x4, 12), {
        "mnemonic_prefix": "sld.bu",
        "must_pcode_ops": ["INT_ZEXT", "LOAD"],
        "load_size": 1,
        "sign_extend": False,
    })
    add("sld.hu", enc_sld_hu(0x8, 13), {
        "mnemonic_prefix": "sld.hu",
        "must_pcode_ops": ["INT_ZEXT", "LOAD"],
        "load_size": 2,
        "sign_extend": False,
    })

    # ld.w disp16 scale.
    add("ld.w", enc_ld_w(4, 10, 0xB0), {
        "mnemonic_prefix": "ld.w",
        "must_pcode_ops": ["LOAD"],
        "load_size": 4,
        "disp": 0xB0,
    })

    # Signed halfword divide.
    add("divh", enc_divh_rr(6, 10), {
        "mnemonic_prefix": "divh",
        "must_pcode_ops": ["INT_SDIV"],
        "forbid_pcode_ops": ["INT_DIV"],
    })

    # Saturating add — SAT should track signed overflow, not carry alone.
    add("satadd", enc_satadd_rr(6, 10), {
        "mnemonic_prefix": "satadd",
        "must_pcode_ops": ["INT_ADD", "INT_SLESS"],
    })

    # Call / return flow.
    add("jarl", enc_jarl_disp22(0x20, 31), {
        "mnemonic_prefix": "jarl",
        "flow": "CALL",
    })
    add("jmp_lp", enc_jmp_lp(), {
        "mnemonic_prefix": "jmp",
        "flow": "RETURN",
    })

    # Frame create/destroy.
    add("prepare", enc_prepare_list12_imm5(2), {
        "mnemonic_prefix": "prepare",
        "must_pcode_ops": ["STORE", "INT_SUB"],
    })
    add("dispose", enc_dispose_list12_imm5_lp(2), {
        "mnemonic_prefix": "dispose",
        "must_pcode_ops": ["LOAD", "INT_ADD"],
        "flow": "RETURN",
    })
    add("jarl_indirect", enc_jarl_indirect(6, 10), {
        "mnemonic_prefix": "jarl",
        "must_pcode_ops": ["CALLIND"],
        "flow": "CALL",
    })
    add("jarl_indirect_alias", enc_jarl_indirect(6, 6), {
        "mnemonic_prefix": "jarl",
        "must_pcode_ops": ["CALLIND"],
        "flow": "CALL",
    })

    # Inventory-driven risky ops: switch/callt/bitfield/bitmem/cmov/mulhi/sar.
    # switch embeds its signed-halfword table immediately after the opcode.
    # Index 0 → table[0]=+2 halfwords → target = inst_next + 4.
    switch_blob = enc_switch(6) + u16(0x0002) + u16(0) + u16(0)  # insn+table+pad+landing
    add("switch", switch_blob, {
        "mnemonic_prefix": "switch",
        "must_pcode_ops": ["LOAD", "INT_SEXT", "BRANCHIND"],
        "flow": "BRANCH",
    }, insn_size=2)

    add("callt", enc_callt(0x4), {
        "mnemonic_prefix": "callt",
        "must_pcode_ops": ["LOAD", "CALLIND"],
        "flow": "CALL",
    })

    add("bins", enc_bins_low(6, 10, pos=4, width=4), {
        "mnemonic_prefix": "bins",
        "must_pcode_ops": ["INT_AND", "INT_OR", "INT_LEFT"],
    })

    add("set1", enc_set1_bit3(3, 6, 0), {
        "mnemonic_prefix": "set1",
        "must_pcode_ops": ["LOAD", "STORE", "INT_OR"],
    })
    add("clr1", enc_clr1_bit3(3, 6, 0), {
        "mnemonic_prefix": "clr1",
        "must_pcode_ops": ["LOAD", "STORE", "INT_AND"],
    })
    add("tst1", enc_tst1_bit3(3, 6, 0), {
        "mnemonic_prefix": "tst1",
        "must_pcode_ops": ["LOAD"],
        "forbid_pcode_ops": ["STORE"],
    })

    # cmovne: cc=0xA. Taken copies reg1→reg3; not-taken copies reg2→reg3.
    add("cmovne", enc_cmov_rr(0xA, 6, 10, 11), {
        "mnemonic_prefix": "cmovne",
        "must_pcode_ops": ["CBRANCH"],
    })

    add("mulhi", enc_mulhi(0x0010, 6, 10), {
        "mnemonic_prefix": "mulhi",
        "must_pcode_ops": ["INT_MULT", "INT_SEXT"],
    })

    add("sar", enc_sar_imm5(4, 10), {
        "mnemonic_prefix": "sar",
        "must_pcode_ops": ["INT_SRIGHT"],
    })
    add("divq", enc_xi(0x2FC, 6, 10, 11), {
        "mnemonic_prefix": "divq",
        "must_pcode_ops": ["INT_SDIV", "CBRANCH"],
    })
    add("divqu", enc_xi(0x2FE, 6, 10, 11), {
        "mnemonic_prefix": "divqu",
        "must_pcode_ops": ["INT_DIV", "CBRANCH"],
    })
    add("loop", enc_loop(6, 4), {
        "mnemonic_prefix": "loop",
        "must_pcode_ops": ["INT_ADD", "CBRANCH"],
    })
    add("shl-reg", enc_xi(0x0C2, 6, 10, 11), {
        "mnemonic_prefix": "shl",
        "must_pcode_ops": ["INT_LEFT", "INT_AND"],
    })
    add("rotl-zero", enc_rotl_imm(0, 10, 11), {
        "mnemonic_prefix": "rotl",
        "must_pcode_ops": ["INT_LEFT", "INT_RIGHT"],
    })
    add("sch0r", enc_search(0x360, 10, 11), {
        "mnemonic_prefix": "sch0r",
        "must_pcode_ops": ["CBRANCH", "INT_RIGHT"],
    })
    add("sch1l", enc_search(0x366, 10, 11), {
        "mnemonic_prefix": "sch1l",
        "must_pcode_ops": ["CBRANCH", "INT_LEFT"],
    })
    add("bsh", enc_search(0x342, 10, 11), {
        "mnemonic_prefix": "bsh",
    })
    add("hsh", enc_search(0x346, 10, 11), {
        "mnemonic_prefix": "hsh",
    })
    add("set1-reg", enc_reg_bit(0x0E0, 6, 10), {
        "mnemonic_prefix": "set1",
        "must_pcode_ops": ["LOAD", "STORE", "INT_AND"],
    })
    add("ldl.w", enc_xi(0x378, 6, 0, 11), {
        "mnemonic_prefix": "ldl.w",
        "must_pcode_ops": ["LOAD"],
    })
    add("stc.w", enc_xi(0x37A, 6, 0, 11), {
        "mnemonic_prefix": "stc.w",
        "must_pcode_ops": ["STORE", "CBRANCH"],
    })
    add("cll", u16(0xFFFF) + u16(0xF160), {
        "mnemonic_prefix": "cll",
    })
    add("cache", enc_cache(0x20, 6), {
        "mnemonic_prefix": "cache",
        "must_pcode_ops": ["CALLOTHER"],
        "userop": "__cache",
    })
    add("pref", enc_pref(0, 6), {
        "mnemonic_prefix": "pref",
        "must_pcode_ops": ["CALLOTHER"],
        "userop": "__prefetch",
    })

    # Every G3M floating mnemonic that had inherited fork spelling drift.
    add("cvtf.dw", enc_fpu(0x04, 10, 12, 0x22, 0x10), {
        "mnemonic_prefix": "cvtf.dw",
        "must_pcode_ops": ["TRUNC"],
    })
    add("cvtf.ld", enc_fpu(0x01, 10, 12, 0x22, 0x12), {
        "mnemonic_prefix": "cvtf.ld",
        "must_pcode_ops": ["INT2FLOAT"],
    })
    add("cvtf.uld", enc_fpu(0x11, 10, 12, 0x22, 0x12), {
        "mnemonic_prefix": "cvtf.uld",
        "must_pcode_ops": ["INT2FLOAT"],
    })
    add("divf.d", enc_fpu(0x06, 10, 12, 0x23, 0x1E), {
        "mnemonic_prefix": "divf.d",
        "must_pcode_ops": ["FLOAT_DIV"],
    })
    add("floorf.sw", enc_fpu(0x03, 10, 11, 0x22, 0x00), {
        "mnemonic_prefix": "floorf.sw",
        "must_pcode_ops": ["FLOOR", "TRUNC"],
    })
    add("cmovf.s", enc_cmovf_s(2, 6, 10, 11), {
        "mnemonic_prefix": "cmovf.s",
    })
    add("cmpf.sf", enc_cmpf_s(8, 10, 6, 2), {
        "mnemonic_prefix": "cmpf.s",
        "operand_contains": "sf",
    })

    # G3M synchronization mnemonics remain distinct even though the processor
    # language gives them one ordering-boundary p-code userop.
    add("synce", u16(0x001D), {
        "mnemonic_prefix": "synce",
        "must_pcode_ops": ["CALLOTHER"],
        "userop": "__synchronize",
    })
    add("syncm", u16(0x001E), {
        "mnemonic_prefix": "syncm",
        "must_pcode_ops": ["CALLOTHER"],
        "userop": "__synchronize",
    })
    add("syncp", u16(0x001F), {
        "mnemonic_prefix": "syncp",
        "must_pcode_ops": ["CALLOTHER"],
        "userop": "__synchronize",
    })
    add("synci", u16(0x001C), {
        "mnemonic_prefix": "synci",
        "must_pcode_ops": ["CALLOTHER"],
        "userop": "__synchronize",
    })
    add("caxi", enc_caxi(6, 10, 11), {
        "mnemonic_prefix": "caxi",
        "must_pcode_ops": ["LOAD", "STORE", "INT_SUB"],
    })
    add("di", u16(0x07E0) + u16(0x0160), {
        "mnemonic_prefix": "di",
        "must_pcode_ops": ["CALLOTHER"],
        "userop": "__disable_irq",
    })
    add("ei", u16(0x87E0) + u16(0x0160), {
        "mnemonic_prefix": "ei",
        "must_pcode_ops": ["CALLOTHER"],
        "userop": "__enable_irq",
    })

    add("rie", u16(0x0040), {
        "mnemonic_prefix": "rie",
        "flow": "BRANCH",
    })
    add("fetrap-3", u16((3 << 11) | 0x0040), {
        "mnemonic_prefix": "fetrap",
        "flow": "CALL",
    })
    add("ctret", u16(0x07E0) + u16(0x0144), {
        "mnemonic_prefix": "ctret",
        "flow": "RETURN",
    })
    add("trap-3", u16((0x3F << 5) | 3) + u16(0x0100), {
        "mnemonic_prefix": "trap",
    })
    add("eiret", u16(0x07E0) + u16(0x0148), {
        "mnemonic_prefix": "eiret",
        "flow": "RETURN",
    })
    add("ldsr-psw", enc_ldsr(6, 5, 0), {
        "mnemonic_prefix": "ldsr",
        "operand_register": "PSW",
    })

    add("ldsr-mcfg0", enc_ldsr(6, 0, 1), {
        "mnemonic_prefix": "ldsr",
        "operand_register": "MCFG0",
    })
    add("ldsr-pmr", enc_ldsr(6, 11, 2), {
        "mnemonic_prefix": "ldsr",
        "operand_register": "PMR",
    })
    add("ldsr-mcc", enc_ldsr(6, 10, 5), {
        "mnemonic_prefix": "ldsr",
        "operand_register": "MCC",
    })
    add("stsr-cdbcr", enc_stsr(24, 10, 13), {
        "mnemonic_prefix": "stsr",
        "operand_register": "CDBCR",
    })
    add("ldsr-mpat15", enc_ldsr(6, 30, 7), {
        "mnemonic_prefix": "ldsr",
        "operand_register": "MPAT15",
    })
    add("stsr-mcfg0", enc_stsr(0, 10, 1), {
        "mnemonic_prefix": "stsr",
        "operand_register": "MCFG0",
    })
    add("stsr-pmr", enc_stsr(11, 10, 2), {
        "mnemonic_prefix": "stsr",
        "operand_register": "PMR",
    })
    add("stsr-mcc", enc_stsr(10, 10, 5), {
        "mnemonic_prefix": "stsr",
        "operand_register": "MCC",
    })
    add("stsr-mpat15", enc_stsr(30, 10, 7), {
        "mnemonic_prefix": "stsr",
        "operand_register": "MPAT15",
    })

    return bytes(blob), cases


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    blob, cases = build()
    bin_path = args.out_dir / "rh850_semantic_fixture.bin"
    man_path = args.out_dir / "manifest.json"
    bin_path.write_bytes(blob)
    man_path.write_text(json.dumps({
        "processor": "v850e3:LE:32:default",
        "binary": bin_path.name,
        "size": len(blob),
        "cases": cases,
    }, indent=2) + "\n")
    print(f"Wrote {bin_path} ({len(blob)} bytes), {len(cases)} cases")
    print(f"Wrote {man_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
