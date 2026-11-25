"""Replay and refit the #440 declarations at a fixed 100 kPa reaction reference."""
# ruff: noqa: E402
from copy import copy, deepcopy
import csv
from hashlib import sha256
from itertools import combinations
import os
from pathlib import Path
import sys
from time import monotonic
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
WORK = HERE.parents[1] / 'build/fixed-reaction-reference'
P_REF = 100000.
SEED = 427
COUNTS = dict(MEA=307, DEA=140, MDEA=281, AMP_free=214, AMP_fixed=214)
ALLOWANCE = dict(MEA=1800, DEA=1080, MDEA=7320, AMP_free=4500, AMP_fixed=4500)
REPLAY_TOLERANCE = dict.fromkeys(COUNTS, 1e-8) | {'MEA': 1e-10}
THREAD_VARIABLES = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS',
                    'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')

sys.path[:0] = [str(HERE.parent / name) for name in ('round_7', 'round_8')]
for variable in THREAD_VARIABLES:
    os.environ[variable] = '1'
os.environ['AGENT_HEAVY_CORES'] = '4'

from scipy.stats import qmc
from calculations import OUT as ROUND7, MDEA, MDEAWeights, Route, a, r, save
from receivers import AMP, DEA, ExpandedDEA, inherited, verify_binding
from part_ii import calculation_declaration, epcsaft, eq, np, reg
from MEA.solvent_specification import conditional_information, jsonable

MEA = a.OUT / 'MEA/F4'
BASE = '5953bd80290767125056eb3393778d777c46aca5'


def fingerprint(point):
    import json
    return sha256(json.dumps(jsonable(point), sort_keys=True, allow_nan=False).encode()).hexdigest()


def put(name, value):
    save(OUT / name, value)


class MEARoute:
    def __init__(self, fixed=True):
        self.fixed = fixed
        self.controls = dict(r.read(r.A6)['controls'], function_tolerance=1e-10)
        self.workers = 4

    def bind(self, point):
        spec = r.bind(point['parameters'], reaction_reference_pressure_pa=P_REF if self.fixed else None)
        spec.inputs['endpoint'] = point['parameters']
        spec.inputs['coordinates'] = point['coordinates']
        assert spec.spec['chemistry']['reactions'] == point['reactions']
        return spec

    def endpoint_mapping(self, point, report, declared):
        p = Route.endpoint_mapping(self, point, report, declared)
        p['parameters'] = r.endpoint_mapping(point['parameters'], report, declared)
        return p

    stability_row = staticmethod(r.stability_row)


def configured(name, tag, fixed=True):
    root = WORK / name / tag
    if name == 'MEA':
        source = MEA/'parameters.json'
        parameters = r.s.parameter_mapping(source)
        spec = r.bind(parameters)
        coordinates = deepcopy(r.read(MEA/'declaration.json')['declared'])
        values = r.s.parameter_values(parameters)
        for q in coordinates:
            q['origin'] = values[q['identity']]
        point = dict(parameters=parameters, coordinates=coordinates, reactions=spec.spec['chemistry']['reactions'])
        cost = r.read(MEA/'replay.json')['cost']
        route = MEARoute(fixed)
    else:
        family, route_type, declaration = {
            'DEA': ('F', ExpandedDEA, DEA),
            'MDEA': ('C/salt', MDEAWeights, MDEA.DECLARATION),
            'AMP_free': ('AMP/free', AMP.ExpandedPressure, AMP.DECLARATION),
            'AMP_fixed': ('AMP/fixed', AMP.ExpandedPressure, AMP.DECLARATION),
        }[name]
        source = ROUND7 / family / 'selection.json.gz'
        cost, _, point = r.read(source)['selected']
        route = route_type(declaration, root, fixed_reference_pressure_pa=P_REF if fixed else None)
    if fixed:
        for group in point['reactions'].values():
            for rx in group:
                rx['reference']['reference_pressure_pa'] = P_REF
    return route, point, dict(path=str(source.relative_to(r.ROOT)), sha256=r.s.sha256(source),
                              revision=BASE, objective=cost)


