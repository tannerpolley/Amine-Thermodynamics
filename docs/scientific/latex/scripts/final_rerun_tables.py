"""Generate issue 197 numerical tables from retained files; no Engine compute."""
import json
import math
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'analyses/mea_parameter_bundle/scripts'))
import a7_presentation as a  # noqa: E402

TABLES = ROOT / 'docs/scientific/latex/tables'
OUTPUTS = {}
NAMES = {'carbon-dioxide': r'\ce{CO2}', 'monoethanolamine': r'\ce{MEA}', 'water': 'water',
         'protonated-monoethanolamine': r'\ce{MEAH+}', 'carbamate-anion': r'\ce{MEACOO-}',
         'bicarbonate-anion': r'\ce{HCO3-}', 'carbonate-anion': r'\ce{CO3^{2-}}', 'hydronium-cation': r'\ce{H3O+}', 'hydroxide-anion': r'\ce{OH-}'}
UNITS = dict(PartialPressure='Pa', PhaseMoleFraction='mole fraction', AdditionEnthalpy='kJ/mol CO2',
             amount_ratio='mol/mol total amine', pressure='Pa', phase_density='kg/m3', temperature='K',
             mole_fraction='vapour water fraction', equilibrium_isobaric_heat_capacity='J/(mol K); total analytical feed')


DISPLAY = {'Common149': 'Common-subset', 'common149': 'common subset', 'vapour': 'vapor', 'Vapour': 'Vapor', 'LogRatio': 'log ratio', 'Cai mole_fraction': 'Cai vapor water fraction', 'Vinjarapu2024': 'Vinjarapu', 'Arcis2011': 'Arcis', ' at 510000.0 Pa': ' at 0.51 MPa', ' at 1030000.0 Pa': ' at 1.03 MPa', 'kg/m3': r'\si{\kilogram\per\cubic\metre}'}
SOURCE_NAMES = {'Bottinger2008':'Böttinger et al. (2008)', 'Matin2012':'Matin et al. (2012)', 'vinjarapu2024':'Vinjarapu et al. (2024)', 'Vinjarapu2024':'Vinjarapu et al. (2024)', 'Arcis2011':'Arcis et al. (2011)', 'Amundsen2009':'Amundsen et al. (2009)', 'Hartono2014':'Hartono et al. (2014)', 'Han2012':'Han et al. (2012)', 'Jakobsen2005':'Jakobsen et al. (2005)', 'Hilliard2008':'Hilliard (2008)', 'Jou1995':'Jou et al. (1995)', 'Mamun2005':'Ma’mun et al. (2005)', 'Xu2011':'Xu and Rochelle (2011)', 'cai1996':'Cai et al. (1996)', 'kiepe':'Kiepe et al. (2002)', 'AMU':'Amundsen et al. (2009)'}
def display(value):
    value = str(value).replace('pooled', 'added together')
    parts = re.split(r'(\\cite(?:\[[^]]*\])?\{[^}]*\})', value)
    if len(parts) > 1:
        return ''.join(part if part.startswith(r'\cite') else display(part) for part in parts)
    for old, new in SOURCE_NAMES.items():
        value = value.replace(old, new)
    substitutions = {'A7': 'reported fit', 'A6': 'comparison fit', 'F1': 'density-free fit', 'restored species': 'additional species', 'canonical': 'six-source', 'packet': 'Hilliard and Jou pressures', 'pool': 'bicarbonate + carbonate total', 'endpoint': 'parameter set', 'PartialPressure':'CO2 partial pressure', 'PhaseMoleFraction':'species mole fraction', 'AdditionEnthalpy':'integral heat', 'Authority': 'Origin of limit', 'Cp': '$C_P$', 'kij': '$k_{ij}$'}
    for old, new in {**DISPLAY, **substitutions}.items():
        value = value.replace(old, new)
    return re.sub(r'(?<!\{)\bCO2\b', lambda _: r'\ce{CO2}', value)

def parameter_source(identity, fitted=False, tied=False):
    if fitted:
        return 'fitted (this work)'
    if tied:
        return 'diameter tie (this work)'
    if '/water/' in identity and '/term-' in identity:
        return 'fixed (Section~\\ref{sec:s-parameters})'
    if 'packing_diameter' in identity:
        return r'$0.88\sigma$ (this work)'
    if 'debye_huckel_diameter' in identity:
        return r'$\sigma$ (this work)'
    if 'dielectric' in identity:
        return r'\cite[Table~6]{Yang2024}' if '/water/' in identity else 'permittivity fit, Section~\\ref{sec:s-parameters}' if '/monoethanolamine/' in identity else 'assumed (this work)'
    if 'solvation_factor' in identity:
        return r'\cite[Table~2]{Figiel2025}' if '/water/' in identity else 'assumed unity (this work)'
    if 'born_diameter' in identity or identity.startswith('pair/'):
        return 'fixed model input (this work); Section~\\ref{sec:s-parameters}'
    if 'segment_count' in identity and any(x in identity for x in ['anion','cation','protonated']):
        return 'spherical ion assumption'
    if 'carbon-dioxide' in identity and not identity.startswith('association'):
        return r'\cite[Table~1]{Gross2001}'
    if '/monoethanolamine/' in identity or 'monoethanolamine(a)' in identity:
        return r'\cite[Table~2]{Baygi2015}' + ('; volume converted here' if 'volume' in identity else '')
    if any(x in identity for x in ['bicarbonate-anion','carbonate-anion','hydroxide-anion','hydronium-cation']):
        return r'\cite[Table~4]{Uyan2015}' + ('; hydrogen-ion values transferred to hydronium' if 'hydronium-cation' in identity else '')
    return 'fitted to IAPWS-95 (Section~\\ref{sec:s-parameters})'

SOURCE_CITE = {'Austgen1991_TableV_reaction_1a': r'\cite[Table~V, 1a]{Austgen1991}', 'Austgen1991_TableV_reaction_4a': r'\cite[Table~V, 4a]{Austgen1991}', 'Austgen1991_TableV_reaction_5a': r'\cite[Table~V, 5a]{Austgen1991}', 'Tong2012_Table5_K5_MEA_via_Aroua1999': r'\cite[Table~5]{Tong2012}, via \cite{arouaEquilibriumConstantCarbamate1999}', 'BatesPinching1951_equation_7': r'\cite[Eq.~10]{batesAcidicDissociationConstant1951}'}

def scientific(value):
    mantissa, exponent = re.split('[eE]', value) if re.search('[eE]', value) else (value, None)
    return mantissa + r'\times10^{' + str(int(exponent)) + '}' if exponent is not None else value

def tex(value):
    if re.fullmatch(r'-(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', str(value)):
        return '$' + scientific(str(value)) + '$'
    parts = re.split(r'(\$[^$]+\$|\\(?:ce|si|cite|ref|makecell)(?:\[[^]]*\])?\{(?:[^{}]|\{[^{}]*\})*\})', str(value))
    if len(parts) > 1:
        return ''.join(part if part.startswith(('$', r'\ce{', r'\si{', r'\cite', r'\ref{', r'\makecell')) else tex(part) for part in parts)
    if re.fullmatch(r'[-+]?\d+(?:\.\d*)?[eE][-+]?\d+', str(value)):
        return '$' + scientific(str(value)) + '$'
    if value == 'angstrom':
        return r'\AA'
    if value == 'dimensionless':
        return '1'
    escaped = ''.join({'^': r'\textasciicircum{}', '&': r'\&', '%': r'\%', '_': r'\_\allowbreak{}', '#': r'\#', '$': r'\$', '{': r'\{', '}': r'\}'}.get(c, c) for c in str(value)).replace('/', r'/\allowbreak{}')
    escaped = re.sub(r'(?<![\w.-])-(?=\d)', r'\\textminus{}', escaped)
    escaped = re.sub(r'(?<![\w.])[-+]?\d+(?:\.\d*)?[eE][-+]?\d+(?![\w.])', lambda m: '$' + scientific(m.group()) + '$', escaped)
    return re.sub(r'[a-f0-9]{64}', lambda m: r'\allowbreak{}'.join(m.group()[i:i+8] for i in range(0,64,8)), escaped)


def num(value, digits=4):
    return '--' if value is None or value == '' else f'{float(value):.{digits}g}'


