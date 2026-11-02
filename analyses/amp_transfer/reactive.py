"""#242 stage 3b: AMP reactive fits (cations A, B; two starts each), gates, calibration selection and Kundu score (design §§2, 5-7)."""
import copy, gzip, hashlib, json, math, os, sys, time
from pathlib import Path
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from pinned_engine import SHA256
from MEA.solvent_specification import SolventSpecification, jsonable, relative_error_statistic

AN, t0 = Path(__file__).resolve().parent, time.perf_counter()
OUT = AN / 'results/reactive'
OUT.mkdir(parents=True, exist_ok=True)
AMP, H, C, W, CO2 = 'aminomethylpropanol', 'protonated-aminomethylpropanol', 'carbamate-anion', 'water', 'carbon-dioxide'
DOC = json.loads((AN / 'inputs/amp-document.json').read_text())
PURE = json.loads((AN / 'results/pure/summary.json').read_text())['frozen_endpoint']['values']
BIN = json.loads((AN / 'results/binary-dielectric.json').read_text())['binary']
summary = dict(wheel_sha256=SHA256, cpu_count=os.cpu_count(), runs={})
def write(name, value):  # gzip above 5 MB
    data = (json.dumps(jsonable(value), indent=1, default=float) + '\n').encode()
    (OUT / (name + '.gz' if len(data) > 5e6 else name)).write_bytes(gzip.compress(data, mtime=0) if len(data) > 5e6 else data)
def stop(disposition):
    summary.update(disposition=disposition, wall_seconds=time.perf_counter() - t0)
    write('summary.json', summary)
    sys.exit(0 if disposition == 'assessed' else disposition)
def record(path, text):
    (AN / path).write_text(text)
    return f'{{path = "{path}", sha256 = "{hashlib.sha256(text.encode()).hexdigest()}"}}'

def variant(cation, second):  # design §2: A sphere (document default) or B charged molecule; start 2 moves the cation-water pair
    d = copy.deepcopy(DOC)
    if cation == 'B':
        h, top = next(c for c in d['components'] if c['component_id'] == H), d['topology']
        h['fixed']['charged_molecule_ion'] = dict(value=dict(magnitude=1, unit='dimensionless'), provenance=dict(source_id='design-842bc73', locator='design §2 cation B'))
        h['coefficients'] = [i for i in h['coefficients'] if i['family'] != 'packing_diameter']
        for i in h['coefficients']:
            i['value']['magnitude'] = dict(segment_count=PURE['m'], segment_diameter=PURE['sigma'], debye_huckel_diameter=PURE['sigma']).get(i['family'], i['value']['magnitude'])
        amp_sites = [s for s in top['sites'] if s['component_id'] == AMP]
        amp_edges = [e for e in top['edges'] if AMP in (e['endpoint_a']['component_id'], e['endpoint_b']['component_id'])]  # self, then two with water
        top['sites'] += json.loads(json.dumps(amp_sites).replace(AMP, H))
        own = json.loads(json.dumps(amp_edges[0]).replace(AMP, H))
        own['energy_over_k']['value']['magnitude'] = 0.0  # zero cation self-association energy, AMP association volume
        water = json.dumps(amp_edges[1:])
        top['edges'] += [own, *json.loads(water.replace(AMP, H)), *json.loads(water.replace(AMP, '@').replace('water', AMP).replace('@', H))]
        top['no_cross_association'] += json.loads(json.dumps(top['no_cross_association']).replace(AMP, H))
    for p in d['pairs'] if second else []:
        if {p['component_id_a'], p['component_id_b']} == {H, W}:
            for i in p['coefficients']:
                i['value']['magnitude'] = 0.1 if i['family'] == 'k_ij' else 100.0
    return d
