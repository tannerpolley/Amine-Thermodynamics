"""Assess frozen density-gated MDEA endpoints, then declared ten-coordinate follow-ups."""
import importlib.util
import sys
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('capped',AN/'scripts/refit_capped.py')
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
s,n=r.s,r.n

def stats(records):
    groups={}
    for g in dict.fromkeys(q['group'] for q in records):
        rows=[q for q in records if q['group']==g];ok=[q for q in rows if q.get('relative_error') is not None]
        groups[g]=dict(rows=len(rows),available=len(ok),AARD_percent=100*s.np.mean([abs(q['relative_error']) for q in ok]) if len(ok)==len(rows) and ok else None)
    return groups

def fitted(doc,folder,fit):
    s.setup(doc);meta,items,weights=s.fitted_items()
    s.items,s.meta,s.fit=items,meta,fit
    rows=s.poolmap(s.replay,list(range(len(items))))
    n.write(f'{folder}/replay.json',rows)
    assert all(q['prediction']['status']=='Available' and q['relative_error']<=1e-8 for q in rows)
    summary=stats([dict(q,relative_error=q['prediction']['value']/q['observed']-1) for q in rows])
    kim=[q for q in rows if q['group']=='Kim']
    logs=[s.np.log(q['prediction']['value']/q['observed']) for q in kim]
    summary['Kim'].update(mean_absolute_log_ratio=float(s.np.mean(s.np.abs(logs))),root_mean_square_log_ratio=float(s.np.sqrt(s.np.mean(s.np.square(logs)))))
    n.write(f'{folder}/fitted-statistics.json',summary)
    return summary

def hsieh(doc,folder):
    s.setup(doc);rows=[]
    for old in s.load('results/dielectric/rows.json'):
        state=s.model.state(old['T'],P=101325.,x={s.j.M:old['x'],s.j.W:1-old['x']},phase='liquid')
        rows.append(dict(old,predicted=state.bulk_relative_permittivity,relative_error=state.bulk_relative_permittivity/old['observed']-1))
    n.write(f'{folder}/Hsieh.json',rows)
    return dict(rows=len(rows),AARD_percent=100*sum(abs(q['relative_error']) for q in rows)/len(rows))

def truncations(doc,folder):
    s.setup(doc);rows=[]
    loading={(q['temperature_K'],q['MDEA_mass_percent']):float(q['alpha_LP_mol_CO2_per_mol_MDEA']) for q in s.j.rows('Merkley1987_loading_points.csv')}
    for row in s.j.rows('Merkley1987_stage1.csv'):
        T=float(row['temperature_K']);P=float(row['proposed_pressure_kPa'])*1000;lp=loading[(row['temperature_K'],row['MDEA_mass_percent'])]
        rec=dict(row,source_loading=lp,pressure_Pa=P)
        if not 293.15<=T<=395:rows.append(dict(rec,status='outside frozen reaction domain'));continue
        sat=s.saturation(dict(row,pressure_MPa=str(P/1e6)))
        rec.update(saturation=sat)
        if sat['status']!='Available' or sat['sign_changes']!=1:raise RuntimeError('Owner decision: saturation refused '+str(rec))
        rec.update(selected_loading=min(lp,sat['alpha_sat']),truncation=max(0.,lp-sat['alpha_sat']))
        rows.append(rec)
    n.write(f'{folder}/Merkley-truncations.json',rows)
    return [q for q in rows if q.get('truncation',0.)>0]

original_coordinates=s.j.coordinates

def follow_coordinates(params,doc,variant):
    coords,decl=original_coordinates(params,doc,variant)
    target=('bicarbonate-anion',s.j.W) if FOLLOW=='bicarbonate' else (s.j.M,s.j.C)
    pair=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}==set(target))
    origin=next(c['value']['magnitude'] for c in pair['coefficients'] if c['family']=='k_ij')
    q=dict(targets=[('k_ij',target,1.)],origin=origin,scale=.01,bounds=(-.5,1.) if FOLLOW=='bicarbonate' else (-.5,.5))
    decl.append(q);coords.append(s.reg.coordinate(params,q['targets'],origin=origin,scale=.01,bounds=q['bounds']))
    return coords,decl

