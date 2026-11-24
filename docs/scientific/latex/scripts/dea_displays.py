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

ROOT = Path(__file__).resolve().parents[4]
LATEX = ROOT / 'docs/scientific/latex'
BASE = 'analyses/dea_transfer/results/refit-413/'
MEA = 'analyses/mea_parameter_bundle/results/'  # read as retained files, so replacing them refreshes every MEA number shown here
OBSERVATIONS = 'analyses/dea_transfer/results/retransfer-346/f2-report-1/data-rows.json'  # source rows only; every calculated value is taken from BASE
outputs = {}
sources = {}

def read(name):
    path = ROOT / name
    sources[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if name.endswith('.json.gz'): return json.loads(gzip.decompress(path.read_bytes()))
    return json.loads(path.read_text()) if name.endswith('.json') else list(csv.DictReader(path.open()))

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

params = read(BASE + 'parameter-values.csv')
dflat = {r['parameter']: (float(r['value']), r['unit']) for r in params}
fitted_names = [r'$k_{\mathrm{DEAH^+,w}}$', r'$k_{\mathrm{DEACOO^-,w}}$', r'R4 constant term $A_4$', r'R4 enthalpy increment $\delta h$']
head = lambda text, n: [r'\addlinespace\multicolumn{' + str(n) + r'}{@{}l}{\textit{' + text + '}}']
fit_rows = [head('DEA', 5)] + [[label + (' (J/mol)' if r['unit'] == 'J/mol' else ''), bold(num(r['value'],d)), num(r['conditional_SE'],d), '['+num(r['lower'],d)+', '+num(r['upper'],d)+']', ''] for label, r in zip(fitted_names, params[:4]) for d in [0 if r['unit'] == 'J/mol' else 3]]
paper = {r['identity']: r for r in read(BASE + 'paper-data.csv')}
data = read(OBSERVATIONS)
for r in data:
    q = paper[r['identity']]
    assert (r['group'], r['role'], r['outside_ranges']) == (q['group'], q['role'], json.loads(q['outside_ranges'])), r['identity']
    r['value'] = float(q['predicted'])
groups = read(BASE + 'group-deviations.csv')

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

dev = {r['group']: r for r in groups if r['model'] == 'F2-carbamate'}
count = lambda n, used: str(n) + (f' ({used})' if int(used) != n else '')
data_rows = [head('DEA', 11)]
for group in dict.fromkeys(r['group'] for r in data):
    rs = [r for r in data if r['group']==group]
    t = [r['T_K'] for r in rs]
    data_rows.append([name(group, cite=True), SETS[group][2], rs[0]['role'], count(len(rs), dev[group]['relative_rows']), span(t, lambda v: num(v,2)), *composition(group), *marks(group), num(dev[group]['AARD_percent'],2), num(dev[group]['bias_percent'],2)])
DATA_HEAD = ['Data set','Property','Role',r'$N$',r'$T$ (K)','Amine content',r'$\alpha$ (mol/mol)','R4','R5',r'AARD (\%)',r'Bias (\%)']
ranges = read(BASE + 'range-deviations.csv')
rows = []
for group in dict.fromkeys(r['group'] for r in data):
    cells = []
    for law in LAWS:
        for outside in ['False','True']:
            hit = [r for r in ranges if r['model']=='F2-carbamate' and r['group']==group and r['law']==law and r['outside_range']==outside]
            cells += [hit[0]['rows']+'/'+hit[0]['relative_rows'], num(hit[0]['AARD_percent'],2)] if hit else ['---','---']
    if set(cells) != {'---'}: rows.append([name(group),*cells])
    else: assert group in ['Cai','Horstmann'], 'Only the binary comparisons use no reaction correlation'
top = ' & ' + ' & '.join(r'\multicolumn{2}{@{}l}{' + law + ', ' + side + '}' for law in LAWS.values() for side in ['inside','outside']) + r' \\ '
table('supplement-dea-ranges','Deviations of the DEA model inside and outside the measured temperature ranges of the carbamate hydrolysis constant (R4) and the DEA dissociation constant (R5).', [top + 'Data set',*[r'$N/N_{\mathrm{rel}}$',r'AARD (\%)']*4],rows,[.26,.075,.085,.075,.085,.075,.085,.075,.085],
      notes='$N/N_{\\mathrm{rel}}$: calculated observations / observations with a defined relative deviation; ---: no observations. The binary sets use no reaction and are omitted.')
SPECIES = {'diethanolamine': 'DEA', 'protonated-diethanolamine': r'DEAH$^+$', 'methyldiethanolamine': 'MDEA', 'protonated-methyldiethanolamine': r'MDEAH$^+$', 'aminomethylpropanol': 'AMP', 'protonated-aminomethylpropanol': r'AMPH$^+$', 'bicarbonate-anion': r'HCO$_3^-$', 'carbonate-anion': r'CO$_3^{2-}$', 'hydronium-cation': r'H$_3$O$^+$', 'hydroxide-anion': r'OH$^-$', 'carbon-dioxide': r'CO$_2$', 'water': r'H$_2$O'}
QUANTITY = {'dispersion_energy_over_k': r'dispersion energy $u/k_B$', 'segment_count': 'segment count', 'segment_diameter': r'segment diameter $\sigma$', 'solvation_factor': 'solvation factor', 'dielectric_volume': r'permittivity coefficient $d_V$', 'dielectric_temperature': r'permittivity coefficient $d_T$', 'charge_number': 'charge number', 'molar_mass': 'molar mass', 'born_diameter': r'Born diameter $d^{\mathrm{Born}}$', 'debye_huckel_diameter': r'Debye--H\"uckel diameter', 'packing_diameter': 'packing diameter', 'charged_molecule_ion': 'charged-chain self-dispersion retained (1 = yes)', 'k_ij': r'$k_{ij}$', 'k_ij_reciprocal_temperature_slope': r'reciprocal-temperature slope of $k_{ij}$', 'k_ij_temperature_slope': r'temperature slope of $k_{ij}$'}
FITTED = dict(zip([r['parameter'] for r in params[:4]], fitted_names))

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
curves = read(BASE + 'curve-data.json')
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
critical = read(MD + 'critical-k.json')
comparison = read(MD + 'comparison.json')['k_versus_critical']
assert critical['pressure_Pa'] == 1466000 and len(comparison) == len(critical['rows'])
assert all(c['T_K'] == r['T_K'] and c['k_no_gap'] == r['k_no_gap'] for c, r in zip(comparison, critical['rows']))
fig, ax = plt.subplots(figsize=(3.2, 2.7), constrained_layout=True)
ax.plot([r['T_K'] for r in comparison], [r['k'] for r in comparison], color=colors[0], label='Reported model')
ax.scatter([r['T_K'] for r in critical['rows']], [r['k_gap'] for r in critical['rows']], s=12, marker='o', facecolors='none', edgecolors=colors[1], label='Calculated gap onset')
ax.set(xlabel='Temperature (K)', ylabel=r'$k_{\mathrm{MDEA,w}}$')
ax.legend()
figure(fig, 'mdea-gap-onset.pdf')
MD343 = 'analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/'  # measured-point locations of the MDEA pressure figure
AM = 'analyses/amp_transfer/results/retransfer-412-f2-05e94210/'  # #412: F2 carbamate inputs
AMM = AM + 'slope-150/'  # the reported AMP model: AMPH+-water reciprocal-temperature slope fixed at a value chosen from a scan
f2 = MEA + 'reduced-refit/evidence/F2/'
mea_pressure = read(f2 + 'canonical-pressure.csv')
fitted_pressure = {r['id'] for r in read(f2 + 'fitted-rows.csv') if r['quantity'] == 'PartialPressure'}
pressure = {'MEA': [(float(r['loading']), float(r['ln_pred_over_obs']), 'fitted' if r['target'] in fitted_pressure else 'not fitted') for r in mea_pressure]}
pressure['DEA'] = [(loading(r['row']), math.log(r['value']/r['observed']), r['role']) for r in data if r['group'] in ('Lawson', 'Lawson-394K', 'SeoHong', 'Lal', 'Lawson-VIII')]
mrows = read(MD + 'data-rows.json')
def mdea_loading(r):
    q = r['row']
    if r['group'] == 'corrected-Kamps': return float(q['m_CO2_mol_kg_water']) / float(q['m_MDEA_mol_kg_water'])
    if r['group'] == 'Sedighi': return float(q['alpha_mol_CO2_per_mol_MDEA'])
    return float(q['m_CO2_mol_per_kg_H2O']) / float(q['m_MDEA_mol_per_kg_H2O'])
pressure['MDEA'] = [(mdea_loading(r), math.log(r['value']/r['observed']), r['role']) for r in mrows if r['group'] in ('Kuranov', 'Kuranov-413K', 'corrected-Kamps', 'Sedighi') and r['status'] == 'Available']
arows = read(AMM + 'data-rows.json')
pressure['AMP'] = [(r['loading_mol_CO2_per_mol_AMP'], math.log(r['value']/r['observed']), r['role']) for r in arows if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'tong') and r['status'] == 'Available']
assert {k: collections.Counter(r for _, _, r in v) for k, v in pressure.items()} == {
    'MEA': {'fitted': 47, 'not fitted': 112}, 'DEA': {'fitted': 30, 'not fitted': 67, 'comparison only': 10},
    'MDEA': {'fitted': 66, 'not fitted': 54}, 'AMP': {'fitted': 47, 'not fitted': 58}}
fig, axes = plt.subplots(2, 2, figsize=(6.48, 5.5), constrained_layout=True)
for ax, (amine, points) in zip(axes.flat, pressure.items()):
    for role, marker, filled in [('fitted', 'o', True), ('not fitted', 'o', False), ('comparison only', '^', False)]:
        rows = [(x, y) for x, y, label in points if label == role]
        if rows: ax.scatter([x for x, y in rows], [y for x, y in rows], s=17, marker=marker, edgecolors=colors[0], facecolors=colors[0] if filled else 'none', label=role.capitalize())
    ax.axhline(0, color='0.5', linewidth=.7)
    ax.set_title(amine + (' — CO$_2$ partial pressure' if amine in ('MEA', 'DEA') else ' — total pressure'))
    ax.set(xlabel='Loading (mol CO$_2$/mol amine)', ylabel=r'$\ln(p^{\mathrm{calc}}/p^{\mathrm{obs}})$')
    ax.legend()
figure(fig, 'loaded-pressure-residuals.pdf')
carbonate = read(f2 + 'carbonate-share.csv')
assert len(carbonate) == 10
fig, ax = plt.subplots(figsize=(3.2, 2.7), constrained_layout=True)
ax.scatter([float(r['observed_share']) for r in carbonate], [float(r['predicted_share']) for r in carbonate], s=24, facecolors='none', edgecolors=colors[0], label='Not fitted')
ax.set(xlabel='Measured carbonate share', ylabel='Calculated carbonate share')
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
            out |= {r['name'] + '/' + k: {'magnitude': r['correlation'][k], 'unit': u} for k, u in zip('abcdef', ['dimensionless', 'K', 'dimensionless', '1/K', 'K^2', '1/K^2'])}
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

