"""Verify every StandardInfo source row, Viewer hashes and searchable summaries."""

import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

from tests.techstream.runtime_db_helpers import at_pointer, read_document
from tools.techstream import techstream_paths
from tools.techstream.diag_bundle import DiagnosticBundle
from tools.techstream.diag_product_projection import project_document

bundle = DiagnosticBundle(Path(sys.argv[1]))
db = sqlite3.connect(f"file:{Path(sys.argv[2]).resolve()}?mode=ro", uri=True)
gts_root = techstream_paths.resolve_gts_root()
statuses = Counter()
zero_help = Counter()
text_errors = []
viewer_sources = {}
seen_sources = set()
fts_samples = []
current_member = None
current_catalog = None
current_stored = None
for region, category, itemid, name, detail, member, pointer in db.execute("""
    SELECT i.region,i.category_id,i.id,i.name,i.detail,s.member,s.pointer
    FROM items i JOIN item_sources s ON s.item_id=i.id
    WHERE i.kind='work-factor-standard-info' ORDER BY s.member,i.id"""):
    if member != current_member:
        current_member = member
        current_catalog = bundle.json(member)
        current_stored = read_document(db, member)
    row = at_pointer(current_stored, pointer)
    original = current_catalog["work_factor"]["standard_info"][row["record"]]
    projected = project_document(member, {"work_factor": {"standard_info": [original]}})
    assert projected["work_factor"]["standard_info"][0] == row, (member, pointer)
    status = row["standard_value_status"]
    statuses[region + ":" + status] += 1
    if row["help_id"] == 0:
        assert status == "not_specified" and row["standard_value"] is None
        zero_help[region] += 1
    else:
        assert status == "resolved", (member, row)
        assert name == row["standard_value"], (member, row)
        assert detail == "resolved", (member, detail)
        assert row["standard_value"] == row["standard_value_help_records"][-1]["text"]
        assert all(r["kind"] == 3 for r in row["standard_value_help_records"])
        if "datainconsistency" in name.lower().replace(" ", ""):
            text_errors.append((member, row["record"], row["help_id"], name))
        if region not in {sample["region"] for sample in fts_samples}:
            tokens = re.findall(r"[A-Za-z]{3,}", name)
            if tokens:
                token = tokens[0]
                assert (
                    db.execute(
                        "SELECT count(*) FROM items_fts WHERE rowid=? AND items_fts MATCH ?",
                        (itemid, '"' + token + '"'),
                    ).fetchone()[0]
                    == 1
                )
                fts_samples.append(
                    {"region": region, "item_id": itemid, "term": token, "text": name}
                )
    if member not in seen_sources:
        seen_sources.add(member)
        identity = current_catalog["source_identity"]["viewer_help"]
        # Viewer provenance belongs to the research corpus, not runtime semantics.
        assert "source_identity" not in current_stored
        for label, source in identity.items():
            key = region + ":" + label
            if key not in viewer_sources:
                path = Path(gts_root) / source["path"]
                data = path.read_bytes()
                assert len(data) == source["bytes"]
                assert hashlib.sha256(data).hexdigest() == source["sha256"]
                viewer_sources[key] = source
assert not text_errors, text_errors
assert len(fts_samples) == 3, fts_samples
print(
    json.dumps(
        {
            "statuses": dict(statuses),
            "zero_help_ids": dict(zero_help),
            "unexpected_data_inconsistency_text": text_errors,
            "viewer_sources": viewer_sources,
            "catalogs_with_standard_info": len(seen_sources),
            "fts_samples": fts_samples,
        },
        indent=2,
    )
)
