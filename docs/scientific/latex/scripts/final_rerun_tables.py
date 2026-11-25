"""Render promoted F2 MEA results (#341, Engine 391dfe5d) and explicitly historical comparisons; no Engine computation."""
import ast
from functools import reduce
import gzip
import json
import math
import re
from operator import getitem
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
# One reader-facing row per fitted quantity and source; the 7 later-added species observations are the same quantity, scale and weight as the other 94.
QUANTITIES = {'PartialPressure': 'partial_pressure', 'PhaseMoleFraction': 'mole_fraction', 'AdditionEnthalpy': 'addition_enthalpy'}
ROWS = {('common149', 'partial_pressure'): (r'\ce{CO2} partial pressure, Hilliard and Jou \cite{Hilliard2008,Jou1995}', ''),
        ('species', 'mole_fraction'): (r'Species mole fraction, B\"ottinger and Matin \cite{Bottinger2008,matinFacileMethodDetermination2012}', ''),
        ('common149', 'addition_enthalpy'): (r'Integral absorption heat, Vinjarapu \cite{HemaBhavya2025}', r'kJ/mol \ce{CO2}'),
        ('Jakobsen', 'amount_ratio'): (r'Species per total amine, Jakobsen \cite{Jakobsen2005}', ''),
        ('Kiepe', 'pressure'): (r'\ce{CO2}--water pressure, Kiepe \cite{kiepeExperimentalDeterminationPrediction2002}', ''),
        ('CO2-free density', 'phase_density'): (r'\ce{CO2}-free solution density, Amundsen \cite{Amundsen2009}', r'kg/m$^3$'),
        ('Cai', 'temperature'): (r'MEA--water bubble temperature, Cai \cite{caiBinaryIsobaricVaporLiquid1996}', 'K'),
        ('Cai', 'mole_fraction'): (r'MEA--water vapor water mole fraction, Cai \cite{caiBinaryIsobaricVaporLiquid1996}', ''),
        ('loaded density', 'phase_density'): (r'Loaded-solution density, Amundsen and Hartono \cite{Amundsen2009,Hartono2014}', r'kg/m$^3$'),
        ('Cp', 'equilibrium_isobaric_heat_capacity'): (r'Heat capacity per mole of apparent components, Hilliard \cite{Hilliard2008}', 'J/(mol K)')}



def rowkey(group, quantity):
    quantity = QUANTITIES.get(quantity, quantity)
    return ('species', 'mole_fraction') if group in ('common149', 'restored species') and quantity == 'mole_fraction' else (group, quantity)


def rowlabel(key, unit=True):
    name, units = ROWS[key]
    return name + (f' ({units})' if unit and units else '')


DISPLAY = {'Common149': 'Pressure--species--heat group', 'common149': 'pressure--species--heat group', 'vapour': 'vapor', 'Vapour': 'Vapor', 'LogRatio': 'log ratio', 'Cai mole_fraction': 'Cai vapor water fraction', 'Vinjarapu2024': 'Vinjarapu', 'Arcis2011': 'Arcis', ' at 510000.0 Pa': ' at 0.51 MPa', ' at 1030000.0 Pa': ' at 1.03 MPa', 'kg/m3': r'kg/m$^3$'}
SOURCE_NAMES = {'Baygi2015':'Baygi and Pahlavanzadeh (2015)', 'Najafloo2018':'Najafloo and Zarei (2018)', 'Zhang2011':'Zhang et al. (2011)', 'Aronu2011':'Aronu et al. (2011)', 'Idris2014':'Idris et al. (2014)', 'Bottinger2008':'Böttinger et al. (2008)', 'Matin2012':'Matin et al. (2012)', 'vinjarapu2024':'Vinjarapu et al. (2024)', 'Vinjarapu2024':'Vinjarapu et al. (2024)', 'Arcis2011':'Arcis et al. (2011)', 'Amundsen2009':'Amundsen et al. (2009)', 'Hartono2014':'Hartono et al. (2014)', 'Han2012':'Han et al. (2012)', 'Jakobsen2005':'Jakobsen et al. (2005)', 'Hilliard2008':'Hilliard (2008)', 'Jou1995':'Jou et al. (1995)', 'Mamun2005':'Ma’mun et al. (2005)', 'Xu2011':'Xu and Rochelle (2011)', 'cai1996':'Cai et al. (1996)', 'kiepe':'Kiepe et al. (2002)', 'AMU':'Amundsen et al. (2009)'}
def display(value):
    value = str(value).replace('pooled', 'added together')
    value = re.sub(r'\bF(?:4-0|[0-5])\b', lambda m: CALIBRATION_NAMES[m[0]], value)
    parts = re.split(r'(\\cite(?:\[[^]]*\])?\{[^}]*\})', value)
    if len(parts) > 1:
        return ''.join(part if part.startswith(r'\cite') else display(part) for part in parts)
    for old, new in SOURCE_NAMES.items():
        value = value.replace(old, new)
    for old, new in DISPLAY.items():
        value = value.replace(old, new)
    return re.sub(r'(?<!\{)\bCO2\b', lambda _: r'\ce{CO2}', value)

CALIBRATION_NAMES = {
    'F0': 'Shifted R2/R5 correlations; separate Born diameters',
    'F1': 'Literature R2/R5 correlations; separate Born diameters',
    'F2': 'Tied amine-ion Born diameters (MEA model)',
    'F3': 'Zero carbamate--water interaction and protonated-MEA--water slope',
    'F4': 'Sodium-salt water--anion interactions',
    'F4-0': 'Zero protonated-MEA--bicarbonate interaction',
    'F5': 'Zero protonated-MEA--carbamate interaction',
}

CITE14 = r'\cite{polleyReactiveEPCSAFTModeling2026}'
PRESSURE_CITE = {'Aronu2011': 'Aronu2011', 'Hilliard2008': 'Hilliard2008', 'Idris2014': 'idrisSpeciationMEACO2Adducts2014', 'Jou1995': 'Jou1995', 'Mamun2005': 'Mamun2005', 'Xu2011': 'Xu2011'}
SET_CITE = {'Six-source': ','.join(PRESSURE_CITE.values()), 'Species fractions': 'Bottinger2008,matinFacileMethodDetermination2012', 'Jakobsen': 'Jakobsen2005', 'Arcis': 'arcisEnthalpySolutionCarbon2011',
            'Amundsen': 'Amundsen2009', 'Hartono': 'Hartono2014', 'Han': 'hanDensityWater12012', 'broad Cp': 'Hilliard2008', 'Wagner': 'wagnerSolubilityCarbonDioxide2013', 'Aronu': 'Aronu2011', 'Kim': 'Kim2007'}

def cited(group, text):
    """A data-set label without its year, followed by the citation of its source."""
    return re.sub(r' \(\d{4}\)', '', display(text)) + next((r' \cite{' + key + '}' for start, key in SET_CITE.items() if group.startswith(start)), '')
SOURCE_CITE = {'Austgen1991_TableV_reaction_1a': r'\cite{Austgen1991}', 'Austgen1991_TableV_reaction_4a': r'\cite{Austgen1991}', 'Austgen1991_TableV_reaction_5a': r'\cite{Austgen1991}', 'Tong2012_Table5_K5_MEA_via_Aroua1999': r'\cite{Tong2012}', 'BatesPinching1951_equation_7': r'\cite{batesAcidicDissociationConstant1951}'}

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


