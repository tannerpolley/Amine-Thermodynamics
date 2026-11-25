"""Render the #435 manuscript handoff using retained records only."""
import argparse
from collections import Counter
import csv
from functools import cache
import gzip
import json
from math import exp, fsum, log, sqrt
from operator import itemgetter
from os.path import relpath
from pathlib import Path
from statistics import fmean
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = 'analyses/mea_parameter_bundle/results/'
PAPER = BUNDLE + 'paper-evidence-341/'
F2 = BUNDLE + 'reduced-refit/evidence/F2/'
READBACK = BUNDLE + 'salt-anchored-435/'
MEA = READBACK + 'MEA/F4/'
EVIDENCE = READBACK + 'MEA/evidence/F4/'
DEA = 'analyses/dea_transfer/results/refit-413/'
MDEA = 'analyses/mdea_mea_workflow/results/bounded-binary-411/'
AMP = 'analyses/amp_transfer/results/retransfer-412-f2-05e94210/'
HONG = BUNDLE + 'same-data-comparison/hong-2027/'
OBJECTIVE = BUNDLE + 'objective-weights-420/'
REFERENCE = BUNDLE + 'reference-states-428/'
PHASE = MDEA.replace('bounded-binary-411', 'phase-search-421')
BANDS = BUNDLE + 'stripper-temperature-409/'
CURRENT = {'MEA': MEA, 'DEA': DEA.replace('refit-413', 'salt-anchored-435/campaign'),
           'MDEA': MDEA.replace('bounded-binary-411', 'salt-anchored-435/campaign'),
           'AMP': AMP.replace('retransfer-412-f2-05e94210', 'salt-anchored-435/free'),
           'AMP fixed': AMP.replace('retransfer-412-f2-05e94210', 'salt-anchored-435/fixed')}
ROUND3 = 'analyses/round_3/results/'
ROUND5 = 'analyses/round_5/results/A/'
OUT = ROOT / READBACK / 'manuscript-handoff.md'
PREVIOUS = {'MEA': READBACK + 'MEA/F2-control/replay.json',
            'DEA': DEA + 'selection.json', 'MDEA': MDEA + 'endpoint.json',
            'AMP': ROUND5 + 'expanded-free.json.gz', 'AMP fixed': ROUND5 + 'expanded-fixed.json.gz'}
INFO = 'information.json.gz'
LABEL = {'AMP': 'AMP expanded free', 'AMP fixed': 'AMP expanded −150 K sensitivity'}


@cache
def read(path):
    path = ROOT / path
    content = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    if path.name.removesuffix('.gz').endswith('.csv'):
        return list(csv.DictReader(content.decode().splitlines()))
    return json.loads(content)


def value_at(path, keys):
    item = read(path)
    for key in keys:
        item = item[key]
    return item


def cell(value, path, field, n='1 state', fmt='.6g'):
    if isinstance(value, (tuple, list)):
        printed = ' / '.join(display(v, fmt) for v in value)
    else:
        printed = display(value, fmt)
    source = quote(relpath(ROOT / path, OUT.parent))
    return f'{printed} · {n} · [{Path(path).name}]({source}) `{field}`'


def display(value, fmt):
    if value is None:
        return 'Unavailable'
    if isinstance(value, float):
        return f'{value!r} ({value:{fmt}})'
    return str(value).replace('|', '&#124;').replace('\n', ' ')


def record(path, keys, fields, n='1 state', fmt='.6g'):
    item = value_at(path, keys)
    selector = ''.join(f'[{k!r}]' for k in keys)
    return cell(tuple(item[k] for k in fields), path, selector + '.' + '/'.join(fields), n, fmt)


def rates(rows, pred='predicted', obs='observed', status='Available'):
    present = [(float(r[pred]), float(r[obs])) for r in rows if r['status'] == status and r[pred] not in (None, '')]
    errors = [100 * (p - o) / o for p, o in present if o]
    return (fmean(map(abs, errors)), fmean(errors), len(errors), len(present)) if errors else (None, None, 0, len(present))


def salt_rows():
    summary = READBACK + 'salt/summary.json'
    baseline = BUNDLE + 'selected-current-best-parameters.json'
    control = READBACK + 'salt/control.json'
    for ion, group in (('sodium-cation', 'NaCl'), ('bicarbonate-anion', 'NaHCO3'), ('carbonate-anion', 'Na2CO3')):
        keys = ('result', 'laws', ion)
        matches = [(i, pair['coefficients'][0]['value']['magnitude']) for i, pair in enumerate(read(baseline)['pairs'])
                   if {pair['component_id_a'], pair['component_id_b']} == {ion, 'water'}]
        old = cell(matches[0][1], baseline, f'pairs[{matches[0][0]}].coefficients[0].value.magnitude', 'constant k') if matches else 'Sodium absent from amine declaration'
        n = value_at(summary, ('result', 'scores', group))['n']
        bounds = value_at(summary, ('result', 'on_bound'))
        bound = next(((i, b['value']) for i, b in enumerate(bounds) if f'/{ion}/' in b['coefficient']), None)
        yield f'Water–{ion} law (intercept / slope / reference T)', '1 / K⁻¹ / K', record(summary, keys, ('a0', 'a1', 't_ref'), n), old
        yield f'Water–{ion} intercept active lower bound', '1', (record(summary, ('result', 'on_bound', bound[0]), ('value',), n)
            if bound else cell('Interior', summary, f'result.on_bound: {ion} absent', n)), 'See constant k above'
        yield f'Water–{ion} k at 313.15 K', '1', record(summary, ('result', 'values_313_15'), (ion,), n), old
        stage = READBACK + 'salt/' + {'NaCl': '1a-sodium', 'NaHCO3': '1b-bicarbonate', 'Na2CO3': '1c-carbonate'}[group] + '.json'
        yield f'{group} calibration objective (start / endpoint)', '1', record(stage, ('result',), ('initial_cost', 'final_cost'), n), 'Historical salt laws were replayed in this control'
    for group, score in value_at(summary, ('result', 'scores')).items():
        old = [r for r in value_at(control, ('f2_rows', group)) if r.get('status') == 'Available']
        n = len(value_at(summary, ('result', 'rows', group)))
        yield f'{group} osmotic coefficient AARD', '%', cell(score['aard_percent'], summary, f'result.scores.{group}.aard_percent', f"{score['n']}/{n}"), (
            cell(100 * fmean(abs(r['relative_error']) for r in old), control, f'f2_rows.{group}: mean |relative_error| × 100', f'{len(old)}/{n}')
            if old else cell('Unavailable: carbonate-salt control could not prepare mixed feeds', control, 'f2_rows.mixed', f'0/{n}'))


