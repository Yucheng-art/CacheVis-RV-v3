"""Offscreen platform integration tests for the available Miss Type Lab."""

import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.gui.lab_registry import AVAILABLE, COMING_SOON, get_lab
from cachevis_rv.gui.main_window import CacheVisMainWindow
from cachevis_rv.labs.miss_type.widget import MissTypeLabWidget


class MissTypePlatformIntegrationTest(unittest.TestCase):
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
        lab = get_lab("miss_type")

        self.assertEqual(lab.status, AVAILABLE)
        self.assertTrue(callable(lab.factory))
        self.assertIsNone(self.window.page_for("miss_type"))

    def test_home_and_sidebar_expose_available_miss_type(self):
        action = self.window.home_page._action_buttons["miss_type"]

        self.assertTrue(action.isEnabled())
        self.assertEqual(action.text(), "Open Lab")
        self.assertIn("miss_type", self.window.sidebar._buttons)
        self.assertEqual(get_lab("miss_type").category, "Learn")

    def test_home_navigation_lazily_creates_and_caches_page(self):
        self.assertTrue(self.window.home_page.request_lab("miss_type"))
        page = self.window.page_for("miss_type")

        self.assertIsInstance(page, MissTypeLabWidget)
        self.assertEqual(self.window.current_page_id, "miss_type")
        self.assertTrue(page.step_experiment())
        state = page.controller.state
        self.assertTrue(self.window.navigate_to("address_explorer"))
        self.assertTrue(self.window.navigate_to("miss_type"))
        self.assertIs(self.window.page_for("miss_type"), page)
        self.assertIs(page.controller.state, state)

    def test_sidebar_navigation_uses_same_registry_route(self):
        button = self.window.sidebar._buttons["miss_type"]
        button.click()
        self.app.processEvents()

        self.assertEqual(self.window.current_page_id, "miss_type")
        self.assertIsInstance(self.window.page_for("miss_type"), MissTypeLabWidget)

    def test_write_policy_is_now_available_with_factory(self):
        lab = get_lab("write_policy")
        self.assertEqual(lab.status, AVAILABLE)
        self.assertTrue(callable(lab.factory))
        self.assertTrue(self.window.navigate_to("write_policy"))
        self.assertIsNotNone(self.window.page_for("write_policy"))


if __name__ == "__main__":
    unittest.main()
