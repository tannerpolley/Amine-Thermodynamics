"""Reduce retained #263 predictions and draw the speciation comparison; no model calls."""
import json
from pathlib import Path
import math
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AN = Path(__file__).resolve().parent
SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
CASES = ('baseline', 'hamborg', 'all-five', 'holdout')


def metrics(rows):
    available = [r for r in rows if r['status'] == 'Available' and r.get('requested_tolerance_met') and r.get('relative_error_percent') is not None]
    return dict(n=len(available), total=len(rows), unavailable=[r['identity'] for r in rows if r not in available],
        aard_percent=sum(abs(r['relative_error_percent']) for r in available) / len(available) if available else None,
        bias=sum(r['value']-r['observed'] for r in available) / len(available) if available else None,
        rmse=math.sqrt(sum((r['value']-r['observed'])**2 for r in available) / len(available)) if available else None)


def main():
    results = {case: json.loads((AN / f'results/{case}-assessment.json').read_text()) for case in CASES}
    assert all(r['wheel_sha256'] == SHA for r in results.values())
    summary = dict(wheel_sha256=SHA, cases={})
    for case, data in results.items():
        rows = data['rows']
        pressure = [r for r in rows if r['family'] == 'pressure']
        species = [r for r in rows if r['family'] == 'species']
        groups = {name: metrics([r for r in pressure if subset is None or r['fitted'] == subset])
                  for name, subset in (('all159', None), ('fitted47', True), ('nonfitted112', False))}
        heat = {str(t): metrics([r for r in data['heat'] if r['T_K'] == t and not r.get('source_inconsistent', False)
                               and r['status'] != 'OutsideLoadingDomain']) for t in (313.15, 353.15, 393.15)}
        item = dict(pressure=groups, heat=heat, species=species, detected_instabilities=data['detected_instabilities'])
        if case in ('all-five', 'holdout'):
            fit = json.loads((AN / f'results/{case}-fit.json').read_text())
            item['fit'] = {k: fit[k] for k in ('status', 'usable', 'initial_cost', 'final_cost', 'shifts_j_per_mol', 'active_bounds', 'holdout', 'trial_failures')}
            item['pressure_cost_percentage_points'] = groups['fitted47']['aard_percent'] - summary['cases']['baseline']['pressure']['fitted47']['aard_percent']
            carbamate = [r for r in species if r['species'] == 'MEACOO-']
            item['maximum_carbamate_excess_percent'] = max(r['relative_error_percent'] for r in carbamate if r.get('relative_error_percent') is not None)
            item['bounded_correction_met'] = (fit['status'] == 'converged' and fit['usable'] and len(carbamate) == 5 and all(r['status'] == 'Available' for r in carbamate) and not fit['active_bounds'] and item['maximum_carbamate_excess_percent'] < 10
                                             and item['pressure_cost_percentage_points'] <= 2)
        if case != 'baseline':
            base = {r['identity']: r for r in results['baseline']['heat']}
            item['heat_attribution'] = {}
            for t in (313.15, 353.15, 393.15):
                paired = [r for r in data['heat'] if r['T_K'] == t and not r.get('source_inconsistent', False)
                          and r['status'] == 'Available' and base[r['identity']]['status'] == 'Available']
                before = sum(abs(base[r['identity']]['value']-r['observed']) for r in paired)
                after = sum(abs(r['value']-r['observed']) for r in paired)
                item['heat_attribution'][str(t)] = dict(n=len(paired), mean_absolute_error_baseline=before/len(paired) if paired else None,
                    mean_absolute_error_candidate=after/len(paired) if paired else None, fraction_absolute_error_removed=(before-after)/before if before else None,
                    excluded_from_pair=[r['identity'] for r in data['heat'] if r['T_K'] == t and r not in paired])
        summary['cases'][case] = item
    summary['input_hashes'] = {f'{c}-assessment.json': hashlib.sha256((AN/f'results/{c}-assessment.json').read_bytes()).hexdigest() for c in CASES}
    table = ['| Case | Fitted pressure AARD, n=47 (%) | Non-fitted pressure AARD, n=112 (%) | All pressure AARD, n=159 (%) |', '| --- | ---: | ---: | ---: |']
    for case, row in summary['cases'].items():
        table.append('| ' + case + ' | ' + ' | '.join(f"{row['pressure'][g]['aard_percent']:.4f}" for g in ('fitted47', 'nonfitted112', 'all159')) + ' |')
    table += ['', '| Case | Kim 313.15 K AARD (%) | Kim 353.15 K AARD (%) | Kim 393.15 K AARD (%) |', '| --- | ---: | ---: | ---: |']
    for case, row in summary['cases'].items():
        table.append('| ' + case + ' | ' + ' | '.join(f"{row['heat'][str(t)]['aard_percent']:.4f}" for t in (313.15, 353.15, 393.15)) + ' |')
    table += ['', 'Kim counts: 27, 26 and 18; loading ≤0.60; two inconsistent 393.15 K rows excluded. Positive heat release on absorbed CO₂ basis.', '', '| Loading (mol CO₂/mol MEA) | Baseline carbamate error (%) | Hamborg (%) | All five (%) | Holdout (%) |', '| ---: | ---: | ---: | ---: | ---: |']
    carbamate = {case: sorted([r for r in data['rows'] if r.get('species') == 'MEACOO-'], key=lambda r: r['loading']) for case, data in results.items()}
    for i in range(5):
        table.append(f"| {carbamate['baseline'][i]['loading']:.6f} | " + ' | '.join(f"{carbamate[c][i]['relative_error_percent']:.4f}" for c in CASES) + ' |')
    table += ['', '| Case | 353.15 K absolute heat error removed (%) | 393.15 K removed (%) |', '| --- | ---: | ---: |']
    for case in CASES[1:]:
        table.append('| ' + case + ' | ' + ' | '.join(f"{100*summary['cases'][case]['heat_attribution'][str(t)]['fraction_absolute_error_removed']:.4f}" for t in (353.15, 393.15)) + ' |')
    (AN/'results/tables.md').write_text('\n'.join(table) + '\n')
    (AN / 'results/summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    for ax, species in zip(axes, ('MEACOO-', 'MEA + MEAH+')):
        for i, (case, marker, color) in enumerate(zip(CASES, ('x', '+', '^', 's'), ('#000000', '#0072B2', '#D55E00', '#009E73'))):
            data = [r for r in results[case]['rows'] if r['family'] == 'species' and r['species'] == species]
            data.sort(key=lambda r: r['loading'])
            ax.scatter([r['loading'] for r in data], [r['value'] for r in data], marker=marker, color=color, label=case)
            if i == 0:
                ax.scatter([r['loading'] for r in data], [r['observed'] for r in data], facecolors='none', edgecolors='black', label='Böttinger NMR')
        ax.set(xlabel='Loading (mol CO₂/mol MEA)', ylabel=f'{species} mole fraction', title=species)
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    fig.suptitle('353.15 K, 31 wt% MEA; fixed EOS, changed reaction laws\nPoints at observed states; no continuous model curve')
    (AN/'figures').mkdir(exist_ok=True)
    fig.savefig(AN/'figures/speciation.png', dpi=180, metadata={'Engine wheel SHA-256': SHA})
    print(json.dumps(summary['cases'], indent=2))


if __name__ == '__main__':
    main()
