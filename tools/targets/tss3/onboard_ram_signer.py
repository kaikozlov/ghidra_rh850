#!/usr/bin/env python3
"""Resolve, build, and simulate the TSS3 request signer from one CodeFlash dump."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from exploit.ephemeral_runtime import build_tss3_request_signer as builder
from exploit.ram_runtime.tss3_request_signer_contract import HELPER_TRANSIT_BASE
from tools import REPO_ROOT
from tools.rh850_codeflash import (
    Overlay,
    Spec,
    run_elf,
)
from tools.rh850_codeflash import (
    run as run_codeflash_sim,
)
from tools.security.build_ephemeral_runtime_manifest import is_jarl22, jarl22_target

ROOT = REPO_ROOT
CACHE_PUBLICATION = bytes.fromhex("1f001c00")  # syncp; synci
HARNESS_ADDRESS = 0xFEF00000
CONTEXT_MARKER = 0xFEF01000
STARTUP_MARKER = 0xFEF01004
SIM_MEMORY_REGIONS = (
    "0xFEBE0000,0x20000",
    "0xFEF00000,0x20000",
    "0xFFFFB000,0x1000",
    "0xFFE50000,0x1000",
)


def _require_empty(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise RuntimeError(f"refusing nonempty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)




def _return_section(name: str) -> str:
    return f"    .section .sim.overlay.{name},\"ax\"\n    jmp [lp]\n"


def _build_harness_source(contract: dict[str, Any], image: bytes) -> tuple[str, tuple[Overlay, ...]]:
    execution = contract["execution"]
    gp = execution["gp"]
    tp = execution["tp"]
    sections: list[str] = [
        (
            "    .section .sim.harness,\"ax\"\n"
            "    .global codeflash_sim_start\n"
            "codeflash_sim_start:\n"
            "    mov 0xfebe2000, sp\n"
            "    jr32 exploit_entry\n\n"
            "    .global codeflash_sim_stop\n"
            "codeflash_sim_stop:\n"
            "    br codeflash_sim_stop\n\n"
            "    .equ exploit_entry, 0xfebf0000\n"
        )
    ]
    overlays: list[Overlay] = []
    occupied: set[int] = set()

    def add_return(address: int, name: str) -> None:
        if address in occupied:
            return
        occupied.add(address)
        section = f".sim.overlay.{name}"
        sections.append(_return_section(name))
        overlays.append(Overlay(section=section, address=address, expected=image[address:address + 2]))

    for index, address in enumerate(contract["boot_calls"][:-1]):
        add_return(address, f"boot_{index}_{address:06x}")

    validity = contract["boot_calls"][-1]
    occupied.add(validity)
    sections.append(
        "    .section .sim.overlay.boot_validity,\"ax\"\n"
        "    mov 0, r10\n"
        "    jmp [lp]\n"
    )
    overlays.append(Overlay(
        section=".sim.overlay.boot_validity",
        address=validity,
        expected=image[validity:validity + 4],
    ))

    context = execution["app_context"]
    occupied.add(context)
    sections.append(
        "    .section .sim.overlay.context,\"ax\"\n"
        f"    mov 0x{gp:08x}, gp\n"
        f"    mov 0x{tp:08x}, tp\n"
        "    mov 0xfebe2000, sp\n"
        "    mov 0x43545831, r10\n"
        f"    mov 0x{CONTEXT_MARKER:08x}, r11\n"
        "    st.w r10, 0[r11]\n"
        "    jmp [lp]\n"
    )
    overlays.append(Overlay(
        section=".sim.overlay.context",
        address=context,
        expected=image[context:context + 36],
    ))

    for offset in range(execution["startup_first"], execution["startup_after"], 4):
        if is_jarl22(image, offset):
            add_return(jarl22_target(image, offset), f"startup_{offset:06x}")

    startup_final = execution["startup_final"]
    if startup_final in occupied:
        raise RuntimeError("startup-final target overlaps another modeled call")
    occupied.add(startup_final)
    sections.append(
        "    .section .sim.overlay.startup_final,\"ax\"\n"
        "    mov 0x53544152, r10\n"
        f"    mov 0x{STARTUP_MARKER:08x}, r11\n"
        "    st.w r10, 0[r11]\n"
        "    jmp [lp]\n"
    )
    overlays.append(Overlay(
        section=".sim.overlay.startup_final",
        address=startup_final,
        expected=image[startup_final:startup_final + 18],
    ))

    for index, address in enumerate(execution["foreground_calls"]):
        add_return(address, f"foreground_{index}_{address:06x}")
    return "\n".join(sections), tuple(overlays)


def _sim_spec(
    *,
    assembly: Path,
    digest: str,
    overlays: tuple[Overlay, ...],
    gdb: tuple[str, ...],
) -> Spec:
    return Spec(
        assembly=assembly,
        codeflash_size=0x100000,
        harness_address=HARNESS_ADDRESS,
        image_sha256=frozenset((digest,)),
        memory_regions=SIM_MEMORY_REGIONS,
        gdb=gdb,
        loads=((builder.STAGING_BASE, builder.STAGING_LIMIT),),
        overlays=overlays,
    )


def simulate_candidate(
    *,
    image_path: Path,
    contract: dict[str, Any],
    metadata: dict[str, Any],
    staging_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    source, overlays = _build_harness_source(contract, image)
    harness = output_dir / "universal_request_signer_sim.S"
    harness.parent.mkdir(parents=True, exist_ok=True)
    harness.write_text(source, encoding="utf-8")

    staging = staging_path.read_bytes()
    if staging.count(CACHE_PUBLICATION) != 2:
        raise RuntimeError("request-signer staging no longer contains two cache-publication sequences")
    simulator_staging = output_dir / "request_signer_simulator.bin"
    simulator_staging.write_bytes(staging.replace(CACHE_PUBLICATION, b"\0" * 4))

    state = contract["runtime_config"]["state_base"]
    producer = contract["runtime_config"]["ring_producer"]
    tick = contract["execution"]["tick_counter"]
    tick_wait = int(metadata["resident"]["tick_wait"], 0)
    resident_handoff = int(metadata["staging"]["resident_handoff"], 0)
    digest = contract["codeflash_sha256"]
    load = ((builder.STAGING_BASE, simulator_staging),)

    fallback_expected = (
        "UNIVERSAL_DUMP_FALLBACK "
        f"STATE=0x{builder.STATE_MAGIC:x} VERSION={builder.STATE_VERSION} INIT=1 TICK=1 "
        "CONTEXT=0x43545831 STARTUP=0x53544152"
    )
    fallback_gdb = (
        "set {unsigned char}0xFFFFB111 = 0x10",
        f"set {{unsigned char}}0x{tick:08X} = 0",
        f"set {{unsigned short}}0x{producer:08X} = 0",
        f"set {{unsigned int}}0x{CONTEXT_MARKER:08X} = 0",
        f"set {{unsigned int}}0x{STARTUP_MARKER:08X} = 0",
        f"break *0x{resident_handoff:08X}",
        "run",
        f"break *0x{HELPER_TRANSIT_BASE:08X}",
        "continue",
        (
            f'printf "UNIVERSAL_DUMP_FALLBACK STATE=0x%x VERSION=%u INIT=%u TICK=%u '
            f'CONTEXT=0x%x STARTUP=0x%x\\n", *(unsigned int *)0x{state:08X}, '
            f'*(unsigned char *)0x{state + 4:08X}, *(unsigned char *)0x{state + 5:08X}, '
            f'*(unsigned char *)0x{tick:08X}, *(unsigned int *)0x{CONTEXT_MARKER:08X}, '
            f'*(unsigned int *)0x{STARTUP_MARKER:08X}'
        ),
    )
    fallback_output, runtime_elf = run_codeflash_sim(
        root=ROOT,
        image_path=image_path,
        spec=_sim_spec(assembly=harness, digest=digest, overlays=overlays, gdb=fallback_gdb),
        ram_loads=load,
        expected_output=(fallback_expected,),
        output_dir=output_dir / "runtime",
    )

    idle_expected = (
        "UNIVERSAL_DUMP_IDLE "
        f"STATE=0x{builder.STATE_MAGIC:x} VERSION={builder.STATE_VERSION} INIT=1 TICK=0 "
        "COUNTER=300000 CONTEXT=0x43545831 STARTUP=0x53544152"
    )
    idle_gdb = (
        "set {unsigned char}0xFFFFB111 = 0x10",
        f"set {{unsigned char}}0x{tick:08X} = 0",
        f"set {{unsigned short}}0x{producer:08X} = 0",
        f"set {{unsigned int}}0x{CONTEXT_MARKER:08X} = 0",
        f"set {{unsigned int}}0x{STARTUP_MARKER:08X} = 0",
        f"break *0x{resident_handoff:08X}",
        "run",
        f"break *0x{tick_wait:08X}",
        "continue",
        "set {unsigned char}0xFFFFB111 = 0",
        f"set {{unsigned short}}0x{producer:08X} = 5",
        "set {unsigned int}0xFFE5001C = 300000",
        f"break *0x{HELPER_TRANSIT_BASE:08X}",
        "continue",
        (
            f'printf "UNIVERSAL_DUMP_IDLE STATE=0x%x VERSION=%u INIT=%u TICK=%u '
            f'COUNTER=%u CONTEXT=0x%x STARTUP=0x%x\\n", *(unsigned int *)0x{state:08X}, '
            f'*(unsigned char *)0x{state + 4:08X}, *(unsigned char *)0x{state + 5:08X}, '
            f'*(unsigned char *)0x{tick:08X}, *(unsigned int *)0xFFE5001C, '
            f'*(unsigned int *)0x{CONTEXT_MARKER:08X}, *(unsigned int *)0x{STARTUP_MARKER:08X}'
        ),
    )
    if runtime_elf is None:
        raise RuntimeError("retained simulator ELF is missing")
    idle_output = run_elf(
        root=ROOT,
        elf_path=runtime_elf,
        memory_regions=SIM_MEMORY_REGIONS,
        gdb_commands=idle_gdb,
        expected_output=(idle_expected,),
        output_path=output_dir / "idle-output.txt",
    )
    elf_path = str(runtime_elf.relative_to(output_dir.parent))
    return {
        "passed": True,
        "harness": str(harness.relative_to(output_dir.parent)),
        "elf": elf_path,
        "fallback": {
            "expected": fallback_expected,
            "output_sha256": hashlib.sha256(fallback_output.encode()).hexdigest(),
        },
        "idle_fast": {
            "expected": idle_expected,
            "output_sha256": hashlib.sha256(idle_output.encode()).hexdigest(),
        },
        "proof_boundary": (
            "instruction execution and modeled startup/foreground transitions only; "
            "ICU-S, RSCFD, MPU enforcement, cache publication, interrupts, and timing remain unmodeled"
        ),
    }


def _default_output(identity: str, digest: str) -> Path:
    root = ROOT / "build/out/ram-runtime/onboard"
    root.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=f"{identity}-{digest[:12]}-", dir=root))


def onboard(image_path: Path, output_dir: Path | None = None) -> tuple[dict[str, Any], int]:
    image_path = image_path.resolve()
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    out = output_dir.resolve() if output_dir is not None else _default_output("dump", digest)
    if output_dir is not None:
        _require_empty(out)

    build_dir = out / "build"
    command = [
        sys.executable,
        str(builder.BUILDER),
        "--codeflash",
        str(image_path),
        "--output-dir",
        str(build_dir),
        "--output-stem",
        "resolved_request_signer",
    ]
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    profile_path = build_dir / "resolved_request_signer_profile.json"
    if proc.returncode != 0:
        status = (
            "candidate-build-failed"
            if profile_path.is_file()
            else "not-proven-compatible"
        )
        report = {
            "schema": "tss3-request-signer-onboarding-v1",
            "codeflash": {"path": str(image_path), "sha256": digest, "size": len(image)},
            "status": status,
            "reason": proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "candidate build failed",
            "build": {"passed": False},
            "simulation": None,
            "output_directory": str(out),
        }
        (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return report, 1

    metadata = json.loads(proc.stdout)
    metadata_path = build_dir / "resolved_request_signer.json"
    contract = json.loads(profile_path.read_text(encoding="utf-8"))
    identity = contract["identity"]
    verdict = metadata["compatibility"]
    report: dict[str, Any] = {
        "schema": "tss3-request-signer-onboarding-v1",
        "codeflash": {"path": str(image_path), "sha256": digest, "size": len(image)},
        "identity": identity,
        **verdict,
        "resolved_profile": str(profile_path.relative_to(out)),
        "output_directory": str(out),
        "build": {
            "passed": True,
            "profile_action": (
                "already-present"
                if verdict["status"] == "covered-by-current-build"
                else "added-to-candidate-build"
            ),
            "metadata": str(metadata_path.relative_to(out)),
            "staging": metadata["staging"],
            "authenticated_payload": metadata["authenticated_payload"],
        },
        "simulation": None,
        "deployment": {
            "ready": False,
            "reason": "offline compatibility cannot derive Panda logical bus or prove ICU-S/RSCFD behavior",
            "next_check": (
                "observe the EPS diagnostic/request buses, register the resolved hash/F181/buses, "
                "package the target kit, then run one parked install/status/self-test/benchmark-100hz session"
            ),
        },
    }
    try:
        report["simulation"] = simulate_candidate(
            image_path=image_path,
            contract=contract,
            metadata=metadata,
            staging_path=build_dir / metadata["staging"]["path"],
            output_dir=out / "simulation",
        )
    except (OSError, RuntimeError) as exc:
        report["status"] = "simulation-failed"
        report["reason"] = str(exc)
        report["simulation"] = {"passed": False, "reason": str(exc)}
        (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return report, 1
    (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report, 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("codeflash", type=Path)
    parser.add_argument("--out", type=Path, help="empty output directory; default creates a unique build/out result")
    args = parser.parse_args()
    try:
        report, status = onboard(args.codeflash, args.out)
    except (OSError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
