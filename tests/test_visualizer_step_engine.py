"""Tests for the pure-Python visualizer step engine."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from visualizer_step_engine import VisualizerStepEngine


class VisualizerStepEngineTest(unittest.TestCase):
    """Covers direct-mapped stepping, view model fields, and reset."""

    def test_direct_mapped_step_results_are_correct(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        engine = VisualizerStepEngine(config, [0x00, 0x04, 0x40])

        first = engine.step()
        second = engine.step()
        third = engine.step()

        self.assertFalse(first.hit)
        self.assertEqual(first.victim_way, 0)
        self.assertEqual(first.replacement_reason, "invalid-line")
        self.assertTrue(second.hit)
        self.assertEqual(second.hit_way, 0)
        self.assertFalse(third.hit)
        self.assertTrue(third.replaced_valid)
        self.assertEqual(third.replaced_tag, 0)
        self.assertEqual(third.replacement_reason, "LRU")
        self.assertEqual(third.total_accesses, 3)
        self.assertEqual(third.hits, 1)
        self.assertEqual(third.misses, 2)

    def test_address_binary_and_split_bit_counts_are_correct(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        step = VisualizerStepEngine(config, [0x4C]).step()

        self.assertEqual(len(step.address_binary), 32)
        self.assertEqual(step.address_binary, format(0x4C, "032b"))
        self.assertEqual(step.offset_bits, 4)
        self.assertEqual(step.index_bits, 2)
        self.assertEqual(step.tag_bits, 26)
        self.assertEqual(step.tag, 1)
        self.assertEqual(step.index, 0)
        self.assertEqual(step.offset, 0xC)

    def test_first_access_to_memory_block_is_compulsory_miss(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        step = VisualizerStepEngine(config, [0x00]).step()

        self.assertFalse(step.hit)
        self.assertEqual(step.miss_type, "compulsory")
        self.assertIn("compulsory", "\n".join(step.explanation_lines))

    def test_hit_step_generates_hit_explanation(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        engine = VisualizerStepEngine(config, [0x00, 0x04])
        engine.step()
        hit = engine.step()

        self.assertTrue(hit.hit)
        self.assertIn("cache hit", "\n".join(hit.explanation_lines))

    def test_miss_step_generates_victim_explanation(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        engine = VisualizerStepEngine(config, [0x00, 0x40])
        engine.step()
        miss = engine.step()

        text = "\n".join(miss.explanation_lines)
        self.assertFalse(miss.hit)
        self.assertIn("cache miss", text)
        self.assertIn("LRU selects way 0", text)

    def test_reset_clears_state_and_rewinds_trace(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        engine = VisualizerStepEngine(config, [0x00, 0x04])
        engine.step()
        engine.step()

        self.assertFalse(engine.has_next())
        engine.reset()

        self.assertTrue(engine.has_next())
        first_again = engine.step()
        self.assertEqual(first_again.step_index, 0)
        self.assertEqual(first_again.total_accesses, 1)
        self.assertEqual(first_again.misses, 1)
        self.assertEqual(first_again.miss_type, "compulsory")

    def test_step_after_trace_end_raises_stop_iteration(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        engine = VisualizerStepEngine(config, [0x00])
        engine.step()

        with self.assertRaises(StopIteration):
            engine.step()


if __name__ == "__main__":
    unittest.main()
