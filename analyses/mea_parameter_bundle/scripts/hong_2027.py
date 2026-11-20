"""Evaluate Hong's published 30 wt% MEA model on the frozen #246 observations."""
import json
import math
import re
import subprocess
import sys
from collections import Counter
from copy import deepcopy
from functools import cache
from pathlib import Path
from time import perf_counter

from kim2007_heat_pathways import BUNDLE, digest, metrics, np, read, write_json
from candidate_evidence_255 import SPEC, table
from fit_observations import heat_solvent, indexed
from epcsaft import Mixture, Parameters, equilibrium as eq
from scipy.constants import R
from scipy.optimize import root
import shared_evaluation as shared
from same_data_comparison import hong_scores

RESULTS = BUNDLE / 'results'
ADOPTED, PUBLISHED = (RESULTS/p for p in ('paper-evidence-341/paper-evidence','same-data-comparison/part1/published'))
OUT = PUBLISHED.parents[1] / 'hong-2027'


def comparison_rows(path):
    rows = indexed(read(path), 'record_id')
    for directory, model, assessment in [(ADOPTED,'adopted',''), (PUBLISHED,'polley_hedengren_2026','selected-assessment/')]:
        for filename,key,obs,pred in (
            (assessment+'state-targets.csv','target','observed','predicted'),
            (assessment+'density.csv','id','observed_kg_m3','predicted_kg_m3'),
            ('kim2007-heat-pathways/kim-heat.csv','record_id','observed','predicted'),
        ):
            reference = indexed([r for r in read(directory/filename)
                                 if key!='target' or r['kind'] in ('canonical','wagner')],key)
            for identity,r in reference.items():
                row = rows[identity]
                assert float(r[obs]) == float(row['observed']) and model not in row, identity
                row[model] = float(r[pred]) if r[pred] else None
    for row in rows.values():
        for k in ('T_K','loading','previous_loading','mea_mass_fraction','observed'):
            row[k] = float(row[k])
        for k in ('inside_hong_grid','three_model_eligible','hilliard_edge','hong_eligible'):
            row[k] = row[k]=='True'
    return list(rows.values())


def replay_comparison(rows):
    pressures = [r for r in rows if r['block']=='canonical']
    values = {}
    for model, expected in [('adopted',20.971795), ('polley_hedengren_2026',52.341322)]:
        score = metrics(pressures,predicted=model)
        assert len(pressures)==score['n']==159 and round(score['aard_percent'],6)==expected, score
        values[model] = score['aard_percent']
    return values


INPUT = json.loads((OUT / 'parameters.json').read_text())
MASS = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in INPUT['parameters']['components']}
ID = tuple(MASS)
TEMPERATURES = np.arange(9) * 10 + 313.15
LOADINGS = np.arange(1, 11) / 10
WEIGHTS = np.array(INPUT['weights'])
STABLE = 'stable'
UNSTABLE = 'locally unstable'
STABLE_PINNED = []
FIGURE_WATER = .70 / MASS['water'] / (.30 / MASS['mea'])


def weight(a, T):
    assert .1 <= a <= 1 and 313.15 <= T <= 393.15, (a, T)
    return float(np.interp(T, TEMPERATURES, [np.interp(a, LOADINGS, row) for row in WEIGHTS]))


def coefficient(name, magnitude, unit='dimensionless'):
    return dict(identity=name, value=dict(magnitude=magnitude, unit=unit))


