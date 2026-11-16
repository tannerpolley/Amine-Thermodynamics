"""Present retained DEA results, with a byte-for-byte display check; no model calls."""
import csv
import hashlib
import json
import sys
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
    text = str(text).replace('Lawson-394K','Lawson, higher temperature').replace('Lawson-VIII','Lawson, Table VIII').replace('SeoHong','Seo and Hong').replace('Bottinger-DEA_plus_DEAH','Bott., DEA + cation').replace('Bottinger-DEACOO','Bott., carbamate').replace('Bottinger-HCO3','Bott., bicarbonate')
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
table('dea-fitted-current', 'DEA fitted parameters. All are interior; standard errors are conditional. Bounds and the enthalpy increment refer to the completed-correlation coordinates. The increment is zero because its fitted change is already included in the completed coefficients.', ['Quantity','Value','Standard error','Bounds'], rows, [.28,.15,.17,.32])
rows = []
for label, key, digits in [('Segment count','segment_count',4), (r'$\sigma$ / \AA','segment_diameter',4), (r'$\epsilon/k_B$ / K','dispersion_energy_over_k',3), (r'$d^{\mathrm{Born}}$ / \AA','born_diameter',4)]:
    vals = [num(p[s+'/'+key]['value'],digits) if s+'/'+key in p else '---' for s in ['diethanolamine','protonated-diethanolamine','carbamate-anion']]
    rows.append([label,*vals])
table('dea-fixed-current', 'Fixed DEA species quantities. Neutral inputs follow Nasrifar and Tafazzol (Table 2); cation chain quantities inherit neutral DEA; carbamate quantities are inherited model assumptions. Both ionic Born diameters equal their segment diameters. Fixed quantities have no estimated standard error or fitted bounds.', ['Quantity','DEA',r'DEAH$^+$',r'DEACOO$^-$'],rows,[.30,.20,.20,.20])
data = read(BASE + 'data-rows.json')
groups = read(BASE + 'group-deviations.csv')
rows = []
for r in groups:
    if r['model'] != 'F2': continue
    old = next(x for x in groups if x['model']=='F0' and x['group']==r['group'])
    marks = []
    for law in ['DEA-dissociation','carbamate-hydrolysis']:
        flags = {x['outside_ranges'][law] for x in data if x['group']==r['group']}
        marks.append('mixed' if len(flags)>1 else ('out' if True in flags else 'in' if False in flags else 'unused'))
    rows.append([esc(r['group']).replace('Bottinger','Bott.'),r['role'],r['rows']+'/'+r['relative_rows'],num(r['AARD_percent'],2),num(r['bias_percent'],2),num(old['AARD_percent'],2),'/'.join(marks)])
table('dea-deviations-current', 'DEA deviations by data source and role. Counts are all observations / observations with defined relative error. Bias is calculated minus measured, divided by measured. Earlier shared inputs are a sensitivity comparison; every result remains provisional. D/H marks dissociation and hydrolysis source intervals separately.', ['Source / quantity','Role',r'$n/n_{rel}$',r'AARD / \%',r'Bias / \%',r'Earlier AARD / \%','D/H'],rows,[.24,.12,.08,.10,.10,.11,.15])
ranges = read(BASE + 'range-deviations.csv')
rows = [[esc(r['group']).replace('Bottinger','Bott.'), 'D' if r['law']=='DEA-dissociation' else 'H', 'outside' if r['outside_range']=='True' else 'inside',r['rows'],r['relative_rows'],num(r['AARD_percent'],2)] for r in ranges if r['model']=='F2' and r['law'] in ['DEA-dissociation','carbamate-hydrolysis'] and r['outside_range'] in ['False','True']]
assert not any(row[0] in ['Cai','Horstmann'] for row in rows), 'Binary comparisons use no reaction correlation'
table('dea-ranges-current','DEA deviations separated by dissociation measurement interval (D) and hydrolysis source measurement interval (H). Binary comparisons do not use reactions and are omitted here. The H interval does not establish validity of the fitted correlation.', ['Source / quantity','Interval','Position',r'$n$',r'$n_{rel}$',r'AARD / \%'],rows,[.33,.12,.14,.08,.08,.14],long=True)
def quantity(key):
    replacements = {'protonated-diethanolamine': 'DEA cation', 'diethanolamine': 'DEA', 'carbamate-anion': 'DEA carbamate', 'bicarbonate-anion': 'bicarbonate', 'carbonate-anion': 'carbonate', 'hydronium-cation': 'hydronium', 'hydroxide-anion': 'hydroxide', 'carbon-dioxide': 'carbon dioxide', 'dispersion_energy_over_k': 'dispersion energy / Boltzmann constant', 'k_ij_reciprocal_temperature_slope': 'reciprocal-temperature interaction slope', 'k_ij': 'dispersion interaction', 'charged_molecule_ion': 'charged-chain indicator', 'energy_over_k': 'association energy / Boltzmann constant', 'DEA-dissociation': 'DEA dissociation', 'hydrolysis-enthalpy-shift': 'hydrolysis enthalpy increment'}
    for old, new in replacements.items(): key = key.replace(old,new)
    return esc(key.replace('_',' ').replace('/',' / '))
