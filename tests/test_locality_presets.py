"""Tests for immutable, deterministic Locality teaching presets."""

from dataclasses import FrozenInstanceError
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.locality import (
    BLOCK_LOCALITY,
    FIXED_STRIDE,
    LOCALITY_PRESETS,
    LOOP_TEMPORAL_REUSE,
    MATRIX_COLUMN_MAJOR,
    MATRIX_ROW_MAJOR,
    SEQUENTIAL_SPATIAL,
    LocalityKind,
    LocalitySession,
)


class LocalityPresetsTest(unittest.TestCase):
    def run_preset(self, preset):
        return LocalitySession(preset.config, preset.addresses).run_all()

    def test_presets_have_unique_stable_ids_and_titles(self):
        self.assertEqual(
            tuple(preset.preset_id for preset in LOCALITY_PRESETS),
            (
                "sequential_spatial",
                "fixed_stride",
                "loop_temporal_reuse",
                "block_locality",
                "matrix_row_major",
                "matrix_column_major",
            ),
        )
        self.assertEqual(len({preset.title for preset in LOCALITY_PRESETS}), 6)

    def test_preset_data_is_frozen_and_tuple_backed(self):
        for preset in LOCALITY_PRESETS:
            with self.subTest(preset=preset.preset_id):
                self.assertIsInstance(preset.addresses, tuple)
                self.assertIsInstance(preset.expected_locality, tuple)
                with self.assertRaises(FrozenInstanceError):
                    preset.title = "changed"

    def test_every_expected_sequence_matches_execution(self):
        for preset in LOCALITY_PRESETS:
            with self.subTest(preset=preset.preset_id):
                self.assertEqual(
                    tuple(step.locality_kind for step in self.run_preset(preset)),
                    preset.expected_locality,
                )

    def test_sequential_has_two_misses_and_six_hits(self):
        stats = self.run_preset(SEQUENTIAL_SPATIAL)[-1].statistics

        self.assertEqual((stats.hits, stats.misses), (6, 2))

    def test_fixed_stride_is_all_first_touch(self):
        steps = self.run_preset(FIXED_STRIDE)

        self.assertTrue(
            all(step.locality_kind is LocalityKind.FIRST_TOUCH for step in steps)
        )

    def test_loop_second_half_is_temporal(self):
        steps = self.run_preset(LOOP_TEMPORAL_REUSE)

        self.assertTrue(
            all(step.locality_kind is LocalityKind.TEMPORAL for step in steps[4:])
        )

    def test_block_locality_sequence_and_reuse_distance(self):
        steps = self.run_preset(BLOCK_LOCALITY)

        self.assertEqual(
            tuple(step.locality_kind for step in steps),
            BLOCK_LOCALITY.expected_locality,
        )
        self.assertEqual(
            tuple(step.evidence.block_reuse_distance for step in steps),
            (None, 0, 0, 0, 0, 0, 0, 0),
        )

    def test_expected_cache_counts_match_all_declared_presets(self):
        for preset in LOCALITY_PRESETS:
            with self.subTest(preset=preset.preset_id):
                stats = self.run_preset(preset)[-1].statistics
                self.assertEqual(stats.hits, preset.expected_hits)
                self.assertEqual(stats.misses, preset.expected_misses)


if __name__ == "__main__":
    unittest.main()
