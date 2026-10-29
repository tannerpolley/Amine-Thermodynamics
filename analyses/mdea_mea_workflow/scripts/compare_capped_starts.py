"""Issue 222: compare Ermatchkov AARDs for admissible starts within 1% cost."""
import importlib.util
import json
import sys
from pathlib import Path

AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('capped',AN/'scripts/refit_capped.py')
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
s,n=r.s,r.n

def primary(records):
    rows=[q for q in records if q['group']=='Ermatchkov' and q['row']['mass_fraction']<=.49]
    assert len(rows)==88 and all(q.get('relative_error') is not None for q in rows)
    assert all(abs(q['relative_error']-(q['predicted']/q['observed']-1))<1e-14 for q in rows)
    return rows

def aard(rows):return 100*float(s.np.mean([abs(q['relative_error']) for q in rows]))

def main():
    runtime=s.load(f'{r.OUT}/runtime.json')
    assert s.p.sha(Path(runtime['wheel']))==runtime['wheel_sha256']==r.a.SHA
    selection=s.load(f'{r.OUT}/selection.json')
    authority=s.load(f'{r.OUT}/authority.json')
    eligibility=[];comparisons=[]
    for label in authority['starts']:
        chosen=selection[label[0]];doc,fit=r.endpoint(label)
        gate=s.load(f'{r.OUT}/{label}/phase-summary.json')
        gap=100*abs(fit['final_cost']/chosen['cost']-1)
        qualifies=gate['passed'] and gap<=1.
        eligibility.append(dict(start=label,cost=fit['final_cost'],gate_passed=gate['passed'],selected=label==chosen['label'],cost_difference_percent=gap,within_one_percent=gap<=1.,qualifies=qualifies,endpoint_sha256=s.p.sha(AN/r.OUT/label/'endpoint.json')))
        if not qualifies or label==chosen['label']:continue
        s.setup(doc);s.cmeta,s.citems=s.comparison_items()
        s.assessment_label='Capped endpoint; declared comparison between nearly equal fitted costs'
        indices=[i for i,q in enumerate(s.cmeta) if q['group']=='Ermatchkov' and q['row']['mass_fraction']<=.49]
        assert len(indices)==88
        rows=primary(n.pool(s.comparison_prediction,indices))
        path=f'{label}/ermatchkov-88.json';n.write(path,rows)
        retained=primary(s.load(f'{r.OUT}/{chosen["label"]}/comparisons.json'))
        assert [q['row'] for q in rows]==[q['row'] for q in retained]
        reference=s.load(f'{r.OUT}/{chosen["label"]}/assessment.json')['Ermatchkov88']['AARD_percent']
        assert abs(aard(retained)-reference)<1e-12
        value=aard(rows);difference=abs(value-reference)
        comparisons.append(dict(start=label,selected=chosen['label'],rows=88,AARD_percent=value,selected_AARD_percent=reference,absolute_difference_points=difference,non_identification=difference>=2.,predictions=path,predictions_sha256=s.p.sha(AN/r.OUT/path)))
    result=dict(authority='Issue 222 implementation ruling item 4, issuecomment-6476822180; owner correction: threshold >=2 percentage points',base_commit='512649a91b41601ceee57b93b774f64196d5115a',runtime=runtime,selection_sha256=s.p.sha(AN/r.OUT/'selection.json'),scoring='100 times mean absolute (predicted CO2 partial pressure / observed CO2 partial pressure - 1), all 88 Ermatchkov rows at mass fraction <=0.49; pressure in Pa',cost_window_percent=1.,non_identification_threshold_points=2.,eligibility=eligibility,duplicates=authority['duplicates'],excluded=authority['excluded'],comparisons=comparisons,passed=all(not q['non_identification'] for q in comparisons))
    n.write('equal-cost-starts.json',result)
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
