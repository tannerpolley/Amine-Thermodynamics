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

def esc(text):
    text = str(text).replace('Lawson-394K','Lawson, higher temperature').replace('Lawson-VIII','Lawson, Table VIII').replace('SeoHong','Seo and Hong').replace('Bottinger-DEA_plus_DEAH',r'B\"ottinger, DEA + cation').replace('Bottinger-DEACOO',r'B\"ottinger, carbamate').replace('Bottinger-HCO3',r'B\"ottinger, bicarbonate')
    return str(text).replace('&', r'\&').replace('_', r'\_').replace('%', r'\%').replace('^', r'\textasciicircum{}')

def num(value, digits=3):
    return f'${float(value):.{digits}f}$'

def table(name, caption, headers, rows, widths, long=False):
    columns = ''.join(r'>{\raggedright\arraybackslash}p{' + str(w) + r'\linewidth}' for w in widths)
    head = ' & '.join(headers) + r' \\ \midrule' + '\n'
    body = '\n'.join(' & '.join(map(str, row)) + r' \\' for row in rows)
    if long:
        text = r'\begingroup\small\setlength{\tabcolsep}{2pt}\begin{longtable}{@{}' + columns + '@{}}\n'
        text += r'\caption{' + caption + r'}\label{tab:p2-' + name + r'}\\' + '\n'
        text += r'\toprule ' + head + r'\endfirsthead\toprule ' + head + r'\endhead\bottomrule\endfoot' + '\n'
        text += body + '\n' + r'\end{longtable}\endgroup' + '\n'
    else:
        text = r'\begin{table}[htbp]\small\setlength{\tabcolsep}{2pt}\caption{' + caption + r'}\label{tab:p2-' + name + '}\n'
        text += r'\begin{tabular}{@{}' + columns + '@{}}\n' + r'\toprule ' + head
        text += body + '\n' + r'\bottomrule\end{tabular}\end{table}' + '\n'
    emit('tables/part2/' + name + '.tex', text)

params = read(BASE + 'parameter-values.csv')
p = {r['parameter']: r for r in params}
fitted_names = [r'$k_{\mathrm{DEAH^+,w}}$', r'$k_{\mathrm{DEACOO^-,w}}$', r'Hydrolysis $a$', r'Hydrolysis $\delta h$ / (J/mol)']
rows = [[name, num(r['value']), num(r['conditional_SE']), '['+num(r['lower'])+', '+num(r['upper'])+']'] for name, r in zip(fitted_names, params[:4])]
table('dea-fitted-current', 'DEA fitted parameters with conditional standard errors and bounds. None is on a bound. The hydrolysis level and enthalpy increment refer to the completed correlation (Section~\\ref{sec:p2-model}).', ['Quantity','Value','Standard error','Bounds'], rows, [.28,.15,.17,.32])
rows = []
for label, key, digits in [('Segment count','segment_count',4), (r'$\sigma$ / \AA','segment_diameter',4), (r'$\epsilon/k_B$ / K','dispersion_energy_over_k',3), (r'$d^{\mathrm{Born}}$ / \AA','born_diameter',4)]:
    vals = [num(p[s+'/'+key]['value'],digits) if s+'/'+key in p else '---' for s in ['diethanolamine','protonated-diethanolamine','carbamate-anion']]
    rows.append([label,*vals])
table('dea-fixed-current', 'Fixed DEA species quantities. Neutral DEA values are from Nasrifar and Tafazzol \\cite[Table~2]{Nasrifar2010}; the cation keeps the neutral chain values, and the carbamate is a single sphere (Section~\\ref{sec:p2-model}). Born diameters equal segment diameters. Fixed quantities have no standard error or bounds.', ['Quantity','DEA',r'DEAH$^+$',r'DEACOO$^-$'],rows,[.30,.20,.20,.20])
data = read(BASE + 'data-rows.json')
groups = read(BASE + 'group-deviations.csv')
rows = []
for r in groups:
    if r['model'] != 'F2': continue
    old = next(x for x in groups if x['model']=='F0' and x['group']==r['group'])
    marks = []
    for law in ['DEA-dissociation','carbamate-hydrolysis']:
        flags = {x['outside_ranges'][law] for x in data if x['group']==r['group']}
        marks.append('mixed' if len(flags)>1 else ('out' if True in flags else 'in' if False in flags else 'not used'))
    rows.append([esc(r['group']),r['role'],r['rows']+'/'+r['relative_rows'],num(r['AARD_percent'],2),num(r['bias_percent'],2),num(old['AARD_percent'],2),'/'.join(marks)])
