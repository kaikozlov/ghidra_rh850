#!/usr/bin/env python3
"""Offline tests of diagnostic session lifetime and shared preflight RX accounting."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.crown.live import crown_f30_sideband_preflight as probe


class Clock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class Panda:
    def __init__(self):
        self.rows = []

    def can_recv(self):
        rows, self.rows = self.rows, []
        return rows

    def set_canfd_auto(self, *args):
        pass


class StaticGenerationSemanticsTests(unittest.TestCase):
    def test_pdu45_generation_is_normal_delivery_generation(self):
        image = (ROOT / 'firmware/crown-8965F3012000/CodeFlash.bin').read_bytes()
        # PDU45 / 0x1DA: raw offset 0x258, length 8, communication flags 0x0C.
        self.assertEqual(image[0x226E0:0x226E8], bytes.fromhex('580200000800000c'))
        flags = image[0x226E7]
        self.assertTrue(flags & 0x04)   # ordinary delivery calls 0x8C212
        self.assertFalse(flags & 0x02)  # secondary callback does not call 0x8C244 for this PDU

        # Ordinary receive/delivery path: SHR 3 exposes original flag bit2 in C,
        # BNC skips the generation update, otherwise pdu_id -> 0x8C212.
        self.assertEqual(image[0x7AFA2:0x7AFAC], bytes.fromhex('83cac9051d3081ff6a12'))
        # Secondary callback path equivalently tests original bit1 before 0x8C244.
        self.assertEqual(image[0x7BBBE:0x7BBC8], bytes.fromhex('82dac9051d3081ff8006'))

        rows = {}
        with (ROOT / 'data/generated/crown-8965F3012000/decompilations.jsonl').open() as fh:
            for line in fh:
                row = json.loads(line)
                if row.get('record') == 'function':
                    rows[int(row['entry_addr'], 16)] = row
        self.assertIn('cVar1 = DAT_febe4e91', rows[0x4B874]['decompiled_c'])
        self.assertIn('FUN_0007a8e6(0x114,0x1d0,4,0,0,&DAT_febe7bb6)', rows[0x4B874]['decompiled_c'])
        self.assertIn("(&DAT_febe4e64)[param_1] + '\\x01'", rows[0x8C212]['decompiled_c'])
        self.assertIn("(&DAT_febe4e64)[param_1 & 0xffff] + '\\x01'", rows[0x8C244]['decompiled_c'])

        # PDU45 is descriptor 40 of the 41 normal application Rx descriptors.
        # Controller-0 starts at descriptor 0/count 41; the generated PDU base is 5.
        self.assertEqual(image[0x218FC:0x21904], bytes.fromhex('0000290000000000'))
        self.assertEqual(int.from_bytes(image[0x21A6C:0x21A70], 'little'), 5)
        self.assertEqual(image[0x22010:0x22018], bytes.fromhex('da01000008000000'))

        # The lower receive matcher maps descriptor index 40 -> PDU 45, then
        # dispatches through module-0's +8 Rx callback to 0x7AEE8.
        self.assertEqual(int.from_bytes(image[0x21CB0:0x21CB2], 'little'), 46)
        self.assertEqual(int.from_bytes(image[0x21CC8:0x21CCC], 'little'), 0x22866)
        self.assertEqual(image[0x2291A:0x2291E], bytes.fromhex('2d00ffff'))
        self.assertEqual(int.from_bytes(image[0x21DFC:0x21E00], 'little'), 0x21D28)
        self.assertEqual(int.from_bytes(image[0x21D30:0x21D34], 'little'), 0x7AEE8)
        self.assertEqual(image[0x7E7C2:0x7E7D4], bytes.fromhex('1d300338630f01006708630f040080ff4e09'))

        # Crown's five generated-COM Tx IDs do not include 0x1DA, so this is
        # not a normal local Tx PDU looping back through generated COM.
        tx = [int.from_bytes(image[0x21E40+i*8:0x21E44+i*8], 'little') & 0x1FFFFFFF for i in range(5)]
        self.assertEqual(tx, [0x30, 0x351, 0x394, 0x4A3, 0x4C8])
        self.assertNotIn(0x1DA, tx)

        # The only SecOC upper-route deliveries are PDU9 (00F), PDU40 (D7),
        # and PDU42 (B6); none can synthesize a delivery to PDU45.
        secoc_routes = [int.from_bytes(image[0x255BA+i*0x50:0x255BC+i*0x50], 'little') for i in range(3)]
        self.assertEqual(secoc_routes, [9, 40, 42])
        self.assertNotIn(45, secoc_routes)

        # Exact driver path: hardware FIFO/buffer readers -> common frame
        # adapter -> receive ring -> foreground drain. These tokens pin the
        # recovered path without requiring Ghidra at test time.
        self.assertIn('FUN_0007fea4(param_1,uVar6 >> 0x10 & 0xff,&puStack_20)', rows[0x7FED0]['decompiled_c'])
        self.assertIn('FUN_0007fea4(param_1,uVar6 >> 0x10 & 0xff,&puStack_20)', rows[0x7FF9C]['decompiled_c'])
        self.assertIn('FUN_0007e1ac', rows[0x7FEA4]['decompiled_c'])
        self.assertIn('FUN_0007e0bc(uVar6,&local_2c)', rows[0x7E1AC]['decompiled_c'])
        self.assertIn('FUN_0007df42(uVar5)', rows[0x7E06A]['decompiled_c'])
        self.assertIn('FUN_0007def0(param_1,&uStack_38)', rows[0x7DF42]['decompiled_c'])
        self.assertIn('FUN_0007e06a()', rows[0x792EE]['decompiled_c'])


class PreflightTests(unittest.TestCase):
    def simulate(self, *, before=115, after=120, opening_rows=(), heartbeat_rows=(), closing_rows=(),
                 duration=5.0, fail_heartbeat=False):
        clock, panda = Clock(), Panda()
        fake_panda = ModuleType('panda')
        fake_panda.Panda = lambda: panda
        uds = SimpleNamespace(SESSION_TYPE=SimpleNamespace(EXTENDED_DIAGNOSTIC=3))
        keepalive_times = []
        read_count = 0

        class Client:
            def __init__(self, tap):
                self.tap = tap
                self.last_request = clock.now

            def diagnostic_session_control(self, session):
                self.last_request = clock.now

            def tester_present(self):
                if fail_heartbeat:
                    raise RuntimeError('simulated diagnostic failure')
                if clock.now - self.last_request >= 5.0:
                    raise RuntimeError('session expired')
                self.last_request = clock.now
                if not keepalive_times:
                    panda.rows.extend(heartbeat_rows)
                # UDS consumes these frames itself, outside the observation loop.
                self.tap.can_recv()
                keepalive_times.append(clock.now)

        def read_memory(client, _uds, address, length):
            nonlocal read_count
            self.assertEqual((address, length), (probe.SIDEBAND_GENERATION_BASE, 1))
            if clock.now - client.last_request >= 5.0:
                raise RuntimeError('session expired')
            client.last_request = clock.now
            read_count += 1
            if read_count == 1:
                panda.rows.extend(opening_rows)
            else:
                panda.rows.extend(closing_rows)
            client.tap.can_recv()
            return bytes([before if read_count == 1 else after])

        with (patch.dict(sys.modules, {'panda': fake_panda}),
              patch.object(probe, 'ensure_boardd_stopped'),
              patch.object(probe, '_import_uds', return_value=uds),
              patch.object(probe, '_make_uds_client', side_effect=lambda tap, *a, **kw: Client(tap)),
              patch.object(probe, '_read_f181', return_value=(probe.EXPECTED_F181_HEX, 'fixture')),
              patch.object(probe, '_read_memory', side_effect=read_memory),
              patch.object(probe.monitor, '_alloutput_mode'),
              patch.object(probe.time, 'monotonic', side_effect=clock.monotonic),
              patch.object(probe.time, 'sleep', side_effect=clock.sleep)):
            result = probe.run(duration)
        return result, keepalive_times

    def test_five_second_window_retains_session_and_existing_stop_result(self):
        result, times = self.simulate()
        self.assertEqual(len(times), 3)
        self.assertLess(max(b - a for a, b in zip([0.0] + times, times)), 2.01)
        self.assertEqual(result['eps_generation']['delta_modulo_256'], 5)
        self.assertEqual(result['observed_1da_counts_by_bus'], {})
        self.assertFalse(result['safe_to_experiment'])
        self.assertEqual(result['verdict'], 'candidate_in_use')

    def test_frame_consumed_only_inside_tester_present_is_not_lost(self):
        result, _ = self.simulate(before=9, after=9,
                                 heartbeat_rows=[(probe.CONTROL_CAN_ID, bytes(8), 1)])
        self.assertEqual(result['observed_1da_counts_by_bus'], {'1': 1})
        self.assertEqual(result['observed_counts_by_bus'], {'1': 1})
        self.assertFalse(result['safe_to_experiment'])

    def test_opening_read_frames_are_also_counted(self):
        result, _ = self.simulate(before=9, after=9,
                                 opening_rows=[(probe.CONTROL_CAN_ID, bytes(8), 1)])
        self.assertEqual(result['observed_1da_counts_by_bus'], {'1': 1})
        self.assertFalse(result['safe_to_experiment'])

    def test_closing_read_frames_are_counted_without_double_counting(self):
        result, _ = self.simulate(before=9, after=9, closing_rows=[
            (probe.CONTROL_CAN_ID, bytes(8), 1), (0x025, bytes(32), 1)])
        self.assertEqual(result['observed_1da_counts_by_bus'], {'1': 1})
        self.assertEqual(result['observed_counts_by_bus'], {'1': 2})
        self.assertEqual(len(result['samples']), 1)
        self.assertFalse(result['safe_to_experiment'])

    def test_tx_returns_are_not_misclassified_as_native_bus_one(self):
        result, _ = self.simulate(before=9, after=9,
                                 heartbeat_rows=[(probe.CONTROL_CAN_ID, bytes(8), 129)])
        self.assertEqual(result['observed_1da_counts_by_bus'], {'129': 1})
        self.assertTrue(result['safe_to_experiment'])

    def test_modulo_counter_delta_is_not_a_rate(self):
        result, _ = self.simulate(before=254, after=3)
        self.assertEqual(result['eps_generation']['delta_modulo_256'], 5)
        self.assertFalse(result['safe_to_experiment'])

    def test_no_target_frames_does_not_mean_no_bus_traffic(self):
        result, _ = self.simulate(before=9, after=9, closing_rows=[(0x025, bytes(32), 1)])
        self.assertEqual(result['observed_1da_counts_by_bus'], {})
        self.assertEqual(result['observed_counts_by_bus'], {'1': 1})

    def test_keepalive_failure_is_not_reported_as_idle(self):
        with self.assertRaisesRegex(RuntimeError, 'diagnostic failure'):
            self.simulate(fail_heartbeat=True)

    def test_maximum_observation_duration_still_maintains_session(self):
        result, times = self.simulate(duration=30.0)
        self.assertGreaterEqual(len(times), 15)
        self.assertLess(max(b-a for a, b in zip([0.0]+times, times)), 2.01)
        self.assertFalse(result['safe_to_experiment'])


if __name__ == '__main__':
    unittest.main()
