"""Structural and offscreen rendering tests for Locality Lab."""

import os
from pathlib import Path
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QScrollArea

from cachevis_rv.labs.locality.widget import LocalityLabWidget


class LocalityWidgetStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = LocalityLabWidget()

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def test_page_is_scrollable_and_components_are_split(self):
        self.assertIsInstance(self.widget, QScrollArea)
        self.assertEqual(
            self.widget.horizontalScrollBarPolicy(),
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        for attribute in (
            "controls", "current_panel", "evidence_panel", "cache_panel",
            "block_access_map", "statistics_panel", "timeline",
        ):
            self.assertTrue(hasattr(self.widget, attribute), attribute)
        self.assertIsInstance(self.widget.cache_panel.scroll, QScrollArea)
        self.assertIsInstance(self.widget.block_access_map.scroll, QScrollArea)
        self.assertIsInstance(self.widget.timeline.scroll, QScrollArea)

    def test_widget_orchestration_does_not_use_domain_implementations(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "locality"
            / "widgets" / "lab_widget.py"
        )
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("CacheSimulator", source)
        self.assertNotIn("LocalitySession", source)
        self.assertNotIn("LocalityAnalyzer", source)
        self.assertNotIn("LocalityKind.FIRST_TOUCH", source)

    def test_widget_entry_is_small_and_components_exist(self):
        root = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "locality"
        )
        entry = (root / "widget.py").read_text(encoding="utf-8")
        self.assertLessEqual(len(entry.splitlines()), 10)
        expected = {
            "__init__.py", "lab_widget.py", "experiment_controls.py",
            "current_access_panel.py", "evidence_panel.py", "cache_panel.py",
            "statistics_panel.py", "timeline.py", "block_access_map.py",
        }
        self.assertTrue(expected.issubset({path.name for path in (root / "widgets").glob("*.py")}))

    def test_importing_pure_package_does_not_require_qapplication(self):
        self.assertIsNotNone(self.widget.controller)
        package = __import__("cachevis_rv.labs.locality", fromlist=["LocalityController"])
        self.assertTrue(hasattr(package, "LocalityController"))
        self.assertFalse(hasattr(package, "LocalityLabWidget"))


if __name__ == "__main__":
    unittest.main()