mrows = read(MD + 'data-rows.json')
for r in mrows: r['key'] = r['group']
mstats = collect(read(MD + 'deviations.json'), 'range_name', 'statistics', lambda e: e['group'])
data_rows += amine('mdea', 'MDEA', MSETS, mrows, mstats, {'MDEA-dissociation': 'R5'}, mdea_basis)
MFIT = [(r'$k_{\mathrm{MDEA,w}}$ at 423 K',1,4), (r'$10^{3}\,\mathrm{d}k_{\mathrm{MDEA,w}}/\mathrm{d}T$ (K$^{-1}$)',1e3,4), (r'$k_{\mathrm{MDEAH^+,CO_2}}$',1,4), (r'$k_{\mathrm{MDEAH^+,w}}$ at 313.15 K',1,4),
        (r'$b_{\mathrm{MDEAH^+,w}}$ (K)',1,3), (r'$k_{\mathrm{MDEAH^+,HCO_3^-}}$',1,4), (r'$\sigma_{\mathrm{MDEAH^+}}$ (\AA)',1,4), (r'$u_{\mathrm{MDEAH^+}}/k_B$ (K)',1,3)]
mfit = read(MD + 'parameter-table.json')[:8]
# Standard errors on the responsive-row convention (#420): rows with zero derivatives leave the residual degrees of freedom.
stage = {k: read(MEA + 'objective-weights-420/' + k + '/information.json.gz')['result'] for k in ('MEA', 'DEA', 'MDEA', 'AMP')}
assert [stage[k]['SE_multiplier'] for k in ('DEA', 'AMP')] == [1.0, 1.0] and [stage[k]['stage_denominator'] for k in ('MEA', 'MDEA')] == [258, 272]
for r in mfit:
    if not r['on_bound']: r['conditional_standard_error'] *= stage['MDEA']['SE_multiplier']
assert all(r['role'] == 'fitted' and (r['conditional_standard_error'] is None) == r['on_bound'] for r in mfit) and [r['on_bound'] for r in mfit] == [True, *[False]*4, True, False, False]
fit_rows += [head('MDEA', 5)] + [[name, bold(num(s*r['value'],d) + (r'\textsuperscript{a}' if r['on_bound'] else '')), '---' if r['on_bound'] else num(s*r['conditional_standard_error'],d), bounds(*r['bounds'],d,s), ''] for (name,s,d), r in zip(MFIT, mfit)]
mdoc = read(MD + 'endpoint.json')
munc = read(MD + 'conditional-uncertainty.json')
mcorr = max(abs(c) for i, row in enumerate(munc['conditional_correlation']) for j, c in enumerate(row) if i != j)  # largest conditional correlation of the MDEA fit
assert next(p for p in mdoc['parameters']['pairs'] if {p['component_id_a'], p['component_id_b']} == {'water', 'methyldiethanolamine'})['coefficients'][0]['temperature_law']['reference_temperature']['magnitude'] == 423.0

arows, afeed = read(AMM + 'data-rows.json'), {r['identity']: r for r in read('analyses/amp_transfer/inputs/retransfer-344/observation-rows.csv')}
akey = lambda e: e['group'] + ('-y' if e['group'] == 'binary' and e['unit'] != 'Pa' else '')
for r in arows: r['key'] = akey(r)
adoc = read(AMM + 'parameters.json')
amass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in adoc['parameters']['components']}
def amp_basis(rs):
    feed = [afeed[r['identity']] for r in rs]
    if 'x_AMP' in rs[0]['row']: return r'$x_{\mathrm{A}}=\,$' + span([float(r['row']['x_AMP']) for r in rs], sig), '---'
    wt = [100*amass['aminomethylpropanol']/(amass['aminomethylpropanol'] + amass['water']*float(f['water'])) for f in feed]
    return span(wt, sig) + r' wt\%', span([float(f['alpha']) for f in feed], sig)
afree, asame, aunc = read(AMF + 'fit-summary.json'), read(AM + 'same-row-deviations.csv'), read(AMM + 'conditional-uncertainty.json')
AMODEL, AFREE = 'Slope -150 K against #404 main', 'F2 main against #404 main'
assert afree['selection']['selected'] == 1 and {r['case'] for r in asame} == {AMODEL, AFREE}
astat = lambda r: dict(rows=int(r['new_calculated']), relative_rows=int(r['new_relative_defined']), AARD_percent=float(r['new_AARD_percent']), bias_percent=float(r['new_bias_percent']))
apoint = lambda case: {r['group']: r for r in asame if r['case'] == case and r['reaction'] == 'R1' and r['range_mark'] == 'False' and r['unit'] == 'Pa'}
# The model, one entry per coordinate in the order of the free fit, with the fixed slope in its place; the enthalpy increment on the basis of retain_404.retain_case.
aq = {q['identity']: q for q in adoc['coordinates']}
assert set(aq) | {'AMPH-water-slope'} == {m['identity'] for m in afree['parameter_table']} and 'AMPH-water-slope' not in aq
def amodel(i):
    if i == 'AMPH-water-slope':
        return dict(identity=i, lower=None, upper=None, fixed=True, model=dict(value=flatten(adoc, {'protonated-aminomethylpropanol'})[ASLOPE][0], on_bound=None, conditional_standard_error=None))
    q, j = aq[i], list(aq).index(i)
    shift = q.get('kind') == 'reaction_enthalpy_shift'
    return dict(identity=i, lower=-5000 if shift else q['bounds'][0], upper=5000 if shift else q['bounds'][1], fixed=False,
                model=dict(value=-5000 - q['bounds'][0] if shift else q['origin'], on_bound=j in aunc['active_bounds'], conditional_standard_error=aunc['conditional_standard_error'].get(i)))
acomp = dict(parameters=[amodel(m['identity']) for m in afree['parameter_table']],
             pressure_deviations_by_range=[dict(range='R1', group=g, role=r['role'], rows=int(r['new_calculated']), model=astat(r), free=astat(apoint(AFREE)[g])) for g, r in apoint(AMODEL).items()])
assert {e['group'] for e in acomp['pressure_deviations_by_range']} == {'hartono-2021-supplemental', 'kundu', 'loaded-pressure', 'tong'}
stable = {e['group']: e for e in acomp['pressure_deviations_by_range']}
adev = [dict(group=r['group'], unit=r['unit'], range_name=r['reaction'], outside_range=r['range_mark'], statistics=astat(r)) for r in asame if r['case'] == AMODEL and r['group'] != 'all pressures']
data_rows += amine('amp', 'AMP', ASETS, arows, collect(adev, 'range_name', 'statistics', akey), {'carbamate-hydrolysis': 'R4', 'AMP-dissociation': 'R5'}, amp_basis)
AFIT = [(r'$k_{\mathrm{AMP,w}}$ at 313.15 K',4), (r'$b_{\mathrm{AMP,w}}$ (K)',3), (r'$k_{\mathrm{AMPH^+,w}}$ at 313.15 K',4), (r'$b_{\mathrm{AMPH^+,w}}$ (K)',3), (r'$k_{\mathrm{AMPH^+,CO_2}}$',4),
        (r'$\sigma_{\mathrm{AMPH^+}}$ (\AA)',4), (r'$\sigma_{\mathrm{AMPCOO^-}}$ (\AA)',4), (r'R4 constant term $A_4$',4), (r'R4 enthalpy increment $\delta h$ (J/mol)',1)]
on = lambda point, d: num(point['value'], d) + (r'\textsuperscript{a}' if point['on_bound'] else '')
fit_rows += [head('AMP', 5)] + [[name, num(r['model']['value'],d) + r'\textsuperscript{b}', '---', '[---, ---]', ''] if r['fixed'] else [name, bold(on(r['model'],d)), num(r['model']['conditional_standard_error'],d) if r['model']['conditional_standard_error'] else '---', bounds(r['lower'],r['upper'],d), ''] for (name,d), r in zip(AFIT, acomp['parameters'])]
# R4 of DEA and AMP relative to the starting correlations (#426): the enthalpy increment and the level change at 313.15 K.
r4 = {k: read(f'analyses/{k}_transfer/results/r4-shift-426/table6.json') for k in ('dea', 'amp')}
r4shift = {k: {round(float(r['T_K']), 2): r for r in read(f'analyses/{k}_transfer/results/r4-shift-426/shift.csv')} for k in ('dea', 'amp')}
ashift = {q['identity']: q for q in acomp['parameters']}['AMP-hydrolysis-enthalpy-increment']['model']
assert abs(r4['dea']['SE_h_J_mol'] - float(params[3]['conditional_SE'])) < 1e-6 and abs(r4['dea']['SE_ln_K4'] - float(params[2]['conditional_SE'])) < 1e-9, 'the DEA R4 shifts are the fitted coordinates of the record'
assert abs(r4['amp']['delta_h_J_mol'] - ashift['value']) < 1e-6 and ashift['on_bound'] and r4['amp']['SE_h_J_mol'] is None and abs(r4['amp']['SE_ln_K4'] - aunc['conditional_standard_error']['AMP-hydrolysis-a']) < 1e-9
assert all(abs(float(r4shift[k][313.15]['delta_ln_K4']) - r4[k]['delta_ln_K4']) < 1e-12 for k in r4)
level = lambda q: [r'R4 change at 313.15 K, $\Delta\ln K_4$\textsuperscript{c}', f"${q['delta_ln_K4']:+.3f}$", num(q['SE_ln_K4'], 3), bounds(*q['bounds']['level'], 3), '']
assert fit_rows[4][0].startswith('R4 enthalpy increment') and fit_rows[-1][0].startswith('R4 enthalpy increment')
fit_rows[4][1:4] = [bold(num(r4['dea']['delta_h_J_mol'], 0)), num(r4['dea']['SE_h_J_mol'], 0), bounds(*r4['dea']['bounds']['enthalpy'], 0)]
fit_rows.insert(4, level(r4['dea']))
fit_rows.insert(len(fit_rows) - 1, level(r4['amp']))
# fit_rows: name, value, standard error, bounds and an unused fifth cell. The main text omits the bounds; the supplement lists them.
columns = lambda n, keep: [[r[0].replace('multicolumn{5}', 'multicolumn{' + str(n) + '}')] if len(r) == 1 else keep(r) for r in fit_rows]
table('transfer-fitted', 'Fitted parameters of the DEA, MDEA and AMP models with conditional standard errors.', ['Parameter','Value','Standard error'], columns(3, lambda r: [r[0], r[1], r[2]]), [.52,.20,.20],
      notes=r'Bold: fitted in this work. \textsuperscript{a}On a bound; no standard error is assigned. DEA and AMP: $\delta h$ is measured from the starting R4 correlation of Table~\ref{tab:reaction-equilibrium-constants}, and the final R4 coefficients include it (Table~\ref{supp-tab:supplement-transfer-parameters}). \textsuperscript{c}Fitted minus starting $\ln K_4$ at \SI{313.15}{\kelvin}: the fitted constant term expressed relative to the starting correlation, with the standard error of $A_4$; it is not a further parameter. MDEA: $k_{\mathrm{MDEA,w}}$ is held at the upper bound that keeps the \COtwo-free MDEA--water solution free of a calculated liquid--liquid gap at \SI{1.466}{\mega\pascal} (Section~\ref{sec:methods-phase}), and $k_{\mathrm{MDEAH^+,HCO_3^-}}$ is at its upper bound; the other standard errors are conditional on both. AMP: \textsuperscript{b}fixed at a value chosen from a scan (Section~\ref{sec:methods-phase}); the standard errors are conditional on it. The standard errors follow Eq.~\eqref{eq:conditional-covariance}. Table~\ref{supp-tab:supplement-transfer-bounds} gives the bounds.')
