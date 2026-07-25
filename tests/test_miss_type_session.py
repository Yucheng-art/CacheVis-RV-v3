"""Unit tests for synchronized actual/reference miss-type sessions."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.miss_type import (
    CAPACITY_PRESET,
    COMPULSORY_PRESET,
    CONFLICT_PRESET,
    MissType,
    MissTypeSession,
)


def classifications(session):
    return tuple(step.miss_type for step in session.run_all())


class MissTypeSessionTest(unittest.TestCase):
    def test_conflict_demo_exact_classification(self):
        session = MissTypeSession(CONFLICT_PRESET.config, CONFLICT_PRESET.addresses)

        self.assertEqual(classifications(session), CONFLICT_PRESET.expected)

    def test_capacity_demo_exact_classification(self):
        session = MissTypeSession(CAPACITY_PRESET.config, CAPACITY_PRESET.addresses)

        self.assertEqual(classifications(session), CAPACITY_PRESET.expected)

    def test_compulsory_demo_exact_classification(self):
        session = MissTypeSession(
            COMPULSORY_PRESET.config,
            COMPULSORY_PRESET.addresses,
        )

        self.assertEqual(classifications(session), COMPULSORY_PRESET.expected)

    def test_actual_and_reference_have_same_total_line_count(self):
        session = MissTypeSession(CONFLICT_PRESET.config, ())
        actual = session.actual_simulator.config
        reference = session.reference_simulator.config

        actual_lines = actual.cache_size_bytes // actual.block_size_bytes
        reference_lines = reference.cache_size_bytes // reference.block_size_bytes
        self.assertEqual(actual_lines, reference_lines)

    def test_reference_cache_is_fully_associative_lru(self):
        session = MissTypeSession(CONFLICT_PRESET.config, ())
        reference = session.reference_config
        line_count = (
            CONFLICT_PRESET.config.cache_size_bytes
            // CONFLICT_PRESET.config.block_size_bytes
        )

        self.assertEqual(reference.sets, 1)
        self.assertEqual(reference.ways, line_count)
        self.assertEqual(reference.replacement_policy, "LRU")

    def test_non_lru_actual_config_is_rejected(self):
        for policy in ("FIFO", "Random"):
            with self.subTest(policy=policy):
                config = CacheConfig(
                    cache_size_bytes=4,
                    block_size_bytes=1,
                    ways=1,
                    replacement_policy=policy,
                )
                with self.assertRaisesRegex(ValueError, "requires an LRU"):
                    MissTypeSession(config, (0, 1))

    def test_reset_reproduces_identical_steps(self):
        session = MissTypeSession(CONFLICT_PRESET.config, CONFLICT_PRESET.addresses)
        first = session.run_all()
        session.reset()
        second = session.run_all()

        self.assertEqual(first, second)
        self.assertTrue(session.is_complete)

    def test_step_and_run_all_produce_identical_results(self):
        stepped = MissTypeSession(CAPACITY_PRESET.config, CAPACITY_PRESET.addresses)
        step_results = []
        while stepped.has_next():
            step_results.append(stepped.step())
        run = MissTypeSession(CAPACITY_PRESET.config, CAPACITY_PRESET.addresses)

        self.assertEqual(tuple(step_results), run.run_all())

    def test_step_after_completion_raises_stop_iteration(self):
        session = MissTypeSession(COMPULSORY_PRESET.config, (0,))
        session.step()

        with self.assertRaisesRegex(StopIteration, "complete"):
            session.step()

    def test_empty_trace_is_immediately_complete(self):
        session = MissTypeSession(COMPULSORY_PRESET.config, ())

        self.assertTrue(session.is_complete)
        self.assertFalse(session.has_next())
        self.assertEqual(session.run_all(), ())
        self.assertEqual(session.statistics.accesses, 0)
        with self.assertRaises(StopIteration):
            session.step()

    def test_address_outside_configured_width_is_rejected(self):
        config = CacheConfig(
            cache_size_bytes=4,
            block_size_bytes=1,
            ways=1,
            replacement_policy="LRU",
            address_bits=4,
        )

        with self.assertRaisesRegex(ValueError, "exceeds"):
            MissTypeSession(config, (16,))
        with self.assertRaisesRegex(ValueError, "non-negative"):
            MissTypeSession(config, (-1,))

    def test_block_address_uses_integer_division_by_block_size(self):
        config = CacheConfig(
            cache_size_bytes=8,
            block_size_bytes=4,
            ways=1,
            replacement_policy="LRU",
        )
        session = MissTypeSession(config, (0, 3, 4))
        steps = session.run_all()

        self.assertEqual(tuple(step.block_address for step in steps), (0, 0, 1))
        self.assertIs(steps[0].miss_type, MissType.COMPULSORY)
        self.assertIsNone(steps[1].miss_type)
        self.assertIs(steps[2].miss_type, MissType.COMPULSORY)

    def test_steps_are_immutable_snapshots(self):
        session = MissTypeSession(COMPULSORY_PRESET.config, (0,))
        session.step()

        self.assertIsInstance(session.steps, tuple)
        with self.assertRaises(AttributeError):
            session.steps.append("invalid")


if __name__ == "__main__":
    unittest.main()
