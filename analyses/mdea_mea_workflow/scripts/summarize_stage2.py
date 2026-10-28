"""Summarize the retained item-(k) and bound-stopped joint fit; no Engine calls."""
import json
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
def load(path):return json.loads((AN/path).read_text())
fit=load('results/joint-fit/A1/fit.json');kim=load('results/kim-prefit/summary.json')
endpoints=[]
for label in ('A1','A2','A3','A4','B1','B2','B3'):
    duplicate=label in ('A2','B2')
    endpoints.append(dict(start=label,endpoint=fit['physical'] if label=='A1' else None,objective=fit['final_cost'] if label=='A1' else None,
        identifiability=fit['covariance'] if label=='A1' else None,disposition='Converged; return to Design: three active arbitrary bounds' if label=='A1' else 'Duplicate of '+label[0]+'1; not run' if duplicate else 'Not run after mandatory A1 bound stop'))
result=dict(issue=222,base_commit='d05701f720b9edf18ff76fd1471d52966f946b7f',item_k=kim,disposition='Return to Design: A1 endpoint on arbitrary bounds and Carson row-10 phase failure',
    verdicts={'A':'No transfer verdict: A1 converged on three arbitrary bounds; no representative selected','B':'Not assessed: stopped before B fits after A1 mandatory stop'},
    seven_endpoints=endpoints,active_bounds=[dict(coordinate='k(MDEAH+-CO2)',value=.5,side='upper'),dict(coordinate='k(MDEAH+-HCO3-)',value=1.,side='upper'),dict(coordinate='Born diameter',value=2.,unit='angstrom',side='lower')],
    follow_up='Not run: no qualified representative endpoint. Corrected Kamps remains excluded from the two-AARD-percentage-point criterion. No MDEA outcome falsifies the MEA bicarbonate value.',
    outside_fit='Not evaluated; Ermatchkov AARD unavailable for both variants, no pass/fail against 24.2 percent',
    Neumann_sensitivity='Not run after mandatory bound stop',profiles='Not run after mandatory bound stop; local singular values and right vectors retained at A1 start/endpoint',
    claim_limits='Kim calibration and numerical verification only. A1 is a bound-constrained calibration endpoint, not an adopted parameter set, independent validation or transfer result. No absorber-use or manuscript claim. Xiao and Zhang remain unscored.',review='Not independently reviewed or promoted.')
if (AN/'results/joint-fit/A1/verification.json').exists():result['replay']=load('results/joint-fit/A1/verification.json')
if (AN/'results/joint-fit/A1/carson-phase.json').exists():result['endpoint_Carson']=[{key:r[key] for key in ('source_row','alpha','success','requested_tolerance_met','max_residual','completed','message','split','split_delta_g_over_rt')} for r in load('results/joint-fit/A1/carson-phase.json')]
(AN/'results/stage2-disposition.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['disposition'])
