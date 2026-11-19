"""Present retained DEA, MDEA and AMP results, with a byte-for-byte display check; no model calls."""
import csv
import hashlib
import json
import sys
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LATEX = ROOT / 'docs/scientific/latex'
BASE = 'analyses/dea_transfer/results/retransfer-398/'
OBSERVATIONS = 'analyses/dea_transfer/results/retransfer-346/f2-report-1/data-rows.json'  # source rows only; every calculated value is taken from BASE
outputs = {}
sources = {}

def read(name):
    path = ROOT / name
    sources[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text()) if name.endswith('.json') else list(csv.DictReader(path.open()))

def emit(name, text):
    outputs[LATEX / name] = text

# Data sets: display name, citation key and measured property.
SETS = {
    'Lawson': ('Lawson and Garst', 'lawsonGasSweeteningData1976', r'$p_{\COtwo}$'),
    'Carson': ('Carson et al.', 'carsonEnthalpySolutionCarbon2000', 'integral heat'),
    'Lawson-394K': ('Lawson and Garst, highest temperature', 'lawsonGasSweeteningData1976', r'$p_{\COtwo}$'),
    'SeoHong': ('Seo and Hong', 'seoSolubilitiesCarbonDioxide1996', r'$p_{\COtwo}$'),
    'Lal': ('Lal et al.', 'lalSolubilityH2SCO21985', r'$p_{\COtwo}$'),
    'Weiland': ('Weiland et al.', 'Weiland1998', 'density'),
    'Lawson-VIII': ('Lawson and Garst, Table VIII', 'lawsonGasSweeteningData1976', r'$p_{\COtwo}$'),
    'Bottinger-DEA_plus_DEAH': (r'B\"ottinger et al., DEA + DEAH$^+$', 'Bottinger2008', 'mole fraction'),
    'Bottinger-DEACOO': (r'B\"ottinger et al., carbamate', 'Bottinger2008', 'mole fraction'),
    'Bottinger-HCO3': (r'B\"ottinger et al., bicarbonate', 'Bottinger2008', 'mole fraction'),
    'Cai': ('Cai et al.', 'caiBinaryIsobaricVaporLiquid1996', 'bubble pressure'),
    'Horstmann': ('Horstmann et al.', 'horstmannPhaseEquilibriumExcess2002', 'excess enthalpy'),
}
LAWS = {'carbamate-hydrolysis': 'R4', 'DEA-dissociation': 'R5'}  # reaction numbers as in Part I
RANGE_NOTE = 'in, out or mixed relative to the measured temperature range of the carbamate hydrolysis constant (R4) and of the DEA dissociation constant (R5); ---: the calculation uses no reaction'

def name(group, cite=False):
    return SETS[group][0] + (r' \cite{' + SETS[group][1] + '}' if cite else '')

def num(value, digits=3):
    return f'${float(value):.{digits}f}$'

def span(values, fmt):
    return fmt(min(values)) if min(values) == max(values) else fmt(min(values)) + '--' + fmt(max(values))

def table(name, caption, headers, rows, widths, long=False, notes=''):
    columns = ''.join(r'>{\raggedright\arraybackslash}p{' + str(w) + r'\linewidth}' for w in widths)
    head = ' & '.join(headers) + r' \\ \midrule' + '\n'
    keep = lambda row: row[0].startswith(r'\addlinespace') or (row[0].startswith('R4, ') and not row[0].endswith('$f$'))
    body = '\n'.join(' & '.join(map(str, row)) + r' \\' + ('*' if keep(row) else '') for row in rows)
    if long:
        text = r'\begingroup\small\setlength{\tabcolsep}{2pt}\begin{longtable}{@{}' + columns + '@{}}\n'
        text += r'\caption{' + caption + r'}\label{tab:p2-' + name + r'}\\' + '\n'
        text += r'\toprule ' + head + r'\endfirsthead\toprule ' + head + r'\endhead\bottomrule\endfoot'
        if notes:
            text += r'\bottomrule\multicolumn{' + str(len(widths)) + r'}{@{}p{0.95\linewidth}@{}}{\footnotesize ' + notes + r'}\\\endlastfoot'
        text += '\n' + body + '\n' + r'\end{longtable}\endgroup' + '\n'
    else:
        text = r'\begin{table}[htbp]\small\setlength{\tabcolsep}{2pt}\caption{' + caption + r'}\label{tab:p2-' + name + '}\n'
        text += r'\begin{tabular}{@{}' + columns + '@{}}\n' + r'\toprule ' + head
        text += body + '\n' + r'\bottomrule\end{tabular}'
        if notes:
            text += '\n' + r'\par\smallskip{\footnotesize\raggedright ' + notes + r'\par}'
        text += r'\end{table}' + '\n'
    emit('tables/part2/' + name + '.tex', text)

params = read(BASE + 'parameter-values.csv')
p = {r['parameter']: r for r in params}
fitted_names = [r'$k_{\mathrm{DEAH^+,w}}$', r'$k_{\mathrm{DEACOO^-,w}}$', r'R4 constant term $a$', r'R4 enthalpy increment $\delta h$']
rows = [[label + (' / (J/mol)' if r['unit'] == 'J/mol' else ''), num(r['value']), num(r['conditional_SE']), '['+num(r['lower'])+', '+num(r['upper'])+']'] for label, r in zip(fitted_names, params[:4])]
table('dea-fitted-current', 'Fitted DEA parameters with conditional standard errors and bounds.', ['Parameter','Value','Standard error','Bounds'], rows, [.34,.15,.17,.28],
      notes='No parameter is on a bound. $a$ and $\\delta h$ refer to the final R4 correlation (Section~\\ref{sec:p2-reactions}).')