# Default parameter formatting before the main-text rounding rule.
PARAMETER_DIGITS = 8


def full_precision(value):
    return '--' if value is None or value == '' else repr(float(value)).removesuffix('.0')
WORDS = 'no one two three four five six seven eight nine ten'.split()


GROUP = re.compile(r'(?<![\w.{-])-?\d{5,}(?:\.\d+)?(?![\w}])')  # numbers with five or more integer digits get a thin-space digit group

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
    return identity.replace('dispersion energy over k', r'dispersion energy $u/k_B$').replace('debye huckel', 'Debye–Hückel').replace('born diameter', 'Born diameter').replace('reaction:', '').replace(':correlation:a k', r' completed $b_5$').replace(':', ' ')

# Main-text parameter tables give provenance in a Ref. column with lettered notes, the supplement in a Source column;
# a value fitted in this work carries a leading ** and is set in bold.

def cell(value, kind):
    number = re.fullmatch(r'(\*\*)?(-?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)([†*‡]*)', str(value))
    if kind == 'r' and number:
        body = scientific(number[2])
        return '$' + (r'\boldsymbol{' + body + '}' if number[1] else body) + '$'
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
            'exponent_coefficient': 'Diameter exponent coefficient', 'dispersion_energy_over_k': r'Dispersion energy $u_i/k_B$',
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
# caption: the one-sentence title; text after ' || ' is set as notes under the table body, as the journal guide asks.
def table(name, caption, headings, data, cols=None, landscape=False, sep=3):
    section_order = re.findall(r'\\section\{[^}]*\}\\label\{(sec:s-[^}]+)\}', (ROOT/'docs/scientific/latex/supplement.tex').read_text())
    sections = {label: f'S{i}' for i,label in enumerate(section_order,1)}
    def section_refs(value):
        return re.sub(r'\\+ref\{(sec:s-[^}]+)\}', lambda m: sections[m[1]], str(value))
    caption = section_refs(caption)
    data = [row if isinstance(row, str) else [section_refs(value) for value in row] for row in data]
    main_tables = set(re.findall(r'\\input\{tables/([^}]+)\}', ''.join(p.read_text() for p in (ROOT/'docs/scientific/latex/sections').glob('*.tex'))))
    if name.removesuffix('.tex') in main_tables:
        def rounded(value):
            return re.sub(r'(?<![\w.])[-+]?\d+\.\d{5,}(?:[eE][-+]?\d+)?', lambda m: (f'{float(m[0]):.4e}' if 0 < abs(float(m[0])) < .001 else f'{float(m[0]):.4f}'), str(value))
        data = [rounded(row) if isinstance(row, str) else [rounded(v) for v in row] for row in data]
    caption = display(caption.replace('CO₂', r'\ce{CO2}')).replace("Ma\\'mun", "Ma'mun")
    caption = caption[:1].upper() + caption[1:]
    caption = re.sub(r'(?<!\\)%', r'\%', caption).replace("\\'s", "'s")
    caption, _, notes = caption.partition(' || ')
    notes = notes and r'\footnotesize\raggedright ' + notes
    cols = cols or 'r'*len(headings)
    spec = '@{}' + ''.join(r'>{\raggedright\arraybackslash}p{' + f'{c:.4f}' + r'\linewidth}' if isinstance(c, float) else c for c in cols) + '@{}'
    head = ' & '.join(tex(display(h)) for h in headings) + r' \\'
    caption = r'\caption{' + caption + r'}\label{tab:' + name.removesuffix('.tex').replace('_', '-') + '}'
    # In a table with block labels, a row followed by another row ends with longtable's no-break \\*.
    blocked = any(isinstance(row, str) and r'\multicolumn' in row for row in data)
    rows = [row if isinstance(row, str) else ' & '.join(cell(x, c) for x, c in zip(row, cols, strict=True)) + (r' \\*' if blocked and isinstance(after, list) else r' \\')
            for row, after in zip(data, [*data[1:], None])]
    if len(data) <= 32 and not landscape and name != 'supplement_literature_comparison.tex':  # a table that fits on one page floats whole instead of breaking; a landscape page holds its table whole
        # The main text's journal class reads the table placement as its pos key; the supplement's article class reads it directly.
        place = '[!htbp]' if name.endswith('_reference_state.tex') or '{tables/' + name.removesuffix('.tex') + '}' in (ROOT/'docs/scientific/latex/supplement.tex').read_text() else '[pos=!htbp]'
        OUTPUTS[name] = '\n'.join([r'\begin{table}' + place + r'\small\setlength{\tabcolsep}{' + str(sep) + r'pt}\centering', caption, r'\begin{tabular}{' + spec + '}',
                                   r'\toprule', head, r'\midrule', *rows, r'\bottomrule', r'\end{tabular}',
                                   *([r'\par\smallskip\parbox{\linewidth}{' + notes + '}'] if notes else []), r'\end{table}', ''])
        return
    body = [r'\begingroup\small\setlength{\tabcolsep}{3pt}', r'\begin{longtable}{' + spec + '}', caption + r'\\',
            r'\toprule', head, r'\midrule\endfirsthead', r'\toprule', head, r'\midrule\endhead', r'\bottomrule\endfoot',
            *([r'\bottomrule', r'\multicolumn{' + str(len(headings)) + r'}{@{}p{\linewidth}@{}}{' + notes + r'}\\', r'\endlastfoot'] if notes else [])]
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
OTHER = {}


def other(path):  # DEA, MDEA and AMP files postdate BASE: hashed into the table headers, not compared with BASE
    data = (ROOT/path).read_bytes()
    OTHER[path] = hashlib.sha256(data).hexdigest()
    return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)




