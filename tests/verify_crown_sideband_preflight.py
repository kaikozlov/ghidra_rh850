#!/usr/bin/env python3
"""Offline tests of diagnostic session lifetime and shared preflight RX accounting."""
from __future__ import annotations

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
