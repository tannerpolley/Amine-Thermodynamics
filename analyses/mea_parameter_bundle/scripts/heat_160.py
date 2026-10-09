"""#147 owner decision 2026-10-08: append eight integral heats to #160 F1."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
BUNDLE = Path(__file__).resolve().parents[1]
OUT = BUNDLE / 'results/heat-160'
os.environ.setdefault('SENSITIVITY_OUTPUT', str(OUT))
os.environ.setdefault('FINAL_POOL', '0')
import d1_density_cp_160 as d1
s = d1.s
PIN = json.loads((OUT / 'engine.json').read_text())
s.ENGINE_WHEEL_SHA256, s.ENGINE_COMMIT = PIN['wheel_sha256'], PIN['commit']
import born_form_diagnosis as d
import verify_reference_calorics as thermal
import numpy as np

reg, epcsaft, eq = d1.regression, d1.m.epcsaft, d1.m.eq
BASELINE = d1.ORIGINAL / 'D1-evidence/F1-double-prime-candidate-parameters.json'
BASE = s.parameter_mapping(BASELINE)
IDS, SCALES = d1.IDS, d1.SCALES
ADMISSION = json.loads((OUT / 'inputs/heat-source-admission.json').read_text())
VINJARAPU = [r for r in ADMISSION['Vinjarapu2024']['rows'] if r['role_147'] == 'heat_calibration']
ARCIS = [dict(r, uH_J_per_mol_CO2=float(r['heat_residual_scale_J_per_mol_CO2']),
              observed_addition_enthalpy_J_per_mol_CO2=float(r['observed_addition_enthalpy_J_per_mol_CO2']),
              alpha_final=float(r['alpha_final']), temperature_K=float(r['temperature_K']),
              system_pressure_Pa=float(r['system_pressure_Pa']))
         for r in csv.DictReader((OUT / 'inputs/Arcis_2011_calorimetry_30wt.csv').open())
         if r['role_147'] == 'required_independent_heat_comparison']
assert len(VINJARAPU) == 8 and len(ARCIS) == 14
assert [r['observed_addition_enthalpy_J_per_mol_CO2'] for r in VINJARAPU] == [-80000, -79000, -85000, -81000, -84000, -82000, -84000, -83000]
assert [r['uH_J_per_mol_CO2'] for r in VINJARAPU] == [3000, 3000, 4000, 4000, 3000, 6000, 3000, 3000]


def save(name, value):
    s.write_json(OUT / name, value)


def heat_items(mapping, params, sources):
    request = s.corrected_request(d1.m.request(mapping, 313.15, .11), s.reaction_values(mapping))
    reactions = s._problem_from_request(request).reactions
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']}
    solvent = {'monoethanolamine': 1., 'water': masses['monoethanolamine']*.7/(.3*masses['water'])}
    items = []
    for row in sources:
        T, P, alpha = row['temperature_K'], row['system_pressure_Pa'], row['alpha_final']
        initial, final = [eq.Problem(T=T, P=P, feed=eq.Amounts({**solvent, 'carbon-dioxide': a}),
            phases=[eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)], reactions=reactions,
            neutral_reference=s._neutral_reference(request)) for a in (0., alpha)]
        assert initial.feed.values['carbon-dioxide'] == 0. and initial.reactions == final.reactions
        items.append(reg.addition_enthalpy(params, initial, final, {'carbon-dioxide': 1.}, alpha,
            T, P, phase='vapor', observed=row['observed_addition_enthalpy_J_per_mol_CO2'],
            form='difference', scale=row['uH_J_per_mol_CO2']))
    return items


def predict(mapping, items):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=thermal.record())
    values = []
    for item in items:
        value = reg.predict(model, item)
        assert value.status.name == 'Available' and math.isfinite(value.value), (value.status.name, value.message)
        values.append(value.value)
    return values


def heat_rows(sources, values):
    return [dict(record_id=r['record_id'], temperature_K=r['temperature_K'], pressure_Pa=r['system_pressure_Pa'],
        loading=r['alpha_final'], observed_kJ_mol=r['observed_addition_enthalpy_J_per_mol_CO2']/1000,
        uH_kJ_mol=r['uH_J_per_mol_CO2']/1000, predicted_kJ_mol=y/1000,
        residual_kJ_mol=(y-r['observed_addition_enthalpy_J_per_mol_CO2'])/1000)
        for r, y in zip(sources, values, strict=True)]


def score(rows, values, residuals):
    result = {}
    for kind, mask in (('pressure', [i for i, r in enumerate(rows) if r[0].endswith('-pco2')]),
                       ('species', [i for i, r in enumerate(rows) if not r[0].endswith('-pco2')])):
        result[kind] = dict(n=len(mask), cost=math.fsum(.5*residuals[i]**2 for i in mask),
            AARD_percent=100*math.fsum(abs(values[i]/rows[i][1].observed-1) for i in mask)/len(mask))
    assert result['pressure']['n'] == 47 and result['species']['n'] == 94
    return result


def benchmark(mapping):
    import probe
    probe.OBSERVATIONS = s.load_state_packet(d.FINAL / 'state-packet.json.gz')['observations']
    ids = {r['identity'] for r in csv.DictReader((d.FINAL / 'accepted-wave/benchmark80-id-reconciliation.csv').open())}
    observations = probe.pressure_observations(lambda r: 'canonical:'+r['observation_id'] in ids)
    params = epcsaft.Parameters.from_mapping(mapping)
    rows = []
    for o in observations:
        path = d1.OUT / 'evaluation/states/F1/canonical' / (o['identity'].replace(':', '_')+'.json')
        anchor = d.anchor(json.loads(path.read_text()))
        problem = s._problem_from_request(s.corrected_request(o['request'], s.reaction_values(mapping)), anchor)
        output = next(r for r in o['request']['outputs'] if r['identity'] == 'co2-partial-pressure')
        target = o['targets'][0]
        rows.append((target['identity'], reg.observation(params, 'partial_pressure', problem,
            observed=target['observed'], form='log_ratio', mass_basis=False,
            phase=output['phase_identity'], species=('carbon-dioxide',)), 1.))
    values = predict(mapping, [r[1] for r in rows])
    assert len(values) == 21
    return dict(AARD_percent=100*math.fsum(abs(y/r[1].observed-1) for r, y in zip(rows, values))/21,
        evidence='prediction; historical benchmark previously accessed', rows=[dict(target=r[0], observed_Pa=r[1].observed,
        predicted_Pa=y) for r, y in zip(rows, values, strict=True)])


def densities(mapping):
    sources = [r for r in csv.DictReader((d1.ROOT / 'data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv').open())
        if r['property'] == 'density' and float(r['mea_mass_fraction']) == .3
        and float(r['temperature_C']) in (50., 70.) and r['co2_loading_mol_per_mol_mea'] in ('0.3', '0.4')]
    assert len(sources) == 4
    c = BASE['empirical_density_correction']['c_cm3_mol']
    return dict(c_cm3_mol=c, coefficient_refitted=False,
        rows=d1.corrected([d1.density_job(mapping, r) for r in sources], c))


def baseline():
    clock = time.monotonic()
    params, _, rows = d.rows_for(BASE, '11')
    expected = d1.load(d1.OUT / 'F1-A/native-fit.json')
    assert [r[0] for r in rows] == expected['targets'] and len(rows) == 141
    values = predict(BASE, [r[1] for r in rows])
    residuals = [math.sqrt(w)*(math.log(y/item.observed) if item.form == reg.ResidualForm.LogRatio
                 else (y-item.observed)/item.scale) for (_, item, w), y in zip(rows, values, strict=True)]
    cost = math.fsum(.5*r*r for r in residuals)
    result = dict(cost=cost, expected_cost=30.089761188864866,
        relative_difference=abs(cost/30.089761188864866-1), scores=score(rows, values, residuals),
        predictions=values, weighted_residuals=residuals, targets=[r[0] for r in rows])
    save('equivalence.json', result)
    assert result['relative_difference'] <= 1e-8, 'failed wheel equivalence'
    print('EQUIVALENCE', cost, result['scores'], flush=True)
    heats = heat_rows(VINJARAPU, predict(BASE, heat_items(BASE, params, VINJARAPU)))
    result.update(Vinjarapu=heats, heat_cost=math.fsum(.5*(r['residual_kJ_mol']/r['uH_kJ_mol'])**2 for r in heats),
        Arcis=heat_rows(ARCIS, predict(BASE, heat_items(BASE, params, ARCIS))))
    save('baseline.json', result)
    result.update(benchmark80=benchmark(BASE), density=densities(BASE), wall_s=time.monotonic()-clock)
    save('baseline.json', result)
    print('BASELINE', result['heat_cost'], result['benchmark80']['AARD_percent'], flush=True)


def fit(letter):
    assert d1.load(OUT / 'equivalence.json')['relative_difference'] <= 1e-8
    original = s.parameter_mapping(d1.ORIGINAL / 'new-water-binaries-parameters.json')
    seed = BASE if letter == 'A' else original
    mapping = s.with_parameter_values(BASE, {i: s.parameter_values(seed)[i] for i in IDS})
    save(f'{letter}-start-parameters.json', mapping)
    params, _, rows = d.rows_for(mapping, '11')
    heat = heat_items(mapping, params, VINJARAPU)
    v = s.parameter_values(mapping)
    coords = [reg.coordinate(params, [('k_ij_reciprocal_temperature_slope' if i == IDS[-1] else 'k_ij',
        tuple(i.split('/')[1:3]), 1.)], origin=v[i], scale=scale, bounds=(float(lo), float(hi)))
        for i, scale, lo, hi in zip(IDS, SCALES, d.LOWER, d.UPPER, strict=True)]
    controls = reg.FitControls(maximum_iterations=40, maximum_elapsed_time_seconds=2250.)
    clock = time.monotonic()
    fitted = reg.fit(params, coords, [r[1] for r in rows]+heat, weights=[r[2] for r in rows]+[1.]*8,
        controls=controls, thermochemistry=thermal.record())
    raw = d1.m.fit_summary(fitted, time.monotonic()-clock)
    save(f'{letter}-native-fit.json', raw)
    raw.update({k: s._jsonable(getattr(fitted, k)) for k in ('residual_evaluations',
        'jacobian_evaluations', 'physical_jacobian', 'residuals')})
    raw.update(coordinates=IDS, scales=SCALES, targets=[r[0] for r in rows]+[r['record_id'] for r in VINJARAPU],
        observed=[r[1].observed for r in rows]+[r['observed_addition_enthalpy_J_per_mol_CO2'] for r in VINJARAPU],
        failures=[dict(trial=f.trial, observation=f.observation, status=f.status.name,
                       message=f.message, jacobian=f.jacobian) for f in fitted.failures],
        covariance={k: s._jsonable(getattr(fitted.covariance, k)) for k in
            ('status', 'assumption', 'rank', 'singular_values', 'physical', 'variance_factor', 'active_bounds')})
    save(f'{letter}-native-fit.json', raw)
    print('FIT', letter, raw['status'], raw['final_cost'], raw['wall_s'], flush=True)
    if raw['status'] != 'converged':
        assert raw['status'] == 'limit_reached' and raw['usable'], raw['message']
        return
    d1.m.complete(fitted)
    assert np.isfinite(fitted.optimizer_jacobian).all()
    final = s.with_parameter_values(mapping, dict(zip(IDS, fitted.physical, strict=True)))
    final.update(document_id=f'mea-heat-160-start-{letter}-unpromoted', purpose='Heat-augmented #160 fit; not adopted or physically validated.')
    assert s.reaction_values(final) == s.reaction_values(BASE)
    save(f'{letter}-parameters.json', final)
    conditional = d.design.refit.identifiability(SimpleNamespace(physical=fitted.physical, covariance=fitted.covariance),
        np.array(fitted.optimizer_jacobian).reshape(149, 5)/np.array(SCALES),
        np.array(fitted.weighted_residuals), IDS, d.LOWER, d.UPPER)
    save(f'{letter}-summary.json', dict(status=raw['status'], cost=raw['final_cost'],
        scores=score(rows, fitted.predictions[:141], fitted.weighted_residuals[:141]),
        heat_cost=math.fsum(.5*r*r for r in fitted.weighted_residuals[141:]),
        physical=dict(zip(IDS, fitted.physical)), active_bounds=[IDS[i] for i in fitted.covariance.active_bounds],
        conditional_uncertainty=conditional, uncertainty_basis='native exact weighted Jacobian; existing #160 conditional covariance calculation, active coordinates held fixed',
        Vinjarapu=heat_rows(VINJARAPU, fitted.predictions[141:])))


def assess(letter):
    mapping = d1.load(OUT / f'{letter}-parameters.json')
    params = epcsaft.Parameters.from_mapping(mapping)
    summary = d1.load(OUT / f'{letter}-summary.json')
    summary.update(Arcis=heat_rows(ARCIS, predict(mapping, heat_items(mapping, params, ARCIS))),
                   benchmark80=benchmark(mapping), density=densities(mapping))
    save(f'{letter}-summary.json', summary)
    print('ASSESS', letter, summary['benchmark80']['AARD_percent'], flush=True)


if __name__ == '__main__':
    s.verify_wheel()
    assert all(hashlib.sha256((d1.ROOT / p).read_bytes()).hexdigest() == h
               for p, h in d1.load(OUT / 'inputs.json')['files'].items())
    if sys.argv[1] == 'baseline':
        baseline()
    elif sys.argv[1] == 'fit':
        fit(sys.argv[2])
    else:
        assess(sys.argv[2])
