"""Regenerate #420 reductions and notebook tables from retained records."""
import argparse
import gzip
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

from objective_weights_420 import (
    BASE, EVIDENCE, OUT, ROOT, attempt_outcome, carbonate_measurement, comparison_groups, f,
    fitted_species_label, information_reduction, np, observable_errors, paper, r, s, search_accounting,
)
from shared_bicarbonate_417 import SHA, WHEEL


def result(folder, name):
    data = r.read(folder/name)
    assert data['wheel_sha256'] == SHA, name
    return data['result']


def objectives(declarations, effective, replays):
    weights, blocks, totals = [], [], {}
    assert len({d['identity'] for d in declarations}) == len(declarations)
    for old, new in zip(declarations, effective, strict=True):
        assert (old['identity'], old['group']) == (new['identity'], new['group'])
        weights.append(dict(identity=old['identity'], observable=old.get('kind', old['constructor']),
                            group=old['group'], original_weight=old['weight'], alternative_weight=new['weight']))
    for (mapping, weighting), replay in replays.items():
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
        totals[mapping, weighting] = math.fsum(row['cost'] for row in replay['rows'])
    return weights, blocks, totals


def paired_comparisons(paired, declarations):
    targets = {v['target']: v for v in f.e.rows(EVIDENCE/'state-targets.csv') if v['kind'] == 'packet'}
    carbonate_label = None
    for row in paired['rows']:
        if row['kind'] != 'fitted':
            continue
        declaration = declarations[row['identity']]
        measurement = carbonate_measurement(declaration, targets.get(row['identity'], {}))
        if measurement:
            label = fitted_species_label(row)
            row.update(measurement)
            carbonate_label = fitted_species_label(row)
            row['groups'] = [carbonate_label if v == label else v for v in row['groups']]
    assert carbonate_label is not None
    paired['groups'] = comparison_groups(paired['rows'])
    return carbonate_label


def handoff_counts(native, census):
    supplied = [entry for state in census for entry in state['coexistence']]
    for entry in supplied:
        if 'attempt' in entry:
            entry['outcome'] = attempt_outcome(entry['attempt'])
    for attempt in native['attempts']:
        attempt['outcome'] = attempt_outcome(attempt)

    groups = [native['attempts'], *(state['coexistence'] for state in census)]
    totals = Counter(entry['outcome'] for group in groups for entry in group)
    return dict(native_attempts=len(native['attempts']), supplied_attempts=len(supplied),
                confirmed=totals['confirmed'], unconfirmed_attempts=totals['unconfirmed'],
                failed_solves=totals['failed_solve'], unavailable=totals['unavailable']+int('classification_error' in native),
                unresolved_states=sum(bool(g) and all(a['outcome'] in ('unconfirmed', 'failed_solve') for a in g)
                                      for g in groups),
                states_with_failed_solves=sum(any(a['outcome']=='failed_solve' for a in g) for g in groups),
                native=dict(Counter(a['outcome'] for a in native['attempts'])),
                supplied=dict(Counter(a['outcome'] for a in supplied)))


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


