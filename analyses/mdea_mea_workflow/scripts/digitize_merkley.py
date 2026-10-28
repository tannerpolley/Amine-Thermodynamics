"""Calibrated Figure 3 marker extraction using the installed CSE XY helper."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.path.insert(0,'/tmp/mdea222-deps')
helper=Path('/home/tnnrpolley21/.codex/plugins/cache/cse/cse/local/skills/digitize/scripts/digitize_xy_plot.py')
spec=importlib.util.spec_from_file_location('xy',helper);xy=importlib.util.module_from_spec(spec);spec.loader.exec_module(xy)
AN=Path(__file__).resolve().parents[1]
axis=dict(x1_pixel=[289,488],x1_value=20,x2_pixel=[550,488],x2_value=60,y1_pixel=[157,488],y1_value=-40,y2_pixel=[157,139],y2_value=-70,x_scale='linear',y_scale='linear')
centres={288.71:[[289,403],[419,380],[550,362]],333.15:[[289,334],[419,309],[550,293]],388.71:[[289,265],[419,231],[550,218]],422.04:[[289,219],[419,194],[549,168]]}
rows=[];image=None
for T,points in centres.items():
 for w,(px,py) in zip([20,40,60],points):
  config=dict(axis=axis,roi=[px-6,py-6,px+7,py+7],series=[dict(name=f'{T}K_{w}wt',mode='points',min_area=1,gray_threshold=160)])
  path=AN/'inputs/merkley-calibration.json'
  path.write_text(json.dumps(config))
  image,found,_=xy.digitize(AN/'inputs/merkley-figure3.png',path)
  assert found
  nearest=min(found,key=lambda r:(r['pixel_x']-px)**2+(r['pixel_y']-py)**2)
  assert abs(nearest['pixel_y']-py)<3
  rows.append(dict(source_key='Merkley1987',pdf_attachment_key='ED7IMI2E',source_locator='Figure 3; PDF p.5 printed p.441',temperature_K=T,MDEA_mass_percent=w,heat_kJ_mol_CO2=round(nearest['y'],1),digitization_uncertainty_kJ_mol_CO2=.3,source_relative_uncertainty=.05,heat_definition='sub-saturation slope of integral heat per mol MDEA vs loading',candidate_pressure_1_kPa=156 if T<350 else (1121 if T<400 else 1466),candidate_pressure_2_kPa=1121 if T<350 else '',pressure_ambiguity='Figure 3 does not identify which of the two Table 1 pressures' if T<350 else 'Table 1 identifies only one pressure at this temperature',proposed_pressure_kPa=1121 if T<400 else 1466,pressure_rule_status='owner-freeze proposal; low-temperature alternative retained',**nearest))
xy._draw_overlay(image,rows,AN/'results/merkley-overlay.png')
path=AN.parents[1]/'data/reference/MDEA/Merkley1987_stage1.csv'
with path.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
(AN/'inputs/merkley-calibration.json').write_text(json.dumps(dict(axis=axis,manually_selected_centres=centres,roi_half_width_pixels=6,threshold=160,helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),image_sha256=hashlib.sha256((AN/'inputs/merkley-figure3.png').read_bytes()).hexdigest(),render='pdftoppm -f 5 -l 5 -scale-to 1600 -png -singlefile; original full-page image preserved',qa='review: overlay checked against all 12 markers; ±0.3 kJ/mol digitization estimate; pressure-specific repeated experiments not separately printed; no loadings supplied for plateau values'),indent=2)+'\n')
manifest=AN.parents[1]/'data/reference/MDEA/stage1-sources.json'
d=json.loads(manifest.read_text());m=next(m for m in d['sources'] if m['source_key']=='Merkley1987');m['files']=[dict(path=str(path.relative_to(AN.parents[1])),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rows=12)];m['check']='12 calibrated Figure 3 markers with QA overlay; Table 1 low-temperature runs use both 156 and 1121 kPa, differing up to 9%; Figure 3 pressure identities are ambiguous. Both candidates and proposed assignments retained; no finite loading invented.'
manifest.write_text(json.dumps(d,indent=2)+'\n')
print([(r['temperature_K'],r['MDEA_mass_percent'],r['heat_kJ_mol_CO2']) for r in rows])
