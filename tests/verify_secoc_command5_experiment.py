#!/usr/bin/env python3
"""Verify the bounded application-context selector-4 command-5 experiment."""

from __future__ import annotations

import copy
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.command5.build_experiment import (
    EXPECTED_RESIDUE,
    FCU_BLOCK_SIZE,
    MUTATIONS,
    TARGET_BLOCK_BASE,
    ExperimentBuildError,
    build_plan,
)
from exploit.command5.stimulus import (
    COMMAND5_MODE,
    COMMAND5_SELECTOR,
    CONTROL_STATUS_ABSENT,
    CONTROL_STATUS_FAILED,
    CONTROL_STATUS_INCOMPATIBLE,
    CONTROL_STATUS_POSITIVE,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_ROUNDS,
    LIVE_RESULT_SCHEMA,
    ROLE_CONTROL,
    ROLE_EXPERIMENT,
    ROLES,
    StimulusError,
    build_input_frames,
    build_stimulus_plan,
    build_verdict,
    classify_dtc_change,
    command5_elm327_param,
    latency_statistics,
    load_control_artifact,
    observation_interval_statistics,
    observation_rtt_statistics,
    parse_bank1_activation_response,
    parse_control_type3_response,
)
from tools.build_secoc_patch_manifest import crc32, discover_crc_descriptors

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


firmware_path = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
firmware = firmware_path.read_bytes()

print("== bounded instruction mutations ==")
check("experiment uses two observation-only instruction mutations", len(MUTATIONS) == 2)
check("all experiment mutations fit one 32 KiB FCU block", all(TARGET_BLOCK_BASE <= m.address and m.address + len(m.original) <= TARGET_BLOCK_BASE + FCU_BLOCK_SIZE for m in MUTATIONS))
check("total changed instruction bytes is 6", sum(len(m.original) for m in MUTATIONS) == 6)
for mutation in MUTATIONS:
    observed = firmware[mutation.address:mutation.address + len(mutation.original)]
    check(f"{mutation.name} preimage matches committed firmware", observed == mutation.original, observed.hex())

by_name = {m.name: m for m in MUTATIONS}
check("diagnostic copy gate patch is two-byte NOP", by_name["rid1010-force-copy"].replacement == b"\x00\x00")
check("diagnostic result source patch points at generated-result buffer encoding", by_name["rid1010-result-source"].replacement.hex() == "2496aa99")
check("experiment contains no activation or status-source mutation", set(by_name) == {"rid1010-force-copy", "rid1010-result-source"})

def short_branch_target(addr: int, raw: bytes | None = None) -> int:
    hw = int.from_bytes(raw if raw is not None else firmware[addr:addr + 2], "little")
    return addr + (((hw >> 11) & 0x1F) << 4) + (((hw >> 4) & 0x7) << 1)

def short_condition(raw: bytes) -> int:
    return raw[0] & 0x0F

# Pin the semantics of the branch we are removing, not merely its bytes.
# Status 2 is the stock copy path; every other status takes the BNE to the
# zero-fill loop. NOPing only that BNE therefore forces the copy path.
check("RID1010 observer compares status 2 then branches on not-equal",
      firmware[0x68EC8:0x68ECC] == bytes.fromhex("629afa05"))
check("status!=2 BNE targets zero-fill loop", short_branch_target(0x68ECA) == 0x68ED8)
check("status==2 fallthrough branches to copy-loop condition",
      firmware[0x68ECC:0x68ECE] == bytes.fromhex("b515") and short_branch_target(0x68ECC) == 0x68EF2)
check("non-copy arm writes literal zero", firmware[0x68ECE:0x68ED4] == bytes.fromhex("01f0c6f18003"))
check("copy arm loads selected source byte and stores it",
      firmware[0x68EDE:0x68EF2] == bytes.fromhex("24963a9a01f0c191c6f1b297ffff410ac1008093"))
check("mutation purpose names the zero-fill branch it removes",
      "status!=2 zero-fill branch" in by_name["rid1010-force-copy"].purpose)
wrong_direction = bytes.fromhex("f505")
check("opposite-direction rewrite would be unconditional branch to zero-fill",
      short_condition(wrong_direction) == 0x5 and short_branch_target(0x68ECA, wrong_direction) == 0x68ED8)

