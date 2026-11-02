"""#242 source preparation: Hamborg Table 16 correlation (D4) and Kundu hold-out overlap check."""
import csv, json
from pathlib import Path
import numpy as np

AN, SRC = Path(__file__).resolve().parent, Path(__file__).resolve().parents[1] / 'amp_pz_scoping/sources'
rows = lambda p: list(csv.DictReader(p.open()))

# Hamborg & Versteeg 2009 Eq.21, ln K = A/T + B + C ln T, weighted by 1/u(ln K)^2 over all 24 Table 16 runs.
runs = rows(SRC / 'hamborg-table-16.csv')
T, y, u = (np.array([float(r[k]) for r in runs]) for k in ('T_K', 'ln_K', 'reported_uncertainty_ln_K'))
X = np.column_stack([1 / T, np.ones_like(T), np.log(T)]) / u[:, None]
coef, *_ = np.linalg.lstsq(X, y / u, rcond=None)
residual = y - (X * u[:, None]) @ coef
covariance = np.linalg.inv(X.T @ X)  # printed uncertainties taken as standard deviations
chi2 = float(np.sum((residual / u) ** 2))
Tref = 313.15  # Engine law ln K = a + b/T + c ln(T/Tref): b = A, c = C, a = B + C ln Tref
J = np.array([[0, 1, np.log(Tref)], [1, 0, 0], [0, 0, 1]])
hamborg = dict(A=coef[0], B=coef[1], C=coef[2], covariance_printed_scale=covariance.tolist(),
               chi2=chi2, degrees_of_freedom=len(T) - 3, covariance_residual_scaled=(covariance * chi2 / (len(T) - 3)).tolist(),
               condition_number=float(np.linalg.cond(X)), residuals=[dict(run=int(r['run']), T_K=t, observed_minus_fit=e, scaled=e / s)
               for r, t, e, s in zip(runs, T, residual, u)],
               engine_law=dict(a=coef[1] + coef[2] * np.log(Tref), b=coef[0], c=coef[2], reference_temperature=Tref,
                               covariance_printed_scale=(J @ covariance @ J.T).tolist()),
               ln_K_standard_error={f'{t}': float(np.sqrt(v @ covariance @ v)) for t in (293.15, 313.15, 333.15, 353.15)
                                    for v in [np.array([1 / t, 1, np.log(t)])]})

# Kundu (hold-out) against every calibration packet: identical (T, stock, alpha, pressure) rows or shared stock/observable.
kundu = rows(SRC / 'kundu-tables-1-3.csv')
hartono = rows(AN / 'inputs/hartono-2021-table-7.csv')
shared = [(k, h) for k in kundu for h in hartono if abs(float(k['T_K']) - float(h['T_K'])) < 0.5
          and float(k['alpha_mol_CO2_per_mol_AMP']) == float(h['alpha_mol_CO2_per_mol_AMP'])
          and float(k['p_CO2_kPa']) == float(h['P_total_kPa'])]
overlap = dict(kundu_rows=len(kundu), kundu_stocks_mol_per_L=sorted({k['stock_AMP_mol_per_L'] for k in kundu}),
               hartono_2021_stock_mol_per_L='3.0', identical_rows=len(shared), observable=dict(kundu='p_CO2', hartono_2021='total pressure'))
(AN / 'results/source-preparation.json').write_text(json.dumps(dict(hamborg=hamborg, kundu_overlap=overlap), indent=2, default=float) + '\n')

# Pure-AMP starting record (D3): the adopted MEA document's neutral amine renamed, Ayad Table 5 values, effective 2B.
import hashlib, epcsaft
MEA = Path(__file__).resolve().parents[1] / 'mea_parameter_bundle/results/selected-current-best-parameters.json'
assert hashlib.sha256(MEA.read_bytes()).hexdigest() == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'
doc = json.loads(MEA.read_text().replace('monoethanolamine', 'aminomethylpropanol'))
ayad = dict(provenance=dict(source_id='ayad-2023', locator='Ayad 2023 Table 5 p.2797; molar mass Table 1 p.2789', domain_id='mea-diagnostic-293-15-to-393-15-k'))
amp = next(c for c in doc['components'] if c['component_id'] == 'aminomethylpropanol')
for item in amp['coefficients']:
    if item['family'] in (start := dict(segment_count=3.1552, segment_diameter=3.4676, dispersion_energy_over_k=237.94)):
        item.update(value=dict(item['value'], magnitude=start[item['family']]), **ayad)
