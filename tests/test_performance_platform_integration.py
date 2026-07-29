import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.gui.lab_registry import AVAILABLE, COMING_SOON, get_available_labs, get_lab
from cachevis_rv.gui.main_window import CacheVisMainWindow
from cachevis_rv.labs.performance.widget import PerformanceLabWidget


class PerformancePlatformIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = CacheVisMainWindow()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_registry_home_sidebar_and_write_policy_statuses(self):
        performance = get_lab("performance")
        self.assertEqual(AVAILABLE, performance.status)
        self.assertTrue(callable(performance.factory))
        self.assertEqual(8, len(get_available_labs()))
        self.assertIsNone(self.window.page_for("performance"))
        action = self.window.home_page._action_buttons["performance"]
        self.assertTrue(action.isEnabled())
        self.assertEqual("Open Lab", action.text())
        learn = [lab_id for lab_id in self.window.sidebar._buttons if lab_id in {"address_explorer", "miss_type", "locality", "policy", "performance"}]
        self.assertEqual(["address_explorer", "miss_type", "locality", "policy", "performance"], learn)
        future = get_lab("write_policy")
        self.assertEqual(AVAILABLE, future.status)
        self.assertTrue(callable(future.factory))

    def test_home_navigation_is_lazy_and_reuses_stateful_page(self):
        self.assertTrue(self.window.home_page.request_lab("performance"))
        page = self.window.page_for("performance")
        self.assertIsInstance(page, PerformanceLabWidget)
        self.assertTrue(page.run_sweep())
        self.assertTrue(page.analyze_hierarchy())
        state = page.controller.state
        self.assertTrue(self.window.navigate_to("policy"))
        self.assertTrue(self.window.navigate_to("locality"))
        self.assertTrue(self.window.navigate_to("performance"))
        self.assertIs(page, self.window.page_for("performance"))
        self.assertIs(state, page.controller.state)

    def test_sidebar_creates_same_cached_pages_including_write_policy(self):
        self.window.sidebar._buttons["performance"].click()
        self.app.processEvents()
        page = self.window.page_for("performance")
        self.assertIsInstance(page, PerformanceLabWidget)
        self.assertTrue(self.window.navigate_to("address_explorer"))
        self.assertTrue(self.window.navigate_to("performance"))
        self.assertIs(page, self.window.page_for("performance"))
        self.assertTrue(self.window.navigate_to("write_policy"))
        self.assertIsNotNone(self.window.page_for("write_policy"))


if __name__ == "__main__":
    unittest.main()
