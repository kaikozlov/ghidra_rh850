#!/usr/bin/env python3
"""Deterministically verify the exact-F33 stationary B6 bring-up probe."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "exploit/behavioral_proof/camry_f33_b6_stationary_probe.py"
SPEC = importlib.util.spec_from_file_location("camry_f33_b6_stationary_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = probe
SPEC.loader.exec_module(probe)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


print("== exact route / read surface ==")
plan = probe.build_plan()
check("exact-F33 full F181 identity is pinned", probe.EXPECTED_F181_HEX == "023839363546333330373030300000000038413331313333303331303000000000")
check("post-repin EPS diagnostics and B6 are both bus0", probe.DIAG_BUS == probe.B6_BUS == 0 and probe.EPS_TX == 0x7A1 and probe.EPS_RX == 0x7A9)
check("AllOutput passthrough parameter is explicit", probe.ALLOUTPUT_PASSTHROUGH_PARAM == 1 and plan["panda_safety"]["relay_forwarding"] == "bus0<->bus2 preserved")
check("B6 is fixed 32-byte CAN-FD at 50 Hz", probe.B6_ADDR == 0x0B6 and probe.B6_LEN == 32 and abs(probe.B6_PERIOD_S - 0.020) < 1e-12)
check("raw COM window is one B3..B31 read", probe.COM_WINDOW_WITNESS.address == 0xFEBE4C02 and
      probe.COM_WINDOW_WITNESS.length == 29 and plan["raw_com_window"]["length"] == 29)
check("every post-COM acceptance-ladder cell is exposed", [c.address for c in probe.LADDER_CELLS] == [
    0xFEBE5364, 0xFEBE7F68, 0xFEBE80BC, 0xFEBE80B8, 0xFEBE80C8, 0xFEBE80C9,
    0xFEBEF13E, 0xFEBEADB9, 0xFEBEADB0, 0xFEBEAE90, 0xFEBECAFF, 0xFEBEACBD,
    0xFEBECB00,
])
check("all ladder cells validate under existing SID23 RMBA policy", all(probe.validate_read(probe.RAM_ID, c.address, c.length) is None for c in probe.LADDER_CELLS))
check("RAM bridge telemetry cells are exact and readable", [c.address for c in probe.BRIDGE_TELEMETRY_CELLS] == [
    0xFEBFFBEC, 0xFEBFFBF0, 0xFEBFFBF4, 0xFEBFFBF8,
] and all(probe.validate_read(probe.RAM_ID, c.address, c.length) is None for c in probe.BRIDGE_TELEMETRY_CELLS))
check("non-bypassing observer telemetry is exact and readable",
      probe.OBSERVER_TELEMETRY_BASE == 0xFEBFFBE0 and probe.OBSERVER_TELEMETRY_SIZE == 28 and
      probe.validate_read(probe.RAM_ID, probe.OBSERVER_TELEMETRY_BASE, probe.OBSERVER_TELEMETRY_SIZE) is None)
check("wide command-funnel trace cells are exact and readable", [c.address for c in probe.TRACE_CELLS] == [
    0xFEBE5564, 0xFEBEC81A, 0xFEBECB38, 0xFEBECC48, 0xFEBECC50, 0xFEBECC60,
    0xFEBECC62, 0xFEBECC66, 0xFEBECC64, 0xFEBEAC54, 0xFEBEAC56,
] and all(probe.validate_read(probe.RAM_ID, c.address, c.length) is None for c in probe.TRACE_CELLS))
check("all four freshness slots are read in one exact 48-byte block",
      probe.FRESHNESS_STATE_BASE == 0xFEBE55DC and probe.FRESHNESS_STATE_SIZE == 48 and
      probe.validate_read(probe.RAM_ID, probe.FRESHNESS_STATE_BASE, probe.FRESHNESS_STATE_SIZE) is None)
check("plan names forbidden mutation surfaces", all(token in plan["forbidden"] for token in (
    "programming session", "SecurityAccess", "RequestDownload", "TransferData", "memory writes", "RoutineControl", "0x08A TX",
)))

print("\n== exact B6 wire vectors ==")
active = probe.build_b6_frame(target_id=11, target_raw=0x0123, sequence=5, message_counter=6, reset_low2=1)
inactive = probe.build_b6_frame(target_id=0, target_raw=-2, sequence=63, message_counter=7, reset_low2=3)
check("active vector byte-exact", active.hex() == "0000000b01230005646400000000000000000000000000000000000090000000")
check("active ID11 / target / clean companions", active[3] == 11 and active[4:6] == b"\x01\x23" and active[6] & 0x04 == 0 and active[8:10] == b"\x64\x64")
check("active zero-MAC28 keeps live FV4", (int.from_bytes(active[28:32], "big") & 0x0FFFFFFF) == 0 and active[28] >> 4 == 9)
check("inactive vector byte-exact", inactive.hex() == "00000000fffe043f0000000000000000000000000000000000000000f0000000")
check("inactive defaults suppress additive contribution", inactive[3] == 0 and inactive[6] & 0x04 and inactive[8:10] == b"\x00\x00")
try:
    probe.build_b6_frame(target_id=4, target_raw=0, sequence=0, message_counter=0, reset_low2=0)
except probe.ProbeError:
    check("probe rejects non-ID0/non-ID11 mode", True)
else:
    check("probe rejects non-ID0/non-ID11 mode", False)

print("\n== target-native observation decoders ==")
angle_frame = bytes.fromhex("000100005000007e" + "00" * 24)
check("0x025 decoder matches current safety formula", abs(probe.decode_steering_angle_deg(angle_frame) - 2.0) < 1e-12)
check("0x0AA parked frame decodes zero", probe.decode_wheel_speeds_kph(bytes.fromhex("1a6f1a6f1a6f1a6f")) == (0.0, 0.0, 0.0, 0.0))
check("0x127 Park decoder exact", probe.decode_gear(bytes.fromhex("00100000000ebe0c")) == 0)
check("0x00F reset counter decoder matches DBC", probe.decode_reset_counter(bytes.fromhex("01b20145cde4b47d")) == 0x145C)
check("B6 scale is exact fraction", abs(probe.B6_DEG_PER_COUNT - (1024 / 17870)) < 1e-15 and probe.angle_deg_to_raw(probe.B6_DEG_PER_COUNT) == 1)
step = probe.small_offset_step_raw()
check("small-offset raw ramp cannot exceed declared rate", step > 0 and (step * probe.B6_DEG_PER_COUNT / probe.B6_PERIOD_S) <= probe.SMALL_OFFSET_MAX_RATE_DEG_S)
check("raw ramp converges without overshoot", [probe.step_toward_raw(v, 5, 2) for v in (0, 4, 5, 7)] == [2, 5, 5, 5])
check("exact frame signature includes target, companion, sequence, FV, and MAC",
      probe.frame_signature(active) == (11, 0x123, 0, 5, 9, 0))
check("CAN-health delta is modular and cumulative-only", probe.can_health_delta(
    {"bus_off_cnt": 1, "transmit_error_cnt": 2, "total_error_cnt": 0xFFFFFFFE,
     "total_tx_cnt": 10, "last_error": "AckError"},
    {"bus_off_cnt": 1, "transmit_error_cnt": 4, "total_error_cnt": 1,
     "total_tx_cnt": 14, "last_error": "No error"},
) == {"bus_off_cnt": 0, "total_error_cnt": 3, "total_tx_cnt": 4})

print("\n== acceptance discriminator ==")
target = probe.angle_deg_to_raw(3.0)
phase_frame = probe.build_b6_frame(target_id=11, target_raw=target, sequence=9, message_counter=2, reset_low2=1)
phase_signature = probe.frame_signature(phase_frame)
sent_signatures = {phase_signature}
good = {
    "com_window_target_lateral_id": phase_signature[0], "com_window_target_angle_raw": phase_signature[1],
    "com_window_companion": phase_signature[2], "com_window_sequence": phase_signature[3],
    "com_window_fv4": phase_signature[4], "com_window_mac28": phase_signature[5],
    "com_rx_group_state": 0, "com_target_lateral_id": 11, "com_target_angle_raw": target,
    "consumed_generation": 7, "unpacker_status": 0, "staged_status": 0, "snapshot_status": 0,
    "target_lateral_id": 11, "target_angle_raw": target,
    "b6_controller_enable": 1, "global_comm_mode": 0, "controller_bank": 2,
}
check("positive ladder is ADMITTED", probe.verdict(
    good, target_id=11, target_raw=target, sent_signatures=sent_signatures) == {
    "admitted": True, "reason": "ADMITTED", "status_healthy": True,
    "com_window_payload_delivered": True, "com_signals_updated": True,
    "payload_delivered": True, "controller_enabled": True, "bank_selected": True,
})
def judge(**changes):
    return probe.verdict(dict(good, **changes), target_id=11, target_raw=target,
                         sent_signatures=sent_signatures)["reason"]
check("raw PDU44 signature miss is classified first",
      judge(com_window_sequence=(phase_signature[3] + 1) & 0x3F) == "pdu_not_copied_to_com_window")
check("current-angle alias without the phase sequence is rejected",
      judge(com_window_target_lateral_id=11, com_window_target_angle_raw=target,
            com_window_sequence=(phase_signature[3] + 1) & 0x3F) == "pdu_not_copied_to_com_window")
check("COM receive-group block is distinguished from failed PduR delivery",
      judge(com_target_lateral_id=0, com_rx_group_state=2) == "com_unpack_blocked_by_rx_group_state")
check("raw COM-to-generated-signal miss is distinguished",
      judge(com_target_lateral_id=0) == "com_window_not_unpacked")
check("generated-COM-to-snapshot miss is distinguished",
      judge(target_lateral_id=0) == "com_signals_not_snapshotted")
check("unhealthy receive status is classified", judge(snapshot_status=0x11) == "receive_status_unhealthy")
check("CAFF failure is classified", judge(b6_controller_enable=0) == "b6_controller_not_enabled")
check("ACBD failure is classified", judge(global_comm_mode=1) == "global_comm_mode_blocks_controller")
check("ID11 bank failure is classified", judge(controller_bank=7) == "id11_bank_not_selected")

print("\n== raw Panda safety envelope ==")
class FakePanda:
    def __init__(self):
        self.calls = []
    def can_send(self, addr, dat, bus, *, fd=False, timeout=10):
        self.calls.append((addr, bytes(dat), bus, fd, timeout))
    def can_recv(self):
        return []

with tempfile.TemporaryDirectory() as td:
    fake = FakePanda()
    state = probe.LiveState()
    log = probe.EventLog(Path(td) / "events.ndjson")
    wrapped = probe.LoggingPanda(fake, state, log)
    wrapped.can_send(0x0B6, active, 0, fd=True)
    check("B6 reaches Panda only with fd=True", fake.calls[-1][0:4] == (0x0B6, active, 0, True))
    try:
        wrapped.can_send(0x0B6, active, 0, fd=False)
    except probe.ProbeError:
        check("classic-CAN B6 is rejected before Panda", True)
    else:
        check("classic-CAN B6 is rejected before Panda", False)
    try:
        wrapped.can_send(0x08A, b"\x00" * 32, 0, fd=True)
    except probe.ProbeError:
        check("0x08A raw TX is impossible through wrapper", True)
    else:
        check("0x08A raw TX is impossible through wrapper", False)
    log.close()

source = MODULE_PATH.read_text(encoding="utf-8")
check("live B6 call explicitly passes fd=True", "panda.can_send(B6_ADDR, frame, B6_BUS, fd=True)" in source)
check("no programming-session enum is referenced", "PROGRAMMING" not in source)
check("no SecurityAccess API is referenced", "security_access" not in source.lower())
check("no download/transfer/write/routine diagnostic API is referenced", all(token not in source for token in (
    "request_download", "transfer_data", "write_data_by_identifier", "routine_control",
)))
check("small-offset actuation is hard-capped and rate-bounded", probe.SMALL_OFFSET_HARD_CAP_DEG == 2.0 and probe.SMALL_OFFSET_MAX_RATE_DEG_S == 6.0 and "ID11 current-angle was not ADMITTED" in source and "max_step_raw=small_offset_step_raw()" in source)
check("small-offset target is refreshed from immediate preflight", 'offset_start_raw = angle_deg_to_raw(offset_preflight["steering_angle_deg"])' in source)
check("bridge-required mode demands heartbeat progression and reports ingress counters", 'RAM bridge heartbeat did not advance' in source and
      'bridge_after_id0 = snapshot_bridge_telemetry' in source and 'bridge_after_id11 = snapshot_bridge_telemetry' in source)
check("observer-required mode is mutually exclusive with bridge and samples during each phase",
      'resident = parser.add_mutually_exclusive_group()' in source and '--require-observer' in source and
      'observe_transactions=args.require_observer' in source and 'observer_samples.append' in source)
check("phase snapshots include freshness and adjacent Toyota/chassis witnesses",
      'snapshot_freshness_state(uds_client, uds_mod, log)' in source and
      'upstream_08a_bus2' in source and 'chassis_081_bus0' in source and 'eps_030_bus0' in source)
check("each phase records supporting Panda CAN health without claiming ACK",
      'boundary="before"' in source and 'boundary="after"' in source and
      '"can_health": id11_health' in source and
      plan["panda_can_health"]["purpose"].endswith("not a physical-ACK witness"))
check("offset phase requires the bridge experiment",
      "small-offset phase requires the RAM route44 bridge experiment" in source)

observer_raw = bytearray(probe.OBSERVER_TELEMETRY_SIZE)
observer_raw[0:4] = (0x4F364250).to_bytes(4, "little")
observer_raw[4] = 1
observer_raw[8:16] = bytes.fromhex("07100000010a0101")
observer_raw[16:21] = bytes.fromhex("0bfff0003e")
observer_raw[24:28] = bytes.fromhex("d1234567")
observer_dec = probe.decode_observer_telemetry(bytes(observer_raw))
check("observer decoder recovers queue/security/wire identity",
      observer_dec["queue_seen"] and observer_dec["b6_target_id"] == 11 and observer_dec["b6_target_raw"] == -16 and
      observer_dec["b6_sequence"] == 62 and observer_dec["b6_fv4"] == 13 and observer_dec["b6_mac28"] == 0x1234567)
observer_signature = probe.observer_signature(observer_dec)
assert observer_signature is not None
matching_observer = dict(observer_dec, b6_mac28=0)
sent_observer = {probe.observer_signature(matching_observer)}
before_observer = dict(observer_dec, b6_target_id=0)
witness = probe.observer_phase_witness(before_observer, [matching_observer], sent_observer)
check("observer witness requires a new exact phase signature",
      witness["matches_phase"] is True and witness["baseline_collision"] is False)
collision = probe.observer_phase_witness(matching_observer, [matching_observer], sent_observer)
check("sticky matching baseline cannot masquerade as new phase ingress",
      collision["matches_phase"] is False and collision["baseline_collision"] is True)

sim = probe.simulate()
check("offline simulation reproduces positive/negative verdicts", sim["good_verdict"]["admitted"] is True and sim["bad_verdict"]["admitted"] is False)

print("\n== car-kit packaging ==")
builder_path = ROOT / "tools/build_camry_f33_car_kit.py"
builder_spec = importlib.util.spec_from_file_location("build_camry_f33_car_kit", builder_path)
assert builder_spec is not None and builder_spec.loader is not None
builder = importlib.util.module_from_spec(builder_spec)
sys.modules[builder_spec.name] = builder
builder_spec.loader.exec_module(builder)
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "kit"
    manifest = builder.build(out, Path("/Users/kai/dev/inspect/repos/kai-openpilot"))
    copied = out / MODULE_PATH.name
    runbook = (out / "RUNBOOK.md").read_text(encoding="utf-8")
    patch_runbook = (out / "FIRMWARE_PATCH.md").read_text(encoding="utf-8")
    check("kit copies the exact standalone probe", copied.read_bytes() == MODULE_PATH.read_bytes())
    check("kit manifest is self-contained v4 and binds exact route", manifest["schema"] == "camry-f33-car-kit-v4" and manifest["target"] == {
        "eps_f181": "8965F3307000", "eps_diag": "0x7A1->0x7A9 bus0", "b6": "0x0B6/32 FD bus0",
    })
    check("kit pins live persistence-verified stage5 as current firmware", manifest["current_firmware"] == {
        "stage": 5,
        "sha256": "669cedf8c8465ebfd02318cb7708b897b817bc3b40925c89743b64ce49aa01af",
        "crc_prefix": "0x1960380A", "crc_fixup": "0xE69FC7F5",
        "note": "live persistence-verified 2026-09-01; no further persistent patch is part of the observer experiment",
    })
    check("kit makes observer the first RAM experiment and bridge conditional",
          manifest["ram_experiments"]["observer"]["bypass"] is False and
          manifest["ram_experiments"]["observer"]["payload_sha256"] == "29841b4965c7a690d76e641efd2d950ab291cfb6332a8d806fa6930fdaecbbbb" and
          manifest["ram_experiments"]["bridge"]["payload_sha256"] == "e83c40e3332b55571a526c0b45952c3944b3c9c4f65f5f2bb6e566c1aeba1f04" and
          manifest["ram_experiments"]["order"][0] == "observer")
    check("historical flash package is explicitly not the next experiment", manifest["firmware_patch"]["historical_only"] is True)
    check("kit retains live stage2 source state only as historical patch evidence", manifest["firmware_patch"]["stage2_installed"] == {
        "sites": [{"address": "0x8F948", "bytes": "003a"}, {"address": "0x8F952", "bytes": "e001"}],
        "fixup": "0xD12ADB05",
        "sha256": builder.stage3.EXPECTED_STAGE2_SHA256,
    })
    check("kit pins root-result stage3 candidate", manifest["firmware_patch"]["stage3_candidate"] == {
        "address": "0x8F930", "bytes": "e00714d3", "final_prefix": "0x13ADA3CC", "final_fixup": "0xEC525C33",
    })
    check("kit carries exact stage2 source and stage3 final SHA", manifest["firmware_patch"]["source_image_sha256"] == builder.stage3.EXPECTED_STAGE2_SHA256 and manifest["firmware_patch"]["final_image_sha256"] == builder.stage3.EXPECTED_FINAL_SHA256)
    check("kit includes preflight/apply/restore/post-apply artifacts", all((out / rel).is_file() for rel in (
        "firmware_patch/payload-validate-only.bin", "firmware_patch/payload-apply.bin",
        "firmware_patch/restore/restore.json", "firmware_patch/post-apply/payload-validate-only.bin",
        "firmware_patch/generic_shellcode_template.bin",
    )))
    check("kit includes observer/bridge payloads and RAM runtime needed on comma", all((out / rel).is_file() for rel in (
        "ram_payloads/camry_f33_b6_transaction_observer_payload.bin",
        "ram_payloads/camry_f33_b6_bridge_payload.bin",
        "runtime/exploit/common/ram_exec.py", "runtime/exploit/common/payload_package.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_transaction_observer_install.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py",
        "runtime/exploit/patcher/deploy.py", "runtime/exploit/patcher/restore.py",
        "runtime/exploit/patcher/post_apply_verify.py", "runtime/tools/build_secoc_patch_manifest.py",
    )))
    runtime_source = (out / "runtime/exploit/common/ram_exec.py").read_text(encoding="utf-8")
    check("kit embeds fixed P1M-E roots without standalone secret files",
          "ba052435f8843f985fd1329d2b6117b0" in runtime_source and
          "f05f36b7d78c03e24ab4faef2a57d044" in runtime_source and
          not any("secret" in p.name.lower() for p in out.rglob("*")))
    check("field runbooks require no secret extraction, files, or environment",
          all(token not in runbook + patch_runbook for token in (
              "f33-boot-secret", "f33-payload-secret", "--boot-secret-file",
              "--security-secret-file", "--payload-secret-file",
              "TOYOTA_EPS_BOOT_SECRET_HEX", "TOYOTA_EPS_PAYLOAD_SECRET_HEX",
          )))
    check("patch runbook requires NRTD zero-write preflight before apply", "NRTD zero-write preflight" in patch_runbook and "If `apply_ready` is not exactly true, **do not APPLY**" in patch_runbook)
    check("patch runbook pins root patch and cumulative CRC", "0x8F930: E1 0F 14 D3 -> E0 07 14 D3" in patch_runbook and "8F948=003A" in patch_runbook and "8F952=E001" in patch_runbook and "EC525C33" in patch_runbook)
    check("patch runbook encodes proven NRTD lifecycle and stage3-only restore", "NRC `0x22` in READY" in patch_runbook and "Full OFF -> NRTD" in patch_runbook and "RESTORE reverses **stage 3 only**" in patch_runbook)
    check("kit manifest pins current opendbc and Panda revisions", len(manifest["repositories"]["opendbc"].get("head", "")) == 40 and len(manifest["repositories"]["panda"].get("head", "")) == 40)
    check("runbook is observer-first, bridge-second, bridge-only offset",
          "install the non-bypassing observer" in runbook and "--require-observer" in runbook and
          "Only after `observer.id11_phase.matches_phase == true`" in runbook and "--require-bridge" in runbook and
          "--small-offset-deg 0.5" in runbook and
          "Only if the immediately preceding **bridge** ID11/current-angle phase says `ADMITTED`" in runbook)
    check("runbook explicitly forbids another result-bit flash patch",
          "do not add another persistent result-bit patch" in runbook and
          "historical/recovery artifacts" in runbook and "pre-`0x667E6` SecOC queue sample point" in runbook)
    check("runbook states the bounded steering ramp", "rate-limits" in runbook and "6 deg/s" in runbook)
    check("runbook rejects target-angle and CAN-health false proof",
          "one B3..B31 raw PDU44 COM read" in runbook and "FEBE7F68" in runbook and
          "supporting evidence, not physical-ACK proof" in runbook and
          "current-angle alone is no longer accepted" in runbook and "matches_phase" in runbook)
    check("runbook pins current bus0 and exclusive Panda ownership", "current post-repin" in runbook and "Panda bus 0" in runbook and "pandad|boardd" in runbook)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
