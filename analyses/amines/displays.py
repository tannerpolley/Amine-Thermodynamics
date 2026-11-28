"""Render manuscript tables and figures from the amine stage records."""

import argparse
from ast import literal_eval
import collections
import csv
from functools import reduce
import gzip
from hashlib import sha256
from io import BytesIO
import json
import math
from math import fsum, sqrt
from operator import getitem
from pathlib import Path
from posixpath import normpath
import re
from statistics import mean
import tomllib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from numpy.linalg import matrix_rank

from analyses.amines.phase import search_class
from analyses.amines.wheel import verify

ROOT = Path(__file__).resolve().parents[2]
LATEX = ROOT / "docs/scientific/latex"
BUNDLE = ROOT / "analyses/mea_parameter_bundle"
TABLES = LATEX / "tables"
MEA_REPORTED_PROPERTIES = "analyses/amines/results/mea/reported/properties/uncertainty-and-activities.json.gz"
GIBBS_DERIVATIVES = "analyses/amines/results/shared/properties/gibbs-derivatives.json"
FIT_SUMMARY = "analyses/amines/results/shared/fit/display-summary.json.gz"
AMP_SCREEN = "analyses/amines/results/amp/reported/phase/AMP_free/screen/selected/supplied/summary.json.gz"
KURANOV_DATA = "data/reference/MDEA/Kuranov_1996_CO2_MDEA_total_pressure.csv"
AMP_PURE_INPUT = "analyses/amp_transfer/inputs/amp-pure-endpoint.json"
MOVE = "analyses/amines/results/move/"
W_AMP_WITHOUT_HOT = MOVE + "amp/without-hot-pressures/phase/supplied.json.gz"
W_AMP_WITHOUT_HOT_PROPERTIES = MOVE + "amp/without-hot-pressures/properties/summary.json.gz"
W_AMP_WITHOUT_HOT_REPLAY = MOVE + "amp/without-hot-pressures/replay/endpoint.json.gz"
W_AMP_WITHOUT_HOT_FIT = MOVE + "amp/without-hot-pressures/fit/A.json.gz"
W_AMP_WITHOUT_HOT_CONTROLS = MOVE + "amp/without-hot-pressures/phase/measured-controls.json.gz"
W_AMP_CONTROLS = MOVE + "amp/reported/phase/measured-controls.json.gz"
W_DEA_BINARY = MOVE + "dea/binary-temperature-dependent/replay/endpoint.json.gz"
W_DEA_SCREEN = MOVE + "dea/reported/phase/declared.json.gz"
W_MDEA_SCREEN = MOVE + "mdea/reported/phase/declared.json.gz"
W_MDEA_PROPERTIES = MOVE + "mdea/reported/properties/summary.json.gz"
W_MEA_PHASE = MOVE + "mea/reported/phase/"
W_SALT = MOVE + "salt/sodium-salts/fit/summary.json.gz"
W_MDEA_BINARY = MOVE + "mdea/reported/phase/binary-gap.json.gz"
W_MDEA_NEUTRAL = MOVE + "mdea/reported/phase/binary-neutral.json.gz"
W_MDEA_REACTIVE = MOVE + "mdea/reported/phase/reactive-zero-loading.json.gz"
W_MDEA_UNWEIGHTED_REACTIVE = MOVE + "mdea/without-binary-gap-bound/phase/reactive-zero-loading.json.gz"
W_MDEA_PUBLISHED = MOVE + "mdea/published/replay/endpoint.json.gz"
W_MDEA_WITHOUT_GAP_BOUND = MOVE + "mdea/without-binary-gap-bound/phase/summary.json.gz"
W_ABLATION = MOVE + "shared/properties/water-bicarbonate-ablation.json.gz"
W_MEA_ABLATION_FIT = MOVE + "mea/water-bicarbonate-ablation/fit/A.json.gz"
W_WATER = MOVE + "mea/reported/water-calibration/summary.json.gz"
BORN = MOVE + "mea/reported/born-sensitivity/summary.json.gz"
DEA_R4_SOURCE = "analyses/dea_transfer/declarations.toml"
AMP_R4_SOURCE = "analyses/amp_transfer/inputs/retransfer-344/phase-2/declarations.toml"
sources = {}
stage_records = {}
record_paths = {}


def register_records(catalog):
    for key, row in catalog.items():
        if "record" not in row or row["disposition"] in ("comparison-only", "orphan"):
            continue
        path = ROOT / key
        if not path.is_relative_to(ROOT / "analyses/amines/results") and row.get("c_disposition") != "retain-in-place":
            continue
        record_paths[key] = key
        if "archive_path" in row:
            record_paths[row["archive_path"]] = key
        stage_records[key] = path
    for family, amine, properties in (
        ("MEA", "mea", None),
        ("DEA", "dea", "DEA/property-comparisons/selected.json.gz"),
        ("MDEA", "mdea", "MDEA/properties.json.gz"),
        ("AMP_free", "amp", "AMP_free/properties.json.gz"),
    ):
        for filename in ("A.json.gz", "selection.json"):
            record_paths[STUDY + f"results/{family}/{filename}"] = MOVE + f"{amine}/reported/fit/{filename}"
        if properties:
            record_paths[STUDY + f"results/{properties}"] = MOVE + f"{amine}/reported/properties/summary.json.gz"
    for source, target in {
        "E/MEA/replay.json.gz": "expanded-pressure",
        "MEA/off-window.json.gz": "off-window",
        "MEA/heat-comparison.json.gz": "heat-comparison",
        "display-replays/mea-comparisons.json.gz": "mea-comparisons",
        "display-replays/wagner.json.gz": "wagner",
        "display-replays/bubble-checks.json.gz": "bubble-checks",
        "display-replays/caloric-and-species.json.gz": "caloric-and-species",
    }.items():
        record_paths[STUDY + "results/" + source] = MOVE + f"mea/reported/properties/{target}.json.gz"
    record_paths[MEA_REPORTED_PROPERTIES] = MOVE + "mea/reported/properties/uncertainty-and-activities.json.gz"
    record_paths[STUDY + "results/MDEA/manifest.json.gz"] = MOVE + "mdea/reported/fit/manifest.json.gz"
    record_paths[STUDY + "results/MDEA/property-comparisons/A.json.gz"] = W_MDEA_PROPERTIES


def read(name):
    path = Path(name)
    if not path.is_absolute():
        path = ROOT / path
    key = record_paths[normpath(path.relative_to(ROOT).as_posix())]
    raw = stage_records[key].read_bytes()
    sources[key] = sha256(raw).hexdigest()
    data = gzip.decompress(raw) if path.suffix == ".gz" else raw
    if path.name.removesuffix(".gz").endswith(".json"):
        return json.loads(data)
    if path.suffix == ".toml":
        return tomllib.loads(data.decode())
    return list(csv.DictReader(data.decode().splitlines()))

STUDY = 'analyses/fixed_reaction_reference/'
KIEPE_AUTHOR = r'Kiepe et al.\ '
KIEPE_CITE = 'kiepeExperimentalDeterminationPrediction2002'
DESIGNS = ('MEA', 'DEA', 'MDEA', 'AMP_free')
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

def count_word(count, *, zero="none", pair="two"):
    return zero if count == 0 else pair if count == 2 else NUMBER_WORDS[count]


def ordinal(count):
    return ("first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh")[count - 1]


def amp_vapor_outcome(outcome):
    return outcome in ("L+V passed; L+L unresolved", "Vapor-directed; root unqualified")


def confirmed_split(state):
    return any(attempt['confirmed'] for attempt in state['attempts'])


def common_profile_starts(profile):
    return set(profile['mdea_starts']['low']) & set(profile['mdea_starts']['high'])


def common_control_outcomes(attempts):
    return set.intersection(*(set(rows.items()) for rows in attempts.values()))


def coefficients(node):
    if isinstance(node, dict):
        if 'identity' in node and isinstance(node.get('value'), dict):
            yield node['identity'], node
        for value in node.values():
            yield from coefficients(value)
    elif isinstance(node, list):
        for value in node:
            yield from coefficients(value)


def source_r4(record):
    reactions = read(record)["chemistry"]["reactions"]["aqueous"]
    return next(row["correlation"] for row in reactions if row["name"] == "carbamate-hydrolysis")


def distinct_phase_rows(record):
    return [row for row in record["rows"] if row["key"] not in record["aliases"]]


def distinct_mea_measured_rows(record):
    states = {}
    for row in record["rows"]:
        feed = row["feed_mol"]
        total = fsum(feed.values())
        composition = tuple(sorted((species, amount / total) for species, amount in feed.items()))
        key = row["T_K"], row["P_Pa"], composition
        first = states.setdefault(key, row)
        if (row["available"], row["descent"]) != (first["available"], first["descent"]):
            raise ValueError(f"Repeated MEA search has a different outcome: {row['identity']}")
    return list(states.values())


def mdea_pressure_rows(record):
    supplemental = [row for row in record.values() if isinstance(row, dict)
                    and row.get("basis", {}).get("template") == "loaded-bubble" and row.get("unit") == "Pa"]
    return [*record["rows"], *(dict(row, role="not fitted") for row in supplemental)]


def stats(part, observed='observed', predicted='predicted'):
    errors = [float(r[predicted]) - float(r[observed]) for r in part]
    fractions = [x / float(r[observed]) for x, r in zip(errors, part, strict=True)]
    return dict(n=len(part), RMSE=math.sqrt(math.fsum(x*x for x in errors)/len(part)),
                bias=math.fsum(errors)/len(part),
                bias_percent=100*math.fsum(fractions)/len(part),
                AARD_percent=100*math.fsum(map(abs, fractions))/len(part))



def kim_prior_interval_counts():
    rows = read("analyses/mea_parameter_bundle/results/reaction-temperature-fit/candidate-targets.csv")
    return collections.Counter(row["key"].split("_")[1] for row in rows
                               if row["family"] == "heat" and row["key"].startswith("kim2007_"))


def mdea_kuranov_rows(result):
    keys = {row["source_row"] for row in read(KURANOV_DATA)}
    selected = [r for r in mdea_pressure_rows(result)
                if r["group"].startswith("Kuranov") and str(r["row"].get("source_row")) in keys]
    if {str(r["row"]["source_row"]) for r in selected} != keys or len(selected) != len(keys):
        raise ValueError("Kuranov source rows differ from the matched Table 2 population")
    return selected


def amp_pure_coordinate_count():
    document = read(AMP_PURE_INPUT)
    pure = next(row for row in document["components"] if row["component_id"] == "aminomethylpropanol")
    families = {"segment_count", "segment_diameter", "dispersion_energy_over_k"}
    edges = document["topology"]["edges"]
    return sum(q["family"] in families for q in pure["coefficients"]) + sum(
        key in edge for edge in edges for key in ("energy_over_k", "volume"))


def mdea_binary_pressure_scale(manifest):
    rows = [row for row in manifest["rows"]["fitted"] if row["group"] == "Kuranov-binary"]
    return 1 / math.sqrt(len(rows) * rows[0]["weight"])


def mdea_pressure_comparisons():
    result = read(W_MDEA_PROPERTIES)
    selected = mdea_kuranov_rows(result)
    used = [r for r in selected if r["status"] == "Available" and r["requested_tolerance_met"]]
    kuranov = dict(available=len(used), AARD_percent=stats(used, predicted="value")["AARD_percent"])
    rows = [r for r in result["rows"] if r["group"] == "corrected-Kamps" and r["status"] == "Available"]
    additional, = (r for r in rows if r["identity"] == "comparison:113")
    common = [r for r in rows if r is not additional]
    kamps = dict(full_rows=len(rows), full_AARD_percent=stats(rows, predicted="value")["AARD_percent"],
                 common_rows=len(common), common_AARD_percent=stats(common, predicted="value")["AARD_percent"],
                 additional_row=additional, additional_signed_percent=100 * (additional["value"] / additional["observed"] - 1))
    return kuranov, kamps


def shared_interaction_table(shared, table, num):
    labels = {MEA_LEGACY_PRESSURE_GROUP: r'MEA, fitted $p_{\COtwo}$',
              'MEA Mamun2005': r'MEA, Ma\textquotesingle mun $p_{\COtwo}$',
              'MDEA Kuranov': 'MDEA, Kuranov loaded total pressure',
              'MDEA Ermatchkov': r'MDEA, Ermatchkov $p_{\COtwo}$',
              'MDEA Carson': 'MDEA, Carson integral heat'}
    rows = [[labels[key], len(case['common']),
             *[num(case['models'][name]['AARD_percent'], 2) for name in ('salt-anchored','MEA-fitted')]]
            for key, case in shared['comparisons'].items()]
    bicarbonate = shared['bicarbonate']
    table('supplement-shared-interaction-sensitivity',
          'Deviations of the MEA and MDEA models, with the water--anion interactions fixed from the sodium-salt data, and of the same fits with the water--bicarbonate interaction fitted to the MEA data, on identical observations.',
          ['Observable', '$N$', r'Salt-fitted interactions, AARD (\%)', r'MEA-fitted interaction, AARD (\%)'],
          rows, [.41,.15,.19,.19],
          notes=rf'In the fits with the MEA-fitted interaction, the water--bicarbonate interaction is the constant ${bicarbonate:.3f}$ and the water--carbonate interaction is $-0.25$ \cite{{Held2014}}; these fits keep the observation weights and parameter bounds of the models.')
