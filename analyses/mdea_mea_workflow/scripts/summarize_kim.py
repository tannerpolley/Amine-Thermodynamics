"""Retained Kim fit and phase-search accounting; no Engine calls."""
import csv,json,math
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
out=AN/'results/kim-prefit'
def load(n):return json.loads((out/n).read_text())
fit=load('fit.json');secondary=load('fit-secondary.json');phase=load('binary-phase-search.json');reactive=load('amended-carson-search.json')
rows=list(csv.DictReader((AN.parents[1]/'data/reference/MDEA/Kim2008_stage1.csv').open()))
assert len(rows)==len(fit['predictions'])==61
with (out/'bubble-pressure-residuals.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['source_row','temperature_K','x_MDEA','observed_pressure_Pa','predicted_pressure_Pa','log_ratio','vapor_witness','matching_positive_sign'])
    writer.writeheader();sign=[]
    for row,pred in zip(rows,fit['predictions']):
        observed=float(row['total_pressure_kPa'])*1000
        report=next(p for p in phase if p['label']=='Kim-'+row['source_row'])
        vapor=any(t['resolved_descent'] and t['kind']=='vapor' for t in report['report']['trials'])
        match=pred>observed if vapor else None
        record=dict(source_row=row['source_row'],temperature_K=float(row['temperature_C'])+273.15,x_MDEA=float(row['liquid_x_MDEA']),observed_pressure_Pa=observed,predicted_pressure_Pa=pred,log_ratio=math.log(pred/observed),vapor_witness=vapor,matching_positive_sign=match)
        writer.writerow(record)
        if vapor:sign.append(record)
(out/'vapor-witnesses.json').write_text(json.dumps([r for r in phase if any(t['resolved_descent'] and t['kind']=='vapor' for t in r['report']['trials'])],indent=2)+'\n')
summary=dict(item_k='pass',fit_converged=fit['status']=='converged' and secondary['status']=='converged',primary=fit['physical'],secondary=secondary['physical'],singular_values=fit['covariance']['singular_values'],AARD_percent=fit['AARD_percent'],objective=fit['final_cost'],binary_searches=len(phase),binary_liquid_witnesses=sum(not r['liquid_miscible'] for r in phase),binary_search_completed=sum(r['report']['completed'] for r in phase),binary_unresolved=sum('unresolved trials 0' not in r['report']['message'] for r in phase),convex_hull_miscible=[r['miscible'] for r in load('mixing-scans.json')],Carson_pass=sum(r.get('completed',False) and not r.get('split',True) and 'unresolved trials 0' in r.get('message','') for r in reactive),Carson_searches=len(reactive),Kim_vapor_witnesses=len(sign),Kim_sign_mismatches=[r for r in sign if not r['matching_positive_sign']])
assert summary['fit_converged'] and summary['binary_liquid_witnesses']==0 and summary['binary_unresolved']==0 and all(summary['convex_hull_miscible']) and summary['Carson_pass']==10
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
