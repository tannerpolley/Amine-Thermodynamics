"""Compare the retained #435 and #434 records with the #430 reruns."""
import argparse
from collections import Counter
import csv
import gzip
import io
import json
from pathlib import Path


ANALYSES = Path(__file__).resolve().parents[2]
STUDY = 'results/salt-anchored-435'
OBSERVATION = ('status', 'observed', 'value', 'branch', 'requested_tolerance_met',
               'endpoint_loading', 'saturation_loading', 'stable_root_count')
STABILITY = ('available', 'optimized_available', 'supplied_available', 'status',
             'completed', 'event', 'descent', 'no_descent_in_trial_set',
             'parent_kind', 'native_branch', 'supplied_branch',
             'native_liquid_descent', 'liquid_liquid_split', 'supplied_trial_counts',
             'same_calculation_as', 'value', 'pressure_Pa', 'raw_minimum',
             'uncertainty', 'supplied_minimum_tpd', 'supplied_parent_pressure_Pa')
CENSUS = ('classification', 'complete', 'parent_admitted', 'reports_completed',
          'resolved', 'supplied_negative', 'trials', 'unresolved_trials',
          'failed_optimizers', 'minimum_tpd')


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def result(record):
    return record.get('result', record) if isinstance(record, dict) else record


def row_key(row):
    if 'identity' in row:
        return str(row['identity'])
    if 'key' in row or 'index' in row:
        return str(row.get('key', row.get('index')))
    return str((row['salt'], row['T'], row['m']))