rows = []
for label, key, digits in [('Segment count','segment_count',4), (r'$\sigma$ / \AA','segment_diameter',4), (r'$\epsilon/k_B$ / K','dispersion_energy_over_k',3), (r'$d^{\mathrm{Born}}$ / \AA','born_diameter',4)]:
    vals = [num(p[s+'/'+key]['value'],digits) if s+'/'+key in p else '---' for s in ['diethanolamine','protonated-diethanolamine','carbamate-anion']]
    rows.append([label,*vals])
table('dea-fixed-current', 'Fixed ePC-SAFT parameters of the DEA species.', ['Parameter','DEA',r'DEAH$^+$',r'DEACOO$^-$'],rows,[.30,.20,.20,.20],
      notes='Neutral DEA values are from Nasrifar and Tafazzol \\cite[Table~2]{Nasrifar2010}; DEAH$^+$ keeps the neutral-chain values and DEACOO$^-$ is a single sphere (Section~\\ref{sec:p2-species}). Born diameters equal segment diameters.')
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
    g, f4 = (lambda v: f'${v:g}$'), (lambda v: num(v,4))
    if get('x_water'): return r'$x_{\mathrm{w}}=\,$' + span(get('x_water'), f4), '---'
    if get('DEA_kmol_per_m3'): amine = span(get('DEA_kmol_per_m3'), f4) + r' kmol/m$^3$'
    else: amine = span(get('DEA_mass_percent') or get('DEA_mass_fraction', 100), g) + r' wt\%'
    if group == 'Carson': return amine, span(get('x_CO2'), f4) + r'\textsuperscript{a}'
    return amine, span(get('alpha_mol_CO2_per_mol_DEA') or get('alpha_mol_CO2_per_mol_amine'), f4)

rows = []
for group in dict.fromkeys(r['group'] for r in data):
    rs = [r for r in data if r['group']==group]
    t = [r['T_K'] for r in rs]
    rows.append([name(group, cite=True), SETS[group][2], rs[0]['role'], str(len(rs)), span(t, lambda v: num(v,2)), *composition(group), *marks(group)])
table('dea-data-current', 'Experimental data for the DEA system and their use in fitting.', ['Data set','Property','Role',r'$N$',r'$T$ / K','Composition',r'$\alpha$ / (mol/mol)','R4','R5'],rows,[.195,.095,.10,.035,.13,.12,.13,.06,.06],
      notes="$N$: number of observations. Composition: DEA content of the unloaded solution, or water mole fraction $x_{\\mathrm{w}}$ for the binary sets. R4 and R5: " + RANGE_NOTE + " (Section~\\ref{sec:p2-data}). All data for loaded solutions lie inside the correlation range of R1--R3, whose measured coverage is unverified. The water--DEA interaction was fitted beforehand to the 365.15 K vapor--liquid equilibria of Horstmann et al.\\ \\cite{horstmannPhaseEquilibriumExcess2002}, which are not listed. The pressures not fitted were inspected before the choice between the 2 numerically tied DEA fits (Section~\\ref{sec:p2-data}). \\textsuperscript{a}Mole fraction of added \\COtwo.")
rows = []
for r in groups:
    if r['model'] != '05e94210': continue
    m = marks(r['group'])
    rows.append([name(r['group']),r['role'],r['rows']+'/'+r['relative_rows'],num(r['AARD_percent'],2),num(r['bias_percent'],2),'---' if m == ['---','---'] else '/'.join(m)])
table('dea-deviations-current', 'Deviations of the present model from the DEA data, by data set and role.', ['Data set','Role',r'$N/N_{\mathrm{rel}}$',r'AARD / \%',r'Bias / \%','R4/R5'],rows,[.34,.17,.10,.11,.11,.11],
      notes="$N/N_{\\mathrm{rel}}$: calculated observations / observations with a defined relative deviation. AARD and bias follow Eq.~\\eqref{eq:p2-deviation}; bias is calculated minus measured, divided by measured. R4/R5: " + RANGE_NOTE + '.')
ranges = read(BASE + 'range-deviations.csv')
rows = []
for group in dict.fromkeys(r['group'] for r in data):
    cells = []
    for law in LAWS:
        for outside in ['False','True']:
            hit = [r for r in ranges if r['model']=='05e94210' and r['group']==group and r['law']==law and r['outside_range']==outside]
            cells += [hit[0]['rows']+'/'+hit[0]['relative_rows'], num(hit[0]['AARD_percent'],2)] if hit else ['---','---']
    if set(cells) != {'---'}: rows.append([name(group),*cells])
    else: assert group in ['Cai','Horstmann'], 'Only the binary comparisons use no reaction correlation'
top = ' & ' + ' & '.join(r'\multicolumn{2}{@{}l}{' + law + ', ' + side + '}' for law in LAWS.values() for side in ['inside','outside']) + r' \\ '
table('dea-ranges-current','Deviations of the present model inside and outside the measured temperature ranges of the carbamate hydrolysis constant (R4) and the DEA dissociation constant (R5).', [top + 'Data set',*[r'$N/N_{\mathrm{rel}}$',r'AARD / \%']*4],rows,[.26,.075,.085,.075,.085,.075,.085,.075,.085],
      notes='$N/N_{\\mathrm{rel}}$: calculated observations / observations with a defined relative deviation; ---: no observations. The binary sets use no reaction and are omitted. All data for loaded solutions lie inside the correlation range of R1--R3, whose measured coverage is unverified.')
