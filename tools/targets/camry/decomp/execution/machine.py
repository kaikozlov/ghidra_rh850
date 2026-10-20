"""Bounded RH850 oracle interpreter and native RAM harness."""
from __future__ import annotations

from collections.abc import Callable
from tools.targets.camry.decomp.lifting.decode import Inst
from collections.abc import Iterable
from collections.abc import Mapping
from tools.targets.camry.decomp.tree import SYSTEM_REGISTERS
from tools.targets.camry.decomp.abi import _BOOT_RELOCATED_COPIES
from tools.targets.camry.decomp.syntax import _stmt_parts
from tools.targets.camry.decomp.lifting.decode import decode_at
from collections import defaultdict
import re
from tools.targets.camry.decomp.execution.model import (
    ARG_BASE,
    ARG_COUNT,
    ARG_STRIDE,
    ENTRY_SP,
    GP,
    Harness,
    ICCTRL_BUSY_READS,
    MAX_BODY,
    PERIPHERAL_POLL_READS,
    Run,
    SENTINEL,
    SPIN_DONE,
    STACK_HI,
    STACK_LO,
    STEP_LIMIT,
    STOP,
    TP,
    _sext,
    _space,
    _u32,
)


def _static_block(fn) -> str | None:
    for inst in fn.insts:
        if inst.kind == "abort":
            return "trap"
        if inst.kind == "callt":
            return "callt"
    return None


def _direct_target(inst: Inst) -> int | None:
    if inst.kind in {"br", "jr"}:
        return inst.target
    if inst.kind == "b" and inst.cc == 5:
        return inst.target
    return None


