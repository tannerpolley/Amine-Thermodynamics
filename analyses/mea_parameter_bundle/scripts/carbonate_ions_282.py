"""Issue 282: water-HCO3- and water-CO3^2- anchored to aqueous sodium-salt osmotic data on the record's water, then an MEA refit.

Design: issue #282 body (revised 2026-11-09). Reuses the #255 driver (stable_refit_255.py) unchanged by import; its
module globals OUT and A6 are pointed at this issue's results directory for the MEA fits.
Commands (repository root, worktree .venv with the bc779473 wheel, `--no-sync`, under agent-heavy):
  qualify | salt | scan | leverage | anchors | fit <final|candidate> | assess <final|candidate> | select
Steps after salt run only when salt/summary.json records F1 as passed (issue branch F1).
"""
# ruff: noqa: E402 -- the #255 driver sets thread counts and the wheel identity before Engine imports.
import copy
import csv
import json
import math
import os
from pathlib import Path
import sys

sys.path[:0] = [str(Path(__file__).parent)]
import stable_refit_255 as r

s, epcsaft, reg, eq = r.s, r.epcsaft, r.reg, r.eq
B, ROOT = r.B, r.ROOT
OUT = B / 'results/carbonate-ions-282'
INPUTS = OUT / 'inputs'
R255 = B / 'results/stable-refit-255'
W, NA, CL = 'water', 'sodium-cation', 'chloride-anion'
HCO3, CO3, OH, MEAH = 'bicarbonate-anion', 'carbonate-anion', 'hydroxide-anion', 'protonated-monoethanolamine'
P_SALT = 1e5  # Pa; the issue's 0.1 MPa liquid
T_SALT = 298.15  # K, reference temperature of the salt laws
T_RECORD = 313.15  # K, the record's pair-law reference temperature
NA_SLOPE = -0.007981  # 1/K, Held 2014 Table 2 note a, held
HELD = dict(source_id='held-2014', locator='Held 2014 Table 2 (strategy 2), Table 3')
# Held 2014 Table 2, strategy 2: sigma / angstrom, u/k / K; charge; molar mass / kg mol-1
IONS = {NA: (2.8232, 230.0, +1, 0.02298977), CL: (2.7560, 170.0, -1, 0.035453)}
SALT_PAIRS = {(NA, CL): 0.317, (NA, HCO3): -0.514, (NA, CO3): -1.0, (NA, OH): 0.649, (CL, W): -0.25}  # Held 2014 Table 3
LAWS = {NA: 'pair/sodium-cation/water/k_ij', HCO3: 'pair/bicarbonate-anion/water/k_ij', CO3: 'pair/carbonate-anion/water/k_ij'}
HELD_A0 = {NA: 2.37999 + NA_SLOPE * T_SALT, HCO3: 0.0, CO3: -0.25}  # starts: Held's values at 298.15 K
BOUNDS = {0: (-1., 1.), 1: (-0.02, 0.02)}  # a0, a1 / K-1 (design choices)
SCALES = {0: 0.01, 1: 1e-4}
WANGLER = (-7.65e-2, -6.25e-4, -6.25e-5)  # Wangler 2018 Table 6, polynomial orders 0-2 about 298.15 K (issue's interpretation)
F1_AARD = 1.5  # percent
F1_NA2CO3_AMENDED = 6.5  # percent; owner amendment to F1, 2026-11-09 (Held 2014 Table 5, worst 1:2 salt 6.43 %)
F1_FALSIFIED = 0.5  # water-HCO3- at 313.15 K
AMENDMENT = ('Owner amendment to F1 (2026-11-09), issue #282 body, "Numerical falsifier": Na2CO3 AARD <= 6.5 % (Held 2014 Table 5, '
             'strategy 2, 298.15 K: Na2SO4 2.41 %, K2HPO4 4.95 %, Na2HPO4 6.43 %); NaHCO3 AARD <= 1.5 %; coefficients on a bound are '
             'stated limits, not gate failures; water-HCO3- >= 0.5 at 313.15 K still falsifies. No fitted number changes.')
FINAL = r.STARTS['final']
CANDIDATE = R255 / 'wide/candidate.json'


r.OUT = OUT  # the #255 driver's writer, grids, census and stage fits write here
write, result = r.write, r.result


def r255(rel):
    payload = r.read(R255 / rel)
    assert payload['wheel_sha256'] == r.SHA
    return payload['result']


# ---------------------------------------------------------------- temperature laws

def law_node(identity, a0, a1, t_ref, provenance):
    """A pair k_ij as k(T) = a0 + a1 (T - t_ref) (Engine polynomial-plus-reciprocal-temperature form, no 1/T term)."""
    term = lambda p, v, u: dict(power=p, coefficient=dict(identity=f'{identity}/a{p}', value=dict(magnitude=v, unit=u)))
    return dict(family='k_ij', identity=identity, provenance=provenance,
                temperature_law=dict(form='polynomial-plus-reciprocal-temperature', reference_temperature=dict(magnitude=t_ref, unit='kelvin'),
                                     terms=[term(0, a0, 'dimensionless'), term(1, a1, '1 / kelvin')]))


def set_pair(mapping, a, b, node):
    x, y = sorted((a, b))
    pair = next((p for p in mapping['pairs'] if {p['component_id_a'], p['component_id_b']} == {x, y}), None)
    if pair is None:
        pair = dict(component_id_a=x, component_id_b=y, coefficients=[])
        mapping['pairs'].append(pair)
    pair['coefficients'] = [c for c in pair['coefficients'] if not c['identity'].startswith(f'pair/{x}/{y}/k_ij')] + [node]


def k_node(mapping, identity, value, provenance):
    template = copy.deepcopy(next(c for p in mapping['pairs'] for c in p['coefficients'] if c['family'] == 'k_ij' and 'value' in c))
    template.update(identity=identity, value=dict(magnitude=value, unit='dimensionless'))
    template['provenance'] = {**template['provenance'], **provenance}
    return template


def law_value(law, T):
    return law['a0'] + law['a1'] * (T - law['t_ref'])


# ---------------------------------------------------------------- salt document