def model(w, pathway=None):
    doc = deepcopy(INPUT['parameters'])
    topology = doc['topology']
    neutral = INPUT['neutral_association']
    (km,kw),(em,ew) = ([e[k]['value']['magnitude'] for e in neutral['edges'][:2]]
                       for k in ('volume','energy_over_k'))
    cross_volume = ((km**(1/3)+kw**(1/3))/2)**3
    cross_energy = INPUT['mea_water_alpha_HB']*math.sqrt(em*ew)
    if pathway:
        position = ('sym','single').index(pathway)
        topology['sites'] = [topology['sites'][position]]
        topology['sites'][0].pop('pathway')
        topology['edges'] = [topology['edges'][position]]
        kij = doc['pairs'][-1]['coefficients'][position]
        doc['pairs'][-1]['coefficients'] = [dict(kij,family='k_ij')]
        doc.pop('pathway_weight')
    else:
        intercept = -800 if w==0 else 800 if w==1 else math.log(w/(1-w))
        doc['pathway_weight']['coefficients'][0]['value']['magnitude'] = intercept
    reactive_sites, topology['sites'] = topology['sites'], []
    for site in reactive_sites:
        suffix = site['site_id'][1:]
        for q in neutral['sites']:
            topology['sites'].append(dict(q,site_id=q['site_id']+suffix,
                                          **({'pathway':site['pathway']} if not pathway else {})))
        topology['sites'].append(site)
        for i, q in enumerate(deepcopy(neutral['edges'])):
            for end in ('endpoint_a','endpoint_b'):
                q[end]['site_id'] += suffix
            if i>=2:
                q.update(energy_over_k=coefficient(f'cross-{i}',cross_energy,'kelvin'),
                         volume=coefficient(f'cross-{i}/volume',cross_volume))
            for k in ('energy_over_k','volume'):
                q[k]['identity'] += suffix
            topology['edges'].append(q)
    return Mixture(Parameters.from_mapping(doc))


def observed_water(rows):
    template = shared.load_state_packet()['observations'][0]['request']
    canonical = indexed(read(shared.CANONICAL_VLE), 'observation_id')
    wagner = indexed([r for r in read(RESULTS / 'temperature-reanchor-140/never-accessed-vle-admission.csv')
                      if r['admitted'] == 'yes'], 'csv_data_row_number')
    kim_solvent = heat_solvent(shared.parameter_mapping(ADOPTED/'reported-parameters.json'))
    declared = indexed(json.loads(SPEC.read_text())['direct_rows'], 'id')
    for row in rows:
        is_kim = row['block'].startswith('Kim ')
        if is_kim or (row['pressure_Pa'] and row['adopted_role']=='fitted'):
            feed = kim_solvent if is_kim else declared[row['record_id']]['analytical_feed']
            loading = row['loading'] if is_kim else feed['carbon-dioxide']/feed['monoethanolamine']
            row.update(analytical_loading=loading, water_per_mea=feed['water']/feed['monoethanolamine'])
            continue
        row_id = row['record_id'].removesuffix('-pco2')
        source = dict(source_key=row['source'], MEA_weight_fraction=row['mea_mass_fraction'],
                      CO2_loading=row['loading'], temperature_reported_C=row['T_K']-273.15)
        if row['block'] == 'canonical':
            source = canonical[row_id]
        if row['block'] == 'wagner':
            original = wagner[row_id.rsplit('-',1)[1]]
            source.update(MEA_weight_fraction=original['MEA_mass_fraction_unloaded'],
                          CO2_loading=original['loading_mol_CO2_per_mol_MEA'])
        system = shared.source_feed_request(template, source)['reaction_system']
        c, m, w, *_ = system['analytical_feed_contract']['neutral_analytical_amounts_mol']
        if row['block'] in ('canonical', 'wagner'):
            seeded_co2, seeded_mea, *_ = system['feed_amounts_mol']
            assert math.isclose(seeded_co2/seeded_mea, row['loading'], rel_tol=1e-12), row
        row.update(analytical_loading=c/m, water_per_mea=w/m)


def composition(a, water):
    n = np.array([1., water, a])
    return n/n.sum()


