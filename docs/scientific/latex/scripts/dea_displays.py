"""Present retained DEA, MDEA and AMP results and the tables that compare the four amines, with a byte-for-byte display check; no model calls."""
import ast
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

ROOT = Path(__file__).resolve().parents[4]
LATEX = ROOT / 'docs/scientific/latex'
BASE = 'analyses/dea_transfer/results/refit-413/'
MEA = 'analyses/mea_parameter_bundle/results/'  # read as retained files, so replacing them refreshes every MEA number shown here
SALT = MEA + 'salt-anchored-435/'
MEAFIT = SALT + 'MEA/F4/'
MEAEVIDENCE = SALT + 'MEA/evidence/F4/'
DEA = BASE.replace('refit-413', 'salt-anchored-435/campaign')
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

def get_fit(path, audit):
    uncertainty = read(path + 'conditional-uncertainty.json.gz')
    multiplier = read(path + audit)['result']['SE_multiplier']
    return uncertainty, {
        r['identity']: dict(value=r['origin'], bounds=r['bounds'], on_bound=i in uncertainty['active_bounds'],
                            error=uncertainty['conditional_standard_error'][r['identity']] * multiplier
                            if r['identity'] in uncertainty['conditional_standard_error'] else None)
        for i, r in enumerate(uncertainty['coordinates'])
    }

params = read(BASE + 'parameter-values.csv')
fitted_names = [r'$k_{\mathrm{DEAH^+,w}}$', r'$k_{\mathrm{DEACOO^-,w}}$', r'R4 constant term $A_4$', r'R4 enthalpy increment $\delta h$']
head = lambda text, n: [r'\addlinespace\multicolumn{' + str(n) + r'}{@{}l}{\textit{' + text + '}}']
fit_rows = [head('DEA', 5)]
data = read(DEA + 'data-rows.json.gz')
groups = read(DEA + 'deviations.json.gz')
dev = {r['group']: r['statistics'] for r in groups if r['range_name'] == 'R1' and r['statistics']}

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

count = lambda n, used: str(n) + (f' ({used})' if int(used) != n else '')
data_rows = [head('DEA', 11)]
for group in dict.fromkeys(r['group'] for r in data):
    rs = [r for r in data if r['group']==group]
    t = [r['T_K'] for r in rs]
    data_rows.append([name(group, cite=True), SETS[group][2], rs[0]['role'], count(len(rs), dev[group]['relative_rows']), span(t, lambda v: num(v,2)), *composition(group), *marks(group), num(dev[group]['AARD_percent'],2), num(dev[group]['bias_percent'],2)])
DATA_HEAD = ['Data set','Property','Role',r'$N$',r'$T$ (K)','Amine content',r'$\alpha$ (mol/mol)','R4','R5',r'AARD (\%)',r'Bias (\%)']
ranges = groups
rows = []
for group in dict.fromkeys(r['group'] for r in data):
    cells = []
    for law in LAWS:
        for outside in ['False','True']:
            hit = [r for r in ranges if r['group']==group and r['range_name']==law and str(r['outside_range'])==outside and r['statistics']]
            cells += [f"{hit[0]['available']}/{hit[0]['statistics']['relative_rows']}", num(hit[0]['statistics']['AARD_percent'],2)] if hit else ['---','---']
    if set(cells) != {'---'}: rows.append([name(group),*cells])
    else: assert group in ['Cai','Horstmann'], 'Only the binary comparisons use no reaction correlation'
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
# Manuscript figures use only retained observation/curve values and range marks.
curves = [r for r in read(DEA + 'curve-data.json.gz') if r['status'] == 'Available']
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
MARKERS = ['o', 's', '^', 'D', 'v', 'P', 'X', '*', 'p', 'h']
def series(ax, x, y, style, T, temperatures, used, filled, label):
    """A model line and its legend entry. In every panel of a figure the symbol shape means the temperature;
    the color separates the curves of one panel, and the line style shows the position relative to the R4 and R5 ranges."""
    i = temperatures.index(round(T))
    color = next(c for c in colors[i % len(colors):] + colors if c not in used)
    used.add(color)
    ax.plot(x, y, style, color=color)
    ax.plot([], [], style, color=color, marker=MARKERS[i], markersize=4.5, markerfacecolor=color if filled else 'none', label=label)
    return dict(marker=MARKERS[i], edgecolors=color, facecolors=color if filled else 'none')
DEA_PANELS = [('Lawson','Lawson-394K'),('SeoHong',),('Lal',),('Carson',)]
dea_temperatures = sorted({round(r['T_K']) for r in curves if any(r['group'] in groups for groups in DEA_PANELS)})
fig,axes=plt.subplots(2,2,figsize=(6.48,5.8),constrained_layout=True)
for ax, groups, title in zip(axes.flat,DEA_PANELS,'abcd'):
    cs, used = [r for r in curves if r['group'] in groups], set()
    for index,label in enumerate(dict.fromkeys(r['curve'] for r in cs)):
        line=sorted([r for r in cs if r['curve']==label],key=lambda r:r['loading'])
        outside=line[0]['outside_ranges']['DEA-dissociation'] is True
        hydrolysis=line[0]['outside_ranges']['carbamate-hydrolysis'] is True
        assert all((r['outside_ranges']['DEA-dissociation'],r['outside_ranges']['carbamate-hydrolysis'])==(outside,hydrolysis) for r in line)
        assert not outside or hydrolysis, 'Figure markers require outside both intervals'
        caption=f"{line[0]['T_K']:.2f} K" if groups!=('Carson',) else f"{float(line[0]['row']['DEA_mass_fraction'])*100:g} wt%"
        look=series(ax,[r['loading'] for r in line],[r['value']/1000 for r in line],'--' if outside else ':' if hydrolysis else '-',line[0]['T_K'],dea_temperatures,used,line[0]['group'] in ('Lawson','Carson'),caption)
        obs=[r for r in data if r['group'] in groups and abs(r['T_K']-line[0]['T_K'])<1e-8]
        if groups==('Carson',): obs=[r for r in obs if r['row']['DEA_mass_fraction']==line[0]['row']['DEA_mass_fraction']]
        assert all((r['outside_ranges']['DEA-dissociation'],r['outside_ranges']['carbamate-hydrolysis'])==(outside,hydrolysis) for r in obs)
        ax.scatter([loading(r['row']) for r in obs],[r['observed']/1000 for r in obs],s=25,**look)
        if groups==('Carson',):  # the short heat curves are labelled at their ends so each reads at print size
            ax.lines[-2].set_linewidth(2.2)
            ax.annotate(caption,(line[-1]['loading'],line[-1]['value']/1000),xytext=(0,8) if caption=='30 wt%' else (3,0),textcoords='offset points',ha='center' if caption=='30 wt%' else 'left',va='center',fontsize=7,color=look['edgecolors'],bbox=dict(boxstyle='square,pad=0.1',facecolor='white',edgecolor='none'))
    ax.set_title(f'({title})', loc='left'); ax.set(xlabel='Loading (mol CO$_2$/mol DEA)',ylabel='Integral heat (kJ/mol CO$_2$)' if groups==('Carson',) else 'CO$_2$ partial pressure (kPa)',yscale='linear' if groups==('Carson',) else 'log')
    ax.legend(ncol=2, columnspacing=.7, handlelength=1.8, handletextpad=.4)
figure(fig,'dea-current-measured-model.pdf')
fig, axes = plt.subplots(1, 3, figsize=(6.48, 2.6), sharey=True, constrained_layout=True)
for ax, fraction in zip(axes, ('0.10', '0.20', '0.30')):
    line = sorted((r for r in curves if r['group'] == 'Carson' and r['row']['DEA_mass_fraction'] == fraction), key=lambda r: r['loading'])
    assert len(line) == 25
    ax.plot([r['loading'] for r in line], [r['value']/1000 for r in line], color=colors[0], linestyle=':')
    obs = [r for r in data if r['group'] == 'Carson' and r['row']['DEA_mass_fraction'] == fraction]
    assert all(r['role'] == 'fitted' for r in obs)
    ax.scatter([loading(r['row']) for r in obs], [r['observed']/1000 for r in obs], s=15, color=colors[0])
    ax.set_title(f'{100*float(fraction):g} wt%')
    ax.set_xlabel('Loading (mol CO$_2$/mol DEA)')
axes[0].set_ylabel('Integral heat (kJ/mol CO$_2$)')
figure(fig, 'dea-integral-heat-concentrations.pdf')
fig,axes=plt.subplots(1,2,figsize=(6.48,3.0),constrained_layout=True)
for ax,group,scale,letter in [(axes[0],'Horstmann',1,'a'),(axes[1],'Cai',0.001,'b')]:
    ps=[r for r in data if r['group']==group]
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
mdoc = read(MDEA + 'selection.json.gz')['point']
law, = [c['temperature_law'] for pair in mdoc['parameters']['pairs']
        if {pair['component_id_a'], pair['component_id_b']} == {'water', 'methyldiethanolamine'}
        for c in pair['coefficients']]
reference = law['reference_temperature']['magnitude']
assert reference == 423.0
coefficients = [t['coefficient']['value']['magnitude'] for t in law['terms']]
assert [t['power'] for t in law['terms']] == [0, 1]
temperatures = [r['T_K'] for r in comparison]
ax.plot(temperatures, [coefficients[0] + coefficients[1] * (T - reference) for T in temperatures], color=colors[0], label='MDEA model')
ax.plot(temperatures, [r['k'] for r in comparison], color=colors[2], ls='--', label='Fit with the MEA-fitted shared set')
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
fitted_pressure = {r['id'] for r in read(f2 + 'fitted-rows.csv') if r['quantity'] == 'PartialPressure'}
pressure = {'MEA': [(float(r['loading']), float(r['ln_pred_over_obs']), 'fitted' if r['target'] in fitted_pressure else 'not fitted', float(r['temperature_K'])) for r in mea_pressure]}
pressure['DEA'] = [(loading(r['row']), math.log(r['value']/r['observed']), r['role'], r['T_K']) for r in data if r['group'] in ('Lawson', 'Lawson-394K', 'SeoHong', 'Lal', 'Lawson-VIII')]
mrows = read(MDEA + 'data-rows.json.gz')
def mdea_loading(r):
    q = r['row']
    if r['group'] == 'corrected-Kamps': return float(q['m_CO2_mol_kg_water']) / float(q['m_MDEA_mol_kg_water'])
    if r['group'] == 'Sedighi': return float(q['alpha_mol_CO2_per_mol_MDEA'])
    return float(q['m_CO2_mol_per_kg_H2O']) / float(q['m_MDEA_mol_per_kg_H2O'])
