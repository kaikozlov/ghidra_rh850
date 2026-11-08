"""Verify the complete product projection and every indexed semantic path.

Usage: python -m tests.techstream.verify_runtime_candidate BUNDLE DATABASE
       [SUPPLEMENTAL_ROOT]
Research-only source fields are checked by the canonical bundle verifiers,
not required in the shipped product database.
"""

import argparse
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from tests.techstream.runtime_db_helpers import at_pointer
from tools import REPO_ROOT
from tools.techstream.diag_bundle import DiagnosticBundle
from tools.techstream.diag_codec import decompress
from tools.techstream.diag_metadata import restore
from tools.techstream.diag_product_projection import project_document
from tools.techstream.diag_runtime_db import SCHEMA, _json

# Independent source coverage contract. Do not import these sets from the
# projection: that would allow a newly dropped fact to redefine its own test.
DECODED_SOURCE_ROOTS = frozenset(
    {
        "monitor_source",
        "physical_catalog",
        "native_ddr",
        "dtc_source",
        "p6_rob_source",
    "ddr_behavior",
    }
)
RAW_VENDOR_FIELDS = frozenset(
    {
        "raw",
        "raw_variants",
        "source_payload_offset",
        "decoded_offset",
        "catalog_database_path",
        "source_path",
    }
)
PROVENANCE_FIELDS = frozenset(
    {
        "source_identity",
        "plugin_identity",
        "occurrence",
        "selection",
        "provenance",
        "catalog_context",
        "native_context",
        "target_native_query",
    }
)
RESEARCH_DOMAINS = frozenset(
    {
        "selected_plugins",
        "plugins",
        "source_tables",
        "native_context",
        "raw_category_occurrences",
        "raw_role_bindings",
        "category_resolution",
        "category_rows",
        "initial_native_context",
        "managed_identities",
        "recovery_proof",
        "sources",
        "request_id_legend_search",
    }
)


def _coverage_excluded(key, value):
    if key in RAW_VENDOR_FIELDS or key in PROVENANCE_FIELDS:
        return True
    if (
        key == "source"
        and isinstance(value, dict)
        and ("sha256" in value or "identity" in value)
    ):
        return True
    # Query graphs, not arbitrary native/unknown dictionaries.
    if key in {"native", "query", "failure_query", "context"} and isinstance(
        value, dict
    ):
        return "provenance" in value or ("files" in value and "loads" in value)
    return False


def _require_original_facts(original, actual, path):
    """Original-source leaf preservation with exact list order/count and types."""
    assert type(actual) is type(original), ("source type changed", path)
    if isinstance(original, dict):
        for key, value in original.items():
            if _coverage_excluded(key, value):
                continue
            assert key in actual, ("source fact missing", path + (key,))
            _require_original_facts(value, actual[key], path + (key,))
    elif isinstance(original, list):
        assert len(original) == len(actual), ("source membership changed", path)
        for index, (before, after) in enumerate(zip(original, actual)):
            _require_original_facts(before, after, path + (index,))
    else:
        assert original == actual, ("source value changed", path, original, actual)


def assert_original_source_coverage(original, actual, member):
    """Reject decoded-root/unknown-field loss independently of project_document."""
    coverage = Counter()
    if member.startswith("catalogs/"):
        for root in DECODED_SOURCE_ROOTS:
            if root in original:
                assert root in actual, ("decoded source root missing", member, root)
                _require_original_facts(original[root], actual[root], (member, root))
                value = original[root]
                if isinstance(value, list):
                    coverage["root_rows:" + root] += len(value)
                elif isinstance(value, dict):
                    for key, rows in value.items():
                        if isinstance(rows, list):
                            coverage["root_rows:" + root + "." + key] += len(rows)

    def category(before, after, path):
        # Category decoded values are independent scalar facts; nested native
        # binding/query graphs are audited by the research pipeline separately.
        for key, value in before.items():
            if (
                key == "generation_low5"
                and isinstance(after, dict)
                and key not in after
                and type(value) is int
                and type(before.get("generation")) is int
                and value == before["generation"] & 31
                and type(after.get("generation")) is int
                and after["generation"] == before["generation"]
            ):
                continue  # Exact recomputable value, not a semantic omission.
            if isinstance(value, (dict, list)) or _coverage_excluded(key, value):
                continue
            assert isinstance(after, dict) and key in after, (
                "category fact missing",
                path + (key,),
            )
            _require_original_facts(value, after[key], path + (key,))

    if member.startswith("catalogs/") and isinstance(original.get("category"), dict):
        category(original["category"], actual.get("category"), (member, "category"))
    if member == "index.json":
        for region, data in original.get("regions", {}).items():
            for collection in ("selected_categories", "initial_categories"):
                for key, value in data.get(collection, {}).items():
                    after = (
                        actual.get("regions", {})
                        .get(region, {})
                        .get(collection, {})
                        .get(key)
                    )
                    category(value, after, (member, region, collection, key))
    if member.startswith("index.json#"):
        pointer = member.split("#", 1)[1].split("/")
        if len(pointer) == 4 and pointer[3] == "ecu_overlays":
            _require_original_facts(original, actual, (member,))
            coverage["overlay_files"] += len(original)
            coverage["overlay_rows"] += sum(
                len(entry["operation_freeze"]) for entry in original
            )
        if len(pointer) >= 4 and pointer[3] in {
            "selected_categories",
            "initial_categories",
        }:
            if len(pointer) == 5:
                category(original, actual, (member,))
            else:
                for key, value in original.items():
                    category(value, actual.get(key), (member, key))

    def walk(before, after, path):
        if isinstance(before, list):
            for index, value in enumerate(before):
                child = (
                    after[index]
                    if isinstance(after, list) and index < len(after)
                    else None
                )
                walk(value, child, path + (index,))
        elif isinstance(before, dict):
            for key, value in before.items():
                if key in RESEARCH_DOMAINS or _coverage_excluded(key, value):
                    continue
                child = after.get(key) if isinstance(after, dict) else None
                if (
                    key.startswith(
                        ("unknown", "unassigned", "uninterpreted", "unconsumed")
                    )
                    or key == "padding"
                ):
                    assert isinstance(after, dict) and key in after, (
                        "unknown source field missing",
                        path + (key,),
                    )
                    _require_original_facts(value, child, path + (key,))
                    coverage["unknown_containers:" + key] += 1
                else:
                    walk(value, child, path + (key,))

    walk(original, actual, (member,))
    return coverage


