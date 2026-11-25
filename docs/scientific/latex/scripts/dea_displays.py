"""Present retained DEA, MDEA and AMP results and the tables that compare the four amines, with a byte-for-byte display check; no model calls."""
import collections
import csv
import gzip
import hashlib
import json
import math
import re
import sys
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from fixed_reference import DESIGNS, KIEPE_AUTHOR, KIEPE_CITE, FixedReference

ROOT = Path(__file__).resolve().parents[4]
LATEX = ROOT / 'docs/scientific/latex'
BASE = 'analyses/dea_transfer/results/refit-413/'
MEA = 'analyses/mea_parameter_bundle/results/'  # read as retained files, so replacing them refreshes every MEA number shown here
SALT = MEA + 'salt-anchored-435/'
MEAFIT = SALT + 'MEA/F4/'
MEAEVIDENCE = SALT + 'MEA/evidence/F4/'
DEA = BASE.replace('refit-413', 'salt-anchored-435/campaign')
ROUND7 = 'analyses/round_7/'
ROUND8 = 'analyses/round_8/results/'

REPLAYS = ROUND7 + 'results/display-replays/'
DEA7, MDEA7, AMP7 = (ROUND7 + 'results/' + name + '/' for name in ('F', 'C/salt', 'AMP'))
outputs = {}
sources = {}

def read(name):
    path = (ROOT / name).resolve()
    raw = path.read_bytes()
    sources[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    data = gzip.decompress(raw) if path.suffix == '.gz' else raw
    if name.removesuffix('.gz').endswith('.json'):
        return json.loads(data)
    return list(csv.DictReader(data.decode().splitlines()))


GROUP = re.compile(r'(?<![\w.{-])-?\d{5,}(?:\.\d+)?(?![\w}])')  # numbers with five or more integer digits get a thin-space digit group

def emit(name, text):
    outputs[LATEX / name] = GROUP.sub(r'\\num{\g<0>}', text) if name.endswith('.tex') else text

# Data sets: display name, citation key and measured property.
SETS = {
    'Lawson': ('Lawson and Garst', 'lawsonGasSweeteningData1976', r'$p_{\COtwo}$'),
    'Carson': ('Carson et al.', 'carsonEnthalpySolutionCarbon2000', 'integral heat'),
    'Lawson-394K': ('Lawson and Garst, highest temperature', 'lawsonGasSweeteningData1976', r'$p_{\COtwo}$'),
    'SeoHong': ('Seo and Hong', 'seoSolubilitiesCarbonDioxide1996', r'$p_{\COtwo}$'),
    'Lal': ('Lal et al.', 'lalSolubilityH2SCO21985', r'$p_{\COtwo}$'),
    'Weiland': ('Weiland et al.', 'Weiland1998', 'density'),
    'Lawson-VIII': (r'Lawson and Garst, 50--54.5 wt\%', 'lawsonGasSweeteningData1976', r'$p_{\COtwo}$'),
    'Bottinger-DEA_plus_DEAH': (r'B\"ottinger et al., DEA + DEAH$^+$', 'Bottinger2008', 'mole fraction'),
    'Bottinger-DEACOO': (r'B\"ottinger et al., carbamate', 'Bottinger2008', 'mole fraction'),
    'Bottinger-HCO3': (r'B\"ottinger et al., bicarbonate', 'Bottinger2008', 'mole fraction'),
    'Cai': ('Cai et al.', 'caiBinaryIsobaricVaporLiquid1996', 'bubble pressure'),
    'Horstmann': ('Horstmann et al.', 'horstmannPhaseEquilibriumExcess2002', 'excess enthalpy'),
}
LAWS = {'carbamate-hydrolysis': 'R4', 'DEA-dissociation': 'R5'}

def name(group, cite=False):
    return SETS[group][0] + (r' \cite{' + SETS[group][1] + '}' if cite else '')

def num(value, digits=3):
    if value is None:
        return '---'
    return f'${float(value):.{digits}f}$'

def bold(text):
    """Set the first number of a cell in bold: the mark of a value fitted in this work."""
    return re.sub(r'\$([^$]+)\$', r'$\\boldsymbol{\1}$', text, count=1)

def span(values, fmt):
    return fmt(min(values)) if min(values) == max(values) else fmt(min(values)) + '--' + fmt(max(values))

def table(name, caption, headers, rows, widths, long=False, notes='', size=r'\small'):
    columns = ''.join(r'>{\raggedright\arraybackslash}p{' + str(w) + r'\linewidth}' for w in widths)
    head = ' & '.join(headers) + r' \\ \midrule' + '\n'
    keep = lambda row: row[0].startswith(r'\addlinespace') or (row[0].startswith('R4, ') and not row[0].endswith('$d$'))
    body = '\n'.join(' & '.join(map(str, row)) + r' \\' + ('*' if keep(row) else '') for row in rows)
    if long:
        text = r'\begingroup' + size + r'\setlength{\tabcolsep}{2pt}\begin{longtable}{@{}' + columns + '@{}}\n'
        text += r'\caption{' + caption + r'}\label{tab:' + name + r'}\\' + '\n'
        text += r'\toprule ' + head + r'\endfirsthead\toprule ' + head + r'\endhead\bottomrule\endfoot'
        if notes:
            text += r'\bottomrule\multicolumn{' + str(len(widths)) + r'}{@{}p{0.95\linewidth}@{}}{\footnotesize ' + notes + r'}\\\endlastfoot'
        text += '\n' + body + '\n' + r'\end{longtable}\endgroup' + '\n'
    else:
        text = r'\begin{table}' + ('[!htbp]' if name.startswith('supplement') else '[pos=!htbp]') + size + r'\setlength{\tabcolsep}{2pt}\caption{' + caption + r'}\label{tab:' + name + '}\n'
        text += r'\begin{tabular}{@{}' + columns + '@{}}\n' + r'\toprule ' + head
        text += body + '\n' + r'\bottomrule\end{tabular}'
        if notes:
            text += '\n' + r'\par\smallskip{\footnotesize\raggedright ' + notes + r'\par}'
        text += r'\end{table}' + '\n'
    emit('tables/' + name + '.tex', text)

def coordinates(uncertainty):
    return {
        r['identity']: dict(value=r['origin'], bounds=r['bounds'], on_bound=i in uncertainty['active_bounds'],
                            error=uncertainty['conditional_standard_error'].get(r['identity']))
        for i, r in enumerate(uncertainty['coordinates'])
    }


fixed = FixedReference(read)
round9 = read('analyses/round_9/manuscript-handoff.json')['quantities']
r9_accounting = round9['R3 start, endpoint and search accounting']
r9_units = round9['R7 AMP hydrolysis enthalpy increment']

ddoc, mdoc, adoc = [fixed.fits[name]['endpoint'] for name in ('DEA', 'MDEA', 'AMP_free')]
dcost, mcost, acost, afcost = [fixed.value(name + ' selected objective') for name in DESIGNS[1:]]
dassessment = fixed.endpoint_record('DEA/property-comparisons/selected.json.gz', 'DEA')
aassessment = fixed.endpoint_record('AMP_free/properties.json.gz', 'AMP_free')
afassessment = fixed.endpoint_record('AMP_fixed/properties.json.gz', 'AMP_fixed')
mrefit = read(MDEA7 + 'refit.json.gz')
mprior = read(MDEA7 + 'incumbent.json.gz')
dcoords, acoords = (coordinates(fixed.conditional(name)) for name in ('DEA', 'AMP_free'))

params = read(BASE + 'parameter-values.csv')
fitted_names = [r'$k_{\mathrm{DEAH^+,w}}$', r'$k_{\mathrm{DEACOO^-,w}}$', r'R4 constant term $A_4$', r'R4 enthalpy increment $\delta h$']
head = lambda text, n: [r'\addlinespace\multicolumn{' + str(n) + r'}{@{}l}{\textit{' + text + '}}']
fit_rows = [head('DEA', 5)]
data = dassessment['rows']


def deviations(rows):
    relative = [100 * (r['value'] / r['observed'] - 1) for r in rows
                if r['status'] == 'Available' and r['observed'] != 0]
    return dict(rows=sum(r['status'] == 'Available' for r in rows), relative_rows=len(relative),
                AARD_percent=math.fsum(map(abs, relative)) / len(relative) if relative else None,
                bias_percent=math.fsum(relative) / len(relative) if relative else None)


dev = {group: deviations([r for r in data if r['group'] == group]) for group in SETS}

def marks(group):
    out = []
    for law in LAWS:
        flags = {x['outside_ranges'][law] for x in data if x['group']==group}
        out.append('mixed' if len(flags)>1 else ('out' if True in flags else 'in' if False in flags else '---'))
    return out

def composition(group):
    rs = [r for r in data if r['group']==group]
    def get(key, scale=1):
        values = []
        for r in rs:
            try: values.append(scale*float(r['row'][key]))
            except (KeyError, ValueError, TypeError): pass
        return values
    g = lambda v: f'${v:g}$'
    if get('x_water'): return r'$x_{\mathrm{w}}=\,$' + span(get('x_water'), g), '---'
    if get('DEA_kmol_per_m3'): amine = span(get('DEA_kmol_per_m3'), lambda v: num(v,1)) + r' kmol/m$^3$'
    else: amine = span(get('DEA_mass_percent') or get('DEA_mass_fraction', 100), g) + r' wt\%'
    if group == 'Carson': return amine, span(get('x_CO2'), lambda v: num(v,4)) + r'\textsuperscript{a}'
    return amine, span(get('alpha_mol_CO2_per_mol_DEA') or get('alpha_mol_CO2_per_mol_amine'), g)

count = lambda n, used: str(n) + (f' ({used})' if used != n else '')
data_rows = [head('DEA', 11)]
for group in dict.fromkeys(r['group'] for r in data):
    rs = [r for r in data if r['group']==group]
    t = [r['T_K'] for r in rs]
    data_rows.append([name(group, cite=True), SETS[group][2], rs[0]['role'], count(len(rs), dev.get(group, {}).get('relative_rows', 0)), span(t, lambda v: num(v,2)), *composition(group), *marks(group), num(dev.get(group, {}).get('AARD_percent'),2), num(dev.get(group, {}).get('bias_percent'),2)])
DATA_HEAD = ['Data set','Property','Role',r'$N$',r'$T$ (K)','Amine content',r'$\alpha$ (mol/mol)','R4','R5',r'AARD (\%)',r'Bias (\%)']
rows = []
for group in dict.fromkeys(r['group'] for r in data):
    cells = []
    for law in LAWS:
        for outside in (False, True):
            stat = deviations([r for r in data if r['group'] == group and r['outside_ranges'][law] is outside])
            cells += [f"{stat['rows']}/{stat['relative_rows']}", num(stat['AARD_percent'], 2)] if stat['rows'] else ['---', '---']
    if set(cells) != {'---'}:
        rows.append([name(group), *cells])
top = ' & ' + ' & '.join(r'\multicolumn{2}{@{}l}{' + law + ', ' + side + '}' for law in LAWS.values() for side in ['inside','outside']) + r' \\ '
table('supplement-dea-ranges','Deviations of the DEA model inside and outside the measured temperature ranges of the carbamate hydrolysis constant (R4) and the DEA dissociation constant (R5).', [top + 'Data set',*[r'$N/N_{\mathrm{rel}}$',r'AARD (\%)']*4],rows,[.26,.075,.085,.075,.085,.075,.085,.075,.085],
      notes='$N/N_{\\mathrm{rel}}$: calculated observations / observations with a defined relative deviation; ---: no observations. The binary sets use no reaction and are omitted.')
SPECIES = {'diethanolamine': 'DEA', 'protonated-diethanolamine': r'DEAH$^+$', 'methyldiethanolamine': 'MDEA', 'protonated-methyldiethanolamine': r'MDEAH$^+$', 'aminomethylpropanol': 'AMP', 'protonated-aminomethylpropanol': r'AMPH$^+$', 'bicarbonate-anion': r'HCO$_3^-$', 'carbonate-anion': r'CO$_3^{2-}$', 'hydronium-cation': r'H$_3$O$^+$', 'hydroxide-anion': r'OH$^-$', 'carbon-dioxide': r'CO$_2$', 'water': r'H$_2$O'}
QUANTITY = {'dispersion_energy_over_k': r'dispersion energy $u/k_B$', 'segment_count': 'segment count', 'segment_diameter': r'segment diameter $\sigma$', 'solvation_factor': 'solvation factor', 'dielectric_volume': r'permittivity coefficient $d_V$', 'dielectric_temperature': r'permittivity coefficient $d_T$', 'charge_number': 'charge number', 'molar_mass': 'molar mass', 'born_diameter': r'Born diameter $d^{\mathrm{Born}}$', 'debye_huckel_diameter': r'Debye--H\"uckel diameter', 'packing_diameter': 'packing diameter', 'charged_molecule_ion': 'charged-chain self-dispersion retained (1 = yes)', 'k_ij': r'$k_{ij}$', 'k_ij_reciprocal_temperature_slope': r'reciprocal-temperature slope of $k_{ij}$', 'k_ij_temperature_slope': r'temperature slope of $k_{ij}$'}
FITTED = dict(zip([r['parameter'] for r in params[:4]], fitted_names))
DEA_PAIR_KEYS = {'protonated-diethanolamine/water/k_ij', 'carbamate-anion/water/k_ij'}

def quantity(key):
    """Return the table group and the row label of one parameter key."""
    parts = key.split('/')
    if key in FITTED: return 'Fitted parameters', FITTED[key]
    if parts[0] == 'association':
        if parts[-1] == 'multiplicity': return 'Association', f'{SPECIES[parts[1]]}, number of association sites of type {parts[2].upper()}'
        return 'Association', f'{SPECIES[parts[1]]}, site {parts[2].upper()}--site {parts[4].upper()} ' + {'energy_over_k': r'association energy $\epsilon^{AB}/k_B$', 'volume': r'association volume $\kappa^{AB}$'}[parts[-1]]
    if parts[0].endswith(('hydrolysis', 'dissociation')): return 'Equilibrium-constant correlations', (f'R4, ${parts[1].upper()}_4$' if parts[0].endswith('hydrolysis') else f'R5, ${parts[1]}$')
    return ('Binary dispersion interactions' if len(parts) == 3 else 'Species parameters'), '--'.join(SPECIES[s] for s in parts[:-1]) + ', ' + QUANTITY[parts[-1]]

units = {'K^2': r'K$^2$', '1/K^2': r'K$^{-2}$', '1/K': r'K$^{-1}$', '1 / kelvin': r'K$^{-1}$', 'kelvin': 'K', 'angstrom': r'\AA', 'liter / mole': 'L/mol', 'kilogram / mole': 'kg/mol', 'dimensionless': '1', 'elementary-charge': '$e$'}
# Manuscript figures use retained observations and endpoint predictions.
def loading(row):
    if 'alpha_mol_CO2_per_mol_DEA' in row: return float(row['alpha_mol_CO2_per_mol_DEA'])
    if 'alpha_mol_CO2_per_mol_amine' in row: return float(row['alpha_mol_CO2_per_mol_amine'])
    fraction = float(row['DEA_mass_fraction'])
    water = (1-fraction)/0.01801528/(fraction/0.105137)
    x = float(row['x_CO2'])
    return x/(1-x)*(1+water)
def figure(fig,name):
    buffer = BytesIO()
    fig.savefig(buffer, format='pdf', metadata={'CreationDate': None, 'ModDate': None})
    outputs[LATEX/'figures/generated'/name] = buffer.getvalue()
    plt.close(fig)
plt.rcParams.update({'font.family': 'STIXGeneral', 'mathtext.fontset': 'stix', 'pdf.fonttype': 42,
                     'font.size': 8, 'legend.fontsize': 8, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
                     'axes.labelsize': 9, 'axes.titlesize': 9})
colors = ['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9']
DEA_PANELS = [('Lawson','Lawson-394K'),('SeoHong',),('Lal',),('Carson',)]
def dea_points(ax, rows, heat=False):
    for role in dict.fromkeys(r['role'] for r in rows):
        obs = [r for r in rows if r['role'] == role]
        ax.scatter([loading(r['row']) for r in obs], [r['observed']/1000 for r in obs],
                   s=16, edgecolors=colors[0], facecolors=colors[0] if role == 'fitted' else 'none',
                   label='Measured, ' + role)
    available = [r for r in rows if r['status'] == 'Available']
    ax.scatter([loading(r['row']) for r in available], [r['value']/1000 for r in available],
               s=16, marker='x', color=colors[1], label='Calculated')
    ax.set(xlabel='Loading (mol CO$_2$/mol DEA)',
           ylabel='Integral heat (kJ/mol CO$_2$)' if heat else 'CO$_2$ partial pressure (kPa)',
           yscale='linear' if heat else 'log')
    ax.legend()


dea_curves = dassessment['curves']
temperatures = sorted({q['T_K'] for q in dea_curves})
markers = dict(zip(temperatures, ['o', 's', '^', 'D', 'v', 'P', 'X', '*', 'p', 'h'], strict=True))


def dea_isotherms(ax, groups):
    rows = [q for q in dea_curves if q['group'] in groups]
    for i, key in enumerate(dict.fromkeys(q['curve'] for q in rows)):
        line = [q for q in rows if q['curve']==key]
        T = line[0]['T_K']
        obs = [q for q in data if q['group'] in groups and q['T_K']==T]
        assert obs and all(q['T_K']==T for q in line)
        assert all(a['loading'] < b['loading'] for a, b in zip(line, line[1:]))
        color, marker = colors[i], markers[T]
        ranges = line[0]['outside_ranges']
        style = '--' if ranges['DEA-dissociation'] is True else ':' if ranges['carbamate-hydrolysis'] is True else '-'
        values = [q['value']/1000 if q['status']=='Available' and q['requested_tolerance_met']
                  else math.nan for q in line]
        filled = all(q['role']=='fitted' for q in obs)
        ax.plot([q['loading'] for q in line], values, color=color, ls=style)
        ax.plot([], [], color=color, ls=style, marker=marker, markersize=4.5,
                markerfacecolor=color if filled else 'none', label=f'{T:.2f} K')
        ax.scatter([loading(q['row']) for q in obs], [q['observed']/1000 for q in obs],
                   s=25, marker=marker, edgecolors=color, facecolors=color if filled else 'none')
    ax.set(xlabel='Loading (mol CO$_2$/mol DEA)', ylabel='CO$_2$ partial pressure (kPa)', yscale='log')
    ax.legend(ncol=2, columnspacing=.7, handlelength=1.8, handletextpad=.4)


fig, axes = plt.subplots(2, 2, figsize=(6.48, 5.8), constrained_layout=True)
for ax, groups_in_panel, letter in zip(axes.flat, DEA_PANELS, 'abcd', strict=True):
    if groups_in_panel == ('Carson',):
        dea_points(ax, [r for r in data if r['group']=='Carson'], True)
    else:
        dea_isotherms(ax, groups_in_panel)
    ax.set_title(f'({letter}) ' + name(groups_in_panel[0]), loc='left')
figure(fig, 'dea-current-measured-model.pdf')
fig, axes = plt.subplots(1, 3, figsize=(6.48, 2.6), sharey=True, constrained_layout=True)
for ax, fraction in zip(axes, ('0.10', '0.20', '0.30'), strict=True):
    dea_points(ax, [r for r in data if r['group'] == 'Carson' and r['row']['DEA_mass_fraction'] == fraction], True)
    ax.set_title(f'{100*float(fraction):g} wt%')
    if ax is not axes[0]:
        ax.set_ylabel('')
figure(fig, 'dea-integral-heat-concentrations.pdf')
fig,axes=plt.subplots(1,2,figsize=(6.48,3.0),constrained_layout=True)
for ax,group,scale,letter in [(axes[0],'Horstmann',1,'a'),(axes[1],'Cai',0.001,'b')]:
    ps=[r for r in data if r['group']==group and r['status']=='Available']
    ax.scatter([float(r['row']['x_water']) for r in ps],[r['observed']*scale for r in ps],facecolors='none',edgecolors=colors[0],label='Measured')
    ax.scatter([float(r['row']['x_water']) for r in ps],[r['value']*scale for r in ps],marker='x',color=colors[1],label='DEA model')
    ax.set_title(f'({letter})', loc='left'); ax.set(xlabel='Water mole fraction',ylabel='Excess enthalpy (J/mol mixture)' if group=='Horstmann' else 'Bubble pressure (kPa)')
    ax.legend(fontsize=8, loc='center' if group=='Horstmann' else 'upper right')
figure(fig,'dea-current-binary-comparisons.pdf')
# MDEA and AMP: the same displays, built from each amine's retained files.
MD = 'analyses/mdea_mea_workflow/results/bounded-binary-411/'  # the reported MDEA fit: k(MDEA-water) at 423 K bounded at the CO2-free gap onset
MDEA = MD.replace('bounded-binary-411', 'salt-anchored-435/campaign')
critical = read(MD + 'critical-k.json')
comparison = read(MD + 'comparison.json')['k_versus_critical']
assert critical['pressure_Pa'] == 1466000 and len(comparison) == len(critical['rows'])
assert all(c['T_K'] == r['T_K'] and c['k_no_gap'] == r['k_no_gap'] for c, r in zip(comparison, critical['rows']))
fig, ax = plt.subplots(figsize=(3.2, 2.7), constrained_layout=True)
def mdea_water(point):
    law, = [c['temperature_law'] for pair in point['parameters']['pairs']
        if {pair['component_id_a'], pair['component_id_b']} == {'water', 'methyldiethanolamine'}
        for c in pair['coefficients']]
    assert law['reference_temperature']['magnitude'] == 423.0
    assert [t['power'] for t in law['terms']] == [0, 1]
    return [t['coefficient']['value']['magnitude'] for t in law['terms']]


temperatures = [r['T_K'] for r in comparison]
for point, label, color, style in [(mdoc, 'Pressure-weighted fit', colors[0], '-'),
                                   (read(MDEA + 'selection.json.gz')['point'], 'Original weights', colors[2], '--')]:
    k0, slope = mdea_water(point)
    ax.plot(temperatures, [k0 + slope * (T - 423.0) for T in temperatures], color=color, ls=style, label=label)
ax.scatter([r['T_K'] for r in critical['rows']], [r['k_gap'] for r in critical['rows']], s=12, marker='o', facecolors='none', edgecolors=colors[1], label='Calculated gap onset')
ax.set(xlabel='Temperature (K)', ylabel=r'$k_{\mathrm{MDEA,w}}$')
ax.legend()
figure(fig, 'mdea-gap-onset.pdf')
MD343 = 'analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/'  # measured-point locations of the MDEA pressure figure
AM = 'analyses/amp_transfer/results/retransfer-412-f2-05e94210/'  # #412: F2 carbamate inputs
AMM = AM + 'slope-150/'  # the reported AMP model: AMPH+-water reciprocal-temperature slope fixed at a value chosen from a scan
AMP = AM.replace('retransfer-412-f2-05e94210', 'salt-anchored-435/free')
AMP_FIXED = AMP.replace('/free/', '/fixed/')
f2 = MEAEVIDENCE
mea_pressure = read(f2 + 'canonical-pressure.csv')
mea_replay = fixed.load('E/MEA/replay.json.gz')
mea_off = fixed.load('MEA/off-window.json.gz')['rows']
eprops = {r['identity']: r for r in [*mea_replay['rows'], *mea_replay['hot_wagner'], *mea_off]}
fitted_pressure = {r['id'] for r in read(f2 + 'fitted-rows.csv') if r['quantity'] == 'PartialPressure'}
pressure = {'MEA': [(float(r['loading']), math.log(eprops[r['target']]['value']/float(r['observed'])), 'fitted' if r['target'] in fitted_pressure else 'not fitted', float(r['temperature_K'])) for r in mea_pressure]}
pressure['DEA'] = [(loading(r['row']), math.log(r['value']/r['observed']), r['role'], r['T_K']) for r in data if r['group'] in ('Lawson', 'Lawson-394K', 'SeoHong', 'Lal', 'Lawson-VIII') and r['status'] == 'Available']
mrows = fixed.endpoint_record('MDEA/properties.json.gz', 'MDEA')['rows']
def mdea_loading(r):
    q = r['row']
    if r['group'] == 'corrected-Kamps': return float(q['m_CO2_mol_kg_water']) / float(q['m_MDEA_mol_kg_water'])
    if r['group'] == 'Sedighi': return float(q['alpha_mol_CO2_per_mol_MDEA'])
    return float(q['m_CO2_mol_per_kg_H2O']) / float(q['m_MDEA_mol_per_kg_H2O'])
pressure['MDEA'] = [(mdea_loading(r), math.log(r['value']/r['observed']), r['role'], r['T_K']) for r in mrows if r['group'] in ('Kuranov', 'Kuranov-413K', 'corrected-Kamps', 'Sedighi') and r['status'] == 'Available']
arows = aassessment['rows']
pressure['AMP'] = [(float(r['row']['alpha_mol_CO2_per_mol_AMP']), math.log(r['value']/r['observed']), r['role'], r['T_K']) for r in arows if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'tong') and r['status'] == 'Available']
assert {k: collections.Counter(r for _, _, r, _ in v) for k, v in pressure.items()} == {
    'MEA': {'fitted': 47, 'not fitted': 112}, 'DEA': {'fitted': 90, 'not fitted': 7, 'comparison only': 10},
    'MDEA': {'fitted': 66, 'not fitted': 54}, 'AMP': {'fitted': 105}}, {k: collections.Counter(r for _, _, r, _ in v) for k, v in pressure.items()}
