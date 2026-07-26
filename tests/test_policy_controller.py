import os
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    POLICY_PRESETS,
    SEEDED_RANDOM_REPLAY,
    PolicyController,
    PolicyComparisonSession,
)


def _step_signature(state):
    return tuple(
        (
            step.address,
            tuple(
                (
                    lane.policy,
                    lane.cache_hit,
                    lane.decision.victim_way,
                    lane.decision.victim_tag,
                )
                for lane in step.lane_steps
            ),
        )
        for step in state.timeline_steps
    )


class PolicyControllerTest(unittest.TestCase):
    def test_start_session_has_three_empty_policy_lanes(self):
        preset = POLICY_PRESETS[0]
        state = PolicyController().start_session(
            preset.config, preset.addresses, preset.random_seed
        )
        self.assertTrue(state.has_session)
        self.assertEqual(("LRU", "FIFO", "Random"), state.policies)
        self.assertIsNone(state.current_step)
        self.assertIsNone(state.selected_step)
        self.assertEqual((), state.timeline_steps)
        self.assertEqual(0, state.statistics.accesses)
        self.assertTrue(all(not line.valid for lane in state.lane_caches for line in lane.cache_lines))

    def test_all_seven_presets_run_through_controller(self):
        for preset in POLICY_PRESETS:
            with self.subTest(preset=preset.preset_id):
                controller = PolicyController()
                state = controller.start_session(
                    preset.config, preset.addresses, preset.random_seed
                )
                state = controller.run_all()
                self.assertTrue(state.is_complete)
                self.assertEqual(len(preset.addresses), state.statistics.accesses)
                self.assertEqual(len(preset.addresses), len(state.timeline_steps))

    def test_current_and_selected_default_to_latest(self):
        controller = PolicyController()
        preset = POLICY_PRESETS[0]
        controller.start_session(preset.config, preset.addresses)
        state = controller.step()
        self.assertIs(state.current_step, state.selected_step)
        state = controller.step()
        self.assertEqual(1, state.current_step.step_index)
        self.assertEqual(1, state.selected_step.step_index)

    def test_historical_selection_changes_only_selection_views(self):
        controller = PolicyController()
        preset = SEEDED_RANDOM_REPLAY
        controller.start_session(preset.config, preset.addresses, preset.random_seed)
        for _ in range(5):
            latest = controller.step()
        caches = latest.lane_caches
        statistics = latest.statistics
        divergence = latest.divergence_summary
        next_index = latest.next_step_index
        state = controller.select_step(1)
        self.assertEqual(4, state.current_step.step_index)
        self.assertEqual(1, state.selected_step.step_index)
        self.assertIs(statistics, state.statistics)
        self.assertEqual(caches, state.lane_caches)
        self.assertEqual(divergence, state.divergence_summary)
        self.assertEqual(next_index, state.next_step_index)
        self.assertEqual(1, state.selected_evidence.step_index)

    def test_selection_then_continue_matches_uninterrupted_random_replay(self):
        preset = SEEDED_RANDOM_REPLAY
        selected = PolicyController()
        selected.start_session(preset.config, preset.addresses, preset.random_seed)
        for _ in range(5):
            selected.step()
        selected.select_step(0)
        selected_state = selected.run_all()

        baseline = PolicyController()
        baseline.start_session(preset.config, preset.addresses, preset.random_seed)
        baseline_state = baseline.run_all()
        self.assertEqual(
            _step_signature(baseline_state),
            _step_signature(selected_state),
        )

    def test_reset_replays_seed_and_clear_fully_empties(self):
        preset = SEEDED_RANDOM_REPLAY
        controller = PolicyController()
        controller.start_session(preset.config, preset.addresses, preset.random_seed)
        first = _step_signature(controller.run_all())
        reset = controller.reset()
        self.assertEqual(0, reset.next_step_index)
        self.assertEqual(0, reset.statistics.accesses)
        second = _step_signature(controller.run_all())
        self.assertEqual(first, second)
        cleared = controller.clear_session()
        self.assertFalse(cleared.has_session)
        self.assertIsNone(cleared.config)
        self.assertEqual((), cleared.addresses)
        self.assertIsNone(cleared.random_seed)

    def test_completion_semantics_match_session(self):
        preset = POLICY_PRESETS[0]
        controller = PolicyController()
        controller.start_session(preset.config, preset.addresses)
        completed = controller.run_all()
        self.assertIs(completed, controller.run_all())
        with self.assertRaises(StopIteration):
            controller.step()

    def test_global_random_state_is_unchanged(self):
        before = random.getstate()
        preset = SEEDED_RANDOM_REPLAY
        controller = PolicyController()
        controller.start_session(preset.config, preset.addresses, preset.random_seed)
        controller.step()
        controller.select_step(0)
        controller.run_all()
        controller.reset()
        controller.run_all()
        self.assertEqual(before, random.getstate())

    def test_controller_is_pure_and_uses_only_public_session_surface(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "policy" / "controller.py"
        )
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("PySide6", source)
        self.assertNotIn("CacheSimulator", source)
        self.assertNotIn("session._", source)
        self.assertNotIn("random_stream", source)

    def test_session_read_only_config_interfaces_are_detached_and_stable(self):
        preset = POLICY_PRESETS[0]
        session = PolicyComparisonSession(preset.config, preset.addresses)
        self.assertEqual(2, session.line_count)
        configs = tuple(session.policy_config(policy) for policy in session.policies)
        self.assertEqual(("LRU", "FIFO", "Random"), tuple(config.replacement_policy for config in configs))
        self.assertEqual(
            {(config.cache_size_bytes, config.block_size_bytes, config.ways, config.address_bits, config.write_policy) for config in configs},
            {(preset.config.cache_size_bytes, preset.config.block_size_bytes, preset.config.ways, preset.config.address_bits, preset.config.write_policy)},
        )
        with self.assertRaises(ValueError):
            session.policy_config("NotAPolicy")


if __name__ == "__main__":
    unittest.main()
