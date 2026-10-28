"""Hsieh pure/aqueous MDEA fit to the MEA solvent law at model densities."""
import csv
import importlib.util
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

spec=importlib.util.spec_from_file_location('preparation',Path(__file__).with_name('prepare.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


def main():
 k=json.loads((p.OUT/'results/kappa/summary.json').read_text())['kappa']
 docs=p.documents(k)
 # Neutral-state density is independent of the dielectric coefficients.
 for d in docs:
  c=next(c for c in d['components'] if c['component_id']==p.M)
  c['coefficients'] += [p.coef(p.M,'dielectric_volume',.7,'liter / mole'),p.coef(p.M,'dielectric_temperature',1000.,'kelvin')]
 model=p.epcsaft.Mixture(p.epcsaft.Parameters.from_mapping(docs[0]))
 rows=[]
 for r in csv.DictReader((p.DATA/'Hsieh_2007_MDEA_relative_permittivity.csv').open()):
  rows.append(dict(T=float(r['temperature_K']),x=1.,observed=float(r['relative_permittivity']),source='Table 2'))
 for r in csv.DictReader((p.DATA/'Hsieh2007_stage1.csv').open()):
  rows.append(dict(T=float(r['temperature_K']),x=float(r['x_MDEA']),observed=float(r['relative_permittivity']),source='Table 5'))
 for r in rows:
  s=model.state(r['T'],P=101325.,x={p.M:r['x'],p.W:1-r['x']},phase='liquid')
  assert s.pressure_density_derivative>0
  r['rho_mol_L']=s.molar_density/1000
  r['pressure_residual_Pa']=s.pressure-101325.
 T,x,rho,y=[np.array([r[q] for r in rows]) for q in ('T','x','rho_mol_L','observed')]
 # MEA fit_campaign.py stage5_study law; same 1% relative residual scale.
 def predict(v):
  return 1+rho*((1-x)*.3777+x*v[0])*(((1-x)*1403+x*v[1])/T-1)
 fit=least_squares(lambda v:(predict(v)-y)/(.01*y),[.7,1000.],xtol=1e-12,ftol=1e-12,gtol=1e-12)
 assert fit.success,fit.message
 alternative=least_squares(lambda v:(predict(v)-y)/(.01*y),[.28,2800.],xtol=1e-12,ftol=1e-12,gtol=1e-12)
 assert alternative.success,alternative.message
 assert fit.x[0]>alternative.x[0] and fit.cost<alternative.cost
 v=fit.x
 for variant,d in zip('AB',docs):
  for c in d['components']:
   if c['component_id']==p.M:
    for coeff in c['coefficients']:
     if coeff['family']=='dielectric_volume': coeff['value']['magnitude']=float(v[0])
     if coeff['family']=='dielectric_temperature': coeff['value']['magnitude']=float(v[1])
  p.write(f'inputs/variant-{variant}.json',d)
 native=p.epcsaft.Mixture(p.epcsaft.Parameters.from_mapping(docs[0]))
 for r,yp in zip(rows,predict(v)):
  r['calculated']=float(yp)
  r['native_replay']=native.state(r['T'],rho=r['rho_mol_L']*1000,x={p.M:r['x'],p.W:1-r['x']}).bulk_relative_permittivity
 assert max(abs(r['calculated']-r['native_replay']) for r in rows)<1e-10
 p.write('results/dielectric/rows.json',rows)
 p.write('results/dielectric/summary.json',dict(status='complete',dielectric_volume_L_mol=v[0],dielectric_temperature_K=v[1],cost=fit.cost,alternative=dict(dielectric_volume_L_mol=alternative.x[0],dielectric_temperature_K=alternative.x[1],cost=alternative.cost,aard_percent=100*np.mean(abs(predict(alternative.x)/y-1))),selection_rule='MEA larger-volume convention, supplement.tex paragraph supplement-20; also lower cost here',mean_signed_percent_by_x={str(q):float(100*np.mean((predict(v)/y-1)[x==q])) for q in sorted(set(x))},density_basis='start-1 neutral densities, MDEA-water k=0',absorber_composition_limit='23-49 wt%, x about 0.04-0.13, below Hsieh minimum x=0.2',n=len(rows),aard_percent=100*np.mean(abs(predict(v)/y-1)),max_abs_native_replay=max(abs(r['calculated']-r['native_replay']) for r in rows),source='Hsieh 2007 Tables 2 and 5',method='MEA fit_campaign.py stage5_study solvent law; 1% relative scales; least squares of two coefficients; neutral EOS densities at 101325 Pa (pressure assumption, not printed in Hsieh)',controls=dict(xtol=1e-12,ftol=1e-12,gtol=1e-12),extrapolation='Above 328.15 K coefficients are a model assumption, not measured evidence.'))
 summary=json.loads((p.OUT/'results/dielectric/summary.json').read_text())
 comparisons=[]
 for fraction in (.04,.13,.2,.4,.6,.8,1.):
  density=native.state(393.,P=101325.,x={p.M:fraction,p.W:1-fraction},phase='liquid').molar_density/1000
  def epsilon(coeff):
   return 1+density*((1-fraction)*.3777+fraction*coeff[0])*(((1-fraction)*1403+fraction*coeff[1])/393.-1)
  comparisons.append(dict(T_K=393.,x_MDEA=fraction,selected=epsilon(v),alternative=epsilon(alternative.x),difference_percent=100*(epsilon(alternative.x)/epsilon(v)-1)))
 summary['comparison_393_K']=comparisons
 p.write('results/dielectric/summary.json',summary)
 print(v,flush=True)

if __name__=='__main__':main()
