"""Issue #338 cumulative source-law refits and their assessment; no adoption."""
# ruff: noqa: E402 -- the qualified adoption module overrides the historical wheel.
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import adoption_297 as a
import candidate_evidence_255 as e

r = a.r
OUT = r.B / 'results/reduced-refit'

LITERATURE = {'reaction:R2:correlation:a':231.465+4.0165, 'reaction:R2:correlation:b_k':-12092.1,
             'reaction:R2:correlation:c':-36.7816, 'reaction:R2:correlation:d_per_k':0.,
             'reaction:R5:correlation:a_k':2677.91, 'reaction:R5:correlation:b':.3869,
             'reaction:R5:correlation:c_per_k':.0004277}


def write(name, value):
    r.s.write_json(OUT / name, value)


def table(name, rows):
    e.table(OUT/name, rows)

def laws():
    """Bates–Pinching Eq. (10), Table 2 p.351; Austgen Table V p.547."""
    measured = (10.3064, 10.1341, 9.9654, 9.8037, 9.6467, 9.4980,
                9.3485, 9.2082, 9.0702, 8.9401, 8.8130)
    native = r.eq.ReactionLogPolynomial(a=-math.log(10)*.3869, b=-math.log(10)*2677.91,
                                      c=0., d=-math.log(10)*.0004277, reference_temperature=313.15,
                                      temperature_min=273.15, temperature_max=393.15, standard_state_id=r.s.COMMON_SOURCE_STANDARD_STATE_ID)
    def evaluate(law,T):
        return law.a + law.b/T + law.c*math.log(T/law.reference_temperature) + law.d*T
    check = evaluate(native, 298.15)
    rows = []
    for i, observed in enumerate(measured):
        # The paper explicitly defines T = t / degC + 273.16 below Eq. (10).
        T = 273.16 + 5*i
        value = -evaluate(native, T)/math.log(10)
        rows.append(dict(temperature_C=5*i, source_temperature_K=T, observed_pK=observed,
                         equation_10_pK=value, difference_pK=value-observed,
                         printed_digits_match=round(value, 4)==observed))
    table('r5-table2-check.csv', rows)
    hamborg = r.read(r.ROOT/'analyses/high_temperature_chemistry/results/hamborg-law.json')['coefficients']
    other = r.eq.ReactionLogPolynomial(**hamborg, temperature_min=273.15, temperature_max=393.15, standard_state_id=r.s.COMMON_SOURCE_STANDARD_STATE_ID)
    table('r5-literature-comparison.csv', [dict(temperature_K=T, bates_pinching_lnK=evaluate(native,T),
          hamborg_derived_lnK=evaluate(other,T), bates_minus_hamborg=evaluate(native,T)-evaluate(other,T))
          for T in (313.15, 323.15, 333.15, 343.15, 353.15)])
    result = dict(r5_298_15_lnK=check, r5_check_value_passed=abs(check + 21.86574617291778) <= math.ulp(check),
                  r5_coefficients={k:getattr(native,k) for k in ('a','b','c','d','reference_temperature')},
                  r2_coefficients=dict(a=231.465+4.0165-36.7816*math.log(313.15), b=-12092.1, c=-36.7816),
                  table2_printed_digits_passed=all(x['printed_digits_match'] for x in rows),
                  table2_max_absolute_difference_pK=max(abs(x['difference_pK']) for x in rows),
                  source='Bates and Pinching 1951, p.351, Eq.(10) and Table 2',
                  source_reported_average_difference_pK=.0010)
    result['table2_mean_absolute_difference_pK'] = sum(abs(x['difference_pK']) for x in rows)/len(rows)
    result['equation10_max_conversion_error_pK'] = max(abs(x['equation_10_pK']-(2677.91/x['source_temperature_K']+.3869+.0004277*x['source_temperature_K'])) for x in rows)
    result['passed'] = result['r5_check_value_passed'] and result['equation10_max_conversion_error_pK'] <= 2*math.ulp(10.)
    result['amendment'] = '#338 orchestrator plan correction, 2026-11-13: Table 2 residuals reported, exact algebraic conversion checked'
    spec = r.bind(r.s.with_parameter_values(r.s.parameter_mapping(a.RECORDS['candidate']),LITERATURE))
    bound = {rx.name:{k:getattr(rx.correlation,k) for k in ('a','b','c','d','reference_temperature')}
             for rx in next(iter(spec.problems.values())).reactions if rx.name in ('R2','R5')}
    result['bound_laws'] = bound
    result['passed'] = result['passed'] and all(bound['R2'][k]==v for k,v in result['r2_coefficients'].items()) and bound['R5']==result['r5_coefficients']
    write('literature-law-check.json', result)
    print(result,flush=True)
    assert result['passed']


def salt():
    import carbonate_ions_282 as b
    r.verify()
    old = r.read(b.OUT/'salt/summary.json')['result']
    doc = b.salt_document({k: (v['a0'],v['a1']) for k,v in old['laws'].items()})
    parameters = r.epcsaft.Parameters.from_mapping(doc)
    rows = {g:b.predict(doc,b.carbonate_rows(parameters,{g})) for g in ('NaHCO3','Na2CO3')}
    scores = {g:b.aard(v) for g,v in rows.items()}
    errors = {g:a.relative(v['aard_percent'],old['scores'][g]['aard_percent']) for g,v in scores.items()}
    prediction_error=max(a.relative(x['value'],y['value']) for g in rows for x,y in zip(rows[g],old['rows'][g],strict=True))
    write('salt-replay.json',dict(rows=rows,scores=scores,relative_aard_differences=errors,max_relative_prediction_difference=prediction_error,passed=max(errors.values())<=1e-8,wheel_sha256=a.SHA))
    print(scores,errors,flush=True)
    assert max(errors.values())<=1e-8, '#338 stop: salt replay failed'


