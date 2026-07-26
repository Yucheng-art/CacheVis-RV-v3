"""Tests for executed-trace block access aggregation."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.locality import (
    MATRIX_COLUMN_MAJOR,
    MATRIX_ROW_MAJOR,
    LocalityController,
)


class LocalityBlockAccessViewModelTest(unittest.TestCase):
    def setUp(self):
        self.controller = LocalityController()
        self.controller.start_session(
            CacheConfig(cache_size_bytes=8, block_size_bytes=4, ways=1),
            [0, 1, 0, 4],
        )

    def test_map_contains_only_executed_addresses_and_aggregates_counts(self):
        self.controller.step()
        state = self.controller.step()
        self.assertEqual(
            tuple(cell.address for cell in state.block_access_cells),
            (0, 1),
        )
        state = self.controller.step()
        address_zero = next(
            cell for cell in state.block_access_cells if cell.address == 0
        )
        self.assertEqual(address_zero.access_count, 2)
        self.assertEqual(address_zero.first_touch_count, 1)
        self.assertEqual(address_zero.temporal_count, 1)

    def test_summaries_and_current_markers_use_latest_not_selection(self):
        completed = self.controller.run_all()
        self.assertEqual(
            tuple(summary.block_address for summary in completed.block_summaries),
            (0, 1),
        )
        self.assertEqual(completed.block_summaries[0].total_accesses, 3)
        selected = self.controller.select_step(0)
        current_cells = [
            cell for cell in selected.block_access_cells if cell.is_current_block
        ]
        self.assertTrue(current_cells)
        self.assertTrue(all(cell.block_address == 1 for cell in current_cells))

    def test_matrix_orders_have_same_cells_but_distinct_access_order(self):
        states = []
        for preset in (MATRIX_ROW_MAJOR, MATRIX_COLUMN_MAJOR):
            controller = LocalityController()
            controller.start_session(preset.config, list(preset.addresses))
            states.append(controller.run_all())
        row, column = states
        self.assertEqual(
            {(cell.block_address, cell.offset, cell.address) for cell in row.block_access_cells},
            {
                (cell.block_address, cell.offset, cell.address)
                for cell in column.block_access_cells
            },
        )
        self.assertNotEqual(
            tuple(step.address for step in row.timeline_steps),
            tuple(step.address for step in column.timeline_steps),
        )
        self.assertEqual(len(row.block_access_cells), 16)
        self.assertEqual(len(column.block_access_cells), 16)


if __name__ == "__main__":
    unittest.main()