def audits(case):
    name = case.split()[0]
    current = CURRENT[case] + ('objective-' if name == 'MEA' else f'{name}/') + INFO
    older = OBJECTIVE + name + '/' + INFO
    return current, older


@cache
def prior_amp_information(case):
    import numpy as np

    prior = read(PREVIOUS[case])
    path = PREVIOUS[case].replace('.json.gz', f"-{prior['start']}.json.gz")
    data = read(path)
    assert data['point'] == prior['point']
    fit = data['report']
    covariance = fit['covariance']
    coords = prior['point']['coordinates']
    interior = [i for i in range(len(coords)) if i not in covariance['active_bounds']]
    # The stored optimizer-coordinate right singular vectors are columns.
    v = np.asarray(covariance['right_vectors']).reshape(len(coords), -1)[interior]
    matrix = v * covariance['singular_values']
    rank = int(np.linalg.matrix_rank(matrix))
    assert rank == len(interior)
    n = len(fit['weighted_residuals'])
    rss = fsum(r*r for r in fit['weighted_residuals'])
    assert abs(rss/2 - prior['cost']) < 1e-9
    dof = n-rank
    variance = rss/dof
    errors = {i: float(se)*coords[i]['scale'] for i, se in zip(
        interior, np.sqrt(variance*np.diag(np.linalg.inv(matrix @ matrix.T))), strict=True)}
    return path, (rss, n, rank, dof, variance), covariance['active_bounds'], errors


def objectives():
    for case, base in CURRENT.items():
        name = case.split()[0]
        label = LABEL.get(case, case)
        new, old = audits(case)
        a = read(new)['result']
        prior = PREVIOUS[case]
        fit = base + ('fit-summary.json' if case == 'MEA' else 'selection.json.gz')
        fit_key = ('chosen',) if case == 'DEA' else ()
        cost = value_at(fit, fit_key)['cost']
        n = a['n']
        if name == 'MDEA':
            prior_cost = record(MDEA+'summary-row.json', (), ('data_cost',), n, '.2f')
        else:
            prior_cost = record(prior, fit_key, ('cost',), n, '.2f')
        yield f'{label} objective', '1', record(fit, fit_key, ('cost',), n, '.2f'), prior_cost
        fields = ('rss', 'stage_rss', 'n', 'na', 'p', 'denominator', 'stage_denominator', 'variance', 'stage_variance')
        if name == 'AMP':
            reference, (rss, count, rank, dof, variance), _, _ = prior_amp_information(case)
            prev = cell((rss, rss, count, count, rank, dof, dof, variance, variance), reference,
                        'report.weighted_residuals; interior rank from report.covariance (see #420)', dof)
        else:
            prev = record(old, ('result',), fields, read(old)['result']['stage_denominator'])
        yield f'{label} RSS / responsive RSS / N / responsive N / interior rank / all df / stage df / all variance / stage variance', '1 / counts / 1', record(new, ('result',), fields, a['stage_denominator']), prev

        contrib = base + ('objective-contributions.csv' if case == 'MEA' else f'{name}/contributions.csv.gz')
        prior_csv = OBJECTIVE + name + '/contributions.csv'
        older = {(r['group'], r['source'], r['observable']): (i, r) for i, r in enumerate(read(prior_csv))} if name != 'AMP' else {}
        for i, r in enumerate(read(contrib)):
            key = (r['group'], r['source'], r['observable'])
            count = int(r['n'])
            if name == 'AMP':
                cohort = [e for e in read(prior)['expanded']['rows']
                          if e['role'] == 'fitted' and e['group'] == r['group'] and e['unit'] in r['unit']]
                assert len(cohort) == count
                c = 0.5 * fsum(e['weight'] * e['prediction']['residual'] ** 2 for e in cohort)
                previous = cell((c, 100*c/read(prior)['cost']), prior,
                                f'expanded.rows (fitted, {r["group"]}, {cohort[0]["unit"]}): ½Σ(weight × prediction.residual²), 100 × contribution/cost', count)
            else:
                j, s = older[key]
                assert s['n'] == r['n']
                previous = cell((float(s['cost']), float(s['percent'])), prior_csv, f'[{j}].cost/percent', count)
            yield f'{label} contribution · {" · ".join(key)}', '1 / %', cell((float(r['cost']), float(r['percent'])), contrib, f'[{i}].cost/percent', count), previous
        assert abs(fsum(float(r['cost']) for r in read(contrib)) - cost) < 1e-9


