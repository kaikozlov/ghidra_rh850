#!/usr/bin/env python3
"""Control-slot oracle for camry-8965F3307000 (F33 EPS) on the exact-image GNU sim.

The static store census cannot bound stores whose target is a register
pointer.  This oracle watches the control-relevant memory itself while the
stock diagnostic and CAN paths execute, so every store is judged at access
time from the simulator's instruction-attributed memory-access trace:

* **Saved-slot tracking.**  Every store issued by a ``prepare`` marks its
  target as a live saved slot (the ``lp`` store is the saved return address)
  until a ``dispose`` reads it.  Any other write to a live slot, any read of a
  live slot by a non-owning instruction, and any second ``prepare`` onto a slot
  whose owner never disposed are violations.
* **Hook-cell tracking.**  Any write to the ten callback/service cells of the
  task context by a PC that is not a stock installer is a violation.  The
  installer PCs are derived from the image (``tools/pseudo --data-ref``
  writers of each cell).
* **Tail tracking.**  Any write into ``0xFEBFF9F0..0xFEBFFBFB`` or
  ``0xFEBF7C00..0xFEBFFBFB`` is a violation.

PREPARE/DISPOSE sites are derived from the image with one offline objdump
run that sweeps every function extent from its own entry (extents are padded
with NOPs so each sweep re-synchronizes).  Every executed site must then match
its decoded shape in the trace (register count, word width, consecutive
descending/ascending words); a mismatch is an oracle-integrity anomaly that is
reported, never ignored silently.

Self-validation (docs/security/fuzz-oracle-methodology.md §5) precedes every
clean result: sim-only single-instruction gadgets write a live saved-return
slot, a live callee-saved slot, a hook cell, the executable tail and the RWX
pocket, and read a live saved-return slot; each must be flagged, and the
unmodified baseline must report zero violations.

Trace machinery is reused from the existing harnesses (``parse_core_accesses``,
``group_script``, ``lean_prelude``, ``trial_image``, ``scenario_image`` and
``case_script``).  Run with ``python -m``.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import subprocess
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from tools import REPO_ROOT
from tools.rh850_codeflash import CodeFlashSimError, run_elf
from tools.targets.camry.research import audit_camry_f33_ab_event_output_contract as ab
from tools.targets.camry.research import fuzz_camry_f33_cantp_ingress as ci
from tools.targets.camry.research import fuzz_camry_f33_dcm_handlers as dcm
from tools.targets.camry.research import fuzz_camry_f33_stateful_coverage as sc

SCHEMA = "camry-f33-control-slot-oracle-v1"
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/route2-20261123/oracle"
IMAGE = dcm.IMAGE
IMAGE_SHA256 = dcm.IMAGE_SHA256
PSEUDOCODE_INDEX = REPO_ROOT / "build/out/pseudocode/index.tsv"

# Callback/service cells a stock path calls without reinstalling
# (baseline §13.5, §13.15).
HOOK_CELLS = (
    0xFEBF117C, 0xFEBF1180, 0xFEBF1194, 0xFEBF1198,
    0xFEBF131C, 0xFEBF1320, 0xFEBF1324,
    0xFEBE5628, 0xFEBF0FD0, 0xFEBF6B04,
)
EXECUTABLE_TAIL = (0xFEBFF9F0, 0xFEBFFBFB)
RWX_POCKET = (0xFEBF7C00, 0xFEBFFBFB)
CODE_FLASH_END = 0x100000
SESSIONS = (1, 2, 3)
BITMAPS = (0, 1, 2, 0xFFFFFFFF)
FAMILIES = ("dcm", "cantp", "stateful", "ab")

VIOLATION_CLASSES = (
    "saved-return-write", "saved-register-write",
    "saved-return-read", "saved-register-read",
    "saved-return-reprepared", "saved-register-reprepared",
    "hook-cell-write", "executable-tail-write", "rwx-pocket-write",
)
ANOMALY_CLASSES = (
    "prepare-shape-mismatch", "dispose-shape-mismatch",
    "dispose-read-of-nonlive", "saved-return-restored-different",
    "prepare-truncated-at-trace-end", "dispose-truncated-at-trace-end",
    "swept-decode-conflict", "prepare-like-in-sweep-gap",
)

OBJDUMP_LINE = re.compile(r"^\s*([0-9a-f]+):\t([0-9a-f]{2}(?: [0-9a-f]{2})*)\s*(.*)$")
DATA_REF_LINE = re.compile(
    r"^(0x[0-9a-f]+)\s+(READ|WRITE)\s+(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+(\S+)\s+op=(\d+)\s*$"
)
STORE_GADGET = re.compile(r"^st\.w\tr10, 0\[r8\]$")
LOAD_GADGET = re.compile(r"^ld\.w\t0\[r1\], r1$")
EXTENT_CAP = 0x8000
RESYNC_PAD = 16
APPLICATION_ENTRY = 0x20880
MAX_TRACE_BYTES = 200 * 1024 * 1024
SAMPLE_LIMIT = 40
SEED_VALUE = 0xA5A5A5A5


def hx(value: int | None) -> str | None:
    return None if value is None else f"0x{value:08x}"


# ---------------------------------------------------------- static derivation

@dataclass(frozen=True)
class Site:
    address: int
    kind: str                   # "prepare" | "dispose"
    length: int                 # 4, 6 or 8 bytes
    imm: int
    registers: tuple[int, ...]  # pushed order: r20..r29, r30 (ep), r31 (lp)
    text: str

    @property
    def access_pc(self) -> int:
        # The simulator attributes an instruction's accesses to its last
        # fetched halfword.
        return self.address + self.length - 2


@dataclass
class SiteTable:
    sites: dict[int, Site]
    by_access_pc: dict[int, Site]
    imap: dict[int, tuple[int, str]]
    entries: list[int]
    names: dict[int, str]
    installers: dict[int, dict]
    installer_trace_pcs: dict[int, set[int]]
    installer_instructions: dict[int, set[int]]
    gadgets: dict[str, int]
    entry_set: set[int]
    prepare_like: set[int]

    def function_of(self, address: int) -> tuple[int | None, str | None]:
        index = bisect.bisect_right(self.entries, address) - 1
        if index < 0:
            return None, None
        entry = self.entries[index]
        return entry, self.names.get(entry)

    def instruction_start(self, pc: int) -> int | None:
        imap = self.imap
        for start, length in ((pc - 6, 8), (pc - 4, 6), (pc - 2, 4), (pc, 2)):
            if imap.get(start, (None, None))[0] == length:
                return start
        return None


def load_functions() -> list[tuple[int, str]]:
    """Function entries from the materialized pseudocode index (read-only)."""
    rows: list[tuple[int, str]] = []
    with PSEUDOCODE_INDEX.open(encoding="utf-8") as stream:
        next(stream)
        for line in stream:
            fields = line.rstrip("\n").split("\t")
            rows.append((int(fields[0], 16), fields[1]))
    rows.sort()
    return rows


def run_objdump(args: list[str]) -> str:
    return subprocess.run(
        [str(REPO_ROOT / "tools/rh850"), "toolchain", "run", "v850-elf-objdump",
         "-D", "-b", "binary", "-m", "v850e3v5", "--adjust-vma=0", *args],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True, timeout=600,
    ).stdout


def sweep_functions(image: bytes, functions: list[tuple[int, str]],
                    work: Path) -> dict[int, tuple[int, str]]:
    """Decode every function extent from its own entry in one objdump run.

    Each extent is followed by at least two NOP halfwords (``00 00``), so a
    sweep that lost instruction alignment inside a function re-synchronizes
    before the next entry.
    """
    image_functions = [(entry, name) for entry, name in functions if entry < len(image)]
    blob = bytearray()
    spans: list[tuple[int, int, int]] = []
    for index, (entry, _name) in enumerate(image_functions):
        following = (image_functions[index + 1][0] if index + 1 < len(image_functions)
                     else len(image))
        extent = image[entry:min(following, entry + EXTENT_CAP)]
        spans.append((len(blob), entry, len(extent)))
        blob += extent
        padding = RESYNC_PAD - len(extent) % RESYNC_PAD
        blob += b"\x00" * (padding if padding >= 2 else padding + RESYNC_PAD)
    padded = work / "functions-padded.bin"
    padded.write_bytes(blob)
    try:
        listing = subprocess.run(
            dcm.rh850_command(work) + [
                "v850-elf-objdump", "-D", "-b", "binary", "-m", "v850e3v5",
                "--adjust-vma=0", "/out/functions-padded.bin",
            ],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True, timeout=600,
        ).stdout
    finally:
        padded.unlink(missing_ok=True)
    starts = [span[0] for span in spans]
    imap: dict[int, tuple[int, str]] = {}
    last: int | None = None
    for line in listing.splitlines():
        match = OBJDUMP_LINE.match(line)
        if match is None:
            continue
        address = int(match.group(1), 16)
        size = len(match.group(2).split())
        text = match.group(3)
        if last is not None and not text:
            # Continuation halfword(s) of a 48/64-bit instruction.
            imap[last] = (imap[last][0] + size, imap[last][1])
            continue
        last = None
        index = bisect.bisect_right(starts, address) - 1
        pad_start, entry, extent_length = spans[index]
        offset = address - pad_start
        if offset + size > extent_length:
            continue                     # straddles into the NOP padding
        last = entry + offset
        imap[last] = (size, text)
    return imap


def register_number(token: str) -> int:
    if token == "lp":
        return 31
    if token == "ep":
        return 30
    if len(token) >= 2 and token[0] == "r" and token[1:].isdigit():
        return int(token[1:])
    raise ValueError(f"unknown register {token!r}")


def parse_register_list(text: str) -> tuple[int, ...]:
    inner = text.strip()
    if not (inner.startswith("{") and inner.endswith("}")):
        raise ValueError(f"unexpected register list {text!r}")
    registers: list[int] = []
    for token in inner[1:-1].split(","):
        token = token.strip()
        if not token:
            continue
        if " - " in token:
            low, high = token.split(" - ")
            registers.extend(range(register_number(low.strip()),
                                  register_number(high.strip()) + 1))
        else:
            registers.append(register_number(token))
    return tuple(sorted(registers))


def split_operands(operands: str) -> list[str]:
    """Comma-split an operand string, ignoring commas inside {register lists}."""
    items: list[str] = []
    depth = 0
    current = ""
    for character in operands:
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
        if character == "," and depth == 0:
            items.append(current.strip())
            current = ""
        else:
            current += character
    items.append(current.strip())
    if depth != 0:
        raise ValueError(f"unbalanced register list in {operands!r}")
    return [item for item in items if item]


def build_sites(imap: dict[int, tuple[int, str]]) -> dict[int, Site]:
    """``prepare {list}, imm[, variant]`` and ``dispose imm, {list}[, reg]``."""
    sites: dict[int, Site] = {}
    for address, (length, text) in imap.items():
        mnemonic, _, operands = text.partition("\t")
        if mnemonic not in ("prepare", "dispose"):
            continue
        items = split_operands(operands)
        list_index = 0 if mnemonic == "prepare" else 1
        imm_index = 1 - list_index
        if len(items) <= max(list_index, imm_index) or not items[list_index].endswith("}"):
            raise ValueError(f"malformed {mnemonic} at {address:#x}: {text!r}")
        sites[address] = Site(address, mnemonic, length, int(items[imm_index], 0),
                              parse_register_list(items[list_index]), text)
    return sites


def instruction_length(image: bytes, address: int) -> int:
    """Length of the instruction at a true instruction start (objdump)."""
    listing = run_objdump([
        f"--start-address={address:#x}",
        f"--stop-address={min(address + 8, len(image)):#x}",
        "/src/firmware/camry-8965F3307000/CodeFlash.bin",
    ])
    for line in listing.splitlines():
        match = OBJDUMP_LINE.match(line)
        if match and int(match.group(1), 16) == address:
            return len(match.group(2).split())
    raise RuntimeError(f"objdump did not decode {address:#x}")


def derive_installers(image: bytes, imap: dict[int, tuple[int, str]]) -> dict[int, dict]:
    """Stock writers of every hook cell, from the image's decoded references."""
    result: dict[int, dict] = {}
    for cell in HOOK_CELLS:
        proc = subprocess.run(
            [str(REPO_ROOT / "tools/pseudo"), "--data-ref", f"{cell:#x}"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True, timeout=600,
        )
        writers, readers = [], []
        for line in proc.stdout.splitlines():
            match = DATA_REF_LINE.match(line)
            if match is None:
                continue
            row = {
                "instruction": int(match.group(1), 16),
                "function": int(match.group(4), 16),
                "name": match.group(5),
            }
            (writers if match.group(2) == "WRITE" else readers).append(row)
        for row in writers:
            length = imap.get(row["instruction"], (None, ""))[0]
            if length is None:
                length = instruction_length(image, row["instruction"])
            row["length"] = length
            row["trace_pc"] = row["instruction"] + length - 2
        result[cell] = {
            "writers": sorted(writers, key=lambda row: row["instruction"]),
            "readers": sorted(readers, key=lambda row: row["instruction"]),
        }
    return result


def find_gadgets(imap: dict[int, tuple[int, str]]) -> dict[str, int]:
    """First single-instruction store/load through a pointer register."""
    gadgets: dict[str, int] = {}
    for address in sorted(imap):
        if address < APPLICATION_ENTRY:
            continue
        text = imap[address][1]
        if "store" not in gadgets and STORE_GADGET.match(text):
            gadgets["store"] = address
        if "load" not in gadgets and LOAD_GADGET.match(text):
            gadgets["load"] = address
        if len(gadgets) == 2:
            break
    if len(gadgets) != 2:
        raise RuntimeError(f"seed gadgets not found in the image: {gadgets}")
    return gadgets


def prepare_like_addresses(image: bytes) -> set[int]:
    """Every 2-byte-aligned image address whose halfword is a PREPARE or
    DISPOSE opcode (bits 15..10 = 000001, bits 9..5 = 11100 / 11001)."""
    result: set[int] = set()
    for address in range(0, len(image) - 4, 2):
        word = image[address] | (image[address + 1] << 8)
        if word >> 10 == 1 and (word >> 5) & 0x1F in (0x1C, 0x19):
            result.add(address)
    return result


def build_table(image: bytes, functions: list[tuple[int, str]], work: Path) -> SiteTable:
    imap = sweep_functions(image, functions, work)
    sites = build_sites(imap)
    by_access_pc: dict[int, Site] = {}
    for site in sites.values():
        if not site.registers:
            continue
        if site.access_pc in by_access_pc:
            raise RuntimeError(
                f"access-PC collision between {site.address:#x} and "
                f"{by_access_pc[site.access_pc].address:#x}"
            )
        by_access_pc[site.access_pc] = site
    installers = derive_installers(image, imap)
    entries = [entry for entry, _name in functions if entry < len(image)]
    return SiteTable(
        sites=sites, by_access_pc=by_access_pc, imap=imap, entries=entries,
        names={entry: name for entry, name in functions},
        installers=installers,
        installer_trace_pcs={
            cell: {row["trace_pc"] for row in info["writers"]}
            for cell, info in installers.items()
        },
        installer_instructions={
            cell: {row["instruction"] for row in info["writers"]}
            for cell, info in installers.items()
        },
        gadgets=find_gadgets(imap),
        entry_set=set(entries),
        prepare_like=prepare_like_addresses(image),
    )


# ------------------------------------------------------------------- oracle

@dataclass
class StepScan:
    step: int
    accesses: int = 0
    prepares: Counter = field(default_factory=Counter)
    disposes: Counter = field(default_factory=Counter)
    events: list[dict] = field(default_factory=list)
    anomalies: Counter = field(default_factory=Counter)
    samples: list[dict] = field(default_factory=list)
    hook_writes: list[dict] = field(default_factory=list)
    live_at_end: int = 0
    max_live: int = 0
    first_slots: dict[str, int] = field(default_factory=dict)
    first_values: dict[str, int] = field(default_factory=dict)
    missing: bool = False


def _event(step: int, kind: str, pc: int, access: dict, table: SiteTable, **extra) -> dict:
    start = table.instruction_start(pc)
    value = access["value"] & ((1 << (8 * access["width"])) - 1)
    return {
        "class": kind,
        "step": step,
        "pc": hx(start),
        "pc_note": None if start is not None else "instruction start not in the swept map",
        "trace_pc": hx(pc),
        "instruction": table.imap[start][1] if start is not None else None,
        "operation": access["operation"],
        "target": hx(access["address"]),
        "width": access["width"],
        "bytes": value.to_bytes(access["width"], "little").hex(),
        **extra,
    }


def scan_step(accesses: list[dict], step: int, table: SiteTable) -> StepScan:
    """Judge one traced step (one top-level call issued by the harness)."""
    scan = StepScan(step, accesses=len(accesses))
    live: dict[int, tuple[str, int, int]] = {}   # word -> (kind, prepare site, value)
    by_pc = table.by_access_pc
    hook_cells = frozenset(HOOK_CELLS)
    installer_pcs = table.installer_trace_pcs
    installer_instructions = table.installer_instructions
    tail_lo, tail_hi = EXECUTABLE_TAIL
    pocket_lo, pocket_hi = RWX_POCKET
    events, anomalies = scan.events, scan.anomalies
    samples, hook_writes = scan.samples, scan.hook_writes
    prepares, disposes = scan.prepares, scan.disposes
    writes: list[tuple[int, int, int]] = []    # every non-PREPARE store (pc, address, width)
    index, total = 0, len(accesses)
    while index < total:
        access = accesses[index]
        pc = access["pc"]
        site = by_pc.get(pc)
        if site is not None:
            count = len(site.registers)
            chunk = accesses[index:index + count]
            # PREPARE pushes r20 first (descending words, lp last); DISPOSE
            # pops lp first (ascending words, r20 last).
            step_word = -4 if site.kind == "prepare" else 4
            shaped = (len(chunk) == count
                      and all(c["pc"] == pc and c["width"] == 4 for c in chunk)
                      and all(c["operation"] == ("write" if site.kind == "prepare" else "read")
                              for c in chunk)
                      and all(chunk[j]["address"] == chunk[0]["address"] + step_word * j
                              for j in range(1, count)))
            if shaped:
                if site.kind == "prepare":
                    prepares[site.address] += 1
                    for position, push in enumerate(chunk):
                        register = site.registers[position]
                        kind = "lp" if register == 31 else "ep" if register == 30 else f"r{register}"
                        previous = live.get(push["address"])
                        if previous is not None:
                            events.append(_event(
                                step, "saved-return-reprepared" if previous[0] == "lp"
                                else "saved-register-reprepared", pc, push, table,
                                slot_kind=previous[0], slot_owner=hx(previous[1]),
                                new_slot_kind=kind, site=hx(site.address),
                                site_instruction=site.text))
                        scan.first_slots.setdefault(kind, push["address"])
                        scan.first_values.setdefault(kind, push["value"])
                        live[push["address"]] = (kind, site.address, push["value"])
                    scan.max_live = max(scan.max_live, len(live))
                else:
                    disposes[site.address] += 1
                    for pop in chunk:
                        slot = live.pop(pop["address"], None)
                        if slot is None:
                            anomalies["dispose-read-of-nonlive"] += 1
                            if len(samples) < SAMPLE_LIMIT:
                                samples.append({"class": "dispose-read-of-nonlive", "step": step,
                                                "pc": hx(site.address),
                                                "instruction": site.text,
                                                "target": hx(pop["address"])})
                        elif slot[0] == "lp" and pop["value"] != slot[2]:
                            anomalies["saved-return-restored-different"] += 1
                            if len(samples) < SAMPLE_LIMIT:
                                samples.append({"class": "saved-return-restored-different",
                                                "step": step, "pc": hx(site.address),
                                                "instruction": site.text,
                                                "target": hx(pop["address"]),
                                                "stored": hx(slot[2]), "read": hx(pop["value"])})
                index += count
                continue
            # The decoded site executed but the trace does not match its shape:
            # judge the whole run as ordinary accesses and record the anomaly.
            end = index
            while end < total and accesses[end]["pc"] == pc:
                end += 1
            shape = (f"{site.kind}-truncated-at-trace-end" if end == total
                     else f"{site.kind}-shape-mismatch")
            anomalies[shape] += 1
            if len(samples) < SAMPLE_LIMIT:
                samples.append({"class": shape, "step": step,
                                "pc": hx(site.address), "instruction": site.text,
                                "trace_pc": hx(pc), "run_length": end - index})
        else:
            end = index + 1
        while index < end:
            access = accesses[index]
            index += 1
            operation = access["operation"]
            address = access["address"]
            width = access["width"]
            write_number = None
            if operation == "write":
                write_number = len(writes)
                writes.append((pc, address, width))
            word = address & ~3
            last_word = (address + width - 1) & ~3
            while word <= last_word:
                slot = live.get(word)
                if slot is not None:
                    if operation == "write":
                        kind = "saved-return-write" if slot[0] == "lp" else "saved-register-write"
                    else:
                        kind = "saved-return-read" if slot[0] == "lp" else "saved-register-read"
                    events.append({**_event(step, kind, pc, access, table, slot_kind=slot[0],
                                            slot_owner=hx(slot[1]), slot_value=hx(slot[2])),
                                   "write": write_number})
                elif operation == "write" and word in hook_cells:
                    start = table.instruction_start(pc)
                    stock = (pc in installer_pcs.get(word, ())
                             or (start is not None and start in installer_instructions[word]))
                    record = {
                        "step": step, "pc": hx(start), "trace_pc": hx(pc),
                        "instruction": table.imap[start][1] if start is not None else None,
                        "target": hx(address), "width": width,
                        "bytes": (access["value"] & ((1 << (8 * width)) - 1))
                        .to_bytes(width, "little").hex(),
                        "slot_kind": None, "slot_owner": None, "slot_value": None,
                    }
                    if stock:
                        hook_writes.append({**record, "cell": hx(word), "value": hx(access["value"])})
                    else:
                        events.append({"class": "hook-cell-write", **record, "cell": hx(word),
                                       "write": write_number})
                word += 4
            if operation == "write":
                if address <= tail_hi and address + width > tail_lo:
                    kind = "executable-tail-write"
                elif address <= pocket_hi and address + width > pocket_lo:
                    kind = "rwx-pocket-write"
                else:
                    kind = None
                if kind is not None:
                    events.append({**_event(step, kind, pc, access, table, slot_kind=None,
                                            slot_owner=None, slot_value=None),
                                   "write": write_number})
    # For every flagged write, name the whole run of writes its instruction
    # issued in this step (a looping store is one writer, not many).
    for event in events:
        number = event.pop("write", None)
        if number is None:
            continue
        run_pc = writes[number][0]
        first = number
        while first > 0 and writes[first - 1][0] == run_pc:
            first -= 1
        last = number
        while last + 1 < len(writes) and writes[last + 1][0] == run_pc:
            last += 1
        run = writes[first:last + 1]
        event["writer_run"] = {
            "count": len(run), "first_target": hx(run[0][1]), "last_target": hx(run[-1][1]),
            "lowest_target": hx(min(target for _pc, target, _width in run)),
            "highest_target": hx(max(target + width - 1 for _pc, target, width in run)),
        }
    scan.live_at_end = len(live)
    if live:
        anomalies["live-slots-at-step-end"] += 1
        if len(samples) < SAMPLE_LIMIT:
            samples.append({
                "class": "live-slots-at-step-end", "step": step, "live_slots": len(live),
                "outermost": [f"{hx(address)} {kind} saved by {hx(owner)}"
                              for address, (kind, owner, _value) in sorted(live.items(),
                                                                           reverse=True)[:6]],
            })
    # Any executed 32-bit instruction whose opcode word is PREPARE/DISPOSE
    # must be a swept site: an access at pc belongs to an instruction at
    # pc-2 unless the swept map shows a 16-bit instruction at pc or a longer
    # one at pc-4/pc-6.
    imap = table.imap
    for executed in {access["pc"] for access in accesses}:
        start = executed - 2
        if start not in table.prepare_like or executed in by_pc:
            continue
        length = imap.get(start, (0, None))[0]
        if length == 4:
            kind = "swept-decode-conflict"
        elif (imap.get(executed, (0, None))[0] == 2
              or imap.get(executed - 4, (0, None))[0] == 6
              or imap.get(executed - 6, (0, None))[0] == 8):
            continue
        else:
            kind = "prepare-like-in-sweep-gap"
        anomalies[kind] += 1
        if len(samples) < SAMPLE_LIMIT:
            samples.append({"class": kind, "step": step, "pc": hx(start),
                            "trace_pc": hx(executed), "swept_length": length,
                            "instruction": imap.get(start, (0, None))[1]})
    return scan


def analyze_trace(path: Path, step: int, table: SiteTable) -> StepScan:
    if not path.is_file():
        scan = StepScan(step, missing=True)
        scan.anomalies["trace-missing"] += 1
        scan.samples.append({"class": "trace-missing", "step": step, "path": path.name})
        return scan
    truncated = path.stat().st_size > MAX_TRACE_BYTES
    if truncated:
        with path.open("r+b") as stream:
            stream.truncate(MAX_TRACE_BYTES)
    scan = scan_step(sc.parse_core_accesses(path), step, table)
    if truncated:
        scan.anomalies["trace-truncated"] += 1
        scan.samples.append({"class": "trace-truncated", "step": step, "path": path.name})
    return scan


# ------------------------------------------------------------------- runner

@dataclass
class Plan:
    commands: list[str]
    marker: str
    traces: dict[str, list[Path]]


@dataclass
class CaseRun:
    family: str
    key: str
    name: str
    detail: dict
    pcs: list[int]
    scans: list[StepScan]
    error: str | None
    state: str = ""       # memory/state model the case started from


class StatefulDriver:
    """Stateful-harness cases (DCM dispatcher matrix, seed cases, self-test)."""

    def __init__(self, family: str, cases: list[sc.Case], work: Path):
        self.family, self.cases, self.work = family, cases, work

    def items(self) -> list:
        return list(self.cases)

    def key(self, case: sc.Case) -> str:
        return case.case_id

    def steps(self, case: sc.Case) -> int:
        return len(case.steps)

    def name(self, case: sc.Case) -> str:
        return case.name

    def plan(self, group: list[sc.Case], _label: str, extra_prelude: tuple[str, ...]) -> Plan:
        marker = "SEQBATCH_" + hashlib.sha256(
            "".join(case.case_id for case in group).encode()
        ).hexdigest()[:16]
        commands, _initial, traces = sc.group_script(group, self.work, "core", marker)
        prelude = len(sc.lean_prelude())
        commands = commands[:prelude] + list(extra_prelude) + commands[prelude:]
        return Plan(commands, marker, traces)

    def pcs(self, output: str, group: list[sc.Case]) -> dict[str, list[int]]:
        observed = {case.case_id: [] for case in group}
        for match in sc.STEP_RE.finditer(output):
            if match.group(1) in observed:
                observed[match.group(1)].append(int(match.group(3)))
        return observed

    def detail(self, case: sc.Case) -> dict:
        return {"session": case.session, "security_bitmap": case.security_bitmap,
                "steps": [step.as_dict() for step in case.steps]}

    def state_of(self, _case: sc.Case) -> str:
        return "stock state (executed lifecycle base, session/security primes)"

    def cleanup(self, case: sc.Case, _label: str) -> None:
        sc.remove_case_inputs(case, self.work)
        (self.work / f"state-{case.case_id}-dump.bin").unlink(missing_ok=True)


class CantpDriver:
    """CanTp ingress corpus: raw frames through cantp_receive_can_frame."""

    family = "cantp-ingress"

    def __init__(self, trials: list[ci.Trial], work: Path):
        self.trials, self.work = trials, work

    def items(self) -> list[int]:
        return list(range(len(self.trials)))

    def key(self, index: int) -> str:
        return f"{index:06d}"

    def steps(self, _index: int) -> int:
        return 1

    def name(self, index: int) -> str:
        return f"{self.trials[index].family}-{index:06d}"

    def plan(self, group: list[int], _label: str, _extra: tuple[str, ...]) -> Plan:
        commands = sc.lean_prelude()
        traces: dict[str, list[Path]] = {}
        for index in group:
            trial = self.trials[index]
            image_name = f"img-{index:06d}.bin"
            (self.work / image_name).write_bytes(ci.trial_image(trial, 0))
            trace = self.work / f"trace-{index:06d}.txt"
            trace.unlink(missing_ok=True)
            traces[self.key(index)] = [trace]
            commands += [f"restore /out/{image_name} binary {ci.RAM_BASE:#x}",
                         f"sim trace-file /out/{trace.name}", "sim trace-core on"]
            for position, frame in enumerate(trial.frames):
                data = bytes.fromhex(frame.hex8())
                # Mirrors ci.trial_script minus the fence watchpoints.
                commands += [
                    (f"set {{unsigned int}}{ci.FRAME_BUF:#x}="
                     f"{int.from_bytes(data[0:4], 'little'):#x}"),
                    (f"set {{unsigned int}}{ci.FRAME_BUF + 4:#x}="
                     f"{int.from_bytes(data[4:8], 'little'):#x}"),
                    f"set $r3={ci.STACK_TOP:#x}", f"set $r31={ci.SENTINEL:#x}",
                    f"set $r5={ci.TP_BASE:#x}", f"set $tp={ci.TP_BASE:#x}",
                    f"set $r6={frame.canif_id:#x}", f"set $r7={ci.PDU_INFO:#x}",
                    f"set $pc={ci.ENTRY:#x}", "continue",
                ]
                following = (trial.frames[position + 1]
                             if position + 1 < len(trial.frames) else None)
                if following is not None and (following.data[0] & 0xF0) == 0x20:
                    grant = ci.cell_for(following.canif_id)
                    if grant is not None:
                        commands += [
                            f"set {{unsigned char}}{grant + 0x1A:#x}=0x5a",
                            f"set {{unsigned char}}{grant + 0x1E:#x}=0xf0",
                        ]
            commands += ["sim trace-core off", f'printf "TPR {index} %u\\n", $pc',
                         f"set $pc={ci.SENTINEL:#x}"]
        commands.append(f'printf "TP_END={group[-1]}\\n"')
        return Plan(commands, f"TP_END={group[-1]}", traces)

    def pcs(self, output: str, group: list[int]) -> dict[str, list[int]]:
        observed = {self.key(index): [] for index in group}
        for match in ci.RX_LINE.finditer(output):
            key = f"{int(match.group(1)):06d}"
            if key in observed:
                observed[key].append(int(match.group(2)))
        return observed

    def detail(self, index: int) -> dict:
        trial = self.trials[index]
        return {"frames": [[hex(f.canif_id), f.dlc, f.hex8()] for f in trial.frames],
                "rx_state": trial.rx_state.hex() if trial.rx_state else None,
                "tx_state": trial.tx_state.hex() if trial.tx_state else None}

    def state_of(self, _index: int) -> str:
        return "stock state (pattern fill, channel reset state, raw frames)"

    def cleanup(self, index: int, _label: str) -> None:
        for name in (f"img-{index:06d}.bin", f"trace-{index:06d}.txt"):
            (self.work / name).unlink(missing_ok=True)


class AbDriver:
    """SID 0xAB output-contract cases over the normalized LocalRAM snapshot."""

    def __init__(self, family: str, cases: list[ab.Case], base: bytes, poison: bytes,
                 work: Path):
        self.family, self.cases, self.base, self.poison, self.work = (
            family, cases, base, poison, work)

    def items(self) -> list[int]:
        return list(range(len(self.cases)))

    def key(self, index: int) -> str:
        return f"{index:06d}"

    def steps(self, _index: int) -> int:
        return 1

    def name(self, index: int) -> str:
        return f"{self.cases[index].family}:{self.cases[index].name}"

    def plan(self, group: list[int], label: str, _extra: tuple[str, ...]) -> Plan:
        commands = ab.prelude()
        traces: dict[str, list[Path]] = {}
        for index in group:
            case = self.cases[index]
            (self.work / f"img-{label}-{index:06d}.bin").write_bytes(
                ab.scenario_image(self.base, case, self.poison))
            trace = self.work / f"tr-{label}-{index:06d}.txt"
            trace.unlink(missing_ok=True)
            traces[self.key(index)] = [trace]
            commands += ab.case_script(index, case, label)
        commands.append(f'printf "TP_END={group[-1]}\\n"')
        return Plan(commands, f"TP_END={group[-1]}", traces)

    def pcs(self, output: str, group: list[int]) -> dict[str, list[int]]:
        observed = {self.key(index): [] for index in group}
        for match in ab.RX_LINE.finditer(output):
            key = f"{int(match.group(1)):06d}"
            if key in observed:
                observed[key].append(int(match.group(2)))
        return observed

    def detail(self, index: int) -> dict:
        case = self.cases[index]
        return {"ab_family": case.family, "request_hex": case.request.hex(),
                "session": case.session, "capacity": case.capacity, "note": case.note}

    def state_of(self, index: int) -> str:
        case = self.cases[index]
        if case.family in ab.SYNTHETIC_FAMILIES:
            return f"synthetic state, not request-reachable ({case.note})"
        if case.capacity != ab.STOCK_CAPACITY:
            return f"stock snapshot with sim-only capacity overlay ({case.note})"
        return "stock snapshot, stock capacity"

    def cleanup(self, index: int, label: str) -> None:
        for name in (f"img-{label}-{index:06d}.bin", f"tr-{label}-{index:06d}.txt",
                     f"tp-{label}-{index:06d}.bin"):
            (self.work / name).unlink(missing_ok=True)


def execute_group(driver, group: list, plan: Plan, elf: Path, out: Path, timeout: float,
                  label: str, table: SiteTable, failure: str | None = None) -> list[CaseRun]:
    log_path = out / f"{label}.txt"
    if failure is None:
        try:
            output = run_elf(
                root=REPO_ROOT, elf_path=elf, stop=f"{dcm.SENTINEL:#x}",
                memory_regions=dcm.SIM_MEMORY_REGIONS, gdb_commands=plan.commands,
                expected_output=[plan.marker], timeout=timeout, output_path=log_path,
            )
        except CodeFlashSimError:
            log_path.unlink(missing_ok=True)
            raise
    else:
        output = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    log_path.unlink(missing_ok=True)
    observed = driver.pcs(output, group)
    runs: list[CaseRun] = []
    for item in group:
        key = driver.key(item)
        pcs = observed.get(key, [])
        scans = [analyze_trace(path, index, table)
                 for index, path in enumerate(plan.traces[key])]
        error = None if len(pcs) == driver.steps(item) else (failure or "steps not observed")[-400:]
        runs.append(CaseRun(driver.family, key, driver.name(item), driver.detail(item),
                            pcs, scans, error, driver.state_of(item)))
        driver.cleanup(item, label)
    return runs


def run_group_bisect(driver, group: list, elf: Path, out: Path, timeout: float, label: str,
                     table: SiteTable, extra_prelude: tuple[str, ...] = ()) -> list[CaseRun]:
    plan = driver.plan(group, label, extra_prelude)
    try:
        return execute_group(driver, group, plan, elf, out, timeout, label, table)
    except CodeFlashSimError as error:
        if len(group) > 1:
            middle = len(group) // 2
            return (run_group_bisect(driver, group[:middle], elf, out, timeout, label + "a",
                                     table, extra_prelude)
                    + run_group_bisect(driver, group[middle:], elf, out, timeout, label + "b",
                                       table, extra_prelude))
        # A wedged singleton keeps the partial trace and log its own plan wrote.
        (out / f"{label}.txt").write_text(str(error), encoding="utf-8")
        return execute_group(driver, group, plan, elf, out, timeout, label, table,
                             failure=str(error))

def run_family(driver, elf: Path, out: Path, args, table: SiteTable,
               extra_prelude: tuple[str, ...] = ()) -> list[CaseRun]:
    if not driver.items():
        return []
    items = driver.items()
    groups = [items[offset:offset + args.batch_size]
              for offset in range(0, len(items), args.batch_size)]
    results: list[CaseRun] = []

    def worker(numbered: tuple[int, list]) -> list[CaseRun]:
        number, group = numbered
        return run_group_bisect(driver, group, elf, out, args.timeout,
                                f"{driver.family}-{number:04d}", table, extra_prelude)

    started = time.time()
    for done, (_number, runs) in enumerate(
            ci.parallel_results(list(enumerate(groups)), worker, args.jobs), start=1):
        results.extend(runs)
        if done % 10 == 0 or done == len(groups):
            violations = sum(len(scan.events) for run in results for scan in run.scans)
            print(f"[{driver.family}] batches {done}/{len(groups)} cases {len(results)} "
                  f"violations {violations} ({time.time() - started:.0f}s)", flush=True)
    return results


# ------------------------------------------------------------------- corpora

def dcm_request_bodies() -> list[tuple[str, bytes]]:
    """Request matrix driven through dcm_run_scheduled_request (0x922AA)."""
    bodies: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()

    def add(name: str, body: bytes) -> None:
        if body not in seen:
            seen.add(body)
            bodies.append((name, body))

    def fixed_width(value: int, width: int) -> bytes:
        if width == 0:
            return b""
        return (value & ((1 << (8 * width)) - 1)).to_bytes(width, "big")

    for sid in range(0x100):
        add(f"sid_{sid:02x}", bytes((sid, 0x03)) if sid in (0x10, 0x11) else bytes((sid,)))
    for sid in (0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x27, 0x2A, 0x2C, 0x2E,
                0x31, 0x37, 0x3D, 0x3E, 0x85, 0x86, 0x87):
        for sub in (0x00, 0x01, 0x02, 0x03, 0x7F, 0x80, 0xFF):
            add(f"sub_{sid:02x}_{sub:02x}", bytes((sid, sub, 0xA5)))
    for did in dcm.WDBI_DIDS:
        for payload in (0, 1, 3, 8, 0xFD):
            add(f"wdbi_{did:04x}_n{payload}",
                bytes((0x2E, did >> 8, did & 0xFF)) + b"\x5A" * payload)
    for rid in dcm.ROUTINE_RIDS:
        for control in (0x00, 0x01, 0x02, 0x03, 0x81, 0xFF):
            for extra in (0, 1, 2, 3, 0x41):
                add(f"rid_{rid:04x}_c{control:02x}_n{extra}",
                    bytes((0x31, control, rid >> 8, rid & 0xFF)) + b"\xA5" * extra)
    publication, classes = dcm.read_did_tables()
    for did in publication:
        add(f"rdbi_{did:04x}", bytes((0x22, did >> 8, did & 0xFF)))
    for _length_callback, first, last in classes:
        for did in {(first - 1) & 0xFFFF, first, first + 1, (first + last) // 2,
                    last - 1, last, (last + 1) & 0xFFFF}:
            add(f"rdbi_class_{did:04x}", bytes((0x22, did >> 8, did & 0xFF)))
    for length, name in ((1, "short"), (2, "one"), (3, "odd"), (4, "two"),
                         (5, "two_pad"), (0, "empty")):
        add(f"rdbi_len_{name}", b"\x0f\x01\x0f\x01\xa5"[:length])
    for addr_size in range(16):
        for size_size in range(16):
            valid = addr_size == 5 and size_size == 1
            address = (bytes((1,)) + fixed_width(dcm.RMEM_SOURCE if valid else 0, 4)
                       if addr_size == 5 else fixed_width(0, addr_size))
            add(f"rmem_fmt_{addr_size}_{size_size}",
                bytes(((size_size << 4) | addr_size,)) + address
                + fixed_width(1 if size_size else 0, size_size))
    for memory_id, address, size in (
        (1, dcm.RMEM_SOURCE, 0), (1, dcm.RMEM_SOURCE, 1), (1, dcm.RMEM_SOURCE, 0xFF),
        (1, 0xFEBE37FF, 1), (1, 0xFEBE3800, 1), (1, 0xFEBE503B, 1), (1, 0xFEBE503C, 1),
        (1, 0xFEBE52A7, 1), (1, 0xFEBE52A8, 1), (1, 0xFEBFFFFF, 1), (1, 0xFEBFFFFF, 2),
        (1, 0xFEC00000, 1), (1, 0xFFFFFFFF, 2), (0, dcm.RMEM_SOURCE, 1),
        (2, 0xFF200000, 1), (0xFF, dcm.RMEM_SOURCE, 1),
    ):
        add(f"rmem_m{memory_id:02x}_a{address:08x}_s{size}",
            bytes((0x15, memory_id)) + address.to_bytes(4, "big") + bytes((size,)))
    for selector, operation in (
        (0xF1, b"JTEKM"), (0xF3, b"TMPCL"), (0xF4, b"JTRM1"), (0xF5, b"JTRM2"),
        (0xF6, b"BADIS"), (0xF7, b"BAENA"), (0xF8, b"TZCLR"), (0xF9, b"JTRM3"),
        (0xFA, b"\x40VSPD"), (0xFB, b"ASINC"), (0x00, b""),
    ):
        add(f"ba_{selector:02x}", bytes((0xBA, selector)) + operation)
    for sub, body in ((0x01, b""), (0x02, b"\x20\x6d"), (0x03, b"\x20\x6d\x00\x00"),
                      (0x81, b""), (0x82, b"\x20\x6d"), (0x83, b"\x20\x6d"),
                      (0x00, b""), (0x04, b"\x20\x6d"), (0x7F, b""), (0xFF, b"")):
        add(f"ab_{sub:02x}", bytes((0xAB, sub)) + body)
    for sub in (0x00, 0x01, 0x02, 0x03, 0x80, 0x81, 0x82, 0x83):
        add(f"session_{sub:02x}", bytes((0x10, sub)))
    for sub in (0x01, 0x02, 0x03, 0x11, 0x81):
        add(f"reset_{sub:02x}", bytes((0x11, sub)))
    for sub in (0x00, 0x01, 0x02, 0x03):
        add(f"clear_dtc_{sub:02x}", bytes((0x14, sub)) + b"\xFF\xFF\xFF")
    for sub, tail in ((0x01, b"\xff"), (0x02, b"\xff"), (0x02, b"\x00"), (0x03, b""),
                      (0x04, b"\x00\x00\x00\xff"), (0x06, b"\xff"), (0x0A, b"\xff"),
                      (0x0F, b"\xff"), (0x12, b"\xff"), (0x13, b"\xff")):
        add(f"dtc_{sub:02x}_{tail.hex() or 'none'}", bytes((0x19, sub)) + tail)
    for sub in (0x00, 0x01, 0x02, 0x03, 0x80, 0x81):
        add(f"security_{sub:02x}", bytes((0x27, sub)))
    for sub in (0x00, 0x01, 0x02, 0x03, 0x80, 0x81):
        add(f"comm_{sub:02x}", bytes((0x28, sub, 0x01)))
    for sub in (0x00, 0x01, 0x02, 0x03, 0x80, 0x81):
        add(f"read_dtc_{sub:02x}", bytes((0x2A, sub)))
    for size in (0x00, 0x01, 0x10, 0xFF):
        add(f"rmba_s{size:02x}", bytes((0x23, 0x15, 0x01)) + b"\xfe\xbe\x70\x00" + bytes((size,)))
    for sub in (0x00, 0x01, 0x80, 0x81):
        add(f"tester_present_{sub:02x}", bytes((0x3E, sub)))
    for sub in (0x00, 0x01, 0x02, 0x03, 0x80, 0x81):
        add(f"control_dtc_{sub:02x}", bytes((0x85, sub)))
    for sub in (0x00, 0x01, 0x02, 0x03):
        add(f"response_{sub:02x}", bytes((0x2C, sub)))
    for sub in (0x00, 0x01, 0x02, 0x03):
        add(f"io_ctrl_{sub:02x}", bytes((0x2F, sub)))
    for sub in (0x00, 0x01, 0x02, 0x03, 0x80, 0x81):
        add(f"download_{sub:02x}", bytes((0x34, sub)) + b"\x00\x00")
    for sub in (0x00, 0x01, 0x02, 0x03):
        add(f"wdbi_2012_{sub:02x}", bytes((0x2E, 0x20, 0x12)) + bytes((sub,)))
    for did in (0xF190, 0xF181, 0xF18C, 0xF122, 0xF1A2):
        add(f"rdbi_extra_{did:04x}", bytes((0x22, did >> 8, did & 0xFF)))
    for rid in dcm.ROUTINE_RIDS:
        add(f"rid_result_{rid:04x}", bytes((0x31, 0x03, rid >> 8, rid & 0xFF)))
    for rid in dcm.ROUTINE_RIDS:
        add(f"rid_stop_{rid:04x}", bytes((0x31, 0x02, rid >> 8, rid & 0xFF)))
    add("segmented_rdbi", b"\x22\x20\x30\xf1\x81\xf1\x8c\x10\x37")
    add("empty", b"")
    return bodies


def dcm_matrix_cases() -> list[sc.Case]:
    bodies = dcm_request_bodies()
    cases: list[sc.Case] = []
    for session in SESSIONS:
        for bitmap in BITMAPS:
            for name, body in bodies:
                cases.append(sc.make_case(
                    f"s{session}_b{bitmap:08x}_{name}", [sc.request(body)], session, bitmap,
                ))
    for slot in (1, 2):
        for sid in range(0x100):
            body = bytes((sid, 0x03)) if sid in (0x10, 0x11) else bytes((sid,))
            cases.append(sc.make_case(f"slot{slot}_sid_{sid:02x}", [sc.request(body, slot)], 1, 0))
    return list({case.case_id: case for case in cases}.values())


# --------------------------------------------------------------- aggregation

def value_class(value: str) -> str:
    """zero / codeflash / other, for values a stock installer wrote."""
    number = int(value, 16)
    if number == 0:
        return "zero"
    return "codeflash" if number < CODE_FLASH_END else "other"


def is_stock_state(case_state: str) -> bool:
    """False only for primed synthetic state or a sim-only capacity overlay."""
    return not case_state.startswith(("synthetic", "stock snapshot with sim-only"))


def merge_runs(runs: list[CaseRun]) -> dict:
    """Fold case runs into family-level counters and lists."""
    prepares: Counter = Counter()
    disposes: Counter = Counter()
    anomalies: Counter = Counter()
    events: list[dict] = []
    samples: list[dict] = []
    hook_stock: Counter = Counter()
    hook_values: dict[tuple[int, int], Counter] = {}
    hook_other: list[dict] = []
    abnormal: list[dict] = []
    incomplete: list[dict] = []
    steps = accesses = live_at_end = max_live = 0
    for run in runs:
        if run.error:
            incomplete.append({"case": run.name, "case_id": run.key, "error": run.error})
        for step_index, pc in enumerate(run.pcs):
            if pc != dcm.SENTINEL:
                abnormal.append({"case": run.name, "case_id": run.key, "step": step_index,
                                 "stop_pc": hx(pc)})
        for scan in run.scans:
            steps += 1
            accesses += scan.accesses
            prepares.update(scan.prepares)
            disposes.update(scan.disposes)
            anomalies.update(scan.anomalies)
            live_at_end += scan.live_at_end
            max_live = max(max_live, scan.max_live)
            context = {"case": run.name, "case_id": run.key, "detail": run.detail,
                       "case_state": run.state}
            events.extend({**event, **context} for event in scan.events)
            samples.extend({**sample, "case": run.name, "case_id": run.key}
                           for sample in scan.samples)
            for record in scan.hook_writes:
                key = (int(record["cell"], 16), int(record["pc"], 16) if record["pc"] else -1)
                value = int(record["value"], 16)
                hook_stock[key] += 1
                hook_values.setdefault(key, Counter())[record["value"]] += 1
                # Stock installers write zero or a CodeFlash address as a word.
                if value and not (record["width"] == 4 and value < CODE_FLASH_END):
                    hook_other.append({"case": run.name, "case_id": run.key,
                                       "step": record["step"], "cell": record["cell"],
                                       "pc": record["pc"], "value": record["value"],
                                       "width": record["width"]})
    return {
        "cases": len(runs), "steps": steps, "accesses": accesses,
        "prepares": prepares, "disposes": disposes, "anomalies": anomalies,
        "events": events, "samples": samples, "hook_stock": hook_stock,
        "hook_values": hook_values, "hook_other": hook_other,
        "abnormal": abnormal, "incomplete": incomplete,
        "live_at_end": live_at_end, "max_live": max_live,
    }


def family_report(family: str, merged: dict, table: SiteTable) -> dict:
    prepares = merged["prepares"]
    entries = sorted(site for site in prepares if site in table.entry_set)
    events = merged["events"]
    return {
        "family": family,
        "cases_traced": merged["cases"],
        "steps_traced": merged["steps"],
        "trace_accesses": merged["accesses"],
        "prepare_sites_executed": len(prepares),
        "prepare_executions": sum(prepares.values()),
        "dispose_sites_executed": len(merged["disposes"]),
        "functions_with_prepare_executed": len(entries),
        "prepare_sites_executed_list": [
            {"site": hx(site), "executions": count,
             "function": table.function_of(site)[1],
             "at_function_entry": site in table.entry_set,
             "instruction": table.sites[site].text}
            for site, count in sorted(prepares.items())
        ],
        "live_slot_violations": sum(event["class"].startswith("saved-") for event in events),
        "hook_cell_violations": sum(event["class"] == "hook-cell-write" for event in events),
        "tail_writes": sum(event["class"] == "executable-tail-write" for event in events),
        "rwx_pocket_writes": sum(event["class"] == "rwx-pocket-write" for event in events),
        "violations": len(events),
        "violations_by_class": dict(Counter(event["class"] for event in events)),
        "violations_stock_state": sum(is_stock_state(event["case_state"]) for event in events),
        "violations_synthetic_or_overlay_state": sum(
            not is_stock_state(event["case_state"]) for event in events),
        "violations_list": [{**event, "family": family} for event in events],
        "abnormal_terminations": len(merged["abnormal"]),
        "abnormal_terminations_list": merged["abnormal"],
        "incomplete_cases": len(merged["incomplete"]),
        "incomplete_cases_list": merged["incomplete"],
        "anomalies_by_class": dict(merged["anomalies"]),
        "anomaly_samples": merged["samples"],
        "live_slots_at_step_end": merged["live_at_end"],
        "max_live_slots": merged["max_live"],
        "hook_cell_stock_writes": sum(merged["hook_stock"].values()),
        "hook_cell_stock_writes_by_installer": [
            {"cell": hx(cell), "pc": hx(pc) if pc >= 0 else None, "writes": count,
             "instruction": table.imap.get(pc, (0, None))[1] if pc >= 0 else None,
             "values": [[value, n, value_class(value)] for value, n in
                        merged["hook_values"][(cell, pc)].most_common(8)]}
            for (cell, pc), count in sorted(merged["hook_stock"].items())
        ],
        "hook_installer_values_outside_codeflash": merged["hook_other"],
    }


def union_coverage(reports: list[dict]) -> dict:
    sites: set[int] = set()
    entries: set[int] = set()
    for report in reports:
        for row in report["prepare_sites_executed_list"]:
            address = int(row["site"], 16)
            sites.add(address)
            if row["at_function_entry"]:
                entries.add(address)
    return {"prepare_sites_executed": len(sites), "functions_with_prepare_executed": len(entries)}


# ---------------------------------------------------------------- self-test

@dataclass(frozen=True)
class Seed:
    name: str
    gadget: int                    # foreign instruction the script executes
    saved: tuple[str, ...]         # registers restored after the gadget rounds
    rounds: tuple[tuple[tuple[str, int], ...], ...]   # assignments before each execution
    expected: str
    target: int
    check_bytes: bool


class SeededStatefulDriver(StatefulDriver):
    """Stateful driver whose single case executes foreign gadget rounds.

    A plain breakpoint after the dispatcher's PREPARE returns control to the
    script (GDB ignores everything that follows a resume command inside a
    breakpoint's command list).  Each round sets the gadget's registers and
    continues onto a temporary breakpoint past the gadget; afterwards the
    script restores the registers, deletes the breakpoint and resumes.
    """

    def __init__(self, cases: list[sc.Case], work: Path, seed: Seed,
                 breakpoint: int, breakpoint_number: int):
        super().__init__("selftest", cases, work)
        self.seed, self.breakpoint, self.breakpoint_number = seed, breakpoint, breakpoint_number

    def plan(self, group: list[sc.Case], _label: str, _extra: tuple[str, ...]) -> Plan:
        case = group[0]
        if len(group) != 1 or len(case.steps) != 1:
            raise ValueError("a seeded run drives exactly one single-step case")
        seed = self.seed
        marker = "SEQBATCH_selftest"
        (self.work / f"state-{case.case_id}-initial.bin").write_bytes(sc.base_image(case))
        trace = self.work / sc.trace_name(case, "core", 0)
        trace.unlink(missing_ok=True)
        step_commands = sc.request_commands(case, 0, case.steps[0], self.work, True)
        if step_commands[-2] != "continue" or not step_commands[-1].startswith("printf"):
            raise RuntimeError("stateful request commands changed shape")
        commands = sc.lean_prelude() + [
            f"restore /out/state-{case.case_id}-initial.bin binary {dcm.RAM_BASE:#x}",
            f"sim trace-file /out/{trace.name}", "sim trace-core on",
            f"break *{self.breakpoint:#x}",
        ]
        commands += step_commands[:-2] + ["continue"]        # stops at the breakpoint
        commands += [f"set $seed_{index} = {register}"
                     for index, register in enumerate(seed.saved)]
        for assignments in seed.rounds:
            commands += [f"set {target} = {value:#x}" for target, value in assignments]
            commands += [f"set $pc={seed.gadget:#x}", f"tbreak *{seed.gadget + 4:#x}",
                         "continue"]
        commands += [f"set {register} = $seed_{index}"
                     for index, register in enumerate(seed.saved)]
        commands += [f"delete {self.breakpoint_number}", f"set $pc={self.breakpoint:#x}",
                     "continue"]
        commands += step_commands[-1:] + [
            "sim trace-core off", f"set $pc={dcm.SENTINEL:#x}", f'printf "{marker}\\n"',
        ]
        return Plan(commands, marker, {case.case_id: [trace]})


def self_test(elf: Path, out: Path, args, table: SiteTable, work: Path) -> dict:
    """Seeded faults must fire; the unmodified baseline must be clean."""
    site = table.sites.get(sc.dcm.DISPATCH_TASK)
    if site is None or site.kind != "prepare":
        raise RuntimeError("dcm_run_scheduled_request does not begin with prepare")
    breakpoint = sc.dcm.DISPATCH_TASK + site.length
    number = 1 + sum(command.startswith("break ") for command in sc.lean_prelude())
    store, load = table.gadgets["store"], table.gadgets["load"]
    case = sc.make_case("selftest_rdbi_2030", [sc.request(b"\x22\x20\x30")], 1, 0)
    baseline = run_group_bisect(StatefulDriver("selftest", [case], work), [case], elf, out,
                                args.timeout, "selftest-baseline", table)[0]
    scan = baseline.scans[0]
    lp_slot = scan.first_slots.get("lp")
    callee_kind, callee_slot = next(
        ((kind, address) for kind, address in scan.first_slots.items() if kind != "lp"),
        (None, None))
    lp_value = scan.first_values.get("lp")
    callee_value = scan.first_values.get(callee_kind) if callee_kind else None
    baseline_ok = (not baseline.error and baseline.pcs == [dcm.SENTINEL]
                   and not scan.events and not scan.anomalies and lp_slot is not None
                   and callee_slot is not None and lp_value is not None
                   and callee_value is not None and sum(scan.prepares.values()) > 0)
    result = {
        "passed": False,
        "breakpoint": hx(breakpoint),
        "store_gadget": hx(store), "store_gadget_instruction": table.imap[store][1],
        "load_gadget": hx(load), "load_gadget_instruction": table.imap[load][1],
        "baseline": {
            "clean": baseline_ok, "step_pc": [hx(pc) for pc in baseline.pcs],
            "violations": len(scan.events), "anomalies": dict(scan.anomalies),
            "prepare_executions": sum(scan.prepares.values()),
            "dispatcher_saved_return_slot": hx(lp_slot),
            "dispatcher_callee_saved_slot": hx(callee_slot),
        },
        "seeds": [],
    }
    if not baseline_ok:
        print(f"[selftest] baseline not clean: pc={[hx(pc) for pc in baseline.pcs]} "
              f"events={len(scan.events)} anomalies={dict(scan.anomalies)}", flush=True)
        return result
    store_saved = ("$r8", "$r10")
    # The two saved-slot seeds write the seed value and then write the stock
    # value back: the foreign store is transient (overwritten before its
    # DISPOSE reads it) and the step still returns to the sentinel.
    seeds = (
        Seed("saved-return-write", store, store_saved,
             ((("$r8", lp_slot), ("$r10", SEED_VALUE)),
              (("$r8", lp_slot), ("$r10", lp_value))),
             "saved-return-write", lp_slot, True),
        Seed("saved-register-write", store, store_saved,
             ((("$r8", callee_slot), ("$r10", SEED_VALUE)),
              (("$r8", callee_slot), ("$r10", callee_value))),
             "saved-register-write", callee_slot, True),
        Seed("saved-return-read", load, ("$r1",), ((("$r1", lp_slot),),),
             "saved-return-read", lp_slot, False),
        Seed("hook-cell-write", store, store_saved,
             ((("$r8", 0xFEBF117C), ("$r10", SEED_VALUE)),),
             "hook-cell-write", 0xFEBF117C, True),
        Seed("executable-tail-write", store, store_saved,
             ((("$r8", 0xFEBFFA00), ("$r10", SEED_VALUE)),),
             "executable-tail-write", 0xFEBFFA00, True),
        Seed("rwx-pocket-write", store, store_saved,
             ((("$r8", 0xFEBF8000), ("$r10", SEED_VALUE)),),
             "rwx-pocket-write", 0xFEBF8000, True),
    )
    seed_bytes = SEED_VALUE.to_bytes(4, "little").hex()
    for seed in seeds:
        driver = SeededStatefulDriver([case], work, seed, breakpoint, number)
        run = run_group_bisect(driver, [case], elf, out, args.timeout,
                               f"selftest-{seed.name}", table)[0]
        scan = run.scans[0]
        hits = [event for event in scan.events
                if event["class"] == seed.expected and event["pc"] == hx(seed.gadget)
                and event["target"] == hx(seed.target)]
        seeded = [event for event in hits
                  if not seed.check_bytes or event["bytes"] == seed_bytes]
        classes = sorted({event["class"] for event in scan.events})
        ok = (bool(seeded) and classes == [seed.expected] and not run.error
              and run.pcs == [dcm.SENTINEL])
        result["seeds"].append({
            "seed": seed.name, "expected_class": seed.expected, "flagged": ok,
            "event_classes": classes, "hits": len(hits),
            "writer_pc": seeded[0]["pc"] if seeded else None,
            "target": seeded[0]["target"] if seeded else None,
            "bytes": seeded[0]["bytes"] if seeded else None,
            "step_pc": [hx(pc) for pc in run.pcs],
            "anomalies": dict(scan.anomalies),
        })
        print(f"[selftest] {seed.name}: {'flagged' if ok else 'MISSED'} {classes} "
              f"stop={[hx(pc) for pc in run.pcs]}", flush=True)
    result["passed"] = all(seed["flagged"] for seed in result["seeds"])
    return result


# ------------------------------------------------------------------- report

def render_report(state: dict) -> str:
    lines: list[str] = []
    add = lines.append
    target = state["target"]
    add("# Control-slot oracle report — camry-8965F3307000")
    add("")
    add(f"- Image: `{target['image']}` SHA-256 `{target['sha256']}`")
    add(f"- Schema: `{SCHEMA}`; application context GP=0xFEBEB800 TP=0x23DFC "
        f"SP=0xFEBE2000; exact-image GNU sim, sim-only PMR thunk patches and DCRA1 model "
        f"as in the reused harnesses.")
    add(f"- Generated: {state['generated']}; mode: {state['mode']}")
    add("")
    total = state["totals"]
    add("## 1. Headline")
    add("")
    add(f"- Cases traced: **{total['cases_traced']}** ({total['steps_traced']} steps, "
        f"{total['trace_accesses']} traced accesses).")
    add(f"- Distinct functions that executed a PREPARE (union over families): "
        f"**{total['functions_with_prepare_executed']}**; distinct PREPARE sites executed: "
        f"**{total['prepare_sites_executed']}** of {state['instruction_sets']['prepare_sites']} "
        f"decoded in the image.")
    add(f"- Violations found: **{total['violations']}** "
        f"(live-slot {total['live_slot_violations']}, hook-cell {total['hook_cell_violations']}, "
        f"executable-tail {total['tail_writes']}, RWX-pocket {total['rwx_pocket_writes']}).")
    add(f"- Abnormal terminations: {total['abnormal_terminations']}; incomplete cases: "
        f"{total['incomplete_cases']}.")
    add(f"- Self-validation: {'passed' if state['self_test']['passed'] else 'FAILED'}")
    add("")
    test = state["self_test"]
    add("## 2. Self-validation (mandatory before any clean result)")
    add("")
    base = test["baseline"]
    add(f"Self-test case: `22 20 30` through `dcm_run_scheduled_request @ 0x922AA`, session 1, "
        f"security bitmap 0, over the executed lifecycle base. A plain breakpoint at "
        f"{test['breakpoint']} (the instruction after the dispatcher's PREPARE) returns control "
        f"to the GDB script, which points the PC at one foreign gadget instruction and resumes "
        f"onto a temporary breakpoint past it; the registers are then restored and the step "
        f"resumes at the breakpointed instruction. Store gadget `{test['store_gadget']}` "
        f"`{test['store_gadget_instruction']}`, load gadget `{test['load_gadget']}` "
        f"`{test['load_gadget_instruction']}`. The dispatcher's live slots at the breakpoint: "
        f"saved return address {base['dispatcher_saved_return_slot']}, callee-saved "
        f"{base['dispatcher_callee_saved_slot']}. The two saved-slot seeds write `a5a5a5a5` "
        f"and then write the stock value back, so the foreign store is transient (overwritten "
        f"before its DISPOSE reads it) and every seeded step still returns to the sentinel.")
    add("")
    add("| seed | expected class | flagged | event classes | flagged events | writer PC | target "
        "| bytes | stop PC |")
    add("|---|---|---|---|---:|---|---|---|---|")
    add(f"| unmodified baseline | (none) | {'clean' if base['clean'] else 'NOT CLEAN'} | — | 0 | — | "
        f"saved-return slot {base['dispatcher_saved_return_slot']} | — | "
        f"{', '.join(base['step_pc'])} |")
    for seed in test["seeds"]:
        add(f"| {seed['seed']} | {seed['expected_class']} | {'yes' if seed['flagged'] else '**NO**'}"
            f" | {', '.join(seed['event_classes'])} | {seed['hits']} | {seed['writer_pc']} | "
            f"{seed['target']} | {seed['bytes'] or '—'} | {', '.join(seed['step_pc'])} |")
    add("")
    sets = state["instruction_sets"]
    add("## 3. Instruction sets derived from the image")
    add("")
    add(f"- One offline objdump run sweeps every function extent "
        f"({sets['functions']} functions from `build/out/pseudocode/index.tsv`) from its own "
        f"entry; extents are padded with NOPs so each sweep re-synchronizes.")
    add(f"- PREPARE sites: **{sets['prepare_sites']}** ({sets['prepare_at_function_entry']} at "
        f"function entries; {sets['prepare_long_forms']} long forms); DISPOSE sites: "
        f"**{sets['dispose_sites']}**; instructions decoded: {sets['instructions']}.")
    add("- Shape rule at run time: a PREPARE must issue exactly its register count of "
        "consecutive descending word stores, a DISPOSE the same number of ascending word loads; "
        "mismatches are reported as anomalies below.")
    add("")
    add("## 4. Per-family results")
    add("")
    add("| family | cases traced | steps | PREPARE sites executed | functions with PREPARE executed "
        "| live-slot violations | hook-cell violations | tail writes | RWX-pocket writes | of "
        "which in synthetic/overlay state | abnormal terminations | incomplete |")
    add("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for report in state["families"]:
        add(f"| {report['family']} | {report['cases_traced']} | {report['steps_traced']} | "
            f"{report['prepare_sites_executed']} | {report['functions_with_prepare_executed']} | "
            f"{report['live_slot_violations']} | {report['hook_cell_violations']} | "
            f"{report['tail_writes']} | {report['rwx_pocket_writes']} | "
            f"{report['violations_synthetic_or_overlay_state']} | "
            f"{report['abnormal_terminations']} | {report['incomplete_cases']} |")
    add("")
    add("Cases whose start state is synthetic or sim-only overlaid are still judged by the "
        "same rules; their violations are counted separately because that state is not "
        "request-reachable (SID 0xAB serializer pending state) or not stock (capacity overlay).")
    add("")
    add("## 5. Violations")
    add("")
    violations = [event for report in state["families"] for event in report["violations_list"]]
    if not violations:
        add("None. No traced step wrote or read a live saved slot outside its owning "
            "PREPARE/DISPOSE, wrote a hook cell from a non-installer PC, or wrote into the "
            "executable tail or RWX pocket.")
    else:
        add("Every violation names the case, the PC that wrote or read, the target and the "
            "bytes. `writer run` is the whole run of stores the same instruction issued in that "
            "step (count, first..last store, lowest..highest byte). The complete per-access list "
            "is in `results.json` under `families[].violations_list`.")
        add("")
        add("| family | case | case state | class | step | PC | instruction | target | bytes | "
            "slot / cell | writer run |")
        add("|---|---|---|---|---:|---|---|---|---|---|---|")
        for event in violations:
            run = event.get("writer_run")
            run_text = (
                f"{run['count']} stores {run['first_target']}..{run['last_target']} "
                f"(bytes {run['lowest_target']}..{run['highest_target']})" if run else "—")
            add(f"| {event['family']} | `{event['case']}` | {event.get('case_state', '')} | "
                f"{event['class']} | {event['step']} | {event['pc']} | `{event['instruction']}` | "
                f"{event['target']} | {event['bytes']} | "
                f"{event.get('slot_kind') or event.get('cell') or ''} | {run_text} |")
        add("")
        add("By family and case state:")
        add("")
        add("| family | case state | cases with violations | violations by class |")
        add("|---|---|---:|---|")
        states: dict[tuple[str, str], dict] = {}
        for event in violations:
            row = states.setdefault((event["family"], event.get("case_state", "")),
                                     {"cases": set(), "classes": Counter()})
            row["cases"].add(event["case"])
            row["classes"][event["class"]] += 1
        for (family, case_state), row in sorted(states.items()):
            names = ", ".join(f"`{name}`" for name in sorted(row["cases"])[:12])
            more = "" if len(row["cases"]) <= 12 else f" (+{len(row['cases']) - 12} more)"
            add(f"| {family} | {case_state} | {len(row['cases'])}: {names}{more} | "
                f"{dict(row['classes'])} |")
    add("")
    add("## 6. Oracle-integrity anomalies")
    add("")
    rows = [(report["family"], cls, count) for report in state["families"]
            for cls, count in sorted(report["anomalies_by_class"].items())]
    if not rows:
        add("None.")
    else:
        add("| family | anomaly | count |")
        add("|---|---|---:|")
        for family, cls, count in rows:
            add(f"| {family} | {cls} | {count} |")
        add("")
        add("Samples:")
        add("")
        for report in state["families"]:
            for sample in report["anomaly_samples"][:8]:
                add(f"- `{report['family']}` `{sample['case']}` {sample['class']}: "
                    + ", ".join(f"{key}={value}" for key, value in sample.items()
                                if key not in ("class", "case", "case_id")))
    add("")
    add("## 7. Hook cells: derived installers and observed stock writes")
    add("")
    add("Installer PCs are the decoded writers of each cell (`tools/pseudo --data-ref`); "
        "any other writer is a violation. Value classes cover the eight most common values per "
        "installer and family: `zero`, `codeflash` (a word holding a CodeFlash address) or "
        "`other`.")
    add("")
    add(f"- Stock installer writes observed: **{total['stock_hook_writes']}**; of those, "
        f"neither zero nor a CodeFlash word address: "
        f"**{total['hook_installer_values_outside_codeflash']}**.")
    add("")
    add("| cell | derived stock installers | observed stock writes (PC: count (value classes, "
        "distinct values)) | foreign writes |")
    add("|---|---|---|---:|")
    observed: dict[str, dict] = {}
    for report in state["families"]:
        for row in report["hook_cell_stock_writes_by_installer"]:
            cell = observed.setdefault(row["cell"], {})
            entry = cell.setdefault(row["pc"], {"writes": 0, "classes": set(), "values": set()})
            entry["writes"] += row["writes"]
            for value, _count, klass in row["values"]:
                entry["classes"].add(klass)
                entry["values"].add(value)
    foreign = Counter(event.get("cell") for report in state["families"]
                      for event in report["violations_list"]
                      if event["class"] == "hook-cell-write")
    for cell, info in state["installers"].items():
        writers = ", ".join(f"`{writer['instruction']}` ({writer['name']})"
                            for writer in info["writers"]) or "none (no decoded writer)"
        rows = observed.get(cell, {})
        seen = "; ".join(
            f"{pc}: {entry['writes']} ({'/'.join(sorted(entry['classes']))}, "
            f"{len(entry['values'])} distinct)" for pc, entry in sorted(rows.items())
        ) or "never written"
        add(f"| {cell} | {writers} | {seen} | {foreign.get(cell, 0)} |")
    add("")
    add("## 8. Method and limits")
    add("")
    for note in state["notes"]:
        add(f"- {note}")
    add("")
    return "\n".join(lines)


def write_outputs(out: Path, state: dict) -> None:
    (out / "results.json").write_text(json.dumps(state, indent=2, sort_keys=True) + "\n",
                                      encoding="utf-8")
    (out / "oracle-report.md").write_text(render_report(state), encoding="utf-8")


# --------------------------------------------------------------------- main

def instruction_set_summary(table: SiteTable, functions: list[tuple[int, str]]) -> dict:
    prepares = [site for site in table.sites.values() if site.kind == "prepare"]
    disposes = [site for site in table.sites.values() if site.kind == "dispose"]
    return {
        "functions": len(table.entries),
        "functions_in_index": len(functions),
        "instructions": len(table.imap),
        "prepare_sites": len(prepares),
        "prepare_at_function_entry": sum(site.address in table.entry_set for site in prepares),
        "prepare_long_forms": sum(site.length > 4 for site in prepares),
        "dispose_sites": len(disposes),
        "extent_cap": hx(EXTENT_CAP),
    }


def installer_json(table: SiteTable) -> dict:
    """Hook-cell allow-list as derived from the image, for the results file."""
    result: dict[str, dict] = {}
    for cell, info in table.installers.items():
        result[hx(cell)] = {
            "writers": [
                {"instruction": hx(row["instruction"]), "function": hx(row["function"]),
                 "name": row["name"], "length": row["length"], "trace_pc": hx(row["trace_pc"])}
                for row in info["writers"]
            ],
            "readers": [
                {"instruction": hx(row["instruction"]), "function": hx(row["function"]),
                 "name": row["name"]}
                for row in info["readers"]
            ],
        }
    return result


def cleanup(out: Path, work: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("*.txt"):
        stale.unlink()
    work.mkdir(parents=True, exist_ok=True)
    for pattern in ("state-*.bin", "trace-*.txt", "img-*.bin", "tr-*.txt", "tp-*.bin",
                    "functions-padded.bin"):
        for stale in work.glob(pattern):
            stale.unlink()


def campaign(out: Path, args) -> dict:
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise SystemExit("CodeFlash.bin sha256 mismatch")
    out = out.resolve()
    if out == REPO_ROOT or not out.is_relative_to((REPO_ROOT / "build/out").resolve()):
        raise SystemExit("oracle outputs must live under build/out/")
    work = out / "linked-image"
    cleanup(out, work)
    elf, _model = sc.prepare_elf(out, args.timeout)
    functions = load_functions()
    started = time.time()
    table = build_table(image, functions, work)
    print(f"derived {len(table.sites)} prepare/dispose sites in {time.time() - started:.0f}s",
          flush=True)
    sites_json = {
        "prepare": [[hx(site.address), site.length, site.imm, list(site.registers), site.text]
                    for site in sorted(table.sites.values(), key=lambda s: s.address)
                    if site.kind == "prepare"],
        "dispose": [[hx(site.address), site.length, site.imm, list(site.registers), site.text]
                    for site in sorted(table.sites.values(), key=lambda s: s.address)
                    if site.kind == "dispose"],
    }
    (out / "instruction-sites.json").write_text(json.dumps(sites_json, indent=1) + "\n",
                                                encoding="utf-8")
    installers_json = installer_json(table)
    print("self-validation ...", flush=True)
    self_test_result = self_test(elf, out, args, table, work)
    families: list[dict] = []
    if self_test_result["passed"] and not args.self_test_only:
        selected = FAMILIES if "all" in args.families else tuple(args.families)
        if "dcm" in selected:
            cases = dcm_matrix_cases()
            if args.max_cases:
                cases = cases[:args.max_cases]
            print(f"[dcm-dispatch-matrix] {len(cases)} cases", flush=True)
            runs = run_family(StatefulDriver("dcm-dispatch-matrix", cases, work), elf, out, args, table)
            families.append(family_report("dcm-dispatch-matrix", merge_runs(runs), table))
        if "cantp" in selected:
            trials = ci.generate(0xC2A7, 256)
            if args.max_cases:
                trials = trials[:args.max_cases]
            print(f"[cantp-ingress] {len(trials)} trials", flush=True)
            runs = run_family(CantpDriver(trials, work), elf, out, args, table)
            families.append(family_report("cantp-ingress", merge_runs(runs), table))
        if "stateful" in selected:
            cases = sc.seed_cases()
            if args.max_cases:
                cases = cases[:args.max_cases]
            print(f"[stateful-seeds] {len(cases)} cases", flush=True)
            runs = run_family(StatefulDriver("stateful-seeds", cases, work), elf, out, args, table)
            families.append(family_report("stateful-seeds", merge_runs(runs), table))
        if "ab" in selected:
            families.extend(ab_families(elf, out, args, table, work, image))
    state = {
        "schema": SCHEMA,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "mode": "self-test-only" if args.self_test_only else "full",
        "target": {"name": "camry-8965F3307000",
                   "image": "firmware/camry-8965F3307000/CodeFlash.bin",
                   "sha256": IMAGE_SHA256},
        "hook_cells": [hx(cell) for cell in HOOK_CELLS],
        "executable_tail": [hx(EXECUTABLE_TAIL[0]), hx(EXECUTABLE_TAIL[1])],
        "rwx_pocket": [hx(RWX_POCKET[0]), hx(RWX_POCKET[1])],
        "violation_classes": list(VIOLATION_CLASSES),
        "anomaly_classes": list(ANOMALY_CLASSES),
        "instruction_sets": instruction_set_summary(table, functions),
        "installers": installers_json,
        "self_test": self_test_result,
        "families": families,
    }
    totals = {
        "cases_traced": sum(r["cases_traced"] for r in families),
        "steps_traced": sum(r["steps_traced"] for r in families),
        "trace_accesses": sum(r["trace_accesses"] for r in families),
        "violations": sum(r["violations"] for r in families),
        "live_slot_violations": sum(r["live_slot_violations"] for r in families),
        "hook_cell_violations": sum(r["hook_cell_violations"] for r in families),
        "tail_writes": sum(r["tail_writes"] for r in families),
        "rwx_pocket_writes": sum(r["rwx_pocket_writes"] for r in families),
        "abnormal_terminations": sum(r["abnormal_terminations"] for r in families),
        "incomplete_cases": sum(r["incomplete_cases"] for r in families),
        "stock_hook_writes": sum(r["hook_cell_stock_writes"] for r in families),
        "hook_installer_values_outside_codeflash": sum(
            len(r["hook_installer_values_outside_codeflash"]) for r in families),
    }
    totals.update(union_coverage(families))
    state["totals"] = totals
    state["notes"] = [
        ("A live saved slot is any word a PREPARE stored and no DISPOSE has read yet; the "
         "lp store (last push, lowest address, sp+4*imm) is the saved return address."),
        ("The oracle sees only executed code: a clean family says nothing about paths its "
         "corpus never reached; coverage is stated per family above."),
        ("Stack discipline is reset at every harness step (SP=0xFEBE2000); slots still live at "
         "the end of a step are counted as the `live-slots-at-step-end` anomaly."),
        ("Sim-only foreign code (the DCRA1 CRC model at 0xFEF00000) is outside the image-derived "
         "PREPARE/DISPOSE sets; it runs below the caller's live slots."),
        ("The sim-only capacity overlay of the SID 0xAB contract cases (CodeFlash 0x25F0C) and "
         "the PMR thunk patches are harness artifacts, not firmware behaviour."),
    ]
    write_outputs(out, state)
    return state


def ab_families(elf: Path, out: Path, args, table: SiteTable, work: Path,
                image: bytes) -> list[dict]:
    base, _ = ab.normalize_snapshot(elf, out, args.timeout)
    poison = ab.poison_image(0xA11CE)
    probes = ab.probe_cases(image)
    observations = ab.run_group(elf, list(enumerate(probes)), base, poison, out,
                                args.timeout, "probe")
    observed: dict[str, int] = {}
    keys = {probe.name: key for probe, key in zip(
        probes, ("kind1_max", "kind3_active_max", "kind3_bank_max", "kind2_bank_max"))}
    probe_runs: list[CaseRun] = []
    for observation in observations:
        record = ab.judge(observation, poison)
        if record.get("published") and record["published"]["disposition"] == 0:
            observed[keys[observation.case.name]] = max(record["selected_length"] or [0])
        scan = scan_step(observation.trace, 0, table)
        probe_runs.append(CaseRun(
            "ab-probe", observation.case.name, observation.case.name,
            {"request_hex": observation.case.request.hex()},
            [observation.pc], [scan], observation.error,
            "stock snapshot, stock capacity, maximum stored-event state"))
    if sorted(set(keys.values()) - set(observed)):
        raise SystemExit(f"probe cases produced no payload: {sorted(set(keys.values()) - set(observed))}")
    cases = ab.build_cases(image, observed)
    if args.max_cases:
        cases = cases[:args.max_cases]
    volatile = [case for case in cases if case.family in ab.SYNTHETIC_FAMILIES]
    steady = [case for case in cases if case.family not in ab.SYNTHETIC_FAMILIES]
    runs: list[CaseRun] = []
    print(f"[ab-contract] {len(steady)} steady + {len(volatile)} synthetic-state cases", flush=True)
    steady_args = argparse.Namespace(**vars(args))
    steady_args.batch_size = min(args.batch_size, 32)
    runs += run_family(AbDriver("ab-contract", steady, base, poison, work), elf, out,
                       steady_args, table)
    volatile_args = argparse.Namespace(**vars(args))
    volatile_args.batch_size = 4
    volatile_args.timeout = min(args.timeout, 30.0)
    runs += run_family(AbDriver("ab-contract", volatile, base, poison, work), elf, out,
                       volatile_args, table)
    return [family_report("ab-probe", merge_runs(probe_runs), table),
            family_report("ab-contract", merge_runs(runs), table)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--self-test-only", action="store_true")
    parser.add_argument("--families", default="all",
                        help="comma-separated subset of dcm,cantp,stateful,ab (default all)")
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-cases", type=int, default=0,
                        help="debug: cap each family at N cases (0 = no cap)")
    args = parser.parse_args()
    chosen = args.families.split(",")
    if "all" not in chosen and any(name not in FAMILIES for name in chosen):
        raise SystemExit(f"--families must be a subset of {','.join(FAMILIES)}")
    args.families = chosen
    state = campaign(args.out, args)
    totals = state["totals"]
    print(json.dumps({
        "self_test_passed": state["self_test"]["passed"],
        "families": {report["family"]: {
            "cases_traced": report["cases_traced"],
            "prepare_sites_executed": report["prepare_sites_executed"],
            "functions_with_prepare_executed": report["functions_with_prepare_executed"],
            "violations": report["violations"],
            "abnormal_terminations": report["abnormal_terminations"],
        } for report in state["families"]},
        "totals": totals,
    }, indent=2, sort_keys=True))
    if not state["self_test"]["passed"]:
        return 2
    return 1 if totals["violations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
