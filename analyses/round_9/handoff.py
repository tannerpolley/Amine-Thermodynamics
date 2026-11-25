"""Recompute round-9 quantities from retained row records without refitting."""
from collections import Counter
import gzip
from hashlib import sha256
import json
from math import fsum, isclose, log
from pathlib import Path
import sys

from notebook import render

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'analyses/fixed_reaction_reference/'
RESULTS = 'analyses/round_9/results/'
WHEEL = 'c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb'
AMP_H = 'AMP-hydrolysis-enthalpy-increment'


class Sources:
    def __init__(self):
        self.hashes = {}

    def read(self, path):
        data = (ROOT / path).read_bytes()
        self.hashes[path] = sha256(data).hexdigest()
        return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)

    def fixed(self, path):
        return self.read(BASE + 'results/' + path)

    def new(self, path):
        value = self.read(RESULTS + path)
        assert value['wheel'] == WHEEL
        return value


def dea(s):
    payload = s.new('dea-phase-controls.json.gz')
    record = dict(payload['value'], wall_s=payload['wall_s'])
    selected = s.fixed('DEA/selection.json')
    assert record['endpoint_fingerprint'] == selected['endpoint_fingerprint']
    for q in record['rows']:
        total = fsum(p['amount_mol'] for p in q['phases'])
        for phase, roots in zip(q['phases'], q['split']['roots'], strict=True):
            phase['true_mole_fraction'] = phase['amount_mol'] / total
            assert isclose(phase['molar_volume_m3_mol'] * phase['density_mol_m3'], 1., rel_tol=1e-14)
            assert any(r.get('returned') == 'liquid'
                       and r['log_density_distance'] <= log(1.01)
                       and r['relative_pressure_residual'] <= q['row_tolerance'] for r in roots)
        q['max_reaction_residual'] = max(abs(r['residual']) for r in q['reaction_contractions'])
        q['max_interphase_residual'] = max(map(abs, q['interphase_residuals'].values()))
        q['declared_confirmed'] = sum(a['confirmed'] for a in q['declared_search_attempts'])
        q['registry_growth_confirmed'] = sum(a['confirmed'] for a in q['registry_growth_attempts'])
    worked = min(record['rows'], key=lambda q: q['split']['Gibbs_decrease_over_RT_mol'])
    assert worked['key'] == 'weiland-1998:32:problem'
    return dict(record, worked_state=worked['key'], denominator='sum of daughter true-species molar amounts')


def amp(s):
    payload = s.new('amp-phase-controls.json.gz')
    record = dict(payload['value'], wall_s=payload['wall_s'])
    assert record['endpoint_fingerprint'] == s.fixed('AMP_free/selection.json')['endpoint_fingerprint']
    for q in record['rows']:
        witness = q['witness']
        if q['key'] != 'worked-state':
            assert q['P_Pa'] == 1000 * float(q['source']['P_total_kPa'])
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
        assert lv['requested_tolerance_met'] and lv['physical_checks_pass'] and min(lv['amounts_mol']) > 0
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


