"""Present retained MEA profile and bootstrap statistics without model calls."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

AN = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
for path, digest in read(AN/'results/result-hashes.json').items():
    assert hashlib.sha256((AN/path).read_bytes()).hexdigest() == digest, path
study = read(AN/'results/study.json')
coords = read(AN/'inputs/coordinates.json')
tasks = read(AN/'inputs/tasks.json')['tasks']
profiles = [read(AN/'results'/t['identity']/'summary.json') for t in tasks if t['kind'] == 'profile']
labels = ['Carbamate–water k', 'MEAH⁺–water k', 'Bicarbonate–water k', 'Carbamate–MEAH⁺ k',
          'MEAH⁺–water slope', 'MEAH⁺ segment diameter', 'Carbamate segment diameter', 'MEAH⁺ Born diameter',
          'Carbamate Born diameter', 'R5 native b before shift', 'R2 incremental enthalpy', 'R5 incremental enthalpy',
          'MEA–water k', 'MEA–water slope', 'MEAH⁺ dispersion energy/kB', 'Carbamate dispersion energy/kB']
figures = AN/'figures'
figures.mkdir(exist_ok=True)
fig, axes = plt.subplots(4, 4, figsize=(14, 11), layout='constrained')
for q, ax, label in zip(coords, axes.flat, labels, strict=True):
    part = [s for s in profiles if s['task']['coordinate'] == q['original_index'] and s.get('coordinates') and not s.get('cause')]
    for s in part:
        phase = s.get('phase', {})
        marker = 'o' if s['inference_available'] else '^'
        color = '#D55E00' if phase.get('descent_states') else '#777777' if phase.get('incomplete_states') else '#0072B2'
        ax.scatter(s['task']['node'], s['twice_delta_cost'], marker=marker, color=color, s=22)
        if phase.get('descent_states'):
            ax.annotate(str(phase['descent_states']), (s['task']['node'], s['twice_delta_cost']), xytext=(2, 3), textcoords='offset points', fontsize=6)
    for bound in q['bounds']:
        ax.axvline(bound, color='#999999', ls=':', lw=.8)
    ax.axhline(3.84, color='black', ls='--', lw=.8)
    ax.axhline(3.929176131182156, color='#777777', ls='-.', lw=.7)
    ax.axhline(0, color='#cccccc', lw=.6)
    ax.set(title=label, xlabel=q['units'], ylabel='2(C − C reference)')
    if max([abs(s['twice_delta_cost']) for s in part], default=0) > 20:
        ax.set_yscale('symlog', linthresh=4)
    ax.tick_params(labelsize=7)
fig.suptitle('Attained nuisance-refitted costs at declared nodes; conditional on the other coordinate bounds')
fig.supxlabel('Circles: converged/admissible; triangles: other attained fits. Orange: descent (state count); gray: incomplete phase search; blue: complete search without descent.', fontsize=8)
fig.savefig(figures/'profiles.png', dpi=160)
plt.close(fig)
origin, scale = np.array([c['origin'] for c in coords]), np.array([c['scale'] for c in coords])
fig, ax = plt.subplots(figsize=(10, 7), layout='constrained')
for key, offset, color, name in (('primary', -.15, '#0072B2', 'primary'), ('complete_case', .15, '#E69F00', 'complete-case sensitivity')):
    q = (np.array(study['parameters'][key]['percentiles'])-origin)/scale
    ax.errorbar(q[1], np.arange(16)+offset, xerr=[q[1]-q[0], q[2]-q[1]], fmt='o', color=color, capsize=3,
                label=f"{name}: {study['parameters'][key]['count']} draws")
ax.axvline(0, color='#555555', ls='--')
ax.set(yticks=range(16), yticklabels=labels, xlabel='(Original coordinate − endpoint) / declared scale (dimensionless)',
       title='Central 95% of converged source/series bootstrap fits within the historical bound box')
ax.legend(loc='lower left', fontsize=8)
ax.invert_yaxis()
fig.savefig(figures/'bootstrap-parameters.png', dpi=160)
plt.close(fig)
if study['curves']:
    states = read(AN/'inputs/curve-states.json')
    panels = [('pressure', 'CO2 partial pressure', 313.15, None), ('species', 'MEAH+', 313.15, None),
              ('density', 'liquid density', 313.15, 1e5), ('heat', 'integral heat of absorption', 313.15, 1734000),
              ('mea-water', 'bubble temperature', None, 101330), ('mea-water', 'vapor water mole fraction', None, 101330)]
    fig, axes = plt.subplots(3, 2, figsize=(12, 11), layout='constrained')
    for ax, (family, quantity, T, P) in zip(axes.flat, panels, strict=True):
        part = [r for r in study['curves'] for s in [states[r['state_index']]] if s['family'] == family and r['quantity'] == quantity
                and (T is None or abs(s['state']['T']-T) < 1e-8) and (P is None or abs(s['state']['P']-P) < 1e-8)]
        part.sort(key=lambda r:states[r['state_index']]['state'].get('a', states[r['state_index']]['state'].get('x')))
        if not part:
            ax.text(.1, .5, 'No usable prediction draws', transform=ax.transAxes)
            continue
        x = [states[r['state_index']]['state'].get('a', states[r['state_index']]['state'].get('x')) for r in part]
        y = np.array([r['percentiles'] if r['count'] else [np.nan]*3 for r in part])
        ax.fill_between(x, y[:, 0], y[:, 2], color='#56B4E9', alpha=.4)
        ax.plot(x, y[:, 1], color='#0072B2')
        counts = [r['count'] for r in part]
        condition = (f'T = {T} K' if T is not None else '') + (f'; P = {P:g} Pa' if P is not None else '')
        ax.set(title=f"{quantity}\n{condition.strip('; ')}; n={min(counts)}–{max(counts)}",
               xlabel='Liquid MEA mole fraction' if family == 'mea-water' else 'CO₂ loading (mol/mol MEA)', ylabel=part[0]['unit'])
        if family == 'pressure':
            ax.set_yscale('log')
    fig.suptitle(f"Pointwise central 95% of the {study['primary_bootstrap']}-draw primary bootstrap set; n = draws available at each state; no coverage claim")
    fig.savefig(figures/'bootstrap-predictions.png', dpi=160)
    plt.close(fig)
lines = ['| Coordinate | Unit | Converged and interaction-admissible / attempted | Attained 2ΔC range | Observed cost restriction | Likelihood interpretation |', '|---|---|---:|---|---|---|']
for label, r in zip(labels, study['classifications'], strict=True):
    span = r['attained_twice_delta_cost_range']
    span_text = 'Unavailable' if span is None else f'{span[0]:.5g} to {span[1]:.5g}'
    lines.append(f"| {label} | {r['unit']} | {r['converged']} / {r['attempted']} | {span_text} | {r['conditional_scan_shape']} | {r['classification']} |")
lines += ['', '| Coordinate | Endpoints searched | State–endpoint calculations | Actual trials | Detected descent state–endpoints | Incomplete state–endpoints |', '|---|---:|---:|---:|---:|---:|']
for label, r in zip(labels, study['classifications'], strict=True):
    p = r['phase_counts']
    lines.append(f"| {label} | {p['endpoints']} | {p['states']} | {p['trials']} | {p['detected_descent_states']} | {p['incomplete_states']} |")
P, F = (study['parameters'][k] for k in ('primary', 'complete_case'))
fmt = lambda values: ', '.join(f'{v:.6g}' for v in values)
lines += ['', f"| Coordinate | Unit | Primary {P['count']}: 2.5%, median, 97.5% | Primary, first 100 attempts ({P['first100']['count']}): 2.5%, median, 97.5% | Complete case {F['count']}: 2.5%, median, 97.5% | Complete case − primary: median, central-95% width |", '|---|---|---|---|---|---|']
for i, (label, q) in enumerate(zip(labels, coords, strict=True)):
    change = study['parameters']['complete_case_change']
    lines.append(f"| {label} | {q['units']} | {fmt(p[i] for p in P['percentiles'])} | {fmt(p[i] for p in P['first100']['percentiles'])} | {fmt(p[i] for p in F['percentiles'])} | {change['median'][i]:.3g}, {change['central95_width'][i]:.3g} |")
lines += ['', f"| Coordinate | Unit | Conditional standard error | Linearized ±1.96 SE width | Primary bootstrap central-95% width | Bootstrap / linearized width | Primary draws at lower / upper historical bound (of {P['count']}) |", '|---|---|---:|---:|---:|---:|---:|']
for label, r in zip(labels, study['conditional_error_comparison'], strict=True):
    bounds = f"{r['draws_at_lower_bound']} / {r['draws_at_upper_bound']}"
    if r['conditional_standard_error'] is None:
        lines.append(f"| {label} | {r['unit']} | on active bound | — | {r['bootstrap_central95_width']:.4g} | — | {bounds} |")
    else:
        lines.append(f"| {label} | {r['unit']} | {r['conditional_standard_error']:.4g} | {r['linearized_central95_width']:.4g} | {r['bootstrap_central95_width']:.4g} | {r['bootstrap_to_linearized_width']:.3g} | {bounds} |")
lines += ['', '| Profile node | Coordinate | Fixed value | Step from endpoint | Reference gradient dC/dθ | First-order ΔC | Attained ΔC | Detected descent / incomplete states |', '|---|---|---:|---:|---:|---:|---:|---|']
for r in study['lower_reference_first_order']:
    phase = r['phase'] or {}
    lines.append(f"| {r['identity']} | {labels[[c['identity'] for c in coords].index(r['coordinate'])]} ({r['unit']}) | {r['node']:.6g} | {r['step']:.4g} | {r['reference_gradient']:.4g} | {r['first_order_delta_cost']:.4g} | {r['attained_delta_cost']:.4g} | {phase.get('descent_states', '—')} / {phase.get('incomplete_states', '—')} |")
lines += ['', f"| AARD membership | Observations | Draws with every member available: primary / complete case | Primary: 2.5%, median, 97.5% (%) | Primary, first 100 attempts: 2.5%, median, 97.5% (%) | Complete case: 2.5%, median, 97.5% (%) |", '|---|---:|---:|---|---|---|']
for name, r in study['AARD'].items():
    cells = [fmt(x['percentiles']) if x['count'] else '—' for x in (r, r['first100'], r['complete_case'])]
    lines.append(f"| {name} | {r['observations']} | {r['count']} / {r['complete_case']['count']} | {cells[0]} | {cells[1]} | {cells[2]} |")
short = [r for r in study['calibration_rows'] if r['count'] < study['primary_bootstrap']]
lines += ['', f"| Calibration row with fewer than {study['primary_bootstrap']} available predictions | Source | Quantity | Observed | Available draws | 2.5%, median, 97.5% |", '|---|---|---|---:|---:|---|']
for r in short:
    lines.append(f"| `{r['identity']}` | {r['source']} | {r['quantity']} | {r['observed']:.6g} | {r['count']} | {fmt(r['percentiles']) if r['count'] else '—'} |")
(AN/'tables.qmd').write_text('\n'.join(lines)+'\n')
print('Rendered retained profiles, bootstrap summaries and tables; no model evaluation')
