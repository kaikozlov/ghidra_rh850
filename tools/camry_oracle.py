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
    _stmt_parts,
    load_matched,
    load_symbols,
    write_indirect_table,
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
MAX_BODY = 16384
STEP_LIMIT = 20000
SCRATCH = 0xFEBE0000
SCRATCH_SIZE = 4
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
    "large": "this run harnesses functions of at most 16384 bytes; larger bodies stay converted",
    "outside-codeflash": "the entry is outside the CodeFlash image the machine executes",
    "undecoded": "the lifter cannot walk every byte of the function, so the harness has no instruction list",
    "no-converted-body": "the converted C is not in src/all (a hand prototype or a dropped body), so the host check has nothing to call",
    "duplicate-body": "the same name is defined twice in src/all, so the host library cannot link it",
    "indirect-call": "an indirect jarl or jmp has no concrete callee, so the closure cannot be built",
    "callt": "callt depends on CTBP, which this harness does not initialize",
    "switch": "a computed switch target is not a fixed closure edge",
    "trap": "rie or fetrap leaves ordinary function return and has no host counterpart",
    "system-register": "ldsr, stsr, di, or ei is visible to the bytes, and the host library does not define those intrinsics",
    "uninitialized-register": "the machine read a system register this scenario does not initialize",
    "host-intrinsic": "the converted body calls a compiler intrinsic the host library does not define",
    "external-branch": "control leaves the decoded function without a direct call, so the closure is incomplete",
    "large-callee": "a direct callee is above 16384 bytes, so its closure is not inlined",
    "unmodeled": "the harness interpreter does not fold this operation and will not invent the address it computes",
    "mmio": "the access is outside codeflash, dataflash, RAM, and the peripheral file",
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
    "instruction-budget": "the closure did not return within 20000 instructions",
    "region-cap": "the host check has eight regions and codeflash plus dataflash already use two; accesses outside the merged local and global RAM banks do not fit",
    "no-observable": "the bytes do not write r10 or caller-visible memory, and the unchanged local-RAM scratch does not fit the host region cap",
    "uninitialized-read": "the machine read a byte the harness did not initialize",
    "simulator": "the P1M-E machine did not return a report for this scenario",
    "harness-drift": "the machine's result does not match the harness interpreter, so the scenario window is not trusted",
    "host-unmapped": "the converted C dereferenced an address the scenario did not map",
    "host-fault": "the converted C aborted in the host check",
    "host-link": "the converted closure calls a function that has no body and no prototype, so the host library cannot link it",
    "host-compile": "the converted body does not compile in the host check",
    "trace-cap": "the machine stopped recording memory accesses at 4096, so the write set is incomplete",
    "dropped-return": "a caller reads r10 after this call and the converted C is void",
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
    root_r10: bool = False
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
    windows: list[tuple[int, int]]


def _u32(value: int) -> int:
    return value & 0xFFFFFFFF


