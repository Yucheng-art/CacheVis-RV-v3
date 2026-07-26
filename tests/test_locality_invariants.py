"""Architecture, compatibility, and cross-trace Locality invariants."""

from dataclasses import FrozenInstanceError
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.gui.lab_registry import AVAILABLE, get_lab
from cachevis_rv.labs.locality import (
    LOCALITY_PRESETS,
    LocalityKind,
    LocalitySession,
)


class LocalityInvariantsTest(unittest.TestCase):
    def test_every_access_has_exactly_one_known_kind(self):
        for preset in LOCALITY_PRESETS:
            for step in LocalitySession(preset.config, preset.addresses).run_all():
                with self.subTest(preset=preset.preset_id, step=step.step_index):
                    self.assertIsInstance(step.locality_kind, LocalityKind)
                    self.assertNotIn("unknown", step.locality_kind.value)

    def test_classification_count_invariant_holds_for_every_preset(self):
        for preset in LOCALITY_PRESETS:
            stats = LocalitySession(preset.config, preset.addresses).run_all()[-1].statistics
            self.assertEqual(
                stats.first_touch_count + stats.spatial_count + stats.temporal_count,
                stats.accesses,
            )

    def test_steps_and_models_are_immutable(self):
        step = LocalitySession(
            LOCALITY_PRESETS[0].config,
            LOCALITY_PRESETS[0].addresses,
        ).step()

        with self.assertRaises(FrozenInstanceError):
            step.address = 99
        with self.assertRaises(FrozenInstanceError):
            step.evidence.address_seen_before = True
        with self.assertRaises(FrozenInstanceError):
            step.statistics.accesses = 99

    def test_locality_package_is_pure_and_independent_of_other_labs(self):
        package = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "locality"
        )
        for path in package.glob("*.py"):
            if path.name == "widget.py":
                continue
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("PySide6", source)
                self.assertNotIn("address_explorer", source)
                self.assertNotIn("miss_type", source)

    def test_importing_package_does_not_import_qt(self):
        src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        script = (
            "import sys; "
            f"sys.path.insert(0, {src!r}); "
            "import cachevis_rv.labs.locality; "
            "assert 'PySide6' not in sys.modules"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", script],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_analyzer_does_not_create_cache_or_session(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "locality" / "analyzer.py"
        )
        source = path.read_text(encoding="utf-8")

        self.assertNotIn("CacheSimulator", source)
        self.assertNotIn("LocalitySession", source)

    def test_locality_registry_is_available_with_lazy_factory(self):
        lab = get_lab("locality")

        self.assertEqual(lab.status, AVAILABLE)
        self.assertTrue(callable(lab.factory))


if __name__ == "__main__":
    unittest.main()
