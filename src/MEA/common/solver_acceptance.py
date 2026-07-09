from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


MASS_BALANCE_TOLERANCE = 1.0e-7
CHARGE_TOLERANCE = 1.0e-6
REACTION_TOLERANCE = 1.0e-7
NORMALIZATION_TOLERANCE = 1.0e-8


@dataclass(frozen=True)
class AcceptanceDecision:
    accepted: bool
    rejection_reasons: tuple[str, ...]

    @property
    def rejection_reason(self) -> str:
        return ";".join(self.rejection_reasons)


def _residual_rejection(
    residuals: Mapping[str, float],
    *,
    missing_reason: str,
    nonfinite_reason: str,
    tolerance_reason: str,
    tolerance: float,
) -> str | None:
    if not residuals:
        return missing_reason
    values = tuple(float(value) for value in residuals.values())
    if not all(math.isfinite(value) for value in values):
        return nonfinite_reason
    if max(abs(value) for value in values) > tolerance:
        return tolerance_reason
    return None


def evaluate_solver_acceptance(
    *,
    solver_returned_success: bool,
    message: str,
    x: Sequence[float] | np.ndarray,
    mass_balance_residuals: Mapping[str, float],
    charge_residual: float,
    reaction_residuals: Mapping[str, float],
    state_failure_count: int,
    mass_balance_tolerance: float = MASS_BALANCE_TOLERANCE,
    charge_tolerance: float = CHARGE_TOLERANCE,
    reaction_tolerance: float = REACTION_TOLERANCE,
    normalization_tolerance: float = NORMALIZATION_TOLERANCE,
) -> AcceptanceDecision:
    reasons: list[str] = []
    if not solver_returned_success:
        reasons.append("solver_returned_unsuccessful")
    if message.strip().lower() != "converged":
        reasons.append("message_not_converged")

    mole_fractions = np.asarray(x, dtype=float)
    if mole_fractions.ndim != 1 or mole_fractions.size == 0:
        reasons.append("mole_fraction_vector_invalid")
    elif not np.all(np.isfinite(mole_fractions)):
        reasons.append("mole_fractions_nonfinite")
    else:
        if not np.all(mole_fractions > 0.0):
            reasons.append("mole_fractions_not_strictly_positive")
        if not math.isclose(float(np.sum(mole_fractions)), 1.0, rel_tol=0.0, abs_tol=normalization_tolerance):
            reasons.append("mole_fractions_not_normalized")

    mass_reason = _residual_rejection(
        mass_balance_residuals,
        missing_reason="mass_balance_residuals_missing",
        nonfinite_reason="mass_balance_residual_nonfinite",
        tolerance_reason="mass_balance_residual_exceeds_tolerance",
        tolerance=mass_balance_tolerance,
    )
    if mass_reason:
        reasons.append(mass_reason)

    charge = float(charge_residual)
    if not math.isfinite(charge):
        reasons.append("charge_residual_nonfinite")
    elif abs(charge) > charge_tolerance:
        reasons.append("charge_residual_exceeds_tolerance")

    reaction_reason = _residual_rejection(
        reaction_residuals,
        missing_reason="reaction_residuals_missing",
        nonfinite_reason="reaction_residual_nonfinite",
        tolerance_reason="reaction_residual_exceeds_tolerance",
        tolerance=reaction_tolerance,
    )
    if reaction_reason:
        reasons.append(reaction_reason)

    if int(state_failure_count) != 0:
        reasons.append("state_evaluation_failed")

    return AcceptanceDecision(accepted=not reasons, rejection_reasons=tuple(reasons))
