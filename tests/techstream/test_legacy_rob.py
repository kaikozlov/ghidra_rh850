"""Binary layout and native scalar tests independent of the GTS installation."""
import json
import struct
import unittest
from types import SimpleNamespace as NS
from tools.techstream.legacy_rob import legacy_rob_catalog, decode_rob_scalar


def section(table, *rows):
    return NS(header=NS(table_type=table, record_count=len(rows)),
              decoded_record_size=len(rows[0]), decoded_data=b"".join(rows),
              iter_records=lambda: iter(NS(raw=bytes(row)) for row in rows))


def fixture():
    signal = bytearray(96)
    struct.pack_into("<dd", signal, 0, 100.5, -10.5)
    signal[16:22] = "RPM".encode("utf-16le")
    struct.pack_into("<ii", signal, 40, 1000, -100)
    struct.pack_into("<I", signal, 56, 100)
    for off,val in ((64,7),(68,9),(70,4),(72,11),(76,2),(78,3),(80,24)):
        struct.pack_into("<H", signal, off, val)
    signal[84],signal[85],signal[87],signal[90] = 2,1,0x20,1
    phy = bytearray(24)
    struct.pack_into("<iiiHH",phy,0,3,2,10,9,5)
    phy[20],phy[21] = 3,1
    unit = bytearray(12)
    struct.pack_into("<IHH",unit,0,101,5,4)
    pattern = bytearray(24)
    struct.pack_into("<Ii",pattern,0,102,-1)
    struct.pack_into("<H",pattern,12,3)
    support = bytearray(8);support[4:6] = bytes([0x20,2])
    bdid = bytearray(8);bdid[2] = 0x20
    check = bytearray(12);struct.pack_into("<HH",check,0,1,7)
    code = bytearray(28);code[:6] = "ABC".encode("utf-16le")
    struct.pack_into("<IIH",code,12,103,104,0x1234);code[26]=1
    return {13:section(13,phy),14:section(14,pattern),15:section(15,unit),
            42:section(42,code),43:section(43,bdid),44:section(44,support),
            45:section(45,signal),46:section(46,check),59:section(59,signal)}


class LegacyRobTests(unittest.TestCase):
    def project(self, tables=None):
        return legacy_rob_catalog(NS(sections=tables or fixture()),NS(get_string=lambda key:f"text{key}"),"fixture")

    def test_complete_join_and_distinct_modes(self):
        result=self.project();self.assertEqual(len(result["families"]),2)
        one,two=result["families"];self.assertEqual((one["mode"],two["mode"]),(1,2))
        signal=one["signals"][0]
        self.assertEqual((signal["name"],signal["short_name"]),("text100","RPM"))
        self.assertEqual((signal["data_max"],signal["data_min"]),(100.5,-10.5))
        self.assertEqual((signal["graph_max"],signal["graph_min"]),(1000,-100))
        info=signal["physical_variants"][0]
        self.assertEqual((info["sign_mode"],info["decimal_point_count"]),(3,1))
        self.assertEqual(info["units"][0]["name"],"text101")
        self.assertEqual(signal["pattern_display"][0]["value"],-1)
        self.assertEqual(signal["support_rule"],"unconditional")
        self.assertTrue(one["support_queries"][0]["requires_prior_support"])
        self.assertEqual(result["signal_checks"][0]["signal_key"],7)
        self.assertNotIn("signal_checks",one)
        for family in result["families"]:
            for kind in ("behavior_codes","identifiers","support_queries","signals"):
                for row in family[kind]:
                    self.assertTrue(row["raw"])
        self.assertTrue(result["signal_checks"][0]["raw"])
        isolated=self.project({46:fixture()[46]})
        self.assertEqual(isolated["families"],[])
        self.assertEqual(len(isolated["signal_checks"]),1)
        self.assertEqual(one["behavior_codes"][0]["signature"],"ABC")
        self.assertEqual(two["signals"][0]["table"],59)
        json.dumps(result,allow_nan=False)

    def test_cross_byte_scalar_signed_magnitude_and_bounds(self):
        signal=self.project()["families"][0]["signals"][0]
        # bits4..11 of18 10 are0x81: signed magnitude -1 *3 /2 +10 =9.
        self.assertEqual(decode_rob_scalar(bytes.fromhex("1810"),signal),9)
        with self.assertRaises(ValueError):decode_rob_scalar(b"\x18",signal)

    def test_variants_are_not_overwritten(self):
        tables=fixture();phy=tables[13].decoded_data
        tables[13]=section(13,phy,phy)
        self.assertEqual(len(self.project(tables)["families"][0]["signals"][0]["physical_variants"]),2)

    def test_wrong_native_stride_fails(self):
        tables=fixture();tables[45]=section(45,bytes(84))
        with self.assertRaisesRegex(ValueError,"96-byte"):self.project(tables)