fig, axes = plt.subplots(2, 2, figsize=(6.48, 5.8), constrained_layout=True)
tnorm = matplotlib.colors.Normalize(min(t for v in pressure.values() for *_, t in v), max(t for v in pressure.values() for *_, t in v))
tmap = matplotlib.colormaps['viridis']
for ax, (amine, points) in zip(axes.flat, pressure.items()):
    for role, marker, filled in [('fitted', 'o', True), ('not fitted', 'o', False), ('comparison only', '^', False)]:
        rows = [(x, y, t) for x, y, label, t in points if label == role]
        if rows:
            shade = [tmap(tnorm(t)) for _, _, t in rows]
            ax.scatter([x for x, _, _ in rows], [y for _, y, _ in rows], s=17, marker=marker, edgecolors=shade, facecolors=shade if filled else 'none', linewidths=.8)
            ax.scatter([], [], s=17, marker=marker, edgecolors='0.3', facecolors='0.3' if filled else 'none', label=role.capitalize())
    ax.axhline(0, color='0.5', linewidth=.7)
    ax.set_title(amine + (' — CO$_2$ partial pressure' if amine in ('MEA', 'DEA') else ' — total pressure'))
    ax.set(xlabel='Loading (mol CO$_2$/mol amine)', ylabel=r'$\ln(p^{\mathrm{calc}}/p^{\mathrm{obs}})$')
    ax.legend()
fig.colorbar(matplotlib.cm.ScalarMappable(norm=tnorm, cmap=tmap), ax=axes, label='Temperature (K)', shrink=.6)
figure(fig, 'loaded-pressure-residuals.pdf')
compare_mea = fixed.endpoint_record('display-replays/mea-comparisons.json.gz', 'MEA')
caloric = fixed.endpoint_record('display-replays/caloric-and-species.json.gz', 'MEA')
carbonate = read(f2 + 'carbonate-share.csv')
share = {row['state']: row for row in compare_mea['carbonate_share']}
assert len(share) == len(carbonate) == 10
old_ratios = [float(row['calc_over_obs']) for row in carbonate]
for row in carbonate:
    new = share[row['id']]
    assert math.isclose(float(row['observed_share']), new['observed'], rel_tol=1e-12)
    row.update(predicted_share=new['value'], calc_over_obs=new['value']/new['observed'])
assert len(carbonate) == 10
fig, ax = plt.subplots(figsize=(3.2, 2.7), constrained_layout=True)
cobs, ccalc = [float(r['observed_share']) for r in carbonate], [float(r['predicted_share']) for r in carbonate]
assert min(cobs + ccalc) > 0
span11 = [min(cobs + ccalc) / 1.5, max(cobs + ccalc) * 1.5]
ax.plot(span11, span11, color='0.4', lw=.8, ls='--', label='1:1')
ax.scatter(cobs, ccalc, s=24, facecolors='none', edgecolors=colors[0], label='Not fitted')
ax.set(xscale='log', yscale='log', xlim=span11, ylim=span11, xlabel='Measured carbonate share', ylabel='Calculated carbonate share')
ax.set_aspect('equal')
ax.legend()
figure(fig, 'jakobsen-carbonate-share.pdf')
AMF = AM + 'main/'  # the comparison fit with that slope also fitted, which has the splits
ASLOPE = 'protonated-aminomethylpropanol/water/k_ij_reciprocal_temperature_slope'
AM344 = 'analyses/amp_transfer/results/retransfer-344-05e94210/'  # the pure-AMP prefit, which the refit keeps
PCO2, PTOT, PBUB, HEAT, XFRAC = r'$p_{\COtwo}$', 'total pressure', 'bubble pressure', 'integral heat', 'mole fraction'
KURANOV, MERKLEY, NMR = 'kuranovSolubilitySingleGases1996', 'merkleyEnthalpiesAbsorptionCarbon1987', 'bottingerOnlineNMRSpectroscopic2008'
MSETS = {
    'Kuranov': ('Kuranov et al.', KURANOV, PTOT), 'Kuranov-binary': (r'Kuranov et al., \COtwo-free', KURANOV, PBUB),
    'Jakobsen': ('Jakobsen et al.', 'Jakobsen2005', 'species ratios'), 'Carson': ('Carson et al.', 'carsonEnthalpySolutionCarbon2000', HEAT),
    'Merkley': ('Merkley et al.', MERKLEY, HEAT), 'Cp': ('Weiland et al.', 'weilandHeatCapacityAqueous1997', 'heat capacity'),
    'loaded-density': ('Weiland et al.', 'Weiland1998', 'density'), 'unloaded-density': ('Sobrino et al.', 'sobrinoViscosityDensityMeasurements2016', 'density'),
    'Kim': ('Kim et al.', 'kimEbulliometricDeterminationVaporLiquid2008', PBUB), 'Ermatchkov': ('Ermatchkov et al.', 'ermatchkovSolubilityCarbonDioxide2006', PCO2),
    'corrected-Kamps': (r'P\'erez-Salado Kamps et al., corrected temperatures', 'ermatchkovSolubilityCarbonDioxide2006', PTOT),
    'Bottinger-amine-sum-5bar': (r'B\"ottinger et al., MDEA + MDEAH$^+$, 0.5 MPa', NMR, XFRAC), 'Bottinger-bicarbonate-5bar': (r'B\"ottinger et al., bicarbonate + carbonate, 0.5 MPa', NMR, XFRAC),
    'Bottinger-amine-sum-25bar': (r'B\"ottinger et al., MDEA + MDEAH$^+$, 2.5 MPa', NMR, XFRAC), 'Bottinger-bicarbonate-25bar': (r'B\"ottinger et al., bicarbonate + carbonate, 2.5 MPa', NMR, XFRAC),
    'Merkley-half-loading': ('Merkley et al., half the read loading', MERKLEY, HEAT), 'Merkley-outside': ('Merkley et al., remaining states', MERKLEY, HEAT),
    'Cp-60wt': (r'Weiland et al., 60 wt\%', 'weilandHeatCapacityAqueous1997', 'heat capacity'), 'density-60wt': (r'Weiland et al., 60 wt\%', 'Weiland1998', 'density'),
    'Kuranov-413K': ('Kuranov et al., 413 K', KURANOV, PTOT), 'Zheng': ('Zheng et al.', 'zhengCO2HeatAbsorption2020', HEAT),
    'Sedighi': ('Sedighi et al.', 'sedighiExperimentalMeasurementThermodynamic2024', PTOT), 'Xiao': ('Xiao et al.', 'xiaoCO2AbsorptionAqueous2018a', PCO2),
}
HARTONO = 'hartonoNewSolubilityHeat2021'
ASETS = {
    'loaded-pressure': ('Hartono et al. (2021), 313--353 K', HARTONO, PTOT), 'binary': ('Hartono et al. (2013)', 'hartonoBinaryTernaryVLE2013', PBUB),
    'binary-y': ('Hartono et al. (2013)', 'hartonoBinaryTernaryVLE2013', 'vapor AMP mole fraction'), 'nmr': ('Ciftja et al.', 'ciftjaExperimentalStudyCarbamate2014a', 'carbamate fraction'),
    'hartono-2021-supplemental': ('Hartono et al. (2021), 373--393 K', HARTONO, PTOT), 'kundu': ('Kundu et al.', 'kunduVaporLiquidEquilibriumCO22003', PCO2),
    'tong-baseline': (r'Tong et al., \COtwo-free', 'Tong2012', PBUB), 'tong': ('Tong et al.', 'Tong2012', PTOT),
}
sig = lambda v: f'${float(f"{v:.3g}"):g}$'
pair = lambda s: f"{s['rows']}/{s['relative_rows']}"

def mark(rs, laws):
    out = []
    for law in laws:
        flags = {r['outside_ranges'][law] for r in rs}
        out.append('mixed' if {True, False} <= flags else 'out' if True in flags else 'in' if False in flags else '---')
    return out

def mdea_basis(rs):
    """MDEA content and loading ranges on the basis the source rows give."""
    def col(*keys, scale=1):
        return [scale*float(r['row'][k]) for r in rs for k in keys if r['row'].get(k) not in (None, '')]
    wt = col('MDEA_mass_percent', 'MDEA_wt_percent') or col('MDEA_mass_fraction', 'unloaded_MDEA_mass_fraction', 'initial_MDEA_mass_fraction', 'mass_fraction', scale=100)
    if rs[0]['group'] == 'Jakobsen': wt = [23.0]  # Jakobsen et al., Table A5: all 8 NMR states are at 23 wt% MDEA
    molal, x = col('m_MDEA_mol_per_kg_H2O', 'm_MDEA_mol_kg_water'), col('liquid_x_MDEA')
    amount = span(wt, sig) + r' wt\%' if wt else span(molal, sig) + ' mol/kg' if molal else r'$x_{\mathrm{A}}=\,$' + span(x, sig) if x else '---'
    alpha = col('loading', 'alpha_exp', 'alpha_mol_CO2_per_mol_MDEA', 'loadNMR', 'alpha_sat_mol_CO2_per_mol_MDEA')
    alpha = alpha or [float(r['row'][k])/float(r['row'][k.replace('CO2', 'MDEA')]) for r in rs for k in ('m_CO2_mol_per_kg_H2O', 'm_CO2_mol_kg_water') if k in r['row']]
    return amount, span(alpha, sig) if alpha else span(col('x_CO2'), sig) + r'\textsuperscript{a}' if col('x_CO2') else '---'

def amine(tag, label, sets, rows, stats, laws, basis):
    """Rows of one amine for the data table, and its range table, from its retained rows and statistics."""
    groups, out, range_rows = {}, [head(label, 11)], []
    for r in rows: groups.setdefault(r['key'], []).append(r)
    for key, rs in groups.items():
        title, source, quantity = sets[key]
        m, all_rows = mark(rs, laws), stats[key]['R1']
        s = all_rows.get('False') or all_rows['reaction not used']
        assert s['rows'] == sum(r['status'] == 'Available' for r in rs), key
        out.append([title + r' \cite{' + source + '}', quantity, rs[0]['role'], count(len(rs), s['relative_rows']), span([r['T_K'] for r in rs], lambda v: num(v,2)), *basis(rs), *['---']*(2-len(m)), *m, num(s['AARD_percent'],2), num(s['bias_percent'],2)])
        cells = []
        for law in laws:
            for side in ('False', 'True'):
                q = stats[key].get(law, {}).get(side)
                cells += [pair(q), num(q['AARD_percent'],2)] if q else ['---', '---']
        if set(cells) != {'---'}: range_rows.append([title + ', ' + quantity, *cells])
    top = ' & ' + ' & '.join(r'\multicolumn{2}{@{}l}{' + code + ', ' + side + '}' for code in laws.values() for side in ['inside','outside']) + r' \\ '
    table('supplement-' + tag + '-ranges', f'Deviations of the {label} model from the {label} data inside and outside the ' + ('source' if tag == 'amp' else 'measured') + ' temperature ranges of the equilibrium constants.', [top + 'Data set', *[r'$N/N_{\mathrm{rel}}$', r'AARD (\%)']*2*len(laws)], range_rows, [round(.92-.16*2*len(laws),2)] + [.07,.09]*2*len(laws),
          notes=r'$N/N_{\mathrm{rel}}$: calculated observations / observations with a defined relative deviation; ---: no observations. Sets that use no reaction are omitted.')
    return out

def flatten(document, own):
    """Values of the species in own from a retained parameter file, as {key: (value, unit)} with the keys of the DEA parameter list."""
    P, out = document['parameters'], {}
    for c in P['components']:
        if c['component_id'] in own:
            out |= {c['component_id'] + '/' + q['family']: q['value'] for q in c['coefficients']} | {c['component_id'] + '/' + k: v['value'] for k, v in c['fixed'].items()}
    for e in P['topology']['edges']:
        a, b = e['endpoint_a'], e['endpoint_b']
        if a['component_id'] in own and 'energy_over_k' in e:  # edges without a value follow the combining rule
            out |= {f"association/{a['component_id']}/{a['site_id']}/{b['component_id']}/{b['site_id']}/{k}": e[k]['value'] for k in ('energy_over_k', 'volume')}
    out |= {f"association/{q['component_id']}/{q['site_id']}/multiplicity": {'magnitude': q['multiplicity'], 'unit': 'dimensionless'} for q in P['topology']['sites'] if q['component_id'] in own}
    for pair in P['pairs']:
        ids = sorted([pair['component_id_a'], pair['component_id_b']])
        for q in pair['coefficients'] if set(ids) & own else []:
            terms = [(q['family'], q)] if 'value' in q else [('k_ij' + '_temperature_slope'*t['power'], t['coefficient']) for t in q['temperature_law']['terms']]
            out |= {'/'.join(ids + [k]): v['value'] for k, v in terms}
    for r in document['reactions']['aqueous']:
        if r['name'].endswith(('hydrolysis', 'dissociation')):
            assert r['correlation']['reference_temperature'] == 313.15 and r['correlation']['standard_state_id'] == 'aqueous-molality-infinite-dilution-water-v1', r['name']
            out |= {r['name'] + '/' + k: {'magnitude': r['correlation'].get(k, 0), 'unit': u} for k, u in zip('abcdef', ['dimensionless', 'K', 'dimensionless', '1/K', 'K^2', '1/K^2'])}
    return {k: (v['magnitude'], v['unit']) for k, v in out.items()}

def species_row(record, s, label, source, fitted):
    """One species in the column layout of the MEA species table; the keys in fitted are set in bold."""
    def get(key):  # a fitted segment diameter, and the Born diameter tied to it, keeps five significant figures
        if key not in record: return '--'
        text = f'{record[key][0]:.4f}' if key.endswith('_diameter') and s + '/segment_diameter' in fitted else repr(round(record[key][0], 4)).removesuffix('.0')
        return (bold if key in fitted else str)('$' + text + '$')
    return [label, *[get(s + '/' + k) for k in ('segment_count', 'segment_diameter', 'dispersion_energy_over_k')], get(f'association/{s}/a/{s}/b/energy_over_k'), get(f'association/{s}/a/{s}/b/volume'), get(s + '/born_diameter'), source]

def bounds(low, high, digits, scale=1):
    return '[' + num(scale*low, digits) + ', ' + num(scale*high, digits) + ']'

mstats = {}
for group in dict.fromkeys(r['group'] for r in mrows):
    cohort = [r for r in mrows if r['group'] == group]
    subsets = collections.defaultdict(list)
    for r in cohort:
        r['key'] = group
        subsets[str(r['outside_ranges']['MDEA-dissociation'])].append(r)
    mstats[group] = {'R1': {'False': deviations(cohort)}, 'MDEA-dissociation': {
        flag: deviations(rs) for flag, rs in subsets.items() if flag != 'None'}}

data_rows += amine('mdea', 'MDEA', MSETS, mrows, mstats, {'MDEA-dissociation': 'R5'}, mdea_basis)
MFIT = [(r'$k_{\mathrm{MDEA,w}}$ at 423 K',1,4), (r'$10^{3}\,\mathrm{d}k_{\mathrm{MDEA,w}}/\mathrm{d}T$ (K$^{-1}$)',1e3,4), (r'$k_{\mathrm{MDEAH^+,CO_2}}$',1,4), (r'$k_{\mathrm{MDEAH^+,w}}$ at 313.15 K',1,4),
        (r'$b_{\mathrm{MDEAH^+,w}}$ (K)',1,3), (r'$k_{\mathrm{MDEAH^+,HCO_3^-}}$',1,4), (r'$\sigma_{\mathrm{MDEAH^+}}$ (\AA)',1,4), (r'$u_{\mathrm{MDEAH^+}}/k_B$ (K)',1,3)]
mfit = list(coordinates(fixed.conditional('MDEA')).values())
fit_rows += [head('MDEA', 5)] + [[name, bold(num(scale*r['value'], digits) + (r'\textsuperscript{a}' if r['on_bound'] else '')),
                                  num(scale*r['error'] if r['error'] is not None else None, digits), bounds(*r['bounds'], digits, scale), '']
                                 for (name, scale, digits), r in zip(MFIT, mfit, strict=True)]

afeed = {r['identity']: r for r in read('analyses/amp_transfer/inputs/retransfer-344/observation-rows.csv')}
akey = lambda e: e['group'] + ('-y' if e['group'] == 'binary' and e['unit'] != 'Pa' else '')
for r in arows: r['key'] = akey(r)
amass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in adoc['parameters']['components']}
def amp_basis(rs):
    feed = [afeed[r['identity']] for r in rs]
    if 'x_AMP' in rs[0]['row']: return r'$x_{\mathrm{A}}=\,$' + span([float(r['row']['x_AMP']) for r in rs], sig), '---'
    wt = [100*amass['aminomethylpropanol']/(amass['aminomethylpropanol'] + amass['water']*float(f['water'])) for f in feed]
    return span(wt, sig) + r' wt\%', span([float(f['alpha']) for f in feed], sig)
afree = read(AMF + 'fit-summary.json')
aunc = fixed.conditional('AMP_free')
aorder = ['AMP-water-k', 'AMP-water-slope', 'AMPH-water-k', 'AMPH-water-slope', 'AMPH-CO2-k',
          'AMPH-segment-diameter', 'AMPCOO-segment-diameter', 'AMP-hydrolysis-a', 'AMP-hydrolysis-enthalpy-increment']
astats = {}
for key in dict.fromkeys(map(akey, arows)):
    cohort = [r for r in arows if akey(r) == key]
    astats[key] = {'R1': {'False': deviations(cohort)}}
    for law in ('carbamate-hydrolysis', 'AMP-dissociation'):
        astats[key][law] = {str(side): stat for side in (False, True)
                            if (stat := deviations([r for r in cohort if r['outside_ranges'][law] is side]))['rows']}
data_rows += amine('amp', 'AMP', ASETS, arows, astats, {'carbamate-hydrolysis': 'R4', 'AMP-dissociation': 'R5'}, amp_basis)
AFIT = [(r'$k_{\mathrm{AMP,w}}$ at 313.15 K',4), (r'$b_{\mathrm{AMP,w}}$ (K)',3), (r'$k_{\mathrm{AMPH^+,w}}$ at 313.15 K',4), (r'$b_{\mathrm{AMPH^+,w}}$ (K)',3), (r'$k_{\mathrm{AMPH^+,CO_2}}$',4),
        (r'$\sigma_{\mathrm{AMPH^+}}$ (\AA)',4), (r'$\sigma_{\mathrm{AMPCOO^-}}$ (\AA)',4), (r'R4 constant term $A_4$',4), (r'R4 enthalpy increment $\delta h$ (J/mol)',1)]
r4 = {}
mea_stage = read(MEAFIT + 'objective-information.json.gz')['result']
for amine_name, document, coords, level_key, enthalpy_key in [
        ('dea', ddoc, dcoords, 'hydrolysis-a', 'hydrolysis-enthalpy-shift'),
        ('amp', adoc, acoords, 'AMP-hydrolysis-a', 'AMP-hydrolysis-enthalpy-increment')]:
    shift = read(f'analyses/{amine_name}_transfer/results/salt-anchored-435/hydrolysis/shift.json')
    final, = [r['correlation'] for r in document['reactions']['aqueous'] if r['name'] == 'carbamate-hydrolysis']
    start = shift['source_law']
    # Same starting correlation and reciprocal-temperature basis as the #435 shift record.
    level = final['a'] - start['a'] + (final['b'] - start['b']) / final['reference_temperature']
    hcoord = coords[enthalpy_key]
    delta_h = (final['b'] - start['b']) * -8.31446261815324
    r4[amine_name] = dict(delta_ln_K4=level, SE_ln_K4=coords[level_key]['error'], delta_h_J_mol=delta_h,
                          SE_h_J_mol=hcoord['error'], bounds=shift['bounds'])
    hcoord.update(value=delta_h, bounds=shift['bounds']['enthalpy'])
dflat = flatten(ddoc, {'diethanolamine', 'protonated-diethanolamine', 'carbamate-anion'})
dcoords['hydrolysis-a']['value'] = dflat['carbamate-hydrolysis/a'][0]
dflat.update({key: (r['value'], params[i]['unit']) for i, (key, r) in enumerate(dcoords.items())})
fit_rows[1:1] = [[label + (' (J/mol)' if i == 3 else ''), bold(num(r['value'], d)), num(r['error'], d),
                  bounds(*r['bounds'], d), ''] for i, (label, r) in enumerate(zip(fitted_names, dcoords.values(), strict=True))
                 for d in [0 if i == 3 else 3]]
fit_rows += [head('AMP', 5)] + [[label, bold(num(r['value'], d) + (r'\textsuperscript{a}' if r['on_bound'] else '')),
                                '---' if r['on_bound'] else num(r['error'], d), bounds(*r['bounds'], d), '']
                               for (label, d), key in zip(AFIT, aorder, strict=True) for r in [acoords[key]]]
level = lambda q: [r'R4 change at 313.15 K, $\Delta\ln K_4$\textsuperscript{c}', f"${q['delta_ln_K4']:+.3f}$", num(q['SE_ln_K4'], 3), bounds(*q['bounds']['level'], 3), '']
assert fit_rows[4][0].startswith('R4 enthalpy increment') and fit_rows[-1][0].startswith('R4 enthalpy increment')
fit_rows[4][1:4] = [bold(num(r4['dea']['delta_h_J_mol'], 0)), num(r4['dea']['SE_h_J_mol'], 0), bounds(*r4['dea']['bounds']['enthalpy'], 0)]
fit_rows[-1][1:4] = [bold(num(r4['amp']['delta_h_J_mol'], 0) + r'\textsuperscript{a}'),
                       '---', bounds(*r9_units['AMP_free']['physical_bounds_J_mol'], 0)]
fit_rows.insert(4, level(r4['dea']))
fit_rows.insert(len(fit_rows) - 1, level(r4['amp']))
# fit_rows: name, value, standard error, bounds and an unused fifth cell. The main text omits the bounds; the supplement lists them.
columns = lambda n, keep: [[r[0].replace('multicolumn{5}', 'multicolumn{' + str(n) + '}')] if len(r) == 1 else keep(r) for r in fit_rows]
# Table 7 gives the level change of R4 at 313.15 K in a footnote to the constant term; the supplement's bounds table keeps it as a row.
main_fit = [r for r in columns(3, lambda r: [r[0].replace('R4 constant term $A_4$', r'R4 constant term $A_4$\textsuperscript{b}'), r[1], r[2]]) if not r[0].startswith('R4 change')]
level_note = ' and '.join(f"${r4[k]['delta_ln_K4']:+.3f}\\pm{r4[k]['SE_ln_K4']:.3f}$ for {k.upper()}" for k in ('dea', 'amp'))
table('transfer-fitted', 'Fitted parameters of the DEA, MDEA and AMP models at a fixed 100 kPa reaction reference, with conditional standard errors.', ['Parameter','Value','Standard error'], main_fit, [.52,.20,.20],
      notes=r'Bold: fitted in this work. \textsuperscript{a}On a bound; no standard error is assigned. DEA and AMP: $\delta h$ is measured from the starting R4 correlation of Table~\ref{tab:reaction-equilibrium-constants}, and the final R4 coefficients include it (Table~\ref{supp-tab:supplement-transfer-parameters}). \textsuperscript{b}Expressed relative to the starting correlation, the fitted constant term changes $\ln K_4$ at \SI{313.15}{\kelvin} by ' + level_note + r', with the standard error of $A_4$; this change is not a further parameter. MDEA: $k_{\mathrm{MDEA,w}}$ is held at the upper bound that keeps the \COtwo-free MDEA--water solution free of a calculated liquid--liquid gap at \SI{1.466}{\mega\pascal} (Section~\ref{sec:methods-phase}), with the margin below the no-gap edge. MDEA standard errors use the pressure-weighted residual Jacobian and the residual variance of the 278 responsive observations, with the bound held fixed. AMP: $\sigma_{\mathrm{AMPCOO^-}}$ and $\delta h$ are at their lower bounds, and the other standard errors are conditional on both. The standard errors follow Eq.~\eqref{eq:conditional-covariance}. Table~\ref{supp-tab:supplement-transfer-bounds} gives the bounds.')
