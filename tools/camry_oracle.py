#!/usr/bin/env python3
"""Differential oracles for converted Camry functions.

The P1M-E machine runs the original bytes. The host library runs the converted
C on the same inputs. A function becomes oracle-verified only when both sides
agree. Harness limits are printed by ``tools/decomp oracle``; they are not a
separate report.
"""
from __future__ import annotations

import ctypes
import json
import os
import re
import signal
import subprocess
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from tools import REPO_ROOT
from tools.camry_decomp import (
    ROOT,
    _c_signature,
    _prototype_names,
    load_matched,
    load_symbols,
)
from tools.camry_lift import Inst, load_image, walk_symbol
from tools.emulation.p1me_machine import P1MEMachineError
from tools.project.analysis_target import target as resolve_target
from tests.decomp.verify_camry_decomp import (
    HOST_MEM,
    call_corpus,
    install_address_space,
    install_regions,
    materialize,
    parse_signature,
    read_regions,
    scenario_regions,
    useful_oracle,
    view_of,
)

TARGET = "camry-8965F3307000"
MAX_BODY = 128
STEP_LIMIT = 12000
SENTINEL = 0x11111111
STOP = 0x798
GP = 0xFEBEB800
TP = 0x23DFC
ENTRY_SP = 0xFEBE2000
STACK_LO = 0xFEBE1000
STACK_HI = 0xFEBE2200
ARG_BASE = 0xFEBE3000
ARG_STRIDE = 0x400
ARG_COUNT = 4
SIM_CHUNK = 160
FAIL_KINDS = {
    "return-mismatch",
    "memory-mismatch",
    "dropped-return",
    "invented-return",
    "host-unmapped",
}

REASONS = {
    "large": "this batch harnesses functions of at most 128 bytes; larger bodies stay converted",
    "outside-codeflash": "the entry is outside the CodeFlash image the machine executes",
    "undecoded": "the lifter cannot walk every byte of the function, so the harness has no instruction list",
    "no-converted-body": "the converted C is not in src/all (a hand prototype or a dropped body), so the host check has nothing to call",
    "duplicate-body": "the same name is defined twice in src/all, so the host library cannot link it",
    "indirect-call": "an indirect jarl or jmp has no concrete callee, so the closure cannot be built",
    "callt": "callt depends on CTBP, which this harness does not initialize",
    "switch": "a computed switch target is not a fixed closure edge",
    "trap": "rie or fetrap leaves ordinary function return and has no host counterpart",
    "system-register": "ldsr, stsr, di, or ei is visible to the bytes, and the host library does not define those intrinsics",
    "host-intrinsic": "the converted body calls a compiler intrinsic the host library does not define",
    "external-branch": "control leaves the decoded function without a direct call, so the closure is incomplete",
    "large-callee": "a direct callee is above 128 bytes, so this is not a small closure",
    "unmodeled": "the harness interpreter does not fold this operation and will not invent the address it computes",
    "mmio": "the address is outside codeflash, dataflash, and RAM; the P1M-E model faults on that uninitialized peripheral",
    "ram-alias": "the access uses the PE1 local-RAM alias at 0xFEDE0000; the host check maps only 0xFEBE0000",
    "code-extension": "the access is in the extended codeflash window, which this image does not contain",
    "code-write": "the bytes write CodeFlash, which the machine keeps immutable",
    "dataflash-write": "the bytes write DataFlash, which the model accepts only through FACI",
    "misaligned": "the load or store is misaligned, which the machine faults",
    "stack-frame": "the stack access does not fit the harness window below the entry SP",
    "harness-overlap": "a non-stack access lands in the harness stack or argument window",
    "argument-window": "a pointer argument walks past the 1024-byte harness buffer",
    "stack-arguments": "the converted signature has more than four parameters, which the host check does not pass",
    "fallthrough": "execution leaves the function without returning through lp",
    "instruction-budget": "the closure did not return within the instruction budget",
    "region-cap": "the host check has eight regions and codeflash plus dataflash already use two; the remaining accesses do not fit",
    "no-observable": "the bytes do not write r10 or caller-visible memory, so a scenario would not check anything",
    "uninitialized-read": "the machine read a byte the harness did not initialize",
    "simulator": "the P1M-E machine did not return a report for this scenario",
    "harness-drift": "the machine's result does not match the harness interpreter, so the scenario window is not trusted",
    "host-unmapped": "the converted C dereferenced an address the scenario did not map",
    "host-fault": "the converted C aborted in the host check",
    "host-link": "the converted closure does not link; the missing callee is outside this batch",
    "host-compile": "the converted body does not compile in the host check",
    "trace-cap": "the machine stopped recording memory accesses at 4096, so the write set is incomplete",
    "dropped-return": "the bytes write a return value and the converted C is void",
    "invented-return": "the bytes leave the incoming r10 alone and the converted C returns a value",
    "return-mismatch": "the host return does not equal the original r10",
    "memory-mismatch": "a caller-visible memory write differs",
    "callee-saved": "the bytes change a callee-saved register the host check cannot observe",
    "stack-imbalance": "the bytes return with a different stack pointer",
    "verifier": "the agreements were rolled back because the retained oracle verifier did not pass",
}


class Harness(Exception):
    def __init__(self, kind: str, detail: str = "") -> None:
        self.kind = kind
        self.detail = detail
        super().__init__(detail or kind)


@dataclass
class Run:
    reads: set[tuple[int, int]] = field(default_factory=set)
    writes: set[tuple[int, int]] = field(default_factory=set)
    memory: dict[int, int] = field(default_factory=dict)
    r10_written: bool = False
    regs: list[int] = field(default_factory=lambda: [0] * 32)
    calls: set[int] = field(default_factory=set)
    steps: int = 0


@dataclass
class Planned:
    address: int
    name: str
    signature: str
    body: str
    runs: list[Run]
    calls: set[int]


def _u32(value: int) -> int:
    return value & 0xFFFFFFFF


