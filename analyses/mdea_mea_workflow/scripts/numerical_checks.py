"""Check selected sensitivity columns against centered finite differences."""
import importlib.util
import json
import math
import sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('probe',Path(__file__).with_name('admission_probe.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);p=a.p
records=json.loads((p.OUT/'inputs/probe-reaction-reference.json').read_text())['shared']
reactions=[]
for r in records:
 sto={c:v for c,v in zip(p.shared.COMPONENT_IDS,r['stoichiometry']) if v}
 reactions.append(p.eq.Reaction(sto,name=r['reaction_id'],correlation=p.shared._reaction_correlation(r,r['reaction_id']),reference=p.shared._reaction_reference(r,r['reaction_id'])))
reactions.append(p.eq.Reaction({p.H:-1,p.W:-1,p.M:1,'hydronium-cation':1},name='MDEA-dissociation',correlation=p.eq.ReactionLogPolynomial(-83.491+4.0165+10.976*math.log(313.15),-819.7,10.976,0.,313.15,278.,393.15,p.shared.COMMON_SOURCE_STANDARD_STATE_ID),reference=p.eq.ReactionReference(p.eq.ReferenceSourceBasis.CommonMolalityInfiniteDilution,1e5)))
r=json.loads((p.OUT/'inputs/probe-rows.json').read_text())[0]
prob=a.problem(float(r['temperature_K']),float(r['m_MDEA_mol_per_kg_H2O']),float(r['m_CO2_mol_per_kg_H2O']),float(r['ten_times_total_pressure_MPa'])*1e5,reactions)
checks=[]
for v in 'AB':
 doc=json.loads((p.OUT/f'inputs/variant-{v}.json').read_text())
 params=p.epcsaft.Parameters.from_mapping(doc)
 item=p.reg.observation(params,'pressure',prob,observed=float(r['ten_times_total_pressure_MPa'])*1e5,form='log_ratio')
 exact=json.loads((p.OUT/f'results/probe-{v}.json').read_text())['residual_optimizer_gradient'][:2]
 for cid,deriv in zip((p.M,p.H),exact):
  pair=next(x for x in doc['pairs'] if {x['component_id_a'],x['component_id_b']}=={cid,p.C})
  identity=pair['coefficients'][0]['identity']; step=float(sys.argv[1]) if len(sys.argv)>1 else 1e-3; vals=[]
  for sign in (-1,1):
   mapped=p.shared.with_parameter_values(doc,{identity:sign*step})
   model=p.epcsaft.Mixture(p.epcsaft.Parameters.from_mapping(mapped))
   pred=p.reg.predict(model,item)
   assert pred.status.name=='Available',pred.message
   vals.append(math.log(pred.value))
  fd=(vals[1]-vals[0])/(2*step)
  checks.append(dict(variant=v,coordinate=cid+'-CO2',step=step,exact=deriv,finite_difference=fd,relative_error=abs(fd-deriv)/abs(deriv),tolerance=1e-5,passed=abs(fd-deriv)/abs(deriv)<=1e-5))
p.write('results/numerical-checks.json',dict(derivatives=checks,derivative_checks_pass=all(r['passed'] for r in checks),source_row=r['source_row'],shared_component_and_pair_invariant='Assertions in prepare.documents compare against the pinned MEA JSON',equilibrium_tolerance=1e-10,kappa_max_equilibrium_residual=json.loads((p.OUT/'results/kappa/summary.json').read_text())['max_equilibrium_residual'],dielectric_native_replay_max=json.loads((p.OUT/'results/dielectric/summary.json').read_text())['max_abs_native_replay'],joint_optimization_run=False))
print(checks)
