import os, sys, unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from PySide6.QtWidgets import QApplication
from cachevis_rv.labs.write_policy.widget import WritePolicyLabWidget


class WritePolicyCacheWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def test_four_cards_show_invalid_clean_dirty_and_reset(self):
        widget = WritePolicyLabWidget(); widget.controls.preset_combo.setCurrentIndex(1); widget.load_experiment()
        self.assertEqual(len(widget.cache_panel.cards), 4)
        self.assertTrue(all(card.table.item(0, 4).text() == "INVALID" for card in widget.cache_panel.cards))
        widget.run_all(); states = {card.table.item(0, 4).text() for card in widget.cache_panel.cards}
        self.assertEqual(states, {"CLEAN", "DIRTY"})
        widget.reset_experiment(); self.assertTrue(all(card.table.item(0, 4).text() == "INVALID" for card in widget.cache_panel.cards))
        widget.close()


if __name__ == "__main__": unittest.main()
