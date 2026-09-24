"""Forward-difference sensitivities of pCO2 and liquid speciation to EOS, ionic and reaction coordinates.

Solves every packet state at the adopted record and once per coordinate step (warm-started from the
adopted solution), then writes:
  sensitivity-states.csv  one row per (state, target): residual ln(pred/obs) and d ln(pred)/d(parameter)
  speciation-states.csv   one row per state: predicted carbon and MEA distribution
Run single-threaded:  OMP_NUM_THREADS=1 python sensitivity.py  (about one hour; solves cached in /tmp)
"""
import csv
import json
import math
from pathlib import Path

import probe

HERE = Path(__file__).parent
SCRATCH = Path('/tmp/cm')
# (identity, forward step); k_ij steps are absolute 0.01, others 2 % or 0.05 in ln K.
COORDINATES = [
    ('pair/carbon-dioxide/water/k_ij', 0.01),
    ('component/carbon-dioxide/dispersion_energy_over_k', 0.02),
    ('pair/carbon-dioxide/monoethanolamine/k_ij', 0.01),
    ('pair/monoethanolamine/water/k_ij', 0.01),
    ('pair/carbamate-anion/protonated-monoethanolamine/k_ij', 0.01),
    ('pair/carbamate-anion/water/k_ij', 0.01),
    ('pair/protonated-monoethanolamine/water/k_ij', 0.01),
    ('pair/bicarbonate-anion/water/k_ij', 0.01),
    ('pair/bicarbonate-anion/protonated-monoethanolamine/k_ij', 0.01),
    ('pair/carbonate-anion/protonated-monoethanolamine/k_ij', 0.01),
    ('component/carbamate-anion/debye_huckel_diameter', 0.02),
    ('component/protonated-monoethanolamine/debye_huckel_diameter', 0.02),
    ('component/carbonate-anion/debye_huckel_diameter', 0.02),
    ('component/bicarbonate-anion/debye_huckel_diameter', 0.02),
    ('component/carbamate-anion/born_diameter', 0.02),
    ('component/protonated-monoethanolamine/born_diameter', 0.02),
    ('component/carbonate-anion/born_diameter', 0.02),
    ('component/carbamate-anion/dispersion_energy_over_k', 0.02),
    ('component/protonated-monoethanolamine/dispersion_energy_over_k', 0.02),
    ('model/relative_permittivity/ionic_region_relative_permittivity', 0.02),
    ('component/monoethanolamine/relative_permittivity', 0.02),
    ('reaction:R4:correlation:a', 0.05),
    ('reaction:R2:correlation:a', 0.05),
    ('reaction:R5:correlation:b', -0.05 / math.log(10.0)),  # +0.05 in ln K (R5 stores -log10 K)
]


def perturbed_value(ident, step, base):
    if 'k_ij' in ident or ident.startswith('reaction:'):
        return base + step
    return base * (1 + step)


def solved(path, sets):
    if not path.exists():
        with path.open('w') as h:
            for rec in probe.evaluate(sets):
                h.write(json.dumps(rec) + '\n')
    return {r['identity']: r for r in map(json.loads, path.open()) if r['status'] == 'evaluated'}


def predicted(rec):
    """Prediction per target identity; NMR "HCO3-" is the model HCO3- + CO3^2- carbon pool."""
    x = rec['liquid']['mole_fractions']
    out = {}
    for t in rec['targets']:
        if t['identity'].endswith('::HCO3-'):
            out[t['identity']] = x[5] + x[6]
        else:
            out[t['identity']] = rec['predictions'][t['prediction_identity']]
    return out


def main():
    SCRATCH.mkdir(exist_ok=True)
    values = probe.shared.parameter_values(probe.shared.parameter_mapping())
    base = solved(SCRATCH / 'base.jsonl', {})
    columns = []
    for n, (ident, step) in enumerate(COORDINATES, 1):
        v = perturbed_value(ident, step, values[ident])
        columns.append((ident, v - values[ident], solved(SCRATCH / f'sens_{n}.jsonl', {ident: v})))
    prov = {'engine_wheel_sha256': probe.shared.ENGINE_WHEEL_SHA256,
            'parameter_sha256': probe.shared.sha256(probe.shared.PARAMETERS),
            'packet_sha256': probe.shared.sha256(probe.shared.STATE_PACKET),
            'script_sha256': probe.shared.sha256(Path(__file__))}
    rows = []
    for ident, rec in base.items():
        p0 = predicted(rec)
        for t in rec['targets']:
            tid = t['identity']
            row = {'identity': ident, 'target': tid, 'source': t['source_identity'],
                   'temperature_c': round(rec['T'] - 273.15, 2), 'loading': rec['feed'][0] / rec['feed'][1],
                   'observed': t['observed'], 'predicted': p0[tid],
                   'ln_pred_over_obs': math.log(p0[tid] / t['observed']) if t['observed'] > 0 else ''}
            for cid, h, recs in columns:
                q = predicted(recs[ident]).get(tid) if ident in recs else None
                row[f'dln_d[{cid}]'] = math.log(q / p0[tid]) / h if q and p0[tid] > 0 else ''
            rows.append({**row, **prov})
    with (HERE / 'sensitivity-states.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    spec = []
    for ident, rec in base.items():
        x = rec['liquid']['mole_fractions']
        c, m = x[0] + x[4] + x[5] + x[6], x[1] + x[3] + x[4]
        spec.append({'identity': ident, 'temperature_c': round(rec['T'] - 273.15, 2),
                     'loading': rec['feed'][0] / rec['feed'][1],
                     'co2_fraction_of_carbon': x[0] / c, 'carbamate_fraction_of_carbon': x[4] / c,
                     'bicarbonate_fraction_of_carbon': x[5] / c, 'carbonate_fraction_of_carbon': x[6] / c,
                     'free_mea_fraction_of_amine': x[1] / m, **prov})
    with (HERE / 'speciation-states.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(spec[0]))
        w.writeheader()
        w.writerows(spec)


if __name__ == '__main__':
    main()
