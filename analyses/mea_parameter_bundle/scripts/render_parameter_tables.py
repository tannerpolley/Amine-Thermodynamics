"""Format current parameters and retained result tables into the notebook; never evaluate a model."""

import csv
import hashlib
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARAM = ROOT / 'results/selected-current-best-parameters.json'
DATA = ROOT / 'results/a7-paper-evidence'
PHYSICAL = ROOT / 'results/joint-recalibration-170/amendment-7/restricted-2/fit/usable-budget-endpoint.json'
CHEMISTRY = ROOT.parents[1] / 'data/reference/MEA/manifests/chemical_reaction_source_contract.json'
OUT = ROOT / 'figures/a7_regression_overview/output'


def magnitude(coefficient):
    return coefficient['value']['magnitude']


def rounded(value, se):
    # Keep nonzero estimates visible independently of the conditional error.
    return format(value, '#.4g').removesuffix('.')


def cell(value, fitted=False, fixed=False, title='', se=None):
    if value is None:
        return '—'
    if fitted:
        text, title = rounded(value, se), f'exact {value!r}' + (f'; {title}' if title else '')
    else:
        text = format(value, '#.4g').removesuffix('.') if isinstance(value, (int, float)) else str(value)
    if isinstance(value, (int, float)):
        text = ('0' if value == 0 else text).replace('-', '−')
    color = 'evidence-1' if fixed else 'evidence-2'
    star = '[★](#fitted-coordinates){.fit-star}' if fitted else ''
    return f'<span class="{color}" title="{html.escape(title, quote=True)}">{text}</span>{star}'


def table(headers, rows, classes):
    return '\n::: {.parameter-table .' + classes + '}\n' + '| ' + ' | '.join(headers) + ' |\n' + \
        '| ' + ' | '.join(':--' for _ in headers) + ' |\n' + \
        '\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in rows) + '\n:::\n'