def accounting(s):
    h = s.read(BASE + 'manuscript-handoff.json')
    endpoints = {}
    for amine, attempts in h['fit_attempts'].items():
        endpoints[amine] = {label: endpoint_stages(s.fixed(f'{amine}/{label}.json.gz')) for label in attempts}
    for label in ('A-continuation', 'A-descent-continuation'):
        endpoints['MDEA'][label] = endpoint_stages(s.fixed(f'MDEA/stationarity/{label}.json.gz'))

    draws = s.fixed('MDEA/replacement-starts.json.gz')
    initial = h['fit_attempts']['MDEA']
    manifest = s.fixed('MDEA/manifest.json.gz')
    initial_draws = {q['draw'] for q in manifest['starts'].values() if q['draw'] is not None}
    tested = initial_draws | {q['start']['draw'] for q in draws['draws'].values()}
    assert tested | set(draws['remaining']) == set(range(64))
    start_counts = dict(inherited=draws['accepted_original'], drawn=64, tested=len(tested),
                        evaluable=[k for k, q in draws['draws'].items() if q['disposition'] == 'eligible'],
                        untested_draws=draws['remaining'], fitted_endpoints=[k for k,q in initial.items() if q['endpoint']])
    start_counts['A_AARD_percent'] = {
        g: h['quantities'][f'MDEA {g} Pa all AARD_percent']['new'] for g in ('Kuranov', 'Ermatchkov')
    }
    assert start_counts['inherited'] == ['A'] and start_counts['evaluable'] == ['LHS-53']
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
    inventory = {q['key']: q for q in s.fixed('MDEA/screen/selected/declared/state-inventory.json.gz')['rows']}
    crosswalk = s.read('analyses/mdea_mea_workflow/results/phase-search-421/observation-crosswalk.json')
    sources = {q['identity']: q['row'] for pool in manifest['rows'].values() for q in pool}
    crosswalk = {q['key']: q['identity'] for q in crosswalk}
    detections = Counter(q.get('same_calculation_as', q['key']) for q in screen['rows'] if q['descent'])
    assert set(detections) == {q['key'] for q in screen['classifications']}
    states = []
    for q in screen['classifications']:
        key = q['key']
        inv = inventory[key]
        identity = crosswalk.get(key, key.rsplit(':', 1)[0].removesuffix(':1'))
        source = sources[identity]
        pressure = inv.get('declared_pressure_Pa', inv.get('search_Pa'))
        assert isclose(pressure, q['pressure_Pa'], rel_tol=1e-13)
        if inv['pressure_basis'] == 'bubble scaled':
            basis = 'calculated'
        elif source['source_key'] in ('BottingerMDEA2008', 'Merkley1987'):
            basis = 'assigned'
        else:
            basis = 'measured'
            assert isclose(pressure, 1e6*float(source['pressure_MPa']), rel_tol=1e-13)
        states.append(dict(key=key, T_K=q['temperature_K'], source=source, pressure_Pa=pressure,
                           pressure_basis=basis, detections=detections[key],
                           confirmed=sum(a['confirmed'] for a in q['attempts']), attempts=len(q['attempts'])))
    assert (sum(detections.values()), len(states)) == (80, 27)
    return dict(coverage=coverage, mdea_start_counts=start_counts, endpoint_stages=endpoints,
                mdea_detections=sum(detections.values()), mdea_distinct_states=states)


def paired(before, after, n):
    left, right = ({r['identity']: r for r in rows} for rows in (before, after))
    assert len(left) == len(right) == n and left.keys() == right.keys()
    assert all(left[k]['observed'] == right[k]['observed'] and left[k]['row'] == right[k]['row'] for k in left)
    common = [k for k in left if all(r[k]['status'] == 'Available' and r[k]['value'] is not None for r in (left, right))]
    outputs = {}
    for name, rows in (('salt-anchored', left), ('MEA-fitted', right)):
        delta = [100*(rows[k]['value']/rows[k]['observed']-1) for k in common]
        outputs[name] = dict(AARD_percent=fsum(map(abs, delta))/len(delta) if delta else None,
                             bias_percent=fsum(delta)/len(delta) if delta else None,
                             unavailable=[q for q in rows.values() if q['status'] != 'Available' or q['value'] is None])
    return dict(requested=n, common=common, models=outputs)


