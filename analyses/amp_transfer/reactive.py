"""#243: calibration-only AMP model comparison; adopted-only Kundu assessment."""
import copy, gzip, hashlib, json, math, os, sys, time, itertools
from pathlib import Path
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable, relative_error_statistic

AN, t0 = Path(__file__).resolve().parent, time.perf_counter()
OUT = AN / 'results/redesign'
OUT.mkdir(parents=True, exist_ok=True)
(AN / 'inputs/redesign').mkdir(exist_ok=True)
R, TP, LIMIT_SECONDS = epcsaft.GAS_CONSTANT_J_PER_MOL_K, 313.15, 12 * 3600
AMP, H, C, W, CO2 = 'aminomethylpropanol', 'protonated-aminomethylpropanol', 'carbamate-anion', 'water', 'carbon-dioxide'
DOC = json.loads((AN / 'inputs/amp-document.json').read_text())
PURE = json.loads((AN / 'results/pure/summary.json').read_text())['frozen_endpoint']['values']
BIN = json.loads((AN / 'results/binary-dielectric.json').read_text())['binary']
SHARED_ENDPOINT = AN.parent / 'mea_parameter_bundle/results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json'  # #243 shared species; #306 rebinds
summary = dict(cpu_count=os.cpu_count(), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), runs={})
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
def weighted(spec, coords, records):  # observation-aware weighted Jacobian at the inferred (document) start
    obs, chart = [spec.observation(r) for r in records], reg.CoordinateSet()
    chart.coordinates = coords
    v = list(chart.start(spec.parameters._native, obs, spec.thermal))
    e = reg.differentiate(spec.parameters, chart.coordinates, obs, optimizer=v, holds=[], thermochemistry=spec.thermal)
    return np.sqrt([r['weight'] for r in records])[:, None] * np.reshape(e.residual_optimizer_gradient, (len(records), len(v))), v
def ln_k(law, T):
    return law['a'] + law['b'] / T + law['c'] * math.log(T / law['reference_temperature']) + law['d'] * T

def apply_laws(spec, chart, parameters):  # completed fitted laws and fitted parameters into every declared problem
    laws = {r['name']: r['correlation'] for g in spec.fitted_reactions(chart).values() for r in g}
    for problem in spec.problems.values():
        for reaction in problem.reactions or []:
            reaction.correlation = eq.ReactionLogPolynomial(**laws[reaction.name])
    spec.model = epcsaft.Mixture(parameters, thermochemistry=spec.thermal)
    return laws
def make_spec(run, document, coords, law=None, seconds=1200, declarations='declarations.toml'):
    text = (AN / declarations).read_text()
    if law is not None:
        assert '"a" = 11.555, "b" = -2546.2' in text
        text = text.replace('"a" = 11.555, "b" = -2546.2', f'"a" = {law["a"]}, "b" = {law["b"]}')
    common = record(f'inputs/redesign/{run}-declarations.toml', text)
    start = record(f'inputs/redesign/{run}-start.json', json.dumps(document, indent=1) + '\n')
    chart = record(f'inputs/redesign/{run}-coordinates.json', json.dumps(coords, indent=1) + '\n')
    caloric = f'{{path = "../solvent_specification_mea/inputs/caloric.json", sha256 = "{hashlib.sha256((AN.parent / "solvent_specification_mea/inputs/caloric.json").read_bytes()).hexdigest()}"}}'
    record(f'{run}.toml', f'schema = "solvent-specification-1"\ndeclarations = {common}\nstart = {start}\nendpoint = {start}\ncoordinates = {chart}\ncaloric = {caloric}\n'
           f'phase_states = {{path = "inputs/no-phase-states.json", sha256 = "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"}}\n'
           f'optimizer = {{maximum_iterations = 60, function_tolerance = 1e-10, parameter_tolerance = 1e-10, gradient_tolerance = 1e-8, maximum_elapsed_time_seconds = {seconds}}}\n')
    return SolventSpecification(AN / f'{run}.toml', parameter='start')


