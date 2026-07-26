"""Tests for Locality statistics presentation and invariants."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.locality import LocalityController


class LocalityStatisticsViewModelTest(unittest.TestCase):
    def test_zero_and_completed_statistics_preserve_all_raw_values(self):
        controller = LocalityController()
        initial = controller.start_session(
            CacheConfig(cache_size_bytes=8, block_size_bytes=4, ways=1),
            [0, 1, 0, 4],
        )
        self.assertEqual(initial.statistics_view.accesses, 0)
        completed = controller.run_all()
        raw = completed.statistics
        view = completed.statistics_view
        for name in raw.__dataclass_fields__:
            self.assertEqual(getattr(view, name), getattr(raw, name))

    def test_all_three_invariants_are_explicitly_valid(self):
        controller = LocalityController()
        controller.start_session(
            CacheConfig(cache_size_bytes=4, block_size_bytes=4, ways=1),
            [0, 1, 0, 4],
        )
        view = controller.run_all().statistics_view
        self.assertTrue(view.partition_invariant_ok)
        self.assertTrue(view.address_invariant_ok)
        self.assertTrue(view.cache_invariant_ok)


if __name__ == "__main__":
    unittest.main()
