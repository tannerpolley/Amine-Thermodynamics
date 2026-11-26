"""Render manuscript tables and figures from the amine stage records."""

import argparse
import collections
import csv
from functools import reduce
import gzip
from hashlib import sha256
import hashlib
from io import BytesIO
import json
import math
from math import fsum, sqrt
from operator import getitem
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from analyses.amines.wheel import verify

ROOT = Path(__file__).resolve().parents[2]
LATEX = ROOT / "docs/scientific/latex"
BUNDLE = ROOT / "analyses/mea_parameter_bundle"
TABLES = LATEX / "tables"
DEA_SALT_SUMMARY = "analyses/amines/results/dea/system-pressure-salt-anchored/replay/summary.json"
MEA_EXPANDED_SUMMARY = "analyses/amines/results/mea/expanded-weights/replay/summary.json"
GIBBS_DERIVATIVES = "analyses/amines/results/shared/properties/gibbs-derivatives.json"
FIT_SUMMARY = "analyses/amines/results/shared/fit/display-summary.json.gz"
PHASE_SUMMARY = "analyses/amines/results/shared/phase/display-summary.json.gz"
PROPERTY_SUMMARY = "analyses/amines/results/shared/properties/display-summary.json.gz"
sources = {}
stage_records = {}


def register_records(catalog):
    stage_records.update({
        key: ROOT / key for key, row in catalog.items()
        if "record" in row and row["disposition"] not in ("comparison-only", "orphan")
    })


def read(name):
    path = Path(name)
    if not path.is_absolute():
        path = ROOT / path
    key = path.resolve().relative_to(ROOT).as_posix()
    raw = stage_records[key].read_bytes()
    sources[key] = sha256(raw).hexdigest()
    data = gzip.decompress(raw) if path.suffix == ".gz" else raw
    if path.name.removesuffix(".gz").endswith(".json"):
        return json.loads(data)
    return list(csv.DictReader(data.decode().splitlines()))

STUDY = 'analyses/fixed_reaction_reference/'
KIEPE_AUTHOR = r'Kiepe et al.\ '
KIEPE_CITE = 'kiepeExperimentalDeterminationPrediction2002'
DESIGNS = ('MEA', 'DEA', 'MDEA', 'AMP_free', 'AMP_fixed')
MEA_LEGACY_PRESSURE_GROUP = 'MEA legacy-47'
MEA_TRACKING_FITTED_PRESSURES = '47 current-fitted pressures'
MEA_TRACKING_ADDITIONAL_PRESSURES = '112 current-not-fitted pressures'

class FixedReference:
    def __init__(self, read):
        self.read = read
        self.selections = {name: self.load(f'{name}/selection.json') for name in DESIGNS}
        self.fits = {name: self.load(f"{name}/{selection['selected']}.json.gz")
                     for name, selection in self.selections.items()}
        for name, selection in self.selections.items():
            if self.fits[name]['endpoint_fingerprint'] != selection['endpoint_fingerprint']:
                raise ValueError(f"Selected start does not match its record for {name}")

    def cost(self, name):
        return self.selections[name]['cost']

    def load(self, relative):
        return self.read(STUDY + 'results/' + relative)

    def endpoint_record(self, relative, name):
        record = self.load(relative)
        if record['endpoint_fingerprint'] != self.fits[name]['endpoint_fingerprint']:
            raise ValueError(f"Wrong endpoint for {relative}")
        return record

    def coverage(self, name, protocol='declared'):
        record = self.endpoint_record(f'{name}/screen/selected/{protocol}/summary.json.gz', name)
        record['confirmed'] = [r['key'] for r in record['classifications'] if any(a['confirmed'] for a in r['attempts'])]
        return record

    def conditional(self, name):
        fit = self.fits[name]
        diagnostic = fit['diagnostics']
        result = diagnostic['uncertainty'].copy()
        rows = fit['replay']['rows']
        active = diagnostic['active_bounds']
        coordinates = fit['endpoint']['coordinates']
        ids = [r['identity'] for r in coordinates]
        free = result['free_coordinates']
        errors = result['conditional_standard_error']
        # #420 identifies Kiepe and the three pure-water Kim rows as structural constants.
        excluded = [i for i, r in enumerate(rows) if
                    (name == 'MEA' and r['group'] == 'Kiepe') or
                    (name == 'MDEA' and r['identity'] in {'fit:227', 'fit:229', 'fit:249'})]
        all_variance = 2 * fsum(r['cost'] for r in rows) / (len(rows) - len(free))
        responsive = len(rows) - len(excluded)
        dof = responsive - len(free)
        variance = 2 * fsum(r['cost'] for i, r in enumerate(rows) if i not in excluded) / dof
        result.update(coordinates=coordinates, active_bounds=[ids.index(k) for k in active],
                      stage_variance=variance, responsive=responsive, dof=dof,
                      conditional_standard_error={k: v * sqrt(variance / all_variance) for k, v in errors.items()})
        return result

def coefficients(node):
    if isinstance(node, dict):
        if 'identity' in node and isinstance(node.get('value'), dict):
            yield node['identity'], node
        for value in node.values():
            yield from coefficients(value)
    elif isinstance(node, list):
        for value in node:
            yield from coefficients(value)


def stats(part, observed='observed', predicted='predicted'):
    errors = [float(r[predicted]) - float(r[observed]) for r in part]
    fractions = [x / float(r[observed]) for x, r in zip(errors, part, strict=True)]
    return dict(n=len(part), RMSE=math.sqrt(math.fsum(x*x for x in errors)/len(part)),
                bias=math.fsum(errors)/len(part),
                bias_percent=100*math.fsum(fractions)/len(part),
                AARD_percent=100*math.fsum(map(abs, fractions))/len(part))



def phase_control_tables(dea, amp, shared, table, head, num, scientific, dea_density, amp_outcomes):
    rows = []
    density = {r['key']: r for r in dea_density['rows']}
    for state in dea['rows']:
        d = density[state['key']]
        case = f"Deposit ID {d['deposit_id']}, processed source row {d['processed_source_row']}, "
        case += rf"{state['unloaded_wt_percent']:.0f} wt\%, $\alpha={state['loading']:.2f}$"
        phase = state['phases']
        rows += [head(case, 6)]
        for label, key, factor, digits in [
            ('Amount (mol true species)', 'amount_mol', 1, 6),
            ('Share of total true moles (\\%)', 'true_mole_fraction', 100, 4),
            ('Share of total mass (\\%)', 'mass_fraction', 100, 4),
            ('Density (kg/m$^3$)', 'density_kg_m3', 1, 3),
            (r'$\partial P/\partial\rho_{\rm mol}$ (Pa m$^3$/mol)', 'dP_drho_Pa_m3_mol', 1, 2),
            ('Molar volume (cm$^3$/mol)', 'molar_volume_m3_mol', 1e6, 5),
        ]:
            values = [num(factor*p[key], digits) for p in phase]
            bulk = [num(d[k+'_kg_m3'], 2) for k in ('observed', 'single_liquid', 'two_liquid')] if key == 'density_kg_m3' else []
            rows.append([label, *values, *bulk])
        rows += [['Mole fraction ' + symbol, *[scientific(p['x'][i]) for p in phase]]
                 for i, symbol in enumerate((r'\COtwo', 'DEA', r'\HtwoO', r'\ce{DEAH+}',
                     r'\ce{DEACOO-}', r'\ce{HCO3-}', r'\ce{CO3^2-}', r'\ce{H3O+}', r'\ce{OH-}'))]
        rows += [
            ['Charge residual (mol)', *[scientific(p['charge_residual_mol']) for p in phase]],
            ['Pressure residual (Pa)', *[scientific(p['pressure_residual_Pa']) for p in phase]],
            ['Maximum reaction residual',
             *[scientific(max(abs(r['residual']) for r in state['reaction_contractions'] if r['phase']==i)) for i in range(2)]],
            ['Maximum interphase residual', scientific(state['max_interphase_residual']), ''],
            ['Elemental balance residuals (mol)', 'C, H, N, O',
             ', '.join(scientific(state['balances']['element_residual_mol'][e]) for e in 'CHNO')],
            [r'$\Delta G^*/(RT)$ decrease and paired error (mol)',
             scientific(state['split']['Gibbs_decrease_over_RT_mol']), scientific(state['split']['numerical_error_over_RT_mol'])],
            ['Two liquid roots', 'Matched', 'Matched'],
            ['Confirmed search / registry-growth repeat', f"{state['declared_confirmed']} / {state['registry_growth_confirmed']}", ''],
            ['Restart from its own daughters', 'Confirmed' if state['daughter_restart']['confirmed'] else 'Coalesced', ''],
        ]
    rows = [row + [''] * (6-len(row)) if len(row) > 1 else row for row in rows]
    feeds = NUMBER_WORDS[len(dea['rows'])]
    rows.append([rf'Density AARD across the {feeds} feeds (\%)', '', '', '',
                 *[num(dea_density['AARD_percent'][m], 3) for m in ('single_liquid', 'two_liquid')]])
    matrix = dea['rows'][0]['conservation_matrix']
    B = r'$\left[\begin{smallmatrix}' + r'\\'.join('&'.join(str(round(x)) for x in row) for row in matrix) + r'\end{smallmatrix}\right]$'
    worked = next(q for q in dea['rows'] if q['key'] == dea['worked_state'])
    worked_density = density[worked['key']]
    dense_phase = max(worked['phases'], key=lambda q: q['density_kg_m3'])
    table('supplement-dea-split-certificate',
          f'Two-liquid certificates for the {feeds} DEA density-cell feeds at 298.15 K and assigned 101.325 kPa.',
          ['Quantity', 'Liquid 1', 'Liquid 2', 'Measured bulk', 'Single-liquid bulk', 'Two-liquid bulk'],
          rows, [.35,.13,.14,.093,.105,.105], long=True, size=r'\footnotesize',
          notes=(rf"One mol DEA in each feed. Deposit IDs are zero-based. The {100 * dense_phase['true_mole_fraction']:.2f}\% "
          f"for the denser liquid of processed source row {worked_density['processed_source_row']} divides "
          r'its true-species amount by the sum of both daughter amounts. '
          r'The two-liquid bulk density is $(\sum_i w_i/\rho_i)^{-1}$ using daughter mass fractions $w_i$ and densities $\rho_i$. '
          r'Liquid roots must match within $|\ln(\rho_{\rm root}/\rho)|\le\ln(1.01)$ and relative pressure error $\le10^{-10}$. '
          r'Both phases must have positive isothermal pressure derivatives and positive amounts and differ by more than $10^{-6}$ in maximum mole-fraction difference or log density ratio. '
          r'The decrease in $G^*/(RT)$ must exceed the paired numerical error. Reaction residuals are $\ln Q-\ln K$ and interphase residuals are differences in '
          r'electrochemical potential divided by $RT$. '
          r'For main-text Eq.~(\ref{main-eq:tpd}), $g=G^*/n$ on the true-species molar basis and $B=$ ' + B +
          f" in the displayed species order, with charge enforced separately. Deposit ID {worked_density['deposit_id']} "
          f"(processed source row {worked_density['processed_source_row']}) is reproduced from the retained neighboring-state start."))

    rows = []
    for state in sorted(amp['rows'], key=lambda q: q['key'] != 'worked-state'):
        key = state['key']
        if key == 'worked-state':
            src = 'Worked feed'
            early = r'Two liquids, $\Delta G^*/(RT)=' + f"-{state['early_attempts'][0]['Gibbs_decrease_over_RT_mol']:.5f}" + '$ mol'
        else:
            family, search, _ = key.split(':')
            src = family.split('-')[0].title() + f" r{state['source']['row']} ({search})"
            early = 'Two liquids'
        witness = state['witness']
        if witness:
            reported = 'Vapor-directed descent'
            lv = 'L+V passed' if state['reported_liquid_vapor_gate'] == 'passed' else 'L+V vapor root unspecified'
            gates = ' / '.join(state['reported_two_liquid_gates'])
        else:
            reported = 'No resolved descent'
            lv = '---'
            gates = '---'
        if key == 'worked-state':
            gates = 'Indeterminate reduced Hessian'
        else:
            reported = amp_outcomes[key]['outcome'].replace('; ', r'\newline ')
        rows.append([src, num(state['T_K'], 2), num(state['P_Pa']/1e6, 5), num(state['reported_bubble_Pa']/1e6, 5),
                     early, reported, gates, lv])
    test_pressures = sum(state['key'] == 'worked-state' for state in amp['rows'])
    measured_pressures = len(amp['rows']) - test_pressures
    unspecified = sum(state.get('reported_liquid_vapor_gate') == 'strict vapor-root identity'
                      for state in amp['rows'])
    table('amp-endpoint-pressure-controls',
          f'Early and reported AMP fits at {NUMBER_WORDS[test_pressures]} common test pressure '
          f'and {NUMBER_WORDS[measured_pressures]} measured total pressures.',
          ['Source row (search ID)', '$T$ (K)', '$P$ (MPa)', r'Reported $P_{\rm bub}$ (MPa)',
           'Early fit', 'Reported outcome', 'Reported L+L refusal', 'Reported L+V'],
          rows, [.113,.070,.085,.105,.121,.127,.161,.140], size=r'\footnotesize',
          notes=r'Tong row numbers restart at each temperature. The early fit uses the system-pressure reference and the reported fit uses 100 kPa. '
          r'The worked feed contains 1 mol AMP at unloaded 30 wt\% and $\alpha=0.70$. '
          r'A dilute-vapor connection was checked for each descent with an unspecified returned density branch. '
          f'For {NUMBER_WORDS[unspecified]} L+V candidates the residuals passed and the strict vapor-root label was unspecified. '
          r'No L+L control passed at the reported endpoint.')

    labels = {MEA_LEGACY_PRESSURE_GROUP: r'MEA, fitted $p_{\COtwo}$',
              'MEA Mamun2005': r'MEA, Ma\textquotesingle mun $p_{\COtwo}$',
              'MDEA Kuranov': 'MDEA, Kuranov loaded total pressure',
              'MDEA Ermatchkov': r'MDEA, Ermatchkov $p_{\COtwo}$',
              'MDEA Carson': 'MDEA, Carson integral heat'}
    rows = [[labels[key], f"{len(case['common'])}/{case['requested']}",
             *[num(case['models'][name]['AARD_percent'], 2) for name in ('salt-anchored','MEA-fitted')]]
            for key, case in shared['comparisons'].items()]
    receiver = shared['fit_stages']['MDEA'][-1]
    table('supplement-shared-interaction-sensitivity',
          'Matched observations for the salt-anchored and historical MEA-fitted shared interactions at 100 kPa.',
          ['Observable', 'Common / requested', r'Salt-anchored AARD (\%)', r'MEA-fitted shared AARD (\%)'],
          rows, [.41,.15,.19,.19],
          notes=r'Start A only for the sensitivity. The alternative has $k_{\rm water,HCO_3^-}=0.765000$ '
          r'and $k_{\rm water,CO_3^{2-}}=-0.25$. The 100 kPa value is the reaction reference. '
          r'The Kuranov pressure weights are the same for both MDEA fits. '
          f"The MDEA sensitivity stopped at the iteration limit, with replayed objective {num(receiver['C'], 6)} "
          f"and projected gradient {scientific(receiver['projected_gradient'])}.")
    rows = [[('Zheng et al., Table 4 r' + case['source']['source_row']) if case['basis'].startswith('measured') else label,
             num(case['P_Pa']/1e6, 5),
             *[model['outcome'].capitalize() for model in case['models'].values()]]
            for label, case in shared['phase_controls'].items()]
    table('supplement-shared-interaction-phase-controls',
          'MDEA phase controls for the two shared sets at a fixed 100 kPa reaction reference.',
          ['State', '$P$ (MPa)', 'Salt-anchored', 'MEA-fitted shared'],
          rows, [.25,.16,.26,.26], notes='The Zheng pressure is measured. The two higher pressures are targeted controls.')


def spread_table(q, table, head, num):
    def spread(value):
        return r'\num{' + f'{value:.3g}' + '}' if value is not None else '---'

    labels = {
        'Cai': 'Cai bubble pressure', 'Horstmann': 'Horstmann excess enthalpy',
        'Lawson-394K': 'Lawson and Garst (394 K) partial pressure',
        'Lawson-VIII': 'Lawson and Garst (50--54.5 wt%) partial pressure',
        'kundu': 'Kundu partial pressure', 'tong-baseline': r'Tong \COtwo-free bubble pressure',
        'Pappa2006': 'Pappa pure AMP vapor pressure',
        'Kuranov': 'Kuranov loaded total pressure', 'Kuranov-413K': 'Kuranov total pressure (413 K)',
        'Carson': 'Carson integral heat', 'Zheng': 'Zheng integral heat',
        'Ermatchkov': 'Ermatchkov partial pressure', 'Xiao': 'Xiao partial pressure',
        'Sedighi': 'Sedighi total pressure',
        'Merkley-half-loading': 'Merkley integral heat (half loading)',
        'Merkley-outside': 'Merkley integral heat (remaining states)',
        'corrected-Kamps': 'Corrected Kamps total pressure',
        'corrected-Kamps (27 common rows)': 'Corrected Kamps total pressure (27 rows)',
        'Arcis2011': 'Arcis integral heat', 'Kim2007': 'Kim and Svendsen absorption heat',
        'Kim2014': 'Kim et al. absorption heat', 'Vinjarapu2024': 'Vinjarapu et al. integral heat',
        'Kim2007 flagged': 'Kim and Svendsen absorption heat (flagged)',
        'Mamun2005 (outside objective)': "Ma'mun partial pressure",
        'Wagner2013': 'Wagner partial pressure',
    }
    rows = []
    for amine, record in q.items():
        rows.append(head(amine.replace('_free', ', free slope'), 6))
        for name, r in record['groups'].items():
            extreme = r['row_spreads'].get(r['max_row'], {})
            label = labels.get(name)
            if label is None:
                base = name.removesuffix(' (hot)')
                label = labels[base] + ' (hot)' if base in labels else name
            rows.append([label.replace('%', r'\%'), f"{r['common']}/{r['requested']}",
                         num(r['endpoint_AARD_percent']['A'], 3), spread(r['AARD_spread_pp']),
                         spread(extreme.get('relative_spread_percent')),
                         num(extreme.get('selected_abs_relative_deviation_percent'), 3)])
    mdea_groups = q['MDEA']['groups']
    table('supplement-endpoint-prediction-spread',
          'Measured-data deviations and prediction spread across retained endpoints at a fixed 100 kPa reaction reference.',
          ['Observation set', 'Common / requested', r'A AARD (\%)',
           'AARD spread (percentage points)', r'Max. row spread (\%)', r'A error at max. spread (\%)'],
          rows, [.37,.11,.103,.132,.116,.102], long=True, size=r'\footnotesize',
          notes=r'A is the reported endpoint. The spreads use A, B and LHS-21 for MEA, A, B and C for DEA, '
          r'A, LHS-06 and LHS-45 for AMP, and both A continuations and LHS-53 for MDEA. '
          f"MDEA Kuranov ({mdea_groups['Kuranov']['requested']}) and Carson ({mdea_groups['Carson']['requested']}) are fitted. "
          'Kuranov pressures are total pressures and Carson heats are integral. '
          r'MEA pressure rows use \COtwo partial pressure. Hot denotes $T\geq370$ K. '
          r'AARD uses the common available rows with nonzero measurements. AARD spread is the maximum minus the minimum AARD. '
          r'Row spread is $100(\max y^{\mathrm{calc}}-\min y^{\mathrm{calc}})/|y^{\mathrm{obs}}|$. '
          r'The last column is the absolute relative deviation of A on the row of maximum spread. '
          r'A dash marks an undefined comparison. The pure AMP prefit is shared.')

