"""Issue 172: retained-fit replay, identification, gas witness and comparisons."""
import json
import hashlib
import math
from pathlib import Path
import subprocess
import sys

import run as c
import family as f
import numpy as np
from reduce_dielectric import measured_provenance


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
        optimizer_condition=float(singular[0]/singular[-1]) if rank==len(ids) else None,
        column_normalized_condition=float(normalized[0]/normalized[-1]) if rank==len(ids) else None,
        free_coordinates=[ids[i] for i in free],free_rank=free_rank,free_singular_values=sv.tolist(),
        column_normalized_singular_values=normalized.tolist(),physical_jacobian=physical.tolist(),
        gradient_optimizer=(J.T@np.array(raw['weighted_residuals'])).tolist(),
        active_bounds=[ids[i] for i in active],conditional_scale_covariance=covariance,conditional_correlations=correlation,
        conditional_scale_errors={identity:None if i not in free or covariance is None else math.sqrt(covariance[free.index(i)][free.index(i)]) for i,identity in enumerate(ids)},
        covariance_interpretation='Free-coordinate local scale sensitivity conditional on held bounds; bound-coordinate uncertainty unavailable; no confidence interval or convergence claim for limited fits',
        cutoff='1e-14 s_max in optimizer coordinates',
        scope='Conditional on dielectric branch, chemistry, water and residual weights; not independently measured ion sizes')


