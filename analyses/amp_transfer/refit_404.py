"""AMP refit with two fixed carbamate coefficients from the reported MEA F0 fit."""
from collections import Counter
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import time

from part_ii import ROOT, SHA, SHARED_SHA, Route, epcsaft, stable
import reduced_refit_338 as reduced

AMP = ROOT/'analyses/amp_transfer'
DECLARATIONS = AMP/'inputs/retransfer-344/phase-2'
PUBLISHED = AMP/'results/retransfer-344-05e94210'
RUN_NAME = os.environ.get('AMP_404_RUN', '404')
assert Path(RUN_NAME).name == RUN_NAME and RUN_NAME.startswith('404'), RUN_NAME
RUN = AMP/'results/runs'/RUN_NAME
FITS = ROOT/'analyses/mea_parameter_bundle/results/reduced-refit/parameter-details.csv'
FITS_SHA = 'a391a1d04ae64ba7c5a9b57c2e0fd7b08290d1c81a907daa64e5a5d8c5272b0a'
TRIAL_SHA = '24f61da662d6bd0e20eec33e91157af9d80992b1f2a078441341b4fc18bd26fb'


def replay_published(route):
    assert epcsaft.__version__ == '1.3.1'
    receipt = {}
    for label, parameter_file, reference_file, target in [
        ('main', 'campaign/start-0/unpenalized/stage-0/parameters.json', 'data-rows.json', 61.70003837317711),
        ('alternative', 'campaign/start-0/retreated-parameters.json', 'campaign/start-0/retreated-data-rows.json', 124.72679408461333),
    ]:
        point = json.loads((PUBLISHED/parameter_file).read_text())
        reference = {r['identity']:r for r in json.loads((PUBLISHED/reference_file).read_text()) if r['role']=='fitted'}
        started = time.monotonic()
        rows, ok, cost = route.replay(point)
        elapsed = time.monotonic()-started
        assert len(rows) == len(reference) == len({r['identity'] for r in rows}) == 156
        errors = []
        for row in rows:
            previous = reference[row['identity']]
            assert all(row[k]==previous[k] for k in ('observed','unit','basis','row','group'))
            errors.append(abs(row['value']/previous['value']-1) if previous['value'] else abs(row['value']))
        report = dict(rows=len(rows),requested_tolerance_met=ok,cost=cost,reference=target,
                      max_relative_prediction_error=max(errors),relative_cost_error=abs(cost/target-1),seconds=elapsed)
        print(label, report, flush=True)
        assert ok and max(report['max_relative_prediction_error'],report['relative_cost_error']) <= 1e-8
        receipt[label] = report
    route.write('replay.json',dict(points=receipt,wheel_sha256=SHA,shared_values_sha256=SHARED_SHA,installed_wheel_bytes_verified=True))


def source_values():
    assert hashlib.sha256(FITS.read_bytes()).hexdigest() == FITS_SHA, FITS
    with FITS.open() as stream:
        rows = list(csv.DictReader(stream))
    selected = []
    for fit, identity, unit in (
        ('F0', 'component/carbamate-anion/dispersion_energy_over_k', 'kelvin'),
        ('F0', 'pair/carbamate-anion/water/k_ij', 'dimensionless'),
        ('F2', 'component/carbamate-anion/segment_diameter', 'angstrom'),
    ):
        row, = [r for r in rows if r['fit']==fit and r['identity']==identity]
        assert row['unit']==unit
        selected.append(row)
    return selected