def reference_states():
    folder = E.parent/'reference-states-428'
    for case, spec in json.loads((folder/'tables.json').read_text()).items():
        record = json.loads((folder/f'{case}.json').read_text())
        assert all(record['checks'].values()), case
        inputs = [folder/'tables.json', folder/f'{case}.json']
        if case == 'mea':  # R1 and R3 on the common molality basis of the conversion equation (#432 Q4); ln K + Gamma does not depend on the basis
            inputs.append(ROOT/'analyses/round_3/results/q4.json')
            for r, c in zip(record['reactions'], json.loads(inputs[-1].read_text())['S15_common_basis'], strict=True):
                assert r['name'] == c['reaction'] and math.isclose(r['ln_K_source'] + r['Gamma'], c['common_ln_K'] + c['common_Gamma'], rel_tol=0, abs_tol=1e-9)
                r['ln_K_source'], r['Gamma'] = c['common_ln_K'], c['common_Gamma']
        rows = [[label, *(format(reduce(getitem, path, record), precision) if path else '' for path in paths)]
                for label, precision, *paths in spec['rows']]
        name = f'{case}_reference_state.tex'
        table(name, spec['caption'], spec['headings'], rows, spec['cols'])
        provenance = ''.join(f'% Input: {p.name} SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()}\n' for p in inputs)
        out = ROOT/'docs/scientific/latex/tables'/name if case == 'mea' else folder/name  # the retained #428 file keeps its mole-fraction R1 and R3 values
        if '--check' not in sys.argv:
            out.write_text(provenance+OUTPUTS[name])
        assert out.read_text() == provenance+OUTPUTS[name], name


    amp, mea, s12 = (json.loads((folder/f'{name}.json').read_text()) for name in ('amp', 'mea', 's12'))
    q = amp['trial_quantities']
    rows = [
        ('Trial Gibbs energy, $g/(RT)$', q['g_over_rt'], 'Per mole of true trial species'),
        ('Plane contraction', amp['plane_contraction'], 'Dimensionless'),
        ('Optimized $D$', q['tpd_over_rt'], 'Dimensionless'),
        ('Plane-value error estimate', q['plane_value_error_estimate_over_rt'], 'Dimensionless'),
        ('Donor slope', q['donor_slope_over_rt'], 'Dimensionless'),
        ('Donor-descent error estimate', q['descent_error_estimate_over_rt'], 'Dimensionless'),
        ('Reclosed supplied trial $D$', amp['supplied']['quantities']['tpd_over_rt'], 'Dimensionless'),
        ('Split-minus-parent $\\Delta G/(RT)$', amp['Gibbs_difference_over_RT_mol'], 'mol per declared feed'),
        ('Paired Gibbs numerical estimate', amp['split']['numerical_error_over_RT_mol'], 'mol per declared feed'),
        ('Equilibrium liquid amounts', ', '.join(map(str, amp['split']['amounts_mol'])), 'mol true species'),
        ('Equilibrium liquid densities', ', '.join(map(str, amp['split']['densities_mol_m3'])), 'mol/m³'),
        ('MEA initial and loaded liquid enthalpies', f"{mea['points']['initial']['H_J']}, {mea['points']['loaded']['H_J']}", 'J on the declared feed'),
        ('Pure CO₂ addition-stream enthalpy', mea['added_stream']['H_J_per_mol'], 'J/mol, vapor branch'),
        ('Loaded solution mass', mea['loaded_mass_kg'], 'kg'),
        ('MEA integral heat', mea['heat_kJ_mol'], 'kJ/mol added CO₂'),
        ('MEA equilibrium $C_P$', mea['cp_J_mol_K'], 'J/(mol apparent feed·K)'),
        ('MEA $C_P$ on loaded feed and per mass', f"{mea['cp_J_K']}, {mea['cp_kJ_kg_K']}", 'J/K; kJ/(kg solution·K)'),
        ('Centered re-solves at 0.10 and 0.05 K', ', '.join(map(str, mea['cp_stencil_J_mol_K'])), 'J/(mol apparent feed·K)'),
        ('Analytic minus fine centered $C_P$', mea['cp_minus_fine_J_mol_K'], 'J/(mol apparent feed·K)'),
    ]
    lines = ['| Quantity | Value | Basis |', '|---|---:|---|']
    lines += [f'| {label} | {value} | {unit} |' for label, value, unit in rows]
    lines += ['', '| Reaction | Source (kJ/mol reaction) | Fugacity correction (kJ/mol reaction) | Ideal-gas sum (kJ/mol reaction) |', '|---|---:|---:|---:|']
    lines += [f"| {r['name']} | {r['source_kJ_mol']:.2f} | {r['fugacity_kJ_mol']:.2f} | {r['ideal_gas_kJ_mol']:.2f} |" for r in mea['reactions']]
    differences = s12['nonzero_differences'][-1]['replay_minus_retained']
    pressure = max(abs(d.get('bubble_pressure_Pa', 0)) for d in differences)
    lines += ['', f"S12: {sum(r['printed_digits_agree'] for r in s12['replay'])} bubble states reproduce the displayed digits; the CO₂–water and MEA–water readbacks are identical to the retained records. For loaded MEA, the replays from the two starting pressures differ from the retained record in {' and '.join(str(len(d)) for d in differences)} unrounded fields; the largest bubble-pressure difference from the record is {pressure:.2e} Pa."]
    output = folder/'tables.md'
    text = '\n'.join(lines)+'\n'
    if '--check' not in sys.argv:
        output.write_text(text)
    assert output.read_text() == text, output


