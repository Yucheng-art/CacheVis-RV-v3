import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.labs.performance.widget import PerformanceLabWidget


class PerformanceHierarchyWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = PerformanceLabWidget()

    def tearDown(self):
        self.widget.close()

    def test_load_example_only_fills_inputs(self):
        self.widget.hierarchy_panel.load_example()
        self.assertFalse(self.widget.controller.state.has_hierarchy_result)
        model = self.widget.hierarchy_panel.build_model()
        self.assertEqual((1.0, 0.1, 8.0, 0.25, 80.0), (model.l1_hit_time_cycles, model.l1_miss_rate, model.l2_hit_time_cycles, model.l2_local_miss_rate, model.memory_penalty_cycles))

    def test_analyze_renders_probabilities_contributions_and_limits(self):
        self.assertTrue(self.widget.analyze_hierarchy())
        view = self.widget.controller.state.hierarchy_view
        self.assertEqual(3.8, view.amat_cycles)
        self.assertEqual((0.9, 0.07500000000000001, 0.025), tuple(row.probability for row in view.probability_rows))
        text = self.widget.hierarchy_panel.result.text()
        for expected in ("AMAT = 3.8", "L2 global miss rate", "Analytical model only", "No actual L2 contents", "No write-back traffic"):
            self.assertIn(expected, text)

    def test_sweep_and_hierarchy_run_and_clear_independently(self):
        self.assertTrue(self.widget.run_sweep())
        sweep = self.widget.controller.state.sweep_result
        self.assertTrue(self.widget.analyze_hierarchy())
        self.assertIs(sweep, self.widget.controller.state.sweep_result)
        hierarchy = self.widget.controller.state.hierarchy_result
        self.assertTrue(self.widget.run_sweep())
        self.assertIs(hierarchy, self.widget.controller.state.hierarchy_result)
        self.widget.clear_hierarchy()
        self.assertTrue(self.widget.controller.state.has_sweep_result)
        self.widget.analyze_hierarchy()
        self.widget.clear_sweep()
        self.assertTrue(self.widget.controller.state.has_hierarchy_result)


if __name__ == "__main__":
    unittest.main()
