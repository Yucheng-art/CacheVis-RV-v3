"""Tests for Miss Type GUI-facing pure view models."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.miss_type import (
    CAPACITY_PRESET,
    COMPULSORY_PRESET,
    CONFLICT_PRESET,
    MissTypeController,
    build_statistics_view_model,
)


class MissTypeGuiViewModelsTest(unittest.TestCase):
    def _run(self, preset):
        controller = MissTypeController()
        initial = controller.start_session(preset.config, list(preset.addresses))
        return initial, controller.run_all()

    def test_initial_statistics_are_zero_and_invariant_is_valid(self):
        initial, _complete = self._run(CONFLICT_PRESET)
        model = build_statistics_view_model(initial.statistics)

        self.assertEqual(
            (model.accesses, model.hits, model.misses, model.compulsory,
             model.conflict, model.capacity),
            (0, 0, 0, 0, 0, 0),
        )
        self.assertEqual(model.hit_rate_text, "0.0%")
        self.assertTrue(model.invariant_valid)

    def test_three_presets_publish_expected_statistics(self):
        expected = (
            (COMPULSORY_PRESET, (4, 0, 4, 4, 0, 0)),
            (CONFLICT_PRESET, (4, 0, 4, 2, 2, 0)),
            (CAPACITY_PRESET, (4, 0, 4, 3, 0, 1)),
        )
        for preset, counts in expected:
            with self.subTest(preset=preset.name):
                _initial, complete = self._run(preset)
                model = build_statistics_view_model(complete.statistics)
                self.assertEqual(
                    (model.accesses, model.hits, model.misses, model.compulsory,
                     model.conflict, model.capacity),
                    counts,
                )
                self.assertTrue(model.invariant_valid)

    def test_cache_markers_come_from_current_step_evidence(self):
        controller = MissTypeController()
        controller.start_session(CONFLICT_PRESET.config, list(CONFLICT_PRESET.addresses))
        state = controller.step()

        actual = [line for line in state.actual_cache_lines if line.is_invalid_fill]
        reference = [line for line in state.reference_cache_lines if line.is_invalid_fill]
        self.assertEqual(len(actual), 1)
        self.assertEqual(len(reference), 1)
        self.assertTrue(actual[0].is_current_set)
        self.assertTrue(reference[0].is_current_set)

    def test_historical_selection_preserves_cache_and_statistics_models(self):
        controller = MissTypeController()
        controller.start_session(CONFLICT_PRESET.config, list(CONFLICT_PRESET.addresses))
        latest = controller.run_all()
        selected = controller.select_step(0)

        self.assertIs(selected.actual_cache_lines, latest.actual_cache_lines)
        self.assertIs(selected.reference_cache_lines, latest.reference_cache_lines)
        self.assertIs(selected.statistics, latest.statistics)
        self.assertEqual(selected.selected_evidence.classification_title, "Compulsory Miss")

    def test_new_view_model_modules_are_qt_free(self):
        package = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "miss_type"
        )
        for name in ("timeline_view_model.py", "statistics_view_model.py"):
            with self.subTest(name=name):
                self.assertNotIn(
                    "PySide6",
                    (package / name).read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
