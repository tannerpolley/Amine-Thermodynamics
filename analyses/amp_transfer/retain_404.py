"""Reduce the #404 run to the same-row evidence retained in the AMP notebook."""
from collections import defaultdict
import csv
import gzip
import hashlib
import json
import math

from part_ii import deviation_statistics
from refit_404 import AMP, DECLARATIONS, FITS, FITS_SHA, PUBLISHED, ROOT, RUN, TRIAL_SHA, Route, record_f0_source, source_values, stable

RETAINED = AMP/'results/retransfer-404-05e94210'
OUT = RETAINED if RUN.name == '404' else RUN.with_name(f'{RUN.name}-retained')
OLD_MAIN = PUBLISHED/'data-rows.json'
OLD_ALTERNATIVE = PUBLISHED/'campaign/start-0/retreated-data-rows.json'
PUBLISHED_COMPARISON = PUBLISHED/'campaign/start-0/retreat-comparison.json'
SCRIPTS = ('launch_404.py', 'refit_404.py', 'stability_404.py', 'classify_descents.py',
           'retain_404.py', 'present_retransfer.py')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, separators=(',', ':'), allow_nan=False)+'\n').encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix=='.gz' else data)


def index(path):
    rows = stable.read(path)
    result = {row['identity']:row for row in rows}
    assert len(result)==len(rows), path
    return result


def compare(label, new_path, old_path):
    new, old = index(new_path), index(old_path)
    assert new.keys()==old.keys() and len(old)==270
    with (AMP/'inputs/retransfer-344/observation-rows.csv').open() as stream:
        source = {r['identity']:r for r in csv.DictReader(stream)}
    assert source.keys()==new.keys()
    groups = defaultdict(list)
    for key, row in new.items():
        before, raw = old[key],source[key]
        assert all(row[k]==before[k] for k in ('observed','unit','role','basis','row','group','T_K','outside_ranges')), key
        assert float(raw['T'])==row['T_K'] and float(raw['observed'])==row['observed'] and raw['role']==row['role']
        row['stock_water_mol_per_mol_AMP'] = float(raw['water']) if raw['water'] else None
        row['loading_mol_CO2_per_mol_AMP'] = float(raw['alpha']) if raw['alpha'] else None
        row['previous_value'], row['previous_status'] = before['value'],before['status']
        row['previous_message'] = before['message'] if before['status']!='Available' else None
        row['delta_prediction'] = row['value']-before['value'] if all(x['status']=='Available' for x in (row,before)) else None
        group = (row['group'],row['role'],row['unit'])
        groups[(*group,'all','all')].append(row)
        for reaction,mark in row['outside_ranges'].items():
            bounds = dict(R1=(273.15,498.15),R2=(273.15,498.15),R3=(273.15,498.15),
                          **{'AMP-dissociation':(293.12,353.22),'carbamate-hydrolysis':(313.15,373.15)})
            lo,hi = bounds[reaction]
            assert mark=='reaction not used' or mark==(not lo<=row['T_K']<=hi), key
            groups[(*group,reaction,str(mark))].append(row)
        if row['unit']=='Pa':
            groups[('all pressures',row['role'],'Pa','all','all')].append(row)
    assert sum(r['role']=='fitted' for r in new.values())==156
    assert sum(r['unit']=='Pa' and r['role']=='not fitted' for r in new.values())==114
    assert sum(r['group']=='tong' and r['T_K']>373.15 for r in new.values())==23
    results = []
    for (group,role,unit,reaction,mark), members in sorted(groups.items()):
        common = [r for r in members if r['delta_prediction'] is not None]
        record = dict(case=label,group=group,role=role,unit=unit,reaction=reaction,range_mark=mark,attempted=len(members))
        for key, subset, field, status in (
            ('new',members,'value','status'),('previous',members,'previous_value','previous_status'),
            ('new_common',common,'value','status'),('previous_common',common,'previous_value','previous_status'),
        ):
            pairs = [(r['observed'],r[field]) for r in subset if r[status]=='Available']
            stats = deviation_statistics(pairs,unit) if pairs else {}
            record.update({f'{key}_{k}': stats.get(k) for k in ('AARD_percent','bias_percent','mean_abs_error','mean_signed_error_predicted_minus_observed')})
            record.update({f'{key}_calculated':len(pairs),f'{key}_relative_defined':sum(o!=0 for o,_ in pairs)})
        for k in ('AARD_percent','bias_percent','mean_abs_error','mean_signed_error_predicted_minus_observed'):
            record[f'delta_{k}'] = record[f'new_common_{k}']-record[f'previous_common_{k}'] if record[f'new_common_{k}'] is not None else None
        results.append(record)
    write(OUT/label/'data-rows.json',list(new.values()))
    return results


