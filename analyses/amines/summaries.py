"""Write display summaries from the retained output of the fit, phase and property stages."""

from collections import Counter, defaultdict
from csv import DictReader
from math import fsum, sqrt

from .records import RESULTS, input_path, read
from scipy.constants import R

from . import amp as amp_model, dea as dea_model, mdea
from .fit import retained_endpoint, route_for, save
from .model import P_REF, REPORTED, ROOT
from .phase import grid_axes, grid_states, phase_outcome
from .wheel import verify

ROUND9 = "analyses/round_9/"
ENDPOINTS = {
    "MEA": ("A", "B", "LHS-21"),
    "DEA": ("A", "B", "C"),
    "AMP_free": ("A", "LHS-06", "LHS-45"),
    "MDEA": ("A", "A-continuation", "A-descent-continuation", "LHS-53"),
}
AMP_H = "AMP-hydrolysis-enthalpy-increment"


class Records:
    def __init__(self):
        self.wheel = verify()
        self.inputs = set()

    def read_bytes(self, name):
        path = input_path(name)
        self.inputs.add(path.relative_to(ROOT).as_posix())
        return path.read_bytes()

    def read(self, name):
        path = input_path(name)
        self.inputs.add(path.relative_to(ROOT).as_posix())
        return read(path)

    def fixed(self, name):
        return self.read(REPORTED / name)

    def new(self, name):
        record = self.read(ROUND9 + "results/" + name)
        if record["wheel"] != self.wheel:
            raise ValueError(f"Wrong wheel for {name}")
        return record

    def write(self, name, values):
        save(RESULTS / name, dict(wheel=self.wheel, inputs=sorted(self.inputs), **values))
        self.inputs.clear()


def dea(s):
    payload = s.new('dea-phase-controls.json.gz')
    record = dict(payload['value'], wall_s=payload['wall_s'])
    selected = s.fixed('DEA/selection.json')
    assert record['endpoint_fingerprint'] == selected['endpoint_fingerprint']
    for q in record['rows']:
        total = fsum(p['amount_mol'] for p in q['phases'])
        for phase in q['phases']:
            phase['true_mole_fraction'] = phase['amount_mol'] / total
        q['max_reaction_residual'] = max(abs(r['residual']) for r in q['reaction_contractions'])
        q['max_interphase_residual'] = max(map(abs, q['interphase_residuals'].values()))
        q['declared_confirmed'] = sum(a['confirmed'] for a in q['declared_search_attempts'])
        q['registry_growth_confirmed'] = sum(a['confirmed'] for a in q['registry_growth_attempts'])
    worked = min(record['rows'], key=lambda q: q['split']['Gibbs_decrease_over_RT_mol'])
    return dict(record, worked_state=worked['key'], denominator='sum of daughter true-species molar amounts')


def amp(s):
    payload = s.new('amp-phase-controls.json.gz')
    record = dict(payload['value'], wall_s=payload['wall_s'])
    assert record['endpoint_fingerprint'] == s.fixed('AMP_free/selection.json')['endpoint_fingerprint']
    for q in record['rows']:
        witness = q['witness']
        if not witness:
            continue
        q['reported_two_liquid_gates'] = []
        for attempt in q['reported_attempts']:
            message = attempt['message']
            gate = ('coalescence' if 'phases_coincide' in message else
                    'electroneutrality' if 'non-electroneutral' in message else
                    'equilibrium residual' if not attempt.get('requested_tolerance_met') else 'phase identity')
            q['reported_two_liquid_gates'].append(gate)
        lv, = [a for a in q['reported_candidates'] if a['support'] == 'L+V']
        q['reported_liquid_vapor_gate'] = 'passed' if lv['root_checks_pass'] else 'strict vapor-root identity'
        assert q['P_Pa'] < q['reported_bubble_Pa']
    return record


def endpoint_stages(record):
    stages = endpoint_stages(record['previous_stage']) if 'previous_stage' in record else []
    report = record['report']
    tol = record['controls']['gradient_tolerance']
    gradient = (report.get('covariance') or {}).get('projected_gradient_norm')
    return stages + [dict(status=report['status'], termination=report['message'],
                          endpoint=record.get('endpoint_fingerprint'),
                          C=record.get('replay', {}).get('cost'), projected_gradient=gradient,
                          gradient_limit=tol, fit_seconds=record.get('fit_seconds', record.get('fit_wall_s')),
                          wall_seconds=record.get('wall_s'), gradient_passed=None if gradient is None else gradient <= tol)]


