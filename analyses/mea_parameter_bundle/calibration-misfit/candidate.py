"""Write parameter records for the calibration-misfit refits. None of them is the selected record.

Every record starts from the base record its refit ran on: the SHA-256 recorded in the refit result
(`parameter_record_sha256`, or `provenance.base_record_sha256` for a multistart; refit A: 868a5018), verified
on disk by base_path. A base that is no longer on disk is refused, never replaced by the current one.

Usage: candidate.py --packet-v5 PARAMETERS.json  the pre-refit record (868a5018) with the association
                                           topology of Engine packet mea-co2-h2o-nine-species-estimation/5
                                           (PARAMETERS.json is that packet's parameters file, hash-checked)
                                           -> pre-refit-packet-v5-parameters.json (probe.RECORD)
       candidate.py                        refit A -> candidate-refit-a-parameters.json (not adopted)
       candidate.py --born-0-0             probe.RECORD with the original Born term set explicitly (c_shell =
                                           c_dielectric = 0; MEA #121 decision 21) -> ../model-d/BORN_00
       candidate.py refit-X.json OUT.json [NAME]  the fitted values of a refit result (a multistart file: its
                                           lowest-cost usable start, named NAME, default C) on its recorded base;
                                           missing k_ij 1/T slope nodes are added as probe.with_values adds them
       candidate.py --check RECORD.json PROBE.jsonl  re-solves four states from the record file (cold) and compares
                                           with probe.py's override solves of the same values -> record-replay-check.csv
"""
import csv
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


def base_path(sha):
    """The base record a refit ran on, found by its recorded SHA-256 and verified; a base that is no longer on disk
    (e.g. after adoption changes the selected record) is refused, never replaced by the current one."""
    path = {PRE_REFIT_SHA256: probe.shared.PARAMETERS, PRE_REFIT_V5_SHA256: probe.RECORD, BORN_00_SHA256: BORN_00}.get(sha)
    if path is None or probe.shared.sha256(path) != sha:
        raise SystemExit(f'base record {sha[:8]} is not on disk; restore it from Git history before writing')
    return path


def write(name, values, source, document_id, purpose, citation, use_basis, out, base_sha256):
    raw = json.loads(base_path(base_sha256).read_text(encoding='utf-8'))  # without runtime defaults
    mapping = probe.with_values(raw, values)
    for node in probe.shared._identified(mapping):
        if node['identity'] in values and 'provenance' in node:
            node['provenance'] = {**node['provenance'], **source}
    r4 = {k: v for k, v in values.items() if k.startswith('reaction:R4:')}
    for record in mapping['reaction_correlations']:
        if record['reaction_id'] == 'R4' and r4:
            note = ('a and b_k set to the source correlation (Tong 2012 via Aroua 1999, chemical_reaction_source_contract.json)'
                    if r4 == probe.SOURCE_R4 else 'coefficient ' + ', '.join(k.split(':')[-1] for k in r4)
                    + f' replaced by calibration-misfit refit {name}')
            record['source'] = {**record['source'], 'locator': record['source']['locator'] + f'; {note} (' + source['locator'] + ')'}
    mapping['document_id'] = document_id
    mapping['purpose'] = purpose
    mapping['sources'].append({'citation': citation, 'source_id': source['source_id'], 'use_basis': use_basis})
    out.write_text(json.dumps(mapping, sort_keys=True, separators=(',', ':')) + '\n')
    probe.epcsaft.Parameters.from_mapping(probe.shared.parameter_mapping(out))  # must parse as an Engine record
    written = probe.shared.reaction_values(probe.shared.parameter_mapping(out))
    assert all(written[k] == v for k, v in r4.items()), 'written R4 differs from the requested values'
    print(out, probe.shared.sha256(out))


# Engine main 1303c119 (#164 Wolbach-Sandler MEA-water cross volume, #166 MEA 2B volume d^3 -> sigma^3).
PACKET_V5 = {'packet_id': 'mea-co2-h2o-nine-species-estimation', 'packet_version': '5',
             'packet_path': 'data/packets/mea-co2-h2o-nine-species-estimation/5',
             'packet_fingerprint': '76315ac4e4961782d089c3c4504fb49667e120b9e31d46fe2a8e99837b8e0a45',
             'parameters_sha256': '1ba95275f9e23264250e891aee3d6284d801f73205dad255101e6561b29aee5f',
             'engine_commit': '1303c119e4a21ba31e46596fe62ee3fdfe4cc253'}
PRE_REFIT_SHA256 = '868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be'
PRE_REFIT_V5_SHA256 = '562b5976c7f6d44b782498480fce54bad1e3142d9541438f6d7a42a876a3df87'  # probe.RECORD
BORN_00 = probe.W / 'analyses/mea_parameter_bundle/model-d/born-0-0-packet-v5-parameters.json'
BORN_00_SHA256 = 'f5831262710bf30133910d7a237f8ef9487a4c5cb1ed167c167ad56b0792d46a'