def coordinates(cation):  # design §6: eight coordinates; tied diameters are one coordinate
    tie = lambda cid: [['segment_diameter', cid, 1.0], ['debye_huckel_diameter', cid, 1.0]] + ([] if cation == 'B' and cid == H else [['packing_diameter', cid, 0.88]])
    q = lambda fam, pair, origin, scale, bounds: dict(targets=[[fam, pair, 1.0]], origin=origin, scale=scale, bounds=bounds)
    return [q('k_ij', [AMP, W], BIN['k_ref'], 0.05, [-0.5, 0.5]), q('k_ij_reciprocal_temperature_slope', [AMP, W], BIN['slope_K'], 100.0, [-1000.0, 1000.0]),
            q('k_ij', [H, W], 0.0, 0.05, [-0.5, 0.5]), q('k_ij_reciprocal_temperature_slope', [H, W], 0.0, 100.0, [-1000.0, 1000.0]), q('k_ij', [H, CO2], 0.0, 0.05, [-0.5, 0.5]),
            dict(targets=tie(H), origin=5.3 if cation == 'A' else PURE['sigma'], scale=0.25, bounds=[4.5, 6.5] if cation == 'A' else [3.0, 4.2]),
            dict(targets=tie(C), origin=5.3, scale=0.25, bounds=[4.5, 6.5]),
            dict(kind='reaction_coordinate', name='carbamate-hydrolysis', coefficient='a', origin=11.555, scale=1.0, bounds=[8.555, 13.555])]
def weighted(spec, coords, records, extra=()):  # observation-aware weighted Jacobian at the inferred (document) start
    obs, chart = [spec.observation(r) for r in records], reg.CoordinateSet()
    chart.coordinates = coords + list(extra)
    v = list(chart.start(spec.parameters._native, obs, spec.thermal))
    e = reg.differentiate(spec.parameters, chart.coordinates, obs, optimizer=v, holds=[], thermochemistry=spec.thermal)
    return np.sqrt([r['weight'] for r in records])[:, None] * np.reshape(e.residual_optimizer_gradient, (len(records), len(v))), v
def ln_k(law, T):
    return law['a'] + law['b'] / T + law['c'] * math.log(T / law['reference_temperature']) + law['d'] * T

# Preflight on all four runs before any fit: balance, shared records, ln Q = ln K at one loaded state, rank gate, CO2 column norms.
MEA = json.loads((AN.parent / 'solvent_specification_mea/inputs/endpoint.json').read_text())
shared = {c['component_id']: c for c in MEA['components'] if c['component_id'] in (W, CO2, 'bicarbonate-anion', 'carbonate-anion', 'hydronium-cation', 'hydroxide-anion')}
specs = {}
for run in ('A-1', 'A-2', 'B-1', 'B-2'):
    cation, second = run[0], run.endswith('2')
    started = time.perf_counter()
    start = record(f'inputs/{run}-start.json', json.dumps(variant(cation, second), indent=1) + '\n')
    coords = record(f'inputs/{cation}-coordinates.json', json.dumps(coordinates(cation), indent=1) + '\n')
    common = record('declarations.toml', (AN / 'declarations.toml').read_text())
    caloric = '{path = "../solvent_specification_mea/inputs/caloric.json", sha256 = "71c0f65204de5f10a22099db8ee6a939895bf280c725292e2cc46c0b1ebe9ef1"}'
    record(f'{run}.toml', f'schema = "solvent-specification-1"\ndeclarations = {common}\nstart = {start}\nendpoint = {start}\ncoordinates = {coords}\ncaloric = {caloric}\n'
           f'phase_states = {record("inputs/no-phase-states.json", "[]\n")}\noptimizer = {{maximum_iterations = 60, function_tolerance = 1e-10, parameter_tolerance = 1e-10, '
           'gradient_tolerance = 1e-8, maximum_elapsed_time_seconds = 4500.0}\n')
    spec = specs[run] = SolventSpecification(AN / f'{run}.toml', parameter='start')
    fitted, loaded = spec.inputs['observations']['fitted'], [r for r in spec.inputs['observations']['fitted'] if r['group'] == 'loaded-pressure']
    spec.species_mapping(spec.spec['chemistry']['reactions'])  # element and charge balance, caloric coverage
    state = eq.solve_equilibrium(spec.model, spec.problems[loaded[0]['problem']])
    laws = {r['name']: r['correlation'] for r in spec.spec['chemistry']['reactions']['aqueous']}
    problem = spec.problems[loaded[0]['problem']]
    lnq = [abs(a.log_quotient - ln_k(laws[problem.reactions[a.reaction_index].name], problem.T)) for a in eq.reaction_activities(spec.model, state) if a.phase_index == 0]  # liquid; the vapor holds no ions
    J, v0 = weighted(spec, spec.coordinates(), fitted)
    _, s, vt = np.linalg.svd(J, full_matrices=False)
    co2 = weighted(spec, spec.coordinates(), loaded, [reg.coordinate(spec.parameters, [('k_ij', (AMP, CO2), 1.0)], origin=0.0, scale=0.05, bounds=(-0.5, 0.5))])[0]
    summary['runs'][run] = pre = dict(rows=len(fitted), inferred_optimizer=v0, shared_records_unchanged=all(c == shared[c['component_id']] for c in spec.inputs['start']['components'] if c['component_id'] in shared),
        max_lnQ_minus_lnK=max(lnq), equilibrium_residual=max(map(abs, state.residuals)), singular_values=s.tolist(), right_vectors=vt.tolist(), weighted_jacobian=J.tolist(), s_min_over_s_max=float(s[-1] / s[0]),
        column_norms=np.linalg.norm(J, axis=0).tolist(), co2_columns=dict(AMPH_CO2=float(np.linalg.norm(co2[:, 4])), AMP_CO2=float(np.linalg.norm(co2[:, 8]))), preflight_seconds=time.perf_counter() - started)
    pre['co2_columns']['ratio'] = pre['co2_columns']['AMP_CO2'] / pre['co2_columns']['AMPH_CO2'] if pre['co2_columns']['AMPH_CO2'] else None
    pre['passed'] = bool(pre['shared_records_unchanged'] and max(lnq) <= 1e-8 and pre['s_min_over_s_max'] >= 1e-4 and min(pre['column_norms']) > 0)
    write('summary.json', summary)