table('supplement-transfer-bounds', 'Bounds of the fitted parameters of the DEA, MDEA and AMP models.', ['Parameter','Lower bound','Upper bound'], columns(3, lambda r: [r[0].replace(r'\textsuperscript{c}', ''), *r[3][1:-1].split(', ')]), [.50,.20,.20],
      notes=r'The parameters are those of main-text Table~\ref{main-tab:transfer-fitted}. For DEA and AMP the bounds of $\delta h$ and of $\Delta\ln K_4$ are measured from the starting R4 correlations, like the values of that table.')
apure, ROLE = read(AM344 + 'pure-binary-on-05e94210.json')['pure'], {'fitted': 'fitted', 'assessment_not_fitted': 'not fitted'}
data_rows.append(head('AMP, pure component', 11))
for key, who in [('Klepacova2011', r"Klep\'a\v{c}ov\'a et al.\ \cite{klepacovaVaporPressuresSeveral2011}"), ('Belabbaci2010', r'Belabbaci et al.\ \cite{belabbaciInvestigationIsothermalVapour2010}'), ('Pappa2006', r'Pappa et al.\ \cite{pappaMeasurementThermodynamicModeling2006}'), ('Ayad2023', r'Ayad et al.\ \cite{ayadMeasurementsModelingThermodynamic2023}')]:
    g, t = apure['groups'][key], [r['T_K'] for r in apure['rows'] if r['campaign'] == key]
    assert g['n'] == len(t), key
    data_rows.append([who, g['metric'], ROLE[g['role']], str(g['n']), span(t, lambda v: num(v,2)), 'pure AMP', '---', '---', '---', *([num(g['AARD_percent'],2), num(g['signed_relative_bias_percent'],2)] if 'AARD_percent' in g else [r'---\textsuperscript{b}', '---'])])
table('supplement-transfer-data', 'Data for DEA, MDEA and AMP with their roles in the fit of each model, their ranges, and the deviations of the DEA, MDEA and AMP models.', DATA_HEAD, data_rows, [.18,.085,.095,.04,.09,.10,.09,.05,.05,.06,.07], long=True, size=r'\footnotesize',
      notes=r'$N$: number of observations; in parentheses, the number with a calculated value and a defined relative deviation. Amine content: that of the unloaded solution, or a mole fraction for the \COtwo-free binary sets ($x_{\mathrm{w}}$: water; $x_{\mathrm{A}}$: amine). R4 and R5: in, out or mixed relative to the source temperature range of that equilibrium constant, which for the AMP R4 is a range of model-derived estimates (main-text Table~\ref{main-tab:reaction-equilibrium-constants} and Section~\ref{main-sec:data-roles}); ---: not reported in the source, or the calculation uses no such reaction. AARD and bias follow main-text Eq.~(\ref{main-eq:aard}). Tables~\ref{tab:supplement-dea-ranges}--\ref{tab:supplement-amp-ranges} give the deviations inside and outside each range, and Section~\ref{sec:s-corrections} gives the source conventions. \textsuperscript{a}Mole fraction of added \COtwo. DEA: the water--DEA interaction was fitted beforehand to the 365.15 K vapor--liquid equilibria of Horstmann et al.\ \cite{horstmannPhaseEquilibriumExcess2002}, which are not listed; the pressures not fitted were inspected before the choice between the two DEA solutions whose objective values agree within the optimizer tolerance. MDEA: the Xiao et al.\ and Ermatchkov et al.\ pressures were used to choose the initial MDEA parameter set but are not in the objective. Pure component: deviations at the fixed pure-AMP parameters, whose fit preceded the reactive fit; \textsuperscript{b}the errors of the three fitted densities are ' + ', '.join(num(e, 3) for e in apure['groups']['Ayad2023']['errors_kg_m3']) + r' kg/m$^3$.')
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
assert [AMINES[2][1][k][0] for k in AKEYS] == [r['model']['value'] for r in acomp['parameters'][:8]], 'AMP values are those of the fit record'
assert all(AMINES[2][1][k][0] == apure['parameter_values'][v] for k, v in APURE.items()), 'bold pure-AMP values are those of the pure-component fit'
permittivity = lambda s: {s + '/dielectric_volume', s + '/dielectric_temperature'}
FITTED_HERE = [{r['parameter'] for r in params if r['fitted_or_fixed'] == 'fitted'} | permittivity('diethanolamine') | {'diethanolamine/water/k_ij'},
               set(MKEYS) | permittivity('methyldiethanolamine'),
               set(AKEYS) - {ASLOPE} | {'carbamate-hydrolysis/b'} | set(APURE) | permittivity('aminomethylpropanol')]  # the fitted AMP enthalpy increment sets B_4; the slope is fixed
SOURCE = [r'\cite{Nasrifar2010}', r'\cite{Nasrifar2010}\textsuperscript{a}', r'This work\textsuperscript{b}', r'\cite{Pahlavanzadeh2013,Uyan2015}\textsuperscript{c}', r'This work\textsuperscript{d}', r'This work\textsuperscript{e}', r'This work\textsuperscript{f}', r'This work\textsuperscript{g}']
# Stated origins of fixed ion inputs (supplement): the DEA and AMP carbamate values come from the MEA model (fit F2);
# its diameter scaled by the cube root of the DEA/MEA ratio of m*sigma^3 (neutral MEA: 3.0353, 3.0435 A); AMPH+ takes the AMP energy.
f2, f2se = ({r['identity']: float(r[k]) for r in read(MEA + 'reduced-refit/parameter-details.csv') if r['fit'] == 'F2' and r[k]} for k in ('value', 'conditional_SE'))
f2se = {k: v * stage['MEA']['SE_multiplier'] for k, v in f2se.items()}
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
      notes=r'The columns are those of Table~\ref{tab:species-parameters}. Bold: fitted in this work; in a row of this work, the values in normal weight are fixed; --: not used. \textsuperscript{a}DEA values, with zero self-association energy. \textsuperscript{b}Dispersion energy of \ce{MEACOO-} in the MEA model and its diameter scaled to DEA (Section~\ref{supp-sec:s-parameters}). \textsuperscript{c}Segment parameters of Ref.~\cite{Pahlavanzadeh2013} and association parameters of Ref.~\cite{Uyan2015}; association volume converted in this work. \textsuperscript{d}Segment count and association volume of MDEA; zero self-association energy. \textsuperscript{e}Fitted beforehand to pure-AMP data. \textsuperscript{f}Dispersion energy of AMP. \textsuperscript{g}Dispersion energy of \ce{MEACOO-} in the MEA model; diameter fitted, with the \ce{MEACOO-} diameter of the MEA model as its lower bound. Table~\ref{tab:transfer-fitted} gives the standard errors of the values fitted in the reactive fits, and Table~\ref{supp-tab:supplement-transfer-parameters} unrounded values and the remaining inputs.')
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
        assert record[key][0] == f2['component/' + key if last == 'dispersion_energy_over_k' else 'pair/' + key]
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
adh = {q['identity']: q for q in acomp['parameters']}['AMP-hydrolysis-enthalpy-increment']['model']['value']
rows.append([r'R4, enthalpy increment $\delta h$, contained in $B_4$', bold(f'${adh}$'), 'J/mol', 'This work'])
table('supplement-transfer-parameters', 'Amine-specific parameter values of the DEA, MDEA and AMP models at full precision.', ['Parameter','Value','Unit','Source'], rows, [.45,.24,.07,.21], long=True,
      notes=r'Bold values were fitted in this work; Table~\ref{main-tab:transfer-fitted} of the main text gives the standard errors of the parameters of the reactive fits, and Table~\ref{tab:supplement-transfer-bounds} their bounds. For DEA, the R4 coefficients $A_4$ and $B_4$ are the final coefficients after the fit, not additional independent fitted parameters. R4: carbamate hydrolysis; R5: amine dissociation; $\ln K=a+b/T+c\ln(T/T_{\mathrm{ref}})+dT$ with $T$ in K and $T_{\mathrm{ref}}=313.15$ K, on the common-molality reference basis; coefficients not listed are zero. For R4, where $c=d=0$, $a$ and $b$ are written $A_4$ and $B_4$: they are the coefficients of main-text Eq.~(\ref{main-eq:reaction-equilibrium-constant-temperature}) on that basis, with $\Delta_4=0$. Binary dispersion interactions not listed are zero; a $k_{ij}$ with a slope is the value at 313.15 K, except MDEA--water, at 423 K. Each of the chain cations DEAH$^+$ and MDEAH$^+$ keeps the dispersion between its own segments. ``DEA value'' and ``MDEA value'': the value of the molecular amine. The data deposit gives the source and basis of each value.')
def pressures(name, amine_name, shape, panels, kinds, curves, points, sep, laws, fitted, mass):
    """Pressure against loading: retained measurements as points, retained model curves as lines."""
    lines = {}
    for r in curves: lines.setdefault(r['curve'], []).append(r)
    assert {q['curve'] for q in points} <= set(lines), 'every plotted measurement belongs to a retained curve'
    fig, axes = plt.subplots(*shape, figsize=(6.48, 3.3*shape[0]), constrained_layout=True)
    temperatures = sorted({round(float(key.split(sep)[1])) for key in lines if any(choose(*key.split(sep)) for choose in panels)})
    for ax, letter, choose, kind in zip(axes.flat, 'abcdef', panels, kinds):
        chosen = [key for key in lines if choose(*key.split(sep))]
        ax.set_yscale('log')
        stocks, used = {key.split(sep)[2] for key in chosen}, set()
        for index, key in enumerate(chosen):
            line, (group, T, water) = sorted(lines[key], key=lambda r: r['loading']), key.split(sep)
            outside = [line[0]['outside_ranges'][law] is True for law in laws]
            style = '-.' if len(laws) > 1 and all(outside) else '--' if outside[0] else ':' if any(outside) else '-'
            label = f'{float(T):.2f} K' + (f', {100*mass[0]/(mass[0] + mass[1]*float(water)):.3g} wt%' if len(stocks) > 1 else '')
            look = series(ax, [r['loading'] for r in line], [r['value']/1000 for r in line], style, float(T), temperatures, used, group in fitted, label)
            obs = [q for q in points if q['curve'] == key]
            ax.scatter([q['loading'] for q in obs], [q['pressure_Pa']/1000 for q in obs], s=22, **look)
        ax.set(xlabel=f'Loading (mol CO$_2$/mol {amine_name})', ylabel={'t': 'Total pressure (kPa)', 'p': 'CO$_2$ partial pressure (kPa)'}[kind])
        ax.set_title(f'({letter})', loc='left')
        ax.yaxis.set_minor_formatter(matplotlib.ticker.LogFormatterSciNotation(labelOnlyBase=False, minor_thresholds=(1.3, 0.4)))
        ax.legend(ncol=1 if len(stocks) > 1 and shape[1] > 2 else 2, columnspacing=.7, handlelength=1.8, handletextpad=.4, loc='upper center', bbox_to_anchor=(.5, -.2), frameon=False)
    figure(fig, name)

