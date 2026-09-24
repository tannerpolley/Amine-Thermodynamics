"""Score model variants on all six pCO2 sources, the refit partition, speciation and carbonate.

Usage: compare.py VARIANT=PACKET.jsonl,CANONICAL.jsonl ...   (probe.py outputs)
Writes variant-scores.csv (one row per variant, scope, quantity) and variant-states.csv
(one row per variant, state, target: observed and predicted).
Carbonate reference: Jakobsen 2005 30 wt% NMR (CO3^2- carbon fraction, inferred from the
fast-exchange HCO3-/CO3^2- shift); model values are interpolated in loading on the packet
states at the same temperature.
"""
import csv
import json
import math
import sys
from pathlib import Path
import numpy as np

import probe
from refit import is_validation, residuals

HERE = Path(__file__).parent
DATA = probe.W / 'data/reference/MEA/observations/liquid_speciation'


def load(path):
    return {r['identity']: r for r in map(json.loads, open(path))}


def carbonate_refs():
    refs = []
    for row in csv.DictReader((DATA / 'Jakobsen_2005_ChEq.csv').open()):
        if row['MEA_weight_fraction'] == '0.3' and float(row['CO2_loading']) <= 0.5:
            c = sum(float(row[k] or 0) for k in ('CO2', 'MEACOO^-', 'HCO3^-', 'CO3^2-'))
            refs.append(('Jakobsen2005', float(row['temperature']), float(row['CO2_loading']),
                         float(row['CO3^2-']) / c))
    return refs


def model_carbonate(packet, temperature_c, loading):
    pts = sorted((r['feed'][0] / r['feed'][1], r['liquid']['mole_fractions']) for r in packet.values()
                 if r['status'] == 'evaluated' and abs(r['T'] - 273.15 - temperature_c) < 0.5)
    if not pts or not pts[0][0] <= loading <= pts[-1][0]:
        return None
    f = [x[6] / (x[0] + x[4] + x[5] + x[6]) for _, x in pts]
    return float(np.interp(loading, [a for a, _ in pts], f))


def stats(values):
    v = np.array(values, float)
    return {'n': len(v), 'mean_ln': v.mean(), 'rms_ln': math.sqrt((v ** 2).mean()),
            'aard_percent': 100 * np.mean(np.abs(np.expm1(v)))}


def main(argv):
    rows, states = [], []
    for spec in argv:
        variant, paths = spec.split('=')
        packet_path, canonical_path = paths.split(',')
        packet, canonical = load(packet_path), load(canonical_path)
        sets = next(iter(packet.values()))['sets']
        groups = {}
        for r in canonical.values():
            if r['status'] != 'evaluated':
                continue
            t = r['targets'][0]
            ln = math.log(r['predictions']['co2-partial-pressure'] / t['observed'])
            groups.setdefault(f"source={t['source_identity']}", []).append(ln)
            groups.setdefault('all six sources', []).append(ln)
        for r in packet.values():
            part = 'validation (80 degC)' if is_validation(r) else 'calibration'
            for kind, _, _, ln in residuals(r) or []:
                if np.isfinite(ln):
                    groups.setdefault(f"packet {part} {'pCO2' if kind == 'p' else 'speciation'}", []).append(ln)
        for r in [*packet.values(), *canonical.values()]:
            x = r['liquid']['mole_fractions'] if r['status'] == 'evaluated' else None
            for t in r['targets']:
                pred = ((x[5] + x[6]) if t['identity'].endswith('::HCO3-') else r['predictions'][t['prediction_identity']]) if x else ''
                states.append({'variant': variant, 'identity': r['identity'], 'target': t['identity'],
                               'source': t['source_identity'], 'temperature_c': round(r['T'] - 273.15, 2),
                               'loading': r['feed'][0] / r['feed'][1], 'observed': t['observed'], 'predicted': pred,
                               'status': r['status']})
        coverage = {'canonical evaluated': sum(r['status'] == 'evaluated' for r in canonical.values()),
                    'canonical total': len(canonical)}
        for scope, v in groups.items():
            rows.append({'variant': variant, 'scope': scope, 'quantity': 'ln(pred/obs)', **stats(v)})
        for source, t, a, obs in carbonate_refs():
            m = model_carbonate(packet, t, a)
            if m is not None:
                rows.append({'variant': variant, 'scope': f'{source} T={t:g}C loading={a:g}',
                             'quantity': 'carbonate fraction of dissolved carbon', 'n': 1,
                             'observed': obs, 'predicted': m})
        for r in rows:
            if r['variant'] == variant:
                r.update({'parameter_overrides': json.dumps(sets, sort_keys=True), **coverage,
                          'engine_wheel_sha256': probe.shared.ENGINE_WHEEL_SHA256,
                          'parameter_sha256': probe.shared.sha256(probe.shared.PARAMETERS),
                          'script_sha256': probe.shared.sha256(Path(__file__))})
    fields = ['variant', 'scope', 'quantity', 'n', 'mean_ln', 'rms_ln', 'aard_percent', 'observed', 'predicted',
              'parameter_overrides', 'canonical evaluated', 'canonical total', 'engine_wheel_sha256',
              'parameter_sha256', 'script_sha256']
    with (HERE / 'variant-scores.csv').open('w', newline='') as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    prov = {k: rows[0][k] for k in ('engine_wheel_sha256', 'parameter_sha256', 'script_sha256')}
    with (HERE / 'variant-states.csv').open('w', newline='') as h:
        w = csv.DictWriter(h, fieldnames=[*states[0], *prov])
        w.writeheader()
        w.writerows({**r, **prov} for r in states)
    for r in rows:
        if r['quantity'] == 'ln(pred/obs)':
            print(f"{r['variant']:10s} {r['scope']:40s} n={r['n']:3d} rms {r['rms_ln']:.3f} mean {r['mean_ln']:+.3f} AARD {r['aard_percent']:.0f}%")
        else:
            print(f"{r['variant']:10s} {r['scope']:40s} CO3 obs {r['observed']:.3f} model {r['predicted']:.3f}")


if __name__ == '__main__':
    main(sys.argv[1:])