class Comparison:
    def __init__(self, writer, name):
        self.writer = writer
        self.name = name
        self.counts = Counter()
        self.max_abs = {}
        self.max_relative = {}
        self.costs = {}
        self.rows = 0

    def field(self, key, field, baseline, candidate, kind='decision'):
        if baseline == candidate:
            return
        self.counts[kind] += 1
        self.writer.writerow((self.name, key, field, kind, json.dumps(baseline), json.dumps(candidate)))
        if isinstance(baseline, (int, float)) and isinstance(candidate, (int, float)) and kind != 'decision':
            absolute = abs(candidate - baseline)
            relative = absolute / abs(baseline) if baseline else None
            for maximum, error in ((self.max_abs, absolute), (self.max_relative, relative)):
                if error is not None and error > maximum.get(field, {}).get('error', -1):
                    maximum[field] = dict(error=error, row=key, study=baseline, candidate=candidate)

    def objective(self, field, baseline, candidate):
        self.field('objective', field, baseline, candidate, 'objective_difference')
        error = None
        if baseline is not None and candidate is not None:
            if baseline:
                error = abs(candidate - baseline) / abs(baseline)
            elif candidate == 0:
                error = 0.
        self.costs[field] = dict(study=baseline, candidate=candidate, relative_error=error,
                                 passed=error is not None and error <= 1e-10)

    def fields(self, key, fields, a, b, numerical=()):
        for field in fields:
            kind = 'numerical_difference' if field in numerical else 'decision'
            self.field(key, field, a.get(field), b.get(field), kind)

    def paired(self, a, b, compare):
        by_key = [{row_key(row): row for row in rows} for rows in (a, b)]
        assert len(by_key[0]) == len(a) and len(by_key[1]) == len(b)
        self.rows += len(by_key[0].keys() & by_key[1].keys())
        for key in dict.fromkeys([*by_key[0], *by_key[1]]):
            x, y = (rows.get(key) for rows in by_key)
            if x is None or y is None:
                self.field(key, 'row_present', x is not None, y is not None)
            else:
                compare(key, x, y)

    def observations(self, a, b):
        self.paired(a, b, lambda key, x, y: self.fields(
            key, OBSERVATION + ('unit', 'basis', 'role'),
            x, y, ('value', 'saturation_loading', 'endpoint_loading')))

    def fit(self, a, b, label='optimizer'):
        for field in ('initial_cost', 'final_cost', 'endpoint_replay_cost'):
            if field in a:
                self.objective(field if label == 'optimizer' else f'{label}/{field}', a[field], b.get(field))
        self.fields(label, ('status', 'on_bound', 'covariance_active_bounds'), a, b)
        bounds = [(x.get('covariance') or {}).get('active_bounds') for x in (a, b)]
        self.field(label, 'active_bounds', *bounds)
        self.field(label, 'trial_failures', a.get('trial_failures'), b.get('trial_failures'))
        self.field(label, 'failed_trials', a.get('failures'), b.get('failures'))
        for field in ('start', 'endpoint'):
            if field in a:
                for name, value in a[field].items():
                    self.field(name, field, value, b.get(field, {}).get(name), 'numerical_difference')

    def search(self, a, b, prefix=''):
        def state(key, x, y):
            key = prefix + key
            self.fields(key, STABILITY, x, y, STABILITY[-6:])
            witnesses = [[(w.get('kind'), w.get('density_side'), w.get('support')) for w in row.get('witnesses', [])]
                         for row in (x, y)]
            self.field(key, 'witness_phase_support', *witnesses)
            for field in ('composition', 'packing'):
                self.field(key, 'witness_' + field, *([w.get(field) for w in row.get('witnesses', [])]
                           for row in (x, y)), 'numerical_difference')
            self.fields(key, ('success', 'pressure', 'rho', 'x'),
                        x.get('parent', {}), y.get('parent', {}), ('pressure', 'rho', 'x'))
            self.trials(key, x.get('optimized_trials', []), y.get('optimized_trials', []))
        self.paired(a, b, state)

    def trials(self, key, a, b):
        self.field(key, 'optimized_trial_count', len(a), len(b))
        def indexed(rows):
            counts = Counter()
            output = {}
            for row in rows:
                signature = (row.get('phase', {}).get('name'), row.get('seed'))
                counts[signature] += 1
                output[(*signature, counts[signature])] = row
            return output
        aa, bb = indexed(a), indexed(b)
        for name in dict.fromkeys([*aa, *bb]):
            trial = f'{key}/{name}'
            x, y = aa.get(name), bb.get(name)
            if x is None or y is None:
                self.field(trial, 'optimized_trial', x, y)
                continue
            self.fields(trial, ('seed', 'evidence', 'resolved_descent', 'optimizer_success',
                                'phase', 'composition'), x, y, ('composition',))
            self.fields(trial, ('success',), x.get('optimizer', {}), y.get('optimizer', {}))
            self.fields(trial, ('tpd_over_rt', 'raw_objective_over_rt'),
                        x.get('quantities', {}), y.get('quantities', {}),
                        ('tpd_over_rt', 'raw_objective_over_rt'))

    def census_detail(self, a, b):
        def state(key, x, y):
            self.fields(key, ('temperature_K', 'loading', 'classification', 'bubble_pressure_Pa',
                              'pressure_Pa', 'pressure_uncertainty_Pa'), x, y,
                        ('bubble_pressure_Pa', 'pressure_Pa', 'pressure_uncertainty_Pa'))
            for stage in ('bubble', 'liquid', 'final'):
                p, q = x.get(stage, {}), y.get(stage, {})
                phase_key = f'{key}/{stage}'
                self.fields(phase_key, ('requested_tolerance_met', 'amounts',
                                              'mole_fractions', 'molar_densities'),
                            p, q, ('amounts', 'mole_fractions', 'molar_densities'))
                self.field(phase_key, 'phases', *([tuple(v.get(field) for field in
                          ('identity', 'role', 'support', 'mechanical_class')) for v in stage.get('phases', [])]
                           for stage in (p, q)))
            aa, bb = (row.get('stability', []) for row in (x, y))
            self.field(key, 'stability_report_count', len(aa), len(bb))
            for i, (p, q) in enumerate(zip(aa, bb)):
                report = f'{key}/report-{i}'
                self.fields(report, ('completed', 'supplied_counts', 'supplied_minimum_tpd'),
                            p, q, ('supplied_minimum_tpd',))
                self.trials(report, p['trials'], q['trials'])
        self.paired(a, b, state)

    def summary(self):
        return dict(status='different' if self.counts else 'equal',
                    rows_compared=self.rows, differences=dict(self.counts), objectives=self.costs,
                    largest_absolute_changes=self.max_abs, largest_relative_changes=self.max_relative)


