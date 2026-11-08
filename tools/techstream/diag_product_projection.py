"""Product catalog boundary: diagnostic facts, not a reverse-engineering archive.

Projection is schema-aware. In particular wire bytes, bit offsets, support gates,
unknown/refused states, decoded source collections, uninterpreted field values
and localized descriptions survive. Raw vendor record blobs, query execution
traces and assembly inventories are excluded; decoded fields are not assumed
to be redundant merely because a higher-level diagnostic view exists.
"""

from __future__ import annotations

from typing import Any

CATALOG_RESEARCH_ROOTS = frozenset(
    {
        "selected_plugins",
        "plugins",
        "source_identity",
        "source_tables",
        "native_context",
        "selection_boundary",
    }
)
INDEX_RESEARCH_ROOTS = frozenset({"source_identity", "native_context_request"})
REGION_RESEARCH_FIELDS = frozenset(
    {
        "source_identity",
        "native_context",
        "initial_native_context",
        "raw_catalog_boundary",
        "raw_category_occurrences",
        "raw_role_bindings",
        "category_resolution",
        "category_rows",
    }
)
SUPPLEMENT_RESEARCH_ROOTS = frozenset(
    {"managed_identities", "recovery_proof", "sources", "request_id_legend_search"}
)
# Operational P5 command guards explicitly inspect these two fields.
PLUGIN_GATE_FIELDS = frozenset({"dll", "exact_category_binding"})


def _source_identity(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and ("sha256" in value or "identity" in value)
        and ("path" in value or "source_path" in value or "format_version" in value)
    )


