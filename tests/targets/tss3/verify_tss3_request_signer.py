#!/usr/bin/env python3
"""Verify the dump-resolved universal TSS3 RAM-resident request signer."""
from __future__ import annotations

import io
import json
import struct
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import mock

import tools.targets.tss3.builders.build_tss3_request_signer as build
import tsk.ram_runtime.tss3_request_signer as host
from tools import REPO_ROOT
from tsk.common.payload_package import inspect_payload
from tsk.common.rh850_build import CJob
from tsk.ram_runtime.target_profiles import registered_specs, spec_from_codeflash
from tsk.ram_runtime.tss3_request_signer_contract import (
    ContractError,
    probe_request_signer_contract,
    resolve_request_signer_contract,
)

ROOT = REPO_ROOT

CAMRY_TARGET = "camry-8965F3307000"
SPECS = registered_specs()
SIENNA_TARGET = "sienna-8965B4512000"
SIENNA_IMAGE = ROOT / "firmware/RH850_P1M-E_CodeFlash.bin"
SIENNA_CONTRACT = resolve_request_signer_contract(SIENNA_IMAGE.read_bytes())
RESOLUTION_SPECS: dict[str, dict[str, Any]] = {
    **SPECS,
    SIENNA_TARGET: {
        "image": SIENNA_IMAGE,
        "sha256": SIENNA_CONTRACT["codeflash_sha256"],
        "contract": SIENNA_CONTRACT,
    },
}
BUILD_TEMP = tempfile.TemporaryDirectory(prefix="verify-tss3-request-signer-")
BUILD_ROOT = Path(BUILD_TEMP.name)
OUT = BUILD_ROOT / "default"

meta = build.build_request_signer(target=CAMRY_TARGET, output_dir=OUT)
meta_path = OUT / "camry_8965F3307000_request_signer.json"



def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")
for artifact_name in ("resident", "helper"):
    artifact_meta = meta[artifact_name]
    artifact = (OUT / artifact_meta["path"]).read_bytes()
    check_name = f"{artifact_name} artifact carries an explicit speculative-fetch guard"
    check(
        check_name,
        artifact_meta["size"] == len(artifact)
        and artifact_meta["guard_size"] == build.SPECULATIVE_FETCH_GUARD_SIZE
        and artifact_meta["code_size"] + artifact_meta["guard_size"] <= len(artifact)
        and artifact[-artifact_meta["guard_size"]:] == bytes(artifact_meta["guard_size"]),
    )
try:
    build.validate_cmp_immediates("cmp 0xc9, r6\n", label="regression fixture")
except RuntimeError:
    pass
else:
    raise AssertionError("builder accepted an out-of-range RH850 cmp immediate")
print("PASS builder rejects GNU-as truncation of RH850 cmp immediates")
real_compile_c_batch = build.compile_c_batch


def _resident_with_unwind_tables(
    work: Path, jobs: Sequence[CJob],
) -> list[dict[str, object]]:
    """Delegate to the real compiler; append unwind tables to the resident only.

    Unwind tables are the one-flag delta that re-enables the V850 noreturn
    save prologue, so the resident genuinely reports retained own frames.
    """
    return real_compile_c_batch(work, tuple(
        replace(job, extra_cflags=(*job.extra_cflags, "-funwind-tables"))
        if job.stem == "resident" else job
        for job in jobs
    ))


over_budget_dir = BUILD_ROOT / "over-budget-resident"
with mock.patch.object(build, "compile_c_batch", _resident_with_unwind_tables):
    try:
        build.build_request_signer(target=CAMRY_TARGET, output_dir=over_budget_dir)
    except RuntimeError as exc:
        over_budget_rejection = str(exc)
    else:
        raise AssertionError("builder accepted a genuinely compiled stack-using resident")
check(
    "builder rejects a genuinely compiled over-budget resident before packaging",
    over_budget_rejection.startswith("resident: own stack exceeds budget:")
    and over_budget_rejection.endswith("> 0")
    and not any(over_budget_dir.glob("*.bin"))
    and not any(over_budget_dir.glob("*_request_signer.json")),
)
check(
    "Sienna identity follows the application F181 callback",
    SIENNA_CONTRACT["identity"]["f181_callback"] == 0x0004E8E4
    and SIENNA_CONTRACT["identity"]["f181_records"] == ["8965B4512000"]
    and SIENNA_CONTRACT["identity"]["runtime_software_id_address"] == 0x00020860
    and SIENNA_CONTRACT["identity"]["application_f181_hex"]
        == "0138393635423435313230303000000000",
)