def verify_product_database(bundle_path, database_path, supplemental_root=Path(".")):
    bundle = DiagnosticBundle(Path(bundle_path))
    path = Path(database_path)
    with sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True) as db:
        assert (
            db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()[0]
            == SCHEMA
        )
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert not db.execute("PRAGMA foreign_key_check").fetchall()
        manifest = json.loads(
            db.execute(
                "SELECT value FROM meta WHERE key='supplemental_sources'"
            ).fetchone()[0]
        )
        supplemental = {}
        for entry in manifest:
            if entry["status"] != "loaded":
                continue
            root = (
                REPO_ROOT
                if entry.get("path_scope") == "repository"
                else Path(supplemental_root)
            )
            source_path = root / entry["path"]
            data = source_path.read_bytes()
            assert hashlib.sha256(data).hexdigest() == entry["sha256"], source_path
            supplemental[entry["uri"]] = source_path
        refs = defaultdict(list)
        for member, pointer, kind, count in db.execute("""
            SELECT r.member_id,p.pointer,i.kind,count(*)
            FROM item_source_refs r JOIN source_pointers p ON p.id=r.pointer_id
            JOIN items i ON i.id=r.item_id GROUP BY r.member_id,p.pointer,i.kind
        """):
            refs[member].append((pointer, kind, count))
        kinds = Counter()
        source_coverage = Counter()
        documents = parts = 0
        for identity, member in db.execute(
            "SELECT id,member FROM source_documents ORDER BY id"
        ).fetchall():
            original = (
                json.loads(supplemental[member].read_bytes())
                if member in supplemental
                else bundle.json(member)
            )
            expected = project_document(member, original)
            # Validate all indexed paths before replacing large part subtrees.
            for pointer, kind, count in refs.pop(identity, []):
                at_pointer(expected, pointer)
                kinds[kind] += count
            packed = db.execute(
                "SELECT data FROM source_documents WHERE id=?", (identity,)
            ).fetchone()[0]
            actual = restore(db, json.loads(decompress(packed)))
            for pointer, blob in db.execute(
                """
                SELECT p.pointer,s.data FROM source_document_parts s
                JOIN source_pointers p ON p.id=s.pointer_id WHERE s.document_id=?
            """,
                (identity,),
            ):
                part = restore(db, json.loads(decompress(blob)))
                source_coverage.update(
                    assert_original_source_coverage(
                        at_pointer(original, pointer), part, member + "#" + pointer
                    )
                )
                assert _json(part) == _json(at_pointer(expected, pointer)), (
                    "part",
                    member,
                    pointer,
                )
                # Compare root without retaining duplicate expanded index trees.
                parent = at_pointer(expected, pointer.rsplit("/", 1)[0])
                token = pointer.rsplit("/", 1)[1].replace("~1", "/").replace("~0", "~")
                parent[int(token) if isinstance(parent, list) else token] = at_pointer(
                    actual, pointer
                )
                parts += 1
            # Index parts were independently checked above. The top-level root
            # contains part markers, so do not traverse those subtrees twice.
            if member != "index.json":
                source_coverage.update(
                    assert_original_source_coverage(original, actual, member)
                )
            assert _json(actual) == _json(expected), ("document", member)
            del original
            documents += 1
        assert not refs, "index refers to missing documents"
        counts = dict(db.execute("SELECT kind,count(*) FROM items GROUP BY kind"))
        assert dict(kinds) == counts, ("unverified indexed rows", kinds, counts)
        assert db.execute("SELECT count(*) FROM item_source_refs").fetchone()[0] == sum(
            kinds.values()
        )
        return {
            "path": str(path),
            "bytes": path.stat().st_size,
            "integrity": "ok",
            "documents": documents,
            "parts": parts,
            "items": sum(kinds.values()),
            "counts_by_kind": dict(kinds),
            "original_source_coverage": dict(source_coverage),
            "contract": "complete product semantic projection",
            "supplemental_sources": manifest,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("database", type=Path)
    parser.add_argument("supplemental_root", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()
    print(
        json.dumps(
            verify_product_database(args.bundle, args.database, args.supplemental_root),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