def transfer_displays(outputs):
    BASE = 'analyses/dea_transfer/results/refit-413/'
    MEA = 'analyses/mea_parameter_bundle/results/'  # read as retained files, so replacing them refreshes every MEA number shown here
    SALT = MEA + 'salt-anchored-435/'
    MEAFIT = SALT + 'MEA/F4/'
    MEAEVIDENCE = SALT + 'MEA/evidence/F4/'
    ROUND7 = 'analyses/round_7/'
    ROUND8 = 'analyses/round_8/results/'

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
        'Horstmann VLE': ('Horstmann et al.', 'horstmannPhaseEquilibriumExcess2002', 'bubble pressure'),
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

    def table(name, caption, headers, rows, widths, long=False, notes='', size=r'\small', spec=''):
        columns = spec or ''.join(r'>{\raggedright\arraybackslash}p{' + str(w) + r'\linewidth}' for w in widths)
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
    amp_outcomes = read(W_AMP_CONTROLS)['rows']
    amp_enthalpy = fit_summary['amp_enthalpy']

    ddoc, mdoc, adoc = [fixed.fits[name]['endpoint'] for name in ('DEA', 'MDEA', 'AMP_free')]
    dassessment = fixed.endpoint_record('DEA/property-comparisons/selected.json.gz', 'DEA')
    aassessment = fixed.endpoint_record('AMP_free/properties.json.gz', 'AMP_free')
    dcoords, acoords = (coordinates(fixed.conditional(name)) for name in ('DEA', 'AMP_free'))

    fitted_names = [r'$k_{\mathrm{DEAH^+,w}}$ at 313.15 K', r'$k_{\mathrm{DEACOO^-,w}}$', r'R4 constant term $A_4$', r'R4 enthalpy increment $\delta h$',
                    r'$b_{\mathrm{DEAH^+,w}}$ (K)', r'$k_{\mathrm{DEAH^+,CO_2}}$']
    head = lambda text, n: [r'\addlinespace\multicolumn{' + str(n) + r'}{@{}l}{\textit{' + text + '}}']
    fit_rows = [head('DEA', 5)]
    binary_replay = read(W_DEA_BINARY)['rows']
    for row in binary_replay:
        result = row["law"]
        if result["status"] != "Available" or result.get("requested_tolerance_met") is False:
            raise ValueError(f"Incomplete DEA binary replay for {row['row']['source_key']} "
                             f"row {row['row']['source_row']}: {result}")
    binary = [dict(row, **row['law'], outside_ranges={law: None for law in LAWS}) for row in binary_replay]
    data = [r for r in dassessment['rows'] if r['group'] not in ('Cai', 'Horstmann')] + binary


    def deviations(rows):
        relative = [100 * (r['value'] / r['observed'] - 1) for r in rows
                    if r['status'] == 'Available' and r['observed'] != 0]
        return dict(rows=sum(r['status'] == 'Available' for r in rows), relative_rows=len(relative),
                    AARD_percent=math.fsum(map(abs, relative)) / len(relative) if relative else None,
                    bias_percent=math.fsum(relative) / len(relative) if relative else None)


    dev = {group: deviations([r for r in data if r['group'] == group]) for group in SETS}

    def marks(rs):
        out = []
        for law in LAWS:
            flags = {x['outside_ranges'][law] for x in rs}
            out.append('mixed' if len(flags)>1 else ('out' if True in flags else 'in' if False in flags else '---'))
        return out

    def composition(group, rs):
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
        group_rows = [r for r in data if r['group'] == group]
        roles = list(dict.fromkeys(r['role'] for r in group_rows))
        for role in roles:
            rs = [r for r in group_rows if r['role'] == role]
            t = [r['T_K'] for r in rs]
            score = deviations(rs)
            data_rows.append([name(group, cite=True), SETS[group][2], role, count(len(rs), score['relative_rows']),
                              span(t, lambda v: num(v,2)), *composition(group, rs), *marks(rs),
                              num(score['AARD_percent'],2), num(score['bias_percent'],2)])
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
    DEA_FITTED = dict(zip(dcoords, fitted_names, strict=True))
    DEA_PAIR_COORDINATES = {
        'protonated-diethanolamine/water/k_ij_reciprocal_temperature_slope': 'k-DEAH-water-slope',
        'carbon-dioxide/protonated-diethanolamine/k_ij': 'k-DEAH-CO2',
    }
    FITTED = DEA_FITTED | {key: DEA_FITTED[coord].removesuffix(' (K)')
                          for key, coord in DEA_PAIR_COORDINATES.items()}
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
            ax.plot([q['loading'] for q in line], values, color=color, ls=style)
            ax.plot([], [], color=color, ls=style, marker=marker, markersize=4.5,
                    markerfacecolor=color if all(q['role'] == 'fitted' for q in obs) else 'none', label=f'{T:.2f} K')
            for role in dict.fromkeys(q['role'] for q in obs):
                measured = [q for q in obs if q['role'] == role]
                ax.scatter([loading(q['row']) for q in measured], [q['observed']/1000 for q in measured],
                           s=25, marker=marker, edgecolors=color, facecolors=color if role == 'fitted' else 'none')
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
    fig,axes=plt.subplots(1,2,figsize=(6.48,3.0),constrained_layout=True)
    for ax,group,scale,letter in [(axes[0],'Horstmann',1,'a'),(axes[1],'Cai',0.001,'b')]:
        ps=[r for r in data if r['group']==group and r['status']=='Available']
        ax.scatter([float(r['row']['x_water']) for r in ps],[r['observed']*scale for r in ps],facecolors='none',edgecolors=colors[0],label='Measured')
        ax.scatter([float(r['row']['x_water']) for r in ps],[r['value']*scale for r in ps],marker='x',color=colors[1],label='DEA model')
        ax.set_title(f'({letter})', loc='left'); ax.set(xlabel='Water mole fraction',ylabel='Excess enthalpy (J/mol mixture)' if group=='Horstmann' else 'Bubble pressure (kPa)')
        ax.legend(fontsize=8, loc='center' if group=='Horstmann' else 'upper right')
    figure(fig,'dea-current-binary-comparisons.pdf')
    # MDEA and AMP: the same displays, built from each amine's retained files.
    critical = read(W_MDEA_BINARY)
    fig, ax = plt.subplots(figsize=(3.2, 2.7), constrained_layout=True)
    def mdea_water(point):
        law, = [c['temperature_law'] for pair in point['parameters']['pairs']
            if {pair['component_id_a'], pair['component_id_b']} == {'water', 'methyldiethanolamine'}
            for c in pair['coefficients']]
        return [t['coefficient']['value']['magnitude'] for t in law['terms']]


    temperatures = [r['T_K'] for r in critical['rows']]
    k0, slope = mdea_water(mdoc)
    ax.plot(temperatures, [k0 + slope * (T - 423.0) for T in temperatures], color=colors[0], label='MDEA model')
    ax.scatter([r['T_K'] for r in critical['rows']], [r['k_gap'] for r in critical['rows']], s=12, marker='o', facecolors='none', edgecolors=colors[1], label='Calculated gap onset')
    ax.set(xlabel='Temperature (K)', ylabel=r'$k_{\mathrm{MDEA,w}}$')
    ax.legend()
    figure(fig, 'mdea-gap-onset.pdf')
    AM = 'analyses/amp_transfer/results/retransfer-412-f2-05e94210/'  # #412: F2 carbamate inputs
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
    def amp_mass_percent(feed):
        return 100*amass['aminomethylpropanol']/(amass['aminomethylpropanol'] + amass['water']*float(feed['water']))
    def amp_basis(rs):
        feed = [afeed[r['identity']] for r in rs]
        if 'x_AMP' in rs[0]['row']: return r'$x_{\mathrm{A}}=\,$' + span([float(r['row']['x_AMP']) for r in rs], sig), '---'
        wt = list(map(amp_mass_percent, feed))
        return span(wt, sig) + r' wt\%', span([float(f['alpha']) for f in feed], sig)
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
    dflat.update({key: (dcoords[key]['value'], unit) for key, unit in zip(
        list(DEA_FITTED)[:4], ('dimensionless', 'dimensionless', 'dimensionless', 'J/mol'), strict=True)})
    fit_rows[1:1] = [[label + (' (J/mol)' if i == 3 else ''), bold(num(r['value'], d)), num(r['error'], d),
                      bounds(*r['bounds'], d), ''] for i, (label, r) in enumerate(zip(fitted_names, dcoords.values(), strict=True))
                     for d in [0 if i == 3 else 3]]
    fit_rows += [head('AMP', 5)] + [[label, bold(num(r['value'], d) + (r'\textsuperscript{a}' if r['on_bound'] else '')),
                                    '---' if r['on_bound'] else num(r['error'], d), bounds(*r['bounds'], d), '']
                                   for (label, d), key in zip(AFIT, aorder, strict=True) for r in [acoords[key]]]
    level = lambda q: [r'R4 change at 313.15 K, $\Delta\ln K_4$\textsuperscript{c}', f"${q['delta_ln_K4']:+.3f}$", num(q['SE_ln_K4'], 3), bounds(*q['bounds']['level'], 3), '']
    fit_rows[4][1:4] = [bold(num(r4['dea']['delta_h_J_mol'], 0)), num(r4['dea']['SE_h_J_mol'], 0), bounds(*r4['dea']['bounds']['enthalpy'], 0)]
    amp_enthalpy_bound = acoords['AMP-hydrolysis-enthalpy-increment']['on_bound']
    fit_rows[-1][1:4] = [
        bold(num(r4['amp']['delta_h_J_mol'], 0) + (r'\textsuperscript{a}' if amp_enthalpy_bound else '')),
        '---' if amp_enthalpy_bound else num(r4['amp']['SE_h_J_mol'], 0),
        bounds(*amp_enthalpy['AMP_free']['physical_bounds_J_mol'], 0),
    ]
    fit_rows.insert(4, level(r4['dea']))
    fit_rows.insert(len(fit_rows) - 1, level(r4['amp']))
    # fit_rows: name, value, standard error, bounds and an unused fifth cell. The main text omits the bounds; the supplement lists them.
    columns = lambda n, keep: [[r[0].replace('multicolumn{5}', 'multicolumn{' + str(n) + '}')] if len(r) == 1 else keep(r) for r in fit_rows]
    # One main-text table per amine; the supplement's bounds table keeps the level change of R4 at 313.15 K as a row.
    main_fit = [r for r in columns(3, lambda r: r[:3]) if not r[0].startswith('R4 change')]
    starts = [i for i, r in enumerate(main_fit) if len(r) == 1] + [len(main_fit)]
    dea_fit, mdea_fit, amp_fit = (main_fit[i + 1:j] for i, j in zip(starts, starts[1:]))
    amp_bounds = fixed.fits['AMP_free']['diagnostics']['active_bounds']
    amp_bound_note = (r'\textsuperscript{a}On its lower bound; no standard error is assigned. '
                      if all(amp_bounds.get(key) == 'lower' for key in ('AMPCOO-segment-diameter', 'AMP-hydrolysis-enthalpy-increment')) else '')
    enthalpy_note = r'$\delta h$ is measured from the starting R4 correlation of Table~\ref{tab:reaction-equilibrium-constants}; the final R4 coefficients include it (Table~\ref{supp-tab:supplement-transfer-parameters}). '
    errors_note = r'Standard errors follow Eq.~\eqref{eq:conditional-covariance}; Table~\ref{supp-tab:supplement-transfer-bounds} gives the bounds.'
    for name, label, rows_, note in (('dea-fitted', 'DEA', dea_fit, enthalpy_note), ('mdea-fitted', 'MDEA', mdea_fit, ''),
                                     ('amp-fitted', 'AMP', amp_fit, amp_bound_note + enthalpy_note)):
        table(name, f'Fitted parameters of the {label} model.', ['Parameter', 'Value', 'Standard error'], rows_, [.46, .2, .2],
              notes='Bold: fitted in this work. ' + note + errors_note)
    table('supplement-transfer-bounds', 'Bounds of the fitted parameters of the DEA, MDEA and AMP models.', ['Parameter','Lower bound','Upper bound'], columns(3, lambda r: [r[0].replace(r'\textsuperscript{c}', ''), *r[3][1:-1].split(', ')]), [.50,.20,.20],
          notes=r'The parameters are those of main-text Tables~\ref{main-tab:dea-fitted}--\ref{main-tab:amp-fitted}. For DEA and AMP the bounds of $\delta h$ and of $\Delta\ln K_4$ are measured from the starting R4 correlations, like the values of those tables.')
    apure, ROLE = read(AM344 + 'pure-binary-on-05e94210.json')['pure'], {'fitted': 'fitted', 'assessment_not_fitted': 'not fitted'}
    data_rows.append(head('AMP, pure component', 11))
    for key, who in [('Klepacova2011', r"Klep\'a\v{c}ov\'a et al.\ \cite{klepacovaVaporPressuresSeveral2011}"), ('Belabbaci2010', r'Belabbaci et al.\ \cite{belabbaciInvestigationIsothermalVapour2010}'), ('Pappa2006', r'Pappa et al.\ \cite{pappaMeasurementThermodynamicModeling2006}'), ('Ayad2023', r'Ayad et al.\ \cite{ayadMeasurementsModelingThermodynamic2023}')]:
        g, t = apure['groups'][key], [r['T_K'] for r in apure['rows'] if r['campaign'] == key]
        data_rows.append([who, g['metric'], ROLE[g['role']], str(g['n']), span(t, lambda v: num(v,2)), 'pure AMP', '---', '---', '---', *([num(g['AARD_percent'],2), num(g['signed_relative_bias_percent'],2)] if 'AARD_percent' in g else [r'---\textsuperscript{b}', '---'])])
    mdea_literature = read(W_MDEA_PUBLISHED)['comparisons']
    literature_by_source = {
        MSETS[group['group']][0] + r' \cite{' + MSETS[group['group']][1] + '}':
        ' / '.join(f"{published['mean_absolute_relative_deviation_percent']:g}"
                   for published in group['published_parameter_sets'])
        for group in mdea_literature
    }
    transfer_rows = [[*row[:7], *row[9:], literature_by_source.get(row[0], '---')]
                     if len(row) > 1 else [row[0].replace(r'\multicolumn{11}', r'\multicolumn{10}')]
                     for row in data_rows]
    # MDEA data sets whose measured or assigned pressure the model puts in its liquid-vapor region.
    mdea_groups = {r['identity']: r['group'] for r in read(W_MDEA_PROPERTIES)['rows']}
    vapor_states = collections.Counter()
    for state in read(W_MDEA_SCREEN)['classifications']:
        identity = state['key'].rsplit(':', 1)[0]
        group = mdea_groups.get(identity) or mdea_groups.get(identity.rsplit(':', 1)[0])
        if group in MSETS and state['liquid_vapor']['qualified'] and min(state['liquid_vapor']['amounts_mol']) > 0:
            vapor_states[group] += 1
    for group in [g for g in MSETS if g.startswith('Bottinger-bicarbonate-')]:
        # The bicarbonate rows are the same NMR states as the amine-sum rows, which carry the search.
        vapor_states[group] = vapor_states[group.replace('bicarbonate', 'amine-sum')]
    for group in ('unloaded-density', 'Bottinger-amine-sum-5bar', 'Bottinger-amine-sum-25bar', 'Bottinger-bicarbonate-5bar',
                  'Bottinger-bicarbonate-25bar', 'Zheng'):
        title, source, _ = MSETS[group]
        next(r for r in transfer_rows if r[0] == title + r' \cite{' + source + '}')[3] += r'\textsuperscript{c}'
    sobrino, nmr5, nmr25, zheng = ((vapor_states[g], sum(r['group'] == g for r in mrows))
                                   for g in ('unloaded-density', 'Bottinger-amine-sum-5bar', 'Bottinger-amine-sum-25bar', 'Zheng'))
    assert nmr5[1] == nmr25[1]
    vapor_note = (f'At {sobrino[0]} of the {sobrino[1]} states of Sobrino et al., {nmr5[0]} and {nmr25[0]} of the {nmr5[1]} '
                  r'states of B\"ottinger et al.\ at 0.5 and 2.5 MPa and '
                  + (f'all {count_word(zheng[1])}' if zheng[0] == zheng[1] else f'{zheng[0]} of the {zheng[1]}') + ' states of Zheng et al.')
    nmr_pairs = {frozenset(r['row']['source_row'] for r in mrows if r['group'] == g)
                 for g in MSETS if g.startswith('Bottinger-')}
    (nmr_keys,) = nmr_pairs
    nmr_rows = len(nmr_keys)
    AMINES = [('DEA', dflat, 'diethanolamine'), ('MDEA', flatten(mdoc, {'methyldiethanolamine', 'protonated-methyldiethanolamine'}), 'methyldiethanolamine'), ('AMP', flatten(adoc, {'aminomethylpropanol', 'protonated-aminomethylpropanol', 'carbamate-anion'}), 'aminomethylpropanol')]
    # Values fitted in this work, by key of each retained record: the reactive fit of each amine (checked against its fit record) and the fits made beforehand:
    # the permittivity coefficients (Hsieh et al.), the water--DEA interaction (Horstmann et al.) and the five pure-AMP parameters.
    MKEYS = ['methyldiethanolamine/water/k_ij', 'methyldiethanolamine/water/k_ij_temperature_slope', 'carbon-dioxide/protonated-methyldiethanolamine/k_ij', 'protonated-methyldiethanolamine/water/k_ij',
             'protonated-methyldiethanolamine/water/k_ij_reciprocal_temperature_slope', 'bicarbonate-anion/protonated-methyldiethanolamine/k_ij', 'protonated-methyldiethanolamine/segment_diameter', 'protonated-methyldiethanolamine/dispersion_energy_over_k']
    AKEYS = ['aminomethylpropanol/water/k_ij', 'aminomethylpropanol/water/k_ij_reciprocal_temperature_slope', 'protonated-aminomethylpropanol/water/k_ij', 'protonated-aminomethylpropanol/water/k_ij_reciprocal_temperature_slope',
             'carbon-dioxide/protonated-aminomethylpropanol/k_ij', 'protonated-aminomethylpropanol/segment_diameter', 'carbamate-anion/segment_diameter', 'carbamate-hydrolysis/a']
    APURE = dict(zip(['aminomethylpropanol/segment_count', 'aminomethylpropanol/segment_diameter', 'aminomethylpropanol/dispersion_energy_over_k', 'association/aminomethylpropanol/a/aminomethylpropanol/b/energy_over_k', 'association/aminomethylpropanol/a/aminomethylpropanol/b/volume'], ['m', 'sigma', 'epsilon', 'eps_ab', 'kappa']))
    permittivity = lambda s: {s + '/dielectric_volume', s + '/dielectric_temperature'}
    FITTED_HERE = [set(FITTED) | DEA_PAIR_KEYS | permittivity('diethanolamine') | {
                      'diethanolamine/water/k_ij', 'diethanolamine/water/k_ij_reciprocal_temperature_slope',
                      'protonated-diethanolamine/water/k_ij_reciprocal_temperature_slope',
                      'carbon-dioxide/protonated-diethanolamine/k_ij', 'k-DEAH-water-slope', 'k-DEAH-CO2'},
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
    # Sensitivity of the MEA fit to the two Born diameters set at 3.0 A (supplement): the tested diameters, the largest objective change and the largest shifts of fitted CO2 partial pressures.
    born = read(BORN)
    born_cost = f"at most {100 * max(abs(c['cost'] / born['reference_cost'] - 1) for c in born['cases']):.2f}"
    [born_cost, f"{dflat['carbamate-anion/dispersion_energy_over_k'][0]:.4f}", f"{f2['component/carbamate-anion/segment_diameter']:.4f}", f'{size_ratio:.4f}', f'{born_oh:.4f}', '$-106.4$ kcal/mol', '78.37']
    ROWS = [(0, 'diethanolamine', r'\ce{DEA}'), (0, 'protonated-diethanolamine', r'\ce{DEAH+}'), (0, 'carbamate-anion', r'\ce{DEACOO-}'), (1, 'methyldiethanolamine', r'\ce{MDEA}'), (1, 'protonated-methyldiethanolamine', r'\ce{MDEAH+}'), (2, 'aminomethylpropanol', r'\ce{AMP}'), (2, 'protonated-aminomethylpropanol', r'\ce{AMPH+}'), (2, 'carbamate-anion', r'\ce{AMPCOO-}')]
    table('transfer-species', 'Segment, association and Born parameters of the DEA, MDEA and AMP species.', ['Species', r'$m^{\mathrm{seg}}$', r'$\sigma$ (\AA)', r'$u/k_B$ (K)', r'$\epsilon^{AB}/k_B$ (K)', r'$\kappa^{AB}$', r'$d^{\mathrm{Born}}$ (\AA)', 'Ref.'], [species_row(AMINES[i][1], s, label, source, FITTED_HERE[i]) for (i, s, label), source in zip(ROWS, SOURCE)], [.12,.10,.10,.12,.13,.10,.12,.14],
          notes=r'The columns are those of Table~\ref{tab:species-parameters}. Bold: fitted in this work; in a row of this work, the values in normal weight are fixed; --: not used. \textsuperscript{a}DEA values, with zero self-association energy. \textsuperscript{b}Dispersion energy of \ce{MEACOO-} in the MEA model and its diameter scaled to DEA (Section~\ref{supp-sec:s-parameters}). \textsuperscript{c}Segment parameters of Ref.~\cite{Pahlavanzadeh2013} and association parameters of Ref.~\cite{Uyan2015}; association volume converted in this work. \textsuperscript{d}Segment count and association volume of MDEA; zero self-association energy. \textsuperscript{e}Fitted beforehand to pure-AMP data. \textsuperscript{f}Dispersion energy of AMP. \textsuperscript{g}Dispersion energy of \ce{MEACOO-} in the MEA model; diameter fitted with that of \ce{MEACOO-} as its lower bound. Tables~\ref{tab:dea-fitted}--\ref{tab:amp-fitted} give the standard errors of the values fitted in the reactive fits, and Table~\ref{supp-tab:supplement-transfer-parameters} unrounded values and the remaining inputs.')
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
        if who == 'DEA' and key == 'carbamate-hydrolysis/b':
            return r'Starting R4 law and fitted $\delta h$'
        if who == 'AMP' and key in ('carbamate-anion/dispersion_energy_over_k', 'carbamate-anion/water/k_ij'):
            return r'\ce{MEACOO-}, MEA model'
        if who == 'AMP' and key == ASLOPE: return 'Set in this work (scan)'
        if who == 'DEA' and key == 'bicarbonate-anion/protonated-diethanolamine/k_ij':
            return r'Inherited from MEA, \ce{MEAH+}--\ce{HCO3-}'
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
        keys = list(record)
        if who == 'DEA':
            order = {key: i for i, key in enumerate(FITTED)}
            keys = sorted((key for key in keys if key not in DEA_PAIR_KEYS | {'carbamate-hydrolysis/a'}),
                          key=lambda key: order.get(key, -1))
        for key in keys:
            value, unit = record[key]
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
          notes=r'Bold values were fitted in this work; main-text Tables~\ref{main-tab:dea-fitted}--\ref{main-tab:amp-fitted} give the standard errors of the parameters of the reactive fits, and Table~\ref{tab:supplement-transfer-bounds} their bounds. For DEA, the R4 coefficients $A_4$ and $B_4$ are printed as their values after the fit of $A_4$ and $\delta h$. For DEA and AMP, $\delta h$ is measured from the starting R4 correlation, as in the main-text tables, and is contained in $B_4$. R4: carbamate hydrolysis; R5: amine dissociation; $\ln K=a+b/T+c\ln(T/T_{\mathrm{ref}})+dT$ with $T$ in K and $T_{\mathrm{ref}}=313.15$ K, on the common-molality reference basis; coefficients not listed are zero. For R4, where $c=d=0$, $a$ and $b$ are written $A_4$ and $B_4$: they are the coefficients of main-text Eq.~(\ref{main-eq:reaction-equilibrium-constant-temperature}) on that basis, with $\Delta_4=0$. Binary dispersion interactions not listed are zero; a $k_{ij}$ with a slope is the value at 313.15 K, except MDEA--water, at 423 K. Each of the chain cations DEAH$^+$ and MDEAH$^+$ keeps the dispersion between its own segments. ``DEA value\textquotedblright{}, ``MDEA value\textquotedblright{} and ``AMP value\textquotedblright{}: the value of the molecular amine. The data deposit gives the source and basis of each value.')
    def amp_loading(r):
        return float(r['row']['alpha_mol_CO2_per_mol_AMP'])

    def draw_series(ax, observed, curves, loading, pressure=False, line_styles=None):
        temperatures = sorted(set(observed) | set(curves))
        markers = ('o', 's', '^', 'v', 'D', 'P', 'X')
        for i, temperature in enumerate(temperatures):
            color = plt.colormaps['viridis'](i / max(1, len(temperatures) - 1))
            for role in ('fitted', 'not fitted', 'comparison only'):
                rows = [r for r in observed.get(temperature, []) if r['role'] == role]
                if rows:
                    ax.scatter([loading(r) for r in rows], [r['observed'] / (1000 if pressure else 1) for r in rows],
                               marker=markers[i % len(markers)], s=18, edgecolors=color,
                               facecolors=color if role == 'fitted' else 'none')
            for series, line in curves.get(temperature, []):
                xs, ys = zip(*sorted(line))
                ax.plot(xs, ys, color=color, ls=line_styles[series] if line_styles else '-')
            filled = all(row['role'] == 'fitted' for row in observed.get(temperature, []))
            ax.plot([], [], color=color, marker=markers[i % len(markers)], ms=3.5,
                    markerfacecolor=color if filled else 'none', label=f'{temperature:g} K')
        ax.legend(fontsize=7)

    def group_curves(rows, x="loading", scale=1, series="curve"):
        grouped = collections.defaultdict(list)
        for row in rows:
            value = row['value'] / scale if row['status'] == 'Available' and row['requested_tolerance_met'] else math.nan
            grouped[row['T_K'], row[series]].append((row[x], value))
        curves = collections.defaultdict(list)
        for (temperature, identity), points in grouped.items():
            curves[temperature].append((identity, points))
        return curves

    def observations_by_temperature(rows):
        grouped = collections.defaultdict(list)
        for row in rows:
            grouped[float(row['T_K'])].append(row)
        return grouped

    mdea_curves = [r for r in fixed.load('MDEA/properties.json.gz')['curves']
                   if r['group'] == 'Kuranov']
    mdea_pressures = [r for r in mrows if r['group'] in ('Kuranov', 'Kuranov-413K')]
    fitted_mdea_pressures = [r for r in mdea_pressures if r['group'] == 'Kuranov']
    stocks = sorted({float(r['row']['m_MDEA_mol_per_kg_H2O']) for r in fitted_mdea_pressures})
    fig, axes = plt.subplots(1, len(stocks), figsize=(6.48, 2.85), sharey=True, constrained_layout=True)
    for ax, molality in zip(axes, stocks, strict=True):
        measured, curves = collections.defaultdict(list), collections.defaultdict(list)
        for r in fitted_mdea_pressures:
            if float(r['row']['m_MDEA_mol_per_kg_H2O']) == molality:
                T = float(r['row']['source_series'].rsplit(' ', 2)[-2]) + .15
                measured[T].append(r)
        for r in mdea_curves:
            if float(r['row']['m_MDEA_mol_per_kg_H2O']) == molality:
                if not curves[r['T_K']]:
                    curves[r['T_K']].append((None, []))
                curves[r['T_K']][0][1].append((r['loading'], r['value'] / 1000 if r['status'] == 'Available' else math.nan))
        draw_series(ax, measured, curves, mdea_loading, pressure=True)
        ax.set(title=f'{molality:g} mol/kg water', xlabel='Loading (mol CO$_2$/mol MDEA)', yscale='log')
    axes[0].set_ylabel('Total pressure (kPa)')
    figure(fig, 'mdea-isotherms.pdf')

    a_curves = aassessment['curves']
    fig, axes = plt.subplots(1, 2, figsize=(6.48, 3), sharey=True, constrained_layout=True)
    for ax, title, groups in zip(axes, ('(a) Hartono et al.', '(b) Tong et al.'),
                                 ({'loaded-pressure', 'hartono-2021-supplemental'}, {'tong'}), strict=True):
        observed = observations_by_temperature(r for r in arows if r['group'] in groups)
        curves = group_curves((r for r in a_curves if r['group'] in groups), scale=1000)
        draw_series(ax, observed, curves, amp_loading, pressure=True)
        ax.set(title=title, xlabel='Loading (mol CO$_2$/mol AMP)', yscale='log')
    axes[0].set_ylabel('Total pressure (kPa)')
    figure(fig, 'amp-isotherms.pdf')

    fig, axes = plt.subplots(2, 2, figsize=(6.48, 4.6), constrained_layout=True)
    speciation_loading = lambda row: float(row['row']['loading'])
    speciation = [row for row in mrows if row['group'].startswith('Bottinger-')]
    mdea_species = fixed.load('MDEA/properties.json.gz')['speciation_curves']
    masses = {q['component_id']: q['fixed']['molar_mass']['value']['magnitude']
              for q in mdoc['parameters']['components']}
    amine_mass = masses['methyldiethanolamine']
    ratios = {row['water_per_mole_amine'] for row in mdea_species}
    nominal_stocks = {ratio: 10 * round(10 * amine_mass / (amine_mass + ratio * masses['water']))
                      for ratio in ratios}
    stock_styles = dict(zip(sorted(set(nominal_stocks.values())), ('-', '--', ':'), strict=True))
    styles = {ratio: stock_styles[wt] for ratio, wt in nominal_stocks.items()}
    for ax, group in zip(axes.flat, dict.fromkeys(row['group'] for row in speciation), strict=True):
        observed = observations_by_temperature(row for row in speciation if row['group'] == group)
        curves = group_curves((row for row in mdea_species if row['group'] == group),
                              series="water_per_mole_amine")
        draw_series(ax, observed, curves, speciation_loading, line_styles=styles)
        ax.set(title=('MDEA + MDEAH$^+$' if 'amine-sum' in group else 'Bicarbonate + carbonate')
               + (' at 0.5 MPa' if group.endswith('-5bar') else ' at 2.5 MPa'),
               xlabel='Loading (mol CO$_2$/mol MDEA)', ylabel='Mole fraction')
    fig.legend(handles=[matplotlib.lines.Line2D([], [], color='0.25', ls=style, label=f'{wt} wt% MDEA')
                        for wt, style in stock_styles.items()], title='Nominal stock',
               loc='outside lower center', ncols=len(stock_styles))
    figure(fig, 'mdea-speciation.pdf')

    # The AMP fit without the Tong and hot Hartono pressures is the comparison whose splits the paper names.
    aclass = read(W_AMP_WITHOUT_HOT)
    cell = lambda s: num(s['AARD_percent'],2) + ' (' + str(s['rows']) + ')'
    def pressure_cell(rows):
        available = [r for r in rows if r.get('status', 'Available').lower() == 'available']
        if not available:
            return 'none'
        return cell(dict(stats(available, predicted='value'), rows=len(available)))

    def split_pressures(pools, within):
        groups = []
        for symbol, pool in pools:
            inside, outside = [], []
            for row in pool:
                (inside if within(row) else outside).append(row)
            groups.append((symbol + ': ' + pressure_cell(inside), symbol + ': ' + pressure_cell(outside)))
        return tuple('; '.join(cells) for cells in zip(*groups, strict=True))

    def fitted_conditions(fitted, conditions):
        temperatures, concentrations = zip(*map(conditions, fitted))
        def within(row):
            temperature, concentration = conditions(row)
            return (min(temperatures) <= temperature <= max(temperatures)
                    and min(concentrations) <= concentration <= max(concentrations))
        return within, temperatures, concentrations

    pco2, ptotal = r'$p_{\COtwo}$', '$P$'
    efit = [eprops[k] for k in fitted_pressure]
    wagner = mea_replay['hot_wagner'] + fixed.endpoint_record('display-replays/wagner.json.gz', 'MEA')['rows']
    enot = ([eprops[r['target']] for r in mea_pressure if r['target'] not in fitted_pressure] + wagner
            + [r for r in mea_off if r['group'] == 'Aronu2011'])
    mea_inside = {row['target'] for role, row, _ in mea_nominal_pressure_rows()
                  if role != 'fitted' and temperature_band(float(row['temperature_K'])) == 'absorber'}
    if collections.Counter(r['identity'] for r in enot if r['identity'] in mea_inside) != dict.fromkeys(mea_inside, 1):
        raise ValueError('The MEA summary pool must contain each held-out absorber observation once')
    _, mea_outside = split_pressures([(pco2, enot)], lambda r: r['identity'] in mea_inside)
    # MEA pressures are fitted at 313-333 K only, so the absorber-band pool splits at the fitted temperatures.
    mea_hot_inside = {target for target, _ in mea_held_out_absorber_split()[1]}
    mea_within = (pco2 + ': ' + pressure_cell([r for r in enot if r['identity'] in mea_inside - mea_hot_inside])
                  + '; ' + pco2 + r' at \SI{353}{\kelvin}\textsuperscript{b}: '
                  + pressure_cell([r for r in enot if r['identity'] in mea_hot_inside]))

    dloaded = {'Lawson', 'Lawson-394K', 'SeoHong', 'Lal', 'Lawson-VIII'}
    dea_pressure = [r for r in data if r['group'] in dloaded and r['unit'] == 'Pa']
    dfit = [r for r in dea_pressure if r['role'] == 'fitted']
    lal_wt = 100 * dea_lal_unloaded_mass_fraction(read(MOVE + 'dea/reported/fit/manifest.json.gz'),
                                                   ddoc['parameters']['components'])
    def dea_conditions(r):
        return r['T_K'], lal_wt if r['group'] == 'Lal' else float(r['row']['DEA_mass_percent'])
    dea_inside, dea_temperatures, dea_concentrations = fitted_conditions(dfit, dea_conditions)
    # The DEA objective fits pressures at or above 0.05 kPa, so the lower Lal pressures lie outside its fitted conditions.
    dea_floor = min(float(r['observed']) for r in dfit)
    # Measured Haji-Sulaiman pressures only; their stage asserts the fitted temperature and pressure range.
    haji = [r for r in read(MOVE + 'dea/reported/held-out-pressures/summary.json.gz')['sources']['HajiSulaiman1998']['rows']
            if r.get('value') is not None]
    dea_within, dea_outside = split_pressures(
        [(pco2, [r for r in dea_pressure if r['role'] != 'fitted'] + haji)],
        lambda r: r['group'] == 'HajiSulaiman1998' or (dea_inside(r) and float(r['observed']) >= dea_floor))

    mdea_pressures = [r for r in mdea_pressure_rows(read(W_MDEA_PROPERTIES)) if r['unit'] == 'Pa']
    mloaded = [r for r in mdea_pressures if r['group'] == 'Kuranov' and r['role'] == 'fitted']
    kuranov = {r['source_row']: r for r in read(KURANOV_DATA)}
    def mdea_conditions(r):
        source = r['row']
        if r['group'].startswith('Kuranov'):
            source = kuranov[source['source_row']]
            # Use the named isotherm, including the retained 393 K supplemental point.
            T = float(source['source_series'].rsplit(' ', 2)[-2])
            return T, round(float(source['m_MDEA_mol_per_kg_H2O']))
        if r['group'] == 'Ermatchkov':
            # The measured molalities vary within the nominal source stocks.
            return round(r['T_K']), float(source['source_series'].split()[-2])
        if r['group'] == 'corrected-Kamps':
            return r['T_K'], float(source['m_MDEA_mol_kg_water'])
        fraction = float(source['unloaded_MDEA_mass_fraction'])
        return round(r['T_K']), fraction / ((1 - fraction) * amine_mass)
    mdea_inside, mdea_temperatures, mdea_concentrations = fitted_conditions(mloaded, mdea_conditions)
    mdea_partial = {'Ermatchkov', 'Xiao'}
    mnot = [r for r in mdea_pressures if r['role'] != 'fitted']
    mdea_within, mdea_outside = split_pressures(
        [(ptotal, [r for r in mnot if r['group'] not in mdea_partial]),
         (pco2, [r for r in mnot if r['group'] in mdea_partial])], mdea_inside)
    def mdea_loading(r):
        source = kuranov[r['row']['source_row']] if r['group'].startswith('Kuranov') else r['row']
        for k in ('alpha_exp', 'alpha_mol_CO2_per_mol_MDEA'):
            if source.get(k) not in (None, ''):
                return float(source[k])
        k = next(k for k in ('m_CO2_mol_per_kg_H2O', 'm_CO2_mol_kg_water') if source.get(k) not in (None, ''))
        return float(source[k]) / float(source[k.replace('CO2', 'MDEA')])
    # The fitted conditions are temperature and content only; held-out MDEA pressures inside them reach lower loadings.
    mdea_loading_floor = min(map(mdea_loading, mloaded))
    mdea_inside_held = [r for r in mnot if mdea_inside(r) and r.get('status', 'Available').lower() == 'available']
    mdea_below_floor = sum(mdea_loading(r) < mdea_loading_floor for r in mdea_inside_held)

    amp_loaded = {'loaded-pressure', 'hartono-2021-supplemental', 'tong'}
    aloaded = [r for r in arows if r['group'] in amp_loaded and r['unit'] == 'Pa' and r['role'] == 'fitted']
    def amp_conditions(r):
        return r['T_K'], amp_mass_percent(afeed[r['identity']])
    amp_inside, amp_temperatures, amp_concentrations = fitted_conditions(aloaded, amp_conditions)
    amp_free = [r for r in arows if r['group'] == 'tong-baseline']
    if any(float(afeed[r['identity']]['alpha']) for r in amp_free):
        raise ValueError('The held-out AMP total pressures of Tong et al. are no longer all CO2-free')
    amp_within, amp_outside = split_pressures(
        [(ptotal + r', \COtwo-free', amp_free),
         (pco2, [r for r in arows if r['group'] == 'kundu'])], amp_inside)

    unclassified = []
    def measured_coverage(record):
        phase = read(record)
        measured = [row for row in distinct_phase_rows(phase) if not row["key"].startswith("grid:")]
        classified = {row["key"] for row in measured if search_class(row) in ("descent", "searched, no instability")}
        splits = str(sum(row["key"] in classified and confirmed_split(row) for row in phase["classifications"]))
        if len(classified) < len(measured):
            unclassified.append((len(classified), len(measured)))
            splits += r'\textsuperscript{a}'
        return splits

    amp_w = MOVE + 'amp/reported/phase/supplied.json.gz'
    mea_measured = [row for row in distinct_mea_measured_rows(read(W_MEA_PHASE + 'measured.json.gz'))
                    if row["available"]]
    mea_no_detection = str(sum(row['descent'] for row in mea_measured))
    rows = [
        ['MEA', len(mea_stage['coordinates']), len(mea_stage['active_bounds']),
         pco2 + ': ' + pressure_cell(efit), mea_within, mea_no_detection],
        ['DEA', len(dcoords), sum(r['on_bound'] for r in dcoords.values()),
         pco2 + ': ' + pressure_cell(dfit), dea_within,
         measured_coverage(W_DEA_SCREEN)],
        ['MDEA', len(mfit), sum(r['on_bound'] for r in mfit),
         ptotal + ': ' + pressure_cell(mloaded), mdea_within,
         measured_coverage(W_MDEA_SCREEN)],
        ['AMP', len(acoords), len(aunc['active_bounds']), ptotal + ': ' + pressure_cell(aloaded), amp_within,
         measured_coverage(amp_w)],
    ]
    salt_data = read(W_SALT)['rows']
    salt_temperatures = sorted({float(r['T']) for group in ('NaHCO3', 'Na2CO3', 'mixed')
                                for r in salt_data[group] if r.get('status') == 'Available'})
    cmap = plt.colormaps['viridis']
    norm = matplotlib.colors.Normalize(min(salt_temperatures), max(salt_temperatures))
    fig, axes = plt.subplots(1, 3, figsize=(6.48, 2.4), constrained_layout=True, sharex=True)
    for ax, salt, title in zip(axes, ('NaHCO3', 'Na2CO3', 'mixed'),
                               ('Sodium bicarbonate', 'Sodium carbonate', 'Mixed salts'), strict=True):
        accepted = [r for r in salt_data[salt] if r.get('status') == 'Available']
        ax.axhline(0, color='0.55', lw=.7)
        ax.scatter([float(r['m']) for r in accepted], [100*r['relative_error'] for r in accepted],
                   c=[float(r['T']) for r in accepted], cmap=cmap, norm=norm, s=18)
        ax.set(title=title, ylabel='Signed residual (%)')
    for ax in axes:
        ax.set(xlabel='Nominal salt molality (mol/kg)', xscale='log')
    fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=axes,
                 ticks=salt_temperatures, label='Temperature (K)', aspect=30)
    figure(fig, 'salt-osmotic-residuals.pdf')

    def conditions_note(label, temperatures, concentrations, unit, extra=''):
        return (label + ' (' + span(temperatures, lambda t: f'{t:.5g}') + ' K, '
                + span(concentrations, lambda c: f'{c:.3g}') + ' ' + unit + extra + ')')
    conditions = ', '.join([
        conditions_note('MEA', [float(r['temperature_K']) for r in mea_pressure
                                if r['target'] in fitted_pressure], [30], r'wt\%'),
        conditions_note('DEA', dea_temperatures, dea_concentrations, r'wt\%', r', $p_{\COtwo}\ge\SI{0.05}{\kilo\pascal}$'),
        conditions_note('MDEA', mdea_temperatures, mdea_concentrations, 'mol/kg water',
                        f'; fitted loadings from {mdea_loading_floor:.3f}, and {mdea_below_floor} of the '
                        f'{len(mdea_inside_held)} held-out MDEA pressures within these conditions lie below it'),
        'and ' + conditions_note('AMP', amp_temperatures, amp_concentrations, r'wt\%'),
    ])
    pressure_note = r'AARD (Eq.~\eqref{eq:aard}) in \% with the number of observations in parentheses. $P$ is total pressure and $p_{\COtwo}$ is \COtwo partial pressure.'
    table('amine-summary', 'The four models: fitted parameters, pressure deviations and predicted liquid--liquid splits.', ['Model', 'Fitted parameters', 'On bounds', 'Fitted loaded-solution pressures', 'Held-out pressures', 'Liquid--liquid splits at measured states'], rows, [.09, .1, .08, .22, .28, .17],
          notes=pressure_note + ' The fitted conditions are the temperatures and nominal unloaded amine contents of the fitted loaded-solution pressures of ' + conditions + '. '
                + f'All {count_word(len(amp_free))} held-out AMP total pressures are \\COtwo-free observations of Tong et al. '
                r'The held-out pressures lie within the fitted conditions, except those marked b. '
                + f'For DEA they are the {len(haji)} measured pressures of Haji-Sulaiman et al. at '
                + span([r['T_K'] for r in haji], lambda t: f'{t:.0f}') + r' K; the smoothed pressures of Lee et al. and the values '
                r'that Kennard and Meisen interpolated within these conditions are not measurements and are compared in Section~\ref{sec:results-dea}. '
                r'Supplementary Table~\ref{supp-tab:transfer-deviations} gives deviations outside the fitted conditions. '
                + ''.join(rf'\textsuperscript{{a}}At the {c} of {n} measured states that the search classified (Section~\ref{{supp-sec:s-phase}}).' for c, n in unclassified)
                + r' \textsuperscript{b}Above the fitted MEA temperatures and not among the deviations outside the fitted conditions.')
    pooled = [head('Pooled pressure deviations outside the fitted conditions', 10)]
    for label, deviation in zip(('MEA', 'DEA', 'MDEA', 'AMP'),
                                (mea_outside, dea_outside, mdea_outside, amp_outside), strict=True):
        pooled.append([label, r'\multicolumn{9}{l}{' + deviation + '}'])
    table('transfer-deviations',
          r'Pooled pressure deviations outside the fitted conditions, followed by data and model deviations for DEA, MDEA and AMP by source.',
          ['Source', 'Observable', 'Role', '$N$', '$T$ (K)', 'Amine content', 'Loading',
           r'AARD (\%)', r'Bias (\%)', r'Published AARD (\%)'],
          pooled + transfer_rows, [.15,.10,.107,.048,.095,.09,.084,.065,.068,.10], long=True,
          notes=r'Pooled deviations give AARD in \% with $N$ in parentheses. '
                r'$N$: observations in the data set (number with a defined relative deviation in parentheses if different). Bias: mean signed relative deviation. Published deviations are for the parameter sets I and II of Ermatchkov et al.\ (Section~\ref{sec:s-published}). The B\"ottinger et al.\ rows at 0.5 and 2.5 MPa repeat the same ' + str(nmr_rows) + r' observations, calculated at the two ends of the reported cell-pressure interval. \textsuperscript{a}Mole fraction of added \COtwo. \textsuperscript{b}A relative density deviation is not reported for this set. '
                r'\textsuperscript{c}Single-liquid values at the measured state, for the heats of Zheng et al.\ at the measured final loading. '
                + vapor_note + r', the measured or assigned pressure lies below the calculated bubble pressure, and the model predicts a vapor (Section~\ref{sec:s-phase}).')
    P341 = MEAEVIDENCE
    mea_fit = read(P341 + 'fitted-rows.csv')
    cai_T = [float(r['observed']) for r in mea_fit if r['group'] == 'Cai' and r['quantity'] == 'temperature']
    cai_high = rf"{sum(T >= 370 for T in cai_T)} of the {len(cai_T)} fitted MEA--water bubble temperatures of Cai et al.\ are at or above \SI{{370}}{{\kelvin}}, up to \SI{{{max(cai_T):.2f}}}{{\kelvin}}"
    # DEA: the reported model against the refit with a temperature-dependent water--DEA interaction, on identical observations (#425).
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
            continue
        title, cite = r[0].split(r' \cite')
        role = 'fitted beforehand' if ',' in who and r[2] == 'fitted' else r[2] if r[2] in ('fitted', 'fitted beforehand') else r'development\textsuperscript{a}' if title.startswith(DEVELOPMENT) else None
        if role:
            design.append([r[1], r'\cite' + cite, r[3], r[4], role])
            if role == 'fitted': objective_n[who] = objective_n.get(who, 0) + int(str(r[3]).split()[0])
    # Published models on the pressure sources this work fitted: this work at the temperatures it fitted there, beside every
    # published model that reports a deviation on the source, each over its own observations (owner decision 2026-11-27,
    # "Sets our model fitted"); the Section S7 table holds the sources and temperatures this work did not fit.
    PUB = {'Baygi2015 PC-SAFT': r'PC-SAFT \cite{Baygi2015}', 'Najafloo2018 SAFT-HR': r'SAFT-HR \cite{Najafloo2018}', 'Zhang2011 eNRTL': r'eNRTL \cite{Zhang2011}'}
    ERM = r'\cite{ermatchkovSolubilityCarbonDioxide2006}'
    ZHANG_CHEN = r'eNRTL \cite{zhangThermodynamicModelingCO22011}'  # Zhang and Chen, their Table 14: AARD 6.8 % on the 82 Kuranov total pressures and 17.7 % on the 101 Ermatchkov CO2 partial pressures, 313-413 K and 313-393 K, both in their regression
    kelvin = lambda ts: span([round(float(t)) for t in ts], str)
    source_key = lambda name: re.match(r"[A-Za-z']*", name)[0].replace("'", '')
    yes = lambda role: {'fitted': 'yes', 'not fitted': 'no'}.get(role, role)
    mea_points = collections.defaultdict(list)
    for role, source, T, observed, value in mea_nominal_pressure_points():
        if value is None:
            raise ValueError(f'{source} at {T} K: MEA pressure not calculated; the table gives no count of the rest')
        mea_points[source_key(source)].append((role, T, observed, value))

    def ours(points, mark=''):
        """This work on (role, T, observed, calculated) points: fitted count, N, temperature range and AARD."""
        fitted = sum(role == 'fitted' for role, *_ in points)
        return [r'\quad This work' + mark, f'{fitted} of {len(points)}' if fitted else 'no', len(points), kelvin([p[1] for p in points]),
                f'{100 * fsum(abs(value / observed - 1) for _, _, observed, value in points) / len(points):.2f}']
    published = collections.defaultdict(list)
    for r in read(MEA + 'paper-evidence-341/same-data-comparison/published-deviations.json'):
        if r['property'] == 'pressure':
            published[source_key(r['source'])].append(r)

    def theirs(r, label, fitted=None):
        """A published deviation as reported: its role, N and temperature range (--, not reported) and AARD."""
        T = re.search(r'(?<![\d.])(\d{3}(?:\.\d+)?)(?:\s*[-–]\s*(\d{3}(?:\.\d+)?))?\s*K', r['conditions'])
        return [r'\quad ' + label, fitted or yes(r['data_role']), r['n'] or '--', kelvin([t for t in T.groups() if t]) if T else '--', str(r['deviation_percent'])]

    def mea_group(key, heading, points):
        # Najafloo and Zarei call their ternary results predictions in their methods and fitted in their conclusions (Section S7).
        rows = sorted((theirs(r, PUB[r['model']], 'unclear' if r['model'].startswith('Najafloo') else None) for r in published[key]),
                      key=lambda row: (row[1] != 'yes', float(row[4])))
        return [head(heading, 5), ours(points), *rows]
    absorber = lambda points: [p for p in points if temperature_band(p[1]) == 'absorber']
    main_rows = mea_group('Hilliard', r'Hilliard \cite{Hilliard2008}, MEA $p_{\COtwo}$', mea_points['Hilliard'])
    main_rows += mea_group('Jou', r'Jou et al.\ \cite{Jou1995}, MEA $p_{\COtwo}$', absorber(mea_points['Jou']))
    other_rows = mea_group('Mamun', r"Ma'mun et al.\ \cite{Mamun2005}, MEA $p_{\COtwo}$", mea_points['Mamun'])
    other_rows += mea_group('Xu', r'Xu and Rochelle \cite{Xu2011}, MEA $p_{\COtwo}$', mea_points['Xu'])
    aronu, = published['Aronu']
    # Biget et al., Results: 19 % on the 30 wt% Aronu pressures, which they fitted, with no count or temperatures.
    other_rows += [head(r'Aronu et al.\ \cite{Aronu2011}, MEA $p_{\COtwo}$', 5), ours(mea_points['Aronu']),
                   [r'\quad extended UNIQUAC \cite{bigetDevelopmentThermodynamicIdentification2015a}', 'yes', '--', '--', '19'], theirs(aronu, r'extended UNIQUAC \cite{Aronu2011}\textsuperscript{a}')]
    mpub = read(W_MDEA_PUBLISHED)['comparisons']
    literature = read(ROUND8 + 'literature-populations.json.gz')['quantities']
    k82_adopted, r9_kamps = mdea_pressure_comparisons()
    # Ermatchkov et al., their Table 5: their 101 pressures at 313-393 K and the 28 corrected Kamps pressures at 314-395 K, the counts of this work.
    ERM_T = {'Ermatchkov': '313--393', 'corrected-Kamps': '314--395'}
    for c in mpub:
        sets = [(r'Ermatchkov et al., set ' + q['set'] + ' ' + ERM, yes({'predicted': 'not fitted'}.get(q['data_role'], q['data_role'])),
                 str(literature['published_Kamps_28']['Ermatchkov ' + q['set']] if c['group'] == 'corrected-Kamps' else q['mean_absolute_relative_deviation_percent'])) for q in c['published_parameter_sets']]
        if c['group'] == 'corrected-Kamps':
            label, available, aard, mark = r"P\'erez-Salado Kamps et al.\ in " + ERM + ', MDEA $P$', r9_kamps['full_rows'], r9_kamps['full_AARD_percent'], ''
        else:
            sets.append((ZHANG_CHEN, 'yes', '17.7'))
            score = mstats[c['group']]['R1']['False']
            label, available, aard, mark = r'Ermatchkov et al.\ ' + ERM + r', MDEA $p_{\COtwo}$', score['rows'], score['AARD_percent'], r'\textsuperscript{b}'
        if available != c['measured_rows']:
            raise ValueError(f"{c['group']}: {available} of {c['measured_rows']} observations calculated; the table gives no count of the rest")
        T = [r['T_K'] for r in mrows if r['group'] == c['group'] and r['status'] == 'Available']
        other_rows += [head(label, 5), [r'\quad This work' + mark, 'no', available, kelvin(T), f'{aard:.2f}'],
                       *sorted(([r'\quad ' + model, fitted, c['measured_rows'], ERM_T[c['group']], value] for model, fitted, value in sets), key=lambda row: (row[1] != 'yes', float(row[4])))]
    K422 = 'analyses/mdea_mea_workflow/results/kuranov-published-422/'
    kuranov_rows = mdea_kuranov_rows(read(W_MDEA_PROPERTIES))
    krae = read(K422 + 'raeispour-table-4.json')
    if k82_adopted['available'] != len(kuranov_rows):
        raise ValueError(f"Kuranov: {k82_adopted['available']} of {len(kuranov_rows)} observations calculated; the table gives no count of the rest")
    n = len(kuranov_rows)
    # This work is scored at its fitted conditions: the loaded pressures at the fitted temperatures, not the 413 K or CO2-free ones.
    kuranov_loaded = [r for r in kuranov_rows if r['group'] in ('Kuranov', 'Kuranov-393K')]
    kuranov_source = {r["source_row"]: r for r in read(KURANOV_DATA)}
    # Each model's own paper reports its deviation on the Kuranov pressures: Ermatchkov et al. Table 5 (sets I and II, 82, fitted), Zhang and Chen Table 14,
    # Sadegh et al. Table 7 (77 of them, fitted), Raeispour Shirazi and Lotfollahi Table 4 (no temperatures), Wangler et al. Table 11, Uyan et al. Table 6, Pahlavanzadeh and Baygi Table 6 (not fitted).
    main_rows += [head(r'Kuranov et al.\ \cite{kuranovSolubilitySingleGases1996}, MDEA $P$', 5),
                  [r'\quad This work', f"{sum(r['role'] == 'fitted' for r in kuranov_loaded)} of {len(kuranov_loaded)}", len(kuranov_loaded),
                   kelvin([float(kuranov_source[r["row"]["source_row"]]["temperature_K"]) for r in kuranov_loaded]), f"{stats(kuranov_loaded, predicted='value')['AARD_percent']:.2f}"],
                  [r'\quad Ermatchkov et al., set I ' + ERM, 'yes', n, '313--413', '1.7'], [r'\quad Ermatchkov et al., set II ' + ERM, 'yes', n, '313--413', '3'],
                  [r'\quad ' + ZHANG_CHEN, 'yes', n, '313--413', '6.8'], [r'\quad extended UNIQUAC \cite{sadeghThermodynamicModelingCO22015}', 'yes', 77, '313--413', '8.60'],
                  [r'\quad ePC-SAFT \cite{raeispourshiraziApplicationEPC_SAFTMBEoS2020}', 'yes', krae['rows'], '--', str(krae['AARD_percent'])],
                  [r'\quad ePC-SAFT \cite{Wangler2018}', 'no', n, '313--413', '19.7'], [r'\quad ePC-SAFT \cite{Uyan2015}\textsuperscript{a}', 'no', n, '313--413', '22.9'],
                  [r'\quad PC-SAFT \cite{Pahlavanzadeh2013}', 'no', n, '313--413', '26.42']]
    # Yi et al. (their Table 4: 45 Tong and 51 Kundu pressures, no temperatures) and Hartono et al. (2020) (their Table 13: no counts or temperatures) fitted both sources.
    YI, HARTONO = r'\quad eNRTL \cite{yiOpenAccessThermodynamically2024}', r'\quad eNRTL \cite{hartonoSolubilityCO201M2020}'
    main_rows += [head(r'Tong et al.\ \cite{Tong2012}, AMP $P$', 5),
                  [r'\quad This work', r'\res{amp-reported-tong-fitted-pressure-count-literature} of \res{amp-assessment-tong-pressure-count-note}', r'\res{amp-assessment-tong-pressure-count-literature}',
                   kelvin([r['T_K'] for r in arows if r['group'] in ('tong', 'tong-baseline')]), r'\res{amp-reported-tong-total-pressure-aard-literature}'],
                  [YI, 'yes', '45', '--', '8.0'], [HARTONO, 'yes', '--', '--', '9.3']]
    other_rows += [head(r'Kundu et al.\ \cite{kunduVaporLiquidEquilibriumCO22003}, AMP $p_{\COtwo}$', 5),
                   [r'\quad This work', 'no', r'\res{amp-kundu-comparison-partial-pressure-count}', kelvin([r['T_K'] for r in arows if r['group'] == 'kundu']), r'\res{amp-kundu-pressure-aard-literature}'],
                   [YI, 'yes', '51', '--', '15.4'], [HARTONO, 'yes', '--', '--', '17.3']]
    # Each model's overall value over its MEA pressures; Biget et al. Table 1 (387, fitted); Zhang et al. as tabulated in Baygi and Pahlavanzadeh, Table 5, row Overall.
    by_model = {r['model']: r for rs in published.values() for r in rs if r['source'] in ('all 18 sources', 'Aronu2011', 'water-MEA-CO2', '30 wt% subset')}
    zhang_fitted = sum(r['n'] for rs in published.values() for r in rs if r['model'] == 'Zhang2011 eNRTL' and r['data_role'] == 'fitted')
    main_rows += [head(r'All MEA $p_{\COtwo}$', 5), ours(absorber(p for points in mea_points.values() for p in points)),
                  theirs(by_model['Tellez2013 eCTS'], r'eCTS \cite{tellez-arredondoModelingCO2H2S2013}\textsuperscript{b}'),
                  [r'\quad extended UNIQUAC \cite{bigetDevelopmentThermodynamicIdentification2015a}', 'yes', 387, '--', '20.6'],
                  theirs(by_model['Aronu2011 extended UNIQUAC'], r'extended UNIQUAC \cite{Aronu2011}\textsuperscript{c}'),
                  theirs(by_model['Najafloo2018 SAFT-HR'], PUB['Najafloo2018 SAFT-HR'], 'unclear'), theirs(by_model['Baygi2015 PC-SAFT'], PUB['Baygi2015 PC-SAFT']),
                  theirs(by_model['Akula2023 modified eNRTL'], r'modified eNRTL \cite{Akula2023a}\textsuperscript{d}'),
                  [r'\quad ' + PUB['Zhang2011 eNRTL'] + r'\textsuperscript{e}', f'{zhang_fitted} of 725', 725, '--', '42.29']]
    COLUMNS = ['Source and model', 'Fitted', '$N$', '$T$ (K)', r'{AARD (\%)}']
    SPEC = r'>{\raggedright\arraybackslash}p{0.46\linewidth}lccS[table-format=2.2,detect-weight]'
    main_rows, other_rows = ([[r'\bfseries ' + str(c) for c in row] if str(row[0]).startswith(r'\quad This work') else row for row in rows] for rows in (main_rows, other_rows))
    TERMS = r'$N$, $T$: number and temperature range of the observations of each AARD, as reported (--, not reported); Fitted: the observations of this work in its objective, or whether the published model fitted its own. $p_{\COtwo}$: \COtwo partial pressure; $P$: total pressure. Bold: this work. '
    table('published-models', 'Pressure AARD of this work on the pressure sources it fitted, at its fitted conditions and for MEA up to 353 K, and of published models that report a deviation on each source, each over its own observations.',
          COLUMNS, main_rows, [], spec=SPEC,
          notes=r'AARD of this work follows Eq.~\eqref{eq:aard}; published values are those reported in each source. ' + TERMS + r'Unclear: the source calls these results predictions in its methods and fitted in its conclusions. '
                r'This work: MEA at nominal 30 wt\% and $T\le\SI{353.2}{\kelvin}$, above the fitted 313--333 K, MDEA loaded pressures only; All MEA $p_{\COtwo}$: the overall value of each model. eCTS: electrolyte cubic-two-state equation of state. '
                r'\textsuperscript{a}Recalculated as 34.4\,\% by Wangler et al.\ \cite{Wangler2018}. \textsuperscript{b}15.2--30.0 wt\% MEA; $T$: their stated fitting interval. \textsuperscript{c}15--60 wt\% MEA. '
                rf"\textsuperscript{{d}}30 wt\% MEA at loadings 0.003--0.5. \textsuperscript{{e}}As tabulated by Baygi and Pahlavanzadeh \cite{{Baygi2015}}; the {zhang_fitted} fitted are the observations of Hilliard, Jou et al., Ma'mun et al.\ and Xu and Rochelle.")
    table('supplement-published-models', 'Pressure AARD of this work and of published models on the pressure sources that this work did not fit.',
          COLUMNS, other_rows, [], spec=SPEC,
          notes=r'AARD of this work follows main-text Eq.~(\ref{main-eq:aard}); published values are those reported in each source. ' + TERMS + r'Unclear: see the text. This work: MEA at nominal 30 wt\%; sets I and II: the two parameter sets of Ermatchkov et al. '
                r'\textsuperscript{a}15--60 wt\% MEA. \textsuperscript{b}Used to choose the initial parameters.')
    # Where the AMP splits lie: retained search states, projected onto temperature and loading.
    acomponents = [c['component_id'] for c in adoc['parameters']['components']]
    def astate(s):
        """Temperature, loading and AMP content of one state with a liquid-directed instability, and its confirmed two-liquid calculation, if any."""
        feed = dict(zip(acomponents, s['feed_mol']))
        confirmed = [a for a in s['attempts'] if a['confirmed']]
        return dict(T_K=s['temperature_K'], loading_mol_CO2_per_mol_AMP=feed['carbon-dioxide'] / feed['aminomethylpropanol'], P_Pa=s['pressure_Pa'], outside=s['outside_ranges'],
                    wt=100 * amass['aminomethylpropanol'] / (amass['aminomethylpropanol'] + amass['water'] * feed['water'] / feed['aminomethylpropanol']), split=confirmed[0] if confirmed else None)
    states = [astate(s) for s in aclass['classifications'] if s['liquid_directed'] and confirmed_split(s)]
    fitted_T = [float(r['row']['T_K']) for r in arows if r['group'] == 'loaded-pressure']  # the Hartono pressures that both AMP fits contain
    fig, ax = plt.subplots(figsize=(4.6, 3.5), constrained_layout=True)
    ax.axhspan(min(fitted_T), max(fitted_T), color='0.87', lw=0, label='Temperatures of the fitted Hartono et al. pressures')
    ax.axhline(read('analyses/amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json')['reaction_ranges_K']['AMP-dissociation'][1], color='k', ls=(0, (5, 2)), lw=1.3, zorder=4, label='Upper limit of the measured R5 range')
    mstates = [r for r in arows if r['group'] in ('loaded-pressure', 'hartono-2021-supplemental', 'tong')]
    ax.scatter([amp_loading(r) for r in mstates], [float(r['T_K']) for r in mstates], s=14, marker='+', color='0.45', linewidths=.7, zorder=2, label='Measured total-pressure states (Hartono, Tong)')
    ax.scatter([r['loading_mol_CO2_per_mol_AMP'] for r in states], [r['T_K'] for r in states],
               label='Confirmed liquid–liquid split', s=28, facecolors='none', edgecolors=colors[0])
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
    table('supplement-objective-contributions', 'Contribution of each fitted data set to the objective value of its model.', ['Data set', '$N$', 'Contribution', r'Share (\%)'], crow, [.52, .08, .14, .12],
          notes=r'The objective is that of main-text Eq.~(\ref{main-eq:fit-objective}) with the scales and weights of Tables~\ref{tab:objective-groups} and \ref{tab:transfer-scales}; values of different amines are not comparable. \textsuperscript{a} Fitted beforehand and constant in the reactive objective.')
    weighted_rows = fixed.fits['MDEA']['replay']['rows']
    manifest = read(MOVE + "mdea/reported/fit/manifest.json.gz")
    mdea_pressure_scale = f"{mdea_binary_pressure_scale(manifest):g}"
    kuranov_count = sum(row['group'] == 'Kuranov' for row in weighted_rows)
    pressures = sum(row['unit'] == 'Pa' for row in fixed.fits['DEA']['replay']['rows'])
    scale_rows = [
        ['DEA', r'\COtwo partial pressures', '0.09', f"average over {pressures} pressures"],
        ['', 'Integral absorption heats', r'$0.02\,|y_l^{\mathrm{obs}}|$', f"average over {sum(row['group'] == 'Carson' for row in fixed.fits['DEA']['replay']['rows'])} heats"],
        ['MDEA', 'Loaded total pressures of Kuranov et al.', mdea_pressure_scale, f'$1/{kuranov_count}$'],
    ]
    for label, group, scale in [
            (r'\COtwo-free pressures of Kuranov et al.', 'Kuranov-binary', mdea_pressure_scale),
            ('Mixture and pure-water pressures of Kim et al.', 'Kim', mdea_pressure_scale),
            ('Species ratios of Jakobsen et al.', 'Jakobsen', r'$0.10\,|y_l^{\mathrm{obs}}|$'),
            ('Heat capacities', 'Cp', r'$0.02\,|y_l^{\mathrm{obs}}|$'),
            ('Integral absorption heats, Carson et al.', 'Carson', r'max(3000 J/mol, $0.05\,|y_l^{\mathrm{obs}}|$)'),
            ('Integral absorption heats, Merkley et al.', 'Merkley', r'max(3000 J/mol, $0.05\,|y_l^{\mathrm{obs}}|$)'),
            ('Loaded densities', 'loaded-density', r'$[(0.001\rho_l)^2+(0.01g_l)^2]^{1/2}$'),
            ('Unloaded densities', 'unloaded-density', r'0.5 kg/m$^3$')]:
        n = sum(r['group'] == group for r in weighted_rows)
        scale_rows.append(['', label, scale if n else '---', f'$1/{n}$' if n else 'not fitted'])
    amp_scale_rows = collections.Counter(row['group'] for row in arows if row['role'] == 'fitted')
    scale_rows += [
        ['AMP', 'Loaded total pressures', '0.015',
         f"average over {sum(row['role'] == 'fitted' and row['group'] in amp_loaded for row in arows)} pressures"],
        ['', 'Binary bubble pressures', '0.05', f"average over {amp_scale_rows['binary']} binary observations"],
        ['', 'Vapor AMP mole fractions', r'$\max(10^{-4},0.05\,y_l^{\mathrm{obs}})$', f"average over {amp_scale_rows['binary']} binary observations"],
        ['', 'Carbamate fractions', '0.003', f"average over {amp_scale_rows['nmr']} fractions"],
    ]
    table('supplement-transfer-scales', 'Residual scales and weights of the fitted DEA, MDEA and AMP data sets.',
          ['Amine','Data set',r'Scale $s_l$',r'Weight $w_l$'], scale_rows, [.08,.32,.27,.27],
          notes=r'Pressure residuals are logarithmic, with dimensionless scales. $\rho_l$ is the measured density and $g_l$ the local secant slope against loading. For MDEA the weights average each observation group. The pressure log scale applies to the loaded and binary MDEA pressures.')
    scales_path = LATEX / 'tables/supplement-transfer-scales.tex'
    outputs[scales_path] = outputs[scales_path].replace('tab:supplement-transfer-scales', 'tab:transfer-scales')

    shared_interaction_table(read(W_ABLATION), table, num)

    # MEA model by temperature band (#409): every row recomputed from the retained points.
    BAND_CITE = dict(Hilliard2008='Hilliard2008', Jou1995='Jou1995', Aronu2011='Aronu2011', Idris2014='idrisSpeciationMEACO2Adducts2014', Wagner2013='wagnerSolubilityCarbonDioxide2013', Mamun2005='Mamun2005',
                     Xu2011='Xu2011', Amundsen2009='Amundsen2009', Hartono2014='Hartono2014', Han2012='hanDensityWater12012', Sobrino2016='sobrinoViscosityDensityMeasurements2016', Concepcion2023='concepcionHeatCapacitiesDifferent2023',
                     Weiland1997='weilandHeatCapacityAqueous1997', Vinjarapu2024='HemaBhavya2025', Arcis2011='arcisEnthalpySolutionCarbon2011', Kim2007='Kim2007', Kim2014='Kim2014')
    PROPS = {'CO2 partial pressure': r'\COtwo partial pressure', 'heat of absorption': 'Absorption heat', 'heat capacity': 'Heat capacity', 'density': 'Density'}
    BROLE = {'fitted': 'fitted', 'not fitted': 'not fitted', 'not fitted, 15/45 wt%': r'not fitted, 15 and 45 wt\%', 'not fitted, source-flagged': r'not fitted, flagged\textsuperscript{a}'}
    trange = lambda b: f"{float(b['T_min_K']):.0f}" + ('' if round(float(b['T_min_K'])) == round(float(b['T_max_K'])) else f"--{float(b['T_max_K']):.0f}")
    def temperature_band_points():
        points = []
        points.extend(('CO2 partial pressure', *row) for row in mea_nominal_pressure_points())
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
        current[prop, temperature_band(T), role].append((source, T, observed, value))
    brows = []
    for prop in PROPS:
        for band in ('absorber', 'intermediate', 'stripper'):
            for (p, b, role), points in sorted(current.items()):
                if (p, b) != (prop, band):
                    continue
                values = [100*(calc/obs-1) for _, _, obs, calc in points if calc is not None]
                source_names = sorted({q[0] for q in points})
                brows.append([PROPS[prop], band.capitalize() + ', ' +
                              trange(dict(T_min_K=min(q[1] for q in points), T_max_K=max(q[1] for q in points))) + ' K',
                              BROLE[role], count(len(points), len(values)),
                              num(math.fsum(map(abs, values))/len(values), 2), num(math.fsum(values)/len(values), 2),
                              r'\cite{' + ','.join(BAND_CITE[q] for q in source_names) + '}'])
    kim_hot = [row for row in compare_mea['kim_2007'] if float(row['T_K']) == 393.15]
    kim_inconsistent = sum(row['source_inconsistent'] == 'True' for row in kim_hot)
    kim_first_additions = sum(row['first_120'] == 'True' for row in kim_hot)
    kim_flagged = sum('True' in (row['source_inconsistent'], row['first_120']) for row in kim_hot)
    table('supplement-temperature-bands', 'Deviations of the MEA model by temperature band.', ['Property', 'Band', 'Role', '$N$', 'AARD (\\%)', 'MSRD (\\%)', 'Sources'], brows, [.17, .17, .16, .045, .08, .08, .13],
          notes=r'Absorber: $T\le\SI{353.2}{\kelvin}$; stripper: $T\ge\SI{370}{\kelvin}$; intermediate: between the two. Fitted observations are in the objective of the MEA model; no loaded-solution observation at or above \SI{370}{\kelvin} is fitted; ' + cai_high + r'. AARD follows main-text Eq.~\eqref{main-eq:aard}; MSRD is the mean of $100\,(y^{\mathrm{calc}}-y^{\mathrm{obs}})/y^{\mathrm{obs}}$, negative where the calculated value is low. Pressures are at nominal 30 wt\% MEA unless stated. Absorption heats are heat releases per mole of \COtwo as each source defines them; the heats of Kim and Svendsen, Kim et al.\ and Vinjarapu et al.\ are calculated at \SI{1.734}{\mega\pascal}, the pressure reported by Vinjarapu et al. '
                rf'\textsuperscript{{a}}{NUMBER_WORDS[kim_flagged].capitalize()} intervals of Kim and Svendsen at \SI{{393.15}}{{\kelvin}}, '
                f'{NUMBER_WORDS[kim_inconsistent]} inconsistent with their integrals and the first {NUMBER_WORDS[kim_first_additions]} additions from zero loading, reported separately.')

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


    # A local column-header row names the columns beneath it where they differ from the table head.


    # Parameter quantity by the last identity part, in display order; units as block headings show them.


    # rows: (identity, unit, cells); blocks ordered as QUANTITY, source order kept within a block.


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
        ['', *(symbol[s] for s in species[1:])]
        pair_specs = [('carbon-dioxide','water','CO2--water fit'),('monoethanolamine','water','Joint fit'),
                      ('water','protonated-monoethanolamine','Joint fit'),('water','carbamate-anion','Joint fit'),
                      ('water','bicarbonate-anion','Sodium-salt fit'),('water','carbonate-anion','Sodium-salt fit'),
                      ('protonated-monoethanolamine','bicarbonate-anion','Joint fit'),('protonated-monoethanolamine','carbamate-anion','Joint fit'),
                      *[('water', ion, r'\cite{Held2014}') for ion in ('hydronium-cation', 'hydroxide-anion')]]
        def pair_se(s, u, quantity=''):  # conditional standard error of a fitted interaction; none for a fixed value or one on its bound
            return num(next((coords[i+quantity]['conditional_SE'] for i in (f'pair/{s}/{u}/k_ij', f'pair/{u}/{s}/k_ij') if i+quantity in coords), None), 3)
        active_pairs = {unordered(key): side for key, side in study.fits['MEA']['diagnostics']['active_bounds'].items()}
        def pair_rows(decimals=None, errors=False):
            def ref(s, u, source):
                if not errors or source.startswith(r'\cite'):
                    return source
                if source == 'CO2--water fit':
                    return source + note('b')
                bound = active_pairs.get(unordered(f'pair/{s}/{u}/k_ij'))
                return source + (note({'upper': 'c', 'lower': 'd'}[bound]) if bound else '')
            return [[symbol[s]+'--'+symbol[u]+mark*(errors and {s,u} <= set(shared_species)),pair(s,u,decimals=decimals),*[pair_se(s,u)]*errors,(pair(s,u,'/temperature_slope',decimals) + r'~K$^{-1}$' if source == 'Sodium-salt fit' else
                    pair(s,u,'/reciprocal_temperature_slope',decimals) + '~K' if pair(s,u,'/reciprocal_temperature_slope',decimals) != '--' else '--'),*[pair_se(s,u,'/reciprocal_temperature_slope')]*errors,ref(s,u,source)] for s,u,source in pair_specs]
        table('interaction_matrix.tex', r"Nonzero or fitted binary interaction parameters of the MEA model with their conditional standard errors (s.e.), $k_{ij}(T)=k_{ij}(313.15\,\mathrm{K})+b_{ij}(1/T-1/313.15\,\mathrm{K})$. || Bold: fitted in this work. A standard error is given for the jointly fitted values that are not on a bound; an absent slope is zero. The two sodium-salt slopes are linear in $T-313.15\,\mathrm{K}$. $^{\mathrm{a}}$Shared interaction, held fixed for DEA, MDEA and AMP. $^{\mathrm{b}}$Fitted beforehand to \ce{CO2}--water pressures (Section~\ref{sec:parameters}). $^{\mathrm{c}}$On its upper bound. $^{\mathrm{d}}$On its lower bound. All unlisted unlike-charge or neutral pairs have $k_{ij}=0$; same-sign ion dispersion is excluded. Table~\ref{supp-tab:supplement-interaction-matrix} gives unrounded values.",
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
        table('reaction_equilibrium_constants.tex', r"Aqueous reactions of an amine A, with the source and source temperature range of each equilibrium constant. || $^{\mathrm{a}}$Range stated for the correlation in its source. $^{\mathrm{b}}$Range of estimates made with a solubility model, not of measurements. $^{\mathrm{c}}$Starting correlation; its constant term and an enthalpy increment are then fitted (Tables~\ref{tab:dea-fitted} and~\ref{tab:amp-fitted}). $^{\mathrm{d}}$Correlation of Silkenb\"aumer et al., which represents three estimates that Xu et al.\ \cite{xuRepresentationEquilibriumSolubility1992} obtained with a solubility model. Table~\ref{supp-tab:supplement-reaction-coefficients} gives the coefficients of R1--R3 and of the MEA correlations on the molality basis, and Table~\ref{supp-tab:supplement-transfer-parameters} those of R4 and R5 for DEA, MDEA and AMP.", ['Reaction', 'Name', 'Stoichiometry'], reaction_rows, ['l','l','l'])
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
        previous_groups = {}
        for row in read(E/'paper-evidence/fitted-rows.csv'):
            previous_groups.setdefault(rowkey(row['group'], row['quantity']), []).append(row)
        # The #341 comparison used these retained Polley–Hedengren predictions.
        published = read(BUNDLE/'results/same-data-comparison/part1/published/selected-assessment/state-targets.csv')
        published_pressures = [r for r in published if r['kind'] in ('canonical', 'wagner', 'transfer')
                               and r['status'] == 'Available']
        published_by_target = {r['target']: r for r in published_pressures}
        if len(published_by_target) != len(published_pressures):
            raise ValueError('Duplicate pressure targets in the Polley–Hedengren assessment')

        def paired_pressure_scores(rows):
            prior = [published_by_target[r['target']] for r in rows]
            if len({r['target'] for r in rows}) != len(rows) or any(
                (float(r['observed']), float(r['temperature_K'])) != (float(p['observed']), float(p['temperature_K']))
                for r, p in zip(rows, prior, strict=True)
            ):
                raise ValueError('MEA pressure observations differ between the paired assessments')
            return stats(rows)['AARD_percent'], stats(prior)['AARD_percent']

        rows_for[MEA_TRACKING_FITTED_PRESSURES] = [r for r in canonical if r['target'] in fitted_ids]
        for r in cp:
            name = r['group']
            if 'pressures' in name:
                rows = rows_for[name]
                _, prior_aard = paired_pressure_scores(rows)
                if [len(rows)] * 2 != r['n'] or f"{prior_aard:.2f}" != f"{r['deviations'][0]:.2f}":
                    raise ValueError(f'{name}: paired rows do not reproduce the reported earlier-model score')
            elif name.startswith('Kim heat'):
                metric = kim_at(name.split()[2])
                r['deviations'][1] = metric['RMSE']
            elif name in rows_for:
                rows = rows_for[name]
                r['deviations'][1] = stats(rows)['AARD_percent' if r['metric'].startswith('AARD') else 'RMSE']
        heat_capacity_labels = {'Weiland1997 comparison': 'Weiland et al.\\ heat capacities \\cite{weilandHeatCapacityAqueous1997}', 'Concepcion2023 comparison': "Concepci\\'on et al.\\ heat capacities \\cite{concepcionHeatCapacitiesDifferent2023}"}
        same_names = {'Species fractions': 'All species fractions',
                      'broad Cp': 'Hilliard heat capacities at 313.15--393.15 K'}
        # The published fitting account of the earlier model does not give the role of each pressure and species observation.
        earlier_role = lambda role: 'not stated' if 'see role note' in role else role.split(';')[0].replace('formulation ','').replace('comparison', r'com\-parison')
        hilliard = read('analyses/round_5/results/records/Hilliard-Cp.json')['current_broad_roles']
        # Fitted quantities that the earlier model was scored on with identical observations, and the prior use of the comparison sets.
        same = {('common149','partial_pressure'): MEA_TRACKING_FITTED_PRESSURES, ('Jakobsen','amount_ratio'): 'Species ratios', ('common149','addition_enthalpy'): 'Vinjarapu2024 heats', ('Cp','equilibrium_isobaric_heat_capacity'): f"{NUMBER_WORDS[hilliard['fitted']].capitalize()} Hilliard heat capacities"}
        prior = {'Arcis2011': 'a', 'Kim heat 313': 'b', 'Kim heat 353': 'b', 'Amundsen2009': 'c', 'Hartono2014': 'c', 'Han2012': 'c'}
        earlier = {r['group']: r for r in cp}
        # #434: the retained role text of the Hilliard heat-capacity group counts two fitted observations; the fit has four of the 51.
        role_of = lambda r: f"{hilliard['fitted']} fitted / {hilliard['outside']} not fitted" if r['group'] == 'broad Cp' else r['roles'][1].split(';')[0]
        # Deviations show two decimals; an RMSE of the main-text table keeps four significant digits, as in its fitted block.
        both = lambda r, value, main: [f'{float(value):.2f}', '--'] if r['metric'].startswith('AARD') else ['--', num(value) if main else f'{float(value):.2f}']
        data = [block(8, 'Fitted', True)]
        for key, rows in groups.items():
            r = earlier.get(same.get(key))
            data.append([rowlabel(key), len(rows), 'fitted', f"{stats(rows)['AARD_percent']:.2f}", '--' if 'pressure' in key[1] else num(stats(rows)['RMSE']/(1000 if key[1]=='addition_enthalpy' else 1)), *([earlier_role(r['roles'][0]), *both(r, r['deviations'][0], True)] if r else ['--']*3)])
        data.append(block(8, 'Not fitted, or fitted in part'))
        nominal = rows_for[MEA_TRACKING_ADDITIONAL_PRESSURES] + rows_for['Wagner pressures']
        within_ids = {row['target'] for role, row, _ in mea_nominal_pressure_rows()
                      if role == 'not fitted' and temperature_band(float(row['temperature_K'])) == 'absorber'}
        within = [r for r in nominal if r['target'] in within_ids]
        if {r['target'] for r in within} != within_ids:
            raise ValueError('The MEA comparison must include the full held-out absorber pressure pool')
        current_aard, prior_aard = paired_pressure_scores(within)
        pressure_cite = PRESSURE_CITE | {'Wagner2013': 'wagnerSolubilityCarbonDioxide2013'}

        def pressure_label(label, rows):
            observed_sources = {r['source'] for r in rows}
            citations = ','.join(key for source, key in pressure_cite.items() if source in observed_sources)
            return label + r' \cite{' + citations + '}'

        data.append([pressure_label(r'\ce{CO2} partial pressure', within), len(within),
                     'not fitted', f'{current_aard:.2f}', '--', 'not stated', f'{prior_aard:.2f}', '--'])
        absorber_limit = rf'\SI{{{MEA_ABSORBER_MAX_K:g}}}{{\kelvin}}'
        outside = []
        for group, name in (
            (MEA_TRACKING_ADDITIONAL_PRESSURES, f'Pressures from the six-source set, $T>{absorber_limit}$'),
            ('Wagner pressures', f'Wagner pressures, $T>{absorber_limit}$'),
            ('Aronu 15 wt% pressures', 'Aronu 15 wt% pressures'),
            ('Aronu 45 wt% pressures', 'Aronu 45 wt% pressures'),
        ):
            rows = [r for r in rows_for[group] if r['target'] not in within_ids]
            current_aard, prior_aard = paired_pressure_scores(rows)
            outside.append([pressure_label(name, rows), len(rows), f'{current_aard:.2f}',
                            earlier_role(earlier[group]['roles'][0]), f'{prior_aard:.2f}'])
        aside = []
        for r in cp:
            if r['group'] in same.values() or 'pressures' in r['group']: continue
            unit = r['metric'].partition('(')[2].rstrip(')')
            main = r['group'] == 'Species fractions'
            (data if main else aside).append([cited(r['group'], heat_capacity_labels.get(r['group'], same_names.get(r['group'], r['group']))) + ('' if r['metric'].startswith('AARD') else f' ({unit})'), r['n'][0],
                         role_of(r) + next((r'$^{\mathrm{' + m + '}}$' for k, m in prior.items() if r['group'].startswith(k)), ''), *both(r, r['deviations'][1], main), earlier_role(r['roles'][0]), *both(r, r['deviations'][0], main)])
        kiepe = groups[('Kiepe', 'pressure')]
        kiepe_cost = math.fsum(float(row["cost"]) for row in kiepe)
        table('mea_data.tex', (r"Data for MEA with their roles in the joint fit and deviations of this work and of Polley and Hedengren CITE14 on identical observations. Held-out \ce{CO2} partial pressures are at nominal 30 wt% MEA and $T\le" + absorber_limit + r"$. || --: not calculated; pressure deviations are given as AARD. For pressures and species fractions marked ``not stated'', Ref.~CITE14 does not give the role of every observation. The species ratios informed the ion parameters of Ref.~CITE14 but were outside its published objective. The \ce{CO2}--water pressures of Kiepe et al.\ contribute " + f"{kiepe_cost:.4f}" + r" to $C$ (Table~\ref{supp-tab:objective-groups}); the interaction was fitted beforehand and held fixed. Tables~\ref{supp-tab:supplement-mea-extrapolation} and~\ref{supp-tab:supplement-mea-comparison} give the pressure extrapolations and the other property comparisons, respectively.").replace('CITE14', CITE14),
              ['Quantity (unit)', '$N$', 'Role', r'\makecell[rb]{AARD\\(\%)}', 'RMSE', 'Role in '+CITE14, r'\makecell[rb]{AARD (\%)\\'+CITE14+'}', r'\makecell[rb]{RMSE\\'+CITE14+'}'], data, [.24,'r',.12,'r','r',.08,'r','r'])
        table('supplement_mea_extrapolation.tex',
              r"Deviations of the MEA model and of Polley and Hedengren " + CITE14
              + r" on identical \ce{CO2} partial pressures outside the conditions fitted in this work. || The six-source and Wagner rows are at nominal 30 wt\% MEA. All rows are held out in this work. For the six-source data, "
              + CITE14 + r" does not give the role of every observation.",
              ['Data set', '$N$', r'\makecell[rb]{AARD\\(\%)}', 'Role in ' + CITE14,
               r'\makecell[rb]{AARD (\%)\\' + CITE14 + '}'],
              outside, [.46, 'r', 'r', .14, 'r'])
        prior_density_rmse = {
            row['group']: row['deviations'][0] for row in cp if row['group'] in ('Han2012 all', 'Hartono2014 loaded')
        }
        (prior_heat_count,) = set(kim_prior_interval_counts().values())
        prior_rmse_range = '--'.join(f'{value:.0f}' for value in sorted(prior_density_rmse.values()))
        table('supplement_mea_comparison.tex', (r"Data for MEA that are not fitted, or fitted in part, and are not pressures, with the deviations of the MEA model and the model of Polley and Hedengren CITE14 on identical observations. || The columns are those of main-text Table~\ref{main-tab:mea-data}. $^{\mathrm{a}}$Also used to select the parameters; $^{\mathrm{b}}$" + NUMBER_WORDS[prior_heat_count] + r" of these intervals are in the objective of the model of Ref.~CITE14; no interval of Kim and Svendsen is in the objective of the MEA model; $^{\mathrm{c}}$the comparison between density sources informed the choice of fitted density observations. The densities of Ref.~CITE14 are those of its equation of state; for column hydraulics Ref.~CITE14 uses a separate empirical density correlation (its Section~2.2 and Appendix~A.2), so its loaded-density RMSEs of " + prior_rmse_range + r" kg/m$^3$ describe the liquid volume of that equation of state under load, not that hydraulic density. These sets overlap with each other and with the fitted observations, so their counts are not additive.").replace('CITE14', CITE14),
              ['Quantity (unit)', '$N$', 'Role', r'\makecell[rb]{AARD\\(\%)}', 'RMSE', 'Role in '+CITE14, r'\makecell[rb]{AARD (\%)\\'+CITE14+'}', r'\makecell[rb]{RMSE\\'+CITE14+'}'], aside, [.24,'r',.12,'r','r',.08,'r','r'])
        interior = [label(k) for k in uncertainty['free_coordinates']]
        correlation = uncertainty['conditional_correlation']
        table('supplement_correlations.tex',
              f"Conditional correlations of the {NUMBER_WORDS[len(interior)]} fitted parameters that are not at a bound.",
              ['Parameter']+[str(i+1) for i in range(len(interior))],
              [[f'{i+1}. {interior[i]}']+[num(v,3) if j<=i else '' for j,v in enumerate(row)] for i,row in enumerate(correlation)],
              [.26]+['r']*len(interior))
        weights = read(E/'objective-groups.csv')  # unchanged scales and weights
        weight_groups = {}
        for r in weights: weight_groups.setdefault(rowkey(r['group'],r['quantity']),[]).append(r)
        table('objective_groups.tex', r"Assigned objective scales and weights. || Scales are in the unit of the quantity, and unity for the logarithmic pressure residuals. The text gives the origin of each scale and weight. The Kiepe pressures were fitted beforehand and contribute a constant to the reactive objective.", ['Quantity','$N$','Scale range','Weight range','Contribution to $C$'], [[rowlabel(key,False),sum(int(r['n']) for r in part),span(float(r['scale']) for r in part),span(float(r['weight']) for r in part),num(sum(float(r['cost']) for r in groups[key]),6)] for key,part in weight_groups.items()], [.42,'r','l','l','r'])
        check_record = study.endpoint_record('display-replays/bubble-checks.json.gz', 'MEA')
        checks = check_record['rows']
        # Each bubble pressure was solved from two initial pressures; the digits shown must agree.
        state = [('$T$ (K)', lambda r, k: num(r['T_K'],7)), ('Bubble pressure (Pa)', lambda r, k: num(r['answers'][k]['bubble_pressure_Pa'],10)), (r'Liquid density (kg/m$^3$)', lambda r, k: num(r['answers'][k]['density_kg_m3'],10))]
        contribution_names = dict(association='Association', born='Born', hard_chain='Hard chain', dispersion='Dispersion', debye_huckel=r'Debye--H\"uckel', residual_helmholtz='Total residual')
        table('supplement_check_values.tex', "Reference values of the MEA model at "
              + NUMBER_WORDS[len(checks)] + r" bubble states, for checking an implementation: temperature, bubble pressure, liquid mass density, reduced residual Helmholtz contributions $A_i/(nRT)$ and true liquid species fractions. || Inputs: $x_{\ce{CO2}}=3.6\times10^{-4}$ in water; $x_{\ce{MEA}}=0.9264$ in MEA--water; 30 wt\% MEA at loading 0.3 mol/mol. Each bubble pressure was solved from " + NUMBER_WORDS[len(checks[0]["answers"])] + r" initial pressures, which agree to the digits shown. Zero terms are omitted. These values check the numerical calculation; they are not measurements.", ['Quantity',r'\ce{CO2}--water','MEA--water','Loaded MEA'], [[name,*[get(r,0) for r in checks]] for name,get in state]+[[('$x_{'+symbol[key[2:]]+'}$') if key.startswith('x_') else contribution_names[key],*[num(r['answers'][0][key],10) for r in checks]] for key in checks[0]['answers'][0] if key not in ('bubble_pressure_Pa','density_kg_m3','molar_density_mol_m3') and any(r['answers'][0][key] for r in checks)], ['l','r','r','r'])
        shared = read(E/'shared-coefficients.csv')
        # S2 and S3 already list species fields and the explicitly retained pairs.
        covered_pairs = {tuple(sorted((x, y))) for x, y, _ in pair_specs}
        missing = [r for r in shared if (r['identity'].startswith('component/') and r['identity'].rsplit('/', 1)[-1] in ('packing_diameter', 'debye_huckel_diameter')) or (r['identity'].startswith('pair/') and tuple(sorted(r['identity'].split('/')[1:3])) not in covered_pairs)]
        table('supplement_shared_remaining.tex', r"Shared parameters not listed in Tables~\ref{tab:supplement-species-parameters} and \ref{tab:supplement-interaction-matrix}, at full precision. || Together with the reaction coefficients in Table~\ref{tab:supplement-reaction-coefficients}, those tables give the unrounded values of the shared parameters marked in main-text Tables~\ref{main-tab:species-parameters} and \ref{main-tab:interaction-matrix}.", ['Parameter','Value','Unit','Source'], [[label(r['identity']), f"{float(r['value']):.15g}" if r['identity'].endswith('/packing_diameter') else full_precision(r['value']), r['unit'],
                                              r'$0.88\sigma$' if r['identity'].endswith('/packing_diameter') else r'Equal to $\sigma$' if r['identity'].endswith('/debye_huckel_diameter') else 'Set in this work'] for r in missing], [.42,'r','l','l'])
        table('pressure_sources.tex', r"Pressure deviations of the MEA model by experimental source at nominal 30 wt\% MEA. || Source subsets contain both fitted observations and observations that are not fitted.", ['Source','Observations','AARD (%)'], [[cited('', SOURCE_NAMES[s]) + r' \cite{' + PRESSURE_CITE[s] + '}',len(part),format(stats(part)['AARD_percent'], '.1f')] for s in sorted({r['source'] for r in canonical}) for part in [[r for r in canonical if r['source']==s]]], ['l','r','r'])
    reference_states()
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
        families = read(MOVE + 'mea/reported/properties/summary.json.gz')['curves']
        def curve(family):
            return [dict(r, status='available', value=r['value'] if r['status'] == 'available' else math.nan,
                         below_bubble_pressure=str(r.get('below_bubble_pressure', False))) for r in families[family]]
        off_window = {r['identity']: r for r in study.load('MEA/off-window.json.gz')['rows']}

        meta={r['observation_id']:r for r in read(ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')}
        canonical = read(evidence/'canonical-pressure.csv'); curves = curve('pressure')
        fitted = {r['id'] for r in read(evidence/'fitted-rows.csv') if r['quantity'] == 'PartialPressure'}
        fig,ax=plt.subplots(figsize=(6.8,4.4))
        pressure_temperatures = sorted({float(row['temperature_K']) for row in curves})
        for T in pressure_temperatures:
            color, style = temperature_style(T)
            part=[r for r in curves if float(r['temperature_K'])==T and r['status']=='available']; part.sort(key=lambda r: float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in part],[float(r['value'])/1000 for r in part],color=color,linestyle=style,label=f'{T:g} K')
            part=[r for r in canonical if abs(float(r['temperature_K'])-T)<2]; ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in part],[float(r['observed'])/1000 for r in part],s=SIZE,marker=temperature_marker(T),facecolors=[color if r['target'] in fitted else 'none' for r in part],edgecolors=color)
        ax.set(xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel='CO$_2$ partial pressure (kPa)',yscale='log'); ax.legend(handles=temperature_legend(pressure_temperatures),ncol=2); save(fig,'pressure')
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
        species_temperatures = sorted({float(row['temperature_K']) for row in rows})
        for ax,name,letter in zip(axes.flat,names,'abcd'):
            for T in species_temperatures:
                color, temperature_dash = temperature_style(T)
                part=[r for r in rows if r['quantity']==name and float(r['temperature_K'])==T and r['status']=='available']
                for below,style in [('False','-'),('True',':')]:
                    sub=sorted([r for r in part if r['below_bubble_pressure']==below],key=lambda r:float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in sub],[float(r['value']) for r in sub],color=color,linestyle=temperature_dash if below=='False' else ':',label=f'{T:g} K' if below=='False' else None)
                sub=[r for r in obs if r['species']==('HCO3-' if name.startswith('HCO3') else name) and float(r['temperature_K'])==T]; ax.scatter([float(membership[r['target']]) for r in sub],[float(r['observed']) for r in sub],s=SIZE,marker=temperature_marker(T),facecolors='none',edgecolors=color)
            ax.set_title(f'({letter}) ' + {'MEA + MEAH+':r'MEA + MEAH$^+$','MEACOO-':r'MEACOO$^-$','MEAH+':r'MEAH$^+$','HCO3- + CO3^2-':r'HCO$_3^-$ + CO$_3^{2-}$'}[name], loc='left'); ax.set(xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel='Liquid mole fraction')
            ax.set_xlim(-.03,.83)
            if name.startswith('HCO3'): ax.set(yscale='log')
        axes[0,0].legend(handles=temperature_legend(species_temperatures),fontsize=9); save(fig,'speciation')
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
                conditions = sorted({(float(row['T_K']), float(row['P_Pa'])) for row in obs})
                legend = []
                for T, P in conditions:
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


