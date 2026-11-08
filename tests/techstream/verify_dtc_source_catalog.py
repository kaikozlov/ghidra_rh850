"""Installation-dependent native DTC metadata/source conservation."""
import json
from collections import Counter
from tools.techstream.gts.dtc_source_catalog import dtc_source_catalog
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.techstream_paths import resolve_gts_root,gts_db_root
from tools.techstream.gts.ddb import _english_strings


def main():
    parser=DDBParser()
    for region in ("NA","EU","JP"):
        root=gts_db_root(resolve_gts_root(),region)
        strings=_english_strings(parser,root)
        counts=Counter()
        for path in sorted(root.glob("*.ddb")):
            try: db=parser.parse_ecu_db(path)
            except (ValueError,AssertionError): continue
            rows=dtc_source_catalog(db,strings,path.name)
            if rows: counts["databases"]+=1
            for table in (5,65):
                assert sum(r["table"]==table for r in rows)==(
                    db.sections[table].header.record_count if table in db.sections else 0),(path,table)
            json.dumps(rows,allow_nan=False)
            for row in rows:
                counts[row["table"]]+=1
                counts["enabled"]+=int(row["enabled"])
                assert row["enabled"]==(row["enabled_value"]!=0)
        print(region,dict(counts),flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