def fit_accounting(s, attempts):
    endpoints = {}
    for amine, fits in attempts.items():
        endpoints[amine] = {label: endpoint_stages(s.fixed(f'{amine}/{label}.json.gz')) for label in fits}
    for label in ('A-continuation', 'A-descent-continuation'):
        endpoints['MDEA'][label] = endpoint_stages(s.fixed(f'MDEA/stationarity/{label}.json.gz'))
    preservation = s.read(RESULTS / 'shared/preservation/fit-cost-budgets.json.gz')
    diagnostic = preservation['fits']['MDEA LHS-53, common prefix']
    stage = endpoints['MDEA']['LHS-53'][-1]
    if preservation['wheel'] == s.wheel and stage['endpoint'] == diagnostic['retained_fingerprint']:
        stage['historical_stop'] = preservation['mdea_path']['printed_stop']

    draws = s.fixed('MDEA/replacement-starts.json.gz')
    initial = attempts['MDEA']
    manifest = s.fixed('MDEA/manifest.json.gz')
    initial_draws = {q['draw'] for q in manifest['starts'].values() if q['draw'] is not None}
    tested = initial_draws | {q['start']['draw'] for q in draws['draws'].values()}
    start_counts = dict(inherited=draws['accepted_original'], drawn=len(tested | set(draws['remaining'])), tested=len(tested),
                        replacement_draws=len(draws['draws']),
                        evaluable=[k for k, q in draws['draws'].items() if q['disposition'] == 'eligible'],
                        untested_draws=draws['remaining'], fitted_endpoints=[k for k,q in initial.items() if q['endpoint']])
    properties = s.fixed('MDEA/properties.json.gz')['rows']
    start_counts['A_AARD_percent'] = {
        group: aard((row['value'], row['observed']) for row in properties
                    if row['group'] == group and row['unit'] == 'Pa' and available(row))
        for group in ('Kuranov', 'Ermatchkov')
    }
    return dict(mdea_start_counts=start_counts, endpoint_stages=endpoints)


def phase_accounting(s):
    mea = s.fixed('MEA/screen/summary.json.gz')
    grid = mea['grid']
    coverage = dict(MEA=dict(attempted=sum(grid[k]['states'] for k in ('grid', 'offset', 'census')),
                             completed=grid['grid']['available']+grid['offset']['available']
                                       +grid['census']['states']-grid['census']['incomplete']),
                    MEA_measured=dict(attempted=mea['measured']['states'], completed=mea['measured']['available']))
    for label, family, protocol in (('DEA', 'DEA', 'declared'), ('MDEA', 'MDEA', 'declared'),
                                    ('AMP', 'AMP_free', 'native')):
        screen = s.fixed(f'{family}/screen/selected/{protocol}/summary.json.gz')
        coverage[label] = dict(attempted=len(screen['rows']), completed=sum(q['available'] for q in screen['rows']))
    screen = s.fixed('MDEA/screen/selected/declared/summary.json.gz')
    grid_rows = [q for q in screen['rows'] if q['key'].startswith('grid:')]
    grid_unavailable = Counter(q['key'].rsplit(':', 1)[1] for q in grid_rows if not q['available'])
    mdea_populations = dict(
        attempted=len(screen['rows']), available=coverage['MDEA']['completed'],
        unavailable=len(screen['rows']) - coverage['MDEA']['completed'],
        grid_attempted=len(grid_rows), grid_unavailable=sum(grid_unavailable.values()),
        grid_unavailable_by_pressure_factor=dict(grid_unavailable),
        measured_attempted=len(screen['rows']) - len(grid_rows),
        measured_unavailable=len(screen['rows']) - coverage['MDEA']['completed'] - sum(grid_unavailable.values()),
    )
    inventory = {q['key']: q for q in s.fixed('MDEA/screen/selected/declared/state-inventory.json.gz')['rows']}
    crosswalk = s.read('analyses/mdea_mea_workflow/results/phase-search-421/observation-crosswalk.json')
    manifest = s.fixed('MDEA/manifest.json.gz')
    sources = {q['identity']: q['row'] for pool in manifest['rows'].values() for q in pool}
    crosswalk = {q['key']: q['identity'] for q in crosswalk}
    descending = [q for q in screen['rows'] if q['descent']]
    detections = Counter(q.get('same_calculation_as', q['key']) for q in descending)
    descent_counts = dict(
        optimized_result_available=sum(q['available'] and q['optimized_available'] for q in descending),
        supplied_trial_optimized_result_unavailable=sum(
            not q['available'] and not q['optimized_available'] and q['supplied_available'] for q in descending
        ),
    )
    assert sum(descent_counts.values()) == len(descending)
    assert set(detections) == {q['key'] for q in screen['classifications']}
    states = []
    for q in screen['classifications']:
        key = q['key']
        inv = inventory[key]
        identity = crosswalk.get(key, key.rsplit(':', 1)[0].removesuffix(':1'))
        source = sources[identity]
        pressure = inv.get('declared_pressure_Pa', inv.get('search_Pa'))
        if inv['pressure_basis'] == 'bubble scaled':
            basis = 'calculated'
        elif source['source_key'] in ('BottingerMDEA2008', 'Merkley1987'):
            basis = 'assigned'
        else:
            basis = 'measured'
        states.append(dict(key=key, T_K=q['temperature_K'], source=source, pressure_Pa=pressure,
                           pressure_basis=basis, detections=detections[key], native_branch=q['native_branch'],
                           confirmed=sum(a['confirmed'] for a in q['attempts']), attempts=len(q['attempts'])))
    return dict(coverage=coverage, mdea_search=mdea_populations, mdea_distinct_states=states,
                mdea_descent_counts=descent_counts)


