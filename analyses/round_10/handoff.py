"""Recompute the round-10 quantities from retained row records."""
from collections import Counter, defaultdict
from csv import DictReader
import gzip
from hashlib import sha256
import json
from math import fsum, isclose
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXED = 'analyses/fixed_reaction_reference/results/'
ROUND9 = 'analyses/round_9/'
WHEEL = 'c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb'
ENDPOINTS = {
    'MEA': ('A', 'B', 'LHS-21'),
    'DEA': ('A', 'B', 'C'),
    'AMP_free': ('A', 'LHS-06', 'LHS-45'),
    'MDEA': ('A', 'A-continuation', 'A-descent-continuation', 'LHS-53'),
}


class Sources:
    def __init__(self):
        self.hashes = {}

    def read_bytes(self, path):
        data = (ROOT / path).read_bytes()
        self.hashes[path] = sha256(data).hexdigest()
        return data

    def read(self, path):
        data = self.read_bytes(path)
        return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)

    def fixed(self, path):
        record = self.read(FIXED + path)
        assert record.get('wheel', WHEEL) == WHEEL
        return record


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
                add('corrected-Kamps (27 common rows)', r)
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
    assert pure['engine']['wheel_sha256'] == WHEEL
    pappas = [dict(identity=f"Pappa2006:{i}", group='Pappa2006', unit='Pa',
                   observed=q['observed'], value=q['predicted'], status=q['status'])
              for i, q in enumerate(pure['pure']['rows']) if q['campaign'] == 'Pappa2006']
    output = {}
    for design, labels in ENDPOINTS.items():
        case, runtimes, fingerprints, source_wheels, pure_amp = {}, {}, {}, {}, []
        selected = s.fixed(f'{design}/selection.json')
        assert selected['selected'] == 'A'
        for label in labels:
            prefix = 'stationarity/' if label.endswith('continuation') else ''
            # A-continuation was obtained on an earlier wheel. Its vector is
            # read unchanged and all round-10 predictions use the study wheel.
            fit = s.read(FIXED + f'{design}/{prefix}{label}.json.gz')
            source_wheels[label] = fit['wheel']
            record = s.read(f'analyses/round_10/results/{design}-{label}.json.gz')
            assert record['wheel'] == WHEEL and record['reference_pressure_Pa'] == 100000
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
        assert fingerprints['A'] == selected['endpoint_fingerprint']
        assert all(c == pure_amp[0] for c in pure_amp)
        assert all(groups.keys() == case['A'].keys() for groups in case.values())
        span = labels[1:] if design == 'MDEA' else labels
        groups = {g: comparison({label: pools[g] for label, pools in case.items()}, span) for g in case['A']}
        output[design] = dict(groups=groups, replay_seconds=runtimes, endpoint_fingerprints=fingerprints,
                              endpoint_source_wheel_sha256=source_wheels)
    checks = {
        'MEA': {'Canonical pressures outside objective': 112, 'Hot canonical pressures': 54,
                'Hot Wagner pressures': 12, 'Hot pressures including Wagner': 66, 'Mamun2005 (outside objective)': 19,
                'Kim2014 (hot)': 7, 'Vinjarapu2024 (hot)': 5, 'Kim2007 flagged (hot)': 4},
        'DEA': {'Lawson-394K': 7, 'Lawson-VIII': 10, 'Cai': 9, 'Horstmann': 14},
        'AMP_free': {'kundu': 51, 'tong-baseline': 5, 'Pappa2006': 23},
        'MDEA': {'Kuranov': 66, 'Ermatchkov': 101, 'Carson': 40},
    }
    for design, groups in checks.items():
        for group, count in groups.items():
            assert output[design]['groups'][group]['requested'] == count, (design, group)
    return output


def selected(s, design, path):
    record = s.fixed(f'{design}/{path}')
    assert record['endpoint_fingerprint'] == s.fixed(f'{design}/selection.json')['endpoint_fingerprint']
    return record


def mea_search(s):
    census = selected(s, 'MEA', 'screen/census.json.gz')['data']['rows']
    grid = selected(s, 'MEA', 'screen/grid.json.gz')['data']
    batches = sorted((ROOT / FIXED / 'E/MEA/measured').glob('*.json.gz'))
    measured = [row for batch in batches for row in s.read(str(batch.relative_to(ROOT)))]
    result = dict(liquid_grid=dict(completed=sum(q['available'] for q in grid), attempted=len(grid)),
                  census=dict(attempted=len(census), outcomes=dict(Counter(q['classification'] for q in census))),
                  measured=dict(completed=sum(q['available'] for q in measured), attempted=len(measured)))
    summary = selected(s, 'MEA', 'screen/summary.json.gz')
    assert result['census'] == dict(attempted=162, outcomes={'passed-two-phase': 149, 'passed-single-liquid': 13})
    assert result['liquid_grid'] == dict(attempted=2484, completed=2483)
    assert result['measured'] == dict(attempted=321, completed=246)
    assert result['measured']['completed'] == summary['measured']['available']
    return result