def main():
    document = a.load(F/'reported-parameters.json')
    fitrows = a.rows(F/'fitted-rows.csv')
    assert len(fitrows) == 307 and hashlib.sha256((F/'reported-parameters.json').read_bytes()).hexdigest() == 'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed'
    params = [r for r in a.rows(a.BUNDLE/'results/reduced-refit/parameter-details.csv') if r['fit']=='F2']
    assert len(params)==11
    # Standard errors on the responsive-row convention (#420): the 39 Kiepe rows have zero derivatives and leave the residual degrees of freedom.
    stage = other('analyses/mea_parameter_bundle/results/objective-weights-420/MEA/information.json.gz')['result']
    assert (stage['n'], stage['na'], stage['p'], stage['stage_denominator']) == (307, 268, 10, 258) and math.isclose(stage['SE_multiplier'] ** 2, stage['stage_variance'] / stage['variance'], rel_tol=1e-6)
    for r in params:
        if r['conditional_SE'] not in (None, ''): r['conditional_SE'] = float(r['conditional_SE']) * stage['SE_multiplier']
    a.close(sum(float(r['cost']) for r in fitrows),a.load(E/'candidate/replay.json')['cost'])
    coords = {r['identity']:r for r in params}
    values = {c['identity']: c['value']['magnitude'] for n in document['components'] + document['pairs'] for c in n['coefficients']}
    values |= {i: c['value']['magnitude'] for n in document['topology']['edges'] for i, c in a.coefficients(n)}
    # Parameters set by the three fits before the joint fit (Results): pure water to IAPWS-95, CO2-water to Kiepe pressures, MEA dielectric pair to permittivities.
    separate = {'component/water/segment_count', 'component/water/dispersion_energy_over_k', 'association/water/a/water/b/energy_over_k', 'association/water/a/water/b/volume',
                'pair/carbon-dioxide/water/k_ij', 'pair/carbon-dioxide/water/k_ij/reciprocal_temperature_slope',
                'component/monoethanolamine/dielectric_volume', 'component/monoethanolamine/dielectric_temperature'}
    unordered = lambda i: '/'.join(['pair', *sorted(i.split('/')[1:3]), *i.split('/')[3:]]) if i.startswith('pair/') else i
    fitted = {unordered(i) for i in [*coords, *separate]}
    assert len(fitted) == 19
    shown = set()
    def value(identity, mark='', decimals=None):
        if identity not in values:
            return '--'
        shown.add(identity)
        v = float(values[identity])
        # Main-text species inputs round to at most four decimal places; the supplement retains all parameter digits.
        text = f'{v:.4f}' if decimals is not None and identity in coords and identity.endswith(('segment_diameter', 'born_diameter')) else (f'{v:.{decimals}f}' if decimals is not None and round(v, decimals) not in (v, 0) else num(v, PARAMETER_DIGITS))
        return '**' * (unordered(identity) in fitted) + (full_precision(v) if decimals is None else text)
    species = [n['component_id'] for n in document['components']]
    shared_species, mark = ['carbon-dioxide','water','bicarbonate-anion','carbonate-anion','hydronium-cation','hydroxide-anion'], r'$^{\mathrm{a}}$'
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
    species_headings = ['Species', r'$m^{\mathrm{seg}}$', r'\makecell[rb]{$\sigma$\\(\AA)}', r'\makecell[rb]{$u/k_B$\\(K)}', r'\makecell[rb]{$\epsilon^{AB}/k_B$\\(K)}', r'$\kappa^{AB}$', '$z$',
                        r'\makecell[rb]{$d^\mathrm{Born}$\\(\AA)}', '$f$', r'\makecell[rb]{$d_V$\\(L/mol)}', r'\makecell[rb]{$d_T$\\(K)}']
    # Per species: the Ref. entry of the main-text table, then the supplement's source of a quantity (column of species_rows) that differs from it.
    note = lambda letters: r'$^{\mathrm{' + letters + '}}$'
    held = r'\cite{Held2014}'
    gross = r'\cite{Gross2001}'
    sources = [(r'\cite{Gross2001,Kleiner2007}', 'b', {1: gross, 2: gross, 3: gross, 4: r'Half the water value \cite{Kleiner2007}', 5: r'Water value \cite{Kleiner2007}'}),
               (r'\cite{Baygi2015}', 'c', {5: r'Converted from \cite{Baygi2015}'}),
               ('This work', '', {2: 'Coefficients below'}),
               *[('This work', 'd', {1: 'Single sphere', 7: r'Equal to $\sigma$'})] * 2,
               *[(held, 'e', {7: 'Set in this work'})] * 2,
               (held, 'f', {7: r'\cite{Figiel2025}'}),
               (held, 'g', {7: r'Calculated from \cite{palascakAccurateExperimentalValues2004}'})]
    # Charge, solvation and dielectric inputs are specified with their sources in S2.
    main_indices = [0,1,2,3,4,5,7]
    table('species_parameters.tex', r"Segment, association and Born parameters of the MEA model. || Bold: fitted in this work; --: not used. $^{\mathrm{a}}$Shared species, held fixed for DEA, MDEA and AMP. $^{\mathrm{b}}$Cross-association with water; its energy is half that of water. $^{\mathrm{c}}$Association volume converted in this work (Section~\ref{supp-sec:s-parameters}). $^{\mathrm{d}}$Single sphere; Born diameter equal to $\sigma$. $^{\mathrm{e}}$Born diameter set in this work. $^{\mathrm{f}}$Born diameter of the hydrogen ion in Ref.~\cite{Figiel2025}. $^{\mathrm{g}}$Born diameter calculated from the hydration free energy of Ref.~\cite{palascakAccurateExperimentalValues2004} (Section~\ref{supp-sec:s-parameters}). For the ions, the packing diameter is $0.88\sigma$ and the Debye--H\"uckel diameter is $\sigma$. Table~\ref{supp-tab:supplement-species-parameters} gives unrounded values and the remaining inputs.",
          [species_headings[i] for i in main_indices]+['Ref.'],
          [[row[0]+mark*(s in shared_species), *[row[i] for i in main_indices[1:]], ref + (note(letters) if letters else '')] for row,(ref,letters,_),s in zip(species_rows(4),sources,species,strict=True)],
          ['l']+['r']*6+['l'],sep=5)
    # Full parameter listing in the supplement: one quantity per row, with provenance.
    inline_headings = ['Species', r'$m^{\mathrm{seg}}$', r'$\sigma$ (\AA)', r'$u/k_B$ (K)', r'$\epsilon^{AB}/k_B$ (K)', r'$\kappa^{AB}$', '$z$', r'$d^\mathrm{Born}$ (\AA)', '$f$', r'$d_V$ (L/mol)', r'$d_T$ (K)']
    full=[]
    for row,(source,_,different) in zip(species_rows(),sources,strict=True):
        for i in range(1,len(row)):
            if row[i]=='--': continue
            origin=different.get(i,source)
            if i==6: origin='By definition'
            elif i==8: origin=r'\cite{Figiel2025}' if row[0]==r'\ce{H2O}' else 'Set in this work'
            elif i in (9,10): origin='Permittivity fit' if row[0]==r'\ce{MEA}' else (r'\cite{Yang2024}' if row[0]==r'\ce{H2O}' else 'Set in this work')
            full.append([row[0],inline_headings[i],row[i],origin])
    water_law = next(c for c in document['correlations'] if c.get('component_id') == 'water' and c.get('family') == 'segment_diameter')
    for coefficient in [water_law['constant'], *[c for term in water_law['terms'] for c in term.values()]]:
        full.append([symbol['water'], label(coefficient['identity']) + (' (' + (r'\AA' if coefficient['value']['unit'] == 'angstrom' else r'K$^{-1}$') + ')'), '**' * (coefficient is water_law['constant']) + full_precision(coefficient['value']['magnitude']), 'This work' if coefficient is water_law['constant'] else r'\cite{Held2008}'])
    table('supplement_species_parameters.tex', r"Complete species inputs of the MEA model. || Bold values were fitted in this work. CO2 association entries apply only to induced bonding with water. The water-diameter correlation and the MEA association-volume conversion are specified in the text.",
          ['Species','Quantity (unit)','Value','Source'],full,['l',.20,'r',.36])
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
                  *[('water', ion, r'\cite{Held2014}') for ion in ('carbonate-anion', 'hydronium-cation', 'hydroxide-anion')]]
    def pair_se(s, u, quantity=''):  # conditional standard error of a fitted interaction; none for a fixed value or one on its bound
        return num(next((coords[i+quantity]['conditional_SE'] for i in (f'pair/{s}/{u}/k_ij', f'pair/{u}/{s}/k_ij') if i+quantity in coords), None), 3)
    def pair_rows(decimals=None, errors=False):
        ref = lambda s, u, source: source if not errors or source.startswith(r'\cite') else 'This work' + (note('b') if source == 'CO2--water fit' else note('c') if {s,u} == {'protonated-monoethanolamine','carbamate-anion'} else '')
        return [[symbol[s]+'--'+symbol[u]+mark*(errors and {s,u} <= set(shared_species)),pair(s,u,decimals=decimals),*[pair_se(s,u)]*errors,pair(s,u,'/reciprocal_temperature_slope',decimals),*[pair_se(s,u,'/reciprocal_temperature_slope')]*errors,ref(s,u,source)] for s,u,source in pair_specs]
    table('interaction_matrix.tex', r"Nonzero or fitted binary interaction parameters of the MEA model with their conditional standard errors (s.e.), $k_{ij}(T)=k_{ij}(313.15\,\mathrm{K})+b_{ij}(1/T-1/313.15\,\mathrm{K})$. || Bold: fitted in this work. A standard error is given for the jointly fitted values that are not on a bound; an absent slope is zero. $^{\mathrm{a}}$Shared interaction, held fixed for DEA, MDEA and AMP. $^{\mathrm{b}}$Fitted beforehand to \ce{CO2}--water pressures (Section~\ref{sec:parameters}). $^{\mathrm{c}}$On its lower bound. All unlisted unlike-charge or neutral pairs have $k_{ij}=0$; same-sign ion dispersion is excluded. Table~\ref{supp-tab:supplement-interaction-matrix} gives unrounded values.",
          ['Pair',r'$k_{ij}(313.15\,\mathrm{K})$','s.e.',r'$b_{ij}$ (K)','s.e.','Ref.'],pair_rows(4,True),['l','r','r','r','r','l'])
    table('supplement_interaction_matrix.tex', r"Binary interactions at full precision. || Bold values were fitted in this work. All unlisted interactions and slopes are zero; same-sign ion dispersion is excluded.",
          ['Pair',r'$k_{ij}(313.15\,\mathrm{K})$',r'$b_{ij}$ (K)','Source'],pair_rows(),['l','r','r','l'])
    table('supplement_fitted_parameters.tex', r"Jointly fitted parameters, bounds and conditional standard errors. || Bold values were fitted in this work. A dash marks the active bound. Born diameters of the two amine ions equal their segment diameters.", ['Parameter','Value','Lower','Upper','Standard error'], [[label(r['identity']),'**'+full_precision(r['value']),num(r['lower']),num(r['upper']),num(r['conditional_SE'])] for r in params], [.27,'r','r','r','r'])
    reaction = a.load(a.BUNDLE/'results/adoption-297/paper-evidence/source-only/chemical_reaction_source_contract.json')
    rr = []
    for r in reaction['reactions']:
        law = next((n for n in document['reaction_correlations'] if n['reaction_id']==r['reaction_id']), None)
        values = {c['identity'].split(':')[-1]:c['value']['magnitude'] for c in law['coefficients']} if law else dict(r['correlation'])
        if not law: values['a'] += reaction['common_source_standard_state']['source_to_common_ln_k_offsets'][int(r['reaction_id'][1:])-1]
        if r['reaction_id']=='R5': values = dict(zip(('a','b_k','c','d_per_k'),[-math.log(10)*values['b'],-math.log(10)*values['a_k'],0,-math.log(10)*values['c_per_k']]))
        lhs, rhs = r['equation'].replace('CO3--','CO3^{2-}').split(' <=> ')
        rr.append([r['reaction_id'],r'\ce{'+lhs+r'} $\rightleftharpoons$ \ce{'+rhs+'}',*[full_precision(values.get(k,0)) for k in ('a','b_k','c','d_per_k')]])
    table('supplement_reaction_coefficients.tex', r"Coefficients of the equilibrium constants on the molality basis at full precision, for $\ln K=A+B/T+C\ln T+DT$ with $T$ in kelvin. || Reactions R1--R5 are defined in main-text Table~\ref{main-tab:reaction-equilibrium-constants}.", ['Reaction','$A$','$B$ (K)','$C$','$D$ (K$^{-1}$)'], [[r[0] + (' (MEA)' if r[0] in ('R4', 'R5') else ''), *r[2:]] for r in rr], ['l']+['r']*4)
    # Separate stoichiometry and coefficients to preserve every printed digit at readable size.
    reaction_names = dict(R1='Water autoprotolysis', R2=r'\ce{CO2} hydration', R3='Bicarbonate dissociation', R4='Carbamate hydrolysis', R5='Amine dissociation')
    reaction_rows = [[r[0], reaction_names[r[0]], r[1].replace('MEACOO-', 'ACOO-').replace('MEAH+', 'AH+').replace('MEA', 'A')] for r in rr]
    table('reaction_equilibrium_constants.tex', r"Aqueous reactions of an amine A, with the source and source temperature range of each equilibrium constant. || $^{\mathrm{a}}$Range stated for the correlation in its source. $^{\mathrm{b}}$Range of estimates made with a solubility model, not of measurements. $^{\mathrm{c}}$Starting correlation; its constant term and an enthalpy increment are then fitted (Table~\ref{tab:transfer-fitted}). $^{\mathrm{d}}$Correlation of Silkenb\"aumer et al., which represents three estimates that Xu et al.\ \cite{xuRepresentationEquilibriumSolubility1992} obtained with a solubility model. Table~\ref{supp-tab:supplement-reaction-coefficients} gives the coefficients of R1--R3 and of the MEA correlations on the molality basis, and Table~\ref{supp-tab:supplement-transfer-parameters} those of R4 and R5 for DEA, MDEA and AMP.", ['Reaction', 'Name', 'Stoichiometry'], reaction_rows, ['l','l','l'])
    ranges = {'MEA': {r['reaction_id']: r['temperature_range_k'] for r in reaction['reactions']}, 'DEA': other('analyses/dea_transfer/inputs/part-ii-346/route-current.json')['reaction_ranges_K'],
              'MDEA': other('analyses/mdea_mea_workflow/results/retransfer-343/reaction-ranges.json')['source_ranges_K'], 'AMP': other('analyses/amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json')['reaction_ranges_K']}
    assert all(ranges[amine][r] == [273.15, 498.15] for amine in ranges for r in ('R1', 'R2', 'R3'))
    # (reaction, amine, name of its range in that amine's file, source, note mark on the range, use in the fit)
    origins = [('R1--R3', 'all four', 'R1', r'Austgen et al.\ \cite{Austgen1991}', 'a', 'fixed'),
               ('R4', 'MEA', 'R4', r'Tong et al.\ \cite{Tong2012}', '', 'fixed'),
               ('R4', 'DEA', 'carbamate-hydrolysis', r'Aroua et al.\ \cite{arouaTemperatureDependencyEquilibrium1997}', '', r'fitted$^{\mathrm{c}}$'),
               ('R4', 'AMP', 'carbamate-hydrolysis', r'Silkenb\"aumer et al.\ \cite{silkenbaumerSolubilityCarbonDioxide1998}$^{\mathrm{d}}$', 'b', r'fitted$^{\mathrm{c}}$'),
               ('R5', 'MEA', 'R5', r'Bates and Pinching \cite{batesAcidicDissociationConstant1951}', '', 'fixed'),
               ('R5', 'DEA', 'DEA-dissociation', r'Bower et al.\ \cite{bowerAcidicDissociationConstant1962}', '', 'fixed'),
               ('R5', 'MDEA', 'MDEA-dissociation', r'P\'erez-Salado Kamps and Maurer \cite{perez-saladokampsDissociationConstantNMethyldiethanolamine1996}', '', 'fixed'),
               ('R5', 'AMP', 'AMP-dissociation', r'Hamborg and Versteeg \cite{hamborgDissociationConstantsThermodynamic2009}', '', 'fixed')]
    extra = [r'\par\medskip', r'\begin{tabular}{@{}llllrr@{}}', r'\toprule', r'Constant & Amine & Source & In the fit & \makecell[rb]{Source\\range (K)} & \makecell[rb]{Model-estimated\\range (K)$^{\mathrm{b}}$} \\', r'\midrule',
             *[f"{name} & {amine} & {source} & {use} & " + ('-- & ' if note == 'b' else '') + f"{ranges[amine if amine in ranges else 'MEA'][key][0]:g}--{ranges[amine if amine in ranges else 'MEA'][key][1]:g}" + (r'$^{\mathrm{a}}$' if note == 'a' else '') + (' & --' if note != 'b' else '') + r' \\' for name, amine, key, source, note, use in origins],  # note b marks model estimates, given in their own column
             r'\bottomrule', r'\end{tabular}']
    OUTPUTS['reaction_equilibrium_constants.tex'] = OUTPUTS['reaction_equilibrium_constants.tex'].replace(r'\par\smallskip\parbox', '\n'.join(extra) + '\n' + r'\par\smallskip\parbox')
    groups = {}
    for r in fitrows: groups.setdefault(rowkey(r['group'],r['quantity']),[]).append(r)
    assert set(groups) == set(ROWS) and len(groups[('species','mole_fraction')]) == 101
    # The Introduction states that the fitted heats, heat capacities and densities of MEA deviate by less than 3 %.
    caloric = [a.stats(groups[k])['AARD_percent'] for k in groups if k[1] in ('addition_enthalpy', 'equilibrium_isobaric_heat_capacity', 'phase_density')]
    assert len(caloric) == 4 and max(caloric) < 3 and 'heat capacities and densities by less than 3\\,\\%' in (ROOT/'docs/scientific/latex/sections/introduction.tex').read_text()
    compare = a.rows(a.BUNDLE/'results/reduced-refit/fit-comparison.csv')
    agreement = a.rows(a.BUNDLE/'results/reduced-refit/agreement.csv')
    score = lambda fit, dataset: next(r for r in agreement if r['fit']==fit and r['dataset']==dataset)['aard_percent']
    table('choice_cost.tex', r"Cumulative parameter restrictions and the resulting deviations on identical observations. || $C$: objective value. The deviations are for the 47 fitted pressures, the 112 pressures not fitted and the 47 fitted loaded densities. Each row adds its restriction to the row above; the last row is an alternative to the row above it, and both start from the sodium-salt row. The fourth row also fixes the carbamate--water interaction and the temperature slope of the protonated-MEA--water interaction at zero. The sodium-salt row fixes the temperature-dependent water--bicarbonate and water--carbonate interactions at values fitted to the osmotic coefficients of aqueous sodium bicarbonate and sodium carbonate that Peiper and Pitzer derived from their model \cite{peiperThermodynamicsAqueousCarbonate1982}, and adds a protonated-MEA--bicarbonate interaction as a fitted parameter. The last two rows fix the protonated-MEA--bicarbonate and the protonated-MEA--carbamate interaction at zero, respectively. Deviations on fitted and not-fitted data are not directly comparable.", ['Calibration','Parameters','On bounds','$C$',r'\makecell[rb]{Fitted\\pressure\\AARD (\%)}',r'\makecell[rb]{Not-fitted\\pressure\\AARD (\%)}',r'\makecell[rb]{Fitted\\density\\AARD (\%)}'], [[r['fit'],r['fitted_parameters'],r['on_bound'],num(r['cost'],6),*[f"{float(score(r['fit'],d)):.2f}" for d in ('fitted: fitted CO2 partial pressure','not fitted: six-source pressures','fitted: loaded density')]] for r in compare], [.36]+['r']*6)
    cp = a.load(E/'same-data-comparison/part1-scores.json')
    heat_capacity_labels = {'Weiland1997 comparison': 'Weiland et al.\\ heat capacities \\cite{weilandHeatCapacityAqueous1997}', 'Concepcion2023 comparison': "Concepci\\'on et al.\\ heat capacities \\cite{concepcionHeatCapacitiesDifferent2023}"}
    same_names = {'Six-source pressures':'All pressures at 30 wt% MEA, six sources', 'Species fractions':'All species fractions', '112 current-not-fitted pressures':'Pressures not fitted, the same six sources', 'broad Cp':'Hilliard heat capacities at 313.15--393.15 K'}
    # The published fitting account of the earlier model does not give the role of each pressure and species observation.
    earlier_role = lambda role: 'not stated' if 'see role note' in role else role.split(';')[0].replace('formulation ','')
    # Fitted quantities that the earlier model was scored on with identical observations, and the prior use of the comparison sets.
    same = {('common149','partial_pressure'): '47 current-fitted pressures', ('Jakobsen','amount_ratio'): 'Species ratios', ('common149','addition_enthalpy'): 'Vinjarapu2024 heats', ('Cp','equilibrium_isobaric_heat_capacity'): 'Four Hilliard heat capacities'}
    prior = {'Arcis2011': 'a', 'Kim heat 313': 'b', 'Kim heat 353': 'b', 'Amundsen2009': 'c', 'Hartono2014': 'c', 'Han2012': 'c'}
    earlier = {r['group']: r for r in cp}
    # Deviations show two decimals; an RMSE of the main-text table keeps four significant digits, as in its fitted block.
    both = lambda r, value, main: [f'{float(value):.2f}', '--'] if r['metric'].startswith('AARD') else ['--', num(value) if main else f'{float(value):.2f}']
    data = [block(8, 'Fitted', True)]
    for key, rows in groups.items():
        r = earlier.get(same.get(key))
        data.append([rowlabel(key), len(rows), 'fitted', f"{a.stats(rows)['AARD_percent']:.2f}", '--' if 'pressure' in key[1] else num(a.stats(rows)['RMSE']/(1000 if key[1]=='addition_enthalpy' else 1)), *([earlier_role(r['roles'][0]), *both(r, r['deviations'][0], True)] if r else ['--']*3)])
    data.append(block(8, 'Not fitted, or fitted in part'))
    aside = []  # the sets of this block that are not pressures are listed in the supplement
    for r in cp:
        if r['group'] in same.values(): continue
        unit = r['metric'].partition('(')[2].rstrip(')')
        main = 'pressures' in r['group'] or r['group'] == 'Species fractions'
        (data if main else aside).append([cited(r['group'], heat_capacity_labels.get(r['group'], same_names.get(r['group'], r['group']))) + ('' if r['metric'].startswith('AARD') else f' ({unit})'), r['n'][0],
                     r['roles'][1].split(';')[0] + next((r'$^{\mathrm{' + m + '}}$' for k, m in prior.items() if r['group'].startswith(k)), ''), *both(r, r['deviations'][1], main), earlier_role(r['roles'][0]), *both(r, r['deviations'][0], main)])
    table('mea_data.tex', r"Data for MEA with their roles in the joint fit of the MEA model, the deviations of that model, and the deviations of the model of Polley and Hedengren CITE14 on identical observations. || --: not calculated; a pressure deviation is given as AARD only. Roles refer to the objective of each model; ``not stated'': Ref.~CITE14 does not state for every pressure and species observation whether it was fitted. For that model, the species-ratio and carbonate-share measurements informed an earlier fit of the ion parameters but were not in the objective of the published parameters. The sets of the lower block overlap with each other and with the fitted observations, so their counts are not additive; Table~\ref{supp-tab:supplement-mea-comparison} lists the sets of that block that are not pressures. The 39 \ce{CO2}--water pressures of Kiepe et al.\ remain in the objective although the \ce{CO2}--water interaction was fitted to them beforehand and is fixed; they contribute 0.0007 to $C$ (Table~\ref{supp-tab:objective-groups}). Deviations on fitted and not-fitted data are not directly comparable.".replace('CITE14', CITE14),
          ['Quantity (unit)', '$N$', 'Role', r'\makecell[rb]{AARD\\(\%)}', 'RMSE', 'Role in '+CITE14, r'\makecell[rb]{AARD (\%)\\'+CITE14+'}', r'\makecell[rb]{RMSE\\'+CITE14+'}'], data, [.31,'r',.15,'r','r',.10,'r','r'])
    table('supplement_mea_comparison.tex', r"Data for MEA that are not fitted, or fitted in part, and are not pressures, with the deviations of the MEA model and of the model of Polley and Hedengren CITE14 on identical observations. || The columns are those of main-text Table~\ref{main-tab:mea-data}. $^{\mathrm{a}}$Also used to select the parameters; $^{\mathrm{b}}$three of these intervals were fitted during earlier model development, in the objective of Ref.~CITE14; no interval of Kim and Svendsen is in the reported fit; $^{\mathrm{c}}$the comparison between density sources informed the choice of fitted density observations. The densities of Ref.~CITE14 are those of its equation of state; for column hydraulics Ref.~CITE14 uses a separate empirical density correlation (its Section~2.2 and Appendix~A.2), so its loaded-density RMSEs of 135--153 kg/m$^3$ describe the liquid volume of that equation of state under load, not that hydraulic density. These sets overlap with each other and with the fitted observations, so their counts are not additive.".replace('CITE14', CITE14),
          ['Quantity (unit)', '$N$', 'Role', r'\makecell[rb]{AARD\\(\%)}', 'RMSE', 'Role in '+CITE14, r'\makecell[rb]{AARD (\%)\\'+CITE14+'}', r'\makecell[rb]{RMSE\\'+CITE14+'}'], aside, [.31,'r',.15,'r','r',.10,'r','r'])
    covariance = a.load(E/'uncertainty/covariance.json')
    interior = [label(r['identity']) for r in params if r['conditional_SE'] not in (None, '')]
    assert len(interior) == 10 == len(covariance['native_correlation'])
    table('supplement_correlations.tex', r"Conditional correlations of the 10 fitted parameters that are not at a bound.", ['Parameter']+[str(i+1) for i in range(10)], [[f'{i+1}. {interior[i]}']+[num(v,3) if j<=i else '' for j,v in enumerate(row)] for i,row in enumerate(covariance['native_correlation'])], [.26]+['r']*10)
    profiles = a.load(E/'uncertainty/profiles.json')
    table('bound_profiles.tex', r"Refits with the \ce{MEAH+}--\ce{MEACOO-} interaction fixed inside its lower bound. || The other parameters are refitted. Phase stability was not searched for these refits.", ['Distance from the bound (% of range)','Fixed interaction','$C$','Change in $C$'], [[num(100*r['fraction']),num(r['fixed_value']),num(r['cost'],9),num(r['delta_cost'],7)] for r in profiles], ['r']*4)
    # The shared water-bicarbonate interaction fixed at two other values whose MEA refits stay within the largest change of bound_profiles; MDEA refitted at each.
    S, M = 'analyses/mdea_mea_workflow/results/shared-bicarbonate-417/', 'analyses/mdea_mea_workflow/results/bounded-binary-411/'
    profile, search, compared = (other(S + f) for f in ('profile.json.gz', 'mdea-search-readback.json', 'mdea-comparison.json.gz'))
    model_cost = a.load(E/'candidate/replay.json')['cost']
    assert abs(model_cost - profile['center_cost']) <= 1e-6 * model_cost  # the caption's statement about the refit at k0
    reported, states = other(M + 'summary-row.json'), other(M + 'stability.json')['grid']['states']
    allowance, sides = max(r['delta_cost'] for r in profiles), [profile['selected'][s] for s in ('low', 'high')]
    assert all(0 < p['cost'] - profile['center_cost'] <= allowance and p['k'] == search[s]['k'] for p, s in zip(sides, ('low', 'high')))
    assert other(S + 'mdea-group-readback.json')['ordered_cases'] == ['reported', 'low', 'high']
    def aard(group):
        cases = compared[group]['original']
        assert len({c['relative_rows'] for c in cases}) == 1
        return [f"{c['AARD_percent']:.2f}" for c in cases]
    assert all(2 * search[s]['pressure_reference_failures'] > search[s]['counts']['unavailable_records'] for s in ('low', 'high'))
    ermatchkov = compared['Ermatchkov']['original'][0]['relative_rows']
    def pooled(sets):  # count-weighted over the sets: the AARD over all of their observations
        cases = [compared[g]['original'] for g in sets]
        n = sum(c[0]['relative_rows'] for c in cases)
        return n, [sum(c[i]['relative_rows'] * c[i]['AARD_percent'] for c in cases) / n for i in range(3)]
    # Total pressures and CO2 partial pressures are different observables; the pooled group mixes them.
    outside = {'Total pressures': pooled(('corrected-Kamps', 'Kuranov-413K', 'Sedighi')), 'CO2 partial pressures': pooled(('Ermatchkov', 'Xiao'))}
    whole = compared['all pressures not fitted']['original']
    assert sum(n for n, _ in outside.values()) == whole[0]['relative_rows'] and all(abs(pooled(('corrected-Kamps', 'Kuranov-413K', 'Sedighi', 'Ermatchkov', 'Xiao'))[1][i] - whole[i]['AARD_percent']) < 1e-9 for i in range(3)), 'the five sets are every pressure outside the objective'
    outside = {k: (n, [f'{v:.2f}' for v in values]) for k, (n, values) in outside.items()}
    table('mdea-shared-control.tex', rf"Controlled transfer to MDEA: the shared water--bicarbonate interaction $k$ fixed at the value of the MEA model and at two other values, with the MEA and the MDEA parameters refitted at each. || Fixed in every column: the other shared parameters, the reaction correlations, the MDEA data, weights and bound, and the three initial MDEA parameter sets. Refitted: the other ten MEA parameters and the eight MDEA parameters. $C(k)$: objective of the MEA fit with $k$ fixed; the refit at the value of the MEA model, $k_0$, reproduces the objective of the MEA model within $10^{{-6}}C$, and both other values keep $C(k)-C(k_0)$ within {allowance:.4f}, the largest change among the refits that hold the \ce{{MEAH+}}--\ce{{MEACOO-}} interaction inside its bound (Table~\ref{{supp-tab:bound-profiles}}). $P$: total pressure; AARD follows Eq.~\eqref{{eq:aard}}. The {ermatchkov} CO2 partial pressures of Ermatchkov et al.\ among the pressures outside the objective helped choose the initial MDEA parameters. Most unfinished searches are at states where no bubble pressure could be calculated; a confirmed split is a second liquid confirmed by a two-liquid equilibrium calculation. The searches are those of Table~\ref{{tab:amine-summary}} and do not include the fixed-pressure calculation of Section~\ref{{sec:results-mdea-phase}}.",
          ['Quantity', 'MEA model, $k_0$', 'Lower value', 'Upper value'],
          [['Water--bicarbonate interaction $k$', *(f'{k:.4f}' for k in (profile['center']['k'], *(p['k'] for p in sides)))],
           ['MEA objective change $C(k)-C(k_0)$', *(f"{c - profile['center_cost']:.4f}" for c in (model_cost, *(p['cost'] for p in sides)))],
           ['MDEA objective', *(f'{c:.4f}' for c in (reported['data_cost'], search['low']['cost'], search['high']['cost']))],
           [f"Fitted loaded-solution $P$ of Kuranov et al.\\ ({compared['Kuranov']['original'][0]['rows']}), AARD (%)", *aard('Kuranov')],
           [f"All fitted MDEA pressures, with the CO2-free binary pressures ({compared['all pressures fitted']['original'][0]['rows']}), AARD (%)", *aard('all pressures fitted')],
           *([f"{label} outside the objective ({n}), AARD (%)", *values] for label, (n, values) in outside.items()),
           [f'Unfinished searches of {states}', reported['unavailable_searches'], *(search[s]['counts']['unavailable_records'] for s in ('low', 'high'))],
           ['Confirmed liquid--liquid splits', reported['liquid_liquid_splits_found'], *(search[s]['counts']['confirmed_distinct_splits'] for s in ('low', 'high'))]],
          [.46, 'r', 'r', 'r'])
    kim = a.load(F/'kim2007-heat-pathways/summary.json')['temperatures']
    table('kim_alternatives.tex', r"Kim finite-interval heat comparisons at 393.15 K for alternative source exclusions. || RMSE is kJ/mol absorbed CO2; AARD is percent. All alternatives use the MEA model.", ['Intervals','$N$','RMSE','AARD'], [[name,kim['393.15']['metrics']['semi_differential'][key]['n'],num(kim['393.15']['metrics']['semi_differential'][key]['rmse'],6),num(kim['393.15']['metrics']['semi_differential'][key]['aard_percent'],6)] for key,name in [('all_printed','All tabulated intervals'),('source_consistent','Without the two inconsistent intervals'),('without_first120','Also without first intervals')]], ['l','r','r','r'])
    weights = a.rows(E/'objective-groups.csv')
    weight_groups = {}
    for r in weights: weight_groups.setdefault(rowkey(r['group'],r['quantity']),[]).append(r)
    assert list(weight_groups) == list(groups)
    table('objective_groups.tex', r"Assigned objective scales and weights. || Scales are in the unit of the quantity, and unity for the logarithmic pressure residuals. The text gives the origin of each scale and weight.", ['Quantity','$N$','Scale range','Weight range','Contribution to $C$'], [[rowlabel(key,False),sum(int(r['n']) for r in part),span(float(r['scale']) for r in part),span(float(r['weight']) for r in part),num(sum(float(r['cost']) for r in part),6)] for key,part in weight_groups.items()], [.42,'r','l','l','r'])
    checks = a.load(E/'check-values.json')
    # Each bubble pressure was solved from two initial pressures; the digits shown must agree.
    state = [('$T$ (K)', lambda r, k: num(r['T_K'],7)), ('Bubble pressure (Pa)', lambda r, k: num(r['answers'][k]['bubble_pressure_Pa'],10)), (r'Liquid density (kg/m$^3$)', lambda r, k: num(r['answers'][k]['density_kg_m3'],10))]
    assert all(get(r,0) == get(r,1) for _, get in state for r in checks)
    contribution_names = dict(association='Association', born='Born', hard_chain='Hard chain', dispersion='Dispersion', debye_huckel=r'Debye--H\"uckel', residual_helmholtz='Total residual')
    table('supplement_check_values.tex', r"Reference values of the MEA model at three bubble states, for checking an implementation: temperature, bubble pressure, liquid mass density, reduced residual Helmholtz contributions $A_i/(nRT)$ and true liquid species fractions. || Inputs: $x_{\ce{CO2}}=3.6\times10^{-4}$ in water; $x_{\ce{MEA}}=0.9264$ in MEA--water; 30 wt\% MEA at loading 0.3 mol/mol. Each bubble pressure was solved from two initial pressures, which agree to the digits shown. Zero terms are omitted. These values check the numerical calculation; they are not measurements.", ['Quantity',r'\ce{CO2}--water','MEA--water','Loaded MEA'], [[name,*[get(r,0) for r in checks]] for name,get in state]+[[('$x_{'+symbol[key[2:]]+'}$') if key.startswith('x_') else contribution_names[key],*[num(r['answers'][0][key],10) for r in checks]] for key in checks[0]['answers'][0] if key not in ('bubble_pressure_Pa','density_kg_m3','molar_density_mol_m3') and any(r['answers'][0][key] for r in checks)], ['l','r','r','r'])
    shared = a.rows(E/'shared-coefficients.csv')
    # One row per shared species; every other shared value follows from a rule stated in the note, which the checks below hold to the retained list.
    sv = {r['identity']: float(r['value']) for r in shared}
    water_pair = lambda s: next((i for i in (f'pair/{s}/water/k_ij', f'pair/water/{s}/k_ij') if i in sv), '')
    used = {f'component/{s}/{q}' for s in shared_species for q in ('segment_count','segment_diameter','dispersion_energy_over_k','born_diameter','solvation_factor')} | {water_pair(s) for s in shared_species}
    for s in shared_species[2:]:
        sigma = sv[f'component/{s}/segment_diameter']
        assert math.isclose(sv[f'component/{s}/packing_diameter'], 0.88*sigma, rel_tol=1e-12) and sv[f'component/{s}/debye_huckel_diameter'] == sigma
        used |= {f'component/{s}/packing_diameter', f'component/{s}/debye_huckel_diameter'}
    slope, dielectric = 'pair/carbon-dioxide/water/k_ij/reciprocal_temperature_slope', [f'component/{s}/dielectric_{q}' for s in shared_species[:2] for q in ('volume','temperature')]
    assert [sv[i] for i in dielectric] == [1e-08, 1403.0, 0.3777, 1403.0]
    assert all(sv[i] == 0 for i in set(sv) - used - {slope, *dielectric})
    # S2 and S3 already list species fields and the explicitly retained pairs.
    covered_pairs = {tuple(sorted((x, y))) for x, y, _ in pair_specs}
    missing = [r for r in shared if (r['identity'].startswith('component/') and r['identity'].rsplit('/', 1)[-1] in ('packing_diameter', 'debye_huckel_diameter')) or (r['identity'].startswith('pair/') and tuple(sorted(r['identity'].split('/')[1:3])) not in covered_pairs)]
    table('supplement_shared_remaining.tex', r"Shared parameters not listed in Tables~\ref{tab:supplement-species-parameters} and \ref{tab:supplement-interaction-matrix}, at full precision. || Together with the reaction coefficients in Table~\ref{tab:supplement-reaction-coefficients}, those tables give the unrounded values of the shared parameters marked in main-text Tables~\ref{main-tab:species-parameters} and \ref{main-tab:interaction-matrix}.", ['Parameter','Value','Unit','Source'], [[label(r['identity']), f"{float(r['value']):.15g}" if r['identity'].endswith('/packing_diameter') else full_precision(r['value']), r['unit'],
                                          r'$0.88\sigma$' if r['identity'].endswith('/packing_diameter') else r'Equal to $\sigma$' if r['identity'].endswith('/debye_huckel_diameter') else 'Set in this work'] for r in missing], [.42,'r','l','l'])
    table('pressure_sources.tex', r"Pressure deviations of the MEA model by experimental source at nominal 30 wt\% MEA. || Source subsets contain both fitted observations and observations that are not fitted.", ['Source','Observations','AARD (%)'], [[cited('', SOURCE_NAMES[s]) + r' \cite{' + PRESSURE_CITE[s] + '}',len(part),format(a.stats(part)['AARD_percent'], '.1f')] for s in sorted({r['source'] for r in a.rows(F/'canonical-pressure.csv')}) for part in [[r for r in a.rows(F/'canonical-pressure.csv') if r['source']==s]]], ['l','r','r'])
    a.load(E/'candidate/replay.json'); a.load(E/'uncertainty/covariance.json'); a.load(E/'stability/candidate/search.json'); a.load(a.BUNDLE/'results/split-cause-342/final-supplied-F2-summary.json')
    for name, body in OUTPUTS.items():
        body = GROUP.sub(r'\\num{\g<0>}', body)
        header = '% Generated from '+BASE+'; F2 ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed\n'+''.join('% Input: '+p+' SHA256 '+h+'\n' for p,h in sorted(a.INPUTS.items()))+''.join('% Input (working tree): '+p+' SHA256 '+h+'\n' for p,h in sorted(OTHER.items()))
        if '--check' in sys.argv: assert (TABLES/name).read_text()==header+body, name
        else: (TABLES/name).write_text(header+body)
    print(json.dumps({'tables_checked':len(OUTPUTS),'inputs_verified_at_commit':len(a.INPUTS),'commit':BASE}))
    (ROOT/'docs/scientific/latex/builds/347-input-hashes.json').write_text(json.dumps({'commit':BASE,'files':a.INPUTS},indent=2)+'\n')

if __name__ == '__main__':
    reference_states() if '--reference-states' in sys.argv else main()
