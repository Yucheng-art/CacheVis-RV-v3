"""Tests for the pure Miss Type Controller workflow."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.miss_type import (
    CAPACITY_PRESET,
    COMPULSORY_PRESET,
    CONFLICT_PRESET,
    EMPTY_PAGE_STATE,
    MissType,
    MissTypeController,
)


def miss_types(state):
    return tuple(step.miss_type for step in state.timeline_steps)


class MissTypeControllerTest(unittest.TestCase):
    def setUp(self):
        self.controller = MissTypeController()

    def start(self, preset=CONFLICT_PRESET):
        return self.controller.start_session(
            preset.config,
            list(preset.addresses),
        )

    def test_start_session_publishes_initial_invalid_caches(self):
        state = self.start()

        self.assertTrue(state.has_session)
        self.assertFalse(state.is_complete)
        self.assertEqual(state.timeline_steps, ())
        self.assertIsNone(state.current_step)
        self.assertIsNone(state.selected_step)
        self.assertIsNone(state.selected_evidence)
        self.assertEqual(state.statistics.accesses, 0)
        self.assertTrue(all(not line.valid for line in state.actual_cache_lines))
        self.assertTrue(all(not line.valid for line in state.reference_cache_lines))

    def test_compulsory_preset_full_flow(self):
        self.start(COMPULSORY_PRESET)

        self.assertEqual(
            miss_types(self.controller.run_all()),
            COMPULSORY_PRESET.expected,
        )

    def test_conflict_preset_full_flow(self):
        self.start(CONFLICT_PRESET)

        self.assertEqual(
            miss_types(self.controller.run_all()),
            CONFLICT_PRESET.expected,
        )

    def test_capacity_preset_full_flow(self):
        self.start(CAPACITY_PRESET)

        self.assertEqual(
            miss_types(self.controller.run_all()),
            CAPACITY_PRESET.expected,
        )

    def test_current_and_selected_follow_latest_step_by_default(self):
        self.start()

        for expected_index in (0, 1):
            state = self.controller.step()
            self.assertEqual(state.current_step.step_index, expected_index)
            self.assertIs(state.current_step, state.selected_step)
            self.assertIs(
                state.selected_evidence.miss_type,
                state.selected_step.miss_type,
            )

    def test_historical_selection_only_changes_selected_and_evidence(self):
        self.start()
        latest = self.controller.run_all()
        state = self.controller.select_step(0)

        self.assertIs(state.current_step, latest.current_step)
        self.assertEqual(state.selected_step.step_index, 0)
        self.assertEqual(state.selected_evidence.classification_title, "Compulsory Miss")
        self.assertEqual(state.timeline_steps, latest.timeline_steps)
        self.assertEqual(state.statistics, latest.statistics)

    def test_historical_selection_preserves_both_cache_views(self):
        self.start()
        latest = self.controller.run_all()
        state = self.controller.select_step(0)

        self.assertIs(state.actual_cache_lines, latest.actual_cache_lines)
        self.assertIs(state.reference_cache_lines, latest.reference_cache_lines)

    def test_historical_selection_preserves_next_step_index(self):
        self.start()
        self.controller.step()
        before = self.controller.step()
        selected = self.controller.select_step(0)

        self.assertEqual(selected.next_step_index, before.next_step_index)
        self.assertEqual(selected.next_step_index, 2)

    def test_step_after_old_selection_advances_without_rollback(self):
        self.start()
        self.controller.step()
        before_selection = self.controller.step()
        self.controller.select_step(0)
        state = self.controller.step()

        self.assertEqual(state.current_step.step_index, 2)
        self.assertIs(state.current_step, state.selected_step)
        self.assertEqual(state.next_step_index, 3)
        self.assertNotEqual(state.actual_cache_lines, before_selection.actual_cache_lines)

    def test_run_all_executes_all_remaining_addresses(self):
        self.start()
        self.controller.step()
        state = self.controller.run_all()

        self.assertEqual(len(state.timeline_steps), 4)
        self.assertTrue(state.is_complete)
        self.assertEqual(state.next_step_index, 4)

    def test_reset_is_reproducible(self):
        self.start()
        first = self.controller.run_all()
        reset = self.controller.reset()

        self.assertEqual(reset.timeline_steps, ())
        self.assertEqual(reset.statistics.accesses, 0)
        self.assertTrue(all(not line.valid for line in reset.actual_cache_lines))
        second = self.controller.run_all()
        self.assertEqual(first.timeline_steps, second.timeline_steps)
        self.assertEqual(first.statistics, second.statistics)

    def test_clear_session_returns_canonical_empty_state(self):
        self.start()
        self.controller.step()

        self.assertIs(self.controller.clear_session(), EMPTY_PAGE_STATE)
        self.assertIs(self.controller.state, EMPTY_PAGE_STATE)

    def test_completed_step_and_run_all_semantics_match_session(self):
        self.start(COMPULSORY_PRESET)
        completed = self.controller.run_all()

        self.assertIs(self.controller.run_all(), completed)
        with self.assertRaises(StopIteration):
            self.controller.step()
        self.assertIs(self.controller.state, completed)

    def test_non_lru_config_is_rejected(self):
        config = CacheConfig(
            cache_size_bytes=4,
            block_size_bytes=1,
            ways=1,
            replacement_policy="FIFO",
        )

        with self.assertRaisesRegex(ValueError, "requires an LRU"):
            self.controller.start_session(config, [0, 1])

    def test_controller_requires_list_of_integer_addresses(self):
        with self.assertRaisesRegex(TypeError, "list"):
            self.controller.start_session(CONFLICT_PRESET.config, (0, 4))
        with self.assertRaisesRegex(TypeError, "integer"):
            self.controller.start_session(CONFLICT_PRESET.config, [0, "4"])

    def test_unknown_selection_is_no_op(self):
        self.start()
        state = self.controller.step()

        self.assertIs(self.controller.select_step(99), state)

    def test_methods_require_an_active_session(self):
        for method in (
            self.controller.reset,
            self.controller.step,
            self.controller.run_all,
        ):
            with self.subTest(method=method.__name__):
                with self.assertRaisesRegex(RuntimeError, "no active"):
                    method()
        with self.assertRaisesRegex(RuntimeError, "no active"):
            self.controller.select_step(0)

    def test_actual_and_reference_line_counts_match(self):
        state = self.start()

        self.assertEqual(len(state.actual_cache_lines), 4)
        self.assertEqual(len(state.reference_cache_lines), 4)
        self.assertEqual({line.set_index for line in state.reference_cache_lines}, {0})

    def test_hit_step_has_no_miss_type_in_controller_state(self):
        self.controller.start_session(CONFLICT_PRESET.config, [0, 0])
        state = self.controller.run_all()

        self.assertIsNone(state.current_step.miss_type)
        self.assertIsNone(state.selected_evidence.miss_type)
        self.assertEqual(state.statistics.hits, 1)


if __name__ == "__main__":
    unittest.main()
