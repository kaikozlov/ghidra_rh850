#!/usr/bin/env python3
"""Deterministically verify the exact-F33 valid-0x090 route40 experiment."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import build_camry_f33_route40_observer as build  # noqa: E402
from exploit.ephemeral_runtime import camry_f33_command5_probe as signer  # noqa: E402
from exploit.ephemeral_runtime import camry_f33_route40_observer as observer  # noqa: E402
from tools.targets.camry.builders import build_camry_f33_car_kit as car_kit  # noqa: E402

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


print("== deterministic route40 observer build ==")
run = subprocess.run([sys.executable, str(build.BUILDER)], cwd=ROOT, capture_output=True, text=True, check=False)
check("route40 observer builder succeeds", run.returncode == 0, run.stderr[-400:])
out = build.DEFAULT_OUTPUT_DIR
meta = json.loads((out / "camry_f33_route40_observer.json").read_text()) if run.returncode == 0 else {}
resident = (out / meta["resident"]["path"]).read_bytes() if meta else b""
stage = (out / meta["staging"]["path"]).read_bytes() if meta else b""
payload = (out / meta["authenticated_payload"]["path"]).read_bytes() if meta else b""
audit = json.loads((ROOT / "exploit/ephemeral_runtime/audited_camry_f33_route40_observer_build.json").read_text())
audited_stage = (ROOT / "exploit/ephemeral_runtime/audited/camry_f33_route40_observer.bin").read_bytes()
check("generated and audited route40 artifacts are byte-exact", meta == audit and stage == audited_stage)
check("route40 resident fits the live-proven high tail with no relocations",
      len(resident) == observer.RESIDENT_SIZE and meta["resident"]["headroom"] == 524 - observer.RESIDENT_SIZE and
      meta["resident"]["relocations"] == 0 and sha(resident) == observer.EXPECTED_RESIDENT_SHA256)
check("staging and authenticated payload identities are pinned",
      sha(stage) == observer.EXPECTED_STAGING_SHA256 and
      sha(payload) == observer.EXPECTED_PAYLOAD_SHA256 and len(payload) == 0x1000)
check("firmware-derived route40 contract is exact", meta["route40"] == {
    "can_id": "0x090", "destination_table_entry": [40, 0xFFFF],
    "generation": "0xFEBE5360", "index": 40,
    "invalid_checksum_counter": "0xFEBE53C0",
    "raw_com": "0xFEBE4BAF", "raw_com_size": 32,
})
check("observer mutation boundary excludes routing/authentication changes",
      meta["mutation_boundary"]["added_write_regions"] == ["FEBF0000..FEBF002F route40 observer mailbox"] and
      all(meta["mutation_boundary"][key] is False for key in (
          "stock_application_writes", "route_table_patch", "secoc_bypass",
          "can_transmit", "command5_call", "codeflash_write",
      )))

print("\n== fully valid prepared 0x090 ==")
application = bytearray(range(28))
application[7] = signer.toyota_legacy_checksum8(can_id=0x090, first_seven=bytes(application[:7]))
native_frame = bytes(application) + bytes.fromhex("51234567")


class FakeSignerSession:
    def __init__(self) -> None:
        self.domains: list[tuple[bytes, bytes]] = []

    def capture_native_090(self, *, timeout_seconds: float) -> dict[str, object]:
        assert timeout_seconds == 1.0
        return {
            "trip_counter": 0x1234, "reset_counter": 0x56789,
            "sync_bus": 0, "frame_bus": 0, "sync_hex": "00" * 8,
            "frame_hex": native_frame.hex(), "sync_age_ms": 1.0, "frame_age_ms": 1.0,
        }

    def generate(self, domain: bytes, *, expected_data_id: bytes) -> dict[str, object]:
        self.domains.append((bytes(domain), bytes(expected_data_id)))
        return {"outcome": "generated", "output_cmac_hex": bytes(range(16)).hex()}


fake = FakeSignerSession()
prepared = signer.prepare_authenticated_valid_090_route_probe(fake)
prepared_frame = bytes.fromhex(prepared["frame_hex"])
check("preparation signs a far-future message2 and never transmits",
      prepared["outcome"] == observer.PREPARED_OUTCOME and prepared["transmitted_090"] is False and
      prepared["signed_epoch"]["message_counter"] == 2 and
      prepared["signed_epoch"]["future_reset_lead"] == signer.NATIVE_090_ROUTE_PREP_RESET_LEAD == 512)
check("prepared application has one unique non-decoded marker and a recomputed valid B7",
      prepared_frame[:6] == native_frame[:6] and prepared_frame[6] == (native_frame[6] ^ 1) and
      prepared_frame[7] != native_frame[7] and prepared_frame[8:28] == native_frame[8:28] and
      prepared["mutation"]["byte"] == 6 and prepared["boundaries"]["mutated_byte_is_not_decoded_by_f33"] is True and
      prepared["f33_b7"]["valid"] is True and
      prepared_frame[7] == signer.toyota_legacy_checksum8(can_id=0x090, first_seven=prepared_frame[:7]))
check("prepared P5 domain binds DataID 0x0090, application, and full freshness",
      len(fake.domains) == 1 and fake.domains[0][1] == bytes.fromhex("0090") and
      fake.domains[0][0].hex() == prepared["domain_hex"] and
      prepared["expected_route40_trailer_hex"] == prepared_frame[28:32].hex())
with tempfile.TemporaryDirectory() as td:
    artifact = Path(td) / "prepared.json"
    artifact.write_text(json.dumps(prepared), encoding="utf-8")
    loaded = observer.load_prepared(artifact)
check("route runner independently validates prepared geometry/B7/FV4/domain",
      loaded["_frame"] == prepared_frame and loaded["_trailer"] == prepared_frame[28:32] and
      loaded["_trip"] == prepared["signed_epoch"]["trip_counter"] and
      loaded["_reset"] == prepared["signed_epoch"]["reset_counter"])

print("\n== sticky mailbox and host sequencing ==")
raw = bytearray(observer.MAILBOX_SIZE)
raw[0:4] = observer.MAILBOX_MAGIC.to_bytes(4, "little")
raw[4:8] = bytes((observer.MAILBOX_VERSION, 7, 0, 1))
raw[8:12] = prepared_frame[28:32]
raw[0x0C] = 41
raw[0x10:0x30] = prepared_frame
state = observer.decode_mailbox(bytes(raw))
check("mailbox latches exact trailer, complete frame, and route metadata",
      state["magic_ok"] and state["version_ok"] and state["matched"] and not state["armed"] and
      state["expected_trailer_hex"] == prepared_frame[28:32].hex() and
      state["latched_frame_hex"] == prepared_frame.hex() and state["generation_at_match"] == 41)
check("36-bit epoch distance handles reset and trip rollover",
      observer.forward_epoch_distance(
          current_trip=0x1234, current_reset=0xFFFFF,
          target_trip=0x1235, target_reset=2,
      ) == 3)
launcher = (ROOT / "exploit/ephemeral_runtime/camry_f33_route40_observer_launcher.sh").read_text()
sign_launcher = (ROOT / "exploit/ephemeral_runtime/camry_f33_command5_launcher.sh").read_text()
check("field launchers expose the two-phase bounded sequence",
      "prepare-native-090-route-probe OUTPUT_JSON" in sign_launcher and
      "run_probe_bounded 60 prepare-native-090-route-probe" in sign_launcher and
      "./f33-route40 run PREPARED_JSON [OUTPUT_JSON]" in launcher and
      "run_bounded 260 run --prepared" in launcher and "f33_panda_lease.sh" in launcher)

print("\n== deployable car-kit packaging ==")
with tempfile.TemporaryDirectory() as td:
    kit_root = Path(td) / "kit"
    manifest = car_kit.build(kit_root, ROOT.parent / "kai-openpilot")
    packaged_payload = (kit_root / "ram_payloads/camry_f33_route40_observer_payload.bin").read_bytes()
    packaged_runtime = kit_root / "runtime/exploit/ephemeral_runtime/camry_f33_route40_observer.py"
    packaged_launcher = kit_root / "f33-route40"
    packaged_runbook = kit_root / "090_ROUTE40_EXPERIMENT.md"
    experiment = manifest["ram_experiments"]["valid_090_route40_experiment"]
    check("car kit packages exact route40 payload, runtime, and launcher",
          sha(packaged_payload) == observer.EXPECTED_PAYLOAD_SHA256 and
          packaged_runtime.read_bytes() == (ROOT / "exploit/ephemeral_runtime/camry_f33_route40_observer.py").read_bytes() and
          packaged_launcher.read_bytes() == (ROOT / "exploit/ephemeral_runtime/camry_f33_route40_observer_launcher.sh").read_bytes() and
          packaged_runbook.read_bytes() == (ROOT / "exploit/ephemeral_runtime/camry_f33_090_route40_experiment.md").read_bytes() and
          manifest["files"]["f33-route40"]["sha256"] == sha(packaged_launcher.read_bytes()))
    check("car-kit manifest exposes the definitive route40 decisions and boundaries",
          experiment["launcher"] == "f33-route40" and
          experiment["positive_verdict"] == "valid_authenticated_090_reached_f33_route40_raw_com" and
          experiment["bounded_negative_verdict"] == "valid_authenticated_090_not_latched_while_native_route40_remained_live" and
          experiment["observer_route_table_patch"] is False and
          experiment["observer_secoc_bypass"] is False and
          experiment["persistent_flash_write"] is False)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
