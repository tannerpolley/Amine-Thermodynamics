from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
sys.path.insert(0, str(HERE.parents[2] / 'src'))
import render_regression_overview as renderer
import matplotlib.pyplot as plt
from MEA.common.plot_style import apply_plot_theme
apply_plot_theme()
for born, label in [('1-1', 'SSM+DS'), ('0-0', 'Original Born')]:
    rows = renderer.read(HERE / f'pressure-40-80C-{born}-eval-28181e72.csv')
    renderer.OUT = HERE / 'figures' / f'{born}-eval-28181e72'
    renderer.OUT.mkdir(parents=True, exist_ok=True)
    renderer.render_parity(rows, renderer.source_colors(rows), f'Model D {label}: 40-80 C')
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
for ax, born in zip(axes, ['1-1', '0-0']):
    paths = [HERE / f'{born}-S1-40-80C-iterations.csv']
    if born == '0-0':
        paths.append(HERE / '0-0-S1-40-80C-28181e72-iterations.csv')
    for path in paths:
        rows = renderer.read(path)
        wheel = '28181e72' if path.name.endswith('28181e72-iterations.csv') else 'f66d972c'
        for start in sorted({row['start'] for row in rows}):
            selected = [row for row in rows if row['start'] == start]
            ax.plot([int(row['iteration']) for row in selected],
                    [float(row['cost']) for row in selected], label=f'{start} ({wheel})')
    ax.set(title=f'Born {born}', xlabel='Recorded iteration', ylabel='Weighted objective')
    ax.set_yscale('log')
    ax.grid(alpha=0.2)
    ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(HERE / 'figures' / 'fit-cost-versus-iteration.svg', metadata={'Date': None})
plt.close(fig)
