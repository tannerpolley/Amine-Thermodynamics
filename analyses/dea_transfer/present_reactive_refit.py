"""Present retained #425 DEA comparisons without calculating a model."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reactive_readback import BINARY, HEAT, REFERENCE, read


def table(title, labels, rows):
    lines = [f'| {" | ".join(labels)} |', '| ' + ' | '.join(['---']*len(labels)) + ' |']
    lines.extend('| ' + ' | '.join(map(str, row)) + ' |' for row in rows)
    return f'### {title}\n\n' + '\n'.join(lines) + '\n'


def comparison(name, record):
    def formatted(rs):
        n = rs['available']
        return f'{n}, {rs["AARD_percent"]:.3f}, {rs["bias_percent"]:+.3f}' if n else '0, —, —'
    return [name, *(formatted(record[side]) for side in ('paired_reference','paired_candidate'))]


def span(values):
    if values is None:
        return '—'
    return '–'.join(dict.fromkeys(f'{v:.5g}' for v in values))


def present(out):
    data = read(out/'comparisons.json')
    run = out/'run'
    stability = read(run/'stability-readback.json')
    costs = data['objective']
    selection = read(run/'selection.json')
    chosen = selection['chosen']
    headings = ['Quantity or dataset', '#413, n / AARD / bias (%)', '#425, n / AARD / bias (%)']
    text = [
        table('Reactive objective', ['Group', '#413', '#425'],
              [(k, *(f'{costs[s][k]:.10g}' for s in ('reference','candidate'))) for k in costs['candidate']]
              + [('Total', *(f'{sum(costs[s].values()):.12f}' for s in ('reference','candidate')))]),
        table('Table 7 pressure readback', headings,
              [comparison(k.replace('_',' ').replace('binary calibration pressure', '#425 binary calibration pressures replayed for both models').replace('pooled calibration pressures', '#425 pooled calibration pressures replayed for both models'), r) for k,r in data['table7'].items()]),
        table('Loaded CO₂ pressure by temperature band', headings,
              [comparison(f"{r['band']}, {r['role']}", r) for r in data['pressure_bands']]),
        table('Table S10 group errors', [headings[0], 'Stage and role', 'Observed / available / relative-error denominator',
              'Temperature (K)', 'Unloaded composition', 'CO₂ loading', 'Outside R4 / R5', '#413, available n / AARD / bias (%)', '#425, available n / AARD / bias (%)'],
              [[r['group'], f"{r['stage']}, {r['role']}" if r['stage'] != 'binary' or r['role'] != 'fitted' else ('binary, #425 calibration; #413 calibration' if r['group'] == 'Horstmann VLE' else 'binary, #425 calibration; #413 comparison'),
                ' / '.join(str(r['candidate'].get(k, 0)) for k in ('observed', 'available', 'relative_rows')),
                span(r['temperature_K']),
                f"{span(r['unloaded_composition'])} ({r['unloaded_composition_basis']})",
                span(r['loading_mol_CO2_per_mol_DEA']),
                ' / '.join('—' if 'reaction not used' in r[k] else str(r[k].get('True', 0)) for k in ('R4','R5')),
                *comparison(r['group'], r)[1:]]
               for r in data['tableS10']]),
        table('Horstmann pressure in water-rich mixtures', headings,
              [comparison(r['x_water'], r) for r in data['process_range']]),
    ]
    lines = []
    for name, row in stability['sections'].items():
        lines.append([name, row['states'], row['available'], len(row['unavailable']), len(row['vapor_descents']),
                      len(row['liquid_descents']), len(row['confirmed']), len(row['unconfirmed_liquid'])])
    text.append(table('Selected reactive stability searches',
                      ['States', 'Searched', 'Available', 'Unfinished', 'Vapor descent', 'Liquid descent',
                       'Confirmed split', 'Unconfirmed liquid descent'], lines))
    coords = chosen['parameters']['coordinates']
    uncertainty = read(run/'conditional-uncertainty.json')
    previous = read(REFERENCE/'conditional-uncertainty.json')
    old = read(REFERENCE/'selection.json')['chosen']
    coordinate_rows = [(q['identity'], q['origin'], q['bounds']) for q in coords[:3]]
    coordinate_rows.append((coords[3]['identity'], chosen['optimizer_report']['endpoint_shifts']['carbamate-hydrolysis'],
                            chosen['optimizer_report']['declared'][3]['bounds']))
    old_values = [q['origin'] for q in old['parameters']['coordinates'][:3]]
    old_values.append(old['optimizer_report']['endpoint_shifts']['carbamate-hydrolysis'])
    text.append(table('Reactive coordinates', ['Quantity', '#413', '#425', 'Lower, upper', '#425 bound', 'Conditional SE #413 / #425'],
                 [[name + (' (J/mol)' if name == 'hydrolysis-enthalpy-shift' else ''), f'{p:.8g}', f'{q:.8g}', ', '.join(f'{b:.8g}' for b in bounds),
                   'lower' if i in uncertainty['active_bounds'] else 'interior',
                   ' / '.join(f'{se:.6g}' if (se := u['conditional_standard_error'].get(name)) is not None else '—'
                              for u in (previous, uncertainty))]
                  for i, ((name, q, bounds), p) in enumerate(zip(coordinate_rows, old_values, strict=True))]))
    (out/'comparison.md').write_text('\n'.join(text).rstrip()+'\n')

    binary = read(BINARY)
    candidate = binary['rows']
    baseline = read(BINARY.parents[1]/'413-comparison.json')
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    for ax, group, unit in zip(axes, (HEAT, 'Cai VLE'), ('Excess enthalpy (J/mol mixture)', 'Bubble pressure (kPa)'), strict=True):
        rows = [r for r in candidate if r['group'] == group]
        ax.scatter([r['x'] for r in rows], [r['observed'] for r in rows], facecolors='none', edgecolors='black', label='Measured')
        for source, label, marker, color in [(baseline, '#413', '+', '#0072B2'), (candidate, '#425', 'x', '#D55E00')]:
            rows = [r for r in source if r['group'] == group]
            ax.scatter([r['x'] for r in rows], [r['predicted'] for r in rows], marker=marker, color=color, label=label)
        ax.set(xlabel='Liquid water mole fraction', ylabel=unit, title=group)
        ax.legend()
    fig.savefig(out/'fig-8-comparison.png', dpi=170)


if __name__ == '__main__':
    present(Path(sys.argv[1]))
