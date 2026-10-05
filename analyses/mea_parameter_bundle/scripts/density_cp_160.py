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
            not math.isfinite(v) for values in (fit.physical,fit.predictions,fit.weighted_residuals) for v in values) or any(
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


def co2_continuation():
    """Owner-authorized subset initialization, then the unchanged 39-row fit."""
    s.verify_wheel()
    mapping = new_water(s.parameter_mapping(F1))
    mea = json.loads((OUT/'MEA-water-fit.json').read_text())
    mapping = s.with_parameter_values(mapping, {'pair/monoethanolamine/water/k_ij':mea['physical'][0]})
    kiepe = module('kiepe160', ROOT/'analyses/reactive_epcsaft_parameter_evidence/co2_water_induced_association/scripts/generate.py')
    source = kiepe.source_rows()
    params = epcsaft.Parameters.from_mapping(mapping, components=kiepe.COMPONENTS)
    model = epcsaft.Mixture(params)
    selected, failed, rows = [], [], []
    for row in source:
        T, x = float(row['temperature_k']), float(row['liquid_co2_mole_fraction'])
        problem = kiepe.problem(T,x)
        problem.P = eq.Free(1000*float(row['observed_pressure_kpa']))
        problem.phases = [eq.Phase(p.name, kind=p.kind, amount=p.amount,
            composition_guess=(.99,.01) if p.kind=='vapor' else (x,1.-x)) for p in problem.phases]
        result = eq.solve_equilibrium(model,problem)
        if not result.success:
            failed.append(dict(row_id=row['row_id'],message=result.message))
            continue
        selected.append(row['row_id'])
        rows.append(regression.observation(params,'pressure',problem,observed=1000*float(row['observed_pressure_kpa']),
                                           form='log_ratio',mass_basis=False))
    identity = 'pair/carbon-dioxide/water/k_ij'
    origin = s.parameter_values(mapping)[identity]
    started = time.monotonic()
    fit = regression.fit(params,[regression.coordinate(params,'k_ij',kiepe.COMPONENTS,
        origin=origin,scale=1.,bounds=(-.5,.5))],rows)
    partial = fit_summary(fit,time.monotonic()-started)
    partial.update(targets=selected,initially_unavailable=failed,role='initialization only; final fit uses all 39 rows')
    json_out('CO2-water-continuation-fit.json',partial)
    complete(fit)
    mapping = s.with_parameter_values(mapping,{identity:fit.physical[0]})
    params = epcsaft.Parameters.from_mapping(mapping,components=kiepe.COMPONENTS)
    model = epcsaft.Mixture(params)
    observations, chain_points = [], []
    warm, previous_T, previous_x = None, None, None
    def carry(T, left, right, start, depth=0):
        problem = kiepe.problem(T,right)
        trial = eq.solve_equilibrium(model,problem,start)
        if trial.success:
            return trial
        if depth==8:
            raise RuntimeError(f'Kiepe composition continuation failed: T={T}, x={right}: {trial.message}')
        middle = (left+right)/2
        midway = carry(T,left,middle,start,depth+1)
        chain_points.append(dict(T_K=T,x_co2=middle,pressure_Pa=midway.pressure[0],target=False))
        return carry(T,middle,right,midway,depth+1)
    for row in source:
        T, x = float(row['temperature_k']),float(row['liquid_co2_mole_fraction'])
        problem = kiepe.problem(T,x)
        if T!=previous_T:
            problem.P = eq.Free(1000*float(row['observed_pressure_kpa']))
            problem.phases = [eq.Phase(p.name,kind=p.kind,amount=p.amount,
                composition_guess=(.99,.01) if p.kind=='vapor' else (x,1.-x)) for p in problem.phases]
            warm = eq.solve_equilibrium(model,problem)
            if not warm.success:
                raise RuntimeError(f'{row["row_id"]}: {warm.message}')
        else:
            warm = carry(T,previous_x,x,warm)
        previous_T,previous_x = T,x
        problem.P = eq.Free(warm.pressure[0])
        problem.phases = [eq.Phase(p.name,kind=p.kind,amount=p.amount,
            composition_guess=tuple(warm.mole_fractions[2*i:2*i+2])) for i,p in enumerate(problem.phases)]
        observations.append(regression.observation(params,'pressure',problem,observed=1000*float(row['observed_pressure_kpa']),
                                                  form='log_ratio',mass_basis=False))
    assert len(observations)==39
    started=time.monotonic()
    fit=regression.fit(params,[regression.coordinate(params,'k_ij',kiepe.COMPONENTS,
        origin=s.parameter_values(mapping)[identity],scale=1.,bounds=(-.5,.5))],observations)
    full=fit_summary(fit,time.monotonic()-started)
    full.update(targets=[r['row_id'] for r in source],solver_path_points=chain_points,
                initialization_k_ij=s.parameter_values(mapping)[identity])
    json_out('CO2-water-full39-fit.json',full)
    complete(fit)
    mapping=s.with_parameter_values(mapping,{identity:fit.physical[0]})
    baseline=list(csv.DictReader((OUT/'stage1-co2-water-baseline.csv').open()))
    values=[dict(row_id=row['row_id'],observed_pressure_Pa=item.observed,old_water_pressure_Pa=float(prior['old_water_pressure_Pa']),
                 after_refit_pressure_Pa=y,deviation_percent=100*(y/item.observed-1))
            for row,item,y,prior in zip(source,observations,fit.predictions,baseline,strict=True)]
    table('stage1-co2-water-values.csv',values)
    summary=json.loads((OUT/'stage1.json').read_text())
    summary['CO2-water']=dict(status=fit.status,usable=fit.usable,k_ij_before=origin,k_ij_after=fit.physical[0],
        old_water_AARD_percent=100*sum(abs(r['old_water_pressure_Pa']/r['observed_pressure_Pa']-1) for r in values)/39,
        after_refit_AARD_percent=sum(abs(r['deviation_percent']) for r in values)/39,
        final_cost=fit.final_cost,subset_fit_wall_s=partial['wall_s'],full_fit_wall_s=full['wall_s'],
        subset_rows=len(selected),final_rows=39,solver_path_points=len(chain_points))
    json_out('stage1.json',summary)
    json_out('new-water-binaries-parameters.json',mapping)
    print('STAGE1',json.dumps(summary),flush=True)
    return mapping


def request(mapping, T, loading, density=False):
    template = next(o['request'] for o in s.load_state_packet()['observations'] if o['identity']=='Bottinger2008_state_046')
    req = s.source_feed_request(template, dict(source_key='Amundsen2009', CO2_loading=loading,
        temperature_reported_C=T-273.15, MEA_weight_fraction=.30))
    if loading < .0001:
        system = req['reaction_system']
        analytical = system['analytical_feed_contract']['neutral_analytical_amounts_mol']
        # Scale only the balanced numerical seeds for the absorber's unloaded trace proxy.
        system['feed_amounts_mol'] = [a + .01*(v-a) for a,v in zip(analytical,system['feed_amounts_mol'],strict=True)]
        system.pop('analytical_feed_contract')
        req['feed'] = dict(generation='density-cp-160', basis='30 wt% CO2-free solvent',
                           proxy_loading=loading, numerical_seed_scale=.01)
    req = vt.request_at(req, T, 101325., liquid_only=True)
    if density:
        req['outputs'] = [dict(identity='phase-density', selector='phase.density',
            phase_identity=req['phases'][0]['identity'], unit='kilogram / meter ** 3')]
    return s.corrected_request(req, s.reaction_values(mapping))


def neutral_problem(T):
    # Reuse physical_acceptance_149's alpha=1e-5 proxy for the alpha=0 observation.
    return s._problem_from_request(request(s.parameter_mapping(F1), T, 1e-5))


def cp_check(mapping, T, loading, observed):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=vrc.record())
    problem = s._problem_from_request(request(mapping,T,max(loading,1e-5)))
    result = eq.solve_equilibrium(model, problem)
    if not result.success:
        raise RuntimeError(result.message)
    mass = sum(problem.feed.values.get(c,0.)*m for c,m in zip(s.COMPONENT_IDS,hc.MOLAR_MASS))/1000
    (h, dh), (n, dn) = vrc.first_actions(model, problem, result, [vrc.observable('PhaseProperty',0,
        prop=epcsaft.PropertyObservable.TotalEnthalpy),vrc.observable('PhaseAmount',0)],[(1.,0.,None)])[0]
    ((cp,_),) = vrc.first_actions(model, problem, result, [vrc.observable('PhaseProperty',0,
        prop=epcsaft.PropertyObservable.TotalIsobaricHeatCapacity)],[(0.,0.,None)])[0]
    equilibrium_cp = (n*dh+h*dn)/mass/1000
    return dict(T_K=T, loading=loading, model_loading=max(loading,1e-5), observed_kJ_kg_K=observed, equilibrium_cp_kJ_kg_K=equilibrium_cp,
                deviation_percent=100*(equilibrium_cp/observed-1), frozen_cp_kJ_kg_K=cp*n/mass/1000)