def parameter_cells(case, current):
    name = case.split()[0]
    new, old = audits(case)
    path = new if current else old
    audit = read(path)['result']
    base = CURRENT[case]
    if name == 'MEA':
        error = base + 'uncertainty/standard-errors.csv' if current else OBJECTIVE + 'MEA/standard-errors.csv'
        errors = {r['parameter']: (i, float(r['adopted_point_SE_bound_fixed'])) for i, r in enumerate(read(error))}
        coord_file, keys, field = path, ('result', 'coordinates'), 'value'
        error_field = 'adopted_point_SE_bound_fixed'
    elif name == 'AMP' and not current:
        coord_file, keys, field = PREVIOUS[case], ('point', 'coordinates'), 'origin'
        error, (_, _, _, dof, _), prior_bounds, prior_errors = prior_amp_information(case)
        errors = {coords['identity']: (i, prior_errors[i]) for i, coords in enumerate(value_at(coord_file, keys))
                  if i in prior_errors}
        error_field = 'report.covariance, report.weighted_residuals'
    else:
        coord_file = (base + 'conditional-uncertainty.json.gz' if current else PREVIOUS[case].rsplit('/', 1)[0] + '/conditional-uncertainty.json')
        keys, field = ('coordinates',), 'origin'
        error, error_field = coord_file, 'conditional_standard_error'
        errors = {k: (k, v) for k, v in read(error)[error_field].items()}
    for i, p in enumerate(value_at(coord_file, keys)):
        key, fit = p['identity'], p[field]
        lo, hi = p['bounds']
        if name == 'AMP' and not current:
            active = i in prior_bounds
        else:
            active = i in audit['active_bounds']
        bound = f'lower {lo!r}' if active and abs(fit-lo) < abs(fit-hi) else f'upper {hi!r}' if active else 'Interior'
        unit = p.get('unit') or ('K⁻¹' if '/a1 /' in key else 'K' if 'slope' in key or 'energy_over_k' in key else
                                  'Å' if 'diameter' in key else 'J/mol' if 'enthalpy' in key else '1')
        denominator = dof if name == 'AMP' and not current else audit['stage_denominator']
        selector = ''.join(f'[{k!r}]' for k in (*keys, i))
        text = cell((fit, bound), coord_file, f'{selector}.{field}/bounds', denominator)
        if key in errors:
            j, se = errors[key]
            if name == 'AMP' and not current:
                text += '<br>' + cell(se, error, f'{error_field}: conditional physical SE for coordinate {j}', denominator)
            else:
                text += '<br>' + cell(se * audit['SE_multiplier'], error, f'{error_field}[{j!r}] × result.SE_multiplier ({Path(path).name})', denominator)
        else:
            text += '<br>' + ('SE withheld at active bound' if active else 'SE unavailable')
        yield key, unit, text


def parameters():
    for case in CURRENT:
        old = {key: (unit, text) for key, unit, text in parameter_cells(case, False)}
        cur = {key: (unit, text) for key, unit, text in parameter_cells(case, True)}
        for key in dict.fromkeys((*cur, *old)):
            unit = (cur.get(key) or old[key])[0]
            yield f'{LABEL.get(case, case)} · {key} (estimate / active bound; stage SE)', unit, cur.get(key, ('', 'Fixed by the salt laws above'))[1], old.get(key, ('', 'Coordinate held at zero in the 0.765 fit'))[1]
        if case.startswith('AMP'):
            yield f'{LABEL[case]} · protonated AMP–water reciprocal slope', 'K', record(CURRENT[case]+'selection.json.gz', (), ('slope_K',), 214), record(PREVIOUS[case], (), ('slope_K',), 214)


def deviations():
    fields = ('AARD_percent', 'bias_percent', 'relative_rows', 'rows')
    for case, base in CURRENT.items():
        if case == 'MEA':
            continue
        path = base.rsplit('/', 2)[0] + '/matched-deviations-' + base.split('/')[-2] + '.json'
        for i, r in enumerate(read(path)['groups']):
            label = ' · '.join((LABEL.get(case, case), r['group'], r['role'], r['observable'], r['unit']))
            yield label, '% / % / counts', record(path, ('groups', i, 'new'), fields, r['count'], '.2f'), record(path, ('groups', i, 'prior'), fields, r['count'], '.2f')
            if r['new']['relative_rows'] != r['prior']['relative_rows'] or r['unavailable_new'] or r['unavailable_prior']:
                yield label + ' · matched available pairs', '% / % / counts', record(path, ('groups', i, 'matched_new'), fields, r['count'], '.2f'), record(path, ('groups', i, 'matched_prior'), fields, r['count'], '.2f')
    species = {"['monoethanolamine', 'protonated-monoethanolamine']": 'MEA + MEAH+',
               "['monoethanolamine']": 'MEA', "['protonated-monoethanolamine']": 'MEAH+',
               "['carbamate-anion']": 'MEACOO-',
               "['bicarbonate-anion', 'carbonate-anion']": 'HCO3- + CO3^2-'}
    for r in read(MEA+'objective-contributions.csv'):
        key = (r['group'], r['source'], r['observable'])
        n = int(r['n'])
        cells = []
        for path in audits('MEA'):
            rows = [row for row in read(path)['result']['rows'] if (row['group'], row['source']) == key[:2]]
            if len(rows) != n:
                quantity = key[2]
                if quantity in species:
                    suffix = species[quantity]
                    if key[1] == 'Bottinger2008' and suffix == 'HCO3- + CO3^2-':
                        suffix = 'HCO3-'
                    rows = [row for row in rows if row['identity'].endswith('::'+suffix)]
                else:
                    observable = 'mole_fraction' if quantity == "['water']" else quantity
                    rows = [row for row in rows if row['observable'] == observable]
            assert len(rows) == n, key
            cells.append(cell(rates(rows, 'value'), path, f'result.rows: {key}; value/observed/status', n, '.2f'))
        yield 'MEA fitted · ' + ' · '.join(key), '% / % / counts', *cells
    fit_ids = {r['id'] for r in read(EVIDENCE+'fitted-rows.csv')}
    yield from mea_pressure_sets(fit_ids)
    for filename, role in (('canonical-pressure.csv', 'pressure'), ('wagner-pressure.csv', 'pressure'),
                           ('transfer.csv', 'pressure'), ('species-figure-data.csv', 'species'),
                           ('pool-figure-data.csv', 'species')):
        groups = set()
        for r in read(EVIDENCE+filename):
            groups.add((r['source'], 'fitted' if r['target'] in fit_ids else 'outside fit', r.get('species', role)))
        for source, use, observable in sorted(groups):
            cells = []
            for base in (EVIDENCE, F2):
                cohort = {r['target']: r for r in read(base+filename) if r['source'] == source
                          and (r['target'] in fit_ids) == (use == 'fitted') and r.get('species', role) == observable}
                cells.append(cell(rates(cohort.values()), base+filename, f'{source}/{use}/{observable}: distinct target, predicted/observed/status', len(cohort), '.2f'))
            yield f'MEA · {filename.removesuffix(".csv")} · {source} · {use} · {observable}', '% / % / counts', *cells


