"""Tests for V3 platform lab metadata and lazy factories."""

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.gui.lab_registry import (
    AVAILABLE,
    COMING_SOON,
    LAB_REGISTRY,
    get_available_labs,
    get_lab,
)


class LabRegistryTest(unittest.TestCase):
    def test_three_available_labs_are_registered(self):
        available = {lab.lab_id for lab in get_available_labs()}

        self.assertEqual(available, {
            "address_explorer",
            "single_experiment",
            "compare_experiment",
        })

    def test_five_future_labs_are_coming_soon(self):
        future = {
            lab.lab_id
            for lab in LAB_REGISTRY
            if lab.status == COMING_SOON
        }

        self.assertEqual(future, {
            "miss_type",
            "locality",
            "policy",
            "performance",
            "write_policy",
        })

    def test_lab_ids_and_orders_are_unique_and_stable(self):
        ids = [lab.lab_id for lab in LAB_REGISTRY]
        orders = [lab.order for lab in LAB_REGISTRY]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(orders), len(set(orders)))
        self.assertEqual(orders, sorted(orders))

    def test_available_labs_have_lazy_callable_factories(self):
        for lab in LAB_REGISTRY:
            with self.subTest(lab=lab.lab_id):
                if lab.status == AVAILABLE:
                    self.assertTrue(callable(lab.factory))
                else:
                    self.assertIsNone(lab.factory)

    def test_importing_registry_does_not_import_qt_or_construct_widgets(self):
        src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        script = (
            "import sys; "
            f"sys.path.insert(0, {src!r}); "
            "import cachevis_rv.gui.lab_registry as registry; "
            "assert 'PySide6' not in sys.modules; "
            "assert all(lab.factory is None or callable(lab.factory) "
            "for lab in registry.LAB_REGISTRY)"
        )

        result = subprocess.run(
            [sys.executable, "-B", "-c", script],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_registry_lookup_has_no_window_instance(self):
        self.assertIs(get_lab("address_explorer"), LAB_REGISTRY[0])
        self.assertIsNone(get_lab("not-a-lab"))
        self.assertTrue(all(not hasattr(lab, "window") for lab in LAB_REGISTRY))


if __name__ == "__main__":
    unittest.main()
