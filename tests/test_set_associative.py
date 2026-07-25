"""Tests for set-associative cache replacement behavior."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from cache_simulator import CacheSimulator


class SetAssociativeCacheTest(unittest.TestCase):
    """Covers replacement inside a 2-way set."""

    def test_lru_replacement_within_same_set(self):
        config = CacheConfig(
            cache_size_bytes=64,
            block_size_bytes=16,
            ways=2,
            replacement_policy="LRU",
        )
        simulator = CacheSimulator(config)

        simulator.access(0x00)
        simulator.access(0x20)
        simulator.access(0x00)
        replacement = simulator.access(0x40)

        self.assertFalse(replacement["hit"])
        self.assertTrue(replacement["replaced_valid"])
        self.assertEqual(replacement["replaced_tag"], 1)

        snapshot = simulator.get_cache_snapshot()
        set_zero_tags = {line["tag"] for line in snapshot[0] if line["valid"]}
        self.assertEqual(set_zero_tags, {0, 2})


if __name__ == "__main__":
    unittest.main()
