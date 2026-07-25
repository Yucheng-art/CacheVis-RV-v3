"""Tests for immutable Miss Type teaching presets."""

from dataclasses import FrozenInstanceError
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.miss_type import (
    CAPACITY_PRESET,
    COMPULSORY_PRESET,
    CONFLICT_PRESET,
    MISS_TYPE_PRESETS,
    MissType,
    MissTypeSession,
)


class MissTypePresetsTest(unittest.TestCase):
    def test_presets_have_stable_names_and_order(self):
        self.assertEqual(
            tuple(preset.name for preset in MISS_TYPE_PRESETS),
            ("Compulsory demo", "Conflict demo", "Capacity demo"),
        )

    def test_preset_traces_and_configs_match_teaching_definition(self):
        self.assertEqual(
            (
                COMPULSORY_PRESET.config.cache_size_bytes,
                COMPULSORY_PRESET.config.block_size_bytes,
                COMPULSORY_PRESET.config.ways,
                COMPULSORY_PRESET.addresses,
            ),
            (4, 1, 1, (0, 1, 2, 3)),
        )
        self.assertEqual(CONFLICT_PRESET.addresses, (0, 4, 0, 4))
        self.assertEqual(
            (
                CAPACITY_PRESET.config.cache_size_bytes,
                CAPACITY_PRESET.config.block_size_bytes,
                CAPACITY_PRESET.config.ways,
                CAPACITY_PRESET.addresses,
            ),
            (2, 1, 2, (0, 1, 2, 0)),
        )

    def test_expected_sequences_match_actual_classification(self):
        for preset in MISS_TYPE_PRESETS:
            with self.subTest(preset=preset.name):
                actual = tuple(
                    step.miss_type
                    for step in MissTypeSession(
                        preset.config,
                        preset.addresses,
                    ).run_all()
                )
                self.assertEqual(actual, preset.expected)

    def test_presets_are_immutable_pure_data(self):
        self.assertIsInstance(MISS_TYPE_PRESETS, tuple)
        self.assertIsInstance(CONFLICT_PRESET.addresses, tuple)
        with self.assertRaises(FrozenInstanceError):
            CONFLICT_PRESET.name = "changed"
        self.assertEqual(
            CONFLICT_PRESET.expected,
            (
                MissType.COMPULSORY,
                MissType.COMPULSORY,
                MissType.CONFLICT,
                MissType.CONFLICT,
            ),
        )


if __name__ == "__main__":
    unittest.main()
