"""Cross-trace invariants and compatibility boundaries for M1.1."""

import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.gui.lab_registry import COMING_SOON, get_lab
from cachevis_rv.labs.address_explorer.engine import VisualizerStepEngine
from cachevis_rv.labs.miss_type import MissType, MissTypeSession


TRACES = (
    (0, 1, 2, 3),
    (0, 4, 0, 4),
    (0, 1, 2, 0),
    (0, 4, 1, 5, 0, 4, 2, 6, 0),
)


def session_for(trace):
    return MissTypeSession(
        CacheConfig(
            cache_size_bytes=4,
            block_size_bytes=1,
            ways=1,
            replacement_policy="LRU",
        ),
        trace,
    )


class MissTypeInvariantsTest(unittest.TestCase):
    def test_hits_plus_misses_equal_accesses_at_every_step(self):
        for trace in TRACES:
            for step in session_for(trace).run_all():
                stats = step.statistics
                self.assertEqual(stats.hits + stats.misses, stats.accesses)

    def test_three_miss_classes_equal_total_misses_at_every_step(self):
        for trace in TRACES:
            for step in session_for(trace).run_all():
                stats = step.statistics
                classified = (
                    stats.compulsory_misses
                    + stats.conflict_misses
                    + stats.capacity_misses
                )
                self.assertEqual(classified, stats.misses)

    def test_hits_plus_three_classes_equal_accesses(self):
        for trace in TRACES:
            stats = session_for(trace).run_all()[-1].statistics
            total = (
                stats.hits
                + stats.compulsory_misses
                + stats.conflict_misses
                + stats.capacity_misses
            )
            self.assertEqual(total, stats.accesses)

    def test_hit_never_carries_a_miss_type(self):
        steps = session_for((0, 0, 4, 0, 4)).run_all()

        for step in steps:
            if step.actual_result == "hit":
                self.assertIsNone(step.miss_type)

    def test_miss_always_carries_exactly_one_miss_type(self):
        for trace in TRACES:
            for step in session_for(trace).run_all():
                if step.actual_result == "miss":
                    self.assertIsInstance(step.miss_type, MissType)

    def test_each_block_has_at_most_one_compulsory_miss(self):
        steps = session_for((0, 4, 0, 4, 1, 1, 5, 1)).run_all()
        compulsory_blocks = [
            step.block_address
            for step in steps
            if step.miss_type is MissType.COMPULSORY
        ]

        self.assertEqual(len(compulsory_blocks), len(set(compulsory_blocks)))

    def test_repeated_runs_are_identical(self):
        trace = (0, 4, 1, 5, 0, 4, 2, 6, 0)

        self.assertEqual(session_for(trace).run_all(), session_for(trace).run_all())

    def test_miss_type_package_has_no_pyside_dependency(self):
        package = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "labs"
            / "miss_type"
        )

        for path in package.glob("*.py"):
            with self.subTest(path=path.name):
                self.assertNotIn("PySide6", path.read_text(encoding="utf-8"))

    def test_address_explorer_compulsory_unknown_behavior_is_unchanged(self):
        config = CacheConfig(
            cache_size_bytes=4,
            block_size_bytes=1,
            ways=1,
            replacement_policy="LRU",
        )
        engine = VisualizerStepEngine(config, [0, 4, 0])
        miss_types = tuple(engine.step().miss_type for _ in range(3))

        self.assertEqual(miss_types, ("compulsory", "compulsory", "unknown"))

    def test_registry_keeps_miss_type_coming_soon_without_factory(self):
        lab = get_lab("miss_type")

        self.assertIsNotNone(lab)
        self.assertEqual(lab.status, COMING_SOON)
        self.assertIsNone(lab.factory)


if __name__ == "__main__":
    unittest.main()
