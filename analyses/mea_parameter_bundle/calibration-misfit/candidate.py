"""Write parameter records for the calibration-misfit refits. None of them is the selected record.

Usage: candidate.py --packet-v5 PARAMETERS.json  the pre-refit record (868a5018) with the association
                                           topology of Engine packet mea-co2-h2o-nine-species-estimation/5
                                           (PARAMETERS.json is that packet's parameters file, hash-checked)
                                           -> pre-refit-packet-v5-parameters.json (probe.RECORD)
       candidate.py                        refit A -> candidate-refit-a-parameters.json (not adopted)
       candidate.py refit-X.json OUT.json  the fitted values of a refit result (a multistart file: its lowest-cost
                                           usable start) on probe.RECORD; missing
                                           k_ij 1/T slope nodes are added as probe.with_values adds them
       candidate.py --check RECORD.json PROBE.jsonl  re-solves four states from the record file (cold) and compares
                                           with probe.py's override solves of the same values
"""
import json
import math
import sys
from pathlib import Path

import probe

REFIT_A = {  # refit-A log line 13 (best iterate; converged, <2 % RMS change per iteration)
    'pair/carbamate-anion/water/k_ij': -0.003712306920832581,
    'pair/protonated-monoethanolamine/water/k_ij': -0.2117629883526623,
    'pair/bicarbonate-anion/water/k_ij': 0.2999999713793792,
    'pair/carbamate-anion/protonated-monoethanolamine/k_ij': -0.29999425594574874,
    'reaction:R4:correlation:a': 1.00501141432932,
}
SOURCE = {'source_id': 'mea-calibration-misfit-refit-a-2026-09-23',
          'locator': 'analyses/mea_parameter_bundle/calibration-misfit/README.md#refit-a'}


def write(name, values, source, document_id, purpose, citation, use_basis, out, base=probe.RECORD):
    raw = json.loads(base.read_text(encoding='utf-8'))  # without runtime defaults
    mapping = probe.with_values(raw, values)
    for node in probe.shared._identified(mapping):
        if node['identity'] in values and 'provenance' in node:
            node['provenance'] = {**node['provenance'], **source}
    for record in mapping['reaction_correlations']:
        if record['reaction_id'] == 'R4' and 'reaction:R4:correlation:a' in values:  # b_k keeps its source
            record['source'] = {**record['source'], 'locator': record['source']['locator']
                                + f"; coefficient a replaced by calibration-misfit refit {name} (" + source['locator'] + ')'}
    mapping['document_id'] = document_id
    mapping['purpose'] = purpose
    mapping['sources'].append({'citation': citation, 'source_id': source['source_id'], 'use_basis': use_basis})
    out.write_text(json.dumps(mapping, sort_keys=True, separators=(',', ':')) + '\n')
    probe.epcsaft.Parameters.from_mapping(probe.shared.parameter_mapping(out))  # must parse as an Engine record
    print(out, probe.shared.sha256(out))


# Engine main 1303c119 (#164 Wolbach-Sandler MEA-water cross volume, #166 MEA 2B volume d^3 -> sigma^3).
PACKET_V5 = {'packet_id': 'mea-co2-h2o-nine-species-estimation', 'packet_version': '5',
             'packet_path': 'data/packets/mea-co2-h2o-nine-species-estimation/5',
             'packet_fingerprint': '76315ac4e4961782d089c3c4504fb49667e120b9e31d46fe2a8e99837b8e0a45',
             'parameters_sha256': '1ba95275f9e23264250e891aee3d6284d801f73205dad255101e6561b29aee5f',
             'engine_commit': '1303c119e4a21ba31e46596fe62ee3fdfe4cc253'}
PRE_REFIT_SHA256 = '868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be'


