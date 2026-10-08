#!/usr/bin/env python3
"""Build and test RH850 payloads and firmware with the pinned toolchain."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections.abc import Sequence
from pathlib import Path

from tools import REPO_ROOT

ROOT = REPO_ROOT
IMAGE = "ghidra-rh850-v850-gcc:16.2.0-binutils2.46.1-gdb18.1-simfix2"
DOCKERFILE = ROOT / "tools" / "toolchains" / "v850-gcc" / "Dockerfile"
SELFTEST_RESULT = "RH850_SELFTEST_RESULT=0x12cb5687"
SELFTEST_CODEFLASH_RESULT = "RH850_CODEFLASH_RESULT=0xc0deface"

SELFTEST_SCRIPT = r"""
set -eu
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cat >"$work/selftest.c" <<'EOF'
unsigned int selftest_compute(unsigned int x) {
  volatile unsigned int value = x;
  return (value + 0x5678u) ^ 0x00ff00ffu;
}
EOF
cat >"$work/selftest.S" <<'EOF'
    .section .codeflash.start
    .global codeflash_start
codeflash_start:
    /* A full 1 MiB low section must retain this block at its real CodeFlash
       address instead of aliasing each 0x8000-byte block. */
    mov 0xc0deface, r10
    mov 0xfebf1004, r11
    st.w r10, 0[r11]
    jr32 high_start

    .section .text.start
    .global high_start
high_start:
    /* Exercise positive and negative format-VI disp32 control flow.  The far
       section forces a non-zero upper displacement word in both directions. */
    jarl32 far_call, lp
    mov 0x13579bdf, r11
    cmp r11, r10
    bne selftest_fail
    jr32 far_jump

selftest_fail:
    mov 0xbad00001, r10
    mov 0xfebf1000, r11
    st.w r10, 0[r11]
    .global rh850_sim_fail_stop
rh850_sim_fail_stop:
    br rh850_sim_fail_stop

low_call:
    mov 0x13579bdf, r10
    jmp [lp]

low_jump:
    mov 0xfebf8000, sp
    mov 0x12340000, r6
    jarl32 _selftest_compute, lp
    mov 0xfebf1000, r11
    st.w r10, 0[r11]
    .global rh850_sim_stop
rh850_sim_stop:
    br rh850_sim_stop

    .section .text.far
far_call:
    mov lp, r20
    jarl32 low_call, lp
    mov r20, lp
    jmp [lp]

far_jump:
    jr32 low_jump
EOF
cat >"$work/selftest.ld" <<'EOF'
SECTIONS {
  .codeflash 0x00000000 : {
    FILL(0x00)
    . = 0x0008F800;
    *(.codeflash.start)
    . = 0x00100000;
  }
  . = 0xFEBF0000;
  .text.start : { *(.text.start) }
  . = 0xFEBF1000;
  .result : { *(.result) }
  . = 0xFEC10000;
  .text.far : { *(.text.far) }
  .text : { *(.text) *(.text.*) }
}
ENTRY(codeflash_start)
EOF
v850-elf-gcc \
  -mv850e3v5 -mno-app-regs -ffreestanding -fno-builtin -Os -nostdlib \
  -Wa,-mv850e3v5,-mextension \
  -Wl,-T,"$work/selftest.ld" -Wl,--build-id=none \
  "$work/selftest.S" "$work/selftest.c" -o "$work/selftest.elf"
v850-elf-gdb -q -batch \
  -ex "file $work/selftest.elf" \
  -ex "target sim --architecture v850e3v5 --memory-region 0xFEBF0000,0x30000" \
  -ex load \
  -ex "break rh850_sim_stop" \
  -ex "break rh850_sim_fail_stop" \
  -ex run \
  -ex 'printf "RH850_SELFTEST_RESULT=0x%x\nRH850_CODEFLASH_RESULT=0x%x\n", *(unsigned int *)0xFEBF1000, *(unsigned int *)0xFEBF1004'
