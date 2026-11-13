"""#317 design steps 4-6: forms A and B, two starts each, D7 checks, frozen selection; held-out scoring after the freeze.

Run with agent-heavy env OMP_NUM_THREADS=1 uv run --no-sync python analyses/dea_transfer/reactive.py fit|score
"""
import copy, csv, hashlib, json, math, sys, time, tomllib
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from pinned import AN, ROOT, MEA, DEA, H, C, W, CO2, SHARED, verify_wheel, save
from MEA.solvent_specification import SolventSpecification, jsonable

R, TP = epcsaft.GAS_CONSTANT_J_PER_MOL_K, 313.15
# Owner decision 2026-11-12: the design's form-B start 2 (DEAH+-water k = -0.5) has no bubble point at Lawson row 7
# (results/fit-runs/B-2-k-0.5-start-rows.json); form B start 2 uses -0.2 with the other start-2 offsets unchanged.
B2_HW = -0.2
A0, B0 = 11.789235676129515, -4100.9040506223955  # Aroua 1997 Eq. 14 inverse (declarations.toml)
DECL = (AN / 'declarations.toml').read_text()
ln_k = lambda law, T: law['a'] + law['b'] / T + law['c'] * math.log(T / law['reference_temperature']) + law['d'] * T
sha = lambda path: hashlib.sha256((AN / path).read_bytes()).hexdigest()
ref = lambda path: dict(path='../' + path, sha256=sha(path))  # specification files live in runs/
toml = lambda d: '{' + ', '.join(f'{k} = {json.dumps(v)}' for k, v in d.items()) + '}'


def variant(form, start):  # D2 form A record, form B charged chain cation; start 2 moves the two ion-water pairs (D5)
    d = json.loads((AN / 'inputs/dea-A.json').read_text())
    if form == 'B':
        h, top, dea = next(c for c in d['components'] if c['component_id'] == H), d['topology'], next(c for c in d['components'] if c['component_id'] == DEA)
        pure = {i['family']: i['value']['magnitude'] for i in dea['coefficients']}
        h['fixed']['charged_molecule_ion'] = dict(value=dict(magnitude=1, unit='dimensionless'), provenance=dict(source_id='issue-317', locator='design D2 form B'))
        h['coefficients'] = [i for i in h['coefficients'] if i['family'] != 'packing_diameter']
        for i in h['coefficients']:
            i['value']['magnitude'] = dict(segment_count=pure['segment_count'], segment_diameter=pure['segment_diameter'], debye_huckel_diameter=pure['segment_diameter'],
                                           dispersion_energy_over_k=pure['dispersion_energy_over_k']).get(i['family'], i['value']['magnitude'])
        edges = [e for e in top['edges'] if DEA in (e['endpoint_a']['component_id'], e['endpoint_b']['component_id'])]  # self, then two with water
        top['sites'] += json.loads(json.dumps([s for s in top['sites'] if s['component_id'] == DEA]).replace(DEA, H))
        own = json.loads(json.dumps(edges[0]).replace(DEA, H))
        own['energy_over_k']['value']['magnitude'] = 0.0  # zero cation self-association energy, DEA association volume
        water = json.dumps(edges[1:])
        top['edges'] += [own, *json.loads(water.replace(DEA, H)), *json.loads(water.replace(DEA, '@').replace(W, DEA).replace('@', H))]
        top['no_cross_association'] += json.loads(json.dumps(top['no_cross_association']).replace(DEA, H))
    for p in d['pairs'] if start == 2 else []:
        ids = {p['component_id_a'], p['component_id_b']}
        if ids in ({H, W}, {C, W}):
            next(i for i in p['coefficients'] if i['family'] == 'k_ij')['value']['magnitude'] = (B2_HW if form == 'B' else -0.5) if H in ids else 0.0
    return d


def coordinates(start, form):  # D5: four coordinates; start 2 moves ln K(313.15 K) by +0.35 and the enthalpy by -11 kJ/mol inside the same physical limits
    s = -11000.0 if start == 2 else 0.0
    a = A0 + (0.35 if start == 2 else 0.0) + s / (R * TP)
    q = lambda pair, origin: dict(targets=[['k_ij', pair, 1.0]], origin=origin, scale=0.05, bounds=[-1.0, 1.0])
    return [q([H, W], (B2_HW if form == 'B' else -0.5) if start == 2 else 0.0), q([C, W], 0.0 if start == 2 else -0.013004788810687472),
            dict(kind='reaction_coordinate', name='carbamate-hydrolysis', coefficient='a', origin=a, scale=1.0, bounds=[A0 - 3 + s / (R * TP), A0 + 3 + s / (R * TP)]),
            dict(kind='reaction_enthalpy_shift', name='carbamate-hydrolysis', pivot_temperature=TP, origin=0.0, scale=1000.0, bounds=[-30000.0 - s, 10000.0 - s])], dict(a=a, b=B0 - s / R)


