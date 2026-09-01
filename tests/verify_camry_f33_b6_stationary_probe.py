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
check("only exact acceptance-ladder cells are exposed", [c.address for c in probe.LADDER_CELLS] == [
    0xFEBE5364, 0xFEBE80C8, 0xFEBE80C9, 0xFEBEF13E, 0xFEBEADB9,
    0xFEBEADB0, 0xFEBEAE90, 0xFEBECAFF, 0xFEBEACBD, 0xFEBECB00,
])
check("all ladder cells validate under existing SID23 RMBA policy", all(probe.validate_read(probe.RAM_ID, c.address, c.length) is None for c in probe.LADDER_CELLS))
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

print("\n== acceptance discriminator ==")
target = probe.angle_deg_to_raw(3.0)
good = {
    "publication_generation": 7, "consumed_generation": 7,
    "unpacker_status": 0, "staged_status": 0, "snapshot_status": 0,
    "target_lateral_id": 11, "target_angle_raw": target,
    "b6_controller_enable": 1, "global_comm_mode": 0, "controller_bank": 2,
}
check("positive ladder is ADMITTED", probe.verdict(good, target_id=11, target_raw=target) == {
    "admitted": True, "reason": "ADMITTED", "status_healthy": True,
    "payload_delivered": True, "controller_enabled": True, "bank_selected": True,
})
check("payload mismatch is classified before downstream gates", probe.verdict(dict(good, target_lateral_id=0), target_id=11, target_raw=target)["reason"] == "payload_not_delivered")
check("unhealthy receive status is classified", probe.verdict(dict(good, snapshot_status=0x11), target_id=11, target_raw=target)["reason"] == "receive_status_unhealthy")
check("CAFF failure is classified", probe.verdict(dict(good, b6_controller_enable=0), target_id=11, target_raw=target)["reason"] == "b6_controller_not_enabled")
check("ACBD failure is classified", probe.verdict(dict(good, global_comm_mode=1), target_id=11, target_raw=target)["reason"] == "global_comm_mode_blocks_controller")
check("ID11 bank failure is classified", probe.verdict(dict(good, controller_bank=7), target_id=11, target_raw=target)["reason"] == "id11_bank_not_selected")

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
    check("kit manifest is self-contained v2 and binds exact route", manifest["schema"] == "camry-f33-car-kit-v2" and manifest["target"] == {
        "eps_f181": "8965F3307000", "eps_diag": "0x7A1->0x7A9 bus0", "b6": "0x0B6/32 FD bus0",
    })
    check("kit pins cumulative two-stage firmware state", manifest["firmware_patch"]["stage1_installed"] == {
        "address": "0x8F952", "bytes": "e001", "fixup": "0xD9AF33AF",
    } and manifest["firmware_patch"]["stage2_candidate"] == {
        "address": "0x8F948", "bytes": "003a", "final_fixup": "0xD12ADB05",
    })
    check("kit carries exact stage1 source and final SHA", manifest["firmware_patch"]["source_image_sha256"] == builder.stage2.EXPECTED_STAGE1_SHA256 and manifest["firmware_patch"]["final_image_sha256"] == builder.stage2.EXPECTED_FINAL_SHA256)
    check("kit includes preflight/apply/restore/post-apply artifacts", all((out / rel).is_file() for rel in (
        "firmware_patch/payload-validate-only.bin", "firmware_patch/payload-apply.bin",
        "firmware_patch/restore/restore.json", "firmware_patch/post-apply/payload-validate-only.bin",
        "firmware_patch/generic_shellcode_template.bin",
    )))
    check("kit includes patch runtime needed on comma", all((out / rel).is_file() for rel in (
        "runtime/exploit/common/ram_exec.py", "runtime/exploit/common/payload_package.py",
        "runtime/exploit/patcher/deploy.py", "runtime/exploit/patcher/restore.py",
        "runtime/exploit/patcher/post_apply_verify.py", "runtime/tools/build_secoc_patch_manifest.py",
    )))
    check("kit never materializes standalone secret files", not any("secret" in p.name.lower() for p in out.rglob("*")))
    check("patch runbook requires zero-write preflight before apply", "Zero-write preflight" in patch_runbook and "If `apply_ready` is not exactly true, **do not APPLY**" in patch_runbook)
    check("patch runbook pins cumulative CRC and both patch sites", "0x8F948: 1A 38 -> 00 3A" in patch_runbook and "0x8F952 = E001" in patch_runbook and "D12ADB05" in patch_runbook and "both" in patch_runbook)
    check("patch runbook includes post-power-cycle verify and stage2-only restore", "OFF -> READY" in patch_runbook and "post_apply_verify.py" in patch_runbook and "RESTORE reverses **stage 2 only**" in patch_runbook)
    check("kit manifest pins current opendbc and Panda revisions", len(manifest["repositories"]["opendbc"].get("head", "")) == 40 and len(manifest["repositories"]["panda"].get("head", "")) == 40)
    check("runbook orders stage2 proof before B6 admission and admitted-only offset", "First follow `FIRMWARE_PATCH.md`" in runbook and "First B6 run after stage-2 persistence proof: admission only" in runbook and "--small-offset-deg 0.5" in runbook and "If it is not ADMITTED, stop there" in runbook)
    check("runbook states the bounded steering ramp", "rate-limits" in runbook and "6 deg/s" in runbook)
    check("runbook pins current bus0 and exclusive Panda ownership", "current post-repin" in runbook and "Panda bus 0" in runbook and "pandad|boardd" in runbook)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