rows = [[quantity(r['parameter']),num(r['value'],8),esc(r['unit']),r['fitted_or_fixed']] for r in params]
table('dea-all-current','Complete DEA parameter values. Fitted-coordinate errors and bounds are in the main text; reaction coefficients are completed coefficients, not additional independent fitted quantities. The electronic parameter table retains each value\'s source and basis.', ['Quantity','Value','Unit','Role'],rows,[.46,.21,.19,.09],long=True)
data = read(BASE + 'data-rows.json')
rows = []
for group in dict.fromkeys(r['group'] for r in data):
    rs = [r for r in data if r['group']==group]
    t = [r['T_K'] for r in rs]
    d = ['out' if r['outside_ranges']['DEA-dissociation'] is True else 'in' for r in rs]
    h = ['out' if r['outside_ranges']['carbamate-hydrolysis'] is True else 'in' for r in rs]
    mark = lambda v: 'mixed' if len(set(v))>1 else v[0]
    if all(r['outside_ranges']['R1']=='reaction not used' for r in rs): d=h=['not used']
    rows.append([esc(group).replace('Bottinger','Bott.'),rs[0]['role'],str(len(rs)),num(min(t),2)+'--'+num(max(t),2),mark(d),mark(h)])
table('dea-data-current','DEA data roles and temperatures. D and H mark the intervals defined in the text. All reactive observations are inside the R1--R3 source-correlation range; its measured coverage is unverified. All observations were previously seen; pressure comparisons were accessed before the choice between numerically tied fits. Comparison only quantities did not choose the fit.', ['Source / quantity','Role',r'$n$',r'$T$ / K','D','H'],rows,[.29,.15,.06,.22,.10,.10])
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
    basis = '; '.join(esc({'DEA_mass_percent':'DEA / wt%','AMP_mass_percent':'AMP / wt%','DEA_mass_fraction':'DEA mass fraction','DEA_kmol_per_m3':'DEA / (kmol per cubic metre)','alpha_mol_CO2_per_mol_DEA':'loading / (mol per mol DEA)','alpha_mol_CO2_per_mol_amine':'loading / (mol per mol amine)','x_water':'water mole fraction','x_CO2':'added carbon dioxide mole fraction'}.get(k,k))+': '+num(min(v),4)+'--'+num(max(v),4) for k,v in fields.items())
    rows.append([esc(group).replace('Bottinger','Bott.'),basis or 'See source observation record'])
table('dea-inventory-current','DEA source composition and loading ranges. Column names preserve each source transformation; mass fractions are dimensionless and loadings are mol/mol.', ['Source / quantity','Retained composition and loading basis'],rows,[.28,.66],long=True)
# Reuse the reviewed plots without recalculation or changing range marks.
for name in ['measured-model.png','binary-comparisons.png']:
    path = ROOT / BASE / name
    sources[BASE + name] = hashlib.sha256(path.read_bytes()).hexdigest()
    outputs[LATEX / 'figures/part2' / ('dea-current-'+name)] = path.read_bytes()
read('analyses/dea_transfer/results/research-380/summary.json')
read(BASE + 'reporting-checks.json')
read('analyses/dea_transfer/inputs/part-ii-346/route-current.json')
emit('tables/part2/dea-number-sources.json',json.dumps(sources,indent=2)+'\n')
if '--check' in sys.argv:
    for path, value in outputs.items():
        assert path.read_bytes()==(value if isinstance(value,bytes) else value.encode()), path
    print(f'Numeric and retained-figure check passed: {len(outputs)} displays; {len(sources)} source files.')
else:
    for path,value in outputs.items():
        path.write_bytes(value if isinstance(value,bytes) else value.encode())
