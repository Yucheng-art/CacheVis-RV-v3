import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.labs.policy import POLICY_PRESETS
from cachevis_rv.labs.policy.widget import PolicyLabWidget


class PolicyControlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = PolicyLabWidget()
        self.errors = []
        self.information = []
        self.widget._show_error = self.errors.append
        self.widget._show_information = lambda title, message: self.information.append((title, message))

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def _select(self, preset_id):
        index = next(i for i, preset in enumerate(POLICY_PRESETS) if preset.preset_id == preset_id)
        self.widget.controls.preset_combo.setCurrentIndex(index)
        self.app.processEvents()
        return POLICY_PRESETS[index]

    def test_all_seven_presets_fill_without_running(self):
        for preset in POLICY_PRESETS:
            with self.subTest(preset=preset.preset_id):
                selected = self._select(preset.preset_id)
                controls = self.widget.controls
                self.assertEqual(str(selected.random_seed), controls.seed_input.text())
                self.assertEqual(selected.config.cache_size_bytes, controls.cache_size_combo.currentData())
                self.assertFalse(self.widget.controller.state.has_session)

    def test_shared_parser_supports_decimal_hex_and_separators(self):
        self.widget.controls.trace_input.setPlainText("0, 0x1\n2  0X3")
        self.assertTrue(self.widget.reset_experiment())
        self.assertEqual((0, 1, 2, 3), self.widget.controller.state.addresses)

    def test_invalid_trace_and_seed_fail_clearly(self):
        for text in ("", "-1", "not-an-address"):
            with self.subTest(trace=text):
                self.widget.controls.trace_input.setPlainText(text)
                self.assertFalse(self.widget.reset_experiment())
                self.assertTrue(self.errors)
        self.widget.controls.trace_input.setPlainText("0, 1")
        for seed in ("", "abc", "2.5"):
            with self.subTest(seed=seed):
                self.widget.controls.seed_input.setText(seed)
                self.assertFalse(self.widget.reset_experiment())
                self.assertIn("seed", self.errors[-1].lower())

    def test_reset_step_run_all_and_completion_are_safe(self):
        self.assertTrue(self.widget.reset_experiment())
        self.assertEqual(0, self.widget.controller.state.next_step_index)
        self.assertTrue(self.widget.step_experiment())
        self.assertEqual(1, self.widget.controller.state.next_step_index)
        self.assertTrue(self.widget.run_all_experiment())
        self.assertTrue(self.widget.controller.state.is_complete)
        self.assertFalse(self.widget.step_experiment())
        self.assertFalse(self.widget.run_all_experiment())
        self.assertEqual(2, len(self.information))

    def test_changed_trace_or_seed_rebuilds_session(self):
        self.widget.step_experiment()
        self.assertEqual(1, self.widget.controller.state.next_step_index)
        self.widget.controls.trace_input.setPlainText("0, 1, 2")
        self.widget.controls.seed_input.setText("99")
        self.assertTrue(self.widget.step_experiment())
        state = self.widget.controller.state
        self.assertEqual((0, 1, 2), state.addresses)
        self.assertEqual(99, state.random_seed)
        self.assertEqual(1, state.next_step_index)


if __name__ == "__main__":
    unittest.main()
