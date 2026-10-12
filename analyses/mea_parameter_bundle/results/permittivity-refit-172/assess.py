"""Issue 172: retained-fit replay, identification, gas witness and comparisons."""
import json
import math
from pathlib import Path
import subprocess
import sys

import run as c
import family as f
import numpy as np


def identification(raw):
    ids,scales = raw['coordinates'],np.array(raw['scales'])
    J = np.array(raw['optimizer_jacobian']).reshape(len(raw['targets']),len(ids))
    physical = np.array(raw['physical_jacobian']).reshape(J.shape)
    active = raw['active_bounds']
    free = [i for i in range(len(ids)) if i not in active]
    singular = np.linalg.svd(J,compute_uv=False)
    norms = np.linalg.norm(J,axis=0)
    normalized = np.linalg.svd(np.divide(J,norms,out=np.zeros_like(J),where=norms>0),compute_uv=False)
    _,sv,V = np.linalg.svd(J[:,free],full_matrices=False)
    rank = int(np.sum(singular>1e-14*singular[0]))
    free_rank = int(np.sum(sv>1e-14*sv[0])) if len(sv) else 0
    covariance,correlation = None,None
    if free_rank==len(free) and free:
        covariance = (V.T/(sv**2))@V
        sd = np.sqrt(np.diag(covariance))
        correlation = (covariance/(sd[:,None]*sd[None,:])).tolist()
        covariance = (scales[free,None]*covariance*scales[None,free]).tolist()
    return dict(coordinates=ids,native_covariance=raw['covariance'],rank=rank,singular_values=singular.tolist(),
        free_coordinates=[ids[i] for i in free],free_rank=free_rank,free_singular_values=sv.tolist(),
        column_normalized_singular_values=normalized.tolist(),physical_jacobian=physical.tolist(),
        gradient_optimizer=(J.T@np.array(raw['weighted_residuals'])).tolist(),
        active_bounds=[ids[i] for i in active],conditional_scale_covariance=covariance,conditional_correlations=correlation,
        cutoff='1e-14 s_max in optimizer coordinates',
        scope='Conditional on dielectric branch, chemistry, water and residual weights; not independently measured ion sizes')


def falsifier(mapping,directory):
    s = f.screen
    s.OUT = directory
    model,off = s.mixture(mapping),s.shell_off(mapping)
    params,groups,_ = c.h.d.rows_for(mapping,'11')
    request = c.s.corrected_request(groups[0][0]['request'],c.s.reaction_values(mapping))
    s.CURRENT_REACTIONS = c.s._problem_from_request(request).reactions
    s.REQUEST = request
    T,P,loading = 318.15,3699.0803800848512,.25557798094241313
    p = s.flash_problem('current',loading,T,P)
    solved = c.h.eq.solve_equilibrium(model,p)
    c.write(directory/'falsifier-solve.json',f.payload(solved))
    compiled = c.h.eq.compile_problem(model,p)
    witness = json.loads((c.OUT/'inputs/falsifier-gas.json').read_text())['row']
    labels = ('CO2','MEA','water','MEAH','carbamate','HCO3','CO3','H3O','OH')
    x = [float(witness['xL_'+v]) for v in labels]
    x = [v/sum(x) for v in x]
    point = compiled.generic_point()
    point[:16] = [*[math.log(float(witness['xL_'+v])) for v in labels],float(witness['N_L']),float(witness['lneta_L']),
        *[math.log(float(witness['yV_'+v])) for v in labels[:3]],max(0.,float(witness['N_V'])),float(witness['lneta_V'])]
    old = compiled.evaluate(point)
    roots = []
    for selector in ('vapor','liquid'):
        try:
            state = model.state(T,P=P,x=x,phase=selector)
            roots.append(dict(selector=selector,stable_root_count=state.stable_root_count,
                **s.contribution(model,off,T,float(witness['N_L']),x,state.molar_density)))
        except Exception as error: roots.append(dict(selector=selector,failure=f'{type(error).__name__}: {error}'))
    scan = [s.contribution(model,off,T,float(witness['N_L']),x,rho) for rho in (1e-6,1e-3,.01,.1,1.4,10.,100.)]
    physical = [dict(phase=phase,**s.contribution(model,off,T,amount,list(solved.mole_fractions[offset:offset+width])+[0.]*(9-width),rho))
        for phase,amount,rho,offset,width in zip(('L','V'),solved.amounts,solved.molar_densities,(0,9),(9,3),strict=True)] if solved.success else []
    removed = solved.success and all(r.get('stable_root_count')==1 for r in roots) and roots[0].get('molar_density_mol_m3')==roots[1].get('molar_density_mol_m3') and old.objective>solved.objective
    result = dict(gas_root_absent=removed,roots=roots,old_witness_G_over_RT=old.objective,
        old_witness_rows=list(old.values),new_physical_G_over_RT=solved.objective if solved.success else None,
        witness_delta_G_over_RT=old.objective-solved.objective if solved.success else None,
        interpretation='One native stable density root for retained gas composition; selectors coincide. Old packing witness is not a converged state. No global stability claim.',
        finite_shell_limit='Fixed ionic-region permittivity leaves finite Born shell as bulk permittivity tends to one')
    c.write(directory/'falsifier.json',result)
    c.table(directory/'low-density.csv',scan)
    if physical: c.table(directory/'falsifier-contributions.csv',physical)
    return result


