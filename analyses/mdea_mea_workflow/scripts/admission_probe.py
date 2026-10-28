"""Admit start-1 documents and retain a pressure sensitivity probe without fitting."""
import csv
import importlib.util
import json
import math
from pathlib import Path

spec=importlib.util.spec_from_file_location('preparation',Path(__file__).with_name('prepare.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
eq=p.eq


def caloric_record(params):
 from math import comb
 sources=json.loads((p.OUT/'inputs/physical-ideal-gas-calorics.json').read_text())
 intervals=[[] for _ in params.component_ids]
 for cid,source in sources['components'].items():
  if cid not in params.component_ids:continue
  if source['representation']=='cp_polynomial':
   centre=source['enthalpy_entropy_anchor_k']; cp=source['coefficients']
   coefficients=[sum(a*comb(j,k)*centre**(j-k) for j,a in enumerate(cp) if j>=k) for k in range(4)]
   form=p.epcsaft.IdealPolynomial(coefficients,centre,0.,0.)
  else:form=p.epcsaft.IdealShomate(source['coefficients'],source['formation_enthalpy_j_per_mol'])
  intervals[list(params.component_ids).index(cid)]=[p.epcsaft.IdealInterval(*source['range_k'],True,True,p.epcsaft.IdealCorrelation(form,1e5))]
 return p.epcsaft.ThermochemistryRecord(1e5,intervals)


def problem(T,m,a,P,reactions):
 n=1/.01801528
 extent=.97*min(m,a)
 guess={p.W:n-2*extent,p.M:m-extent,p.C:a-extent,p.H:extent,'bicarbonate-anion':extent,'carbonate-anion':1e-6,'hydronium-cation':1e-8,'hydroxide-anion':1e-8}
 return eq.Problem(T=T,P=eq.Free(P),feed=eq.Amounts({p.W:n,p.M:m,p.C:a}),phases=[eq.Phase('L',kind='liquid',support=p.published.SPECIES,composition_guess=guess),eq.Phase('V',kind='vapor',support=p.published.NEUTRAL,amount=eq.Pinned(0.),composition_guess={p.W:.1,p.M:.00001,p.C:.89999})],reactions=reactions,neutral_reference=p.published.NEUTRAL_REFERENCE,row_tolerance=1e-10)


def main():
 packet=p.shared.load_state_packet()['observations'][0]['request']
 records=p.shared._engine_reaction_records(packet,p.shared.reaction_values(p.BASE),mapping=p.BASE)[:3]
 reactions=[]
 for r in records:
  sto={c:v for c,v in zip(p.shared.COMPONENT_IDS,r['stoichiometry']) if v}
  reactions.append(eq.Reaction(sto,name=r['reaction_id'],correlation=p.shared._reaction_correlation(r,r['reaction_id']),reference=p.shared._reaction_reference(r,r['reaction_id'])))
 ref=p.shared.COMMON_SOURCE_STANDARD_STATE_ID
 reactions.append(eq.Reaction({p.H:-1,p.W:-1,p.M:1,'hydronium-cation':1},name='MDEA-dissociation',correlation=eq.ReactionLogPolynomial(-83.491+4.0165+10.976*math.log(313.15),-819.7,10.976,0.,313.15,278.,393.15,ref),reference=eq.ReactionReference(eq.ReferenceSourceBasis.CommonMolalityInfiniteDilution,1e5)))
 p.write('inputs/probe-reaction-reference.json',dict(shared=records,MDEA=dict(a=-83.491,b=-819.7,c=10.976,lnKx_to_lnKm=4.0165,reference_pressure_Pa=1e5,range_note='278-368 K original title; extension to 393 K is the issue 222 model assumption; original paper unavailable'),row_tolerance=1e-10))
 rows=[r for r in csv.DictReader((p.DATA/'Kuranov_1996_CO2_MDEA_total_pressure.csv').open()) if float(r['m_CO2_mol_per_kg_H2O'])/float(r['m_MDEA_mol_per_kg_H2O'])>1 and round(float(r['temperature_K']))<=393]
 # The 20 rows comprise 13 at nominal 313 K, five at 333 K and two at 373 K; none at 393 K.
 assert len(rows)==20,len(rows)
 p.write('inputs/probe-rows.json',rows)
 for variant in 'AB':
  d=json.loads((p.OUT/f'inputs/variant-{variant}.json').read_text())
  report=dict(variant=variant,status='incomplete',states=[])
  try:
   params=p.epcsaft.Parameters.from_mapping(d)
   model=p.epcsaft.Mixture(params,thermochemistry=caloric_record(params))
   report['admission_message']='Parameters.from_mapping and Mixture construction returned without exception'
   for name,x in [('unloaded',{p.W:.95,p.M:.05}),('loaded',{p.W:.94,p.M:.04,p.H:.01,'bicarbonate-anion':.01})]:
    state=model.state(313.15,P=1e5,x=x,phase='liquid')
    terms={k:getattr(state,k) for k in ('hard_chain','dispersion','association','debye_huckel','born','residual_helmholtz')}
    report['states'].append(dict(name=name,T_K=313.15,P_Pa=1e5,x=x,rho_mol_m3=state.molar_density,bulk_permittivity=state.bulk_relative_permittivity,terms=terms,pressure_residual_Pa=state.pressure-1e5))
   pure_params=p.epcsaft.Parameters.from_mapping(d,components=[p.M,p.W])
   pure_model=p.epcsaft.Mixture(pure_params,thermochemistry=caloric_record(pure_params))
   pure=pure_model.state(313.15,rho=1e5/(p.epcsaft.GAS_CONSTANT_J_PER_MOL_K*313.15),x={p.M:1.})
   expected=json.loads((p.OUT/'inputs/physical-ideal-gas-calorics.json').read_text())['components'][p.M]['coefficients']
   assert abs(pure.ideal_enthalpy)<1e-9 and abs(pure.ideal_isobaric_heat_capacity-sum(c*313.15**i for i,c in enumerate(expected)))<1e-9
   assert abs(pure.ideal_entropy)<1e-9
   report['status']='complete'
   neutral_params=p.epcsaft.Parameters.from_mapping(d,components=[p.M,p.W])
   neutral_model=p.epcsaft.Mixture(neutral_params,thermochemistry=caloric_record(neutral_params))
   unloaded=neutral_model.state(313.15,P=1e5,x={p.W:.95,p.M:.05},phase='liquid')
   assert unloaded.ideal_enthalpy is not None and unloaded.ideal_isobaric_heat_capacity is not None
   report['unloaded_calorics']=dict(ideal_h_J_mol=unloaded.ideal_enthalpy,ideal_Cp_J_mol_K=unloaded.ideal_isobaric_heat_capacity,total_h_J_mol=unloaded.total_enthalpy)
   report['MDEA_ideal_at_anchor']=dict(T_K=313.15,h_J_mol=pure.ideal_enthalpy,s_J_mol_K=pure.ideal_entropy,Cp_J_mol_K=pure.ideal_isobaric_heat_capacity)
   report['caloric_limit']='Full eight-species neutral thermochemistry admitted. Direct Mixture.state totals require all ionic ideal records, even at zero ionic fractions; reaction-completed ionic totals are deferred to item (g). MDEA ideal functions separately evaluated in native selected-component model.'
   report['reason']='Full parameter and MDEA ideal-gas admission succeeded in both liquid compositions; prescribed charged composition is not reactive equilibrium. Ionic reference completion remains conditional on item (g).'
  except Exception as e:
   report['status']='incomplete'
   report['admission_message']=f'{type(e).__name__}: {e}'
   report['reason']='Refusal retained; no alternate convention substituted.'
   p.write(f'results/admission-{variant}.json',report)
   p.write(f'results/probe-{variant}.json',dict(status='blocked',reason='Variant admission refused',message=report['admission_message']))
   continue
  p.write(f'results/admission-{variant}.json',report)
  try:
   # Native regression observations and coordinates as in MEA fit_observations.py.
   coordinates=[p.reg.coordinate(params,[('k_ij',(cid,p.C),1.)],origin=0.,scale=1.) for cid in (p.M,p.H)]
   observations=[]
   for r in rows:
    prob=problem(float(r['temperature_K']),float(r['m_MDEA_mol_per_kg_H2O']),float(r['m_CO2_mol_per_kg_H2O']),float(r['ten_times_total_pressure_MPa'])*1e5,reactions)
    observations.append(p.reg.observation(params,'pressure',prob,observed=float(r['ten_times_total_pressure_MPa'])*1e5,form='log_ratio'))
   # evaluate, never fit: exact coordinate Jacobian.
   print('differentiate start 1',variant,flush=True)
   result=p.reg.differentiate(params,coordinates,observations,optimizer=[0.,0.])
   p.write(f'results/probe-{variant}.json',result)
  except Exception as e:
   p.write(f'results/probe-{variant}.json',dict(status='incomplete',error=f'{type(e).__name__}: {e}',rows=20,columns=['k(MDEA-CO2)','k(MDEAH+-CO2)'],note='No optimizer run; no coordinate selected.'))
 print('admission and probe attempts retained',flush=True)

if __name__=='__main__':main()