print("\n== stock RoutineControl activation contract ==")
ROUTINE_RID = struct.Struct("<HBBI")
rid_100f = ROUTINE_RID.unpack_from(firmware, 0x26AEC + 8 * ROUTINE_RID.size)
check("RoutineControl entry 8 is enabled RID 0x100F", rid_100f == (0x100F, 0, 1, 0x26678), repr(rid_100f))
check("RID 0x100F selects policy index 0", struct.unpack_from("<H", firmware, 0x26690 + 8 * 2)[0] == 0)
check("policy 0 has no SecurityAccess requirement and three sessions", firmware[0x26420:0x26422] == b"\x00\x03")
session_list = struct.unpack_from("<I", firmware, 0x26678 + 4)[0]
session_records = [struct.unpack_from("<I", firmware, session_list + i * 4)[0] for i in range(3)]
check("policy 0 resolves to default/programming/extended sessions",
      session_list == 0x26668 and [firmware[record + 1] for record in session_records] == [1, 2, 3],
      repr([hex(record) for record in session_records]))
rid_config = firmware[0x26B8D + 8 * 15:0x26B8D + 9 * 15]
check("RID 0x100F enables control type 1", rid_config[4] == 1, rid_config.hex())
check("RID 0x100F control type 1 consumes zero data fields", firmware[0x26B93 + 8 * 15] == 0)
callback_row = struct.unpack_from("<HHII", firmware, 0x25804 + 8 * 12)
check("RID 0x100F callback row selects success precheck and action wrapper",
      callback_row == (0x100F, 0, 0x8A768, 0x8A782), repr(callback_row))
check("RID 0x100F action wrapper directly calls crypto_test_bank1_activate",
      firmware[0x8A786:0x8A78A] == bytes.fromhex("bdff92e8"))

print("\n== static crypto-test harness contract ==")
check("stable-input threshold is three observations", firmware[0x30FBB] == 3, str(firmware[0x30FBB]))
# The stock finalizer must not erase the generated-result buffer before the
# diagnostic shim can observe it.
finalizer = None
for line in (REPO / "data" / "generated" / "decompilations.jsonl").open(encoding="utf-8"):
    row = json.loads(line)
    if row.get("record") == "function" and row.get("entry_addr") == "0x00068de6":
        finalizer = row
        break
check("crypto_test_bank1_finalize is present in decompiler corpus", finalizer is not None)
if finalizer is not None:
    result_writes = [
        ref
        for ref in finalizer.get("data_references", [])
        if ref.get("ref_type") == "WRITE"
        and isinstance(ref.get("to_addr"), str)
        and 0xFEBE51AA <= int(ref["to_addr"], 16) < 0xFEBE51BA
    ]
    check("stock finalizer does not clear generated-result buffer", not result_writes, repr(result_writes))
# Signal metadata table used by crypto_test_read_input_properties:
# signal 95 -> COM byte offset 0x97, 8 bits; signal 96 -> offset 0x98, 8 bits.
check("selector signal id is 95", struct.unpack_from("<H", firmware, 0x25912)[0] == 0x5F)
check("mode signal id is 96", struct.unpack_from("<H", firmware, 0x25914)[0] == 0x60)
check("selector/mode COM offsets are consecutive bytes 0x97/0x98", struct.unpack_from("<H", firmware, 0x2592E)[0] == 0x97 and struct.unpack_from("<H", firmware, 0x25930)[0] == 0x98)
check("selector/mode widths are eight bits", firmware[0x2593A] == 8 and firmware[0x2593B] == 8)
# Message/expected-result signal groups map to offsets 0x9F,0xA7,0xAF,0xB7.
check("message/result group COM offsets match 0x01C..0x01F payloads", [struct.unpack_from("<H", firmware, off)[0] for off in (0x25932, 0x25934, 0x25936, 0x25938)] == [0x9F, 0xA7, 0xAF, 0xB7])

