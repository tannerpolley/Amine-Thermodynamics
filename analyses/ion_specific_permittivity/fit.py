"""Part I objective with the three ion coefficients free; no adoption."""
from time_fit import coordinates
from calculate import *
import numpy as np

verify()
spec=specification()
coordinates(spec)
controls=json.loads((ROOT/'analyses/mea_parameter_bundle/results/engine-3e83e19c-refit-chain/a6/spec.json').read_text())['controls']
controls.update(maximum_elapsed_time_seconds=3600.,workers=int(os.environ['AGENT_HEAVY_CORES']))
spec.spec['optimizer']=controls
D=json.loads((OUT/'derivative-timing.json').read_text())
R=json.loads((OUT/'replay.json').read_text())
jacobian_seconds=sum(r['seconds'] for r in D)
residual_seconds=sum(r['seconds'] for r in R['groups'].values())
dump('runtime-estimate.json',dict(derivative_seconds=jacobian_seconds,residual_seconds=residual_seconds,iterations=180,
     assumption='One exact derivative evaluation and two residual evaluations per iteration; no parallel speedup credit',
     upper_seconds=180*(jacobian_seconds+2*residual_seconds),typical_15_iterations_seconds=15*(jacobian_seconds+2*residual_seconds),
     timing_repeats=1,scope='Fit only; stability sets timed separately',controls=controls))
assert 180*(jacobian_seconds+2*residual_seconds)<3600
started=time.perf_counter()
result,report,parameters=spec.fit()
report['elapsed_seconds']=time.perf_counter()-started
report['controls']=controls
report['statuses']=[s.name for s in result.statuses]
dump('fit.json',report)
if parameters is not None:
    from epcsaft.parameters import document_mapping
    dump('fitted-parameters.json',document_mapping(parameters))
# Conditional covariance is exposed in physical/optimizer parameter order by the Engine.
dump('fit-information.json',dict(physical=list(result.physical),covariance=report['covariance'],
    available_attributes=[x for x in dir(result.covariance) if not x.startswith('_')]))
print(json.dumps({k:report[k] for k in ('status','message','initial_cost','final_cost','iterations','elapsed_seconds','trial_failures')}),flush=True)
