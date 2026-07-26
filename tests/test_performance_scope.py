import ast
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.gui.lab_registry import COMING_SOON, get_lab


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "cachevis_rv" / "labs" / "performance"


class PerformanceScopeTest(unittest.TestCase):
    def test_package_contains_only_pure_python_modules(self):
        self.assertEqual(
            {
                "__init__.py",
                "timing.py",
                "model.py",
                "runner.py",
                "sweep.py",
                "hierarchy.py",
                "presets.py",
                "controller.py",
                "page_state.py",
                "metrics_view_model.py",
                "sweep_view_model.py",
                "chart_view_model.py",
                "comparison_view_model.py",
                "hierarchy_view_model.py",
            },
            {path.name for path in PACKAGE.glob("*.py")},
        )
        for path in PACKAGE.glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"))

    def test_package_does_not_depend_on_pyside_or_gui(self):
        source = "\n".join(path.read_text(encoding="utf-8") for path in PACKAGE.glob("*.py"))
        self.assertNotIn("PySide6", source)
        self.assertNotIn("QApplication", source)
        self.assertNotIn("QWidget", source)
        self.assertNotIn("cachevis_rv.gui", source)

    def test_package_does_not_use_wall_clock_or_new_heavy_dependencies(self):
        source = "\n".join(path.read_text(encoding="utf-8") for path in PACKAGE.glob("*.py"))
        for forbidden in ("perf_counter", "time.time", "numpy", "pandas", "matplotlib"):
            self.assertNotIn(forbidden, source)

    def test_package_does_not_depend_on_other_lab_internals(self):
        source = "\n".join(path.read_text(encoding="utf-8") for path in PACKAGE.glob("*.py"))
        for lab in ("miss_type", "locality", "policy", "address_explorer"):
            self.assertNotIn(f"labs.{lab}", source)

    def test_hierarchy_does_not_create_an_l2_simulator(self):
        source = (PACKAGE / "hierarchy.py").read_text(encoding="utf-8")
        self.assertNotIn("CacheSimulator", source)
        self.assertNotIn("CacheConfig", source)

    def test_performance_lab_remains_coming_soon_without_factory(self):
        lab = get_lab("performance")
        self.assertEqual(COMING_SOON, lab.status)
        self.assertIsNone(lab.factory)

    def test_importing_package_has_no_qapplication_side_effect(self):
        before = set(sys.modules)
        __import__("cachevis_rv.labs.performance")
        after = set(sys.modules)
        self.assertNotIn("PySide6", after - before)


if __name__ == "__main__":
    unittest.main()
