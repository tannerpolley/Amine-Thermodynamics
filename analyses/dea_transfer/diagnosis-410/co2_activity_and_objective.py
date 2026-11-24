"""#410 follow-up probes.

1. Why the fit kept the carbamate-hydrolysis constant: split of the fitted objective (Lawson vs Carson)
   when ln K_hydrolysis is raised with every other value fixed.
2. What sets the CO2 activity at high loading: molality-basis gamma(CO2) and ln p(CO2) sensitivity to the
   unfitted CO2-DEA, CO2-protonated DEA and CO2-carbamate k_ij at 313.15 K, 25 wt% DEA.
Run: AGENT_HEAVY_CORES=1 .venv/bin/python analyses/dea_transfer/diagnosis-410/co2_activity_and_objective.py <scratch-run-dir>
"""
import copy, math, sys
from pathlib import Path
from common import endpoint, route, save
from pressure_shape import SPECIES, M_W, law, k_ij
from epcsaft import equilibrium as eq

WATER_25 = 17.50797101127487
CO2_PAIRS = ('diethanolamine', 'protonated-diethanolamine', 'carbamate-anion')


def objective(r, point, shift):
    p = copy.deepcopy(point)
    law(p, 'carbamate-hydrolysis')['a'] += shift
    rows, ok, cost = r.replay(p)
    assert ok
    split = {}
    for row in rows:
        split[row['group']] = split.get(row['group'], 0.0)+row['cost']
    return dict(shift=shift, cost=cost, by_group=split)


def state(r, point, alpha):
    spec = r.bind(point)
    res = eq.solve_equilibrium(spec.model, spec.problem('loaded-bubble', dict(T=313.15, P=1e4, water=WATER_25, alpha=alpha)))
    assert res.requested_tolerance_met
    x = dict(zip(SPECIES, res.mole_fractions[:9]))
    liquid = next(a for a in eq.reaction_activities(spec.model, res) if a.phase_index == 0 and a.basis.startswith('common-molality'))
    a = dict(zip(SPECIES, liquid.species.activities))
    return res.pressure*res.mole_fractions[9], a['carbon-dioxide']/(x['carbon-dioxide']/(x['water']*M_W))


def main(out):
    r, point = route(out), endpoint(out)
    obj = [objective(r, point, s) for s in (0.0, 0.5, 0.9)]
    alphas = (1e-4, 0.5, 1.0, 1.1)
    base = {a: state(r, point, a) for a in alphas}
    sens = {}
    for other in CO2_PAIRS:
        p = copy.deepcopy(point)
        k_ij(p, 'carbon-dioxide', other)['magnitude'] += 0.05
        moved = {a: state(r, p, a) for a in alphas}
        sens[other] = {a: dict(dlnp_per_0_05=math.log(moved[a][0]/base[a][0]), gamma_CO2=moved[a][1]) for a in alphas}
    save('diagnosis-410/co2-activity-and-objective.json', dict(objective_vs_hydrolysis_shift=obj,
         base={a: dict(p_CO2_Pa=v[0], gamma_CO2=v[1]) for a, v in base.items()}, co2_k_ij_plus_0_05=sens))
    for o in obj:
        print(f"ln K_hyd +{o['shift']}: cost {o['cost']:.4f} ", {g: round(c, 4) for g, c in o['by_group'].items()})
    for a, v in base.items():
        print(f"alpha {a}: p_CO2 {v[0]:.4g} Pa gamma_CO2 {v[1]:.3f}", {o: round(sens[o][a]['dlnp_per_0_05'], 3) for o in CO2_PAIRS})


if __name__ == '__main__':
    main(Path(sys.argv[1]))
