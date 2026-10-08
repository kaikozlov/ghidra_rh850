#!/usr/bin/env python3
"""Build and test RH850 payloads and firmware with the pinned toolchain."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
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
        raise Rh850ToolError("exec requires a command")
    base = _container_base(
        writable=args.work_dir is None,
        work_dir=args.work_dir,
    )
    return _run(base + command).returncode


def _container_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(ROOT)
    except ValueError as exc:
        message = f"sim ELF must be inside the repository: {resolved}"
        raise Rh850ToolError(message) from exc
    return "/src/" + relative.as_posix()


def cmd_sim(args: argparse.Namespace) -> int:
    _require_image()
    elf = args.elf
    if not elf.is_absolute():
        elf = ROOT / elf
    if not elf.is_file():
        raise Rh850ToolError(f"ELF does not exist: {elf}")

    target = "target sim --architecture v850e3v5"
    for region in args.memory_region:
        target += f" --memory-region {region}"

    gdb_args = [
        "v850-elf-gdb",
        "-q",
        "-batch",
        "-ex",
        f"file {_container_path(elf)}",
        "-ex",
        target,
        "-ex",
        "load",
    ]
    for command in args.gdb_command:
        gdb_args += ["-ex", command]
    return _run(_container_base(writable=False) + gdb_args).returncode


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

    image = args.image if args.image.is_absolute() else ROOT / args.image
    output_dir = args.output_dir
    if output_dir is not None and not output_dir.is_absolute():
        output_dir = ROOT / output_dir

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
        loads[address] = Path(raw_path)

    spec = None
    if args.spec is not None:
        if args.image_base is not None or args.entry is not None:
            raise Rh850ToolError("--base and --entry cannot override a spec")
        spec_path = args.spec if args.spec.is_absolute() else ROOT / args.spec
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
        help="run a linked payload ELF in the GNU instruction simulator",
    )
    p.add_argument("elf", type=Path)
    p.add_argument(
        "--memory-region",
        action="append",
        default=[],
        metavar="BASE,SIZE",
        help="simulator RAM/flash mapping; repeat as needed",
    )
    p.add_argument(
        "--command",
        "-ex",
        dest="gdb_command",
        action="append",
        default=[],
        help="GDB command to execute after load; repeat as needed",
    )
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
        "--expect",
        dest="expected_output",
        action="append",
        default=[],
        help="require a string in simulator output; repeat as needed",
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
    p.add_argument(
        "--memory-region",
        action="append",
        default=[],
        metavar="BASE,SIZE",
        help="additional simulator memory mapping; repeat as needed",
    )
    p.add_argument(
        "--command",
        "-ex",
        dest="gdb_command",
        action="append",
        default=[],
        help="GDB command after load; repeat as needed",
    )
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
    except (Rh850ToolError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