def make_spec(run, document, coords, law, parameter='start', caloric='inputs/caloric.json'):
    text = DECL.replace(f'"a": {A0}, "b": {B0}'.replace(': ', ' = '), f'"a" = {law["a"]}, "b" = {law["b"]}')
    assert text != DECL or law == dict(a=A0, b=B0)
    text = text.replace('"path" = "inputs/', '"path" = "../inputs/')  # dataset packets resolve against runs/
    paths = {k: f'inputs/runs/{run}-{k}' for k in ('declarations.toml', 'document.json', 'coordinates.json')}
    for key, value in zip(paths.values(), (text, json.dumps(document, indent=1) + '\n', json.dumps(coords, indent=1) + '\n')):
        (AN / key).parent.mkdir(parents=True, exist_ok=True)
        (AN / key).write_text(value)
    fields = dict(declarations=ref(paths['declarations.toml']), start=ref(paths['document.json']), endpoint=ref(paths['document.json']), coordinates=ref(paths['coordinates.json']),
                  caloric=ref(caloric), phase_states=ref('inputs/no-phase-states.json'),
                  optimizer=dict(maximum_iterations=60, function_tolerance=1e-10, parameter_tolerance=1e-10, gradient_tolerance=1e-8, maximum_elapsed_time_seconds=1200.0))
    (AN / f'runs/{run}.toml').parent.mkdir(exist_ok=True)
    (AN / f'runs/{run}.toml').write_text('schema = "solvent-specification-1"\n' + ''.join(f'{k} = {toml(v)}\n' for k, v in fields.items()))
    return SolventSpecification(AN / f'runs/{run}.toml', parameter=parameter)


def weighted(spec, records):  # weighted, scaled Jacobian of the fitted rows at the specification's start
    obs, chart = [spec.observation(r) for r in records], reg.CoordinateSet()
    chart.coordinates = spec.coordinates()
    v = list(chart.start(spec.parameters._native, obs, spec.thermal))
    e = reg.differentiate(spec.parameters, chart.coordinates, obs, optimizer=v, holds=[], thermochemistry=spec.thermal)
    J = np.sqrt([r['weight'] for r in records])[:, None] * np.reshape(e.residual_optimizer_gradient, (len(records), len(v)))
    sv = np.linalg.svd(J, compute_uv=False)
    return dict(singular_values=sv.tolist(), s_min_over_s_max=float(sv[-1] / sv[0]), rank=int(np.linalg.matrix_rank(J)))


def checks(spec):  # shared record unchanged; |ln Q - ln K| at one loaded Lawson state
    mea = json.loads(MEA.read_text())
    doc = spec.inputs['endpoint']
    same = lambda d: ([c for c in d['components'] if c['component_id'] in SHARED], [p for p in d['pairs'] if {p['component_id_a'], p['component_id_b']} <= set(SHARED)], d['correlations'])
    laws = {r['name']: r['correlation'] for r in spec.spec['chemistry']['reactions']['aqueous']}
    mea_laws = {r['name']: r['correlation'] for r in tomllib.loads((ROOT / 'analyses/solvent_specification_mea/declarations.toml').read_text())['chemistry']['reactions']['aqueous']}
    row = next(r for r in spec.inputs['observations']['fitted'] if r['group'] == 'Lawson')
    prob = spec.problems[row['problem']]
    state = eq.solve_equilibrium(spec.model, prob)
    lnq = max(abs(a.log_quotient - ln_k(laws[prob.reactions[a.reaction_index].name], prob.T)) for a in eq.reaction_activities(spec.model, state) if a.phase_index == 0)
    return dict(shared_unchanged=same(doc) == same(mea), shared_laws_unchanged=all(laws[k] == mea_laws[k] for k in ('R1', 'R2', 'R3')),
                max_lnQ_minus_lnK=lnq, equilibrium_residual=max(map(abs, state.residuals)))


def replay(spec):
    rows = spec.inputs['observations']['fitted']
    pred = [spec.prediction(r) for r in rows]
    w = [math.sqrt(r['weight']) * p['residual'] if p.get('status') == 'Available' else math.nan for r, p in zip(rows, pred)]
    return pred, w, math.fsum(0.5 * x * x for x in w)