def paired(before, after):
    left, right = ({r['identity']: r for r in rows} for rows in (before, after))
    if left.keys() != right.keys():
        raise ValueError('Mismatched comparison rows')
    assert all(left[k]['observed'] == right[k]['observed'] and left[k]['row'] == right[k]['row'] for k in left)
    common = [k for k in left if all(r[k]['status'] == 'Available' and r[k]['value'] is not None for r in (left, right))]
    outputs = {}
    for name, rows in (('salt-anchored', left), ('MEA-fitted', right)):
        delta = [100*(rows[k]['value']/rows[k]['observed']-1) for k in common]
        outputs[name] = dict(AARD_percent=fsum(map(abs, delta))/len(delta) if delta else None,
                             bias_percent=fsum(delta)/len(delta) if delta else None,
                             unavailable=[q for q in rows.values() if q['status'] != 'Available' or q['value'] is None])
    return dict(requested=len(left), common=common, models=outputs)


def shared(s):
    quantities, fits = {}, {}
    mea = s.fixed('E/MEA/replay.json.gz')
    mdea = s.fixed('MDEA/properties.json.gz')
    baselines = {'MEA': {'legacy-47': [q for q in mea['rows'] if q['group'] == 'common149' and q['unit'] == 'Pa'],
                         'Mamun2005': [q for q in mea['rows'] if mea['pressure_population'].get(q['identity'], {}).get('source_key') == 'Mamun2005']},
                 'MDEA': {g: [q for q in mdea['rows'] if q['group'] == g] for g in ('Kuranov', 'Ermatchkov', 'Carson')}}
    for name, before in baselines.items():
        fit = s.new(f'{name}-shared-fit.json.gz')
        assess = s.new(f'{name}-shared-assessment.json.gz')
        assert assess['endpoint_fingerprint'] == fit['endpoint_fingerprint']
        fits[name] = endpoint_stages(fit)
        for group, rows in before.items():
            quantities[f'{name} {group}'] = paired(rows, assess['rows'][group])
    phase_record = s.new('mdea-phase-controls.json.gz')
    phases = phase_record['value']
    for case in phases.values():
        for model in case['models'].values():
            model['outcome'] = ('unavailable' if 'refusal' in model else
                                'confirmed split' if any(a['confirmed'] for a in model['attempts']) else
                                'unresolved phase identity' if model['instability'] == 'resolved descent' else model['instability'])
    return dict(comparisons=quantities, fit_stages=fits, phase_controls=phases)


def kamps(s):
    rows = [q for q in s.fixed('MDEA/property-comparisons/A.json.gz')['rows'] if q['group'] == 'corrected-Kamps']
    additional, = [q for q in rows if q['identity'] == 'comparison:113']
    def aard(pool):
        return 100*fsum(abs(q['value']/q['observed']-1) for q in pool)/len(pool)
    return dict(full_rows=len(rows), full_AARD_percent=aard(rows), common_rows=len(rows)-1,
                common_AARD_percent=aard([q for q in rows if q is not additional]),
                additional_row=additional, additional_signed_percent=100*(additional['value']/additional['observed']-1))