SPECIES = {'diethanolamine': 'DEA', 'protonated-diethanolamine': r'DEAH$^+$', 'carbamate-anion': r'DEACOO$^-$', 'bicarbonate-anion': r'HCO$_3^-$', 'carbonate-anion': r'CO$_3^{2-}$', 'hydronium-cation': r'H$_3$O$^+$', 'hydroxide-anion': r'OH$^-$', 'carbon-dioxide': r'CO$_2$', 'water': r'H$_2$O'}
QUANTITY = {'dispersion_energy_over_k': r'dispersion energy $\epsilon/k_B$', 'segment_count': 'segment count', 'segment_diameter': r'segment diameter $\sigma$', 'solvation_factor': 'solvation factor', 'dielectric_volume': r'dielectric volume $d_V$', 'dielectric_temperature': r'dielectric temperature $d_T$', 'charge_number': 'charge number', 'molar_mass': 'molar mass', 'born_diameter': r'Born diameter $d^{\mathrm{Born}}$', 'debye_huckel_diameter': r'Debye--H\"uckel diameter', 'packing_diameter': 'packing diameter', 'charged_molecule_ion': 'charged-chain self-dispersion retained (1 = yes)', 'k_ij': r'$k_{ij}$', 'k_ij_reciprocal_temperature_slope': r'reciprocal-temperature slope of $k_{ij}$'}
FITTED = dict(zip([r['parameter'] for r in params[:4]], fitted_names))

def quantity(key):
    """Return the table group and the row label of one parameter key."""
    parts = key.split('/')
    if key in FITTED: return 'Fitted parameters', FITTED[key]
    if parts[0] == 'association':
        if parts[-1] == 'multiplicity': return 'Association', f'{SPECIES[parts[1]]}, number of type-{parts[2]} sites'
        return 'Association', f'{SPECIES[parts[1]]}, site {parts[2]}--site {parts[4]} ' + {'energy_over_k': r'association energy $\epsilon^{AB}/k_B$', 'volume': r'association volume $\kappa^{AB}$'}[parts[-1]]
    if parts[0] in LAWS: return 'Equilibrium-constant correlations', LAWS[parts[0]] + ', $' + parts[1] + '$'
    return ('Binary dispersion interactions' if len(parts) == 3 else 'Species parameters'), '--'.join(SPECIES[s] for s in parts[:-1]) + ', ' + QUANTITY[parts[-1]]

units = {'K^2': r'K$^2$', '1/K^2': r'K$^{-2}$', 'kelvin': 'K', 'angstrom': r'\AA', 'liter / mole': 'L/mol', 'kilogram / mole': 'kg/mol', 'dimensionless': '1', 'elementary-charge': '$e$'}
rows, heading = [], None
for r in params:
    group, label = quantity(r['parameter'])
    if group != heading:
        heading = group
        rows.append([r'\addlinespace\multicolumn{4}{@{}l}{\textit{' + group + '}}'])
    rows.append([label,'$' + repr(float(r['value'])).removesuffix('.0') + '$',units.get(r['unit'],r['unit']),r['fitted_or_fixed']])
table('dea-all-current','Amine-specific parameter values of the DEA model at full precision.', ['Parameter','Value','Unit','Role'],rows,[.44,.30,.12,.09],long=True,
      notes='Standard errors and bounds of the fitted parameters are in Table~\\ref{main-tab:p2-dea-fitted-current} of the main text. The R4 coefficients $a$ and $b$ are the final coefficients after the fit, not additional independent fitted parameters. R4: carbamate hydrolysis; R5: DEA dissociation. The archived parameter file gives the source and basis of each value.')
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
    outputs[LATEX/'figures/part2'/name] = buffer.getvalue()
    plt.close(fig)
plt.rcParams.update({'font.family': 'STIXGeneral', 'mathtext.fontset': 'stix', 'pdf.fonttype': 42,
                     'font.size': 8, 'legend.fontsize': 8, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
                     'axes.labelsize': 9, 'axes.titlesize': 9})
colors = ['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9']
fig,axes=plt.subplots(2,2,figsize=(6.48,5.8),constrained_layout=True)
for ax, groups, title in zip(axes.flat,[('Lawson','Lawson-394K'),('SeoHong',),('Lal',),('Carson',)],'abcd'):
    cs=[r for r in curves if r['group'] in groups]
    for index,label in enumerate(dict.fromkeys(r['curve'] for r in cs)):
        line=sorted([r for r in cs if r['curve']==label],key=lambda r:r['loading'])
        color=colors[index%len(colors)]
        outside=line[0]['outside_ranges']['DEA-dissociation'] is True
        hydrolysis=line[0]['outside_ranges']['carbamate-hydrolysis'] is True
        assert all((r['outside_ranges']['DEA-dissociation'],r['outside_ranges']['carbamate-hydrolysis'])==(outside,hydrolysis) for r in line)
        assert not outside or hydrolysis, 'Figure markers require outside both intervals'
        caption=f"{line[0]['T_K']:.2f} K" if groups!=('Carson',) else f"{float(line[0]['row']['DEA_mass_fraction'])*100:g} wt%"
        ax.plot([r['loading'] for r in line],[r['value']/1000 for r in line],'--' if outside else ':' if hydrolysis else '-',color=color,label=caption)
        obs=[r for r in data if r['group'] in groups and abs(r['T_K']-line[0]['T_K'])<1e-8]
        if groups==('Carson',): obs=[r for r in obs if r['row']['DEA_mass_fraction']==line[0]['row']['DEA_mass_fraction']]
        assert all((r['outside_ranges']['DEA-dissociation'],r['outside_ranges']['carbamate-hydrolysis'])==(outside,hydrolysis) for r in obs)
        ax.scatter([loading(r['row']) for r in obs],[r['observed']/1000 for r in obs],marker='^' if outside else 's' if hydrolysis else 'o',facecolors=color if line[0]['group'] in ('Lawson','Carson') else 'none',edgecolors=color,s=25)
    ax.set_title(f'({title})', loc='left'); ax.set(xlabel='Loading (mol CO$_2$/mol DEA)',ylabel='Integral heat (kJ/mol CO$_2$)' if groups==('Carson',) else 'CO$_2$ partial pressure (kPa)',yscale='linear' if groups==('Carson',) else 'log')
    ax.legend(ncol=2, columnspacing=.7, handlelength=1.8, handletextpad=.4)
