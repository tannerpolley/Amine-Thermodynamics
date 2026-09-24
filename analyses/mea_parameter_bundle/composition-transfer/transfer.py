"""Predict the frozen #108 composition-transfer rows (Aronu 2011, 15 and 45 wt% MEA) once per record.

Usage: transfer.py LABEL=PARAMETERS.json ...
Rows: aronu-2011-untouched-vle-rows.txt, checked against the #108 audit hash before any solve.
Each state is the 30 wt% packet pCO2 request at the same temperature and nearest loading, with the
CO2 feed set to the row loading and water rescaled to the row's MEA mass fraction (probe.py).
Writes transfer-states.csv (every row, failures kept) and transfer-scores.csv (per record and
mass fraction: n solved/total, AARD, bias, RMS of ln(pred/obs)).
"""
import csv
import hashlib
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'calibration-misfit'))
import probe  # noqa: E402

ROWS = HERE / 'aronu-2011-untouched-vle-rows.txt'
ROWS_SHA256 = 'eaaaa6f9f138d1ada838b166f9e5866ea110ddf2141862cc304dfd4fa433cea1'  # #108 access audit


def main(argv):
    if hashlib.sha256(ROWS.read_bytes()).hexdigest() != ROWS_SHA256:
        raise SystemExit('frozen partition changed')
    ids = set(ROWS.read_text().split())
    states = probe.pressure_observations(lambda row: row['observation_id'] in ids)
    assert len(states) == len(ids) == 70
    s = probe.shared
    s.RUNS = HERE.parent / 'results/runs/composition-transfer'
    fraction = {r['observation_id']: r['MEA_weight_fraction'] for r in csv.DictReader(s.CANONICAL_VLE.open())}
    out, scores = [], []
    for spec in argv:
        label, path = spec.split('=')
        path = Path(path)
        model = probe.epcsaft.Mixture(s.load_parameters(path))
        reactions = s.reaction_values(s.parameter_mapping(path))  # explicit path: the defaults bind PARAMETERS
        digest = s.sha256(path)
        groups = {}
        for o in states:
            r = s.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=90,
                                 model_fingerprint='sha256:' + digest)
            t = o['targets'][0]
            w = fraction[t['identity'].removesuffix('-pco2')]
            pred = r['predictions'].get('co2-partial-pressure') if r['status'] == 'evaluated' else None
            ln = math.log(pred / t['observed']) if pred else None
            groups.setdefault(w, []).append(ln)
            out.append({'record': label, 'observation_id': t['identity'].removesuffix('-pco2'), 'mea_mass_fraction': w,
                        'temperature_c': round(o['request']['temperature']['value'] - 273.15, 2),
                        'loading': o['request']['reaction_system']['feed_amounts_mol'][0],
                        'observed_pa': t['observed'], 'predicted_pa': pred, 'ln_pred_over_obs': ln,
                        'status': r['status'], **probe.check(r), 'parameter_sha256': digest})
            print(label, o['identity'], r['status'], ln, flush=True)
        for w, v in sorted(groups.items()):
            ok = [x for x in v if x is not None]
            scores.append({'record': label, 'mea_mass_fraction': w, 'n_solved': len(ok), 'n_rows': len(v),
                           'aard_percent': 100 * sum(abs(math.expm1(x)) for x in ok) / len(ok),
                           'bias_mean_ln': sum(ok) / len(ok), 'rms_ln': math.sqrt(sum(x * x for x in ok) / len(ok)),
                           'parameter_sha256': digest})
    prov = {'engine_wheel_sha256': s.ENGINE_WHEEL_SHA256, 'rows_sha256': ROWS_SHA256,
            'script_sha256': s.sha256(Path(__file__)), 'probe_sha256': s.sha256(Path(probe.__file__))}
    for name, rows in (('transfer-states.csv', out), ('transfer-scores.csv', scores)):
        with (HERE / name).open('w', newline='') as h:
            w = csv.DictWriter(h, fieldnames=[*rows[0], *prov])
            w.writeheader()
            w.writerows({**r, **prov} for r in rows)
    for r in scores:
        print(r)


if __name__ == '__main__':
    main(sys.argv[1:])
