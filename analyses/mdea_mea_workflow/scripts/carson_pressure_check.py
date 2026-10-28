"""Owner-declared Carson integral-heat pressure sensitivity on the pinned wheel."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import importlib.util,json,math,csv,zipfile
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('admission',AN/'scripts/admission_probe.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);p=a.p;eq=p.eq
runtime=json.loads((AN/'inputs/runtime.json').read_text());wheel=Path(runtime['wheel']);assert p.sha(wheel)==runtime['wheel_sha256']==p.shared.ENGINE_WHEEL_SHA256
with zipfile.ZipFile(wheel) as z:
 files=[n for n in z.namelist() if n.startswith('epcsaft/') and not n.endswith('/')]
 assert all((Path(p.epcsaft.__file__).parent.parent/n).read_bytes()==z.read(n) for n in files)
source=next(s for s in json.loads((p.DATA/'stage1-sources.json').read_text())['sources'] if s['source_key']=='Carson2000')
pdf=next((Path('/home/tnnrpolley21/Zotero/storage')/source['pdf_attachment_key']).glob('*.pdf'))
assert p.sha(pdf)==source['pdf_sha256']
runtime.update(installed_files_checked=len(files),Carson_pdf_sha256=p.sha(pdf),Carson_pdf_attachment_key=source['pdf_attachment_key'])
p.write('results/stage2-runtime.json',runtime)
recs=json.loads((AN/'inputs/probe-reaction-reference.json').read_text())['shared']
reactions=[eq.Reaction({cid:v for cid,v in zip(p.shared.COMPONENT_IDS,r['stoichiometry']) if v},name=r['reaction_id'],correlation=p.shared._reaction_correlation(r,r['reaction_id']),reference=p.shared._reaction_reference(r,r['reaction_id'])) for r in recs]
ref=p.shared.COMMON_SOURCE_STANDARD_STATE_ID
reactions.append(eq.Reaction({p.H:-1,p.W:-1,p.M:1,'hydronium-cation':1},name='MDEA-dissociation',correlation=eq.ReactionLogPolynomial(-83.491+4.0165+10.976*math.log(313.15),-819.7,10.976,0.,313.15,278.,393.15,ref),reference=eq.ReactionReference(eq.ReferenceSourceBasis.CommonMolalityInfiniteDilution,1e5)))
rows=list(csv.DictReader((p.DATA/'Carson2000_stage1.csv').open()))
for r in rows:
 w=float(r['MDEA_mass_fraction']);nw=.1191622*(1-w)/w/.01801528;x=float(r['x_CO2']);r['alpha']=x/(1-x)*(1+nw);r['water']=nw
largest=max(rows,key=lambda r:r['alpha'])
print('largest',largest,flush=True)
records=[]
for variant in 'AB':
 d=json.loads((AN/f'inputs/variant-{variant}.json').read_text());params=p.epcsaft.Parameters.from_mapping(d);model=p.epcsaft.Mixture(params,thermochemistry=a.caloric_record(params))
 def problem(row,alpha,P):
  return eq.Problem(T=298.15,P=P,feed=eq.Amounts({p.W:row['water'],p.M:1.,p.C:alpha}),phases=[eq.Phase('L',kind='liquid',support=p.published.SPECIES)],reactions=reactions,neutral_reference=p.published.NEUTRAL_REFERENCE,row_tolerance=1e-10)
 results=[]
 for P in (101325.,265000.):
  initial=problem(largest,0.,P);final=problem(largest,largest['alpha'],P)
  item=p.reg.addition_enthalpy(params,initial,final,{p.C:1.},largest['alpha'],298.15,P,phase='vapor',observed=float(largest['solution_enthalpy_kJ_mol_CO2'])*1000,form='difference',scale=3000.)
  value=p.reg.predict(model,item)
  results.append(dict(P_Pa=P,prediction=p.conversion.jsonable(value)))
 change=abs(results[1]['prediction']['value']/results[0]['prediction']['value']-1)
 records.append(dict(variant=variant,start='1',pressure_results=results,relative_change=change,pressure_check_pass=change<=.005))
 print(variant, 'relative change',change,flush=True)
 p.write('results/carson-pressure-check.json',dict(largest_loading_row=largest,rows=records,limit_relative=.005,pressure_convention_Pa=101325.,alternative_Pa=265000.,note='Declared owner convention 2026-10-28; not source-reported pressure. Start-1 check; endpoint check remains required.'))
