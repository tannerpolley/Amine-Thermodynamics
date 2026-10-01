"""Issue #151: fixed-volume term attribution; render reads retained CSVs only."""
import csv
import json
import os
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
TERMS = ['hc', 'disp', 'assoc', 'DH', 'Born', 'V', 'total']
FIELDS = ['hard_chain', 'dispersion', 'association', 'debye_huckel', 'born']


def render():
    import pandas as pd
    import matplotlib.pyplot as plt
    a = pd.read_csv(HERE / 'state-activity-contributions.csv')
    p = pd.read_csv(HERE / 'born-off-pressure-decomposition.csv')
    rows = []
    for T, group in p[(p.parent == 'adopted') & (p.comparison == 'off-refit')].groupby('T_K'):
        for third, part in enumerate(np.array_split(group.sort_values(['loading', 'state']), 3), 1):
            row = dict(T_K=T, third=third, loading_low=part.loading.min(), loading_high=part.loading.max())
            for record in ('adopted', 'original'):
                q = a[(a.record == record) & a.state.isin(part.state) & (a.quantity == 'Q')]
                for term in ('Born', 'Born-transfer', 'Born-ion', 'Born-permittivity', 'Born-shell'):
                    row[record + '_' + term] = q[q.term == term].value.mean()
                fraction = p[(p.parent == record) & (p.comparison == 'off-refit') & p.state.isin(part.state)].phi
                row[record + '_phi'] = fraction.mean() if fraction.notna().all() else np.nan
            rows.append(row)
    pd.DataFrame(rows).to_csv(HERE / 'born-activity-contributions-table.csv', index=False)
    plotted = p[(p.parent == 'adopted') & (p.comparison == 'off-refit')].copy()
    plotted['other_activity'] = plotted[['dQ_hc', 'dQ_assoc', 'dQ_DH', 'dQ_V']].sum(axis=1)
    no_refit = p[(p.parent == 'adopted') & (p.comparison == 'adopted-no-refit')].set_index('state')
    plotted['no_refit_dlnp'] = plotted.state.map(no_refit.dlnp)
    plotted.to_csv(HERE / 'born-off-pressure-decomposition-plotted-values.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True, layout='constrained')
    series = [('dlnp', 'Refit total'), ('dQ_Born', 'Born removal'), ('dQ_disp', 'Dispersion'),
              ('other_activity', 'Other activity'), ('dS', 'Speciation'), ('dH', 'Vapor/reference H'),
              ('no_refit_dlnp', 'Without refit')]
    for ax, (T, group) in zip(axes, plotted.groupby('T_K'), strict=True):
        ax.axhspan(-.3, .3, color='grey', alpha=.15)
        for (column, label), marker in zip(series, 'oxs^vD+', strict=True):
            ax.scatter(group.loading, group[column], s=19, marker=marker, label=label)
        ax.set(xlabel='Loading (mol CO₂ / mol MEA)', title=f'{T:.2f} K')
    axes[0].set_ylabel('Change in ln CO₂ partial pressure (dimensionless)')
    axes[1].legend(fontsize=8, loc='best')
    fig.suptitle('Born-off pressure shifts combine activity and speciation changes')
    for suffix in ('svg', 'pdf'):
        fig.savefig(HERE / ('born-off-pressure-decomposition.' + suffix))


def check(name, values, tolerance, context):
    error = float(np.max(np.abs(values)))
    previous = checks.get(name, {'max_abs_error': -1, 'evaluations': 0})
    checks[name] = {**previous, 'evaluations': previous['evaluations'] + 1, 'tolerance': tolerance}
    if not np.isfinite(error) or error > previous['max_abs_error']:
        checks[name].update(max_abs_error=error, context=context)
    checks[name]['passed'] = bool(np.isfinite(error) and error <= tolerance)
    if not checks[name]['passed']:
        checks['failure'] = dict(check=name, context=context, values=np.asarray(values).tolist())
        d.s.write_json(HERE / 'checks.json', checks)
    assert checks[name]['passed'], (name, context, error, tolerance)


def mixture(mapping):
    return d.epcsaft.Mixture(d.epcsaft.Parameters.from_mapping(mapping))


def scalar(state):
    return np.array([getattr(state, field) for field in FIELDS])


def difference(model, T, state, x, context, h=1e-5, reference=False, off=None):
    rho = state.molar_density
    base = scalar(state)
    check('N2', base.sum() - state.residual_helmholtz, 1e-12, context)
    mu = np.empty((5, 9))
    for i in range(9):
        samples = []
        for delta in (h, 2*h):
            amounts = x.copy()
            amounts[i] += delta
            shifted = model.state(T, rho=rho*(1+delta), x=amounts/(1+delta))
            check('N2', scalar(shifted).sum() - shifted.residual_helmholtz, 1e-12, context)
            samples.append((1+delta)*scalar(shifted))
        mu[:, i] = (-3*base + 4*samples[0] - samples[1])/(2*h)
    smooth = mu[[0, 1, 2, 4]].sum(axis=0) if reference else mu.sum(axis=0)
    check('N3', smooth - state.residual_chemical_potential_over_rt, 1e-5, context)
    check('N4', mu[4] - born(model, off or mixture(p1.without_born(current_mapping)), T, state, x), 1e-5, context)
    return mu


def born(on, off, T, state, x):
    return p1.potentials(on, off, T, state.molar_density, x)[0]


def expected_k(mapping, request, T):
    records = d.s._engine_reaction_records(request, d.s.reaction_values(mapping))
    scale = np.array(source_contract['common_source_standard_state']['log_activity_scale_factors_by_species'])
    values = []
    for rec, nu in zip(records, matrix, strict=True):
        c = rec['engine_correlation']
        value = c['a'] + c['b']/T + c['c']*np.log(T/c['reference_temperature']) + c['d']*T
        values.append(value + nu@scale if rec['engine_reference']['source_basis'] == 'CommonMolalityInfiniteDilution' else value)
    return np.array(values)


def activities(model, T, state, x):
    refs = [model.state(T, P=P or state.pressure, x=pure, phase='liquid') for P in pressures]
    gamma = np.array([np.asarray(state.log_fugacity_coefficient) - ref.log_fugacity_coefficient for ref in refs])
    G = np.einsum('ri,ri->r', matrix, gamma)
    return gamma, G, G[1]-G[3]-G[4]+gamma[1, 0], refs


def calculate(arguments):
    global current_mapping
    assert len(arguments) % 2 == 0, 'calculate takes NAME RECORD pairs; states are runs/NAME-states.jsonl'
    inputs = json.loads((HERE / 'inputs.json').read_text())
    mappings = {name: d.s.parameter_mapping(Path(path)) for name, path in zip(arguments[::2], arguments[1::2], strict=True)}
    inputs['sha256'][str(Path(__file__))] = d.s.sha256(Path(__file__))
    d.s.verify_wheel()
    rows, summaries, closures = [], {}, {}
    for name, mapping in mappings.items():
        current_mapping = mapping
        model, off = mixture(mapping), mixture(p1.without_born(mapping))
        records = list(map(json.loads, (HERE / 'runs' / (name+'-states.jsonl')).open()))
        pressure_records = [r for r in records if 'co2-partial-pressure' in r['predictions']]
        sentinels = []
        for T in (313.15, 333.15):
            group = sorted([r for r in pressure_records if r['T']==T], key=lambda r: (r['feed'][0]/r['feed'][1], r['identity']))
            sentinels.extend([group[0]['identity'], group[-1]['identity']])
            if T == 313.15:
                sentinels.append(group[(len(group)-1)//2]['identity'])
        reference_cache, frozen = {}, {}
        for rec in records:
            T, identity, liq = rec['T'], rec['identity'], rec['liquid']
            x = np.array(liq['mole_fractions'])
            state = model.state(T, rho=liq['molar_density_mol_m3'], x=x)
            context = dict(record=name, state=identity)
            mu = difference(model, T, state, x, context)
            if identity in sentinels:
                half = difference(model, T, state, x, context, h=5e-6)
                checks.setdefault('N9_estimates', []).append(dict(**context, terms=FIELDS, species=d.s.COMPONENT_IDS, h=mu.tolist(), half=half.tolist(), difference=(half-mu).tolist()))
                check('N9', half-mu, 1e-5, context)
            gamma, analytic_G, Q, refs = activities(model, T, state, x)
            K = expected_k(mapping, observations[identity]['request'], T)
            closure = np.einsum('ri,ri->r', matrix, gamma+np.log(x))
            check('N5a', closure-K, 1e-6, context)
            closures.setdefault(T, []).append(closure)
            gammas = []
            for r, ref in enumerate(refs):
                key = (T, ref.pressure)
                if key not in reference_cache:
                    reference_cache[key] = difference(model, T, ref, pure, {**context, 'reference_pressure':ref.pressure}, reference=True)
                parts = mu-reference_cache[key]
                parts[3] = mu[3]
                gammas.append(np.vstack([parts, np.full(9, np.log(state.molar_density/ref.molar_density)), gamma[r]]))
            gammas = np.array(gammas)
            B = born(model, off, T, state, x) - born(model, off, T, refs[1], pure)
            neutral = x.copy()
            neutral[3:] = 0
            neutral /= neutral.sum()
            transfer_state = model.state(T, rho=state.molar_density, x=neutral)
            transfer = born(model, off, T, transfer_state, neutral)-born(model, off, T, refs[1], pure)
            split = {'Born-transfer':transfer, 'Born-ion':B-transfer}
            if any(f['choice']=='born' for f in mapping['model_families']):
                eps = refs[1].bulk_relative_permittivity
                changes_E = {'component/monoethanolamine/relative_permittivity':eps}
                changes_F = {f'component/{c}/solvation_factor':1.5 for c in d.s.COMPONENT_IDS}
                frozen.setdefault(T, [mixture(d.s.with_parameter_values(mapping, changes)) for changes in (changes_E, changes_F, {**changes_E, **changes_F})])
                Bs = [born(m, mixture(p1.without_born(d.s.with_parameter_values(mapping, changes))), T, state, x)-born(m, mixture(p1.without_born(d.s.with_parameter_values(mapping, changes))), T, refs[1], pure) for m, changes in zip(frozen[T], (changes_E, changes_F, {**changes_E, **changes_F}), strict=True)]
                check('N7', Bs[2], 1e-10, context)
                split.update({'Born-permittivity':(B-Bs[0]+Bs[1]-Bs[2])/2, 'Born-shell':(B-Bs[1]+Bs[0]-Bs[2])/2, 'Born-single-permittivity':B-Bs[0], 'Born-single-shell':B-Bs[1]})
            else:
                split.update({term:np.zeros(9) for term in ('Born-permittivity','Born-shell','Born-single-permittivity','Born-single-shell')})
            Eoff = mixture(d.s.with_parameter_values(p1.without_born(mapping), {'component/monoethanolamine/relative_permittivity':refs[1].bulk_relative_permittivity}))
            split['DH-permittivity'] = difference(off, T, off.state(T,rho=state.molar_density,x=x), x, context, off=off)[3]-difference(Eoff,T,Eoff.state(T,rho=state.molar_density,x=x),x,context,off=Eoff)[3]
            G = np.einsum('ri,rki->rk', matrix, gammas)
            q = G[1]-G[3]-G[4]+gammas[1,:,0]
            loading = rec['feed'][0]/rec['feed'][1]
            info = dict(record=name, sha256=d.s.sha256(Path(arguments[arguments.index(name)+1])), state=identity, source=rec['targets'][0]['source_identity'], T_K=T, loading=loading)
            for r in range(5):
                for i, species in enumerate(d.s.COMPONENT_IDS):
                    rows.extend({**info,'quantity':'species ln gamma*','species':species,'reaction':f'R{r+1}','reference_pressure_Pa':refs[r].pressure,'term':term,'value':value} for term,value in zip(TERMS,gammas[r,:,i],strict=True))
            for term, vector in split.items():
                gammas = np.concatenate([gammas, np.tile(vector,(5,1))[:,None,:]],axis=1)
            all_terms = TERMS+list(split)
            G = np.einsum('ri,rki->rk', matrix, gammas)
            quantities = {**{f'R{r+1}':G[r] for r in range(5)}, 'OV':G[1]-G[3]-G[4], 'Q':G[1]-G[3]-G[4]+gammas[1,:,0]}
            rows.extend({**info,'quantity':quantity if quantity=='Q' else 'reaction sum','species':'','reaction':quantity,'reference_pressure_Pa':refs[int(quantity[1:])-1].pressure if quantity.startswith('R') else None,'term':term,'value':value} for quantity,values in quantities.items() for term,value in zip(all_terms,values,strict=True))
            if rec in pressure_records:
                S = np.log(x[3]*x[4]/x[1]**2)
                vapor_x = [rec['predictions']['vapor-y-'+c] for c in ('co2','mea','water')]+[0.]*6
                vapor = model.state(T,P=liq['pressure_pa'],x=vapor_x,phase='vapor')
                H = refs[1].log_fugacity_coefficient[0]+np.log(liq['pressure_pa'])-vapor.log_fugacity_coefficient[0]
                ln_p = np.log(rec['predictions']['co2-partial-pressure'])
                check('N8', ln_p-(S+Q-(K[1]-K[3]-K[4])+H),1e-6,context)
                summaries[(name,identity)] = {**info,'S':S,'H':H,'lnp':ln_p,'Q':Q,**dict(zip(all_terms,quantities['Q'],strict=True))}
        if name in ('adopted','original'):
            masses = [c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']]
            saltfree = np.array([0,.3/masses[1],.7/masses[2]]+[0.]*6)
            saltfree /= saltfree.sum()
            pure_ref = model.state(313.15,P=101325.,x=pure,phase='liquid')
            salt_state = model.state(313.15,P=101325.,x=saltfree,phase='liquid')
            values = (born(model,off,313.15,salt_state,saltfree)-born(model,off,313.15,pure_ref,pure))[[3,4,7]]
            expected = [-.145297,-.144975,-.421485] if name=='adopted' else [.419167,.418239,1.215939]
            checks.setdefault('N6_values',{})[name] = values.tolist()
            check('N6',values-expected,1e-6,dict(record=name))
    for T, values in closures.items():
        check('N5',np.ptp(values,axis=0),1e-6,dict(T_K=T))
    d.s.write_json(HERE/'checks.json',checks)
    d.s.write_json(HERE/'inputs.json',inputs)
    raise RuntimeError('C1/C2, falsifiers and table export not implemented; no table authorized yet')


if __name__ == '__main__':
    if sys.argv[1] == 'render':
        render()
    else:
        os.environ['SENSITIVITY_OUTPUT'] = str(HERE/'runs')
        sys.path.insert(0,str(HERE.parent/'born-form-diagnosis'))
        import p1
        d = p1.d
        checks = json.loads((HERE/'checks.json').read_text())
        observations = {o['identity']:o for o in d.OBS}
        matrix = np.array(d.OBS[0]['request']['reaction_system']['reaction_matrix'])
        pure = np.array([float(c=='water') for c in d.s.COMPONENT_IDS])
        pressures = list(d.s.REACTION_REFERENCE_PRESSURES.values())
        source_contract = json.loads((d.ROOT/'data/reference/MEA/manifests/chemical_reaction_source_contract.json').read_text())
        calculate(sys.argv[2:])
