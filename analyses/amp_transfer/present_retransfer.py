"""Render retained AMP Part II comparisons; no thermodynamic calculations."""
import csv
import hashlib
import json
import sys
from pathlib import Path

from matplotlib.figure import Figure

AN = Path(__file__).resolve().parent
OUT = AN / 'results/retransfer-344' / (sys.argv[1] if sys.argv[1:] else 'campaign')
sys.path.insert(0, str(AN.parents[1] / 'src'))
from MEA.solvent_specification import deviation_statistics


def read(name):
    return json.loads((OUT / name).read_text())


def table(name, rows):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(k for row in rows for k in row)), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


provisional = not (OUT / 'selection.json').exists()
selected = None if provisional else read('selection.json')['chosen']
assert provisional or selected is not None, 'No converged AMP start is available for reporting'
point = read(read('unpenalized-reduction-point.json')['point_path']) if provisional else selected['parameters']
information = read('conditional-uncertainty.json') if not provisional or (OUT / 'conditional-uncertainty.json').exists() else None
assert information is None or information['coordinates'] == point['coordinates']
if provisional and information:
    assert read('uncertainty-point.json')['sha256'] == hashlib.sha256((OUT / read('unpenalized-reduction-point.json')['point_path']).read_bytes()).hexdigest()
original = json.loads((AN / 'inputs/retransfer-344/fitted-coordinates.json').read_text())
parameters = []
for i, q in enumerate(point['coordinates'] if information else []):
    total_shift = q.get('kind') == 'reaction_enthalpy_shift'
    lower, upper = original[i]['bounds'] if total_shift else q['bounds']
    value = lower-q['bounds'][0] if total_shift else q['origin']
    parameters.append(dict(identity=q['identity'], value=value, unit=q['unit'],
        quantity='total enthalpy shift' if total_shift else 'fitted coordinate',
        lower=lower, upper=upper, on_bound=i in information['active_bounds'],
        conditional_standard_error=information['conditional_standard_error'].get(q['identity']),
        standard_error_basis='not reported: active-bound coordinate held fixed' if i in information['active_bounds']
            else 'local linearization; residual-variance scaled; conditional on bounds and fixed model',
        role='fitted', source='#344: retained #306 coordinates, F2 diameter floor and Born ties'))
if parameters:
    component = next(c for c in point['parameters']['components'] if c['component_id'] == 'aminomethylpropanol')
    fixed = [c for c in component['coefficients'] if c['family'] in
             ('segment_count', 'segment_diameter', 'dispersion_energy_over_k')]
    edge = next(e for e in point['parameters']['topology']['edges'] if
                {e['endpoint_a']['component_id'], e['endpoint_b']['component_id']} == {'aminomethylpropanol'})
    fixed += [edge['energy_over_k'], edge['volume']]
    parameters += [dict(identity=c['identity'], value=c['value']['magnitude'], unit=c['value']['unit'],
        quantity='retained pure-AMP parameter', role='fixed', source='results/pure/summary.json: five-second',
        conditional_standard_error=None, standard_error_basis='fixed in #344', lower=None, upper=None,
        on_bound=None) for c in fixed]
    table('parameter-table.csv', parameters)
comparisons = []
ranges = json.loads((AN / 'inputs/retransfer-344/phase-2/AMP.json').read_text())['range_meanings']
for model, path in [('F2', OUT / 'deviations.json'),
                    ('F0', AN / 'results/retransfer-344/campaign/previous/deviations.json')]:
    for row in json.loads(path.read_text()):
        if row['rows']:
            basis = ranges[{'AMP-dissociation': 'AMP_dissociation', 'carbamate-hydrolysis': 'AMP_hydrolysis'}.get(row['range_name'], 'R1_R2_R3')]['basis']
            comparisons.append(dict(model=model, range_basis=basis, **{**(row['statistics'] or {}),
                **{k: v for k, v in row.items() if k != 'statistics'}}))
table('range-deviations.csv', comparisons)
starts = []
for i in range(2):
    for endpoint in ([] if provisional else read(f'start-{i}/endpoints.json')):
        report, tally = endpoint['optimizer_report'], endpoint['search']['grid']
        starts.append(dict(start=i, stage=report['scale'], cost=endpoint['cost'],
            iterations=report['iterations'], converged=endpoint['optimizer_converged'],
            disposition=endpoint['disposition'], available=tally['available'],
            unavailable=len(tally['unavailable']), descents_lower_bound=tally['descent'],
            liquid_liquid_splits_lower_bound=sum(tally['liquid_liquid_splits'].values()),
            **{f'{group}_{source}_{branch}': count for group, sources in tally['branches'].items()
               for source, branches in sources.items() for branch, count in branches.items()},
            **{'supplied_'+k: v for k, v in tally['supplied_trial_counts'].items()}))