mmass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mdoc['parameters']['components']}
pressures('mdea-current-measured-model.pdf', 'MDEA', (2, 3), [lambda g, T, w: g.startswith('Kuranov') and float(w) > 20, lambda g, T, w: g.startswith('Kuranov') and float(w) < 20, lambda g, T, w: g == 'Xiao',
          lambda g, T, w: g == 'Ermatchkov' and float(w) > 20, lambda g, T, w: g == 'Ermatchkov' and 10 < float(w) < 20, lambda g, T, w: g == 'Ermatchkov' and float(w) < 10], 'ttpppp',
          read(MD + 'curves/curve-data.json'), read(MD343 + 'curves/data-points.json'), ':', ['MDEA-dissociation'], {'Kuranov'}, (mmass['methyldiethanolamine'], mmass['water']))
apoints = [dict(curve=f"{f['dataset']}|{float(f['T'])}|{float(f['water'])}", loading=float(f['alpha']), pressure_Pa=r['observed']) for r in arows for f in [afeed[r['identity']]] if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'kundu', 'tong')]
pressures('amp-current-measured-model.pdf', 'AMP', (2, 2), [lambda g, T, w: g.startswith('hartono'), lambda g, T, w: g.startswith('tong'), lambda g, T, w: g.startswith('kundu') and float(w) > 12, lambda g, T, w: g.startswith('kundu') and float(w) < 12], 'ttpp',
          read(AMM + 'curve-data.json'), apoints, '|', ['AMP-dissociation', 'carbamate-hydrolysis'], {'hartono-2021-calibration'}, (amass['aminomethylpropanol'], amass['water']))
# One summary row per model, from each amine's retained summary.
dsum, msum = read(BASE + 'paper-summary.json'), read(MD + 'summary-row.json')
mstability = read(MD + 'stability.json')
aconf, asearchrows = read(AMM + 'confirmation.json'), read(AMM + 'search-1.json.gz')
msearch, asearch = mstability['grid'], aconf['full_search']
# The free fit (selected start 1) is the comparison whose splits the paper names; its classification and search.
afreesearch, aclass = next(f for f in afree['fits'] if f['start'] == 1)['search']['grid'], read(AMF + 'phase-classification-1.json.gz')
aall = {r['role']: astat(r) for r in asame if r['case'] == AMODEL and r['group'] == 'all pressures'}
asum = {'fitted_parameters': sum(not r['fixed'] for r in acomp['parameters']), 'active_bounds': sum(bool(r['model']['on_bound']) for r in acomp['parameters']), 'fitted_pressure': aall['fitted'], 'not fitted_pressure': aall['not fitted'],
        'liquid_liquid_splits': asearch['liquid_liquid_splits']['data'] + asearch['liquid_liquid_splits']['grid'], 'unavailable_stability_entries': asearch['states'] - asearch['available']}
assert aconf['stable'] and asearch['descent'] == asum['liquid_liquid_splits'] == asum['unavailable_stability_entries'] == 0 and len(asearchrows) == asearch['states'] and not any(r['descent'] for r in asearchrows)
assert aclass['counts']['descents'] == aclass['counts']['liquid_directed'] == afreesearch['descent'] == len(aclass['states']) and aclass['counts']['classification_errors'] == 0
cell = lambda s: num(s['AARD_percent'],2) + ' (' + str(s['rows']) + ')'
escore = {r['group']: (r['deviations'][1], r['n'][1]) for r in read(MEA + 'paper-evidence-341/same-data-comparison/part1-scores.json')}
enot = [escore[g] for g in ('112 current-not-fitted pressures', 'Wagner pressures', 'Aronu 15 wt% pressures', 'Aronu 45 wt% pressures')]  # every MEA pressure not fitted; the count-weighted mean of the four set means is the mean over all of them
e47 = num(escore['47 current-fitted pressures'][0], 2) + f" ({escore['47 current-fitted pressures'][1]})"
efit, esearch = [r for r in read(MEA + 'reduced-refit/parameter-details.csv') if r['fit'] == 'F2'], read(MEA + 'paper-evidence-341/stability/candidate/search.json')
pooled = lambda rs: num(100*sum(abs(r['value']/r['observed'] - 1) for r in rs)/len(rs), 2) + f' ({len(rs)})'  # mean over retained per-observation pressures
by_role = lambda rs, role: [r for r in rs if r['unit'] == 'Pa' and r['role'] == role]
assert pooled(by_role(arows, 'fitted')) == cell(asum['fitted_pressure']) and pooled(by_role(arows, 'not fitted')) == cell(asum['not fitted_pressure']), 'the mean over rows reproduces the retained AMP summary'
assert pooled(by_role(mrows, 'not fitted')) == cell(msum['not_fitted_pressure']['statistics']), 'the mean over rows reproduces the retained MDEA summary'
def by_observable(rs, total, partial):  # total pressures and CO2 partial pressures deviate differently, so they are not added together
    out = by_role(rs, 'not fitted')
    assert {r['group'] for r in out} == total | partial
    return '$P$: ' + pooled([r for r in out if r['group'] in total]) + r'; $p_{\COtwo}$: ' + pooled([r for r in out if r['group'] in partial])
mcomp = read(MD + 'comparison.json')
mbounded = mcomp['runs'][mcomp['chosen']]
assert mbounded['checks']['native'] == {'states': 78, 'available': 78, 'descent': 0, 'minimum': 0.0} and mbounded['checks']['hull']['gaps'] == 0 and all(r['below'] for r in mcomp['k_versus_critical']), 'MDEA binary states without a gap'
assert mcomp['runs']['unbounded-2']['checks']['native']['descent'] == 14 and not mstability['interpolated_set_split_state']['available'], 'the unconstrained fit has the gap; the former split state is unavailable'
rows = [['MEA', len(efit), sum(r['on_bound'] == 'True' for r in efit), e47, e47, num(sum(a*n for a, n in enot)/sum(n for a, n in enot), 2) + f' ({sum(n for a, n in enot)})', sum(esearch[k]['states'] for k in ('grid', 'offset', 'census')), len(esearch['grid']['unavailable']) + len(esearch['offset']['unavailable']) + esearch['census']['incomplete'], sum(esearch[k]['descent'] for k in ('grid', 'offset', 'census'))],
        ['DEA', dsum['fitted_parameters'], len(dsum['active_bounds']), cell(dsum['pressure']['fitted']), cell(dsum['pressure']['fitted']), cell(dsum['pressure']['not fitted']), dsum['stability']['grid']['states'], len(dsum['stability']['grid']['unavailable']), sum(dsum['stability']['grid']['liquid_liquid_splits'].values())],
        ['MDEA', msum['free_fitted_parameters'], msum['on_bounds'], cell(mstats['Kuranov']['R1']['False']), cell(msum['fitted_pressure']['statistics']), by_observable(mrows, {'corrected-Kamps', 'Kuranov-413K', 'Sedighi'}, {'Ermatchkov', 'Xiao'}), msearch['states'], msum['unavailable_searches'], msum['liquid_liquid_splits_found']],
        ['AMP', asum['fitted_parameters'], asum['active_bounds'], cell(stable['loaded-pressure']['model']), cell(asum['fitted_pressure']), by_observable(arows, {'hartono-2021-supplemental', 'tong', 'tong-baseline'}, {'kundu'}), asearch['states'], asum['unavailable_stability_entries'], asum['liquid_liquid_splits']]]
fixedp = read('analyses/mdea_mea_workflow/results/phase-search-421/fixed-pressure.json')
fsplit = next(q for q in fixedp['attempts'] if q['confirmed'])
fwt = 100 * mmass['methyldiethanolamine'] * fixedp['feed']['methyldiethanolamine'] / (mmass['methyldiethanolamine'] * fixedp['feed']['methyldiethanolamine'] + mmass['water'] * fixedp['feed']['water'])
fstate = rf"\SI{{{fixedp['T_K']:.2f}}}{{\kelvin}}, {fwt:.2f} wt\% MDEA, {fixedp['feed']['carbon-dioxide'] / fixedp['feed']['methyldiethanolamine']:.3f} mol/mol and \SI{{{fixedp['P_Pa'] / 1e6:.3f}}}{{\mega\pascal}}"
assert fixedp['outcome'] == 'confirmed split' and fsplit['distinct'] and fsplit['Gibbs_decrease_over_RT_mol'] > 1e5 * fsplit['numerical_error_over_RT_mol']
rows.append([r'MDEA, one state at fixed pressure\textsuperscript{a}', '', '', '', '', '', 1, 0, 1])
for row in rows[:4]: row[3] = {'MEA': r'$p_{\COtwo}$', 'DEA': r'$p_{\COtwo}$', 'MDEA': '$P$', 'AMP': '$P$'}[row[0]] + ': ' + row[3]  # fitted loaded-solution observable: Hilliard/Jou and Lawson-Garst partial, Kuranov and Hartono total pressures
for row in rows[:2]: row[5] = r'$p_{\COtwo}$: ' + row[5]  # every MEA and DEA pressure not fitted is a CO2 partial pressure (Tables 5 and S8)
table('amine-summary', 'Summary of the four amine models.', ['Model','Fitted parameters','On bounds',r'Fitted loaded-solution pressures: AARD (\%) ($N$)',r'All fitted pressures, with the \COtwo-free binary pressures: AARD (\%) ($N$)',r'Pressures not fitted: AARD (\%) ($N$)','Searches','Searches not completed','Liquid--liquid splits found'], rows, [.13,.09,.06,.135,.105,.115,.07,.10,.10],
      notes=r'AARD follows Eq.~\eqref{eq:aard}; $N$ is the number of observations. Fitted loaded-solution pressures are the fitted \COtwo partial pressures ($p_{\COtwo}$) of loaded MEA and DEA and the fitted total pressures ($P$) of loaded MDEA and AMP; the next column adds the fitted \COtwo-free bubble pressures of MDEA--water and AMP--water. Neither includes the fitted \COtwo--water pressures of Kiepe et al.\ in the MEA objective (Table~\ref{tab:mea-data}). The MEA value for pressures not fitted is the mean over the observations of its four pressure sets not fitted; for MDEA and AMP the pressures not fitted are given separately as total pressures and \COtwo partial pressures, and the AMP total pressures include the ' + str(sum(r['group'] == 'tong-baseline' for r in arows)) + r' \COtwo-free bubble pressures of Tong et al. The searches are finite and their designs differ between the amines (Section~\ref{supp-sec:s-phase}), so the counts do not measure equal coverage, and split counts are lower bounds. \textsuperscript{a}Two-liquid equilibrium calculation at ' + fstate + r', the pressure at which an earlier parameter set gave a split; it is not one of the \num{' + str(msearch['states']) + r'} searches, and that pressure is far above process conditions (Section~\ref{sec:results-mdea-phase}).')