def replay():
    r.verify()
    record = a.RECORDS['candidate']
    assert a.sha(record) == 'f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97'
    values, ok, cost = r.replay(r.s.parameter_mapping(record))
    reference = r.read(a.OUT/'candidate/replay.json')
    errors = [a.relative(v['value'], old['value']) for v, old in zip(values, reference['rows'], strict=True)] if ok else []
    report = dict(wheel_sha256=a.SHA, engine_commit=a.COMMIT, parameter_sha256=a.sha(record),
                  rows=values, cost=cost, reference_cost=reference['cost'], available=ok,
                  max_relative_prediction_difference=max(errors, default=None),
                  relative_cost_difference=a.relative(cost,reference['cost']) if ok else None,
                  passed=ok and len(values)==307 and max(errors)<=1e-8 and a.relative(cost,reference['cost'])<=1e-8)
    write('F0-replay.json', report)
    print({k:v for k,v in report.items() if k!='rows'}, flush=True)
    assert report['passed'], '#338 stop: F0 replay failed'


def fit(name, start, fixed, fitted, ties=None, scale=None, route=None):
    """One start, with at most two same-control continuations after a limit."""
    mapping = start if route else r.s.with_parameter_values(start, fixed)
    enforced = route.states(route.bind(start)) if route else r.states()[0]
    excluded = set() if route else set(r.read(r.B/'results/stable-refit-255/qualification/summary.json')['result']['excluded'])
    enforced = [x for x in enforced if x['key'] not in excluded]
    if route:
        values, ok, cost = route.replay(mapping)
        route.write(name+'/start-replay.json',dict(rows=values,available=ok,cost=cost))
        if not ok:
            return None, None
    split_found = False
    previous_endpoint = None
    for attempt in range(3):
        if route:
            report = r.stage_fit(name,attempt,scale,mapping,{},enforced if scale else [],route=route)
            if not report.get('endpoint_replay_available'):
                route.write(f'{name}/stage-{attempt}/unavailable.json',report)
                return previous_endpoint if previous_endpoint is not None else (None, report)
            mapping = route.result(f'{name}/stage-{attempt}/parameters.json')
            assert abs(report['endpoint_replay_cost']/(report['data_cost'] if report['data_cost'] is not None else report['final_cost'])-1)<=1e-8
            split_found = any(map(r.descent,route.grid(mapping,enforced))) or split_found
            report['earlier_split'] = split_found
            previous_endpoint = mapping, report
            if report['status']!='limit_reached':
                break
            continue
        path = OUT/name/f'attempt-{attempt}.json'
        legacy = {'F1/previous/unpenalized':'F1/current','F1/current/unpenalized':'F1/r2-held'}.get(name)
        if not path.exists() and legacy and (OUT/legacy/f'attempt-{attempt}.json').exists():
            write(f'{name}/attempt-{attempt}.json',r.read(OUT/legacy/f'attempt-{attempt}.json'))
            write(f'{name}/parameters-{attempt}.json',r.read(OUT/legacy/f'parameters-{attempt}.json'))
        if path.exists():
            report = r.read(path)
            mapping = r.read(OUT/name/f'parameters-{attempt}.json') if report.get('physical') else mapping
        else:
            spec = r.bind(mapping)
            spec.inputs['endpoint'] = mapping
            declared = r.coordinates(spec, {}, fitted=fitted, fixed=fixed, ties=ties)
            values, ok, cost = r.replay(mapping)
            write(f'{name}/declaration.json',dict(declared=declared,fixed=fixed,available=ok,cost=cost))
            if not ok:
                write(f'{name}/no-candidate.json',dict(reason='first-start 307-row evaluation unavailable',rows=values))
                return None, None
            r.OUT = OUT
            report = r.stage_fit(name,attempt,scale,mapping,{},[] if scale is None else enforced,fitted=fitted,fixed=fixed,ties=ties)
            report.update(fixed=fixed,wheel_sha256=a.SHA)
            write(f'{name}/attempt-{attempt}.json',report)
            if not report['physical'] or not report['reactions']:
                return None, report
            mapping = r.result(f'{name}/stage-{attempt}/parameters.json')
            write(f'{name}/parameters-{attempt}.json',mapping)
            mapping = r.read(OUT/name/f'parameters-{attempt}.json')
        print(name,attempt,report['status'],report['final_cost'],flush=True)
        if report['status'] != 'limit_reached':
            break
    if route:
        return mapping, report
    rows, ok, cost = r.replay(mapping)
    write(f'{name}/replay.json',dict(rows=rows,available=ok,cost=cost))
    assert not ok or a.relative(cost,report['data_cost'] if report['data_cost'] is not None else report['final_cost'])<=1e-8
    assert all(r.s.parameter_values(mapping)[k]==v for k,v in fixed.items())
    declared = report['declared']
    changed = {q['identity'] for q in declared}
    changed.update(f'component/{target}/{family}' for q in declared for family,target,_ in q.get('targets',[]) if isinstance(target,str))
    assert all(v == r.s.parameter_values(mapping)[k] for k,v in r.s.parameter_values(start).items() if k not in changed and k not in fixed)
    write(f'{name}/checks.json',dict(endpoint_replay_relative_difference=a.relative(cost,report['data_cost'] if report['data_cost'] is not None else report['final_cost']) if ok else None,fixed_values_identical=True,other_parameters_unchanged=True))
    return mapping if ok else None, report


