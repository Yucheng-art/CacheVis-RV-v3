import ast
import os
from pathlib import Path
import subprocess
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


class PerformanceWidgetStructureTest(unittest.TestCase):
    def test_widget_facade_is_lightweight(self):
        source = (SRC / "cachevis_rv/labs/performance/widget.py").read_text(encoding="utf-8")
        self.assertNotIn("class PerformanceLabWidget", source)
        self.assertIn("from .widgets.lab_widget import PerformanceLabWidget", source)

    def test_gui_is_split_into_focused_subcomponents(self):
        widgets = SRC / "cachevis_rv/labs/performance/widgets"
        expected = {
            "__init__.py", "lab_widget.py", "experiment_controls.py", "point_editor.py",
            "summary_panel.py", "comparison_panel.py", "chart_panel.py", "chart_canvas.py",
            "sweep_table.py", "selected_point_panel.py", "metrics_panel.py", "hierarchy_panel.py",
        }
        self.assertEqual(expected, {path.name for path in widgets.glob("*.py")})
        for path in widgets.glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"))

    def test_gui_does_not_call_domain_engines_or_reimplement_formulas(self):
        widgets = SRC / "cachevis_rv/labs/performance/widgets"
        source = "\n".join(path.read_text(encoding="utf-8") for path in widgets.glob("*.py"))
        for forbidden in (
            "CacheSimulator", "PerformanceRunner(", "PerformanceSweepRunner(",
            "TwoLevelPerformanceAnalyzer(", "perf_counter", "time.time",
            "baseline.total_cycles /", "miss_rate *", "amat_cycles =",
        ):
            self.assertNotIn(forbidden, source)

    def test_pure_package_import_does_not_import_qt(self):
        script = (
            f"import sys; sys.path.insert(0, {str(SRC)!r}); "
            "import cachevis_rv.labs.performance; assert 'PySide6' not in sys.modules"
        )
        result = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
