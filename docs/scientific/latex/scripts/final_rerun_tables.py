"""Render promoted F2 MEA results (#341, Engine 391dfe5d) and explicitly historical comparisons; no Engine computation."""
import ast
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
UNITS = dict(PartialPressure='CO2 partial pressure (Pa)', PhaseMoleFraction='species fraction', AdditionEnthalpy='integral heat (J/mol CO2)',
             amount_ratio='species / total amine', pressure='pressure (Pa)', phase_density='density (kg/m3)', temperature='temperature (K)',
             mole_fraction='vapor water fraction', equilibrium_isobaric_heat_capacity='J/(mol K); total analytical feed')


DISPLAY = {'Common149': 'Pressure--species--heat group', 'common149': 'pressure--species--heat group', 'vapour': 'vapor', 'Vapour': 'Vapor', 'LogRatio': 'log ratio', 'Cai mole_fraction': 'Cai vapor water fraction', 'Vinjarapu2024': 'Vinjarapu', 'Arcis2011': 'Arcis', ' at 510000.0 Pa': ' at 0.51 MPa', ' at 1030000.0 Pa': ' at 1.03 MPa', 'kg/m3': r'\si{\kilogram\per\cubic\metre}'}
SOURCE_NAMES = {'Baygi2015':'Baygi and Pahlavanzadeh (2015)', 'Najafloo2018':'Najafloo and Zarei (2018)', 'Zhang2011':'Zhang et al. (2011)', 'Aronu2011':'Aronu et al. (2011)', 'Idris2014':'Idris et al. (2014)', 'Bottinger2008':'Böttinger et al. (2008)', 'Matin2012':'Matin et al. (2012)', 'vinjarapu2024':'Vinjarapu et al. (2024)', 'Vinjarapu2024':'Vinjarapu et al. (2024)', 'Arcis2011':'Arcis et al. (2011)', 'Amundsen2009':'Amundsen et al. (2009)', 'Hartono2014':'Hartono et al. (2014)', 'Han2012':'Han et al. (2012)', 'Jakobsen2005':'Jakobsen et al. (2005)', 'Hilliard2008':'Hilliard (2008)', 'Jou1995':'Jou et al. (1995)', 'Mamun2005':'Ma’mun et al. (2005)', 'Xu2011':'Xu and Rochelle (2011)', 'cai1996':'Cai et al. (1996)', 'kiepe':'Kiepe et al. (2002)', 'AMU':'Amundsen et al. (2009)'}
def display(value):
    value = str(value).replace('pooled', 'added together')
    parts = re.split(r'(\\cite(?:\[[^]]*\])?\{[^}]*\})', value)
    if len(parts) > 1:
        return ''.join(part if part.startswith(r'\cite') else display(part) for part in parts)
    for old, new in SOURCE_NAMES.items():
        value = value.replace(old, new)
    for old, new in DISPLAY.items():
        value = value.replace(old, new)
    return re.sub(r'(?<!\{)\bCO2\b', lambda _: r'\ce{CO2}', value)

SOURCE_CITE = {'Austgen1991_TableV_reaction_1a': r'\cite[Table~V, 1a]{Austgen1991}', 'Austgen1991_TableV_reaction_4a': r'\cite[Table~V, 4a]{Austgen1991}', 'Austgen1991_TableV_reaction_5a': r'\cite[Table~V, 5a]{Austgen1991}', 'Tong2012_Table5_K5_MEA_via_Aroua1999': r'\cite[Table~5]{Tong2012}', 'BatesPinching1951_equation_7': r'\cite[Eq.~10]{batesAcidicDissociationConstant1951}'}

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


# Parameters print 8 significant figures.
PARAMETER_DIGITS = 8
WORDS = 'no one two three four five six seven eight nine ten'.split()


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
    return identity.replace(' over k', '/k').replace('debye huckel', 'Debye–Hückel').replace('born diameter', 'Born diameter').replace('reaction:', '').replace(':correlation:a k', r' completed $b_5$').replace(':', ' ')

# Parameter provenance is stated in Source columns; numeric cells use no fitted/bound markers.

def cell(value, kind):
    number = re.fullmatch(r'(\*\*)?(-?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)([†*‡]*)', str(value))
    if kind == 'r' and number:
        body = scientific(number[2])
        return '$' + body + '$'
    return tex(display(value))


