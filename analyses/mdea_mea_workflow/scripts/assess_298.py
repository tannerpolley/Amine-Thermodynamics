"""Assess declared endpoints without selecting on comparison errors."""
import copy
import math
import sys
import continue_298 as c
r,s,owner=c.r,c.s,c.owner

def pressure(i):
    group,row,prob,observed=PRESSURES[i]
    result=dict(group=group,row=row,observed_Pa=observed)
    try:
        state=s.eq.solve_equilibrium(s.model,prob)
        result.update(success=state.success,requested_tolerance_met=state.requested_tolerance_met,message=state.message)
        if state.success and state.requested_tolerance_met:
            value=state.pressure*state.phase_mole_fractions(1)[list(s.params.component_ids).index(s.j.C)]
            result.update(predicted_Pa=value,relative_error=value/observed-1)
    except Exception as e:result['message']=str(e)
    return result

def pressure_scores(doc,name):
    global PRESSURES
    s.setup(doc)
    jobs=[]
    for row in s.j.rows('Xiao2018_context.csv'):
        jobs.append(('Xiao',row,s.j.problem(float(row['temperature_K']),101000.,s.j.water(float(row['unloaded_MDEA_mass_fraction'])),float(row['alpha_exp']),True),float(row['p_CO2_kPa'])*1000))
    for row in s.j.rows('Ermatchkov_2006_CO2_MDEA_partial_pressure.csv'):
        m=float(row['m_MDEA_mol_per_kg_H2O'])
        if m*.1191622/(1+m*.1191622)>.49:continue
        jobs.append(('Ermatchkov',row,s.j.problem(float(row['temperature_K']),max(1e5,float(row['p_CO2_kPa'])*1000),1/.01801528/m,float(row['m_CO2_mol_per_kg_H2O'])/m,True),float(row['p_CO2_kPa'])*1000))
    PRESSURES=jobs
    assert len(jobs)==108
    rows=r.pool(pressure,list(range(len(jobs))))
    r.write(name+'/pressure.json',rows)
    if name.endswith('-baseline-278'):
        old=r.read(r.ROOT/f'analyses/mea_parameter_bundle/results/stable-refit-255/evidence/mdea-transfer/{name[:2]}-final-k/pressure.json')
        delta=max(abs(a['predicted_Pa']-b['predicted_Pa'])/max(1.,abs(b['predicted_Pa'])) for a,b in zip(rows,old,strict=True))
        r.write(name+'/pressure-replay.json',dict(max_relative_difference=delta,tolerance=1e-8,passed=delta<=1e-8))
        assert delta<=1e-8
    summary={}
    for group in ('Xiao','Ermatchkov'):
        q=[x for x in rows if x['group']==group]
        ok=[x['relative_error'] for x in q if 'relative_error' in x]
        summary[group]=dict(rows=len(q),available=len(ok),AARD_percent=100*sum(map(abs,ok))/len(q) if len(ok)==len(q) else None,bias_percent=100*sum(ok)/len(q) if len(ok)==len(q) else None,mean_log_ratio=sum(math.log1p(v) for v in ok)/len(q) if len(ok)==len(q) else None,underpredictions=sum(v<0 for v in ok))
    r.write(name+'/pressure-summary.json',summary)
    return summary

def comparisons(doc,name,label):
    summary=s.assess(doc,name,label)
    summary['unscored']=['Derks: unresolved basis/temperature','Zhang: unresolved source/basis restrictions']
    summary['Xiao']='Scored separately in pressure.json, using the retained Xiao context observations'
    r.write(name+'/summary.json',summary)