def phase_solve(mix, a, T, water, pinned=0.):
    x = composition(a, water)
    problem = eq.bubble_point(liquid=eq.Phase('L', kind='liquid', composition_guess=dict(zip(ID,x))),
                              T=T, feed=eq.Amounts(dict(zip(ID,(1.,water,a)))))
    if pinned:
        # Seed the same fixed-amount solve with the liquid's 1 bar fugacities.
        state = mix.state(T, P=1e5, x=x, phase='liquid')
        fugacity = x*np.exp(state.log_fugacity_coefficient)*1e5
        guess = float(fugacity.sum())
        problem.P = eq.Free(guess)
        problem.phases[1].composition_guess = dict(zip(ID,fugacity/guess))
        problem.phases[1].amount = eq.Pinned(pinned)
    return eq.solve_equilibrium(mix, problem)


@cache
def pressure(a, T, water, w):
    mix = model(w)
    result = phase_solve(mix, a, T, water)
    eigenvalue, stability = None, STABLE
    if not result.success:
        match = re.search(r'lowest eigenvalue (-?[\d.eE+-]+)', result.message)
        if match is None or 'local phase instability:' not in result.message or float(match[1]) >= 0:
            raise RuntimeError((a,T,water,w,result.message))
        eigenvalue, stability = float(match[1]), UNSTABLE
        result = phase_solve(mix, a, T, water, 1e-9)
        if not result.success:
            raise RuntimeError((a,T,water,w,eigenvalue,result.message))
    x, y = np.asarray(result.mole_fractions).reshape(2,3)
    predicted = float(result.pressure*y[2])
    if stability==STABLE:
        pinned = phase_solve(mix,a,T,water,1e-9)
        difference = relative(pinned.pressure*pinned.mole_fractions[5],predicted) if pinned.success else None
        STABLE_PINNED.append(dict(T_K=T,loading=a,water_per_mea=water,relative_difference=difference,
                                  failure='' if pinned.success else pinned.message))
    return dict(predicted=predicted, stability=stability, minimum_eigenvalue=eigenvalue, w=w,
                pressure_Pa=result.pressure, liquid_density_mol_m3=result.molar_densities[0],
                max_solver_residual=max(map(abs,result.classified_residuals)), liquid=x.tolist(), vapor=y.tolist())


def relative(value, reference):
    return abs(value/reference - 1)


def equal_fugacity(mix, a, T, water, solved):
    x = composition(a,water)
    def equations(z):
        P, y = np.exp(z[0]), np.exp(z[1:])
        y /= sum(y)
        L, V = (mix.state(T, P=P, x=q, phase=phase).log_fugacity_coefficient
                for q,phase in [(x,'liquid'), (y,'vapor')])
        return np.r_[np.log(x/y)+np.asarray(L)-V, sum(np.exp(z[1:]))-1]
    status = root(equations, np.log([solved['pressure_Pa'], *solved['vapor']]), tol=1e-11)
    residual = float(np.max(np.abs(equations(status.x))))
    assert residual <= 1e-10, (a,T,status.message,residual)
    return float(np.exp(status.x[0]+status.x[3])), residual


def eigenvalue_fd(mix, T, x, rho, step):
    def potential(n):
        state = mix.state(T, rho=rho*sum(n), x=n/sum(n))
        return np.log(rho*n) + state.residual_chemical_potential_over_rt
    hessian = np.column_stack([(potential(x+d)-potential(x-d))/(2*d[i])
                               for i,d in enumerate(np.diag(step*x))])
    scaled = np.sqrt(x[:,None]*x) * (hessian+hessian.T)/2
    return float(np.linalg.eigvalsh(scaled)[0])


