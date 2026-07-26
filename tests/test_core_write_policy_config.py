"""Formal configuration contract for core write policies."""

import os
import sys
import unittest
from dataclasses import asdict, fields, replace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig


class CoreWritePolicyConfigTest(unittest.TestCase):
    def test_exact_field_contract_and_defaults(self):
        self.assertEqual(
            tuple(field.name for field in fields(CacheConfig)),
            (
                "cache_size_bytes",
                "block_size_bytes",
                "ways",
                "replacement_policy",
                "write_policy",
                "address_bits",
                "write_allocate",
            ),
        )
        config = CacheConfig()
        self.assertEqual(config.write_policy, "write-through")
        self.assertIs(config.write_allocate, True)

    def test_both_write_policies_and_allocation_values_are_valid(self):
        for write_policy in ("write-through", "write-back"):
            for write_allocate in (True, False):
                config = CacheConfig(
                    write_policy=write_policy, write_allocate=write_allocate
                )
                self.assertEqual(config.write_policy, write_policy)
                self.assertIs(config.write_allocate, write_allocate)

    def test_invalid_write_policy_and_non_bool_allocation_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "write_policy must be one of"):
            CacheConfig(write_policy="write-around")
        for value in (1, 0, "true", "false", None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "write_allocate must be a bool"):
                    CacheConfig(write_allocate=value)

    def test_equality_replace_repr_and_serialization_include_new_field(self):
        allocated = CacheConfig(write_policy="write-back", write_allocate=True)
        bypass = replace(allocated, write_allocate=False)
        self.assertNotEqual(allocated, bypass)
        self.assertIn("write_allocate=False", repr(bypass))
        self.assertIs(asdict(allocated)["write_allocate"], True)
        self.assertIs(asdict(bypass)["write_allocate"], False)

    def test_old_positional_constructor_keeps_address_bits_position(self):
        config = CacheConfig(64, 16, 1, "FIFO", "write-through", 24)
        self.assertEqual(config.address_bits, 24)
        self.assertIs(config.write_allocate, True)


if __name__ == "__main__":
    unittest.main()
