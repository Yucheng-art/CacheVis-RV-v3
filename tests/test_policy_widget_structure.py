import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


class PolicyWidgetStructureTest(unittest.TestCase):
    def test_facade_is_lightweight_and_subcomponents_are_split(self):
        root = Path(__file__).resolve().parents[1]
        facade = root / "src" / "cachevis_rv" / "labs" / "policy" / "widget.py"
        source = facade.read_text(encoding="utf-8")
        self.assertLess(len(source.splitlines()), 15)
        self.assertNotIn("PySide6", source)
        widgets = facade.parent / "widgets"
        expected = {
            "__init__.py", "lab_widget.py", "experiment_controls.py",
            "current_access_panel.py", "divergence_panel.py",
            "policy_lane_panel.py", "decision_panel.py", "cache_panel.py",
            "statistics_panel.py", "timeline.py",
        }
        self.assertTrue(expected.issubset({path.name for path in widgets.glob("*.py")}))

    def test_gui_orchestrator_uses_controller_not_domain_engines(self):
        path = Path(__file__).resolve().parents[1] / "src" / "cachevis_rv" / "labs" / "policy" / "widgets" / "lab_widget.py"
        source = path.read_text(encoding="utf-8")
        self.assertIn("PolicyController", source)
        self.assertNotIn("CacheSimulator", source)
        self.assertNotIn("PolicyComparisonSession", source)
        self.assertNotIn("PolicyDecisionExplainer", source)
        self.assertNotIn("random.seed", source)
        self.assertNotIn("choose_victim", source)

    def test_subcomponents_only_render_models(self):
        widgets = Path(__file__).resolve().parents[1] / "src" / "cachevis_rv" / "labs" / "policy" / "widgets"
        for path in widgets.glob("*.py"):
            if path.name in {"lab_widget.py", "experiment_controls.py", "__init__.py"}:
                continue
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("PolicyController", source)
                self.assertNotIn("PolicyComparisonSession", source)
                self.assertNotIn("CacheSimulator", source)
                self.assertNotIn("PolicyDecisionExplainer", source)

    def test_importing_pure_policy_package_does_not_import_qt(self):
        src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        script = (
            "import sys; "
            f"sys.path.insert(0, {src!r}); "
            "import cachevis_rv.labs.policy; "
            "assert 'PySide6' not in sys.modules"
        )
        result = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
