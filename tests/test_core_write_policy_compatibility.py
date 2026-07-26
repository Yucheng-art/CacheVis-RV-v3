"""Compatibility and scope guards for the core write-policy extension."""

import ast
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig, CacheSimulator
from cachevis_rv.gui.lab_registry import COMING_SOON, get_lab


ROOT = Path(__file__).resolve().parents[1]


class CoreWritePolicyCompatibilityTest(unittest.TestCase):
    def test_default_behavior_matches_explicit_write_through_allocate(self):
        implicit = CacheSimulator(CacheConfig(64, 16, 1, "LRU"))
        explicit = CacheSimulator(CacheConfig(
            64, 16, 1, "LRU", "write-through", 32, True
        ))
        trace = ((0, "write"), (4, "write"), (16, "read"), (0, "read"))
        implicit_results = [implicit.access(address, operation) for address, operation in trace]
        explicit_results = [explicit.access(address, operation) for address, operation in trace]
        self.assertEqual(implicit_results, explicit_results)
        self.assertEqual(implicit.get_cache_snapshot(), explicit.get_cache_snapshot())
        self.assertEqual(implicit.get_statistics(), explicit.get_statistics())

    def test_reset_replay_is_identical_for_all_four_combinations(self):
        trace = ((0, "write"), (0, "read"), (16, "write"))
        for policy in ("write-through", "write-back"):
            for allocate in (True, False):
                with self.subTest(policy=policy, allocate=allocate):
                    cache = CacheSimulator(CacheConfig(
                        16, 16, 1, "LRU", policy, 32, allocate
                    ))
                    first = [cache.access(*access) for access in trace]
                    first_snapshot = cache.get_cache_snapshot()
                    cache.reset()
                    second = [cache.access(*access) for access in trace]
                    self.assertEqual(first, second)
                    self.assertEqual(first_snapshot, cache.get_cache_snapshot())

    def test_write_policy_registry_contract_is_unchanged(self):
        lab = get_lab("write_policy")
        self.assertEqual(lab.status, COMING_SOON)
        self.assertIsNone(lab.factory)

    def test_core_has_no_gui_third_party_or_wall_clock_dependency(self):
        for path in (ROOT / "src" / "cachevis_rv" / "core").glob("*.py"):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            imports = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imports.update(
                (node.module or "").split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.level == 0
            )
            self.assertNotIn("PySide6", imports)
            self.assertNotIn("time", imports)


if __name__ == "__main__":
    unittest.main()