if not all(summary['runs'][r]['passed'] for r in specs):
    stop('preflight failed (rank gate, ln Q = ln K, shared records or start): return to Design with the matrices')

def apply_laws(spec, chart, parameters):  # completed fitted laws and fitted parameters into every declared problem
    laws = {r['name']: r['correlation'] for g in spec.fitted_reactions(chart).values() for r in g}
    for problem in spec.problems.values():
        for reaction in problem.reactions or []:
            reaction.correlation = eq.ReactionLogPolynomial(**laws[reaction.name])
    spec.model = epcsaft.Mixture(parameters, thermochemistry=spec.thermal)
    return laws
for run, spec in specs.items():
    started = time.perf_counter()
    result, report, fitted = spec.fit()
    pre, rows = summary['runs'][run], spec.inputs['observations']['fitted']
    laws = apply_laws(spec, result.chart, fitted)
    replay = [spec.prediction(r) for r in rows]
    w = [math.sqrt(r['weight']) * p['residual'] if p.get('status') == 'Available' else math.nan for r, p in zip(rows, replay)]
    cost = math.fsum(0.5 * x * x for x in w)
    groups = {g: math.fsum(0.5 * x * x for x, r in zip(w, rows) if r['group'] == g) for g in dict.fromkeys(r['group'] for r in rows)}
    pre.update(status=result.status, usable=result.usable, message=result.message, iterations=result.iterations, initial_cost=result.initial_cost, cost=result.final_cost,
               fit_seconds=time.perf_counter() - started, physical=list(result.chart.physical), active_bounds=list(result.covariance.active_bounds), groups=groups,
               endpoint_singular_values=list(result.covariance.singular_values), replay_cost_relative=abs(cost / result.final_cost - 1), carbamate_law=laws['carbamate-hydrolysis'],
               delta=laws['carbamate-hydrolysis']['a'] - 11.555, nmr_rms=math.sqrt(np.mean([(p['value'] - p['observed']) ** 2 for p in replay if p['group'] == 'nmr'])))
    pre['admissible'] = bool(result.status == 'converged' and result.usable and not pre['active_bounds'] and pre['replay_cost_relative'] <= 1e-8 and not math.isnan(cost))
    write(f'{run}-fit.json', dict(report=report, replay=replay))
    (AN / f'inputs/{run}-endpoint.json').write_text(json.dumps(epcsaft.parameters.document_mapping(fitted), indent=1) + '\n')
    write('summary.json', summary)

