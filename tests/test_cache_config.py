"""Boundary tests for cache configuration and address splitting."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig


class CacheConfigTest(unittest.TestCase):
    """Covers validation and derived address fields."""

    def test_default_derived_fields(self):
        config = CacheConfig()
        self.assertEqual(config.sets, 128)
        self.assertEqual(config.offset_bits, 5)
        self.assertEqual(config.index_bits, 7)
        self.assertEqual(config.tag_bits, 20)

    def test_split_address(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        parts = config.split_address(0x4C)

        self.assertEqual(parts["offset"], 0xC)
        self.assertEqual(parts["index"], 0)
        self.assertEqual(parts["tag"], 1)

    def test_rejects_non_power_of_two_cache_size(self):
        with self.assertRaisesRegex(ValueError, "cache_size_bytes must be a power"):
            CacheConfig(cache_size_bytes=96, block_size_bytes=16, ways=1)

    def test_rejects_non_power_of_two_block_size(self):
        with self.assertRaisesRegex(ValueError, "block_size_bytes must be a power"):
            CacheConfig(cache_size_bytes=128, block_size_bytes=24, ways=1)

    def test_rejects_ways_greater_than_total_lines(self):
        with self.assertRaisesRegex(ValueError, "ways must not exceed"):
            CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=8)

    def test_rejects_negative_address(self):
        config = CacheConfig()
        with self.assertRaisesRegex(ValueError, "address must be a non-negative"):
            config.split_address(-1)


if __name__ == "__main__":
    unittest.main()