def transfer_displays(outputs):
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
    fit_summary = read(FIT_SUMMARY)
    phases = read(PHASE_SUMMARY)
    property_summary = read(PROPERTY_SUMMARY)
    mea_search = phases['mea_search']
    amp_outcomes = phases['amp_outcomes']
    amp_enthalpy = fit_summary['amp_enthalpy']
    mdea_draws = fit_summary['mdea_start_counts']

    ddoc, mdoc, adoc = [fixed.fits[name]['endpoint'] for name in ('DEA', 'MDEA', 'AMP_free')]
    dcost, mcost, acost, afcost = [fixed.cost(name) for name in DESIGNS[1:]]
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
    fig, ax = plt.subplots(figsize=(3.2, 2.7), constrained_layout=True)
    def mdea_water(point):
        law, = [c['temperature_law'] for pair in point['parameters']['pairs']
            if {pair['component_id_a'], pair['component_id_b']} == {'water', 'methyldiethanolamine'}
            for c in pair['coefficients']]
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
    [float(row['calc_over_obs']) for row in carbonate]
    for row in carbonate:
        new = share[row['id']]
        row.update(predicted_share=new['value'], calc_over_obs=new['value']/new['observed'])
    fig, ax = plt.subplots(figsize=(3.2, 2.7), constrained_layout=True)
    cobs, ccalc = [float(r['observed_share']) for r in carbonate], [float(r['predicted_share']) for r in carbonate]
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
    fit_rows[4][1:4] = [bold(num(r4['dea']['delta_h_J_mol'], 0)), num(r4['dea']['SE_h_J_mol'], 0), bounds(*r4['dea']['bounds']['enthalpy'], 0)]
    fit_rows[-1][1:4] = [bold(num(r4['amp']['delta_h_J_mol'], 0) + r'\textsuperscript{a}'),
                           '---', bounds(*amp_enthalpy['AMP_free']['physical_bounds_J_mol'], 0)]
    fit_rows.insert(4, level(r4['dea']))
    fit_rows.insert(len(fit_rows) - 1, level(r4['amp']))
    # fit_rows: name, value, standard error, bounds and an unused fifth cell. The main text omits the bounds; the supplement lists them.
    columns = lambda n, keep: [[r[0].replace('multicolumn{5}', 'multicolumn{' + str(n) + '}')] if len(r) == 1 else keep(r) for r in fit_rows]
    # Table 7 gives the level change of R4 at 313.15 K in a footnote to the constant term; the supplement's bounds table keeps it as a row.
    main_fit = [r for r in columns(3, lambda r: [r[0].replace('R4 constant term $A_4$', r'R4 constant term $A_4$\textsuperscript{b}'), r[1], r[2]]) if not r[0].startswith('R4 change')]
    level_note = ' and '.join(f"${r4[k]['delta_ln_K4']:+.3f}\\pm{r4[k]['SE_ln_K4']:.3f}$ for {k.upper()}" for k in ('dea', 'amp'))
    table('transfer-fitted', 'Fitted parameters of the DEA, MDEA and AMP models at a fixed 100 kPa reaction reference, with conditional standard errors.', ['Parameter','Value','Standard error'], main_fit, [.52,.20,.20],
          notes=r'Bold: fitted in this work. \textsuperscript{a}On a bound; no standard error is assigned. DEA and AMP: $\delta h$ is measured from the starting R4 correlation of Table~\ref{tab:reaction-equilibrium-constants}, and the final R4 coefficients include it (Table~\ref{supp-tab:supplement-transfer-parameters}). \textsuperscript{b}Expressed relative to the starting correlation, the fitted constant term changes $\ln K_4$ at \SI{313.15}{\kelvin} by ' + level_note + r', with the standard error of $A_4$; this change is not a further parameter. MDEA: $k_{\mathrm{MDEA,w}}$ is held at the upper bound that keeps the \COtwo-free MDEA--water solution free of a calculated liquid--liquid gap at \SI{1.466}{\mega\pascal} (Section~\ref{sec:methods-phase}), with the margin below the no-gap edge. MDEA standard errors use the pressure-weighted residual Jacobian and the residual variance of the ' + str(fixed.conditional("MDEA")["responsive"]) + r' responsive observations, with the bound held fixed. AMP: $\sigma_{\mathrm{AMPCOO^-}}$ and $\delta h$ are at their lower bounds, and the other standard errors are conditional on both. The standard errors follow Eq.~\eqref{eq:conditional-covariance}. Table~\ref{supp-tab:supplement-transfer-bounds} gives the bounds.')
    table('supplement-transfer-bounds', 'Bounds of the fitted parameters of the DEA, MDEA and AMP models.', ['Parameter','Lower bound','Upper bound'], columns(3, lambda r: [r[0].replace(r'\textsuperscript{c}', ''), *r[3][1:-1].split(', ')]), [.50,.20,.20],
          notes=r'The parameters are those of main-text Table~\ref{main-tab:transfer-fitted}. For DEA and AMP the bounds of $\delta h$ and of $\Delta\ln K_4$ are measured from the starting R4 correlations, like the values of that table.')
    apure, ROLE = read(AM344 + 'pure-binary-on-05e94210.json')['pure'], {'fitted': 'fitted', 'assessment_not_fitted': 'not fitted'}
    data_rows.append(head('AMP, pure component', 11))
    for key, who in [('Klepacova2011', r"Klep\'a\v{c}ov\'a et al.\ \cite{klepacovaVaporPressuresSeveral2011}"), ('Belabbaci2010', r'Belabbaci et al.\ \cite{belabbaciInvestigationIsothermalVapour2010}'), ('Pappa2006', r'Pappa et al.\ \cite{pappaMeasurementThermodynamicModeling2006}'), ('Ayad2023', r'Ayad et al.\ \cite{ayadMeasurementsModelingThermodynamic2023}')]:
        g, t = apure['groups'][key], [r['T_K'] for r in apure['rows'] if r['campaign'] == key]
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
          notes=r'The last column gives the original salt-anchored fit on the same observations. Paired values are calculated on the common rows with defined relative errors (reported fit first and the paired count in parentheses). $N$: number of observations; in parentheses, the number with a calculated value and a defined relative deviation. Amine content: that of the unloaded solution, or a mole fraction for the \COtwo-free binary sets ($x_{\mathrm{w}}$: water; $x_{\mathrm{A}}$: amine). R4 and R5: in, out or mixed relative to the source temperature range of that equilibrium constant, which for the AMP R4 is a range of model-derived estimates (main-text Table~\ref{main-tab:reaction-equilibrium-constants} and Section~\ref{main-sec:data-roles}); ---: not reported in the source, or the calculation uses no such reaction. AARD and bias follow main-text Eq.~(\ref{main-eq:aard}). Tables~\ref{tab:supplement-dea-ranges}--\ref{tab:supplement-amp-ranges} give the deviations inside and outside each range, and Section~\ref{sec:s-corrections} gives the source conventions. \textsuperscript{a}Mole fraction of added \COtwo. DEA: the water--DEA interaction was fitted beforehand to the 365.15 K vapor--liquid equilibria of Horstmann et al.\ \cite{horstmannPhaseEquilibriumExcess2002}, which are not listed; the ' + str(sum(r["role"] == "fitted" and r["unit"] == "Pa" for r in data)) + r' fitted partial pressures include Lawson and Garst, Seo and Hong, and Lal et al. MDEA: the Xiao et al.\ and Ermatchkov et al.\ pressures were used to choose the initial MDEA parameter set but are not in the objective. Pure component: deviations at the fixed pure-AMP parameters, whose fit preceded the reactive fit; \textsuperscript{b}the errors of the ' + NUMBER_WORDS[apure["groups"]["Ayad2023"]["n"]] + r' fitted densities are ' + ', '.join(num(e, 3) for e in apure['groups']['Ayad2023']['errors_kg_m3']) + r' kg/m$^3$.')
    AMINES = [('DEA', dflat, 'diethanolamine'), ('MDEA', flatten(mdoc, {'methyldiethanolamine', 'protonated-methyldiethanolamine'}), 'methyldiethanolamine'), ('AMP', flatten(adoc, {'aminomethylpropanol', 'protonated-aminomethylpropanol', 'carbamate-anion'}), 'aminomethylpropanol')]
    # Values fitted in this work, by key of each retained record: the reactive fit of each amine (checked against its fit record) and the fits made beforehand:
    # the permittivity coefficients (Hsieh et al.), the water--DEA interaction (Horstmann et al.) and the five pure-AMP parameters.
    MKEYS = ['methyldiethanolamine/water/k_ij', 'methyldiethanolamine/water/k_ij_temperature_slope', 'carbon-dioxide/protonated-methyldiethanolamine/k_ij', 'protonated-methyldiethanolamine/water/k_ij',
             'protonated-methyldiethanolamine/water/k_ij_reciprocal_temperature_slope', 'bicarbonate-anion/protonated-methyldiethanolamine/k_ij', 'protonated-methyldiethanolamine/segment_diameter', 'protonated-methyldiethanolamine/dispersion_energy_over_k']
    AKEYS = ['aminomethylpropanol/water/k_ij', 'aminomethylpropanol/water/k_ij_reciprocal_temperature_slope', 'protonated-aminomethylpropanol/water/k_ij', 'protonated-aminomethylpropanol/water/k_ij_reciprocal_temperature_slope',
             'carbon-dioxide/protonated-aminomethylpropanol/k_ij', 'protonated-aminomethylpropanol/segment_diameter', 'carbamate-anion/segment_diameter', 'carbamate-hydrolysis/a']
    APURE = dict(zip(['aminomethylpropanol/segment_count', 'aminomethylpropanol/segment_diameter', 'aminomethylpropanol/dispersion_energy_over_k', 'association/aminomethylpropanol/a/aminomethylpropanol/b/energy_over_k', 'association/aminomethylpropanol/a/aminomethylpropanol/b/volume'], ['m', 'sigma', 'epsilon', 'eps_ab', 'kappa']))
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
    # Hydroxide Born diameter from the Born equation: hydration free energy -106.4 kcal/mol, water permittivity 78.37 at 298.15 K.
    born_oh = 6.02214076e23 * 1.602176634e-19 ** 2 * (1 - 1 / 78.37) / (4 * math.pi * 8.8541878128e-12 * 106.4 * 4184) * 1e10
    {r['identity']: float(r['value']) for r in read(MEA + 'paper-evidence-341/shared-coefficients.csv') if r['identity'].endswith('born_diameter')}
    # Sensitivity of the MEA fit to the two Born diameters set at 3.0 A (supplement): the tested diameters, the largest objective change and the largest shifts of fitted CO2 partial pressures.
    born = read(MEA + 'born-diameter-sensitivity-405/summary.json')
    lambda ion: max(abs(r['change_percent']) for c in born['cases'][1:] if c['ion'] == ion for r in c['largest_relative_changes'] if r['quantity'] == 'partial_pressure')
    born_cost = f"at most {100 * max(abs(c['cost_change']) for c in [*born['cases'], born['bicarbonate_interior']]) / born['reference_cost']:.2f}"
    [born_cost, f"{dflat['carbamate-anion/dispersion_energy_over_k'][0]:.4f}", f"{f2['component/carbamate-anion/segment_diameter']:.4f}", f'{size_ratio:.4f}', f'{born_oh:.4f}', '$-106.4$ kcal/mol', '78.37']
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
    _dsum, _msum = read(BASE + 'paper-summary.json'), read(MD + 'summary-row.json')
    mstability = read(MD + 'stability.json')
    aconf, _asearchrows = read(AMM + 'confirmation.json'), read(AMM + 'search-1.json.gz')
    _msearch, _asearch = mstability['grid'], aconf['full_search']
    # The free fit (selected start 1) is the comparison whose splits the paper names; its classification and search.
    _afreesearch, aclass = next(f for f in afree['fits'] if f['start'] == 1)['search']['grid'], read(AMF + 'phase-classification-1.json.gz')
    cell = lambda s: num(s['AARD_percent'],2) + ' (' + str(s['rows']) + ')'
    escore = {r['group']: (r['deviations'][1], r['n'][1]) for r in read(MEA + 'paper-evidence-341/same-data-comparison/part1-scores.json')}
    [r for r in read(MEA + 'reduced-refit/parameter-details.csv') if r['fit'] == 'F2']
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
    enot = ([eprops[r['target']] for r in mea_pressure if r['target'] not in fitted_pressure] + wagner
            + [r for r in mea_off if r['group'] == 'Aronu2011'])
    dloaded = {'Lawson', 'Lawson-394K', 'SeoHong', 'Lal', 'Lawson-VIII'}
    doutside = [r for r in data if r['group'] in dloaded and r['role'] == 'not fitted']
    dfitted = scores([r for r in data if r['role'] == 'fitted' and r['unit'] == 'Pa'], dloaded)
    ephase = [phases['mea_grid'][key] for key in ('grid', 'offset', 'census')]
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
    mcomp = read(MD + 'comparison.json')
    mcomp['runs'][mcomp['chosen']]
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
    table('supplement-amp-expanded', f'AMP fits to the extended data, {len(fixed.fits["AMP_free"]["replay"]["rows"])} observations, with the temperature slope of the \\ce{{AMPH+}}--water interaction fitted or fixed.', ['Fit', 'Objective', 'Loaded total pressures, AARD (\\%) ($N$)', 'Instabilities, search trials', 'Instabilities, supplied trials'],
          amp_sensitivity, [.34,.11,.21,.13,.13],
          notes=r'Instabilities: states with a detected instability of the number searched, with the trial phases of the search alone and with the supplied trial compositions added. Both pairs have the salt-anchored shared set and the same weights. The splits of main-text Fig.~\ref{main-fig:amp-splits} belong to the fit to the first data, with the MEA-fitted shared set.')
    target = LATEX / 'tables/supplement-amp-ranges.tex'
    outputs[target] += outputs.pop(LATEX / 'tables/supplement-amp-expanded.tex')
    fixedp = read('analyses/mdea_mea_workflow/results/phase-search-421/fixed-pressure.json')
    next(q for q in fixedp['attempts'] if q['confirmed'])
    fwt = 100 * mmass['methyldiethanolamine'] * fixedp['feed']['methyldiethanolamine'] / (mmass['methyldiethanolamine'] * fixedp['feed']['methyldiethanolamine'] + mmass['water'] * fixedp['feed']['water'])
    rf"\SI{{{fixedp['T_K']:.2f}}}{{\kelvin}}, {fwt:.2f} wt\% MDEA, {fixedp['feed']['carbon-dioxide'] / fixedp['feed']['methyldiethanolamine']:.3f} mol/mol and \SI{{{fixedp['P_Pa'] / 1e6:.3f}}}{{\mega\pascal}}"
    new_fixed = read(MDEA + 'fixed-pressure.json.gz')
    common = read(AMP + '../common-pressure.json')
    amp_bubbles = [fixed.endpoint_record(f'display-replays/AMP_{family}-bubble.json.gz', f'AMP_{family}')
                   for family in ('free', 'fixed')]
    amp_replay = read(REPLAYS + 'amp-common-pressure.json.gz')


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
              phases['amp_worked']['AMP_' + case]]
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
    for convention, outcome in reference.items():
        trial = outcome['attempts'][0]
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
                             num(property_summary['mdea']['objectives'][weight], 2),
                             scores(mrows, {'Kuranov'})])
    kuranov_count = sum(row['group'] == 'Kuranov' and row['role'] == 'fitted' for row in mrows)
    table('supplement-mdea-weighting', 'MDEA objectives on the same fitted observations and loaded total-pressure deviations.',
          ['Fit', 'Objective weights', '$N$', 'Objective', r'Loaded pressure AARD (\%) ($N$)'],
          mcomparisons, [.22,.20,.08,.15,.25],
          notes=f'Compare objectives within the same weighting. Tracking rows use the historical reaction references. The pressure deviation uses the {kuranov_count} fitted Kuranov total pressures.')

    dea_prior = read(DEA_SALT_SUMMARY)
    methane = fixed.endpoint_record('display-replays/dea-methane.json.gz', 'DEA')['rows']
    methane_shifts = [abs(v)/1e6 for q in methane for v in q.get('pCO2_change_Pa', [])]
    horstmann = [r for r in data if r['group'] == 'Horstmann' and r['observed'] < 0]
    horstmann_positive = sum(r['value'] > 0 for r in horstmann if r['status'] == 'Available')
    expanded_groups = dea_prior['expanded_groups']
    pressures = sum(expanded_groups[group] for group in ('Lawson', 'SeoHong', 'Lal'))
    heats = expanded_groups['Carson']
    table('supplement-dea-expanded', 'Broadened DEA objective and diagnostics of the reported fit.',
          ['Quantity', 'Original salt fit', 'Broadened fit, 100 kPa'], [
              [f'Common {pressures + heats}-row objective', num(dea_prior['expanded_objective'], 2), num(dcost, 2)],
              [r'Seo and Hong partial-pressure AARD (\%)', num(dea_prior['seohong_aard_percent'], 2), num(dev['SeoHong']['AARD_percent'], 2)],
              ['Horstmann excess enthalpies with the wrong sign',
               f"{dea_prior['horstmann_positive']} of {dea_prior['horstmann_negative_observations']}",
               f"{horstmann_positive} of {len(horstmann)}"],
              ['Maximum conditional methane shift (MPa)',
               num(dea_prior['methane_maximum_shift_pa']/1e6, 3),
               num(max(methane_shifts, default=None), 3)]
          ], [.52,.21,.21], notes=f'The common objective has {pressures} partial pressures and {heats} integral heats. The methane shift holds the methane-free liquid composition fixed. The measurements do not bound the effects of dissolved methane.')

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
        elif source_id == 'Merkley1987':
            locator = 'Merkley, Fig.~3'
            source_pressure = r'/\allowbreak '.join(f"{float(source[k])/1000:.3f}" for k in
                                       ('candidate_pressure_1_kPa', 'candidate_pressure_2_kPa'))
        else:
            locator = f"{source_id[:-4]}, T{source['source_locator'].split('Table ')[1].split()[0].rstrip(',')}, r{source['source_row']}"
            source_pressure = num(source['pressure_MPa'])
        pressure_record = next(q for q in phases['mdea_distinct_states'] if q['key'] == key)
        bubble = property_summary['mdea_bubble'].get(key)
        bubble_cell = '---'
        if bubble:
            bubble_cell = (num(bubble['bubble_Pa']/1e6, 5) if bubble['status'] == 'Available'
                           else 'Refused' + r'\textsuperscript{a}')
            if bubble['status'] == 'Refused':
                refusal = re.match(r'infeasible: residual (\S+) against EQUILIBRIUM_ROW_RESIDUAL (\S+)',
                                   bubble['diagnostic'])
                residual, tolerance = map(float, refusal.groups())
        phase_rows.append([key.replace(':', r':\allowbreak '), locator, num(state['temperature_K'], 2),
                           num(feed_wt(mdoc, feed, 'methyldiethanolamine'), 2),
                           num(feed['carbon-dioxide']/feed['methyldiethanolamine']),
                           source_pressure, num(state['pressure_Pa']/1e6) + r'\newline ' + pressure_record['pressure_basis'], bubble_cell,
                           state['native_branch'], state['supplied_branch'],
                           'None confirmed' if state['attempts'] else 'Not attempted'])
    table('supplement-mdea-phase-outcomes', 'Outcomes at the descent states of the provisional MDEA endpoint.',
          ['State', 'Source', '$T$ (K)', r'MDEA (wt\%)', r'$\alpha$', r'Source $P$ (MPa)',
           r'Search $P$ (MPa)', r'$P_{\rm bub}$ (MPa)', 'Native', 'Supplied', 'Two-liquid outcome'],
          phase_rows, [.102,.113,.064,.061,.051,.073,.077,.086,.071,.092,.082], long=True, size=r'\footnotesize',
          notes=f"{mnew['tally']['available']} of {mnew['tally']['states']} searches completed; "
                f"{mnew['tally']['descent']} detections at {len(phase_rows)} distinct states and no confirmed splits. "
                r"$\alpha$ is in mol \COtwo/mol MDEA and wt\% excludes \COtwo. T and r identify the source table "
                r"and row. B\"ottinger cell pressures are assignments. Merkley Fig.~3 gives the digitized traces; "
                r"the two possible pressures in Table~1 are shown, with the higher one used for the searches. "
                r"The two separate high-pressure controls are unresolved. The bubble-pressure column covers measured-pressure descents. "
                r"\textsuperscript{a}The bubble solve returned infeasible with scaled residual "
                + num(residual, 5) + " against " + reduced_gibbs(tolerance) + ".")

    amp_designs = ('AMP_free', 'AMP_fixed')
    amp_controls = {}
    amp_screen = {}
    for design in amp_designs:
        selected = fixed.fits[design]['start']
        amp_controls[design] = fixed.endpoint_record(f'{design}/controls/{selected}.json.gz', design)['rows']
        amp_screen[design] = {q['key']: q for q in fixed.coverage(design, 'native')['rows']}
    measured = sorted(amp_controls['AMP_free'].keys() - {'worked-state'})
    amp_rows = []
    for key in measured:
        free, held = (amp_controls[d][key]['value'] for d in amp_designs)
        feed = dict(zip(free['species'], free['feed_mol'], strict=True))

        fits = []
        for design, control in zip(amp_designs, (free, held), strict=True):
            outcome = 'No descent' if control['search']['no_descent_in_trial_set'] else 'Unresolved'
            expected = 'finite search, no resolved descent' if outcome == 'No descent' else 'unresolved phase identity'
            trial = control['minimum_trial']['seed'].replace('positive-neutral-base', 'neutral base')
            parent, parent_error = control['parent_gibbs_RT_mol']
            candidate = next((q for q in control.get('candidates', []) if q['support'] == 'L+V'), {})
            delta = candidate.get('Gibbs_over_RT_mol')
            flag = r'\textsuperscript{a}' if delta is not None and not candidate['qualified'] else ''
            if design == 'AMP_free':
                outcome = amp_outcomes[key]['outcome'].replace('; ', r'\newline ')
            fits.append([num(amp_screen[design][key]['pressure_Pa']/1e6, 5), trial,
                         reduced_gibbs(delta - parent) + flag if delta is not None else '---',
                         reduced_gibbs(parent_error + candidate['error']) if delta is not None else '---', outcome])
        source, _, _ = key.split(':')
        row = amp_outcomes[key]['source']['row']
        amp_rows.append([source.split('-')[0].capitalize() + ' r' + row, num(free['T_K'], 2),
                         num(feed_wt(adoc, feed, 'aminomethylpropanol'), 2) + r'\newline ' +
                         num(feed['carbon-dioxide']/feed['aminomethylpropanol']),
                         num(free['P_Pa']/1e6, 5),
                         *[r'\newline '.join(pair) for pair in zip(*fits, strict=True)]])
    table('supplement-fixed-reference-controls', NUMBER_WORDS[len(amp_outcomes)].capitalize() +
          ' AMP controls at the measured absolute pressures. '
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
    for group, match in property_summary['mdea']['paired'].items():
        matched.append([group, match['n'], *[num(model[metric], 2)
                        for model in match['models'] for metric in ('AARD_percent', 'bias_percent')]])
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

    fixed.load('salt.json.gz')
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
    rows += [['MEA', '', '', eold(MEA_TRACKING_FITTED_PRESSURES), eold(MEA_TRACKING_FITTED_PRESSURES), eold(MEA_TRACKING_ADDITIONAL_PRESSURES, 'Wagner pressures', 'Aronu 15 wt% pressures', 'Aronu 45 wt% pressures'),
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
            coverage = phases['coverage'][row[0]]
        if row[0] in ('MEA', 'DEA'): row[5] = r'$p_{\COtwo}$: ' + row[5]  # every MEA and DEA pressure not fitted is a CO2 partial pressure (Tables 5 and S8)
    for row, label in zip(rows[4:], ('MEA-fitted shared set', '30-pressure Lawson--Garst fit',
                                     'fit with MEA weights', 'earlier carbamate inputs'), strict=True):
        row[:3] = [r'\multicolumn{3}{@{}p{.24\linewidth}}{' + row[0] + ', ' + label + '}']
    rows.insert(4, head('Comparison fits', 9))
    table('amine-summary', 'The four fixed-reference models and their comparison fits with system-pressure references.', ['Model','Fitted parameters','On bounds',r'Fitted loaded-solution pressures\textsuperscript{a}',r'All fitted pressures\textsuperscript{b}',r'Pressures not fitted\textsuperscript{c}','Attempted searches','Completed searches',r'Liquid--liquid splits found\textsuperscript{d}'], rows, [.09,.08,.06,.14,.10,.15,.08,.10,.105],
          notes=r'Pressure columns: AARD (Eq.~\eqref{eq:aard}) in \%, with the number of observations $N$ in parentheses. \textsuperscript{a}Fitted \COtwo partial pressures ($p_{\COtwo}$) of loaded MEA and DEA and fitted total pressures ($P$) of loaded MDEA and AMP. \textsuperscript{b}Column a with the fitted \COtwo-free bubble pressures of MDEA--water and AMP--water; neither column includes the fitted \COtwo--water pressures of Kiepe et al.\ in the MEA objective (Table~\ref{tab:mea-data}). \textsuperscript{c}MEA: all pressures not fitted, those at nominal 30 wt\% of the six sources of Table~\ref{tab:mea-data}, those of Wagner et al.\ and those at 15 and 45 wt\%; MDEA and AMP: total pressures and \COtwo partial pressures separately, the AMP total pressures including the 5 \COtwo-free bubble pressures of Tong et al. The receiver comparisons use the original salt-anchored fits. \textsuperscript{d}In the searches of each fit, which are finite and differ in design between the amines (Section~\ref{supp-sec:s-phase}), so the counts do not measure equal coverage and split counts are lower bounds. '
                'The MDEA endpoint is provisional. '
                f"The MEA liquid grid completed {mea_search['liquid_grid']['completed']:,} of {mea_search['liquid_grid']['attempted']:,} searches. "
                f"The {mea_search['census']['attempted']} L--V census cases returned "
                f"{mea_search['census']['outcomes']['passed-two-phase']} passed two-phase parents and "
                f"{mea_search['census']['outcomes']['passed-single-liquid']} passed single-liquid parents. "
                f"The separate MEA measured-state search completed {mea_search['measured']['completed']} of "
                f"{mea_search['measured']['attempted']} attempts.")
    P341 = MEAEVIDENCE
    mea_fit = read(P341 + 'fitted-rows.csv')
    cai_T = [float(r['observed']) for r in mea_fit if r['group'] == 'Cai' and r['quantity'] == 'temperature']
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
    table('calibration-data', 'Data in the objective of each model, data fitted beforehand and data outside the objective that informed a choice.', ['Observable', 'Source', '$N$', '$T$ (K)', 'Role'], design, [.36, .16, .07, .19, .18],
          notes=r'Fitted: in the objective of the reported fit, ' + ', '.join(f'{n} observations for {k}' for k, n in objective_n.items()) + r'. Fitted beforehand: used to set a parameter that the reactive fit holds fixed. \textsuperscript{a}Development: outside the objective, but used to choose the parameters or the initial parameter set (Section~\ref{sec:data-roles}). \textsuperscript{b}The Kiepe pressures give a constant contribution to the reactive objective. $p_{\COtwo}$: \COtwo partial pressure; total pressure: bubble pressure of the loaded solution. Table~\ref{tab:mea-data} and Table~\ref{supp-tab:supplement-transfer-data} give the compositions, loadings and deviations of every set, including those that are neither fitted nor used for a choice.')
    # Carbonate share of Jakobsen et al. under the tested electrostatic and shared-ion changes (#423).
    (electrostatics,) = (key for key in stage_records if '/shared-ion-electrostatics-423/' in key and key.endswith('/arm-replay-costs.json'))
    C423 = electrostatics.removesuffix('arm-replay-costs.json')
    CCASES = [('P0', 'Fit with the MEA-fitted shared set'), ('bicarbonate-anion-2.5', r'Bicarbonate Born diameter \SI{2.5}{\angstrom}'), ('bicarbonate-anion-3.5', r'Bicarbonate Born diameter \SI{3.5}{\angstrom}'), ('bicarbonate-anion-4', r'Bicarbonate Born diameter \SI{4.0}{\angstrom}'),
              ('carbonate-anion-2.5', r'Carbonate Born diameter \SI{2.5}{\angstrom}'), ('carbonate-anion-4', r'Carbonate Born diameter \SI{4.0}{\angstrom}'), ('carbonate-anion-4.953', r'Carbonate Born diameter \SI{4.953}{\angstrom}'),
              ('permittivity--5pct', r'Permittivity lowered by 5\,\%'), ('permittivity-+5pct', r'Permittivity raised by 5\,\%'), ('P1', 'Second pair of MEA permittivity coefficients'), ('M1', r'Solvation factor of \COtwo 1.5'), ('M3', 'Solvation factor of MEA 1.5'),
              ('P1-refit', 'Second permittivity pair, refitted'), ('M3-refit', 'Solvation factor of MEA 1.5, refitted')]
    cshare = {k: read(C423 + k + '/carbonate-share.json') for k, _ in CCASES}
    _carm, _crefit = read(C423 + 'arm-replay-costs.json')['arms'], read(C423 + 'refit-comparison.json')['arms']
    cgm = {k: v['summary']['all']['geometric_mean'] for k, v in cshare.items()}
    ratios = [float(r['calc_over_obs']) for r in carbonate]
    adopted_carbonate = dict(geometric_mean=math.exp(math.fsum(map(math.log, ratios))/len(ratios)),
                             aard_percent=100 * math.fsum(abs(r-1) for r in ratios)/len(ratios))
    table('supplement-carbonate-sensitivity', r'Carbonate share of dissolved carbon at the ten states of Jakobsen et al.\ \cite{Jakobsen2005} for the MEA model and for the changes tested.', ['Case', 'Geometric mean of calculated/observed', r'AARD (\%)'],
          [['MEA model', f"${adopted_carbonate['geometric_mean']:.4f}$", num(adopted_carbonate['aard_percent'], 2)]] + [[label, f'${cgm[k]:.4f}$', num(cshare[k]['summary']['all']['aard_percent'], 2)] for k, label in CCASES], [.52, .26, .14],
          notes=r'The shares are not fitted in any case. Every change below the second row is made to the fit with the MEA-fitted shared set. The last two rows refit the other MEA parameters; every other change is made with all other parameters fixed. The Born diameters of bicarbonate and carbonate are \SI{3.0}{\angstrom} in the MEA model.')
    [float(r['calc_over_obs']) for r in cshare['P0']['rows']]
    # Volume-equivalent Born diameters of the chain cations: retained replays at fixed other parameters (#423).
    def born_replay(amine, group):
        out = []
        for case in ('control', 'volume-equivalent'):
            rs = [r for r in read(C423 + amine + '/' + case + '/data-rows.json.gz') if r['group'] == group and r.get('status', 'Available') == 'Available']
            out.append(100 * sum(abs(r['value'] / r['observed'] - 1) for r in rs) / len(rs))
        return out
    _bdea, _bmdea = born_replay('diethanolamine', 'Lawson'), born_replay('methyldiethanolamine', 'Kuranov')
    lambda record, s: record[s + '/segment_diameter'][0] * record[s + '/segment_count'][0] ** (1 / 3)
    # Published models on identical observations only, each with the role of those observations in that model's fit.
    PUB = {'Baygi2015 PC-SAFT': r'Baygi and Pahlavanzadeh, PC-SAFT \cite{Baygi2015}', 'Najafloo2018 SAFT-HR': r'Najafloo and Zarei, SAFT-HR \cite{Najafloo2018}', 'Zhang2011 eNRTL': r'Zhang et al., eNRTL \cite{Zhang2011}'}
    SHARED = {'Ermatchkov': r'\COtwo partial pressures of Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}, MDEA', 'corrected-Kamps': r"total pressures of P\'erez-Salado Kamps et al.\ at the temperatures corrected by Ermatchkov et al.\ \cite{ermatchkovSolubilityCarbonDioxide2006}, MDEA"}
    exact = [r for r in read(MEA + 'paper-evidence-341/same-data-comparison/published-deviations.json') if r['comparison'].startswith('exact:')]
    own = lambda path: num(read(MEA + path)['pressure_aard_percent'], 2)
    mamun_count = mea_replay['summary']['pressure']['Mamun2005']['attempted']
    rows = [head(rf"{mamun_count} \COtwo partial pressures of Ma'mun et al.\ \cite{{Mamun2005}}, MEA near 393 K", 3)] + [[PUB[r['model']], (r'unclear\textsuperscript{a}' if 'role_note' in r else r['data_role']), f"${r['deviation_percent']:g}$"] for r in exact]
    rows += [['This work, 16-parameter calibration', 'not fitted', own('same-data-comparison/matched-score.json')], ['This work, MEA-fitted shared set', 'not fitted', own('paper-evidence-341/same-data-comparison/matched-score.json')]]
    read(SALT + 'MEA/baygi-matched-pressure.json')['aard_percent']
    # The archived prior_F2 column was read from the 16-parameter matched-pressure table.
    rows.append(['This work, MEA model', 'not fitted', num(property_summary['mea_mamun'], 2)])
    mpub = read(MD + 'published-pressure-comparisons.json')['comparisons']
    ZHANG_CHEN = r'Zhang and Chen, eNRTL \cite{zhangThermodynamicModelingCO22011}'  # their Table 14: AARD 6.8 % on the 82 Kuranov total pressures and 17.7 % on the 101 Ermatchkov CO2 partial pressures, both in their regression
    literature = read(ROUND8 + 'literature-populations.json.gz')['quantities']
    for c in mpub:
        if c['group'] == 'corrected-Kamps':
            kamps = literature['kamps']
            common = kamps['salt/refit']['common_keys']
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
            r9_kamps = property_summary['kamps']
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
    collections.Counter(r['role'] for r in mrows if r['group'] in ('Kuranov', 'Kuranov-binary'))
    k82 = read(MDEA + '../kuranov-matched-pressure.json.gz')['grouped']['K82']['salt_anchored']
    kuranov = literature['kuranov']
    k82_adopted = property_summary['mdea']['kuranov']
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
            measured = read(HONG + block + '.csv')
            ids = {q['record_id'] for q in measured if q['three_model_eligible'] == 'True'
                   and (subset != 'strict grid' or q['inside_hong_grid'] == 'True')}
            if block in hong_pressures:
                predictions = eprops | {q['identity']: q for q in wagner}
                cohort = [predictions[key] for key in ids]
                adopted = deviations(cohort)['AARD_percent']
            elif block.startswith('Kim'):
                predictions = {r['record_id']: r for r in compare_mea['kim_2007']}
                cohort = [predictions[key] for key in ids]
                good = [q for q in cohort if q['interval_status'] == 'available']
                adopted = math.sqrt(math.fsum((float(q['predicted'])-float(q['observed']))**2 for q in good)/len(good))
            else:
                predictions = {r['identity']: r for r in compare_mea['density']}
                cohort = [predictions[key] for key in ids]
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
    fitted_T = [float(r['row']['T_K']) for r in arows if r['group'] == 'loaded-pressure']  # the loaded pressures of the first data, the fit that has the splits
    fig, ax = plt.subplots(figsize=(4.6, 3.5), constrained_layout=True)
    ax.axhspan(min(fitted_T), max(fitted_T), color='0.87', lw=0, label='Loaded-solution pressures fitted by the first fit')
    ax.axhline(read('analyses/amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json')['reaction_ranges_K']['AMP-dissociation'][1], color='k', ls=(0, (5, 2)), lw=1.3, zorder=4, label='Upper limit of the measured R5 range')
    mstates = [r for r in arows if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'tong')]
    ax.scatter([amp_loading(r) for r in mstates], [float(r['T_K']) for r in mstates], s=14, marker='+', color='0.45', linewidths=.7, zorder=2, label='Measured total-pressure states (Hartono, Tong)')
    for rs, label, style in [([r for r in states if r not in split], 'Instability, split not confirmed', dict(s=46, facecolors='none', edgecolors=colors[0], linewidths=0.9)), (split, 'Confirmed liquid--liquid split', dict(s=9, color=colors[1]))]:
        ax.scatter([float(r['loading_mol_CO2_per_mol_AMP']) for r in rs], [float(r['T_K']) for r in rs], label=label, **style)
    amp_measured_splits = read(ROUND8 + 'amp-six-states.json.gz')['quantities']['rows']
    {s['key'] for s, point in zip(aclass['states'], states, strict=True) if point['split']}
    ax.scatter([r['crosswalk']['loading_mol_CO2_per_mol_AMP'] for r in amp_measured_splits],
               [r['crosswalk']['T_K'] for r in amp_measured_splits],
               s=28, marker='D', facecolors=colors[1], edgecolors='black', linewidths=.7, zorder=5,
               label='Confirmed split at a measured state')
    ax.set(xlabel='Loading (mol CO$_2$/mol AMP)', ylabel='Temperature (K)', xlim=(0, 1.02), ylim=(308, 398))
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.18), frameon=False, ncol=1, handletextpad=.5)
    figure(fig, 'amp-splits.pdf')
    reported_costs = [fixed.cost(name) for name in DESIGNS]
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
    {r['group']: r['weight'] for r in weighted_rows}
    scale_rows = [
        ['DEA', r'\COtwo partial pressures', '0.09', f"average over {pressures} pressures"],
        ['', 'Integral absorption heats', r'$0.02\,|y_j^{\mathrm{obs}}|$', 'average over 50 heats'],
        ['MDEA', 'Loaded total pressures of Kuranov et al.', '0.015', f'$1/{kuranov_count}$'],
    ]
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
        scale_rows.append(['', label, scale, f'$1/{n}$'])
    scale_rows += [
        ['AMP', 'Loaded total pressures', '0.015',
         f"average over {sum(row['role'] == 'fitted' and row['group'] in amp_loaded for row in arows)} pressures"],
        ['', 'Binary bubble pressures', '0.05', 'average over 52 binary observations'],
        ['', 'Vapor AMP mole fractions', r'$\max(10^{-4},0.05\,y_j^{\mathrm{obs}})$', 'average over 52 binary observations'],
        ['', 'Carbamate fractions', '0.003', 'average over 57 fractions'],
    ]
    table('supplement-transfer-scales', 'Residual scales and weights of the fitted DEA, MDEA and AMP data sets.',
          ['Amine','Data set',r'Scale $s_j$',r'Weight $w_j$'], scale_rows, [.08,.32,.27,.27],
          notes=r'Pressure residuals are logarithmic, with dimensionless scales. $\rho_j$ is the measured density and $g_j$ the local secant slope against loading. For MDEA the weights average each observation group. The extra factor $0.015^{-2}$ in the retained Kuranov weight is written in the scale column.')
    scales_path = LATEX / 'tables/supplement-transfer-scales.tex'
    outputs[scales_path] = outputs[scales_path].replace('tab:supplement-transfer-scales', 'tab:transfer-scales')

    # Distances are in optimizer-bound coordinates.
    start_rows = []
    vector_rows = []
    for design, attempts in fit_summary['attempts'].items():
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
        distances = fit_summary['start_distances'][design]
        for start, attempt in attempts.items():
            near = [value for pair, value in distances.items() if start in pair.split('/')]
            bound_ids = [r['identity'] for r in fixed.fits[design]['endpoint']['coordinates']]
            bound = attempt['active_bounds'] or {}
            active = ', '.join(f"{bound_ids.index(k)+1} {v}" for k, v in bound.items())
            selected = fixed.selections[design]['selected'] == start
            status = ('Provisional' if design == 'MDEA' else 'Selected') if selected else attempt['status'].replace('_', ' ')
            gradient = attempt['solver_scale_projected_gradient_inf']
            vector = vectors['A' if start == 'A-loose' else start]
            fixed.load(f'{design}/{start}.json.gz')
            anchor = f"start-{design.replace('_', '-')}-{start}"
            physical = vector['vector'].copy()
            if design in amp_enthalpy:
                conversion = amp_enthalpy[design]
                physical[conversion['coordinate_index']] += conversion['offset_J_mol']
            vector_rows.append([rf'\hypertarget{{{anchor}}}{{{start}}}',
                                ', '.join(rf'\num{{{q:.9g}}}' for q in physical)])
            endpoint = fit_summary['endpoint_stages'][design][start][-1]
            stop = endpoint['termination'].split(' tolerance', 1)[0]
            if stop in ('Function', 'Parameter'):
                status += r'\newline ' + stop + ' tolerance'
            start_rows.append([design_label, rf'\hyperlink{{{anchor}}}{{{start}}}',  num(min(near) if near else (0 if start == 'A-loose' else None)),
                               num(attempt['initial_cost']), num(attempt['objective'], 6),
                               reduced_gibbs(gradient) if gradient is not None else '---', active or '---', status])
    pressure_groups = property_summary['mdea']['paired']
    table('supplement-fit-starts', 'Starts and endpoints of the fits at the fixed 100 kPa reaction reference.',
          ['Fit', 'Start', 'Nearest RMS', 'Initial $C$', 'Endpoint $C$', 'Projected gradient', 'Active bounds', 'Outcome'],
          start_rows, [.115,.085,.085,.102,.12,.12,.15,.125], long=True, size=r'\footnotesize',
          notes=r'RMS distance is measured relative to coordinate bounds. A-loose repeats A. Active bounds are numbered in fit coordinate order. '
                r'The projected gradient uses the optimizer scale. The endpoints missed the projected-gradient limit of $10^{-8}$. '
                f"MDEA had {NUMBER_WORDS[len(mdea_draws['evaluable'])]} evaluable draw of {mdea_draws['drawn']}, "
                f"in addition to inherited start {', '.join(mdea_draws['inherited'])}. "
                f"Draw {', '.join(map(str, mdea_draws['untested_draws']))} missed the start-separation rule. "
                + 'Start A gives ' + num(mdea_draws['A_AARD_percent']['Kuranov'], 2)
                + rf"\% on {pressure_groups['Kuranov']['n']} loaded Kuranov pressures and "
                + num(mdea_draws['A_AARD_percent']['Ermatchkov'], 2)
                + rf"\% on {pressure_groups['Ermatchkov']['n']} Ermatchkov partial pressures. " +
                f"AMP with fixed slope retains a second basin at {fixed.selections['AMP_fixed']['attempts']['C']['cost']:.2f}. "
                'A dash marks an unavailable value or an empty active set.')

    vector_caption = ('Initial vectors in physical fit coordinates. AMP enthalpy entry '
                      f"{amp_enthalpy['AMP_free']['coordinate_index'] + 1} is the signed increment in J/mol.")
    table('supplement-start-vectors', vector_caption,
          ['Start', 'Coordinates in fit order'], vector_rows, [.13,.85], long=True, size=r'\footnotesize')
    vectors_path = LATEX / 'tables/supplement-start-vectors.tex'
    # LTcaptype is local to this group and keeps the unnumbered vectors out of the table sequence.
    outputs[vectors_path] = outputs[vectors_path].replace(r'\begingroup', r'\begingroup\def\LTcaptype{}', 1).replace(
        rf'\caption{{{vector_caption}}}\label{{tab:supplement-start-vectors}}',
        rf'\multicolumn{{2}}{{@{{}}l}}{{{vector_caption}}}')

    c1 = []
    c1_declarations = {}
    for design in DESIGNS[:-1]:
        for mode, point in (
            ('fixed-at-old', fixed.load(f'{design}/manifest.json.gz')['prior_declaration']),
            ('selected', fixed.fits[design]['endpoint']),
        ):
            c1_declarations[mode, design] = hashlib.sha256(
                json.dumps(point, sort_keys=True, allow_nan=False).encode()).hexdigest()

    for row in read(GIBBS_DERIVATIVES)['rows']:
        volume = row['comparison'] == 'volume'
        pressure_type = 'imposed' if row['pressure_basis'] == 'retained absolute pressure' else 'calculated bubble'
        state_label = (row['state'].replace('AMP_free', 'AMP (free slope)') + r'\newline '
                       f"{row['temperature_K']:.2f} K, {row['pressure_Pa']/1e6:.5g} MPa")
        c1.append([state_label, pressure_type,
                   r'$\partial G^*/\partial P - V_{\mathrm{EOS}}$ (m$^3$)' if volume else r'Eq.~12 $-$ Gibbs--Helmholtz (J/mol amine)',
                   reduced_gibbs(row['signed_error']), reduced_gibbs(row['estimated_error']),
                   row['admitted_steps'], row['disposition']])
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
    amp_fixed['AMP-hydrolysis-enthalpy-increment']['value'] = amp_enthalpy['AMP_fixed']['endpoint_increment_J_mol']
    table('supplement-amp-fixed-parameters', r'Parameters of the fixed-reference AMP sensitivity with the slope held at $-150$ K.',
          ['Parameter', 'Value', 'Standard error', 'Active bound'],
          [[label, num(amp_fixed[key]['value'], digits), num(amp_fixed[key]['error'], digits),
            fixed.fits['AMP_fixed']['diagnostics']['active_bounds'].get(key, '---')]
           for (label, digits), key in zip(AFIT, aorder, strict=True) if key in amp_fixed],
          [.45,.15,.17,.15], notes=r'The enthalpy increment is relative to the starting R4 correlation in J/mol.')
    outputs[path] += outputs.pop(LATEX / 'tables/supplement-amp-fixed-parameters.tex')
    phase_control_tables(phases['dea_controls'], phases['amp_controls'], property_summary['shared'],
                         table, head, num, reduced_gibbs, property_summary['dea_density'], amp_outcomes)
    spread_table(property_summary['spread'], table, head, num)

    read('analyses/dea_transfer/results/binary.json')
    read(BASE + 'conditional-uncertainty.json')
    read(BASE + 'checks.json')
    read('analyses/dea_transfer/inputs/part-ii-346/route-current.json')
    # Values used by the surviving MEA and historical-comparison prose checks.
    f2 = lambda v: f'{float(v):.2f}'
    f1 = lambda v: f'{float(v):.1f}'
    f1(pressure_stats([r for r in mea_fit if r['quantity'] == 'PartialPressure'], 'predicted')['AARD_percent'])
    hstrict, hall, hwagner = (next(r for r in hong if (r['block'], r['subset']) == k) for k in (('canonical', 'strict grid'), ('canonical', 'all'), ('wagner', 'all')))
    [f1(hstrict['hong']), f1(hong_pressures['canonical']['strict_grid']['salt_anchored']['aard_percent']), f"the {hstrict['n']} observations", f"at {hstrict['locally_unstable']} of them"]
    [f"{f2(hstrict['hong'])}\\,\\%, the MEA model by {f2(hstrict['adopted'])}\\,\\% and the model of Polley and Hedengren by {f2(hstrict['polley_hedengren_2026'])}", ', '.join(f2(hall[k]) for k in ('hong', 'adopted')) + f" and {f2(hall['polley_hedengren_2026'])}",
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
        bstat[*key, 'all'] = dict(b, previous_AARD=historical_bands[key]['AARD_percent'])
    for b in read(BANDS + 'band-table.csv'):
        if b['cohort'] == 'all':
            continue
        key = (b['property'], b['band'], b['role'], b['cohort'])
        d = brel([q for q in bpts if (q['property'], q['band'], q['role'], q['cohort']) == key])
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

def mea_tables(outputs):
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
            ('Kiepe', 'pressure'): (rf'\ce{{CO2}}--water pressures, {KIEPE_AUTHOR}\cite{{{KIEPE_CITE}}}', ''),
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
        'F2': 'Tied amine-ion Born diameters (fit with the MEA-fitted shared set)',
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
    'no one two three four five six seven eight nine ten'.split()


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
        if (match := re.fullmatch(r'(.+?)~(K.*)', str(value))):
            return cell(match[1], kind) + '~' + match[2]
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
    def table(name, caption, headings, data, cols=None, landscape=False, sep=3, included_in=None):
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
            place = '[!htbp]' if name.endswith('_reference_state.tex') or '{tables/' + (included_in or name).removesuffix('.tex') + '}' in (ROOT/'docs/scientific/latex/supplement.tex').read_text() else '[pos=!htbp]'
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


    E = BUNDLE/'results/paper-evidence-341'
    SALT = BUNDLE/'results/salt-anchored-435'
    ADOPTED = SALT/'MEA/F4'
    F = SALT/'MEA/evidence/F4'

    def reference_states():
        folder = E.parent/'reference-states-428'
        record_path = ROOT / STUDY / 'results/display-replays/caloric-and-species.json.gz'
        old_record = read(ADOPTED/'reference-state.json')
        basis_path = ADOPTED/'q4.json'
        spec = read(folder/'tables.json')['mea']
        record = read(str(record_path.relative_to(ROOT)))['reference_state']
        common = read(basis_path)['result']['S15_common_basis']
        for reaction, old, basis in zip(record['reactions'], old_record['reactions'], common, strict=True):
            offset = basis['common_ln_K'] - old['ln_K_source']
            reaction['ln_K_source'] += offset
            reaction['Gamma'] -= offset
        rows = [[label, *(format(reduce(getitem, path, record), precision) if path else '' for path in paths)]
                for label, precision, *paths in spec['rows']]
        name = 'mea_reference_state.tex'
        table(name, spec['caption'].replace('MEA model.', 'MEA model with all reaction references at 100 kPa.'),
              spec['headings'], rows, spec['cols'])

    def tables():
        study = FixedReference(read)
        endpoint = study.fits['MEA']
        document = endpoint['endpoint']['parameters']
        fitrows = read(F/'fitted-rows.csv')
        fit = {r['identity']: r for r in endpoint['replay']['rows']}
        for row in fitrows:
            replay = fit[row['id']]
            row.update(predicted=replay['value'], cost=replay['cost'])
        uncertainty = study.conditional('MEA')
        errors = uncertainty['conditional_standard_error']
        params = [dict(identity=r['identity'], value=r['origin'], lower=r['bounds'][0], upper=r['bounds'][1],
                       conditional_SE=errors.get(r['identity'])) for r in uncertainty['coordinates']]
        coords = {r['identity']:r for r in params}
        values = {c['identity']: c['value']['magnitude'] for n in document['components'] + document['pairs'] for c in n['coefficients'] if 'value' in c}
        values |= {i: c['value']['magnitude'] for n in document['topology']['edges'] for i, c in coefficients(n)}
        salt_pairs = read(SALT/'shared-parameters.json')['water_ion_pairs']
        for pair_record in salt_pairs:
            coefficient, = pair_record['coefficients']
            constant, slope = (term['coefficient']['value']['magnitude'] for term in coefficient['temperature_law']['terms'])
            values[coefficient['identity']] = constant
            values[coefficient['identity'] + '/temperature_slope'] = slope
        # Parameters set by the three fits before the joint fit (Results): pure water to IAPWS-95, CO2-water to Kiepe pressures, MEA dielectric pair to permittivities.
        separate = {'component/water/segment_count', 'component/water/dispersion_energy_over_k', 'association/water/a/water/b/energy_over_k', 'association/water/a/water/b/volume',
                    'pair/carbon-dioxide/water/k_ij', 'pair/carbon-dioxide/water/k_ij/reciprocal_temperature_slope',
                    'component/monoethanolamine/dielectric_volume', 'component/monoethanolamine/dielectric_temperature'}
        unordered = lambda i: '/'.join(['pair', *sorted(i.split('/')[1:3]), *i.split('/')[3:]]) if i.startswith('pair/') else i
        fitted = {unordered(i) for i in [*coords, *separate]}
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
        main_species = species_rows(4)
        main_species[species.index('carbamate-anion')][3] = r'$\boldsymbol{\res{mea-carbamate-dispersion-energy-species-table}}$'
        table('species_parameters.tex', r"Segment, association and Born parameters of the MEA model. || Bold: fitted in this work; --: not used. $^{\mathrm{a}}$Shared species, held fixed for DEA, MDEA and AMP. $^{\mathrm{b}}$Cross-association with water; its energy is half that of water. $^{\mathrm{c}}$Association volume converted in this work (Section~\ref{supp-sec:s-parameters}). $^{\mathrm{d}}$Single sphere; Born diameter equal to $\sigma$. $^{\mathrm{e}}$Born diameter set in this work. $^{\mathrm{f}}$Born diameter of the hydrogen ion in Ref.~\cite{Figiel2025}. $^{\mathrm{g}}$Born diameter calculated from the hydration free energy of Ref.~\cite{palascakAccurateExperimentalValues2004} (Section~\ref{supp-sec:s-parameters}). For the ions, the packing diameter is $0.88\sigma$ and the Debye--H\"uckel diameter is $\sigma$. Table~\ref{supp-tab:supplement-species-parameters} gives unrounded values and the remaining inputs.",
              [species_headings[i] for i in main_indices]+['Ref.'],
              [[row[0]+mark*(s in shared_species), *[row[i] for i in main_indices[1:]], ref + (note(letters) if letters else '')] for row,(ref,letters,_),s in zip(main_species,sources,species,strict=True)],
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
        ['', *(symbol[s] for s in species[1:])]
        pair_specs = [('carbon-dioxide','water','CO2--water fit'),('monoethanolamine','water','Joint fit'),
                      ('water','protonated-monoethanolamine','Joint fit'),('water','carbamate-anion','Joint fit'),
                      ('water','bicarbonate-anion','Sodium-salt fit'),('water','carbonate-anion','Sodium-salt fit'),
                      ('protonated-monoethanolamine','bicarbonate-anion','Joint fit'),('protonated-monoethanolamine','carbamate-anion','Joint fit'),
                      *[('water', ion, r'\cite{Held2014}') for ion in ('hydronium-cation', 'hydroxide-anion')]]
        def pair_se(s, u, quantity=''):  # conditional standard error of a fitted interaction; none for a fixed value or one on its bound
            return num(next((coords[i+quantity]['conditional_SE'] for i in (f'pair/{s}/{u}/k_ij', f'pair/{u}/{s}/k_ij') if i+quantity in coords), None), 3)
        def pair_rows(decimals=None, errors=False):
            ref = lambda s, u, source: source if not errors or source.startswith(r'\cite') else source + (note('b') if source == 'CO2--water fit' else note('c') if {s,u} == {'protonated-monoethanolamine','carbamate-anion'} else note('d') if {s,u} == {'protonated-monoethanolamine','bicarbonate-anion'} else '')
            return [[symbol[s]+'--'+symbol[u]+mark*(errors and {s,u} <= set(shared_species)),pair(s,u,decimals=decimals),*[pair_se(s,u)]*errors,(pair(s,u,'/temperature_slope',decimals) + r'~K$^{-1}$' if source == 'Sodium-salt fit' else
                    pair(s,u,'/reciprocal_temperature_slope',decimals) + '~K' if pair(s,u,'/reciprocal_temperature_slope',decimals) != '--' else '--'),*[pair_se(s,u,'/reciprocal_temperature_slope')]*errors,ref(s,u,source)] for s,u,source in pair_specs]
        table('interaction_matrix.tex', r"Nonzero or fitted binary interaction parameters of the MEA model with their conditional standard errors (s.e.), $k_{ij}(T)=k_{ij}(313.15\,\mathrm{K})+b_{ij}(1/T-1/313.15\,\mathrm{K})$. || Bold: fitted in this work. A standard error is given for the jointly fitted values that are not on a bound; an absent slope is zero. The two sodium-salt slopes are linear in $T-313.15\,\mathrm{K}$. $^{\mathrm{a}}$Shared interaction, held fixed for DEA, MDEA and AMP. $^{\mathrm{b}}$Fitted beforehand to \ce{CO2}--water pressures (Section~\ref{sec:parameters}). $^{\mathrm{c}}$On its lower bound. $^{\mathrm{d}}$On its upper bound. All unlisted unlike-charge or neutral pairs have $k_{ij}=0$; same-sign ion dispersion is excluded. Table~\ref{supp-tab:supplement-interaction-matrix} gives unrounded values.",
              ['Pair',r'$k_{ij}(313.15\,\mathrm{K})$','s.e.','Slope','s.e. (K)','Ref.'],pair_rows(4,True),['l','r','r','r','r','l'])
        table('supplement_interaction_matrix.tex', r"Binary interactions at full precision. || Bold values were fitted in this work. Sodium-salt slopes multiply $T-313.15\,\mathrm{K}$; slopes in kelvin multiply $1/T-1/(313.15\,\mathrm{K})$. All unlisted interactions and slopes are zero; same-sign ion dispersion is excluded.",
              ['Pair',r'$k_{ij}(313.15\,\mathrm{K})$','Slope','Source'],pair_rows(),['l','r','r','l'])
        table('supplement_fitted_parameters.tex', r"Jointly fitted parameters, bounds and conditional standard errors. || Bold values were fitted in this work. A dash in the standard-error column marks an active bound. Born diameters of the two amine ions equal their segment diameters.", ['Parameter','Value','Lower','Upper','Standard error'], [[label(r['identity']),'**'+full_precision(r['value']),num(r['lower']),num(r['upper']),num(r['conditional_SE'])] for r in params], [.27,'r','r','r','r'])
        reaction = read(BUNDLE/'results/adoption-297/paper-evidence/source-only/chemical_reaction_source_contract.json')
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
        ranges = {'MEA': {r['reaction_id']: r['temperature_range_k'] for r in reaction['reactions']}, 'DEA': read('analyses/dea_transfer/inputs/part-ii-346/route-current.json')['reaction_ranges_K'],
                  'MDEA': read('analyses/mdea_mea_workflow/results/retransfer-343/reaction-ranges.json')['source_ranges_K'], 'AMP': read('analyses/amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json')['reaction_ranges_K']}
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
        compare = read(BUNDLE/'results/reduced-refit/fit-comparison.csv')
        agreement = read(BUNDLE/'results/reduced-refit/agreement.csv')
        score = lambda fit, dataset: next(r for r in agreement if r['fit']==fit and r['dataset']==dataset)['aard_percent']
        dataset_counts = {r['dataset']: r['n'] for r in agreement if r['fit'] == compare[0]['fit']}
        table('choice_cost.tex', rf"Parameter restrictions for MEA and their deviations on identical observations. || $C$: objective value. The MEA model is not a row of this sequence: it keeps the eleven-parameter form of the third row, with the water--bicarbonate and water--carbonate interactions fixed from the salt data and the protonated-MEA--bicarbonate interaction fitted in place of the water--bicarbonate interaction. The deviations are for the {dataset_counts['fitted: fitted CO2 partial pressure']} fitted pressures, the {dataset_counts['not fitted: six-source pressures']} pressures not fitted and the {dataset_counts['fitted: loaded density']} fitted loaded densities. Each row adds its restriction to the row above; the last row is an alternative to the row above it, and both start from the sodium-salt row. The fourth row also fixes the carbamate--water interaction and the temperature slope of the protonated-MEA--water interaction at zero. The sodium-salt row fixes the temperature-dependent water--bicarbonate and water--carbonate interactions at values fitted to the osmotic coefficients of aqueous sodium bicarbonate and sodium carbonate that Peiper and Pitzer derived from their model \cite{{peiperThermodynamicsAqueousCarbonate1982}}, and adds a protonated-MEA--bicarbonate interaction as a fitted parameter. The last two rows fix the protonated-MEA--bicarbonate and the protonated-MEA--carbamate interaction at zero, respectively. Deviations on fitted and not-fitted data are not directly comparable.", ['Calibration','Parameters','On bounds','$C$',r'\makecell[rb]{Fitted\\pressure\\AARD (\%)}',r'\makecell[rb]{Not-fitted\\pressure\\AARD (\%)}',r'\makecell[rb]{Fitted\\density\\AARD (\%)}'], [[r['fit'],r['fitted_parameters'],r['on_bound'],num(r['cost'],6),*[f"{float(score(r['fit'],d)):.2f}" for d in ('fitted: fitted CO2 partial pressure','not fitted: six-source pressures','fitted: loaded density')]] for r in compare], [.36]+['r']*6)
        cp = read(E/'same-data-comparison/part1-scores.json')
        replay = study.load('E/MEA/replay.json.gz')
        predictions = {r['identity']: r for r in replay['rows']}
        def apply(rows, predictions, key):
            scored = []
            for row in rows:
                q = predictions[key(row)]
                if q['status'] == 'Available' and q['requested_tolerance_met']:
                    scored.append(dict(row, predicted=q['value']))
            return scored

        canonical = apply(read(F/'canonical-pressure.csv'), predictions, lambda r: r['target'])
        wagner = {r['identity']: r for r in [*replay['hot_wagner'], *study.endpoint_record('display-replays/wagner.json.gz', 'MEA')['rows']]}
        off_window = {r['identity']: r for r in study.load('MEA/off-window.json.gz')['rows']}

        fitted_ids = {r['id'] for r in fitrows}
        comparison = study.endpoint_record('display-replays/mea-comparisons.json.gz', 'MEA')
        caloric = study.endpoint_record('display-replays/caloric-and-species.json.gz', 'MEA')
        density_by_id = {r['identity']: r for r in comparison['density']}
        density = [dict(row, predicted_kg_m3=density_by_id[row['id']]['value']) for row in read(F/'density.csv')]
        cp_rows = comparison['heat_capacity']
        heat = caloric['arcis']
        kim = comparison['kim_2007']
        def kim_at(T, subset='all_printed'):
            rows = [r for r in kim if r['T_K'].startswith(T) and r['interval_status'] == 'available'
                    and (subset == 'all_printed' or r['source_inconsistent'] == 'False')
                    and (subset != 'without_first120' or r['first_120'] == 'False')]
            return stats(rows)

        rows_for = {
            'Six-source pressures': canonical,
            MEA_TRACKING_ADDITIONAL_PRESSURES: [r for r in canonical if r['target'] not in fitted_ids],
            'Wagner pressures': apply(read(F/'wagner-pressure.csv'), wagner, lambda r: r['target']),
            'Species fractions': caloric['species'],
            'Jakobsen carbonate share': [dict(observed=r['observed'], predicted=r['value'])
                                         for r in comparison['carbonate_share']],
            'Arcis2011 heats': heat,
        }
        all_density = {'Amundsen2009 loaded': ('Amundsen2009', True), 'Amundsen2009 CO2-free': ('Amundsen2009', False),
                       'Hartono2014 loaded': ('Hartono2014', True), 'Han2012 all': ('Han2012', None)}
        for group, (source, loaded) in all_density.items():
            rows_for[group] = [dict(observed=r['observed_kg_m3'], predicted=r['predicted_kg_m3']) for r in density
                               if r['source'] == source and (loaded is None or (float(r['loading']) > 0) == loaded)]
        for group, source in [('broad Cp', 'Hilliard'), ('Weiland1997 comparison', 'Weiland'),
                              ('Concepcion2023 comparison', 'Concepcion')]:
            rows_for[group] = [dict(observed=r['observed_kJ_kg_K'], predicted=r['predicted_kJ_kg_K'])
                               for r in cp_rows if r['source'].startswith(source) and r['observed_kJ_kg_K']]
        transfer = apply(read(F/'transfer.csv'), off_window, lambda r: 'off-window:' + r['target'].removesuffix('-pco2'))
        for concentration in (15, 45):
            ids = {r['observation_id'] for r in read(ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')
                   if float(r['MEA_weight_fraction'] or 0) == concentration / 100}
            rows_for[f'Aronu {concentration} wt% pressures'] = [r for r in transfer if r['target'].removesuffix('-pco2') in ids]
        previous = {r['group']: r['deviations'][1] for r in cp}
        previous_groups = {}
        for row in read(E/'paper-evidence/fitted-rows.csv'):
            previous_groups.setdefault(rowkey(row['group'], row['quantity']), []).append(row)
        prior_stats = {k: stats(v) for k,v in previous_groups.items()}
        for r in cp:
            name = r['group']
            if name.startswith('Kim heat'):
                metric = kim_at(name.split()[2])
                r['deviations'][1] = metric['RMSE']
            elif name in rows_for:
                rows = rows_for[name]
                r['deviations'][1] = stats(rows)['AARD_percent' if r['metric'].startswith('AARD') else 'RMSE']
        heat_capacity_labels = {'Weiland1997 comparison': 'Weiland et al.\\ heat capacities \\cite{weilandHeatCapacityAqueous1997}', 'Concepcion2023 comparison': "Concepci\\'on et al.\\ heat capacities \\cite{concepcionHeatCapacitiesDifferent2023}"}
        same_names = {'Six-source pressures':'All pressures at 30 wt% MEA, six sources', 'Species fractions':'All species fractions', MEA_TRACKING_ADDITIONAL_PRESSURES:'Pressures not fitted, the same six sources', 'broad Cp':'Hilliard heat capacities at 313.15--393.15 K'}
        # The published fitting account of the earlier model does not give the role of each pressure and species observation.
        earlier_role = lambda role: 'not stated' if 'see role note' in role else role.split(';')[0].replace('formulation ','').replace('comparison', r'com\-parison')
        # Fitted quantities that the earlier model was scored on with identical observations, and the prior use of the comparison sets.
        same = {('common149','partial_pressure'): MEA_TRACKING_FITTED_PRESSURES, ('Jakobsen','amount_ratio'): 'Species ratios', ('common149','addition_enthalpy'): 'Vinjarapu2024 heats', ('Cp','equilibrium_isobaric_heat_capacity'): 'Four Hilliard heat capacities'}
        prior = {'Arcis2011': 'a', 'Kim heat 313': 'b', 'Kim heat 353': 'b', 'Amundsen2009': 'c', 'Hartono2014': 'c', 'Han2012': 'c'}
        earlier = {r['group']: r for r in cp}
        # #434: the retained role text of the Hilliard heat-capacity group counts two fitted observations; the fit has four of the 51.
        hilliard = read('analyses/round_5/results/records/Hilliard-Cp.json')['current_broad_roles']
        role_of = lambda r: f"{hilliard['fitted']} fitted / {hilliard['outside']} not fitted" if r['group'] == 'broad Cp' else r['roles'][1].split(';')[0]
        # Deviations show two decimals; an RMSE of the main-text table keeps four significant digits, as in its fitted block.
        both = lambda r, value, main: [f'{float(value):.2f}', '--'] if r['metric'].startswith('AARD') else ['--', num(value) if main else f'{float(value):.2f}']
        data = [block(9, 'Fitted', True)]
        for key, rows in groups.items():
            r = earlier.get(same.get(key))
            data.append([rowlabel(key), len(rows), 'fitted', f"{stats(rows)['AARD_percent']:.2f}", '--' if 'pressure' in key[1] else num(stats(rows)['RMSE']/(1000 if key[1]=='addition_enthalpy' else 1)), *([earlier_role(r['roles'][0]), *both(r, r['deviations'][0], True)] if r else ['--']*3),
                         f"{prior_stats[key]['AARD_percent']:.2f}" + (' / ' + num(prior_stats[key]['RMSE']/(1000 if key[1]=='addition_enthalpy' else 1)) if 'pressure' not in key[1] else '')])
        data.append(block(9, 'Not fitted, or fitted in part'))
        aside = []  # the sets of this block that are not pressures are listed in the supplement
        for r in cp:
            if r['group'] in same.values(): continue
            unit = r['metric'].partition('(')[2].rstrip(')')
            main = 'pressures' in r['group'] or r['group'] == 'Species fractions'
            (data if main else aside).append([cited(r['group'], heat_capacity_labels.get(r['group'], same_names.get(r['group'], r['group']))) + ('' if r['metric'].startswith('AARD') else f' ({unit})'), r['n'][0],
                         role_of(r) + next((r'$^{\mathrm{' + m + '}}$' for k, m in prior.items() if r['group'].startswith(k)), ''), *both(r, r['deviations'][1], main), earlier_role(r['roles'][0]), *both(r, r['deviations'][0], main), num(previous[r['group']])])
        kiepe = groups[('Kiepe', 'pressure')]
        kiepe_cost = math.fsum(float(row["cost"]) for row in kiepe)
        table('mea_data.tex', (r"Data for MEA with their roles in the joint fit of the MEA model, the deviations of that model, the deviations of the model of Polley and Hedengren CITE14, and the fit with the MEA-fitted shared set on identical observations. || The last column reports the AARD of the fit with the MEA-fitted shared set, followed by RMSE where both are available. --: not calculated; a pressure deviation is given as AARD only. Roles refer to the objective of each model; ``not stated'': Ref.~CITE14 does not state for every pressure and species observation whether it was fitted. For that model, the species-ratio and carbonate-share measurements informed an earlier fit of the ion parameters but were not in the objective of the published parameters. The sets of the lower block overlap with each other and with the fitted observations, so their counts are not additive; Table~\ref{supp-tab:supplement-mea-comparison} lists the sets of that block that are not pressures. The " + str(len(kiepe)) + r" \ce{CO2}--water pressures of Kiepe et al.\ remain in the objective although the \ce{CO2}--water interaction was fitted to them beforehand and is fixed; they contribute " + f"{kiepe_cost:.4f}" + r" to $C$ (Table~\ref{supp-tab:objective-groups}). Deviations on fitted and not-fitted data are not directly comparable.").replace('CITE14', CITE14),
              ['Quantity (unit)', '$N$', 'Role', r'\makecell[rb]{AARD\\(\%)}', 'RMSE', 'Role in '+CITE14, r'\makecell[rb]{AARD (\%)\\'+CITE14+'}', r'\makecell[rb]{RMSE\\'+CITE14+'}', r'\makecell[rb]{MEA-fitted\\shared set}'], data, [.24,'r',.12,'r','r',.08,'r','r','r'])
        table('supplement_mea_comparison.tex', r"Data for MEA that are not fitted, or fitted in part, and are not pressures, with the deviations of the MEA model, the model of Polley and Hedengren CITE14, and the fit with the MEA-fitted shared set on identical observations. || The deviations of the last column use the metric of the row. The columns are those of main-text Table~\ref{main-tab:mea-data}. $^{\mathrm{a}}$Also used to select the parameters; $^{\mathrm{b}}$three of these intervals were fitted during earlier model development, in the objective of Ref.~CITE14; no interval of Kim and Svendsen is in the reported fit; $^{\mathrm{c}}$the comparison between density sources informed the choice of fitted density observations. The densities of Ref.~CITE14 are those of its equation of state; for column hydraulics Ref.~CITE14 uses a separate empirical density correlation (its Section~2.2 and Appendix~A.2), so its loaded-density RMSEs of 135--153 kg/m$^3$ describe the liquid volume of that equation of state under load, not that hydraulic density. These sets overlap with each other and with the fitted observations, so their counts are not additive.".replace('CITE14', CITE14),
              ['Quantity (unit)', '$N$', 'Role', r'\makecell[rb]{AARD\\(\%)}', 'RMSE', 'Role in '+CITE14, r'\makecell[rb]{AARD (\%)\\'+CITE14+'}', r'\makecell[rb]{RMSE\\'+CITE14+'}', r'\makecell[rb]{MEA-fitted\\shared set}'], aside, [.24,'r',.12,'r','r',.08,'r','r','r'])
        interior = [label(k) for k in uncertainty['free_coordinates']]
        correlation = uncertainty['conditional_correlation']
        table('supplement_correlations.tex', r"Conditional correlations of the nine fitted parameters that are not at a bound.", ['Parameter']+[str(i+1) for i in range(9)], [[f'{i+1}. {interior[i]}']+[num(v,3) if j<=i else '' for j,v in enumerate(row)] for i,row in enumerate(correlation)], [.26]+['r']*9)
        profiles = read(ADOPTED/'uncertainty/profiles.json')
        table('bound_profiles.tex', r"Historical tracking-reference refits with one interaction fixed inside its active bound. || The other parameters are refitted. Phase stability was not searched for these refits.", ['Interaction','Distance from the bound (% of range)','Fixed value','$C$','Change in $C$'], [[label(r['parameter']),num(100*r['fraction']),num(r['fixed_value']),num(r['cost'],9),num(r['delta_cost'],7)] for r in profiles], ['l']+['r']*4)
        # Historical sensitivity on the previous shared set.
        # The shared water-bicarbonate interaction fixed at two other values whose MEA refits stay within the largest change of bound_profiles; MDEA refitted at each.
        S, M = 'analyses/mdea_mea_workflow/results/shared-bicarbonate-417/', 'analyses/mdea_mea_workflow/results/bounded-binary-411/'
        profile, search, compared = (read(S + f) for f in ('profile.json.gz', 'mdea-search-readback.json', 'mdea-comparison.json.gz'))
        comparison_order = read(S + 'mdea-group-readback.json')['ordered_cases']
        column_order = [comparison_order.index(case) for case in ('reported', 'low', 'high')]
        model_cost = read(E/'candidate/replay.json')['cost']
        reported, states = read(M + 'summary-row.json'), read(M + 'stability.json')['grid']['states']
        _allowance, sides = max(r['delta_cost'] for r in read(E/'uncertainty/profiles.json')), [profile['selected'][s] for s in ('low', 'high')]
        reference_change = read('analyses/round_5/results/C/MEA-k-profile.json.gz')['delta_cutoff']  # half the variance factor times the 95 % chi-square value for one parameter
        def aard(group):
            cases = compared[group]['original']
            return [f"{cases[i]['AARD_percent']:.2f}" for i in column_order]
        ermatchkov = compared['Ermatchkov']['original'][column_order[0]]['relative_rows']
        def pooled(sets):  # count-weighted over the sets: the AARD over all of their observations
            cases = [compared[g]['original'] for g in sets]
            n = sum(c[column_order[0]]['relative_rows'] for c in cases)
            return n, [sum(c[i]['relative_rows'] * c[i]['AARD_percent'] for c in cases) / n for i in column_order]
        # Total pressures and CO2 partial pressures are different observables; the pooled group mixes them.
        outside = {'Total pressures': pooled(('corrected-Kamps', 'Kuranov-413K', 'Sedighi')), 'CO2 partial pressures': pooled(('Ermatchkov', 'Xiao'))}
        compared['all pressures not fitted']['original']
        outside = {k: (n, [f'{v:.2f}' for v in values]) for k, (n, values) in outside.items()}
        table('mdea-shared-control.tex', rf"MDEA fits with the MEA-fitted shared set: the shared water--bicarbonate interaction $k$ fixed at its MEA-fitted value, $k_0$, and at two other values, with the MEA and the MDEA parameters refitted at each. || Fixed in every column: the other shared parameters, the reaction correlations, the MDEA data, weights and bound, and the three initial MDEA parameter sets. Refitted: the other ten MEA parameters and the eight MDEA parameters. $C(k)$: objective of the MEA fit with $k$ fixed; the refit at $k_0$ reproduces the objective of the fit with $k$ free within $10^{{-6}}C$, and both other values keep $C(k)-C(k_0)$ within the reference change of {reference_change:.2f} (Section~\ref{{sec:s-uncertainty}}). $P$: total pressure; AARD follows main-text Eq.~\eqref{{main-eq:aard}}. The {ermatchkov} CO2 partial pressures of Ermatchkov et al.\ among the pressures outside the objective helped choose the initial MDEA parameters. Most unfinished searches are at states where no bubble pressure could be calculated; a confirmed split is a second liquid confirmed by a two-liquid equilibrium calculation. The searches are those of Section~\ref{{sec:s-phase}}.",
              ['Quantity', '$k_0$', 'Lower value', 'Upper value'],
              [['Water--bicarbonate interaction $k$', *(f'{k:.4f}' for k in (profile['center']['k'], *(p['k'] for p in sides)))],
               ['MEA objective change $C(k)-C(k_0)$', *(f"{c - profile['center_cost']:.4f}" for c in (model_cost, *(p['cost'] for p in sides)))],
               ['MDEA objective', *(f'{c:.4f}' for c in (reported['data_cost'], search['low']['cost'], search['high']['cost']))],
               [f"Fitted loaded-solution $P$ of Kuranov et al.\\ ({compared['Kuranov']['original'][column_order[0]]['rows']}), AARD (%)", *aard('Kuranov')],
               [f"All fitted MDEA pressures, with the CO2-free binary pressures ({compared['all pressures fitted']['original'][column_order[0]]['rows']}), AARD (%)", *aard('all pressures fitted')],
               *([f"{label} outside the objective ({n}), AARD (%)", *values] for label, (n, values) in outside.items()),
               [f'Unfinished searches of {states}', reported['unavailable_searches'], *(search[s]['counts']['unavailable_records'] for s in ('low', 'high'))],
               ['Confirmed liquid--liquid splits', reported['liquid_liquid_splits_found'], *(search[s]['counts']['confirmed_distinct_splits'] for s in ('low', 'high'))]],
              [.46, 'r', 'r', 'r'])
        table('kim_alternatives.tex', r"Kim finite-interval heat comparisons at 393.15 K for alternative source exclusions. || RMSE is kJ/mol absorbed CO2; AARD is percent. All alternatives use the MEA model.", ['Intervals','$N$','RMSE','AARD'], [[name,kim_at('393.15', key)['n'],num(kim_at('393.15', key)['RMSE'],6),num(kim_at('393.15', key)['AARD_percent'],6)] for key,name in [('all_printed','All tabulated intervals'),('source_consistent','Without the two inconsistent intervals'),('without_first120','Also without first intervals')]], ['l','r','r','r'])
        weights = read(E/'objective-groups.csv')  # unchanged scales and weights
        weight_groups = {}
        for r in weights: weight_groups.setdefault(rowkey(r['group'],r['quantity']),[]).append(r)
        table('objective_groups.tex', r"Assigned objective scales and weights. || Scales are in the unit of the quantity, and unity for the logarithmic pressure residuals. The text gives the origin of each scale and weight. The Kiepe pressures were fitted beforehand and contribute a constant to the reactive objective.", ['Quantity','$N$','Scale range','Weight range','Contribution to $C$'], [[rowlabel(key,False),sum(int(r['n']) for r in part),span(float(r['scale']) for r in part),span(float(r['weight']) for r in part),num(sum(float(r['cost']) for r in groups[key]),6)] for key,part in weight_groups.items()], [.42,'r','l','l','r'])
        check_record = study.endpoint_record('display-replays/bubble-checks.json.gz', 'MEA')
        checks = check_record['rows']
        # Each bubble pressure was solved from two initial pressures; the digits shown must agree.
        state = [('$T$ (K)', lambda r, k: num(r['T_K'],7)), ('Bubble pressure (Pa)', lambda r, k: num(r['answers'][k]['bubble_pressure_Pa'],10)), (r'Liquid density (kg/m$^3$)', lambda r, k: num(r['answers'][k]['density_kg_m3'],10))]
        contribution_names = dict(association='Association', born='Born', hard_chain='Hard chain', dispersion='Dispersion', debye_huckel=r'Debye--H\"uckel', residual_helmholtz='Total residual')
        table('supplement_check_values.tex', r"Reference values of the MEA model at three bubble states, for checking an implementation: temperature, bubble pressure, liquid mass density, reduced residual Helmholtz contributions $A_i/(nRT)$ and true liquid species fractions. || Inputs: $x_{\ce{CO2}}=3.6\times10^{-4}$ in water; $x_{\ce{MEA}}=0.9264$ in MEA--water; 30 wt\% MEA at loading 0.3 mol/mol. Each bubble pressure was solved from two initial pressures, which agree to the digits shown. Zero terms are omitted. These values check the numerical calculation; they are not measurements.", ['Quantity',r'\ce{CO2}--water','MEA--water','Loaded MEA'], [[name,*[get(r,0) for r in checks]] for name,get in state]+[[('$x_{'+symbol[key[2:]]+'}$') if key.startswith('x_') else contribution_names[key],*[num(r['answers'][0][key],10) for r in checks]] for key in checks[0]['answers'][0] if key not in ('bubble_pressure_Pa','density_kg_m3','molar_density_mol_m3') and any(r['answers'][0][key] for r in checks)], ['l','r','r','r'])
        shared = read(E/'shared-coefficients.csv')
        # One row per shared species; every other shared value follows from a rule stated in the note, which the checks below hold to the retained list.
        sv = {r['identity']: float(r['value']) for r in shared}
        water_pair = lambda s: next((i for i in (f'pair/{s}/water/k_ij', f'pair/water/{s}/k_ij') if i in sv), '')
        used = {f'component/{s}/{q}' for s in shared_species for q in ('segment_count','segment_diameter','dispersion_energy_over_k','born_diameter','solvation_factor')} | {water_pair(s) for s in shared_species}
        for s in shared_species[2:]:
            sv[f'component/{s}/segment_diameter']
            used |= {f'component/{s}/packing_diameter', f'component/{s}/debye_huckel_diameter'}
        slope, _dielectric = 'pair/carbon-dioxide/water/k_ij/reciprocal_temperature_slope', [f'component/{s}/dielectric_{q}' for s in shared_species[:2] for q in ('volume','temperature')]
        # S2 and S3 already list species fields and the explicitly retained pairs.
        covered_pairs = {tuple(sorted((x, y))) for x, y, _ in pair_specs}
        missing = [r for r in shared if (r['identity'].startswith('component/') and r['identity'].rsplit('/', 1)[-1] in ('packing_diameter', 'debye_huckel_diameter')) or (r['identity'].startswith('pair/') and tuple(sorted(r['identity'].split('/')[1:3])) not in covered_pairs)]
        table('supplement_shared_remaining.tex', r"Shared parameters not listed in Tables~\ref{tab:supplement-species-parameters} and \ref{tab:supplement-interaction-matrix}, at full precision. || Together with the reaction coefficients in Table~\ref{tab:supplement-reaction-coefficients}, those tables give the unrounded values of the shared parameters marked in main-text Tables~\ref{main-tab:species-parameters} and \ref{main-tab:interaction-matrix}.", ['Parameter','Value','Unit','Source'], [[label(r['identity']), f"{float(r['value']):.15g}" if r['identity'].endswith('/packing_diameter') else full_precision(r['value']), r['unit'],
                                              r'$0.88\sigma$' if r['identity'].endswith('/packing_diameter') else r'Equal to $\sigma$' if r['identity'].endswith('/debye_huckel_diameter') else 'Set in this work'] for r in missing], [.42,'r','l','l'])
        table('pressure_sources.tex', r"Pressure deviations of the MEA model by experimental source at nominal 30 wt\% MEA. || Source subsets contain both fitted observations and observations that are not fitted.", ['Source','Observations','AARD (%)'], [[cited('', SOURCE_NAMES[s]) + r' \cite{' + PRESSURE_CITE[s] + '}',len(part),format(stats(part)['AARD_percent'], '.1f')] for s in sorted({r['source'] for r in canonical}) for part in [[r for r in canonical if r['source']==s]]], ['l','r','r'])
        round7 = 'analyses/round_7/'
        sensitivity = read(MEA_EXPANDED_SUMMARY)
        expanded = read(round7 + 'results/E/F4/replay.json.gz')
        replays = [replay, expanded]
        rows = []
        for cohort_label, key in [
                ('Legacy fitted pressures', 'legacy'), ('Added pressures', 'added'),
                ('Hot pressures in the expanded objective', 'hot_expanded'),
                ('Hot pressures including Wagner', 'hot_published'),
                ('All pressures in the expanded objective', 'all_pressure'),
                *[(s, s) for s in PRESSURE_CITE]]:
            summaries = [r['summary']['pressure'][key] for r in replays]
            rows.append([cohort_label, summaries[0]['attempted'],
                         *[f"{r['AARD_percent']:.2f} / {r['bias_percent']:+.2f}" for r in summaries]])
        wagner = [r['hot_wagner'] for r in replays]
        wagner_scores = []
        for cohort in wagner:
            relative = [100*(r['value']/r['observed'] - 1) for r in cohort if r['status'] == 'Available']
            wagner_scores.append(f'{math.fsum(map(abs, relative))/len(relative):.2f} / {math.fsum(relative)/len(relative):+.2f}')
        rows.append(['Hot Wagner pressures, outside both fits', len(wagner[0]), *wagner_scores])
        for source in ('Jou1995', 'Mamun2005'):
            scores = []
            for replay in replays:
                ids = {key for key, row in replay['pressure_population'].items()
                       if row['source_key'] == source
                       and round(float(row['temperature_series_C'] or row['temperature_reported_C'])) == 120}
                relative = [100*(r['value']/r['observed'] - 1) for r in replay['rows']
                            if r['identity'] in ids and r['status'] == 'Available']
                scores.append(f'{math.fsum(map(abs, relative))/len(relative):.2f} / {math.fsum(relative)/len(relative):+.2f}')
            rows.append([source + ', nominal 120 degrees Celsius', len(ids), *scores])
        pressure = expanded['summary']['pressure']
        table('supplement-mea-pressure-sensitivity.tex',
              'MEA CO2 partial-pressure sensitivity at nominal 30 wt% with the selected fixed-reference fit and the historical full-weight tracking-reference fit. || '
              f"The {pressure['added']['attempted']} added pressures include the {pressure['hot_expanded']['attempted']} hot rows. "
              f"The {len(wagner[1])} hot Wagner pressures enter the {pressure['hot_published']['attempted']}-row hot comparison and the separate Wagner row. "
              'Signed bias is the mean signed relative deviation. Both fits retain the salt-anchored shared interactions.',
              ['Pressure cohort', '$N$', '100 kPa AARD / bias (%)', 'Expanded AARD / bias (%)'],
              rows, [.43,.06,.22,.22])
        heat_path = round7 + 'results/display-replays/mea-heat-sensitivity.json.gz'
        heat = read(heat_path)['replay']
        selected_heat = study.load('MEA/heat-comparison.json.gz')['rows']['rows']
        heat_rows = []
        for dataset, dataset_label in [('Kim2014', r'Kim et al. \cite{Kim2014}, finite-addition heat'),
                               ('Vinjarapu2024', r'Vinjarapu et al. \cite{HemaBhavya2025}, integral heat')]:
            q = sensitivity['hot_heat'][dataset]
            observed = [row['observed_kJ_mol'] for row in heat['rows'] if row['source']==dataset and row['T_K']>=370.]
            new_rows = [r for r in selected_heat if r['source'] == dataset and r['T_K'] >= 370]
            values = [r['predicted_kJ_mol'] for r in new_rows if r['status'] == 'available']
            heat_rows.append([dataset_label, f"{q['available']}/{q['attempted']}",
                              f'{min(observed):.2f}--{max(observed):.2f}',
                              f'{min(values):.2f}--{max(values):.2f}',
                              f"{q['minimum']:.2f}--{q['maximum']:.2f}"])
        heat_table = 'supplement-mea-heat-sensitivity.tex'
        table(heat_table,
              r'MEA absorption heats at 393.15 K and 30 wt% with the reported fit and the full-weight expanded fit. || Ranges are in kJ/mol CO2 as positive heat release. The first column of predictions uses the selected fixed-reference fit and the second uses the historical tracking-reference sensitivity. Both models are evaluated at 1.734 MPa and at the source loading intervals for Kim or from zero loading for Vinjarapu.',
              ['Calorimetry', 'Available', 'Measured', '100 kPa fit', 'Expanded fit'],
              heat_rows, [.34,.12,.16,.16,.16], included_in='supplement-mea-pressure-sensitivity.tex')
        OUTPUTS['supplement-mea-pressure-sensitivity.tex'] += OUTPUTS.pop(heat_table)
        off_window = sensitivity['off_window']
        off_rows = []
        for source in ('Aronu2011', 'Aronu2011 15 wt%', 'Aronu2011 45 wt%', 'Jou1995'):
            entries = [off_window[fit][source] for fit in ('reported', 'expanded')]
            off_rows.append([source, *[v for entry in entries for v in (f"{entry['available']}/{entry['attempted'] - entry['available']}",
                             f"{entry['AARD_percent']:.2f} / {entry['bias_percent']:+.2f}")]])
        jou = off_window['expanded']['Jou1995']
        refused = jou['attempted'] - jou['available']
        table('supplement-mea-off-window.tex',
              r'MEA CO2 partial-pressure comparison outside the expanded fit window. || The Aronu rows at 15 and 45 wt% sum to the Aronu total. The separate Jou comparison is at 30 wt%. Both endpoints refused the ' + NUMBER_WORDS[refused] + ' Jou rows at 0 degrees Celsius under the 293.15 K lower limit. AARD and signed bias use available predictions. The population contains ' + str(off_window['population']) + ' observations.',
              ['Source', '100 kPa available/refused', 'AARD / bias (%)',
               'Expanded available/refused', 'AARD / bias (%)'],
              off_rows, [.26,.16,.17,.16,.17])
        table('supplement-mea-window-objective.tex', r'MEA objectives evaluated on the original and expanded observation sets.',
              ['Observation set', '$N$', 'MEA, 100 kPa', 'Tracking, expanded fit'],
              [[population_label, sensitivity['objective'][key]['count'],
                f"{replay['summary'][key + '_cost']:.2f}", f"{sensitivity['objective'][key]['expanded_fit']:.2f}" ]
               for key, population_label in [('original', 'Original'), ('expanded', 'Expanded')]], [.27,.08,.25,.28])
    reference_states()
    folder = E.parent / 'reference-states-428'
    spec = read(folder / 'tables.json')['amp']
    record = read(folder / 'amp.json')
    rows = [[label, *(format(reduce(getitem, path, record), precision) if path else '' for path in paths)]
            for label, precision, *paths in spec['rows']]
    table('amp_reference_state.tex', spec['caption'], spec['headings'], rows, spec['cols'], landscape=True)
    tables()
    for name, body in OUTPUTS.items():
        outputs[TABLES / name] = body if name.endswith('_reference_state.tex') else GROUP.sub(r'\\num{\g<0>}', body)

def mea_figures(outputs):
    adopted = BUNDLE / 'results/salt-anchored-435/MEA/F4'
    evidence = adopted.parent / 'evidence/F4'
    plt.rcParams.update({'font.size':11,'font.family':'STIXGeneral','mathtext.fontset':'stix','pdf.fonttype':42,'figure.constrained_layout.use':True})
    STYLES = ['-', '--', '-.', (0, (7, 2, 1, 2, 1, 2)), (0, (5, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1)), '-', ':']
    TEMPERATURES = [293.15, 313.15, 333.15, 353.15, 373.15, 393.15, 298.15, 322.5]
    COLORS = ['#0072B2','#D55E00','#009E73','#CC79A7','#665500','#007DA8','#222222','#6F4C9B']
    DENSITY_MAP, DENSITY_NORM = matplotlib.colormaps['viridis'], matplotlib.colors.Normalize(293.15, 393.15)  # density figure: one temperature scale for curves and observations

    def temperature_style(temperature):
        index = TEMPERATURES.index(float(temperature)) if float(temperature) in TEMPERATURES else 0
        return COLORS[index % len(COLORS)], STYLES[index % len(STYLES)]

    # Temperature is shown by marker shape at one size, with the color and line style of the same temperature.
    SIZE = 26
    def temperature_marker(temperature):
        return {293.15: 'v', 313.15: 'o', 322.5: 's', 333.15: 's', 353.15: '^', 373.15: 'D', 393.15: 'P'}[float(temperature)]

    def temperature_legend(temperatures):
        return [Line2D([], [], color=temperature_style(T)[0], linestyle=temperature_style(T)[1],
                       marker=temperature_marker(T), markerfacecolor='none', markersize=SIZE**0.5,
                       label=f'{T:g} K') for T in temperatures]

    def save(fig,name):
        with BytesIO() as buffer:
            fig.savefig(buffer, format='pdf', metadata={'CreationDate':None,'ModDate':None})
            outputs[LATEX / 'figures/generated' / (name + '.pdf')] = buffer.getvalue()
        plt.close(fig)

    def points(ax,rows,x,y,label,marker='o',scale=1):
        ax.scatter([float(r[x]) for r in rows],[float(r[y])*scale for r in rows],s=16,facecolors='none',edgecolors='black',marker=marker,label=label,zorder=3)

    def main():
        study = FixedReference(read)
        def curve(family):
            result = study.load(f'MEA/curves/{family}.json.gz')
            return [dict(r, status='available', value=r['value'] if r['status'] == 'available' else math.nan,
                         below_bubble_pressure=str(r.get('below_bubble_pressure', False))) for r in result['rows']]
        off_window = {r['identity']: r for r in study.load('MEA/off-window.json.gz')['rows']}

        meta={r['observation_id']:r for r in read(ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')}
        canonical = read(evidence/'canonical-pressure.csv'); curves = curve('pressure')
        fitted = {r['id'] for r in read(evidence/'fitted-rows.csv') if r['quantity'] == 'PartialPressure'}
        fig,ax=plt.subplots(figsize=(6.8,4.4))
        for T,color in zip([313.15,333.15,353.15,373.15,393.15],COLORS):
            color, style = temperature_style(T)
            part=[r for r in curves if float(r['temperature_K'])==T and r['status']=='available']; part.sort(key=lambda r: float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in part],[float(r['value'])/1000 for r in part],color=color,linestyle=style,label=f'{T:g} K')
            part=[r for r in canonical if abs(float(r['temperature_K'])-T)<2]; ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in part],[float(r['observed'])/1000 for r in part],s=SIZE,marker=temperature_marker(T),facecolors=[color if r['target'] in fitted else 'none' for r in part],edgecolors=color)
        ax.set(xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel='CO$_2$ partial pressure (kPa)',yscale='log'); ax.legend(handles=temperature_legend([313.15,333.15,353.15,373.15,393.15]),ncol=2); save(fig,'pressure')
        fig,axes=plt.subplots(1,2,figsize=(6.8,3.4)); rows=read(evidence/'transfer.csv')
        for ax,w,letter in zip(axes,[.15,.45],'ab'):
            part=[r for r in rows if float(meta[r['target'].removesuffix('-pco2')]['MEA_weight_fraction'])==w]
            for T,color in zip(sorted({r['temperature_K'] for r in part},key=float),COLORS):
                color, style = temperature_style(T)
                sub=[r for r in part if r['temperature_K']==T]
                ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in sub],[float(r['observed'])/1000 for r in sub],s=SIZE,marker=temperature_marker(T),facecolors='none',edgecolors=color,label=f'{float(T):g} K')
                ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in sub],[off_window['off-window:'+r['target'].removesuffix('-pco2')]['value']/1000 if off_window['off-window:'+r['target'].removesuffix('-pco2')]['status'] == 'Available' else math.nan for r in sub],s=SIZE,color=color,marker='x')
            ax.set_title(f'({letter}) {100*w:g} wt% MEA', loc='left'); ax.set(yscale='log',xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel='CO$_2$ partial pressure (kPa)')
        axes[0].legend(fontsize=9)
        save(fig,'concentration-pressure')
        rows=curve('species'); obs=list({r['target']:r for r in read(evidence/'species-figure-data.csv')}.values()); membership={r['membership_id'].replace('|','::'):r['co2_loading_mol_per_mol_mea'] for r in read(ROOT/'data/reference/MEA/manifests/speciation_target_membership.csv')}
        names=['MEA + MEAH+','MEACOO-','MEAH+','HCO3- + CO3^2-']; fig,axes=plt.subplots(2,2,figsize=(6.8,5.4))
        for ax,name,letter in zip(axes.flat,names,'abcd'):
            for T,color in zip([293.15,313.15,333.15,353.15],COLORS):
                color, temperature_dash = temperature_style(T)
                part=[r for r in rows if r['quantity']==name and float(r['temperature_K'])==T and r['status']=='available']
                for below,style in [('False','-'),('True',':')]:
                    sub=sorted([r for r in part if r['below_bubble_pressure']==below],key=lambda r:float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in sub],[float(r['value']) for r in sub],color=color,linestyle=temperature_dash if below=='False' else ':',label=f'{T:g} K' if below=='False' else None)
                sub=[r for r in obs if r['species']==('HCO3-' if name.startswith('HCO3') else name) and float(r['temperature_K'])==T]; ax.scatter([float(membership[r['target']]) for r in sub],[float(r['observed']) for r in sub],s=SIZE,marker=temperature_marker(T),facecolors='none',edgecolors=color)
            ax.set_title(f'({letter}) ' + {'MEA + MEAH+':r'MEA + MEAH$^+$','MEACOO-':r'MEACOO$^-$','MEAH+':r'MEAH$^+$','HCO3- + CO3^2-':r'HCO$_3^-$ + CO$_3^{2-}$'}[name], loc='left'); ax.set(xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel='Liquid mole fraction')
            ax.set_xlim(-.03,.83)
            if name.startswith('HCO3'): ax.set(yscale='log')
        axes[0,0].legend(handles=temperature_legend([293.15,313.15,333.15,353.15]),fontsize=9); save(fig,'speciation')
        for file,name,ylabel,quantity,scale in [('heat','heat-of-absorption','Integral heat (kJ/mol CO$_2$)','integral heat of absorption',1),('density','density-curves','Liquid density (kg/m$^3$)','liquid density',1)]:
            rows=curve(file); fig,ax=plt.subplots(figsize=(6.8,3.8))
            for key,color in zip(dict.fromkeys(r['curve'] for r in rows),COLORS*3):
                color, style = temperature_style(next(r['temperature_K'] for r in rows if r['curve']==key))
                if file == 'density': color = DENSITY_MAP(DENSITY_NORM(float(next(r['temperature_K'] for r in rows if r['curve']==key))))
                if file == 'heat' and key.startswith('322.5'):
                    style = ':' if '0.51' in key else '-.'
                part=[r for r in rows if r['curve']==key and r['status']=='available' and r['quantity']==quantity]; part.sort(key=lambda r: float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in part],[float(r['value'])*scale for r in part],label=key,color=color,linestyle=style)
            obs=[r for r in read(evidence/f'{file}.csv') if file=='heat' or abs(float(r['mea_mass_fraction'])-.3)<1e-6]
            if file == 'heat':
                conditions = [(313.15,1734000.,8), (322.5,510000.,8), (322.5,1030000.,6)]
                legend = []
                for T, P, count in conditions:
                    sub = [r for r in obs if float(r['T_K'])==T and float(r['P_Pa'])==P]
                    color, style = temperature_style(T)
                    if T == 322.5: style = ':' if P==510000. else '-.'
                    face = color if P==1030000. else 'none'
                    ax.scatter([float(r['loading']) for r in sub], [float(r['observed_kJ_mol']) for r in sub],
                               s=SIZE, marker=temperature_marker(T), facecolors=face, edgecolors=color, zorder=3)
                    legend.append(Line2D([], [], color=color, linestyle=style, marker=temperature_marker(T),
                                         markerfacecolor=face, markersize=SIZE**0.5,
                                         label=f'{T:g} K, {P/1e6:g} MPa'))
                ax.legend(handles=legend, fontsize=9)
            else:  # observations colored by temperature on the scale of the curves; filled if fitted (the CO2-free AMU-DENS-n rows are Amundsen state n)
                fitted = {r['id'].replace('AMU-DENS-', 'Amundsen2009_state_') for r in read(evidence/'fitted-rows.csv') if r['quantity'] == 'phase_density'}
                filled = [r['id'] in fitted for r in obs]
                shade = [DENSITY_MAP(DENSITY_NORM(float(r['T_K']))) for r in obs]
                ax.scatter([float(r['loading']) for r in obs], [float(r['observed_kg_m3']) for r in obs], s=18, facecolors=[c if f else 'none' for c, f in zip(shade, filled)], edgecolors=shade, linewidths=.8, zorder=3)
                handles = ax.get_legend_handles_labels()[0] + [Line2D([], [], ls='', marker='o', color='0.3', label='Measured, fitted'), Line2D([], [], ls='', marker='o', markerfacecolor='none', color='0.3', label='Measured, not fitted')]
                ax.legend(handles=handles, fontsize=9, ncol=2)
                fig.colorbar(matplotlib.cm.ScalarMappable(norm=DENSITY_NORM, cmap=DENSITY_MAP), ax=ax, label='Temperature (K)')
            ax.set(xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel=ylabel); save(fig,name)
        rows=curve('mea-water'); fig,ax=plt.subplots(figsize=(6.8,3.4))
        for key,color in zip(dict.fromkeys(r['curve'] for r in rows),COLORS):
            style = STYLES[list(dict.fromkeys(r['curve'] for r in rows)).index(key)]
            part=[r for r in rows if r['curve']==key and r['quantity']=='bubble temperature' and r['status']=='available']; ax.plot([float(r['liquid_mea_mole_fraction']) for r in part],[float(r['value']) for r in part],color=color,linestyle=style,label=key)
        replay=read(adopted/'replay.json')['rows']; obs=[dict(r['row'],observed=r['observed']) for r in replay if r['group']=='Cai' and r['row']['quantity']=='temperature']; points(ax,[dict(r,x_mea=r['feed']['monoethanolamine']) for r in obs],'x_mea','observed','Measured')
        ax.set(xlabel='Liquid MEA mole fraction',ylabel='Bubble temperature (K)'); ax.legend(); save(fig,'mea-water')

    main()


