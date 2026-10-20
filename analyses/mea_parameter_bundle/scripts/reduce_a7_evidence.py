"""Reduce retained A7 results for #196; no Engine solve or differentiation."""
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
BASE = BUNDLE / 'results/joint-recalibration-170/amendment-7'
OUT = BUNDLE / 'results/a7-paper-evidence'
INPUTS = {}


def bind(path):
    INPUTS[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def load(path):
    return json.loads(bind(path).read_text())


def read(path):
    return list(csv.DictReader(bind(path).open()))


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def table(name, rows):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(k for r in rows for k in r)), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def coefficients(node):
    if isinstance(node, dict):
        if 'identity' in node and isinstance(node.get('value'), dict) and 'magnitude' in node['value']:
            yield node['identity'], node['value']['magnitude']
        for value in node.values():
            yield from coefficients(value)
    elif isinstance(node, list):
        for value in node:
            yield from coefficients(value)


def uncertainty(spec, native, endpoint):
    sys.path.insert(0, str(BUNDLE / 'calibration-misfit'))
    import refit
    import verify_reference_calorics as thermal
    for path in ('calibration-misfit/refit.py', 'scripts/fit_campaign.py', 'scripts/verify_reference_calorics.py'):
        bind(BUNDLE / path)
    chemistry = load(BASE / 'restricted-2/fit/chemistry-coordinates.json')
    start = spec['information_starts'][0]
    initial = dict(coefficients(load(ROOT / start['parameters_path'])))
    values = dict(coefficients(endpoint))
    coordinates, lower, upper, physical, slopes = [], [], [], [], []
    for index, c in enumerate(spec['information_coordinates']):
        identity = c['identity']
        factor = math.copysign(c['scale'], c.get('source_to_native_factor', 1.))
        origin = initial.get(identity, 0.)
        shift = 0.
        if c.get('enthalpy_shift'):
            origin = start['reaction_enthalpy_shifts_J_mol'][c['reaction']]
            shift = origin
            value = chemistry['enthalpy_shifts_J_mol'][c['reaction']]
        elif 'reaction' in c:
            shift = -start['reaction_enthalpy_shifts_J_mol'][c['reaction']] / (thermal.R * math.log(10.))
            origin += shift
            value = chemistry['R5_unshifted_a_k']
        else:
            value = values[identity]
        assert math.isclose(value, origin + factor * native['optimizer'][index], rel_tol=1e-12, abs_tol=1e-10)
        for tie in c.get('ties', []):
            assert math.isclose(values[tie['identity']], tie['factor'] * value, rel_tol=1e-14)
        lo, hi = [b + shift for b in c['bounds']]
        coordinates.append(dict(identity=identity, optimizer_column=index, value=value, bounds=[lo, hi],
            origin=origin, d_scientific_d_optimizer=factor, ties=c.get('ties', []),
            unit='J/mol' if c.get('enthalpy_shift') else 'K' if 'reaction' in c or c['family'] in
                 ('dispersion_energy_over_k', 'k_ij_reciprocal_temperature_slope') else 'angstrom' if 'diameter' in c['family'] else 'dimensionless'))
        lower.append(lo); upper.append(hi); physical.append(value); slopes.append(factor)
    r5 = 'reaction:R5:correlation:a_k'
    assert math.isclose(values[r5], chemistry['R5_unshifted_a_k'] + chemistry['enthalpy_shifts_J_mol']['R5'] /
                        (thermal.R * math.log(10.)), rel_tol=0., abs_tol=1e-10)
    active = native['covariance']['active_bounds']
    assert active == [1, 3, 5, 7, 8, 11]
    ids = [c['identity'] for c in coordinates]
    free = [i for i in range(16) if i not in active]
    J = np.asarray(native['optimizer_jacobian']).reshape(307, 16) / np.asarray(slopes)
    residual = np.asarray(native['weighted_residuals'])
    spectrum = np.linalg.svd(J[:, free], compute_uv=False)
    rank = int(np.sum(spectrum > spectrum[0] * 1e-14))
    assert rank == 10 and np.isfinite(J).all() and np.isfinite(residual).all()
    proxy = SimpleNamespace(physical=physical, covariance=SimpleNamespace(active_bounds=active))
    result = refit.identifiability(proxy, J, residual, ids, lower, upper)
    assert np.isfinite(list(result['conditional_standard_error'].values())).all()
    assert np.isfinite(result['conditional_correlation']).all()
    result.update(coordinate_map=coordinates, free_rank=rank, free_spectrum=spectrum.tolist(), rank_relative_cutoff=1e-14,
        active_bound_indices=active, residual_count=307, degrees_of_freedom=297,
        basis='R5 unshifted source A; total inherited-plus-fitted enthalpy shifts; tied diameters as declared',
        meaning='Conditional on residual weights, fixed inputs, active bounds and local linearization; no measurement-error, uniqueness or prediction-interval claim.')
    write('conditional-uncertainty.json', result)
    table('conditional-standard-errors.csv', [dict(c, bound_active=i in active,
        conditional_standard_error=result['conditional_standard_error'].get(c['identity'])) for i, c in enumerate(coordinates)])
    table('conditional-correlations.csv', [dict(coordinate_a=a, coordinate_b=b, correlation=result['conditional_correlation'][i][j])
        for i, a in enumerate(result['free_coordinates']) for j, b in enumerate(result['free_coordinates'])])
    return coordinates


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bind(Path(__file__))
    endpoint = load(BASE / 'restricted-2/fit/usable-budget-endpoint.json')
    selected = bind(BUNDLE / 'results/selected-current-best-parameters.json')
    sha = INPUTS[str(selected.relative_to(ROOT))]
    assert selected.read_bytes() == (BASE / 'restricted-2/fit/usable-budget-endpoint.json').read_bytes()
    assert sha == 'e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e'
    spec = load(BASE / 'restricted-2/fit-spec.json')
    for item in spec['inputs']:
        assert INPUTS.setdefault(item['path'], hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()) == item['sha256']
    native = load(BASE / 'restricted-2/fit/native.json')
    replay = load(BASE / 'restricted-2/replay/A7-restricted-2-full-replay.json')
    score = load(BASE / 'fixed-study/wheel-8298c602/restricted-2-endpoint/score.json')
    declarations = {r['id']: r for r in native['rows']}
    assert len(replay) == len(declarations) == 307 and {r['target'] for r in replay} == set(declarations)
    common = set(spec['observations'][0]['ordered_row_ids'])
    loaded = set(spec['loaded_density_ids'])
    groups = {}
    fitted = []
    for row in replay:
        d = declarations[row['target']]
        assert row['status'] == 'Available' and math.isfinite(row['predicted'])
        assert all(row[k] == d.get(k, 1.) for k in ('observed', 'scale', 'weight'))
        group = ('common149' if d['id'] in common else 'loaded density' if d['id'] in loaded else 'CO2-free density'
            if d['id'].startswith('AMU-DENS') else 'Cai' if d['id'].startswith('cai') else 'Kiepe'
            if d['id'].startswith('kiepe') else 'Cp' if d['id'].startswith('Hilliard2008_Cp') else 'Jakobsen'
            if d['id'].startswith('Jakobsen') else 'restored species')
        fitted.append(dict(row, id=d['id'], quantity=d['quantity'], group=group, declaration=d))
        groups.setdefault(group, []).append(row)
        assert math.isclose(row['cost'], .5 * row['weight'] * row['residual']**2, rel_tol=1e-12, abs_tol=1e-12)
    assert {k: len(v) for k, v in groups.items()} == dict(common149=149, **{'restored species':7, 'Jakobsen':6,
        'loaded density':47, 'CO2-free density':5, 'Cai':50, 'Kiepe':39, 'Cp':4})
    for name, predicate in [('pressure', lambda r:r['target'].endswith('-pco2')),
                            ('heat', lambda r:r['target'].startswith('vinjarapu')),
                            ('species', lambda r:'::' in r['target'])]:
        groups['common149 ' + name] = [r for r in groups['common149'] if predicate(r)]
    stats = {k:dict(n=len(v), cost=math.fsum(r['cost'] for r in v),
        AARD_percent=100 * math.fsum(abs(r['predicted']/r['observed']-1) for r in v)/len(v)) for k,v in groups.items()}
    cost = math.fsum(r['cost'] for r in replay)
    assert math.isclose(cost, score['cost'], rel_tol=1e-10) and math.isclose(cost, native['final_cost'], rel_tol=1e-10)
    assert math.isclose(stats['common149']['cost'], score['C149'], rel_tol=1e-10)
    table('fitted-rows.csv', fitted)
    coordinates = uncertainty(spec, native, endpoint)
    write('fit-summary.json', dict(cost=cost, groups=stats, iterations=native['iterations'], coordinates=coordinates,
        active_bounds=native['covariance']['active_bounds'], gate_score=score, engine=spec['engine'], record_sha256=sha))
    for name in ('state-targets.csv', 'state-summary.json', 'states-excluded.json', 'states-unavailable.json',
                 'summary.json', 'verification.json', 'density.csv', 'cp.csv', 'carbonate-share.csv'):
        shutil.copyfile(bind(BASE / 'selected-assessment' / name), OUT / name)
    states = read(BASE / 'selected-assessment/state-targets.csv')
    assert len(states) == len({(r['kind'],r['identity'],r['target']) for r in states}) == 462
    assert all(r['status']=='Available' and r['record_sha256']==sha for r in states)
    for name, kind, quantity, count in [('pressure-figure-data.csv','packet','pressure',79),
        ('species-figure-data.csv','packet','species',131), ('canonical-pressure.csv','canonical','pressure',159),
        ('wagner-pressure.csv','wagner','pressure',23), ('transfer.csv','transfer','pressure',70)]:
        rows = [r for r in states if (r['kind'],r['quantity'])==(kind,quantity)]
        assert len(rows)==count
        table(name, rows)
    pool = [r for r in states if r['kind']=='packet' and r['source']=='Matin2012' and r['species']=='HCO3-']
    assert len(pool)==19 and not any(r['target'] in declarations for r in pool)
    table('pool-figure-data.csv', pool)
    state_summary = load(BASE / 'selected-assessment/state-summary.json')
    for name, cohort in state_summary['scores'].items():
        rows = [r for r in states if r['target'] in cohort['row_ids'] and r['identity'] in cohort['state_ids']]
        assert len(rows)==cohort['n_total'] and set(cohort['row_ids'])=={r['target'] for r in rows}
        aard = 100 * math.fsum(abs(float(r['predicted'])/float(r['observed'])-1) for r in rows)/len(rows)
        assert math.isclose(aard, cohort['AARD_percent'], rel_tol=1e-12)
    table('high-temperature-comparison.csv', [dict(cohort=k, **{f:v for f,v in c.items() if f not in ('row_ids','state_ids')})
        for k,c in state_summary['scores'].items() if '100-120' in k])
    heats = read(BASE / 'selected-assessment/heats.csv')
    sources = {r['record_id']:r for r in load(ROOT / spec['heat_rows_path'])}
    assert len(heats)==22 and {r['id'] for r in heats}==set(sources)
    table('heat.csv', [dict(r, scale_J_mol_CO2=sources[r['id']]['uH_J_per_mol_CO2'], unit='kJ/mol CO2',
        role='fitted' if r['id'] in declarations else 'non-fitted prediction', source_row=sources[r['id']]) for r in heats])
    phase = []
    for label, directory in [('A7','restricted-2-endpoint'), ('A6','after-adoption/a6-selected')]:
        path = BASE / 'fixed-study/wheel-8298c602' / directory
        reduction = load(path / 'reduction.json')
        assert len(reduction)==73 and {r['index'] for r in reduction}==set(range(73))
        for row in reduction:
            point = load(path / f"point-{row['index']}.json")
            phase.append(dict(record=label, **row, **{k:point[k] for k in ('temperature_K','loading','pressure_Pa')}))
    table('phase-family.csv', phase)
    predecessor = BUNDLE / 'results/heat-final-170'
    paths = [bind(predecessor / name) for name in ('fit-comparison.csv','pressure-figure-data.csv', 'species-figure-data.csv',
        'heat-comparison.csv', 'high-temperature-comparison.csv', 'corrected-densities.csv', 'heat-capacity-comparison.csv', 'evaluation/execution.json')]
    paths += [bind(BUNDLE / ('results/' + name)) for name in ('heat-160/A-parameters.json', 'engine-8298c602-adoption/comparison.json',
        'engine-8298c602-adoption/checks.json', 'engine-8298c602-adoption/README.md')]
    write('predecessor-f1.json', dict(inputs={str(p.relative_to(ROOT)):INPUTS[str(p.relative_to(ROOT))] for p in paths},
        wheel_transfer='152 named F1 quantities only, worst relative difference 2.9e-12; no qualification of other retained F1 results.'))
    write('input-hashes.json', INPUTS)
    print(json.dumps(dict(objective_rows=307, cost=cost, groups=stats, state_rows=462, phase_rows=len(phase)), indent=2))


if __name__ == '__main__':
    main()
