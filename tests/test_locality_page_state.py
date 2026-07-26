"""Tests for immutable Locality page state."""

import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.locality import EMPTY_PAGE_STATE, LocalityController
from cachevis_rv.gui.lab_registry import COMING_SOON, get_lab


class LocalityPageStateTest(unittest.TestCase):
    def test_empty_state_is_explicit_and_invariants_hold(self):
        state = EMPTY_PAGE_STATE
        self.assertFalse(state.has_session)
        self.assertIsNone(state.config)
        self.assertIsNone(state.next_step_index)
        self.assertTrue(state.statistics_view.partition_invariant_ok)
        self.assertTrue(state.statistics_view.address_invariant_ok)
        self.assertTrue(state.statistics_view.cache_invariant_ok)

    def test_published_sequences_are_immutable_and_selection_is_paired(self):
        controller = LocalityController()
        controller.start_session(
            CacheConfig(cache_size_bytes=8, block_size_bytes=4, ways=1),
            [0, 1],
        )
        state = controller.run_all()
        self.assertIsInstance(state.timeline_steps, tuple)
        self.assertIsInstance(state.timeline_items, tuple)
        self.assertIsNotNone(state.selected_evidence)
        with self.assertRaises(FrozenInstanceError):
            state.has_session = False

    def test_controller_and_new_models_are_qt_free(self):
        root = os.path.join(
            os.path.dirname(__file__), "..", "src", "cachevis_rv", "labs", "locality"
        )
        for name in (
            "controller.py", "page_state.py", "cache_view_model.py",
            "evidence_view_model.py", "statistics_view_model.py",
            "timeline_view_model.py", "block_access_view_model.py",
        ):
            with open(os.path.join(root, name), encoding="utf-8") as source:
                self.assertNotIn("PySide6", source.read())

    def test_registry_keeps_locality_coming_soon_without_factory(self):
        definition = get_lab("locality")
        self.assertEqual(definition.status, COMING_SOON)
        self.assertIsNone(definition.factory)


if __name__ == "__main__":
    unittest.main()
