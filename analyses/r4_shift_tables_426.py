"""Format retained #426 results for the Quarto notebooks without importing Engine."""
import argparse
import csv
import json
from pathlib import Path

RESULTS = Path(__file__).parent


def tables(folder):
    def read(name):
        return json.loads((folder / name).read_text())

    def rows(name):
        with (folder / name).open(newline='') as file:
            return list(csv.DictReader(file))

    def fmt(value, spec='.3f'):
        return '—' if value in (None, '') else format(float(value), spec)

    def table(header, values):
        return ['| ' + ' | '.join(row) + ' |' for row in (header, ['---'] * len(header), *values)] + ['']

    output = table(['T (K)', 'Source ln K₄', 'Fitted ln K₄', 'Δln K₄', 'Fitted/source K₄', 'Conditional SE of ln K₄', 'Source range'],
                   [[fmt(r['T_K'], '.2f'), fmt(r['source_ln_K4']), fmt(r['fitted_ln_K4']), fmt(r['delta_ln_K4'], '+.3f'),
                     fmt(r['K4_ratio']), fmt(r['SE_ln_K4']), r['source_range']] for r in rows('shift.csv')])
    r = read('table6.json')
    output += table(['Table 6 quantity', 'Value', 'Conditional SE', 'Lower bound', 'Upper bound'], [
        ['Δln K₄ at 313.15 K', fmt(r['delta_ln_K4'], '+.3f'), fmt(r['SE_ln_K4']), *[fmt(b, '+.0f') for b in r['bounds']['level']]],
        ['Enthalpy increment (J/mol)', fmt(r['delta_h_J_mol'], ',.0f'), fmt(r['SE_h_J_mol'], ',.0f'), *[fmt(b, ',.0f') for b in r['bounds']['enthalpy']]],
    ])
    output += [f"The source and fitted hydrolysis enthalpies are {r['source_h_J_mol']/1000:.2f} and {r['fitted_h_J_mol']/1000:.2f} kJ/mol.", '']
    output += ['### Numerical controls', ''] + table(['Control', 'Outcome', 'Result'], [
        [key, r['outcome'], ', '.join(f"{k.replace('_', ' ')} = {v}" for k, v in r.items() if k != 'outcome')]
        for key, r in sorted(read('controls.json').items())])
    variants = [p.name.removesuffix('-replay.json') for p in sorted(folder.glob('*-replay.json'))]
    replay = {name: read(f'{name}-replay.json') for name in variants}
    groups = sorted(replay['reported']['cost_by_group'])
    output += ['### Fitted-row costs and replay time', ''] + table(
        ['R4 law', 'Replayed rows', 'Replay (s)', 'Grid (s)', 'NMR curves (s)', 'Fitted cost', *groups],
        [[name, str(r['rows']), fmt(r['seconds'], '.2f'), fmt(r.get('grid_seconds'), '.2f'), fmt(r.get('nmr_curve_seconds'), '.2f'), fmt(r['cost'], '.6f'),
          *[fmt((r['cost_by_group'] or {}).get(g), '.6f') for g in groups]] for name, r in replay.items()])
    output += ['### Deviations from observations', '',
               'Absorber is T ≤ 353.2 K, stripper is T ≥ 370 K, and intermediate is between. AARD and signed bias use available rows with nonzero observations.',
               'Reaction-specific breakdowns and the observation bases are in the linked deviation CSVs.', ''] + table(
        ['R4 law', 'Group', 'Role', 'Band', 'Unit', 'Available / rows', 'AARD (%)', 'Bias (%)'],
        [[name, r['group'], r['role'], r['band'], r['unit'], f"{r['available']} / {r['rows']}",
          fmt(r['AARD_percent'], '.2f'), fmt(r['bias_percent'], '+.2f')]
         for name in variants for r in rows(f'{name}-deviations.csv') if r['reaction'] == 'all'])
    baseline = {(r['T_K'], r['loading'], r['curve']): r for r in rows('reported-grid.csv')}
    deltas = []
    for name in variants:
        if name == 'reported':
            continue
        grid = rows(f'{name}-grid.csv')
        for T, quantity in sorted({(r['T_K'], r['curve']) for r in grid}):
            pairs = [(r, baseline[T, r['loading'], quantity]) for r in grid if (r['T_K'], r['curve']) == (T, quantity)]
            scale = 1000 if quantity == 'CO2 partial pressure' else 1
            changes = [(float(a['value']) - float(b['value'])) / scale for a, b in pairs
                       if all(r['status'] == 'Available' and r['requested_tolerance_met'] == 'True' for r in (a, b))]
            deltas.append([name, T, quantity, 'kPa' if scale == 1000 else 'mol/mol', f'{len(changes)} / {len(pairs)}',
                           fmt(min(changes, default=None), '+.5g'), fmt(max(changes, default=None), '+.5g')])
    output += ['### Grid changes relative to the reported law', ''] + table(
        ['R4 law', 'T (K)', 'Quantity', 'Unit', 'Available pairs', 'Minimum change', 'Maximum change'], deltas)
    if 'source-enthalpy' in variants:
        retained = {name: read(f'{name}-rows.json') for name in variants}
        reference = {r['identity']: r for r in retained['reported']}
        pressure = []
        for name in variants:
            for group in ('tong', 'hartono-2021-supplemental'):
                for band, lower, upper in [('absorber', 0, 353.2), ('intermediate', 353.2, 370), ('stripper', 370, float('inf'))]:
                    pairs = [(r, reference[r['identity']]) for r in retained[name] if r['group'] == group and r['role'] == 'not fitted'
                             and (lower <= r['T_K'] <= upper if band != 'intermediate' else lower < r['T_K'] < upper)
                             and r['basis'] == 'Total equilibrium pressure']
                    if not pairs:
                        continue
                    errors = [abs(b['value']/b['observed']-1)*100 for _, b in pairs if b['status'] == 'Available']
                    change = [(r['value']-b['value'])/1000 for r, b in pairs if r['status'] == b['status'] == 'Available']
                    pressure.append([name, group, band, f'{len(change)} / {len(pairs)}', fmt(sum(errors)/len(errors) if errors else None, '.2f'),
                                     fmt(min(change, default=None), '+.4g'), fmt(max(change, default=None), '+.4g')])
        output += ['### AMP total-pressure sensitivity at not-fitted observations', ''] + table(
            ['R4 law', 'Campaign', 'Band', 'Available pairs', 'Reported-law AARD (%)', 'Min ΔP (kPa)', 'Max ΔP (kPa)'], pressure)
        nmr = [r for r in retained['reported'] if r['group'] == 'nmr']
        output += ['### Reported residuals at the calibration temperatures', ''] + table(
            ['T (K)', 'Rows', 'Mean observed carbamate (mol/mol)', 'Mean predicted minus observed (mol/mol)'],
            [[fmt(T, '.2f'), str(len(items)), fmt(sum(r['observed'] for r in items)/len(items), '.5f'),
              fmt(sum(r['value']-r['observed'] for r in items)/len(items), '+.5f')]
             for T in sorted({r['T_K'] for r in nmr}) if (items := [r for r in nmr if r['T_K'] == T])])
    return '\n'.join(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('folders', nargs='*', type=Path, default=[
        RESULTS / amine / 'results/r4-shift-426' for amine in ('dea_transfer', 'amp_transfer')])
    args = parser.parse_args()
    for folder in args.folders:
        path = folder / 'tables.md'
        rendered = tables(folder)
        if args.check:
            if not path.is_file() or path.read_text() != rendered:
                raise SystemExit(f'Stale generated include: {path}')
        else:
            path.write_text(rendered)