figure(fig,'dea-current-measured-model.pdf')
fig,axes=plt.subplots(1,2,figsize=(6.48,3.0),constrained_layout=True)
for ax,group,scale,letter in [(axes[0],'Horstmann',1,'a'),(axes[1],'Cai',0.001,'b')]:
    ps=[r for r in data if r['group']==group]
    ax.scatter([float(r['row']['x_water']) for r in ps],[r['observed']*scale for r in ps],facecolors='none',edgecolors=colors[0],label='Measured')
    ax.scatter([float(r['row']['x_water']) for r in ps],[r['value']*scale for r in ps],marker='x',color=colors[1],label='Present model')
    ax.set_title(f'({letter})', loc='left'); ax.set(xlabel='Water mole fraction',ylabel='Excess enthalpy (J/mol mixture)' if group=='Horstmann' else 'Bubble pressure (kPa)')
    ax.legend(fontsize=8, loc='center' if group=='Horstmann' else 'upper right')
figure(fig,'dea-current-binary-comparisons.pdf')
# MDEA and AMP: the same displays, built from each amine's retained files.
MD = 'analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/'
AM = 'analyses/amp_transfer/results/retransfer-344-05e94210/'
PCO2, PTOT, PBUB, HEAT, XFRAC = r'$p_{\COtwo}$', 'total pressure', 'bubble pressure', 'integral heat', 'mole fraction'
KURANOV, MERKLEY, NMR = 'kuranovSolubilitySingleGases1996', 'merkleyEnthalpiesAbsorptionCarbon1987', 'bottingerOnlineNMRSpectroscopic2008'
MSETS = {
    'Kuranov': ('Kuranov et al.', KURANOV, PTOT), 'Kuranov-binary': (r'Kuranov et al., \COtwo-free', KURANOV, PBUB),
    'Jakobsen': ('Jakobsen et al.', 'Jakobsen2005', 'species ratios'), 'Carson': ('Carson et al.', 'carsonEnthalpySolutionCarbon2000', HEAT),
    'Merkley': ('Merkley et al.', MERKLEY, HEAT), 'Cp': ('Weiland et al.', 'weilandHeatCapacityAqueous1997', 'heat capacity'),
    'loaded-density': ('Weiland et al.', 'Weiland1998', 'density'), 'unloaded-density': ('Sobrino et al.', 'sobrinoViscosityDensityMeasurements2016', 'density'),
    'Kim': ('Kim et al.', 'kimEbulliometricDeterminationVaporLiquid2008', PBUB), 'Ermatchkov': ('Ermatchkov et al.', 'ermatchkovSolubilityCarbonDioxide2006', PCO2),
    'corrected-Kamps': (r'P\'erez-Salado Kamps et al., corrected', 'ermatchkovSolubilityCarbonDioxide2006', PTOT),
    'Bottinger-amine-sum-5bar': (r'B\"ottinger et al., MDEA + MDEAH$^+$, 0.5 MPa', NMR, XFRAC), 'Bottinger-bicarbonate-5bar': (r'B\"ottinger et al., bicarbonate + carbonate, 0.5 MPa', NMR, XFRAC),
    'Bottinger-amine-sum-25bar': (r'B\"ottinger et al., MDEA + MDEAH$^+$, 2.5 MPa', NMR, XFRAC), 'Bottinger-bicarbonate-25bar': (r'B\"ottinger et al., bicarbonate + carbonate, 2.5 MPa', NMR, XFRAC),
    'Merkley-half-loading': ('Merkley et al., half the reported loading', MERKLEY, HEAT), 'Merkley-outside': ('Merkley et al., other states', MERKLEY, HEAT),
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

def amine(tag, label, sets, rows, stats, laws, basis, widths, note, extra_head=(), extra=lambda key: []):
    """Data, deviation and range tables of one amine from its retained rows and statistics."""
    groups, data_rows, dev_rows, range_rows = {}, [], [], []
    for r in rows: groups.setdefault(r['key'], []).append(r)
    for key, rs in groups.items():
        title, source, quantity = sets[key]
        m, all_rows = mark(rs, laws), stats[key]['R1']
        s = all_rows.get('False') or all_rows['reaction not used']
        assert s['rows'] == sum(r['status'] == 'Available' for r in rs), key
        data_rows.append([title + r' \cite{' + source + '}', quantity, rs[0]['role'], str(len(rs)), span([r['T_K'] for r in rs], lambda v: num(v,2)), *basis(rs), *m])
        dev_rows.append([title + ', ' + quantity, rs[0]['role'], pair(s), num(s['AARD_percent'],2), num(s['bias_percent'],2), *extra(key), '/'.join(m)])
        cells = []
        for law in laws:
            for side in ('False', 'True'):
                q = stats[key].get(law, {}).get(side)
                cells += [pair(q), num(q['AARD_percent'],2)] if q else ['---', '---']
        if set(cells) != {'---'}: range_rows.append([title + ', ' + quantity, *cells])
    codes = '/'.join(laws.values())
    table(tag + '-data-current', f'Experimental data for the {label} system and their use in fitting.', ['Data set','Property','Role',r'$N$',r'$T$ / K','Composition',r'$\alpha$ / (mol/mol)',*laws.values()], data_rows, widths,
          notes=r'$N$: number of observations. Composition: ' + label + (r' content of the unloaded solution on the source basis' if tag == 'mdea' else r' content of the unloaded solution in wt\% as used in the calculation') + r', or amine mole fraction $x_{\mathrm{A}}$ for the binary sets. ' + codes + r': in, out or mixed relative to the measured temperature range of the equilibrium constant; ---: not given in the source rows, or the calculation uses no reaction (Section~\ref{sec:p2-data}). ' + note)
    table(tag + '-deviations-current', f'Deviations of the present model from the {label} data, by data set and role.', ['Data set','Role',r'$N/N_{\mathrm{rel}}$',r'AARD / \%',r'Bias / \%',*extra_head,codes], dev_rows, [.29 if extra_head else .42,.11,.08,.08,.08] + [.09]*len(extra_head) + [.11],
          notes=r'$N/N_{\mathrm{rel}}$: calculated observations / observations with a defined relative deviation. AARD and bias follow Eq.~\eqref{eq:p2-deviation}. ' + codes + ': in, out or mixed relative to the measured temperature range of the equilibrium constant; ---: the calculation uses no reaction.' + (r' Alternative: the stability-constrained alternative parameter set of Table~\ref{tab:p2-amp-fitted-current}.' if extra_head else ''))
    top = ' & ' + ' & '.join(r'\multicolumn{2}{@{}l}{' + code + ', ' + side + '}' for code in laws.values() for side in ['inside','outside']) + r' \\ '
    table(tag + '-ranges-current', f'Deviations of the present model from the {label} data inside and outside the measured temperature ranges of the equilibrium constants.', [top + 'Data set', *[r'$N/N_{\mathrm{rel}}$', r'AARD / \%']*2*len(laws)], range_rows, [round(.92-.16*2*len(laws),2)] + [.07,.09]*2*len(laws),
          notes=r'$N/N_{\mathrm{rel}}$: calculated observations / observations with a defined relative deviation; ---: no observations. Sets that use no reaction are omitted.')

def species(tag, label, document, heads, note):
    """Species parameters side by side, from the retained parameter file."""
    values = {c['component_id']: {q['family']: q['value']['magnitude'] for q in c['coefficients']} for c in document['parameters']['components']}
    kinds = [('Segment count','segment_count',4), (r'$\sigma$ / \AA','segment_diameter',4), (r'$\epsilon/k_B$ / K','dispersion_energy_over_k',3), (r'$d^{\mathrm{Born}}$ / \AA','born_diameter',4)]
    rows = [[name, *[num(values[c][family], digits) if family in values[c] else '---' for c in heads]] for name, family, digits in kinds]
    table(tag + '-species-current', f'ePC-SAFT parameters of the {label} species.', ['Parameter', *heads.values()], rows, [.30] + [.20]*len(heads), notes=note)

def bounds(low, high, digits, scale=1):
    return '[' + num(scale*low, digits) + ', ' + num(scale*high, digits) + ']'

mrows = read(MD + 'post-binary/data-rows.json')
for r in mrows: r['key'] = r['group']
mstats = collect(read(MD + 'same-row-deviations.json'), 'reaction', 'retreated_all_available', lambda e: e['group'])
amine('mdea', 'MDEA', MSETS, mrows, mstats, {'MDEA-dissociation': 'R5'}, mdea_basis, [.27,.11,.08,.04,.14,.13,.11,.05],
      r'Of the 20 heat calculations in the last 2 Merkley et al.\ sets, 13 were unavailable. The Xiao and Ermatchkov pressures informed the earlier choice of the MDEA parameter set used to initialize the present fit (Section~\ref{sec:p2-data}). \textsuperscript{a}Mole fraction of added \COtwo.')
MFIT = [(r'$k_{\mathrm{MDEA,w}}$ at 313.15 K',1,4), (r'$10^{3}\,\mathrm{d}k_{\mathrm{MDEA,w}}/\mathrm{d}T$ / K$^{-1}$',1e3,4), (r'$k_{\mathrm{MDEAH^+,CO_2}}$',1,4), (r'$k_{\mathrm{MDEAH^+,w}}$ at 313.15 K',1,4),
        (r'$b_{\mathrm{MDEAH^+,w}}$ / K',1,3), (r'$k_{\mathrm{MDEAH^+,HCO_3^-}}$',1,4), (r'$\sigma_{\mathrm{MDEAH^+}}$ / \AA',1,4), (r'$\epsilon_{\mathrm{MDEAH^+}}/k_B$ / K',1,3)]
mfit = read(MD + 'parameter-table.json')[:8]
assert all(r['role'] == 'fitted' and not r['on_bound'] for r in mfit)
table('mdea-fitted-current', 'Fitted MDEA parameters with conditional standard errors and bounds.', ['Parameter','Value','Standard error','Bounds'],
      [[name, num(s*r['value'],d), num(s*r['conditional_standard_error'],d), bounds(*r['bounds'],d,s)] for (name,s,d), r in zip(MFIT, mfit)], [.40,.15,.17,.24],
      notes=r'No parameter is on a bound. The values are those of the reported, interpolated parameter set (Section~\ref{sec:p2-results-parameters}); the standard errors are local values at that set.')
mdoc = read(MD + 'start-0/endpoint.json')
species('mdea', 'MDEA', mdoc, {'methyldiethanolamine': 'MDEA', 'protonated-methyldiethanolamine': r'MDEAH$^+$'},
        r'Neutral MDEA values are from Pahlavanzadeh and Fakouri Baygi \cite[Table~2]{Pahlavanzadeh2013}. MDEAH$^+$ keeps the neutral segment count; its segment diameter and dispersion energy are fitted (Table~\ref{tab:p2-mdea-fitted-current}), and its Born diameter equals its segment diameter.')

arows, afeed = read(AM + 'data-rows.json'), {r['identity']: r for r in read('analyses/amp_transfer/inputs/retransfer-344/observation-rows.csv')}
akey = lambda e: e['group'] + ('-y' if e['group'] == 'binary' and e['unit'] != 'Pa' else '')
for r in arows: r['key'] = akey(r)
adoc = read(AM + 'campaign/start-0/unpenalized/stage-0/parameters.json')
amass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in adoc['parameters']['components']}
def amp_basis(rs):
    feed = [afeed[r['identity']] for r in rs]
    if 'x_AMP' in rs[0]['row']: return r'$x_{\mathrm{A}}=\,$' + span([float(r['row']['x_AMP']) for r in rs], sig), '---'
    wt = [100*amass['aminomethylpropanol']/(amass['aminomethylpropanol'] + amass['water']*float(f['water'])) for f in feed]
    return span(wt, sig) + r' wt\%', span([float(f['alpha']) for f in feed], sig)