def record_f0_source(point, source):
    """Attribute the two fixed magnitudes after checking them against F0."""
    mapping = point['parameters']
    rows = {row['identity']: row for row in source if row['fit'] == 'F0'}
    assert len(rows) == 2
    path = FITS.relative_to(ROOT).as_posix()
    source_id = 'mea-reduced-refit-f0'
    found = set()
    for section in ('components', 'pairs'):
        for block in mapping[section]:
            for coefficient in block['coefficients']:
                identity = coefficient['identity']
                if identity not in rows:
                    continue
                row = rows[identity]
                assert identity not in found
                assert coefficient['value'] == dict(magnitude=float(row['value']), unit=row['unit'])
                coefficient['provenance'] = dict(source_id=source_id, locator=f'{path}:fit=F0:identity={identity}')
                coefficient['source_sha256'] = f'sha256:{FITS_SHA}'
                found.add(identity)
    assert found == rows.keys()
    entry = dict(source_id=source_id, citation='F0 16-parameter MEA calibration',
                 use_basis=f'Fixed AMP carbamate inputs transferred from {path}.')
    registered = [s for s in mapping['sources'] if s['source_id'] == source_id]
    if registered:
        assert registered == [entry]
    else:
        mapping['sources'].append(entry)
    return point


def trial_bank(route):
    bank = route.load(route.config['split_record'])
    with gzip.open(PUBLISHED/'campaign/new-witnesses.json.gz') as stream:
        saved = json.load(stream)
    manifest = stable.read(PUBLISHED/'campaign/start-0/retreat-disposition.json')
    assert len(bank['trials'])==saved['initial'] and not bank['supplied_trials']
    for trial in bank['trials']:
        trial.setdefault('density_side', None)
        trial.setdefault('branch', route.density_branch([trial]))
    bank['trials'] += saved['additional'][:manifest['initial_trial_count']-saved['initial']]
    assert len(bank['trials'])==7301
    assert hashlib.sha256((json.dumps(bank, indent=2)+'\n').encode()).hexdigest()==manifest['initial_trial_file_sha256']==TRIAL_SHA
    return bank


def replace_fixed(point, fixed):
    original = stable.s.parameter_values(point['parameters'])
    updated = stable.s.with_parameter_values(point['parameters'], fixed)
    values = stable.s.parameter_values(updated)
    assert original.keys()==values.keys()
    assert {k for k in values if values[k]!=original[k]}==fixed.keys()
    assert all(values[k]==v for k,v in fixed.items())
    assert stable.s.with_parameter_values(updated, {k:original[k] for k in fixed})==point['parameters']
    return dict(point, parameters=updated)


def check_fixed(point, fixed):
    values = stable.s.parameter_values(point['parameters'])
    assert all(values[k]==v for k,v in fixed.items())


