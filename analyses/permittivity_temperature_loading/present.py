"""Render retained permittivity sensitivities; never evaluates the model."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AN = Path(__file__).resolve().parent
summary = json.loads((AN / 'results/summary.json').read_text())
base = summary['scenarios'][0]
rows = []
baseline = json.loads((AN / 'results/baseline/diagnostics.json').read_text())
ids = [c['component_id'] for c in json.loads((AN.parent / 'solvent_specification_mea/inputs/endpoint.json').read_text())['components']]
for scenario in summary['scenarios']:
    diagnostics = json.loads((AN / 'results' / scenario['name'] / 'diagnostics.json').read_text())
    for T, state in diagnostics.items():
        for quantity, value in state.get('quantities', {}).items():
            reference = baseline[T]['quantities'][quantity]
            rows.append(dict(scenario=scenario['name'], T_K=T, quantity=quantity, value=value['value'],
                             baseline=reference['value'], status=value['status'], requested_tolerance_met=value['requested_tolerance_met'],
                             relative_change=None if value['status'] != 'Available' or reference['status'] != 'Available' else value['value'] / reference['value'] - 1))
        for cid, value, reference in zip(ids, state['mole_fractions'][:len(ids)], baseline[T]['mole_fractions'][:len(ids)], strict=True):
            rows.append(dict(scenario=scenario['name'], T_K=T, quantity='liquid_x/' + cid, value=value, baseline=reference,
                             status='Available' if state['success'] else 'Unavailable', requested_tolerance_met=state['requested_tolerance_met'],
                             relative_change=value / reference - 1))
        bubble = state.get('bubble', {})
        reference = baseline[T].get('bubble', {})
        rows.append(dict(scenario=scenario['name'], T_K=T, quantity='bubble_pressure_Pa', value=bubble.get('pressure'),
                         baseline=reference.get('pressure'), status='Available' if bubble.get('success') else 'Unavailable',
                         requested_tolerance_met=bubble.get('requested_tolerance_met'),
                         relative_change=bubble['pressure'] / reference['pressure'] - 1 if bubble.get('success') and reference.get('success') else None))
with (AN / 'results/plotted-values.csv').open('w') as h:
    writer = csv.DictWriter(h, list(rows[0])); writer.writeheader(); writer.writerows(rows)
fig, axes = plt.subplots(1, 3, figsize=(12, 4), layout='constrained')
for ax, quantity, label in zip(axes, ['bubble_pressure_Pa', 'phase_density', 'equilibrium_isobaric_heat_capacity'],
                                ['Bubble pressure', 'Liquid density', 'Equilibrium heat capacity'], strict=True):
    for T, marker, color in [('353.0', 'o', '#0072B2'), ('393.0', 'x', '#D55E00')]:
        selected = [r for r in rows if r['quantity'] == quantity and r['T_K'] == T and r['scenario'].startswith(T[:-2] + '-') and r['relative_change'] is not None]
        ax.scatter([r['scenario'].split('-', 1)[1] for r in selected], [100*r['relative_change'] for r in selected], marker=marker, color=color, label=T + ' K')
    ax.axhline(0, color='0.6', linewidth=.6); ax.set_ylabel(label + ' change (%)')
    ax.tick_params(axis='x', rotation=60); ax.legend(); ax.grid(axis='y', alpha=.2)
fig.savefig(AN / 'sensitivity.png', dpi=170)
lines = ['| Scenario | Available / 307 | Available-row cost | Descent / 162 | Incomplete / 162 |', '|---|---:|---:|---:|---:|']
for r in summary['scenarios']:
    lines.append(f"| {r['name']} | {r['available']} | {r['available_cost']:.8g} | {r['phase']['resolved_descent_states']} | {r['phase']['incomplete_states']} |")
(AN / 'results/scenario-table.md').write_text('\n'.join(lines) + '\n')

source = json.loads((AN / 'results/source-comparison.json').read_text())
fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), layout='constrained')
for ax, T in zip(axes, ['293.15', '353.15'], strict=True):
    selected = [r for r in source if r['source'] == 'HajjLoaded2024' and r['T_K'] == T]
    for key, marker, color, label in [('epsilon', 'o', '#D55E00', 'Hajj inferred static limit'), ('calculated_epsilon', 'x', '#0072B2', 'Current law + speciation')]:
        ax.scatter([float(r['loading']) for r in selected], [float(r[key]) for r in selected], marker=marker, color=color, label=label)
    ax.set(xlabel='Loading (mol CO₂/mol MEA)', ylabel='Relative permittivity', title=T + ' K; 30 wt% MEA stock')
    ax.legend(fontsize=8); ax.grid(alpha=.2)
fig.savefig(AN / 'source-comparison.png', dpi=170)

mdea = json.loads((AN / 'results/mdea/summary.json').read_text())
lines = ['| Model | Group | Matched / requested | Nonzero terms | AARD (%) | Baseline matched AARD (%) |', '|---|---|---:|---:|---:|---:|']
for scenario in mdea['scenarios']:
    for group, value in scenario['groups'].items():
        lines.append(f"| {scenario['name']} | {group} | {value['matched_available']} / {value['rows']} | {value['nonzero_terms']} | {format(value['AARD_percent'], '.6g') if value['AARD_percent'] is not None else 'unavailable'} | {format(value['baseline_matched_AARD_percent'], '.6g') if value['baseline_matched_AARD_percent'] is not None else 'unavailable'} |")
(AN / 'results/mdea/table.md').write_text('\n'.join(lines) + '\n')