table('supplement-transfer-bounds', 'Bounds of the fitted parameters of the DEA, MDEA and AMP models.', ['Parameter','Lower bound','Upper bound'], columns(3, lambda r: [r[0].replace(r'\textsuperscript{c}', ''), *r[3][1:-1].split(', ')]), [.50,.20,.20],
      notes=r'The parameters are those of main-text Table~\ref{main-tab:transfer-fitted}. For DEA and AMP the bounds of $\delta h$ and of $\Delta\ln K_4$ are measured from the starting R4 correlations, like the values of that table.')
apure, ROLE = read(AM344 + 'pure-binary-on-05e94210.json')['pure'], {'fitted': 'fitted', 'assessment_not_fitted': 'not fitted'}
data_rows.append(head('AMP, pure component', 11))
for key, who in [('Klepacova2011', r"Klep\'a\v{c}ov\'a et al.\ \cite{klepacovaVaporPressuresSeveral2011}"), ('Belabbaci2010', r'Belabbaci et al.\ \cite{belabbaciInvestigationIsothermalVapour2010}'), ('Pappa2006', r'Pappa et al.\ \cite{pappaMeasurementThermodynamicModeling2006}'), ('Ayad2023', r'Ayad et al.\ \cite{ayadMeasurementsModelingThermodynamic2023}')]:
    g, t = apure['groups'][key], [r['T_K'] for r in apure['rows'] if r['campaign'] == key]
    assert g['n'] == len(t), key
    data_rows.append([who, g['metric'], ROLE[g['role']], str(g['n']), span(t, lambda v: num(v,2)), 'pure AMP', '---', '---', '---', *([num(g['AARD_percent'],2), num(g['signed_relative_bias_percent'],2)] if 'AARD_percent' in g else [r'---\textsuperscript{b}', '---'])])
comparison_scores = {}
for who, current, prior in [
        ('DEA', data, read(DEA + 'data-rows.json.gz')),
        ('MDEA', mrows, mprior['rows']),
        ('AMP', arows, read(AMP + 'data-rows.json.gz'))]:
    old = {(r['identity'], r['unit']): r for r in prior}
    matched = collections.defaultdict(list)
    for r in current:
        q = old.get((r['identity'], r['unit']))
        if q and r['status'] == q['status'] == 'Available' and r['observed'] != 0:
            assert r['observed'] == q['observed']
            group = akey(r) if who == 'AMP' else r['group']
            title, cite, _ = {'DEA': SETS, 'MDEA': MSETS, 'AMP': ASETS}[who][group]
            matched[title + r' \cite{' + cite + '}'].append((r, q))
    for key, pairs in matched.items():
        new, old = zip(*pairs, strict=True)
        comparison_scores[who, key] = (deviations(new), deviations(old))

transfer_rows = []
for row in data_rows:
    if len(row) == 1:
        who = re.search(r'textit\{([^}]*)\}', row[0])[1]
        transfer_rows.append([row[0].replace('multicolumn{11}', 'multicolumn{12}')])
    else:
        comparison = comparison_scores.get((who, row[0]))
        value = '---'
        if comparison:
            new, prior = comparison
            value = num(prior['AARD_percent'], 2)
            if new['relative_rows'] != int(str(row[3]).split()[0]):
                value = num(new['AARD_percent'], 2) + ' / ' + value + f" ({new['relative_rows']})"
        shown = [*row, value]
        shown[2] = shown[2].replace('comparison', r'com\-parison')
        transfer_rows.append(shown)
table('supplement-transfer-data', 'Data for DEA, MDEA and AMP with their roles in the fit of each model, their ranges, and the deviations of the DEA, MDEA and AMP models.', DATA_HEAD + ['AARD (\\%), original salt fit'], transfer_rows, [.15,.085,.08,.035,.08,.084,.086,.05,.05,.057,.07,.075], long=True, size=r'\footnotesize',
      notes=r'The last column gives the original salt-anchored fit on the same observations. Paired values are calculated on the common rows with defined relative errors (reported fit first and the paired count in parentheses). $N$: number of observations; in parentheses, the number with a calculated value and a defined relative deviation. Amine content: that of the unloaded solution, or a mole fraction for the \COtwo-free binary sets ($x_{\mathrm{w}}$: water; $x_{\mathrm{A}}$: amine). R4 and R5: in, out or mixed relative to the source temperature range of that equilibrium constant, which for the AMP R4 is a range of model-derived estimates (main-text Table~\ref{main-tab:reaction-equilibrium-constants} and Section~\ref{main-sec:data-roles}); ---: not reported in the source, or the calculation uses no such reaction. AARD and bias follow main-text Eq.~(\ref{main-eq:aard}). Tables~\ref{tab:supplement-dea-ranges}--\ref{tab:supplement-amp-ranges} give the deviations inside and outside each range, and Section~\ref{sec:s-corrections} gives the source conventions. \textsuperscript{a}Mole fraction of added \COtwo. DEA: the water--DEA interaction was fitted beforehand to the 365.15 K vapor--liquid equilibria of Horstmann et al.\ \cite{horstmannPhaseEquilibriumExcess2002}, which are not listed; the 90 fitted partial pressures include Lawson and Garst, Seo and Hong, and Lal et al. MDEA: the Xiao et al.\ and Ermatchkov et al.\ pressures were used to choose the initial MDEA parameter set but are not in the objective. Pure component: deviations at the fixed pure-AMP parameters, whose fit preceded the reactive fit; \textsuperscript{b}the errors of the three fitted densities are ' + ', '.join(num(e, 3) for e in apure['groups']['Ayad2023']['errors_kg_m3']) + r' kg/m$^3$.')
AMINES = [('DEA', dflat, 'diethanolamine'), ('MDEA', flatten(mdoc, {'methyldiethanolamine', 'protonated-methyldiethanolamine'}), 'methyldiethanolamine'), ('AMP', flatten(adoc, {'aminomethylpropanol', 'protonated-aminomethylpropanol', 'carbamate-anion'}), 'aminomethylpropanol')]
assert [record[f'association/{s}/a/multiplicity'][0] for _, record, s in AMINES] == [2, 2, 1], 'site counts stated in the species note'
# Values fitted in this work, by key of each retained record: the reactive fit of each amine (checked against its fit record) and the fits made beforehand:
# the permittivity coefficients (Hsieh et al.), the water--DEA interaction (Horstmann et al.) and the five pure-AMP parameters.
MKEYS = ['methyldiethanolamine/water/k_ij', 'methyldiethanolamine/water/k_ij_temperature_slope', 'carbon-dioxide/protonated-methyldiethanolamine/k_ij', 'protonated-methyldiethanolamine/water/k_ij',
         'protonated-methyldiethanolamine/water/k_ij_reciprocal_temperature_slope', 'bicarbonate-anion/protonated-methyldiethanolamine/k_ij', 'protonated-methyldiethanolamine/segment_diameter', 'protonated-methyldiethanolamine/dispersion_energy_over_k']
AKEYS = ['aminomethylpropanol/water/k_ij', 'aminomethylpropanol/water/k_ij_reciprocal_temperature_slope', 'protonated-aminomethylpropanol/water/k_ij', 'protonated-aminomethylpropanol/water/k_ij_reciprocal_temperature_slope',
         'carbon-dioxide/protonated-aminomethylpropanol/k_ij', 'protonated-aminomethylpropanol/segment_diameter', 'carbamate-anion/segment_diameter', 'carbamate-hydrolysis/a']
APURE = dict(zip(['aminomethylpropanol/segment_count', 'aminomethylpropanol/segment_diameter', 'aminomethylpropanol/dispersion_energy_over_k', 'association/aminomethylpropanol/a/aminomethylpropanol/b/energy_over_k', 'association/aminomethylpropanol/a/aminomethylpropanol/b/volume'], ['m', 'sigma', 'epsilon', 'eps_ab', 'kappa']))
assert [AMINES[1][1][k][0] for k in MKEYS] == [r['value'] for r in mfit], 'bold MDEA values are those of the fit record'
assert [AMINES[2][1][k][0] for k in AKEYS] == [acoords[key]['value'] for key in aorder[:8]], 'AMP values are those of the fit record'
assert all(AMINES[2][1][k][0] == apure['parameter_values'][v] for k, v in APURE.items()), 'bold pure-AMP values are those of the pure-component fit'
permittivity = lambda s: {s + '/dielectric_volume', s + '/dielectric_temperature'}
FITTED_HERE = [{r['parameter'] for r in params if r['fitted_or_fixed'] == 'fitted'} | DEA_PAIR_KEYS | permittivity('diethanolamine') | {'diethanolamine/water/k_ij'},
               set(MKEYS) | permittivity('methyldiethanolamine'),
               set(AKEYS) | {'carbamate-hydrolysis/b'} | set(APURE) | permittivity('aminomethylpropanol')]  # the fitted AMP enthalpy increment sets B_4; the reciprocal-temperature slope is fitted
SOURCE = [r'\cite{Nasrifar2010}', r'\cite{Nasrifar2010}\textsuperscript{a}', r'This work\textsuperscript{b}', r'\cite{Pahlavanzadeh2013,Uyan2015}\textsuperscript{c}', r'This work\textsuperscript{d}', r'This work\textsuperscript{e}', r'This work\textsuperscript{f}', r'This work\textsuperscript{g}']
# Stated origins of fixed ion inputs (supplement): the DEA and AMP carbamate values come from the MEA model (fit F2);
# its diameter scaled by the cube root of the DEA/MEA ratio of m*sigma^3 (neutral MEA: 3.0353, 3.0435 A); AMPH+ takes the AMP energy.
f2 = {}
shared_fit = read(SALT + 'shared-parameters.json')
f2.update({'component/carbamate-anion/segment_diameter': shared_fit['carbamate']['sigma'],
           'component/carbamate-anion/dispersion_energy_over_k': shared_fit['carbamate']['epsilon']})
f2.update({r['identity']: r['origin'] for r in fixed.fits['MEA']['endpoint']['coordinates']})
size_ratio = (dflat['diethanolamine/segment_count'][0] * dflat['diethanolamine/segment_diameter'][0] ** 3 / (3.0353 * 3.0435 ** 3)) ** (1 / 3)
assert abs(size_ratio * f2['component/carbamate-anion/segment_diameter'] - dflat['carbamate-anion/segment_diameter'][0]) < 1e-9
assert f2['component/carbamate-anion/dispersion_energy_over_k'] == dflat['carbamate-anion/dispersion_energy_over_k'][0]
assert AMINES[2][1]['protonated-aminomethylpropanol/dispersion_energy_over_k'] == AMINES[2][1]['aminomethylpropanol/dispersion_energy_over_k']
# Hydroxide Born diameter from the Born equation: hydration free energy -106.4 kcal/mol, water permittivity 78.37 at 298.15 K.
born_oh = 6.02214076e23 * 1.602176634e-19 ** 2 * (1 - 1 / 78.37) / (4 * math.pi * 8.8541878128e-12 * 106.4 * 4184) * 1e10
shared = {r['identity']: float(r['value']) for r in read(MEA + 'paper-evidence-341/shared-coefficients.csv') if r['identity'].endswith('born_diameter')}
assert abs(born_oh - shared['component/hydroxide-anion/born_diameter']) < 1e-6
# Sensitivity of the MEA fit to the two Born diameters set at 3.0 A (supplement): the tested diameters, the largest objective change and the largest shifts of fitted CO2 partial pressures.
born = read(MEA + 'born-diameter-sensitivity-405/summary.json')
assert sorted((c['ion'], c['diameter_A']) for c in born['cases'][1:]) == [(ion, d) for ion in ('bicarbonate-anion', 'carbonate-anion') for d in (2.5, 4.0)] and born['bicarbonate_interior']['diameter_A'] == 3.5
born_shift = lambda ion: max(abs(r['change_percent']) for c in born['cases'][1:] if c['ion'] == ion for r in c['largest_relative_changes'] if r['quantity'] == 'partial_pressure')
assert round(born_shift('bicarbonate-anion')) == 6 and born_shift('carbonate-anion') < 0.02
born_cost = f"at most {100 * max(abs(c['cost_change']) for c in [*born['cases'], born['bicarbonate_interior']]) / born['reference_cost']:.2f}"
origins = [born_cost, f"{dflat['carbamate-anion/dispersion_energy_over_k'][0]:.4f}", f"{f2['component/carbamate-anion/segment_diameter']:.4f}", f'{size_ratio:.4f}', f'{born_oh:.4f}', '$-106.4$ kcal/mol', '78.37']
ROWS = [(0, 'diethanolamine', r'\ce{DEA}'), (0, 'protonated-diethanolamine', r'\ce{DEAH+}'), (0, 'carbamate-anion', r'\ce{DEACOO-}'), (1, 'methyldiethanolamine', r'\ce{MDEA}'), (1, 'protonated-methyldiethanolamine', r'\ce{MDEAH+}'), (2, 'aminomethylpropanol', r'\ce{AMP}'), (2, 'protonated-aminomethylpropanol', r'\ce{AMPH+}'), (2, 'carbamate-anion', r'\ce{AMPCOO-}')]
table('transfer-species', 'Segment, association and Born parameters of the DEA, MDEA and AMP species.', ['Species', r'$m^{\mathrm{seg}}$', r'$\sigma$ (\AA)', r'$u/k_B$ (K)', r'$\epsilon^{AB}/k_B$ (K)', r'$\kappa^{AB}$', r'$d^{\mathrm{Born}}$ (\AA)', 'Ref.'], [species_row(AMINES[i][1], s, label, source, FITTED_HERE[i]) for (i, s, label), source in zip(ROWS, SOURCE)], [.12,.10,.10,.12,.13,.10,.12,.14],
      notes=r'The columns are those of Table~\ref{tab:species-parameters}. Bold: fitted in this work; in a row of this work, the values in normal weight are fixed; --: not used. \textsuperscript{a}DEA values, with zero self-association energy. \textsuperscript{b}Dispersion energy of \ce{MEACOO-} in the MEA model and its diameter scaled to DEA (Section~\ref{supp-sec:s-parameters}). \textsuperscript{c}Segment parameters of Ref.~\cite{Pahlavanzadeh2013} and association parameters of Ref.~\cite{Uyan2015}; association volume converted in this work. \textsuperscript{d}Segment count and association volume of MDEA; zero self-association energy. \textsuperscript{e}Fitted beforehand to pure-AMP data. \textsuperscript{f}Dispersion energy of AMP. \textsuperscript{g}Dispersion energy of \ce{MEACOO-} in the reported MEA model; diameter fitted with the donor diameter as its lower bound. Table~\ref{tab:transfer-fitted} gives the standard errors of the values fitted in the reactive fits, and Table~\ref{supp-tab:supplement-transfer-parameters} unrounded values and the remaining inputs.')
NEUTRAL = {'DEA': r'\cite{Nasrifar2010}', 'MDEA': r'\cite{Pahlavanzadeh2013}'}
R5_SOURCE = {'DEA': r'\cite{bowerAcidicDissociationConstant1962}', 'MDEA': r'\cite{perez-saladokampsDissociationConstantNMethyldiethanolamine1996}', 'AMP': r'\cite{hamborgDissociationConstantsThermodynamic2009}'}

def origin(who, record, neutral, key, fitted):
    """Short source of one amine-specific value; a stated tie is checked against the retained values."""
    parts = key.split('/')
    last, species = parts[-1], parts[1] if parts[0] == 'association' else parts[0]
    tie = lambda other: record[key][0] == record[other][0]
    if key in fitted: return 'Permittivity fit' if last.startswith('dielectric') else 'This work'
    if last == 'charge_number': return 'By definition'
    if last == 'molar_mass': return 'From the formula'
    if last == 'solvation_factor': return 'Set in this work'
    if last in ('born_diameter', 'debye_huckel_diameter') and tie(species + '/segment_diameter'): return r'Equal to $\sigma$'
    if last == 'packing_diameter' and math.isclose(record[key][0], 0.88 * record[species + '/segment_diameter'][0], rel_tol=1e-12): return r'$0.88\sigma$'
    if parts[0].endswith('dissociation'): return R5_SOURCE[who]
    if who == 'AMP' and key in ('carbamate-anion/dispersion_energy_over_k', 'carbamate-anion/water/k_ij'):
        donor_key = ('carbamate energy divided by k' if last == 'dispersion_energy_over_k'
                     else "selected parameter pair/carbamate-anion/water/k_ij")
        design = 'AMP_free' if last == 'dispersion_energy_over_k' else 'MEA'
        assert record[key][0] == fixed.value(f'{design} {donor_key}')
        return r'\ce{MEACOO-}, MEA model'
    if who == 'AMP' and key == ASLOPE: return 'Set in this work (scan)'
    if species == neutral:
        if who == 'AMP': return 'Set in this work'  # only the site numbers of AMP are not fitted
        if who == 'MDEA' and parts[0] == 'association': return (r'Converted from ' if last == 'volume' else '') + r'\cite{Uyan2015}'
        return NEUTRAL[who]
    if last == 'segment_count' and record[key][0] == 1: return 'Single sphere'
    if last == 'energy_over_k' and record[key][0] == 0: return 'Set in this work'
    if species.startswith('protonated') and tie(key.replace(species, neutral)): return who + ' value'
    if species == 'carbamate-anion' and who == 'DEA': return {'dispersion_energy_over_k': r'\ce{MEACOO-}, MEA model', 'segment_diameter': r'Scaled from \ce{MEACOO-}'}[last]
    raise AssertionError(('no stated source', who, key))

rows = []
for (who, record, neutral), fitted in zip(AMINES, FITTED_HERE):
    SPECIES['carbamate-anion'], heading = who + 'COO$^-$', None
    for key, (value, unit) in record.items():
        last = key.split('/')[-1]
        assert last != 'charged_molecule_ion' or value == 1, key
        if last == 'charged_molecule_ion' or value == 0 and (last in 'cdef' or last.startswith('k_ij')): continue  # stated in the note
        group, label = quantity(key)
        if group != heading:
            heading = group
            rows.append(head(who + ': ' + group.lower(), 4))
        rows.append([label, (bold if key in fitted else str)('$' + repr(float(value)).removesuffix('.0') + '$'), units.get(unit, unit), origin(who, record, neutral, key, fitted)])
# Table S5 gives the DEA increment on the starting-law basis of Table 7, like the AMP increment (the record stores the final correlation, increment 0).
ddh = next(i for i, r in enumerate(rows) if r[0] == r'R4 enthalpy increment $\delta h$')
rows[ddh][:2] = [r'R4, enthalpy increment $\delta h$, contained in $B_4$', bold(f"${r4['dea']['delta_h_J_mol']!r}$")]
adh = r4['amp']['delta_h_J_mol']
rows.append([r'R4, enthalpy increment $\delta h$, contained in $B_4$', bold(f'${adh}$'), 'J/mol', 'This work'])
table('supplement-transfer-parameters', 'Amine-specific parameter values of the DEA, MDEA and AMP models at full precision.', ['Parameter','Value','Unit','Source'], rows, [.45,.24,.07,.21], long=True,
      notes=r'Bold values were fitted in this work; Table~\ref{main-tab:transfer-fitted} of the main text gives the standard errors of the parameters of the reactive fits, and Table~\ref{tab:supplement-transfer-bounds} their bounds. For DEA, the R4 coefficients $A_4$ and $B_4$ are the final coefficients after the fit, not additional independent fitted parameters. For DEA and AMP, $\delta h$ is measured from the starting R4 correlation, as in main-text Table~\ref{main-tab:transfer-fitted}, and is contained in $B_4$. R4: carbamate hydrolysis; R5: amine dissociation; $\ln K=a+b/T+c\ln(T/T_{\mathrm{ref}})+dT$ with $T$ in K and $T_{\mathrm{ref}}=313.15$ K, on the common-molality reference basis; coefficients not listed are zero. For R4, where $c=d=0$, $a$ and $b$ are written $A_4$ and $B_4$: they are the coefficients of main-text Eq.~(\ref{main-eq:reaction-equilibrium-constant-temperature}) on that basis, with $\Delta_4=0$. Binary dispersion interactions not listed are zero; a $k_{ij}$ with a slope is the value at 313.15 K, except MDEA--water, at 423 K. Each of the chain cations DEAH$^+$ and MDEAH$^+$ keeps the dispersion between its own segments. ``DEA value\textquotedblright{} and ``MDEA value\textquotedblright{}: the value of the molecular amine. The data deposit gives the source and basis of each value.')
def pressure_points(filename, rows, panels, shape):
    fig, axes = plt.subplots(*shape, figsize=(6.48, 2.25 * shape[0]), constrained_layout=True)
    cmap = plt.colormaps['viridis']
    groups_shown = set().union(*(p[1] for p in panels))
    temperatures = [float(r['T_K']) for r in rows if r['group'] in groups_shown]
    norm = matplotlib.colors.Normalize(min(temperatures), max(temperatures))
    for ax, (title, groups, loading_of, observable) in zip(axes.flat, panels, strict=True):
        part = [r for r in rows if r['group'] in groups]
        assert part, title
        for role, filled in [('fitted', True), ('not fitted', False)]:
            observed = [r for r in part if r['role'] == role]
            if observed:
                shades = cmap(norm([float(r['T_K']) for r in observed]))
                ax.scatter([loading_of(r) for r in observed], [r['observed']/1000 for r in observed],
                           s=18, edgecolors=shades, facecolors=shades if filled else 'none',
                           label=f'Measured, {role}')
        available = [r for r in part if r['status'] == 'Available']
        ax.scatter([loading_of(r) for r in available], [r['value']/1000 for r in available],
                   s=14, marker='x', color=cmap(norm([float(r['T_K']) for r in available])),
                   label='Model')
        ax.set(title=title, xlabel='Loading (mol CO$_2$/mol amine)', ylabel=observable, yscale='log')
        labels = ax.get_legend_handles_labels()[1]
        handles = [matplotlib.lines.Line2D([], [], ls='none', color='0.2',
                   marker='x' if label == 'Model' else 'o', markersize=4,
                   markerfacecolor='none' if label == 'Measured, not fitted' else '0.2')
                   for label in labels]
        ax.legend(handles, labels, fontsize=7)
    fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=axes,
                 label='Temperature (K)', location='right', aspect=30)
    figure(fig, filename)

mmass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mdoc['parameters']['components']}
total_pressure = 'Total pressure (kPa)'
partial_pressure = 'CO$_2$ partial pressure (kPa)'
pressure_points('mdea-current-measured-model.pdf', mrows, [
    ('Kuranov, 413 K', {'Kuranov-413K'}, mdea_loading, total_pressure),
    ('Kamps, corrected', {'corrected-Kamps'}, mdea_loading, total_pressure),
    ('Sedighi', {'Sedighi'}, mdea_loading, total_pressure),
    ('Ermatchkov', {'Ermatchkov'}, mdea_loading, partial_pressure),
    ('Xiao', {'Xiao'}, lambda r: float(r['row']['alpha_exp']), partial_pressure),
    ('Kuranov, fitted', {'Kuranov'}, mdea_loading, total_pressure),
    ], (2, 3))
def amp_loading(r):
    return float(r['row']['alpha_mol_CO2_per_mol_AMP'])

pressure_points('amp-current-measured-model.pdf', arows, [
    ('Hartono, 313--353 K', {'loaded-pressure'}, amp_loading, total_pressure),
    ('Hartono, 373--393 K', {'hartono-2021-supplemental'}, amp_loading, total_pressure),
    ('Tong', {'tong'}, amp_loading, total_pressure),
    ('Kundu', {'kundu'}, amp_loading, partial_pressure),
    ], (2, 2))