pressure['MDEA'] = [(mdea_loading(r), math.log(r['value']/r['observed']), r['role'], r['T_K']) for r in mrows if r['group'] in ('Kuranov', 'Kuranov-413K', 'corrected-Kamps', 'Sedighi') and r['status'] == 'Available']
arows = read(AMP + 'data-rows.json.gz')
pressure['AMP'] = [(float(r['row']['alpha_mol_CO2_per_mol_AMP']), math.log(r['value']/r['observed']), r['role'], r['T_K']) for r in arows if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'tong') and r['status'] == 'Available']
assert {k: collections.Counter(r for _, _, r, _ in v) for k, v in pressure.items()} == {
    'MEA': {'fitted': 47, 'not fitted': 112}, 'DEA': {'fitted': 30, 'not fitted': 67, 'comparison only': 10},
    'MDEA': {'fitted': 66, 'not fitted': 54}, 'AMP': {'fitted': 105}}
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
carbonate = read(f2 + 'carbonate-share.csv')
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

def collect(entries, law, stat, key):
    """Retained statistics as out[data set][reaction][position relative to the measured range]."""
    out = {}
    for e in entries:
        if e[stat]: out.setdefault(key(e), {}).setdefault(e[law], {})[str(e['outside_range'])] = e[stat]
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

mrows = read(MDEA + 'data-rows.json.gz')
for r in mrows: r['key'] = r['group']
mstats = collect(read(MDEA + 'deviations.json.gz'), 'range_name', 'statistics', lambda e: e['group'])
data_rows += amine('mdea', 'MDEA', MSETS, mrows, mstats, {'MDEA-dissociation': 'R5'}, mdea_basis)
MFIT = [(r'$k_{\mathrm{MDEA,w}}$ at 423 K',1,4), (r'$10^{3}\,\mathrm{d}k_{\mathrm{MDEA,w}}/\mathrm{d}T$ (K$^{-1}$)',1e3,4), (r'$k_{\mathrm{MDEAH^+,CO_2}}$',1,4), (r'$k_{\mathrm{MDEAH^+,w}}$ at 313.15 K',1,4),
        (r'$b_{\mathrm{MDEAH^+,w}}$ (K)',1,3), (r'$k_{\mathrm{MDEAH^+,HCO_3^-}}$',1,4), (r'$\sigma_{\mathrm{MDEAH^+}}$ (\AA)',1,4), (r'$u_{\mathrm{MDEAH^+}}/k_B$ (K)',1,3)]
munc, mcoords = get_fit(MDEA, 'MDEA/information.json.gz')
mfit = list(mcoords.values())
fit_rows += [head('MDEA', 5)] + [[name, bold(num(scale*r['value'], digits) + (r'\textsuperscript{a}' if r['on_bound'] else '')),
                                  '---' if r['on_bound'] else num(scale*r['error'], digits), bounds(*r['bounds'], digits, scale), '']
                                 for (name, scale, digits), r in zip(MFIT, mfit, strict=True)]
stage = {k: read(MEA + 'objective-weights-420/' + k + '/information.json.gz')['result'] for k in ('MEA', 'DEA', 'MDEA', 'AMP')}
mcorr = max(abs(c) for i, row in enumerate(munc['conditional_correlation']) for j, c in enumerate(row) if i != j)  # largest conditional correlation of the MDEA fit

afeed = {r['identity']: r for r in read('analyses/amp_transfer/inputs/retransfer-344/observation-rows.csv')}
akey = lambda e: e['group'] + ('-y' if e['group'] == 'binary' and e['unit'] != 'Pa' else '')
for r in arows: r['key'] = akey(r)
adoc = read(AMP + 'selection.json.gz')['point']
amass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in adoc['parameters']['components']}
def amp_basis(rs):
    feed = [afeed[r['identity']] for r in rs]
    if 'x_AMP' in rs[0]['row']: return r'$x_{\mathrm{A}}=\,$' + span([float(r['row']['x_AMP']) for r in rs], sig), '---'
    wt = [100*amass['aminomethylpropanol']/(amass['aminomethylpropanol'] + amass['water']*float(f['water'])) for f in feed]
    return span(wt, sig) + r' wt\%', span([float(f['alpha']) for f in feed], sig)
afree, asame, aunc = read(AMF + 'fit-summary.json'), read(AM + 'same-row-deviations.csv'), read(AMM + 'conditional-uncertainty.json')
AMODEL, AFREE = 'Slope -150 K against #404 main', 'F2 main against #404 main'
assert afree['selection']['selected'] == 1 and {r['case'] for r in asame} == {AMODEL, AFREE}
aunc, acoords = get_fit(AMP, 'AMP/information.json.gz')
aorder = ['AMP-water-k', 'AMP-water-slope', 'AMPH-water-k', 'AMPH-water-slope', 'AMPH-CO2-k',
          'AMPH-segment-diameter', 'AMPCOO-segment-diameter', 'AMP-hydrolysis-a', 'AMP-hydrolysis-enthalpy-increment']
adev = read(AMP + 'deviations.json.gz')
astats = collect(adev, 'range_name', 'statistics', akey)
data_rows += amine('amp', 'AMP', ASETS, arows, astats, {'carbamate-hydrolysis': 'R4', 'AMP-dissociation': 'R5'}, amp_basis)
AFIT = [(r'$k_{\mathrm{AMP,w}}$ at 313.15 K',4), (r'$b_{\mathrm{AMP,w}}$ (K)',3), (r'$k_{\mathrm{AMPH^+,w}}$ at 313.15 K',4), (r'$b_{\mathrm{AMPH^+,w}}$ (K)',3), (r'$k_{\mathrm{AMPH^+,CO_2}}$',4),
        (r'$\sigma_{\mathrm{AMPH^+}}$ (\AA)',4), (r'$\sigma_{\mathrm{AMPCOO^-}}$ (\AA)',4), (r'R4 constant term $A_4$',4), (r'R4 enthalpy increment $\delta h$ (J/mol)',1)]
r4, r4shift = {}, {}
mea_stage = read(MEAFIT + 'objective-information.json.gz')['result']
for amine_name in ('dea', 'amp'):
    shift = read(f'analyses/{amine_name}_transfer/results/salt-anchored-435/hydrolysis/shift.json')
    temperatures = {r['T_K']: r for r in shift['temperatures']}
    at_reference = temperatures[313.15]
    uncertainty, coordinates = (get_fit(DEA, 'DEA/information.json.gz') if amine_name == 'dea' else (aunc, acoords))
    level_key, enthalpy_key = (('hydrolysis-a', 'hydrolysis-enthalpy-shift') if amine_name == 'dea' else
                               ('AMP-hydrolysis-a', 'AMP-hydrolysis-enthalpy-increment'))
    r4[amine_name] = dict(shift, delta_ln_K4=at_reference['delta_ln_K4'], SE_ln_K4=coordinates[level_key]['error'],
                          SE_h_J_mol=coordinates[enthalpy_key]['error'])
    r4shift[amine_name] = {T: dict(r, SE_ln_K4=r['conditional_SE_ln_K4']) for T, r in temperatures.items()}
    if amine_name == 'dea':
        dcoords = coordinates
        dflat = flatten(read(DEA + 'selection.json.gz')['chosen']['parameters'],
                        {'diethanolamine', 'protonated-diethanolamine', 'carbamate-anion'})
        dflat.update({key: (r['value'], params[i]['unit']) for i, (key, r) in enumerate(dcoords.items())})
        fit_rows[1:1] = [[label + (' (J/mol)' if i == 3 else ''), bold(num(r['value'], d)), num(r['error'], d),
                          bounds(*r['bounds'], d), ''] for i, (label, r) in enumerate(zip(fitted_names, dcoords.values(), strict=True))
                         for d in [0 if i == 3 else 3]]
acoords[aorder[-1]].update(value=r4['amp']['delta_h_J_mol'], bounds=r4['amp']['bounds']['enthalpy'])
fit_rows += [head('AMP', 5)] + [[label, bold(num(r['value'], d) + (r'\textsuperscript{a}' if r['on_bound'] else '')),
                                '---' if r['on_bound'] else num(r['error'], d), bounds(*r['bounds'], d), '']
                               for (label, d), key in zip(AFIT, aorder, strict=True) for r in [acoords[key]]]
level = lambda q: [r'R4 change at 313.15 K, $\Delta\ln K_4$\textsuperscript{c}', f"${q['delta_ln_K4']:+.3f}$", num(q['SE_ln_K4'], 3), bounds(*q['bounds']['level'], 3), '']
assert fit_rows[4][0].startswith('R4 enthalpy increment') and fit_rows[-1][0].startswith('R4 enthalpy increment')
fit_rows[4][1:4] = [bold(num(r4['dea']['delta_h_J_mol'], 0)), num(r4['dea']['SE_h_J_mol'], 0), bounds(*r4['dea']['bounds']['enthalpy'], 0)]
fit_rows.insert(4, level(r4['dea']))
fit_rows.insert(len(fit_rows) - 1, level(r4['amp']))
# fit_rows: name, value, standard error, bounds and an unused fifth cell. The main text omits the bounds; the supplement lists them.
columns = lambda n, keep: [[r[0].replace('multicolumn{5}', 'multicolumn{' + str(n) + '}')] if len(r) == 1 else keep(r) for r in fit_rows]
# Table 7 gives the level change of R4 at 313.15 K in a footnote to the constant term; the supplement's bounds table keeps it as a row.
main_fit = [r for r in columns(3, lambda r: [r[0].replace('R4 constant term $A_4$', r'R4 constant term $A_4$\textsuperscript{b}'), r[1], r[2]]) if not r[0].startswith('R4 change')]
level_note = ' and '.join(f"${r4[k]['delta_ln_K4']:+.3f}\\pm{r4[k]['SE_ln_K4']:.3f}$ for {k.upper()}" for k in ('dea', 'amp'))
table('transfer-fitted', 'Fitted parameters of the DEA, MDEA and AMP models with conditional standard errors.', ['Parameter','Value','Standard error'], main_fit, [.52,.20,.20],
      notes=r'Bold: fitted in this work. \textsuperscript{a}On a bound; no standard error is assigned. DEA and AMP: $\delta h$ is measured from the starting R4 correlation of Table~\ref{tab:reaction-equilibrium-constants}, and the final R4 coefficients include it (Table~\ref{supp-tab:supplement-transfer-parameters}). \textsuperscript{b}Expressed relative to the starting correlation, the fitted constant term changes $\ln K_4$ at \SI{313.15}{\kelvin} by ' + level_note + r', with the standard error of $A_4$; this change is not a further parameter. MDEA: $k_{\mathrm{MDEA,w}}$ is held at the upper bound that keeps the \COtwo-free MDEA--water solution free of a calculated liquid--liquid gap at \SI{1.466}{\mega\pascal} (Section~\ref{sec:methods-phase}), and $k_{\mathrm{MDEAH^+,HCO_3^-}}$ is at its upper bound; the other standard errors are conditional on both. AMP: $\sigma_{\mathrm{AMPCOO^-}}$ and $\delta h$ are at their lower bounds, and the other standard errors are conditional on both. The standard errors follow Eq.~\eqref{eq:conditional-covariance}. Table~\ref{supp-tab:supplement-transfer-bounds} gives the bounds.')
