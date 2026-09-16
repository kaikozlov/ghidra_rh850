#!/usr/bin/env python3
"""Verify the parallel unified functional-0x777 TSS3 signer implementation."""
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
    "camry-8965F3307000": ("0xFEBE5751", "split-functional-loader", 522, 596, 600, "supervised-continuous", 7),
    "corolla-8965H1202000": ("0xFEBE563D", "embedded-helper-functional-control", 522, 458, 458, "supervised-continuous", 7),
    "corolla-8965F1208000": ("0xFEBE563D", "embedded-helper-functional-control", 522, 458, 458, "supervised-continuous", 7),
    "crown-8965F3012000": ("0xFEBE527D", "split-functional-loader", 522, 596, 600, "supervised-continuous", 7),
}

# This intentionally supersedes yesterday's live-corrected one-shot Crown
# helper while preserving its functional-0x777 DCM geometry. The new split
# helper carries the same seven-tick host-loss lease as the road-proven Camry
# supervised runtime.
CROWN_SUPERVISED_UNIFIED_SHA256 = {
    "resident": "6942f152a698d2656848727a2c0624c3dd4c5a7e820524a70c389ddf0f18a417",
    "helper": "962f55958aa681904f89824e8e289efd55f062457c6ea2aafbb51c2ca0ab8345",
    "helper_image": "35aa8d097410d3a6847f6427c4aacc6a137f88aac7aaeac3bce05f356b5addaa",
    "payload": "90b3b2e27b238bcf26d96d5cab735d0e792c3a1e603c30db208ca943422e132a",
    "staging": "a62a3a580b079a8f5e8bc28f804686c50848be0bdf819d520b210c36d82ba74e",
}


def check(label: str, condition: object) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[PASS] {label}")


check("unified wire frames exact",
      host.loader_frame(3, bytes.fromhex("11223344")) == bytes.fromhex("07c6c60311223344") and
      host.loader_frame(0xFF) == bytes.fromhex("07c6c6ff00000000") and
      host.replacement_frame(7, 0x1234) == bytes.fromhex("07c7c70712340000") and
      host.release_frame() == bytes.fromhex("07c7c70000000000"))
post_replace_raw = bytearray(host.SPLIT_TELEMETRY_SIZE)
post_replace_raw[8:12] = bytes.fromhex("d4a561f5")
post_replace_raw[12:16] = bytes.fromhex("11223344")
post_replace_raw[17] = 1
post_replace = host.decode_split_telemetry(bytes(post_replace_raw))
check("unified split telemetry distinguishes sticky oracle from latest trailer equality",
      post_replace["oracle_latched"] is True and post_replace["native_verified"] is True and
      post_replace["latest_trailer_equality"] is False and post_replace["native_signature_match"] is False)
check("legacy target-specific implementations remain in tree",
      all((ROOT / p).is_file() for p in (
          "exploit/ephemeral_runtime/build_camry_f33_b6_inline_signer.py",
          "exploit/ephemeral_runtime/build_corolla_hf_b6_inline_signer.py",
          "exploit/ephemeral_runtime/build_crown_f30_b6_inline_signer.py",
          "exploit/ephemeral_runtime/camry_f33_b6_inline_signer.py",
          "exploit/ephemeral_runtime/corolla_hf_b6_inline_signer.py",
          "exploit/ephemeral_runtime/crown_f30_b6_inline_signer.py",
      )))

resident_source = (ROOT / "exploit/ephemeral_runtime/tss3_unified_b6_signer_resident.S").read_text()
helper_source = (ROOT / "exploit/ephemeral_runtime/tss3_unified_b6_signer_helper.S").read_text()
check("one maintained resident/helper source covers F3 and Corolla scheduler shapes",
      "#ifdef TSS3_COROLLA_HF" in resident_source and "#ifdef TSS3_COROLLA_HF" in helper_source and
      "TSS3_DCM_TAG_OFF" in resident_source and "TSS3_DCM_TAG_OFF" in helper_source)
check("Camry unified target config uses durable functional DCM tail offsets",
      unified_builder.TARGETS["camry-8965F3307000"]["resident_macros"] == {
          "TSS3_DCM_TAG_OFF": -0x60AE, "TSS3_DCM_INDEX_OFF": -0x60AD, "TSS3_DCM_WORD_OFF": -0x60AC,
      } and unified_builder.TARGETS["camry-8965F3307000"]["helper_macros"]["TSS3_DCM_SEQ_OFF"] == -0x60AD)
check("Corolla unified target config selects common Corolla branch",
      unified_builder.TARGETS["corolla-8965H1202000"]["resident_macros"] == {"TSS3_COROLLA_HF": 1} and
      unified_builder.TARGETS["corolla-8965F1208000"]["helper_macros"] == {"TSS3_COROLLA_HF": 1})
