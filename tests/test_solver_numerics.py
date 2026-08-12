from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from MEA.common.solver_acceptance import evaluate_solver_acceptance
from MEA.epcsaft_ionic import model


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


def test_reactive_paths_pass_row_mea_fraction_to_material_totals(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeEpcsaft:
        class ReactiveSpeciationOptions:
            def __init__(self, **kwargs) -> None:
                self.options = kwargs

        @staticmethod
        def solve_reactive_speciation(**kwargs):
            captured["totals"] = kwargs["totals"]
            return SimpleNamespace(
                x=dict(zip(model.SPECIES, kwargs["initial_x"])),
                mass_balance_residuals={name: 0.0 for name in kwargs["balances"]},
                reaction_residuals=[0.0],
                success=True,
                message="converged",
                charge_residual=0.0,
                state_failure_count=0,
                activity_coefficients={species: 1.0 for species in model.SPECIES},
            )

        @staticmethod
        def solve_reactive_electrolyte_bubble_sweep(**kwargs):
            captured["bubble_totals"] = [point["totals"] for point in kwargs["points"]]
            return [SimpleNamespace() for _ in kwargs["points"]]

    monkeypatch.setattr(model, "load_epcsaft", FakeEpcsaft)
    initial_x = np.full(len(model.SPECIES), 1.0 / len(model.SPECIES))
    result = model.solve_activity_speciation(
        loading=0.4,
        T=313.15,
        P=101325.0,
        initial_x=initial_x,
        values={},
        mea_weight_fraction=0.6,
        reactions=(SimpleNamespace(name="R1"),),
    )

    assert result.accepted
    assert captured["totals"] == pytest.approx(
        model.apparent_totals(loading=0.4, mea_weight_fraction=0.6)
    )
    assert captured["totals"] != pytest.approx(
        model.apparent_totals(loading=0.4, mea_weight_fraction=0.3)
    )

    monkeypatch.setattr(model, "reaction_definitions", lambda temperature: ())
    monkeypatch.setattr(model, "reactive_electrolyte_options", lambda pressure: {})
    targets = [
        model.VLETarget(
            row_id=f"row-{mea_fraction}",
            source_key="toy",
            T=313.15,
            P=101325.0,
            loading=0.4,
            mea_weight_fraction=mea_fraction,
            pressure_kPa=10.0,
            x=initial_x,
            paper="toy",
            split="toy",
            group_id="toy",
        )
        for mea_fraction in (0.15, 0.45)
    ]
    model.solve_reactive_bubble_targets(targets, values={})

    assert captured["bubble_totals"] == [
        model.apparent_totals(loading=0.4, mea_weight_fraction=mea_fraction)
        for mea_fraction in (0.15, 0.45)
    ]