def split_registry():
    """Exact phase-kind/support/composition/packing deduplication; no rounding."""
    if 'SPLITS' in globals():
        return globals()['SPLITS']
    import json
    pool, sources, unreadable, split_evidence, composed_resolved, composed_unresolved, negative_records = {}, {}, [], set(), set(), set(), {}
    def add(witness, source):
        witness = dict(witness, kind=witness.get('kind','liquid' if len(witness['support'])==len(r.s.COMPONENT_IDS) else 'vapor').lower())
        if len(witness['composition']) != len(r.s.COMPONENT_IDS):
            witness['composition'] = [dict(zip(witness['support'],witness['composition'],strict=True)).get(i,0.) for i in range(len(r.s.COMPONENT_IDS))]
        key = json.dumps(witness, sort_keys=True)
        pool.setdefault(key, witness)
        sources[source] = sources.get(source, 0) + 1
    def scan(raw, source):
        if isinstance(raw, list):
            for value in raw:
                scan(value, source)
        elif isinstance(raw, dict):
            negative = any(isinstance(v,(float,int)) and v<0 and ('tpd' in k.lower() or k.startswith('delta_G_over_RT')) for values in (raw,raw.get('quantities',{})) if isinstance(values,dict) for k,v in values.items())
            if raw.get('resolved_descent') is True or negative:
                split_evidence.add(source)
            if raw.get('composition') and negative and raw.get('resolved_descent') is not True:
                negative_records.setdefault(source,[]).append(raw.get('evidence','indeterminate'))
            if raw.get('composition') and (raw.get('resolved_descent') is True or negative):
                (composed_resolved if raw.get('resolved_descent') is True else composed_unresolved).add(source)
            if raw.get('resolved_descent') and raw.get('split_coordinates') and 'composition' in raw:
                add(dict(kind=raw['phase']['kind'], support=raw['phase']['support'],
                         composition=raw['composition'], packing=math.exp(raw['split_coordinates'][-1])), source)
            elif raw.get('resolved_descent') and raw.get('composition') and raw.get('optimizer',{}).get('success') and raw['optimizer'].get('packing_fractions'):
                # stability-diagnosis/README.md: one liquid trial with all nine species.
                add(dict(kind='liquid',support=list(range(len(r.s.COMPONENT_IDS))),composition=raw['composition'],
                         packing=raw['optimizer']['packing_fractions'][0]),source)
            result = raw.get('result', {})
            if (isinstance(result, dict) and result.get('success') and
                (raw.get('confirmed') or any(raw.get(k,0)<0 for k in ('delta_G_over_RT','delta_G_over_RT_vs_original','delta_G_over_RT_vs_single_liquid')))):
                phases = result.get('phases', [])
                if sum(p['role']=='liquid' for p in phases) >= 2:
                    for phase in phases:
                        add(dict(kind=phase['role'], support=[r.s.COMPONENT_IDS.index(i) for i in phase['support']],
                                 composition=phase['mole_fractions'], packing=phase['packing_fraction']), source)
            for key, value in raw.items():
                if isinstance(value,list) and all(isinstance(w,dict) and {'support','composition','packing'} <= w.keys() for w in value):
                    for witness in value:
                        add(witness, source)
                elif isinstance(value, (dict, list)):
                    scan(value, source)
    import subprocess
    import gzip
    import re
    omitted, unread_formats = [], []
    paths = subprocess.check_output(['git','ls-files','-z','--','analyses/mea_parameter_bundle'],cwd=r.ROOT).decode().split('\0')
    for source in filter(None, paths):
        path = r.ROOT/source
        if path.name in ('split-registry.json','split-completeness.json'):
            continue
        data = gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()
        fields = bool(re.search(rb'composition|mole_fractions|tangent.plane|tpd_over_rt|delta_G_over_RT|witnesses',data))
        try:
            raw = r.read(path) if path.name.endswith(('.json','.json.gz')) else [json.loads(line) for line in data.splitlines() if line.strip()] if path.suffix=='.jsonl' else None
            scan(raw,source)
            if fields and raw is None:
                unread_formats.append(source)
            if fields and source not in sources:
                omitted.append(dict(file=source, fields=sorted(set(x.decode() for x in re.findall(rb'composition[a-z_]*|mole_fractions|tangent.plane[a-z_]*|tpd_over_rt|delta_G_over_RT[a-z_]*|witnesses',data))), reason='no resolved descent, confirmed two-liquid split, or retained witness' if raw is not None else 'non-JSON composition or tangent-plane reference; not parsed'))
        except (ValueError, UnicodeDecodeError) as exc:
            unreadable.append(dict(file=source,reason=str(exc)))
    old = r.read(OUT/'split-registry.json')
    registry = dict(trials=[pool[k] for k in sorted(pool)], sources=sources,
                    before_dedup=sum(sources.values()), after_dedup=len(pool), unreadable=unreadable,
                    dedup_rule='exact kind, ordered support, full component composition and packing; no rounding')
    registry['sha256'] = a.hashlib.sha256(json.dumps(registry['trials'],sort_keys=True).encode()).hexdigest()
    registry.update(previous_trials=old['trials'] if old['sha256']!=registry['sha256'] else old['previous_trials'], previous_sha256=old['sha256'] if old['sha256']!=registry['sha256'] else old['previous_sha256'])
    unread_split = sorted(composed_resolved-sources.keys())
    unresolved = sorted(composed_unresolved-sources.keys()-set(unread_split))
    scalar = sorted(split_evidence-sources.keys()-set(unread_split)-set(unresolved))
    for row in omitted:
        if row['file'] in unread_split:
            row['reason'] = 'unread split'
        elif row['file'] in unresolved:
            row['reason'] = 'negative-distance composition; descent not resolved'
        elif row['file'] in scalar:
            row['reason'] = 'split-indicating record without a retained associated composition'
    write('split-completeness.json',dict(tracked_files=len(paths)-1, without_split=omitted, unreadable=unreadable, unread_formats=unread_formats, unread_split=unread_split, classification_counts=dict(scalar=len(scalar),unresolved_negative=len(unresolved),unread_split=len(unread_split)), explained_scalar=scalar, explained_unresolved_negative=unresolved, admission='A split found earlier is a native resolved descent (#255, Engine #1224; owner 2026-11-13).', class_reasons=dict(explained_scalar='split-indicating record without a retained associated composition', explained_unresolved_negative='Unconverged or rejected optimizer iterates; native descent not resolved.'), excluded_negative_records={state:sum(value==state for source in unresolved for value in negative_records[source]) for state in ('no_resolved_descent','indeterminate')}))
    globals()['SPLITS'] = registry
    write('split-registry.json', registry)
    return registry


