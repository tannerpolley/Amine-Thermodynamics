"""Check the retained one-factor evidence against the frozen primary inputs."""
import csv,gzip,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));import probe
import epcsaft
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
e=json.load(open(P/'execution.json'));assert epcsaft.provenance()[1]==e['wheel_sha256']
assert sha(P.parent/'row-results.json')==e['primary_rows_sha256']
source=[]
for r in json.load(open(P.parent/'sources.json'))['pdfs']:
 actual=sha(r['path']);assert actual==r['sha256'];source.append(dict(path=r['path'],sha256=actual))
shelf=Path('/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/literature')
for r in csv.DictReader(open(shelf/'index.csv')):
 if r['citation_key'] in ['Bulow2021a','Held2014']:
  # Shelf's file column names are read from the retained index.
  assert sha(shelf/r['local_file'])==r['sha256']==sha(r['source_path'])
  source.append(dict(path=r['source_path'],sha256=r['sha256']))
rows=list(csv.DictReader((probe.primary.p.ROOT/'data/reference/MDEA/Kuranov_1996_CO2_MDEA_total_pressure.csv').open()))
inv=json.load(open(P.parent/'inventory.json'));ids={i for g in inv['isotherms'] for i in g['source_rows']};rows=[r for r in rows if int(r['source_row']) in ids]
inputs={}
for name in probe.PROBES:
 result=json.load(open(P/(name+'-rows.json')));assert {r['source_row'] for r in result}==ids
 assert {r['source_row'] for r in result if r.get('not_retried')}==probe.SKIP
 assert sum(r['qualified'] for r in result)==63
 inputs[name]={r['source_row']:probe.document(name,float(r['temperature_K'])) for r in rows}
 assert all(r.get('max_equilibrium_residual',0)<=1e-10 for r in result)
# Confirm the Held source PDF as well as its current companion.
held_pdf=next(Path('/home/tnnrpolley21/Zotero/storage/TD5T732H').glob('*.pdf'))
source.append(dict(path=str(held_pdf),sha256=sha(held_pdf)))
# The documented exact previous figure failure must stay inside the corrected image bound.
f=list(csv.DictReader(open(P/'figure4-lines.csv')));q=min((r for r in f if r['T_K']=='373'),key=lambda r:abs(float(r['loading'])-.4991535423));assert 194<=float(q['y_pixel'])<=197
# All marker-crossing interpolation differences lie inside the stated bound.
meta=json.load(open(P/'figure4-metadata.json'));assert all(r['max_crossing_lane_difference_pixels']<meta['uncertainty']['y_pixels'] for r in meta['curves'])
with gzip.open(P/'input-documents.json.gz','wt') as f:f.write(json.dumps(inputs,indent=2)+'\n')
(P/'verification.json').write_text(json.dumps(dict(primary_rows_unchanged=True,source_hashes=source,probe_qualified_counts={n:63 for n in probe.PROBES},not_retried=sorted(probe.SKIP),figure4_previous_failure_y_pixel=float(q['y_pixel']),crossing_max_pixel_difference=max(r['max_crossing_lane_difference_pixels'] for r in meta['curves']),input_documents_sha256=sha(P/'input-documents.json.gz'),code_sha256={n:sha(P/n) for n in ['probe.py','compare.py','digitize.py','present.py','verify.py']}),indent=2)+'\n')
