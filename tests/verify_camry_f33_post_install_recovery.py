#!/usr/bin/env python3
"""Offline regression checks for exact-car recovery transport and evidence."""
from __future__ import annotations
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exploit.ephemeral_runtime import camry_f33_post_install_recovery as recovery


class FakePanda:
    replies = []
    closed = False
    safety = []

    @staticmethod
    def list():
        return ["offline-fixture"]

    def __init__(self, *args):
        self.pending = []
        self.sent = []
        self.closed = False
        self.safety = []

    def set_heartbeat_disabled(self):
        pass

    def set_safety_mode(self, *args):
        self.safety.append(args)

    def set_canfd_auto(self, *args):
        pass

    def can_recv(self):
        out, self.pending = self.pending, []
        return out

    def can_send(self, addr, data, bus):
        self.sent.append((addr, data, bus))
        if data[0] < 8:
            self.pending = list(self.replies)

    def close(self):
        self.closed = True


class TestRecovery(unittest.TestCase):
    def test_gts_permission_requires_distance_control_mode(self):
        for mode in range(6):
            for allowed in (False, True):
                for unavailable in (False, True):
                    oracles = {
                        "0x1903": recovery.decode_frc_did(0x1903, bytes.fromhex("621903") + bytes([mode])),
                        "0x1905": recovery.decode_frc_did(0x1905, bytes.fromhex("62190500") + bytes([128 * allowed])),
                        "0x1906": recovery.decode_frc_did(0x1906, bytes.fromhex("6219060080000000") + bytes([128 * unavailable])),
                    }
                    self.assertEqual(recovery.drcc_permission_observed(oracles), mode in (1, 2, 4) and allowed and not unavailable)

    def test_missing_fields_never_mean_no_fault(self):
        for did, required in ((0x1B09, 6), (0x1903, 1), (0x1905, 2), (0x1906, 6)):
            for size in range(required):
                with self.assertRaises(recovery.RecoveryError):
                    recovery.decode_frc_did(did, b"\x62" + did.to_bytes(2, "big") + bytes(size))
        for did, required in ((0x102D, 8), (0x102F, 10)):
            for size in range(required):
                with self.assertRaises(recovery.RecoveryError):
                    recovery.decode_brake_did(did, b"\x62" + did.to_bytes(2, "big") + bytes(size))
        with self.assertRaises(KeyError):
            recovery.drcc_permission_observed({"0x1903": {"control_mode": 1}, "0x1905": {"cruise_control_allowed": True}, "0x1906": {}})

    def test_gts_fault_state_decoders(self):
        frc = recovery.decode_frc_did(0x1B09, bytes.fromhex("621b09010203040506"))
        self.assertEqual(frc["fail_safe_factors"], {"b1a": 1, "b1b": 2, "b2": 3, "c1": 4, "c2": 5, "d1": 6})
        brake_102d = recovery.decode_brake_did(0x102D, bytes.fromhex("62102d0000000000000060"))
        self.assertTrue(brake_102d["fail_status"])
        self.assertTrue(brake_102d["fail_control"])
        brake_102f = recovery.decode_brake_did(0x102F, bytes.fromhex("62102f00000000000000000020"))
        self.assertTrue(brake_102f["eps_communication_open"])

    def test_pending_and_unrelated_reply_do_not_finish_request(self):
        panda = FakePanda()
        panda.replies = [(0x79A, bytes.fromhex(h), 0) for h in (
            "0362180400000000",  # different service still 62; not the test SID14
            "037f197800000000",  # pending for a different service
            "037f147800000000",  # our pending response
            "0154000000000000",
        )]
        self.assertEqual(recovery.isotp_request(panda, 0x792, 0, b"\x14\xff\xff\xff"), b"\x54")

    def test_malformed_single_frame_is_rejected(self):
        panda = FakePanda()
        panda.replies = [(0x79A, b"\x07\x62\x19\x06", 0)]
        with self.assertRaises(recovery.RecoveryError):
            recovery.isotp_request(panda, 0x792, 0, b"\x22\x19\x06")

    def test_multiframe_counter_and_full_payload(self):
        panda = FakePanda()
        panda.replies = [(0x79A, bytes.fromhex(h), 0) for h in ("1009621906008000", "2100000000000000")]
        self.assertEqual(recovery.isotp_request(panda, 0x792, 0, b"\x22\x19\x06"), bytes.fromhex("621906008000000000"))
        self.assertEqual(panda.sent[-1], (0x792, recovery.FLOW_CONTROL, 0))
        panda.replies[1] = (0x79A, bytes.fromhex("2200000000000000"), 0)
        with self.assertRaises(recovery.RecoveryError):
            recovery.isotp_request(panda, 0x792, 0, b"\x22\x19\x06")

    def test_control_domain_restart_is_frc_brake_frc_and_restores_drcc(self):
        panda = FakePanda()
        class Factory:
            @staticmethod
            def list(): return ["offline"]
            def __new__(cls, serial): return panda

        phase = {"value": 0}
        calls = []
        brake_reset_attempts = {"value": 0}
        brake_programming_poll = {"value": 0}
        def respond(_panda, address, bus, pdu, **kwargs):
            calls.append((address, bus, pdu.hex()))
            if pdu == bytes.fromhex("22f181"):
                if address == recovery.EPS_TX:
                    return bytes.fromhex("62f181") + recovery.EXPECTED_EPS_F181
                if address == recovery.FRC_TX:
                    return bytes.fromhex("62f181") + recovery.EXPECTED_FRC_F181
                if address == recovery.BRAKE_TX:
                    if brake_reset_attempts["value"]:
                        brake_programming_poll["value"] += 1
                        self.fail("Brake F181 was polled after reset dispatch")
                    return bytes.fromhex("62f181") + recovery.EXPECTED_BRAKE_F181
            if pdu == bytes.fromhex("1002"):
                return bytes.fromhex("5002003201f4")
            if pdu == bytes.fromhex("1101"):
                if address == recovery.FRC_TX and phase["value"] == 0:
                    phase["value"] = 1
                    return bytes.fromhex("5101")
                if address == recovery.BRAKE_TX and phase["value"] == 1:
                    brake_reset_attempts["value"] += 1
                    phase["value"] = 2
                    raise TimeoutError("Brake reset response intentionally not observed")
                if address == recovery.FRC_TX and phase["value"] == 2:
                    phase["value"] = 3
                    return bytes.fromhex("5101")
                self.fail(f"unexpected reset address=0x{address:03X} phase={phase['value']}")
            if pdu == bytes.fromhex("221b09"):
                return bytes.fromhex("621b09000000000000")
            if pdu == bytes.fromhex("221903"):
                return bytes.fromhex("62190301")
            if pdu == bytes.fromhex("221905"):
                return bytes.fromhex("62190500") + bytes((0x80 if phase["value"] >= 3 else 0x00,))
            if pdu == bytes.fromhex("221906"):
                return bytes.fromhex("6219060080000000") + bytes((0x00 if phase["value"] >= 3 else 0x80,))
            if pdu == bytes.fromhex("22102d"):
                return bytes.fromhex("62102d0000000000000000")
            if pdu == bytes.fromhex("22102f"):
                return bytes.fromhex("62102f00000000000000000000")
            self.fail(f"unexpected request address=0x{address:03X} pdu={pdu.hex()}")

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "restart.json"
            with (patch.dict(sys.modules, {"panda": types.SimpleNamespace(Panda=Factory)}),
                  patch.object(recovery, "isotp_request", side_effect=respond),
                  patch.object(recovery.time, "sleep", return_value=None) as sleep_mock):
                result = recovery.restart_control_domains(output)
            saved = json.loads(output.read_text())

        self.assertEqual(phase["value"], 3)
        self.assertEqual(brake_reset_attempts["value"], 1)
        self.assertEqual(brake_programming_poll["value"], 0)
        fixed_waits = [call.args[0] for call in sleep_mock.call_args_list if call.args]
        self.assertGreaterEqual(fixed_waits.count(recovery.RESET_APP_RETURN_INITIAL_WAIT_SECONDS), 2)
        self.assertGreaterEqual(fixed_waits.count(recovery.DOMAIN_SETTLE_SECONDS), 3)
        self.assertEqual(result["verdict"], "control_domains_restarted_drcc_permission_restored")
        self.assertTrue(result["drcc_permission_observed"])
        self.assertFalse(result["frc_prereset"]["security_access_used"])
        self.assertFalse(result["brake_restart"]["security_access_used"])
        self.assertFalse(result["frc_final_restart"]["security_access_used"])
        self.assertFalse(result["after_frc_prereset_fault_state"]["frc"]["0x1905"]["cruise_control_allowed"])
        self.assertFalse(result["after_brake_fault_state"]["frc"]["0x1905"]["cruise_control_allowed"])
        self.assertTrue(result["after_frc_fault_state"]["frc"]["0x1905"]["cruise_control_allowed"])
        self.assertFalse(result["after_frc_fault_state"]["frc"]["0x1906"]["acc_not_available_icon"])
        reset_calls = [(addr, pdu) for addr, _bus, pdu in calls if pdu == "1101"]
        self.assertEqual(reset_calls, [
            (recovery.FRC_TX, "1101"),
            (recovery.BRAKE_TX, "1101"),
            (recovery.FRC_TX, "1101"),
        ])
        self.assertEqual(saved["verdict"], result["verdict"])
        self.assertEqual(panda.safety[-1], (recovery.SILENT_SAFETY,))
        self.assertTrue(panda.closed)

    def test_brake_single_domain_has_no_post_reset_diagnostics(self):
        panda = FakePanda()
        class Factory:
            @staticmethod
            def list(): return ["offline"]
            def __new__(cls, serial): return panda

        calls = []
        reset_sent = {"value": False}
        def respond(_panda, address, bus, pdu, **kwargs):
            calls.append((address, bus, pdu.hex()))
            if reset_sent["value"]:
                self.fail(f"post-reset diagnostic sent after Brake 11 01: addr=0x{address:03X} pdu={pdu.hex()}")
            if pdu == bytes.fromhex("22f181") and address == recovery.EPS_TX:
                return bytes.fromhex("62f181") + recovery.EXPECTED_EPS_F181
            if pdu == bytes.fromhex("22f181") and address == recovery.BRAKE_TX:
                return bytes.fromhex("62f181") + recovery.EXPECTED_BRAKE_F181
            if pdu == bytes.fromhex("1002") and address == recovery.BRAKE_TX:
                return bytes.fromhex("5002003201f4")
            if pdu == bytes.fromhex("1101") and address == recovery.BRAKE_TX:
                reset_sent["value"] = True
                raise TimeoutError("response disappears during reset")
            self.fail(f"unexpected request address=0x{address:03X} pdu={pdu.hex()}")

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "brake.json"
            with (patch.dict(sys.modules, {"panda": types.SimpleNamespace(Panda=Factory)}),
                  patch.object(recovery, "isotp_request", side_effect=respond)):
                result = recovery.restart_one_domain("brake", output)
            saved = json.loads(output.read_text())

        self.assertEqual(calls, [
            (recovery.EPS_TX, recovery.EPS_BUS, "22f181"),
            (recovery.BRAKE_TX, recovery.BRAKE_BUS, "22f181"),
            (recovery.BRAKE_TX, recovery.BRAKE_BUS, "1002"),
            (recovery.BRAKE_TX, recovery.BRAKE_BUS, "1101"),
        ])
        self.assertEqual(result["verdict"], "brake_reset_dispatched_no_post_reset_diagnostics")
        self.assertFalse(result["restart"]["application_return_verified"])
        self.assertEqual(result["restart"]["post_reset_diagnostics"], "none")
        self.assertIsNone(result["eps_identity_after"])
        self.assertEqual(saved["verdict"], result["verdict"])
        self.assertTrue(panda.closed)

    def test_exact_control_domain_identity_is_required_before_reset(self):
        panda = FakePanda()
        with patch.object(
            recovery, "isotp_request",
            return_value=bytes.fromhex("62f181") + bytes.fromhex("0142414449440000000000000000000000"),
        ):
            with self.assertRaises(recovery.RecoveryError):
                recovery.read_exact_f181(
                    panda, recovery.BRAKE_TX, recovery.BRAKE_BUS,
                    recovery.EXPECTED_BRAKE_F181, "Brake/EPB",
                )

    def test_failure_preserves_preclear_evidence_and_releases_panda(self):
        panda = FakePanda()
        class Factory:
            @staticmethod
            def list(): return ["offline"]
            def __new__(cls, serial): return panda
        def respond(_panda, address, bus, pdu, **kwargs):
            if pdu == bytes.fromhex("22f181"):
                return bytes.fromhex("62f181") + recovery.EXPECTED_EPS_F181
            if pdu == bytes.fromhex("1902ff"):
                return bytes.fromhex("5902bdc13187ac")
            if pdu == bytes.fromhex("221b09"):
                return bytes.fromhex("621b09010203040506")
            if pdu == bytes.fromhex("221903"):
                return bytes.fromhex("62190301")
            if pdu == bytes.fromhex("221905"):
                return bytes.fromhex("6219050080")
            if pdu == bytes.fromhex("221906"):
                return bytes.fromhex("621906008000000000")
            if pdu == bytes.fromhex("22102d"):
                return bytes.fromhex("62102d0000000000000060")
            if pdu == bytes.fromhex("22102f"):
                return bytes.fromhex("62102f00000000000000000020")
            if pdu == bytes.fromhex("14ffffff"):
                # The durable pre-clear file must precede even the first clear.
                saved = json.loads(output.read_text())
                self.assertEqual(len(saved["pre_clear"]), 11)
                if address == recovery.PHYSICAL_CLEAR[1]:
                    raise TimeoutError("injected mid-clear failure")
                return b"\x54"
            self.fail(f"unexpected request {pdu.hex()}")
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "capture.json"
            with patch.dict(sys.modules, {"panda": types.SimpleNamespace(Panda=Factory)}), patch.object(recovery, "isotp_request", side_effect=respond):
                with self.assertRaises(TimeoutError): recovery.execute(output)
            saved = json.loads(output.read_text())
            self.assertEqual(saved["verdict"], "recovery_failed")
            self.assertEqual(len(saved["pre_clear"]), 11)
            self.assertEqual(len(saved["physical_clear"]), 1)
            self.assertEqual(panda.safety[-1], (recovery.SILENT_SAFETY,))
            self.assertTrue(panda.closed)


if __name__ == "__main__":
    unittest.main()