def _can_return(fn) -> bool:
    """Whether any instruction can transfer back to the caller."""
    sites = {inst.addr: inst for inst in fn.insts}
    edges: dict[int, list[int | str]] = {}
    for inst in fn.insts:
        nxt = inst.addr + inst.size
        out: list[int | str] = []
        if inst.kind == "br":
            out.append(inst.target)
        elif inst.kind in {"b", "loop"}:
            out.append(inst.target)
            out.append(nxt)
        elif inst.kind == "jmp" and inst.reg == 31:
            out.append("ret")
        elif inst.kind == "eiret":
            out.append("ret")
        elif inst.kind == "jr":
            out.append(inst.target)
        elif inst.kind == "dispose":
            out.append("ret" if inst.ret else nxt)
        elif inst.kind == "jarl":
            out.append(nxt)
        elif inst.kind in {"abort", "callt", "jarl_ind", "jmp", "jmpdisp", "switch"}:
            pass
        else:
            out.append(nxt)
        edges[inst.addr] = out
    seen: set[int] = set()
    pending = [fn.entry]
    while pending:
        pc = pending.pop()
        if pc in seen:
            continue
        seen.add(pc)
        for dest in edges.get(pc, []):
            if dest == "ret":
                return True
            if isinstance(dest, int) and dest in sites and dest not in seen:
                pending.append(dest)
    return False


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
        self.boot_copies = {
            entry: (source, size)
            for name, (source, entry, size) in _BOOT_RELOCATED_COPIES.items()
            if entry in functions and functions[entry].name == name
        }
        # The boot's immutable TP table points at its copied RAM image. A
        # standalone caller has that same exact image as an entry precondition.
        self.boot_copy_users = set(self.boot_copies)
        callers: dict[int, set[int]] = defaultdict(set)
        for fn in functions.values():
            for index, inst in enumerate(fn.insts):
                if inst.kind in {"jarl", "jr", "br"} and inst.target not in fn.sites:
                    callers[inst.target].add(fn.entry)
                parts = _stmt_parts(inst.stmt)
                if parts is None or parts[0] != "ld32" or fn.entry >= 0x20000:
                    continue
                reg, base, disp = parts[1]
                if base != 5 or disp is None or index + 1 == len(fn.insts):
                    continue
                call = fn.insts[index + 1]
                slot = (0x869C + disp) & 0xffffffff
                if (call.kind == "jarl_ind" and call.reg == reg and slot + 4 <= len(code)
                        and int.from_bytes(code[slot:slot + 4], "little") in self.boot_copies):
                    self.boot_copy_users.add(fn.entry)
        pending = list(self.boot_copy_users)
        while pending:
            for caller in callers[pending.pop()] - self.boot_copy_users:
                self.boot_copy_users.add(caller)
                pending.append(caller)
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
        self.sr = [[0] * 32 for _ in range(14)]
        self.root = 0
        self.in_root = False
        self._peripheral_polls: dict[int, int] = {}
        self._switch_base: int | None = None
        self._switch_lo = 0
        self.bounded_entries: set[int] = set()
        self._bounded_frames: dict[int, list[tuple[int, list[int]]]] = {}
        self._icctrl_busy = 0
        self._root_sites: set[int] = set()
        self._root_returns = True
        self.bound_this = False
        self._returned_from_exception = False
        self.stack_lo = STACK_LO
        self.stack_hi = STACK_HI
        self.entry_sp = ENTRY_SP
        self.arg_base = ARG_BASE
        self.arg_slots = ARG_COUNT
        self.relocated = False
        self.allow_unaligned = True
        self.fill_regs: set[int] = set()
        self.fill_addr: dict[int, int] = {}

    def execute(self, fn, params: list[tuple[bool, int]], fill: int, bound: bool = False) -> Run:
        pinned: tuple[int, ...] = ()
        while True:
            run = self._execute_run(fn, params, fill, bound, pinned)
            slots = tuple(dict.fromkeys(run.stub_slots))
            if slots == pinned:
                return run
            pinned = slots

    def _execute_run(
        self, fn, params: list[tuple[bool, int]], fill: int, bound: bool,
        stub_slots: tuple[int, ...],
    ) -> Run:
        self.fill = fill
        self.bound_this = bound
        self.fill_regs = set()
        self.fill_addr = {}
        self._peripheral_polls = {}
        self._icctrl_busy = 0
        self._switch_base = None
        self._switch_lo = 0
        self._bounded_frames = {}
        self._returned_from_exception = False
        gp, tp = (0xFEBF9800, 0x869C) if fn.entry < 0x20000 or fn.entry in self.boot_copies else (GP, TP)
        self.run = Run(
            fill=fill,
            gp=gp,
            tp=tp,
            stack_lo=self.stack_lo,
            stack_hi=self.stack_hi,
            entry_sp=self.entry_sp,
            arg_base=self.arg_base,
            arg_slots=self.arg_slots,
            stub_slots=list(stub_slots),
        )
        for address in stub_slots:
            for offset in range(4):
                self.run.memory[address + offset] = (0x798 >> (8 * offset)) & 0xFF
        if fn.entry in self.boot_copy_users:
            start = min(self.boot_copies)
            end = max(entry + size for entry, (_source, size) in self.boot_copies.items())
            source = self.boot_copies[start][0]
            payload = self.code[source:source + end - start]
            self.run.code_regions.append((start, payload))
            self.run.memory.update((start + offset, value) for offset, value in enumerate(payload))
        self._root_sites = set(fn.sites)
        self._root_returns = _can_return(fn)
        self.flags = [0, 0, 0, 0]
        self.ep_stack = False
        self.stack_regs = {3}
        self.regs = [SENTINEL] * 32
        # Same reset the P1M-E machine applies: PSW.ID set, every other
        # system register zero. stsr of PSW packs the live condition flags.
        # MCTL.MA is set so a halfword or word the bytes leave unaligned
        # completes, matching the retained misaligned-access scenario.
        self.sr = [[0] * 32 for _ in range(14)]
        self.sr[0][5] = 0x20
        self.sr[1][5] = 2
        arch_returns = {inst.text for inst in fn.insts if inst.kind == "eiret"}
        for name, pc, psw in (("ctret", 16, 17), ("eiret", 0, 1), ("feret", 2, 3)):
            if name in arch_returns:
                self.sr[0][pc] = STOP
                if fn.entry == 0x65BD4 and name == "feret":
                    self.sr[0][pc] = STOP - 4
                self.sr[0][psw] = (fill & 0x1F) | (0 if name == "ctret" else 0x20)
        self.run.system_inputs = self._system_state()
        self.regs[0] = 0
        self.regs[3] = self.entry_sp
        self.regs[4] = gp
        self.regs[5] = tp
        self.regs[31] = STOP
        for index, (pointer, ordinal) in enumerate(params):
            value = self.arg_base + index * ARG_STRIDE if pointer else ordinal
            if pointer:
                value &= ~3
            if index < 4:
                self.regs[6 + index] = value
                continue
            addr = self.entry_sp + (index - 4) * 4
            self._write_ram(addr, 4, value, 3)
            self.run.stack_args.append((addr, value))
        # Setup is the scenario's initial memory, not a store the function made.
        self.run.reads.clear()
        self.run.writes.clear()
        self.root = fn.entry
        self.in_root = False
        blocked = _static_block(fn)
        if blocked:
            raise Harness(blocked)
        self._block(fn, fn.entry)
        self._close_switch()
        self.run.regs = self.regs[:]
        self.run.system_outputs = {
            name: value for name, value in self._system_state().items()
            if value != self.run.system_inputs[name] and (name != "PSW" or self._returned_from_exception)
        }
        return self.run

    def _finish_counted_delay(self) -> None:
        self.regs[12] = 0
        self.regs[13] = 0
        # Last outer decrement is addi of 1 and -1: Z and CY set, S and OV clear.
        self._flags_add(1, _u32(-1))

    def _block(self, fn, pc: int) -> None:
        while self.run.steps < STEP_LIMIT:
            if pc == STOP:
                return
            if self._bounded_stop(pc) or self._halt_branch(pc):
                self.run.halt = pc
                return
            returned = self._return_bounded_callee(pc)
            if returned is not None:
                pc = returned
                continue
            if pc in SPIN_DONE:
                self.run.steps += 1
                self._finish_counted_delay()
                pc = SPIN_DONE[pc]
                continue
            inst = self._inst(pc)
            if inst is None or inst.addr not in fn.sites and self.owner.get(pc) is None:
                raise Harness("fallthrough")
            owner = self.owner.get(pc)
            if owner is None:
                raise Harness("fallthrough")
            self.run.steps += 1
            self.run.visited.add(pc)
            self.in_root = owner.entry == self.root
            pc = self._step(owner, inst)
            if pc is None:
                return
        raise Harness("instruction-budget", self._budget_cause())

    def _budget_cause(self) -> str:
        """Why the closure was still running at the step limit."""
        if self.root == 0 or 0 in self.run.calls:
            return "reset-vector"
        if self._peripheral_polls:
            _addr, count = max(self._peripheral_polls.items(), key=lambda item: item[1])
            if count >= 64:
                return "peripheral-poll"
        return "long-loop"

    def _halt_branch(self, pc: int) -> bool:
        """An unconditional branch to itself does not finish with more steps."""
        inst = self._inst(pc)
        return inst is not None and inst.kind == "br" and inst.target == pc

    def _bounded_stop(self, pc: int) -> bool:
        """Stop a rewritten loop before its self-branch or back-edge."""
        if pc not in self._root_sites:
            return False
        inst = self._inst(pc)
        if inst is None:
            return False
        if not self.bound_this:
            return False
        target = _direct_target(inst)
        if target is None:
            return False
        # The host copy runs one iteration and returns. Stop the bytes at the
        # self-branch, or at that same back-edge. Other functions run to return.
        if target == pc:
            return True
        return target < pc and target in self.run.visited

    def _return_bounded_callee(self, pc: int) -> int | None:
        """A rewritten callee loop returns to its caller after one iteration.

        The host copy replaces while(true) with return. The bytes branch
        back. Restore the caller's stack and callee-saved registers, then
        continue at the return address. A self-branch still halts.
        """
        owner = self.owner.get(pc)
        if owner is None or owner.entry == self.root or owner.entry not in self.bounded_entries:
            return None
        frames = self._bounded_frames.get(owner.entry)
        if not frames:
            return None
        inst = self._inst(pc)
        if inst is None or inst.addr not in owner.sites:
            return None
        target = _direct_target(inst)
        if target is None or target == pc or target not in owner.sites:
            return None
        if not (target < pc and target in self.run.visited):
            return None
        sp, saved = frames.pop()
        self.regs[3] = sp
        self.regs[20:32] = saved
        self._note_sp()
        return saved[11]

    def _inst(self, pc: int) -> Inst | None:
        owner = self.owner.get(pc)
        if owner is None:
            return None
        for inst in owner.insts:
            if inst.addr == pc:
                if owner.entry in self.boot_copies:
                    source, _size = self.boot_copies[owner.entry]
                    offset = source + pc - owner.entry
                    actual = bytes(self.run.memory.get(pc + i, self.fill) for i in range(inst.size))
                    if actual != self.code[offset:offset + inst.size]:
                        raise Harness("external-branch", "RAM bytes differ from recovered boot copy")
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
            return self._transfer(self._fill_callee(inst.reg))
        if kind == "eiret":
            self._returned_from_exception = True
            return self._transfer(self._return_target(inst.text))
        if kind == "jarl_ind":
            self._write_reg(inst.link, nxt)
            return self._transfer(self._fill_callee(inst.reg), call=True)
        if kind == "switch":
            return self._switch(fn, nxt, inst.reg)
        if kind == "jmpdisp":
            return self._transfer(_u32(inst.base + self.regs[inst.reg]))
        if kind == "jr":
            return self._transfer(inst.target)
        if kind == "jarl":
            self._write_reg(inst.link, nxt)
            if self.in_root:
                self.run.call_seq.append(inst.target)
            return self._transfer(inst.target, call=True)
        if kind == "dispose":
            self.regs[3] = _u32(self.regs[3] + (inst.slots << 2))
            for reg in (31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20):
                if inst.mask & (1 << reg):
                    if reg != 3:
                        self._write_reg(reg, self._read_ram(self.regs[3], 4, False, 3))
                    self.regs[3] = _u32(self.regs[3] + 4)
            self._note_sp()
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
        if target in fn.sites:
            return target
        # A branch that leaves the function is a tail call: run the target,
        # then return through the link the caller already holds.
        return self._transfer(target)

    def _fill_callee(self, reg: int) -> int:
        """An unwritten word is not a callee. Call the return stub instead.

        The scenario records that word as 0x798 so the host load reaches the
        same stub. 0x798 is jmp [lp], so the caller continues after the call.
        """
        if reg not in self.fill_regs:
            return self.regs[reg]
        slot = self.fill_addr.get(reg)
        if slot is not None:
            self.run.stub_slots.append(slot)
        return 0x798

    def _transfer(self, target: int, call: bool = False) -> int | None:
        if target == STOP:
            return None
        # Untouched RAM is the scenario fill. An indirect call of that word
        # is not a callee; the other fill still has a real target.
        pattern = (self.fill & 0xFF) * 0x01010101
        if self.fill and target == pattern and target >= 0x100000:
            raise Harness("fill-target")
        owner = self.owner.get(target)
        if owner is None:
            # The boot driver is copied to RAM and called there. The RAM bytes
            # are that flash function, so run the flash function.
            alias = self._overlay_entry(target)
            if alias is not None:
                target = alias
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
        if call and owner.entry == target and target in self.bounded_entries:
            # r31 already holds the return address. r20-r30 are still the caller's.
            self._bounded_frames.setdefault(target, []).append((self.regs[3], list(self.regs[20:32])))
        return target

    def _overlay_entry(self, target: int) -> int | None:
        if any((target + index) not in self.run.memory for index in range(16)):
            return None
        key = bytes(self.run.memory[target + index] for index in range(16))
        return self._overlay_index().get(key)

    def _overlay_index(self) -> dict[bytes, int]:
        cached = getattr(self, "_overlay_entries", None)
        if cached is not None:
            return cached
        found: dict[bytes, int] = {}
        duplicated: set[bytes] = set()
        for fn in self.functions.values():
            entry = fn.entry
            if entry < 0 or entry + 16 > len(self.code):
                continue
            key = self.code[entry:entry + 16]
            if key in found:
                duplicated.add(key)
            else:
                found[key] = entry
        for key in duplicated:
            del found[key]
        self._overlay_entries = found
        return found

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
        if hasattr(self, "fill_regs"):
            self.fill_regs.discard(reg)
            self.fill_addr.pop(reg, None)
        if reg == 3:
            self._note_sp()

    def _note_sp(self) -> None:
        """A stack switch outside the harness window is not a caller-visible store.

        save_registers_switch_stack_apply_mpu_profile_71378 points r3 at 0xfebe2800 and saves the old frame under it.
        The converted C keeps the host stack, so those spills are not checks.
        """
        sp = self.regs[3]
        if self.stack_lo <= sp < self.stack_hi:
            self._close_switch()
            return
        if not (0xFEBE0000 <= sp < 0xFEC00000):
            return
        if self._switch_base is not None and sp > self._switch_base:
            self._close_switch()
        if self._switch_base is None or sp > self._switch_base:
            self._switch_base = sp
            self._switch_lo = sp
        elif sp < self._switch_lo:
            self._switch_lo = sp

    def _close_switch(self) -> None:
        if self._switch_base is not None and self._switch_lo < self._switch_base:
            self.run.switch_spans.append((self._switch_lo, self._switch_base))
        self._switch_base = None

    def _pack_psw(self) -> int:
        z, s, ov, cy = self.flags
        sat = (self.sr[0][5] >> 4) & 1
        return (self.sr[0][5] & ~0x1F) | z | (s << 1) | (ov << 2) | (cy << 3) | (sat << 4)

    def _write_psw(self, value: int) -> None:
        value = _u32(value)
        self.sr[0][5] = value
        self.flags = [value & 1, (value >> 1) & 1, (value >> 2) & 1, (value >> 3) & 1]

    def _system_state(self) -> dict[str, int]:
        return {
            **{name: self.sr[selector][ident] for name, (selector, ident) in SYSTEM_REGISTERS.items()},
            "PSW": self._pack_psw(), "PMR": self.sr[2][11],
            "CDBCR": self.sr[13][24], "ICCTRL": self.sr[4][24],
        }

    def _return_target(self, name: str) -> int:
        if name == "ctret":
            self._write_psw((self._pack_psw() & ~0x1F) | (self.sr[0][17] & 0x1F))
            return self.sr[0][16]
        if (self._pack_psw() & 0x40) == 0 and (self.sr[2][13] & 1) == 0:
            self.sr[2][10] &= _u32(self.sr[2][10] - 1)
        pc = self.sr[0][2 if name == "feret" else 0]
        self._write_psw(self.sr[0][3 if name == "feret" else 1])
        self.sr[2][12] &= ~2
        if (self.sr[0][11] & 1) == 0:
            return pc
        priority = min(self.sr[1][7] & 31, 16)
        if self.sr[2][11] & (1 << min(priority, 15)):
            self.sr[2][12] |= 2
            return pc
        if self.sr[2][10] & ((1 << (priority + 1)) - 1) & 0xFFFF or self._pack_psw() & 0xA0:
            return pc
        self.sr[0][11] = 0
        self.sr[0][0] = pc
        self.sr[0][1] = self._pack_psw()
        self.sr[0][13] = 0x72
        self._write_psw((self._pack_psw() & 0xBFFFFFFF) | 0x60)
        return (self.sr[1][3 if self._pack_psw() & 0x8000 else 2] & 0xFFFFFE00) + 0x70

    def _op_ldsr(self, src: int, ident: int, sel: int) -> None:
        if not (0 <= sel < len(self.sr) and 0 <= ident < 32):
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
        if not (0 <= sel < len(self.sr) and 0 <= ident < 32):
            self._write_reg(dst, 0)
            return
        if sel == 4 and ident == 24:
            value = self.sr[4][24]
            if value & 0x100:
                self._icctrl_busy += 1
                if self._icctrl_busy == ICCTRL_BUSY_READS:
                    value &= ~0x100
                    self.sr[4][24] = value
                    self._icctrl_busy = 0
            else:
                self._icctrl_busy = 0
        if sel == 0 and ident == 5:
            value = self._pack_psw()
        elif sel == 13 and ident == 24:
            # CDBCR.CDBCLR reads as zero. The machine's stsr already masks it.
            value = self.sr[13][24] & ~2
        else:
            value = self.sr[sel][ident]
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
        if src in self.fill_regs:
            self.fill_regs.add(dst)
            if src in self.fill_addr:
                self.fill_addr[dst] = self.fill_addr[src]

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

    def _op_sbf(self, dst: int, src: int, other: int, cc: int) -> None:
        borrow = int(self._take(cc))
        left, right = self.regs[other], self.regs[src]
        result = _u32(left - right - borrow)
        self.flags = [
            int(result == 0),
            result >> 31,
            int(bool((left ^ right) & (left ^ result) & 0x80000000)),
            int(left < right + borrow),
        ]
        self._write_reg(dst, result)

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

    def _op_bins(self, dst: int, src: int, pos: int, width: int) -> None:
        mask = (1 << width) - 1
        result = _u32((self.regs[dst] & ~(mask << pos)) | ((self.regs[src] & mask) << pos))
        self.flags[0] = int(result == 0)
        self.flags[1] = result >> 31
        self.flags[2] = 0
        self._write_reg(dst, result)

    def _read_pair(self, even: int) -> int:
        if even == 0:
            return self.regs[1] << 32
        return (self.regs[even + 1] << 32) | self.regs[even]

    def _write_pair(self, even: int, value: int) -> None:
        if even == 0:
            self._write_reg(1, (value >> 32) & 0xFFFFFFFF)
            return
        self._write_reg(even, value & 0xFFFFFFFF)
        self._write_reg(even + 1, (value >> 32) & 0xFFFFFFFF)

    def _mac(self, src1: int, src2: int, acc: int, dst: int, signed: bool) -> None:
        if signed:
            left = self.regs[src1] - 0x100000000 if self.regs[src1] >> 31 else self.regs[src1]
            right = self.regs[src2] - 0x100000000 if self.regs[src2] >> 31 else self.regs[src2]
        else:
            left, right = self.regs[src1], self.regs[src2]
        self._write_pair(dst, (self._read_pair(acc) + left * right) & ((1 << 64) - 1))

    def _op_mac(self, src1: int, src2: int, acc: int, dst: int) -> None:
        self._mac(src1, src2, acc, dst, True)

    def _op_macu(self, src1: int, src2: int, acc: int, dst: int) -> None:
        self._mac(src1, src2, acc, dst, False)

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
        self._write_reg(reg, self.regs[reg] & 0xFF)

    def _op_zxh(self, reg: int) -> None:
        self._write_reg(reg, self.regs[reg] & 0xFFFF)

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
        self._cover_field_base(base, disp, size)
        addr = _u32(self.regs[base] + disp)
        self._write_reg(dst, self._read_ram(addr, size, signed, base))
        # An unwritten scenario word is the fill, not a callee. A later
        # indirect call of that register is skipped so the other fill can run.
        if dst != 0 and not signed and self._fill_word(addr, size):
            self.fill_regs.add(dst)
            self.fill_addr[dst] = addr

    def _fill_word(self, addr: int, size: int) -> bool:
        if self._image(addr, size) is not None or self._overlaid(addr, size) is not None:
            return False
        pattern = self.fill & 0xFF
        return all(self.run.memory.get(addr + offset, pattern) == pattern for offset in range(size))

    def _store(self, src: int, base: int, disp: int, size: int) -> None:
        self._cover_field_base(base, disp, size)
        self._write_ram(_u32(self.regs[base] + disp), size, self.regs[src], base)

    def _cover_field_base(self, base: int, disp: int, size: int) -> None:
        """The C takes camry_host_ptr of the base and then the field.

        The bytes only touch the field. A positive displacement is that field,
        so the scenario window starts at the register or the host reads a zero
        page there.
        """
        if disp <= 0 or disp > 0x400 or base in {3, 4, 5}:
            return
        origin = self.regs[base]
        if origin < 0x100:
            return
        end = origin + disp + size
        if end > 0x100000000:
            return
        if not (end <= self.stack_lo or origin >= self.stack_hi):
            return
        arg_end = self.arg_base + self.arg_slots * ARG_STRIDE
        if not (end <= self.arg_base or origin >= arg_end):
            return
        if _space(origin, 1) in {"code", "code-ext", "data", "alias"}:
            return
        self.run.reads.add((origin, end - origin))

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
        self._cover_field_base(base, disp, 1)
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
                self._note_sp()
                self._write_ram(self.regs[3], 4, self.regs[reg], 3)
        # The allocated frame is this call's locals. An earlier frame's bytes
        # are not still stored there; an unwritten local reads as the fill.
        frame = slots << 2
        self.regs[3] = _u32(self.regs[3] - frame)
        self._note_sp()
        for offset in range(frame):
            slot = self.regs[3] + offset
            if self.stack_lo <= slot < self.stack_hi:
                self.run.memory.pop(slot, None)
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
        pointer = self.regs[3]
        for reg in range(low, high + 1):
            pointer = _u32(pointer - 4)
            self._write_ram(pointer & ~3, 4, self.regs[reg], 3)
        self.regs[3] = pointer
        self._note_sp()

    def _op_popsp(self, low: int, high: int) -> None:
        if low > high:
            return
        for reg in range(high, low - 1, -1):
            if reg != 3:
                self._write_reg(reg, self._read_ram(self.regs[3], 4, False, 3))
            self.regs[3] = _u32(self.regs[3] + 4)
        self._note_sp()

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

    def _search(self, src: int, dst: int, one: bool, left: bool) -> None:
        value = self.regs[src] if one else _u32(~self.regs[src])
        count = 0 if value == 0 else (
            33 - value.bit_length() if left else (value & -value).bit_length()
        )
        self.flags = [int(count == 0), 0, 0, int(count == 32)]
        self._write_reg(dst, count)

    def _op_sch0r(self, src: int, dst: int) -> None:
        self._search(src, dst, False, False)

    def _op_sch1r(self, src: int, dst: int) -> None:
        self._search(src, dst, True, False)

    def _op_sch0l(self, src: int, dst: int) -> None:
        self._search(src, dst, False, True)

    def _op_sch1l(self, src: int, dst: int) -> None:
        self._search(src, dst, True, True)

    def _kind_of(self, addr: int, size: int, base: int) -> str:
        misaligned = size == 2 and addr & 1 or size >= 4 and addr & 3
        if misaligned and not (self.allow_unaligned and size < 8):
            raise Harness("misaligned")
        stack_base = base in self.stack_regs or (base == 30 and self.ep_stack)
        if self.stack_lo <= addr and addr + size <= self.stack_hi:
            # The window sits in RAM this function does not use as globals.
            # An EP or reloaded frame pointer is still the stack.
            if not stack_base and not self.relocated:
                raise Harness("harness-overlap")
            return "stack"
        arg_end = self.arg_base + self.arg_slots * ARG_STRIDE
        if self.arg_base <= addr and addr + size <= arg_end:
            if stack_base:
                raise Harness("stack-frame")
            return "arg"
        if stack_base:
            raise Harness("stack-frame")
        space = _space(addr, size)
        if space == "code-ext":
            raise Harness("code-extension")
        return space

    def _overlaid(self, addr: int, size: int) -> int | None:
        """A store onto code is visible to a later load. Fetch still uses the image."""
        if not (0 <= addr and addr + size <= len(self.code)):
            return None
        if not any((addr + offset) in self.run.memory for offset in range(size)):
            return None
        image = self._image(addr, size)
        raw = 0
        for offset in range(size):
            if (addr + offset) in self.run.memory:
                byte = self.run.memory[addr + offset]
            elif image is not None:
                byte = (image >> (8 * offset)) & 0xFF
            else:
                byte = self.fill
            raw |= byte << (8 * offset)
        return raw

    def _return_stub(self, addr: int, size: int) -> bool:
        # jmp [lp] is the halfword 0x007f. The bytes store over that stub.
        if size != 2 or addr & 1 or addr < 0 or addr + 2 > len(self.code):
            return False
        return self.code[addr] == 0x7F and self.code[addr + 1] == 0x00

    def _read_ram(self, addr: int, size: int, signed: bool, base: int) -> int:
        if 0xFEDE0000 <= addr < 0xFEE00000:
            if size > 0xFEE00000 - addr:
                raise Harness("mmio", f"{addr:#x}")
            addr -= 0x200000
        kind = self._kind_of(addr, size, base)
        overlaid = self._overlaid(addr, size)
        image = None if overlaid is not None else self._image(addr, size)
        if overlaid is not None:
            raw = overlaid
            if kind in {"local", "global", "stack", "arg", "mmio"}:
                self.run.reads.add((addr, size))
            return _sext(raw, size * 8) if signed else raw
        if image is None:
            if kind in {"code", "data", "code-ext"}:
                raise Harness("code-extension")
            if kind not in {"stack", "arg", "local", "global", "mmio"}:
                raise Harness("mmio")
            raw = 0
            for offset in range(size):
                raw |= self.run.memory.get(addr + offset, self.fill) << (8 * offset)
            self.run.reads.add((addr, size))
            raw = self._poll_peripheral(addr, size, raw)
        else:
            raw = image
        if kind in {"local", "global", "stack", "arg", "mmio"}:
            self.run.reads.add((addr, size))
        return _sext(raw, size * 8) if signed else raw

    def _poll_peripheral(self, addr: int, size: int, raw: int) -> int:
        """The Nth read of one peripheral completes the poll.

        A byte becomes all-ones, then zero on the next N reads, so a wait
        for a status bit and a wait for a clear byte both end. A zero word
        becomes all-ones. Any other word becomes zero.
        """
        if addr < 0xFF000000 or 0xFF200000 <= addr < 0xFF208000:
            return raw
        count = self._peripheral_polls.get(addr, 0) + 1
        self._peripheral_polls[addr] = count
        if size == 1 and count == PERIPHERAL_POLL_READS * 2:
            raw = 0
        elif count != PERIPHERAL_POLL_READS:
            return raw
        elif size == 1:
            raw = 0xFF
        else:
            raw = 0 if raw else (1 << (size * 8)) - 1
        for offset in range(size):
            self.run.memory[addr + offset] = (raw >> (8 * offset)) & 0xFF
        self.run.writes.add((addr, size))
        return raw

    def _image(self, addr: int, size: int) -> int | None:
        if 0 <= addr and addr + size <= len(self.code):
            return int.from_bytes(self.code[addr:addr + size], "little")
        if self.data_base <= addr and addr + size <= self.data_base + len(self.data):
            offset = addr - self.data_base
            return int.from_bytes(self.data[offset:offset + size], "little")
        return None

    def _write_ram(self, addr: int, size: int, value: int, base: int) -> None:
        if 0xFEDE0000 <= addr < 0xFEE00000:
            if size > 0xFEE00000 - addr:
                raise Harness("mmio", f"{addr:#x}")
            addr -= 0x200000
        kind = self._kind_of(addr, size, base)
        if kind == "code" and not self._return_stub(addr, size):
            raise Harness("code-write", f"{addr:#x}")
        if kind == "data":
            raise Harness("dataflash-write")
        if kind not in {"stack", "arg", "local", "global", "mmio", "code"}:
            raise Harness("mmio")
        for offset in range(size):
            self.run.memory[addr + offset] = (value >> (8 * offset)) & 0xFF
        self._note_sp()
        self.run.writes.add((addr, size))


