"""Extract source strings without changing their precision; retain source lineage."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'data/reference/MDEA'
AN=ROOT/'analyses/mdea_mea_workflow'
SHELF=Path('/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/literature')
SOURCES={
'Hsieh2007':('8X653CVB','Table 5, PDF p.4, printed p.622','relative permittivity; T K; MDEA mole fraction','x uncertainty 0.00015, p.619; Table 5 has no per-row permittivity uncertainty'),
'Ermatchkov2006':('UD6X5RGU','Table 6, PDF p.8, printed p.6088','total bubble pressure MPa; T K; overall molality mol/kg water','Source Table 6 prints no per-row uncertainty; corrected Kamps data; see source discussion pp.6085,6089'),
'Jakobsen2005':('XVFDEJM2','Table A5, PDF p.9, printed p.9902','species mole fractions; T degC; loadNMR mol CO2/mol amine; 23 wt% unloaded MDEA','species ratios estimated 5-10%, Experimental/Discussion; issue 222 fixes same scale; no per-row uncertainties'),
'BottingerMDEA2008':('W3HEICT5','Table 2, PDF p.6, printed p.7922','species mole fractions; initial amine g/g; loading mol CO2/mol amine; T K','amine balance <3%, CO2 <5%, p.7919'),
'Carson2000':('8ZD86YIF','Table 3, PDF p.9, printed p.1293','integral enthalpy from zero loading kJ/mol CO2; cumulative amount mol; CO2 mole fraction; unloaded amine mass fraction','estimated uncertainty 1-2%, abstract and p.1294'),
'Weiland1997':('27V9SYLA','Table 1, PDF p.1, printed p.1004','Cp J/g/K; loading mol CO2/mol amine; unloaded amine mass fraction; 298.15 K; complete loaded solution mass','repeatability and standard-system comparison 1%, p.1004'),
'Weiland1998':('U4KFM6ST','Table 1, PDF p.2, printed p.379','density g/mL; loading mol CO2/mol amine; unloaded amine mass fraction; 298.15 K; complete solution','unloaded densities within 0.1% of literature, p.378; not an explicit loaded-density uncertainty'),
'Sobrino2016':('VWXSCIWF','Table 5, PDF p.4, printed p.234','density kg/m3; T K; pressure MPa; unloaded MDEA mass fraction','standard u(T)=0.01 K, ur(p)=0.0001, u(w)=0.0001, u(rho)=0.35 kg/m3, Table 5 footnote'),
'Kim2008':('4SMCK4SC','Table 8, PDF p.4, printed p.2524','total bubble pressure kPa; T degC; liquid/vapor MDEA mole fractions','u(T)=0.05 K, u(P)=0.3 kPa, p.2526; composition uncertainty discussed pp.2526-2527'),
'Merkley1987':('ED7IMI2E','Figure 3, PDF p.5, printed p.441; Table 1 p.439','sub-saturation plateau differential enthalpy kJ/mol CO2; T K; unloaded MDEA wt%; CO2 partial pressure kPa','accuracy 5%, repeat runs within 4%, p.439')}
texts={}; manifest=[]
for name,(key,loc,units,unc) in SOURCES.items():
 pdf=next((Path.home()/'Zotero/storage'/key).glob('*.pdf'))
 text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-']).decode()
 texts[name]=text
 meta=json.load(urllib.request.urlopen('http://localhost:23119/api/users/0/items/'+key))['data']
 manifest.append(dict(source_key=name,zotero_parent_key=meta['parentItem'],pdf_attachment_key=key,pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),locator=loc,units_and_basis=units,uncertainty=unc,files=[]))


def emit(name,columns,rows,complete=True,note=''):
 meta=next(m for m in manifest if m['source_key']==name)
 p=OUT/(name+'_stage1.csv')
 with p.open('w',newline='') as f:
  w=csv.writer(f,lineterminator="\n");w.writerow(['source_key','pdf_attachment_key','source_locator','source_row',*columns])
  w.writerows([[name,meta['pdf_attachment_key'],meta['locator'],i,*r] for i,r in enumerate(rows,1)])
 meta['files'].append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rows=len(rows)))
 meta.update(status='complete' if complete else 'incomplete',check=note)

num=r'-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?'
# Hsieh aqueous block, all 24 entries; source table gives exact compositions.
b=texts['Hsieh2007'].split('Table 5.')[1].split('MDEA + H2O')[1].split('TEA + H2O')[0]
rows=[]
for line in b.splitlines():
 vals=re.findall(num,line[:80])
 if len(vals)==5 and vals[0].endswith('.15'):
  rows.extend([[vals[0],x,y] for x,y in zip(['0.2','0.4','0.6','0.8'],vals[1:])])
assert len(rows)==24
emit('Hsieh2007',['temperature_K','x_MDEA','relative_permittivity'],rows,note='24 table entries; printed columns and values checked in PDF page render.')
# Kamps corrected temperatures; only right-hand column on p.6088.
rows=[]; mol=''
page=texts['Ermatchkov2006'].split('\f')[7]
for line in page.split('Table 6.')[1].split('a Experimental')[0].splitlines():
 vals=re.findall(num,line[68:])
 if len(vals) in (3,4) and 300<float(vals[0])<400:
  if len(vals)==4: mol=vals.pop(1)
  rows.append([vals[0],mol,*vals[1:]])
rows.extend([['394.94',mol,'4.440','5.310'],['394.95',mol,'4.761','6.117']])
assert len(rows)==28,len(rows)
emit('Ermatchkov2006',['temperature_K','m_MDEA_mol_kg_water','m_CO2_mol_kg_water','total_pressure_MPa'],rows,note='28 rows; blank molality cells forward-filled only within the printed group.')
# Jakobsen source Markdown has checked explicit cell separators.
shelf=next(SHELF.glob('Jakobsen2005--*.md')).read_text()
b=shelf.split('caption{Table A5.')[1].split('end{tabular}')[0]
rows=[]
for line in b.splitlines():
 cells=[x.strip().replace('\\hline','').strip() for x in line.replace('\\\\','').split('&')]
 if len(cells)==8 and cells[0] in ('20','40'): rows.append(cells)
assert len(rows)==8
emit('Jakobsen2005',['temperature_C','maxload','loadNMR','x_CO2','x_MDEA','x_HCO3','x_CO3','x_MDEAH_printed_xAmCOO'],rows,note='Printed xAmCOO- interpreted as MDEAH+ per issue; blanks preserved; all eight charge imbalances retained separately.')
checks=[]
for r in rows:
 am,hco,co,ion=map(float,[r[4],r[5],r[6],r[7]])
 checks.append(dict(temperature_C=r[0],loadNMR=r[2],charge_imbalance_mole_fraction=ion-hco-2*co,charge_imbalance_per_amine=(ion-hco-2*co)/(am+ion)))
(AN/'results/jakobsen-charge.json').write_text(json.dumps(checks,indent=2)+'\n')
# Böttinger: left column, 52 rows over three temperature blocks.
b=texts['BottingerMDEA2008'].split('Table 2. Species Distribution')[1].split('Table 3. Species Distribution')[0]
rows=[];T=''
for line in b.splitlines():
 if 'T ) ' in line[:70]: T=re.search(r'T \) (\d+\.\d+) K',line).group(1)
 vals=re.findall(num,line[:76])
 if len(vals)==7 and re.match(r'^0\.',line): rows.append([T,*vals])
assert len(rows)>=52,len(rows)
emit('BottingerMDEA2008',['temperature_K','initial_MDEA_mass_fraction','loading','x_MDEA_H','x_DMDEA','x_HCO3_reported','x_CO2','x_byproduct'],rows,note='All rows kept. Reported HCO3 signal includes carbonate; amine signal includes protonated MDEA; no species splitting inferred.')
flags=[]
for i,r in enumerate(rows,1):
 total=float(r[3])+float(r[4])+float(r[7]); dm=float(r[4])/total; by=float(r[7])/total
 flags.append(dict(row=i,DMDEA_fraction_of_reported_amine_signals=dm,byproduct_fraction_of_reported_amine_signals=by,above_3_percent=(dm>.03 or by>.03),combined_above_3_percent=(dm+by>.03)))
(AN/'results/bottinger-flags.json').write_text(json.dumps(flags,indent=2)+'\n')
# Carson: keep printed cumulative quantities and both repeat runs.
b=texts['Carson2000'].split('TABLE 3. Partial molar')[1].split('TABLE 4.')[0]
rows=[];w='';run='1'
for line in b.splitlines():
 if 'w3 =' in line:
  w=re.search(r'w3 = (\d+\.\d+)',line).group(1);run='2' if 'Run 2' in line else '1'
 vals=re.findall(num,line.replace('−','-'))
 if len(vals)==4 and re.match(r'^\s*0\.',line):rows.append([w,run,*vals,'integral-from-zero-loading'])
assert len(rows)==40,len(rows)
emit('Carson2000',['MDEA_mass_fraction','run','n_CO2_mol','x_CO2','enthalpy_change_J','solution_enthalpy_kJ_mol_CO2','heat_definition'],rows,note='Integral DeltaH/n1 from zero loading, procedure printed p.1289 PDF p.5. Printed row 38 n1=0.0180 mol is a source typo: -622.0/(-48.59*1000)=0.012801 mol; printed values retained; arithmetic in results/carson-arithmetic.json.')
# Weiland Cp table has empty cells: read numeric columns by fixed printed positions.
b=texts['Weiland1997'].split('Table 1. Heat Capacity')[1].split('Table 2. Heat Capacity')[0]
rows=[]
for line in b.splitlines():
 if re.match(r'^.{65,85}0\.\d\d',line):
  vals=[(m.start(),m.group()) for m in re.finditer(num,line) if m.start()>=74]
  if len(vals)>=2 and 0<=float(vals[0][1])<1:
   for pos,v in vals[1:]:
    col=min(range(4),key=lambda j:abs(pos-[89,102,116,128][j]))
    rows.append([vals[0][1],['0.30','0.40','0.50','0.60'][col],v])
assert len(rows)==39,len(rows)
emit('Weiland1997',['loading','MDEA_mass_fraction','Cp_J_g_K'],rows,note='33 fitted-range and 6 extrapolation entries; 298.15 K; no blank cells fabricated.')
# Weiland density: two left-side blocks per row; parse each independently.
b=texts['Weiland1998'].split('Table 1. Density')[1].split('Table 2. Density')[0]
rows=[];w=''
for line in b.splitlines():
 left=line[:62]
 if re.search(r'\d+ mass % MDEA',left): w=re.search(r'(\d+) mass',left).group(1)
 if re.match(r'^\s*0\.\d',left) and w:
  for part in [left[:30],left[30:]]:
   vals=re.findall(num,part)
   if len(vals)>=2:rows.append([w,vals[0],vals[1]])
assert len(rows)==44,len(rows)
emit('Weiland1998',['MDEA_mass_percent','loading','density_g_mL'],rows,complete=False,note='Loaded density uncertainty s_rho not explicitly given; unloaded comparison 0.1% cannot be promoted to loaded uncertainty. No residual scale assigned.')
# Sobrino only authorized atmospheric-pressure rows.
b=texts['Sobrino2016'].split('Table 5\n')[1].split('Table 6')[0]
rows=[];w=''
for line in b.splitlines():
 if 'w1 =' in line: w=line.split('w1 =')[1].strip()
 vals=re.findall(num,line)
 if len(vals)==7 and vals[0]=='0.1': rows.extend([[w,T,vals[0],v] for T,v in zip(['293.15','313.15','333.15','353.15','373.15','393.15'],vals[1:])])
assert len(rows)==24,len(rows)
emit('Sobrino2016',['MDEA_mass_fraction','temperature_K','pressure_MPa','density_kg_m3'],rows,note='Only 0.1 MPa rows, four printed compositions, six temperatures.')
# Kim left table includes repeated isotherms, all retained.
b=texts['Kim2008'].split('Table 8. VLE Data')[1].split('Table 10.')[0]
rows=[];group=''
for line in b.splitlines():
 left=line[:62]
 if 'MDEA (1) + H2O (2),' in left:group=left.strip()
 vals=re.findall(num,left)
 if len(vals)==4 and re.match(r'^\s*(?:39|40|59|60|79|80|99|100)\.',left):rows.append([group,*vals])
emit('Kim2008',['series','temperature_C','total_pressure_kPa','liquid_x_MDEA','vapor_y_MDEA'],rows,complete=True,note='61 rows verified against all Table 8 blocks on PDF p.4; Table 10 starts on p.5 and is excluded. Source prints y above the range in issue text; y is retained and never scored.')
# Figure values cannot be replaced by the published regression, which is not observations.
next(m for m in manifest if m['source_key']=='Merkley1987').update(status='incomplete',check='Run digitize_merkley.py; Figure 3 plateau values do not specify individual finite-loading states.')
(OUT/'stage1-sources.json').write_text(json.dumps(dict(issue=222,sources=manifest),indent=2)+'\n')
print([(m['source_key'],m.get('files'),m.get('status')) for m in manifest])