# A block of rows with a different form or unit starts with one spanning label that carries the unit once.
# table() keeps a block's rows together, so a page breaks only before a label, never between it and its rows.
def block(ncols, label, first=False):
    return ('' if first else r'\addlinespace[\aboverulesep]') + r'\multicolumn{' + str(ncols) + r'}{@{}l}{\itshape ' + label + r'} \\*'


# rows: (heading, unit, cells). One block per heading and unit, in first-appearance order.
def blocks(rows, ncols):
    groups = {}
    for heading, unit, cells in rows:
        groups.setdefault(heading + (f' ({unit})' if unit else ''), []).append(cells)
    return [row for i, (label, part) in enumerate(groups.items()) for row in [block(ncols, label, i == 0), *part]]


# A local column-header row names the columns beneath it where they differ from the table head.
def columns(*names):
    return ' & '.join(names) + r' \\*'


# Parameter quantity by the last identity part, in display order; units as block headings show them.
QUANTITY = {'k_ij': r'Interaction $k_{ij}$', 'reciprocal_temperature_slope': r'Temperature slope $b_{ij}$', 'segment_count': 'Segment count',
            **dict.fromkeys(['segment_diameter', 'born_diameter', 'debye_huckel_diameter', 'packing_diameter', 'constant', 'amplitude'], 'Diameter'),
            'exponent_coefficient': 'Diameter exponent coefficient', 'dispersion_energy_over_k': r'Dispersion energy $\epsilon_i/k_B$',
            'energy_over_k': r'Association energy $\epsilon^{AB}/k_B$', 'volume': r'Association volume $\kappa^{AB}$', 'solvation_factor': r'Solvation factor $f_i$',
            'dielectric_volume': r'Dielectric volume $d_{V,i}$', 'dielectric_temperature': r'Dielectric temperature $d_{T,i}$',
            'ionic_region_relative_permittivity': 'Relative permittivity', 'a_k': 'Reaction coefficient', 'enthalpy_shift': r'Enthalpy shift $\delta h_r$'}
UNIT_HEADS = {'dimensionless': '', 'kelvin': 'K', 'K': 'K', 'angstrom': r'\AA', 'liter / mole': 'L/mol', '1 / kelvin': r'\si{\per\kelvin}', 'kJ/mol': 'kJ/mol'}


# rows: (identity, unit, cells); blocks ordered as QUANTITY, source order kept within a block.
def parameter_blocks(rows, ncols):
    order = list(QUANTITY.values())
    rows = [(QUANTITY[re.split('[/:]', identity)[-1]], UNIT_HEADS[unit], cells) for identity, unit, cells in rows]
    return blocks(sorted(rows, key=lambda r: order.index(r[0])), ncols)