# One summary row per model, from each amine's retained summary.
dsum, msum = read(BASE + 'paper-summary.json'), read(MD + 'summary-row.json')
mstability = read(MD + 'stability.json')
aconf, asearchrows = read(AMM + 'confirmation.json'), read(AMM + 'search-1.json.gz')
msearch, asearch = mstability['grid'], aconf['full_search']
# The free fit (selected start 1) is the comparison whose splits the paper names; its classification and search.
afreesearch, aclass = next(f for f in afree['fits'] if f['start'] == 1)['search']['grid'], read(AMF + 'phase-classification-1.json.gz')
cell = lambda s: num(s['AARD_percent'],2) + ' (' + str(s['rows']) + ')'
escore = {r['group']: (r['deviations'][1], r['n'][1]) for r in read(MEA + 'paper-evidence-341/same-data-comparison/part1-scores.json')}
efit = [r for r in read(MEA + 'reduced-refit/parameter-details.csv') if r['fit'] == 'F2']
mea_fit = read(MEAEVIDENCE + 'fitted-rows.csv')
dnew = fixed.coverage('DEA')
mnew = fixed.coverage('MDEA')
anew = fixed.coverage('AMP_free', 'native')
def pressure_stats(rows, pred='value'):
    deviations = [100 * (float(r[pred]) / float(r['observed']) - 1) for r in rows
                  if r.get('status', 'Available').lower() == 'available']
    return dict(AARD_percent=math.fsum(map(abs, deviations))/len(deviations), rows=len(deviations))

def search_summary(tally, splits):
    return [tally['states'], len(tally['unavailable']), splits]

def scores(rows, groups):
    return cell(pressure_stats([r for r in rows if r['group'] in groups]))
def pressure_columns(rows, groups, total, partial):
    fitted = [r for r in rows if r['unit'] == 'Pa' and r['role'] == 'fitted']
    return [scores(fitted, groups), cell(pressure_stats(fitted)),
            '$P$: ' + scores(rows, total) + r'; $p_{\COtwo}$: ' + scores(rows, partial)]

e47 = cell(pressure_stats([eprops[k] for k in fitted_pressure]))
wagner = mea_replay['hot_wagner'] + fixed.endpoint_record('display-replays/wagner.json.gz', 'MEA')['rows']
assert len(wagner) == 23
enot = ([eprops[r['target']] for r in mea_pressure if r['target'] not in fitted_pressure] + wagner
        + [r for r in mea_off if r['group'] == 'Aronu2011'])
dloaded = {'Lawson', 'Lawson-394K', 'SeoHong', 'Lal', 'Lawson-VIII'}
doutside = [r for r in data if r['group'] in dloaded and r['role'] == 'not fitted']
dfitted = scores([r for r in data if r['role'] == 'fitted' and r['unit'] == 'Pa'], dloaded)
ephase = [fixed.value(f'MEA {key} finite search counts') for key in ('main', 'offset')]
ephase += [fixed.value('MEA native and supplied census counts')]
assert all(q['descent'] == 0 for q in ephase)
amp_loaded = {'loaded-pressure', 'hartono-2021-supplemental', 'tong'}
rows = [
    ['MEA', len(mea_stage['coordinates']), len(mea_stage['active_bounds']), e47, e47,
     cell(pressure_stats(enot)), sum(q['states'] for q in ephase), sum(q['states']-q.get('available', q['states']-q.get('incomplete', 0)) for q in ephase), 0],
    ['DEA', len(dcoords), sum(r['on_bound'] for r in dcoords.values()), dfitted, dfitted, cell(pressure_stats(doutside)),
     *search_summary(dnew['tally'], len(dnew['confirmed']))],
    ['MDEA', len(mfit), sum(r['on_bound'] for r in mfit),
     *pressure_columns(mrows, {'Kuranov'}, {'corrected-Kamps', 'Kuranov-413K', 'Sedighi'}, {'Ermatchkov', 'Xiao'}),
     *search_summary(mnew['tally'], len(mnew['confirmed']))],
    ['AMP', len(acoords), len(aunc['active_bounds']), *pressure_columns(arows, amp_loaded, {'tong-baseline'}, {'kundu'}),
     *search_summary(anew['tally'], len(anew['confirmed']))],
]
assert rows[3][3].endswith('(105)') and rows[3][4].endswith('(131)')
mcomp = read(MD + 'comparison.json')
mbounded = mcomp['runs'][mcomp['chosen']]
assert mbounded['checks']['native'] == {'states': 78, 'available': 78, 'descent': 0, 'minimum': 0.0} and mbounded['checks']['hull']['gaps'] == 0 and all(r['below'] for r in mcomp['k_versus_critical'])
assert mcomp['runs']['unbounded-2']['checks']['native']['descent'] == 14 and not mstability['interpolated_set_split_state']['available']
round5 = 'analyses/round_5/results/A/'
amp_sensitivity = []
for family, assess, cost in [('free', aassessment, acost), ('fixed', afassessment, afcost)]:
    outcome = [fixed.coverage('AMP_' + family, protocol) for protocol in ('native', 'supplied')]
    amp_sensitivity.append([{'free': '100 kPa, slope fitted (AMP model)',
                             'fixed': '100 kPa, slope fixed at $-150$ K'}[family],
                            num(cost, 4), scores(assess['rows'], amp_loaded),
                            *[f"{q['tally']['descent']}/{q['tally']['available']}" for q in outcome]])
    prior = AMP if family == 'free' else AMP_FIXED
    outcome = [read(prior + protocol + '/search-outcome.json.gz') for protocol in ('native', 'supplied')]
    amp_sensitivity.append([f'Original salt fit, {family} slope', num(read(prior + 'selection.json.gz')['cost'], 4),
                            scores(read(prior + 'data-rows.json.gz'), amp_loaded),
                            *[f"{q['tally']['descent']}/{q['tally']['available']}" for q in outcome]])
table('supplement-amp-expanded', 'AMP fits to the extended data, 214 observations, with the temperature slope of the \\ce{AMPH+}--water interaction fitted or fixed.', ['Fit', 'Objective', 'Loaded total pressures, AARD (\\%) ($N$)', 'Instabilities, search trials', 'Instabilities, supplied trials'],
      amp_sensitivity, [.34,.11,.21,.13,.13],
      notes=r'Instabilities: states with a detected instability of the number searched, with the trial phases of the search alone and with the supplied trial compositions added. Both pairs have the salt-anchored shared set and the same weights. The splits of main-text Fig.~\ref{main-fig:amp-splits} belong to the fit to the first data, with the MEA-fitted shared set.')
target = LATEX / 'tables/supplement-amp-ranges.tex'
outputs[target] += outputs.pop(LATEX / 'tables/supplement-amp-expanded.tex')
fixedp = read('analyses/mdea_mea_workflow/results/phase-search-421/fixed-pressure.json')
fsplit = next(q for q in fixedp['attempts'] if q['confirmed'])
fwt = 100 * mmass['methyldiethanolamine'] * fixedp['feed']['methyldiethanolamine'] / (mmass['methyldiethanolamine'] * fixedp['feed']['methyldiethanolamine'] + mmass['water'] * fixedp['feed']['water'])
fstate = rf"\SI{{{fixedp['T_K']:.2f}}}{{\kelvin}}, {fwt:.2f} wt\% MDEA, {fixedp['feed']['carbon-dioxide'] / fixedp['feed']['methyldiethanolamine']:.3f} mol/mol and \SI{{{fixedp['P_Pa'] / 1e6:.3f}}}{{\mega\pascal}}"
assert fixedp['outcome'] == 'confirmed split' and fsplit['distinct'] and fsplit['Gibbs_decrease_over_RT_mol'] > 1e5 * fsplit['numerical_error_over_RT_mol']
new_fixed = read(MDEA + 'fixed-pressure.json.gz')
assert new_fixed['T_K'] == fixedp['T_K'] and new_fixed['P_Pa'] == fixedp['P_Pa']
common = read(AMP + '../common-pressure.json')
amp_bubbles = [fixed.endpoint_record(f'display-replays/AMP_{family}-bubble.json.gz', f'AMP_{family}')
               for family in ('free', 'fixed')]
amp_replay = read(REPLAYS + 'amp-common-pressure.json.gz')
assert amp_replay['common_Pa'] == common['common_Pa']


def amp_replay_outcome(q):
    if 'refusal' in q:
        return 'Replay refused'
    record = q['fixed']
    attempts = record['attempts']
    return (f"{record['instability']}; {sum(a['confirmed'] for a in attempts)}/{len(attempts)} "
            "seeded splits confirmed")


table('supplement-phase-replays', 'Two-liquid calculations at fixed feed, temperature and pressure for MDEA and AMP.', ['Fit', 'Pressure (MPa)', 'Outcome'],
      [['MDEA, MEA-fitted shared set', num(fixedp['P_Pa']/1e6, 3), fixedp['outcome']],
       ['MDEA, original salt fit', num(new_fixed['P_Pa']/1e6, 3), new_fixed['outcome']],
       *[[f'AMP, tracking, corrected inputs, slope {label}', num(amp_replay['common_Pa']/1e6, 6),
          amp_replay_outcome(amp_replay['outcomes'][case])]
         for case, label in [('free', 'fitted'), ('fixed', 'fixed at $-150$ K')]],
       *[[f'AMP, 100 kPa, slope {label}', num(amp_replay['common_Pa']/1e6, 6),
          fixed.value(f'AMP_{case} A phase worked-state')]
         for case, label in [('free', 'fitted'), ('fixed', 'fixed at $-150$ K')]],
       *[[name, num(common['common_Pa']/1e6, 6),
          f"{sum(a['confirmed'] for a in common['outcomes'][case]['attempts'])} confirmed of {len(common['outcomes'][case]['attempts'])} attempted splits"]
         for case, name in [('free', 'AMP, original salt fit, slope fitted'),
                            ('prior-free', 'AMP, MEA-fitted shared set, slope fitted'),
                            ('fixed', 'AMP, original salt fit, slope fixed at $-150$ K'),
                            ('prior-fixed', 'AMP, MEA-fitted shared set, slope fixed at $-150$ K')]]],
      [.42,.19,.32], notes=r'MDEA: the state of Section~\ref{sec:s-phase} at which the fit with the MEA-fitted shared set has a confirmed split. AMP: the fits to the extended data at the feed and temperature of the worked split of Table~\ref{tab:amp-reference-state}, at the historical common pressure. Tracking-reference corrected-input bubble pressures are '
      + ' and '.join(num(amp_replay['outcomes'][case]['bubble_Pa']/1e6, 6) for case in ('free', 'fixed'))
      + ' MPa for fitted and fixed slope, respectively. At the selected fixed-reference endpoints they are '
      + ' and '.join(num(q['pressure_Pa']/1e6 if q['pressure_Pa'] is not None else None, 6) for q in amp_bubbles)
      + ' MPa in that order.')
target = LATEX / 'tables/supplement-amp-ranges.tex'
outputs[target] += outputs.pop(LATEX / 'tables/supplement-phase-replays.tex')
onset = fixed.endpoint_record('display-replays/mdea-binary-onset.json.gz', 'MDEA')
old_onset = read(MDEA + 'binary-onset.json')['result']['pressures']


def onset_cell(data):
    brackets = data['brackets']
    return ', '.join(
        '--'.join(f'{T:.5f}' for T in q['bracket_K']) + ('' if q['resolved'] else ' (unresolved)')
        for q in brackets
    ) or 'No resolved bracket'


table('supplement-mdea-binary-onset',
      r'Calculated onset of a liquid--liquid gap in \COtwo-free MDEA--water with the fitted temperature laws extrapolated.',
      ['Pressure (MPa)', 'Original salt fit (K)', 'Provisional 100 kPa fit (K)'],
      [[num(int(P)/1e6, 3), onset_cell(old_onset[f'binary-{P}.json']), onset_cell(value)]
       for P, value in onset['pressures'].items()], [.24,.33,.33],
      notes='The endpoints bracket an onset classified by both the sampled Gibbs hull and tangent-plane distance '
            'on the original and refined composition grids. These are calculated brackets.')
outputs[target] += outputs.pop(LATEX / 'tables/supplement-mdea-binary-onset.tex')
# Search counts refer to the finite screen. The targeted fixed-pressure runs use separate feeds.
def reduced_gibbs(value):
    mantissa, exponent = f'{value:.3e}'.split('e')
    return rf'${mantissa}\times 10^{{{int(exponent)}}}$'


def feed_wt(point, feed, amine_id):
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude']
              for c in point['parameters']['components']}
    amine, water = (feed[k] * masses[k] for k in (amine_id, 'water'))
    return 100 * amine / (amine + water)


reference = read(ROUND7 + 'results/A/reference.json.gz')['comparisons']
fixed_c = [read(MDEA7 + case + '-fixed-pressures.json.gz') for case in ('original', 'rms')]
phase_rows = []
components = [c['component_id'] for c in ddoc['parameters']['components']]
for state in sorted(dnew['classifications'], key=lambda q: q['key']):
    key = state['key']
    feed = dict(zip(components, state['feed_mol'], strict=True))
    trial = next((r for r in state['attempts'] if r['confirmed']), None)
    label = 'DEA, feed ' + key.split(':')[1] if key.startswith('weiland-1998:') else 'DEA, Lawson VIII'
    phase_rows.append([label, num(state['temperature_K'], 2), num(state['pressure_Pa']/1e6, 3),
                       num(feed_wt(ddoc, feed, 'diethanolamine'), 2),
                       num(feed['carbon-dioxide']/feed['diethanolamine'], 3),
                       'Confirmed' if trial else 'Unresolved',
                       reduced_gibbs(trial['Gibbs_decrease_over_RT_mol']) if trial else '---',
                       reduced_gibbs(trial['numerical_error_over_RT_mol']) if trial else '---'])
assert sorted(dnew['confirmed']) == fixed.value('C3 DEA split-feed comparison')
for convention, outcome in reference.items():
    trial = outcome['attempts'][0]
    assert all(r['disposition'] == trial['disposition'] for r in outcome['attempts'])
    original = read(MDEA + 'selection.json.gz')['point']
    feed = dict(zip(outcome['species'], outcome['feed_mol'], strict=True))
    phase_rows.append(['MDEA, original weights, ' + ('tracking' if convention == 'tracking' else '100 kPa reference'),
                       num(outcome['T_K'], 2), num(outcome['P_Pa']/1e6, 3),
                       num(feed_wt(original, feed, 'methyldiethanolamine'), 2), num(feed['carbon-dioxide']/feed['methyldiethanolamine'], 3),
                       trial['disposition'].capitalize(), reduced_gibbs(trial['Gibbs_decrease_over_RT_mol']),
                       reduced_gibbs(trial['numerical_error_over_RT_mol'])])
table('supplement-liquid-splits', 'Liquid--liquid calculations for the selected DEA endpoint and the historical original-weight MDEA fit.',
      ['Fit and state', '$T$ (K)', '$P$ (MPa)', r'Amine (wt\%)', r'$\alpha$ (mol/mol)', 'Result', r'$-\Delta G/(RT)$ (mol)', 'Numerical error (mol)'],
      phase_rows, [.19,.08,.12,.075,.09,.105,.13,.135],
      notes=r'Tracking means R1--R3 use the system pressure and R5 uses 100 kPa. The 100 kPa reference case also fixes R1--R3 at 100 kPa. The DEA rows use a fixed 100 kPa reference for every reaction. The 100 kPa candidate has unresolved liquid roots even though its Gibbs energy is lower. DEA feed 31 has unresolved phase identity. One search did not finish.')
fixed_rows = []
for label, results in zip(('Original weights', 'Pressure-weighted'), fixed_c, strict=True):
    for key in ('pressure_121_MPa', 'pressure_262_MPa'):
        outcome = results[key]
        confirmed = [r for r in outcome['attempts'] if r.get('confirmed')]
        fixed_rows.append([label, num(outcome['P_Pa']/1e6, 3),
                           'Confirmed split' if confirmed else outcome.get('outcome', 'Unresolved').capitalize()])
table('supplement-mdea-fixed-pressure', 'Historical tracking-reference MDEA fits at the same two absolute pressures.',
      ['Fit', '$P$ (MPa)', 'Outcome'], fixed_rows, [.32,.18,.45],
      notes=r'R1--R3 track the system pressure and R5 uses 100 kPa. These two targeted calculations are outside the finite-screen counts in main-text Table~\ref{main-tab:amine-summary}.')

# The same objective is evaluated on both endpoints within each weighting.
mcomparisons = []
for label, record in [('Original weights', mprior), ('Pressure-weighted', mrefit)]:
    for weight, objective in record['objective'].items():
        mcomparisons.append([label + ', tracking', {'original': 'Original', 'rms': 'Pressure-weighted'}[weight],
                             objective['n'], num(objective['objective'], 2), scores(record['rows'], {'Kuranov'})])
for weight, label in [('original', 'Original'), ('rms', 'Pressure-weighted')]:
    mcomparisons.append(['Provisional, 100 kPa', label, len(fixed.fits['MDEA']['replay']['rows']),
                         num(fixed.value(f'C5 MDEA salt refit {weight} objective'), 2),
                         scores(mrows, {'Kuranov'})])
table('supplement-mdea-weighting', 'MDEA objectives on the same fitted observations and loaded total-pressure deviations.',
      ['Fit', 'Objective weights', '$N$', 'Objective', r'Loaded pressure AARD (\%) ($N$)'],
      mcomparisons, [.22,.20,.08,.15,.25],
      notes=r'Compare objectives within the same weighting. Tracking rows use the historical reaction references. The pressure deviation uses the 66 fitted Kuranov total pressures.')

quantities = read(ROUND7 + 'manuscript-handoff.json')['quantities']
def quantity_value(key):
    return quantities[key]['value']

methane = fixed.endpoint_record('display-replays/dea-methane.json.gz', 'DEA')['rows']
lawson = {q['identity']: q for q in data if q['group'] == 'Lawson'}
assert len(methane) == len(lawson) == 30
assert all(q['observed_Pa'] == lawson[q['identity']]['observed'] for q in methane)
methane_shifts = [abs(v)/1e6 for q in methane for v in q.get('pCO2_change_Pa', [])]
sign_misses = quantities['F DEA Horstmann positive predictions for negative excess enthalpy']
horstmann = [r for r in data if r['group'] == 'Horstmann' and r['observed'] < 0]
sign_misses['value'] = sum(r['value'] > 0 for r in horstmann if r['status'] == 'Available')
table('supplement-dea-expanded', 'Broadened DEA objective and diagnostics of the reported fit.',
      ['Quantity', 'Original salt fit', 'Broadened fit, 100 kPa'], [
          ['Common 140-row objective', num(quantity_value('F DEA historical expanded objective'), 2), num(dcost, 2)],
          [r'Seo and Hong partial-pressure AARD (\%)', num(quantities['F DEA SeoHong AARD_percent']['prior'], 2), num(dev['SeoHong']['AARD_percent'], 2)],
          ['Horstmann excess enthalpies with the wrong sign',
           *[f"{sign_misses[field]} of {sign_misses['population']}" for field in ('prior', 'value')]],
          ['Maximum conditional methane shift (MPa)',
           num(quantity_value('F DEA methane conditional maximum pCO2 shift')/1e6, 3),
           num(max(methane_shifts, default=None), 3)]
      ], [.52,.21,.21], notes=r'The common objective has 90 partial pressures and 50 integral heats. The methane shift holds the methane-free liquid composition fixed. The measurements do not bound the effects of dissolved methane.')

mdea_manifest = fixed.load('MDEA/manifest.json.gz')
mdea_sources = {q['identity']: q['row'] for rows in mdea_manifest['rows'].values() for q in rows}
crosswalk = {q['key']: q['identity'] for q in read(
    'analyses/mdea_mea_workflow/results/phase-search-421/observation-crosswalk.json')}
mcomponents = [c['component_id'] for c in mdoc['parameters']['components']]
phase_rows = []
for state in sorted(mnew['classifications'], key=lambda q: (q['temperature_K'], q['key'])):
    key = state['key']
    source = mdea_sources[crosswalk[key] if key.startswith('Merkley-capped:') else key.rsplit(':', 1)[0].removesuffix(':1')]
    feed = dict(zip(mcomponents, state['feed_mol'], strict=True))
    source_id = source['source_key']
    if source_id == 'BottingerMDEA2008':
        locator = r'B\"ottinger, T2 r' + source['source_row']
        source_pressure = '---'
        assert state['pressure_Pa'] == source['pressure_Pa']
    elif source_id == 'Merkley1987':
        locator = 'Merkley, Fig.~3'
        source_pressure = '/'.join(f"{float(source[k])/1000:.3f}" for k in
                                   ('candidate_pressure_1_kPa', 'candidate_pressure_2_kPa'))
        assert math.isclose(state['pressure_Pa'], float(source['proposed_pressure_kPa'])*1000)
    else:
        locator = f"{source_id[:-4]}, T{source['source_locator'].split('Table ')[1].split()[0].rstrip(',')}, r{source['source_row']}"
        source_pressure = num(source['pressure_MPa'])
        assert math.isclose(state['pressure_Pa'], float(source['pressure_MPa'])*1e6)
    pressure_record = next(q for q in r9_accounting['mdea_distinct_states'] if q['key'] == key)
    phase_rows.append([key.replace(':', r':\allowbreak '), locator, num(state['temperature_K'], 2),
                       num(feed_wt(mdoc, feed, 'methyldiethanolamine'), 2),
                       num(feed['carbon-dioxide']/feed['methyldiethanolamine']),
                       source_pressure, num(state['pressure_Pa']/1e6) + r'\newline ' + pressure_record['pressure_basis'],
                       state['native_branch'], state['supplied_branch'],
                       'None confirmed' if state['attempts'] else 'Not attempted'])
assert mnew['tally']['states'] == 11824 and not mnew['confirmed']
table('supplement-mdea-phase-outcomes', 'Outcomes at the descent states of the provisional MDEA endpoint.',
      ['State', 'Source', '$T$ (K)', r'MDEA (wt\%)', r'$\alpha$', r'Source $P$ (MPa)',
       r'Search $P$ (MPa)', 'Native', 'Supplied', 'Two-liquid outcome'],
      phase_rows, [.125,.127,.077,.077,.058,.096,.083,.089,.089,.090], long=True, size=r'\footnotesize',
      notes=f"{mnew['tally']['available']} of {mnew['tally']['states']} searches completed; "
            f"{mnew['tally']['descent']} detections at {len(phase_rows)} distinct states and no confirmed splits. "
            r"$\alpha$ is in mol \COtwo/mol MDEA and wt\% excludes \COtwo. T and r identify the source table "
            r"and row. B\"ottinger cell pressures are assignments. Merkley Fig.~3 gives the digitized traces; "
            r"the two possible pressures in Table~1 are shown, with the higher one used for the searches. "
            "The two separate high-pressure controls are unresolved.")

amp_designs = ('AMP_free', 'AMP_fixed')
amp_controls = {}
amp_screen = {}
for design in amp_designs:
    selected = fixed.fits[design]['start']
    amp_controls[design] = fixed.endpoint_record(f'{design}/controls/{selected}.json.gz', design)['rows']
    amp_screen[design] = {q['key']: q for q in fixed.coverage(design, 'native')['rows']}
