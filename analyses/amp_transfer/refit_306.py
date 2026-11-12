"""#306: cation A, set 1, fitted-slope refit with the two arbitrary limits widened; rescore Kundu and Tong. No adoption.

Run from the repository root: agent-heavy env PYTHONPATH=src OMP_NUM_THREADS=1 <python> analyses/amp_transfer/refit_306.py
"""
import copy, json, math, os, sys, tomllib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import kundu  # asserts the pinned Engine wheel 391dfe5d
import reactive as r
from kundu import AN, bind, current_shared, save, score, toml_value
from MEA.solvent_specification import SolventSpecification, relative_error_statistic

OUT = r.OUT = AN / 'results/refit-306'
OUT.mkdir(exist_ok=True)
(AN / 'inputs/refit-306').mkdir(exist_ok=True)
r.SHARED_ENDPOINT = AN.parent / 'solvent_specification_mea/inputs/endpoint.json'  # adopted #255/#297 shared species
WIDE = {4: [-1.0, 1.0], 6: [3.5, 6.5]}  # owner 2026-11-11: AMPH+-CO2 k and AMPCOO- diameter; all other bounds as #243
MEACOO = 5.31999516340193  # adopted MEACOO- segment diameter, owner-requested comparison floor (2026-11-12)
SIZE_ESTIMATE = 5.888119745589194  # MEACOO- x cube root of (m sigma^3 AMP + CO2)/(MEA + CO2), adopted pure parameters
H243 = -5000.0
workers = int(os.environ['AGENT_HEAVY_CORES'])

def declarations(law=None):
    decl = tomllib.loads((AN / 'declarations.toml').read_text())
    current_shared({'components': [], 'pairs': []}, decl)
    if law:
        next(x for x in decl['chemistry']['reactions']['aqueous'] if x['name'] == 'carbamate-hydrolysis')['correlation'] = law
    return '\n'.join(f'{k} = {toml_value(v)}' for k, v in decl.items()) + '\n'

def start_document(second):
    d = r.variant('A', second)
    current_shared(d, tomllib.loads((AN / 'declarations.toml').read_text()))
    return d

def set_carbamate_diameter(document, value):
    c = next(c for c in document['components'] if c['component_id'] == r.C)
    for q in c['coefficients']:
        if q['family'] in ('segment_diameter', 'debye_huckel_diameter', 'packing_diameter'):
            q['value']['magnitude'] = value * (.88 if q['family'] == 'packing_diameter' else 1.)

def coordinates(H0=0.):
    qs = r.coordinates('A')
    for i, b in WIDE.items():
        qs[i]['bounds'] = b
    qs.append(dict(kind='reaction_enthalpy_shift', name='carbamate-hydrolysis', pivot_temperature=r.TP, origin=0., scale=1000., bounds=[-5000.-H0, 5000.-H0]))
    a = qs[7]  # #243 transport rule for a restart from a completed law with total shift H0
    a['origin'] += H0/(r.R*r.TP)
    a['bounds'] = [v + H0/(r.R*r.TP) for v in a['bounds']]
    return qs

def calibration(rows, replay):
    w = [math.sqrt(x['weight'])*p['residual'] for x, p in zip(rows, replay)]
    loaded = [p for p in replay if p['group'] == 'loaded-pressure']
    errors = [100*(p['value']/p['observed']-1) for p in loaded]
    return dict(cost=math.fsum(.5*x*x for x in w), groups={g: math.fsum(.5*x*x for x, y in zip(w, rows) if y['group'] == g) for g in dict.fromkeys(y['group'] for y in rows)},
        loaded_pressure=dict(rows=len(loaded), mean_abs_percent=float(np.mean(np.abs(errors))), bias_percent=float(np.mean(errors)), max_abs_percent=float(max(map(abs, errors))),
            isotherms={str(T): relative_error_statistic([p for p in loaded if round(float(p['row']['T_K'])) == T]) for T in (313, 333, 353)}),
        nmr_rms=math.sqrt(np.mean([(p['value']-p['observed'])**2 for p in replay if p['group'] == 'nmr'])),
        binary_mean_abs_percent=float(np.mean([100*abs(p['value']/p['observed']-1) for x, p in zip(rows, replay) if x['group'] == 'binary' and x['kind'] == 'pressure'])))

