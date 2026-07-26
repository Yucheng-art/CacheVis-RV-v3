import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.gui.lab_registry import AVAILABLE, COMING_SOON, get_lab, get_available_labs
from cachevis_rv.gui.main_window import CacheVisMainWindow
from cachevis_rv.labs.policy.widget import PolicyLabWidget


class PolicyPlatformIntegrationTest(unittest.TestCase):
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
        lab = get_lab("policy")
        self.assertEqual(AVAILABLE, lab.status)
        self.assertTrue(callable(lab.factory))
        self.assertIsNone(self.window.page_for("policy"))
        self.assertEqual(6, len(get_available_labs()))

    def test_home_and_sidebar_expose_policy_in_learn_order(self):
        action = self.window.home_page._action_buttons["policy"]
        self.assertTrue(action.isEnabled())
        self.assertEqual("Open Lab", action.text())
        learn = [lab_id for lab_id in self.window.sidebar._buttons if lab_id in {"address_explorer", "miss_type", "locality", "policy"}]
        self.assertEqual(["address_explorer", "miss_type", "locality", "policy"], learn)

    def test_home_navigation_lazily_creates_and_preserves_policy(self):
        self.assertTrue(self.window.home_page.request_lab("policy"))
        page = self.window.page_for("policy")
        self.assertIsInstance(page, PolicyLabWidget)
        self.assertTrue(page.step_experiment())
        state = page.controller.state
        self.assertTrue(self.window.navigate_to("locality"))
        self.assertTrue(self.window.navigate_to("miss_type"))
        self.assertTrue(self.window.navigate_to("policy"))
        self.assertIs(page, self.window.page_for("policy"))
        self.assertIs(state, page.controller.state)

    def test_sidebar_route_uses_same_cached_instance(self):
        self.window.sidebar._buttons["policy"].click()
        self.app.processEvents()
        page = self.window.page_for("policy")
        self.assertIsInstance(page, PolicyLabWidget)
        self.assertTrue(self.window.navigate_to("address_explorer"))
        self.assertTrue(self.window.navigate_to("policy"))
        self.assertIs(page, self.window.page_for("policy"))

    def test_only_performance_and_write_policy_remain_unavailable(self):
        for lab_id in ("performance", "write_policy"):
            lab = get_lab(lab_id)
            self.assertEqual(COMING_SOON, lab.status)
            self.assertIsNone(lab.factory)
            self.assertFalse(self.window.navigate_to(lab_id))
            self.assertIsNone(self.window.page_for(lab_id))


if __name__ == "__main__":
    unittest.main()
