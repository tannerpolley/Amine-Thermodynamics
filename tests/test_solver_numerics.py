from __future__ import annotations

import numpy as np

from MEA.common.solver_acceptance import evaluate_solver_acceptance


def _valid_inputs() -> dict[str, object]:
    return {
        "solver_returned_success": True,
        "message": "converged",
        "x": np.array([0.2, 0.3, 0.5]),
        "mass_balance_residuals": {"amine": 1.0e-9, "carbon": -2.0e-9},
        "charge_residual": 3.0e-8,
        "reaction_residuals": {"R1": 4.0e-9, "R2": -5.0e-9},
        "state_failure_count": 0,
    }


def test_accepts_converged_normalized_state_within_residual_tolerances() -> None:
    decision = evaluate_solver_acceptance(**_valid_inputs())
    assert decision.accepted
    assert decision.rejection_reasons == ()


def test_rejects_nonconverged_nonfinite_or_out_of_tolerance_states() -> None:
    cases = (
        ({"message": "chemical equilibrium did not converge"}, {"message_not_converged"}),
        (
            {"x": np.array([0.2, np.nan, 0.8]), "charge_residual": np.inf},
            {"mole_fractions_nonfinite", "charge_residual_nonfinite"},
        ),
        (
            {
                "x": np.array([0.0, 0.2, 0.7]),
                "mass_balance_residuals": {"amine": 2.0e-7},
                "charge_residual": 2.0e-6,
                "reaction_residuals": {"R1": 2.0e-7},
                "state_failure_count": 1,
            },
            {
                "mole_fractions_not_strictly_positive",
                "mole_fractions_not_normalized",
                "mass_balance_residual_exceeds_tolerance",
                "charge_residual_exceeds_tolerance",
                "reaction_residual_exceeds_tolerance",
                "state_evaluation_failed",
            },
        ),
    )
    for changes, expected_reasons in cases:
        inputs = _valid_inputs()
        inputs.update(changes)
        decision = evaluate_solver_acceptance(**inputs)
        assert not decision.accepted
        assert expected_reasons <= set(decision.rejection_reasons)
