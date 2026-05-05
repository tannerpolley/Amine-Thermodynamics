from __future__ import annotations

import unittest

import numpy as np

from MEA.common.config import CANONICAL_MEA_WEIGHT_FRACTION, CANONICAL_TEMPERATURE_K
from MEA.nine_species.chemistry import _residual_success, balance_matrix, solve_all_species_result


class NineSpeciesChemistryTests(unittest.TestCase):
    def test_balance_matrix_uses_physical_carbon_accounting(self) -> None:
        np.testing.assert_array_equal(
            balance_matrix()[0],
            np.array([1, 0, 0, 0, 1, 1, 1, 0, 0], dtype=float),
        )

    def test_residual_success_uses_physical_carbon_balance(self) -> None:
        residuals = {
            "model_carbon_balance": 0.1,
            "physical_carbon_balance": 0.0,
            "mea_balance": 0.0,
            "water_balance": 0.0,
            "charge_balance": 0.0,
            "logK_residual_1": 0.0,
        }
        success, message = _residual_success(np.ones(9) / 9.0, residuals)
        self.assertTrue(success, message)

    def test_high_loading_point_solves_with_physical_carbon_balance(self) -> None:
        result = solve_all_species_result(0.5, CANONICAL_MEA_WEIGHT_FRACTION, CANONICAL_TEMPERATURE_K)
        self.assertTrue(result.success, result.message)
        self.assertLess(abs(result.residuals["physical_carbon_balance"]), 1e-3)


if __name__ == "__main__":
    unittest.main()
