"""Tests for locality statistics, rates, averages, and invariants."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.locality import (
    BLOCK_LOCALITY,
    FIXED_STRIDE,
    LocalitySession,
    LOOP_TEMPORAL_REUSE,
)


class LocalityStatisticsTest(unittest.TestCase):
    def test_all_count_invariants_hold_after_every_step(self):
        session = LocalitySession(
            LOOP_TEMPORAL_REUSE.config,
            LOOP_TEMPORAL_REUSE.addresses,
        )

        for step in session.run_all():
            stats = step.statistics
            self.assertEqual(
                stats.first_touch_count + stats.spatial_count + stats.temporal_count,
                stats.accesses,
            )
            self.assertEqual(stats.first_touch_count, stats.unique_blocks)
            self.assertEqual(
                stats.first_touch_count + stats.spatial_count,
                stats.unique_addresses,
            )
            self.assertEqual(stats.hits + stats.misses, stats.accesses)

    def test_rates_stay_between_zero_and_one(self):
        stats = LocalitySession(
            BLOCK_LOCALITY.config, BLOCK_LOCALITY.addresses
        ).run_all()[-1].statistics

        for rate in (
            stats.hit_rate,
            stats.miss_rate,
            stats.spatial_event_rate,
            stats.temporal_event_rate,
        ):
            self.assertGreaterEqual(rate, 0.0)
            self.assertLessEqual(rate, 1.0)

    def test_no_reuse_samples_are_represented_by_none(self):
        stats = LocalitySession(
            FIXED_STRIDE.config, FIXED_STRIDE.addresses
        ).run_all()[-1].statistics

        self.assertIsNone(stats.average_address_reuse_gap)
        self.assertIsNone(stats.average_block_reuse_gap)
        self.assertIsNone(stats.average_block_reuse_distance)

    def test_reuse_averages_are_exact(self):
        session = LocalitySession(BLOCK_LOCALITY.config, BLOCK_LOCALITY.addresses)
        stats = session.run_all()[-1].statistics

        self.assertEqual(stats.average_address_reuse_gap, 4.0)
        self.assertEqual(stats.average_block_reuse_gap, 1.0)
        self.assertEqual(stats.average_block_reuse_distance, 0.0)

    def test_same_block_transition_count_excludes_first_step(self):
        stats = LocalitySession(
            BLOCK_LOCALITY.config, BLOCK_LOCALITY.addresses
        ).run_all()[-1].statistics

        self.assertEqual(stats.same_block_transition_count, 7)

    def test_reset_restores_zero_statistics_and_none_averages(self):
        session = LocalitySession(BLOCK_LOCALITY.config, BLOCK_LOCALITY.addresses)
        session.run_all()
        session.reset()
        stats = session.statistics

        self.assertEqual(stats.accesses, 0)
        self.assertEqual(stats.first_touch_count, 0)
        self.assertIsNone(stats.average_address_reuse_gap)
        self.assertIsNone(stats.average_block_reuse_gap)
        self.assertIsNone(stats.average_block_reuse_distance)


if __name__ == "__main__":
    unittest.main()
