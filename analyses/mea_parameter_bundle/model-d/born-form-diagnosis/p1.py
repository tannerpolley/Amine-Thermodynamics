"""Descriptive native Born chemical potentials and reaction activities; no refitting."""
import time
STARTED = time.perf_counter()
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import born_form_diagnosis as d


def without_born(mapping):
    out = d.copy.deepcopy(mapping)
    next(f for f in out['model_families'] if f['kind'] == 'electrolyte')['choice'] = 'fully-dissociated-debye-huckel'
    # Same accepted Born-off document construction as model-d/binary.py.
    for c in out['components']:
        c['coefficients'] = [q for q in c['coefficients'] if q['family'] not in ('born_diameter','solvation_factor')]
    out['model_coefficients'] = [q for q in out['model_coefficients'] if q['family'] != 'ionic_region_relative_permittivity']
    return out


def potentials(on, off, T, rho, x):
    a = on.state(T, rho=rho, x=x)
    b = off.state(T, rho=rho, x=x)
    for term in ('hard_chain', 'dispersion', 'association', 'debye_huckel'):
        assert abs(getattr(a, term)-getattr(b, term)) < 1e-10, 'Born isolation changed another contribution'
    mu = np.asarray(a.residual_chemical_potential_over_rt) - b.residual_chemical_potential_over_rt
    assert np.isfinite(mu).all(), 'nonfinite native Born chemical potential'
    return mu, float(a.bulk_relative_permittivity), float(a.born)


def transfer_records():
    ids = set((d.BUNDLE / 'composition-transfer/aronu-2011-untouched-vle-rows.txt').read_text().split())
    obs = {o['identity']: o for o in d.design.probe.pressure_observations(lambda r: r['observation_id'] in ids)}
    fractions = {r['observation_id']: float(r['MEA_weight_fraction']) for r in d.csv.DictReader(d.s.CANONICAL_VLE.open())}
    out = {'11': {}, '00': {}}
    hashes = {}
    fps = {form: 'sha256:' + d.s.sha256(path) for form, path in d.FILES.items()}
    for path in (d.BUNDLE / 'results/runs/composition-transfer/states').glob('*.json'):
        r = json.loads(path.read_text())
        for form, fp in fps.items():
            if (r.get('model_parameters_fingerprint') != fp or r.get('engine_wheel_sha256') != d.s.ENGINE_WHEEL_SHA256
                    or r['identity'] not in obs): continue
            assert r['status'] == 'evaluated'
            o = obs[r['identity']]
            rec = {'identity': r['identity'], 'T': o['request']['temperature']['value'],
                   'feed': o['request']['reaction_system']['feed_amounts_mol'], 'targets': o['targets'],
                   'liquid': next(p for p in r['phases'] if p['role'] == 'liquid'),
                   'predictions': r['predictions'], 'status': r['status'],
                   'mass_fraction': fractions[r['identity'].removeprefix('canonical:')]}
            out[form][r['identity']] = rec; hashes[str(path)] = d.s.sha256(path)
    assert all(len(r) == 70 for r in out.values()), 'retained transfer compositions unavailable'
    d.save('p1-transfer-input-hashes.json', hashes)
    return out


