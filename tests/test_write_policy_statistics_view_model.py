import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import WRITE_POLICY_PRESETS, WritePolicyController


class WritePolicyStatisticsViewModelTest(unittest.TestCase):
    def test_empty_rates_and_all_invariants(self):
        controller = WritePolicyController()
        state = controller.load_preset(WRITE_POLICY_PRESETS[-1])
        for item in state.current_lane_statistics:
            self.assertEqual((item.hit_rate, item.miss_rate), (0.0, 0.0))
            self.assertTrue(math.isfinite(item.hit_rate))
        state = controller.run_all()
        invariant_names = (
            "access_partition_ok", "read_partition_ok", "write_partition_ok",
            "write_miss_partition_ok", "fill_relation_ok",
            "dirty_writeback_relation_ok", "runtime_traffic_relation_ok",
            "final_drain_relation_ok",
        )
        self.assertTrue(all(getattr(item, name)
                            for item in state.current_lane_statistics
                            for name in invariant_names))

    def test_runtime_and_final_drain_remain_distinct(self):
        controller = WritePolicyController()
        controller.load_preset(WRITE_POLICY_PRESETS[1])
        stats = {item.lane_id: item for item in controller.run_all().current_lane_statistics}
        self.assertEqual(stats["wb_wa"].total_lower_memory_bytes, 16)
        self.assertEqual(stats["wb_wa"].total_lower_memory_bytes_with_final_drain, 32)
        current = tuple(stats.values())
        self.assertEqual(controller.select_step(0).current_lane_statistics, current)


if __name__ == "__main__":
    unittest.main()
