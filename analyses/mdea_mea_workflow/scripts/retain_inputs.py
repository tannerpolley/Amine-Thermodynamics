"""Verify source identities and retain exact stage-1 input hashes."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
AN=ROOT/'analyses/mdea_mea_workflow'
MAIN=Path('/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'data/reference/MDEA/stage1-sources.json').read_text())
for s in manifest['sources']:
 pdf=next((Path.home()/'Zotero/storage'/s['pdf_attachment_key']).glob('*.pdf'))
 assert sha(pdf)==s['pdf_sha256']
 for f in s['files']:
  path=ROOT/f['path'];assert sha(path)==f['sha256']
  assert len(list(csv.DictReader(path.open())))==f['rows']
 assert s['uncertainty'] and s['units_and_basis'] and s['locator']
# Reading-shelf identity is checked against the live Zotero companion, not assumed from names.
reading=[]
for r in csv.DictReader((MAIN/'literature/index.csv').open()):
 if r['citation_key'] in ('Jakobsen2005','Uyan2015','Wangler2018','Pahlavanzadeh2013','Baygi2015'):
  shelf=MAIN/'literature'/r['local_file'];original=Path(r['source_path'])
  reading.append(dict(citation_key=r['citation_key'],pdf_attachment_keys=r['pdf_attachment_keys'],local_file=r['local_file'],sha256=sha(shelf),source_path=str(original),live_source_sha256=sha(original),indexed_sha256=r['sha256']))
  assert sha(shelf)==sha(original)==r['sha256'],r['citation_key']
(AN/'inputs/reading-copy-checks.json').write_text(json.dumps(reading,indent=2)+'\n')
pdf=next((Path.home()/'Zotero/storage/5467GXJK').glob('*.pdf'))
(AN/'results/derks-basis.json').write_text(json.dumps(dict(status='unscored',source='Derks2011',pdf_attachment_key='5467GXJK',pdf_sha256=sha(pdf),locator='Table 1, PDF p.5 printed p.603; abstract p.599',temperature='room temperature, no numerical value established',basis='2 kmol/m3 analytical MDEA solution; concentrations kmol/m3; loading mol CO2/mol MDEA',reason='Missing numerical temperature; no conversion to mass or mole fractions and no scoring authorized.'),indent=2)+'\n')
# Source tables have one owner; retain their hashes without analysis copies.
source_paths=[ROOT/f['path'] for s in manifest['sources'] for f in s['files']]
source_paths += [ROOT/'data/reference/MDEA'/n for n in ('Hsieh_2007_MDEA_relative_permittivity.csv','Kuranov_1996_CO2_MDEA_total_pressure.csv')]
methods=[ROOT/'analyses/mea_parameter_bundle/scripts'/n for n in ('mea_association_volume.py','fit_observations.py','fit_campaign.py','shared_evaluation.py')]
owner=ROOT/'analyses/mea_parameter_bundle/results/selected-current-best-parameters.json'
assert sha(owner)=='00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'
files=source_paths+methods+[owner]+list((AN/'scripts').glob('*.py'))+list((AN/'inputs').glob('*.json'))
(AN/'inputs/hashes.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files)) if p.name!='hashes.json'},indent=2)+'\n')
print('Source PDF/table identities, row counts and reading-copy hashes verified; retained rows:',sum(s['files'][0]['rows'] for s in manifest['sources']))
