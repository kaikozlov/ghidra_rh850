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
check("ABI-safe RAM bridge v3 mailbox and stock-tick witness are exact and readable",
      (probe.BRIDGE_MAILBOX.address, probe.BRIDGE_MAILBOX.length, probe.BRIDGE_MAILBOX_MAGIC, probe.BRIDGE_MAILBOX_VERSION) ==
      (0xFEBF0000, 0x30, 0x42364252, 3) and probe.BRIDGE_FOREGROUND_TICK.address == 0xFEBE39DB and
      probe.validate_read(probe.RAM_ID, probe.BRIDGE_MAILBOX.address, probe.BRIDGE_MAILBOX.length) is None and
      probe.validate_read(probe.RAM_ID, probe.BRIDGE_FOREGROUND_TICK.address, probe.BRIDGE_FOREGROUND_TICK.length) is None)
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
check("bridge-required mode verifies v3 mailbox, armed state, and stock-tick liveness",
      'RAM bridge v3 mailbox identity mismatch' in source and
      'RAM bridge is installed but not armed' in source and 'stock foreground tick did not advance' in source and
      'snapshot_bridge_telemetry(uds_client, uds_mod, log)' in source and
      '"after_id0": bridge_after["id0"]' in source and '"after_id11": bridge_after["id11"]' in source and
      plan["bridge_mailbox"]["fields"] == {"last_sequence": 5, "running": 6, "bridged": 8, "pending": 12, "saved_b6": 16})
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
e2e = json.loads((ROOT / "data/generated/camry_f33_b6_end_to_end.json").read_text())
expected_phases = {row["phase"]: tuple(int(w["address"], 16) for w in row["watch_windows"]) for row in e2e["stationary_monitor_phases"]}
check("generic monitor phase presets are byte-for-byte the verified A-G ladder",
      monitor.MONITOR_PHASES == expected_phases and set(monitor.MONITOR_PHASES) == set("ABCDEFG") and
      all(len(v) == 8 for v in monitor.MONITOR_PHASES.values()))