def fit_endpoint(run, spec):
    started = time.perf_counter()
    result, report, fitted = spec.fit()
    pre, rows = {}, spec.inputs['observations']['fitted']
    fitted = epcsaft.Parameters.from_mapping(epcsaft.parameters.document_mapping(fitted))
    laws = apply_laws(spec, result.chart, fitted)
    replay = [spec.prediction(r) for r in rows]
    w = [math.sqrt(r['weight']) * p['residual'] if p.get('status') == 'Available' else math.nan for r, p in zip(rows, replay)]
    cost = math.fsum(0.5 * x * x for x in w)
    groups = {g: math.fsum(0.5 * x * x for x, r in zip(w, rows) if r['group'] == g) for g in dict.fromkeys(r['group'] for r in rows)}
    pre.update(status=result.status, usable=result.usable, message=result.message, iterations=result.iterations, initial_cost=result.initial_cost, cost=result.final_cost,
               fit_seconds=time.perf_counter() - started, physical=list(result.chart.physical), optimizer=list(report['optimizer']), active_bounds=list(result.covariance.active_bounds), groups=groups,
               endpoint_singular_values=list(result.covariance.singular_values), replay_cost_relative=abs(cost / result.final_cost - 1), carbamate_law=laws['carbamate-hydrolysis'],
               delta=laws['carbamate-hydrolysis']['a'] - 11.555, weighted_residuals=w, endpoint_s_min_over_s_max=min(result.covariance.singular_values) / max(result.covariance.singular_values), nmr_rms=math.sqrt(np.mean([(p['value'] - p['observed']) ** 2 for p in replay if p['group'] == 'nmr'])))
    pre['calibration_available'] = all(p.get('status') == 'Available' and math.isfinite(p['value']) and p.get('requested_tolerance_met') is True for p in replay)
    pre['admissible'] = bool(pre['calibration_available'] and result.status == 'converged' and result.usable and not pre['active_bounds'] and pre['replay_cost_relative'] <= 1e-8 and not math.isnan(cost) and pre['endpoint_s_min_over_s_max'] >= 1e-4)
    pre['replay_rows_max_difference'] = max(abs(x - y) for x, y in zip(w, report['weighted_residuals']))
    write(f'{run}-fit.json', dict(report=report, replay=replay))
    pre['independent_physical'] = [q['origin'] + q['scale'] * v for q, v in zip(spec.inputs['coordinates'], report['optimizer'])]
    pre['covariance'] = {k: jsonable(getattr(result.covariance, k)) for k in ('status', 'assumption', 'optimizer', 'physical', 'variance_factor')}
    pre['law'] = laws['carbamate-hydrolysis']
    pre['endpoint'] = f'inputs/redesign/{run}-endpoint.json'
    (AN / pre['endpoint']).write_text(json.dumps(epcsaft.parameters.document_mapping(fitted), indent=1) + '\n')
    return pre, fitted, replay

def preflight(spec):
    rows = spec.inputs['observations']['fitted']
    J, v = weighted(spec, spec.coordinates(), rows)
    _, sv, vt = np.linalg.svd(J, full_matrices=False)
    shared_ids = (W, CO2, 'bicarbonate-anion', 'carbonate-anion', 'hydronium-cation', 'hydroxide-anion')
    same = lambda x: [c for c in x['components'] if c['component_id'] in shared_ids]
    pairs = lambda x: [p for p in x['pairs'] if {p['component_id_a'], p['component_id_b']} <= set(shared_ids)]
    mea = json.loads(SHARED_ENDPOINT.read_text())
    unchanged = same(spec.inputs['start']) == same(mea) and pairs(spec.inputs['start']) == pairs(mea)
    spec.species_mapping(spec.spec['chemistry']['reactions'])
    row = next(r for r in rows if r['group'] == 'loaded-pressure')
    prob = spec.problems[row['problem']]
    state = eq.solve_equilibrium(spec.model, prob)
    laws = {r['name']: r['correlation'] for r in spec.spec['chemistry']['reactions']['aqueous']}
    lnq = max(abs(a.log_quotient - ln_k(laws[prob.reactions[a.reaction_index].name], prob.T)) for a in eq.reaction_activities(spec.model, state) if a.phase_index == 0)
    residual = max(map(abs, state.residuals))
    return dict(weighted_jacobian=J.tolist(), singular_values=sv.tolist(), right_vectors=vt.tolist(), start_optimizer=v,
                column_norms=np.linalg.norm(J, axis=0).tolist(), s_min_over_s_max=float(sv[-1]/sv[0]), shared_unchanged=unchanged,
                equilibrium_residual=residual, max_lnQ_minus_lnK=lnq,
                passed=bool(unchanged and state.requested_tolerance_met and residual <= 1e-10 and lnq <= 1e-8 and sv[-1]/sv[0] >= 1e-4))


