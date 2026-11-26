"""A tied fit keeps the first declared start when attempts arrive out of order."""

from analyses.amines.fit import fingerprint, select
from analyses.amines.wheel import verify


def test_fit_tie_follows_declared_start_order():
    declaration = {
        "starts": {"A": {}, "B": {}, "C": {}},
        "fit_controls": {"function_tolerance": 1e-10},
    }
    records = {
        label: dict(
            wheel=verify(),
            manifest_fingerprint=fingerprint(declaration),
            report={"status": "converged"},
            replay_passed=True,
            replay={"cost": 15.588667},
            endpoint_fingerprint=label,
        )
        for label in declaration["starts"]
    }
    ordered = select(declaration, records)
    reversed_order = select(declaration, dict(reversed(records.items())))
    assert ordered == reversed_order
    assert ordered["selected"] == "A"
