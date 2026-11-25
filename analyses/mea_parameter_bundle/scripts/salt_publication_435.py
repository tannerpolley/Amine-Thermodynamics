"""Read retained #435 records for the #429 manuscript quantities."""
import csv
from functools import cache
import gzip
import hashlib
import json
from math import exp, log, sqrt
from pathlib import Path
from statistics import fmean

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = 'analyses/mea_parameter_bundle/results/'
PAPER = BUNDLE + 'paper-evidence-341/'
F2 = BUNDLE + 'reduced-refit/evidence/F2/'
F2_PARAMETERS = PAPER + 'paper-evidence/reported-parameters.json'
READBACK = BUNDLE + 'salt-anchored-435/'
MEA = READBACK + 'MEA/F4/'
EVIDENCE = READBACK + 'MEA/evidence/F4/'
DEA = 'analyses/dea_transfer/results/refit-413/'
MDEA = 'analyses/mdea_mea_workflow/results/bounded-binary-411/'
AMP = 'analyses/amp_transfer/results/retransfer-412-f2-05e94210/'
KURANOV = MDEA.replace('bounded-binary-411', 'kuranov-published-422')
HONG = BUNDLE + 'same-data-comparison/hong-2027/'
OBJECTIVE = BUNDLE + 'objective-weights-420/'
REFERENCE = BUNDLE + 'reference-states-428/'
PHASE = MDEA.replace('bounded-binary-411', 'phase-search-421')
SHARED = MDEA.replace('bounded-binary-411', 'shared-bicarbonate-417')
C423 = (BUNDLE + 'shared-ion-electrostatics-423/'
        'c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb/'
        'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed/')
BANDS = BUNDLE + 'stripper-temperature-409/'
CURRENT = {'MEA': MEA, 'DEA': DEA.replace('refit-413', 'salt-anchored-435/campaign'),
           'MDEA': MDEA.replace('bounded-binary-411', 'salt-anchored-435/campaign'),
           'AMP': AMP.replace('retransfer-412-f2-05e94210', 'salt-anchored-435/free'),
           'AMP fixed': AMP.replace('retransfer-412-f2-05e94210', 'salt-anchored-435/fixed')}
DISPLAYS = 'docs/scientific/latex/scripts/'


@cache
def read(path):
    data = (ROOT / path).read_bytes()
    if path.endswith('.gz'):
        data = gzip.decompress(data)
    if path.removesuffix('.gz').endswith('.csv'):
        return list(csv.DictReader(data.decode().splitlines()))
    return json.loads(data)


def statistics(rows, prediction='predicted'):
    available = [(float(r['observed']), float(r[prediction])) for r in rows
                 if r[prediction] not in ('', None) and r['status'] == 'Available']
    relative = [(pred - obs) * 100 / obs for obs, pred in available if obs]
    return dict(n=len(rows), available=len(available), relative_n=len(relative),
                aard_percent=fmean(map(abs, relative)) if relative else None,
                bias_percent=fmean(relative) if relative else None,
                rmse=sqrt(fmean((pred-obs)**2 for obs, pred in available)) if available else None)


