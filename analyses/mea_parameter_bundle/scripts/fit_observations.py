"""Declared MEA pressure, species and integral-heat observations (#179)."""
import json
import math
import os
from pathlib import Path

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
import shared_evaluation as s
import verify_reference_calorics as thermal

ROOT = Path(__file__).resolve().parents[3]


def load(path):
    return json.loads((ROOT / path).read_text())


def indexed(rows, key):
    result = {r[key]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError(f'duplicate {key}')
    return result


def heat_items(mapping, params, sources, request):
    request = s.corrected_request(request, s.reaction_values(mapping))
    reactions = s._problem_from_request(request).reactions
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']}
    solvent = {'monoethanolamine': 1., 'water': masses['monoethanolamine']*.7/(.3*masses['water'])}
    items = []
    for row in sources:
        T, P, alpha = row['temperature_K'], row['system_pressure_Pa'], row['alpha_final']
        initial, final = [eq.Problem(T=T, P=P, feed=eq.Amounts({**solvent, 'carbon-dioxide': a}),
            phases=[eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)], reactions=reactions,
            neutral_reference=s._neutral_reference(request)) for a in (0., alpha)]
        items.append(reg.addition_enthalpy(params, initial, final, {'carbon-dioxide': 1.}, alpha,
            T, P, phase='vapor', observed=row['observed_addition_enthalpy_J_per_mol_CO2'],
            form='difference', scale=row['uH_J_per_mol_CO2']))
    return items


def rows_for(spec, mapping, observation_id):
    declaration = indexed(spec['observations'], 'id')[observation_id]
    ids = declaration['ordered_row_ids']
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate observation IDs')
    frozen = indexed(load(declaration['table']), 'target')
    packet = s.load_state_packet(ROOT / spec['packet_path'])['observations']
    targets = indexed([dict(t, state=o) for o in packet for t in o['targets']], 'identity')
    anchors = indexed([json.loads(line) for line in (ROOT / spec['anchors_path']).open()], 'identity')
    sources = indexed(load(spec['heat_rows_path']), 'record_id')
    params = epcsaft.Parameters.from_mapping(mapping)
    template = next(o['request'] for o in packet if o['identity'] == 'Bottinger2008_state_046')
    from verify_temperature_reference import request_at
    heat_request = s.source_feed_request(template, dict(source_key='Amundsen2009', CO2_loading=.11,
        temperature_reported_C=40., MEA_weight_fraction=.30))
    heat_request = request_at(heat_request, 313.15, 101325., liquid_only=True)
    groups, rows = {}, []
    for identity, weight in zip(ids, declaration['weights'], strict=True):
        row = frozen[identity]
        if row['weight'] != weight:
            raise ValueError(f'{identity}: weight mismatch')
        if identity in sources:
            item = heat_items(mapping, params, [sources[identity]], heat_request)[0]
        else:
            target = targets[identity]
            o = target['state']
            if o['identity'] not in groups:
                request = s.corrected_request(o['request'], s.reaction_values(mapping))
                groups[o['identity']] = s._problem_from_request(request, s.anchor_from(anchors[o['identity']]))
            problem = groups[o['identity']]
            output = indexed(o['request']['outputs'], 'identity')[target['prediction_identity']]
            support = next(p.support for p in problem.phases if p.name == output['phase_identity']) or s.COMPONENT_IDS
            if any(c not in (0., 1.) for c in output['coefficients']):
                raise ValueError(f'{identity}: unsupported linear coefficients')
            species = (('bicarbonate-anion', 'carbonate-anion') if identity.startswith(('Matin','Bottinger'))
                and identity.endswith('::HCO3-') else tuple(c for c, v in zip(support, output['coefficients'], strict=True) if v))
            if target['observed'] != row['observed']:
                raise ValueError(f'{identity}: observed mismatch')
            item = reg.observation(params, 'partial_pressure' if row['form']=='LogRatio' else 'mole_fraction',
                problem, observed=row['observed'], form={'LogRatio':'log_ratio','Difference':'difference'}[row['form']],
                mass_basis=False, phase=output['phase_identity'], species=species,
                **({'scale':row['scale']} if row['form']=='Difference' else {}))
        if (item.observed, item.scale, item.form.name) != (row['observed'], row['scale'], row['form']):
            raise ValueError(f'{identity}: observation declaration mismatch')
        rows.append((identity, item, weight))
    return params, rows