def amp_units(s):
    source = s.read('analyses/amp_transfer/results/salt-anchored-435/hydrolysis/shift.json')
    values = {}
    for label in ('AMP_free', 'AMP_fixed'):
        manifest = s.fixed(f'{label}/manifest.json.gz')
        index = manifest['coordinate_order'].index(AMP_H)
        coord = manifest['start_A_declaration']['coordinates'][index]
        physical = source['bounds']['enthalpy']
        offset = physical[0]-coord['bounds'][0]
        assert [v + offset for v in coord['bounds']] == physical
        fit = s.fixed(f'{label}/A.json.gz')
        final, = [q['correlation']['b'] for q in fit['endpoint']['reactions']['aqueous'] if q['name'] == 'carbamate-hydrolysis']
        fitted_increment = -R*(final-source['source_law']['b'])
        values[label] = dict(coordinate_index=index, offset_J_mol=offset, physical_bounds_J_mol=physical,
                             fit_bounds_J_mol=coord['bounds'], endpoint_increment_J_mol=fitted_increment)
    return values


def aard(pairs):
    errors = [abs((calc - observed) / observed) * 100 for calc, observed in pairs]
    return fsum(errors) / len(errors) if errors else None


def comparison(models, spread_labels):
    """Use the same nonzero measurements for each endpoint in a spread."""
    a = models['A']
    assert all(a.keys() == rows.keys() for rows in models.values())
    common, unavailable, excluded, spreads = [], {}, [], {}
    for key, observed in a.items():
        y = observed['observed']
        samples = {label: rows[key] for label, rows in models.items()}
        assert all(row['observed'] == y and row['unit'] == observed['unit'] for row in samples.values()), key
        refusals = {name: row for name, row in samples.items()
                    if row['status'].lower() != 'available' or row.get('value') is None}
        if refusals:
            unavailable[key] = refusals
        if not y:
            excluded.append(key)
        if refusals or not y:
            continue
        common.append(key)
        values = [models[name][key]['value'] for name in spread_labels]
        spreads[key] = dict(relative_spread_percent=100 * (max(values) - min(values)) / abs(y),
                            selected_abs_relative_deviation_percent=100 * abs(a[key]['value'] - y) / abs(y))
    deviations = {name: aard((rows[key]['value'], a[key]['observed']) for key in common)
                  for name, rows in models.items()}
    low, high = (None, None) if not common else (min(deviations[k] for k in spread_labels),
                                                 max(deviations[k] for k in spread_labels))
    maximum = max(spreads, key=lambda key: spreads[key]['relative_spread_percent'], default=None)
    return dict(requested=len(a), common=len(common), endpoints=list(spread_labels),
                endpoint_AARD_percent=deviations, AARD_spread_pp=None if low is None else high-low,
                max_row=maximum, row_spreads=spreads, unavailable=unavailable,
                zero_observation=excluded)


def cohorts(design, rows, canonical):
    pools = defaultdict(dict)

    def add(group, r):
        assert r['identity'] not in pools[group]
        pools[group][r['identity']] = r

    for r in rows:
        g = r['group']
        if design != 'MEA':
            add(g, r)
            if g == 'corrected-Kamps' and r['identity'] != 'comparison:113':
                add('corrected-Kamps common rows', r)
            continue
        if r['unit'] != 'Pa':
            add(g, r)
            if r['T_K'] >= 370:
                add(g + ' (hot)', r)
            continue
        if g == 'canonical':
            add('Canonical pressures outside objective', r)
            add(r['source'] + ' (outside objective)', r)
        elif g == 'off-window':
            add(r['source'] + ' (off-window)', r)
            if r['source'] == 'Aronu2011':
                source = canonical[r['identity'].removeprefix('off-window:')]
                add(f"Aronu2011 ({100*float(source['MEA_weight_fraction']):.0f} wt%)", r)
        else:
            add('Wagner2013', r)
        if g != 'off-window' or r['source'] == 'Aronu2011':
            add('All Table 8 outside-objective pressures', r)
        if r['T_K'] >= 370 and g in ('canonical', 'Wagner'):
            add('Hot pressures including Wagner', r)
            add('Hot canonical pressures' if g == 'canonical' else 'Hot Wagner pressures', r)
    return pools