def hajj(mapping,directory):
    model = f.screen.mixture(mapping)
    masses = {x['component_id']:x['fixed']['molar_mass']['value']['magnitude'] for x in mapping['components']}
    params,groups,_ = c.h.d.rows_for(mapping,'11')
    request = c.s.corrected_request(groups[0][0]['request'],c.s.reaction_values(mapping))
    reactions = c.s._problem_from_request(request).reactions
    loaded = {.22:[71.3,70.1,67.8,69.7,66.8,63.6,60.1],.33:[80.5,80.9,79.5,76.6,72.4,68.6,63.4],
        .44:[89.6,90.6,88.3,84.1,79.3,74.7,68.8],.55:[92.7,92.7,82.7,84.2,87.2,75.2,72.4]}
    rows = []
    for loading,epsilons in loaded.items():
        for i,eps in enumerate(epsilons):
            T = 293.15+10*i
            p = c.h.eq.Problem(T=T,P=101325.,feed=c.h.eq.Amounts({'monoethanolamine':1.,
                'water':masses['monoethanolamine']*.7/(.3*masses['water']),'carbon-dioxide':loading}),
                phases=[c.h.eq.Phase('L',kind='liquid')],reactions=reactions,neutral_reference=c.s._neutral_reference(request))
            r = c.h.eq.solve_equilibrium(model,p)
            row = dict(temperature_K=T,loading=loading,observed_epsilon=eps,pressure_assumption_Pa=101325.,
                success=r.success,message=r.message,source_locator=f'Hajj2024 Table1 p9 alpha={loading} T_C={20+10*i}',
                source_sha256='ffbaa92067f598d8b808a5becc934e62d76748918be57c2de28d59f9af86e30f')
            if r.success:
                state = model.state(T,rho=r.molar_densities[0],x=r.mole_fractions[:9])
                row.update(native_density_mol_m3=state.molar_density,predicted_epsilon=state.bulk_relative_permittivity,
                    residual_epsilon=state.bulk_relative_permittivity-eps,liquid=f.payload(r))
            rows.append(row)
    c.write(directory/'hajj.json',rows)
    c.table(directory/'hajj.csv',[{k:v for k,v in row.items() if k!='liquid'} for row in rows])
    return dict(available=sum(r['success'] for r in rows),n=28,
        RMSE_epsilon=math.sqrt(sum(r['residual_epsilon']**2 for r in rows if r['success'])/sum(r['success'] for r in rows)),
        warning='Hajj section 3.3.1: static-limit extrapolation uncertain, particularly cold/high loading; comparison only')


def main():
    summaries = []
    for branch in ('smaller-dV','larger-dV'):
        for problem in (f'F{i}' for i in range(1,7)):
            candidates = []
            for letter in ('A','B'):
                path = c.OUT/branch/f'{problem}-{letter}'
                if (path/'parameters.json').exists():
                    raw = json.loads((path/'native-fit.json').read_text())
                    candidates.append((raw['final_cost'],letter,path,raw))
            if not candidates:
                summaries.append(dict(branch=branch,problem=problem,failure='No complete converged fit'))
                continue
            _,letter,directory,raw = min(candidates)
            dispersion = None if len(candidates)!=2 else {i:abs(a-b) for i,a,b in zip(raw['coordinates'],candidates[0][3]['physical'],candidates[1][3]['physical'],strict=True)}
            row = dict(branch=branch,problem=problem,selected_start=letter,complete_starts=len(candidates),
                starts_relative_cost_difference=None if len(candidates)!=2 else abs(candidates[0][0]-candidates[1][0])/max(x[0] for x in candidates),
                coordinate_dispersion=dispersion,iterations=raw['iterations'],wall_s=raw['wall_s'],
                fitted_coordinates=dict(zip(raw['coordinates'],raw['physical'],strict=True)))
            mapping = json.loads((directory/'parameters.json').read_text())
            command = [sys.executable,str(c.OUT/'run.py'),'evaluate',str(directory/'parameters.json'),str(directory)]
            subprocess.run(command,check=True)
            replay = json.loads((directory/'replay.json').read_text())[:len(raw['targets'])]
            assert [r['target'] for r in replay]==raw['targets']
            row['replay_relative_cost'] = abs(sum(r['cost'] for r in replay)/raw['final_cost']-1)
            row['replay_max_abs_weighted_residual'] = max(abs(r['weighted_residual']-v) for r,v in zip(replay,raw['weighted_residuals'],strict=True))
            c.write(directory/'replay-comparison.json',row)
            assert row['replay_relative_cost']<=1e-8 and row['replay_max_abs_weighted_residual']<=1e-8
            row.update(json.loads((directory/'summary.json').read_text()))
            c.write(directory/'identification.json',identification(raw))
            row['falsifier'] = falsifier(mapping,directory)
            family_command = [sys.executable,str(c.OUT/'family.py'),str(directory/'parameters.json'),str(directory)]
            subprocess.run(family_command,check=True)
            row['family'] = json.loads((directory/'family-counts.json').read_text())
            if problem=='F1':
                row['Hajj'] = hajj(mapping,directory)
                row['gates'] = dict(cost=row['common149_cost']<=35.26,pressure=row['scores']['pressure']['AARD_percent']<=15.81,
                    species=row['scores']['species']['AARD_percent']<=9.89,Vinjarapu=row['Vinjarapu_RMSE_kJ_mol']<=3.13,
                    Arcis=row['Arcis_RMSE_kJ_mol']<=9.36,gas_root=row['falsifier']['gas_root_absent'],
                    family=row['family']['unresolved']==row['family']['failed']==0,complete_starts=len(candidates)==2)
            summaries.append(row)
            c.write(c.OUT/'comparison.json',summaries)
            print('ASSESSED',branch,problem,row.get('gates',{}),flush=True)


if __name__=='__main__': main()