table('dea-deviations-current', 'DEA deviations by data source and role. Counts are all observations / observations with defined relative error. Bias is calculated minus measured, divided by measured. The Earlier-set column reports DEA refitted on Part I\'s earlier shared parameter set; it is a sensitivity comparison. D/H marks dissociation and hydrolysis source intervals separately.', ['Source / quantity','Role',r'$n/n_{rel}$',r'AARD / \%',r'Bias / \%',r'Earlier-set AARD / \%','D/H'],rows,[.24,.12,.08,.10,.10,.11,.15])
ranges = read(BASE + 'range-deviations.csv')
rows = [[esc(r['group']), 'D' if r['law']=='DEA-dissociation' else 'H', 'outside' if r['outside_range']=='True' else 'inside',r['rows'],r['relative_rows'],num(r['AARD_percent'],2)] for r in ranges if r['model']=='F2' and r['law'] in ['DEA-dissociation','carbamate-hydrolysis'] and r['outside_range'] in ['False','True']]
assert not any(row[0] in ['Cai','Horstmann'] for row in rows), 'Binary comparisons use no reaction correlation'
table('dea-ranges-current','DEA deviations separated by dissociation measurement interval (D) and hydrolysis source measurement interval (H). Binary comparisons do not use reactions and are omitted here.', ['Source / quantity','Interval','Position',r'$n$',r'$n_{rel}$',r'AARD / \%'],rows,[.33,.12,.14,.08,.08,.14],long=True)
def quantity(key):
    if key == 'hydrolysis-a': return fitted_names[2]
    if key == 'hydrolysis-enthalpy-shift': return fitted_names[3]
    if key == 'protonated-diethanolamine/charged_molecule_ion':
        return 'DEA cation, charged-chain self-dispersion retained (1 = yes)'
    parts = key.split('/')
    if parts[0] == 'association':
        species = 'DEA cation' if parts[1] == 'protonated-diethanolamine' else 'DEA'
        if parts[-1] == 'multiplicity': return f'{species}, number of type-{parts[2]} sites'
        return f'{species} site {parts[2]}--site {parts[4]} ' + {'energy_over_k': 'association energy / Boltzmann constant', 'volume': 'association volume'}[parts[-1]]
    if parts[0] in ['DEA-dissociation', 'carbamate-hydrolysis']:
        return ('DEA dissociation' if parts[0] == 'DEA-dissociation' else 'Carbamate hydrolysis') + ', $' + parts[-1] + '$'
    if key in ['k-DEAH-water','k-DEACOO-water']: return fitted_names[['k-DEAH-water','k-DEACOO-water'].index(key)]
    replacements = {'protonated-diethanolamine': 'DEA cation', 'diethanolamine': 'DEA', 'carbamate-anion': 'DEA carbamate', 'bicarbonate-anion': 'bicarbonate', 'carbonate-anion': 'carbonate', 'hydronium-cation': 'hydronium', 'hydroxide-anion': 'hydroxide', 'carbon-dioxide': 'carbon dioxide', 'dispersion_energy_over_k': 'dispersion energy / Boltzmann constant', 'k_ij_reciprocal_temperature_slope': 'reciprocal-temperature interaction slope', 'k_ij': 'dispersion interaction', 'charged_molecule_ion': 'charged-chain indicator', 'energy_over_k': 'association energy / Boltzmann constant', 'DEA-dissociation': 'DEA dissociation', 'hydrolysis-enthalpy-shift': 'hydrolysis enthalpy increment', 'born': 'Born', 'debye_huckel': r'Debye--H\"uckel'}
    for old, new in replacements.items(): key = key.replace(old,new)
    return esc(key.replace('_',' ').replace('/',' / '))