def reconcile(info, contributions, blocks, paired, selected, search, census, handoff):
    report = {}
    for amine, record in info.items():
        rows, p = record['rows'], record['p']
        excluded = [v['identity'] for v in record['excluded']]
        responsive = [v for v in rows if v['identity'] not in excluded]
        rss, stage_rss = (math.fsum(v['weighted_residual']**2 for v in values) for values in (rows, responsive))
        total = math.fsum(float(v['cost']) for v in contributions[amine])
        assert math.isclose(total, rss/2, rel_tol=1e-14), amine
        assert sum(int(v['n']) for v in contributions[amine]) == len(rows)
        old, stage = rss/(len(rows)-p), stage_rss/(len(responsive)-p)
        assert math.isclose(record['variance'], old, rel_tol=1e-14)
        assert math.isclose(record['stage_variance'], stage, rel_tol=1e-14)
        report[amine] = dict(n=len(rows), na=len(responsive), p=p, objective=rss/2, all_row_variance=old,
                             stage_variance=stage, excluded=excluded, contribution_sum=total)
    published = re.findall(r' & \$([\d.]+)\$ & [^\n]+? & \$([\d.]+)\$ \\',
                           (ROOT/'docs/scientific/latex/tables/objective_groups.tex').read_text())
    s9 = {
        'partial_pressure': ('partial_pressure',),
        'mole_fraction': ('common149:mole_fraction', 'restored species:mole_fraction'),
        'addition_enthalpy': ('addition_enthalpy',),
        'Jakobsen': ('amount_ratio',),
        'Kiepe': ('pressure',),
        'CO2-free density': ('CO2-free density:phase_density',),
        'temperature': ('temperature',),
        'Cai vapor water fraction': ('Cai:mole_fraction',),
        'loaded density': ('loaded density:phase_density',),
        'Cp': ('equilibrium_isobaric_heat_capacity',),
    }
    original = [v for v in blocks if (v['mapping'], v['weights']) == ('reported', 'original')]
    report['F2_S9'] = {}
    for (label, keys), (n, cost) in zip(s9.items(), published, strict=True):
        rows = [v for v in original if v['observable'] in keys or f"{v['group']}:{v['observable']}" in keys]
        count, value = sum(v['rows'] for v in rows), math.fsum(v['cost'] for v in rows)
        assert count == int(n) and float(f'{value:.6g}') == float(cost), label
        report['F2_S9'][label] = dict(n=count, cost=value, reference=float(cost))
    report['mapping_fingerprints'] = dict(reported=s.parameter_fingerprint(s.parameter_mapping(paper.RECORD)),
                                          alternative=s.parameter_fingerprint(selected['mapping']))
    supplied = Counter()
    for state in census:
        for record in state['stability']:
            supplied.update(record['supplied_counts'])
    supplied['missing'] = len(census)*len(r.read(BASE/'split-registry.json')['trials'])-sum(supplied.values())
    supplied['negative'] = sum(r.supplied_negative(v) for state in census for record in state['stability']
                               for v in record['supplied_trials'])
    assert supplied == search['supplied']
    reference = {v['dataset']: v['n'] for v in r.read(BASE/'F2/agreement.json')}
    counts = {group: paired[group]['reported']['declared'] for group in REFERENCE_GROUPS}
    assert all(n == reference[REFERENCE_GROUPS[group]] for group, n in counts.items())
    return dict(report, search=search['alternative'], supplied=dict(supplied),
                reference_count_checks=counts, handoff=handoff)


