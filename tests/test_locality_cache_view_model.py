"""Tests for Locality cache-line presentation models."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.locality import LocalityController, LocalitySession


class LocalityCacheViewModelTest(unittest.TestCase):
    def setUp(self):
        self.controller = LocalityController()
        self.controller.start_session(
            CacheConfig(cache_size_bytes=4, block_size_bytes=1, ways=1),
            [0, 0, 4],
        )

    def test_initial_lines_are_invalid_and_have_no_markers(self):
        lines = self.controller.state.cache_lines
        self.assertEqual(len(lines), 4)
        self.assertTrue(all(not line.valid for line in lines))
        self.assertFalse(any(line.is_current_set for line in lines))

    def test_invalid_fill_hit_and_victim_markers_come_from_current_step(self):
        first = self.controller.step()
        self.assertEqual(sum(line.is_invalid_fill for line in first.cache_lines), 1)
        hit = self.controller.step()
        self.assertEqual(sum(line.is_hit_way for line in hit.cache_lines), 1)
        victim = self.controller.step()
        self.assertEqual(sum(line.is_victim_way for line in victim.cache_lines), 1)
        self.assertFalse(any(line.is_invalid_fill for line in victim.cache_lines))

    def test_session_snapshot_is_detached_and_read_only(self):
        session = LocalitySession(
            CacheConfig(cache_size_bytes=4, block_size_bytes=1, ways=1),
            [0],
        )
        snapshot = session.get_cache_snapshot()
        self.assertIsInstance(snapshot, tuple)
        self.assertIsInstance(snapshot[0], tuple)
        with self.assertRaises(TypeError):
            snapshot[0][0]["valid"] = True
        session.step()
        self.assertFalse(snapshot[0][0]["valid"])


if __name__ == "__main__":
    unittest.main()