def render_all():
    outputs = {}
    with matplotlib.rc_context():
        transfer_displays(outputs)
    mea_tables(outputs)
    with matplotlib.rc_context():
        mea_figures(outputs)
    return outputs



def manuscript_sources():
    return sorted([LATEX / "main.tex", LATEX / "supplement.tex", *LATEX.glob("sections/*.tex")])


RES = re.compile(r"\\res\{([a-z0-9-]+)\}")
NUMERAL = re.compile(r"(?<![\w.])(?:(?<!-)[+-])?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?(?!\w|\.\d)")
SCIENTIFIC = re.compile(r"(?P<mantissa>[+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*\\times\s*10\^\{(?P<exponent>[+-]?\d+)\}")
NUMBER_WORDS = "zero one two three four five six seven eight nine ten".split()
NUMBER_WORD = re.compile(
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|"
    r"fifty|sixty|seventy|eighty|ninety|hundred|thousand|million)\b", re.I
)
COMMENT = re.compile(r"(?<!\\)%[^\n]*")
REFERENCE = re.compile(
    r"\\(?:[Cc]ref|[Cc]pageref|pageref|eqref|ref|label|cite\w*|input|includegraphics|begin|end|"
    r"bibliography|bibliographystyle|url|nolinkurl|res|orcidlink|orcid|author|affil|affiliation|email|ead|cormark|thanks|"
    r"date|runningauthor|correspondingauthor|hypersetup|usepackage|documentclass|newcolumntype|newcommand|renewcommand|"
    r"providecommand|def|gdef|edef|xdef|setlength|addtolength|setcounter)\b\*?"
)
GROUPS = re.compile(r"[\s{}\[\]\\]")
LAYOUT = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:pt|pc|in|cm|mm|em|ex|bp|sp|dd|cc)\b"
    r"|\b\d+(?:\.\d+)?\\(?:textwidth|linewidth|columnwidth|textheight|baselineskip)\b"
)
INDEX = re.compile(r"(?<=[A-Za-z0-9}\]])[_^](?:\{[^}]*\}|[0-9]+)")