sienna_relocated_identity = bytearray(SIENNA_IMAGE.read_bytes())
sienna_identity = SIENNA_CONTRACT["identity"]
sienna_old_record = int(sienna_identity["runtime_software_id_address"])
sienna_new_record = next(
    offset
    for offset in range(0x8000, 0x10000, 2)
    if sienna_relocated_identity[offset:offset + 16] == b"\xff" * 16
)
sienna_relocated_identity[sienna_new_record:sienna_new_record + 16] = (
    sienna_relocated_identity[sienna_old_record:sienna_old_record + 16]
)
sienna_relocated_identity[sienna_old_record:sienna_old_record + 16] = b"\xff" * 16
sienna_f181_callback = int(sienna_identity["f181_callback"])
struct.pack_into("<H", sienna_relocated_identity, sienna_f181_callback + 10, sienna_new_record >> 16)
struct.pack_into(
    "<H", sienna_relocated_identity, sienna_f181_callback + 20,
    (sienna_new_record & 0xFFFF) | 1,
)
sienna_relocated_contract = resolve_request_signer_contract(bytes(sienna_relocated_identity))
check(
    "F181 resolution follows a relocated callback source instead of a fixed address",
    sienna_relocated_contract["identity"]["runtime_software_id_address"] == sienna_new_record
    and sienna_relocated_contract["identity"]["application_f181_hex"]
        == SIENNA_CONTRACT["identity"]["application_f181_hex"],
)

synthetic_image = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
old_selector = SPECS[CAMRY_TARGET]["runtime_software_id"].encode("ascii")
new_selector = b"8965F3307999"
if synthetic_image.count(old_selector) != 1:
    raise AssertionError("Camry selector identity is not unique")
selector_offset = synthetic_image.find(old_selector)
synthetic_image[selector_offset:selector_offset + len(old_selector)] = new_selector
synthetic_path = BUILD_ROOT / "synthetic-unknown-CodeFlash.bin"
synthetic_path.write_bytes(synthetic_image)
synthetic_spec = spec_from_codeflash(synthetic_path)
synthetic_out = BUILD_ROOT / "synthetic"
synthetic_meta = build.build_request_signer(
    codeflash=synthetic_path, output_dir=synthetic_out, stem="synthetic_request_signer",
)

reference_staging = (OUT / meta["staging"]["path"]).read_bytes()
reference_payload = (OUT / meta["authenticated_payload"]["path"]).read_bytes()
target_builds = {CAMRY_TARGET: (meta, OUT)}
for target in SPECS:
    if target == CAMRY_TARGET:
        continue
    target_out = BUILD_ROOT / f"target-{target}"
    target_builds[target] = (
        build.build_request_signer(target=target, output_dir=target_out),
        target_out,
    )
sienna_out = BUILD_ROOT / f"target-{SIENNA_TARGET}"
sienna_meta = build.build_request_signer(
    codeflash=SIENNA_IMAGE, output_dir=sienna_out, stem="sienna_request_signer",
)
target_builds[SIENNA_TARGET] = (sienna_meta, sienna_out)

for target, (target_meta, target_out) in target_builds.items():
    check(
        f"{target} build emits the identical self-resolving staging and payload",
        (target_out / target_meta["staging"]["path"]).read_bytes() == reference_staging
        and (target_out / target_meta["authenticated_payload"]["path"]).read_bytes()
            == reference_payload
        and target_meta["compatibility"]["status"] == "self-resolved-compatible"
        and target_meta["state"] == {
            "version": host.STATE_VERSION,
            "base": "0xFEBFF9F0",
            "size": host.STATE_SIZE,
            "layout": "resident-prefix-global-tail",
        },
    )

payload_plaintext = inspect_payload(
    reference_payload, secret=build.TOYOTA_P1ME_PAYLOAD_BUILD_SECRET,
).shellcode_region
helper_guard_start = (
    meta["staging"]["helper_offset"] + meta["helper"]["size"] - meta["helper"]["guard_size"]
)
check(
    "authenticated shell padding supplies the staged helper fetch guard",
    payload_plaintext[helper_guard_start:helper_guard_start + meta["helper"]["guard_size"]]
        == bytes(meta["helper"]["guard_size"]),
)


resolver_runner = BUILD_ROOT / "resolver-host"
subprocess.run([
    "cc", "-O2", "-Wall", "-Wextra", "-Werror",
    str(build.RESOLVER_SOURCE),
    str(ROOT / "tests/fixtures/rh850/tss3_request_signer_resolver_host.c"),
    "-o", str(resolver_runner),
], cwd=ROOT, check=True, text=True, timeout=30)