table('supplement-transfer-bounds', 'Bounds of the fitted parameters of the DEA, MDEA and AMP models.', ['Parameter','Lower bound','Upper bound'], columns(3, lambda r: [r[0].replace(r'\textsuperscript{c}', ''), *r[3][1:-1].split(', ')]), [.50,.20,.20],
      notes=r'The parameters are those of main-text Table~\ref{main-tab:transfer-fitted}. For DEA and AMP the bounds of $\delta h$ and of $\Delta\ln K_4$ are measured from the starting R4 correlations, like the values of that table.')
apure, ROLE = read(AM344 + 'pure-binary-on-05e94210.json')['pure'], {'fitted': 'fitted', 'assessment_not_fitted': 'not fitted'}
data_rows.append(head('AMP, pure component', 11))
for key, who in [('Klepacova2011', r"Klep\'a\v{c}ov\'a et al.\ \cite{klepacovaVaporPressuresSeveral2011}"), ('Belabbaci2010', r'Belabbaci et al.\ \cite{belabbaciInvestigationIsothermalVapour2010}'), ('Pappa2006', r'Pappa et al.\ \cite{pappaMeasurementThermodynamicModeling2006}'), ('Ayad2023', r'Ayad et al.\ \cite{ayadMeasurementsModelingThermodynamic2023}')]:
    g, t = apure['groups'][key], [r['T_K'] for r in apure['rows'] if r['campaign'] == key]
    assert g['n'] == len(t), key
    data_rows.append([who, g['metric'], ROLE[g['role']], str(g['n']), span(t, lambda v: num(v,2)), 'pure AMP', '---', '---', '---', *([num(g['AARD_percent'],2), num(g['signed_relative_bias_percent'],2)] if 'AARD_percent' in g else [r'---\textsuperscript{b}', '---'])])
comparison_paths = {
    'DEA': DEA + '../matched-deviations-campaign.json',
    'MDEA': MDEA + '../matched-deviations-campaign.json',
    'AMP': AMP + '../matched-deviations-free.json',
}
comparison_scores = {}
for who, path in comparison_paths.items():
    for record in read(path)['groups']:
        if who == 'DEA':
            key = name(record['group'], cite=True)
        else:
            sets = MSETS if who == 'MDEA' else ASETS
            group = record['group'] + ('-y' if who == 'AMP' and record['group'] == 'binary' and record['unit'] != 'Pa' else '')
            title, cite, _ = sets[group]
            key = title + r' \cite{' + cite + '}'
        comparison_scores[who, key] = record

transfer_rows = []
for row in data_rows:
    if len(row) == 1:
        who = re.search(r'textit\{([^}]*)\}', row[0])[1]
        transfer_rows.append([row[0].replace('multicolumn{11}', 'multicolumn{12}')])
    else:
        record = comparison_scores.get((who, row[0]))
        prior = record['matched_prior'] if record and (record['unavailable_new'] or record['unavailable_prior']) else record['prior'] if record else None
        value = num(prior['AARD_percent'], 2) if prior else '---'
        if prior and (record['unavailable_new'] or record['unavailable_prior']):
            value = num(record['matched_new']['AARD_percent'], 2) + ' / ' + value
        shown = [*row, value]
        shown[2] = shown[2].replace('comparison', r'com\-parison')
        transfer_rows.append(shown)
table('supplement-transfer-data', 'Data for DEA, MDEA and AMP with their roles in the fit of each model, their ranges, and the deviations of the DEA, MDEA and AMP models.', DATA_HEAD + ['AARD (\\%), MEA-fitted set'], transfer_rows, [.15,.085,.08,.035,.08,.084,.086,.05,.05,.057,.07,.075], long=True, size=r'\footnotesize',
      notes=r'The last column gives the AARD of the fit made with the MEA-fitted shared set, for AMP the fit to the extended data with the slope $b_{\mathrm{AMPH^+,w}}$ fitted. Where the two fits could not be calculated at the same observations, it gives both AARDs on the common observations, the reported model first. $N$: number of observations; in parentheses, the number with a calculated value and a defined relative deviation. Amine content: that of the unloaded solution, or a mole fraction for the \COtwo-free binary sets ($x_{\mathrm{w}}$: water; $x_{\mathrm{A}}$: amine). R4 and R5: in, out or mixed relative to the source temperature range of that equilibrium constant, which for the AMP R4 is a range of model-derived estimates (main-text Table~\ref{main-tab:reaction-equilibrium-constants} and Section~\ref{main-sec:data-roles}); ---: not reported in the source, or the calculation uses no such reaction. AARD and bias follow main-text Eq.~(\ref{main-eq:aard}). Tables~\ref{tab:supplement-dea-ranges}--\ref{tab:supplement-amp-ranges} give the deviations inside and outside each range, and Section~\ref{sec:s-corrections} gives the source conventions. \textsuperscript{a}Mole fraction of added \COtwo. DEA: the water--DEA interaction was fitted beforehand to the 365.15 K vapor--liquid equilibria of Horstmann et al.\ \cite{horstmannPhaseEquilibriumExcess2002}, which are not listed; the pressures not fitted were inspected before the choice between the two DEA solutions whose objective values agree within the optimizer tolerance. MDEA: the Xiao et al.\ and Ermatchkov et al.\ pressures were used to choose the initial MDEA parameter set but are not in the objective. Pure component: deviations at the fixed pure-AMP parameters, whose fit preceded the reactive fit; \textsuperscript{b}the errors of the three fitted densities are ' + ', '.join(num(e, 3) for e in apure['groups']['Ayad2023']['errors_kg_m3']) + r' kg/m$^3$.')
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
f2, f2se = ({r['identity']: float(r[k]) for r in read(MEA + 'reduced-refit/parameter-details.csv') if r['fit'] == 'F2' and r[k]} for k in ('value', 'conditional_SE'))
prior_f2 = f2.copy()
prior_f2se = {k: v * stage['MEA']['SE_multiplier'] for k, v in f2se.items()}
shared_fit = read(SALT + 'shared-parameters.json')
f2.update({'component/carbamate-anion/segment_diameter': shared_fit['carbamate']['sigma'],
           'component/carbamate-anion/dispersion_energy_over_k': shared_fit['carbamate']['epsilon']})
f2.update({r['identity']: r['value'] for r in mea_stage['coordinates']})
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
      notes=r'The columns are those of Table~\ref{tab:species-parameters}. Bold: fitted in this work; in a row of this work, the values in normal weight are fixed; --: not used. \textsuperscript{a}DEA values, with zero self-association energy. \textsuperscript{b}Dispersion energy of \ce{MEACOO-} in the MEA model and its diameter scaled to DEA (Section~\ref{supp-sec:s-parameters}). \textsuperscript{c}Segment parameters of Ref.~\cite{Pahlavanzadeh2013} and association parameters of Ref.~\cite{Uyan2015}; association volume converted in this work. \textsuperscript{d}Segment count and association volume of MDEA; zero self-association energy. \textsuperscript{e}Fitted beforehand to pure-AMP data. \textsuperscript{f}Dispersion energy of AMP. \textsuperscript{g}Dispersion energy of \ce{MEACOO-} in the MEA fit with the MEA-fitted shared set; diameter fitted, with the \ce{MEACOO-} diameter of that fit as its lower bound. Table~\ref{tab:transfer-fitted} gives the standard errors of the values fitted in the reactive fits, and Table~\ref{supp-tab:supplement-transfer-parameters} unrounded values and the remaining inputs.')
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
        assert record[key][0] == prior_f2['component/' + key if last == 'dispersion_energy_over_k' else 'pair/' + key]
        return r'\ce{MEACOO-}, MEA-fitted set'
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
assert dcoords['hydrolysis-enthalpy-shift']['value'] == 0
rows[ddh][:2] = [r'R4, enthalpy increment $\delta h$, contained in $B_4$', bold(f"${r4['dea']['delta_h_J_mol']!r}$")]
adh = r4['amp']['delta_h_J_mol']
rows.append([r'R4, enthalpy increment $\delta h$, contained in $B_4$', bold(f'${adh}$'), 'J/mol', 'This work'])
table('supplement-transfer-parameters', 'Amine-specific parameter values of the DEA, MDEA and AMP models at full precision.', ['Parameter','Value','Unit','Source'], rows, [.45,.24,.07,.21], long=True,
      notes=r'Bold values were fitted in this work; Table~\ref{main-tab:transfer-fitted} of the main text gives the standard errors of the parameters of the reactive fits, and Table~\ref{tab:supplement-transfer-bounds} their bounds. For DEA, the R4 coefficients $A_4$ and $B_4$ are the final coefficients after the fit, not additional independent fitted parameters. For DEA and AMP, $\delta h$ is measured from the starting R4 correlation, as in main-text Table~\ref{main-tab:transfer-fitted}, and is contained in $B_4$. R4: carbamate hydrolysis; R5: amine dissociation; $\ln K=a+b/T+c\ln(T/T_{\mathrm{ref}})+dT$ with $T$ in K and $T_{\mathrm{ref}}=313.15$ K, on the common-molality reference basis; coefficients not listed are zero. For R4, where $c=d=0$, $a$ and $b$ are written $A_4$ and $B_4$: they are the coefficients of main-text Eq.~(\ref{main-eq:reaction-equilibrium-constant-temperature}) on that basis, with $\Delta_4=0$. Binary dispersion interactions not listed are zero; a $k_{ij}$ with a slope is the value at 313.15 K, except MDEA--water, at 423 K. Each of the chain cations DEAH$^+$ and MDEAH$^+$ keeps the dispersion between its own segments. ``DEA value\textquotedblright{} and ``MDEA value\textquotedblright{}: the value of the molecular amine. The data deposit gives the source and basis of each value.')