class _NativeHarnessMachine(_Machine):
    """Reuse arithmetic, never the oracle's image fetch or memory model."""

    def __init__(self, script_regions, read_memory, write_memory) -> None:
        super().__init__(b"", b"", 0, {})
        self.script_regions = sorted(script_regions)
        end = 0
        for base, blob in self.script_regions:
            if not blob or base & 1 or base < end or _space(base, len(blob)) not in {"local", "global", "alias"}:
                raise ValueError("script regions must be disjoint, halfword-aligned literal RAM bytes")
            end = base + len(blob)
        self.read_memory = read_memory
        self.write_memory = write_memory
        self.instructions: dict[int, Inst] = {}

    def _script_bytes(self, address: int, size: int) -> bytes | None:
        for base, blob in self.script_regions:
            offset = address - base
            if 0 <= offset and offset + size <= len(blob):
                return blob[offset:offset + size]
        return None

    def _inst(self, pc: int) -> Inst | None:
        if pc in self.instructions:
            return self.instructions[pc]
        for base, blob in self.script_regions:
            if base <= pc < base + len(blob):
                if pc & 1:
                    raise Harness("misaligned", hex(pc))
                inst = decode_at(blob, pc - base)
                if inst is None:
                    raise Harness("unmodeled", f"RAM script at {pc:#x}")
                # Only these fields contain decoder-PC-relative destinations.
                # mov immediates and jmpdisp.base are absolute and stay intact.
                inst.addr = pc
                if inst.kind in {"br", "b", "loop", "jr", "jarl"}:
                    inst.target = _u32(base + inst.target)
                self.instructions[pc] = inst
                return inst
        return None

    def _sequential(self, fn, nxt: int) -> int:
        return _u32(nxt)

    def _jump(self, fn, target: int) -> int:
        return _u32(target)

    def _transfer(self, target: int, call: bool = False) -> int:
        return _u32(target)

    def _fill_callee(self, reg: int) -> int:
        return self.regs[reg]

    def _fill_word(self, addr: int, size: int) -> bool:
        return False

    def _cover_field_base(self, base: int, disp: int, size: int) -> None:
        pass

    def _read_ram(self, addr: int, size: int, signed: bool, base: int) -> int:
        value = self.read_memory(addr, size) & ((1 << (8 * size)) - 1)
        return _sext(value, 8 * size) if signed else value

    def _write_ram(self, addr: int, size: int, value: int, base: int) -> None:
        self.write_memory(addr, size, value & ((1 << (8 * size)) - 1))

    def _step(self, fn, inst: Inst) -> int:
        if inst.kind == "jarl_ind":
            target = self.regs[inst.reg]
            self._write_reg(inst.link, inst.addr + inst.size)
            return target
        return super()._step(fn, inst)

    def _switch(self, fn, nxt: int, reg: int) -> int:
        slot = _u32(nxt + (self.regs[reg] << 1))
        if self._script_bytes(slot, 2) is None:
            raise Harness("external-branch", f"RAM script switch table at {slot:#x}")
        disp = self._read_ram(slot, 2, True, 0)
        return _u32(nxt + (disp << 1))

    def _import_registers(self, registers: Mapping[str, str | int]) -> None:
        aliases = {"sp": 3, "gp": 4, "tp": 5, "ep": 30, "lp": 31}
        system = {**SYSTEM_REGISTERS, "PSW": (0, 5), "PMR": (2, 11),
                  "CDBCR": (13, 24), "ICCTRL": (4, 24)}
        for name, raw in registers.items():
            value = _u32(int(raw, 0) if isinstance(raw, str) else raw)
            reg = aliases.get(name.lower())
            if reg is None and re.fullmatch(r"r(?:[0-9]|[12][0-9]|3[01])", name.lower()):
                reg = int(name[1:])
            if reg is not None:
                self._write_reg(reg, value)
            elif name.upper() in system:
                selector, ident = system[name.upper()]
                if name.upper() == "PSW":
                    self._write_psw(value)
                else:
                    self.sr[selector][ident] = value
            else:
                raise ValueError(f"unknown native harness register: {name}")

    def _export_registers(self) -> dict[str, str]:
        return {
            **{f"r{index}": hex(value) for index, value in enumerate(self.regs)},
            **{name: hex(value) for name, value in self._system_state().items()},
        }