def run_resolver(image_path: Path) -> tuple[int, list[int]]:
    fields = subprocess.check_output(
        [str(resolver_runner), str(image_path)], text=True, timeout=30,
    ).split()
    return int(fields[0]), [int(value, 16) for value in fields[1:]]

CANONICAL_MEMORY = {
    "layout": "resident-prefix-global-tail",
    "state_base": 0xFEBFF9F0,
    "scratch_base": 0xFEF07F98,
}



for target, spec in RESOLUTION_SPECS.items():
    resolver_status, resolver_words = run_resolver(spec["image"])
    contract = spec["contract"]
    expected_words = [
        *contract["boot_calls"],
        *(contract["runtime_config"][name] for name in build.CONFIG_FIELDS),
    ]
    check(
        f"{target} on-device resolver reproduces the independent host contract",
        resolver_status == 0 and resolver_words == expected_words,
    )
    check(
        f"{target} uses the canonical payload-owned state and scratch layout",
        contract["schema"] == "tss3-request-signer-contract-v2"
        and contract["memory"] == CANONICAL_MEMORY
        and contract["runtime_config"]["state_base"] == CANONICAL_MEMORY["state_base"]
        and contract["runtime_config"]["scratch_base"] == CANONICAL_MEMORY["scratch_base"],
    )
synthetic_status, synthetic_words = run_resolver(synthetic_path)
camry_contract = SPECS[CAMRY_TARGET]["contract"]
check(
    "on-device resolution is independent of the unknown software identity",
    synthetic_status == 0
    and synthetic_words == [
        *camry_contract["boot_calls"],
        *(camry_contract["runtime_config"][name] for name in build.CONFIG_FIELDS),
    ],
)

route_shifted = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
class_route = camry_contract["signer_abi"]["class_route_table"]
route_shifted[class_route + 2] += 1
route_shifted_path = BUILD_ROOT / "resolver-shifted-class-route.bin"
route_shifted_path.write_bytes(route_shifted)
route_shifted_contract = resolve_request_signer_contract(bytes(route_shifted))
route_shifted_status, route_shifted_words = run_resolver(route_shifted_path)
check(
    "on-device response resolution follows the diagnostic class and resource tables",
    route_shifted_contract["signer_abi"]["response_handle"]
        != camry_contract["signer_abi"]["response_handle"]
    and route_shifted_status == 0
    and route_shifted_words == [
        *route_shifted_contract["boot_calls"],
        *(route_shifted_contract["runtime_config"][name] for name in build.CONFIG_FIELDS),
    ],
)
ring_resized = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
capacity_table = camry_contract["request"]["capacity_table"]
ring_resized[capacity_table:capacity_table + 2] = (0x224).to_bytes(2, "little")
ring_resized_path = BUILD_ROOT / "resolver-ring-resized.bin"
ring_resized_path.write_bytes(ring_resized)
ring_resized_contract = resolve_request_signer_contract(bytes(ring_resized))
ring_resized_status, ring_resized_words = run_resolver(ring_resized_path)
check(
    "ring geometry follows the firmware capacity table instead of a compiled literal",
    ring_resized_contract["request"]["ring_words"] == 0x224
    and ring_resized_contract["runtime_config"]["runtime_geometry"] & 0xFFFF == 0x224
    and ring_resized_contract["request"]["ring_base"]
        == camry_contract["request"]["ring_base"]
    and ring_resized_status == 0
    and ring_resized_words == [
        *ring_resized_contract["boot_calls"],
        *(ring_resized_contract["runtime_config"][name] for name in build.CONFIG_FIELDS),
    ],
)
ring_oversized = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
ring_oversized[capacity_table:capacity_table + 2] = (0x1001).to_bytes(2, "little")
try:
    resolve_request_signer_contract(bytes(ring_oversized))
except ContractError:
    pass
else:
    raise AssertionError("dump resolver accepted an out-of-range ring capacity")
print("PASS dump resolver rejects out-of-range ring capacity")

