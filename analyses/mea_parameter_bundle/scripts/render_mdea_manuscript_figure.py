"""Compare retained MDEA CO2 pressures; no model evaluation or fitting."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from manuscript_style import FULL_WIDTH, apply_style

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / 'analyses/mdea_mea_workflow/results'
OUT = ROOT / 'docs/scientific/latex/figures/generated'


def main():
    apply_style()
    inputs, panels, statistics = {}, [], {}
    for source, count, expected in [('Ermatchkov', 88, (26.208, 19.146)),
                                     ('Xiao', 20, (20.398, 28.276))]:
        series = []
        for label, reference in zip(('A3', 'B1'), expected):
            path = RESULTS / (f'stage2-capped/{label}/comparisons.json' if source == 'Ermatchkov'
                              else f'context-sources/{label}-Xiao.json')
            inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
            rows = json.loads(path.read_text())
            if source == 'Ermatchkov':
                rows = [r for r in rows if r['group'] == source and r['row']['mass_fraction'] <= .49]
                observed, predicted = 'observed', 'predicted'
            else:
                observed, predicted = 'observed_p_CO2_Pa', 'predicted_p_CO2_Pa'
            assert len(rows) == count and all(r['status'].lower() == 'available' for r in rows)
            x, y = [r[observed] for r in rows], [r[predicted] for r in rows]
            assert all(v > 0 for v in x + y)
            aard = 100 * sum(abs(p / o - 1) for o, p in zip(x, y)) / count
            if abs(aard - reference) > .0005:
                raise ValueError(f'{source} {label}: {aard} does not reproduce {reference}')
            statistics[f'{source}-{label}'] = dict(rows=count, AARD_percent=aard)
            series.append(([v / 1000 for v in x], [v / 1000 for v in y], aard))
        assert series[0][0] == series[1][0]
        panels.append((source, count, series))

    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.4), layout='constrained')
    for ax, (source, count, series), letter in zip(axes, panels, 'ab'):
        values = [v for x, y, _ in series for v in x + y]
        lo, hi = min(values) * .8, max(values) * 1.25
        ax.plot([lo, hi], [lo, hi], color='0.5', lw=.7, label='Equality')
        for (x, y, aard), name, marker, color in zip(series, ('Single-sphere', 'Charged-molecule'),
                                                  ('o', 'x'), ('#0072B2', '#D55E00')):
            ax.plot(x, y, ls='none', marker=marker, color=color, markerfacecolor='none',
                    markersize=3.5, label=f'{name}: {aard:.2f}%')
        ax.set(xscale='log', yscale='log', xlim=(lo, hi), ylim=(lo, hi),
               xlabel=r'Measured CO$_2$ partial pressure (kPa)',
               ylabel=r'Calculated CO$_2$ partial pressure (kPa)',
               title=f'({letter}) {source}: {count} observations')
        ax.set_aspect('equal', adjustable='box')
        ax.legend(loc='upper left', fontsize=7, frameon=False, title='AARD', title_fontsize=8)
    name = 'mdea-pressure'
    fig.savefig(OUT / f'{name}.pdf', metadata={'CreationDate': None, 'ModDate': None})
    plt.close(fig)
    for path in (Path(__file__), Path(__file__).with_name('manuscript_style.py')):
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    provenance_path = OUT / 'provenance.json'
    provenance = json.loads(provenance_path.read_text())
    provenance['outputs'][name] = dict(generator=str(Path(__file__).relative_to(ROOT)),
        files=[f'{name}.pdf'], inputs=inputs, statistics=statistics,
        selection='Ermatchkov: group == Ermatchkov and row.mass_fraction <= 0.49; Xiao: all rows',
        units='Retained Pa divided by 1000 to kPa',
        scoring='100 mean(abs(predicted / observed - 1)); all rows available')
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + '\n')
    print(json.dumps(statistics, indent=2))


if __name__ == '__main__':
    main()
