"""Tests for Locality teaching evidence models."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.locality import LocalityController, LocalityKind


class LocalityEvidenceViewModelTest(unittest.TestCase):
    def test_first_spatial_temporal_paths_and_cache_status_are_independent(self):
        controller = LocalityController()
        controller.start_session(
            CacheConfig(cache_size_bytes=4, block_size_bytes=4, ways=1),
            [0, 1, 0],
        )
        models = []
        for _ in range(3):
            models.append(controller.step().selected_evidence)
        self.assertEqual(
            tuple(model.locality_kind for model in models),
            (
                LocalityKind.FIRST_TOUCH,
                LocalityKind.SPATIAL,
                LocalityKind.TEMPORAL,
            ),
        )
        self.assertIn("First Touch", models[0].rule_path)
        self.assertIn("Spatial Locality", models[1].rule_path)
        self.assertIn("Temporal Locality", models[2].rule_path)
        self.assertEqual(models[0].cache_status, "Miss")
        self.assertEqual(models[1].cache_status, "Hit")
        self.assertIn("does not guarantee", models[2].teaching_insight)

    def test_evidence_fields_are_copied_from_authoritative_step(self):
        controller = LocalityController()
        controller.start_session(
            CacheConfig(cache_size_bytes=8, block_size_bytes=4, ways=1),
            [0, 4, 0],
        )
        state = controller.run_all()
        step = state.selected_step
        view = state.selected_evidence
        self.assertEqual(view.block_reuse_distance, step.evidence.block_reuse_distance)
        self.assertEqual(view.address_reuse_gap, step.evidence.address_reuse_gap)
        self.assertEqual(view.classification_reason, step.evidence.classification_reason)


if __name__ == "__main__":
    unittest.main()
