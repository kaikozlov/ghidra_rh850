#!/usr/bin/env python3
"""Verify the dump-resolved universal TSS3 RAM-resident request signer."""
from __future__ import annotations

import io
import json
import subprocess
import struct
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import tsk.ram_runtime.tss3_request_signer as host
import tools.targets.tss3.builders.build_tss3_request_signer as build
from tsk.common.payload_package import inspect_payload
from tsk.common.rh850_build import CJob
from tsk.ram_runtime.target_profiles import registered_specs, spec_from_codeflash
from tsk.ram_runtime.tss3_request_signer_contract import (
    ContractError,
    probe_request_signer_contract,
    resolve_request_signer_contract,
)
from tools import REPO_ROOT

ROOT = REPO_ROOT

CAMRY_TARGET = "camry-8965F3307000"
SPECS = registered_specs()
SIENNA_TARGET = "sienna-8965B4512000"
SIENNA_IMAGE = ROOT / "firmware/RH850_P1M-E_CodeFlash.bin"
SIENNA_CONTRACT = resolve_request_signer_contract(SIENNA_IMAGE.read_bytes())
RESOLUTION_SPECS = {
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
synthetic_spec = spec_from_codeflash(synthetic_path, known_specs=SPECS)
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

route_ambiguous = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
route_map = SPECS[CAMRY_TARGET]["contract"]["signer_abi"]["route_map"]
response_handle = SPECS[CAMRY_TARGET]["contract"]["signer_abi"]["response_handle"]
duplicate_handle = next(
    handle for handle in range(256)
    if handle != response_handle
    and route_ambiguous[route_map + handle * 2:route_map + handle * 2 + 2] != b"\x01\x06"
)
route_ambiguous[route_map + duplicate_handle * 2:route_map + duplicate_handle * 2 + 2] = b"\x01\x06"
route_ambiguous_path = BUILD_ROOT / "resolver-route-ambiguous.bin"
route_ambiguous_path.write_bytes(route_ambiguous)

check(
    "on-device resolver fails closed on missing, duplicate, and ambiguous dependencies",
    run_resolver(command5_damaged_path)[0] == -2
    and run_resolver(command5_duplicated_path)[0] == -2
    and run_resolver(route_ambiguous_path)[0] == -11,
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
expected_confirmation_paths = {
    "camry-8965F3307000": (0x00085240, 0xFEBE5036, 0x0008043C, 0x0008152E),
    "crown-8965F3012000": (0x000813D0, 0xFEBE4AE6, 0x0007DAA8, 0x0007EB4A),
    "corolla-8965F1208000": (0x0007E550, 0xFEBE4F22, 0x0007974C, 0x0007A83E),
    "corolla-8965H1202000": (0x0007E550, 0xFEBE4F22, 0x0007974C, 0x0007A83E),
    "sienna-8965B4512000": (0x00084150, 0xFEBE502A, 0x0007F350, 0x00080442),
}
expected_slot4_configs = {
    "camry-8965F3307000": 0x00025828,
    "crown-8965F3012000": 0x00025564,
    "corolla-8965F1208000": 0x0002570C,
    "corolla-8965H1202000": 0x0002570C,
    "sienna-8965B4512000": 0x00025950,
}
expected_shadow_copy = {
    "camry-8965F3307000": 0x000636D4,
    "crown-8965F3012000": 0x00062AD4,
    "corolla-8965F1208000": 0x0005C992,
    "corolla-8965H1202000": 0x0005C992,
    "sienna-8965B4512000": 0x0006263E,
}
for target, spec in RESOLUTION_SPECS.items():
    probe = probe_request_signer_contract(spec["image"].read_bytes())
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
        f"{target} binds the exact startup shadow copy before the resident boundary",
        shadow["function"] == expected_shadow_copy[target]
        and shadow["source"] == 0x00010000
        and shadow["destination"] == 0xFEBF7C00
        and shadow["size"] == 0x7DF0
        and shadow["destination"] + shadow["size"] == 0xFEBFF9F0,
    )
    abi = probe["contract"]["signer_abi"]
    completion, slot, dispatcher, noop = expected_confirmation_paths[target]
    check(
        f"{target} proves fixed command5 config is target-native type1/selector4",
        abi["slot4_config"] == expected_slot4_configs[target]
        and abi["command5_config_type"] == 1
        and abi["command5_selector"] == 4
        and spec["image"].read_bytes()[abi["slot4_config"]:abi["slot4_config"] + 32]
            == bytes.fromhex("0100000004000000000000000000000000000000000000000000cc000f000000"),
    )
    check(
        f"{target} proves private confirmation handle F0 follows the native completion path to a no-op",
        abi["lower_tx_completion"] == completion
        and abi["response_confirmation_slot"] == slot
        and abi["software_confirmation_handle"] == 0x00F0
        and abi["software_confirmation_dispatcher"] == dispatcher
        and abi["software_confirmation_noop"] == noop
        and spec["image"].read_bytes()[noop:noop + 2] == bytes.fromhex("7f00"),
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
four_resource_contract = resolve_request_signer_contract(bytes(four_resource_image))
check(
    "primary diagnostic response routing is independent of optional fifth resource",
    four_resource_contract["signer_abi"]["resource_row_count"] == 4
    and four_resource_contract["signer_abi"]["response_handle"] == camry_abi["response_handle"]
    and four_resource_contract["signer_abi"]["response_resource"] == camry_abi["response_resource"],
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
summary = host.latency_summary([4.0, 1.0, 3.0, 2.0])
check("parked benchmark reports deterministic distribution statistics",
      {name: round(value, 3) for name, value in summary.items()} == {
          "mean_ms": 2.5, "median_ms": 2.5, "p95_ms": 3.85, "p99_ms": 3.97, "max_ms": 4.0,
      })


def _recorded_send(index: int, seq: int, *, lateness_ms: float, started_ns: int) -> dict:
    application = host.safe_application(seq)
    frames = host.build_request(application, seq)
    return {
        "index": index,
        "seq": seq,
        "codec": host.FOUR_FRAME_CODEC,
        "request_sequence": application[26],
        "scheduled_start_lateness_ms": round(max(0.0, lateness_ms), 3),
        "started_ns": started_ns,
        "submit_ms": 0.15,
        "frames_hex": [frame.hex() for frame in frames],
    }


def _recorded_response(seq: int, status_value: int, started_ns: int, *, rtt_ms: float, counter: int) -> dict:
    frame = bytes((host.RESPONSE_MAGIC, seq, status_value, seq ^ 0xFF)) + bytes(
        (0x10 | (counter & 0x0F), seq, 0xA5, 0x5A))
    parsed = host.parse_response(frame)
    return {
        "monotonic_ns": started_ns + round(rtt_ms * 1e6),
        "frame_hex": frame.hex(),
        "seq": parsed.seq,
        "status": parsed.status,
        "trailer": parsed.trailer.hex(),
        "fv4": parsed.trailer[0] >> 4,
    }


def _recorded_run(count: int, period_ms: float, *, lateness_ms: list[float], rtt_ms: list[float],
                  statuses: list[int] | None = None, sent: int | None = None, answered: int | None = None,
                  rx_errors: tuple[str, ...] = (), max_outstanding: int = 1,
                  sequence_window_exhausted: bool = False,
                  outstanding_after_drain: int | None = None) -> dict:
    """Rebuild a pipelined transcript in the exact shape benchmark_pipelined records."""
    sent = count if sent is None else sent
    answered = sent if answered is None else answered
    sends: list[dict] = []
    responses: dict[int, dict] = {}
    started_ns = 1_000_000_000
    for index in range(sent):
        seq = index + 1
        sends.append(_recorded_send(index, seq, lateness_ms=lateness_ms[index], started_ns=started_ns))
        if index < answered:
            status_value = statuses[index] if statuses is not None else 0
            responses[index] = _recorded_response(
                seq, status_value, started_ns, rtt_ms=rtt_ms[index], counter=index + 1)
        started_ns += round(period_ms * 1e6)
    return host._reduce_pipelined_benchmark(
        count, period_ms, sends, responses,
        unsolicited_count=0,
        rx_errors=list(rx_errors),
        outstanding_after_drain=sent - answered if outstanding_after_drain is None else outstanding_after_drain,
        max_outstanding=max_outstanding,
        sequence_window_exhausted=sequence_window_exhausted,
    )


boundary_run = _recorded_run(
    4, 10.0,
    lateness_ms=[0.0, 1.25, 6.0, 9.999],
    rtt_ms=[2.0, 45.0, 12.5, 90.0],
    max_outstanding=host.RUNTIME_MAX_PENDING_GENERATIONS,
)
check("pipelined completion verdict accepts a recorded run at every inclusive boundary",
      boundary_run["complete_target_rate_run"] is True and
      boundary_run["count_sent"] == boundary_run["success_count"] == boundary_run["responses_received"] == 4 and
      boundary_run["success_rate"] == 1.0 and boundary_run["outstanding_after_drain"] == 0 and
      boundary_run["sequence_window_exhausted"] is False and
      boundary_run["scheduled_start_lateness_ms"]["max_ms"] == 9.999 and
      boundary_run["request_start_to_response_ms"]["max_ms"] == 90.0 and
      boundary_run["rows"][3]["request_start_to_response_ms"] == 90.0 and
      boundary_run["response_interarrival_ms"]["max_ms"] == 65.0 and
      boundary_run["effective_success_response_rate_hz"] == 25.424)

clean_lateness = [0.0, 0.5, 1.0, 1.5]
clean_rtt = [2.0, 3.0, 4.0, 5.0]

missing_reply = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=clean_rtt, answered=3)
check("pipelined completion verdict rejects a run whose last reply never arrives",
      missing_reply["complete_target_rate_run"] is False and
      missing_reply["success_count"] == 3 and missing_reply["responses_received"] == 3 and
      missing_reply["outstanding_after_drain"] == 1 and missing_reply["success_rate"] == 0.75 and
      missing_reply["rows"][3]["error"] == "missing_response" and
      "status" not in missing_reply["rows"][3])

error_status = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=clean_rtt,
                             statuses=[0, 0, 0, 0x21])
check("pipelined completion verdict rejects a delivered nonzero signer status",
      error_status["complete_target_rate_run"] is False and
      error_status["success_count"] == 3 and error_status["responses_received"] == 4 and
      error_status["outstanding_after_drain"] == 0 and
      error_status["rows"][3]["status"] == 0x21 and "error" not in error_status["rows"][3] and
      error_status["rows"][3]["request_start_to_response_ms"] == 5.0)

rx_failure = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=clean_rtt,
                           rx_errors=("OSError: can recv failed",))