units = {'K^2': r'K$^2$', '1/K^2': r'K$^{-2}$', 'kelvin': 'K', 'angstrom': r'\AA', 'liter / mole': 'L/mol', 'kilogram / mole': 'kg/mol', 'dimensionless': '1', 'elementary-charge': '$e$'}
rows = [[quantity(r['parameter']),'$' + repr(float(r['value'])).removesuffix('.0') + '$',units.get(r['unit'],r['unit']),r['fitted_or_fixed']] for r in params]
table('dea-all-current','Complete DEA parameter values. Fitted-coordinate errors and bounds are in the main text; reaction coefficients are completed coefficients, not additional independent fitted quantities. The electronic parameter table retains each value\'s source and basis.', ['Quantity','Value','Unit','Role'],rows,[.42,.30,.14,.09],long=True)
data = read(BASE + 'data-rows.json')
rows = []
for group in dict.fromkeys(r['group'] for r in data):
    rs = [r for r in data if r['group']==group]
    t = [r['T_K'] for r in rs]
    d = ['out' if r['outside_ranges']['DEA-dissociation'] is True else 'in' for r in rs]
    h = ['out' if r['outside_ranges']['carbamate-hydrolysis'] is True else 'in' for r in rs]
    mark = lambda v: 'mixed' if len(set(v))>1 else v[0]
    if all(r['outside_ranges']['R1']=='reaction not used' for r in rs): d=h=['not used']
    rows.append([esc(group),rs[0]['role'],str(len(rs)),num(min(t),2) if min(t)==max(t) else num(min(t),2)+'--'+num(max(t),2),mark(d),mark(h)])
table('dea-data-current', "DEA data roles and temperature ranges. D and H give each set's position relative to the DEA dissociation and hydrolysis source intervals (Section~\\ref{sec:p2-methods}): in, out or mixed; binary sets use no reactions. All reactive observations lie inside the R1--R3 source-correlation interval, whose measured coverage is unverified. The DEA--water interaction was fitted beforehand to Horstmann's 365.15 K vapor--liquid equilibria, which are not listed.", ['Source / quantity','Role',r'$n$',r'$T$ / K','D','H'],rows,[.29,.15,.06,.22,.10,.10])
rows = []
for group in dict.fromkeys(r['group'] for r in data):
    rs = [r for r in data if r['group']==group]
    fields = {}
    for r in rs:
        for key, v in r['row'].items():
            if key == 'x_CO2' and group != 'Carson': continue
            if any(t in key.lower() for t in ['fraction','alpha','loading','molality','mass_percent','kmol_per_m3','x_water','x_co2']):
                try: fields.setdefault(key, []).append(float(v))
                except (ValueError, TypeError): pass
    compositions = []
    labels = {'DEA_mass_percent': r'DEA / wt\%', 'DEA_mass_fraction': r'DEA / wt\%', 'DEA_kmol_per_m3': 'DEA / (kmol per cubic metre)', 'alpha_mol_CO2_per_mol_DEA': 'loading / (mol per mol DEA)', 'alpha_mol_CO2_per_mol_amine': 'loading / (mol per mol amine)', 'x_water': 'water mole fraction', 'x_CO2': 'added carbon dioxide mole fraction'}
    for key, values in fields.items():
        if key == 'AMP_mass_percent': continue
        if key == 'DEA_mass_fraction': values = [100*v for v in values]
        fmt = (lambda v: f'${v:g}$') if key in ['DEA_mass_percent','DEA_mass_fraction'] else (lambda v:num(v,4))
        bounds = fmt(min(values)) if min(values)==max(values) else fmt(min(values))+'--'+fmt(max(values))
        compositions.append(labels[key]+': '+bounds)
    basis = '; '.join(compositions)
    rows.append([esc(group),basis or 'See source observation record'])
table('dea-inventory-current','DEA source composition and loading ranges. Column names preserve each source transformation; mass fractions are dimensionless and loadings are mol/mol.', ['Source / quantity','Retained composition and loading basis'],rows,[.28,.66],long=True)
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
