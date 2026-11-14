"""Render retained DEA Part II values; no model calculation."""
import csv
import json
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from MEA.solvent_specification import deviation_statistics
AN = Path(__file__).resolve().parent
OUT = AN / 'results/retransfer-346/f2-current'
read = lambda p: json.loads(p.read_text())
rows = read(OUT / 'data-rows.json')
old = read(AN / 'results/retransfer-346/previous-current/data-rows.json')
curves = read(OUT / 'curve-data.json')
assert len(rows) == len(old) == 299 and {r['identity'] for r in rows} == {r['identity'] for r in old}
assert all(r['status'] == 'Available' for r in rows + old + curves)
def write_csv(name, records):
    with (OUT / name).open('w') as f:
        w = csv.DictWriter(f, list(records[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(records)
summary = []
for model, source in [('F2', rows), ('F0', old)]:
    for group in dict.fromkeys(r['group'] for r in source):
        ps = [r for r in source if r['group'] == group]
        summary.append(dict(model=model, group=group, role=ps[0]['role'], **deviation_statistics([(r['observed'], r['value']) for r in ps], ps[0]['unit'])))
write_csv('group-deviations.csv', summary)
range_rows = []
for model, path in [('F2', OUT), ('F0', AN / 'results/retransfer-346/previous-current')]:
    for r in read(path / 'deviations.json'):
        if r['rows']:
            range_rows.append(dict(model=model, group=r['group'], role=r['role'], law=r['range_name'], outside_range=r['outside_range'], count=r['rows'], available=r['available'], **(r['statistics'] or {})))
write_csv('range-deviations.csv', range_rows)
flat = [dict(model='F2', identity=r['identity'], group=r['group'], role=r['role'], T_K=r['T_K'], observed=r['observed'], predicted=r['value'], unit=r['unit'], outside_ranges=json.dumps(r['outside_ranges'], sort_keys=True)) for r in rows]
write_csv('paper-data.csv', flat)
write_csv('horstmann.csv', [dict(identity=r['identity'], x_water=r['row']['x_water'], T_K=r['T_K'], P_MPa=r['row']['P_MPa'], observed_J_mol=r['observed'], F2_J_mol=r['value'], F0_J_mol=next(x['value'] for x in old if x['identity']==r['identity']), role=r['role'], reaction_ranges='reaction not used') for r in rows if r['group']=='Horstmann'])
selection = read(OUT / 'selection.json')
uncertainty = read(OUT / 'conditional-uncertainty.json')
parameters = []
for index, coordinate in enumerate(uncertainty['coordinates']):
    identity = coordinate['identity']
    parameters.append(dict(parameter=identity, value=coordinate['origin'],
        unit='J/mol' if coordinate.get('kind')=='reaction_enthalpy_shift' else 'dimensionless',
        lower=coordinate['bounds'][0], upper=coordinate['bounds'][1],
        on_bound=index in uncertainty['active_bounds'],
        conditional_SE=uncertainty['conditional_standard_error'][identity],
        basis='completed-law endpoint chart; enthalpy is an increment about the completed law'))
write_csv('parameter-values.csv', parameters)
paper = dict(selected_start=selection['chosen']['name'], cost=selection['chosen']['cost'], fitted_parameters=4, conditional_standard_errors=uncertainty['conditional_standard_error'], active_bounds=uncertainty['active_bounds'], stability=selection['chosen']['search'], pressure={})
for role in ('fitted', 'not fitted'):
    ps = [r for r in rows if r['role']==role and r['unit']=='Pa']
    paper['pressure'][role] = deviation_statistics([(r['observed'],r['value']) for r in ps], 'Pa')
(OUT / 'paper-summary.json').write_text(json.dumps(paper, indent=2)+'\n')
def loading(r):
    for key in ('alpha_mol_CO2_per_mol_DEA', 'alpha_mol_CO2_per_mol_amine'):
        if key in r['row']:
            return float(r['row'][key])
    w = float(r['row']['DEA_mass_fraction'])
    water = (1-w)/0.01801528/(w/0.105137)
    x = float(r['row']['x_CO2'])
    return x/(1-x)*(1+water)
colors = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9']
fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
for ax, groups, title in zip(axes.flat, [('Lawson','Lawson-394K'),('SeoHong',),('Lal',),('Carson',)], ['Lawson: fitted; 394.26 K not fitted','Seo and Hong: not fitted','Lal: not fitted','Carson: fitted']):
    cs = [r for r in curves if r['group'] in groups]
    labels = list(dict.fromkeys(r['curve'] for r in cs))
    for index, label in enumerate(labels):
        line = sorted([r for r in cs if r['curve']==label], key=lambda r:r['loading'])
        color = colors[index % len(colors)]
        outside = line[0]['outside_ranges']['DEA-dissociation'] is True
        caption = f"{line[0]['T_K']:.2f} K"
        if groups==('Carson',):
            caption = f"{float(line[0]['row']['DEA_mass_fraction'])*100:g} wt%"
        ax.plot([r['loading'] for r in line], [r['value']/1000 for r in line], '--' if outside else '-', color=color, label=caption)
        obs = [r for r in rows if r['group'] in groups and abs(r['T_K']-line[0]['T_K'])<1e-8]
        if groups==('Carson',):
            obs = [r for r in obs if r['row']['DEA_mass_fraction']==line[0]['row']['DEA_mass_fraction']]
        ax.scatter([loading(r) for r in obs], [r['observed']/1000 for r in obs], marker='^' if outside else 'o', facecolors='none', edgecolors=color, s=25)
    ax.set(title=title, xlabel='Loading (mol CO₂/mol DEA)', ylabel='Integral heat (kJ/mol CO₂)' if groups==('Carson',) else 'CO₂ partial pressure (kPa)', yscale='linear' if groups==('Carson',) else 'log')
    ax.legend(fontsize=7, ncol=2)
fig.suptitle('DEA on F2: measurements and model curves\nTriangles and dashed curves exceed the Bower dissociation range; hydrolysis source range unknown', fontsize=11)
fig.savefig(OUT / 'measured-model.png', dpi=170)
plt.close(fig)
fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
for ax, group, xlabel, xkey, scale in [(axes[0],'Horstmann','Water mole fraction','x_water',1),(axes[1],'Cai','Water mole fraction','x_water',0.001)]:
    ps = [r for r in rows if r['group']==group]
    ax.scatter([float(r['row'][xkey]) for r in ps], [r['observed']*scale for r in ps], facecolors='none', edgecolors='#0072B2', label='Measured')
    ax.scatter([float(r['row'][xkey]) for r in ps], [r['value']*scale for r in ps], marker='x', color='#D55E00', label='F2 model')
    ax.set(title=f'{group}: comparison only; reactions not used', xlabel=xlabel, ylabel='Excess enthalpy (J/mol mixture)' if group=='Horstmann' else 'Bubble pressure (kPa)')
    ax.legend(fontsize=8)
fig.savefig(OUT / 'binary-comparisons.png', dpi=170)
plt.close(fig)
print('Retained tables and figures rendered', flush=True)