def supplied_census(task):
    """Reconstitute the retained parent; evaluate trials without optimizing them."""
    mapping, raw, witnesses = task
    import phase_diagnosis_255 as p
    import tempfile
    original = p.f.stability
    p.f.stability = lambda model,problem,result: original(model,problem,result,supplied=witnesses,retained=raw['stability'][0])
    row = {k:raw[k] for k in ('index','temperature_K','loading','pressure_Pa')}
    with tempfile.TemporaryDirectory(dir=r.ROOT/'.venv') as temporary:
        path = Path(temporary)/'parent.json'
        try:
            p.f.family_job(mapping,p.e.request(mapping,313.15,.11),row,[],path)
        finally:
            p.f.stability = original
        checked = r.read(path)
    assert checked['final']['coordinates']==raw['final']['coordinates'], f"parent changed at {raw['index']}"
    report = checked['stability'][0]
    supplied = report['supplied_trials']
    assert len(supplied)==len(witnesses) and all(t['evidence']=='evaluated' for t in supplied), (raw['index'], [(i,t) for i,t in enumerate(supplied) if t['evidence']!='evaluated'][:2])
    print('supplied',raw['index'],len(supplied),min(t['quantities']['tpd_over_rt'] for t in supplied),flush=True)
    return dict(index=raw['index'], evaluated=len(supplied), negative=sum(map(r.supplied_negative,supplied)),
                minimum_tpd=min(t['quantities']['tpd_over_rt'] for t in supplied),
                minimum_liquid_tpd=min(t['quantities']['tpd_over_rt'] for t,w in zip(supplied,witnesses,strict=True) if w['kind']=='liquid'), unavailable=sum(t['evidence']!='evaluated' for t in supplied),
                distances=[t['quantities']['tpd_over_rt'] for t in supplied])


def search(name, mapping):
    r.OUT = OUT
    registry = split_registry()
    r.GRID_TRIALS = r.read(OUT/'split-trials.json')
    path = OUT/name/'search.json'
    if path.exists() and r.read(path).get('registry_sha256') == registry['sha256']:
        return r.read(path)
    if path.exists():
        from concurrent.futures import ProcessPoolExecutor
        raw = r.result(f'{name}/census-raw.json.gz')
        previous = registry['previous_trials'] if r.read(path).get('registry_sha256')==registry['previous_sha256'] else []
        trials = [w for w in registry['trials'] if w not in previous]
        with ProcessPoolExecutor(r.CORES,initializer=r.verify) as pool:
            supplied = list(pool.map(supplied_census,[(mapping,row,trials) for row in raw]))
        if previous:
            indices = [previous.index(w) if w in previous else None for w in registry['trials']]
            for row,old in zip(supplied,r.result(f'{name}/supplied.json.gz'),strict=True):
                assert row['index']==old['index']
                values = row['distances']
                row['distances'] = [old['distances'][i] if i is not None else values[trials.index(w)] for w,i in zip(registry['trials'],indices,strict=True)]
                row.update(evaluated=len(row['distances']),negative=sum(v<0 for v in row['distances']),minimum_tpd=min(row['distances']),minimum_liquid_tpd=min(v for v,w in zip(row['distances'],registry['trials'],strict=True) if w['kind']=='liquid'),unavailable=old['unavailable']+row['unavailable'])
        r.write(f'{name}/supplied.json.gz',supplied)
        out = r.read(path)
        out['census']['descent_indices'] = sorted(set(out['census']['descent_indices']) | {row['index'] for row in supplied if row['negative']})
        out['census']['descent'] = len(out['census']['descent_indices'])
        out['supplied'] = dict(evaluated=sum(row['evaluated'] for row in supplied), negative=sum(row['negative'] for row in supplied),
                               minimum_tpd=min(row['minimum_tpd'] for row in supplied), minimum_liquid_tpd=min(row['minimum_liquid_tpd'] for row in supplied), unavailable=sum(row['unavailable'] for row in supplied), compositions=len(registry['trials']))
    else:
        chosen, offset = r.states()
        memory = r.read(OUT/'split-trials.json')
        rows = r.grid(mapping,chosen+offset,memory)
        write(f'{name}/grid.json',rows)
        census = r.census(mapping,name)
        for raw in r.result(f'{name}/census-raw.json.gz'):
            for report in raw.get('stability', []):
                for trial in report['trials']:
                    if trial['resolved_descent'] and trial['split_coordinates']:
                        memory.setdefault('census', {}).setdefault(str(raw['index']), []).append(dict(kind=trial['phase']['kind'],
                            support=trial['phase']['support'], composition=trial['composition'], packing=math.exp(trial['split_coordinates'][-1])))
        write('split-trials.json',memory)
        write(f'{name}/search.json',dict(grid=r.tally(rows[:1908]),offset=r.tally(rows[1908:]),census=census))
        globals().pop('SPLITS',None)
        return search(name,mapping)
    out['registry_sha256'] = registry['sha256']
    out['stable'] = all(out[g]['descent']==0 for g in ('grid','offset','census')) and not out['grid']['unavailable'] and not out['offset']['unavailable'] and out['census']['incomplete']==0
    write(f'{name}/search.json',out)
    print(name,out,flush=True)
    return out


def coverage():
    """Complete earlier split-composition checks without repeating fitted evidence."""
    r.OUT = OUT
    r.verify()
    if not (OUT/'F0/census-raw.json.gz').exists():
        r.write('F0/census-raw.json.gz',[r.read(a.OUT/f'candidate/census/{i}.json')['raw'] for i in range(162)])
    if not (OUT/'F0/search.json').exists():
        previous = r.read(a.OUT/'f2.json')['records']['candidate']
        write('F0/search.json',dict(grid=dict(states=1908,available=1908,descent=0,unavailable=[]),offset=previous['offset'],
              census=dict(states=162,descent=0,incomplete=0,descent_indices=[],incomplete_indices=[])))
    results = {}
    names = ['F0']+[f'{fit}/{start}/unpenalized' for fit in ('F1','F2','F3','F4','F4-0','F5') for start in ('previous','current')]
    for name in names:
        path = OUT/'F0/parameters.json' if name=='F0' else sorted((OUT/name).glob('parameters-*.json'))[-1]
        results[name] = search(name,r.s.parameter_mapping(path))
        write('coverage-summary.json',results)
        assert results[name]['stable'], f'{name}: prescribed stability-enforced route required'


