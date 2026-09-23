"""Evaluate fixed-bundle finite-dose absorption heat from Engine total enthalpy.

Every heat calculation needs the anchored species reference enthalpies, whose
reaction constraints are the EOS-standard-state reaction enthalpies
RT^2 d ln K_rho/dT.  That derivative needs sum_i nu_i dLambda_i/dT|_P, the
temperature derivative of the source-to-EOS reference transfer.  The pinned
Engine provides it as a first-order temperature solved-state action (ePC-SAFT
#84; qualified on the adopted model in results/reference-temperature/), but this
heat calculation has not been rebuilt on it, and caloric solved-state actions
(total and ideal enthalpy) remain unavailable.  The calculation that produced
the retained calorimetry results on the superseded Engine is in Git history.
"""

from __future__ import annotations


THERMAL_REFERENCE_UNAVAILABLE = (
    "the anchored thermal reference and every heat calculation that consumes it "
    "have not been rebuilt on the pinned Engine's first-order reference temperature "
    "actions (tannerpolley/ePC-SAFT#84); caloric solved-state actions remain "
    "unavailable; the retained heat results come from the superseded Engine"
)


def main() -> None:
    raise RuntimeError(THERMAL_REFERENCE_UNAVAILABLE)


if __name__ == "__main__":
    main()
