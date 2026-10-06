"""Issue 147 corrected campaign presolve and complete residual/Jacobian timing; no fit."""
import importlib.util
import json
import math
import os
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[2]
sys.path[:0] = [str(BUNDLE / 'scripts'), str(BUNDLE / 'calibration-misfit')]
import shared_evaluation as s
s.ENGINE_WHEEL_SHA256 = 'e8ad39e0c5d7da471a6d3ace6ff62d60518c57bc1c96fe5198d8bf18747ba8b5'
s.ENGINE_COMMIT = 'c106702048e87d0c583a3a5516cb5746e7a6ac07'
s.verify_wheel()
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
import verify_reference_calorics as thermal
spec = importlib.util.spec_from_file_location('low_temperature_fit', HERE.parent.with_name('temperature-reanchor-140') / 'low-temperature-fit.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
f.NATIVE_INPUTS = HERE.parent / 'campaign-reactions.json'
mapping, reactions, original = f.source_context()
params = epcsaft.Parameters.from_mapping(s.with_parameter_values(mapping, dict.fromkeys(f.IDS + [f.SLOPE], 0.0)))
model = epcsaft.Mixture(params, thermochemistry=thermal.record())
chart = reg.CoordinateSet()
chart.coordinates = [reg.coordinate(params, [('k_ij_reciprocal_temperature_slope' if i == f.SLOPE else 'k_ij', tuple(i.split('/')[1:3]), 1.0)], origin=0.0, scale=h, bounds=b) for i, b, h, _ in zip(*f.design('slope-fixed', '1'), strict=True)]
active_model = epcsaft.Mixture(params, thermochemistry=thermal.record(), active_parameters=chart.active())
training = BUNDLE / 'results/final-rerun/training-inputs.json'
assert s.sha256(training) == 'a063148a1c3c68765adbfca81e17d32cd327c68b035e19c84ebeb007f76bb369'
observations = json.loads(training.read_text())
rows = []
record = {'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'module_origin': epcsaft.__file__, 'checks': [], 'branches': {}, 'pool_size_available': len(os.sched_getaffinity(0))}
clock = time.perf_counter()
try:
    for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        assert os.environ[variable] == '1'
    for o in observations:
        assert o['request']['temperature']['value'] <= 333.15
        s.RUNS = BUNDLE / 'results/runs/temperature-heat-147/timing' / o['identity']
        rec = s.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=175, limits=s.EvaluationLimits(175, 175), model_fingerprint=s.parameter_fingerprint(mapping))
        check = f.check_state(rec, o)
        record['checks'].append({'identity': o['identity'], 'state': rec, 'check': check})
        f.save(HERE / 'timing.json', record)
        assert check['complete'], (o['identity'], check)
        problem = s._problem_from_request(s.corrected_request(o['request'], reactions), s.anchor_from(rec))
        rows.extend(f.refit.observations(params, o, problem, 60))
        print('presolve', o['identity'], flush=True)
    assert len(observations) == 83 and len(rows) == 141
    heat = [r for r in json.loads((HERE.parent / 'heat-source-admission.json').read_text())['Vinjarapu2024']['rows'] if r['role_147'] == 'calibration']
    solvent = {'monoethanolamine': 1.0, 'water': 7.911062165006594}
    template = s._problem_from_request(s.corrected_request(observations[0]['request'], reactions))
    heat_rows = []
    for r in heat:
        endpoints = [eq.Problem(T=313.15, P=1734000.0, feed=eq.Amounts({**solvent, 'carbon-dioxide': a}), phases=[eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)], reactions=template.reactions, neutral_reference=template.neutral_reference) for a in (0.0, r['alpha_final'])]
        heat_rows.append((r['record_id'], reg.addition_enthalpy(params, *endpoints, {'carbon-dioxide': 1.0}, r['alpha_final'], 313.15, 1734000.0, phase='vapor', observed=r['observed_addition_enthalpy_J_per_mol_CO2'], form='difference', scale=r['uH_J_per_mol_CO2']), 1.0))
    for branch, items in (('no-heat', rows), ('heat', rows + heat_rows)):
        values = []
        for identity, item, weight in items:
            t = time.perf_counter()
            p = reg.predict(model, item)
            residual_s = time.perf_counter() - t
            record['current_prediction'] = {'target': identity, **{k: s._jsonable(getattr(p, k)) for k in ('value', 'status', 'message', 'residual', 'requested_tolerance_met', 'convergence', 'branch', 'stable_root_count')}}
            f.save(HERE / 'timing.json', record)
            assert p.status.name == 'Available' and p.requested_tolerance_met is not False, (identity, p.message)
            t = time.perf_counter()
            g = reg.differentiate(active_model, item)
            values.append({'target': identity, 'prediction': p.value, 'weighted_residual': math.sqrt(weight)*p.residual, 'gradient': list(g.value), 'status': g.status.name, 'message': g.message, 'residual_s': residual_s, 'jacobian_s': time.perf_counter()-t})
            record['branches'][branch] = values
            f.save(HERE / 'timing.json', record)
            assert g.status.name == 'Available' and len(g.value) == 5 and all(math.isfinite(v) for v in g.value), (identity, g.message)
            print('timing', branch, identity, flush=True)
except Exception as error:
    record['failure'] = {'exception': type(error).__name__, 'message': str(error)}
    raise
finally:
    record.update(wall_s=time.perf_counter()-clock, maximum_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    f.save(HERE / 'timing.json', record)