def salt_document(laws):
    """The selected record reduced to water, Na+, Cl-, HCO3-, CO3^2- and OH-; Na+/Cl- in the record's ion conventions.

    ``laws``: {ion: (a0, a1)} about 298.15 K for the three water-ion laws."""
    mapping = copy.deepcopy(s.parameter_mapping(FINAL))
    template = next(c for c in mapping['components'] if c['component_id'] == HCO3)
    for ion, (sigma, u, z, molar_mass) in IONS.items():
        c = copy.deepcopy(template)
        c.update(component_id=ion, name=ion, aliases=[ion])
        c['fixed']['charge_number']['value']['magnitude'] = z
        c['fixed']['molar_mass']['value']['magnitude'] = molar_mass
        for field in c['fixed'].values():
            field['provenance'] = {**field['provenance'], **HELD}
        values = dict(segment_count=1.0, segment_diameter=sigma, dispersion_energy_over_k=u, packing_diameter=0.88 * sigma,
                      debye_huckel_diameter=sigma, born_diameter=sigma, solvation_factor=1.0)  # Born diameter sigma: design choice
        for node in c['coefficients']:
            node['identity'] = f"component/{ion}/{node['family']}"
            node['value'] = {**node['value'], 'magnitude': values[node['family']]}
            node['provenance'] = {**node['provenance'], **HELD}
        mapping['components'].append(c)
    keep = {W, NA, CL, HCO3, CO3, OH}
    mapping['components'] = [c for c in mapping['components'] if c['component_id'] in keep]
    mapping['pairs'] = [p for p in mapping['pairs'] if {p['component_id_a'], p['component_id_b']} <= keep]
    mapping['correlations'] = [c for c in mapping['correlations'] if c['component_id'] in keep]
    mapping['reaction_correlations'] = []
    topology = mapping['topology']
    topology['sites'] = [x for x in topology['sites'] if x['component_id'] in keep]
    topology['edges'] = [e for e in topology['edges'] if {e['endpoint_a']['component_id'], e['endpoint_b']['component_id']} <= keep]
    for key in ('no_cross_association',):
        for owner in (mapping, topology):
            if key in owner:
                owner[key] = [x for x in owner[key] if {v for k, v in x.items() if k.startswith('component_id')} <= keep]
    for (a, b), k in SALT_PAIRS.items():
        set_pair(mapping, a, b, k_node(mapping, f'pair/{min(a, b)}/{max(a, b)}/k_ij', k, HELD))
    own = dict(source_id='carbonate-ions-282', locator='analyses/mea_parameter_bundle/scripts/carbonate_ions_282.py')
    for ion, (a0, a1) in laws.items():
        set_pair(mapping, ion, W, law_node(LAWS[ion], a0, a1, T_SALT, own))
    return mapping


def water_molar_mass():
    return next(c for c in s.parameter_mapping(FINAL)['components'] if c['component_id'] == W)['fixed']['molar_mass']['value']['magnitude']


# ---------------------------------------------------------------- salt rows

def nacl_rows(parameters):
    out = []
    for row in csv.DictReader((INPUTS / 'hamer-wu-1972-nacl.csv').open()):
        m, phi = float(row['molality']), float(row['phi'])
        item = reg.electrolyte(parameters, 'osmotic_coefficient', float(row['temperature_K']), P_SALT, {W: 1.0}, ions=(NA, CL),
                               stoichiometry=(1, 1), molality=m, observed=phi, form='difference', scale=0.003)
        out.append(dict(salt='NaCl', T=float(row['temperature_K']), m=m, observed=phi, item=item))
    return out


def carbonate_rows(parameters, salts):
    """Peiper & Pitzer Table 6 rows at the printed equilibrium ionic composition (charge-closed), observed on the ionic basis."""
    mw, out = water_molar_mass(), []
    for row in csv.DictReader((INPUTS / 'peiper-pitzer-1982-table6.csv').open()):
        if row['salt'] not in salts:
            continue
        m = float(row['nominal_molality'])
        printed = {k: float(row[k]) for k in ('X2', 'Y', 'H2X', 'Z')}
        na = {'NaHCO3': m, 'Na2CO3': 2 * m, 'mixed': 3 * m}[row['salt']]
        ions = {NA: na, CO3: printed['X2'], HCO3: printed['Y'], OH: printed['Z']}
        minor = CO3 if row['salt'] == 'NaHCO3' else OH  # charge closure (issue: Na+ nominal, minor anion by balance)
        ions[minor] = (na - ions[HCO3] - (2 * ions[CO3] if minor == OH else ions[OH])) / (2 if minor == CO3 else 1)
        adjustment = ions[minor] - (printed['X2'] if minor == CO3 else printed['Z'])
        if ions[minor] < 0:
            out.append(dict(salt=row['salt'], T=float(row['temperature_K']), m=m, unavailable='charge closure gives a negative minor anion'))
            continue
        total_printed = na + sum(printed.values())
        ionic = sum(ions.values())
        phi_ion = (float(row['phi']) * total_printed - printed['H2X']) / ionic  # dissolved CO2 ideal
        n_water = 1 / mw
        x = {W: n_water / (n_water + ionic), **{k: v / (n_water + ionic) for k, v in ions.items()}}
        item = reg.mixture_osmotic_coefficient(parameters, float(row['temperature_K']), P_SALT, x, observed=phi_ion, scale=0.01)
        out.append(dict(salt=row['salt'], T=float(row['temperature_K']), m=m, observed=phi_ion, phi_printed=float(row['phi']),
                        water_activity=float(row['water_activity']), charge_adjustment=adjustment, h2x_share=printed['H2X'] / total_printed,
                        composition_mol_per_kg=ions, item=item))
    return out


def predict(mapping, rows):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    out = []
    for x in rows:
        if 'item' not in x:
            out.append({k: v for k, v in x.items() if k != 'item'})
            continue
        p = reg.predict(model, x['item'])
        out.append(dict({k: v for k, v in x.items() if k != 'item'}, status=p.status.name, value=p.value,
                        relative_error=p.value / x['observed'] - 1 if p.status.name == 'Available' else None))
    return out


def aard(rows):
    e = [abs(x['relative_error']) for x in rows if x.get('relative_error') is not None]
    return dict(n=len(e), aard_percent=100 * sum(e) / len(e), max_percent=100 * max(e))


# ---------------------------------------------------------------- salt fits (Method step 2)

