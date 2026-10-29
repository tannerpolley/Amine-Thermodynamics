"""Compare retained convention probes, measured pressures and model-line pixels."""
import csv,json,math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
base={r['source_row']:r for r in json.load(open(P.parent/'row-results.json'))};inv=json.load(open(P.parent/'inventory.json'))['isotherms']
sets={'primary':list(base.values())};sets.update({f.name.removesuffix('-rows.json'):json.load(open(f)) for f in sorted(P.glob('*-rows.json'))})
summary=[];signed=[];curve=[]
fig=list(csv.DictReader((P/'figure4-lines.csv').open()))
for name,rows in sets.items():
 rr={r['source_row']:r for r in rows}
 for g in inv:
  ids=[i for i in g['source_rows'] if rr[i]['qualified'] and base[i]['qualified']];ard=np.mean([rr[i]['ARD_row_percent'] for i in ids]);bp=np.mean([base[i]['ARD_row_percent'] for i in ids])
  summary.append(dict(probe=name,nominal_MDEA_wt_percent=g['nominal_wt_percent'],T_K=g['nominal_T_K'],N=g['N'],qualified=len(ids),ARD_qualified_subset_percent=float(ard),primary_same_subset_ARD_percent=float(bp),delta_ARD_percentage_points=float(ard-bp),SI_S3_ARD_percent=g['SI_S3_percent'],delta_from_SI_percentage_points=float(ard-g['SI_S3_percent']),ARD_pressure_vs_primary_percent=float(np.mean([100*abs(rr[i]['P_Pa']/base[i]['P_Pa']-1) for i in ids])),complete=len(ids)==g['N'],inside_window=bool(len(ids)==g['N'] and g['interval_percent'][0]<=ard<=g['interval_percent'][1])))
 for r in rows:
  i=r['source_row'];b=base[i];out=dict(probe=name,source_row=i,qualified=r['qualified'],T_K=b['T_K'],m_MDEA=b['m_MDEA'],loading=b['m_CO2']/b['m_MDEA'])
  if r['qualified']:
   z=math.log(r['P_Pa']/r['observed_P_Pa']);zb=math.log(b['P_Pa']/b['observed_P_Pa']);out.update(signed_log_pressure=z,primary_signed_log_pressure=zb,delta_signed_log_pressure=z-zb,P_Pa=r['P_Pa'],yCO2_P_Pa=r['yCO2_P_Pa'])
   if b['m_MDEA']<3:
    T=min([313,333,373,393],key=lambda t:abs(t-b['T_K']));f=[v for v in fig if int(v['T_K'])==T];x=np.array([float(v['loading']) for v in f]);y=np.array([float(v['y_pixel']) for v in f]);a=out['loading']
    if min(x)<=a<=max(x):
     yp=float(np.interp(a,x,y));c=10**((281-yp)/148)*1e5
     curve.append(dict(probe=name,source_row=i,T_K=T,actual_T_K=b['T_K'],loading=a,curve_P_Pa=c,total_P_Pa=r['P_Pa'],yCO2_P_Pa=r['yCO2_P_Pa'],total_relative_error_percent=100*(r['P_Pa']/c-1),partial_relative_error_percent=100*(r['yCO2_P_Pa']/c-1),image_vertical_bound_percent=100*(10**(5/148)-1)))
  signed.append(out)
def csvout(name,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with (P/name).open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
csvout('isotherm-comparison.csv',summary);csvout('signed-log-pressure.csv',signed);csvout('figure4-comparison.csv',curve)
(P/'summary.json').write_text(json.dumps(dict(isotherms=summary,curve_comparisons=curve),indent=2)+'\n')
print(summary[:2]);print('row23',[r for r in curve if r['probe']=='primary' and r['source_row']==23])
