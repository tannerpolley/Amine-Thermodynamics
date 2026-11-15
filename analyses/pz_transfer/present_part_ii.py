"""Present retained PZ Part II values; no Engine calculations or parameter adoption."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

AN = Path(__file__).resolve().parent
OUT = AN / 'results/retransfer-345'
PREVIOUS = AN / 'results/retransfer-345-previous-replay'
FIG = AN / 'figures/part-ii-345'
FIG.mkdir(exist_ok=True)


def read(path):
    return json.loads(path.read_text())


def csv_write(name, rows):
    with (OUT / name).open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def number(value):
    return '—' if value is None else f'{value:.6g}'


selection = read(OUT / 'selection.json')
chosen = selection['chosen']
if chosen is None:
    raise ValueError('No converged selected point; retain and report the individual attempt histories')
uncertainty = read(OUT / 'conditional-uncertainty.json')
coordinates = chosen['parameters']['coordinates']
parameters = []
for i, q in enumerate(coordinates):
    shift = sum(q['bounds']) / 2 if q.get('kind') == 'reaction_coordinate' else 0.
    parameters.append(dict(quantity=q['identity'],value=q['origin']-shift,
                           unit=q.get('unit','dimensionless'),role='fitted',
                           lower=q['bounds'][0]-shift,upper=q['bounds'][1]-shift,
                           on_bound=i in uncertainty['active_bounds'],
                           conditional_SE=uncertainty['conditional_standard_error'].get(q['identity']),
                           source='F2 reactive calibration; P3-P5 reported as source-law offsets'))
csv_write('parameters.csv', parameters)
fixed_blocks = [c for c in chosen['parameters']['parameters']['components'] if c['component_id']=='piperazine']
fixed_blocks += [c for c in chosen['parameters']['parameters']['pairs'] if 'piperazine' in (c['component_id_a'],c['component_id_b']) and 'water' in (c['component_id_a'],c['component_id_b'])]
fixed_blocks += [e for e in chosen['parameters']['parameters']['topology']['edges'] if e['endpoint_a']['component_id']==e['endpoint_b']['component_id']=='piperazine']
fixed = {}
def fixed_values(value):
    if isinstance(value,dict):
        if 'identity' in value and isinstance(value.get('value',{}).get('magnitude'),(int,float)):
            fixed[value['identity']] = dict(quantity=value['identity'],value=value['value']['magnitude'],unit=value['value']['unit'],role='fixed',source='Retained PZ pure/binary inputs; fixed in this reactive fit',conditional_SE=None,lower=None,upper=None)
        for child in value.values():
            fixed_values(child)
    elif isinstance(value,list):
        for child in value:
            fixed_values(child)
fixed_values(fixed_blocks)
csv_write('fixed-pz-parameters.csv',list(fixed.values()))
comparisons = []
for model, folder in [('F2', OUT), ('previous F0 A12', PREVIOUS)]:
    for r in read(folder / 'deviations.json'):
        if r['outside_range'] not in (False, True):
            continue
        stats = r['statistics'] or {}
        comparisons.append(dict(model=model,dataset=r['group'],role=r['role'],
                                reaction=r['range_name'],range='outside' if r['outside_range'] else 'inside',
                                rows=r['rows'],available=r['available'],unit=r['unit'],
                                AARD_percent=stats.get('AARD_percent'),bias_percent=stats.get('bias_percent'),
                                mean_absolute_error=stats.get('mean_abs_error'),
                                signed_error=stats.get('mean_signed_error_predicted_minus_observed')))
csv_write('deviations.csv', comparisons)
summary = dict(selected_start=chosen['name'],cost=chosen['cost'],converged=chosen['optimizer_converged'],
               fitted_parameters=len(parameters),parameters_on_bounds=sum(r['on_bound'] for r in parameters),
               stability={k:v for k,v in chosen['search']['grid'].items() if k not in ('unavailable','unavailable_searches')},
               unavailable_searches=len(chosen['search']['grid']['unavailable']),ties=selection['ties'])
summary['pressure_deviations'] = {r['group']: dict(role=r['role'],rows=r['rows'],available=r['available'],statistics=r['statistics'])
                                  for r in read(OUT / 'deviations.json')
                                  if r['unit']=='Pa' and r['range_name']=='R1' and r['outside_range'] is False}
summary['split_counts_are_lower_bounds'] = True
summary['route_absolute_tolerance_ties'] = summary.pop('ties')
summary['unpenalized_start_comparison'] = read(OUT / 'unpenalized-start-cost-comparison.json')
(OUT / 'summary-row.json').write_text(json.dumps(summary,indent=2)+'\n')
lines = ['| Dataset | Role | Model | Reaction | Range | Rows / available | AARD (%) | Bias (%) | Mean absolute error | Signed error | Unit |',
         '|---|---|---|---|---|---:|---:|---:|---:|---:|---|']
for r in comparisons:
    if r['rows']:
        lines.append(f"| {r['dataset']} | {r['role']} | {r['model']} | {r['reaction']} | {r['range']} | {r['rows']} / {r['available']} | {number(r['AARD_percent'])} | {number(r['bias_percent'])} | {number(r['mean_absolute_error'])} | {number(r['signed_error'])} | {r['unit']} |")
(OUT / 'deviations.md').write_text('\n'.join(lines)+'\n')
lines = ['| Fitted quantity | Value | Unit | Conditional SE | Bounds | On bound |',
         '|---|---:|---|---:|---|---|']
for r in parameters:
    lines.append(f"| {r['quantity']} | {number(r['value'])} | {r['unit']} | {number(r['conditional_SE'])} | [{number(r['lower'])}, {number(r['upper'])}] | {r['on_bound']} |")
(OUT / 'parameters.md').write_text('\n'.join(lines)+'\n')
rows, curves = read(OUT / 'data-rows.json'), read(AN / 'results/retransfer-345-source-curves/curve-data.json')
source_comparisons = []
for model, folder in [('F2',OUT),('previous F0 A12',PREVIOUS)]:
    for r in read(folder / 'data-rows.json'):
        if r['group'] in ('Ermatchkov','Kamps') and r['status']=='Available':
            error = abs(r['value']-r['observed'])
            source_comparisons.append(dict(model=model,identity=r['identity'],dataset=r['group'],absolute_error_Pa=error,
                source_lower_bound_Pa=float(r['row']['pCO2_total_uncertainty_kPa'])*1000 if r['group']=='Ermatchkov' else 4000 if r['observed']<=4e6 else 10000,
                source_upper_bound_Pa=float(r['row']['pCO2_total_uncertainty_kPa'])*1000 if r['group']=='Ermatchkov' else 10000))
csv_write('source-uncertainties.csv',source_comparisons)
def level(group, m):
    options = (.9,2.,2.5,3.6,5.) if group=='Hilliard' else (1.,2.,2.75,4.) if group=='Ermatchkov' else (round(m,10),)
    return min(options,key=lambda x:abs(x-m))


plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
for group in sorted({r['group'] for r in rows}):
    data = [r for r in rows if r['group']==group]
    model = [r for r in curves if r['group']==group]
    temperatures = [313.15,333.15] if group=='Hilliard' else sorted({r['T_K'] for r in model})
    panel = lambda t:min(temperatures,key=lambda x:abs(t-x))
    columns = 2 if len(temperatures)==4 else min(3,len(temperatures))
    fig, axes = plt.subplots(int(np.ceil(len(temperatures)/columns)),columns,
                             figsize=(4.1*columns,3.2*int(np.ceil(len(temperatures)/columns))),squeeze=False)
    for ax, T in zip(axes.flat,temperatures):
        series = sorted({r['curve'] for r in model if panel(r['T_K'])==T})
        levels = sorted({level(group,float(key.split('|')[-1].split()[0])) for key in series})
        labels = set()
        for j, key in enumerate(series):
            values = sorted([r for r in model if r['curve']==key],key=lambda r:r['loading'])
            m = level(group,float(key.split('|')[-1].split()[0]))
            color = plt.cm.viridis(.9*levels.index(m)/max(1,len(levels)-1))
            valid = [r['status']=='Available' and r.get('value') is not None for r in values]
            outside = any(v is True for v in values[0]['outside_ranges'].values())
            y = [r['value'] if ok else np.nan for r,ok in zip(values,valid)]
            ax.plot([r['loading'] for r in values],y,color=color,ls='--' if outside else '-',label=f'{m:g}' if m not in labels else None)
            labels.add(m)
        for r in data:
            source = r['row']
            temperature = min(temperatures,key=lambda t:abs(t-r['T_K']))
            if temperature!=T:
                continue
            a = float(source['co2_mol'])/float(source['pz_mol']) if 'co2_mol' in source else float(source['alpha_per_PZ'])
            outside = any(v is True for v in r['outside_ranges'].values())
            m = level(group,float(source['pz_mol'] if 'pz_mol' in source else source['mPZ']))
            color = plt.cm.viridis(.9*levels.index(m)/max(1,len(levels)-1))
            marker_style = dict(color=color) if outside else dict(facecolors='none',edgecolors=color)
            ax.scatter([a],[r['observed']],marker='x' if outside else 'o',s=17,**marker_style,zorder=3)
            if group=='Ermatchkov':
                ax.errorbar(a,r['observed'],yerr=float(source['pCO2_total_uncertainty_kPa'])*1000,color=color,lw=.5)
        ax.set(title=f'Near {T:g} K (source temperatures)' if group=='Hilliard' else f'{T:g} K',xlabel='Loading (mol CO₂ / mol PZ)',ylabel='Carbamate group fraction (mol/mol)' if group.startswith('NMR') else 'Total pressure (Pa)' if group=='Kamps' else 'CO₂ partial pressure (Pa)')
        if data[0]['unit']=='Pa':
            ax.set_yscale('log')
        handles, labels = ax.get_legend_handles_labels()
        ordered = sorted(zip(labels,handles),key=lambda pair:float(pair[0]))
        ax.legend([h for _,h in ordered],[label for label,_ in ordered],fontsize=6,ncol=2,frameon=False,title='PZ stock (mol/kg; nominal labels)' if group in ('Hilliard','Ermatchkov') else 'PZ stock (mol/kg)',title_fontsize=6)
    for ax in list(axes.flat)[len(temperatures):]:
        ax.set_visible(False)
    fig.suptitle(group+' ('+data[0]['role']+'): measured points and single-liquid F2 curves\n× / dashed: outside a source range; stability assessed separately',fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / (group+'.png'),dpi=180)
    plt.close(fig)
print('Retained parameter/deviation tables, summary row and measured-data/model figures',flush=True)