def calibration_checks(pre, spec, replay, slope, H0):
    coords, x = spec.inputs['coordinates'], pre['independent_physical']
    pre['near_bounds'] = sum(min(v-q['bounds'][0], q['bounds'][1]-v)/(q['bounds'][1]-q['bounds'][0]) <= .01 for q, v in zip(coords, x))
    pre['interior'] = all(q['bounds'][0] < v < q['bounds'][1] for q, v in zip(coords, x))
    loaded = [r for r in replay if r['group'] == 'loaded-pressure']
    errors = [100*abs(r['value']/r['observed']-1) for r in loaded]
    pre['pressure'] = dict(mean_percent=float(np.mean(errors)), max_percent=max(errors),
        isotherms={str(T): relative_error_statistic([r for r in loaded if round(float(r['row']['T_K'])) == T]) for T in (313,333,353)})
    pre['binary'] = [r for r in replay if r['group'] == 'binary']
    pre['total_shift_J_mol'] = H0 + (x[-1] if slope else 0.)
    pre['delta'] = next(v for q,v in zip(coords,x) if q.get('coefficient') == 'a') - 11.555 - H0/(R*TP)
    pre['effective_enthalpy_J_mol'] = R*2546.2 + pre['total_shift_J_mol']
    pre['slope_identified'] = not slope
    if slope and pre['covariance']['status'] == 'available':
        cov = np.reshape(pre['covariance']['optimizer'], (len(x), len(x)))
        sd = np.sqrt(np.diag(cov)); correlation = cov[-1]/(sd[-1]*sd)
        se = float(sd[-1]*coords[-1]['scale'])
        factor = pre['covariance']['variance_factor']
        pre['slope_uncertainty'] = dict(standard_error_J_mol=se, b_standard_error_K=se/R,
            variance_scaled_error_J_mol=se*math.sqrt(factor) if factor is not None else None,
            correlations=correlation[:-1].tolist(), conditional_on='unit residual variance; fixed model, group weights; local linearization')
        pre['slope_identified'] = bool(se <= abs(pre['effective_enthalpy_J_mol']) and max(abs(correlation[:-1])) <= .95)
    pre['admissible'] = bool(pre['admissible'] and pre['interior'] and pre['replay_rows_max_difference'] <= 1e-8 and pre['nmr_rms'] <= .006
        and max([pre['pressure']['mean_percent'], *pre['pressure']['isotherms'].values()]) <= 10 and max(errors) <= 30 and pre['slope_identified'])


def compare_starts(runs):
    comparisons = {}
    for first, a in runs.items():
        second = first[:-1] + '2'
        if not first.endswith('1') or 'cost' not in a or 'cost' not in runs.get(second, {}):
            continue
        b, vectors, predictions = runs[second], [], []
        for run, point in ((first, a), (second, b)):
            qs = json.loads((AN / f'inputs/redesign/{run}-coordinates.json').read_text())
            physical = point.get('independent_physical', [q['origin']+q['scale']*v for q,v in zip(qs,point['optimizer'])])
            vectors.append([(point['delta'] if q.get('coefficient') == 'a' else point['total_shift_J_mol'] if q.get('kind') == 'reaction_enthalpy_shift' else x)/q['scale'] for q,x in zip(qs,physical)])
            path = AN / point.get('reused_from', f'results/redesign/{run}-fit.json')
            if not path.exists():
                path = path.with_suffix(path.suffix + '.gz')
            data = json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())
            predictions.append(data['report']['predictions'])
        comparisons[first[:-2]] = dict(first=first, second=second, rows=len(predictions[0]), absolute_cost_difference=abs(a['cost']-b['cost']),
            max_scaled_coordinate_difference=max(abs(x-y) for x,y in zip(*vectors)), max_relative_prediction_difference=max(abs(x/y-1) for x,y in zip(*predictions)))
    return comparisons


