"""Load the selected #440 endpoint and verify the installed Engine bytes."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / 'analyses/fixed_reaction_reference'
RESULTS = STUDY / 'results'
sys.path.insert(0, str(STUDY))

from refit import a, fingerprint, r  # noqa: E402


def endpoint(design):
    a.study.reuse.bind_wheel()
    r.verify()
    selection = r.read(RESULTS / design / 'selection.json')
    record = r.read(RESULTS / design / (selection['selected'] + '.json.gz'))
    point = record['endpoint']
    assert record['wheel'] == r.SHA
    assert fingerprint(point) == selection['endpoint_fingerprint']
    return point
