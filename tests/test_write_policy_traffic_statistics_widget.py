import os, sys, unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from PySide6.QtWidgets import QApplication
from cachevis_rv.labs.write_policy.widget import WritePolicyLabWidget


class WritePolicyTrafficStatisticsWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def _run(self, preset_index):
        widget = WritePolicyLabWidget(); widget.controls.preset_combo.setCurrentIndex(preset_index)
        widget.load_experiment(); widget.run_all(); return widget

    def test_repeated_dirty_streaming_and_mixed_numbers(self):
        expected = {1: ((36, 36, 16, 16), (36, 36, 32, 32)),
                    3: ((40, 8, 48, 8), (40, 8, 64, 8)),
                    4: ((80, 16, 112, 16), (80, 16, 128, 16)),
                    6: ((76, 44, 96, 44), (76, 44, 112, 44))}
        for index, values in expected.items():
            widget = self._run(index); models = widget.controller.state.current_lane_statistics
            self.assertEqual(tuple(x.total_lower_memory_bytes for x in models), values[0])
            self.assertEqual(tuple(x.total_lower_memory_bytes_with_final_drain for x in models), values[1])
            self.assertTrue(all(x.runtime_traffic_relation_ok and x.final_drain_relation_ok for x in models))
            widget.close()

    def test_empty_trace_has_finite_zero_rates(self):
        widget = WritePolicyLabWidget(); widget.controls.trace_input.clear(); widget.load_experiment()
        self.assertTrue(all(x.hit_rate == 0.0 and x.miss_rate == 0.0 for x in widget.controller.state.current_lane_statistics))
        widget.close()


if __name__ == "__main__": unittest.main()
