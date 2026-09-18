#!/usr/bin/env python3
"""Verify the one-payload functional-0x777 TSS3 signer implementation."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import build_tss3_unified_b6_signer as unified_builder
from exploit.ephemeral_runtime import tss3_unified_b6_signer as host

BUILDER = ROOT / "exploit/ephemeral_runtime/build_tss3_unified_b6_signer.py"
KIT_BUILDER = ROOT / "tools/targets/tss3/builders/build_tss3_unified_b6_signer_kit.py"
TARGETS = {
    "camry-8965F3307000": ("0xFEBE5751", "split-telemetry", 462, 596, "supervised-continuous", 7),
    "corolla-8965H1202000": ("0xFEBE563D", "corolla-resident-prefix", 522, 458, "supervised-continuous", 7),
    "corolla-8965F1208000": ("0xFEBE563D", "corolla-resident-prefix", 522, 458, "supervised-continuous", 7),
    "crown-8965F3012000": ("0xFEBE527D", "split-telemetry", 462, 596, "supervised-continuous", 7),
}


def check(label: str, condition: object) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[PASS] {label}")


check("C7 is recurring control and C6 is split-target installation only",
      host.loader_frame(3, bytes.fromhex("11223344")) == bytes.fromhex("07c6c60311223344") and
      host.replacement_frame(7, 0x1234) == bytes.fromhex("07c7c70712340000") and
      host.release_frame() == bytes.fromhex("07c7c70000000000"))
post_replace_raw = bytearray(host.SPLIT_TELEMETRY_SIZE)
post_replace_raw[8:12] = bytes.fromhex("d4a561f5")
post_replace_raw[12:16] = bytes.fromhex("11223344")
post_replace_raw[17] = 1
post_replace = host.decode_split_telemetry(bytes(post_replace_raw))
check("Camry/Crown telemetry distinguishes sticky oracle from latest trailer equality",
      post_replace["oracle_latched"] is True and post_replace["native_verified"] is True and
      post_replace["latest_trailer_equality"] is False and post_replace["native_signature_match"] is False)
postauth_raw = bytearray(host.SPLIT_TELEMETRY_SIZE)
postauth_raw[0:4] = (7).to_bytes(4, "little")
postauth_raw[4:8] = (5).to_bytes(4, "little")
postauth_raw[16] = 23
postauth_raw[17] = 1
postauth = host.decode_postauth_telemetry(bytes(postauth_raw))
check("post-auth telemetry reports native publications and application overrides without inventing command5 work",
      postauth["native_publication_count"] == 7 and postauth["override_count"] == 5 and
      postauth["last_control_seq"] == 23 and postauth["native_publication_observed"] is True and
      postauth["command5_attempts"] == 0 and postauth["native_signature_match"] is False)
check("legacy target-specific implementations remain in tree",
      all((ROOT / path).is_file() for path in (
          "exploit/ephemeral_runtime/build_camry_f33_b6_inline_signer.py",
          "exploit/ephemeral_runtime/build_corolla_hf_b6_inline_signer.py",
          "exploit/ephemeral_runtime/build_crown_f30_b6_inline_signer.py",
          "exploit/ephemeral_runtime/camry_f33_b6_inline_signer.py",
          "exploit/ephemeral_runtime/corolla_hf_b6_inline_signer.py",
          "exploit/ephemeral_runtime/crown_f30_b6_inline_signer.py",
      )))

resident_source = (ROOT / "exploit/ephemeral_runtime/tss3_unified_b6_signer_resident.S").read_text()
field_resident_source = (ROOT / "exploit/ephemeral_runtime/tss3_unified_b6_signer_field_resident.S").read_text()
helper_source = (ROOT / "exploit/ephemeral_runtime/tss3_unified_b6_signer_helper.S").read_text()
postauth_helper_source = (ROOT / "exploit/ephemeral_runtime/camry_f33_b6_postauth_override_helper.S").read_text()
check("experimental one-shot and field split-loader residents remain separate",
      "#ifdef TSS3_COROLLA_HF" in resident_source and "#ifdef TSS3_COROLLA_HF" in helper_source and
      "FEF07C00" in resident_source and ".L_parse_loader" not in resident_source and
      "C6 C6" in field_resident_source and ".L_parse_loader" in field_resident_source and
      "FEF07C00" not in field_resident_source)
check("Camry/Crown helper keeps call-spanning locals in ABI-preserved registers",
      "prepare {r20-r21,lp}, 0" in helper_source and
      "mov 2, r20                   /* operation = replace; callee-saved */" in helper_source and
      "ld.hu TSS3_DCM_TARGET_OFF[gp], r21" in helper_source and
      "st.h r21, 0x4a8e[gp]" in helper_source and
      "dispose 0, {r20-r21,lp}, lp" in helper_source and
      "st.b r6, 0x4ad0[gp]" not in helper_source and "st.h r6, 0x4ad2[gp]" not in helper_source)
check("native oracle retries freshness skew and command5 rc2 before terminal failure",
      "Keep oracle state 0 while the snapshot/result is still retryable" in helper_source and
      "be .L_return              /* rc2 = transient busy/poll timeout; retry next native frame */" in helper_source and
      ".L_terminal_fail:" in helper_source and
      "st.b r6, 0x4a79[gp]" in helper_source)
check("Camry field post-auth backend leaves native SecOC untouched and overrides only route44 application bytes",
      "jarl32 secoc_aggregate, lp" in postauth_helper_source and
      "jarl32 comm_after_secoc, lp" in postauth_helper_source and
      "jarl32 application_aggregate, lp" in postauth_helper_source and
      "jarl32 aggregate_final, lp" in postauth_helper_source and
      "command5_sync" not in postauth_helper_source and "freshness_encode" not in postauth_helper_source and
      all(token in postauth_helper_source for token in (
          "TSS3_RAW_B3_OFF", "TSS3_RAW_B4_OFF", "TSS3_RAW_B5_OFF",
          "TSS3_RAW_B6_OFF", "TSS3_RAW_B8_OFF", "TSS3_RAW_B9_OFF")) and
      "TSS3_RAW_B7_OFF" not in postauth_helper_source and "TSS3_B6_TRAILER_OFF" not in postauth_helper_source)
check("Camry post-auth resident cannot execute low helper before C6 arm",
      "#ifdef TSS3_CAMRY_POSTAUTH_OVERRIDE" in field_resident_source and
      "tst1 0, 0x4a62[gp]" in field_resident_source and
      "be .L_postauth_stock_tail" in field_resident_source and
      "jr32 target_stock_aggregate_tail" in field_resident_source)
check("Camry/Crown resident no longer depends on functional-loader offsets",
      unified_builder.TARGETS["camry-8965F3307000"]["resident_macros"] == {} and
      unified_builder.TARGETS["crown-8965F3012000"]["resident_macros"] == {} and
      unified_builder.TARGETS["camry-8965F3307000"]["helper_macros"]["TSS3_DCM_SEQ_OFF"] == -0x60AD and
      unified_builder.TARGETS["crown-8965F3012000"]["helper_macros"]["TSS3_DCM_SEQ_OFF"] == -0x6581)
check("Corolla H/F select one shared runtime profile",
      unified_builder.TARGETS["corolla-8965H1202000"]["profile"] == "corolla-hf" and
      unified_builder.TARGETS["corolla-8965F1208000"]["profile"] == "corolla-hf" and
      unified_builder.PROFILE_RUNTIME_IDENTITIES["corolla-hf"] == "8965F1208000")

for target, spec in unified_builder.TARGETS.items():
    image = Path(spec["image"]).read_bytes()
    signature = int.from_bytes(
        image[unified_builder.BOOT_FAMILY_PROBE_ADDR:unified_builder.BOOT_FAMILY_PROBE_ADDR + 4], "little"
    )
    check(
        f"{target}: universal dispatcher has an exact low-CodeFlash boot-family discriminator",
        signature == unified_builder.BOOT_FAMILY_SIGNATURES[spec["boot_family"]],
    )

# The temporary helper transit is deliberately the last 1 KiB of exact GlobalRAM.
# Every supported image is SHA-bound separately by the builder; independently pin
# the useful negative that no aligned CodeFlash pointer targets the transit span.
for target, spec in unified_builder.TARGETS.items():
    image = Path(spec["image"]).read_bytes()
    refs = []
    for off in range(0, len(image) - 3, 4):
        value = int.from_bytes(image[off:off + 4], "little")
        if unified_builder.UNIVERSAL_HELPER_TRANSIT_BASE <= value < (
                unified_builder.UNIVERSAL_HELPER_TRANSIT_BASE + unified_builder.UNIVERSAL_HELPER_TRANSIT_LIMIT):
            refs.append((off, value))
    check(f"{target}: universal GlobalRAM helper transit has no aligned pointer literal", refs == [])
    corpus = ROOT / "data/generated" / target / "decompilations.jsonl"
    check(f"{target}: tracked decompiler corpus available for GlobalRAM transit audit", corpus.is_file())
    data_refs = []
    for line in corpus.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("record") != "function":
            continue
        for ref in row.get("data_references", []):
            address = int(ref["to_addr"], 16)
            if unified_builder.UNIVERSAL_HELPER_TRANSIT_BASE <= address < (
                    unified_builder.UNIVERSAL_HELPER_TRANSIT_BASE + unified_builder.UNIVERSAL_HELPER_TRANSIT_LIMIT):
                data_refs.append((row["entry_addr"], ref["from_addr"], ref["to_addr"], ref["ref_type"]))
    check(f"{target}: recovered application graph has no direct GlobalRAM transit reference", data_refs == [])

built: dict[str, tuple[dict, Path]] = {}
with tempfile.TemporaryDirectory(prefix="verify-tss3-unified-") as td:
    root = Path(td)
    out = root / "universal"
    proc = subprocess.run(
        [sys.executable, str(BUILDER), "--target", "all", "--output-dir", str(out)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    printed = json.loads(proc.stdout)
    check("builder emits one universal build set", printed["schema"] == "tss3-universal-b6-signer-build-set-v1")
    universal = printed["universal"]
    payload_path = out / universal["payload"]["path"]
    stage_path = out / universal["staging"]["path"]
    payload = payload_path.read_bytes(); stage = stage_path.read_bytes()
    check("one authenticated payload contains all three runtime profiles",
          len(payload) == 0x1000 and universal["payload"]["size"] == 0x1000 and
          universal["staging"]["size"] == len(stage) < unified_builder.UNIVERSAL_STAGING_LIMIT and
          set(universal["profiles"]) == {"camry-f33", "crown-f30", "corolla-hf"} and
          universal["dispatcher"]["boot_family_probe_address"] == "0x00000C80" and
          universal["dispatcher"]["boot_family_signatures"] == {"f3": "0x9D230D21", "corolla": "0x0030F6F3"} and
          universal["dispatcher"]["identity_address"] == "0x00020860" and
          universal["dispatcher"]["ordering"] == "low boot-family signature -> exact family boot init/validity -> application identity" and
          universal["helper_transit"]["base"] == "0xFEF07C00")
    transit_mpu = universal["helper_transit"]["mpu"]
    check("universal GlobalRAM transit is MPU R/W/X in both recovered application contexts",
          set(transit_mpu) == set(unified_builder.TARGETS) and
          all(row["mpu_region"] == 12 and row["mpu_bounds"] == ["0xFEC00000", "0xFFFFFFFC"] and
              row["ctx0_mpat"] == row["ctx1_mpat"] == "0x000000B8" and
              row["aligned_codeflash_pointer_hits"] == [] for row in transit_mpu.values()))
    for profile, row in universal["profiles"].items():
        resident = (out / row["resident_path"]).read_bytes()
        helper = (out / row["helper_path"]).read_bytes()
        check(f"{profile}: profile bytes are embedded byte-exact in universal staging",
              stage[row["resident_offset"]:row["resident_offset"] + len(resident)] == resident and
              stage[row["helper_offset"]:row["helper_offset"] + len(helper)] == helper)

    common_payload_sha = universal["payload"]["sha256"]
    common_staging_sha = universal["staging"]["sha256"]
    for target, (buffer, state_model, resident_size, helper_size, runtime_mode, host_loss_ticks) in TARGETS.items():
        meta = printed["targets"][target]
        meta_path = out / f"{target.replace('-', '_')}_unified_b6_signer.json"
        check(f"{target}: target wrapper written byte-for-byte", json.loads(meta_path.read_text()) == meta)
        check(f"{target}: exact common functional control",
              meta["schema"] == "tss3-unified-b6-signer-build-v1" and
              meta["control"]["can_id"] == "0x777" and meta["control"]["bus"] == 1 and
              meta["control"]["extended"] is False and meta["control"]["dcm_buffer"] == buffer and
              meta["control"]["loader_frame"] is None and
              meta["control"]["runtime_frame"] == "07 C7 C7 seq target_hi target_lo 00 00" and
              meta["control"]["runtime_mode"] == runtime_mode and
              meta["control"]["host_loss_ticks"] == host_loss_ticks and
              meta["control"]["release_sequence_zero"] is True and
              meta["control"]["functional_nrc11_suppressed"] is True and
              meta["install_strategy"] == "universal-one-shot" and meta["state_model"] == state_model)
        check(f"{target}: wrapper references the exact same universal executable",
              meta["artifacts_sha256"]["payload"] == common_payload_sha and
              meta["artifacts_sha256"]["staging"] == common_staging_sha and
              meta["universal_payload"]["sha256"] == common_payload_sha and
              meta["layout"]["helper_transfer"]["host_loader"] is False)
        check(f"{target}: resident/helper reproduce reviewed exact sizes",
              meta["resident"]["size"] == resident_size and meta["resident"]["headroom"] == 524 - resident_size and
              meta["helper"]["size"] == helper_size and meta["helper"]["image_size"] == helper_size and
              meta["helper"]["headroom"] == meta["helper"]["limit"] - helper_size and
              meta["resident"]["relocations"] == meta["helper"]["relocations"] == 0)
        bundle = host.load_bundle(meta_path)
        plan = host.plan(bundle)
        check(f"{target}: plan is one-shot install followed only by C7 runtime control",
              plan["sequence"][0].startswith("NRTD/Park: prove exact-target stock functional 0x777") and
              "helper" in plan["sequence"][2] and "native command-5 MAC oracle" in plan["sequence"][2] and
              meta["artifacts"]["payload"] == universal["payload"]["path"] and
              plan["old_implementations_retained"] is True)
        built[target] = (meta, meta_path)

    check("all target wrappers use one payload SHA",
          {meta["artifacts_sha256"]["payload"] for meta, _ in built.values()} == {common_payload_sha})
    check("Corolla H/F wrappers share the same resident and helper runtime bytes",
          built["corolla-8965H1202000"][0]["resident"]["sha256"] == built["corolla-8965F1208000"][0]["resident"]["sha256"] and
          built["corolla-8965H1202000"][0]["helper"]["sha256"] == built["corolla-8965F1208000"][0]["helper"]["sha256"])

    # Execute the exact compiled Corolla H helper's C7 lease gates in the
    # target Ghidra emulator. This protects continuous 100-Hz host ownership,
    # seven-tick host-loss expiry, zero release, and empty-queue aging.
    corolla_meta, corolla_meta_path = built["corolla-8965H1202000"]
    corolla_helper = corolla_meta_path.parent / corolla_meta["artifacts"]["helper"]
    liveness_result = root / "corolla-unified-liveness.json"
    liveness_script = ROOT / "ghidra/scripts/verify/VerifyCorollaUnifiedSignerHostLiveness.java"
    liveness = subprocess.run(
        [str(ROOT / "tools/gtarget"), "corolla-8965H1202000", "script", "run", str(liveness_script), "--",
         str(corolla_helper), str(liveness_result)],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=90,
    )
    liveness_record = json.loads(liveness_result.read_text(encoding="utf-8"))
    check("Corolla unified compiled helper has continuous supervised C7 liveness",
          liveness_record["passed"] == 36 and liveness_record["vehicle_executed"] is False and
          liveness_record["helper_sha256"] == corolla_meta["helper"]["sha256"] and
          "normal 100 Hz host remains continuously admitted" in liveness_record["tests"] and
          "host loss expires at seventh tick" in liveness_record["tests"] and
          "returning native B6 after empty-queue expiry stays native" in liveness_record["tests"] and
          liveness.returncode == 0)

    # Behavioral fixture for the common mailbox proof. DCM teardown may clear
    # service byte 0 while the six-byte tail remains the durable witness.
    meta, meta_path = built["camry-8965F3307000"]
    bundle = host.load_bundle(meta_path)

    class FakePanda:
        def __init__(self): self.sent = []
        def can_recv(self): return []
        def can_send(self, addr, dat, bus, **kwargs): self.sent.append((addr, bytes(dat), bus))

    panda = FakePanda()
    reads = iter((bytes(7), bytes.fromhex("00c7a512340000")))
    clock = iter(i / 1000 for i in range(10000))
    with (mock.patch.object(host, "verify_nrtd_ready", return_value={"ready_values": [0]}),
          mock.patch.object(host, "_open_app", return_value=(panda, object(), object(), bundle.target["application_f181_hex"], "fixture", None)),
          mock.patch.object(host, "_resident_already_present", return_value=False),
          mock.patch.object(host, "_read_memory", side_effect=lambda *a, **k: next(reads)),
          mock.patch.object(host.time, "monotonic", side_effect=lambda: next(clock)),
          mock.patch.object(host.time, "monotonic_ns", return_value=123456789),
          mock.patch.object(host.time, "sleep", return_value=None)):
        result = host.preflight(bundle)
    check("common functional mailbox fixture qualifies durable tail with no response",
          result["qualified"] is True and result["verdict"] == "stock_functional_mailbox_live" and
          result["mailbox"]["tail_match"] is True and panda.sent == [(0x777, host.PROBE_FRAME, 1)])

    # One packaged Crown kit exercises the field handoff without multiplying the
    # already-covered four-target compilation cost.
    kit = root / "crown-kit"
    kit_proc = subprocess.run(
        [sys.executable, str(KIT_BUILDER), "--target", "crown-8965F3012000", "--out", str(kit)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    kit_meta = json.loads(kit_proc.stdout)
    packaged_meta = json.loads((kit / "bundle/unified.json").read_text(encoding="utf-8"))
    check("unified field kit packages one exact target and common launcher",
          kit_meta["schema"] == "tss3-unified-b6-signer-kit-v1" and
          kit_meta["target"]["name"] == "crown-8965F3012000" and
          kit_meta["install_strategy"] == "split-functional-loader" and
          packaged_meta["install_strategy"] == "split-functional-loader" and
          packaged_meta["control"]["loader_frame"] == "07 C6 C6 index word_le32" and
          packaged_meta["control"]["runtime_frame"] == "07 C7 C7 seq target_hi target_lo 00 00" and
          packaged_meta["layout"]["helper_transfer"]["strategy"] == "functional-c6-after-startup" and
          packaged_meta["layout"]["helper_transfer"]["boot_context_globalram_write"] is False and
          packaged_meta["helper"]["image_size"] == 600 and
          packaged_meta["exact_target_payload"]["dispatcher"]["mode"] == "host-exact-f181-bound" and
          packaged_meta["exact_target_payload"]["dispatcher"]["codeflash_data_reads_before_resident"] is False and
          packaged_meta["exact_target_payload"]["dispatcher"]["boot_context_globalram_write"] is False and
          packaged_meta["exact_target_payload"]["dispatcher"]["boot_calls"] ==
              ["0x00000C9A", "0x00000E54", "0x00000F80", "0x000010C6", "0x0000119E"] and
          (kit / "tss3-unified-signer").is_file() and (kit / "bundle/unified.json").is_file() and
          (kit / "runtime/tsk/lib/programming.py").is_file() and
          (kit / "runtime/exploit/ephemeral_runtime/camry_f33_post_install_recovery.py").is_file())
    launcher = (kit / "tss3-unified-signer").read_text(encoding="utf-8")
    check("unified kit prefers vendored runtime and exposes common test ladder plus exact-F33 DRCC diagnostic clear",
          'PYTHONPATH="$KIT_ROOT/runtime:$OPENPILOT_ROOT"' in launcher and
          "camry_f33_post_install_recovery.py" in launcher and "require_camry_recovery" in launcher and
          all(cmd in launcher for cmd in ("preflight", "install", "qualify", "bringup", "recover-drcc", "replace-current", "replace-once")))

    field_bundle = host.load_bundle(kit / "bundle/unified.json")
    check("split field bundle carries the exact padded 150-word helper image",
          field_bundle.strategy == "split-functional-loader" and
          len(field_bundle.helper_image) == 600 and len(field_bundle.helper_image) // 4 == 150)
    loader_session = object.__new__(host.Session)
    loader_session.bundle = field_bundle
    loader_session.client = object(); loader_session.uds_mod = object()
    loader_session.panda = FakePanda()
    init_state = {"initialized": True, "armed": False, "armed_raw": 0, "next_index": 0, "last_command5_rc": 0, "signed_count": 0}
    loaded_state = {"initialized": True, "armed": False, "armed_raw": 0, "next_index": 150, "last_command5_rc": 0, "signed_count": 0}
    armed_state = {"initialized": True, "armed": True, "armed_raw": 1, "next_index": 150, "last_command5_rc": 0, "signed_count": 0}
    loader_session.split_state = mock.Mock(side_effect=(init_state, loaded_state, armed_state))
    with (mock.patch.object(host, "_read_memory_retry", return_value=field_bundle.helper_image),
          mock.patch.object(host.time, "sleep", return_value=None)):
        loaded = loader_session.load_and_arm_split_helper()
    check("split field loader sends 150 repeated C6 words then explicit arm and verifies readback",
          loaded["helper_byte_exact"] is True and loaded["state"] == armed_state and
          len(loader_session.panda.sent) == 150 * host.WORD_REPEAT_COUNT + 1 and
          loader_session.panda.sent[0] == (0x777, host.loader_frame(0, field_bundle.helper_image[:4]), 1) and
          loader_session.panda.sent[-1] == (0x777, host.loader_frame(host.ARM_INDEX), 1))

    camry_kit = root / "camry-postauth-kit"
    camry_kit_proc = subprocess.run(
        [sys.executable, str(KIT_BUILDER), "--target", "camry-8965F3307000", "--out", str(camry_kit)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    camry_kit_meta = json.loads(camry_kit_proc.stdout)
    camry_field_meta = json.loads((camry_kit / "bundle/unified.json").read_text(encoding="utf-8"))
    camry_field_bundle = host.load_bundle(camry_kit / "bundle/unified.json")
    camry_plan = host.plan(camry_field_bundle)
    check("Camry field kit uses post-auth raw-COM ownership with no command5 runtime dependency",
          camry_kit_meta["target"]["name"] == "camry-8965F3307000" and
          camry_field_meta["runtime_backend"] == "postauth-raw-com" and
          camry_field_meta["resident"]["size"] == 522 and camry_field_meta["helper"]["size"] == 218 and
          camry_field_meta["helper"]["image_size"] == 600 and
          camry_field_meta["sources"]["helper"]["path"].endswith("camry_f33_b6_postauth_override_helper.S") and
          camry_field_meta["mutation_boundary"]["postauth_raw_com_override"] is True and
          camry_field_meta["mutation_boundary"]["native_secoc_bytes_mutated"] is False and
          camry_field_meta["mutation_boundary"]["command5_runtime_required"] is False and
          camry_field_meta["mutation_boundary"]["native_mac_oracle_required"] is False and
          camry_field_meta["layout"]["postauth_override"]["raw_com_base"] == "0xFEBE4BFF" and
          "native authenticated route44 publication" in camry_plan["sequence"][2] and
          "command-5 MAC oracle" not in camry_plan["sequence"][2])

    postauth_qual_session = object.__new__(host.Session)
    postauth_qual_session.bundle = camry_field_bundle
    postauth_qual_session.wait_self_install = mock.Mock(return_value={"state": {"initialized": True}})
    postauth_qual_session.load_and_arm_split_helper = mock.Mock(return_value={"passes": [], "state": {"armed": True}, "helper_byte_exact": True})
    postauth_qual_session.split_state = mock.Mock(return_value={
        "initialized": True, "armed": True, "signed_count": 0, "last_command5_rc": 0,
    })
    postauth_qual_session.split_telemetry = mock.Mock(return_value={
        "native_publication_count": 3, "override_count": 0, "last_control_seq": 0,
        "native_publication_observed": True, "native_verified_raw": 1,
    })
    postauth_qualified = postauth_qual_session.qualify()
    check("Camry post-auth qualification proves released native publication without invoking command5 oracle",
          postauth_qualified["qualified"] is True and postauth_qualified["runtime_backend"] == "postauth-raw-com" and
          postauth_qual_session.split_telemetry.call_count == 1)

    postauth_emu_result = root / "camry-postauth-override-emulation.json"
    postauth_emu_script = ROOT / "ghidra/scripts/verify/VerifyCamryPostauthOverrideHelper.java"
    postauth_emu = subprocess.run(
        [str(ROOT / "tools/gtarget"), "camry-8965F3307000", "script", "run", str(postauth_emu_script), "--",
         str(camry_kit / "bundle" / camry_field_meta["artifacts"]["helper"]), str(postauth_emu_result)],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=90,
    )
    postauth_emu_record = json.loads(postauth_emu_result.read_text(encoding="utf-8"))
    check("compiled Camry post-auth helper enforces exclusive cached C7 ownership in the F33 emulator",
          postauth_emu_record["passed"] == 18 and postauth_emu_record["vehicle_executed"] is False and
          postauth_emu_record["helper_sha256"] == camry_field_meta["helper"]["sha256"] and
          "unrelated DCM traffic cannot leak native target during live lease" in postauth_emu_record["tests"] and
          "same C7 generation cannot change cached target" in postauth_emu_record["tests"] and
          "seventh held tick expires to stock target" in postauth_emu_record["tests"] and postauth_emu.returncode == 0)

    class GuardPanda:
        def __init__(self, *, fault=False, gear=0, stale=False):
            self.calls = 0
            self.fault = fault
            self.gear = gear
            self.stale = stale
        def can_recv(self):
            import time
            self.calls += 1
            wheel = bytearray.fromhex("1a6f1a6f1a6f1a6f")
            if self.fault:
                for i in (0, 2, 4, 6): wheel[i] |= 0x80
            angle = bytes(32)
            gear127 = bytes((0, 0, 0, 0, 0, (self.gear & 0x0F) << 4, 0, 0))
            if self.stale:
                if self.calls == 1:
                    return [(host.WHEEL_SPEED_CAN_ID, bytes(wheel), host.CONTROL_BUS),
                            (host.STEERING_ANGLE_CAN_ID, angle, host.CONTROL_BUS),
                            (0x127, gear127, host.CONTROL_BUS)]
                if self.calls == 2:
                    time.sleep(0.11)
                    return [(host.READY_CAN_ID, bytes.fromhex("8000000000000000"), host.CONTROL_BUS)]
                return []
            if self.calls > 1:
                return []
            return [
                (host.READY_CAN_ID, bytes.fromhex("8000000000000000"), host.CONTROL_BUS),
                (host.WHEEL_SPEED_CAN_ID, bytes(wheel), host.CONTROL_BUS),
                (host.STEERING_ANGLE_CAN_ID, angle, host.CONTROL_BUS),
                (0x127, gear127, host.CONTROL_BUS),
            ]

    guard = host.verify_ready_stationary_current_angle(GuardPanda(), target_family="corolla-hf")
    check("unified current-angle guard derives a zero no-offset target while READY, Park, and stationary",
          guard["ready_values"] == [1] and guard["wheel_centered_raw"] == [0, 0, 0, 0] and
          guard["wheel_faults"] == [False, False, False, False] and guard["gear"]["park"] is True and
          guard["steering_angle_deg"] == 0.0 and guard["recommended_current_target_raw"] == 0)

    for label, fixture in (("wheel fault", GuardPanda(fault=True)), ("not Park", GuardPanda(gear=3))):
        try:
            host.verify_ready_stationary_current_angle(fixture, target_family="corolla-hf", timeout=0.15)
        except host.UnifiedSignerError:
            pass
        else:
            raise AssertionError(f"current-angle guard accepted {label}")
    check("unified current-angle guard rejects wheel faults and non-Park Corolla state", True)

    try:
        host.verify_ready_stationary_current_angle(GuardPanda(stale=True), target_family="corolla-hf", timeout=0.15)
    except host.UnifiedSignerError:
        pass
    else:
        raise AssertionError("current-angle guard accepted stale wheel/angle samples")
    check("unified current-angle guard rejects stale motion/angle samples", True)

    # Application diagnostics can be briefly unavailable while the replayed application
    # settles. Normalize that into a bounded retry instead of leaking a raw UDS timeout.
    meta, camry_meta_path = built["camry-8965F3307000"]
    camry_bundle = host.load_bundle(camry_meta_path)
    read_attempts = iter((TimeoutError("startup transient"), camry_bundle.resident))
    def flaky_read(*_args, **_kwargs):
        value = next(read_attempts)
        if isinstance(value, Exception):
            raise value
        return value
    class RetryClient:
        def __init__(self): self.sessions = []
        def diagnostic_session_control(self, session): self.sessions.append(session)
    class RetryUds:
        class SESSION_TYPE:
            EXTENDED_DIAGNOSTIC = 3
    retry_client = RetryClient()
    with mock.patch.object(host, "_read_memory", side_effect=flaky_read):
        retried = host._read_memory_retry(retry_client, RetryUds, 0xFEBFF9F0, len(camry_bundle.resident),
                                          label="fixture resident", timeout=0.2)
    check("resident readback retries startup DCM reset by re-entering extended session",
          retried == camry_bundle.resident and retry_client.sessions == [3])

    damaged = bytearray(camry_bundle.resident); damaged[7] ^= 1
    try:
        host._resident_attestation(camry_bundle, bytes(damaged))
    except host.UnifiedSignerError as exc:
        mismatch_text = str(exc)
    else:
        raise AssertionError("Camry resident attestation accepted a byte mismatch")
    check("Camry resident mismatch reports hashes and first differing offset",
          "observed_sha256=" in mismatch_text and "expected_sha256=" in mismatch_text and
          "first_offset=0x7" in mismatch_text)

    # Install is not complete merely because the application answers F181. For split
    # targets it must cross count 224, arm, read the full helper back, and re-attest
    # the high resident before bringup is allowed to prompt for READY.
    session = object.__new__(host.Session)
    session.bundle = camry_bundle
    session.client = object(); session.uds_mod = object()
    state0 = {"initialized": False, "armed": False}
    state1 = {"initialized": True, "armed": True}
    session.split_state = mock.Mock(side_effect=(state0, state1))
    helper_base = int(camry_bundle.meta["helper"]["base"], 0)
    resident_base = int(camry_bundle.meta["resident"]["base"], 0)
    def installed_read(_client, _uds, address, size, **_kwargs):
        if address == helper_base:
            return camry_bundle.helper_image
        if address == resident_base:
            return camry_bundle.resident
        raise AssertionError(f"unexpected self-install read 0x{address:X}/0x{size:X}")
    with mock.patch.object(host, "_read_memory_retry", side_effect=installed_read):
        self_install = session.wait_self_install(timeout=0.2)
    check("split install gate requires armed state, byte-exact helper, and post-boundary resident",
          self_install["state"] == state1 and self_install["helper"]["byte_exact"] is True and
          self_install["resident_attestation"]["byte_exact"] is True and session.split_state.call_count == 2)

    # Corolla startup intentionally reuses the one-shot resident prefix as state/scratch.
    # Attestation must therefore pin the immutable foreground suffix plus live state magic,
    # not compare the mutable prefix against the pristine build image.
    _, corolla_meta_path = built["corolla-8965F1208000"]
    corolla_bundle = host.load_bundle(corolla_meta_path)
    observed = bytearray(corolla_bundle.resident)
    immutable_offset = int(corolla_bundle.meta["layout"]["foreground_entry"], 0) - int(corolla_bundle.meta["resident"]["base"], 0)
    observed[:immutable_offset] = bytes([0xA5]) * immutable_offset
    observed[0:4] = host.COROLLA_STATE_MAGIC.to_bytes(4, "little")
    attestation = host._resident_attestation(corolla_bundle, bytes(observed))
    check("Corolla resident attestation accepts mutable startup prefix and pins immutable foreground",
          attestation["mode"] == "mutable-prefix+immutable-foreground" and
          attestation["mutable_prefix_size"] == immutable_offset and attestation["state"]["resident_present"] is True)
    observed[immutable_offset] ^= 1
    try:
        host._resident_attestation(corolla_bundle, bytes(observed))
    except host.UnifiedSignerError:
        pass
    else:
        raise AssertionError("Corolla resident attestation accepted immutable-code mutation")
    check("Corolla resident attestation rejects immutable foreground mutation", True)


print("Unified TSS3 functional B6 signer verification passed.")
