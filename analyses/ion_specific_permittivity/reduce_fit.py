"""Rebuild the fitted declaration and check its predictions and conditional errors."""
from calculate import *
from time_fit import coordinates
from types import SimpleNamespace
import numpy as np
from MEA.solvent_specification import conditional_information

verify()
report=json.loads((OUT/'fit.json').read_text())
spec=specification()
declared=coordinates(spec)
values=[q['origin']+q['scale']*v for q,v in zip(declared,report['optimizer'],strict=True)]
mapping=composed(BASE)
# Each declared multiplier is the existing tie to the independent physical coordinate.
for q,v in zip(declared,values,strict=True):
    for family,target,factor in q['targets']:
        if isinstance(target,str):
            component=next(c for c in mapping['components'] if c['component_id']==target)
            selected='ion_specific_suppression_coefficient' if family=='ion_suppression_coefficient' else family
            coefficient=next(c for c in component['coefficients'] if c['family']==selected)
        else:
            pair=next(p for p in mapping['pairs'] if {p['component_id_a'],p['component_id_b']}==set(target))
            selected='k_ij_reciprocal_temperature_slope' if family=='k_ij_reciprocal_temperature_slope' else family
            coefficient=next(c for c in pair['coefficients'] if c['family']==selected)
        coefficient['value']['magnitude']=v*factor
# The independently reconstructed coordinate values must reproduce the native fit.
parameters=epcsaft.Parameters.from_mapping(mapping)
spec.parameters=parameters
spec.model=epcsaft.Mixture(parameters,thermochemistry=spec.thermal)
records=spec.inputs['observations']['fitted']
predictions=[spec.prediction(r) for r in records]
for r,p in zip(records,predictions,strict=True):
    assert p['status']=='Available' and p['requested_tolerance_met'],p
    p['cost']=.5*r['weight']*p['residual']**2
cost=math.fsum(p['cost'] for p in predictions)
assert abs(cost/report['final_cost']-1)<1e-10,(cost,report['final_cost'])
assert max(abs(p['value']-v)/max(1.,abs(v)) for p,v in zip(predictions,report['predictions'],strict=True))<1e-10
dump('fitted-parameters.json',mapping)
dump('fitted-observations.json',predictions)
ev=reg.differentiate(spec.parameters,spec.coordinates(),[spec.observation(r) for r in records],optimizer=report['optimizer'],holds=[],thermochemistry=spec.thermal)
J=np.asarray(ev.residual_optimizer_gradient).reshape(len(records),len(declared))
J*=np.sqrt([r['weight'] for r in records])[:,None]
J/=np.asarray([q['scale'] for q in declared])[None,:]
r=np.asarray([math.sqrt(row['weight'])*p['residual'] for row,p in zip(records,predictions,strict=True)])
result=SimpleNamespace(covariance=SimpleNamespace(active_bounds=report['covariance']['active_bounds']),physical=values)
info=conditional_information(result,J,r,[q['identity'] for q in declared],[q['bounds'][0] for q in declared],[q['bounds'][1] for q in declared])
info.update(parameters=[dict(identity=q['identity'],start=q['origin'],fitted=v,standard_error=info['conditional_standard_error'].get(q['identity']),active_bound=i in report['covariance']['active_bounds']) for i,(q,v) in enumerate(zip(declared,values,strict=True))],
            replay_cost=cost,max_prediction_relative_difference=max(abs(p['value']-v)/max(1.,abs(v)) for p,v in zip(predictions,report['predictions'],strict=True)),
            groups={g:sum(p['cost'] for p in predictions if p['group']==g) for g in dict.fromkeys(p['group'] for p in predictions)})
dump('fit-information.json',info)
print(json.dumps(info['parameters'][-3:]),cost,flush=True)