def feed_basis(point, rows, declaration):
    run = 'sensitivity' if declaration.endswith('-sensitivity.json') else 'main'
    route = Route(DECLARATIONS/declaration, RUN/run)
    route.check_run_output()
    spec = route.bind(point)
    observations = spec.inputs['observations']['fitted'] + spec.inputs['observations']['comparisons']
    assert len(observations) == len(rows) == 270
    for observation in observations:
        row = rows[observation['identity']]
        feed = spec.problems[observation['problem']].feed
        assert feed.basis.name == 'Amounts' and feed.values['aminomethylpropanol'] == 1.0
        assert feed.values['water'] == row['stock_water_mol_per_mol_AMP']
        assert feed.values.get('carbon-dioxide', 0.) == (row['loading_mol_CO2_per_mol_AMP'] or 0.)
    return dict(rows=len(rows), stock='mol water per mol analytical AMP',
                loading='mol CO2 per mol analytical AMP', mismatches=0)


def group_costs(rows, cost, previous_name):
    old = {(r['group'],r['unit']):r for r in stable.read(PUBLISHED_COMPARISON)['fitted_group_costs']}
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['group'],row['unit']].append(row['cost'])
    assert grouped.keys()==old.keys()
    out = []
    for (group,unit), costs in grouped.items():
        previous = old[group,unit]
        new = math.fsum(costs)
        assert len(costs)==previous['rows']
        out.append(dict(group=group,unit=unit,rows=len(costs),cost=new,
                        previous_cost=previous[previous_name],delta=new-previous[previous_name]))
    assert abs(math.fsum(r['cost'] for r in out)/cost-1)<=1e-8
    return out


def retain_curves(label, path):
    curves = stable.read(path)
    baseline = index(PUBLISHED/'curve-data.json')
    assert len(baseline)==len(curves)==620 and all(
        all(r[k]==baseline[r['identity']][k] for k in ('curve','unit','T_K','loading','outside_ranges')) for r in curves)
    write(OUT/label/'curve-data.json',curves)


def retain_case(label, folder, old_path, source):
    run = RUN/folder
    uncertainty = stable.read(run/'conditional-uncertainty.json')
    active = set(uncertainty['active_bounds'])
    errors = uncertainty['conditional_standard_error']
    selection = stable.read(run/'selection.json')
    fits = stable.read(run/'fits.json')
    compact_fits = []
    for fit in fits:
        i = fit['start']
        histories = []
        stage_paths = sorted((run/f'start-{i}/unpenalized').glob('stage-*/fit.json'))
        for stage in stage_paths:
            report = stable.read(stage)
            fields = ('status','message','iterations','residual_evaluations','jacobian_evaluations','initial_cost',
                      'data_cost','stability_cost','iteration_costs','trial_failures',
                      'endpoint_replay_cost','endpoint_prediction_difference','wall_s','workers')
            histories.append({k:report[k] for k in fields})
        assert all(abs(r['endpoint_replay_cost']/r['data_cost']-1)<=1e-8 for r in histories)
        phases = stable.read(run/f'phase-classification-{i}.json')
        assert len(phases['states'])==fit['search']['grid']['descent']
        compact_fits.append(dict(start=i,cost=fit['cost'],fit_seconds=fit['fit_seconds'],stages=histories,
                                 search=fit['search'],search_seconds=fit['search_seconds'],classification=phases['counts'],
                                 classification_seconds=phases['seconds'],coordinates=fit['endpoint']['coordinates']))
        write(OUT/label/f'phase-classification-{i}.json.gz',phases)
        rows = stable.read(run/f'search-{i}.json')
        write(OUT/label/f'search-{i}.json.gz',[{k:r[k] for k in r if k!='message' or not r['available']} for r in rows])
    selected, = [x for x in fits if x['start']==selection['selected']]
    i = selected['start']
    point = selected['endpoint']
    write(OUT/label/'parameters.json', record_f0_source(point, source))
    write(OUT/label/'conditional-uncertainty.json',uncertainty)
    replay_file = sorted((run/f'start-{i}/unpenalized').glob('stage-*/replay.json'))[-1]
    costs = group_costs(stable.read(replay_file), selected['cost'], 'unpenalized')
    table = []
    for j,q in enumerate(point['coordinates']):
        shift = q.get('kind')=='reaction_enthalpy_shift'
        enthalpy = -5000-q['bounds'][0]
        table.append(dict(identity=q['identity'],value=enthalpy if shift else q['origin'],
                          lower=-5000 if shift else q['bounds'][0],upper=5000 if shift else q['bounds'][1],
                          active_bound=('lower' if q['origin']-q['bounds'][0] < q['bounds'][1]-q['origin'] else 'upper') if j in active else None,
                          conditional_SE=errors.get(q['identity'])))
    write(OUT/label/'fit-summary.json',dict(selection=selection,fits=compact_fits,group_costs=costs,
                                           parameter_table=table))
    retain_curves(label,run/'curve-data.json')
    return compare(label,run/'data-rows.json',old_path)


