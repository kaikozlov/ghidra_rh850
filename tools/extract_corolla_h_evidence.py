#!/usr/bin/env python3
"""Compact Corolla-H decompiler corpora into image-bound evidence artifacts.

The profiles in this module replace the former one-file-per-surface extractors.
They deliberately cover only the common operation: select known function rows
from one or more disposable JSONL corpora, bind the decompilation to CodeFlash
bytes, and write the surface's existing JSON schema.  Extractors with dynamic
target discovery or additional semantic joins remain separate tools.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from corolla_h_constants import RAW_DUMP, XCP_ROLE_MAP  # noqa: E402

RAW = RAW_DUMP


@dataclass(frozen=True)
class Source:
    path: str
    boundary: str | None = None
    tolerate_invalid_json: bool = False
    function_records_only: bool = False


@dataclass(frozen=True)
class Selection:
    target: int
    source: str = "default"
    reference: int | None = None


@dataclass(frozen=True)
class Profile:
    summary: str
    schema: str
    output: str
    sources: dict[str, Source]
    selections: tuple[Selection, ...]
    row_format: str = "function"
    include_name: bool = False
    include_source_label: bool = False
    source_format: str = "single"
    boundary_key: str | None = None
    boundary: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
    sort_functions: bool = False
    # Some retired extractors merged multiple corpora before target lookup.
    # Preserve that exact "later source wins" behavior when specified instead
    # of assuming the target is unique to one corpus.
    row_source_precedence: tuple[str, ...] | None = None


def _selections(addresses: list[int], source: str = "default") -> tuple[Selection, ...]:
    return tuple(Selection(address, source) for address in addresses)


PROFILES: dict[str, Profile] = {
    "application-interrupt-bodies": Profile(
        summary="application timer/CAN interrupt bodies",
        schema="corolla-h-application-interrupt-body-evidence-v1",
        output="data/generated/corolla_8965H1202000_application_interrupt_body_decompiler_evidence.json",
        sources={
            "default": Source(
                "build/work/corpora/h_small_adapters_forced.jsonl",
                function_records_only=True,
            )
        },
        selections=_selections([0x5F258, 0x5F294, 0x5F2D0, 0x5FB12, 0x5FB1E, 0x7D240, 0x7EB4E]),
    ),
    "application-transport": Profile(
        summary="residual application CAN/PduR transport bodies",
        schema="corolla-h-application-transport-evidence-v1",
        output="data/generated/corolla_8965H1202000_application_transport_decompiler_evidence.json",
        sources={
            "default": Source(
                "build/work/corpora/h_small_adapters_forced.jsonl",
                "only the five already-identified application transport bodies are compacted",
                function_records_only=True,
            )
        },
        selections=_selections([0x7A382, 0x7A402, 0x7ADC2, 0x7B040, 0x47ADA]),
    ),
    "can-com": Profile(
        summary="changed CAN/COM transport surface",
        schema="corolla-h-can-com-decompiler-evidence-v1",
        output="data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json",
        sources={
            "clean": Source("build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl"),
            "forced": Source(
                "build/work/corpora/h_8965H1202000_can_com_rx_decompilations.jsonl",
                "used only for transport entry points missing from the clean partition; no unrelated forced boundaries are promoted",
            ),
        },
        selections=(
            *_selections([0x3E118, 0x524B8, 0x52F22, 0x53030, 0x58450, 0x58BBC, 0x6418C, 0x77224, 0x7AD8E, 0x7EB10, 0x7EB4E], "clean"),
            *_selections([0x76A3C, 0x78708, 0x789EE, 0x793FE, 0x7A382, 0x7A402, 0x7ADC2, 0x7B040], "forced"),
        ),
        include_name=True,
        include_source_label=True,
        source_format="mapping",
        sort_functions=True,
    ),
    "crypto-residue": Profile(
        summary="seven residual named crypto roles",
        schema="corolla-h-crypto-residue-decompiler-evidence-v1",
        output="data/generated/corolla_8965H1202000_crypto_residue_decompiler_evidence.json",
        sources={
            "clean": Source("build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl"),
            "secoc_app": Source("build/work/corpora/h_8965H1202000_secoc_app_decompilations.jsonl"),
        },
        selections=tuple(
            Selection(reference=reference, target=target, source=source)
            for reference, target, source in [
                (0x70FC, 0x70E0, "clean"),
                (0x68F0C, 0x63244, "secoc_app"),
                (0x68F92, 0x632CA, "secoc_app"),
                (0x68FC2, 0x632FA, "secoc_app"),
                (0x69018, 0x63350, "secoc_app"),
                (0x88302, 0x82702, "secoc_app"),
                (0x88508, 0x82908, "secoc_app"),
            ]
        ),
        row_format="reference-pair",
        include_source_label=True,
        source_format="mapping",
        boundary_key="boundary",
        boundary="seven residual canonical crypto roles only; no neighboring disposable-project boundaries are promoted",
    ),
    "keyless-event-formatter": Profile(
        summary="keyless event-formatter re-audit",
        schema="corolla-h-keyless-event-formatter-evidence-v1",
        output="data/generated/corolla_8965H1202000_keyless_event_formatter_decompiler_evidence.json",
        sources={
            "default": Source(
                "build/work/corpora/h_8965H1202000_keyless_event_formatter_decompilations.jsonl",
                "six target-native functions recovered from the disposable H Ghidra project; downstream verification consumes only this compact image-bound evidence",
            )
        },
        selections=_selections([0x50038, 0x50122, 0x501A6, 0x5031A, 0x50D10, 0x87384]),
        include_name=True,
        boundary_key="boundary",
        boundary="This artifact establishes the H formatter/wrapper/sibling/config helper and AB worker semantics. Reachable output bounds remain a separate deterministic raw-table calculation.",
    ),
    "motor-control": Profile(
        summary="changed motor-control roles",
        schema="corolla-h-motor-control-decompiler-evidence-v1",
        output="data/generated/corolla_8965H1202000_motor_control_decompiler_evidence.json",
        sources={
            "default": Source(
                "build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl",
                "clean disposable H application corpus; no motor entries were forced for this evidence set",
            )
        },
        selections=_selections([0x2E3E8, 0x2E44C, 0x2E780, 0x2EDE6, 0x324D4, 0x32616, 0x33C70, 0x33D60, 0x52DBA, 0x57CEA, 0x57EEE, 0x57FC8, 0x58226]),
        include_name=True,
    ),
    "plausibility-monitor": Profile(
        summary="nine-channel plausibility-monitor family",
        schema="corolla-h-plausibility-monitor-evidence-v1",
        output="data/generated/corolla_8965H1202000_plausibility_monitor_decompiler_evidence.json",
        sources={
            "default": Source(
                "build/work/corpora/h_8965H1202000_decompilations.corrected-context.raw.jsonl",
                tolerate_invalid_json=True,
                function_records_only=True,
            )
        },
        selections=_selections([0x3E118, 0x3E1CA, 0x3E27C, 0x3E42C, 0x3E5DC, 0x3E7CC, 0x3E87A, 0x3E928, 0x3EA16, 0x3EAE8, 0x3ECCC, 0x58450]),
        boundary_key="boundary",
        boundary="H-native channel/aggregate/publisher roles plus generated Rx-dispatch owner; no S operands are transferred",
    ),
    "small-adapters": Profile(
        summary="bounded API, packet-selector, and record-operation adapters",
        schema="corolla-h-small-adapter-evidence-v1",
        output="data/generated/corolla_8965H1202000_small_adapter_decompiler_evidence.json",
        sources={
            "default": Source(
                "build/work/corpora/h_small_adapters_forced.jsonl",
                "only configuration-backed/triage-backed adapter starts compacted; FE veneer experiments are excluded",
                function_records_only=True,
            )
        },
        selections=_selections([0x75168, 0x7517C, 0x7518E, 0x751A0, 0x751B4, 0x751C8, 0x8B69C, 0x8C362, 0x8FA78, 0x8FB8C, 0x903D0, 0x90E22, 0x91B32, 0x8E5E0, 0x8E610, 0x8E640, 0x8E670, 0x8E6A0]),
    ),
    "steering-nested": Profile(
        summary="remaining steering root and nested-command roles",
        schema="corolla-h-steering-nested-evidence-v1",
        output="data/generated/corolla_8965H1202000_steering_nested_decompiler_evidence.json",
        sources={
            "default": Source(
                "build/work/corpora/h_8965H1202000_decompilations.corrected-context.raw.jsonl",
                tolerate_invalid_json=True,
                function_records_only=True,
            )
        },
        selections=_selections([0xC9C16, 0xC9CD2, 0xCB68A, 0xCBE6E, 0xCB8BA, 0xCB9B6, 0xCBA40, 0xCD3CC, 0xCD440, 0xCE974, 0xCEFF8, 0xB8E84, 0xCEDAE, 0xCF028]),
        boundary_key="boundary",
        boundary="remaining steering-role evidence only; target-native roles are bound by caller/callee topology and dataflow, not local byte alignment",
    ),
    "storage-nvm": Profile(
        summary="changed storage/NvM roles",
        schema="corolla-h-storage-nvm-decompiler-evidence-v1",
        output="data/generated/corolla_8965H1202000_storage_nvm_decompiler_evidence.json",
        sources={
            "default": Source(
                "build/work/corpora/h_8965H1202000_storage_nvm_decompilations.jsonl",
                "disposable H corpus with only the three missing storage/NvM entry points forced",
            )
        },
        selections=_selections([0x4A534, 0x5FFBC, 0x610EA]),
        include_name=True,
    ),
    "xcp": Profile(
        summary="XCP command-table residuals",
        schema="corolla-h-xcp-decompiler-evidence-v1",
        output="data/generated/corolla_8965H1202000_xcp_decompiler_evidence.json",
        sources={
            "commands": Source("build/work/corpora/h_8965H1202000_xcp_decompilations.jsonl"),
            "helpers": Source("build/work/corpora/h_8965H1202000_xcp_helpers_decompilations.jsonl"),
        },
        selections=_selections([row[2] for row in XCP_ROLE_MAP], "commands")
        + _selections([0x9227E, 0x92314, 0x9238A, 0x92436, 0x7C390, 0x7C39C, 0x92724], "helpers"),
        include_name=True,
        source_format="list",
        # The retired extractor did rows=load(commands); rows.update(load(helpers)).
        # Keep helper-corpus precedence for every target if the corpora overlap.
        row_source_precedence=("commands", "helpers"),
        boundary_key="boundary",
        boundary="only forced XCP command/helper boundaries are promoted; unrelated disposable-project partitioning is ignored",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_corpus(
    path: Path,
    *,
    tolerate_invalid_json: bool = False,
    function_records_only: bool = False,
) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            if tolerate_invalid_json:
                continue
            raise ValueError(f"invalid JSON in {path}:{line_number}") from None
        if function_records_only and row.get("record") != "function":
            continue
        entry = row.get("entry_addr")
        if entry is not None:
            rows[int(entry, 16)] = row
    return rows


def _source_metadata(profile: Profile, source_paths: dict[str, Path]) -> Any:
    def metadata(name: str) -> dict[str, Any]:
        source = profile.sources[name]
        path = source_paths[name]
        result: dict[str, Any] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path.read_bytes()),
        }
        if source.boundary:
            result["boundary"] = source.boundary
        return result

    if profile.source_format == "single":
        return metadata(next(iter(profile.sources)))
    if profile.source_format == "mapping":
        return {name: metadata(name) for name in profile.sources}
    if profile.source_format == "list":
        return [metadata(name) for name in profile.sources]
    raise ValueError(f"unknown source format: {profile.source_format}")


def build_artifact(
    profile: Profile,
    *,
    raw_path: Path = RAW,
    source_paths: dict[str, Path] | None = None,
) -> dict[str, Any]:
    resolved_sources = (
        {name: ROOT / source.path for name, source in profile.sources.items()}
        if source_paths is None
        else source_paths
    )
    if set(resolved_sources) != set(profile.sources):
        raise ValueError("source override names must exactly match the profile")

    image = raw_path.read_bytes()[:0x100000]
    corpora = {
        name: load_corpus(
            resolved_sources[name],
            tolerate_invalid_json=source.tolerate_invalid_json,
            function_records_only=source.function_records_only,
        )
        for name, source in profile.sources.items()
    }
    merged_rows: dict[int, dict[str, Any]] | None = None
    if profile.row_source_precedence is not None:
        if profile.include_source_label:
            raise ValueError("merged source precedence cannot be combined with source labels")
        if len(set(profile.row_source_precedence)) != len(profile.row_source_precedence):
            raise ValueError("row source precedence contains duplicates")
        unknown = set(profile.row_source_precedence) - set(profile.sources)
        if unknown:
            raise ValueError(f"unknown row source precedence entries: {sorted(unknown)}")
        merged_rows = {}
        for source_name in profile.row_source_precedence:
            merged_rows.update(corpora[source_name])

    functions: list[dict[str, Any]] = []
    for selection in profile.selections:
        row = (
            merged_rows.get(selection.target)
            if merged_rows is not None
            else corpora[selection.source].get(selection.target)
        )
        if not row or not row.get("decompile_completed") or not row.get("decompiled_c"):
            source_description = (
                " merged sources " + " -> ".join(profile.row_source_precedence)
                if profile.row_source_precedence is not None
                else f" source {selection.source}"
            )
            raise ValueError(
                f"missing completed decompilation {selection.target:#x} from{source_description}"
            )
        body_size = int(row["body_size"])
        decompiled = row["decompiled_c"]
        if profile.row_format == "reference-pair":
            record: dict[str, Any] = {
                "reference_entry": f"0x{selection.reference:08X}",
                "target_entry": f"0x{selection.target:08X}",
                "target_reported_body_size": body_size,
                "body_sha256": sha256(image[selection.target : selection.target + body_size]),
                "decompiled_c_sha256": sha256(decompiled.encode()),
                "decompiled_c": decompiled,
            }
        else:
            record = {
                "entry": f"0x{selection.target:08X}",
                "body_size": body_size,
                "body_sha256": sha256(image[selection.target : selection.target + body_size]),
                "decompiled_c_sha256": sha256(decompiled.encode()),
                "decompiled_c": decompiled,
            }
            if profile.include_name:
                record["name"] = row.get("name", f"FUN_{selection.target:08x}")
        if profile.include_source_label:
            record["source_corpus"] = selection.source
        functions.append(record)

    if profile.sort_functions:
        functions.sort(
            key=lambda row: int(
                row["entry"] if "entry" in row else row["target_entry"], 16
            )
        )

    payload: dict[str, Any] = {
        "schema": profile.schema,
        "software_id": "8965H1202000",
        "image": {
            "path": str(raw_path.relative_to(ROOT)),
            "codeflash_size": len(image),
            "codeflash_sha256": sha256(image),
        },
        "functions": functions,
        "function_count": len(functions),
    }
    source_key = "source_corpus" if profile.source_format == "single" else "source_corpora"
    payload[source_key] = _source_metadata(profile, resolved_sources)
    if profile.boundary_key and profile.boundary:
        payload[profile.boundary_key] = profile.boundary
    payload.update(profile.extra)
    return payload


def describe_profiles() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "summary": profile.summary,
            "schema": profile.schema,
            "output": profile.output,
            "sources": [source.path for source in profile.sources.values()],
            "function_count": len(profile.selections),
        }
        for name, profile in sorted(PROFILES.items())
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="list available surface profiles as JSON")
    extract = subparsers.add_parser("extract", help="write one profile's evidence artifact")
    extract.add_argument("profile", choices=sorted(PROFILES))
    extract.add_argument("--out", type=Path, help="override the profile's tracked output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "list":
        print(json.dumps(describe_profiles(), indent=2, sort_keys=True))
        return 0

    profile = PROFILES[args.profile]
    output = args.out or ROOT / profile.output
    payload = build_artifact(profile)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {output}: {payload['function_count']} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
