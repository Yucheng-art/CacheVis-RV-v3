"""Static dependency, package-scope, and platform-status guards for M5.1."""

import ast
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.gui.lab_registry import AVAILABLE, get_lab


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "cachevis_rv" / "labs" / "write_policy"
PURE_MODULES = {
    "__init__.py", "model.py", "parser.py", "explainer.py", "session.py",
    "traffic.py", "presets.py", "controller.py", "page_state.py",
    "decision_view_model.py", "traffic_view_model.py", "cache_view_model.py",
    "statistics_view_model.py", "timeline_view_model.py", "comparison_view_model.py",
}


class WritePolicyScopeTest(unittest.TestCase):
    def test_package_has_exact_fifteen_module_set(self):
        self.assertEqual(
            {path.name for path in PACKAGE.glob("*.py") if path.name != "widget.py"},
            PURE_MODULES,
        )

    def test_package_is_pure_and_has_no_other_lab_wall_clock_or_gui_dependency(self):
        for name in PURE_MODULES:
            path = PACKAGE / name
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            self.assertNotIn("PySide6", source)
            self.assertNotIn("QWidget", source)
            self.assertNotIn("QApplication", source)
            self.assertNotIn("cachevis_rv.labs.miss_type", source)
            self.assertNotIn("cachevis_rv.labs.locality", source)
            self.assertNotIn("cachevis_rv.labs.policy", source)
            self.assertNotIn("cachevis_rv.labs.performance", source)
            imports = {
                (node.module or "").split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.level == 0
            }
            self.assertNotIn("time", imports)

    def test_session_uses_core_simulator_without_reimplementation_or_victim_selection(self):
        source = (PACKAGE / "session.py").read_text(encoding="utf-8")
        explainer = (PACKAGE / "explainer.py").read_text(encoding="utf-8")
        self.assertIn("CacheSimulator", source)
        self.assertNotIn("class CacheSimulator", source)
        self.assertNotIn("choose_victim_way", source + explainer)
        self.assertNotIn("victim_way", source + explainer)
        self.assertIn('access_result["evicted_way"]', explainer)

    def test_write_policy_lab_is_available_with_lazy_factory(self):
        lab = get_lab("write_policy")
        self.assertEqual(lab.status, AVAILABLE)
        self.assertTrue(callable(lab.factory))


if __name__ == "__main__":
    unittest.main()