def mea_pressure_sets(fitted):
    cohorts = {'six sources, all': ('canonical-pressure.csv',),
               'six sources, outside fit': ('canonical-pressure.csv',),
               'all outside fit': ('canonical-pressure.csv', 'wagner-pressure.csv', 'transfer.csv')}
    for label, names in cohorts.items():
        cells = []
        for base in (EVIDENCE, F2):
            rows = [r for name in names for r in read(base+name)
                    if label == 'six sources, all' or r['target'] not in fitted]
            cells.append(cell(rates(rows), base+names[0], f'{", ".join(names)}: {label}, predicted/observed/status', len(rows), '.2f'))
        yield f'MEA partial pressure · {label}', '% / % / counts', *cells
    canonical = 'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv'
    fraction = {r['observation_id']: float(r['MEA_weight_fraction']) for r in read(canonical) if r['MEA_weight_fraction']}
    for content in (15, 45):
        cells = []
        for base in (EVIDENCE, F2):
            path = base+'transfer.csv'
            rows = [r for r in read(path) if fraction[r['target'].removesuffix('-pco2')] == content/100]
            cells.append(cell(rates(rows), path, f'{content} wt% by canonical target; predicted/observed/status', len(rows), '.2f'))
        yield f'MEA Aronu {content} wt% outside-fit partial pressure', '% / % / counts', *cells


def search_cell(path, keys, confirmed=()):
    q = value_at(path, keys)
    n = q['states']
    available = q.get('available', n - q.get('incomplete', 0))
    return cell((available, n, q['descent'], len(confirmed), n-available),
                path, f'{keys!r}: available/states/descent/refused; confirmation records', f'{n} state records')


def searches():
    label = 'available / attempted / descents / confirmed LL / incomplete'
    older = BUNDLE + 'wheel-recheck-05e94210/stability-adopted-law/search.json'
    for model in ('F2', 'F4'):
        path = READBACK + f'MEA/{model}/search-summary.json'
        for group in ('grid', 'offset', 'census'):
            yield f'MEA {model} {group} · {label}', 'states', search_cell(path, (group,)), search_cell(older, (group,))
        yield f'MEA {model} supplied trials evaluated', 'trials', record(path, ('supplied',), ('evaluated',), '162 census states'), record(older, ('supplied',), ('evaluated',), '162 census states')

    new = CURRENT['DEA'] + 'selection.json.gz'
    old = PREVIOUS['DEA']
    keys = ('chosen', 'search', 'grid')
    yield f'DEA grid · {label}', 'states', search_cell(new, keys), search_cell(old, keys)
    refusals = [{r['key']: i for i, r in enumerate(value_at(p, keys)['unavailable_searches'])} for p in (new, old)]
    for key in dict.fromkeys((*refusals[0], *refusals[1])):
        yield f'DEA search refusal · {key}', '1', *(
            record(path, (*keys, 'unavailable_searches', indices[key]), ('cause',)) if key in indices else
            cell('Available', path, 'chosen.search.grid.unavailable: key absent')
            for path, indices in zip((new, old), refusals, strict=True))
    route = 'analyses/dea_transfer/inputs/part-ii-346/f2-carbamate-413-route.json'
    tolerance = value_at(route, ('optimizer', 'function_tolerance'))
    yield 'DEA objective tie tolerance (absolute)', '1', record(route, ('optimizer',), ('function_tolerance',), '2 starts'), record(route, ('optimizer',), ('function_tolerance',), '2 starts')
    for path in (new, old):
        d = read(path)
        minimum = min(c['cost'] for c in d['candidates'])
        assert d['chosen']['cost'] == minimum
        assert d['ties'] == [c['name'] for c in d['candidates'] if abs(c['cost']-minimum) <= tolerance]
    for i in range(len(read(new)['candidates'])):
        yield f'DEA candidate {i} · name / objective', '1', record(new, ('candidates', i), ('name', 'cost'), 80), record(old, ('candidates', i), ('name', 'cost'), 80)

    new = CURRENT['MDEA'] + 'search-outcome.json.gz'
    old = PHASE + 'coverage.json'
    before = read(old)
    confirmed = read(new)['confirmed']
    yield f'MDEA full search · {label}', 'states', search_cell(new, ('tally',), confirmed), cell(
        (sum(r['complete'] for r in before), len(before), sum(r['descent'] for r in before), 'see fixed-pressure and measured-state records below',
         sum(not r['complete'] for r in before)), old, 'rows: complete/descent', len(before))
    raw = CURRENT['MDEA'] + 'search-0.json.gz'
    bubble_refusals = set(read(new)['bubble_refusals'])
    causes = Counter()
    for r in read(raw):
        if r['available']:
            continue
        cause = ('bubble reference' if r['key'] in bubble_refusals else
                 'preparation failed' if r['status'] == 'Exception' else
                 'supplied incomplete' if r['status'] == 'Available' else
                 'optimized unavailable: ' + (r['event'] or 'see cause in search row'))
        causes[cause] += 1
    assert sum(causes.values()) == len(read(new)['tally']['unavailable'])
    for cause in ('bubble reference', 'preparation failed', 'supplied incomplete', 'optimized unavailable'):
        count = sum(n for key, n in causes.items() if key.startswith(cause))
        yield f'MDEA incomplete · {cause}', 'states', cell(count, raw, f'unavailable rows: {cause} from key/status/event', len(before)), cell(
            sum(not r['complete'] and r['stage'] == cause for r in before), old, f'rows: complete=false, stage={cause}', len(before))
    for cause, count in sorted(causes.items()):
        if cause.startswith('optimized unavailable'):
            yield f'MDEA {cause}', 'states', cell(count, raw, 'unavailable rows: key/status/event/cause/message', len(before)), '0.765 cause counts are grouped above'
    for key in confirmed:
        prior_index = next(i for i, row in enumerate(before) if row['key'] == key)
        i, split = next((i, r) for i, r in enumerate(read(new)['classifications']) if r['key'] == key)
        j = next(j for j, r in enumerate(split['attempts']) if r['confirmed'])
        fields = ('Gibbs_decrease_over_RT_mol', 'numerical_error_over_RT_mol')
        yield f'MDEA confirmed grid split · {key} · T / absolute P', 'K / Pa', record(new, ('classifications', i), ('temperature_K', 'pressure_Pa'), '1 mol MDEA'), record(old, (prior_index,), ('T_K', 'pressure_Pa'), 'same grid key, pressure missing from archive')
        yield 'MDEA confirmed grid split · Gibbs decrease / paired numerical error', 'mol (G/RT)', record(
            new, ('classifications', i, 'attempts', j), fields, '1 mol MDEA'), record(old, (prior_index,), ('descent',), 'same grid key, no descent')

    for family, case in (('free', 'AMP'), ('fixed', 'AMP fixed')):
        for protocol in ('native', 'supplied'):
            new = CURRENT[case] + protocol + '/search-outcome.json.gz'
            old = ROUND5 + f'search-{family}-{protocol}-full.json.gz'
            yield f'{LABEL[case]} {protocol} · {label}', 'states', search_cell(new, ('tally',), read(new)['confirmed']), search_cell(old, ('tally',), read(old)['classification']['confirmed'])
            keys = ('tally', 'supplied_trial_counts')
            fields = ('available', 'unavailable', 'not_applicable')
            yield f'{LABEL[case]} {protocol} supplied trials (available / refused / inapplicable)', 'trials', record(new, keys, fields, '666 states'), record(old, keys, fields, '666 states')


