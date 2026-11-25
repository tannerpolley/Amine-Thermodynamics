"""Use the Table S6 source-row population in the salt-anchored fit."""
# ruff: noqa: E402
import csv
from functools import lru_cache
import math
import sys
from time import monotonic

from calculations import OUT, WORK, a, r, save

s, eq, f = r.s, r.eq, a.f
REFERENCE = a.OUT / 'MEA'
S6 = r.B / 'results/paper-evidence-341/paper-evidence/canonical-pressure.csv'


@lru_cache
def canonical():
    with s.CANONICAL_VLE.open(newline='') as stream:
        return {row['observation_id']: row for row in csv.DictReader(stream)}


@lru_cache
def membership():
    with S6.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    selected = {row['target']: canonical()[row['identity'].removeprefix('canonical:')] for row in rows}
    assert len(selected) == len(rows) == 159
    assert len({(row['source_file'], row['source_row']) for row in selected.values()}) == len(selected)
    assert all(row['active_view_member'] == 'yes' for row in selected.values())
    assert all(float(q['observed']) == float(selected[q['target']]['CO2_pressure'])*1000 for q in rows)
    return selected


@lru_cache
def requests():
    import final_evidence

    _, groups = final_evidence.observations()
    canonical_requests = {row['targets'][0]['identity']: row for row in groups['canonical']}
    assert membership().keys() <= canonical_requests.keys()
    return canonical_requests, {row['targets'][0]['identity']: row for row in groups['wagner']}


def pressure_record(spec, template, identity, evidence, *, group):
    request = evidence['request']
    problem = s._problem_from_request(s.corrected_request(request, s.reaction_values(spec.inputs['endpoint']),
                                                          mapping=spec.inputs['endpoint']))
    bind = spec.problems[template['problem']]
    problem.reactions = bind.reactions
    problem.neutral_reference = bind.neutral_reference
    problem.row_tolerance = bind.row_tolerance
    target, = evidence['targets']
    observed = target['observed']
    spec.problems[identity] = problem
    arguments = dict(template['arguments'], observed=observed, phase=problem.phases[1].name)
    source = request['reaction_system'].get('analytical_feed_contract', {}).get('source_coordinates', {})
    row = dict(id=identity, observed=observed, quantity='PartialPressure', temperature_K=problem.T,
               feed_mol=dict(zip(s.COMPONENT_IDS, problem.feed.values, strict=True)),
               source=target['source_identity'], source_coordinates=source, weight=template['weight'],
               form='LogRatio', scale=1.)
    return dict(template, identity=identity, problem=identity, group=group, row=row, arguments=arguments,
                unit='Pa', temperature_domain=[293.15, 393.15], basis=dict(template['basis'], arguments=arguments))


def pressure_template(spec):
    return [q for q in spec.inputs['observations']['fitted'] if q['group']=='common149' and q['kind']=='partial_pressure']


def expanded(spec):
    legacy = pressure_template(spec)
    primary, _ = requests()
    old = {q['identity']: q for q in legacy}
    assert len(old) == 47 and old.keys() <= membership().keys()
    assert all(q['arguments']['observed'] == float(membership()[i]['CO2_pressure'])*1000 for i, q in old.items())
    new = [pressure_record(spec, legacy[0], i, primary[i], group='Table S6 additions')
           for i in membership() if i not in old]
    assert len(new) == 112 and all(q['temperature_domain'][0] <= spec.problems[q['problem']].T <= q['temperature_domain'][1] for q in new)
    originals = spec.inputs['observations']['fitted']
    assert len(originals) == 307
    return [*originals, *new]


def statistics(rows):
    good = [x for x in rows if x['status']=='Available' and x['requested_tolerance_met']]
    error = [x['value']/x['observed']-1 for x in good]
    return dict(attempted=len(rows), available=len(good),
                bias_percent=100*math.fsum(error)/len(error) if error else None,
                AARD_percent=100*math.fsum(map(abs,error))/len(error) if error else None,
                log_RMSE=math.sqrt(math.fsum(math.log1p(e)**2 for e in error)/len(error)) if error else None)


