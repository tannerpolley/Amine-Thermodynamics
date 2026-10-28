"""Merkley (1987), Fig. 4, printed p.442: calibrated loading-point markers."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, '/tmp/mdea222-deps')
helper = Path('/home/tnnrpolley21/.codex/plugins/cache/cse/cse/local/skills/digitize/scripts/digitize_xy_plot.py')
spec = importlib.util.spec_from_file_location('xy', helper)
xy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xy)
AN = Path(__file__).resolve().parents[1]
DATA = AN.parents[1] / 'data/reference/MDEA'
axis = dict(x1_pixel=[238, 652], x1_value=275, x2_pixel=[950, 652], x2_value=450,
            y1_pixel=[238, 652], y1_value=0, y2_pixel=[238, 169], y2_value=1.5,
            x_scale='linear', y_scale='linear')
# Centres read visually from the rendered source, including open-marker interiors.
centres = {288.71: [[295, 240], [295, 289], [295, 297]],
           333.15: [[475, 327], [475, 349], [475, 391]],
           388.71: [[699, 463], [699, 536], [699, 594]],
           422.04: [[836, 562], [836, 603], [836, 627]]}
transform = xy.AxisTransform(axis)
image = xy.cv2.imread(str(AN / 'inputs/merkley-figure4.png'))
assert image is not None
rows = []
for T, points in centres.items():
    for wt, (px, py) in zip((20, 40, 60), points, strict=True):
        x, alpha = transform.pixel_to_data(px, py)
        assert abs(x - T) < 1
        rows.append(dict(temperature_K=T, MDEA_mass_percent=wt,
                         pressure_kPa=1466 if T > 400 else 1121,
                         alpha_LP_mol_CO2_per_mol_MDEA=round(alpha, 3),
                         digitization_uncertainty_mol_CO2_per_mol_MDEA=0.02,
                         pixel_x=px, pixel_y=py, digitized_temperature_K=x))
check = next(r for r in rows if r['temperature_K'] == 388.71 and r['MDEA_mass_percent'] == 40)
assert abs(check['alpha_LP_mol_CO2_per_mol_MDEA'] - .35) <= .02
with (DATA / 'Merkley1987_loading_points.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
xy._draw_overlay(image, rows, AN / 'results/merkley-loading-overlay.png')
assigned = []
for heat in csv.DictReader((DATA / 'Merkley1987_stage1.csv').open()):
    loading = next(r for r in rows if r['temperature_K'] == float(heat['temperature_K'])
                   and r['MDEA_mass_percent'] == float(heat['MDEA_mass_percent']))
    assigned.append(dict(**loading, heat_kJ_mol_CO2=float(heat['heat_kJ_mol_CO2']),
                         role='fit' if loading['MDEA_mass_percent'] < 60 else 'outside-fit',
                         endpoint_rule='alpha_LP', flatness_endpoint_rule='alpha_LP/2'))
    if loading['temperature_K'] < 350:
        assigned.append(dict(assigned[-1], pressure_kPa=156, role='alternative-pressure',
                             endpoint_rule='min(alpha_LP, model saturation loading at 156 kPa)'))
assert len(rows) == 12 and len(assigned) == 18
pdf = next(Path('/home/tnnrpolley21/Zotero/storage/ED7IMI2E').glob('*.pdf'))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(pdf) == '35f5b41c6c48cba5c555588accc2f8e25679907a7142de0da401fc97692878aa'
metadata = dict(item='j', status='pass', visual_QA='Native-resolution overlay inspected: all twelve centres coincide with their source markers; open circle 20 wt%, open square 40 wt%, filled square 60 wt%', pdf_attachment_key='ED7IMI2E',
                pdf_sha256=sha(pdf), locator='Figure 4, PDF p.6, printed p.442',
                render='pdftoppm -f 6 -l 6 -scale-to 2000 -png -singlefile',
                image_sha256=sha(AN / 'inputs/merkley-figure4.png'), axis=axis,
                method='Manual marker centres transformed with CSE digitize_xy_plot.AxisTransform; no line interpolation',
                helper_sha256=sha(helper),
                uncertainty='Conservative absolute reading allowance ±0.02 mol CO2/mol MDEA, not a statistical confidence interval or source measurement uncertainty. Marker half-width about 6 pixels (0.019 loading); includes axis placement and scan skew.',
                independent_check=dict(printed=.35, digitized=check['alpha_LP_mol_CO2_per_mol_MDEA'],
                                       difference=check['alpha_LP_mol_CO2_per_mol_MDEA']-.35,
                                       locator='Fig.2 discussion, printed p.442'),
                limitations='One independent printed loading check; remaining markers checked visually. Source reports no loading-point uncertainty. Alternative endpoints depend on fitted model and are retained as rules, not invented numbers.',
                rows=rows, assignments=assigned)
(AN / 'results/merkley-loading-points.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(json.dumps(rows, indent=2))