acomp = read(AM + 'campaign/start-0/retreat-comparison.json')
stable = {e['group']: e['retreat'] for e in acomp['pressure_deviations_by_range'] if e['range'] == 'R1'}
amine('amp', 'AMP', ASETS, arows, collect(read(AM + 'deviations.json'), 'range_name', 'statistics', akey), {'carbamate-hydrolysis': 'R4', 'AMP-dissociation': 'R5'}, amp_basis, [.21,.12,.08,.04,.14,.11,.12,.05,.05],
      r'The \COtwo-free Tong et al.\ observations are the unloaded solution of that work.', extra_head=[r'AARD, alternative / \%', r'Bias, alternative / \%'],
      extra=lambda key: [num(stable[key]['AARD_percent'],2), num(stable[key]['bias_percent'],2)] if key in stable else ['---', '---'])
AFIT = [(r'$k_{\mathrm{AMP,w}}$ at 313.15 K',4), (r'$b_{\mathrm{AMP,w}}$ / K',3), (r'$k_{\mathrm{AMPH^+,w}}$ at 313.15 K',4), (r'$b_{\mathrm{AMPH^+,w}}$ / K',3), (r'$k_{\mathrm{AMPH^+,CO_2}}$',4),
        (r'$\sigma_{\mathrm{AMPH^+}}$ / \AA',4), (r'$\sigma_{\mathrm{AMPCOO^-}}$ / \AA',4), (r'R4 constant term $a$',4), (r'R4 enthalpy increment $\delta h$ / (J/mol)',1)]
