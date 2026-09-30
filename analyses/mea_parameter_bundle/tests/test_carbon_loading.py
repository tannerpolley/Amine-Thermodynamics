"""The canonical request conserves the measured CO2 loading, including ionic carbon."""

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "calibration-misfit"))
import probe  # noqa: E402


def test_vle_obs_0203_conserved_carbon_loading():
    row = next(r for r in csv.DictReader(probe.shared.CANONICAL_VLE.open())
               if r["observation_id"] == "vle_obs_0203")
    observation, = probe.pressure_observations(lambda r: r["observation_id"] == row["observation_id"])
    carbon, mea = observation["request"]["reaction_system"]["conserved_totals"]
    # Remove the two carbons per MEA; 1e-12 mol allows floating-point summation error.
    assert math.isclose(carbon - 2 * mea, float(row["CO2_loading"]) * mea, rel_tol=0, abs_tol=1e-12)