def main():
    p = json.loads(PARAM.read_text())
    fit = json.loads((DATA / 'fit-summary.json').read_text())
    fitted = {c['identity'] for c in fit['coordinates']}
    uncertainty = json.loads((DATA / 'conditional-uncertainty.json').read_text())
    se = uncertainty['conditional_standard_error']
    assert hashlib.sha256(PARAM.read_bytes()).hexdigest() == hashlib.sha256(PHYSICAL.read_bytes()).hexdigest()
    components = p['components']
    labels = {'CO2': 'CO₂', 'H2O': 'H₂O', 'MEAH+': 'MEAH⁺', 'MEACOO-': 'MEACOO⁻',
              'HCO3-': 'HCO₃⁻', 'CO3^2-': 'CO₃²⁻', 'H3O+': 'H₃O⁺', 'OH-': 'OH⁻', 'MEA': 'MEA'}
    names = {c['component_id']: labels[c['name']] for c in components}
    species = []
    for c in components:
        cid = c['component_id']
        coeff = {r['family']: r for r in c['coefficients']}
        values = {k: magnitude(v) for k, v in coeff.items()}
        edge = next((e for e in p['topology']['edges'] if
                     e['endpoint_a']['component_id'] == cid == e['endpoint_b']['component_id']), None)
        sites = [s for s in p['topology']['sites'] if s['component_id'] == cid]
        scheme = '2B' if sites else '—'
        epsilon = magnitude(edge['energy_over_k']) if edge else None
        kappa = magnitude(edge['volume']) if edge else None
        charge = magnitude(c['fixed']['charge_number'])
        permittivity = values.get('relative_permittivity', 'solvent law' if 'dielectric_volume' in values else
                                   magnitude(p['model_coefficients'][0]) if charge else None)
        species.append([names[cid], cell(values['segment_count']),
                        cell(values.get('segment_diameter', 'water law'), coeff.get('segment_diameter', {}).get('identity') in fitted,
                             se=se.get(coeff.get('segment_diameter', {}).get('identity'))),
                        cell(values['dispersion_energy_over_k'], coeff['dispersion_energy_over_k']['identity'] in fitted,
                             se=se.get(coeff['dispersion_energy_over_k']['identity'])),
                        cell(epsilon), cell(kappa), cell(scheme, fixed=True), cell(charge, fixed=True),
                        cell(permittivity), cell(values.get('born_diameter'), coeff.get('born_diameter', {}).get('identity') in fitted), cell(values['solvation_factor'])])
    text = '## Species parameters {#species-parameters}\n\nLengths are Å; energy parameters are K. Association volumes, segment counts, permittivities and solvation factors are dimensionless. A dash means the input is absent, not a fitted zero.\n'
    text += table(['Species', '$m$ (1)', '$\\sigma$ (Å)', '$\\epsilon/k$ (K)', '$\\epsilon^{AB}/k$ (K)', '$\\kappa^{AB}$ (1)',
                   'Scheme'], [r[:7] for r in species], 'species-table')
    text += '\n### Electrostatic inputs\n'
    text += table(['Species', '$z$ (1)', '$\\epsilon_r$ (1)', '$d_B$ (Å)', '$f_{\\mathrm{solv}}$ (1)'],
                  [[r[0]] + r[7:] for r in species], 'species-table')
    text += '\nCO₂ has induced 2B association with water and no self-association; its cross-association inputs are in `topology.edges` of the selected file. Ion association is absent.\n\n'
    for law in p['correlations']:
        constant = magnitude(law['constant'])
        if law['family'] == 'segment_diameter':
            terms = ''.join(f"{magnitude(t['amplitude']):+.4g} e^{{{magnitude(t['exponent_coefficient']):.4g}T}}" for t in law['terms'])
            text += f'\n::: {{title="Exact water-diameter constant {constant:.12g} Å; full coefficients in the selected JSON"}}\n\n'
            text += f'Water diameter (rounded display; use the selected JSON for numerical work), with $T$ in K and $\\sigma$ in Å. The constant and amplitudes are in Å; exponent coefficients are in K⁻¹:\n\n$$\\sigma_{{\\mathrm{{H_2O}}}}(T)={constant:.4g}{terms}$$\n\n:::\n\n'
        else:
            ref = law['reference_temperature']['magnitude']
            terms = ''.join(f"{magnitude(t['coefficient']):+.4g}(T-{ref})^{{{t['power']}}}" for t in law['terms'])
            text += f'Water relative permittivity:\n\n$$\\epsilon_{{r,\\mathrm{{H_2O}}}}(T)={constant:.4g}{terms}$$\n\n'
    text += 'The selected file uses solvent-density-temperature permittivity with the retained shared stage-5 water parameters. It excludes dispersion between ions with the same charge sign. For MEAH⁺ and MEACOO⁻, packing diameter is 0.88 times segment diameter and Debye–Hückel diameter equals segment diameter; Born diameters vary separately. No empirical density translation is applied. Fixed and transferred inputs carry their recorded qualifications; these tables confer no new physical validation.\n'
    dielectric = [[names[c['component_id']], *[cell(magnitude(next(r for r in c['coefficients'] if r['family'] == family)))
                  for family in ('dielectric_volume', 'dielectric_temperature')]] for c in components
                  if any(r['family'] == 'dielectric_volume' for r in c['coefficients'])]
    text += '\n## Permittivity inputs\n\nSolvent-density-temperature inputs (retained shared stage 5):\n'
    text += table(['Component', 'Dielectric volume (L/mol)', 'Dielectric temperature (K)'], dielectric, 'summary-table')
    pairs = {frozenset((r['component_id_a'], r['component_id_b'])): r for r in p['pairs']}
    text += '\n## Binary interactions\n\nSymmetric dimensionless $k_{ij}$ at the reference temperature, upper triangle. A blue zero is a serialized fixed input, not a measured absence of interaction. Green exclusions state the selected formulation rule.\n'
    rows = []
    for i, ca in enumerate(components):
        row = [names[ca['component_id']]]
        for j, cb in enumerate(components):
            if j < i:
                value = ''
            elif j == i:
                value = '—'
            elif magnitude(ca['fixed']['charge_number']) * magnitude(cb['fixed']['charge_number']) > 0:
                value = cell('excluded', fixed=True)
            else:
                pair = pairs[frozenset((ca['component_id'], cb['component_id']))]
                coefficient = next(c for c in pair['coefficients'] if c['family'] == 'k_ij')
                value = cell(magnitude(coefficient), coefficient['identity'] in fitted, se=se.get(coefficient['identity']),
                             title='A7 second restricted fit' if coefficient['identity'] in fitted else coefficient['provenance']['locator'])
            row.append(value)
        rows.append(row)
    text += table([''] + [names[c['component_id']] for c in components], rows, 'binary-interactions-table')
    slopes = [[names[r['component_id_a']] + '–' + names[r['component_id_b']],
               cell(magnitude(c), c['identity'] in fitted, se=se.get(c['identity'])), c['reference_temperature']['magnitude']]
              for r in p['pairs'] for c in r['coefficients'] if c['family'] == 'k_ij_reciprocal_temperature_slope']
    text += '\nThe stored temperature dependence is $k_{ij}(T)=k_{ij}(T_{\\mathrm{ref}})+b(1/T-1/T_{\\mathrm{ref}})$. The slope $b$ has units K.\n'
    text += table(['Pair', '$b$ (K)', '$T_{\\mathrm{ref}}$ (K)'], slopes, 'summary-table')
    rows = []
    for index, coordinate in enumerate(fit['coordinates']):
        identity = coordinate['identity']
        label = identity.replace('pair/', '').replace('component/', '')
        for component in sorted(names, key=len, reverse=True):
            label = label.replace(component, names[component])
        label = label.replace('/k_ij/reciprocal_temperature_slope', ' reciprocal-temperature slope')
        label = label.replace('/k_ij', ' interaction').replace('/', '–')
        label = label.replace('segment_diameter', 'segment diameter').replace('born_diameter', 'Born diameter')
        label = label.replace('dispersion_energy_over_k', 'dispersion energy/k')
        label = label.replace('reaction:R5:correlation:a_k', 'R5 unshifted source A')
        label = label.replace('reaction:R2:enthalpy_shift', 'R2 total enthalpy shift').replace('reaction:R5:enthalpy_shift', 'R5 total enthalpy shift')
        error = se.get(identity)
        bound = ('On bound; ' if index in fit['active_bounds'] else 'Free; ') + ' to '.join(format(v, 'g') for v in coordinate['bounds'])
        rows.append([label, cell(coordinate['value'], fitted=True, se=error), {'angstrom': 'Å', 'dimensionless': '1'}.get(coordinate['unit'], coordinate['unit']),
                     '—' if error is None else f'{error:.2g}', bound])
    text += '\n## Fitted coordinates and conditional uncertainty {#fitted-coordinates}\n'
    text += table(['Coordinate', 'Current value', 'Unit', 'Conditional standard error (same unit)', 'Bounds (same unit)'], rows, 'summary-table')
    text += (f"\nThe ten free coordinates have rank {uncertainty['free_rank']} at the campaign cutoff "
             f"{uncertainty['rank_relative_cutoff']:g}. The residual variance factor is {uncertainty['residual_variance']:.4g} "
             "with 307 − 10 = 297 degrees of freedom. R5 A is the unshifted source coordinate; enthalpy shifts are totals including inherited shifts. "
             "The errors condition on residual weights, fixed inputs, active bounds and local linearization. They do not establish "
             "independent-error measurement uncertainty, parameter uniqueness or prediction intervals.\n")
    chemistry = json.loads(CHEMISTRY.read_text())
    overrides = {r['reaction_id']: r for r in p['reaction_correlations']}
    offsets = chemistry['common_source_standard_state']['source_to_common_ln_k_offsets']
    rows = []
    for index, reaction in enumerate(chemistry['reactions']):
        rid = reaction['reaction_id']
        if rid in overrides:
            values = {c['name']: magnitude(c) for c in overrides[rid]['coefficients']}
            source = 'Selected JSON'
            delta = None
        else:
            values = reaction['correlation']
            delta = offsets[index]
            source = 'Fixed chemistry'
        equation = reaction['equation'].replace('<=>', '⇌').replace('CO3--', 'CO₃²⁻')
        for name, label in labels.items():
            equation = equation.replace(name, label)
        rows.append([rid + ' · ' + equation,
                     cell(values.get('a', values.get('a_k'))), cell(values.get('b_k', values.get('b'))),
                     cell(values.get('c', values.get('c_per_k'))), cell(values.get('d_per_k')),
                     cell(delta), source])
    text += '\n## Reaction correlations\n\nR2/R4/R5 below are generated from the current selected JSON. It does not serialize fixed R1/R3; those rows and the reaction equations come from the retained [chemistry declaration](https://github.com/tannerpolley/Amine-Thermodynamics/blob/30ce082/data/reference/MEA/manifests/chemical_reaction_source_contract.json), including its stored aqueous-molality offsets.\n'
    text += table(['Reaction', '$A$ (1)', '$B$ (K)', '$C$ (1)', '$D$ (K⁻¹)', '$\\Delta$ (1)', 'Input owner'], rows[:4], 'summary-table')
    text += '\nR5 uses a base-10 logarithm and different coefficient units:\n'
    text += table(['Reaction', '$A$ (K)', '$B$ (1)', '$C$ (K⁻¹)', 'Input owner'],
                  [[r[0], r[1], r[2], r[3], r[6]] for r in rows[4:]], 'summary-table')
    text += '\nFor R1–R3, $\\ln K=A+B/T+C\\ln T+DT+\\Delta$; R2 already includes the conversion in $A$ and has no separate offset. For R4, $\\ln K=A+B/T$. For R5, $-\\log_{10}K=A/T+B+CT$. The displayed layouts therefore give $B$ in K for R1–R4 and $A$ in K for R5; $D$ for R1–R3 and $C$ for R5 are in K⁻¹. Other coefficients are dimensionless. R2/R5 include the fitted pivot-preserving enthalpy shifts at 313.15 K; R5 also varies its unshifted source A. The displayed reaction coefficients include these transformations and are not independent fitted coordinates or new source measurements.\n'
    OUT.mkdir(parents=True, exist_ok=True)
    destinations = {'fits': ROOT / 'joint-recalibration/index.qmd',
                    'high-temperature': ROOT / 'high-temperature/index.qmd'}
    notebook = ROOT / 'notebook.qmd'
    notebook.write_text(splice(notebook.read_text(), 'CURRENT-PARAMETERS', text))
    for name, block in results().items():
        destination = destinations.get(name, notebook)
        destination.write_text(splice(destination.read_text(), 'RESULTS:' + name, block))
    inputs = [PARAM, PHYSICAL, CHEMISTRY, Path(__file__)] + [DATA / f for f in (
        'conditional-uncertainty.json', 'fit-summary.json', 'heat.csv', 'summary.json',
        'high-temperature-comparison.csv', 'density.csv', 'cp.csv')] + [OUT / 'statistics.csv']
    (OUT / 'parameter-table-inputs.json').write_text(json.dumps(
        {str(f.relative_to(ROOT.parents[1])): hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs}, indent=2) + '\n')


