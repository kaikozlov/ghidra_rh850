"""Read-only candidate runtime checks; prints reproducible verification JSON."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from urllib.parse import urlparse, unquote
import zlib
from tools import REPO_ROOT
from tools.techstream.diag_bundle import DiagnosticBundle
from tools.techstream.diag_runtime_db import _json

bundle=DiagnosticBundle(Path(sys.argv[1]))
path=Path(sys.argv[2])
db=sqlite3.connect(f"file:{path.resolve()}?mode=ro",uri=True)
assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
counts=dict(db.execute("SELECT kind,count(*) FROM items GROUP BY kind"))
missing=dict(db.execute("SELECT i.kind,count(*) FROM items i LEFT JOIN item_sources s ON i.id=s.item_id WHERE s.item_id IS NULL GROUP BY i.kind"))
assert set(missing)<= {"ecu","vehicle","utility-family"},missing
assert db.execute("SELECT count(*) FROM items i LEFT JOIN item_payloads p ON p.item_id=i.id WHERE p.item_id IS NULL").fetchone()[0]==0
assert db.execute("SELECT count(*) FROM item_sources s LEFT JOIN items i ON i.id=s.item_id WHERE i.id IS NULL").fetchone()[0]==0
manifest=json.loads(db.execute("SELECT value FROM meta WHERE key='supplemental_sources'").fetchone()[0])
documents={}
for entry in manifest:
    if entry["status"]!="loaded": continue
    root=REPO_ROOT if entry.get("path_scope")=="repository" else Path(sys.argv[3]) if len(sys.argv)>3 else Path(".")
    data=(root/entry["path"]).read_bytes()
    assert hashlib.sha256(data).hexdigest()==entry["sha256"]
    documents[entry["uri"]]=json.loads(data)
samples=[]
normalized_samples=[]
for kind,itemid in db.execute("SELECT i.kind,min(i.id) FROM items i JOIN item_sources s ON s.item_id=i.id GROUP BY i.kind"):
    member,pointer,payload=db.execute("SELECT s.member,s.pointer,p.data FROM item_sources s JOIN item_payloads p ON p.item_id=s.item_id WHERE s.item_id=?",(itemid,)).fetchone()
    source=documents[member] if member in documents else bundle.json(member)
    for token in pointer.split("/")[1:]:
        token=token.replace("~1","/").replace("~0","~")
        source=source[int(token)] if isinstance(source,list) else source[token]
    actual=json.loads(zlib.decompress(payload))
    if actual!=source:
        assert actual==json.loads(_json(source)),(kind,member,pointer)
        normalized_samples.append({"kind":kind,"member":member,"pointer":pointer})
    samples.append({"kind":kind,"member":member,"pointer":pointer})
result={"path":str(path),"bytes":path.stat().st_size,"integrity":"ok","items":sum(counts.values()),
    "source_items":db.execute("SELECT count(*) FROM item_sources").fetchone()[0],
    "unsourced_summary_items":missing,"counts_by_kind":counts,
    "supplemental_sources":manifest,"verified_sample_count":len(samples),"samples":samples,"path_normalized_samples":normalized_samples}
print(json.dumps(result,indent=2))