GRAPHICAL_ABSTRACT = LATEX / "submission/graphical_abstract"


def graphical_abstract(outputs):
    """Elsevier graphical abstract: the shared base over the lowest- and highest-temperature pressure isotherm of each amine, from the records of the manuscript pressure figures."""
    fixed = FixedReference(read)
    meta = {r['observation_id']: r for r in read(ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')}
    mea_measured = read(BUNDLE/'results/salt-anchored-435/MEA/evidence/F4/canonical-pressure.csv')
    mea_curves = read(MOVE + 'mea/reported/properties/summary.json.gz')['curves']['pressure']
    dea = fixed.endpoint_record('DEA/property-comparisons/selected.json.gz', 'DEA')
    mdea = fixed.endpoint_record('MDEA/properties.json.gz', 'MDEA')['rows']
    mdea_curves = fixed.load('MDEA/properties.json.gz')['curves']
    amp = fixed.endpoint_record('AMP_free/properties.json.gz', 'AMP_free')
    usable = lambda r: r['status'] == 'Available' and r['requested_tolerance_met']
    kuranov = lambda r: r['group'] == 'Kuranov' and r['row']['m_MDEA_mol_per_kg_H2O'] == '3.9707'
    # Per amine: (temperature, measured (loading, kPa), retained model curve (loading, kPa)) of each isotherm.
    panels = {
        'MEA': [(T, [(float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']), float(r['observed'])/1000)
                  for r in mea_measured if abs(float(r['temperature_K']) - T) < 2],
                 [(r['analytical_loading'], r['value']/1000) for r in mea_curves
                  if r['temperature_K'] == T and r['status'] == 'available']) for T in (313.15, 393.15)],
        'DEA': [(T, [(float(r['row']['alpha_mol_CO2_per_mol_DEA']), r['observed']/1000) for r in dea['rows'] if r['group'] == g and r['T_K'] == T],
                 [(r['loading'], r['value']/1000) for r in dea['curves'] if r['group'] == g and r['T_K'] == T and usable(r)])
                for g in ('Lawson', 'Lawson-394K') for T in [min(r['T_K'] for r in dea['curves'] if r['group'] == g)]],
        'MDEA': [(T, [(float(r['row']['m_CO2_mol_per_kg_H2O'])/float(r['row']['m_MDEA_mol_per_kg_H2O']), r['observed']/1000)
                   for r in mdea if kuranov(r) and r['row']['source_series'].rsplit(' ', 2)[-2] == f'{T:.0f}'],
                  [(r['loading'], r['value']/1000) for r in mdea_curves if kuranov(r) and r['T_K'] == T and usable(r)])
                 for T in (313.15, 393.15)],
        'AMP': [(T, [(float(r['row']['alpha_mol_CO2_per_mol_AMP']), r['observed']/1000) for r in amp['rows'] if r['group'] == g and r['T_K'] == T],
                 [(r['loading'], r['value']/1000) for r in amp['curves'] if r['group'] == g and r['T_K'] == T and usable(r)])
                for g, T in (('loaded-pressure', 313.0), ('hartono-2021-supplemental', 393.0))],
    }
    for amine, isotherms in panels.items():
        if not all(measured and curve for _, measured, curve in isotherms):
            raise ValueError(f"Empty graphical-abstract isotherm for {amine}")
    # DejaVu Sans ships with Matplotlib, so the rendered bytes do not depend on installed system fonts.
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'mathtext.fontset': 'dejavusans', 'pdf.fonttype': 42, 'font.size': 7.5,
                         'axes.labelsize': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7, 'axes.linewidth': .6,
                         'xtick.major.width': .6, 'ytick.major.width': .6, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5})
    styles = (('#0072B2', 'o', '-'), ('#D55E00', '^', (0, (4, 1.5))))
    fig = plt.figure(figsize=(1328/254, 531/254))  # Elsevier minimum 1328 x 531 px, drawn at the 13 x 5 cm reading size
    left, width, pair_gap, gap, bottom, height = .112, .188, .105, .012, .3, .445
    xs = [left, left + width + gap, left + 2*width + gap + pair_gap, left + 3*width + 2*gap + pair_gap]
    axes = [fig.add_axes((x, bottom, width, height)) for x in xs]
    for ax, (amine, isotherms) in zip(axes, panels.items(), strict=True):
        for (T, measured, curve), (color, marker, dash), y in zip(isotherms, styles, (.07, .2), strict=True):
            ax.plot(*zip(*sorted(curve)), color=color, ls=dash, lw=1.1)
            ax.plot(*zip(*measured), ls='none', marker=marker, ms=2.8, mfc='none', mec=color, mew=.7)
            ax.text(.95, y, f'{T:.0f} K', color=color, transform=ax.transAxes, ha='right', va='bottom', fontsize=7)
        ax.set_yscale('log'); ax.minorticks_off()
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(3))
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        ax.set_title(amine, fontsize=9, fontweight='bold', pad=2.5)
    for ax, partner, low, ticks, label in ((axes[0], axes[1], 1e-3, (1e-2, 1, 1e2, 1e4), 'CO$_2$ partial\npressure (kPa)'),
                                           (axes[2], axes[3], .1, (1, 1e2, 1e4), 'Total\npressure (kPa)')):
        for a in (ax, partner):
            a.set_ylim(low, 1e4); a.set_yticks(ticks)
        partner.tick_params(labelleft=False)
        ax.set_ylabel(label, labelpad=2, linespacing=1.1)
    fig.text(.45, .165, 'Loading (mol CO$_2$/mol amine)', ha='center', va='center')
    fig.legend(handles=[Line2D([], [], color='0.25', ls='none', marker='o', ms=2.8, mfc='none', mew=.7, label='Measured'),
                        Line2D([], [], color='0.25', lw=1.1, label='ePC-SAFT')],
               loc='center right', bbox_to_anchor=(.995, .165), ncols=2, frameon=False, handlelength=1.8, columnspacing=1, fontsize=7.5)
    for y0, h, y, text in ((.88, .105, .9325, 'Shared base without amine data: water, CO$_2$, inorganic ions and reactions'),
                           (.012, .095, .0595, 'Reactive stability searches find no confirmed second liquid in the four models')):
        fig.patches.append(matplotlib.patches.FancyBboxPatch((.008, y0), .984, h, boxstyle='round,pad=0,rounding_size=.012',
                                                             transform=fig.transFigure, fc='0.93', ec='0.35', lw=.6))
        fig.text(.5, y, text, ha='center', va='center', fontsize=8)
    for x in xs:
        fig.patches.append(matplotlib.patches.FancyArrowPatch((x + width/2, .88), (x + width/2, .815), transform=fig.transFigure,
                                                              arrowstyle=matplotlib.patches.ArrowStyle('-|>', head_length=2.5, head_width=1.5), color='0.35', lw=.8))
    for suffix, options in (('.png', {'dpi': 508}), ('.pdf', {'metadata': {'CreationDate': None, 'ModDate': None}})):
        with BytesIO() as buffer:
            fig.savefig(buffer, format=suffix[1:], facecolor='white', **options)
            outputs[GRAPHICAL_ABSTRACT.with_suffix(suffix)] = buffer.getvalue()
    plt.close(fig)