def stage6_rows(spec, mapping):
    """Common-149 plus the declared restored, pooled, density and molality-Cp rows."""
    params, common = rows_for(spec, mapping, 'base')
    params, added = stage2_rows(spec, mapping, spec['cases'][0], assessment=True)
    rows = [(dict(id=i, observed=item.observed, scale=item.scale, weight=w,
        form=item.form.name, quantity=item.kind.name), item) for i, item, w in common]
    rows.extend((row, item) for row, item, _ in added)
    template = s.load_state_packet(ROOT/spec['packet_path'])['observations'][0]['request']
    request = s.corrected_request(template, s.reaction_values(mapping))
    reactions = s._problem_from_request(request).reactions
    for row in spec['direct_rows']:
        problem = eq.Problem(T=row['T_K'], P=row['P_Pa'], feed=eq.Amounts(row['analytical_feed']),
            phases=[eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)], reactions=reactions,
            neutral_reference=s._neutral_reference(request), row_tolerance=spec['verification']['raw_residual'])
        item = reg.observation(params, row['quantity'], problem, observed=row['observed'],
            form='difference', scale=row['scale'],
            **(dict(phase='L', mass_basis=True) if row['quantity']=='phase_density' else {}))
        rows.append((dict(row, form='difference'), item))
    assert len(rows)==len(common)+len(added)+len(spec['direct_rows'])
    assert len({r['id'] for r, _ in rows})==len(rows)
    if any(w==0 for d in spec['observations'] for w in d['weights']):
        heat_ids = {r['record_id'] for r in load(spec['heat_rows_path']) if r['record_id'].startswith('vinjarapu')}
        assert len(heat_ids)==8 and {r['id'] for r,_ in rows if r['weight']==0}==heat_ids
        assert {i for d in spec['observations'] for i,w in zip(d['ordered_row_ids'],d['weights'],strict=True) if w==0}==heat_ids
    return params, rows


def predict(mapping, items):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=thermal.record())
    values = [reg.predict(model, item) for item in items]
    if any(v.status.name != 'Available' or not all(math.isfinite(x) for x in (v.value, v.residual)) for v in values):
        raise RuntimeError([(v.status.name, v.message, v.value, v.residual) for v in values
            if v.status.name != 'Available' or not all(math.isfinite(x) for x in (v.value, v.residual))])
    return values


def replay(mapping, rows):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=thermal.record())
    result = []
    for identity, item, weight in rows:
        value = reg.predict(model, item)
        row = dict(target=identity, observed=item.observed, scale=item.scale, weight=weight, form=item.form.name,
            status=value.status.name, message=value.message, requested_tolerance_met=value.requested_tolerance_met,
            stable_root_count=value.stable_root_count)
        if hasattr(value, 'branch'):
            row.update(branch=None if value.branch is None else value.branch.name,
                convergence=None if value.convergence is None else {k:s._jsonable(getattr(value.convergence,k))
                    for k in ('residual','floor','amplification','contraction','iterations','stop')})
        if value.status.name == 'Available':
            r = math.sqrt(weight)*value.residual
            row.update(predicted=value.value, residual=value.residual, weighted_residual=r, cost=.5*r**2)
        result.append(row)
    return result


