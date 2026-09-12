#!/usr/bin/env python3
"""Build and verify the exact H/F split-resident B6 signer candidate."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "exploit/ephemeral_runtime/build_corolla_hf_b6_inline_signer.py"
sys.path.insert(0, str(REPO))
from exploit.ephemeral_runtime import corolla_hf_b6_inline_signer as installer
from tools.targets.corolla.builders import build_corolla_hf_car_kit as car_kit


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[PASS] {label}")


def build(target: str, root: Path) -> dict[str, object]:
    out = root / target
    result = subprocess.run(
        [sys.executable, str(BUILDER), "--target", target, "--output-dir", str(out)],
        cwd=REPO, check=True, capture_output=True, text=True,
    )
    meta = json.loads(result.stdout)
    meta["_out"] = out
    return meta


with tempfile.TemporaryDirectory(prefix="verify-corolla-hf-inline-signer-") as td:
    root = Path(td)
    h = build("8965H1202000", root)
    f = build("8965F1208000", root)

    check("H/F schemas", h["schema"] == f["schema"] == "corolla-hf-b6-inline-signer-build-v1")
    check("startup survival review boundary", h["review_status"] == "firmware-verified-startup-survival-live-command5-unvalidated")
    check("exact target identities differ", h["target"]["codeflash_sha256"] != f["target"]["codeflash_sha256"])
    check("application-identical H/F resident", h["resident"]["sha256"] == f["resident"]["sha256"])
    check("application-identical H/F helper", h["helper"]["sha256"] == f["helper"]["sha256"])
    check("application-identical H/F payload", h["authenticated_payload"]["sha256"] == f["authenticated_payload"]["sha256"])
    check("H/F startup-survival contract identical", h["startup_survival"] == f["startup_survival"])
    check("resident fits exact post-shadow tail", h["resident"]["size"] == 522 and h["resident"]["headroom"] == 2)
    check("helper fits exact low candidate", h["helper"]["size"] == 460 and h["helper"]["headroom"] == 4)
    survival = h["startup_survival"]
    check("startup survival is firmware-verified", survival["classification"] == "firmware-verified-startup-survival")
    check("low helper ends before first startup writer", survival["low_helper"] == {
        "range": ["0xFEBF0000", "0xFEBF01CF"],
        "first_recovered_startup_write": "0xFEBF0200",
        "startup_clear_gap": 48,
        "localram_initializer": "0x0006149A",
        "normalized_reference_count": 0,
    })
    check("high resident begins after exact shadow copy", survival["high_resident"] == {
        "range": ["0xFEBFF9F0", "0xFEBFFBFB"],
        "shadow_copy_function": "0x0005C992",
        "shadow_source": ["0x00010000", "0x00017DEF"],
        "shadow_destination": ["0xFEBF7C00", "0xFEBFF9EF"],
        "normalized_reference_count": 0,
    })
    check("runtime ownership boundary stays explicit", all(x in survival["boundary"] for x in ("computed pointers", "externally initiated memory writes", "hardware writers")))
    mailbox = h["mailbox"]
    check("mailbox ends before recurring foreground", int(mailbox["base"], 16) + mailbox["size"] <= int(mailbox["foreground_entry"], 16))
    check("control reuses proven stock-Toyota-B C7 recipe", h["control"] == {
        "can_id": "0x1FDC0002", "extended": True, "bus": 1,
        "staging": "0xFEBE4B20", "magic": "00c7",
        "format": "00 C7 seq 00 target_hi target_lo 00 00",
    })
    check("hook is after drain and before SecOC", h["hook"] == {"receive_drain": "0x0007744A", "helper": "0xFEBF0000", "secoc_periodic": "0x000636C0"})
    check("exact Corolla B6 queue geometry", h["b6"]["queue_record"] == "0xFEBE5366" and h["b6"]["secured_buffer"] == "0xFEBE53C0")
    check("exact synchronous command5 wrapper", h["command5"]["synchronous_wrapper"] == "0x00082ED2")
    check("native pass-through failure", h["behavior"]["failure"] == "native B6 untouched")
    check("replacement explicitly requires native B6", h["behavior"]["requires_native_b6_stream"] is True)
    check("C7 is consumed before command 5", "C7 sequence consumed before command 5" in h["behavior"]["replacement_gate"])
    check("no direct CAN or verification bypass", not h["behavior"]["can_transmit"] and not h["behavior"]["secoc_result_override"])

    helper_source = (REPO / "exploit/ephemeral_runtime/corolla_hf_b6_inline_signer_helper.S").read_text()
    resident_source = (REPO / "exploit/ephemeral_runtime/corolla_hf_b6_inline_signer_resident.S").read_text()
    builder_source = (REPO / "exploit/ephemeral_runtime/build_corolla_hf_b6_inline_signer.py").read_text()
    check("resident has no address-in-r6 call trampoline", all(
        "call0" not in source and "jarl [r6]" not in source
        for source in (resident_source, builder_source)
    ))
    check("resident directly links stock startup calls",
          all(f"jarl32 startup_{i:02d}, lp" in resident_source for i in range(18)) and
          "mov 0, r6\n    jarl32 app_startup_final_init, lp" in resident_source)
    consume = helper_source.index("sst.b r8, 5[ep]")
    command5 = helper_source.index("jarl32 command5_sync")
    check("helper consumes C7 before signing", consume < command5)
    check("helper preserves operation across stock calls", all(x in helper_source for x in (
        "prepare {r20-r21,lp}", "mov 2, r21", "mov 1, r21", "dispose 0, {r20-r21,lp}",
    )) and "addi -2, r19" not in helper_source)

    class FakeService:
        READ_MEMORY_BY_ADDRESS = 0x23

    class FakeUds:
        SERVICE_TYPE = FakeService

    class FakeClient:
        def __init__(self) -> None:
            self.requests = []

        def _uds_request(self, service, *, data):
            self.requests.append((service, data))
            return bytes([len(self.requests)]) * data[-1]

    fake = FakeClient()
    rmba = installer.read_memory(fake, FakeUds, address=installer.STATE_BASE, length=0xF5)
    check("status uses chunked SID23 RMBA", len(rmba) == 0xF5 and fake.requests == [
        (0x23, bytes((0x15, 0x01)) + installer.STATE_BASE.to_bytes(4, "big") + b"\xF0"),
        (0x23, bytes((0x15, 0x01)) + (installer.STATE_BASE + 0xF0).to_bytes(4, "big") + b"\x05"),
    ])

    for meta in (h, f):
        out = meta["_out"]
        target = meta["target"]["software_id"]
        prefix = f"corolla_{target}_b6_inline_signer"
        bundle = installer.load_bundle(out / f"{prefix}_payload.bin", out / f"{prefix}.json")
        plan = installer.build_plan(bundle)
        check(f"{target} installer binds exact F181", plan["target"]["required_application_f181_hex"] == installer.APP_F181[target])
        check(f"{target} installer binds exact CodeFlash", plan["target"]["codeflash_sha256"] == installer.CODEFLASH_SHA256[target])
        check(f"{target} status is SID23, not XCP", plan["runtime"]["status"] == {
            "transport": "application UDS SID 0x23 RMBA", "alfid": "0x15", "memory_id": 1,
        })
        check(f"{target} plan exposes native carrier requirement",
              plan["runtime"]["requires_native_b6_stream"] is True)
        check(f"{target} installer remains volatile", not plan["install"]["flash_writes"] and plan["install"]["removal"] == "full EPS power cycle")

    waiting = installer.decode_state(bytes.fromhex("423646530000000000000000000000001122334455667788"))
    verified = installer.decode_state(bytes.fromhex("423646530000000001000000000000001122334455667788"))
    check("installer state decoder distinguishes oracle gate", waiting["oracle_state_name"] == "awaiting-native-b6" and verified["oracle_state_name"] == "native-mac-verified")
    extracted = installer.decode_b6_extract(bytes.fromhex("34120b000100000900000000000000"))
    check("status decodes target-native B6 secondary tuple", extracted == {
        "raw_hex": "34120b000100000900000000000000",
        "source": "last generated-COM B6 scalar extraction; not a live queue snapshot",
        "target_lateral_id": 11,
        "target_angle_raw": 0x1234,
        "secondary": {
            "signal258": 1, "signal260": 0, "signal261_native_sequence": 9,
            "signal262": 0, "signal263": 0, "signal264": 0, "signal265": 0,
        },
        "matches_firmware_minimal_id11_secondary_tuple": True,
    })
    waiting["b6_extracted_fields"] = extracted
    verified["b6_extracted_fields"] = extracted
    check("qualification blocks before native oracle", installer.qualify_state(waiting) == {
        "ready_for_stationary_c7": False,
        "verdict": "awaiting-native-b6",
        "next_action": "keep READY/Park and re-read status; do not send active C7 until a distinct native B6 is verified",
    })
    check("qualification admits only verified minimal native shape",
          installer.qualify_state(verified)["verdict"] == "native-path-qualified-for-stationary-c7")
    nonminimal = dict(verified)
    nonminimal["b6_extracted_fields"] = dict(extracted)
    nonminimal["b6_extracted_fields"]["matches_firmware_minimal_id11_secondary_tuple"] = False
    check("qualification blocks an unreviewed native secondary tuple",
          installer.qualify_state(nonminimal)["verdict"] == "native-b6-secondary-tuple-needs-review")

    dirty_kit = root / "retained-kit"
    dirty_kit.mkdir()
    (dirty_kit / "obsolete-xcp-client.py").write_text("stale\n")
    try:
        car_kit.build("8965H1202000", dirty_kit)
    except RuntimeError as exc:
        check("car kit refuses retained output files", "refusing to mix" in str(exc))
    else:
        raise AssertionError("car kit accepted retained output files")

    clean_kit = root / "clean-kit"
    manifest = car_kit.build("8965H1202000", clean_kit)
    check("car kit contains only current runtime dependencies", set(manifest["files"]) == {
        "corolla-tss3-signer",
        "ram_payloads/corolla_hf_b6_inline_signer.json",
        "ram_payloads/corolla_hf_b6_inline_signer_payload.bin",
        "runtime/exploit/common/ram_exec.py",
        "runtime/exploit/ephemeral_runtime/corolla_hf_b6_inline_signer.py",
        "runtime/exploit/ephemeral_runtime/f33_panda_lease.sh",
    })

print("Corolla H/F inline signer build verification passed.")