def publication_readback():
    """Reduce observations once, retaining cohort identities and effective models."""
    verification = read(READBACK + 'receiver-law-verification.json')
    models = {name: {k: model[k] for k in ('path', 'endpoint_json_sha256')}
              for name, model in verification['models'].items()}
    for name, base in CURRENT.items():
        identity = base + ('declaration.json' if name == 'MEA' else 'identity.json.gz')
        models['AMP free' if name == 'AMP' else name]['declaration'] = dict(
            path=identity, sha256=(hashlib.sha256((ROOT / identity).read_bytes()).hexdigest()
                                   if name == 'MEA' else read(identity)['declaration_sha256']))
    results = {}

    def record(key, case, source, field, unit, denominator, value):
        results[key] = dict(model=case, source=source, field=field, unit=unit,
                            denominator=denominator, value=value)

    def metrics(key, case, source, rows, field, unit, prediction='predicted'):
        for metric, value in statistics(rows, prediction).items():
            units = 'rows' if metric in ('n', 'available', 'relative_n') else (
                unit if metric == 'rmse' else '%')
            record(f'{key}/{metric}', case, source, f'{field}: {metric}', units,
                   [r.get('id') or r['identity'] for r in rows], value)

    fit = MEA + 'fit-summary.json'
    record('MEA/C', 'MEA', fit, 'cost', '1', '307 fitted observations at declared scales and weights',
           read(fit)['cost'])
    assert len(read(EVIDENCE + 'fitted-rows.csv')) == 307
    assert abs(sum(float(r['cost']) for r in read(EVIDENCE + 'fitted-rows.csv')) - read(fit)['cost']) < 1e-9
    record('MEA/fitted coordinates', 'MEA', fit, 'coordinates', 'count', 'adopted F4',
           len(read(fit)['coordinates']))
    record('MEA/active bounds', 'MEA', fit, 'active_bounds', 'count', 'adopted F4',
           len(read(fit)['active_bounds']))
    groups = {'fitted CO2 partial pressure': ('common149', 'PartialPressure', 'Pa'),
              'fitted species': ('common149|restored species', 'PhaseMoleFraction|mole_fraction', '1'),
              'fitted heat of absorption': ('common149', 'AdditionEnthalpy', 'J/mol CO2'),
              'Jakobsen ratio': ('Jakobsen', '', 'mol/mol total amine'),
              'Kiepe pressure': ('Kiepe', '', 'Pa'),
              'CO2-free density': ('CO2-free density', '', 'kg/m³'),
              'Cai temperature': ('Cai', 'temperature', 'K'),
              'Cai vapour water fraction': ('Cai', 'mole_fraction', '1'),
              'loaded density': ('loaded density', '', 'kg/m³'),
              'heat capacity': ('Cp', '', 'J/(mol apparent feed K)')}
    fitted = EVIDENCE + 'fitted-rows.csv'
    for group, (owner, quantity, unit) in groups.items():
        rows = [r for r in read(fitted) if r['group'] in owner.split('|') and
                (not quantity or r['quantity'] in quantity.split('|'))]
        assert rows, group
        metrics(f'MEA/{group}', 'MEA', fitted, rows, f'group={owner}, quantity={quantity or "all"}', unit)
    pressure = EVIDENCE + 'canonical-pressure.csv'
    fit_ids = {r['id'] for r in read(fitted) if r['quantity'] == 'PartialPressure'}
    all_pressure = read(pressure)
    assert sum(r['target'] in fit_ids for r in all_pressure) == 47
    metrics('MEA/six sources', 'MEA', pressure, all_pressure, 'all nominal 30 wt% rows', 'Pa')
    metrics('MEA/six sources outside fit', 'MEA', pressure,
            [r for r in all_pressure if r['target'] not in fit_ids], 'exclude fitted PartialPressure identities', 'Pa')
    for source in sorted({r['source'] for r in all_pressure}):
        metrics(f'MEA/source/{source}', 'MEA', pressure, [r for r in all_pressure if r['source'] == source],
                f'source={source}', 'Pa')
    composition = {r['observation_id']: float(r['MEA_weight_fraction'])
                   for r in read('data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')
                   if r['MEA_weight_fraction']}
    for dataset, filename in [('Wagner', 'wagner-pressure.csv'), ('transfer', 'transfer.csv')]:
        path = EVIDENCE + filename
        rows = read(path)
        if dataset == 'Wagner':
            metrics('MEA/Wagner', 'MEA', path, rows, 'all Wagner rows', 'Pa')
        else:
            for content in (15, 45):
                subset = [r for r in rows if composition[r['target'].removesuffix('-pco2')] == content / 100]
                if subset:
                    metrics(f'MEA/Aronu {content} wt%', 'MEA', path, subset, f'{content} wt% Aronu', 'Pa')
    species = EVIDENCE + 'species-figure-data.csv'
    rows = list({r['target']: dict(r, id=r['target']) for r in read(species)}.values())
    assert len(rows) == 131 and sum(r['id'] in {q['id'] for q in read(fitted)} for r in rows) == 101
    metrics('MEA/all species', 'MEA', species, rows, 'all distinct species target IDs', '1')
    for key, parts in {
        'all outside-fit pressures': [
            [r for r in all_pressure if r['target'] not in fit_ids], read(EVIDENCE + 'transfer.csv'),
            read(EVIDENCE + 'wagner-pressure.csv')]}.items():
        rows = [r for part in parts for r in part]
        assert len(rows) == 205
        metrics(f'MEA/{key}', 'MEA', pressure, rows,
                'canonical-pressure except fitted; all transfer.csv and wagner-pressure.csv', 'Pa')
    path = EVIDENCE + 'carbonate-share.csv'
    ratios = [float(r['calc_over_obs']) for r in read(path)]
    for metric, value in {'geometric mean': exp(fmean(map(log, ratios))), 'minimum': min(ratios),
                          'maximum': max(ratios), 'aard_percent': 100 * fmean(abs(x-1) for x in ratios),
                          'n': len(ratios)}.items():
        record(f'MEA/carbonate share/{metric}', 'MEA', path, f'calc_over_obs: {metric}',
               '%' if metric == 'aard_percent' else '1', [r['id'] for r in read(path)], value)

    source = MEA + 'objective-contributions.csv'
    for label, observable in [('temperature', 'temperature'), ("vapour water fraction", "['water']")]:
        row, = [r for r in read(source) if r['group'] == 'Cai' and r['observable'] == observable]
        record(f'MEA/Cai {label} objective cost', 'MEA', source, f'Cai/{observable}.cost', '1', int(row['n']), float(row['cost']))
    for group in ('Cai', 'Kiepe'):
        rows = [r for r in read(source) if r['group'] == group]
        cost = sum(float(r['cost']) for r in rows)
        record(f'MEA/{group} objective cost', 'MEA', source, f'{group}: sum(cost)', '1',
               f'{sum(int(r["n"]) for r in rows)} objective rows', cost)
        record(f'MEA/{group} objective share', 'MEA', source, f'{group}: 100 × sum(cost) / fit-summary.cost',
               '%', 'MEA/C', 100 * cost / read(fit)['cost'])
    onset = CURRENT['MDEA'] + 'binary-onset.json'
    for pressure, row in read(onset)['result']['pressures'].items():
        bracket, = row['brackets']
        assert bracket['resolved']
        for location, value in enumerate(bracket['bracket_K']):
            record(f'MDEA/{pressure.removesuffix(".json")}/onset/{location}', 'MDEA', onset,
                   f'result.pressures[{pressure}].brackets[0].bracket_K[{location}]', 'K',
                   f'{pressure.removesuffix(".json").removeprefix("binary-")} Pa; matched coarse and refined binary grids', value)
    source = MEA + 'search-summary.json'
    search = read(source)
    for group, keys in [('liquid', ('grid', 'offset')), ('liquid–vapor', ('census',)),
                        ('all', ('grid', 'offset', 'census'))]:
        n = sum(search[k]['states'] for k in keys)
        done = sum(search[k].get('available', search[k]['states'] - search[k].get('incomplete', 0)) for k in keys)
        for field, value in [('states', n), ('incomplete', n-done), ('descent', sum(search[k]['descent'] for k in keys))]:
            record(f'MEA/search/{group}/{field}', 'MEA', source, ' + '.join(keys) + f': {field}', 'states', n, value)
    path = MEA + 'reference-state.json'
    state = read(path)
    for field, unit in {'T_K': 'K', 'P_Pa': 'Pa', 'MEA_wt_percent': 'wt%', 'added_CO2_mol': 'mol',
                        'loading_initial': 'mol/mol', 'loading_final': 'mol/mol', 'loaded_mass_kg': 'kg',
                        'heat_kJ_mol': 'kJ/mol added CO2', 'cp_J_mol_K': 'J/(mol feed K)',
                        'cp_kJ_kg_K': 'kJ/(kg solution K)', 'cp_minus_fine_J_mol_K': 'J/(mol feed K)'}.items():
        record(f'MEA/worked state/{field}', 'MEA', path, field, unit, '313.15 K, 1.734 MPa, 30 wt% MEA, α=0.31',
               state[field])
    for i, reaction in enumerate(state['reactions']):
        for field in ('P_source_Pa', 'ln_K_source', 'Gamma', 'source_kJ_mol', 'fugacity_kJ_mol', 'ideal_gas_kJ_mol'):
            unit = 'Pa' if field.endswith('_Pa') else 'kJ/mol reaction' if field.endswith('_kJ_mol') else '1'
            record(f'MEA/worked state/{reaction["name"]}/{field}', 'MEA', path, f'reactions[{i}].{field}', unit,
                   '313.15 K, 1.734 MPa, 30 wt% MEA, α=0.31', reaction[field])
    for case in CURRENT:
        base = CURRENT[case]
        name = 'AMP free' if case == 'AMP' else case
        if case != 'MEA':
            source = base + 'selection.json.gz'
            selection = read(source)
            endpoint = selection['chosen'] if case == 'DEA' else selection
            n = len([r for r in read(base + 'data-rows.json.gz') if r['role'] == 'fitted'])
            assert n == {'DEA': 80, 'MDEA': 281, 'AMP': 214, 'AMP fixed': 214}[case]
            record(f'{case}/C', name, source, 'chosen.cost' if case == 'DEA' else 'cost', '1', n, endpoint['cost'])
            record(f'{case}/fitted rows', name, base + 'data-rows.json.gz', 'role=fitted', 'rows', n, n)
            for field in ('slope_K',):
                if field in endpoint:
                    record(f'{case}/{field}', name, source, field, 'K', n, endpoint[field])
            data = base + 'data-rows.json.gz'
            subsets = {}
            for row in read(data):
                subsets.setdefault((row['group'], row['role'], row['unit']), []).append(row)
            pressure_groups = {
                'DEA': [('fitted loaded', ['Lawson'], 'fitted'), ('outside partial', ['SeoHong', 'Lal', 'Lawson-394K'], 'not fitted')],
                'MDEA': [('fitted loaded', ['Kuranov'], 'fitted'), ('outside total', ['corrected-Kamps', 'Kuranov-413K', 'Sedighi'], 'not fitted'),
                         ('outside partial', ['Ermatchkov', 'Xiao'], 'not fitted')],
                'AMP': [('fitted total pressure', ['loaded-pressure', 'hartono-2021-supplemental', 'tong'], 'fitted'),
                        ('outside total', ['tong-baseline'], 'not fitted'), ('outside partial', ['kundu'], 'not fitted')],
            }
            for label, selected, role in pressure_groups.get(case, []):
                rows = [r for group in selected for r in subsets.get((group, role, 'Pa'), [])]
                if rows:
                    metrics(f'{case}/{label}', name, data, rows, f'group={selected}, role={role}, unit=Pa', 'Pa', 'value')
            if case in pressure_groups:
                rows = [r for (group, role, unit), subset in subsets.items()
                        if role == 'fitted' and unit == 'Pa' for r in subset]
                metrics(f'{case}/all fitted pressures', name, data, rows, 'role=fitted, unit=Pa', 'Pa', 'value')
            for (group, role, unit), rows in subsets.items():
                metrics(f'{case}/{group}/{role}/{unit}', name, data, rows,
                        f'group={group}, role={role}, unit={unit}', unit, 'value')
        source = base + ('objective-information.json.gz' if case == 'MEA' else f'{case.split()[0]}/information.json.gz')
        audit = read(source)['result']
        for field in ('n', 'na', 'p', 'denominator', 'stage_denominator', 'stage_variance', 'variance', 'SE_multiplier'):
            record(f'{case}/information/{field}', name, source, f'result.{field}', '1',
                   f'{audit["na"]} responsive rows; {audit["p"]} interior coordinates', audit[field])
    outside = {
        'MEA': [],
        'DEA': [f'DEA/{g}/not fitted/Pa/aard_percent' for g in ('SeoHong', 'Lal', 'Lawson-394K')],
        'MDEA': [f'MDEA/{g}/not fitted/Pa/aard_percent' for g in
                 ('corrected-Kamps', 'Kuranov-413K', 'Sedighi', 'Ermatchkov', 'Xiao')],
        'AMP': ['AMP/kundu/not fitted/Pa/aard_percent'],
    }
    # MEA needs only the outside-fit portion of each six-source cohort here.
    for group in sorted({r['source'] for r in all_pressure}):
        cohort = [r for r in all_pressure if r['source'] == group and r['target'] not in fit_ids]
        if cohort:
            key = f'MEA/outside fit/{group}'
            metrics(key, 'MEA', pressure, cohort, 'source subset excluding fitted identity', 'Pa')
            outside['MEA'].append(key + '/aard_percent')
    outside['MEA'] += ['MEA/Wagner/aard_percent', 'MEA/Aronu 15 wt%/aard_percent', 'MEA/Aronu 45 wt%/aard_percent']
    outside_keys = [k for group in outside.values() for k in group]
    extrema = {name: f(outside_keys, key=lambda k: results[k]['value']) for name, f in [('minimum', min), ('maximum', max)]}
    for name, key in extrema.items():
        results[f'Across amines/outside loaded pressure AARD/{name}'] = results[key] | dict(denominator=outside_keys)
    path = MEA + 'bands.json'
    for i, row in enumerate(read(path)['result']):
        key = f'MEA/temperature bands/{row["property"]}/{row["band"]}/{row["role"]}'
        for field, unit in [('n', 'rows'), ('T_min_K', 'K'), ('T_max_K', 'K'), ('AARD_percent', '%'),
                            ('mean_signed_relative_percent', '%')]:
            record(f'{key}/{field}', 'MEA', path, f'result[{i}].{field}', unit, row['n'], row[field])

    path = MEA + 'uncertainty/prediction-bands.csv'
    pressure_bands = [r for r in read(path) if r['group'] == 'common149: partial_pressure']
    assert len(pressure_bands) == 47
    multiplier = results['MEA/information/SE_multiplier']['value']
    errors = [100 * float(r['SE_bound_fixed']) * multiplier / float(r['value']) for r in pressure_bands]
    for name, value in [('minimum', min(errors)), ('maximum', max(errors))]:
        record(f'MEA/pressure SE/{name}', 'MEA', path,
               f'{name}(100 × SE_bound_fixed × SE_multiplier / value)', '%',
               [r['identity'] for r in pressure_bands], value)
    path = READBACK + 'MEA/baygi-matched-pressure.json'
    row = read(path)
    record('MEA/Baygi/aard_percent', 'MEA', path, 'aard_percent.salt_anchored_Pa', '%', row['n'],
           row['aard_percent']['salt_anchored_Pa'])
    for kind, groups in read(READBACK + 'MEA/hong-matched-pressure.json')['grouped'].items():
        for group, values in groups.items():
            row = values['salt_anchored']
            record(f'MEA/Hong/{kind}/{group}/aard_percent', 'MEA', READBACK + 'MEA/hong-matched-pressure.json',
                   f'grouped.{kind}.{group}.salt_anchored.aard_percent', '%', row['available'], row['aard_percent'])
    density_file = EVIDENCE + 'density.csv'
    heat_file = EVIDENCE + 'kim2007-heat-pathways/kim-heat.csv'
    for block, n in [('Amundsen2009', 18), ('Hartono2014', 25), ('Han2012', 45),
                     ('Kim 313.15 K', 21), ('Kim 353.15 K', 20), ('Kim 393.15 K', 15)]:
        match = [row for row in read(HONG + block + '.csv') if row['three_model_eligible'] == 'True']
        is_heat = block.startswith('Kim')
        new_path = heat_file if is_heat else density_file
        new = {r['record_id' if is_heat else 'id']: r for r in read(new_path)}
        assert len(match) == n
        matched = [new[r['record_id']] for r in match]
        rows = []
        for comparator, item in zip(match, matched, strict=True):
            obs = item['observed' if is_heat else 'observed_kg_m3']
            value = item['predicted' if is_heat else 'predicted_kg_m3']
            status = ('Available' if item['interval_status'] == 'available' else item['interval_status']) if is_heat else item['status']
            assert abs(float(obs)-float(comparator['observed'])) < 1e-9
            if is_heat:
                assert abs(float(item['previous_loading']) - float(comparator['previous_loading'])) < 1e-9
            rows.append(dict(id=comparator['record_id'], observed=obs, predicted=value, status=status))
        metrics(f'MEA/Hong/{block}', 'MEA', new_path, rows,
                f'three_model_eligible identities in {HONG + block + ".csv"}',
                'kJ/mol CO2' if is_heat else 'kg/m³')

    selection = read(CURRENT['DEA'] + 'selection.json.gz')
    ordered = sorted(selection['candidates'], key=lambda row: row['cost'])
    best = ordered[0]['cost']
    declaration = 'analyses/dea_transfer/inputs/part-ii-346/f2-carbamate-413-route.json'
    tolerance = read(declaration)['optimizer']['function_tolerance']
    delta = ordered[1]['cost'] - best
    absolute = [row['name'] for row in selection['candidates'] if abs(row['cost']-best) <= tolerance]
    relative = [row['name'] for row in selection['candidates'] if abs(row['cost']-best) <= tolerance*abs(best)]
    assert absolute == relative == selection['ties'] and ordered[0]['name'] == selection['chosen']['name'] == 'start-1'
    tie = dict(selection=CURRENT['DEA'] + 'selection.json.gz', candidate_costs={x['name']: x['cost'] for x in ordered},
               chosen=ordered[0]['name'], declaration=declaration, absolute_delta=delta, absolute_tolerance=tolerance,
               old_relative_threshold=tolerance*abs(best), ties=absolute, old_relative_ties=relative)
    return {'wheel_sha256': verification['wheel'], 'models': models, 'quantities': results,
            'DEA absolute tie check': tie}