def render_all():
    outputs = {}
    with matplotlib.rc_context():
        transfer_displays(outputs)
    mea_tables(outputs)
    with matplotlib.rc_context():
        mea_figures(outputs)
    with matplotlib.rc_context():
        graphical_abstract(outputs)
    return outputs



def manuscript_sources():
    return sorted([LATEX / "main.tex", LATEX / "supplement.tex", *LATEX.glob("sections/*.tex")])


RES = re.compile(r"\\res\{([a-z0-9-]+)\}")
NUMERAL = re.compile(r"(?<![\w.])(?:(?<!-)[+-])?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?(?!\w|\.\d)")
SCIENTIFIC = re.compile(
    r"(?<![\w.])(?:(?P<mantissa>[+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*\\times\s*)?"
    r"(?P<base>10)\^\{(?P<exponent>[+-]?\d+)\}"
)
NUMBER_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
                "fifteen sixteen seventeen eighteen nineteen").split()
NUMBER_WORD = re.compile(
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|"
    r"fifty|sixty|seventy|eighty|ninety|hundred|thousand|million)\b", re.I
)
COMMENT = re.compile(r"(?<!\\)%[^\n]*")
REFERENCE = re.compile(
    r"\\(?:[Cc]ref|[Cc]pageref|pageref|eqref|ref|label|cite\w*|input|includegraphics|begin|end|"
    r"bibliography|bibliographystyle|multicolumn|url|nolinkurl|res|orcidlink|orcid|author|affil|affiliation|email|ead|cormark|thanks|"
    r"date|runningauthor|correspondingauthor|hypersetup|usepackage|documentclass|newcolumntype|newcommand|renewcommand|"
    r"providecommand|def|gdef|edef|xdef|setlength|addtolength|setcounter)\b\*?"
)
GROUPS = re.compile(r"[\s{}\[\]\\]")
LAYOUT = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:pt|pc|in|cm|mm|em|ex|bp|sp|dd|cc)\b"
    r"|\b\d+(?:\.\d+)?\\(?:textwidth|linewidth|columnwidth|textheight|baselineskip)\b"
)
INDEX = re.compile(r"(?<=[A-Za-z0-9}$\]{])[_^](?:\{[^}]*\}|[0-9]+)")


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


def prose_exponent(value, precision):
    mantissa, exponent = format(value, precision).split("e")
    return f"{mantissa}e{int(exponent)}"


def prose_scientific(value, precision):
    if precision is None:
        return rf"10^{{{round(math.log10(value))}}}"
    mantissa, exponent = format(value, precision).split("e")
    return rf"{mantissa}\times10^{{{int(exponent)}}}"


def dea_lal_unloaded_mass_fraction(manifest, components):
    row = next(row for row in manifest["rows"]["fitted"] if row["group"] == "Lal")
    feed = row["states"]["problem"]["feed"]["values"]
    masses = {
        row["component_id"]: row["fixed"]["molar_mass"]["value"]["magnitude"]
        for row in components if row["component_id"] in ("diethanolamine", "water")
    }
    amine_mass = feed["diethanolamine"] * masses["diethanolamine"]
    return amine_mass / (amine_mass + feed["water"] * masses["water"])


def mea_absorber_pressures(replay, wagner):
    absorber = []
    for row in replay["rows"]:
        source = replay["pressure_population"].get(row["identity"])
        if row["group"] == "Table S6 additions" and source:
            temperature = float(source["temperature_series_C"] or source["temperature_reported_C"]) + 273.15
            if temperature <= 353.2:
                absorber.append(row)
    absorber.extend(row for row in wagner if float(row["row"]["temperature_K"]) <= 353.2)
    return absorber


MEA_NOMINAL_PRESSURE_RECORDS = (
    "analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/evidence/F4/canonical-pressure.csv",
    "analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/evidence/F4/wagner-pressure.csv",
    MOVE + "mea/reported/fit/A.json.gz",
    STUDY + "results/E/MEA/replay.json.gz",
    STUDY + "results/display-replays/wagner.json.gz",
)
MEA_ABSORBER_MAX_K = 353.2


def mea_nominal_pressure_rows():
    canonical, wagner, fitted, replay, comparison = map(read, MEA_NOMINAL_PRESSURE_RECORDS)
    fitted_ids = {r["identity"] for r in fitted["replay"]["rows"] if r["unit"] == "Pa"}
    predicted = {r["identity"]: r for r in replay["rows"] + replay["hot_wagner"] + comparison["rows"]}
    for row in canonical + wagner:
        yield ("fitted" if row["target"] in fitted_ids else "not fitted", row, predicted[row["target"]])


def mea_nominal_pressure_points():
    for role, row, result in mea_nominal_pressure_rows():
        yield role, row["source"], float(row["temperature_K"]), result["observed"], result["value"]


def temperature_band(T):
    return 'absorber' if T <= MEA_ABSORBER_MAX_K else 'stripper' if T >= 370 else 'intermediate'


def mea_held_out_absorber_split():
    """Held-out MEA absorber-band pressures at the fitted temperatures and above them, as (target, point) pairs."""
    rows = list(mea_nominal_pressure_rows())
    fitted_max = max(float(row["temperature_K"]) for role, row, _ in rows if role == "fitted")
    held = [(row["target"], dict(observed=result["observed"], predicted=result["value"], T=float(row["temperature_K"])))
            for role, row, result in rows if role == "not fitted" and temperature_band(float(row["temperature_K"])) == "absorber"]
    # Measured isotherm temperatures scatter by tenths of a kelvin (Hilliard 2008 at 333.26 K belongs to 333 K).
    inside = [h for h in held if h[1]["T"] <= fitted_max + 1]
    above = [h for h in held if h[1]["T"] > fitted_max + 1]
    if min(p["T"] for _, p in above) < 350:
        raise ValueError("The held-out MEA absorber pressures above the fitted temperatures are no longer the 353 K isotherm")
    return inside, above