def manuscript_body(source):
    marker = r"\begin{document}"
    source = COMMENT.sub(lambda match: " " * len(match[0]), source)
    start = source.find(marker)
    if start < 0:
        return source
    return re.sub(r"[^\n]", " ", source[:start + len(marker)]) + source[start + len(marker):]


def mask_syntax(text):
    masked = list(text)
    for match in REFERENCE.finditer(text):
        end = match.end()
        definition = match[0].lstrip("\\").startswith(
            ("def", "gdef", "edef", "xdef", "newcommand", "renewcommand", "providecommand")
        )
        if definition:
            prefix = re.match(r"\s*\\[a-zA-Z@:_]+(?:#\d+)*", text[end:])
            if prefix:
                end += prefix.end()
        while end < len(text):
            spaces = re.match(r"\s*", text[end:])
            start = end + spaces.end()
            if start == len(text) or text[start] not in "{[":
                break
            # Only definitions and length assignments take consecutive braced arguments.
            depth = 1
            closing = "}" if text[start] == "{" else "]"
            for token in GROUPS.finditer(text, start + 1):
                if token[0] == text[start] and text[token.start() - 1] != "\\":
                    depth += 1
                if token[0] == closing and text[token.start() - 1] != "\\":
                    depth -= 1
                    if depth == 0:
                        end = token.end()
                        break
            else:
                break
            if closing == "}" and not definition and match[0] not in (
                r"\newcolumntype", r"\setlength", r"\addtolength", r"\setcounter"
            ):
                if match[0] == r"\author":
                    metadata = re.match(r"\s*\[orcid=[^\]]+\]", text[end:])
                    if metadata:
                        end += metadata.end()
                break
        masked[match.start():end] = re.sub(r"[^\n]", " ", text[match.start():end])
    filtered = "".join(masked)
    for syntax in (LAYOUT, INDEX):
        filtered = syntax.sub(lambda match: " " * len(match[0]), filtered)
    return filtered


