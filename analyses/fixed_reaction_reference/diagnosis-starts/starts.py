"""Shared setup for the issue #429 MDEA start probes (pinned study wheel only)."""
# ruff: noqa: E402
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import refit
from refit import OUT, np, r, reg

refit.a.study.reuse.bind_wheel()
r.verify()
MANIFEST = r.read(OUT/'MDEA/manifest.json.gz')
POINT = MANIFEST['start_A_declaration']
RUN = refit.configured('MDEA', 'diagnosis-starts')[0]
SPEC = RUN.bind(POINT)
NATIVE = SPEC.coordinates()
ROWS = SPEC.inputs['observations']['fitted']
LOWER, UPPER, ORIGIN, SCALE = (np.array([getattr(q, k) for q in NATIVE]) for k in ('lower', 'upper', 'origin', 'scale'))
CANDIDATES = refit.qmc.LatinHypercube(d=len(NATIVE), seed=refit.SEED).random(64)


def vector(draw):
    """Physical start vector of a Latin-hypercube draw, as the campaign formed it."""
    return LOWER + (UPPER-LOWER)*CANDIDATES[draw]


def at(values):
    """Specification bound at a physical coordinate vector."""
    u = (np.asarray(values)-ORIGIN)/SCALE
    chart = reg.evaluate_coordinates(SPEC.parameters, NATIVE, u.tolist(), [], thermochemistry=SPEC.thermal)
    report = dict(physical=chart.physical, optimizer=u.tolist(), reactions=POINT['reactions'])
    return RUN.bind(RUN.endpoint_mapping(POINT, report, POINT['coordinates']))


def census(values):
    """Status of each fitted row evaluated alone at a physical coordinate vector."""
    spec = at(values)
    return [{k: q.get(k) for k in ('identity', 'group', 'status', 'message', 'value', 'requested_tolerance_met')}
            for q in map(spec.prediction, spec.inputs['observations']['fitted'])]