def label(identity):
    water_symbols = {
        'component/water/segment_diameter/constant-plus-sum-of-exponentials/constant': r'$\sigma_0$',
        'component/water/segment_diameter/constant-plus-sum-of-exponentials/term-0/amplitude': r'$a_1$',
        'component/water/segment_diameter/constant-plus-sum-of-exponentials/term-0/exponent_coefficient': r'$b_1$',
        'component/water/segment_diameter/constant-plus-sum-of-exponentials/term-1/amplitude': r'$a_2$',
        'component/water/segment_diameter/constant-plus-sum-of-exponentials/term-1/exponent_coefficient': r'$b_2$',
    }
    if identity in water_symbols:
        return water_symbols[identity]
    if 'ionic_region_relative_permittivity' in identity:
        return r'ion-region permittivity $\varepsilon_{\mathrm{ion}}$'
    for source, name in sorted(NAMES.items(), key=lambda item: -len(item[0])):
        identity = identity.replace(source, name)
    identity = identity.replace('reciprocal_temperature_slope', 'temperature slope').replace('_', ' ')
    kind, _, rest = identity.partition('/')
    parts = rest.split('/')
    if kind == 'component':
        identity = ' '.join(parts)
    elif kind == 'pair':
        identity = parts[0] + '–' + parts[1] + ' ' + ' '.join(parts[2:]).replace('k ij', '$k_{ij}$')
    elif kind == 'association' and len(parts) >= 5:
        identity = (f'{parts[0]}–{parts[2]} association ' if parts[0] == parts[2] else f'{parts[0]}({parts[1]})–{parts[2]}({parts[3]}) association ') + ' '.join(parts[4:])
    return identity.replace(' over k', '/k').replace('debye huckel', 'Debye–Hückel').replace('born diameter', 'Born diameter').replace('reaction:', '').replace(':correlation:a k', r' $A_5$ (before enthalpy shift)').replace(':', ' ')

# Numbers in right-aligned columns are math, as in Table 1; an at-bound asterisk hangs outside the alignment.
def cell(value, kind):
    number = re.fullmatch(r'(-?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)(\*?)', str(value))
    if kind == 'r' and number:
        return '$' + scientific(number[1]) + '$' + (r'\rlap{*}' if number[2] else '')
    return tex(display(value))


# Sub-header rows that start a block of rows with a different form or unit.
def block(*cells):
    return [r'\midrule', ' & '.join(cells) + r' \\', r'\midrule']


# cols: one entry per column: 'l' label, 'r' number, or a float width (fraction of linewidth) for wrapped text.
def table(name, caption, headings, data, cols=None):
    section_order = re.findall(r'\\section\{[^}]*\}\\label\{(sec:s-[^}]+)\}', a.bind(ROOT/'docs/scientific/latex/supplement.tex').read_text())
    sections = {label: f'S{i}' for i,label in enumerate(section_order,1)}
    def section_refs(value):
        return re.sub(r'\\+ref\{(sec:s-[^}]+)\}', lambda m: sections[m[1]], str(value))
    caption = section_refs(caption)
    data = [row if isinstance(row, str) else [section_refs(value) for value in row] for row in data]
    caption = display(caption.replace('CO₂', r'\ce{CO2}'))
    caption = caption[:1].upper() + caption[1:]
    caption = re.sub(r'(?<!\\)%', r'\%', caption).replace("\\'s", "'s")
    cols = cols or 'r'*len(headings)
    spec = '@{}' + ''.join(r'>{\raggedright\arraybackslash}p{' + f'{c:.4f}' + r'\linewidth}' if isinstance(c, float) else c for c in cols) + '@{}'
    head = ' & '.join(tex(display(h)) for h in headings) + r' \\'
    body = [r'\begingroup\small\setlength{\tabcolsep}{3pt}', r'\begin{longtable}{' + spec + '}',
            r'\caption{' + caption + r'}\label{tab:' + name.removesuffix('.tex').replace('_', '-') + r'}\\',
            r'\toprule', head, r'\midrule\endfirsthead', r'\toprule', head, r'\midrule\endhead',
            r'\bottomrule\endfoot']
    body += [row if isinstance(row, str) else ' & '.join(cell(x, c) for x, c in zip(row, cols, strict=True)) + r' \\' for row in data]
    OUTPUTS[name] = '\n'.join(body + [r'\end{longtable}\endgroup', ''])


def span(values, digits=6):
    values = list(values)
    lo, hi = min(values), max(values)
    return num(lo, digits) if lo == hi else num(lo, digits) + '--' + num(hi, digits)


def comparison_label(name):
    if name == 'canonical':
        return 'Six-source pressures'
    if name == 'packet':
        return 'Hilliard and Jou pressures'
    if name == 'transfer':
        return 'Aronu et al. (2011), 15 and 45 wt%'
    if name == 'wagner':
        return 'Wagner et al. (2013)'
    if name.startswith('Wagner near '):
        return 'Wagner et al. (2013), near ' + ('353 K' if '353' in name else '392 K')
    if name.startswith('transfer '):
        return 'Aronu et al. (2011), ' + name.removeprefix('transfer ')
    if '100-120 C' in name:
        source, _, detail = name.partition(' 100-120 C')
        detail = re.sub(r' (\d+) C$', r', \1 $^\\circ$C', detail.strip())
        return ('100--120 $^\\circ$C: ' + detail if detail else 'Six-source pressures, 100--120 $^\\circ$C') if source == 'canonical' else 'Hilliard and Jou pressures, 100--120 $^\\circ$C' + (': ' + detail if detail else '')
    return name