def shared(s):
    quantities, fits, assessment_seconds = {}, {}, {}
    mea = s.fixed('E/MEA/replay.json.gz')
    mdea = s.fixed('MDEA/properties.json.gz')
    baselines = {'MEA': {'legacy-47': [q for q in mea['rows'] if q['group'] == 'common149' and q['unit'] == 'Pa'],
                         'Mamun2005': [q for q in mea['rows'] if mea['pressure_population'].get(q['identity'], {}).get('source_key') == 'Mamun2005']},
                 'MDEA': {g: [q for q in mdea['rows'] if q['group'] == g] for g in ('Kuranov', 'Ermatchkov', 'Carson')}}
    counts = {'legacy-47': 47, 'Mamun2005': 19, 'Kuranov': 66, 'Ermatchkov': 101, 'Carson': 40}
    for name, before in baselines.items():
        fit = s.new(f'{name}-shared-fit.json.gz')
        assess = s.new(f'{name}-shared-assessment.json.gz')
        assert fit['reference_pressure_pa'] == 100000 and fit['replay_passed']
        assert assess['endpoint_fingerprint'] == fit['endpoint_fingerprint']
        fits[name] = endpoint_stages(fit)
        assessment_seconds[name] = assess['wall_s']
        for group, rows in before.items():
            quantities[f'{name} {group}'] = paired(rows, assess['rows'][group], counts[group])
    historical = s.read('analyses/round_8/results/salt-and-weighting.json.gz')['quantities']['properties']
    tradeoff = {g: {k: historical[g][k]['matched']['AARD_percent']
                    for k in ('historical/incumbent', 'salt/incumbent')} for g in ('Kuranov', 'Ermatchkov')}
    phase_record = s.new('mdea-phase-controls.json.gz')
    phases = phase_record['value']
    for case in phases.values():
        for model in case['models'].values():
            model['outcome'] = ('unavailable' if 'refusal' in model else
                                'confirmed split' if any(a['confirmed'] for a in model['attempts']) else
                                'unresolved phase identity' if model['instability'] == 'resolved descent' else model['instability'])
    return dict(pressure_reference_Pa=100000, comparisons=quantities, fit_stages=fits, historical_tracking_tradeoff=tradeoff,
                phase_controls=phases, phase_wall_s=phase_record['wall_s'],
                assessment_wall_s=assessment_seconds,
                fit_projection_s=fits['MEA'][0]['wall_seconds'] +
                                 s.fixed('MDEA/projection.json')['designs']['MDEA']['remaining_fit_s'])


def kamps(s):
    rows = [q for q in s.fixed('MDEA/property-comparisons/A.json.gz')['rows'] if q['group'] == 'corrected-Kamps']
    additional, = [q for q in rows if q['identity'] == 'comparison:113']
    assert len(rows) == 28 and all(q['status'] == 'Available' for q in rows)
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
        fitted_increment = -8.31446261815324*(final-source['source_law']['b'])
        assert isclose(fitted_increment, fit['endpoint']['coordinates'][index]['origin'] + offset, abs_tol=1e-9)
        values[label] = dict(coordinate_index=index, offset_J_mol=offset, physical_bounds_J_mol=physical,
                             fit_bounds_J_mol=coord['bounds'], endpoint_increment_J_mol=fitted_increment)
    return values


def main(check):
    src = Sources()
    quantities = {
        'R1 DEA two-liquid certificates': dea(src),
        'R2 AMP early and reported pressure controls': amp(src),
        'R3 start, endpoint and search accounting': accounting(src),
        'R4 shared interactions at 100 kPa': shared(src),
        'R6 corrected Kamps pressure comparisons': kamps(src),
        'R7 AMP hydrolysis enthalpy increment': amp_units(src),
    }
    path = HERE / 'manuscript-handoff.json'
    result = dict(study_wheel_sha256=WHEEL, quantities=quantities, sources=src.hashes)
    notebook = HERE / 'notebook.qmd'
    presentation = render(quantities)
    if check:
        retained = json.loads(path.read_text())
        assert retained['study_wheel_sha256'] == WHEEL
        for key, value in quantities.items():
            assert value == retained['quantities'][key], f'{key}: recomputed quantity differs'
        assert result == retained, 'Round-9 contributor or inventory changed'
        assert notebook.read_text() == presentation, 'Round-9 notebook is out of date'
    else:
        path.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
        notebook.write_text(presentation)
    print(f'Round-9 handoff verified {len(quantities)} quantity groups from {len(src.hashes)} records')


if __name__ == '__main__':
    main('--check' in sys.argv[1:])