def replay_summary(values, heat_sources):
    heat_ids = {r['record_id'] for r in heat_sources}
    arcis_ids = {r['record_id'] for r in heat_sources if not r['record_id'].startswith('vinjarapu')}
    common = [r for r in values if r['target'] not in arcis_ids]
    if any(r['status'] != 'Available' for r in values):
        raise RuntimeError('unavailable replay observations; see predictions.json')
    score = dict(cost=math.fsum(r['cost'] for r in common), common149_cost=math.fsum(r['cost'] for r in common), scores={})
    for kind in ('pressure', 'species'):
        rr = [r for r in common if r['target'] not in heat_ids and r['target'].endswith('-pco2') == (kind=='pressure')]
        score['scores'][kind] = dict(n=len(rr), cost=math.fsum(.5*r['weighted_residual']**2 for r in rr),
            AARD_percent=100*math.fsum(abs(r['predicted']/r['observed']-1) for r in rr)/len(rr))
    for name, prefix in (('Vinjarapu','vinjarapu'),('Arcis','arcis')):
        rr = [r for r in values if (r['target'] in arcis_ids) == (name=='Arcis') and r['target'] in heat_ids]
        score[name+'_RMSE_kJ_mol'] = math.sqrt(math.fsum(((r['predicted']-r['observed'])/1000)**2 for r in rr)/len(rr))
    return score


def water_rows(spec, mapping):
    params = epcsaft.Parameters.from_mapping(mapping, components=['water'])
    source, p0 = thermal.CALORICS['components']['water'], thermal.CALORICS['reference_pressure_pa']
    calorics = epcsaft.ThermochemistryRecord(p0, [[epcsaft.IdealInterval(*source['range_k'], True, True,
        epcsaft.IdealCorrelation(epcsaft.IdealShomate(tuple(source['coefficients']), source['formation_enthalpy_j_per_mol']), p0))]])
    model, rows = epcsaft.Pure(params, thermochemistry=calorics), []
    import csv
    for ref in csv.DictReader((ROOT/spec['reference_path']).open()):
        T, P = float(ref['T_K']), float(ref['P_Pa'])
        observed = float(ref['cp_kJ_kg_K'])*1000*spec['molar_mass_kg_mol']
        cp = reg.isobaric_heat_capacity(params,T,P,{'water':1.},phase='liquid',observed=observed,
            form='difference',scale=spec['relative_scales']['cp']*observed)
        problem = eq.Problem(T=T,P=eq.Free(float(ref['psat_Pa'])),feed=eq.Amounts({'water':1.}),
            phases=[eq.Phase('L',kind='liquid',amount=eq.Free(),composition_guess=(1.,)),
                eq.Phase('V',kind='vapor',amount=eq.Pinned(0.),composition_guess=(1.,))],row_tolerance=1e-10)
        rows.append((ref,cp,problem))
    return params, model, calorics, rows


