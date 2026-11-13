"""Render Part II tables and discrete figures from retained values; no model imports."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LATEX = ROOT / 'docs/scientific/latex'
TABLES = LATEX / 'tables/part2'
FIGURES = LATEX / 'figures/part2'
INPUTS = {}
NUMBERS = []


def read(path):
    raw = (ROOT / path).read_bytes()
    INPUTS[path] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw) if path.endswith('.json') else list(csv.DictReader(raw.decode().splitlines()))


def value(path, keys, digits=2):
    x = read(path)
    for key in keys:
        x = x[key]
    shown = f'{x:.8g}' if digits == 'g' else f'{x:.{digits}f}'
    NUMBERS.append((shown, path, json.dumps(keys), str(x)))
    return shown


def table(name, caption, headers, rows, widths):
    cols = ''.join(r'>{\raggedright\arraybackslash}p{' + str(w) + r'\linewidth}' for w in widths)
    def cell_text(cell):
        text = str(cell)
        if re.fullmatch(r'[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?', text):
            text = re.sub(r'e([-+]?\d+)', lambda m: r'\times10^{' + str(int(m[1])) + '}', text)
            return '$' + text + '$'
        return re.sub(r'(?<!\\)([&%])', r'\\\1', text)
    body = '\n'.join(' & '.join(cell_text(cell) for cell in row) + r' \\' for row in rows)
    # Longtable follows the Part I generator's booktabs style and permits page breaks.
    tex = (r'\begingroup\small\setlength{\tabcolsep}{3pt}' '\n'
           r'\begin{longtable}{@{}' + cols + r'@{}}' '\n'
           r'\caption{' + caption + r'}\label{tab:p2-' + name + r'}\\' '\n'
           r'\toprule ' + ' & '.join(headers) + r' \\ \midrule\endfirsthead' '\n'
           r'\toprule ' + ' & '.join(headers) + r' \\ \midrule\endhead' '\n'
           r'\bottomrule\endfoot' '\n' + body + '\n' + r'\end{longtable}\endgroup' '\n')
    (TABLES / (name + '.tex')).write_text(tex)


M = 'analyses/solvent_specification_mdea/results/retained-statistics-320.json'
A = 'analyses/amp_transfer/results/refit-306/summary.json'
P = 'analyses/pz_transfer/results/reactive-A12-record.json'
K = 'analyses/pz_transfer/results/kamps2003-A12.json'
D = 'analyses/dea_transfer/results/score.json'
DF = 'analyses/dea_transfer/results/fits.json'
W = 'analyses/mdea_mea_workflow/results/refit-298/pressure-scores.json'
amp = read(A)
assert amp['scored'] == 'refit-306-floor'
assert sum(x['rows'] for k, x in read(M)['B1_fitted_by_source'].items() if 'rows' in x) == 278
assert read(P)['holdout']['rows'] == 52
rows = []
for key, name in [('Kuranov','MDEA: Kuranov total pressure'),('Jakobsen','MDEA: protonated fraction'),('Carson','MDEA: Carson heat'),('Merkley','MDEA: Merkley heat'),('Cp',r'MDEA: $C_P$'),('loaded-density','MDEA: loaded density'),('unloaded-density','MDEA: unloaded density'),('Kim','MDEA: binary pressure')]:
    rows.append([name, value(M,['B1_fitted_by_source',key,'rows'],0),value(M,['B1_fitted_by_source',key,'AARD_percent']),value(M,['B1_fitted_by_source',key,'scaled_RMS'])])
for name, keys in [('AMP: Hartono total pressure',['steps','4 k widened, floor 5.32 A','calibration','loaded_pressure']),('PZ: Hilliard partial pressure',['hilliard'])]:
    if name.startswith('AMP'):
        rows.append([name,value(A,keys+['rows'],0),value(A,keys+['mean_abs_percent']), '--'])
    else: rows.append([name,'62',value(P,keys+['MARE_percent']),value(P,['pressure_RMS'])])
for key, name in [('Lawson','DEA: Lawson partial pressure'),('Carson','DEA: Carson integral heat')]:
    rows.append([name,value(DF,['runs','B-2','errors',key,'n'],0),value(DF,['runs','B-2','errors',key,'mean_abs_percent']),'--'])
table('calibration','Calibration deviations. AARD uses each observable separately. Scaled RMS is the root mean square of residuals divided by their assigned observation scales, before applying additional objective weights. Pressure residuals are logarithmic for MDEA and relative differences for PZ. These statistics do not provide a cross-amine accuracy ranking.', ['Observable and fitted source','$n$',r'AARD / \%','Scaled RMS'],rows,[.48,.07,.16,.17])

rows=[]
for source in ['Xiao','Ermatchkov']:
    for block,label in [('overall','all'),('inside_278_368K','278--368 K'),('outside_278_368K','above 368 K')]:
        if read(M)['ermatchkov_xiao_pressure'][source][block] is None or (source == 'Xiao' and block != 'overall'): continue
        keys=['ermatchkov_xiao_pressure',source,block]
        rows.append(['MDEA '+source,label,value(M,keys+['rows'],0),value(M,keys+['AARD_percent']),value(M,keys+['bias_percent'])])
for block,label in [('overall','all'),('isotherms','')]:
    groups=[([],label)] if block=='overall' else [([t],t+' K') for t in ['303.0','313.0','323.0']]
    for extra,label in groups:
        k=['kundu',block]+extra
        rows.append(['AMP Kundu',label,value(A,k+['rows'],0),value(A,k+['E_p']),value(A,k+['bias_percent'])])
rows.append(['AMP Tong (total)','313--353 K',value(A,['tong','new','scored'],0),value(A,['tong','new','E_p']),value(A,['tong','new','bias_percent'])])
for extra,label in [([],'all'),(['by_temperature','313.1'],'313.1 K'),(['by_temperature','353.15'],'353.15 K'),(['by_temperature','393.15'],'393.15 K')]:
    k=['holdout']+extra
    rows.append(['PZ Ermatchkov',label,value(P,k+['n' if extra else 'rows'],0),value(P,k+['MARE_percent']),value(P,k+['bias_percent'])])
for source in ['SeoHong','Lal']:
    for k,label in [(['overall'],'all')]+[(['per_temperature',t],t+r'$\,^{\circ}$C') for t in read(D)[source]['per_temperature']]:
        rows.append(['DEA '+(r'Seo \& Hong' if source=='SeoHong' else source),label,value(D,[source]+k+['n'],0),value(D,[source]+k+['mean_abs_percent']),value(D,[source]+k+['bias_percent'])])
for row in rows:
    amine, condition = row[:2]
    domain = 'mixed' if condition == 'all' else 'inside'
    if amine == 'MDEA Xiao': domain = 'inside'
    elif amine.startswith('MDEA') and condition == 'above 368 K': domain = 'dissociation extrapolated'
    elif amine == 'AMP Kundu' and condition == '303.0 K': domain = 'hydrolysis slope extrapolated'
    elif amine.startswith('PZ') and condition == '353.15 K': domain = 'carbamate extrapolated'
    elif amine.startswith('PZ') and condition == '393.15 K': domain = 'carbamate and protonation extrapolated'
    elif amine.startswith('DEA') and condition != 'all' and not condition.startswith('40'): domain = 'protonation extrapolated'
    row.append(domain)
rows.append(['PZ Kamps (total)','all',value(K,['summary','overall','n'],0),value(K,['summary','overall','AARD_percent'],1),value(K,['summary','overall','bias_percent'],1),'mixed; comparison-only'])
table('unfitted','Unfitted pressure errors by source and temperature. MDEA sets were previously accessed; AMP Kundu and PZ Ermatchkov were scored before final parameter selection, and DEA was first scored on a numerically tied fit. Kamps was scored once after the PZ fit was frozen. All are partial pressures except AMP Tong and PZ Kamps.', ['Amine and source','Conditions','$n$',r'AARD / \%',r'Bias / \%','Measured-law range'],rows,[.20,.15,.04,.10,.10,.29])
rows=[]
for group in ['inside_278_368K','outside_278_368K']:
    k=['B1_fitted_by_source','Kuranov_by_law_range',group]
    rows.append(['Kuranov total pressure','inside' if group.startswith('inside') else 'outside',value(M,k+['rows'],0),value(M,k+['AARD_percent']),value(M,k+['bias_percent'])])
for t in ['333.15','388.71']:
    k=['B1_fitted_by_source','Merkley_by_temperature_K',t]
    rows.append([r'Merkley heat (20 and 40 wt\%)',('inside (' if t=='333.15' else 'outside (')+t+' K)',value(M,k+['rows'],0),value(M,k+['AARD_percent']),value(M,k+['mean_signed_error_predicted_minus_observed'],0)+r' J/mol'])
table('mdea-range','Fitted MDEA errors separated against the 278--368 K dissociation measurements. Heat signed errors are calculated minus measured; they are not relative biases.', ['Observable','Law range / $T$','$n$',r'AARD / \%','Bias / signed error'],rows,[.31,.19,.07,.14,.18])
rows=[]
path='analyses/mdea_mea_workflow/results/refit-298/pressure-comparison.csv'
for i,r in enumerate(read(path)):
 if r['source'] != 'Ermatchkov': continue
 vals=[]
 for field in ['rebased_baseline_AARD_percent','fixed_substitution_AARD_percent','refit_AARD_percent']:
  vals.append(f"{float(r[field]):.2f}"); NUMBERS.append((vals[-1],path,f'row {i}, {field}',r[field]))
 rows.append(['MDEA alternative ion description A3 (Ermatchkov)' if r['record']=='A3' else 'MDEA reported fit (Ermatchkov)',*vals])
historical=read('analyses/amp_transfer/results/kundu/summary.json')
rows.append(['AMP (Kundu)',value('analyses/amp_transfer/results/kundu/summary.json',['variants','historical','overall','E_p']),value(A,['old','kundu','overall','E_p']),value(A,['steps','2 #243 limits','kundu','overall','E_p'])])
table('shared-sensitivity','Same-data pressure AARD (\\%). Each row compares the earlier shared inputs, substitution of the Part I bicarbonate--water interaction and R2 law without refitting the amine, then amine-specific refitting. A3 is a counter-case, not the selected MDEA description. AMP here uses the original bounds; its final bounded fit is reported separately.', ['Amine fit (unfitted source)','Earlier','Substituted','Refitted'],rows,[.48,.13,.13,.13])
rows=[]
for key,title in [('old','Shared substitution; no AMP refit')]+[(k,lab) for k,lab in zip(amp['steps'],['Original AMP limits','Carbamate diameter floor raised','Cation--CO2 interaction widened','Carbamate diameter floor lowered'])]:
 k=['old'] if key=='old' else ['steps',key]
 rows.append([title,value(A,k+['calibration','cost']),value(A,k+['calibration','loaded_pressure','mean_abs_percent']),value(A,k+['calibration','nmr_rms'],5),value(A,k+['kundu','overall','E_p']),value(A,k+['kundu','overall','bias_percent'])])
table('amp-chain','AMP same-data sequence. Calibration uses total pressure and carbamate fraction; Kundu uses partial pressure and remains outside every objective. The fourth row is the reported fit.', ['Change','Cost',r'Fitted $P$ AARD / \%','Species RMS',r'Kundu AARD / \%',r'Bias / \%'],rows,[.35,.09,.13,.11,.13,.09])

# Kamps summaries use the frozen-fit comparison and row-level law labels.
krows=read('analyses/pz_transfer/results/kamps2003-A12.csv')
assert len(krows)==read(K)['summary']['overall']['n']==94
rows=[]
for group in ['below 0.2 MPa','374-395 K','313-354 K, 0.2 MPa and above','unloaded']:
 k=['summary','by_group',group]
 rows.append([group.replace('-', '--'),value(K,k+['n'],0),value(K,k+['AARD_percent'],1),value(K,k+['bias_percent'],1)])
table('kamps-groups',r'Kamps total-pressure groups. Loaded high-temperature groups exclude unloaded rows and pressures below 0.2 MPa. Overall: 94 rows, 42.5\,\% AARD, $-40.3$\,\% bias.', ['Group','$n$',r'AARD / \%',r'Bias / \%'],rows,[.52,.08,.15,.15])
rows=[]
for block in read(K)['summary']['by_block']:
 t,m=block.split(' K, ');m=m.split()[0]
 b=[r for r in krows if r['T_K']==t and float(r['mPZ'])==float(m)]
 assert len(b)==read(K)['summary']['by_block'][block]['n']
 for field,shown in [('T_K',t),('mPZ',m)]:
  NUMBERS.append((shown,'analyses/pz_transfer/results/kamps2003-A12.csv','row '+b[0]['row']+', '+field,b[0][field]))
 labels=[b[0][f] for f in ['carbamate_law','protonation_law','shared_R2_law']]
 rows.append([t,m,*labels,value(K,['summary','by_block',block,'n'],0),value(K,['summary','by_block',block,'AARD_percent'],1),value(K,['summary','by_block',block,'bias_percent'],1)])
table('kamps-blocks',r'Kamps total-pressure blocks at corrected temperatures. Law labels: carbamate measurements 283.15--333.15 K; protonation measurements 293.14--353.42 K; shared R2 interval 293.15--393.15 K. Unloaded rows are included. Labels describe temperature ranges, not phase stability.', ['$T$ / K',r'$m_{PZ}$ / mol kg$^{-1}$','Carbamate','Protonation','R2','$n$',r'AARD / \%',r'Bias / \%'],rows,[.10,.12,.13,.14,.10,.04,.10,.10])
c=read(K)['summary']['census']
table('kamps-census','Kamps phase census at 94 scored bubble states. Split counts are lower bounds; states without a detected split do not prove stability.', ['Outcome','States'],[
 ['No additional phase found',value(K,['summary','census','no_extra_phase'],0)],
 ['Resolved dense-liquid split',str(len(c['dense_split']))],
 ['Undecided (unloaded rows)',value(K,['summary','census','undecided'],0)],
 ['Gas split',str(len(c['gas_split']))],['Ambiguous',str(len(c['ambiguous']))]], [.65,.20])
for field in ['dense_split','gas_split','ambiguous']:
 NUMBERS.append((str(len(c[field])),K,'len(summary.census.'+field+')',str(len(c[field]))))
for path in ['analyses/pz_transfer/results/check-states-A12.json','analyses/pz_transfer/results/check-states-A12-direct.json']:
 read(path)

# Full scalar input tables retain units from the parameter documents.
shared={'water','carbon-dioxide','hydronium-cation','hydroxide-anion','bicarbonate-anion','carbonate-anion'}
short={'water':'water','carbon-dioxide':r'\ce{CO2}','hydronium-cation':r'\ce{H3O+}','hydroxide-anion':r'\ce{OH-}','bicarbonate-anion':r'\ce{HCO3-}','carbonate-anion':r'\ce{CO3^{2-}}','methyldiethanolamine':'MDEA','protonated-methyldiethanolamine':r'\ce{MDEAH+}','aminomethylpropanol':'AMP','protonated-aminomethylpropanol':r'\ce{AMPH+}','diethanolamine':'DEA','protonated-diethanolamine':r'\ce{DEAH+}','carbamate-anion':'carbamate','piperazine':'PZ','piperazinium':r'\ce{PZH+}','piperazinediium':r'\ce{PZH2^{2+}}','piperazine-carbamate':'PZ carbamate','piperazine-dicarbamate':'PZ dicarbamate','protonated-piperazine-carbamate':'HPZCOO'}
fields={'segment_count':('$m^{seg}$','1'),'segment_diameter':(r'$\sigma$',r'\AA'),'dispersion_energy_over_k':(r'$\epsilon/k_B$','K'),'born_diameter':('$d^{Born}$',r'\AA'),'debye_huckel_diameter':('$d^{DH}$',r'\AA'),'packing_diameter':('$d^{pack}$',r'\AA'),'dielectric_volume':('$d_V$','L/mol'),'dielectric_temperature':('$d_T$','K'),'solvation_factor':('$f$','1')}
endpoints={'shared':'analyses/mea_parameter_bundle/results/selected-current-best-parameters.json','mdea':'analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/endpoint.json','amp':'analyses/amp_transfer/inputs/redesign/refit-306-floor-endpoint.json','pz':'analyses/pz_transfer/results/reactive-A12-start2-endpoint.json','dea':'analyses/dea_transfer/inputs/runs/B-2-endpoint-document.json'}
for amine,path in endpoints.items():
    doc=read(path); rows=[]
    for i,c in enumerate(doc['components']):
        identity=c['component_id']
        if (amine=='shared') != (identity in shared):continue
        for j,q in enumerate(c['coefficients']):
            if q['family'] not in fields or not isinstance(q['value'].get('magnitude'),(float,int)):continue
            symbol,unit=fields[q['family']]
            rows.append([short.get(identity,identity.replace('-',' ')),symbol,value(path,['components',i,'coefficients',j,'value','magnitude'],'g'),unit])
    table(amine+'-parameters',('Shared species' if amine=='shared' else amine.upper()+' amine-specific species')+' inputs. Constant scalar coefficients are shown; temperature laws, site topology, ties and fitted quantities are specified in the text and electronic parameter files.', ['Species','Quantity','Value','Unit'],rows,[.34,.20,.21,.12])

# Conditional standard errors and sensitivity (all values come from stored ranking rows).
for amine,path in [('mdea','analyses/solvent_specification_mdea/results/uncertainty-307/ranking.csv'),('amp','analyses/amp_transfer/results/refit-306/uncertainty/ranking.csv'),('pz','analyses/pz_transfer/results/uncertainty-A12/ranking.csv'),('dea','analyses/dea_transfer/results/uncertainty-307/ranking.csv')]:
    rows=[]
    for i,r in enumerate(read(path)):
        name=r['parameter']
        for old,new in sorted(short.items(),key=lambda x:-len(x[0])):name=name.replace(old,new)
        name=name.replace('[','').replace(']','').replace("'",'').replace('_',r'\_').replace(' / ',': ').replace('k\\_ij\\_reciprocal\\_temperature\\_slope','water interaction slope')
        name=name.replace('dispersion\\_energy\\_over\\_k',r'$\epsilon/k_B$').replace('segment\\_diameter',r'$\sigma$').replace('temperature\\_law\\_coefficient','coefficient').replace('pair/mdea-water/k\\_ij/','MDEA--water ')
        vals=[]
        for key in ['value','SE_bound_fixed','max_fractional_change']:
            s=r.get(key,''); vals.append('--' if s=='' else f'{float(s):.5g}')
            if s!='':NUMBERS.append((vals[-1],path,f'row {i}, {key}',s))
        rows.append([name,*vals])
    table(amine+'-uncertainty',amine.upper()+' conditional parameter errors and largest fractional prediction change. The last column uses one marginal standard error for interior parameters and the first inward refit step for bound parameters; these perturbations have different sizes. Units follow the named parameters; enthalpy shifts are J/mol.', ['Parameter','Value','SE','Largest change'],rows,[.52,.12,.12,.13])


# Categorical information is transcribed from the four approved notebooks and Part I.
for path in ['analyses/solvent_specification_mdea/notebook.qmd','analyses/mdea_mea_workflow/notebook.qmd','analyses/amp_transfer/notebook.qmd','analyses/pz_transfer/notebook.qmd','analyses/dea_transfer/notebook.qmd','docs/scientific/latex/supplement.tex']:
 INPUTS[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
table('origins','Transferred quantities and their origins. All shared quantities remain fixed here; amine-specific interactions with shared species may be fitted.', ['Quantity','Origin in Part I','Implication here'],[
 ['Water segment, energy and association coefficients','Independent fit to IAPWS-95','Fixed; not fitted to any of these amines'],
 [r'\ce{CO2} segment and energy coefficients',r'Gross and Sadowski, Table 2 \cite{Gross2001}','Literature inputs; fixed'],
 [r'\ce{CO2}--water dispersion correction and slope','Independent fit to Kiepe pressures','Fixed'],
 ['Inorganic-ion segment sizes and energies',r'Uyan et al., Table 4 \cite{Uyan2015}','Fixed; hydrogen-ion values used for hydronium'],
 ['Inorganic Born sizes and remaining water--ion terms','Assumed inputs in Part I','Fixed; not independently measured in MEA'],
 ['Bicarbonate--water interaction','MEA joint fit, upper bound $+1$','Fixed at bound; conditional SE excludes this direction'],
 ['R2 level and enthalpy correction','MEA joint fit; interior with conditional errors','Fixed; source-law correction, not a new measurement'],
 ['R1 and R3 water/carbonate laws','Literature laws as mapped in Part I','Fixed with source-reference conversion'],
 ['Solvation and dielectric descriptions','Literature coefficients and assumptions in Part I','Water/CO2 inputs fixed; amine coefficients specified separately'],
 ['Reactive coordinates (MDEA / AMP / PZ / DEA)','Amine-specific fits: 9 / 9 / 12 / 4','Not totals of earlier pure and binary fitting'],
 ],[.32,.36,.25])
table('laws',"Reaction-law measurement intervals and use. A calculation inside a declared interval can still extrapolate the measurements. Rounded source limits are distinguished from actual tabulated temperatures.", ['Law','Measured interval / K','Declared interval / K','Use and limitation'],[
 ['MDEA dissociation','278--368','278--395','393.15 K pressure and 388.71 K heat extrapolate measurements'],
 ['AMP dissociation','to 353.22','to 353.22','Tong 373--393 K rows not calculated (outside declared interval)'],
 ['AMP hydrolysis','source estimates: 313--373','includes 303--353','Not direct law measurements; slope extrapolated below 313 K; level and slope fitted'],
 ['PZ protonation','293.14--353.42','includes 283.15--395.0','283.15 K and above 353.42 K extrapolate'],
 ['PZ carbamate','283.15--333.15 (rounded 283--333)','includes 353.15--395.0','Above 333.15 K extrapolates'],
 ['DEA protonation','to approximately 323','to 393.15','23/30 fitted Lawson rows above measured range'],
 ['Shared R2','not established here','293.15--393.15','Seven Lawson rows at 394.26 K not calculated (outside declared interval); PZ 283.15 K extrapolates below lower limit; Kamps 395.0 K above upper limit'],
 ],[.18,.23,.22,.28])
table('data-roles','Observation roles and prior access. Held out means never in any fitting objective. Comparison-only means calculated after parameter selection without entering that selection. Prior scoring is stated even when no held-out value determined the objective.', ['Amine / role','Observations','Scored before final fit chosen?'],[
 ['MDEA fitted','278 entries: 67 Kuranov; 16 Jakobsen; 40 Carson; 4 Merkley; 33 heat capacities; 33 loaded and 24 unloaded densities; 61 Kim binary pressures','---'],
 ['MDEA held-out','20 Xiao and 88 Ermatchkov partial pressures','Yes; previously accessed in model development'],
 ['MDEA exclusions','Kuranov source rows 28 and 72; seven states above the 393.15 K R2 limit','Not counted as available predictions'],
 ['AMP fitted','156 entries: 47 Hartono loaded total pressures; 52 Hartono binary entries; 57 Ciftja fractions','---'],
 ['AMP held-out','51 Kundu partial pressures','Yes; scored during the sequence preceding final diameter choice'],
 ['AMP held-out comparison','17 Tong total pressures scored; 23 not calculated','Earlier fits had been compared; no blind test claimed'],
 ['PZ fitted','294 entries: 62 Hilliard pressures; 232 NMR group observations at 121 states','---'],
 ['PZ held-out','52 Ermatchkov partial pressures','Yes; unconstrained refit scored before penalty alternative and final choice'],
 ['PZ comparison-only','94 Kamps total pressures; precipitation row excluded','No; scored once on frozen twelve-coordinate fit'],
 ['DEA fitted','80 entries: 30 Lawson pressures at 25 wt%; 50 Carson heats','---'],
 ['DEA held-out','16 Seo and Hong; 44 Lal partial pressures','Yes; first selected start, then numerically tied second start'],
 ['DEA comparison-only','Lawson Table VIII; Cai binary; Böttinger species; Horstmann excess heat; Weiland densities','No; added after fit selection'],
 ],[.20,.48,.25])
table('phase-searches','Finite phase-search results. Detected liquid-split counts are lower bounds.', ['Fit / states','Detected liquid splits','Other outcomes and omissions'],[
 ['MDEA: 775 searched states','0 found','37 gas-like phases; no ambiguous or unresolved result; seven states above the R2 interval not calculated'],
 ['AMP: 51 Kundu states','0 found','No gas, ambiguous or unresolved result; calibration gas outcomes not stored'],
 ['PZ: 183 calibration states','at least 4','No ambiguous or unresolved result; three rich NMR pressures moved above bubble pressure'],
 ['PZ: 52 held-out bubble states','0 found','Finite search only'],
 ['PZ: 94 Kamps bubble states','at least 36','56 without detected split; 2 unloaded undecided; no gas or ambiguous split'],
 ['PZ: compressed Hilliard states','at least 4','At 1.5 times bubble pressure; routine search misses two'],
 ['PZ: 121 NMR states at $T+0.5$ K','0 found','Three rich states above 0.1 MPa evaluated at 1.05 times bubble pressure'],
 ['PZ penalty alternative','at least 3','One found routinely; two additional splits resolved by direct distance evaluation'],
 ['DEA: 140 fitted/held-out states','0 found','No gas, ambiguous or unresolved result'],
 ],[.30,.20,.43])
# Nonzero amine-specific pair coefficients and association edges complete the scalar tables.
for amine,path in endpoints.items():
 doc=read(path);rows=[]
 for i,pair in enumerate(doc['pairs']):
  names=pair.get('components',pair.get('component_ids',[]))
  for j,c in enumerate(pair['coefficients']):
   ident=c['identity'];v=c.get('value',{}).get('magnitude')
   if not isinstance(v,(int,float)) or v==0:continue
   if amine!='shared' and not any(cmp not in shared for cmp in ident.split('/')[1:3]):continue
   if amine=='shared' and not all(cmp in shared for cmp in ident.split('/')[1:3]):continue
   parts=ident.split('/');nm='--'.join(short.get(cmp,cmp.replace('-',' ')) for cmp in parts[1:3])
   family=c['family'].replace('_',' ')
   rows.append([nm,family,value(path,['pairs',i,'coefficients',j,'value','magnitude'],7)])
 for i,edge in enumerate(doc['topology'].get('edges',[])):
  a=edge['endpoint_a']['component_id'];b=edge['endpoint_b']['component_id']
  if (amine=='shared') != (a in shared and b in shared):continue
  nm=short.get(a,a)+'--'+short.get(b,b)
  for field,title in [('energy_over_k','association energy / K'),('volume','association volume')]:
   if field in edge and 'value' in edge[field]:rows.append([nm,title,value(path,['topology','edges',i,field,'value','magnitude'],7)])
 if rows:table(amine+'-interactions',('Shared' if amine=='shared' else amine.upper())+' nonzero constant pair coefficients and explicit association edges. Unlisted constant pair corrections are zero. Temperature-law coefficients are stated separately.', ['Pair','Quantity','Value'],rows,[.40,.33,.19])

# Complete source-state law coefficients. Logarithms use T/T0, T0=313.15 K.
import tomllib
lawsets={}
for amine,path in [('mdea','analyses/solvent_specification_mdea/B1-declarations.toml'),('dea','analyses/dea_transfer/inputs/runs/B-2-endpoint-declarations.toml')]:
 INPUTS[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
 lawsets[amine]=tomllib.loads((ROOT/path).read_text())['chemistry']['reactions']['aqueous']
lawsets['pz']=read('analyses/pz_transfer/results/speciation-reactions.json')
for r in lawsets['pz']:
 if r['name'] in ['P3','P4','P5']:r['correlation']['a']+=read(P)['offsets'][['P3','P4','P5'].index(r['name'])]
# AMP completed hydrolysis is the recorded scored law; its fixed dissociation declaration is explicit.
path='analyses/amp_transfer/inputs/kundu/current-declarations.toml'
INPUTS[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
lawsets['amp']=tomllib.loads((ROOT/path).read_text())['chemistry']['reactions']['aqueous']
for r in lawsets['amp']:
 if r['name']=='carbamate-hydrolysis':r['correlation']=read(A)['runs']['refit-306-floor']['law']
for amine,laws in lawsets.items():
 rows=[]
 for r in laws:
  c=r['correlation'];name=r['name'].replace('-',' ')
  rows.append([name,*[f'{c.get(k,0):.7g}' for k in ['a','b','c','d']], 'molality' if 'molality' in c.get('standard_state_id','') else 'mole fraction'])
 table(amine+'-laws',amine.upper()+r' reaction coefficients in $\ln K=a+b/T+c\ln(T/313.15\,\mathrm K)+dT$. Coefficients $a,c$ are dimensionless, $b$ is K and $d$ is K$^{-1}$. Source-reference basis is retained, not silently interchanged. PZ P3--P5 include the fitted offsets.', ['Reaction','$a$','$b$','$c$','$d$','Basis'],rows,[.22,.13,.13,.13,.15,.14])
# Source locators copied from the numerical rows keep transcription identities explicit.
rows=[]
for r in read('analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/fitted-replay.json'):
 q=r['meta']['row'];g=r['meta']['group']
 if any(z[0]=='MDEA '+g for z in rows):continue
 loc=q.get('source_locator',q.get('source_table','')+', printed p. '+q.get('source_printed_page',''))
 rows.append(['MDEA '+g,q.get('source_key',''),loc])
rows.extend([
 ['AMP loaded total pressure',r'Hartono et al. (2021) \cite{hartonoNewSolubilityHeat2021}','Table 7; 47 fitted rows at 313, 333 and 353 K'],
 ['AMP binary pressure and vapor composition',r'Hartono et al. (2013) \cite{hartonoBinaryTernaryVLE2013}','Table 3; 26 pressure and 26 vapor-composition observations'],
 ['AMP carbamate fraction',r'Ciftja et al. (2014) \cite{ciftjaExperimentalStudyCarbamate2014a}','Supporting Information, Tables S1--S3; 57 observations'],
])
rows.extend([
 ['PZ fitted partial pressure',r'Hilliard (2008) \cite{Hilliard2008}','Appendix D.5, printed pp. 916--917'],
 ['PZ NMR groups',r'Ermatchkov et al. (2003) \cite{ermatchkovChemicalEquilibriumConstants2003}','Tables 1--4; 121 states'],
 ['PZ comparison-only total pressure',r'Kamps et al. (2003) \cite{kampsSolubilityCO2H2O+piperazine2003a}',r'Table 3, p. 2666; corrected temperatures: Ermatchkov (2006), Table 6, p. 1794; excludes precipitation row (313.75 K, 1.995 mol/kg, loading 1.69, 4.446 MPa)'],
 ['PZ held-out partial pressure',r'Ermatchkov et al. (2006) \cite{ermatchkovSolubilityCarbonDioxide2006a}','Tables 1--3, printed p. 1789'],
 ['DEA fitted partial pressure',r'Lawson and Garst (1976) \cite{lawsonGasSweeteningData1976}','Table II, PDF p. 4; 30 fitted rows'],
 ['DEA fitted integral heat',r'Carson et al. (2000) \cite{carsonEnthalpySolutionCarbon2000}','Table 2; 50 rows at 298.15 K'],
])
for group in ['SeoHong','Lal']:
 q=read(D)[group]['table'][0]['row'];rows.append(['DEA '+group,q['source_key'],q['source_locator']])
for group in ['weiland','lawson_viii','bottinger_DEACOO','cai','excess_enthalpy']:
 q=read(D)['comparisons'][group]['rows'][0];q=q.get('row',q);rows.append(['DEA '+group.replace('_',' '),q.get('source_key',''),q.get('source_locator','')])
source_citations = {
 'Kuranov1996':'kuranovSolubilitySingleGases1996', 'Jakobsen2005':'Jakobsen2005',
 'Carson2000':'carsonEnthalpySolutionCarbon2000','Merkley1987':'merkleyEnthalpiesAbsorptionCarbon1987',
 'Weiland1997':'weilandHeatCapacityAqueous1997','Weiland1998':'Weiland1998',
 'Sobrino2016':'sobrinoViscosityDensityMeasurements2016','Kim2008':'kimEbulliometricDeterminationVaporLiquid2008',
 'SeoHong1996':'seoSolubilitiesCarbonDioxide1996','Lal1985':'lalSolubilityH2SCO21985',
 'LawsonGarst1976':'lawsonGasSweeteningData1976','Bottinger2008':'Bottinger2008',
 'Cai1996':'caiBinaryIsobaricVaporLiquid1996','Horstmann2002':'horstmannPhaseEquilibriumExcess2002'}
for row in rows:
 if row[1] in source_citations: row[1] += r' \cite{' + source_citations[row[1]] + '}'
table('source-locators','Measurement locators preserved with the calculation inputs. Source row identities and original-observable columns accompany the electronic numerical files; fitted and unfitted roles are in the main paper.', ['Observation','Source','Locator'],rows,[.25,.23,.45])


# Published scores are the source-verified values specified for the manuscript.
# They describe different fitting roles and never enter a common accuracy score.
INPUTS['docs/scientific/latex/references.bib']=hashlib.sha256((LATEX/'references.bib').read_bytes()).hexdigest()
table('published-comparisons','Published-model comparisons with data roles stated. Only the PZ Hilliard row has the same fitted source and row count in both models; objective and chemistry still differ. Tong coverage differs. MDEA and qualitative comparisons use different observation subsets.', ['Model / system','Source and published deviation','Published role / role here'],[
 [r'Yi e-NRTL, PZ \cite[Table~3]{yiOpenAccessThermodynamically2024}',r'Hilliard: 62 points, 18.0\% partial-pressure AARD','Fitted / fitted'],
 [r'Yi e-NRTL, PZ \cite[Table~3]{yiOpenAccessThermodynamically2024}',r'Ermatchkov: 52 points, 7.8\% partial-pressure AARD','Fitted / held out; previously scored'],
 [r'Yi e-NRTL, AMP \cite[Table~4]{yiOpenAccessThermodynamically2024}',r'Kundu: 51 points, 15.4\% partial-pressure AARD','Fitted / held out; previously scored'],
 [r'Yi e-NRTL, AMP \cite[Table~4]{yiOpenAccessThermodynamically2024}',r'Tong: 45 points, 8.0\% total-pressure AARD','Fitted / unfitted; 17 points here'],
 [r'Wangler ePC-SAFT, MDEA \cite[Table~11]{Wangler2018}',r'Own 82-point set: ARD 19.7\%; corrected Uyan 34.4\%','Ternary predictions / different reactive fit and partial-pressure subsets here'],
 [r'Cleeton ePC-SAFT, MDEA \cite[Sect.~3.3.2]{Cleeton2020}','Concentration and low-loading comparisons; no matched score','Ternary predictions after pure/binary estimation'],
 [r'Perdomo SAFT-$\gamma$ Mie, PZ / DEA \cite[Sects.~4.2, 4.3.3]{perdomoPredictiveGroupcontributionFramework2023}','PZ concentration transfer; Lal pressures and Böttinger species','Selected reactive group estimation; other concentrations/species predicted'],
 [r'Nasrifar PC-SAFT, DEA \cite[Sect.~6, Figs.~13--14]{Nasrifar2010}','Species and acid-gas curves; no matched score','Predicted after pure/binary estimation; ideal-activity chemistry'],
 ],[.29,.34,.29])
# Search intervals are numerical restrictions, not physical confidence limits.
rows=[]
for amine,path in [('MDEA','analyses/solvent_specification_mdea/inputs/B1-coordinates.json'),('AMP','analyses/amp_transfer/inputs/redesign/refit-306-floor-coordinates.json'),('DEA','analyses/dea_transfer/inputs/runs/B-2-coordinates.json')]:
 for i,c in enumerate(read(path)):
  if 'targets' in c:
   kind,target,*_=c['targets'][0];target='--'.join(target) if isinstance(target,list) else target
   for old,new in sorted(short.items(),key=lambda x:-len(x[0])):target=target.replace(old,new)
   name=target.replace('_',r'\_')+': '+kind.replace('_',' ')
  else:name=c['name'].replace('-',' ')+' '+c.get('coefficient','enthalpy increment / J mol$^{-1}$')
  lo,hi=c['bounds'];rows.append([amine,name,f'{lo:.6g}',f'{hi:.6g}'])
  for j,v in enumerate([lo,hi]):NUMBERS.append((f'{v:.6g}',path,f'[{i}].bounds[{j}]',str(v)))
for name,lo,hi in [('Cation diameter / '+r'\AA',2,9),('Cation dispersion / K',50,1000),('Cation--water interaction',-1,.5),('Cation--bicarbonate interaction',-1,.5),('Carbamate diameter / '+r'\AA',2,9),('Carbamate dispersion / K',50,1000),('Carbamate--water interaction',-.5,.5),('HPZCOO diameter / '+r'\AA',2,6),('HPZCOO dispersion / K',50,1000),('P3, P4 and P5 offsets (each)',-3,3)]:rows.append(['PZ',name,str(lo),str(hi)])
table('bounds','Original search bounds of the reported reactive fits. Reaction-level bounds refer to the fitted coordinate before the coupled enthalpy completion; DEA enthalpy bounds are refit increments. PZ values and ties follow the complete twelve-coordinate chart. Bounds are not measured molecular intervals.', ['Amine','Coordinate','Lower','Upper'],rows,[.09,.59,.10,.10])
rows=[]
path='analyses/mdea_mea_workflow/results/refit-298/attempts.json'
for i,r in enumerate(read(path)):
 rows.append(['MDEA '+r['name'].replace('-',' '),value(path,[i,'cost'],5),value(path,[i,'iterations'],0),str(len(r['active_bounds'])),'converged'])
for name in ['refit-306-floor','refit-306-1','refit-306-2','refit-306-243']:
 r=read(A)['runs'][name];rows.append(['AMP '+('reported floor' if name=='refit-306-floor' else '3.5 '+r'\AA\ start '+name.rsplit('-',1)[-1]),value(A,['runs',name,'cost'],5),value(A,['runs',name,'iterations'],0),str(len(r['active_bounds'])),r['status'].replace('_',' ')])
rows.append(['PZ reported',value(P,['fit','cost'],3),value(P,['fit','iterations'],0),'1','iteration limit'])
for name,r in read(DF)['runs'].items():rows.append(['DEA '+name,value(DF,['runs',name,'final_cost'],6),value(DF,['runs',name,'iterations'],0),str(len(r['active_bounds'])),r['status']])
table('fit-starts','Retained start outcomes. Costs use different objective scales and must not be compared across amines. The MDEA A3 rows and smaller-diameter AMP fits are sensitivity comparisons, not additional selected results.', ['Fit / start','Cost','Iterations','Bounds','Termination'],rows,[.39,.16,.12,.09,.16])
# Figures use only discrete calculations at measured coordinates.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':9,'pdf.fonttype':42,'savefig.bbox':'tight'})
colors=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00']
plotrows=[]
fig,axs=plt.subplots(2,2,figsize=(7.0,5.6),layout='constrained')
mp=read('analyses/solvent_specification_mdea/results/adoption-302/B1/pressure.json')
for ax in axs.flat:ax.grid(alpha=.18); ax.set_xlabel(r'Loading $\alpha$ / mol CO$_2$ per mol amine');ax.set_ylabel('Relative pressure error / %');ax.axhline(0,color='.5',lw=.6)
# MDEA pressure rows expose their source in meta.group.
mr=mp if isinstance(mp,list) else mp.get('rows',[])
for i,t in enumerate([313.15,353.15,393.15]):
    block=[r for r in mr if r['group']=='Ermatchkov' and abs(float(r['row']['temperature_K'])-t)<.2]
    if block:
        xx=[float(r['row']['m_CO2_mol_per_kg_H2O'])/float(r['row']['m_MDEA_mol_per_kg_H2O']) for r in block]
        yy=[100*r['relative_error'] for r in block]
        axs[0,0].scatter(xx,yy,s=13,color=colors[i],marker=['o','x','^'][i],label=f'{t:g} K')
        plotrows.extend([['MDEA',t,x,y] for x,y in zip(xx,yy)])
a=read('analyses/amp_transfer/results/refit-306/kundu-pressures.csv')
for i,t in enumerate(sorted({r['T_K'] for r in a})):
 b=[r for r in a if r['T_K']==t];x=[float(r['alpha']) for r in b];y=[100*(float(r['predicted_Pa'])/float(r['observed_Pa'])-1) for r in b];axs[0,1].scatter(x,y,s=13,color=colors[i],marker=['o','x','^'][i],label=t+' K');plotrows.extend([['AMP',t,xx,yy] for xx,yy in zip(x,y)])
p=read('analyses/pz_transfer/results/holdout-A12.csv')
d=read('analyses/dea_transfer/results/figure-values.csv')
for i,t in enumerate(sorted({r['T_K'] for r in p})):
 b=[r for r in p if r['T_K']==t];
 # Column names are quantity-specific and checked by a failed-key exception.
 x=[float(r['alpha_per_PZ']) for r in b];y=[100*float(r['relative_error']) for r in b];axs[1,0].scatter(x,y,s=13,color=colors[i],marker=['o','x','^'][i],label=t+' K');plotrows.extend([['PZ',t,xx,yy] for xx,yy in zip(x,y)])
for i,source in enumerate(['Seo','Lal']):
 for t,marker in zip([313.15,333.15,353.15,373.15],['o','x','^','s']):
  b=[r for r in d if source in r['set'] and abs(float(r['T_K'])-t)<.2]
  if not b: continue
  x=[float(r['alpha']) for r in b];y=[100*(float(r['predicted'])/float(r['observed'])-1) for r in b]
  axs[1,1].scatter(x,y,s=13,color=colors[i],marker=marker,label=('Seo & Hong' if i==0 else 'Lal')+f' {t-273.15:.0f} C')
  plotrows.extend([['DEA '+source,r['T_K'],xx,yy] for r,xx,yy in zip(b,x,y)])
for ax,title in zip(axs.flat,['(a) MDEA: Ermatchkov','(b) AMP: Kundu','(c) PZ: Ermatchkov','(d) DEA: held-out sources']):ax.set_title(title);ax.legend(fontsize=7,frameon=False)
fig.savefig(FIGURES/'unfitted-pressure.pdf');plt.close(fig)
with (FIGURES/'unfitted-pressure.csv').open('w') as f:
 w=csv.writer(f, lineterminator="\n");w.writerow(['set','T_K','alpha','relative_error_percent']);w.writerows(plotrows)


# Fitted pressure residuals expose loading shape while retaining separate observables.
fig,axs=plt.subplots(2,2,figsize=(7,5.2),layout='constrained')
fitted=[]
replay=read('analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/fitted-replay.json')
for r in replay:
 if r['meta']['group']=='Kuranov':
  row=r['meta']['row'];fitted.append(['MDEA',float(row['temperature_K']),float(row['m_CO2_mol_per_kg_H2O'])/float(row['m_MDEA_mol_per_kg_H2O']),100*(r['value']/r['meta']['observed']-1)])
for r in read('analyses/amp_transfer/results/refit-306/refit-306-floor-fit.json')['replay']:
 if r['group']=='loaded-pressure':fitted.append(['AMP',float(r['row']['T_K']),float(r['row']['alpha_mol_CO2_per_mol_AMP']),100*(r['value']/r['observed']-1)])
for r in read('analyses/pz_transfer/results/reactive-A12-residuals.csv'):
 if r['group']=='pressure':fitted.append(['PZ',float(r['T_C'])+273.15,float(r['alpha_per_PZ']),100*(float(r['calculated'])/(1000*float(r['pCO2_kPa']))-1)])
for r in d:
 if 'Lawson' in r['set']:fitted.append(['DEA',float(r['T_K']),float(r['alpha']),100*(float(r['predicted'])/float(r['observed'])-1)])
for ax,amine in zip(axs.flat,['MDEA','AMP','PZ','DEA']):
 block=[r for r in fitted if r[0]==amine]
 for i,t in enumerate(sorted({round(r[1]) for r in block})):
  b=[r for r in block if round(r[1])==t];ax.scatter([r[2] for r in b],[r[3] for r in b],s=12,color=colors[i%len(colors)],marker=['o','x','^','s','+'][i%5],label=f'{t} K')
 ax.axhline(0,color='.5',lw=.6);ax.set_title(amine);ax.set_xlabel(r'Loading $\alpha$ / mol CO$_2$ per mol amine');ax.set_ylabel('Pressure error / %');ax.grid(alpha=.18);ax.legend(fontsize=6,frameon=False)
 assert len(block)=={'MDEA':67,'AMP':47,'PZ':62,'DEA':30}[amine], (amine,len(block))
fig.savefig(FIGURES/'calibration.pdf');plt.close(fig)
with (FIGURES/'calibration.csv').open('w') as f:
 w=csv.writer(f, lineterminator="\n");w.writerow(['amine','T_K','alpha','error_percent']);w.writerows(fitted)

# Absorption heats and the separate wrong-sign binary mixing heat.
fig,axs=plt.subplots(1,3,figsize=(7,2.6),layout='constrained')
b=[r for r in d if 'Carson' in r['set']]
propertyrows=[['Carson-signed-heat',r['alpha'],-float(r['observed']),-float(r['predicted'])] for r in b]
axs[0].scatter([float(r['alpha']) for r in b],[-float(r['observed']) for r in b],s=13,facecolors='none',edgecolors=colors[0],label='measured')
axs[0].scatter([float(r['alpha']) for r in b],[-float(r['predicted']) for r in b],s=13,marker='x',color=colors[1],label='calculated')
axs[0].set(xlabel=r'Source CO$_2$ mole fraction',ylabel='Integral heat / kJ per mol CO$_2$',title='(a) Carson: fitted')
b=[r for r in read(D)['comparisons']['bottinger_DEACOO']['rows'] if float(r['row'].get('x_HEOD','0'))==0]
# Clean-state membership is explicit in the retained rows (checked below).
b=[r for r in b if not r.get('byproduct',False)]
assert len(b)==9
propertyrows.extend([['Bottinger-carbamate',r['row']['alpha_mol_CO2_per_mol_DEA'],r['observed'],r['value']] for r in b])
axs[1].scatter([r['observed'] for r in b],[r['value'] for r in b],s=15,marker='x',color=colors[1]);lims=[0,max(r['observed'] for r in b)*1.2];axs[1].plot(lims,lims,color='.5',lw=.7)
axs[1].set(xlabel='Measured carbamate mole fraction',ylabel='Calculated carbamate mole fraction',title='(b) Böttinger: unfitted')
b=read(D)['comparisons']['excess_enthalpy']['rows']
propertyrows.extend([['excess-enthalpy',r['x_water'],r['HE_J_per_mol'],r['HE_model']] for r in b])
with (FIGURES/'dea-properties.csv').open('w') as f:
 w=csv.writer(f, lineterminator="\n");w.writerow(['property','source_CO2_fraction_or_loading_or_water_fraction','observed','calculated']);w.writerows(propertyrows)
for field,marker,label,color in [('HE_J_per_mol','o','measured',colors[0]),('HE_model','x','calculated',colors[1])]:axs[2].scatter([float(r['x_water']) for r in b],[float(r[field]) for r in b],s=13,marker=marker,label=label,color=color)
axs[2].axhline(0,color='.5',lw=.6);axs[2].set(xlabel='Water mole fraction',ylabel='Excess enthalpy / J per mol mixture',title='(c) Horstmann: unfitted')
for ax in axs:ax.grid(alpha=.18)
axs[0].legend(fontsize=6,frameon=False);fig.savefig(FIGURES/'dea-properties.pdf');plt.close(fig)

# Ratio intervals identify scale relative to the observed pressure without implying a curve.
fig,axs=plt.subplots(1,3,figsize=(7,3.0),layout='constrained')
bandrows=[]
for ax,amine,path in zip(axs,['MDEA','AMP','DEA'],['analyses/solvent_specification_mdea/results/uncertainty-307/prediction-bands.csv','analyses/amp_transfer/results/refit-306/uncertainty/prediction-bands.csv','analyses/dea_transfer/results/uncertainty-307/prediction-bands.csv']):
 bands=read(path);lookup={}
 if amine=='MDEA':
  pred=read('analyses/solvent_specification_mdea/results/uncertainty-307/predictions.json')
  for r in (pred if isinstance(pred,list) else pred.get('records',[])):
   if r.get('group') in ['Xiao','Ermatchkov']:lookup[r['identity']]=r['arguments']['observed']
 elif amine=='AMP':lookup={r['identity']:float(r['observed_Pa']) for r in a}
 else:
  for group in ['SeoHong','Lal']:
   lookup.update({r['identity']:r['observed'] for r in read(D)[group]['table']})
 hits=[r for r in bands if r['identity'] in lookup]
 assert hits,amine
 for i,r in enumerate(hits):
  obs=lookup[r['identity']];val=float(r['value'])/obs;se=float(r['SE_bound_fixed'])/obs;bandrows.append([amine,r['identity'],obs,r['value'],r['SE_bound_fixed'],val,se]);ax.errorbar(i+1,val,yerr=1.96*se,fmt='x',ms=2.5,lw=.5,color=colors[0])
 ax.axhline(1,color='.5',lw=.7);ax.set(xlabel='Observation index',ylabel='Calculated / measured pressure',title=amine);ax.grid(alpha=.18)
fig.savefig(FIGURES/'pressure-bands.pdf');plt.close(fig)
with (FIGURES/'pressure-bands.csv').open('w') as f:
 w=csv.writer(f, lineterminator="\n");w.writerow(['amine','identity','observed','calculated','SE','ratio','relative_SE']);w.writerows(bandrows)
# Final provenance comments bind every generated table to exact input bytes.
for out in TABLES.glob('*.tex'):
 header='% Generator: docs/scientific/latex/scripts/part2_displays.py; no model evaluation.\n'
 header+=''.join(f'% Input: {p} SHA256 {h}\n' for p,h in sorted(INPUTS.items()))
 out.write_text(header+out.read_text())
(FIGURES/'provenance.json').write_text(json.dumps(INPUTS,indent=2)+'\n')
with (TABLES/'displayed-values.csv').open('w') as f:
 w=csv.writer(f, lineterminator="\n");w.writerow(['display','source_file','field','retained_value']);w.writerows(NUMBERS)