def errors(pred, group):
    rows = [p for p in pred if p['group'] == group and p.get('status') == 'Available']
    rel = lambda p: p['value'] / p['observed'] - 1
    by_T = {}
    for p in rows:
        by_T.setdefault(p['row'].get('T_F') or p['row'].get('DEA_mass_fraction'), []).append(p)  # Lawson per isotherm (deg F), Carson per mass fraction
    stat = lambda ps: dict(n=len(ps), mean_abs_percent=100 * float(np.mean([abs(rel(p)) for p in ps])), bias_percent=100 * float(np.mean([rel(p) for p in ps])),
                           mean_log_ratio=float(np.mean([math.log(p['value'] / p['observed']) for p in ps])) if group != 'Carson' else None)
    return dict(stat(rows), per_temperature={k: stat(v) for k, v in sorted(by_T.items())}) if rows else dict(n=0)


def fit(run, form, start):
    coords, law = coordinates(start, form)
    spec = make_spec(run, variant(form, start), coords, law)
    out = dict(form=form, start=start, start_information=weighted(spec, spec.inputs['observations']['fitted']), start_checks=checks(spec))
    t = time.perf_counter()
    result, report, fitted = spec.fit()
    out.update(seconds=time.perf_counter() - t, **{k: report[k] for k in ('status', 'message', 'usable', 'initial_cost', 'final_cost', 'iterations', 'physical', 'optimizer')},
               active_bounds=list(result.covariance.active_bounds), endpoint_singular_values=list(result.covariance.singular_values), covariance_rank=result.covariance.rank)
    save(f'results/fit-runs/{run}-fit.json', dict(report=report))
    if fitted is None:
        return out
    laws = {r['name']: r['correlation'] for g in spec.fitted_reactions(result.chart).values() for r in g}
    law = laws['carbamate-hydrolysis']
    out.update(law=law, lnK_313=ln_k(law, TP), enthalpy_J_mol=-R * law['b'], coordinates={f'k_ij {c[0]}-{c[1]}': v for c, v in zip(([H, W], [C, W]), result.chart.physical[:2])})
    # Cold reload: endpoint document and completed law written, then a fresh specification reproduces the cost and every row.
    endpoint = epcsaft.parameters.document_mapping(epcsaft.Parameters.from_mapping(epcsaft.parameters.document_mapping(fitted)))
    cold = make_spec(run + '-endpoint', endpoint, coords, dict(a=law['a'], b=law['b']), parameter='endpoint')
    pred, w, cost = replay(cold)
    out.update(reload_cost=cost, reload_cost_relative=abs(cost / result.final_cost - 1), reload_rows_max_difference=max(abs(x - y) for x, y in zip(w, report['weighted_residuals'])),
               available=sum(p.get('status') == 'Available' for p in pred), rows=len(pred), endpoint_checks=checks(cold),
               errors={g: errors(pred, g) for g in ('Lawson', 'Carson')}, endpoint_sha256=cold.parameter_sha256, law_sha256=hashlib.sha256(json.dumps(law, sort_keys=True).encode()).hexdigest())
    save(f'results/fit-runs/{run}-replay.json', pred)
    return out


