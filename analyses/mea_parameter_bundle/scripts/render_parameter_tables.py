"""Format current component, binary and reaction inputs; never evaluate a model."""

import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARAM = ROOT / 'results/selected-current-best-parameters.json'
DATA = ROOT / 'results/density-cp-160/D1-evidence'
QUALIFICATION = ROOT / 'results/density-cp-160/common-wheel-48a639e7/qualification.json'
CHEMISTRY = ROOT.parents[1] / 'data/reference/MEA/manifests/chemical_reaction_source_contract.json'
OUT = ROOT / 'figures/regression_overview/output'


def magnitude(coefficient):
    return coefficient['value']['magnitude']


def cell(value, fitted=False, fixed=False, title=''):
    if value is None:
        return '—'
    text = str(value) if fitted else format(value, '.12g') if isinstance(value, (int, float)) else str(value)
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
    assert hashlib.sha256(PARAM.read_bytes()).hexdigest() == json.loads(QUALIFICATION.read_text())['inputs']['candidate_record_sha256']
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
                value = cell(magnitude(coefficient), coefficient['identity'] in fitted,
                             title='Current F1 fit: F1-A/native-fit.json' if coefficient['identity'] in fitted else coefficient['provenance']['locator'])
            row.append(value)
        rows.append(row)
    text += table([''] + [names[c['component_id']] for c in components], rows, 'binary-interactions-table')
    slopes = [[names[r['component_id_a']] + '–' + names[r['component_id_b']],
               cell(magnitude(c), c['identity'] in fitted), c['reference_temperature']['magnitude']]
              for r in p['pairs'] for c in r['coefficients'] if c['family'] == 'k_ij_reciprocal_temperature_slope']
    text += '\nThe stored temperature dependence is $k_{ij}(T)=k_{ij}(T_{\\mathrm{ref}})+b(1/T-1/T_{\\mathrm{ref}})$. The slope $b$ has units K.\n'
    text += table(['Pair', '$b$ (K)', '$T_{\\mathrm{ref}}$ (K)'], slopes, 'summary-table')
    uncertainty = next(r for r in json.loads((DATA / 'conditional-uncertainty.json').read_text()) if r['problem'] == 'F1')['uncertainty']
    coordinates = {c['identity']: c for r in p['pairs'] for c in r['coefficients']}
    coordinate_labels = ['MEACOO⁻–water $k_{ij}$', 'MEAH⁺–water $k_{ij}$', 'HCO₃⁻–water $k_{ij}$',
              'MEACOO⁻–MEAH⁺ $k_{ij}$', 'MEAH⁺–water $b$ (K)']
    rows = []
    for index, (identity, label) in enumerate(zip(fit['coordinates'], coordinate_labels, strict=True)):
        se = uncertainty['conditional_standard_error'].get(identity)
        bound = 'Upper bound; SE excluded' if index in fit['active_bounds'] else 'Free'
        rows.append([label, cell(magnitude(coordinates[identity]), fitted=True), '—' if se is None else f'{se:.5g}', bound])
    text += '\n## Five fitted coordinates {#fitted-coordinates}\n'
    text += table(['Coordinate', 'Current value', 'Conditional standard error', 'Bound'], rows, 'summary-table')
    text += '\nThe errors condition on fixed chemistry, water, neutral binaries, Born inputs and residual weights. The HCO₃⁻–water coordinate is on its upper bound. The MEAH⁺–water slope is not distinguishable from zero on this conditional scale: its standard error is much larger than its magnitude. No uncertainty band or concentration-transfer claim follows.\n'
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
    begin = '<!-- CURRENT-PARAMETERS:BEGIN -->'
    end = '<!-- CURRENT-PARAMETERS:END -->'
    source = notebook.read_text()
    prefix, rest = source.split(begin, 1)
    _, suffix = rest.split(end, 1)
    notebook.write_text(prefix + begin + '\n\n' + text + '\n' + end + suffix)
    inputs = [PARAM, QUALIFICATION, CHEMISTRY, DATA / 'conditional-uncertainty.json', DATA / 'F1-A/native-fit.json', Path(__file__)]
    (OUT / 'parameter-table-inputs.json').write_text(json.dumps(
        {str(f.relative_to(ROOT.parents[1])): hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs}, indent=2) + '\n')


if __name__ == '__main__':
    main()