check("Crown unified target config matches live-corrected durable tail offsets",
      unified_builder.TARGETS["crown-8965F3012000"]["resident_macros"] == {
          "TSS3_DCM_TAG_OFF": -0x6582, "TSS3_DCM_INDEX_OFF": -0x6581, "TSS3_DCM_WORD_OFF": -0x6580,
      } and unified_builder.TARGETS["crown-8965F3012000"]["helper_macros"]["TSS3_DCM_SEQ_OFF"] == -0x6581)

built: dict[str, tuple[dict, Path]] = {}
with tempfile.TemporaryDirectory(prefix="verify-tss3-unified-") as td:
    root = Path(td)
    for target, (buffer, strategy, resident_size, helper_size, helper_image_size, runtime_mode, host_loss_ticks) in TARGETS.items():
        out = root / target
        proc = subprocess.run(
            [sys.executable, str(BUILDER), "--target", target, "--output-dir", str(out)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        printed = json.loads(proc.stdout)
        metas = list(out.glob("*.json"))
        check(f"{target}: one unified metadata artifact", len(metas) == 1)
        meta = json.loads(metas[0].read_text())
        check(f"{target}: stdout/meta byte contract", printed == meta)
        check(f"{target}: exact common functional control",
              meta["schema"] == "tss3-unified-b6-signer-build-v1" and
              meta["control"]["can_id"] == "0x777" and meta["control"]["bus"] == 1 and
              meta["control"]["extended"] is False and meta["control"]["dcm_buffer"] == buffer and
              meta["control"]["runtime_frame"] == "07 C7 C7 seq target_hi target_lo 00 00" and
              meta["control"]["runtime_mode"] == runtime_mode and
              meta["control"]["host_loss_ticks"] == host_loss_ticks and
              meta["control"]["release_sequence_zero"] is True and
              meta["control"]["functional_nrc11_suppressed"] is True and
              meta["install_strategy"] == strategy)
        check(f"{target}: bundle uses the single maintained resident/helper sources",
              meta["sources"]["resident"]["path"] == "exploit/ephemeral_runtime/tss3_unified_b6_signer_resident.S" and
              meta["sources"]["helper"]["path"] == "exploit/ephemeral_runtime/tss3_unified_b6_signer_helper.S" and
              meta["compile_macros"]["resident"] == unified_builder.TARGETS[target]["resident_macros"] and
              meta["compile_macros"]["helper"] == unified_builder.TARGETS[target]["helper_macros"])
        check(f"{target}: no persistent target mutation",
              meta["mutation_boundary"] == {
                  "firmware_patch": False, "native_mac_oracle_required": True,
                  "persistent_flash_write": False, "resident_can_transmit": False,
                  "secoc_result_override": False,
              })
        check(f"{target}: resident/helper reproduce reviewed exact sizes",
              meta["resident"]["size"] == resident_size and meta["resident"]["headroom"] == 524 - resident_size and
              meta["helper"]["size"] == helper_size and meta["helper"]["image_size"] == helper_image_size and
              meta["helper"]["headroom"] == meta["helper"]["limit"] - helper_size and
              meta["resident"]["relocations"] == meta["helper"]["relocations"] == 0)
        bundle = host.load_bundle(metas[0])
        p = host.plan(bundle)
        check(f"{target}: unified plan selects functional mailbox first",
              p["sequence"][0].startswith("NRTD/Park: prove exact-target stock functional 0x777") and
              p["old_implementations_retained"] is True)
        if target == "crown-8965F3012000":
            check("Crown unified artifacts pin the supervised functional runtime",
                  meta["artifacts_sha256"] == CROWN_SUPERVISED_UNIFIED_SHA256)
        built[target] = (meta, metas[0])

    check("Corolla H/F unified helpers share the same supervised runtime bytes",
          built["corolla-8965H1202000"][0]["helper"]["sha256"] ==
          built["corolla-8965F1208000"][0]["helper"]["sha256"])

    # Execute the exact compiled Corolla H helper's C7 lease gates in the
    # target Ghidra emulator. This protects continuous 50-Hz host ownership,
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
    with (mock.patch.object(host, "_open_app", return_value=(panda, object(), object(), bundle.target["application_f181_hex"], "fixture", None)),
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
    check("unified field kit packages one exact target and common launcher",
          kit_meta["schema"] == "tss3-unified-b6-signer-kit-v1" and
          kit_meta["target"]["name"] == "crown-8965F3012000" and
          (kit / "tss3-unified-signer").is_file() and (kit / "bundle/unified.json").is_file() and
          (kit / "runtime/tsk/lib/programming.py").is_file())
    launcher = (kit / "tss3-unified-signer").read_text(encoding="utf-8")
    check("unified kit prefers vendored runtime and exposes common test ladder",
          'PYTHONPATH="$KIT_ROOT/runtime:$OPENPILOT_ROOT"' in launcher and
          all(cmd in launcher for cmd in ("preflight", "install", "qualify", "replace-once")))

print("Unified TSS3 functional B6 signer verification passed.")
