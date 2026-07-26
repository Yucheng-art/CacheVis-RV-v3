"""Tests for Locality timeline presentation."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.locality import LocalityController


class LocalityTimelineViewModelTest(unittest.TestCase):
    def test_labels_are_f_s_t_and_cache_result_is_separate(self):
        controller = LocalityController()
        controller.start_session(
            CacheConfig(cache_size_bytes=4, block_size_bytes=4, ways=1),
            [0, 1, 0],
        )
        items = controller.run_all().timeline_items
        self.assertEqual(tuple(item.short_label for item in items), ("F", "S", "T"))
        self.assertEqual(tuple(item.cache_hit for item in items), (False, True, True))
        self.assertIn("cache MISS", items[0].tooltip)
        self.assertIn("cache HIT", items[1].tooltip)

    def test_current_and_selected_markers_are_independent(self):
        controller = LocalityController()
        controller.start_session(
            CacheConfig(cache_size_bytes=4, block_size_bytes=4, ways=1),
            [0, 1, 0],
        )
        controller.run_all()
        items = controller.select_step(0).timeline_items
        self.assertEqual([item.step_index for item in items if item.is_current], [2])
        self.assertEqual([item.step_index for item in items if item.is_selected], [0])


if __name__ == "__main__":
    unittest.main()