def pressure_checks(run):
    assert all(weight(a,T)==WEIGHTS[i,j] for i,T in enumerate(TEMPERATURES) for j,a in enumerate(LOADINGS))
    limits = {}
    for w,pathway in [(0,'single'),(1,'sym')]:
        state, pure = [m.state(333.15, rho=42424.79, x=composition(.4,FIGURE_WATER))
                       for m in (model(w), model(w,pathway))]
        limits[w] = relative(state.residual_helmholtz,pure.residual_helmholtz)
        assert state.pathway_weight == w and limits[w] <= 1e-10, limits
    grid, independent, hessian = [], [], []
    for r in read(OUT/'figure-5-printed.csv'):
        a,T = float(r['loading']),float(r['T_K'])
        w = weight(a,T)
        p = pressure(a,T,FIGURE_WATER,w)
        mix = model(w)
        state = mix.state(T, rho=p['liquid_density_mol_m3'], x=p['liquid'])
        X = state.site_fractions
        grid.append(dict(T_K=T,loading=a,**p, carbamate=w*(1-X[4]**2), bicarbonate=(1-w)*(1-X[9]),
                         printed_carbamate=float(r['carbamate']), printed_bicarbonate=float(r['bicarbonate'])))
        reference = {(.1,313.15):1.539633,(.5,313.15):2502.019,(.4,393.15):134289.998}.get((a,T))
        if reference is not None:
            assert p['stability']==UNSTABLE
            independent_P, residual = equal_fugacity(mix,a,T,FIGURE_WATER,p)
            independent.append(dict(loading=a,T_K=T,reference_Pa=reference,independent_Pa=independent_P,
                pinned_Pa=p['predicted'],relative_difference=relative(p['predicted'],independent_P), residual=residual))
        if reference is not None or (a,T) in ((.7,333.15),(.3,363.15)):
            assert p['stability']==UNSTABLE
            values = [eigenvalue_fd(mix,T,composition(a,FIGURE_WATER),p['liquid_density_mol_m3'],step) for step in (1e-6,5e-7)]
            hessian.append(dict(loading=a,T_K=T,engine=p['minimum_eigenvalue'],step=values[0],half_step=values[1]))
    table(run/'grid.csv', grid)
    fig4 = json.loads((OUT/'figure-4b-calibration.json').read_text())
    fig4['model_Pa'] = next(p['predicted'] for p in grid
                            if (p['T_K'],p['loading'])==(fig4['reference_temperature_K'],fig4['reference_loading']))
    lo,hi = fig4['reading_interval_Pa']
    fig4['passed'] = lo <= fig4['model_Pa'] <= hi
    fractions = {}
    for key in ('carbamate','bicarbonate'):
        error = np.array([r[key]-r['printed_'+key] for r in grid])
        fractions[key] = dict(bias=float(error.mean()),rmse=float(np.sqrt(np.mean(error**2))),
                              abs_quantiles=dict(zip(('0','50','90','100'),np.quantile(abs(error),[0,.5,.9,1]).tolist())))
    checks = dict(weight_knots_exact=90, residual_helmholtz_limit_relative=limits, independent=independent,
                  hessian=hessian, figure_4b=fig4, figure_5=fractions,
                  grid_stability=dict(Counter(r['stability'] for r in grid)))
    write_json(run/'pressure-checks.json',checks)
    assert len(independent)==3 and all(r['relative_difference']<=5e-8 and
        round(r['independent_Pa'],6 if r['loading']==.1 else 3)==r['reference_Pa'] for r in independent), independent
    assert len(hessian)==5 and all(r['engine']<0 and len({f'{v:.4g}' for v in (r['engine'],r['step'],r['half_step'])})==1
                                   for r in hessian), hessian
    assert fig4['passed'], fig4
    return checks