# cols: one entry per column: 'l' label, 'r' number, or a float width (fraction of linewidth) for wrapped text.
def table(name, caption, headings, data, cols=None, landscape=False, sep=3):
    source = {'supplement_fitted_parameters.tex':'Joint fit', 'comparison_fit_parameters.tex':'Two fitted sets', 'density_free_parameters.tex':'Density-free fit'}.get(name)
    if source:
        ncols=len(headings)
        headings=[*headings, 'Source']
        cols=[*(cols or 'r'*ncols), 'l']
        data=[row.replace(r'\multicolumn{'+str(ncols)+'}',r'\multicolumn{'+str(ncols+1)+'}') if isinstance(row,str) else [*row,source] for row in data]
    section_order = re.findall(r'\\section\{[^}]*\}\\label\{(sec:s-[^}]+)\}', (ROOT/'docs/scientific/latex/supplement.tex').read_text())
    sections = {label: f'S{i}' for i,label in enumerate(section_order,1)}
    def section_refs(value):
        return re.sub(r'\\+ref\{(sec:s-[^}]+)\}', lambda m: sections[m[1]], str(value))
    caption = section_refs(caption)
    data = [row if isinstance(row, str) else [section_refs(value) for value in row] for row in data]
    caption = display(caption.replace('CO₂', r'\ce{CO2}')).replace("Ma\\'mun", "Ma'mun")
    caption = caption[:1].upper() + caption[1:]
    caption = re.sub(r'(?<!\\)%', r'\%', caption).replace("\\'s", "'s")
    cols = cols or 'r'*len(headings)
    spec = '@{}' + ''.join(r'>{\raggedright\arraybackslash}p{' + f'{c:.4f}' + r'\linewidth}' if isinstance(c, float) else c for c in cols) + '@{}'
    head = ' & '.join(tex(display(h)) for h in headings) + r' \\'
    caption = r'\caption{' + caption + r'}\label{tab:' + name.removesuffix('.tex').replace('_', '-') + '}'
    # In a table with block labels, a row followed by another row ends with longtable's no-break \\*.
    blocked = any(isinstance(row, str) and r'\multicolumn' in row for row in data)
    rows = [row if isinstance(row, str) else ' & '.join(cell(x, c) for x, c in zip(row, cols, strict=True)) + (r' \\*' if blocked and isinstance(after, list) else r' \\')
            for row, after in zip(data, [*data[1:], None])]
    if len(data) <= 32 and not landscape and name not in ('supplement_literature_comparison.tex','same_data.tex','current_data_inventory.tex'):  # a table that fits on one page floats whole instead of breaking; a landscape page holds its table whole
        # The main text's journal class reads the table placement as its pos key; the supplement's article class reads it directly.
        place = '[!htbp]' if '{tables/' + name.removesuffix('.tex') + '}' in (ROOT/'docs/scientific/latex/supplement.tex').read_text() else '[pos=!htbp]'
        OUTPUTS[name] = '\n'.join([r'\begin{table}' + place + r'\small\setlength{\tabcolsep}{' + str(sep) + r'pt}\centering', caption, r'\begin{tabular}{' + spec + '}',
                                   r'\toprule', head, r'\midrule', *rows, r'\bottomrule', r'\end{tabular}', r'\end{table}', ''])
        return
    body = [r'\begingroup\small\setlength{\tabcolsep}{3pt}', r'\begin{longtable}{' + spec + '}', caption + r'\\',
            r'\toprule', head, r'\midrule\endfirsthead', r'\toprule', head, r'\midrule\endhead', r'\bottomrule\endfoot']
    OUTPUTS[name] = '\n'.join(body + rows + [r'\end{longtable}\endgroup', ''])


def span(values, digits=6):
    values = list(values)
    lo, hi = min(values), max(values)
    return num(lo, digits) if lo == hi else num(lo, digits) + '--' + num(hi, digits)


# F2 manuscript inputs are immutable files at the investigator-promoted commit.
import hashlib
import subprocess
BASE = 'd73b90cc6ae00962dc34f77252bbcf54eeff430e'
E = a.BUNDLE/'results/paper-evidence-341'
F = E/'paper-evidence'
READ = a.bind

def verified(path):
    path = READ(path)
    original = subprocess.check_output(['git','show',BASE+':'+str(path.relative_to(ROOT))], cwd=ROOT)
    assert hashlib.sha256(original).hexdigest() == a.INPUTS[str(path.relative_to(ROOT))], path
    return path

a.bind = verified

def observable(group, quantity):
    return 'species fraction' if quantity=='mole_fraction' and group!='Cai' else UNITS.get(quantity,quantity)

