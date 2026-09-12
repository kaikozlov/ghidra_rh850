#!/usr/bin/env python3
"""Verify the fail-closed, hardware-free isolated EPS CAN probe."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_support import toyota_eps_isolated_can_probe as probe

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def expect_probe_error(name: str, fn) -> None:
    try:
        fn()
    except probe.ProbeError:
        check(name, True)
    else:
        check(name, False)


print("== fixed dry-run / transmit surface ==")
plan = probe.build_plan()
check("route is fixed to orientation-stable Panda bus 1", plan["route"]["panda_bus"] == 1 and "not swapped" in plan["route"]["controller"])
check("CAN geometry is 500k/2M ISO with auto disabled", plan["can"] == {
    "nominal_kbps": 500,
    "data_kbps": 2000,
    "canfd_non_iso": False,
    "canfd_auto": False,
    "controller_loopback": False,
    "explicit_frame_format": True,
})
check("at most three gated host submissions are possible", plan["max_host_submissions"] == 3 and "only a validated positive 7E00 reply plus complete clean" in plan["state_machine"] and [p.name for p in probe.TX_PHASES] == [
    "tester-present-classical", "f181-classical", "tester-present-fd", "f181-fd",
])
check("plan discloses automatic wire retries and F181 early-stop", "retry each host submission" in plan["automatic_retransmission"] and "same-format F181" in plan["early_stop"] and "even if F181 is silent" in plan["early_stop"] and "negative TesterPresent stops" in plan["early_stop"] and "without flow control" in plan["early_stop"])
check("bounded NOOUTPUT transition monitoring precedes TX", plan["passive_listen"] == {
    "settle_seconds_after_each_transition": 1.0,
    "transitions": ["aux-negative reconnect with IG OFF", "IG ON / not READY"],
    "panda_safety": "NOOUTPUT (host data frames blocked; protocol ACK bits enabled)",
    "tx_count": 0,
    "collection": "baseline before each prompt through post-attestation settle; read CAN-health RX delta first and call can_recv only when queued RX is proven",
    "loss_policy": "any controller/Panda fault or drift, unexpected host TX receipt, controller RX loss, or Panda RX overflow stops before active TX",
})
check("TesterPresent request is exact padded ISO-TP SF", probe.TESTER_PRESENT_FRAME.hex() == "023e000000000000")
check("F181 request is exact padded ISO-TP SF", probe.F181_FRAME.hex() == "0322f18100000000")
check("both requests are emitted explicitly as Classical and FD", [(p.data, p.fd) for p in probe.TX_PHASES] == [
    (probe.TESTER_PRESENT_FRAME, False), (probe.F181_FRAME, False),
    (probe.TESTER_PRESENT_FRAME, True), (probe.F181_FRAME, True),
])
check("CAN0/CAN2 relay has no direct control and no physical legs", "no direct/debug control" in plan["route"]["can0_can2_intercept_relay"] and "physically unconnected" in plan["route"]["can0_can2_intercept_relay"])
check("plan never treats a TX echo as physical ACK", "never called physical ACK" in plan["ack_discriminator"]["boundary"])
check("plan requires exact TX receipt and bounded native-RX reconciliation", "exactly one" in plan["rx_accounting"]["tx_receipt_gate"] and "reconcile exactly" in plan["rx_accounting"]["bounded_drain"])
check("mutating/session surfaces are explicitly forbidden", all(token in plan["forbidden"] for token in (
    "DiagnosticSessionControl", "SecurityAccess", "WriteDataByIdentifier", "RoutineControl",
    "RequestDownload", "TransferData", "RequestTransferExit", "flow-control TX",
)))

for phase in probe.TX_PHASES:
    probe.assert_allowed_tx(probe.TX_ADDR, phase.data, phase.fd)
check("all four planned frames pass the hard allowlist", True)
for description, address, data, fd in (
    ("programming session", probe.TX_ADDR, bytes.fromhex("0210020000000000"), False),
    ("SecurityAccess", probe.TX_ADDR, bytes.fromhex("0227010000000000"), False),
    ("RequestDownload", probe.TX_ADDR, bytes.fromhex("0134000000000000"), False),
    ("functional address", 0x777, probe.TESTER_PRESENT_FRAME, False),
    ("modified padding", probe.TX_ADDR, bytes.fromhex("0322f18100000001"), True),
    ("non-boolean frame-format selector", probe.TX_ADDR, probe.F181_FRAME, 1),
):
    expect_probe_error(f"allowlist blocks {description}", lambda a=address, d=data, f=fd: probe.assert_allowed_tx(a, d, f))


print("\n== physical execution gates ==")
valid = probe.PhysicalPreflight(
    a30_disconnected=True,
    a30_mating_connector_correct_terminals_no_backprobe_no_piercing_no_generic_pin=True,
    stationary=True,
    parking_brake_set=True,
    level_ground=True,
    wheel_chocks=True,
    foot_off_brake=True,
    probe_will_use_ignition_on_not_ready=True,
    ignition_off_now=True,
    auxiliary_battery_negative_disconnected_now=True,
    usb_host_battery_powered_not_vehicle_or_mains=True,
    rack_only_peer=True,
    common_ground=True,
    dc1_polarity_verified=True,
    resistance_measured_power_off=True,
    battery_negative_disconnected_for_isolation_checks=True,
    meter_removed=True,
    openpilot_stopped=True,
    rack_only_ohms=120.0,
    complete_bus_ohms=60.0,
    dc1h_to_ground_ohms=1000.0,
    dc1l_to_ground_ohms=1000.0,
    dc1h_to_aux_positive_ohms=10000.0,
    dc1l_to_aux_positive_ohms=10000.0,
    external_can1_termination_installed=True,
    unused_can1_pass_through_unconnected=True,
    only_can1_connected=True,
    arm=probe.ARM_TOKEN,
)
probe.validate_preflight(valid, 1)
check("fully attested bus-1 preflight passes", True)
expect_probe_error("missing A30 disconnect fails closed", lambda: probe.validate_preflight(replace(valid, a30_disconnected=False), 1))
for field in (
    "a30_mating_connector_correct_terminals_no_backprobe_no_piercing_no_generic_pin",
    "parking_brake_set",
    "level_ground",
    "wheel_chocks",
    "foot_off_brake",
    "probe_will_use_ignition_on_not_ready",
    "ignition_off_now",
    "auxiliary_battery_negative_disconnected_now",
    "usb_host_battery_powered_not_vehicle_or_mains",
    "dc1_polarity_verified",
    "battery_negative_disconnected_for_isolation_checks",
):
    expect_probe_error(
        f"{field} attestation fails closed",
        lambda field=field: probe.validate_preflight(replace(valid, **{field: False}), 1),
    )
expect_probe_error("wrong arm token fails closed", lambda: probe.validate_preflight(replace(valid, arm="yes"), 1))
expect_probe_error("out-of-range rack-only resistance fails closed", lambda: probe.validate_preflight(replace(valid, rack_only_ohms=80.0), 1))
expect_probe_error("NaN complete-bus resistance fails closed", lambda: probe.validate_preflight(replace(valid, complete_bus_ohms=float("nan")), 1))
for field, bad_value in (
    ("dc1h_to_ground_ohms", 199.0),
    ("dc1l_to_ground_ohms", 199.0),
    ("dc1h_to_aux_positive_ohms", 5999.0),
    ("dc1l_to_aux_positive_ohms", 5999.0),
):
    expect_probe_error(
        f"{field} isolation threshold fails closed",
        lambda field=field, bad_value=bad_value: probe.validate_preflight(
            replace(valid, **{field: bad_value}), 1
        ),
    )
expect_probe_error("meter must be removed before live execution", lambda: probe.validate_preflight(replace(valid, meter_removed=False), 1))
expect_probe_error("live preflight rejects orientation-ambiguous bus 0", lambda: probe.validate_preflight(valid, 0))
expect_probe_error("dry plan also rejects orientation-ambiguous bus 0", lambda: probe.build_plan(0))
expect_probe_error("external CAN1 termination is mandatory", lambda: probe.validate_preflight(replace(valid, external_can1_termination_installed=False), 1))
expect_probe_error("unused CAN1 pass-through must be unconnected", lambda: probe.validate_preflight(replace(valid, unused_can1_pass_through_unconnected=False), 1))
expect_probe_error("standalone adapter must expose only CAN1", lambda: probe.validate_preflight(replace(valid, only_can1_connected=False), 1))
expect_probe_error("settle interval cannot be shortened below error observation window", lambda: probe.build_plan(1, 0.05))
expect_probe_error("passive interval is bounded", lambda: probe.build_plan(1, probe.DEFAULT_SETTLE_SECONDS, 10.0))
mapped_flags = probe._preflight_from_args(probe.build_parser().parse_args([
    "--confirm-dc1h-dc1l-polarity",
    "--confirm-a30-mating-connector-correct-terminals-no-backprobe-no-piercing-no-generic-pin",
]))
check("CLI polarity and nondamaging-connection attestations map to the correct gates", mapped_flags.dc1_polarity_verified and mapped_flags.a30_mating_connector_correct_terminals_no_backprobe_no_piercing_no_generic_pin)


print("\n== native / echo / rejection and health discriminator ==")
rows = [
    (0x7A1, probe.TESTER_PRESENT_FRAME, 129),
    (0x7A9, bytes.fromhex("027e000000000000"), 1),
    (0x7A1, probe.TESTER_PRESENT_FRAME, 193),
    (0x123, b"\x01", 2),
]
frames = probe.classify_frames(rows, 1)
check("frame sources stay in four separate inventories", [len(frames[key]) for key in (
    "native", "tx_echo", "tx_rejected", "other_source",
)] == [1, 1, 1, 1])
base_health = {
    "bus_off": False, "bus_off_cnt": 0, "error_warning": False, "error_passive": False,
    "transmit_error_cnt": 0, "total_error_cnt": 4, "total_tx_lost_cnt": 0,
    "total_rx_lost_cnt": 0, "total_tx_cnt": 10, "total_rx_cnt": 20,
    "total_tx_checksum_error_cnt": 0, "can_core_reset_count": 1,
    "last_error": "No error", "last_stored_error": "No error",
    "last_data_error": "No error", "last_data_stored_error": "No error",
    "receive_error_cnt": 0,
    "can_speed": 500, "can_data_speed": 2000, "canfd_enabled": True,
    "brs_enabled": True, "canfd_non_iso": False,
    "total_fwd_cnt": 0,
}
base_panda_health = {
    "uptime": 100,
    "safety_tx_blocked": 0,
    "safety_rx_invalid": 0,
    "tx_buffer_overflow": 0,
    "rx_buffer_overflow": 0,
    "faults": 0,
    "safety_mode": probe.ELM327_SAFETY_MODE,
    "safety_param": probe.ELM327_NORMAL_ROUTE_PARAM,
    "heartbeat_lost": False,
    "power_save_enabled": False,
    "car_harness_status": 0,
}

def assess_test(frames, before, after, *, request_data=probe.TESTER_PRESENT_FRAME, panda_after=None):
    after = dict(after)
    if isinstance(before.get("total_rx_cnt"), int):
        after["total_rx_cnt"] = before["total_rx_cnt"] + len(frames["native"])
    merged_panda_after = dict(base_panda_health)
    if panda_after is not None:
        merged_panda_after.update(panda_after)
    return probe.assess_phase(
        frames,
        before,
        after,
        request_data=request_data,
        panda_health_before=base_panda_health,
        panda_health_after=merged_panda_after,
    )

response_frames = probe.classify_frames(rows[:2], 1)
response = assess_test(response_frames, base_health, dict(base_health, total_tx_cnt=11))
check("validated native 0x7A9 diagnostic reply confirms request response and ACK", response["verdict"] == "matched-eps-diagnostic-response" and response["wire_ack"] == "confirmed-by-native-response")
echo_only = probe.classify_frames(rows[:1], 1)
clean = assess_test(echo_only, base_health, dict(base_health, total_tx_cnt=11))
check("clean echo-only phase is labeled ACK-consistent, not confirmed", clean["verdict"] == "ack-consistent-no-eps-response" and clean["wire_ack"] == "inferred-from-clean-controller-health")
incomplete_health = dict(base_health)
del incomplete_health["transmit_error_cnt"]
incomplete = assess_test(echo_only, base_health, incomplete_health)
check("missing required CAN-health counter blocks clean ACK inference", incomplete["verdict"] == "can-health-incomplete" and incomplete["wire_ack"] == "indeterminate" and incomplete["can_health_contract_errors"])
missing_panda_health = dict(base_panda_health)
del missing_panda_health["safety_tx_blocked"]
incomplete_panda = probe.assess_phase(
    echo_only,
    base_health,
    dict(base_health, total_tx_cnt=11),
    request_data=probe.TESTER_PRESENT_FRAME,
    panda_health_before=missing_panda_health,
    panda_health_after=missing_panda_health,
)
check("missing required Panda-health counter blocks clean ACK inference", incomplete_panda["verdict"] == "can-health-incomplete" and not incomplete_panda["phase_evidence_valid"] and incomplete_panda["panda_health_contract_errors"])
rx_loss = assess_test(
    echo_only,
    base_health,
    dict(base_health, total_tx_cnt=11, total_rx_lost_cnt=1),
)
check("controller RX loss invalidates an otherwise clean phase", rx_loss["verdict"] == "can-rx-evidence-loss-or-overflow" and rx_loss["can_rx_evidence_lost"] and not rx_loss["fd_fallback_eligible"])
rx_overflow = assess_test(
    echo_only,
    base_health,
    dict(base_health, total_tx_cnt=11),
    panda_after={"rx_buffer_overflow": 1},
)
check("Panda RX overflow invalidates an otherwise clean phase", rx_overflow["verdict"] == "can-rx-evidence-loss-or-overflow" and rx_overflow["panda_rx_buffer_overflow_delta_mod32"] == 1 and not rx_overflow["controller_health_clean"])
ack_failure_health = dict(
    base_health,
    total_tx_cnt=11,
    total_error_cnt=5,
    can_core_reset_count=2,
    last_error="AckError",
    last_stored_error="AckError",
)
ack_failure = assess_test(echo_only, base_health, ack_failure_health)
check("AckError/core reset overrides host echo", ack_failure["verdict"] == "ack-error-or-link-fault" and ack_failure["wire_ack"] == "not-observed" and ack_failure["can_core_reset"])
form_error_health = dict(base_health, total_tx_cnt=11, total_error_cnt=5, last_error="Form error", last_stored_error="Form error")
form_failure = assess_test(echo_only, base_health, form_error_health)
check("non-ACK CAN errors also prevent a clean-ACK inference", form_failure["verdict"] == "can-controller-error-or-link-fault" and form_failure["wire_ack"] == "not-observed")
persistent_tec_health = dict(base_health, transmit_error_cnt=3)
persistent_tec = assess_test(
    echo_only,
    persistent_tec_health,
    dict(persistent_tec_health, total_tx_cnt=11),
)
check("nonzero pre-existing TEC is never considered complete clean health", persistent_tec["verdict"] == "tx-queued-health-indeterminate" and not persistent_tec["controller_health_clean"] and not persistent_tec["fd_fallback_eligible"])
persistent_lec_health = dict(base_health, last_error="Form error")
persistent_lec = assess_test(
    echo_only,
    persistent_lec_health,
    dict(persistent_lec_health, total_tx_cnt=11),
)
check("reported controller error is never considered complete clean health", persistent_lec["verdict"] == "tx-queued-health-indeterminate" and persistent_lec["reported_controller_error"] and not persistent_lec["controller_health_clean"])
stale_stored_error_health = dict(base_health, last_stored_error="Form error")
stale_stored_error = assess_test(
    echo_only,
    stale_stored_error_health,
    dict(stale_stored_error_health, total_tx_cnt=11),
)
check("unchanged historical stored LEC does not masquerade as a new controller fault", stale_stored_error["verdict"] == "ack-consistent-no-eps-response" and stale_stored_error["controller_health_clean"] and not stale_stored_error["controller_error_field_changed"])
nochange_health = dict(
    base_health,
    last_error="NoChange",
    last_data_error="NoChange",
    total_tx_cnt=11,
)
nochange = assess_test(echo_only, base_health, nochange_health)
check("FDCAN NoError to NoChange read transition stays clean", nochange["verdict"] == "ack-consistent-no-eps-response" and nochange["controller_health_clean"] and not nochange["controller_error_field_changed"])
probe._verify_panda_configuration(
    base_panda_health,
    dict(base_health, last_error="NoChange", last_data_error="NoChange"),
    expected_safety_mode=probe.ELM327_SAFETY_MODE,
    expected_safety_param=probe.ELM327_NORMAL_ROUTE_PARAM,
)
check("configuration readback accepts FDCAN NoChange as clean", True)
rejected_only = probe.classify_frames(rows[2:3], 1)
rejected = assess_test(rejected_only, base_health, base_health)
check("Panda rejection is never mistaken for wire activity", rejected["verdict"] == "host-safety-rejected" and rejected["wire_ack"] == "not-transmitted")
positive_native_row = (probe.RX_ADDR, bytes.fromhex("027e000000000000"), 1)
wrong_echo_frames = probe.classify_frames([
    (probe.TX_ADDR, probe.F181_FRAME, 129),
    positive_native_row,
], 1)
wrong_echo = assess_test(wrong_echo_frames, base_health, dict(base_health, total_tx_cnt=11))
check("wrong-payload source-129 echo cannot gate follow-up", wrong_echo["matched_diagnostic_response_count"] == 1 and not wrong_echo["host_tx_receipt_confirmed"] and not wrong_echo["phase_evidence_valid"])
duplicate_echo_frames = probe.classify_frames([
    (probe.TX_ADDR, probe.TESTER_PRESENT_FRAME, 129),
    (probe.TX_ADDR, probe.TESTER_PRESENT_FRAME, 129),
    positive_native_row,
], 1)
duplicate_echo = assess_test(duplicate_echo_frames, base_health, dict(base_health, total_tx_cnt=11))
check("duplicate source-129 echoes cannot gate follow-up", duplicate_echo["tx_echo_count"] == 2 and not duplicate_echo["host_tx_receipt_confirmed"] and not duplicate_echo["phase_evidence_valid"])
wrong_tx_delta = assess_test(response_frames, base_health, dict(base_health, total_tx_cnt=12))
check("total_tx_cnt delta greater than one cannot gate follow-up", wrong_tx_delta["can_health_delta_mod32"]["total_tx_cnt"] == 2 and not wrong_tx_delta["host_tx_receipt_confirmed"] and not wrong_tx_delta["phase_evidence_valid"])
other_source_frames = probe.classify_frames([
    (probe.TX_ADDR, probe.TESTER_PRESENT_FRAME, 129),
    positive_native_row,
    (0x123, b"\x01", 0),
], 1)
other_source = assess_test(other_source_frames, base_health, dict(base_health, total_tx_cnt=11))
check("other-source contamination overrides an otherwise valid TP response", other_source["verdict"] == "unexpected-source-topology-contamination" and other_source["topology_contaminated"] and not other_source["phase_evidence_valid"])
unmatched_native = assess_test(
    probe.classify_frames([(probe.RX_ADDR, bytes.fromhex("0123000000000000"), 1)], 1),
    base_health,
    dict(base_health, total_tx_cnt=11),
)
check("arbitrary native 0x7A9 is peer traffic, not a diagnostic response or fallback without TX receipt", unmatched_native["verdict"] == "native-eps-frame-diagnostic-unmatched" and unmatched_native["matched_diagnostic_response_count"] == 0 and unmatched_native["wire_ack"] == "request-ack-indeterminate" and not unmatched_native["host_tx_receipt_confirmed"] and not unmatched_native["fd_fallback_eligible"])
boot_extended_f181 = bytes([0, 0x24]) + bytes.fromhex("62f181") + probe.BOOT_F181_BODY
application_extended_f181 = bytes([0, 0x24]) + bytes.fromhex("62f181") + probe.APPLICATION_F181_BODY
check("known boot F181 FirstFrame is only a boot prefix", probe.classify_f181_identity_response(bytes.fromhex("102462f181022121")) == "boot-prefix")
check("known application F181 FirstFrame is only an application prefix", probe.classify_f181_identity_response(bytes.fromhex("102462f181023839")) == "application-prefix")
check("exact complete boot F181 extended SF gets full label", probe.classify_f181_identity_response(boot_extended_f181) == "boot-full")
check("exact complete application F181 extended SF gets full label", probe.classify_f181_identity_response(application_extended_f181) == "application-full")
boot_near_miss = bytearray(boot_extended_f181)
boot_near_miss[-1] ^= 1
application_near_miss = bytearray(application_extended_f181)
application_near_miss[-1] ^= 1
check("near-miss boot extended SF remains unknown", probe.classify_f181_identity_response(boot_near_miss) == "unknown")
check("near-miss application extended SF remains unknown", probe.classify_f181_identity_response(application_near_miss) == "unknown")
check("unrecognized F181 identity body stays unknown", probe.classify_f181_identity_response(bytes.fromhex("102462f18102abcd")) == "unknown")
check("non-F181 response has no restore-route classification", probe.classify_f181_identity_response(bytes.fromhex("027e000000000000")) is None)
f181_extended_payload = bytes.fromhex("62f181023839") + bytes(30)
for description, request, reply in (
    ("TesterPresent positive", probe.TESTER_PRESENT_FRAME, bytes.fromhex("027e000000000000")),
    ("TesterPresent negative", probe.TESTER_PRESENT_FRAME, bytes.fromhex("037f3e1100000000")),
    ("F181 positive extended SF", probe.F181_FRAME, bytes([0, 0x24]) + f181_extended_payload),
    ("F181 positive FF", probe.F181_FRAME, bytes.fromhex("102462f181023839")),
    ("F181 negative", probe.F181_FRAME, bytes.fromhex("037f223100000000")),
):
    check(f"phase matcher accepts {description}", probe.classify_phase_response(request, reply) is not None)
for description, request, reply in (
    ("truncated TP negative", probe.TESTER_PRESENT_FRAME, bytes.fromhex("027f3e0000000000")),
    ("wrong-length F181 FirstFrame", probe.F181_FRAME, bytes.fromhex("101362f181023839")),
    ("bare short F181 positive", probe.F181_FRAME, bytes.fromhex("0362f18100000000")),
):
    check(f"phase matcher rejects {description}", probe.classify_phase_response(request, reply) is None)


print("\n== mocked live orchestration (no hardware) ==")
class FakePanda:
    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.safety_mode = 73  # representative car safety: heartbeat-disable must be ignored here
        self.safety_param = 0
        self.heartbeat_disabled = False
        self.heartbeat_lost = False
        self.uptime = 100
        self.safety_tx_blocked = 0
        self.safety_rx_invalid = 0
        self.tx_buffer_overflow = 0
        self.rx_buffer_overflow = 0
        self.faults = 0
        self.power_save_enabled = False
        self.car_harness_status = 0
        self.speed = 0
        self.data_speed = 0
        self.non_iso = True
        self.fd_enabled = False
        self.brs = False
        self.total_tx = 0
        self.total_rx = 0
        self.total_error = 0
        self.total_tx_lost = 0
        self.total_tx_checksum_error = 0
        self.total_rx_lost = 0
        self.total_fwd = 0
        self.receive_error = 0
        self.core_resets = 0
        self.error = "No error"
        self.pending: list[tuple[int, bytes, int]] = []
        self.send_count = 0

    def send_heartbeat(self, engaged=True):
        self.calls.append(("heartbeat", engaged))
        self.heartbeat_disabled = False

    def set_heartbeat_disabled(self):
        accepted = self.safety_mode in {
            probe.SILENT_SAFETY_MODE,
            probe.NOOUTPUT_SAFETY_MODE,
            probe.ELM327_SAFETY_MODE,
        }
        self.calls.append(("heartbeat_disabled", accepted))
        if accepted:
            self.heartbeat_disabled = True

    def operator_prompt_wait(self):
        self.calls.append(("operator_wait", self.heartbeat_disabled))
        if not self.heartbeat_disabled:
            self.safety_mode = probe.SILENT_SAFETY_MODE

    def can_clear(self, bus):
        self.calls.append(("can_clear", bus))
        if bus == 0xFFFF:
            self.pending.clear()

    def set_safety_mode(self, mode, param=0):
        self.calls.append(("safety", mode, param))
        self.safety_mode = mode
        self.safety_param = param

    def set_can_loopback(self, enabled):
        self.calls.append(("loopback", enabled))

    def set_can_speed_kbps(self, bus, speed):
        self.calls.append(("speed", bus, speed))
        self.speed = speed

    def set_can_data_speed_kbps(self, bus, speed):
        self.calls.append(("data_speed", bus, speed))
        self.data_speed = speed
        self.fd_enabled = True
        self.brs = speed > self.speed

    def set_canfd_non_iso(self, bus, non_iso):
        self.calls.append(("non_iso", bus, non_iso))
        self.non_iso = non_iso

    def set_canfd_auto(self, bus, auto):
        self.calls.append(("fd_auto", bus, auto))

    def health(self):
        return {
            "uptime": self.uptime,
            "safety_tx_blocked": self.safety_tx_blocked,
            "safety_rx_invalid": self.safety_rx_invalid,
            "tx_buffer_overflow": self.tx_buffer_overflow,
            "safety_mode": self.safety_mode,
            "safety_param": self.safety_param,
            "heartbeat_lost": self.heartbeat_lost,
            "power_save_enabled": self.power_save_enabled,
            "faults": self.faults,
            "car_harness_status": self.car_harness_status,
            "rx_buffer_overflow": self.rx_buffer_overflow,
        }

    def can_health(self, bus):
        return {
            "bus_off": False,
            "bus_off_cnt": 0,
            "error_warning": False,
            "error_passive": False,
            "transmit_error_cnt": 0,
            "total_error_cnt": self.total_error,
            "total_tx_lost_cnt": self.total_tx_lost,
            "total_rx_lost_cnt": self.total_rx_lost,
            "total_fwd_cnt": self.total_fwd,
            "total_tx_cnt": self.total_tx,
            "total_rx_cnt": self.total_rx,
            "total_tx_checksum_error_cnt": self.total_tx_checksum_error,
            "can_core_reset_count": self.core_resets,
            "last_error": self.error,
            "last_stored_error": self.error,
            "last_data_error": "No error",
            "last_data_stored_error": "No error",
            "receive_error_cnt": self.receive_error,
            "can_speed": self.speed,
            "can_data_speed": self.data_speed,
            "canfd_enabled": self.fd_enabled,
            "brs_enabled": self.brs,
            "canfd_non_iso": self.non_iso,
        }

    def can_send(self, address, data, bus, *, fd=False):
        self.calls.append(("send", address, bytes(data), bus, fd))
        self.send_count += 1
        self.total_tx += 1
        self.pending.append((address, bytes(data), bus + 128))

    def can_recv(self):
        rows, self.pending = self.pending, []
        return rows


fake = FakePanda()
sleep_calls = 0
attestation_calls: list[tuple[str, int, int]] = []
def fake_sleep(_seconds):
    global sleep_calls
    sleep_calls += 1
    if sleep_calls == 1:
        fake.total_rx += 1
        fake.pending.append((0x030, bytes.fromhex("00" * 32), 1))

def attest_aux_reconnect():
    fake.operator_prompt_wait()
    attestation_calls.append(("aux", fake.safety_mode, fake.send_count))
    return probe.AUX_RECONNECTED_TOKEN

def attest_ignition_on():
    fake.operator_prompt_wait()
    attestation_calls.append(("ignition", fake.safety_mode, fake.send_count))
    return probe.IGNITION_ON_TOKEN

def attest_shutdown():
    fake.operator_prompt_wait()
    attestation_calls.append(("shutdown", fake.safety_mode, fake.send_count))
    return probe.SHUTDOWN_TOKEN

mock_result = probe.run_on_panda(
    fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=attest_aux_reconnect,
    ignition_on_confirm_fn=attest_ignition_on,
    shutdown_confirm_fn=attest_shutdown,
    sleep_fn=fake_sleep,
)
send_calls = [call for call in fake.calls if call[0] == "send"]
transition_captures = mock_result["passive_listen"]["transitions"]
check("mocked NOOUTPUT transition phase captures native EPS traffic without host TX", transition_captures[0]["native_frame_count"] == 1 and all(item["tx_count"] == 0 for item in transition_captures))
check("Panda is ACKing in NOOUTPUT before both power transitions", attestation_calls[:2] == [
    ("aux", probe.NOOUTPUT_SAFETY_MODE, 0),
    ("ignition", probe.NOOUTPUT_SAFETY_MODE, 0),
])
check("Panda CAN-health readback uses current kbps units", mock_result["nooutput_armed_while_aux_negative_disconnected"]["can_health"]["can_speed"] == 500 and mock_result["nooutput_armed_while_aux_negative_disconnected"]["can_health"]["can_data_speed"] == 2000)
check("silent TesterPresent tries both formats but never sends F181", mock_result["status"] == "complete" and send_calls == [
    ("send", probe.TX_ADDR, probe.TESTER_PRESENT_FRAME, 1, False),
    ("send", probe.TX_ADDR, probe.TESTER_PRESENT_FRAME, 1, True),
])
check("both silent TesterPresent phases retain clean ACK-consistent assessment", all(phase["assessment"]["verdict"] == "ack-consistent-no-eps-response" for phase in mock_result["phases"]))
check("clean Classical silence is the only silence verdict eligible for FD fallback", mock_result["phases"][0]["assessment"]["fd_fallback_eligible"] and mock_result["phases"][0]["assessment"]["controller_health_clean"])
check("every phase records before/after CAN health", all("can_health_before" in phase and "can_health_after" in phase for phase in mock_result["phases"]))
check("live path never calls the unsupported Panda transceiver API", all(call[0] != "can_enable" for call in fake.calls))
check("live path never issues a force-relay debug request", all(call[0] != "relay" for call in fake.calls))
check("Panda controller loopback is always disabled", all(call[1] is False for call in fake.calls if call[0] == "loopback"))
first_send = fake.calls.index(send_calls[0])
check("NOOUTPUT is established before any transmit call", ("safety", probe.NOOUTPUT_SAFETY_MODE, 0) in fake.calls[:first_send] and ("safety", probe.ELM327_SAFETY_MODE, probe.ELM327_NORMAL_ROUTE_PARAM) in fake.calls[:first_send])
first_nooutput = fake.calls.index(("safety", probe.NOOUTPUT_SAFETY_MODE, 0))
first_heartbeat_disable = next(index for index, call in enumerate(fake.calls) if call[0] == "heartbeat_disabled")
check("heartbeat reset/disable occurs only after NOOUTPUT and survives operator waits", first_nooutput < first_heartbeat_disable and all(call[1] for call in fake.calls if call[0] == "heartbeat_disabled") and all(call[1] for call in fake.calls if call[0] == "operator_wait"))
check("all FD-auto configuration calls explicitly disable it", all(call[2] is False for call in fake.calls if call[0] == "fd_auto"))
check("shutdown is requested only after restoring ACKing NOOUTPUT", attestation_calls[-1] == ("shutdown", probe.NOOUTPUT_SAFETY_MODE, 2))
check("SILENT is entered only after shutdown attestation", ("safety", probe.SILENT_SAFETY_MODE, 0) in fake.calls and mock_result["nooutput_restore"]["errors"] == [] and mock_result["silent_cleanup_errors"] == [])

class AlternatingNoChangePanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.health_read_count = 0

    def can_health(self, bus):
        health = super().can_health(bus)
        self.health_read_count += 1
        if self.health_read_count % 2 == 0:
            health["last_error"] = "NoChange"
            health["last_data_error"] = "NoChange"
        return health

alternating_nochange_fake = AlternatingNoChangePanda()
alternating_nochange_result = probe.run_on_panda(
    alternating_nochange_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("alternating FDCAN NoError/NoChange stays usable through passive and active phases", alternating_nochange_result["status"] == "complete" and alternating_nochange_fake.send_count == 2 and all(capture["evidence_valid"] for capture in alternating_nochange_result["passive_listen"]["transitions"]) and all(phase["assessment"]["controller_health_clean"] for phase in alternating_nochange_result["phases"]))

class IncompleteHealthPanda(FakePanda):
    def can_health(self, bus):
        health = super().can_health(bus)
        del health["can_core_reset_count"]
        return health

incomplete_health_fake = IncompleteHealthPanda()
power_transition_called = False
def forbidden_power_transition():
    global power_transition_called
    power_transition_called = True
    return probe.AUX_RECONNECTED_TOKEN

incomplete_health_result = probe.run_on_panda(
    incomplete_health_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=forbidden_power_transition,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("incomplete CAN-health schema fails before power prompt or TX", incomplete_health_result["status"] == "error" and not power_transition_called and incomplete_health_fake.send_count == 0 and "Panda configuration did not read back" in incomplete_health_result["error"])

class UnhealthyBaselinePanda(FakePanda):
    def can_health(self, bus):
        health = super().can_health(bus)
        health["transmit_error_cnt"] = 1
        health["last_error"] = "AckError"
        return health

unhealthy_baseline_fake = UnhealthyBaselinePanda()
unhealthy_power_transition_called = False
def forbidden_unhealthy_power_transition():
    global unhealthy_power_transition_called
    unhealthy_power_transition_called = True
    return probe.AUX_RECONNECTED_TOKEN

unhealthy_baseline_result = probe.run_on_panda(
    unhealthy_baseline_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=forbidden_unhealthy_power_transition,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("non-clean current CAN health fails before power prompt or TX", unhealthy_baseline_result["status"] == "error" and not unhealthy_power_transition_called and unhealthy_baseline_fake.send_count == 0 and "transmit_error_cnt=1" in unhealthy_baseline_result["error"] and "last_error='AckError'" in unhealthy_baseline_result["error"])

class UnhealthyPandaBaseline(FakePanda):
    def __init__(self):
        super().__init__()
        self.power_save_enabled = True
        self.faults = 4

unhealthy_panda_fake = UnhealthyPandaBaseline()
unhealthy_panda_prompt_called = False
def forbidden_unhealthy_panda_prompt():
    global unhealthy_panda_prompt_called
    unhealthy_panda_prompt_called = True
    return probe.AUX_RECONNECTED_TOKEN

unhealthy_panda_result = probe.run_on_panda(
    unhealthy_panda_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=forbidden_unhealthy_panda_prompt,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("Panda power-save/current faults fail before power prompt or TX", unhealthy_panda_result["status"] == "error" and not unhealthy_panda_prompt_called and unhealthy_panda_fake.send_count == 0 and "power_save_enabled=True" in unhealthy_panda_result["error"] and "faults=4" in unhealthy_panda_result["error"])

class IdentityResponsePanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        if self.send_count == 1:
            self.total_rx += 1
            self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))
        elif self.send_count == 2:
            self.total_rx += 1
            self.pending.append((probe.RX_ADDR, bytes.fromhex("102462f181023839"), bus))

identity_response_fake = IdentityResponsePanda()
identity_response_result = probe.run_on_panda(
    identity_response_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
identity_response_sends = [call for call in identity_response_fake.calls if call[0] == "send"]
check("TesterPresent response is followed by exactly one same-format F181", len(identity_response_sends) == 2 and identity_response_sends[0][4] is False and identity_response_sends[1][2] == probe.F181_FRAME and identity_response_sends[1][4] is False)
check("native F181 FirstFrame stops every later format trial", identity_response_result["host_submission_count"] == 2 and "f181-classical" in identity_response_result["stopped_early"])
check("8-byte phase assessment records prefix only and never authorizes restore", identity_response_result["phases"][1]["assessment"]["f181_identity_classification"] == "application-prefix" and identity_response_result["phases"][1]["assessment"]["f181_identity_scope"] == "prefix" and not identity_response_result["phases"][1]["assessment"]["restore_authorized"])
check("result never invents a wire-attempt count", identity_response_result["wire_attempt_count"].startswith("not observable") and identity_response_result["phases"][0]["wire_attempts"].startswith("unknown"))

class TesterPositiveF181SilentPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        if self.send_count == 1:
            self.total_rx += 1
            self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

tester_positive_fake = TesterPositiveF181SilentPanda()
tester_positive_result = probe.run_on_panda(
    tester_positive_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
tester_positive_sends = [call for call in tester_positive_fake.calls if call[0] == "send"]
check("positive TesterPresent gets one same-format F181 then stops even when F181 is silent", len(tester_positive_sends) == 2 and tester_positive_result["host_submission_count"] == 2 and "one F181 follow-up" in tester_positive_result["stopped_early"])

class FdFallbackResponsePanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        if self.send_count == 2:
            self.total_rx += 1
            self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))
        elif self.send_count == 3:
            self.total_rx += 1
            self.pending.append((probe.RX_ADDR, bytes.fromhex("102462f181022121"), bus))

fd_fallback_fake = FdFallbackResponsePanda()
fd_fallback_result = probe.run_on_panda(
    fd_fallback_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
fd_fallback_sends = [call for call in fd_fallback_fake.calls if call[0] == "send"]
check("silent Classical TP falls back to FD TP and only then gated FD F181", fd_fallback_sends == [
    ("send", probe.TX_ADDR, probe.TESTER_PRESENT_FRAME, 1, False),
    ("send", probe.TX_ADDR, probe.TESTER_PRESENT_FRAME, 1, True),
    ("send", probe.TX_ADDR, probe.F181_FRAME, 1, True),
])
check("FD F181 FirstFrame records boot prefix only", fd_fallback_result["phases"][-1]["assessment"]["f181_identity_classification"] == "boot-prefix" and fd_fallback_result["phases"][-1]["assessment"]["f181_identity_scope"] == "prefix")

class NegativeTesterPresentPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("037f3e1100000000"), bus))

negative_tp_fake = NegativeTesterPresentPanda()
negative_tp_result = probe.run_on_panda(
    negative_tp_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("validated negative TesterPresent proves DCM but stops without F181", negative_tp_result["host_submission_count"] == 1 and negative_tp_result["phases"][0]["assessment"]["diagnostic_response_kinds"] == ["tester-present-negative"] and "F181 not sent" in negative_tp_result["stopped_early"])

class Unmatched7A9Panda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("0123000000000000"), bus))

unmatched_7a9_fake = Unmatched7A9Panda()
unmatched_7a9_result = probe.run_on_panda(
    unmatched_7a9_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
unmatched_7a9_sends = [call for call in unmatched_7a9_fake.calls if call[0] == "send"]
check("clean unmatched native 0x7A9 permits only FD TP fallback, never F181", len(unmatched_7a9_sends) == 2 and all(call[2] == probe.TESTER_PRESENT_FRAME for call in unmatched_7a9_sends) and all(phase["assessment"]["matched_diagnostic_response_count"] == 0 for phase in unmatched_7a9_result["phases"]) and unmatched_7a9_result["phases"][0]["assessment"]["fd_fallback_eligible"])

class HostRejectedPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.pending.append((address, bytes(data), bus + 192))

host_rejected_fake = HostRejectedPanda()
host_rejected_result = probe.run_on_panda(
    host_rejected_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("host rejection stops before FD fallback", host_rejected_fake.send_count == 1 and host_rejected_result["phases"][0]["assessment"]["verdict"] == "host-safety-rejected" and not host_rejected_result["phases"][0]["assessment"]["fd_fallback_eligible"])

class PositiveWithHostRejectionPanda(HostRejectedPanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

positive_rejected_fake = PositiveWithHostRejectionPanda()
positive_rejected_result = probe.run_on_panda(
    positive_rejected_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
positive_rejected_assessment = positive_rejected_result["phases"][0]["assessment"]
check("matched positive TP plus host rejection never permits F181", positive_rejected_fake.send_count == 1 and positive_rejected_assessment["diagnostic_response_kinds"] == ["tester-present-positive"] and positive_rejected_assessment["verdict"] == "host-safety-rejected" and not positive_rejected_assessment["phase_evidence_valid"])

class NoTxReceiptPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        self.calls.append(("send", address, bytes(data), bus, fd))
        self.send_count += 1
        self.total_tx += 1

no_receipt_fake = NoTxReceiptPanda()
no_receipt_result = probe.run_on_panda(
    no_receipt_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("missing TX receipt stops before FD fallback", no_receipt_fake.send_count == 1 and no_receipt_result["phases"][0]["assessment"]["verdict"] == "no-tx-receipt" and not no_receipt_result["phases"][0]["assessment"]["fd_fallback_eligible"])

class PositiveNoTxReceiptPanda(NoTxReceiptPanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

positive_no_receipt_fake = PositiveNoTxReceiptPanda()
positive_no_receipt_result = probe.run_on_panda(
    positive_no_receipt_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
positive_no_receipt_assessment = positive_no_receipt_result["phases"][0]["assessment"]
check("matched positive TP without host TX receipt never permits F181", positive_no_receipt_fake.send_count == 1 and positive_no_receipt_assessment["diagnostic_response_kinds"] == ["tester-present-positive"] and positive_no_receipt_assessment["verdict"] == "matched-eps-diagnostic-response" and not positive_no_receipt_assessment["phase_evidence_valid"])

class WrongEchoPositivePanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.pending[-1] = (address, probe.F181_FRAME, bus + 128)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

wrong_echo_positive_fake = WrongEchoPositivePanda()
wrong_echo_positive_result = probe.run_on_panda(
    wrong_echo_positive_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("matched positive TP plus wrong echo stops before F181", wrong_echo_positive_fake.send_count == 1 and not wrong_echo_positive_result["phases"][0]["assessment"]["host_tx_receipt_confirmed"] and "F181 not sent" in wrong_echo_positive_result["stopped_early"])

class OtherSourcePositivePanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))
        self.pending.append((0x123, b"\x01", 0))

other_source_positive_fake = OtherSourcePositivePanda()
other_source_positive_result = probe.run_on_panda(
    other_source_positive_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("coexisting exact TP/echo plus other source stops before F181", other_source_positive_fake.send_count == 1 and other_source_positive_result["phases"][0]["assessment"]["verdict"] == "unexpected-source-topology-contamination" and not other_source_positive_result["phases"][0]["assessment"]["phase_evidence_valid"])

class ExtraTxCountPositivePanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_tx += 1
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

extra_tx_positive_fake = ExtraTxCountPositivePanda()
extra_tx_positive_result = probe.run_on_panda(
    extra_tx_positive_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("matched positive TP plus total_tx delta two stops before F181", extra_tx_positive_fake.send_count == 1 and extra_tx_positive_result["phases"][0]["assessment"]["can_health_delta_mod32"]["total_tx_cnt"] == 2 and not extra_tx_positive_result["phases"][0]["assessment"]["phase_evidence_valid"])

class ZeroTxCountPositivePanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_tx -= 1
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

zero_tx_positive_fake = ZeroTxCountPositivePanda()
zero_tx_positive_result = probe.run_on_panda(
    zero_tx_positive_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("matched positive TP plus total_tx delta zero stops before F181", zero_tx_positive_fake.send_count == 1 and zero_tx_positive_result["phases"][0]["assessment"]["can_health_delta_mod32"]["total_tx_cnt"] == 0 and not zero_tx_positive_result["phases"][0]["assessment"]["phase_evidence_valid"])

class QueuedHealthIndeterminatePanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_tx -= 1

queued_indeterminate_fake = QueuedHealthIndeterminatePanda()
queued_indeterminate_result = probe.run_on_panda(
    queued_indeterminate_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("queued but indeterminate TX stops before FD fallback", queued_indeterminate_fake.send_count == 1 and queued_indeterminate_result["phases"][0]["assessment"]["verdict"] == "tx-queued-health-indeterminate" and not queued_indeterminate_result["phases"][0]["assessment"]["fd_fallback_eligible"])

class AckFaultPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_error += 1
        self.core_resets += 1
        self.error = "AckError"

ack_fault_fake = AckFaultPanda()
ack_fault_result = probe.run_on_panda(
    ack_fault_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("AckError/core reset stops before FD fallback", ack_fault_fake.send_count == 1 and ack_fault_result["phases"][0]["assessment"]["verdict"] == "ack-error-or-link-fault" and not ack_fault_result["phases"][0]["assessment"]["controller_health_clean"])

class ControllerFaultPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_error += 1
        self.total_tx_lost += 1
        self.error = "Form error"

controller_fault_fake = ControllerFaultPanda()
controller_fault_result = probe.run_on_panda(
    controller_fault_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("non-ACK controller/link fault stops before FD fallback", controller_fault_fake.send_count == 1 and controller_fault_result["phases"][0]["assessment"]["verdict"] == "can-controller-error-or-link-fault" and not controller_fault_result["phases"][0]["assessment"]["fd_fallback_eligible"])

class PositiveWithAckFaultPanda(AckFaultPanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

positive_fault_fake = PositiveWithAckFaultPanda()
positive_fault_result = probe.run_on_panda(
    positive_fault_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
positive_fault_assessment = positive_fault_result["phases"][0]["assessment"]
check("matched positive TP plus controller fault never permits F181", positive_fault_fake.send_count == 1 and positive_fault_assessment["diagnostic_response_kinds"] == ["tester-present-positive"] and positive_fault_assessment["verdict"] == "ack-error-or-link-fault" and not positive_fault_assessment["controller_health_clean"])

class PositiveWithIncompleteHealthPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.phase_sent = False

    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.phase_sent = True
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

    def can_health(self, bus):
        health = super().can_health(bus)
        if self.phase_sent:
            del health["transmit_error_cnt"]
        return health

positive_incomplete_fake = PositiveWithIncompleteHealthPanda()
positive_incomplete_result = probe.run_on_panda(
    positive_incomplete_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
positive_incomplete_assessment = positive_incomplete_result["phases"][0]["assessment"]
check("matched positive TP plus incomplete health never permits F181", positive_incomplete_fake.send_count == 1 and positive_incomplete_assessment["diagnostic_response_kinds"] == ["tester-present-positive"] and positive_incomplete_assessment["verdict"] == "can-health-incomplete" and not positive_incomplete_assessment["controller_health_clean"])

class ActiveRxLossPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx_lost += 1

active_rx_loss_fake = ActiveRxLossPanda()
active_rx_loss_result = probe.run_on_panda(
    active_rx_loss_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("active controller RX loss invalidates phase and stops later TX", active_rx_loss_fake.send_count == 1 and active_rx_loss_result["phases"][0]["assessment"]["verdict"] == "can-rx-evidence-loss-or-overflow" and not active_rx_loss_result["phases"][0]["assessment"]["phase_evidence_valid"])

class ActiveRxOverflowPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.rx_buffer_overflow += 1

active_overflow_fake = ActiveRxOverflowPanda()
active_overflow_result = probe.run_on_panda(
    active_overflow_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("active Panda RX overflow invalidates phase and stops later TX", active_overflow_fake.send_count == 1 and active_overflow_result["phases"][0]["assessment"]["verdict"] == "can-rx-evidence-loss-or-overflow" and active_overflow_result["phases"][0]["assessment"]["panda_rx_buffer_overflow_delta_mod32"] == 1)

class PostDrainOverflowPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.injected = False

    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

    def can_recv(self):
        rows = super().can_recv()
        if self.send_count and not self.injected:
            self.injected = True
            self.rx_buffer_overflow += 1
        return rows

post_drain_overflow_fake = PostDrainOverflowPanda()
post_drain_overflow_result = probe.run_on_panda(
    post_drain_overflow_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("RX overflow occurring during USB drain is in final health and blocks F181", post_drain_overflow_fake.send_count == 1 and post_drain_overflow_result["phases"][0]["assessment"]["verdict"] == "can-rx-evidence-loss-or-overflow" and post_drain_overflow_result["phases"][0]["assessment"]["panda_rx_buffer_overflow_delta_mod32"] == 1)

class PostDrainPandaFaultPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.injected = False

    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

    def can_recv(self):
        rows = super().can_recv()
        if self.send_count and not self.injected:
            self.injected = True
            self.safety_param = 9
            self.heartbeat_lost = True
            self.power_save_enabled = True
            self.faults = 1
            self.car_harness_status = 1
            self.safety_tx_blocked += 1
            self.safety_rx_invalid += 1
            self.tx_buffer_overflow += 1
            self.uptime = 1
        return rows

post_drain_panda_fault_fake = PostDrainPandaFaultPanda()
post_drain_panda_fault_result = probe.run_on_panda(
    post_drain_panda_fault_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
post_drain_panda_assessment = post_drain_panda_fault_result["phases"][0]["assessment"]
check("post-drain Panda mode/heartbeat/power/fault/counter/uptime/harness drift blocks F181", post_drain_panda_fault_fake.send_count == 1 and post_drain_panda_assessment["verdict"] == "panda-health-fault-or-drift" and not post_drain_panda_assessment["panda_health_clean"] and post_drain_panda_assessment["panda_uptime_reset"] and any("car_harness_status" in issue for issue in post_drain_panda_assessment["panda_runtime_issues"]) and all(post_drain_panda_assessment["panda_health_delta_mod32"][field] == 1 for field in ("safety_tx_blocked", "safety_rx_invalid", "tx_buffer_overflow")))

class PostDrainCanDriftPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.injected = False

    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((probe.RX_ADDR, bytes.fromhex("027e000000000000"), bus))

    def can_recv(self):
        rows = super().can_recv()
        if self.send_count and not self.injected:
            self.injected = True
            self.receive_error = 1
            self.total_fwd += 1
            self.speed = 2500
        return rows

post_drain_can_drift_fake = PostDrainCanDriftPanda()
post_drain_can_drift_result = probe.run_on_panda(
    post_drain_can_drift_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
post_drain_can_assessment = post_drain_can_drift_result["phases"][0]["assessment"]
check("post-drain REC/config/forwarding drift blocks F181", post_drain_can_drift_fake.send_count == 1 and post_drain_can_assessment["verdict"] == "can-configuration-or-receive-health-drift" and not post_drain_can_assessment["controller_health_clean"] and post_drain_can_assessment["can_health_delta_mod32"]["total_fwd_cnt"] == 1)

class ChunkedDrainPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        for index in range(5):
            self.total_rx += 1
            self.pending.append((0x500 + index, bytes([index]), bus))

    def can_recv(self):
        rows = self.pending[:2]
        self.pending = self.pending[2:]
        return rows

chunked_drain_fake = ChunkedDrainPanda()
chunked_drain_phase = probe._run_tx_phase(
    chunked_drain_fake,
    bus=1,
    phase=probe.TX_PHASES[0],
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    sleep_fn=lambda _seconds: None,
)
check("active drain loops until all native rows reconcile to total_rx count", chunked_drain_phase["drain"]["complete"] and chunked_drain_phase["drain"]["drain_calls"] == 3 and chunked_drain_phase["drain"]["expected_native_rx_count_mod32"] == 5 and chunked_drain_phase["drain"]["observed_native_rx_count"] == 5)

class LateNativeDrainPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.injected_late = False

    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 1
        self.pending.append((0x550, b"\x01", bus))

    def can_recv(self):
        rows = super().can_recv()
        if not self.injected_late:
            self.injected_late = True
            self.total_rx += 1
            self.pending.append((0x551, b"\x02", 1))
        return rows

late_native_fake = LateNativeDrainPanda()
late_native_phase = probe._run_tx_phase(
    late_native_fake,
    bus=1,
    phase=probe.TX_PHASES[0],
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    sleep_fn=lambda _seconds: None,
)
check("active drain notices and reconciles native traffic arriving during USB read", late_native_phase["drain"]["complete"] and late_native_phase["drain"]["drain_calls"] == 2 and late_native_phase["drain"]["observed_native_rx_count"] == 2)

class UnreconciledDrainPanda(FakePanda):
    def can_send(self, address, data, bus, *, fd=False):
        super().can_send(address, data, bus, fd=fd)
        self.total_rx += 2
        self.pending.append((0x560, b"\x01", bus))

unreconciled_drain_fake = UnreconciledDrainPanda()
unreconciled_drain_phase = probe._run_tx_phase(
    unreconciled_drain_fake,
    bus=1,
    phase=probe.TX_PHASES[0],
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    sleep_fn=lambda _seconds: None,
)
check("unreconciled final native RX count fails phase evidence closed", not unreconciled_drain_phase["drain"]["complete"] and unreconciled_drain_phase["assessment"]["verdict"] == "native-rx-evidence-unreconciled" and not unreconciled_drain_phase["assessment"]["phase_evidence_valid"])

passive_rx_loss_fake = FakePanda()
passive_rx_loss_sleep_count = 0
def passive_rx_loss_sleep(_seconds):
    global passive_rx_loss_sleep_count
    passive_rx_loss_sleep_count += 1
    if passive_rx_loss_sleep_count == 1:
        passive_rx_loss_fake.total_rx_lost += 1

passive_rx_loss_result = probe.run_on_panda(
    passive_rx_loss_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=passive_rx_loss_sleep,
)
passive_rx_loss_capture = passive_rx_loss_result["passive_listen"]["transitions"][0]
check("passive controller RX loss is recorded and aborts before active TX", passive_rx_loss_result["status"] == "error" and passive_rx_loss_fake.send_count == 0 and not passive_rx_loss_capture["evidence_valid"] and "CAN controller RX loss increased" in passive_rx_loss_capture["evidence_loss_reasons"])

passive_overflow_fake = FakePanda()
passive_overflow_sleep_count = 0
def passive_overflow_sleep(_seconds):
    global passive_overflow_sleep_count
    passive_overflow_sleep_count += 1
    if passive_overflow_sleep_count == 1:
        passive_overflow_fake.rx_buffer_overflow += 1

passive_overflow_result = probe.run_on_panda(
    passive_overflow_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=passive_overflow_sleep,
)
passive_overflow_capture = passive_overflow_result["passive_listen"]["transitions"][0]
check("passive Panda RX overflow is recorded and aborts before active TX", passive_overflow_result["status"] == "error" and passive_overflow_fake.send_count == 0 and not passive_overflow_capture["evidence_valid"] and passive_overflow_capture["panda_rx_buffer_overflow_delta_mod32"] == 1)

class PassiveTransitionFaultPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.transition_faulted = False
        self.heartbeat_lost = False

    def health(self):
        health = super().health()
        health["heartbeat_lost"] = self.heartbeat_lost
        return health

    def can_health(self, bus):
        health = super().can_health(bus)
        if self.transition_faulted:
            health["bus_off"] = True
            health["error_warning"] = True
            health["error_passive"] = True
            health["transmit_error_cnt"] = 128
        return health

passive_fault_fake = PassiveTransitionFaultPanda()
passive_fault_sleep_count = 0
def passive_fault_sleep(_seconds):
    global passive_fault_sleep_count
    passive_fault_sleep_count += 1
    if passive_fault_sleep_count == 1:
        passive_fault_fake.transition_faulted = True
        passive_fault_fake.heartbeat_lost = True
        passive_fault_fake.power_save_enabled = True
        passive_fault_fake.faults = 2
        passive_fault_fake.safety_tx_blocked += 1
        passive_fault_fake.safety_rx_invalid += 1
        passive_fault_fake.tx_buffer_overflow += 1
        passive_fault_fake.uptime = 1
        passive_fault_fake.total_tx += 1
        passive_fault_fake.total_tx_lost += 1
        passive_fault_fake.total_tx_checksum_error += 1
        passive_fault_fake.total_error += 1
        passive_fault_fake.core_resets += 1
        passive_fault_fake.total_fwd += 1
        passive_fault_fake.receive_error = 1
        passive_fault_fake.speed = 2500
        passive_fault_fake.error = "AckError"

passive_fault_result = probe.run_on_panda(
    passive_fault_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=passive_fault_sleep,
)
passive_fault_capture = passive_fault_result["passive_listen"]["transitions"][0]
check("passive NOOUTPUT Panda/CAN/config/link faults invalidate capture and abort TX", passive_fault_fake.send_count == 0 and not passive_fault_capture["evidence_valid"] and any("total_tx_cnt" in reason for reason in passive_fault_capture["evidence_loss_reasons"]) and any("core_reset" in reason for reason in passive_fault_capture["evidence_loss_reasons"]) and any("transmit error counter" in reason for reason in passive_fault_capture["evidence_loss_reasons"]) and any("heartbeat" in reason for reason in passive_fault_capture["evidence_loss_reasons"]) and any("power_save" in reason for reason in passive_fault_capture["evidence_loss_reasons"]) and any("receive_error_cnt" in reason for reason in passive_fault_capture["evidence_loss_reasons"]) and passive_fault_capture["panda_uptime_reset"])

passive_receipt_fake = FakePanda()
passive_receipt_sleep_count = 0
def passive_receipt_sleep(_seconds):
    global passive_receipt_sleep_count
    passive_receipt_sleep_count += 1
    if passive_receipt_sleep_count == 1:
        passive_receipt_fake.total_rx += 1
        passive_receipt_fake.pending.append((probe.TX_ADDR, probe.TESTER_PRESENT_FRAME, 129))

passive_receipt_result = probe.run_on_panda(
    passive_receipt_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=passive_receipt_sleep,
)
passive_receipt_capture = passive_receipt_result["passive_listen"]["transitions"][0]
check("unexpected host receipt contaminates passive capture and aborts TX", passive_receipt_fake.send_count == 0 and passive_receipt_capture["contaminated_by_host_receipt"] and not passive_receipt_capture["evidence_valid"] and "unexpected host TX receipt during NOOUTPUT capture" in passive_receipt_capture["evidence_loss_reasons"])

passive_other_source_fake = FakePanda()
passive_other_source_sleep_count = 0
def passive_other_source_sleep(_seconds):
    global passive_other_source_sleep_count
    passive_other_source_sleep_count += 1
    if passive_other_source_sleep_count == 1:
        passive_other_source_fake.total_rx += 1
        passive_other_source_fake.pending.append((0x222, b"\x01", 1))
        passive_other_source_fake.pending.append((0x123, b"\x02", 128))

passive_other_source_result = probe.run_on_panda(
    passive_other_source_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=passive_other_source_sleep,
)
passive_other_source_capture = passive_other_source_result["passive_listen"]["transitions"][0]
check("other-source frame invalidates passive standalone-CAN1 evidence", passive_other_source_fake.send_count == 0 and not passive_other_source_capture["evidence_valid"] and passive_other_source_capture["frames"]["other_source"] and any("other-source" in reason for reason in passive_other_source_capture["evidence_loss_reasons"]))

passive_safety_drift_fake = FakePanda()
passive_safety_drift_sleep_count = 0
def passive_safety_drift_sleep(_seconds):
    global passive_safety_drift_sleep_count
    passive_safety_drift_sleep_count += 1
    if passive_safety_drift_sleep_count == 1:
        passive_safety_drift_fake.safety_mode = probe.SILENT_SAFETY_MODE
        passive_safety_drift_fake.safety_param = 7

passive_safety_drift_result = probe.run_on_panda(
    passive_safety_drift_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=passive_safety_drift_sleep,
)
passive_safety_drift_capture = passive_safety_drift_result["passive_listen"]["transitions"][0]
check("post-capture Panda safety drift invalidates passive evidence", passive_safety_drift_fake.send_count == 0 and not passive_safety_drift_capture["evidence_valid"] and any("safety_mode" in reason for reason in passive_safety_drift_capture["evidence_loss_reasons"]) and any("safety_param" in reason for reason in passive_safety_drift_capture["evidence_loss_reasons"]))

unconfirmed_shutdown_fake = FakePanda()
unconfirmed_shutdown_result = probe.run_on_panda(
    unconfirmed_shutdown_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: "wrong",
    sleep_fn=lambda _seconds: None,
)
check("failed shutdown attestation leaves best-effort ACKing NOOUTPUT and returns error", unconfirmed_shutdown_result["status"] == "error" and unconfirmed_shutdown_fake.safety_mode == probe.NOOUTPUT_SAFETY_MODE and not any(call == ("safety", probe.SILENT_SAFETY_MODE, 0) for call in unconfirmed_shutdown_fake.calls) and "urgent_shutdown_instruction" in unconfirmed_shutdown_result)

class CleanupInterruptPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.nooutput_attempts = 0
        self.silent_attempts = 0

    def set_safety_mode(self, mode, param=0):
        if mode == probe.NOOUTPUT_SAFETY_MODE:
            self.nooutput_attempts += 1
            if self.nooutput_attempts == 2:
                self.calls.append(("safety_interrupt", mode))
                raise KeyboardInterrupt
        if mode == probe.SILENT_SAFETY_MODE:
            self.silent_attempts += 1
            if self.silent_attempts == 1:
                self.calls.append(("safety_interrupt", mode))
                raise KeyboardInterrupt
        super().set_safety_mode(mode, param)

cleanup_interrupt_fake = CleanupInterruptPanda()
cleanup_interrupt_shutdown_called = False
def cleanup_interrupt_shutdown():
    global cleanup_interrupt_shutdown_called
    cleanup_interrupt_shutdown_called = True
    return probe.SHUTDOWN_TOKEN

cleanup_interrupt_result = probe.run_on_panda(
    cleanup_interrupt_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=cleanup_interrupt_shutdown,
    sleep_fn=lambda _seconds: None,
)
check("second Ctrl+C during NOOUTPUT cleanup cannot skip later actions/readback/shutdown", cleanup_interrupt_shutdown_called and cleanup_interrupt_result["nooutput_restore"]["panda_health"]["safety_mode"] == probe.NOOUTPUT_SAFETY_MODE and any("KeyboardInterrupt" in error for error in cleanup_interrupt_result["nooutput_restore"]["errors"]) and cleanup_interrupt_fake.nooutput_attempts >= 3)
check("second Ctrl+C during SILENT cleanup is caught and SILENT is retried", cleanup_interrupt_fake.safety_mode == probe.SILENT_SAFETY_MODE and cleanup_interrupt_fake.silent_attempts >= 2 and any("KeyboardInterrupt" in error for error in cleanup_interrupt_result["silent_cleanup_errors"]))

class SilentReadbackFailurePanda(FakePanda):
    def set_safety_mode(self, mode, param=0):
        if mode == probe.SILENT_SAFETY_MODE:
            self.calls.append(("ignored_silent", mode, param))
            return
        super().set_safety_mode(mode, param)

silent_readback_fake = SilentReadbackFailurePanda()
silent_readback_result = probe.run_on_panda(
    silent_readback_fake,
    bus=1,
    passive_seconds=probe.DEFAULT_PASSIVE_SECONDS,
    settle_seconds=probe.DEFAULT_SETTLE_SECONDS,
    aux_reconnect_confirm_fn=lambda: probe.AUX_RECONNECTED_TOKEN,
    ignition_on_confirm_fn=lambda: probe.IGNITION_ON_TOKEN,
    shutdown_confirm_fn=lambda: probe.SHUTDOWN_TOKEN,
    sleep_fn=lambda _seconds: None,
)
check("unverified SILENT readback returns error and keeps power/A30-disconnect instruction", silent_readback_result["status"] == "error" and any("verify SILENT cleanup" in error for error in silent_readback_result["silent_cleanup_errors"]) and "urgent_cleanup_instruction" in silent_readback_result and "auxiliary-battery negative disconnected" in silent_readback_result["urgent_cleanup_instruction"])


print("\n== CLI remains dry-run and pre-hardware fail-closed ==")
script = REPO / "tools/toyota"
dry = subprocess.run(
    [str(script), "eps-isolated-probe"], cwd=REPO, capture_output=True, text=True, check=False,
)
check("default CLI dry-run succeeds without Panda", dry.returncode == 0, dry.stderr.strip())
dry_output = json.loads(dry.stdout)
check("default CLI does not execute hardware", dry_output["mode"] == "dry-run" and "result" not in dry_output)

missing = subprocess.run(
    [str(script), "eps-isolated-probe", "--execute"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("execute without attestations fails before Panda import", missing.returncode != 0 and "live execution preflight failed" in missing.stderr and "cannot import panda" not in missing.stderr)

full_non_tty = subprocess.run(
    [
        str(script), "eps-isolated-probe", "--execute",
        "--arm", probe.ARM_TOKEN,
        "--confirm-a30-disconnected",
        "--confirm-a30-mating-connector-correct-terminals-no-backprobe-no-piercing-no-generic-pin",
        "--confirm-stationary", "--confirm-parking-brake-set", "--confirm-level-ground",
        "--confirm-wheel-chocks", "--confirm-foot-off-brake",
        "--confirm-probe-will-use-ignition-on-not-ready", "--confirm-ignition-off-now",
        "--confirm-auxiliary-battery-negative-disconnected-now",
        "--confirm-usb-host-battery-powered-not-vehicle-or-mains", "--confirm-rack-only-peer",
        "--confirm-common-ground", "--confirm-dc1h-dc1l-polarity",
        "--confirm-resistance-measured-power-off",
        "--confirm-battery-negative-was-disconnected-for-isolation-checks",
        "--confirm-meter-removed", "--confirm-external-can1-120-ohm-termination",
        "--confirm-unused-can1-pass-through-unconnected", "--confirm-only-can1-connected",
        "--confirm-openpilot-stopped", "--rack-only-ohms", "120", "--complete-bus-ohms", "60",
        "--dc1h-to-ground-ohms", "1000", "--dc1l-to-ground-ohms", "1000",
        "--dc1h-to-aux-positive-ohms", "10000", "--dc1l-to-aux-positive-ohms", "10000",
    ],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("fully attested execute still requires a real TTY before Panda import", full_non_tty.returncode != 0 and "real interactive" in full_non_tty.stderr and "cannot import panda" not in full_non_tty.stderr)

caps = subprocess.run(
    [str(script), "capabilities"], cwd=REPO, capture_output=True, text=True, check=False,
)
check("Toyota capability surface advertises isolated probe", caps.returncode == 0 and "eps-isolated-probe" in json.loads(caps.stdout))

source = (REPO / "tools/toyota_support/toyota_eps_isolated_can_probe.py").read_text(encoding="utf-8")
check("implementation has exactly one CAN transmit call site", source.count("panda.can_send(") == 1)
check("hard allowlist directly guards sole transmit call", source.index("assert_allowed_tx(TX_ADDR, phase.data, phase.fd)") < source.index("panda.can_send(TX_ADDR, phase.data, bus, fd=phase.fd)"))
check("implementation avoids unsupported transceiver and debug-relay APIs", "set_can_enable(" not in source and "force_relay_drive(" not in source)
check("live discovery is restricted to a directly connected USB Panda", "Panda.list(usb_only=True)" in source and "panda.is_connected_usb()" in source)
check("implementation never instantiates a high-level UDS client", "UdsClient" not in source and "_import_uds" not in source)


print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