foreground_shifted = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
foreground = camry_contract["execution"]["foreground"]
foreground_displacement = struct.unpack_from("<h", foreground_shifted, foreground + 6)[0]
shifted_displacement = foreground_displacement + 2
struct.pack_into("<h", foreground_shifted, foreground + 6, shifted_displacement)
struct.pack_into("<h", foreground_shifted, foreground + 12, shifted_displacement)
foreground_shifted_path = BUILD_ROOT / "resolver-foreground-flag-shifted.bin"
foreground_shifted_path.write_bytes(foreground_shifted)
foreground_shifted_contract = resolve_request_signer_contract(bytes(foreground_shifted))
foreground_shifted_status, foreground_shifted_words = run_resolver(foreground_shifted_path)
expected_foreground_flag = shifted_displacement & 0xFFFFFFFF
check(
    "foreground flag address follows the stock test/clear displacement",
    foreground_shifted_contract["execution"]["foreground_flag"] == expected_foreground_flag
    and foreground_shifted_contract["execution"]["idle_fast"]["foreground_flag_address"]
        == expected_foreground_flag
    and foreground_shifted_contract["runtime_config"]["runtime_geometry"]
        == (camry_contract["request"]["ring_words"] | ((shifted_displacement & 0xFFFF) << 16))
    and foreground_shifted_status == 0
    and foreground_shifted_words == [
        *foreground_shifted_contract["boot_calls"],
        *(foreground_shifted_contract["runtime_config"][name] for name in build.CONFIG_FIELDS),
    ],
)
foreground_mismatched = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
struct.pack_into("<h", foreground_mismatched, foreground + 6, shifted_displacement)
foreground_mismatched_path = BUILD_ROOT / "resolver-foreground-flag-mismatched.bin"
foreground_mismatched_path.write_bytes(foreground_mismatched)
try:
    resolve_request_signer_contract(bytes(foreground_mismatched))
except ContractError:
    pass
else:
    raise AssertionError("dump resolver accepted mismatched foreground test/clear addresses")
check(
    "both resolvers reject mismatched foreground test/clear addresses",
    run_resolver(foreground_mismatched_path)[0] == -6,
)

command5_damaged = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
command5_address = SPECS[CAMRY_TARGET]["contract"]["signer_abi"]["command5_sync"]
command5_damaged[command5_address:command5_address + 16] = bytes(16)
command5_damaged_path = BUILD_ROOT / "resolver-command5-missing.bin"
command5_damaged_path.write_bytes(command5_damaged)

command5_duplicated = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
duplicate_address = next(
    address
    for address in range(0, len(command5_duplicated) - 16, 2)
    if command5_duplicated[address:address + 16] == b"\xff" * 16
)
command5_duplicated[duplicate_address:duplicate_address + 16] = (
    command5_duplicated[command5_address:command5_address + 16]
)
command5_duplicated_path = BUILD_ROOT / "resolver-command5-duplicated.bin"
command5_duplicated_path.write_bytes(command5_duplicated)

class_route_ambiguous = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
class_route = SPECS[CAMRY_TARGET]["contract"]["signer_abi"]["class_route_table"]
duplicate_address = next(
    address
    for address in range(0, len(class_route_ambiguous) - 6, 2)
    if class_route_ambiguous[address:address + 6] == b"\xff" * 6
)
class_route_ambiguous[duplicate_address:duplicate_address + 6] = (
    class_route_ambiguous[class_route:class_route + 6]
)
class_route_ambiguous_path = BUILD_ROOT / "resolver-class-route-ambiguous.bin"
class_route_ambiguous_path.write_bytes(class_route_ambiguous)

check(
    "on-device resolver fails closed on missing and ambiguous dependencies",
    run_resolver(command5_damaged_path)[0] == -2
    and run_resolver(command5_duplicated_path)[0] == -2
    and run_resolver(class_route_ambiguous_path)[0] == -11,
)

def run_core_simulator() -> None:
    import subprocess

    with tempfile.TemporaryDirectory(prefix="request-signer-core-sim-") as td:
        subprocess.run([
            str(ROOT / "tools/rh850"), "test", "payload",
            "tests/fixtures/rh850/tss3_request_signer_core_sim.S",
            "tests/fixtures/rh850/tss3_request_signer_core_sim.c",
            "--linker-script", "tests/fixtures/rh850/tss3_request_signer_core_sim.ld",
            "--output-dir", td,
            "--memory-region", "0xFEBF0000,0x10000",
            "--stop", "rh850_sim_stop",
            "--assert", "*(unsigned int *)&oracle_sim_result == 0x8a0c0de",
            "--assert", "*(unsigned int *)&oracle_sim_failure == 0",
        ], cwd=ROOT, check=True, text=True, timeout=150)


run_core_simulator()
print("PASS production C core executes and satisfies result checks")


application = bytes(range(28))
four_frames = host.build_request(application, 0xA7)
check("host transport preserves all application bytes in four exact frames",
      four_frames == (
          bytes.fromhex("8700010203040506"),
          bytes.fromhex("9a0708090a0b0c0d"),
          bytes.fromhex("a70e0f1011121314"),
          bytes.fromhex("ba15161718191a1b"),
      ) and
      b"".join(frame[1:] for frame in four_frames) == application and
      host.build_request(application, 0xA7) == four_frames)


