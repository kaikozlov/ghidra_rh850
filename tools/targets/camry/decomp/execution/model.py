"""Shared Camry oracle harness limits and execution records."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import re


MAX_BODY = 16384


POLL_STEP_LIMIT = 800000


STEP_LIMIT = 8000000


# A peripheral word read this many times is a poll. Zero becomes all-ones
# (a status bit set); any other value becomes zero (a command bit cleared).
# The same threshold is in RunP1MEMachine.java and host_memory.c.
PERIPHERAL_POLL_READS = 4096


# ICCTRL bit 8 is the cache clear request. The CPU leaves it set; the
# environment clears it after this many busy reads. Returning functions do
# not read ICCTRL. The same count is in RunP1MEMachine.java and host_memory.c.
ICCTRL_BUSY_READS = 4


# movea that reloads the inner counter -> the jmp after the outer decrement.
# r12/r13 only count down; finishing them is the same architectural state.
SPIN_DONE = {0x7210: 0x721C, 0x71C70: 0x71C7C, 0x71C88: 0x71C94}


SCRATCH = 0xFEBE0000


SCRATCH_SIZE = 4


SENTINEL = 0x11111111


# 0x798 is return_only_stub_798, a real jmp [lp]. A call of that stub was
# the sentinel return, so the caller's dispose never ran.
STOP = 0xFFFFE


GP = 0xFEBEB800


TP = 0x23DFC


# host_memory.c CAMRY_HOST_REGIONS. CodeFlash and DataFlash use two.
HOST_REGIONS = 64


DATA_REGIONS = HOST_REGIONS - 2


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
    "register-mismatch",
    "dropped-return",
    "invented-return",
    "host-unmapped",
}


REASONS = {
    "large": "this run harnesses functions of at most 16384 bytes; larger bodies stay converted",
    "outside-codeflash": "the entry is outside the CodeFlash image the machine executes",
    "undecoded": "the lifter cannot walk every byte of the function, so the harness has no instruction list",
    "no-converted-body": "no retained, curated, or selected candidate C body is available, so the host check has nothing to call",
    "duplicate-body": "the same name has multiple definitions in the selected source bank, so the host library cannot link it",
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
    "region-cap": "codeflash and dataflash already use two host regions, and the other accesses do not fit in the rest",
    "no-observable": "the bytes do not write r10 or caller-visible memory, and the unchanged local-RAM scratch does not fit the host region cap",
    "uninitialized-read": "the machine read a byte the harness did not initialize",
    "simulator": "the P1M-E machine did not return a report for this scenario",
    "harness-drift": "the machine's result does not match the harness interpreter, so the scenario window is not trusted",
    "host-unmapped": "the converted C dereferenced an address the scenario did not map",
    "host-fault": "the converted C aborted in the host check",
    "host-link": "the converted closure calls a function that has no body and no prototype, so the host library cannot link it",
    "host-compile": "the converted body does not compile in the host check",
    "trace-cap": "the memory-access trace omitted new write addresses, so the write set is incomplete",
    "dropped-return": "a caller reads r10 after this call and the converted C is void",
    "invented-return": "the bytes leave the incoming r10 alone and the converted C returns a value",
    "return-mismatch": "the host return does not equal the original r10",
    "memory-mismatch": "a caller-visible memory write differs",
    "register-mismatch": "a caller-visible architectural register differs",
    "call-sequence": "the host call sequence differs from the bytes up to the bounded stop",
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
    call_seq: list[int] = field(default_factory=list)
    visited: set[int] = field(default_factory=set)
    steps: int = 0
    fill: int = 0
    gp: int = GP
    tp: int = TP
    # PC of a self-branch or non-returning back-edge. Execution stops before it.
    halt: int | None = None
    stack_lo: int = STACK_LO
    stack_hi: int = STACK_HI
    entry_sp: int = ENTRY_SP
    arg_base: int = ARG_BASE
    arg_slots: int = ARG_COUNT
    stack_args: list[tuple[int, int]] = field(default_factory=list)
    # Addresses whose unwritten word was used as an indirect-call target.
    stub_slots: list[int] = field(default_factory=list)
    # [lo, hi) frames under a stack pointer the converted C does not use.
    switch_spans: list[tuple[int, int]] = field(default_factory=list)
    system_inputs: dict[str, int] = field(default_factory=dict)
    system_outputs: dict[str, int] = field(default_factory=dict)
    code_regions: list[tuple[int, bytes]] = field(default_factory=list)


@dataclass
class Planned:
    address: int
    name: str
    signature: str
    body: str
    runs: list[Run]
    calls: set[int]
    windows: list[tuple[int, int]]
    pointers: list[bool]
    bounded: bool = False


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