check("generic monitor decodes the live 0x00F/0x025 inputs used by the host B6 phase sender",
      monitor.decode_secoc_sync(bytes.fromhex("1234abcde0000000")) == {"trip_counter": 0x1234, "reset_counter": 0xABCDE} and
      monitor.decode_steering_angle_deg(bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")) == 0.0)
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

print("\n== sticky pre-aggregate B6 ingress monitor ==")
from exploit.ephemeral_runtime import camry_f33_runtime_monitor_preaggregate as preagg
preagg_source_path = ROOT / "exploit/ephemeral_runtime/camry_f33_runtime_monitor_preaggregate.S"
preagg_builder_path = ROOT / "exploit/ephemeral_runtime/build_camry_f33_runtime_monitor_preaggregate.py"
preagg_audit_path = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_runtime_monitor_preaggregate_build.json"
preagg_stage_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_runtime_monitor_preaggregate.bin"
preagg_source = preagg_source_path.read_text()
preagg_audit = json.loads(preagg_audit_path.read_text())
preagg_stage = preagg_stage_path.read_bytes()
preagg_resident = preagg_stage[0x80:0x80 + preagg.RESIDENT_SIZE]
check("pre-aggregate monitor audited binary/source/builder identities exact",
      preagg_audit["schema"] == "camry-f33-runtime-monitor-preaggregate-build-v1" and
      preagg_audit["source"]["sha256"] == sha(preagg_source_path.read_bytes()) and
      preagg_audit["builder"]["sha256"] == sha(preagg_builder_path.read_bytes()) and
      sha(preagg_stage) == preagg.EXPECTED_STAGING_SHA256 and
      sha(preagg_resident) == preagg.EXPECTED_RESIDENT_SHA256 and
      preagg_audit["authenticated_payload"]["sha256"] == preagg.EXPECTED_PAYLOAD_SHA256)
check("pre-aggregate monitor fits the proven tail and samples before unchanged aggregate",
      preagg.RESIDENT_SIZE == preagg_audit["resident"]["size"] == 522 and
      preagg_audit["resident"]["headroom"] == 2 and preagg_audit["resident"]["relocations"] == 0 and
      preagg_audit["observation"]["sample_point"] == "after fg_pre_3 and immediately before fg_aggregate" and
      preagg_audit["observation"]["run_trigger"]["address"] == "0xFEBE547A" and
      preagg_audit["observation"]["run_trigger"]["condition"] == "u16 != 0" and
      preagg_source.index("ld.hu -0x6386[gp], r1") < preagg_source.index("jarl32 fg_aggregate, lp"))
check("pre-aggregate phase P captures exact secured signature plus prior route44 boundary",
      preagg.PREAGGREGATE_PHASES == {"P": (
          0xFEBE5478, 0xFEBE54D4, 0xFEBE54D8, 0xFEBE54DC,
          0xFEBE54F0, 0xFEBE4C00, 0xFEBE4C04, 0xFEBE5364,
      )})
synthetic_values = []
synthetic_bytes = (
    "00002000", "0000000b", "002f0007", "64640000", "a1234567", "00000000", "2e001900", "12000000",
)
for i, hx in enumerate(synthetic_bytes):
    synthetic_values.append({"slot": i, "bytes_le": hx})
queued_sig = bytes.fromhex("0000000b002f000764640000a1234567").hex()
preagg_result = {
    "capture": {"last": {"values": synthetic_values, "sample_generation": 42}},
    "b6": {"phase_signatures_hex": ["00" * 16, queued_sig]},
}
check("pre-aggregate host classifies a sticky exact phase queue hit deterministically",
      preagg.classify_ingress(preagg_result)["verdict"] == "exact_phase_b6_queued_preaggregate" and
      preagg.classify_ingress(preagg_result)["queue_length"] == 32 and
      preagg.classify_ingress(preagg_result)["matched_phase_frame_indices"] == [1])
preagg_payload = package_shellcode(preagg_stage, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
preagg_inspection = inspect_payload(preagg_payload, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
check("pre-aggregate monitor authenticated payload identity exact",
      len(preagg_payload) == 0x1000 and sha(preagg_payload) == preagg.EXPECTED_PAYLOAD_SHA256 and
      preagg_inspection.cmac_valid and preagg_inspection.crc_residue == 0xFFFFFFFF)

print("\n== inter-tick B6 ingress monitor ==")
from exploit.ephemeral_runtime import camry_f33_runtime_monitor_intertick as intertick
intertick_source_path = ROOT / "exploit/ephemeral_runtime/camry_f33_runtime_monitor_intertick.S"
intertick_builder_path = ROOT / "exploit/ephemeral_runtime/build_camry_f33_runtime_monitor_intertick.py"
intertick_audit_path = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_runtime_monitor_intertick_build.json"
intertick_stage_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_runtime_monitor_intertick.bin"
intertick_source = intertick_source_path.read_text()
intertick_audit = json.loads(intertick_audit_path.read_text())
intertick_stage = intertick_stage_path.read_bytes()
intertick_resident = intertick_stage[0x80:0x80 + intertick.RESIDENT_SIZE]
check("inter-tick monitor audited binary/source/builder identities exact",
      intertick_audit["schema"] == "camry-f33-runtime-monitor-intertick-build-v2" and
      intertick_audit["source"]["sha256"] == sha(intertick_source_path.read_bytes()) and
      intertick_audit["builder"]["sha256"] == sha(intertick_builder_path.read_bytes()) and
      sha(intertick_stage) == intertick.EXPECTED_STAGING_SHA256 and
      sha(intertick_resident) == intertick.EXPECTED_RESIDENT_SHA256 and
      intertick_audit["authenticated_payload"]["sha256"] == intertick.EXPECTED_PAYLOAD_SHA256)
check("inter-tick monitor fits tail and marker-filters before foreground tick/aggregate",
      intertick.RESIDENT_SIZE == intertick_audit["resident"]["size"] == 518 and
      intertick_audit["resident"]["headroom"] == 6 and intertick_audit["resident"]["relocations"] == 0 and
      intertick_audit["observation"]["trigger"] == {
          "queue_length": {"address": "0xFEBE547A", "condition": "u16 == 32"},
          "marker": {"address": "0xFEBE54D7", "condition": "B3 low6 == 63"},
      } and
      "outside the recovered F33 command-mode decoder" in intertick_audit["observation"]["marker_semantics"] and
      "native/background route44/B6 is ID0" in intertick_audit["observation"]["native_stationary_disambiguation"] and
      "copies payload" in intertick_audit["observation"]["queue_publication_order"] and
      intertick_source.index("ld.hu -0x6386[gp], r6") < intertick_source.index("ld.bu -0x6329[gp], r6") <
      intertick_source.index("tst1 4, -0x4eef[r0]") < intertick_source.index("jarl32 fg_aggregate, lp"))
check("inter-tick monitor has fixed ingress-only phase Q",
      intertick.INTERTICK_PHASES == {"Q": (0xFEBE5478,0xFEBE54D4,0xFEBE54D8,0xFEBE54DC,0xFEBE54F0,0,0,0)})
synthetic_it_values=[]
queued_marker_sig = "0000003f002f040700000000a1234567"
for i,hx in enumerate(("00002000","0000003f","002f0407","00000000","a1234567","00000000","00000000","00000000")):
    synthetic_it_values.append({"slot":i,"bytes_le":hx})
it_result={"capture":{"last":{"values":synthetic_it_values,"sample_generation":7}},"b6":{"phase_signatures_hex":[queued_marker_sig]}}
check("inter-tick host classifies exact queued ID63 marker deterministically",
      intertick.classify_ingress(it_result)["verdict"] == "exact_phase_b6_queued_intertick" and
      intertick.classify_ingress(it_result)["matched_phase_frame_indices"] == [0] and
      "marker-filtered" in intertick.classify_ingress(it_result)["sample_point"])
check("inter-tick Phase Q sender is non-command ID63 with additive contribution suppressed",
      "target_lateral_id=63" in (ROOT / "exploit/ephemeral_runtime/camry_f33_runtime_monitor_intertick.py").read_text() and
      "suppress_additive=True" in (ROOT / "exploit/ephemeral_runtime/camry_f33_runtime_monitor_intertick.py").read_text())
it_zero_values=[{"slot":i,"bytes_le":"00000000"} for i in range(8)]
it_nohit={"capture":{"last":None},"post":{"state":{"values":it_zero_values,"sample_generation":0}},"b6":{"phase_signatures_hex":[queued_marker_sig]}}
check("inter-tick no-hit remains a valid classified result with generation zero",
      intertick.classify_ingress(it_nohit)["verdict"] == "no_profile2_queue_hit_intertick" and
      intertick.classify_ingress(it_nohit)["sample_generation"] == 0)
intertick_payload = package_shellcode(intertick_stage, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
intertick_inspection = inspect_payload(intertick_payload, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
check("inter-tick monitor authenticated payload identity exact",
      len(intertick_payload) == 0x1000 and sha(intertick_payload) == intertick.EXPECTED_PAYLOAD_SHA256 and
      intertick_inspection.cmac_valid and intertick_inspection.crc_residue == 0xFFFFFFFF)

print("\n== deterministic mid-aggregate B6 ingress observer ==")
from exploit.ephemeral_runtime import camry_f33_b6_midaggregate_observer as midagg
from exploit.ephemeral_runtime import build_camry_f33_command5_probe as command5_build
from exploit.ephemeral_runtime import camry_f33_command5_probe as command5_probe
midagg_source_path = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_midaggregate_observer.S"
midagg_builder_path = ROOT / "exploit/ephemeral_runtime/build_camry_f33_b6_midaggregate_observer.py"
midagg_audit_path = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_b6_midaggregate_observer_build.json"
midagg_stage_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_midaggregate_observer.bin"
midagg_source = midagg_source_path.read_text()
midagg_audit = json.loads(midagg_audit_path.read_text())
midagg_stage = midagg_stage_path.read_bytes()
midagg_resident = midagg_stage[0x80:0x80 + midagg.RESIDENT_SIZE]
check("mid-aggregate observer audited binary/source/builder identities exact",
      midagg_audit["schema"] == "camry-f33-b6-midaggregate-observer-build-v1" and
      midagg_audit["source"]["sha256"] == sha(midagg_source_path.read_bytes()) and
      midagg_audit["builder"]["sha256"] == sha(midagg_builder_path.read_bytes()) and
      sha(midagg_stage) == midagg.EXPECTED_STAGING_SHA256 and
      sha(midagg_resident) == midagg.EXPECTED_RESIDENT_SHA256 and
      midagg_audit["authenticated_payload"]["sha256"] == midagg.EXPECTED_PAYLOAD_SHA256)
check("mid-aggregate observer fits tail with deterministic receive-to-SecOC boundary",
      midagg.RESIDENT_SIZE == midagg_audit["resident"]["size"] == 498 and
      midagg_audit["resident"]["headroom"] == 26 and midagg_audit["resident"]["relocations"] == 0 and
      midagg_audit["resident"]["external_tail_jumps"] == ["0x000667F2", "0x0007A272"] and
      "0x79EDE" in midagg_audit["static_pins"]["observation_boundary"] and
      "0x6A410" in midagg_audit["static_pins"]["observation_boundary"])
check("mid-aggregate statistics contract has D7 control, exact marker identity, and no treatment SID23",
      midagg_audit["statistics_contract"]["no_sid23_during_treatment"] is True and
      "0x0D7" in midagg_audit["statistics_contract"]["same_scheduler_positive_control"] and
      midagg_audit["statistics_contract"]["marker_signature"] == "B0..B11 || B28..B31" and
      midagg.JITTER_MS == (11, 17, 23, 13, 19))
check("mid-aggregate mailbox preserves arbitrary baselines and only added mailbox writes",
      "Counters are deliberately not zeroed" in midagg_source and ".L_clear_mailbox" not in midagg_source and
      midagg_audit["mutation_boundary"]["added_write_regions"] == ["FEBF0000..FEBF0027 observer mailbox"])
midagg_payload = package_shellcode(midagg_stage, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
midagg_inspection = inspect_payload(midagg_payload, secret=(ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()[0xBFD8:0xBFE8])
check("mid-aggregate observer authenticated payload identity exact",
      len(midagg_payload) == 0x1000 and sha(midagg_payload) == midagg.EXPECTED_PAYLOAD_SHA256 and
      midagg_inspection.cmac_valid and midagg_inspection.crc_residue == 0xFFFFFFFF)

print("\n== bounded exact-F33 command-5 permission probe ==")
command5_out = ROOT / "build/out/ephemeral-runtime/camry-f33-command5-probe"
command5_audit_path = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_command5_probe_build.json"
command5_stage_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_command5_probe.bin"
command5_build_run = subprocess.run(
    [sys.executable, str(command5_build.BUILDER)], cwd=ROOT, capture_output=True, text=True, check=False)
check("command-5 probe deterministic builder succeeds", command5_build_run.returncode == 0, command5_build_run.stderr[-300:])
command5_meta = json.loads((command5_out / "camry_f33_command5_probe.json").read_text()) if command5_build_run.returncode == 0 else {}
command5_resident = (command5_out / command5_meta["resident"]["path"]).read_bytes() if command5_meta else b""
command5_stage = (command5_out / command5_meta["staging"]["path"]).read_bytes() if command5_meta else b""
command5_payload = (command5_out / command5_meta["authenticated_payload"]["path"]).read_bytes() if command5_meta else b""
check("command-5 exact target and deterministic identities",
      command5_meta.get("target") == {"software_id": "8965F3307000", "codeflash_sha256": command5_build.IMAGE_SHA256} and
      sha(command5_resident) == command5_probe.EXPECTED_RESIDENT_SHA256 == command5_meta["resident"]["sha256"] and
      sha(command5_stage) == command5_probe.EXPECTED_STAGING_SHA256 == command5_meta["staging"]["sha256"] and
      sha(command5_payload) == command5_probe.EXPECTED_PAYLOAD_SHA256 == command5_meta["authenticated_payload"]["sha256"])
check("command-5 audited stage and metadata are exact",
      command5_stage_path.read_bytes() == command5_stage and
      json.loads(command5_audit_path.read_text()) == command5_meta)
check("command-5 resident exactly fits live-proven high tail",
      len(command5_resident) == command5_probe.RESIDENT_SIZE == 524 and
      command5_meta["resident"]["headroom"] == 0 and command5_meta["resident"]["end_limit"] == "0xFEBFFBFC" and
      command5_meta["resident"]["relocations"] == 0)
check("command-5 only extra stock call is synchronous wrapper",
      command5_meta["resident"]["jarl_targets"][-1] == "0x00089BC2" and
      command5_meta["resident"]["jarl_targets"][:-1] == [f"0x{x:08X}" for x in command5_build.EXPECTED_RESIDENT_JARL_TARGETS])
check("command-5 fixed wrapper contract and corrected output ABI", command5_meta["command5"] == {
    "synchronous_wrapper": "0x00089BC2", "dispatcher": "0x00089440", "engine": "0x0008A720",
    "driver_record": 0, "key_selector": 4, "input_length": 36, "output_length": 16,
    "config_type": 1, "config_type_address": "0xFEBF0048",
    "config_selector_offset": 4, "config_selector_address": "0xFEBF004C",
    "output_buffer": "0xFEBF0034", "output_length_cell": "0xFEBF000C",
    "done_flag": "0xFEBF13BC", "status_flag": "0xFEBF13BD",
} and "movea 0x24, r6, r7" in command5_build.SOURCE.read_text(encoding="utf-8") and
      "st.w r6, 0x4848[gp]" in command5_build.SOURCE.read_text(encoding="utf-8") and
      "st.w r8, 0x484c[gp]" in command5_build.SOURCE.read_text(encoding="utf-8") and
      "0x00040001" not in command5_build.SOURCE.read_text(encoding="utf-8") and
      "movea 0x4824, r6, r7" not in command5_build.SOURCE.read_text(encoding="utf-8"))
check("command-5 mutation boundary excludes actuation and extraction",
      command5_meta["mutation_boundary"]["chosen_input_lengths"] == [36] and
      command5_meta["mutation_boundary"]["key_selector_mutable"] is False and
      command5_meta["mutation_boundary"]["key_extraction"] is False and
      command5_meta["mutation_boundary"]["steering_can_transmit"] is False and
      command5_meta["mutation_boundary"]["b6_transmit"] is False and
      command5_meta["mutation_boundary"]["secoc_bypass"] is False and
      command5_meta["mutation_boundary"]["codeflash_write"] is False)
check("command-5 control frame is exact", command5_probe.command_frame(0x23, 0x35, 0x44332211) == bytes.fromhex("00c5233511223344"))
command5_app = bytes(range(28))
check("command-5 B6 domain matches opendbc DataID/application/freshness framing",
      command5_probe.build_b6_domain(command5_app, 0x1234, 0x56789, 0xAB) ==
      bytes.fromhex("00b6") + command5_app + bytes.fromhex("123456789ab4"))
freshness_record = (
    (0x1234).to_bytes(4, "little") + (0x56789).to_bytes(4, "little") +
    (0xAB).to_bytes(2, "little") + bytes.fromhex("5a00")
)
check("command-5 host decodes exact 12-byte ordinary freshness record",
      command5_probe.decode_freshness_record(freshness_record) == {
          "raw_hex": freshness_record.hex(), "trip_counter": 0x1234,
          "reset_counter": 0x56789, "message_counter": 0xAB, "aux_hex": "5a00",
      })
check("command-5 host chooses a strictly-forward same-epoch message counter",
      command5_probe.next_b6_message_counter(
          live_trip=0x1234, live_reset=0x56789,
          committed=command5_probe.decode_freshness_record(freshness_record),
      ) == (0xAC, "strictly_forward_same_epoch"))
older_record = command5_probe.decode_freshness_record(bytes(12))
check("command-5 host seeds any newer live epoch at message zero",
      command5_probe.next_b6_message_counter(
          live_trip=0x1234, live_reset=0x56789, committed=older_record,
      ) == (0, "newer_live_epoch_seed_zero"))
check("command-5 host advances and mirrors F33 +/-2 reset candidate window",
      command5_probe.advance_reset_epoch(0x1234, 0xFFFFF, 1) == (0x1235, 0) and
      [command5_probe.receiver_candidate_offset(
          signed_trip=0x1234, signed_reset=0x56789 + delta,
          current_trip=0x1234, current_reset=0x56789,
      ) for delta in range(4)] == [0, 1, 2, None] and
      command5_probe.receiver_candidate_offset(
          signed_trip=0x1234, signed_reset=0xFFFFF,
          current_trip=0x1235, current_reset=0,
      ) == -1)
signed_id0_app = command5_probe.build_inactive_b6_application(target_angle_raw=-2, sequence=63)
signed_id0_frame = command5_probe.build_signed_b6_frame(
    application=signed_id0_app, reset_counter=0x56789, message_counter=0xAB,
    cmac=bytes(range(0xA0, 0xB0)),
)
check("command-5 post-permission frame is exact ID0/current-angle suppressed shape",
      signed_id0_app.hex() == "00000000fffe043f" + "00" * 20 and
      signed_id0_frame.hex() == signed_id0_app.hex() + "da0a1a2a" and
      signed_id0_frame[3] == 0 and signed_id0_frame[6] == 4 and signed_id0_frame[8:10] == bytes(2))
check("command-5 post-permission trailer packs FV4 plus CMAC MSB28",
      signed_id0_frame[28] >> 4 == 0xD and
      (int.from_bytes(signed_id0_frame[28:32], "big") & 0x0FFFFFFF) == 0x0A0A1A2A)
check("command-5 signed discriminator binds the exact authenticated-sync and B6 state windows",
      command5_probe.AUTHENTICATED_SYNC_BASE == 0xFEBE55C0 and
      command5_probe.AUTHENTICATED_SYNC_SIZE == 8 and
      command5_probe.FRESHNESS_STATE_BASE == 0xFEBE55DC and
      command5_probe.FRESHNESS_STATE_SIZE == 48 and
      command5_probe.B6_COM_WINDOW == 0xFEBE4C02 and
      command5_probe.B6_COM_WINDOW_SIZE == 29)
command5_raw = bytearray(command5_probe.MAILBOX_SIZE)
command5_raw[0:4] = command5_probe.MAILBOX_MAGIC.to_bytes(4, "little")
command5_raw[4] = command5_probe.MAILBOX_VERSION
command5_raw[5:8] = bytes((0x23, 2, 0))
command5_raw[8:10] = (0x1FF).to_bytes(2, "little")
command5_raw[0x0A:0x0C] = bytes((0, 1))
command5_raw[0x0C:0x10] = (16).to_bytes(4, "little")
command5_domain = bytes(range(36))
command5_cmac = bytes(range(0xA0, 0xB0))
command5_raw[0x10:0x34] = command5_domain
command5_raw[0x34:0x44] = command5_cmac
command5_raw[0x48:0x4C] = (1).to_bytes(4, "little")
command5_raw[0x4C:0x50] = (4).to_bytes(4, "little")
command5_decoded = command5_probe.decode_mailbox(bytes(command5_raw))
check("command-5 mailbox distinguishes wrapper/done/status/output",
      command5_decoded["magic_ok"] and command5_decoded["version_ok"] and command5_decoded["state_name"] == "complete" and
      command5_decoded["wrapper_return_code"] == 0 and command5_decoded["input_complete"] and
      command5_decoded["command_status"] == 0 and command5_decoded["done_flag"] == 1 and
      command5_decoded["output_length"] == 16 and command5_decoded["input_hex"] == command5_domain.hex() and
      command5_decoded["output_hex"] == command5_cmac.hex() and command5_decoded["config_type"] == 1 and
      command5_decoded["config_selector"] == 4 and command5_decoded["config_valid"] is True)

generated = command5_probe.classify_command5_result(command5_decoded)
busy_state = {**command5_decoded, "wrapper_return_code": 2, "done_flag": 0, "command_status": 1}
terminal_state = {**command5_decoded, "wrapper_return_code": 1, "done_flag": 0, "command_status": 1}
bad_config_state = {**command5_decoded, "config_valid": False, "config_selector": 0}
bad_completion_state = {**command5_decoded, "done_flag": 0}
check("command-5 result classification preserves permission uncertainty",
      generated[:3] == ("generated", True, False) and
      command5_probe.classify_command5_result(busy_state)[:3] == ("transient_busy_or_timeout", None, True) and
      command5_probe.classify_command5_result(terminal_state)[:3] == ("terminal_driver_error", None, False) and
      command5_probe.classify_command5_result(bad_config_state)[:3] == ("resident_config_contract_error", None, False) and
      command5_probe.classify_command5_result(bad_completion_state)[:3] == ("completion_contract_error", None, False))
command5_launcher_text = (
    ROOT / "exploit/ephemeral_runtime/camry_f33_command5_launcher.sh"
).read_text(encoding="utf-8")
check("command-5 launcher exposes only one bounded signed ID0 B6 discriminator",
      "./f33-sign signed-id0 [OUTPUT_JSON]" in command5_launcher_text and
      'run_probe_bounded 30 signed-id0 --execute --parked-stationary-confirmed' in command5_launcher_text and
      command5_launcher_text.count("signed-id0)") == 1)
check("command-5 launcher exposes non-transmitting paced-burst timing probe",
      "./f33-sign generate-fast 72_HEX_DIGITS [OUTPUT_JSON]" in command5_launcher_text and
      'run_probe_bounded 10 generate-fast --input-hex' in command5_launcher_text and
      "pacing changed input" not in command5_launcher_text)
panda_lease_text = (
    ROOT / "exploit/ephemeral_runtime/f33_panda_lease.sh"
).read_text(encoding="utf-8")
check("shared Panda lease helper matches the actual Python pandad supervisor command line",
      r"pgrep -f '^openpilot\\.selfdrive\\.pandad\\.pandad$'" not in panda_lease_text and
      r"pgrep -f '^openpilot\.selfdrive\.pandad\.pandad$'" in panda_lease_text)
check("command-5 launcher uses cooperative Panda lease without stopping manager/pandad wrapper",
      "pkill -TERM -f '/openpilot/system/manager" not in command5_launcher_text and
      "systemctl stop openpilot" not in command5_launcher_text and
      'kill -STOP "$PANDAD_WRAPPER_PID"' not in command5_launcher_text and
      'kill -CONT "$PANDAD_WRAPPER_PID"' not in command5_launcher_text and
      "start_power_watchdog_keeper" not in command5_launcher_text and
      "f33_panda_lease.sh" in command5_launcher_text and
      "source \"$PANDA_LEASE_LIB\"" in command5_launcher_text and
      'timeout --signal=TERM --kill-after=2 "${seconds}s"' in command5_launcher_text)

retry_session = object.__new__(command5_probe.ProbeSession)
retry_input = bytearray(36)
retry_bitmap = 0
retry_exec_count = 0

def _retry_state() -> dict:
    return {
        **command5_decoded,
        "input_bitmap": retry_bitmap,
        "input_complete": retry_bitmap == 0x1FF,
        "input_hex": bytes(retry_input).hex(),
    }

def _retry_read_state() -> dict:
    return _retry_state()

def _retry_send(opcode: int, argument: int, predicate) -> dict:
    global retry_bitmap, retry_exec_count
    if command5_probe.OP_WORD_BASE <= opcode < command5_probe.OP_WORD_BASE + 9:
        word = opcode - command5_probe.OP_WORD_BASE
        retry_input[word * 4:(word + 1) * 4] = argument.to_bytes(4, "little")
        retry_bitmap |= 1 << word
        state = _retry_state()
    else:
        retry_exec_count += 1
        state = {
            **_retry_state(), "state": 2,
            "wrapper_return_code": 2 if retry_exec_count == 1 else 0,
            "done_flag": 0 if retry_exec_count == 1 else 1,
            "command_status": 1 if retry_exec_count == 1 else 0,
        }
    assert predicate(state)
    return {"sequence": opcode, "opcode": f"0x{opcode:02X}", "frame_hex": "", "state": state}

retry_session.read_state = _retry_read_state
retry_session._send = _retry_send
retry_result = retry_session.generate(bytes.fromhex("00b6") + bytes(range(34)))
check("command-5 host retries only ambiguous busy/timeout and preserves attempt evidence",
      retry_result["outcome"] == "generated" and retry_result["slot4_command5_permitted"] is True and
      retry_result["reused_input_words"] == [] and
      len(retry_result["execute_attempts"]) == 2 and
      [row["outcome"] for row in retry_result["execute_attempts"]] == ["transient_busy_or_timeout", "generated"])
retry_exec_count = 0
retry_result_reused = retry_session.generate(bytes.fromhex("00b6") + bytes(range(34)))
check("command-5 host reuses all unchanged resident input words",
      retry_result_reused["outcome"] == "generated" and
      retry_result_reused["reused_input_words"] == list(range(9)) and
      retry_result_reused["chunk_commands"] == [])

class _BurstPanda:
    def __init__(self, state: dict, *, drop_word_once: int | None = None):
        self.state = state
        self.sent: list[tuple[int, bytes, int]] = []
        self.drop_word_once = drop_word_once

    def can_send(self, addr: int, dat: bytes, bus: int, **_kwargs) -> None:
        self.sent.append((addr, bytes(dat), bus))
        sequence, opcode = dat[2], dat[3]
        self.state["last_sequence"] = sequence
        if command5_probe.OP_WORD_BASE <= opcode < command5_probe.OP_WORD_BASE + 9:
            word = opcode - command5_probe.OP_WORD_BASE
            if self.drop_word_once == word:
                self.drop_word_once = None
                return
            raw = bytearray.fromhex(self.state["input_hex"])
            raw[word * 4:(word + 1) * 4] = dat[4:8]
            self.state["input_hex"] = bytes(raw).hex()
            self.state["input_bitmap"] = int(self.state["input_bitmap"]) | (1 << word)
            self.state["input_complete"] = int(self.state["input_bitmap"]) == 0x1FF
            self.state["state"] = 0
        elif opcode == command5_probe.OP_EXECUTE:
            self.state.update({
                "state": 2, "wrapper_return_code": 0, "done_flag": 1, "command_status": 0,
                "output_length": 16, "output_hex": command5_cmac.hex(),
                "config_type": 1, "config_selector": 4, "config_valid": True,
            })

burst_domain = bytes.fromhex("00b6") + bytes(range(34))
burst_state = {
    **command5_decoded,
    "last_sequence": 200,
    "state": 0,
    "input_bitmap": 0,
    "input_complete": False,
    "input_hex": (bytes(36)).hex(),
    "config_valid": False,
}
burst_session = object.__new__(command5_probe.ProbeSession)
burst_session.panda = _BurstPanda(burst_state, drop_word_once=4)
burst_session.read_state = lambda: dict(burst_state)
burst_result = burst_session.generate_fast(burst_domain)
check("command-5 fast host path tick-paces words and repairs a missed word before execute",
      burst_result["outcome"] == "generated" and
      burst_result["transport"] == "foreground-tick-paced-burst" and
      len(burst_result["chunk_commands"]) == 10 and
      [row["word"] for row in burst_result["chunk_commands"]].count(4) == 2 and
      burst_result["execute_attempts"][0]["completion_observation_reads"] == 1 and
      burst_result["final_state"]["input_hex"] == burst_domain.hex() and
      burst_result["timing"]["foreground_tick_s"] == 0.005 and
      burst_result["timing"]["word_interval_s"] == 0.010)
burst_sent_before = len(burst_session.panda.sent)
burst_result_reused = burst_session.generate_fast(burst_domain)
check("command-5 fast host path reuses stable resident words and sends only execute",
      burst_result_reused["outcome"] == "generated" and
      burst_result_reused["reused_input_words"] == list(range(9)) and
      burst_result_reused["chunk_commands"] == [] and
      len(burst_session.panda.sent) == burst_sent_before + 1 and
      burst_session.panda.sent[-1][1][3] == command5_probe.OP_EXECUTE)
check("command-5 fast path remains observation-only",
      burst_result["boundaries"]["transmitted_b6"] is False and
      burst_result["boundaries"]["persistent_flash_write"] is False)

def _command5_rejects(candidate: bytes) -> bool:
    session = object.__new__(command5_probe.ProbeSession)
    try:
        session.generate(candidate)
    except command5_probe.Command5ProbeError:
        return True
    return False

check("command-5 host rejects invalid lengths and non-B6 domains",
      all(_command5_rejects(bytes(n)) for n in (0, 7, 12, 35, 37, 80)) and
      _command5_rejects(b"\x00\xB7" + bytes(34)))
check("command-5 plan is non-actuating and ephemeral", command5_probe.plan(None)["boundaries"] == {
    "persistent_flash_write": False, "b6_transmit": False,
    "steering_can_transmit": False, "key_extraction": False,
    "arbitrary_length_or_selector": False,
})

print("\n== inline B6 signer host-visible state ==")
from exploit.ephemeral_runtime import camry_f33_b6_inline_signer as inline_signer
check("inline signer state remains wholly SID23-readable below the protected boundary",
      inline_signer.STATE_BASE == 0xFEBF025C and inline_signer.STATE_SIZE == 12 and
      inline_signer.STATE_BASE + inline_signer.STATE_SIZE == inline_signer.TELEMETRY_BASE and
      probe.validate_read(probe.RAM_ID, inline_signer.STATE_BASE, inline_signer.STATE_SIZE) is None)
state_raw = inline_signer.STATE_MAGIC.to_bytes(4, "little") + bytes((7, 1, 0, 0)) + (9).to_bytes(4, "little")
state_decoded = inline_signer.decode_state(state_raw)
check("inline signer state decoder requires both magic and initialized byte",
      state_decoded["initialized"] is True and state_decoded["initialized_raw"] == 1 and
      state_decoded["next_index"] == 7 and state_decoded["signed_count"] == 9 and
      inline_signer.decode_state(state_raw[:5] + b"\x00" + state_raw[6:])["initialized"] is False)
scratch_read_rejected = False
try:
    probe.validate_read(probe.RAM_ID, inline_signer.SCRATCH_BASE, inline_signer.SCRATCH_SIZE)
except probe.ProbeError:
    scratch_read_rejected = True
check("inline signer command5 scratch intentionally begins at the SID23 exclusion",
      inline_signer.SCRATCH_BASE == 0xFEBF0288 and inline_signer.SCRATCH_SIZE == 0x48 and
      inline_signer.SCRATCH_BASE == inline_signer.APPLICATION_RMBA_PROTECTED_START and scratch_read_rejected)
telemetry_raw = (
    (11).to_bytes(4, "little") + (3).to_bytes(4, "little") +
    bytes.fromhex("a1b2c3d4") + bytes.fromhex("a1b2c3d4") + bytes((9, 1, 1, 0))
)
telemetry_decoded = inline_signer.decode_signer_telemetry(telemetry_raw)
check("inline signer telemetry exposes native-frame/signing equality gates",
      inline_signer.TELEMETRY_BASE == 0xFEBF0268 and inline_signer.TELEMETRY_SIZE == 0x14 and
      inline_signer.TELEMETRY_BASE + inline_signer.TELEMETRY_SIZE <= inline_signer.APPLICATION_RMBA_PROTECTED_START and
      probe.validate_read(probe.RAM_ID, inline_signer.TELEMETRY_BASE, inline_signer.TELEMETRY_SIZE) is None and
      telemetry_decoded["native_frame_count"] == 11 and telemetry_decoded["command5_attempts"] == 3 and
      telemetry_decoded["last_native_trailer_hex"] == "a1b2c3d4" and
      telemetry_decoded["last_computed_trailer_hex"] == "a1b2c3d4" and
      telemetry_decoded["last_control_seq"] == 9 and telemetry_decoded["native_verified"] is True and
      telemetry_decoded["native_signature_match"] is True and telemetry_decoded["last_done_flag"] == 1 and
      telemetry_decoded["last_command_status"] == 0)
check("inline signer telemetry refuses equality without completed native verification",
      inline_signer.decode_signer_telemetry(telemetry_raw[:17] + b"\x00" + telemetry_raw[18:])["native_signature_match"] is False and
      inline_signer.decode_signer_telemetry(telemetry_raw[:12] + bytes.fromhex("11223344") + telemetry_raw[16:])["native_signature_match"] is False)
check("inline signer replacement control is exact one-shot C7 signed16 big-endian",
      inline_signer.replacement_frame(sequence=0x2A, target_angle_raw=-13) == bytes.fromhex("00c72a00fff30000"))
check("inline signer exposes exact profile2 queue and full secured buffer through SID23",
      inline_signer.B6_QUEUE_RECORD_BASE == 0xFEBE547A and inline_signer.B6_QUEUE_RECORD_SIZE == 8 and
      inline_signer.B6_SECURED_BUFFER_BASE == 0xFEBE54D4 and inline_signer.B6_SECURED_BUFFER_SIZE == 32 and
      probe.validate_read(probe.RAM_ID, inline_signer.B6_QUEUE_RECORD_BASE, inline_signer.B6_QUEUE_RECORD_SIZE) is None and
      probe.validate_read(probe.RAM_ID, inline_signer.B6_SECURED_BUFFER_BASE, inline_signer.B6_SECURED_BUFFER_SIZE) is None)

# quiet-source now counts distinct native B6 frames by frame-unique protected
# trailer, rather than scheduler ticks during which the queue remains occupied.
def _telem_blob(native_frames: int, command5_attempts: int) -> bytes:
    return (
        native_frames.to_bytes(4, "little") + command5_attempts.to_bytes(4, "little") +
        bytes.fromhex("01020304") + bytes.fromhex("01020304") + bytes((0, 1, 1, 0))
    )

class _FakeQuietSession:
    client = object()
    uds_mod = object()
    def __init__(self, bundle, *, require_ready_parked):
        assert require_ready_parked is False
    def read_state(self):
        return {"initialized": True, "armed": True, "signed_count": 0}

_quiet_blobs = iter((_telem_blob(0xFFFFFFFE, 7), _telem_blob(1, 7)))
_orig_inline_session = inline_signer.InlineSignerSession
_orig_inline_read = inline_signer._read_memory
_orig_inline_sleep = inline_signer.time.sleep
_orig_inline_monotonic = inline_signer.time.monotonic
inline_signer.InlineSignerSession = _FakeQuietSession
inline_signer._read_memory = lambda client, uds_mod, address, size: next(_quiet_blobs)
_times = iter((10.0, 11.0))
inline_signer.time.sleep = lambda _: None
inline_signer.time.monotonic = lambda: next(_times)
try:
    quiet = inline_signer.quiet_source_rate(object(), duration=1.0)
finally:
    inline_signer.InlineSignerSession = _orig_inline_session
    inline_signer._read_memory = _orig_inline_read
    inline_signer.time.sleep = _orig_inline_sleep
    inline_signer.time.monotonic = _orig_inline_monotonic
check("inline signer quiet-source measures modular native-frame movement without CAN transmit",
      quiet["host_b6_producer_quiesced"] is True and quiet["can_transmit"] is False and
      quiet["delta"]["native_frame_count"] == 3 and quiet["delta"]["command5_attempts"] == 0 and
      quiet["rates"]["native_frame_count_per_second"] == 3.0)

# The loader mailbox stores only the latest 8-byte control frame. Prove that a
# completely missed first transfer pass is retried rather than aborting, and
# that each sequential word is held across multiple nominal foreground ticks.
class _FakePanda:
    def __init__(self):
        self.frames = []
    def can_send(self, address, data, bus):
        self.frames.append((address, bytes(data), bus))

fake_bundle = type("FakeBundle", (), {
    "helper": bytes.fromhex("1122334455667788"),
    "helper_words": 2,
    "meta": {"helper": {"padded_sha256": hashlib.sha256(bytes.fromhex("1122334455667788")).hexdigest()}},
})()
fake_session = object.__new__(inline_signer.InlineSignerSession)
fake_session.bundle = fake_bundle
fake_session.panda = _FakePanda()
base_state = {"initialized": True, "armed": False, "armed_raw": 0, "last_command5_rc": 0, "signed_count": 0}
fake_session.wait_initialized = lambda timeout=2.0: dict(base_state, next_index=0)
_state_reads = iter((dict(base_state, next_index=0), dict(base_state, next_index=2)))
fake_session.read_state = lambda: next(_state_reads)
fake_session.read_helper = lambda: fake_bundle.helper
_orig_sleep = inline_signer.time.sleep
inline_signer.time.sleep = lambda _: None
try:
    fake_load = inline_signer.InlineSignerSession.load_helper(fake_session)
finally:
    inline_signer.time.sleep = _orig_sleep
check("inline signer loader retries a zero-progress mailbox pass",
      len(fake_load["passes"]) == 2 and fake_load["passes"][0]["state_after"]["next_index"] == 0 and
      fake_load["passes"][1]["state_after"]["next_index"] == 2)
check("inline signer holds every sequential word across multiple foreground ticks",
      inline_signer.WORD_REPEAT_COUNT >= 3 and
      inline_signer.WORD_REPEAT_INTERVAL_SECONDS >= inline_signer.CONTROL_TICK_SECONDS and
      len(fake_session.panda.frames) == 2 * 2 * inline_signer.WORD_REPEAT_COUNT)

print("\n== car-kit packaging ==")
builder_path = ROOT / "tools/targets/camry/builders/build_camry_f33_car_kit.py"
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
    check("kit manifest is self-contained v12 and binds exact route", manifest["schema"] == "camry-f33-car-kit-v12" and manifest["target"] == {
        "eps_f181": "8965F3307000", "eps_diag": "0x7A1->0x7A9 bus0", "b6": "0x0B6/32 FD bus0",
    })
    check("kit pins live persistence-verified stage5 as current firmware", manifest["current_firmware"] == {
        "stage": 5,
        "sha256": "669cedf8c8465ebfd02318cb7708b897b817bc3b40925c89743b64ce49aa01af",
        "crc_prefix": "0x1960380A", "crc_fixup": "0xE69FC7F5",
        "note": "live persistence-verified 2026-09-01; no further persistent patch is part of the observer experiment",
    })
    inline = manifest["ram_experiments"]["b6_inline_signer"]
    check("kit packages native-B6 verify/replace signer as the primary fast path",
          inline["launcher"] == "f33-secoc" and
          inline["resident_base"] == "0xFEBFF9F0" and inline["resident_size"] == 520 and
          inline["resident_sha256"] == "38cd55db115456bfe72b747b509becf12916f633108a1073af48917ea44cad83" and
          inline["helper_base"] == "0xFEBF0000" and inline["helper_padded_size"] == 604 and
          inline["helper_word_count"] == 151 and
          inline["helper_padded_sha256"] == "44b5f04d350b7d5c384559ac1f6a1585416f9fcf6866b5dbdcc1cbd86fbbd0bd" and
          inline["state"]["base"] == "0xFEBF025C" and inline["state"]["magic"] == "0x53364249" and
          inline["telemetry"]["base"] == "0xFEBF0268" and inline["telemetry"]["size"] == 0x14 and
          inline["scratch"] == {"base": "0xFEBF0288", "size": 0x48, "sid23_readable": False} and
          probe.validate_read(probe.RAM_ID, int(inline["state"]["base"], 0), inline["state"]["size"]) is None and
          probe.validate_read(probe.RAM_ID, int(inline["telemetry"]["base"], 0), inline["telemetry"]["size"]) is None and
          inline["control_can_id"] == "0x1FDC0002" and "00 C7" in inline["runtime_control_frame"] and
          "native" in inline["native_oracle"].lower() and "B3..B9" in inline["replacement"] and
          inline["mutation_boundary"]["native_oracle_mutates_queue"] is False and
          inline["mutation_boundary"]["replacement_requires_native_mac_equality"] is True and
          inline["mutation_boundary"]["command5_failure_leaves_queue_unchanged"] is True and
          inline["mutation_boundary"]["secoc_result_override"] is False and
          inline["mutation_boundary"]["can_transmit"] is False and
          inline["persistent_flash_write"] is False and inline["live_qualified"] is False and
          manifest["ram_experiments"]["order"][0].startswith("b6_inline_signer is the production-shaped fast path"))
    mid = manifest["ram_experiments"]["b6_midaggregate_observer"]
    signer = manifest["ram_experiments"]["command5_probe"]
    check("kit packages bounded high-tail command5 permission probe",
          signer["payload_sha256"] == command5_probe.EXPECTED_PAYLOAD_SHA256 and
          signer["staging_sha256"] == command5_probe.EXPECTED_STAGING_SHA256 and
          signer["resident_sha256"] == command5_probe.EXPECTED_RESIDENT_SHA256 and
          signer["resident_size"] == 524 and signer["mailbox"] == "0xFEBF0000..0xFEBF004F" and
          signer["config_layout"] == "u32 type=1 at config+0; u32 selector=4 at config+4" and
          signer["transient_retry"] == "wrapper rc2 only; at most 3 total execute attempts" and
          "does not prove slot 4 is forbidden" in signer["negative_semantics"] and
          signer["persistent_flash_write"] is False and signer["key_extraction"] is False and
          signer["resident_b6_transmit"] is False and signer["secoc_bypass"] is False and
          "cooperative exact-token lease" in signer["panda_ownership"] and
          "without reset/recovery/flash" in signer["panda_ownership"] and
          manifest["ram_experiments"]["order"][1].startswith("command5_probe is retained as the already-live-qualified"))
    check("kit makes deterministic mid-aggregate observer the immediate ingress experiment",
          mid["payload_sha256"] == midagg.EXPECTED_PAYLOAD_SHA256 and
          mid["staging_sha256"] == midagg.EXPECTED_STAGING_SHA256 and
          mid["resident_sha256"] == midagg.EXPECTED_RESIDENT_SHA256 and mid["resident_size"] == 498 and
          mid["mailbox"] == "0xFEBF0000..0xFEBF0027" and
          mid["install_success_verdict"] == "runtime_midaggregate_observer_live" and
          mid["selfcheck_success_verdict"] == "midaggregate_observer_selfcheck_pass" and
          mid["marker_success_verdict"] == "exact_id63_b6_seen_after_canif_before_secoc" and
          mid["marker_negative_verdict"] == "id63_not_seen_at_midaggregate_boundary" and
          "0x79EDE" in mid["observation_boundary"] and "0x6A410" in mid["observation_boundary"] and
          "0x0D7" in mid["same_scheduler_positive_control"] and mid["marker_jitter_ms"] == [11,17,23,13,19] and
          mid["sid23_reads_during_treatment"] == 0 and mid["source_memory_write"] is False and
          mid["secoc_bypass"] is False and mid["route44_publish"] is False and mid["live_qualified"] is False and
          manifest["ram_experiments"]["order"][2].startswith("b6_midaggregate_observer install in NRTD"))
    mon = manifest["ram_experiments"]["runtime_monitor"]
    check("kit retains generic external-control monitor for downstream A-G localization",
          mon["payload_sha256"] == monitor.EXPECTED_PAYLOAD_SHA256 and
          mon["resident_sha256"] == monitor.EXPECTED_RESIDENT_SHA256 and mon["resident_size"] == 520 and
          mon["watch_slots"] == 8 and mon["control_can_id"] == "0x1FDC0002" and
          mon["control_frame"] == "00 F3 seq opcode arg32-le" and mon["source_memory_write"] is False and
          mon["dynamic_call"] is False and mon["resident_b6_transmit"] is False and mon["host_phase_b6_transmit"] is True and
          mon["stationary_monitor_phases"] == {k: [f"0x{x:08X}" for x in v] for k, v in monitor.MONITOR_PHASES.items()} and
          "current /data/openpilot opendbc" in mon["host_phase_b6_construction"])
    pre = manifest["ram_experiments"]["runtime_monitor_preaggregate"]
    check("kit retains live-tested pre-aggregate predecessor as timing-insufficient",
          pre["payload_sha256"] == preagg.EXPECTED_PAYLOAD_SHA256 and
          pre["staging_sha256"] == preagg.EXPECTED_STAGING_SHA256 and
          pre["resident_sha256"] == preagg.EXPECTED_RESIDENT_SHA256 and pre["resident_size"] == 522 and
          pre["sample_point"] == "after fg_pre_3, immediately before stock fg_aggregate" and
          "FEBE547A" in pre["run_trigger"] and pre["phase"] == {"P": [f"0x{x:08X}" for x in preagg.PREAGGREGATE_PHASES["P"]]} and
          pre["source_memory_write"] is False and pre["secoc_bypass"] is False and pre["live_qualified"] is True and
          pre["superseded_by"] == "b6_midaggregate_observer")
    ingress = manifest["ram_experiments"]["runtime_monitor_intertick"]
    check("kit retains inter-tick monitor only as superseded pre-live predecessor",
          ingress["payload_sha256"] == intertick.EXPECTED_PAYLOAD_SHA256 and
          ingress["staging_sha256"] == intertick.EXPECTED_STAGING_SHA256 and
          ingress["resident_sha256"] == intertick.EXPECTED_RESIDENT_SHA256 and ingress["resident_size"] == 518 and
          "before the tick test" in ingress["sample_point"] and "FEBE547A == 32" in ingress["run_trigger"] and
          ingress["success_verdict"] == "exact_phase_b6_queued_intertick" and ingress["source_memory_write"] is False and
          ingress["secoc_bypass"] is False and ingress["live_qualified"] is False and
          ingress["superseded_by"] == "b6_midaggregate_observer" and ingress["superseded_before_live_use"] is True)
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
    check("legacy C observer stays blocked while ABI-safe bridge is packaged but not live-qualified",
          manifest["ram_experiments"]["observer"]["bypass"] is False and
          manifest["ram_experiments"]["observer"]["payload_sha256"] == "5be3e474c965e3111957227f7db44b30aa2c6eca6ba341a8279ceea043e2728d" and
          manifest["ram_experiments"]["observer"]["live_qualified"] is False and
          "call0(address)" in manifest["ram_experiments"]["observer"]["blocked_by"] and
          manifest["ram_experiments"]["bridge"]["payload_sha256"] == "6d605013f1868295df6b998874e54f6c07ba8af2e9b839fc1243d1ac5a0126cd" and
          manifest["ram_experiments"]["bridge"]["call_abi"].startswith("direct linker-resolved JARL32") and
          "conservatively skip" in manifest["ram_experiments"]["bridge"]["behavior"] and
          "exact injected ID63 frame" in manifest["ram_experiments"]["bridge"]["requires_before_arm"] and
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
          (out / "f33").is_file() and (out / "f33").stat().st_mode & 0o111 and
          (out / "f33-pre").is_file() and (out / "f33-pre").stat().st_mode & 0o111 and
          (out / "f33-ingress").is_file() and (out / "f33-ingress").stat().st_mode & 0o111 and
          (out / "f33-secoc").is_file() and (out / "f33-secoc").stat().st_mode & 0o111 and all((out / rel).is_file() for rel in (
        "ram_payloads/camry_f33_runtime_monitor_payload.bin",
        "ram_payloads/camry_f33_runtime_monitor_preaggregate_payload.bin",
        "ram_payloads/camry_f33_runtime_monitor_intertick_payload.bin",
        "ram_payloads/camry_f33_b6_midaggregate_observer_payload.bin",
        "ram_payloads/camry_f33_b6_inline_signer_payload.bin",
        "ram_payloads/camry_f33_b6_inline_signer_helper_padded.bin",
        "ram_payloads/camry_f33_b6_inline_signer.json",
        "ram_payloads/camry_f33_runtime_replay_discriminator_payload.bin",
        "ram_payloads/camry_f33_b6_transaction_observer_payload.bin",
        "ram_payloads/camry_f33_b6_bridge_payload.bin",
        "runtime/exploit/common/ram_exec.py", "runtime/exploit/common/payload_package.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_transaction_observer_install.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_runtime_monitor.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_runtime_monitor_preaggregate.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_runtime_monitor_intertick.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_midaggregate_observer.py",
        "runtime/exploit/ephemeral_runtime/camry_f33_b6_inline_signer.py",
        "runtime/exploit/ephemeral_runtime/f33_panda_lease.sh",
        "runtime/exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.py",
        "runtime/exploit/followups/xcp_read_probe.py", "runtime/exploit/followups/xcp_daq_probe.py",
        "runtime/tools/targets/camry/live/camry_f33_steering_state_capture.py",
        "runtime/exploit/patcher/deploy.py", "runtime/exploit/patcher/restore.py",
        "runtime/exploit/patcher/post_apply_verify.py", "runtime/tools/security/build_secoc_patch_manifest.py",
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
    lease_source = (out / "runtime/exploit/ephemeral_runtime/f33_panda_lease.sh").read_text(encoding="utf-8")
    check("kit packages exact-token cooperative pandad lease helper",
          "kill -WINCH" in lease_source and "openpilot-pandad-direct-ready" in lease_source and
          "DIRECT_PANDA_LEASE_ID" in lease_source and 'kill -STOP "$PANDAD_WRAPPER_PID"' not in lease_source and
          (out / "runtime/exploit/ephemeral_runtime/f33_panda_lease.sh").stat().st_mode & 0o111)
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
    check("runbook is launcher-first and pins deterministic ingress before legacy monitors",
          "generic runtime monitor" in runbook and "runtime_monitor_live" in runbook and
          "./f33 doctor" in runbook and "./f33 install" in runbook and "./f33 shell" in runbook and
          "./f33-ingress install" in runbook and "./f33-ingress selfcheck" in runbook and
          "./f33-ingress marker" in runbook and "runtime_midaggregate_observer_live" in runbook and
          "midaggregate_observer_selfcheck_pass" in runbook and
          "./f33-pre phase P" in runbook and
          "watch SLOT ADDRESS" in runbook and "./f33 phase A" in runbook and "current opendbc" in runbook and
          "superseded" in runbook)
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
          "manager/manager\\.py" in launcher_text and "pandad" in launcher_text and "boardd" in launcher_text and
          "phase requires a phase name" in launcher_text and 'monitor phase "$@" --execute' in launcher_text)
    secoc_launcher = out / "f33-secoc"
    secoc_launcher_text = secoc_launcher.read_text(encoding="utf-8")
    check("inline signer launcher preserves manager lifecycle and exposes install/load-arm/status/quiet-source/replace-once",
          "systemctl stop openpilot" not in secoc_launcher_text and
          'kill -STOP "$PANDAD_WRAPPER_PID"' not in secoc_launcher_text and
          'kill -CONT "$PANDAD_WRAPPER_PID"' not in secoc_launcher_text and
          "start_power_watchdog_keeper" not in secoc_launcher_text and
          "f33_panda_lease.sh" in secoc_launcher_text and
          "source \"$PANDA_LEASE_LIB\"" in secoc_launcher_text and
          "load-arm" in secoc_launcher_text and "quiet-source" in secoc_launcher_text and "replace-once" in secoc_launcher_text and
          "verify_openpilot_ready_parked" in secoc_launcher_text and
          secoc_launcher_text.index("verify_openpilot_ready_parked") < secoc_launcher_text.rindex("quiesce_panda_owner") and
          "camry_f33_b6_inline_signer_helper_padded.bin" in secoc_launcher_text)
    local_openpilot = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
    local_python = local_openpilot / ".venv/bin/python"
    env = dict(os.environ, F33_PYTHON=str(local_python), F33_OPENPILOT_ROOT=str(local_openpilot))
    secoc_doctor = subprocess.run([str(secoc_launcher), "doctor"], cwd=out, env=env, capture_output=True, text=True, check=False)
    check("built inline signer launcher doctor validates payload/helper/metadata without Panda access",
          secoc_doctor.returncode == 0 and "f33-secoc doctor: PASS" in secoc_doctor.stdout, secoc_doctor.stderr[-300:])
    secoc_plan = subprocess.run([str(secoc_launcher), "plan"], cwd=out, env=env, capture_output=True, text=True, check=False)
    secoc_plan_obj = json.loads(secoc_plan.stdout) if secoc_plan.returncode == 0 else {}
    check("built inline signer launcher plan is no-roundtrip architecture",
          secoc_plan.returncode == 0 and secoc_plan_obj.get("schema") == "camry-f33-b6-inline-signer-plan-v1" and
          secoc_plan_obj.get("resident", {}).get("size") == 520 and secoc_plan_obj.get("helper", {}).get("word_count") == 151 and
          secoc_plan_obj.get("telemetry", {}).get("base") == "0xFEBF0268" and secoc_plan_obj.get("telemetry", {}).get("size") == 0x14 and
          any("native B6" in row for row in secoc_plan_obj.get("sequence", [])),
          secoc_plan.stderr[-300:])
    doctor = subprocess.run([str(launcher), "doctor"], cwd=out, env=env, capture_output=True, text=True, check=False)
    check("built launcher doctor validates imports and payload without Panda access",
          doctor.returncode == 0 and "f33 doctor: PASS" in doctor.stdout and monitor.EXPECTED_PAYLOAD_SHA256 in doctor.stdout, doctor.stderr[-300:])
    launch_plan = subprocess.run([str(launcher), "plan"], cwd=out, env=env, capture_output=True, text=True, check=False)
    plan_obj = json.loads(launch_plan.stdout) if launch_plan.returncode == 0 else {}
    check("built launcher plan resolves canonical monitor with no manual arguments",
          launch_plan.returncode == 0 and plan_obj.get("schema") == "camry-f33-runtime-monitor-plan-v1" and
          plan_obj.get("payload", {}).get("sha256") == monitor.EXPECTED_PAYLOAD_SHA256, launch_plan.stderr[-300:])
    pre_launcher = out / "f33-pre"
    pre_launcher_text = pre_launcher.read_text(encoding="utf-8")
    check("pre-aggregate launcher pins separate host/payload identities",
          "camry_f33_runtime_monitor_preaggregate.py" in pre_launcher_text and
          "camry_f33_runtime_monitor_preaggregate_payload.bin" in pre_launcher_text and
          preagg.EXPECTED_PAYLOAD_SHA256 in pre_launcher_text)
    pre_doctor = subprocess.run([str(pre_launcher), "doctor"], cwd=out, env=env, capture_output=True, text=True, check=False)
    check("built pre-aggregate launcher doctor validates exact payload without Panda access",
          pre_doctor.returncode == 0 and "f33 doctor: PASS" in pre_doctor.stdout and
          preagg.EXPECTED_PAYLOAD_SHA256 in pre_doctor.stdout, pre_doctor.stderr[-300:])
    ingress_launcher = out / "f33-ingress"
    ingress_launcher_text = ingress_launcher.read_text(encoding="utf-8")
    check("mid-aggregate ingress launcher pins separate host/payload identities",
          "camry_f33_b6_midaggregate_observer.py" in ingress_launcher_text and
          "camry_f33_b6_midaggregate_observer_payload.bin" in ingress_launcher_text and
          midagg.EXPECTED_PAYLOAD_SHA256 in ingress_launcher_text and
          "selfcheck" in ingress_launcher_text and "marker" in ingress_launcher_text)
    ingress_doctor = subprocess.run([str(ingress_launcher), "doctor"], cwd=out, env=env, capture_output=True, text=True, check=False)
    check("built mid-aggregate launcher doctor validates exact payload without Panda access",
          ingress_doctor.returncode == 0 and "f33-ingress doctor: PASS" in ingress_doctor.stdout and
          midagg.EXPECTED_PAYLOAD_SHA256 in ingress_doctor.stdout, ingress_doctor.stderr[-300:])
    ingress_plan = subprocess.run([str(ingress_launcher), "plan"], cwd=out, env=env, capture_output=True, text=True, check=False)
    ingress_plan_obj = json.loads(ingress_plan.stdout) if ingress_plan.returncode == 0 else {}
    check("built mid-aggregate launcher plan resolves exact deterministic observer",
          ingress_plan.returncode == 0 and ingress_plan_obj.get("schema") == "camry-f33-b6-midaggregate-plan-v1" and
          ingress_plan_obj.get("payload", {}).get("sha256") == midagg.EXPECTED_PAYLOAD_SHA256 and
          ingress_plan_obj.get("treatment_statistics", {}).get("sid23_reads_during_block") == 0,
          ingress_plan.stderr[-300:])
    sign_launcher = out / "f33-sign"
    sign_launcher_text = sign_launcher.read_text(encoding="utf-8")
    check("command-5 launcher pins host/payload identities",
          "camry_f33_command5_probe.py" in sign_launcher_text and
          "camry_f33_command5_probe_payload.bin" in sign_launcher_text and
          command5_probe.EXPECTED_PAYLOAD_SHA256 in sign_launcher_text)
    sign_doctor = subprocess.run([str(sign_launcher), "doctor"], cwd=out, env=env, capture_output=True, text=True, check=False)
    check("built command-5 launcher doctor validates exact payload without Panda access",
          sign_doctor.returncode == 0 and "f33-sign doctor: PASS" in sign_doctor.stdout and
          command5_probe.EXPECTED_PAYLOAD_SHA256 in sign_doctor.stdout, sign_doctor.stderr[-300:])
    sign_plan = subprocess.run([str(sign_launcher), "plan"], cwd=out, env=env, capture_output=True, text=True, check=False)
    sign_plan_obj = json.loads(sign_plan.stdout) if sign_plan.returncode == 0 else {}
    check("built command-5 launcher plan resolves bounded non-actuating probe",
          sign_plan.returncode == 0 and sign_plan_obj.get("schema") == "camry-f33-command5-probe-plan-v2" and
          sign_plan_obj.get("payload", {}).get("sha256") == command5_probe.EXPECTED_PAYLOAD_SHA256 and
          sign_plan_obj.get("boundaries", {}).get("b6_transmit") is False and
          sign_plan_obj.get("boundaries", {}).get("key_extraction") is False, sign_plan.stderr[-300:])
    check("kit manifest hashes launchers and root runbook",
          manifest["files"]["f33"]["sha256"] == sha(launcher.read_bytes()) and
          manifest["files"]["f33-pre"]["sha256"] == sha(pre_launcher.read_bytes()) and
          manifest["files"]["f33-ingress"]["sha256"] == sha(ingress_launcher.read_bytes()) and
          manifest["files"]["f33-sign"]["sha256"] == sha(sign_launcher.read_bytes()) and
          manifest["files"]["RUNBOOK.md"]["sha256"] == sha((out / "RUNBOOK.md").read_bytes()))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
