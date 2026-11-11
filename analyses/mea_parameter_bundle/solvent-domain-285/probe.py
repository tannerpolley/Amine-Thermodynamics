import sys, json, hashlib, csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'analyses/mea_parameter_bundle/scripts')]
import shared_evaluation as s
import epcsaft
from epcsaft import equilibrium as e

s.verify_wheel()
base=ROOT/'analyses/mea_parameter_bundle'
paths={'final':base/'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json','candidate':base/'results/stable-refit-255/evidence/candidate-parameters.json'}
template=s.load_state_packet()['observations'][0]['request']
ids=s.COMPONENT_IDS
feed=e.Amounts(dict(zip(ids,[.358,1,7.929776437398854,0,0,0,0,0,0])))
L0=[9.359e-06,.04206,.8778,.04011,.03807,.001865,.00008891,1.199e-9,6.590e-7]
V0=[.03927,.001210,.9595]
for name,path in paths.items():
 for rule in ('solvent-only','solvent-density-temperature'):
  mapping=s.parameter_mapping(path)
  if rule=='solvent-only':
   old=json.loads((base/'data/input/fit-campaigns/effective-F3-A.json').read_text())
   next(f for f in mapping['model_families'] if f['kind']=='permittivity')['choice']=rule
   for c in mapping['components']:
    c['coefficients']=[v for v in c['coefficients'] if v['family'] not in ('dielectric_volume','dielectric_temperature')]
    source=next(x for x in old['components'] if x['component_id']==c['component_id'])
    c['coefficients'] += [v for v in source['coefficients'] if v['family']=='relative_permittivity']
   mapping['correlations'] += [v for v in old['correlations'] if v['family']=='relative_permittivity']
  model=epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
  records=s._engine_reaction_records(template,s.reaction_values(mapping),mapping=mapping)
  reactions=[e.Reaction(dict(zip(ids,map(float,r['stoichiometry']))),name=r['reaction_id'],correlation=s._reaction_correlation(r,r['reaction_id']),reference=s._reaction_reference(r,r['reaction_id'])) for r in records]
  for T in (353.15,358.15):
   L,V,P=L0,V0,45000.
   for nv in [0.645,1,2,3,3.5,3.8,3.9,3.95,4,4.5,5,5.5,5.6,5.7,5.8,5.9,6,6.1,6.2,6.3,6.4,6.5,7,7.5,7.75,8,8.05,8.1,8.3]:
    p=e.Problem(T=T,P=e.Free(P),feed=feed,reactions=reactions,neutral_reference=s._neutral_reference(template),row_tolerance=1e-10,topology_declared=True,phases=[e.Phase('L',kind='liquid',support=ids,amount=e.Free(),composition_guess=L),e.Phase('V',kind='vapor',support=ids[:3],amount=e.Pinned(nv/9.287776437398854),composition_guess=V)])
    r=e.solve_equilibrium(model,p)
    print(name,rule,T,nv,r.success,r.message,flush=True)
    if r.success:
     L,V,P=list(r.mole_fractions[:9]),list(r.mole_fractions[9:12]),r.pressure
     print('RESULT',json.dumps(dict(set=name,rule=rule,T=T,V=nv,P=P,L=L,y=V,amounts=list(r.amounts))),flush=True)