def tong(path):
    kundu.initialize(path)
    records = [x for x in kundu.spec.inputs['observations']['comparisons'] if x['group'] == 'tong']
    inside = [x for x in records if float(x['row']['T_K']) <= 353.22]  # fixed Hamborg AMP-dissociation law ends at 353.22 K
    rows = [kundu.spec.prediction(x) for x in inside]
    assert all(p['status'] == 'Available' and p['requested_tolerance_met'] for p in rows)
    rows = [dict(identity=p['identity'], T_K=float(p['row']['T_K']), alpha=float(p['row']['alpha_mol_CO2_per_mol_AMP']), observed_Pa=p['observed'], predicted_Pa=p['value']) for p in rows]
    errors = [100*(x['predicted_Pa']/x['observed_Pa']-1) for x in rows]
    return dict(rows=rows, scored=len(rows), refused_out_of_domain=len(records)-len(inside), E_p=float(np.mean(np.abs(errors))), bias_percent=float(np.mean(errors)),
        isotherms={str(T): float(np.mean([abs(e) for e, x in zip(errors, rows) if x['T_K'] == T])) for T in sorted({x['T_K'] for x in rows})})

def configuration(run, law, endpoint, name):
    decl = AN / f'inputs/refit-306/{name}-declarations.toml'
    decl.write_text(declarations(law))
    c = tomllib.loads((AN / f'{run}.toml').read_text())
    c.update(declarations=bind(decl), start=bind(endpoint), endpoint=bind(endpoint))
    path = AN / f'{name}.toml'
    path.write_text('\n'.join(f'{k} = {toml_value(v)}' for k, v in c.items()) + '\n')
    return path

(AN / 'inputs/refit-306/declarations.toml').write_text(declarations())
old_summary = json.loads((AN / 'results/redesign/summary.json').read_text())['runs']['redesign-1-A-slope-1']
old_spec = SolventSpecification(AN / 'kundu-current.toml')  # #243 endpoint with adopted shared species, as scored in #304
old_rows = old_spec.inputs['observations']['fitted']
old = dict(calibration=calibration(old_rows, [old_spec.prediction(x) for x in old_rows]), parameters=old_summary['independent_physical'],
           total_shift_J_mol=old_summary['total_shift_J_mol'], delta=old_summary['delta'], law=old_summary['law'],
           kundu=json.loads((AN / 'results/kundu/summary.json').read_text())['variants']['current'])
summary = dict(wheel_sha256=kundu.SHA256, workers=workers, widened=WIDE, size_check=dict(MEACOO_diameter=MEACOO, AMPCOO_volume_estimate=SIZE_ESTIMATE,
    basis='MEACOO- diameter x cube root of segment-volume ratio sum(m sigma^3) for AMP+CO2 over MEA+CO2 (adopted pure parameters); parent-amine ratio gives 6.15 A'),
    old=old, runs={})
if sys.argv[1:] == ['old-k']:  # orchestrator 2026-11-12: attribution comparison only; never selected or scored
    summary = json.loads((OUT / 'summary.json').read_text())
    for run, second, floor in [(f'refit-306-{name}-{1+second}', second, floor) for name, floor in (('limits243', 4.5), ('oldk', MEACOO)) for second in (False, True)]:
        document = start_document(second)  # #243 limits keep the declared 5.3 A start; the 5.32 A floor starts at the size estimate
        qs = coordinates()
        qs[4]['bounds'] = [-.5, .5]
        qs[6]['bounds'] = [floor, 6.5]
        if floor == MEACOO:
            set_carbamate_diameter(document, SIZE_ESTIMATE)
            qs[6]['origin'] = SIZE_ESTIMATE
        spec = r.make_spec(run, document, qs, None, seconds=4500, declarations='inputs/refit-306/declarations.toml')
        pre = summary.setdefault('attribution', {})[run] = dict(start=r.preflight(spec), start_H0=0.)
        endpoint, fitted, replay = r.fit_endpoint(run, spec)
        pre.update(endpoint, calibration=calibration(spec.inputs['observations']['fitted'], replay))
        r.calibration_checks(pre, spec, replay, True, 0.)
        pre['bound'] = [i for i, (q, v) in enumerate(zip(qs, pre['independent_physical'])) if min(v-q['bounds'][0], q['bounds'][1]-v) <= 1e-6*q['scale']]
        print(run, pre['status'], pre['cost'], 'bound', pre['bound'], flush=True)
        save(OUT / 'summary.json', summary)
    sys.exit()
if sys.argv[1:] == ['kundu-steps']:  # orchestrator 2026-11-12: held-out error for each attribution step; no selection
    summary = json.loads((OUT / 'summary.json').read_text())
    runs = {**summary['runs'], **summary['attribution']}
    pick = lambda name: min((k for k in runs if k.startswith(f'refit-306-{name}-')), key=lambda k: runs[k]['cost'])
    (OUT / 'steps').mkdir(exist_ok=True)
    summary['steps'] = {}
    for step, run in (('2 #243 limits', pick('limits243')), ('3 old k, floor 5.32 A', pick('oldk')), ('4 k widened, floor 5.32 A', 'refit-306-floor'), ('5 floor 3.5 A', 'refit-306-1')):
        path = configuration(run, runs[run]['law'], AN / runs[run]['endpoint'], f'kundu-{run}')
        summary['steps'][step] = dict(run=run, cost=runs[run]['cost'], calibration=runs[run]['calibration'], parameters=runs[run]['independent_physical'],
                                      bound=runs[run]['bound'], kundu=score(path, OUT / 'steps', run, workers))
        print(step, run, summary['steps'][step]['kundu']['overall'], flush=True)
        save(OUT / 'summary.json', summary)
    sys.exit()
