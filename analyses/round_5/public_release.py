"""Replay the three S13 examples using only the isolated public conda package."""
import argparse
import json
import math
import platform
from pathlib import Path
from time import monotonic
from tempfile import TemporaryDirectory

from common import ROOT, RESULTS, digest, fingerprints
from part_ii import eq, epcsaft, reg, stable
from reference_states_428 import balances, phase, phase_passed

RECORD = ROOT / 'analyses/mea_parameter_bundle/results/reference-states-428/s12.json'
PARAMS = ROOT / 'analyses/mea_parameter_bundle/results/selected-current-best-parameters.json'
PACKAGE_SHA = '3945ef7b5ad038196c64055daf194c380be0c86275ccb2ae2625a8229d760a31'


def calculate(package, study_control):
    if study_control:
        from part_ii import Route
        from recall import DECLARATION
        with TemporaryDirectory() as work:
            Route(DECLARATION, Path(work))
    else:
        check_public(package)
    calculate_states(package, study_control)


def check_public(package):
    assert epcsaft.__version__ == '1.3.2' and digest(package) == PACKAGE_SHA
    assert '.venv' not in Path(epcsaft.__file__).parts


def calculate_states(package, study_control, *, params=PARAMS, reference=RECORD, output=None):
    started = monotonic()
    record = stable.read(reference)
    retained = record['retained'] if isinstance(record, dict) else record
    spec = stable.bind(stable.s.parameter_mapping(params))
    ids = spec.parameters.component_ids
    formulas = [spec.spec['element_formulas'][c] for c in ids]
    model = spec.model
    outputs = []
    for ref in retained:
        group = ref['group']
        obs = next(o for o in spec.inputs['observations']['fitted'] if o['group'] == group)
        problem = spec.problems[obs['problem']]
        initial = 50000. if group == 'Cai' else problem.P.guess
        problem.T, problem.feed = ref['T_K'], eq.Amounts(ref['feed'])
        answers = []
        for factor, target in zip((1.,1.5), ref['answers'], strict=True):
            row = dict(starting_Pa=initial*factor)
            answers.append(row)
            try:
                problem.P = eq.Free(row['starting_Pa'])
                result = eq.solve_equilibrium(model, problem)
                row.update(message=result.message, success=result.requested_tolerance_met, solver_settings=result.solver_settings,
                           max_equilibrium_residual=max(map(abs, result.residuals), default=None), row_tolerance=problem.row_tolerance)
                if not result.requested_tolerance_met:
                    row['disposition'] = 'Numerical miss'
                    continue
                n, rho, T, P = result.amounts, result.molar_densities, result.temperature, result.pressure
                x, y = (result.phase_mole_fractions(i) for i in range(2))
                xs = [list(x), list(y)]
                physical = [phase(model, T, P, ni, rhoi, xi, formulas) for ni, rhoi, xi in zip(n,rho,xs,strict=True)]
                atom = balances([ref['feed'].get(c, 0) for c in ids], physical, formulas)
                states = [model.state(T,rho=rhoi,x=xi) for rhoi,xi in zip(rho,xs,strict=True)]
                fugacity = {c: math.log(xi/yi) + a-b for c,xi,yi,a,b in
                            zip(ids,x,y,states[0].log_fugacity_coefficient,states[1].log_fugacity_coefficient,strict=True)
                            if xi > 0 and yi > 0}
                density = reg.predict(model, reg.observation(spec.parameters,'phase_density',problem,observed=1000.,
                                      scale=1.,form='difference',phase=problem.phases[0].name,mass_basis=True))
                values = dict(bubble_pressure_Pa=P,molar_density_mol_m3=rho[0],
                              density_kg_m3=density.value if density.status.name=='Available' else None)
                terms = ('hard_chain','dispersion','association','debye_huckel','born','cation_mixing','dipolar','residual_helmholtz')
                values.update({t:getattr(states[0],t) for t in terms})
                values.update({'x_'+c:v for c,v in zip(ids,x,strict=True)})
                assert values.keys() == target.keys()
                checks = {k: dict(value=v, target=target[k], difference=v-target[k] if v is not None else None,
                                  displayed_match=v is not None and format(v,'.10g') == format(target[k],'.10g')) for k,v in values.items()}
                row.update(quantities=checks, phases=physical, balances=atom, fugacity_log_ratios=fugacity,
                           checks=dict(phase=all(phase_passed(p,P,problem.row_tolerance) for p in physical),
                                       elements=max(map(abs,atom['scaled_element_residual'].values()))<=problem.row_tolerance,
                                       fugacity=max(map(abs,fugacity.values()),default=0.)<=problem.row_tolerance))
                row['disposition'] = 'Match' if all(row['checks'].values()) and all(v['displayed_match'] for v in checks.values()) else 'Numerical miss'
            except (AttributeError, TypeError, ValueError, RuntimeError, AssertionError) as error:
                row.update(disposition='Call refused', refusal=f'{type(error).__name__}: {error}')
        outputs.append(dict(group=group, temperature_K=ref['T_K'], feed=ref['feed'], answers=answers))
    path = output or RESULTS / 'records' / ('study-wheel-S13-controls.json' if study_control else 'public-1.3.2.json')
    path.write_text(json.dumps(dict(platform=platform.platform(), python=platform.python_version(),
                                    package=package.name if package else None, package_sha256=digest(package) if package else None, engine=epcsaft.__version__,
                                    declaration_inputs=fingerprints(reference, params), rows=outputs,
                                    seconds=monotonic()-started), indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path, nargs='?')
    parser.add_argument('--study-control', action='store_true')
    args = parser.parse_args()
    calculate(args.package, args.study_control)