def endpoint_predictions(s):
    canonical = s.read_bytes('data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')
    canonical = {q['observation_id']: q for q in DictReader(canonical.decode().splitlines())}
    pure = s.read('analyses/amp_transfer/results/retransfer-344-05e94210/pure-binary-on-05e94210.json')
    assert pure['engine']['wheel_sha256'] == s.wheel
    pappas = [dict(identity=f"Pappa2006:{i}", group='Pappa2006', unit='Pa',
                   observed=q['observed'], value=q['predicted'], status=q['status'])
              for i, q in enumerate(pure['pure']['rows']) if q['campaign'] == 'Pappa2006']
    output = {}
    for design, labels in ENDPOINTS.items():
        case, runtimes, fingerprints, source_wheels, pure_amp = {}, {}, {}, {}, []
        selected = s.fixed(f'{design}/selection.json')
        for label in labels:
            prefix = 'stationarity/' if label.endswith('continuation') else ''
            # A-continuation was obtained on an earlier wheel. Its vector is
            # read unchanged and all round-10 predictions use the study wheel.
            fit = s.fixed(f'{design}/{prefix}{label}.json.gz')
            source_wheels[label] = fit['wheel']
            record = s.read(f'analyses/round_10/results/{design}-{label}.json.gz')
            assert record['wheel'] == s.wheel and record['reference_pressure_Pa'] == P_REF
            assert record['endpoint_fingerprint'] == fit['endpoint_fingerprint']
            rows = record['rows']
            if design == 'AMP_free':
                pure_amp.append(next(c for c in fit['endpoint']['parameters']['components']
                                     if c['component_id'] == 'aminomethylpropanol'))
                rows = rows + pappas
            assert len({q['identity'] for q in rows}) == len(rows)
            case[label] = cohorts(design, rows, canonical)
            runtimes[label] = record['seconds']
            fingerprints[label] = record['endpoint_fingerprint']
        assert fingerprints[selected['selected']] == selected['endpoint_fingerprint']
        assert all(groups.keys() == case['A'].keys() for groups in case.values())
        span = labels[1:] if design == 'MDEA' else labels
        groups = {g: comparison({label: pools[g] for label, pools in case.items()}, span) for g in case['A']}
        output[design] = dict(groups=groups, replay_seconds=runtimes, endpoint_fingerprints=fingerprints,
                              endpoint_source_wheel_sha256=source_wheels)
    return output


def selected(s, design, path):
    record = s.fixed(f'{design}/{path}')
    assert record['endpoint_fingerprint'] == s.fixed(f'{design}/selection.json')['endpoint_fingerprint']
    return record


def mea_search(s):
    census = selected(s, 'MEA', 'screen/census.json.gz')['data']['rows']
    grid = selected(s, 'MEA', 'screen/grid.json.gz')['data']
    batches = sorted((RESULTS / 'mea/reported/phase/measured').glob('*.json.gz'))
    measured = [row for batch in batches for row in s.read(str(batch.relative_to(ROOT)))]
    liquid_counts = Counter(q['key'].split('|', 1)[0] for q in grid)
    result = dict(liquid_grid=dict(completed=sum(q['available'] for q in grid), attempted=len(grid),
                                   populations=dict(liquid_counts)),
                  census=dict(attempted=len(census), outcomes=dict(Counter(q['classification'] for q in census))),
                  measured=dict(completed=sum(q['available'] for q in measured), attempted=len(measured)))
    summary = selected(s, 'MEA', 'screen/summary.json.gz')
    assert result['measured']['completed'] == summary['measured']['available']
    return result


def amp_outcomes(s):
    record = s.read(ROUND9 + 'results/amp-phase-controls.json.gz')
    assert record['wheel'] == s.wheel
    assert record['value']['endpoint_fingerprint'] == s.fixed('AMP_free/selection.json')['endpoint_fingerprint']
    outcomes = {}
    for row in record['value']['rows']:
        if row['key'] == 'worked-state':
            continue
        assert not any(q['confirmed'] for q in row['reported_attempts'])
        if not row['witness']:
            assert row['outcomes']['reported'] == 'finite search, no resolved descent'
            outcome = 'No resolved descent'
        else:
            assert row['outcomes']['reported'] == 'unresolved phase identity'
            lv, = [q for q in row['reported_candidates'] if q['support'] == 'L+V']
            assert lv['requested_tolerance_met'] and lv['physical_checks_pass']
            assert lv['qualified'] == lv['root_checks_pass']
            if lv['qualified']:
                assert lv['Gibbs_over_RT_mol'] == min(q['Gibbs_over_RT_mol'] for q in row['reported_candidates']
                                                       if q['qualified'])
            outcome = 'L+V passed; L+L unresolved' if lv['root_checks_pass'] else 'Vapor-directed; root unqualified'
        outcomes[row['key']] = dict(outcome=outcome, source=row['source'], pressure_Pa=row['P_Pa'])
    return outcomes


