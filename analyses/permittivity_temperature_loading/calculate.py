"""Reference-anchored dielectric-volume sensitivity; fixed chemistry and parameters (#265)."""
import copy
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'analyses/mea_parameter_bundle'
AN = Path(__file__).resolve().parent
OUT = AN / 'results'
sys.path[:0] = [str(ROOT / 'src'), str(B / 'scripts'), str(B / 'calibration-misfit')]
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from dielectric_volume import composition, dump, scaled, specification, verify_wheel
from MEA.solvent_specification import jsonable
import phase_diagnosis_255 as phase
f = phase.f
BASE = json.loads((B / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json').read_text())
STATES = json.loads(gzip.decompress((phase.OUT / 'final/phase-results.json.gz').read_bytes()))
SPEC = ROOT / 'analyses/mea_parameter_bundle/results/adoption-297/historical-spec/MEA.toml'


def diagnostic(spec, temperature):
    problem = copy.copy(spec.problems[spec.inputs['observations']['fitted'][0]['problem']])
    problem.T, problem.P = temperature, 101325.
    x = composition(BASE, .30)
    feed = {k: v / x['monoethanolamine'] for k, v in x.items()}
    problem.feed = eq.Amounts(dict(feed, **{'carbon-dioxide': .44}))
    problem.phases = [eq.Phase('L', kind='liquid', support=spec.model.component_ids)]
    state = eq.solve_equilibrium(spec.model, problem)
    result = f.phase_payload(spec.model, problem, state)
    if state.success and state.requested_tolerance_met:
        native = spec.model.state(temperature, rho=state.molar_densities[0], x=state.phase_mole_fractions(0))
        result['bulk_relative_permittivity'] = native.bulk_relative_permittivity
    result['quantities'] = {}
    for kind, args in [('phase_density', dict(mass_basis=True)), ('equilibrium_isobaric_heat_capacity', dict(mass_basis=False))]:
        value = reg.predict(spec.model, reg.observation(spec.parameters, kind, problem, phase='L', observed=0., form='difference', scale=1., **args))
        result['quantities'][kind] = {k: jsonable(getattr(value, k)) for k in ('status', 'value', 'message', 'requested_tolerance_met')}
    problem.phases = [eq.Phase('L', kind='liquid', support=spec.model.component_ids),
                      eq.Phase('V', kind='vapor', support=spec.model.component_ids[:3], amount=eq.Pinned(0.))]
    problem.P = eq.Free(101325.)
    bubble = eq.solve_equilibrium(spec.model, problem)
    result['bubble'] = f.phase_payload(spec.model, problem, bubble)
    return result


def evaluate(case):
    name, scale, anchor = case
    spec = specification(SPEC, scale)
    records = []
    for row in spec.inputs['observations']['fitted']:
        value = spec.prediction(row)
        if value['status'] == 'Available' and value.get('requested_tolerance_met'):
            value['cost'] = .5 * row['weight'] * value['residual'] ** 2
        problem = spec.problems[row.get('problem', row.get('final', row.get('initial'))) ]
        try:
            state = eq.solve_equilibrium(spec.model, problem)
            value['epsilon_state'] = dict(requested_tolerance_met=state.requested_tolerance_met, message=state.message)
            if state.success and state.requested_tolerance_met:
                native = spec.model.state(state.temperature, rho=state.molar_densities[0], x=state.phase_mole_fractions(0))
                value['epsilon_state']['value'] = native.bulk_relative_permittivity
        except Exception as error:
            value['epsilon_state'] = dict(cause=type(error).__name__, message=str(error))
        records.append(value)
    for identity in {r['state_identity'] for r in spec.inputs['observations']['fitted'] if r['group'] == 'Cai'}:
        pair = [(r, p) for r, p in zip(spec.inputs['observations']['fitted'], records, strict=True) if r['state_identity'] == identity]
        temperature = next(p for r, p in pair if r['kind'] == 'temperature')
        admitted = len(pair) == 2 and all(p['status'] == 'Available' and p.get('requested_tolerance_met') for r, p in pair)
        admitted = admitted and pair[0][0]['temperature_domain'][0] <= temperature.get('value', -math.inf) <= pair[0][0]['temperature_domain'][1]
        for r, p in pair:
            p['paired_temperature'] = temperature.get('value')
            if not admitted:
                p['status'] = 'PairUnavailable'
                p.pop('cost', None)
    if name == 'baseline':
        reference = json.loads((SPEC.parent / 'inputs/reference.json').read_text())
        for result, ref in zip(records, reference, strict=True):
            assert result['identity'] == ref['target'] and result['status'] == 'Available' and result['requested_tolerance_met']
            for key, field in [('value', 'predicted'), ('residual', 'residual'), ('cost', 'cost')]:
                assert abs(result[key] - ref[field]) <= 1e-10 * max(abs(ref[field]), abs(result[key])), (result['identity'], key)
    groups = {g: dict(rows=sum(r['group'] == g for r in records), unavailable=sum(r['group'] == g and 'cost' not in r for r in records),
                     available_cost=math.fsum(r['cost'] for r in records if r['group'] == g and 'cost' in r)) for g in dict.fromkeys(r['group'] for r in records)}
    dump(OUT / name / 'observations.json', records)
    diagnostics = {str(T): diagnostic(spec, T) for T in (353., 393.)}
    assert all(d['success'] and d['requested_tolerance_met'] and d['bubble']['success']
               and d['bubble']['requested_tolerance_met'] for d in diagnostics.values())
    assert all(q['status'] == 'Available' and q['requested_tolerance_met']
               for d in diagnostics.values() for q in d['quantities'].values())
    dump(OUT / name / 'diagnostics.json', diagnostics)
    report = dict(name=name, scale=scale, anchor=anchor, groups=groups, rows=len(records), available=sum('cost' in r for r in records),
                  available_cost=math.fsum(r.get('cost', 0.) for r in records))
    dump(OUT / name / 'summary.json', report)
    print(json.dumps(report), flush=True)
    return report


def phase_case(task):
    name, scale, old = task
    row = {k: old[k] for k in ('index', 'temperature_K', 'loading', 'pressure_Pa')}
    path = OUT / name / f'phase-{row["index"]}.json'
    mapping = scaled(BASE, scale)
    try:
        f.family_job(mapping, phase.e.request(mapping, 313.15, .11), row, [], path)
        raw = json.loads(path.read_text())
    except Exception as error:
        raw = dict(json.loads(path.read_text()) if path.exists() else row, failure=f'{type(error).__name__}: {error}')
        raw['classification'] = f.phase_classification(raw)
    reduction = phase.reduce_state(raw)
    return name, raw, reduction


def source_comparison(model):
    rows = []
    for original in csv.DictReader((AN / 'inputs/source-values.csv').open()):
        row = dict(original)
        T, weight, loading = (float(row[k]) for k in ('T_K', 'MEA_mass_fraction', 'loading'))
        try:
            if loading == 0:
                state = model.state(T, P=101325., x=composition(BASE, weight), phase='liquid')
            else:
                problem = f.flash_problem(phase.e.request(BASE, 313.15, .11), loading, T, 101325.,
                    [eq.Phase('L', kind='liquid', support=model.component_ids)])
                liquid = eq.solve_equilibrium(model, problem)
                row['equilibrium'] = dict(success=liquid.success, requested_tolerance_met=liquid.requested_tolerance_met, residuals=list(liquid.residuals), message=liquid.message)
                if not liquid.success or not liquid.requested_tolerance_met:
                    raise ValueError('Source-state native equilibrium unavailable: ' + liquid.message)
                state = model.state(T, rho=liquid.molar_densities[0], x=liquid.phase_mole_fractions(0))
            row.update(calculated_epsilon=state.bulk_relative_permittivity, density_mol_m3=state.molar_density,
                       pressure_density_derivative=state.pressure_density_derivative,
                       relative_deviation=state.bulk_relative_permittivity / float(row['epsilon']) - 1)
        except Exception as error:
            row.update(cause=type(error).__name__, message=str(error))
        rows.append(row)
    dump(OUT / 'source-comparison.json', rows)


def main():
    started = time.monotonic()
    wheel = next((ROOT / 'build/engine-wheels').rglob('*.whl'))
    verify_wheel(wheel, f.s.ENGINE_WHEEL_SHA256)
    assert hashlib.sha256((B / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json').read_bytes()).hexdigest() == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(BASE))
    source_comparison(model)
    cases = [('baseline', 1., {})]
    for T in (353., 393.):
        x = composition(BASE, .30)
        ref = model.state(T, P=101325., x=x, phase='liquid')
        for label, delta in [('minus5', -.05 * ref.bulk_relative_permittivity), ('plus5', .05 * ref.bulk_relative_permittivity),
                             *[(f'hajj-{alpha}', epsilon - 52.855) for alpha, epsilon in [(0.22, 60.1), (.33, 63.4), (.44, 68.8), (.55, 72.4)]]]:
            scale = 1 + delta / (ref.bulk_relative_permittivity - 1)
            check = epcsaft.Mixture(epcsaft.Parameters.from_mapping(scaled(BASE, scale))).state(T, rho=ref.molar_density, x=x)
            assert abs(check.bulk_relative_permittivity - (ref.bulk_relative_permittivity + delta)) <= 1e-10
            cases.append((f'{T:g}-{label}', scale, dict(T_K=T, pressure_Pa=101325., rho_mol_m3=ref.molar_density,
                         epsilon=ref.bulk_relative_permittivity, delta=delta, fixed_density_epsilon=check.bulk_relative_permittivity)))
    dump(OUT / 'cases.json', cases)
    assert len(STATES) == len({r['index'] for r in STATES}) == 162
    with ProcessPoolExecutor(os.cpu_count()) as pool:
        summaries = list(pool.map(evaluate, cases))
        raw, reduced = {c[0]: [] for c in cases}, {c[0]: [] for c in cases}
        jobs = [(name, scale, old) for name, scale, _ in cases for old in sorted(STATES, key=lambda r: r['index'])]
        for name, state, reduction in pool.map(phase_case, jobs):
            raw[name].append(state)
            reduced[name].append(reduction)
            (OUT / name / f'phase-{state["index"]}.json').unlink(missing_ok=True)
        for summary in summaries:
            name = summary['name']
            dump(OUT / name / 'phase-results.json.gz', raw[name])
            dump(OUT / name / 'phase-reduction.json', reduced[name])
            summary['phase'] = dict(states=len(reduced[name]), resolved_descent_states=sum(r['resolved'] > 0 for r in reduced[name]),
                                   incomplete_states=sum(not r['complete'] for r in reduced[name]),
                                   classifications={k: sum(r['classification'] == k for r in reduced[name]) for k in ('failed', 'unresolved', 'passed-two-phase', 'passed-single-liquid')})
            dump(OUT / name / 'summary.json', summary)
            if name == 'baseline':
                assert summary['phase']['classifications']['passed-two-phase'] == 162 and summary['phase']['incomplete_states'] == summary['phase']['resolved_descent_states'] == 0
    dump(OUT / 'summary.json', dict(scenarios=summaries, wall_seconds=time.monotonic() - started, engine_wheel_sha256=f.s.ENGINE_WHEEL_SHA256,
         workers=os.cpu_count(), threads={k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')},
         inputs={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [SPEC, SPEC.parent / 'declarations.toml', *sorted((SPEC.parent / 'inputs').iterdir()), AN / 'inputs/source-values.csv', Path(__file__), AN / 'dielectric_volume.py', ROOT / 'src/MEA/solvent_specification.py', Path(f.__file__), Path(phase.__file__)]}))


if __name__ == '__main__':
    main()