def born_0_0():
    """The packet v5 pre-refit record with c_shell = c_dielectric = 0 written explicitly; the record omits both and
    shared_evaluation.parameter_mapping fills (1, 1). Nothing else changes."""
    s = probe.shared
    if s.sha256(probe.RECORD) != PRE_REFIT_V5_SHA256:
        raise SystemExit('probe.RECORD changed')
    raw = json.loads(probe.RECORD.read_text(encoding='utf-8'))
    family = next(f for f in raw['model_families'] if f['kind'] == 'electrolyte')
    assert family['choice'] == 'born' and not {'c_shell', 'c_dielectric'} & set(family), family
    family.update(c_shell=0.0, c_dielectric=0.0)
    raw['purpose'] = (f'pre-refit packet v5 record {PRE_REFIT_V5_SHA256[:8]} with the original Born term '
                      '(c_shell = c_dielectric = 0; MEA #121 decision 21); not adopted')
    BORN_00.write_text(json.dumps(raw, sort_keys=True, separators=(',', ':')) + '\n')
    probe.epcsaft.Parameters.from_mapping(s.parameter_mapping(BORN_00))  # must parse as an Engine record
    print(BORN_00, s.sha256(BORN_00))


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
    if argv[:1] == ['--born-0-0']:
        return born_0_0()
    if not argv:
        return write('A', REFIT_A, SOURCE, 'mea-co2-h2o-nine-species-calibration-misfit-candidate-a',
                     'candidate, not adopted: diagnostic refit A of the pCO2 calibration misfit',
                     'MEA-Thermodynamics calibration-misfit refit A (2026-09-23)',
                     'candidate ion-water, cation-anion and R4 values; not adopted',
                     Path(__file__).with_name('candidate-refit-a-parameters.json'), PRE_REFIT_SHA256)  # refit A's base
    result, out = json.loads(Path(argv[0]).read_text()), Path(argv[1])
    if 'provenance' in result:  # refit.py multistart: the lowest-cost usable start
        best = min((v for k, v in result.items() if k != 'provenance' and v['usable']), key=lambda v: v['final_cost'])
        result = {'name': argv[2] if len(argv) > 2 else 'C', 'parameters': result['provenance']['parameters'], 'fitted': best['fitted'],
                  'wheel_sha256': result['provenance']['wheel_sha256'],
                  'parameter_record_sha256': result['provenance']['base_record_sha256'],
                  'reaction_overrides': result['provenance'].get('reaction_overrides', {})}
    name, r4 = result['name'], result.get('reaction_overrides', {})
    assert r4 in ({}, probe.SOURCE_R4), r4
    write(name, {**dict(zip(result['parameters'], result['fitted'])), **r4},
          {'source_id': f'mea-calibration-misfit-refit-{name.lower()}',
           'locator': str(Path(argv[0]).resolve().relative_to(probe.W))},
          f'mea-co2-h2o-nine-species-calibration-misfit-refit-{name.lower()}',
          f'candidate, not adopted: calibration-misfit refit {name}, R4 '
          + ('at its source correlation (MEA #107)' if r4 else "the incumbent's fitted value"),
          f'MEA-Thermodynamics calibration-misfit refit {name} on {result["wheel_sha256"][:8]}',
          'ion-water, MEAH+-water 1/T slope and cation-anion k_ij; not adopted', out, result['parameter_record_sha256'])


def check(path, probe_out):
    s = probe.shared
    s.RUNS = probe.SCRATCH / 'candidate-check'
    best = {r['identity']: r for r in map(json.loads, open(probe_out))}
    model = probe.epcsaft.Mixture(s.load_parameters(path))
    reactions = s.reaction_values(s.parameter_mapping(path))  # explicit path: the defaults bind PARAMETERS
    rows = []
    for o in probe.OBSERVATIONS:
        if o['identity'] in ('vle_obs_0135', 'vle_obs_0193', 'vle_obs_0206', 'Matin2012_state_010'):
            r = s.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=90,
                                 model_fingerprint='sha256:' + s.sha256(path))
            b = best[o['identity']]
            x = next(p for p in r['phases'] if p['role'] == 'liquid')['mole_fractions']
            dp = (math.log(r['predictions']['co2-partial-pressure'] / b['predictions']['co2-partial-pressure'])
                  if 'co2-partial-pressure' in b['predictions'] else 0.0)
            dx = max(abs(u - v) for u, v in zip(x, b['liquid']['mole_fractions']))
            rows.append({'record': path.name, 'record_sha256': s.sha256(path), 'probe_output': probe_out.name,
                         'identity': o['identity'], 'status': r['status'], 'abs_dln_pco2': abs(dp), 'max_abs_dx': dx,
                         'engine_wheel_sha256': s.ENGINE_WHEEL_SHA256})
            print(o['identity'], r['status'], f'|dln pCO2| {abs(dp):.1e}', f'max |dx| {dx:.1e}')
    out = Path(__file__).with_name('record-replay-check.csv')
    kept = [x for x in (list(csv.DictReader(out.open())) if out.exists() else []) if x['record'] != path.name]
    with out.open('w', newline='') as h:
        w = csv.DictWriter(h, list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(kept + rows)


if __name__ == '__main__':
    check(Path(sys.argv[2]), Path(sys.argv[3])) if sys.argv[1:2] == ['--check'] else main(sys.argv[1:])
