import os, sys, unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from PySide6.QtWidgets import QApplication
from cachevis_rv.gui.lab_registry import AVAILABLE, COMING_SOON, get_available_labs, get_lab, get_labs
from cachevis_rv.gui.main_window import CacheVisMainWindow
from cachevis_rv.labs.write_policy.widget import WritePolicyLabWidget


class WritePolicyPlatformIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def setUp(self): self.window = CacheVisMainWindow()
    def tearDown(self): self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def test_registry_home_sidebar_and_empty_future_state(self):
        lab = get_lab("write_policy")
        self.assertEqual(lab.status, AVAILABLE); self.assertTrue(callable(lab.factory))
        self.assertEqual(len(get_available_labs()), 8)
        self.assertEqual(tuple(x for x in get_labs() if x.status == COMING_SOON), ())
        self.assertTrue(self.window.home_page._action_buttons["write_policy"].isEnabled())
        learn = [lab_id for lab_id in self.window.sidebar._buttons if lab_id not in {"home", "single_experiment", "compare_experiment"}]
        self.assertEqual(learn, ["address_explorer", "miss_type", "locality", "policy", "performance", "write_policy"])

    def test_lazy_creation_reuse_and_state_preservation(self):
        self.assertIsNone(self.window.page_for("write_policy"))
        self.assertTrue(self.window.navigate_to("write_policy")); page = self.window.page_for("write_policy")
        self.assertIsInstance(page, WritePolicyLabWidget); page.load_experiment(); page.step(); state = page.controller.state
        self.assertTrue(self.window.navigate_to("performance")); self.assertTrue(self.window.navigate_to("policy"))
        self.assertTrue(self.window.navigate_to("write_policy")); self.assertIs(self.window.page_for("write_policy"), page)
        self.assertIs(page.controller.state, state)


if __name__ == "__main__": unittest.main()