def information(name, mapping, declared):
    """Use #307's exact derivative and its shared conditional-information producer."""
    import uncertainty_307 as u
    from types import SimpleNamespace
    import numpy as np
    spec = r.bind(mapping)
    values = r.s.parameter_values(mapping)
    declared = [dict(q,origin=values[q['identity']],value=values[q['identity']]) for q in declared]
    spec.inputs['coordinates'] = declared
    ev = u.derivative(spec,spec.inputs['observations']['fitted'])
    rows, ok, cost = r.replay(mapping)
    assert ok and max(a.relative(p,x['value']) for p,x in zip(ev.predictions,rows,strict=True))<=1e-8
    scales = np.array([q['scale'] for q in declared])
    weights = np.sqrt([x['weight'] for x in spec.inputs['observations']['fitted']])
    J = np.array(ev.residual_optimizer_gradient).reshape(len(rows),len(declared))*weights[:,None]/scales
    residual = np.array([x['residual'] for x in rows])*weights
    active = [i for i,q in enumerate(declared) if min(q['origin']-q['bounds'][0],q['bounds'][1]-q['origin'])<=1e-6*q['scale']]
    out = u.refit.identifiability(SimpleNamespace(physical=[q['origin'] for q in declared],covariance=SimpleNamespace(active_bounds=active)),
        J,residual,[q['identity'] for q in declared],[q['bounds'][0] for q in declared],[q['bounds'][1] for q in declared])
    out.update(coordinates=declared,active_bounds=active,weighted_physical_jacobian=J.tolist(),cost=cost)
    out['conditional_standard_error_ratio']={k:v/abs(values[k]) if values[k] else None for k,v in out['conditional_standard_error'].items()}
    out['correlation_pairs_above_095']=[dict(parameters=[out['free_coordinates'][i],out['free_coordinates'][j]],correlation=v) for i,row in enumerate(out['conditional_correlation']) for j,v in enumerate(row) if j>i and abs(v)>.95]
    out['shared_reactions']=[rx for rx in spec.spec['chemistry']['reactions']['aqueous'] if rx['name'] in ('R1','R2','R3')]
    out['shared_water_ion_pairs']=[p for p in mapping['pairs'] if 'water' in (p['component_id_a'],p['component_id_b']) and any(x in (p['component_id_a'],p['component_id_b']) for x in ('bicarbonate-anion','carbonate-anion'))]
    out['se_larger_than_value'] = [k for k,v in out['conditional_standard_error'].items() if v>abs(values[k])]
    write(f'{name}/information.json',out)


def evidence(name, path):
    """Run the adoption assessment owners; stage their executable copies outside retained evidence."""
    import tempfile
    e.EV, e.RECORDS = OUT/'evidence', {name:path}
    original = e.copy_of
    def copy_of(*args,**kwargs):
        produced = original(*args,**kwargs)
        text = produced.read_text().replace('os.cpu_count()', "int(os.environ['AGENT_HEAVY_CORES'])")
        if "SPEC = json.loads((BASE/'spec.json').read_text())" in text:
            import importlib.metadata
            engine=dict(wheel_path=str(a.WHEEL.relative_to(r.ROOT)),wheel_sha256=a.SHA,packages={k:importlib.metadata.version(k) for k in ('epcsaft','numpy','scipy')})
            text=text.replace("SPEC = json.loads((BASE/'spec.json').read_text())","SPEC = json.loads((BASE/'spec.json').read_text())\nSPEC['engine'] = "+repr(engine))
        produced.unlink()
        temporary = Path(tempfile.mkdtemp(dir=r.ROOT/'.venv'))/produced.name
        temporary.write_text(text)
        return temporary
    e.copy_of = copy_of
    try:
        e.assessment(name)
        r.OUT = OUT/'point-data'
        r.write(f'{name}/replay.json',r.read(OUT/name/'replay.json')['rows'])
        e.point_data(name,name)
        curves = e.curves(name)
        e.kim(name,curves)
        e.density(name)
        e.heat_capacity(name)
    finally:
        e.copy_of, r.OUT = original, OUT