P341 = MEA + 'paper-evidence-341/paper-evidence/'
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
table('dea-binary-tradeoff', 'DEA model against a refit with a temperature-dependent water--DEA interaction, on identical observations.', ['Observations', '$N$', 'Role, DEA model', 'Role, refit', r'AARD (\%), DEA model', r'AARD (\%), refit'],
      [[label, dpair[g, r]['reference']['rows'], a413, a425, num(dpair[g, r]['reference']['AARD_percent'], 2), num(dpair[g, r]['candidate']['AARD_percent'], 2)] for g, r, label, a413, a425 in DPAIR], [.40, .05, .14, .14, .11, .10],
      notes=r'AARD follows Eq.~\eqref{eq:aard}. DEA model: constant water--DEA interaction fitted beforehand to the bubble pressures of Horstmann et al. Refit: a water--DEA interaction with a temperature coefficient fitted beforehand to those pressures, the excess enthalpies and the bubble pressures of Cai et al., followed by a reactive fit of the same four parameters to the same data. The excess enthalpies are negative and their relative deviations large because the DEA model gives the wrong sign. The pressures outside the reactive fit were examined during development.')
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
assert D425['tableS10'][12]['group'] == 'Horstmann VLE' and len(arcis) == 14 and objective_n == {'MEA': 307, 'DEA': 80, 'MDEA': 281, 'AMP': 156}, objective_n
table('calibration-data', 'Data in the objective of each model, data fitted beforehand and data outside the objective that informed a choice.', ['Observable', 'Source', '$N$', '$T$ (K)', 'Role'], design, [.36, .16, .07, .19, .18],
      notes=r'Fitted: in the objective of the reported fit, ' + ', '.join(f'{n} observations for {k}' for k, n in objective_n.items()) + r'. Fitted beforehand: used to set a parameter that the reactive fit holds fixed. \textsuperscript{a}Development: outside the objective, but used to choose the parameters or the initial parameter set (Section~\ref{sec:data-roles}). $p_{\COtwo}$: \COtwo partial pressure; total pressure: bubble pressure of the loaded solution. Table~\ref{tab:mea-data} and Table~\ref{supp-tab:supplement-transfer-data} give the compositions, loadings and deviations of every set, including those that are neither fitted nor used for a choice.')
# Carbonate share of Jakobsen et al. under the tested electrostatic and shared-ion changes (#423).
C423 = MEA + 'shared-ion-electrostatics-423/c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb/ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed/'
CCASES = [('P0', 'MEA model'), ('bicarbonate-anion-2.5', r'Bicarbonate Born diameter \SI{2.5}{\angstrom}'), ('bicarbonate-anion-3.5', r'Bicarbonate Born diameter \SI{3.5}{\angstrom}'), ('bicarbonate-anion-4', r'Bicarbonate Born diameter \SI{4.0}{\angstrom}'),
          ('carbonate-anion-2.5', r'Carbonate Born diameter \SI{2.5}{\angstrom}'), ('carbonate-anion-4', r'Carbonate Born diameter \SI{4.0}{\angstrom}'), ('carbonate-anion-4.953', r'Carbonate Born diameter \SI{4.953}{\angstrom}'),
          ('permittivity--5pct', r'Permittivity lowered by 5\,\%'), ('permittivity-+5pct', r'Permittivity raised by 5\,\%'), ('P1', 'Second pair of MEA permittivity coefficients'), ('M1', r'Solvation factor of \COtwo 1.5'), ('M3', 'Solvation factor of MEA 1.5'),
          ('P1-refit', 'Second permittivity pair, refitted'), ('M3-refit', 'Solvation factor of MEA 1.5, refitted')]
cshare = {k: read(C423 + k + '/carbonate-share.json') for k, _ in CCASES}
carm, crefit = read(C423 + 'arm-replay-costs.json')['arms'], read(C423 + 'refit-comparison.json')['arms']
cgm = {k: v['summary']['all']['geometric_mean'] for k, v in cshare.items()}
assert all(v['summary']['all']['n'] == 10 for v in cshare.values()) and carm['P0']['delta'] == 0
table('supplement-carbonate-sensitivity', r'Carbonate share of dissolved carbon at the ten states of Jakobsen et al.\ \cite{Jakobsen2005} for the MEA model and for the changes tested.', ['Case', 'Geometric mean of calculated/observed', r'AARD (\%)'],
      [[label, f'${cgm[k]:.4f}$', num(cshare[k]['summary']['all']['aard_percent'], 2)] for k, label in CCASES], [.52, .26, .14],
      notes=r'The shares are not fitted in any case. The last two rows refit the other MEA parameters; every other change is made with all other parameters fixed. The Born diameters of bicarbonate and carbonate are \SI{3.0}{\angstrom} in the MEA model.')
cratio = [float(r['calc_over_obs']) for r in cshare['P0']['rows']]
# Volume-equivalent Born diameters of the chain cations: retained replays at fixed other parameters (#423).
def born_replay(amine, group):
    out = []
    for case in ('control', 'volume-equivalent'):
        rs = [r for r in read(C423 + amine + '/' + case + '/data-rows.json.gz') if r['group'] == group and r.get('status', 'Available') == 'Available']
        out.append(100 * sum(abs(r['value'] / r['observed'] - 1) for r in rs) / len(rs))
    return out
bdea, bmdea = born_replay('diethanolamine', 'Lawson'), born_replay('methyldiethanolamine', 'Kuranov')
assert abs(bdea[0] - dsum['pressure']['fitted']['AARD_percent']) < 1e-6 and abs(bmdea[0] - mstats['Kuranov']['R1']['False']['AARD_percent']) < 1e-6
veq = lambda record, s: record[s + '/segment_diameter'][0] * record[s + '/segment_count'][0] ** (1 / 3)
# Published models on identical observations only, each with the role of those observations in that model's fit.
PUB = {'Baygi2015 PC-SAFT': r'Baygi and Pahlavanzadeh, PC-SAFT \cite{Baygi2015}', 'Najafloo2018 SAFT-HR': r'Najafloo and Zarei, SAFT-HR \cite{Najafloo2018}', 'Zhang2011 eNRTL': r'Zhang et al., eNRTL \cite{Zhang2011}'}
SHARED = {'Ermatchkov': r'\COtwo partial pressures of Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}, MDEA', 'corrected-Kamps': r"total pressures of P\'erez-Salado Kamps et al.\ at the temperatures corrected by Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}, MDEA"}
exact = [r for r in read(MEA + 'paper-evidence-341/same-data-comparison/published-deviations.json') if r['comparison'].startswith('exact:')]
own = lambda path: num(read(MEA + path)['pressure_aard_percent'], 2)
assert {r['n'] for r in exact} == {19} == {read(MEA + path)['n'] for path in ('same-data-comparison/matched-score.json', 'paper-evidence-341/same-data-comparison/matched-score.json')}
rows = [head(r"19 \COtwo partial pressures of Ma'mun et al.\ \cite{Mamun2005}, MEA near 393 K", 3)] + [[PUB[r['model']], (r'unclear\textsuperscript{a}' if 'role_note' in r else r['data_role']), f"${r['deviation_percent']:g}$"] for r in exact]
rows += [['This work, 16-parameter calibration', 'not fitted', own('same-data-comparison/matched-score.json')], ['This work, MEA model', 'not fitted', own('paper-evidence-341/same-data-comparison/matched-score.json')]]
mpub = read(MD + 'published-pressure-comparisons.json')['comparisons']
ZHANG_CHEN = r'Zhang and Chen, eNRTL \cite{zhangThermodynamicModelingCO22011}'  # their Table 14: AARD 6.8 % on the 82 Kuranov total pressures and 17.7 % on the 101 Ermatchkov CO2 partial pressures, both in their regression
for c in mpub:
    rows += [head(f"{c['measured_rows']} " + SHARED[c['group']], 3)] + [['Ermatchkov et al., parameter set ' + q['set'], {'predicted': 'not fitted'}.get(q['data_role'], q['data_role']), f"${q['mean_absolute_relative_deviation_percent']:g}$"] for q in c['published_parameter_sets']]
    if c['group'] == 'Ermatchkov': rows.append([ZHANG_CHEN, 'fitted', '$17.7$'])
    rows.append(['This work, MDEA model', c['data_role'] + ('; used to choose the initial parameters' if c['group'] == 'Ermatchkov' else ''), num(c['selected_point_mean_absolute_relative_deviation_percent'], 2)])
K422 = 'analyses/mdea_mea_workflow/results/kuranov-published-422/'
kstat, krae = read(K422 + 'statistics.json'), read(K422 + 'raeispour-table-4.json')
kroles = collections.Counter(r['role'] for r in mrows if r['group'] in ('Kuranov', 'Kuranov-binary'))
assert {('Uyan', '22.9'), ('Uyan', '34.4'), ('Wangler', '19.7')} <= {(r['reading'], r['printed']) for r in kstat['reconstruction'] if r['subset'] == 'K82'}
assert (krae['rows'], krae['AARD_percent'], krae['role']) == (82, 10.9, 'fitted') and kstat['present']['K82']['n'] == kstat['present']['K82']['solved'] == 82 and kroles == {'fitted': 70}
rows += [head(r'82 total pressures of Kuranov et al.\ \cite{kuranovSolubilitySingleGases1996}, MDEA\textsuperscript{b}', 3),
         [r'Uyan et al., ePC-SAFT \cite{Uyan2015}', 'not fitted', r'$22.9$\textsuperscript{c}'], [r'Wangler et al., ePC-SAFT \cite{Wangler2018}', 'not fitted', '$19.7$'],
         [r'Raeispour Shirazi and Lotfollahi, ePC-SAFT \cite{raeispourshiraziApplicationEPC_SAFTMBEoS2020}', 'fitted', f"${krae['AARD_percent']:g}$"], [ZHANG_CHEN, 'fitted', '$6.8$'],
         ['This work, MDEA model', r'70 fitted, of which 4 \COtwo-free; 12 not fitted', num(kstat['present']['K82']['AARD_percent'], 2)]]
table('published-models', 'Pressure deviations of published models and of this work on identical observations.', ['Observations and model', 'Role of these observations in the fit of that model', r'AARD (\%)'], rows, [.50,.36,.10],
      notes=r'AARD follows Eq.~\eqref{eq:aard} over the stated observations. Published values are those reported in each source, with the digits given there; the values of this work are calculated for the same observations. The 16-parameter calibration is defined in Section~\ref{sec:parameters}. Parameter sets I and II are the two sets of interaction parameters of Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}. \textsuperscript{a}Najafloo and Zarei do not define their average absolute deviation; it is assumed equivalent to Eq.~\eqref{eq:aard}, and their methods and conclusions describe the fitting differently. \textsuperscript{b}The published values are identified with the 82 total pressures of Table~2 of Kuranov et al.\ by their count. \textsuperscript{c}Recalculated as 34.4\,\% by Wangler et al.\ \cite{Wangler2018}.')
