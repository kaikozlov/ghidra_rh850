"""Installation-dependent full regional source/variable join verification."""
import json
from collections import Counter
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.techstream_paths import resolve_gts_root,gts_db_root
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.gts.master import _master_variable
from tools.techstream.gts.active_test_support import active_test_support_catalog

TABLES={67:"data_id_definitions",69:"support_conditions",70:"panel_support",
        72:"routine_status",73:"display_patterns",78:"description_patterns",
        79:"result_patterns",142:"routine_support_conditions"}


def main():
    parser=DDBParser()
    for region in ("NA","EU","JP"):
        root=gts_db_root(resolve_gts_root(),region)
        master=parser.parse_master_db(root/"Toyota.ddb")
        strings=_english_strings(parser,root)
        counts=Counter()
        for path in sorted(root.glob("*.ddb")):
            try: db=parser.parse_ecu_db(path)
            except (ValueError,AssertionError): continue
            if not any(t in db.sections for t in TABLES): continue
            def resolve(index):
                return bytes.fromhex(_master_variable(master if index>10000 else db,index)["bytes"])
            catalog=active_test_support_catalog(db,strings,path.name,resolve_variable=resolve,
                variable_namespace=lambda index: "Toyota.ddb" if index>10000 else path.name)
            json.dumps(catalog,allow_nan=False)
            counts["databases"]+=1
            for table,name in TABLES.items():
                expected=db.sections[table].header.record_count if table in db.sections else 0
                assert len(catalog[name])==expected,(path,table)
                counts[table]+=expected
                for row in catalog[name]:
                    for key in ("did_variable","mask","reference","pattern","press","pull"):
                        if key in row:
                            assert row[key]["resolved"],(path,table,row["record"],key)
                            counts["resolved_variables"]+=1
                    if table in (69,142):
                        assert row["condition_type"]==7 and row["did_variable"]["length"]==2,row
        print(region,dict(counts),flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