def dea_density(s):
    record = s.read(ROUND9 + 'results/dea-phase-controls.json.gz')
    densities = selected(s, 'DEA', 'property-comparisons/selected.json.gz')
    assert record['wheel'] == s.wheel and record['value']['endpoint_fingerprint'] == densities['endpoint_fingerprint']
    by_id = {q['identity']: q for q in densities['rows'] if q['group'] == 'Weiland'}
    rows = []
    for case in record['value']['rows']:
        q = by_id[case['key'].removesuffix(':problem')]
        deposit_id = int(q['identity'].split(':')[1])
        source_row = int(q['row']['source_row'])
        assert q['status'] == 'Available' and q['T_K'] == case['T_K']
        assert float(q['row']['alpha_mol_CO2_per_mol_DEA']) == case['loading']
        daughters = case['phases']
        bulk = 1 / fsum(p['mass_fraction'] / p['density_kg_m3'] for p in daughters)
        rows.append(dict(key=case['key'], deposit_id=deposit_id, processed_source_row=source_row,
                         T_K=case['T_K'], pressure_Pa=case['P_Pa'], pressure_basis=case['pressure_basis'],
                         observed_kg_m3=q['observed'], single_liquid_kg_m3=q['value'], two_liquid_kg_m3=bulk))
    return dict(rows=rows, AARD_percent={model: aard((r[model+'_kg_m3'], r['observed_kg_m3']) for r in rows)
                                        for model in ('single_liquid', 'two_liquid')})


def mdea_bubble(s, pressure_basis):
    screen = selected(s, 'MDEA', 'screen/selected/declared/summary.json.gz')
    inventory = selected(s, 'MDEA', 'screen/selected/declared/state-inventory.json.gz')

    measured = {r['key']: r for r in pressure_basis['mdea_distinct_states'] if r['pressure_basis'] == 'measured'}
    classified = {r['key']: r for r in screen['classifications']}
    states = {r['key']: r for r in inventory['rows']}
    output = {}
    for key, measurement in measured.items():
        row = states[key]
        assert row['pressure_basis'] == 'declared absolute'
        assert row['declared_pressure_Pa'] == classified[key]['pressure_Pa'] == measurement['pressure_Pa']
        value, diagnostic = row['bubble_Pa'], row['bubble_status']
        assert value is not None or diagnostic
        output[key] = dict(source=measurement['source'], T_K=row['T_K'], measured_Pa=row['declared_pressure_Pa'],
                           bubble_Pa=value, status='Available' if value is not None else 'Refused', diagnostic=diagnostic)
    return output


def available(row):
    return row.get('status') == 'Available' and row.get('requested_tolerance_met', True) and row.get('value') is not None


