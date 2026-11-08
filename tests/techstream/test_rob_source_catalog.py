import unittest
from types import SimpleNamespace as NS
from tools.techstream.gts.rob_source_catalog import rob_source_catalog


def section(table,*rows):
    return NS(header=NS(table_type=table,record_count=len(rows)),
              decoded_record_size=len(rows[0]),decoded_data=b"".join(rows),
              iter_records=lambda:iter(NS(raw=bytes(r)) for r in rows))


class RobSourceTests(unittest.TestCase):
    def test_independent_of_live_monitor_layout_and_admission(self):
        # An incompatible old monitor table must not be parsed by ROB projection.
        db=NS(sections={62:section(62,b"x"),163:section(163,bytes(68)),
                        164:section(164,bytes(48),bytes(48))})
        result=rob_source_catalog(db,NS(get_string=lambda key:""),"mixed-protocol",
                                  resolve_variable=lambda key:b"")
        self.assertEqual(len(result["behavior_codes"]),1)
        self.assertEqual(result["behavior_codes"][0]["enabled"],0)
        self.assertEqual(len(result["signals"]),2)
        self.assertEqual([r["record"] for r in result["signals"]],[0,1])
        self.assertEqual(result["signals"][0]["raw"],bytes(48).hex())