def worked_states():
    path = MEA + 'bands.json'
    old = BANDS + 'band-table.csv'
    fields = ('T_min_K', 'T_max_K', 'AARD_percent', 'mean_signed_relative_percent', 'RMSE')
    bands = ('property', 'band', 'role')
    prior = {tuple(r[k] for k in bands): (i, r) for i, r in enumerate(read(old)) if r['cohort'] == 'all'}
    for i, r in enumerate(read(path)['result']):
        key = tuple(r[k] for k in bands)
        j, v = prior[key]
        assert r['n'] == int(v['n'])
        yield 'MEA temperature band · ' + ' · '.join(key), 'K / K / % / % / ' + r['unit'], record(path, ('result', i), fields, r['n']), cell(
            tuple(float(v[k]) for k in fields), old, f'[{j}].'+'/'.join(fields), v['n'])

    points = MEA + 'band-points.json'
    for j, r in enumerate(read(old)):
        if r['cohort'] == 'all':
            continue
        terms = (r['property'], r['role'], r['cohort'])
        group = [p for p in read(points)['result'] if itemgetter('property', 'role', 'cohort')(p) == terms and
                 ('absorber' if p['T_K'] <= 353.2 else 'stripper' if p['T_K'] >= 370.0 else 'intermediate') == r['band']]
        assert len(group) == int(r['n']), terms
        errors = [(p['predicted']-p['observed'], p['observed']) for p in group]
        relative = [100*e/o for e, o in errors]
        temperatures = [p['T_K'] for p in group]
        values = min(temperatures), max(temperatures), fmean(map(abs, relative)), fmean(relative), sqrt(fmean(e*e for e, _ in errors))
        yield 'MEA temperature band · '+' · '.join((*terms, r['band'])), 'K / K / % / % / '+r['unit'], cell(
            values, points, f'result rows: {terms}; {r["band"]}; T_K/observed/predicted', len(group)), cell(
            tuple(float(r[k]) for k in fields), old, f'[{j}].'+'/'.join(fields), r['n'])

    path = MEA + 'heat-replay.json'
    old = BANDS + 'heat-replay.json'
    yield 'MEA added heat replay (available / attempted)', 'rows', *(
        cell((sum(r['status'] == 'available' for r in read(p)['rows']), len(read(p)['rows'])), p, 'rows[].status', 'Kim 2014 and Vinjarapu Table 5')
        for p in (path, old))
    path = READBACK + 'MEA/hong-matched-pressure.json'
    for kind, rows in read(path)['grouped'].items():
        for cohort, arms in rows.items():
            fields = ('aard_percent', 'bias_percent', 'available')
            keys = ('grouped', kind, cohort)
            for arm in ('salt_anchored', 'hong', 'polley_hedengren'):
                yield f'MEA Hong matched pressure · {kind} · {cohort} · {arm}', '% / % / rows', record(
                    path, (*keys, arm), fields, arms[arm]['attempted'], '.2f'), record(path, (*keys, 'prior_f2'), fields, arms['prior_f2']['attempted'], '.2f')
    path = READBACK + 'MEA/baygi-matched-pressure.json'
    n = read(path)['n']
    yield 'MEA Baygi matched pressure · AARD / bias / relative N / available N', '% / % / counts', *(
        cell(rates((dict(r, status='Available') for r in read(path)['rows']), column, 'observed_Pa'),
             path, f'rows: {column}/observed_Pa', n, '.2f') for column in ('salt_anchored_Pa', 'prior_F2_Pa'))
    yield 'Baygi–Pahlavanzadeh published AARD', '%', record(path, ('reference',), ('deviation_percent',), n, '.2f'), 'Published comparator'

    path = CURRENT['MDEA'] + '../kuranov-matched-pressure.json.gz'
    for cohort, rows in read(path)['grouped'].items():
        fields = ('solved_AARD_percent', 'bias_percent', 'solved')
        yield f'MDEA Kuranov matched pressure · {cohort}', '% / % / rows', record(
            path, ('grouped', cohort, 'salt_anchored'), fields, rows['salt_anchored']['n'], '.2f'), record(path, ('grouped', cohort, 'present'), fields, rows['present']['n'], '.2f')

    yield from hong_properties()
    yield from pressure_uncertainty()
    yield from kim_intervals()

    yield 'MEA carbonate-pool predicted/observed geometric mean / min / max / AARD / bias', '1 / 1 / 1 / % / %', *(
        carbonate(p+'carbonate-share.csv') for p in (EVIDENCE, F2))

    for i, r in enumerate(read(MEA+'check-values.json')):
        old = PAPER+'check-values.json'
        assert (r['group'], r['feed'], r['T_K']) == tuple(read(old)[i][k] for k in ('group', 'feed', 'T_K'))
        for field in ('T_K', 'printed_digits_agree', *r['answers'][0]):
            keys = (i,) if field in ('T_K', 'printed_digits_agree') else (i, 'answers', 0)
            unit = 'K' if field == 'T_K' else 'Pa' if field.endswith('_Pa') else 'kg/m³' if field.endswith('_kg_m3') else 'mol/m³' if field.endswith('_mol_m3') else '1'
            yield f'MEA {r["group"]} bubble check · {field}', unit, *(record(p, keys, (field,), 'two starts', '.10g') for p in (MEA+'check-values.json', old))

    path, old = MEA+'reference-state.json', REFERENCE+'mea.json'
    basis = '1 mol MEA in unloaded stock; loading 0 → 0.31'
    units = {'T_K':'K', 'P_Pa':'Pa', 'MEA_wt_percent':'wt%', 'added_CO2_mol':'mol',
             'loading_initial':'mol/mol', 'loading_final':'mol/mol', 'loaded_mass_kg':'kg',
             'heat_kJ_mol':'kJ/mol added CO₂', 'cp_J_mol_K':'J/(mol feed K)', 'cp_kJ_kg_K':'kJ/(kg solution K)',
             'cp_minus_fine_J_mol_K':'J/(mol feed K)'}
    for field, unit in units.items():
        yield f'MEA S15 · {field}', unit, *(record(p, (), (field,), basis, '.6f') for p in (path, old))
    for i, reaction in enumerate(read(path)['reactions']):
        for field in ('P_source_Pa', 'ln_K_source', 'Gamma', 'source_kJ_mol', 'fugacity_kJ_mol', 'ideal_gas_kJ_mol'):
            unit = 'Pa' if field.endswith('_Pa') else 'kJ/mol reaction' if field.endswith('_kJ_mol') else '1'
            yield f'MEA S15 {reaction["name"]} · {field}', unit, *(record(p, ('reactions', i), (field,), basis, '.6f') for p in (path, old))


