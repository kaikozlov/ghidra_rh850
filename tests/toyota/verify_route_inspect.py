#!/usr/bin/env python3
"""Verify local rlog reading and schema inspection without external captures."""
from __future__ import annotations

import bz2
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from struct import pack

import zstandard

# pycapnp exposes SchemaParser from its untyped compiled extension.
from capnp import SchemaParser  # ty: ignore[missing-module-member]

from tools.toyota_support.cli import build_parser
from tools.toyota_support.route_log import load_logreader

LOG_SCHEMA = """
@0x8d7b8d57b6c5a190;
using Car = import "/car.capnp";
struct Event {
  logMonoTime @0 :UInt64;
  union {
    reading @1 :Car.Detail;
    spare @2 :List(Car.Frame);
    %s
  }
}
"""
CAR_SCHEMA = """
@0x897b8d57b6c5a191;
struct Frame {
  detail @0 :Detail;
}
struct Detail {
  enabled @0 :Bool;
}
"""


class RouteInspectTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.flat = self.root / "flat"
        self.nested = self.root / "nested"
        for cereal, car in (
            (self.flat / "cereal", self.flat / "cereal"),
            (self.nested / "openpilot/cereal", self.nested / "opendbc_repo/opendbc/car"),
        ):
            cereal.mkdir(parents=True)
            car.mkdir(parents=True, exist_ok=True)
            (cereal / "log.capnp").write_text(LOG_SCHEMA % "", encoding="utf-8")
            (car / "car.capnp").write_text(CAR_SCHEMA, encoding="utf-8")

        newer = self.root / "future.capnp"
        newer.write_text(LOG_SCHEMA % "future @3 :Void;", encoding="utf-8")
        schema = SchemaParser().load(str(newer), imports=[str(self.flat / "cereal")])
        self.raw = b"".join((
            schema.Event.new_message(logMonoTime=30, reading={"enabled": False}).to_bytes(),
            schema.Event.new_message(logMonoTime=20, future=None).to_bytes(),
            schema.Event.new_message(logMonoTime=10, reading={"enabled": True}).to_bytes(),
        ))
        self.rlog = self.root / "rlog.zst"
        self.rlog.write_bytes(zstandard.ZstdCompressor().compress(self.raw))

    def inspect(self, root: Path, *options: str) -> dict:
        args = build_parser().parse_args([
            "route", "inspect", str(self.rlog), "--openpilot-root", str(root), *options,
        ])
        with redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(args.func(args), 0)
        return json.loads(stdout.getvalue())

    def test_checkout_layouts_and_unobserved_nested_field(self) -> None:
        for root in (self.flat, self.nested, self.nested / "openpilot"):
            with self.subTest(root=root):
                report = self.inspect(root, "--event", "spare", "--field", "detail.enabled")
                self.assertEqual(report["schema_event_types"], ["reading", "spare"])
                self.assertEqual(report["observed_event_types"], {"reading": 2})
                self.assertEqual(report["unrecognized_event_count"], 1)
                self.assertEqual(report["event"], {
                    "name": "spare", "observed_event_count": 0,
                    "schema_type": "list(struct)", "schema_fields": {"detail": "struct"},
                })
                self.assertEqual(report["field"], {"path": "detail.enabled", "schema_type": "bool"})

    def test_undefined_event_and_field(self) -> None:
        with self.assertRaisesRegex(SystemExit, "undefined Cereal event: 'future'"):
            self.inspect(self.flat, "--event", "future")
        with self.assertRaisesRegex(SystemExit, r"undefined Cereal field: spare\.detail\.missing"):
            self.inspect(self.flat, "--event", "spare", "--field", "detail.missing")
        with self.assertRaisesRegex(SystemExit, "--field requires --event"):
            self.inspect(self.flat, "--field", "enabled")

    def test_missing_schema_files(self) -> None:
        with self.assertRaisesRegex(SystemExit, "no cereal/log.capnp"):
            self.inspect(self.root / "missing")
        (self.flat / "cereal/car.capnp").unlink()
        with self.assertRaisesRegex(SystemExit, "no car.capnp"):
            self.inspect(self.flat)

    def test_compressions_sort_and_union_filter(self) -> None:
        reader = load_logreader(self.flat)
        self.assertEqual([event.logMonoTime for event in reader(self.rlog)], [30, 20, 10])
        self.assertEqual([event.logMonoTime for event in reader(self.rlog, only_union_types=True)], [30, 10])
        for name, data in (("rlog", self.raw), ("rlog.bz2", bz2.compress(self.raw))):
            (self.root / name).write_bytes(data)
        for name in ("rlog", "rlog.bz2", "rlog.zst"):
            with self.subTest(name=name):
                events = reader(self.root / name, sort_by_time=True, only_union_types=True)
                self.assertEqual([(event.logMonoTime, event.which()) for event in events], [(10, "reading"), (30, "reading")])

    def test_corrupt_suffix_keeps_readable_events(self) -> None:
        rlog = self.root / "rlog"
        # One framed word containing a list pointer where Event needs a struct.
        rlog.write_bytes(self.raw + pack("<IIQ", 0, 1, 1))
        with self.assertWarnsRegex(RuntimeWarning, "Corrupted events detected"):
            events = list(load_logreader(self.flat)(rlog, only_union_types=True))
        self.assertEqual([event.logMonoTime for event in events], [30, 10])


if __name__ == "__main__":
    unittest.main()
