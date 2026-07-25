"""Tests for synchronized CacheSimulator and locality sessions."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.locality import (
    LocalityKind,
    LocalitySession,
    SEQUENTIAL_SPATIAL,
)


def config(policy="LRU", *, address_bits=32):
    return CacheConfig(
        cache_size_bytes=64,
        block_size_bytes=16,
        ways=1,
        replacement_policy=policy,
        address_bits=address_bits,
    )


class LocalitySessionTest(unittest.TestCase):
    def test_step_and_run_all_produce_identical_steps(self):
        addresses = list(SEQUENTIAL_SPATIAL.addresses)
        stepped = LocalitySession(config(), addresses)
        while stepped.has_next():
            stepped.step()
        run = LocalitySession(config(), addresses)

        self.assertEqual(stepped.steps, run.run_all())

    def test_reset_reproduces_non_random_results(self):
        for policy in ("LRU", "FIFO"):
            with self.subTest(policy=policy):
                session = LocalitySession(config(policy), [0, 16, 64, 0])
                first = session.run_all()
                session.reset()
                self.assertEqual(session.run_all(), first)

    def test_completion_and_repeated_step_semantics(self):
        session = LocalitySession(config(), [0])

        self.assertTrue(session.has_next())
        self.assertEqual(session.next_step_index, 0)
        session.step()
        self.assertTrue(session.is_complete)
        self.assertFalse(session.has_next())
        self.assertEqual(session.next_step_index, 1)
        with self.assertRaisesRegex(StopIteration, "complete"):
            session.step()

    def test_empty_trace_is_immediately_complete(self):
        session = LocalitySession(config(), [])

        self.assertTrue(session.is_complete)
        self.assertEqual(session.run_all(), ())
        self.assertEqual(session.statistics.accesses, 0)

    def test_negative_and_out_of_range_addresses_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            LocalitySession(config(), [0, -1])
        with self.assertRaisesRegex(ValueError, "8-bit"):
            LocalitySession(config(address_bits=8), [256])

    def test_non_integer_addresses_are_rejected(self):
        with self.assertRaisesRegex(TypeError, "integer"):
            LocalitySession(config(), [0, "4"])

    def test_lru_fifo_and_random_are_accepted(self):
        for policy in ("LRU", "FIFO", "Random"):
            with self.subTest(policy=policy):
                session = LocalitySession(config(policy), [0, 4, 0])
                self.assertEqual(len(session.run_all()), 3)

    def test_random_policy_does_not_change_locality_classification(self):
        trace = [0, 16, 32, 0, 4, 0]
        expected = tuple(
            step.locality_kind
            for step in LocalitySession(config("LRU"), trace).run_all()
        )

        for _ in range(5):
            actual = tuple(
                step.locality_kind
                for step in LocalitySession(config("Random"), trace).run_all()
            )
            self.assertEqual(actual, expected)

    def test_cache_results_and_locality_evidence_are_independent(self):
        spatial_hit = LocalitySession(config(), [0, 4]).run_all()[1]
        temporal_miss_config = CacheConfig(
            cache_size_bytes=2,
            block_size_bytes=1,
            ways=1,
            replacement_policy="LRU",
        )
        temporal_miss = LocalitySession(
            temporal_miss_config, [0, 2, 0]
        ).run_all()[-1]

        self.assertTrue(spatial_hit.cache_hit)
        self.assertIs(spatial_hit.locality_kind, LocalityKind.SPATIAL)
        self.assertFalse(temporal_miss.cache_hit)
        self.assertIs(temporal_miss.locality_kind, LocalityKind.TEMPORAL)

    def test_block_address_and_offset_use_configured_block_size(self):
        step = LocalitySession(config(), [23]).step()

        self.assertEqual(step.block_address, 1)
        self.assertEqual(step.offset, 7)
        self.assertEqual(step.address_hex, "0x17")

    def test_reset_clears_steps_statistics_and_analyzer(self):
        session = LocalitySession(config(), [0, 4])
        session.run_all()
        session.reset()

        self.assertEqual(session.steps, ())
        self.assertEqual(session.statistics.accesses, 0)
        self.assertEqual(session.next_step_index, 0)
        self.assertEqual(session.analyzer.seen_addresses, frozenset())


if __name__ == "__main__":
    unittest.main()