def water_assessment(spec, mapping):
    _, model, _, declared = water_rows(spec,mapping)
    rows = []
    for ref, item, problem in declared:
        row = dict(grid=ref['grid'],T_K=float(ref['T_K']),P_Pa=float(ref['P_Pa']),evaluated=False)
        try:
            prediction = reg.predict(model,item)
            if prediction.status.name != 'Available':
                raise RuntimeError(prediction.message)
            state = model.state(row['T_K'],P=row['P_Pa'],phase='liquid')
            row.update(cp_J_mol_K=prediction.value,rho_kg_m3=state.molar_density*spec['molar_mass_kg_mol'],cp_error_relative=prediction.value/item.observed-1,
                rho_error_relative=state.molar_density*spec['molar_mass_kg_mol']/float(ref['rho_kg_m3'])-1,
                density_termination=s._jsonable(state.density_convergence),dP_drho=state.pressure_density_derivative,enthalpy_ladder=[])
            for step in spec['enthalpy_steps_K']:
                hs = [model.state(row['T_K']+d*step,P=row['P_Pa'],phase='liquid').total_enthalpy for d in (-1,1)]
                fd = (hs[1]-hs[0])/(2*step)
                row['enthalpy_ladder'].append(dict(step_K=step,enthalpies_J_mol=hs,cp_J_mol_K=fd,
                    error_relative=abs(fd/prediction.value-1),subtraction_roundoff_relative=8*max(map(math.ulp,hs))/(2*step*abs(prediction.value))))
            coarse, fine = row['enthalpy_ladder']
            row['cp_verified'] = (max(coarse['error_relative'],fine['error_relative'])<=spec['cp_verification_tolerance']
                and (fine['error_relative']<coarse['error_relative'] or max(coarse['error_relative'],fine['error_relative'])<=max(coarse['subtraction_roundoff_relative'],fine['subtraction_roundoff_relative'])))
            if ref['grid'] != 'atmospheric-controls':
                solved = eq.solve_equilibrium(model,problem)
                row.update(saturation_termination=solved.message,saturation_success=solved.success,
                    saturation_max_abs_residual=max(map(abs,solved.residuals)),saturation_phase_kinds=['liquid','vapor'],
                    saturation_molar_densities=list(solved.molar_densities),saturation_pressure_Pa=solved.pressure)
                sat = model.state(row['T_K'],rho=solved.molar_densities[0])
                row.update(saturated_dP_drho=sat.pressure_density_derivative,saturated_liquid_rho_kg_m3=solved.molar_densities[0]*spec['molar_mass_kg_mol'],
                    saturated_liquid_rho_error_relative=solved.molar_densities[0]*spec['molar_mass_kg_mol']/float(ref['saturated_liquid_rho_kg_m3'])-1,
                    psat_error_relative=solved.pressure/float(ref['psat_Pa'])-1)
            row['evaluated'] = all(math.isfinite(v) for k,v in row.items() if isinstance(v,(int,float)))
        except Exception as error:
            row['failure'] = f'{type(error).__name__}: {error}'
        rows.append(row)
    metrics = []
    for grid in dict.fromkeys(r['grid'] for r in rows):
        for q in ('cp','rho','saturated_liquid_rho','psat'):
            selected = [r for r in rows if r['grid']==grid and (grid!='atmospheric-controls' or q in ('cp','rho'))]
            if not selected:
                continue
            errors = [abs(r[q+'_error_relative']) for r in selected if r['evaluated'] and q+'_error_relative' in r]
            metrics.append(dict(grid=grid,quantity=q,requested_rows=len(selected),evaluated_rows=len(errors),
                mean_absolute_relative_error=math.fsum(errors)/len(errors) if errors else None,maximum_absolute_relative_error=max(errors,default=None)))
    return dict(rows=rows,metrics=metrics)


def stage2_rows(spec, mapping, case, assessment=False):
    declared = load(spec['stage2_rows_path'])[case.get('observations_id',case['id'])]
    mapping = json.loads(json.dumps(mapping))
    for domain in mapping['domains']:
        if domain['domain_id'] in case['neutral_domain_ids']:
            domain.update(case['neutral_domain'])
    params = epcsaft.Parameters.from_mapping(mapping)
    rows, problems = [], {}
    adjacent = {}
    template = s.load_state_packet(ROOT/spec['packet_path'])['observations'][0]['request']
    for row in declared:
        if row['weight'] == 0 and not assessment:
            continue
        group = row['state_id']
        if group not in problems:
            if 'request_id' in row:
                request = s.corrected_request(load(spec['state_requests_path'])[row['request_id']],s.reaction_values(mapping))
                problem = s._problem_from_request(request)
            elif row['quantity'] == 'phase_density':
                problem = s.unloaded_density_problem(mapping,template,row)
            else:
                support = tuple(row['feed'])
                phases = [eq.Phase('L',kind='liquid',support=support,amount=eq.Free(),composition_guess=row['feed']),
                    eq.Phase('V',kind='vapor',support=support,amount=eq.Pinned(0.),composition_guess=row['vapor_guess'])]
                problem = eq.Problem(T=eq.Free(row['T_K']) if row['quantity'] in ('temperature','mole_fraction') else row['T_K'],
                    P=eq.Free(row['P_Pa']) if row['quantity']=='pressure' else row['P_Pa'],
                    feed=eq.Amounts(row['feed']),phases=phases,row_tolerance=1e-10)
            if case.get('kiepe_continuation') and row['id'].startswith('kiepe-'):
                model = epcsaft.Mixture(params,thermochemistry=thermal.record())
                previous = adjacent.get(row['T_K'])
                if previous is not None:
                    problem.P = eq.Free(previous.pressure)
                    for i,phase in enumerate(problem.phases):
                        payload = s._phase_payload(problem,previous,i,len(model.component_ids))
                        phase.composition_guess = dict(zip(payload['support'],payload['mole_fractions'],strict=True))
                        phase.packing_guess = previous.packing_fractions[i]
                state = eq.solve_equilibrium(model,problem)
                if not state.success:
                    raise RuntimeError(f"{row['id']}: continuation unavailable: {state.message}; residuals={list(state.residuals)}")
                adjacent[row['T_K']] = state
            problems[group] = problem
        extra = dict(phase=row['phase'],species=row['species']) if 'request_id' in row else dict(phase='L',mass_basis=True) if row['quantity']=='phase_density' else (
            dict(phase='V',species=['water']) if row['quantity']=='mole_fraction' else {})
        if row['quantity']=='amount_ratio':
            extra.update(denominator_phase=row['phase'],denominator_species=row['denominator_species'])
        item = reg.observation(params,row['quantity'],problems[group],observed=row['observed'],form=row['form'],
            **extra,**(dict(scale=row['scale']) if row['form']=='difference' else {}))
        rows.append((row,item,problems[group]))
    return params,rows


