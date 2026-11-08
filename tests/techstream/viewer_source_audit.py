"""Independent Viewer table2 / V_English audit for ECU StandardInfo18."""
from __future__ import annotations
import hashlib
from pathlib import Path
import struct
from tools.techstream.ddb_semantics import records
from tools.techstream.parse_ddb import DDBParser

def expected_viewer_rows(db, strings):
    result = {}
    for ordinal, raw in enumerate(records(db.sections[2])):
        if len(raw) != 12:
            raise ValueError("Viewer table2 must have 12-byte rows")
        string_index, help_id, kind = struct.unpack_from("<IIH",raw)
        if kind != 3:
            continue
        text = strings.get_string(string_index)
        row = {"source":"Viewer.ddb","namespace":"viewer","table":2,
               "record":ordinal,"raw":raw.hex(),"help_id":help_id,"kind":kind,
               "string_index":string_index,"string_source":"V_English.ddb",
               "text":text,"translation_available":text is not None}
        result.setdefault(help_id,[]).append(row)
    return result

def audit_viewer_rows(catalog, expected_rows, expected_identity):
    errors = []
    identity = catalog.get("source_identity",{}).get("viewer_help")
    if identity != expected_identity:
        errors.append("Viewer source identity path/hash/bytes differs from actual files")
    for row in catalog.get("work_factor",{}).get("standard_info",[]):
        label = f"StandardInfo18 record {row['record']}"
        try:
            help_id = struct.unpack_from("<I",bytes.fromhex(row["raw"]))[0]
        except (KeyError,ValueError,struct.error):
            errors.append(label+": invalid ECU source bytes")
            continue
        if row.get("help_id") != help_id:
            errors.append(label+": help_id differs from ECU source")
        expected = expected_rows.get(help_id,[]) if help_id else []
        actual = row.get("standard_value_help_records",[])
        fields = ("source","namespace","table","record","raw","help_id","kind",
                  "string_index","string_source","text","translation_available")
        if [{k:r.get(k) for k in fields} for r in actual] != expected:
            errors.append(label+": Viewer source records/namespace/text/order differ")
        selected = expected[-1] if expected else None
        status = ("not_specified" if not help_id else "help_not_found" if selected is None
                  else "translation_unavailable" if selected["text"] is None else "resolved")
        text = selected["text"] if selected else None
        if row.get("standard_value_status") != status:
            errors.append(label+": incorrect standard_value_status")
        if row.get("standard_value") != text:
            errors.append(label+": standard_value is not last matching Viewer kind3 text")
    return errors

class ViewerSourceAuditor:
    def __init__(self, root):
        self.root = Path(root)
        self.parser = DDBParser()
        self.cache = {}

    def audit(self, catalog, region):
        if not any(s["table"] == 18 for s in catalog["source_tables"]):
            return []
        identity = catalog.get("source_identity",{}).get("viewer_help")
        if not isinstance(identity,dict):
            return ["Viewer source identity missing for StandardInfo18"]
        try:
            db_path = Path(identity["database"]["path"])
            text_path = Path(identity["strings"]["path"])
        except (KeyError,TypeError):
            return ["Viewer source identity malformed"]
        if (not db_path.parts or not text_path.parts or
            db_path.is_absolute() or text_path.is_absolute() or
            ".." in db_path.parts or ".." in text_path.parts or
            db_path.parts[0] != region or text_path.parts[0] != region or
            db_path.name != "Viewer.ddb" or text_path.name != "V_English.ddb" or
            db_path.parent != text_path.parent):
            return ["Viewer source identity uses wrong region or string namespace"]
        key = str(db_path),str(text_path)
        if key not in self.cache:
            expected_identity = {}
            for name,relative in (("database",db_path),("strings",text_path)):
                data = (self.root/relative).read_bytes()
                expected_identity[name] = {"path":str(relative),"bytes":len(data),
                                           "sha256":hashlib.sha256(data).hexdigest()}
            rows = expected_viewer_rows(self.parser.parse_viewer_db(self.root/db_path),
                                        self.parser.load_string_db(self.root/text_path))
            self.cache[key] = rows,expected_identity
        return audit_viewer_rows(catalog,*self.cache[key])
