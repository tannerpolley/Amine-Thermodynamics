"""Issue 140 source-constant control: preparation and 142-target replay; no fitting.

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
 timeout 1800 uv run --no-sync python <this-file> replay
"""
import base64
import copy
import csv
import hashlib
import importlib.metadata
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[1]
sys.path.insert(0, str(BUNDLE / 'calibration-misfit'))
import probe  # noqa: E402
import compare  # noqa: E402

s = probe.shared
ADOPTED = BUNDLE / 'results/selected-current-best-parameters.json'
RAW = BUNDLE / 'results/runs/temperature-reanchor-140'
probe.RECORD = ADOPTED
s.RUNS = RAW / 'replay-cache'
REFERENCE_COST = 32.99189726122113
IDS = ['pair/carbamate-anion/water/k_ij', 'pair/protonated-monoethanolamine/water/k_ij',
       'pair/bicarbonate-anion/water/k_ij', 'pair/carbamate-anion/protonated-monoethanolamine/k_ij']
SLOPE = IDS[1] + '/reciprocal_temperature_slope'
EPSILON = 'component/carbon-dioxide/dispersion_energy_over_k'


def save(path, value):
    path.write_text(json.dumps(s._jsonable(value), indent=2, allow_nan=False) + '\n')


def table(path, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def verify():
    s.verify_wheel()
    distribution = importlib.metadata.distribution('epcsaft')
    count = 0
    for name, digest, size in csv.reader(distribution.read_text('RECORD').splitlines()):
        if digest:
            algorithm, expected = digest.split('=', 1)
            data = Path(distribution.locate_file(name)).read_bytes()
            assert base64.urlsafe_b64encode(hashlib.new(algorithm, data).digest()).decode().rstrip('=') == expected, name
            assert len(data) == int(size), name
            count += 1
    origin = Path(probe.epcsaft.__file__).resolve()
    assert origin.is_relative_to((probe.W / '.venv').resolve()), origin
    assert s.sha256(ADOPTED) == '9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241'
    return {'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'installed_record_hashes': count,
            'module_origin': str(origin), 'direct_url': json.loads(distribution.read_text('direct_url.json'))}


def training():
    states = []
    for observation in probe.OBSERVATIONS:
        rec = {'T': observation['request']['temperature']['value'], 'identity': observation['identity']}
        targets = [t for t in observation['targets'] if compare.in_working_objective(rec, t)]
        if targets:
            assert rec['T'] <= 333.15
            o = copy.deepcopy(observation)
            o['targets'] = targets
            states.append(o)
    assert len(states) == 84 and sum(len(o['targets']) for o in states) == 142
    return states


def replay():
    environment = verify()
    states = training()
    clock = time.perf_counter()
    rows, checks = [], []
    with (RAW / 'replay-states.jsonl').open('w') as handle:
        for result in probe.evaluate(states=states):
            handle.write(json.dumps(result) + '\n')
            handle.flush()
            print(result['identity'], result['status'], round(result['wall_s'], 2), flush=True)
            checks.append({'identity': result['identity'], **result['check']})
            assert result['status'] == 'evaluated', result
            assert result['check']['tolerance_met'] and not result['check']['balance_errors'], result['check']
            assert result['check']['max_abs_stationarity'] <= 1e-10, result['check']
            for target, residual in zip(result['targets'], compare.residuals(result), strict=True):
                rows.append({'identity': result['identity'], 'target': target['identity'],
                    'source': target['source_identity'], 'temperature_k': result['T'],
                    'quantity': 'pressure' if residual[0] == 'p' else 'species',
                    'observed': target['observed'], 'predicted': compare.predicted(result, target),
                    'scaled_residual': residual[2], 'cost': .5 * residual[2] ** 2})
    cost = math.fsum(r['cost'] for r in rows)
    table(HERE / 'replay-targets.csv', rows)
    summary = {'environment': environment, 'states': len(checks), 'targets': len(rows), 'cost': cost,
        'reference_cost': REFERENCE_COST, 'difference': cost - REFERENCE_COST,
        'pressure_targets': sum(r['quantity'] == 'pressure' for r in rows),
        'species_targets': sum(r['quantity'] == 'species' for r in rows),
        'pressure_cost': math.fsum(r['cost'] for r in rows if r['quantity'] == 'pressure'),
        'species_cost': math.fsum(r['cost'] for r in rows if r['quantity'] == 'species'),
        'max_abs_stationarity': max(c['max_abs_stationarity'] for c in checks),
        'requested_tolerance_met': all(c['tolerance_met'] for c in checks),
        'balance_errors': sum(bool(c['balance_errors']) for c in checks),
        'wall_s': time.perf_counter() - clock,
        'parameter_sha256': s.sha256(ADOPTED), 'state_packet_sha256': s.sha256(s.STATE_PACKET)}
    save(HERE / 'replay.json', summary)
    assert abs(summary['difference']) <= 1e-8, summary
    print(json.dumps(summary), flush=True)


def prepare():
    environment = verify()
    contract_path = probe.W / 'data/reference/MEA/manifests/chemical_reaction_source_contract.json'
    contract = json.loads(contract_path.read_text())
    source = {r['reaction_id']: r for r in contract['reactions']}
    offsets = dict(zip(source, contract['common_source_standard_state']['source_to_common_ln_k_offsets']))
    adopted = s.parameter_mapping(ADOPTED)
    changes = {**{i: 0.0 for i in IDS + [SLOPE]}, EPSILON: 169.21}
    for rid in ('R2', 'R4', 'R5'):
        changes.update({f'reaction:{rid}:correlation:{k}': v + (offsets[rid] if rid == 'R2' and k == 'a' else 0.)
                        for k, v in source[rid]['correlation'].items() if k != 'kind'})
    restored = s.with_parameter_values(adopted, changes)
    # Value provenance changes with the source reset; old fit locators must not describe the new values.
    for node in s._identified(restored):
        if node['identity'] in changes and 'provenance' in node:
            node['provenance'] = {'source_id': 'issue-140-source-constant-control',
                                  'locator': 'preregistration.md: source reset and prescribed default starts'}
            node.pop('source_sha256', None)
    for reaction in restored['reaction_correlations']:
        rid = reaction['reaction_id']
        reaction['source'] = {'source_id': source[rid]['selected_source'],
            'locator': 'chemical_reaction_source_contract.json; preregistration.md: verified published coefficients'}
        reaction['source_sha256'] = 'sha256:' + s.sha256(contract_path)
        reaction['source_temperature_range_k'] = source[rid]['temperature_range_k']
        reaction['candidate_domain_id'] = 'mea-temperature-reanchor-293-15-to-353-15-k'
    restored['domains'].append({'domain_id': 'mea-temperature-reanchor-293-15-to-353-15-k',
        'kind': 'reported-conditions', 'temperature_min': {'magnitude': 293.15, 'unit': 'kelvin'},
        'temperature_max': {'magnitude': 353.15, 'unit': 'kelvin'}})
    restored['purpose'] = 'Issue 140 source-constant control default start; not fitted, adopted, or physically validated.'
    restored['document_id'] = 'mea-temperature-reanchor-140-source-constant-control'
    save(HERE / 'restored-source-parameters.json', restored)
    probe.epcsaft.Parameters.from_mapping(restored)
    table(HERE / 'parameter-changes.csv', [{'identity': k,
        'adopted': {**s.parameter_values(adopted), **s.reaction_values(adopted)}[k], 'restored': v,
        'role': 'free-coordinate default start' if k in IDS + [SLOPE] else 'fixed source'} for k, v in changes.items()])
    native = s._engine_reaction_records(training()[0]['request'], s.reaction_values(restored))
    checks = []
    for record in native:
        rid = record['reaction_id']
        record['engine_correlation']['temperature_min'] = 293.15
        record['engine_correlation']['temperature_max'] = 353.15
        polynomial = s._reaction_correlation(record, rid)
        c = source[rid]['correlation']
        for temperature in (293.15, 313.15, 333.15, 353.15):
            published = (-math.log(10.) * (c['a_k'] / temperature + c['b'] + c['c_per_k'] * temperature)
                         if rid == 'R5' else c['a'] + c['b_k'] / temperature
                         + c.get('c', 0.) * math.log(temperature) + c.get('d_per_k', 0.) * temperature)
            evaluated = (polynomial.a + polynomial.b / temperature
                         + polynomial.c * math.log(temperature / polynomial.reference_temperature)
                         + polynomial.d * temperature)
            native_offset = 0. if record['engine_reference']['source_basis'] == 'CommonMolalityInfiniteDilution' else offsets[rid]
            common = published + offsets[rid]
            difference = evaluated + native_offset - common
            assert abs(difference) < 5e-13, (rid, temperature, difference)
            checks.append({'reaction': rid, 'temperature_k': temperature, 'published_ln_k': published,
                'molality_offset': offsets[rid], 'common_molality_ln_k': common,
                'native_basis': record['engine_reference']['source_basis'], 'native_a': polynomial.a,
                'native_b_k': polynomial.b, 'native_c': polynomial.c, 'native_d_per_k': polynomial.d,
                'native_ln_k': evaluated, 'native_to_common_offset': native_offset,
                'difference_common_ln_k': difference,
                'source_extrapolation': not source[rid]['temperature_range_k'][0] <= temperature <= source[rid]['temperature_range_k'][1]})
    table(HERE / 'source-ln-k-checks.csv', checks)
    save(HERE / 'native-reaction-inputs.json', native)
    table(HERE / 'r5-source-rounding.csv', [{'temperature_k': r['temperature_k'],
        'bates_ln_k': r['published_ln_k'],
        'bottinger_table5_ln_k': -.8909 - 6166.11 / r['temperature_k'] - 9.8482e-4 * r['temperature_k'],
        'bottinger_minus_bates_ln_k': -.8909 - 6166.11 / r['temperature_k'] - 9.8482e-4 * r['temperature_k'] - r['published_ln_k']}
        for r in checks if r['reaction'] == 'R5'])
    rows = []
    for observation in training():
        for target in observation['targets']:
            quantity = 'pressure' if target['prediction_identity'] == 'co2-partial-pressure' else 'species'
            pool = compare.pooled_species(target['identity'])
            rows.append({'identity': observation['identity'], 'target': target['identity'],
                'source': target['source_identity'], 'source_sha256': target.get('source_hash', ''),
                'temperature_k': observation['request']['temperature']['value'], 'quantity': quantity,
                'observed': target['observed'], 'unit': target['unit'], 'basis': target['basis'],
                'operator': '+'.join(pool) if pool else target['prediction_identity'],
                'scale': .3 if quantity == 'pressure' else .1 * target['observed'] + .001,
                'prior_access': 'historical calibration; same unchanged objective', 'role': 'training-selection'})
    table(HERE / 'training-targets.csv', rows)
    canonical = list(csv.DictReader(s.CANONICAL_VLE.open()))
    pressure80 = [r['observation_id'] for r in canonical if r['active_view_member'] == 'yes' and float(r['temperature_canonical_C']) == 80]
    outside = [r['observation_id'] for r in canonical if r['active_view_member'] == 'yes' and 100 <= float(r['temperature_canonical_C']) <= 120]
    transfer = {w: [r['observation_id'] for r in canonical if r['source_key'] == 'Aronu2011' and float(r['MEA_weight_fraction']) == w] for w in (.15, .45)}
    species80 = [{'identity': o['identity'], 'target': t['identity'], 'operator': compare.pooled_species(t['identity']) or t['prediction_identity']}
                 for o in probe.OBSERVATIONS if o['request']['temperature']['value'] == 353.15
                 for t in o['targets'] if t['prediction_identity'] != 'co2-partial-pressure']
    assert (len(pressure80), len(outside), len(transfer[.15]), len(transfer[.45]), len(species80)) == (21, 57, 33, 37, 11)
    heat_path = BUNDLE / 'data/input/calorimetry-observation-partition.csv'
    heat = [dict((k, r[k]) for k in ('record_id', 'source', 'temperature_C', 'previous_loading_mol_per_mol_mea',
             'co2_loading_mol_per_mol_mea')) for r in csv.DictReader(heat_path.open()) if r['regression_eligible'] == 'true']
    save(HERE / 'assessment-row-ids.json', {'primary_80c_pressure': pressure80,
        'secondary_80c_pressure_19': [i for i in pressure80 if i not in ('vle_obs_0206', 'vle_obs_0211')],
        'packet_80c_species': species80, 'outside_100_120c_pressure': outside,
        'outside_15wt_pressure': transfer[.15], 'outside_45wt_pressure': transfer[.45],
        'outside_objective_heat': heat})
    fit_inputs = training()
    for observation in fit_inputs:
        request = observation['request']
        # Replay keeps historical same-T continuation; fitting starts use only the declared feed.
        feed = dict(zip(s.COMPONENT_IDS, request['reaction_system']['feed_amounts_mol'], strict=True))
        phases = []
        for phase in request['phases']:
            support = s.COMPONENT_IDS if phase['support']['kind'] == 'all_components' else phase['support']['component_ids']
            total = math.fsum(feed[i] for i in support)
            phases.append({'role': phase['fluid_role'], 'supported_component_ids': list(support),
                           'mole_fractions': [feed[i] / total for i in support]})
        request['continuation'] = {'state': {'phases': phases}}
        if request['pressure']['role'] == 'solved':
            lower, upper = request['pressure']['bounds']
            request['pressure']['initial'] = math.sqrt(lower * upper)
    save(RAW / 'training-inputs.json', fit_inputs)
    inputs = [ADOPTED, s.STATE_PACKET, s.CANONICAL_VLE, contract_path, Path(probe.__file__),
              Path(compare.__file__), Path(s.__file__), Path(__file__), heat_path,
              BUNDLE / 'calibration-misfit/refit.py', BUNDLE / 'model-d/fit.py',
              probe.W / 'src/MEA/common/mea_source_contracts.py',
              HERE / 'restored-source-parameters.json', HERE / 'training-targets.csv', HERE / 'assessment-row-ids.json',
              RAW / 'training-inputs.json', HERE / 'fixed-parameter-ancestry.csv', HERE / 'preregistration.md']
    save(HERE / 'input-hashes.json', {'base_commit': 'd730dc80bbe3b11385c43c2d8e7f3c90b60f52ab',
        'hash_convention': 'shared_evaluation.sha256: decompressed content for .json.gz; file bytes otherwise',
        'state_packet_file_sha256': hashlib.sha256(s.STATE_PACKET.read_bytes()).hexdigest(),
        'environment': environment, 'hashes': {str(p.relative_to(probe.W)): s.sha256(p) for p in inputs}})
    print('Prepared 142 low-temperature targets and source polynomial checks; no fit or assessment performed.', flush=True)


if __name__ == '__main__':
    RAW.mkdir(parents=True, exist_ok=True)
    if sys.argv[1:] == ['replay']:
        replay()
    elif sys.argv[1:] == ['prepare']:
        prepare()
    else:
        raise SystemExit('prepare | replay')