def stage2_native(spec, mapping, case, operation, workers=0, output_path=None):
    params, rows = stage2_rows(spec,mapping,case,assessment=operation=='assessment')
    model = epcsaft.Mixture(params,thermochemistry=thermal.record())
    if operation == 'fit':
        coords = []
        for c in case.get('coordinates',[case.get('coordinate')]):
            factor = c.get('source_to_native_factor',1.)
            kwargs = dict(origin=factor*s.parameter_values(mapping)[c['identity']],scale=abs(factor)*c['scale'],bounds=tuple(sorted(factor*b for b in c['bounds'])))
            coords.append(reg.reaction_coordinate(c['reaction'],c['coefficient'],**kwargs) if 'reaction' in c else
                reg.coordinate(params,[(t['family'],tuple(t['target']) if isinstance(t['target'],list) else t['target'],t.get('factor',1.))
                    for t in c.get('targets',[dict(family=c.get('family','k_ij'),target=c.get('target'))])],**kwargs))
        fitted = reg.fit(params,coords,[r[1] for r in rows],weights=[r[0]['weight'] for r in rows],
            thermochemistry=thermal.record(),controls=reg.FitControls(**spec['controls'],workers=workers,
                maximum_elapsed_time_seconds=case['fit_wall_s']),singular_vectors=True)
        result = {k:s._jsonable(getattr(fitted,k)) for k in ('status','message','usable','initial_cost','final_cost','physical',
            'optimizer','predictions','residuals','weighted_residuals','optimizer_jacobian','physical_jacobian','iterations',
            'iteration_costs','iteration_seconds','trial_failures','residual_evaluations','jacobian_evaluations')}
        result.update(targets=[r[0]['id'] for r in rows],statuses=[v.name for v in fitted.statuses],
            covariance={k:s._jsonable(getattr(fitted.covariance,k)) for k in ('status','assumption','rank','singular_values',
                'physical','optimizer','variance_factor','active_bounds','projected_gradient_norm','left_vectors','right_vectors')},
            failures=[dict(trial=f.trial,observation=f.observation,status=f.status.name,message=f.message,jacobian=f.jacobian) for f in fitted.failures])
        return result
    result, solved = [], {}
    for row,item,problem in rows:
        value = reg.predict(model,item)
        retained = dict(row,status=value.status.name,message=value.message,requested_tolerance_met=value.requested_tolerance_met,
            stable_root_count=value.stable_root_count)
        if value.status.name != 'Available' or not all(math.isfinite(v) for v in (value.value,value.residual)):
            result.append(retained)
            if output_path is not None:
                s.write_json(output_path,result)
            raise RuntimeError(f"{row['id']}: {value.status.name}: {value.message}")
        retained.update(predicted=value.value,error=value.value-item.observed,residual=value.residual,
            weighted_residual=math.sqrt(row['weight'])*value.residual)
        if operation != 'residuals':
            if row['state_id'] not in solved:
                state = eq.solve_equilibrium(model,problem)
                point = eq.compile_problem(model,problem).evaluate(state.coordinates)
                phases = [s._phase_payload(problem,state,i,len(model.component_ids)) for i in range(state.phase_count)]
                evidence = dict(success=state.success,message=state.message,raw_residuals=list(point.values),
                    classified_residuals=list(state.classified_residuals),reduced_hessian_minimum=state.reduced_hessian_minimum,
                    temperature=state.temperature,pressure=state.pressure,phases=phases,
                    dP_drho=[model.state(state.temperature,rho=state.molar_densities[i],x={k:v for k,v in zip(p['support'],p['mole_fractions'],strict=True)}).pressure_density_derivative for i,p in enumerate(phases)])
                solved[row['state_id']] = evidence
            retained['equilibrium'] = solved[row['state_id']]
        result.append(retained)
        if output_path is not None:
            s.write_json(output_path,result)
    return result


