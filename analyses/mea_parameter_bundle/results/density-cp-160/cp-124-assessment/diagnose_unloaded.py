"""One authorized tighter-control diagnostic; retain the existing raw gate."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT/'analyses/mea_parameter_bundle/scripts'))
import density_cp_160 as d
import epcsaft

source = HERE/'solution-request-0.0.json'
request = json.loads(source.read_text())
mapping = d.s.parameter_mapping(d.OUT/'D1-evidence/F1-double-prime-candidate-parameters.json')
model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=d.vrc.record())
assert d.vt.wheel_sha256() == '48a639e78d00ef88a2f7e66ed1e3d89831ca0ad5267322330d44f48c34926060'
started = time.monotonic()
problem = d.s._problem_from_request(request)
problem.row_tolerance = 1e-12
result = epcsaft.equilibrium.solve_equilibrium(model, problem)
raw = {name:d.s._jsonable(getattr(result, name)) for name in dir(result)
       if not name.startswith('_') and not callable(getattr(result, name))}
maximum = max(map(abs, result.residuals))
report = dict(native_row_tolerance=1e-12, unchanged_raw_gate=1e-9,
    raw_gate_passed=bool(result.success and maximum<=1e-9), raw_result=raw,
    request_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    wheel_sha256=d.vt.wheel_sha256(), Cp_evaluated=False)
if report['raw_gate_passed']:
    mass = sum(problem.feed.values.get(c,0.)*m for c,m in zip(d.s.COMPONENT_IDS,d.hc.MOLAR_MASS))/1000
    Q = epcsaft.PropertyObservable
    hobs = [d.vrc.observable('PhaseProperty',0,prop=Q.TotalEnthalpy), d.vrc.observable('PhaseAmount',0)]
    (h,dh),(n,dn) = d.vrc.first_actions(model,problem,result,hobs,[(1.,0.,None)])[0]
    cp = (n*dh+h*dn)/mass/1000
    obs = [d.vrc.observable('PhaseProperty',0,prop=q) for q in
           [Q.IdealIsobaricHeatCapacity,Q.ResidualIsobaricHeatCapacity,Q.TotalIsobaricHeatCapacity]]
    frozen = [v[0]*n/mass/1000 for v in d.vrc.first_actions(model,problem,result,obs,[(0.,0.,None)])[0]]
    report.update(Cp_evaluated=True, equilibrium_cp_kJ_kg_K=cp,
        ideal_frozen_cp_kJ_kg_K=frozen[0], residual_frozen_cp_kJ_kg_K=frozen[1],
        frozen_cp_kJ_kg_K=frozen[2], reaction_response_kJ_kg_K=cp-frozen[2],
        frozen_sum_error_kJ_kg_K=frozen[0]+frozen[1]-frozen[2], observed_kJ_kg_K=3.8566,
        observed_error_relative=cp/3.8566-1, neighbouring_states=[])
    for step,name in [(.1,'coarse'),(.05,'fine')]:
        values=[]
        for T in [353.15-step,353.15+step]:
            req = copy.deepcopy(request)
            req['temperature']['value'] = T
            pr = d.s._problem_from_request(req); pr.row_tolerance = 1e-12
            rs = epcsaft.equilibrium.solve_equilibrium(model,pr)
            maximum=max(map(abs,rs.residuals))
            report['neighbouring_states'].append(dict(T_K=T,success=rs.success,
                maximum_raw_residual=maximum,maximum_classified_residual=max(map(abs,rs.classified_residuals)),
                termination=rs.message))
            if not rs.success or maximum>1e-9:
                report['FD_failure']='Neighbour fails unchanged raw gate; no Cp qualification.'
                break
            (hs,_),(ns,_) = d.vrc.first_actions(model,pr,rs,hobs,[(0.,0.,None)])[0]
            values.append(hs*ns)
        if len(values)!=2: break
        fd=(values[1]-values[0])/(2*step)/mass/1000
        report[name+'_enthalpy_cp_kJ_kg_K']=fd
        report[name+'_error_relative']=abs(fd/cp-1)
report['wall_s']=time.monotonic()-started
with (HERE/'unloaded-80C-tighter-control.json').open('x') as stream:
    json.dump(report,stream,indent=2,sort_keys=True,default=str);stream.write('\n')
print(json.dumps({k:v for k,v in report.items() if k!='raw_result'},indent=2,default=str))