def row_manifest(spec):
    fields = ('problem', 'initial', 'final', 'bubble')
    return {role: [dict(row, states={field: calculation_declaration(spec.problems[row[field]])
                                    for field in fields if field in row})
                   for row in spec.inputs['observations'][role]] for role in ('fitted', 'comparisons')}


def remove_reference_pressure(value):
    if isinstance(value, dict):
        return {k: remove_reference_pressure(v) for k, v in value.items() if k != 'reference_pressure_pa'}
    if isinstance(value, list):
        return [remove_reference_pressure(v) for v in value]
    return value


def bound_readback(point, spec):
    assert all(rx.reference.reference_pressure_pa == P_REF for p in spec.problems.values() for rx in p.reactions)
    assert all(rx['reference']['reference_pressure_pa'] == P_REF for group in spec.spec['chemistry']['reactions'].values()
               for rx in group)
    assert all(rx['reference']['reference_pressure_pa'] == P_REF for group in point['reactions'].values() for rx in group)
    probe = next(p for p in spec.problems.values() if len(p.phases)==1 and len(p.reactions)>=3 and sum(p.feed.values.values())>0
                 and p.feed.values.get('carbon-dioxide', 0)>0)
    readbacks = {}
    for pressure in (1e5, 1e7):
        p = copy(probe)
        p.P = pressure
        solution = eq.solve_equilibrium(spec.model, p)
        activities = [dict(name=p.reactions[q.reaction_index].name, reference_pressure_pa=q.reference_pressure_pa)
                      for q in eq.reaction_activities(spec.model, solution)] if solution.requested_tolerance_met else []
        if activities:
            assert all(x['reference_pressure_pa'] == P_REF for x in activities)
        readbacks[str(pressure)] = dict(message=solution.message, activities=activities,
                                        pressure_pa=solution.pressure,
                                        max_abs_residual=max(map(abs, solution.residuals), default=None))
    assert readbacks['10000000.0']['activities'], readbacks
    return readbacks


def replay(spec):
    records = spec.inputs['observations']['fitted']
    rows = r.d.evaluate(spec, records)
    return dict(rows=rows, attempted=len(rows), refused=sum('cost' not in row for row in rows),
                cost=sum(row['cost'] for row in rows) if all('cost' in row for row in rows) else None)


def salt_controls():
    owner = a.salt
    folder = a.OUT / 'salt'
    summary = r.read(folder/'summary.json')['result']
    groups = {'1a-sodium':'NaCl', '1b-bicarbonate':'NaHCO3', '1c-carbonate':'Na2CO3'}
    stages = {}
    for label, group in groups.items():
        record = r.read(folder/f'{label}.json')['result']
        laws = {ion: (law['a0'], law['a1']) for ion, law in record['laws'].items()}
        document = owner.salt_document(laws, a.study.RECORD)
        parameters = epcsaft.Parameters.from_mapping(document)
        inputs = owner.nacl_rows(parameters) if group=='NaCl' else owner.carbonate_rows(parameters, {group})
        rows = owner.predict(document, inputs)
        change = a.salt_checks({group:rows}, {group:record['rows']})[group]
        model = epcsaft.Mixture(parameters)
        residuals = [reg.predict(model,x['item']).residual for x in inputs]
        cost = .5 * sum(x*x for x in residuals)
        scale = .003 if group=='NaCl' else .01
        optimizer_delta = record['replay_maximum_difference']/scale
        cost_roundoff = sum(abs(x)*optimizer_delta + .5*optimizer_delta**2 for x in residuals)
        stages[label] = dict(group=group, rows=rows, retained_cost=record['final_cost'],
                             replayed_cost=cost, differences=change, optimizer_replay_cost_error_bound=cost_roundoff,
                             source_sha256=r.s.sha256(folder/f'{label}.json'),
                             passed=change['maximum_relative_prediction_difference'] <= 1e-10
                             and abs(cost-record['final_cost']) <= cost_roundoff + 1e-10*abs(cost))
    rows = a.salt_rows(summary['document'])
    changes = a.salt_checks(rows, summary['rows'])
    printed = next(csv.DictReader((owner.INPUTS/'peiper-pitzer-1982-table6.csv').read_text().splitlines()))
    target = next(q for q in rows[printed['salt']] if q['m']==float(printed['nominal_molality'])
                  and q['T']==float(printed['temperature_K']))
    ions = target['composition_mol_per_kg']
    neutral = float(printed['H2X'])
    numerator = float(printed['phi']) * (ions[owner.NA] + sum(float(printed[k]) for k in ('X2','Y','H2X','Z')))
    reconstructed = (numerator-neutral) / sum(ions.values())
    _, incumbent, _ = configured('MEA', 'salt', fixed=False)
    values = r.s.parameter_values(incumbent['parameters'])
    laws = {ion: summary['laws_at_record_reference'][ion] for ion in (owner.HCO3,owner.CO3)}
    assert all(values[owner.LAWS[ion]+'/a'+str(i)]==law[f'a{i}'] for ion,law in laws.items() for i in (0,1))
    refusals = [row for row in rows['mixed'] if row.get('status')!='Available']
    passed = (all(q['passed'] for q in stages.values()) and reconstructed==target['observed'] and len(refusals)==6
              and all(x['maximum_relative_prediction_difference'] <= 1e-10 for x in changes.values()))
    put('salt.json.gz', dict(wheel=r.SHA, stages=stages, combined=rows, differences=changes, laws=laws,
                             reconstruction=dict(printed=printed, ions=ions, numerator=numerator, ideal_co2=neutral,
                                                 ionic_sum=sum(ions.values()), target=reconstructed),
                             mixed_refusals=refusals, passed=passed))
    assert passed, 'salt replay missed its retained tolerance'