def replay(mapping, label):
    spec = r.bind(mapping)
    spec.inputs['endpoint'] = mapping
    records = expanded(spec)
    values = r.d.evaluate(spec, records)
    baseline = r.read(REFERENCE / 'F2-control/replay.json')['rows']
    assert [(x['identity'],x['group'],x['row']) for x in values[:307]] == [(x['identity'],x['group'],x['row']) for x in baseline]
    inc = r.read(REFERENCE / 'F4/replay.json')['rows']
    originals = values[:307]
    metrics = r.metrics(originals) if all('cost' in x for x in originals) else None
    by_pressure = {x['identity']: x for x in values if x['identity'] in membership()}
    _, held = requests()
    hot_wagner = [pressure_record(spec, pressure_template(spec)[0], i, evidence, group='Wagner comparison')
                  for i,evidence in held.items()
                  if evidence['request']['temperature']['value'] >= 370.]
    wagner = r.d.evaluate(spec, hot_wagner)
    assert len(wagner) == 12
    hot = [x for i,x in by_pressure.items() if float(membership()[i]['temperature_reported_C']) + 273.15 >= 370.]
    assert len(hot) == 54
    pools = {name: [x for i,x in by_pressure.items() if rowcheck(i)] for name, rowcheck in (
        ('legacy', lambda i: by_pressure[i]['group']=='common149'),
        ('added', lambda i: by_pressure[i]['group']=='Table S6 additions'),
        *[(source, lambda i, source=source: membership()[i]['source_key']==source)
          for source in sorted({q['source_key'] for q in membership().values()})],
        *[(f'{T} C nominal', lambda i, T=T: series(membership()[i])==T)
          for T in (40,60,80,100,120)],
    )}
    pools.update(hot_expanded=hot, hot_published=hot+wagner, all_pressure=list(by_pressure.values()))
    costs = [math.fsum(x['cost'] for x in group) if all('cost' in x for x in group) else None
             for group in (originals, values)]
    summary = dict(parameter_fingerprint=s.parameter_fingerprint(mapping), original_cost=costs[0],
                   expanded_cost=costs[1], pressure={name:statistics(rows) for name,rows in pools.items()},
                   metrics=metrics, relative_to_F2=r.acceptance(metrics,r.metrics(baseline)) if metrics else None,
                   relative_to_incumbent=r.acceptance(metrics,r.metrics(inc)) if metrics else None)
    save(OUT / f'E/{label}/replay.json.gz', dict(summary=summary, rows=values, hot_wagner=wagner,
          pressure_population=membership(), source_hashes={p.relative_to(r.ROOT).as_posix():s.sha256(p) for p in (S6,s.CANONICAL_VLE)}))
    print(label, costs, summary['pressure']['hot_expanded'], summary['pressure']['hot_published'], flush=True)
    return summary


def series(row):
    return round(float(row['temperature_series_C'] or row['temperature_reported_C']))


def fit(label):
    started = monotonic()
    a.study.reuse.bind_wheel()
    r.verify()
    r.OUT = a.OUT
    if label in ('incumbent', 'historical-F2'):
        path = REFERENCE/'F4/parameters.json' if label == 'incumbent' else a.study.RECORD
        replay(s.parameter_mapping(path), label)
    else:
        mapping, coordinates, ties = a.mea_start(label)
        f.OUT = r.OUT = WORK / 'E'
        endpoint, report = f.fit(label, mapping, f.LITERATURE, coordinates, ties, rows=expanded)
        if endpoint is not None:
            save(OUT / f'E/{label}/parameters.json', endpoint)
            replay(endpoint, label)
        save(OUT / f'E/{label}/optimizer.json.gz', report)
    save(OUT / f'E/{label}/fit-timing.json', dict(seconds=monotonic()-started, projected_fit_s=67*419/307))


def off_window():
    started = monotonic()
    r.verify()
    rows = [q for q in canonical().values() if q['active_view_member']=='yes' and q['CO2_pressure']
            and q['MEA_weight_fraction'] and q['temperature_reported_C'] and (
        (q['source_key']=='Jou1995' and float(q['temperature_reported_C'])<40 and float(q['MEA_weight_fraction'])==.30)
        or (q['source_key']=='Aronu2011' and float(q['MEA_weight_fraction']) in (.15,.45)))]
    template = next(iter(requests()[0].values()))['request']
    for label in ('incumbent','F2','F4'):
        path = REFERENCE/'F4/parameters.json' if label=='incumbent' else OUT/f'E/{label}/parameters.json'
        mapping = s.parameter_mapping(path)
        spec = r.bind(mapping)
        spec.inputs['endpoint'] = mapping
        observations = []
        for source in rows:
            identity = 'off-window:'+source['observation_id']
            q = pressure_record(spec,pressure_template(spec)[0],identity,dict(
                request=s.source_feed_request(template,source),targets=[dict(source_identity=source['source_key'],
                    observed=float(source['CO2_pressure'])*1000)]),group=source['source_key'])
            observations.append(dict(q,role='comparison'))
        values = r.d.evaluate(spec,observations)
        save(OUT/f'E/{label}/off-window.json.gz',dict(rows=values,source_rows=rows,
             parameter_sha256=s.sha256(path),source_sha256=s.sha256(s.CANONICAL_VLE),seconds=monotonic()-started))


if __name__=='__main__':
    for label in sys.argv[1:]:
        if label=='off-window':
            a.study.reuse.bind_wheel()
            off_window()
        else:
            fit(label)