def hong_properties():
    for block in ('Amundsen2009', 'Hartono2014', 'Han2012', 'Kim 313.15 K', 'Kim 353.15 K', 'Kim 393.15 K'):
        path = HONG + block + '.csv'
        matched = [r for r in read(path) if r['three_model_eligible'] == 'True']
        heat = block.startswith('Kim')
        source = 'kim2007-heat-pathways/kim-heat.csv' if heat else 'density.csv'
        identity = 'record_id' if heat else 'id'
        pred, obs = ('predicted', 'observed') if heat else ('predicted_kg_m3', 'observed_kg_m3')
        cells = []
        new_path = EVIDENCE + source
        keyed = {r[identity]: r for r in read(new_path)}
        current = [keyed[r['record_id']] for r in matched]
        for row, reference in zip(current, matched, strict=True):
            assert abs(float(row[obs])-float(reference['observed'])) < 1e-9
            if heat:
                assert abs(float(row['previous_loading'])-float(reference['previous_loading'])) < 1e-9
        if heat:
            current = [dict(r, status=r['interval_status']) for r in current]
        cells.append(cell(rates(current, pred, obs, 'available' if heat else 'Available'), new_path,
                          f'{identity} matches {block}.csv three_model_eligible=true; {pred}/{obs}', len(matched), '.2f'))
        reference = [dict(r, status='Available') for r in matched]
        cells.append(cell(rates(reference, 'adopted'), path,
                          'three_model_eligible=true; adopted/observed', len(matched), '.2f'))
        yield f'MEA Hong matched {'heat' if heat else 'density'} · {block}', '% / % / counts', *cells


def pressure_uncertainty():
    cells = []
    for path, audit in zip((MEA+'uncertainty/prediction-bands.csv', OBJECTIVE+'MEA/prediction-bands.csv'), audits('MEA'), strict=True):
        cohort = [r for r in read(path) if r['group'] == 'common149: partial_pressure']
        assert len(cohort) == 47
        multiplier = read(audit)['result']['SE_multiplier']
        errors = [100 * float(r['SE_bound_fixed']) * multiplier / float(r['value']) for r in cohort]
        cells.append(cell((min(errors), max(errors)), path,
                          'common149 partial pressure: range of 100 × SE_bound_fixed × result.SE_multiplier / value',
                          f'{len(cohort)} fitted pressures', '.2f'))
    yield 'MEA fitted partial pressure relative stage SE range', '%', *cells