print("\n== deterministic patch/restore builder ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    try:
        build_plan(firmware_path, temp / "refuse")
    except ExperimentBuildError as exc:
        check("live preparation rejects invalid source boot CRC", "source boot-crc descriptor is invalid" in str(exc).lower(), str(exc))
    else:
        check("live preparation rejects invalid source boot CRC", False)

    fixture_plan = build_plan(firmware_path, temp / "fixture", allow_invalid_source_crc=True)
    check("offline fixture plan records invalid source CRC rather than hiding it", fixture_plan["source_image"]["boot_crc_valid_before"] is False)
    check("fixture patched image reaches expected CRC residue", int(fixture_plan["boot_crc"]["patched_residue"], 0) == EXPECTED_RESIDUE)
    check("fixture RESTORE preserves original target-block bytes", fixture_plan["restore"]["restored_target_block_matches_source"] is True)
    check("fixture RESTORE may differ only because invalid source CRC is normalized", fixture_plan["restore"]["restored_image_matches_source"] is False)
    restore = json.loads((temp / "fixture" / "RESTORE.json").read_text(encoding="utf-8"))
    check("RESTORE artifact is explicitly validated", restore["validated"] is True and int(restore["boot_crc"]["validated_restore_residue"], 0) == EXPECTED_RESIDUE)

    repaired = bytearray(firmware)
    # Existing CRC reconstruction evidence shows the public acquisition anomaly is
    # exactly 0xBB1C4: 0x80 -> 0x82. This produces a valid source for the generic
    # safety property test without changing any command-5 mutation preimage.
    repaired[0xBB1C4] = 0x82
    descriptors = discover_crc_descriptors(bytes(repaired), 0)
    high = next(item for item in descriptors if item.start == 0x18000)
    check("synthetic repaired source has valid high boot CRC", high.terminal_fixup_valid)
    repaired_path = temp / "repaired.bin"
    repaired_path.write_bytes(repaired)
    repaired_plan = build_plan(repaired_path, temp / "repaired")
    check("valid-source plan succeeds without unsafe override", repaired_plan["source_image"]["boot_crc_valid_before"] is True)
    check("valid-source RESTORE reconstructs exact source image", repaired_plan["restore"]["restored_image_matches_source"] is True)
    patched = (temp / "repaired" / "command5_experiment_patched.bin").read_bytes()
    for mutation in MUTATIONS:
        check(f"patched image contains {mutation.name} replacement", patched[mutation.address:mutation.address + len(mutation.replacement)] == mutation.replacement)
    patched_crc = next(item for item in discover_crc_descriptors(patched, 0) if item.start == 0x18000)
    check("patched image dynamically validates boot CRC", patched_crc.terminal_fixup_valid and patched_crc.full_crc == EXPECTED_RESIDUE)

print("\n== exact CAN stimulus mapping ==")
message = bytes(range(16))
expected = bytes(range(0x80, 0x90))
frames = build_input_frames(message, expected=expected)
check("selector-4/mode-1 frame is 0x01B bytes 04 01 ...", frames[0].address == 0x01B and frames[0].data == b"\x04\x01" + b"\x00" * 6)
check("0x01C/0x01D carry the exact 16-byte command-5 message", frames[1].address == 0x01C and frames[1].data == message[:8] and frames[2].address == 0x01D and frames[2].data == message[8:])
check("0x01E/0x01F carry the exact 16-byte expected value", frames[3].address == 0x01E and frames[3].data == expected[:8] and frames[4].address == 0x01F and frames[4].data == expected[8:])
plan = build_stimulus_plan(message, expected=expected)
check("default plan uses stock RoutineControl bank-1 activation", plan["activation"]["request"] == "31 01 10 0F")
check("default plan keeps fresh application boot as deterministic baseline", "fresh application boot" in plan["activation"]["lifecycle"] and "tester-controlled re-arm" in plan["activation"]["lifecycle"])
check("default plan uses five spaced rounds", plan["rounds"] == DEFAULT_ROUNDS == 5 and plan["round_interval_seconds"] == 0.10)
check("plan records three required stable observations", plan["stability"]["required_unchanged_observations"] == 3)
check("bounded Panda parameter encodes flag and selected bus", command5_elm327_param(base_param=1, bus=2) == 0x8201)
for invalid_param in (0x100, 0x8000, 0x10000):
    try:
        command5_elm327_param(base_param=invalid_param, bus=2)
    except StimulusError:
        check(f"reserved ELM327 parameter 0x{invalid_param:X} is rejected", True)
    else:
        check(f"reserved ELM327 parameter 0x{invalid_param:X} is rejected", False)
try:
    build_stimulus_plan(message, rounds=3)
except StimulusError as exc:
    check("too-few update rounds are rejected", "at least four" in str(exc), str(exc))
else:
    check("too-few update rounds are rejected", False)

print("\n== diagnostic response parsers ==")
activation = parse_bank1_activation_response(b"\x71\x01\x10\x0f")
check("bank-1 activation parser accepts exact stock RoutineControl response", activation["positive_response"] == "7101100f")
try:
    parse_bank1_activation_response(b"\x71\x01\x10\x0e")
except StimulusError as exc:
    check("bank-1 activation parser rejects wrong RID", "unexpected" in str(exc), str(exc))
else:
    check("bank-1 activation parser rejects wrong RID", False)

response = b"\x71\x03\x10\x10" + b"\x10" + bytes(range(16)) + bytes(range(32))
parsed = parse_control_type3_response(response)
check("RoutineControl result parser exposes patched status byte", parsed["status"] == 0x10)
check("RoutineControl result parser extracts exactly first 16 generated-result bytes", parsed["generated_cmac"] == bytes(range(16)))
check("RoutineControl result parser quarantines adjacent 32 bytes", parsed["extra"] == bytes(range(32)))
try:
    parse_control_type3_response(b"\x71\x03\x10\x11" + b"\x00" * 49)
except StimulusError as exc:
    check("wrong RID/selector response prefix is rejected", "unexpected" in str(exc), str(exc))
else:
    check("wrong RID/selector response prefix is rejected", False)

print("\n== live-observation timing/provenance/verdict schema (v4) ==")
stimulus_source = (REPO / "exploit" / "command5" / "stimulus.py").read_text(encoding="utf-8").lower()
check("live result schema is pinned as v4", '"sienna-command5-app-live-result-v4"' in stimulus_source)
check("older live result schemas are retired", all(f'"sienna-command5-app-live-result-v{s}"' not in stimulus_source for s in (1, 2, 3)))
check("live module constant matches the pinned schema", LIVE_RESULT_SCHEMA == "sienna-command5-app-live-result-v4")
check("configured command-5 poll interval is a named constant of 0.05 s", DEFAULT_POLL_INTERVAL == 0.05)
check("polling loop sleeps exactly the configured interval", 'time.sleep(default_poll_interval)' in stimulus_source)
check("poll interval is reported in the output timing block", '"poll_interval_seconds": default_poll_interval' in stimulus_source)
check("poll window and round interval are reported in the timing block", '"poll_window_seconds": poll_seconds' in stimulus_source and '"round_interval_seconds": round_interval' in stimulus_source)
check("each sent frame records monotonic and wall timestamps", '"sent_monotonic": sent_monotonic' in stimulus_source and '"sent_wall_utc": _utc_now()' in stimulus_source)
check("each polling observation records per-request RTT from monotonic clock", '"rtt_seconds": observed_monotonic - requested_monotonic' in stimulus_source and '"requested_monotonic": requested_monotonic' in stimulus_source and '"observed_monotonic": observed_monotonic' in stimulus_source)
check("each polling observation records a wall-clock stamp", '"observed_wall_utc": _utc_now()' in stimulus_source)
check("run-level provenance records start and finish monotonic/wall stamps", '"started_monotonic": started_monotonic' in stimulus_source and '"finished_wall_utc": _utc_now()' in stimulus_source)
check("timing block documents the clock semantics", '"monotonic": "time.monotonic seconds; deltas only (rtt, intervals), not wall time"' in stimulus_source)
check("baseline result request records its own RTT", '"rtt_seconds": baseline_rtt' in stimulus_source)
check("timing/DTC fields add no new mutating diagnostic service", stimulus_source.count("service_type.routine_control") == 2 and "service_type.read_dtc_information" in stimulus_source and "clear_diagnostic" not in stimulus_source and "service_type.write" not in stimulus_source and "request_download" not in stimulus_source and "write_data_by_identifier" not in stimulus_source)
check("live harness records read-only 19 02 FF DTC snapshots before and after", 'data=b"\\x02\\xff"' in stimulus_source and '"dtc_observation"' in stimulus_source and '"read_only": true' in stimulus_source)
check("DTC interpretation keeps command-failure/mismatch ambiguity", "cannot separate command failure from expected-result mismatch" in stimulus_source)

print("\n== v4 machine-readable verdict ==")
check("verdict schema is pinned", '"sienna-command5-verdict-v1"' in stimulus_source)
positive = build_verdict(result_regenerated=True, result_matches_expected=True, control_status=CONTROL_STATUS_ABSENT, dtc_changed=None)
check("regenerated result matching expected value is positive/equal", positive["conclusion"] == "positive" and positive["command_failure"] is False and positive["compare_mismatch"] is False)
positive_mismatch = build_verdict(result_regenerated=True, result_matches_expected=False, control_status=CONTROL_STATUS_ABSENT, dtc_changed=None)
check("regenerated result with wrong expected value separates compare mismatch", positive_mismatch["conclusion"] == "positive" and positive_mismatch["command_failure"] is False and positive_mismatch["compare_mismatch"] is True)
check("regenerated result without expected value leaves mismatch undecided", build_verdict(result_regenerated=True, result_matches_expected=None, control_status=CONTROL_STATUS_ABSENT, dtc_changed=None)["compare_mismatch"] is None)
control_sep = build_verdict(result_regenerated=False, result_matches_expected=None, control_status=CONTROL_STATUS_POSITIVE, dtc_changed=False)
check("passing separate-boot control leaves current-run failure mode unresolved", control_sep["conclusion"] == "negative_control_passed" and control_sep["command_failure"] is None and control_sep["compare_mismatch"] is None, repr(control_sep))
control_dtc = build_verdict(result_regenerated=False, result_matches_expected=None, control_status=CONTROL_STATUS_POSITIVE, dtc_changed=True)
check("passing control + latched DTC stays ambiguous", control_dtc["conclusion"] == "negative_control_passed" and control_dtc["command_failure"] is None and control_dtc["compare_mismatch"] is None)
control_no_dtc = build_verdict(result_regenerated=False, result_matches_expected=None, control_status=CONTROL_STATUS_POSITIVE, dtc_changed=None)
check("passing control without DTC snapshot stays ambiguous", control_no_dtc["command_failure"] is None and control_no_dtc["compare_mismatch"] is None)
control_failed = build_verdict(result_regenerated=False, result_matches_expected=None, control_status=CONTROL_STATUS_FAILED, dtc_changed=None)
check("failing control marks the run uninformative", control_failed["conclusion"] == "negative_control_failed" and control_failed["command_failure"] is None)
no_control = build_verdict(result_regenerated=False, result_matches_expected=None, control_status=CONTROL_STATUS_ABSENT, dtc_changed=True)
check("negative without control never decides the failure mode", no_control["conclusion"] == "negative_no_control" and no_control["command_failure"] is None and no_control["compare_mismatch"] is None)
check("incompatible control artifact downgrades to no-control", build_verdict(result_regenerated=False, result_matches_expected=None, control_status=CONTROL_STATUS_INCOMPATIBLE, dtc_changed=False)["conclusion"] == "negative_no_control")
check("missing baseline is explicitly inconclusive", build_verdict(result_regenerated=None, result_matches_expected=None, control_status=CONTROL_STATUS_ABSENT, dtc_changed=None)["conclusion"] == "inconclusive_no_baseline")
check("every verdict conclusion is from the pinned set", all(v["conclusion"] in ("positive", "inconclusive_no_baseline", "negative_no_control", "negative_control_passed", "negative_control_failed") for v in (positive, positive_mismatch, control_sep, control_dtc, control_no_dtc, control_failed, no_control)))

print("\n== v4 latency statistics and DTC classification ==")
stats = latency_statistics([0.10, 0.20, 0.30, 0.40])
check("latency statistics expose min/max/mean/jitter from monotonic deltas", stats["count"] == 4 and abs(stats["min_seconds"] - 0.10) < 1e-9 and abs(stats["max_seconds"] - 0.40) < 1e-9 and abs(stats["mean_seconds"] - 0.25) < 1e-9 and abs(stats["jitter_seconds"] - 0.30) < 1e-9)
check("empty latency input is None, not zero", latency_statistics([]) is None)
check("RTT statistics read observation rtt_seconds fields", observation_rtt_statistics([{"rtt_seconds": 0.5}, {"rtt_seconds": 0.7}])["max_seconds"] == 0.7)
check("interval statistics need two observations", observation_interval_statistics([{ "observed_monotonic": 1.0 }]) is None and abs(observation_interval_statistics([{ "observed_monotonic": 1.0 }, { "observed_monotonic": 1.25 }])["mean_seconds"] - 0.25) < 1e-9)
check("unchanged DTC snapshot classifies as no change", classify_dtc_change("ab00", "ab00") == {"available": True, "changed": False, "before_hex": "ab00", "after_hex": "ab00"})
check("changed DTC snapshot classifies as changed", classify_dtc_change("ab00", "ab01")["changed"] is True)
check("missing DTC snapshot classifies as unavailable", classify_dtc_change(None, "ab01") == {"available": False, "changed": None})

print("\n== v4 chronology, separate-boot control artifact, and CLI guards ==")
check("timeline marks every phase boundary in order", all(marker in stimulus_source for marker in ("_stimulus_started", "_stimulus_finished", "_polling_started", "_polling_finished", "bank1_activation", "dtc_snapshot_before", "dtc_snapshot_after", "control_artifact_loaded")) and '"phase": phase' in stimulus_source and 'phase="primary"' in stimulus_source)
check("timeline events carry monotonic and wall stamps", '"monotonic": time.monotonic()' in stimulus_source and '"wall_utc": _utc_now()' in stimulus_source)
check("exactly one stimulus/poll trial executes per run", stimulus_source.count("def _run_trial") == 1 and 'phase="primary"' in stimulus_source and stimulus_source.count("trial = _run_trial(") == 1 and 'phase="control"' not in stimulus_source)
check("same-boot control CLI options are fully removed", "--control-message" not in stimulus_source and "--control-expected" not in stimulus_source)
check("control is loaded artifact evidence, never executed", '"executed_this_boot": false' in stimulus_source and '"source": "separate-boot artifact"' in stimulus_source and stimulus_source.count("load_control_artifact(") >= 1)
check("control artifact loader is SHA-bound and role-checked", '"sha256": hashlib.sha256(raw).hexdigest()' in stimulus_source and "was not produced by a --role" in stimulus_source)
check("control run is bound to a fresh boot in plan text", "separate fresh boot" in json.dumps(build_stimulus_plan(bytes(16))) and "never re-executed" in stimulus_source)
check("roles are exactly experiment and control", ROLES == ("experiment", "control") and ROLE_EXPERIMENT == "experiment" and ROLE_CONTROL == "control")
check("experiment-role live result carries the role field", '"role": role' in stimulus_source)
check("--control-artifact is refused on control-role runs", "--control-artifact is valid only for --role experiment runs" in stimulus_source and "--control-artifact is for experiment runs" in stimulus_source)
check("--control-artifact requires --execute", '"--control-artifact requires --execute"' in stimulus_source)

print("\n== separate-boot control artifact loader ==")
import tempfile
from exploit.common.ram_exec import RamExecRoute
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    route = RamExecRoute(0, 1, "old", 0)
    good_control = {
        "schema": "sienna-command5-app-live-result-v4",
        "role": "control",
        "f181_hex": "41424344",
        "route": {"bus": 0, "elm327_param": 1, "uds_variant": "old", "cpu_index": 0},
        "verdict": {"result_regenerated": True, "conclusion": "positive"},
    }
    good_path = tmp / "control.json"
    good_path.write_text(json.dumps(good_control))
    evidence = load_control_artifact(good_path, f181_hex="41424344", route=route)
    check("matching control artifact classifies positive", evidence["status"] == CONTROL_STATUS_POSITIVE and evidence["f181_match"] is True and evidence["route_match"] is True and evidence["executed_this_boot"] is False)
    check("control artifact SHA-256 binds the loaded bytes", evidence["sha256"] == hashlib.sha256(good_path.read_bytes()).hexdigest())
    check("F181 mismatch classifies incompatible", load_control_artifact(good_path, f181_hex="ffff", route=route)["status"] == CONTROL_STATUS_INCOMPATIBLE)
    check("route mismatch classifies incompatible", load_control_artifact(good_path, f181_hex="41424344", route=RamExecRoute(1, 1, "old", 0))["status"] == CONTROL_STATUS_INCOMPATIBLE)
    check("UDS variant mismatch classifies incompatible", load_control_artifact(good_path, f181_hex="41424344", route=RamExecRoute(0, 1, "new", 0))["status"] == CONTROL_STATUS_INCOMPATIBLE)
    check("CPU index mismatch classifies incompatible", load_control_artifact(good_path, f181_hex="41424344", route=RamExecRoute(0, 1, "old", 1))["status"] == CONTROL_STATUS_INCOMPATIBLE)
    failed_control = dict(good_control); failed_control["verdict"] = {"result_regenerated": False}
    failed_path = tmp / "failed.json"; failed_path.write_text(json.dumps(failed_control))
    check("non-regenerating control run classifies failed", load_control_artifact(failed_path, f181_hex="41424344", route=route)["status"] == CONTROL_STATUS_FAILED)
    experiment_role = dict(good_control); experiment_role["role"] = "experiment"
    role_path = tmp / "role.json"; role_path.write_text(json.dumps(experiment_role))
    try:
        load_control_artifact(role_path, f181_hex="41424344", route=route)
        check("artifact not tagged --role control is rejected", False)
    except StimulusError:
        check("artifact not tagged --role control is rejected", True)
    wrong_schema = dict(good_control); wrong_schema["schema"] = "sienna-command5-app-live-result-v3"
    schema_path = tmp / "schema.json"; schema_path.write_text(json.dumps(wrong_schema))
    try:
        load_control_artifact(schema_path, f181_hex="41424344", route=route)
        check("non-v4 control artifact is rejected", False)
    except StimulusError:
        check("non-v4 control artifact is rejected", True)
    trash_path = tmp / "trash.json"; trash_path.write_text("not json")
    try:
        load_control_artifact(trash_path, f181_hex=None, route=route)
        check("malformed control artifact is rejected", False)
    except StimulusError:
        check("malformed control artifact is rejected", True)
    missing_path = tmp / "absent.json"
    try:
        load_control_artifact(missing_path, f181_hex=None, route=route)
        check("missing control artifact is rejected", False)
    except StimulusError:
        check("missing control artifact is rejected", True)

print("\n== scope and interpretation discipline ==")
check("primary timing block reports RTT and poll-interval statistics", '"rtt_statistics": trial["rtt_statistics"]' in stimulus_source and '"poll_interval_statistics": trial["poll_interval_statistics"]' in stimulus_source)
check("plan publishes the verdict contract and control option", '"verdict_contract": verdict_contract' in stimulus_source and '"known_good_control"' in stimulus_source)

print("\n== scope and interpretation discipline ==")
source = (REPO / "exploit" / "command5" / "build_experiment.py").read_text(encoding="utf-8").lower()
check("experiment patch does not contain SecOC Gate-2 target addresses", "8e6c6" not in source and "8e6c8" not in source)
check("experiment patch does not import production flash backend", "flash_backend" not in source)
check("stimulus labels result as application-context evidence only", "does not prove production secoc transmit integration" in stimulus_source)
check("live stimulus activates bank 1 through stock RoutineControl", "_raw_bank1_activate" in stimulus_source and "service_type.routine_control" in stimulus_source and "rid_bank1_activate" in stimulus_source)
check("live stimulus keeps fresh boot as deterministic baseline and documents runtime reset bound", "fresh application boot" in stimulus_source and "tester-controlled re-arm" in stimulus_source)
check("live stimulus keeps pre-stimulus diagnostic baseline", "result_changed_from_pre_stimulus_baseline" in stimulus_source)
check("live stimulus selects bounded ELM327 command-5 mode", "command5_elm327_param" in stimulus_source)
check("live stimulus rejects Panda-blocked frames", "safety_tx_blocked" in stimulus_source)
check("live stimulus restores ordinary ELM327 mode", "restore ordinary diagnostic-only elm mode" in stimulus_source)

print("\n== bounded Panda safety provenance ==")
safety_patch_path = REPO / "exploit" / "command5" / "kai-openpilot-command5-safety.patch"
safety_meta_path = REPO / "exploit" / "command5" / "kai-openpilot-command5-safety.json"
safety_meta = json.loads(safety_meta_path.read_text(encoding="utf-8"))
check("bounded safety patch is hash-pinned", hashlib.sha256(safety_patch_path.read_bytes()).hexdigest() == safety_meta["patch"]["sha256"])
check("bounded safety pins full external commits", len(safety_meta["commit"]) == 40 and len(safety_meta["opendbc"]["commit"]) == 40)
check("bounded safety remains local-only", safety_meta["pushed"] is False)
safety_patch = safety_patch_path.read_text(encoding="utf-8").lower()
check("bounded safety allows exact five application IDs", "msg->addr >= 0x01bu" in safety_patch and "msg->addr <= 0x01fu" in safety_patch)
check("bounded safety binds the selected bus", "msg->bus == elm327_command5_bus" in safety_patch)
check("bounded safety retains eight-byte gate", "if (len != 8)" in safety_patch)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