def comparisons(candidate, writer):
    summaries = {}

    def compare(study_path, candidate_path, method, extract=result):
        name = study_path.relative_to(ANALYSES).as_posix()
        if not candidate_path.exists():
            summaries[name] = dict(status='missing candidate record')
            return
        record = Comparison(writer, name)
        method(record, *(extract(load(p)) for p in (study_path, candidate_path)))
        summaries[name] = record.summary()

    owner = 'mea_parameter_bundle'
    baseline = ANALYSES / owner / STUDY
    new = candidate / owner
    for name in ('1a-sodium', '1b-bicarbonate', '1c-carbonate'):
        def salt(compare, a, b):
            compare.fit(a, b)
            compare.observations(a['rows'], b['rows'])
        path = f'salt/{name}.json'
        compare(baseline / path, new / path, salt)

    def salt_replay(compare, a, b):
        for group in a['rows']:
            compare.observations(a['rows'][group], b['rows'][group])
        for ion, law in a['laws_at_record_reference'].items():
            compare.fields(ion, ('a0', 'a1', 't_ref'), law, b['laws_at_record_reference'][ion], ('a0', 'a1'))

    compare(baseline / 'salt/summary.json', new / 'salt/summary.json', salt_replay)

    def salt_control(c, a, b):
        for label in ('old_rows', 'f2_rows'):
            for group in a[label]:
                c.observations(a[label][group], b[label][group])

    compare(baseline / 'salt/control.json', new / 'salt/control.json', salt_control)

    def replay(compare, a, b):
        compare.objective('cost', a['cost'], b['cost'])
        compare.observations(a['rows'], b['rows'])

    for start in ('F2-control', 'F2', 'F4'):
        path = f'MEA/{start}/replay.json'
        compare(baseline / path, new / path, replay)
        if start == 'F2-control':
            continue
        for name, method in (
            ('stage-0/fit.json', Comparison.fit),
            ('search/grid.json.gz', Comparison.search),
            ('search/census-raw.json.gz', Comparison.census_detail),
            ('search/census.json', lambda c, a, b: c.paired(a['rows'], b['rows'], lambda k, x, y:
                c.fields(k, CENSUS, x, y, ('minimum_tpd',)))),
        ):
            path = f'MEA/{start}/{name}'
            compare(baseline / path, new / path, method)

    def selection(c, a, b):
        aa, bb = (row.get('chosen') or row for row in (a, b))
        c.objective('cost', aa.get('cost'), bb.get('cost'))
        c.fields('selected', ('name', 'label', 'start', 'stable', 'optimizer_converged',
                              'tied_starts'), aa, bb)
        c.field('selected', 'ties', a.get('ties'), b.get('ties'))

    compare(baseline / 'MEA/selection.json', new / 'MEA/selection.json', selection)

    def search_outcome(c, a, b):
        for field in ('confirmed', 'bubble_refusals'):
            old, new = (set(row.get(field, [])) for row in (a, b))
            for key in sorted(old ^ new):
                c.field(key, field, key in old, key in new)

        def classify(key, x, y):
            c.fields(key, ('native_branch', 'supplied_branch', 'liquid_directed',
                           'pressure_Pa'), x, y, ('pressure_Pa',))
            for i, (p, q) in enumerate(zip(x['attempts'], y['attempts'])):
                c.fields(f'{key}/coexistence-{i}',
                         ('confirmed', 'distinct', 'split_only', 'requested_tolerance_met',
                          'Gibbs_decrease_over_RT_mol', 'phases', 'densities_mol_m3'),
                         p, q, ('Gibbs_decrease_over_RT_mol', 'phases', 'densities_mol_m3'))
            c.field(key, 'coexistence_attempts', len(x['attempts']), len(y['attempts']))
        c.paired(a.get('classifications', []), b.get('classifications', []), classify)

    def fixed(c, a, b, case='fixed pressure'):
        c.fields(case, ('outcome', 'physical_checks_pass', 'instability',
                                    'realized_Pa', 'P_Pa'), a, b, ('P_Pa', 'realized_Pa'))
        c.field(case, 'status', a.get('status'), b.get('status'), 'diagnostic_difference')
        aa, bb = a.get('attempts', []), b.get('attempts', [])
        c.field(case, 'attempt_count', len(aa), len(bb))
        for i, (x, y) in enumerate(zip(aa, bb)):
            c.fields(f'{case}/attempt-{i}', ('confirmed', 'distinct', 'split_only',
                     'requested_tolerance_met', 'Gibbs_decrease_over_RT_mol', 'amounts_mol',
                     'densities_mol_m3', 'phases'), x, y,
                     ('Gibbs_decrease_over_RT_mol', 'amounts_mol', 'densities_mol_m3', 'phases'))

    def amp_pressure(c, a, b):
        c.field('common pressure', 'common_Pa', a['common_Pa'], b['common_Pa'], 'numerical_difference')
        for name in a['outcomes']:
            c.fields(name, ('status', 'pressure_Pa'), a['bubbles'][name], b['bubbles'][name], ('pressure_Pa',))
            fixed(c, a['outcomes'][name], b['outcomes'][name], name)

    def dea_refusals(c, a, b):
        for case in ('salt', 'prior'):
            c.search(a[case], b[case], case + '/')

    compare(ANALYSES / 'amp_transfer' / STUDY / 'common-pressure.json',
            candidate / 'amp_transfer/A/common-pressure.json.gz', amp_pressure)
    compare(ANALYSES / 'dea_transfer' / STUDY / 'campaign/refusal-replay.json',
            candidate / 'dea_transfer/campaign/refusal-replay.json', dea_refusals)
    for owner in ('dea_transfer', 'mdea_mea_workflow', 'amp_transfer'):
        baseline = ANALYSES / owner / STUDY
        for study_path in sorted(baseline.rglob('*.json.gz')):
            rel = study_path.relative_to(baseline)
            name = rel.stem
            method = {
                'fit.json': Comparison.fit,
                'replay.json': Comparison.observations,
                'start-replay.json': replay,
                'data-rows.json': Comparison.observations,
                'search-0.json': Comparison.search,
                'search-1.json': Comparison.search,
                'search-outcome.json': search_outcome,
                'selection.json': selection,
                'fixed-pressure.json': fixed,
            }.get(name)
            if method:
                compare(study_path, candidate / owner / rel.with_suffix(''), method)

    def normalized(c, a, b):
        if not a['report'] or not b['report']:
            c.field('optimizer', 'report_present', bool(a['report']), bool(b['report']))
            return
        c.fit(a['report'], b['report'])
        for key in a['records']:
            if key in a['records'] and key in b['records']:
                x, y = (d['records'][key] for d in (a, b))
                if key.startswith('start'):
                    replay(c, x, y)
                elif key.endswith('/replay.json'):
                    c.observations(x, y)
                elif key.endswith('/fit.json'):
                    c.fit(x, y, key.removesuffix('/fit.json'))
            else:
                c.field(key, 'record_present', key in a['records'], key in b['records'])

    path = 'C/normalized-MDEA-1.json.gz'
    compare(ANALYSES / 'round_5/results' / path, candidate / 'normalized' / path, normalized)
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / 'differences.csv.gz').open('wb') as compressed:
        with gzip.GzipFile(filename='', mode='wb', mtime=0, fileobj=compressed) as data, \
                io.TextIOWrapper(data, encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(('study_record', 'row_or_state', 'field', 'kind', 'study', 'candidate'))
            summaries = comparisons(args.candidate, writer)
    (args.output / 'comparison.json.gz').write_bytes(
        gzip.compress((json.dumps(summaries, indent=2, allow_nan=False) + '\n').encode(), mtime=0))


if __name__ == '__main__':
    main()