def splice(source, name, text):
    begin, end = f'<!-- {name}:BEGIN -->', f'<!-- {name}:END -->'
    assert source.count(begin) == source.count(end) == 1, name
    prefix, rest = source.split(begin, 1)
    _, suffix = rest.split(end, 1)
    return prefix + begin + '\n\n' + text + '\n' + end + suffix


def read(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def plain(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join('---' for _ in headers) + ' |\n' + \
        ''.join('| ' + ' | '.join(map(str, row)) + ' |\n' for row in rows)


def f4(value):
    return f'{float(value):.4f}'


def results():
    fit = json.loads((DATA / 'fit-summary.json').read_text())
    summary = json.loads((DATA / 'summary.json').read_text())
    groups = fit['groups']
    blocks = {'working-record': plain(['Objective', 'Rows', 'Cost (dimensionless)'],
        [['A7 joint objective', 307, f"{fit['cost']:.4f}"],
         ['Common calibration subset', 149, f"{groups['common149']['cost']:.4f}"]])}
    blocks['fits'] = plain(['Objective group', 'Rows', 'Cost (dimensionless)'],
        [[name, r['n'], f"{r['cost']:.4f}"] for name, r in groups.items()])
    heats = read(DATA / 'heat.csv')
    blocks['heat'] = plain(['Source / role', 'n', 'RMSE (kJ/mol CO₂)', 'Bias (kJ/mol CO₂)'],
        [[name + (' · fitted' if name == 'Vinjarapu2024' else ' · non-fitted prediction'), len(rows),
          f"{math.sqrt(sum(float(r['error_kJ_mol'])**2 for r in rows)/len(rows)):.2f}",
          f"{sum(float(r['error_kJ_mol']) for r in rows)/len(rows):+.3g}"]
         for name in ('Vinjarapu2024', 'Arcis2011') for rows in [[r for r in heats if r['source']==name]]])
    cohort_labels = {
        'canonical 100-120 C': 'Canonical, 100–120 °C',
        'packet 100-120 C': 'Packet (Jou subset), 100–120 °C',
        'canonical 100-120 C Jou1995 100 C': 'Jou 1995, 100 °C (canonical and packet)',
        'canonical 100-120 C Jou1995 120 C': 'Jou 1995, 120 °C (canonical and packet)',
        'canonical 100-120 C Mamun2005 120 C': 'Mamun 2005, 120 °C',
        'canonical 100-120 C Xu2011 100 C': 'Xu 2011, 100 °C',
        'canonical 100-120 C Xu2011 120 C': 'Xu 2011, 120 °C',
    }
    blocks['high-temperature'] = plain(['Cohort', 'n', 'A7 pressure AARD (%)'],
        [[cohort_labels[r['cohort']], r['n_total'], f"{float(r['AARD_percent']):.2f}"]
         for r in read(DATA / 'high-temperature-comparison.csv') if r['cohort'] in cohort_labels])
    density = read(DATA / 'density.csv')
    blocks['density'] = plain(['Fitted cohort', 'Evaluated / requested', 'Within limit', 'Max \\|error\\|/s (1)', 'RMSE (kg/m³)', 'AARD (%)'],
        [[('Amundsen, CO₂-free (5 rows)' if name == 'Amundsen CO2-free gate five' else name),
          f"{r['n_available']} / {r['n_total']}", f"{r.get('within_gate', r['within_2s'])} / {r['n_total']}",
          f"{max(abs(float(row['error_over_s'])) for row in density if row['id'] in r['row_ids']):.2f}",
          f"{r['RMSE']:.3f}", f"{r['AARD_percent']:.2f}"] for name, r in summary['density'].items()
         if name in ('Amundsen fitted 15', 'Hartono fitted 32', 'Amundsen CO2-free gate five')])
    blocks['density'] += '\nLoaded rows use their row-specific $2s$ limits; the CO₂-free five use 1.0 kg/m³.\n\n'
    blocks['density'] += plain(['Source (all retained states; overlaps fitted rows)', 'n', 'RMSE (kg/m³)', 'AARD (%)'],
        [[name, r['n_available'], f"{r['RMSE']:.3f}", f"{r['AARD_percent']:.2f}"] for name, r in summary['density'].items()
         if name in ('Amundsen2009', 'Hartono2014', 'Han2012')])
    cp = read(DATA / 'cp.csv')
    blocks['heat-capacity'] = plain(['Temperature (K)', 'Nominal loading (mol/mol MEA)', 'Cp (kJ/(kg·K))', 'Observed Cp (kJ/(kg·K))', 'Deviation (%)', 'Within 3%'],
        [[r['T_K'], r['loading'], f4(r['equilibrium_cp_kJ_kg_K']), f4(r['observed_kJ_kg_K']), f"{float(r['error_percent']):+.2f}", 'Yes' if r['within_3_percent'] == 'True' else 'No'] for r in cp])
    blocks['heat-capacity'] += f"\n{sum(abs(float(r['error_percent'])) > 3 for r in cp)} of {len(cp)} states exceed the 3% comparison limit.\n"
    stats = read(OUT / 'statistics.csv')
    labels = {
        ('pressure', 'displayed', 'all'): 'Hilliard 2008 + Jou 1995 comparison subset',
        ('pressure', 'common149 fitted', 'all'): 'Fitted (common calibration subset)',
        ('pressure', 'displayed source', 'Hilliard2008'): 'Hilliard 2008',
        ('pressure', 'displayed source', 'Jou1995'): 'Jou 1995',
        ('species', 'displayed', 'all'): 'All shown (Böttinger 2008 + Matin 2012)',
        ('species', 'common149 fitted', 'all'): 'Fitted, common calibration subset (94 targets)',
        ('species', 'all fitted', 'all'): 'Fitted, including 7 restored targets (101 targets)',
        ('species', 'restored fitted', 'all'): 'Restored targets only (7)',
        ('species', 'displayed source', 'Bottinger2008'): 'Böttinger 2008',
        ('species', 'displayed source', 'Matin2012'): 'Matin 2012',
        ('Matin pool', 'displayed', 'all'): 'Matin HCO₃⁻ + CO₃²⁻ pool (report only)',
    }
    for family in ('pressure', 'species'):
        blocks[family] = plain(['Cohort / role', 'Evaluated / requested', 'AARD (%)', 'RMS ln(calc/obs) (1)'],
            [[labels[(r['family'], r['group_type'], r['group'])], f"{r['evaluated_positive']} / {r['attempted']}",
              f"{float(r['aard_percent']):.2f}", f"{float(r['rms_ln_pred_over_obs']):.4f}"]
             for r in stats if (r['family'], r['group_type'], r['group']) in labels
             and (r['family'] == family or (family == 'species' and r['family'] == 'Matin pool'))])
    subset = next(r['attempted'] for r in stats if (r['family'], r['group_type'], r['group']) == ('pressure', 'displayed', 'all'))
    shown = sum(len(read(DATA / f'{n}-pressure.csv')) for n in ('canonical', 'wagner'))
    blocks['pressure'] += f'\nThese statistics cover {subset} of the {shown} measurements in the CO₂ pressure figure.\n'
    return blocks


if __name__ == '__main__':
    main()
