#!/usr/bin/env python3
"""Verify the acquisition -> structure-scanner -> resolver-readiness artifact."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.firmware.p1me_codeflash import P1M_E_CODEFLASH_SIZE  # noqa: E402
from tools.variants.check_variant_acquisition import (  # noqa: E402
    CATALOG_SCHEMA,
    MANIFEST_SCHEMA,
    RUN_SCHEMA,
    SCHEMA,
    AcquisitionReadinessError,
    build_registered_catalog,
    build_report,
    check_acquisition,
    check_resolver_readiness,
    check_structure,
)

FIRMWARE = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
BLOB = FIRMWARE.read_bytes()
import hashlib  # noqa: E402

SHA = hashlib.sha256(BLOB).hexdigest()
passed = failed = 0


def check(label: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {label}{suffix}")


print("== acquisition stage ==")
acq = check_acquisition(FIRMWARE, BLOB, None)
check("canonical firmware passes the geometry gate", acq["geometry_valid"] is True and acq["problems"] == [])
check("acquisition recomputes the canonical SHA-256", acq["sha256"] == SHA and acq["size_bytes"] == P1M_E_CODEFLASH_SIZE)
short = check_acquisition(Path("truncated.bin"), BLOB[:0x80000], None)
check("truncated image fails the geometry gate", short["geometry_valid"] is False and short["size_bytes"] < short["expected_size_bytes"])
concat = check_acquisition(Path("concat.bin"), b"\x00" * 0x8000 + BLOB, None)
check("unstripped concatenation fails the geometry gate", concat["geometry_valid"] is False and concat["size_bytes"] == concat["expected_size_bytes"] + 0x8000)

run_record = {
    "schema": RUN_SCHEMA,
    "image": {"sha256": SHA, "complete": True, "missing_word_count": 0},
    "capture": {"sha256": "0" * 64, "accepted_frames": 262145},
    "resolver": {"status": "resolved"},
    "interrupted": False,
}
bound = check_acquisition(FIRMWARE, BLOB, run_record)
check("run record SHA binding passes for matching bytes", bound["run_record"]["run_sha_matches_bytes"] is True and bound["run_record"]["run_reports_complete"] is True and bound["problems"] == [])
bad_run = dict(run_record)
bad_run["image"] = {"sha256": "f" * 64, "complete": False, "missing_word_count": 4}
mismatch = check_acquisition(FIRMWARE, BLOB, bad_run)
check(
    "run record SHA/completeness disagreement is reported as problems",
    mismatch["run_record"]["run_sha_matches_bytes"] is False
    and mismatch["run_record"]["run_reports_complete"] is False
    and mismatch["problems"] == [
        "run sha256 does not match image bytes",
        "run record does not report a complete acquisition",
    ],
    repr(mismatch["problems"]),
)

print("\n== structure triage stage ==")
structure = check_structure(BLOB)
check("triage stage summarizes the scanner output", structure["schema"] == "rh850-codeflash-structure-triage-v2" and structure["image_sha256"] == SHA)
check("canonical image classifies as bare 1 MiB CodeFlash", structure["geometry"] == "bare-codeflash-1m")
check("Sienna image shows the XCP route/map anchors", structure["xcp_surface"]["command_map_window_count"] >= 1 and structure["xcp_surface"]["request_can_id_immediate_count"] >= 1)
check("Sienna image shows boot-CRC descriptors and RAM-exec anchors", structure["boot_trust"]["crc_descriptor_count"] >= 1 and structure["ram_exec_gate"]["download_window_immediate_count"] >= 1)
check("Sienna image shows resolver prefilter sites", structure["semantic_resolver_prefilter"]["byte_load_then_cmov_site_count"] >= 1)

print("\n== bare-file triage ladder ==")
triage = build_report(FIRMWARE, BLOB, None, None, None)
report_arch = triage["architecture"]
check("canonical architecture decision is high-confidence RH850", report_arch["decision"] == "RH850" and report_arch["confidence"] == "high")
check("container is classified as bare CodeFlash", triage["container_triage"]["classification"] == "bare-codeflash")
check("reset and INTBP agree on load address zero", triage["load_address_vote"]["selected_load_address"] == "0x0" and triage["load_address_vote"]["vote_spread_bytes"] == 0)
check("reset-vector slots hold branch instructions", triage["vector_entries"]["form"] == "jump-instruction" and triage["vector_entries"]["entries"][0]["target"] == "0x1B0")
sienna_tables = {item["address"] for item in triage["uds_table_candidates"]["service_tables"]}
check("known Sienna application and resident UDS tables are recovered", {"0x25E28", "0x8E54"} <= sienna_tables)
sienna_xcp = {item["address"] for item in triage["ccp_xcp_candidates"]["command_table_candidates"]}
check("known Sienna XCP command table is recovered", "0x2B3F0" in sienna_xcp)

camry_path = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
camry = build_report(camry_path, camry_path.read_bytes(), None, None, None)
camry_tables = {item["address"] for item in camry["uds_table_candidates"]["service_tables"]}
check("known Camry application UDS table is recovered", "0x25C54" in camry_tables)
camry_nrc = camry["uds_table_candidates"]["nrc_compare_candidates"]["compare_load_hits"]
check(
    "Camry NRC range compare loads are located",
    {(item["constant"], item["compare_address"]) for item in camry_nrc}
    >= {("0x35", "0x4C93A"), ("0x36", "0x4C93A")},
)

prefixed = build_report(Path("concatenated.bin"), b"\x00" * 0x8000 + BLOB, None, None, None)
check("0x8000 DataFlash prefix is peeled before byte triage", prefixed["container_triage"]["classification"] == "dataflash-prefix-plus-codeflash" and prefixed["architecture"]["decision"] == "RH850")
under_prefix = build_report(Path("short.bin"), BLOB[:0x1000], None, None, None)
check("file under the prefix size remains bounded", under_prefix["container_triage"]["classification"] == "bare-codeflash" and under_prefix["ready"] is False)
erased = build_report(Path("erased.bin"), b"\xFF" * 0x1000, None, None, None)
check("all-FF image is classified without vector over-read", erased["architecture"]["decision"] == "erased-or-empty" and erased["vector_entries"]["form"] == "neither")

crc_fixture = bytearray(b"\xFF" * 0x100)
crc_fixture[0x40:0x50] = bytes.fromhex("00000000963007772c610eeeba510999")
crc = build_report(Path("crc.bin"), bytes(crc_fixture), None, None, None)
check("CRC32 standard table prefix is located", crc["crc_table_constants"]["hits"][0]["table_address"] == "0x40")

registry_path = REPO / "data/analysis_targets.json"
catalog = build_registered_catalog(registry_path)
check(
    "catalog includes exactly the registered targets",
    catalog["schema"] == CATALOG_SCHEMA
    and catalog["targets"].keys() == json.loads(registry_path.read_text())["targets"].keys(),
)
check(
    "registered bases agree with byte-derived votes",
    all(
        int(item["registered"]["codeflash_base"], 16)
        == int(item["readiness"]["load_address_vote"]["selected_load_address"], 16)
        for item in catalog["targets"].values()
    ),
)
check(
    "all registered images retain RH850 byte evidence",
    all(item["readiness"]["architecture"]["decision"] == "RH850" for item in catalog["targets"].values()),
)

print("\n== resolver readiness stage ==")
resolver = check_resolver_readiness(acq, None)
check("geometry-valid acquisition is resolver-ready without a manifest", resolver["ready"] is True and resolver["manifest_bound"] is None)
blocked = check_resolver_readiness(short, None)
check("geometry-invalid acquisition is not resolver-ready", blocked["ready"] is False and "fix acquisition problems" in blocked["next_step"])

good_manifest = {"schema": MANIFEST_SCHEMA, "image": {"sha256": SHA}, "semantic_resolution": {"gate_va": "0x8E6C8"}}
manifest_bound = check_resolver_readiness(acq, good_manifest)
check("manifest SHA binding passes for matching bytes", manifest_bound["manifest_bound"] is True and manifest_bound["ready"] is True and manifest_bound["manifest"]["semantic_resolution_present"] is True)
wrong_manifest = {"schema": MANIFEST_SCHEMA, "image": {"sha256": "e" * 64}, "semantic_resolution": {}}
manifest_refused = check_resolver_readiness(acq, wrong_manifest)
check("manifest SHA mismatch blocks readiness", manifest_refused["manifest_bound"] is False and manifest_refused["ready"] is False)

print("\n== full report and CLI ==")
report = build_report(FIRMWARE, BLOB, run_record, good_manifest, "unit-test provenance note")
check("report ready flag agrees with stages", report["ready"] is True and report["acquisition"]["geometry_valid"] and report["resolver_readiness"]["ready"])

with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    image = temp / "target.bin"
    image.write_bytes(BLOB)
    out = temp / "readiness.json"
    cli = subprocess.run(
        [sys.executable, str(REPO / "tools/variants/check_variant_acquisition.py"), str(image), "-o", str(out), "--notes", "cli"],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    check("CLI exits 0 on a ready artifact", cli.returncode == 0)
    written = json.loads(out.read_text())
    check("CLI artifact matches the report schema and SHA", written["schema"] == SCHEMA and written["acquisition"]["sha256"] == SHA)

    partial = temp / "partial.bin"
    partial.write_bytes(BLOB[:0x1000])
    bad = subprocess.run(
        [sys.executable, str(REPO / "tools/variants/check_variant_acquisition.py"), str(partial)],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    check("CLI exits nonzero on a non-ready artifact", bad.returncode == 1 and json.loads(bad.stdout)["ready"] is False)

    bad_run_path = temp / "run.json"
    bad_run_path.write_text(json.dumps(bad_run))
    schema_refusal = subprocess.run(
        [sys.executable, str(REPO / "tools/variants/check_variant_acquisition.py"), str(image), "--run-json", str(bad_run_path)],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    check("CLI still reports run-record problems through the exit code", schema_refusal.returncode == 1)
    foreign = temp / "foreign.json"
    foreign.write_text(json.dumps({"schema": "something-else"}))
    try:
        from tools.variants.check_variant_acquisition import _load_json
        _load_json(foreign, RUN_SCHEMA, "dumper run record")
    except AcquisitionReadinessError:
        check("foreign run-record schema is rejected", True)
    else:
        check("foreign run-record schema is rejected", False)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