check(
    "registered and unknown compatible dumps use the self-resolving payload",
    meta["compatibility"]["status"] == "self-resolved-compatible"
    and synthetic_meta["compatibility"]["status"] == "self-resolved-compatible"
    and synthetic_spec["runtime_software_id"] == new_selector.decode("ascii")
    and (synthetic_out / synthetic_meta["staging"]["path"]).read_bytes() == reference_staging
    and (synthetic_out / synthetic_meta["authenticated_payload"]["path"]).read_bytes()
        == reference_payload,
)
check(
    "Sienna dump build uses the shared self-resolving payload without deployment metadata",
    sienna_meta["target"]["application_f181_hex"]
        == SIENNA_CONTRACT["identity"]["application_f181_hex"]
    and sienna_meta["request"]["bus"] is None
    and sienna_meta["response"]["bus"] is None,
)
for target, spec in RESOLUTION_SPECS.items():
    image = spec["image"].read_bytes()
    probe = probe_request_signer_contract(image)
    check(
        f"{target} exposes every dynamically required signer component",
        probe["compatible"]
        and probe["contract"]["codeflash_sha256"] == spec["sha256"]
        and all(
            row["status"] == "resolved"
            for row in probe["components"].values()
        ),
    )
    shadow = probe["contract"]["execution"]["startup_shadow_copy"]
    check(
        f"{target} binds the startup shadow copy before the resident boundary",
        0 <= shadow["function"] < len(image)
        and shadow["source"] == 0x00010000
        and shadow["destination"] == 0xFEBF7C00
        and shadow["size"] == 0x7DF0
        and shadow["destination"] + shadow["size"] == CANONICAL_MEMORY["state_base"],
    )
    abi = probe["contract"]["signer_abi"]
    check(
        f"{target} resolves the target-native type1/selector4 command config",
        abi["command5_config_type"] == 1
        and abi["command5_selector"] == 4
        and image[abi["slot4_config"]:abi["slot4_config"] + 32]
            == bytes.fromhex("0100000004000000000000000000000000000000000000000000cc000f000000"),
    )
    route_pair = abi["route_map"] + abi["response_handle"] * 2
    check(
        f"{target} resolves the private response completion path to a no-op",
        image[route_pair:route_pair + 2]
            == bytes((abi["response_controller"], abi["response_resource"]))
        and 0 <= abi["lower_tx_completion"] < len(image) - 4
        and 0xFEBE0000 <= abi["response_confirmation_slot"] < 0xFEC00000
        and abi["software_confirmation_handle"] == 0x00F0
        and 0 <= abi["software_confirmation_dispatcher"] < len(image)
        and image[abi["software_confirmation_noop"]:abi["software_confirmation_noop"] + 2]
            == bytes.fromhex("7f00"),
    )

# CanIf class-2 HTH routing selects the primary 0x7A9 response independently of
# the count of unrelated transmit resources. Remove Camry's fifth resource to
# reproduce Crown's four-row topology; the primary diagnostic lower
# handle/resource must remain unchanged.
camry_contract = SPECS[CAMRY_TARGET]["contract"]
camry_abi = camry_contract["signer_abi"]
four_resource_image = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
row4 = camry_abi["resource_table"] + 4 * 10
four_resource_image[row4:row4 + 10] = b"\0" * 10
four_resource_path = BUILD_ROOT / "resolver-four-resource.bin"
four_resource_path.write_bytes(four_resource_image)
four_resource_contract = resolve_request_signer_contract(bytes(four_resource_image))
four_resource_status, four_resource_words = run_resolver(four_resource_path)
check(
    "primary diagnostic response routing is independent of optional fifth resource",
    four_resource_contract["signer_abi"]["resource_row_count"] == 4
    and four_resource_contract["signer_abi"]["response_handle"] == camry_abi["response_handle"]
    and four_resource_contract["signer_abi"]["response_resource"] == camry_abi["response_resource"]
    and four_resource_status == 0
    and four_resource_words == [
        *four_resource_contract["boot_calls"],
        *(four_resource_contract["runtime_config"][name] for name in build.CONFIG_FIELDS),
    ],
)

shadow_damaged_image = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
shadow_function = SPECS[CAMRY_TARGET]["contract"]["execution"]["startup_shadow_copy"]["function"]
shadow_damaged_image[shadow_function] ^= 1
shadow_damaged_probe = probe_request_signer_contract(bytes(shadow_damaged_image))
check(
    "capability probe rejects firmware without the exact startup shadow-copy boundary",
    not shadow_damaged_probe["compatible"]
    and shadow_damaged_probe["components"]["execution"]["status"] == "missing-or-ambiguous",
)