def unloaded(mapping):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    rows=[]
    for reference in json.loads((OUT/'iapws95-reference.json').read_text()):
        T=reference['T_K']; x=[float(c=='water') for c in s.COMPONENT_IDS]
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


def reactive_fit(problem_name, letter):
    directory=OUT/(problem_name+'-'+letter)
    directory.mkdir(parents=True,exist_ok=True)
    os.environ['SENSITIVITY_OUTPUT']=str(directory)
    os.environ['FINAL_POOL']='1' if problem_name in ('F4','F5') else '0'
    owner=module('p5160',BUNDLE/'model-d/born-form-diagnosis/p5conv-fit.py')
    d=owner.d
    adopted=json.loads((OUT/'new-water-binaries-parameters.json').read_text())
    original=BUNDLE/'model-d/born-form-diagnosis/p5conv-a-00-diagnostic-parameters.json'
    primary=BUNDLE/'results/final-rerun/v1-start-parameters.json'
    off=BUNDLE/'model-d/sensitivity-current/ablation-off-11-diagnostic-parameters.json'
    paths={'F1':(F1,F1),'F2':(original,primary),'F3':(off,primary),
           'F4':(primary,original),'F5':(original,primary)}
    if problem_name=='F6':
        low=module('low160',BUNDLE/'results/temperature-reanchor-140/low-temperature-fit.py')
        low.NATIVE_INPUTS=low.HERE/'native-reaction-inputs.json'
        mapping,_,_=low.source_context()
        ids,bounds,scales,values=low.design('slope-fixed','1' if letter=='A' else '2')
        mapping=s.with_parameter_values(mapping,dict(zip(ids,values,strict=True)))
    else:
        mapping=s.parameter_mapping(original if problem_name in ('F2','F5') else F1)
        values=s.parameter_values(s.parameter_mapping(paths[problem_name][letter=='B']))
        mapping=s.with_parameter_values(mapping,{identity:values[identity] for identity in d.IDS})
    old_water=copy.deepcopy(mapping)
    mapping=new_water(mapping)
    binary_ids=('pair/monoethanolamine/water/k_ij','pair/carbon-dioxide/water/k_ij')
    mapping=s.with_parameter_values(mapping,{identity:s.parameter_values(adopted)[identity] for identity in binary_ids})
    old_water=s.with_parameter_values(old_water,{identity:s.parameter_values(adopted)[identity] for identity in binary_ids})
    ion_m=2. if letter=='A' else 1.
    mapping=s.with_parameter_values(mapping,{f'component/{ion}/segment_count':ion_m for ion in IONS})
    old_water=s.with_parameter_values(old_water,{f'component/{ion}/segment_count':1. for ion in IONS})
    if problem_name=='F3':
        for document in (mapping,old_water):
            family=next(f for f in document['model_families'] if f['kind']=='electrolyte')
            family['choice']='fully-dissociated-debye-huckel'
            for key in ('c_shell','c_dielectric'):
                family.pop(key,None)
            for component in document['components']:
                component['coefficients']=[c for c in component['coefficients'] if c['family'] not in ('solvation_factor','born_diameter')]
            document['model_coefficients']=[c for c in document['model_coefficients'] if c['family']!='ionic_region_relative_permittivity']
    def build(document):
        params,groups,rows=d.rows_for(document,'11')
        for T,a,rho in DENSITIES:
            req=request(document,T,a,density=True)
            prob=s._problem_from_request(req)
            groups.append((dict(identity=f'Amundsen_{T}_{a}',request=req,targets=[]),prob))
            rows.append((f'Amundsen_{T}_{a}',regression.observation(params,'phase_density',prob,
                phase=prob.phases[0].name,observed=rho,form='log_ratio',mass_basis=True),3906.25))
        return params,groups,rows
    params,groups,rows=build(mapping)
    v=s.parameter_values(mapping)
    ids=[*d.IDS,'shared-ion-segment-count']
    coords=[regression.coordinate(params,'k_ij_reciprocal_temperature_slope' if identity.endswith(d.design.probe.SLOPE) else 'k_ij',
        tuple(identity.split('/')[1:3]),origin=v[identity],scale=float(scale),bounds=(float(lo),float(hi)))
        for identity,scale,lo,hi in zip(d.IDS,d.SCALES,d.LOWER,d.UPPER,strict=True)]
    coords.append(regression.coordinate(params,'segment_count',*IONS,origin=ion_m,scale=.1,bounds=(.5,5.)))
    controls=regression.FitControls();controls.maximum_iterations=40;controls.maximum_elapsed_time_seconds=2250.
    started=time.monotonic()
    fit=regression.fit(params,coords,[r[1] for r in rows],weights=[r[2] for r in rows],controls=controls)
    path=[]
    if fit.status=='initial_evaluation_failed':
        s.write_json(directory/'initial-failed-fit.json',fit_summary(fit,time.monotonic()-started))
        # Owner-authorized state continuation; these points never become observations.
        old_params,old_groups,_=build(old_water)
        warm=[None]*len(old_groups)
        for fraction in (0.,.25,.5,.75,1.):
            blended=copy.deepcopy(old_water)
            old_values=s.parameter_values(old_water);new_values=s.parameter_values(mapping)
            water_ids=[i for i in new_values if i.startswith('component/water/') or
                i.startswith('association/') and '/water/' in i and ('/carbon-dioxide/' in i or i.startswith('association/water/'))]
            path_ids=water_ids+[f'component/{ion}/segment_count' for ion in IONS]
            blended=s.with_parameter_values(blended,{i:old_values[i]+fraction*(new_values[i]-old_values[i]) for i in path_ids})
            model=epcsaft.Mixture(epcsaft.Parameters.from_mapping(blended))
            _,next_groups,_=build(blended)
            for i,(o,prob) in enumerate(next_groups):
                if warm[i] is not None:
                    prob.P=eq.Free(warm[i].pressure[0]) if isinstance(prob.P,eq.Free) else prob.P
                    width=len(s.COMPONENT_IDS)
                    prob.phases=[eq.Phase(p.name,support=p.support,kind=p.kind,amount=p.amount,
                        composition_guess=tuple(warm[i].mole_fractions[j*width+s.COMPONENT_IDS.index(c)] for c in p.support))
                        for j,p in enumerate(prob.phases)]
                solved=eq.solve_equilibrium(model,prob,warm[i])
                if not solved.success:
                    s.write_json(directory/'continuation-failure.json',dict(fraction=fraction,state=o['identity'],message=solved.message))
                    raise RuntimeError(f'water continuation failed: {o["identity"]}, fraction={fraction}: {solved.message}')
                warm[i]=solved
            path.append(dict(water_fraction=fraction,ion_m=1.+fraction*(ion_m-1.),states=len(warm),target=False))
        # Rebuild unchanged observations on the carried liquid and vapor guesses.
        rows=[]
        for i,(o,prob) in enumerate(groups):
            width=len(s.COMPONENT_IDS)
            prob.P=eq.Free(warm[i].pressure[0]) if isinstance(prob.P,eq.Free) else prob.P
            prob.phases=[eq.Phase(p.name,support=p.support,kind=p.kind,amount=p.amount,
                composition_guess=tuple(warm[i].mole_fractions[j*width+s.COMPONENT_IDS.index(c)] for c in p.support))
                for j,p in enumerate(prob.phases)]
            if o['identity'].startswith('Amundsen_'):
                T,a,rho=DENSITIES[i-len(d.OBS)]
                rows.append((o['identity'],regression.observation(params,'phase_density',prob,phase=prob.phases[0].name,
                    observed=rho,form='log_ratio',mass_basis=True),3906.25))
            else:
                rows.extend(d.design.refit.observations(params,o,prob,80))
        fit=regression.fit(params,coords,[r[1] for r in rows],weights=[r[2] for r in rows],controls=controls)
    raw=fit_summary(fit,time.monotonic()-started)
    raw.update(coordinates=ids,scales=[*map(float,d.SCALES),.1],targets=[r[0] for r in rows],
        observed=[r[1].observed for r in rows],solver_path=path,
        failures=[dict(observation=f.observation,status=f.status.name,message=f.message) for f in fit.failures])
    s.write_json(directory/'native-fit.json',raw)
    complete(fit)
    final=s.with_parameter_values(mapping,{**dict(zip(d.IDS,fit.physical[:5],strict=True)),
        **{f'component/{ion}/segment_count':fit.physical[5] for ion in IONS}})
    final['purpose']='Issue 160 candidate; not promoted.'
    s.write_json(directory/'parameters.json',final)


