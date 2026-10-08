#!/usr/bin/env python3
"""Exercise source-to-verified-result behavior through the public RH850 CLI."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from tools import REPO_ROOT

CLI = REPO_ROOT / "tools/rh850"


def invoke(cwd: Path, *args: str, success: bool = True, error: str = "") -> str:
    proc = subprocess.run(
        [str(CLI), "test", "payload", *args], cwd=cwd,
        text=True, capture_output=True, timeout=150, check=False,
    )
    output = proc.stdout + proc.stderr
    if (proc.returncode == 0) != success:
        raise AssertionError(f"unexpected exit {proc.returncode}: {args}\n{output}")
    if error and error not in output:
        raise AssertionError(f"missing diagnostic {error!r}\n{output}")
    if not success and "Payload test: PASS" in output:
        raise AssertionError(f"failed run reported success\n{output}")
    return output


def main() -> int:
    # Outside the repository, including spaces, to exercise caller-relative inputs.
    with tempfile.TemporaryDirectory(prefix="rh850 payload ") as td:
        work = Path(td)
        (work / "offset.h").write_text("#define OFFSET 8u\n", encoding="utf-8")
        (work / "compute.c").write_text(
            '#include "offset.h"\nunsigned compute(unsigned x) { return x + OFFSET; }\n',
            encoding="utf-8",
        )
        (work / "entry.S").write_text(
            "    .section .text\n    .global _start\n_start:\n"
            "    mov 0x12345670, r6\n    jarl _compute, lp\n"
            "    mov 0x200, r11\n    st.w r10, 0[r11]\n"
            "    .global payload_stop\npayload_stop:\n    add 1, r12\n    br payload_stop\n"
            "    .global unreachable_stop\nunreachable_stop:\n    br unreachable_stop\n"
            '    .section .result,"aw"\n    .long 0\n', encoding="utf-8",
        )
        (work / "layout.ld").write_text(
            "SECTIONS { . = 0x100; .text : { *(.text) } "
            ". = 0x200; .result : { *(.result) } }\nENTRY(_start)\n", encoding="utf-8",
        )
        predicate = "*(unsigned int *)0x200 == 0x12345678"
        contract = ("--stop", "payload_stop", "--assert", predicate)
        invoke(
            work, "entry.S", "compute.c", "--linker-script", "layout.ld",
            "--output-dir", "result", *contract,
        )
        report = json.loads((work / "result/report.json").read_text())
        elf = work / "result/payload.elf"
        assert report["status"] == "passed"
        assert report["elf_sha256"] == hashlib.sha256(elf.read_bytes()).hexdigest()
        assert "RH850_CHECK_1=1" in (work / "result/output.txt").read_text()
        print("PASS caller-relative C/assembly build, exact ELF execution, and checked result")

        retained = ("result/payload.elf", "--output-dir", "rerun")
        invoke(work, *retained, success=False, error="requires --stop")
        invoke(work, *retained, "--stop", "payload_stop", success=False, error="requires a postcondition")
        invoke(work, *retained, "--stop", "0x100", "--assert", predicate,
               success=False, error="stop equals entry")
        invoke(work, *retained, "--stop", "payload_stop", "--assert", "*(unsigned int *)0x200 == 7",
               success=False, error="postcondition 1 failed")
        assert json.loads((work / "rerun/report.json").read_text())["status"] == "failed"
        invoke(work, *retained, *contract, "-ex", "starti",
               success=False, error="must execute run or continue")
        invoke(work, *retained, *contract, "-ex", "break *0x100", "-ex", "run",
               success=False, error="unexpected stop")
        invoke(work, *retained, "--stop", "unreachable_stop", "--assert", predicate,
               "--timeout", "0.2", success=False, error="timed out")
        print("PASS load-only, entry-only, false predicate, wrong stop, and nonterminating execution rejected")

        # A failed rebuild must not test the previous successful ELF or retain its verdict.
        (work / "compute.c").write_text("not valid C\n", encoding="utf-8")
        invoke(
            work, "entry.S", "compute.c", "--linker-script", "layout.ld",
            "--output-dir", "result", *contract, success=False, error="payload build failed",
        )
        failed = json.loads((work / "result/report.json").read_text())
        assert failed["status"] == "failed" and "elf_sha256" not in failed
        print("PASS failed rebuild cannot reuse a previous passing result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