measured = sorted(amp_controls['AMP_free'].keys() - {'worked-state'})
assert len(measured) == 6 and set(amp_controls['AMP_free']) == set(amp_controls['AMP_fixed'])
amp_rows = []
for key in measured:
    free, held = (amp_controls[d][key]['value'] for d in amp_designs)
    assert (free['T_K'], free['feed_mol'], free['P_Pa']) == (held['T_K'], held['feed_mol'], held['P_Pa'])
    feed = dict(zip(free['species'], free['feed_mol'], strict=True))
    assert all(amp_controls[d][key]['P_Pa'] == free['P_Pa'] for d in amp_designs)

    fits = []
    for design, control in zip(amp_designs, (free, held), strict=True):
        assert not any(q['confirmed'] for q in control['attempts'])
        outcome = 'No descent' if control['search']['no_descent_in_trial_set'] else 'Unresolved'
        expected = 'finite search, no resolved descent' if outcome == 'No descent' else 'unresolved phase identity'
        assert fixed.value(f"{design} {fixed.fits[design]['start']} phase {key}") == expected
        trial = control['minimum_trial']['seed'].replace('positive-neutral-base', 'neutral base')
        parent, parent_error = control['parent_gibbs_RT_mol']
        candidate = next((q for q in control.get('candidates', []) if q['support'] == 'L+V'), {})
        delta = candidate.get('Gibbs_over_RT_mol')
        flag = r'\textsuperscript{a}' if delta is not None and not candidate['qualified'] else ''
        fits.append([num(amp_screen[design][key]['pressure_Pa']/1e6, 5), trial,
                     reduced_gibbs(delta - parent) + flag if delta is not None else '---',
                     reduced_gibbs(parent_error + candidate['error']) if delta is not None else '---', outcome])
    source, row, _ = key.split(':')
    amp_rows.append([source.split('-')[0].capitalize() + ' r' + row, num(free['T_K'], 2),
                     num(feed_wt(adoc, feed, 'aminomethylpropanol'), 2) + r'\newline ' +
                     num(feed['carbon-dioxide']/feed['aminomethylpropanol']),
                     num(free['P_Pa']/1e6, 5),
                     *[r'\newline '.join(pair) for pair in zip(*fits, strict=True)]])
table('supplement-fixed-reference-controls', 'Six AMP controls at the measured absolute pressures. '
      'Paired entries give the fitted slope above the fixed slope.',
      ['Source row', '$T$ (K)', r'Feed (wt\%, $\alpha$)', '$P$ (MPa)', r'$P_{\rm bub}$ (MPa)',
       'Trial initialization', r'$\Delta G/(RT)$ (mol)', 'Error (mol)', 'Outcome'],
      amp_rows, [.102,.064,.083,.087,.092,.120,.139,.125,.100], size=r'\footnotesize',
      notes=r'Feed gives unloaded AMP mass percent and mol \COtwo/mol AMP. Initialization is the native seed of the minimum '
            r'tangent-plane trial. Two-liquid attempts used archived and, when available, native splits. '
            r'$\Delta G/(RT)$ is the retained liquid--vapor candidate minus the parent liquid, per feed with 1 mol AMP. '
            r'The error is the sum of the two Gibbs-energy error estimates. A dash marks an unavailable comparison. '
            r'\textsuperscript{a}The candidate did not qualify. No two-liquid split was confirmed. '
            r'The separate AMP worked-state controls find no resolved descent at either slope.')
path = LATEX / 'tables/supplement-fixed-reference-controls.tex'

matched = []
for group, unit in [('Kuranov', 'Pa'), ('Ermatchkov', 'Pa'), ('Xiao', 'Pa'),
                    ('Carson', 'J/mol'), ('corrected-Kamps', 'Pa')]:
    prefix = f'MDEA {group} {unit} matched'
    ard, bias = (fixed.quantities[f'{prefix} {metric}'] for metric in ('AARD_percent', 'bias_percent'))
    n = ard['population']['new']['available']
    assert n == ard['population']['old']['available'] == bias['population']['new']['available']
    matched.append([group, n, *[num(r[side], 2) for side in ('old', 'new') for r in (ard, bias)]])
table('supplement-mdea-reference-comparison', 'MDEA deviations for the endpoints with system-pressure and fixed references on common observations.',
      ['Source', '$N$', r'System-pressure AARD (\%)', r'System-pressure bias (\%)', r'Fixed AARD (\%)', r'Fixed bias (\%)'],
      matched, [.23,.08,.15,.15,.15,.15])
outputs[path] += outputs.pop(LATEX / 'tables/supplement-mdea-reference-comparison.tex')

salt_weighting = read(ROUND8 + 'salt-and-weighting.json.gz')['quantities']
models = salt_weighting['models']
properties = salt_weighting['properties']
cases = ('salt/incumbent', 'salt/refit', 'historical/incumbent', 'historical/refit')
matched_rows = []
for group in ('Kuranov', 'Ermatchkov', 'Xiao', 'Carson'):
    records = [properties[group][case] for case in cases]
    common = records[0]['common_keys']
    assert all(r['common_keys'] == common and r['matched']['relative_count'] == len(common) for r in records)
    property_label = {'Kuranov': 'total pressure', 'Ermatchkov': r'$p_{\COtwo}$',
                      'Xiao': r'$p_{\COtwo}$', 'Carson': 'integral heat'}[group]
    matched_rows.append([f'{group} {property_label} ({len(common)})',
                         *[num(r['matched']['AARD_percent'], 2) for r in records]])
matched_rows += [
    ['Objective at first weights', *[num(models[c]['objective']['original'], 1) for c in cases]],
]
for stratum in ('measured', 'grid'):
    coverage = [models[c]['phase']['common_keys'][stratum] for c in cases]
    matched_rows.extend([
        [f'{stratum.capitalize()} searches completed', *[f"{r['available']}/{r['requested']}" for r in coverage]],
        [f'{stratum.capitalize()} searches with a descent', *[r['descents'] for r in coverage]],
    ])
matched_rows += [
    ['Confirmed grid splits', *[r['distinct'] if isinstance(r, dict) else len(r)
                               for r in (models[c]['confirmed'] for c in cases)]],
    [f"Targeted state at {num(fixed_c[1]['pressure_262_MPa']['P_Pa']/1e6)} MPa", *[models[c]['targeted'].capitalize() for c in cases]],
]
table('supplement-mdea-matched-weights', 'Historical tracking-reference MDEA refits with two shared parameter sets and two weightings on identical observations.',
      ['Quantity', 'Salt-fitted, first weights', 'Salt-fitted, pressure weights',
       'MEA-fitted, first weights', 'MEA-fitted, pressure weights'],
      matched_rows, [.34, .15, .15, .15, .15],
      notes=r'Property rows give AARD (\%) and the common number of observations in parentheses. '
            r'Measured and grid coverage use common search keys. Search counts include repeated searches at the same state. No measured state had a confirmed split for these four fits.')

salt_replay = fixed.load('salt.json.gz')
assert salt_replay['passed']
salt_rows = salt_weighting['residuals']
salt_temperatures = sorted({float(r['temperature_K']) for r in salt_rows})
cmap = plt.colormaps['viridis']
norm = matplotlib.colors.Normalize(min(salt_temperatures), max(salt_temperatures))
fig, axes = plt.subplots(2, 2, figsize=(6.48, 4.5), constrained_layout=True, sharex=True)
for ax, salt, title in zip(axes.flat[:3], ('NaHCO3', 'Na2CO3', 'mixed'),
                           ('Sodium bicarbonate', 'Sodium carbonate', 'Mixed salts'), strict=True):
    accepted = [r for r in salt_rows if r['salt'] == salt and r['status'] == 'available']
    ax.axhline(0, color='0.55', lw=.7)
    ax.scatter([float(r['nominal_molality']) for r in accepted], [r['signed_percent'] for r in accepted],
               c=[float(r['temperature_K']) for r in accepted], cmap=cmap, norm=norm, s=18)
    ax.set(title=title, ylabel='Signed residual (%)')
refused = [r for r in salt_rows if r['status'] != 'available']
assert all(r['salt'] == 'mixed' and r['signed_percent'] is None for r in refused)
axes[1, 1].scatter([float(r['nominal_molality']) for r in refused],
                   [float(r['temperature_K']) for r in refused], color='0.2', marker='x')
axes[1, 1].set(title='Mixed salts: charge-closure refusals', ylabel='Temperature (K)',
               yticks=salt_temperatures)
for ax in axes[1]:
    ax.set(xlabel='Nominal salt molality (mol/kg)', xscale='log')
fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=axes,
             ticks=salt_temperatures, label='Temperature (K)', aspect=30)
figure(fig, 'salt-osmotic-residuals.pdf')

def salt_reconstruction():
    salt_example = fixed.load('salt.json.gz')['reconstruction']
    printed = salt_example['printed']
    m, X2, Y, H2X, Z, phi = (float(printed[k]) for k in
        ('nominal_molality', 'X2', 'Y', 'H2X', 'Z', 'phi'))
    carbonate = (m - Y - Z) / 2
    ionic_sum = m + carbonate + Y + Z
    numerator = phi * (m + X2 + Y + H2X + Z)
    target = (numerator - H2X) / ionic_sum
    for field, derived in [('ionic_sum', ionic_sum), ('numerator', numerator),
                           ('ideal_co2', H2X), ('target', target)]:
        assert math.isclose(salt_example[field], derived, rel_tol=1e-12), field
    assert printed['salt'] == 'NaHCO3' and printed['source_locator'] == 'Peiper and Pitzer 1982, Table 6(a)'
    table('supplement-salt-reconstruction', r'Worked sodium bicarbonate row from Peiper and Pitzer, '
          r'Table 6(a) \cite{peiperThermodynamicsAqueousCarbonate1982}.',
          ['$T$ (K)', '$m$', '$X_2$', '$Y$', '$H_2X$', '$Z$', '$a_w$', r'$\phi_{\rm eq}$'],
          [[printed[k] for k in ('temperature_K', 'nominal_molality', 'X2', 'Y', 'H2X', 'Z', 'water_activity', 'phi')]],
          [.11,.10,.10,.10,.10,.10,.10,.10],
          notes=rf'Molalities are in mol/kg water. The symbols denote nominal salt and sodium ($m$), '
                rf'$X_2$ carbonate, $Y$ bicarbonate, $H_2X$ dissolved \COtwo, and $Z$ hydroxide. '
                rf'Charge closure gives $m_{{\mathrm{{CO}}_3^{{2-}}}}=(m-Y-Z)/2={carbonate:.4f}$. '
                rf'The ionic target is $[\phi_{{\rm eq}}(m+X_2+Y+H_2X+Z)-H_2X]/'
                rf'(m+m_{{\mathrm{{CO}}_3^{{2-}}}}+Y+Z)=({numerator:.5f}-{H2X:.5f})/'
                rf'{ionic_sum:.5f}={target:.7f}$.')
    # The worked row belongs with the salt figure and does not shift the subsequent table numbers.
    salt_path = LATEX / 'tables/supplement-salt-reconstruction.tex'
    outputs[salt_path] = outputs[salt_path].replace(r'\caption{', r'\caption*{').replace(
        r'\label{tab:supplement-salt-reconstruction}', '')

salt_reconstruction()

# MEA keeps its historical shared-set comparison. The receivers use their original salt fits.
eold = lambda *gs: (lambda cs: num(sum(a * n for a, n in cs) / sum(n for a, n in cs), 2) + f' ({sum(n for a, n in cs)})')([escore[g] for g in gs])
eoldsearch = [read(MEA + 'paper-evidence-341/stability/candidate/search.json')[k] for k in ('grid', 'offset', 'census')]
dorig = read(DEA + 'selection.json.gz')['chosen']['search']['grid']
dorig_rows = read(DEA + 'data-rows.json.gz')
morig = read(MDEA + 'search-outcome.json.gz')
aorig = read(AMP + 'native/search-outcome.json.gz')
dorig_fit = scores(dorig_rows, {'Lawson'})
rows += [['MEA', '', '', eold('47 current-fitted pressures'), eold('47 current-fitted pressures'), eold('112 current-not-fitted pressures', 'Wagner pressures', 'Aronu 15 wt% pressures', 'Aronu 45 wt% pressures'),
          sum(q['states'] for q in eoldsearch), sum(len(q['unavailable']) if 'unavailable' in q else q['incomplete'] for q in eoldsearch), sum(q['descent'] for q in eoldsearch)],
         ['DEA', '', '', dorig_fit, dorig_fit, cell(pressure_stats([r for r in dorig_rows if r['group'] in dloaded and r['role'] == 'not fitted'])),
          *search_summary(dorig, sum(dorig['liquid_liquid_splits'].values()))],
         ['MDEA', '', '', *pressure_columns(mprior['rows'], {'Kuranov'}, {'corrected-Kamps', 'Kuranov-413K', 'Sedighi'}, {'Ermatchkov', 'Xiao'}),
          *search_summary(morig['tally'], len(morig['confirmed']))],
         ['AMP', '', '', *pressure_columns(read(AMP + 'data-rows.json.gz'), amp_loaded, {'tong-baseline'}, {'kundu'}),
          *search_summary(aorig['tally'], len(aorig['confirmed']))]]
for row in rows: row[3] = {'MEA': r'$p_{\COtwo}$', 'DEA': r'$p_{\COtwo}$', 'MDEA': '$P$', 'AMP': '$P$'}[row[0]] + ': ' + row[3]  # fitted loaded-solution observable: Hilliard/Jou and Lawson-Garst partial, Kuranov and Hartono total pressures
for i, row in enumerate(rows):
    row[7] = row[6] - row[7]
    if i < 4:
        coverage = r9_accounting['coverage'][row[0]]
        assert row[6:8] == [coverage['attempted'], coverage['completed']]
    if row[0] in ('MEA', 'DEA'): row[5] = r'$p_{\COtwo}$: ' + row[5]  # every MEA and DEA pressure not fitted is a CO2 partial pressure (Tables 5 and S8)
for row, label in zip(rows[4:], ('MEA-fitted shared set', '30-pressure Lawson--Garst fit',
                                 'fit with MEA weights', 'earlier carbamate inputs'), strict=True):
    row[:3] = [r'\multicolumn{3}{@{}p{.24\linewidth}}{' + row[0] + ', ' + label + '}']
rows.insert(4, head('Comparison fits', 9))
table('amine-summary', 'The four fixed-reference models and their comparison fits with system-pressure references.', ['Model','Fitted parameters','On bounds',r'Fitted loaded-solution pressures\textsuperscript{a}',r'All fitted pressures\textsuperscript{b}',r'Pressures not fitted\textsuperscript{c}','Attempted searches','Completed searches',r'Liquid--liquid splits found\textsuperscript{d}'], rows, [.09,.08,.06,.14,.10,.15,.08,.10,.105],
      notes=r'Pressure columns: AARD (Eq.~\eqref{eq:aard}) in \%, with the number of observations $N$ in parentheses. \textsuperscript{a}Fitted \COtwo partial pressures ($p_{\COtwo}$) of loaded MEA and DEA and fitted total pressures ($P$) of loaded MDEA and AMP. \textsuperscript{b}Column a with the fitted \COtwo-free bubble pressures of MDEA--water and AMP--water; neither column includes the fitted \COtwo--water pressures of Kiepe et al.\ in the MEA objective (Table~\ref{tab:mea-data}). \textsuperscript{c}MEA: all pressures not fitted, those at nominal 30 wt\% of the six sources of Table~\ref{tab:mea-data}, those of Wagner et al.\ and those at 15 and 45 wt\%; MDEA and AMP: total pressures and \COtwo partial pressures separately, the AMP total pressures including the 5 \COtwo-free bubble pressures of Tong et al. The receiver comparisons use the original salt-anchored fits. \textsuperscript{d}In the searches of each fit, which are finite and differ in design between the amines (Section~\ref{supp-sec:s-phase}), so the counts do not measure equal coverage and split counts are lower bounds. '
            'The MDEA endpoint is provisional. The separate MEA measured-state search completed '
            f"{r9_accounting['coverage']['MEA_measured']['completed']} of "
            f"{r9_accounting['coverage']['MEA_measured']['attempted']} attempts.")
P341 = MEAEVIDENCE
mea_fit = read(P341 + 'fitted-rows.csv')
cai_T = [float(r['observed']) for r in mea_fit if r['group'] == 'Cai' and r['quantity'] == 'temperature']
assert len(mea_fit) == 307 and len(cai_T) == 25
cai_high = rf"{sum(T >= 370 for T in cai_T)} of the {len(cai_T)} fitted MEA--water bubble temperatures of Cai et al.\ are at or above \SI{{370}}{{\kelvin}}, up to \SI{{{max(cai_T):.2f}}}{{\kelvin}}"
# DEA: the reported model against the refit with a temperature-dependent water--DEA interaction, on identical observations (#425).
D425 = read('analyses/dea_transfer/results/reactive-refit-425/comparisons.json')
dpair = {(r['group'], r['role']): r for r in D425['tableS10']} | {('outside', 'not fitted'): D425['table7']['loaded_outside_reactive_fit']}
DPAIR = [('Horstmann VLE', 'fitted', r'Water--DEA bubble pressures, Horstmann et al.\ \cite{horstmannPhaseEquilibriumExcess2002}', 'fitted beforehand', 'fitted beforehand'),
         ('Horstmann heat', 'fitted', r'Water--DEA excess enthalpies, Horstmann et al.\ \cite{horstmannPhaseEquilibriumExcess2002}', 'comparison only', 'fitted beforehand'),
         ('Cai VLE', 'fitted', r'Water--DEA bubble pressures, Cai et al.\ \cite{caiBinaryIsobaricVaporLiquid1996}', 'comparison only', 'fitted beforehand'),
         ('Lawson', 'fitted', r'$p_{\COtwo}$, Lawson and Garst \cite{lawsonGasSweeteningData1976}', 'fitted', 'fitted'),
         ('Carson', 'fitted', r'Integral absorption heats, Carson et al.\ \cite{carsonEnthalpySolutionCarbon2000}', 'fitted', 'fitted'),
         ('outside', 'not fitted', r'$p_{\COtwo}$ outside the reactive fit \cite{lawsonGasSweeteningData1976,seoSolubilitiesCarbonDioxide1996,lalSolubilityH2SCO21985}', 'not fitted', 'not fitted'),
         ('SeoHong', 'not fitted', r'of which Seo and Hong \cite{seoSolubilitiesCarbonDioxide1996}', 'not fitted', 'not fitted')]
assert all(dpair[g, r]['reference']['rows'] == dpair[g, r]['candidate']['rows'] == dpair[g, r]['reference']['relative_rows'] for g, r, *_ in DPAIR)
assert abs(dpair['Lawson', 'fitted']['reference']['AARD_percent'] - dsum['pressure']['fitted']['AARD_percent']) < 1e-9, 'the reference column is the reported DEA model'
table('supplement-dea-binary', 'Historical DEA fit with a constant water--DEA interaction against a refit with a temperature-dependent interaction, both with the MEA-fitted shared set, on identical observations.', ['Observations', '$N$', 'Role, constant interaction', 'Role, refit', r'AARD (\%), constant interaction', r'AARD (\%), refit'],
      [[label, dpair[g, r]['reference']['rows'], a413, a425, num(dpair[g, r]['reference']['AARD_percent'], 2), num(dpair[g, r]['candidate']['AARD_percent'], 2)] for g, r, label, a413, a425 in DPAIR], [.40, .05, .14, .14, .11, .10],
      notes=r'AARD follows main-text Eq.~\eqref{main-eq:aard}. Constant interaction: the constant water--DEA interaction, fitted beforehand to the bubble pressures of Horstmann et al. Refit: a water--DEA interaction with a temperature coefficient fitted beforehand to those pressures, the excess enthalpies and the bubble pressures of Cai et al., followed by a reactive fit of the same four parameters to the same data. The excess enthalpies are negative and their relative deviations large because the constant interaction gives the wrong sign. The pressures outside the reactive fit were examined during development.')
# Calibration data by amine: the sets of each objective, the sets fitted beforehand and the sets outside the objective that informed a choice.
mea_T = {r['identity']: float(r['row']['T_K']) for r in read(MEA + 'paper-evidence-341/objective-declarations.json') if r['group'] in ('Jakobsen', 'CO2-free density')} | {r['target']: float(r['temperature_K']) for r in read(P341 + 'state-targets.csv')} | {r['id']: float(r['T_K']) for f in ('density.csv', 'heat.csv', 'cp.csv') for r in read(P341 + f)}
MEA_SETS = [(r'$p_{\COtwo}$', 'Hilliard2008,Jou1995', lambda r: r['quantity'] == 'PartialPressure'), ('species mole fractions', 'Bottinger2008,matinFacileMethodDetermination2012', lambda r: r['quantity'] in ('PhaseMoleFraction', 'mole_fraction') and r['group'] != 'Cai'),
            ('species per total amine', 'Jakobsen2005', lambda r: r['group'] == 'Jakobsen'), ('integral heat', 'HemaBhavya2025', lambda r: r['quantity'] == 'AdditionEnthalpy'), ('heat capacity', 'Hilliard2008', lambda r: r['group'] == 'Cp'),
            ('loaded density', 'Amundsen2009,Hartono2014', lambda r: r['group'] == 'loaded density'), (r'\COtwo-free density', 'Amundsen2009', lambda r: r['group'] == 'CO2-free density'),
            ('MEA--water bubble temperature and vapor composition', 'caiBinaryIsobaricVaporLiquid1996', lambda r: r['group'] == 'Cai'), (r'\COtwo--water pressures', KIEPE_CITE, lambda r: r['group'] == 'Kiepe')]
