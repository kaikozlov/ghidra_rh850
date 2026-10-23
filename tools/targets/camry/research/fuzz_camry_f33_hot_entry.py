"""Reproducible offline RH850 CodeFlash fuzzing of exact-Camry hot-entry gates.

Runs *original RH850 instructions* in the pinned V850E3v5 GNU simulator. One
linked stock image is reused across all GDB batches; no Ghidra, car, patch, or
synthetic bytecode implementation is involved. The pending-join cohort stops
*before* the system-mode/programming request at 0x4D604 and must not be
construed as proof that the subsequent handoff or RAM payload executes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from tools import REPO_ROOT
from tools.rh850_codeflash import run, run_elf

IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/hot-entry-fuzz"
BASE = {"speed": 0x4D5BA, "precondition": 0x4D5D8, "latch": 0x8B17E,
        "stage": 0x8B1B2, "pending": 0x8B334, "xcp": 0x98E80}
RETURN = 0x798
EVENT = 0x4D604
RX = re.compile(r"^HOT (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)\s*$", re.MULTILINE)
SEQ_PRE = re.compile(r"^SEQ_PRE (\d+) (\d+) (\d+) (\d+)\s*$", re.MULTILINE)
SEQ_MID = re.compile(r"^SEQ_MID (\d+) (\d+) (\d+) (\d+)\s*$", re.MULTILINE)
SEQ_POST = re.compile(r"^SEQ_POST (\d+) (\d+) (\d+) (\d+) (\d+)\s*$", re.MULTILINE)
WINDOW_PRE = re.compile(r"^WINDOW_PRE (\d+) (\d+) (\d+)\s*$", re.MULTILINE)
WINDOW_POST = re.compile(r"^WINDOW_POST (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)\s*$", re.MULTILINE)
CANCEL_RX = re.compile(r"^CANCEL (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Trial:
    family: str
    target: int = 2
    speed: int = 0
    phase: int = 0x22
    supply: int = 0xA00
    addressing: int = 0
    latch: int = 0
    pending: int = 0
    state: int = 0
    application_status: int = 1
    lower_status: int = 1
    request_latch: int = 0x5A
    xcp_word0: int = 0
    xcp_word1: int = 0


def generate(seed: int, random_each: int) -> list[Trial]:
    rng = random.Random(seed)
    items: list[Trial] = []
    boundary_speed = [0, 1, 0x7F, 0x100, 0x17E, 0x17F, 0x180, 0x181,
                      0x182, 0x1FF, 0x7FFF, 0x8000, 0xFFFF]
    boundary_supply = [0, 1, 0x9FE, 0x9FF, 0xA00, 0xA01, 0x8000, 0xFFFF]
    for session in (0, 1, 2, 3, 0x40, 0x82, 0xFF):
        items.extend(Trial("speed", target=session, speed=v) for v in boundary_speed)
    items.extend(Trial("speed", target=session, speed=0x181) for session in range(256))
    for phase in range(256):
        items.append(Trial("precondition", phase=phase))
        items.append(Trial("latch", phase=phase))
        items.append(Trial("latch", phase=phase, latch=0x5A))
        items.append(Trial("stage", phase=phase))
        items.append(Trial("pending", phase=phase))
    for addressing in range(256):
        items.append(Trial("precondition", addressing=addressing))
    for supply in boundary_supply:
        for addressing in (0, 1, 0x80, 0xFF):
            items.extend((Trial("precondition", supply=supply, addressing=addressing),
                          Trial("latch", supply=supply, addressing=addressing),
                          Trial("pending", supply=supply, addressing=addressing)))
    for opcode in range(256):
        items.append(Trial("xcp", xcp_word0=(rng.getrandbits(24) << 8) | opcode,
                           xcp_word1=rng.getrandbits(32)))
    for family in BASE:
        for _ in range(random_each):
            fields = {"phase": rng.randrange(256), "supply": rng.randrange(65536),
                      "addressing": rng.randrange(256)}
            if family == "xcp":
                fields = {"target": rng.randrange(256), "xcp_word0": rng.getrandbits(32),
                          "xcp_word1": rng.getrandbits(32)}
            elif family == "speed":
                fields = {"target": rng.choice((2, 2, 2, 2, 0, 1, 3, 0x40, rng.randrange(256))),
                          "speed": rng.randrange(65536)}
            elif family == "latch":
                fields["latch"] = rng.choice((0, 0, 0, 0x5A, 1, 0xFF))
            elif family == "stage":
                # Stage 0 is firmware startup for this state machine. Stage 1
                # models its poll; other states are deliberately exploratory.
                fields.update({"state": rng.choice((0, 0, 0, 1, 2, 255)),
                               "application_status": rng.choice((0, 1, 10)),
                               "lower_status": rng.choice((0, 1, 10)),
                               "latch": rng.choice((0, 0, 0x5A))})
            elif family == "pending":
                fields.update({"pending": rng.choice((0, 0, 0, 0x5A)),
                               "latch": rng.choice((0, 0, 0x5A))})
            items.append(Trial(family, **fields))
    # Fixed ordering and seed; zero-value edge cases are not lost to sampling.
    return items


def expected(trial: Trial) -> tuple[int | None, int | None, int | None, int | None]:
    """Independent input/return oracle; None means exploratory rather than tested."""
    gate = int(trial.phase == 0x11 or trial.supply < 0xA00 or trial.addressing != 0)
    if trial.family == "xcp":
        # Fixed original CodeFlash[0x30D68] = 0x5A blocks XCP before any
        # command or payload fields are interpreted.
        return RETURN, 1, trial.latch, trial.request_latch
    if trial.family == "speed":
        return RETURN, 11 if trial.target == 2 and trial.speed > 0x180 else 0, None, None
    if trial.family == "precondition":
        return RETURN, gate, None, None
    if trial.family == "latch":
        blocked = gate if trial.latch == 0 else 0
        return RETURN, blocked, trial.latch or (0x5A if not blocked else 0), (0 if trial.latch == 0 and not blocked else trial.request_latch)
    if trial.family in ("stage", "pending"):
        if trial.family == "stage" and trial.state == 0 and trial.application_status == 1 and trial.lower_status == 1:
            blocked = gate if trial.latch == 0 else 0
            return RETURN, blocked, trial.latch or (0x5A if not blocked else 0), (0 if trial.latch == 0 and not blocked else trial.request_latch)
        if trial.family == "pending" and trial.state == 0 and trial.pending == 0:
            blocked = gate if trial.latch == 0 else 0
            return RETURN if blocked else EVENT, (1 if blocked else None), trial.latch or (0x5A if not blocked else 0), (0 if trial.latch == 0 and not blocked else trial.request_latch)
        if trial.family == "pending" and trial.pending:
            return RETURN, 10, trial.latch, trial.request_latch
    return None, None, None, None


def gdb_commands(batch: list[tuple[int, Trial]]) -> list[str]:
    commands = [
        "set $r4=0xFEBEB800", "set $r5=0x23DFC", "break *0x798", "commands", "silent", "end",
        "break *0x4D604", "commands", "silent", "end",
    ]
    for index, case in batch:
        # RAM is set anew for *every* run; GDB registers/stack also reset.
        commands.extend((
            f"set $pc=0x{BASE[case.family]:x}", "set $r3=0xFEBE2000", "set $r31=0x798",
            f"set $r6={case.target if case.family == 'xcp' else 0}",
            f"set $r7={0xFEBE4000 if case.family == 'xcp' else case.target}",
            f"set $r8={8 if case.family == 'xcp' else 0}",
            f"set {{unsigned int}}0xFEBE4000={case.xcp_word0}",
            f"set {{unsigned int}}0xFEBE4004={case.xcp_word1}",
            f"set {{unsigned short}}0xFEBEE892={case.speed}",
            f"set {{unsigned char}}0xFEBEE81F={case.phase}",
            f"set {{unsigned short}}0xFEBE66BA={case.supply}",
            f"set {{unsigned char}}0xFEBE819A={case.addressing}",
            f"set {{unsigned char}}0xFEBF3B18={case.latch}",
            f"set {{unsigned char}}0xFEBF3B19={case.pending}",
            f"set {{unsigned char}}0xFEBF3B1A={case.state}",
            f"set {{unsigned char}}0xFEBF3B1B={case.application_status}",
            f"set {{unsigned char}}0xFEBF3B1C={case.lower_status}",
            "set {unsigned char}0xFEBF3B1D=255",
            f"set {{unsigned char}}0xFEBE81AE={case.request_latch}",
            "continue",
            f'printf "HOT {index} %u %u %u %u %u %u %u %u %u\\n", $pc, $r10, *(unsigned char*)0xFEBF3B18, *(unsigned char*)0xFEBF3B19, *(unsigned char*)0xFEBF3B1A, *(unsigned char*)0xFEBF3B1B, *(unsigned char*)0xFEBF3B1C, *(unsigned char*)0xFEBE81AE, *(unsigned short*)0xFEBE66BA',
            # Stop at event admission; never execute the ECU mode/reset request.
            "set $pc=0x798",
        ))
    commands.append(f'printf "HOT_END={batch[-1][0]}\\n"')
    return commands


def sequence_cases(seed: int, random_count: int) -> list[tuple[int, int, int]]:
    """Mutate state *after* successful first admission, before DCM polls again."""
    rng = random.Random(seed ^ 0x8B134)
    cases = [(phase, 0xA00, 0) for phase in range(256)]
    cases.extend((0x22, 0xA00, addr) for addr in range(256))
    cases.extend((rng.randrange(256), rng.randrange(65536), rng.randrange(256))
                 for _ in range(random_count))
    return cases


def sequence_commands(group: list[tuple[int, tuple[int, int, int]]]) -> list[str]:
    commands = ["set $r4=0xFEBEB800", "set $r5=0x23DFC"]
    for addr in (0x8B134, 0x8B170, EVENT, RETURN):
        commands += [f"break *0x{addr:x}", "commands", "silent", "end"]
    for index, (phase, supply, addressing) in group:
        commands += [
            # The first gate passes through the actual 0x8B1B2 state-machine
            # body: the latch is produced by original firmware, not fabricated.
            "set $r3=0xFEBE2000", "set $r31=0x798", "set $pc=0x8B1B2",
            "set {unsigned char}0xFEBF3B18=0", "set {unsigned char}0xFEBF3B19=0",
            "set {unsigned char}0xFEBF3B1A=0", "set {unsigned char}0xFEBF3B1B=1",
            "set {unsigned char}0xFEBF3B1C=1", "set {unsigned char}0xFEBF3B1D=255",
            "set {unsigned char}0xFEBE81AE=90", "set {unsigned char}0xFEBEE81F=34",
            "set {unsigned short}0xFEBE66BA=2560", "set {unsigned char}0xFEBE819A=0",
            "continue",
            f'printf "SEQ_PRE {index} %u %u %u\\n", $pc, *(unsigned char*)0xFEBF3B18, *(unsigned char*)0xFEBF3B1A',
            f"set {{unsigned char}}0xFEBEE81F={phase}",
            f"set {{unsigned short}}0xFEBE66BA={supply}",
            f"set {{unsigned char}}0xFEBE819A={addressing}",
            # Normal DCM deferred-event owner: on the stage-1 failure this
            # function must enter the genuine reset helper, not event 9.
            "set $r3=0xFEBE2000", "set $r31=0x798", "set $pc=0x95CB0",
            "continue",
            f'printf "SEQ_MID {index} %u %u %u\\n", $pc, *(unsigned char*)0xFEBF3B18, *(unsigned char*)0xFEBF3B1A',
            "continue",
            f'printf "SEQ_POST {index} %u %u %u %u\\n", $pc, *(unsigned char*)0xFEBF3B18, *(unsigned char*)0xFEBF3B1A, *(unsigned char*)0xFEBF3B19',
            "set $pc=0x798",
        ]
    commands.append(f'printf "SEQ_END={group[-1][0]}\\n"')
    return commands


def fuzz_sequences(elf: Path, out: Path, seed: int, random_count: int,
                   batch_size: int, timeout: float) -> dict:
    cases = sequence_cases(seed, random_count)
    failures: list[dict] = []
    for offset in range(0, len(cases), batch_size):
        group = list(enumerate(cases[offset:offset+batch_size], offset))
        output = run_elf(root=REPO_ROOT, elf_path=elf, stop="0x798",
                         memory_regions=["0xFEBE0000,0x20000"],
                         gdb_commands=sequence_commands(group),
                         expected_output=[f"SEQ_END={group[-1][0]}"], timeout=timeout,
                         output_path=out / f"sequence-batch-{offset//batch_size:04d}.txt")
        pre = {int(m[1]): tuple(map(int, m.groups()[1:])) for m in SEQ_PRE.finditer(output)}
        mid = {int(m[1]): tuple(map(int, m.groups()[1:])) for m in SEQ_MID.finditer(output)}
        post = {int(m[1]): tuple(map(int, m.groups()[1:])) for m in SEQ_POST.finditer(output)}
        for index, args in group:
            if (pre.get(index) != (RETURN, 0x5A, 1) or
                mid.get(index) != (0x8B134, 0x5A, 0) or
                post.get(index) != (0x8B170, 0, 0, 0)):
                failures.append({"index": index, "altered_gate_inputs": args,
                                 "first_admission": pre.get(index),
                                 "dcm_reset_entry": mid.get(index),
                                 "after_actual_reset_stores": post.get(index)})
        print(f"simulated call sequences {offset+len(group)}/{len(cases)}", flush=True)
    return {"count": len(cases), "mismatches": len(failures), "failures": failures[:30],
            "path": "0x8B1B2 (accept) -> 0x95CB0 (failure/cancel) -> 0x8B134 (reset)",
            "coverage": "all 256 post-admission phase bytes and addressing bytes, plus seeded mutation",
            "conclusion": "the tested DCM deferred-error path clears the existing latch, rather than carrying it into another request"}


def window_commands(group: list[tuple[int, tuple[int, int, int]]]) -> list[str]:
    """Inject a synthetic state change *between* stock admission and request."""
    cmds = ["set $r4=0xFEBEB800", "set $r5=0x23DFC"]
    for addr in (0x8B1A4, EVENT, RETURN):
        cmds += [f"break *0x{addr:x}", "commands", "silent", "end"]
    for index, (phase, supply, addressing) in group:
        cmds += [
            "set $r3=0xFEBE2000", "set $r31=0x798", "set $pc=0x8B334",
            "set {unsigned char}0xFEBF3B18=0", "set {unsigned char}0xFEBF3B19=0",
            "set {unsigned char}0xFEBF3B1A=0", "set {unsigned char}0xFEBF3B1B=1",
            "set {unsigned char}0xFEBF3B1C=1", "set {unsigned char}0xFEBF3B1D=255",
            "set {unsigned char}0xFEBE81AE=90", "set {unsigned char}0xFEBEE81F=34",
            "set {unsigned short}0xFEBE66BA=2560", "set {unsigned char}0xFEBE819A=0",
            "continue",
            f'printf "WINDOW_PRE {index} %u %u\\n", $pc, *(unsigned char*)0xFEBF3B18',
            f"set {{unsigned char}}0xFEBEE81F={phase}",
            f"set {{unsigned short}}0xFEBE66BA={supply}",
            f"set {{unsigned char}}0xFEBE819A={addressing}",
            "continue",
            f'printf "WINDOW_POST {index} %u %u %u %u %u\\n", $pc, *(unsigned char*)0xFEBF3B18, *(unsigned char*)0xFEBEE81F, *(unsigned short*)0xFEBE66BA, *(unsigned char*)0xFEBE819A',
            # The ECU programming/mode request has not been executed.
            "set $pc=0x798",
        ]
    cmds.append(f'printf "WINDOW_END={group[-1][0]}\\n"')
    return cmds


def fuzz_window(elf: Path, out: Path, seed: int, random_count: int,
                batch_size: int, timeout: float) -> dict:
    cases = sequence_cases(seed ^ 0x4D604, random_count)
    failures: list[dict] = []
    for offset in range(0, len(cases), batch_size):
        group = list(enumerate(cases[offset:offset+batch_size], offset))
        output = run_elf(root=REPO_ROOT, elf_path=elf, stop="0x798",
                         memory_regions=["0xFEBE0000,0x20000"],
                         gdb_commands=window_commands(group),
                         expected_output=[f"WINDOW_END={group[-1][0]}"], timeout=timeout,
                         output_path=out / f"window-batch-{offset//batch_size:04d}.txt")
        before = {int(m[1]): tuple(map(int, m.groups()[1:])) for m in WINDOW_PRE.finditer(output)}
        after = {int(m[1]): tuple(map(int, m.groups()[1:])) for m in WINDOW_POST.finditer(output)}
        for index, (phase, supply, addressing) in group:
            if before.get(index) != (0x8B1A4, 0) or after.get(index) != (
                EVENT, 0x5A, phase, supply, addressing
            ):
                failures.append({"index": index, "altered_inputs": cases[index],
                                 "before": before.get(index), "after": after.get(index)})
        print(f"simulated mid-admission mutations {offset+len(group)}/{len(cases)}", flush=True)
    return {"count": len(cases), "mismatches": len(failures), "failures": failures[:30],
            "mutation_point": "0x8B1A4, after precondition 0x4D5D8, before admission-latch store",
            "stop": "0x4D604, before the actual programming request",
            "scope": "synthetic synchronous RAM input changes; not an externally demonstrated race"}


def cancel_cases(seed: int, random_count: int) -> list[tuple[int, int]]:
    rng = random.Random(seed ^ 0x95B48)
    result = [(row, deferred) for row in range(256) for deferred in (0, 1, 2, 3, 4, 255)]
    result.extend((rng.randrange(256), rng.randrange(256)) for _ in range(random_count))
    return result


def cancel_commands(group: list[tuple[int, tuple[int, int]]]) -> list[str]:
    commands = ["set $r4=0xFEBEB800", "set $r5=0x23DFC"]
    for addr in (0x98A44, RETURN):
        commands += [f"break *0x{addr:x}", "commands", "silent", "end"]
    for index, (row, deferred) in group:
        commands += [
            "set $r3=0xFEBE2000", "set $r31=0x798", "set $pc=0x95B48",
            "set {unsigned char}0xFEBF3B18=90", "set {unsigned char}0xFEBF3B19=90",
            "set {unsigned char}0xFEBF3B1A=1", f"set {{unsigned char}}0xFEBE5D54={row}",
            f"set {{unsigned char}}0xFEBE5D55={deferred}",
            "continue",
            f'printf "CANCEL {index} %u %u %u %u %u\\n", $pc, *(unsigned char*)0xFEBE5D54, *(unsigned char*)0xFEBE5D55, *(unsigned char*)0xFEBF3B18, *(unsigned char*)0xFEBF3B19',
            # The normal cancel callback subsequently invokes event-ring cleanup.
            # Stop at its entry; the latch effects have already occurred.
            "set $pc=0x798",
        ]
    commands.append(f'printf "CANCEL_END={group[-1][0]}\\n"')
    return commands


def fuzz_cancel(elf: Path, out: Path, seed: int, random_count: int,
                batch_size: int, timeout: float) -> dict:
    cases = cancel_cases(seed, random_count)
    failures: list[dict] = []
    seen_reset = 0
    for offset in range(0, len(cases), batch_size):
        group = list(enumerate(cases[offset:offset + batch_size], offset))
        output = run_elf(root=REPO_ROOT, elf_path=elf, stop="0x798",
                         memory_regions=["0xFEBE0000,0x20000"],
                         gdb_commands=cancel_commands(group),
                         expected_output=[f"CANCEL_END={group[-1][0]}"], timeout=timeout,
                         output_path=out / f"cancel-batch-{offset//batch_size:04d}.txt")
        rows = {int(m[1]): tuple(map(int, m.groups()[1:])) for m in CANCEL_RX.finditer(output)}
        for index, (row, deferred) in group:
            reset = row == 1 and deferred in (1, 2)
            seen_reset += reset
            want = (0x98A44, row, 0 if reset else deferred,
                    0 if reset else 0x5A, 0 if reset else 0x5A)
            if rows.get(index) != want:
                failures.append({"index": index, "input": {"row": row, "deferred": deferred},
                                 "actual": rows.get(index), "expected": want})
        print(f"simulated cancel transitions {offset + len(group)}/{len(cases)}", flush=True)
    return {"count": len(cases), "reset_cases": seen_reset, "mismatches": len(failures),
            "failures": failures[:30], "entry": "0x95B48", "stop": "0x98A44",
            "scope": "synthetic row/state combinations at cancel callback; not proof of an externally reachable stale latch"}


def verify_image() -> None:
    digest = hashlib.sha256(IMAGE.read_bytes()).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"exact F33 CodeFlash changed: {digest}")


def fuzz(out: Path, seed: int, random_each: int, sequences: int, windows: int, cancels: int, batch_size: int, timeout: float) -> dict:
    verify_image()
    if out.resolve() == REPO_ROOT or not out.resolve().is_relative_to(REPO_ROOT / "build/out"):
        raise ValueError("fuzz outputs must live under build/out/")
    out.mkdir(parents=True, exist_ok=True)
    # Prepare exact 1-MiB firmware ELF once. Reuse the same linked bytes for all
    # trials rather than paying the GDB/objcopy startup for each mutation.
    _boot, elf = run(root=REPO_ROOT, image_path=IMAGE, entry=0x4D5BA,
                     stop="0x798", memory_regions=["0xFEBE0000,0x20000"],
                     gdb_commands=["set $r4=0xFEBEB800", "set $r31=0x798", "set $r7=0",
                                   "break *0x798", "continue"],
                     assertions=["$r10 == 0"], output_dir=out / "linked-image", timeout=timeout)
    if elf is None:
        raise RuntimeError("linked firmware was not retained")
    trials = generate(seed, random_each)
    observed: dict[int, dict] = {}
    failures: list[dict] = []
    result_groups: Counter[str] = Counter()
    for offset in range(0, len(trials), batch_size):
        group = list(enumerate(trials[offset:offset+batch_size], offset))
        marker = f"HOT_END={group[-1][0]}"
        output = run_elf(root=REPO_ROOT, elf_path=elf, stop="0x798",
                         memory_regions=["0xFEBE0000,0x20000"],
                         gdb_commands=gdb_commands(group), expected_output=[marker],
                         timeout=timeout, output_path=out / f"batch-{offset//batch_size:04d}.txt")
        matches = list(RX.finditer(output))
        if len(matches) != len(group):
            raise RuntimeError(f"simulated {len(matches)} / {len(group)} inputs in batch at {offset}")
        for match in matches:
            index, pc, value, latch, pending, state, app, low, request, supply = map(int, match.groups())
            if index in observed or index >= len(trials):
                raise RuntimeError(f"duplicate/bad simulated trial {index}")
            trial = trials[index]
            record = {"pc": pc, "r10": value, "latch": latch, "pending": pending,
                      "state": state, "application_status": app, "lower_status": low,
                      "request_latch": request, "supply": supply}
            observed[index] = record
            want_pc, want_return, want_latch, want_request = expected(trial)
            bad = ((want_pc is not None and pc != want_pc)
                   or (want_return is not None and value != want_return)
                   or (want_latch is not None and latch != want_latch)
                   or (want_request is not None and request != want_request)
                   or supply != trial.supply)
            if pc not in (RETURN, EVENT):
                bad = True
            result_groups[f"{trial.family}:0x{pc:x}:r10={value}"] += 1
            if bad:
                failures.append({"index": index, "input": asdict(trial), "actual": record,
                                 "expected": {"pc": want_pc, "r10": want_return,
                                              "latch": want_latch, "request_latch": want_request}})
        print(f"simulated {offset+len(group)}/{len(trials)}", flush=True)
    assert len(observed) == len(trials)
    sequence_result = fuzz_sequences(elf, out, seed, sequences, batch_size, timeout)
    window_result = fuzz_window(elf, out, seed, windows, batch_size, timeout)
    cancel_result = fuzz_cancel(elf, out, seed, cancels, batch_size, timeout)
    summary = {
        "schema": "camry-f33-hot-entry-original-rh850-fuzz-v1", "target": "8965F3307000",
        "codeflash_sha256": IMAGE_SHA256, "backend": "tools/rh850 CodeFlash, GNU V850E3v5 GDB simulator",
        "gdb_codeflash_patch": False, "physical_vehicle": False,
        "seed": seed, "random_cases_per_family": random_each, "batch_size": batch_size,
        "trials": len(trials), "observed": len(observed), "mismatches": len(failures),
        "sequences": sequence_result, "temporal_window": window_result,
        "cancel": cancel_result,
        "families": dict(Counter(trial.family for trial in trials)),
        "results": dict(sorted(result_groups.items())),
        "failures": failures[:30],
        "scope": "function-entry microstates; pending execution stops before 0x4D604",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20261022)
    parser.add_argument("--random-each", type=int, default=128, help="pseudorandom trials per entry family")
    parser.add_argument("--batch-size", type=int, default=300)
    parser.add_argument("--sequence-random", type=int, default=512, help="extra two-call deferred-error sequence mutations")
    parser.add_argument("--window-random", type=int, default=512, help="extra post-admission temporal mutations")
    parser.add_argument("--cancel-random", type=int, default=512, help="extra cancellation state mutations")
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if min(args.random_each, args.sequence_random, args.window_random, args.cancel_random) < 0 or args.batch_size < 1 or args.timeout <= 0:
        parser.error("random-each must be >=0; batch-size and timeout must be positive")
    result = fuzz(args.out, args.seed, args.random_each, args.sequence_random, args.window_random, args.cancel_random, args.batch_size, args.timeout)
    print(json.dumps({k:v for k,v in result.items() if k not in ("results", "failures")}, indent=2))
    if result["failures"]:
        print(json.dumps({"first_mismatch": result["failures"][0]}, indent=2))
    return int(any(result[k]["mismatches"] for k in ("sequences", "temporal_window", "cancel")) or result["mismatches"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
