import dataclasses
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import WriteTrafficDelta, build_traffic_view_model


class WritePolicyTrafficViewModelTest(unittest.TestCase):
    def test_formal_fields_and_decompositions_are_preserved(self):
        delta = WriteTrafficDelta(block_fills=1, block_fill_bytes=16,
            dirty_writebacks=1, dirty_writeback_bytes=16,
            memory_read_transactions=1, memory_read_bytes=16,
            memory_write_transactions=1, memory_write_bytes=16,
            total_lower_memory_transactions=2, total_lower_memory_bytes=32)
        model = build_traffic_view_model(delta)
        for name in delta.__dataclass_fields__:
            self.assertEqual(getattr(model, name), getattr(delta, name))
        self.assertTrue(model.transaction_decomposition_ok)
        self.assertTrue(model.byte_decomposition_ok)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            model.total_lower_memory_bytes = 0


if __name__ == "__main__":
    unittest.main()
