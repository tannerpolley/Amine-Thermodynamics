from __future__ import annotations

import unittest

import numpy as np

from MEA.common.solver_acceptance import evaluate_solver_acceptance


class SolverAcceptanceTests(unittest.TestCase):
    def valid_inputs(self) -> dict[str, object]:
        return {
            "solver_returned_success": True,
            "message": "converged",
            "x": np.array([0.2, 0.3, 0.5]),
            "mass_balance_residuals": {"amine": 1.0e-9, "carbon": -2.0e-9},
            "charge_residual": 3.0e-8,
            "reaction_residuals": {"R1": 4.0e-9, "R2": -5.0e-9},
            "state_failure_count": 0,
        }

    def test_accepts_only_a_converged_finite_normalized_state_within_residual_gates(self) -> None:
        decision = evaluate_solver_acceptance(**self.valid_inputs())

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.rejection_reasons, ())
        self.assertEqual(decision.rejection_reason, "")

    def test_rejects_best_effort_state_even_when_the_vector_is_finite(self) -> None:
        inputs = self.valid_inputs()
        inputs["solver_returned_success"] = True
        inputs["message"] = "chemical equilibrium did not converge"

        decision = evaluate_solver_acceptance(**inputs)

        self.assertFalse(decision.accepted)
        self.assertIn("message_not_converged", decision.rejection_reasons)

    def test_rejects_each_scientific_gate_with_explicit_reasons(self) -> None:
        inputs = self.valid_inputs()
        inputs.update(
            {
                "x": np.array([0.0, 0.2, 0.7]),
                "mass_balance_residuals": {"amine": 2.0e-7},
                "charge_residual": 2.0e-6,
                "reaction_residuals": {"R1": 2.0e-7},
                "state_failure_count": 1,
            }
        )

        decision = evaluate_solver_acceptance(**inputs)

        self.assertEqual(
            set(decision.rejection_reasons),
            {
                "mole_fractions_not_strictly_positive",
                "mole_fractions_not_normalized",
                "mass_balance_residual_exceeds_tolerance",
                "charge_residual_exceeds_tolerance",
                "reaction_residual_exceeds_tolerance",
                "state_evaluation_failed",
            },
        )

    def test_rejects_nonfinite_values(self) -> None:
        inputs = self.valid_inputs()
        inputs["x"] = np.array([0.2, np.nan, 0.8])
        inputs["charge_residual"] = np.inf

        decision = evaluate_solver_acceptance(**inputs)

        self.assertIn("mole_fractions_nonfinite", decision.rejection_reasons)
        self.assertIn("charge_residual_nonfinite", decision.rejection_reasons)


if __name__ == "__main__":
    unittest.main()