# Published parameters of Hong et al. on identical MEA observations: retained scores, no model call.
HONG = MEA + 'same-data-comparison/hong-2027/'
hong, hchecks = read(HONG + 'supplement-table.csv'), read(HONG + 'checks.json')
hsets = [(r'\COtwo partial pressure, AARD (\%)', [('canonical', 'strict grid', 'Six sources, inside the fitted range of Hong et al.'), ('canonical', 'all', 'Six sources, with the 13 Hilliard observations at 313.00--313.147 K'), ('wagner', 'all', 'Wagner et al.')]),
         (r'Heat of Kim and Svendsen, RMSE (kJ/mol \COtwo)', [(f'Kim {T} K', 'all', f'{T} K' + mark) for T, mark in (('313.15', r'\textsuperscript{a}'), ('353.15', r'\textsuperscript{a,b}'), ('393.15', ''))]),
         (r'Loaded-solution density, RMSE (kg/m$^3$)', [(b, 'all', label + r'\textsuperscript{c}') for b, label in (('Amundsen2009', 'Amundsen et al.'), ('Hartono2014', 'Hartono et al.'), ('Han2012', 'Han et al.'))])]
hrows = []
for heading, sets in hsets:
    hrows += [head(heading, 8)]
    for block, subset, label in sets:
        rs = [r for r in hong if (r['block'], r['subset']) == (block, subset)]  # two rows where Hong's slope is taken on both sides of a node
        r, fitted = rs[0], int(rs[0]['adopted_fitted'])
        assert rs and len({(q['n'], q['adopted'], q['polley_hedengren_2026'], q['locally_unstable']) for q in rs}) == 1 and {q['hong_role'] for q in rs} == {'not fitted'}
        hrows.append([label, r['n'], f"{fitted} fitted / {int(r['n']) - fitted} not fitted" if fitted else 'not fitted', 'not stated' if block == 'canonical' else r['polley_hedengren_2026_role'],
                      ' / '.join(num(q['hong'], 2) for q in rs), num(r['adopted'], 2), num(r['polley_hedengren_2026'], 2), '--' if heading.startswith('Loaded') else f"{r['locally_unstable']} of {r['n']}"])
