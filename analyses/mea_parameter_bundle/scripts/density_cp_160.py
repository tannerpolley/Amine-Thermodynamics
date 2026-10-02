"""Issue 160: pinned native fits and physical checks; no parameter promotion."""
import copy
import csv
import json
import math
import os
from pathlib import Path
import sys
import time

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
os.environ['FINAL_RERUN'] = '1'
BUNDLE = Path(__file__).resolve().parents[1]
ROOT = BUNDLE.parents[1]
OUT = BUNDLE / 'results/density-cp-160'
sys.path[:0] = [str(BUNDLE / 'scripts'), str(BUNDLE / 'calibration-misfit')]
from final_rerun import module
import shared_evaluation as s
import verify_reference_calorics as vrc
import verify_temperature_reference as vt
import verify_solution_heat_capacity as hc
import epcsaft
from epcsaft import regression, equilibrium as eq

F1 = BUNDLE / 'results/final-rerun/F1-parameters.json'
IONS = ('protonated-monoethanolamine', 'carbamate-anion')
DENSITIES = ((323.15, .3, 1058.), (323.15, .4, 1083.),
             (343.15, .3, 1046.4), (343.15, .4, 1071.9))
HILLIARD = ((318.15, 0., 3.7195), (318.15, .358, 3.3675), (353.15, .358, 3.4707))


def table(name, rows):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader()
        writer.writerows(rows)


def json_out(name, value):
    s.write_json(OUT / name, value)


def new_water(mapping):
    changes = {'component/water/segment_count': 1.3340338,
               'component/water/dispersion_energy_over_k': 415.47578,
               'component/water/segment_diameter/constant-plus-sum-of-exponentials/constant': 2.7176052}
    out = s.with_parameter_values(mapping, changes)
    for edge in out['topology']['edges']:
        components = {edge[k]['component_id'] for k in ('endpoint_a', 'endpoint_b')}
        if components == {'water'} or components == {'water', 'carbon-dioxide'}:
            edge['energy_over_k']['value']['magnitude'] = 1725.6848 if components == {'water'} else 862.8424
            edge['volume']['value']['magnitude'] = .04610350
    return out


# Copied from Engine mea_water.py: unchanged Cai temperature and vapor composition objective.
def cai_problem(row):
    water = float(row['water_liquid_mole_fraction'])
    return eq.Problem(phases=[eq.Phase('L', kind='liquid'), eq.Phase('V', kind='vapor', amount=eq.Pinned(0.))],
                      T=eq.Free(float(row['temperature_k'])), P=float(row['pressure_pa']),
                      feed=eq.MoleFractions({'water': water, 'monoethanolamine': 1.-water}))


def cai_observations(parameters, rows):
    items = []
    for row in rows:
        problem = cai_problem(row)
        items.extend((regression.observation(parameters, 'temperature', problem,
            observed=float(row['temperature_k']), form='difference', scale=1., mass_basis=False),
            regression.observation(parameters, 'mole_fraction', problem,
            observed=float(row['water_vapor_mole_fraction']), phase='V', species=('water',),
            form='difference', scale=.01, mass_basis=False)))
    return items


def predictions(parameters, items):
    values = [regression.predict(epcsaft.Mixture(parameters), item) for item in items]
    if any(v.status != regression.ObservationStatus.Available or not math.isfinite(v.value) for v in values):
        raise RuntimeError([(v.status.name, v.message) for v in values if v.status != regression.ObservationStatus.Available])
    return [v.value for v in values]


def fit_summary(fit, elapsed):
    return {**{k: s._jsonable(getattr(fit, k)) for k in ('status', 'message', 'usable', 'initial_cost',
        'final_cost', 'physical', 'predictions', 'weighted_residuals', 'optimizer_jacobian',
        'iterations', 'iteration_costs', 'iteration_seconds', 'trial_failures')},
        'active_bounds': list(fit.covariance.active_bounds), 'wall_s': elapsed,
        'observation_statuses': [v.name for v in fit.statuses]}


def complete(fit):
    if fit.status != 'converged' or not fit.usable or not math.isfinite(fit.final_cost) or any(
            v != regression.ObservationStatus.Available for v in fit.statuses):
        raise RuntimeError(f'incomplete/non-finite fit: {fit.status}: {fit.message}')