def heat(row):
    a,b,T,w = (row[k] for k in ('previous_loading','loading','T_K','water_per_mea'))
    points = [a, a+(b-a)/4, a+(b-a)/2, a+3*(b-a)/4, b]
    output, states = {}, []
    for side in ((1,) if T==313.15 else (-1,) if T==393.15 else (-1,1)):
        label = 'warm' if side==1 else 'cool'
        for step in (.1,.01):
            Ta = T+side*step
            p = [(pressure(x,T,w,weight(x,T)),pressure(x,Ta,w,weight(x,Ta))) for x in points]
            states.extend(q for pair in p for q in pair)
            g = [-R*math.log(v['predicted']/u['predicted'])/(1/Ta-1/T)/1000 for u,v in p]
            output.update({f'{label}_{step}_simpson':(g[0]+4*g[2]+g[4])/6,
                           f'{label}_{step}_halved':(g[0]+4*g[1]+2*g[2]+4*g[3]+g[4])/12,
                           f'{label}_{step}_endpoint':g[4]})
    unstable = [r for r in states if r['stability']==UNSTABLE]
    return dict(output, stability=UNSTABLE if unstable else STABLE,
                minimum_eigenvalue=min((q['minimum_eigenvalue'] for q in unstable),default=None),
                max_solver_residual=max(q['max_solver_residual'] for q in states),
                w=weight(b,T), pressure_states=len(states), unstable_pressure_states=len(unstable),
                min_w=min(q['w'] for q in states), max_w=max(q['w'] for q in states))


def predict(row):
    T,a,water = (row[k] for k in ('T_K','analytical_loading','water_per_mea'))
    if row['block'].startswith('Kim '):
        return heat(row)
    w = weight(a,313.15 if row['hilliard_edge'] else T)
    if not row['pressure_Pa']:
        return pressure(a,T,water,w)
    x = composition(a,water)
    P = float(row['pressure_Pa'])
    state = model(w).state(T,P=P,x=x,phase='liquid')
    return dict(predicted=float(state.molar_density*(x @ list(MASS.values()))), w=w,
                liquid_density_mol_m3=state.molar_density, pressure_residual_Pa=state.pressure-P)


def run_comparison(run):
    started = perf_counter()
    shared.verify_wheel()
    path = OUT/'admission.csv'
    assert path.read_bytes()==subprocess.check_output(['git','show',f'cdc1d4ddf:{path.relative_to(BUNDLE.parents[1])}'])
    rows = comparison_rows(path)
    full_replay = replay_comparison(rows)
    assert Counter(r['block'] for r in rows if r['three_model_eligible']) == {
        'canonical':145,'wagner':23,'Kim 313.15 K':21,'Kim 353.15 K':20,'Kim 393.15 K':15,
        'Amundsen2009':18,'Hartono2014':25,'Han2012':45,
    }
    run.mkdir(parents=True,exist_ok=False)
    checks = dict(pressure_checks(run),full_pressure_replay_AARD_percent=full_replay)
    selected = [r for r in rows if r['hong_eligible']]
    observed_water(selected)
    for block in dict.fromkeys(r['block'] for r in selected):
        group = [r for r in selected if r['block']==block]
        for r in group:
            try:
                r.update(predict(r),failure='')
            except (RuntimeError,ValueError) as exc:
                r['failure'] = str(exc)
        table(run/f'{block}.csv',group)
        print(block,len(group),sum(bool(r['failure']) for r in group),flush=True)
    assert not any(r['failure'] for r in selected), 'Failed rows retained in the block tables.'
    checks['stable_fixed_vapor'] = dict(
        tried=len(STABLE_PINNED), converged=sum(not r['failure'] for r in STABLE_PINNED),
        max_relative_difference=max(r['relative_difference'] for r in STABLE_PINNED if not r['failure']),
        failures=[r for r in STABLE_PINNED if r['failure']])
    summary = hong_scores(selected)
    table(run/'scores.csv',summary)
    table(run/'supplement-table.csv',[r for r in summary if r['subset'] in ('all','strict grid')])
    write_json(run/'checks.json',dict(checks,engine_commit=shared.ENGINE_COMMIT,
        wheel_sha256=shared.ENGINE_WHEEL_SHA256, admission_sha256=digest(path),
        pressure_states=pressure.cache_info().currsize, wall_seconds=perf_counter()-started))


if __name__ == '__main__':
    assert len(sys.argv)==2
    destination = Path(sys.argv[1]).resolve()
    assert subprocess.run(['git','check-ignore','-q',destination],check=False).returncode==0
    run_comparison(destination)
