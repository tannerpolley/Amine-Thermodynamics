"""Issue 222 downstream acceptance before the saturation-capped refits."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import importlib.util
import importlib.metadata
import sys
import json
from pathlib import Path
import zipfile
AN=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AN.parents[1]/'analyses/mea_parameter_bundle/scripts'))
sys.path.insert(0,str(AN.parents[1]/'src'))
import shared_evaluation
# This process alone qualifies the MDEA wheel; the MEA source pin stays unchanged.
shared_evaluation.ENGINE_WHEEL_SHA256='ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5'
spec=importlib.util.spec_from_file_location('phase_diagnosis',AN/'scripts/diagnose_phase_search.py')
n=importlib.util.module_from_spec(spec);sys.modules[spec.name]=n;spec.loader.exec_module(n)
s=n.s
OUT='results/stage2-density/engine-d5138209'
n.OUT=OUT;s.OUT=OUT
COMMIT='d513820994a78bfe628d42fffd55b2eeab6f89bd'
SHA='ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5'

def identity():
    wheel=s.p.ROOT/f'build/engine-wheels/main-{COMMIT}/epcsaft-1.0.0-cp313-cp313-manylinux_2_39_x86_64.whl'
    assert s.p.sha(wheel)==SHA
    release=json.loads((wheel.parent/'release.json').read_text())
    assert release['commit']==COMMIT and release['sha256']==SHA and release['wheel']==wheel.name
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith(('epcsaft/','epcsaft.libs/')) and not name.endswith('/'):
                assert z.read(name)==(Path(s.p.epcsaft.__file__).parent.parent/name).read_bytes(),name
    n.write('runtime.json',dict(engine_commit=COMMIT,wheel=str(wheel),wheel_sha256=SHA,module=s.p.epcsaft.__file__,installed_files_byte_identical=True,python=sys.version,packages={name:importlib.metadata.version(name) for name in ('epcsaft','numpy','scipy','matplotlib','pandas')},github_digest='sha256:'+SHA,github_tag_target=COMMIT,engine_reading_clone_commit='7f2a1d7d24b79970ab5fe8b0bbc159ede553de31',workers=16,BLAS_threads_per_process=1))

def phases():
    summaries={}
    for label in ('A1','B1'):
        states=n.declare(n.vector(label))
        jobs=[(index,prob) for index,(_,prob) in states.items() if 293.15<=prob.T<=395]
        rows=n.load(f'results/diagnosis-phase-search/reproduce/{label}/saturation-phase-inputs.json')
        jobs += [(r['index'],s.j.problem(r['T_K'],r['P_Pa'],s.j.water(r['mass_fraction']),r['alpha_phase'])) for r in rows if r['status']=='Available']
        assert len(jobs)==754
        s.phase_jobs=jobs
        records=n.pool(s.phase,list(range(len(jobs))))
        n.write(f'{label}/phase.json',records)
        old=n.load(f'results/stage2-density/phase-checks/{label}/phase.json')
        changes=[];checked=0
        for a,b in zip(old,records,strict=True):
            assert a['index']==b['index']
            for t,u in zip(a['stability']['trials'],b['stability']['trials'],strict=True):
                assert (t['seed'],t['phase'])==(u['seed'],u['phase'])
                if t['message'].endswith('reconstruction destroys support'):continue
                checked+=1
                if (t['evidence'],t['resolved_descent'],t['quantities'].get('split_delta_g_over_rt')) != (u['evidence'],u['resolved_descent'],u['quantities'].get('split_delta_g_over_rt')):
                    changes.append(dict(index=a['index'],before=t,after=u))
        errors=[abs((r['after']['quantities']['split_delta_g_over_rt']-r['before']['quantities']['split_delta_g_over_rt'])/r['before']['quantities']['split_delta_g_over_rt']) for r in changes]
        summary=s.phase_summary(records)
        summary.update(max_energy_relative_change=max(errors,default=0.),trials_exceeding_relative_1e8=sum(e>1e-8 for e in errors))
        summary.update(states=len(records),unchanged_trials_checked=checked,changes=changes,energy_comparison='owner clarification: absolute change <=1e-10 with classification unchanged',passed_acceptance=not summary['rounding_states'] and all(r['before']['evidence']==r['after']['evidence'] and r['before']['resolved_descent']==r['after']['resolved_descent'] and abs(r['before']['quantities']['split_delta_g_over_rt']-r['after']['quantities']['split_delta_g_over_rt'])<=1e-10 for r in changes))
        n.write(f'{label}/acceptance.json',summary);summaries[label]=summary
        print(label,dict(states=len(records),changed_energies=len(changes),reconstruction_trials=summary['rounding_trials'],passed_acceptance=summary['passed_acceptance']),flush=True)
    n.write('phase-acceptance.json',summaries)
    return all(r['passed_acceptance'] for r in summaries.values())

if __name__=='__main__':
    identity()
    phases()
