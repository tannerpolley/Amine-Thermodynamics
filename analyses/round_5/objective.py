"""Reconcile objective contributions and refit the declared weight and start contrasts."""
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import math
import subprocess
import sys

from amp import DECLARATION, ENDPOINTS, ORIGINAL, reduced
from amp_stability import AMP_REFERENCE
from common import ROOT, RESULTS, fingerprints, save
from part_ii import Route, active_bound_indices, deviation_statistics, np, stable
from phases import BOUNDED, MDEA, fixed
from shared_bicarbonate_417 import KEY

OBJECTIVES = ROOT / 'analyses/mea_parameter_bundle/results/objective-weights-420'
SHARED_K = BOUNDED.parent / 'shared-bicarbonate-417'
LOW, = (SHARED_K / 'mdea').glob('mdea-low-*/endpoint.json.gz')
HIGH, = (SHARED_K / 'mdea').glob('mdea-high-*/endpoint.json.gz')
REPORTED = BOUNDED / 'endpoint.json'


def observable(row):
    kind, group = row['observable'], row['group']
    if row['unit'] == 'kg/m^3':
        return 'mass density'
    if group == 'Jakobsen' and 'ratio' in row['row']:
        return row['row']['ratio']
    if group in ('Carson', 'Merkley'):
        return group + ' addition enthalpy'
    if kind == 'pressure':
        return 'total pressure'
    return kind