def fit_attempts(s):
    attempts, distances = {}, {}
    for design in ('MEA', 'DEA', 'MDEA', 'AMP_free', 'AMP_fixed'):
        manifest = s.fixed(f'{design}/manifest.json.gz')
        initial = manifest['starts']
        admitted = initial
        pairwise = {"/".join(pair): value for pair, value in manifest['pair_rms_distances'].items()}
        replacement = f'{design}/replacement-starts.json.gz'
        if input_path(REPORTED / replacement).is_file():
            screened = s.fixed(replacement)
            extra = {key: draw['start'] for key, draw in screened['draws'].items() if draw['disposition'] == 'eligible'}
            admitted = {key: initial[key] for key in screened['accepted_original']} | extra
            for i, (name, vector) in enumerate(admitted.items()):
                for other in list(admitted)[i + 1:]:
                    difference = [(a - b) ** 2 for a, b in zip(vector['normalized'], admitted[other]['normalized'], strict=True)]
                    pairwise[f'{name}/{other}'] = sqrt(fsum(difference) / len(difference))
        diagnostic = f'{design}/A-loose.json.gz'
        labels = list(dict.fromkeys([*initial, *admitted]))
        if input_path(REPORTED / diagnostic).is_file():
            labels.append(s.fixed(diagnostic)['start'])
        attempts[design], distances[design] = {}, pairwise
        for label in labels:
            fit = s.fixed(f'{design}/{label}.json.gz')
            report = fit['report']
            first = fit
            while 'previous_stage' in first:
                first = first['previous_stage']
            info = fit.get('diagnostics', {})
            bounds = info.get('active_bounds')
            gradient = None
            if 'jacobian_bound_normalized' in info:
                residual = [row['weighted_residual'] for row in fit['replay']['rows']]
                coordinates = fit['endpoint']['coordinates']
                gradients = [fsum(a * b for a, b in zip(column, residual, strict=True))
                             for column in zip(*info['jacobian_bound_normalized'], strict=True)]
                gradient = max(abs(min((d['bounds'][1] - d['origin']) / d['scale'],
                                       max((d['bounds'][0] - d['origin']) / d['scale'],
                                           -g * d['scale'] / (d['bounds'][1] - d['bounds'][0]))))
                               for g, d in zip(gradients, coordinates, strict=True))
            start_report = first['report']
            attempts[design][label] = dict(
                status=report['status'], initial_cost=start_report['initial_cost'] if start_report['residual_evaluations'] else None,
                objective=(fit.get('replay') or {}).get('cost'), active_bounds=bounds,
                solver_scale_projected_gradient_inf=gradient, gradient_tolerance=fit['controls']['gradient_tolerance'],
                endpoint=fit.get('endpoint_fingerprint'),
            )
    return attempts, distances


def mdea_properties(s):
    fixed = s.fixed('MDEA/properties.json.gz')
    tracking = s.read('analyses/round_7/results/C/salt/refit.json.gz')
    paired_scores = {}
    for group, unit in [('Kuranov', 'Pa'), ('Ermatchkov', 'Pa'), ('Xiao', 'Pa'),
                        ('Carson', 'J/mol'), ('corrected-Kamps', 'Pa')]:
        left, right = ({row['identity']: row for row in records['rows']
                         if row['group'] == group and row['unit'] == unit}
                        for records in (tracking, fixed))
        common = [i for i in right if i in left and available(left[i]) and available(right[i]) and right[i]['observed']]
        paired_scores[group] = dict(n=len(common), models=[
            dict(AARD_percent=aard((r[i]['value'], r[i]['observed']) for i in common),
                 bias_percent=100 * fsum(r[i]['value']/r[i]['observed'] - 1 for i in common) / len(common))
            for r in (left, right)
        ])
    endpoint = s.fixed('MDEA/A.json.gz')
    residual = {row['identity']: row['residual'] for row in endpoint['replay']['rows']}
    objectives = {weight: fsum(.5 * row['weight'] * residual[row['identity']] ** 2 for row in target['rows'])
                  for weight, target in tracking['objective'].items()}
    comparison = s.fixed('MDEA/property-comparisons/A.json.gz')
    literature = s.read('analyses/round_8/results/literature-populations.json.gz')['quantities']
    source_rows = set(map(str, literature['kuranov']['source_rows']))
    rows = [row for row in comparison['rows'] if row['group'] in ('Kuranov', 'Kuranov-binary', 'Kuranov-413K')
            and row['row']['source_row'] in source_rows] + [comparison['additional_Kuranov_72']]
    if {row['row']['source_row'] for row in rows} != source_rows:
        raise ValueError('Mismatched Kuranov published comparison rows')
    values = [(row['value'], row['observed']) for row in rows if available(row)]
    return dict(paired=paired_scores, objectives=objectives,
                kuranov=dict(available=len(values), AARD_percent=aard(values)))


def reported_grid_axes(s):
    result = {}
    for label, module, family in (('DEA', dea_model, 'DEA'), ('MDEA', mdea, 'MDEA'), ('AMP', amp_model, 'AMP_free')):
        fit = module.FIT_SETS['reported']
        selection = s.fixed(f'{family}/selection.json')
        record = s.fixed(f'{family}/{selection["selected"]}.json.gz')
        point, _ = retained_endpoint(fit)
        route = route_for(fit)
        stocks, loadings = grid_axes(route, route.bind(point))
        masses = {row['component_id']: row['fixed']['molar_mass']['value']['magnitude']
                  for row in record['endpoint']['parameters']['components']}
        amine = route.config['amine']
        stock_weights = [100 * stock[amine] * masses[amine] / fsum(n * masses[k] for k, n in stock.items())
                         for stock in stocks]
        result[label] = dict(stocks=len(stocks), loadings=len(loadings), maximum_loading=max(loadings),
                             stock_wt_percent=stock_weights,
                             temperatures=len({row['T'] for row in grid_states(stocks, loadings)}),
                             endpoint_fingerprint=record['endpoint_fingerprint'])
    return result