on = lambda point, d: num(point['value'], d) + (r'\textsuperscript{b}' if point['on_bound'] else '')
table('amp-fitted-current', 'Fitted AMP parameters with conditional standard errors and bounds, and the stability-constrained alternative.', ['Parameter','Value','Standard error','Bounds','Stability-constrained alternative'],
      [[name, on(r['unpenalized'],d), num(r['unpenalized']['conditional_standard_error'],d) if r['unpenalized']['conditional_standard_error'] else '---', bounds(r['lower'],r['upper'],d), on(r['retreat'],d)] for (name,d), r in zip(AFIT, acomp['parameters'])], [.33,.13,.13,.21,.15],
      notes=r'\textsuperscript{b}On a bound; no standard error is assigned. Stability-constrained alternative: the interpolated parameter set with no detected descent (Section~\ref{sec:p2-results-stability}); it has no standard errors. $\delta h$ is relative to the initial R4 correlation (Section~\ref{sec:p2-reactions}).')
apure, aedge = read(AM + 'pure-binary-on-05e94210.json')['pure']['groups'], adoc['parameters']['topology']['edges'][0]
assert {aedge[e]['component_id'] for e in ('endpoint_a', 'endpoint_b')} == {'aminomethylpropanol'} and apure['Ayad2023']['role'] == 'fitted'
ROLE = {'fitted': 'fitted', 'assessment_not_fitted': 'not fitted'}
species('amp', 'AMP', adoc, {'aminomethylpropanol': 'AMP', 'protonated-aminomethylpropanol': r'AMPH$^+$', 'carbamate-anion': r'AMPCOO$^-$'},
        r'Neutral AMP values are the pure-component fit described in Section~\ref{sec:p2-species} and are fixed during reactive estimation; its other 2 fitted values are $\epsilon^{AB}/k_B=\,$' + num(aedge['energy_over_k']['value']['magnitude'], 3) + r' K and $\kappa^{AB}=\,$' + num(aedge['volume']['value']['magnitude'], 7) + '. At these fixed values the vapor-pressure AARD (bias) is ' + ', '.join(num(g['AARD_percent'], 2) + r'\,\% (' + num(g['signed_relative_bias_percent'], 2) + r'\,\%) for the ' + str(g['n']) + ' observations of ' + who + ' (' + ROLE[g['role']] + ')' for who, g in zip([r"Klep\'a\v{c}ov\'a et al.\ \cite{klepacovaVaporPressuresSeveral2011}", r'Belabbaci et al.\ \cite{belabbaciInvestigationIsothermalVapour2010}', r'Pappa et al.\ \cite{pappaMeasurementThermodynamicModeling2006}'], [apure[k] for k in ('Klepacova2011', 'Belabbaci2010', 'Pappa2006')])) + r', and the errors of the 3 fitted liquid densities of Ayad et al.\ \cite{ayadMeasurementsModelingThermodynamic2023} are ' + ', '.join(num(e, 3) for e in apure['Ayad2023']['errors_kg_m3']) + r' kg/m$^3$; these are comparisons at fixed parameters, not an independent validation. AMPH$^+$ and AMPCOO$^-$ are single spheres; their segment diameters are fitted (Table~\ref{tab:p2-amp-fitted-current}) and their Born diameters equal their segment diameters.')
