"""Present retained DEA results, with a byte-for-byte display check; no model calls."""
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
BASE = 'analyses/dea_transfer/results/retransfer-346/f2-report-1/'
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
data = read(BASE + 'data-rows.json')
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
      notes="$N$: number of points. Composition: DEA content of the unloaded solution, or water mole fraction $x_{\\mathrm{w}}$ for the binary sets. R4 and R5: " + RANGE_NOTE + " (Section~\\ref{sec:p2-data}). All data for loaded solutions lie inside the correlation range of R1--R3, whose measured coverage is unverified. The water--DEA interaction was fitted beforehand to the 365.15 K vapor--liquid equilibria of Horstmann et al.\\ \\cite{horstmannPhaseEquilibriumExcess2002}, which are not listed. \\textsuperscript{a}Mole fraction of added \\COtwo.")
rows = []
for r in groups:
    if r['model'] != 'F2': continue
    old = next(x for x in groups if x['model']=='F0' and x['group']==r['group'])
    m = marks(r['group'])
    rows.append([name(r['group']),r['role'],r['rows']+'/'+r['relative_rows'],num(r['AARD_percent'],2),num(r['bias_percent'],2),num(old['AARD_percent'],2),'---' if m == ['---','---'] else '/'.join(m)])
table('dea-deviations-current', 'Deviations of the present model from the DEA data, by data set and role.', ['Data set','Role',r'$N/N_{\mathrm{rel}}$',r'AARD / \%',r'Bias / \%',r'AARD, less restricted calibration / \%','R4/R5'],rows,[.27,.14,.08,.09,.09,.15,.11],
      notes="$N/N_{\\mathrm{rel}}$: all points / points with a defined relative deviation. AARD and bias follow Eq.~\\eqref{eq:p2-deviation}; bias is calculated minus measured, divided by measured. Less restricted calibration: the Part I calibration described in Section~\\ref{sec:p2-shared}, on which DEA is refitted as a sensitivity comparison. R4/R5: " + RANGE_NOTE + '.')
ranges = read(BASE + 'range-deviations.csv')
rows = []
for group in dict.fromkeys(r['group'] for r in data):
    cells = []
    for law in LAWS:
        for outside in ['False','True']:
            hit = [r for r in ranges if r['model']=='F2' and r['group']==group and r['law']==law and r['outside_range']==outside]
            cells += [hit[0]['rows']+'/'+hit[0]['relative_rows'], num(hit[0]['AARD_percent'],2)] if hit else ['---','---']
    if set(cells) != {'---'}: rows.append([name(group),*cells])
    else: assert group in ['Cai','Horstmann'], 'Only the binary comparisons use no reaction correlation'
top = ' & ' + ' & '.join(r'\multicolumn{2}{@{}l}{' + law + ', ' + side + '}' for law in LAWS.values() for side in ['inside','outside']) + r' \\ '
table('dea-ranges-current','Deviations of the present model inside and outside the measured temperature ranges of the carbamate hydrolysis constant (R4) and the DEA dissociation constant (R5).', [top + 'Data set',*[r'$N/N_{\mathrm{rel}}$',r'AARD / \%']*4],rows,[.26,.075,.085,.075,.085,.075,.085,.075,.085],
      notes='$N/N_{\\mathrm{rel}}$: all points / points with a defined relative deviation; ---: no points. The binary sets use no reaction and are omitted. All data for loaded solutions lie inside the correlation range of R1--R3, whose measured coverage is unverified.')
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
for ax, groups, title in zip(axes.flat,[('Lawson','Lawson-394K'),('SeoHong',),('Lal',),('Carson',)],['Lawson: fitted; 394.26 K not fitted','Seo and Hong: not fitted','Lal: not fitted','Carson: fitted']):
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
        ax.scatter([loading(r['row']) for r in obs],[r['observed']/1000 for r in obs],marker='^' if outside else 's' if hydrolysis else 'o',facecolors='none',edgecolors=color,s=25)
    ax.set(title=title,xlabel='Loading (mol CO$_2$/mol DEA)',ylabel='Integral heat (kJ/mol CO$_2$)' if groups==('Carson',) else 'CO$_2$ partial pressure (kPa)',yscale='linear' if groups==('Carson',) else 'log')
    ax.legend(ncol=2, columnspacing=.7, handlelength=1.8, handletextpad=.4)
fig.suptitle('DEA: measurements and model curves',fontsize=9)
figure(fig,'dea-current-measured-model.pdf')
fig,axes=plt.subplots(1,2,figsize=(6.48,3.0),constrained_layout=True)
for ax,group,scale in [(axes[0],'Horstmann',1),(axes[1],'Cai',0.001)]:
    ps=[r for r in data if r['group']==group]
    ax.scatter([float(r['row']['x_water']) for r in ps],[r['observed']*scale for r in ps],facecolors='none',edgecolors=colors[0],label='Measured')
    ax.scatter([float(r['row']['x_water']) for r in ps],[r['value']*scale for r in ps],marker='x',color=colors[1],label='Present model')
    ax.set(title=f'{group}: comparison only;\nreactions not used',xlabel='Water mole fraction',ylabel='Excess enthalpy (J/mol mixture)' if group=='Horstmann' else 'Bubble pressure (kPa)')
    ax.legend(fontsize=8, loc='center' if group=='Horstmann' else 'upper right')
figure(fig,'dea-current-binary-comparisons.pdf')
read('analyses/dea_transfer/results/research-380/summary.json')
read(BASE + 'reporting-checks.json')
read('analyses/dea_transfer/results/binary.json')
read('analyses/dea_transfer/results/retransfer-346/f2-current/conditional-uncertainty.json')
read('analyses/dea_transfer/inputs/part-ii-346/route-current.json')
emit('tables/part2/dea-number-sources.json',json.dumps(sources,indent=2)+'\n')
if '--check' in sys.argv:
    for path, value in outputs.items():
        assert path.read_bytes()==(value if isinstance(value,bytes) else value.encode()), path
    print(f'Numeric and retained-figure check passed: {len(outputs)} displays; {len(sources)} source files.')
else:
    for path,value in outputs.items():
        path.write_bytes(value if isinstance(value,bytes) else value.encode())
