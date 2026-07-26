"""Offscreen tests for Locality experiment controls and actions."""

import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.experiments.address_trace_parser import parse_address_trace
from cachevis_rv.labs.locality import LOCALITY_PRESETS
from cachevis_rv.labs.locality.widget import LocalityLabWidget


class LocalityControlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = LocalityLabWidget()
        self.messages = []
        self.widget._show_error = lambda message: self.messages.append(("error", message))
        self.widget._show_information = (
            lambda title, message: self.messages.append((title, message))
        )

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def test_six_presets_fill_without_running(self):
        self.assertEqual(self.widget.controls.preset_combo.count(), 6)
        for index, preset in enumerate(LOCALITY_PRESETS):
            self.widget.controls.preset_combo.setCurrentIndex(index)
            self.assertEqual(
                parse_address_trace(self.widget.controls.trace_input.toPlainText()),
                list(preset.addresses),
            )
            self.assertFalse(self.widget.controller.state.has_session)
            self.assertEqual(
                self.widget.preset_conclusion_label.text(),
                "Teaching expectation: " + preset.expected_teaching_conclusion,
            )

    def test_shared_parser_formats_and_failures(self):
        self.assertEqual(parse_address_trace("0, 0x4\n8 12"), [0, 4, 8, 12])
        for text in ("", "0, nope", "0, -1"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_address_trace(text)

    def test_lru_fifo_random_can_run(self):
        for policy in ("LRU", "FIFO", "Random"):
            with self.subTest(policy=policy):
                self.widget.controls.policy_combo.setCurrentIndex(
                    self.widget.controls.policy_combo.findData(policy)
                )
                self.assertTrue(self.widget.reset_experiment())
                self.assertTrue(self.widget.step_experiment())
                self.assertEqual(
                    self.widget.controller.state.config.replacement_policy,
                    policy,
                )

    def test_reset_step_run_all_and_completed_calls(self):
        self.assertTrue(self.widget.reset_experiment())
        self.assertTrue(self.widget.step_experiment())
        self.assertTrue(self.widget.run_all_experiment())
        state = self.widget.controller.state
        self.assertTrue(state.is_complete)
        self.assertFalse(self.widget.step_experiment())
        self.assertFalse(self.widget.run_all_experiment())
        self.assertIs(self.widget.controller.state, state)
        self.assertTrue(any(title == "Trace complete" for title, _ in self.messages))

    def test_input_change_rebuilds_session_before_step(self):
        self.widget.controls.trace_input.setPlainText("0, 4")
        self.assertTrue(self.widget.step_experiment())
        self.assertEqual(self.widget.controller.state.addresses, (0, 4))
        self.widget.controls.trace_input.setPlainText("8, 12")
        self.assertTrue(self.widget.step_experiment())
        state = self.widget.controller.state
        self.assertEqual(state.addresses, (8, 12))
        self.assertEqual(state.current_step.step_index, 0)


if __name__ == "__main__":
    unittest.main()