def apply_phase_domain(name):
    doc=r.read(r.OUT/name/'endpoint.json')
    s.setup(doc)
    cmeta,_=s.comparison_items()
    raw=r.read(r.OUT/name/'phase.json')
    extra=r.read(r.OUT/name/'capped-phase.json')
    excluded=[]
    keep=[]
    for row in raw:
        if row['index'].startswith('comparison:'):
            index=int(row['index'].split(':')[1])
            meta=cmeta[index]
            T=s.comparison_problems[index][-1].T
            if meta['group']=='corrected-Kamps' and 394.94<=T<=395.:
                excluded.append(dict(index=row['index'],T_K=T,meta=meta,native_refusal=row))
                continue
        keep.append(row)
    assert len(excluded)==7
    r.write(name+'/phase-domain-exclusions.json',excluded)
    baseline=name[:2]+'-baseline-278'
    r.write(baseline+'/phase-domain-exclusions.json',[dict(index=x['index'],T_K=x['T_K'],meta=x['meta'],status='Excluded by owner: outside adopted R2 domain; not extrapolated') for x in excluded])
    summary=s.phase_summary(keep+extra)
    previous=r.read(r.OUT/name/'phase-summary.json')
    summary.update(excluded_out_of_domain_states=7,total_retained_phase_records=len(raw)+len(extra),mandatory_Carson_gas_witnesses=previous['mandatory_Carson_gas_witnesses'],binary_mixing_passed=previous['binary_mixing_passed'])
    summary['passed']=summary['passed'] and not summary['mandatory_Carson_gas_witnesses'] and summary['binary_mixing_passed']
    r.write(name+'/phase-summary.json',summary)
    eligibility=r.read(r.OUT/name/'eligibility.json')
    # Verify the retained endpoint predictions and cost before selection.
    rows=r.read(r.OUT/name/'fitted-replay.json')
    fit=r.read(r.OUT/name/'fit.json')
    _,_,weights=s.j.objective(s.params)
    pe=max(abs(x['value']-v)/max(1.,abs(v)) for x,v in zip(rows,fit['predictions'],strict=True))
    re=max(abs(w**.5*x['residual']-v) for w,x,v in zip(weights,rows,fit['weighted_residuals'],strict=True))
    ce=abs(sum(.5*w*x['residual']**2 for w,x in zip(weights,rows,strict=True))/fit['final_cost']-1)
    verification=dict(max_relative_prediction_difference=pe,max_absolute_weighted_residual_difference=re,relative_cost_difference=ce,passed=max(pe,re,ce)<=1e-8)
    r.write(name+'/fit-replay-verification.json',verification)
    eligibility.update(phase=summary,fit_replay=verification,passed=summary['passed'] and verification['passed'] and eligibility['derivatives_passed'] and eligibility['max_relative_element_error']<=1e-8 and eligibility['max_absolute_charge_error_mol']<=1e-8)
    r.write(name+'/eligibility.json',eligibility)
    return eligibility

