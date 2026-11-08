import json
import unittest
from tools import REPO_ROOT
from tools.techstream.gts.bundle import _bundle_json_bytes

class BundleSerializationTest(unittest.TestCase):
    def test_portable_nested_plugin_identity_and_stable_json(self):
        value={"plugin":{"source_path":str(REPO_ROOT / "software/plugin.dll"),
                         "identity":"gts:"+str(REPO_ROOT / "software/plugin.dll")+":sha256:abc"},
               "raw":"00ff"}
        raw=_bundle_json_bytes(value)
        self.assertEqual(json.loads(raw),{"plugin":{"source_path":"software/plugin.dll",
            "identity":"gts:software/plugin.dll:sha256:abc"},"raw":"00ff"})
        self.assertEqual(raw,_bundle_json_bytes(dict(reversed(list(value.items())))))
    def test_reject_nonfinite_values(self):
        with self.assertRaises(ValueError):
            _bundle_json_bytes({"value":float("nan")})
