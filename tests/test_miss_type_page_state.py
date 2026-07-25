"""Tests for immutable Miss Type page-state semantics."""

from dataclasses import FrozenInstanceError
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.gui.lab_registry import COMING_SOON, get_lab
from cachevis_rv.labs.miss_type import (
    CONFLICT_PRESET,
    EMPTY_PAGE_STATE,
    MissTypeController,
)


class MissTypePageStateTest(unittest.TestCase):
    def test_empty_state_has_explicit_no_session_values(self):
        state = EMPTY_PAGE_STATE

        self.assertFalse(state.has_session)
        self.assertFalse(state.is_complete)
        self.assertIsNone(state.config)
        self.assertEqual(state.addresses, ())
        self.assertIsNone(state.current_step)
        self.assertIsNone(state.selected_step)
        self.assertIsNone(state.next_step_index)

    def test_published_sequences_are_immutable(self):
        controller = MissTypeController()
        state = controller.start_session(
            CONFLICT_PRESET.config,
            list(CONFLICT_PRESET.addresses),
        )

        self.assertIsInstance(state.addresses, tuple)
        self.assertIsInstance(state.timeline_steps, tuple)
        self.assertIsInstance(state.actual_cache_lines, tuple)
        self.assertIsInstance(state.reference_cache_lines, tuple)
        with self.assertRaises(FrozenInstanceError):
            state.has_session = False

    def test_current_and_selected_semantics_can_diverge(self):
        controller = MissTypeController()
        controller.start_session(
            CONFLICT_PRESET.config,
            list(CONFLICT_PRESET.addresses),
        )
        controller.run_all()
        state = controller.select_step(0)

        self.assertEqual(state.current_step.step_index, 3)
        self.assertEqual(state.selected_step.step_index, 0)

    def test_selected_evidence_always_matches_selected_step(self):
        controller = MissTypeController()
        controller.start_session(
            CONFLICT_PRESET.config,
            list(CONFLICT_PRESET.addresses),
        )
        controller.run_all()

        for index in range(4):
            state = controller.select_step(index)
            self.assertIs(
                state.selected_evidence.miss_type,
                state.selected_step.miss_type,
            )
            self.assertEqual(
                state.selected_evidence.classification_reason,
                state.selected_step.evidence.classification_reason,
            )

    def test_statistics_invariants_hold_in_page_state(self):
        controller = MissTypeController()
        controller.start_session(
            CONFLICT_PRESET.config,
            list(CONFLICT_PRESET.addresses),
        )
        stats = controller.run_all().statistics

        self.assertEqual(stats.hits + stats.misses, stats.accesses)
        self.assertEqual(
            stats.compulsory_misses
            + stats.conflict_misses
            + stats.capacity_misses,
            stats.misses,
        )

    def test_new_pure_modules_have_no_pyside_dependency(self):
        package = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "labs"
            / "miss_type"
        )
        for name in (
            "controller.py",
            "page_state.py",
            "cache_view_model.py",
            "evidence_view_model.py",
        ):
            with self.subTest(name=name):
                self.assertNotIn(
                    "PySide6",
                    (package / name).read_text(encoding="utf-8"),
                )

    def test_controller_does_not_access_simulators_or_classifier(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "labs"
            / "miss_type"
            / "controller.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("CacheSimulator", source)
        self.assertNotIn("actual_simulator", source)
        self.assertNotIn("reference_simulator", source)
        self.assertNotIn(".classifier", source)

    def test_registry_remains_coming_soon_without_factory(self):
        lab = get_lab("miss_type")

        self.assertEqual(lab.status, COMING_SOON)
        self.assertIsNone(lab.factory)


if __name__ == "__main__":
    unittest.main()
