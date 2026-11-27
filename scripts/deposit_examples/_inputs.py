"""Read the selected endpoint and verify the deposited wheel."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analyses.amines.fit import fingerprint as fingerprint, retained_endpoint, route_for
from analyses.amines.records import RESULTS as RESULTS, read as read
from analyses.amines.wheel import verify


def endpoint(fit_set):
    verify()
    point, _ = retained_endpoint(fit_set)
    return route_for(fit_set), point