amp['fixed']['molar_mass'].update(value=dict(magnitude=0.08914, unit='kilogram / mole'), **ayad)
edge = next(e for e in doc['topology']['edges'] if {e['endpoint_a']['component_id'], e['endpoint_b']['component_id']} == {'aminomethylpropanol'})
edge['energy_over_k']['value']['magnitude'], edge['volume']['value']['magnitude'], edge['source'] = 3526.15, 0.0058, dict(kind='explicit', provenance=[ayad['provenance']])
doc.update(components=[amp], pairs=[], correlations=[], reaction_correlations=[], topology=dict(doc['topology'], edges=[edge], no_cross_association=[], sites=[s for s in doc['topology']['sites'] if s['component_id'] == 'aminomethylpropanol']))
epcsaft.Parameters.from_mapping(doc)  # native admission
(AN / 'inputs/amp-pure-ayad.json').write_text(json.dumps(doc, indent=1) + '\n')

# Reactive packets in SolventSpecification row form: one mol analytical AMP; water from the stock mass fraction (design §§4-5).
water = lambda w: (1 - w) / 0.01801528 / (w / 0.08914)
order = iter(range(10_000))
def packet(name, source, values):
    out = [dict(observation_order=next(order), identity=f'{name}:{i}', source=json.dumps(r), **values(r)) for i, r in enumerate(source)]
    with (AN / f'inputs/{name}.csv').open('w') as f:
        writer = csv.DictWriter(f, list(out[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(out)
packet('hartono-2021', hartono, lambda r: dict(T=float(r['T_K']), P=1e3 * float(r['P_total_kPa']), water=water(0.268), alpha=float(r['alpha_mol_CO2_per_mol_AMP']),
       observed=1e3 * float(r['P_total_kPa']), weight=100 / 9 / 47 / max(float(r['u_P_kPa']) / float(r['P_total_kPa']), 0.05) ** 2))
for kind in ('P', 'y'):  # 26 total pressures (log, scale 0.05) and 26 vapor AMP fractions, one group of 52
    packet(f'hartono-2013-{kind}', rows(AN / 'inputs/hartono-2013-table-3.csv'), lambda r: dict(T=float(r['t_C']) + 273.15, P=1e3 * float(r['P_kPa']),
           water=(1 - float(r['x_AMP'])) / float(r['x_AMP']), alpha=0.0, observed=1e3 * float(r['P_kPa']) if kind == 'P' else float(r['y_AMP']),
           scale=max(1e-4, 0.05 * float(r['y_AMP'])), weight=1 / 52 / (0.05 ** 2 if kind == 'P' else 1)))
ciftja = [r for r in rows(SRC / 'ciftja-2014-tables-s1-s3.csv') if r['row_status'] == 'ok' and float(r['alpha_NMR_mol_CO2_per_mol_AMP']) > 0]
packet('ciftja-2014', ciftja, lambda r: dict(T=float(r['T_C']) + 273.15, P=101325.0, water=water(0.30), alpha=float(r['alpha_NMR_mol_CO2_per_mol_AMP']),
       observed=float(r['x_AMPCOO']) / (float(r['x_AMP_plus_AMPH']) + float(r['x_AMPCOO'])), scale=0.003, weight=1 / 57))
packet('kundu-2003', kundu, lambda r: dict(T=float(r['T_K']), P=1e3 * (float(r['p_CO2_kPa']) + 5), water=water(float(r['stock_AMP_mass_percent']) / 100),
       alpha=float(r['alpha_mol_CO2_per_mol_AMP']), observed=1e3 * float(r['p_CO2_kPa']), weight=1.0))
packet('tong-2012', rows(AN / 'inputs/tong-2012-table-4.csv'), lambda r: dict(T=float(r['T_K']), P=1e3 * float(r['P_total_kPa']), water=water(0.30),
       alpha=float(r['alpha_mol_CO2_per_mol_AMP']), observed=1e3 * float(r['P_total_kPa']), weight=1.0))
