import sys,csv
from pathlib import Path
sys.path.insert(0,str(Path('analyses/mea_parameter_bundle/results/permittivity-screen-172').resolve()))
import permittivity_probe as s
masses={c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in s.CURRENT['components']}
loaded={.22:[71.3,70.1,67.8,69.7,66.8,63.6,60.1],.33:[80.5,80.9,79.5,76.6,72.4,68.6,63.4],.44:[89.6,90.6,88.3,84.1,79.3,74.7,68.8],.55:[92.7,92.7,82.7,84.2,87.2,75.2,72.4]}
rows=[]
for name,record in s.VARIANTS.items():
 model=s.mixture(record)
 for datum in csv.DictReader((s.OUT/'inputs/agieienko-298K.csv').open()):
  w,eps,rho_g=float(datum['MEA_wt_percent'])/100,float(datum['epsilon_s']),float(datum['density_g_cm3'])
  am=[0.,w/masses['monoethanolamine'],(1-w)/masses['water']]+[0.]*6
  x=[v/sum(am) for v in am];rho=rho_g*1000/(1/sum(am))
  measured=model.state(298.15,rho=rho,x=x)
  predicted=model.state(298.15,P=101325,x=x,phase='liquid')
  rows.append(dict(variant=name,source='AgieienkoBuchner2024-SI-S1-S2',temperature_K=298.15,MEA_wt_percent=100*w,loading=0.,observed_epsilon=eps,source_density_kg_m3=rho_g*1000,source_density_mol_m3=rho,predicted_density_mol_m3=predicted.molar_density,epsilon_at_source_density=measured.bulk_relative_permittivity,epsilon_at_model_density=predicted.bulk_relative_permittivity,comparison='nonreactive neutral composition; neat MEA density source-independent check'))
 for loading,epsilons in loaded.items():
  for T,eps in zip(range(293,354,10),epsilons):
   T=T+.15
   feed=s.h.eq.Amounts({'monoethanolamine':1.,'water':masses['monoethanolamine']*.7/(.3*masses['water']),'carbon-dioxide':loading})
   prob=s.h.eq.Problem(T=T,P=101325.,feed=feed,phases=[s.h.eq.Phase('L',kind='liquid')],reactions=s.CURRENT_REACTIONS,neutral_reference=s.s._neutral_reference(s.REQUEST))
   r=s.h.eq.solve_equilibrium(model,prob)
   row=dict(variant=name,source='Hajj2024-Table1-p9',temperature_K=T,MEA_wt_percent=30.,loading=loading,observed_epsilon=eps,pressure_assumption_Pa=101325.,accepted=r.success,message=r.message,comparison='qualified static-limit extrapolation; not a calibration target')
   if r.success:
    state=model.state(T,rho=r.molar_densities[0],x=r.mole_fractions[:9]);row.update(epsilon_at_model_density=state.bulk_relative_permittivity,predicted_density_mol_m3=state.molar_density,residual_epsilon=state.bulk_relative_permittivity-eps)
   rows.append(row)
s.table('dielectric-comparisons.csv',rows)
print('DIELECTRIC',len(rows),flush=True)