def main():
    models = {f: (d.epcsaft.Mixture(d.epcsaft.Parameters.from_mapping(m)),
                  d.epcsaft.Mixture(d.epcsaft.Parameters.from_mapping(without_born(m)))) for f, m in d.MAPPINGS.items()}
    # Infinite-dilution water reference: the native EOS residual chemical potentials
    # at zero solute fractions. The Born term is independent of density for this model.
    reference = {}
    xpure = [float(c == 'water') for c in d.s.COMPONENT_IDS]
    reference_rows = []
    all_records = {f: dict(r) for f, r in d.RETAINED.items()}
    for f, records in transfer_records().items(): all_records[f].update(records)
    Ts = sorted({r['T'] for r in all_records['00'].values()})
    for form, (on, off) in models.items():
        for T in Ts:
            d.enough(1.)
            pure = on.state(T, P=101325., x=xpure, phase='liquid')
            mu, eps, born = potentials(on, off, T, pure.molar_density, xpure)
            reference[(form, T)] = mu
            for c, v in zip(d.s.COMPONENT_IDS, mu):
                reference_rows.append({'form': form, 'T_K': T, 'reference_pressure_Pa': 101325.,
                                       'component': c, 'born_mu_reference_over_RT': float(v), 'bulk_permittivity': eps})
    d.table('p1-infinite-dilution-reference.csv', reference_rows)
    matrix = d.design.probe.OBSERVATIONS[0]['request']['reaction_system']['reaction_matrix']
    charges = d.design.probe.OBSERVATIONS[0]['request']['reaction_system']['charges']
    assert np.max(np.abs(np.asarray(matrix) @ np.asarray(charges))) == 0.
    rows, reactions, activities, associations = [], [], {}, []
    for identity, r00 in all_records['00'].items():
        r11 = all_records['11'][identity]
        selected = identity.startswith(('Matin', 'Bottinger', 'canonical:')) or round(r00['T']-273.15) in (40, 80)
        if not selected: continue
        d.enough(1.)
        T = r00['T']; x00 = r00['liquid']['mole_fractions']; x11 = r11['liquid']['mole_fractions']
        geometries = [('own-00', '00', r00), ('own-11', '11', r11), ('common-11-on-00', '11', r00)]
        local = {}
        for path, form, rec in geometries:
            x = rec['liquid']['mole_fractions']; rho = rec['liquid']['molar_density_mol_m3']
            mu, eps, born = potentials(*models[form], T, rho, x)
            ln_gamma = mu-reference[(form, T)]
            f_mix = sum(float(v)*d.values(d.MAPPINGS[form])[f'component/{c}/solvation_factor']
                        for c, v in zip(d.s.COMPONENT_IDS, x))
            local[path] = (mu, ln_gamma)
            for i, c in enumerate(d.s.COMPONENT_IDS):
                rows.append({'identity': identity, 'path': path, 'form': form, 'T_K': T,
                    'mass_fraction': rec.get('mass_fraction', .3), 'loading_mol_CO2_per_mol_MEA': rec['feed'][0]/rec['feed'][1],
                    'component': c, 'x': x[i], 'rho_mol_m3': rho, 'bulk_permittivity': eps, 'f_mix': f_mix,
                    'born_a_over_RT': born, 'born_mu_over_RT': float(mu[i]),
                    'born_mu_reference_over_RT': float(reference[(form,T)][i]), 'born_ln_gamma': float(ln_gamma[i])})
            for i, nu in enumerate(matrix):
                reactions.append({'identity': identity, 'path': path, 'T_K': T,
                    'mass_fraction': rec.get('mass_fraction', .3), 'loading_mol_CO2_per_mol_MEA': rec['feed'][0]/rec['feed'][1],
                    'reaction': f'R{i+1}', 'born_reaction_mu_finite_over_RT': float(np.dot(nu, mu)),
                    'born_reaction_mu_reference_over_RT': float(np.dot(nu, reference[(form,T)])),
                    'born_ln_product_gamma_nu': float(np.dot(nu, ln_gamma))})
        water = d.s.COMPONENT_IDS.index('water')
        summary = {'identity': identity, 'T_K': T,
                   'loading_mol_CO2_per_mol_MEA': r00['feed'][0]/r00['feed'][1],
                   'in_fitted_objective': bool(any(d.compare.in_objective(r00,t,80) for t in r00['targets']))}
        for c in ('water', *d.ION_IDS[:3]):
            i = d.s.COMPONENT_IDS.index(c)
            v00 = local['own-00'][1][i]; v11 = local['own-11'][1][i]; common = local['common-11-on-00'][1][i]
            for key, v in [('00',v00), ('11',v11), ('difference',v11-v00), ('common_difference',common-v00)]:
                summary[f'{c}_born_ln_activity_{key}'] = float(v)
        activities[identity] = summary
        if identity.startswith('Matin'):
            rr00 = d.compare.residuals(r00); rr11 = d.compare.residuals(r11)
            for (kind, target, w00, _), (_, target11, w11, _) in zip(rr00, rr11, strict=True):
                assert target == target11
                associations.append({**summary, 'target': target, 'species': target.split('::')[-1],
                                     'weighted_residual_00': w00, 'weighted_residual_11': w11,
                                     'weighted_residual_difference': w11-w00})
    d.table('p1-native-born-potentials.csv', rows)
    d.table('p1-reaction-activities.csv', reactions)
    d.table('p1-water-and-ion-activities.csv', list(activities.values()))
    d.table('p1-matin-associations.csv', associations)
    correlations = []
    for species in sorted({r['species'] for r in associations}):
        for population in ('all-retained', 'fitted-only'):
            sub = [r for r in associations if r['species']==species and (population=='all-retained' or r['in_fitted_objective'])]
            for path in ('difference', 'common_difference'):
                xx=[r[f'water_born_ln_activity_{path}'] for r in sub]; yy=[r['weighted_residual_difference'] for r in sub]
                correlations.append({'species':species,'population':population,'path':path,'n':len(sub),
                    'spearman_rho':float(spearmanr(xx,yy).statistic), 'interpretation':'descriptive association; no causal attribution'})
    d.table('p1-rank-correlations.csv', correlations)
    ranges = []
    for path in ('own-00','own-11','common-11-on-00'):
        for w in (.15,.3,.45):
            for T in (313.15,353.15):
                for reaction in ('R1','R2','R3','R4','R5'):
                    sub=[r for r in reactions if r['path']==path and r['mass_fraction']==w and abs(r['T_K']-T)<1e-6 and r['reaction']==reaction]
                    # At fixed temperature/feed basis these are pooled retained model paths.
                    for source in ('vle_obs','canonical:'):
                        pts=sorted([r for r in sub if r['identity'].startswith(source)],key=lambda r:r['loading_mol_CO2_per_mol_MEA'])
                        if len(pts)<2: continue
                        a,b=pts[0],pts[-1]
                        ranges.append({'path':path,'mass_fraction':w,'T_K':T,'reaction':reaction,'n':len(pts),
                            'loading_low':a['loading_mol_CO2_per_mol_MEA'],'loading_high':b['loading_mol_CO2_per_mol_MEA'],
                            'born_ln_product_gamma_nu_low':a['born_ln_product_gamma_nu'],
                            'born_ln_product_gamma_nu_high':b['born_ln_product_gamma_nu'],
                            'change_over_retained_loading_range':b['born_ln_product_gamma_nu']-a['born_ln_product_gamma_nu']})
    d.table('p1-loading-range-changes.csv', ranges)
    d.save('p1-summary.json', {'states':len(activities),'native_rows':len(rows),'correlations':correlations,
        'reference':'native infinite-dilution pure water at 101325 Pa; Born chemical potentials from on/off at identical T,rho,x',
        'interpretation':'descriptive association, not recovery of the fitted objective or causal evidence'})
    print('P1 retained',len(activities),'states;',json.dumps(correlations),flush=True)


if __name__ == '__main__':
    status='complete'
    try: main()
    except BaseException as error:
        status='failed';d.save('p1-job-failure.json',{'exception':type(error).__name__,'message':str(error)});raise
    finally:
        d.save('job-times.json',d.OLD_JOBS+[{'job':'p1','wall_s':time.perf_counter()-STARTED,'status':status,
              'script_sha256':d.s.sha256(Path(__file__))}])