table('supplement-hong-comparison', r'Deviations of the published parameters of Hong et al.\ \cite{hongModelingCO2Absorption2027}, of the MEA model and of the model of Polley and Hedengren \cite{polleyReactiveEPCSAFTModeling2026} on identical MEA observations at nominal 30 wt\%.',
      ['Observations', '$N$', 'Role in the MEA model', r'Role in \cite{polleyReactiveEPCSAFTModeling2026}', 'Hong et al.', 'MEA model', r'Ref.~\cite{polleyReactiveEPCSAFTModeling2026}', 'Fails the local test'], hrows, [.25, .04, .16, .10, .12, .08, .08, .10],
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
fitted_T = [float(f['T']) for f in afeed.values() if f['dataset'] == 'hartono-2021-calibration']
fig, ax = plt.subplots(figsize=(4.6, 3.5), constrained_layout=True)
ax.axhspan(min(fitted_T), max(fitted_T), color='0.87', lw=0, label='Temperatures of the fitted loaded-solution pressures')
ax.axhline(read('analyses/amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json')['reaction_ranges_K']['AMP-dissociation'][1], color='0.25', ls='--', lw=0.9, label='Upper limit of the measured R5 range')
for rs, label, style in [([r for r in states if r not in split], 'Detected instability, split not confirmed', dict(s=46, facecolors='none', edgecolors=colors[0], linewidths=0.9)), (split, 'Confirmed liquid–liquid split', dict(s=9, color=colors[1]))]:
    ax.scatter([float(r['loading_mol_CO2_per_mol_AMP']) for r in rs], [float(r['T_K']) for r in rs], label=label, **style)
ax.set(xlabel='Loading (mol CO$_2$/mol AMP)', ylabel='Temperature (K)', xlim=(0, 1.02), ylim=(308, 398))
ax.legend(loc='upper center', bbox_to_anchor=(.5, -.18), frameon=False, ncol=1, handletextpad=.5)
figure(fig, 'amp-splits.pdf')
read('analyses/dea_transfer/results/binary.json')
read(BASE + 'conditional-uncertainty.json')
read(BASE + 'checks.json')
read('analyses/dea_transfer/inputs/part-ii-346/route-current.json')
# Numbers quoted in the prose, recomputed from the retained files read above.
f2 = lambda v: f'{float(v):.2f}'
f1 = lambda v: f'{float(v):.1f}'  # the main text and the highlights give percent deviations to one decimal; tables and the supplement keep two
notfit = [float(r['AARD_percent']) for r in read(BASE + 'group-deviations.csv') if r['model'] == 'F2-carbamate' and r['role'] == 'not fitted'] + [mstats[g]['R1']['False']['AARD_percent'] for g in ('Ermatchkov', 'corrected-Kamps', 'Kuranov-413K', 'Sedighi', 'Xiao')] + [e['model']['AARD_percent'] for e in acomp['pressure_deviations_by_range'] if e['range'] == 'R1' and e['role'] == 'not fitted']
fitted_mdea = [float((mstats[g]['R1'].get('False') or mstats[g]['R1']['reaction not used'])['AARD_percent']) for g in {r['group'] for r in mrows if r['role'] == 'fitted'} if g != 'Kuranov']  # every fitted MDEA set but the loaded pressures
viii = next(r for r in data if r['identity'] + ':problem' == dsum['stability']['grid']['unavailable'][0])
kur, ermatchkov = mstats['Kuranov']['MDEA-dissociation'], next(c for c in mpub if c['group'] == 'Ermatchkov')
assert kur['True']['AARD_percent'] == kur['True']['bias_percent'] and hchecks['stable_fixed_vapor']['converged'] == hchecks['stable_fixed_vapor']['tried'], 'every MDEA pressure above R5 is overpredicted; every stable Hong state converged'
mea, dea, mdea = f1(escore['47 current-fitted pressures'][0]), f1(dsum['pressure']['fitted']['AARD_percent']), f1(mstats['Kuranov']['R1']['False']['AARD_percent'])
amp, afree_loaded = (f1(stable['loaded-pressure'][k]['AARD_percent']) for k in ('model', 'free'))
outside = f'{min(notfit):.1f}--{max(notfit):.1f}'
mcost = [f"{mbounded['data_cost']:.1f}", f"{mcomp['runs']['unbounded-2']['data_cost']:.1f}"]  # the reported fit and the fit without the bound, from one start
mratio = '{:.4f}--{:.4f}'.format(*mstability['descent_witnesses']['bubble_pressure_ratio_range'])  # assigned over calculated bubble pressure at the 27 vapor-directed measured states
ours, theirs = f1(ermatchkov['selected_point_mean_absolute_relative_deviation_percent']), f"{ermatchkov['published_parameter_sets'][0]['mean_absolute_relative_deviation_percent']:g}"
searched = dsum['stability']['grid']['states']
hstrict, hall, hwagner = (next(r for r in hong if (r['block'], r['subset']) == k) for k in (('canonical', 'strict grid'), ('canonical', 'all'), ('wagner', 'all')))
hong_main = [f1(hstrict['hong']), f1(hstrict['adopted']), f"the {hstrict['n']} observations", f"at {hstrict['locally_unstable']} of them"]
hong_supplement = [f"{f2(hstrict['hong'])}\\,\\%, the MEA model by {f2(hstrict['adopted'])}\\,\\% and the model of Polley and Hedengren by {f2(hstrict['polley_hedengren_2026'])}", ', '.join(f2(hall[k]) for k in ('hong', 'adopted')) + f" and {f2(hall['polley_hedengren_2026'])}",
                   f"{int(hall['locally_unstable']) + int(hwagner['locally_unstable'])} of the {int(hall['n']) + int(hwagner['n'])} measured pressure states", f"{hchecks['grid_stability']['locally unstable']} of the {sum(hchecks['grid_stability'].values())} nodes",
                   ' and '.join(f2(hchecks['full_pressure_replay_AARD_percent'][k]) for k in ('adopted', 'polley_hedengren_2026')), ' or '.join(f2(hchecks['kim_endpoint_AARD_313_353'][k]['AARD_percent']) for k in ('cool', 'warm'))]
# MEA model by temperature band (#409): every row recomputed from the retained points.
BANDS = MEA + 'stripper-temperature-409/'
bpts = read(BANDS + 'points.csv')
BAND_CITE = dict(Hilliard2008='Hilliard2008', Jou1995='Jou1995', Aronu2011='Aronu2011', Idris2014='idrisSpeciationMEACO2Adducts2014', Wagner2013='wagnerSolubilityCarbonDioxide2013', Mamun2005='Mamun2005',
                 Xu2011='Xu2011', Amundsen2009='Amundsen2009', Hartono2014='Hartono2014', Han2012='hanDensityWater12012', Sobrino2016='sobrinoViscosityDensityMeasurements2016', Concepcion2023='concepcionHeatCapacitiesDifferent2023',
                 Weiland1997='weilandHeatCapacityAqueous1997', Vinjarapu2024='HemaBhavya2025', Arcis2011='arcisEnthalpySolutionCarbon2011', Kim2007='Kim2007', Kim2014='Kim2014')
brel = lambda rows: [100 * (float(q['predicted']) - float(q['observed'])) / float(q['observed']) for q in rows]
bstat = {}
for b in read(BANDS + 'band-table.csv'):
    if b['cohort'] == 'all':
        d = brel([q for q in bpts if (q['property'], q['band'], q['role']) == (b['property'], b['band'], b['role'])])
        assert len(d) == int(b['n']) and math.isclose(sum(map(abs, d)) / len(d), float(b['AARD_percent']), rel_tol=1e-9) and abs(sum(d) / len(d) - float(b['mean_signed_relative_percent'])) < 1e-9, b
    bstat[b['property'], b['band'], b['role'], b['cohort']] = b
PROPS = {'CO2 partial pressure': r'\COtwo partial pressure', 'heat of absorption': 'Absorption heat', 'heat capacity': 'Heat capacity', 'density': 'Density'}
BROLE = {'fitted': 'fitted', 'not fitted': 'not fitted', 'not fitted, 15/45 wt%': r'not fitted, 15 and 45 wt\%', 'not fitted, source-flagged': r'not fitted, flagged\textsuperscript{a}'}
trange = lambda b: f"{float(b['T_min_K']):.0f}" + ('' if round(float(b['T_min_K'])) == round(float(b['T_max_K'])) else f"--{float(b['T_max_K']):.0f}")
brows = [[PROPS[b['property']], b['band'].capitalize() + ', ' + trange(b) + ' K', BROLE[b['role']], b['n'], f"${float(b['AARD_percent']):.2f}$", f"${float(b['mean_signed_relative_percent']):.2f}$",
          r'\cite{' + ','.join(BAND_CITE[c] for c in b['sources'].split()) + '}']
         for prop in PROPS for band in ('absorber', 'intermediate', 'stripper') for b in [v for (q, bd, _, c), v in bstat.items() if (q, bd, c) == (prop, band, 'all')]]
table('supplement-temperature-bands', 'Deviations of the MEA model by temperature band.', ['Property', 'Band', 'Role', '$N$', 'AARD (\\%)', 'MSRD (\\%)', 'Sources'], brows, [.17, .19, .19, .05, .09, .09, .16],
      notes=r'Absorber: $T\le\SI{353.2}{\kelvin}$; stripper: $T\ge\SI{370}{\kelvin}$; intermediate: between the two. Fitted observations are in the objective of the MEA model; no loaded-solution observation at or above \SI{370}{\kelvin} is fitted, and all were examined during development; ' + cai_high + r'. AARD follows Eq.~\eqref{main-eq:aard}; MSRD is the mean of $100\,(y^{\mathrm{calc}}-y^{\mathrm{obs}})/y^{\mathrm{obs}}$, negative where the calculated value is low. Pressures are at nominal 30 wt\% MEA unless stated. Absorption heats are heat releases per mole of \COtwo as each source defines them; the heats of Kim and Svendsen, Kim et al.\ and Vinjarapu et al.\ are calculated at \SI{1.734}{\mega\pascal}, the pressure reported by Vinjarapu et al. \textsuperscript{a}Four intervals of Kim and Svendsen at \SI{393.15}{\kelvin}, two inconsistent with their integrals and the first two additions from zero loading, reported separately.')
bget = lambda prop, band, role='not fitted', cohort='all': bstat[prop, band, role, cohort]
bpa, bps = bget('CO2 partial pressure', 'absorber'), bget('CO2 partial pressure', 'stripper')
assert round(float(bpa['AARD_percent'])) == round(float(bps['AARD_percent'])) == 25 and int(bget('CO2 partial pressure', 'absorber', cohort='six-source 30 wt%')['n']) + int(bget('CO2 partial pressure', 'stripper', cohort='six-source 30 wt%')['n']) == escore['112 current-not-fitted pressures'][1]
assert all('Wagner2013' in b['sources'].split() for b in (bpa, bps)) and float(bget('density', 'stripper', cohort='Han2012 loaded')['mean_signed_relative_percent']) < 0
bmin = {prop: min(brel([q for q in bpts if q['property'] == prop and q['band'] == 'stripper'])) for prop in ('heat capacity', 'density')}
bheat = {c: -float(bget('heat of absorption', 'stripper', cohort=c)['mean_signed_relative_percent']) for c in ('Vinjarapu 2024 Table 5 (replayed)', 'Kim et al. 2014 (replayed)', 'Kim and Svendsen 2007')}
assert min(bheat.values()) > 0
bkim = {role: [q for q in bpts if q['property'] == 'heat of absorption' and q['band'] == 'stripper' and q['cohort'] == 'Kim and Svendsen 2007' and q['role'] == role] for role in ('not fitted', 'not fitted, source-flagged')}
bkim_rmse = math.sqrt(sum((float(q['predicted']) - float(q['observed'])) ** 2 for rows in bkim.values() for q in rows) / sum(map(len, bkim.values())))
assert [len(v) for v in bkim.values()] == [16, 4] and f'{bkim_rmse:.2f}' == '31.77', 'the paper\'s Kim and Svendsen RMSE at 393.15 K covers the 16 unflagged and 4 flagged intervals'
bands_main = [rf"\SI{{{bkim_rmse:.2f}}}{{\kilo\joule\per\mole}} of \COtwo over all {sum(map(len, bkim.values()))} intervals, including the {WORDS[len(bkim['not fitted, source-flagged'])]} flagged for source problems", rf"by about 25\,\% both at 313--\SI{{353}}{{\kelvin}}, on {bpa['n']} observations, and at 373--\SI{{393}}{{\kelvin}}, on {bps['n']},", rf"the {escore['112 current-not-fitted pressures'][1]} not-fitted pressures of the six sources at 313--\SI{{393}}{{\kelvin}}",
              rf"the {bget('heat capacity', 'stripper')['n']} heat capacities and {bget('density', 'stripper')['n']} densities deviate on average by {f1(bget('heat capacity', 'stripper')['AARD_percent'])}\,\% and {f1(bget('density', 'stripper')['AARD_percent'])}\,\%", rf"by up to ${bmin['heat capacity']:.1f}$ and ${bmin['density']:.1f}$\,\%",
              rf"for the {bget('density', 'stripper', cohort='Han2012 loaded')['n']} loaded-solution densities of Han et al.\ \cite{{hanDensityWater12012}} are {f1(-float(bget('density', 'stripper', cohort='Han2012 loaded')['mean_signed_relative_percent']))}\,\% low on average",
              rf"low by {f1(bheat['Vinjarapu 2024 Table 5 (replayed)'])}\,\% for Vinjarapu et al.", rf"{f1(bheat['Kim et al. 2014 (replayed)'])}\,\% for Kim et al.", rf"{f1(bheat['Kim and Svendsen 2007'])}\,\% for Kim and Svendsen"]
# AMP prose (#412 handoff): the model, the free fit's splits, the slope choice and the cause of the splits.
acost = [aconf['selected_cost'], aconf['start_1']['cost']]
assert abs(acost[1] / acost[0] - 1) < 1e-9 and aconf['selected_cost'] == aconf['warm_cost']  # warm start from the free fit and declared start 1 agree
afreeq = {m['identity']: m for m in afree['parameter_table']}
aslope, aslope_se = afreeq['AMPH-water-slope']['value'], afreeq['AMPH-water-slope']['conditional_SE']
afixed = {q['identity']: q for q in acomp['parameters']}['AMPH-water-slope']['model']['value']
afreecost = next(f for f in afree['fits'] if f['start'] == afree['selection']['selected'])['cost']
aloaded = {g['group']: g['cost'] for g in read(AMM + 'group-costs.json')}['loaded-pressure'], afree['group_costs'][0]['cost']
assert afree['group_costs'][0]['group'] == 'loaded-pressure'
afk = lambda T: afreeq['AMPH-water-k']['value'] + aslope * (1 / T - 1 / 313.15)  # k_ij(T) of the free fit, reference temperature 313.15 K
aciftja = [read(AM + 'diagnosis/f0-scan.json')[v]['native']['measured_descent_by_set'].get('ciftja-2014', 0) for v in ('0.0', '-50.0', '-100.0')]
abank = {sum(r['supplied_trial_counts'].values()) for r in asearchrows}
assert len(abank) == 1
astate_split = [r for r in states if r['split']]
atrange = f"{min(r['T_K'] for r in astate_split):.2f}--" + r'\SI{' + f"{max(r['T_K'] for r in astate_split):.2f}" + '}{\\kelvin}'
adiam = {q['identity']: q for q in acomp['parameters']}['AMPCOO-segment-diameter']
assert adiam['model']['on_bound'] and adiam['model']['value'] == adiam['upper']
amp_main = [f"{['No', 'One', 'Two', 'Three'][asum['active_bounds']]} of the {WORDS[asum['fitted_parameters']]} fitted AMP parameters", rf"\SI{{{adiam['model']['value']:g}}}{{\angstrom}}",
            f"{next(iter(abank))} trial compositions", f"at least {aclass['counts']['confirmed']} confirmed splits", atrange, rf"{amp}\,\%", rf"{afree_loaded}\,\%"]
amp_supplement = [rf"\SI{{{AMINES[2][1]['carbamate-anion/dispersion_energy_over_k'][0]:.4f}}}{{\kelvin}}, and its interaction with water, ${AMINES[2][1]['carbamate-anion/water/k_ij'][0]:.4f}$", rf"\SI{{{adiam['lower']:.4f}}}{{\angstrom}}, as its lower bound",
                  f"{f2se['pair/carbamate-anion/water/k_ij']:.4f}", f"{aunc['conditional_standard_error']['AMP-hydrolysis-a']:.3f}",
                  f"{acost[0]:.4f}", f"{(afixed - aslope) / aslope_se:.2f}", f"{acost[0] - afreecost:.2f}", f"{aloaded[0]:.2f}", f"{aloaded[1]:.2f}",
                  rf"{asearch['supplied_minimum_tpd'] * 1e4:.2f}\times10^{{-4}}", f"{afk(353.22):.3f}", f"{afk(393.15):.3f}", ', '.join(map(str, aciftja[:-1])) + f' and {aciftja[-1]}']
# Prose values of the story pass (#429): each string repeats a table or retained-record value and is rebuilt from it here.
W420 = MEA + 'objective-weights-420/'
ecost = stage['MEA']['rss'] / 2  # the objective value is half the weighted sum of squares
wcai = [float(r['cost']) for r in read(W420 + 'MEA/contributions.csv') if r['group'] == 'Cai']
wband = [float(r['stage_SE']) / float(r['value']) for r in read(W420 + 'MEA/prediction-bands.csv') if r['group'] == 'common149: partial_pressure']
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
assert r4[k := 'dea']['delta_ln_K4'] < 0 < r4['amp']['delta_ln_K4'] and r4['amp']['delta_h_J_mol'] == r4['amp']['bounds']['enthalpy'][0]
cother = [v for k, v in cgm.items() if k != 'P0' and not k.endswith('-refit')]
dcation, mcation = AMINES[0][1], AMINES[1][1]
stated = {'main.tex': [mea, dea, pair, f'objective values of {f1(afreecost)} and {f1(acost[0])}', f'gives {nsplit} calculated liquid--liquid splits', f'none in {nsearch} finite phase-stability searches', rf"\SI{{{fixedp['P_Pa'] / 1e6:.1f}}}{{\mega\pascal}}"],
          'sections/introduction.tex': [mea, pair],
          'sections/conclusion.tex': [mea, dea, mdea, pair, f'{nsplit} confirmed liquid--liquid splits', f'none in {nsearch} finite searches', rf"\SI{{{fixedp['P_Pa'] / 1e6:.3f}}}{{\mega\pascal}}"],
          'sections/transfer_results.tex': [outside, f"all {kur['True']['rows']} pressures", f'{min(fitted_mdea):.1f}--{max(fitted_mdea):.1f}', f'{searched-1} of the {searched}', *amp_main, *hong_main, *bands_main[1:],
                                            f"their bias equals their AARD, {f1(kur['True']['AARD_percent'])}",
                                            rf"Of the \num{{{msearch['states']}}} MDEA searches, {msum['unavailable_searches']} did not finish, {next(c['count'] for c in mstability['unavailable_by_cause'] if c['cause'] == 'pressure reference')} of them at grid states",
                                            f'objective value of {afreecost:.2f}', f'the objective value is {acost[0]:.2f}', rf'\SI{{{aslope:.0f}}}{{\kelvin}}$ and a conditional standard error of \SI{{{aslope_se:.0f}}}{{\kelvin}}', f'{(afixed - aslope) / aslope_se:.2f} standard errors away',
                                            rf'from ${afk(353.22):.3f}$ at \SI{{353}}{{\kelvin}} to ${afk(393.15):.3f}$', f'all {nsearch} searches finish', f'from {mcost[1]} to {mcost[0]}',
                                            rf"\SI{{{fixedp['P_Pa'] / 1e6:.3f}}}{{\mega\pascal}}", f"${sci(fatt['Gibbs_decrease_over_RT_mol'], 3)}$ mol", f"${sci(fatt['numerical_error_over_RT_mol'], 1)}$ mol", rf'{fdense:.1f}\,\% of the moles',
                                            rf"from {dp('Horstmann heat')[0]:.0f} to {f1(dp('Horstmann heat')[1])}\,\%", rf"from {f1(dp('Horstmann VLE')[0])} to {f1(dp('Horstmann VLE')[1])}\,\%", rf"by {f1(dp('Lawson')[1])} instead of {f1(dp('Lawson')[0])}\,\%",
                                            rf"the {dpair['outside', 'not fitted']['reference']['rows']} \COtwo partial pressures outside the fit deviate by {f1(dp('outside', 'not fitted')[1])} instead of {f1(dp('outside', 'not fitted')[0])}\,\%", rf"by {f1(dp('Carson')[1])} instead of {f1(dp('Carson')[0])}\,\%",
                                            *(rf'by ${v:.3f}\pm{se:.3f}$, a factor of {ratio:.3f}' for v, se, ratio in map(r4q, ('dea', 'amp'))), rf"$\num{{{r4['dea']['delta_h_J_mol']:.0f}}}\pm\SI{{{r4['dea']['SE_h_J_mol']:.0f}}}{{\joule\per\mole}}$", rf"\SI{{{r4['amp']['delta_h_J_mol']:.0f}}}{{\joule\per\mole}}",
                                            rf'{mea}\,\% from', rf'{dea}\,\% from', rf'{mdea}\,\% from', rf'{amp}\,\% from', rf"it deviates by {f1(kstat['present']['K82']['AARD_percent'])}\,\%", rf'by {ours}\,\%, against {theirs}\,\%',
                                            rf'from {f1(bdea[0])} to {f1(bdea[1])}\,\% for DEA and from {f1(bmdea[0])} to {f1(bmdea[1])}\,\% for MDEA', f"by {carm['M1']['delta']:.2f} at fixed parameters", f"by {carm['M3']['delta']:.1f}, which a refit"],
          'sections/mea_system_modeling_results.tex': bands_main[:1] + [f1(read(MEA + path)['pressure_aard_percent']) for path in ('same-data-comparison/matched-score.json', 'paper-evidence-341/same-data-comparison/matched-score.json')] + [f"AARD of {escore['Jakobsen carbonate share'][0]:.1f}",
                                            f"ratios is {cgm['P0']:.3f}", f'between {min(cother):.3f} and {max(cother):.3f}', f"by {-crefit['M3-refit']['delta_cost']:.3f} but also lowers the ratio, to {cgm['M3-refit']:.3f}", rf'{100 * min(wband):.1f}--{100 * max(wband):.1f}\,\%'],
          'sections/data_methods.tex': [rf"{100 * sum(wcai) / ecost:.1f}\,\% of the objective value, {ecost:.2f}", f"leaves {stage['MEA']['na']} observations and {stage['MEA']['stage_denominator']} residual degrees of freedom", f"leaves {stage['MDEA']['na']} and {stage['MDEA']['stage_denominator']}",
                                        rf"by {100 * (stage['MEA']['SE_multiplier'] - 1):.1f}\,\% and those of MDEA by {100 * (stage['MDEA']['SE_multiplier'] - 1):.1f}\,\%"],
          'sections/epc_saft_equation_of_state.tex': [rf"\SI{{{dcation['protonated-diethanolamine/segment_diameter'][0]:.3f}}}{{\angstrom}} for \ce{{DEAH+}} and \SI{{{mcation['protonated-methyldiethanolamine/segment_diameter'][0]:.3f}}}{{\angstrom}} for \ce{{MDEAH+}}",
                                                      rf"of {veq(dcation, 'protonated-diethanolamine'):.3f} and \SI{{{veq(mcation, 'protonated-methyldiethanolamine'):.3f}}}{{\angstrom}}"],
          'submission/highlights.txt': [f'MEA {mea}%', f'DEA {dea}%', f'MDEA {mdea}%', f'AMP {amp}%', f'{nsplit} calculated splits'],
          'supplement.tex': [*origins, f"loading of {float(viii['row']['alpha_mol_CO2_per_mol_DEA']):.3f} mol/mol", rf"\num{{{mstability['distinct_calculations']}}} distinct states", *mcost, f'{mcorr:.3f}', mratio, f2(mstats['Kuranov']['R1']['False']['AARD_percent']), *amp_supplement, *hong_supplement, f"with the Hong parameters, {hchecks['stable_fixed_vapor']['tried']} pass the test",
                             'lies ' + '{:.3f}, {:.3f} and {:.3f}'.format(*r4T('dea', 'delta_ln_K4')) + ' below', 'standard errors of ' + '{:.3f}, {:.3f} and {:.3f}'.format(*r4T('dea', 'SE_ln_K4')), 'lies ' + '{:.3f}, {:.3f} and {:.3f}'.format(*r4T('amp', 'delta_ln_K4')) + ' above',
                             rf"\SI{{{f2se['component/carbamate-anion/dispersion_energy_over_k']:.2f}}}{{\kelvin}}", f"by {carm['M1']['delta']:.3f}", f"by {carm['M3']['delta']:.3f}", f"falls {-crefit['M3-refit']['delta_cost']:.3f} below", f"falls to {cgm['M3-refit']:.4f}", f'tested changes is {max(cother):.4f}',
                             f'contribute {wcai[0]:.3f} and {wcai[1]:.3f} to the objective value of {ecost:.3f}, together {100 * sum(wcai) / ecost:.2f}', f"factor of that equation is {stage['MEA']['stage_variance']:.8f}", f"MDEA variance factor is {stage['MDEA']['stage_variance']:.8f}", f"would give {stage['MDEA']['variance']:.8f}",
                             f"{fixedp['P_Pa'] / 1e6:.3f} MPa", rf'{fdense:.3f}\,\% of the moles', f"${sci(fatt['Gibbs_decrease_over_RT_mol'], 5)}$ mol", rf"the {f2(kstat['present']['K82']['AARD_percent'])}\,\% of the MDEA model"]}
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
assert f1(sbkur[0]) == mdea
def sbset(sets):  # count-weighted over the sets: the AARD over all of their observations
    cases = [sbcomp[g]['original'] for g in sets]
    n = sum(c[0]['relative_rows'] for c in cases)
    return n, [sum(c[i]['relative_rows'] * c[i]['AARD_percent'] for c in cases) / n for i in range(3)]
(sbtn, sbtot), (sbpn, sbpart) = sbset(('corrected-Kamps', 'Kuranov-413K', 'Sedighi')), sbset(('Ermatchkov', 'Xiao'))
assert sbtn + sbpn == sbcomp['all pressures not fitted']['original'][0]['relative_rows'] and all(abs(v - w) < 1e-9 for v, w in zip(sbset(('corrected-Kamps', 'Kuranov-413K', 'Sedighi', 'Ermatchkov', 'Xiao'))[1], sbout)), 'total and CO2 partial pressures are every pressure outside the objective'
assert max(abs(v[2] - v[0]) for v in (sbkur, sbtot, sbpart)) < 0.1 and sbtot[1] < sbtot[0] and sbpart[1] > sbpart[0], 'at the upper value the displayed deviations change by less than 0.1 points; at the lower value total pressures improve and CO2 partial pressures worsen'
sbsplits = WORDS[sbsearch['low']['counts']['confirmed_distinct_splits']]
stated['main.tex'] += [rf'from {f1(sbkur[0])} to {f1(sbkur[1])}\,\%', rf'\COtwo partial-pressure AARD from {f1(sbpart[0])} to {f1(sbpart[1])}\,\%', f"introduces {sbsplits} calculated splits"]
stated['submission/chemrxiv.md'] = [f'raises outside-fit CO₂ partial-pressure AARD from {f1(sbpart[0])} to {f1(sbpart[1])}%']
stated['submission/cover_letter.md'] = [f'raises that of {sbpn} outside-fit CO₂ partial pressures from {f1(sbpart[0])} to {f1(sbpart[1])} %']
stated['sections/conclusion.tex'] += [rf'from {f1(sbkur[0])} to {f1(sbkur[1])}\,\%', rf'lowers that of {sbtn} outside-fit total pressures from {f1(sbtot[0])} to {f1(sbtot[1])}\,\%, raises that of {sbpn} outside-fit \COtwo partial pressures from {f1(sbpart[0])} to {f1(sbpart[1])}\,\%', f"at {sblow['k']:.4f} instead of {sbprof['center']['k']:.4f} raises the refitted MEA objective by {sbrise[0]:.3f}", f"in {sbmea['grid']['states'] + sbmea['offset']['states'] + sbmea['census']['states']} searches"]
stated['sections/mea_system_modeling_results.tex'] += [f"The {sbmea['grid']['states'] + sbmea['offset']['states'] + sbmea['census']['states']} finite searches"]
stated['submission/highlights.txt'] += [f'from {f1(sbkur[0])} to {f1(sbkur[1])}%']
stated['sections/transfer_results.tex'] += [f"{sbcorr['pair/carbamate-anion/water/k_ij']:.3f} with the carbamate--water and ${sbcorr['pair/protonated-monoethanolamine/water/k_ij']:.3f}$ with",
    f"These values, {sblow['k']:.4f} and its upper bound {sbhigh['k']:.1f} against {sbprof['center']['k']:.4f} in the MEA model, raise the refitted MEA objective by {sbrise[0]:.3f} and {sbrise[1]:.3f}, within {sballow:.4f}",
    rf"deviate by {f1(sbkur[1])} instead of {f1(sbkur[0])}\,\%, while outside the objective the {sbtn} total pressures deviate by {f1(sbtot[1])} instead of {f1(sbtot[0])}\,\% and the {sbpn} \COtwo partial pressures by {f1(sbpart[1])} instead of {f1(sbpart[0])}\,\%",
    f"{sbsearch['low']['counts']['unavailable_records']} instead of {msum['unavailable_searches']} searches do not finish, and {WORDS[sbsearch['low']['counts']['confirmed_distinct_splits']]} liquid--liquid splits are confirmed"]
stated['supplement.tex'] += [f"at the {sbmea['grid']['states'] + sbmea['offset']['states']} liquid and {sbmea['census']['states']} liquid--vapor states",
    f"At the lower bound, ${sbprof['points']['-0.5']['k']:g}$, the objective rises by {sbprof['points']['-0.5']['cost'] - sbprof['center_cost']:.2f}, so the midpoint {sblow['k']:.4f} was taken"]
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
