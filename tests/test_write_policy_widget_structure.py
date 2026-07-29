import os, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "cachevis_rv" / "labs" / "write_policy"


class WritePolicyWidgetStructureTest(unittest.TestCase):
    def test_gui_is_split_and_does_not_duplicate_domain_engines(self):
        files = tuple((PACKAGE / "widgets").glob("*.py")) + (PACKAGE / "widget.py",)
        self.assertGreaterEqual(len(files), 10)
        source = "\n".join(path.read_text(encoding="utf-8") for path in files)
        for forbidden in ("CacheSimulator", "WritePolicyComparisonSession", "WritePolicyExplainer", "victim_way", "matplotlib", "numpy", "pandas", "QtCharts"):
            self.assertNotIn(forbidden, source)
        self.assertIn("WritePolicyController", (PACKAGE / "widgets" / "lab_widget.py").read_text(encoding="utf-8"))

    def test_facade_is_lightweight_and_package_import_stays_qt_free(self):
        facade = (PACKAGE / "widget.py").read_text(encoding="utf-8")
        self.assertLess(len(facade.splitlines()), 10)
        script = f"import sys; sys.path.insert(0,{str(ROOT / 'src')!r}); import cachevis_rv.labs.write_policy; assert 'PySide6' not in sys.modules"
        result = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__": unittest.main()