def binaries():
    s.verify_wheel()
    old = s.parameter_mapping(F1)
    updated = new_water(old)
    rows = [r for r in csv.DictReader((ROOT / 'data/reference/MEA/observations/vapor_liquid_equilibrium/Cai_1996_MEA_H2O_VLE.csv').open())
            if r['role'] in {'binary_model_selection', 'binary_training'}]
    assert len(rows) == 25
    kiepe = module('kiepe160', ROOT / 'analyses/reactive_epcsaft_parameter_evidence/co2_water_induced_association/scripts/generate.py')
    cases = [('MEA-water', ('water', 'monoethanolamine'), rows),
             ('CO2-water', kiepe.COMPONENTS, kiepe.source_rows())]
    summary, values = {}, []
    for label, components, source in cases:
        assert len(source) == (25 if label == 'MEA-water' else 39)
        def items(parameters):
            if label == 'MEA-water':
                return cai_observations(parameters, source)
            model = epcsaft.Mixture(parameters)
            observations, warm, previous = [], None, None
            for r in source:
                T, x = float(r['temperature_k']), float(r['liquid_co2_mole_fraction'])
                if T != previous:
                    warm, previous = None, T
                problem = kiepe.problem(T, x)
                # Converged old-water anchors declare every row, including high-pressure rows.
                problem.P = eq.Free(warm.pressure[0] if warm else 1000*float(r['observed_pressure_kpa']))
                problem.phases = [eq.Phase(p.name, support=p.support, kind=p.kind, amount=p.amount,
                    composition_guess=tuple(warm.mole_fractions[2*i:2*i+2]) if warm else
                    ((.99,.01) if p.kind=='vapor' else (x,1.-x))) for i,p in enumerate(problem.phases)]
                warm = eq.solve_equilibrium(model, problem, warm)
                if not warm.success:
                    raise RuntimeError(f'{r["row_id"]}: {warm.message}')
                problem.P = eq.Free(warm.pressure[0])
                problem.phases = [eq.Phase(p.name, support=p.support, kind=p.kind, amount=p.amount,
                    composition_guess=tuple(warm.mole_fractions[2*i:2*i+2])) for i,p in enumerate(problem.phases)]
                observations.append(regression.observation(parameters, 'pressure', problem,
                    observed=1000*float(r['observed_pressure_kpa']), form='log_ratio', mass_basis=False))
            return observations
        before = epcsaft.Parameters.from_mapping(old, components=components)
        params = epcsaft.Parameters.from_mapping(updated, components=components)
        observations = items(before)
        old_y = predictions(before, observations)
        identity = next(c['identity'] for p in updated['pairs'] if {p['component_id_a'], p['component_id_b']} == set(components)
                        for c in p['coefficients'] if c['family'] == 'k_ij')
        origin = s.parameter_values(updated)[identity]
        bounds = (origin-.03, origin+.03) if label == 'MEA-water' else (-.5, .5)
        coordinate = regression.coordinate(params, 'k_ij', components, origin=origin, scale=1., bounds=bounds)
        start = time.monotonic()
        fit = regression.fit(params, [coordinate], observations)
        elapsed = time.monotonic()-start
        result = fit_summary(fit, elapsed)
        result['failures'] = [dict(observation=f.observation, status=f.status.name, message=f.message) for f in fit.failures]
        json_out(label+'-fit.json', result)
        complete(fit)
        new_y = predictions(params, observations)
        updated = s.with_parameter_values(updated, {identity: fit.physical[0]})
        for i, (observation, y0, y1, y2) in enumerate(zip(observations, old_y, new_y, fit.predictions, strict=True)):
            values.append(dict(binary=label, row_id=source[i//2 if label=='MEA-water' else i]['row_id'],
                quantity=('temperature_K' if i%2==0 else 'vapor_water') if label=='MEA-water' else 'pressure_Pa',
                observed=observation.observed, old_water=y0, new_water_before_refit=y1, after_refit=y2))
        summary[label] = dict(k_ij_before=origin, k_ij_after=fit.physical[0], bounds=bounds, wall_s=elapsed,
                             final_cost=fit.final_cost)
        for quantity in {r['quantity'] for r in values if r['binary']==label}:
            part = [r for r in values if r['binary']==label and r['quantity']==quantity]
            summary[label][quantity] = {key+'_AARD_percent':100*sum(abs(r[key]/r['observed']-1) for r in part)/len(part)
                                      for key in ('old_water','new_water_before_refit','after_refit')}
        table('stage1-binary-values.csv', values)
        json_out('stage1.json', summary)
    table('stage1-binary-values.csv', values)
    json_out('stage1.json', summary)
    json_out('new-water-binaries-parameters.json', updated)
    print('STAGE1', json.dumps(summary), flush=True)
    return updated


def request(mapping, T, loading, density=False):
    template = next(o['request'] for o in s.load_state_packet()['observations'] if o['identity']=='Bottinger2008_state_046')
    req = s.source_feed_request(template, dict(source_key='Amundsen2009', CO2_loading=loading,
        temperature_reported_C=T-273.15, MEA_weight_fraction=.30))
    req = vt.request_at(req, T, 101325., liquid_only=True)
    if density:
        req['outputs'] = [dict(identity='phase-density', selector='phase.density',
            phase_identity=req['phases'][0]['identity'], unit='kilogram / meter ** 3')]
    return s.corrected_request(req, s.reaction_values(mapping))


def neutral_problem(T):
    # No absorbed-carbon species at alpha=0. Keep aqueous MEA protonation and water dissociation.
    mapping = s.parameter_mapping(F1)
    req = request(mapping, T, .1)
    prob = s._problem_from_request(req)
    allowed = ('monoethanolamine', 'water', 'protonated-monoethanolamine', 'hydroxide-anion', 'hydronium-cation')
    prob.phases = [eq.Phase(prob.phases[0].name, support=allowed, kind='liquid')]
    masses = req['reaction_system']['molar_masses_kg_per_mol']
    water = .7*masses[1]/(.3*masses[2])
    prob.feed = eq.Amounts({'monoethanolamine':1., 'water':water})
    prob.reactions = [reaction for reaction, coefficients in zip(prob.reactions, req['reaction_system']['reaction_matrix'], strict=True)
                      if all(c==0 or name in allowed for name,c in zip(s.COMPONENT_IDS, coefficients, strict=True))]
    return prob


def cp_check(mapping, T, loading, observed):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=vrc.record())
    problem = neutral_problem(T) if loading==0 else s._problem_from_request(request(mapping,T,loading))
    result = eq.solve_equilibrium(model, problem)
    if not result.success:
        raise RuntimeError(result.message)
    mass = sum(problem.feed.values.get(c,0.)*m for c,m in zip(s.COMPONENT_IDS,hc.MOLAR_MASS))/1000
    (h, dh), (n, dn) = vrc.first_actions(model, problem, result, [vrc.observable('PhaseProperty',0,
        prop=epcsaft.PropertyObservable.TotalEnthalpy),vrc.observable('PhaseAmount',0)],[(1.,0.,None)])[0]
    ((cp,_),) = vrc.first_actions(model, problem, result, [vrc.observable('PhaseProperty',0,
        prop=epcsaft.PropertyObservable.TotalIsobaricHeatCapacity)],[(0.,0.,None)])[0]
    equilibrium_cp = (n*dh+h*dn)/mass/1000
    return dict(T_K=T, loading=loading, observed_kJ_kg_K=observed, equilibrium_cp_kJ_kg_K=equilibrium_cp,
                deviation_percent=100*(equilibrium_cp/observed-1), frozen_cp_kJ_kg_K=cp*n/mass/1000)