if starts:
    table('fit-summary.csv', starts)
histories = {}
for path in sorted(OUT.glob('start-*/**/stage-*/fit.json')):
    report = json.loads(path.read_text())
    histories[str(path.relative_to(OUT))] = {k: report[k] for k in
        ('status', 'message', 'iterations', 'initial_cost', 'final_cost', 'iteration_costs')}
(OUT / 'cost-histories.json').write_text(json.dumps(histories, indent=2)+'\n')
rows, curves = read('data-rows.json'), read('curve-data.json')
if not provisional:
    summary = dict(amine='AMP', start=selected['name'], fitted_parameters=sum(p['role'] == 'fitted' for p in parameters),
        parameters_on_bounds=len(information['active_bounds']), fitted_cost=selected['cost'],
        pressure_summary_basis='Arithmetic means over Pa observations; total and CO2 partial pressures pooled; dataset values in range-deviations.csv',
        split_count_lower_bound=sum(selected['search']['grid']['liquid_liquid_splits'].values()),
        diagnostic_descents_lower_bound=selected['search']['grid']['descent'],
        branches=selected['search']['grid']['branches'], stable=selected['stable'])
    for role in ('fitted', 'not fitted'):
        summary[role+'_pressure'] = deviation_statistics([(r['observed'], r['value']) for r in rows
            if r['role'] == role and r['unit'] == 'Pa' and r['status'] == 'Available'], 'Pa')
    (OUT / 'summary-row.json').write_text(json.dumps(summary, indent=2)+'\n')
with (AN / 'inputs/retransfer-344/observation-rows.csv').open() as stream:
    inputs = {r['identity']: r for r in csv.DictReader(stream)}
assert len(rows) == 270 and all(r['status'] == 'Available' for r in rows)
assert curves and all(r['status'] == 'Available' for r in curves)
table('curve-values.csv', [dict(curve=r['curve'], loading=r['loading'], T_K=r['T_K'], value=r['value'],
    unit=r['unit'], **{'outside_'+k: v for k, v in r['outside_ranges'].items()}) for r in curves])
panels = sorted({(r['curve'].split('|')[0], float(r['curve'].split('|')[2])) for r in curves})
colors = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#8C510A']
shown = set()
fig = Figure(figsize=(15, 13), constrained_layout=True)
axes = fig.subplots(3, 3)
for ax, (dataset, water) in zip(axes.flat, panels):
    series = sorted({r['curve'] for r in curves if r['curve'].split('|')[0] == dataset
                     and float(r['curve'].split('|')[2]) == water})
    for color, name in zip(colors, series):
        line = sorted([r for r in curves if r['curve'] == name], key=lambda r: r['loading'])
        T, unit = line[0]['T_K'], line[0]['unit']
        outside = any(v is True for v in line[0]['outside_ranges'].values())
        factor = 1000 if unit == 'Pa' else 1
        measured = [r for r in rows if inputs[r['identity']]['dataset'] == dataset and r['T_K'] == T
                    and abs(float(inputs[r['identity']]['water'])-water) < 1e-8]
        assert measured, name
        shown.update(r['identity'] for r in measured)
        ax.plot([r['loading'] for r in line], [r['value']/factor for r in line],
                color=color, ls='--' if outside else '-', label=f'{T:g} K'+(' outside range' if outside else ''))
        ax.scatter([float(inputs[r['identity']]['alpha']) for r in measured],
                   [r['observed']/factor for r in measured], marker='D' if outside else 'o',
                   facecolors='none', edgecolors=color, s=23)
    ax.set(title=f"{dataset} ({measured[0]['role']})\nwater/AMP = {water:.4g} mol/mol",
           xlabel='Loading / mol CO₂ per mol AMP',
           ylabel=('CO₂ partial pressure / kPa' if dataset == 'kundu-2003' else 'Total pressure / kPa')
                  if unit == 'Pa' else 'Carbamate / analytical AMP')
    if unit == 'Pa':
        ax.set_yscale('log')
    ax.grid(alpha=.2)
    ax.legend(fontsize=7)
for ax in list(axes.flat)[len(panels):]:
    ax.set_visible(False)
assert shown == {k for k, r in inputs.items() if r['reactive'] == 'True'}
fig.suptitle(('Provisional unpenalized AMP on F2' if provisional else 'AMP on F2')+'\nMeasured observations and homogeneous model curves\nDashed lines / diamonds: outside an applicable source range; uncertainty bands not shown')
fig.savefig(OUT / 'measured-model.png', dpi=160)
