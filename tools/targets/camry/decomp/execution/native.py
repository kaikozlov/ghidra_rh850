"""Execute native host workflows and compare machine observables."""
from __future__ import annotations

from tools.targets.camry.decomp.abi import _BOOT_RELOCATED_COPIES
from tools.targets.camry.decomp.syntax import _c_signature
from tools.targets.camry.decomp.execution.calls import call_corpus
import ctypes
from tools.targets.camry.decomp.execution.memory import install_address_space
from tools.targets.camry.decomp.execution.memory import install_regions
from tools.targets.camry.decomp.tree import load_matched
from tools.targets.camry.decomp.tree import load_symbols
from tools.targets.camry.decomp.execution.memory import materialize
import os
from tools.targets.camry.decomp.execution.memory import read_regions
from tools.targets.camry.decomp.execution.memory import scenario_regions
import signal
from tools.targets.camry.decomp.execution.memory import view_of
from tools.targets.camry.decomp.execution.calls import with_registers
from tools.targets.camry.decomp.execution.host_rewrite import (
    _NATIVE_LIVE_FRAME_STOPS,
    _native_entry_frame,
    _native_ram_continuation,
    _scenario_fill,
    native_workflow_stops,
)
from tools.targets.camry.decomp.execution.machine import run_native_harness
from tools.targets.camry.decomp.execution.model import FAIL_KINDS, Harness, Planned, STEP_LIMIT
from tools.targets.camry.decomp.execution.scenario import _clusters
from tools.targets.camry.decomp.sources import _load_bodies


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


def _check_call_sequence(library: ctypes.CDLL, scenario: dict) -> None:
    expected = scenario.get("call_sequence")
    if expected is None:
        return
    count = int(ctypes.c_uint32.in_dll(library, "camry_note_count").value)
    notes = (ctypes.c_uint32 * 8192).in_dll(library, "camry_notes")
    actual = [int(notes[index]) for index in range(min(count, 8192))]
    root = int(scenario["entry"]["address"], 16)
    if actual and actual[0] == root:
        actual = actual[1:]
    want = [int(value, 16) for value in expected]
    if actual != want:
        raise Harness(
            "call-sequence",
            "host "
            + " ".join(f"{addr:x}" for addr in actual[:8])
            + " bytes "
            + " ".join(f"{addr:x}" for addr in want[:8]),
        )