def unloaded(mapping):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    rows=[]
    for reference in json.loads((OUT/'iapws95-reference.json').read_text()):
        T=reference['T_K']; x={c:float(c=='water') for c in s.COMPONENT_IDS}
        state=model.state(T,P=101325.,x=x,phase='liquid')
        cp=(state.residual_isobaric_heat_capacity+hc.water_ideal_cp(T))/18.01528
        rho=state.molar_density*.01801528
        rows.append({**reference,'model_rho_kg_m3':rho,'model_cp_kJ_kg_K':cp,
            'density_deviation_percent':100*(rho/reference['rho_kg_m3']-1),
            'cp_deviation_percent':100*(cp/reference['cp_kJ_kg_K']-1)})
    table('stage2-water.csv',rows)
    cp=cp_check(mapping,*HILLIARD[0])
    params=epcsaft.Parameters.from_mapping(mapping)
    densities=[]
    for row in csv.DictReader((ROOT/'data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv').open()):
        if row['property']=='density' and float(row['mea_mass_fraction'])==.30 and not row['co2_loading_mol_per_mol_mea']:
            T=float(row['temperature_C'])+273.15
            problem=neutral_problem(T)
            item=regression.observation(params,'phase_density',problem,phase=problem.phases[0].name,
                observed=1000*float(row['value']),form='log_ratio',mass_basis=True)
            y=predictions(params,[item])[0]
            densities.append(dict(T_K=T,observed_kg_m3=item.observed,model_kg_m3=y,deviation_percent=100*(y/item.observed-1)))
    table('stage2-unloaded-density.csv',densities)
    json_out('stage2.json',dict(water=rows,unloaded_density=densities,unloaded_heat_capacity=cp,
        water_cp_passed=all(abs(r['cp_deviation_percent'])<=3 for r in rows)))
    print('STAGE2',json.dumps(dict(water=rows,unloaded_density=densities,unloaded_heat_capacity=cp)),flush=True)
    if not all(abs(r['cp_deviation_percent'])<=3 for r in rows):
        raise RuntimeError('pure-water heat capacity acceptance failed')


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1:] == ['prepare']:
        started=time.monotonic()
        unloaded(binaries())
        json_out('stage1-2-execution.json',dict(wall_s=time.monotonic()-started,wheel_sha256=s.ENGINE_WHEEL_SHA256))