def endpoint_gate(name):
    if (r.OUT/name/'eligibility.json').exists():return apply_phase_domain(name)
    doc=r.read(r.OUT/name/'endpoint.json')
    replay=c.replay(doc,name)
    # Keep original phase identities, removing exactly the two excluded observations.
    s.j.objective=c.original_objective
    s.setup(doc)
    metadata,_,_=s.fitted_items()
    excluded={i for i,m in enumerate(metadata) if m['group']=='Kuranov' and m['row']['source_row'] in ('28','72')}
    jobs=[(f'fit:{i}:{k}',prob) for i,ps in enumerate(s.problems) if i not in excluded for k,prob in enumerate(ps)]
    s.comparison_items()
    jobs += [(f'comparison:{i}:{k}',prob) for i,ps in enumerate(s.comparison_problems) for k,prob in enumerate(ps) if 293.15<=prob.T<=395]
    # Xiao is an explicit required pressure comparison in the accepted design.
    for i,row in enumerate(s.j.rows('Xiao2018_context.csv')):
        jobs.append((f'Xiao:{i}',s.j.problem(float(row['temperature_K']),101000.,s.j.water(float(row['unloaded_MDEA_mass_fraction'])),float(row['alpha_exp']),True)))
    carson=[]
    for row in s.j.rows('Carson2000_stage1.csv'):
        nw=s.j.water(float(row['MDEA_mass_fraction']));x=float(row['x_CO2'])
        carson.append((x/(1-x)*(1+nw),nw,row))
    alpha,nw,row=max(carson,key=lambda q:q[0])
    heats=[]
    for P in (101325.,265000.):
        initial,final=s.j.problem(298.15,P,nw,0.),s.j.problem(298.15,P,nw,alpha)
        obs=s.reg.addition_enthalpy(s.params,initial,final,{s.j.C:1.},alpha,298.15,P,phase='vapor',observed=float(row['solution_enthalpy_kJ_mol_CO2'])*1000,form='difference',scale=3000.)
        prediction=s.reg.predict(s.model,obs)
        heats.append(dict(P_Pa=P,status=prediction.status.name,message=prediction.message,value=prediction.value if prediction.status.name=='Available' else None))
        jobs.extend([(f'Carson-pressure:{P}:0',initial),(f'Carson-pressure:{P}:1',final)])
    change=abs(heats[1]['value']/heats[0]['value']-1) if all(x['value'] is not None for x in heats) else None
    r.write(name+'/carson-pressure-check.json',dict(row=row,predictions=heats,relative_change=change,passed=change is not None and change<=.005))
    s.precompute_saturations(s.saturation_jobs())
    caps=r.pool(s.phase_saturation,s.saturation_jobs())
    r.write(name+'/saturation-phase-inputs.json',caps)
    for row in caps:
        if row.get('status')=='Available':jobs.append((row['index'],s.j.problem(row['T_K'],row['P_Pa'],s.j.water(row['mass_fraction']),row['alpha_phase'])))
    r.write(name+'/phase-states.json',[dict(index=i,T_K=p.T) for i,p in jobs])
    s.phase_jobs=jobs
    phases=r.pool(s.phase,list(range(len(jobs))))
    phases += [dict(index=x['index'],requested_tolerance_met=False,error=x['status']) for x in caps if x.get('status')!='Available']
    r.write(name+'/phase.json',phases)
    summary=s.phase_summary(phases)
    r.write(name+'/phase-summary.json',summary)
    try:
        summary=owner.saturation_gate(name)
    except Exception as error:
        summary.update(passed=False,capped_phase_refusal=str(error))
        r.write(name+'/phase-summary.json',summary)
    # Existing binary convex-hull grid, using the refitted linear law at each temperature.
    fitted=r.read(r.OUT/name/'fit.json')['physical']
    values=fitted[:2]
    scans=[s.j.k.d.mixing_scan(values[0]+values[1]*(T-313.15),T) for T in (293.15,313.15,353.15,393.15)]
    r.write(name+'/binary-mixing-scans.json',scans)
    mandatory=[x for x in phases if x['index'].startswith('Carson-pressure:') or (x['index'].startswith('fit:') and metadata[int(x['index'].split(':')[1])]['group']=='Carson')]
    summary['mandatory_Carson_gas_witnesses']=[x['index'] for x in mandatory if x.get('density_gate',{}).get('gas_evolution')]
    summary['passed']=summary['passed'] and not summary['mandatory_Carson_gas_witnesses']
    summary['binary_mixing_passed']=all(x['miscible'] for x in scans)
    summary['passed']=summary['passed'] and summary['binary_mixing_passed']
    r.write(name+'/phase-summary.json',summary)
    r.write(name+'/fitted-phase.json',[dict(x,index=x['index'][4:]) for x in phases if x['index'].startswith('fit:')])
    s.numerical(name)
    derivative=r.read(r.OUT/name/'derivatives.json')
    balance=r.read(r.OUT/name/'balances.json')
    s.j.objective=c.objective
    passed=replay['passed'] and summary['passed'] and derivative['passed'] and balance['max_relative_element_error']<=1e-8 and balance['max_absolute_charge_error_mol']<=1e-8
    result=dict(passed=passed,phase=summary,derivatives_passed=derivative['passed'],max_relative_element_error=balance['max_relative_element_error'],max_absolute_charge_error_mol=balance['max_absolute_charge_error_mol'])
    r.write(name+'/eligibility.json',result)
    print(name,result,flush=True)
    return apply_phase_domain(name)