def historical_bicarbonate_profile(s):
    declaration = s.read('analyses/mea_parameter_bundle/results/reduced-refit/F2/current/unpenalized/declaration.json')
    coordinates = [row['identity'] for row in declaration['declared']
                   if row['identity'] != 'pair/bicarbonate-anion/water/k_ij']
    starts = {}
    for case, fit_set in (('low', 'bicarbonate-0.1325'), ('high', 'bicarbonate-1.0')):
        directory = mdea.FIT_SETS[fit_set]['endpoint'].parent
        starts[case] = {
            path.parent.parent.name: [row['identity'] for row in s.read(path)['coordinates']]
            for path in sorted(directory.glob('fit-*/stage-0/parameters.json.gz'))
        }
    return dict(mea_refitted_coordinates=coordinates, mdea_starts=starts)


def tied_phase_controls(s):
    return {
        family: {
            start: {key: phase_outcome(row['value']) for key, row in
                    s.fixed(f'{family}/controls/{start}.json.gz')['rows'].items()}
            for start in ENDPOINTS[family]
        }
        for family in ('DEA', 'AMP_free')
    }


def main():
    s = Records()
    attempts, distances = fit_attempts(s)
    s.write('shared/fit/display-summary.json.gz', dict(
        attempts=attempts, start_distances=distances, amp_enthalpy=amp_units(s),
        historical_bicarbonate_profile=historical_bicarbonate_profile(s), **fit_accounting(s, attempts),
    ))
    account = phase_accounting(s)
    amp_early = s.read('analyses/round_3/results/q1.json')['rows']
    mdea_early = s.read('analyses/round_3/results/q3.json')['rows']
    mdea_measured = s.read('analyses/mdea_mea_workflow/results/phase-search-421/measured-phase.json')
    s.write('shared/phase/display-summary.json.gz', dict(
        **account, grid_axes=reported_grid_axes(s), tied_controls=tied_phase_controls(s),
        mea_search=mea_search(s), mea_grid=s.fixed('MEA/screen/summary.json.gz')['grid'],
        dea_controls=dea(s), amp_controls=amp(s), amp_outcomes=amp_outcomes(s),
        amp_worked={family: phase_outcome(selected(s, family, 'controls/A.json.gz')['rows']['worked-state']['value'])
                    for family in ('AMP_free', 'AMP_fixed')},
        amp_early={fit: dict(
            attempted=len(amp_early),
            confirmed=sum(any(a['confirmed'] for a in row[fit]['attempts']) for row in amp_early),
        ) for fit in ('free', 'fixed')},
        mdea_early=[{key: row[key] for key in ('key', 'P_Pa', 'T_K', 'instability', 'reference', 'attempts')}
                    for row in mdea_early],
        mdea_historical_measured=[{key: row[key] for key in ('key', 'native_branch', 'supplied_branch', 'attempts')}
                                  for row in mdea_measured],
    ))
    covariance = s.read('analyses/mea_parameter_bundle/results/paper-evidence-341/uncertainty/covariance.json')
    mea_early = s.read('analyses/round_3/results/q4.json')
    readback = s.read('analyses/round_3/results/q8.json')
    amp_reference = s.read('analyses/mea_parameter_bundle/results/reference-states-428/amp.json')
    candidate = readback['dea']
    s.write('shared/properties/display-summary.json.gz', dict(
        shared=shared(s), kamps=kamps(s), mdea=mdea_properties(s), mdea_bubble=mdea_bubble(s, account),
        dea_density=dea_density(s), spread=endpoint_predictions(s),
        mea_mamun=s.fixed('E/MEA/replay.json.gz')['summary']['pressure']['Mamun2005']['AARD_percent'],
        mea_historical_covariance=covariance['native_correlation'],
        mea_early_reference={key: mea_early[key] for key in ('rows', 'heat_previous_kJ_mol', 'heat_change')},
        dea_alternative={key: candidate[key] for key in ('endpoint', 'chosen_cost', 'alternative_cost', 'rows', 'scores')},
        water_calibration=readback['water'],
        amp_historical_reference_state=amp_reference,
    ))


if __name__ == '__main__':
    main()