tspan = lambda t: span(t, lambda v: num(v, 2))
design, mea_n = [head('MEA', 5)], 0
for label, cite, choose in MEA_SETS:
    rs = [r for r in mea_fit if choose(r)]
    t = cai_T if cite.startswith('cai') else [float(r['id'].split('-')[1]) for r in rs] if cite.startswith('kiepe') else [mea_T[r['id']] for r in rs if r['id'] in mea_T]
    assert rs and len(t) in (len(rs), len(rs) // 2), label
    role = r'fitted beforehand\textsuperscript{b}' if cite.startswith('kiepe') else 'fitted'
    source = (KIEPE_AUTHOR if cite == KIEPE_CITE else '') + r'\cite{' + cite + '}'
    design.append([label, source, len(rs), tspan(t), role])
    mea_n += len(rs)
arcis = [r for r in read(P341 + 'heat.csv') if r['source'].startswith('Arcis')]
design.append(['integral heat', r'\cite{arcisEnthalpySolutionCarbon2011}', len(arcis), tspan([float(r['T_K']) for r in arcis]), r'development\textsuperscript{a}'])
DEVELOPMENT = ('Seo and Hong', 'Lal et al.', 'Lawson and Garst, highest temperature', 'Ermatchkov et al.', 'Xiao et al.')
objective_n = {'MEA': mea_n}
for r in data_rows:
    if len(r) == 1:
        who = re.search(r'textit\{([^}]*)\}', r[0])[1]
        if ',' not in who: design.append(head(who, 5))
        if who == 'DEA': design.append(['water--DEA bubble pressure', r'\cite{horstmannPhaseEquilibriumExcess2002}', dpair['Horstmann VLE', 'fitted']['reference']['rows'], num(D425['tableS10'][12]['temperature_K'][0], 2), 'fitted beforehand'])
        continue
    title, cite = r[0].split(r' \cite')
    role = 'fitted beforehand' if ',' in who and r[2] == 'fitted' else r[2] if r[2] == 'fitted' else r'development\textsuperscript{a}' if title.startswith(DEVELOPMENT) else None
    if role:
        design.append([r[1], r'\cite' + cite, r[3], r[4], role])
        if role == 'fitted': objective_n[who] = objective_n.get(who, 0) + int(str(r[3]).split()[0])
assert D425['tableS10'][12]['group'] == 'Horstmann VLE' and len(arcis) == 14 and objective_n == {'MEA': 307, 'DEA': 140, 'MDEA': 281, 'AMP': 214}, objective_n
table('calibration-data', 'Data in the objective of each model, data fitted beforehand and data outside the objective that informed a choice.', ['Observable', 'Source', '$N$', '$T$ (K)', 'Role'], design, [.36, .16, .07, .19, .18],
      notes=r'Fitted: in the objective of the reported fit, ' + ', '.join(f'{n} observations for {k}' for k, n in objective_n.items()) + r'. Fitted beforehand: used to set a parameter that the reactive fit holds fixed. \textsuperscript{a}Development: outside the objective, but used to choose the parameters or the initial parameter set (Section~\ref{sec:data-roles}). \textsuperscript{b}The Kiepe pressures give a constant contribution to the reactive objective. $p_{\COtwo}$: \COtwo partial pressure; total pressure: bubble pressure of the loaded solution. Table~\ref{tab:mea-data} and Table~\ref{supp-tab:supplement-transfer-data} give the compositions, loadings and deviations of every set, including those that are neither fitted nor used for a choice.')
# Carbonate share of Jakobsen et al. under the tested electrostatic and shared-ion changes (#423).
C423 = MEA + 'shared-ion-electrostatics-423/c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb/ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed/'
CCASES = [('P0', 'Fit with the MEA-fitted shared set'), ('bicarbonate-anion-2.5', r'Bicarbonate Born diameter \SI{2.5}{\angstrom}'), ('bicarbonate-anion-3.5', r'Bicarbonate Born diameter \SI{3.5}{\angstrom}'), ('bicarbonate-anion-4', r'Bicarbonate Born diameter \SI{4.0}{\angstrom}'),
          ('carbonate-anion-2.5', r'Carbonate Born diameter \SI{2.5}{\angstrom}'), ('carbonate-anion-4', r'Carbonate Born diameter \SI{4.0}{\angstrom}'), ('carbonate-anion-4.953', r'Carbonate Born diameter \SI{4.953}{\angstrom}'),
          ('permittivity--5pct', r'Permittivity lowered by 5\,\%'), ('permittivity-+5pct', r'Permittivity raised by 5\,\%'), ('P1', 'Second pair of MEA permittivity coefficients'), ('M1', r'Solvation factor of \COtwo 1.5'), ('M3', 'Solvation factor of MEA 1.5'),
          ('P1-refit', 'Second permittivity pair, refitted'), ('M3-refit', 'Solvation factor of MEA 1.5, refitted')]
cshare = {k: read(C423 + k + '/carbonate-share.json') for k, _ in CCASES}
carm, crefit = read(C423 + 'arm-replay-costs.json')['arms'], read(C423 + 'refit-comparison.json')['arms']
cgm = {k: v['summary']['all']['geometric_mean'] for k, v in cshare.items()}
assert all(v['summary']['all']['n'] == 10 for v in cshare.values()) and carm['P0']['delta'] == 0
ratios = [float(r['calc_over_obs']) for r in carbonate]
adopted_carbonate = dict(geometric_mean=math.exp(math.fsum(map(math.log, ratios))/len(ratios)),
                         aard_percent=100 * math.fsum(abs(r-1) for r in ratios)/len(ratios))
table('supplement-carbonate-sensitivity', r'Carbonate share of dissolved carbon at the ten states of Jakobsen et al.\ \cite{Jakobsen2005} for the MEA model and for the changes tested.', ['Case', 'Geometric mean of calculated/observed', r'AARD (\%)'],
      [['MEA model', f"${adopted_carbonate['geometric_mean']:.4f}$", num(adopted_carbonate['aard_percent'], 2)]] + [[label, f'${cgm[k]:.4f}$', num(cshare[k]['summary']['all']['aard_percent'], 2)] for k, label in CCASES], [.52, .26, .14],
      notes=r'The shares are not fitted in any case. Every change below the second row is made to the fit with the MEA-fitted shared set. The last two rows refit the other MEA parameters; every other change is made with all other parameters fixed. The Born diameters of bicarbonate and carbonate are \SI{3.0}{\angstrom} in the MEA model.')
cratio = [float(r['calc_over_obs']) for r in cshare['P0']['rows']]
# Volume-equivalent Born diameters of the chain cations: retained replays at fixed other parameters (#423).
def born_replay(amine, group):
    out = []
    for case in ('control', 'volume-equivalent'):
        rs = [r for r in read(C423 + amine + '/' + case + '/data-rows.json.gz') if r['group'] == group and r.get('status', 'Available') == 'Available']
        out.append(100 * sum(abs(r['value'] / r['observed'] - 1) for r in rs) / len(rs))
    return out
bdea, bmdea = born_replay('diethanolamine', 'Lawson'), born_replay('methyldiethanolamine', 'Kuranov')
assert abs(bdea[0] - dsum['pressure']['fitted']['AARD_percent']) < 1e-6 and abs(bmdea[0] - next(r['statistics']['AARD_percent'] for r in read(MD + 'deviations.json') if (r['group'], r['range_name'], r['outside_range']) == ('Kuranov', 'R1', False))) < 1e-6
veq = lambda record, s: record[s + '/segment_diameter'][0] * record[s + '/segment_count'][0] ** (1 / 3)
# Published models on identical observations only, each with the role of those observations in that model's fit.
PUB = {'Baygi2015 PC-SAFT': r'Baygi and Pahlavanzadeh, PC-SAFT \cite{Baygi2015}', 'Najafloo2018 SAFT-HR': r'Najafloo and Zarei, SAFT-HR \cite{Najafloo2018}', 'Zhang2011 eNRTL': r'Zhang et al., eNRTL \cite{Zhang2011}'}
SHARED = {'Ermatchkov': r'\COtwo partial pressures of Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}, MDEA', 'corrected-Kamps': r"total pressures of P\'erez-Salado Kamps et al.\ at the temperatures corrected by Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}, MDEA"}
exact = [r for r in read(MEA + 'paper-evidence-341/same-data-comparison/published-deviations.json') if r['comparison'].startswith('exact:')]
own = lambda path: num(read(MEA + path)['pressure_aard_percent'], 2)
assert {r['n'] for r in exact} == {19} == {read(MEA + path)['n'] for path in ('same-data-comparison/matched-score.json', 'paper-evidence-341/same-data-comparison/matched-score.json')}
rows = [head(r"19 \COtwo partial pressures of Ma'mun et al.\ \cite{Mamun2005}, MEA near 393 K", 3)] + [[PUB[r['model']], (r'unclear\textsuperscript{a}' if 'role_note' in r else r['data_role']), f"${r['deviation_percent']:g}$"] for r in exact]
rows += [['This work, 16-parameter calibration', 'not fitted', own('same-data-comparison/matched-score.json')], ['This work, MEA-fitted shared set', 'not fitted', own('paper-evidence-341/same-data-comparison/matched-score.json')]]
baygi = read(SALT + 'MEA/baygi-matched-pressure.json')['aard_percent']
# The archived prior_F2 column was read from the 16-parameter matched-pressure table.
assert num(baygi['prior_F2_Pa'], 2) == own('same-data-comparison/matched-score.json')
rows.append(['This work, MEA model', 'not fitted', num(fixed.value('MEA pressure Mamun2005 AARD_percent'), 2)])
mpub = read(MD + 'published-pressure-comparisons.json')['comparisons']
ZHANG_CHEN = r'Zhang and Chen, eNRTL \cite{zhangThermodynamicModelingCO22011}'  # their Table 14: AARD 6.8 % on the 82 Kuranov total pressures and 17.7 % on the 101 Ermatchkov CO2 partial pressures, both in their regression
literature = read(ROUND8 + 'literature-populations.json.gz')['quantities']
for c in mpub:
    if c['group'] == 'corrected-Kamps':
        kamps = literature['kamps']
        common = kamps['salt/refit']['common_keys']
        assert all(q['common_keys'] == common for q in kamps.values())
        rows += [head(f"{c['measured_rows']} " + SHARED[c['group']] + ' (published)', 3)]
        rows += [['Ermatchkov et al., parameter set ' + q['set'], q['data_role'],
                  f"${literature['published_Kamps_28']['Ermatchkov ' + q['set']]:g}$"] for q in c['published_parameter_sets']]
        rows += [head(f'{len(common)} corrected Kamps total pressures (matched by row)', 3)]
        for case, label in [('historical/incumbent', 'MEA-fitted shared set'),
                            ('salt/incumbent', 'original salt fit'),
                            ('salt/refit', 'pressure-weighted fit')]:
            rows.append(['This work, system-pressure references, ' + label, c['data_role'], num(kamps[case]['matched']['AARD_percent'], 2)])
        ids = set(common)
        cohort = [r for r in mrows if r['identity'] in ids and r['group'] == c['group']]
        assert len(cohort) == len(ids)
        r9_kamps = round9['R6 corrected Kamps pressure comparisons']
        assert math.isclose(deviations(cohort)['AARD_percent'], r9_kamps['common_AARD_percent'])
        rows.append(['This work, provisional 100 kPa MDEA model (27 rows)', c['data_role'],
                     num(r9_kamps['common_AARD_percent'], 2)])
        rows.append([r'This work, same fit (all 28 rows)\textsuperscript{d}', c['data_role'],
                     num(r9_kamps['full_AARD_percent'], 2)])
        continue
    rows += [head(f"{c['measured_rows']} " + SHARED[c['group']], 3)] + [['Ermatchkov et al., parameter set ' + q['set'], {'predicted': 'not fitted'}.get(q['data_role'], q['data_role']), f"${q['mean_absolute_relative_deviation_percent']:g}$"] for q in c['published_parameter_sets']]
    if c['group'] == 'Ermatchkov': rows.append([ZHANG_CHEN, 'fitted', '$17.7$'])
    rows.append(['This work, MEA-fitted shared set', c['data_role'] + ('; used to choose the initial parameters' if c['group'] == 'Ermatchkov' else ''), num(c['selected_point_mean_absolute_relative_deviation_percent'], 2)])
    rows.append(['This work, original salt fit', c['data_role'], scores(mprior['rows'], {c['group']}).split(' (')[0]])
    score = mstats[c['group']]['R1']['False']
    role = c['data_role']
    if score['rows'] < c['measured_rows']:
        role += f"; {score['rows']} of {c['measured_rows']} predictions available"
    rows.append(['This work, pressure-weighted MDEA model', role, num(score['AARD_percent'], 2)])
K422 = 'analyses/mdea_mea_workflow/results/kuranov-published-422/'
kstat, krae = read(K422 + 'statistics.json'), read(K422 + 'raeispour-table-4.json')
kroles = collections.Counter(r['role'] for r in mrows if r['group'] in ('Kuranov', 'Kuranov-binary'))
assert {('Uyan', '22.9'), ('Uyan', '34.4'), ('Wangler', '19.7')} <= {(r['reading'], r['printed']) for r in kstat['reconstruction'] if r['subset'] == 'K82'}
assert (krae['rows'], krae['AARD_percent'], krae['role']) == (82, 10.9, 'fitted') and kstat['present']['K82']['n'] == kstat['present']['K82']['solved'] == 82 and kroles == {'fitted': 70}
k82 = read(MDEA + '../kuranov-matched-pressure.json.gz')['grouped']['K82']['salt_anchored']
assert k82['solved'] == k82['n'] == 82
kuranov = literature['kuranov']
k82_result = fixed.quantities['C7 Kuranov row-matched 82 AARD']
k82_adopted = {'available': k82_result['population'], 'AARD_percent': k82_result['new']}
kuranov_label = str(len(kuranov['source_rows'])) + r' total pressures of Kuranov et al.\ \cite{kuranovSolubilitySingleGases1996}'
rows += [head(kuranov_label + r', MDEA (matched by count)\textsuperscript{b}', 3),
         [r'Uyan et al., ePC-SAFT \cite{Uyan2015}', 'not fitted', r'$22.9$\textsuperscript{c}'], [r'Wangler et al., ePC-SAFT \cite{Wangler2018}', 'not fitted', '$19.7$'],
         [r'Raeispour Shirazi and Lotfollahi, ePC-SAFT \cite{raeispourshiraziApplicationEPC_SAFTMBEoS2020}', 'fitted', f"${krae['AARD_percent']:g}$"], [ZHANG_CHEN, 'fitted', '$6.8$'],
         head(kuranov_label + ', MDEA (matched by row)', 3),
         ['This work, MEA-fitted shared set', r'70 fitted, of which 4 \COtwo-free; 12 not fitted', num(kstat['present']['K82']['AARD_percent'], 2)],
         ['This work, original salt fit', r'70 fitted, of which 4 \COtwo-free; 12 not fitted', num(k82['AARD_percent'], 2)],
         ['This work, pressure-weighted MDEA model',
          r'70 fitted, of which 4 \COtwo-free; 12 not fitted' + (
              f"; {k82_adopted['available']} predictions available" if k82_adopted['available'] != len(kuranov['source_rows']) else ''),
          num(k82_adopted['AARD_percent'], 2)]]
table('published-models', r'Pressure deviations of published models and of this work. Published Kuranov values are matched by count\textsuperscript{b}.', ['Observations and model', 'Role of these observations in the fit of that model', r'AARD (\%)'], rows, [.50,.36,.10],
      notes=r'AARD follows Eq.~\eqref{eq:aard} over the stated observations. Published values are those reported in each source, with the digits given there. The 16-parameter calibration is defined in Section~\ref{sec:parameters}. Parameter sets I and II are the two sets of interaction parameters of Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}. \textsuperscript{a}Najafloo and Zarei do not define their average absolute deviation; it is assumed equivalent to Eq.~\eqref{eq:aard}, and their methods and conclusions describe the fitting differently. \textsuperscript{b}The published values are identified with the 82 total pressures of Table~2 of Kuranov et al.\ by their count. \textsuperscript{c}Recalculated as 34.4\,\% by Wangler et al.\ \cite{Wangler2018}. ' +
            rf'\textsuperscript{{d}}Added row {r9_kamps["additional_row"]["row"]["source_row"]} of Ermatchkov et al. Table 6 '
            rf'has {num(r9_kamps["additional_row"]["observed"]/1e6, 3)} MPa measured, '
            rf'{num(r9_kamps["additional_row"]["value"]/1e6, 3)} MPa calculated '
            rf'(+{num(r9_kamps["additional_signed_percent"], 2)}\%).')
# Published parameters of Hong et al. on identical MEA observations: retained scores, no model call.
HONG = MEA + 'same-data-comparison/hong-2027/'
hong, hchecks = read(HONG + 'supplement-table.csv'), read(HONG + 'checks.json')
hsets = [(r'\COtwo partial pressure, AARD (\%)', [('canonical', 'strict grid', 'Six sources, inside the fitted range of Hong et al.'), ('canonical', 'all', 'Six sources, with the 13 Hilliard observations at 313.00--313.147 K'), ('wagner', 'all', 'Wagner et al.')]),
         (r'Heat of Kim and Svendsen, RMSE (kJ/mol \COtwo)', [(f'Kim {T} K', 'all', f'{T} K' + mark) for T, mark in (('313.15', r'\textsuperscript{a}'), ('353.15', r'\textsuperscript{a,b}'), ('393.15', ''))]),
         (r'Loaded-solution density, RMSE (kg/m$^3$)', [(b, 'all', label + r'\textsuperscript{c}') for b, label in (('Amundsen2009', 'Amundsen et al.'), ('Hartono2014', 'Hartono et al.'), ('Han2012', 'Han et al.'))])]
hong_pressures = read(SALT + 'MEA/hong-matched-pressure.json')['grouped']
hong_phase = literature['hong']
hrows = []
for heading, sets in hsets:
    hrows += [head(heading, 9)]
    for block, subset, label in sets:
        rs = [r for r in hong if (r['block'], r['subset']) == (block, subset)]  # two rows where Hong's slope is taken on both sides of a node
        r, fitted = rs[0], int(rs[0]['adopted_fitted'])
        assert rs and len({(q['n'], q['adopted'], q['polley_hedengren_2026'], q['locally_unstable']) for q in rs}) == 1 and {q['hong_role'] for q in rs} == {'not fitted'}
        measured = read(HONG + block + '.csv')
        ids = {q['record_id'] for q in measured if q['three_model_eligible'] == 'True'
               and (subset != 'strict grid' or q['inside_hong_grid'] == 'True')}
        assert len(ids) == int(r['n']), (block, subset, len(ids), r['n'])
        if block in hong_pressures:
            predictions = eprops | {q['identity']: q for q in wagner}
            cohort = [predictions[key] for key in ids]
            adopted = deviations(cohort)['AARD_percent']
        elif block.startswith('Kim'):
            predictions = {r['record_id']: r for r in compare_mea['kim_2007']}
            cohort = [predictions[key] for key in ids]
            good = [q for q in cohort if q['interval_status'] == 'available']
            assert len(good) == len(ids)
            adopted = math.sqrt(math.fsum((float(q['predicted'])-float(q['observed']))**2 for q in good)/len(good))
        else:
            predictions = {r['identity']: r for r in compare_mea['density']}
            cohort = [predictions[key] for key in ids]
            assert all(q['status'] == 'Available' for q in cohort)
            adopted = math.sqrt(math.fsum((q['value']-q['observed'])**2 for q in cohort)/len(cohort))
        hrows.append([label, r['n'], f"{fitted} fitted / {int(r['n']) - fitted} not fitted" if fitted else 'not fitted', 'not stated' if block == 'canonical' else r['polley_hedengren_2026_role'],
                      ' / '.join(num(q['hong'], 2) for q in rs), num(adopted, 2), num(r['adopted'], 2), num(r['polley_hedengren_2026'], 2), '--' if heading.startswith('Loaded') else f"{r['locally_unstable']} of {r['n']}"])
table('supplement-hong-comparison', r'Deviations of the reconstruction of the Hong et al.\ model\ \cite{hongModelingCO2Absorption2027}, of the fixed-reference MEA model, of the MEA-fitted shared set with system-pressure references, and of the model of Polley and Hedengren \cite{polleyReactiveEPCSAFTModeling2026} on identical MEA observations at nominal 30 wt\%. '
      rf'The Hong pressures use equal fugacity at a vapor amount of \num{{{hong_phase["vapor_amount_fraction_of_feed"]:g}}} of the feed. '
      rf'{hong_phase["local_failures"]} of {hong_phase["inside_count"]} liquids in the fitted range fail the local stability test.',
      ['Observations', '$N$', 'Role in the MEA model', r'Role in \cite{polleyReactiveEPCSAFTModeling2026}', 'Hong et al. reconstruction', 'MEA model', 'MEA-fitted shared set', r'Ref.~\cite{polleyReactiveEPCSAFTModeling2026}', 'Fails the local test'], hrows, [.21, .035, .13, .09, .105, .10, .09, .08, .085],
      notes=r"Roles refer to the objective of each model; no observation was fitted by Hong et al. ``Not stated'' is defined in main-text Table~\ref{main-tab:mea-data}. The last column counts the states at which the liquid of the Hong model fails the local stability test at fixed pathway weight; the density calculation involves no phase equilibrium. \textsuperscript{a}Three of the intervals at this temperature in the full set of Kim and Svendsen were fitted during earlier model development, in the objective of Ref.~\cite{polleyReactiveEPCSAFTModeling2026}. \textsuperscript{b}The two Hong values use the pressure slope toward lower and toward higher temperature. \textsuperscript{c}The comparison between density sources informed the choice of fitted density observations. Deviations on fitted and on not-fitted data are not directly comparable.")
# Where the AMP splits lie: retained search states, projected onto temperature and loading.
acomponents = [c['component_id'] for c in adoc['parameters']['components']]
def astate(s):
    """Temperature, loading and AMP content of one state with a liquid-directed instability, and its confirmed two-liquid calculation, if any."""
    feed = dict(zip(acomponents, s['feed_mol']))
    confirmed = [a for a in s['attempts'] if a['confirmed']]
    return dict(T_K=s['temperature_K'], loading_mol_CO2_per_mol_AMP=feed['carbon-dioxide'] / feed['aminomethylpropanol'], P_Pa=s['pressure_Pa'], outside=s['outside_ranges'],
                wt=100 * amass['aminomethylpropanol'] / (amass['aminomethylpropanol'] + amass['water'] * feed['water'] / feed['aminomethylpropanol']), split=confirmed[0] if confirmed else None)
states = [astate(s) for s in aclass['states']]
split = [r for r in states if r['split']]
assert len(split) == aclass['counts']['confirmed'] and all(s['liquid_directed'] for s in aclass['states'])
WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
fitted_T = [float(r['row']['T_K']) for r in arows if r['group'] == 'loaded-pressure']  # the loaded pressures of the first data, the fit that has the splits
fig, ax = plt.subplots(figsize=(4.6, 3.5), constrained_layout=True)
ax.axhspan(min(fitted_T), max(fitted_T), color='0.87', lw=0, label='Loaded-solution pressures fitted by the first fit')
ax.axhline(read('analyses/amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json')['reaction_ranges_K']['AMP-dissociation'][1], color='k', ls=(0, (5, 2)), lw=1.3, zorder=4, label='Upper limit of the measured R5 range')
mstates = [r for r in arows if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'tong')]
ax.scatter([amp_loading(r) for r in mstates], [float(r['T_K']) for r in mstates], s=14, marker='+', color='0.45', linewidths=.7, zorder=2, label='Measured total-pressure states (Hartono, Tong)')
for rs, label, style in [([r for r in states if r not in split], 'Instability, split not confirmed', dict(s=46, facecolors='none', edgecolors=colors[0], linewidths=0.9)), (split, 'Confirmed liquid--liquid split', dict(s=9, color=colors[1]))]:
    ax.scatter([float(r['loading_mol_CO2_per_mol_AMP']) for r in rs], [float(r['T_K']) for r in rs], label=label, **style)
amp_measured_splits = read(ROUND8 + 'amp-six-states.json.gz')['quantities']['rows']
split_keys = {s['key'] for s, point in zip(aclass['states'], states, strict=True) if point['split']}
assert {r['key'] for r in amp_measured_splits} <= split_keys
ax.scatter([r['crosswalk']['loading_mol_CO2_per_mol_AMP'] for r in amp_measured_splits],
           [r['crosswalk']['T_K'] for r in amp_measured_splits],
           s=28, marker='D', facecolors=colors[1], edgecolors='black', linewidths=.7, zorder=5,
           label='Confirmed split at a measured state')
ax.set(xlabel='Loading (mol CO$_2$/mol AMP)', ylabel='Temperature (K)', xlim=(0, 1.02), ylim=(308, 398))
ax.legend(loc='upper center', bbox_to_anchor=(.5, -.18), frameon=False, ncol=1, handletextpad=.5)
figure(fig, 'amp-splits.pdf')
reported_costs = [fixed.value(name + ' selected objective') for name in DESIGNS]
CONTRIB = [('MEA', [
                (r'\COtwo partial pressures', [('common149', 'Pa')]), ('Species mole fractions', [('common149', '1'), ('restored species', '1')]), ('Species ratios of Jakobsen et al.', [('Jakobsen', '1')]),
                ('Integral absorption heats', [('common149', 'J/mol')]), ('Heat capacities', [('Cp', 'J/(mol-feed K)')]), ('Loaded densities', [('loaded density', 'kg/m^3')]), (r'\COtwo-free densities', [('CO2-free density', 'kg/m^3')]),
                ('MEA--water bubble temperatures of Cai et al.', [('Cai', 'K')]), ('MEA--water vapor mole fractions of Cai et al.', [('Cai', '1')]), (rf'\COtwo--water pressures, {KIEPE_AUTHOR}\cite{{{KIEPE_CITE}}}', [('Kiepe', 'Pa')])]),
           ('DEA', [(r'\COtwo partial pressures', [(g, 'Pa') for g in ('Lawson','SeoHong','Lal')]), ('Integral absorption heats', [('Carson', 'J/mol CO2')])]),
           ('MDEA', [
                ('Loaded total pressures of Kuranov et al.', [('Kuranov', 'Pa')]), (r'\COtwo-free pressures of Kuranov et al.', [('Kuranov-binary', 'Pa')]), ('MDEA--water and water pressures of Kim et al.', [('Kim', 'Pa')]),
                ('Species ratios of Jakobsen et al.', [('Jakobsen', '1')]), ('Integral absorption heats', [('Carson', 'J/mol'), ('Merkley', 'J/mol')]), ('Heat capacities', [('Cp', 'J/(mol-feed K)')]),
                ('Loaded densities', [('loaded-density', 'kg/m^3')]), (r'\COtwo-free densities', [('unloaded-density', 'kg/m^3')])]),
           ('AMP', [
                (r'Loaded total pressures, 313--353 K', [('loaded-pressure', 'Pa')]), (r'Loaded total pressures of Hartono et al., 373--393 K', [('hartono-2021-supplemental', 'Pa')]), ('Loaded total pressures of Tong et al.', [('tong', 'Pa')]),
                ('AMP--water bubble pressures', [('binary', 'Pa')]), ('AMP--water vapor mole fractions', [('binary', 'dimensionless')]), ('Carbamate fractions', [('nmr', 'dimensionless')])])]
crow = []
for (amine, sets), expected in zip(CONTRIB, reported_costs[:4], strict=True):
    recs = collections.defaultdict(list)
    design = 'AMP_free' if amine == 'AMP' else amine
    for row in fixed.fits[design]['replay']['rows']:
        recs[row['group'], row['unit']].append((1, row['cost']))
    total = math.fsum(cost for values in recs.values() for _, cost in values)
    assert math.isclose(total, expected, rel_tol=1e-9), amine
    assert {k for _, keys in sets for k in keys} == set(recs), (amine, set(recs))
    crow.append(head(f'{amine}, objective value {total:.3f}', 4))
    for label, keys in sets:
        values = [part for k in keys for part in recs[k]]
        n, cost = sum(n for n, _ in values), math.fsum(cost for _, cost in values)
        if keys == [('Kiepe', 'Pa')]:
            crow.append([label + r'\textsuperscript{a}', n, num(cost, 7), num(100 * cost / total, 1)])
        else:
            crow.append([label, n, num(cost, 3), num(100 * cost / total, 1)])
