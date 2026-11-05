#!/usr/bin/env python3
"""Verify evidence tooling behavior.

Covers the profile-driven Corolla-H evidence extractor (corpus filtering and
merged-source precedence), artifact catalog queries, caller-relative wrapper
paths, the working-project exporter's output guard, and the cross-variant
evidence extraction modes.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from tools import REPO_ROOT
from tools.catalog import artifact_catalog
from tools.techstream import extract_gtsplus_lifecycle_operations as operations_mod
ROOT = REPO_ROOT
VARIANT_TOOL = ROOT / "tools/variants/extract_variant_evidence.py"
EXPORTER = ROOT / "tools/project/export_ghidra_project.sh"
GTS_TOOL = ROOT / "tools/gts"
ARTIFACT_TOOL = ROOT / "tools/artifact"
VARIANT_MODES = ("structural", "function", "application-diagnostics", "reference-census")

import tools.targets.corolla.extract.extract_corolla_h_evidence as mod

import tools.variants.extract_variant_evidence as variant_mod


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


# Preserve the old extractors' distinction between whole JSONL corpora and
# Ghidra function-only corpora. A later non-function record with the same entry
# must not overwrite the function record when the profile requests filtering.
(ROOT / "build/tmp").mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="evidence-tooling-", dir=ROOT / "build/tmp") as td:
    corpus = Path(td) / "fixture.jsonl"
    corpus.write_text(
        json.dumps({
            "record": "function",
            "entry_addr": "0x10",
            "body_size": 4,
            "decompile_completed": True,
            "decompiled_c": "FUNCTION",
        })
        + "\n"
        + json.dumps({
            "record": "metadata",
            "entry_addr": "0x10",
            "body_size": 4,
            "decompile_completed": True,
            "decompiled_c": "NOT_FUNCTION",
        })
        + "\n"
    )
    filtered = mod.load_corpus(corpus, function_records_only=True)
    unfiltered = mod.load_corpus(corpus)
    check(filtered[0x10]["decompiled_c"] == "FUNCTION", "function-only corpus filter is preserved")
    check(unfiltered[0x10]["decompiled_c"] == "NOT_FUNCTION", "unfiltered corpus semantics are preserved")

    # The retired XCP extractor merged command rows first and helper rows
    # second, so a helper-corpus duplicate had to win. Pin that otherwise easy
    # to lose behavior with an intentional overlapping fixture.
    raw = Path(td) / "raw.bin"
    raw.write_bytes(bytes(range(256)) * 0x1000)
    commands = Path(td) / "commands.jsonl"
    helpers = Path(td) / "helpers.jsonl"
    commands.write_text(json.dumps({
        "entry_addr": "10", "body_size": 4, "decompile_completed": True,
        "decompiled_c": "COMMAND_VERSION",
    }) + "\n")
    helpers.write_text(json.dumps({
        "entry_addr": "10", "body_size": 4, "decompile_completed": True,
        "decompiled_c": "HELPER_VERSION",
    }) + "\n")
    overlap_profile = mod.Profile(
        summary="precedence fixture",
        schema="test-v1",
        output="build/tmp/unused.json",
        sources={
            "commands": mod.Source(str(commands.relative_to(ROOT))),
            "helpers": mod.Source(str(helpers.relative_to(ROOT))),
        },
        selections=(mod.Selection(0x10, "commands"),),
        source_format="list",
        row_source_precedence=("commands", "helpers"),
    )
    overlap_payload = mod.build_artifact(
        overlap_profile,
        raw_path=raw,
        source_paths={"commands": commands, "helpers": helpers},
    )
    check(overlap_payload["functions"][0]["decompiled_c"] == "HELPER_VERSION", "merged-corpus later-source precedence is preserved")

# The wrapper must resolve its own environment from the repository root while
# keeping caller-relative artifact paths intact.
with tempfile.TemporaryDirectory(prefix="gts-wrapper-cwd-") as td:
    local_cuw = Path(td) / "local.cuw"
    local_cuw.write_bytes(b"x")
    proc = subprocess.run(
        [str(GTS_TOOL), "cuw", "./local.cuw"], cwd=td, text=True, capture_output=True,
    )
    check(
        proc.returncode != 0 and "truncated CUW header" in proc.stderr,
        "GTS+ query wrapper runs from any cwd and preserves caller-relative artifact paths",
    )

proc = subprocess.run(
    [str(ARTIFACT_TOOL), "show", "camry_8965F3307000_fault_status.json", "--json"],
    cwd=ROOT, text=True, capture_output=True,
)
artifact_row = json.loads(proc.stdout) if proc.returncode == 0 else {}
check(
    proc.returncode == 0
    and artifact_row.get("producers") == ["tools/targets/camry/builders/build_camry_8965F3307000_fault_status.py"],
    "artifact catalog derives producer without a hand-maintained builder list",
)
proc = subprocess.run([str(ARTIFACT_TOOL), "list", "fault_status"], cwd=ROOT, text=True, capture_output=True)
check(proc.returncode == 0 and "camry_8965F3307000_fault_status.json" in proc.stdout, "artifact catalog provides substring discovery")

# Directory ownership includes tracked nested proofs, not siblings or untracked files.
with tempfile.TemporaryDirectory(prefix="artifact-directory-") as td:
    fixture = Path(td)
    producer = "tools/extract_package.py"
    tracked_outputs = [
        "data/generated/package.json",
        "data/generated/package.proofs/first.json",
        "data/generated/package.proofs/nested/second.json",
    ]
    sibling = "data/generated/package.proofs-other/unowned.json"
    untracked = "data/generated/package.proofs/untracked.json"
    (fixture / "tools").mkdir()
    (fixture / producer).write_text(
        'DEFAULT_OUT = REPO_ROOT / "data/generated/package.json"\n'
        'ARTIFACT_OUTPUT_DIR = REPO_ROOT / "data/generated/package.proofs"\n',
        encoding="utf-8",
    )
    for relative in [*tracked_outputs, sibling, untracked]:
        path = fixture / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    subprocess.run(["git", "init", "--quiet", str(fixture)], check=True, capture_output=True)
    subprocess.run(
        ["git", "add", "--force", "--", producer, *tracked_outputs, sibling],
        cwd=fixture, check=True, capture_output=True,
    )
    old_repo = artifact_catalog.REPO
    cached_queries = (
        artifact_catalog._tracked_artifacts,
        artifact_catalog._source_files_cached,
        artifact_catalog._declared_outputs,
        artifact_catalog._producer_candidates,
    )
    try:
        artifact_catalog.REPO = fixture
        for query in cached_queries:
            query.cache_clear()
        check(
            all(artifact_catalog.producer_candidates(path) == [producer]
                for path in tracked_outputs),
            "declared output directory resolves its tracked nested proof producers",
        )
        check(
            artifact_catalog.producer_candidates(sibling) == []
            and artifact_catalog.producer_candidates(untracked) == []
            and untracked not in artifact_catalog.tracked_artifacts(),
            "output directory ownership excludes prefix siblings and untracked files",
        )
    finally:
        artifact_catalog.REPO = old_repo
        for query in cached_queries:
            query.cache_clear()

# Matching duplicate metadata must not attribute recovered code to its installed stub.
with tempfile.TemporaryDirectory(prefix="operation-source-", dir=ROOT / "build/tmp") as td:
    fixture = Path(td)
    source_ref = "DS-4/bin/Protected.dll"
    installed_sha = hashlib.sha256(b"installed stub").hexdigest()
    analysis_sha = hashlib.sha256(b"recovered analysis image").hexdigest()
    record_id, shard_id = "native-proof", "native-proof-shard"
    payload = {"source_ref": source_ref, "source_sha256": installed_sha}
    compressed = gzip.compress(json.dumps({
        "schema": operations_mod.OPERATION_PROOF_SCHEMA,
        "id": shard_id,
        "records": {record_id: payload},
    }).encode(), mtime=0)
    (fixture / "proof.json.gz").write_bytes(compressed)
    family = {
        "native_evidence": {record_id: {
            **payload,
            "proof_location": {
                "shard_id": shard_id, "record_id": record_id,
                "json_pointer": "/records/" + record_id,
            },
        }},
        "bodies": {},
        "native_evidence_shards": [{
            "id": shard_id, "path": "proof.json.gz",
            "sha256": hashlib.sha256(compressed).hexdigest(),
            "size": len(compressed), "record_count": 1,
        }],
    }
    for recovered_admission in (False, True):
        binding = {"installed_sha256": installed_sha}
        if recovered_admission:
            binding["recovered"] = {"sha256": analysis_sha}
        specs = {
            "families.CompiledUtilities": {operations_mod.OPERATION_PROOF_FAMILY: family},
            "admission": {"native": {source_ref: binding}},
            "families.PlatformAdapters": {
                "gts-platform-canonical-source-identities": {"sources": {
                    "protected-source": {
                        "installed": {"path": source_ref, "sha256": installed_sha},
                        "analysis": {"sha256": analysis_sha},
                    },
                }},
            },
        }
        with patch.object(operations_mod, "OPERATION_SPEC_ROOT", fixture):
            try:
                operations_mod._operation_proof_specs(specs, [])
            except ValueError:
                pass
            else:
                raise AssertionError("installed-stub identity admitted for recovered code")
        print(
            "[PASS] native proof source follows "
            + ("recovered admission" if recovered_admission else "canonical owner analysis")
        )

# Canonical family inputs use the same ordered last-definition precedence as the builder.
with tempfile.TemporaryDirectory(prefix="operation-report-", dir=ROOT / "build/tmp") as td:
    fixture = Path(td)
    inputs = []
    for ident, data in (
        ("families.First", {
            operations_mod.OPERATION_PROOF_FAMILY: {"native_evidence_shards": []},
            "provider": {"algorithm": "return 3"},
        }),
        ("families.Second", {"provider": {"algorithm": "return 7"}}),
    ):
        raw = json.dumps({
            "schema": "gtsplus-lifecycle-operations-spec-v1",
            "id": ident, "kind": "families", "data": data,
        }).encode()
        source = fixture / (ident + ".json.gz")
        compressed = gzip.compress(raw, mtime=0)
        source.write_bytes(compressed)
        inputs.append({
            "id": ident, "kind": "families", "path": source.name,
            "size": len(compressed), "sha256": hashlib.sha256(compressed).hexdigest(),
        })
    report = fixture / "report.json.gz"
    report.write_bytes(gzip.compress(json.dumps({
        "diagnostic_operations": {"native_proof_shards": []},
        "operation_contract_inputs": inputs,
    }).encode(), mtime=0))
    restored = operations_mod.load_operation_report(report)
    check(
        restored["diagnostic_operations"]["shared_family_contracts"]["provider"]
        == {"algorithm": "return 7"},
        "retained operation contracts preserve ordered provider-definition precedence",
    )
    source.write_bytes(gzip.compress(raw.replace(b"return 7", b"return 9"), mtime=0))
    try:
        operations_mod.load_operation_report(report)
    except ValueError as exc:
        check("input drift" in str(exc), "changed canonical evidence is rejected before use")
    else:
        raise AssertionError("operation report accepted a changed canonical provider")

provider_family = {
    "caller": {
        "dependencies": [{
            "id": "provider.method",
            "artifact": "provider",
            "kind": "native-provider-reference",
        }, {
            "contract_id": "provider.method",
            "artifact": "provider",
            "kind": "native-provider-reference",
        }, {
            "id": "provider.method",
            "artifact": "provider",
            "types": ["CDrsMonSettingInfo", "CDrsMonStopInfo"],
            "scope": "Payload provider",
        }, {
            "id": "provider.method",
            "artifact": "provider",
            "selector": ["contracts", {"id": "provider.method"}],
            "body_sha256": "source-body-digest",
        }, {
            "id": "provider.method",
            "artifact": "provider",
            "name": "Method",
            "proof_artifact": "provider-proof",
            "source_sha256": "source-digest",
            "status": "source-qualified",
            "va": "0x10001000",
        }, {
            "id": "provider.method",
            "artifact": "provider",
            "binding": "First row for the selected ECU.",
        }, {
            "id": "provider.method",
            "artifact": "provider",
            "join": "Use the canonical serializer.",
            "source_sha256": "source-digest",
        }, {
            "id": "provider.method",
            "artifact": "provider",
            "kind": "value-lifecycle",
            "obligation": "Initialize the caller's stack value.",
            "product": "DS-4",
        }, {
            "contract": "provider.method",
            "artifact": "provider",
            "abi": "int Method(unsigned key)",
            "owner": "Provider",
            "source_sha256": "source-digest",
            "va": "0x10001000",
        }],
        "source_identity": {"id": "provider.method", "sha256": "source-digest"},
        "facet_reference": {
            "id": "provider.method", "artifact": "provider", "facet": "/methods/0x10001000",
        },
        "source_method_tuple": {
            "contract_id": "provider.method",
            "native_entry": "0x10001000",
            "source_sha256": "source-digest",
        },
        "public_entry_join": {
            "contract_id": "provider.method",
            "actual_public_contract_id": "provider.method",
            "ordinal": 1,
            "symbol": "Method",
            "VA": "0x10001000",
        },
        "exports": [{
            "id": "provider.interface",
            "name": "Method",
            "ordinal": 1,
            "va": "0x10001000",
            "rva": "0x1000",
            "source_sha256": "source-digest",
            "abi": {"convention": "stdcall", "stack_bytes": 4},
            "contract": "provider.method",
            "evidence": {"instructions": "provider-proof#/functions/10001000"},
            "virtual_dispatch": {"slot": "0x4c", "target_va": "0x10002000"},
            "critical_section_10028838": False,
        }],
        "typed_joins": [{
            "id": "provider.method",
            "artifact": "provider",
            "ABI": {"writer": "WriteTable(slot14)"},
        }],
        "typed_engine_callee_join": {
            "contract_id": "provider.method",
            "artifact": "provider",
            "complete_local_methods": {"Dispatch": "0x1000e850"},
            "native_proof": "provider-proof",
        },
        "canonical_joins": [{
            "id": "provider.method",
            "artifact": "provider",
            "VAs": ["0x10001000"],
            "purpose": "Call the existing provider.",
            "qualified_children": [{
                "id": "provider.child",
                "kind": "native-body",
                "native_evidence_ref": "proof.child",
            }],
            "qualified_value": {
                "contract": "provider.value",
                "artifact": "provider",
                "ABI": "thiscall ctor()",
                "json_pointer": "/variants/DS-4/constructor",
            },
        }],
        "typed_provider_joins": {"private": {"0x10001000": {
            "id": "provider.method",
            "canonical_artifact": "provider",
            "native_target": "0x10001000",
            "actual_business_callers": ["caller.method"],
            "semantic_status": "composed",
        }}},
        "actual_shared_private_provider_joins": [{
            "id": "provider.method",
            "interface_artifact": "provider",
            "interface_snapshot": {"id": "provider.snapshot", "algorithm": "return 8"},
        }],
    },
    "provider": {
        "contracts": [{
            "contract_id": "provider.method",
            "native_entry": "0x10001000",
            "source_sha256": "source-digest",
            "algorithm": "return 7",
        }],
        "exports": [{
            "id": "provider.export_body",
            "name": "NativeMethod",
            "ordinal": 2,
            "contract": "provider.method",
            "abi": {"convention": "stdcall", "stack_bytes": 4},
            "native_body_ref": "provider-proof#/functions/10003000",
            "critical_section_10028838": True,
        }],
    },
}
provider_call = {"id": "caller.method", "provider_contract_id": "provider.method"}
provider_definitions, provider_links = operations_mod._operation_contract_links(
    {}, provider_family, [provider_call],
)
check(
    provider_links[0]["provider_definition_locations"]
    == ["/shared_family_contracts/provider/contracts/0"],
    "provider lookup selects the algorithm rather than reference-only joins",
)
check(
    provider_definitions["provider.child"]
    == ["/shared_family_contracts/caller/canonical_joins/0/qualified_children/0"]
    and provider_definitions["provider.snapshot"]
    == ["/shared_family_contracts/caller/actual_shared_private_provider_joins/0/interface_snapshot"]
    and provider_definitions["provider.value"]
    == ["/shared_family_contracts/caller/canonical_joins/0/qualified_value"]
    and provider_definitions["provider.export_body"]
    == ["/shared_family_contracts/provider/exports/0"],
    "reference traversal retains nested body proxies and algorithm definitions",
)
try:
    operations_mod._operation_contract_links(
        {}, {"caller": provider_family["caller"]}, [provider_call],
    )
except ValueError:
    pass
else:
    raise AssertionError("a provider reference concealed a missing algorithm definition")
print("[PASS] reference-only providers remain unresolved without a definition")
try:
    operations_mod._operation_contract_links(
        {}, provider_family,
        [{"id": "caller.export", "provider_contract_id": "provider.interface"}],
    )
except ValueError:
    pass
else:
    raise AssertionError("an export interface substituted for its selected algorithm")
print("[PASS] export metadata cannot satisfy a semantic provider dependency")

# BUILD_ROOT may be supplied through a symlink. The inventory guard must compare
# canonical paths, and a failed headless preflight must not delete a pre-existing
# output artifact before the shared safety runner has succeeded.
with tempfile.TemporaryDirectory(prefix="exporter-symlink-", dir=ROOT / "build/tmp") as td:
    fixture = Path(td)
    actual = fixture / "actual"
    actual.mkdir()
    linked = fixture / "linked"
    linked.symlink_to(actual, target_is_directory=True)
    project_dir = linked / "work/project"
    (actual / "work/project/rh850_p1me_mapped.rep").mkdir(parents=True)
    fake_home = fixture / "fake-ghidra"
    (fake_home / "support").mkdir(parents=True)
    fake_analyze = fake_home / "support/analyzeHeadless"
    fake_analyze.write_text("#!/bin/sh\nexit 7\n")
    fake_analyze.chmod(0o755)
    inventory_out = linked / "out/inventory.jsonl"
    (actual / "out").mkdir(parents=True)
    inventory_out.write_text("sentinel\n")
    environment = os.environ.copy()
    environment.update({
        "BUILD_ROOT": str(linked),
        "PROJECT_DIR": str(project_dir),
        "GHIDRA_NO_BOOTSTRAP": "1",
        "GHIDRA_HOME": str(fake_home),
    })
    failed_export = subprocess.run(
        [str(EXPORTER), "project-inventory", str(inventory_out)],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    check(failed_export.returncode != 0, "inventory fake-headless failure is surfaced")
    check("refusing inventory output outside" not in failed_export.stderr, "inventory guard accepts canonicalized symlinked build root")
    check(inventory_out.read_text() == "sentinel\n", "failed inventory export preserves prior output")

# Exercise every variant mode on one synthetic image/corpus so the shared
# extraction implementation itself stays pinned.
with tempfile.TemporaryDirectory(prefix="variant-evidence-", dir=ROOT / "build/tmp") as td:
    fixture = Path(td)
    image = bytearray((index * 17 + 5) & 0xFF for index in range(0x100000))
    did_offset = 0x200
    routine_offset = 0x300
    variant_mod.DID.pack_into(image, did_offset, 0xF410, 4, 0x40, 0, 0)
    variant_mod.RID_CB.pack_into(image, routine_offset, 0x0203, 0, 0x80, 0xC0)
    image_path = fixture / "image.bin"
    image_path.write_bytes(image)

    fingerprints = fixture / "fingerprints.jsonl"
    fingerprints.write_text(json.dumps({
        "entry_addr": "40",
        "body_size": 4,
        "instruction_count": 2,
        "mnemonics": ["mov", "ret"],
        "instruction_lengths": [2, 2],
        "conditional_branch_count": 0,
        "unconditional_branch_count": 0,
        "direct_call_target_count": 0,
        "indirect_call_count": 0,
        "return_count": 1,
    }) + "\n")

    corpus = fixture / "corpus.jsonl"
    corpus.write_text("\n".join(json.dumps(row) for row in [
        {
            "entry_addr": "40", "body_size": 4, "decompile_completed": True,
            "decompiled_c": "int a(void) { return TOKEN; }",
        },
        {
            "entry_addr": "80", "body_size": 6, "decompile_completed": True,
            "decompiled_c": "int b(void) { return 2; }",
        },
        {
            "entry_addr": "c0", "body_size": 8, "decompile_completed": True,
            "decompiled_c": "int c(void) { return 3; }",
        },
    ]) + "\n")

    outputs = {name: fixture / f"{name}.json" for name in VARIANT_MODES}
    subprocess.run([
        sys.executable, str(VARIANT_TOOL), "structural",
        "--image", str(image_path), "--fingerprints", str(fingerprints),
        "--software-id", "TEST", "--address", "0x40", "--out", str(outputs["structural"]),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    structural_payload = json.loads(outputs["structural"].read_text())
    check(structural_payload["functions"][0]["body_sha256"] == variant_mod.sha256(bytes(image[0x40:0x44])), "structural mode binds raw body")

    subprocess.run([
        sys.executable, str(VARIANT_TOOL), "function",
        "--image", str(image_path), "--corpus", str(corpus),
        "--software-id", "TEST", "--address", "0x80", "--out", str(outputs["function"]),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    function_payload = json.loads(outputs["function"].read_text())
    check(function_payload["functions"][0]["entry"] == "0x00000080", "function mode selects requested address")
    check(function_payload["functions"][0]["decompiled_c"] == "int b(void) { return 2; }", "function mode preserves decompilation")

    subprocess.run([
        sys.executable, str(VARIANT_TOOL), "application-diagnostics",
        "--image", str(image_path), "--corpus", str(corpus),
        "--did-table", hex(did_offset), "--did-count", "1",
        "--routine-callback-table", hex(routine_offset), "--routine-count", "1",
        "--extra", "0xc0", "--software-id", "TEST", "--out", str(outputs["application-diagnostics"]),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    diagnostic_payload = json.loads(outputs["application-diagnostics"].read_text())
    diagnostic_rows = {row["entry"]: row for row in diagnostic_payload["functions"]}
    check(set(diagnostic_rows) == {"0x00000040", "0x00000080", "0x000000C0"}, "diagnostic mode resolves image callback tables")
    check(diagnostic_rows["0x00000040"]["selection_roles"] == ["rdbi_producer"], "diagnostic mode labels RDBI role")
    check(diagnostic_rows["0x000000C0"]["selection_roles"] == ["extra_helper_or_downstream", "routine_control_callback"], "diagnostic mode preserves overlapping roles")

    subprocess.run([
        sys.executable, str(VARIANT_TOOL), "reference-census",
        "--image", str(image_path), "--corpus", str(corpus),
        "--software-id", "TEST", "--term", "token=TOKEN", "--out", str(outputs["reference-census"]),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    census_payload = json.loads(outputs["reference-census"].read_text())
    check(census_payload["terms"]["token"]["match_count"] == 1, "reference census finds exact substring")
    check(census_payload["terms"]["token"]["matches"][0]["entry"] == "0x00000040", "reference census binds matching function")

    malformed = fixture / "blank-line.jsonl"
    malformed.write_text(json.dumps({"entry_addr": "40"}) + "\n\n")
    try:
        list(variant_mod.iter_corpus(malformed))
    except json.JSONDecodeError:
        pass
    else:
        raise AssertionError("variant corpus parser silently accepted a blank JSONL record")
    print("[PASS] variant corpus parser preserves strict blank-line rejection")

print(
    "verified evidence tooling: corpus filtering, merged-source precedence, "
    "artifact catalog queries, caller-relative wrapper paths, exporter output "
    f"guard, and {len(VARIANT_MODES)} variant evidence modes"
)
