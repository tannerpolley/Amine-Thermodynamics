"""#121 decision 20, report only (not a gate): NaHCO3 osmotic coefficient against Peiper & Pitzer 1982 Table 6.

Usage: nahco3.py LABEL=RECORD.json ...   (a parameter record written by candidate.py; it fixes the Born form)
Rows: the 60 frozen #122 rows (peiper_pitzer_1982_nahco3_osmotic.csv; values evaluated from the authors' Pitzer fit),
scored against the stoichiometric column phi^st at the row's temperature and 101.325 kPa.
Model: binary.document((Na+, HCO3-)) on RECORD: water, HCO3- and HCO3--water (k_ij and any 1/T slope) as the record
holds them. Na+ as #121 decision 16 fixes it: Figiel 2025 Table 3 (sigma 2.8232 A, u/k 230 K, d_Born 3.445 A), packing
0.88 sigma and Debye-Hueckel sigma (Held's convention), Na+-HCO3- -0.514 (Held 2014 Table 3); Na+-water -0.3 (Figiel
2025 Table 5, 298.15 K), not refitted (decision 20). phi from the Engine's infinite-dilution reference (binary.activity).
Writes nahco3-states.csv and nahco3-scores.csv.
"""
import csv
import sys
from pathlib import Path

import binary as b

s = b.s
DATA = b.probe.W / 'data/reference/MEA/observations/ionic_activity/peiper_pitzer_1982_nahco3_osmotic.csv'
NA_BORN_DIAMETER = 3.445  # Figiel 2025 Table 3
NA_WATER = (b.NA, b.W, -0.3, None, None)  # Figiel 2025 Table 5


def model(record):
    b.probe.RECORD = Path(record)
    mapping = b.document((b.NA, b.HCO3), [NA_WATER])
    mapping = s.with_parameter_values(mapping, {f'component/{b.NA}/born_diameter': NA_BORN_DIAMETER})
    return b.epcsaft.Mixture(b.epcsaft.Parameters.from_mapping(mapping))


def main(specs):
    rows = list(csv.DictReader(DATA.open()))
    assert len(rows) == 60
    states, scores = [], []
    for spec in specs:
        label, record = spec.split('=')
        m = model(record)
        errors = {}
        for r in rows:
            T, molality = float(r['temperature_K']), float(r['nominal_molality_mol_per_kg'])
            phi = b.activity(m, T, 1000 * float(r['inferred_reference_pressure_kPa']), molality)[0]
            obs = float(r['osmotic_coefficient_stoichiometric'])
            errors.setdefault(T, []).append(phi / obs - 1)
            states.append({'record': label, 'record_id': r['record_id'], 'temperature_k': T, 'molality': molality,
                           'phi_st_observed': obs, 'phi_model': phi, 'relative_error': phi / obs - 1,
                           'parameter_sha256': s.sha256(Path(record))})
        for T, e in [*sorted(errors.items()), ('all', [x for v in errors.values() for x in v])]:
            scores.append({'record': label, 'temperature_k': T, 'n': len(e),
                           'ard_percent': 100 * sum(map(abs, e)) / len(e), 'mean_relative_error': sum(e) / len(e),
                           'max_abs_relative_error': max(map(abs, e)), 'parameter_sha256': s.sha256(Path(record))})
            print(scores[-1], flush=True)
    prov = {'engine_wheel_sha256': s.ENGINE_WHEEL_SHA256, 'data_sha256': s.sha256(DATA),
            'script_sha256': s.sha256(Path(__file__)), 'binary_sha256': s.sha256(Path(b.__file__))}
    for name, out in (('nahco3-states.csv', states), ('nahco3-scores.csv', scores)):
        with (b.HERE / name).open('w', newline='') as h:
            w = csv.DictWriter(h, fieldnames=[*out[0], *prov], lineterminator='\n')
            w.writeheader()
            w.writerows({**r, **prov} for r in out)


if __name__ == '__main__':
    main(sys.argv[1:])
