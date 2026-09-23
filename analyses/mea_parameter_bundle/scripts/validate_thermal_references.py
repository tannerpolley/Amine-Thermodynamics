"""Validate the anchored species thermal references for non-isothermal use.

The validation starts from the anchored reference, which the pinned Engine
cannot construct (see ``evaluate_direct_absorption_heat``).  The checks that
produced the retained validation results are in Git history.
"""

from __future__ import annotations

from evaluate_direct_absorption_heat import THERMAL_REFERENCE_UNAVAILABLE


def main() -> None:
    raise RuntimeError(THERMAL_REFERENCE_UNAVAILABLE)


if __name__ == "__main__":
    main()
