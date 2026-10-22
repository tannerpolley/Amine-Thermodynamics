"""Plot retained Kuranov total pressures; no model calculation."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
RESULTS = HERE / 'results'


def main():
    report = json.loads((RESULTS / 'refit-summary.json').read_text())
    cases = [('reading-a-reproduction-rows.csv', 'Wangler temperature laws'),
             ('constant-start-kuranov.csv', 'Constant start'), ('fitted-kuranov.csv', 'Fitted endpoint')]
    colors = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00']
    temperatures = [313, 333, 373, 393, 413]
    markers = ['o', 's', '^', 'D', 'v']
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.8), sharex=True, sharey=True, layout='constrained')
    for col, (filename, title) in enumerate(cases):
        with (RESULTS / filename).open() as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 82 and all(r['success'] == 'True' for r in rows)
        for half in range(2):
            ax = axes[half, col]
            subset = [r for r in rows if (float(r['m_mdea']) > 3) == bool(half)]
            ard = 100 * sum(abs(1-float(r['p_calc'])/float(r['p_exp'])) for r in subset)/len(subset)
            for T, color, marker in zip(temperatures, colors, markers):
                group = [r for r in subset if round(float(r['T'])) == T]
                loading = [float(r['m_co2'])/float(r['m_mdea']) for r in group]
                ax.scatter(loading, [float(r['p_exp'])/1e5 for r in group], marker=marker,
                           s=34, facecolors='none', edgecolors='0.2', linewidths=.8)
                ax.scatter(loading, [float(r['p_calc'])/1e5 for r in group], marker=marker,
                           s=14, color=color)
            ax.set_title(f'{title}\n{[19, 32][half]} mass % MDEA; ARD {ard:.2f}%', fontsize=10)
            ax.set_yscale('log')
            ax.grid(alpha=.2)
            if col == 0:
                ax.set_ylabel('Total pressure / bar')
            if half == 1:
                ax.set_xlabel('Loading / (mol CO₂ per mol MDEA)')
    legend = [Line2D([], [], color=c, marker=m, linestyle='', label=f'{T} K')
              for T, c, m in zip(temperatures, colors, markers)]
    fig.legend(handles=legend, loc='outside lower center', ncol=5, frameon=False)
    fig.suptitle(f'Constant ion–water fit misses the 10.9% rule: {report["fit"]["kuranov"]["ARD_percent_solved_rows"]:.2f}% overall\n'
                 'Open markers: Kuranov Table 2 measurements; filled markers: calculated at the same states', fontsize=12)
    (HERE / 'figures').mkdir(exist_ok=True)
    fig.savefig(HERE / 'figures/kuranov-pressure-comparison.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    main()