damaged_image = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
camry_contract = SPECS[CAMRY_TARGET]["contract"]
freshness_address = camry_contract["signer_abi"]["freshness_encode"]
damaged_image[freshness_address:freshness_address + 16] = b"\0" * 16
damaged_probe = probe_request_signer_contract(bytes(damaged_image))
check(
    "capability probe preserves independent results after signer ABI damage",
    not damaged_probe["compatible"]
    and damaged_probe["components"]["identity"]["status"] == "resolved"
    and damaged_probe["components"]["request"]["status"] == "resolved"
    and damaged_probe["components"]["signer_abi"]["status"] == "missing-or-ambiguous"
    and damaged_probe["components"]["memory"]["status"] == "resolved"
    and damaged_probe["components"]["memory"]["value"] == CANONICAL_MEMORY,
)
try:
    resolve_request_signer_contract(bytes(damaged_image))
except ContractError:
    pass
else:
    raise AssertionError("dump resolver accepted firmware without the signer freshness primitive")
print("PASS dump resolver rejects firmware with an unresolved signer ABI")

check(
    "generated transport satisfies the host metadata contract",
    host.meta_transport(meta)["codec"] == "four-frame",
)
try:
    host.meta_transport({
        "request": {"can_id": "0x1FDC0002", "bus": 0, "carrier": "raw-extended"},
        "response": {"can_id": "0x1FE00002", "bus": 0},
    })
except host.RequestSignerError:
    pass
else:
    raise AssertionError("host accepted an unsupported request carrier")
print("PASS host rejects unsupported request carriers")
resp = host.parse_response(bytes.fromhex("c90700f8d64e2a5e"), expected_seq=0x07)
check("host response decoder matches resident layout",
      resp.seq == 0x07 and resp.status == 0 and resp.trailer == bytes.fromhex("d64e2a5e"))


class _FakeProbePanda:
    def __init__(self, *, safety_mode=host.ELM327_SAFETY_MODE, safety_param=1,
                 respond=True, receipt_offset=host.TX_RECEIPT_ACCEPTED_BUS_OFFSET):
        self.request_count = 0
        self.rx: list[tuple[int, bytes, int]] = []
        self.safety_modes: list[tuple[int, int]] = []
        self.health_state = {"safety_mode": safety_mode, "safety_param": safety_param}
        self.respond = respond
        self.receipt_offset = receipt_offset

    def health(self):
        return dict(self.health_state)

    def get_version(self):
        return "DEV-92eb5651-DEBUG"

    def get_signature(self):
        return b"\xA5" * 128

    def up_to_date(self, fn=None):
        return True

    def set_safety_mode(self, mode, param=0):
        self.safety_modes.append((int(mode), int(param)))

    def can_send_many(self, frames):
        self.request_count += 1
        for frame in frames:
            self.rx.append((int(frame[0]), b"", int(frame[2]) + self.receipt_offset))
        if not self.respond:
            return
        data = [bytes(frame[1]) for frame in frames]
        seq = (data[0][0] & 0x0F) | ((data[1][0] & 0x0F) << 4)
        self.rx.append((0x7A9, bytes((0xC9, seq, 0x00, seq ^ 0xFF, 0x10 | (self.request_count & 0x0F), seq, 0xA5, 0x5A)), 0))

    def can_recv(self):
        rows, self.rx = self.rx, []
        return rows

    def close(self):
        pass


fake_probe_panda = _FakeProbePanda()
with (mock.patch.object(host, "load_security_secret", return_value=(b"\x00" * 16, "test")),
      mock.patch.object(host, "execute_ram_payload", return_value={"direct_bootloader": True}) as execute,
      mock.patch.object(host, "wait_for_f181", return_value={"ok": True}) as wait_for_application):
    direct = host.install(
        OUT / meta["authenticated_payload"]["path"], meta_path,
        direct_boot=True, panda=fake_probe_panda,
    )
check("post-activation install success is proved by the signer response",
      direct["entry_condition"] == "exact_bootloader_f181" and
      direct["verdict"] == "request_signer_live_probe_pass" and
      fake_probe_panda.request_count == 1 and
      execute.call_args.kwargs["allow_direct_boot"] is True and
      execute.call_args.kwargs["programming_already_requested"] is True and
      wait_for_application.call_count == 1 and
      wait_for_application.call_args.kwargs["expected_f181_hex"] == meta["target"]["application_f181_hex"] and
      fake_probe_panda.safety_modes[-1] == (host.ELM327_SAFETY_MODE, 1))