def salt_pairs(mapping):
    return [p for p in mapping['pairs'] if {p['component_id_a'],p['component_id_b']}
            in ({a.salt.W,a.salt.HCO3},{a.salt.W,a.salt.CO3})]


def selected_donor():
    path = OUT / 'MEA/selection.json'
    selection = r.read(path)
    if selection['selected'] is None:
        raise ValueError('MEA selection is undecided')
    source = OUT / f"MEA/{selection['selected']}.json.gz"
    record = r.read(source)
    assert selection['endpoint_fingerprint']==fingerprint(record['endpoint'])
    mapping = record['endpoint']['parameters']
    return mapping, dict(path=str(source.relative_to(r.ROOT)), sha256=r.s.sha256(source),
                         endpoint=selection['endpoint_fingerprint'], parameter_sha256=fingerprint(mapping))


def starts(spec):
    declared = spec.inputs['coordinates']
    native = spec.coordinates()
    lower = np.array([q.lower for q in native])
    upper = np.array([q.upper for q in native])
    incumbent = np.array([q.origin for q in native])
    width = upper-lower
    scaled_a = (incumbent-lower)/width
    assert np.all((0<=scaled_a) & (scaled_a<=1))
    candidates = qmc.LatinHypercube(d=len(declared), seed=SEED).random(64)
    distance = lambda x,y: np.sqrt(np.mean((x-y)**2, axis=-1))
    b = int(np.argmax(distance(candidates,scaled_a)))
    c = int(np.argmax(np.minimum(distance(candidates,scaled_a),distance(candidates,candidates[b]))))
    vectors = dict(A=incumbent, B=lower+width*candidates[b], C=lower+width*candidates[c])
    result = {}
    for label, values in vectors.items():
        u = (values-incumbent)/np.array([q.scale for q in native])
        # The first physical target of each EOS coordinate independently checks every tie.
        chart = reg.evaluate_coordinates(spec.parameters, native, u.tolist(), [],
                                         thermochemistry=spec.thermal)
        targets = iter(chart.physical[:len(chart.active)])
        reactions = iter(chart.physical[len(chart.active):])
        actual = []
        for q, value in zip(declared, values, strict=True):
            if q.get('targets'):
                bound = [next(targets) / factor for _, _, factor in q['targets']]
                assert np.allclose(bound,value,rtol=1e-13,atol=1e-14), (q,bound,value)
                actual.append(bound[0])
            else:
                bound = next(reactions)
                assert np.isclose(bound,value,rtol=1e-13,atol=1e-14), (q,bound,value)
                actual.append(bound)
        result[label] = dict(draw={'A':None,'B':b,'C':c}[label], vector=actual, optimizer=u.tolist(),
                             normalized=((np.array(actual)-lower)/width).tolist())
    distances = {x+y:float(distance(np.array(result[x]['normalized']),np.array(result[y]['normalized'])))
                 for x,y in combinations(result,2)}
    assert min(distances.values()) >= .20, distances
    return result, distances