def fit_process(problem_name,letter):
    import subprocess
    directory=OUT/(problem_name+'-'+letter)
    directory.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    timeout=900 if problem_name=='F1' else 2400
    with (directory/'execution.log').open('w') as log:
        process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'fit',problem_name,letter],stdout=log,stderr=log)
        (directory/'child.pid').write_text(str(process.pid))
        watchdog=False
        try:
            code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill();process.wait();watchdog=True;code=None
        (directory/'child.pid').unlink(missing_ok=True)
    result=dict(problem=problem_name,start=letter,returncode=code,watchdog=watchdog,
                wall_s=time.monotonic()-started,timeout_s=timeout)
    s.write_json(directory/'execution.json',result)
    return result


def acceptance():
    starts=[]
    for letter in 'AB':
        raw=json.loads((OUT/f'F1-{letter}/native-fit.json').read_text())
        assert len(raw['physical'])==7 and raw['physical'][5]==raw['physical'][6]
        coordinate_values=raw['physical'][:6]
        if raw['status']!='converged' or not raw['usable']:
            raise RuntimeError('incomplete Stage 3 fit')
        n=len(raw['targets']);assert n==145
        cost=.5*sum(r*r for r in raw['weighted_residuals'][:141])
        aard={quantity:100*sum(abs(y/o-1) for target,y,o in zip(raw['targets'][:141],raw['predictions'][:141],raw['observed'][:141],strict=True)
            if (target.endswith('-pco2'))==(quantity=='pressure') and o>0)/sum((target.endswith('-pco2'))==(quantity=='pressure') and o>0
            for target,o in zip(raw['targets'][:141],raw['observed'][:141],strict=True)) for quantity in ('pressure','species')}
        density=[dict(T_K=T,loading=a,observed_kg_m3=rho,model_kg_m3=y,deviation_percent=100*(y/rho-1))
                 for (T,a,rho),y in zip(DENSITIES,raw['predictions'][-4:],strict=True)]
        starts.append(dict(start=letter,cost145=raw['final_cost'],cost141=cost,aard_percent=aard,density=density,
            ion_m=raw['physical'][5],tied_ion_segment_counts=dict(zip(IONS,raw['physical'][5:],strict=True)),
            coordinates=dict(zip(raw['coordinates'],coordinate_values,strict=True)),
            active_bounds=[raw['coordinates'][i] for i in raw['active_bounds']],fit_wall_s=raw['wall_s'],
            process_wall_s=json.loads((OUT/f'F1-{letter}/execution.json').read_text())['wall_s']))
    prior=json.loads((BUNDLE/'results/final-rerun/F1-A/runs/F1-A/F1-A-fit.json').read_text())
    gap=abs(starts[0]['cost145']-starts[1]['cost145'])/max(r['cost145'] for r in starts)
    best=min(starts,key=lambda r:r['cost145'])
    passed=best['cost141']<=1.10*prior['final_cost'] and all(abs(r['deviation_percent'])<=1.6 for r in best['density'])
    result=dict(starts=starts,selected=best['start'],agreement_relative=gap,start_agreement=gap<=1e-6,
        F1_cost141=prior['final_cost'],preservation_limit=1.10*prior['final_cost'],passed=passed,
        preservation_passed=best['cost141']<=1.10*prior['final_cost'],
        density_passed=all(abs(r['deviation_percent'])<=1.6 for r in best['density']))
    previous=next(r for r in json.loads((BUNDLE/'results/final-rerun/fit-summary.json').read_text()) if r['problem']=='F1')
    result['F1_aard_percent']=next(r['aard_percent'] for r in previous['starts'] if r['start']==previous['lower_complete_start'])
    json_out('acceptance.json',result)
    candidate=json.loads((OUT/f'F1-{best["start"]}/parameters.json').read_text())
    candidate['purpose']='Issue 160 candidate; '+('acceptance passed; not promoted.' if passed else 'failed 1.6% density acceptance; not promoted.')
    json_out('F1-prime-candidate-parameters.json',candidate)
    return result