table('supplement-objective-contributions', 'Contribution of each fitted data set to the objective value of its reported model.', ['Data set', '$N$', 'Contribution', r'Share (\%)'], crow, [.52, .08, .14, .12],
      notes=r'The objective is that of main-text Eq.~(\ref{main-eq:fit-objective}) with the scales and weights of Tables~\ref{tab:objective-groups} and \ref{tab:transfer-scales}; values of different amines are not comparable. \textsuperscript{a} Fitted beforehand and constant in the reactive objective.')
weighted_rows = mrefit['objective']['rms']['rows']
mweights = {r['group']: r['weight'] for r in weighted_rows}
assert all(r['weight'] == mweights[r['group']] for r in weighted_rows)
scale_rows = [
    ['DEA', r'\COtwo partial pressures', '0.09', 'average over 90 pressures'],
    ['', 'Integral absorption heats', r'$0.02\,|y_j^{\mathrm{obs}}|$', 'average over 50 heats'],
    ['MDEA', 'Loaded total pressures of Kuranov et al.', '0.015', r'$1/66$'],
]
assert math.isclose(mweights['Kuranov'], 1 / (66 * .015**2))
for label, group, scale in [
        (r'\COtwo-free pressures of Kuranov et al.', 'Kuranov-binary', '1'),
        ('Mixture and pure-water pressures of Kim et al.', 'Kim', '1'),
        ('Species ratios of Jakobsen et al.', 'Jakobsen', r'$0.10\,|y_j^{\mathrm{obs}}|$'),
        ('Heat capacities', 'Cp', r'$0.02\,|y_j^{\mathrm{obs}}|$'),
        ('Integral absorption heats, Carson et al.', 'Carson', r'max(3000 J/mol, $0.05\,|y_j^{\mathrm{obs}}|$)'),
        ('Integral absorption heats, Merkley et al.', 'Merkley', r'max(3000 J/mol, $0.05\,|y_j^{\mathrm{obs}}|$)'),
        ('Loaded densities', 'loaded-density', r'$[(0.001\rho_j)^2+(0.01g_j)^2]^{1/2}$'),
        ('Unloaded densities', 'unloaded-density', r'0.5 kg/m$^3$')]:
    n = sum(r['group'] == group for r in weighted_rows)
    assert mweights[group] == 1 / n
    scale_rows.append(['', label, scale, f'$1/{n}$'])
scale_rows += [
    ['AMP', 'Loaded total pressures', '0.015', 'average over 105 pressures'],
    ['', 'Binary bubble pressures', '0.05', 'average over 52 binary observations'],
    ['', 'Vapor AMP mole fractions', r'$\max(10^{-4},0.05\,y_j^{\mathrm{obs}})$', 'average over 52 binary observations'],
    ['', 'Carbamate fractions', '0.003', 'average over 57 fractions'],
]
table('supplement-transfer-scales', 'Residual scales and weights of the fitted DEA, MDEA and AMP data sets.',
      ['Amine','Data set',r'Scale $s_j$',r'Weight $w_j$'], scale_rows, [.08,.32,.27,.27],
      notes=r'Pressure residuals are logarithmic, with dimensionless scales. $\rho_j$ is the measured density and $g_j$ the local secant slope against loading. For MDEA the weights average each observation group. The extra factor $0.015^{-2}$ in the retained Kuranov weight is written in the scale column.')
scales_path = LATEX / 'tables/supplement-transfer-scales.tex'
outputs[scales_path] = outputs[scales_path].replace('tab:supplement-transfer-scales', 'tab:transfer-scales')

# Distances are in optimizer-bound coordinates. The complete pairwise distances
# and screened draws are preserved by the study handoff.
start_rows = []
vector_rows = []
for design, attempts in fixed.handoff['fit_attempts'].items():
    design_label = design.replace('_', ' ')
    record = fixed.load(f'{design}/manifest.json.gz')
    vectors = record['starts']
    if any(start.startswith('LHS-') for start in attempts):
        draws = fixed.load(f'{design}/replacement-starts.json.gz')['draws']
        vectors |= {key: value['start'] for key, value in draws.items() if value['disposition'] == 'eligible'}
    coordinate_order = record['coordinate_order']
    coordinates_text = r'; \allowbreak '.join(
        rf'{i}. \nolinkurl{{{key}}}' for i, key in enumerate(coordinate_order, 1))
    vector_rows.append(head(design_label, 2))
    vector_rows.append(['Order', coordinates_text])
    manifest = fixed.value(design + ' start distances')
    expanded_key = design + ' admitted-start distances'
    distances = fixed.value(expanded_key) if expanded_key in fixed.quantities else {
        '/'.join(pair): value for pair, value in manifest.items()}
    distances |= {'/'.join(pair): value for pair, value in manifest.items()}
    for start, attempt in attempts.items():
        near = [value for pair, value in distances.items() if start in pair.split('/')]
        bound_ids = [r['identity'] for r in fixed.fits[design]['endpoint']['coordinates']]
        bound = attempt['active_bounds'] or {}
        active = ', '.join(f"{bound_ids.index(k)+1} {v}" for k, v in bound.items())
        selected = fixed.handoff['selected_starts'][design] == start
        status = ('Provisional' if design == 'MDEA' else 'Selected') if selected else attempt['status'].replace('_', ' ')
        gradient = attempt['solver_scale_projected_gradient_inf']
        vector = vectors['A' if start == 'A-loose' else start]
        fit_start = fixed.load(f'{design}/{start}.json.gz')
        assert fit_start['optimizer_start'] == vector['optimizer'], (design, start)
        assert len(vector['vector']) == len(coordinate_order)
        anchor = f"start-{design.replace('_', '-')}-{start}"
        physical = vector['vector'].copy()
        if design in r9_units:
            conversion = r9_units[design]
            physical[conversion['coordinate_index']] += conversion['offset_J_mol']
        vector_rows.append([rf'\hypertarget{{{anchor}}}{{{start}}}',
                            ', '.join(rf'\num{{{q:.9g}}}' for q in physical)])
        endpoint = r9_accounting['endpoint_stages'][design][start][-1]
        stop = endpoint['termination'].split(' tolerance', 1)[0]
        if stop in ('Function', 'Parameter'):
            status += r'\newline ' + stop + ' tolerance'
        start_rows.append([design_label, rf'\hyperlink{{{anchor}}}{{{start}}}',  num(min(near) if near else (0 if start == 'A-loose' else None)),
                           num(attempt['initial_cost']), num(attempt['objective'], 6),
                           reduced_gibbs(gradient) if gradient is not None else '---', active or '---', status])
table('supplement-fit-starts', 'Starts and endpoints of the fits at the fixed 100 kPa reaction reference.',
      ['Fit', 'Start', 'Nearest RMS', 'Initial $C$', 'Endpoint $C$', 'Projected gradient', 'Active bounds', 'Outcome'],
      start_rows, [.115,.085,.085,.102,.12,.12,.15,.125], long=True, size=r'\footnotesize',
      notes=r'RMS distance is measured relative to coordinate bounds. A-loose repeats A. Active bounds are numbered in fit coordinate order. '
            r'The projected gradient uses the optimizer scale. The endpoints missed the projected-gradient limit of $10^{-8}$. '
            r'MDEA had one evaluable draw of 64, in addition to inherited start A. Draw 17 missed the start-separation rule. '
            + 'Start A gives ' + num(r9_accounting['mdea_start_counts']['A_AARD_percent']['Kuranov'], 2)
            + r'\% on 66 loaded Kuranov pressures and '
            + num(r9_accounting['mdea_start_counts']['A_AARD_percent']['Ermatchkov'], 2)
            + r'\% on 101 Ermatchkov partial pressures. ' +
            r'AMP with fixed slope retains a second basin at 2741.26. A dash marks an unavailable value or an empty active set.')

table('supplement-start-vectors', 'Initial vectors in physical fit coordinates. AMP enthalpy entry 8 is the signed increment in J/mol.',
      ['Start', 'Coordinates in fit order'], vector_rows, [.13,.85], long=True, size=r'\footnotesize')
vectors_path = LATEX / 'tables/supplement-start-vectors.tex'
# LTcaptype is local to this group and keeps the unnumbered vectors out of the table sequence.
outputs[vectors_path] = outputs[vectors_path].replace(r'\begingroup', r'\begingroup\def\LTcaptype{}', 1).replace(
    r'\caption{Initial vectors in physical fit coordinates. AMP enthalpy entry 8 is the signed increment in J/mol.}\label{tab:supplement-start-vectors}',
    r'\multicolumn{2}{@{}l}{Initial vectors in physical fit coordinates. AMP enthalpy entry 8 is the signed increment in J/mol.}')

c1 = []
c1_declarations = {}
for design in DESIGNS[:-1]:
    for mode, point in (
        ('fixed-at-old', fixed.load(f'{design}/manifest.json.gz')['prior_declaration']),
        ('selected', fixed.fits[design]['endpoint']),
    ):
        c1_declarations[mode, design] = hashlib.sha256(
            json.dumps(point, sort_keys=True, allow_nan=False).encode()).hexdigest()

for key, record in fixed.quantities.items():
    if not key.startswith(('C1 fixed-at-old', 'C1 selected')):
        continue
    state, comparison = key[3:].rsplit(' ', 1)
    if comparison == 'enthalpy':
        continue
    volume = comparison == 'volume'
    state = state.removesuffix(' Eq.')
    err = record['new']
    mode = 'selected' if state.startswith('selected') else 'fixed-at-old'
    design = state[len(mode) + 1:].split()[0].split('-')[0]
    conditions = record['pressure_basis']
    pressure_type = None
    # Read both contributors for the daughter sum.
    for source in record['new_contributors']:
        case = read(source['path'])
        assert case['mode'] == mode, key
        assert (case['endpoint_fingerprint'] == record['endpoint_fingerprint']
                == c1_declarations[mode, design]), key
        assert all(case[field] == value for field, value in conditions.items()), key
        if case.get('pressure_basis') == 'retained absolute pressure':
            basis = 'imposed'
        else:
            assert 'observation' in case and 'tracking_pressure_Pa' in case, key
            basis = 'calculated bubble'
        assert pressure_type in (None, basis), key
        pressure_type = basis
    assert pressure_type is not None, key
    state_label = (state.replace('AMP_free', 'AMP (free slope)') + r'\newline '
                   f"{conditions['T_K']:.2f} K, {conditions['P_Pa']/1e6:.5g} MPa")
    c1.append([state_label, pressure_type,
               r'$\partial G^*/\partial P - V_{\mathrm{EOS}}$ (m$^3$)' if volume else r'Eq.~12 $-$ Gibbs--Helmholtz (J/mol amine)',
               reduced_gibbs(err['signed_error']), reduced_gibbs(err['estimated_error']),
               err['admitted_steps'], err['disposition']])
table('supplement-fixed-reference-consistency', 'Gibbs-energy derivative checks at the named states and fixed 100 kPa reaction reference.',
      ['State', 'Pressure type', 'Comparison', 'Discrepancy', 'Error estimate', 'Steps', 'Disposition'],
      c1, [.22,.105,.197,.106,.11,.055,.149], long=True, size=r'\footnotesize',
      notes=r'Fixed-at-old rows use the tracking-fit parameter vectors re-evaluated with reaction references fixed at 100 kPa '
            r"(\nolinkurl{prior_declaration} in each model's \nolinkurl{manifest.json.gz}). "
            r'Selected rows use the MEA, DEA, provisional MDEA and free-slope AMP endpoints of main-text Table~\ref{main-tab:amine-summary} '
            r'(\nolinkurl{endpoint} in the fit file named by the selected start in \nolinkurl{selection.json}). '
            r'The imposed pressure is shared by the MDEA parent and the two daughter inventories, including their sum. '
            r'Calculated bubble pressures are total pressures. '
            r'The declarations are archived in \nolinkurl{analyses/fixed_reaction_reference/results/}, '
            r'under each model name (\nolinkurl{AMP_free} for AMP). Each SHA-256 fingerprint identifies one declaration.\par '
            + r'\par '.join(
                rf'{design.removesuffix("_free")}, {mode}: \nolinkurl{{{digest}}}'
                for (mode, design), digest in c1_declarations.items()))
path = LATEX / 'tables/supplement-fit-starts.tex'
outputs[path] += outputs.pop(LATEX / 'tables/supplement-fixed-reference-consistency.tex')

scale_rows = []
for design in DESIGNS:
    u = fixed.conditional(design)
    scale_rows.append([design.replace('_', ' '), len(fixed.fits[design]['replay']['rows']),
                       u['responsive'], len(u['free_coordinates']), u['dof'],
                       num(u['stage_variance'], 8)])
table('supplement-fixed-reference-variance', 'Conditional variance of the responsive observations at each selected endpoint.',
      ['Fit', 'Fitted rows', 'Responsive rows', 'Interior rank', 'Degrees of freedom', 'Variance'],
      scale_rows, [.17,.13,.15,.13,.15,.16],
      notes='The variance excludes the 39 structurally constant Kiepe pressures and the three pure-water Kim pressures from their respective fits. Active parameters are held fixed.')
path = LATEX / 'tables/supplement-transfer-bounds.tex'
outputs[path] += outputs.pop(LATEX / 'tables/supplement-fixed-reference-variance.tex')

amp_fixed = coordinates(fixed.conditional('AMP_fixed'))
amp_fixed['AMP-hydrolysis-enthalpy-increment']['value'] = r9_units['AMP_fixed']['endpoint_increment_J_mol']
table('supplement-amp-fixed-parameters', r'Parameters of the fixed-reference AMP sensitivity with the slope held at $-150$ K.',
      ['Parameter', 'Value', 'Standard error', 'Active bound'],
      [[label, num(amp_fixed[key]['value'], digits), num(amp_fixed[key]['error'], digits),
        fixed.fits['AMP_fixed']['diagnostics']['active_bounds'].get(key, '---')]
       for (label, digits), key in zip(AFIT, aorder, strict=True) if key in amp_fixed],
      [.45,.15,.17,.15], notes=r'The enthalpy increment is relative to the starting R4 correlation in J/mol.')
outputs[path] += outputs.pop(LATEX / 'tables/supplement-amp-fixed-parameters.tex')
sys.path.insert(0, str(ROOT / 'analyses/round_9'))
from displays import tables as round9_tables

round9_tables(round9, table, head, num, reduced_gibbs)

read('analyses/dea_transfer/results/binary.json')
read(BASE + 'conditional-uncertainty.json')
read(BASE + 'checks.json')
read('analyses/dea_transfer/inputs/part-ii-346/route-current.json')
# Values used by the surviving MEA and historical-comparison prose checks.
f2 = lambda v: f'{float(v):.2f}'
f1 = lambda v: f'{float(v):.1f}'
mea = f1(pressure_stats([r for r in mea_fit if r['quantity'] == 'PartialPressure'], 'predicted')['AARD_percent'])
hstrict, hall, hwagner = (next(r for r in hong if (r['block'], r['subset']) == k) for k in (('canonical', 'strict grid'), ('canonical', 'all'), ('wagner', 'all')))
hong_main = [f1(hstrict['hong']), f1(hong_pressures['canonical']['strict_grid']['salt_anchored']['aard_percent']), f"the {hstrict['n']} observations", f"at {hstrict['locally_unstable']} of them"]
hong_supplement = [f"{f2(hstrict['hong'])}\\,\\%, the MEA model by {f2(hstrict['adopted'])}\\,\\% and the model of Polley and Hedengren by {f2(hstrict['polley_hedengren_2026'])}", ', '.join(f2(hall[k]) for k in ('hong', 'adopted')) + f" and {f2(hall['polley_hedengren_2026'])}",
                   f"{int(hall['locally_unstable']) + int(hwagner['locally_unstable'])} of the {int(hall['n']) + int(hwagner['n'])} measured pressure states", f"{hchecks['grid_stability']['locally unstable']} of the {sum(hchecks['grid_stability'].values())} nodes",
                   ' and '.join(f2(hchecks['full_pressure_replay_AARD_percent'][k]) for k in ('adopted', 'polley_hedengren_2026')), ' or '.join(f2(hchecks['kim_endpoint_AARD_313_353'][k]['AARD_percent']) for k in ('cool', 'warm'))]
# MEA model by temperature band (#409): every row recomputed from the retained points.
BANDS = MEA + 'stripper-temperature-409/'
bpts = read(MEAFIT + 'band-points.json')['result']
for point in bpts:
    point['band'] = 'absorber' if point['T_K'] <= 353.2 else 'stripper' if point['T_K'] >= 370 else 'intermediate'
historical_bands = {(r['property'], r['band'], r['role']): r for r in read(BANDS + 'band-table.csv') if r['cohort'] == 'all'}
current_bands = read(MEAFIT + 'bands.json')['result']
BAND_CITE = dict(Hilliard2008='Hilliard2008', Jou1995='Jou1995', Aronu2011='Aronu2011', Idris2014='idrisSpeciationMEACO2Adducts2014', Wagner2013='wagnerSolubilityCarbonDioxide2013', Mamun2005='Mamun2005',
                 Xu2011='Xu2011', Amundsen2009='Amundsen2009', Hartono2014='Hartono2014', Han2012='hanDensityWater12012', Sobrino2016='sobrinoViscosityDensityMeasurements2016', Concepcion2023='concepcionHeatCapacitiesDifferent2023',
                 Weiland1997='weilandHeatCapacityAqueous1997', Vinjarapu2024='HemaBhavya2025', Arcis2011='arcisEnthalpySolutionCarbon2011', Kim2007='Kim2007', Kim2014='Kim2014')
brel = lambda rows: [100 * (float(q['predicted']) - float(q['observed'])) / float(q['observed']) for q in rows]
bstat = {}
for b in current_bands:
    key = b['property'], b['band'], b['role']
    d = brel([q for q in bpts if (q['property'], q['band'], q['role']) == key])
    assert len(d) == b['n'] and math.isclose(math.fsum(map(abs, d))/len(d), b['AARD_percent'], rel_tol=1e-9)
    assert math.isclose(math.fsum(d)/len(d), b['mean_signed_relative_percent'], abs_tol=1e-9)
    bstat[*key, 'all'] = dict(b, previous_AARD=historical_bands[key]['AARD_percent'])
for b in read(BANDS + 'band-table.csv'):
    if b['cohort'] == 'all':
        continue
    key = (b['property'], b['band'], b['role'], b['cohort'])
    d = brel([q for q in bpts if (q['property'], q['band'], q['role'], q['cohort']) == key])
    assert len(d) == int(b['n']), key
    bstat[key] = dict(b, AARD_percent=math.fsum(map(abs, d))/len(d), mean_signed_relative_percent=math.fsum(d)/len(d))
PROPS = {'CO2 partial pressure': r'\COtwo partial pressure', 'heat of absorption': 'Absorption heat', 'heat capacity': 'Heat capacity', 'density': 'Density'}
BROLE = {'fitted': 'fitted', 'not fitted': 'not fitted', 'not fitted, 15/45 wt%': r'not fitted, 15 and 45 wt\%', 'not fitted, source-flagged': r'not fitted, flagged\textsuperscript{a}'}
trange = lambda b: f"{float(b['T_min_K']):.0f}" + ('' if round(float(b['T_min_K'])) == round(float(b['T_max_K'])) else f"--{float(b['T_max_K']):.0f}")
def temperature_band_points():
    points = []
    for row in mea_pressure:
        prediction = eprops[row['target']]
        points.append(('CO2 partial pressure', 'fitted' if row['target'] in fitted_pressure else 'not fitted',
                       row['source'], float(row['temperature_K']), prediction['observed'], prediction['value']))
    for row in read(MEAEVIDENCE + 'wagner-pressure.csv'):
        prediction = next(q for q in wagner if q['identity'] == row['target'])
        points.append(('CO2 partial pressure', 'not fitted', row['source'], float(row['temperature_K']),
                       prediction['observed'], prediction['value']))
    for row in read(MEAEVIDENCE + 'transfer.csv'):
        prediction = eprops['off-window:'+row['target'].removesuffix('-pco2')]
        points.append(('CO2 partial pressure', 'not fitted, 15/45 wt%', row['source'],
                       float(row['temperature_K']), prediction['observed'], prediction.get('value')))
    ids = {q['identity'].replace('AMU-DENS-', 'Amundsen2009_state_')
           for q in fixed.fits['MEA']['replay']['rows'] if 'density' in q['group']}
    for q in compare_mea['density']:
        points.append(('density', 'fitted' if q['identity'] in ids else 'not fitted', q['row']['source'],
                       float(q['row']['T_K']), q['observed'], q.get('value')))
    cp_fitted = {(float(row['T_K']), float(row['loading'])) for row in read(MEAEVIDENCE + 'cp.csv')}
    for q in compare_mea['heat_capacity']:
        points.append(('heat capacity', 'fitted' if q['source'] == 'Hilliard2008' and (q['T_K'], q['loading']) in cp_fitted else 'not fitted',
                       q['source'], q['T_K'], q['observed_kJ_kg_K'], q['predicted_kJ_kg_K']))
    fitted = {q['identity']: q for q in fixed.fits['MEA']['replay']['rows']}
    arcis = {q['identity']: q for q in caloric['arcis']}
    for row in read(MEAEVIDENCE + 'heat.csv'):
        is_fit = row['role'] == 'fitted'
        result = fitted[row['id']] if is_fit else arcis[row['id']]
        prediction = result['value']/1000 if is_fit else result['predicted']
        points.append(('heat of absorption', 'fitted' if is_fit else 'not fitted', row['source'],
                       float(row['T_K']), -float(row['observed_kJ_mol']), -prediction if prediction is not None else None))
    for q in fixed.load('MEA/heat-comparison.json.gz')['rows']['rows']:
        points.append(('heat of absorption', 'not fitted', q['source'], q['T_K'], q['observed_kJ_mol'],
                       q['predicted_kJ_mol']))
    for q in compare_mea['kim_2007']:
        if q['interval_status'] == 'available':
            flagged = q['source_inconsistent'] == 'True' or q['first_120'] == 'True'
            points.append(('heat of absorption', 'not fitted, source-flagged' if flagged else 'not fitted',
                           'Kim2007', float(q['T_K']), float(q['observed']), float(q['predicted'])))
    return points

current = collections.defaultdict(list)
for prop, role, source, T, observed, value in temperature_band_points():
    band = 'absorber' if T <= 353.2 else 'stripper' if T >= 370 else 'intermediate'
    current[prop, band, role].append((source, T, observed, value))
brows = []
for prop in PROPS:
    for band in ('absorber', 'intermediate', 'stripper'):
        for (p, b, role), points in sorted(current.items()):
            if (p, b) != (prop, band):
                continue
            values = [100*(calc/obs-1) for _, _, obs, calc in points if calc is not None]
            assert values, (prop, band, role)
            previous = historical_bands[prop, band, role]
            # The band registry supplies the tracking population. Match source,
            # temperature and measured value with multiplicity before reusing its
            # common-population comparison with the earlier MEA-fitted set.
            identity = lambda source, T, observed: (source, round(T, 8), round(observed, 10))
            old_rows = [q for q in bpts if (q['property'], q['band'], q['role']) == (prop, band, role)]
            old_ids = collections.Counter(identity(q['source'], float(q['T_K']), float(q['observed'])) for q in old_rows)
            new_ids = collections.Counter(identity(source, T, obs) for source, T, obs, value in points if value is not None)
            paired = old_ids == new_ids and int(previous['n']) == len(values)
            source_names = sorted({q[0] for q in points})
            brows.append([PROPS[prop], band.capitalize() + ', ' +
                          trange(dict(T_min_K=min(q[1] for q in points), T_max_K=max(q[1] for q in points))) + ' K',
                          BROLE[role], count(len(points), len(values)),
                          num(math.fsum(map(abs, values))/len(values), 2), num(math.fsum(values)/len(values), 2),
                          num(previous['AARD_percent'], 2) if paired else '---',
                          r'\cite{' + ','.join(BAND_CITE[q] for q in source_names) + '}'])