def pressure_points(filename, rows, panels, shape):
    fig, axes = plt.subplots(*shape, figsize=(6.48, 2.25 * shape[0]), constrained_layout=True)
    for ax, (title, groups, loading_of, observable) in zip(axes.flat, panels, strict=True):
        part = [r for r in rows if r['group'] in groups]
        assert part, title
        for role, filled in [('fitted', True), ('not fitted', False)]:
            observed = [r for r in part if r['role'] == role]
            if observed:
                ax.scatter([loading_of(r) for r in observed], [r['observed']/1000 for r in observed],
                           s=14, edgecolors=colors[0], facecolors=colors[0] if filled else 'none',
                           label=f'Measured, {role}')
        available = [r for r in part if r['status'] == 'Available']
        ax.scatter([loading_of(r) for r in available], [r['value']/1000 for r in available],
                   s=14, marker='x', color=colors[1], label='Model')
        ax.set(title=title, xlabel='Loading (mol CO$_2$/mol amine)', ylabel=observable, yscale='log')
        ax.legend(fontsize=6)
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
esearch = read(MEAFIT + 'search-summary.json')
dnew = read(DEA + 'selection.json.gz')['chosen']['search']['grid']
mnew = read(MDEA + 'search-outcome.json.gz')
anew = read(AMP + 'native/search-outcome.json.gz')
apair = read(AMP + '../matched-deviations-free.json')
matched_amp = {r['group']: r for r in apair['groups'] if r['unit'] == 'Pa'}
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