def prepare(name, controls_only=False):
    tick = monotonic()
    if name=='MEA':
        salt_controls()
    old, old_point, source = configured(name, 'tracking', fixed=False)
    run, point, _ = configured(name, 'fixed')
    old_spec, spec = old.bind(old_point), run.bind(point)
    if name=='MEA':
        spec.inputs['endpoint'] = point['parameters']
    old_rows, fixed_rows = row_manifest(old_spec), row_manifest(spec)
    assert remove_reference_pressure(fixed_rows)==remove_reference_pressure(old_rows), 'changed row or pressure basis'
    tracking, fixed = replay(old_spec), replay(spec)
    put(f'{name}/reference-control.json.gz', dict(tracking=tracking, fixed_at_old_parameters=fixed, source=source,
          fixed_readback=bound_readback(point,spec), wheel=r.SHA))
    assert tracking['attempted']==COUNTS[name] and tracking['cost'] is not None
    assert a.f.a.relative(tracking['cost'],source['objective']) <= REPLAY_TOLERANCE[name]
    if controls_only:
        return
    before = deepcopy(point)
    donor = None
    if name!='MEA':
        mapping, donor = selected_donor()
        if name=='MDEA':
            assert salt_pairs(point['parameters'])==salt_pairs(mapping)
        else:
            point = inherited(point, amp=name.startswith('AMP'), donor_record=(mapping,donor))
            verify_binding(run, point, amp=name.startswith('AMP'), donor_record=(mapping,donor))
    spec = run.bind(point)
    vectors, distances = starts(spec)
    put(f'{name}/manifest.json.gz', dict(source=source, wheel=r.SHA, engine_commit=r.COMMIT,
        fixed_reference_pressure_pa=P_REF, prior_declaration=before, start_A_declaration=point,
        fit_controls=run.controls, rows=row_manifest(spec), tracking_row_fingerprint=fingerprint(old_rows),
        fixed_row_fingerprint=fingerprint(fixed_rows), donor=donor, salt_pairs=salt_pairs(point['parameters']),
        coordinate_order=[q['identity'] for q in point['coordinates']], seed=SEED, candidates=64,
        starts=vectors, pair_rms_distances=distances, seconds=monotonic()-tick))


def endpoint_diagnostics(spec, fit_replay, point, controls):
    declared = point['coordinates']
    native = spec.coordinates()
    rows = spec.inputs['observations']['fitted']
    ev = reg.differentiate(spec.parameters, native, [spec.observation(q) for q in rows],
                           optimizer=[0.]*len(native), thermochemistry=spec.thermal)
    values = dict(derivative_statuses=[q.name for q in ev.statuses])
    if fit_replay['cost'] is None or any(q.name!='Available' for q in ev.statuses):
        return values
    residual = np.array([q['weighted_residual'] for q in fit_replay['rows']])
    J = spec.whiten(np.array(ev.residual_optimizer_gradient).reshape(len(rows),len(native)))
    scale = np.array([q.scale for q in native])
    width = np.array([q.upper-q.lower for q in native])
    grad = (J * (width/scale)).T @ residual
    projected = grad.copy()
    active = {}
    for i, q in enumerate(native):
        side = 'lower' if q.origin-q.lower <= 1e-6*q.scale else 'upper' if q.upper-q.origin <= 1e-6*q.scale else None
        if side:
            active[declared[i]['identity']] = side
            if (side=='lower' and grad[i]>0) or (side=='upper' and grad[i]<0):
                projected[i] = 0.
    values.update(jacobian_bound_normalized=(J*(width/scale)).tolist(), gradient=grad.tolist(),
                  projected_gradient=projected.tolist(), projected_gradient_inf=float(np.max(np.abs(projected))),
                  active_bounds=active, stationarity_met=bool(np.max(np.abs(projected))<=controls['gradient_tolerance']),
                  maximum_prediction_relative_difference=max(abs(v-q['value'])/max(1.,abs(q['value']))
                    for v,q in zip(ev.predictions,fit_replay['rows'],strict=True)))
    ids = [q['identity'] for q in declared]
    result = SimpleNamespace(physical=[q.origin for q in native],
                             covariance=SimpleNamespace(active_bounds=[ids.index(i) for i in active]))
    try:
        values['uncertainty'] = conditional_information(result,J/scale,residual,ids,
                                                        [q.lower for q in native],[q.upper for q in native])
    except np.linalg.LinAlgError as exc:
        values['uncertainty_refusal'] = str(exc)
    return values


