"""Write display summaries from the retained output of the fit, phase and property stages."""

from collections import Counter
from math import fsum, sqrt

from .records import RESULTS, input_path, read

from . import amp as amp_model, dea as dea_model, mdea
from .fit import retained_endpoint, route_for, save
from .model import REPORTED, ROOT
from .phase import grid_axes, grid_states, retained_measured_grid
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
    quantities = {}
    mea = s.fixed('E/MEA/replay.json.gz')
    mdea = s.fixed('MDEA/properties.json.gz')
    baselines = {'MEA': {'legacy-47': [q for q in mea['rows'] if q['group'] == 'common149' and q['unit'] == 'Pa'],
                         'Mamun2005': [q for q in mea['rows'] if mea['pressure_population'].get(q['identity'], {}).get('source_key') == 'Mamun2005']},
                 'MDEA': {g: [q for q in mdea['rows'] if q['group'] == g] for g in ('Kuranov', 'Ermatchkov', 'Carson')}}
    for name, before in baselines.items():
        directory = RESULTS / name.lower() / 'water-bicarbonate-ablation'
        fit = s.read(directory / 'fit/A.json.gz')
        assess = s.read(directory / 'properties/assessment.json.gz')
        if {fit['wheel'], assess['wheel']} != {s.wheel} or assess['endpoint_fingerprint'] != fit['endpoint_fingerprint']:
            raise ValueError(f'{name}: ablation assessment does not match the held fit')
        for group, rows in before.items():
            quantities[f'{name} {group}'] = paired(rows, assess['rows'][group])
    return dict(comparisons=quantities)


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
    manifest = s.fixed('AMP_free/manifest.json.gz')
    index = manifest['coordinate_order'].index(AMP_H)
    coord = manifest['start_A_declaration']['coordinates'][index]
    physical = source['bounds']['enthalpy']
    offset = physical[0] - coord['bounds'][0]
    if [value + offset for value in coord['bounds']] != physical:
        raise ValueError('AMP enthalpy bounds differ before and after reference conversion')
    return {'AMP_free': dict(physical_bounds_J_mol=physical)}


def aard(pairs):
    errors = [abs((calc - observed) / observed) * 100 for calc, observed in pairs]
    return fsum(errors) / len(errors) if errors else None


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
    for design in ('MEA', 'DEA', 'MDEA', 'AMP_free'):
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
    comparison = s.fixed('MDEA/property-comparisons/A.json.gz')
    literature = s.read('analyses/round_8/results/literature-populations.json.gz')['quantities']
    source_rows = set(map(str, literature['kuranov']['source_rows']))
    rows = [row for row in comparison['rows'] if row['group'] in ('Kuranov', 'Kuranov-binary', 'Kuranov-413K')
            and row['row']['source_row'] in source_rows] + [comparison['additional_Kuranov_72']]
    if {row['row']['source_row'] for row in rows} != source_rows:
        raise ValueError('Mismatched Kuranov published comparison rows')
    values = [(row['value'], row['observed']) for row in rows if available(row)]
    return dict(kuranov=dict(available=len(values), AARD_percent=aard(values)))


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


def main():
    s = Records()
    attempts, distances = fit_attempts(s)
    s.write('shared/fit/display-summary.json.gz', dict(
        attempts=attempts, start_distances=distances, amp_enthalpy=amp_units(s),
    ))
    account = phase_accounting(s)
    s.write('shared/phase/display-summary.json.gz', dict(
        **account, grid_axes=reported_grid_axes(s), mea_search=mea_search(s),
        dea_controls=dea(s), amp_controls=amp(s), amp_outcomes=amp_outcomes(s),
    ))
    selected_fits = {name: dict(endpoint_fingerprints={
        label: s.fixed(f'{name}/{label}.json.gz')['endpoint_fingerprint'] for label in ENDPOINTS[name]
    }) for name in ('MEA', 'DEA', 'AMP_free')}
    s.write('shared/properties/display-summary.json.gz', dict(
        shared=shared(s), kamps=kamps(s), mdea=mdea_properties(s), mdea_bubble=mdea_bubble(s, account),
        spread=selected_fits,
        mea_mamun=s.fixed('E/MEA/replay.json.gz')['summary']['pressure']['Mamun2005']['AARD_percent'],
        water_calibration=s.read('analyses/round_3/results/q8.json')['water'],
    ))
    screen_path = 'mdea/reported/phase/MDEA/screen/selected/declared/summary.json.gz'
    screen = s.read(RESULTS / screen_path)
    fit = mdea.FIT_SETS['reported']
    point, selection = retained_endpoint(fit)
    if (screen['wheel'], screen['endpoint_fingerprint']) != (s.wheel, selection['endpoint_fingerprint']):
        raise ValueError('MDEA restricted grid uses a different wheel or endpoint')
    route = route_for(fit)
    s.write('mdea/reported/phase/diagnosis/restricted-grid.json.gz', dict(
        endpoint_fingerprint=selection['endpoint_fingerprint'], source=screen_path,
        **retained_measured_grid(route, route.bind(point), screen),
    ))


if __name__ == '__main__':
    main()