def candidate(name, start, fixed, fitted, ties, route=None):
    from functools import partial
    fit_call = fit if route is None else partial(fit,route=route)
    search_call = search if route is None else lambda name,mapping: route.search(mapping)
    write_call, folder = (write,OUT) if route is None else (route.write,route.out)
    endpoints = []
    def retain(mapping, report, searched):
        endpoints.append(dict(name=name,cost=report['endpoint_replay_cost'],parameters=mapping,declared=report['declared'],optimizer_converged=report['status']=='converged',stable=searched['stable'],search=searched,split_counts='lower bounds',disposition='not converged' if report['status']!='converged' else 'converged and stable' if searched['stable'] else 'converged but still splitting' if any(searched[g]['descent'] for g in ('grid','offset','census')) else f"no split found in the available searches; {len(searched['grid']['unavailable'])} searches unavailable",optimizer_report=report))
        route.write(f'{name}/endpoints.json',endpoints)
    mapping, report = fit_call(name+'/unpenalized',start,fixed,fitted,ties)
    if mapping is None:
        return None
    unpenalized = search_call(name+'/unpenalized',mapping)
    if route: retain(mapping,report,unpenalized)
    if report['status'] != 'converged':
        write_call(f'{name}/finding.json',dict(reason='unpenalized start not converged after permitted continuations',cost=report['final_cost'],unpenalized=unpenalized))
        return endpoints[-1] if route and endpoints else None
    chosen, final_report = mapping, report
    if report.get('earlier_split') or any(unpenalized[g]['descent'] for g in ('grid','offset','census')):
        stable_anchor = None
        for index, scale in enumerate(r.STAGES):
            if final_report['status'] != 'converged':
                break
            try:
                chosen, final_report = fit_call(name+f'/penalized-{index}',chosen,fixed,fitted,ties,scale)
            except ValueError as error:
                if route is None: raise
                route.write(name+f'/penalized-{index}/unavailable.json',dict(cause=str(error)))
                chosen = None
                break
            if chosen is None:
                break
            searched = search_call(name+f'/penalized-{index}',chosen)
            if route:
                retain(chosen,final_report,searched)
            if searched['stable']:
                stable_anchor = chosen
        if chosen is not None and not searched['stable']:
            anchor = stable_anchor if stable_anchor is not None else (start if route else r.s.with_parameter_values(start,fixed))
            if stable_anchor is not None or search_call(name+'/anchor',anchor)['stable']:
                enforced = route.states(route.bind(start)) if route else r.states()[0]
                excluded = set() if route else set(r.read(r.B/'results/stable-refit-255/qualification/summary.json')['result']['excluded'])
                r.OUT = OUT
                r.retreat(name,anchor,chosen,[x for x in enforced if x['key'] not in excluded],shifts=({},{}),route=route,optimizer_report=final_report)
                if route is None:
                    write_call('split-trials.json',r.GRID_TRIALS)
                path = folder/name/'candidate.json'
                chosen = (route.result if route else r.result)(f'{name}/candidate.json') if path.exists() else None
            else:
                chosen = None
    if route:
        converged = [point for point in endpoints if point['optimizer_converged']]
        return min(converged or endpoints,key=lambda point:point['cost'])
    if chosen is None:
        write_call(f'{name}/finding.json',dict(reason='no stability-enforced candidate',unpenalized=unpenalized))
        return None
    final_search = unpenalized if chosen is mapping else search_call(name+'/candidate',chosen)
    rows, ok, cost = (route.replay if route else r.replay)(chosen)
    converged = final_report['status']=='converged'
    retreat = (route.result(f'{name}/retreat.json') if route and (folder/name/'retreat.json').exists() else None)
    write_call(f'{name}/finding.json',dict(cost=cost,optimizer_converged=converged,retreat=retreat,stable=final_search['stable'],unpenalized=unpenalized,penalty_cost=0. if final_search['stable'] else None,endpoint_penalty_cost=final_report['stability_cost']))
    if not (ok and converged and final_search['stable']):
        return None
    write_call(f'{name}/parameters.json',chosen)
    write_call(f'{name}/replay.json',dict(rows=rows,cost=cost))
    return dict(name=name,cost=cost,parameters=chosen,declared=final_report['declared'],optimizer_converged=converged,optimizer_cost=final_report.get('data_cost',final_report['final_cost']),retreat=retreat)


def campaign():
    import copy
    import carbonate_ions_282 as b
    r.OUT = OUT
    current = r.s.parameter_mapping(a.RECORDS['candidate'])
    previous = current
    fixed = dict(LITERATURE)
    fitted = [q['identity'] for q in r.read(r.A6)['information_coordinates'] if 'reaction' not in q]
    ties = {}
    summaries = {}
    assert r.read(OUT/'F0-replay.json')['passed'] and r.read(OUT/'literature-law-check.json')['passed'] and r.read(OUT/'salt-replay.json')['passed']
    for number in range(1,6):
        name = f'F{number}'
        if number==2:
            for ion in ('protonated-monoethanolamine','carbamate-anion'):
                fitted.remove(f'component/{ion}/born_diameter')
                ties[f'component/{ion}/segment_diameter'] = [['born_diameter',ion,1.]]
            probe=r.s.with_parameter_values(previous,{f'component/{ion}/born_diameter':r.s.parameter_values(previous)[f'component/{ion}/segment_diameter'] for ion in ('protonated-monoethanolamine','carbamate-anion')})
            spec=r.bind(r.s.with_parameter_values(probe,fixed))
            spec.inputs['endpoint']=r.s.with_parameter_values(probe,fixed)
            spec.inputs['coordinates']=r.coordinates(spec,{},fitted=fitted,fixed=fixed,ties=ties)
            try:
                ev=r.reg.differentiate(spec.parameters,spec.coordinates(),[spec.observation(spec.inputs['observations']['fitted'][0])],
                    optimizer=[0.]*len(fitted),holds=[],thermochemistry=spec.thermal)
                write('born-tie-outcome.json',dict(accepted=True,statuses=[x.name for x in ev.statuses],declaration=spec.inputs['coordinates']))
            except r.epcsaft.ParameterError as error:
                write('born-tie-outcome.json',dict(accepted=False,refusal=str(error),declaration=spec.inputs['coordinates'],substitute='Born diameters fixed at F1 fitted segment diameters'))
                fixed.update({f'component/{ion}/born_diameter':r.s.parameter_values(previous)[f'component/{ion}/segment_diameter'] for ion in ('protonated-monoethanolamine','carbamate-anion')})
                ties={}
        if number==3:
            for k in ('pair/carbamate-anion/water/k_ij','pair/protonated-monoethanolamine/water/k_ij/reciprocal_temperature_slope'):
                fixed[k]=0.
                fitted.remove(k)
        if number==4:
            fitted.remove('pair/bicarbonate-anion/water/k_ij')
            fitted.append(dict(identity='pair/bicarbonate-anion/protonated-monoethanolamine/k_ij',family='k_ij',
                               target=['bicarbonate-anion','protonated-monoethanolamine'],scale=.01,bounds=[-1.,1.]))
        if number==5:
            k='pair/carbamate-anion/protonated-monoethanolamine/k_ij'
            fixed[k]=0.
            fitted.remove(k)
        candidates=[]
        prepared={}
        for label, source in [('previous',previous),('current',current)]:
            if number==1 and label=='current':
                source=r.read(r.B/'results/stable-refit-255/r2-held/candidate.json')['result']
            start=copy.deepcopy(source)
            if number>=2:
                start=r.s.with_parameter_values(start,{f'component/{ion}/born_diameter':r.s.parameter_values(start)[f'component/{ion}/segment_diameter'] for ion in ('protonated-monoethanolamine','carbamate-anion')})
            if number>=4:
                laws=r.read(b.OUT/'salt/summary.json')['result']['laws_at_record_reference']
                for ion in (b.HCO3,b.CO3):
                    law=laws[ion]
                    b.set_pair(start,ion,b.W,b.law_node(b.LAWS[ion],law['a0'],law['a1'],law['t_ref'],dict(source_id='carbonate-ions-282',locator='salt/summary.json')))
                identity='pair/bicarbonate-anion/protonated-monoethanolamine/k_ij'
                if identity not in r.s.parameter_values(start):
                    b.set_pair(start,b.HCO3,b.MEAH,b.k_node(start,identity,0.,dict(source_id='issue-338',locator='F4 start')))
            prepared[label]=start
            result=candidate(name+'/'+label,start,fixed,fitted,ties)
            if result:
                candidates.append(result)
        if candidates:
            best=min(candidates,key=lambda x:x['cost'])
            summaries[name]=dict(start=best['name'],cost=best['cost'],delta_F0=best['cost']-148.51054565397726,
                                 tied_starts=[x['name'] for x in candidates if abs(x['cost']-best['cost'])<=r.read(r.A6)['controls']['function_tolerance']*best['cost']])
            previous=best['parameters']
            write(f'{name}/parameters.json',previous)
            summaries[name]['record_sha256']=a.sha(OUT/name/'parameters.json')
            write(f'{name}/replay.json',r.read(OUT/best['name']/'replay.json'))
            information(name,previous,best['declared'])
            if number==4:
                key='pair/bicarbonate-anion/protonated-monoethanolamine/k_ij'
                if abs(abs(r.s.parameter_values(previous)[key])-1.)<=1e-6*.01:
                    reduced=[q for q in fitted if not (isinstance(q,dict) and q['identity']==key)]
                    alternatives=[candidate('F4-0/'+label,source,dict(fixed,**{key:0.}),reduced,ties)
                                  for label,source in prepared.items()]
                    alternatives=[x for x in alternatives if x]
                    if alternatives:
                        selected=min(alternatives,key=lambda x:x['cost'])
                        summaries['F4-0']=dict(start=selected['name'],cost=selected['cost'],delta_F0=selected['cost']-148.51054565397726, tied_starts=[x['name'] for x in alternatives if abs(x['cost']-selected['cost'])<=r.read(r.A6)['controls']['function_tolerance']*selected['cost']])
                        write('F4-0/parameters.json',selected['parameters'])
                        summaries['F4-0']['record_sha256']=a.sha(OUT/'F4-0/parameters.json')
                        write('F4-0/replay.json',r.read(OUT/selected['name']/'replay.json'))
                        information('F4-0',selected['parameters'],selected['declared'])
                    else:
                        summaries['F4-0']=dict(reason='no converged stable candidate')
        else:
            summaries[name]=dict(reason='no converged stable candidate; see each start finding')
            findings=[]
            for label in prepared:
                folder=OUT/name/label/'unpenalized'
                reports=sorted(folder.glob('attempt-*.json'))
                if reports and r.read(reports[-1])['status']=='converged' and (folder/'replay.json').exists():
                    replayed=r.read(folder/'replay.json')
                    if replayed['available']:
                        findings.append((replayed['cost'],folder,reports[-1]))
            if findings:
                cost,folder,report=min(findings)
                endpoint=r.read(folder/f"parameters-{report.stem.split('-')[-1]}.json")
                write(f'{name}/unpenalized-finding.json',endpoint)
                write(f'{name}/replay.json',r.read(folder/'replay.json'))
                summaries[name].update(unpenalized_cost=cost,delta_F0=cost-148.51054565397726,record_sha256=a.sha(OUT/name/'unpenalized-finding.json'))
                information(name,endpoint,r.read(report)['declared'])
            previous=current
        write('summary.json',summaries)


