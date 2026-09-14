#!/usr/bin/env python3
"""Verify the exact-Crown volatile native-B6 signer build and fail-closed host contract."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import crown_f30_b6_inline_signer as host

CONTRACT_BUILDER = ROOT / "tools/targets/crown/builders/build_crown_8965F3012000_b6_signer_contract.py"
CONTRACT = ROOT / "data/generated/crown_8965F3012000_b6_signer_contract.json"
SIGNER_BUILDER = ROOT / "exploit/ephemeral_runtime/build_crown_f30_b6_inline_signer.py"
KIT_BUILDER = ROOT / "tools/targets/crown/builders/build_crown_f30_car_kit.py"
PREFLIGHT = ROOT / "tools/targets/crown/live/crown_f30_sideband_preflight.py"


def check(label: str, cond: object) -> None:
    if not cond:
        raise AssertionError(label)
    print(f"[PASS] {label}")


with tempfile.TemporaryDirectory(prefix="verify-crown-f30-signer-") as td:
    root = Path(td)
    regen = root / "contract.json"
    subprocess.run([sys.executable, str(CONTRACT_BUILDER), "--out", str(regen)], cwd=ROOT, check=True, capture_output=True, text=True)
    check("static contract regenerates byte-exact", regen.read_bytes() == CONTRACT.read_bytes())
    contract = json.loads(regen.read_text())
    check("exact Crown target identity", contract["target"] == {
        "codeflash_sha256": "5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273",
        "gp": "0xFEBEB800", "mcu": "R7F701381", "secondary_id": "8A3113008000",
        "software_id": "8965F3012000", "tp": "0x00023C98",
    })
    check("Crown slot4/B6 geometry closed",
          contract["secoc"]["key_config"] == {"address": "0x00025564", "selector": 4, "type": 1} and
          contract["secoc"]["b6_queue_record"] == "0xFEBE4FA6" and
          contract["secoc"]["b6_secured_buffer"] == "0xFEBE5000")
    b6 = contract["b6_application"]
    check("Crown B6 lateral tuple is firmware-derived",
          b6["target_lateral_id"]["wire"] == "B3[5:0]" and b6["target_lateral_id"]["id11_bank"] == 2 and
          b6["target_angle"]["wire"] == "B4:B5 signed16" and
          b6["signal259"] == {"replacement_value": 0, "wire": "B6[2]"} and
          b6["contribution_1"]["replacement_value"] == b6["contribution_2"]["replacement_value"] == 100)
    scale = contract["target_angle_scaling"]
    check("Crown B6 target-angle controller scale is exact",
          scale["physical_scale_closed"] is True and
          scale["controller_equivalent_fraction_deg_per_b6_count"] == {"numerator": 1024, "denominator": 17870} and
          abs(scale["controller_equivalent_deg_per_b6_count"] - (1024 / 17870)) < 1e-15 and
          abs(scale["controller_equivalent_mrad_per_b6_count"] - 1.0001215187701138) < 1e-12)
    check("Crown target/measured scaling proof is target-native",
          scale["functions"] == {
              "b6_target_scale": "0x000C9B64", "b6_unpack": "0x0004B608", "did1037": "0x0004D550",
              "fd025_stage": "0x0004749C", "fd025_unpack": "0x0004AEF8", "matched_comparator": "0x000C9D7E",
              "measured_reconstruct": "0x000CB640", "measured_republish": "0x000CB730",
          } and "1787 / 512" in scale["measured_internal_relation"] and "same 0xB76/0x400 gain" in scale["matched_controller"])
    side = contract["sideband_candidate"]
    check("0x1DA sideband is explicitly candidate/live-gated",
          side["status"] == "firmware-qualified-live-conflict-gated" and side["unused_wire_bytes"] == [1,2,3,4,5,6,7] and
          side["direct_snapshot_readers"] == [] and side["direct_raw_buffer_references"] == [] and
          "live preflight is mandatory" in side["boundary"])
    guard = contract["vehicle_state_guard"]
    check("Crown READY/stationary guard is target-native and does not import F33 gear",
          guard["ready"] == {"can_id": "0x51E", "signal": 155, "unpacker": "0x0004ACD2", "wire": "B0[7]"} and
          guard["wheel_speed"]["raw_zero"] == 6767 and guard["wheel_speed"]["signals"] == [193,195,197,199] and
          "operator-confirmed" in guard["park"])
    check("Camry XCP/C7 ingress is not silently transferred", side["can_id"] == "0x1DA" and side["format"] == "classic")

    out = root / "build"
    result = subprocess.run([sys.executable, str(SIGNER_BUILDER), "--output-dir", str(out)], cwd=ROOT, check=True, capture_output=True, text=True)
    meta = json.loads(result.stdout)
    check("signer build schema/review boundary", meta["schema"] == "crown-f30-b6-inline-signer-build-v1" and meta["review_status"] == "firmware-closed-live-unqualified")
    check("resident exactly fills reviewed high tail", meta["resident"]["size"] == 524 and meta["resident"]["headroom"] == 0 and meta["resident"]["relocations"] == 0)
    check("helper fits reviewed low-RAM pocket", meta["helper"]["size"] == 590 and meta["helper"]["padded_size"] == 600 and meta["helper"]["word_count"] == 150 and meta["helper"]["relocations"] == 0)
    check("bootstrap payload remains 4 KiB authenticated RAM", meta["authenticated_payload"]["size"] == 0x1000)
    check("runtime carrier is classic bus1 0x1DA with mandatory live conflict gate",
          meta["loader"]["can_id"] == "0x1DA" and meta["loader"]["extended"] is False and meta["loader"]["bus"] == 1 and
          meta["loader"]["live_source_conflict_gate"].startswith("mandatory"))
    check("resident has no CAN transmitter / flash write / SecOC-result bypass",
          meta["mutation_boundary"]["can_transmit_from_resident"] is False and
          meta["mutation_boundary"]["flash_write"] is False and
          meta["mutation_boundary"]["secoc_result_override"] is False)
    check("native no-mutation oracle is mandatory before replacement", "require byte-exact" in meta["signer"]["native_oracle"] and meta["mutation_boundary"]["replacement_requires_native_mac_equality"] is True)

    payload = out / "crown_f30_b6_inline_signer_payload.bin"
    helper = out / "crown_f30_b6_inline_signer_helper_padded.bin"
    bundle = host.load_bundle(payload=payload, helper=helper, meta=out / "crown_f30_b6_inline_signer.json")
    plan = host.plan(bundle)
    check("host binds stock-wire bus1 route", host.ROUTE.bus == 1 and host.ROUTE.elm327_param == 1)
    check("host exact F181 includes both Crown records",
          host.EXPECTED_F181_HEX == "023839363546333031323030300000000038413331313330303830303000000000")
    check("loader frame exact", host.loader_frame(word_index=3, word=bytes.fromhex("11223344")) == bytes.fromhex("00c65a1122334403"))
    check("arm frame exact", host.loader_frame(word_index=0xFF) == bytes.fromhex("00c65a00000000ff"))
    check("runtime C7 frame exact", host.replacement_frame(sequence=7, target_angle_raw=0x1234) == bytes.fromhex("00c75a1234000007"))
    check("plan keeps first live action passive", "passively prove no native bus1 0x1DA" in plan["sequence"][2])

    class FakePanda:
        def __init__(self, rows): self.rows = list(rows)
        def can_recv(self):
            rows, self.rows = self.rows, []
            return rows

    class FakeSession:
        uds_mod = object()
        client = object()
        panda = FakePanda([])

    original_read = host._read_memory
    try:
        values = iter((b"\x17", b"\x17"))
        host._read_memory = lambda *a, **k: next(values)
        idle = host.InlineSignerSession.require_idle_sideband(FakeSession(), duration=0.001)
        check("passive sideband gate accepts stable no-frame window", idle["eps_generation_stable"] and not idle["native_frames"])

        values = iter((b"\x17", b"\x18"))
        host._read_memory = lambda *a, **k: next(values)
        try:
            host.InlineSignerSession.require_idle_sideband(FakeSession(), duration=0.001)
        except host.InlineSignerError as exc:
            check("passive sideband gate rejects hidden EPS generation movement", "not idle" in str(exc))
        else:
            raise AssertionError("Crown sideband gate accepted generation movement")

        values = iter((b"\x17", b"\x17"))
        host._read_memory = lambda *a, **k: next(values)
        active = FakeSession(); active.panda = FakePanda([(0x1DA, 0, b"\0" * 8, 1)])
        try:
            host.InlineSignerSession.require_idle_sideband(active, duration=0.001)
        except host.InlineSignerError as exc:
            check("passive sideband gate rejects native bus1 0x1DA", "not idle" in str(exc))
        else:
            raise AssertionError("Crown sideband gate accepted native 0x1DA")
    finally:
        host._read_memory = original_read

    class GuardPanda:
        def __init__(self, rows): self.rows = list(rows)
        def can_recv(self):
            rows, self.rows = self.rows, []
            return rows

    def wheel_frame(raw_values):
        out = bytearray()
        for raw in raw_values:
            out += bytes(((raw >> 8) & 0x7F, raw & 0xFF))
        return bytes(out)

    zero_angle = bytes(32)
    ready_rows = [
        (0x51E, 0, bytes.fromhex("8000000000000000"), 1),
        (0x0AA, 0, wheel_frame([6767, 6767, 6767, 6767]), 1),
        (0x025, 0, zero_angle, 1),
    ]
    g = host.verify_crown_ready_stationary_on_panda(GuardPanda(ready_rows), timeout=0.01)
    check("Crown READY/stationary guard accepts exact centered wheel raw",
          g["wheel_centered_raw"] == [0,0,0,0] and g["steering_angle_deg"] == 0.0 and
          g["recommended_current_target_raw"] == 0 and "operator-confirmed" in g["park"])
    moving_rows = [
        (0x51E, 0, bytes.fromhex("8000000000000000"), 1),
        (0x0AA, 0, wheel_frame([6867, 6767, 6767, 6767]), 1),
        (0x025, 0, zero_angle, 1),
    ]
    try:
        host.verify_crown_ready_stationary_on_panda(GuardPanda(moving_rows), timeout=0.01)
    except host.InlineSignerError as exc:
        check("Crown READY/stationary guard rejects off-center wheel raw", "stationary guard" in str(exc))
    else:
        raise AssertionError("Crown stationary guard accepted moving raw wheel value")

    angle = bytearray(32)
    angle[1] = 1       # coarse +1 => +1.5 deg
    angle[4] = 0x50    # fraction +5 => +0.5 deg
    check("Crown 0x025 decoder reconstructs coarse+fraction", host.decode_crown_steering_angle_deg(bytes(angle)) == 2.0)
    check("Crown physical B6 conversion uses exact 1024/17870 scale",
          host.target_raw_from_degrees(0.0) == 0 and host.target_raw_from_degrees(2.0) == 35 and
          abs(host.target_degrees_from_raw(35) - (35 * 1024 / 17870)) < 1e-15)
    angle_rows = [
        (0x51E, 0, bytes.fromhex("8000000000000000"), 1),
        (0x0AA, 0, wheel_frame([6767, 6767, 6767, 6767]), 1),
        (0x025, 0, bytes(angle), 1),
    ]
    current = host.verify_crown_ready_stationary_on_panda(GuardPanda(angle_rows), timeout=0.01)
    check("current-angle guard recommends nearest B6 raw target",
          current["steering_angle_deg"] == 2.0 and current["recommended_current_target_raw"] == 35 and
          abs(current["recommended_current_target_deg"] - host.target_degrees_from_raw(35)) < 1e-15)

    preflight_source = PREFLIGHT.read_text(encoding="utf-8")
    check("standalone first-action preflight has no CAN/application write primitive",
          ".can_send(" not in preflight_source and "write_data_by_identifier" not in preflight_source and
          "transfer_data" not in preflight_source and "routine_control" not in preflight_source)

    kit = root / "kit"
    kit_result = subprocess.run([sys.executable, str(KIT_BUILDER), "--out", str(kit)], cwd=ROOT, check=True, capture_output=True, text=True)
    kit_meta = json.loads(kit_result.stdout)
    check("field kit is exact Crown/live-unqualified", kit_meta["schema"] == "crown-f30-car-kit-v1" and
          kit_meta["target"]["software_id"] == "8965F3012000" and kit_meta["review_status"] == "firmware-closed-live-unqualified")
    check("field kit includes passive preflight and volatile signer entrypoint",
          (kit / "crown-tss3-signer").is_file() and
          (kit / "runtime/tools/targets/crown/live/crown_f30_sideband_preflight.py").is_file() and
          (kit / "ram_payloads/crown_f30_b6_inline_signer_payload.bin").is_file())
    check("field kit usage orders passive preflight before install",
          kit_meta["usage"].index("NRTD/Park: ./crown-tss3-signer preflight /tmp/crown-preflight.json") <
          kit_meta["usage"].index("NRTD/Park: ./crown-tss3-signer install /tmp/crown-install.json"))
    check("field kit makes current-angle replacement the first bounded command",
          "READY/Park/stationary: ./crown-tss3-signer replace-current /tmp/crown-replace-current.json" in kit_meta["usage"] and
          "replace-current" in (kit / "crown-tss3-signer").read_text(encoding="utf-8"))

print("Crown F30 B6 inline signer verification passed.")