def falsifier(mapping,directory):
    s = f.screen
    s.OUT = directory
    model = s.mixture(mapping)
    off = model if next(x for x in mapping['model_families'] if x['kind']=='electrolyte')['choice']=='fully-dissociated-debye-huckel' else s.shell_off(mapping)
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
                density_branch=c.s._jsonable(state.density_branch),pressure_density_derivative=state.pressure_density_derivative,
                **s.contribution(model,off,T,float(witness['N_L']),x,state.molar_density)))
        except Exception as error: roots.append(dict(selector=selector,failure=f'{type(error).__name__}: {error}'))
    scan = [s.contribution(model,off,T,float(witness['N_L']),x,rho) for rho in (1e-6,1e-3,.01,.1,1.4,10.,100.)]
    physical = [dict(phase=phase,**s.contribution(model,off,T,amount,list(solved.mole_fractions[offset:offset+width])+[0.]*(9-width),rho))
        for phase,amount,rho,offset,width in zip(('L','V'),solved.amounts,solved.molar_densities,(0,9),(9,3),strict=True)] if solved.success else []
    removed = solved.success and all(r.get('stable_root_count')==1 for r in roots) and roots[0].get('molar_density_mol_m3')==roots[1].get('molar_density_mol_m3')
    result = dict(gas_root_absent=removed,roots=roots,old_witness_G_over_RT=old.objective,
        old_witness_rows=list(old.values),new_physical_G_over_RT=solved.objective if solved.success else None,
        witness_delta_G_over_RT=old.objective-solved.objective if solved.success else None,
        interpretation='One native stable density root for retained gas composition; selectors coincide. Old packing witness is not a converged state. No global stability claim.',
        finite_shell_limit='Fixed ionic-region permittivity leaves finite Born shell as bulk permittivity tends to one',
        low_density_endpoints=[scan[0],scan[-1]],
        low_density_interpretation='Native fixed-composition scan; epsilon tends to one and bulk Born tends to zero. Shell finiteness is disclosed, not an extra gate.')
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
            candidates,attempts = [],[]
            for letter in ('A','B'):
                path = c.OUT/branch/f'{problem}-{letter}'
                raw = json.loads((path/'native-fit.json').read_text())
                c.write(path/'identification.json',identification(raw))
                attempts.append(dict(start=letter,**{k:raw[k] for k in ('status','message','usable','final_cost','iterations','wall_s','trial_failures')},
                    physical=raw['physical'],active_bounds=raw['active_bounds'],eligible=(path/'parameters.json').exists()))
                record_path = path/'parameters.json'
                if raw['usable'] and not record_path.exists():
                    record_path = path/'endpoint-parameters.json'
                    endpoint = c.s.with_parameter_values(json.loads((path/'start-parameters.json').read_text()),dict(zip(raw['coordinates'],raw['physical'],strict=True)))
                    endpoint['purpose'] = 'Budget-limited endpoint replay only; not a complete converged fit or adoption candidate.'
                    c.write(record_path,endpoint)
                if record_path.exists():
                    original = json.loads(record_path.read_text())
                    corrected = measured_provenance(original)
                    for node in c.s._identified(corrected):
                        if node['identity'] in raw['coordinates']:
                            node['source_sha256'] = 'sha256:'+hashlib.sha256((path/'native-fit.json').read_bytes()).hexdigest()
                            node['provenance'].update(source_id='permittivity-refit-172',locator=f'{branch}/{problem}-{letter}/native-fit.json: physical vector matched by coordinates; {raw["status"]}')
                    assert c.s.parameter_values(original)==c.s.parameter_values(corrected) and c.s.reaction_values(original)==c.s.reaction_values(corrected)
                    corrected['document_id'] = f'mea-permittivity-refit-172-{branch}-{problem}-{letter}'
                    c.write(record_path,corrected)
                    command = [sys.executable,str(c.OUT/'run.py'),'evaluate',str(record_path),str(path)]
                    subprocess.run(command,check=True)
                    replay = json.loads((path/'replay.json').read_text())[:len(raw['targets'])]
                    assert [r['target'] for r in replay]==raw['targets']
                    replay_check = dict(relative_cost=abs(sum(r['cost'] for r in replay)/raw['final_cost']-1),
                        max_abs_weighted_residual=max(abs(r['weighted_residual']-v) for r,v in zip(replay,raw['weighted_residuals'],strict=True)))
                    c.write(path/'replay-comparison.json',replay_check)
                    assert replay_check['relative_cost']<=1e-8 and replay_check['max_abs_weighted_residual']<=1e-8
                    if attempts[-1]['eligible']: candidates.append((raw['final_cost'],letter,path,raw))
            if not candidates:
                summaries.append(dict(branch=branch,problem=problem,attempts=attempts,failure='No complete converged fit'))
                continue
            _,letter,directory,raw = min(candidates)
            dispersion = None if len(candidates)!=2 else {i:abs(a-b) for i,a,b in zip(raw['coordinates'],candidates[0][3]['physical'],candidates[1][3]['physical'],strict=True)}
            row = dict(branch=branch,problem=problem,selected_start=letter,complete_starts=len(candidates),
                attempts=attempts,all_starts_relative_cost_difference=abs(attempts[0]['final_cost']-attempts[1]['final_cost'])/max(a['final_cost'] for a in attempts),
                all_starts_coordinate_dispersion={i:abs(a-b) for i,a,b in zip(raw['coordinates'],attempts[0]['physical'],attempts[1]['physical'],strict=True)},
                starts_relative_cost_difference=None if len(candidates)!=2 else abs(candidates[0][0]-candidates[1][0])/max(x[0] for x in candidates),
                coordinate_dispersion=dispersion,iterations=raw['iterations'],wall_s=raw['wall_s'],
                fitted_coordinates=dict(zip(raw['coordinates'],raw['physical'],strict=True)))
            row['complete_starts_agree_1e_6'] = None if len(candidates)!=2 else row['starts_relative_cost_difference']<=1e-6
            mapping = json.loads((directory/'parameters.json').read_text())
            row['parameters'] = str(directory/'parameters.json')
            row['replay'] = json.loads((directory/'replay-comparison.json').read_text())
            row.update(json.loads((directory/'summary.json').read_text()))
            row['falsifier'] = falsifier(mapping,directory)
            if problem=='F1':
                row['Hajj'] = hajj(mapping,directory)
            summaries.append(row)
            c.write(c.OUT/'comparison.json',summaries)
            print('REPLAYED',branch,problem,flush=True)
    controls = [(c.s.parameter_mapping(),c.OUT/'baseline')]
    for branch,pair in zip(('smaller-dV','larger-dV'),json.loads((c.OUT/'dielectric/reduction.json').read_text())['branches'],strict=True):
        mapping = measured_provenance(c.declaration(c.s.parameter_mapping(),pair))
        c.write(c.OUT/branch/'unrefitted/parameters.json',mapping)
        controls.append((mapping,c.OUT/branch/'unrefitted'))
    for mapping,directory in controls: falsifier(mapping,directory)
    f.families(controls+[(json.loads(Path(row['parameters']).read_text()),Path(row['parameters']).parent)
        for row in summaries if 'parameters' in row])
    for row in summaries:
        if 'parameters' in row:
            directory = Path(row['parameters']).parent
            row['family'] = json.loads((directory/'family-counts.json').read_text())
            if row['problem']=='F1':
                row['gates'] = dict(cost=row['common149_cost']<=35.26,pressure=row['scores']['pressure']['AARD_percent']<=15.81,
                    species=row['scores']['species']['AARD_percent']<=9.89,Vinjarapu=row['Vinjarapu_RMSE_kJ_mol']<=3.13,
                    Arcis=row['Arcis_RMSE_kJ_mol']<=9.36,gas_root=row['falsifier']['gas_root_absent'],
                    family=row['family']['unresolved']==row['family']['failed']==0)
            print('ASSESSED',row['branch'],row['problem'],row.get('gates',{}),flush=True)
    c.write(c.OUT/'comparison.json',summaries)


if __name__=='__main__': main()