# The row label, column heading and source selector identify the quantity. Tables
# with mixed ownership (literature, design inputs and current outputs) split here.
FINAL = DISPLAYS + 'final_rerun_tables.py'
TRANSFER = DISPLAYS + 'dea_displays.py'
RETAINED = 'retained #435'
CARRIED = 'unchanged'
HISTORICAL = 'historical'
OPEN = 'must be recomputed'
EXCLUDED = 'excluded'


def carried(source, field, reason):
    return dict(old_source=source, old_field=field, disposition=CARRIED, note=reason)


def historical(source, field):
    return dict(old_source=source, old_field=field, disposition=HISTORICAL,
                note='Keep the comparison with its original declaration, rows and trial protocol.')


def current(source, field, key):
    return dict(old_source=source, old_field=field, disposition=RETAINED, quantity=key)


def pending(source, field, producer, minutes, reason):
    return dict(old_source=source, old_field=field, disposition=OPEN, producer=producer,
                estimated_cost=minutes, note=reason)


def bound(source, field, target, selector, note=''):
    return dict(old_source=source, old_field=field, disposition=RETAINED,
                record=target, record_field=selector, note=note)


def table_quantity(name, line, column, block, row, heading, position):
    field = f'{block}: {row} / {heading}' if block else f'{row} / {heading}'
    case = next((case for case in ('DEA', 'MDEA', 'AMP') if block.startswith(case)), '')
    old = {'DEA': DEA, 'MDEA': MDEA, 'AMP': AMP + 'slope-150/'}
    case_path = old.get(case, '')
    old_data = DEA + 'paper-data.csv' if case == 'DEA' else case_path + 'data-rows.json'
    if name in ('reaction_equilibrium_constants', 'supplement_reaction_coefficients'):
        return carried(BUNDLE + 'adoption-297/paper-evidence/source-only/chemical_reaction_source_contract.json',
                       field, 'Fixed source correlations and stoichiometry are independent of the new interaction laws.')
    if name == 'mdea-shared-control':
        return historical(SHARED + 'profile.json.gz; ' + SHARED + 'mdea-comparison.json.gz; ' +
                          SHARED + 'mdea-search-readback.json', field)
    if name == 'choice_cost':
        return historical(BUNDLE + 'reduced-refit/fit-comparison.csv; ' + BUNDLE + 'reduced-refit/agreement.csv', field)
    if name == 'bound_profiles':
        return historical(PAPER + 'uncertainty/profiles.json', field)
    if name == 'amp_reference_state':
        return historical(REFERENCE + 'amp.json; ' + REFERENCE + 'tables.json', field)
    if name == 'dea-binary-tradeoff':
        return historical(DEA.replace('refit-413', 'reactive-refit-425') + 'comparisons.json', 'tableS10/table7: ' + field)
    if name == 'calibration-data':
        source = old_data if case else PAPER + 'objective-declarations.json'
        if case == 'AMP':
            return bound(source, field, CURRENT['AMP'] + 'data-rows.json.gz',
                         'role and source membership (Hartono + Tong added to fitted total pressures)',
                         'Rebuild fitted and comparison memberships for the expanded AMP declaration.')
        return carried(source, field, 'Observation identities and input conditions do not depend on the shared laws.')
    if name in ('mea_data', 'supplement_mea_comparison'):
        source = PAPER + 'same-data-comparison/part1-scores.json'
        if column in (1, 2, 5, 6, 7):
            return carried(source, field, 'Source membership and the predictions of the separately published model carry forward.')
        group = {36: 'fitted CO2 partial pressure', 37: 'fitted species', 38: 'fitted heat of absorption',
                 39: 'Jakobsen ratio', 40: 'Kiepe pressure', 41: 'CO2-free density', 42: 'Cai temperature',
                 43: 'Cai vapour water fraction', 44: 'loaded density', 45: 'heat capacity',
                 47: 'six sources', 48: 'six sources outside fit', 50: 'Wagner'}
        if name == 'mea_data' and line in group and column in (3, 4):
            record = current(PAPER + 'paper-evidence/fitted-rows.csv' if line < 46 else source, field,
                             f'MEA/{group[line]}/' + ('aard_percent' if column == 3 else 'rmse'))
            if line == 38 and column == 4:
                record['note'] = 'Divide retained J/mol by 1000 for the printed kJ/mol.'
            return record
        if name == 'supplement_mea_comparison' and line == 35 and column == 3:
            return current(source, field, 'MEA/carbonate share/aard_percent')
        if name == 'mea_data' and line in (51, 52):
            return current(source, field, f'MEA/Aronu {15 if line == 51 else 45} wt%/aard_percent')
        if name == 'mea_data' and line == 49:
            return current(source, field, 'MEA/all species/rmse')
        target = ('heat.csv' if line == 36 else 'density.csv' if 37 <= line <= 40
                  else 'heat-capacity-264.json' if 41 <= line <= 43 else 'kim2007-heat-pathways/summary.json')
        return bound(source, field, EVIDENCE + target, 'Select by source, composition, state and property in row label')
    if name == 'pressure_sources':
        if column == 0:
            return carried(F2 + 'canonical-pressure.csv', field, 'Nominal solvent composition for source comparison.')
        group = next(s for s in ('Aronu2011', 'Hilliard2008', 'Idris2014', 'Jou1995', 'Mamun2005', 'Xu2011')
                     if s.lower()[:3] in row.lower() or (s == 'Mamun2005' and "Ma'mun" in row))
        return current(F2 + 'canonical-pressure.csv', field, f'MEA/source/{group}/' + ('n' if column == 1 else 'aard_percent'))
    if name == 'objective_groups':
        if column in (1, 2, 3):
            return carried(PAPER + 'objective-groups.csv', field, 'The MEA objective keeps all observation weights and scales.')
        return bound(PAPER + 'objective-groups.csv', field, MEA + 'objective-contributions.csv',
                     'Sum cost by group and quantity; combine common149 mole fractions with restored species.')
    if name == 'kim_alternatives':
        return bound(F2 + 'kim2007-heat-pathways/summary.json', field, EVIDENCE + 'kim2007-heat-pathways/summary.json',
                     'temperatures.393.15.metrics.semi_differential[all_printed|source_consistent|without_first120], then n/rmse/aard_percent')
    if name == 'supplement_check_values':
        return bound(PAPER + 'check-values.json', field, MEA + 'check-values.json',
                     'group=Kiepe (CO2–water), Cai (MEA–water), common149 (loaded MEA); T_K or answers[0] by row',
                     'Compare printed_digits_agree and retain both initial-pressure runs.')
    if name == 'mea_reference_state':
        fields = ['T_K', 'P_Pa', 'MEA_wt_percent', 'loading_initial', 'loading_final', 'apparent_feed_mol[MEA]',
                  'apparent_feed_mol[water]', 'added_CO2_mol', 'loaded_mass_kg', 'points.initial.H_J',
                  'points.loaded.H_J', 'added_stream.H_J_per_mol', 'heat_kJ_mol', 'cp_J_mol_K',
                  'cp_stencil_J_mol_K[0]', 'cp_stencil_J_mol_K[1]', 'cp_minus_fine_J_mol_K', 'cp_kJ_kg_K']
        reaction_fields = ['P_source_Pa', 'ln_K_source', 'Gamma', 'source_kJ_mol', 'fugacity_kJ_mol', 'ideal_gas_kJ_mol']
        if 10 <= line <= 27 and column == 1 and '/' not in fields[line-10]:
            key = fields[line-10]
            return bound(REFERENCE + 'mea.json', key, MEA + 'reference-state.json', key)
        if 29 <= line <= 34 and column > 0:
            return current(REFERENCE + 'mea.json', f'reactions[{column-1}].{reaction_fields[line-29]}',
                           f'MEA/worked state/R{column}/{reaction_fields[line-29]}')
        return carried(REFERENCE + 'tables.json', field, 'State definitions and column labels are fixed.')
    if name == 'supplement_correlations':
        return bound(OBJECTIVE + 'MEA/information.json.gz', field, MEA + 'objective-information.json.gz',
                     'result.conditional_correlation, with interior identities in result.coordinates',
                     'Rebuild both headers and matrix after excluding active bounds.')
    if name == 'supplement_fitted_parameters':
        return bound(BUNDLE + 'reduced-refit/parameter-details.csv; ' + OBJECTIVE + 'MEA/information.json.gz',
                     field, MEA + 'objective-information.json.gz', 'result.coordinates matched by parameter identity',
                     'Replace the table with the F4 coordinates and responsive-row standard errors.')
    if name in ('interaction_matrix', 'supplement_interaction_matrix', 'species_parameters',
                'supplement_species_parameters', 'supplement_shared_remaining'):
        return bound(F2_PARAMETERS, field, MEA + 'parameters.json',
                     f'Effective parameter coefficients: {row} / {heading}',
                     'Use the coefficient unit and equation in the declaration. Water–anion a1 is per K in the linear-T law.')
    if name in ('supplement-dea-ranges', 'supplement-mdea-ranges', 'supplement-amp-ranges'):
        case = name.split('-')[1].upper()
        source = DEA + 'range-deviations.csv' if case == 'DEA' else (
            MDEA if case == 'MDEA' else AMP + 'slope-150/') + ('deviations.json' if case == 'MDEA' else 'data-rows.json')
        return bound(source, field, CURRENT[case] + 'deviations.json.gz',
                     f'{row}: group/role and range_name/outside_range from {heading}; statistics.relative_rows and AARD_percent')
    if name == 'supplement-transfer-data':
        if column in (3, 4, 5, 6) and case != 'AMP':
            return carried(old_data, field, 'Source observation counts and state inputs are fixed.')
        return bound(old_data if case else TRANSFER, field,
                     CURRENT.get(case, CURRENT['AMP']) + 'data-rows.json.gz',
                     'Filter group, role and unit, then use source inputs or available nonzero relative residuals as indicated.')
    if name in ('transfer-fitted', 'supplement-transfer-bounds', 'supplement-transfer-parameters',
                'transfer-species'):
        if not case:
            case = 'MDEA' if 'MDEA' in row else 'DEA' if 'DEA' in row else 'AMP'
            case_path = old[case]
        if 'enthalpy increment' in row or ('ln K' in row and case in ('DEA', 'AMP')):
            return bound(case_path.split('results/')[0] + 'results/r4-shift-426/table6.json', field,
                         CURRENT[case].rsplit('/', 2)[0] + '/hydrolysis/shift.json',
                         'delta_h_J_mol, conditional_SE_h_J_mol, bounds or temperatures at 313.15 K')
        target = (CURRENT[case] + f'{case}/information.json.gz' if name in ('transfer-fitted', 'supplement-transfer-bounds')
                  else CURRENT[case] + 'selection.json.gz')
        selector = 'result.coordinates by parameter identity' if 'information.json' in target else (
            'chosen.parameters.parameters' if case == 'DEA' else 'point.parameters')
        return bound(case_path + {'DEA': 'parameter-values.csv', 'MDEA': 'parameter-table.json', 'AMP': 'parameters.json'}[case], field,
                     target, selector + f': {row}; {heading}')
    if name == 'supplement-carbonate-sensitivity':
        if 'MEA model' == row and column in (1, 2):
            return current(C423 + 'P0/carbonate-share.json', field,
                           'MEA/carbonate share/' + ('geometric mean' if column == 1 else 'aard_percent'))
        return historical(C423 + 'refit-comparison.json; ' + C423 + '*/carbonate-share.json', field)
    if name == 'supplement-hong-comparison':
        if column == 5:
            key = {5: 'canonical/strict_grid', 6: 'canonical/all', 7: 'wagner/all'}.get(line)
            if key:
                return current(HONG + 'supplement-table.csv', field, f'MEA/Hong/{key}/aard_percent')
            block = {9: 'Kim 313.15 K', 10: 'Kim 353.15 K', 11: 'Kim 393.15 K',
                     13: 'Amundsen2009', 14: 'Hartono2014', 15: 'Han2012'}[line]
            return current(HONG + 'supplement-table.csv', f'{block}, subset=all, adopted', f'MEA/Hong/{block}/rmse')
        return carried(HONG + 'supplement-table.csv', field, 'The Hong and Polley–Hedengren records and shared observation subsets are fixed.')
    if name == 'published-models':
        if '16-parameter' in row:
            return historical(PAPER + 'same-data-comparison/published-deviations.json', field)
        if 'This work' in row and column == 2:
            if line == 9:
                return bound(BUNDLE + 'same-data-comparison/matched-pressure-rows.csv', field,
                             READBACK + 'MEA/baygi-matched-pressure.json', 'aard_percent.salt_anchored_Pa; n=19')
            if line == 24:
                return bound(KURANOV + 'statistics.json', field,
                             CURRENT['MDEA'].rsplit('/', 2)[0] + '/kuranov-matched-pressure.json.gz',
                             'grouped.K82 (retain row identities and availability)')
            group = 'Ermatchkov' if line == 14 else 'corrected-Kamps'
            return current(MDEA + 'published-pressure-comparisons.json', field,
                           f'MDEA/{group}/not fitted/Pa/aard_percent')
        return carried(KURANOV + 'statistics.json; ' + PAPER + 'same-data-comparison/published-deviations.json', field,
                       'Cited literature statistic or retained matched-cohort design.')
    if name == 'supplement-temperature-bands':
        prop = {r'\COtwo partial pressure': 'CO2 partial pressure', 'Absorption heat': 'heat of absorption',
                'Heat capacity': 'heat capacity', 'Density': 'density'}.get(row)
        if prop and line in range(4, 20):
            band = 'stripper' if line in (7, 10, 11, 15, 19) else 'intermediate' if line in (14, 18) else 'absorber'
            role = ('fitted' if line in (4, 8, 12, 16) else 'not fitted, 15/45 wt%' if line == 6 else
                    'not fitted, source-flagged' if line == 11 else 'not fitted')
            metric = {1: 'T_min_K' if position == 0 else 'T_max_K', 3: 'n', 4: 'AARD_percent',
                      5: 'mean_signed_relative_percent'}.get(column)
            if metric:
                return current(BANDS + 'band-table.csv', field, f'MEA/temperature bands/{prop}/{band}/{role}/{metric}')
        return carried(BANDS + 'band-table.csv', field, 'Fixed source selection and temperature-band definitions.')
    if name == 'amine-summary':
        if row not in CURRENT:
            if 'Tong' in row:
                return bound(TRANSFER, 'Pressure comparison membership and notes',
                             CURRENT['AMP'] + 'data-rows.json.gz', 'Tong unloaded total pressures, 5 outside fit')
            return carried(TRANSFER, field, 'Definition of pressure columns and observation roles.')
        case = row
        source = {'MEA': F2 + 'summary.json', 'DEA': DEA + 'paper-summary.json',
                  'MDEA': MDEA + 'summary-row.json', 'AMP': AMP + 'slope-150/confirmation.json'}[case]
        if case == 'MEA' and column in (1, 2, 6, 7):
            key = {1: 'fitted coordinates', 2: 'active bounds', 6: 'search/all/states', 7: 'search/all/incomplete'}[column]
            return current(source, field, 'MEA/' + key)
        if column >= 6:
            file = {'MEA': 'search-summary.json', 'DEA': 'selection.json.gz', 'MDEA': 'search-outcome.json.gz',
                    'AMP': 'native/search-outcome.json.gz'}[case]
            return bound(source, field, CURRENT[case] + file,
                         'States, available/incomplete and confirmed splits; keep native and supplied protocols separate.')
        if column <= 2:
            return bound(source, field, CURRENT[case] + f'{case}/information.json.gz',
                         'result.coordinates and result.active_bounds')
        groups = {
            'MEA': ['fitted CO2 partial pressure', 'fitted CO2 partial pressure', 'all outside-fit pressures', 'all outside-fit pressures'],
            'DEA': ['fitted loaded', 'all fitted pressures', 'outside partial', 'outside partial'],
            'MDEA': ['fitted loaded', 'all fitted pressures', 'outside total', 'outside partial'],
            'AMP': ['fitted total pressure', 'all fitted pressures', 'outside total', 'outside partial'],
        }
        group = groups[case][column-3 + (column == 5 and position > 1)]
        return current(source, field, f'{case}/{group}/' + ('aard_percent' if position % 2 == 0 else 'n'))
    raise ValueError(f'No quantity rule for table {name}: {field}')