def packet_v5(packet_parameters):
    """The pre-refit record with packet v5's topology: only the MEA self-volume value and the MEA-water rule change."""
    s = probe.shared
    if s.sha256(packet_parameters) != PACKET_V5['parameters_sha256'] or s.sha256(s.PARAMETERS) != PRE_REFIT_SHA256:
        raise SystemExit('packet v5 parameters or the pre-refit record changed')
    v5, raw = json.loads(packet_parameters.read_text()), json.loads(s.PARAMETERS.read_text(encoding='utf-8'))
    before = s.parameter_values(raw)
    raw['topology'] = v5['topology']
    changed = {k for k, v in s.parameter_values(raw).items() if before.get(k) != v}
    assert changed == {'association/monoethanolamine/a/monoethanolamine/b/volume'}, changed
    have = {x['source_id'] for x in raw['sources']}
    raw['sources'] += [x for x in v5['sources'] if x['source_id'] not in have]
    raw['sources'].append({'source_id': 'epcsaft-packet-mea-co2-h2o-nine-species-estimation-5',
                           'citation': 'ePC-SAFT Engine data packet ' + json.dumps(PACKET_V5, sort_keys=True),
                           'use_basis': 'association topology: MEA 2B volume 0.036287 (sigma^3 convention) and '
                                        'Wolbach-Sandler MEA-water cross-association rule'})
    raw['purpose'] = f'pre-refit record {PRE_REFIT_SHA256[:8]} with the packet v5 association topology; not adopted'
    probe.RECORD.write_text(json.dumps(raw, sort_keys=True, separators=(',', ':')) + '\n')
    probe.epcsaft.Parameters.from_mapping(s.parameter_mapping(probe.RECORD))  # must parse as an Engine record
    print(probe.RECORD, s.sha256(probe.RECORD))


def main(argv):
    if argv[:1] == ['--packet-v5']:
        return packet_v5(Path(argv[1]))
    if not argv:
        return write('A', REFIT_A, SOURCE, 'mea-co2-h2o-nine-species-calibration-misfit-candidate-a',
                     'candidate, not adopted: diagnostic refit A of the pCO2 calibration misfit',
                     'MEA-Thermodynamics calibration-misfit refit A (2026-09-23)',
                     'candidate ion-water, cation-anion and R4 values; not adopted',
                     Path(__file__).with_name('candidate-refit-a-parameters.json'))
    result, out = json.loads(Path(argv[0]).read_text()), Path(argv[1])
    if 'provenance' in result:  # refit.py multistart: the lowest-cost usable start
        best = min((v for k, v in result.items() if k != 'provenance' and v['usable']), key=lambda v: v['final_cost'])
        result = {'name': 'C', 'parameters': result['provenance']['parameters'], 'fitted': best['fitted'],
                  'wheel_sha256': result['provenance']['wheel_sha256']}
    name = result['name']
    write(name, dict(zip(result['parameters'], result['fitted'])),
          {'source_id': f'mea-calibration-misfit-refit-{name.lower()}',
           'locator': f'analyses/mea_parameter_bundle/calibration-misfit/{Path(argv[0]).name}'},
          'mea-co2-h2o-nine-species-calibration-misfit-refit-c',
          f'candidate, not adopted: calibration-misfit refit {name}, R4 at its source value (MEA #107)',
          f'MEA-Thermodynamics calibration-misfit refit {name} on {result["wheel_sha256"][:8]}',
          'ion-water, MEAH+-water 1/T slope and cation-anion k_ij; not adopted', out)


def check(path, probe_out):
    s = probe.shared
    s.RUNS = probe.SCRATCH / 'candidate-check'
    best = {r['identity']: r for r in map(json.loads, open(probe_out))}
    model = probe.epcsaft.Mixture(s.load_parameters(path))
    reactions = s.reaction_values(s.parameter_mapping(path))  # explicit path: the defaults bind PARAMETERS
    for o in probe.OBSERVATIONS:
        if o['identity'] in ('vle_obs_0135', 'vle_obs_0193', 'vle_obs_0206', 'Matin2012_state_010'):
            r = s.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=90,
                                 model_fingerprint='sha256:' + s.sha256(path))
            b = best[o['identity']]
            x = next(p for p in r['phases'] if p['role'] == 'liquid')['mole_fractions']
            dp = (math.log(r['predictions']['co2-partial-pressure'] / b['predictions']['co2-partial-pressure'])
                  if 'co2-partial-pressure' in b['predictions'] else 0.0)
            dx = max(abs(u - v) for u, v in zip(x, b['liquid']['mole_fractions']))
            print(o['identity'], r['status'], f'|dln pCO2| {abs(dp):.1e}', f'max |dx| {dx:.1e}')


if __name__ == '__main__':
    check(Path(sys.argv[2]), Path(sys.argv[3])) if sys.argv[1:2] == ['--check'] else main(sys.argv[1:])
