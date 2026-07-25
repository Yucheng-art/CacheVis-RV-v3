"""Row-major and column-major locality/cache comparison tests."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.locality import (
    MATRIX_COLUMN_MAJOR,
    MATRIX_ROW_MAJOR,
    LocalitySession,
)


class LocalityMatrixPatternsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row = LocalitySession(
            MATRIX_ROW_MAJOR.config, MATRIX_ROW_MAJOR.addresses
        ).run_all()[-1].statistics
        cls.column = LocalitySession(
            MATRIX_COLUMN_MAJOR.config, MATRIX_COLUMN_MAJOR.addresses
        ).run_all()[-1].statistics

    def test_both_patterns_visit_the_same_sixteen_addresses(self):
        self.assertEqual(
            set(MATRIX_ROW_MAJOR.addresses),
            set(MATRIX_COLUMN_MAJOR.addresses),
        )
        self.assertEqual(len(set(MATRIX_ROW_MAJOR.addresses)), 16)

    def test_both_patterns_use_the_same_cache_configuration(self):
        self.assertEqual(MATRIX_ROW_MAJOR.config, MATRIX_COLUMN_MAJOR.config)

    def test_row_major_has_four_first_touch_and_twelve_spatial(self):
        self.assertEqual(
            (self.row.first_touch_count, self.row.spatial_count, self.row.temporal_count),
            (4, 12, 0),
        )

    def test_column_major_retains_same_locality_counts(self):
        self.assertEqual(
            (
                self.column.first_touch_count,
                self.column.spatial_count,
                self.column.temporal_count,
            ),
            (4, 12, 0),
        )

    def test_row_major_cache_results_are_twelve_hits_four_misses(self):
        self.assertEqual((self.row.hits, self.row.misses), (12, 4))

    def test_column_major_has_significantly_more_misses(self):
        self.assertEqual((self.column.hits, self.column.misses), (0, 16))
        self.assertGreaterEqual(self.column.misses - self.row.misses, 8)

    def test_column_teaching_conclusion_does_not_deny_spatial_locality(self):
        conclusion = MATRIX_COLUMN_MAJOR.expected_teaching_conclusion.lower()

        self.assertIn("spatial locality potential", conclusion)
        self.assertNotIn("no spatial", conclusion)


if __name__ == "__main__":
    unittest.main()