"""


class Rh850ToolError(RuntimeError):
    pass


def _docker() -> str:
    path = shutil.which("docker")
    if path is None:
        raise Rh850ToolError("docker is required")
    return path


def _run(
    args: list[str],
    *,
    input_text: str | None = None,
    capture: bool = False,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=capture,
        check=check,
    )


def _image_id() -> str:
    proc = _run(
        [_docker(), "image", "inspect", IMAGE, "--format", "{{.Id}}"],
        capture=True,
    )
    if proc.returncode != 0:
        raise Rh850ToolError(
            f"Docker image {IMAGE!r} is missing; "
            "build it with `tools/rh850 toolchain build`."
        )
    return proc.stdout.strip()


def _require_image() -> None:
    _image_id()


def _container_base(*, writable: bool, work_dir: Path | None = None) -> list[str]:
    mount_mode = "rw" if writable else "ro"
    command = [
        _docker(),
        "run",
        "--rm",
        "-v",
        f"{ROOT}:/src:{mount_mode}",
        "-w",
        "/src",
    ]
    if work_dir is not None:
        resolved = work_dir.resolve()
        if not resolved.is_dir():
            raise Rh850ToolError(f"work directory does not exist: {resolved}")
        command += ["-v", f"{resolved}:/out:rw"]
    command.append(IMAGE)
    return command


def cmd_build_image(_args: argparse.Namespace) -> int:
    if not DOCKERFILE.is_file():
        raise Rh850ToolError(f"missing toolchain recipe: {DOCKERFILE}")
    command = [
        _docker(),
        "build",
        "--file",
        str(DOCKERFILE),
        "--tag",
        IMAGE,
        str(DOCKERFILE.parent),
    ]
    return _run(command).returncode


def cmd_image(_args: argparse.Namespace) -> int:
    print(IMAGE)
    return 0


def cmd_info(_args: argparse.Namespace) -> int:
    image_id = _image_id()
    print(json.dumps({
        "schema": "rh850-toolchain-v1",
        "backend": "tools/rh850",
        "image": IMAGE,
        "image_id": image_id,
    }, sort_keys=True))
    return 0

def cmd_doctor(_args: argparse.Namespace) -> int:
    image_id = _image_id()
    probe = _run(
        _container_base(writable=False)
        + [
            "sh",
            "-lc",
            """