def stage2_scores(rows):
    scores = []
    for key in dict.fromkeys((r['quantity'],r['P_Pa'] if r['quantity']!='pressure' else r['T_K']) for r in rows):
        rr = [r for r in rows if (r['quantity'],r['P_Pa'] if r['quantity']!='pressure' else r['T_K'])==key]
        scores.append(dict(quantity=key[0],condition=key[1],n=len(rr),cost=sum(.5*r['weighted_residual']**2 for r in rr),
            MAE=sum(abs(r['error']) for r in rr)/len(rr),maximum_absolute_error=max(abs(r['error']) for r in rr),
            AARD_percent=100*sum(abs(r['error']/r['observed']) for r in rr)/len(rr),
            RMSE=math.sqrt(sum(r['error']**2 for r in rr)/len(rr))))
    return scores


def stage2_balances(spec, mapping, rows):
    system = s.load_state_packet(ROOT/spec['packet_path'])['observations'][0]['request']['reaction_system']
    source_mass = dict(zip(s.COMPONENT_IDS,system['molar_masses_kg_per_mol'],strict=True))
    eos_mass = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']}
    result = []
    for row in rows:
        phases = row['equilibrium']['phases']
        feed = row.get('feed',{'monoethanolamine':1.,'water':source_mass['monoethanolamine']*.7/(.3*source_mass['water'])})
        final = {c:math.fsum(p['amount_mol']*dict(zip(p['support'],p['mole_fractions'],strict=True)).get(c,0.) for p in phases) for c in s.COMPONENT_IDS}
        moiety = [math.fsum(b*(final[c]-feed.get(c,0.)) for c,b in zip(s.COMPONENT_IDS,balance,strict=True)) for balance in system['balance_matrix']]
        charge = math.fsum(q*final[c] for c,q in zip(s.COMPONENT_IDS,system['charges'],strict=True))
        carbon = math.fsum(final[c] for c in ('carbon-dioxide','carbamate-anion','bicarbonate-anion','carbonate-anion'))
        expected_carbon = math.fsum(feed.get(c,0.) for c in ('carbon-dioxide','carbamate-anion','bicarbonate-anion','carbonate-anion'))
        mass_error = math.fsum(source_mass[c]*(final[c]-feed.get(c,0.)) for c in s.COMPONENT_IDS)
        record = dict(target=row['id'],analytical_feed_mol=feed,final_amounts_mol=final,moiety_residuals_mol=moiety,
            charge_residual_mol=charge,carbon_residual_mol=carbon-expected_carbon,source_mass_kg=math.fsum(source_mass[c]*n for c,n in feed.items()),
            source_mass_residual_kg=mass_error,eos_mass_residual_kg=math.fsum(eos_mass[c]*(final[c]-feed.get(c,0.)) for c in s.COMPONENT_IDS))
        if max(map(abs,moiety+[charge,carbon-expected_carbon,mass_error]))>spec['verification']['raw_residual']:
            raise RuntimeError(record)
        if row['quantity']=='phase_density' and carbon!=0.:
            raise RuntimeError('exact-zero-carbon face was not retained')
        result.append(record)
    return result