def _sext(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return _u32(value)


_MAPPED = (
    ("code", 0, 0x100000),
    ("code-ext", 0x01000000, 0x01008000),
    ("local", 0xFEBE0000, 0xFEC00000),
    ("alias", 0xFEDE0000, 0xFEE00000),
    ("global", 0xFEEF8000, 0xFEF08000),
    ("data", 0xFF200000, 0xFF208000),
)
_HOST_PTR = re.compile(r"camry_host_ptr\(\s*(0x[0-9A-Fa-f]+)")


def _space(addr: int, size: int) -> str:
    end = addr + size
    for name, start, stop in _MAPPED:
        if start <= addr and end <= stop:
            return name
    return "mmio"


def _covers_mapped(start: int, end: int) -> bool:
    for _name, left, right in _MAPPED:
        if start < right and left < end:
            return True
    return False


def _load_c_bodies(paths: list[Path]) -> tuple[dict[str, str], set[str]]:
    bodies: dict[str, str] = {}
    duplicates: set[str] = set()
    for path in paths:
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


def _load_bodies() -> tuple[dict[str, str], set[str]]:
    """src/all bodies, plus verified functions that live only in oracle.c.

    The differential link does not compile oracle.c. A converted caller still
    needs that verified text when its bytes enter the function.
    """
    bodies, duplicates = _load_c_bodies(sorted((ROOT / "src" / "all").glob("*.c")))
    oracle = ROOT / "src" / "oracle.c"
    if oracle.is_file():
        extra, extra_dups = _load_c_bodies([oracle])
        duplicates.update(name for name in extra_dups if name not in bodies)
        for name, chunk in extra.items():
            if name not in bodies:
                bodies[name] = chunk
    return bodies, duplicates


_HOST_INTRINSICS = ("__disable_irq", "__enable_irq", "__synchronize")


def _unmodeled_intrinsic(body: str) -> bool:
    for name in _HOST_INTRINSICS:
        body = body.replace(name, "")
    return "__" in body


def _static_block(fn) -> str | None:
    for inst in fn.insts:
        if inst.kind == "abort":
            return "trap"
        if inst.kind == "callt":
            return "callt"
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
        self.sr = [[0] * 32 for _ in range(8)]
        self.root = 0
        self.in_root = False

    def execute(self, fn, params: list[tuple[bool, int]], fill: int) -> Run:
        self.fill = fill
        self.run = Run()
        self.flags = [0, 0, 0, 0]
        self.ep_stack = False
        self.stack_regs = {3}
        self.regs = [SENTINEL] * 32
        # Same reset the P1M-E machine applies: PSW.ID set, every other
        # system register zero. stsr of PSW packs the live condition flags.
        self.sr = [[0] * 32 for _ in range(8)]
        self.sr[0][5] = 0x20
        self.regs[0] = 0
        self.regs[3] = ENTRY_SP
        self.regs[4] = GP
        self.regs[5] = TP
        self.regs[31] = STOP
        for index, (pointer, ordinal) in enumerate(params):
            self.regs[6 + index] = ARG_BASE + index * ARG_STRIDE if pointer else ordinal
        self.root = fn.entry
        self.in_root = False
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
            self.in_root = owner.entry == self.root
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
            if inst.text == "di":
                self.sr[0][5] |= 0x20
            elif inst.text == "ei":
                self.sr[0][5] &= ~0x20
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
        if kind == "jarl_ind":
            self._write_reg(inst.link, nxt)
            return self._transfer(self.regs[inst.reg])
        if kind == "switch":
            return self._switch(fn, nxt, inst.reg)
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

    def _switch(self, fn, nxt: int, reg: int) -> int:
        # Halfword displacement table immediately after the instruction.
        slot = _u32(nxt + (self.regs[reg] << 1))
        if slot + 2 > len(self.code):
            raise Harness("external-branch")
        disp = int.from_bytes(self.code[slot:slot + 2], "little", signed=True)
        target = _u32(nxt + (disp << 1))
        if target not in fn.sites:
            raise Harness("external-branch")
        return target

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
            if self.in_root:
                self.run.root_r10 = True
        self.stack_regs.discard(reg)
        if stack:
            self.stack_regs.add(reg)

    def _pack_psw(self) -> int:
        z, s, ov, cy = self.flags
        sat = (self.sr[0][5] >> 4) & 1
        return (self.sr[0][5] & ~0x1F) | z | (s << 1) | (ov << 2) | (cy << 3) | (sat << 4)

    def _write_psw(self, value: int) -> None:
        value = _u32(value)
        self.sr[0][5] = value
        self.flags = [value & 1, (value >> 1) & 1, (value >> 2) & 1, (value >> 3) & 1]

    def _op_ldsr(self, src: int, ident: int, sel: int) -> None:
        if not (0 <= sel < 8 and 0 <= ident < 32):
            return
        # ISPR writes are ignored unless INTCFG bit 0 is set.
        if sel == 2 and ident == 10 and (self.sr[2][13] & 1) == 0:
            return
        value = self.regs[src]
        if sel == 0 and ident == 5:
            self._write_psw(value)
            return
        self.sr[sel][ident] = value

    def _op_stsr(self, dst: int, ident: int, sel: int) -> None:
        if not (0 <= sel < 8 and 0 <= ident < 32):
            self._write_reg(dst, 0)
            return
        value = self._pack_psw() if sel == 0 and ident == 5 else self.sr[sel][ident]
        self._write_reg(dst, value)

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
        return space

    def _read_ram(self, addr: int, size: int, signed: bool, base: int) -> int:
        kind = self._kind_of(addr, size, base)
        image = self._image(addr, size)
        if image is None:
            if kind in {"code", "data", "code-ext"}:
                raise Harness("code-extension")
            if kind not in {"stack", "arg", "local", "global", "mmio"}:
                raise Harness("mmio")
            raw = 0
            for offset in range(size):
                raw |= self.run.memory.get(addr + offset, self.fill) << (8 * offset)
            self.run.reads.add((addr, size))
        else:
            raw = image
        if kind in {"local", "global", "stack", "arg", "mmio"}:
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
        if kind not in {"stack", "arg", "local", "global", "mmio"}:
            raise Harness("mmio")
        for offset in range(size):
            self.run.memory[addr + offset] = (value >> (8 * offset)) & 0xFF
        self.run.writes.add((addr, size))


def _params_of(signature: str, name: str) -> list[bool]:
    _return_type, params = parse_signature(signature, name)
    if len(params) > 4:
        raise Harness("stack-arguments")
    return ["*" in param for param in params]


_VOLATILE_REGS = (1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 30, 31)
_POINTER_MAP: dict[int, list[bool]] | None = None


def _param_source(origin: dict[int, int], reg: int) -> int | None:
    if reg in origin:
        value = origin[reg]
        if isinstance(value, int) and 6 <= value <= 9:
            return value - 6
        return None
    if 6 <= reg <= 9:
        return reg - 6
    return None


def _local_pointer_bases(fn, pointers: list[bool]) -> tuple[list[bool], list[tuple[int, list[int | None]]]]:
    """Pointer parameters this function uses, and the parameter each direct call passes."""
    pointed = list(pointers)
    origin: dict[int, int] = {}
    calls: list[tuple[int, list[int | None]]] = []
    memory = {"ld8s", "ld8u", "ld16s", "ld16u", "ld32", "st8", "st16", "st32"}
    for inst in fn.insts:
        if inst.kind in {"jarl", "jarl_ind"}:
            if inst.kind == "jarl" and inst.target:
                calls.append((inst.target, [_param_source(origin, reg) for reg in (6, 7, 8, 9)]))
            for reg in _VOLATILE_REGS:
                origin.pop(reg, None)
            continue
        parsed = _stmt_parts(inst.stmt) if inst.stmt else None
        if parsed is None:
            continue
        name, args = parsed
        if name == "mov" and len(args) >= 2 and isinstance(args[0], int):
            src = args[1]
            origin[args[0]] = origin.get(src, src) if isinstance(src, int) else -1
            continue
        if name == "addi_imm5" and args and isinstance(args[0], int):
            src = origin.get(args[0], args[0])
            if isinstance(src, int) and 6 <= src <= 9:
                origin[args[0]] = src
            else:
                origin.pop(args[0], None)
            continue
        if name in {"add", "addi", "movea"} and len(args) >= 2 and isinstance(args[0], int):
            src = origin.get(args[1], args[1]) if isinstance(args[1], int) else -1
            dst = origin.get(args[0], args[0])
            if isinstance(src, int) and 6 <= src <= 9:
                origin[args[0]] = src
            elif isinstance(dst, int) and 6 <= dst <= 9:
                origin[args[0]] = dst
            else:
                origin.pop(args[0], None)
            continue
        base = None
        if name in memory and len(args) >= 2 and isinstance(args[1], int):
            base = args[1]
        elif name in {"set1", "not1", "clr1", "tst1"} and args and isinstance(args[0], int):
            base = args[0]
        if base is not None:
            src = origin.get(base, base)
            if isinstance(src, int) and 6 <= src <= 9:
                index = src - 6
                if index < len(pointed):
                    pointed[index] = True
        if (
            args
            and isinstance(args[0], int)
            and name not in {"st8", "st16", "st32", "cmp", "cmpi", "mov", "add", "addi", "movea", "addi_imm5"}
        ):
            origin.pop(args[0], None)
    return pointed, calls


def _pointer_map() -> dict[int, list[bool]]:
    """Parameters that are pointers here or in a direct callee."""
    global _POINTER_MAP
    if _POINTER_MAP is not None:
        return _POINTER_MAP
    from tools.camry_lift import load_image, walk_symbol

    image = load_image()
    bodies, _duplicates = _load_bodies()
    functions = {}
    signatures: dict[int, list[bool]] = {}
    for row in load_symbols():
        fn = walk_symbol(image, row)
        if fn is None:
            continue
        functions[fn.entry] = fn
        body = bodies.get(row["name"])
        if body is None:
            signatures[fn.entry] = []
            continue
        try:
            signatures[fn.entry] = _params_of(_c_signature(body), row["name"])
        except (AssertionError, Harness, ValueError):
            signatures[fn.entry] = []
    local: dict[int, list[bool]] = {}
    calls: dict[int, list[tuple[int, list[int | None]]]] = {}
    for entry, fn in functions.items():
        seed = signatures.get(entry, [])
        pointed, sites = _local_pointer_bases(fn, seed)
        width = max(4, len(pointed))
        flags = [False] * width
        for index, flag in enumerate(pointed):
            flags[index] = flag
        local[entry] = flags
        calls[entry] = sites
    changed = True
    while changed:
        changed = False
        for entry, sites in calls.items():
            flags = local[entry]
            for target, args in sites:
                callee = local.get(target)
                if callee is None:
                    continue
                for index, source in enumerate(args):
                    if source is None or index >= len(callee) or source >= len(flags):
                        continue
                    if callee[index] and not flags[source]:
                        flags[source] = True
                        changed = True
    _POINTER_MAP = local
    return local


def _pointer_bases(fn, pointers: list[bool]) -> list[bool]:
    """An integer parameter the bytes use as an address still needs a mapped buffer."""
    pointed = list(pointers)
    extra = _pointer_map().get(fn.entry, [])
    for index, flag in enumerate(extra):
        if flag and index < len(pointed):
            pointed[index] = True
    return pointed


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


def _span(spans: list[tuple[int, int]]) -> tuple[int, int] | None:
    if not spans:
        return None
    start = min(addr for addr, _size in spans)
    end = max(addr + size for addr, size in spans)
    return start, end - start


def _cover_objects(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Map the whole named object when a field access uses its base pointer.

    ``slots[i].armed`` calls ``camry_host_ptr`` on the object base, while the
    bytes only touch the field. The base is otherwise outside the write window.
    """
    from tools.camry_decomp import _GP_DELTA, _gp_objects

    covered = list(spans)
    for addr, size in spans:
        end = addr + size
        for _name, base, obj_size, _expr in _gp_objects():
            runtime = (base - _GP_DELTA) & 0xFFFFFFFF
            if addr < runtime + obj_size and runtime < end:
                covered.append((runtime, obj_size))
    return covered


def _windows(
    runs: list[Run],
    pointers: list[bool] | None = None,
    cover: list[int] | None = None,
) -> list[tuple[int, int]]:
    """One window per RAM bank. Separate clusters overflow the host's eight regions."""
    local: list[tuple[int, int]] = []
    glob: list[tuple[int, int]] = []
    other: list[tuple[int, int]] = []
    stack = False
    arg = False
    for run in runs:
        for addr, size in run.reads | run.writes:
            if STACK_LO <= addr and addr + size <= STACK_HI:
                stack = True
            elif ARG_BASE <= addr and addr + size <= ARG_BASE + ARG_COUNT * ARG_STRIDE:
                arg = True
            elif _space(addr, size) == "local":
                local.append((addr, size))
            elif _space(addr, size) == "global":
                glob.append((addr, size))
            else:
                other.append((addr, size))
    for addr in cover or []:
        if _space(addr, 1) == "local":
            local.append((addr, 1))
        elif _space(addr, 1) == "global":
            glob.append((addr, 1))
        else:
            other.append((addr, 1))
    if stack:
        local.append((STACK_LO, STACK_HI - STACK_LO))
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
        local.append((ARG_BASE, slot * ARG_STRIDE))
    local = _cover_objects(local)
    glob = _cover_objects(glob)
    other = _cover_objects(other)
    windows = [window for window in (_span(local), _span(glob)) if window is not None]
    packed = _clusters(other, 0x400)
    if len(windows) + len(packed) > 6 and packed:
        start = min(addr for addr, _size in other)
        end = max(addr + size for addr, size in other)
        if end - start <= 0x10000 and not _covers_mapped(start, end):
            packed = [(start, end - start)]
    if len(windows) + len(packed) > 6:
        raise Harness("region-cap")
    windows.extend(packed)
    return windows


def _cover(windows: list[tuple[int, int]], addr: int, size: int) -> str:
    end = addr + size
    for base, span in windows:
        if base <= addr and end <= base + span:
            return "full"
        if not (end <= base or addr >= base + span):
            return "partial"
    return "none"


def _attach_scratch(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
    cover = _cover(windows, SCRATCH, SCRATCH_SIZE)
    if cover == "full":
        return windows
    if cover == "partial" or len(windows) >= 6:
        raise Harness("no-observable")
    return [*windows, (SCRATCH, SCRATCH_SIZE)]


def _note_mmio_bases(runs: list[Run], texts: list[str]) -> None:
    """The bytes may touch a field while the C takes the object's base pointer."""
    for text in texts:
        for match in _HOST_PTR.finditer(text):
            addr = int(match.group(1), 16)
            if _space(addr, 1) != "mmio":
                continue
            for run in runs:
                run.reads.add((addr, 1))


def _scenario_windows(
    runs: list[Run],
    pointers: list[bool],
    cover: list[int] | None = None,
) -> list[tuple[int, int]]:
    windows = _windows(runs, pointers, cover)
    if any(_observable(run) for run in runs):
        return windows
    return _attach_scratch(windows)


def _region_fill(scenario: dict, address: int) -> int | None:
    for region in scenario.get("memory", []):
        base = int(region["address"], 16)
        if base <= address < base + int(region["size"]):
            return int(region["fill"]) & 0xFF
    return None


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
    spans = _write_spans(run)
    for addr, size in spans:
        checks.append({
            "name": f"mem-{addr:x}",
            "kind": "memory",
            "address": hex(addr),
            "size": size,
            "equals_hex": "00" * size,
        })
    if not spans and _cover(windows, SCRATCH, SCRATCH_SIZE) == "full":
        checks.append({
            "name": f"mem-{SCRATCH:x}",
            "kind": "memory",
            "address": hex(SCRATCH),
            "size": SCRATCH_SIZE,
            "equals_hex": "00" * SCRATCH_SIZE,
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
        "peripheral_file": True,
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


def _object_definitions() -> list[tuple[str, str]]:
    """Definitions for extern objects declared in common.h."""
    cached = getattr(_object_definitions, "cached", None)
    if cached is not None:
        return cached
    header = ROOT / "src" / "all" / "common.h"
    found: list[tuple[str, str]] = []
    if header.exists():
        pattern = re.compile(
            r"extern\s+((?:volatile\s+)?(?:u?int(?:8|16|32|64)_t|unsigned|int)\s+\*?\s*)"
            r"([A-Za-z_][A-Za-z0-9_]*)\s*;\s*$"
        )
        for line in header.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line.strip())
            if match:
                found.append((match.group(2), f"{match.group(1)}{match.group(2)};"))
    _object_definitions.cached = found
    return found


def _diagnostic(log: str) -> str:
    for line in log.splitlines():
        text = line.strip()
        if (
            "error:" in text
            or "duplicate symbol" in text
            or "Undefined symbols" in text
            or "undefined reference" in text
        ):
            return text[:220]
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    return (lines[0][:220] if lines else "unknown")


def _compile(
    directory: Path,
    names: list[str],
    bodies: dict[str, str],
    stubs: dict[str, str] | None = None,
    provided: set[str] | None = None,
) -> tuple[ctypes.CDLL | None, str]:
    source = directory / "candidates.c"
    stub_path = directory / "stubs.c"
    library = directory / "liboracle.dylib"
    defined = _src_definitions() | (provided or set())
    parts = ['#include "common.h"', ""]
    emitted = set()
    for name in names:
        if name in defined or name in emitted or name not in bodies:
            continue
        emitted.add(name)
        parts.append(bodies[name])
    source.write_text("\n".join(parts) + "\n", encoding="utf-8")
    stub_text = ['#include <stdlib.h>', '#include "common.h"', ""]
    for name, signature in sorted((stubs or {}).items()):
        if name in defined or name in emitted:
            continue
        stub_text.append(signature.rstrip())
        stub_text.append("{")
        stub_text.append("  abort();")
        stub_text.append("}")
        stub_text.append("")
    for _name, decl in _object_definitions():
        stub_text.append(decl)
    stub_path.write_text("\n".join(stub_text) + "\n", encoding="utf-8")
    table = directory / "indirect_table.c"
    linked = [source, *(_src_paths())]
    write_indirect_table(table, linked)
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
            str(source), str(stub_path), str(table), str(HOST_MEM),
            *[str(path) for path in _src_paths()],
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


def _body_closure(roots: list[str], bodies: dict[str, str]) -> list[str]:
    """Functions the host must link, including calls the scenario did not take."""
    needed: list[str] = []
    seen: set[str] = set()
    pending = list(roots)
    while pending:
        name = pending.pop()
        if name in seen or name not in bodies:
            continue
        seen.add(name)
        needed.append(name)
        pending.extend(callee for callee in _c_calls(bodies[name]) if callee not in seen)
    return needed


def _defined_lines(text: str) -> set[str]:
    """Names of function definitions, including signatures wrapped before '('."""
    names = set()
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        raw = lines[index]
        index += 1
        if not raw or raw[0] in " \t#/*}" or raw.startswith("static"):
            continue
        buf = raw.strip()
        while index < len(lines) and "{" not in buf and ";" not in buf:
            nxt = lines[index]
            if not nxt.strip() or nxt.startswith(("/*", " *", " */", "//")):
                index += 1
                continue
            # A return type can sit on its own line. After '(' only an indented
            # continuation or the opening brace still belongs to this signature.
            if "(" in buf and nxt[0] not in " \t{":
                break
            buf += " " + nxt.strip()
            index += 1
            if len(buf) > 1500:
                break
        head = buf.split("{", 1)[0]
        if "{" not in buf or ";" in head:
            continue
        # The declarator is the identifier immediately before '('. A pointer
        # return such as `void *name(` has no space for a type-then-name match.
        paren = head.find("(")
        if paren < 0:
            continue
        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", head[:paren])
        if match and match.group(1) not in _CALL_WORDS:
            names.add(match.group(1))
    return names


def _src_paths() -> list[Path]:
    return sorted(path for path in (ROOT / "src").glob("*.c") if path.name != "oracle.c")


def _src_definitions() -> set[str]:
    cached = getattr(_src_definitions, "cached", None)
    if cached is not None:
        return cached
    names: set[str] = set()
    for path in _src_paths():
        names.update(_defined_lines(path.read_text(encoding="utf-8")))
    _src_definitions.cached = names
    return names


def _prototypes() -> dict[str, str]:
    """Declarator text from common.h, without the trailing semicolon."""
    header = ROOT / "src" / "all" / "common.h"
    if not header.exists():
        return {}
    found: dict[str, str] = {}
    buf = ""
    for line in header.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not buf and (
            not stripped
            or stripped.startswith(("#", "//", "/*", "*"))
            or stripped.startswith(("typedef", "struct", "enum", "union"))
        ):
            continue
        buf = f"{buf} {stripped}".strip()
        if not buf.endswith(";"):
            if len(buf) > 800:
                buf = ""
            continue
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*;$", buf)
        if match:
            found[match.group(1)] = buf[:-1].rstrip()
        buf = ""
    return found


def _undefined_symbols(log: str) -> list[str]:
    missing = re.findall(r'"_([^"]+)", referenced from:', log)
    if not missing:
        missing = re.findall(r"undefined reference to [`']_?([^']+)'", log)
    seen: list[str] = []
    for name in missing:
        if name not in seen:
            seen.append(name)
    return seen


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
        for callee in _c_calls(body) | (
            set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", body)) & bodies.keys()
        ):
            if callee in seen or callee not in bodies:
                continue
            seen.add(callee)
            support.append(callee)
            pending.append(callee)
    return kept, support


def _error_names(
    log: str,
    names: list[str],
    bodies: dict[str, str],
    skip: set[str] | None = None,
) -> list[str]:
    lines = [int(number) for number in re.findall(r"candidates\.c:(\d+):", log)]
    if not lines:
        return []
    defined = _src_definitions() | (skip or set())
    cursor = 3
    spans = []
    emitted: set[str] = set()
    for name in names:
        if name in defined or name in emitted or name not in bodies:
            continue
        emitted.add(name)
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
                raise Harness("return-mismatch", f"host {returned:#x} bytes {expected:#x}")
        elif check.get("kind") == "memory":
            address = int(check["address"], 16)
            size = int(check["size"])
            actual = read_regions(images, address, size).hex()
            if actual != check["equals_hex"]:
                raise Harness(
                    "memory-mismatch",
                    f"{address:#x} host {actual} bytes {check['equals_hex']}",
                )
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
            raise Harness("memory-mismatch", f"{address:#x} extra {new:02x} was {old:02x}")


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
            os.write(write_fd, f"{exc.kind} {exc.detail}".encode()[:400])
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
            if kind in {"memory-mismatch", "return-mismatch"}:
                print(f"disagree {kind} {planned.name} {detail[:180]}", flush=True)
            return kind
    if "unmapped" in detail or "outside" in detail:
        return "host-unmapped"
    return "host-fault"


def _reachable_stubs(
    planned: list[tuple[Planned, list[dict]]],
    support: list[str],
    bodies: dict[str, str],
    stubs: dict[str, str],
) -> list[str]:
    wanted: list[str] = []
    seen: set[str] = set()
    pending = list(support) + [item.name for item, _rows in planned]
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        referenced = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", bodies.get(name, "")))
        referenced.update(_c_calls(bodies.get(name, "")))
        for callee in referenced:
            if callee in stubs and callee not in wanted:
                wanted.append(callee)
            elif callee in bodies:
                pending.append(callee)
    return wanted


def _refresh_text(existing: str, bodies: dict[str, str]) -> str:
    """Replace converted support copies with the current src/all body.

    Equivalent functions keep the text their oracles passed with. A converted
    callee that was copied into oracle.c earlier still has Ghidra's gp, so the
    verifier would fault on an address the scenario never mapped.
    """
    blocked: set[str] = set()
    allowed: set[str] = set()
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    for name, statuses in by_name.items():
        if statuses & {"equivalent", "byte-matched"}:
            blocked.add(name)
        elif "converted" in statuses:
            allowed.add(name)
    lines = existing.splitlines()
    out: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if (
            not line.strip()
            or line.startswith("#")
            or line.startswith((" ", "\t", "/*", "//"))
        ):
            out.append(line)
            index += 1
            continue
        start = index
        while index < len(lines) and "{" not in lines[index]:
            index += 1
        if index >= len(lines):
            out.extend(lines[start:])
            break
        depth = 0
        while index < len(lines):
            depth += lines[index].count("{") - lines[index].count("}")
            index += 1
            if depth <= 0:
                break
        chunk = "\n".join(lines[start:index])
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _c_signature(chunk))
        name = match.group(1) if match else ""
        fresh = bodies.get(name)
        if (
            name in allowed
            and name not in blocked
            and fresh is not None
            and fresh.strip() != chunk.strip()
        ):
            chunk = fresh.strip()
        out.extend(chunk.split("\n"))
    return "\n".join(out).rstrip() + "\n"


def _promote(
    planned: list[tuple[Planned, list[dict]]],
    support: list[str],
    bodies: dict[str, str],
    stubs: dict[str, str] | None = None,
) -> None:
    oracle_path = ROOT / "src" / "oracle.c"
    existing = oracle_path.read_text(encoding="utf-8") if oracle_path.exists() else '#include "common.h"\n'
    existing = _refresh_text(existing, bodies)
    # src/*.c is already linked by the verifier. Emitting those names again
    # fails the link with a duplicate symbol and drops the whole batch.
    have = _defined_lines(existing) | _src_definitions()
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
        have.add(item.name)
    for name in _reachable_stubs(planned, support, bodies, stubs or {}):
        if name in have:
            continue
        signature = stubs[name]
        parts.append(signature.rstrip())
        parts.append("{")
        parts.append("  __builtin_trap();")
        parts.append("}")
        parts.append("")
        have.add(name)
    text = "\n".join(parts)
    for name, decl in _object_definitions():
        if name in have or re.search(rf"^{re.escape(decl)}$", text, re.M):
            continue
        if re.search(rf"\b{re.escape(name)}\b", text):
            parts.append(decl)
            parts.append("")
            have.add(name)
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
    log_path = REPO_ROOT / "build" / "tmp" / "camry-oracle-verify.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text((result.stderr or "") + "\n" + (result.stdout or ""), encoding="utf-8")
    if result.returncode == 0:
        return None
    blob = (result.stderr or "") + "\n" + (result.stdout or "")
    missing = _undefined_symbols(blob)
    err = [line for line in (result.stderr or "").splitlines() if line.strip()]
    fails = [line for line in (result.stdout or "").splitlines() if line.startswith("FAIL ")]
    shown = (err[-4:] + fails) or (result.stdout or "").strip().splitlines()[-6:]
    text = " | ".join(shown)
    if missing:
        text = "undefined:" + ",".join(missing) + "\n" + text
    return text


def _keep_verified(
    passed: list[tuple[Planned, list[dict]]],
    snapshots: dict[Path, str | None],
    bodies: dict[str, str],
    defined: set[str],
    symbols: set[str],
    macros: set[str],
    reject,
    examples: dict[str, str],
    stubs: dict[str, str] | None = None,
    forced: tuple[str, ...] = (),
) -> list[tuple[Planned, list[dict]]]:
    if not passed:
        return []
    kept, support = _linkable(
        [item.name for item, _rows in passed], bodies, defined, symbols, macros,
    )
    support = list(dict.fromkeys((*forced, *support)))
    runnable = [(item, rows) for item, rows in passed if item.name in kept]
    for item, _rows in passed:
        if item.name not in kept:
            reject("host-link", item.name, address=item.address)
    if not runnable:
        return []
    _restore(snapshots)
    _promote(runnable, support, bodies, stubs)
    error = _verify()
    if error is None:
        return runnable
    _restore(snapshots)
    if error.startswith("undefined:"):
        header, _, detail = error.partition("\n")
        missing = [name for name in header.split(":", 1)[1].split(",") if name]
        prototypes = _prototypes()
        have = set(forced) | set(support) | defined
        extra = list(forced)
        stub_map = dict(stubs or {})
        grew = False
        for name in missing:
            if name in have or name in stub_map:
                continue
            if name in bodies:
                extra.append(name)
                have.add(name)
                grew = True
            elif name in prototypes:
                stub_map[name] = prototypes[name]
                grew = True
        if grew:
            return _keep_verified(
                runnable, snapshots, bodies, defined, symbols, macros, reject, examples,
                stub_map, tuple(extra),
            )
        error = detail or error
    dupes = set(re.findall(
        r"(?:redefinition of '|duplicate symbol '_)([A-Za-z_][A-Za-z0-9_]*)",
        error,
    ))
    if dupes:
        def reaches(name: str, seen: set[str] | None = None) -> bool:
            if name in dupes:
                return True
            if name not in bodies:
                return False
            seen = set() if seen is None else seen
            if name in seen:
                return False
            seen.add(name)
            return any(reaches(callee, seen) for callee in _c_calls(bodies[name]))

        bad = [item for item, _rows in runnable if reaches(item.name)]
        if bad and len(bad) < len(runnable):
            for item in bad:
                reject("verifier", item.name, address=item.address)
            examples["verifier"] = error[:180]
            rest = [(item, rows) for item, rows in runnable if item not in bad]
            return _keep_verified(
                rest, snapshots, bodies, defined, symbols, macros, reject, examples, stubs, forced,
            )
    named = [item for item, _rows in runnable if item.name in error]
    if named and len(named) < len(runnable):
        for item in named:
            reject("verifier", item.name, address=item.address)
        examples["verifier"] = error[:180]
        rest = [(item, rows) for item, rows in runnable if item not in named]
        return _keep_verified(
            rest, snapshots, bodies, defined, symbols, macros, reject, examples, stubs, forced,
        )
    if len(runnable) == 1 or "FAIL " not in error:
        for item, _rows in runnable:
            reject("verifier", item.name, address=item.address)
        examples["verifier"] = error[:180]
        return []
    mid = len(runnable) // 2
    left = _keep_verified(
        runnable[:mid], snapshots, bodies, defined, symbols, macros, reject, examples, stubs, forced,
    )
    right = _keep_verified(
        runnable[mid:], snapshots, bodies, defined, symbols, macros, reject, examples, stubs, forced,
    )
    return left + right


def run_oracles() -> int:
    metadata = resolve_target(TARGET)[1]
    code = load_image()
    data_base = int(metadata["dataflash_base"], 16)
    data = (REPO_ROOT / metadata["dataflash"]).read_bytes()
    symbols = load_symbols()
    status = {int(row["addr"], 16): row for row in load_matched()}
    bodies, duplicates = _load_bodies()
    linked = _src_definitions()
    functions = {}
    for row in symbols:
        fn = walk_symbol(code, row)
        if fn is not None:
            functions[fn.entry] = fn
    global _CONSUMED_RETURNS
    _CONSUMED_RETURNS = _returns_read_by_callers(functions)
    machine = _Machine(code, data, data_base, functions)
    counts: Counter[str] = Counter()
    examples: dict[str, str] = {}
    planned: list[Planned] = []
    hand = _prototype_names()
    seen: set[object] = set()
    focus = {"addr": None}

    def reject(kind: str, name: str, detail: str = "", address: int | None = None) -> None:
        key = address if address is not None else focus["addr"]
        if key is None:
            key = name
        if key in seen:
            return
        seen.add(key)
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
        focus["addr"] = address
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
        if _unmodeled_intrinsic(body):
            reject("host-intrinsic", name)
            continue
        fn = functions.get(address)
        if fn is None:
            reject("undecoded", name)
            continue
        try:
            signature = _c_signature(body)
            pointers = _pointer_bases(fn, _params_of(signature, name))
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
        texts = [body]
        for target in set().union(*(run.calls for run in runs)):
            callee = functions.get(target)
            if callee is not None and callee.name in bodies:
                texts.append(bodies[callee.name])
        _note_mmio_bases(runs, texts)
        # The bytes address gp+disp. The C holds camry_host_ptr(gp) and indexes it.
        cover = (
            [GP]
            if any("camry_host_ptr(0xfebeb800u)" in text for text in texts)
            else None
        )
        try:
            windows = _scenario_windows(runs, pointers, cover)
        except Harness as exc:
            reject(exc.kind, name, exc.detail)
            continue
        calls = set().union(*(run.calls for run in runs))
        if any(
            functions[target].name not in bodies and functions[target].name not in linked
            for target in calls
            if target in functions
        ):
            reject("no-converted-body", name)
            continue
        planned.append(Planned(address, name, signature, body, runs, calls, windows))

    focus["addr"] = None
    print(f"harnessed {len(planned)}", flush=True)
    # A function-pointer target is not a textual call. Link every converted
    # body so camry_indirect can reach it. Names already defined in src/*.c
    # are skipped by the compiler.
    needed = list(bodies)
    # Keep only roots whose whole executed closure is in the compiled set.
    dropped: set[str] = set()
    stubs: dict[str, str] = {}
    prototypes = _prototypes()
    provided: set[str] = set()
    failed_states: set[tuple[frozenset[str], frozenset[str], frozenset[str]]] = set()
    with tempfile.TemporaryDirectory(prefix="camry-oracle-") as directory:
        directory_path = Path(directory)
        def state_of(names: list[str]) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
            return (frozenset(names), frozenset(stubs), frozenset(provided))

        def fit(names: list[str]) -> tuple[ctypes.CDLL | None, list[str]]:
            names = list(dict.fromkeys(name for name in names if name not in dropped))
            if not names:
                return None, []
            state = state_of(names)
            if state in failed_states:
                for name in names:
                    dropped.add(name)
                    reject("host-compile", name)
                return None, []
            compiled, log = _compile(directory_path, names, bodies, stubs, provided)
            if compiled is not None:
                return compiled, names
            failed_states.add(state)
            missing = _undefined_symbols(log)
            defined_now = _src_definitions() | provided
            extra = [
                name for name in missing
                if name in bodies and name not in defined_now
                and name not in dropped and name not in names
            ]
            if extra:
                grown = list(dict.fromkeys(names + extra))
                if state_of(grown) not in failed_states:
                    return fit(grown)
                # The real bodies recreate a set that already failed. Stub the
                # callees so this slice can link, and keep going.
                for name in extra:
                    if name in prototypes and name not in stubs:
                        stubs[name] = prototypes[name]
                        dropped.add(name)
                        reject("host-link", name)
                if any(name in stubs for name in extra):
                    return fit(names)
            fresh = {
                name: prototypes[name]
                for name in missing
                if name not in bodies and name not in defined_now
                and name not in stubs and name in prototypes
            }
            if fresh:
                stubs.update(fresh)
                return fit(names)
            dupes: list[str] = []
            for name in re.findall(
                r"(?:duplicate symbol '_|redefinition of ')([A-Za-z_][A-Za-z0-9_]*)",
                log,
            ):
                if name not in dupes:
                    dupes.append(name)
            if dupes:
                acted = False
                for name in dupes:
                    if name in stubs:
                        del stubs[name]
                        acted = True
                    if name not in provided:
                        provided.add(name)
                        acted = True
                if acted:
                    return fit(names)
            linked = _drop_unlinked(names, bodies, log)
            if linked:
                for name in linked:
                    dropped.add(name)
                    reject("host-link", name)
                return fit(names)
            bad = _error_names(log, names, bodies, provided)
            if bad:
                for name in bad:
                    dropped.add(name)
                    reject("host-compile", name)
                return fit(names)
            if len(names) == 1:
                print(_diagnostic(log), flush=True)
                dropped.add(names[0])
                reject("host-compile", names[0])
                return None, []
            mid = len(names) // 2
            print(f"compile split {len(names)} {_diagnostic(log)}", flush=True)
            left_lib, left = fit(names[:mid])
            right_lib, right = fit(names[mid:])
            del left_lib, right_lib
            union = list(dict.fromkeys(left + right))
            remaining = [name for name in names if name not in dropped]
            if len(union) == len(remaining) or state_of(union) in failed_states:
                prefer, discard = (left, right) if len(left) >= len(right) else (right, left)
                for name in discard:
                    if name not in prefer and name not in dropped:
                        dropped.add(name)
                        reject("host-compile", name)
                if not prefer:
                    return None, []
                return fit(prefer)
            return fit(union)

        library, _kept = fit([name for name in needed if name not in dropped])
        if library is None:
            for item in planned:
                reject("host-compile", item.name, address=item.address)
            _print_summary(verified, converted, unconvertible, counts, examples, 0, 0)
            return 0
        runnable = []
        for item in planned:
            closure = {functions[address].name for address in item.calls if address in functions}
            closure.add(item.name)
            if closure & dropped:
                if item.name not in dropped:
                    reject("host-link", item.name, address=item.address)
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
            windows = item.windows
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
                    if kind == "dropped-return":
                        print(f"disagree dropped-return {item.name} {item.address:#x}", flush=True)
                    reject(kind, item.name, address=item.address)
                    if kind in FAIL_KINDS:
                        fail += 1
                    ok = False
                    break
            if ok and saved:
                passed.append((item, saved))
            elif ok:
                reject("no-observable", item.name, address=item.address)
        del library

    if not passed:
        _print_summary(verified, converted, unconvertible, counts, examples, 0, fail)
        return 0

    snapshots = {
        path: path.read_text(encoding="utf-8") if path.exists() else None
        for path in (ROOT / "matched.jsonl", ROOT / "oracles.jsonl", ROOT / "src" / "oracle.c")
    }
    defined = _src_definitions() | set(stubs)
    symbols_names = {row["name"] for row in symbols}
    macros = _macro_names()
    final = _keep_verified(
        passed, snapshots, bodies, defined, symbols_names, macros, reject, examples, stubs,
    )
    _restore(snapshots)
    if not final:
        _print_summary(verified, converted, unconvertible, counts, examples, 0, fail)
        return 0
    kept, support = _linkable(
        [item.name for item, _rows in final], bodies, defined, symbols_names, macros,
    )
    for item, _rows in final:
        if item.name not in kept:
            reject("host-link", item.name, address=item.address)
    final = [(item, rows) for item, rows in final if item.name in kept]
    _promote(final, support, bodies, stubs)
    verifier = _verify()
    if verifier is not None:
        _restore(snapshots)
        for item, _rows in final:
            reject("verifier", item.name, address=item.address)
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


_R10_DEST = {
    "mov", "movi", "movea", "movhi", "add", "sub", "subr", "or", "xor", "and", "not",
    "addi", "addi_imm5", "ld8s", "ld8u", "ld16s", "ld16u", "ld32",
    "mul", "mulh", "mulhi", "muli", "mului", "div3", "divh2",
    "shl_imm", "shr", "sar", "shr_reg", "sar_reg", "shl_reg",
    "satadd", "satsub", "satsubr", "sataddi", "satsubi", "satadd3", "satsub3",
    "cmov", "adf", "sbf",
}
_R10_UPDATE = {"addi_imm5", "sxh", "zxh", "sxb", "zxb", "shr", "sar", "shl_imm"}
_CONSUMED_RETURNS: set[int] = set()


# The last operand is an immediate, not a register. A displacement of 10 is not r10.
_IMM_TAIL = {
    "ld8s", "ld8u", "ld16s", "ld16u", "ld32",
    "st8", "st16", "st32",
    "addi", "cmpi", "movi", "movea", "movhi",
    "mulhi", "muli", "mului", "addi_imm5", "shl_imm", "shr", "sar",
    "sataddi", "satsubi",
}


def _reg_args(op: str, args: list) -> list:
    if op in _IMM_TAIL and args:
        return list(args[:-1])
    return list(args)


def _r10_effects(inst: Inst) -> tuple[bool, bool]:
    """Whether this instruction reads r10 and whether it writes r10."""
    if inst.kind in {"jarl", "jarl_ind"} and inst.link == 10:
        return False, True
    parsed = _stmt_parts(inst.stmt) if inst.stmt else None
    if parsed is None:
        return False, False
    op, args = parsed
    regs = [arg for arg in _reg_args(op, args) if arg is not None]
    if op in {"cmp", "cmpi", "tst"}:
        return 10 in regs, False
    if op in {"st8", "st16", "st32", "set1", "not1", "clr1", "tst1"}:
        return bool(regs) and regs[0] == 10, False
    if op in _R10_UPDATE and regs and regs[0] == 10:
        return True, True
    if op in _R10_DEST and regs and regs[0] == 10:
        return 10 in regs[1:], True
    if op in _R10_DEST:
        return 10 in regs[1:], False
    return False, False


def _returns_read_by_callers(functions: dict[int, object]) -> set[int]:
    """Entries whose r10 a direct caller reads before replacing it."""
    consumed: set[int] = set()
    for fn in functions.values():
        insts = fn.insts
        for index, inst in enumerate(insts):
            if inst.kind != "jarl":
                continue
            for nxt in insts[index + 1:index + 21]:
                reads, writes = _r10_effects(nxt)
                if reads:
                    consumed.add(inst.target)
                    break
                if writes or nxt.kind in {"jarl", "jarl_ind", "jmp", "dispose"}:
                    break
    return consumed


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
    scratch_name = f"mem-{SCRATCH:x}"
    if not _write_spans(run) and scratch_name in checks:
        actual = checks[scratch_name].get("actual")
        fill = _region_fill(scenario, SCRATCH)
        if fill is None or not actual or actual == "unavailable" or actual != f"{fill:02x}" * SCRATCH_SIZE:
            return "harness-drift"
    return_type, _params = parse_signature(item.signature, item.name)
    bytes_return = sim_r10 != SENTINEL
    if not bytes_return and return_type != "void":
        return "invented-return"
    if (
        bytes_return
        and return_type == "void"
        and run.root_r10
        and item.address in _CONSUMED_RETURNS
    ):
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
    scratch = checks.get(f"mem-{SCRATCH:x}", {}).get("actual")
    if not _write_spans(run) and scratch and scratch != "unavailable":
        saved_checks.append({
            "name": f"write {SCRATCH:x}",
            "kind": "memory",
            "address": hex(SCRATCH),
            "size": SCRATCH_SIZE,
            "equals_hex": scratch,
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