def salt_fit(name, laws, active, rows_of):
    """One cascade fit: ``active`` = [(ion, power), ...] law coefficients; other laws held at ``laws``."""
    mapping = salt_document(laws)
    parameters = epcsaft.Parameters.from_mapping(mapping)
    rows = rows_of(parameters)
    coordinates = [reg.coordinate(parameters, [('temperature_law_coefficient', f'{LAWS[ion]}/a{p}', 1.0)], origin=laws[ion][p],
                                  scale=SCALES[p], bounds=BOUNDS[p]) for ion, p in active]
    controls = reg.FitControls(maximum_iterations=200, maximum_elapsed_time_seconds=3600., function_tolerance=1e-12,
                               parameter_tolerance=1e-12, gradient_tolerance=1e-10, workers=r.CORES)
    fit = reg.fit(parameters, coordinates, [x['item'] for x in rows], controls=controls)
    fitted = copy.deepcopy(laws)
    for (ion, p), value in zip(active, fit.physical, strict=True):
        fitted[ion] = tuple(value if i == p else fitted[ion][i] for i in (0, 1))
    on_bound = [dict(coefficient=f'{LAWS[ion]}/a{p}', value=v, bounds=BOUNDS[p]) for (ion, p), v in zip(active, fit.physical, strict=True)
                if min(abs(v - BOUNDS[p][0]), abs(v - BOUNDS[p][1])) <= 1e-8 * max(1., abs(v))]
    replay = predict(salt_document(fitted), rows)
    difference = max(abs(x['value'] - pv) for x, pv in zip(replay, fit.predictions, strict=True))
    report = dict(name=name, status=fit.status, message=fit.message, usable=fit.usable, iterations=len(fit.iteration_costs or []),
                  initial_cost=fit.initial_cost, final_cost=fit.final_cost, active=[f'{LAWS[i]}/a{p}' for i, p in active],
                  start={f'{LAWS[i]}/a{p}': laws[i][p] for i, p in active}, endpoint={f'{LAWS[i]}/a{p}': v for (i, p), v in zip(active, fit.physical, strict=True)},
                  on_bound=on_bound, covariance_active_bounds=r.jsonable(fit.covariance.active_bounds), replay_maximum_difference=difference,
                  laws={ion: dict(a0=v[0], a1=v[1], t_ref=T_SALT) for ion, v in fitted.items()}, rows=replay)
    write(f'salt/{name}.json', report)
    print(name, fit.status, fit.final_cost, json.dumps(report['endpoint']), 'bounds', len(on_bound), 'replay', difference, flush=True)
    return fitted, report