def main():
    fit, summary, document, fitted, spec, density, heat, errors, paired = a.checked()
    a.bind(Path(__file__))
    coords = {c['identity']: c for c in fit['coordinates']}
    # Operator rows partition the eight groups; common149 is not counted again.
    groups = {}
    for r in fitted:
        groups.setdefault((r['group'], r['quantity']), []).append(r)
    objective = []
    operators = {'PartialPressure':'CO2 vapour partial pressure', 'PhaseMoleFraction':'liquid species or reported species sum',
                 'AdditionEnthalpy':'integral heat of absorption', 'amount_ratio':r'(\ce{MEAH+}, \ce{MEACOO-}, \ce{HCO3- + CO3^{2-}}) / total amine; two states',
                 'pressure':'CO2-water bubble pressure', 'phase_density':'liquid density',
                 'temperature':'MEA-water bubble temperature', 'mole_fraction':'vapour water fraction',
                 'equilibrium_isobaric_heat_capacity':'equilibrium heat capacity per mole analytical feed'}
    for (group, quantity), part in groups.items():
        def unique(key):
            return ', '.join(num(x) if key != 'form' else x for x in sorted({r[key] for r in part}, key=lambda x: float(x) if key != 'form' else x))
        scales = [float(r['scale']) for r in part]
        factor = 1000 if quantity == 'AdditionEnthalpy' else 1
        scale = [num(min(scales)/factor), '--' if len(set(scales)) == 1 else num(max(scales)/factor)]
        objective.append([group, 'liquid species fraction' if group=='restored species' else operators[quantity], 'liquid mole fraction' if group=='restored species' else UNITS[quantity], len(part), unique('form'), *scale, {1/47:'1/47',1/39:'1/39',100/9:'100/9'}.get(float(part[0]['weight']),unique('weight')), num(math.fsum(float(r['cost']) for r in part))])
    objective.append(r'\midrule')
    for group in ['common149','Cai']:
        objective.append([group+' subtotal (already included)', '--', '--', fit['groups'][group]['n'], '--', '--', '--', '--', num(fit['groups'][group]['cost'])])
    objective.append(['Objective total', '--', '--', 307, '--', '--', '--', '--', num(fit['cost'])])
    table('objective_groups.tex', r'A7 objective groups. The eight groups are disjoint and contain 307 quantities; common149 contains pressure, species and heat. Cai contains 25 temperatures and 25 vapour fractions at 25 states. Difference residuals are $(y_c-y_o)/s$; LogRatio residuals are $\ln(y_c/y_o)/s$. Cost is $\frac12\sum w r^2$. Scales are not uniformly measurement uncertainties. Where a highest scale is listed, the scale varies per observation between the two values.',
          ['Group', 'Quantity', 'Unit/basis', 'n', 'Residual', r'\makecell[rb]{Lowest\\scale}', r'\makecell[rb]{Highest\\scale}', 'Weight', 'Cost'], objective, [.16,.18,.12,'r','l','r','r','r','r'])
    residual = []
    for name in ['common149 pressure', 'common149 species', 'restored species', 'Jakobsen', 'Kiepe', 'loaded density', 'CO2-free density']:
        s = fit['groups'][name]
        residual.append([name, 'calibration; Kiepe checks fixed inputs' if name == 'Kiepe' else 'calibration', s['n'], num(s['AARD_percent']), '', ''])
    for quantity, unit in [('temperature', ' (K)'), ('mole_fraction', '')]:
        part = groups['Cai', quantity]
        s = a.stats(part)
        residual += [*block('', '', '', 'RMSE' + unit, 'Bias' + unit, ''), ['Cai ' + quantity, 'calibration', len(part), num(s['RMSE']), num(s['bias']), '']]
    residual += block('', '', '', r'\makecell[rb]{RMSE\\(kJ/mol \ce{CO2})}', r'\makecell[rb]{Bias\\(kJ/mol \ce{CO2})}', '')
    for name, s in summary['heat'].items():
        residual.append([name, 'calibration' if name == 'Vinjarapu2024' else 'used to accept fits', s['n_total'], num(s['RMSE']), num(s['bias']), ''])
    residual += block('', '', '', r'Signed error (\%)', '$T$ (K)', 'Loading')
    for r in a.rows(a.E / 'cp.csv'):
        residual.append(['Hilliard Cp', 'calibration', 1, num(r['error_percent']), r['T_K'], r['loading']])
    table('residual_summary.tex', r'A7 property deviations. AARD denotes average absolute relative deviation. Fitted deviations and the Arcis comparison do not establish physical validation; Cai deviations are in K and mole fraction. Cp remains on its source mass basis.',
          ['Data set', 'Role', 'n', 'AARD (%)', '', ''], residual, ['l',.24,'r','r','r','r'])
    parameter_rows, pair_rows = [], []
    for kind in ['components', 'pairs']:
        for node in document[kind]:
            for c in node['coefficients']:
                identity = c['identity']
                tie = any(t['identity'] == identity for x in fit['coordinates'] for t in x['ties'])
                row = [label(identity), num(c['value']['magnitude'], 6), c['value']['unit'], parameter_source(identity, identity in coords, tie)]
                if 'reference_temperature' in c:
                    assert c['reference_temperature'] == {'magnitude': 313.15, 'unit': 'kelvin'}
                if kind == 'pairs' and 'carbon-dioxide/water' in identity:
                    row[-1] = r'Kiepe pressure fit, Section~\\ref{sec:s-parameters} \cite{kiepeExperimentalDeterminationPrediction2002}'
                (parameter_rows if kind == 'components' else pair_rows).append(row)
    for node in document['correlations'] + document['model_coefficients'] + document['topology']['edges']:
        for identity, c in a.coefficients(node):
            source = r'\cite[Eqs.~5--10]{Figiel2025}' if 'ionic_region' in identity else 'induced association; half water energy and water volume' if 'carbon-dioxide' in identity else parameter_source(identity)
            parameter_rows.append([label(identity), num(c['value']['magnitude'],6), c['value']['unit'], source])
    table('full_ionic_ssm_ds_parameters.tex', r'Species, association and correlation inputs. Lengths are in angstrom, energies divided by Boltzmann constant in kelvin. Ion packing diameters are $0.88\sigma$ and Debye--H\"uckel diameters equal $\sigma$. CO2, MEA and water each have one donor and one acceptor site; CO2 associates only with water. MEA--water association follows the Wolbach--Sandler rule. Fixed model inputs and assumptions for use in reacting mixtures are explained in Section~\\ref{sec:s-parameters}.',
          ['Parameter', 'Value', 'Unit', 'Source or estimation'], parameter_rows, ['l','r','l',.43])
    table('binary_interaction_parameters.tex', r'Binary interactions. Slopes multiply $(1/T-1/T_{\rm ref})$ with $T_{\rm ref}=313.15$ K. All fixed ion interactions are model assumptions, rather than measured pair energies. Dispersion between ions of the same charge sign is excluded.',
          ['Parameter', 'Value', 'Unit', 'Source or estimation'], pair_rows, ['l','r','l',.43])
    reaction = a.load(a.ROOT / 'data/reference/MEA/manifests/chemical_reaction_source_contract.json')
    offsets = reaction['common_source_standard_state']['source_to_common_ln_k_offsets']
    assert offsets[3] == offsets[4] == 0
    reaction_rows = []
    for r in reaction['reactions']:
        rid = r['reaction_id']
        selected = next((x for x in document['reaction_correlations'] if x['reaction_id'] == rid), None)
        values = ({label(c['identity'].split(':')[-1]).split()[0].upper(): c['value']['magnitude'] for c in selected['coefficients']} if selected
                  else {k.split('_')[0].upper(): v for k, v in r['correlation'].items() if k != 'kind'})
        lhs, rhs = (r'\ce{' + side.replace('CO3--', 'CO3^{2-}').replace('HCO3-', 'HCO3^-') + '}' for side in r['equation'].split(' <=> '))
        cells = ['$' + num(values[k], 6) + '$' if k in values else '--' for k in 'ABCD']
        if rid == 'R5':  # pK form: its A5, B5, C5 sit under a sub-header in the A, B, C columns
            cells[3] = ''
            reaction_rows += [r'\midrule', r' & & $A_5$ (K) & $B_5$ & $C_5$ (K$^{-1}$) & & & \\', r'\midrule']
        reaction_rows.append(' & '.join([rid, lhs + r' $\rightleftharpoons$ ' + rhs, *cells, '--'.join(num(x, 6) for x in r['temperature_range_k']), SOURCE_CITE[r['selected_source']]]) + r' \\')
    caption = (r'Reaction equilibrium constants for the reported parameters. R1--R4 use $\ln K=A+B/T+C\ln T+DT+\Delta_r$ and R5 uses $\mathrm{p}K=A_5/T+B_5+C_5T$, with $T$ in K; a dash marks a term the correlation does not include. '
               r'R1 and R3 are fixed source laws; R2, R4 and R5 list the selected coefficients, and the R2 and R5 coefficients already include the fitted shifts. '
               r'The offset $\Delta_r$ converts each source to the common aqueous molality standard, 1 mol/kg at infinite dilution in water: it is ' + num(offsets[0]) + ' for R1 and ' + num(offsets[2])
               + r' for R3, is already included in the R2 coefficients and is zero for R4 and R5. Source ranges are not validation domains.')
    head = r' & Reaction & $A$ & $B$ (K) & $C$ & $D$ (K$^{-1}$) & Range (K) & Source \\'
    OUTPUTS['reaction_equilibrium_constants.tex'] = '\n'.join([r'\begingroup\small\setlength{\tabcolsep}{3pt}', r'\begin{longtable}{@{}llrrrrll@{}}',
        r'\caption{' + caption + r'}\label{tab:reaction-equilibrium-constants}\\', r'\toprule', head, r'\midrule\endfirsthead', r'\toprule', head,
        r'\midrule\endhead', r'\bottomrule\endfoot', *reaction_rows, r'\end{longtable}\endgroup', ''])
    coordinate_rows = []
    for c, se in zip(fit['coordinates'], errors, strict=True):
        factor = .001 if c['unit'] in ['joule / mole', 'J/mol'] else 1
        coordinate_rows.append([label(c['identity']), num(c['value']*factor), 'kJ/mol' if factor != 1 else c['unit'],
                                *(num(v*factor) for v in c['bounds']),
                                '--' if se['bound_active'] == 'True' else num(float(se['conditional_standard_error'])*factor)])
    table('supplement_fitted_parameters.tex', r'Sixteen fitted parameters and conditional standard errors (SE). Errors depend on weights, fixed inputs, bounds and local linearization. Born and segment diameters are separate; packing diameter is $0.88\sigma$ and Debye--H\"uckel diameter is $\sigma$. The R5 reciprocal-temperature coefficient precedes its enthalpy shift; R2/R5 shifts are total adjustments. Full optimizer transformations are in the data deposit. A dash marks a parameter at a bound, for which no conditional SE is reported.',
          ['Parameter', 'Value', 'Unit', 'Lower bound', 'Upper bound', 'Conditional SE'], coordinate_rows, 'lrlrrr')
    table('fitted_coordinates.tex', r'Sixteen fitted parameters and final bounds. An asterisk marks a parameter at a bound. Interactions and slopes use 313.15 K as reference temperature. Born and segment diameters are separate. R5 $A_5$ is specified before the enthalpy shift; R2/R5 shifts are total adjustments already included in the reaction coefficients. Section~\\ref{sec:s-uncertainty} gives conditional errors.',
          ['Parameter', 'Value', 'Unit', 'Lower bound', 'Upper bound'],
          [[r[0], r[1]+('*' if r[5]=='--' else ''), *r[2:5]] for r in coordinate_rows], 'lrlrr')
    uncertainty = a.load(a.E / 'conditional-uncertainty.json')
    correlations = a.rows(a.E / 'conditional-correlations.csv')
    free = uncertainty['free_coordinates']
    assert len(free) == uncertainty['free_rank'] == 10 and uncertainty['degrees_of_freedom'] == 297
    corr = {(r['coordinate_a'],r['coordinate_b']): float(r['correlation']) for r in correlations}
    corr_rows = [[str(i+1)]+[num(corr[n,m],3) if k <= i else '' for k,m in enumerate(free)] for i,n in enumerate(free)]
    table('supplement_correlations.tex', r'Lower-triangular conditional correlation matrix. Ten free parameters have rank ten and 297 degrees of freedom; variance factor ' + num(uncertainty['residual_variance']) + r'. Parameter order: ' + tex('; '.join(str(i+1)+': '+label(n) for i,n in enumerate(free))) + '.',
          ['Parameter']+[str(i+1) for i in range(10)], corr_rows)
    old = a.load(a.E / 'predecessor-f1.json')
    old_engine = a.load(a.F / 'evaluation/execution.json')
    for path, digest in old['inputs'].items():
        a.bind(a.ROOT / path)
        assert a.INPUTS[path] == digest
    comparison = [r for r in a.rows(a.F / 'fit-comparison.csv') if r['objective'] == 'with heat']
    f1 = next(r for r in comparison if r['problem'] == 'F1')
    oldheat = [r for r in a.rows(a.F / 'heat-comparison.csv') if r['record'] == 'heat F1' and not r['pressure_Pa']]
    native = a.load(a.F / 'F1-A/native-fit.json')
    common = {r['id']: r for r in fitted if r['group'] == 'common149'}
    assert set(native['targets']) == set(common) and len(common) == 149
    for identity, obs, pred, residual in zip(native['targets'], native['observed'], native['predictions'], native['weighted_residuals'], strict=True):
        r = common[identity]
        a.close(obs, r['observed'])
        raw = math.log(pred/obs) if r['form'] == 'LogRatio' else pred-obs
        a.close(raw/float(r['scale'])*math.sqrt(float(r['weight'])), residual)
    predecessor = [[q, n, num(f1[key]), num(fit['groups'][group]['AARD_percent']), '%'] for q,n,key,group in
                   [('Pressure AARD',47,'pressure_AARD_percent','common149 pressure'),('Species AARD',94,'species_AARD_percent','common149 species')]]
    predecessor += [['Vinjarapu RMSE',8,num(next(x['RMSE_kJ_mol'] for x in oldheat if x['source']=='Vinjarapu2024')),num(summary['heat']['Vinjarapu2024']['RMSE']),'kJ/mol CO2'],
                    ['Common-subset cost',149,num(f1['cost']),num(fit['groups']['common149']['cost']),'dimensionless']]
    old_density = a.rows(a.F / 'corrected-densities.csv')
    old_states = a.load(a.F / 'density-states.json')
    assert len(old_states) == len(old_density) == 68
    assert all(x['solved_state']['phases'][0]['pressure_pa'] == 101325 for x in old_states)
    a.bind(a.BUNDLE / 'scripts/heat_evidence_170.py')
    matched = []
    for r in old_density:
        matches = [d for d in density if d['source']=='Amundsen2009' and float(d['P_Pa'])==100000 and all(float(d[k])==float(r[field]) for k,field in [('T_K','temperature_K'),('loading','loading'),('mea_mass_fraction','mea_mass_fraction')])]
        assert len(matches) <= 1
        if matches:
            d=matches[0]
            a.close(d['observed_kg_m3'],r['observed_kg_m3'])
            matched.append((r,d))
    assert matched
    for title, key in [('Density-free-fit density','eos_density_kg_m3'),('Reported-fit density','predicted_kg_m3')]:
        part=[{'observed':r['observed_kg_m3'],'predicted':r[key] if key in r else d[key]} for r,d in matched]
        predecessor.append([title+' matched AARD',len(part),num(a.stats(part)['AARD_percent']) if key=='eos_density_kg_m3' else '--',num(a.stats(part)['AARD_percent']) if key!='eos_density_kg_m3' else '--','%'])
    table('supplement_predecessor.tex', r'Density-free and reported fits on the shared 149 calibration quantities and 68 matched Amundsen densities. Density states match temperature, loading and unloaded-solvent composition; calculation pressures are 101325 and 100000 Pa, respectively (1325 Pa difference). No density-pressure derivative is retained, so this difference is not corrected. Density-free calculations retain their software identity, listed in the deposit README.',
          ['Metric', 'n', 'Density-free fit', 'Reported fit', 'Unit'], predecessor, 'lrrrl')
    OUTPUTS['supplement_predecessor.tex'] += '% Temperature/loading/mass-fraction matched IDs (pressure disclosed, not matched): '+', '.join(d['id'] for _,d in matched)+'\n'
    OUTPUTS['supplement_predecessor.tex'] += '% F1 excluded rows: none. A7 rows outside baseline: '+', '.join(d['id'] for d in density if d['id'] not in {x['id'] for _,x in matched})+'\n'
    fixed = a.J / 'amendment-7/fixed-study/wheel-8298c602'
    endpoints = ['after-adoption/a6-selected','restricted-endpoint','restricted-2-endpoint']
    scores = [a.load(fixed / p / 'score.json') for p in endpoints]
    a6_provenance = a.load(a.J/'amendment-6/selected-assessment/provenance.json')
    first_endpoint = a.bind(a.J/'amendment-7/restricted/fit/usable-budget-endpoint.json')
    assert a.INPUTS[str(first_endpoint.relative_to(a.ROOT))] == scores[1]['parameter_sha256']
    comparison_identities = dict(A6_original_assessment=a.record_identity(a6_provenance['parameter_sha256'], a6_provenance['engine']),
                                **{name: a.phase_identity(fixed/path, fit['engine']) for name,path in zip(['A6_after_adoption','First_A7','Accepted_A7'], endpoints, strict=True)})
    a.bind(a.J / 'amendment-7/restricted/README.md')
    reductions = [a.load(fixed / p / 'reduction.json') for p in endpoints]
    acceptance = []
    for title,key,limit,authority,f1value in [('Common-subset cost','C149','35.26','F1 value + 10% (rounded)',f1['cost']),('Pressure AARD (%)','pressure_AARD_pct','15.81','F1 value + 2 percentage points (rounded)',f1['pressure_AARD_percent']),('Species AARD (%)','species_AARD_pct','9.89','F1 value + 2 percentage points (rounded)',f1['species_AARD_percent']),('Vinjarapu RMSE (kJ/mol)','vinjarapu_rmse_kJ_mol','3.13','F1 value + 1 kJ/mol (rounded)',next(x['RMSE_kJ_mol'] for x in oldheat if x['source']=='Vinjarapu2024')),('Loaded within 2s','loaded_within_2s','47/47','density requirement (Section~\\ref{sec:s-density})',''),('Cai cost','cai_cost','95.90','constant-interaction Cai cost + 5% (rounded)','')]:
        acceptance.append([title,limit,authority,num(f1value) if f1value!='' else '--']+[num(scores[i][key]) for i in [0,2]])
    acceptance.append(['States with detected instability','0/73','finite search at the specified states','--']+[str(sum(x['resolved_trials']>0 for x in reductions[i]))+'/73' for i in [0,2]])
    acceptance.append(['CO2-free max absolute error (kg/m3)','1.0','density requirement','--']+[num(max(abs(x) for x in scores[i]['co2_free_errors'].values())) for i in [0,2]])
    acceptance.append(['Total cost (307 quantities)','--','not comparable with the density-free-fit cost','--']+[num(scores[i]['cost']) for i in [0,2]])
    for name,ceiling in [('Arcis2011',9.36)]:
        a6=a.load(a.J/'amendment-6/selected-assessment/summary.json')
        acceptance.append(['Arcis RMSE (kJ/mol)',num(ceiling),'F1 value + 1 kJ/mol (rounded)',num(next(x['RMSE_kJ_mol'] for x in oldheat if x['source']==name)),num(a6['heat'][name]['RMSE']),num(summary['heat'][name]['RMSE'])])
    table('acceptance_limits.tex', r'Study-specific limits and values for the density-free, comparison and reported fits. Section~\\ref{sec:s-fits} explains the tolerances.',
          ['Quantity','Limit','Origin of limit',r'\makecell[rb]{Density-free\\fit}',r'\makecell[rb]{Comparison\\fit}',r'\makecell[rb]{Reported\\fit}'],acceptance,[.24,'r',.31,'r','r','r'])
    state = a.rows(a.E/'state-targets.csv')
    source_rows, cai_rows = [], []
    meta = {r['target']:r for r in state if r['kind']=='packet'}
    by_source = {}
    for r in fitted:
        source = meta.get(r['id'],{}).get('source', r['id'].split('_')[0].split('-')[0])
        by_source.setdefault((source,r['group'],r['quantity']),[]).append(r)
    for (source,group,quantity), part in by_source.items():
        row = [source,group,label(quantity),len(part),num(a.stats(part)['RMSE' if group=='Cai' else 'AARD_percent']),num(math.fsum(float(r['cost']) for r in part))]
        (cai_rows.extend([*block('', '', '', '', 'RMSE (K)' if quantity=='temperature' else 'RMSE', ''), row]) if group=='Cai' else source_rows.append(row))
    table('supplement_source_aard.tex',r'A7 calibration deviations by source, group and observable. Deviation is AARD in percent except Cai RMSE in K or vapour water mole fraction. It does not combine quantities into an accuracy ranking. Entry costs add to the total objective cost of 148.9; quantity definitions, units and weights are in Section~\\ref{sec:s-objective}.',
          ['Source','Group','Observable','n','AARD (%)','Cost'],source_rows+cai_rows,['l','l',.22,'r','r','r'])
    outside=[]
    for name,s in a.load(a.E/'state-summary.json')['scores'].items():
        part = [r for r in state if r['identity'] in s['state_ids'] and r['target'] in s['row_ids'] and r['target'] not in common and r['target'] not in {x['id'] for x in fitted}]
        if part and not name.startswith('packet 100-120 C '):
            score = a.stats(part)
            bias = math.fsum(math.log(float(r['predicted'])/float(r['observed'])) for r in part)/len(part)
            row = [comparison_label(name), len(part), num(score['AARD_percent']), num(bias)]
            if row not in outside:
                outside.append(row)
    table('supplement_outside_fit.tex',r'A7 comparisons outside the fit. Fitted observations are removed from each set; sets overlap and are not additive. None of these observations was fitted; all were compared with intermediate parameter sets during model development, so none is a blind test. Hilliard and Jou pressures are the 79 Jou and Hilliard pressures used in the pressure and species calculations, 47 of them fitted.',
          ['Data set','n','AARD (%)','Mean ln(calc/obs)'],outside,'lrrr')
    loaded_ids=set(spec['loaded_density_ids'])
    excluded=set(summary['density']['Amundsen source-conflict five']['row_ids'])
    free_ids=set(summary['density']['Amundsen CO2-free gate five']['row_ids'])
    density_rows=[]
    for source in sorted({r['source'] for r in density}):
        part=[r for r in density if r['source']==source]
        density_rows.append([source,len(part),sum(r['id'] in loaded_ids|free_ids for r in part),num(min(float(r['T_K']) for r in part),6),num(max(float(r['T_K']) for r in part),6),num(min(float(r['error_kg_m3']) for r in part)),num(max(float(r['error_kg_m3']) for r in part)),num(a.stats([dict(observed=r['observed_kg_m3'],predicted=r['predicted_kg_m3']) for r in part])['RMSE'])])
    table('supplement_carbonate_density.tex',r'Density comparison without volume translation. All 210 observed/calculated values, pressures, compositions, scales and exclusions are supplied as CSV in the data deposit. Errors and RMSE are in kg/m3. Five Amundsen loading-0.4 observations are excluded from fitting.',
          ['Source','n','Fitted',r'$T_{\min}$ (K)',r'$T_{\max}$ (K)','Lowest error','Highest error','RMSE'],density_rows,'lrrrrrrr')
    previous=OUTPUTS['supplement_carbonate_density.tex']
    carbonate=a.rows(a.E/'carbonate-share.csv')
    table('supplement_carbonate_density.tex',r'All ten carbonate-share comparisons (different observables from the six fitted Jakobsen amount ratios). Corrected unloaded MEA mass fraction is '+num(float(carbonate[0]['mea_mass_fraction']))+r'; model loading uses NMR. Source: Jakobsen et al.\ \cite{Jakobsen2005}, Tables A1--A2 (p.~9902) and Table~2 (p.~9896).',
          ['Row','T (K)','NMR loading','Maximum loading','Observed share','Calculated share','Calc/obs'],[[i,r['T_K'],num(r['model_loading']),num(r['maxload']),num(r['observed_share']),num(r['predicted_share']),num(r['calc_over_obs'])] for i,r in enumerate(carbonate,1)])
    OUTPUTS['supplement_carbonate_density.tex']=previous+OUTPUTS['supplement_carbonate_density.tex'].replace('tab:supplement-carbonate-density','tab:supplement-carbonate-share')
    reference_rows=[]
    loadings=sorted({float(r['loading']) for i,r in paired['A7'].items() if i})
    temperatures=sorted({float(r['temperature_K']) for r in paired['A7'].values()})
    for loading in loadings:
        pressures=[]
        for temperature in temperatures:
            part=sorted([float(r['pressure_Pa']) for i,r in paired['A7'].items() if i and float(r['loading'])==loading and float(r['temperature_K'])==temperature])
            assert len(part)==3 and all(math.isclose(p/part[0],factor/.5,rel_tol=1e-12) for p,factor in zip(part,[.5,.8,.95]))
            pressures.append(num(part[0]/.5/1000,7))
        reference_rows.append([num(loading,8)]+pressures)
    table('phase_reference_pressures.tex',r'Fixed reference pressures $P_*$ in kPa defining the test grid. Each row generates three pressure levels at each temperature. The additional pressure-rounded state is described in the text.', ['Loading']+[num(t,6)+' K' for t in temperatures],reference_rows)
    phase_rows=[]
    for temperature in sorted({float(r['temperature_K']) for r in paired['A7'].values()}):
        part=[i for i,r in paired['A7'].items() if float(r['temperature_K'])==temperature]
        phase_rows.append([num(temperature,6),len(part),sum(int(paired['A6'][i]['resolved_trials'])>0 for i in part),sum(int(paired['A7'][i]['resolved_trials'])>0 for i in part)])
    table('supplement_phase_family.tex',r'Phase-search summary for both fits. The complete 73-state temperature, pressure, loading and trial data are supplied as CSV in the data deposit. One 318.15 K state (loading 0.2556) is evaluated twice, once at its pressure rounded to 5918.5286 Pa; both evaluations are counted. Two-phase classifications include liquid--vapor equilibrium.',
          ['T (K)','Test states','Comparison fit','Reported fit'],phase_rows)
    previous=OUTPUTS['supplement_phase_family.tex']
    extension = a.BUNDLE/'results/phase-extension-201/run-3'
    outcomes = a.rows(extension/'outcomes-by-temperature.csv')
    counts = a.rows(extension/'counts-by-temperature.csv')
    assert sum(int(r['completed']) for r in outcomes if r['record']=='A7') == 60
    assert all(int(r['parent_numerical_failures']) == int(r['failed_trial_optimizers']) == 0 for r in counts)
    extension_counts = [[r['record'], r['temperature_K'], r['scheduled_states'], r['unavailable_pressure'], r['completed'], r['returned_trials'], r['resolved_trials'], r['descent_states']] for r in outcomes]
    table('phase_extension.tex',r'Extended phase-search counts by temperature and fit. Declared states with reference pressure above 10 MPa are excluded before the search. All trial optimizations at admitted states complete, with no unresolved trials or numerical failures.',
          ['Fit','T (K)','Declared','Excluded','Searched','Trials','Descending trials','Instability states'],extension_counts,'lrrrrrrr')
    previous_extension = OUTPUTS['phase_extension.tex']
    reference = [r for r in a.rows(extension/'reference-pressure/reference-pressures.csv') if float(r['fraction']) == 1.]
    reference_temperatures = sorted({float(r['temperature_K']) for r in reference})
    reference_values = {(float(r['temperature_K']),float(r['loading'])):float(r['pressure_Pa'])/1000 for r in reference}
    table('phase_extension.tex',r'Frozen extension reference pressures $P_*$ in kPa. Each row generates pressures of 0.50, 0.80 and 0.95 times $P_*$. References above 10000 kPa exclude all three states; the reference values were reused unchanged.',
          ['Loading']+[num(t,6)+' K' for t in reference_temperatures],
          [[num(alpha,8)]+[num(reference_values[t,alpha],7) for t in reference_temperatures] for alpha in sorted({float(r['loading']) for r in reference})])
    OUTPUTS['phase_extension.tex'] = previous_extension + OUTPUTS['phase_extension.tex'].replace('tab:phase-extension','tab:phase-extension-references')
    previous_extension = OUTPUTS['phase_extension.tex']
    confirmations = list({r['path']:r for r in a.rows(extension/'split-confirmations.csv')}.values())
    assert len(confirmations) == 27 and sum(r['confirmed']=='True' for r in confirmations) == 23
    states = {int(r['index']):r for r in a.rows(extension/'inputs/states.csv')}
    confirmation_rows = []
    for index in sorted({int(r['index']) for r in confirmations}):
        part = [r for r in confirmations if int(r['index']) == index]
        extension_state = states[index]
        confirmation_rows.append([extension_state['temperature_K'],num(extension_state['loading']),num(float(extension_state['pressure_Pa'])/1000,7),len(part),sum(r['confirmed']=='True' for r in part)])
    assert len(confirmation_rows)==21 and sum(row[-1]>0 for row in confirmation_rows)==17
    table('phase_extension.tex',r'Separately seeded two-liquid confirmations for the comparison fit in the extension. Attempts count distinct split solves; repeated trial seeds that share one solve are counted once. Confirmations occur at 17 of 21 tested instability states, in 23 of 27 attempts.',
          ['T (K)','Loading','P (kPa)','Attempts','Confirmed'],confirmation_rows)
    OUTPUTS['phase_extension.tex'] = previous_extension + OUTPUTS['phase_extension.tex'].replace('tab:phase-extension','tab:phase-extension-confirmations')
    adoption = a.load(a.BUNDLE/'results/engine-3e83e19c-adoption/adoption-check.json')
    engine = a.load(a.BUNDLE/'results/engine-3e83e19c-adoption/checks.json')['candidate_wheel']
    assert adoption['summary']['accepted_split_changes']['retained_engine'] == engine['commit']
    assert engine['sha256'] == '0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804'
    split_rows=[]
    split_phases=[]
    for i in [21,63,70]:
        for r in a.load(a.BUNDLE/f'results/engine-3e83e19c-adoption/A6-supplement-splits/split-seeded-{i}.json'):
            seed = r['seed'].replace('positive-neutral-base','uniform').replace('near-pure-0','CO2-rich').replace('near-pure-1','MEA-rich').replace('near-pure-2','water-rich')
            phases = r['result'].get('phases', [])
            for phase in phases:
                split_phases.append([i,seed,phase['identity'],num(phase['amount_mol']),num(phase['molar_density_mol_m3']),*(num(x) for x in phase['mole_fractions']),*['--']*(len(NAMES)-len(phase['mole_fractions']))])
            first = [i,seed,'yes' if r['result']['success'] else 'no',num(r['delta_G_over_RT_vs_original'],5),num(r['delta_G_over_RT_vs_single_liquid'],5)]
            split_rows += ([r'\addlinespace'] if split_rows else []) + ([(first if k == 0 else ['']*5)+[p['identity'],p['role'],num(v)] for k,(p,v) in enumerate(zip(phases,r['result']['molar_densities'],strict=True))] or [first+['--']*3])
    table('supplement_phase_family.tex',r'Separately seeded A6 split solves, including failed attempts. Gibbs differences are extensive $\Delta G/(RT)$ values in mol for 9.7292821 mol analytical MEA, 76.9751925 mol water and 9.7292821 times loading mol CO2; phase densities are mol/m3. States 21, 63 and 70 are $(T,\alpha,P/\mathrm{kPa})=(313.15,0.1,4.737142)$, $(333.15,0.4,21.78783)$ and $(333.15,0.5,38.28678)$. Only successful split solves support the split comparison.',
          ['State','Seed','Success',r'\makecell[rb]{Delta vs\\original (mol)}',r'\makecell[rb]{Delta vs single\\liquid (mol)}','Phase','Role',r'Density (\si{\mole\per\cubic\metre})'],split_rows,'rllrrllr')
    OUTPUTS['supplement_phase_family.tex']=previous+OUTPUTS['supplement_phase_family.tex'].replace('tab:supplement-phase-family','tab:supplement-split-states')
    previous=OUTPUTS['supplement_phase_family.tex']
    table('supplement_phase_family.tex', r'A6 successful split phase amounts (mol), densities (mol/m3) and mole fractions in source order: CO2, MEA, water, MEAH+, carbamate, bicarbonate, carbonate, hydronium, hydroxide. Vapour rows list only their three supported neutral species (CO2, MEA, water); liquid rows list all nine.',
          ['State','Seed','Phase',r'\makecell[rb]{Amount\\(mol)}',r'\makecell[rb]{Density\\(\si{\mole\per\cubic\metre})}',*NAMES.values()],split_phases,'rllrr'+'r'*len(NAMES))
    OUTPUTS['supplement_phase_family.tex']=previous+'\\begin{landscape}\n'+OUTPUTS['supplement_phase_family.tex'].replace('tab:supplement-phase-family','tab:supplement-split-compositions')+'\\end{landscape}\n'
    inventory=[]
    meta_by_target={r['target']:r for r in state if r['kind']=='packet'}
    for (source,group,quantity),part in by_source.items():
        states=[meta_by_target[r['id']] for r in part if r['id'] in meta_by_target]
        if states:
            domain=span(float(r['temperature_K']) for r in states)+' K; loading '+span((float(r['loading']) for r in states), 4)
        elif group in ['loaded density','CO2-free density']:
            states=[r for r in density if r['id'] in (loaded_ids if group=='loaded density' else free_ids) and (r['source']==source or group=='CO2-free density')]
            domain=span(float(r['T_K']) for r in states)+' K; loading '+span((float(r['loading']) for r in states), 4)
        else:
            domain={'common149':'313.15 K; 1.734 MPa; 30 wt%','Cai':'Binary MEA--water; 66.66/101.33 kPa','Kiepe':'Binary CO2--water; 313.20--393.17 K','Cp':'318.15/353.15 K; loading 0/0.358; 7 mol/kg water','Jakobsen':'293.15/313.15 K; NMR composition'} .get(group,'source states in electronic data')
        inventory.append([source,'liquid species fraction' if group=='restored species' else 'equilibrium heat capacity' if group=='Cp' else operators.get(quantity,quantity),len(part),domain,'fitted'])
    inventory.append(r'\midrule')
    for source,n,domain,role in [('Six-source pressure',159,'313.00--393.15 K; nominal 30 wt%','47 fitted; remainder compared'),('Wagner',23,'near 353/392 K; 30 wt%','not fitted; not blind'),('Aronu et al. (2011)',70,'15/45 wt%; source states','not fitted; not blind'),('Arcis',14,'322.5 K; 0.51/1.03 MPa','used to accept fits'),('Matin bicarbonate + carbonate',19,'293.15 K approximation; 30 wt%','compared'),('Jakobsen carbonate share',10,'293.15/313.15 K; diluted NMR samples','compared'),('All densities',210,'293.15--393.15 K; 20--100 wt%','52 fitted; others compared')]:
        inventory.append([source,'pressure' if 'pressure' in source or source=='Aronu et al. (2011)' else 'heat' if source=='Arcis' else 'density' if source=='All densities' else 'pressure' if source=='Wagner' else 'species',n,domain,role])
    table('supplement_data_roles.tex', r'Experimental data and their use by source. Counts in comparison sets overlap fitted observations and are not additive. Exact states, source locators and exclusions are in the electronic data. Pressure and species calculations use each source\'s reported solvent composition.',
          ['Source','Property','n','Conditions','Role'],inventory,['l',.2,'r',.27,.16])
    species_states = [meta_by_target[r['id']] for r in fitted if r['quantity']=='PhaseMoleFraction' or r['group']=='restored species']
    fitted_density_states = [r for r in density if r['id'] in loaded_ids]
    data_rows = [
        [r'Hilliard, Jou \cite{Hilliard2008,Jou1995}', 'CO2 partial pressure', fit['groups']['common149 pressure']['n'], '30 wt%; source states', 'fitted'],
        [r'Böttinger, Matin \cite{Bottinger2008,matinFacileMethodDetermination2012}', 'Species fractions', fit['groups']['common149 species']['n']+fit['groups']['restored species']['n'], span(float(r['temperature_K']) for r in species_states)+' K; source compositions', 'fitted'],
        [r'Jakobsen \cite{Jakobsen2005}', 'Species/total-amine ratios', fit['groups']['Jakobsen']['n'], '293.15/313.15 K; diluted samples', 'fitted'],
        [r'Vinjarapu \cite{HemaBhavya2025}', 'Integral heat', fit['groups']['common149 heat']['n'], '313.15 K; 1.734 MPa; 30 wt%', 'fitted'],
        [r'Amundsen, Hartono \cite{Amundsen2009,Hartono2014}', 'Loaded density', len(loaded_ids), span(float(r['T_K']) for r in fitted_density_states)+' K; 30 wt%', 'fitted'],
        [r'Amundsen \cite{Amundsen2009}', 'CO2-free density', len(free_ids), '298.15--353.15 K; 30 wt%', 'fitted'],
        [r'Cai \cite{caiBinaryIsobaricVaporLiquid1996}', 'Bubble T; vapor fraction', fit['groups']['Cai']['n'], 'MEA--water; 66.66/101.33 kPa', 'fitted; 25 states'],
        [r'Kiepe \cite{kiepeExperimentalDeterminationPrediction2002}', 'CO2--water pressure', fit['groups']['Kiepe']['n'], '313.20--393.17 K', 'fitted earlier; fixed input check'],
        [r'Hilliard \cite{Hilliard2008}', 'Heat capacity', fit['groups']['Cp']['n'], '318.15/353.15 K; 7 mol MEA/kg water', 'fitted'],
        r'\midrule',
        ['Six-source pressure comparison', 'CO2 partial pressure', 159, '313.00--393.15 K; nominal 30 wt%', '47 fitted; 112 not fitted'],
        [r'Wagner \cite{wagnerSolubilityCarbonDioxide2013}', 'CO2 partial pressure', 23, 'near 353/392 K; 30 wt%', 'not fitted; not blind'],
        [r'Aronu \cite{Aronu2011}', 'CO2 partial pressure', 70, '15/45 wt%; source states', 'not fitted; not blind'],
        [r'Arcis \cite{arcisEnthalpySolutionCarbon2011}', 'Integral heat', 14, '322.5 K; 0.51/1.03 MPa', 'not fitted; used to accept fits'],
        ['Matin', 'Bicarbonate total', 19, 'source states', 'not fitted'],
        ['Jakobsen', 'Carbonate share', 10, 'source states', 'not fitted'],
        [r'Amundsen, Hartono, Han \cite{hanDensityWater12012}', 'All densities', len(density), '293.15--393.15 K; 20--100 wt%', '52 fitted; others compared']]
    table('current_data_inventory.tex', r'Fitted and compared observations. Counts in comparison sets overlap fitted observations and are not additive. Section~\\ref{sec:s-objective} defines the objective. Source-specific conditions and roles are listed in the supplement.',
          ['Source','Quantity','n','Conditions','Use'],data_rows,['l',.21,'r',.25,.15])
    failures=[r for r in density if r['id'] in loaded_ids and abs(float(r['error_over_s']))>2]
    assert len(failures)==3 and all(float(r['T_K'])==353.15 for r in failures)
    table('density_failures.tex',r'Three fitted loaded densities outside $\pm2s$ at \SI{353.15}{\kelvin}. Error is calculated minus observed.',
          ['Source','Loading','Error (kg/m3)','$e/s$'],[[r['source'],num(r['loading']),num(r['error_kg_m3'],3),num(r['error_over_s'],3)] for r in failures],'lrrr')
    scales=a.load(a.J/'amendment-6/inputs/without-amundsen-0p4/density-scales.json')
    scale_rows=[]
    for source in ['Amundsen2009','Hartono2014']:
        part=[r for r in scales if r['source']==source]
        scale_rows.append([source,num(min(r['u_rho'] for r in part)),num(min(r['u_alpha'] for r in part)),num(max(r['u_alpha'] for r in part)),num(min(r['scale'] for r in part)),num(max(r['scale'] for r in part)),'2% of loading; density uncertainty scope unresolved at high T/loading' if source=='Amundsen2009' else 'loading 0.01; density expanded k=2 value used without division'])
    table('density_scales.tex',r'Source inputs for $s_\rho=[u_\rho^2+(g u_\alpha)^2]^{1/2}$. Density scales are in kg/m3 and loading is mol CO2/mol total amine. Exact secant pairs and per-observation scales are in the deposit.', ['Source',r'$u_\rho$',r'\makecell[rb]{Lowest\\$u_\alpha$}',r'\makecell[rb]{Highest\\$u_\alpha$}',r'\makecell[rb]{Lowest\\$s_\rho$}',r'\makecell[rb]{Highest\\$s_\rho$}','Qualification'],scale_rows,['l','r','r','r','r','r',.3])
    conflicts=[r for r in a.load(a.J/'amendment-6/density-sweep-1b/summary.json')['source_disagreement'] if r['loading']==.4]
    table('density_source_differences.tex',r'Amundsen minus linearly interpolated Hartono densities at loading 0.4 and nominal 30 wt% solvent. These five source differences motivated exclusion from fitting; neither source is thereby established as correct.',
          ['T (K)','Difference (kg/m3)'],[[num(r['T_K'],6),num(r['amundsen_minus_hartono'])] for r in sorted(conflicts,key=lambda r:r['T_K'])])
    calorics=a.load(a.ROOT/'data/reference/MEA/thermal/physical-ideal-gas-calorics.json')
    shomate, mea = [calorics['components'][k] for k in ['carbon-dioxide','water']], calorics['components']['monoethanolamine']
    assert [c['representation'] for c in shomate] == ['shomate']*2 and mea['representation'].startswith('cp_')
    ranges = lambda c, j: str(c.get('source_range_k', c['range_k'])[j])
    caloric_rows = [[f'${x}$', *(str(c['coefficients'][j]) for c in shomate)] for j, x in enumerate('ABCDEFGH')]
    caloric_rows += [['Source range, lowest (K)', *(ranges(c, 0) for c in shomate)], ['Source range, highest (K)', *(ranges(c, 1) for c in shomate)], ['Formation enthalpy (J/mol)', *(str(c['formation_enthalpy_j_per_mol']) for c in shomate)]]
    caloric_rows += [*block(r'$C_P$ polynomial coefficient', r'\ce{MEA}', ''), *([f'${x}$', str(v), ''] for x, v in zip('abcd', mea['coefficients'], strict=True)), ['Source range, lowest (K)', ranges(mea, 0), ''], ['Source range, highest (K)', ranges(mea, 1), ''], ['Reference', 'Zhang Table 3', '']]
    table('ideal_calorics.tex',r'Ideal-gas caloric inputs. Shomate $C_P=A+Bt+Ct^2+Dt^3+E/t^2$, $t=T/1000$, in J/(mol K); enthalpy is $h_f+1000(At+Bt^2/2+Ct^3/3+Dt^4/4-E/t+F-H)$. MEA uses $C_P=a+bT+cT^2+dT^3$ with $h=s=0$ at 313.15 K. Shomate entries list A--H in order.',
          ['Shomate coefficient','CO2','Water'],caloric_rows,'lrr')
    literature=[
        [r'Böttinger et al. \cite{Bottinger2008}','Pitzer; 6 coefficients in 2 MEA reaction laws','NMR; 293--353 K','No aggregate MEA error stated; R5 fixed to Bates--Pinching','VLE compared with earlier VLE-fitted interactions (Tables 5--6)'],
        [r'Zhang et al. \cite{Zhang2011}','eNRTL/PC-SAFT vapor; 12 ternary coefficients','Pressure, differential heat, heat capacity, NMR','Pressure 13.5--35.5% by source; heat 10.9% (84); Cp 2.4% (102); species 35.7% (24), Table 9','Additional pressure sources 28.6--112% (Table 11)'],
        [r'Nasrifar and Tafazzol \cite{Nasrifar2010}','PC-SAFT/ideal reactions; 5 pure-MEA + 1 MEA--water parameter','Pure and binary properties','Pure-MEA density 0.50%, vapor pressure 3.36% (Table 2); no aggregate ternary error','Acid-gas solubility; ideal-activity speciation'],
        [r'Baygi and Pahlavanzadeh \cite{Baygi2015}','PC-SAFT/ideal reactions; 5 pure-MEA + 1 binary parameter','Pure properties; binary VLE','Ternary pressure 36.42% (691), outside fit (Table 5)','NMR (Fig. 8), binary excess enthalpy (Fig. 6); ternary uses 3B MEA/4C water'],
        [r'Najafloo and Zarei \cite{Najafloo2018}','SAFT-HR/ideal reactions; 5 pure-MEA parameters','Pure vapor pressure/density','Ternary pressure 34.71% (691), Table 5','Methods describe pure-component fitting only; the conclusion lists ternary ranges among the fitted data'],
        [r'Lloret et al. \cite{lloretConsistentTransferableThermodynamic2017}','soft-SAFT; 2 reactive-association parameters','30 wt% VLE; 313.15--373.15 K','No aggregate pressure error stated; Section 4.7','Heat from pressure derivative underpredicted; no calculated temperature dependence'],
        [r'Akula et al. \cite{Akula2023a}','eNRTL; 10 ternary parameters','263 pressures + 93 differential heats','Mean absolute percentage error: pressure 40.5%, differential heat 5.9% (Section 4.2)','NMR and heat capacity outside objective'],
        [r'Hessen et al. \cite{Hessen2010}','Refined eNRTL; temperature-dependent interactions (Table 2)','Binary VLE, freezing point, excess enthalpy and ternary pressures','No aggregate MEA pressure statistic stated','Speciation and activity comparisons; Section 4'],
        [r'Aronu et al. \cite{Aronu2011}','Extended UNIQUAC; ion size/surface and pair coefficients (Tables 7--9)',r'VLE at 15--60 wt%; \ce{N2O}-derived physical solubility','Fitted CO2 partial pressure 24.3%; total pressure 11.7%; physical solubility 2.7% (Section 5)','NMR and absorption heat compared outside objective'],
        [r'Téllez-Arredondo and Medeiros \cite{tellez-arredondoModelingCO2H2S2013}','Electrolyte cubic two-state association; 7 MEA ternary parameters','VLE; 15.2--30 wt%; 298.15--393.15 K in Table~2 and Fig.~8; Section~4.3.3 instead states an upper limit of 366.68 K','Relative pressure deviation 12.5%, fitted (Tables 5, 8)','Parameters from earlier subsystems retained'],
        [r'Neumann et al. \cite{neumannNewModelCombining2022}','Helmholtz energy/eNRTL; 3 ternary reaction laws refitted; ternary eNRTL interactions retained',r'Binary and ternary VLE; one MEA--\ce{CO2} reducing parameter also uses ternary data','Ternary density AARD 0.92% Hartono; 3.5% complete Han (Section 4.2)','VLE/density comparisons; density data sets differ from this work'],
        ['This work','16 fitted parameters; 6 at bounds','307 quantities: pressure, species, heat, density, heat capacity and binary VLE','Fitted pressure/species 11.86/7.10%; integral heat RMSE 1.83 kJ/mol','159-pressure comparison 20.55%; previously examined data']]
    table('literature_model_comparison.tex',r'Model complexity, data roles and reported deviations in related MEA studies. Parameter counts refer to the stated fit, excluding earlier subsystem fits. Relative pressure deviations and caloric metrics use each source\'s own data and definitions; integral-heat RMSE and differential-heat percentage errors are not directly comparable. These are not common-data accuracy rankings.',
          ['Study','Model; fitted parameters','Fitted data','Reported agreement','Other comparisons or qualification'],literature,[.14,.21,.18,.23,.18])
    symbols=[
        [r'$\alpha$',r'Added CO2 per mole total amine'],
        [r'$w_{\mathrm{MEA}}$',r'MEA mass fraction of unloaded solvent'],
        [r'$T,T_{\mathrm{ref}}$',r'Temperature; interaction reference temperature 313.15 K'],
        [r'$P,p_{\mathrm{CO2}},P^\circ$',r'Bubble pressure; CO2 partial pressure; source reference pressure'],
        [r'$x_i,y_i,\boldsymbol w$',r'True-species liquid, vapor and trial mole fractions'],
        [r'$z_i,M_i$',r'Species charge number and molar mass'],
        [r'$A,a^{\mathrm{res}}$',r'Extensive Helmholtz energy; residual Helmholtz energy divided by nRT'],
        [r'$\rho,Z,V$',r'Molar density; compressibility factor; phase volume'],
        [r'$\sigma_i,u_i/k_B$',r'Segment diameter; dispersion energy divided by Boltzmann constant'],
        [r'$k_{ij},b_{ij}$',r'Binary interaction and its reciprocal-temperature slope (K)'],
        [r'$\kappa^{AB},\epsilon^{AB}/k_B$',r'Association volume and energy divided by Boltzmann constant'],
        [r'$d_i^{\mathrm{Born}},D_i$',r'Born diameter and outer solvation-shell diameter'],
        [r'$f_i,f_{\mathrm{mix}}$',r'Component solvation factor and mixture average'],
        [r'$c_{\mathrm{shell}},c_{\mathrm{dielectric}}$',r'Solvation-shell and dielectric-saturation coefficients'],
        [r'$\varepsilon_{\mathrm{bulk}},\varepsilon_{\mathrm{ion}}$',r'Bulk and ion-region relative permittivities'],
        [r'$e,\varepsilon_0,k_B,R$',r'Elementary charge; vacuum permittivity; Boltzmann and gas constants'],
        [r'$d_{V,i},d_{T,i},n_s$',r'Dielectric-volume and temperature coefficients; neutral-solvent amount'],
        [r'$\nu_{ri},K_r,K_{m,r},K_{x,r}$',r'Stoichiometric coefficient; reaction constant and its molality/mole-fraction forms'],
        [r'$A_r,B_r,C_r,D_r,\Delta_r$',r'Reaction-correlation coefficients and standard-state offset'],
        [r'$a_i,\phi_i,\mu_i$',r'Activity; fugacity coefficient; chemical potential'],
        [r'$m_i,m^\circ$',r'Species molality; standard molality 1 mol/kg'],
        [r'$\delta h_r$',r'Constant reaction-enthalpy adjustment'],
        [r'$H,\Delta h,h^{\mathrm{feed}}$',r'Extensive enthalpy; integral absorption heat; feed molar enthalpy'],
        [r'$C_P,c_P,m_{\mathrm{feed}}$',r'Extensive and mass-specific heat capacities; analytical-feed mass'],
        [r'$s_j,r_j,w_j,C$',r'Assigned scale; residual; weight; weighted least-squares cost'],
        [r'$u_\rho,u_\alpha,g,s_\rho$',r'Density and loading uncertainty inputs; local secant; combined density scale'],
        [r'$\boldsymbol\theta,J_I,s_C^2$',r'Fitted parameters; free-parameter weighted Jacobian; variance factor'],
        [r'$B,\boldsymbol\lambda,D$',r'Conserved-quantity matrix; equilibrium multipliers; tangent-plane distance'],
        ['AARD; RMSE',r'Average absolute relative deviation; root-mean-square error']]
    table('nomenclature.tex','Symbols used in this manuscript.',['Symbol','Definition'],symbols,['l',.7])
    for name, body in OUTPUTS.items():
        head='% Generator: docs/scientific/latex/scripts/final_rerun_tables.py; do not hand-edit.\n'
        head+='% A7 parameter SHA256: '+fit['record_sha256']+'\n'
        if name == 'acceptance_limits.tex':
            head += '% Record identities: '+json.dumps(comparison_identities,sort_keys=True)+'\n'
            head += '% '+a.A6_ASSESSMENT_NOTE+'\n'
        head+='% F1 original wheel SHA256: '+old_engine['wheel_sha256']+'\n' if name in ['supplement_fits.tex','supplement_predecessor.tex','acceptance_limits.tex'] else ''
        head+='% F1 predecessor inputs/identity: '+json.dumps(old,sort_keys=True)+'\n' if name in ['supplement_fits.tex','supplement_predecessor.tex','acceptance_limits.tex'] else ''
        head+=''.join('% Input: '+p+' SHA256 '+h+'\n' for p,h in sorted(a.INPUTS.items()))
        (TABLES/name).write_text(head+body)
    print(json.dumps(dict(objective_rows=len(fitted),group_costs=fit['groups'],loaded_density=len(loaded_ids),densities=len(density),heats=len(heat),coordinates=len(errors),phase_points=73,matched_F1_densities=len(matched)),indent=2))


if __name__ == '__main__':
    main()
