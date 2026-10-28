"""Check the density gate on historical A1/B1 states, without fitting or scoring."""
import importlib.util
import math
from pathlib import Path
import sys
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('phase_diagnosis',AN/'scripts/diagnose_phase_search.py')
n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
s=n.s
n.OUT='results/stage2-density/phase-checks'
s.OUT=n.OUT


def classification_check():
    def trial(eta,kind):
        return dict(resolved_descent=True,split_coordinates=[math.log(eta)],seed='density-check',
            phase=dict(kind=kind),quantities=dict(split_delta_g_over_rt=-.01),evidence='numerically_resolved_descending_split_with_estimated_uncertainty')
    report=dict(completed=True,message='unresolved trials 0',trials=[trial(.02,'liquid'),trial(.43,'vapor')])
    q=s.classify_trials(report)
    assert len(q['dense_splits'])==len(q['gas_evolution'])==1 and not q['ambiguous']
    report['trials']=[trial(.1,'liquid')]
    assert s.classify_trials(report)['ambiguous']
    report.update(message='unresolved trials 1',trials=[dict(resolved_descent=False,seed='check',evidence='unresolved',message='iteration limit')])
    assert s.classify_trials(report)['other_unresolved']
    report['trials'][0]['message']='converged; reconstruction destroys support'
    q=s.classify_trials(report)
    assert len(q['rounding_trials'])==1 and not q['other_unresolved']


if __name__=='__main__':
    classification_check()
    assert not s.phase_summary([])['passed']
    runtime=s.load('inputs/runtime.json')
    assert s.p.sha(Path(runtime['wheel']))==runtime['wheel_sha256']==s.p.shared.ENGINE_WHEEL_SHA256
    n.write('runtime.json',dict(runtime,workers=16,base_commit='6714b76',purpose='No refit; historical phase check'))
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
        summary=s.phase_summary(records)
        summary['purpose']='Historical endpoint phase verification only; no refit and no outside-fit statistic'
        summary['carbon_free_states']=sum(r.get('carbon_free_trial_supports',False) for r in records)
        summary['ion_free_checks']=sum(r.get('ion_free_check') is not None for r in records)
        assert summary['ion_free_checks']==len(summary['rounding_states'])
        n.write(f'{label}/summary.json',summary)
        summaries[label]=summary
        print(label,{k:len(v) if isinstance(v,list) else v for k,v in summary.items()},flush=True)
    n.write('summary.json',summaries)