def run_native_harness(
    entry: int,
    registers: Mapping[str, str | int],
    script_regions: Iterable[tuple[int, bytes]],
    read_memory: Callable[[int, int], int],
    write_memory: Callable[[int, int, int], None],
    call_native: Callable[[int, dict[str, str]], Mapping[str, str | int] | None],
    stop_addresses: Iterable[int],
    limit: int,
    before_instruction: Callable[[int, dict[str, str]], None] | None = None,
) -> dict:
    """Run native firmware interleaved with explicitly owned literal RAM scripts.

    ``script_regions`` is an explicit whitelist, not a collection of all mapped
    RAM: callers MUST exclude copied firmware bytes. Only those literals are
    decoded, at their actual RAM PCs; self-modifying scripts are not supported.
    No image is loaded or consulted. ``read_memory(address, byte_width)`` and
    ``write_memory(address, byte_width, value)`` MUST access the native C's same
    mapped memory, including the script stack, not reference/expected memory.

    Every non-script destination (including the root firmware entry) goes to
    ``call_native(address, registers)``. It MUST execute actual native C, and
    reject addresses outside its native domain by returning None or raising;
    there is no byte-execution fallback. It returns complete or partial register
    updates, optionally including ``pc`` (or ``PC``) for an interior stop or
    RAM callback. Otherwise execution resumes at the updated lp/r31.

    Register values accept integers or hex strings. Input/update names accept
    r0..r31, sp/gp/tp/ep/lp, and modeled system-register names. Exported maps
    contain canonical r0..r31 and system names, with hex values and no pc.
    ``before_instruction(pc, registers)`` may mutate its register map; it runs
    before each script instruction/native dispatch AND before the stop check,
    allowing timed inputs and stop provenance to share the caller's clock.
    Native-internal instruction hooks, stops and budgets remain the native
    callback's responsibility.

    ``limit`` bounds script instructions plus native dispatches. Reaching a
    supplied stop returns {registers, pc, steps, reason: "stop-address"}; unknown
    instructions/targets and exhausted budgets raise Harness, without retries.
    """
    machine = _NativeHarnessMachine(script_regions, read_memory, write_memory)
    machine._import_registers(registers)
    stops = set(stop_addresses)
    pc = _u32(entry)
    steps = 0
    while True:
        if before_instruction is not None:
            state = machine._export_registers()
            before_instruction(pc, state)
            machine._import_registers(state)
        if pc in stops:
            return {"registers": machine._export_registers(), "pc": hex(pc),
                    "steps": steps, "reason": "stop-address"}
        if steps >= limit:
            raise Harness("instruction-budget", f"native harness at {pc:#x}")
        inst = machine._inst(pc)
        if inst is not None:
            pc = machine._step(None, inst)
        else:
            updates = call_native(pc, machine._export_registers())
            if updates is None:
                raise Harness("external-branch", f"no native C target at {pc:#x}")
            updates = dict(updates)
            resume = updates.pop("pc", updates.pop("PC", None))
            machine._import_registers(updates)
            pc = _u32(int(resume, 0) if isinstance(resume, str) else resume) if resume is not None else machine.regs[31]
        steps += 1