def kim_intervals():
    subpath = 'kim2007-heat-pathways/summary.json'
    for subset in ('all_printed', 'source_consistent', 'without_first120'):
        keys = ('temperatures', '393.15', 'metrics', 'semi_differential', subset)
        yield f'MEA Kim 393.15 K finite-interval heat · {subset} · AARD / RMSE', '% / kJ/mol added CO₂', *(
            record(path, keys, ('aard_percent', 'rmse'), value_at(path, keys)['n'])
            for path in (EVIDENCE+subpath, F2+subpath))


def carbonate(path):
    ratios = [float(r['calc_over_obs']) for r in read(path)]
    values = exp(fmean(map(log, ratios))), min(ratios), max(ratios), 100*fmean(abs(r-1) for r in ratios), 100*fmean(r-1 for r in ratios)
    return cell(values, path, 'calc_over_obs: exp(mean(log)), min, max, 100 × mean absolute and signed relative deviations', len(ratios))


def readbacks():
    q4, q5 = MEA+'q4.json', MEA+'q5.json'
    old4, old5 = ROUND3+'q4.json', ROUND3+'q5.json'
    for i, r in enumerate(read(q4)['result']['rows']):
        assert r['identity'] == read(old4)['rows'][i]['identity']
        for convention in ('baseline', 'fixed_reference'):
            field = ('P_Pa', 'value_Pa') if 'value_Pa' in r[convention] else ('P_Pa',)
            yield f'MEA reaction reference · {r["identity"]} · {convention} system P' + (' / pCO₂' if len(field) == 2 else ''), 'Pa', record(q4, ('result', 'rows', i, convention), field), record(old4, ('rows', i, convention), field)
        if r.get('bubble_pressure_change'):
            yield f'MEA reaction reference · {r["identity"]} · bubble pressure change', 'Pa / %', record(q4, ('result', 'rows', i, 'bubble_pressure_change'), ('absolute', 'percent')), record(old4, ('rows', i, 'bubble_pressure_change'), ('absolute', 'percent'))
    for i, convention in enumerate(('system pressure', 'fixed reference')):
        yield f'MEA S15 reaction pressure sensitivity · {convention} addition heat', 'kJ/mol added CO₂', record(q4, ('result', 'heat', i), ('value_kJ_mol',)), record(old4, ('heat', i), ('value_kJ_mol',))
    for field in read(q4)['result']['checks']:
        yield f'MEA reaction pressure check · {field}', '1', record(q4, ('result', 'checks'), (field,)), record(old4, ('checks',), (field,))
    for i, r in enumerate(read(q4)['result']['S15_common_basis']):
        yield f'MEA S15 {r["reaction"]} common molality ln K / Γ', '1', record(q4, ('result', 'S15_common_basis', i), ('common_ln_K', 'common_Gamma'), fmt='.6f'), record(old4, ('S15_common_basis', i), ('common_ln_K', 'common_Gamma'), fmt='.6f')
    for i, r in enumerate(read(q5)['result']['rows']):
        if r['symbol'] is None:
            fields = ('pH', 'raw_R1_pH', 'water_reaction_pass', 'carbonate_share')
            yield f'MEA activity at {r["T_K"]} K, {r["P_Pa"]} Pa, loading {r["loading"]} · pH / raw R1 pH / agreement / carbonate-pool split', '1', record(q5, ('result', 'rows', i), fields), record(old5, ('rows', i), fields)
    i = next(i for i, r in enumerate(read(q5)['result']['rows']) if r['symbol'] is None and r['T_K'] == 313.15 and r['loading'] == 0.30)
    for ion in value_at(q5, ('result', 'rows', i, 'ions')):
        keys = ('rows', i, 'ions', ion)
        yield f'MEA activity at loading 0.30 · {ion} · ln γ / DH / Born / remainder', '1', *(
            record(path, (*prefix, *keys), ('ln_gamma',), fmt='.6f') + '<br>' +
            record(path, (*prefix, *keys, 'dilutions', 2), ('DH', 'Born', 'remainder'), 'dilution ε=10⁻¹⁴', '.5f')
            for path, prefix in ((q5, ('result',)), (old5, ())))
    for field in ('control_carbonate_total_carbon_fraction', 'control_pass'):
        yield f'MEA pH readback · {field}', '1', record(q5, ('result',), (field,)), record(old5, (), (field,))
    for i, r in enumerate(read(q5)['result']['carbonate_pool_comparison']):
        fields = ('loading', 'observed', 'carbonate_pool_split')
        yield f'MEA pH readback · {r["identity"]} (loading / observed / calculated)', 'mol/mol / 1 / 1', record(q5, ('result', 'carbonate_pool_comparison', i), fields), record(old5, ('carbonate_pool_comparison', i), fields)

    path = CURRENT['MDEA']+'binary-onset.json'
    for pressure, data in read(path)['result']['pressures'].items():
        old = PHASE+pressure
        yield f'MDEA CO₂-free onset bracket · {pressure[7:-5]} Pa', 'K', cell(data['brackets'][0]['bracket_K'], path, f'result.pressures.{pressure}.brackets[0].bracket_K', 'refined coexistence bracket', '.5f'), cell(
            read(old)['brackets'][0]['bracket_K'], old, 'brackets[0].bracket_K', 'refined coexistence bracket', '.5f')
        yield f'MDEA CO₂-free interaction at 423 K · {pressure[7:-5]} Pa', '1', record(path, ('result', 'pressures', pressure), ('fitted_k_at_423_K',)), record(old, (), ('fitted_k_at_423_K',))

    path, old = CURRENT['MDEA']+'fixed-pressure.json.gz', PHASE+'fixed-pressure.json'
    fields = ('T_K', 'P_Pa', 'outcome')
    yield 'MDEA 262.862 MPa worked state · T / P / outcome (old split historical)', 'K / Pa / 1', record(path, (), fields, '1 mol MDEA'), record(old, (), fields, '1 mol MDEA')
    for i, r in enumerate(read(path)['attempts']):
        yield f'MDEA 262.862 MPa attempt {i+1} · confirmation / cause', '1', record(path, ('attempts', i), ('confirmed', 'message')), record(old, ('attempts', i), ('confirmed', 'message'))

    for i, attempt in enumerate(read(old)['attempts']):
        if 'Gibbs_decrease_over_RT_mol' not in attempt:
            continue
        fields = ('Gibbs_decrease_over_RT_mol', 'numerical_error_over_RT_mol')
        yield f'MDEA 262.862 MPa attempt {i+1} · Gibbs decrease / paired numerical error', 'mol (G/RT)', record(path, ('attempts', i), fields), record(old, ('attempts', i), fields)

    path = CURRENT['AMP']+'../common-pressure.json'
    yield 'AMP S14 replay common absolute pressure', 'Pa', record(path, (), ('common_Pa',), '1 feed'), record(path, (), ('common_Pa',), '1 feed')
    for family in ('free', 'fixed'):
        yield f'AMP {family} historical S14 feed · bubble pressure', 'Pa', *(
            record(path, ('bubbles', case), ('pressure_Pa',)) for case in (family, 'prior-'+family))
        yield f'AMP {family} historical S14 feed · common pressure above bubble', 'Pa', record(
            path, ('margins_Pa',), (family,)), record(path, ('margins_Pa',), ('prior-'+family,))
        fields = ('tpd_over_rt',)
        selector = ('minimum_trial', 'quantities')
        yield f'AMP {family} S14 feed · min TPD/RT at common pressure', '1', record(path, ('outcomes', family, *selector), fields, f"{read(path)['common_Pa']!r} Pa"), record(path, ('outcomes', 'prior-'+family, *selector), fields, f"{read(path)['common_Pa']!r} Pa")
        yield f'AMP {family} S14 feed · confirmed / attempted LL at common pressure', 'states', *(
            cell((sum(r['confirmed'] for r in attempts), len(attempts)), path, f'outcomes.{case}.attempts[].confirmed', '1 feed')
            for case in (family, 'prior-'+family) for attempts in [read(path)['outcomes'][case]['attempts']])

    old = REFERENCE+'amp.json'
    yield 'Historical original AMP S14 split · T / P / Gibbs decrease / numerical error', 'K / Pa / mol (G/RT) / mol (G/RT)', (
        'See expanded S14-feed comparison above'), record(old, (), ('T_K', 'P_Pa'), '1 feed') + '<br>' + record(
            old, ('split',), ('Gibbs_decrease_over_RT_mol', 'numerical_error_over_RT_mol'), '1 feed')