if __name__ == '__main__':
    from pinned_engine import SHA256
    summary['wheel_sha256'] = SHA256
    specs, best = {}, {}
    for setting, cation, slope, second in itertools.product((1,2), ('A','B'), (False,True), (False,True)):
        run = f'redesign-{setting}-{cation}-{"slope" if slope else "fixed"}-{1+second}'
        print(run, flush=True)
        if time.perf_counter()-t0 >= LIMIT_SECONDS:
            stop('12 hour budget reached; incomplete assessment')
        d, qs, H0, baseline = variant(cation, second), coordinates(cation), 0., None
        if setting == 2:
            for c in d['components']:
                if c['component_id'] == C:
                    for q in c['coefficients']:
                        if q['family'] in ('segment_diameter','debye_huckel_diameter','packing_diameter'):
                            q['value']['magnitude'] = 4.866108647520244 * (.88 if q['family'] == 'packing_diameter' else 1.)
            qs[4] = dict(targets=[['k_ij',[AMP,CO2],1.]], origin=0., scale=.05, bounds=[-.5,.5])
            qs[6] = dict(targets=[['k_ij',[C,W],1.]], origin=-.0036580495327475336, scale=.05, bounds=[-.5,.5])
        if slope:
            qs.append(dict(kind='reaction_enthalpy_shift', name='carbamate-hydrolysis', pivot_temperature=TP, origin=0., scale=1000., bounds=[-5000.,5000.]))
        try:
            if cation == 'B':
                restricted = copy.deepcopy(qs)
                if setting == 1:
                    restricted.pop(4)
                initial = make_spec(run+'-initial', d, restricted, seconds=600)
                start_diagnostic = preflight(initial)
                init, fitted, rows = fit_endpoint(run+'-initial', initial)
                write(run+'-initial.json', dict(start=start_diagnostic, endpoint=init))
                if init['status'] != 'converged' or not init['usable'] or init['replay_cost_relative'] > 1e-8:
                    summary['runs'][run] = dict(initialization=init, disposition='initialization unavailable; Diagnose')
                    write('summary.json', summary)
                    continue
                d, baseline = epcsaft.parameters.document_mapping(fitted), init['law']
                H0 = init['independent_physical'][-1] if slope else 0.
                for q in qs:
                    if q.get('coefficient') == 'a':
                        q['origin'] += H0/(R*TP)
                        q['bounds'] = [v+H0/(R*TP) for v in q['bounds']]
                    if q.get('kind') == 'reaction_enthalpy_shift':
                        q['bounds'] = [v-H0 for v in q['bounds']]
            spec = specs[run] = make_spec(run, d, qs, baseline)
            if cation == 'B':
                restart = [spec.prediction(r) for r in spec.inputs['observations']['fitted']]
                restart_error = abs(math.fsum(.5*r['weight']*p['residual']**2 for r,p in zip(spec.inputs['observations']['fitted'], restart))/init['cost']-1)
                assert restart_error <= 1e-8, 'B restart changed initialization law before fitting'
            start = preflight(spec)
            if cation == 'B':
                start['initialization_cost_relative'] = restart_error
            summary['runs'][run] = pre = dict(start=start, setting=setting, cation=cation, fitted_slope=slope)
            write('summary.json', summary)
            if not start['passed']:
                pre['disposition'] = 'full start gate failed; Diagnose'
                continue
            if setting == 1 and cation == 'A' and not slope:
                old = json.loads((AN/'results/reactive/summary.json').read_text())['runs'][f'A-{1+second}']
                pre.update(old, reused_from=f'results/reactive/A-{1+second}-fit.json')
                pre['disposition'] = 'historical endpoint on two bounds; not adopted'
                continue
            endpoint, fitted, replay = fit_endpoint(run, spec)
            pre.update(endpoint)
            if cation == 'B':
                pre['initialization_cost_relative'] = abs(pre['initial_cost']/init['cost']-1)
                assert pre['initialization_cost_relative'] <= 1e-8, 'B restart changed initialization law'
            calibration_checks(pre, spec, replay, slope, H0)
            if pre['admissible']:
                spec.parameter_sha256 = hashlib.sha256((AN/pre['endpoint']).read_bytes()).hexdigest()
                phases = [spec.phase(dict(identity=r['identity'], problem=r['problem'], endpoint_sha256=spec.parameter_sha256), spec.spec['phase_policy']) for r in spec.inputs['observations']['fitted']]
                write(run+'-calibration-phases.json', phases)
                pre['admissible'] = all(not(p.get('dense') or p.get('ambiguous') or p.get('unresolved')) for p in phases)
                if pre['admissible']:
                    best[run] = pre
            print(run, 'cost', pre['cost'], 'NMR RMS', pre['nmr_rms'], 'admissible', pre['admissible'], flush=True)
        except Exception as error:
            summary['runs'].setdefault(run, {}).update(exception=type(error).__name__, message=str(error), disposition='execution failure; Diagnose')
            print(run, type(error).__name__, str(error), flush=True)
        finally:
            write('summary.json', summary)
    summary['start_comparisons'] = compare_starts(summary['runs'])
    if not best:
        stop('no adopted endpoint; Kundu not scored; calibration evidence requires diagnosis')
    selected = min(best, key=lambda r: (best[r]['near_bounds'], best[r]['cost'], best[r]['fitted_slope'], best[r]['setting'], best[r]['cation'], r))
    summary.update(selected=selected, adopted=dict(run=selected, parameter_sha256=specs[selected].parameter_sha256, law=best[selected]['law'], law_sha256=hashlib.sha256(json.dumps(best[selected]['law'], sort_keys=True).encode()).hexdigest()))
    write('adopted.json', summary['adopted'])
    best = {selected: selected}
    policy = specs[selected].spec['phase_policy']
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
                                nmr_limit=0.006, phase_clean=not (s['phase']['dense'] or s['phase']['unresolved'] or s['phase']['ambiguous']))
    stop('assessed')