e47 = cell(pressure_stats([r for r in mea_fit if r['quantity'] == 'PartialPressure'], 'predicted'))
enot = [r for r in mea_pressure if r['target'] not in fitted_pressure] + read(MEAEVIDENCE + 'wagner-pressure.csv') + read(MEAEVIDENCE + 'transfer.csv')
dloaded = {'Lawson', 'Lawson-394K', 'SeoHong', 'Lal', 'Lawson-VIII'}
doutside = [r for r in data if r['group'] in dloaded and r['role'] == 'not fitted']
d47 = cell(dev['Lawson'])
ephase = [esearch[k] for k in ('grid', 'offset', 'census')]
amp_loaded = {'loaded-pressure', 'hartono-2021-supplemental', 'tong'}
rows = [
    ['MEA', len(mea_stage['coordinates']), len(mea_stage['active_bounds']), e47, e47,
     cell(pressure_stats(enot, 'predicted')), sum(q['states'] for q in ephase), sum(q['states']-q.get('available', q['states']-q.get('incomplete', 0)) for q in ephase), 0],
    ['DEA', len(dcoords), sum(r['on_bound'] for r in dcoords.values()), d47, d47, cell(pressure_stats(doutside)),
     *search_summary(dnew, sum(dnew['liquid_liquid_splits'].values()))],
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
for label, case in [('Reported shared set, slope fitted (AMP model)', AMP), ('Reported shared set, slope fixed at $-150$ K', AMP_FIXED)]:
    fit = read(case + 'selection.json.gz')
    paired = read(case + 'paired-expanded-scores.json.gz')
    family = case.rstrip('/').split('/')[-1]
    for arm in ('new', 'prior'):
        selected_rows = [r['prediction'] for r in paired[arm]['rows'] if r['group'] in amp_loaded]
        assert len(selected_rows) == 105
        loaded_score = pressure_stats(selected_rows)
        model_name = label if arm == 'new' else 'MEA-fitted shared set, slope ' + {'free': 'fitted', 'fixed': 'fixed at $-150$ K'}[family]
        outcome = [read(case + protocol + '/search-outcome.json.gz') if arm == 'new' else
                   read(round5 + f'search-{family}-{protocol}-full.json.gz') for protocol in ('native', 'supplied')]
        amp_sensitivity.append([model_name, num(fit['cost'] if arm == 'new' else fit['prior_expanded_cost'], 4),
                                cell(loaded_score),
                                *[f"{q['tally']['descent']}/{q['tally']['states']}" for q in outcome]])
table('supplement-amp-expanded', 'AMP fits to the extended data, 214 observations, with the temperature slope of the \\ce{AMPH+}--water interaction fitted or fixed.', ['Fit', 'Objective', 'Loaded total pressures, AARD (\\%) ($N$)', 'Instabilities, search trials', 'Instabilities, supplied trials'],
      amp_sensitivity, [.34,.11,.21,.13,.13],
      notes=r'Instabilities: states with a detected instability of the number searched, with the trial phases of the search alone and with the supplied trial compositions added. The objectives of fits with different shared sets are not comparable. The splits of main-text Fig.~\ref{main-fig:amp-splits} belong to the fit to the first data, with the MEA-fitted shared set.')
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
table('supplement-phase-replays', 'Two-liquid calculations at fixed feed, temperature and pressure for MDEA and AMP.', ['Fit', 'Pressure (MPa)', 'Outcome'],
      [['MDEA, MEA-fitted shared set', num(fixedp['P_Pa']/1e6, 3), fixedp['outcome']],
       ['MDEA model', num(new_fixed['P_Pa']/1e6, 3), new_fixed['outcome']],
       *[[name, num(common['common_Pa']/1e6, 6),
          f"{sum(a['confirmed'] for a in common['outcomes'][case]['attempts'])} confirmed of {len(common['outcomes'][case]['attempts'])} attempted splits"]
         for case, name in [('free', 'AMP model'),
                            ('prior-free', 'AMP, MEA-fitted shared set, slope fitted'),
                            ('fixed', 'AMP, reported shared set, slope fixed at $-150$ K'),
                            ('prior-fixed', 'AMP, MEA-fitted shared set, slope fixed at $-150$ K')]]],
      [.42,.19,.32], notes=r'MDEA: the state of Section~\ref{sec:s-phase} at which the fit with the MEA-fitted shared set has a confirmed split. AMP: the four fits to the extended data at the feed and temperature of the worked split of Table~\ref{tab:amp-reference-state}, at one pressure above the bubble pressure of each fit.')
target = LATEX / 'tables/supplement-amp-ranges.tex'
outputs[target] += outputs.pop(LATEX / 'tables/supplement-phase-replays.tex')
# The same four fits made with the MEA-fitted shared set, from their retained scores on the same observations.
sb0 = read('analyses/mdea_mea_workflow/results/shared-bicarbonate-417/mdea-comparison.json.gz')
mold = lambda *gs: (lambda cs: cell(dict(AARD_percent=sum(c['relative_rows'] * c['AARD_percent'] for c in cs) / sum(c['relative_rows'] for c in cs), rows=sum(c['relative_rows'] for c in cs))))([sb0[g]['original'][0] for g in gs])
eold = lambda *gs: (lambda cs: num(sum(a * n for a, n in cs) / sum(n for a, n in cs), 2) + f' ({sum(n for a, n in cs)})')([escore[g] for g in gs])
eoldsearch = [read(MEA + 'paper-evidence-341/stability/candidate/search.json')[k] for k in ('grid', 'offset', 'census')]
aprior = [dict(r['prediction'], role=r['role']) for r in read(AMP + 'paired-expanded-scores.json.gz')['prior']['rows']]
apriorsearch = read(round5 + 'search-free-native-full.json.gz')['tally']
assert mold('Kuranov') == cell(sb0['Kuranov']['original'][0]) and len(aprior) == len(arows)
rows += [['MEA', '', '', eold('47 current-fitted pressures'), eold('47 current-fitted pressures'), eold('112 current-not-fitted pressures', 'Wagner pressures', 'Aronu 15 wt% pressures', 'Aronu 45 wt% pressures'),
          sum(q['states'] for q in eoldsearch), sum(len(q['unavailable']) if 'unavailable' in q else q['incomplete'] for q in eoldsearch), sum(q['descent'] for q in eoldsearch)],
         ['DEA', '', '', cell(dsum['pressure']['fitted']), cell(dsum['pressure']['fitted']), cell(dsum['pressure']['not fitted']), dsum['stability']['grid']['states'], len(dsum['stability']['grid']['unavailable']), sum(dsum['stability']['grid']['liquid_liquid_splits'].values())],
         ['MDEA', '', '', mold('Kuranov'), mold('all pressures fitted'), '$P$: ' + mold('corrected-Kamps', 'Kuranov-413K', 'Sedighi') + r'; $p_{\COtwo}$: ' + mold('Ermatchkov', 'Xiao'), msearch['states'], msum['unavailable_searches'], msum['liquid_liquid_splits_found']],
         ['AMP', '', '', *pressure_columns(aprior, amp_loaded, {'tong-baseline'}, {'kundu'}), apriorsearch['states'], len(apriorsearch['unavailable']), apriorsearch['descent']]]
for row in rows: row[3] = {'MEA': r'$p_{\COtwo}$', 'DEA': r'$p_{\COtwo}$', 'MDEA': '$P$', 'AMP': '$P$'}[row[0]] + ': ' + row[3]  # fitted loaded-solution observable: Hilliard/Jou and Lawson-Garst partial, Kuranov and Hartono total pressures
for row in rows:
    if row[0] in ('MEA', 'DEA'): row[5] = r'$p_{\COtwo}$: ' + row[5]  # every MEA and DEA pressure not fitted is a CO2 partial pressure (Tables 5 and S8)
rows.insert(4, head('The same fits with the MEA-fitted shared set', 9))
table('amine-summary', 'The four reported models and the same fits made with the MEA-fitted shared set.', ['Model','Fitted parameters','On bounds',r'Fitted loaded-solution pressures\textsuperscript{a}',r'All fitted pressures\textsuperscript{b}',r'Pressures not fitted\textsuperscript{c}','Searches','Searches not completed',r'Liquid--liquid splits found\textsuperscript{d}'], rows, [.09,.08,.06,.14,.10,.15,.08,.10,.105],
      notes=r'Pressure columns: AARD (Eq.~\eqref{eq:aard}) in \%, with the number of observations $N$ in parentheses. \textsuperscript{a}Fitted \COtwo partial pressures ($p_{\COtwo}$) of loaded MEA and DEA and fitted total pressures ($P$) of loaded MDEA and AMP. \textsuperscript{b}Column a with the fitted \COtwo-free bubble pressures of MDEA--water and AMP--water; neither column includes the fitted \COtwo--water pressures of Kiepe et al.\ in the MEA objective (Table~\ref{tab:mea-data}). \textsuperscript{c}MEA: all pressures not fitted, those at nominal 30 wt\% of the six sources of Table~\ref{tab:mea-data}, those of Wagner et al.\ and those at 15 and 45 wt\%; MDEA and AMP: total pressures and \COtwo partial pressures separately, the AMP total pressures including the 5 \COtwo-free bubble pressures of Tong et al. The lower block repeats each fit with the shared water--bicarbonate interaction fitted to the MEA data and the water--carbonate interaction of Held et al.\ \cite{Held2014}, on the same observations and with the same number of fitted parameters; its AMP fit uses the extended data. \textsuperscript{d}In the searches of each fit, which are finite and differ in design between the amines (Section~\ref{supp-sec:s-phase}), so the counts do not measure equal coverage and split counts are lower bounds.')
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
table('supplement-dea-binary', 'DEA fit with a constant water--DEA interaction against a refit with a temperature-dependent interaction, both with the MEA-fitted shared set, on identical observations.', ['Observations', '$N$', 'Role, constant interaction', 'Role, refit', r'AARD (\%), constant interaction', r'AARD (\%), refit'],
      [[label, dpair[g, r]['reference']['rows'], a413, a425, num(dpair[g, r]['reference']['AARD_percent'], 2), num(dpair[g, r]['candidate']['AARD_percent'], 2)] for g, r, label, a413, a425 in DPAIR], [.40, .05, .14, .14, .11, .10],
      notes=r'AARD follows main-text Eq.~\eqref{main-eq:aard}. Constant interaction: the water--DEA interaction of the DEA model, fitted beforehand to the bubble pressures of Horstmann et al. Refit: a water--DEA interaction with a temperature coefficient fitted beforehand to those pressures, the excess enthalpies and the bubble pressures of Cai et al., followed by a reactive fit of the same four parameters to the same data. The excess enthalpies are negative and their relative deviations large because the constant interaction gives the wrong sign. The pressures outside the reactive fit were examined during development.')
# Calibration data by amine: the sets of each objective, the sets fitted beforehand and the sets outside the objective that informed a choice.
mea_T = {r['identity']: float(r['row']['T_K']) for r in read(MEA + 'paper-evidence-341/objective-declarations.json') if r['group'] in ('Jakobsen', 'CO2-free density')} | {r['target']: float(r['temperature_K']) for r in read(P341 + 'state-targets.csv')} | {r['id']: float(r['T_K']) for f in ('density.csv', 'heat.csv', 'cp.csv') for r in read(P341 + f)}
MEA_SETS = [(r'$p_{\COtwo}$', 'Hilliard2008,Jou1995', lambda r: r['quantity'] == 'PartialPressure'), ('species mole fractions', 'Bottinger2008,matinFacileMethodDetermination2012', lambda r: r['quantity'] in ('PhaseMoleFraction', 'mole_fraction') and r['group'] != 'Cai'),
            ('species per total amine', 'Jakobsen2005', lambda r: r['group'] == 'Jakobsen'), ('integral heat', 'HemaBhavya2025', lambda r: r['quantity'] == 'AdditionEnthalpy'), ('heat capacity', 'Hilliard2008', lambda r: r['group'] == 'Cp'),
            ('loaded density', 'Amundsen2009,Hartono2014', lambda r: r['group'] == 'loaded density'), (r'\COtwo-free density', 'Amundsen2009', lambda r: r['group'] == 'CO2-free density'),
            ('MEA--water bubble temperature and vapor composition', 'caiBinaryIsobaricVaporLiquid1996', lambda r: r['group'] == 'Cai'), (r'\COtwo--water pressure', 'kiepeExperimentalDeterminationPrediction2002', lambda r: r['group'] == 'Kiepe')]
tspan = lambda t: span(t, lambda v: num(v, 2))
design, mea_n = [head('MEA', 5)], 0
for label, cite, choose in MEA_SETS:
    rs = [r for r in mea_fit if choose(r)]
    t = cai_T if cite.startswith('cai') else [float(r['id'].split('-')[1]) for r in rs] if cite.startswith('kiepe') else [mea_T[r['id']] for r in rs if r['id'] in mea_T]
    assert rs and len(t) in (len(rs), len(rs) // 2), label
    design.append([label, r'\cite{' + cite + '}', len(rs), tspan(t), 'fitted'])
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
assert D425['tableS10'][12]['group'] == 'Horstmann VLE' and len(arcis) == 14 and objective_n == {'MEA': 307, 'DEA': 80, 'MDEA': 281, 'AMP': 214}, objective_n
table('calibration-data', 'Data in the objective of each model, data fitted beforehand and data outside the objective that informed a choice.', ['Observable', 'Source', '$N$', '$T$ (K)', 'Role'], design, [.36, .16, .07, .19, .18],
      notes=r'Fitted: in the objective of the reported fit, ' + ', '.join(f'{n} observations for {k}' for k, n in objective_n.items()) + r'. Fitted beforehand: used to set a parameter that the reactive fit holds fixed. \textsuperscript{a}Development: outside the objective, but used to choose the parameters or the initial parameter set (Section~\ref{sec:data-roles}). $p_{\COtwo}$: \COtwo partial pressure; total pressure: bubble pressure of the loaded solution. Table~\ref{tab:mea-data} and Table~\ref{supp-tab:supplement-transfer-data} give the compositions, loadings and deviations of every set, including those that are neither fitted nor used for a choice.')
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
rows.append(['This work, MEA model', 'not fitted', num(baygi['salt_anchored_Pa'], 2)])
mpub = read(MD + 'published-pressure-comparisons.json')['comparisons']
ZHANG_CHEN = r'Zhang and Chen, eNRTL \cite{zhangThermodynamicModelingCO22011}'  # their Table 14: AARD 6.8 % on the 82 Kuranov total pressures and 17.7 % on the 101 Ermatchkov CO2 partial pressures, both in their regression
for c in mpub:
    rows += [head(f"{c['measured_rows']} " + SHARED[c['group']], 3)] + [['Ermatchkov et al., parameter set ' + q['set'], {'predicted': 'not fitted'}.get(q['data_role'], q['data_role']), f"${q['mean_absolute_relative_deviation_percent']:g}$"] for q in c['published_parameter_sets']]
    if c['group'] == 'Ermatchkov': rows.append([ZHANG_CHEN, 'fitted', '$17.7$'])
    rows.append(['This work, MEA-fitted shared set', c['data_role'] + ('; used to choose the initial parameters' if c['group'] == 'Ermatchkov' else ''), num(c['selected_point_mean_absolute_relative_deviation_percent'], 2)])
    rows.append(['This work, MDEA model', c['data_role'], num(mstats[c['group']]['R1']['False']['AARD_percent'], 2)])
K422 = 'analyses/mdea_mea_workflow/results/kuranov-published-422/'
kstat, krae = read(K422 + 'statistics.json'), read(K422 + 'raeispour-table-4.json')
kroles = collections.Counter(r['role'] for r in mrows if r['group'] in ('Kuranov', 'Kuranov-binary'))
assert {('Uyan', '22.9'), ('Uyan', '34.4'), ('Wangler', '19.7')} <= {(r['reading'], r['printed']) for r in kstat['reconstruction'] if r['subset'] == 'K82'}
assert (krae['rows'], krae['AARD_percent'], krae['role']) == (82, 10.9, 'fitted') and kstat['present']['K82']['n'] == kstat['present']['K82']['solved'] == 82 and kroles == {'fitted': 70}
k82 = read(MDEA + '../kuranov-matched-pressure.json.gz')['grouped']['K82']['salt_anchored']
assert k82['solved'] == k82['n'] == 82
rows += [head(r'82 total pressures of Kuranov et al.\ \cite{kuranovSolubilitySingleGases1996}, MDEA\textsuperscript{b}', 3),
         [r'Uyan et al., ePC-SAFT \cite{Uyan2015}', 'not fitted', r'$22.9$\textsuperscript{c}'], [r'Wangler et al., ePC-SAFT \cite{Wangler2018}', 'not fitted', '$19.7$'],
         [r'Raeispour Shirazi and Lotfollahi, ePC-SAFT \cite{raeispourshiraziApplicationEPC_SAFTMBEoS2020}', 'fitted', f"${krae['AARD_percent']:g}$"], [ZHANG_CHEN, 'fitted', '$6.8$'],
         ['This work, MEA-fitted shared set', r'70 fitted, of which 4 \COtwo-free; 12 not fitted', num(kstat['present']['K82']['AARD_percent'], 2)],
         ['This work, MDEA model', r'70 fitted, of which 4 \COtwo-free; 12 not fitted', num(k82['AARD_percent'], 2)]]
table('published-models', r'Pressure deviations of published models and of this work on the same observations, identified for the Kuranov pressures by their count\textsuperscript{b}.', ['Observations and model', 'Role of these observations in the fit of that model', r'AARD (\%)'], rows, [.50,.36,.10],
      notes=r'AARD follows Eq.~\eqref{eq:aard} over the stated observations. Published values are those reported in each source, with the digits given there; the values of this work are calculated for the same observations. The 16-parameter calibration is defined in Section~\ref{sec:parameters}. Parameter sets I and II are the two sets of interaction parameters of Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}. \textsuperscript{a}Najafloo and Zarei do not define their average absolute deviation; it is assumed equivalent to Eq.~\eqref{eq:aard}, and their methods and conclusions describe the fitting differently. \textsuperscript{b}The published values are identified with the 82 total pressures of Table~2 of Kuranov et al.\ by their count. \textsuperscript{c}Recalculated as 34.4\,\% by Wangler et al.\ \cite{Wangler2018}.')
# Published parameters of Hong et al. on identical MEA observations: retained scores, no model call.
HONG = MEA + 'same-data-comparison/hong-2027/'
hong, hchecks = read(HONG + 'supplement-table.csv'), read(HONG + 'checks.json')
hsets = [(r'\COtwo partial pressure, AARD (\%)', [('canonical', 'strict grid', 'Six sources, inside the fitted range of Hong et al.'), ('canonical', 'all', 'Six sources, with the 13 Hilliard observations at 313.00--313.147 K'), ('wagner', 'all', 'Wagner et al.')]),
         (r'Heat of Kim and Svendsen, RMSE (kJ/mol \COtwo)', [(f'Kim {T} K', 'all', f'{T} K' + mark) for T, mark in (('313.15', r'\textsuperscript{a}'), ('353.15', r'\textsuperscript{a,b}'), ('393.15', ''))]),
         (r'Loaded-solution density, RMSE (kg/m$^3$)', [(b, 'all', label + r'\textsuperscript{c}') for b, label in (('Amundsen2009', 'Amundsen et al.'), ('Hartono2014', 'Hartono et al.'), ('Han2012', 'Han et al.'))])]
hong_pressures = read(SALT + 'MEA/hong-matched-pressure.json')['grouped']
hrows = []
for heading, sets in hsets:
    hrows += [head(heading, 9)]
    for block, subset, label in sets:
        rs = [r for r in hong if (r['block'], r['subset']) == (block, subset)]  # two rows where Hong's slope is taken on both sides of a node
        r, fitted = rs[0], int(rs[0]['adopted_fitted'])
        assert rs and len({(q['n'], q['adopted'], q['polley_hedengren_2026'], q['locally_unstable']) for q in rs}) == 1 and {q['hong_role'] for q in rs} == {'not fitted'}
        if block in hong_pressures:
            match = hong_pressures[block][subset.replace(' ', '_')]['salt_anchored']
            assert match['available'] == int(r['n'])
            adopted = match['aard_percent']
        else:
            heat = block.startswith('Kim')
            observations = read(HONG + block + '.csv')
            predictions = read(MEAEVIDENCE + ('kim2007-heat-pathways/kim-heat.csv' if heat else 'density.csv'))
            keyed = {q['record_id' if heat else 'id']: q for q in predictions}
            observed, predicted = ('observed', 'predicted') if heat else ('observed_kg_m3', 'predicted_kg_m3')
            pairs = [(q, keyed[q['record_id']]) for q in observations if q['three_model_eligible'] == 'True']
            assert len(pairs) == int(r['n'])
            assert all(math.isclose(float(q['observed']), float(p[observed]), abs_tol=1e-9) for q, p in pairs)
            adopted = math.sqrt(math.fsum((float(p[predicted]) - float(p[observed])) ** 2 for q, p in pairs)/len(pairs))
        hrows.append([label, r['n'], f"{fitted} fitted / {int(r['n']) - fitted} not fitted" if fitted else 'not fitted', 'not stated' if block == 'canonical' else r['polley_hedengren_2026_role'],
                      ' / '.join(num(q['hong'], 2) for q in rs), num(adopted, 2), num(r['adopted'], 2), num(r['polley_hedengren_2026'], 2), '--' if heading.startswith('Loaded') else f"{r['locally_unstable']} of {r['n']}"])
table('supplement-hong-comparison', r'Deviations of the published parameters of Hong et al.\ \cite{hongModelingCO2Absorption2027}, of the MEA model and of the model of Polley and Hedengren \cite{polleyReactiveEPCSAFTModeling2026} on identical MEA observations at nominal 30 wt\%.',
      ['Observations', '$N$', 'Role in the MEA model', r'Role in \cite{polleyReactiveEPCSAFTModeling2026}', 'Hong et al.', 'MEA model', 'MEA-fitted shared set', r'Ref.~\cite{polleyReactiveEPCSAFTModeling2026}', 'Fails the local test'], hrows, [.21, .035, .13, .09, .105, .10, .09, .08, .085],
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
ax.set(xlabel='Loading (mol CO$_2$/mol AMP)', ylabel='Temperature (K)', xlim=(0, 1.02), ylim=(308, 398))
ax.legend(loc='upper center', bbox_to_anchor=(.5, -.18), frameon=False, ncol=1, handletextpad=.5)
figure(fig, 'amp-splits.pdf')
reported_costs = [mea_stage['rss'] / 2, read(DEA + 'selection.json.gz')['chosen']['cost'], read(MDEA + 'selection.json.gz')['cost'], read(AMP + 'selection.json.gz')['cost'], read(AMP_FIXED + 'selection.json.gz')['cost']]
# Contribution of each fitted data set to the objective of its reported model, from the retained contributions.
CONTRIB = [('MEA', MEAFIT + 'objective-contributions.csv', [
                (r'\COtwo partial pressures', [('common149', 'Pa')]), ('Species mole fractions', [('common149', '1'), ('restored species', '1')]), ('Species ratios of Jakobsen et al.', [('Jakobsen', '1')]),
                ('Integral absorption heats', [('common149', 'J/mol')]), ('Heat capacities', [('Cp', 'J/(mol-feed K)')]), ('Loaded densities', [('loaded density', 'kg/m^3')]), (r'\COtwo-free densities', [('CO2-free density', 'kg/m^3')]),
                ('MEA--water bubble temperatures of Cai et al.', [('Cai', 'K')]), ('MEA--water vapor mole fractions of Cai et al.', [('Cai', '1')]), (r'\COtwo--water pressures of Kiepe et al.', [('Kiepe', 'Pa')])]),
           ('DEA', DEA + 'DEA/contributions.csv.gz', [(r'\COtwo partial pressures', [('Lawson', 'Pa')]), ('Integral absorption heats', [('Carson', 'J/mol CO2')])]),
           ('MDEA', MDEA + 'MDEA/contributions.csv.gz', [
                ('Loaded total pressures of Kuranov et al.', [('Kuranov', 'Pa')]), (r'\COtwo-free pressures of Kuranov et al.', [('Kuranov-binary', 'Pa')]), ('MDEA--water and water pressures of Kim et al.', [('Kim', 'Pa')]),
                ('Species ratios of Jakobsen et al.', [('Jakobsen', '1')]), ('Integral absorption heats', [('Carson', 'J/mol'), ('Merkley', 'J/mol')]), ('Heat capacities', [('Cp', 'J/(mol-feed K)')]),
                ('Loaded densities', [('loaded-density', 'kg/m^3')]), (r'\COtwo-free densities', [('unloaded-density', 'kg/m^3')])]),
           ('AMP', AMP + 'AMP/contributions.csv.gz', [
                (r'Loaded total pressures, 313--353 K', [('loaded-pressure', 'Pa')]), (r'Loaded total pressures of Hartono et al., 373--393 K', [('hartono-2021-supplemental', 'Pa')]), ('Loaded total pressures of Tong et al.', [('tong', 'Pa')]),
                ('AMP--water bubble pressures', [('binary', 'Pa')]), ('AMP--water vapor mole fractions', [('binary', 'dimensionless')]), ('Carbamate fractions', [('nmr', 'dimensionless')])])]
crow, cshare = [], {}
for amine, path, sets in CONTRIB:
    recs = collections.defaultdict(lambda: dict(n=0, cost=0.0))
    for r in read(path):  # one retained row per source; a data set sums its sources
        key = r['group'], ast.literal_eval(r['unit'])[0]
        recs[key] = dict(n=recs[key]['n'] + int(r['n']), cost=recs[key]['cost'] + float(r['cost']))
    total = math.fsum(r['cost'] for r in recs.values())
    assert math.isclose(total, reported_costs[len(crow and [c for c in crow if len(c) == 1])], rel_tol=1e-9), amine
    assert {k for _, keys in sets for k in keys} == set(recs), (amine, set(recs))
    crow.append(head(f'{amine}, objective value {total:.3f}', 4))
    for label, keys in sets:
        n, cost = sum(recs[k]['n'] for k in keys), math.fsum(recs[k]['cost'] for k in keys)
        cshare[amine, label] = 100 * cost / total
        crow.append([label, n, num(cost, 3), num(100 * cost / total, 1)])
table('supplement-objective-contributions', 'Contribution of each fitted data set to the objective value of its reported model.', ['Data set', '$N$', 'Contribution', r'Share (\%)'], crow, [.52, .08, .14, .12],
      notes=r'The objective is that of main-text Eq.~(\ref{main-eq:fit-objective}) with the scales and weights of Tables~\ref{tab:objective-groups} and \ref{tab:transfer-scales}; values of different amines are not comparable.')
# Every start of the four reported fits and of the AMP fit with the fixed slope.
def start_costs(folder, names):
    return [(n, r['initial_cost'], r['final_cost']) for n in names for r in [read(folder + n + '/outcome.json.gz')['report']]]
STARTS = [('MEA', [(n, r['initial_cost'], r['final_cost']) for n in ('F2', 'F4') for r in [read(SALT + f'MEA/{n}/attempt-0.json')]]),
          ('DEA', [(c['name'], None, c['cost']) for c in read(DEA + 'selection.json.gz')['candidates']]),
          ('MDEA', start_costs(MDEA, ('fit-0', 'fit-1', 'fit-2'))), ('AMP', start_costs(AMP, ('incumbent', 'opposite'))),
          (r'AMP, slope fixed at $-150$ K', start_costs(AMP_FIXED, ('incumbent', 'opposite')))]
srow = []
for fit, starts in STARTS:
    best = min(c for *_, c in starts)
    srow += [[fit if i == 0 else '', i + 1, num(c0, 3), f'${c:.12f}$', 'reported' if c == best else ''] for i, (_, c0, c) in enumerate(starts)]
assert all(math.isclose(min(c for *_, c in starts), cost, rel_tol=1e-9) for (_, starts), cost in zip(STARTS, reported_costs)), 'the lowest start is the reported fit'
table('supplement-fit-starts', 'Objective value at the start and at convergence for every start of the reported fits.', ['Fit', 'Start', 'Objective at the start', 'Objective at convergence', ''], srow, [.30, .07, .20, .24, .10],
      notes=r'---: not retained. Every start converged by the function tolerance of $10^{-10}$ in the relative change of the objective. The AMP row with the fixed slope is the sensitivity fit of Section~\ref{sec:s-amp-slope}.')
read('analyses/dea_transfer/results/binary.json')
read(BASE + 'conditional-uncertainty.json')
read(BASE + 'checks.json')
read('analyses/dea_transfer/inputs/part-ii-346/route-current.json')
# Numbers quoted in the prose, recomputed from the retained files read above.
f2 = lambda v: f'{float(v):.2f}'
f1 = lambda v: f'{float(v):.1f}'  # the main text and the highlights give percent deviations to one decimal; tables and the supplement keep two
notfit = [float(r['new']['AARD_percent']) for r in read(DEA + '../matched-deviations-campaign.json')['groups'] if r['role'] == 'not fitted'] + [mstats[g]['R1']['False']['AARD_percent'] for g in ('Ermatchkov', 'corrected-Kamps', 'Kuranov-413K', 'Sedighi', 'Xiao')] + [r['new']['AARD_percent'] for r in matched_amp.values() if r['role'] == 'not fitted']
fitted_mdea = [float((mstats[g]['R1'].get('False') or mstats[g]['R1']['reaction not used'])['AARD_percent']) for g in {r['group'] for r in mrows if r['role'] == 'fitted'} if g != 'Kuranov']  # every fitted MDEA set but the loaded pressures
viii = next(r for r in data if r['identity'] + ':problem' == dsum['stability']['grid']['unavailable'][0])
kur, ermatchkov = mstats['Kuranov']['MDEA-dissociation'], next(c for c in mpub if c['group'] == 'Ermatchkov')
assert hchecks['stable_fixed_vapor']['converged'] == hchecks['stable_fixed_vapor']['tried']
mea, dea, mdea = f1(pressure_stats([r for r in mea_fit if r['quantity'] == 'PartialPressure'], 'predicted')['AARD_percent']), f1(dev['Lawson']['AARD_percent']), f1(mstats['Kuranov']['R1']['False']['AARD_percent'])
amp_groups = [r for r in matched_amp.values() if r['group'] in amp_loaded]
amp, afree_loaded = [f1(sum(r[k]['AARD_percent'] * r[k]['relative_rows'] for r in amp_groups) / 105) for k in ('new', 'prior')]
outside = f'{min(notfit):.1f}--{max(notfit):.1f}'
mcost = [f"{mbounded['data_cost']:.1f}", f"{mcomp['runs']['unbounded-2']['data_cost']:.1f}"]  # the reported fit and the fit without the bound, from one start
mratio = '{:.4f}--{:.4f}'.format(*mstability['descent_witnesses']['bubble_pressure_ratio_range'])  # assigned over calculated bubble pressure at the 27 vapor-directed measured states
ours, theirs = f1(mstats['Ermatchkov']['R1']['False']['AARD_percent']), f"{ermatchkov['published_parameter_sets'][0]['mean_absolute_relative_deviation_percent']:g}"
searched = dsum['stability']['grid']['states']
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
brows = [[PROPS[b['property']], b['band'].capitalize() + ', ' + trange(b) + ' K', BROLE[b['role']], b['n'], f"${float(b['AARD_percent']):.2f}$", f"${float(b['mean_signed_relative_percent']):.2f}$", num(b['previous_AARD'], 2),
          r'\cite{' + ','.join(BAND_CITE[c] for c in b['sources'].split()) + '}']
         for prop in PROPS for band in ('absorber', 'intermediate', 'stripper') for b in [v for (q, bd, _, c), v in bstat.items() if (q, bd, c) == (prop, band, 'all')]]
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
# Original 47-row AMP endpoints remain the source of the historical split evidence.
acost = [read(AMP_FIXED + 'selection.json.gz')['cost']]
aslope, aslope_se = (acoords['AMPH-water-slope'][k] for k in ('value', 'error'))
afixed = read(AMP_FIXED + 'selection.json.gz')['slope_K']
afreecost = read(AMP + 'selection.json.gz')['cost']
aloaded = [sum(float(r['cost']) for r in read(path + 'AMP/contributions.csv.gz')
               if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'tong')) for path in (AMP_FIXED, AMP)]
afk = lambda T: acoords['AMPH-water-k']['value'] + aslope * (1 / T - 1 / 313.15)
amp_main = [f"{WORDS[len(aunc['active_bounds'])].capitalize()} of the {WORDS[len(acoords)]} fitted AMP parameters",
            rf"{amp}\,\%"]
amp_supplement = [rf"\SI{{{AMINES[2][1]['carbamate-anion/dispersion_energy_over_k'][0]:.4f}}}{{\kelvin}}, and its interaction with water, ${AMINES[2][1]['carbamate-anion/water/k_ij'][0]:.4f}$",
                  f"{prior_f2se['pair/carbamate-anion/water/k_ij']:.4f}", f"{acoords['AMP-hydrolysis-a']['error']:.3f}",
                  f"{acost[0]:.4f}", f"{(afixed - aslope) / aslope_se:.2f}", f"{acost[0] - afreecost:.2f}",
                  f"{aloaded[0]:.2f}", f"{aloaded[1]:.2f}"]
# Prose values of the story pass (#429): each string repeats a table or retained-record value and is rebuilt from it here.
W420 = MEA + 'objective-weights-420/'
stage['MEA'] = mea_stage
stage['MDEA'] = read(MDEA + 'MDEA/information.json.gz')['result']
ecost = stage['MEA']['rss'] / 2  # the objective value is half the weighted sum of squares
wcai = [float(r['cost']) for r in read(MEAFIT + 'objective-contributions.csv') if r['group'] == 'Cai']
wband = [stage['MEA']['SE_multiplier'] * float(r['SE_bound_fixed']) / float(r['value']) for r in read(MEAFIT + 'uncertainty/prediction-bands.csv') if r['group'] == 'common149: partial_pressure']
assert len(wcai) == 2 and len(wband) == escore['47 current-fitted pressures'][1]
pair = rf'{afree_loaded} and {amp}\,\%'
nsplit, nsearch = aclass['counts']['confirmed'], asearch['states']
fatt = fixedp['attempts'][0]
assert fixedp['outcome'] == 'confirmed split' and fatt['confirmed'] and fatt['densities_mol_m3'][1] > fatt['densities_mol_m3'][0]
fdense = 100 * fatt['amounts_mol'][1] / sum(fatt['amounts_mol'])
sci = lambda v, d: (lambda m, e: rf'{float(m):.{d}f}\times10^{{{int(e)}}}')(*f'{v:.{d}e}'.split('e'))
dp = lambda g, role='fitted': [dpair[g, role][m]['AARD_percent'] for m in ('reference', 'candidate')]
r4q = lambda k: (abs(r4[k]['delta_ln_K4']), r4[k]['SE_ln_K4'], float(r4shift[k][313.15]['K4_ratio']))
r4T = lambda k, f: [abs(float(r4shift[k][T][f])) for T in (298.15, 313.15, 393.15)]
assert r4[k := 'dea']['delta_ln_K4'] < 0 < r4['amp']['delta_ln_K4'] and math.isclose(r4['amp']['delta_h_J_mol'], r4['amp']['bounds']['enthalpy'][0], abs_tol=1e-9)
cother = [v for k, v in cgm.items() if k != 'P0' and not k.endswith('-refit')]
dcation, mcation = AMINES[0][1], AMINES[1][1]
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
ncomp = lambda rows, groups, role: pressure_stats([r for r in rows if r['group'] in groups and r['role'] == role])['AARD_percent']
erm_old, erm_n = f1(ermatchkov['selected_point_mean_absolute_relative_deviation_percent']), ermatchkov['measured_rows']
dold, dout = f1(dsum['pressure']['fitted']['AARD_percent']), [f1(pressure_stats(doutside)['AARD_percent']), f1(dsum['pressure']['not fitted']['AARD_percent'])]
mtot, mpart = (f1(ncomp(mrows, g, 'not fitted')) for g in ({'corrected-Kamps', 'Kuranov-413K', 'Sedighi'}, {'Ermatchkov', 'Xiao'}))
e112 = f1(pressure_stats([r for r in mea_pressure if r['target'] not in fitted_pressure], 'predicted')['AARD_percent'])
eall = [f1(pressure_stats(enot, 'predicted')['AARD_percent']), eold('112 current-not-fitted pressures', 'Wagner pressures', 'Aronu 15 wt% pressures', 'Aronu 45 wt% pressures').split('$')[1][:-1]]
nsearched = sum(q['states'] for q in ephase)
dstart = [c['cost'] for c in read(DEA + 'selection.json.gz')['candidates']]
refchange = read('analyses/round_5/results/C/MEA-k-profile.json.gz')['delta_cutoff']
q4a = read(MEAFIT + 'q4.json')['result']
hp = lambda block, subset, model: f2(hong_pressures[block][subset][model]['aard_percent'])
munfin = sum(not str(u).startswith('grid') for u in mnew['tally']['unavailable'])  # unfinished MDEA searches at measured states
mgas = [c for c in mnew['classifications'] if not str(c['key']).startswith('grid')]
assert len(mnew['classifications']) - len(mgas) == len(mnew['confirmed']) == 1 and sum(bool(c['attempts']) for c in mgas) == 17
k413 = f1(ncomp(mrows, {'Kuranov-413K'}, 'not fitted'))
headline = rf'deviate by {dea}\,\% for DEA, {mdea}\,\% for MDEA and {amp}\,\% for AMP'
say('main.tex', rf'at 30 wt\% deviate by {mea}\,\%', headline)
say('submission/chemrxiv.md', f'at 30 wt% deviate by {mea}%', f'deviate by {dea}% for DEA, {mdea}% for MDEA and {amp}% for AMP')
say('submission/cover_letter.md', f'deviate by {mea} % for MEA, {dea} % for DEA, {mdea} % for MDEA and {amp} % for AMP', f'from {f1(sbkur[0])} to {mdea} %', f'from {erm_old} to {ours} %', f'from {dold} to {dea} %')
say('sections/introduction.tex', rf'deviate by {mea}\,\%, and the fitted pressures of DEA, MDEA and AMP by {dea}, {mdea} and {amp}\,\%')
say('sections/conclusion.tex', rf'deviates by {mea}\,\% from its 47 fitted', headline, rf'falls from {f1(sbkur[0])} to {mdea}\,\%', rf'rises from {erm_old} to {ours}\,\%', rf'from {dold} to {dea}\,\%')
say('sections/transfer_results.tex',
    rf'The fitted pressures deviate by {dea}\,\%', rf'that are not fitted deviate by {dout[0]}\,\%', rf'deviate by {mdea}\,\% (\cref{{fig:mdea-pressure}})', rf'deviate by {k413}\,\%', rf'deviate by {ours}\,\% and are almost all underpredicted',
    f'{min(fitted_mdea):.1f}--{max(fitted_mdea):.1f}', f"AARD of {f1(kur['True']['AARD_percent'])} and bias of {f1(kur['True']['bias_percent'])}",
    rf"contribute {cshare['MDEA', 'Loaded total pressures of Kuranov et al.']:.0f}\,\% of the objective",
    rf'These pressures deviate by {amp}\,\%', rf"by {f1(matched_amp['kundu']['new']['AARD_percent'])}\,\% (\cref{{fig:amp-pressure}})", rf"deviate by {f1(matched_amp['binary']['new']['AARD_percent'])}\,\%",
    rf'=\SI{{{aslope:.0f}}}{{\kelvin}}$, with a conditional standard error of \SI{{{aslope_se:.0f}}}{{\kelvin}}',
    *(rf'by ${v:.3f}\pm{se:.3f}$, a factor of {ratio:.3f}' for v, se, ratio in map(r4q, ('dea', 'amp'))), rf"$\num{{{r4['dea']['delta_h_J_mol']:.0f}}}\pm\SI{{{r4['dea']['SE_h_J_mol']:.0f}}}{{\joule\per\mole}}$",
    rf'falls from {f1(sbkur[0])} to {mdea}\,\%', rf'rises from {erm_old} to {ours}\,\%', rf'rises from {dold} to {dea}\,\%', rf"from {sbprof['center']['k']:.3f} to {sblow['k']:.4f}", rf'to {f1(sbkur[1])}\,\%',
    f"at any of the {sum(q['states'] for q in ephase[:2])} liquid states or {ephase[2]['states']} liquid--vapor states", f"{dnew['available']} of the {dnew['states']}",
    rf"Of the \num{{{mnew['tally']['states']}}} MDEA searches, {len(mnew['tally']['unavailable'])} did not finish, {len(mnew['bubble_refusals'])} with a bubble reference refusal", f'and {munfin} of them at measured states', f'{munfin} of its 1564 searches at measured states',
    f"detect an instability at {len(mnew['classifications'])} distinct states", f'At {len(mgas)} of them', f'at any of these {len(mgas)} states',
    f"all {anew['tally']['states']} searches of the AMP model finish without a detected instability", rf"from which it deviates by {f1(lowT(first['original']['rows'], 'loaded-pressure'))}\,\%",
    f"gave {nsplit} confirmed liquid--liquid splits and {aclass['counts']['descents'] - nsplit} further detected instabilities among the same {nsearch} states",
    rf"by {f1(q2s['hartono-2021'][0])} and {f1(q2s['tong-2012'][0])}\,\% on average", rf"deviate by {f1(matched_amp['hartono-2021-supplemental']['prior']['AARD_percent'])}\,\%, and no search detects an instability",
    rf'from ${afk(353.22):.3f}$ at \SI{{353}}{{\kelvin}} to ${afk(393.15):.3f}$',
    rf"deviates by {f1(matched_amp['kundu']['new']['AARD_percent'])}\,\% from the Kundu pressures, which it did not fit, and by {f1((40 * matched_amp['tong']['new']['AARD_percent'] + 5 * matched_amp['tong-baseline']['new']['AARD_percent']) / 45)}\,\% from the 45 pressures of Tong et al.",
    bands_main[1], bands_main[3], *bands_main[6:], rf"it deviates by {f1(k82['AARD_percent'])}\,\%", rf'by {ours}\,\%, against {theirs}\,\%')
say('sections/mea_system_modeling_results.tex', rf'deviate by {mea}\,\%', rf'deviate by {e112}\,\%', f"at most {max(r['delta_cost'] for r in read(MEAFIT + 'uncertainty/profiles.json')):.2f}", rf'{100 * min(wband):.1f}--{100 * max(wband):.1f}\,\%',
    f"from {sbprof['center_cost']:.2f} to {ecost:.2f}", rf"deviate by {e112} instead of {f1(escore['112 current-not-fitted pressures'][0])}\,\%",
    rf"{f1(baygi['prior_F2_Pa'])}\,\% for the 16-parameter calibration, {f1(read(MEA + 'paper-evidence-341/same-data-comparison/matched-score.json')['pressure_aard_percent'])}\,\% with the MEA-fitted shared set and {f1(baygi['salt_anchored_Pa'])}\,\% for the MEA model",
    f"AARD of {adopted_carbonate['aard_percent']:.1f}", f"is {adopted_carbonate['geometric_mean']:.3f}, against {cgm['P0']:.3f}", bands_main[0])
say('sections/data_methods.tex', rf"{100 * sum(wcai) / ecost:.1f}\,\% of the objective value, {ecost:.2f}", f"leaves {stage['MEA']['na']} observations and {stage['MEA']['stage_denominator']} residual degrees of freedom", f"leaves {stage['MDEA']['na']} and {stage['MDEA']['stage_denominator']}",
    rf"contribute {cshare['DEA', r'\COtwo partial pressures']:.0f}\,\% of the DEA objective and {sum(v for (a, l), v in cshare.items() if a == 'AMP' and l.startswith('Loaded')):.0f}\,\% of the AMP objective but {cshare['MDEA', 'Loaded total pressures of Kuranov et al.']:.0f}\,\% of the MDEA objective, in which the 24 densities of the \COtwo-free solution contribute {cshare['MDEA', r'\COtwo-free densities']:.0f}\,\%")
say('sections/epc_saft_equation_of_state.tex', rf"\SI{{{dcation['protonated-diethanolamine/segment_diameter'][0]:.3f}}}{{\angstrom}} for \ce{{DEAH+}} and \SI{{{mcation['protonated-methyldiethanolamine/segment_diameter'][0]:.3f}}}{{\angstrom}} for \ce{{MDEAH+}}",
    rf"of {veq(dcation, 'protonated-diethanolamine'):.3f} and \SI{{{veq(mcation, 'protonated-methyldiethanolamine'):.3f}}}{{\angstrom}}")
say('supplement.tex', *origins, f"loading of {float(viii['row']['alpha_mol_CO2_per_mol_DEA']):.3f} mol/mol", rf"\num{{{mstability['distinct_calculations']}}} distinct states", *mcost, f'{mcorr:.3f}', f2(mstats['Kuranov']['R1']['False']['AARD_percent']), *amp_supplement[:4],
    f'{abs(afixed - aslope) / aslope_se:.2f} standard errors below', f'raises the objective value by {acost[0] - afreecost:.2f}', f'contribute {aloaded[0]:.2f} to that objective, against {aloaded[1]:.2f}',
    rf"deviate by {hp('canonical', 'strict_grid', 'hong')}\,\%, the MEA model by {hp('canonical', 'strict_grid', 'salt_anchored')}\,\% and the model of Polley and Hedengren by {hp('canonical', 'strict_grid', 'polley_hedengren')}",
    f"{hp('canonical', 'all', 'hong')}, {hp('canonical', 'all', 'salt_anchored')} and {hp('canonical', 'all', 'polley_hedengren')}", *hong_supplement[2:4], hong_supplement[5], f"with the Hong parameters, {hchecks['stable_fixed_vapor']['tried']} pass the test",
    'lies ' + '{:.3f}, {:.3f} and {:.3f}'.format(*r4T('dea', 'delta_ln_K4')) + ' below', 'standard errors of ' + '{:.3f}, {:.3f} and {:.3f}'.format(*r4T('dea', 'SE_ln_K4')), 'lies ' + '{:.3f}, {:.3f} and {:.3f}'.format(*r4T('amp', 'delta_ln_K4')) + ' above',
    rf"\SI{{{prior_f2se['component/carbamate-anion/dispersion_energy_over_k']:.2f}}}{{\kelvin}}", f"by {carm['M1']['delta']:.3f}", f"by {carm['M3']['delta']:.3f}", f"falls {-crefit['M3-refit']['delta_cost']:.3f} below", f"falls to {cgm['M3-refit']:.4f}", f'tested changes is {max(cother):.4f}',
    f'contribute {wcai[0]:.3f} and {wcai[1]:.3f} to the objective value of {ecost:.3f}, together {100 * sum(wcai) / ecost:.2f}', f"factor of that equation is {stage['MEA']['stage_variance']:.8f}", f"MDEA variance factor is {stage['MDEA']['stage_variance']:.8f}", f"would give {stage['MDEA']['variance']:.8f}",
    rf"the {f2(k82['AARD_percent'])}\,\% of the MDEA model",
    f"at the {sbmea['grid']['states'] + sbmea['offset']['states']} liquid and {sbmea['census']['states']} liquid--vapor states", f"At the lower bound, ${sbprof['points']['-0.5']['k']:g}$, the objective rises by {sbprof['points']['-0.5']['cost'] - sbprof['center_cost']:.2f}, so the midpoint {sblow['k']:.4f} was taken",
    f'reference change of {refchange:.2f}', rf'deviate by {f1(sbkur[1])} instead of {f1(sbkur[0])}\,\%', rf'by {f1(sbpart[1])} instead of {f1(sbpart[0])}\,\%',
    rf"by {q2s['hartono-2021'][0]:.2f} and {q2s['tong-2012'][0]:.2f}\,\% for the first fit and by {q2s['hartono-2021'][1]:.2f} and {q2s['tong-2012'][1]:.2f}\,\% for the second",
    f"by {q4a['rows'][0]['pCO2_change']['absolute']:.5f} and " + rf"\SI{{{q4a['rows'][1]['pCO2_change']['absolute']:.2f}}}{{\pascal}}", f"from ${q4a['heat_previous_kJ_mol']:.3f}$ to " + rf"\SI{{{q4a['heat_previous_kJ_mol'] + q4a['heat_change']['absolute']:.3f}}}",
    f"distance of $+{q6d['trial_minimum']:.4f}$", f"give $+{q6d['vapor_connected_minimum']:.4f}$", f"recovers all {q7['recovered']} detected instabilities and finds none at the other {q7['searched_negatives']} states",
    rf"${sci(q3d[0], 3)}$ and ${sci(q3d[1], 3)}$ mol", f'objective values of {dstart[0]:.12f} and {dstart[1]:.12f}',
    f"Of the {len(mnew['tally']['unavailable'])} searches that did not finish, {len(mnew['bubble_refusals'])} are at grid states", f"{len(mnew['tally']['unavailable']) - munfin} are at grid states and {munfin} at measured states",
    f"detect an instability {mnew['tally']['descent']} times, at {len(mnew['classifications'])} distinct states", f'attempted at {sum(bool(c["attempts"]) for c in mgas)} of these states',
    f"from {first['cost']:.4f} to {second['cost']:.4f}", rf"from {f1(lowT(first['original']['rows'], 'loaded-pressure'))} to {f1(lowT(second['original']['rows'], 'loaded-pressure'))}\,\%")
missing = [(path, value) for path, values in stated.items() for value in values if value not in (LATEX / path).read_text()]
emit('tables/number-sources.json',json.dumps(sources,indent=2)+'\n')
if '--check' in sys.argv:
    for path, value in outputs.items():
        assert path.read_bytes()==(value if isinstance(value,bytes) else value.encode()), path
    print(f'Numeric and retained-figure check passed: {len(outputs)} displays; {len(sources)} source files.')
else:
    for path,value in outputs.items():
        path.write_bytes(value if isinstance(value,bytes) else value.encode())
for path, value in missing: print(f'Prose check failed: {path} lacks {value!r}')
assert not missing, f'{len(missing)} prose values missing'
