import importlib.util,json,csv,hashlib
from pathlib import Path
import numpy as np
an=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prep',an/'scripts/prepare.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
# Replay unconverted kappa against the exact source-model reference, without fitting.
# reuse pure parameter preparation from published source, without any Engine source import
q=p.published.document();q['components']=[c for c in q['components'] if c['component_id']==p.M];q['correlations']=[c for c in q['correlations'] if c['component_id']==p.M];q['pairs']=[];q['reaction_correlations']=[]
q['topology']={k:[v for v in vals if (v['component_id']==p.M if k=='sites' else v['endpoint_a']['component_id']==p.M and v['endpoint_b']['component_id']==p.M)] for k,vals in q['topology'].items()}
p.conversion.DOCUMENT=q;p.conversion.MEA=p.M;p.conversion.EDGE='association/methyldiethanolamine/volume';p.conversion.OUT=an/'results/kappa'
refs=json.loads((an/'results/kappa/reference.json').read_text());rows=[dict(p.conversion.state(.123858,r['T_K']),reference=r) for r in refs]
p.write('results/kappa/unconverted-replay.json',rows)
f=an/'results/kappa/summary.json';j=json.loads(f.read_text());j.update(status='complete',reason='Owner accepted 2026-10-28, issue 222 Stage-1 owner decisions; fixed to eight significant figures.',unconverted_kappa=.123858,unconverted_pressure_aard_percent=100*np.mean([abs(r['p_Pa']/r['reference']['p_Pa']-1) for r in rows]),unconverted_density_aard_percent=100*np.mean([abs(r['rho_L_mol_m3']/r['reference']['rho_L_mol_m3']-1) for r in rows]));p.write('results/kappa/summary.json',j)
# Audit Carson cumulative arithmetic; retain printed values unchanged.
rows=[]
for r in csv.DictReader((p.DATA/'Carson2000_stage1.csv').open()):
 calc=float(r['enthalpy_change_J'])/float(r['n_CO2_mol'])/1000
 rows.append(dict(source_row=int(r['source_row']),printed_n_mol=float(r['n_CO2_mol']),DeltaH_over_printed_n_kJ_mol=calc,printed_heat_kJ_mol=float(r['solution_enthalpy_kJ_mol_CO2']),difference_kJ_mol=calc-float(r['solution_enthalpy_kJ_mol_CO2']),n_from_DeltaH_and_printed_heat_mol=float(r['enthalpy_change_J'])/(1000*float(r['solution_enthalpy_kJ_mol_CO2']))))
p.write('results/carson-arithmetic.json',dict(definition='Integral DeltaH/n1 from zero loading, sequential cumulative CO2 additions; printed p.1289 PDF p.5',rows=rows,count_within_0_03=sum(abs(r['difference_kJ_mol'])<=.03 for r in rows),row38_note='Printed 0.0180 mol is a source typo; arithmetic gives 0.012801 mol, not substituted into source table.'))
# Source metadata hashes follow retained source corrections.
f=p.DATA/'stage1-sources.json';j=json.loads(f.read_text())
for source in j['sources']:
 for row in source['files']:row['sha256']=hashlib.sha256((p.ROOT/row['path']).read_bytes()).hexdigest()
 if source['source_key']=='Carson2000':
  source['units_and_basis']='integral enthalpy from zero loading kJ/mol CO2; cumulative n1 mol; CO2 mole fraction; unloaded amine mass fraction'
  source['check']='Procedure printed p.1289 PDF p.5: cumulative DeltaH/n1, not derivative. 27/40 rows within 0.03 kJ/mol; rows 11-20 differ up to 0.29 due to two-significant-figure n1; rows 32/34 differ 0.03-0.04. Row 38 printed 0.0180 mol retained; -622.0/(-48.59*1000)=0.012801 mol. See results/carson-arithmetic.json.'
 if source['source_key']=='Merkley1987':source['check']='Both Table 1 candidate pressures retained at 288.71 and 333.15 K: 156 and 1121 kPa; repeats differ up to 9%; Figure 3 assignments unknown. Other temperatures have one Table 1 pressure: 1121 at 388.71 K and 1466 at 422.04 K. Proposed rule awaits owner freeze. Text -66 kJ/mol at 40 wt%, 422.04 K differs from digitized -65.3 by 0.7 kJ/mol.'
f.write_text(json.dumps(j,indent=2)+'\n')
print('kappa comparison',json.loads((an/'results/kappa/summary.json').read_text()))