def decompose(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[observable(r)].append(r)
    return {group: dict(count=len(rr), sources=sorted({r.get('source', r['group']) for r in rr}),
                        identities=[r['identity'] for r in rr], cost=math.fsum(r['cost'] for r in rr),
                        units=sorted({str(r['unit']) for r in rr}), transforms=sorted({r['form'] for r in rr}),
                        scales=sorted({r['scale'] for r in rr}), weights=sorted({r['weight'] for r in rr}),
                        weight_sum=math.fsum(r['weight'] for r in rr),
                        deviations=deviation_statistics([(r['observed'],r['value']) for r in rr], rr[0]['unit'])) for group, rr in groups.items()}


def information(route, point):
    spec, replay, derivative = route.differentiate_endpoint(point)
    return reduce_information(spec, replay, derivative, point)


def reduce_information(spec, replay, derivative, point):
    observations = spec.inputs['observations']['fitted']
    coords = point['coordinates']
    jacobian = np.array(derivative.residual_optimizer_gradient).reshape(len(replay), len(coords))
    weighted = spec.whiten(jacobian)
    residual = spec.whiten(np.array([r['residual'] for r in replay]))
    active = active_bound_indices(coords)
    interior = [i for i in range(len(coords)) if i not in active]
    rank = int(np.linalg.matrix_rank(weighted[:, interior]))
    absent = [r['identity'] for r, j in zip(replay, weighted, strict=True) if not np.any(j)]
    rows = [dict(v, unit=r['unit'], observable=r['kind'] if r['constructor'] == 'observation' else r['constructor'], scale=r['arguments'].get('scale', 1.),
                 form=r['arguments']['form'], weight=r['weight'], source=r['row'].get('source_key', r['group']),
                 zero_response=v['identity'] in absent, weighted_residual=float(w), cost=.5*float(w)**2)
            for r, v, w in zip(observations, replay, residual, strict=True)]
    stage = [r for r in rows if r['row'].get('liquid_x_MDEA') != '0']
    gradient = weighted.T @ residual
    cost, stage_cost = (math.fsum(r['cost'] for r in rr) for rr in (rows, stage))
    return dict(objective=cost, n=len(rows), rank=rank, active_bounds=[coords[i]['identity'] for i in active],
                exact_zero_response=absent, stage_excluded=[r['identity'] for r in rows if r not in stage],
                all_variance=2 * cost / (len(rows) - rank), stage_variance=2 * stage_cost / (len(stage) - rank),
                gradient=dict(zip([q['identity'] for q in coords], gradient, strict=True)), rows=rows, groups=decompose(rows))


def retained():
    start = monotonic()
    comparison = stable.read(OBJECTIVES / 'reconciliation.json')
    paths = [OBJECTIVES / s / 'information.json.gz' for s in ('MEA', 'DEA', 'MDEA', 'AMP')]
    output = {}
    for p in paths:
        case = p.parent.name
        info = stable.read(p)['result']
        original = comparison[case]
        rows = info['rows']
        groups = decompose(rows)
        cost = math.fsum(g['cost'] for g in groups.values())
        assert math.isclose(cost, original['objective'], rel_tol=1e-12)
        stage_variance = info['stage_rss'] / info['stage_denominator']
        assert math.isclose(stage_variance, original['stage_variance'], rel_tol=1e-12)
        zero = [r['identity'] for r in info['excluded']]
        if case == 'MDEA':
            pure = stable.read(OBJECTIVES / 'MDEA/pure-water-derivative-control.json')
            zero = pure['result']['raw_exact_zero_rows']
        output[case] = dict(groups=groups, objective=cost, rank=info['p'],
                            active_bounds=[info['coordinates'][i]['identity'] for i in info['active_bounds']],
                            all_variance=info['variance'], stage_variance=stage_variance, exact_zero_response=zero,
                            stage_excluded=original['excluded'], stage_dof=info['stage_denominator'], all_dof=info['denominator'])
    profile_path = SHARED_K / 'profile.json.gz'
    profile = stable.read(profile_path)
    points = [profile['center'], *profile['points'].values()]
    points = [dict(k=p['k'], cost=p['cost'], increase=p['cost'] - profile['center_cost'], start=p['start'],
                   active_bounds=p['active_bounds']) for p in points if p['cost'] is not None]
    save('C/reported-objectives.json', dict(models=output, MEA_profile=points, MEA_center_cost=profile['center_cost'],
         inputs=fingerprints(*paths, profile_path, OBJECTIVES/'reconciliation.json')), start=start)


class ObservableWeights(Route):
    def __init__(self, declaration, out, subset):
        self.subset = subset
        super().__init__(declaration, out)

    def weights(self, spec):
        rows = spec.inputs['observations']['fitted']
        group_weights = defaultdict(list)
        definitions = []
        for r in rows:
            args = r['arguments']
            engine_scale = args.get('scale', 1.)
            group = observable(dict(r, observable=r['kind'] if r['constructor']=='observation' else r['constructor']))
            scale, weight = engine_scale, r['weight']
            if self.subset == 'AMP' and args['form'] == 'log_ratio':
                scale, weight = (.015, 1/47) if r['group'] == 'loaded-pressure' else (.05, 1/52)
            group_weights[group].append(weight)
            definitions.append(dict(identity=r['identity'], observable=group, scale=scale, weight=weight,
                                    engine_scale=engine_scale, default_coefficient=r['weight']/engine_scale**2))
        ref = {r['identity']: r for r in stable.read(OBJECTIVES / self.subset / 'information.json.gz')['result']['rows']}
        for definition, r in zip(definitions, rows, strict=True):
            s, w, k = (definition[v] for v in ('scale','weight','identity'))
            den = math.fsum(group_weights[definition['observable']])
            coeff = w / s**2
            assert math.isclose(coeff, definition['default_coefficient'], rel_tol=1e-12)
            assert math.isclose(coeff, ref[k]['weight']/ref[k]['scale']**2, rel_tol=1e-12)
            definition.update(denominator=den, alternative_weight=w/den, alternative_coefficient=(w/den)/s**2)
        return definitions

    def bind(self, point):
        spec = super().bind(point)
        for r, w in zip(spec.inputs['observations']['fitted'], self.weights(spec), strict=True):
            r['weight'] = w['alternative_coefficient'] * w['engine_scale']**2
        return spec


def fit(route, name, starting):
    point, report = reduced.fit(name, starting, {}, [], route=route, penalty_rows=[])
    return dict(point=point, report=report, starting_point=starting, records=fit_records(route.out / name))


def fit_records(folder):
    return {p.relative_to(folder).as_posix(): stable.read(p) for p in folder.rglob('*.json')}


def q3_checks(route, point):
    spec = route.bind(point)
    q3 = ROOT / 'analyses/round_3/results/q3.json'
    outcomes = []
    for r in stable.read(q3)['rows'][:2]:
        feed = dict(zip(r['species'], r['feed_mol'], strict=True))
        loading = feed.pop('carbon-dioxide')
        state = dict(stock={k: v for k, v in feed.items() if v}, T=r['T_K'], a=loading)
        try:
            outcome = fixed(route, spec, state, r['P_Pa'], dict(pair=r['attempts'][0]), mdea=True)
        except (RuntimeError, AssertionError, ValueError) as error:
            outcome = dict(refusal=f'{type(error).__name__}: {error}')
        outcomes.append(dict(outcome, key=r['key']))
    return outcomes


def cross_start(work):
    total_start = monotonic()
    route = Route(MDEA, work)
    lo, bounded = map(stable.read, (LOW, REPORTED))
    def signature(p):
        return [{k: v for k, v in q.items() if k != 'origin'} for q in p['coordinates']]
    assert signature(lo) == signature(bounded) and lo['reactions'] == bounded['reactions']
    for label, incumbent, other in (('low', lo, bounded), ('reported', bounded, lo)):
        started = monotonic()
        k = stable.s.parameter_values(incumbent['parameters'])[KEY]
        mapped = dict(other, parameters=stable.s.with_parameter_values(other['parameters'], {KEY: k}))
        result = fit(route, label, mapped)
        result['k'] = k
        save(f'C/cross-start-{label}.json.gz', result, start=started)
        candidates = dict(incumbent=incumbent)
        if result['point'] is not None:
            candidates['cross_start'] = result['point']
        for name, point in candidates.items():
            save(f'C/cross-start-{label}-{name}-assessment.json.gz',
                 dict(information=information(route, point), Q3=q3_checks(route, point)), start=started)
    save('C/cross-start-timing.json', dict(projection_minutes=[2,4]), start=total_start)


def normalized_assessment(default, weighted, point, definitions):
    spec, replay, derivative = default.differentiate_endpoint(point)
    alternative_spec = weighted.bind(point)
    assert [r['identity'] for r in spec.inputs['observations']['fitted']] == [
        r['identity'] for r in alternative_spec.inputs['observations']['fitted']]
    assessment = dict(default=reduce_information(spec, replay, derivative, point),
                      alternative=reduce_information(alternative_spec, replay, derivative, point))
    for d, r in zip(definitions, assessment['default']['rows'], strict=True):
        assert d['identity'] == r['identity']
        r['declared_difference'] = r['residual'] * d['engine_scale']
        r['physical_scale'] = d['scale']
        r['baseline_weight'] = d['weight']
        r['alternative_weight'] = d['alternative_weight']
    return assessment


def assess_limited_MDEA(work, outcome):
    started = monotonic()
    default = Route(MDEA, work/'default')
    weighted = ObservableWeights(MDEA, work/'alternative', 'MDEA')
    candidate = stable.read(outcome)
    point = candidate['stage-0/parameters.json']
    definitions = weighted.weights(default.bind(point))
    assessment = normalized_assessment(default,weighted,point,definitions)
    save('C/normalized-MDEA-0-limited-assessment.json.gz',
         dict(assessment, Q3=q3_checks(default, point), inputs=fingerprints(outcome,MDEA)),start=started)


def alternative(work, only):
    total_start = monotonic()
    paths = {'AMP': [ENDPOINTS / label / 'parameters.json' for label in ORIGINAL], 'MDEA': [LOW, REPORTED]}
    for solvent, cases in paths.items():
        declaration = DECLARATION if solvent == 'AMP' else MDEA
        default = Route(declaration, work / solvent / 'default')
        weighted = ObservableWeights(declaration, work / solvent / 'alternative', solvent)
        for i, path in enumerate(cases):
            name = f'{solvent}-{i}'
            if only != name:
                continue
            started = monotonic()
            old = stable.read(path)
            definitions = weighted.weights(default.bind(old))
            result = fit(weighted, name, old)
            save(f'C/normalized-{name}.json.gz', dict(result, weights=definitions, inputs=fingerprints(path, declaration)), start=started)
            for label, point in (('original', old), ('refit', result['point'])):
                if point is None:
                    continue
                assessment = normalized_assessment(default,weighted,point,definitions)
                if solvent == 'MDEA':
                    assessment['Q3'] = q3_checks(default, point)
                else:
                    amp = stable.read(AMP_REFERENCE)
                    stock = dict(zip(amp['species'], amp['feed_mol'], strict=True))
                    stock = {c:n for c,n in stock.items() if n and c != 'carbon-dioxide'}
                    S14 = dict(T=amp['T_K'], stock=stock, a=amp['loading'])
                    P = stable.read(RESULTS/'A/common-pressure.json.gz')['common_Pa']
                    assessment['S14'] = fixed(default, default.bind(point), S14, P, dict(pair=amp['split']))
                save(f'C/normalized-{name}-{label}-assessment.json.gz', assessment, start=started)
    save(f'C/normalized-{only}-timing.json', dict(endpoint=only), start=total_start)


def alternative_refits(work, only=None):
    cases = ('AMP-0', 'AMP-1', 'MDEA-0', 'MDEA-1')
    if only is not None and only not in cases:
        raise ValueError(f'Unknown normalized refit {only}')
    for candidate in (only,) if only else cases:
        if candidate.startswith('AMP'):
            alternative(work, candidate)
            continue
        # Each MDEA refit gets the full wall-time allowance formerly shared by Group C.
        started = monotonic()
        try:
            subprocess.run([sys.executable, __file__, 'alternative_case', candidate, str(work)],
                           timeout=1680, check=True)
        except subprocess.TimeoutExpired:
            folder = work / 'MDEA' / 'alternative' / candidate
            save(f'C/normalized-{candidate}-time-stop.json.gz',
                 dict(records=fit_records(folder), alternative_process_wall_seconds=monotonic()-started),
                 start=started)



def replay_k(work):
    begun = monotonic()
    profile_path = SHARED_K / 'profile.json.gz'
    profile = stable.read(profile_path)
    ps = [profile['center'], *profile['points'].values()]
    spec_path = stable.TOML
    records = []
    for p in ps:
        tick = monotonic()
        rows, ok, cost = stable.replay(p['mapping'])
        stage = [r for r in rows if r['group'] != 'Kiepe']
        records.append(dict(k=p['k'], replay_cost=cost, retained_cost=p['cost'], available=ok, rows=rows,
                            stage_rss=2*math.fsum(r['cost'] for r in stage) if ok else None,
                            stage_n=len(stage), seconds=monotonic()-tick))
    center = records[0]
    rank = stable.read(OBJECTIVES / 'MEA/information.json.gz')['result']['p']
    if center['available']:
        variance = center['stage_rss'] / (center['stage_n'] - rank)
        cutoff = .5 * variance * 3.84146
        for row in records:
            row['increase_from_center'] = row['replay_cost'] - center['replay_cost'] if row['available'] else None
    else:
        variance = cutoff = None
    route = Route(MDEA,work/'mdea')
    for label,path in (('low',LOW),('reported',REPORTED),('high',HIGH)):
        tick = monotonic()
        point = stable.read(path)
        k = stable.s.parameter_values(point['parameters'])[KEY]
        save(f'C/MDEA-k-{label}.json.gz', dict(k=k, information=information(route, point),
             inputs=fingerprints(path, MDEA)),start=tick)
    save('C/MEA-k-profile.json.gz', dict(rows=records, stage_variance=variance, delta_cutoff=cutoff,
         profile_reference='Conditional profile over fixed bicarbonate-water k',
         inputs=fingerprints(profile_path,spec_path)), start=begun)


if __name__ == '__main__':
    operation = dict(retained=retained, cross_start=cross_start, alternative=alternative_refits,
                     alternative_case=alternative, replay_k=replay_k,
                     assess_limited_MDEA=assess_limited_MDEA)[sys.argv[1]]
    if operation is retained:
        operation()
    elif operation is alternative:
        operation(Path(sys.argv[3]), only=sys.argv[2])
    else:
        with TemporaryDirectory() as directory:
            if operation is alternative_refits and len(sys.argv)>2:
                operation(Path(directory),only=sys.argv[2])
            elif operation is assess_limited_MDEA:
                operation(Path(directory),Path(sys.argv[2]).resolve())
            else:
                operation(Path(directory))
