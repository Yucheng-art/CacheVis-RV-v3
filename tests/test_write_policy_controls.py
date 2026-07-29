import os, sys, unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from PySide6.QtWidgets import QApplication
from cachevis_rv.labs.write_policy.widget import WritePolicyLabWidget


class WritePolicyControlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def setUp(self): self.widget = WritePolicyLabWidget()
    def tearDown(self): self.widget.close(); self.widget.deleteLater(); self.app.processEvents()

    def test_seven_presets_fill_without_loading_and_restore(self):
        self.assertEqual(self.widget.controls.preset_combo.count(), 7)
        for index in range(7):
            self.widget.controls.preset_combo.setCurrentIndex(index)
            self.assertFalse(self.widget.controller.state.has_experiment)
            self.assertTrue(self.widget.controls.trace_input.toPlainText() or index >= 0)
        original = self.widget.controls.trace_input.toPlainText()
        self.widget.controls.trace_input.setPlainText("R 123")
        self.widget.controls.restore_current_preset()
        self.assertEqual(self.widget.controls.trace_input.toPlainText(), original)

    def test_load_step_run_reset_clear_and_button_states(self):
        self.assertFalse(self.widget.controls.step_button.isEnabled())
        self.assertTrue(self.widget.load_experiment())
        self.assertTrue(self.widget.controls.step_button.isEnabled())
        self.assertTrue(self.widget.step()); self.assertEqual(self.widget.controller.state.next_step_index, 1)
        self.assertTrue(self.widget.run_all()); self.assertFalse(self.widget.controls.step_button.isEnabled())
        self.assertTrue(self.widget.reset_experiment()); self.assertEqual(self.widget.controller.state.timeline_steps, ())
        self.assertTrue(self.widget.clear()); self.assertFalse(self.widget.controller.state.has_experiment)

    def test_empty_and_invalid_inputs_have_formal_semantics(self):
        self.widget.controls.trace_input.clear(); self.assertTrue(self.widget.load_experiment())
        self.assertTrue(self.widget.controller.state.is_complete)
        self.widget.controls.trace_input.setPlainText("X 0"); self.assertFalse(self.widget.load_experiment())
        self.assertTrue(self.widget.controls.error_label.text())
        self.widget.controls.trace_input.setPlainText("W 15")
        self.widget.controls.block_size_input.setValue(16); self.widget.controls.store_size_input.setValue(4)
        self.assertFalse(self.widget.load_experiment())


if __name__ == "__main__": unittest.main()