def result_values(required):
    values = {}

    def add(name, record, key, value):
        if name not in required:
            return
        def stage_path(locator):
            if locator in record_paths:
                return record_paths[locator]
            return re.sub(r"(?:analyses|data)/[^ ,;\[\]|]+",
                          lambda part: record_paths.get(normpath(part[0]), part[0]), locator)

        record = [stage_path(locator) for locator in record] if isinstance(record, (list, tuple)) else stage_path(record)
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
    for label, group in (("kim", "Kim"), ("kuranov-co2-free", "Kuranov-binary")):
        rows = [row for row in mdea_rows if row["group"] == group and row["unit"] == "Pa"]
        add(f"mdea-{label}-fitted-pressure-aard-mdea-results", record, f"rows[{group},Pa].observed,value",
            f"{stats(rows, predicted='value')['AARD_percent']:.1f}")
    for label, filename, groups in (
        ("dea-fitted-pressure", "DEA/property-comparisons/selected.json.gz", ("Lawson", "SeoHong", "Lal")),
        ("amp-fitted-pressure", "AMP_free/properties.json.gz", ("loaded-pressure", "hartono-2021-supplemental", "tong")),
    ):
        record = STUDY + "results/" + filename
        rows = [row for row in read(record)["rows"] if row["role"] == "fitted" and row["group"] in groups]
        key = "rows[fitted," + "|".join(groups) + "].observed,value"
        reported_aard[label] = (record, key, stats(rows, predicted="value")["AARD_percent"])
    locations = {
        "mea-fitted-pressure": ("abstract", "introduction", "mea-results", "conclusion", "reference-comparison"),
        "dea-fitted-pressure": ("abstract", "introduction", "dea-results", "conclusion", "reference-comparison"),
        "mdea-fitted-pressure": ("abstract", "introduction", "mdea-results", "transfer-comparison", "conclusion",
                                 "reference-comparison", "literature-subsets"),
        "amp-fitted-pressure": ("abstract", "introduction", "amp-results", "conclusion", "reference-comparison", "slope-comparison"),
        "mdea-ermatchkov-pressure": ("abstract", "mdea-results", "transfer-comparison", "literature-comparison", "reference-comparison"),
    }
    for quantity, occurrences in locations.items():
        record, key, value = reported_aard[quantity]
        for occurrence in occurrences:
            digits = 1 if occurrence in ("abstract", "introduction", "mea-results", "dea-results",
                                         "mdea-results", "amp-results", "conclusion") else 2
            add(f"{quantity}-aard-{occurrence}", record, key, f"{value:.{digits}f}")
    record, key, value = reported_aard["dea-fitted-pressure"]
    add("dea-fitted-pressure-aard-limitations", record, key, f"{value:.1f}")

    record = W_AMP_WITHOUT_HOT_PROPERTIES
    rows = [r for r in read(record)["rows"] if r["unit"] == "Pa" and r["status"] == "Available"]
    for source, group in (("hartono", "hartono-2021-supplemental"), ("tong", "tong")):
        hot = [r for r in rows if r["group"] == group and r["T_K"] >= 373.]
        if any(float(r["value"]) >= float(r["observed"]) for r in hot):
            raise ValueError(f"The AMP fit without the added pressures no longer underpredicts every {group} pressure from 373 K")
        score = stats(hot, predicted="value")["AARD_percent"]
        for passage, digits in (("supplement", 2), ("transfer", 1)):
            add(f"amp-without-hot-{source}-aard-{passage}", record, f"rows[{group}, Pa, T >= 373 K]: AARD",
                f"{score:.{digits}f}")
    fitted = [r for r in rows if r["group"] == "loaded-pressure" and r["role"] == "fitted"]
    add("amp-without-hot-fitted-pressure-aard-transfer", record, "rows[loaded-pressure, Pa, fitted]: AARD",
        f"{stats(fitted, predicted='value')['AARD_percent']:.1f}")

    for name, label, occurrences in (
        ("MEA", "mea", (("starts", 3), ("cai-weight", 2), ("reference-comparison", 3), ("restrictions", 3))),
        ("DEA", "dea", (("starts", 3), ("penalty", 3), ("reference-comparison", 3))),
        ("MDEA", "mdea", (("continuation", 3), ("basin-comparison", 3), ("reference-comparison", 3))),
        ("AMP_free", "amp", (("starts", 3), ("slope-comparison", 3), ("reference-comparison", 3))),
    ):
        record = STUDY + f"results/{name}/selection.json"
        selection = read(record)
        for passage, digits in occurrences:
            add(f"{label}-selected-objective-{passage}", record, "cost", f"{selection['cost']:.{digits}f}")

    record = STUDY + "results/MDEA/A.json.gz"
    fit = read(record)

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

    record = MEA_REPORTED_PROPERTIES
    reported = read(record)
    cai = reported["cai"]
    add("mea-reported-cai-temperature-objective", record, "cai.temperature.cost", f"{cai['temperature']['cost']:.3f}")
    add("mea-reported-cai-vapor-fraction-objective", record, "cai.mole_fraction.cost", f"{cai['mole_fraction']['cost']:.3f}")
    add("mea-reported-cai-total-objective", record, "objective", f"{reported['objective']:.3f}")
    add("mea-reported-cai-objective-share", record, "sum(cai[].cost) / objective",
        f"{100 * fsum(group['cost'] for group in cai.values()) / reported['objective']:.2f}")
    relative = [row["relative_se_percent"] for row in reported["fitted_pressure_bands"]]
    for passage, digits in (("results", 1), ("supplement", 2)):
        add(f"mea-reported-fitted-pressure-minimum-relative-se-{passage}", record,
            "min(fitted_pressure_bands[].relative_se_percent)", f"{min(relative):.{digits}f}")
        add(f"mea-reported-fitted-pressure-maximum-relative-se-{passage}", record,
            "max(fitted_pressure_bands[].relative_se_percent)", f"{max(relative):.1f}")
        add(f"mea-reported-covariance-volatilization-pressure-count-{passage}", record,
            "len(fitted_pressure_bands)", str(len(relative)))
    add("mea-reported-residual-variance", record, "variance", f"{reported['variance']:.3f}")
    add("mea-responsive-to-all-row-standard-error-ratio", record,
        "sqrt(variance / raw_row_variance)", f"{sqrt(reported['variance'] / reported['raw_row_variance']):.4f}")

    record = MOVE + "amp/reported/phase/supplied.json.gz"
    screen = distinct_phase_rows(read(record))
    grid = sum(row["key"].startswith("grid:") for row in screen)
    for passage in ("transfer", "supplement"):
        add(f"amp-reported-screen-grid-states-{passage}", record, "distinct rows[grid].count", str(grid))
        add(f"amp-reported-screen-measured-states-{passage}", record, "distinct rows[measurement-derived].count",
            str(len(screen) - grid))
    add("amp-reported-screen-states-transfer", record, "distinct rows.count", str(len(screen)))

    record = W_AMP_WITHOUT_HOT
    search = read(record)
    split_states = [row for row in search["classifications"] if row["liquid_directed"] and confirmed_split(row)]
    temperatures = [row["temperature_K"] for row in split_states]
    for bound, fun in (("minimum", min), ("maximum", max)):
        add(f"amp-without-hot-{bound}-split-temperature-supplement", record,
            f"classifications[confirmed splits].temperature_K: {bound}", f"{fun(temperatures):.2f}")
        for passage in ("conclusion", "transfer"):
            add(f"amp-without-hot-{bound}-split-temperature-{passage}", record,
                f"classifications[confirmed splits].temperature_K: {bound}", f"{fun(temperatures):.0f}")
    for passage in ("transfer", "supplement"):
        add(f"amp-without-hot-split-states-{passage}", record, "classifications[confirmed splits].count",
            str(len(split_states)))
        add(f"amp-without-hot-screen-states-{passage}", record, "distinct rows.count",
            str(len(distinct_phase_rows(search))))
    add("amp-without-hot-measured-split-states-supplement", record, "classifications[measured, confirmed splits].count",
        count_word(sum(not row["key"].startswith("grid:") for row in split_states)))
    record = STUDY + "results/AMP_free/screen/selected/native/state-inventory.json.gz"
    maximum = max(row["T_K"] for row in read(record)["rows"])
    add("amp-reported-screen-maximum-temperature", record, "rows[].T_K: max", f"{maximum:.2f}")
    record = W_AMP_WITHOUT_HOT_CONTROLS
    controls = read(record)["rows"]
    if controls.keys() != read(W_AMP_CONTROLS)["rows"].keys() or any(
            row["outcome"] != "confirmed split" for row in controls.values()):
        raise ValueError("The AMP fit without the added pressures no longer splits at every measured control of the AMP model")
    for passage in ("transfer", "supplement", "abstract", "limits", "conclusion"):
        add(f"amp-measured-control-states-{passage}", record, "len(rows)", count_word(len(controls)))
    # Worked positive control of Section S6: the first Hartono et al. state at 373 K under that fit.
    locator = "rows[hartono-2021:55:problem].result"
    worked = controls["hartono-2021:55:problem"]["result"]
    attempt = next(a for a in worked["attempts"] if a["confirmed"])
    liquids = attempt["diagnostics"]["phases"]
    for name, value in (
            ("pressure", f"{worked['P_Pa'] / 1e3:.1f}"),
            ("loading", f"{worked['feed_mol'][0] / worked['feed_mol'][1]:.2f}"),
            ("trial-distance", f"{worked['minimum_trial']['quantities']['tpd_over_rt']:.5f}"),
            ("first-density", f"{liquids[0]['density_mol_m3'] / 1e3:.1f}"),
            ("second-density", f"{liquids[1]['density_mol_m3'] / 1e3:.1f}"),
            ("first-water", f"{liquids[0]['x'][worked['species'].index('water')]:.3f}"),
            ("second-water", f"{liquids[1]['x'][worked['species'].index('water')]:.3f}"),
            ("first-amount", f"{attempt['amounts_mol'][0]:.2f}"), ("second-amount", f"{attempt['amounts_mol'][1]:.2f}"),
            ("gibbs-decrease", f"{attempt['Gibbs_decrease_over_RT_mol']:.5f}"),
            ("gibbs-error", prose_scientific(attempt["numerical_error_over_RT_mol"], ".1e")),
            ("row-tolerance", prose_scientific(worked["row_tolerance"], None))):
        add(f"amp-worked-control-{name}", record, locator, value)

    # Additional-liquid search of the AMP model at its liquid-vapor measured controls.
    record = MOVE + "amp/reported/phase/third-liquid.json.gz"
    third = read(record)["rows"]
    liquid_vapor = {key for key, row in read(W_AMP_CONTROLS)["rows"].items() if row["outcome"] == "L+V passed; L+L unresolved"}
    trials = {len(row["search"]["trials"]) for row in third.values()}
    if third.keys() != liquid_vapor or len(trials) != 1 or any(
            not row["search"]["completed"] or not row["search"]["no_descent_in_trial_set"]
            or any(t["kind"] != "Liquid" or t["descent"]
                   or abs(t["quantities"]["tpd_over_rt"]) > t["quantities"]["plane_value_error_estimate_over_rt"]
                   for t in row["search"]["trials"]) for row in third.values()):
        raise ValueError("The additional-liquid search no longer finds no descent at every liquid-vapor AMP control")
    for passage in ("abstract", "transfer", "limits", "conclusion", "supplement"):
        add(f"amp-third-liquid-trial-count-{passage}", record, "rows[].search.trials.count (per state)",
            count_word(next(iter(trials))))

    # AMP fit without the Tong et al. pressures: Hartono et al. above 353 K fitted, Tong et al. predicted.
    record = MOVE + "amp/without-tong/phase/supplied.json.gz"
    search = read(record)
    if ({row["key"] for row in distinct_phase_rows(search)} != {row["key"] for row in distinct_phase_rows(read(W_AMP_WITHOUT_HOT))}
            or any(search_class(row) != "searched, no instability" for row in distinct_phase_rows(search))):
        raise ValueError("The AMP fit without the Tong et al. pressures no longer has no detected instability at the states searched for the other fits")
    record = MOVE + "amp/without-tong/phase/measured-controls.json.gz"
    controls = read(record)["rows"]
    if controls.keys() != read(W_AMP_CONTROLS)["rows"].keys() or any(row["outcome"] == "confirmed split" for row in controls.values()):
        raise ValueError("The AMP fit without the Tong et al. pressures no longer has no split at the measured controls")
    for name, outcome in (("no-descent", "No resolved descent"), ("liquid-vapor", "L+V passed; L+L unresolved")):
        add(f"amp-without-tong-control-{name}-supplement", record, f"rows[outcome {outcome}].count",
            count_word(sum(row["outcome"] == outcome for row in controls.values())))
    record = MOVE + "amp/without-tong/properties/summary.json.gz"
    rows = [r for r in read(record)["rows"] if r["unit"] == "Pa" and r["status"] == "Available"]
    for source, group, role in (("hartono", "hartono-2021-supplemental", "fitted"), ("tong", "tong", "not fitted")):
        hot = [r for r in rows if r["group"] == group and r["T_K"] >= 373.]
        if {r["role"] for r in hot} != {role}:
            raise ValueError(f"The {group} pressures from 373 K are no longer all {role} in the AMP fit without Tong et al.")
        score = stats(hot, predicted="value")["AARD_percent"]
        for passage, digits in (("supplement", 2), ("transfer", 1)):
            add(f"amp-without-tong-{source}-aard-{passage}", record, f"rows[{group}, Pa, T >= 373 K]: AARD",
                f"{score:.{digits}f}")

    # Carbamate-hydrolysis correlation held at its starting form (sensitivity of the reported DEA and AMP fits).
    for amine, source in (("dea", DEA_R4_SOURCE), ("amp", AMP_R4_SOURCE)):
        record = MOVE + f"{amine}/fixed-r4/properties/summary.json.gz"
        comparison = read(record)["comparison"]
        start = source_r4(source)
        held = comparison["reaction_correlations"]["fixed_r4"]
        if (held["a"], held["b"]) != (start["a"], start["b"]) or comparison["active_bounds"]["fixed_r4"]:
            raise ValueError(f"The {amine.upper()} fixed-R4 fit no longer holds the starting correlation off its bounds")
        for fit in ("reported", "fixed_r4"):
            label = fit.replace("_", "-")
            for passage, digits in (("transfer", ".3g"), ("supplement", ".4g")):
                add(f"{amine}-fixed-r4-{label}-objective-{passage}", record, f"comparison.objective.{fit}",
                    format(comparison["objective"][fit], digits))
        add(f"{amine}-fixed-r4-reported-bound-count-supplement", record, "comparison.active_bounds.reported.count",
            count_word(len(comparison["active_bounds"]["reported"]), zero="no"))
        groups = {(s["group"], s["role"], s["unit"]): s for s in comparison["statistics"]}
        for name, group, passages in {
            "dea": (("lawson", ("Lawson", "fitted", "Pa"), ("transfer", "supplement")),
                    ("lal", ("Lal", "fitted", "Pa"), ("supplement",)),
                    ("carson", ("Carson", "fitted", "J/mol CO2"), ("supplement",)),
                    ("seo-hong", ("SeoHong", "not fitted", "Pa"), ("supplement",))),
            "amp": (("nmr", ("nmr", "fitted", "dimensionless"), ("transfer", "supplement")),
                    ("tong", ("tong", "fitted", "Pa"), ("transfer", "supplement")),
                    ("hartono", ("hartono-2021-supplemental", "fitted", "Pa"), ("supplement",)),
                    ("loaded", ("loaded-pressure", "fitted", "Pa"), ("supplement",))),
        }[amine]:
            for fit in ("reported", "fixed_r4"):
                value = groups[group][fit]["AARD_percent"]
                for passage in passages:
                    add(f"{amine}-fixed-r4-{name}-{fit.replace('_', '-')}-aard-{passage}", record,
                        f"comparison.statistics[{', '.join(group)}].{fit}.AARD_percent",
                        f"{value:.{1 if passage == 'transfer' else 2}f}")

    # Zheng et al. heats at the calculated saturation loading, where the measured final loading lies above it.
    record = MOVE + "mdea/reported/zheng-saturation/summary.json.gz"
    zheng = read(record)
    if any(r["calculated_loading"] >= r["measured_loading"] or not r["measured_loading_phase"]["vapor_descent"]
           for r in zheng["rows"]):
        raise ValueError("A Zheng et al. state no longer saturates below its measured loading with a vapor at that loading")
    for passage, digits in (("transfer", 1), ("supplement", 2)):
        add(f"mdea-zheng-saturation-states-{passage}", record, "len(rows)", count_word(len(zheng["rows"])))
        for name, field in (("saturation-loading", "loading"), ("saturation-heat", "heat_at_calculated_loading")):
            add(f"mdea-zheng-{name}-aard-{passage}", record, f"statistics.{field}.AARD_percent",
                f"{zheng['statistics'][field]['AARD_percent']:.{digits}f}")

    # Static permittivity: the CO2-free calibration values and the loaded values that Hajj et al. inferred.
    record = MOVE + "mea/reported/permittivity-validation/summary.json.gz"
    calibration = read(record)["statistics"]
    add("mea-permittivity-calibration-rows-supplement", record, "statistics.rows", str(calibration["rows"]))
    add("mea-permittivity-calibration-aard-supplement", record, "statistics.AARD_percent",
        f"{calibration['AARD_percent']:.2f}")
    add("mea-permittivity-calibration-bias-supplement", record, "statistics.bias_percent",
        f"{calibration['bias_percent']:+.2f}")
    record = MOVE + "mea/reported/hajj-permittivity/summary.json.gz"
    hajj = read(record)
    if (any(r["predicted"] >= r["inferred"] for r in hajj["rows"])
            or any(i["predicted_change"] >= 0 or i["inferred_change"] <= 0 for i in hajj["isotherms"])):
        raise ValueError("A Hajj et al. permittivity is no longer above its calculated value, or an isotherm trend changed sign")
    add("mea-hajj-permittivity-states-supplement", record, "statistics.rows", str(hajj["statistics"]["rows"]))
    add("mea-hajj-permittivity-isotherms-supplement", record, "len(isotherms)", count_word(len(hajj["isotherms"])))
    add("mea-hajj-permittivity-aard-supplement", record, "statistics.AARD_percent",
        f"{hajj['statistics']['AARD_percent']:.2f}")
    for amine in ("mea", "amp"):
        record = MOVE + f"{amine}/reported/alternate-starts/summary.json.gz"
        count = read(record)["tied_count"]
        for passage in ("methods", "supplement"):
            add(f"{amine}-tied-start-count-{passage}", record, "tied_count", NUMBER_WORDS[count])

    record = GIBBS_DERIVATIVES
    checks = {(row["state"], row["comparison"]): row for row in read(record)["rows"]}
    relative_max = max(abs(checks[f"selected-{name}", "volume"]["relative_error"])
                       for name in ("MEA", "DEA", "AMP_free", "MDEA"))
    mantissa, exponent = f"{relative_max:.1e}".split("e")
    for amine, design, scale, digits in (
        ("mea", "MEA", 1000, 3), ("dea", "DEA", 1000, 3),
        ("amp", "AMP_free", 1000, 2), ("mdea", "MDEA", 1000000, 3),
    ):
        state = f"selected-{design}"
        volume = checks[state, "volume"]
        for passage in ("theory", "supplement"):
            pass
        mantissa, exponent = f"{volume['relative_error']:.2e}".split("e")
        relative = rf"{mantissa}\times10^{{{int(exponent)}}}"
        if amine in ("mea", "dea"):
            pass
        places = 1 if amine in ("mea", "dea") else 2
        passages = ("theory", "conclusion", "abstract") if amine == "mea" else (
            ("theory", "conclusion") if amine == "dea" else ("theory", "abstract") if amine == "mdea" else ("theory",))
        for passage in passages:
            pass

    record = W_MDEA_PROPERTIES
    kuranov, kamps = mdea_pressure_comparisons()
    for passage in ("transfer", "supplement"):
        add(f"mdea-kuranov-all-pressure-aard-{passage}", (record, KURANOV_DATA),
            "rows matched by source_row to kuranov[]: AARD", f"{kuranov['AARD_percent']:.2f}")
    for key, label, value in (
        ("common_rows", "common-pressure-count", str(kamps["common_rows"])),
        ("common_AARD_percent", "common-pressure-aard", f"{kamps['common_AARD_percent']:.2f}"),
        ("full_AARD_percent", "all-pressure-aard", f"{kamps['full_AARD_percent']:.2f}"),
        ("additional_signed_percent", "additional-pressure-deviation", f"{kamps['additional_signed_percent']:+.2f}"),
    ):
        add(f"mdea-corrected-kamps-{label}-transfer", record, f"kamps.{key}", value)
    for quantity, key in (("source-row", "source_row"), ("molality", "m_MDEA_mol_kg_water")):
        add(f"mdea-corrected-kamps-additional-pressure-{quantity}", record, f"kamps.additional_row.row.{key}",
            kamps['additional_row']['row'][key])
    for quantity, key, digits in (("measured", "observed", 3), ("predicted", "value", 3)):
        add(f"mdea-corrected-kamps-additional-pressure-{quantity}", record,
            f"kamps.additional_row.{key} / 1e6", f"{kamps['additional_row'][key]/1e6:.{digits}f}")
    record = W_WATER
    water = read(record)
    for passage in ("fit-input", "fit-deviations"):
        add(f"water-fit-vapor-pressure-temperature-count-{passage}", record,
            "fitted_rows.psat", str(water["fitted_rows"]["psat"]))
    diameter = "component/water/segment_diameter/constant-plus-sum-of-exponentials/constant"
    add("water-fit-segment-diameter-offset-supplement", record,
        f"coefficients.{diameter}", f"{water['coefficients'][diameter]:.7f}")
    add("water-fit-isobaric-heat-capacity-input-count-supplement", record, "fitted_rows.cp",
        str(water["fitted_rows"]["cp"]))
    add("water-fitted-parameter-count", record, "coefficients.count", NUMBER_WORDS[len(water["coefficients"])])
    for quantity, label in (("psat", "vapor-pressure"), ("rho", "liquid-density"),
                            ("saturated_liquid_rho", "saturated-liquid-density"), ("cp", "heat-capacity")):
        for grid in sorted({row["grid"] for row in water["rows"]}):
            cohort = [row for row in water["rows"] if row["grid"] == grid]
            errors = [100 * abs(row["predicted"][quantity] / row["observed"][quantity] - 1) for row in cohort]
            digits = 2 if quantity == "cp" else 3
            add(f"water-fit-{grid}-{label}-mean-deviation", record,
                f"rows[{grid}].{quantity} AARD", f"{mean(errors):.{digits}f}")
            add(f"water-fit-{grid}-{label}-max-deviation", record,
                f"rows[{grid}].{quantity} maximum relative deviation", f"{max(errors):.{digits}f}")
    roots = water["roots"]
    for name, key in (("liquid-root-density", "density_mol_m3"),
                      ("liquid-vapor-gibbs-difference", "delta_G_liquid_minus_vapor_J_mol"),
                      ("density-margin", "density_margin_mol_m3")):
        add(f"pure-water-selected-{name}", record, f"roots.{key} / 1000", f"{roots[key] / 1000:.2f}")
    mdea_screen = read(W_MDEA_SCREEN)
    mdea_rows = mdea_screen["rows"]
    mdea_grid = [r for r in mdea_rows if r["key"].startswith("grid:")]
    measured = [row for row in distinct_phase_rows(mdea_screen) if not row["key"].startswith("grid:")]
    measured_counts = collections.Counter(search_class(row) for row in measured)
    for passage in ("transfer", "supplement-design"):
        add(f"mdea-measured-states-{passage}", W_MDEA_SCREEN,
            "distinct rows[measurement-derived].count", str(len(measured)))
    for passage in ("transfer", "supplement"):
        add(f"mdea-measured-states-without-instability-{passage}", W_MDEA_SCREEN,
            "distinct measured rows[searched, no instability].count",
            str(measured_counts["searched, no instability"]))
    for passage in ("supplement", "transfer", "abstract", "limits", "conclusion"):
        add(f"mdea-measured-states-unclassified-{passage}", W_MDEA_SCREEN,
            "distinct measured rows[unavailable].count", count_word(measured_counts["unavailable"], zero="zero"))
    record = MOVE + "mdea/reported/phase/capped-heat-diagnosis.json.gz"
    diagnosis = read(record)["rows"]
    outside = [row for row in diagnosis if row["key"] not in mdea_screen["aliases"]
               and "outside_interval" in row["cause"]]
    within = [row for row in diagnosis if row["key"] not in mdea_screen["aliases"] and row.get("minimum") is not None
              and abs(row["minimum"]) <= row["uncertainty"]]
    add("mdea-merkley-searches-outside-caloric-interval-supplement", record,
        "rows[cause includes outside_interval].count", count_word(len(outside), zero="zero"))
    add("mdea-merkley-searches-within-resolution-supplement", record,
        "rows[abs(minimum) <= uncertainty].count", count_word(len(within), zero="zero"))
    keys = {row["key"] for row in within}
    supplied = {row["supplied_trial_counts"]["available"] for row in mdea_rows
                if row["key"] in keys and "supplied_trial_counts" in row}
    if len(supplied) == 1:
        add("mdea-supplied-trial-count-supplement", (record, W_MDEA_SCREEN),
            "rows[abs(minimum) <= uncertainty].supplied_trial_counts.available (per state)", str(supplied.pop()))
    observations = {row["identity"]: row["row"] for row in read(W_MDEA_PROPERTIES)["rows"]}
    states = []
    for row in mdea_screen["classifications"]:
        identity = row["key"].rsplit(":", 1)[0]
        if identity.startswith("Merkley-capped:"):
            source = {"source_key": "Merkley1987"}
        else:
            source = observations.get(identity) or observations[identity.rsplit(":", 1)[0]]
        states.append(dict(row, source=source))
    if len(states) != measured_counts["descent"]:
        raise ValueError("The MDEA classifications differ from the distinct descent states")
    for passage in ("transfer", "supplement-total", "supplement-by-source", "limits"):
        add(f"mdea-distinct-descent-states-{passage}", W_MDEA_SCREEN, "len(classifications)", str(len(states)))
    mdea_bubbles = read(W_MDEA_PROPERTIES)["mdea_bubble"]
    zheng = {str(observations[key.rsplit(":", 1)[0]]["source_row"]): key
             for key in mdea_bubbles
             if observations.get(key.rsplit(":", 1)[0], {}).get("source_key") == "Zheng2020"}
    for row, digits, passages in (("2", 3, ("transfer", "supplement")), ("5", 2, ("transfer",))):
        if row not in zheng:
            continue
        key = zheng[row]
        result = mdea_bubbles[key]
        for passage in passages:
            add(f"mdea-zheng-row-{row}-bubble-pressure-{passage}", W_MDEA_PROPERTIES,
                f"mdea_bubble[{key}].bubble_Pa / 1e6", f"{result['bubble_Pa']/1e6:.{digits}f}")
    mea_grid = W_MEA_PHASE + "grid.json.gz"
    mea_measured = W_MEA_PHASE + "measured.json.gz"
    mea_census = W_MEA_PHASE + "census.json.gz"
    grid_rows, census_rows = (read(p)["rows"] for p in (mea_grid, mea_census))
    measured_rows = distinct_mea_measured_rows(read(mea_measured))
    census_classes = collections.Counter(row["classification"] for row in census_rows)
    for passage in ("transfer", "supplement", "limits"):
        add(f"mea-liquid-grid-requests-{passage}", mea_grid, "len(rows)", str(len(grid_rows)))
        add(f"mea-measured-state-search-requests-{passage}", mea_measured, "distinct measured states by temperature, pressure and composition", str(len(measured_rows)))
        add(f"mea-census-two-phase-parent-count-{passage}", mea_census, "rows[passed-two-phase].count",
            str(census_classes["passed-two-phase"]))
    for passage in ("transfer-all", "transfer-outcomes", "supplement", "limits"):
        add(f"mea-liquid-vapor-census-requests-{passage}", mea_census, "len(rows)", str(len(census_rows)))
    for population, count in collections.Counter(r["key"].split("|", 1)[0] for r in grid_rows).items():
        add(f"mea-liquid-grid-{population}-requests", mea_grid, f"rows[{population}].count", str(count))

    record = W_DEA_SCREEN
    dea_screen = read(record)
    dea_rows = distinct_phase_rows(dea_screen)
    grid = sum(row["key"].startswith("grid:") for row in dea_rows)
    for label, key, count in (
        ("grid-requests", "rows[grid].count", grid),
        ("measurement-requests", "rows[measurement-derived].count", len(dea_rows) - grid),
        ("transfer-requests", "len(rows)", len(dea_screen["rows"])),
        ("transfer-completed", "rows[available].count", sum(row["available"] for row in dea_screen["rows"])),
        ("supplement-completed", "rows[available].count", sum(row["available"] for row in dea_screen["rows"])),
    ):
        add(f"dea-phase-search-{label}", record, key, str(count))
    add("dea-measured-state-search-count-transfer", W_DEA_SCREEN, "rows[measurement-derived].count",
        str(len(dea_rows) - grid))
    add("dea-grid-state-search-count-transfer", W_DEA_SCREEN, "rows[grid].count", str(grid))

    record = STUDY + "results/DEA/property-comparisons/selected.json.gz"
    fitted = [row for row in read(record)["rows"] if row["role"] == "fitted"]
    carson = [row for row in fitted if row["group"] == "Carson"]
    seo_hong_pressure_count = sum(row["group"] == "SeoHong" and row["unit"] == "Pa" for row in fitted)
    for passage in ("methods", "transfer"):
        add(f"dea-seo-hong-fitted-pressure-count-{passage}", record, "rows[SeoHong,Pa,fitted].count",
            str(seo_hong_pressure_count))
    for label, fraction in (("lowest", "0.10"), ("intermediate", "0.20"), ("highest", "0.30")):
        count = sum(row["row"]["DEA_mass_fraction"] == fraction for row in carson)
    for reaction, label in (("carbamate-hydrolysis", "r4"), ("DEA-dissociation", "r5")):
        outside = sum(row["unit"] == "Pa" and row["outside_ranges"].get(reaction, False) for row in fitted)
        add(f"dea-fitted-pressure-outside-{label}-range", record,
            f"rows[fitted,Pa].outside_ranges.{reaction}: count", str(outside))
    record = STUDY + "results/display-replays/mea-comparisons.json.gz"
    kim = read(record)["kim_2007"]
    hot = [row for row in kim if row["T_K"].startswith("393.15") and row["interval_status"] == "available"]
    for passage in ("results", "limits"):
        add(f"mea-kim-svendsen-hot-interval-count-{passage}", record, "kim_2007[393.15 K,available].count", str(len(hot)))
    rmse = sqrt(fsum((float(row["predicted"]) - float(row["observed"]))**2 for row in hot) / len(hot))
    add("mea-kim-svendsen-hot-interval-rmse-results", record,
        "kim_2007[393.15 K,available].predicted,observed: RMSE (kJ/mol)", f"{rmse:.2f}")
    clean_hot = [row for row in hot if 'True' not in (row["source_inconsistent"], row["first_120"])]
    key = "kim_2007[393.15 K, available, unflagged]"
    for passage in ("transfer", "limits"):
        add(f"mea-kim-svendsen-unflagged-hot-interval-count-{passage}", record, key + ".count", str(len(clean_hot)))
    kim_svendsen_bias = 100 * fsum(1 - float(row["predicted"]) / float(row["observed"]) for row in clean_hot) / len(clean_hot)
    add("mea-kim-svendsen-hot-interval-low-bias-transfer", record, key + ": negative signed deviation %", f"{kim_svendsen_bias:.1f}")
    add("mea-kim-svendsen-hot-interval-low-bias-limit", record, key + ": negative signed deviation %", f"{kim_svendsen_bias:.1f}")
    for flag, label in (("source_inconsistent", "inconsistent"), ("first_120", "first-additions")):
        count = sum(row[flag] == "True" for row in hot)
        add(f"mea-kim-svendsen-hot-{label}-intervals-transfer", record,
            f"kim_2007[393.15 K,available].{flag}: count", NUMBER_WORDS[count])
    add("mea-kim-svendsen-hot-flagged-intervals-transfer", record,
        "kim_2007[393.15 K,available]: count flagged by either source_inconsistent or first_120",
        NUMBER_WORDS[len(hot) - len(clean_hot)])
    record = STUDY + "results/MEA/heat-comparison.json.gz"
    heats = read(record)["rows"]["rows"]
    for source, label in (("Kim2014", "kim"), ("Vinjarapu2024", "vinjarapu")):
        rows = [row for row in heats if row["source"] == source and row["T_K"] >= 370
                and row["predicted_kJ_mol"] is not None]
        bias = 100 * fsum(1 - row["predicted_kJ_mol"] / row["observed_kJ_mol"] for row in rows) / len(rows)
        add(f"mea-{label}-hot-heat-low-bias-transfer", record,
            f"rows.rows[{source},stripper, available]: negative signed deviation %", f"{bias:.1f}")
        if label == "vinjarapu":
            add("mea-vinjarapu-hot-heat-low-bias-limit", record,
                f"rows.rows[{source},stripper, available]: negative signed deviation %", f"{bias:.1f}")

    record = STUDY + "results/display-replays/mea-comparisons.json.gz"
    carbonate = read(record)["carbonate_share"]
    ratios = [row["value"] / row["observed"] for row in carbonate]
    geometric = math.exp(fsum(map(math.log, ratios)) / len(ratios))
    for passage in ("mea-results", "transfer"):
        add(f"mea-carbonate-share-geometric-mean-{passage}", record,
            "carbonate_share[].value / observed: geometric mean", f"{geometric:.3f}")
    add("mea-carbonate-share-aard-results", record, "carbonate_share[].value/observed: AARD",
        f"{100 * fsum(abs(ratio - 1) for ratio in ratios) / len(ratios):.2f}")

    record = W_MEA_ABLATION_FIT
    ion = "pair/bicarbonate-anion/water/k_ij"
    uncertainty = read(record)["diagnostics"]["uncertainty"]["conditional_standard_error"]
    add("mea-shared-bicarbonate-water-conditional-se-supplement", record,
        f"diagnostics.uncertainty.conditional_standard_error[{ion}]", f"{uncertainty[ion]:.2f}")

    record = STUDY + "results/AMP_free/properties.json.gz"
    amp_pressures = [row for row in read(record)["rows"]
                     if row["role"] == "fitted" and row["group"] in ("loaded-pressure", "hartono-2021-supplemental", "tong")]
    n_pressure = len(amp_pressures)
    key = "rows[fitted,loaded-pressure|hartono-2021-supplemental|tong].count"
    for passage in ("introduction", "transfer", "conclusion", "residual-figure-caption", "extended-data", "slope-comparison"):
        add(f"amp-reported-loaded-pressure-count-{passage}", record, key, str(n_pressure))
    for group, label in (("hartono-2021-supplemental", "hot-hartono"), ("tong", "tong")):
        count = sum(row["group"] == group for row in amp_pressures)
        passages = ("conclusion", "transfer", "supplement-additions", "supplement-deviations")
        if group == "tong":
            passages += ("literature",)
        for passage in passages:
            add(f"amp-reported-{label}-fitted-pressure-count-{passage}", record,
                f"rows[fitted,{group}].count", str(count))

    record = STUDY + f"results/AMP_free/{starts['AMP_free']}.json.gz"
    n_fit = len(read(record)["replay"]["rows"])
    for passage in ("transfer", "methods", "supplement"):
        add(f"amp-reported-objective-row-count-{passage}", record, "replay.rows.count", str(n_fit))
    record = W_AMP_WITHOUT_HOT_REPLAY
    rows = read(record)["replay"]["rows"]
    add("amp-without-hot-objective-row-count-supplement", record, "replay.rows.count", str(len(rows)))

    record = STUDY + "results/MDEA/properties.json.gz"
    available_rows = read(record)["rows"]
    mdea_not_fitted = sum(row["group"] in ("Kuranov-413K", "corrected-Kamps", "Sedighi") and row["role"] == "not fitted"
                          and row["status"] == "Available" for row in available_rows)
    add("mdea-not-fitted-total-pressure-count-residual-figure-caption", record,
        "rows[Kuranov-413K|corrected-Kamps|Sedighi, not fitted, Available].count", str(mdea_not_fitted))
    rows = [row for row in available_rows if row["group"] == "Ermatchkov" and row["unit"] == "Pa"]
    for passage in ("abstract", "mdea-results", "shared-comparison", "literature", "weighting"):
        add(f"mdea-ermatchkov-partial-pressure-count-{passage}", record, "rows[Ermatchkov,Pa].count", str(len(rows)))
    rows = [row for row in available_rows if row["group"] == "Kuranov" and row["role"] == "fitted"]
    for passage in ("introduction", "conclusion", "relative-weight", "mdea-results", "shared-comparison",
                    "weighting", "normalized-weight", "historical-comparison", "residual-figure-caption", "supplement-weighting",
                    "published-fit-coverage", "literature-subsets"):
        add(f"mdea-fitted-kuranov-pressure-count-{passage}", record, "rows[Kuranov,fitted].count", str(len(rows)))

    record = STUDY + "results/DEA/property-comparisons/selected.json.gz"
    dea_rows = read(record)["rows"]
    dea_pressures = [row for row in dea_rows if row["unit"] == "Pa" and row["role"] == "fitted"]
    for passage in ("introduction", "conclusion", "dea-results", "residual-figure-caption", "expanded-comparison", "range-check"):
        add(f"dea-fitted-partial-pressure-count-{passage}", record, "rows[Pa,fitted].count", str(len(dea_pressures)))
    add("dea-not-fitted-partial-pressure-count-residual-figure-caption", record,
        "rows[Lawson|Lawson-394K|SeoHong|Lal|Lawson-VIII, Pa, not fitted, Available].count",
        str(sum(row["group"] in ('Lawson', 'Lawson-394K', 'SeoHong', 'Lal', 'Lawson-VIII')
                and row["unit"] == "Pa" and row["role"] == "not fitted" and row["status"] == "Available"
                for row in dea_rows)))
    add("dea-comparison-only-partial-pressure-count-residual-figure-caption", record,
        "rows[Lawson-VIII, comparison only, Available].count",
        str(sum(row["group"] == "Lawson-VIII" and row["role"] == "comparison only" and row["status"] == "Available"
                for row in dea_rows)))

    hot = [dict(observed=observed, predicted=value)
           for role, _, T, observed, value in mea_nominal_pressure_points()
           if role == "not fitted" and temperature_band(T) == "stripper"]
    for label, part in zip(("fitted-temperature", "353"), mea_held_out_absorber_split(), strict=True):
        part = stats([point for _, point in part])
        locator = f"canonical and Wagner [not fitted, absorber band, {label}]"
        add(f"mea-held-out-{label}-pressure-count", MEA_NOMINAL_PRESSURE_RECORDS, locator + ".count", str(part["n"]))
        add(f"mea-held-out-{label}-pressure-aard", MEA_NOMINAL_PRESSURE_RECORDS, locator + ".AARD_percent",
            f"{part['AARD_percent']:.1f}")
        add(f"mea-held-out-{label}-pressure-bias", MEA_NOMINAL_PRESSURE_RECORDS, locator + ".bias_percent",
            f"{part['bias_percent']:.1f}")
    locator = "canonical and Wagner [not fitted, stripper temperature band]"
    for passage in ("supplement", "transfer"):
        add(f"mea-hot-pressure-count-{passage}", MEA_NOMINAL_PRESSURE_RECORDS, locator + ".count", str(len(hot)))
    add("mea-hot-pressure-aard-transfer", MEA_NOMINAL_PRESSURE_RECORDS, locator + ".AARD_percent",
        f"{stats(hot)['AARD_percent']:.1f}")

    record = STUDY + "results/MDEA/property-comparisons/A.json.gz"
    row72 = read(record)["additional_Kuranov_72"]
    add("mdea-kuranov-row-72-reported-reference-pressure", record, "additional_Kuranov_72.value / 1e6",
        f"{row72['value']/1e6:.4f}")
    add("mdea-kuranov-row-72-measured-pressure", record, "additional_Kuranov_72.observed / 1e6",
        f"{row72['observed']/1e6:.4f}")

    record = W_MDEA_BINARY
    count = len(read(record)["rows"])
    for passage in ("transfer", "figure-caption", "supplement"):
        add(f"mdea-binary-gap-tested-temperatures-{passage}", record, "rows.count", str(count))

    record = STUDY + "results/E/MEA/replay.json.gz"
    pressure_stats = read(record)["summary"]["pressure"]
    for cohort, passages in (
        ("legacy", ("results", "conclusion", "historical-comparison", "residual-caption",
                    "weighting-sensitivity", "weighting-interpretation")),
        ("added", ("results", "residual-caption", "restriction-comparison", "weighting-sensitivity")),
    ):
        for passage in passages:
            add(f"mea-{cohort}-pressure-count-{passage}", record, f"summary.pressure.{cohort}.attempted",
                str(pressure_stats[cohort]["attempted"]))
    replay = read(record)
    population = replay["pressure_population"]
    fitted_ids = {x["row"]["id"] for x in replay["rows"]
                  if x["group"] == "common149" and x["row"].get("quantity") == "PartialPressure"}
    assert len(fitted_ids) == pressure_stats["legacy"]["attempted"]
    for source, label in (("Hilliard2008", "hilliard"), ("Jou1995", "jou")):
        ids = [k for k, v in population.items() if v["source_key"] == source]
        add(f"mea-{label}-fitted-pressure-count-methods", record,
            f"pressure_population[{source}] in fitted rows: count", str(sum(k in fitted_ids for k in ids)))
        add(f"mea-{label}-pressure-count-methods", record, f"pressure_population[{source}].count", str(len(ids)))
    unfitted, = (v for k, v in population.items() if v["source_key"] == "Hilliard2008" and k not in fitted_ids)
    add("mea-hilliard-unfitted-pressure-temperature-methods", record,
        f"pressure_population[{unfitted['observation_id']}].temperature_reported_C + 273.15",
        f"{float(unfitted['temperature_reported_C']) + 273.15:.2f}")
    for label, cohort in (("added-same-sources", "added"), ("aronu-nominal", "Aronu2011")):
        add(f"mea-{label}-pressure-aard-results", record,
            f"summary.pressure.{cohort}.AARD_percent", f"{pressure_stats[cohort]['AARD_percent']:.1f}")
    for passage in ("mea-results", "literature-comparison"):
        add(f"mea-mamun-pressure-aard-{passage}", record, "summary.pressure.Mamun2005.AARD_percent",
            f"{pressure_stats['Mamun2005']['AARD_percent']:.2f}")
        add(f"mea-mamun-assessment-pressure-count-{passage}", record, "summary.pressure.Mamun2005.attempted",
            str(pressure_stats["Mamun2005"]["attempted"]))
    record = STUDY + "results/MEA/off-window.json.gz"
    rows = read(record)["rows"]
    for label, concentration in (("lower", 15), ("higher", 45)):
        pressures = [row for row in rows if row["group"] == "Aronu2011"
                     and round(100 * float(row["row"]["source_coordinates"]["MEA_weight_fraction"])) == concentration and row["status"] == "Available"]
        add(f"mea-aronu-{label}-concentration-pressure-aard-results", record,
            f"rows[Aronu2011,{concentration} wt%,Available].AARD_percent",
            f"{stats(pressures, predicted='value')['AARD_percent']:.1f}")

    record = W_MDEA_WITHOUT_GAP_BOUND
    binary_search = read(record)
    add("mdea-unbounded-binary-states-searched", record, "searched", str(binary_search["searched"]))
    add("mdea-unbounded-binary-instabilities", record, "liquid_descent", str(binary_search["liquid_descent"]))
    unstable = [row["T_K"] for row in binary_search["rows"] if (row["search"]["value"] or 0) < 0]
    assert len(unstable) == binary_search["liquid_descent"]
    add("mdea-unbounded-binary-minimum-instability-temperature", record, "rows[search.value < 0].T_K: min",
        f"{min(unstable):.0f}")

    for key, source in (("reported", W_MDEA_NEUTRAL),
                        ("unweighted-reactive", W_MDEA_UNWEIGHTED_REACTIVE),
                        ("reported-reactive", W_MDEA_REACTIVE)):
        search = read(source)
        add(f"mdea-{key}-binary-states-searched", source, "searched", str(search["searched"]))
        add(f"mdea-{key}-binary-instabilities", source, "liquid_descent", str(search["liquid_descent"]))
        add(f"mdea-{key}-binary-instabilities-words", source, "liquid_descent", count_word(search["liquid_descent"]))
    for name in ("without-binary-gap-bound", "reported"):
        manifest = MOVE + f"mdea/{name}/fit/manifest.json.gz"
        for passage in ("", "-transfer"):
            add(f"mdea-{name}-binary-pressure-log-scale{passage}", manifest, "1 / sqrt(n * weight) for Kuranov-binary",
                f"{mdea_binary_pressure_scale(read(manifest)):g}")
    endpoint = MOVE + "mdea/reported/fit/A.json.gz"
    coordinate = next(row for row in read(endpoint)["endpoint"]["coordinates"]
                      if row["identity"].startswith("pair/mdea-water/k_ij/a0"))
    k423 = coordinate["origin"]
    onset = next(row["k_gap"] for row in read(W_MDEA_BINARY)["rows"] if row["T_K"] == 423)
    add("mdea-reported-water-k-423", endpoint, "MDEA–water k(423 K)", f"{k423:.5f}")
    add("mdea-water-gap-onset-k-423", W_MDEA_BINARY, "rows[T_K=423].k_gap", f"{onset:.5f}")
    add("mdea-reported-water-k-423-distance-to-gap-onset", (endpoint, W_MDEA_BINARY),
        "rows[T_K=423].k_gap minus MDEA–water k(423 K)", f"{onset - k423:.3f}")

    fixed = FixedReference(read)
    for family in ("MEA", "DEA", "MDEA", "AMP_free"):
        record = STUDY + f"results/{family}/{fixed.selections[family]['selected']}.json.gz"
        rows = fixed.fits[family]["replay"]["rows"]
        amine = family.split("_")[0].lower()
        if family == "MDEA":
            pass
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
            locations = (("methods", "transfer", "supplement") if quantity != "integral-heats" else ("transfer",)
                         ) if family == "MDEA" else ("methods",)
            for passage in locations:
                add(f"{amine}-{quantity}-objective-share-{passage}", record, key, f"{share:.1f}")

    binary = read(W_DEA_BINARY)["rows"]
    for group, label in (("Horstmann VLE", "horstmann"), ("Cai", "cai")):
        cohort = [row for row in binary if row["group"] == group and row["role"] == "fitted beforehand"]
        aard = stats([dict(observed=row["observed"], predicted=row["law"]["value"]) for row in cohort])["AARD_percent"]
        for passage in ("transfer", "supplement") if label == "horstmann" else ("supplement",):
            digits = 1 if passage == "transfer" else 2
            add(f"dea-binary-law-{label}-pressure-aard-{passage}", W_DEA_BINARY,
                f"rows[{group}, fitted beforehand].law.value AARD", f"{aard:.{digits}f}")
        if label == "cai":
            add("dea-binary-law-cai-pressure-aard-transfer", W_DEA_BINARY,
                f"rows[{group}, fitted beforehand].law.value AARD", f"{aard:.1f}")
    heat = [row for row in binary if row["group"] == "Horstmann"]
    rmse = sqrt(fsum((row["law"]["value"] - row["observed"])**2 for row in heat) / len(heat))
    for passage, digits in (("transfer", 0), ("supplement", 0)):
        add(f"dea-binary-law-excess-enthalpy-rmse-{passage}", W_DEA_BINARY,
            "rows[Horstmann].law.value, observed: RMSE", f"{rmse:.{digits}f}")

    record = W_AMP_WITHOUT_HOT_REPLAY
    add("amp-without-hot-fitted-pressure-count-supplement", record, "replay.rows[loaded-pressure,Pa].count",
        str(sum(row["group"] == "loaded-pressure" and row["unit"] == "Pa" for row in read(record)["replay"]["rows"])))

    record = MOVE + "dea/reported/properties/summary.json.gz"
    rows = read(record)["rows"]
    for group, role, label, metrics in (
        ("Lal", "fitted", "lal-fitted-pressure", ("AARD_percent", "bias_percent")),
        ("Lal", "not fitted", "lal-low-pressure", ("AARD_percent", "bias_percent")),
        ("SeoHong", "not fitted", "seo-hong-pressure", ()),
        ("Lawson-VIII", "comparison only", "lawson-concentrated-pressure", ("AARD_percent", "bias_percent")),
        ("Bottinger-DEACOO", "comparison only", "bottinger-carbamate", ("AARD_percent", "bias_percent")),
        ("Bottinger-HCO3", "comparison only", "bottinger-bicarbonate", ("AARD_percent",)),
    ):
        cohort = [row for row in rows if (row["group"], row["role"]) == (group, role)]
        key = f"rows[{group}, {role}]"
        add(f"dea-{label}-count-methods", record, key + ".count", str(len(cohort)))
        if metrics:
            relative = [row for row in cohort if row["status"] == "Available" and row["observed"] != 0]
            summary = stats(relative, predicted="value")
            for metric in metrics:
                add(f"dea-{label}-{metric.split('_')[0].lower()}-transfer", record, key + ": " + metric,
                    f"{summary[metric]:{'+.1f' if metric == 'bias_percent' else '.1f'}}")
            if group == "Lawson-VIII":
                add("dea-lawson-concentrated-pressure-low-bias-limit", record,
                    key + ": -bias_percent", f"{-summary['bias_percent']:.1f}")

    record = MOVE + "dea/reported/fit/selection.json"
    for passage in ("methods", "supplement"):
        add(f"dea-tied-start-count-{passage}", record, "len(tied)", NUMBER_WORDS[len(read(record)["tied"])])

    for amine, name, cohorts in (
        ("dea", "DEA/property-comparisons/selected", (
            ("Carson", "carson-heat", "J/mol CO2", ("AARD_percent",)),
            ("Lawson", "lawson-fitted-pressure", "Pa", ("AARD_percent", "bias_percent")),
            ("SeoHong", "seo-hong-fitted-pressure", "Pa", ("AARD_percent", "bias_percent")),
            ("Lawson-394K", "lawson-hot-pressure", "Pa", ("AARD_percent", "bias_percent")),
        )),
        ("mdea", "MDEA/properties", (
            ("Ermatchkov", "ermatchkov-pressure", "Pa", ("bias_percent",)),
            ("Kuranov-413K", "kuranov-held-out-pressure", "Pa", ("AARD_percent",)),
            ("Xiao", "xiao-pressure", "Pa", ("AARD_percent", "bias_percent")),
            ("Sedighi", "sedighi-pressure", "Pa", ("AARD_percent",)),
            ("Carson", "carson-heat", "J/mol", ("AARD_percent",)),
            ("unloaded-density", "unloaded-density", "kg/m^3", ("AARD_percent",)),
            ("Jakobsen", "jakobsen-species-ratio", None, ("AARD_percent", "bias_percent")),
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
                    digits = 2 if label == "kundu-pressure" else 1
                    sign = "+" if metric == "bias_percent" else ""
                    add(f"{amine}-{label}-{metric.split('_')[0].lower()}-{passage}", record,
                        f"rows[{group},{unit or 'all units'}].value,observed: {metric}",
                        f"{summary[metric]:{sign}.{digits}f}")
            if label == "lawson-hot-pressure":
                for passage in ("methods", "transfer"):
                    add(f"dea-lawson-hot-pressure-row-count-{passage}", record,
                        "rows[Lawson-394K,Pa].count", NUMBER_WORDS[len(selected)])
        if amine == "mdea":
            low = [row["value"] / row["observed"] for row in rows if row["group"] == "Ermatchkov" and row["unit"] == "Pa"]
            add("mdea-ermatchkov-factor-low-count", record, "rows[Ermatchkov,Pa]: count value/observed < 1/1.5",
                str(sum(ratio < 1 / 1.5 for ratio in low)))
            add("mdea-ermatchkov-largest-low-factor", record, "rows[Ermatchkov,Pa]: 1/min(value/observed)",
                f"{1 / min(low):.1f}")
            sedighi = [(float(row["row"]["MDEA_wt_percent"]), float(row["row"]["alpha_mol_CO2_per_mol_MDEA"]),
                        row["value"] / row["observed"]) for row in rows if row["group"] == "Sedighi"]
            # "near a loading of 1 in 10 and 20 wt%" and "in 40 and 50 wt%" of the MDEA results paragraph
            for label, ratios in (("dilute", [r for w, a, r in sedighi if w <= 20 and a >= 0.89]),
                                  ("concentrated", [r for w, a, r in sedighi if w >= 40])):
                for end, value in (("minimum", min(ratios)), ("maximum", max(ratios))):
                    add(f"mdea-sedighi-{label}-pressure-ratio-{end}", record,
                        f"rows[Sedighi,{label}]: {end} value/observed", f"{value:.2g}")
            hot = [row for row in rows if row["group"] == "Kuranov" and row["outside_ranges"]["MDEA-dissociation"]]
            summary = stats(hot, predicted="value")
            for passage in ("results", "discussion"):
                for metric, fmt in (("AARD_percent", ".1f"), ("bias_percent", "+.1f")):
                    add(f"mdea-hot-fitted-pressure-{metric.split('_')[0].lower()}-{passage}", record,
                        f"rows[Kuranov,outside MDEA-dissociation].value,observed: {metric}", format(summary[metric], fmt))

    record = W_SALT
    salt = read(record)
    for formula, label, locations in (
        ("NaCl", "sodium-chloride", (("supplement", 2),)),
        ("NaHCO3", "sodium-bicarbonate", (("supplement", 2), ("theory", 1))),
        ("Na2CO3", "sodium-carbonate", (("supplement", 2), ("theory", 1), ("limits", 1))),
        ("mixed", "mixed-salts", (("supplement", 2),)),
    ):
        deltas = [100 * row["relative_error"] for row in salt["rows"][formula] if row.get("status") == "Available"]
        for passage, digits in locations:
            add(f"salt-{label}-osmotic-aard-{passage}", record, f"rows.{formula}[available].relative_error: AARD %",
                f"{fsum(map(abs, deltas)) / len(deltas):.{digits}f}")
        if formula in ("NaHCO3", "mixed"):
            for bound, reduce in (("minimum", min), ("maximum", max)):
                pass
    refused = sum(r.get("status") not in (None, "Available") for r in salt["rows"]["mixed"])
    for passage in ("theory", "refusal-description"):
        add(f"salt-mixed-unavailable-count-{passage}", record, "rows.mixed[status refused].count",
            NUMBER_WORDS[refused])
    for label, ion in (("bicarbonate", "bicarbonate-anion"), ("carbonate", "carbonate-anion")):
        law = salt["laws_at_record_reference"][ion]
        mantissa, exponent = f"{law['a1']:.3e}".split("e")
        add(f"salt-water-{label}-linear-slope", record, f"laws.{ion}.a1", f"{mantissa}e{int(exponent)}")
        add(f"salt-water-{label}-value-at-reference-temperature", record, f"laws.{ion}.a0", f"{law['a0']:.4f}")
        if label == "bicarbonate":
            for temperature, passage, digits in ((298.15, "original-intercept", 4), (353.15, "absorber-extrapolation", 3),
                                                 (393.15, "stripper-extrapolation", 3)):
                add(f"salt-water-bicarbonate-{passage}", record, f"laws.{ion} evaluated at {temperature} K",
                    f"{law['a0'] + law['a1'] * (temperature - law['t_ref']):.{digits}f}")

    coefficient = read(W_ABLATION)["bicarbonate"]
    for passage, digits in (("transfer", 3), ("supplement", 4)):
        add(f"mea-fitted-water-bicarbonate-interaction-{passage}", W_ABLATION, "bicarbonate",
            f"{coefficient:.{digits}f}")

    record = 'analyses/fixed_reaction_reference/results/MEA/A.json.gz'
    r = read(record)
    add('mea-jointly-fitted-parameter-count-abstract', record,
        'endpoint.coordinates.count',
        format((len(r["endpoint"]["coordinates"])), '.0f'))
    add('mea-jointly-fitted-parameter-count-conclusion', record,
        'endpoint.coordinates.count',
        format((len(r["endpoint"]["coordinates"])), '.0f'))
    add('mea-kiepe-pressure-count-methods', record,
        'replay.rows[Kiepe].count',
        format((sum(x["group"]=='Kiepe' for x in r["replay"]["rows"])), '.0f'))
    add('mea-cai-binary-observation-count-methods', record,
        'replay.rows[Cai].count',
        format((sum(x["group"]=='Cai' for x in r["replay"]["rows"])), '.0f'))
    add('mea-kiepe-constant-pressure-count-covariance', record,
        'replay.rows[Kiepe].count',
        format((sum(x["group"]=='Kiepe' for x in r["replay"]["rows"])), '.0f'))
    add('mea-jointly-fitted-parameter-count-methods', record,
        'endpoint.coordinates.count',
        NUMBER_WORDS[int(len(r["endpoint"]["coordinates"]))].capitalize())
    add('mea-jointly-fitted-parameter-count-results', record,
        'endpoint.coordinates.count',
        format((len(r["endpoint"]["coordinates"])), '.0f'))
    add('co2-water-cross-association-energy-supplement', record,
        'endpoint.parameters.topology.edges[carbon-dioxide,water].energy_over_k.value.magnitude',
        format((next(x['energy_over_k']["value"]["magnitude"] for x in r["endpoint"]["parameters"]["topology"]["edges"] if x["endpoint_a"]["component_id"]=='carbon-dioxide' and x["endpoint_b"]["component_id"]=='water')), '.3f'))
    add('mea-baygi-association-volume-converted', record,
        'endpoint.parameters.topology.edges[monoethanolamine,monoethanolamine].volume.value.magnitude',
        format((next(x['volume']["value"]["magnitude"] for x in r["endpoint"]["parameters"]["topology"]["edges"] if x["endpoint_a"]["component_id"]=='monoethanolamine' and x["endpoint_b"]["component_id"]=='monoethanolamine')), '.9f'))
    add('mea-kiepe-constant-pressure-count-supplement-covariance', record,
        'replay.rows[Kiepe].count',
        format((sum(x["group"]=='Kiepe' for x in r["replay"]["rows"])), '.0f'))
    add('mea-jointly-fitted-parameter-count-kiepe-derivatives', record,
        'endpoint.coordinates.count',
        format((len(r["endpoint"]["coordinates"])), '.0f'))
    add('mea-covariance-weighted-jacobian-rank', record,
        'diagnostics.uncertainty.conditional_correlation matrix rank over free coordinates',
        format((matrix_rank(r["diagnostics"]["uncertainty"]["conditional_correlation"])), '.0f'))
    add('mea-interior-coordinate-count-supplement', record,
        'fit coordinates or structural exclusions identified by conditional covariance',
        NUMBER_WORDS[int(len(r["diagnostics"]["uncertainty"]["free_coordinates"]))])
    add('mea-all-row-variance-supplement', record,
        'replay.rows: twice cost / (all rows minus free coordinates)',
        format((2 * fsum(x["cost"] for x in r["replay"]["rows"]) / (len(r["replay"]["rows"])-len(r["diagnostics"]["uncertainty"]["free_coordinates"]))), '.8f'))
    born = read(BORN)
    add('mea-born-objective-change', BORN, 'cases: largest |cost / reference_cost - 1| in percent',
        format(100 * max(abs(c['cost'] / born['reference_cost'] - 1) for c in born['cases']), '.2f'))
    for ion, digits in (('bicarbonate', '.1f'), ('carbonate', '.2f')):
        add(f'mea-born-{ion}-pressure-change', BORN, f'cases[ion={ion}-anion].largest_pressure_change_percent, largest',
            format(max(c['largest_pressure_change_percent'] for c in born['cases'] if c['ion'] == f'{ion}-anion'), digits))
    add('mea-fixed-hydroxide-born-diameter', record,
        'endpoint.parameters.components[hydroxide-anion].born_diameter in Å',
        format((next(c["value"]["magnitude"] for x in r["endpoint"]["parameters"]["components"] if x["component_id"]=='hydroxide-anion' for c in x["coefficients"] if c["family"]=='born_diameter')), '.4f'))
    add('dea-transferred-mea-carbamate-diameter', record,
        'endpoint.coordinates[component/carbamate-anion/segment_diameter].origin',
        format((next(x["origin"] for x in r["endpoint"]["coordinates"] if x["identity"]=='component/carbamate-anion/segment_diameter')), '.4f'))
    add('amp-transferred-mea-carbamate-water-interaction', record,
        'endpoint.coordinates[pair/carbamate-anion/water/k_ij].origin',
        format((next(x["origin"] for x in r["endpoint"]["coordinates"] if x["identity"]=='pair/carbamate-anion/water/k_ij')), '.6f'))
    add('amp-transferred-mea-carbamate-diameter-lower-bound', record,
        'endpoint.coordinates[component/carbamate-anion/segment_diameter].origin',
        format((next(x["origin"] for x in r["endpoint"]["coordinates"] if x["identity"]=='component/carbamate-anion/segment_diameter')), '.6f'))
    add('dea-carbamate-segment-volume-scaling', (record, 'analyses/fixed_reaction_reference/results/DEA/A.json.gz'),
        'MEA and DEA endpoint.parameters: cube root of the DEA/MEA neutral segment-volume ratio',
        format(((next(c["value"]["magnitude"] for x in read('analyses/fixed_reaction_reference/results/DEA/A.json.gz')["endpoint"]["parameters"]["components"] if x["component_id"]=='diethanolamine' for c in x["coefficients"] if c["family"]=='segment_count') / next(c["value"]["magnitude"] for x in r["endpoint"]["parameters"]["components"] if x["component_id"]=='monoethanolamine' for c in x["coefficients"] if c["family"]=='segment_count'))**(1/3) * next(c["value"]["magnitude"] for x in read('analyses/fixed_reaction_reference/results/DEA/A.json.gz')["endpoint"]["parameters"]["components"] if x["component_id"]=='diethanolamine' for c in x["coefficients"] if c["family"]=='segment_diameter') / next(c["value"]["magnitude"] for x in r["endpoint"]["parameters"]["components"] if x["component_id"]=='monoethanolamine' for c in x["coefficients"] if c["family"]=='segment_diameter')), '.4f'))

    record = STUDY + 'results/MEA/A.json.gz'
    r = read(record)
    add('mea-fitted-heat-cp-density-maximum-aard-rounded', record,
        'maximum AARD over fitted heat, Cp and density groups',
        f"{max(100*math.fsum(abs(x['value']/x['observed']-1) for x in r['replay']['rows'] if x['status']=='Available' and x['group']==g and x['unit']==u)/sum(x['status']=='Available' and x['group']==g and x['unit']==u for x in r['replay']['rows']) for g,u in [('common149','J/mol'),('Cp','J/(mol-feed K)'),('CO2-free density','kg/m^3'),('loaded density','kg/m^3')]):.1f}")
    add('mea-cai-bubble-temperature-rmse', record,
        'RMSE available Cai rows with unit K',
        f"{math.sqrt(math.fsum((x['value']-x['observed'])**2 for x in r['replay']['rows'] if x['group']=='Cai' and x['unit']=='K' and x['status']=='Available')/sum(x['group']=='Cai' and x['unit']=='K' and x['status']=='Available' for x in r['replay']['rows'])):.3f}")
    uncertainty = r['diagnostics']['uncertainty']
    ions = ('protonated-monoethanolamine', 'carbamate-anion')
    i, j = (uncertainty['free_coordinates'].index(f'component/{ion}/segment_diameter') for ion in ions)
    add('mea-ion-segment-diameter-conditional-correlation', record,
        'diagnostics.uncertainty.conditional_correlation: free coordinates for protonated MEA and carbamate segment diameters',
        f"{uncertainty['conditional_correlation'][i][j]:.3f}")

    record = 'analyses/fixed_reaction_reference/results/DEA/A.json.gz'
    r = read(record)
    add('dea-fitted-loaded-pressure-source-count-methods', record,
        'distinct replay.rows[Pa].group',
        NUMBER_WORDS[int(len({x["group"] for x in r["replay"]["rows"] if x["unit"]=="Pa"}))])
    add('dea-lawson-fitted-pressure-count-methods', record,
        'replay.rows[Lawson].count',
        format((sum(x["group"]=='Lawson' for x in r["replay"]["rows"])), '.0f'))
    add('dea-lal-fitted-pressure-count-methods', record,
        'replay.rows[Lal].count',
        format((sum(x["group"]=='Lal' for x in r["replay"]["rows"])), '.0f'))
    add('dea-cation-volume-equivalent-diameter', record,
        'endpoint.parameters.components[protonated-diethanolamine]: segment_diameter * segment_count**(1/3)',
        format((next(c['value']['magnitude'] for part in r['endpoint']['parameters']['components'] if part['component_id']=='protonated-diethanolamine' for c in part['coefficients'] if c['identity']=='component/protonated-diethanolamine/segment_diameter') * next(c['value']['magnitude'] for part in r['endpoint']['parameters']['components'] if part['component_id']=='protonated-diethanolamine' for c in part['coefficients'] if c['identity']=='component/protonated-diethanolamine/segment_count')**(1/3)), '.3f'))
    add('dea-hydrolysis-enthalpy-shift-transfer', (record, DEA_R4_SOURCE),
        'endpoint.reactions.aqueous[carbamate-hydrolysis].correlation.b minus the source R4 b, times -R',
        format((-8.31446261815324 * (next(x['correlation']['b'] for x in r['endpoint']['reactions']['aqueous'] if x['name']=='carbamate-hydrolysis') - source_r4(DEA_R4_SOURCE)['b'])), '.0f'))
    add('dea-reactive-fitted-parameter-count-methods', record,
        'endpoint.coordinates.count',
        NUMBER_WORDS[int(len(r["endpoint"]["coordinates"]))])
    add('dea-fitted-r4-log-constant-change-low-temperature', (record, DEA_R4_SOURCE),
        'endpoint carbamate-hydrolysis a,b minus source_law a,b at 298.15 K',
        format((next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["a"] - source_r4(DEA_R4_SOURCE)["a"] + (next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["b"] - source_r4(DEA_R4_SOURCE)["b"]) / 298.15), '+.3f'))
    add('dea-fitted-r4-log-constant-change-reference-temperature', (record, DEA_R4_SOURCE),
        'endpoint carbamate-hydrolysis a,b minus source_law a,b at 313.15 K',
        format((next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["a"] - source_r4(DEA_R4_SOURCE)["a"] + (next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["b"] - source_r4(DEA_R4_SOURCE)["b"]) / 313.15), '+.3f'))
    add('dea-fitted-r4-log-constant-change-high-temperature', (record, DEA_R4_SOURCE),
        'endpoint carbamate-hydrolysis a,b minus source_law a,b at 393.15 K',
        format((next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["a"] - source_r4(DEA_R4_SOURCE)["a"] + (next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["b"] - source_r4(DEA_R4_SOURCE)["b"]) / 393.15), '.3f'))
    add('dea-r4-log-constant-conditional-standard-error', record,
        'diagnostics.uncertainty.conditional_standard_error[hydrolysis-a]',
        format((FixedReference(read).conditional('DEA')["conditional_standard_error"]['hydrolysis-a']), '.3f'))
    add('dea-r4-log-constant-shift-discussion', (record, DEA_R4_SOURCE),
        'endpoint carbamate-hydrolysis a,b minus source_law a,b at reference temperature',
        format((next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["a"] - source_r4(DEA_R4_SOURCE)["a"] + (next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["b"] - source_r4(DEA_R4_SOURCE)["b"]) / 313.15), '+.3f'))
    add('dea-carbamate-water-r4-level-conditional-correlation-coefficients-discussion', record,
        'diagnostics.uncertainty.conditional_correlation[k-DEACOO-water,hydrolysis-a]',
        format((r["diagnostics"]["uncertainty"]["conditional_correlation"][r["diagnostics"]["uncertainty"]["free_coordinates"].index("k-DEACOO-water")][r["diagnostics"]["uncertainty"]["free_coordinates"].index("hydrolysis-a")]), '.3f'))
    add('dea-carbamate-water-r4-level-conditional-correlation-reactive-parameters-discussion', record,
        'diagnostics.uncertainty.conditional_correlation[k-DEACOO-water,hydrolysis-a]',
        format((r["diagnostics"]["uncertainty"]["conditional_correlation"][r["diagnostics"]["uncertainty"]["free_coordinates"].index("k-DEACOO-water")][r["diagnostics"]["uncertainty"]["free_coordinates"].index("hydrolysis-a")]), '.3f'))
    add('dea-carbamate-water-r4-level-conditional-correlation-supplement', record,
        'diagnostics.uncertainty.conditional_correlation[k-DEACOO-water,hydrolysis-a]',
        format((r["diagnostics"]["uncertainty"]["conditional_correlation"][r["diagnostics"]["uncertainty"]["free_coordinates"].index("k-DEACOO-water")][r["diagnostics"]["uncertainty"]["free_coordinates"].index("hydrolysis-a")]), '.3f'))
    add('dea-reactive-fitted-parameters-results', record,
        'fit coordinates or structural exclusions identified by conditional covariance',
        NUMBER_WORDS[int(len(r["endpoint"]["coordinates"]))])
    add('dea-conditional-stage-variance-supplement', record,
        'diagnostics.uncertainty and replay cost, conditional stage_variance',
        format((FixedReference(read).conditional('DEA')['stage_variance']), '.8f'))
    add('dea-conditional-dof-supplement', record,
        'diagnostics.uncertainty and replay cost, conditional dof',
        format((FixedReference(read).conditional('DEA')['dof']), '.0f'))

    record = 'analyses/fixed_reaction_reference/results/MDEA/A.json.gz'
    r = read(record)
    add('mdea-unloaded-density-count-methods', record,
        'replay.rows[unloaded-density].count',
        format((sum(x["group"]=='unloaded-density' for x in r["replay"]["rows"])), '.0f'))
    add('mdea-reactive-fitted-parameter-count-methods', record,
        'endpoint.coordinates.count',
        NUMBER_WORDS[int(len(r["endpoint"]["coordinates"]))])
    add('mdea-unloaded-density-count-supplement-weights', record,
        'replay.rows[unloaded-density].count',
        format((sum(x["group"]=='unloaded-density' for x in r["replay"]["rows"])), '.0f'))
    add('mdea-cation-water-interaction-results', record,
        "endpoint.coordinates [['protonated-methyldiethanolamine', 'water'] / k_ij].origin",
        format((next(x["origin"] for x in r["endpoint"]["coordinates"] if x["identity"]=="['protonated-methyldiethanolamine', 'water'] / k_ij")), '.4f'))
    add('mdea-cation-dispersion-energy-results', record,
        'endpoint.coordinates [protonated-methyldiethanolamine / dispersion_energy_over_k].origin',
        format((next(x["origin"] for x in r["endpoint"]["coordinates"] if x["identity"]=='protonated-methyldiethanolamine / dispersion_energy_over_k')), '.1f'))
    add('mdea-cation-dispersion-energy-conditional-se-results', record,
        'diagnostics.uncertainty.conditional_standard_error[protonated-methyldiethanolamine / dispersion_energy_over_k] rescaled by responsive-row variance from replay.rows',
        format((FixedReference(read).conditional("MDEA")["conditional_standard_error"]['protonated-methyldiethanolamine / dispersion_energy_over_k']), '.1f'))
    add('mdea-cation-water-and-dispersion-conditional-correlation-results', record,
        'diagnostics.uncertainty.conditional_correlation: cation-water interaction and cation dispersion energy',
        format((r["diagnostics"]["uncertainty"]["conditional_correlation"][r["diagnostics"]["uncertainty"]["free_coordinates"].index("['protonated-methyldiethanolamine', 'water'] / k_ij")][r["diagnostics"]["uncertainty"]["free_coordinates"].index("protonated-methyldiethanolamine / dispersion_energy_over_k")]), '+.4f'))
    add('mdea-cation-water-and-dispersion-conditional-correlation-covariance', record,
        'diagnostics.uncertainty.conditional_correlation: cation-water interaction and cation dispersion energy',
        format((r["diagnostics"]["uncertainty"]["conditional_correlation"][r["diagnostics"]["uncertainty"]["free_coordinates"].index("['protonated-methyldiethanolamine', 'water'] / k_ij")][r["diagnostics"]["uncertainty"]["free_coordinates"].index("protonated-methyldiethanolamine / dispersion_energy_over_k")]), '+.4f'))
    add('mdea-pure-water-pressures-constant-methods', record,
        'fit coordinates or structural exclusions identified by conditional covariance',
        NUMBER_WORDS[int(len(r["replay"]["rows"]) - FixedReference(read).conditional("MDEA")["responsive"])])
    add('mdea-pure-water-pressures-constant-supplement', record,
        'fit coordinates or structural exclusions identified by conditional covariance',
        NUMBER_WORDS[int(len(r["replay"]["rows"]) - FixedReference(read).conditional("MDEA")["responsive"])])

    amp_controls = read(W_AMP_CONTROLS)["rows"]
    for source, prefix, count_name in (
        ("hartono", "hartono-2021:", "amp-hartono-373-pressure-control-count-supplement"),
        ("tong", "tong-2012:", "amp-tong-measured-pressure-control-count-supplement"),
    ):
        cohort = [r for key, r in amp_controls.items() if key.startswith(prefix)]
        add(count_name, W_AMP_CONTROLS, f"len(rows[{prefix}])", NUMBER_WORDS[len(cohort)])
        add(f'amp-{source}-vapor-directed-controls-supplement', W_AMP_CONTROLS,
            f'rows[{prefix}, outcome L+V passed or vapor-directed].count',
            NUMBER_WORDS[sum(amp_vapor_outcome(r['outcome']) for r in cohort)])
    add('amp-reported-measured-pressure-control-vapor-directed-supplement', W_AMP_CONTROLS,
        'rows[outcome L+V passed or vapor-directed].count',
        NUMBER_WORDS[sum(amp_vapor_outcome(r['outcome']) for r in amp_controls.values())])
    for passage in ("supplement", "transfer", "abstract", "limits", "conclusion"):
        add(f'amp-reported-measured-pressure-control-no-descent-{passage}', W_AMP_CONTROLS,
            'rows[outcome no resolved descent].count',
            NUMBER_WORDS[sum(r['outcome'] == 'No resolved descent' for r in amp_controls.values())])
    liquid_vapor = 'L+V passed; L+L unresolved'
    for source, prefix, passages in (("hartono", "hartono-2021:", ("supplement",)), ("tong", "tong-2012:", ("supplement",)),
                                     ("reported", "", ("supplement", "transfer", "abstract", "limits", "conclusion"))):
        for passage in passages:
            add(f'amp-{source}-liquid-vapor-qualified-controls-{passage}', W_AMP_CONTROLS,
                f'rows[{prefix}, outcome {liquid_vapor}].count',
                NUMBER_WORDS[sum(r['outcome'] == liquid_vapor for key, r in amp_controls.items() if key.startswith(prefix))])
    changes, change_records = [], []
    for amine in ("mea", "dea", "amp"):
        kind = "pressure" if amine == "amp" else "partial_pressure"
        record = MOVE + f"{amine}/water-anion-control/properties/summary.json.gz"
        control = read(record)
        before, after = control["objective_before"], control["objective_after"]
        add(f"{amine}-water-anion-release-objective-supplement", record, "objective_before", f"{before:.4g}")
        add(f"{amine}-water-anion-release-objective-decrease-supplement", record,
            "objective_before - objective_after", f"{before - after:.2g}")
        for anion in ("bicarbonate", "carbonate"):
            released = control["parameters"][f"pair/{anion}-anion/water/k_ij/a0"]["after"]
            if released["bound"] is None:
                add(f"{amine}-water-{anion}-release-se-supplement", record,
                    f"parameters[pair/{anion}-anion/water/k_ij/a0].after.standard_error",
                    f"{released['standard_error']:.{3 if amine == 'amp' else 1}f}")
        fitted, = (e for e in control["loaded_pressure"] if e["role"] == "fitted" and e["kind"] == kind)
        add(f"{amine}-water-anion-release-fitted-aard-supplement", record,
            f"loaded_pressure[fitted,{kind}].rows.after: AARD",
            f"{stats([r['after'] for r in fitted['rows']], predicted='value')['AARD_percent']:.2f}")
        if amine == "amp":
            kundu, = (e for e in control["pressure"] if e["source"] == "kundu")
            for side, passages in (("before", ("supplement",)), ("after", ("supplement", "transfer"))):
                score = stats([r[side] for r in kundu["rows"]], predicted="value")["AARD_percent"]
                for passage in passages:
                    add(f"amp-water-anion-release-kundu-{side}-aard-{passage}", record,
                        f"pressure[kundu].rows.{side}: AARD", f"{score:.1f}")
        record = MOVE + f"{amine}/common-pressure-weight/properties/summary.json.gz"
        fitted, = (e for e in read(record)["loaded_pressure"] if e["role"] == "fitted" and e["kind"] == kind)
        scores = {side: stats([r[side] for r in fitted["rows"]], predicted="value")["AARD_percent"]
                  for side in ("before", "after")}
        for side, score in scores.items():
            add(f"{amine}-common-pressure-weight-{side}-aard-supplement", record,
                f"loaded_pressure[fitted,{kind}].rows.{side}: AARD", f"{score:.2f}")
        changes.append(abs(scores["after"] - scores["before"]))
        change_records.append(record)
    add("common-pressure-weight-maximum-aard-change-transfer", change_records,
        "max over MEA, DEA, AMP of |AARD after - AARD before| on loaded_pressure[fitted]", f"{max(changes):.1f}")
    record = MOVE + "mdea/water-anion-control/properties/summary.json.gz"
    control = read(record)
    before, after = control["objective_before"], control["objective_after"]
    add("mdea-water-anion-release-objective-supplement", record, "objective_before", f"{before:.5g}")
    add("mdea-water-anion-release-objective-decrease-supplement", record,
        "objective_before - objective_after", f"{before - after:.2g}")
    intercept = control["water_anion_intercepts"]["bicarbonate-anion"]
    for side in ("before", "after"):
        add(f"mdea-water-bicarbonate-release-intercept-{side}-supplement", record,
            f"water_anion_intercepts[bicarbonate-anion].a0_{side}", f"{intercept[f'a0_{side}']:.3f}")
    add("mdea-water-bicarbonate-release-se-supplement", record,
        "water_anion_intercepts[bicarbonate-anion].standard_error", f"{intercept['standard_error']:.3f}")
    for side in ("before", "after"):
        add(f"mdea-water-anion-release-ermatchkov-{side}-aard-supplement", record,
            f"pressure[Ermatchkov].{side}.AARD_percent",
            f"{next(e for e in control['pressure'] if e['source'] == 'Ermatchkov')[side]['AARD_percent']:.2f}")
    record = MOVE + "mdea/common-pressure-weight/properties/summary.json.gz"
    weighted = {e["source"]: e for e in read(record)["pressure"]}
    for source, group in (("kim", "Kim"), ("kuranov", "Kuranov"), ("ermatchkov", "Ermatchkov"), ("xiao", "Xiao")):
        for side in ("before", "after"):
            add(f"mdea-common-pressure-weight-{source}-{side}-aard-supplement", record,
                f"pressure[{group}].{side}.AARD_percent", f"{weighted[group][side]['AARD_percent']:.2f}")
    manifests = [MOVE + f"{amine}/common-pressure-weight/fit/manifest.json.gz" for amine in ("dea", "amp", "mdea")]
    scales = set()
    for manifest in manifests:
        rows = [r for r in read(manifest)["rows"]["fitted"] if r.get("unit") == "Pa"]
        for group in {r["group"] for r in rows}:
            weights = [r["weight"] for r in rows if r["group"] == group]
            scales.add(f"{1 / math.sqrt(len(weights) * weights[0]):.3g}")
    assert len(scales) == 1, scales
    add("common-pressure-weight-log-scale-supplement", manifests,
        "1 / sqrt(n * weight) for every fitted pressure group (DEA, AMP, MDEA)", scales.pop())
    add("mdea-reported-binary-pressure-log-scale-supplement", MOVE + "mdea/reported/fit/manifest.json.gz",
        "1 / sqrt(n * weight) for Kuranov-binary", f"{mdea_binary_pressure_scale(read(MOVE + 'mdea/reported/fit/manifest.json.gz')):g}")
    record = MOVE + "mdea/common-pressure-weight/fit/descent-probe.json.gz"
    probe = read(record)
    refused = [x for t in probe["trials"] for x in t["replay"]["rows"] if x["status"] != "Available"]
    assert {x["group"] for x in refused} == {"Kuranov-binary"} and len(refused) == len(probe["trials"]), refused
    add("mdea-common-pressure-weight-remaining-reduction-supplement", record,
        "relative_linearized_reduction * 100", f"{100 * probe['relative_linearized_reduction']:.1f}")
    add("mdea-common-pressure-weight-trial-steps-supplement", record, "len(trials)", NUMBER_WORDS[len(probe["trials"])])
    kuranov_rows = mdea_kuranov_rows(read(W_MDEA_PROPERTIES))
    records = (W_MDEA_PROPERTIES, KURANOV_DATA)
    add("mdea-published-kuranov-total-pressure-count", records, "matched Kuranov Table 2 rows.count",
        str(len(kuranov_rows)))
    add("mdea-published-kuranov-fitted-pressure-count", records, "matched Kuranov Table 2 rows[fitted].count",
        str(sum(row["role"] == "fitted" for row in kuranov_rows)))

    record = 'analyses/mea_parameter_bundle/results/engine-3e83e19c-association-volume/least-squares-declaration.json'
    r = read(record)
    add('mea-association-volume-conversion-temperature-count', record,
        'distinct observations[].T_K',
        format((len({x["T_K"] for x in r["observations"]})), '.0f'))

    record = W_SALT
    r = read(record)
    for group, name in (("NaCl", "sodium-chloride-fitted"), ("NaHCO3", "sodium-bicarbonate-fitted"),
                        ("Na2CO3", "sodium-carbonate-fitted"), ("mixed", "mixed-assessment-available")):
        count = r["scores"][group]["n"]
        add(f"salt-{name}-osmotic-row-count", record, f"scores[{group}].n",
            NUMBER_WORDS[count] if group == "NaCl" else str(count))
    for stage, ion, name in (("1a-sodium", "sodium-cation", "sodium"),
                             ("1c-carbonate", "carbonate-anion", "water-carbonate")):
        value = r["stages"][stage]["laws"][ion]["a0"]
        add(f"salt-{name}-intercept-at-lower-bound-supplement", record, f"stages[{stage}].laws[{ion}].a0",
            f"{value:.0f}")
    count = sum(len(stage["on_bound"]) for stage in r["stages"].values())
    for name in ("lower-bound-intercept-count-supplement", "interactions-on-lower-bounds-species-model",
                 "interactions-on-lower-bounds-limits"):
        add(f"salt-{name}", record, "stages[].on_bound.count", NUMBER_WORDS[count])

    record = 'analyses/fixed_reaction_reference/results/display-replays/caloric-and-species.json.gz'
    r = read(record)
    caloric_state = r["reference_state"]
    step, stencil_cp = min(zip(caloric_state["stencil_steps_K"], caloric_state["cp_stencil_J_mol_K"], strict=True))



    record = 'analyses/fixed_reaction_reference/results/DEA/property-comparisons/selected.json.gz'
    r = read(record)
    add('dea-weiland-density-assessment-count-transfer', record,
        'rows[Weiland].count',
        format((sum(x["group"]=="Weiland" for x in r["rows"])), '.0f'))
    add('dea-weiland-density-assessment-aard-transfer', record,
        'rows[Weiland].observed,value: AARD percent',
        format((stats([x for x in r["rows"] if x["group"]=="Weiland"],predicted="value")["AARD_percent"]), '.1f'))

    record = W_MDEA_BINARY
    r = read(record)
    add('mdea-binary-hull-compositions', record,
        'compositions',
        format((r["compositions"]), '.0f'))
    add('mdea-binary-hull-pressure', record,
        'pressure_Pa in MPa',
        format((r["pressure_Pa"] / 1e6), '.3f'))
    add('mdea-binary-hull-cold-no-gap-limit', record,
        'rows[lowest T_K].k_no_gap',
        format((min(r["rows"],key=lambda x:x["T_K"])["k_no_gap"]), '.4f'))
    add('mdea-binary-hull-hot-no-gap-limit', record,
        'rows[highest T_K].k_no_gap',
        format((max(r["rows"],key=lambda x:x["T_K"])["k_no_gap"]), '.4f'))

    for label, record in (("without-hot", W_AMP_WITHOUT_HOT_FIT), ("reported", MOVE + "amp/reported/fit/A.json.gz")):
        pair = next(x["coefficients"] for x in read(record)["endpoint"]["parameters"]["pairs"]
                    if (x["component_id_a"], x["component_id_b"]) == ("protonated-aminomethylpropanol", "water"))
        for T in (353.15, 393.15):
            add(f"amp-{label}-cation-water-interaction-{T:.0f}", record,
                f"endpoint.parameters.pairs[AMPH+,water].k_ij and slope at {T} K",
                f"{pair[0]['value']['magnitude'] + pair[1]['value']['magnitude'] * (1 / T - 1 / pair[1]['reference_temperature']['magnitude']):.3f}")


    record = 'analyses/fixed_reaction_reference/results/AMP_free/properties.json.gz'
    r = read(record)
    add('amp-reported-tong-total-pressure-aard-literature', record,
        'rows[tong,tong-baseline].observed,value',
        format((stats([x for x in r["rows"] if x["group"] in ("tong","tong-baseline")],predicted="value")["AARD_percent"]), '.2f'))
    for passage in ("literature", "note"):
        add(f'amp-assessment-tong-pressure-count-{passage}', record,
            'count rows[tong,tong-baseline]',
            format((sum(x["group"] in ("tong","tong-baseline") for x in r["rows"])), '.0f'))
    add('amp-kundu-comparison-partial-pressure-count', record,
        'rows[kundu].count',
        format((sum(x["group"]=="kundu" for x in r["rows"])), '.0f'))
    add('amp-reported-binary-bubble-pressure-fitted-aard', record,
        'rows[binary,Pa]: AARD percent',
        format((stats([x for x in r["rows"] if x["group"]=="binary" and x["unit"]=="Pa"],predicted="value")["AARD_percent"]), '.1f'))

    record = 'analyses/fixed_reaction_reference/results/AMP_free/A.json.gz'
    r = read(record)
    add('amp-reactive-fitted-parameter-count-methods', record,
        'endpoint.coordinates.count',
        NUMBER_WORDS[int(len(r["endpoint"]["coordinates"]))])
    add('amp-fitted-r4-log-constant-change-low-temperature', (record, AMP_R4_SOURCE),
        'endpoint carbamate-hydrolysis a,b minus source_law a,b at 298.15 K',
        format((next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["a"] - source_r4(AMP_R4_SOURCE)["a"] + (next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["b"] - source_r4(AMP_R4_SOURCE)["b"]) / 298.15), '.3f'))
    add('amp-fitted-r4-log-constant-change-reference-temperature', (record, AMP_R4_SOURCE),
        'endpoint carbamate-hydrolysis a,b minus source_law a,b at 313.15 K',
        format((next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["a"] - source_r4(AMP_R4_SOURCE)["a"] + (next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["b"] - source_r4(AMP_R4_SOURCE)["b"]) / 313.15), '.3f'))
    add('amp-fitted-r4-log-constant-change-high-temperature', (record, AMP_R4_SOURCE),
        'endpoint carbamate-hydrolysis a,b minus source_law a,b at 393.15 K',
        format((next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["a"] - source_r4(AMP_R4_SOURCE)["a"] + (next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["b"] - source_r4(AMP_R4_SOURCE)["b"]) / 393.15), '.3f'))
    add('amp-r4-log-constant-conditional-standard-error', record,
        'diagnostics.uncertainty.conditional_standard_error[AMP-hydrolysis-a]',
        format((FixedReference(read).conditional('AMP_free')["conditional_standard_error"]['AMP-hydrolysis-a']), '.3f'))
    add('amp-r4-log-constant-shift-discussion', (record, AMP_R4_SOURCE),
        'endpoint carbamate-hydrolysis a,b minus source_law a,b at reference temperature',
        format((next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["a"] - source_r4(AMP_R4_SOURCE)["a"] + (next(x["correlation"] for x in r["endpoint"]["reactions"]["aqueous"] if x["name"]=="carbamate-hydrolysis")["b"] - source_r4(AMP_R4_SOURCE)["b"]) / 313.15), '.3f'))
    add('dea-amp-uncertainty-log-constant-standard-error', record,
        'diagnostics.uncertainty.conditional_standard_error[AMP-hydrolysis-a]',
        format((FixedReference(read).conditional('AMP_free')["conditional_standard_error"]['AMP-hydrolysis-a']), '.3f'))
    add('amp-uncertainty-cation-water-slope-standard-error', record,
        'diagnostics.uncertainty.conditional_standard_error[AMPH-water reciprocal temperature slope]',
        format((FixedReference(read).conditional("AMP_free")["conditional_standard_error"]['AMPH-water-slope']), '.3f'))
    add('amp-conditional-stage-variance-supplement', record,
        'diagnostics.uncertainty and replay cost, conditional stage_variance',
        format((FixedReference(read).conditional('AMP_free')['stage_variance']), '.8f'))
    add('amp-conditional-dof-supplement', record,
        'diagnostics.uncertainty and replay cost, conditional dof',
        format((FixedReference(read).conditional('AMP_free')['dof']), '.0f'))

    record = MOVE + "amp/reported/fit/A.json.gz"
    slope = next(q["origin"] for q in read(record)["endpoint"]["coordinates"] if q["identity"] == "AMPH-water-slope")
    for name in ("amp-reported-fitted-slope-slope-comparison", "amp-uncertainty-cation-water-slope"):
        add(name, record, "endpoint.coordinates[AMPH-water-slope].origin", f"{slope:.3f}")

















    record = 'analyses/fixed_reaction_reference/results/display-replays/mea-comparisons.json.gz'
    r = read(record)
    add('mea-carbonate-share-observation-count-results', record,
        'carbonate_share.count',
        NUMBER_WORDS[int(len(r["carbonate_share"]))])
    add('mea-carbonate-share-observation-count-supplement-description', record,
        'carbonate_share.count',
        NUMBER_WORDS[int(len(r["carbonate_share"]))])
    add('mea-carbonate-share-minimum-calculated-to-observed-ratio', record,
        'carbonate_share[].value/observed: minimum',
        format((min(x["value"]/x["observed"] for x in r["carbonate_share"])), '.3f'))
    add('mea-weiland-outside-heat-capacity-count', record,
        'heat_capacity[Weiland1997].count',
        NUMBER_WORDS[int(sum(x["source"]=="Weiland1997" for x in r["heat_capacity"]))])
    add('mea-weiland-outside-heat-capacity-aard', record,
        'heat_capacity[Weiland1997].predicted_kJ_kg_K / observed_kJ_kg_K: AARD',
        format((100 * mean(abs(x["predicted_kJ_kg_K"]/x["observed_kJ_kg_K"]-1) for x in r["heat_capacity"] if x["source"]=="Weiland1997")), '.2f'))
    add('mea-heat-capacity-outside-weiland-concepcion-maximum-aard', record,
        'heat_capacity[Weiland1997 or Concepcion2023]: max source AARD percent',
        format((max(100 * mean(abs(x["predicted_kJ_kg_K"]/x["observed_kJ_kg_K"]-1) for x in r["heat_capacity"] if x["source"]==source) for source in ("Weiland1997","Concepcion2023"))), '.1f'))
    add('mea-carbonate-share-observations-figure-caption', record,
        'carbonate_share.count',
        NUMBER_WORDS[int(len(r["carbonate_share"]))])
    add('mea-stripper-density-count-transfer', record,
        'density[T_K >= 370, Available]: available count',
        format((len([x for x in r['density'] if float(x["row"]["T_K"])>=370 and x["status"]=="Available"])), '.0f'))
    add('mea-stripper-density-aard-transfer', record,
        'density[T_K >= 370, Available]: AARD percent',
        format((stats([x for x in r['density'] if float(x["row"]["T_K"])>=370 and x["status"]=="Available"], predicted="value")["AARD_percent"]), '.1f'))
    add('mea-stripper-heat-capacity-count-transfer', record,
        'heat_capacity[T_K >= 370, Available]: available count',
        format((len([x for x in r['heat_capacity'] if float(x["row"]["T_K"])>=370 and x["status"]=="Available"])), '.0f'))
    add('mea-stripper-heat-capacity-aard-transfer', record,
        'heat_capacity[T_K >= 370, Available]: AARD percent',
        format((stats([x for x in r['heat_capacity'] if float(x["row"]["T_K"])>=370 and x["status"]=="Available"], predicted="value")["AARD_percent"]), '.1f'))
    add('mea-kim-hot-inconsistent-tabulated-observation-count', record,
        'kim_2007 at 393.15 K: source_inconsistent count',
        NUMBER_WORDS[int(sum(float(x["T_K"])==393.15 and x["source_inconsistent"]=="True" for x in r["kim_2007"]))])










    temperatures_record = 'analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/evidence/F4/carbonate-share.csv'
    replay_record = STUDY + 'results/display-replays/mea-comparisons.json.gz'
    temperature_by_state = {row['id']: float(row['T_K']) for row in read(temperatures_record)}
    temperatures = [temperature_by_state[row['state']] for row in read(replay_record)['carbonate_share']]
    for bound, temperature in (('lower', 293.15), ('higher', 313.15)):
        add(f'mea-carbonate-share-observations-{bound}-temperature', (replay_record, temperatures_record),
            f'carbonate_share[].state joined to id; count where T_K={temperature}', NUMBER_WORDS[temperatures.count(temperature)])

    record = 'analyses/fixed_reaction_reference/results/MDEA/properties.json.gz'
    r = read(record)
    amine_sum = [
        format(stats([x for x in r["rows"] if x["group"] == group and x["observed"]
                      and x["status"] == "Available"], predicted="value")["AARD_percent"], ".2f")
        for group in ("Bottinger-amine-sum-5bar", "Bottinger-amine-sum-25bar")
    ]
    add('mdea-bottinger-amine-sum-aard-across-assigned-pressures', record,
        'rows[Bottinger-amine-sum at 5 and 25 bar]: per-pressure AARD at printed precision',
        '/'.join(dict.fromkeys(amine_sum)))

    record = 'analyses/mea_parameter_bundle/results/reaction-temperature-fit/candidate-targets.csv'
    r = read(record)
    add('mea-kim-prior-heat-intervals-fitted-313-k', record,
        'rows[key kim2007_t40_].count',
        NUMBER_WORDS[int(sum(row["family"]=="heat" and row["key"].startswith("kim2007_t40_") for row in r))])
    add('mea-kim-prior-heat-intervals-fitted-353-k', record,
        'rows[key kim2007_t80_].count',
        NUMBER_WORDS[int(sum(row["family"]=="heat" and row["key"].startswith("kim2007_t80_") for row in r))])

    record = MEA_REPORTED_PROPERTIES
    activity = read(record)
    pool = activity["carbonate_pool"]
    add("mea-reported-jakobsen-carbonate-pool-states", record, "len(carbonate_pool)", NUMBER_WORDS[len(pool)])
    share_states = {row["id"] for row in read(temperatures_record)}
    shared = [row for row in pool if row["identity"].split(":", 1)[0] in share_states]
    additional = [row for row in pool if row not in shared]
    if min(row["loading"] for row in additional) <= max(row["loading"] for row in shared):
        raise ValueError("The Jakobsen et al. carbonate-pool states outside the carbonate-share set no longer lie above its loadings")
    add("mea-jakobsen-carbonate-pool-share-states", (record, temperatures_record),
        "carbonate_pool[state id in carbonate-share.csv].count", count_word(len(shared)))
    add("mea-jakobsen-carbonate-pool-additional-states", (record, temperatures_record),
        "carbonate_pool[state id not in carbonate-share.csv].count", count_word(len(additional)))
    for label, select, precision in (("minimum", min, ".1e"), ("maximum", max, ".3f")):
        value = select(row["carbonate_pool_split"] for row in pool if row["available"])
        add(f"mea-reported-carbonate-pool-ratio-{label}", record,
            f"{label}(carbonate_pool[available].carbonate_pool_split)",
            prose_scientific(value, precision) if label == "minimum" else format(value, precision))
    for label, select, precision in (("minimum", min, ".3f"), ("maximum", max, ".2f")):
        add(f"mea-jakobsen-carbonate-pool-observation-{label}", record, f"{label}(carbonate_pool[].observed)",
            format(select(row["observed"] for row in pool), precision))
    activity_rows = activity["activity_rows"]
    for loading, field, name in ((0.05, "pH", "r2-ph-at-low-loading"),
                                 (0.50, "pH", "r2-ph-at-high-loading"),
                                 (0.30, "raw_R1_pH", "ph-r1-mole-fraction-at-intermediate-loading"),
                                 (0.30, "pH", "ph-r2-molality-at-intermediate-loading")):
        value, = (row[field] for row in activity_rows if row["loading"] == loading and row["symbol"] is None)


    record = 'analyses/fixed_reaction_reference/results/E/MEA/replay.json.gz'
    r = read(record)
    add('mea-canonical-pressure-source-count-residual-caption', record,
        'pressure_population: six canonical source identities',
        NUMBER_WORDS[int(len({x["source_key"] for x in r["pressure_population"].values() if x["source_key"] in ('Aronu2011', 'Hilliard2008', 'Idris2014', 'Jou1995', 'Mamun2005', 'Xu2011')}))])
    add('mea-absorber-unfitted-pressure-count', (record, 'analyses/fixed_reaction_reference/results/display-replays/wagner.json.gz'),
        'replay rows not fitted at nominal 30 wt% plus Wagner comparisons, absorber band',
        format((len(mea_absorber_pressures(r, read('analyses/fixed_reaction_reference/results/display-replays/wagner.json.gz')["rows"]))), '.0f'))
    for key in ('mea-absorber-unfitted-pressure-aard', 'mea-absorber-unfitted-pressure-aard-results'):
        add(key, (record, 'analyses/fixed_reaction_reference/results/display-replays/wagner.json.gz'),
            'replay rows not fitted at nominal 30 wt% plus Wagner comparisons, absorber band',
            format((stats(mea_absorber_pressures(r, read('analyses/fixed_reaction_reference/results/display-replays/wagner.json.gz')["rows"]),predicted="value")["AARD_percent"]), '.1f'))




    record = 'analyses/fixed_reaction_reference/results/display-replays/bubble-checks.json.gz'
    r = read(record)
    add('mea-bubble-verification-count-supplement', record,
        'rows: count',
        NUMBER_WORDS[int(len(r["rows"]))])

    binary = read(W_DEA_BINARY)["rows"]
    horstmann_n = sum(row["group"] == "Horstmann VLE" for row in binary)
    for passage in ("supplement", "transfer"):
        add(f"dea-horstmann-prior-binary-fit-count-{passage}", W_DEA_BINARY,
            "rows[Horstmann VLE].count", str(horstmann_n))
        add(f"dea-horstmann-measured-negative-excess-enthalpy-count-{passage}", W_DEA_BINARY,
            "rows[Horstmann, observed < 0].count",
            str(sum(row["group"] == "Horstmann" and row["observed"] < 0 for row in binary)))
    add("dea-cai-prior-binary-fit-count-supplement", W_DEA_BINARY, "rows[Cai, fitted beforehand].count",
        NUMBER_WORDS[sum(row["group"] == "Cai" and row["role"] == "fitted beforehand" for row in binary)])

    record = MEA_REPORTED_PROPERTIES
    for label, kind in (("temperatures", "temperature"), ("vapor-fractions", "mole_fraction")):
        add(f"mea-reported-cai-{label}-count", record, f"cai.{kind}.count", str(read(record)["cai"][kind]["count"]))

    record = 'analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/evidence/F4/states-excluded.json'
    r = read(record)
    add('mea-xu-pressure-rows-excluded-above-admitted-temperature', record,
        'canonical pressure rows excluded above 393.15 K',
        NUMBER_WORDS[int(len(r))].capitalize())





    record = 'analyses/round_5/results/B/reactions.json.gz'
    r = read(record)

    record = MOVE + "dea/reported/fit/manifest.json.gz"
    r = read(record)
    add('dea-lal-unloaded-feed-mass-fraction', (record, 'analyses/fixed_reaction_reference/results/DEA/A.json.gz'),
        'rows.fitted[Lal].states.problem.feed: unloaded DEA fraction by endpoint molar masses',
        format((dea_lal_unloaded_mass_fraction(r, read('analyses/fixed_reaction_reference/results/DEA/A.json.gz')["endpoint"]["parameters"]["components"])), '.4f'))

    record = 'analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/evidence/F4/selected-assessment/density-summary.json'
    r = read(record)
    add('mea-amundsen-source-conflict-density-count', record,
        'Amundsen source-conflict five.row_ids',
        NUMBER_WORDS[int(len(r["Amundsen source-conflict five"]["row_ids"]))].capitalize())

    record = 'analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/F4/uncertainty/standard-errors.csv'
    r = read(record)

    dea_fit = 'analyses/fixed_reaction_reference/results/DEA/A.json.gz'
    dea_fit_data = read(dea_fit)
    mdea_fit = 'analyses/fixed_reaction_reference/results/MDEA/A.json.gz'
    mdea_fit_data = read(mdea_fit)
    amp_fit = 'analyses/fixed_reaction_reference/results/AMP_free/A.json.gz'
    amp_fit_data = read(amp_fit)
    mea_fit = 'analyses/fixed_reaction_reference/results/MEA/A.json.gz'
    mea_fit_data = read(mea_fit)
    dea_properties = 'analyses/fixed_reaction_reference/results/DEA/property-comparisons/selected.json.gz'
    dea_properties_data = read(dea_properties)
    mdea_properties = 'analyses/fixed_reaction_reference/results/MDEA/properties.json.gz'
    mdea_properties_data = read(mdea_properties)
    add('dea-parameter-count-results-intro', dea_fit, 'len(endpoint.coordinates)', NUMBER_WORDS[len(dea_fit_data["endpoint"]["coordinates"])])
    add('mdea-parameter-count-results-intro', mdea_fit, 'len(endpoint.coordinates)', NUMBER_WORDS[len(mdea_fit_data["endpoint"]["coordinates"])])
    add('amp-parameter-count-results-intro', amp_fit, 'len(endpoint.coordinates)', NUMBER_WORDS[len(amp_fit_data["endpoint"]["coordinates"])])
    add('amp-parameter-count-bound-results', amp_fit, 'len(endpoint.coordinates)', NUMBER_WORDS[len(amp_fit_data["endpoint"]["coordinates"])])
    add('amp-active-bounds-results', amp_fit, 'len(diagnostics.active_bounds)', NUMBER_WORDS[len(amp_fit_data["diagnostics"]["active_bounds"])].capitalize())
    add('dea-carson-heats-results-intro', dea_fit, 'len(replay.rows[group=Carson])', str(sum(row["group"]=="Carson" for row in dea_fit_data["replay"]["rows"])))
    dea_pressure_sources = collections.Counter(row["group"] for row in dea_fit_data["replay"]["rows"] if row["unit"] == "Pa")
    add('dea-pressure-source-count-fit-results', dea_fit, 'len(distinct replay.rows[unit=Pa].group)', NUMBER_WORDS[len(dea_pressure_sources)])
    add('dea-pressure-source-count-limitations', dea_fit, 'len(distinct replay.rows[unit=Pa].group)', NUMBER_WORDS[len(dea_pressure_sources)])
    add('dea-lawson-pressure-count-fit-results', dea_fit, 'len(replay.rows[unit=Pa,group=Lawson])', str(dea_pressure_sources['Lawson']))
    add('dea-lal-pressure-count-fit-results', dea_fit, 'len(replay.rows[unit=Pa,group=Lal])', str(dea_pressure_sources['Lal']))
    add('dea-lawson-pressure-count-methane-sensitivity', dea_fit, 'len(replay.rows[unit=Pa,group=Lawson])', str(dea_pressure_sources['Lawson']))
    add('dea-negative-horstmann-assessment-count', dea_properties, 'len(rows[Horstmann,observed<0])', str(sum(row["group"]=="Horstmann" and row["observed"]<0 for row in dea_properties_data["rows"])))
    dea_r4 = DEA_R4_SOURCE
    dea_r4_data = source_r4(dea_r4)
    dea_r4_delta = {key: next(r["correlation"][key] for r in dea_fit_data["endpoint"]["reactions"]["aqueous"] if r["name"]=="carbamate-hydrolysis") - dea_r4_data[key] for key in ("a", "b")}
    amp_r4 = AMP_R4_SOURCE
    amp_r4_data = source_r4(amp_r4)
    amp_r4_delta = {key: next(r["correlation"][key] for r in amp_fit_data["endpoint"]["reactions"]["aqueous"] if r["name"]=="carbamate-hydrolysis") - amp_r4_data[key] for key in ("a", "b")}
    dea_r4_se = FixedReference(read).conditional("DEA")["conditional_standard_error"]
    amp_r4_se = FixedReference(read).conditional("AMP_free")["conditional_standard_error"]
    r4_factor = math.exp(dea_r4_delta["a"] + dea_r4_delta["b"] / 313.15)
    add("dea-r4-equilibrium-factor-at-313-results", (dea_fit, dea_r4),
        "exp(endpoint R4 minus source_law at 313.15 K)", f"{r4_factor:.3f}")
    add("dea-reciprocal-r4-equilibrium-factor-discussion", (dea_fit, dea_r4),
        "1 / exp(endpoint R4 minus source_law at 313.15 K)", f"{1 / r4_factor:.0f}")
    add('dea-r4-change-at-313-results', (dea_fit, dea_r4), 'endpoint R4 a,b minus source_law a,b at 313.15 K', format(dea_r4_delta["a"] + dea_r4_delta["b"]/313.15, '+.3f'))
    add('dea-r4-log-shift-standard-error-results', dea_fit, 'conditional SE of hydrolysis-a at the response-adjusted variance', format(dea_r4_se["hydrolysis-a"], '.3f'))
    add('dea-r4-enthalpy-standard-error-results', dea_fit, 'response-adjusted conditional SE of hydrolysis-enthalpy-shift in J/mol', format(dea_r4_se["hydrolysis-enthalpy-shift"], '.0f'))
    add('dea-r4-change-at-393-results', (dea_fit, dea_r4), 'endpoint R4 a,b minus source_law a,b at 393.15 K', format(dea_r4_delta["a"] + dea_r4_delta["b"]/393.15, '.3f'))
    base = MOVE + "dea/without-lawson/"
    record = base + "properties/summary.json.gz"
    rows = read(record)["rows"]
    for group, role, label in (("Lal", "fitted", "lal"), ("Carson", "fitted", "carson"), ("Lawson", "not fitted", "lawson")):
        score = stats([r for r in rows if r["group"] == group and r["role"] == role], predicted="value")
        add(f"dea-without-lawson-{label}-aard-supplement", record, f"rows[{group},{role}]: AARD", f"{score['AARD_percent']:.1f}")
        add(f"dea-without-lawson-{label}-bias-transfer", record, f"rows[{group},{role}]: bias", f"{score['bias_percent']:.1f}")
    record = base + "fit/A.json.gz"
    without = read(record)
    law = next(r["correlation"] for r in without["endpoint"]["reactions"]["aqueous"] if r["name"] == "carbamate-hydrolysis")
    add("dea-without-lawson-r4-change-at-313-transfer", (record, dea_r4), "endpoint R4 a,b minus source_law a,b at 313.15 K",
        format(law["a"] - dea_r4_data["a"] + (law["b"] - dea_r4_data["b"]) / 313.15, "+.2f"))
    add("dea-without-lawson-r4-standard-error-transfer", record,
        "diagnostics.uncertainty.conditional_standard_error[hydrolysis-a]",
        format(without["diagnostics"]["uncertainty"]["conditional_standard_error"]["hydrolysis-a"], ".2f"))
    record = base + "phase/declared.json.gz"
    phase = read(record)
    without_states = {row["key"] for row in distinct_phase_rows(phase)}
    split = str(sum(confirmed_split(c) for c in phase["classifications"] if c["key"] in without_states))
    for place in ("transfer", "supplement"):
        add(f"dea-without-lawson-split-states-{place}", record, "classifications[distinct rows, confirmed split].count", split)
        add(f"dea-without-lawson-searched-states-{place}", record, "len(distinct rows)", str(len(without_states)))
    record = MOVE + "dea/reported/held-out-pressures/summary.json.gz"
    held = read(record)["sources"]
    for name, label in (("HajiSulaiman1998", "hajisulaiman"), ("Lee1972", "lee"), ("KennardMeisen1984", "kennard")):
        score = stats([r for r in held[name]["rows"] if r.get("value") is not None], predicted="value")
        add(f"dea-held-out-{label}-count-transfer", record, f"sources.{name}.rows[value]: count", str(score["n"]))
        if score["n"] < len(NUMBER_WORDS):
            add(f"dea-held-out-{label}-count-words-transfer", record, f"sources.{name}.rows[value]: count", count_word(score["n"]))
        add(f"dea-held-out-{label}-aard-transfer", record, f"sources.{name}.rows[value]: AARD", f"{score['AARD_percent']:.1f}")
        add(f"dea-held-out-{label}-bias-transfer", record, f"sources.{name}.rows[value]: bias", f"{score['bias_percent']:.1f}")
    amp_log_change = amp_r4_delta["a"] + amp_r4_delta["b"]/313.15
    add('amp-r4-log-decrease-at-313-results', (amp_fit, amp_r4), 'negative of endpoint R4 a,b change from source_law at 313.15 K', format(-amp_log_change, '.3f'))
    add('amp-r4-log-shift-standard-error-results', amp_fit, 'response-adjusted conditional SE of AMP-hydrolysis-a', format(amp_r4_se["AMP-hydrolysis-a"], '.3f'))
    add('amp-r4-equilibrium-factor-at-313-results', (amp_fit, amp_r4), 'exp(endpoint R4 a,b change from source_law at 313.15 K)', format(math.exp(amp_log_change), '.3f'))
    add('amp-reciprocal-r4-equilibrium-factor-discussion', (amp_fit, amp_r4), 'exp(negative R4 log shift from source_law at 313.15 K), rounded to a whole number', NUMBER_WORDS[round(math.exp(-amp_log_change))])
    add('amp-cation-water-slope-results', amp_fit, 'endpoint.coordinates[AMPH-water-slope].origin', format(next(q["origin"] for q in amp_fit_data["endpoint"]["coordinates"] if q["identity"]=="AMPH-water-slope"), '.3f'))
    add('amp-cation-water-slope-standard-error-results', amp_fit, 'response-adjusted conditional SE of AMPH-water-slope', format(amp_r4_se["AMPH-water-slope"], '.3f'))
    add('mdea-cation-water-conditional-se-results', mdea_fit, 'conditional SE [protonated-methyldiethanolamine, water]/k_ij scaled to responsive-row variance', format(FixedReference(read).conditional("MDEA")["conditional_standard_error"][str(["protonated-methyldiethanolamine","water"])+" / k_ij"], '.4f'))
    add('mea-carbamate-water-interaction-transferred-amp-results', values['amp-transferred-mea-carbamate-water-interaction']['record'], values['amp-transferred-mea-carbamate-water-interaction']['key'], values['amp-transferred-mea-carbamate-water-interaction']['value'])
    add('mdea-kuranov-fit-outside-r5-count-results', mdea_properties, 'rows[Kuranov,fitted,outside_ranges.MDEA-dissociation=true].count', str(sum(q["group"]=="Kuranov" and q["role"]=="fitted" and q["outside_ranges"]["MDEA-dissociation"] is True for q in mdea_properties_data["rows"])))
    add('mdea-kuranov-hot-assessment-count-results', mdea_properties, 'rows[Kuranov-413K,not fitted].count', str(sum(q["group"]=="Kuranov-413K" and q["role"]!="fitted" for q in mdea_properties_data["rows"])))
    for quantity, rows in (("states", [r for r in mdea_grid if r["available"]]),
                           ("unsearched-states", [r for r in mdea_grid if not r["available"]]),
                           ("requested-states", mdea_grid)):
        add("mdea-restricted-grid-" + quantity, W_MDEA_SCREEN, f"rows[restricted grid].{quantity}.count", str(len(rows)))
    add("mdea-zheng-row-6-bubble-pressure", W_MDEA_PROPERTIES, "zheng_row_6.cold.pressure / 1e6",
        f"{read(W_MDEA_PROPERTIES)['zheng_row_6']['cold']['pressure'] / 1e6:.1f}")
    add('mdea-kamps-comparison-count-results', W_MDEA_PROPERTIES, 'kamps.full_rows', str(kamps["full_rows"]))
    add('mdea-kamps-same-row-count-results', W_MDEA_PROPERTIES, 'kamps.full_rows', str(kamps["full_rows"]))
    add('mdea-kamps-additional-row-ordinal-results', W_MDEA_PROPERTIES, 'kamps.common_rows + one additional row', str(kamps["common_rows"]+1))
    add('mdea-kuranov-source-matched-count-literature-results', (W_MDEA_PROPERTIES, KURANOV_DATA), 'matched Kuranov Table 2 rows.count', str(len(mdea_kuranov_rows(read(W_MDEA_PROPERTIES)))))
    dea_methane = MOVE + "dea/reported/properties/lawson-methane.json.gz"
    dea_methane_data = read(dea_methane)
    add('dea-largest-lawson-methane-pressure-change', dea_methane, 'maximum |pCO2_change_Pa| / 1e6', format(max(abs(change) for q in dea_methane_data["rows"] for change in q["pCO2_change_Pa"])/1e6, '.3f'))
    increases = [100 * math.expm1(max(q["node_log_corrections"])) for q in dea_methane_data["rows"]]
    for passage in ("limitations", "supplement"):
        add(f'dea-lawson-methane-row-count-{passage}', dea_methane, 'len(rows)', str(len(increases)))
        for name, value in (("minimum", min(increases)), ("maximum", max(increases))):
            add(f'dea-lawson-methane-{name}-pressure-increase-{passage}', dea_methane,
                f'{name} over rows of 100 (exp(max node_log_corrections) - 1)', f'{value:.1f}')
    earlier = "analyses/amines/results/dea/reported/"
    record = earlier + "fit/manifest.json.gz"
    earlier_fit = read(record)
    groups = collections.Counter(row["group"] for row in earlier_fit["rows"]["fitted"])
    add('dea-earlier-fit-fitted-observation-count-supplement', record, 'len(rows.fitted)',
        str(len(earlier_fit["rows"]["fitted"])))
    for group in ("SeoHong", "Lal"):
        add(f'dea-earlier-fit-{group.lower()}-count-supplement', record, f'rows.fitted[{group}].count', str(groups[group]))
    add('dea-earlier-fit-coordinate-count-supplement', record, 'len(coordinate_order)',
        NUMBER_WORDS[len(earlier_fit["coordinate_order"])])
    record = earlier + "phase/rebuild-441/declared/summary.json.gz"
    tally = read(record)["tally"]
    add('dea-earlier-fit-searched-states-supplement', record, 'tally.states', str(tally["states"]))
    add('dea-earlier-fit-descent-states-supplement', record, 'tally.descent', NUMBER_WORDS[tally["descent"]])
    record = earlier + "phase/diagnosis/assemblages.json.gz"
    splits = [row["feed"][0] for row in read(record)["dea"]
              if row["key"] == "weiland-1998:32:problem" and row["physical_checks_pass"]]
    for name, value in (("minimum", min(splits)), ("maximum", max(splits))):
        add(f'dea-earlier-fit-split-{name}-loading-supplement', record,
            f'{name} feed[CO2]/feed[DEA] over dea[weiland-1998:32:problem, physical_checks_pass]', f'{value:.2f}')
    add('mea-active-interactions-count-results', mea_fit, 'len(diagnostics.active_bounds)', NUMBER_WORDS[len(mea_fit_data["diagnostics"]["active_bounds"])].capitalize())
    mea_coordinates = {row['identity']: row['origin'] for row in mea_fit_data['endpoint']['coordinates']}
    for end, identity in (
        ('lower', 'pair/carbamate-anion/protonated-monoethanolamine/k_ij'),
        ('upper', 'pair/bicarbonate-anion/protonated-monoethanolamine/k_ij'),
    ):
        add(f'mea-active-interaction-{end}-value-results', mea_fit, f'endpoint.coordinates[{identity}].origin',
            f'{mea_coordinates[identity]:+.0f}')
    identity = 'pair/bicarbonate-anion/protonated-monoethanolamine/k_ij'
    mea_canonical = 'analyses/fixed_reaction_reference/results/E/MEA/replay.json.gz'
    mea_canonical_data = read(mea_canonical)
    add('mea-canonical-observation-source-count-results', mea_canonical, 'len(distinct pressure_population[].source_key)', NUMBER_WORDS[len({q["source_key"] for q in mea_canonical_data["pressure_population"].values()})])
    add('mea-canonical-observation-source-count-caption', mea_canonical, 'len(distinct pressure_population[].source_key)', NUMBER_WORDS[len({q["source_key"] for q in mea_canonical_data["pressure_population"].values()})])
    mea_comparisons = 'analyses/fixed_reaction_reference/results/display-replays/mea-comparisons.json.gz'
    mea_comparisons_data = read(mea_comparisons)
    add('mea-kim-hot-flagged-interval-count-results', mea_comparisons, 'kim_2007[393.15 K,source_inconsistent or first_120].count', NUMBER_WORDS[sum(float(q["T_K"])==393.15 and "True" in (q["source_inconsistent"],q["first_120"]) for q in mea_comparisons_data["kim_2007"])])
    mdea_cation = next(q for q in mdea_fit_data["endpoint"]["parameters"]["components"] if q["component_id"]=="protonated-methyldiethanolamine")
    mdea_segment = {q["family"]: q["value"]["magnitude"] for q in mdea_cation["coefficients"]}
    add('mdea-cation-segment-diameter-equation', mdea_fit, 'endpoint.parameters.components[protonated-methyldiethanolamine].segment_diameter', format(mdea_segment["segment_diameter"], '.3f'))
    add('mdea-cation-volume-equivalent-diameter-equation', mdea_fit, 'MDEA cation segment_diameter times segment_count^(1/3)', format(mdea_segment["segment_diameter"] * mdea_segment["segment_count"]**(1/3), '.3f'))
    phase_summary = 'analyses/amines/results/shared/phase/display-summary.json.gz'
    phase_summary_data = read(phase_summary)
    mdea_fit = 'analyses/fixed_reaction_reference/results/MDEA/A.json.gz'
    mdea_fit_data = read(mdea_fit)
    mea_fit = 'analyses/fixed_reaction_reference/results/MEA/A.json.gz'
    mea_fit_data = read(mea_fit)
    mdea_properties = 'analyses/fixed_reaction_reference/results/MDEA/properties.json.gz'
    mdea_properties_data = read(mdea_properties)
    mea_comparisons = 'analyses/fixed_reaction_reference/results/display-replays/mea-comparisons.json.gz'
    mea_comparisons_data = read(mea_comparisons)
    add('mea-carbonate-share-maximum-calculated-to-observed-ratio', mea_comparisons, 'max(carbonate_share[].value / observed)', format(max(q["value"]/q["observed"] for q in mea_comparisons_data["carbonate_share"]), '.3f'))
    add('mea-carbonate-share-geometric-mean-detailed-supplement', mea_comparisons, 'exp(mean(log(carbonate_share[].value / observed)))', format(math.exp(mean(math.log(q["value"]/q["observed"]) for q in mea_comparisons_data["carbonate_share"])), '.4f'))
    add('mdea-bottinger-bicarbonate-aard-five-bar', mdea_properties, 'rows[Bottinger-bicarbonate-5bar,value,observed].AARD percent', format(stats([q for q in mdea_properties_data["rows"] if q["group"]=="Bottinger-bicarbonate-5bar" and q["observed"] and q["status"]=="Available"],predicted="value")["AARD_percent"], '.2f'))
    add('mdea-bottinger-bicarbonate-aard-twenty-five-bar', mdea_properties, 'rows[Bottinger-bicarbonate-25bar,value,observed].AARD percent', format(stats([q for q in mdea_properties_data["rows"] if q["group"]=="Bottinger-bicarbonate-25bar" and q["observed"] and q["status"]=="Available"],predicted="value")["AARD_percent"], '.2f'))
    kiepe_derivative = max(abs(v) for q,j in zip(mea_fit_data["replay"]["rows"], mea_fit_data["diagnostics"]["jacobian_bound_normalized"], strict=True) if q["group"]=="Kiepe" for v in j)
    add('mea-kiepe-zero-derivative-value', mea_fit, 'max(abs(diagnostics.jacobian_bound_normalized[rows group=Kiepe]))', count_word(0, zero="zero") if kiepe_derivative == 0 else prose_scientific(kiepe_derivative, ".2e"))
    add('mea-single-liquid-census-parents-supplement', mea_census, 'rows[passed-single-liquid].count', str(census_classes["passed-single-liquid"]))
    descent_sources = collections.Counter(row["source"]["source_key"] for row in states)
    for label, source in (("sobrino", "Sobrino2016"), ("bottinger", "BottingerMDEA2008"),
                          ("zheng", "Zheng2020"), ("merkley", "Merkley1987")):
        count = descent_sources[source]
        add(f"mdea-distinct-descents-{label}-supplement", (W_MDEA_SCREEN, W_MDEA_PROPERTIES),
            f"classifications joined to measured rows with source_key={source}",
            str(count) if label == "bottinger" else count_word(count, zero="zero"))
    add("mdea-distinct-descents-sobrino-transfer", (W_MDEA_SCREEN, W_MDEA_PROPERTIES),
        "classifications joined to measured rows with source_key=Sobrino2016",
        count_word(descent_sources["Sobrino2016"], zero="zero"))
    add('mdea-source-matched-kuranov-count-supplement', (W_MDEA_PROPERTIES, KURANOV_DATA), 'matched Kuranov Table 2 rows.count', str(len(mdea_kuranov_rows(read(W_MDEA_PROPERTIES)))))
    add('mdea-source-matched-kuranov-free-fitted-count', W_MDEA_PROPERTIES, 'fitted Kuranov-binary record count', NUMBER_WORDS[sum(q["role"]=="fitted" and q["group"]=="Kuranov-binary" for q in mdea_properties_data["rows"])])

    salt_replay = 'analyses/mea_parameter_bundle/results/salt-anchored-435/salt/summary.json'
    salt_replay_data = read(salt_replay)
    carbonate_residuals = collections.defaultdict(list)
    for row in salt_replay_data["result"]["rows"]["Na2CO3"]:
        if row["m"] < 0.4:
            carbonate_residuals[row["m"]].append(100 * row["relative_error"])
    amp_hot = 'analyses/round_3/results/q2.json'
    amp_hot_data = read(amp_hot)
    amp_hot_descents, = {q["fixed_pressure_outcomes"]["resolved descent"] for q in amp_hot_data["scores"].values()}
    amp_assessed = 'analyses/fixed_reaction_reference/results/AMP_free/properties.json.gz'
    amp_assessed_data = read(amp_assessed)
    add('amp-unfitted-kundu-partial-pressure-count', amp_assessed, 'rows[group=kundu,role=not fitted] count', str(sum(q["group"]=="kundu" and q["role"]=="not fitted" for q in amp_assessed_data["rows"])))
    add('mdea-sobrino-example-bubble-pressure-transfer', W_MDEA_PROPERTIES, 'mdea_bubble[fit:218:problem].bubble_Pa / 1e6',
        format(read(W_MDEA_PROPERTIES)["mdea_bubble"]["fit:218:problem"]["bubble_Pa"]/1e6, '.2f'))



    dea_binary_fit = 'analyses/amines/results/dea/binary-temperature-dependent/fit-inputs/inputs.json'
    water_dea = next(pair for pair in dea_fit_data["endpoint"]["parameters"]["pairs"]
                     if {pair["component_id_a"], pair["component_id_b"]} == {"water", "diethanolamine"})
    coefficients = {row["family"]: row["value"]["magnitude"] for row in water_dea["coefficients"]}
    for term, label, places in (("k_ij", "reference", 4), ("k_ij_reciprocal_temperature_slope", "slope", 2)):
        add(f"dea-water-interaction-{label}-results", dea_fit, f"endpoint.parameters.pairs[DEA,water].{term}",
            f"{coefficients[term]:.{places}f}")
    for amine, design, component in (
        ('dea', 'DEA', 'diethanolamine'), ('mdea', 'MDEA', 'methyldiethanolamine'),
        ('amp', 'AMP_free', 'aminomethylpropanol'),
    ):
        endpoint_path = STUDY + f'results/{design}/A.json.gz'
        endpoint = read(endpoint_path)['endpoint']
        adjusted = len(endpoint['coordinates'])
        selected = next(q for q in endpoint['parameters']['components'] if q['component_id'] == component)
        adjusted += sum(q['family'].startswith('dielectric_') for q in selected['coefficients'])
        records = [endpoint_path]
        if amine == 'dea':
            adjusted += len(read(dea_binary_fit)['binary'].keys() & {'a', 'b_K'})
            records.append(dea_binary_fit)
        elif amine == 'amp':
            adjusted += amp_pure_coordinate_count()
            records.append(AMP_PURE_INPUT)
        add(f'{amine}-adjusted-coordinate-count-across-stages', records,
            'endpoint.coordinates plus neutral fitted dielectric coefficients and prior binary or pure fit coordinates',
            str(adjusted))

    for amine, record, endpoint_record in (("dea", W_DEA_SCREEN, dea_fit),
                                            ("amp", MOVE + "amp/reported/phase/supplied.json.gz", amp_fit)):
        grid_keys = [row["key"][len("grid:"):] for row in read(record)["rows"] if row["key"].startswith("grid:")]
        stocks, temperatures, loadings, _ = zip(*(key.rsplit(":", 3) for key in grid_keys), strict=True)
        axes = dict(stocks=NUMBER_WORDS[len(set(stocks))], loadings=str(len(set(loadings))),
                    temperatures=NUMBER_WORDS[len(set(temperatures))],
                    maximum_loading=f"{max(map(float, loadings)):.3f}")
        for axis, value in axes.items():
            add(f'{amine}-reported-grid-{axis.replace("_", "-")}-supplement', record,
                f'distinct grid keys: {axis}', value)
        if amine == "amp":
            components = read(endpoint_record)["endpoint"]["parameters"]["components"]
            masses = {q["component_id"]: q["fixed"]["molar_mass"]["value"]["magnitude"] for q in components}
            weights = []
            for stock in map(literal_eval, set(stocks)):
                total = fsum(n * masses[species] for species, n in stock.items())
                weights.append(100 * stock["aminomethylpropanol"] * masses["aminomethylpropanol"] / total)
            for bound, reduce in (("minimum", min), ("maximum", max)):
                add(f"amp-reported-grid-{bound}-stock-supplement", (record, endpoint_record),
                    f"{bound}(grid stock weight percentages)", f"{reduce(weights):.1f}")

    for passage in ("methods", "theory"):
        add(f"amp-pure-adjusted-coordinate-count-{passage}", AMP_PURE_INPUT,
            "adopted pure AMP segment and association coefficients.count", NUMBER_WORDS[amp_pure_coordinate_count()])
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

    # TeX terminates a control word at the digit in expressions such as \pm0.390.
    def mask_control(match):
        return " " * len(match[0])

    numeric_text = re.sub(r"\\pm(?=[+\-\d.])", mask_control, text)
    masked = re.sub(r"\\pm(?=[+\-\d.])", mask_control, masked)
    for match in SCIENTIFIC.finditer(numeric_text):
        if masked[match.start():match.end("base")].strip():
            yield match, Decimal(match["mantissa"] or "1").scaleb(int(match["exponent"]))
            masked = masked[:match.start()] + " " * len(match[0]) + masked[match.end():]
    for match in NUMERAL.finditer(masked):
        # An f-string can hold only the base of a power before its exponent interpolation.
        value = Decimal(match[0])
        if value == 10 and text[match.end():] == "^{":
            continue
        yield match, value


def collision_contexts(text, excerpt):
    start = r"(?<!\w)" if excerpt and excerpt[0].isalnum() else ""
    return re.finditer(start + re.escape(excerpt), text)


def display_literals(path):
    import ast

    source = path.read_text()
    lines = source.splitlines()
    tree = ast.parse(source)
    locators = {
        node for call in ast.walk(tree)
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
        and call.func.id == "add" and len(call.args) == 4
        for argument in call.args[:3] for node in ast.walk(argument)
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.FormattedValue) and node.format_spec is not None:
            locators.update(ast.walk(node.format_spec))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "re":
                locators.update(part for argument in node.args[:1] for part in ast.walk(argument))
        if (isinstance(node, ast.Compare) and isinstance(node.left, ast.Subscript)
                and isinstance(node.left.slice, ast.Constant)
                and node.left.slice.value in {"block", "case", "group", "identity", "source", "subset"}):
            locators.update(part for argument in node.comparators for part in ast.walk(argument)
                            if isinstance(part, ast.Constant) and isinstance(part.value, str))
        if (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)):
            locators.add(node.slice)
        if isinstance(node, ast.keyword) and node.arg in {"color", "edgecolor", "edgecolors", "facecolor", "facecolors"}:
            locators.update(ast.walk(node.value))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and node not in locators and node.value != SCIENTIFIC.pattern and node.value not in record_paths):
            yield node.lineno, node.value, lines[node.lineno - 1].strip()


def typed_numbers(values, collisions):
    def candidates():
        for path in manuscript_sources():
            text = manuscript_body(path.read_text())
            yield path.relative_to(ROOT).as_posix(), 1, text, mask_syntax(text), None
        path = Path(__file__)
        for line, literal, statement in display_literals(path):
            yield path.relative_to(ROOT).as_posix(), line, literal, mask_syntax(literal), statement

    registered = {value for row in values.values() for _, value in numeric_occurrences(row["value"], row["value"])}
    reviewed = collections.defaultdict(list)
    for i, entry in enumerate(collisions):
        reviewed[entry["file"], entry["token"]].append((i, entry))
    used = collections.Counter()
    for file, line, text, masked, statement in candidates():
        for match, value in numeric_occurrences(text, masked):
            if value not in registered:
                continue
            accepted = []
            for i, entry in reviewed[file, match[0]]:
                if "statement" in entry and statement != entry["statement"]:
                    continue
                excerpt = entry["context"]
                if entry.get("literal") and text != excerpt:
                    continue
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
        if used[i] != entry.get("count", 1):
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
    outputs = render_all()
    manuscript = "\n".join(COMMENT.sub("", path.read_text()) for path in manuscript_sources())
    expected_tables = {LATEX / (name + ".tex") for name in re.findall(r"\\input\{(tables/[^}]+)\}", manuscript)}
    expected_figures = {
        LATEX / "figures/generated" / name
        for name in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", manuscript)
    }
    expected = expected_tables | expected_figures | {GRAPHICAL_ABSTRACT.with_suffix(s) for s in (".png", ".pdf")}
    if expected != outputs.keys():
        raise ValueError(f"Display files differ from the manuscript: missing {sorted(expected - outputs.keys())}; "
                         f"unused {sorted(outputs.keys() - expected)}")
    occurrences = collections.Counter(RES.findall(manuscript))
    for body in outputs.values():
        if isinstance(body, str):
            occurrences.update(RES.findall(COMMENT.sub("", body)))
    values = result_values(occurrences)
    if args.bindings is not None:
        bindings(values, outputs, args.bindings or None)
        return
    values_path = TABLES / "results.tex"
    values_text = tex_values(values)
    source_path = TABLES / "number-sources.json"
    binding_sources = {record for value in values.values()
                       for record in (value["record"] if isinstance(value["record"], list) else [value["record"]])}
    unknown = binding_sources - catalog.keys()
    if unknown:
        raise ValueError(f"Unregistered number sources: {sorted(unknown)}")
    source_text = json.dumps(
        {
            key: dict(record=row["record"], sha256=sources.get(key, row["sha256"]), read=key in sources,
                      **({"printed_binding": True} if key in binding_sources else {}))
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