SECTIONS = {'Salt calibration': salt_rows, 'Objectives, contributions and variance': objectives,
            'Fitted parameters and conditional standard errors': parameters, 'Deviations by observable and source': deviations,
            'Phase-search coverage and outcomes': searches, 'Matched comparisons and worked states': worked_states,
            'Worked-state readbacks': readbacks}


def handoff(check):
    lines = ['# Salt-anchored parameter handoff', '',
             'Full-precision values precede printed rounding in parentheses. The count beside each record gives its denominator or state basis. '
             'Relative deviations use prediction minus observation divided by observation. Deviation columns give AARD, signed bias, relative N and available N. '
             'For conditional SE, stage degrees of freedom use responsive rows minus interior rank (#420).', '',
             'The 0.765 comparison uses MEA F2, the selected #413 DEA and #411 MDEA fits, and the #434 expanded AMP fit of the same slope family. '
             'The salt osmotic control replays the historical salt laws with F2 effective inputs. The AMP −150 K fit is a sensitivity. '
             'Search counts describe sampled numerical behavior. The 262.862 MPa MDEA split, original AMP S14 split, and #432/#434 old-set sensitivities remain historical.', '',
             'Engine wheel and endpoint identities are in [receiver-law-verification.json](receiver-law-verification.json). '
             'Display rebinding belongs to #429.', '',
             'Historical sensitivities and certificates are documented in the '
             '[#432 handoff](../../../round_3/manuscript-handoff.md) and '
             '[#434 handoff](../../../round_5/manuscript-handoff.md).', '']
    existing = OUT.read_text().splitlines() if check else []
    saved = {(line.split(' | ', 1)[0], section): line for section, line in table_rows(existing)}
    for section, make_rows in SECTIONS.items():
        rows = list(make_rows())
        lines += [f'## {section} ({len(rows)})', '',
                  '| Quantity | Units | Salt-anchored #435 | 0.765 comparison |', '| --- | --- | --- | --- |']
        if len(rows) != len({row[0] for row in rows}):
            raise SystemExit(f'{section}: repeated quantity key')
        for label, unit, new, old in rows:
            if '](' not in new and '](' not in old:
                raise SystemExit(f'{section} / {label}: missing retained record')
            label = display(label, '')
            line = f'| {label} | {unit} | {new} | {old} |'
            if check and saved.get((f'| {label}', section)) != line:
                raise SystemExit(f'{section} / {label}: retained-record readback mismatch\nExpected {line}\nFound {saved.get((f"| {label}", section))}')
            lines.append(line)
        lines.append('')
        print(f'{section}: {len(rows)}')
    if check:
        if lines != existing + ['']:
            raise SystemExit(f'{OUT}: section layout or quantity inventory differs')
    else:
        OUT.write_text('\n'.join(lines))


def table_rows(lines):
    section = ''
    for line in lines:
        if line.startswith('## '):
            section = line[3:].rsplit(' (', 1)[0]
        elif line.startswith('| ') and not line.startswith(('| Quantity |', '| --- |')):
            yield section, line


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    handoff(parser.parse_args().check)
