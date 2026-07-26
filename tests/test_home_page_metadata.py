"""Metadata and non-navigation tests for V3 Home lab cards."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.gui.lab_registry import AVAILABLE, COMING_SOON, get_lab, get_labs


class HomePageMetadataTest(unittest.TestCase):
    def test_home_has_metadata_for_eight_lab_cards(self):
        labs = get_labs()

        self.assertEqual(len(labs), 8)
        self.assertEqual(
            [lab.title for lab in labs],
            [
                "Address Explorer",
                "Miss Type Lab",
                "Locality Lab",
                "Policy Lab",
                "Performance Lab",
                "Write Policy Lab",
                "Single Experiment",
                "Compare Experiment",
            ],
        )

    def test_available_and_coming_soon_statuses_are_accurate(self):
        statuses = {lab.lab_id: lab.status for lab in get_labs()}

        self.assertEqual(statuses["address_explorer"], AVAILABLE)
        self.assertEqual(statuses["miss_type"], AVAILABLE)
        self.assertEqual(statuses["locality"], AVAILABLE)
        self.assertEqual(statuses["policy"], AVAILABLE)
        self.assertEqual(statuses["single_experiment"], AVAILABLE)
        self.assertEqual(statuses["compare_experiment"], AVAILABLE)
        for lab_id in (
            "performance",
            "write_policy",
        ):
            self.assertEqual(statuses[lab_id], COMING_SOON)

    def test_coming_soon_cards_cannot_create_or_navigate_to_pages(self):
        future = [lab for lab in get_labs() if lab.status == COMING_SOON]

        self.assertTrue(future)
        self.assertTrue(all(lab.factory is None for lab in future))
        source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "gui"
            / "home_page.py"
        ).read_text(encoding="utf-8")
        self.assertIn("lab.status != AVAILABLE", source)
        self.assertIn("action.setEnabled(lab.status == AVAILABLE)", source)

    def test_address_explorer_display_name_is_exact(self):
        lab = get_lab("address_explorer")

        self.assertEqual(lab.title, "Address Explorer")
        self.assertEqual(lab.short_title, "Address Explorer")
        self.assertEqual(lab.category, "Learn")

    def test_classic_tools_category_is_exact(self):
        self.assertEqual(get_lab("single_experiment").category, "Classic Tools")
        self.assertEqual(get_lab("compare_experiment").category, "Classic Tools")


if __name__ == "__main__":
    unittest.main()
