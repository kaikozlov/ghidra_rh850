import struct
import unittest
from types import SimpleNamespace
from tools.techstream.parse_ddb import Section, TableDataHead
from tools.techstream.gts.variable_drive import variable_drive_catalog

def section(table, rows):
    data=b"".join(rows)
    return Section(TableDataHead(table,0,len(rows),len(data)),0,data)

class VariableDriveTests(unittest.TestCase):
    def test_real_offsets_no_legacy_nibble_program_confusion(self):
        raw=bytearray(92)
        struct.pack_into("<I",raw,32,123)
        struct.pack_into("<3H",raw,62,4,7,0)
        struct.pack_into("<H",raw,68,15)
        struct.pack_into("<H",raw,74,0xabc)
        raw[80:89]=bytes([0x30,1,1,2,0,3,8,3,9])
        phy=bytearray(24)
        struct.pack_into("<iiiHH",phy,0,1,1,0,4,0)
        phy[20]=3
        pattern=bytearray(24)
        struct.pack_into("<H",pattern,0,7)
        comm=struct.pack("<4H4B",9,2,7,11,0x99,1,0,0)
        db=SimpleNamespace(sections={41:section(41,[raw,raw]),38:section(38,[comm]),
            13:section(13,[phy]),12:section(12,[pattern]),15:section(15,[bytes(8)])})
        out=variable_drive_catalog(db,SimpleNamespace(get_string=lambda n:str(n)),"fixture")
        self.assertEqual(len(out["active_tests"]),2)
        active=out["active_tests"][0]
        self.assertEqual(active["request_identifier"],0x30)
        self.assertEqual(active["communication_frame_key"],0xabc)
        self.assertEqual(active["signal_info"]["sign_mode"],3)
        self.assertEqual(active["pattern_match_count"],1)
        self.assertEqual(active["exception_flag"],3)
        self.assertEqual(active["request_encoding"]["operations"]["17"],"pattern_timeout_literal")
        self.assertEqual(out["communication_data"][0]["pid"],0x99)
        self.assertEqual(out["communication_data"][0]["bit_end"],7)

    def test_pid_frame_append_and_service_override(self):
        db=SimpleNamespace(sections={
            55:section(55,[struct.pack("<HH4B",0x1234,0x56,0x78,1,0,0)]),
            60:section(60,[struct.pack("<H2BH2B",123,0x2f,0,99,1,0)])})
        out=variable_drive_catalog(db,None,"fixture")
        self.assertEqual(out["pid_addition_frames"][0]["communication_frame_key"],0x1234)
        self.assertEqual(out["pid_addition_frames"][0]["pid"],0x78)
        self.assertEqual(out["active_test_communication_modes"][0]["service_override"],0x2f)
        self.assertEqual(out["active_test_communication_modes"][0]["active_test_id"],123)

    def test_uninterpreted_ranges_cover_remaining_bytes(self):
        layouts = (
            (38, 12, "communication_data", [(0,10)], [(10,12)]),
            (41, 92, "active_tests", [(20,70),(72,84),(85,89)],
             [(0,20),(70,72),(84,85),(89,92)]),
            (55, 8, "pid_addition_frames", [(0,6)], [(6,8)]),
            (60, 8, "active_test_communication_modes", [(0,3),(4,7)],
             [(3,4),(7,8)]),
        )
        for table, size, field, decoded, unknown in layouts:
            covered = [i for start,end in decoded + unknown for i in range(start,end)]
            self.assertEqual(sorted(covered), list(range(size)))
            for fill in (0, 0xa5):
                with self.subTest(table=table, fill=fill):
                    raw = bytearray(size)
                    for start,end in unknown:
                        raw[start:end] = bytes([fill]) * (end-start)
                    db = SimpleNamespace(sections={table:section(table,[raw])})
                    row = variable_drive_catalog(db,SimpleNamespace(get_string=lambda _: ""), "fixture")[field][0]
                    self.assertEqual(row["uninterpreted_bytes"],
                                     {str(start):raw[start:end].hex() for start,end in unknown})
                    from tools.techstream.diag_product_projection import project_document
                    projected = project_document("catalogs/NA/1.json", {"variable_drive":{field:[row]}})
                    self.assertEqual(projected["variable_drive"][field][0]["uninterpreted_bytes"],
                                     row["uninterpreted_bytes"])

    def test_reject_unknown_geometry(self):
        with self.assertRaises(ValueError):
            variable_drive_catalog(SimpleNamespace(sections={38:section(38,[bytes(11)])}),None,"fixture")

if __name__=="__main__": unittest.main()
