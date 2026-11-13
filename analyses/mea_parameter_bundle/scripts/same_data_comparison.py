"""Issue 339: qualify explicit Born declaration against retained exact-record predictions."""
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

BUNDLE = Path(__file__).resolve().parents[1]
ROOT = BUNDLE.parents[1]
OUT = BUNDLE / 'results/same-data-comparison'
REFERENCE_COMMIT = '8d6e261'


def historical(path):
    return subprocess.check_output(['git', 'show', f'{REFERENCE_COMMIT}:{path}'], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def qualify():
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    import shared_evaluation as s
    import epcsaft
    s.verify_wheel()
    original = OUT / 'polley-2026-parameters.json'
    assert digest(original.read_bytes()) == '868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be'
    mapping = json.loads(original.read_bytes())
    family = next(f for f in mapping['model_families'] if f['kind'] == 'electrolyte')
    assert 'c_shell' not in family and 'c_dielectric' not in family
    family.update(c_shell=1.0, c_dielectric=1.0)
    translated = OUT / 'polley-2026-explicit-born.json'
    translated.write_text(json.dumps(mapping, sort_keys=True, separators=(',', ':')) + '\n')
    raw = historical('analyses/mea_parameter_bundle/data/input/state-packet.json.gz')
    packet_bytes = gzip.decompress(raw)
    assert digest(packet_bytes) == '86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448'
    (OUT / 'qualification-inputs.json.gz').write_bytes(raw)
    observations = s.expand_state_packet(json.loads(packet_bytes))['observations']
    reference_bytes = historical('analyses/mea_parameter_bundle/calibration-misfit/variant-states.csv')
    refs = [r for r in csv.DictReader(io.StringIO(reference_bytes.decode())) if r['variant'] == 'adopted']
    (OUT / 'qualification-reference.csv').write_bytes(reference_bytes)
    assert all(r['parameter_sha256'] == digest(original.read_bytes()) for r in refs)
    result = dict(original_sha256=digest(original.read_bytes()), translated_sha256=digest(translated.read_bytes()),
                  engine_commit=s.ENGINE_COMMIT, engine_wheel_sha256=s.ENGINE_WHEEL_SHA256,
                  reference_commit=REFERENCE_COMMIT, reference_sha256=digest(reference_bytes),
                  original_input_sha256=digest(packet_bytes), relative_limit=1e-8,
                  limit_origin='issue #339; cross-wheel replay #255', scored_observations=0,
                  heat_gate=False, status='not qualified', comparisons=[])
    s.RUNS = OUT / 'qualification-cache'
    try:
        model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    except epcsaft.ParameterError as error:
        result.update(status='refused translated record', exception_type=type(error).__name__, message=str(error))
        s.write_json(OUT / 'translation-qualification.json', result)
        print(json.dumps(result, indent=2), flush=True)
        return
    for ref in refs:
        observation = next(o for o in observations if o['identity'] == ref['identity'])
        state = s.evaluate_state(model, observation['request'], s.reaction_values(mapping), ref['identity'], [],
                                 mapping=mapping, parameter_path=translated, model_fingerprint=s.parameter_fingerprint(mapping))
        s.write_json(OUT / 'qualification-state.json', state)
        prediction = state['predictions'].get('co2-partial-pressure')
        expected = float(ref['predicted'])
        error = abs(prediction / expected - 1) if prediction is not None else None
        row = dict(identity=ref['identity'], quantity='CO2 partial pressure', unit='Pa',
                   reference=expected, translated=prediction, relative_error=error, status=state['status'])
        result['comparisons'].append(row)
        if error is None or error > 1e-8:
            result.update(status='stopped: first differing quantity', first_difference=row)
            break
    else:
        result['status'] = 'pressures pass; species and heat qualification still required'
    s.write_json(OUT / 'translation-qualification.json', result)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__' and sys.argv[1:] != ['tables']:
    qualify()


def tables():
    """Recalculate only deviations from retained pinned-wheel predictions."""
    import math
    evidence = BUNDLE / 'results/adoption-297/paper-evidence'
    rows = list(csv.DictReader((evidence / 'canonical-pressure.csv').open()))
    matched = [r for r in rows if r['source'] == 'Mamun2005']
    source_path = ROOT / 'data/reference/MEA/observations/vapor_liquid_equilibrium/Mamun_2005_VLE.csv'
    source = list(csv.DictReader(source_path.open(encoding='utf-8-sig')))
    assert len(matched) == len(source) == 19
    assert [r['identity'] for r in matched] == [f'canonical:vle_obs_{i:04}' for i in range(246, 265)]
    for row, original in zip(matched, source, strict=True):
        assert float(row['observed']) == float(original['CO2_pressure']) * 1000
        assert float(row['temperature_K']) == float(original['temperature']) + 273.15
        assert row['status'] == 'Available'
        assert row['record_sha256'] == 'f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97'
    aard = math.fsum(abs(float(r['predicted']) / float(r['observed']) - 1) for r in matched) * 100 / len(matched)
    assert abs(aard - 19.4320747) < 5e-8  # independent source-inventory calculation, rounded to 7 decimals
    fitted = list(csv.DictReader((evidence / 'fitted-rows.csv').open()))
    assert not any(r['target'] == f['id'] for r in matched for f in fitted)
    with (OUT / 'matched-pressure-rows.csv').open('w') as handle:
        writer = csv.DictWriter(handle, matched[0].keys())
        writer.writeheader()
        writer.writerows(matched)
    published = json.loads((OUT / 'published-deviations.json').read_text())
    published.append(dict(model='This work f8f64820', property='pressure', source='Mamun2005', n=19,
                          deviation_percent=aard, data_role='not fitted', fitted_parameters=16,
                          definition='100/n sum(abs(calculated-observed)/observed)',
                          conditions='393.15 K; 30 mass% MEA; source loading .155-.4182 mol/mol',
                          locator='matched-pressure-rows.csv; original Table 2 p.632',
                          comparison='exact: vle_obs_0246..0264; source pressure pairs verified'))
    files = ['canonical-pressure.csv', 'fitted-rows.csv', 'reported-parameters.json', 'summary.json']
    provenance = {name: digest((evidence / name).read_bytes()) for name in files}
    provenance.update(source_csv_sha256=digest(source_path.read_bytes()),
                      published_inventory_sha256=digest((OUT / 'published-deviations.json').read_bytes()),
                      wheel_sha256='0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b')
    (OUT / 'matched-score.json').write_text(json.dumps(dict(n=19, pressure_aard_percent=aard,
        evidence='retained fixed-parameter predictions against measurements', provenance=provenance), indent=2)+'\n')
    columns = ['model', 'source', 'fitted_parameters', 'data_role', 'n', 'deviation_percent', 'conditions', 'locator', 'comparison']
    groups = sorted({r['property'] for r in published})
    text = []
    for prop in groups:
        text += ['### '+prop.replace('-', ' ').capitalize(), '', '| '+' | '.join(columns)+' |', '| '+' | '.join(['---']*len(columns))+' |']
        for row in (r for r in published if r['property'] == prop):
            text.append('| '+' | '.join(str(row.get(c) if row.get(c) is not None else 'not reported').replace('|', '/') for c in columns)+' |')
        text.append('')
    (OUT / 'property-tables.md').write_text('\n'.join(text)+'\n')
    print(f'Mamun2005: {len(matched)} rows; pressure AARD {aard:.9f}%; not fitted', flush=True)


if __name__ == '__main__' and sys.argv[1:] == ['tables']:
    tables()