def expand(text, values):
    return RES.sub(lambda match: values[match[1]]["value"], text)


def visible(body):
    return COMMENT.sub("", body).split()


def result_values():
    values = {}

    def add(name, record, key, value):
        values[name] = dict(value=value, record=record, key=key)

    starts = {name: read(STUDY + f"results/{name}/selection.json")["selected"] for name in ("MEA", "AMP_free")}
    fit_record = STUDY + f"results/MEA/{starts['MEA']}.json.gz"
    key = "endpoint.parameters.components.carbamate-anion.coefficients.dispersion_energy_over_k.value.magnitude"
    endpoint = read(fit_record)["endpoint"]
    component = next(c for c in endpoint["parameters"]["components"] if c["component_id"] == "carbamate-anion")
    energy = next(c["value"]["magnitude"] for c in component["coefficients"]
                  if c["identity"] == "component/carbamate-anion/dispersion_energy_over_k")
    for name in (
        "dea-carbamate-dispersion-energy-supplement",
        "amp-carbamate-dispersion-energy-supplement",
        "amp-carbamate-dispersion-energy-transfer-parameters",
        "amp-carbamate-dispersion-energy-transfer-sensitivity",
        "mea-carbamate-dispersion-energy-species-table",
    ):
        add(name, fit_record, key, f"{energy:.4f}")
    record = STUDY + "results/DEA/screen/selected/declared/summary.json.gz"
    count = sum(any(a["confirmed"] for a in row["attempts"]) for row in read(record)["classifications"])
    add("dea-confirmed-splits-abstract", record, "classifications[].attempts[].confirmed", NUMBER_WORDS[count])
    record = STUDY + f"results/AMP_free/controls/{starts['AMP_free']}.json.gz"
    measured = [row for key, row in read(record)["rows"].items() if key != "worked-state"]
    count = sum(not row["value"]["search"]["no_descent_in_trial_set"] for row in measured)
    add("amp-measured-control-descents-abstract", record,
        "rows[measured].value.search.no_descent_in_trial_set", NUMBER_WORDS[count])
    record = STUDY + "results/E/MEA/replay.json.gz"
    reported_aard = {
        "mea-fitted-pressure": (record, "summary.pressure.legacy.AARD_percent",
                                read(record)["summary"]["pressure"]["legacy"]["AARD_percent"])
    }
    record = STUDY + "results/MDEA/properties.json.gz"
    mdea_rows = read(record)["rows"]
    for label, group in (("mdea-fitted-pressure", "Kuranov"), ("mdea-ermatchkov-pressure", "Ermatchkov")):
        rows = [row for row in mdea_rows if row["group"] == group and row["unit"] == "Pa"]
        reported_aard[label] = (record, f"rows[{group},Pa].observed,value", stats(rows, predicted="value")["AARD_percent"])
    for label, filename, groups in (
        ("dea-fitted-pressure", "DEA/property-comparisons/selected.json.gz", ("Lawson", "SeoHong", "Lal")),
        ("amp-fitted-pressure", "AMP_free/properties.json.gz", ("loaded-pressure", "hartono-2021-supplemental", "tong")),
    ):
        record = STUDY + "results/" + filename
        rows = [row for row in read(record)["rows"] if row["role"] == "fitted" and row["group"] in groups]
        key = "rows[fitted," + "|".join(groups) + "].observed,value"
        reported_aard[label] = (record, key, stats(rows, predicted="value")["AARD_percent"])
    locations = {
        "mea-fitted-pressure": ("abstract", "introduction", "mea-results", "transfer-comparison", "conclusion", "reference-comparison"),
        "dea-fitted-pressure": ("abstract", "introduction", "dea-results", "conclusion", "reference-comparison"),
        "mdea-fitted-pressure": ("abstract", "introduction", "mdea-results", "transfer-comparison", "conclusion",
                                 "reference-comparison", "literature-subsets"),
        "amp-fitted-pressure": ("abstract", "introduction", "amp-results", "conclusion", "reference-comparison", "slope-comparison"),
        "mdea-ermatchkov-pressure": ("abstract", "mdea-results", "transfer-comparison", "literature-comparison", "reference-comparison"),
    }
    for quantity, occurrences in locations.items():
        record, key, value = reported_aard[quantity]
        for occurrence in occurrences:
            add(f"{quantity}-aard-{occurrence}", record, key, f"{value:.2f}")

    record = "analyses/round_3/results/q2.json"
    scores = read(record)["scores"]
    for source, group in (("hartono", "hartono-2021"), ("tong", "tong-2012")):
        for fit in ("free", "fixed"):
            value = scores[group][fit]["AARD_percent"]
            key = f"scores.{group}.{fit}.AARD_percent"
            add(f"amp-first-data-{fit}-{source}-aard-supplement", record, key, f"{value:.2f}")
            if fit == "free":
                for passage in ("first-fit", "split-diagnostic"):
                    add(f"amp-first-data-free-{source}-aard-{passage}", record, key, f"{value:.1f}")

    record = "analyses/round_3/results/q6.json"
    diagnostics = read(record)["split"]["diagnostics"]
    for start_set, key in (("all", "trial_minimum"), ("vapor-connected", "vapor_connected_minimum")):
        add(f"amp-worked-state-{start_set}-minimum-tangent-distance", record,
            f"split.diagnostics.{key}", f"{diagnostics[key]:.4f}")

    for fit, occurrences in (("main", ("free-starts", "slope-comparison")),
                             ("slope-150", ("slope-comparison",))):
        record = f"analyses/round_5/results/A/original-{fit}.json.gz"
        cost = read(record)["cost"]
        for passage in occurrences:
            add(f"amp-first-data-{fit}-objective-{passage}", record, "cost", f"{cost:.4f}")
        pressures = [row["prediction"] for row in read(record)["original"]["rows"] if row["group"] == "loaded-pressure"]
        deviation = stats(pressures, predicted="value")["AARD_percent"]
        for passage in ("first-fit", "supplement") if fit == "main" else ("supplement",):
            add(f"amp-first-data-{fit}-loaded-pressure-aard-{passage}", record,
                "original.rows[loaded-pressure].prediction: AARD", f"{deviation:.1f}")

    for name, label, occurrences in (
        ("MEA", "mea", (("starts", 3), ("cai-weight", 2), ("reference-comparison", 3), ("restrictions", 3))),
        ("DEA", "dea", (("starts", 3), ("penalty", 3), ("reference-comparison", 3))),
        ("MDEA", "mdea", (("continuation", 3), ("basin-comparison", 3), ("reference-comparison", 3))),
        ("AMP_free", "amp", (("starts", 3), ("slope-comparison", 3), ("reference-comparison", 3))),
        ("AMP_fixed", "amp-fixed-slope", (("starts", 3), ("slope-comparison", 3), ("methods", 2))),
    ):
        record = STUDY + f"results/{name}/selection.json"
        selection = read(record)
        for passage, digits in occurrences:
            add(f"{label}-selected-objective-{passage}", record, "cost", f"{selection['cost']:.{digits}f}")
        if name == "AMP_fixed":
            cost = selection["attempts"]["C"]["cost"]
            add("amp-fixed-slope-alternate-basin-objective", record, "attempts.C.cost", f"{cost:.3f}")
            add("amp-fixed-slope-alternate-basin-objective-methods", record, "attempts.C.cost", f"{cost:.2f}")

    record = STUDY + "results/MDEA/A.json.gz"
    fit = read(record)
    for stage, key, value, digits in (
        ("first", "previous_stage.previous_stage.replay.cost", fit["previous_stage"]["previous_stage"]["replay"]["cost"], 3),
        ("second", "previous_stage.replay.cost", fit["previous_stage"]["replay"]["cost"], 5),
        ("third", "replay.cost", fit["replay"]["cost"], 5),
    ):
        add(f"mdea-{stage}-fit-stage-objective", record, key, f"{value:.{digits}f}")
    record = STUDY + "results/MDEA/stationarity/A-descent-continuation.json.gz"
    add("mdea-descent-restart-objective", record, "replay.cost", f"{read(record)['replay']['cost']:.5f}")
    record = STUDY + "results/MDEA/LHS-53.json.gz"
    cost = read(record)["replay"]["cost"]
    for passage in ("draw-accounting", "basin-comparison", "calibration-methods", "property-spread"):
        add(f"mdea-alternate-basin-objective-{passage}", record, "replay.cost", f"{cost:.1f}")

    record = STUDY + "results/display-replays/caloric-and-species.json.gz"
    reference_state = read(record)["reference_state"]
    for quantity, key in (("integral-heat", "heat_kJ_mol"), ("equilibrium-heat-capacity", "cp_J_mol_K")):
        add(f"mea-reference-state-{quantity}", record, f"reference_state.{key}", f"{reference_state[key]:.3f}")
    record = STUDY + f"results/MEA/{starts['MEA']}.json.gz"
    rows = read(record)["replay"]["rows"]
    cai_share = 100 * math.fsum(row["cost"] for row in rows if row["group"] == "Cai") / math.fsum(
        row["cost"] for row in rows
    )
    add("mea-cai-objective-share-methods", record, "replay.rows[Cai].cost relative to all costs", f"{cai_share:.1f}")

    tracking = "analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/F4/"
    objective_record = tracking + "objective-information.json.gz"
    objective = read(objective_record)["result"]
    for passage in ("cai-weight", "reference-comparison", "restrictions"):
        add(f"mea-tracking-objective-{passage}", objective_record, "result.rss / 2", f"{objective['rss'] / 2:.3f}")
    record = tracking + "objective-contributions.csv"
    cai = {row["observable"]: float(row["cost"]) for row in read(record) if row["group"] == "Cai"}
    add("mea-tracking-cai-temperature-objective", record, "Cai,temperature: cost", f"{cai['temperature']:.3f}")
    add("mea-tracking-cai-vapor-fraction-objective", record, "Cai,['water']: cost", f"{cai["['water']"]:.3f}")
    add("mea-tracking-cai-objective-share", record, "Cai: cost / objective", f"{200 * math.fsum(cai.values()) / objective['rss']:.2f}")

    record = tracking + "uncertainty/prediction-bands.csv"
    pressures = [row for row in read(record) if row["group"] == "common149: partial_pressure"]
    relative = [100 * objective["SE_multiplier"] * float(row["SE_bound_fixed"]) / float(row["value"])
                for row in pressures]
    for passage, digits in (("results", 1), ("supplement", 2)):
        add(f"mea-tracking-fitted-pressure-minimum-relative-se-{passage}", record,
            "common149: partial_pressure: minimum SE_bound_fixed / value times SE_multiplier",
            f"{min(relative):.{digits}f}")
        add(f"mea-tracking-fitted-pressure-maximum-relative-se-{passage}", record,
            "common149: partial_pressure: maximum SE_bound_fixed / value times SE_multiplier", f"{max(relative):.1f}")

    record = STUDY + "results/AMP_fixed/properties.json.gz"
    rows = [row for row in read(record)["rows"] if row["role"] == "fitted"
            and row["group"] in ("loaded-pressure", "hartono-2021-supplemental", "tong")]
    add("amp-fixed-slope-loaded-pressure-aard", record,
        "rows[fitted,loaded-pressure|hartono-2021-supplemental|tong].observed,value",
        f"{stats(rows, predicted='value')['AARD_percent']:.2f}")

    record = DEA_SALT_SUMMARY
    add("dea-salt-anchored-common-objective-transfer", record, "expanded_objective",
        f"{read(record)['expanded_objective']:.2f}")
    record = "analyses/round_7/results/F/selection.json.gz"
    add("dea-tracking-expanded-common-objective-transfer", record, "selected[0]",
        f"{read(record)['selected'][0]:.2f}")
    record = "analyses/round_3/results/q7-summary.json"
    add("amp-first-data-recall-searched-negative-states", record, "searched_negatives",
        str(read(record)["searched_negatives"]))
    add("amp-first-data-recall-states-supplement", record, "searched", str(read(record)["searched"]))

    record = STUDY + "results/AMP_free/screen/selected/native/summary.json.gz"
    screen = read(record)
    for passage in ("abstract", "conclusion", "conclusion-refit", "figure-caption", "transfer", "supplement-slope"):
        add(f"amp-reported-screen-states-{passage}", record, "tally.states", str(screen["tally"]["states"]))
    grid = sum(row["key"].startswith("grid:") for row in screen["rows"])
    for passage in ("transfer", "supplement"):
        add(f"amp-reported-screen-grid-states-{passage}", record, "rows[grid].count", str(grid))
        add(f"amp-reported-screen-measured-states-{passage}", record, "rows[measurement-derived].count",
            str(len(screen["rows"]) - grid))

    record = "analyses/amp_transfer/results/retransfer-412-f2-05e94210/main/phase-classification-1.json.gz"
    instabilities = read(record)["states"]
    split_states = [row for row in instabilities if any(attempt["confirmed"] for attempt in row["attempts"])]
    confirmed = len(split_states)
    for passage in ("figure-caption", "transfer", "supplement"):
        add(f"amp-first-data-confirmed-splits-{passage}", record, "states[].attempts[].confirmed", str(confirmed))
        add(f"amp-first-data-unconfirmed-descents-{passage}", record, "states without a confirmed attempt",
            str(len(instabilities) - confirmed))
    temperatures = [row["temperature_K"] for row in split_states]
    for bound, fun in (("minimum", min), ("maximum", max)):
        add(f"amp-first-data-{bound}-instability-temperature-supplement", record,
            f"states[confirmed splits].temperature_K: {bound}", f"{fun(temperatures):.2f}")
    endpoint = read(STUDY + f"results/AMP_free/{starts['AMP_free']}.json.gz")["endpoint"]
    species = [row["component_id"] for row in endpoint["parameters"]["components"]]
    co2, amp = species.index("carbon-dioxide"), species.index("aminomethylpropanol")
    loading = min(row["feed_mol"][co2] / row["feed_mol"][amp] for row in split_states)
    add("amp-first-data-minimum-confirmed-split-loading", record,
        "states[confirmed splits].feed_mol carbon-dioxide / aminomethylpropanol: min", f"{loading:.3f}")
    record = STUDY + "results/AMP_free/screen/selected/native/state-inventory.json.gz"
    maximum = max(row["T_K"] for row in read(record)["rows"])
    add("amp-reported-screen-maximum-temperature", record, "rows[].T_K: max", f"{maximum:.2f}")
    record = "analyses/round_3/results/q7-summary.json"
    for passage in ("transfer", "supplement-first-fit"):
        add(f"amp-first-data-screen-states-{passage}", record, "total", str(read(record)["total"]))
    record = "analyses/round_8/results/amp-six-states.json.gz"
    controls = read(record)["quantities"]["rows"]
    for passage in ("caption-diamonds", "caption-observations", "abstract", "conclusion-controls",
                    "conclusion-confirmed", "transfer-controls", "transfer-confirmed", "transfer-interpretation",
                    "transfer-claim", "supplement",
                    "supplement-endpoint-spread"):
        add(f"amp-first-data-measured-splits-{passage}", record, "quantities.rows.count", NUMBER_WORDS[len(controls)])
    add("amp-first-data-measured-splits-supplement-positions", record,
        "quantities.rows.count", NUMBER_WORDS[len(controls)].capitalize())
    record = PHASE_SUMMARY
    outcomes = read(record)["amp_outcomes"]
    for label, count in (("vapor-descents", sum(row["outcome"] != "No resolved descent" for row in outcomes.values())),
                         ("no-descent", sum(row["outcome"] == "No resolved descent" for row in outcomes.values()))):
        for passage in ("caption", "conclusion", "transfer-description", "transfer-interpretation"):
            add(f"amp-reported-measured-controls-{passage}-{label}", record, "amp_outcomes[].outcome", NUMBER_WORDS[count])
        if label == "no-descent":
            add("amp-reported-measured-controls-abstract-no-descent", record, "amp_outcomes[].outcome", NUMBER_WORDS[count])
        else:
            add("amp-reported-measured-controls-transfer-qualification-vapor-descents", record,
                "amp_outcomes[].outcome", NUMBER_WORDS[count])
    for label, outcome in (("qualified-vapor", "L+V passed; L+L unresolved"),
                           ("unqualified-vapor", "Vapor-directed; root unqualified")):
        count = sum(row["outcome"] == outcome for row in outcomes.values())
        for passage in ("transfer-description", "transfer-interpretation"):
            add(f"amp-reported-measured-controls-{passage}-{label}", record,
                f"amp_outcomes[outcome={outcome}].count", NUMBER_WORDS[count])
    vapor = [row for row in read(record)["amp_controls"]["rows"]
             if row.get("reported_liquid_vapor_gate") and row["key"] in outcomes]
    for label, source in (("hartono", "hartono-2021"), ("tong", "tong-2012")):
        rows = [row for row in vapor if row["key"].startswith(source)]
        add(f"amp-reported-measured-controls-{label}-vapor-descents", record,
            f"amp_controls.rows[{source},descents].count", NUMBER_WORDS[len(rows)])
        if label == "tong":
            row, = rows
            for label, key in (("measured-pressure", "P_Pa"), ("bubble-pressure", "reported_bubble_Pa")):
                add(f"amp-tong-descending-state-{label}", record,
                    f"amp_controls.rows[{row['key']}].{key}/1e6", f"{row[key] / 1e6:.5f}")

    record = FIT_SUMMARY
    fitting = read(record)
    draws = fitting["mdea_start_counts"]
    for passage in ("abstract", "conclusion", "transfer", "methods", "supplement"):
        add(f"mdea-evaluable-drawn-starts-{passage}", record, "mdea_start_counts.evaluable.count",
            NUMBER_WORDS[len(draws["evaluable"])])
        if passage != "supplement":
            add(f"mdea-planned-drawn-starts-{passage}", record, "mdea_start_counts.drawn", str(draws["drawn"]))
    add("mdea-skipped-drawn-starts-methods", record, "mdea_start_counts.untested_draws.count",
        NUMBER_WORDS[len(draws["untested_draws"])])
    add("mdea-tested-drawn-starts-methods", record, "mdea_start_counts.tested", str(draws["tested"]))
    add("mdea-replacement-drawn-starts-supplement", record, "mdea_start_counts.replacement_draws",
        str(draws["replacement_draws"]))
    rms_distances = [distance for design in ("MEA", "DEA", "AMP_free")
                     for pair, distance in fitting["start_distances"][design].items()
                     if all(fitting["attempts"][design][key]["status"] == "converged" for key in pair.split("/"))]
    rms_key = "start_distances[MEA,DEA,AMP_free]: converged pairs"
    for passage in ("methods", "supplement"):
        add(f"reported-starts-minimum-rms-distance-{passage}", record, rms_key + ": min", f"{min(rms_distances):.2f}")
    add("reported-starts-maximum-rms-distance-supplement", record, rms_key + ": max", f"{max(rms_distances):.2f}")

    record = GIBBS_DERIVATIVES
    checks = {(row["state"], row["comparison"]): row for row in read(record)["rows"]}
    relative_max = max(abs(checks[f"selected-{name}", "volume"]["relative_error"])
                       for name in ("MEA", "DEA", "AMP_free", "MDEA"))
    mantissa, exponent = f"{relative_max:.1e}".split("e")
    for passage in ("abstract", "conclusion"):
        add(f"gibbs-derivative-maximum-relative-error-{passage}", record,
            "rows[selected,volume].relative_error: maximum absolute", rf"{mantissa}\times10^{{{int(exponent)}}}")
    for amine, design, scale, digits in (
        ("mea", "MEA", 1000, 3), ("dea", "DEA", 1000, 3),
        ("amp", "AMP_free", 1000, 2), ("mdea", "MDEA", 1000000, 3),
    ):
        state = f"selected-{design}"
        volume = checks[state, "volume"]
        for passage in ("theory", "supplement"):
            add(f"{amine}-gibbs-derivative-bubble-pressure-{passage}", record,
                f"rows[{state},volume].pressure_Pa/{scale}", f"{volume['pressure_Pa'] / scale:.{digits}f}")
        mantissa, exponent = f"{volume['relative_error']:.2e}".split("e")
        relative = rf"{mantissa}\times10^{{{int(exponent)}}}"
        add(f"{amine}-gibbs-derivative-relative-error-supplement", record,
            f"rows[{state},volume].relative_error", relative)
        if amine in ("mea", "dea"):
            add(f"{amine}-gibbs-derivative-relative-error-theory", record,
                f"rows[{state},volume].relative_error", ("+" if amine == "mea" else "") + relative)
        estimate = volume["relative_estimated_error"]
        add(f"{amine}-gibbs-derivative-relative-resolution-supplement", record,
            f"rows[{state},volume].relative_estimated_error", f"{estimate:.{'3' if amine in ('mea', 'dea') else '4'}f}")
        places = 1 if amine in ("mea", "dea") else 2
        passages = ("theory", "conclusion", "abstract") if amine == "mea" else (
            ("theory", "conclusion") if amine == "dea" else ("theory", "abstract") if amine == "mdea" else ("theory",))
        for passage in passages:
            add(f"{amine}-gibbs-derivative-resolution-percent-{passage}", record,
                f"100 * rows[{state},volume].relative_estimated_error", f"{100 * estimate:.{places}f}")
        caloric = checks[state, "Eq. 12"]
        add(f"{amine}-gibbs-helmholtz-enthalpy-discrepancy-supplement", record,
            f"rows[{state},Eq. 12].signed_error*1000", f"{caloric['signed_error'] * 1000:.2f}")
        add(f"{amine}-gibbs-helmholtz-enthalpy-resolution-supplement", record,
            f"rows[{state},Eq. 12].estimated_error*1000", f"{caloric['estimated_error'] * 1000:.0f}")

    record = PROPERTY_SUMMARY
    property_summary = read(record)
    water = property_summary["water_calibration"]
    for passage in ("fit-input", "fit-deviations"):
        add(f"water-fit-vapor-pressure-temperature-count-{passage}", record,
            "water_calibration.fitted_rows.psat", str(water["fitted_rows"]["psat"]))
    midpoint = next(row for row in water["metrics"]
                    if row["record"] == "lambda-0.1-A" and row["grid"] == "staggered" and row["quantity"] == "psat")
    add("water-fit-staggered-temperature-count", record, "water_calibration.metrics[staggered,psat].evaluated_rows",
        str(midpoint["evaluated_rows"]))
    diameter = "component/water/segment_diameter/constant-plus-sum-of-exponentials/constant"
    add("water-fit-segment-diameter-offset-supplement", record,
        f"water_calibration.coefficients.{diameter}", f"{water['coefficients'][diameter]:.7f}")
    for metric in water["metrics"]:
        if metric["record"] != "lambda-0.1-A":
            continue
        quantity = metric["quantity"]
        grid = metric["grid"]
        label = {"psat": "vapor-pressure", "rho": "liquid-density",
                 "saturated_liquid_rho": "saturated-liquid-density", "cp": "heat-capacity"}[quantity]
        digits = 2 if quantity == "cp" else 3
        fields = [("mean", digits)]
        if grid == "primary":
            fields.append(("max", 2 if quantity in ("psat", "cp") else 3))
        for score, places in fields:
            field = score + "_percent"
            key = f"water_calibration.metrics[lambda-0.1-A,{grid},{quantity}].{field}"
            add(f"water-fit-{grid}-{label}-{score}-deviation", record, key, f"{metric[field]:.{places}f}")
    for cohort in ("Kuranov", "Carson"):
        scores = property_summary["spread"]["MDEA"]["groups"][cohort]["endpoint_AARD_percent"]
        add(f"mdea-alternate-basin-{cohort.lower()}-aard-transfer", record,
            f"spread.MDEA.groups.{cohort}.endpoint_AARD_percent.LHS-53", f"{scores['LHS-53']:.0f}")

    record = PHASE_SUMMARY
    phase_results = read(record)
    assigned = sum(row["pressure_basis"] == "assigned" for row in phase_results["mdea_distinct_states"])
    for passage in ("transfer", "supplement"):
        add(f"mdea-assigned-pressure-distinct-descents-{passage}", record,
            "mdea_distinct_states[assigned].count", str(assigned))
    for passage in ("transfer-search", "transfer-detections", "supplement"):
        add(f"mdea-descents-all-{passage}", record, "mdea_descent_counts: sum",
            str(sum(phase_results["mdea_descent_counts"].values())))
    mea = phase_results["mea_search"]
    for passage in ("transfer", "supplement"):
        add(f"mea-liquid-grid-requests-{passage}", record, "mea_search.liquid_grid.attempted",
            str(mea["liquid_grid"]["attempted"]))
        add(f"mea-liquid-grid-incomplete-{passage}", record,
            "mea_search.liquid_grid.attempted minus completed",
            NUMBER_WORDS[mea["liquid_grid"]["attempted"] - mea["liquid_grid"]["completed"]])
        add(f"mea-measured-state-search-requests-{passage}", record, "mea_search.measured.attempted",
            str(mea["measured"]["attempted"]))
        add(f"mea-census-two-phase-parent-count-{passage}", record, "mea_search.census.outcomes.passed-two-phase",
            str(mea["census"]["outcomes"]["passed-two-phase"]))
    for passage in ("transfer-all", "transfer-outcomes", "supplement"):
        add(f"mea-liquid-vapor-census-requests-{passage}", record, "mea_search.census.attempted",
            str(mea["census"]["attempted"]))
    add("mea-measured-state-search-completed", record, "mea_search.measured.completed",
        str(mea["measured"]["completed"]))
    for population, count in mea["liquid_grid"]["populations"].items():
        add(f"mea-liquid-grid-{population}-requests", record, f"mea_search.liquid_grid.populations.{population}", str(count))

    record = "analyses/mdea_mea_workflow/results/shared-bicarbonate-417/profile.json.gz"
    profile = read(record)
    candidates = [profile["searches"][repr(case["k"])] for case in profile["selected"].values()]
    coverage = [(case["grid"]["states"] + case["offset"]["states"], case["census"]["states"]) for case in candidates]
    (liquid_grid, census), = set(coverage)
    add("mea-bicarbonate-profile-liquid-grid-requests", record, "searches per selected value: grid.states + offset.states",
        str(liquid_grid))
    add("mea-bicarbonate-profile-liquid-vapor-census-requests", record, "searches per selected value: census.states",
        str(census))

    record = STUDY + "results/DEA/screen/selected/declared/summary.json.gz"
    dea_screen = read(record)
    grid = sum(row["key"].startswith("grid:") for row in dea_screen["rows"])
    for label, key, count in (
        ("grid-requests", "rows[grid].count", grid),
        ("measurement-requests", "rows[measurement-derived].count", len(dea_screen["rows"]) - grid),
        ("transfer-requests", "tally.states", dea_screen["tally"]["states"]),
        ("transfer-completed", "tally.available", dea_screen["tally"]["available"]),
        ("supplement-completed", "tally.available", dea_screen["tally"]["available"]),
    ):
        add(f"dea-phase-search-{label}", record, key, str(count))
    add("dea-phase-search-detected-instabilities", record, "tally.descent",
        NUMBER_WORDS[dea_screen["tally"]["descent"]])
    count = sum(any(a["confirmed"] for a in row["attempts"]) for row in dea_screen["classifications"])
    for passage in ("transfer", "supplement"):
        add(f"dea-confirmed-phase-splits-{passage}", record, "classifications[].attempts[].confirmed: count",
            NUMBER_WORDS[count])

    record = STUDY + "results/DEA/property-comparisons/selected.json.gz"
    fitted = [row for row in read(record)["rows"] if row["role"] == "fitted"]
    carson = [row for row in fitted if row["group"] == "Carson"]
    for label, fraction in (("intermediate", "0.20"), ("highest", "0.30")):
        count = sum(row["row"]["DEA_mass_fraction"] == fraction for row in carson)
        add(f"dea-carson-{label}-concentration-observations-caption", record,
            f"rows[Carson,fitted,{fraction}].count", str(count))
    for reaction, label in (("carbamate-hydrolysis", "r4"), ("DEA-dissociation", "r5")):
        outside = sum(row["unit"] == "Pa" and row["outside_ranges"].get(reaction, False) for row in fitted)
        add(f"dea-fitted-pressure-outside-{label}-range", record,
            f"rows[fitted,Pa].outside_ranges.{reaction}: count", str(outside))
    record = STUDY + "results/display-replays/mea-comparisons.json.gz"
    kim = read(record)["kim_2007"]
    hot = [row for row in kim if row["T_K"].startswith("393.15") and row["interval_status"] == "available"]
    add("mea-kim-svendsen-hot-interval-count-results", record, "kim_2007[393.15 K,available].count", str(len(hot)))
    low = sum(float(row["previous_loading"]) < 0.1 for row in kim)
    add("hong-kim-svendsen-intervals-below-loading-window", record, "kim_2007[previous_loading < 0.1].count", str(low))
    record = "analyses/mea_parameter_bundle/results/same-data-comparison/hong-2027/checks.json"
    figure = read(record)["figure_5"]
    for pathway in ("carbamate", "bicarbonate"):
        add(f"hong-pathway-{pathway}-maximum-fraction-difference", record,
            f"figure_5.{pathway}.abs_quantiles.100", f"{figure[pathway]['abs_quantiles']['100']:.4f}")
    record = "analyses/round_5/results/A/"
    rise = read(record + "original-slope-150.json.gz")["cost"] - read(record + "original-main.json.gz")["cost"]
    add("amp-first-data-slope-fixed-objective-rise", record + "original-slope-150.json.gz",
        "cost minus original-main.json.gz cost", f"{rise:.2f}")

    record = STUDY + "results/display-replays/mea-comparisons.json.gz"
    carbonate = read(record)["carbonate_share"]
    ratios = [row["value"] / row["observed"] for row in carbonate]
    geometric = math.exp(fsum(map(math.log, ratios)) / len(ratios))
    for passage in ("mea-results", "transfer"):
        add(f"mea-carbonate-share-geometric-mean-{passage}", record,
            "carbonate_share[].value / observed: geometric mean", f"{geometric:.3f}")
    add("mea-carbonate-share-aard-results", record, "carbonate_share[].value/observed: AARD",
        f"{100 * fsum(abs(ratio - 1) for ratio in ratios) / len(ratios):.2f}")

    record = "analyses/mea_parameter_bundle/results/objective-weights-420/MEA/standard-errors.csv"
    standard_errors = {row["parameter"]: float(row["native_stage_SE"]) for row in read(record)}
    for label, ion in (("carbamate", "carbamate-anion"), ("protonated-mea", "protonated-monoethanolamine")):
        parameter = f"pair/{ion}/water/k_ij"
        add(f"mea-shared-{label}-water-conditional-se-before-fixing", record,
            f"parameter={parameter}: native_stage_SE", f"{standard_errors[parameter]:.2f}")
    parameter = "pair/bicarbonate-anion/water/k_ij"
    for passage in ("theory", "supplement"):
        add(f"mea-shared-bicarbonate-water-conditional-se-{passage}", record,
            f"parameter={parameter}: native_stage_SE", f"{standard_errors[parameter]:.2f}")

    record = "analyses/amines/results/shared/deposit/reviewer-package.json"
    package = read(record)
    add("reproducibility-package-size", record, "bytes / 1000000", f"{package['bytes'] / 1e6:.2f}")
    add("reproducibility-package-checksum-covered-files", record, "checksum_entries",
        str(package["checksum_entries"]))

    record = STUDY + "results/AMP_free/properties.json.gz"
    amp_pressures = [row for row in read(record)["rows"]
                     if row["role"] == "fitted" and row["group"] in ("loaded-pressure", "hartono-2021-supplemental", "tong")]
    n_pressure = len(amp_pressures)
    key = "rows[fitted,loaded-pressure|hartono-2021-supplemental|tong].count"
    for passage in ("introduction", "transfer", "conclusion", "residual-figure-caption", "extended-data", "slope-comparison"):
        add(f"amp-reported-loaded-pressure-count-{passage}", record, key, str(n_pressure))
    add("amp-refit-added-loaded-pressures-abstract", record,
        "rows[fitted,hartono-2021-supplemental|tong].count",
        str(sum(row["group"] != "loaded-pressure" for row in amp_pressures)))

    record = STUDY + f"results/AMP_free/{starts['AMP_free']}.json.gz"
    n_fit = len(read(record)["replay"]["rows"])
    for passage in ("transfer", "methods", "supplement"):
        add(f"amp-reported-objective-row-count-{passage}", record, "replay.rows.count", str(n_fit))
    record = "analyses/round_5/results/A/original-main.json.gz"
    add("amp-first-data-objective-row-count-supplement", record, "original.rows[fitted].count",
        str(sum(row["role"] == "fitted" for row in read(record)["original"]["rows"])))

    record = STUDY + "results/MDEA/properties.json.gz"
    rows = [row for row in read(record)["rows"] if row["group"] == "Ermatchkov" and row["unit"] == "Pa"]
    for passage in ("abstract", "mdea-results", "shared-comparison", "literature", "weighting"):
        add(f"mdea-ermatchkov-partial-pressure-count-{passage}", record, "rows[Ermatchkov,Pa].count", str(len(rows)))
    rows = [row for row in read(record)["rows"] if row["group"] == "Kuranov" and row["role"] == "fitted"]
    for passage in ("introduction", "conclusion", "relative-weight", "mdea-results", "shared-comparison",
                    "weighting", "normalized-weight", "historical-comparison", "residual-figure-caption", "supplement-weighting",
                    "published-fit-coverage", "literature-subsets"):
        add(f"mdea-fitted-kuranov-pressure-count-{passage}", record, "rows[Kuranov,fitted].count", str(len(rows)))

    record = STUDY + "results/DEA/property-comparisons/selected.json.gz"
    dea_pressures = [row for row in read(record)["rows"] if row["unit"] == "Pa" and row["role"] == "fitted"]
    for passage in ("introduction", "conclusion", "dea-results", "residual-figure-caption", "expanded-comparison", "range-check"):
        add(f"dea-fitted-partial-pressure-count-{passage}", record, "rows[Pa,fitted].count", str(len(dea_pressures)))

    record = STUDY + "results/E/MEA/replay.json.gz"
    hot = read(record)["summary"]["pressure"]["hot_published"]
    for passage in ("supplement", "transfer"):
        add(f"mea-hot-pressure-count-{passage}", record, "summary.pressure.hot_published.attempted", str(hot["attempted"]))
    add("mea-hot-pressure-aard-transfer", record, "summary.pressure.hot_published.AARD_percent", f"{hot['AARD_percent']:.2f}")

    record = "analyses/amp_transfer/results/retransfer-412-f2-05e94210/diagnosis/f2-probes.json"
    probes = read(record)
    for passage, case, key in (
        ("dissociation-sensitivity", "dissociation-353", "states"),
        ("hydrolysis-sensitivity", "hydrolysis-353", "descent"),
        ("carbamate-diameter-sensitivity", "carbamate-diameter-floor", "descent"),
        ("sensitivity-baseline", "base", "descent"),
    ):
        add(f"amp-first-data-instabilities-{passage}", record, f"{case}.{key}", str(probes[case][key]))
    record = "analyses/round_3/results/q7-summary.json"
    add("amp-first-data-detected-instabilities-supplement", record, "archived_positive", str(read(record)["archived_positive"]))
    add("amp-first-data-recovered-instabilities-supplement", record, "recovered", str(read(record)["recovered"]))

    record = "analyses/mea_parameter_bundle/results/same-data-comparison/hong-2027/checks.json"
    hong = read(record)
    add("hong-reconstructed-weight-nodes", record, "weight_knots_exact", str(hong["weight_knots_exact"]))
    add("hong-checked-weight-nodes", record, "grid_stability: total", str(sum(hong["grid_stability"].values())))

    record = "analyses/mdea_mea_workflow/results/bounded-binary-411/critical-k.json"
    count = len(read(record)["rows"])
    for passage in ("transfer", "figure-caption", "supplement"):
        add(f"mdea-binary-gap-tested-temperatures-{passage}", record, "rows.count", str(count))

    record = PHASE_SUMMARY
    dea = read(record)["dea_controls"]
    worked = next(row for row in dea["rows"] if row["key"] == dea["worked_state"])
    phases = sorted(worked["phases"], key=lambda phase: phase["density_kg_m3"])
    loading = min(row["loading"] for row in dea["rows"])
    for passage in ("transfer", "supplement"):
        add(f"dea-minimum-confirmed-split-loading-{passage}", record,
            "dea_controls.rows[].loading: min", f"{loading:.2f}")
    for label, phase in zip(("water-rich", "ion-rich"), phases, strict=True):
        add(f"dea-worked-split-{label}-liquid-density", record,
            f"dea_controls.rows[worked_state].phases[{label}].density_kg_m3", f"{phase['density_kg_m3']:.1f}")
    for label, key in (("true-moles", "true_mole_fraction"), ("mass", "mass_fraction")):
        add(f"dea-worked-split-ion-rich-liquid-share-of-{label}", record,
            f"dea_controls.rows[worked_state].phases[ion-rich].{key} * 100", f"{100 * phases[-1][key]:.2f}")
    for passage in ("conclusion", "transfer-density", "supplement-density"):
        add(f"dea-confirmed-split-density-feeds-{passage}", record,
            "dea_controls.rows.count", NUMBER_WORDS[len(dea["rows"])])

    record = STUDY + "results/E/MEA/replay.json.gz"
    pressure_stats = read(record)["summary"]["pressure"]
    for cohort, passages in (
        ("legacy", ("results", "conclusion", "shared-set", "historical-comparison", "residual-caption",
                    "weighting-sensitivity", "weighting-interpretation")),
        ("added", ("results", "residual-caption", "restriction-comparison", "weighting-sensitivity")),
    ):
        for passage in passages:
            add(f"mea-{cohort}-pressure-count-{passage}", record, f"summary.pressure.{cohort}.attempted",
                str(pressure_stats[cohort]["attempted"]))
    for label, cohort in (("added-same-sources", "added"), ("aronu-nominal", "Aronu2011")):
        add(f"mea-{label}-pressure-aard-results", record,
            f"summary.pressure.{cohort}.AARD_percent", f"{pressure_stats[cohort]['AARD_percent']:.2f}")
    for passage in ("mea-results", "shared-set", "literature-comparison"):
        add(f"mea-mamun-pressure-aard-{passage}", record, "summary.pressure.Mamun2005.AARD_percent",
            f"{pressure_stats['Mamun2005']['AARD_percent']:.2f}")
        add(f"mea-mamun-assessment-pressure-count-{passage}", record, "summary.pressure.Mamun2005.attempted",
            str(pressure_stats["Mamun2005"]["attempted"]))
    record = MEA_EXPANDED_SUMMARY
    pressures = read(record)["off_window"]["reported"]
    for label, cohort in (("lower", "Aronu2011 15 wt%"), ("higher", "Aronu2011 45 wt%")):
        add(f"mea-aronu-{label}-concentration-pressure-aard-results", record,
            f"off_window.reported[{cohort}].AARD_percent", f"{pressures[cohort]['AARD_percent']:.2f}")

    record = "analyses/round_8/results/salt-and-weighting.json.gz"
    weighting = read(record)["quantities"]
    models = {
        "salt-first": "salt/incumbent", "salt-pressure": "salt/refit",
        "mea-first": "historical/incumbent", "mea-pressure": "historical/refit",
    }
    comparisons = {
        ("Kuranov", "salt-first"): ("initial-weighting", "reweighting", "shared-first"),
        ("Kuranov", "salt-pressure"): ("reweighting", "shared-pressure"),
        ("Kuranov", "mea-first"): ("shared-first",),
        ("Kuranov", "mea-pressure"): ("shared-pressure",),
        ("Ermatchkov", "salt-first"): ("reweighting", "shared-first", "supplement-reweighting"),
        ("Ermatchkov", "salt-pressure"): ("reweighting", "shared-pressure", "supplement-reweighting"),
        ("Ermatchkov", "mea-first"): ("shared-first",),
        ("Ermatchkov", "mea-pressure"): ("shared-pressure",),
        ("Carson", "salt-first"): ("initial-weighting", "reweighting"),
        ("Carson", "salt-pressure"): ("reweighting", "shared-pressure"),
        ("Carson", "mea-pressure"): ("shared-pressure",),
    }
    for group in ("Kuranov", "Ermatchkov", "Xiao", "Carson"):
        for label, case in models.items():
            value = weighting["properties"][group][case]["matched"]["AARD_percent"]
            key = f"quantities.properties[{group},{case}].matched.AARD_percent"
            for passage in ("matched-subset", *comparisons.get((group, label), ())):
                add(f"mdea-{group.lower()}-{label}-aard-{passage}", record, key, f"{value:.2f}")
    for group, name in (
        ("Kuranov", "mdea-fitted-kuranov-pressure-count-supplement-weighting"),
        ("Ermatchkov", "mdea-ermatchkov-partial-pressure-count-weighting"),
        ("Xiao", "mdea-xiao-matched-pressure-comparison-count"),
    ):
        subset = weighting["properties"][group]
        assert all(row["common_keys"] == subset["salt/incumbent"]["common_keys"] for row in subset.values())
        add(name, record, f"quantities.properties[{group},salt/incumbent].common_keys: count",
            str(len(subset["salt/incumbent"]["common_keys"])))
    for label, case in models.items():
        data = weighting["models"][case]
        key = f"quantities.models[{case}]"
        add(f"mdea-{label}-original-weight-objective-matched-subset", record,
            key + ".objective.original", f"{data['objective']['original']:.1f}")
        for population in ("measured", "grid"):
            add(f"mdea-{label}-matched-{population}-searches-available", record,
                key + f".phase.common_keys.{population}.available",
                str(data["phase"]["common_keys"][population]["available"]))

    pair_record = PROPERTY_SUMMARY
    paired = read(pair_record)["mdea"]["paired"]
    for group in ("Kuranov", "Ermatchkov", "Carson"):
        add(f"mdea-{group.lower()}-tracking-reference-paired-aard", pair_record,
            f"mdea.paired.{group}.models[system pressure].AARD_percent",
            f"{paired[group]['models'][0]['AARD_percent']:.2f}")
    record = "analyses/mdea_mea_workflow/results/bounded-binary-411/comparison.json"
    bounded = read(record)
    chosen = bounded["chosen"]
    add("mdea-bounded-historical-fit-objective", record,
        f"runs[{chosen}].data_cost", f"{bounded['runs'][chosen]['data_cost']:.1f}")

    fixed = FixedReference(read)
    for family in ("MEA", "DEA", "MDEA", "AMP_free"):
        record = STUDY + f"results/{family}/{fixed.selections[family]['selected']}.json.gz"
        rows = fixed.fits[family]["replay"]["rows"]
        amine = family.split("_")[0].lower()
        if family != "AMP_free":
            add(f"{amine}-objective-observations-methods", record, "replay.rows.count", str(len(rows)))
        if family in ("MEA", "MDEA"):
            covariance = fixed.conditional(family)
            for passage in ("methods", "supplement"):
                add(f"{amine}-residual-degrees-of-freedom-{passage}", record,
                    "replay responsive rows minus diagnostics.uncertainty.free_coordinates count",
                    str(covariance["dof"]))
                if family == "MEA":
                    add(f"mea-responsive-observations-{passage}", record,
                        "replay.rows[group != Kiepe].count", str(covariance["responsive"]))
            add(f"{amine}-conditional-variance-factor-supplement", record,
                "twice sum of responsive replay row costs / residual degrees of freedom",
                f"{covariance['stage_variance']:.8f}")
            if family == "MDEA":
                add("mdea-responsive-observations-methods", record,
                    "replay.rows.count excluding pure-water Kim rows", str(covariance["responsive"]))
            else:
                for passage in ("methods-covariance", "supplement-covariance", "electrostatics"):
                    add(f"mea-objective-observations-{passage}", record, "replay.rows.count", str(len(rows)))
                add("mea-responsive-observations-methods-data", record,
                    "replay.rows[group != Kiepe].count", str(covariance["responsive"]))
        total = fsum(row["cost"] for row in rows)
        groups = {
            "DEA": {"loaded-pressures": ("Lawson", "SeoHong", "Lal")},
            "MDEA": {"loaded-pressures": ("Kuranov",), "integral-heats": ("Carson", "Merkley"),
                     "unloaded-densities": ("unloaded-density",)},
            "AMP_free": {"loaded-pressures": ("loaded-pressure", "hartono-2021-supplemental", "tong")},
        }
        for quantity, cohort in groups.get(family, {}).items():
            parts = [fsum(row["cost"] for row in rows if row["group"] == group) for group in cohort]
            key = f"replay.rows[{','.join(cohort)}].cost / replay total cost * 100"
            share = 100 * fsum(parts) / total
            if family == "AMP_free":
                # The methods sentence sums the three printed shares of the cited table.
                share = fsum(round(100 * part / total, 1) for part in parts)
                key += ": sum of row percentages rounded to one decimal"
            locations = (("methods", "transfer", "supplement") if quantity != "integral-heats" else ("transfer",)
                         ) if family == "MDEA" else ("methods",)
            for passage in locations:
                add(f"{amine}-{quantity}-objective-share-{passage}", record, key, f"{share:.1f}")

    record = PROPERTY_SUMMARY
    spread = read(record)["spread"]["MDEA"]["groups"]
    for cohort, digits in (("Kuranov", 1), ("Carson", 0)):
        add(f"mdea-{cohort.lower()}-endpoint-aard-spread", record,
            f"spread.MDEA.groups.{cohort}.AARD_spread_pp", f"{spread[cohort]['AARD_spread_pp']:.{digits}f}")

    for population, variants in (
        ("first-data", ("original-main", "original-slope-150")),
        ("expanded-data", ("expanded-free", "expanded-fixed")),
    ):
        for label, variant in zip(("free-slope", "fixed-slope"), variants, strict=True):
            record = f"analyses/round_5/results/D/AMP-{variant}.json.gz"
            rows = [row for row in read(record)["rows"] if row.get("state_type") == "loaded reactive"]
            add(f"amp-{population}-{label}-minimum-gibbs-curvature", record,
                "rows[loaded reactive].minimum: minimum", f"{min(row['minimum'] for row in rows):.3f}")
            if label == "free-slope":
                add(f"amp-{population}-gibbs-curvature-states", record, "rows[loaded reactive].count", str(len(rows)))

    record = "analyses/dea_transfer/results/reactive-refit-425/comparisons.json"
    binary = read(record)
    rows = {row["group"]: row for row in binary["tableS10"] if row["role"] == "fitted"}
    for quantity, row, key, reference_digits in (
        ("horstmann-pressure", rows["Horstmann VLE"], "tableS10[Horstmann VLE,fitted]", 1),
        ("horstmann-excess-enthalpy", rows["Horstmann heat"], "tableS10[Horstmann heat,fitted]", 0),
        ("lawson-pressure", rows["Lawson"], "tableS10[Lawson,fitted]", 1),
        ("carson-absorption-heat", rows["Carson"], "tableS10[Carson,fitted]", 1),
        ("held-out-pressure", binary["table7"]["loaded_outside_reactive_fit"],
         "table7.loaded_outside_reactive_fit", 1),
    ):
        for label, case, digits in (("constant", "reference", reference_digits), ("temperature-dependent", "candidate", 1)):
            add(f"dea-binary-{label}-{quantity}-aard-supplement", record,
                f"{key}.{case}.AARD_percent", f"{row[case]['AARD_percent']:.{digits}f}")
        if quantity == "horstmann-pressure":
            add("dea-binary-constant-horstmann-pressure-aard-transfer", record,
                key + ".reference.AARD_percent", f"{row['reference']['AARD_percent']:.1f}")

    record = GIBBS_DERIVATIVES
    checks = read(record)["rows"]
    fitted_caloric = [r for r in checks if r["comparison"] == "Eq. 12" and
                      r["state"] in {f"selected-{name}" for name in ("MEA", "DEA", "MDEA", "AMP_free")}]
    for key, label, scale, precision in (
        ("signed_error", "discrepancy-mj-per-mol", 1000, 1),
        ("estimated_error", "resolution-j-per-mol", 1, 2),
    ):
        values_at_states = [abs(row[key]) for row in fitted_caloric]
        for bound, fun in (("minimum", min), ("maximum", max)):
            add(f"gibbs-enthalpy-{bound}-{label}", record, f"rows[selected,Eq. 12].{key}: {bound} absolute times {scale}",
                f"{fun(values_at_states) * scale:.{precision}f}")

    record = "analyses/round_8/results/salt-and-weighting.json.gz"
    mixed = collections.defaultdict(list)
    for row in read(record)["quantities"]["residuals"]:
        if row["salt"] == "mixed":
            mixed[float(row["nominal_molality"])].append(
                row["signed_percent"] if row["status"] == "available" else None)
    for label, fun, sign in (("negative", max, -1), ("positive", min, 1)):
        molality = fun(molality for molality, deltas in mixed.items()
                       if all(value is not None and sign * value > 0 for value in deltas))
        add(f"mixed-salt-{label}-residual-molality-bracket", record,
            f"quantities.residuals[mixed] fully evaluated series with {label} residuals: {fun.__name__} molality",
            f"{molality:.1f}")

    record = "analyses/round_5/results/A/original-main.json.gz"
    first_pressures = sum(row["role"] == "fitted" and row["group"] == "loaded-pressure"
                          for row in read(record)["original"]["rows"])
    for passage in ("transfer", "supplement", "slope-comparison", "extended-data"):
        add(f"amp-first-data-fitted-pressure-count-{passage}", record,
            "original.rows[loaded-pressure,fitted].count", str(first_pressures))

    controls = "analyses/mea_parameter_bundle/results/objective-weights-420/alternative/"
    record = controls + "search/summary.json"
    alt = read(record)["result"]
    add("mea-cai-reweighting-liquid-grid-requests", record, "result.grid.states + result.offset.states",
        str(alt["grid"]["states"] + alt["offset"]["states"]))
    add("mea-cai-reweighting-liquid-vapor-census-requests", record, "result.census.states", str(alt["census"]["states"]))
    record = controls + "observable-errors.csv"
    scores = {row["group"]: row for row in read(record)}
    for label, group in (("fitted", "fitted fitted CO2 partial pressure"),
                         ("added", "unfitted six-source pressures"), ("wagner", "Wagner pressures")):
        data = scores[group]
        for case in ("reported", "alternative"):
            key = f"paired_{case}_aard"
            add(f"mea-cai-reweighting-{label}-{case}-aard", record, f"group {group}: {key}", f"{float(data[key]):.2f}")
        if label != "wagner":
            add(f"mea-cai-reweighting-{label}-pressure-count", record, f"group {group}: paired_reported_available",
                data["paired_reported_available"])

    record = "analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/F4/uncertainty/prediction-bands.csv"
    n = sum(row["group"] == "common149: partial_pressure" for row in read(record))
    for passage in ("results", "supplement"):
        add(f"mea-tracking-covariance-volatilization-pressure-count-{passage}", record,
            "group common149: partial_pressure count", str(n))
    record = "analyses/mea_parameter_bundle/results/reduced-refit/agreement.csv"
    historic = next(row for row in read(record)
                    if row["fit"] == "F2" and row["dataset"] == "fitted: fitted CO2 partial pressure")
    add("mea-fitted-shared-set-fitted-pressure-aard-transfer", record,
        "F2, fitted CO2 partial pressure: aard_percent", f"{float(historic['aard_percent']):.2f}")

    for amine, name, cohorts in (
        ("dea", "DEA/property-comparisons/selected", (
            ("Carson", "carson-heat", "J/mol CO2", ("AARD_percent",)),
            ("Lawson", "lawson-fitted-pressure", "Pa", ("AARD_percent", "bias_percent")),
            ("SeoHong", "seo-hong-fitted-pressure", "Pa", ("AARD_percent", "bias_percent")),
            ("Lawson-394K", "lawson-hot-pressure", "Pa", ("AARD_percent",)),
        )),
        ("mdea", "MDEA/properties", (
            ("Ermatchkov", "ermatchkov-pressure", "Pa", ("bias_percent",)),
            ("Kuranov-413K", "kuranov-held-out-pressure", "Pa", ("AARD_percent",)),
            ("Carson", "carson-heat", "J/mol", ("AARD_percent",)),
            ("unloaded-density", "unloaded-density", "kg/m^3", ("AARD_percent",)),
            ("Jakobsen", "jakobsen-species-ratio", None, ("bias_percent",)),
        )),
        ("amp", "AMP_free/properties", (("kundu", "kundu-pressure", "Pa", ("AARD_percent",)),)),
    ):
        record = STUDY + f"results/{name}.json.gz"
        rows = read(record)["rows"]
        for group, label, unit, metrics in cohorts:
            selected = [row for row in rows if row["group"] == group and (unit is None or row["unit"] == unit)]
            summary = stats(selected, predicted="value")
            for metric in metrics:
                passages = ("transfer", "literature") if label == "kundu-pressure" else ("transfer",)
                for passage in passages:
                    add(f"{amine}-{label}-{metric.split('_')[0].lower()}-{passage}", record,
                        f"rows[{group},{unit or 'all units'}].value,observed: {metric}",
                        f"{summary[metric]:{'+.2f' if metric == 'bias_percent' else '.2f'}}")
            if label == "lawson-hot-pressure":
                for passage in ("methods", "transfer"):
                    add(f"dea-lawson-hot-pressure-row-count-{passage}", record,
                        "rows[Lawson-394K,Pa].count", NUMBER_WORDS[len(selected)])
        if amine == "mdea":
            hot = [row for row in rows if row["group"] == "Kuranov" and row["outside_ranges"]["MDEA-dissociation"]]
            summary = stats(hot, predicted="value")
            for passage in ("results", "discussion"):
                for metric, fmt in (("AARD_percent", ".2f"), ("bias_percent", "+.2f")):
                    add(f"mdea-hot-fitted-pressure-{metric.split('_')[0].lower()}-{passage}", record,
                        f"rows[Kuranov,outside MDEA-dissociation].value,observed: {metric}", format(summary[metric], fmt))

    record = PROPERTY_SUMMARY
    data = read(record)
    shared = data["shared"]["comparisons"]
    for group, label in (
        (MEA_LEGACY_PRESSURE_GROUP, "mea-fitted-pressure"),
        ("MEA Mamun2005", "mea-mamun"),
        ("MDEA Kuranov", "mdea-kuranov"),
        ("MDEA Ermatchkov", "mdea-ermatchkov"),
        ("MDEA Carson", "mdea-carson"),
    ):
        value = shared[group]["models"]["MEA-fitted"]["AARD_percent"]
        add(f"{label}-mea-fitted-shared-set-aard", record,
            f"shared.comparisons[{group}].models[MEA-fitted].AARD_percent", f"{value:.2f}")
        if label == "mdea-carson":
            value = shared[group]["models"]["salt-anchored"]["AARD_percent"]
            add("mdea-carson-salt-anchored-aard-shared-set-comparison", record,
                f"shared.comparisons[{group}].models[salt-anchored].AARD_percent", f"{value:.2f}")
    value = data["mdea"]["paired"]["Carson"]["models"][1]["AARD_percent"]
    add("mdea-carson-fixed-reference-paired-aard", record, "mdea.paired.Carson.models[fixed reference].AARD_percent",
        f"{value:.2f}")
    return values