def salt():
    r.verify()
    laws = {ion: (a0, NA_SLOPE if ion == NA else 0.) for ion, a0 in HELD_A0.items()}
    laws, a = salt_fit('1a-sodium', laws, [(NA, 0)], nacl_rows)
    laws, b = salt_fit('1b-bicarbonate', laws, [(HCO3, 0), (HCO3, 1)], lambda p: carbonate_rows(p, {'NaHCO3'}))
    laws, c = salt_fit('1c-carbonate', laws, [(CO3, 0), (CO3, 1)], lambda p: carbonate_rows(p, {'Na2CO3'}))
    combined = salt_document(laws)
    parameters = epcsaft.Parameters.from_mapping(combined)
    groups = dict(NaCl=nacl_rows(parameters), NaHCO3=carbonate_rows(parameters, {'NaHCO3'}), Na2CO3=carbonate_rows(parameters, {'Na2CO3'}),
                  mixed=carbonate_rows(parameters, {'mixed'}))
    replay = {g: predict(combined, rows) for g, rows in groups.items()}
    scores = {g: aard(v) for g, v in replay.items()}
    for g in ('NaHCO3', 'Na2CO3', 'mixed'):
        scores[g]['by_temperature'] = {T: aard([x for x in replay[g] if x['T'] == T]) for T in sorted({x['T'] for x in replay[g]})}
    hco3 = dict(a0=laws[HCO3][0], a1=laws[HCO3][1], t_ref=T_SALT)
    at_313 = law_value(hco3, T_RECORD)
    bounded = a['on_bound'] + b['on_bound'] + c['on_bound']
    temperatures = [278.15 + 5 * i for i in range(24)]
    curves = [dict(T=T, sodium=law_value(dict(a0=laws[NA][0], a1=laws[NA][1], t_ref=T_SALT), T), bicarbonate=law_value(hco3, T),
                   carbonate=law_value(dict(a0=laws[CO3][0], a1=laws[CO3][1], t_ref=T_SALT), T), held_bicarbonate=0.0, held_carbonate=-0.25,
                   wangler_bicarbonate=sum(c_ * (T - 298.15) ** i for i, c_ in enumerate(WANGLER)), final_set_bicarbonate=0.7270558477497251,
                   candidate_255_bicarbonate=1.0) for T in temperatures]
    adjustments = [abs(x['charge_adjustment']) for g in ('NaHCO3', 'Na2CO3') for x in replay[g]]
    record = dict(laws={ion: dict(a0=v[0], a1=v[1], t_ref=T_SALT) for ion, v in laws.items()},
                  laws_at_record_reference={ion: dict(a0=v[0] + v[1] * (T_RECORD - T_SALT), a1=v[1], t_ref=T_RECORD) for ion, v in laws.items()},
                  values_313_15={ion: v[0] + v[1] * (T_RECORD - T_SALT) for ion, v in laws.items()},
                  scores=scores, **f1_gates(scores, at_313, bounded), on_bound=bounded, largest_charge_adjustment=max(adjustments),
                  largest_dissolved_co2_share=max(x['h2x_share'] for g in ('NaHCO3', 'Na2CO3') for x in replay[g]),
                  curves=curves, rows=replay, document=combined)
    write('salt/summary.json', record)
    with (OUT / 'salt/phi-residuals.csv').open('w', newline='') as h:
        w = csv.DictWriter(h, ['salt', 'temperature_K', 'molality', 'phi_observed_ionic', 'phi_printed', 'phi_model', 'relative_error',
                               'charge_adjustment', 'dissolved_co2_share', 'role'], lineterminator='\n')
        w.writeheader()
        for g, rows in replay.items():
            for x in rows:
                w.writerow(dict(salt=g, temperature_K=x['T'], molality=x['m'], phi_observed_ionic=x.get('observed'), phi_printed=x.get('phi_printed', x.get('observed')),
                                phi_model=x.get('value'), relative_error=x.get('relative_error'), charge_adjustment=x.get('charge_adjustment'),
                                dissolved_co2_share=x.get('h2x_share'), role='comparison' if g == 'mixed' else 'fitted'))
    with (OUT / 'salt/laws.csv').open('w', newline='') as h:
        w = csv.DictWriter(h, list(curves[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(curves)
    salt_figure(replay, curves)
    print(json.dumps(dict(scores={g: {k: v for k, v in x.items() if k != 'by_temperature'} for g, x in scores.items()}, gates=record['gates'],
                          values_313_15=record['values_313_15'])), flush=True)


def f1_gates(scores, at_313, bounded):
    """F1 as written in the issue (kept) and under the owner amendment (``gates``, which the MEA guard reads)."""
    nahco3, na2co3 = scores['NaHCO3']['aard_percent'], scores['Na2CO3']['aard_percent']
    falsified = at_313 >= F1_FALSIFIED
    written = dict(nahco3_aard_passed=nahco3 <= F1_AARD, na2co3_aard_passed=na2co3 <= F1_AARD, coefficients_interior=not bounded,
                   water_bicarbonate_313=at_313, compensation_falsified=falsified)
    written['F1_passed'] = written['nahco3_aard_passed'] and written['na2co3_aard_passed'] and written['coefficients_interior'] and not falsified
    amended = dict(rule=AMENDMENT, nahco3_aard_percent=nahco3, nahco3_aard_limit=F1_AARD, nahco3_aard_passed=nahco3 <= F1_AARD,
                   na2co3_aard_percent=na2co3, na2co3_aard_limit=F1_NA2CO3_AMENDED, na2co3_aard_passed=na2co3 <= F1_NA2CO3_AMENDED,
                   coefficients_on_bound_stated_limits=[x['coefficient'] for x in bounded], water_bicarbonate_313=at_313,
                   compensation_falsified=falsified,
                   conditional_on='every result after F1 is conditional on water-Na+ a0 = -1 (lower bound; Held 2014 about 0.0005 at 298.15 K) '
                                  'and water-CO3^2- a0 = -1 (lower bound)')
    amended['F1_passed'] = amended['nahco3_aard_passed'] and amended['na2co3_aard_passed'] and not falsified
    return dict(gates_as_written=written, gates=amended)


def amend():
    """Re-score F1 on the retained combined document under the owner amendment; no fit, no prediction."""
    path = OUT / 'salt/summary.json'
    payload = r.read(path)
    assert payload['wheel_sha256'] == r.SHA
    record = payload['result']
    written = record.pop('gates_as_written', None) or record['gates']  # a rerun finds the as-written block already moved
    record.pop('gates')
    at_313 = law_value(record['laws'][HCO3], T_RECORD)
    gates = f1_gates(record['scores'], at_313, record['on_bound'])
    assert gates['gates_as_written'] == written, 'as-written gates do not reproduce from the retained scores'
    ordered = {}
    for k, v in record.items():
        ordered[k] = v
        if k == 'scores':
            ordered.update(gates)
    write('salt/summary.json', ordered)
    print(json.dumps(gates['gates']), flush=True)


def salt_figure(replay, curves):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.2), constrained_layout=True)
    colors = dict(zip((278.15, 288.15, 298.15, 308.15, 318.15), plt.cm.viridis([0, .25, .5, .75, .95])))
    for ax, g in zip(axes[:3], ('NaCl', 'NaHCO3', 'Na2CO3')):
        for T in sorted({x['T'] for x in replay[g]}):
            rows = sorted((x for x in replay[g] if x['T'] == T), key=lambda x: x['m'])
            ax.plot([x['m'] for x in rows], [x['observed'] for x in rows], 'o', ms=4, color=colors[T], label=f'{T:.2f} K')
            ax.plot([x['m'] for x in rows], [x['value'] for x in rows], '-', color=colors[T])
        ax.set(xlabel='nominal molality / mol kg$^{-1}$', ylabel=r'$\Phi$ (ionic basis)', title=f'{g}: points source, lines model')
        ax.legend(fontsize=7)
    ax = axes[3]
    T = [c['T'] for c in curves]
    for key, style, label in (('bicarbonate', 'C0-', 'water-HCO$_3^-$ (1b)'), ('carbonate', 'C1-', 'water-CO$_3^{2-}$ (1c)'),
                              ('wangler_bicarbonate', 'C0--', 'Wangler 2018 HCO$_3^-$'), ('held_bicarbonate', 'C0:', 'Held 2014 HCO$_3^-$'),
                              ('held_carbonate', 'C1:', 'Held 2014 CO$_3^{2-}$'), ('final_set_bicarbonate', 'k-.', 'final set HCO$_3^-$'),
                              ('candidate_255_bicarbonate', 'k:', '#255 candidate HCO$_3^-$')):
        ax.plot(T, [c[key] for c in curves], style, label=label)
    ax.axvspan(278.15, 318.15, color='0.9')
    ax.set(xlabel='T / K', ylabel='$k_{ij}$', title='water-anion laws (fitted range shaded)')
    ax.legend(fontsize=7)
    fig.savefig(OUT / 'salt/phi-molality.png', dpi=150)


def scan():
    """Diagnostic after F1 (no fit): NaCl phi on the formula and full-composition paths, and phi against each pinned a0."""
    r.verify()
    laws = {ion: (v['a0'], v['a1']) for ion, v in result('salt/summary.json')['laws'].items()}
    mapping = salt_document(laws)
    parameters = epcsaft.Parameters.from_mapping(mapping)
    model, n = epcsaft.Mixture(parameters), 1 / water_molar_mass()
    paths = []
    for m in (0.1, 0.5, 1.0):
        formula = reg.predict(model, reg.electrolyte(parameters, 'osmotic_coefficient', T_SALT, P_SALT, {W: 1.0}, ions=(NA, CL), stoichiometry=(1, 1),
                                                     molality=m, observed=1., form='difference', scale=1.)).value
        full = reg.predict(model, reg.mixture_osmotic_coefficient(parameters, T_SALT, P_SALT, {W: n / (n + 2 * m), NA: m / (n + 2 * m), CL: m / (n + 2 * m)},
                                                                  observed=1., scale=1.)).value
        paths.append(dict(molality=m, formula=formula, mixture=full, difference=formula - full))
    sweeps = []
    for ion, rows_of in ((NA, nacl_rows), (CO3, lambda p: [x for x in carbonate_rows(p, {'Na2CO3'}) if x['T'] == T_SALT])):
        for a0 in (-1., -0.5, 0., 0.5, 1.):
            trial = dict(laws, **{ion: (a0, laws[ion][1])})
            document = salt_document(trial)
            for x in predict(document, rows_of(epcsaft.Parameters.from_mapping(document))):
                sweeps.append(dict(law=LAWS[ion], a0=a0, salt=x['salt'], T=x['T'], molality=x['m'], observed=x['observed'], model=x['value']))
    write('salt/sensitivity.json', dict(paths=paths, sweeps=sweeps))


# ---------------------------------------------------------------- MEA records with the salt laws held

MEAH_HCO3 = 'pair/bicarbonate-anion/protonated-monoethanolamine/k_ij'
A6_282 = OUT / 'a6-spec.json'


def salt_laws():
    summary = result('salt/summary.json')
    assert summary['gates']['F1_passed'], 'F1 failed: no MEA step runs on an unestablished anchor'
    return summary['laws_at_record_reference']


def substituted(mapping, meah_hco3=0.):
    """The MEA record with water-HCO3- and water-CO3^2- held at the salt laws (about 313.15 K) and MEAH+-HCO3- set."""
    out = copy.deepcopy(mapping)
    own = dict(source_id='carbonate-ions-282', locator='results/carbonate-ions-282/salt/summary.json laws_at_record_reference')
    for ion, law in salt_laws().items():
        if ion != NA:
            set_pair(out, ion, W, law_node(LAWS[ion], law['a0'], law['a1'], law['t_ref'], own))
    return s.with_parameter_values(out, {MEAH_HCO3: meah_hco3})


STARTS = {'final': lambda: (substituted(s.parameter_mapping(FINAL)), dict(r.SHIFTS['final'])),
          'candidate': lambda: (substituted(r.read(CANDIDATE)['result']), r255('wide/retreat.json')['shifts'])}


def enforced_states():
    excluded = r255('qualification/summary.json')['excluded']
    return [x for x in r.states()[0] if x['key'] not in excluded]


def qualify():
    """Method 1: the #255 candidate and the final set replayed against the retained #255 rows within 1e-8 relative."""
    r.verify()
    out = {}
    for name, mapping, retained in (('final', s.parameter_mapping(FINAL), 'qualification/final-replay.json'),
                                     ('candidate', r.read(CANDIDATE)['result'], 'wide/replay.json')):
        values, ok, cost = r.replay(mapping)
        old = {v['identity']: v for v in r255(retained)}
        diff = max(max(abs(v[k] - old[v['identity']][k]) / max(1., abs(old[v['identity']][k])) for k in ('value', 'residual', 'weighted_residual'))
                   for v in values)
        reference = math.fsum(v['cost'] for v in old.values())
        out[name] = dict(rows=len(values), available=ok, cost=cost, retained_cost=reference, relative_cost_difference=abs(cost / reference - 1),
                         maximum_row_difference=diff)
        write(f'qualification/{name}-replay.json', values)
    out['passed'] = all(x['available'] and x['rows'] == 307 and x['maximum_row_difference'] <= 1e-8 and x['relative_cost_difference'] <= 1e-8
                        for x in out.values())
    write('qualification/summary.json', out)
    print(json.dumps(out), flush=True)
    assert out['passed'], 'qualification failed'


def leverage():
    """Method 3: finite-difference change of the 307-row cost and weighted residuals for MEAH+-HCO3- = +/-0.1 (no fit)."""
    r.verify()
    base = substituted(s.parameter_mapping(FINAL))
    runs = {}
    for k in (0., .1, -.1):
        values, ok, cost = r.replay(s.with_parameter_values(base, {MEAH_HCO3: k}))
        runs[k] = dict(available=ok, cost=cost, weighted=[v.get('weighted_residual') for v in values], groups=r.metrics(values) if ok else None)
    assert all(x['available'] for x in runs.values()), 'a leverage replay is unavailable'
    c0 = runs[0.]['cost']
    plus, minus = runs[.1]['cost'] - c0, runs[-.1]['cost'] - c0
    delta = lambda k: math.sqrt(math.fsum((a - b) ** 2 for a, b in zip(runs[k]['weighted'], runs[0.]['weighted'], strict=True)))
    statistic = max(abs(plus), abs(minus))
    out = dict(cost_0=c0, cost_plus=runs[.1]['cost'], cost_minus=runs[-.1]['cost'], change_plus=plus, change_minus=minus,
               statistic=statistic, threshold=0.1, negligible=statistic < 0.1, cost_derivative_central=(runs[.1]['cost'] - runs[-.1]['cost']) / .2,
               weighted_residual_change_norm_plus=delta(.1), weighted_residual_change_norm_minus=delta(-.1),
               group_cost_change={g: dict(plus=runs[.1]['groups'][g]['cost'] - runs[0.]['groups'][g]['cost'],
                                          minus=runs[-.1]['groups'][g]['cost'] - runs[0.]['groups'][g]['cost']) for g in runs[0.]['groups']})
    write('leverage.json', out)
    print(json.dumps({k: v for k, v in out.items() if k != 'group_cost_change'}), flush=True)


def a6_spec():
    """The #255 a6 coordinates without water-HCO3- (held), plus MEAH+-HCO3- unless step 3 found negligible leverage."""
    spec = json.loads((r.CHAIN / 'a6/spec.json').read_text())
    coordinates = [q for q in spec['information_coordinates'] if q['identity'] != LAWS[HCO3]]
    assert len(coordinates) == len(spec['information_coordinates']) - 1
    if not result('leverage.json')['negligible']:
        coordinates.append(dict(identity=MEAH_HCO3, family='k_ij', scale=0.1, bounds=[-1., 1.], target=[HCO3, MEAH]))
    text = json.dumps(dict(controls=spec['controls'], information_coordinates=coordinates,
                           source='results/engine-3e83e19c-refit-chain/a6/spec.json with issue 282 changes'), indent=1) + '\n'
    if not A6_282.exists() or A6_282.read_text() != text:  # the two refits run in parallel and read this file
        A6_282.write_text(text)


def admissible(mapping, enforced):
    ok, tal, cost = r.admissible(mapping, enforced)
    return dict(admissible=ok, cost=cost, **{k: tal[k] for k in ('states', 'available', 'descent', 'minimum_tau')}, unavailable=tal['unavailable'])


def anchors():
    """Method 4 qualification of both substituted starts; the anchor is the substituted final set if admissible, else the candidate."""
    r.verify()
    enforced = enforced_states()
    assert len(enforced) == 1903
    out = {name: admissible(start()[0], enforced) for name, start in STARTS.items()}
    out['anchor'] = next((n for n in ('final', 'candidate') if out[n]['admissible']), None)
    write('anchors.json', out)
    print(json.dumps({k: (v if k == 'anchor' else {x: v[x] for x in ('admissible', 'cost', 'descent', 'available')}) for k, v in out.items()}), flush=True)
    assert out['anchor'], 'neither substituted start is admissible: return to Design'


STAGE_SECONDS = 76800.  # owner, 2026-11-09: #255's 7200 s per stage x 32/3 for the standing 3-core cap; these two refits only


def scaled_bind(mapping):
    """r.bind whose fit uses STAGE_SECONDS; #255's stage_fit (shared with #283) keeps its 7200 s line unchanged."""
    spec = BIND(mapping)
    fit = spec.fit

    def scaled(*args, **kwargs):
        spec.spec['optimizer']['maximum_elapsed_time_seconds'] = STAGE_SECONDS
        return fit(*args, **kwargs)
    spec.fit = scaled
    return spec


BIND = r.bind


def run_fit(run):
    """#255 penalty stages and stop rule from one substituted start; retreat toward the qualified anchor, never to it."""
    r.verify()
    r.A6 = A6_282
    r.bind = scaled_bind
    a6_spec()
    assert result('qualification/summary.json')['passed']
    anchor_name = result('anchors.json')['anchor']
    enforced = enforced_states()
    start, shifts = STARTS[run]()
    anchor, anchor_shifts = STARTS[anchor_name]()
    endpoint, endpoint_shifts = None, None
    for index, scale in enumerate(r.STAGES):
        report = r.stage_fit(run, index, scale, start, shifts, enforced)
        if not report.get('endpoint_replay_available'):
            break
        endpoint, shifts = result(f'{run}/stage-{index}/parameters.json'), report['endpoint_shifts']
        endpoint_shifts = shifts
        tal = report['stability_tally']
        if tal['descent'] == 0 and not tal['unavailable']:
            break
        if report['status'] not in ('converged', 'limit_reached') or tal['unavailable']:
            break
        start = endpoint
    refreshed = admissible(anchor, enforced)  # the issue: refresh the anchor before the inherited retreat
    retreat(run, anchor, anchor_name, refreshed, endpoint, enforced, (anchor_shifts, endpoint_shifts))


def retreat(run, anchor, anchor_name, refreshed, endpoint, enforced, shifts):
    """The #255 scan (t = 1, 0.99, ...) and bisection, without the anchor fallback: t = 0 is never a candidate."""
    if (OUT / run / 'retreat.json').exists():
        return
    trace, passing, suspects = [], None, ()
    if endpoint is not None and refreshed['admissible']:
        t = 1.
        while t > 0.005:
            ok, tal, cost = r.admissible(r.segment(anchor, endpoint, t), enforced, suspects=suspects)
            suspects = tal['suspects']  # states failing here are searched first at the next step (same decision, cheaper rejection)
            trace.append(dict(t=t, admissible=ok, cost=cost, screened=tal.get('screened', False), **{k: tal[k] for k in ('descent', 'available', 'minimum_tau')},
                              unavailable=len(tal['unavailable'])))
            print(run, 'retreat', json.dumps(trace[-1]), flush=True)
            if ok:
                passing = t
                break
            t = round(t - .01, 10)
        if passing is not None and passing < 1.:
            low, high = passing, min(1., passing + .01)
            for _ in range(10):
                mid = (low + high) / 2
                ok, tal, cost = r.admissible(r.segment(anchor, endpoint, mid), enforced, suspects=suspects)
                suspects = tal['suspects'] or suspects
                trace.append(dict(t=mid, admissible=ok, cost=cost, screened=tal.get('screened', False), **{k: tal[k] for k in ('descent', 'available', 'minimum_tau')},
                                  unavailable=len(tal['unavailable'])))
                print(run, 'refine', json.dumps(trace[-1]), flush=True)
                low, high = (mid, high) if ok else (low, mid)
            passing = low
    reason = ('no stage returned an available 307-row endpoint' if endpoint is None else 'the refreshed anchor is not admissible'
              if not refreshed['admissible'] else 'no admissible point with t > 0' if passing is None else None)
    a, e = shifts
    write(f'{run}/retreat.json', dict(t=passing, failed=reason is not None, reason=reason, anchor=anchor_name, anchor_refreshed=refreshed, trace=trace,
                                      shifts=None if passing is None else {k: a.get(k, 0.) + passing * (e.get(k, 0.) - a.get(k, 0.)) for k in a.keys() | e.keys()}))
    if passing is not None:
        write(f'{run}/candidate.json', r.segment(anchor, endpoint, passing))


def assess(run):
    """#255 criteria 1-3 against the unsubstituted final set on the same wheel and inputs."""
    r.verify()
    r.A6 = A6_282
    retreat_ = result(f'{run}/retreat.json')
    if retreat_['failed']:
        write(f'{run}/assessment.json', dict(run=run, passed=False, reason=retreat_['reason']))
        return
    enforced, offset = r.states()
    excluded = r255('qualification/summary.json')['excluded']
    candidate = result(f'{run}/candidate.json')
    values, ok, cost = r.replay(candidate)
    assert ok, 'candidate replay unavailable'
    g = r.grid(candidate, enforced + offset)
    write(f'{run}/grid.json.gz', g)
    stab = dict(enforced=r.tally([x for x in g[:len(enforced)] if x['key'] not in excluded]),
                excluded=r.tally([x for x in g[:len(enforced)] if x['key'] in excluded]), offset=r.tally(g[len(enforced):]), census=r.census(candidate, run))
    stability_pass = (stab['enforced']['descent'] == 0 and not stab['enforced']['unavailable'] and stab['offset']['descent'] == 0
                      and stab['census']['descent'] == 0 and stab['excluded']['descent'] == 0)
    base = r.metrics(r255('qualification/final-replay.json'))
    m = r.metrics(values)
    checks = r.acceptance(m, base)
    a6 = json.loads(A6_282.read_text())['information_coordinates']
    reference = s.parameter_values(STARTS['final']()[0])
    a = s.parameter_values(candidate)
    scales = {q['identity']: q['scale'] for q in a6}
    bounds = {q['identity']: q['bounds'] for q in a6}
    coordinates = {k: dict(final=reference[k], candidate=a[k], scaled=(a[k] - reference[k]) / scales[k], bounds=bounds[k],
                           on_bound=min(abs(a[k] - b) for b in bounds[k]) <= 1e-8 * max(1., abs(a[k]))) for k in scales if k in a}
    shifts = retreat_['shifts']
    for name, total in shifts.items():
        coordinates[f'reaction:{name}:enthalpy_shift_total'] = dict(candidate=total, bounds=[-10000., 10000.], on_bound=abs(abs(total) - 1e4) <= 1e-6)
    passed = stability_pass and all(c['passed'] for c in checks.values())
    summary = dict(run=run, t=retreat_['t'], cost=cost, final_cost=r.FINAL_COST, candidate_255_cost=148.5105456539468, stability=stab,
                   stability_passed=stability_pass, metrics=m, baseline_metrics=base, checks=checks, passed=passed, coordinates=coordinates,
                   on_bounds=[k for k, v in coordinates.items() if v['on_bound']])
    write(f'{run}/assessment.json', summary)
    write(f'{run}/replay.json', values)
    print(run, json.dumps({k: summary[k] for k in ('t', 'cost', 'stability_passed', 'passed', 'on_bounds')}), flush=True)


def select():
    """The #255 lower-cost rule among the two runs that pass F2."""
    runs = {x: result(f'{x}/assessment.json') for x in ('final', 'candidate')}
    passing = [x for x, v in runs.items() if v['passed']]
    chosen = min(passing, key=lambda x: runs[x]['cost']) if passing else None
    write('selected.json', dict(F2_passed=bool(passing), run=chosen, runs={x: {k: v.get(k) for k in ('t', 'cost', 'passed', 'stability_passed', 'reason')}
                                                                            for x, v in runs.items()}))


# ---------------------------------------------------------------- comparisons (Method 5) and MDEA transfer (Method 6)

POOL_266 = B / 'results/bicarbonate-carbonate-266/inputs.json'
CARBONATE_IDS = [x['id'] for x in csv.DictReader((R255 / 'evidence/final/carbonate-share.csv').open())]  # the A7 ten F_C states


def pool_and_shares(mapping):
    """#266's retained comparison records at one record: Matin pool against the Matin-Böttinger envelope at three pressures,
    the Jakobsen pool, S_pool (carbonate-pool-split) and F_C (carbonate-carbon-fraction). Compared, never fitted."""
    spec = r.bind(mapping)
    inputs = json.loads(POOL_266.read_text())
    spec.spec['templates'].update(inputs['problems'])
    spec.problems.update({k: spec.problem(k, {}) for k in inputs['problems']})
    rows = []
    for x in inputs['records']:
        p = spec.prediction(x)
        rows.append(dict(identity=x['identity'], group=x['group'], state=x['state_identity'], pressure_Pa=spec.spec['templates'][x['problem']]['P'],
                         observed=x['arguments']['observed'], status=p['status'], value=p.get('value')))
    assert all(x['status'] == 'Available' for x in rows), [x['identity'] for x in rows if x['status'] != 'Available']
    envelope = {x['identity']: x for x in inputs['reconciliation']}
    inside = {}
    for x in rows:
        if x['group'] == 'Matin2012 pool':
            e = envelope[x['state']]
            x.update(lower=e['lower'], upper=e['upper'], inside=e['lower'] <= x['value'] <= e['upper'])
            inside.setdefault(x['pressure_Pa'], []).append(x['inside'])
    ratio = lambda xs: [x['value'] / x['observed'] for x in xs if x['observed']]
    fc = [x for x in rows if x['group'] == 'Jakobsen2005 carbonate-carbon-fraction' and x['state'] in CARBONATE_IDS]
    split = [x for x in rows if x['group'] == 'Jakobsen2005 carbonate-pool-split']
    jak = [x for x in rows if x['group'] == 'Jakobsen2005 pool']
    assert len(fc) == 10
    summary = dict(matin_pool_inside={str(P): dict(inside=sum(v), total=len(v)) for P, v in sorted(inside.items())},
                   matin_pool_aard_percent_101325=100 * sum(abs(q - 1) for q in ratio([x for x in rows if x['group'] == 'Matin2012 pool' and x['pressure_Pa'] == 101325.])) / 19,
                   F_C_mean_calc_over_obs_10=sum(ratio(fc)) / len(ratio(fc)), S_pool_mean_calc_over_obs=sum(ratio(split)) / len(ratio(split)),
                   S_pool_rows_with_nonzero_observation=len(ratio(split)), jakobsen_pool_aard_percent=100 * sum(abs(q - 1) for q in ratio(jak)) / len(ratio(jak)),
                   jakobsen_011=dict(S_pool=next(x['value'] for x in split if x['state'] == 'Jakobsen2005_state_011'),
                                     F_C=next(x['value'] for x in rows if x['group'] == 'Jakobsen2005 carbonate-carbon-fraction' and x['state'] == 'Jakobsen2005_state_011')),
                   jakobsen_015_S_pool=next(x['value'] for x in split if x['state'] == 'Jakobsen2005_state_015'))
    return summary, rows


def compare():
    """Carbonate and pool comparisons at the final set (reference), the substituted final set and each refit candidate."""
    r.verify()
    sets = {'final set': s.parameter_mapping(FINAL), 'substituted final set': STARTS['final']()[0]}
    sets.update({f'refit from {x}': result(f'{x}/candidate.json') for x in ('final', 'candidate') if (OUT / x / 'candidate.json').exists()})
    out, rows = {}, {}
    for name, mapping in sets.items():
        out[name], rows[name] = pool_and_shares(mapping)
        print(name, json.dumps(out[name]), flush=True)
    # The reference reproduces #266's baseline envelope count and the A7 ten-state F_C mean (0.0727222, notebook #266).
    write('comparisons.json', dict(summary=out, rows=rows, reference_checks=dict(
        inside_266=json.loads((B / 'results/bicarbonate-carbonate-266/summary.json').read_text())['inside']['baseline'],
        F_C_A7_retained=[float(x['calc_over_obs']) for x in csv.DictReader((R255 / 'evidence/final/carbonate-share.csv').open())])))


def mdea():
    """#267 MDEA pressure and heat at fixed MDEA-specific parameters, with water-HCO3- and water-CO3^2- held at the salt laws.
    Cases: the frozen final-set R2 law, and the selected MEA refit's R2 law (only when F2 selected a candidate)."""
    import candidate_evidence_255 as ce
    r.verify()
    laws = salt_laws()
    chosen = result('selected.json')
    r2 = ce.r2_law(result(f"{chosen['run']}/candidate.json")) if chosen['run'] else None
    frozen = next(x for x in json.loads((ROOT / 'analyses/mdea_mea_workflow/inputs/probe-reaction-reference.json').read_text())['shared']
                  if x['reaction_id'] == 'R2')['engine_correlation']
    final = ce.r2_law(s.parameter_mapping(FINAL))
    assert all(abs(final[k] - frozen[k]) <= 1e-9 * max(1., abs(frozen[k])) for k in ('a', 'b', 'c', 'd', 'reference_temperature'))
    out = OUT / 'mdea-transfer'
    ce.EV = OUT  # the producer copy lands in mdea-transfer/producers/
    nodes = {ion: law_node(LAWS[ion], law['a0'], law['a1'], law['t_ref'], dict(source_id='carbonate-ions-282', locator='salt/summary.json'))
             for ion, law in laws.items() if ion != NA}
    cases = [('-salt-frozen-r2', None)] + ([('-salt-refit-r2', {k: r2[k] for k in ('a', 'b', 'c', 'd', 'e', 'f', 'reference_temperature')})] if r2 else [])
    inject = ("SALT = " + repr(nodes) + "\nR2_FROZEN = []\n\n\n"
              "def salt(document):\n"
              "    # issue 282: water-HCO3- and water-CO3^2- replaced by the salt laws; every other pair unchanged\n"
              "    for ion, node in SALT.items():\n"
              "        p = next(p for p in document['pairs'] if {p['component_id_a'], p['component_id_b']} == {ion, 'water'})\n"
              "        assert [c['family'] for c in p['coefficients']] == ['k_ij']\n"
              "        p['coefficients'] = [copy.deepcopy(node)]\n"
              "    return document\n\n\n"
              "def set_r2(law):\n"
              "    reaction = next(x for x in s.j.d.REACTIONS if x.name == 'R2')\n"
              "    R2_FROZEN[:] = R2_FROZEN or [reaction.correlation]\n"
              "    old = R2_FROZEN[0]\n"
              "    reaction.correlation = old if law is None else s.eq.ReactionLogPolynomial(**law, temperature_min=old.temperature_min, "
              "temperature_max=old.temperature_max, standard_state_id=old.standard_state_id)\n\n\n")
    held = "{p['component_id_a'],p['component_id_b']} not in ({'water','bicarbonate-anion'},{'water','carbonate-anion'})"
    old_wheel = "'/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-d5138209/epcsaft-1.0.0-cp313-cp313-manylinux_2_39_x86_64.whl'"
    producer = ce.copy_of('mdea-transfer', ROOT / 'analyses/mdea_mea_workflow/scripts/transfer_probes.py', [
        ("AN / 'results/transfer-267'", f'Path({str(out)!r})'), (old_wheel, repr(str(r.WHEEL))),
        ("'ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5'", repr(r.SHA)),
        ("def metric(records):", inject + "def metric(records):"),
        ("max_workers=min(os.cpu_count(), len(jobs),", f"max_workers=min({r.CORES}, len(jobs),"),  # agent-heavy's per-job core cap
        ("    frozen=copy.deepcopy(document); pair(frozen)['value']['magnitude']=pair(base)['value']['magnitude']\n"
         "    assert [p for p in frozen['pairs'] if {p['component_id_a'],p['component_id_b']}<=shared]==[p for p in base['pairs'] if {p['component_id_a'],p['component_id_b']}<=shared]",
         f"    same=lambda d:[p for p in d['pairs'] if {{p['component_id_a'],p['component_id_b']}}<=shared and {held}]\n    assert same(document)==same(base)"),
        ("summary=dict(shared_k=pair(document)['value']['magnitude'],", "summary=dict(shared_laws=SALT,"),
        ("for suffix,k in [('',base_k),('-kminus',base_k-.1),('-kplus',base_k+.1)]:", f"for suffix,r2 in {cases!r}:"),
        ("candidate=copy.deepcopy(document); pair(candidate)['value']['magnitude']=k", "set_r2(r2); candidate=salt(copy.deepcopy(document))"),
        ("assess(candidate,label+suffix,baseline=not suffix)", "assess(candidate,label+suffix)"),
        ("            assess(read(AN/f'results/stage2-capped/{label}/followup-bicarbonate/endpoint.json'),label+'-released')\n", ''),
        ("for label,T in [('B1',333.15),('A3',333.15),('B1',388.71)]:",
         f"for (label,T),(case,r2) in [(c,v) for c in [('B1',333.15),('A3',333.15),('B1',388.71)] for v in {cases!r}]:"),
        ("            s.setup(read(AN/f'results/stage2-capped/{label}/endpoint.json'))\n",
         "            set_r2(r2); s.setup(salt(read(AN/f'results/stage2-capped/{label}/endpoint.json')))\n"),
        ("results.append(dict(label=label,T_K=T,", "results.append(dict(label=label,case=case,T_K=T,")])
    for mode in ('pressure', 'heat'):
        ce.run('candidate', producer, [mode], record=False)
    write('mdea-transfer/r2-laws.json', dict(frozen_mdea=frozen, final_set=final, refit=r2, refit_run=chosen['run']))
    base = {(x['label'], x['T_K']): x for x in json.loads((R255 / 'evidence/mdea-transfer/heat.json').read_text()) if len(x['grid']) == 30 and x['k'] == 0.7270558477497251 and x['R2'] == 'final'}
    table = []
    for label in ('A3', 'B1'):
        reference = json.loads((R255 / f'evidence/mdea-transfer/{label}-final-k/summary.json').read_text())['pressure']
        for case, _ in cases:
            p = json.loads((out / f'{label}{case}/summary.json').read_text())['pressure']
            table += [dict(quantity='pressure AARD %', label=label, source=src, case=case.strip('-'), final_set=reference[src]['AARD_percent'],
                           value=p[src]['AARD_percent'], available=p[src]['available'], rows=p[src]['rows']) for src in ('Xiao', 'Ermatchkov')]
    for x in json.loads((out / 'heat.json').read_text()):
        if len(x['grid']) == 30:
            b = base[(x['label'], x['T_K'])]
            table.append(dict(quantity='heat J/mol (30-point grid)', label=x['label'], source=f"{x['T_K']} K", case=x['case'].strip('-'),
                              final_set=b['value'] if b['status'] == 'Available' else b['status'],
                              value=x['value'] if x['status'] == 'Available' else x['status']))
    write('mdea-transfer/summary.json', table)
    print(json.dumps(table), flush=True)


if __name__ == '__main__':
    command = sys.argv[1]
    if command in {'leverage', 'anchors', 'fit', 'assess', 'select', 'compare', 'mdea'}:
        salt_laws()
    commands = dict(salt=salt, amend=amend, scan=scan, qualify=qualify, leverage=leverage, anchors=anchors, select=select, compare=compare, mdea=mdea)
    if command in commands:
        commands[command]()
    elif command == 'fit':
        run_fit(sys.argv[2])
    elif command == 'assess':
        assess(sys.argv[2])
    else:
        raise SystemExit(__doc__)
