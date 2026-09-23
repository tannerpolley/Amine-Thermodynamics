"""Evaluate fixed-bundle finite-dose absorption heat from Engine total enthalpy.

Every heat calculation needs the anchored species reference enthalpies, whose
reaction constraints are the EOS-standard-state reaction enthalpies
RT^2 d ln K_rho/dT.  That derivative needs sum_i nu_i dLambda_i/dT|_P, the
temperature derivative of the source-to-EOS reference transfer, which the
pinned Engine does not expose.  The calculation that produced the retained
calorimetry results is in Git history.
"""

from __future__ import annotations


THERMAL_REFERENCE_UNAVAILABLE = (
    "reaction-reference temperature derivatives are unavailable in the pinned "
    "Engine (tannerpolley/ePC-SAFT#84, EqID "
    "standard_state_transfer_temperature_derivative); the anchored thermal "
    "reference and every heat calculation that consumes it cannot be evaluated"
)


def main() -> None:
    raise RuntimeError(THERMAL_REFERENCE_UNAVAILABLE)


if __name__ == "__main__":
    main()
