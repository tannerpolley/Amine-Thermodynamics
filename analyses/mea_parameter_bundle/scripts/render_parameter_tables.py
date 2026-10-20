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
    # Two significant digits of the conditional standard error set the displayed decimals.
    return format(value, '.6g') if se is None else f'{value:.{max(0, 1 - math.floor(math.log10(se)))}f}'


def cell(value, fitted=False, fixed=False, title='', se=None):
    if value is None:
        return '—'
    if fitted:
        text, title = rounded(value, se), f'exact {value!r}' + (f'; {title}' if title else '')
    else:
        text = format(value, '.12g') if isinstance(value, (int, float)) else str(value)
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
    text = '## Species parameters\n\nLengths are Å; energy parameters are K. Association volumes, segment counts, permittivities and solvation factors are dimensionless. A dash means the input is absent, not a fitted zero.\n'
    text += table(['Species', '$m$', '$\\sigma$', '$\\epsilon/k$', '$\\epsilon^{AB}/k$', '$\\kappa^{AB}$',
                   'Scheme', '$z$', '$\\epsilon_r$', '$d_B$', '$f_{\\mathrm{solv}}$'], species, 'species-table')
    text += '\nCO₂ has induced 2B association with water and no self-association; its cross-association inputs are in `topology.edges` of the selected file. Ion association is absent.\n\n'
    for law in p['correlations']:
        constant = magnitude(law['constant'])
        if law['family'] == 'segment_diameter':
            terms = ''.join(f"{magnitude(t['amplitude']):+.12g} e^{{{magnitude(t['exponent_coefficient']):.12g}T}}" for t in law['terms'])
            text += f'Water diameter, with $T$ in K and $\\sigma$ in Å:\n\n$$\\sigma_{{\\mathrm{{H_2O}}}}(T)={constant:.12g}{terms}$$\n\n'
        else:
            ref = law['reference_temperature']['magnitude']
            terms = ''.join(f"{magnitude(t['coefficient']):+.12g}(T-{ref})^{{{t['power']}}}" for t in law['terms'])
            text += f'Water relative permittivity:\n\n$$\\epsilon_{{r,\\mathrm{{H_2O}}}}(T)={constant:.12g}{terms}$$\n\n'
    text += 'The selected file uses solvent-density-temperature permittivity with the retained shared stage-5 water parameters. It excludes dispersion between ions with the same charge sign. For MEAH⁺ and MEACOO⁻, packing diameter is 0.88 times segment diameter and Debye–Hückel diameter equals segment diameter; Born diameters vary separately. No empirical density translation is applied. Fixed and transferred inputs carry their recorded qualifications; these tables confer no new physical validation.\n'
    dielectric = [[names[c['component_id']], *[cell(magnitude(next(r for r in c['coefficients'] if r['family'] == family)))
                  for family in ('dielectric_volume', 'dielectric_temperature')]] for c in components
                  if any(r['family'] == 'dielectric_volume' for r in c['coefficients'])]
    text += '\nSolvent-density-temperature permittivity inputs (retained shared stage 5):\n'
    text += table(['Component', 'Dielectric volume (L/mol)', 'Dielectric temperature (K)'], dielectric, 'summary-table')
    pairs = {frozenset((r['component_id_a'], r['component_id_b'])): r for r in p['pairs']}
    text += '\n## Binary interactions\n\nSymmetric $k_{ij}$, upper triangle. A blue zero is a serialized fixed input, not a measured absence of interaction. Green exclusions state the selected formulation rule.\n'
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
        label = identity
        for component in sorted(names, key=len, reverse=True):
            label = label.replace(component, names[component])
        error = se.get(identity)
        bound = 'On bound; no symmetric error' if index in fit['active_bounds'] else 'Free'
        rows.append([label, cell(coordinate['value'], fitted=True, se=error), coordinate['unit'],
                     '—' if error is None else f'{error:.2g}', bound])
    text += '\n## Sixteen fitted coordinates {#fitted-coordinates}\n'
    text += table(['Coordinate', 'Current value', 'Unit', 'Conditional standard error', 'Bound'], rows, 'summary-table')
    text += (f"\nThe ten free coordinates have rank {uncertainty['free_rank']} at the campaign cutoff "
             f"{uncertainty['rank_relative_cutoff']:g}. The residual variance factor is {uncertainty['residual_variance']:.10f} "
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
    text += '\n## Reactions\n\nR2/R4/R5 below are generated from the current selected JSON. It does not serialize fixed R1/R3; those rows and the reaction equations come from the retained [chemistry declaration](https://github.com/tannerpolley/Amine-Thermodynamics/blob/30ce082/data/reference/MEA/manifests/chemical_reaction_source_contract.json), including its stored aqueous-molality offsets.\n'
    text += table(['Reaction', '$A$', '$B$', '$C$', '$D$', '$\\Delta$', 'Input owner'], rows, 'summary-table')
    text += '\nFor R1–R3, $\\ln K=A+B/T+C\\ln T+DT+\\Delta$; R2 already includes the conversion in $A$ and has no separate offset. For R4, $\\ln K=A+B/T$. For R5, $-\\log_{10}K=A/T+B+CT$. The displayed layouts therefore give $B$ in K for R1–R4 and $A$ in K for R5; $D$ for R1–R3 and $C$ for R5 are in K⁻¹. Other coefficients are dimensionless. R2/R5 include the fitted pivot-preserving enthalpy shifts at 313.15 K; R5 also varies its unshifted source A. The displayed reaction coefficients include these transformations and are not independent fitted coordinates or new source measurements.\n'
    OUT.mkdir(parents=True, exist_ok=True)
    notebook = ROOT / 'notebook.qmd'
    source = splice(notebook.read_text(), 'CURRENT-PARAMETERS', text)
    for name, block in results().items():
        source = splice(source, 'RESULTS:' + name, block)
    notebook.write_text(source)
    inputs = [PARAM, PHYSICAL, CHEMISTRY, Path(__file__)] + [DATA / f for f in (
        'conditional-uncertainty.json', 'fit-summary.json', 'heat.csv', 'summary.json',
        'high-temperature-comparison.csv', 'density.csv', 'cp.csv')]
    (OUT / 'parameter-table-inputs.json').write_text(json.dumps(
        {str(f.relative_to(ROOT.parents[1])): hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs}, indent=2) + '\n')


def splice(source, name, text):
    begin, end = f'<!-- {name}:BEGIN -->', f'<!-- {name}:END -->'
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
    blocks = {'working-record': (
        f"The adopted A7 [307 objective rows](results/a7-paper-evidence/fitted-rows.csv) have cost **{fit['cost']:.6f}**. "
        f"The common 149 cost is **{groups['common149']['cost']:.6f}**: 47 pressures, 94 species targets and eight Vinjarapu heats. "
        f"Their pressure and species average absolute relative deviations (AARDs) are **{groups['common149 pressure']['AARD_percent']:.6f}%** "
        f"and **{groups['common149 species']['AARD_percent']:.6f}%**. The added targets and their separate costs appear below.\n")}
    blocks['fits'] = plain(['Objective group', 'Rows', 'Cost'],
        [[name, r['n'], f"{r['cost']:.6f}"] for name, r in groups.items()])
    heats = read(DATA / 'heat.csv')
    blocks['heat'] = plain(['Source / role', 'n', 'RMSE (kJ/mol CO₂)', 'Bias (kJ/mol CO₂)'],
        [[name + (' · fitted' if name == 'Vinjarapu2024' else ' · non-fitted prediction'), len(rows),
          f"{math.sqrt(sum(float(r['error_kJ_mol'])**2 for r in rows)/len(rows)):.4f}",
          f"{sum(float(r['error_kJ_mol']) for r in rows)/len(rows):.4f}"]
         for name in ('Vinjarapu2024', 'Arcis2011') for rows in [[r for r in heats if r['source']==name]]])
    blocks['high-temperature'] = plain(['Cohort', 'n', 'A7 pressure AARD (%)'],
        [[r['cohort'], r['n_total'], f4(r['AARD_percent'])] for r in read(DATA / 'high-temperature-comparison.csv')])
    blocks['density'] = plain(['Source (all retained states)', 'n', 'RMSE (kg/m³)', 'AARD (%)'],
        [[name, r['n_available'], f4(r['RMSE']), f4(r['AARD_percent'])] for name, r in summary['density'].items()
         if name in ('Amundsen2009', 'Hartono2014', 'Han2012')])
    cp = read(DATA / 'cp.csv')
    blocks['heat-capacity'] = plain(['Temperature (K)', 'Nominal loading (mol/mol MEA)', 'Cp (kJ/(kg·K))', 'Observed Cp (kJ/(kg·K))', 'Deviation (%)'],
        [[r['T_K'], r['loading'], f4(r['equilibrium_cp_kJ_kg_K']), f4(r['observed_kJ_kg_K']), f4(r['error_percent'])] for r in cp])
    blocks['heat-capacity'] += f"\n{sum(abs(float(r['error_percent'])) > 3 for r in cp)} of {len(cp)} states exceed the 3% comparison limit.\n"
    return blocks


if __name__ == '__main__':
    main()
