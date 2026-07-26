"""Architecture and compatibility boundaries for Policy core."""

import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.gui.lab_registry import AVAILABLE, get_lab
from cachevis_rv.labs.policy import (
    POLICY_PRESETS,
    PolicyComparisonSession,
    PolicyDecisionKind,
)


class PolicyInvariantsTest(unittest.TestCase):
    def test_every_decision_has_one_known_kind_and_consistent_metadata(self):
        for preset in POLICY_PRESETS:
            session = PolicyComparisonSession(
                preset.config, preset.addresses, preset.random_seed
            )
            for step in session.run_all():
                for lane in step.lane_steps:
                    self.assertIsInstance(
                        lane.decision.decision_kind, PolicyDecisionKind
                    )
                    self.assertNotIn("unknown", lane.decision.decision_kind.value)
                    self.assertTrue(lane.decision.metadata_consistent)

    def test_package_is_pure_and_does_not_depend_on_other_labs(self):
        package = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "policy"
        )
        for path in package.glob("*.py"):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("PySide6", source)
                self.assertNotIn("miss_type", source)
                self.assertNotIn("locality", source)
                self.assertNotIn("address_explorer", source)

    def test_importing_policy_does_not_import_qt(self):
        src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        script = (
            "import sys; "
            f"sys.path.insert(0, {src!r}); "
            "import cachevis_rv.labs.policy; "
            "assert 'PySide6' not in sys.modules"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", script],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_session_uses_core_simulator_without_reimplementing_cache(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "policy" / "session.py"
        )
        source = path.read_text(encoding="utf-8")
        self.assertIn("CacheSimulator", source)
        self.assertNotIn("choose_victim_way", source)
        self.assertNotIn("_find_hit_way", source)

    def test_policy_lab_is_available_with_lazy_factory(self):
        lab = get_lab("policy")
        self.assertEqual(lab.status, AVAILABLE)
        self.assertTrue(callable(lab.factory))


if __name__ == "__main__":
    unittest.main()
