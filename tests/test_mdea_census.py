from math import nextafter

from MEA.common.retained_results import read
from analyses.amines.mdea import census_status
from analyses.amines.records import RESULTS
from analyses.amines.wheel import verify


def test_retained_available_row_misses_tighter_tolerance():
    record = read(RESULTS / "move/mdea/reported/fit/A.json.gz")
    assert record["wheel"] == verify()
    (row,) = (r for r in record["replay"]["rows"] if r["identity"] == "fit:0")
    residual = row["convergence"]["residual"]
    requested = nextafter(residual, 0.0)
    assert census_status(row) == "Available"
    # Hold the admitted solve in place and reconsider only its requested tolerance.
    assert census_status(dict(row, requested_tolerance_met=residual <= requested)) == "ToleranceNotMet"