def main():
    source = source_values()
    statistics = []
    for label, folder in [('main','main'),('sensitivity-3.5','sensitivity')]:
        statistics.extend(retain_case(label, folder, OLD_MAIN, source))
    alternatives = []
    for folder in sorted(RUN.glob('penalty-*')):
        if not (folder/'finding.json').exists():
            continue
        finding = stable.read(folder/'finding.json')
        label = folder.name
        for p in sorted(folder.glob('*.json')):
            if p.name.startswith('phase-'):
                write(OUT/label/(p.name+'.gz'),stable.read(p))
            elif p.name == 'alternative-parameters.json':
                write(OUT/label/p.name, record_f0_source(stable.read(p), source))
            elif p.name == 'alternative-checks.json' and finding.get('alternative', {}).get('accepted'):
                continue  # Write it after validating the search records below.
            elif p.name.startswith(('profile-', 'anchor-', 'alternative-', 'retreat-')) or p.name=='finding.json':
                write(OUT/label/p.name,stable.read(p))
        unavailable = {}
        for path in sorted(folder.glob('search-*.json')):
            failures = [r for r in stable.read(path) if not r['available']]
            if failures:
                unavailable[path.name] = failures
        write(OUT/label/'unavailable-searches.json.gz',unavailable)
        for stage in folder.glob('penalized-*/stage-*/fit.json'):
            report = stable.read(stage)
            fields = ('status','message','iterations','initial_cost','final_cost','data_cost','stability_cost',
                      'residual_evaluations','jacobian_evaluations','endpoint_replay_cost','iteration_costs',
                      'trial_failures','stability_tally','enforced','wall_s','workers')
            write(OUT/label/stage.relative_to(folder),{k:report[k] for k in fields})
        if finding.get('alternative',{}).get('accepted'):
            alternatives.append((finding['alternative']['cost'],label))
            statistics.extend(compare(label,folder/'data-rows.json',OLD_ALTERNATIVE))
            retain_curves(label,folder/'curve-data.json')
            checked = stable.read(folder/'alternative-checks.json')
            checked['penalty_cost'] = 0.0  # Every enforced compressed entry completed with no descent.
            if 'search_record' in checked['compressed']:
                files = {name: checked[name]['search_record'] for name in
                         ('compressed', 'full', 'compressed_recheck', 'full_recheck')}
            else:
                # The completed #404 run predates search-record references in the raw files.
                files = stable.read(RETAINED/label/'alternative-checks.json')['search_records']
            rows = {name:stable.read(folder/file) for name,file in files.items()}
            for name, search in rows.items():
                tally = stable.tally(search)
                assert all(tally[k]==checked[name][k] for k in tally)
                assert len(search)==checked[name]['available'] and not tally['descent']
            bank = stable.read(folder/'split-record.json')
            count = len(bank['trials']) + len(bank['supplied_trials'])
            assert all(sum(checked[name]['supplied_trial_counts'].values()) == checked[name]['states']*count
                       for name in files)
            checked['supplied_trial_bank_count'] = count
            checked['search_records'] = files
            checked['compressed_recheck_reused_retreat_sweep'] = bool(finding.get('retreat')) and (
                int(files['compressed_recheck'].removeprefix('search-').removesuffix('.json')) <
                int(files['compressed'].removeprefix('search-').removesuffix('.json')))
            write(OUT/label/'alternative-checks.json',checked)
            write(OUT/label/'alternative-searches.json.gz',rows)
            if finding.get('retreat'):
                timing = stable.read(folder/'retreat-timing.json')
                timing['bisection_wall_seconds_from_file_times'] = (
                    (folder/'retreat/retreat.json').stat().st_mtime - (folder/'retreat-timing.json').stat().st_mtime)
                write(OUT/label/'retreat-timing.json',timing)

            point = stable.read(folder/'alternative-parameters.json')
            costs = group_costs(stable.read(folder/'alternative-replay.json'),finding['alternative']['cost'],'retreat')
            write(OUT/label/'group-costs.json',costs)
            write(OUT/label/'parameter-table.json',[dict(
                identity=q['identity'],
                value=-5000-q['bounds'][0] if q.get('kind')=='reaction_enthalpy_shift' else q['origin'],
                active_bound=('lower' if q['origin']-q['bounds'][0] < q['bounds'][1]-q['origin'] else 'upper')
                    if min(q['origin']-q['bounds'][0],q['bounds'][1]-q['origin'])<=1e-6*q['scale'] else None,
                conditional_SE=None)
                for q in point['coordinates']])

    write(OUT/'alternatives.json',dict(selected=min(alternatives)[1] if alternatives else None,
                                       eligible=[dict(label=label,cost=cost) for cost,label in alternatives]))
    with (OUT/'same-row-deviations.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(statistics[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(statistics)
    receipts = {name:stable.read(RUN/'inputs'/name) for name in ('identity.json','source.json','replay.json','endpoint-replays.json')}
    assert receipts['source.json']['source_sha256'] == FITS_SHA and receipts['source.json']['coefficients'] == source
    receipts['source.json']['path'] = FITS.relative_to(ROOT).as_posix()
    for label, declaration, parameter_file in (
        ('main', 'AMP-05e94210.json', 'parameters.json'),
        ('sensitivity-3.5', 'AMP-05e94210-sensitivity.json', 'parameters.json'),
        *((label, 'AMP-05e94210.json', 'alternative-parameters.json') for _, label in alternatives),
    ):
        basis = feed_basis(stable.read(OUT/label/parameter_file), index(OUT/label/'data-rows.json'), declaration)
        assert receipts.setdefault('basis-check.json', basis) == basis
    receipts['scripts'] = [(AMP/name).relative_to(ROOT).as_posix() for name in SCRIPTS]
    receipts.update({name:stable.read(RUN/name/'input-checks.json') for name in ('main','sensitivity')})
    receipts['declarations_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        DECLARATIONS/'AMP-05e94210.json', DECLARATIONS/'AMP-05e94210-sensitivity.json', DECLARATIONS/'specification.toml',
    )}
    receipts['engine'] = dict(version='1.3.1',commit='05e94210fa64cf69725e45babc0411d32139df5a',
                              recorded_as_ancestor_of_main=True)
    receipts['coordinate_differences'] = stable.read(RUN/'main/start-coordinate-differences.json')
    logs = RUN.with_name(f'{RUN.name}-launch')
    receipts['resources_at_launch'] = {p:json.loads((logs/p).read_text().splitlines()[0])
                                       for p in ('campaign.log','penalty.log')}
    receipts['run_sizes_bytes'] = {p.name:sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
                                  for p in RUN.iterdir() if p.is_dir()}
    for name in ('main','sensitivity'):
        bank = stable.read(RUN/name/'split-record.json')
        write(OUT/f'{name}-new-witnesses.json.gz',dict(
            initial_trials=7301, initial_sha256=TRIAL_SHA, total_trials=len(bank['trials']),
            added=bank['trials'][7301:], supplied_trials=bank['supplied_trials']))
    write(OUT/'checks.json',receipts)


if __name__=='__main__':
    main()
