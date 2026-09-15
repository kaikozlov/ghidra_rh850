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
from tools.targets.crown.live import crown_f30_resident_soak as soak
from tools.targets.crown.live import crown_f30_diag_mailbox_probe as mailbox_probe

CONTRACT_BUILDER = ROOT / "tools/targets/crown/builders/build_crown_8965F3012000_b6_signer_contract.py"
CONTRACT = ROOT / "data/generated/crown_8965F3012000_b6_signer_contract.json"
SIGNER_BUILDER = ROOT / "exploit/ephemeral_runtime/build_crown_f30_b6_inline_signer.py"
KIT_BUILDER = ROOT / "tools/targets/crown/builders/build_crown_f30_car_kit.py"
PREFLIGHT = ROOT / "tools/targets/crown/live/crown_f30_diag_mailbox_probe.py"


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
    check("0x1DA private-mailbox premise is explicitly rejected",
          side["status"] == "rejected-as-idle-private-mailbox" and side["unused_wire_bytes"] == [1,2,3,4,5,6,7] and
          side["direct_snapshot_readers"] == [] and side["direct_raw_buffer_references"] == [] and
          "Do not transmit active 0x1DA sideband frames" in side["boundary"])
    guard = contract["vehicle_state_guard"]
    check("Crown READY/stationary guard is target-native and does not import F33 gear",
          guard["ready"] == {"can_id": "0x51E", "signal": 155, "unpacker": "0x0004ACD2", "wire": "B0[7]"} and
          guard["wheel_speed"]["raw_zero"] == 6767 and guard["wheel_speed"]["signals"] == [193,195,197,199] and
          "operator-confirmed" in guard["park"])
    check("legacy prototype carrier remains distinct from Camry C7 ingress", side["can_id"] == "0x1DA" and side["format"] == "classic")

    ingress = contract["functional_diagnostic_ingress"]
    check("stock functional 0x777 ingress is closed through DCM",
          ingress["can_id"] == "0x777" and ingress["wire"] == {
              "isotp": "single frame, PCI=0x07",
              "loader": "07 C6 index 00 word_le32",
              "runtime": "07 C7 seq 00 target_hi target_lo 00 00",
          } and ingress["application_route"]["cantp_rx_pdu"] == "0x0805" and
          ingress["application_route"]["pdur_rx_pdu"] == "0x0803" and
          ingress["application_route"]["dcm_buffer"] == "0xFEBE527D" and
          ingress["application_route"]["request_type"] == "functional" and
          ingress["application_route"]["dcm_tp_callbacks"] == {
              "start_of_reception": "0x0008FB5E",
              "copy_rx_data": "0x0008FBF2",
              "rx_indication": "0x0008FC72",
              "copy_engine": "0x00091888",
          })
    check("resident samples after TP delivery but before separate DCM-main service dispatch",
          ingress["service_semantics"]["rx_indication_dispatches_service_inline"] is False and
          ingress["service_semantics"]["dcm_main_worker"] == "0x0008F6AA" and
          ingress["service_semantics"]["service_dispatch"] == "0x0008F006" and
          "0x8F6AA -> 0x8F006" in ingress["resident_sampling_boundary"])
    check("C6/C7 are outside the exact functional service set and NRC11 is suppressed",
          ingress["service_semantics"]["descriptor_count"] == 23 and
          ingress["service_semantics"]["functional_service_ids"] == ["0x10", "0x14", "0x28", "0x31", "0x3E", "0x85"] and
          ingress["service_semantics"]["service_sets"][1] == {
              "message_channel_id": 3, "indices": [17, 2, 7, 9, 13, 14], "index_table": "0x00025928",
          } and ingress["service_semantics"]["c6_configured"] is False and
          ingress["service_semantics"]["c7_configured"] is False and
          ingress["service_semantics"]["unsupported_service_nrc"] == "0x11" and
          ingress["service_semantics"]["functional_nrc11_response"] == "suppressed")

    out = root / "build"
    result = subprocess.run([sys.executable, str(SIGNER_BUILDER), "--output-dir", str(out)], cwd=ROOT, check=True, capture_output=True, text=True)
    meta = json.loads(result.stdout)
    check("signer build schema/review boundary", meta["schema"] == "crown-f30-b6-inline-signer-build-v1" and meta["review_status"] == "firmware-closed-live-unqualified")
    check("resident fits reviewed high tail with diagnostic ingress", meta["resident"]["size"] == 522 and meta["resident"]["headroom"] == 2 and meta["resident"]["relocations"] == 0)
    check("helper fits reviewed low-RAM pocket", meta["helper"]["size"] == 588 and meta["helper"]["padded_size"] == 600 and meta["helper"]["word_count"] == 150 and meta["helper"]["relocations"] == 0)
    check("bootstrap payload remains 4 KiB authenticated RAM", meta["authenticated_payload"]["size"] == 0x1000)
    check("runtime carrier is stock functional classic bus1 0x777",
          meta["loader"]["can_id"] == "0x777" and meta["loader"]["extended"] is False and meta["loader"]["bus"] == 1 and
          meta["loader"]["dcm_buffer"] == "0xFEBE527D" and
          meta["loader"]["unsupported_service_response"] == "stock DCM functional NRC11 suppression")
    check("resident has no CAN transmitter / flash write / SecOC-result bypass",
          meta["mutation_boundary"]["can_transmit_from_resident"] is False and
          meta["mutation_boundary"]["flash_write"] is False and
          meta["mutation_boundary"]["secoc_result_override"] is False)
    check("native no-mutation oracle is mandatory before replacement", "require byte-exact" in meta["signer"]["native_oracle"] and meta["mutation_boundary"]["replacement_requires_native_mac_equality"] is True)

    payload = out / "crown_f30_b6_inline_signer_payload.bin"
    helper = out / "crown_f30_b6_inline_signer_helper_padded.bin"
    bundle = host.load_bundle(payload=payload, helper=helper, meta=out / "crown_f30_b6_inline_signer.json")
    legacy_meta_path = root / "legacy-carrier-meta.json"
    legacy_meta = json.loads((out / "crown_f30_b6_inline_signer.json").read_text())
    legacy_meta["loader"]["can_id"] = "0x1DA"
    legacy_meta_path.write_text(json.dumps(legacy_meta))
    try:
        host.load_bundle(payload=payload, helper=helper, meta=legacy_meta_path)
    except host.InlineSignerError as exc:
        check("host rejects stale 0x1DA bundle metadata", "control ingress metadata drift" in str(exc))
    else:
        raise AssertionError("host accepted stale 0x1DA bundle metadata")
    plan = host.plan(bundle)
    check("host binds stock-wire bus1 route", host.ROUTE.bus == 1 and host.ROUTE.elm327_param == 1)
    check("host exact F181 includes both Crown records",
          host.EXPECTED_F181_HEX == "023839363546333031323030300000000038413331313330303830303000000000")
    check("loader frame exact", host.loader_frame(word_index=3, word=bytes.fromhex("11223344")) == bytes.fromhex("07c6030011223344"))
    check("arm frame exact", host.loader_frame(word_index=0xFF) == bytes.fromhex("07c6ff0000000000"))
    check("runtime C7 frame preserves Camry C7 N-SDU semantics", host.replacement_frame(sequence=7, target_angle_raw=0x1234) == bytes.fromhex("07c7070012340000"))
    check("host control uses stock ELM diagnostic address", host.CONTROL_CAN_ID == 0x777 and host.FUNCTIONAL_DCM_BUFFER_BASE == 0xFEBE527D)
    host_source = (ROOT / "exploit/ephemeral_runtime/crown_f30_b6_inline_signer.py").read_text(encoding="utf-8")
    check("active Crown host stays on ELM327 and explicitly disables auto-FD",
          "monitor._alloutput_mode" not in host_source and host_source.count("set_canfd_auto(CONTROL_BUS, False)") == 2)
    check("plan makes functional mailbox proof the first vehicle action", "prove stock functional 0x777 mailbox delivery" in plan["sequence"][0])
    check("standalone mailbox probe frame exact", mailbox_probe.PROBE_FRAME == bytes.fromhex("07c7a50012340000"))
    check("mailbox tail witness tolerates stock DCM first-byte reset",
          mailbox_probe.mailbox_tail_matches(bytes.fromhex("00a50012340000")) and
          mailbox_probe.mailbox_tail_matches(bytes.fromhex("c7a50012340000")))

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
    check("standalone first-action probe is one stock diagnostic frame with no RAM/flash primitive",
          preflight_source.count("panda.can_send(") == 1 and "execute_ram_payload" not in preflight_source and
          "write_data_by_identifier" not in preflight_source and "transfer_data" not in preflight_source and
          "routine_control" not in preflight_source and "_alloutput_mode" not in preflight_source)

    kit = root / "kit"
    kit_result = subprocess.run([sys.executable, str(KIT_BUILDER), "--out", str(kit)], cwd=ROOT, check=True, capture_output=True, text=True)
    kit_meta = json.loads(kit_result.stdout)
    check("field kit is exact Crown/live-unqualified", kit_meta["schema"] == "crown-f30-car-kit-v1" and
          kit_meta["target"]["software_id"] == "8965F3012000" and kit_meta["review_status"] == "firmware-closed-live-unqualified")
    check("field kit includes functional-mailbox preflight, current-angle soak, and volatile signer entrypoint",
          (kit / "crown-tss3-signer").is_file() and
          (kit / "runtime/tools/targets/crown/live/crown_f30_diag_mailbox_probe.py").is_file() and
          (kit / "runtime/tools/targets/crown/live/crown_f30_resident_soak.py").is_file() and
          (kit / "runtime/tsk/lib/programming.py").is_file() and
          (kit / "runtime/tsk/lib/diagnostic_route.py").is_file() and
          (kit / "ram_payloads/crown_f30_b6_inline_signer_payload.bin").is_file())
    check("field kit vendors byte-exact field-proven programming handoff",
          kit_meta["programming_helper"]["source_commit"] == "fdded7183e41bed42d0c74b1a204e8883e543a6f" and
          kit_meta["programming_helper"]["files"]["tsk/lib/programming.py"]["sha256"] ==
              "ab6aba3b47cd4ab2fa2ad680504dfe9f013c7f936f02169ba3334c1435829905" and
          kit_meta["programming_helper"]["files"]["tsk/lib/diagnostic_route.py"]["sha256"] ==
              "703739d2257eb27fd0dfbfc60beea3883e661ae05f1ad6b04ee64e57c87c22d9")
    import_cmd = [sys.executable, "-c",
                  "from tsk.lib.programming import enter_programming_bootloader, uds_client; "
                  "from tsk.lib.diagnostic_route import rediscover_route"]
    imported = subprocess.run(import_cmd, cwd=kit, env={**__import__("os").environ, "PYTHONPATH": str(kit / "runtime")},
                              capture_output=True, text=True)
    check("field kit programming helper imports without a device tsk checkout", imported.returncode == 0)
    source_commit = (kit / "SOURCE_COMMIT").read_text(encoding="utf-8").strip()
    testing_text = (kit / "TESTING.txt").read_text(encoding="utf-8")
    check("field kit carries source revision and self-contained current instructions",
          kit_meta["source_commit"] == source_commit and len(source_commit) == 40 and
          "stock functional diagnostic path on classic CAN 0x777" in testing_text and
          "qualified=true" in testing_text and "stock_functional_mailbox_live" in testing_text and
          "safe_to_experiment" not in testing_text and
          "no TSKM reflash or separate tsk checkout is required" in testing_text)
    check("field kit usage orders mailbox preflight before install",
          kit_meta["usage"].index("NRTD/Park: ./crown-tss3-signer preflight /tmp/crown-preflight.json") <
          kit_meta["usage"].index("NRTD/Park: ./crown-tss3-signer install /tmp/crown-install.json"))
    launcher_text = (kit / "crown-tss3-signer").read_text(encoding="utf-8")
    check("field kit runtime precedes host openpilot on PYTHONPATH",
          'PYTHONPATH="$KIT_ROOT/runtime:$OPENPILOT_ROOT"' in launcher_text)
    # Reproduce mruno's actual shape: Sunnypilot provides panda/opendbc, while a
    # leftover partial host tsk package exists but lacks programming.py. The kit
    # must win package resolution so that stale host tsk cannot shadow it.
    fake_host = root / "fake-sunnypilot"
    (fake_host / "tsk/lib").mkdir(parents=True)
    (fake_host / "tsk/__init__.py").write_text("", encoding="utf-8")
    (fake_host / "tsk/lib/__init__.py").write_text("", encoding="utf-8")
    (fake_host / "tsk/lib/dump_dataflash.py").write_text("HOST_PARTIAL_TSK = True\n", encoding="utf-8")
    resolution = subprocess.run(
        [sys.executable, "-c",
         "import tsk.lib.programming as p, tsk.lib.diagnostic_route as d; "
         "print(p.__file__); print(d.__file__)"],
        cwd=kit, env={**__import__("os").environ, "PYTHONPATH": f"{kit / 'runtime'}:{fake_host}"},
        capture_output=True, text=True,
    )
    check("vendored tsk wins over incomplete host Sunnypilot tsk",
          resolution.returncode == 0 and str(kit / "runtime/tsk/lib/programming.py") in resolution.stdout and
          str(kit / "runtime/tsk/lib/diagnostic_route.py") in resolution.stdout)
    check("field kit makes current-angle replacement the first bounded command",
          "READY/Park/stationary: ./crown-tss3-signer replace-current /tmp/crown-replace-current.json" in kit_meta["usage"] and
          "replace-current" in launcher_text)
    check("field kit exposes repeated current-angle qualification without changing the resident",
          "soak-current" in launcher_text and
          any("soak-current" in row for row in kit_meta["usage"]))
    soak_tool = kit / "runtime/tools/targets/crown/live/crown_f30_resident_soak.py"
    soak_plan = subprocess.run([
        sys.executable, str(soak_tool),
        "--payload", str(kit / "ram_payloads/crown_f30_b6_inline_signer_payload.bin"),
        "--helper", str(kit / "ram_payloads/crown_f30_b6_inline_signer_helper_padded.bin"),
        "--meta", str(kit / "ram_payloads/crown_f30_b6_inline_signer.json"),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    soak_plan_json = json.loads(soak_plan.stdout)
    check("current-angle soak is inert without execute",
          soak_plan_json["schema"] == "crown-f30-b6-resident-current-angle-soak-plan-v1" and
          soak_plan_json["resident_bytes_modified"] is False and soak_plan_json["persistent_flash_writes"] is False)
    soak_state = {"initialized": True, "armed": True, "last_command5_rc": 0}
    soak_telemetry = {"native_verified_raw": 1, "last_done_flag": 1, "last_command_status": 0, "native_signature_match": False}
    soak_source = (ROOT / "tools/targets/crown/live/crown_f30_resident_soak.py").read_text(encoding="utf-8")
    check("current-angle soak uses sticky native oracle after a prior replacement",
          "session.wait_native_verification" not in soak_source and "native_verified_raw" in soak_source and "sticky_oracle" in soak_source)
    check("current-angle soak treats post-replacement trailer inequality as expected",
          soak.repeated_signing_qualified(state_after=soak_state, telemetry_after=soak_telemetry, signed_delta=10, attempt_delta=10))
    check("current-angle soak fails on command5/replacement count mismatch",
          not soak.repeated_signing_qualified(state_after=soak_state, telemetry_after=soak_telemetry, signed_delta=9, attempt_delta=10))

print("Crown F30 B6 inline signer verification passed.")
