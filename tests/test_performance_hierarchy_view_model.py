import os
from pathlib import Path
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.performance import (
    ANALYTICAL_L1_L2_MODEL,
    TwoLevelPerformanceAnalyzer,
    build_hierarchy_view_model,
)


class PerformanceHierarchyViewModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = TwoLevelPerformanceAnalyzer.analyze(ANALYTICAL_L1_L2_MODEL)
        cls.view = build_hierarchy_view_model(cls.result)

    def test_probability_rows_have_fixed_order_and_values(self):
        self.assertEqual(("l1_hit", "l2_global_hit", "memory_access"), tuple(row.row_id for row in self.view.probability_rows))
        self.assertEqual((0.9, 0.07500000000000001, 0.025), tuple(row.probability for row in self.view.probability_rows))

    def test_contribution_rows_have_fixed_order_and_sum(self):
        self.assertEqual(("l1_lookup", "l2_lookup", "memory"), tuple(row.row_id for row in self.view.contribution_rows))
        self.assertEqual((1.0, 0.8, 2.0), tuple(row.cycles for row in self.view.contribution_rows))
        self.assertEqual(3.8, self.view.amat_cycles)
        self.assertEqual(3.8, sum(row.cycles for row in self.view.contribution_rows))

    def test_local_global_explanation_is_explicit(self):
        text = self.view.local_vs_global_explanation
        self.assertIn("reached L2", text)
        self.assertIn("all CPU memory accesses", text)
        self.assertIn("global = L1 miss rate × L2 local miss rate", text)

    def test_rule_path_is_exact(self):
        self.assertEqual((
            "Every access pays L1 hit time",
            "Only L1 misses reach L2",
            "Only L2 local misses reach memory",
            "Sum the three expected-cycle contributions",
            "AMAT",
        ), self.view.rule_path)

    def test_invariants_and_limitations_are_complete(self):
        self.assertTrue(self.view.probability_partition_ok)
        self.assertTrue(self.view.contribution_sum_ok)
        for note in (
            "Analytical model only", "No actual L2 contents",
            "No inclusion/exclusion behavior", "No write-back traffic",
            "No parallel lookup model",
        ):
            self.assertIn(note, self.view.limitation_notes)

    def test_models_are_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            self.view.amat_cycles = 0
        with self.assertRaises(FrozenInstanceError):
            self.view.probability_rows[0].probability = 0

    def test_view_model_source_does_not_create_l2_simulator(self):
        source = (Path(__file__).resolve().parents[1] / "src/cachevis_rv/labs/performance/hierarchy_view_model.py").read_text(encoding="utf-8")
        self.assertNotIn("CacheSimulator", source)
        self.assertNotIn("CacheConfig", source)


if __name__ == "__main__":
    unittest.main()