def generate(folder, check):
    def load(name):
        return result(folder, name)

    history = paper.OUT/'uncertainty'
    declarations = r.read(paper.OUT/'objective-declarations.json')
    adopted = r.read(history/'adopted.json')
    coordinates = r.read(history/'inputs.json')['coordinates']
    historical = r.read(paper.OUT/'candidate/replay.json')['rows']
    assert adopted['predictions'] == [v['value'] for v in historical]
    assert adopted['residuals'] == [v['residual'] for v in historical]
    sqrt_weight = np.sqrt([v['weight'] for v in declarations])
    weighted = sqrt_weight*adopted['residuals']
    assert np.array_equal(weighted, [v['weighted_residual'] for v in historical])
    jacobian = sqrt_weight[:, None]*np.asarray(adopted['jacobian']).reshape(len(historical), len(coordinates))
    covariance = r.read(history/'covariance.json')['adopted_point']
    wheel = r.read(paper.OUT/'wheel.json')['commit'][:8]
    mea, mea_contributions = information_reduction(
        'MEA', declarations, historical, coordinates, weighted, jacobian, covariance, wheel)
    info = dict(MEA=mea, **{k: load(f'{k}/information.json.gz') for k in ('DEA', 'MDEA', 'AMP')})
    contributions = dict(MEA=mea_contributions, **{k: f.e.rows(folder/f'{k}/contributions.csv') for k in info if k != 'MEA'})

    selection = load('alternative/selection.json')
    selected = selection['selected']
    assert selected['mapping'] == s.parameter_mapping(folder/'alternative/parameters.json')
    replays = {('reported', 'original'): load('reported-mea.json.gz'),
               ('reported', 'Cai mean'): load('alternative/f2-replay.json.gz'),
               ('alternative', 'original'): load('alternative/cross-score.json.gz'),
               ('alternative', 'Cai mean'): r.read(folder/selected['run']/'replay.json')}
    effective = load(f"{selected['run']}/inputs.json.gz")['rows']
    weights, blocks, totals = objectives(declarations, effective, replays)
    assert all(math.isclose(totals[k], v, rel_tol=1e-14)
               for k, v in zip(replays, sum(replays['alternative', 'original']['objectives'], []), strict=True))

    paired = load('alternative/paired-comparisons.json.gz')
    carbonate = paired_comparisons(paired, {v['identity']: v for v in declarations})
    native, handoff_raw = load('handoff/classification.json'), load('handoff/census-raw.json.gz')
    handoff = handoff_counts(native, handoff_raw)
    handoff_census, = load('handoff/census.json')['rows']
    assert handoff['supplied_attempts'] == handoff_census['supplied_negative']
    assert load('handoff/supplied-grid-guard.json') == 'MEA grid carries supplied trials'
    census = load('alternative/search/census-raw.json.gz')
    search = search_accounting(lambda name: load(f'alternative/{name}'), census)
    reconciliation = reconcile(info, contributions, blocks, paired['groups'], selected, search, census, handoff)
    tables = notebook_tables(folder, info, contributions, weights, totals, selection, replays['alternative', 'original'],
                            paired, carbonate, search, handoff)

    with TemporaryDirectory() as tmp:
        def emit(name, data):
            stored = folder/name
            if stored.suffix == '.csv':
                path = Path(tmp)/stored.name
                f.e.table(path, data)
                body = path.read_bytes()
            elif stored.suffix == '.md':
                body = data.encode()
            else:
                wrapped = name != 'reconciliation.json'
                content = dict(wheel_sha256=SHA, result=r.jsonable(data)) if wrapped else data
                body = (json.dumps(content, indent=1 if wrapped else 2, allow_nan=False)+'\n').encode()
            if check:
                current = stored.read_bytes()
                assert (gzip.decompress(current) if stored.suffix=='.gz' else current) == body, f'{name} needs regeneration'
            else:
                stored.write_bytes(gzip.compress(body, mtime=0) if stored.suffix=='.gz' else body)

        for name, data in (
            ('MEA/information.json.gz', mea), ('MEA/contributions.csv', mea_contributions),
            ('alternative/weights.csv', weights), ('alternative/objective-blocks.csv', blocks),
            ('alternative/paired-comparisons.json.gz', paired),
            ('alternative/observable-errors.csv', observable_errors(paired['groups'])),
            ('handoff/classification.json', native), ('handoff/census-raw.json.gz', handoff_raw),
            ('alternative/search/outcomes.json', search), ('reconciliation.json', reconciliation), ('tables.md', tables),
        ):
            emit(name, data)