def tex_values(values):
    return "".join(r"\resultvalue{" + name + "}{" + row["value"] + "}\n" for name, row in values.items())


def sentences(source):
    """Yield source line and text, ignoring TeX comments and preserving display cells."""
    clean = COMMENT.sub(lambda match: " " * len(match[0]), source)
    boundary = re.compile(r"[.!?](?=\s|$)|\n\s*\n|\\\\(?=\n|$)")
    start = 0
    for end in [*(match.end() for match in boundary.finditer(clean)), len(clean)]:
        chunk = clean[start:end]
        text = " ".join(chunk.split())
        if text:
            first = start + len(chunk) - len(chunk.lstrip())
            yield 1 + source.count("\n", 0, first), text
        start = end


def bindings(values, outputs, commit=None):
    from difflib import SequenceMatcher

    for path in [*manuscript_sources(), *(path for path, body in outputs.items() if isinstance(body, str))]:
        content = path.read_text() if path.is_file() else outputs[path]
        current = list(sentences(content))
        changed = set()
        removed_binding = set()
        if commit:
            previous = list(sentences(at_revision(path, commit, missing="")))
            matcher = SequenceMatcher(None, [s for _, s in previous], [s for _, s in current], autojunk=False)
            for tag, before, after, start, stop in matcher.get_opcodes():
                if tag != "equal":
                    changed.update(range(start, stop))
                if tag == "replace" and any(RES.search(sentence) for _, sentence in previous[before:after]):
                    removed_binding.update(range(start, stop))
        for index, (line, sentence) in enumerate(current):
            matches = list(RES.finditer(sentence))
            for match in matches:
                name = match[1]
                row = values[name]
                print(json.dumps(dict(file=str(path.relative_to(ROOT)), line=line, name=name,
                                      sentence=sentence, **row), ensure_ascii=False))
            if index in changed and not matches and (
                index in removed_binding or NUMERAL.search(sentence) or NUMBER_WORD.search(sentence)
            ):
                print(json.dumps(dict(file=str(path.relative_to(ROOT)), line=line, sentence=sentence),
                                 ensure_ascii=False))