table('supplement-temperature-bands', 'Deviations of the MEA model by temperature band.', ['Property', 'Band', 'Role', '$N$', 'AARD (\\%)', 'MSRD (\\%)', 'AARD (\\%), MEA-fitted set', 'Sources'], brows, [.17, .17, .16, .045, .08, .08, .10, .13],
      notes=r'Absorber: $T\le\SI{353.2}{\kelvin}$; stripper: $T\ge\SI{370}{\kelvin}$; intermediate: between the two. Fitted observations are in the objective of the MEA model; no loaded-solution observation at or above \SI{370}{\kelvin} is fitted, and all were examined during development; ' + cai_high + r'. AARD follows Eq.~\eqref{main-eq:aard}; MSRD is the mean of $100\,(y^{\mathrm{calc}}-y^{\mathrm{obs}})/y^{\mathrm{obs}}$, negative where the calculated value is low. Pressures are at nominal 30 wt\% MEA unless stated. Absorption heats are heat releases per mole of \COtwo as each source defines them; the heats of Kim and Svendsen, Kim et al.\ and Vinjarapu et al.\ are calculated at \SI{1.734}{\mega\pascal}, the pressure reported by Vinjarapu et al. \textsuperscript{a}Four intervals of Kim and Svendsen at \SI{393.15}{\kelvin}, two inconsistent with their integrals and the first two additions from zero loading, reported separately.')
bget = lambda prop, band, role='not fitted', cohort='all': bstat[prop, band, role, cohort]
bpa, bps = bget('CO2 partial pressure', 'absorber'), bget('CO2 partial pressure', 'stripper')
assert int(bget('CO2 partial pressure', 'absorber', cohort='six-source 30 wt%')['n']) + int(bget('CO2 partial pressure', 'stripper', cohort='six-source 30 wt%')['n']) == escore['112 current-not-fitted pressures'][1]
assert all('Wagner2013' in b['sources'].split() for b in (bpa, bps)) and float(bget('density', 'stripper', cohort='Han2012 loaded')['mean_signed_relative_percent']) < 0
bmin = {prop: min(brel([q for q in bpts if q['property'] == prop and q['band'] == 'stripper'])) for prop in ('heat capacity', 'density')}
bheat = {c: -float(bget('heat of absorption', 'stripper', cohort=c)['mean_signed_relative_percent']) for c in ('Vinjarapu 2024 Table 5 (replayed)', 'Kim et al. 2014 (replayed)', 'Kim and Svendsen 2007')}
assert min(bheat.values()) > 0
bkim = {role: [q for q in bpts if q['property'] == 'heat of absorption' and q['band'] == 'stripper' and q['cohort'] == 'Kim and Svendsen 2007' and q['role'] == role] for role in ('not fitted', 'not fitted, source-flagged')}
bkim_rmse = math.sqrt(sum((float(q['predicted']) - float(q['observed'])) ** 2 for rows in bkim.values() for q in rows) / sum(map(len, bkim.values())))
assert [len(v) for v in bkim.values()] == [16, 4], 'the paper\'s Kim and Svendsen RMSE at 393.15 K covers the 16 unflagged and 4 flagged intervals'
bands_main = [rf"\SI{{{bkim_rmse:.2f}}}{{\kilo\joule\per\mole}} of \COtwo over all {sum(map(len, bkim.values()))} intervals, including the {WORDS[len(bkim['not fitted, source-flagged'])]} flagged for source problems", rf"by {float(bpa['AARD_percent']):.2f}\,\% at 313--\SI{{353}}{{\kelvin}}, on {bpa['n']} observations, and by {float(bps['AARD_percent']):.2f}\,\% at 373--\SI{{393}}{{\kelvin}}, on {bps['n']},", rf"the {escore['112 current-not-fitted pressures'][1]} not-fitted pressures of the six sources at 313--\SI{{393}}{{\kelvin}}",
              rf"the {bget('heat capacity', 'stripper')['n']} heat capacities and {bget('density', 'stripper')['n']} densities deviate on average by {f1(bget('heat capacity', 'stripper')['AARD_percent'])}\,\% and {f1(bget('density', 'stripper')['AARD_percent'])}\,\%", rf"by up to ${bmin['heat capacity']:.1f}$ and ${bmin['density']:.1f}$\,\%",
              rf"for the {bget('density', 'stripper', cohort='Han2012 loaded')['n']} loaded-solution densities of Han et al.\ \cite{{hanDensityWater12012}} are {f1(-float(bget('density', 'stripper', cohort='Han2012 loaded')['mean_signed_relative_percent']))}\,\% low on average",
              rf"low by {f1(bheat['Vinjarapu 2024 Table 5 (replayed)'])}\,\% for Vinjarapu et al.", rf"{f1(bheat['Kim et al. 2014 (replayed)'])}\,\% for Kim et al.", rf"{f1(bheat['Kim and Svendsen 2007'])}\,\% for Kim and Svendsen"]
ecost = mea_stage['rss'] / 2
wcai = [float(r['cost']) for r in read(MEAFIT + 'objective-contributions.csv') if r['group'] == 'Cai']
wband = [mea_stage['SE_multiplier'] * float(r['SE_bound_fixed']) / float(r['value'])
         for r in read(MEAFIT + 'uncertainty/prediction-bands.csv') if r['group'] == 'common149: partial_pressure']
assert len(wcai) == 2 and len(wband) == escore['47 current-fitted pressures'][1]
sci = lambda v, d: (lambda m, e: rf'{float(m):.{d}f}\times10^{{{int(e)}}}')(*f'{v:.{d}e}'.split('e'))
cother = [v for k, v in cgm.items() if k != 'P0' and not k.endswith('-refit')]
# Water-bicarbonate refits: the main-text paragraph and the supplement text beside the table that final_rerun_tables.py writes from the same files.
SB = 'analyses/mdea_mea_workflow/results/shared-bicarbonate-417/'
sbprof, sbsearch, sbcomp = read(SB + 'profile.json.gz'), read(SB + 'mdea-search-readback.json'), read(SB + 'mdea-comparison.json.gz')
assert read(SB + 'mdea-group-readback.json')['ordered_cases'] == ['reported', 'low', 'high']  # the case order of every 'original' list below
sbids = [r['identity'] for r in efit if r['conditional_SE']]
sbcorr = dict(zip(sbids, read(MEA + 'paper-evidence-341/uncertainty/covariance.json')['native_correlation'][sbids.index('pair/bicarbonate-anion/water/k_ij')]))
sballow = max(r['delta_cost'] for r in read(MEA + 'paper-evidence-341/uncertainty/profiles.json'))
sblow, sbhigh = (sbprof['selected'][s] for s in ('low', 'high'))
sbrise = [p['cost'] - sbprof['center_cost'] for p in (sblow, sbhigh)]
sbfit, sbout = ([c['AARD_percent'] for c in sbcomp[g]['original']] for g in ('all pressures fitted', 'all pressures not fitted'))
sbmea = sbprof['searches'][repr(sblow['k'])]
assert max(sbrise) <= sballow and max(abs(sbfit[2] - sbfit[0]), abs(sbout[2] - sbout[0])) < 0.05 and sbsearch['high']['counts']['confirmed_distinct_splits'] == 0
assert all(sbprof['searches'][repr(p['k'])]['grid']['descent'] == sbprof['searches'][repr(p['k'])]['offset']['descent'] == sbprof['searches'][repr(p['k'])]['census']['descent'] == 0 for p in (sblow, sbhigh))
sbkur = [c['AARD_percent'] for c in sbcomp['Kuranov']['original']]
assert abs(sbkur[0] - bmdea[0]) < 1e-6
def sbset(sets):  # count-weighted over the sets: the AARD over all of their observations
    cases = [sbcomp[g]['original'] for g in sets]
    n = sum(c[0]['relative_rows'] for c in cases)
    return n, [sum(c[i]['relative_rows'] * c[i]['AARD_percent'] for c in cases) / n for i in range(3)]
(sbtn, sbtot), (sbpn, sbpart) = sbset(('corrected-Kamps', 'Kuranov-413K', 'Sedighi')), sbset(('Ermatchkov', 'Xiao'))
assert sbtn + sbpn == sbcomp['all pressures not fitted']['original'][0]['relative_rows'] and all(abs(v - w) < 1e-9 for v, w in zip(sbset(('corrected-Kamps', 'Kuranov-413K', 'Sedighi', 'Ermatchkov', 'Xiao'))[1], sbout)), 'total and CO2 partial pressures are every pressure outside the objective'
assert max(abs(v[2] - v[0]) for v in (sbkur, sbtot, sbpart)) < 0.1 and sbtot[1] < sbtot[0] and sbpart[1] > sbpart[0], 'at the upper value the displayed deviations change by less than 0.1 points; at the lower value total pressures improve and CO2 partial pressures worsen'
sbsplits = WORDS[sbsearch['low']['counts']['confirmed_distinct_splits']]
# The 27 measured MDEA states with a vapor-directed instability: states with a converged two-phase calculation, and those shown only by an earlier trial composition.
mphase = read('analyses/mdea_mea_workflow/results/phase-search-421/measured-phase.json')
mconv = sum(any(a.get('requested_tolerance_met') and a.get('distinct') for a in r['attempts']) for r in mphase)
mtrial = sum(r['native_branch'] == 'none' for r in mphase)
# Round-3 calculations (#432) quoted in text pass 4.
R3 = 'analyses/round_3/results/'
q1, q2, q3, q4, q6, q7, q8 = (read(R3 + f) for f in ('q1.json', 'q2.json', 'q3.json', 'q4.json', 'q6.json', 'q7-summary.json', 'q8.json'))
q1ll = {k: sum(any(a['confirmed'] for a in r[k]['attempts']) for r in q1['rows']) for k in ('free', 'fixed')}
q1tpd = [r['free']['minimum_trial']['quantities']['tpd_over_rt'] for r in q1['rows'] if any(a['confirmed'] for a in r['free']['attempts'])]
assert len(q1['rows']) == 15 and q1ll == {'free': 14, 'fixed': 0}
assert max(abs(r['fixed']['minimum_trial']['quantities']['tpd_over_rt']) for r in q1['rows'][1:]) < 1.2e-13
q2s = {g: [q2['scores'][g][f]['AARD_percent'] for f in ('free', 'fixed')] for g in ('hartono-2021', 'tong-2012')}
assert all(math.isclose(q2['scores'][g][f]['AARD_percent'], -q2['scores'][g][f]['bias_percent']) for g in q2s for f in ('free', 'fixed')), 'every pressure underpredicted'
q3d = [r['reference'] for r in q3['rows'][:2]]
assert [r['k'] < 0.2 for r in q3['rows']] == [True, True] + [False] * 4 and all(r['instability'] == 'finite search, no resolved descent' and not any(a.get('confirmed') for a in r['attempts']) for r in q3['rows'][2:])
q4p = [r['pCO2_change']['absolute'] for r in q4['rows'][:2]]
q6d = q6['split']['diagnostics']
q8d = q8['dea']
# Prose check: each string repeats a value of the text and is rebuilt here from the retained records.
stated = {}
def say(path, *values): stated.setdefault(path, []).extend(values)
lowT = lambda rows, group: pressure_stats([r['prediction'] for r in rows if r['group'] == group])['AARD_percent']
first, second = (read(round5 + f'original-{k}.json.gz') for k in ('main', 'slope-150'))  # the two fits to the first AMP data
e112 = f1(pressure_stats([r for r in mea_pressure if r['target'] not in fitted_pressure], 'predicted')['AARD_percent'])
refchange = read('analyses/round_5/results/C/MEA-k-profile.json.gz')['delta_cutoff']
q4a = read(MEAFIT + 'q4.json')['result']
hp = lambda block, subset, model: f2(hong_pressures[block][subset][model]['aard_percent'])
say('main.tex', rf'at 30 wt\% deviate by {mea}\,\%')
say('submission/chemrxiv.md', f'at 30 wt% deviate by {mea}%')
say('sections/conclusion.tex', rf'deviates by {mea}\,\% from its 47 fitted')
say('sections/transfer_results.tex', bands_main[1], bands_main[3], *bands_main[6:],
    f"at any of the {sum(q['states'] for q in ephase[:2])} liquid states or {ephase[2]['states']} liquid--vapor states",
    rf"from which it deviates by {f1(lowT(first['original']['rows'], 'loaded-pressure'))}\,\%",
    f"gave {len(split)} confirmed liquid--liquid splits and {len(states) - len(split)} further detected instabilities among the same {asearch['states']} states")
say('sections/mea_system_modeling_results.tex', rf'deviate by {mea}\,\%', rf'deviate by {e112}\,\%', f"at most {max(r['delta_cost'] for r in read(MEAFIT + 'uncertainty/profiles.json')):.2f}", rf'{100 * min(wband):.1f}--{100 * max(wband):.1f}\,\%',
    f"from {sbprof['center_cost']:.2f} to {ecost:.2f}", rf"deviate by {e112} instead of {f1(escore['112 current-not-fitted pressures'][0])}\,\%",
    rf"{f1(baygi['prior_F2_Pa'])}\,\% for the 16-parameter calibration, {f1(read(MEA + 'paper-evidence-341/same-data-comparison/matched-score.json')['pressure_aard_percent'])}\,\% with the MEA-fitted shared set and {f1(baygi['salt_anchored_Pa'])}\,\% for the MEA model",
    f"AARD of {100*math.fsum(abs(r-1) for r in old_ratios)/len(old_ratios):.1f}", f"is {math.exp(math.fsum(map(math.log, old_ratios))/len(old_ratios)):.3f}, against {cgm['P0']:.3f}", bands_main[0])
say('sections/data_methods.tex', rf"{100 * sum(wcai) / ecost:.1f}\,\% of the objective value, {ecost:.2f}", f"leaves {mea_stage['na']} observations and {mea_stage['stage_denominator']} residual degrees of freedom")
say('supplement.tex', origins[0], *origins[3:],
    rf"deviate by {hp('canonical', 'strict_grid', 'hong')}\,\%, the MEA model by {hp('canonical', 'strict_grid', 'salt_anchored')}\,\% and the model of Polley and Hedengren by {hp('canonical', 'strict_grid', 'polley_hedengren')}",
    f"{hp('canonical', 'all', 'hong')}, {hp('canonical', 'all', 'salt_anchored')} and {hp('canonical', 'all', 'polley_hedengren')}", *hong_supplement[2:4], hong_supplement[5], f"with the Hong parameters, {hchecks['stable_fixed_vapor']['tried']} pass the test",
    f'by {carm['M1']['delta']:.3f}', f'by {carm['M3']['delta']:.3f}',
    f"falls {-crefit['M3-refit']['delta_cost']:.3f} below", f"falls to {cgm['M3-refit']:.4f}", f'tested changes is {max(cother):.4f}',
    f'contribute {wcai[0]:.3f} and {wcai[1]:.3f} to the objective value of {ecost:.3f}, together {100 * sum(wcai) / ecost:.2f}', f"factor of that equation is {mea_stage['stage_variance']:.8f}",
    f"at the {sbmea['grid']['states'] + sbmea['offset']['states']} liquid and {sbmea['census']['states']} liquid--vapor states", f"At the lower bound, ${sbprof['points']['-0.5']['k']:g}$, the objective rises by {sbprof['points']['-0.5']['cost'] - sbprof['center_cost']:.2f}, so the midpoint {sblow['k']:.4f} was taken",
    f'reference change of {refchange:.2f}', rf'deviate by {f1(sbkur[1])} instead of {f1(sbkur[0])}\,\%', rf'by {f1(sbpart[1])} instead of {f1(sbpart[0])}\,\%',
    rf"by {q2s['hartono-2021'][0]:.2f} and {q2s['tong-2012'][0]:.2f}\,\% for the first fit and by {q2s['hartono-2021'][1]:.2f} and {q2s['tong-2012'][1]:.2f}\,\% for the second",
    f"by {q4a['rows'][0]['pCO2_change']['absolute']:.5f} and " + rf"\SI{{{q4a['rows'][1]['pCO2_change']['absolute']:.2f}}}{{\pascal}}", f"from ${q4a['heat_previous_kJ_mol']:.3f}$ to " + rf"\SI{{{q4a['heat_previous_kJ_mol'] + q4a['heat_change']['absolute']:.3f}}}",
    f"distance of $+{q6d['trial_minimum']:.4f}$", f"give $+{q6d['vapor_connected_minimum']:.4f}$", f"recovers all {q7['recovered']} detected instabilities and finds none at the other {q7['searched_negatives']} states",
    f"from {first['cost']:.4f} to {second['cost']:.4f}", rf"from {f1(lowT(first['original']['rows'], 'loaded-pressure'))} to {f1(lowT(second['original']['rows'], 'loaded-pressure'))}\,\%")
# Fixed 100 kPa references (#429, #440): the text now states these values from the selected fits.
# Read directly so the source index of the displays is unchanged; each value is traced to a #440 record or to a display that final_rerun_tables.py checks.
FXR = ROOT / 'analyses/fixed_reaction_reference'
fxload = lambda name: json.loads(gzip.decompress((FXR / name).read_bytes()) if name.endswith('.gz') else (FXR / name).read_bytes())
fxq = fxload('manuscript-handoff.json')['quantities']
fx = lambda key: fxq[key]['new']
fxrow = lambda table, label: re.search(re.escape(label) + r'.*?\\\\', (LATEX / 'tables' / table).read_text()).group(0)
fxnum = lambda text: re.findall(r'\$(-?[0-9.]+)\$', text)
fxmea = f"{fx('MEA pressure legacy AARD_percent'):.2f}"
fxcarb = [r['value'] / r['observed'] for r in fxload('results/display-replays/mea-comparisons.json.gz')['carbonate_share']]
fxcai = [r['cost'] for r in fxload('results/MEA/A.json.gz')['replay']['rows'] if r['group'] == 'Cai']
assert len(fxcarb) == 10 and len(fxcai) == 50 and math.isclose(fx('MEA selected objective'), math.fsum(r['cost'] for r in fxload('results/MEA/A.json.gz')['replay']['rows']), rel_tol=1e-9)
fxband = {k: fxnum(fxrow('supplement-temperature-bands.tex', k)) for k in (r'\COtwo partial pressure & Absorber, 313--353 K & not fitted &', r'\COtwo partial pressure & Stripper, 373--393 K & not fitted &', r'Heat capacity & Stripper, 373--393 K', r'Density & Stripper, 373--393 K')}
fxhong = {k: fxnum(fxrow('supplement-hong-comparison.tex', k)) for k in ('Six sources, inside the fitted range', 'Six sources, with the 13 Hilliard')}
fxheat = fxload('results/display-replays/caloric-and-species.json.gz')['reference_state']
fxstale = {('main.tex', rf'at 30 wt\% deviate by {mea}\,\%'): rf'at 30 wt\% deviate by {fxmea}\,\%',
    ('submission/chemrxiv.md', f'at 30 wt% deviate by {mea}%'): f'at 30 wt% deviate by {fxmea}%',
    ('sections/conclusion.tex', rf'deviates by {mea}\,\% from its 47 fitted'): rf'deviates by {fxmea}\,\% from its 47 fitted',
    ('sections/mea_system_modeling_results.tex', rf'deviate by {mea}\,\%'): rf'deviate by {fxmea}\,\%',
    ('sections/mea_system_modeling_results.tex', rf'deviate by {e112}\,\%'): rf"deviate by {fx('MEA pressure added AARD_percent'):.2f}\,\%",
    ('sections/mea_system_modeling_results.tex', rf"{f1(baygi['prior_F2_Pa'])}\,\% for the 16-parameter calibration, {f1(read(MEA + 'paper-evidence-341/same-data-comparison/matched-score.json')['pressure_aard_percent'])}\,\% with the MEA-fitted shared set and {f1(baygi['salt_anchored_Pa'])}\,\% for the MEA model"):
        rf"{f1(baygi['prior_F2_Pa'])}\,\% for the 16-parameter calibration, {f1(read(MEA + 'paper-evidence-341/same-data-comparison/matched-score.json')['pressure_aard_percent'])}\,\% with the MEA-fitted shared set and {f1(baygi['salt_anchored_Pa'])}\,\% for the restricted model in that sequence; the MEA model with the \SI{{100}}{{\kilo\pascal}} references deviates by {fx('MEA pressure Mamun2005 AARD_percent'):.2f}\,\%",
    ('sections/mea_system_modeling_results.tex', f"AARD of {100*math.fsum(abs(r-1) for r in old_ratios)/len(old_ratios):.1f}"): f"AARD of {100*math.fsum(abs(r-1) for r in fxcarb)/len(fxcarb):.2f}",
    ('sections/data_methods.tex', rf"{100 * sum(wcai) / ecost:.1f}\,\% of the objective value, {ecost:.2f}"): rf"{100 * math.fsum(fxcai) / fx('MEA selected objective'):.1f}\,\% of the objective value, {fx('MEA selected objective'):.2f}",
    ('sections/transfer_results.tex', bands_main[1]): rf"by {fxband[r'\COtwo partial pressure & Absorber, 313--353 K & not fitted &'][0]}\,\% at 313--\SI{{353}}{{\kelvin}}, on 69 observations, and by {fxband[r'\COtwo partial pressure & Stripper, 373--393 K & not fitted &'][0]}\,\% at 373--\SI{{393}}{{\kelvin}}, on 66,",
    ('sections/transfer_results.tex', bands_main[3]): rf"the 15 heat capacities and 26 densities deviate on average by {fxband['Heat capacity & Stripper, 373--393 K'][0]}\,\% and {fxband['Density & Stripper, 373--393 K'][0]}\,\%",
    ('supplement.tex', rf"deviate by {hp('canonical', 'strict_grid', 'hong')}\,\%, the MEA model by {hp('canonical', 'strict_grid', 'salt_anchored')}\,\% and the model of Polley and Hedengren by {hp('canonical', 'strict_grid', 'polley_hedengren')}"):
        rf"deviate by {fxhong['Six sources, inside the fitted range'][0]}\,\%, the MEA model by {fxhong['Six sources, inside the fitted range'][1]}\,\% and the model of Polley and Hedengren by {fxhong['Six sources, inside the fitted range'][3]}",
    ('supplement.tex', f"{hp('canonical', 'all', 'hong')}, {hp('canonical', 'all', 'salt_anchored')} and {hp('canonical', 'all', 'polley_hedengren')}"):
        f"{fxhong['Six sources, with the 13 Hilliard'][0]}, {fxhong['Six sources, with the 13 Hilliard'][1]} and {fxhong['Six sources, with the 13 Hilliard'][3]}",
    ('supplement.tex', f"factor of that equation is {mea_stage['stage_variance']:.8f}"): f"factor of that equation is {fixed.conditional('MEA')['stage_variance']:.8f}",
    ('supplement.tex', f"by {q4a['rows'][0]['pCO2_change']['absolute']:.5f} and " + rf"\SI{{{q4a['rows'][1]['pCO2_change']['absolute']:.2f}}}{{\pascal}}"): rf"\SI{{-81.803}}{{\kilo\joule\per\mole}} of \COtwo and {fxheat['cp_J_mol_K']:.3f} J/(mol K)",
    ('supplement.tex', f"from ${q4a['heat_previous_kJ_mol']:.3f}$ to " + rf"\SI{{{q4a['heat_previous_kJ_mol'] + q4a['heat_change']['absolute']:.3f}}}"): None}
assert f"{fxheat['heat_kJ_mol']:.3f}" == '-81.803'
for (path, old), new in fxstale.items():
    stated[path] = [v for v in stated[path] if v != old] + ([new] if new else [])
missing = [(path, value) for path, values in stated.items() for value in values if value not in (LATEX / path).read_text()]
emit('tables/number-sources.json',json.dumps(sources,indent=2)+'\n')
if '--check' in sys.argv:
    previous_sources = json.loads((LATEX / 'tables/number-sources.json').read_text())
    for source in sorted(previous_sources.keys() | sources.keys()):
        assert previous_sources.get(source) == sources.get(source), f'Changed display record: {source}'
    for path, value in outputs.items():
        assert path.read_bytes()==(value if isinstance(value,bytes) else value.encode()), path
    print(f'Numeric and retained-figure check passed: {len(outputs)} displays; {len(sources)} source files.')
else:
    for path,value in outputs.items():
        path.write_bytes(value if isinstance(value,bytes) else value.encode())
for path, value in missing: print(f'Prose check failed: {path} lacks {value!r}')
assert not missing, f'{len(missing)} prose values missing'
