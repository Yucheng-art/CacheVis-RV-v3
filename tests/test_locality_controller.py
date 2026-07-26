"""Tests for the pure Locality Controller workflow."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.locality import (
    EMPTY_PAGE_STATE,
    LOCALITY_PRESETS,
    LocalityController,
)


CONFIG = CacheConfig(cache_size_bytes=8, block_size_bytes=4, ways=1)
TRACE = [0, 1, 0, 8]


class LocalityControllerTest(unittest.TestCase):
    def setUp(self):
        self.controller = LocalityController()

    def test_start_step_run_all_and_clear(self):
        initial = self.controller.start_session(CONFIG, TRACE)
        self.assertTrue(initial.has_session)
        self.assertEqual(initial.timeline_steps, ())
        self.assertTrue(all(not line.valid for line in initial.cache_lines))
        first = self.controller.step()
        self.assertIs(first.current_step, first.selected_step)
        completed = self.controller.run_all()
        self.assertEqual(len(completed.timeline_steps), len(TRACE))
        self.assertTrue(completed.is_complete)
        self.assertIs(self.controller.clear_session(), EMPTY_PAGE_STATE)

    def test_historical_selection_preserves_current_aggregate_state(self):
        self.controller.start_session(CONFIG, TRACE)
        latest = self.controller.run_all()
        selected = self.controller.select_step(0)
        self.assertIs(selected.current_step, latest.current_step)
        self.assertEqual(selected.selected_step.step_index, 0)
        self.assertIs(selected.cache_lines, latest.cache_lines)
        self.assertIs(selected.statistics, latest.statistics)
        self.assertIs(selected.statistics_view, latest.statistics_view)
        self.assertIs(selected.block_access_cells, latest.block_access_cells)
        self.assertIs(selected.block_summaries, latest.block_summaries)

    def test_step_after_history_selection_advances_without_rollback(self):
        self.controller.start_session(CONFIG, TRACE)
        self.controller.step()
        self.controller.step()
        self.controller.select_step(0)
        state = self.controller.step()
        self.assertEqual(state.current_step.step_index, 2)
        self.assertIs(state.current_step, state.selected_step)
        self.assertEqual(state.next_step_index, 3)

    def test_reset_reproduces_results_and_unknown_selection_is_no_op(self):
        self.controller.start_session(CONFIG, TRACE)
        first = self.controller.run_all()
        self.controller.reset()
        second = self.controller.run_all()
        self.assertEqual(first.timeline_steps, second.timeline_steps)
        self.assertIs(self.controller.select_step(99), second)

    def test_requires_active_session_and_list_addresses(self):
        with self.assertRaisesRegex(RuntimeError, "no active"):
            self.controller.step()
        with self.assertRaisesRegex(TypeError, "list"):
            self.controller.start_session(CONFIG, tuple(TRACE))

    def test_controller_does_not_access_simulator_or_session_private_state(self):
        path = os.path.join(
            os.path.dirname(__file__), "..", "src", "cachevis_rv", "labs",
            "locality", "controller.py",
        )
        with open(path, encoding="utf-8") as source:
            text = source.read()
        self.assertNotIn("CacheSimulator", text)
        self.assertNotIn("session._", text)

    def test_all_six_presets_match_expected_locality_and_cache_totals(self):
        for preset in LOCALITY_PRESETS:
            with self.subTest(preset=preset.preset_id):
                controller = LocalityController()
                controller.start_session(preset.config, list(preset.addresses))
                state = controller.run_all()
                self.assertEqual(
                    tuple(step.locality_kind for step in state.timeline_steps),
                    preset.expected_locality,
                )
                self.assertEqual(state.statistics.hits, preset.expected_hits)
                self.assertEqual(state.statistics.misses, preset.expected_misses)


if __name__ == "__main__":
    unittest.main()