def numeric_occurrences(text, masked):
    from decimal import Decimal

    for match in SCIENTIFIC.finditer(text):
        if masked[match.start():match.end("mantissa")].strip():
            yield match, Decimal(match["mantissa"]).scaleb(int(match["exponent"]))
            masked = masked[:match.start()] + " " * len(match[0]) + masked[match.end():]
    for match in NUMERAL.finditer(masked):
        yield match, Decimal(match[0])


def collision_contexts(text, excerpt):
    start = r"(?<!\w)" if excerpt and excerpt[0].isalnum() else ""
    return re.finditer(start + re.escape(excerpt), text)


def typed_numbers(values, collisions):
    import ast

    def candidates():
        for path in manuscript_sources():
            text = manuscript_body(path.read_text())
            yield path.relative_to(ROOT).as_posix(), 1, text, mask_syntax(text)
        path = Path(__file__)
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                yield path.relative_to(ROOT).as_posix(), node.lineno, node.value, mask_syntax(node.value)

    registered = {value for row in values.values() for _, value in numeric_occurrences(row["value"], row["value"])}
    used = collections.Counter()
    for file, line, text, masked in candidates():
        for match, value in numeric_occurrences(text, masked):
            if value not in registered:
                continue
            accepted = []
            for i, entry in enumerate(collisions):
                if file != entry["file"] or match[0] != entry["token"]:
                    continue
                excerpt = entry["context"]
                if any(m.start() <= match.start() and match.end() <= m.end()
                       for m in collision_contexts(text, excerpt)):
                    accepted.append(i)
            if len(accepted) == 1:
                used[accepted[0]] += 1
            else:
                lineno = line + text.count("\n", 0, match.start())
                yield f"Typed result candidate: {file}:{lineno}: {match[0]}"
    for i, entry in enumerate(collisions):
        if not re.fullmatch("[a-z]+", entry["reason"]):
            yield f"Invalid number collision reason: {entry['file']}: {entry['context']}"
        if used[i] != 1:
            yield f"Stale or ambiguous number collision: {entry['file']}: {entry['context']}"