def prose_quantity(name, line, index, token, sentence):
    """Bind the quantities in the pinned prose; index is within the printed statement."""
    field = f'Printed statement at line {line}, quantity {index+1}'
    if name == 'data_code_availability':
        return bound(F2 + 'summary.json', 'engine', READBACK + 'receiver-law-verification.json', 'wheel')
    if name in ('chemistry_macros', 'epc_saft_equation_of_state', 'nomenclature'):
        return carried(F2_PARAMETERS, field,
                       'Chemical identity, fixed EoS coefficient, or source/model convention; see cited equation on this line.')
    if name == 'acknowledgements':
        return dict(disposition=EXCLUDED, note='Funding and acknowledgement identifiers.')
    if name == 'graphical_abstract':
        case = {17: 'MEA', 18: 'DEA', 19: 'MDEA', 20: 'AMP'}.get(line)
        if case:
            if index == 0:
                if case == 'MEA':
                    return current(F2_PARAMETERS, 'number of fitted coordinates', 'MEA/fitted coordinates')
                return bound(TRANSFER, 'number of fitted coordinates', CURRENT[case] + f'{case}/information.json.gz',
                             'len(result.coordinates)')
            if index == 1:
                key = dict(MEA='MEA/fitted CO2 partial pressure/aard_percent', DEA='DEA/Lawson/fitted/Pa/aard_percent',
                           MDEA='MDEA/Kuranov/fitted/Pa/aard_percent', AMP='AMP/fitted total pressure/aard_percent')[case]
                return current(FINAL if case == 'MEA' else TRANSFER, 'fitted loaded pressure AARD', key)
            return carried(MDEA + 'critical-k.json', 'reference pressure', 'The CO2-free bound keeps its reference pressure.')
    if name in ('main', 'conclusion', 'introduction', 'chemrxiv', 'cover_letter', 'highlights'):
        if any(x in sentence for x in ('10.3', '10.5', '73 ', '666')):
            return historical(AMP + 'main/phase-classification-1.json.gz; ' + AMP + 'slope-150/confirmation.json',
                              'Original 47-row AMP free/fixed comparison, ' + field)
        if '0.1325' in sentence or '33.6' in sentence:
            return historical(SHARED + 'mdea-comparison.json.gz; ' + SHARED + 'mdea-search-readback.json', field)
        key = {'11.6': 'MEA/fitted CO2 partial pressure/aard_percent', '2646': 'MEA/search/all/states',
               '28.5': 'DEA/Lawson/fitted/Pa/aard_percent', '20.1': 'MDEA/Kuranov/fitted/Pa/aard_percent'}.get(token)
        if key:
            return current(FINAL if key.startswith('MEA') else TRANSFER, 'Summary: ' + key.partition('/')[2], key)
        if name == 'conclusion' and line == 13:
            return current(F2_PARAMETERS, 'fitted coordinates or pressure observations',
                           'MEA/fitted coordinates' if token == '11' else 'MEA/fitted CO2 partial pressure/n')
        if token == '3' and name == 'introduction' and line == 43:
            return bound(F2 + 'fitted-rows.csv', 'upper deviation assertion over caloric and density cohorts',
                         MEA + 'fit-summary.json', 'metrics for fitted heat, Cp and both density groups',
                         'Review the claim against the new individual group AARDs.')
        return carried(TRANSFER, field, 'Chemical name, source conditions, or retained observation design.')
    if name == 'data_methods':
        if line == 9:
            if token == '156':
                return current(AMP + 'slope-150/data-rows.json', 'fitted AMP row count', 'AMP/fitted rows')
            return carried(TRANSFER, 'MEA, DEA and MDEA objective membership', 'Same fitted rows and cohort definitions.')
        if line in (18, 48, 49, 127):
            return bound(AMP + 'slope-150/data-rows.json', field, CURRENT['AMP'] + 'selection.json.gz',
                         'point.coordinates, slope_K; role and group from data-rows.json.gz')
        if line in (46, 60, 61):
            key = ('MEA/Kiepe objective cost' if token == '0.0007' else
                   {'150.76': 'MEA/C', '60.8': 'MEA/Cai objective share'}.get(token))
            if key:
                return current(OBJECTIVE + 'MEA/contributions.csv', 'Cai share or objective on primary weights' if line == 61
                               else 'Kiepe cost', key)
        if line in (62, 68, 72, 73, 110, 113, 114, 115, 121):
            return historical(OBJECTIVE + 'alternative/' if line == 62 else BUNDLE + 'reduced-refit/F2/',
                              'Alternative weighting or earlier MEA calibration, ' + field)
        if line == 66:
            return historical(DEA + 'selection.json', 'Two-start #413 comparison; abs(ΔC) ≤ 1e-10, ' + field)
        if line == 67:
            return current(F2_PARAMETERS, 'fitted coordinate count', 'MEA/fitted coordinates')
        if line in (91, 92):
            keys = {'268': 'MEA/information/na', '258': 'MEA/information/stage_denominator',
                    '278': 'MDEA/information/na', '272': 'MDEA/information/stage_denominator'}
            if token in keys:
                return current(OBJECTIVE, keys[token], keys[token])
            if line == 92:
                case = 'MEA' if index == 0 else 'MDEA'
                return bound(OBJECTIVE + f'{case}/information.json.gz', '100 × (SE_multiplier − 1)',
                             CURRENT[case] + ('objective-information.json.gz' if case == 'MEA' else 'MDEA/information.json.gz'),
                             '100 × (result.SE_multiplier − 1)')
        if line == 124:
            return bound(MDEA + 'comparison.json', 'k_versus_critical', CURRENT['MDEA'] + 'selection.json.gz',
                         'binary.hull; compare all tested onset temperatures')
        return carried(PAPER + 'objective-declarations.json' if line < 93 else MDEA + 'critical-k.json', field,
                       'Stated objective/search convention, source range or bound fixed before fitting.')
    if name == 'mea_system_modeling_results':
        if line in (46, 47, 106, 108, 110):
            return historical(C423 + 'refit-comparison.json' if line < 100 else BUNDLE + 'reduced-refit/fit-comparison.csv', field)
        if line in (5, 17, 19, 27, 44, 94):
            key = {5: 'fitted coordinates', 17: 'Cai temperature/rmse', 19: 'pressure SE/' + ('minimum' if index == 1 else 'maximum'),
                   27: 'search/' + {'2646': 'all', '2484': 'liquid', '162': 'liquid–vapor'}.get(token, 'all') + '/states',
                   44: 'carbonate share/aard_percent' if token == '95.0' else 'Jakobsen ratio/aard_percent',
                   94: {'45.1': 'Aronu 15 wt%/aard_percent', '45.9': 'Aronu 45 wt%/aard_percent',
                        '31.2': 'source/Aronu2011/aard_percent'}.get(token)}[line]
            if key and token not in ('47', '15', '45'):
                return current(F2 + 'summary.json', key, 'MEA/' + key)
        if line in (77, 79, 90):
            return bound(PAPER + 'same-data-comparison/part1-scores.json', field,
                         EVIDENCE + ('kim2007-heat-pathways/summary.json' if line == 77 else
                                     'heat-capacity-264.json' if line == 79 else 'density.csv'),
                         'Use stated source, temperature, fitted role and interval policy.')
        return carried(F2 + 'state-targets.csv', field, 'Source conditions, cohort membership or published comparator.')
    if name == 'transfer_results':
        if line < 41 or 53 <= line <= 71 or line in (82, 83, 126, 179, 213, 218, 219):
            source = (AMP + 'main/phase-classification-1.json.gz' if line < 41 or line == 179 else
                      SHARED + 'mdea-comparison.json.gz' if line < 72 else
                      MDEA + 'comparison.json' if line <= 83 or line == 213 else
                      DEA.replace('refit-413', 'reactive-refit-425') + 'comparisons.json' if line == 126 else C423 + 'refit-comparison.json')
            return historical(source, field)
        if line in (48, 49, 76, 77, 84, 85, 91, 97, 98, 99, 100, 103, 106, 107, 108, 138, 139, 143, 144, 145,
                    159, 174, 175, 180, 181, 188, 194, 196, 197, 198, 203):
            case = ('AMP' if line < 53 else 'MDEA' if line < 117 or line in (180, 181, 194, 196, 197, 198) else
                    'DEA' if line < 155 else 'MEA')
            if line == 159:
                return current(TRANSFER, 'Outside-fit loaded pressure AARD by amine and source',
                               'Across amines/outside loaded pressure AARD/' + ('minimum' if index == 0 else 'maximum'))
            if line in (174, 175):
                return bound(BANDS + 'band-table.csv', field, MEA + 'bands.json',
                             'result: group by band, property and role; n, AARD_percent, mean_signed_relative_percent, T_min_K/T_max_K')
            if line == 188 and token == '33.5':
                return current(BUNDLE + 'same-data-comparison/matched-pressure-rows.csv', 'Ma’mun 19-row AARD',
                               'MEA/Baygi/aard_percent')
            if line == 203:
                if token in ('24.8', '22.6'):
                    if token == '22.6':
                        return current(HONG + 'canonical.csv', 'strict-grid reported model AARD', 'MEA/Hong/canonical/strict_grid/aard_percent')
                return carried(HONG + 'canonical.csv', field, 'Published Hong and matched source membership.')
            if line == 194 and token == '19.5':
                return bound(KURANOV + 'statistics.json', 'present.K82.AARD_percent',
                             CURRENT['MDEA'].rsplit('/', 2)[0] + '/kuranov-matched-pressure.json.gz', 'grouped.K82')
            if line == 139:
                case = 'DEA' if index < 6 else 'AMP'
                base = CURRENT[case].rsplit('/', 2)[0] + '/'
                return bound(base.replace('salt-anchored-435', 'r4-shift-426') + 'shift.csv', field,
                             base + 'hydrolysis/shift.json',
                             'temperatures[T_K=313.15], delta_h_J_mol and conditional_SE_h_J_mol')
            if line in (84, 85, 91):
                if line == 85:
                    return bound(PHASE + 'binary-1466000.json', 'brackets[0].bracket_K',
                                 CURRENT['MDEA'] + 'binary-onset.json', 'result.pressures by imposed P, brackets[0].bracket_K')
                return bound(MDEA + 'comparison.json', 'k_versus_critical and binary checks',
                             CURRENT['MDEA'] + 'selection.json.gz', 'binary.native, binary.hull and point.parameters MDEA–water k(T)',
                             'Use critical-k.json for the fixed trial onset curve.')
            if line in (97, 98, 99, 100, 103, 180, 143, 144):
                old = DEA + 'selection.json' if case == 'DEA' else PHASE + ('fixed-pressure.json' if line == 103 else 'measured-phase.json')
                file = 'selection.json.gz' if case == 'DEA' else 'fixed-pressure.json.gz' if line == 103 else 'search-outcome.json.gz'
                return bound(old, field, CURRENT[case] + file, 'Selected endpoint search, by protocol, row key, and phase classification')
            base = {'MEA': F2, 'DEA': DEA, 'MDEA': MDEA, 'AMP': AMP + 'slope-150/'}[case]
            return bound(base + ('canonical-pressure.csv' if case == 'MEA' else 'paper-data.csv' if case == 'DEA' else 'data-rows.json'), field,
                         EVIDENCE + 'canonical-pressure.csv' if case == 'MEA' else
                         CURRENT[case] + (f'{case}/information.json.gz' if line in (48, 77, 138) else 'data-rows.json.gz'),
                         'Select the named role, source/state, property, and bound/covariance or available residual field.')
        return carried(DEA + 'paper-data.csv', field,
                       'Source conditions, unchanged neutral parameters or cited comparisons.')
    if name == 'supplement':
        if line in range(395, 399) or 530 <= line <= 537 or 561 <= line <= 598:
            return historical(REFERENCE + 'amp.json' if line < 400 else AMP + 'main/phase-classification-1.json.gz', field)
        if line in range(449, 454) or line in range(522, 525):
            return historical(SHARED + 'profile.json.gz; ' + SHARED + 'mdea-search-readback.json', field)
        if line in (158, 265, 266, 267, 272, 291, 292, 293, 456, 457, 458, 459, 460, 461):
            return historical(C423 + 'refit-comparison.json' if line < 280 else
                              OBJECTIVE + 'alternative/' if line < 300 else BUNDLE + 'reduced-refit/fit-comparison.csv', field)
        if line == 207:
            case = 'DEA' if index < 9 else 'AMP'
            base = CURRENT[case].rsplit('/', 2)[0] + '/'
            return bound(base.replace('salt-anchored-435', 'r4-shift-426') + 'shift.csv', field,
                         base + 'hydrolysis/shift.json', 'temperatures by T_K: delta_lnK and conditional SE')
        if 209 <= line <= 212:
            return bound(F2_PARAMETERS, field, READBACK + 'receiver-law-verification.json',
                         'models.DEA.carbamate / models.AMP free.carbamate; use recipient coordinates for diameter bounds.')
        if line == 263:
            key = {'0.004': 'minimum', '0.182': 'maximum', '0.0317': 'geometric mean'}.get(token)
            if key:
                return current(C423 + 'P0/carbonate-share.json', 'calc_over_obs ' + key, 'MEA/carbonate share/' + key)
        if line in (269, 270, 271):
            return bound('analyses/round_3/results/q5.json', field, MEA + 'q5.json',
                         'result.rows by temperature, pressure, loading and source symbol; result.carbonate_pool_comparison',
                         'control_pass compares to the old F2 pH. It is false with the changed parameter set; water_reaction_pass is the same-endpoint identity check.')
        if line in (289, 290, 423, 424, 425, 426, 427, 442, 443, 444, 445):
            key = {'1.169': 'information/stage_variance', '150.763': 'C', '60.78': 'Cai objective share',
                   '1.16869941': 'information/stage_variance', '268': 'information/na', '258': 'information/stage_denominator',
                   '1.01523840': 'information/variance', '1.0729': 'information/SE_multiplier',
                   '5.98': 'pressure SE/minimum', '16.9': 'pressure SE/maximum',
                   '39.824': 'Cai temperature objective cost', '51.807': 'Cai vapour water fraction objective cost'}.get(token)
            if key:
                return current(OBJECTIVE + 'MEA/information.json.gz', key, 'MEA/' + key)
            case = 'MEA' if line < 442 else 'DEA' if line == 442 else 'AMP' if line == 443 else 'MDEA'
            return bound(OBJECTIVE + f'{case}/information.json.gz', field,
                         CURRENT[case] + ('objective-information.json.gz' if case == 'MEA' else f'{case}/information.json.gz'),
                         'result rows, rank, active bounds, stage variance and conditional correlation by coordinate')
        if line == 375:
            return bound(AMP + 'slope-150/data-rows.json', 'loaded-pressure observation count and scale',
                         CURRENT['AMP'] + 'AMP/contributions.csv.gz', 'expanded group of 105 rows, declared scale and weight')
        if line in (331, 353, 354):
            return bound(REFERENCE + 's12.json' if line == 331 else MDEA + 'data-rows.json', field,
                         CURRENT['MDEA'] + 'data-rows.json.gz', 'group, identity, available and residual fields on matched rows')
        if line in (399, 405, 406):
            key = {'-81.553': 'heat_kJ_mol', '84.628': 'cp_J_mol_K'}.get(token)
            if key:
                return current(REFERENCE + 'mea.json', key, 'MEA/worked state/' + key)
            return bound(REFERENCE + 'mea.json', field, MEA + 'reference-state.json',
                         'Worked initial/loaded solution at 313.15 K, energy, Cp and pressure-standard reaction checks')
        if line == 407:
            return bound('analyses/round_3/results/q4.json', field, MEA + 'q4.json',
                         'result.rows by canonical identity; baseline, fixed_reference and pCO2_change',
                         'The legacy F2 archived pressure equality check is false under #435; the matched-pressure control and basis identity are retained.')
        if 489 <= line <= 499:
            return bound(F2 + 'summary.json', field, MEA + 'search-summary.json',
                         'grid/offset/census counts and outcomes; input state definitions in reduced_refit_338.py')
        if 516 <= line <= 521:
            return historical(PHASE + 'fixed-pressure.json', 'Original fixed-pressure parent and split; ' + field)
        if 512 <= line <= 527:
            return bound(PHASE + 'measured-phase.json; ' + PHASE + 'fixed-pressure.json', field,
                         CURRENT['MDEA'] + 'search-outcome.json.gz',
                         'Match measurement/grid or fixed-pressure protocol and state identity.')
        if line in (507, 509, 547, 548):
            return bound(DEA + 'selection.json', field, CURRENT['DEA'] + 'selection.json.gz',
                         'Candidates by start and parameter identity; abs tie and searched-state counts, plus refusal-replay.json')
        if line == 553:
            return bound(MDEA + 'comparison.json', 'Start objectives and active bounds',
                         CURRENT['MDEA'] + 'selection.json.gz',
                         'Selected endpoint, three fit-*/outcome.json.gz report.endpoint_replay_cost records and active bounds in MDEA/information.json.gz')
        if line == 554:
            return historical(MDEA + 'comparison.json', 'Unbounded control, ' + field)
        if line == 555:
            return bound(MDEA + 'comparison.json', 'k_versus_critical and binary checks',
                         CURRENT['MDEA'] + 'selection.json.gz', 'binary.native and binary.hull')
        if line in (557, 558):
            return bound(PHASE + 'binary-1121000.json; ' + PHASE + 'binary-1466000.json; ' + PHASE + 'binary-1811000.json',
                         'brackets[0].bracket_K and k_bound', CURRENT['MDEA'] + 'binary-onset.json',
                         'result.pressures by imposed P, k_bound or brackets[0].bracket_K')
        if line in (618, 619):
            return bound(KURANOV + 'statistics.json', field,
                         CURRENT['MDEA'].rsplit('/', 2)[0] + '/kuranov-matched-pressure.json.gz',
                         'grouped.K82 and grouped.fitted loaded')
        if line in (655, 656, 676):
            group = {655: 'canonical/strict_grid', 656: 'canonical/all', 676: 'six sources'}[line]
            if token in ('22.59', '21.25', '20.97'):
                key = f'MEA/Hong/{group}/aard_percent' if line != 676 else 'MEA/six sources/aard_percent'
                return current(HONG + 'canonical.csv', 'AARD on named cohort', key)
        if line >= 600:
            return carried(HONG + 'canonical.csv; ' + KURANOV + 'statistics.json', field,
                           'Published-model-only value or source selection; the cited source and basis are given in this statement.')
        source = (MDEA + 'critical-k.json' if line >= 539 else 'analyses/part_ii.py' if line >= 478 else
                  PAPER + 'objective-groups.csv' if line >= 276 else F2 + 'state-targets.csv' if line >= 218 else
                  F2_PARAMETERS)
        return carried(source, field, 'Fixed model convention, source value or declared state input specified in this statement.')
    raise ValueError(f'No quantity rule for text {name}:{line}')