if __name__=='__main__':
    import subprocess,json
    selected=s.load(f'{r.OUT}/selection.json')
    retained=subprocess.check_output(['git','show',f'HEAD:analyses/mdea_mea_workflow/{r.OUT}/selection.json'],text=True)
    assert json.loads(retained)==selected,'Selection must be committed before outside-fit statistics'
    for variant,choice in selected.items():
        label=choice['label'];doc,fit=r.endpoint(label)
        summary=fitted(doc,label,fit)
        comparison=s.assess(doc,label,'Density-gated capped endpoint; conditional transfer assessment')
        comparison['Hsieh']=hsieh(doc,label);comparison['fitted']=summary
        comparison['Wangler_fitted']=stats(s.load(f'{r.OUT}/{label}/wangler-fitted-heat-cp.json'))
        comparison['Wangler_Cp_delta_points']=comparison['Wangler_fitted']['Cp']['AARD_percent']-summary['Cp']['AARD_percent']
        comparison['Ermatchkov_pass']=comparison['Ermatchkov88']['AARD_percent']<=24.2
        comparison['Merkley_truncations']=truncations(doc,label)
        # Endpoint Jacobian and local weak-direction profiles precede follow-up fits.
        s.sensitivity(label)
        phase=n.load(f'{r.OUT}/{label}/phase.json')
        n.write(f'{label}/fitted-phase.json',[dict(q,index=q['index'].removeprefix('fit:')) for q in phase if q['index'].startswith('fit:')])
        s.numerical(label)
        n.write(f'{label}/assessment.json',comparison)
        for FOLLOW in ('bicarbonate','control'):
            s.j.coordinates=follow_coordinates
            s.setup(doc);coords,decl=follow_coordinates(s.params,doc,variant)
            folder=f'{label}/followup-{FOLLOW}'
            candidate,result=s.fit_document(doc,variant,[q['bounds'] for q in decl],folder)
            if not result['usable'] or result['status']!='converged' or result['covariance']['rank']<10:raise RuntimeError('Owner decision: non-identifiable or unusable '+folder)
            phase=s.search_document(candidate,folder)
            if not phase['passed']:raise RuntimeError('Owner decision: follow-up phase gate '+folder)
            jac=s.np.array(result['optimizer_jacobian']).reshape(-1,10)
            correlation=float(s.np.dot(jac[:,9],jac[:,3])/(s.np.linalg.norm(jac[:,9])*s.np.linalg.norm(jac[:,3])))
            n.write(f'{folder}/correlation.json',dict(definition='Cosine correlation of weighted scaled-Jacobian columns for released coordinate and cation-water constant',correlation=correlation,non_separable=abs(correlation)>.95))
            follow_summary=s.assess(candidate,folder,'Sensitivity follow-up; not attribution')
            fitted(candidate,folder,result)
            n.write(f'{folder}/assessment.json',follow_summary)
        s.j.coordinates=original_coordinates
        bicarbonate=s.load(f'{r.OUT}/{label}/followup-bicarbonate/assessment.json')['Ermatchkov88']['AARD_percent']
        control=s.load(f'{r.OUT}/{label}/followup-control/assessment.json')['Ermatchkov88']['AARD_percent']
        n.write(f'{label}/followup-comparison.json',dict(bicarbonate_AARD=bicarbonate,control_AARD=control,improvement_points=control-bicarbonate,margin_points=2.,meets_pressure_margin=control-bicarbonate>=2.,corrected_Kamps_excluded=True,claim='No MDEA outcome falsifies the MEA bicarbonate value; other-property retention must be assessed beside this pressure margin.'))