def main():
    document = a.load(F/'reported-parameters.json')
    fitrows = a.rows(F/'fitted-rows.csv')
    assert len(fitrows) == 307 and hashlib.sha256((F/'reported-parameters.json').read_bytes()).hexdigest() == 'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed'
    params = [r for r in a.rows(a.BUNDLE/'results/reduced-refit/parameter-details.csv') if r['fit']=='F2']
    assert len(params)==11
    a.close(sum(float(r['cost']) for r in fitrows),a.load(E/'candidate/replay.json')['cost'])
    coords = {r['identity']:r for r in params}
    values = {c['identity']: c['value']['magnitude'] for n in document['components'] + document['pairs'] for c in n['coefficients']}
    values |= {i: c['value']['magnitude'] for n in document['topology']['edges'] for i, c in a.coefficients(n)}
    # Parameters set by the three fits before the joint fit (Results): pure water to IAPWS-95, CO2-water to Kiepe pressures, MEA dielectric pair to permittivities.
    separate = {'component/water/segment_count', 'component/water/dispersion_energy_over_k', 'association/water/a/water/b/energy_over_k', 'association/water/a/water/b/volume',
                'pair/carbon-dioxide/water/k_ij', 'pair/carbon-dioxide/water/k_ij/reciprocal_temperature_slope',
                'component/monoethanolamine/dielectric_volume', 'component/monoethanolamine/dielectric_temperature'}
    shown = set()
    def value(identity, mark='', decimals=None):
        if identity not in values:
            return '--'
        shown.add(identity)
        v = float(values[identity])
        # Main-text Table 3 rounds to at most four decimal places; the supplement species table carries eight significant figures.
        text = f'{v:.{decimals}f}' if decimals is not None and round(v, decimals) not in (v, 0) else num(v, PARAMETER_DIGITS)
        return text
    species = [n['component_id'] for n in document['components']]
    charge = {s: n.get('fixed', {}).get('charge_number', {}).get('value', {}).get('magnitude', 0) for s, n in zip(species, document['components'])}
    symbol = {**NAMES, 'water': r'\ce{H2O}'}
    def species_rows(decimals=None):
        def v(identity, mark=''):
            return value(identity, mark, decimals)
        def association(s, quantity):
            if s == 'carbon-dioxide':  # induced association with water only, marked ‡
                return v(f'association/carbon-dioxide/a/water/b/{quantity}', '‡')
            return v(f'association/{s}/a/{s}/b/{quantity}')
        return [[symbol[s], v(f'component/{s}/segment_count'),
                 r'$\sigma_w(T)$' if s == 'water' else v(f'component/{s}/segment_diameter'),
                 v(f'component/{s}/dispersion_energy_over_k'), association(s, 'energy_over_k'), association(s, 'volume'),
                 f'${int(charge[s]):+d}$' if charge[s] else '0', v(f'component/{s}/born_diameter'), v(f'component/{s}/solvation_factor'),
                 v(f'component/{s}/dielectric_volume'), v(f'component/{s}/dielectric_temperature')] for s in species]
    species_headings = ['Species', r'$m^{\mathrm{seg}}$', r'\makecell[rb]{$\sigma$\\(\AA)}', r'\makecell[rb]{$\epsilon/k_B$\\(K)}', r'\makecell[rb]{$\epsilon^{AB}/k_B$\\(K)}', r'$\kappa^{AB}$', '$z$',
                        r'\makecell[rb]{$d^\mathrm{Born}$\\(\AA)}', '$f$', r'\makecell[rb]{$d_V$\\(L/mol)}', r'\makecell[rb]{$d_T$\\(K)}']
    sources = [r'Segments: \cite[Table~2]{Gross2001}; association: water fit (energy/2)',
               r'Segments, energy: \cite[Table~2]{Baygi2015}; association volume converted here',
               'Water fit', 'Joint fit; segment count assumed', 'Joint fit; segment count assumed',
               r'Size, energy: \cite[Table~4]{Uyan2015}; Born: assumed',
               r'Size, energy: \cite[Table~4]{Uyan2015}; Born: assumed',
               r'Size, energy transferred: \cite[Table~4]{Uyan2015}; Born: assumed',
               r'Size, energy: \cite[Table~4]{Uyan2015}; Born: assumed']
    # Charge, solvation and dielectric inputs are specified with their sources in S2.
    main_indices = [0,1,2,3,4,5,7]
    table('species_parameters.tex', r'Segment, association and Born parameters of the adopted parameter set. Sources identify fitted quantities and transferred inputs; Table~\ref{supp-tab:supplement-species-parameters} gives eight-significant-figure values and the remaining inputs. A dash denotes an unused input.',
          [species_headings[i] for i in main_indices]+['Source'],
          [[row[i] for i in main_indices]+[source] for row,source in zip(species_rows(4),sources,strict=True)],
          ['l']+['r']*6+[.25],sep=3)
    # Full parameter listing in the supplement: one quantity per row, with provenance.
    inline_headings = ['Species', r'$m^{\mathrm{seg}}$', r'$\sigma$ (\AA)', r'$\epsilon/k_B$ (K)', r'$\epsilon^{AB}/k_B$ (K)', r'$\kappa^{AB}$', '$z$', r'$d^\mathrm{Born}$ (\AA)', '$f$', r'$d_V$ (L/mol)', r'$d_T$ (K)']
    full=[]
    for row,source in zip(species_rows(),sources,strict=True):
        for i in range(1,len(row)):
            if row[i]=='--': continue
            origin=source
            if i==6: origin='Chemical charge'
            elif i==8: origin=r'Water: \cite[Table~2]{Figiel2025}; others: assumed' if row[0]==r'\ce{H2O}' else 'Assumed'
            elif i in (9,10): origin='Permittivity fit' if row[0]==r'\ce{MEA}' else (r'\cite[Table~6]{Yang2024}' if row[0]==r'\ce{H2O}' else 'Assumed')
            full.append([row[0],inline_headings[i],row[i],origin])
    table('supplement_species_parameters.tex', 'Complete species inputs of the adopted parameter set. CO2 association entries apply only to induced bonding with water. The water diameter law and the MEA association-volume conversion are specified in the text.',
          ['Species','Quantity (unit)','Value','Source'],full,['l',.25,'r',.4])
    def pair(s, t, quantity='', decimals=None):
        if charge[s] * charge[t] > 0:  # same-sign ions: dispersion excluded
            return '--'
        identity = next((i for i in [f'pair/{s}/{t}/k_ij', f'pair/{t}/{s}/k_ij'] if i in values), None)
        return value(identity + quantity, '', decimals) if identity else '--'
    matrix = lambda quantity, rows, decimals=None: [[symbol[s]] + [pair(s, t, quantity, decimals) if j > i else '' for j, t in enumerate(species) if j > 0] for i, s in enumerate(species) if s in rows]
    def interaction_rows(decimals=None):
        slopes = [[r[0]] + [x.replace('--', '') for x in r[1:]] for r in matrix('/reciprocal_temperature_slope', species[:-1], decimals)]
        slopes = [r for r in slopes if any(r[1:])]
        return [block(9, r'Interaction $k_{ij}(T_{\mathrm{ref}})$', True), *matrix('', species[:-1], decimals), block(9, r'Temperature slope $b_{ij}$ (K)'), *slopes]
    interaction_headings = ['', *(symbol[s] for s in species[1:])]
    pair_specs = [('carbon-dioxide','water','CO2--water fit'),('monoethanolamine','water','Joint fit'),
                  ('water','protonated-monoethanolamine','Joint fit'),('water','carbamate-anion','Joint fit'),
                  ('water','bicarbonate-anion','Joint fit'),('protonated-monoethanolamine','carbamate-anion','Joint fit'),
                  ('water','carbonate-anion','Assumed'),('water','hydronium-cation','Assumed'),('water','hydroxide-anion','Assumed')]
    def pair_rows(decimals=None):
        return [[symbol[s]+'--'+symbol[u],pair(s,u,decimals=decimals),pair(s,u,'/reciprocal_temperature_slope',decimals),source] for s,u,source in pair_specs]
    table('interaction_matrix.tex', r'Nonzero or fitted binary interactions, $k_{ij}(T)=k_{ij}(313.15\,\mathrm{K})+b_{ij}(1/T-1/313.15\,\mathrm{K})$. All unlisted unlike-charge or neutral pairs have $k_{ij}=0$; same-sign ion dispersion is excluded. An absent slope is zero. Sources of fixed inputs are in Section~\ref{supp-sec:s-parameters}.',
          ['Pair',r'$k_{ij}(313.15\,\mathrm{K})$',r'$b_{ij}$ (K)','Source'],pair_rows(4),['l','r','r','l'])
    table('supplement_interaction_matrix.tex', 'Binary interactions to eight significant figures. All unlisted interactions and slopes are zero; same-sign ion dispersion is excluded.',
          ['Pair',r'$k_{ij}(313.15\,\mathrm{K})$',r'$b_{ij}$ (K)','Source'],pair_rows(),['l','r','r','l'])
    table('supplement_fitted_parameters.tex', 'Jointly fitted parameters, bounds and conditional standard errors. A dash marks the active bound. Born diameters of the two amine ions equal their segment diameters.', ['Parameter','Value','Lower','Upper','SE'], [[label(r['identity']),num(r['value'],8),num(r['lower']),num(r['upper']),num(r['conditional_SE'])] for r in params], ['l','r','r','r','r'])
    reaction = a.load(a.BUNDLE/'results/adoption-297/paper-evidence/source-only/chemical_reaction_source_contract.json')
    rr = []
    for r in reaction['reactions']:
        law = next((n for n in document['reaction_correlations'] if n['reaction_id']==r['reaction_id']), None)
        values = {c['identity'].split(':')[-1]:c['value']['magnitude'] for c in law['coefficients']} if law else dict(r['correlation'])
        if not law: values['a'] += reaction['common_source_standard_state']['source_to_common_ln_k_offsets'][int(r['reaction_id'][1:])-1]
        if r['reaction_id']=='R5': values = dict(zip(('a','b_k','c','d_per_k'),[-math.log(10)*values['b'],-math.log(10)*values['a_k'],0,-math.log(10)*values['c_per_k']]))
        rr.append([r['reaction_id'],r'\ce{'+r['equation'].replace(' <=> ',' <=> ').replace('CO3--','CO3^{2-}')+'}',*[num(values.get(k,0),9) for k in ('a','b_k','c','d_per_k')]])
    table('reaction_equilibrium_constants.tex', r'Completed aqueous-molality laws, $\ln K=A+B/T+C\ln T+DT$, $T$ in K. Source-to-molality offsets are included once. R1--R3: Austgen Table V; R4: Tong Table 5; R5: Bates--Pinching Eq. (10). All laws are fixed in the joint fit.', ['Reaction','Stoichiometry','$A$','$B$ (K)','$C$','$D$ (1/K)'], rr, ['l','l','r','r','r','r'])
    groups = {}
    for r in fitrows: groups.setdefault((r['group'],r['quantity']),[]).append(r)
    groupname = {'common149':'Pressure, species and heat','restored species':'Additional species','Jakobsen':'Jakobsen ratios','Kiepe':r'\ce{CO2}--water','CO2-free density':r'\ce{CO2}-free density','Cai':'MEA--water','Cp':'Heat capacity','loaded density':'Loaded density'}
    table('residual_summary.tex', r'Fitted observations by quantity. AARD is in percent; RMSE uses the stated unit. These groups are disjoint.', ['Quantity (unit)','n','AARD','RMSE'], [[groupname[g]+'; '+observable(g,q),len(rows),num(a.stats(rows)['AARD_percent']),num(a.stats(rows)['RMSE'])] for (g,q),rows in groups.items()], [.60,'r','r','r'])
    compare = a.rows(a.BUNDLE/'results/reduced-refit/fit-comparison.csv')
    agreement = a.rows(a.BUNDLE/'results/reduced-refit/agreement.csv')
    score = lambda fit, dataset: next(r for r in agreement if r['fit']==fit and r['dataset']==dataset)['aard_percent']
    table('choice_cost.tex', r'Cumulative restrictions and their measured cost on identical observations. P: 47 fitted pressures; U: 112 pressures not fitted; L: 47 fitted loaded densities. Deviations are AARD (percent). No across-role ranking is implied.', ['Set','Parameters','On bounds','$C$','P','U','L'], [[r['fit'],r['fitted_parameters'],r['on_bound'],num(r['cost'],6),*[num(score(r['fit'],d)) for d in ('fitted: fitted CO2 partial pressure','not fitted: six-source pressures','fitted: loaded density')]] for r in compare], ['l']+['r']*6)
    cp = a.load(E/'same-data-comparison/part1-scores.json')
    table('same_data.tex', r'Identical-row comparisons with Polley--Hedengren (2026). Columns disclose each model\'s data role; they do not provide an across-role model ranking. For the 2026 species ratios and carbonate shares, the measurements informed an earlier ion fit despite not entering the reported formulation objective. Heat RMSE is kJ/mol \ce{CO2}; density RMSE is kg/m$^3$.', ['Quantity; metric','n','2026 role','F2 role','2026','F2'], [[r['group'].replace('current-','F2 ').replace('not-fitted','not fitted').replace('broad Cp','Broad heat capacity')+'; '+r['metric'],r['n'][0],r['roles'][0].split(';')[0].replace('formulation ',''),r['roles'][1],num(r['deviations'][0],5),num(r['deviations'][1],5)] for r in cp], [.27,'r',.18,.18,'r','r'])
    published = [r for r in a.load(E/'same-data-comparison/published-deviations.json') if r['comparison'].startswith('exact:')]
    table('matched_pressure.tex', r'Ma\'mun pressure observations on identical rows. Published deviations and parameter counts refer to the source estimation stage. Najafloo\'s AAD definition is inferred equivalent; its conclusion and detailed fitting description differ. F0 is a comparison parameter set.', ['Model','n','Role','Parameters','Deviation (percent)'], [[r['model'],r['n'],r['data_role'],r['fitted_parameters'],num(r['deviation_percent'])] for r in published]+[['F0',19,'not fitted',16,num(a.load(a.BUNDLE/'results/same-data-comparison/matched-score.json')['pressure_aard_percent'])],['F2',19,'not fitted',11,num(a.load(E/'same-data-comparison/matched-score.json')['pressure_aard_percent'])]], [.34,'r','l','r','r'])
    inventory = [[groupname[g]+'; '+observable(g,q),len(rows),'fitted','Joint objective'] for (g,q),rows in groups.items()]
    inventory += [['Six-source pressures',159,'47 fitted; 112 not fitted','Outside-objective rows inspected before adoption'],['Aronu, other concentrations',70,'not fitted','Inspected before adoption'],['Wagner pressures',23,'not fitted','Inspected before adoption'],['Matin bicarbonate totals',19,'not fitted','Inspected before adoption'],['Jakobsen carbonate shares',10,'not fitted','Inspected before adoption'],['Arcis heats',14,'not fitted','Used in parameter selection'],['Kim finite-interval heats',73,'not fitted','Earlier fitting and prior inspection'],['All density observations',210,'52 fitted; 158 not fitted','Source comparisons informed fitting'],['Broad heat capacities',51,'2 fitted; 49 not fitted','Inspected before adoption']]
    table('current_data_inventory.tex', r'Data roles in the reported joint fit and earlier use. Comparison sets overlap and their counts are not additive. The fixed Kiepe interaction was fitted separately. No present Part I group qualifies as comparison only because all were seen during development.', ['Quantity','n','Role','Earlier use'],inventory,[.37,'r',.21,.30])
    covariance = a.load(E/'uncertainty/covariance.json')
    table('supplement_correlations.tex', r'Conditional correlations of the ten interior parameters, ordered as the fitted-parameter table with its active-bound row omitted.', ['Parameter']+[str(i+1) for i in range(10)], [[str(i+1)]+[num(v,3) if j<=i else '' for j,v in enumerate(row)] for i,row in enumerate(covariance['native_correlation'])], ['r']*11)
    profiles = a.load(E/'uncertainty/profiles.json')
    table('bound_profiles.tex', r'Inward scans of the ion--ion interaction, with the other parameters refitted. These are diagnostic fits without renewed stability qualification.', ['Inward step (percent)','Fixed interaction','$C$','Change in $C$'], [[num(100*r['fraction']),num(r['fixed_value']),num(r['cost'],9),num(r['delta_cost'],7)] for r in profiles], ['r']*4)
    kim = a.load(F/'kim2007-heat-pathways/summary.json')['temperatures']
    table('kim_alternatives.tex', r'Kim finite-interval heat comparisons at 393.15 K. RMSE is kJ/mol absorbed CO2; AARD is percent. All alternatives use the same F2 parameters.', ['Rows','n','RMSE','AARD'], [[name,kim['393.15']['metrics']['semi_differential'][key]['n'],num(kim['393.15']['metrics']['semi_differential'][key]['rmse'],6),num(kim['393.15']['metrics']['semi_differential'][key]['aard_percent'],6)] for key,name in [('all_printed','All printed'),('source_consistent','Without inconsistent rows'),('without_first120','Also without first intervals')]], ['l','r','r','r'])
    weights = a.rows(E/'objective-groups.csv')
    table('objective_groups.tex', r'Assigned objective scales and weights. Rows with identical group and quantity are combined by range; the weight and scale are distinct. Origins and unrecorded rationales are described in the text.', ['Group; quantity','n','Scale range','Weight range','Cost'], [[groupname[g]+'; '+{'partial_pressure':'CO2 pressure','mole_fraction':'mole fraction','addition_enthalpy':'integral heat','amount_ratio':'amount ratio','pressure':'pressure','phase_density':'density','temperature':'temperature','equilibrium_isobaric_heat_capacity':'equilibrium heat capacity'}[q],sum(int(r['n']) for r in weights if (r['group'],r['quantity'])==(g,q)),span(float(r['scale']) for r in weights if (r['group'],r['quantity'])==(g,q)),span(float(r['weight']) for r in weights if (r['group'],r['quantity'])==(g,q)),num(sum(float(r['cost']) for r in weights if (r['group'],r['quantity'])==(g,q)),6)] for g,q in dict.fromkeys((r['group'],r['quantity']) for r in weights)], [.45,'r','l','l','r'])
    checks = a.load(E/'check-values.json')
    table('check_values.tex', r'Bubble-state reproduction values. Inputs: $x_{\ce{CO2}}=0.00036$ in water; $x_{\MEA}=0.9264$ in MEA--water; 30 wt\% MEA at loading 0.3 mol/mol. Each was solved from two initial pressures; printed values agree. Density is liquid mass density.', ['System','$T$ (K)','$P$ (Pa)',r'$\rho$ (kg/m$^3$)'], [[name,num(r['T_K'],7),num(r['answers'][0]['bubble_pressure_Pa'],10),num(r['answers'][0]['density_kg_m3'],10)] for name,r in zip([r'\ce{CO2}--water','MEA--water','Loaded MEA'],checks)], ['l','r','r','r'])
    contribution_names = dict(association='Association', born='Born', hard_chain='Hard chain', dispersion='Dispersion', debye_huckel=r'Debye--H\"uckel', residual_helmholtz='Total residual')
    table('supplement_check_values.tex', r'Reduced residual molar Helmholtz contributions $A_i/(nRT)$ and true liquid species fractions at the three main-text reproduction states. Zero terms are omitted.', ['Contribution or species',r'\ce{CO2}--water','MEA--water','Loaded MEA'], [[('$x_{'+symbol[key[2:]]+'}$') if key.startswith('x_') else contribution_names[key],*[num(r['answers'][0][key],10) for r in checks]] for key in checks[0]['answers'][0] if key not in ('bubble_pressure_Pa','density_kg_m3','molar_density_mol_m3') and any(r['answers'][0][key] for r in checks)], ['l','r','r','r'])
    shared = a.rows(E/'shared-coefficients.csv')
    table('shared_parameters.tex', r'Exact shared coefficient set held fixed in Part II, grouped by physical quantity. Water, \ce{CO2}, \ce{H3O+}, \ce{OH-}, \ce{HCO3-}, \ce{CO3^{2-}}, their shared interactions and R1--R3 laws are included. Topology, fixed fields and standard states also transfer as specified in the text.', ['Parameter','Value','Unit'], [[label(r['identity']),num(r['value'],10),r['unit']] for r in shared]+[['R1--R3 laws','Table~\\ref{tab:reaction-equilibrium-constants}','1']], [.66,'r','l'])
    table('pressure_sources.tex', r'Pressure errors by experimental source at nominal 30 wt\% MEA; source subsets contain both fitted observations and observations that are not fitted.', ['Source','n','AARD (percent)'], [[SOURCE_NAMES.get(s,s),len(part),num(a.stats(part)['AARD_percent'])] for s in sorted({r['source'] for r in a.rows(F/'canonical-pressure.csv')}) for part in [[r for r in a.rows(F/'canonical-pressure.csv') if r['source']==s]]], ['l','r','r'])
    a.load(E/'candidate/replay.json'); a.load(E/'uncertainty/covariance.json'); a.load(E/'stability/candidate/search.json'); a.load(a.BUNDLE/'results/split-cause-342/final-supplied-F2-summary.json')
    for name, body in OUTPUTS.items():
        header = '% Generated from '+BASE+'; F2 ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed\n'+''.join('% Input: '+p+' SHA256 '+h+'\n' for p,h in sorted(a.INPUTS.items()))
        if '--check' in sys.argv: assert (TABLES/name).read_text()==header+body, name
        else: (TABLES/name).write_text(header+body)
    print(json.dumps({'tables_checked':len(OUTPUTS),'inputs_verified_at_commit':len(a.INPUTS),'commit':BASE}))
    (ROOT/'docs/scientific/latex/builds/347-input-hashes.json').write_text(json.dumps({'commit':BASE,'files':a.INPUTS},indent=2)+'\n')

if __name__ == '__main__':
    main()