starts = {'refit-306-1': (start_document(False), None, 0.), 'refit-306-2': (start_document(True), None, 0.),
          'refit-306-243': (json.loads((AN / 'inputs/kundu/current-endpoint.json').read_text()), old_summary['law'], H243),
          'refit-306-floor': (start_document(False), None, 0.)}
set_carbamate_diameter(starts['refit-306-floor'][0], SIZE_ESTIMATE)
for run, (document, law, H0) in starts.items():
    qs = coordinates(H0)
    if run.endswith('floor'):
        qs[6].update(origin=SIZE_ESTIMATE, bounds=[MEACOO, 6.5])
    spec = r.make_spec(run, document, qs, law, seconds=4500, declarations='inputs/refit-306/declarations.toml')
    summary['runs'][run] = pre = dict(start=r.preflight(spec), start_H0=H0)
    if not pre['start']['passed']:
        pre['disposition'] = 'start gate failed; Diagnose'
        continue
    endpoint, fitted, replay = r.fit_endpoint(run, spec)
    pre.update(endpoint)
    r.calibration_checks(pre, spec, replay, True, H0)
    pre['calibration'] = calibration(spec.inputs['observations']['fitted'], replay)
    x = pre['independent_physical']
    pre['bound'] = [i for i, (q, v) in enumerate(zip(qs, x)) if min(v-q['bounds'][0], q['bounds'][1]-v) <= 1e-6*q['scale']]
    pre['on_new_limit'] = [i for i in pre['bound'] if i in WIDE and not run.endswith('floor')]  # #243 limits are interior now
    if run.endswith('243'):
        pre['restart_cost_relative'] = abs(pre['initial_cost']/old['calibration']['cost']-1)
    print(run, pre['status'], pre['cost'], 'bound', pre['bound'], flush=True)
    save(OUT / 'summary.json', summary)
main = [k for k in ('refit-306-1', 'refit-306-2', 'refit-306-243') if 'cost' in summary['runs'][k]]
selected = min(main, key=lambda k: summary['runs'][k]['cost'])
vector = lambda p, qs: [(p['delta'] if q.get('coefficient') == 'a' else p['total_shift_J_mol'] if q.get('kind') == 'reaction_enthalpy_shift' else v)/q['scale'] for q, v in zip(qs, p['independent_physical'])]
qs = coordinates()
summary['starts'] = {k: dict(cost_minus_selected=summary['runs'][k]['cost']-summary['runs'][selected]['cost'],
    max_scaled_coordinate_difference=max(abs(a-b) for a, b in zip(vector(summary['runs'][k], qs), vector(summary['runs'][selected], qs)))) for k in main}
summary['selected'] = selected
s = summary['runs'][selected]
summary['new_limit'] = s['on_new_limit']
save(OUT / 'summary.json', summary)
if s['on_new_limit']:  # step 2 stop; owner 2026-11-12: score the size-check floor instead, as the issue allows
    print(f'{selected} sits on a new limit {s["on_new_limit"]}; scoring refit-306-floor', flush=True)
    selected = summary['scored'] = 'refit-306-floor'
    s = summary['runs'][selected]
else:
    summary['scored'] = selected
path = configuration(selected, s['law'], AN / s['endpoint'], 'kundu-refit-306')
replay = SolventSpecification(path)
summary['endpoint_replay_cost_relative'] = abs(calibration(replay.inputs['observations']['fitted'], [replay.prediction(x) for x in replay.inputs['observations']['fitted']])['cost']/s['cost']-1)
phases = [replay.phase(dict(identity=x['identity'], problem=x['problem'], endpoint_sha256=replay.parameter_sha256), replay.spec['phase_policy']) for x in replay.inputs['observations']['fitted']]
summary['calibration_phase'] = {k: [p['identity'] for p in phases if p.get(k)] for k in ('dense', 'ambiguous', 'unresolved')}
summary['kundu'] = score(path, OUT, 'kundu', workers)
summary['tong'] = dict(new=tong(path), old=tong(AN / 'kundu-current.toml'))
save(OUT / 'summary.json', summary)
print('Kundu', summary['kundu']['overall'], 'Tong', summary['tong']['new']['E_p'], flush=True)