def scores(name, mapping):
    root=a.OUT/'paper-evidence' if name=='F0' else OUT/'evidence'/name
    fitted=r.read(OUT/name/'replay.json')['rows']
    groups={}
    for label,group,quantity,_ in r.GROUPS:
        groups['fitted: '+label]=[dict(observed=x['observed'],predicted=x['value'],cost=x['cost'],residual=x['residual']) for x in fitted
            if x['group']==group and (quantity is None or (x['row'].get('quantity') or x['row'].get('kind'))==quantity)]
    states=e.rows(root/'state-targets.csv')
    ids={x['identity'] for x in fitted}
    groups['not fitted: six-source pressures']=[x for x in states if x['kind']=='canonical' and x['quantity']=='pressure' and x['target'] not in ids]
    groups['not fitted: Wagner pressures']=[x for x in states if x['kind']=='wagner']
    roles=r.read(root/'state-summary.json')['scores']
    for label in ('transfer 15 wt%','transfer 45 wt%','Matin 19 pools'):
        members=set(roles[label]['row_ids'])
        groups['not fitted: '+label]=[x for x in states if x['target'] in members and x['kind']==('transfer' if label.startswith('transfer') else 'packet')]
    groups['not fitted: Arcis heats']=[dict(observed=x['observed_kJ_mol'],predicted=x['predicted_kJ_mol'],cost=.5*float(x['scaled_residual'])**2) for x in e.rows(root/'heat.csv') if x['source']=='Arcis2011']
    kim_ids={x['record_id'] for x in e.rows(a.OUT/'paper-evidence/kim2007-heat-pathways/kim-heat.csv') if float(x['T_K']) in (313.15,353.15) and x['interval_status']=='available'}
    groups['not fitted: Kim heats']=[dict(observed=x['observed'],predicted=x['predicted'],cost=.5*float(x['scaled_residual'])**2 if x['scaled_residual'] else None) for x in e.rows(root/'kim2007-heat-pathways/kim-heat.csv') if x['record_id'] in kim_ids]
    groups['not fitted: Han densities']=[dict(observed=x['observed'],predicted=x['value'],cost=.5*x['residual']**2) for x in r.read(root/'density-268/density.json')['result'] if x['row']['source']=='Han2012']
    groups['not fitted: broad heat capacities']=[dict(observed=x['observed_kJ_kg_K'],predicted=x['predicted_kJ_kg_K'],cost=.5*x['residual']**2) for x in r.read(root/'heat-capacity-264.json')['rows'] if x['group']=='broad Cp']
    spec=r.bind(mapping)
    bottinger=[]
    for item in r.bottinger_targets(spec,mapping):
        value=r.reg.predict(spec.model,item['item'])
        bottinger.append(dict(identity=item['identity'],species=item['species'],status=value.status.name,message=value.message,observed=item['observed'],predicted=value.value,cost=.5*value.residual**2 if value.status.name=='Available' and value.requested_tolerance_met else None))
    write(f'{name}/bottinger-353.json',bottinger)
    groups['not fitted: Bottinger 353 K']=bottinger
    groups.pop('fitted: Cai MEA-water VLE')
    for quantity in ('temperature','mole_fraction'):
        groups['fitted: Cai '+quantity]=[dict(observed=x['observed'],predicted=x['value'],cost=x['cost'],residual=x['residual']) for x in fitted if x['group']=='Cai' and x['row']['quantity']==quantity]
    out=[]
    for label,rows in groups.items():
        available=[x for x in rows if x['predicted'] not in (None,'','None') and x['cost'] is not None]
        if len(available)!=len(rows):
            out.append(dict(fit=name,dataset=label,n=len(rows),available=len(available),cost=None,aard_percent=None,rmse=None,bias=None))
            continue
        measured=[float(x['observed']) for x in rows]
        errors=[float(x['predicted'])-v for x,v in zip(rows,measured,strict=True)]
        out.append(dict(fit=name,dataset=label,n=len(rows),cost=sum(float(x['cost']) for x in rows),
                        aard_percent=100*sum(abs(error/value) for error,value in zip(errors,measured,strict=True))/len(rows),
                        rmse=math.sqrt(sum(x*x for x in errors)/len(rows)),bias=sum(errors)/len(rows),within_2scale=sum(abs(x['residual'])<=2 for x in rows) if all('residual' in x for x in rows) else None))
    write(f'{name}/agreement.json',out)
    return out


