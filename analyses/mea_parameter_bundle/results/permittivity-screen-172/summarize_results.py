import csv,json,math
from pathlib import Path
O=Path('analyses/mea_parameter_bundle/results/permittivity-screen-172')
def table(name,rows):
 with (O/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for r in rows for k in r)),lineterminator='\n');w.writeheader();w.writerows(rows)
rs=json.loads((O/'targets.json').read_text()); summary=[]; groups=[]
for name in sorted({r['variant'] for r in rs}):
 part=[r for r in rs if r['variant']==name]
 for r in part:r['quantity']='heat' if r['source'] in ('Vinjarapu2024','Arcis2011') else 'pressure' if r['target'].endswith('-pco2') else 'species'
 row=dict(variant=name,targets=149,available=sum(r['status']=='Available' for r in part),cost=sum(r['cost'] for r in part if r['source']!='Arcis2011'))
 for q in ('pressure','species'):
  p=[r for r in part if r['quantity']==q];row[q+'_AARD_percent']=100*sum(abs(r['predicted']/r['observed']-1) for r in p)/len(p);row[q+'_cost']=sum(r['cost'] for r in p)
 for src in ('Vinjarapu2024','Arcis2011'):
  p=[r for r in part if r['source']==src];row[src+'_RMSE_kJ_mol']=math.sqrt(sum((r['predicted']-r['observed'])**2 for r in p)/len(p))/1000;row[src+'_cost']=sum(r['cost'] for r in p)
 summary.append(row)
 for source,q,T in sorted({(r['source'],r['quantity'],r['temperature_K']) for r in part}):
  p=[r for r in part if (r['source'],r['quantity'],r['temperature_K'])==(source,q,T)]
  groups.append(dict(variant=name,source=source,quantity=q,temperature_K=T,n=len(p),cost=sum(r['cost'] for r in p),AARD_percent=100*sum(abs(r['predicted']/r['observed']-1) for r in p)/len(p),RMSE=math.sqrt(sum((r['predicted']-r['observed'])**2 for r in p)/len(p)),RMSE_unit='J/mol CO2' if q=='heat' else 'Pa' if q=='pressure' else 'mole fraction'))
base=next(r for r in summary if r['variant']=='baseline')
for r in summary:
 for k in ('cost','pressure_AARD_percent','species_AARD_percent','Vinjarapu2024_RMSE_kJ_mol','Arcis2011_RMSE_kJ_mol'):r['delta_'+k]=r[k]-base[k]
table('target-summary.csv',summary);table('target-source-temperature.csv',groups)
co=[]
for dt in (900,1403,2200):
 a,b=[next(r for r in summary if r['variant']==f'MEA-{dt}-CO2-{v}') for v in ('near-zero','epsilon-1.55')]
 co.append(dict(MEA_dT_K=dt,**{k+'_difference_low_minus_nearzero':b[k]-a[k] for k in ('cost','pressure_AARD_percent','species_AARD_percent','Vinjarapu2024_RMSE_kJ_mol','Arcis2011_RMSE_kJ_mol')}))
table('co2-sensitivity.csv',co)
expected=dict(cost=32.056684,pressure_AARD_percent=13.814751,species_AARD_percent=7.891434,Vinjarapu2024_RMSE_kJ_mol=2.1266,Arcis2011_RMSE_kJ_mol=8.3644)
table('baseline-replay.csv',[dict(quantity=k,reported=v,replayed=base[k],difference=base[k]-v) for k,v in expected.items()])
print('SUMMARIZED 7 target records',flush=True)
family=json.loads((O/'flash-family.json').read_text())
recovered=json.loads((O/'flash-family-recovery.json').read_text())+json.loads((O/'flash-family-bubble-starts.json').read_text())
accepted={(r['basis'],r['variant'],r['index']) for r in family if r['accepted']}
accepted.update((r['basis'],r['variant'],r['index']) for r in recovered if r.get('accepted'))
summary=[]; joined=[]
for basis in ('current','engine-case7'):
 for variant in sorted({r['variant'] for r in family}):
  part=[r for r in family if r['basis']==basis and r['variant']==variant]
  summary.append(dict(basis=basis,variant=variant,n=73,cold_accepted=sum(r['accepted'] for r in part),accepted_after_bounded_starts=sum((basis,variant,r['index']) in accepted for r in part),row66_cold=next(r['accepted'] for r in part if r['index']==66),row66_after_starts=(basis,variant,66) in accepted))
 for i in range(73):
  part=[r for r in family if r['basis']==basis and r['index']==i]
  joined.append(dict(basis=basis,index=i,loading=part[0]['loading'],temperature_K=part[0]['temperature_K'],pressure_Pa=part[0]['pressure_Pa'],**{r['variant']+'_cold':r['accepted'] for r in part},**{r['variant']+'_after_starts':(basis,r['variant'],i) in accepted for r in part}))
table('flash-family-summary.csv',summary);table('flash-family-comparison.csv',joined)
dielectric=list(csv.DictReader((O/'dielectric-comparisons.csv').open())); summary=[]
for variant in sorted({r['variant'] for r in dielectric}):
 for source in sorted({r['source'] for r in dielectric}):
  part=[r for r in dielectric if r['variant']==variant and r['source']==source]
  for density in ['model']+(['source'] if source.startswith('Agieienko') else []):
   available=[r for r in part if r['epsilon_at_'+density+'_density']!='']
   summary.append(dict(variant=variant,source=source,density_basis=density,n=len(part),available=len(available),RMSE_epsilon=math.sqrt(sum((float(r['epsilon_at_'+density+'_density'])-float(r['observed_epsilon']))**2 for r in available)/len(available))))
table('dielectric-summary.csv',summary)