def call_native_workflow(
    library: ctypes.CDLL,
    name: str,
    signature: str,
    registers: dict,
    scenario: dict,
    stops: dict[int, tuple[str, int]],
) -> int:
    """Run linked native C and literal RAM glue to an actual requested PC."""
    from tools.targets.camry.decomp.execution.calls import load_registers

    entry = int(scenario["entry"]["address"], 16)
    symbols = {int(row["addr"], 16): row for row in load_symbols()}
    boot_signatures: dict[str, str] = {}
    targets = {}
    for row in load_matched():
        address = int(row["addr"], 16)
        if address == entry and row.get("form") == "lifted":
            raise Harness("external-branch", "native workflow cannot execute a lifted root")
        if row.get("status") not in {"equivalent", "byte-matched", "converted"} or row.get("form") == "lifted":
            continue
        symbol = symbols.get(address, {})
        target_signature = row.get("signature") or symbol.get("signature")
        if target_signature and symbol.get("name") == row["name"]:
            targets[address] = row["name"], target_signature
    targets[entry] = name, signature
    probes = {}
    for pc, (owner, address) in stops.items():
        if not owner:  # RAM stops are reached by the glue machine, not C probes.
            continue
        if address in probes and probes[address] != owner:
            raise Harness("external-branch", f"conflicting native stop owners at {address:#x}")
        probes[address] = owner

    u32 = ctypes.c_uint32
    arm = u32.in_dll(library, "camry_stop_arm")
    hit = u32.in_dll(library, "camry_stop_pc")
    halted = ctypes.c_int.in_dll(library, "camry_halted")
    ctypes.c_int.in_dll(library, "camry_halt_propagate").value = 1
    library.camry_read8.argtypes = [u32]
    library.camry_read8.restype = u32
    library.camry_write8.argtypes = [u32, u32]
    library.camry_write8.restype = None

    def read_memory(address: int, size: int) -> int:
        return sum(int(library.camry_read8(address + offset)) << (8 * offset) for offset in range(size))

    def write_memory(address: int, size: int, value: int) -> None:
        for offset in range(size):
            library.camry_write8(address + offset, (value >> (8 * offset)) & 0xFF)

    def call_native(address: int, state: dict[str, str]) -> dict[str, str]:
        target = targets.get(address)
        if target is None:
            raise Harness("external-branch", f"unregistered native C target at {address:#x}")
        target_name, target_signature = target
        if target_name in _BOOT_RELOCATED_COPIES:
            if not boot_signatures:
                boot_bodies, _duplicates = _load_bodies()
                boot_signatures.update({
                    owner: _c_signature(body) for owner, body in boot_bodies.items()
                    if owner in _BOOT_RELOCATED_COPIES
                })
            target_signature = boot_signatures.get(target_name, target_signature)
        try:
            getattr(library, target_name)
        except AttributeError as exc:
            raise Harness("external-branch", f"unlinked native C target {target_name} at {address:#x}") from exc
        probe = probes.get(address)
        if probe is not None and probe != target_name:
            raise Harness("external-branch", f"native stop owner mismatch at {address:#x}")
        firmware_stops = {pc for pc, (owner, _entry) in stops.items() if owner}
        active = (next(iter(firmware_stops)) if len(firmware_stops) == 1
                  else 0xffffffff if firmware_stops else 0)
        arm.value = active
        hit.value = 0
        halted.value = 0
        current = {**scenario, "entry": {**scenario["entry"], "address": hex(address)}}
        try:
            returned = call_corpus(library, target_name, target_signature, state, current)
        finally:
            arm.value = 0
        if returned is not None and not hit.value:
            (u32 * 32).in_dll(library, "camry_gpr")[10] = returned
        if hit.value:
            if (active != 0xffffffff and hit.value != active) or hit.value not in stops or not halted.value:
                raise Harness("external-branch", f"unexpected native stop probe at {hit.value:#x}")
            owner_entry = stops[hit.value][1]
            if (owner_entry != address and address not in {0x8370, 0xFEBF1000}
                    and hit.value not in _NATIVE_LIVE_FRAME_STOPS.get(address, ())):
                frame = _native_entry_frame(address, owner_entry)
                if hit.value != owner_entry or frame is None:
                    raise Harness("external-branch", "unsupported nested native checkpoint frame")
                size, return_pc = frame
                gpr = (u32 * 32).in_dll(library, "camry_gpr")
                sp = u32.in_dll(library, "camry_sp")
                sp.value -= size
                gpr[3] = sp.value
                write_memory(sp.value, 4, int(state["r31"], 16))
                gpr[31] = return_pc
        elif halted.value:
            raise Harness("external-branch", f"native C halted without a requested probe in {target_name}")
        observed = with_registers(library, state)
        if hit.value:
            observed["pc"] = hex(hit.value)
        return observed

    for label, index in (("sp", 3), ("gp", 4), ("tp", 5)):
        raw = registers.get(label, registers.get(f"r{index}", "0"))
        u32.in_dll(library, f"camry_{label}").value = int(raw, 0) if isinstance(raw, str) else raw
    raw_fill = scenario.get("gpr_fill", "0x11111111")
    fill = int(raw_fill, 0) if isinstance(raw_fill, str) else raw_fill
    load_registers(library, registers, fill)
    initial = with_registers(library, registers)
    scripts = _native_ram_continuation(scenario)
    for base, blob in scripts:
        if any(read_memory(base + offset, 1) != value for offset, value in enumerate(blob)):
            raise Harness("external-branch", f"native RAM glue differs from literal input at {base:#x}")
    result = run_native_harness(
        entry, initial, scripts, read_memory, write_memory, call_native,
        [int(pc, 0) if isinstance(pc, str) else int(pc) for pc in scenario["stop_addresses"]],
        int(scenario.get("max_instructions") or STEP_LIMIT),
    )
    load_registers(library, result["registers"], fill)
    hit.value = int(result["pc"], 16)
    halted.value = 1
    return int(result["registers"]["r10"], 16)


