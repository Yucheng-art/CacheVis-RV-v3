"""Offscreen Block Access Map behavior tests."""

import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.labs.locality import (
    FIXED_STRIDE,
    LOOP_TEMPORAL_REUSE,
    MATRIX_COLUMN_MAJOR,
    MATRIX_ROW_MAJOR,
    SEQUENTIAL_SPATIAL,
)
from cachevis_rv.labs.locality.widget import LocalityLabWidget


class LocalityBlockAccessWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = LocalityLabWidget()
        self.widget._show_error = lambda _message: None
        self.widget._show_information = lambda _title, _message: None

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def run_preset(self, preset):
        index = self.widget.controls.preset_combo.findData(preset)
        self.widget.controls.preset_combo.setCurrentIndex(index)
        self.assertTrue(self.widget.run_all_experiment())
        return self.widget.controller.state

    def test_sequential_and_stride_block_distributions(self):
        sequential = self.run_preset(SEQUENTIAL_SPATIAL)
        self.assertEqual(len(sequential.block_summaries), 2)
        stride = self.run_preset(FIXED_STRIDE)
        self.assertEqual(len(stride.block_summaries), 8)
        self.assertEqual(
            tuple(summary.block_address for summary in stride.block_summaries),
            tuple(range(8)),
        )

    def test_loop_reuse_makes_repeat_counts_visible(self):
        state = self.run_preset(LOOP_TEMPORAL_REUSE)
        self.assertTrue(all(cell.access_count == 2 for cell in state.block_access_cells))
        self.assertEqual(len(self.widget.block_access_map.cell_widgets), 4)

    def test_row_and_column_have_same_cells_and_different_timeline(self):
        row = self.run_preset(MATRIX_ROW_MAJOR)
        row_cells = {
            (cell.block_address, cell.offset, cell.address)
            for cell in row.block_access_cells
        }
        row_order = tuple(step.address for step in row.timeline_steps)
        column = self.run_preset(MATRIX_COLUMN_MAJOR)
        column_cells = {
            (cell.block_address, cell.offset, cell.address)
            for cell in column.block_access_cells
        }
        self.assertEqual(row_cells, column_cells)
        self.assertNotEqual(
            row_order, tuple(step.address for step in column.timeline_steps)
        )
        self.assertEqual(row.statistics.spatial_count, column.statistics.spatial_count)
        self.assertNotEqual(row.statistics.hits, column.statistics.hits)

    def test_current_markers_and_map_do_not_rollback_on_selection(self):
        latest = self.run_preset(LOOP_TEMPORAL_REUSE)
        current = [
            cell for cell in latest.block_access_cells if cell.is_current_address
        ]
        self.assertEqual(len(current), 1)
        self.widget.select_timeline_step(0)
        selected = self.widget.controller.state
        self.assertIs(selected.block_access_cells, latest.block_access_cells)
        self.assertEqual(
            [cell.address for cell in selected.block_access_cells if cell.is_current_address],
            [current[0].address],
        )


if __name__ == "__main__":
    unittest.main()