def run_fits(label, declaration, floor, source, reference):
    route = Route(DECLARATIONS/declaration, RUN/label)
    route.check_run_output()
    bank = trial_bank(route)
    fixed = {row['identity']: float(row['value']) for row in source[:2]}
    starts = [record_f0_source(replace_fixed(route.start(ref), fixed), source) for ref in route.config['starts']]
    for point in starts:
        assert len(point['coordinates'])==9
        q, = [q for q in point['coordinates'] if q['identity']=='AMPCOO-segment-diameter']
        assert q['bounds']==[floor,6.5]
        spec = route.bind(point)
        checks = Counter()
        for group in ('fitted','comparisons'):
            for row in spec.inputs['observations'][group]:
                old = reference[row['identity']]
                problem = spec.problems[row['problem']]
                assert (old['role'],old['group'],old['T_K'],old['outside_ranges'])==(
                    row['role'],row['group'],problem.T,route.marks(problem.T,problem))
                assert (row['arguments']['observed'],row['unit'],row['basis'],row['row'])==(
                    old['observed'],old['unit'],old['basis'],old['row'])
                if group=='fitted':
                    pressure = old['unit']=='Pa'
                    scale, count = {'loaded-pressure':(.015,47), 'binary':(.05 if pressure else max(1e-4,.05*old['observed']),52), 'nmr':(.003,57)}[row['group']]
                    assert row['arguments']['form']==('log_ratio' if pressure else 'difference')
                    assert math.isclose(row['weight']/row['arguments'].get('scale',1.)**2,
                                        1/(count*scale**2), rel_tol=1e-14)
                checks[old['group'],old['unit']]+=1
        assert sum(checks.values())==len(reference)==270 and len(route.states(spec))==666
    route.write('input-checks.json',dict(
        fixed=fixed, floor=floor, starts=2, active_coordinates=9, initial_trials=len(bank['trials']),
        initial_trial_sha256=TRIAL_SHA, workers=route.workers,
        rows=[dict(group=k[0],unit=k[1],count=v) for k,v in sorted(checks.items())],
    ))
    fits = []
    for i, point in enumerate(starts):
        name = f'start-{i}/unpenalized'
        started = time.monotonic()
        endpoint, report = reduced.fit(name, point, {}, [], route=route, penalty_rows=[])
        assert endpoint is not None, name
        check_fixed(endpoint, fixed)
        histories = []
        for path in sorted((route.out/name).glob('stage-*/fit.json')):
            step = stable.read(path)
            histories.append({k:step.get(k) for k in (
                'status','message','iterations','residual_evaluations','jacobian_evaluations',
                'initial_cost','final_cost','iteration_costs','trial_failures',
                'data_cost','stability_cost','endpoint_replay_cost','endpoint_prediction_difference','wall_s',
            )})
        fits.append(dict(start=i, cost=report['endpoint_replay_cost'], fit_seconds=time.monotonic()-started,
                         stages=histories, endpoint=endpoint))
        route.write('fits.json', fits)
    converged = [entry for entry in fits if entry['stages'][-1]['status']=='converged']
    selected = min(converged,key=lambda entry:entry['cost'])
    ties = [entry['start'] for entry in converged if abs(entry['cost']/selected['cost']-1)<=route.controls['function_tolerance']]
    route.write('selection.json',dict(selected=selected['start'],ties=ties))
    point = selected['endpoint']
    route.reduce(point)
    route.uncertainty(point)
    route.curves(point)
    if not (route.out/'split-record.json').exists():
        route.write('split-record.json', bank)
    for entry in fits:
        started = time.monotonic()
        searched = route.search(entry['endpoint'])
        entry.update(search=searched,search_seconds=time.monotonic()-started)
        route.write('fits.json', fits)
        print(label, entry['start'], {k:searched['grid'][k] for k in ('states','available','descent')},
              'penalty trigger:', searched['penalty_trigger'], 'seconds:', entry['search_seconds'], flush=True)
    return replay_endpoints(route, label, fixed)


def replay_endpoints(route, case, fixed):
    checks = []
    for path in sorted(route.out.glob('start-*/unpenalized/stage-*/parameters.json')):
        point = stable.read(path)
        check_fixed(point, fixed)
        started = time.monotonic()
        rows, ok, cost = route.replay(point)
        report = stable.read(path.with_name('fit.json'))
        errors = [abs(r['value']/p-1) if p else abs(r['value'])
                  for r, p in zip(rows, report['predictions'], strict=True)]
        relative = abs(cost/report['data_cost']-1) if ok else None
        assert len(rows) == 156 and ok and max(relative, max(errors)) <= 1e-8
        checks.append(dict(case=case, stage=str(path.parent.relative_to(route.out)), rows=len(rows),
                           available=ok, native_cost=report['data_cost'], reloaded_cost=cost,
                           relative_difference=relative, max_relative_prediction_difference=max(errors),
                           seconds=time.monotonic()-started))
    assert len(checks) >= 2
    return checks


def main():
    receipt = Route(DECLARATIONS/'AMP-05e94210.json', RUN/'inputs')
    receipt.check_run_output()
    replay_published(receipt)
    published = stable.read(PUBLISHED/'data-rows.json')
    reference = {r['identity']:r for r in published}
    assert len(published)==len(reference)==270
    source = source_values()
    receipt.write('source.json', dict(coefficients=source, source_sha256=FITS_SHA,
                                      path=FITS.relative_to(ROOT).as_posix()))
    checks = run_fits('main', 'AMP-05e94210.json', float(source[2]['value']), source, reference)
    checks += run_fits('sensitivity', 'AMP-05e94210-sensitivity.json', 3.5, source, reference)
    receipt.write('endpoint-replays.json', checks)


if __name__=='__main__':
    main()