def _host_child(library: ctypes.CDLL, planned: Planned, scenario: dict, code: bytes) -> None:
    _bind_host(library)
    mapped = materialize(scenario)
    code_bytes = bytearray(code)
    code_view = view_of(code_bytes)
    if mapped is None:
        images = scenario_regions(scenario)
        install_regions(library, code_view, len(code), images)
    else:
        memory, base = mapped
        view = view_of(memory) if memory else view_of(bytearray(b"\x00"))
        install_address_space(library, code_view, len(code), view, base, memory)
        images = [(base, memory)]
    before = [(base, bytes(data)) for base, data in images]
    ctypes.c_uint8.in_dll(library, "camry_fill").value = _scenario_fill(scenario)
    ctypes.c_int.in_dll(library, "camry_halted").value = 0
    ctypes.c_int.in_dll(library, "camry_halt_propagate").value = 1
    stops = native_workflow_stops(scenario)
    if stops:
        returned = call_native_workflow(
            library, planned.name, planned.signature, scenario["registers"], scenario, stops,
        )
    else:
        returned = call_corpus(
            library, planned.name, planned.signature, scenario["registers"], scenario,
        )
    observed = with_registers(library, scenario["registers"])
    for check in scenario["checks"]:
        if check.get("kind") == "register" and check.get("register") == "r10":
            expected = int(check["equals"], 16)
            if returned is None:
                raise Harness("dropped-return")
            if returned != expected:
                raise Harness("return-mismatch", f"host {returned:#x} bytes {expected:#x}")
        elif check.get("kind") == "register":
            label = check["register"]
            actual = int(observed[label], 16)
            expected = int(check["equals"], 16)
            if actual != expected:
                raise Harness("register-mismatch", f"{label} host {actual:#x} bytes {expected:#x}")
        elif check.get("kind") == "memory":
            address = int(check["address"], 16)
            size = int(check["size"])
            try:
                actual = read_regions(images, address, size).hex()
            except AssertionError:
                if not (0 <= address and address + size <= len(code_bytes)):
                    raise
                actual = bytes(code_bytes[address:address + size]).hex()
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
    covered.extend(
        (run.stack_lo, run.stack_hi)
        for run in planned.runs if run.fill == _scenario_fill(scenario)
    )
    for run in planned.runs:
        if run.fill != _scenario_fill(scenario):
            continue
        for lo, length in _clusters([(lo, hi - lo) for lo, hi in run.switch_spans], 0):
            hi = lo + length
            live = hi
            if run.halt is None and lo <= run.regs[3] < hi:
                live = run.regs[3]
            if lo <= run.regs[2] < hi:
                live = min(live, run.regs[2])
            # Exempt only dead ABI spills, never an escaped r2 frame or live
            # switched-SP frame. Their writes must have passed checks above.
            covered.append((lo, live))
    for (base, original), (_base, data) in zip(before, images):
        for offset, (old, new) in enumerate(zip(original, data)):
            if old == new:
                continue
            address = base + offset
            if any(start <= address < end for start, end in covered):
                continue
            raise Harness("memory-mismatch", f"{address:#x} extra {new:02x} was {old:02x}")
    for offset, (old, new) in enumerate(zip(code, code_bytes)):
        if old == new:
            continue
        if any(start <= offset < end for start, end in covered):
            continue
        raise Harness("memory-mismatch", f"{offset:#x} extra {new:02x} was {old:02x}")
    _check_call_sequence(library, scenario)


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
        # A Python handler cannot interrupt a native ctypes call.
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
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
    if os.WIFSIGNALED(status):
        detail = f"signal {os.WTERMSIG(status)} {detail}"
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
        return None
    for kind in FAIL_KINDS:
        if kind in detail:
            if kind in {"memory-mismatch", "return-mismatch", "register-mismatch", "call-sequence"}:
                print(f"disagree {kind} {planned.name} {detail[:180]}", flush=True)
            return kind
    if "unmapped" in detail or "outside" in detail:
        print(f"disagree host-unmapped {planned.name} {detail[:180]}", flush=True)
        return "host-unmapped"
    text = " ".join(detail.split())[:80]
    return f"host-fault {text}" if text else "host-fault"