def figure_quantities(figures):
    """Bind plotted series to point fields, keeping axes and legends in the renderer."""
    dea, mdea, amp = (CURRENT[case].rsplit('/', 2)[0] + '/' for case in ('DEA', 'MDEA', 'AMP'))
    dea += 'campaign/'
    f2_figures = DISPLAYS + 'f2_figures.py'
    series = {
        'pressure.pdf': (f2_figures, PAPER + "paper-evidence/", EVIDENCE, [
            ('Measured pressure', 'canonical-pressure.csv', 'loading, observed Pa, temperature_K; markers by fitted IDs'),
            ('Bubble curves', 'model-curves/pressure.csv', 'analytical_loading, value Pa, temperature_K, status')]),
        'speciation.pdf': (f2_figures, PAPER + "paper-evidence/", EVIDENCE, [
            ('Observed species and sums', 'species-figure-data.csv', 'target, species, loading, observed mole fraction, temperature_K'),
            ('Species curves', 'model-curves/species.csv', 'species, temperature_K, value mole fraction, analytical_loading, below_bubble_pressure')]),
        'density-curves.pdf': (f2_figures, PAPER + "paper-evidence/", EVIDENCE, [
            ('Measured liquid densities', 'density.csv', 'loading, observed_kg_m3, T_K; nominal 30 wt% and fitted ID marks'),
            ('Liquid density curves', 'model-curves/density.csv', 'analytical_loading, value kg/m³, temperature_K, pressure_Pa, below_bubble_pressure')]),
        'heat-of-absorption.pdf': (f2_figures, PAPER + "paper-evidence/", EVIDENCE, [
            ('Vinjarapu and Arcis', 'heat.csv', 'loading, observed_kJ_mol, source, role, P_Pa'),
            ('Integral heats', 'model-curves/heat.csv', 'analytical_loading, value, unit, curve, status')]),
        'concentration-pressure.pdf': (f2_figures, PAPER + "paper-evidence/", EVIDENCE, [
            ('Aronu 15/45 wt% data and predictions', 'transfer.csv', 'target, temperature_K, observed/predicted Pa; CO2_loading in canonical source')]),
        'jakobsen-carbonate-share.pdf': (TRANSFER, F2, EVIDENCE, [
            ('Ten carbonate comparisons', 'carbonate-share.csv', 'observed_share and predicted_share of dissolved carbon; identity id')]),
        'mea-water.pdf': (f2_figures, PAPER + "paper-evidence/", EVIDENCE, [
            ('Cai binary curves', 'model-curves/mea-water.csv', 'liquid_mea_mole_fraction, value K, pressure_Pa'),
            ('Cai observations and roles', 'fitted-rows.csv', 'Cai / temperature; source composition/pressure from objective declarations')]),
        'amp-current-measured-model.pdf': (TRANSFER, AMP + 'slope-150/', amp, [
            ('AMP model pressure curves', 'curve-data.json', 'rows by pressure group, loading, temperature, value Pa, role markers from fit declaration')]),
        'mdea-current-measured-model.pdf': (TRANSFER, MDEA, mdea, [
            ('MDEA model pressure curves', 'curve-data.json', 'rows by pressure group, loading, temperature, value Pa; compare retained measurements at their own conditions')]),
        'dea-current-measured-model.pdf': (TRANSFER, DEA, dea, [
            ('Lawson, Seo/Hong, Lal and Carson curves', 'curve-data.json.gz', 'group, T_K, loading, value [Pa or J/mol CO2], outside_ranges'),
            ('Measured pressure and heat', 'data-rows.json.gz', 'group, observed, unit, T_K, row composition and loading, role')]),
        'dea-integral-heat-concentrations.pdf': (TRANSFER, DEA, dea, [
            ('Carson heat curves', 'curve-data.json.gz', 'group=Carson, row.DEA_mass_fraction, loading, value J/mol CO2'),
            ('Carson heat observations', 'data-rows.json.gz', 'group=Carson, fitted, observed J/mol CO2 and loading')]),
    }
    old_files = {('amp-current-measured-model.pdf', 'curve-data.json'): 'curve-data.json',
                 ('mdea-current-measured-model.pdf', 'curve-data.json'): 'curves/curve-data.json',
                 ('dea-current-measured-model.pdf', 'curve-data.json.gz'): 'curve-data.json',
                 ('dea-current-measured-model.pdf', 'data-rows.json.gz'): 'paper-data.csv',
                 ('dea-integral-heat-concentrations.pdf', 'curve-data.json.gz'): 'curve-data.json',
                 ('dea-integral-heat-concentrations.pdf', 'data-rows.json.gz'): 'paper-data.csv'}
    records = []
    for name, locators in sorted(figures.items()):
        if name in series:
            producer, old, new, fields = series[name]
            bindings = [dict(series=label, old_producer=producer,
                             **bound(old + old_files.get((name, file), file), keys, new + file, keys))
                        for label, file, keys in fields]
            if name in ('amp-current-measured-model.pdf', 'mdea-current-measured-model.pdf'):
                case = 'AMP' if name.startswith('amp') else 'MDEA'
                bindings.append(dict(series='Measured pressures and fit membership', old_producer=producer,
                                     **bound(old + 'data-rows.json', 'observed, role, T_K and source loading',
                                             CURRENT[case] + 'data-rows.json.gz', 'observed, role, unit, T_K and source loading')))
        elif name == 'amp-splits.pdf':
            bindings = [dict(series=label, old_producer=TRANSFER, **historical(
                AMP + 'main/phase-classification-1.json.gz', field)) for label, field in
                [('Confirmed second liquid', 'confirmed witnesses, temperature, loading, pressure and composition'),
                 ('Detected instability without confirmation', 'unconfirmed witnesses at same protocol')]]
        elif name == 'dea-current-binary-comparisons.pdf':
            bindings = [dict(series=label, old_producer=TRANSFER,
                             **historical(DEA + 'paper-data.csv', field)) for label, field in
                        [('Horstmann', 'water fraction, measured and calculated excess enthalpy, J/mol mixture'),
                         ('Cai', 'water fraction, measured and calculated bubble pressure, Pa converted to kPa')]]
        elif name == 'mdea-gap-onset.pdf':
            bindings = [dict(series='CO2-free onset points', old_producer=TRANSFER,
                             **carried(MDEA + 'critical-k.json', 'rows[].T_K and k_gap',
                                       'CO2-free onset procedure varies the MDEA binary coefficient with common neutral inputs.')),
                        dict(series='Fitted MDEA–water law', old_producer=TRANSFER,
                             **bound(MDEA + 'comparison.json', 'k_versus_critical', CURRENT['MDEA'] + 'selection.json.gz',
                                     'point.parameters.pairs for MDEA–water; evaluate at critical-k rows.T_K'))]
        elif name == 'loaded-pressure-residuals.pdf':
            files = {'MEA': (F2 + 'canonical-pressure.csv', EVIDENCE + 'canonical-pressure.csv', 'ln_pred_over_obs, loading, temperature_K; fitted IDs from fitted-rows.csv'),
                     'DEA': (DEA + 'paper-data.csv', dea + 'data-rows.json.gz', 'Lawson, Lawson-394K, SeoHong, Lal, Lawson-VIII: ln(value/observed), role, source loading'),
                     'MDEA': (MDEA + 'data-rows.json', CURRENT['MDEA'] + 'data-rows.json.gz', 'Kuranov, Kuranov-413K, corrected-Kamps, Sedighi: ln(value/observed), role, source loading'),
                     'AMP': (AMP + 'slope-150/data-rows.json', CURRENT['AMP'] + 'data-rows.json.gz', 'loaded-pressure, hartono-2021-supplemental, tong, loaded rows: ln(value/observed), role, source loading')}
            bindings = [dict(series=case, old_producer=TRANSFER, **bound(old, keys, new, keys))
                        for case, (old, new, keys) in files.items()]
        else:
            raise ValueError(f'No figure series inventory for {name}')
        for binding in bindings:
            source = binding.get('record', binding['old_source'])
            binding['source_sha256'] = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
            binding['old_source_sha256'] = hashlib.sha256((ROOT / binding['old_source']).read_bytes()).hexdigest()
            records.append(dict(figure=name, inclusions=locators, **binding))
    return records