def pressures(name, amine_name, shape, panels, curves, points, sep, laws, fitted, mass):
    """Pressure against loading: retained measurements as points, retained model curves as lines."""
    lines = {}
    for r in curves: lines.setdefault(r['curve'], []).append(r)
    assert {q['curve'] for q in points} <= set(lines), 'every plotted measurement belongs to a retained curve'
    fig, axes = plt.subplots(*shape, figsize=(6.48, 3.3*shape[0]), constrained_layout=True)
    for ax, letter, choose in zip(axes.flat, 'abcdef', panels):
        chosen = [key for key in lines if choose(*key.split(sep))]
        ax.set_yscale('log')
        stocks = {key.split(sep)[2] for key in chosen}
        for index, key in enumerate(chosen):
            line, (group, T, water) = sorted(lines[key], key=lambda r: r['loading']), key.split(sep)
            outside = [line[0]['outside_ranges'][law] is True for law in laws]
            style, marker = ('-.', 'D') if len(laws) > 1 and all(outside) else ('--', '^') if outside[0] else (':', 's') if any(outside) else ('-', 'o')
            label = f'{float(T):.2f} K' + (f', {100*mass[0]/(mass[0] + mass[1]*float(water)):.3g} wt%' if len(stocks) > 1 else '')
            ax.plot([r['loading'] for r in line], [r['value']/1000 for r in line], style, color=colors[index % len(colors)], label=label)
            obs = [q for q in points if q['curve'] == key]
            ax.scatter([q['loading'] for q in obs], [q['pressure_Pa']/1000 for q in obs], marker=marker, s=22, edgecolors=colors[index % len(colors)], facecolors=colors[index % len(colors)] if group in fitted else 'none')
        ax.set(xlabel=f'Loading (mol CO$_2$/mol {amine_name})', ylabel='Pressure (kPa)')
        ax.set_title(f'({letter})', loc='left')
        ax.yaxis.set_minor_formatter(matplotlib.ticker.LogFormatterSciNotation(labelOnlyBase=False, minor_thresholds=(1.3, 0.4)))
        ax.legend(ncol=1 if len(stocks) > 1 and shape[1] > 2 else 2, columnspacing=.7, handlelength=1.8, handletextpad=.4, loc='upper center', bbox_to_anchor=(.5, -.2), frameon=False)
    figure(fig, name)

mmass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mdoc['parameters']['components']}
pressures('mdea-current-measured-model.pdf', 'MDEA', (2, 3), [lambda g, T, w: g.startswith('Kuranov') and float(w) > 20, lambda g, T, w: g.startswith('Kuranov') and float(w) < 20, lambda g, T, w: g == 'Xiao',
          lambda g, T, w: g == 'Ermatchkov' and float(w) > 20, lambda g, T, w: g == 'Ermatchkov' and 10 < float(w) < 20, lambda g, T, w: g == 'Ermatchkov' and float(w) < 10],
          read(MD + 'curves/curve-data.json'), read(MD + 'curves/data-points.json'), ':', ['MDEA-dissociation'], {'Kuranov'}, (mmass['methyldiethanolamine'], mmass['water']))
apoints = [dict(curve=f"{f['dataset']}|{float(f['T'])}|{float(f['water'])}", loading=float(f['alpha']), pressure_Pa=r['observed']) for r in arows for f in [afeed[r['identity']]] if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'kundu', 'tong')]
pressures('amp-current-measured-model.pdf', 'AMP', (2, 2), [lambda g, T, w: g.startswith('hartono'), lambda g, T, w: g.startswith('tong'), lambda g, T, w: g.startswith('kundu') and float(w) > 12, lambda g, T, w: g.startswith('kundu') and float(w) < 12],
          read(AM + 'curve-data.json'), apoints, '|', ['AMP-dissociation', 'carbamate-hydrolysis'], {'hartono-2021-calibration'}, (amass['aminomethylpropanol'], amass['water']))
# One summary row per amine, from each amine's retained summary.
dsum, msum, asum = read(BASE + 'paper-summary.json'), read(MD + 'summary-row.json'), read(AM + 'summary-row.json')
msearch, asearch = read(MD + 'post-binary-stability.json')['grid'], read(AM + 'campaign/selected-supplied-check.json')['search']['grid']
cell = lambda s: num(s['AARD_percent'],2) + ' (' + str(s['rows']) + ')'
rows = [['DEA', dsum['fitted_parameters'], len(dsum['active_bounds']), cell(dsum['pressure']['fitted']), cell(dsum['pressure']['not fitted']), dsum['stability']['grid']['states'], len(dsum['stability']['grid']['unavailable']), sum(dsum['stability']['grid']['liquid_liquid_splits'].values())],
        ['MDEA', msum['free_fitted_parameters'], msum['on_bounds'], cell(msum['fitted_pressure']['statistics']), cell(msum['not_fitted_pressure']['statistics']), msearch['states'], msum['unavailable_searches'], msum['liquid_liquid_split_state_lower_bound']],
        ['AMP', asum['fitted_parameters'], asum['active_bounds'], cell(asum['fitted_pressure']), cell(asum['not fitted_pressure']), asearch['states'], asum['unavailable_stability_entries'], asum['liquid_liquid_lower_bound']]]