check("successful probe records the active safety mode and accepted TX receipts",
      direct["signer_session"]["safety_mode_ok"] is True and
      direct["signer_session"]["safety_mode_reported"] == host.ELM327_SAFETY_MODE and
      direct["signer_session"]["tx_receipts_accepted"] == 4 and
      direct["signer_session"]["tx_receipts_rejected"] == 0 and
      direct["signer_session"]["panda_version"] == "DEV-92eb5651-DEBUG")

silent_panda = _FakeProbePanda(safety_mode=0, safety_param=0, respond=False,
                               receipt_offset=host.TX_RECEIPT_REJECTED_BUS_OFFSET)
fake_resident_state = {
    "magic": f"0x{host.STATE_MAGIC:08X}", "magic_ok": True,
    "version": host.STATE_VERSION, "version_ok": True, "initialized": True,
    "request_count": 0, "success_count": 0, "response_count": 0,
}
with (mock.patch.object(host, "load_security_secret", return_value=(b"\x00" * 16, "test")),
      mock.patch.object(host, "execute_ram_payload", return_value={"direct_bootloader": True}),
      mock.patch.object(host, "wait_for_f181", return_value={"ok": True}),
      mock.patch.object(host, "read_resident_state", return_value=fake_resident_state) as read_state,
      mock.patch.object(host, "SIGNER_PROBE_TIMEOUT_SECONDS", 0.25)):
    silent = host.install(
        OUT / meta["authenticated_payload"]["path"], meta_path,
        direct_boot=True, panda=silent_panda,
    )
check("failed probe still records the silent safety fallback and rejected TX receipts",
      silent["verdict"] == "application_live_but_request_signer_probe_failed" and
      silent["signer_session"]["safety_mode_ok"] is False and
      silent["signer_session"]["safety_mode_reported"] == 0 and
      silent["signer_session"]["tx_receipts_accepted"] == 0 and
      silent["signer_session"]["tx_receipts_rejected"] > 0)
check("failed probe retains target-bound resident state readback",
      read_state.call_count == 1 and
      read_state.call_args.args[0]["state"]["base"] == meta["state"]["base"] and
      read_state.call_args.args[1] is silent_panda and
      silent["resident_state_after_probe"] == fake_resident_state)

class _FakeStateUdsClient:
    def __init__(self, *_args, **_kwargs):
        self.sessions = []
        self.requests = []

    def diagnostic_session_control(self, session):
        self.sessions.append(session)

    def _uds_request(self, service, *, data):
        self.requests.append((service, bytes(data)))
        raw = bytearray(host.STATE_SIZE)
        raw[0:4] = host.STATE_MAGIC.to_bytes(4, "little")
        raw[4] = host.STATE_VERSION
        raw[5] = 1
        raw[8:12] = (7).to_bytes(4, "little")
        raw[12:16] = (6).to_bytes(4, "little")
        raw[16:20] = (5).to_bytes(4, "little")
        return bytes(raw)


fake_state_client = _FakeStateUdsClient()
fake_uds_module = SimpleNamespace(
    UdsClient=lambda *_a, **_k: fake_state_client,
    SESSION_TYPE=SimpleNamespace(EXTENDED_DIAGNOSTIC=3),
    SERVICE_TYPE=SimpleNamespace(READ_MEMORY_BY_ADDRESS=0x23),
)
with mock.patch.object(host, "_import_uds", return_value=fake_uds_module):
    decoded_state = host.read_resident_state(meta, fake_probe_panda)
check("resident state readback uses the canonical resident-prefix geometry",
      meta["state"] == {
          "version": host.STATE_VERSION,
          "base": "0xFEBFF9F0",
          "size": host.STATE_SIZE,
          "layout": "resident-prefix-global-tail",
      }
      and fake_state_client.sessions == [3]
      and fake_state_client.requests == [(0x23, bytes.fromhex("1501febff9f024"))]
      and decoded_state["magic_ok"] is True
      and decoded_state["initialized"] is True
      and decoded_state["request_count"] == 7
      and decoded_state["success_count"] == 6
      and decoded_state["response_count"] == 5)

fake_self_test_panda = _FakeProbePanda()
with mock.patch.dict("sys.modules", {"panda": SimpleNamespace(Panda=lambda *_a, **_k: fake_self_test_panda)}):
    signer_self_test = host.self_test(meta_path, panda=fake_self_test_panda)