# Each variant keeps its lower-cost admissible start; select on calibration cost (ties within 1 % prefer A), then score both.
best = {}
for cation in 'AB':
    pair = [summary['runs'][f'{cation}-{i}'] for i in (1, 2)]
    ok = [(f'{cation}-{i}', p) for i, p in zip((1, 2), pair) if p['admissible']]
    summary[f'{cation}_starts'] = dict(cost_difference=pair[0]['cost'] - pair[1]['cost'], max_physical_difference=max(abs(a - b) for a, b in zip(pair[0]['physical'], pair[1]['physical'])))
    if ok:
        best[cation] = min(ok, key=lambda x: x[1]['cost'])[0]
if not best:
    stop('no admissible reactive endpoint')
selected = 'A' if 'A' in best and ('B' not in best or summary['runs'][best['A']]['cost'] <= 1.01 * summary['runs'][best['B']]['cost']) else 'B'
summary.update(best=best, selected=selected)
policy = specs['A-1'].spec['phase_policy']
for cation, run in best.items():
    spec = specs[run]  # already carries its fitted model and laws
    comparisons = [spec.prediction(r) for r in spec.inputs['observations']['comparisons']]
    kundu = [p for p in comparisons if p['group'] == 'kundu']
    phases = [spec.phase(dict(identity=r['identity'], problem=r['problem'], endpoint_sha256=spec.parameter_sha256), policy)
              for r in spec.inputs['observations']['fitted'] + spec.inputs['observations']['comparisons'] if 'problem' in r]
    envelope = []
    for r in [r for r in spec.inputs['observations']['comparisons'] if r['group'] == 'kundu']:  # alpha +/- 2 % alpha, no refit
        base = spec.problems[r['problem']]
        values = []
        for f in (0.98, 1.02):
            problem = copy.deepcopy(base)
            problem.feed.values[CO2] = f * base.feed.values[CO2]
            p = reg.predict(spec.model, reg.observation(spec.parameters, 'partial_pressure', problem, observed=r['arguments']['observed'], form='log_ratio', phase='V', species=[CO2]))
            values.append(p.value if p.status.name == 'Available' else None)
        envelope.append(dict(identity=r['identity'], low_alpha=values[0], high_alpha=values[1]))
    summary[cation] = dict(run=run, kundu_E_p=relative_error_statistic(kundu), kundu_available=sum(p['status'] == 'Available' for p in kundu),
        kundu_rows=[dict(identity=p['identity'], table=p['row']['table'], T=p['row']['T_K'], observed=p['observed'], predicted=p.get('value'), status=p['status'],
                         log_ratio=math.log(p['value'] / p['observed']) if p.get('value') else None) for p in kundu],
        comparisons={g: dict(rows=sum(p['group'] == g for p in comparisons), available=sum(p['group'] == g and p['status'] == 'Available' for p in comparisons),
                             mean_abs_percent=relative_error_statistic([p for p in comparisons if p['group'] == g and p['status'] == 'Available']))
                     for g in dict.fromkeys(p['group'] for p in comparisons)},
        phase=dict(states=len(phases), dense=[p['identity'] for p in phases if p.get('dense')], unresolved=[p['identity'] for p in phases if p.get('unresolved')],
                   ambiguous=[p['identity'] for p in phases if p.get('ambiguous')]), alpha_envelope=envelope)
    write(f'{cation}-assessment.json', dict(comparisons=comparisons, phases=phases))
s = summary[selected]
summary['falsifier'] = dict(variant=selected, E_p=s['kundu_E_p'], limit=30.0, all_rows=s['kundu_available'] == 51, nmr_rms=summary['runs'][best[selected]]['nmr_rms'],
                            nmr_limit=0.006, phase_clean=not (s['phase']['dense'] or s['phase']['unresolved']))
stop('assessed')