def at_revision(path, commit, *, missing=None, binary=False):
    import subprocess

    key = path.relative_to(ROOT).as_posix()
    result = subprocess.run(["git", "show", f"{commit}:{key}"], cwd=ROOT, capture_output=True)
    if result.returncode and missing is not None:
        return missing
    result.check_returncode()
    return result.stdout if binary else result.stdout.decode()


def main():
    from time import monotonic

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--compare", metavar="COMMIT")
    mode.add_argument("--bindings", nargs="?", const="", metavar="COMMIT")
    args = parser.parse_args()
    started = monotonic()
    verify()
    catalog = json.loads(Path(__file__).with_name("sources.json").read_text())
    register_records(catalog)
    values = result_values()
    outputs = render_all()
    if args.bindings is not None:
        bindings(values, outputs, args.bindings or None)
        return
    values_path = TABLES / "results.tex"
    values_text = tex_values(values)
    manuscript = "\\n".join(COMMENT.sub("", path.read_text()) for path in manuscript_sources())
    expected_tables = {LATEX / (name + ".tex") for name in re.findall(r"\\input\{(tables/[^}]+)\}", manuscript)}
    expected_figures = {
        LATEX / "figures/generated" / name
        for name in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", manuscript)
    }
    missing = (expected_tables | expected_figures) - outputs.keys()
    if missing:
        raise ValueError(f"Included displays missing from renderer: {sorted(missing)}")
    source_path = TABLES / "number-sources.json"
    source_text = json.dumps(
        {
            key: dict(record=row["record"], sha256=sources.get(key, row["sha256"]), read=key in sources)
            for key, row in catalog.items() if "record" in row
        },
        indent=2,
    ) + "\n"
    if args.check or args.compare:
        errors = []
        old_values = values
        if args.compare:
            old_values_source = at_revision(values_path, args.compare, missing="")
            old_values = {name: {"value": value} for name, value in
                          re.findall(r"^\\resultvalue\{([^}]+)\}\{(.*)\}$", old_values_source, re.M)}
            for name in sorted(old_values.keys() | values.keys()):
                before = old_values.get(name, {}).get("value")
                after = values.get(name, {}).get("value")
                if before != after:
                    print(f"{name}: {before!r} -> {after!r}")
        figures = tables = 0
        for path, content in outputs.items():
            if args.compare:
                old = at_revision(path, args.compare, missing="", binary=isinstance(content, bytes))
                if not old and path.name == "amp_reference_state.tex":
                    original = BUNDLE / "results/reference-states-428" / path.name
                    old = at_revision(original, args.compare)
            else:
                old = path.read_bytes() if isinstance(content, bytes) else path.read_text()
            if isinstance(content, bytes):
                figures += 1
                equal = old == content
            else:
                tables += 1
                equal = visible(expand(old, old_values)) == visible(expand(content, values))
            if not equal:
                errors.append(f"Changed display: {path.relative_to(LATEX)}")
        if args.check and (not values_path.exists() or values_path.read_text() != values_text):
            errors.append("Stale tables/results.tex")
        if args.check and source_path.read_text() != source_text:
            errors.append("Stale tables/number-sources.json")
        if args.check:
            occurrences = collections.Counter(RES.findall(manuscript))
            for body in outputs.values():
                if isinstance(body, str):
                    occurrences.update(RES.findall(COMMENT.sub("", body)))
            unpaired = {name: occurrences[name] for name in occurrences.keys() | values.keys()
                        if name not in values or occurrences[name] != 1}
            if unpaired:
                errors.append(f"Each result requires exactly one occurrence: {unpaired}")
            collisions = json.loads(Path(__file__).with_name("number-collisions.json").read_text())
            errors.extend(typed_numbers(values, collisions))
        if errors:
            for error in errors:
                print(error)
        print(f"{tables} tables, {figures} figures, {len(sources)} records read, {monotonic() - started:.2f} s")
        raise SystemExit(bool(errors))
    outputs[values_path] = values_text
    outputs[source_path] = source_text
    for path, content in outputs.items():
        path.write_bytes(content if isinstance(content, bytes) else content.encode())


if __name__ == "__main__":
    main()