def notebook_tables(folder, info, contributions, weights, totals, selection, cross, paired, carbonate, search, handoff):
    lines = ['<!-- Generated by objective_tables_420.py. -->', '']
    groups = paired['groups']

    def add(*paragraphs):
        for paragraph in paragraphs:
            lines.extend((paragraph, ''))

    def table(head, rows):
        def row(cells):
            return '| ' + ' | '.join(map(str, cells)) + ' |'

        lines.extend((row(head), row(['---']*len(head))))
        lines.extend(row(cells) for cells in rows)
        lines.append('')

    def fmt(values, precision='.8f'):
        return [format(v, precision) if v is not None else '—' for v in values]

    def band_stats():
        rows = [v for v in f.e.rows(folder/'MEA/prediction-bands.csv') if v['group']=='common149: partial_pressure']
        relative = [[100*float(v[key])/float(v['value']) for v in rows] for key in ('SE_bound_fixed', 'stage_SE')]
        spans = ['–'.join(fmt((min(v), max(v)), '.3g')) + '%' for v in relative]
        first = rows[0]
        multiplier = (float(first['stage_upper_95']) - float(first['value']))/float(first['stage_SE'])
        return len(rows), spans, multiplier

    cai = [v for v in weights if v['group']=='Cai']
    ncai = Counter(v['observable'] for v in cai)
    cai_scales = {v['observable']: v['scale'] for v in info['MEA']['rows'] if v['group']=='Cai'}
    add(f"Each of the {ncai['temperature']} Cai bubble temperatures and {ncai['mole_fraction']} vapor water mole "
        f"fractions received weight {cai[0]['alternative_weight']:g}. Their respective residual scales were "
        f"{cai_scales['temperature']:g} K and {cai_scales['mole_fraction']:g} mole fraction. "
        f"Each observable contributed half its mean squared scaled residual. The fit retained all {len(weights)} "
        f"observations. Both mappings were evaluated on ePC-SAFT {WHEEL.name.split('-')[1]} "
        f"(build `{WHEEL.parent.name.removeprefix('main-')[:8]}`).",
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
    water = result(folder, 'MDEA/pure-water-derivative-control.json')
    nw = sum(len(v['diagnostic_derivatives']) for v in water['rows'])
    pressure = max(abs(v['pressure_change_Pa']) for v in water['rows'])
    add(f"The Cai observables account for {100*mea['Cai']['cost']/mea['whole fit']['cost']:.2f}% of the reported "
        f"objective. All {mea['Kiepe']['n']} Kiepe rows contribute to the objective and have exactly zero "
        f"derivatives. The MEA Jacobian uses the retained derivatives from build `{info['MEA']['wheel']}`.",
        f"Disabling the MDEAH⁺–water association edges for the pure-water diagnostic produced {nw} exact-zero "
        f"derivatives and a maximum pressure change of {pressure:.2e} Pa. The {len(water['rows'])} pure-water "
        f"rows contribute {water['pure_water_cost']:.10g} to the {water['declared']}-row objective. "
        f"The stage variance uses {info['MDEA']['stage_denominator']} residual degrees of freedom.",
        '## Conditional uncertainty at the reported fits')
    mea_se, mdea_se = (100*(info[k]['SE_multiplier']-1) for k in ('MEA', 'MDEA'))
    n, (old_span, new_span), multiplier = band_stats()
    add(f"The stage variance increases conditional standard errors by {mea_se:.3f}% for MEA "
        f"and {mdea_se:.3f}% for MDEA. The MEA bands use nominal ±{multiplier:.2f} conditional standard "
        f"errors. For the {n} retained loaded partial pressures, relative standard errors span "
        f"{old_span} under the original convention and {new_span} under the stage convention.",
        '## MEA reweighting and paired comparisons')
    table(('Mapping', 'Original weights', 'Cai mean weights'),
          ([m.title()+' MEA', *fmt(totals[m, w] for w in ('original', 'Cai mean'))] for m in ('reported', 'alternative')))
    start_costs = ' and '.join(f"{v['cost']:.8f} ({v['start']})" for v in selection['starts'])
    add(f"The converged start families reached replayed objectives of {start_costs} with all {len(weights)} "
        f"fitted predictions available. The selected endpoint came from the {selection['selected']['start']} family.")
    table(('Coordinate', 'Unit', 'Reported', 'Alternative', 'Change', 'Bound before → after'),
          ([f"`{v['identity']}`", v['unit'], *fmt((v[k] for k in ('reported', 'alternative', 'change')), '.8g'),
            f"{v['reported_bound'] or 'interior'} → {v['alternative_bound'] or 'interior'}"] for v in cross['parameters']))
    species_row = groups[carbonate]['largest_change']
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
        carbonate: f"Fitted Böttinger {species_row['measured']} (linear aggregate of true liquid mole fractions)",
        'fitted Jakobsen ratio': 'Jakobsen fitted ratios',
        'Matin 19 pools': 'Matin unfitted pools',
        'Böttinger 353 K checks': f"Böttinger at {bot['temperature_K']} K",
        'fitted loaded density': 'Loaded density (kg/m³)',
        'fitted CO2-free density': 'Amundsen unloaded density (kg/m³)',
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
           for key, label in zip(search['alternative'], ('Main grid', 'Offset grid', 'Fixed-pressure census'), strict=True)))
    supplied = search['supplied']
    baseline = search['baseline']
    descents = sum(baseline[k]['descent'] for k in search['alternative'])
    incomplete = len(baseline['grid']['unavailable'])+len(baseline['offset']['unavailable'])+baseline['census']['incomplete']
    source_ranges = f.e.rows(paper.OUT/'reaction-source-ranges.csv')
    source = source_ranges[0]
    reactions = ', '.join(v['reaction'] for v in source_ranges)
    assert all(v['minimum_K']==source['minimum_K'] and v['maximum_K']==source['maximum_K'] for v in source_ranges)
    add(f"The reported mapping had {descents} descents and {incomplete} incomplete states across the same state sets. "
        f"The alternative census evaluated {supplied['evaluated']:,} supplied trials, with {supplied['negative']} "
        f"negative trials and {supplied['missing']} missing evaluations.",
        f"The retained source range for {reactions} is {source['minimum_K']}–{source['maximum_K']} K "
        f"({source['source'].split(', reactions')[0]}).",
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
