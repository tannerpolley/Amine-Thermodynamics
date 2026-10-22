"""Generate issue 197 numerical tables from retained files; no Engine compute."""
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
NAMES = {'carbon-dioxide': 'CO2', 'monoethanolamine': 'MEA', 'water': 'water',
         'protonated-monoethanolamine': 'MEAH+', 'carbamate-anion': 'MEACOO-',
         'bicarbonate-anion': 'HCO3-', 'carbonate-anion': r'\ce{CO3^{2-}}', 'hydronium-cation': 'H3O+', 'hydroxide-anion': 'OH-'}
UNITS = dict(PartialPressure='Pa', PhaseMoleFraction='mole fraction', AdditionEnthalpy='J/mol CO2',
             amount_ratio='mol/mol total amine', pressure='Pa', phase_density='kg/m3', temperature='K',
             mole_fraction='vapour water fraction', equilibrium_isobaric_heat_capacity='J/(mol K), feed basis')


DISPLAY = {'Common149': 'Common-subset', 'common149': 'common subset', 'vapour': 'vapor', 'LogRatio': 'log ratio', 'Cai mole_fraction': 'Cai vapor water fraction', 'Vinjarapu2024': 'Vinjarapu', 'Arcis2011': 'Arcis', ' at 510000.0 Pa': ' at 0.51 MPa', ' at 1030000.0 Pa': ' at 1.03 MPa'}
def display(value):
    value = str(value)
    for old, new in DISPLAY.items():
        value = value.replace(old, new)
    return value

ORIGIN = {
    'mea-retained-phase-two-artifact': 'inherited project inputs',
    'joint-recalibration-170': 'earlier project inputs; fixed in A7',
    'joint-recalibration-170-stage5': 'earlier dielectric calibration and fixed inputs',
    'mea-model-d-p5conv-a-11-28181e72': 'earlier project calibration (ancestry)',
    'schick-2023-pabsch-2020-induced-association': 'Schick et al. 2023; Pabsch et al. 2020',
    'fakouri-baygi-pahlavanzadeh-2015': 'Fakouri Baygi and Pahlavanzadeh 2015',
}

SOURCE_TEXT = {'Austgen1991_TableV_reaction_1a': 'Austgen 1991, Table V, reaction 1a', 'Austgen1991_TableV_reaction_4a': 'Austgen 1991, Table V, reaction 4a', 'Austgen1991_TableV_reaction_5a': 'Austgen 1991, Table V, reaction 5a', 'Tong2012_Table5_K5_MEA_via_Aroua1999': 'Tong 2012, Table 5, via Aroua 1999', 'BatesPinching1951_equation_7': 'Bates and Pinching 1951, Eq. 7'}

def tex(value):
    if re.fullmatch(r'-(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', str(value)):
        return r'\mbox{' + str(value) + '}'
    parts = re.split(r'(\\ce\{(?:[^{}]|\{[^{}]*\})*\})', str(value))
    if len(parts) > 1:
        return ''.join(part if part.startswith(r'\ce{') else tex(part) for part in parts)
    if value == 'angstrom':
        return r'\AA'
    if value == 'dimensionless':
        return '1'
    escaped = ''.join({'^': r'\textasciicircum{}', '&': r'\&', '%': r'\%', '_': r'\_\allowbreak{}', '#': r'\#', '$': r'\$', '{': r'\{', '}': r'\}'}.get(c, c) for c in str(value)).replace('/', r'/\allowbreak{}')
    return re.sub(r'[a-f0-9]{64}', lambda m: r'\allowbreak{}'.join(m.group()[i:i+8] for i in range(0,64,8)), escaped)


def num(value, digits=6):
    return '--' if value is None or value == '' else f'{float(value):.{digits}g}'


def label(identity):
    for source, name in sorted(NAMES.items(), key=lambda item: -len(item[0])):
        identity = identity.replace(source, name)
    identity = identity.replace('reciprocal_temperature_slope', 'temperature slope').replace('_', ' ')
    kind, _, rest = identity.partition('/')
    parts = rest.split('/')
    if kind == 'component':
        identity = ' '.join(parts)
    elif kind == 'pair':
        identity = parts[0] + '–' + parts[1] + ' ' + ' '.join(parts[2:]).replace('k ij', 'kij')
    elif kind == 'association' and len(parts) >= 5:
        identity = f'{parts[0]}({parts[1]})–{parts[2]}({parts[3]}) association ' + ' '.join(parts[4:])
    return identity.replace(' over k', '/k').replace('debye huckel', 'Debye–Hückel').replace('reaction:', '').replace(':correlation:a k', ' A').replace(':', ' ')