check("fresh signer self-test needs no post-activation diagnostic transport",
      signer_self_test["passed"] is True and signer_self_test["response"]["status"] == 0 and
      fake_self_test_panda.request_count == 1 and
      fake_self_test_panda.safety_modes[-1] == (host.ELM327_SAFETY_MODE, 1))

fw_dir = BUILD_ROOT / "fw-file"
fw_dir.mkdir(parents=True, exist_ok=True)
(fw_dir / "panda_h7.bin.signed").write_bytes(b"\x00" * 16 + b"\xA5" * 128)
fake_panda_module = SimpleNamespace(
    FW_PATH=str(fw_dir),
    McuType=SimpleNamespace(H7=SimpleNamespace(config=SimpleNamespace(app_fn="panda_h7.bin.signed"))),
    Panda=SimpleNamespace(
        get_signature_from_firmware=lambda fn: Path(fn).read_bytes()[-128:],
    ),
)
with mock.patch.dict("sys.modules", {"panda": fake_panda_module}):
    identity_session = host.RequestSignerSession(meta, panda=_FakeProbePanda())
check("session telemetry proves the running firmware matches the flash-candidate file",
      identity_session.telemetry["panda_signature_matches_fw_file"] is True and
      identity_session.telemetry["fw_file_signature_hex_prefix"] == "a5" * 8 and
      identity_session.telemetry["panda_signature_hex_prefix"] == "a5" * 8)
identity_session.close()

for app_live, signer_replies, expected_exit in ((True, True, 0), (True, False, 2), (False, False, 2)):
    cli_output = BUILD_ROOT / "install-cli.json"
    cli_panda = _FakeProbePanda(respond=signer_replies)
    with (
        mock.patch("sys.argv", [
            "signer", "install", "--execute",
            "--payload", str(OUT / meta["authenticated_payload"]["path"]),
            "--meta", str(meta_path), "--output", str(cli_output),
        ]),
        mock.patch("sys.stdout", io.StringIO()) as stdout,
        mock.patch.dict(sys.modules, {"panda": SimpleNamespace(Panda=lambda panda=cli_panda: panda)}),
        mock.patch.object(host, "execute_ram_payload", return_value={}),
        mock.patch.object(host, "wait_for_f181", return_value={"ok": app_live}),
        mock.patch.object(host, "SIGNER_PROBE_TIMEOUT_SECONDS", 0.01),
    ):
        exit_status = host.main()
    report = json.loads(cli_output.read_text())
    check(
        f"install CLI exit reflects application={app_live}, signer={signer_replies}",
        exit_status == expected_exit
        and (report["verdict"] == "request_signer_live_probe_pass") == (expected_exit == 0)
        and json.loads(stdout.getvalue()) == report,
    )


def _source_git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, stderr=subprocess.STDOUT, timeout=10,
    ).strip()


source_root = BUILD_ROOT / "source-checkouts"
source_origin = BUILD_ROOT / "source-origin"
for repo, branch in ((source_root, "host-branch"), (source_origin, "dbc-branch")):
    repo.mkdir()
    _source_git(repo, "init", "--quiet", f"--initial-branch={branch}")
    _source_git(
        repo, "-c", "user.name=Signer test", "-c", "user.email=signer@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "--allow-empty", "-m", branch,
    )
source_commit = _source_git(source_origin, "rev-parse", "HEAD")
host_commit = _source_git(source_root, "rev-parse", "HEAD")
_source_git(
    source_root, "-c", "protocol.file.allow=always", "submodule", "add", "--quiet",
    str(source_origin), "opendbc_repo",
)
source_submodule = source_root / "opendbc_repo"
_source_git(source_submodule, "checkout", "--quiet", "--detach")
host_identity = host._checkout_identity(source_root)
submodule_identity = host._checkout_identity(source_submodule)
check(
    "source provenance identifies an attached branch and a detached submodule independently",
    host_identity["branch"] == "host-branch"
    and host_identity["commit"] == host_commit
    and submodule_identity["branch"] is None
    and submodule_identity["commit"] == source_commit
    and source_commit != host_commit,
)
uninitialized_submodule = source_root / "panda"
uninitialized_submodule.mkdir()
uninitialized_identity = host._checkout_identity(uninitialized_submodule)
missing_identity = host._checkout_identity(source_root / "missing")
check(
    "missing or uninitialized checkouts report errors without inheriting the parent commit",
    all(
        identity["branch"] is None and identity["commit"] is None and identity.get("error")
        for identity in (uninitialized_identity, missing_identity)
    ),
)

BUILD_TEMP.cleanup()
print("PASS TSS3 request signer behavior")
