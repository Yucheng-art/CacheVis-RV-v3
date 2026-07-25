"""Tests for the pure Address Explorer controller and page state."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.address_explorer import (
    AddressExplorerController,
    AddressExplorerPageState,
)
from cachevis_rv.labs.address_explorer.engine import VisualizerStepEngine
from cachevis_rv.labs.address_explorer.widget import AddressVisualizerWidget
from visualizer_step_engine import VisualizerStepEngine as FlatVisualizerStepEngine
from visualizer_widget import AddressVisualizerWidget as FlatAddressVisualizerWidget


TRACE = [0, 2, 0, 1, 4, 0]


def make_config() -> CacheConfig:
    return CacheConfig(
        cache_size_bytes=4,
        block_size_bytes=1,
        ways=2,
        replacement_policy="LRU",
    )


class AddressExplorerControllerTest(unittest.TestCase):
    """Covers session, history selection, reset, and completion semantics."""

    def setUp(self):
        self.controller = AddressExplorerController()

    def test_controller_and_page_state_are_pure_python(self):
        package_root = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "labs"
            / "address_explorer"
        )
        for name in ("controller.py", "page_state.py"):
            with self.subTest(name=name):
                self.assertNotIn(
                    "PySide6",
                    (package_root / name).read_text(encoding="utf-8"),
                )

    def test_start_session_publishes_empty_timeline_and_invalid_cache(self):
        state = self.controller.start_session(make_config(), TRACE)

        self.assertIsInstance(state, AddressExplorerPageState)
        self.assertTrue(state.has_session)
        self.assertFalse(state.is_complete)
        self.assertEqual(state.next_step_index, 0)
        self.assertIsNone(state.current_step)
        self.assertIsNone(state.selected_step)
        self.assertEqual(state.timeline_steps, ())
        self.assertTrue(state.cache_lines)
        self.assertTrue(
            all(not line.valid for cache_set in state.cache_lines for line in cache_set)
        )

    def test_fixed_trace_hit_miss_results_and_latest_selection(self):
        self.controller.start_session(make_config(), TRACE)
        states = [self.controller.step() for _ in TRACE]

        self.assertEqual(
            [state.current_step.hit for state in states],
            [False, False, True, False, False, True],
        )
        for count, state in enumerate(states, start=1):
            self.assertEqual(state.current_step.step_index, count - 1)
            self.assertIs(state.selected_step, state.current_step)
            self.assertEqual(len(state.timeline_steps), count)

    def test_select_old_step_changes_only_selection(self):
        self.controller.start_session(make_config(), TRACE)
        self.controller.step()
        latest = self.controller.step()
        cache_lines = latest.cache_lines
        next_step_index = latest.next_step_index

        selected = self.controller.select_step(0)

        self.assertEqual(selected.selected_step.step_index, 0)
        self.assertIs(selected.current_step, latest.current_step)
        self.assertIs(selected.cache_lines, cache_lines)
        self.assertEqual(selected.next_step_index, next_step_index)

    def test_step_after_old_selection_advances_without_cache_rollback(self):
        self.controller.start_session(make_config(), TRACE)
        self.controller.step()
        second = self.controller.step()
        self.controller.select_step(0)

        third = self.controller.step()

        self.assertEqual(second.next_step_index, 2)
        self.assertEqual(third.current_step.step_index, 2)
        self.assertIs(third.selected_step, third.current_step)
        self.assertTrue(third.current_step.hit)
        self.assertEqual(third.next_step_index, 3)

    def test_run_all_executes_every_remaining_address(self):
        self.controller.start_session(make_config(), TRACE)
        self.controller.step()

        state = self.controller.run_all()

        self.assertEqual(len(state.timeline_steps), len(TRACE))
        self.assertEqual(state.current_step.step_index, len(TRACE) - 1)
        self.assertIs(state.selected_step, state.current_step)
        self.assertTrue(state.is_complete)
        self.assertIsNone(state.next_step_index)

    def test_reset_restores_initial_state(self):
        self.controller.start_session(make_config(), TRACE)
        self.controller.run_all()

        state = self.controller.reset()

        self.assertTrue(state.has_session)
        self.assertFalse(state.is_complete)
        self.assertEqual(state.next_step_index, 0)
        self.assertIsNone(state.current_step)
        self.assertIsNone(state.selected_step)
        self.assertEqual(state.timeline_steps, ())
        self.assertTrue(
            all(not line.valid for cache_set in state.cache_lines for line in cache_set)
        )

    def test_completion_and_repeated_calls_preserve_existing_semantics(self):
        self.controller.start_session(make_config(), [0])
        complete = self.controller.step()

        self.assertTrue(complete.is_complete)
        self.assertIs(self.controller.run_all(), complete)
        with self.assertRaises(StopIteration):
            self.controller.step()

    def test_unknown_selection_is_a_no_op(self):
        self.controller.start_session(make_config(), TRACE)
        state = self.controller.step()

        self.assertIs(self.controller.select_step(99), state)

    def test_compulsory_and_unknown_miss_semantics_are_unchanged(self):
        direct_mapped = CacheConfig(
            cache_size_bytes=4,
            block_size_bytes=1,
            ways=1,
            replacement_policy="LRU",
        )
        self.controller.start_session(direct_mapped, [0, 4, 0])

        steps = [self.controller.step().current_step for _ in range(3)]

        self.assertEqual(
            [step.miss_type for step in steps],
            ["compulsory", "compulsory", "unknown"],
        )

    def test_engine_compatibility_interfaces_report_current_state(self):
        engine = VisualizerStepEngine(make_config(), [0])

        self.assertFalse(engine.is_complete)
        self.assertEqual(engine.next_step_index, 0)
        self.assertTrue(
            all(
                not line.valid
                for cache_set in engine.get_cache_line_models()
                for line in cache_set
            )
        )
        engine.step()
        self.assertTrue(engine.is_complete)
        self.assertIsNone(engine.next_step_index)

    def test_widget_and_controller_do_not_access_simulator_or_duplicate_conversion(self):
        package_root = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "labs"
            / "address_explorer"
        )
        controller_source = (package_root / "controller.py").read_text(encoding="utf-8")
        widget_source = (package_root / "widget.py").read_text(encoding="utf-8")
        engine_source = (package_root / "engine.py").read_text(encoding="utf-8")

        self.assertNotIn(".simulator", controller_source)
        self.assertNotIn(".simulator", widget_source)
        self.assertNotIn("_snapshot_to_line_models", widget_source)
        self.assertEqual(engine_source.count("def _snapshot_to_line_models"), 1)

    def test_old_facades_and_package_paths_remain_identical(self):
        self.assertIs(FlatVisualizerStepEngine, VisualizerStepEngine)
        self.assertIs(FlatAddressVisualizerWidget, AddressVisualizerWidget)


if __name__ == "__main__":
    unittest.main()
