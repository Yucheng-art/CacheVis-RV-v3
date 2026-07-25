"""Tests for immutable actual/reference cache display models."""

from dataclasses import FrozenInstanceError
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.miss_type import (
    CONFLICT_PRESET,
    MissTypeCacheLineViewModel,
    MissTypeSession,
    build_cache_line_models,
)


class MissTypeCacheViewModelTest(unittest.TestCase):
    def setUp(self):
        self.session = MissTypeSession(
            CONFLICT_PRESET.config,
            CONFLICT_PRESET.addresses,
        )

    def test_actual_line_count_matches_actual_cache(self):
        lines = build_cache_line_models(
            self.session.get_actual_cache_snapshot(),
            "actual",
        )

        self.assertEqual(len(lines), self.session.line_count)

    def test_reference_line_count_matches_actual_line_count(self):
        lines = build_cache_line_models(
            self.session.get_reference_cache_snapshot(),
            "reference",
        )

        self.assertEqual(len(lines), self.session.line_count)

    def test_reference_lines_are_all_in_set_zero(self):
        lines = build_cache_line_models(
            self.session.get_reference_cache_snapshot(),
            "reference",
        )

        self.assertEqual({line.set_index for line in lines}, {0})
        self.assertEqual(
            tuple(line.way for line in lines),
            tuple(range(self.session.line_count)),
        )

    def test_actual_set_and_way_mapping_is_preserved(self):
        lines = build_cache_line_models(
            self.session.get_actual_cache_snapshot(),
            "actual",
        )

        self.assertEqual(
            tuple((line.set_index, line.way) for line in lines),
            ((0, 0), (1, 0), (2, 0), (3, 0)),
        )

    def test_initial_cache_lines_are_all_invalid(self):
        actual = build_cache_line_models(
            self.session.get_actual_cache_snapshot(),
            "actual",
        )
        reference = build_cache_line_models(
            self.session.get_reference_cache_snapshot(),
            "reference",
        )

        self.assertTrue(all(not line.valid for line in (*actual, *reference)))
        self.assertTrue(all(line.tag is None for line in (*actual, *reference)))

    def test_executed_metadata_matches_detached_snapshot(self):
        self.session.step()
        snapshot = self.session.get_actual_cache_snapshot()
        lines = build_cache_line_models(snapshot, "actual")
        raw = snapshot[0][0]
        line = next(item for item in lines if item.set_index == 0 and item.way == 0)

        self.assertEqual(line.tag, raw["tag"])
        self.assertEqual(line.last_used, raw["last_used"])
        self.assertEqual(line.insert_time, raw["insert_time"])
        self.assertTrue(line.valid)

    def test_models_are_tuple_and_frozen(self):
        lines = build_cache_line_models(
            self.session.get_actual_cache_snapshot(),
            "actual",
        )

        self.assertIsInstance(lines, tuple)
        with self.assertRaises(FrozenInstanceError):
            lines[0].valid = True

    def test_snapshot_does_not_expose_mutable_cache_lines(self):
        snapshot = self.session.get_actual_cache_snapshot()

        self.assertIsInstance(snapshot, tuple)
        self.assertIsInstance(snapshot[0], tuple)
        with self.assertRaises(TypeError):
            snapshot[0][0]["valid"] = True
        self.assertFalse(self.session.get_actual_cache_snapshot()[0][0]["valid"])

    def test_actual_and_reference_use_same_model_type(self):
        actual = build_cache_line_models(
            self.session.get_actual_cache_snapshot(),
            "actual",
        )
        reference = build_cache_line_models(
            self.session.get_reference_cache_snapshot(),
            "reference",
        )

        self.assertTrue(all(isinstance(line, MissTypeCacheLineViewModel) for line in actual))
        self.assertTrue(
            all(isinstance(line, MissTypeCacheLineViewModel) for line in reference)
        )

    def test_invalid_cache_role_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cache_role"):
            build_cache_line_models(
                self.session.get_actual_cache_snapshot(),
                "unknown",
            )


if __name__ == "__main__":
    unittest.main()