def main_fit():
    verify_wheel()
    summary = dict(runs={})
    for form in ('A', 'B'):
        for start in (1, 2):
            run = f'{form}-{start}'
            print(run, flush=True)
            try:
                summary['runs'][run] = fit(run, form, start)
            except Exception as error:
                summary['runs'][run] = dict(form=form, start=start, exception=type(error).__name__, message=str(error))
            print(json.dumps(jsonable({k: v for k, v in summary['runs'][run].items() if k not in ('physical', 'optimizer')}), default=float)[:1500], flush=True)
            save('results/fits.json', jsonable(summary))
    usable = {r: x for r, x in summary['runs'].items() if x.get('status') == 'converged' and x.get('usable') and x.get('available') == 80 and x.get('reload_cost_relative', 1) <= 1e-8}
    best = {}
    for run, x in sorted(usable.items(), key=lambda i: i[1]['final_cost']):
        best.setdefault(x['form'], run)
    summary['per_form'] = best
    summary['start_differences'] = {f: start_difference(summary['runs'][f'{f}-1'], summary['runs'][f'{f}-2']) for f in 'AB' if f'{f}-1' in usable and f'{f}-2' in usable}
    if not best:
        save('results/fits.json', jsonable(summary))
        sys.exit('no usable endpoint: Diagnose')
    selected = min(best.values(), key=lambda r: (len(usable[r]['active_bounds']), usable[r]['final_cost'], usable[r]['form']))
    x = usable[selected]
    frozen = dict(run=selected, endpoint=f'inputs/runs/{selected}-endpoint-document.json', endpoint_sha256=x['endpoint_sha256'], law=x['law'], law_sha256=x['law_sha256'],
                  declarations_sha256=sha(f'inputs/runs/{selected}-endpoint-declarations.toml'), specification=f'runs/{selected}-endpoint.toml', frozen_at=time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    summary['selection'] = frozen
    save('results/fits.json', jsonable(summary))
    save('results/selection.json', frozen)  # written before any held-out model evaluation (D7)


def start_difference(a, b):
    pa, pb = (json.load(open(AN / f'results/fit-runs/{x}-replay.json')) for x in (f"{a['form']}-1", f"{b['form']}-2"))
    vec = lambda x: [*[v / 0.05 for v in x['coordinates'].values()], x['lnK_313'], x['enthalpy_J_mol'] / 1000]
    return dict(cost_difference=abs(a['final_cost'] - b['final_cost']), max_scaled_coordinate_difference=max(abs(u - v) for u, v in zip(vec(a), vec(b))),
                max_relative_prediction_difference=max(abs(u['value'] / v['value'] - 1) for u, v in zip(pa, pb)))


def heldout(spec, group):
    rows = [r for r in spec.inputs['observations']['comparisons'] if r['group'] == group]
    out = []
    for r in rows:
        p = spec.prediction(r)
        if p.get('status') == 'Available':
            base, alt = spec.problems[r['problem']], []
            for f in (0.97, 1.03):  # stated loading error (upper value, 3 %) carried through the model (D7)
                prob = spec.problem('loaded-bubble', dict(T=base.T, P=base.P.guess, water=base.feed.values[W], alpha=f * base.feed.values[CO2]))
                q = reg.predict(spec.model, reg.observation(spec.parameters, 'partial_pressure', prob, observed=r['arguments']['observed'], form='log_ratio', phase='V', species=[CO2]))
                alt.append(q.value if q.status.name == 'Available' else math.nan)
            obs = r['arguments']['observed']
            s = math.sqrt((690.0 / obs) ** 2 + (0.5 * math.log(alt[1] / alt[0])) ** 2) if group == 'SeoHong' else None
            p.update(log_ratio=math.log(p['value'] / obs), relative_percent=100 * (p['value'] / obs - 1), p_low_alpha=alt[0], p_high_alpha=alt[1], s=s,
                     z=math.log(p['value'] / obs) / s if s else None)
        out.append(p)
    return out


def holdout(spec):
    out = {}
    for group in ('SeoHong', 'Lal'):
        rows = heldout(spec, group)
        ok =[p for p in rows if p.get('status') == 'Available']
        stat = lambda ps: dict(n=len(ps), mean_abs_percent=float(np.mean([abs(p['relative_percent']) for p in ps])), bias_percent=float(np.mean([p['relative_percent'] for p in ps])),
                               mean_log_ratio=float(np.mean([p['log_ratio'] for p in ps])), rms_log_ratio=float(np.sqrt(np.mean([p['log_ratio'] ** 2 for p in ps]))))
        by_T = {T: stat([p for p in ok if p['row']['T_C'] == T]) for T in dict.fromkeys(p['row']['T_C'] for p in ok)}
        res = dict(rows=len(rows), available=len(ok), overall=stat(ok), per_temperature=by_T, table=rows)
        if group == 'SeoHong':
            z = np.array([p['z'] for p in ok])
            res.update(within_2s=int(np.sum(np.abs(z) <= 2)), rms_z=float(np.sqrt(np.mean(z ** 2))), sum_z2=float(np.sum(z ** 2)),
                       stated_components='gauge 0.69 kPa + 3 % loading through the model; GC composition uncertainty not stated (absent)')
        else:  # Lal p.681: +-15 % in partial pressure above 0.05 kPa, much larger below
            above = [p for p in ok if p['observed'] > 50.0]
            res.update(above_0_05_kPa=dict(stat(above), within_15_percent=sum(abs(p['relative_percent']) <= 15 for p in above)),
                       at_or_below_0_05_kPa=stat([p for p in ok if p['observed'] <= 50.0]))
        out[group] = res
    return out


def main_score():
    verify_wheel()
    frozen = json.loads((AN / 'results/selection.json').read_text())
    spec = SolventSpecification(AN / frozen['specification'])
    assert spec.parameter_sha256 == frozen['endpoint_sha256'] and sha(f"inputs/runs/{frozen['run']}-endpoint-declarations.toml") == frozen['declarations_sha256']
    assert next(r['correlation'] for r in spec.spec['chemistry']['reactions']['aqueous'] if r['name'] == 'carbamate-hydrolysis') == frozen['law']
    out = dict(selection=frozen, **holdout(spec))
    # D7: the other form's lower-cost usable endpoint scored side by side, after the freeze; it does not change the selection.
    others = [r for r in json.loads((AN / 'results/fits.json').read_text())['per_form'].values() if r != frozen['run']]
    out['other_forms'] = {r: holdout(SolventSpecification(AN / f'runs/{r}-endpoint.toml')) for r in others}
    comps = [spec.prediction(r) for r in spec.inputs['observations']['comparisons'] if r['group'] in ('Lawson-394K', 'Weiland')]
    weiland =[p for p in comps if p['group'] == 'Weiland' and p.get('status') == 'Available' and not p['row']['note']]
    out['comparisons'] = dict(lawson_394K=[{k: p.get(k) for k in ('identity', 'status', 'message')} for p in comps if p['group'] == 'Lawson-394K'],
                              weiland=dict(n=len(weiland), mean_abs_percent=float(np.mean([abs(p['value'] / p['observed'] - 1) * 100 for p in weiland])),
                                           bias_percent=float(np.mean([(p['value'] / p['observed'] - 1) * 100 for p in weiland])), rows=[p for p in comps if p['group'] == 'Weiland']))
    # Comparison-only sets on the frozen selection (owner decision 2026-11-12); none enters the fit.
    rel = lambda ps: dict(n=len(ps), mean_abs_percent=float(np.mean([abs(p['value'] / p['observed'] - 1) * 100 for p in ps])), bias_percent=float(np.mean([(p['value'] / p['observed'] - 1) * 100 for p in ps])))
    viii = [spec.prediction(r) for r in spec.inputs['observations']['comparisons'] if r['group'] == 'Lawson-VIII']
    out['comparisons']['lawson_viii'] = dict(rel([p for p in viii if p.get('status') == 'Available']), per_T={T: rel([p for p in viii if p['row']['T_F'] == T and p.get('status') == 'Available']) for T in ('77', '100', '200')}, rows=viii)
    for q in ('DEA_plus_DEAH', 'DEACOO', 'HCO3'):
        ps = [spec.prediction(r) for r in spec.inputs['observations']['comparisons'] if r['group'] == f'Bottinger-{q}']
        diff = lambda sel: dict(n=len(sel), mean_abs_difference=float(np.mean([abs(p['value'] - p['observed']) for p in sel])), bias=float(np.mean([p['value'] - p['observed'] for p in sel])))
        ok = [p for p in ps if p.get('status') == 'Available']
        out['comparisons'][f'bottinger_{q}'] = dict(available=len(ok), clean=diff([p for p in ok if float(p['row']['x_HEOD']) == 0]), byproduct=diff([p for p in ok if float(p['row']['x_HEOD']) > 0]), rows=ps)
    cai, model = [], spec.model
    for r in csv.DictReader((ROOT / 'data/reference/DEA/Cai1996_Table4_water_DEA.csv').open()):  # bubble pressure at the measured T and x
        x = float(r['x_water'])
        feed = {c: n for c, n in ((W, x), (DEA, 1 - x)) if n > 0}
        prob = eq.problem_from_mapping(dict(T=float(r['T_K']), P=dict(free=True, guess=6660.0), feed=dict(basis='amounts', values=feed), row_tolerance=1e-10,
            phases=[dict(name='L', kind='liquid', support=list(feed)), dict(name='V', kind='vapor', support=list(feed), amount=dict(status='pinned', value=0.0))]))
        s = eq.solve_equilibrium(model, prob)
        y = s.mole_fractions[len(model.component_ids) + model.component_ids.index(W)] if s.requested_tolerance_met else None
        cai.append(dict(r, P_model_kPa=s.pressure / 1e3 if s.requested_tolerance_met else None, y_water_model=y, message=s.message))
    ok = [r for r in cai if r['P_model_kPa']]
    out['comparisons']['cai'] = dict(n=len(ok), mean_abs_P_percent=float(np.mean([abs(r['P_model_kPa'] / 6.66 - 1) * 100 for r in ok])),
                                     mean_abs_y=float(np.mean([abs(r['y_water_model'] - float(r['y_water'])) for r in ok])), rows=cai)
    he, hr = [], lambda T, x: model.state(T, P=1.75e6, x={W: x, DEA: 1 - x}, phase='liquid').residual_enthalpy  # ideal-gas enthalpy is linear in x and cancels
    for r in csv.DictReader((ROOT / 'data/reference/DEA/Horstmann2002_Table6_water_DEA_HE.csv').open()):
        x = float(r['x_water'])
        he.append(dict(r, HE_model=hr(363.15, x) - x * hr(363.15, 1.0) - (1 - x) * hr(363.15, 0.0), sigma=2 + 0.01 * abs(float(r['HE_J_per_mol']))))
    out['comparisons']['excess_enthalpy'] = dict(n=len(he), mean_abs_J_mol=float(np.mean([abs(r['HE_model'] - float(r['HE_J_per_mol'])) for r in he])),
        mean_abs_percent=float(np.mean([abs(r['HE_model'] / float(r['HE_J_per_mol']) - 1) * 100 for r in he])), within_2sigma=sum(abs(r['HE_model'] - float(r['HE_J_per_mol'])) <= 2 * r['sigma'] for r in he),
        water_residual_enthalpy_J_mol=hr(363.15, 1.0), rows=he)
    # Phase census at every fitted and held-out state (fitted heat rows: the loaded final liquid).
    policy = spec.spec['phase_policy']
    states = [r for r in spec.inputs['observations']['fitted'] + spec.inputs['observations']['comparisons'] if r['group'] in ('Lawson', 'Carson', 'SeoHong', 'Lal')]
    phases = [dict(spec.phase(dict(identity=r['identity'], problem=r.get('problem', r.get('final')), endpoint_sha256=spec.parameter_sha256), policy), group=r['group']) for r in states]
    out['census'] = {g: dict(states=sum(p['group'] == g for p in phases), **{k: [p['identity'] for p in phases if p['group'] == g and p.get(k)] for k in ('dense', 'gas', 'ambiguous', 'unresolved')})
                     for g in ('Lawson', 'Carson', 'SeoHong', 'Lal')}
    save('results/phases.json', jsonable(phases))
    # D3 check: +-10 % DEA ideal-gas Cp leaves the isothermal Carson heats unchanged.
    base = [p['value'] for p in replay(spec)[0] if p['group'] == 'Carson']
    caloric = json.loads((AN / 'inputs/caloric.json').read_text())
    moved = []
    for f in (0.9, 1.1):
        c = copy.deepcopy(caloric)
        c['components'][DEA]['coefficients'] = [f * v for v in c['components'][DEA]['coefficients']]
        save('inputs/runs/caloric-check.json', c)
        old, new = (f'path = "../{x}", sha256 = "{sha(x)}"' for x in ('inputs/caloric.json', 'inputs/runs/caloric-check.json'))
        text = (AN / frozen['specification']).read_text()
        assert old in text
        (AN / 'runs/caloric-check.toml').write_text(text.replace(old, new))
        other = SolventSpecification(AN / 'runs/caloric-check.toml')
        moved += [abs(p['value'] / b - 1) for p, b in zip([p for p in replay(other)[0] if p['group'] == 'Carson'], base)]
    out['cp_check_max_relative_change'] = max(moved)
    save('results/score.json', jsonable(out))
    print(json.dumps({k: v for k, v in jsonable(out).items() if k in ('census', 'cp_check_max_relative_change')}), flush=True)
    for g in ('SeoHong', 'Lal'):
        print(g, json.dumps({k: v for k, v in out[g].items() if k != 'table'}, default=float), flush=True)


def start_rows(form, start):  # diagnosis of an unavailable start: every fitted row evaluated at the declared start, no fit
    verify_wheel()
    coords, law = coordinates(start, form)
    spec = make_spec(f'{form}-{start}', variant(form, start), coords, law)
    rows = [dict({k: p.get(k) for k in ('identity', 'status', 'message', 'value', 'observed')}, row=p.get('row')) for p in map(spec.prediction, spec.inputs['observations']['fitted'])]
    save(f'results/fit-runs/{form}-{start}-start-rows.json', dict(available=sum(r['status'] == 'Available' for r in rows), rows=rows))


if __name__ == '__main__':
    {'fit': main_fit, 'score': main_score, 'start-rows': lambda: start_rows(sys.argv[2], int(sys.argv[3]))}[sys.argv[1]]()
