#!/usr/bin/env python3
"""Deterministically verify the exact-F33 stationary B6 bring-up probe."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
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
    0xFEBE5364, 0xFEBE5360, 0xFEBE5361, 0xFEBE5365, 0xFEBE7F68, 0xFEBE80BC,
    0xFEBE80B8, 0xFEBE80C8, 0xFEBE80C9, 0xFEBEF13E, 0xFEBEADB9, 0xFEBEADB0,
    0xFEBEAE90, 0xFEBECAFF, 0xFEBEACBD, 0xFEBECB00,
])
check("all ladder cells validate under existing SID23 RMBA policy", all(probe.validate_read(probe.RAM_ID, c.address, c.length) is None for c in probe.LADDER_CELLS))
check("RAM bridge telemetry cells are exact and readable", [c.address for c in probe.BRIDGE_TELEMETRY_CELLS] == [
    0xFEBFFBEC, 0xFEBFFBF0, 0xFEBFFBF4, 0xFEBFFBF8,
] and all(probe.validate_read(probe.RAM_ID, c.address, c.length) is None for c in probe.BRIDGE_TELEMETRY_CELLS))
check("non-bypassing observer telemetry is exact and readable",
      probe.OBSERVER_TELEMETRY_BASE == 0xFEBFFBE0 and probe.OBSERVER_TELEMETRY_SIZE == 28 and
      probe.validate_read(probe.RAM_ID, probe.OBSERVER_TELEMETRY_BASE, probe.OBSERVER_TELEMETRY_SIZE) is None)
check("freshness and command-funnel trace cells are exact and readable", [c.address for c in probe.TRACE_CELLS] == [
    0xFEBE5564, 0xFEBE551A, 0xFEBE5526, 0xFEBEC81A, 0xFEBECB38, 0xFEBECC48,
    0xFEBECC50, 0xFEBECC60, 0xFEBECC62, 0xFEBECC66, 0xFEBECC64, 0xFEBEAC54,
    0xFEBEAC56,
] and all(probe.validate_read(probe.RAM_ID, c.address, c.length) is None for c in probe.TRACE_CELLS))
check("committed and pending freshness pairs are read in one exact 48-byte block",
      probe.FRESHNESS_STATE_BASE == 0xFEBE55DC and probe.FRESHNESS_STATE_SIZE == 48 and
      plan["freshness_state"]["layout"] == "committed0[12], committed1[12], pending0[12], pending1[12]" and
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
phase_payload = phase_frame[3:]
sent_payloads = {phase_payload}
baseline_payload = b"\xff" * probe.COM_WINDOW_WITNESS.length
good = {
    "com_window_b3_b31_hex": phase_payload.hex(),
    "com_window_target_lateral_id": phase_signature[0], "com_window_target_angle_raw": phase_signature[1],
    "com_window_companion": phase_signature[2], "com_window_sequence": phase_signature[3],
    "com_window_fv4": phase_signature[4], "com_window_mac28": phase_signature[5],
    "com_rx_group_state": 0, "com_target_lateral_id": 11, "com_target_angle_raw": target,
    "consumed_generation": 7, "unpacker_status": 0, "staged_status": 0, "snapshot_status": 0,
    "target_lateral_id": 11, "target_angle_raw": target,
    "b6_controller_enable": 1, "global_comm_mode": 0, "controller_bank": 2,
}
check("positive ladder is ADMITTED", probe.verdict(
    good, target_id=11, target_raw=target,
    sent_payloads=sent_payloads, baseline_payload=baseline_payload) == {
    "admitted": True, "reason": "ADMITTED", "status_healthy": True,
    "com_window_payload_delivered": True, "com_window_baseline_collision": False,
    "com_signals_updated": True, "payload_delivered": True,
    "controller_enabled": True, "bank_selected": True,
})
def judge(*, raw_payload=phase_payload, baseline=baseline_payload, **changes):
    return probe.verdict(
        dict(good, com_window_b3_b31_hex=raw_payload.hex(), **changes),
        target_id=11, target_raw=target,
        sent_payloads=sent_payloads, baseline_payload=baseline,
    )["reason"]
sequence_miss = bytearray(phase_payload)
sequence_miss[4] = (sequence_miss[4] + 1) & 0x3F
check("raw PDU44 payload miss is classified first",
      judge(raw_payload=bytes(sequence_miss)) == "pdu_not_copied_to_com_window")
omitted_field_miss = bytearray(phase_payload)
omitted_field_miss[5] ^= 0x01
check("bytes omitted from the compact signature still require exact equality",
      probe.frame_signature(b"\x00\x00\x00" + bytes(omitted_field_miss)) == phase_signature and
      judge(raw_payload=bytes(omitted_field_miss)) == "pdu_not_copied_to_com_window")
check("current-angle alias without the exact phase payload is rejected",
      judge(raw_payload=bytes(sequence_miss), com_window_target_lateral_id=11,
            com_window_target_angle_raw=target) == "pdu_not_copied_to_com_window")
check("a matching stale phase baseline is not delivery proof",
      judge(baseline=phase_payload) == "pdu_not_copied_to_com_window")
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
check("bridge-required mode demands heartbeat progression and reports ingress counters",
      'RAM bridge heartbeat did not advance' in source and
      'snapshot_bridge_telemetry(uds_client, uds_mod, log)' in source and
      '"after_id0": bridge_after["id0"]' in source and '"after_id11": bridge_after["id11"]' in source)
check("observer-required mode is mutually exclusive with bridge and samples during each phase",
      'resident = parser.add_mutually_exclusive_group()' in source and '--require-observer' in source and
      'observe_transactions=args.require_observer' in source and 'observer_samples.append' in source)
check("phase order is explicit and supports active-first carryover testing",
      plan["phases"]["default_order"] == "id0-id11" and plan["phases"]["alternate_order"] == "id11-id0" and
      '"--phase-order", choices=("id0-id11", "id11-id0")' in source)
check("phase snapshots include freshness, retry/profile state, and adjacent CAN witnesses",
      'snapshot_freshness_state(uds_client, uds_mod, log)' in source and
      'secoc_freshness_retry_budget' in source and 'b6_profile_state' in source and
      'upstream_08a_bus2' in source and 'chassis_081_bus0' in source and 'eps_030_bus0' in source)
check("each phase records supporting Panda CAN health without claiming ACK",
      'boundary="before"' in source and 'boundary="after"' in source and
      '"can_health": health' in source and
      plan["panda_can_health"]["purpose"].endswith("not a physical-ACK witness"))
check("offset phase requires the bridge experiment",
      "small-offset phase requires the RAM route44 bridge experiment" in source)

observer_raw = bytearray(probe.OBSERVER_TELEMETRY_SIZE)
observer_raw[0:4] = (0x4F364250).to_bytes(4, "little")
observer_raw[4] = 3
observer_raw[5] = 9
observer_raw[8:10] = bytes((0xD2, 0xE1))
observer_raw[10:12] = (0).to_bytes(2, "little")
observer_raw[12] = 1
observer_raw[16:21] = bytes.fromhex("0bfff0003e")
observer_raw[24:28] = bytes.fromhex("d1234567")
observer_dec = probe.decode_observer_telemetry(bytes(observer_raw))
check("observer decoder recovers queue/control/security/wire identity",
      observer_dec["queue_samples"] == 3 and observer_dec["d7_queue_samples"] == 9 and
      observer_dec["pre_profile_state"] == 0xD2 and observer_dec["post_profile_state"] == 0xE1 and
      observer_dec["b6_target_id"] == 11 and observer_dec["b6_target_raw"] == -16 and
      observer_dec["b6_sequence"] == 62 and observer_dec["b6_fv4"] == 13 and
      observer_dec["b6_mac28"] == 0x1234567)
matching_observer = dict(observer_dec, b6_mac28=0, queue_samples=4, d7_queue_samples=10)
sent_observer = {probe.observer_signature(matching_observer)}
before_observer = dict(observer_dec, b6_target_id=0)
witness = probe.observer_phase_witness(before_observer, [matching_observer], sent_observer)
check("observer witness requires counter movement plus a new exact phase signature",
      witness["matches_phase"] is True and witness["queue_activity"] is True and
      witness["queue_sample_delta_mod256"] == 1 and witness["d7_queue_sample_delta_mod256"] == 1 and
      witness["baseline_collision"] is False)
collision_after = dict(matching_observer, queue_samples=5)
collision = probe.observer_phase_witness(matching_observer, [collision_after], sent_observer)
check("matching baseline cannot masquerade as new phase ingress",
      collision["matches_phase"] is False and collision["baseline_collision"] is True)

sim = probe.simulate()
check("offline simulation reproduces positive/negative verdicts", sim["good_verdict"]["admitted"] is True and sim["bad_verdict"]["admitted"] is False)

print("\n== ABI-preserving runtime/source-term discriminator ==")
from exploit.common.payload_package import inspect_payload, package_shellcode
from exploit.ephemeral_runtime import build_camry_f33_runtime_replay_discriminator as replay_builder
from exploit.ephemeral_runtime import camry_f33_runtime_replay_discriminator as replay_runner
replay_source = (ROOT / "exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.S").read_text()
replay_builder_path = ROOT / "exploit/ephemeral_runtime/build_camry_f33_runtime_replay_discriminator.py"
replay_audit = json.loads((ROOT / "exploit/ephemeral_runtime/audited_camry_f33_runtime_replay_discriminator_build.json").read_text())
replay_staging = (ROOT / "exploit/ephemeral_runtime/audited/camry_f33_runtime_replay_discriminator.bin").read_bytes()
sha = lambda b: hashlib.sha256(b).hexdigest()
check("runtime discriminator audited v2 source/builder binding",
      replay_audit["schema"] == "camry-f33-runtime-replay-discriminator-build-v2" and
      replay_audit["source"]["sha256"] == sha((ROOT / replay_audit["source"]["path"]).read_bytes()) and
      replay_audit["builder"]["sha256"] == sha(replay_builder_path.read_bytes()))
check("runtime discriminator staging/resident identities and tail fit",
      len(replay_staging) == replay_audit["staging"]["size"] == 534 and
      sha(replay_staging) == replay_runner.EXPECTED_STAGING_SHA256 and
      replay_audit["resident"]["size"] == replay_runner.RESIDENT_SIZE == 406 and
      replay_audit["resident"]["headroom"] == 118 and replay_audit["resident"]["relocations"] == 0 and
      replay_audit["resident"]["sha256"] == replay_runner.EXPECTED_RESIDENT_SHA256)
check("runtime discriminator uses exact direct-JARL target order without C trampoline",
      "call0" not in replay_source and replay_source.count("jarl32 ") == 33 and
      replay_audit["resident"]["jarl_targets"] == [f"0x{x:08X}" for x in replay_builder.EXPECTED_RESIDENT_JARL_TARGETS])
check("runtime discriminator first observer write is gated to count 224",
      replay_source.index("tst1 7, 0[ep]") < replay_source.index("tst1 6, 0[ep]") <
      replay_source.index("tst1 5, 0[ep]") < replay_source.index("st.w r2, 0[sp]") and
      replay_runner.FIRST_SNAPSHOT_TICK == 224)
try:
    replay_builder.verify_static_contract((ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes())
    replay_static_ok = True
except Exception as exc:
    print(f"runtime discriminator static contract error: {exc}")
    replay_static_ok = False
check("runtime discriminator exact F33 startup/foreground/MPU/source-term guards", replay_static_ok)
replay_payload = package_shellcode(replay_staging, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
replay_inspection = inspect_payload(replay_payload, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
check("runtime discriminator authenticated payload identity exact",
      sha(replay_payload) == replay_runner.EXPECTED_PAYLOAD_SHA256 and replay_inspection.cmac_valid and
      replay_inspection.crc_residue == 0xFFFFFFFF and replay_inspection.callback_address == 0xFEBF0000)
raw = bytearray(replay_runner.MAILBOX_SIZE)
raw[0:4] = replay_runner.MAILBOX_MAGIC.to_bytes(4, "little"); raw[4] = raw[0x24] = 0xE7
for name, offset, width, signed in replay_runner.MAILBOX_FIELDS:
    value = -3 if signed else 3
    raw[offset:offset+width] = value.to_bytes(width, "little", signed=signed)
check("runtime discriminator mailbox decoder fails closed on torn snapshots",
      replay_runner.decode_mailbox(bytes(raw))["coherent"] is True and
      replay_runner.decode_mailbox(bytes(raw[:0x24] + bytes((0xE6,))))["coherent"] is False)
replay_plan = replay_runner.plan(None)
check("runtime discriminator plan exposes guarded READY read-existing follow-up",
      replay_plan["schema"] == "camry-f33-runtime-replay-discriminator-run-v3" and
      replay_plan["ready_read_existing"]["ram_execute"] is False and
      replay_plan["ready_read_existing"]["writes"] is False and
      replay_plan["ready_read_existing"]["success_verdict"] == "ready_parked_source_terms_live" and
      "Park" in replay_plan["live_guards"]["ready_read_existing"])
zero_speed = bytes.fromhex("1a6f1a6f1a6f1a6f")
check("READY parked guard decoders pin zero wheel speed and Park code",
      replay_runner.decode_wheel_speeds_kph(zero_speed) == (0.0, 0.0, 0.0, 0.0) and
      replay_runner.decode_gear(bytes(8)) == 0)

print("\n== generic external-control runtime monitor ==")
from exploit.ephemeral_runtime import camry_f33_runtime_monitor as monitor
monitor_source_path = ROOT / "exploit/ephemeral_runtime/camry_f33_runtime_monitor.S"
monitor_builder_path = ROOT / "exploit/ephemeral_runtime/build_camry_f33_runtime_monitor.py"
monitor_audit_path = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_runtime_monitor_build.json"
monitor_stage_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_runtime_monitor.bin"
monitor_source = monitor_source_path.read_text()
monitor_audit = json.loads(monitor_audit_path.read_text())
monitor_stage = monitor_stage_path.read_bytes()
monitor_resident = monitor_stage[0x80:0x80 + monitor.RESIDENT_SIZE]
check("generic monitor audited binary and source identities exact",
      monitor_audit["schema"] == "camry-f33-runtime-monitor-build-v1" and
      monitor_audit["source"]["sha256"] == sha(monitor_source_path.read_bytes()) and
      monitor_audit["builder"]["sha256"] == sha(monitor_builder_path.read_bytes()) and
      sha(monitor_stage) == monitor.EXPECTED_STAGING_SHA256 and
      sha(monitor_resident) == monitor.EXPECTED_RESIDENT_SHA256)
check("generic monitor fits proven high tail and keeps direct stock-call semantics",
      monitor.RESIDENT_SIZE == monitor_audit["resident"]["size"] == 520 and
      monitor_audit["resident"]["headroom"] == 4 and monitor_audit["resident"]["relocations"] == 0 and
      "call0" not in monitor_source and monitor_source.count("jarl32 ") == 33)
check("generic monitor control protocol is exact non-XCP extended-CAN shape",
      monitor.CONTROL_CAN_ID == 0x1FDC0002 and
      monitor.command_frame(0x23, 0x12, 0xFEBECC48) == bytes.fromhex("00f3231248ccbefe"))
check("generic monitor host bounds and aligns LocalRAM windows",
      monitor.validate_window(0xFEBEAC2B) == 0xFEBEAC28 and monitor.validate_window(0) == 0)
try:
    monitor.validate_window(0x12345678)
    monitor_bad_addr_rejected = False
except monitor.MonitorError:
    monitor_bad_addr_rejected = True
check("generic monitor rejects non-LocalRAM host watch addresses", monitor_bad_addr_rejected)
block_raw = bytearray(monitor.CONTROL_BLOCK_SIZE)
block_raw[0:4] = monitor.MONITOR_MAGIC.to_bytes(4, "little")
block_raw[4] = monitor.MONITOR_VERSION
block_raw[5] = 7
block_raw[8:12] = (9).to_bytes(4, "little")
block_raw[0x10:0x14] = (0xFEBECC48).to_bytes(4, "little")
block_raw[0x30:0x34] = (9).to_bytes(4, "little")
block_raw[0x34:0x38] = (0x89ABCDEF).to_bytes(4, "little")
block_raw[0x54:0x58] = (9).to_bytes(4, "little")
monitor_decoded = monitor.decode_control_block(bytes(block_raw))
check("generic monitor decoder recovers coherent dynamic watch snapshot",
      monitor_decoded["magic_ok"] and monitor_decoded["version_ok"] and monitor_decoded["snapshot_coherent"] and
      monitor_decoded["watch_addresses_raw"][0] == 0xFEBECC48 and
      monitor_decoded["values"][0]["raw_u32"] == 0x89ABCDEF)
monitor_payload = package_shellcode(monitor_stage, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
monitor_inspection = inspect_payload(monitor_payload, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
check("generic monitor authenticated payload identity exact",
      len(monitor_payload) == 0x1000 and sha(monitor_payload) == monitor.EXPECTED_PAYLOAD_SHA256 and
      monitor_inspection.cmac_valid and monitor_inspection.crc_residue == 0xFFFFFFFF)
check("generic monitor resident has no source-write/dynamic-call primitive and rejects unaligned windows",
      "st.w r1, 0[r10]" not in monitor_source and "jmp [r10]" not in monitor_source and
      "andi 3, r9, r10" in monitor_source and "bne .L_sample_gate" in monitor_source)

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
    check("kit manifest is self-contained v7 and binds exact route", manifest["schema"] == "camry-f33-car-kit-v7" and manifest["target"] == {
        "eps_f181": "8965F3307000", "eps_diag": "0x7A1->0x7A9 bus0", "b6": "0x0B6/32 FD bus0",
    })
    check("kit pins live persistence-verified stage5 as current firmware", manifest["current_firmware"] == {
        "stage": 5,
        "sha256": "669cedf8c8465ebfd02318cb7708b897b817bc3b40925c89743b64ce49aa01af",
        "crc_prefix": "0x1960380A", "crc_fixup": "0xE69FC7F5",
        "note": "live persistence-verified 2026-09-01; no further persistent patch is part of the observer experiment",
    })
    mon = manifest["ram_experiments"]["runtime_monitor"]
    check("kit makes generic external-control monitor the primary RAM experiment",
          mon["payload_sha256"] == monitor.EXPECTED_PAYLOAD_SHA256 and
          mon["resident_sha256"] == monitor.EXPECTED_RESIDENT_SHA256 and mon["resident_size"] == 520 and
          mon["watch_slots"] == 8 and mon["control_can_id"] == "0x1FDC0002" and
          mon["control_frame"] == "00 F3 seq opcode arg32-le" and mon["source_memory_write"] is False and
          mon["dynamic_call"] is False and manifest["ram_experiments"]["order"][0] == "runtime_monitor install once in NRTD")
    replay = manifest["ram_experiments"]["runtime_replay_discriminator"]
    check("superseded ABI source-term discriminator remains identity-pinned",
          replay["payload_sha256"] == "48f269aec2c95fbf33217db67a201faad2716985784f5e196ba5ddeade46d8dd" and
          replay["staging_sha256"] == "0e0d6cc19c8fe8a4f04d216a1b85d73c41dce6e283d5d18d6a80d9da2937b1e6" and
          replay["resident_sha256"] == "26e13ab455f9580e005cb50fc5ef1bb26d6214f3cbc9ff02056ad6af2ebb7ba9" and
          replay["resident_base"] == "0xFEBFF9F0" and replay["resident_size"] == 406 and
          replay["clean_window_ticks"] == 224 and replay["clean_window_nominal_seconds"] == 1.12 and
          replay["source_terms_mailbox"] == "0xFEBF0000..0xFEBF0024" and
          replay["success_verdict"] == "abi_preserving_runtime_and_source_terms_live" and
          replay["ready_read_existing_success_verdict"] == "ready_parked_source_terms_live" and
          "NRTD->READY without OFF" in replay["next_after_success"] and replay["bypass"] is False and
          replay["live_qualified"] is False and replay["superseded_by"] == "runtime_monitor")
    check("legacy B6 observer and bridge remain packaged but are explicitly not live-qualified",
          manifest["ram_experiments"]["observer"]["bypass"] is False and
          manifest["ram_experiments"]["observer"]["payload_sha256"] == "5be3e474c965e3111957227f7db44b30aa2c6eca6ba341a8279ceea043e2728d" and
          manifest["ram_experiments"]["observer"]["live_qualified"] is False and
          "call0(address)" in manifest["ram_experiments"]["observer"]["blocked_by"] and
          manifest["ram_experiments"]["bridge"]["payload_sha256"] == "8eec0e29fb1110f7865c85199c6b348ab3a69ccfa8f98cec981f2232f9c2d0ef" and
          manifest["ram_experiments"]["bridge"]["live_qualified"] is False)
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
    check("kit includes launcher, monitor/legacy payloads, and RAM runtime needed on comma",
          (out / "f33").is_file() and (out / "f33").stat().st_mode & 0o111 and all((out / rel).is_file() for rel in (
        "ram_payloads/camry_f33_runtime_monitor_payload.bin",
        "ram_payloads/camry_f33_runtime_replay_discriminator_payload.bin",
        "ram_payloads/camry_f33_b6_transaction_observer_payload.bin",
        "ram_payloads/camry_f33_b6_bridge_payload.bin",
        "runtime/exploit/common/ram_exec.py", "runtime/exploit/common/payload_package.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_transaction_observer_install.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_runtime_monitor.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.py",
        "runtime/exploit/followups/xcp_read_probe.py", "runtime/exploit/followups/xcp_daq_probe.py",
        "runtime/tools/camry_f33_steering_state_capture.py",
        "runtime/exploit/patcher/deploy.py", "runtime/exploit/patcher/restore.py",
        "runtime/exploit/patcher/post_apply_verify.py", "runtime/tools/build_secoc_patch_manifest.py",
    )))
    xcp_observer = manifest["live_observers"]["native_xcp_steering_state"]
    check("kit marks native XCP steering observer stock-disabled",
          xcp_observer["preferred_before_ephemeral_resident"] is False and
          xcp_observer["profiles"] == ["full-path", "source-terms", "command-funnel"] and
          xcp_observer["default_profile"] == "full-path" and
          xcp_observer["full_path_bytes"] == 52 and
          xcp_observer["full_path_daq_lists"] == 2 and
          xcp_observer["default_daq_prescaler"] == 10 and
          xcp_observer["source_memory_write"] is False and
          xcp_observer["steering_transmit"] is False and
          "0x30D68=0x5A" in xcp_observer["live_status"] and
          "stock-native execution disabled" in xcp_observer["live_status"])
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
    check("runbook is launcher-first and externally configurable",
          "generic runtime monitor" in runbook and "runtime_monitor_live" in runbook and
          "./f33 doctor" in runbook and "./f33 install" in runbook and "./f33 shell" in runbook and
          "watch SLOT ADDRESS" in runbook and "Do not execute them from this runbook" in runbook)
    check("runbook preserves observation-only boundary",
          "no dynamic source-memory writer" in runbook and "steering CAN transmit" in runbook and
          "current coherent snapshot" in runbook and "on-ECU history ring" in runbook)
    check("runbook pins current bus0 and canonical Panda ownership",
          "post-repin diagnostics" in runbook and "Panda bus 0" in runbook and
          "manager/manager.py" in runbook and "pandad`/`boardd`" in runbook)
    launcher = out / "f33"
    launcher_text = launcher.read_text(encoding="utf-8")
    check("launcher pins field environment and fixed monitor payload path",
          "/usr/local/venv/bin/python" in launcher_text and "/data/openpilot" in launcher_text and
          "ram_payloads/camry_f33_runtime_monitor_payload.bin" in launcher_text and
          "PYTHONPATH" in launcher_text and "systemctl stop openpilot" in launcher_text and
          "manager/manager\\.py" in launcher_text and "pandad" in launcher_text and "boardd" in launcher_text)
    local_openpilot = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
    local_python = local_openpilot / ".venv/bin/python"
    env = dict(os.environ, F33_PYTHON=str(local_python), F33_OPENPILOT_ROOT=str(local_openpilot))
    doctor = subprocess.run([str(launcher), "doctor"], cwd=out, env=env, capture_output=True, text=True, check=False)
    check("built launcher doctor validates imports and payload without Panda access",
          doctor.returncode == 0 and "f33 doctor: PASS" in doctor.stdout and monitor.EXPECTED_PAYLOAD_SHA256 in doctor.stdout, doctor.stderr[-300:])
    launch_plan = subprocess.run([str(launcher), "plan"], cwd=out, env=env, capture_output=True, text=True, check=False)
    plan_obj = json.loads(launch_plan.stdout) if launch_plan.returncode == 0 else {}
    check("built launcher plan resolves canonical monitor with no manual arguments",
          launch_plan.returncode == 0 and plan_obj.get("schema") == "camry-f33-runtime-monitor-plan-v1" and
          plan_obj.get("payload", {}).get("sha256") == monitor.EXPECTED_PAYLOAD_SHA256, launch_plan.stderr[-300:])
    check("kit manifest hashes launcher and root runbook",
          manifest["files"]["f33"]["sha256"] == sha(launcher.read_bytes()) and
          manifest["files"]["RUNBOOK.md"]["sha256"] == sha((out / "RUNBOOK.md").read_bytes()))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