def assess_all():
    import shutil
    (OUT/'F0').mkdir(exist_ok=True)
    shutil.copyfile(a.RECORDS['candidate'],OUT/'F0/parameters.json')
    write('F0/replay.json',r.read(OUT/'F0-replay.json'))
    table_rows=[]
    for name in ['F0',*r.read(OUT/'summary.json')]:
        path=OUT/name/'parameters.json'
        if not path.exists():
            path=OUT/name/'unpenalized-finding.json'
        if not path.exists():
            continue
        if name!='F0':
            evidence(name,path)
        table_rows.extend(scores(name,r.read(path)))
    baseline={x['dataset']:x for x in table_rows if x['fit']=='F0'}
    for x in table_rows:
        base=baseline[x['dataset']]
        x.update(aard_change_points=x['aard_percent']-base['aard_percent'] if x['aard_percent'] is not None else None,rmse_ratio=x['rmse']/base['rmse'] if x['rmse'] is not None and base['rmse'] else None,within_2scale_change=x.get('within_2scale')-base['within_2scale'] if x.get('within_2scale') is not None else None)
    table('agreement.csv',table_rows)


def check_retreat():
    r.OUT=OUT
    mapping=r.s.parameter_mapping(r.STARTS['wide'])
    state=next(x for x in r.states()[0] if x['key']=='dense|0.15|313.15|0.6|1.05')
    measured=r.grid(mapping,[state])
    assert r.descent(measured[0]), measured
    r.retreat('retreat-no-endpoint-check',mapping,None,[state],shifts=({},{}))
    assert not (OUT/'retreat-no-endpoint-check/candidate.json').exists()
    write('retreat-no-endpoint-check/measured.json',measured)


def present():
    import matplotlib.pyplot as plt
    summary=r.read(OUT/'summary.json')
    rows,parameter_rows=[],[]
    units={q['identity']:q['unit'] for q in r.read(a.OUT/'conditional-uncertainty.json')['coordinate_map']}
    for name,data in {'F0':dict(cost=148.51054565397726),**summary}.items():
        path=OUT/name/'information.json'
        info=r.read(path) if path.exists() else r.read(a.OUT/'conditional-uncertainty.json') if name=='F0' else {}
        coordinates=info.get('coordinates',info.get('coordinate_map',[]))
        values={q['identity']:q.get('value',q['origin']) for q in coordinates}
        errors=info.get('conditional_standard_error',{})
        parameter_rows.extend(dict(fit=name,identity=q['identity'],unit=units.get(q['identity'],'dimensionless'),value=values[q['identity']],lower=q['bounds'][0],upper=q['bounds'][1],scale=q['scale'],on_bound=i in info['active_bounds'] or q['identity'] in info['active_bounds'],conditional_SE=errors.get(q['identity']),SE_over_absolute_value=errors[q['identity']]/abs(values[q['identity']]) if q['identity'] in errors and values[q['identity']] else None) for i,q in enumerate(coordinates))
        rows.append(dict(fit=name,cost=data.get('cost',data.get('unpenalized_cost')),delta_F0=data.get('delta_F0',0. if name=='F0' else None),
                         fitted_parameters=len(coordinates) if info else None,on_bound=len(info['active_bounds']) if info else None,
                         SE_larger_than_value=sum(v>abs(values[k]) for k,v in errors.items()) if info else None,
                         record_sha256=data.get('record_sha256',a.sha(a.RECORDS['candidate']) if name=='F0' else None),
                         disposition=data.get('reason','finite-search candidate' if name!='F0' else 'current record replay')))
    table('fit-comparison.csv',rows)
    table('parameter-details.csv',parameter_rows)
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    for i,row in enumerate(rows):
        if row['cost'] is not None:
            ax.scatter(i,row['cost']-rows[0]['cost'],marker='o' if row['disposition'].startswith(('finite','current')) else 'x',color='#0072B2')
    ax.axhline(0,color='0.5',linewidth=.8)
    ax.set(xticks=range(len(rows)),xticklabels=[x['fit'] for x in rows],ylabel='307-row fitted cost minus F0 (dimensionless)',xlabel='Cumulative parameter fixes')
    fig.savefig(OUT/'cost-comparison.png',dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    {'coverage': coverage, 'laws': laws, 'replay': replay, 'salt': salt, 'campaign': campaign, 'assess': assess_all, 'present': present, 'check-retreat': check_retreat}[sys.argv[1]]()
