"""Evaluate MDEA starts from a caller-supplied route and declaration."""
# ruff: noqa: E402
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import refit
from refit import np, reg


class Starts:
    def __init__(self, run, point):
        self.run, self.point = run, point
        self.spec = run.bind(point)
        self.native = self.spec.coordinates()
        self.rows = self.spec.inputs['observations']['fitted']
        self.lower, self.upper, self.origin, self.scale = (
            np.array([getattr(q, k) for q in self.native]) for k in ('lower', 'upper', 'origin', 'scale')
        )
        self.candidates = refit.qmc.LatinHypercube(d=len(self.native), seed=refit.SEED).random(64)

    def vector(self, draw):
        return self.lower + (self.upper-self.lower)*self.candidates[draw]

    def at(self, values):
        u = ((np.asarray(values)-self.origin)/self.scale).tolist()
        chart = reg.evaluate_coordinates(self.spec.parameters, self.native, u, [], thermochemistry=self.spec.thermal)
        report = dict(physical=chart.physical, optimizer=u, reactions=self.point['reactions'])
        return self.run.bind(self.run.endpoint_mapping(self.point, report, self.point['coordinates']))

    def census(self, values):
        spec = self.at(values)
        return [{k: q.get(k) for k in ('identity', 'group', 'status', 'message', 'value', 'requested_tolerance_met')}
                for q in map(spec.prediction, spec.inputs['observations']['fitted'])]
