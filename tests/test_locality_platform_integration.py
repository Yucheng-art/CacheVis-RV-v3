"""Offscreen platform integration tests for available Locality Lab."""

import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.gui.lab_registry import AVAILABLE, COMING_SOON, get_lab
from cachevis_rv.gui.main_window import CacheVisMainWindow
from cachevis_rv.labs.locality.widget import LocalityLabWidget


class LocalityPlatformIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = CacheVisMainWindow()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_registry_factory_is_callable_and_lazy(self):
        lab = get_lab("locality")
        self.assertEqual(lab.status, AVAILABLE)
        self.assertTrue(callable(lab.factory))
        self.assertIsNone(self.window.page_for("locality"))

    def test_home_and_sidebar_expose_available_locality(self):
        action = self.window.home_page._action_buttons["locality"]
        self.assertTrue(action.isEnabled())
        self.assertEqual(action.text(), "Open Lab")
        self.assertIn("locality", self.window.sidebar._buttons)
        self.assertEqual(get_lab("locality").category, "Learn")

    def test_home_navigation_lazily_creates_and_preserves_page(self):
        self.assertTrue(self.window.home_page.request_lab("locality"))
        page = self.window.page_for("locality")
        self.assertIsInstance(page, LocalityLabWidget)
        self.assertTrue(page.step_experiment())
        state = page.controller.state
        self.assertTrue(self.window.navigate_to("miss_type"))
        self.assertTrue(self.window.navigate_to("locality"))
        self.assertIs(self.window.page_for("locality"), page)
        self.assertIs(page.controller.state, state)

    def test_sidebar_uses_same_registry_route_and_page_cache(self):
        self.window.sidebar._buttons["locality"].click()
        self.app.processEvents()
        page = self.window.page_for("locality")
        self.assertIsInstance(page, LocalityLabWidget)
        self.assertEqual(self.window.current_page_id, "locality")
        self.assertTrue(self.window.navigate_to("address_explorer"))
        self.assertTrue(self.window.navigate_to("locality"))
        self.assertIs(self.window.page_for("locality"), page)

    def test_three_future_labs_remain_unavailable(self):
        for lab_id in ("policy", "performance", "write_policy"):
            with self.subTest(lab_id=lab_id):
                lab = get_lab(lab_id)
                self.assertEqual(lab.status, COMING_SOON)
                self.assertIsNone(lab.factory)
                self.assertFalse(self.window.navigate_to(lab_id))
                self.assertIsNone(self.window.page_for(lab_id))


if __name__ == "__main__":
    unittest.main()
