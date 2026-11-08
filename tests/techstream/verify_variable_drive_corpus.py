"""Account for selected variable-drive/communication rows and rare table presence."""
from collections import Counter
from tools.techstream import techstream_paths
from tools.techstream.diag_bundle import DiagnosticBundle, DEFAULT_BUNDLE
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts.variable_drive import variable_drive_catalog
from tools.techstream.parse_ddb import DDBParser
parser=DDBParser()
base=techstream_paths.gts_db_root(techstream_paths.resolve_gts_root())
index=DiagnosticBundle(DEFAULT_BUNDLE).json("index.json")
for region,regional in sorted(index["regions"].items()):
    root=base.parents[2]/region/"DB"/"Gen"
    strings=_english_strings(parser,root)
    counts=Counter()
    rare=Counter()
    for category in regional["selected_categories"].values():
        filename=category.get("database")
        if not filename: continue
        db=parser.parse_ecu_db(root/filename)
        for table in (17,20,55,60,64):
            if table in db.sections: rare[table]+=db.sections[table].header.record_count
        if not any(table in db.sections for table in (38,41,55,60)): continue
        out=variable_drive_catalog(db,strings,filename)
        for table,field in ((38,"communication_data"),(41,"active_tests"),(55,"pid_addition_frames"),(60,"active_test_communication_modes")):
            expected=db.sections[table].header.record_count if table in db.sections else 0
            assert len(out[field])==expected,(region,filename,table)
            counts[field]+=len(out[field])
            spans = {38:((10,12),),41:((0,20),(70,72),(84,85),(89,92)),
                     55:((6,8),),60:((3,4),(7,8))}[table]
            for row in out[field]:
                raw = row["raw"]
                assert row["uninterpreted_bytes"] == {
                    str(start):raw[start:end].hex() for start,end in spans
                }, (region,filename,table,row["record"])
                counts["unknown_ranges"] += len(spans)
                counts["nonzero_unknown_rows"] += any(
                    any(raw[start:end]) for start,end in spans)
        for row in out["active_tests"]:
            assert row["signal_info"] is not None,(region,filename,row["id"])
            assert row["pattern_match_count"]>0,(region,filename,row["id"])
            assert row["bit_end"]>=row["bit_start"]
            counts["named_active_tests"]+=bool(row["name"])
    print(region,dict(counts),"rare_tables",dict(rare),flush=True)