set -eu
v850-elf-gcc --version | head -n 1
v850-elf-ld --version | head -n 1
v850-elf-gdb --version | head -n 1
v850-elf-gdb -q -batch -ex 'target sim --architecture-info'
""",
        ],
        capture=True,
    )
    sys.stdout.write(f"image: {IMAGE}\nimage_id: {image_id}\n")
    sys.stdout.write(probe.stdout)
    if probe.stderr:
        sys.stderr.write(probe.stderr)
    if probe.returncode != 0:
        return probe.returncode
    if "v850e3v5" not in probe.stdout:
        raise Rh850ToolError("GDB simulator does not advertise v850e3v5 support")
    print("doctor: PASS")
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    _require_image()
    command = list(args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        raise Rh850ToolError("toolchain run requires a command")
    base = _container_base(
        writable=args.work_dir is None,
        work_dir=args.work_dir,
    )
    return _run(base + command).returncode


def _bounded_container(
    base: list[str], command: list[str], timeout: float,
) -> subprocess.CompletedProcess[str]:
    """Bound the process inside Docker as well as its host-side client."""
    name = f"rh850-test-{uuid.uuid4().hex}"
    args = [
        *base[:-1], "--name", name, base[-1],
        "timeout", "--signal=KILL", f"{timeout}s", *command,
    ]
    try:
        return subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, timeout=timeout + 10, check=False,
        )
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        subprocess.run(
            [_docker(), "rm", "-f", name], capture_output=True, timeout=10, check=False,
        )
        raise


def validate_execution(
    *, stop: str, assertions: Sequence[str], expected_output: Sequence[str],
    gdb_commands: Sequence[str], timeout: float,
) -> str:
    """Validate a test contract before any compilation or simulator work."""
    if not math.isfinite(timeout) or timeout <= 0:
        raise Rh850ToolError("execution timeout must be positive and finite")
    if not stop:
        raise Rh850ToolError("test requires --stop (a symbol or numeric address)")
    if re.fullmatch(r"0[xX][0-9a-fA-F]+|[0-9]+", stop):
        address = int(stop, 16 if stop.lower().startswith("0x") else 10)
        if not 0 <= address <= 0xFFFFFFFF:
            raise Rh850ToolError("stop address is outside the 32-bit address space")
        expression = f"0x{address:X}"
    elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.$]*", stop):
        expression = f"(unsigned long)&{stop}"
    else:
        raise Rh850ToolError("stop must be a symbol or numeric address, not a GDB command")
    if not assertions and not expected_output:
        raise Rh850ToolError("test requires a postcondition: --assert or --expect")
    if any(not value.strip() for value in (*assertions, *expected_output)):
        raise Rh850ToolError("postconditions must not be empty")
    if gdb_commands and not any(
        re.match(r"^(run|continue)(\s|$)", command.strip()) for command in gdb_commands
    ):
        raise Rh850ToolError("an explicit GDB script must execute run or continue")
    return expression


def execute_elf(
    *, elf_path: Path, stop: str, assertions: Sequence[str] = (),
    memory_regions: Sequence[str] = (), gdb_commands: Sequence[str] = (),
    expected_output: Sequence[str] = (), timeout: float = 30.0,
    output_path: Path | None = None,
) -> str:
    """Execute to a checked completion point; never report load-only success."""
    stop_expression = validate_execution(
        stop=stop, assertions=assertions, expected_output=expected_output,
        gdb_commands=gdb_commands, timeout=timeout,
    )
    elf = elf_path.resolve()
    if not elf.is_file():
        raise Rh850ToolError(f"ELF does not exist: {elf}")
    _require_image()
    target = "target sim --architecture v850e3v5"
    for region in memory_regions:
        target += f" --memory-region {region}"
    commands = [
        "set confirm off", "set pagination off",
        'file "/out/' + elf.name.replace("\\", "\\\\").replace('"', '\\"') + '"',
        target, "load", "starti",
        f"set $rh850_stop = {stop_expression}",
        'if $pc == $rh850_stop\nprintf "stop equals entry; no execution verified\\n"\nquit 1\nend',
    ]
    commands.extend(gdb_commands or (f"break *{stop_expression}", "continue"))
    commands.append(
        'if $pc != $rh850_stop\nprintf "unexpected stop: PC=0x%x expected=0x%x\\n", '
        '$pc, $rh850_stop\nquit 1\nend'
    )
    for index, expression in enumerate(assertions, 1):
        commands.extend((
            f"set $rh850_check = !!({expression})",
            f'printf "RH850_CHECK_{index}=%d\\n", $rh850_check',
            f'if !$rh850_check\nprintf "postcondition {index} failed\\n"\nquit 1\nend',
        ))
    commands.append('printf "RH850_EXECUTION_VERIFIED\\n"')
    output = ""
    try:
        try:
            with tempfile.TemporaryDirectory(prefix="rh850-gdb-") as td:
                script = Path(td) / "execute.gdb"
                script.write_text("\n".join(commands) + "\n", encoding="utf-8")
                base = _container_base(writable=False, work_dir=elf.parent)
                base[-1:-1] = ["-v", f"{td}:/script:ro"]
                proc = _bounded_container(
                    base,
                    ["v850-elf-gdb", "-nx", "-q", "-batch", "-x", "/script/execute.gdb"],
                    timeout,
                )
        except subprocess.TimeoutExpired as exc:
            output = "".join(
                value.decode(errors="replace") if isinstance(value, bytes) else value or ""
                for value in (exc.stdout, exc.stderr)
            )
            raise Rh850ToolError(f"execution timed out after {timeout:g}s\n{output}") from exc
        output = proc.stdout + proc.stderr
        if proc.returncode in (124, 137):
            raise Rh850ToolError(f"execution timed out after {timeout:g}s\n{output}")
        if proc.returncode != 0:
            raise Rh850ToolError(f"execution failed (exit {proc.returncode})\n{output}")
        if "RH850_EXECUTION_VERIFIED\n" not in output:
            raise Rh850ToolError(f"execution did not complete its checks\n{output}")
        for expected in expected_output:
            if expected not in output:
                raise Rh850ToolError(f"postcondition output lacks {expected!r}\n{output}")
        return output
    finally:
        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output, encoding="utf-8")


def _build_payload(sources: Sequence[Path], linker: Path, work: Path) -> Path:
    """Link caller sources with the same freestanding ABI used by payload builders."""
    inputs = [path.resolve() for path in (*sources, linker)]
    for path in inputs:
        if not path.is_file():
            raise Rh850ToolError(f"build input does not exist: {path}")
    _require_image()
    base = _container_base(writable=False, work_dir=work)
    mounts: dict[Path, str] = {}
    mapped: list[str] = []
    for path in inputs:
        if path.is_relative_to(ROOT):
            mapped.append(f"/src/{path.relative_to(ROOT)}")
        else:
            if path.parent not in mounts:
                mounts[path.parent] = f"/input{len(mounts)}"
            mapped.append(f"{mounts[path.parent]}/{path.name}")
    # Preserve repository-relative includes and external inputs' sibling headers.
    for parent, mount in mounts.items():
        base[-1:-1] = ["-v", f"{parent}:{mount}:ro"]
    # Linker INCLUDE paths are relative to its directory.
    base[-1:-1] = ["-w", str(Path(mapped[-1]).parent)]
    elf = work / "payload.elf"
    proc = _bounded_container(base, [
        "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-ffreestanding",
        "-fno-builtin", "-Os", "-nostdlib", "-Wa,-mv850e3v5,-mextension",
        f"-Wl,-T,{mapped[-1]}", "-Wl,--build-id=none",
        *mapped[:-1], "-o", "/out/payload.elf",
    ], 120.0)
    (work / "build.txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        raise Rh850ToolError(f"payload build failed (exit {proc.returncode})\n{proc.stdout}{proc.stderr}")
    return elf


def cmd_sim(args: argparse.Namespace) -> int:
    validate_execution(
        stop=args.stop, assertions=args.assertions, expected_output=args.expected_output,
        gdb_commands=args.gdb_command, timeout=args.timeout,
    )
    if args.linker_script is None and len(args.inputs) != 1:
        raise Rh850ToolError("supply one ELF, or sources with --linker-script")
    if args.output_dir is None:
        parent = ROOT / "build/out/rh850-payload"
        parent.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix=f"{args.inputs[0].stem}-", dir=parent))
    else:
        work = args.output_dir.resolve()
        work.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "failed", "stop": args.stop, "assertions": args.assertions,
        "expected_output": args.expected_output, "timeout_seconds": args.timeout,
    }
    report_path = work / "report.json"
    # Invalidate a previous successful report before starting another build.
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (work / "output.txt").write_text("", encoding="utf-8")
    try:
        elf = (
            _build_payload(args.inputs, args.linker_script, work)
            if args.linker_script is not None else args.inputs[0].resolve()
        )
        report["elf"] = str(elf)
        report["elf_sha256"] = hashlib.sha256(elf.read_bytes()).hexdigest()
        output = execute_elf(
            elf_path=elf, stop=args.stop, assertions=args.assertions,
            memory_regions=args.memory_region, gdb_commands=args.gdb_command,
            expected_output=args.expected_output, timeout=args.timeout,
            output_path=work / "output.txt",
        )
        report["status"] = "passed"
    except (Rh850ToolError, OSError, subprocess.SubprocessError) as exc:
        report["error"] = str(exc)
        raise
    finally:
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(output)
    print(f"Payload test: PASS\nreport: {report_path}")
    return 0


def cmd_selftest(_args: argparse.Namespace) -> int:
    _require_image()
    proc = _run(
        [_docker(), "run", "--rm", "-i", IMAGE, "sh", "-s"],
        input_text=SELFTEST_SCRIPT,
        capture=True,
    )
    sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        return proc.returncode
    for expected in (SELFTEST_RESULT, SELFTEST_CODEFLASH_RESULT):
        if expected not in proc.stdout:
            raise Rh850ToolError(
                f"simulator completed without expected result {expected!r}"
            )
    print("toolchain self-test: PASS")
    return 0


def cmd_codeflash_sim(args: argparse.Namespace) -> int:
    from tools.rh850_codeflash import CodeFlashSimError, load_spec, run

    image = args.image.resolve()
    output_dir = args.output_dir.resolve() if args.output_dir is not None else None

    loads: dict[int, Path] = {}
    for value in args.load:
        raw_address, separator, raw_path = value.partition("=")
        if not separator or not raw_address or not raw_path:
            raise Rh850ToolError("--load must use ADDRESS=PATH")
        try:
            address = int(raw_address, 0)
        except ValueError as exc:
            raise Rh850ToolError(f"invalid --load address {raw_address!r}") from exc
        if not 0 <= address <= 0xFFFFFFFF:
            raise Rh850ToolError(f"--load address {raw_address!r} is outside 32-bit space")
        if address in loads:
            raise Rh850ToolError(f"duplicate --load address 0x{address:08X}")
        loads[address] = Path(raw_path).resolve()

    spec = None
    if args.spec is not None:
        if args.image_base is not None or args.entry is not None:
            raise Rh850ToolError("--base and --entry cannot override a spec")
        spec_path = args.spec.resolve()
        try:
            spec = load_spec(ROOT, spec_path)
        except CodeFlashSimError as exc:
            raise Rh850ToolError(str(exc)) from exc

    try:
        output, _elf = run(
            root=ROOT,
            image_path=image,
            spec=spec,
            image_base=args.image_base or 0,
            entry=args.entry,
            memory_regions=args.memory_region,
            gdb_commands=args.gdb_command,
            ram_loads=list(loads.items()),
            output_dir=output_dir,
            expected_output=args.expected_output,
            stop=args.stop,
            assertions=args.assertions,
            timeout=args.timeout,
        )
    except CodeFlashSimError as exc:
        raise Rh850ToolError(str(exc)) from exc
    sys.stdout.write(output)
    print("CodeFlash test: PASS")
    return 0


def cmd_machine_run(args: argparse.Namespace) -> int:
    from tools.emulation.p1me_machine import P1MEMachineError, run_many

    output_dir = args.output_dir
    if output_dir is None:
        batch_name = args.scenarios[0].stem if len(args.scenarios) == 1 else "batch"
        output_dir = ROOT / "build" / "out" / "rh850-machine" / args.target / batch_name
    try:
        reports = run_many(args.target, args.scenarios, output_dir)
    except P1MEMachineError as exc:
        raise Rh850ToolError(str(exc)) from exc
    print(json.dumps({
        "target": args.target,
        "reports": [
            {
                "scenario": report["scenario"],
                "status": report["status"],
                "instruction_count": report["instruction_count"],
                "report": report["report_path"],
            }
            for report in reports
        ],
    }, indent=2, sort_keys=True))
    return 0


def cmd_machine_model(args: argparse.Namespace) -> int:
    from tools.emulation.generate_p1me_model import generate

    try:
        changed = generate(check=args.check)
    except RuntimeError as exc:
        raise Rh850ToolError(str(exc)) from exc
    if not changed:
        print("P1M-E model projections are current")
    else:
        for path in changed:
            print(path.relative_to(ROOT))
    return 0


def _execution_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--stop", help="required completion symbol/address (or supplied by --spec)")
    parser.add_argument(
        "--assert", dest="assertions", action="append", default=[], metavar="EXPR",
        help="GDB boolean expression required to hold at completion; repeat as needed",
    )
    parser.add_argument(
        "--expect", dest="expected_output", action="append", default=[], metavar="TEXT",
        help="required output from an explicit GDB script; repeat as needed",
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, metavar="SECONDS",
        help="finite execution deadline (default: 30 seconds)",
    )
    parser.add_argument(
        "--memory-region", action="append", default=[], metavar="BASE,SIZE",
        help="simulator RAM/flash mapping; repeat as needed",
    )
    parser.add_argument(
        "--command", "-ex", dest="gdb_command", action="append", default=[],
        help="advanced complete GDB script, including run/continue; repeat for each command",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rh850", description=__doc__)
    sub = parser.add_subparsers(dest="area", required=True)

    toolchain = sub.add_parser(
        "toolchain",
        help="manage or invoke the single pinned GNU toolchain",
    )
    toolchain_sub = toolchain.add_subparsers(
        dest="toolchain_command",
        required=True,
    )

    p = toolchain_sub.add_parser("build", help="build the pinned toolchain image")
    p.set_defaults(func=cmd_build_image)

    p = toolchain_sub.add_parser(
        "image",
        help="print the pinned image tag without requiring Docker",
    )
    p.set_defaults(func=cmd_image)

    p = toolchain_sub.add_parser(
        "info",
        help="print canonical toolchain metadata as JSON",
    )
    p.set_defaults(func=cmd_info)

    p = toolchain_sub.add_parser(
        "doctor",
        help="show compiler/GDB identities and simulator architecture support",
    )
    p.set_defaults(func=cmd_doctor)

    p = toolchain_sub.add_parser(
        "self-test",
        help="run the low-CodeFlash and high-RAM simulator regression",
    )
    p.set_defaults(func=cmd_selftest)

    p = toolchain_sub.add_parser(
        "run",
        help="run a v850-elf tool inside the pinned image",
    )
    p.add_argument(
        "--work-dir",
        type=Path,
        help=(
            "mount a builder scratch directory at /out "
            "and mount the repository read-only"
        ),
    )
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_exec)

    model = sub.add_parser(
        "model",
        help="manage the generated SystemRDL-backed P1M-E device model",
    )
    model_sub = model.add_subparsers(dest="model_command", required=True)

    p = model_sub.add_parser(
        "update",
        help="regenerate P1M-E machine, SFR, and product projections",
    )
    p.set_defaults(func=cmd_machine_model, check=False)

    p = model_sub.add_parser(
        "check",
        help="fail if generated P1M-E projections are stale",
    )
    p.set_defaults(func=cmd_machine_model, check=True)

    test = sub.add_parser(
        "test",
        help="exercise a payload, CodeFlash image, or exact firmware scenario",
    )
    test_sub = test.add_subparsers(dest="test_kind", required=True)

    p = test_sub.add_parser(
        "payload",
        help="build sources or load an ELF, execute to --stop, and verify postconditions",
    )
    p.add_argument("inputs", nargs="+", type=Path, metavar="INPUT")
    p.add_argument(
        "--linker-script", type=Path,
        help="compile INPUT sources with this linker script before testing the resulting ELF",
    )
    p.add_argument(
        "--output-dir", type=Path,
        help="retain build output, exact ELF, execution log, and verdict (default: unique build/out directory)",
    )
    _execution_arguments(p)
    p.set_defaults(func=cmd_sim)

    p = test_sub.add_parser(
        "codeflash",
        help="run a raw or byte-pinned CodeFlash image in the GNU simulator",
    )
    p.add_argument("image", type=Path)
    p.add_argument(
        "--spec",
        type=Path,
        help="optional strict execution contract for a known image",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        help="retain the modeled image, ELF, overlay audit, and simulator output",
    )
    p.add_argument(
        "--load",
        action="append",
        default=[],
        metavar="ADDRESS=PATH",
        help="load a raw RAM artifact at an exact address; repeat as needed",
    )
    p.add_argument(
        "--base",
        dest="image_base",
        type=lambda value: int(value, 0),
        help="CodeFlash base without --spec (default: 0)",
    )
    p.add_argument(
        "--entry",
        type=lambda value: int(value, 0),
        help="entry address without --spec (default: CodeFlash base)",
    )
    _execution_arguments(p)
    p.set_defaults(func=cmd_codeflash_sim)

    p = test_sub.add_parser(
        "firmware",
        help="run checked scenarios against exact registered P1M-E firmware",
    )
    p.add_argument("target", help="registered analysis target")
    p.add_argument(
        "scenarios",
        nargs="+",
        type=Path,
        help="machine scenario JSON files",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        help="write one execution report per scenario",
    )
    p.set_defaults(func=cmd_machine_run)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except (Rh850ToolError, OSError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
