"""Start-A sensitivity at the #440 fixed 100 kPa reaction reference."""
from copy import deepcopy
from pathlib import Path
import sys
from time import monotonic

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'fixed_reaction_reference'))
from refit import (OUT, P_REF, REPLAY_TOLERANCE, a, configured, endpoint_diagnostics,
                   fingerprint, r, replay, row_manifest, salt_pairs)
from calculations import mdea_incumbent, save
from mea_pressure import expanded, membership

RESULTS = HERE / 'results'


def start(amine):
    route, _, _ = configured(amine, 'round-9-shared-interactions')
    manifest = r.read(OUT / amine / 'manifest.json.gz')
    baseline = manifest['start_A_declaration']
    point = deepcopy(baseline)
    historical, source = mdea_incumbent('historical')
    shared = salt_pairs(historical['parameters'])
    for pair in shared:
        node, = [q for q in pair['coefficients'] if q['family'] == 'k_ij']
        assert node['value']['magnitude'] in (0.7650000233694618, -0.25)
        a.salt.set_pair(point['parameters'], pair['component_id_a'], pair['component_id_b'], node)
    spec = route.bind(point)
    assert row_manifest(spec) == row_manifest(route.bind(baseline))
    assert all(rx.reference.reference_pressure_pa == P_REF
               for problem in spec.problems.values() for rx in problem.reactions)
    return route, point, spec, manifest, shared, source


def fit(amine, maximum_seconds, *, continuation=False):
    tick = monotonic()
    route, point, spec, manifest, shared, source = start(amine)
    controls = dict(manifest['fit_controls'], workers=4,
                    maximum_elapsed_time_seconds=maximum_seconds)
    path = RESULTS / f'{amine}-shared-fit.json.gz'
    previous = r.read(path) if continuation else None
    u = manifest['starts']['A']['optimizer']
    if previous:
        assert previous['report']['status'] == 'limit_reached' and previous['replay_passed']
        assert not previous.get('previous_stage', {}).get('previous_stage')
        point = previous['endpoint']
        u = [0.] * len(point['coordinates'])
        spec = route.bind(point)
    spec.spec['optimizer'] = controls
    record = dict(amine=amine, wheel=r.SHA, reference_pressure_pa=P_REF,
                  shared_pairs=shared, shared_source=str(source.relative_to(r.ROOT)),
                  shared_source_sha256=r.s.sha256(source), start=point, optimizer_start=u,
                  controls=controls, row_fingerprint=fingerprint(row_manifest(spec)))
    if previous:
        record['previous_stage'] = previous
    save(path, record)
    _, report, _ = spec.fit(starts=None if previous else [u])
    record.update(report=report, fit_wall_s=monotonic()-tick)
    save(path, record)
    if report['physical'] and report['reactions']:
        endpoint = route.endpoint_mapping(point, report, point['coordinates'])
        assert salt_pairs(endpoint['parameters']) == salt_pairs(point['parameters'])
        bound = route.bind(endpoint)
        result = replay(bound)
        cost = report['data_cost'] if report['data_cost'] is not None else report['final_cost']
        record.update(endpoint=endpoint, endpoint_fingerprint=fingerprint(endpoint), replay=result,
                      replay_passed=(result['cost'] is not None and cost is not None
                                     and a.f.a.relative(result['cost'], cost) <= REPLAY_TOLERANCE[amine]))
        save(path, record)
        record['diagnostics'] = endpoint_diagnostics(bound, result, endpoint, controls)
    record['wall_s'] = monotonic()-tick
    save(path, record)
    print(amine, report['status'], report['message'], report['final_cost'],
          record.get('replay_passed'), record['wall_s'], flush=True)


def assess(amine):
    tick = monotonic()
    fit_record = r.read(RESULTS / f'{amine}-shared-fit.json.gz')
    route, _, _ = configured(amine, 'round-9-shared-interactions')
    spec = route.bind(fit_record['endpoint'])
    fitted = fit_record['replay']['rows']
    if amine == 'MEA':
        legacy = [q for q in fitted if q['group'] == 'common149' and q['unit'] == 'Pa']
        mamun = [q for q in expanded(spec) if membership().get(q['identity'], {}).get('source_key') == 'Mamun2005']
        observations = {'legacy-47': legacy, 'Mamun2005': r.d.evaluate(spec, mamun)}
    else:
        observations = {group: [q for q in fitted if q['group'] == group] for group in ('Kuranov', 'Carson')}
        observations['Ermatchkov'] = [spec.prediction(q) for q in spec.inputs['observations']['comparisons']
                                      if q['group'] == 'Ermatchkov']
    save(RESULTS / f'{amine}-shared-assessment.json.gz', dict(rows=observations, wheel=r.SHA,
         endpoint_fingerprint=fit_record['endpoint_fingerprint'], wall_s=monotonic()-tick))
    print(amine, {k: len(v) for k, v in observations.items()}, monotonic()-tick, flush=True)


if __name__ == '__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    if sys.argv[1] == 'assess':
        assess(sys.argv[2])
    else:
        fit(sys.argv[1], float(sys.argv[2]), continuation='--continue' in sys.argv[3:])