def _query_evidence(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return (
        ("provenance" in value and ("records" in value or "mode" in value))
        or ("context" in value and ("query" in value or "status" in value))
        or (
            "table_type" in value
            and "ordinal" in value
            and ("raw" in value or "identity" in value)
        )
        or ("selector_occurrence" in value and "selector_query" in value)
        or ("files" in value and "loads" in value)
    )


def _category_facts(value: dict[str, Any]) -> dict[str, Any]:
    research = {
        "raw",
        "support_plugin_single",
        "support_plugin_multi",
        "catalog_database_path",
    }
    return {
        key: child
        for key, child in value.items()
        if key not in research
        and not (
            key == "generation_low5"
            and type(value.get("generation")) is int
            and child == (value["generation"] & 31)
        )
    }


def _project(value: Any, path: tuple[str, ...]) -> Any:
    if isinstance(value, list):
        return [_project(child, path + ("[]",)) for child in value]
    if not isinstance(value, dict):
        return value
    result = {}
    category_row = (
        len(path) == 4
        and path[0] == "regions"
        and path[2] in {"selected_categories", "initial_categories"}
    )
    if category_row:
        value = _category_facts(value)
    evidence = value.get("native")
    if isinstance(evidence, dict):
        status = evidence.get("status")
        if status not in (None, 0) and "resolution_status" not in value:
            result["resolution_status"] = status
        reason = evidence.get("reason")
        if isinstance(reason, str) and reason and "resolution_reason" not in value:
            result["resolution_reason"] = reason
    source_row = "record" in value and (
        "table" in value or "did" in value or "encoding_mode" in value
    )
    native_row = "ordinal" in value and "table_type" in value
    transport_frame = "comm_frame_id" in value and "send" in value
    for key, child in value.items():
        # All object-valued native fields in this export schema are research
        # containers. Unknown details inside that container are not product facts.
        if key == "native" and isinstance(child, dict):
            continue
        if path and path[0] == "legacy_records" and key == "native_consumers":
            continue
        if key == "plugin_binding" and isinstance(child, dict):
            result[key] = {
                k: _project(v, path + (key, k))
                for k, v in child.items()
                if k in PLUGIN_GATE_FIELDS
            }
            continue
        if key in (
            "native",
            "occurrence",
            "selection",
            "provenance",
            "context",
            "query",
            "failure_query",
            "native_context",
        ) and (
            _query_evidence(child) or (key == "provenance" and isinstance(child, list))
        ):
            continue
        if key in ("source_identity", "plugin_identity") and isinstance(child, dict):
            continue
        if key == "source" and _source_identity(child):
            continue
        if key == "catalog_context" and isinstance(child, dict):
            continue
        if key in (
            "catalog_database_path",
            "source_path",
            "source_payload_offset",
            "decoded_offset",
        ) and (source_row or native_row or "catalog_member" in value):
            continue
        if key == "raw" and path == (
            "active_test_groups",
            "groups",
            "[]",
            "members",
            "[]",
        ):
            continue
        if key == "raw" and (source_row or native_row or "comm_set_id" in value):
            continue
        if transport_frame and key in ("comm_frame_raw", "func_comm_frame_raw"):
            continue
        if (
            key in ("raw_variants", "native_key", "query_key", "identity")
            and native_row
        ):
            continue
        if (
            key == "string_resolution"
            and isinstance(child, dict)
            and ("source" in child or "status" in child)
        ):
            continue
        # Same retained record still exposes known unsupported status and reason;
        # dropping evidence does not turn a refused operation into an allowed one.
        result[key] = _project(child, path + (key,))
    return result


def _customize_facts(value: Any) -> Any:
    if isinstance(value, list):
        return [_customize_facts(v) for v in value]
    if not isinstance(value, dict):
        return value
    row = dict(value)
    if "source_ordinal" in row:
        row.pop("raw", None)
        evidence = row.pop("target_native_query", None)
        if isinstance(evidence, dict):
            if evidence.get("status") not in (None, 0):
                row.setdefault("target_resolution_status", evidence["status"])
            if isinstance(evidence.get("reason"), str) and evidence["reason"]:
                row.setdefault("target_resolution_reason", evidence["reason"])
    return {k: _customize_facts(v) for k, v in row.items()}


def project_document(member: str, value: dict[str, Any]) -> dict[str, Any]:
    """Return one clean semantic document; callers index ONLY this result.

    Existing retained collection paths and ordering are stable. Removed roots
    have no product search rows. Unknown semantic fields are retained rather
    than guessed away. Concise source/table/record origin is kept when present.
    """
    if not isinstance(value, dict):
        raise ValueError("product document must be an object")
    drop = set()
    if member.startswith("catalogs/") or member.startswith("customize/"):
        drop.update(CATALOG_RESEARCH_ROOTS)
    if member == "index.json":
        drop.update(INDEX_RESEARCH_ROOTS)
    if member.startswith("supplement://"):
        drop.update(SUPPLEMENT_RESEARCH_ROOTS)
    selected = {k: v for k, v in value.items() if k not in drop}
    if member.startswith("catalogs/") and isinstance(selected.get("category"), dict):
        selected["category"] = _category_facts(selected["category"])
    if member.startswith("customize/"):
        selected = _customize_facts(selected)
    result = _project(selected, ())
    if member == "index.json" and isinstance(value.get("regions"), dict):
        result["regions"] = {
            region: _project(
                {k: v for k, v in row.items() if k not in REGION_RESEARCH_FIELDS},
                ("regions", region),
            )
            for region, row in value["regions"].items()
        }
    return result


def retained_pointer(member: str, pointer: str) -> bool:
    """Search retention is path-based: no duplicate research inventory rows."""
    tokens = pointer.split("/")[1:]
    if (
        member.startswith(("catalogs/", "customize/"))
        and tokens
        and tokens[0] in CATALOG_RESEARCH_ROOTS
    ):
        return False
    if (
        member.startswith("supplement://")
        and tokens
        and tokens[0] in SUPPLEMENT_RESEARCH_ROOTS
    ):
        return False
    if member == "index.json":
        if tokens and tokens[0] in INDEX_RESEARCH_ROOTS:
            return False
        if (
            len(tokens) >= 3
            and tokens[0] == "regions"
            and tokens[2] in REGION_RESEARCH_FIELDS
        ):
            return False
    return True
