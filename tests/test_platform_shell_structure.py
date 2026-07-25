"""Static structure tests for the V3 platform shell."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app_window import CacheVisMainWindow as FacadeWindow
from cachevis_rv.gui.main_window import CacheVisMainWindow as PackageWindow


class PlatformShellStructureTest(unittest.TestCase):
    def setUp(self):
        self.src = Path(__file__).resolve().parents[1] / "src"
        self.gui = self.src / "cachevis_rv" / "gui"

    def test_app_window_is_explicit_compatibility_facade(self):
        source = (self.src / "app_window.py").read_text(encoding="utf-8")

        self.assertIs(FacadeWindow, PackageWindow)
        self.assertIn(
            "from cachevis_rv.gui.main_window import CacheVisMainWindow",
            source,
        )
        self.assertIn('__all__ = ["CacheVisMainWindow"]', source)
        self.assertNotIn("class CacheVisMainWindow", source)

    def test_main_window_contains_no_lab_input_widget_implementation(self):
        source = (self.gui / "main_window.py").read_text(encoding="utf-8")

        for forbidden in (
            "QComboBox",
            "QSpinBox",
            "QTableWidget",
            "CacheSimulator",
            "run_single_experiment",
            "run_compare_experiment",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_main_window_uses_sidebar_and_stack_without_tabs(self):
        source = (self.gui / "main_window.py").read_text(encoding="utf-8")

        self.assertIn("NavigationSidebar", source)
        self.assertIn("QStackedWidget", source)
        self.assertNotIn("QTabWidget", source)

    def test_gui_package_does_not_import_cache_core(self):
        for path in self.gui.glob("*.py"):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("cachevis_rv.core", source)
                self.assertNotIn("CacheSimulator", source)

    def test_registry_is_only_place_that_names_concrete_lab_widgets(self):
        main_source = (self.gui / "main_window.py").read_text(encoding="utf-8")
        registry_source = (self.gui / "lab_registry.py").read_text(encoding="utf-8")

        for widget_name in (
            "AddressVisualizerWidget",
            "SingleExperimentWidget",
            "CompareExperimentWidget",
        ):
            self.assertNotIn(widget_name, main_source)
            self.assertIn(widget_name, registry_source)

    def test_page_cache_reuses_existing_pages(self):
        source = (self.gui / "main_window.py").read_text(encoding="utf-8")

        self.assertIn("self._page_cache", source)
        self.assertIn("if page_id not in self._page_cache", source)
        self.assertIn("self._page_cache[page_id] = page", source)
        self.assertIn("def page_for", source)


if __name__ == "__main__":
    unittest.main()
