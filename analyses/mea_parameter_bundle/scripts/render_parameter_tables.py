"""Format current parameters and retained result tables into the notebook; never evaluate a model."""

import csv
import hashlib
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARAM = ROOT / 'results/selected-current-best-parameters.json'
DATA = ROOT / 'results/heat-final-170'
PHYSICAL = ROOT / 'results/heat-160/A-parameters.json'
CHEMISTRY = ROOT.parents[1] / 'data/reference/MEA/manifests/chemical_reaction_source_contract.json'
OUT = ROOT / 'figures/regression_overview/output'
CALIBRATION = ROOT / 'results/density-cp-160/D1-evidence/corrected-target-densities.csv'


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
    fit = json.loads((DATA / 'F1-A/native-fit.json').read_text())
    fitted = set(fit['coordinates'])
    uncertainty = json.loads((DATA / 'conditional-uncertainty.json').read_text())['F1']
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
        permittivity = values.get('relative_permittivity', 'water law' if cid == 'water' else
                                   magnitude(p['model_coefficients'][0]) if charge else None)
        species.append([names[cid], cell(values['segment_count']),
                        cell(values.get('segment_diameter', 'water law')), cell(values['dispersion_energy_over_k']),
                        cell(epsilon), cell(kappa), cell(scheme, fixed=True), cell(charge, fixed=True),
                        cell(permittivity), cell(values.get('born_diameter')), cell(values['solvation_factor'])])
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
    text += 'The selected file retains solvent-only dielectric mixing and excludes dispersion between ions with the same charge sign. Packing and Debye–Hückel diameters remain separate fields in that file; Born diameters are shown above. Fixed and transferred inputs carry their recorded qualifications; these tables confer no new physical validation.\n'
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
                             title='Current F1 fit: F1-A/native-fit.json' if coefficient['identity'] in fitted else coefficient['provenance']['locator'])
            row.append(value)
        rows.append(row)
    text += table([''] + [names[c['component_id']] for c in components], rows, 'binary-interactions-table')
    slopes = [[names[r['component_id_a']] + '–' + names[r['component_id_b']],
               cell(magnitude(c), c['identity'] in fitted, se=se.get(c['identity'])), c['reference_temperature']['magnitude']]
              for r in p['pairs'] for c in r['coefficients'] if c['family'] == 'k_ij_reciprocal_temperature_slope']
    text += '\nThe stored temperature dependence is $k_{ij}(T)=k_{ij}(T_{\\mathrm{ref}})+b(1/T-1/T_{\\mathrm{ref}})$. The slope $b$ has units K.\n'
    text += table(['Pair', '$b$ (K)', '$T_{\\mathrm{ref}}$ (K)'], slopes, 'summary-table')
    coordinates = {c['identity']: c for r in p['pairs'] for c in r['coefficients']}
    coordinate_labels = ['MEACOO⁻–water $k_{ij}$', 'MEAH⁺–water $k_{ij}$', 'HCO₃⁻–water $k_{ij}$',
              'MEACOO⁻–MEAH⁺ $k_{ij}$', 'MEAH⁺–water $b$ (K)']
    rows = []
    for identity, label in zip(fit['coordinates'], coordinate_labels, strict=True):
        error = se.get(identity)
        bound = 'On bound; no standard error' if identity in fit['active_bounds'] else 'Free'
        rows.append([label, cell(magnitude(coordinates[identity]), fitted=True, se=error), '—' if error is None else f'{error:.2g}', bound])
    text += '\n## Five fitted coordinates {#fitted-coordinates}\n'
    text += table(['Coordinate', 'Current value', 'Conditional standard error', 'Bound'], rows, 'summary-table')
    text += '\nThe errors condition on fixed chemistry, water, neutral binaries, Born inputs and residual weights. They do not establish unique ion properties; no uncertainty band or concentration-transfer claim follows.\n'
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
    text += '\nFor R1–R3, $\\ln K=A+B/T+C\\ln T+DT+\\Delta$; R2 already includes the conversion in $A$ and has no separate offset. For R4, $\\ln K=A+B/T$. For R5, $-\\log_{10}K=A/T+B+CT$. The displayed layouts therefore give $B$ in K for R1–R4 and $A$ in K for R5; $D$ for R1–R3 and $C$ for R5 are in K⁻¹. Other coefficients are dimensionless. R2/R5 are inherited calibrated chemistry, held fixed in the five-coordinate fit; they are not new source measurements.\n'
    OUT.mkdir(parents=True, exist_ok=True)
    notebook = ROOT / 'notebook.qmd'
    source = splice(notebook.read_text(), 'CURRENT-PARAMETERS', text)
    for name, block in results().items():
        source = splice(source, 'RESULTS:' + name, block)
    notebook.write_text(source)
    inputs = [PARAM, PHYSICAL, CHEMISTRY, CALIBRATION, Path(__file__)] + [DATA / f for f in (
        'conditional-uncertainty.json', 'F1-A/native-fit.json', 'fit-comparison.csv', 'heat-comparison.csv',
        'high-temperature-comparison.csv', 'corrected-densities.csv', 'heat-capacity-comparison.csv')]
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
    fits = read(DATA / 'fit-comparison.csv')
    f1 = {r['objective']: r for r in fits if r['problem'] == 'F1'}
    heat, base = f1['with heat'], f1['no heat']
    blocks = {'working-record': (
        f"The current [fit-comparison rows](results/heat-final-170/fit-comparison.csv) give a {heat['targets']}-target objective cost of "
        f"**{float(heat['cost']):.6f}**: {heat['pressure_n']} pressures, {heat['species_n']} species targets and {heat['heat_n']} integral heats. "
        f"The matched pressure/species subtotal is **{float(heat['cost']) - float(heat['heat_cost']):.6f}**, against **{float(base['cost']):.6f}** "
        f"without heat. Fitted pressure AARD is **{float(heat['pressure_AARD_percent']):.6f}%** and species AARD is "
        f"**{float(heat['species_AARD_percent']):.6f}%**. AARD is the average absolute relative deviation; the declared residual scales "
        "and conditional errors do not constitute measured uncertainty for all targets.\n")}
    rows = read(DATA / 'heat-comparison.csv')
    role = lambda r: 'predicted' if r['source'] != 'Vinjarapu2024' else 'fitted' if r['record'] == 'heat F1' else 'predicted control'
    blocks['heat'] = plain(['Record', 'Source / role', 'Pressure (MPa)', 'n', 'RMSE (kJ/mol)', 'Bias (kJ/mol)'],
        [[r['record'], f"{r['source']} · {role(r)}", f"{float(r['pressure_Pa']) / 1e6:.4f}" if r['pressure_Pa'] else 'All',
          r['n'], f4(r['RMSE_kJ_mol']), f4(r['bias_kJ_mol'])] for r in rows])
    total = {(r['record'], r['source']): r for r in rows if not r['pressure_Pa']}
    v, v0 = total['heat F1', 'Vinjarapu2024'], total['no-heat F1', 'Vinjarapu2024']
    a, a0 = total['heat F1', 'Arcis2011'], total['no-heat F1', 'Arcis2011']
    blocks['heat'] += (f"\nThe current fit gives {f4(v['minimum_predicted_kJ_mol'])} to {f4(v['maximum_predicted_kJ_mol'])} kJ/mol CO₂ for Vinjarapu. "
        f"Vinjarapu RMSE is {f4(v['RMSE_kJ_mol'])} kJ/mol against {f4(v0['RMSE_kJ_mol'])} without heat; Arcis RMSE is "
        f"{f4(a['RMSE_kJ_mol'])} against {f4(a0['RMSE_kJ_mol'])} kJ/mol.\n").replace(' -', ' −')
    blocks['fits'] = plain(['Problem', 'Objective', 'Targets', 'Cost', 'Pressure AARD (%)', 'Species n', 'Species AARD (%)', 'Heat cost'],
        [[r['problem'], r['objective'], r['targets'], f4(r['cost']), f4(r['pressure_AARD_percent']), r['species_n'],
          f4(r['species_AARD_percent']), f4(r['heat_cost'])] for r in fits])
    blocks['high-temperature'] = plain(['Cohort', 'Nominal temperature (°C)', 'n', 'No-heat F1 AARD (%)', 'Heat F1 AARD (%)'],
        [[r['cohort'], r['nominal_temperature_C'] or 'All', r['n'], f4(r['no_heat_AARD_percent']), f4(r['with_heat_AARD_percent'])]
         for r in read(DATA / 'high-temperature-comparison.csv')])
    key = lambda r: (float(r['temperature_K']), float(r['loading']), float(r['mea_mass_fraction']))
    calibration = {key(r) for r in read(CALIBRATION)}
    densities = read(DATA / 'corrected-densities.csv')
    groups = {'Translation calibration': [r for r in densities if key(r) in calibration],
              'Other retained states': [r for r in densities if key(r) not in calibration]}
    def span(rows, field, scale=1):
        values = sorted({float(r[field]) * scale for r in rows})
        return f'{values[0]:g}' if len(values) == 1 else f'{values[0]:g}–{values[-1]:g}'
    def error(rows, field):
        values = [abs(float(r[field])) for r in rows]
        return f'{sum(values) / len(values):.2f} / {max(values):.2f}'
    blocks['density'] = plain(['States', 'n', 'MEA (wt%)', 'T (K)', 'Loading (mol/mol MEA)', 'Without translation, mean / max (%)', 'With translation, mean / max (%)'],
        [[name, len(rows), span(rows, 'mea_mass_fraction', 100), span(rows, 'temperature_K'), span(rows, 'loading'),
          error(rows, 'eos_deviation_percent'), error(rows, 'corrected_deviation_percent')] for name, rows in groups.items()])
    cp = [r for r in read(DATA / 'heat-capacity-comparison.csv') if r['record'] == 'heat F1']
    blocks['heat-capacity'] = plain(['Temperature (K)', 'Nominal loading (mol/mol MEA)', 'Cp (kJ/(kg·K))', 'Observed Cp (kJ/(kg·K))', 'Deviation (%)'],
        [[r['T_K'], r['loading'], f4(r['equilibrium_cp_kJ_kg_K']), f4(r['observed_kJ_kg_K']), f4(r['deviation_percent'])] for r in cp])
    blocks['heat-capacity'] += f"\n{sum(abs(float(r['deviation_percent'])) > 3 for r in cp)} of {len(cp)} states exceed the 3% comparison limit.\n"
    return blocks


if __name__ == '__main__':
    main()