def attempt(name, label):
    manifest = r.read(OUT/f'{name}/manifest.json.gz')
    run, _, _ = configured(name, 'fixed')
    point = manifest['start_A_declaration']
    spec = run.bind(point)
    controls = manifest['fit_controls'] | dict(workers=4)
    controls.setdefault('maximum_elapsed_time_seconds', 1.5*ALLOWANCE[name])
    if label=='A-loose':
        controls['function_tolerance'] = 1e-6
    spec.spec['optimizer'] = controls
    u = manifest['starts']['A' if label=='A-loose' else label]['optimizer']
    tick = monotonic()
    _, report, _ = spec.fit(starts=[u])
    record = dict(start=label, controls=controls, wheel=r.SHA, manifest_fingerprint=fingerprint(manifest),
                  optimizer_start=u, report=report, fit_seconds=monotonic()-tick)
    filename = f'{name}/{label}.json.gz'
    put(filename, record)
    if report['physical'] and report['reactions']:
        endpoint = run.endpoint_mapping(point,report,point['coordinates'])
        record.update(endpoint=endpoint, endpoint_fingerprint=fingerprint(endpoint))
        put(filename,record)
        tick = monotonic()
        bound = run.bind(endpoint)
        fit_replay = replay(bound)
        record.update(replay=fit_replay, replay_seconds=monotonic()-tick)
        put(filename,record)
        cost = report['data_cost'] if report['data_cost'] is not None else report['final_cost']
        record['replay_passed'] = (fit_replay['cost'] is not None and cost is not None
                                  and a.f.a.relative(fit_replay['cost'],cost)<=REPLAY_TOLERANCE[name])
        tick = monotonic()
        record['diagnostics'] = endpoint_diagnostics(bound,fit_replay,endpoint,controls)
        record['diagnostic_seconds'] = monotonic()-tick
    put(filename,record)
    print(name,label,report['status'],report['initial_cost'],report['final_cost'],
          record.get('replay_passed'),record['fit_seconds'],record.get('replay_seconds'),flush=True)


def select(name):
    records = {label:r.read(OUT/f'{name}/{label}.json.gz') for label in 'ABC'}
    eligible = {k:v for k,v in records.items() if v.get('replay_passed') and v['report']['status']=='converged'}
    best = min((v['replay']['cost'] for v in eligible.values()),default=None)
    tolerance = eligible[next(iter(eligible))]['controls']['function_tolerance'] if eligible else None
    tied = [label for label,v in eligible.items() if a.f.costs_tied(v['replay']['cost'],best,tolerance)]
    selected = tied[0] if tied else None
    put(f'{name}/selection.json',dict(selected=selected,numerical_minimum=best,tied=tied,
        endpoint_fingerprint=eligible[selected]['endpoint_fingerprint'] if selected else None,
        cost=eligible[selected]['replay']['cost'] if selected else None,
        attempts={label:dict(cost=v.get('replay',{}).get('cost'),status=v['report']['status'],
                             replay_passed=v.get('replay_passed',False), endpoint=v.get('endpoint_fingerprint'))
                  for label,v in records.items()}))


if __name__ == '__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    action, name, *args = sys.argv[1:]
    if action=='controls':
        for design in (name,*args):
            prepare(design,controls_only=True)
    else:
        {'prepare':prepare,'attempt':attempt,'select':select}[action](name,*args)
