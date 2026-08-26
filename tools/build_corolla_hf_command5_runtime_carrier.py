#!/usr/bin/env python3
"""Build the H/F command-5 static runtime-carrier contract from promoted evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "data/generated/corolla_hf_command5_runtime_carrier_evidence.json"
PORTABILITY = REPO / "data/generated/corolla_hf_command5_portability.json"
PROXY_AUDIT = REPO / "exploit/ephemeral_runtime/audited_corolla_hf_command5_proxy_build.json"
CANARY_AUDIT = REPO / "exploit/ephemeral_runtime/audited_corolla_hf_canary_build.json"
PROXY_BIN = REPO / "exploit/ephemeral_runtime/audited/corolla_hf_command5_proxy.bin"
CANARY_BIN = REPO / "exploit/ephemeral_runtime/audited/corolla_hf_runtime_canary.bin"
RUNTIME_BUILDER = REPO / "exploit/ephemeral_runtime/build_corolla_hf_command5_carrier.py"
PROXY_SOURCE = REPO / "exploit/ephemeral_runtime/corolla_hf_command5_proxy.c"
CANARY_SOURCE = REPO / "exploit/ephemeral_runtime/corolla_hf_canary.c"
RAMREQ = REPO / "data/variant_ram_exec_requirements.json"
OUT = REPO / "data/generated/corolla_hf_command5_runtime_carrier.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def validate_build(audit: dict, binary: Path, source: Path, kind: str, expected_size: int, expected_headroom: int, expected_sha: str) -> None:
    need(audit["schema"] == "corolla-hf-command5-carrier-build-v1", f"{kind} audit schema drift")
    need(audit["kind"] == kind, f"{kind} audit kind drift")
    need(audit["review_status"] == "static-carrier-candidate-not-live-validated", f"{kind} review grade drift")
    shell = audit["shellcode"]
    need(shell == {"headroom": expected_headroom, "sha256": expected_sha, "size": expected_size}, f"{kind} shellcode identity drift")
    need(sha_file(binary) == expected_sha and binary.stat().st_size == expected_size, f"{kind} audited binary drift")
    need(audit["source"]["path"] == str(source.relative_to(REPO)) and audit["source"]["sha256"] == sha_file(source), f"{kind} source binding drift")
    need(audit["builder"]["path"] == str(RUNTIME_BUILDER.relative_to(REPO)) and audit["builder"]["sha256"] == sha_file(RUNTIME_BUILDER), f"{kind} runtime builder binding drift")
    cc = audit["compile_contract"]
    need(cc["candidate_base"] == "0xFEBF0000" and cc["candidate_end_exclusive"] == "0xFEBF01D0" and cc["candidate_limit"] == 464, f"{kind} carrier compile geometry drift")
    need(cc["entry_offset"] == 0 and cc["relocations"] == 0 and cc["architecture"] == "v850e3v5", f"{kind} relocation/entry drift")
    need(audit["toolchain"]["reproduced_byte_exact"] is True and audit["toolchain"]["reference_sha256"] == "273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660", f"{kind} toolchain equivalence drift")


def build() -> dict:
    ev = load(EVIDENCE)
    port = load(PORTABILITY)
    proxy = load(PROXY_AUDIT)
    canary = load(CANARY_AUDIT)
    req = load(RAMREQ)

    need(ev["schema"] == "corolla-hf-command5-runtime-carrier-evidence-v1", "carrier evidence schema drift")
    need(ev["generator"]["path"] == "tools/extract_corolla_hf_command5_runtime_carrier_evidence.py", "carrier extractor path drift")
    need(ev["generator"]["sha256"] == sha_file(REPO / ev["generator"]["path"]), "carrier extractor hash drift")
    need(port["schema"] == "corolla-hf-command5-portability-v1", "portability schema drift")

    candidate = ev["carrier_candidate"]
    mpu = ev["application_mpu"]["carrier_region"]
    mailbox = ev["xcp_mailbox_candidate"]
    static = ev["static_conclusion"]
    need(candidate["start"] == "0xFEBF0000" and candidate["end_exclusive"] == "0xFEBF01D0" and candidate["size"] == 464, "carrier pocket geometry drift")
    need(candidate["first_normalized_direct_reference"] == "0xFEBF01D0" and candidate["normalized_direct_reference_count_inside"] == 0, "carrier negative-reference boundary drift")
    need(mpu["lower"] == "0xFEBEF400" and mpu["upper_inclusive"] == "0xFEBF33FC", "carrier MPU range drift")
    need(mpu["ctx0_mpat"] == mpu["ctx1_mpat"] == "0x000000B8", "carrier MPU attributes drift")
    for context in ("ctx0_permissions", "ctx1_permissions"):
        perms = mpu[context]
        need(perms["supervisor_read"] and perms["supervisor_write"] and perms["supervisor_execute"], f"{context} lacks supervisor RWX")
        need(not perms["user_read"] and not perms["user_write"] and not perms["user_execute"], f"{context} unexpectedly grants user access")
    need(mailbox["start"] == "0xFEBFFB80" and mailbox["end_exclusive"] == "0xFEBFFBBC" and mailbox["size"] == 60, "mailbox geometry drift")
    need(mailbox["normalized_direct_reference_count_inside"] == 0, "mailbox direct-reference boundary drift")
    need(static["h_f_prerequisites_transfer_byte_exact"] and ev["h_f_exact_transfer"]["all_ranges_byte_equal"], "H/F prerequisite transfer drift")

    validate_build(proxy, PROXY_BIN, PROXY_SOURCE, "command5-proxy", 462, 2, "9b9b055c65246bb4e25bc512753772bbe474c0ba5847ecb253e4147fd1db8dbf")
    validate_build(canary, CANARY_BIN, CANARY_SOURCE, "runtime-canary", 332, 132, "a32baf46dd8e0599021b5c174763887513b3ba903d40ebe284f19d31c97424f4")

    variants = {row["id"] for row in req["variants"]}
    need("corolla-8965h1202000" not in variants and "corolla-8965f1208000" not in variants, "static carrier candidate must not be promoted as verified RAM geometry")

    runtime = proxy["runtime_contract"]
    need(runtime["command5_dispatcher"] == "0x00082750" and runtime["command5_driver_record"] == 0 and runtime["command5_key_selector"] == 4, "proxy command5 route drift")
    need(runtime["command5_done_flag"] == "0xFEBF1280" and runtime["command5_status_flag"] == "0xFEBF1281", "proxy completion route drift")
    need(runtime["fixed_command5_input_length"] == 36 and runtime["mailbox_address"] == "0xFEBFFB80" and runtime["mailbox_size"] == 60, "proxy B6/mailbox contract drift")
    need(port["command5_core"]["b6_authenticated_input_bytes"] == 36 and port["command5_core"]["b6_authenticated_input_fits"], "joined B6 command5 portability drift")

    return {
        "schema": "corolla-hf-command5-runtime-carrier-v1",
        "applies_to": ["8965H1202000", "8965F1208000"],
        "sources": {
            "static_evidence": {"path": str(EVIDENCE.relative_to(REPO)), "sha256": sha_file(EVIDENCE)},
            "command5_portability": {"path": str(PORTABILITY.relative_to(REPO)), "sha256": sha_file(PORTABILITY)},
            "proxy_audit": {"path": str(PROXY_AUDIT.relative_to(REPO)), "sha256": sha_file(PROXY_AUDIT)},
            "canary_audit": {"path": str(CANARY_AUDIT.relative_to(REPO)), "sha256": sha_file(CANARY_AUDIT)},
            "runtime_builder": {"path": str(RUNTIME_BUILDER.relative_to(REPO)), "sha256": sha_file(RUNTIME_BUILDER)},
            "ram_exec_requirements": {"path": str(RAMREQ.relative_to(REPO)), "sha256": sha_file(RAMREQ)},
        },
        "carrier_geometry": {
            "base": candidate["start"],
            "end_inclusive": candidate["end_inclusive"],
            "end_exclusive": candidate["end_exclusive"],
            "size": candidate["size"],
            "first_recovered_normalized_reference": candidate["first_normalized_direct_reference"],
            "normalized_direct_reference_count_inside": 0,
            "mpu_region_index": ev["application_mpu"]["carrier_region_index"],
            "mpu_bounds": [mpu["lower"], mpu["upper_inclusive"]],
            "mpat_contexts": [mpu["ctx0_mpat"], mpu["ctx1_mpat"]],
            "permissions": "supervisor-read-write-execute in both recovered application contexts; no user permissions",
            "static_negative_boundary": candidate["normalization"]["boundary"],
        },
        "mailbox_geometry": {
            "base": mailbox["start"],
            "end_exclusive": mailbox["end_exclusive"],
            "size": mailbox["size"],
            "normalized_direct_reference_count_inside": 0,
            "xcp_shadow_window": mailbox["xcp_shadow_write_window"],
            "startup_shadow_copy_end_inclusive": mailbox["startup_shadow_copy_end_inclusive"],
            "request_state_precondition": "installer must initialize mailbox request_state byte to 0 before launching the command5 proxy",
            "static_negative_boundary": mailbox["boundary"],
        },
        "runtime_candidates": {
            "inert_canary": {
                "binary": str(CANARY_BIN.relative_to(REPO)),
                "size": 332,
                "headroom": 132,
                "sha256": "a32baf46dd8e0599021b5c174763887513b3ba903d40ebe284f19d31c97424f4",
                "entry_offset": 0,
                "relocations": 0,
                "heartbeat_address": "0xFEBFFB80",
                "purpose": "validate boot-to-application handoff, scheduler ownership, executable retention, and observation-cell lifetime before any command-5 request",
            },
            "fixed_b6_command5_proxy": {
                "binary": str(PROXY_BIN.relative_to(REPO)),
                "size": 462,
                "headroom": 2,
                "sha256": "9b9b055c65246bb4e25bc512753772bbe474c0ba5847ecb253e4147fd1db8dbf",
                "entry_offset": 0,
                "relocations": 0,
                "input_length": 36,
                "driver_record": 0,
                "key_selector": 4,
                "dispatcher": "0x00082750",
                "done_flag": "0xFEBF1280",
                "status_flag": "0xFEBF1281",
                "busy_behavior": "shared-driver busy result 2 leaves request_state=1 so the next foreground iteration retries; no command-7 abort primitive is called",
            },
        },
        "scheduler_transfer": {
            "application_context_init": ev["startup_scheduler_contract"]["application_context_init"],
            "startup_jarl_first": ev["startup_scheduler_contract"]["startup_jarl_first"],
            "startup_jarl_after": ev["startup_scheduler_contract"]["startup_jarl_after"],
            "startup_jarl_count": ev["startup_scheduler_contract"]["startup_jarl_count"],
            "startup_final_init": ev["startup_scheduler_contract"]["startup_final_init"],
            "foreground_scheduler": ev["startup_scheduler_contract"]["foreground_scheduler"],
            "foreground_tick_counter": ev["startup_scheduler_contract"]["foreground_tick_counter"],
            "h_f_listed_prerequisites_byte_identical": True,
        },
        "toolchain_reproducibility": {
            "canonical_sienna_proxy_sha256": "273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660",
            "noncanonical_image_acceptance_rule": "accepted only after byte-exact reproduction of the canonical audited Sienna 546-byte proxy",
            "selected_build_reproduced_canonical_reference": True,
        },
        "validation_sequence": [
            {
                "stage": 1,
                "name": "inert carrier canary",
                "criterion": "heartbeat at FEBFFB80 changes after the boot-to-application transition while normal application scheduling remains healthy",
                "purpose": "close retention/lifetime/control-flow before exposing command-5",
            },
            {
                "stage": 2,
                "name": "known-input slot4 command5 permission",
                "criterion": "on a fresh isolated bench run, a known authenticated-domain input produces a stable current-run result under selector4 without scheduler failure",
                "purpose": "close live slot4 generation permission independently of vehicle actuation",
            },
            {
                "stage": 3,
                "name": "independent MAC agreement",
                "criterion": "7/12/36-byte generated results agree with independently known CMAC vectors for the same live key/domain where such vectors are available",
                "purpose": "validate semantic output, not merely command completion",
            },
            {
                "stage": 4,
                "name": "latency and contention characterization",
                "criterion": "measure completion latency/jitter under ordinary command-7 verification load and demonstrate a sender schedule compatible with the B6 cadence/deadline",
                "purpose": "close production timing before any lateral Tx enablement",
            },
        ],
        "boundary": {
            "static_target_native_carrier_candidate_closed": True,
            "verified_variant_ram_exec_requirement_promoted": False,
            "live_retention_closed": False,
            "live_slot4_permission_closed": False,
            "command5_latency_jitter_closed": False,
            "production_b6_signer_closed": False,
            "vehicle_actuation_authorized": False,
            "interpretation": "Static H/F carrier geometry and executable fit are now closed enough to define a concrete live canary experiment. This is not proof that FEBF0000..01CF remains unmodified in a running ECU, that slot4 permits command5, or that signing meets B6 timing. Those remain dynamic gates.",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
