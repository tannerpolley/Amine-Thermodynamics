from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from MEA.epcsaft_ionic.speciation_feasibility import ActivityState, solve_activity_speciation
from MEA.smith_missen.ideal_speciation import SPECIES_9, solve_ideal_speciation


ROOT = Path(__file__).resolve().parents[1]


class IdealActivityEvaluator:
    def __init__(self) -> None:
        self.evaluation_count = 0

    def evaluate(self, temperature_K: float, pressure_Pa: float, mole_fractions: np.ndarray) -> ActivityState:
        del temperature_K, pressure_Pa
        self.evaluation_count += 1
        charge = (
            mole_fractions[3]
            + mole_fractions[7]
            - mole_fractions[4]
            - mole_fractions[5]
            - 2.0 * mole_fractions[6]
            - mole_fractions[8]
        )
        if abs(charge) > 1.0e-14:
            raise ValueError(f"provider received charge-imbalanced state: {charge}")
        return ActivityState(
            log_activities=np.log(np.clip(mole_fractions, 1.0e-300, None)),
            convention="mole_fraction_activity",
            diagnostics={"model": "ideal"},
        )


def test_reactive_solver_reproduces_independent_ideal_solution() -> None:
    reference = solve_ideal_speciation(0.4, 0.3, 313.15)
    evaluator = IdealActivityEvaluator()
    result = solve_activity_speciation(
        loading=0.4,
        mea_weight_fraction=0.3,
        temperature_K=313.15,
        pressure_Pa=101325.0,
        evaluator=evaluator,
        initial_mole_fractions=reference.mole_fractions,
    )

    assert result.success
    assert result.max_abs_residual < 1.0e-8
    assert np.sum(result.mole_fractions) == pytest.approx(1.0, abs=1.0e-12)
    assert result.mole_fractions == pytest.approx(reference.mole_fractions, rel=1.0e-7, abs=1.0e-12)
    assert result.provider_evaluations == evaluator.evaluation_count


def test_reactive_solver_rejects_invalid_activity_evaluations() -> None:
    class InvalidEvaluator:
        def __init__(self, state: ActivityState) -> None:
            self.state = state

        def evaluate(self, temperature_K: float, pressure_Pa: float, mole_fractions: np.ndarray) -> ActivityState:
            del temperature_K, pressure_Pa, mole_fractions
            return self.state

    invalid_states = (
        (
            ActivityState(np.zeros(len(SPECIES_9)), "unknown_standard_state", {}),
            "mole_fraction_activity",
        ),
        (
            ActivityState(np.full(len(SPECIES_9), np.nan), "mole_fraction_activity", {}),
            "nonfinite log activities",
        ),
    )
    for state, message in invalid_states:
        with pytest.raises(ValueError, match=message):
            solve_activity_speciation(
                loading=0.4,
                mea_weight_fraction=0.3,
                temperature_K=313.15,
                pressure_Pa=101325.0,
                evaluator=InvalidEvaluator(state),
            )


def test_feasibility_runs_converge_repeatably() -> None:
    path = ROOT / "analyses/phase3/reactive_speciation_feasibility/results/reactive_speciation_feasibility_receipt.json"
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert receipt["clean_lane"]["all_runs_successful"] is True
    for state in receipt["clean_lane"]["states"]:
        assert state["max_repeat_mole_fraction_spread"] < 1.0e-10
        for run in state["runs"]:
            assert run["success"] is True
            assert run["max_abs_residual"] < 1.0e-8