table('summary-current', 'Summary of the transfer by amine.', ['Amine','Fitted parameters','On bounds',r'Fitted pressures: AARD / \% ($N$)',r'Pressures not fitted: AARD / \% ($N$)','Search requests','Searches unavailable','Liquid--liquid splits found'], rows, [.08,.10,.08,.15,.16,.10,.12,.13],
      notes=r'Pressures pool the total, partial and \COtwo-free bubble pressures of each amine (Tables~\ref{tab:p2-dea-deviations-current}, \ref{tab:p2-mdea-deviations-current} and \ref{tab:p2-amp-deviations-current}). Each pooled pressure column includes reactive observations both inside and outside the applicable temperature ranges; \COtwo-free pressures use no reaction constant. Split counts are lower bounds from finite searches; an unavailable search is not counted as stable. The MDEA and AMP rows are the reported parameter sets; the AMP stability-constrained alternative has no detected split.')
read('analyses/dea_transfer/results/binary.json')
read(BASE + 'conditional-uncertainty.json')
read(BASE + 'checks.json')
read('analyses/dea_transfer/inputs/part-ii-346/route-current.json')
mean = lambda values: sum(values)/len(values)
jak = {k: 100*mean([abs(r['value']/r['observed'] - 1) for r in mrows if r['group'] == 'Jakobsen' and r['row']['ratio'] == k]) for k in ('cation', 'carbonate')}
bias = [mstats[g]['R1']['False']['bias_percent'] for g in ('Bottinger-bicarbonate-5bar', 'Bottinger-bicarbonate-25bar')]
loaded = [float(r['AARD_percent']) for r in read(BASE + 'group-deviations.csv') if r['model'] == '05e94210' and r['role'] == 'not fitted'] + [mstats[g]['R1']['False']['AARD_percent'] for g in ('Ermatchkov', 'corrected-Kamps', 'Kuranov-413K', 'Sedighi', 'Xiao')] + [e['unpenalized']['AARD_percent'] for e in acomp['pressure_deviations_by_range'] if e['range'] == 'R1' and e['role'] == 'not fitted']
heats = [mstats[g]['R1']['False']['AARD_percent'] for g in ('Carson', 'Merkley')]
viii = next(r for r in data if r['identity'] + ':problem' == dsum['stability']['grid']['unavailable'][0])
pub = {c['group']: c for c in read(MD + 'published-pressure-comparisons.json')['comparisons']}['Ermatchkov']
gap = [abs(s['mean_absolute_relative_deviation_percent'] - pub['selected_point_mean_absolute_relative_deviation_percent']) for s in pub['published_parameter_sets']]
alt = {(e['range'], e['group'], e['outside_range']): f"{e['retreat']['AARD_percent']:.2f}" for e in acomp['pressure_deviations_by_range']}
H, C, L, T_ = 'carbamate-hydrolysis', 'AMP-dissociation', 'loaded-pressure', 'hartono-2021-supplemental'
stated = {'part2.tex': [f'{min(loaded):.2f}--{max(loaded):.2f}', f'{min(heats):.2f}--{max(heats):.2f}'], 'sections/part2/conclusions.tex': [f'{min(loaded):.2f}--{max(loaded):.2f}'], 'submission/part2_highlights.txt': [f'{min(loaded):.2f}-{max(loaded):.2f}'],
          'sections/part2/results.tex': [f"{jak['cation']:.2f}", f"{jak['carbonate']:.2f}", f'$+{bias[0]:.2f}$ and $+{bias[1]:.2f}$', f"loading of {float(viii['row']['alpha_mol_CO2_per_mol_DEA']):.3f} did not complete", f"{read(MD + 'verification.json')['raw_search_files']} distinct calculations", f'{gap[0]:.2f} percentage points below', f'{gap[1]:.2f} points above', f"{max(float(f['T']) for f in afeed.values() if f['dataset'] == 'hartono-2021-calibration'):.0f}~K"],
          'sections/part2/supplement.tex': [f'{alt[H,L,False]} and {alt[H,L,True]}', f'{alt[H,T_,False]} and {alt[H,T_,True]}', f"{alt[H,'kundu',False]} and {alt[H,'kundu',True]}", f"{alt[H,'tong',False]} and {alt[H,'tong',True]}", f"({alt[C,L,False]} and {alt[C,'kundu',False]}", f'({alt[C,T_,True]}', f"loading {float(viii['row']['alpha_mol_CO2_per_mol_DEA']):.3f} mol/mol"]}
for path, values in stated.items():
    for value in values: assert value in (LATEX / path).read_text(), (path, value)
emit('tables/part2/number-sources.json',json.dumps(sources,indent=2)+'\n')
if '--check' in sys.argv:
    for path, value in outputs.items():
        assert path.read_bytes()==(value if isinstance(value,bytes) else value.encode()), path
    print(f'Numeric and retained-figure check passed: {len(outputs)} displays; {len(sources)} source files.')
else:
    for path,value in outputs.items():
        path.write_bytes(value if isinstance(value,bytes) else value.encode())
