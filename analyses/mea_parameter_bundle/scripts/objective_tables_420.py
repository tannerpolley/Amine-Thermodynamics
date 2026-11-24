"""Regenerate #420 table and reconciliation records from retained results."""
import argparse
import csv
import io
import json
import math
import sys
from collections import Counter, defaultdict
from functools import partial

from a7_presentation import BUNDLE, ROOT

sys.path[:0] = [str(ROOT/'src'), str(ROOT/'docs/scientific/latex/scripts')]
from final_rerun_tables import rowkey  # noqa: E402
from MEA.common.retained_results import parameter_fingerprint, read, result  # noqa: E402

RESULTS = BUNDLE/'results'
OUT = RESULTS/'objective-weights-420'
PAPER = RESULTS/'paper-evidence-341'
BASE = RESULTS/'reduced-refit'
WHEEL = ROOT/'analyses/mdea_mea_workflow/results/shared-bicarbonate-417/wheel-modules.json'


def csv_rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def csv_bytes(rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def objectives(declarations, effective, replays, scores):
    weights, blocks = [], []
    assert len({d['identity'] for d in declarations}) == len(declarations)
    for old, new in zip(declarations, effective, strict=True):
        assert (old['identity'], old['group']) == (new['identity'], new['group'])
        weights.append(dict(identity=old['identity'], observable=old.get('kind', old['constructor']),
                            group=old['group'], original_weight=old['weight'], alternative_weight=new['weight']))
    for ((mapping, weighting), replay), score in zip(replays.items(), scores, strict=True):
        costs = defaultdict(list)
        for weight, row in zip(weights, replay['rows'], strict=True):
            assert row['status'] == 'Available' and row['identity'] == weight['identity']
            w = weight['original_weight' if weighting == 'original' else 'alternative_weight']
            assert math.isclose(row['cost'], .5*w*row['residual']**2, rel_tol=1e-14), row['identity']
            constructor = row['basis']['constructor']
            observable = weight['observable'] if constructor == 'observation' else constructor
            costs[weight['group'], observable].append(row['cost'])
        blocks.extend(dict(mapping=mapping, weights=weighting, group=g, observable=q, rows=len(v),
                           cost=math.fsum(v)) for (g, q), v in costs.items())
        assert math.isclose(math.fsum(row['cost'] for row in replay['rows']), score, rel_tol=1e-14)
    return weights, blocks


# Paired groups and the corresponding independent #338 counts.
REFERENCE_GROUPS = {
    'fitted fitted CO2 partial pressure': 'fitted: fitted CO2 partial pressure',
    'unfitted six-source pressures': 'not fitted: six-source pressures',
    'Wagner pressures': 'not fitted: Wagner pressures',
    'fitted fitted phase mole fraction': 'fitted: fitted phase mole fraction',
    'fitted restored species': 'fitted: restored species',
    'fitted Jakobsen ratio': 'fitted: Jakobsen ratio',
    'Matin 19 pools': 'not fitted: Matin 19 pools',
    'Böttinger 353 K checks': 'not fitted: Bottinger 353 K',
}


def s9_check(blocks):
    published, reduced = defaultdict(list), defaultdict(list)
    for row in csv_rows(PAPER/'objective-groups.csv'):
        published[rowkey(row['group'], row['quantity'])].append(row)
    for row in blocks:
        if (row['mapping'], row['weights']) == ('reported', 'original'):
            reduced[rowkey(row['group'], row['observable'])].append(row)
    assert reduced.keys() == published.keys()
    report = {}
    for key, reference in published.items():
        part = reduced[key]
        n, cost = sum(v['rows'] for v in part), math.fsum(v['cost'] for v in part)
        expected = float(f"{sum(float(v['cost']) for v in reference):.6g}")
        assert n == sum(int(v['n']) for v in reference) and float(f'{cost:.6g}') == expected, key
        group, quantity = key
        label = ('Cai vapor water fraction' if key == ('Cai', 'mole_fraction')
                 else quantity if group in ('common149', 'species', 'Cai') else group)
        report[label] = dict(n=n, cost=cost, reference=expected)
    return report


def reconcile(info, contributions, blocks, paired, mapping, search, load):
    report = {}
    for amine, record in info.items():
        rows, p = record['rows'], record['p']
        excluded = [v['identity'] for v in record['excluded']]
        responsive = [v for v in rows if v['identity'] not in excluded]
        rss, stage_rss = (math.fsum(v['weighted_residual']**2 for v in values) for values in (rows, responsive))
        total = math.fsum(float(v['cost']) for v in contributions[amine])
        assert math.isclose(total, rss/2, rel_tol=1e-14), amine
        n, na = len(rows), len(responsive)
        assert n == sum(int(v['n']) for v in contributions[amine]) == record['n']
        assert (na, n-p, na-p) == (record['na'], record['denominator'], record['stage_denominator'])
        old, stage = rss/(n-p), stage_rss/(na-p)
        for field, value in (('rss', rss), ('stage_rss', stage_rss), ('variance', old), ('stage_variance', stage)):
            assert math.isclose(record[field], value, rel_tol=1e-14), (amine, field)
        report[amine] = dict(n=n, na=na, p=p, objective=rss/2, all_row_variance=old,
                             stage_variance=stage, excluded=excluded, contribution_sum=total)
    report['F2_S9'] = s9_check(blocks)
    report['mapping_fingerprints'] = dict(
        reported=parameter_fingerprint(read(RESULTS/'selected-current-best-parameters.json')),
        alternative=parameter_fingerprint(mapping))
    census = load('alternative/search/census-raw.json.gz')
    records = [v for state in census for v in state.get('stability', [])]
    supplied = Counter()
    for record in records:
        supplied.update(record['supplied_counts'])
    supplied['missing'] = len(census)*len(read(BASE/'split-registry.json')['trials'])-sum(supplied.values())
    supplied['negative'] = sum(v['evidence'] == 'evaluated' and v['quantities']['tpd_over_rt'] < 0
                               for record in records for v in record['supplied_trials'])
    assert supplied == search['supplied'], 'supplied-trial accounting'
    reference = {v['dataset']: v['n'] for v in read(BASE/'F2/agreement.json')}
    membership = Counter(group for row in paired['rows'] for group in row['groups'])
    counts = {group: membership[group] for group in REFERENCE_GROUPS}
    for group, n in counts.items():
        assert n == reference[REFERENCE_GROUPS[group]] == paired['groups'][group]['reported']['declared'], group

    native = load('handoff/classification.json')
    census_control, = load('handoff/census-raw.json.gz')
    reduced, = load('handoff/census.json')['rows']
    supplied_attempts = census_control['coexistence']
    assert len(supplied_attempts) == reduced['supplied_negative']
    assert load('handoff/supplied-grid-guard.json') == 'MEA grid carries supplied trials'
    native_counts = Counter()
    for attempt in native['attempts']:
        failed = not attempt['requested_tolerance_met']
        outcome = 'failed_solve' if failed else 'confirmed' if attempt['confirmed'] else 'unconfirmed'
        assert attempt.get('outcome', outcome) == outcome
        native_counts[outcome] += 1
    supplied_counts = Counter(v['outcome'] for v in supplied_attempts)
    totals = native_counts + supplied_counts
    attempts = native['attempts'] + [v['attempt'] for v in supplied_attempts if 'attempt' in v]
    assert totals['failed_solve'] == sum(not v['requested_tolerance_met'] for v in attempts)
    assert totals['confirmed'] == sum(v['requested_tolerance_met'] and v['confirmed'] for v in attempts)
    assert totals['unconfirmed'] == len(attempts) - totals['confirmed'] - totals['failed_solve']
    states = (native_counts, supplied_counts)
    handoff = dict(native_attempts=len(native['attempts']), supplied_attempts=len(supplied_attempts),
                   confirmed=totals['confirmed'], unconfirmed_attempts=totals['unconfirmed'],
                   failed_solves=totals['failed_solve'], unavailable=totals['unavailable']+int('classification_error' in native),
                   unresolved_states=sum(bool(v) and v.keys() <= {'unconfirmed', 'failed_solve'} for v in states),
                   states_with_failed_solves=sum(bool(v['failed_solve']) for v in states),
                   native=dict(native_counts), supplied=dict(supplied_counts))
    return dict(report, search=search['alternative'], supplied=dict(supplied),
                reference_count_checks=counts, handoff=handoff)


def generate(folder, check):
    wheel = read(WHEEL)
    load = partial(result, folder, wheel_sha256=wheel['sha256'])
    info = {k: load(f'{k}/information.json.gz') for k in ('MEA', 'DEA', 'MDEA', 'AMP')}
    contributions = {k: csv_rows(folder/f'{k}/contributions.csv') for k in info}
    selection, cross = load('alternative/selection.json'), load('alternative/cross-score.json.gz')
    selected = selection['selected']
    assert selected['mapping'] == read(folder/'alternative/parameters.json')
    replays = {('reported', 'original'): load('reported-mea.json.gz'),
               ('reported', 'Cai mean'): load('alternative/f2-replay.json.gz'),
               ('alternative', 'original'): cross,
               ('alternative', 'Cai mean'): read(folder/selected['run']/'replay.json')}
    declarations = read(PAPER/'objective-declarations.json')
    effective = load(f"{selected['run']}/inputs.json.gz")['rows']
    weights, blocks = objectives(declarations, effective, replays, [v for row in cross['objectives'] for v in row])
    paired, search = load('alternative/paired-comparisons.json.gz'), load('alternative/search/outcomes.json')
    report = reconcile(info, contributions, blocks, paired, selected['mapping'], search, load)
    tables = notebook_tables(folder, info, contributions, weights, selection, cross, paired, search,
                            report['handoff'], load('MDEA/pure-water-derivative-control.json'), wheel)
    for name, body in (
        ('alternative/weights.csv', csv_bytes(weights)), ('alternative/objective-blocks.csv', csv_bytes(blocks)),
        ('reconciliation.json', (json.dumps(report, indent=2, allow_nan=False)+'\n').encode()),
        ('tables.md', tables.encode()),
    ):
        path = folder/name
        if check:
            assert path.read_bytes() == body, f'{name} needs regeneration'
        else:
            path.write_bytes(body)


def notebook_tables(folder, info, contributions, weights, selection, cross, paired, search, handoff, water, wheel):
    lines = ['<!-- Generated by objective_tables_420.py. -->', '']
    groups = paired['groups']

    def add(*paragraphs):
        lines.extend(item for paragraph in paragraphs for item in (paragraph, ''))

    def table(head, rows):
        for cells in (head, ['---']*len(head), *rows):
            lines.append('| ' + ' | '.join(map(str, cells)) + ' |')
        lines.append('')

    def fmt(values, precision='.8f'):
        return [format(v, precision) if v is not None else '—' for v in values]

    cai = [v for v in weights if v['group']=='Cai']
    ncai = Counter(v['observable'] for v in cai)
    cai_scales = {v['observable']: v['scale'] for v in info['MEA']['rows'] if v['group']=='Cai'}
    add(f"Each of the {ncai['temperature']} Cai bubble temperatures and {ncai['mole_fraction']} vapor water mole "
        f"fractions received weight {cai[0]['alternative_weight']:g}. Their respective residual scales were "
        f"{cai_scales['temperature']:g} K and {cai_scales['mole_fraction']:g} mole fraction. "
        f"Each observable contributed half its mean squared scaled residual. The fit retained all {len(weights)} "
        f"observations. Both mappings were evaluated on ePC-SAFT {wheel['wheel'].split('-')[1]} (build `{wheel['commit'][:8]}`).",
        '## Which rows inform the fitted coordinates?')
    table(('Amine', 'Objective', 'Rows', 'Responsive rows', 'Interior rank', 'All-row DOF', 'Stage DOF',
           'All-row variance', 'Stage variance', 'SE multiplier'),
          ([name, f"{v['rss']/2:.8f}", *(v[k] for k in ('n','na','p','denominator','stage_denominator')),
            *fmt(v[k] for k in ('variance', 'stage_variance', 'SE_multiplier'))] for name, v in info.items()))
    lawson, = (v for v in contributions['DEA'] if v['group']=='Lawson')
    n = int(lawson['n'])
    scale = math.sqrt(1/(n*float(lawson['coefficient_min'])))
    amp = [int(v['n']) for v in contributions['AMP'] if v['group']=='binary']
    amp_coordinates = info['AMP']['coordinates']
    active = [amp_coordinates[i] for i in info['AMP']['active_bounds']]
    bounds = ', '.join(f"`{v['identity']}` at the {'lower' if v['origin']==v['bounds'][0] else 'upper'} bound" for v in active)
    add(f"The Lawson block folds its assigned log-pressure scale into its squared-residual coefficient "
        f"$1/({n}\\times{scale:g}^2)$. The AMP binary block shares a denominator of {sum(amp)} "
        f"across {amp[0]} pressure and {amp[1]} vapor-fraction rows. The AMP active coordinates are {bounds}.")

    rank_labels = {
        'fitted CO2 partial pressure': 'Loaded CO₂ partial pressure',
        'species mole fractions': 'Liquid species mole fractions',
        'temperature': 'Cai bubble temperature',
        'mole_fraction': 'Cai vapor water fraction',
        'Cai': 'Cai union',
        'Kiepe': 'Kiepe CO₂–water pressure',
        'whole fit': 'Whole fit',
    }
    mea = info['MEA']['blocks']
    rank_rows = []
    for key, label in rank_labels.items():
        v = mea[key]
        full, interior = v['adjustable']['rank'], v['interior']['rank']
        smallest = fmt([v['adjustable']['singular_values'][full-1] if full else None], '.6g')[0]
        rank_rows.append((label, v['n'], v['zero_rows'], f"{v['cost']:.9g}", f'{full} / {interior}', smallest))
    table(('MEA block', 'Rows', 'Exact-zero rows', 'Cost', 'Adjustable / interior rank',
           'Smallest retained adjustable singular value'), rank_rows)
    derivatives = sum(len(v['diagnostic_derivatives']) for v in water['rows'])
    max_pressure = max(abs(v['pressure_change_Pa']) for v in water['rows'])
    add(f"The Cai observables account for {100*mea['Cai']['cost']/mea['whole fit']['cost']:.2f}% of the reported "
        f"objective. All {mea['Kiepe']['n']} Kiepe rows contribute to the objective and have exactly zero "
        f"derivatives. The MEA Jacobian uses the retained derivatives from build `{info['MEA']['wheel']}`.",
        f"Disabling the MDEAH⁺–water association edges for the pure-water diagnostic produced {derivatives} exact-zero "
        f"derivatives and a maximum pressure change of {max_pressure:.2e} Pa. The {len(water['rows'])} pure-water "
        f"rows contribute {water['pure_water_cost']:.10g} to the {water['declared']}-row objective. "
        f"The stage variance uses {info['MDEA']['stage_denominator']} residual degrees of freedom.",
        '## Conditional uncertainty at the reported fits')
    mea_se, mdea_se = (100*(info[k]['SE_multiplier']-1) for k in ('MEA', 'MDEA'))
    bands = [v for v in csv_rows(folder/'MEA/prediction-bands.csv') if v['group']=='common149: partial_pressure']
    relative = [[100*float(v[key])/float(v['value']) for v in bands] for key in ('SE_bound_fixed', 'stage_SE')]
    old_span, new_span = ('–'.join(fmt((min(v), max(v)), '.3g')) + '%' for v in relative)
    # objective_weights_420.revised_uncertainty defines the nominal multiplier.
    add(f"The stage variance increases conditional standard errors by {mea_se:.3f}% for MEA "
        f"and {mdea_se:.3f}% for MDEA. The MEA bands use nominal ±1.96 conditional standard "
        f"errors. For the {len(bands)} retained loaded partial pressures, relative standard errors span "
        f"{old_span} under the original convention and {new_span} under the stage convention.",
        '## MEA reweighting and paired comparisons')
    table(('Mapping', 'Original weights', 'Cai mean weights'),
          ([m+' MEA', *fmt(scores)] for m, scores in zip(('Reported', 'Alternative'), cross['objectives'], strict=True)))
    start_costs = ' and '.join(f"{v['cost']:.8f} ({v['start']})" for v in selection['starts'])
    add(f"The converged start families reached replayed objectives of {start_costs} with all {len(weights)} "
        f"fitted predictions available. The selected endpoint came from the {selection['selected']['start']} family.")
    table(('Coordinate', 'Unit', 'Reported', 'Alternative', 'Change', 'Bound before → after'),
          ([f"`{v['identity']}`", v['unit'], *fmt((v[k] for k in ('reported', 'alternative', 'change')), '.8g'),
            f"{v['reported_bound'] or 'interior'} → {v['alternative_bound'] or 'interior'}"] for v in cross['parameters']))
    carbonate, = (k for k in groups if k.startswith('fitted Bottinger2008 ')
                  and k.endswith('true-species-liquid-mole-fraction-linear-aggregate'))
    measured = groups[carbonate]['largest_change']['measured']
    density, = (v['source'].removesuffix('2009') for v in contributions['MEA'] if v['group']=='CO2-free density')
    bot = groups['Böttinger 353 K checks']['largest_change']
    comparisons = {
        'fitted fitted CO2 partial pressure': 'Fitted loaded CO₂ partial pressure (Pa)',
        'unfitted six-source pressures': 'Additional six-source CO₂ partial pressure (Pa)',
        'Wagner pressures': 'Wagner CO₂ partial pressure (Pa)',
        **{key: f"{key.removeprefix('transfer ')} transfer pressure (Pa)" for key in groups if key.startswith('transfer ')},
        'fitted Cai temperature': 'Cai bubble temperature (K)',
        'fitted Cai mole_fraction': 'Cai vapor water mole fraction',
        'fitted fitted phase mole fraction': 'Original fitted species mole fractions',
        'fitted restored species': 'Restored fitted species mole fractions',
        carbonate: f"Fitted Böttinger {measured} (linear aggregate of true liquid mole fractions)",
        'fitted Jakobsen ratio': 'Jakobsen fitted ratios',
        'Matin 19 pools': 'Matin unfitted pools',
        'Böttinger 353 K checks': f"Böttinger at {bot['temperature_K']} K",
        'fitted loaded density': 'Loaded density (kg/m³)',
        'fitted CO2-free density': f"{density} unloaded density (kg/m³)",
        'fitted fitted heat of absorption': 'Absorption enthalpy (J/mol CO₂)',
        'fitted heat capacity': 'Heat capacity (J/(mol feed K))',
    }
    errors = []
    for key, label in comparisons.items():
        v = groups[key]
        old, new = v['paired_reported'], v['paired_alternative']
        errors.append([label, old['available'], *fmt((old['aard'], new['aard'], v['aard_change_pp'],
                                                    old['rmse'], new['rmse']), '.6g')])
    table(('Comparison', 'Paired rows', 'Reported AARD / %', 'Alternative AARD / %',
           'Change / pp', 'Reported RMSE', 'Alternative RMSE'), errors)
    available = [v for v in paired['rows'] if v['change'] is not None]
    pressure = max((v for v in available if v['unit']=='Pa'), key=lambda v: abs(v['change']))
    liquid = max((v for v in available if 'mole fraction' in v.get('basis', '').replace('-', ' ')),
                 key=lambda v: abs(v['change']))
    add(f"The largest absolute paired CO₂ partial-pressure change was {pressure['change']:+.0f} Pa at "
        f"{pressure['source']} row `{pressure['target']}`, {pressure['temperature_K']} K, "
        f"{100*float(pressure['mea_mass_fraction']):g} wt% MEA and {float(pressure['loading']):.5g} mol CO₂/mol MEA.",
        f"The largest absolute paired liquid mole-fraction change was {liquid['change']:+.5g} for "
        f"{liquid.get('measured', liquid['species'])} at `{liquid['identity']}`, {liquid['temperature_K']} K "
        f"and {float(liquid['loading']):.5g} mol CO₂/mol MEA.",
        '## Phase-stability search')
    table(('State set', 'States', 'Available parents', 'Descents', 'Confirmed two-liquid states',
           'Unconfirmed attempts', 'Failed solves', 'Unresolved states', 'Unavailable states'),
          ([label, *(search['alternative'][key][field] for field in (
              'states', 'parents_available', 'descents', 'confirmed', 'unconfirmed', 'failed_solves', 'unresolved', 'unavailable'))]
           for key, label in (('grid', 'Main grid'), ('offset', 'Offset grid'), ('census', 'Fixed-pressure census'))))
    supplied = search['supplied']
    baseline = search['baseline']
    descents = sum(baseline[k]['descent'] for k in search['alternative'])
    incomplete = len(baseline['grid']['unavailable'])+len(baseline['offset']['unavailable'])+baseline['census']['incomplete']
    source_ranges = csv_rows(PAPER/'reaction-source-ranges.csv')
    source = source_ranges[0]
    reactions = ', '.join(v['reaction'] for v in source_ranges)
    assert all(v['minimum_K']==source['minimum_K'] and v['maximum_K']==source['maximum_K'] for v in source_ranges)
    add(f"The reported mapping had {descents} descents and {incomplete} incomplete states across the same state sets. "
        f"The alternative census evaluated {supplied['evaluated']:,} supplied trials, with {supplied['negative']} "
        f"negative trials and {supplied['missing']} missing evaluations.",
        f"The retained source range for {reactions} is {source['minimum_K']}–{source['maximum_K']} K ({source['source'].split(', reactions')[0]}).",
        f"The handoff controls produced {handoff['native_attempts']} native and {handoff['supplied_attempts']} supplied "
        f"coexistence attempts. There were **{handoff['failed_solves']} failed solves**, "
        f"**{handoff['unconfirmed_attempts']} completed attempts without a confirmed split**, "
        f"and {handoff['confirmed']} confirmed splits. The controls left {handoff['unresolved_states']} states "
        f"unresolved, including {handoff['states_with_failed_solves']} with failed solves. "
        f"Stored attempt messages distinguish tolerance failures from completed checks.")
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='compare generated content without writing')
    args = parser.parse_args()
    generate(OUT, args.check)