def table(name, caption, headings, data, widths=None):
    caption = display(caption.replace('CO₂', r'\ce{CO2}'))
    widths = widths or [1/len(headings)]*len(headings)
    cols = '@{}' + ''.join(r'>{\raggedright\arraybackslash}p{' + f'{w*.94:.4f}' + r'\linewidth}' for w in widths) + '@{}'
    head = ' & '.join(tex(h) for h in headings) + r' \\'
    body = [r'\begingroup\small\setlength{\tabcolsep}{2pt}', r'\begin{longtable}{' + cols + '}',
            r'\caption{' + caption + r'}\label{tab:' + name.removesuffix('.tex').replace('_', '-') + r'}\\',
            r'\toprule', head, r'\midrule\endfirsthead', r'\toprule', head, r'\midrule\endhead',
            r'\bottomrule\endfoot']
    body += [' & '.join(tex(display(x)) for x in row) + r' \\' for row in data]
    OUTPUTS[name] = '\n'.join(body + [r'\end{longtable}\endgroup', ''])


def main():
    fit, summary, document, fitted, spec, density, heat, errors, paired = a.checked()
    a.bind(Path(__file__))
    coords = {c['identity']: c for c in fit['coordinates']}
    # Operator rows partition the eight groups; common149 is not counted again.
    groups = {}
    for r in fitted:
        groups.setdefault((r['group'], r['quantity']), []).append(r)
    objective = []
    operators = {'PartialPressure':'CO2 vapour partial pressure', 'PhaseMoleFraction':'liquid species / declared aggregate',
                 'AdditionEnthalpy':'integral heat of absorption', 'amount_ratio':r'(\ce{MEAH+}, \ce{MEACOO-}, \ce{HCO3- + CO3^{2-}}) / total amine; two states',
                 'pressure':'CO2-water bubble pressure', 'phase_density':'liquid density',
                 'temperature':'MEA-water bubble temperature', 'mole_fraction':'vapour water fraction',
                 'equilibrium_isobaric_heat_capacity':'equilibrium isobaric Cp'}
    for (group, quantity), part in groups.items():
        def unique(key):
            return ', '.join(num(x) if key != 'form' else x for x in sorted({r[key] for r in part}, key=lambda x: float(x) if key != 'form' else x))
        scales = [float(r['scale']) for r in part]
        scale = num(scales[0]) if len(set(scales)) == 1 else num(min(scales)) + ' to ' + num(max(scales)) + ' (row-specific)'
        objective.append([group, 'liquid species fraction' if group=='restored species' else operators[quantity], 'liquid mole fraction' if group=='restored species' else UNITS[quantity], len(part), unique('form'), scale, unique('weight'), num(math.fsum(float(r['cost']) for r in part))])
    for group in ['common149','Cai']:
        objective.append([group+' subtotal (already included)', '--', '--', fit['groups'][group]['n'], '--', '--', '--', num(fit['groups'][group]['cost'])])
    objective.append(['Objective total', '--', '--', 307, '--', '--', '--', num(fit['cost'])])
    table('objective_groups.tex', r'A7 objective operators. Rows partition eight disjoint groups and 307 quantities; common149 contains pressure, species and heat. Cai contains 25 temperatures and 25 vapour fractions at 25 states. Difference residuals are $(y_c-y_o)/s$; LogRatio residuals are $\ln(y_c/y_o)/s$. Cost is $\frac12\sum w r^2$. Scales retain their declared meaning; they are not uniformly measurement uncertainties.',
          ['Group', 'Operator', 'Unit/basis', 'n', 'Residual', 'Scale', 'Weight', 'Cost'], objective, [.13,.16,.15,.04,.12,.16,.10,.14])
    residual = []
    for name in ['common149 pressure', 'common149 species', 'restored species', 'Jakobsen', 'Kiepe', 'loaded density', 'CO2-free density']:
        s = fit['groups'][name]
        residual.append([name, 'calibration; Kiepe checks fixed inputs' if name == 'Kiepe' else 'calibration', s['n'], 'AARD', num(s['AARD_percent']), '%'])
    for quantity in ['temperature', 'mole_fraction']:
        part = groups['Cai', quantity]
        s = a.stats(part)
        residual.append(['Cai ' + quantity, 'calibration', len(part), 'RMSE; bias', num(s['RMSE']) + '; ' + num(s['bias']), 'K' if quantity == 'temperature' else 'vapour water fraction'])
    for name, s in summary['heat'].items():
        residual.append([name, 'calibration' if name == 'Vinjarapu2024' else 'acceptance check', s['n_total'], 'RMSE; bias', num(s['RMSE']) + '; ' + num(s['bias']), 'kJ/mol CO2'])
    for r in a.rows(a.E / 'cp.csv'):
        residual.append([f"Hilliard Cp, {r['T_K']} K, loading {r['loading']}", 'calibration', 1, 'signed error', num(r['error_percent']), '%'])
    table('residual_summary.tex', r'A7 property deviations. AARD denotes mean absolute relative deviation. Calibration errors and acceptance checks do not establish physical validation; Cai operators use native units. Cp remains on its source mass basis.',
          ['Cohort', 'Role', 'n', 'Statistic', 'Value', 'Unit'], residual, [.24,.21,.04,.16,.20,.15])
    parameter_rows, pair_rows = [], []
    for kind in ['components', 'pairs']:
        for node in document[kind]:
            for c in node['coefficients']:
                identity = c['identity']
                role = 'fitted in A7' if identity in coords else 'fixed in A7'
                tie = next((x for x in fit['coordinates'] for t in x['ties'] if t['identity'] == identity), None)
                if tie:
                    role = 'tied to ' + label(tie['identity'])
                source = c.get('provenance', {})
                origin = 'A7 joint fit (this work)' if identity in coords else 'tied to an A7 fitted coordinate' if tie else ORIGIN.get(source.get('source_id', ''), source.get('source_id', ''))
                row = [label(identity), num(c['value']['magnitude'], 10), c['value']['unit'], role,
                       '; '.join(filter(None, [origin, c.get('qualification', '').replace('candidate_extrapolation', 'candidate extrapolation')])) + ('; Tref='+str(c['reference_temperature']['magnitude'])+' K' if 'reference_temperature' in c else '')]
                (parameter_rows if kind == 'components' else pair_rows).append(row)
    def sources(node):
        entries = node.get('source', {}).get('provenance', [node.get('provenance', {})])
        return '; '.join(filter(None, [*dict.fromkeys(ORIGIN.get(entry['source_id'], entry['source_id']) for entry in entries if entry), node.get('qualification', '').replace('candidate_extrapolation', 'candidate extrapolation')]))

    for node in document['correlations'] + document['model_coefficients'] + document['topology']['edges']:
        for identity, c in a.coefficients(node):
            parameter_rows.append([label(identity), num(c['value']['magnitude'], 10), c['value']['unit'], 'fixed correlation/association input', sources(node)])
    for site in document['topology']['sites']:
        parameter_rows.append([label(site['component_id'])+' site '+site['site_id'], site['multiplicity'], '--',
                               'fixed '+site['site_role']+' site', sources(site)])
    for edge in document['topology']['edges']:
        source = edge['source']
        if source['kind'] == 'combining-rule':
            endpoints = [label(edge[k]['component_id'])+'('+edge[k]['site_id']+')' for k in ['endpoint_a','endpoint_b']]
            parameter_rows.append(['–'.join(endpoints), source['rule_id'], '--', 'fixed combining rule; '+
                                   '; '.join(k.replace('energy_over_k', 'energy')+' from '+' and '.join(label(x) for x in v) for k,v in source['inputs'].items()), sources(edge)])
    for family in document['model_families']:
        parameter_rows.append([family['family_id'], family['choice'], '--', 'model choice', family.get('qualification', '').replace('candidate_extrapolation', 'candidate extrapolation')])
    table('full_ionic_ssm_ds_parameters.tex', r"""A7 species, association and correlation inputs. Packing diameters are $0.88\sigma$ and the six ion Debye--H\"uckel diameters equal $\sigma$. The provenance column distinguishes the A7 fit from inherited project inputs and source ancestry; inherited labels do not establish that every current value was reported directly in the named source. Entries marked ``candidate extrapolation'' retain that qualification from the selected parameter file; absence of the label does not establish validation. ``Fixed'' means fixed in A7, including inputs estimated earlier. Water diameter is constant plus the sum of amplitude times exponential of coefficient times temperature; no new values are evaluated here. Fixed association topology: CO₂, MEA and water each have one donor site a and one acceptor site b. MEA(a)–water(b) and MEA(b)–water(a) use the retained Wolbach–Sandler combining rule with the corresponding self-association inputs. These topology declarations are fixed in A7.""",
          ['Parameter/input', 'Value', 'Unit', 'Role', 'Provenance/qualification'], parameter_rows, [.33,.13,.12,.20,.22])
    table('binary_interaction_parameters.tex', r'A7 binary parameters. Temperature slopes multiply $(1/T-1/T_{\rm ref})$, with retained reference temperatures listed explicitly. Unlisted interactions retain the selected document conventions, including the same-sign ion dispersion exclusion. Fixed inputs are not new A7 fitted coordinates.',
          ['Parameter', 'Value', 'Unit', 'Role', 'Provenance/qualification'], pair_rows, [.31,.16,.12,.19,.22])
    reaction = a.load(a.ROOT / 'data/reference/MEA/manifests/chemical_reaction_source_contract.json')
    reaction_rows = []
    for i, r in enumerate(reaction['reactions']):
        rid = r['reaction_id']
        selected = next((x for x in document['reaction_correlations'] if x['reaction_id'] == rid), None)
        coeff = '; '.join(label(c['identity'].split(':')[-1]).split()[0].upper() + ' = ' + num(c['value']['magnitude'], 10) for c in selected['coefficients']) if selected else '; '.join(k.split('_')[0].upper() + ' = ' + str(v) for k, v in r['correlation'].items() if k != 'kind')
        offset = reaction['common_source_standard_state']['source_to_common_ln_k_offsets'][i]
        reaction_rows.append([rid + r': \ce{' + r['equation'].replace('CO3--', 'CO3^{2-}').replace('HCO3-', 'HCO3^-') + '}', coeff, SOURCE_TEXT.get(r['selected_source'], r['selected_source']), str(r['temperature_range_k']),
                              'offset included in R2 coefficients' if rid == 'R2' else 'add source-to-common offset '+num(offset)])
    table('reaction_equilibrium_constants.tex', r'A7 reaction correlations and source conventions. R1/R3 are fixed source laws; R2/R4/R5 list the selected coefficients. R1--R3 use $\ln K=A+B/T+C\ln T+DT$, R4 $\ln K=A+B/T$, and R5 $\ln K=-\ln(10)(A/T+B+CT)$. R2/R5 fitted shifts are already included: do not apply them again. Source ranges are not A7 validation domains. The common aqueous molality standard is 1 mol/kg at infinite dilution in water.',
          ['Reaction', 'Coefficients', 'Source', 'Source range (K)', 'Offset'], reaction_rows, [.25,.28,.20,.10,.17])
    coordinate_rows = []
    for c, se in zip(fit['coordinates'], errors, strict=True):
        coordinate_rows.append([str(c['optimizer_column']) + ': ' + label(c['identity']), num(c['value'], 8), c['unit'],
                                ' to '.join(num(v,8) for v in c['bounds']), num(c['origin'],8) + '; ' + num(c['d_scientific_d_optimizer'],8),
                                'bound; no symmetric SE' if se['bound_active'] == 'True' else num(se['conditional_standard_error']),
                                '; '.join(label(t['identity'])+' = '+str(t['factor'])+' times coordinate' for t in c['ties'])])
    table('fitted_coordinates.tex', r'All 16 A7 scientific coordinates in optimizer-column order. Transformation: value = origin + signed slope times optimizer coordinate. R5 A is unshifted; enthalpy shifts are inherited-plus-fitted totals. Conditional standard errors (SE) depend on weights, fixed inputs, active bounds and local linearization; they are not measurement uncertainties or prediction intervals.',
          ['Coordinate', 'Value', 'Unit', 'Bounds', 'Origin; signed slope', 'Conditional SE', 'Ties'], coordinate_rows, [.23,.12,.07,.14,.16,.14,.14])
    uncertainty = a.load(a.E / 'conditional-uncertainty.json')
    correlations = a.rows(a.E / 'conditional-correlations.csv')
    free = uncertainty['free_coordinates']
    assert len(free) == uncertainty['free_rank'] == 10 and uncertainty['degrees_of_freedom'] == 297
    corr_rows = [[str(free.index(r['coordinate_a'])), str(free.index(r['coordinate_b'])), num(r['correlation'],8)] for r in correlations]
    table('supplement_correlations.tex', r'A7 conditional correlations: ten free coordinates, rank ten, 297 degrees of freedom. Variance factor ' + num(uncertainty['residual_variance'],10) + r'. Free-coordinate indices below follow: ' + tex('; '.join(str(i)+': '+label(n) for i,n in enumerate(free))) + r'. Six active-bound coordinates and all conditional errors are in the coordinate table. This local calculation does not establish uniqueness or prediction intervals.',
          ['Free index a', 'Free index b', 'Correlation'], corr_rows)
    old = a.load(a.E / 'predecessor-f1.json')
    old_engine = a.load(a.F / 'evaluation/execution.json')
    for path, digest in old['inputs'].items():
        a.bind(a.ROOT / path)
        assert a.INPUTS[path] == digest
    comparison = [r for r in a.rows(a.F / 'fit-comparison.csv') if r['objective'] == 'with heat']
    f1 = next(r for r in comparison if r['problem'] == 'F1')
    oldheat = [r for r in a.rows(a.F / 'heat-comparison.csv') if r['record'] == 'heat F1' and not r['pressure_Pa']]
    native = a.load(a.F / 'F1-A/native-fit.json')
    common = {r['id']: r for r in fitted if r['group'] == 'common149'}
    assert set(native['targets']) == set(common) and len(common) == 149
    for identity, obs, pred, residual in zip(native['targets'], native['observed'], native['predictions'], native['weighted_residuals'], strict=True):
        r = common[identity]
        a.close(obs, r['observed'])
        raw = math.log(pred/obs) if r['form'] == 'LogRatio' else pred-obs
        a.close(raw/float(r['scale'])*math.sqrt(float(r['weight'])), residual)
    predecessor = [[q, n, num(f1[key]), num(fit['groups'][group]['AARD_percent']), '%'] for q,n,key,group in
                   [('Pressure AARD',47,'pressure_AARD_percent','common149 pressure'),('Species AARD',94,'species_AARD_percent','common149 species')]]
    predecessor += [['Vinjarapu RMSE',8,num(next(x['RMSE_kJ_mol'] for x in oldheat if x['source']=='Vinjarapu2024')),num(summary['heat']['Vinjarapu2024']['RMSE']),'kJ/mol CO2'],
                    ['Common-subset cost',149,num(f1['cost']),num(fit['groups']['common149']['cost']),'dimensionless']]
    old_density = a.rows(a.F / 'corrected-densities.csv')
    old_states = a.load(a.F / 'density-states.json')
    assert len(old_states) == len(old_density) == 68
    assert all(x['solved_state']['phases'][0]['pressure_pa'] == 101325 for x in old_states)
    a.bind(a.BUNDLE / 'scripts/heat_evidence_170.py')
    matched = []
    for r in old_density:
        matches = [d for d in density if d['source']=='Amundsen2009' and float(d['P_Pa'])==100000 and all(float(d[k])==float(r[field]) for k,field in [('T_K','temperature_K'),('loading','loading'),('mea_mass_fraction','mea_mass_fraction')])]
        assert len(matches) <= 1
        if matches:
            d=matches[0]
            a.close(d['observed_kg_m3'],r['observed_kg_m3'])
            matched.append((r,d))
    assert matched
    for title, key in [('Native F1 density','eos_density_kg_m3'),('A7 density','predicted_kg_m3')]:
        part=[{'observed':r['observed_kg_m3'],'predicted':r[key] if key in r else d[key]} for r,d in matched]
        predecessor.append([title+' matched AARD',len(part),num(a.stats(part)['AARD_percent']) if key=='eos_density_kg_m3' else '--',num(a.stats(part)['AARD_percent']) if key!='eos_density_kg_m3' else '--','%'])
    table('supplement_predecessor.tex', r'F1 predecessor versus A7. Common149 identities, observations, units and effective residual scales/weights reconcile, with 47 pressures, 94 species and eight heats. F1 uses its original retained parameter and Engine identities; its 152-quantity wheel-transfer check does not qualify other results. Native F1 density is the untranslated equation-of-state density at 101325 Pa; A7 uses 100000 Pa (1325 Pa difference). Rows match temperature, loading and unloaded-solvent mass fraction exactly, not pressure. No pressure-density derivative is retained in these density records, so no magnitude bound is claimed. These Amundsen states exclude unmatched temperatures/loadings and other sources. Matched ' + str(len(matched)) + ' of ' + str(len(old_density)) + r' F1 rows; the pressure basis is disclosed, not matched.',
          ['Metric', 'n', 'F1', 'A7', 'Unit'], predecessor, [.42,.06,.18,.18,.16])
    OUTPUTS['supplement_predecessor.tex'] += '% Temperature/loading/mass-fraction matched IDs (pressure disclosed, not matched): '+', '.join(d['id'] for _,d in matched)+'\n'
    OUTPUTS['supplement_predecessor.tex'] += '% F1 excluded rows: none. A7 rows outside baseline: '+', '.join(d['id'] for d in density if d['id'] not in {x['id'] for _,x in matched})+'\n'
    historic = []
    for r in comparison:
        historic.append([r['problem'],r['targets'],num(r['pressure_cost']),num(r['species_cost']),num(r['heat_cost']),num(r['cost']),
                         '/'.join(num(r[k+'_AARD_percent']) for k in ['pressure','species','heat'])])
    table('supplement_fits.tex', r'Predecessor-model F1--F6 with-heat study. Each fit retains its own target count and costs; F4/F5 include pool targets. These are different models, not A7 Born, pool or source-law controls. AARD order is pressure/species/heat. Coordinates follow in a separate table.',
          ['Fit','n','Pressure cost','Species cost','Heat cost','Total cost','AARD (percent)'],historic,[.06,.06,.16,.16,.16,.16,.24])
    coordinate_keys = [k for k in f1 if k.startswith('pair/')]
    previous = OUTPUTS['supplement_fits.tex']
    table('supplement_fits.tex', r'Predecessor fitted coordinates: ' + tex('; '.join(str(i)+': '+label(k) for i,k in enumerate(coordinate_keys))) + '.',
          ['Fit']+[str(i) for i in range(len(coordinate_keys))],[[r['problem']]+[num(r[k],8) for k in coordinate_keys] for r in comparison])
    OUTPUTS['supplement_fits.tex'] = previous + OUTPUTS['supplement_fits.tex'].replace('tab:supplement-fits','tab:supplement-fits-coordinates')
    fixed = a.J / 'amendment-7/fixed-study/wheel-8298c602'
    endpoints = ['after-adoption/a6-selected','restricted-endpoint','restricted-2-endpoint']
    scores = [a.load(fixed / p / 'score.json') for p in endpoints]
    a6_provenance = a.load(a.J/'amendment-6/selected-assessment/provenance.json')
    first_endpoint = a.bind(a.J/'amendment-7/restricted/fit/usable-budget-endpoint.json')
    assert a.INPUTS[str(first_endpoint.relative_to(a.ROOT))] == scores[1]['parameter_sha256']
    comparison_identities = dict(A6_original_assessment=a.record_identity(a6_provenance['parameter_sha256'], a6_provenance['engine']),
                                **{name: a.phase_identity(fixed/path, fit['engine']) for name,path in zip(['A6_after_adoption','First_A7','Accepted_A7'], endpoints, strict=True)})
    a.bind(a.J / 'amendment-7/restricted/README.md')
    reductions = [a.load(fixed / p / 'reduction.json') for p in endpoints]
    acceptance = []
    for title,key,limit,authority,f1value in [('Common-subset cost','C149','35.26','F1 value + 10% (rounded; retained for A7)',f1['cost']),('Pressure AARD (%)','pressure_AARD_pct','15.81','F1 value + 2 percentage points (rounded; retained for A7)',f1['pressure_AARD_percent']),('Species AARD (%)','species_AARD_pct','9.89','F1 value + 2 percentage points (rounded; retained for A7)',f1['species_AARD_percent']),('Vinjarapu RMSE (kJ/mol)','vinjarapu_rmse_kJ_mol','3.13','F1 value + 1 kJ/mol (rounded; retained for A7)',next(x['RMSE_kJ_mol'] for x in oldheat if x['source']=='Vinjarapu2024')),('Loaded within 2s','loaded_within_2s','47/47','declared density requirement; three failures disclosed',''),('Cai cost','cai_cost','95.90','constant-interaction Cai cost + 5% (rounded; retained for A7)','')]:
        acceptance.append([title,limit,authority,num(f1value) if f1value!='' else 'inapplicable']+[num(s[key]) for s in scores])
    acceptance.append(['Descent points','0/73','declared finite-family requirement; no continuous certificate','omitted']+[str(sum(x['resolved_trials']>0 for x in d))+'/73' for d in reductions])
    acceptance.append(['CO2-free max absolute error (kg/m3)','1.0','declared density requirement','inapplicable']+[num(max(abs(x) for x in s['co2_free_errors'].values())) for s in scores])
    acceptance.append(['307-row cost','none','report only; not comparable to F1 total cost','inapplicable']+[num(s['cost']) for s in scores])
    for name,ceiling in [('Arcis2011',9.36)]:
        a6=a.load(a.J/'amendment-6/selected-assessment/summary.json')
        acceptance.append(['Arcis RMSE (kJ/mol)',num(ceiling),'F1 value + 1 kJ/mol (rounded; acceptance check)',num(next(x['RMSE_kJ_mol'] for x in oldheat if x['source']==name)),num(a6['heat'][name]['RMSE']),'unavailable',num(summary['heat'][name]['RMSE'])])
    table('acceptance_limits.tex', r'Acceptance limits and endpoint values. The declared rounded ceilings allow a 10\,\% increase in common-subset cost, two percentage points in pressure and species AARD, and \SI{1}{\kilo\joule\per\mole} in each heat RMSE relative to F1; these absolute limits were explicitly retained for A7. The Cai ceiling is the rounded value of 1.05 times the preceding constant-interaction Cai-only cost. Density and finite-phase requirements were set separately. The three density failures remain failures; accepting A7 with them changed no limit. Unavailable means no retained assessment. A6 and A7 phase values come from the same software build.',
          ['Quantity','Limit','Authority','F1 reference','A6','First restricted fit','A7'],acceptance,[.19,.10,.25,.11,.11,.12,.12])
    state = a.rows(a.E/'state-targets.csv')
    source_rows = []
    meta = {r['target']:r for r in state if r['kind']=='packet'}
    by_source = {}
    for r in fitted:
        source = meta.get(r['id'],{}).get('source', r['id'].split('_')[0].split('-')[0])
        by_source.setdefault((source,r['group'],r['quantity']),[]).append(r)
    for (source,group,quantity), part in by_source.items():
        source_rows.append([source,group,label(quantity),len(part),num(a.stats(part)['RMSE']) if group=='Cai' else num(a.stats(part)['AARD_percent']),num(math.fsum(float(r['cost']) for r in part))])
    table('supplement_source_aard.tex',r'A7 calibration deviations by source, group and observable. Deviation is AARD in percent except Cai RMSE in K or vapour water mole fraction. It does not combine quantities into an accuracy ranking. Costs sum disjoint fitted rows; quantity meanings and native units are in the objective table.',
          ['Source','Group','Observable','n','Deviation','Cost'],source_rows,[.18,.20,.24,.05,.16,.17])
    outside=[]
    for name,s in a.load(a.E/'state-summary.json')['scores'].items():
        part = [r for r in state if r['identity'] in s['state_ids'] and r['target'] in s['row_ids'] and r['target'] not in common and r['target'] not in {x['id'] for x in fitted}]
        if part:
            score = a.stats(part)
            bias = math.fsum(math.log(float(r['predicted'])/float(r['observed'])) for r in part)/len(part)
            outside.append([name, 'outside objective IDs; previously accessed', len(part), num(score['AARD_percent']), num(bias)])
    table('supplement_outside_fit.tex',r'A7 retained state cohorts. Fitted IDs are removed from each retained cohort; canonical and packet subsets still overlap and must not be pooled. Named high-temperature, transfer, Wagner and Matin-pool comparisons retain prior data access. Arcis is an acceptance check in the property table, not independent validation.',
          ['Cohort/view','Data use','n','AARD (%)','Mean ln(calc/obs)'],outside,[.30,.29,.06,.15,.20])
    density_rows=[]
    loaded_ids=set(spec['loaded_density_ids'])
    excluded=set(summary['density']['Amundsen source-conflict five']['row_ids'])
    free_ids=set(summary['density']['Amundsen CO2-free gate five']['row_ids'])
    for r in density:
        role='excluded source conflict' if r['id'] in excluded else 'fitted loaded' if r['id'] in loaded_ids else 'fitted CO2-free' if r['id'] in free_ids else 'non-fitted comparison'
        if r['id'] in loaded_ids and abs(float(r['error_over_s'])) > 2:
            role += '; FAIL >2s'
        density_rows.append([r['id'],r['source']+'; '+role,num(r['T_K']),num(r['P_Pa']),num(r['loading'])+'; '+num(r['mea_mass_fraction']),num(r['observed_kg_m3'])+'; '+num(r['predicted_kg_m3']),num(r['error_kg_m3'])+'; '+num(r['s_kg_m3'])+'; '+num(r['error_over_s'])])
    table('supplement_carbonate_density.tex',r'All 210 native A7 densities. Temperature is K, pressure Pa, density/error/scale are kg/m3; mass fraction uses unloaded solvent. Scales are not uniformly source uncertainties, and 2s is not a 95 percent interval. Amundsen source pressure is unreported; 100000 Pa is the declared calculation basis. Its high-temperature/loading uncertainty boundary remains unresolved; source locators and per-row uncertainty scope remain in density.csv. The $2s$ requirement on the 47 fitted loaded densities does not apply to non-fitted or excluded rows.',
          ['Row ID','Source; role','T','P','Loading; mass fraction','Observed; calculated','Error; s; e/s'],density_rows,[.22,.20,.07,.08,.12,.16,.15])
    previous=OUTPUTS['supplement_carbonate_density.tex']
    carbonate=a.rows(a.E/'carbonate-share.csv')
    table('supplement_carbonate_density.tex',r'All ten carbonate-share comparisons (different observables from the six fitted Jakobsen amount ratios). Corrected unloaded MEA mass fraction is '+num(float(carbonate[0]['mea_mass_fraction']),10)+r'; model loading uses NMR. Historical-nine membership is provenance, not an exclusion. Source: Jakobsen et al.\ \cite{Jakobsen2005}, Tables A1--A2 (p.~9902) and Table~2 (p.~9896).',
          ['ID','T (K)','NMR loading; maxload','Observed share','Calculated share','Calc/obs','Historical nine'],[[r['id'],r['T_K'],num(r['model_loading'])+'; '+num(r['maxload']),num(r['observed_share']),num(r['predicted_share']),num(r['calc_over_obs']),r['historical_nine_included']] for r in carbonate],[.25,.08,.17,.13,.13,.12,.12])
    OUTPUTS['supplement_carbonate_density.tex']=previous+OUTPUTS['supplement_carbonate_density.tex'].replace('tab:supplement-carbonate-density','tab:supplement-carbonate-share')
    phase_rows=[]
    for i in range(73):
        x,y=paired['A6'][i],paired['A7'][i]
        phase_rows.append([i,x['temperature_K'],x['loading'],x['pressure_Pa'],x['classification']+'; trials '+x['resolved_trials']+'; success '+x['final_success']+'; failed '+x['failed_trial_optimizers'],y['classification']+'; trials '+y['resolved_trials']+'; success '+y['final_success']+'; failed '+y['failed_trial_optimizers']])
    table('supplement_phase_family.tex',r'The 73 matched A6/A7 states on the A7 software build: 12/73 versus 0/73 resolved-descent points. Resolved counts are trial counts, not Gibbs changes. Blank minimum fields report no resolved minimum. Index 0 repeats the index-41 state with a rounded pressure; both are listed. A two-phase classification alone does not establish a liquid–liquid split. This finite search does not certify a continuous stable region.',
          ['Index','T (K)','Loading (exact)','P (Pa, exact)','A6','A7'],phase_rows,[.05,.08,.22,.21,.22,.22])
    previous=OUTPUTS['supplement_phase_family.tex']
    split_rows=[]
    split_phases=[]
    for i in [21,63,70]:
        for r in a.load(a.J/f'amendment-6/selected-checks/phase-diagnosis/split-seeded-{i}.json'):
            for phase in r['result'].get('phases', []):
                split_phases.append([i,r['seed']+' / '+phase['identity'],num(phase['amount_mol']),num(phase['molar_density_mol_m3']),'; '.join(num(x) for x in phase['mole_fractions'])])
            split_rows.append([i,r['seed'],str(r['result']['success']),num(r['delta_G_over_RT_vs_original'],10),num(r['delta_G_over_RT_vs_single_liquid'],10),'; '.join(num(v) for v in r['result']['molar_densities']),'; '.join(p['identity']+' ('+p['role']+')' for p in r['result'].get('phases', [])) or 'unavailable: failed split'])
    identity=a.load(a.J/'amendment-6/selected-checks/phase-diagnosis/engine-identity.json')
    identity='wheel SHA-256 '+identity['wheel_sha256']
    table('supplement_phase_family.tex',r'Separately seeded A6 split solves, including failed attempts. Original Engine identity (not the same-wheel classification comparison): '+tex(identity.strip())+r'. Gibbs differences are extensive $\Delta G/(RT)$ values in mol for the retained feed amounts; phase densities are mol/m3. Only successful split solves support the split comparison.',
          ['Index','Seed','Success','Delta vs original','Delta vs single liquid','Densities','Phases'],split_rows,[.06,.17,.09,.14,.14,.18,.22])
    OUTPUTS['supplement_phase_family.tex']=previous+OUTPUTS['supplement_phase_family.tex'].replace('tab:supplement-phase-family','tab:supplement-split-states')
    previous=OUTPUTS['supplement_phase_family.tex']
    table('supplement_phase_family.tex', r'A6 successful split phase amounts (mol), densities (mol/m3) and mole fractions in source order: CO2, MEA, water, MEAH+, carbamate, bicarbonate, carbonate, hydronium, hydroxide. Vapour rows list only their three supported neutral species (CO2, MEA, water); liquid rows list all nine. The same original Engine identity applies.',
          ['Index','Seed / phase','Amount','Density','Mole fractions in declared order'],split_phases,[.05,.20,.11,.12,.52])
    OUTPUTS['supplement_phase_family.tex']=previous+OUTPUTS['supplement_phase_family.tex'].replace('tab:supplement-phase-family','tab:supplement-split-compositions')
    previous=OUTPUTS['supplement_correlations.tex']
    table('supplement_correlations.tex', r'A7 conditional errors in the complete scientific-coordinate order, including six bound-active coordinates without symmetric SE. These are local sensitivities conditional on the stated weights, fixed inputs and bounds.',
          ['Coordinate','Value','Unit','Conditional SE'],[[label(r['identity']),num(r['value'],8),r['unit'],'bound; unavailable' if r['bound_active']=='True' else num(r['conditional_standard_error'])] for r in errors],[.47,.17,.14,.22])
    OUTPUTS['supplement_correlations.tex']=previous+OUTPUTS['supplement_correlations.tex'].replace('tab:supplement-correlations','tab:supplement-conditional-errors')
    for name, body in OUTPUTS.items():
        head='% Generator: docs/scientific/latex/scripts/final_rerun_tables.py; do not hand-edit.\n'
        head+='% A7 parameter SHA256: '+fit['record_sha256']+'\n'
        if name == 'acceptance_limits.tex':
            head += '% Record identities: '+json.dumps(comparison_identities,sort_keys=True)+'\n'
            head += '% '+a.A6_ASSESSMENT_NOTE+'\n'
        head+='% F1 original wheel SHA256: '+old_engine['wheel_sha256']+'\n' if name in ['supplement_fits.tex','supplement_predecessor.tex','acceptance_limits.tex'] else ''
        head+='% F1 predecessor inputs/identity: '+json.dumps(old,sort_keys=True)+'\n' if name in ['supplement_fits.tex','supplement_predecessor.tex','acceptance_limits.tex'] else ''
        head+=''.join('% Input: '+p+' SHA256 '+h+'\n' for p,h in sorted(a.INPUTS.items()))
        (TABLES/name).write_text(head+body)
    print(json.dumps(dict(objective_rows=len(fitted),group_costs=fit['groups'],loaded_density=len(loaded_ids),densities=len(density),heats=len(heat),coordinates=len(errors),phase_points=73,matched_F1_densities=len(matched)),indent=2))


if __name__ == '__main__':
    main()
