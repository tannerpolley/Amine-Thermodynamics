"""Compare retained diagnostic pressures with the frozen primary rows, Eq.28."""
import csv,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parent
base=json.loads((P.parent/'row-results.json').read_text())
groups=json.loads((P.parent/'inventory.json').read_text())['isotherms']
runs={n:json.loads((P/(n+'-rows.json')).read_text()) for n in ['solvent-normalized','126-temperature-laws']}
rows=[]
for r in base:
 row={k:r[k] for k in ['source_row','T_K','m_MDEA','m_CO2','qualified','observed_P_Pa']}
 row['loading']=r['m_CO2']/r['m_MDEA']
 if r['qualified']:
  row.update(P_Pa=r['P_Pa'],signed_log_pressure_deviation=math.log(r['P_Pa']/r['observed_P_Pa']),ARD_percent=r['ARD_row_percent'],partial_pressure_diagnostic_percent=r['pressure_label_diagnostic_percent'],epsilon=r['permittivity'][0],solvent_fraction=sum(r['x_liquid'][:2]),y_water=r['y_vapor'][0],y_MDEA=r['y_vapor'][1],y_CO2=r['y_vapor'][2])
 rows.append(row)
with (P/'signed-pressure-deviations.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)),lineterminator='\n');w.writeheader();w.writerows(rows)
summary=[]
for g in groups:
 rs=[r for r in base if r['source_row'] in g['source_rows']];ok=[r for r in rs if r['qualified']];complete=len(ok)==g['N']
 s=dict(g,qualified=len(ok),complete=complete,positive_log_count=sum(r['P_Pa']>r['observed_P_Pa'] for r in ok),negative_log_count=sum(r['P_Pa']<r['observed_P_Pa'] for r in ok),log_min=min(math.log(r['P_Pa']/r['observed_P_Pa']) for r in ok),log_max=max(math.log(r['P_Pa']/r['observed_P_Pa']) for r in ok))
 s['primary_ARD']=sum(r['ARD_row_percent'] for r in ok)/len(rs) if complete else None
 s['partial_pressure_ARD']=sum(r['pressure_label_diagnostic_percent'] for r in ok)/len(rs) if complete else None
 s['minimum_subset_ARD']=min(r['ARD_row_percent'] for r in ok) if complete else None
 for name,rr in runs.items():
  selected=[r for r in rr if r['source_row'] in g['source_rows']]
  s[name]=sum(r['ARD_row_percent'] for r in selected)/len(rs) if complete and all(r['qualified'] for r in selected) else None
 if complete and g['nominal_T_K']==393:s['zero_loading_inclusion_lower_bound_ARD']=sum(r['ARD_row_percent'] for r in ok)/(g['N']+1)
 summary.append(s)
(P/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['| MDEA / wt% | T / K | Primary | Normalized solvent | #126 laws | CO₂ partial vs total data | SI S3 |','|---|---|---|---|---|---|---|']
for s in summary:
 if s['complete']:lines.append('| '+ ' | '.join([str(s['nominal_wt_percent']),str(s['nominal_T_K'])]+[f'{s[k]:.4f}' for k in ['primary_ARD','solvent-normalized','126-temperature-laws','partial_pressure_ARD','SI_S3_percent']])+' |')
(P/'comparison.md').write_text('\n'.join(lines)+'\n')
# Interpolate digitized colored trace, retaining its marker/curve ambiguity.
trace=list(csv.DictReader((P/'figure4-373.csv').open()))
trace=[(float(r['x']),float(r['y'])) for r in trace]
figrows=[]
for r in base:
 if r['source_row'] not in range(19,28):continue
 a=r['m_CO2']/r['m_MDEA']; pair=next(((l,h) for l,h in zip(trace,trace[1:]) if l[0]<=a<=h[0]),None)
 if pair is None:continue
 l,h=pair;pressure=math.exp(math.log(l[1])+(a-l[0])/(h[0]-l[0])*math.log(h[1]/l[1]))
 figrows.append(dict(source_row=r['source_row'],loading=a,digitized_bar=pressure,primary_total_bar=r['P_Pa']/1e5,primary_partial_bar=r['yCO2_P_Pa']/1e5,observed_total_bar=r['observed_P_Pa']/1e5,primary_total_over_digitized=r['P_Pa']/1e5/pressure))
(P/'figure4-comparison.json').write_text(json.dumps(figrows,indent=2)+'\n')
assert abs(summary[2]['primary_ARD']-19.116765680576624)<1e-10
assert summary[7]['minimum_subset_ARD']>summary[7]['interval_percent'][1]
assert all(r['qualified'] for rr in runs.values() for r in rr)
print((P/'comparison.md').read_text());print(json.dumps(figrows[:3],indent=2))
