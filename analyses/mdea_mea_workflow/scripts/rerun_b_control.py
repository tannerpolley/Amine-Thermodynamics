"""One owner-authorized B CO2-control fit with the iteration limit raised to 100."""
import collections
import subprocess
import importlib.util
import json
import sys
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('assessment',AN/'scripts/assess_capped.py')
a=importlib.util.module_from_spec(spec);sys.modules[spec.name]=a;spec.loader.exec_module(a)
s,n,r=a.s,a.n,a.r
FOLDER='B1/followup-control-100'
OLD='B1/followup-control'

def main():
    assert not (AN/r.OUT/FOLDER).exists(),'The authorized 100-iteration attempt is already retained; do not repeat it.'
    runtime=s.load(f'{r.OUT}/runtime.json')
    assert s.p.sha(Path(runtime['wheel']))==runtime['wheel_sha256']==r.a.SHA
    a.FOLLOW='control';s.j.coordinates=a.follow_coordinates
    doc,_=r.endpoint('B1')
    s.setup(doc);coords,decl=a.follow_coordinates(s.params,doc,'B')
    metadata,_,_=s.j.objective(s.params)
    old=s.load(f'{r.OUT}/{OLD}/declaration.json')
    assert json.loads(json.dumps(dict(coordinates=decl,observations=metadata,removed_indices=[])))==old
    controls=s.load(f'{r.OUT}/{OLD}/compute.json')['controls']
    assert controls['maximum_iterations']==40 and controls['workers']==16
    n.write(f'{FOLDER}/start.json',doc)
    n.write(f'{FOLDER}/authority.json',dict(owner_decision='2026-10-29: rerun once from the same control start; change only maximum_iterations from 40 to 100; unavailable if unconverged or phase gate fails; no further question',base_commit='cc01ca59035e44badf3d79ccc01430e27f8ef9bc',start_sha256=s.p.sha(AN/r.OUT/FOLDER/'start.json'),old_declaration_sha256=s.p.sha(AN/r.OUT/OLD/'declaration.json'),runtime=runtime))
    candidate,result=s.fit_document(doc,'B',[q['bounds'] for q in decl],FOLDER,maximum_iterations=100)
    new_controls=s.load(f'{r.OUT}/{FOLDER}/compute.json')['controls']
    assert new_controls==dict(controls,maximum_iterations=100)
    assert s.load(f'{r.OUT}/{FOLDER}/declaration.json')==old
    refusal=dict(total=result['trial_failures'],recorded=len(result['failures']),saturation_refusals=sum('saturation:' in f['message'] for f in result['failures']),by_status=dict(collections.Counter(f['status'] for f in result['failures'])),by_observation=dict(collections.Counter(f['observation'] for f in result['failures'])))
    assert refusal['total']==refusal['recorded']
    n.write(f'{FOLDER}/refusal-summary.json',refusal)
    phase=s.search_document(candidate,FOLDER)
    assert phase['states']==s.load(f'{r.OUT}/{OLD}/phase-summary.json')['states']==754
    jac=s.np.array(result['optimizer_jacobian']).reshape(-1,10)
    correlation=float(s.np.dot(jac[:,9],jac[:,3])/(s.np.linalg.norm(jac[:,9])*s.np.linalg.norm(jac[:,3])))
    n.write(f'{FOLDER}/correlation.json',dict(definition='Cosine correlation of weighted scaled-Jacobian columns for released MDEA-CO2 coordinate and cation-water constant',correlation=correlation,non_separable=abs(correlation)>.95))
    summary=dict(status='UNAVAILABLE',control_folder=FOLDER,control_status=result['status'],control_cost=result['final_cost'],control_refusals=result['trial_failures'],control_iterations=result['iterations'],refusal_summary=refusal,control_phase=phase,control_column_correlation=correlation,control_outside_fit_scored=False,bicarbonate_AARD=s.load(f'{r.OUT}/B1/followup-bicarbonate/assessment.json')['Ermatchkov88']['AARD_percent'],margin_points=2.,corrected_Kamps_excluded=True,bicarbonate_claim=False,owner_decision='2026-10-29: one 100-iteration rerun; unavailable if it does not converge or fails the unchanged density gate; do not ask again')
    if result['status']=='converged' and phase['passed']:
        s.setup(candidate);s.cmeta,s.citems=s.comparison_items();s.assessment_label='B CO2-control, owner-authorized 100 iterations'
        indices=[i for i,q in enumerate(s.cmeta) if q['group']=='Ermatchkov' and q['row']['mass_fraction']<=.49]
        assert len(indices)==88
        predictions=n.pool(s.comparison_prediction,indices)
        n.write(f'{FOLDER}/ermatchkov-88.json',predictions)
        if all(q.get('relative_error') is not None for q in predictions):
            aard=100*sum(abs(q['relative_error']) for q in predictions)/88
            summary.update(status='AVAILABLE',control_outside_fit_scored=True,control_AARD=aard,improvement_points=aard-summary['bicarbonate_AARD'],meets_pressure_margin=aard-summary['bicarbonate_AARD']>=2.)
        else:summary['reason']='At least one of the 88 pressure predictions is unavailable'
    else:summary['reason']='Control did not converge' if result['status']!='converged' else 'Converged control failed the unchanged density-classified phase gate'
    old_dir=AN/r.OUT/OLD
    files=subprocess.check_output(['git','ls-tree','-r','--name-only','cc01ca5','--',str(old_dir.relative_to(AN.parents[1]))],text=True).splitlines()
    for name in files:assert (AN.parents[1]/name).read_bytes()==subprocess.check_output(['git','show','cc01ca5:'+name]),name
    n.write(f'{FOLDER}/verification.json',dict(old_control_files_verified=len(files),old_control_base_commit='cc01ca59035e44badf3d79ccc01430e27f8ef9bc',only_changed_native_control=dict(maximum_iterations=[40,100]),identical_start_coordinate_observation_declaration=True,control_outside_fit_scored=summary['control_outside_fit_scored']))
    n.write(f'{FOLDER}/outcome.json',summary)
    n.write('B1/followup-comparison.json',summary)
    print(json.dumps({key:value for key,value in summary.items() if key!='control_phase'},indent=2),flush=True)

if __name__=='__main__':main()