def _sext(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return _u32(value)


def _space(addr: int, size: int) -> str:
    end = addr + size
    windows = (
        ("code", 0, 0x100000),
        ("code-ext", 0x01000000, 0x01008000),
        ("local", 0xFEBE0000, 0xFEC00000),
        ("alias", 0xFEDE0000, 0xFEE00000),
        ("global", 0xFEEF8000, 0xFEF08000),
        ("data", 0xFF200000, 0xFF208000),
    )
    for name, start, stop in windows:
        if start <= addr and end <= stop:
            return name
    return "mmio"


def _load_bodies() -> tuple[dict[str, str], set[str]]:
    bodies: dict[str, str] = {}
    duplicates: set[str] = set()
    for path in sorted((ROOT / "src" / "all").glob("*.c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        index = 0
        while index < len(lines):
            line = lines[index]
            if (
                not line.strip()
                or line.startswith("#")
                or line.startswith(" ")
                or line.startswith("\t")
                or line.startswith("/*")
                or line.startswith("//")
            ):
                index += 1
                continue
            start = index
            while index < len(lines) and "{" not in lines[index]:
                index += 1
            if index >= len(lines):
                break
            depth = 0
            while index < len(lines):
                depth += lines[index].count("{") - lines[index].count("}")
                index += 1
                if depth <= 0:
                    break
            chunk = "\n".join(lines[start:index]).strip() + "\n"
            match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
            if match is None:
                continue
            name = match.group(1)
            if name in bodies:
                duplicates.add(name)
            bodies[name] = chunk
    return bodies, duplicates


def _static_block(fn) -> str | None:
    for inst in fn.insts:
        if inst.kind == "abort":
            return "trap"
        if inst.kind == "callt":
            return "callt"
        if inst.kind in {"jarl_ind", "switch"}:
            return "indirect-call" if inst.kind == "jarl_ind" else "switch"
        if inst.kind == "jmp" and inst.reg not in {0, 31}:
            return "indirect-call"
        if "ldsr" in inst.stmt or "stsr" in inst.stmt or inst.text in {"di", "ei"}:
            return "system-register"
    return None


def _args(text: str) -> list[int]:
    if not text.strip():
        return []
    values = []
    for part in text.split(","):
        values.append(int(part.strip().rstrip("uU"), 0))
    return values


class _Machine:
    def __init__(self, code: bytes, data: bytes, data_base: int, functions: dict[int, object]) -> None:
        self.code = code
        self.data = data
        self.data_base = data_base
        self.functions = functions
        self.owner = {}
        for fn in functions.values():
            for inst in fn.insts:
                self.owner[inst.addr] = fn
        self.flags = [0, 0, 0, 0]
        self.ep_stack = False
        self.stack_regs = {3}
        self.fill = 0
        self.run = Run()
        self.regs = [0] * 32
        self.root = 0

    def execute(self, fn, params: list[tuple[bool, int]], fill: int) -> Run:
        self.fill = fill
        self.run = Run()
        self.flags = [0, 0, 0, 0]
        self.ep_stack = False
        self.stack_regs = {3}
        self.regs = [SENTINEL] * 32
        self.regs[0] = 0
        self.regs[3] = ENTRY_SP
        self.regs[4] = GP
        self.regs[5] = TP
        self.regs[31] = STOP
        for index, (pointer, ordinal) in enumerate(params):
            self.regs[6 + index] = ARG_BASE + index * ARG_STRIDE if pointer else ordinal
        self.root = fn.entry
        blocked = _static_block(fn)
        if blocked:
            raise Harness(blocked)
        self._block(fn, fn.entry)
        self.run.regs = self.regs[:]
        return self.run

    def _block(self, fn, pc: int) -> None:
        while self.run.steps < STEP_LIMIT:
            if pc == STOP:
                return
            inst = self._inst(pc)
            if inst is None or inst.addr not in fn.sites and self.owner.get(pc) is None:
                raise Harness("fallthrough")
            owner = self.owner.get(pc)
            if owner is None:
                raise Harness("fallthrough")
            self.run.steps += 1
            pc = self._step(owner, inst)
            if pc is None:
                return
        raise Harness("instruction-budget")

    def _inst(self, pc: int) -> Inst | None:
        owner = self.owner.get(pc)
        if owner is None:
            return None
        for inst in owner.insts:
            if inst.addr == pc:
                return inst
        return None

    def _step(self, fn, inst: Inst) -> int | None:
        nxt = inst.addr + inst.size
        kind = inst.kind
        if kind == "nop":
            return self._sequential(fn, nxt)
        if kind == "br":
            return self._jump(fn, inst.target)
        if kind == "b":
            return self._jump(fn, inst.target if self._take(inst.cc) else nxt)
        if kind == "loop":
            current = self.regs[inst.reg]
            self._flags_sub(current, 1)
            count = _u32(current - 1)
            self._write_reg(inst.reg, count)
            return self._jump(fn, inst.target if count else nxt)
        if kind == "jmp":
            return self._transfer(self.regs[inst.reg])
        if kind == "jmpdisp":
            return self._transfer(_u32(inst.base + self.regs[inst.reg]))
        if kind == "jr":
            return self._transfer(inst.target)
        if kind == "jarl":
            self._write_reg(inst.link, nxt)
            return self._transfer(inst.target)
        if kind == "dispose":
            self.regs[3] = _u32(self.regs[3] + (inst.slots << 2))
            for reg in (31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20):
                if inst.mask & (1 << reg):
                    if reg != 3:
                        self._write_reg(reg, self._read_ram(self.regs[3], 4, False, 3))
                    self.regs[3] = _u32(self.regs[3] + 4)
            if inst.ret:
                return self._transfer(self.regs[inst.ret])
            return self._sequential(fn, nxt)
        if kind != "alu":
            raise Harness("unmodeled", kind or inst.text)
        self._alu(inst.stmt.strip())
        return self._sequential(fn, nxt)

    def _sequential(self, fn, nxt: int) -> int:
        if nxt in fn.sites:
            return nxt
        raise Harness("fallthrough")

    def _jump(self, fn, target: int) -> int:
        if target not in fn.sites:
            raise Harness("external-branch")
        return target

    def _transfer(self, target: int) -> int | None:
        if target == STOP:
            return None
        owner = self.owner.get(target)
        if owner is None:
            raise Harness("external-branch")
        if owner.entry != target and target not in owner.sites:
            raise Harness("external-branch")
        blocked = _static_block(owner)
        if blocked:
            raise Harness(blocked)
        callee_size = sum(end - start + 1 for start, end in owner.ranges)
        if owner.entry != self.root and callee_size > MAX_BODY:
            raise Harness("large-callee")
        self.run.calls.add(owner.entry)
        return target

    def _take(self, cc: int) -> bool:
        z, s, ov, cy = self.flags
        return {
            0x0: ov,
            0x1: cy,
            0x2: z,
            0x3: cy or z,
            0x4: s,
            0x5: 1,
            0x6: s ^ ov,
            0x7: (s ^ ov) or z,
            0x8: 1 - ov,
            0x9: 1 - cy,
            0xA: 1 - z,
            0xB: 1 - (cy or z),
            0xC: 1 - s,
            0xE: 1 - (s ^ ov),
            0xF: 1 - ((s ^ ov) or z),
        }.get(cc & 0xF, 0) != 0

    def _flags_add(self, left: int, right: int) -> int:
        wide = left + right
        result = _u32(wide)
        sign_l, sign_r, sign_o = left >> 31, right >> 31, result >> 31
        self.flags = [
            int(result == 0),
            sign_o,
            int(sign_l == sign_r and sign_r != sign_o),
            int(wide >> 32),
        ]
        return result

    def _flags_sub(self, left: int, right: int) -> int:
        result = _u32(left - right)
        sign_l, sign_r, sign_o = left >> 31, right >> 31, result >> 31
        self.flags = [
            int(result == 0),
            sign_o,
            int(sign_l != sign_r and sign_r == sign_o),
            int(left < right),
        ]
        return result

    def _write_reg(self, reg: int, value: int, stack: bool = False) -> None:
        if reg == 0:
            return
        value = _u32(value)
        self.regs[reg] = value
        if reg == 10:
            self.run.r10_written = True
        self.stack_regs.discard(reg)
        if stack:
            self.stack_regs.add(reg)

    def _alu(self, stmt: str) -> None:
        match = re.match(r"camry_([A-Za-z0-9_]+)\((.*)\);?$", stmt)
        if match is None:
            if stmt in {"", "/* sync */", "/* nop */", "/* cache */", "/* pref */"}:
                return
            raise Harness("unmodeled", stmt or "empty")
        op, args = match.group(1), _args(match.group(2))
        handler = getattr(self, f"_op_{op}", None)
        if handler is None:
            raise Harness("unmodeled", op)
        handler(*args)

    def _op_mov(self, dst: int, src: int) -> None:
        self._write_reg(dst, self.regs[src], stack=src in self.stack_regs)

    def _op_movi(self, dst: int, imm: int) -> None:
        self._write_reg(dst, imm)

    def _op_movea(self, dst: int, src: int, imm: int) -> None:
        self._write_reg(dst, self.regs[src] + imm, stack=src in self.stack_regs)

    def _op_movhi(self, dst: int, src: int, imm: int) -> None:
        self._write_reg(dst, self.regs[src] + (_u32(imm) << 16), stack=src in self.stack_regs)

    def _op_add(self, dst: int, src: int) -> None:
        tagged = (dst in self.stack_regs) ^ (src in self.stack_regs)
        self._write_reg(dst, self._flags_add(self.regs[dst], self.regs[src]), stack=tagged)

    def _op_addi(self, dst: int, src: int, imm: int) -> None:
        self._write_reg(
            dst, self._flags_add(self.regs[src], _u32(imm)), stack=src in self.stack_regs,
        )

    def _op_addi_imm5(self, dst: int, imm: int) -> None:
        self._op_addi(dst, dst, imm)

    def _op_sub(self, dst: int, src: int) -> None:
        tagged = dst in self.stack_regs and src not in self.stack_regs
        self._write_reg(dst, self._flags_sub(self.regs[dst], self.regs[src]), stack=tagged)

    def _op_subr(self, dst: int, src: int) -> None:
        tagged = src in self.stack_regs and dst not in self.stack_regs
        self._write_reg(dst, self._flags_sub(self.regs[src], self.regs[dst]), stack=tagged)

    def _op_cmp(self, dst: int, src: int) -> None:
        self._flags_sub(self.regs[dst], self.regs[src])

    def _op_cmpi(self, dst: int, imm: int) -> None:
        self._flags_sub(self.regs[dst], _u32(imm))

    def _logic(self, dst: int, value: int) -> None:
        value = _u32(value)
        self.flags[0] = int(value == 0)
        self.flags[1] = value >> 31
        self.flags[2] = 0
        self._write_reg(dst, value)

    def _op_and(self, dst: int, src: int) -> None:
        self._logic(dst, self.regs[dst] & self.regs[src])

    def _op_andi(self, dst: int, src: int, imm: int) -> None:
        self._logic(dst, self.regs[src] & _u32(imm))

    def _op_or(self, dst: int, src: int) -> None:
        self._logic(dst, self.regs[dst] | self.regs[src])

    def _op_ori(self, dst: int, src: int, imm: int) -> None:
        self._logic(dst, self.regs[src] | _u32(imm))

    def _op_xor(self, dst: int, src: int) -> None:
        self._logic(dst, self.regs[dst] ^ self.regs[src])

    def _op_xori(self, dst: int, src: int, imm: int) -> None:
        self._logic(dst, self.regs[src] ^ _u32(imm))

    def _op_not(self, dst: int, src: int) -> None:
        self._logic(dst, ~self.regs[src])

    def _shift(self, dst: int, value: int, amount: int, direction: str) -> None:
        amount &= 31
        value = _u32(value)
        if direction == "left":
            result = _u32(value << amount)
            carry = 0 if amount == 0 else (value >> (32 - amount)) & 1
        elif direction == "sar":
            signed = value - 0x100000000 if value >> 31 else value
            result = _u32(signed >> amount)
            carry = 0 if amount == 0 else (value >> (amount - 1)) & 1
        else:
            result = value >> amount
            carry = 0 if amount == 0 else (value >> (amount - 1)) & 1
        self.flags = [int(result == 0), result >> 31, 0, carry]
        self._write_reg(dst, result)

    def _op_shl_imm(self, dst: int, amount: int) -> None:
        self._shift(dst, self.regs[dst], amount, "left")

    def _op_shl_reg(self, dst: int, src: int, amount: int) -> None:
        self._shift(dst, self.regs[src], self.regs[amount], "left")

    def _op_shr(self, dst: int, amount: int) -> None:
        self._shift(dst, self.regs[dst], amount, "right")

    def _op_shr_reg(self, dst: int, src: int, amount: int) -> None:
        self._shift(dst, self.regs[src], self.regs[amount], "right")

    def _op_sar_imm(self, dst: int, amount: int) -> None:
        self._shift(dst, self.regs[dst], amount, "sar")

    def _op_sar_reg(self, dst: int, src: int, amount: int) -> None:
        self._shift(dst, self.regs[src], self.regs[amount], "sar")

    def _op_zxb(self, reg: int) -> None:
        self._logic(reg, self.regs[reg] & 0xFF)

    def _op_zxh(self, reg: int) -> None:
        self._logic(reg, self.regs[reg] & 0xFFFF)

    def _op_sxb(self, reg: int) -> None:
        self._write_reg(reg, _sext(self.regs[reg], 8))

    def _op_sxh(self, reg: int) -> None:
        self._write_reg(reg, _sext(self.regs[reg], 16))

    def _op_setf(self, dst: int, cc: int) -> None:
        self._write_reg(dst, 1 if self._take(cc) else 0)

    def _op_cmovi(self, dst: int, fallback: int, imm: int, cc: int) -> None:
        if self._take(cc):
            self._write_reg(dst, imm)
            return
        self._write_reg(dst, self.regs[fallback], stack=fallback in self.stack_regs)

    def _op_cmov(self, dst: int, fallback: int, taken: int, cc: int) -> None:
        chosen = taken if self._take(cc) else fallback
        self._write_reg(dst, self.regs[chosen], stack=chosen in self.stack_regs)

    def _op_cmp_only(self) -> None:
        return

    def _load(self, dst: int, base: int, disp: int, size: int, signed: bool) -> None:
        self._write_reg(dst, self._read_ram(_u32(self.regs[base] + disp), size, signed, base))

    def _store(self, src: int, base: int, disp: int, size: int) -> None:
        self._write_ram(_u32(self.regs[base] + disp), size, self.regs[src], base)

    def _op_ld8u(self, dst: int, base: int, disp: int) -> None:
        self._load(dst, base, disp, 1, False)

    def _op_ld8s(self, dst: int, base: int, disp: int) -> None:
        self._load(dst, base, disp, 1, True)

    def _op_ld16u(self, dst: int, base: int, disp: int) -> None:
        self._load(dst, base, disp, 2, False)

    def _op_ld16s(self, dst: int, base: int, disp: int) -> None:
        self._load(dst, base, disp, 2, True)

    def _op_ld32(self, dst: int, base: int, disp: int) -> None:
        self._load(dst, base, disp, 4, False)

    def _op_st8(self, src: int, base: int, disp: int) -> None:
        self._store(src, base, disp, 1)

    def _op_st16(self, src: int, base: int, disp: int) -> None:
        self._store(src, base, disp, 2)

    def _op_st32(self, src: int, base: int, disp: int) -> None:
        self._store(src, base, disp, 4)

    def _bit(self, base: int, disp: int, bit: int, kind: int) -> None:
        addr = _u32(self.regs[base] + disp)
        value = self._read_ram(addr, 1, False, base)
        mask = 1 << (bit & 7)
        self.flags[0] = int((value & mask) == 0)
        if kind == 0:
            self._write_ram(addr, 1, value | mask, base)
        elif kind == 1:
            self._write_ram(addr, 1, value ^ mask, base)
        elif kind == 2:
            self._write_ram(addr, 1, value & ~mask, base)

    def _op_set1(self, base: int, disp: int, bit: int) -> None:
        self._bit(base, disp, bit, 0)

    def _op_not1(self, base: int, disp: int, bit: int) -> None:
        self._bit(base, disp, bit, 1)

    def _op_clr1(self, base: int, disp: int, bit: int) -> None:
        self._bit(base, disp, bit, 2)

    def _op_tst1(self, base: int, disp: int, bit: int) -> None:
        self._bit(base, disp, bit, 3)

    def _op_set1r(self, base: int, bitreg: int) -> None:
        self._bit(base, 0, self.regs[bitreg], 0)

    def _op_not1r(self, base: int, bitreg: int) -> None:
        self._bit(base, 0, self.regs[bitreg], 1)

    def _op_clr1r(self, base: int, bitreg: int) -> None:
        self._bit(base, 0, self.regs[bitreg], 2)

    def _op_tst1r(self, base: int, bitreg: int) -> None:
        self._bit(base, 0, self.regs[bitreg], 3)

    def _op_prepare(self, mask: int, slots: int, mode: int, imm: int) -> None:
        for reg in (20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31):
            if mask & (1 << reg):
                self.regs[3] = _u32(self.regs[3] - 4)
                self._write_ram(self.regs[3], 4, self.regs[reg], 3)
        self.regs[3] = _u32(self.regs[3] - (slots << 2))
        if mode == 1:
            self.regs[30] = self.regs[3]
            self.ep_stack = True
            self.stack_regs.add(30)
        elif mode == 2:
            self.regs[30] = _u32(imm)
            self.ep_stack = False
            self.stack_regs.discard(30)
        elif mode == 3:
            self.regs[30] = _u32(imm << 16)
            self.ep_stack = False
            self.stack_regs.discard(30)
        elif mode == 4:
            self.regs[30] = _u32(imm)
            self.ep_stack = False
            self.stack_regs.discard(30)

    def _op_pushsp(self, low: int, high: int) -> None:
        if low > high:
            return
        for reg in range(low, high + 1):
            self.regs[3] = _u32(self.regs[3] - 4)
            self._write_ram(self.regs[3], 4, self.regs[reg], 3)

    def _op_popsp(self, low: int, high: int) -> None:
        if low > high:
            return
        for reg in range(high, low - 1, -1):
            if reg != 3:
                self._write_reg(reg, self._read_ram(self.regs[3], 4, False, 3))
            self.regs[3] = _u32(self.regs[3] + 4)

    def _mul(self, left: int, right: int, signed: bool) -> tuple[int, int]:
        if signed:
            product = (left - 0x100000000 if left >> 31 else left) * (
                right - 0x100000000 if right >> 31 else right
            )
        else:
            product = left * right
        return _u32(product), _u32(product >> 32)

    def _op_mul(self, lo: int, hi: int, left: int, right: int, signed: int) -> None:
        low, high = self._mul(self.regs[left], self.regs[right], bool(signed))
        self._write_reg(lo, low)
        self._write_reg(hi, high)

    def _op_muli(self, lo: int, hi: int, imm: int) -> None:
        low, high = self._mul(self.regs[lo], _u32(imm), True)
        self._write_reg(lo, low)
        self._write_reg(hi, high)

    def _op_mului(self, lo: int, hi: int, imm: int) -> None:
        low, high = self._mul(self.regs[lo], _u32(imm), False)
        self._write_reg(lo, low)
        self._write_reg(hi, high)

    def _op_mulh(self, dst: int, src: int) -> None:
        left = _sext(self.regs[src], 16)
        right = _sext(self.regs[dst], 16)
        left = left - 0x100000000 if left >> 31 else left
        right = right - 0x100000000 if right >> 31 else right
        self._write_reg(dst, left * right)

    def _op_mulhi(self, dst: int, src: int, imm: int) -> None:
        left = _sext(self.regs[src], 16)
        left = left - 0x100000000 if left >> 31 else left
        signed = imm - 0x100000000 if _u32(imm) >> 31 else imm
        self._write_reg(dst, left * signed)

    def _op_div3(self, quot: int, divisor: int, rem: int, signed: int, half: int) -> None:
        dividend = self.regs[quot]
        divider = self.regs[divisor]
        if half:
            divider = _sext(divider, 16)
        if divider == 0:
            self.flags[2] = 1
            return
        if signed and dividend == 0x80000000 and divider == 0xFFFFFFFF:
            self.flags = [0, 1, 1, self.flags[3]]
            self._write_reg(quot, 0x80000000)
            self._write_reg(rem, 0)
            return
        if signed:
            left = dividend - 0x100000000 if dividend >> 31 else dividend
            right = divider - 0x100000000 if divider >> 31 else divider
            value, remainder = int(left / right), left - int(left / right) * right
        else:
            value, remainder = divmod(dividend, divider)
        result = _u32(value)
        self.flags = [int(result == 0), result >> 31, 0, self.flags[3]]
        self._write_reg(quot, result)
        self._write_reg(rem, _u32(remainder))

    def _kind_of(self, addr: int, size: int, base: int) -> str:
        if size == 2 and addr & 1 or size == 4 and addr & 3:
            raise Harness("misaligned")
        stack_base = base in self.stack_regs or (base == 30 and self.ep_stack)
        if STACK_LO <= addr and addr + size <= STACK_HI:
            if not stack_base:
                raise Harness("harness-overlap")
            return "stack"
        arg_end = ARG_BASE + ARG_COUNT * ARG_STRIDE
        if ARG_BASE <= addr and addr + size <= arg_end:
            if stack_base:
                raise Harness("stack-frame")
            return "arg"
        if stack_base:
            raise Harness("stack-frame")
        space = _space(addr, size)
        if space == "alias":
            raise Harness("ram-alias")
        if space == "code-ext":
            raise Harness("code-extension")
        if space == "mmio":
            raise Harness("mmio")
        return space

    def _read_ram(self, addr: int, size: int, signed: bool, base: int) -> int:
        kind = self._kind_of(addr, size, base)
        image = self._image(addr, size)
        if image is None:
            if kind in {"code", "data", "code-ext"}:
                raise Harness("code-extension")
            if kind not in {"stack", "arg", "local", "global"}:
                raise Harness("mmio")
            raw = 0
            for offset in range(size):
                raw |= self.run.memory.get(addr + offset, self.fill) << (8 * offset)
            self.run.reads.add((addr, size))
        else:
            raw = image
        if kind in {"local", "global", "stack", "arg"}:
            self.run.reads.add((addr, size))
        return _sext(raw, size * 8) if signed else raw

    def _image(self, addr: int, size: int) -> int | None:
        if 0 <= addr and addr + size <= len(self.code):
            return int.from_bytes(self.code[addr:addr + size], "little")
        if self.data_base <= addr and addr + size <= self.data_base + len(self.data):
            offset = addr - self.data_base
            return int.from_bytes(self.data[offset:offset + size], "little")
        return None

    def _write_ram(self, addr: int, size: int, value: int, base: int) -> None:
        kind = self._kind_of(addr, size, base)
        if kind == "code":
            raise Harness("code-write")
        if kind == "data":
            raise Harness("dataflash-write")
        if kind not in {"stack", "arg", "local", "global"}:
            raise Harness("mmio")
        for offset in range(size):
            self.run.memory[addr + offset] = (value >> (8 * offset)) & 0xFF
        self.run.writes.add((addr, size))


def _params_of(signature: str, name: str) -> list[bool]:
    _return_type, params = parse_signature(signature, name)
    if len(params) > 4:
        raise Harness("stack-arguments")
    return ["*" in param for param in params]


def _return_width(return_type: str) -> int:
    if "*" in return_type:
        return 32
    if return_type in {"byte", "uchar", "uint8_t", "undefined1", "char", "bool"}:
        return 8
    if return_type in {"ushort", "short", "uint16_t", "int16_t", "undefined2"}:
        return 16
    return 32


def _observable(run: Run) -> bool:
    for addr, size in run.writes:
        if not (STACK_LO <= addr and addr + size <= STACK_HI):
            return True
    # A write of the incoming sentinel is not distinguishable from r10 being untouched.
    return run.r10_written and run.regs[10] != SENTINEL


def _clusters(spans: list[tuple[int, int]], gap: int) -> list[tuple[int, int]]:
    if not spans:
        return []
    ordered = sorted(spans)
    start, end = ordered[0][0], ordered[0][0] + ordered[0][1]
    packed = []
    for addr, size in ordered[1:]:
        if addr <= end + gap:
            end = max(end, addr + size)
            continue
        packed.append((start, end - start))
        start, end = addr, addr + size
    packed.append((start, end - start))
    return packed


def _windows(runs: list[Run], pointers: list[bool] | None = None) -> list[tuple[int, int]]:
    reads: list[tuple[int, int]] = []
    stack = False
    arg = False
    for run in runs:
        for addr, size in run.reads | run.writes:
            if STACK_LO <= addr and addr + size <= STACK_HI:
                stack = True
            elif ARG_BASE <= addr and addr + size <= ARG_BASE + ARG_COUNT * ARG_STRIDE:
                arg = True
            else:
                reads.append((addr, size))
    windows = []
    if stack:
        windows.append((STACK_LO, STACK_HI - STACK_LO))
    pointer_slots = [
        ARG_BASE + index * ARG_STRIDE
        for index, is_pointer in enumerate(pointers or [])
        if is_pointer
    ]
    if arg or pointer_slots:
        touched = [
            addr
            for run in runs
            for addr, size in run.reads | run.writes
            if ARG_BASE <= addr < ARG_BASE + ARG_COUNT * ARG_STRIDE
        ]
        touched.extend(pointer_slots)
        last = max(touched)
        slot = (last - ARG_BASE) // ARG_STRIDE + 1
        windows.append((ARG_BASE, slot * ARG_STRIDE))
    packed = _clusters(reads, 16)
    if len(windows) + len(packed) > 6 and packed:
        start = min(addr for addr, _size in reads)
        end = max(addr + size for addr, size in reads)
        if end - start <= 0x2000:
            packed = [(start, end - start)]
    if len(windows) + len(packed) > 6:
        raise Harness("region-cap")
    windows.extend(packed)
    return windows


def _write_spans(run: Run) -> list[tuple[int, int]]:
    spans = [
        (addr, size)
        for addr, size in run.writes
        if not (STACK_LO <= addr and addr + size <= STACK_HI)
    ]
    return _clusters(spans, 0)


def _preserved(run: Run) -> str | None:
    if run.regs[3] != ENTRY_SP:
        return "stack-imbalance"
    expected = {4: GP, 5: TP}
    for reg in (4, 5, *range(20, 30)):
        if run.regs[reg] != expected.get(reg, SENTINEL):
            return "callee-saved"
    return None


def _scenario(name: str, address: int, run: Run, fill: int, params: list[tuple[bool, int]], windows: list[tuple[int, int]]) -> dict:
    registers = {
        "sp": hex(ENTRY_SP),
        "gp": hex(GP),
        "tp": hex(TP),
        "lp": hex(STOP),
        "PSW": "0x20",
        "PMR": "0x0",
    }
    for index, (pointer, ordinal) in enumerate(params):
        registers[f"r{6 + index}"] = hex(ARG_BASE + index * ARG_STRIDE if pointer else ordinal)
    checks = [{
        "name": "r10",
        "kind": "register",
        "register": "r10",
        "equals": "0x0",
    }]
    for reg, label in ((3, "sp"), (4, "gp"), (5, "tp")):
        checks.append({
            "name": label,
            "kind": "register",
            "register": label,
            "equals": "0x0",
        })
    for addr, size in _write_spans(run):
        checks.append({
            "name": f"mem-{addr:x}",
            "kind": "memory",
            "address": hex(addr),
            "size": size,
            "equals_hex": "00" * size,
        })
    return {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": name,
        "entry": {"role": "generated", "scope": "resolved-address", "address": hex(address)},
        "max_instructions": 20000,
        "reset": "none",
        "gpr_fill": hex(SENTINEL),
        "registers": registers,
        "stop_addresses": [hex(STOP)],
        "memory": [
            {"address": hex(base), "size": size, "fill": fill, "evidence": "generated"}
            for base, size in windows
        ],
        "checks": checks,
    }


def _hex_bytes(run: Run, addr: int, size: int) -> str:
    return "".join(f"{run.memory.get(addr + offset, 0):02x}" for offset in range(size))


def _report_map(report: dict) -> dict[str, dict]:
    return {row.get("name"): row for row in report.get("checks", [])}


def _sim_chunks(paths: list[Path]) -> list[dict]:
    from tools.emulation.p1me_machine import capture_many as capture

    reports: list[dict] = []

    def run(chunk: list[Path]) -> None:
        if not chunk:
            return
        try:
            reports.extend(capture(TARGET, chunk, REPO_ROOT / "build" / "tmp" / "camry-oracle"))
        except P1MEMachineError:
            if len(chunk) == 1:
                reports.append({
                    "scenario": chunk[0].stem,
                    "passed": False,
                    "termination_reason": "simulator",
                    "checks": [],
                    "memory_accesses": [],
                })
                return
            mid = len(chunk) // 2
            run(chunk[:mid])
            run(chunk[mid:])

    for start in range(0, len(paths), SIM_CHUNK):
        batch = paths[start:start + SIM_CHUNK]
        print(f"simulate {start + len(batch)}/{len(paths)}", flush=True)
        run(batch)
    return reports


def _compile(directory: Path, names: list[str], bodies: dict[str, str]) -> tuple[ctypes.CDLL | None, str]:
    source = directory / "candidates.c"
    support = directory / "support.c"
    library = directory / "liboracle.dylib"
    support.write_text(
        "unsigned camry_gp, camry_tp, camry_sp, camry_pmr;\n",
        encoding="utf-8",
    )
    parts = ['#include "common.h"', ""]
    for name in names:
        parts.append(bodies[name])
    source.write_text("\n".join(parts) + "\n", encoding="utf-8")
    result = subprocess.run(
        [
            "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-fwrapv",
            "-Wno-unused-variable", "-Wno-unused-parameter",
            "-Wno-unused-function", "-Wno-unused-label",
            "-Wno-pointer-to-int-cast", "-Wno-int-to-pointer-cast",
            "-Wno-bitwise-op-parentheses", "-Wno-sign-compare", "-Wno-parentheses",
            "-Wno-pointer-sign", "-Wno-incompatible-pointer-types",
            "-Wno-unused-but-set-variable",
            "-Wno-uninitialized", "-Wno-deprecated-non-prototype",
            "-DCAMRY_HOST",
            "-I", str(ROOT / "include"),
            "-I", str(ROOT / "src" / "all"),
            "-dynamiclib", "-o", str(library),
            str(source), str(support), str(HOST_MEM),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None, (result.stderr or result.stdout)
    return ctypes.CDLL(library), ""


def _drop_unlinked(names: list[str], bodies: dict[str, str], log: str) -> list[str]:
    missing = re.findall(r'"_([^"]+)", referenced from:', log)
    if not missing:
        missing = re.findall(r"undefined reference to [`']([^']+)'", log)
    if not missing:
        return []
    dropped = []
    for name in names:
        text = bodies[name]
        if any(re.search(rf"\b{re.escape(symbol)}\b", text) for symbol in missing):
            dropped.append(name)
    return dropped


_CALL_WORDS = {
    "if", "for", "while", "switch", "return", "sizeof", "defined", "offsetof",
    "static_assert", "_Generic",
}


def _c_calls(body: str) -> set[str]:
    return {
        name for name in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", body)
        if name not in _CALL_WORDS
    }


def _defined_lines(text: str) -> set[str]:
    names = set()
    for line in text.splitlines():
        match = re.match(r"^[A-Za-z_][\w\s\*]*\s([A-Za-z_][A-Za-z0-9_]*)\s*\(", line)
        if match and not line.rstrip().endswith(";"):
            names.add(match.group(1))
    return names


def _src_definitions() -> set[str]:
    names: set[str] = set()
    for path in (ROOT / "src").glob("*.c"):
        if path.name == "oracle.c":
            continue
        names.update(_defined_lines(path.read_text(encoding="utf-8")))
    return names


def _macro_names() -> set[str]:
    header = ROOT / "src" / "all" / "common.h"
    if not header.exists():
        return set()
    return set(re.findall(
        r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        header.read_text(encoding="utf-8"),
        re.M,
    ))


def _linkable(
    roots: list[str],
    bodies: dict[str, str],
    defined: set[str],
    symbols: set[str],
    macros: set[str],
) -> tuple[set[str], list[str]]:
    memo: dict[str, bool] = {}

    def ok(name: str) -> bool:
        if name in memo:
            return memo[name]
        if name in defined or name in macros:
            memo[name] = True
            return True
        if name not in bodies:
            memo[name] = name not in symbols
            return memo[name]
        memo[name] = True
        good = all(callee == name or ok(callee) for callee in _c_calls(bodies[name]))
        memo[name] = good
        return good

    kept = {name for name in roots if ok(name)}
    support: list[str] = []
    seen = set(kept) | defined | macros
    pending = list(kept)
    while pending:
        name = pending.pop()
        body = bodies.get(name)
        if body is None:
            continue
        for callee in _c_calls(body):
            if callee in seen or callee not in bodies:
                continue
            seen.add(callee)
            support.append(callee)
            pending.append(callee)
    return kept, support


def _error_names(log: str, names: list[str], bodies: dict[str, str]) -> list[str]:
    lines = [int(number) for number in re.findall(r"candidates\.c:(\d+):", log)]
    if not lines:
        return []
    cursor = 3
    spans = []
    for name in names:
        spans.append((cursor, name))
        cursor += bodies[name].count("\n") + 1
    found = []
    for line in lines:
        owner = None
        for start, name in spans:
            if start <= line:
                owner = name
            else:
                break
        if owner and owner not in found:
            found.append(owner)
    return found


def _unbuffer_stderr() -> None:
    libc = ctypes.CDLL(None)
    for symbol in ("__stderrp", "stderr"):
        try:
            stream = ctypes.c_void_p.in_dll(libc, symbol)
        except ValueError:
            continue
        libc.setvbuf(stream, None, 2, 0)
        return


def _bind_host(library: ctypes.CDLL) -> None:
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32 = ctypes.c_uint32
    library.camry_host_reset.argtypes = []
    library.camry_host_reset.restype = None
    library.camry_host_add.argtypes = [u32, u8p, u32]
    library.camry_host_add.restype = None
    library.camry_host_ptr.argtypes = [u32]
    library.camry_host_ptr.restype = u8p
    library.camry_host_addr.argtypes = [ctypes.c_void_p]
    library.camry_host_addr.restype = u32


def _host_child(library: ctypes.CDLL, planned: Planned, scenario: dict, code: bytes) -> None:
    _bind_host(library)
    mapped = materialize(scenario)
    code_view = view_of(bytearray(code))
    if mapped is None:
        images = scenario_regions(scenario)
        install_regions(library, code_view, len(code), images)
    else:
        memory, base = mapped
        if memory:
            view = view_of(memory)
            install_address_space(library, code_view, len(code), view, base, memory)
        images = [(base, memory)]
    before = [(base, bytes(data)) for base, data in images]
    returned = call_corpus(library, planned.name, planned.signature, scenario["registers"])
    for check in scenario["checks"]:
        if check.get("kind") == "register" and check.get("register") == "r10":
            expected = int(check["equals"], 16)
            if returned is None:
                raise Harness("dropped-return")
            if returned != expected:
                raise Harness("return-mismatch")
        elif check.get("kind") == "memory":
            address = int(check["address"], 16)
            size = int(check["size"])
            if read_regions(images, address, size).hex() != check["equals_hex"]:
                raise Harness("memory-mismatch")
    covered = []
    for check in scenario["checks"]:
        if check.get("kind") != "memory":
            continue
        address = int(check["address"], 16)
        covered.append((address, address + int(check["size"])))
    for (base, original), (_base, data) in zip(before, images):
        for offset, (old, new) in enumerate(zip(original, data)):
            if old == new:
                continue
            address = base + offset
            if any(start <= address < end for start, end in covered):
                continue
            raise Harness("memory-mismatch")


def _host_compare(
    library: ctypes.CDLL,
    planned: Planned,
    scenario: dict,
    code: bytes,
) -> str | None:
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        os.dup2(write_fd, 2)
        _unbuffer_stderr()
        signal.signal(signal.SIGALRM, lambda *_args: os._exit(1))
        signal.alarm(2)
        try:
            _host_child(library, planned, scenario, code)
        except Harness as exc:
            os.write(write_fd, exc.kind.encode())
            os._exit(1)
        except BaseException as exc:
            os.write(write_fd, str(exc).encode()[:400])
            os._exit(1)
        os._exit(0)
    os.close(write_fd)
    _pid, status = os.waitpid(pid, 0)
    detail = os.read(read_fd, 500).decode(errors="replace")
    os.close(read_fd)
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
        return None
    for kind in FAIL_KINDS:
        if kind in detail:
            return kind
    if "unmapped" in detail or "outside" in detail:
        return "host-unmapped"
    return "host-fault"


def _promote(
    planned: list[tuple[Planned, list[dict]]],
    support: list[str],
    bodies: dict[str, str],
) -> None:
    oracle_path = ROOT / "src" / "oracle.c"
    existing = oracle_path.read_text(encoding="utf-8") if oracle_path.exists() else '#include "common.h"\n'
    have = _defined_lines(existing)
    parts = [existing.rstrip(), ""]
    for name in support:
        if name in have:
            continue
        parts.append(bodies[name].rstrip())
        parts.append("")
        have.add(name)
    for item, _scenarios in sorted(planned, key=lambda row: row[0].address):
        if item.name in have:
            continue
        parts.append(item.body.rstrip())
        parts.append("")
    oracle_path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")

    matched_path = ROOT / "matched.jsonl"
    promoted = {item.address: item for item, _scenarios in planned}
    lines = []
    for line in matched_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        item = promoted.get(int(row["addr"], 16))
        if item is not None and row.get("status") == "converted":
            row = {
                "addr": row["addr"],
                "name": row["name"],
                "status": "equivalent",
                "form": "corpus",
                "signature": item.signature,
            }
            line = json.dumps(row, separators=(", ", ": "))
        lines.append(line)
    matched_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    oracle_rows = ROOT / "oracles.jsonl"
    with oracle_rows.open("a", encoding="utf-8") as handle:
        for _item, scenarios in planned:
            for scenario in scenarios:
                handle.write(json.dumps(scenario, separators=(",", ":")) + "\n")


def _restore(snapshots: dict[Path, str | None]) -> None:
    for path, text in snapshots.items():
        if text is None:
            if path.exists():
                path.unlink()
            continue
        path.write_text(text, encoding="utf-8")


def _verify() -> str | None:
    result = subprocess.run(
        ["uv", "run", "--locked", "python", "tests/decomp/verify_camry_decomp.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return None
    tail = ((result.stderr or "") + "\n" + (result.stdout or "")).strip().splitlines()
    return " | ".join(tail[-24:])


def _keep_verified(
    passed: list[tuple[Planned, list[dict]]],
    snapshots: dict[Path, str | None],
    bodies: dict[str, str],
    defined: set[str],
    symbols: set[str],
    macros: set[str],
    reject,
    examples: dict[str, str],
) -> list[tuple[Planned, list[dict]]]:
    if not passed:
        return []
    kept, support = _linkable(
        [item.name for item, _rows in passed], bodies, defined, symbols, macros,
    )
    runnable = [(item, rows) for item, rows in passed if item.name in kept]
    for item, _rows in passed:
        if item.name not in kept:
            reject("host-link", item.name)
    if not runnable:
        return []
    _restore(snapshots)
    _promote(runnable, support, bodies)
    error = _verify()
    if error is None:
        return runnable
    _restore(snapshots)
    named = [item for item, _rows in runnable if item.name in error]
    if named and len(named) < len(runnable):
        for item in named:
            reject("verifier", item.name)
        examples["verifier"] = error[:180]
        rest = [(item, rows) for item, rows in runnable if item not in named]
        return _keep_verified(rest, snapshots, bodies, defined, symbols, macros, reject, examples)
    if len(runnable) == 1 or "FAIL " not in error:
        for item, _rows in runnable:
            reject("verifier", item.name)
        examples["verifier"] = error[:180]
        return []
    mid = len(runnable) // 2
    left = _keep_verified(runnable[:mid], snapshots, bodies, defined, symbols, macros, reject, examples)
    right = _keep_verified(runnable[mid:], snapshots, bodies, defined, symbols, macros, reject, examples)
    return left + right


def run_oracles() -> int:
    metadata = resolve_target(TARGET)[1]
    code = load_image()
    data_base = int(metadata["dataflash_base"], 16)
    data = (REPO_ROOT / metadata["dataflash"]).read_bytes()
    symbols = load_symbols()
    status = {int(row["addr"], 16): row for row in load_matched()}
    bodies, duplicates = _load_bodies()
    functions = {}
    for row in symbols:
        fn = walk_symbol(code, row)
        if fn is not None:
            functions[fn.entry] = fn
    machine = _Machine(code, data, data_base, functions)
    counts: Counter[str] = Counter()
    examples: dict[str, str] = {}
    planned: list[Planned] = []
    hand = _prototype_names()
    rejected: set[str] = set()

    def reject(kind: str, name: str, detail: str = "") -> None:
        if name in rejected:
            return
        rejected.add(name)
        label = f"{kind} {detail}".strip() if kind == "unmodeled" else kind
        counts[label] += 1
        examples.setdefault(label, name)

    verified = converted = unconvertible = 0
    for row in symbols:
        address = int(row["addr"], 16)
        state = status.get(address, {})
        kind = state.get("status")
        if kind == "equivalent":
            verified += 1
            continue
        if kind == "unconvertible":
            unconvertible += 1
            continue
        converted += 1
        name = row["name"]
        if address >= len(code):
            reject("outside-codeflash", name)
            continue
        if row["size"] > MAX_BODY:
            reject("large", name)
            continue
        if name in duplicates:
            reject("duplicate-body", name)
            continue
        if name not in bodies or name in hand:
            reject("no-converted-body", name)
            continue
        body = bodies[name]
        if "__" in body:
            reject("host-intrinsic", name)
            continue
        fn = functions.get(address)
        if fn is None:
            reject("undecoded", name)
            continue
        try:
            signature = _c_signature(body)
            pointers = _params_of(signature, name)
        except (AssertionError, Harness, ValueError) as exc:
            reject(getattr(exc, "kind", "stack-arguments"), name, getattr(exc, "detail", ""))
            continue
        runs = []
        failed = False
        for index, fill in ((0, 0), (1, 0xA5)):
            params = [
                (pointer, 0 if index == 0 or pointer else index + ordinal)
                for ordinal, pointer in enumerate(pointers)
            ]
            # Integer scenario B uses 1, 2, 3, 4. Pointers stay at the buffers.
            if index == 1:
                params = [
                    (pointer, ordinal + 1)
                    for ordinal, pointer in enumerate(pointers)
                ]
            try:
                runs.append(machine.execute(fn, params, fill))
            except Harness as exc:
                reject(exc.kind, name, exc.detail)
                failed = True
                break
        if failed:
            continue
        preserved = _preserved(runs[0]) or _preserved(runs[1])
        if preserved:
            reject(preserved, name)
            continue
        if not any(_observable(run) for run in runs):
            reject("no-observable", name)
            continue
        try:
            windows = _windows(runs, pointers)
        except Harness as exc:
            reject(exc.kind, name, exc.detail)
            continue
        calls = set().union(*(run.calls for run in runs))
        if any(functions[target].name not in bodies for target in calls if target in functions):
            reject("no-converted-body", name)
            continue
        planned.append(Planned(address, name, signature, body, runs, calls))

    print(f"harnessed {len(planned)}", flush=True)
    needed = []
    for item in planned:
        for address in item.calls | {item.address}:
            fn = functions.get(address)
            if fn is None or fn.name not in bodies:
                continue
            if fn.name not in needed:
                needed.append(fn.name)
    # Keep only roots whose whole executed closure is in the compiled set.
    dropped: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="camry-oracle-") as directory:
        directory_path = Path(directory)
        def fit(names: list[str]) -> tuple[ctypes.CDLL | None, list[str]]:
            names = [name for name in names if name not in dropped]
            if not names:
                return None, []
            compiled, log = _compile(directory_path, names, bodies)
            if compiled is not None:
                return compiled, names
            linked = _drop_unlinked(names, bodies, log)
            if linked:
                for name in linked:
                    dropped.add(name)
                    reject("host-link", name)
                return fit(names)
            bad = _error_names(log, names, bodies)
            if bad:
                for name in bad:
                    dropped.add(name)
                    reject("host-compile", name)
                return fit(names)
            if len(names) == 1:
                print(log[-800:], flush=True)
                dropped.add(names[0])
                reject("host-compile", names[0])
                return None, []
            mid = len(names) // 2
            print(f"compile split {len(names)}", flush=True)
            left_lib, left = fit(names[:mid])
            right_lib, right = fit(names[mid:])
            del left_lib, right_lib
            union = left + right
            if len(union) == len([name for name in names if name not in dropped]):
                print(log[-800:], flush=True)
                for name in names:
                    dropped.add(name)
                    reject("host-compile", name)
                return None, []
            return fit(union)

        library, _kept = fit([name for name in needed if name not in dropped])
        if library is None:
            for item in planned:
                reject("host-compile", item.name)
            _print_summary(verified, converted, unconvertible, counts, examples, 0, 0)
            return 0
        runnable = []
        for item in planned:
            closure = {functions[address].name for address in item.calls if address in functions}
            closure.add(item.name)
            if closure & dropped:
                if item.name not in dropped:
                    reject("host-link", item.name)
                continue
            runnable.append(item)
        if not runnable:
            _print_summary(verified, converted, unconvertible, counts, examples, 0, 0)
            return 0

        work = REPO_ROOT / "build" / "tmp" / "camry-oracle"
        if work.exists():
            for child in work.glob("*"):
                child.unlink()
        work.mkdir(parents=True, exist_ok=True)
        scenarios = []
        owners = []
        for item in runnable:
            pointers = _params_of(item.signature, item.name)
            windows = _windows(item.runs, pointers)
            for index, (fill, run) in enumerate(zip((0, 0xA5), item.runs)):
                params = [
                    (pointer, 0 if index == 0 or pointer else ordinal + 1)
                    for ordinal, pointer in enumerate(pointers)
                ]
                if index == 1:
                    params = [(pointer, ordinal + 1) for ordinal, pointer in enumerate(pointers)]
                scenario = _scenario(
                    f"camry_diff_{item.address:x}_{index}",
                    item.address,
                    run,
                    fill,
                    params,
                    windows,
                )
                path = work / f"{scenario['name']}.json"
                path.write_text(json.dumps(scenario), encoding="utf-8")
                scenarios.append(path)
                owners.append((item, run, scenario))
        reports = _sim_chunks(scenarios)
        by_scenario = {}
        for report in reports:
            by_scenario[report.get("scenario") or Path(report.get("report_path", "")).stem] = report

        passed: list[tuple[Planned, list[dict]]] = []
        fail = 0
        grouped: dict[int, list[tuple[Run, dict, dict]]] = defaultdict(list)
        for item, run, scenario in owners:
            grouped[item.address].append((run, scenario, by_scenario.get(scenario["name"], {})))
        for item in runnable:
            rows = grouped[item.address]
            ok = True
            saved = []
            for run, scenario, report in rows:
                kind = _judge(item, run, scenario, report)
                if kind is None:
                    final = _finalize(item, run, scenario, report)
                    kind = _host_compare(library, item, final, code)
                    if kind is None and useful_oracle(final):
                        saved.append(final)
                if kind is not None:
                    reject(kind, item.name)
                    if kind in FAIL_KINDS:
                        fail += 1
                    ok = False
                    break
            if ok and saved:
                passed.append((item, saved))
            elif ok:
                reject("no-observable", item.name)
        del library

    if not passed:
        _print_summary(verified, converted, unconvertible, counts, examples, 0, fail)
        return 0

    snapshots = {
        path: path.read_text(encoding="utf-8") if path.exists() else None
        for path in (ROOT / "matched.jsonl", ROOT / "oracles.jsonl", ROOT / "src" / "oracle.c")
    }
    defined = _src_definitions()
    symbols_names = {row["name"] for row in symbols}
    macros = _macro_names()
    final = _keep_verified(passed, snapshots, bodies, defined, symbols_names, macros, reject, examples)
    _restore(snapshots)
    if not final:
        _print_summary(verified, converted, unconvertible, counts, examples, 0, fail)
        return 0
    kept, support = _linkable(
        [item.name for item, _rows in final], bodies, defined, symbols_names, macros,
    )
    final = [(item, rows) for item, rows in final if item.name in kept]
    _promote(final, support, bodies)
    verifier = _verify()
    if verifier is not None:
        _restore(snapshots)
        for item, _rows in final:
            reject("verifier", item.name)
        examples["verifier"] = verifier[:180]
        _print_summary(verified, converted, unconvertible, counts, examples, 0, fail)
        return 1
    _print_summary(
        verified + len(final),
        converted - len(final),
        unconvertible,
        counts,
        examples,
        len(final),
        fail,
    )
    return 0


def _judge(item: Planned, run: Run, scenario: dict, report: dict) -> str | None:
    if not report or report.get("termination_reason") in {None, "simulator"}:
        return "simulator"
    if report.get("termination_reason") != "stop-address":
        reason = report.get("termination_reason") or "simulator"
        fault = (report.get("fault") or {}).get("kind")
        if reason == "instruction-budget":
            return "instruction-budget"
        if fault:
            return fault if fault in REASONS else "simulator"
        return "simulator"
    if len(report.get("memory_accesses") or []) >= 4096:
        return "trace-cap"
    checks = _report_map(report)
    for label, expected in (("sp", ENTRY_SP), ("gp", GP), ("tp", TP)):
        actual = checks.get(label, {}).get("actual")
        if actual is None or int(actual, 16) != expected:
            return "stack-imbalance" if label == "sp" else "callee-saved"
    sim_r10 = int(checks["r10"]["actual"], 16) if "r10" in checks else SENTINEL
    if run.regs[10] != sim_r10:
        return "harness-drift"
    writes = set()
    for row in report.get("memory_accesses") or []:
        if row.get("kind") != "write":
            continue
        addr = int(row["address"], 16)
        for offset in range(int(row["size"])):
            writes.add(addr + offset)
    interpreted = {addr + offset for addr, size in run.writes for offset in range(size)}
    if not writes <= interpreted:
        return "harness-drift"
    for addr, size in _write_spans(run):
        actual = checks.get(f"mem-{addr:x}", {}).get("actual")
        if not actual or actual == "unavailable" or len(actual) != size * 2:
            return "uninitialized-read"
        if actual != _hex_bytes(run, addr, size):
            return "harness-drift"
    return_type, _params = parse_signature(item.signature, item.name)
    bytes_return = sim_r10 != SENTINEL
    if not bytes_return and return_type != "void":
        return "invented-return"
    if bytes_return and return_type == "void":
        return "dropped-return"
    return None


def _finalize(item: Planned, run: Run, scenario: dict, report: dict) -> dict:
    checks = _report_map(report)
    return_type, _params = parse_signature(item.signature, item.name)
    saved = dict(scenario)
    saved_checks = []
    if return_type != "void" and "r10" in checks:
        width = _return_width(return_type)
        value = int(checks["r10"]["actual"], 16) & ((1 << width) - 1)
        saved_checks.append({
            "name": "original r10",
            "kind": "register",
            "register": "r10",
            "equals": hex(value),
        })
    for addr, size in _write_spans(run):
        saved_checks.append({
            "name": f"write {addr:x}",
            "kind": "memory",
            "address": hex(addr),
            "size": size,
            "equals_hex": checks[f"mem-{addr:x}"]["actual"],
        })
    saved["checks"] = saved_checks
    return saved


def _print_summary(
    verified: int,
    converted: int,
    unconvertible: int,
    counts: Counter[str],
    examples: dict[str, str],
    passed: int,
    failed: int,
) -> None:
    not_runnable = sum(
        count for kind, count in counts.items()
        if kind.split()[0] not in FAIL_KINDS | {"verifier"}
    )
    print(f"functions {verified + converted + unconvertible}")
    print(f"oracle-verified {verified}")
    print(f"converted-unverified {converted}")
    print(f"unconvertible {unconvertible}")
    print(f"pass {passed}")
    print(f"fail {failed}")
    print(f"not-runnable {not_runnable}")
    print("failure classes:")
    for kind, count in counts.most_common(30):
        base = kind.split()[0]
        reason = REASONS.get(base, REASONS.get(kind, ""))
        example = examples.get(kind, "")
        extra = f" ({kind.split(' ', 1)[1]})" if base == "unmodeled" and " " in kind else ""
        print(f"  {count:5d}  {base}{extra}  {example}")
        if reason:
            print(f"         {reason}")

