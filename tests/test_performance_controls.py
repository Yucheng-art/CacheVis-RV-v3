import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication, QTableWidgetItem

from cachevis_rv.labs.performance.widget import PerformanceLabWidget


class PerformanceControlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = PerformanceLabWidget()
        self.widget._show_error = lambda *_args: None

    def tearDown(self):
        self.widget.close()

    def test_six_presets_fill_without_automatic_run(self):
        self.assertEqual(6, self.widget.controls.preset_combo.count())
        for index in range(6):
            self.widget.controller.clear_all()
            self.widget.controls.preset_combo.setCurrentIndex(index)
            self.assertFalse(self.widget.controller.state.has_sweep_result)
            definition = self.widget.controls.build_definition()
            self.assertGreater(len(definition.points), 0)

    def test_shared_trace_formats_and_empty_trace_run(self):
        self.widget.controls.trace_input.setPlainText("0, 0x4\n8 12")
        self.assertEqual((0, 4, 8, 12), self.widget.controls.build_definition().addresses)
        self.widget.controls.trace_input.clear()
        self.assertTrue(self.widget.run_sweep())
        self.assertTrue(all(point.metrics.amat_cycles is None for point in self.widget.controller.state.point_view_models))

    def test_invalid_token_negative_and_out_of_range_are_rejected(self):
        for trace in ("0, bad", "-1", str(1 << 32)):
            with self.subTest(trace=trace):
                self.widget.controls.trace_input.setPlainText(trace)
                with self.assertRaises(ValueError):
                    self.widget.controls.build_definition()

    def test_duplicate_id_missing_baseline_and_random_are_rejected(self):
        editor = self.widget.controls.point_editor
        editor.table.setItem(1, 0, QTableWidgetItem(editor.table.item(0, 0).text()))
        with self.assertRaisesRegex(ValueError, "unique"):
            self.widget.controls.build_definition()
        self.widget.controls.restore_current_preset()
        self.widget.controls.baseline_combo.addItem("missing")
        self.widget.controls.baseline_combo.setCurrentText("missing")
        with self.assertRaisesRegex(ValueError, "baseline"):
            self.widget.controls.build_definition()
        self.widget.controls.restore_current_preset()
        editor.table.setItem(0, 6, QTableWidgetItem("Random"))
        with self.assertRaisesRegex(ValueError, "Policy Lab"):
            self.widget.controls.build_definition()

    def test_invalid_config_and_timing_use_formal_validation(self):
        editor = self.widget.controls.point_editor
        editor.table.setItem(0, 3, QTableWidgetItem("3"))
        with self.assertRaises(ValueError):
            self.widget.controls.build_definition()
        self.widget.controls.restore_current_preset()
        editor.table.setItem(0, 7, QTableWidgetItem("0"))
        with self.assertRaises(ValueError):
            self.widget.controls.build_definition()

    def test_restore_and_clear_sweep_preserve_hierarchy(self):
        self.widget.controls.trace_input.setPlainText("99")
        self.widget.controls.restore_current_preset()
        self.assertNotEqual("99", self.widget.controls.trace_input.toPlainText())
        self.assertTrue(self.widget.analyze_hierarchy())
        self.assertTrue(self.widget.run_sweep())
        self.widget.clear_sweep()
        self.assertFalse(self.widget.controller.state.has_sweep_result)
        self.assertTrue(self.widget.controller.state.has_hierarchy_result)


if __name__ == "__main__":
    unittest.main()
