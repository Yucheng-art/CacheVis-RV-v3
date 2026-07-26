"""Lifecycle, isolation, and synchronized four-lane session tests."""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig, CacheSimulator
from cachevis_rv.labs.write_policy import (
    MemoryAccess, MemoryAccessKind, WritePolicyComparisonSession,
    WriteTrafficAssumptions, parse_memory_access_trace,
)


TRACE = parse_memory_access_trace("W 0, R 0, W 16")


def make_session(trace=TRACE, config=None):
    return WritePolicyComparisonSession(
        config or CacheConfig(16, 16, 1), trace, WriteTrafficAssumptions(4)
    )


class WritePolicySessionTest(unittest.TestCase):
    def test_lane_order_is_fixed_and_each_step_uses_the_same_access(self):
        session = make_session()
        self.assertEqual(tuple(lane.lane_id for lane in session.lanes),
                         ("wt_wa", "wt_nwa", "wb_wa", "wb_nwa"))
        step = session.step()
        self.assertEqual(tuple(lane.evidence.access for lane in step.lane_steps),
                         (TRACE[0],) * 4)

    def test_each_lane_calls_formal_core_access_exactly_once_per_step(self):
        original = CacheSimulator.access
        calls = []

        def counted(simulator, address, operation="read"):
            calls.append((id(simulator), address, operation))
            return original(simulator, address, operation)

        with patch.object(CacheSimulator, "access", new=counted):
            make_session().step()
        self.assertEqual(len(calls), 4)
        self.assertEqual(len({call[0] for call in calls}), 4)

    def test_step_run_all_reset_and_new_session_are_equivalent(self):
        stepped = make_session()
        stepped.step()
        stepped.run_all()
        all_at_once = make_session()
        all_at_once.run_all()
        self.assertEqual(stepped.steps, all_at_once.steps)
        stepped.reset()
        self.assertEqual(stepped.run_all(), make_session().run_all())

    def test_empty_and_completed_session_semantics_are_explicit(self):
        empty = make_session(())
        self.assertTrue(empty.is_complete)
        self.assertFalse(empty.has_next())
        self.assertEqual(empty.run_all(), ())
        with self.assertRaises(StopIteration):
            empty.step()
        complete = make_session((TRACE[0],))
        complete.run_all()
        self.assertEqual(len(complete.run_all()), 1)
        with self.assertRaises(StopIteration):
            complete.step()

    def test_inputs_are_retained_as_immutable_values_and_public_simulator_is_absent(self):
        config = CacheConfig(16, 16, 1)
        accesses = tuple(TRACE)
        assumptions = WriteTrafficAssumptions(4)
        session = WritePolicyComparisonSession(config, accesses, assumptions)
        session.run_all()
        self.assertIs(session.config, config)
        self.assertEqual(session.accesses, accesses)
        self.assertIs(session.assumptions, assumptions)
        self.assertFalse(hasattr(session, "simulators"))
        self.assertFalse(hasattr(session, "cache"))

    def test_snapshots_are_detached_immutable_and_lane_states_are_independent(self):
        session = make_session((TRACE[0],))
        session.step()
        snapshots = dict(session.get_all_cache_snapshots())
        self.assertNotEqual(snapshots["wt_wa"], snapshots["wt_nwa"])
        self.assertIsInstance(snapshots["wt_wa"], tuple)
        with self.assertRaises(TypeError):
            snapshots["wt_wa"][0] = snapshots["wt_wa"][0]

    def test_address_width_and_unknown_lane_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "address width"):
            make_session((MemoryAccess(MemoryAccessKind.READ, 16),),
                         CacheConfig(4, 4, 1, address_bits=4))
        with self.assertRaisesRegex(ValueError, "unknown"):
            make_session(()).get_cache_snapshot("missing")

    def test_read_ignores_write_allocate_and_wb_nwa_resident_hit_becomes_dirty(self):
        session = make_session(parse_memory_access_trace("R 0, W 0"))
        steps = session.run_all()
        self.assertTrue(all(lane.evidence.allocated for lane in steps[0].lane_steps))
        wb_nwa = steps[1].lane_steps[3].evidence
        self.assertTrue(wb_nwa.cache_hit)
        self.assertTrue(wb_nwa.line_dirty_after)


if __name__ == "__main__":
    unittest.main()