check("pipelined completion verdict rejects a run whose receiver thread died",
      rx_failure["complete_target_rate_run"] is False and
      rx_failure["success_count"] == 4 and
      rx_failure["rx_errors"] == ["OSError: can recv failed"])

overloaded = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=clean_rtt,
                           max_outstanding=host.RUNTIME_MAX_PENDING_GENERATIONS + 1)
check("pipelined completion verdict rejects backlog past the pending-generation limit",
      overloaded["complete_target_rate_run"] is False and
      overloaded["success_count"] == 4 and
      overloaded["max_outstanding"] == host.RUNTIME_MAX_PENDING_GENERATIONS + 1)

late_publication = _recorded_run(4, 10.0, lateness_ms=[0.0, 0.5, 1.0, 10.0], rtt_ms=clean_rtt)
check("pipelined completion verdict rejects a publication that slipped a full period",
      late_publication["complete_target_rate_run"] is False and
      late_publication["rows"][3]["scheduled_start_lateness_ms"] == 10.0)

slow_reply = _recorded_run(4, 10.0, lateness_ms=clean_lateness, rtt_ms=[2.0, 3.0, 4.0, 90.001])
check("pipelined completion verdict rejects a reply past the publication deadline",
      slow_reply["complete_target_rate_run"] is False and
      slow_reply["rows"][3]["request_start_to_response_ms"] == 90.001 and
      slow_reply["request_start_to_response_ms"]["max_ms"] == 90.001)

wedged = _recorded_run(300, 10.0, lateness_ms=[0.5] * host.SEQUENCE_MAX, rtt_ms=[3.0] * host.SEQUENCE_MAX,
                       sent=host.SEQUENCE_MAX, answered=3, sequence_window_exhausted=True,
                       max_outstanding=host.SEQUENCE_MAX)
check("pipelined completion verdict rejects a wedged signer that exhausted the sequence window",
      wedged["complete_target_rate_run"] is False and
      wedged["count_sent"] == host.SEQUENCE_MAX and wedged["count_requested"] == 300 and
      wedged["sequence_window_exhausted"] is True and
      wedged["outstanding_after_drain"] == host.SEQUENCE_MAX - 3 and
      wedged["responses_received"] == 3 and wedged["success_rate"] == 3 / 300 and
      len(wedged["rows"]) == host.SEQUENCE_MAX and
      [row.get("error") for row in wedged["rows"][3:]] == ["missing_response"] * (host.SEQUENCE_MAX - 3))




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