def amp_outcomes(s):
    record = s.read(ROUND9 + 'results/amp-phase-controls.json.gz')
    assert record['wheel'] == WHEEL
    assert record['value']['endpoint_fingerprint'] == s.fixed('AMP_free/selection.json')['endpoint_fingerprint']
    outcomes = {}
    for row in record['value']['rows']:
        if row['key'] == 'worked-state':
            continue
        assert row['P_Pa'] == 1000 * float(row['source']['P_total_kPa'])
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
    assert Counter(r['outcome'] for r in outcomes.values()) == {
        'L+V passed; L+L unresolved': 1, 'Vapor-directed; root unqualified': 3, 'No resolved descent': 2}
    return outcomes


def dea_density(s):
    record = s.read(ROUND9 + 'results/dea-phase-controls.json.gz')
    densities = selected(s, 'DEA', 'property-comparisons/selected.json.gz')
    assert record['wheel'] == WHEEL and record['value']['endpoint_fingerprint'] == densities['endpoint_fingerprint']
    by_id = {q['identity']: q for q in densities['rows'] if q['group'] == 'Weiland'}
    rows = []
    for case in record['value']['rows']:
        q = by_id[case['key'].removesuffix(':problem')]
        deposit_id = int(q['identity'].split(':')[1])
        source_row = int(q['row']['source_row'])
        assert source_row == deposit_id + 1
        assert q['status'] == 'Available' and q['T_K'] == case['T_K']
        assert float(q['row']['alpha_mol_CO2_per_mol_DEA']) == case['loading']
        assert isclose(float(q['row']['DEA_mass_percent']), case['unloaded_wt_percent'], rel_tol=1e-12)
        daughters = case['phases']
        assert isclose(fsum(p['mass_fraction'] for p in daughters), 1, rel_tol=1e-12)
        bulk = 1 / fsum(p['mass_fraction'] / p['density_kg_m3'] for p in daughters)
        rows.append(dict(key=case['key'], deposit_id=deposit_id, processed_source_row=source_row,
                         T_K=case['T_K'], pressure_Pa=case['P_Pa'], pressure_basis=case['pressure_basis'],
                         observed_kg_m3=q['observed'], single_liquid_kg_m3=q['value'], two_liquid_kg_m3=bulk))
    assert len(rows) == 4 and all(row['pressure_Pa'] == 101325 for row in rows)
    return dict(rows=rows, AARD_percent={model: aard((r[model+'_kg_m3'], r['observed_kg_m3']) for r in rows)
                                        for model in ('single_liquid', 'two_liquid')})


def mdea_bubble(s):
    screen = selected(s, 'MDEA', 'screen/selected/declared/summary.json.gz')
    inventory = selected(s, 'MDEA', 'screen/selected/declared/state-inventory.json.gz')
    pressure_basis = s.read(ROUND9+'manuscript-handoff.json')['quantities']['R3 start, endpoint and search accounting']
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
    assert len(output) == 10
    return output


def main(check):
    from notebook import render

    src = Sources()
    quantities = {
        'K1 Endpoint prediction spread': endpoint_predictions(src),
        'K2 MEA search parent assemblages': mea_search(src),
        'K2 AMP control outcomes': amp_outcomes(src),
        'K3 DEA measured and calculated densities': dea_density(src),
        'K4 MDEA bubble pressures at measured descent states': mdea_bubble(src),
    }
    path = HERE / 'manuscript-handoff.json'
    notebook = HERE / 'notebook.qmd'
    result = dict(study_wheel_sha256=WHEEL, quantities=quantities, sources=src.hashes)
    presentation = render(quantities)
    if check:
        retained = json.loads(path.read_text())
        for key, value in quantities.items():
            assert value == retained['quantities'][key], f'{key}: recomputed quantity differs'
        assert result == retained, 'Round-10 contributor or inventory changed'
        assert notebook.read_text() == presentation, 'Round-10 notebook is out of date'
    else:
        path.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
        notebook.write_text(presentation)
    print(f'Round-10 handoff verified {len(quantities)} quantity groups from {len(src.hashes)} records')


if __name__ == '__main__':
    main('--check' in sys.argv[1:])