if __name__=='__main__':
    r.identities()
    next(x for x in s.j.d.REACTIONS if x.name=='R2').correlation=s.eq.ReactionLogPolynomial(**r.read(r.ADOPTION/'shared-R2.json'))
    attempts=r.read(r.OUT/'attempts.json')
    eligibility={}
    for a in attempts:
        name=a['name']
        if a['usable'] and a['status']=='converged' and a['rank']==9:
            eligibility[name]=endpoint_gate(name)
        else:
            eligibility[name]=dict(passed=False,reason='Nonconverged, unusable or rank deficient',status=a['status'],rank=a['rank'])
    r.write('eligibility.json',eligibility)
    selection={}
    for label in ('A3','B1'):
        eligible=[a for a in attempts if a['representation']==label and eligibility[a['name']]['passed']]
        if eligible:
            a=min(eligible,key=lambda a:a['cost'])
            selection[label]=dict(name=a['name'],cost=a['cost'],endpoint_sha256=r.sha(r.OUT/a['name']/'endpoint.json'))
    r.write('selection.json',selection)
    r.write('selection-identity.json',dict(sha256=r.sha(r.OUT/'selection.json'),selection=selection))
    # Selection is frozen before any pressure comparison statistic is evaluated.
    scores={}
    for label in ('A3','B1'):
        name=label+'-baseline-278'
        original=next(x for x in s.j.d.REACTIONS if x.name=='R2').correlation
        next(x for x in s.j.d.REACTIONS if x.name=='R2').correlation=c.s.eq.ReactionLogPolynomial(**r.read(r.OUT/(label+'-historical/R2.json')))
        scores[name]=pressure_scores(r.read(r.OUT/name/'parameters.json'),name)
        if label in selection:comparisons(r.read(r.OUT/name/'parameters.json'),name,label)
        next(x for x in s.j.d.REACTIONS if x.name=='R2').correlation=original
        name=label+'-substitution-278'
        scores[name]=pressure_scores(r.read(r.OUT/name/'parameters.json'),name)
        comparisons(r.read(r.OUT/name/'parameters.json'),name,label)
        if label in selection:
            name=selection[label]['name']
            scores[name]=pressure_scores(r.read(r.OUT/name/'endpoint.json'),name)
            comparisons(r.read(r.OUT/name/'endpoint.json'),name,label)
            for a in attempts:
                if a['representation']==label and eligibility[a['name']]['passed'] and a['name']!=name and a['cost']<=1.01*selection[label]['cost']:
                    scores[a['name']]=pressure_scores(r.read(r.OUT/a['name']/'endpoint.json'),a['name'])
    r.write('pressure-scores.json',scores)
    gates=dict(F1=dict(status='passed on owner rebase',evidence='F1.json'),F2={},F3={},F4=dict(eligibility=eligibility),F5=dict(status='declared bounds, weights, shared law and search grid preserved',parameter_adoption=False))
    for label in ('A3','B1'):
        if label not in selection:
            for gate in ('F2','F3'):
                gates[gate][label]=dict(status='unavailable: no eligible converged endpoint; comparison errors withheld')
            continue
        name=selection[label]['name']
        base=label+'-baseline-278'
        gates['F2'][label]={g:dict(baseline=scores[base][g],refit=scores[name][g],passed=scores[name][g]['AARD_percent'] is not None and scores[name][g]['AARD_percent']<=scores[base][g]['AARD_percent']+1e-6,older_24_2_percent_pass=scores[name][g]['AARD_percent']<=24.2 if g=='Ermatchkov' and scores[name][g]['AARD_percent'] is not None else None) for g in ('Xiao','Ermatchkov')}
        bg=r.read(r.OUT/base/'replay-summary.json')['groups']
        fg=r.read(r.OUT/name/'replay-summary.json')['groups']
        groups={g:dict(baseline_RMS=bg[g]['scaled_RMS'],refit_RMS=fg[g]['scaled_RMS'],ratio=fg[g]['scaled_RMS']/bg[g]['scaled_RMS'],passed=fg[g]['scaled_RMS']<=1.1*bg[g]['scaled_RMS']) for g in bg}
        baseline_comparison=r.read(r.OUT/base/'comparisons.json')
        fitted_comparison=r.read(r.OUT/name/'comparisons.json')
        heats=[]
        for before,after in zip(baseline_comparison,fitted_comparison,strict=True):
            if before['group'] not in ('Zheng','Merkley-outside','Merkley-half-loading'):continue
            assert before['row']==after['row']
            obs=before['observed']
            available='predicted' in before and 'predicted' in after
            heats.append(dict(group=before['group'],row=before['row'],observed_J_mol=obs,baseline=before,refit=after,passed=abs(after['predicted']-obs)<=abs(before['predicted']-obs)+max(3000.,.05*abs(obs)) if available else False if 'predicted' in before else None))
        equal=[dict(start=a['name'],cost=a['cost'],Ermatchkov_AARD_difference_points=abs(scores[a['name']]['Ermatchkov']['AARD_percent']-scores[name]['Ermatchkov']['AARD_percent'])) for a in attempts if a['representation']==label and a['name'] in scores and a['cost']<=1.01*selection[label]['cost']]
        gates['F4'][label]=dict(equal_cost_starts=equal,non_identification_warning=any(x['Ermatchkov_AARD_difference_points']>=2 for x in equal))
        gates['F3'][label]=dict(groups=groups,outside_fit_heats=heats,Carson_pressure=r.read(r.OUT/name/'carson-pressure-check.json'))
    for label in selection:
        gates['F2'][label]['passed']=all(gates['F2'][label][g]['passed'] for g in ('Xiao','Ermatchkov'))
        result=gates['F3'][label]
        result['passed']=all(x['passed'] for x in result['groups'].values()) and not any(x['passed'] is False for x in result['outside_fit_heats']) and result['Carson_pressure']['passed']
    gates['F4']['passed']=len(selection)==2 and all(eligibility[x['name']]['passed'] for x in selection.values()) and not any(gates['F4'][label]['non_identification_warning'] for label in selection)
    gates['F5']['disposition']='Transfer penalty under this model, objective, bounds and declared starts' if len(selection)==2 and any(not gates[g][label]['passed'] for g in ('F2','F3') for label in selection) else 'No remaining recovery failure established' if len(selection)==2 else 'No admissible endpoint; no physical transfer penalty assigned'
    r.write('gates.json',gates)