def campaign():
    import concurrent.futures
    import multiprocessing
    import signal
    started=time.monotonic()
    workers=len(os.sched_getaffinity(0));runs=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        futures=[pool.submit(fit_process,'F1',letter) for letter in 'AB']
        for future in concurrent.futures.as_completed(futures):
            row=future.result();runs.append(row);print('STAGE3',json.dumps(row),flush=True)
            if row['watchdog'] or row['returncode']!=0:
                for pid in OUT.glob('F1-*/child.pid'):
                    try:os.kill(int(pid.read_text()),signal.SIGTERM)
                    except ProcessLookupError:pass
                json_out('campaign-execution.json',dict(runs=runs,workers=workers,threads=1,
                    wall_s=time.monotonic()-started,stop='Stage 3 watchdog' if row['watchdog'] else 'incomplete Stage 3 fit'))
                return
        result=acceptance();print('ACCEPTANCE',json.dumps(result),flush=True)
        if not result['passed']:
            json_out('campaign-execution.json',dict(runs=runs,workers=workers,threads=1,
                wall_s=time.monotonic()-started,stop='acceptance failure'))
            return
        # All remaining problems launch together, without an agent round trip.
        futures=[pool.submit(fit_process,f'F{i}',letter) for i in range(2,7) for letter in 'AB']
        for future in concurrent.futures.as_completed(futures):
            row=future.result();runs.append(row);print('STAGE4',json.dumps(row),flush=True)
            if row['returncode']!=0:
                for pid in OUT.glob('F*-*/child.pid'):
                    try:os.kill(int(pid.read_text()),signal.SIGTERM)
                    except ProcessLookupError:pass
                json_out('campaign-execution.json',dict(runs=runs,workers=workers,threads=1,
                    wall_s=time.monotonic()-started,stop='incomplete Stage 4 fit'))
                return
        json_out('campaign-execution.json',dict(runs=runs,workers=workers,threads=1,wall_s=time.monotonic()-started,
            stop=None if all(r['returncode']==0 for r in runs) else 'incomplete Stage 4 fit'))


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1:] == ['prepare']:
        started=time.monotonic()
        unloaded(co2_continuation())
        json_out('stage1-2-execution.json',dict(wall_s=time.monotonic()-started,wheel_sha256=s.ENGINE_WHEEL_SHA256))
    elif sys.argv[1:] == ['stage2']:
        unloaded(json.loads((OUT/'new-water-binaries-parameters.json').read_text()))
    elif sys.argv[1:2] == ['fit']:
        reactive_fit(*sys.argv[2:])
    elif sys.argv[1:] == ['campaign']:
        campaign()
    elif sys.argv[1:] == ['acceptance']:
        print(json.dumps(acceptance(),indent=2))
