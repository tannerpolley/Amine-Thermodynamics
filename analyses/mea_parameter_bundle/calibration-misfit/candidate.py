"""Write the refit-A candidate record: the selected record with the five refit coordinates replaced.

A CANDIDATE only. It does not replace results/selected-current-best-parameters.json.
``--check`` re-solves four states from this file and compares with /tmp/cm/best.jsonl (probe overrides).
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


def main():
    raw = json.loads(probe.shared.PARAMETERS.read_text(encoding='utf-8'))  # without runtime defaults
    mapping = probe.shared.with_parameter_values(raw, REFIT_A)
    for node in probe.shared._identified(mapping):
        if node['identity'] in REFIT_A and 'provenance' in node:
            node['provenance'] = {**node['provenance'], **SOURCE}
    for record in mapping['reaction_correlations']:
        if record['reaction_id'] == 'R4':  # b_k keeps its source; only a comes from refit A
            record['source'] = {**record['source'], 'locator': record['source']['locator']
                                + '; coefficient a replaced by calibration-misfit refit A ('
                                + SOURCE['locator'] + ')'}
    mapping['document_id'] = 'mea-co2-h2o-nine-species-calibration-misfit-candidate-a'
    mapping['purpose'] = 'candidate, not adopted: diagnostic refit A of the pCO2 calibration misfit'
    mapping['sources'].append({'citation': 'MEA-Thermodynamics calibration-misfit refit A (2026-09-23)',
                               'source_id': SOURCE['source_id'],
                               'use_basis': 'candidate ion-water, cation-anion and R4 values; not adopted'})
    out = Path(__file__).with_name('candidate-refit-a-parameters.json')
    out.write_text(json.dumps(mapping, sort_keys=True, separators=(',', ':')) + '\n')
    probe.epcsaft.Parameters.from_mapping(probe.shared.parameter_mapping(out))  # must parse as an Engine record
    print(out, probe.shared.sha256(out))


def check():
    s = probe.shared
    path = Path(__file__).with_name('candidate-refit-a-parameters.json')
    s.RUNS = Path('/tmp/mea-candidate-check')
    best = {r['identity']: r for r in map(json.loads, open('/tmp/cm/best.jsonl'))}
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
    check() if '--check' in sys.argv else main()
