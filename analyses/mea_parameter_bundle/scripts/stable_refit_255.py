"""Issue 255 stage 3: fit with liquid stability enforced inside the original wide bounds; no adoption.

Design: issue #255 comment "Stage 2 design: stability-constrained refit" (copy in results/stable-refit-255/design-probe/design.md).
Commands (repository root, worktree .venv with the bc779473 wheel, `--no-sync`):
  qualify | old-wheel-replay | fit <run> | assess <run> | select | extras <run>
"""
# ruff: noqa: E402 -- numerical-library threads and the wheel identity are set before Engine imports.
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import zipfile

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
CORES = int(os.environ.get('AGENT_HEAVY_CORES', os.cpu_count()))  # agent-heavy's per-job core cap
ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'analyses/mea_parameter_bundle'
sys.path[:0] = [str(B / 'scripts'), str(B / 'calibration-misfit'), str(ROOT / 'src')]
import shared_evaluation as s

COMMIT = 'bc7794731e94be961d16028d3f4880c6718a93ad'
SHA = '8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069'
WHEEL = ROOT / f'build/engine-wheels/main-{COMMIT}/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl'
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import jsonable, stability_payload, supplied_negative
import density_268 as d

OUT = B / 'results/stable-refit-255'
CHAIN = B / 'results/engine-3e83e19c-refit-chain'
A6 = CHAIN / 'a6/spec.json'
STARTS = {'final': B / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json', 'wide': CHAIN / 'a6/run/fit/usable-budget-endpoint.json'}
START_SHA = {'final': '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91',
             'wide': 'efb2a9abe3787410734394f5ee32e6eade42d7cb6f5ad23445a357423690b2f3'}
SHIFTS = {'final': {'R2': -1363.931574116721, 'R5': 10000.}, 'wide': {'R2': 3442.783280905225, 'R5': 10000.}}
HISTORICAL_COST = 148.87893934557388  # final set on pre-#260 water calorics
FINAL_COST = 148.8832604402288  # final set replayed on current inputs (#260 IAPWS-95 water record), new wheel
STAGES = (1e-2, 3e-3)
ELAPSED = 7200.  # per-stage wall limit, sized for 32 cores; #284 stage 2 raises it for its 3-core fits
CENSUS_FEED = (9.7292821, 76.9751925)
CENSUS_T = (313.15, 318.15, 333.15, 353.15, 373.15, 393.15)
CENSUS_A = (1e-5, .05, .1, .2, .256, .3, .4, .5, .6)


def read(path):
    path = Path(path)
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


def write(rel, value):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(dict(wheel_sha256=SHA, result=jsonable(value)), indent=1, allow_nan=False) + '\n').encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)


def result(rel):
    payload = read(OUT / rel)
    assert payload['wheel_sha256'] == SHA
    return payload['result']


def verify():
    """Installed Engine bytes must equal the bc779473 wheel; no source checkout is importable."""
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
    base = Path(epcsaft.__file__).parent.parent
    with zipfile.ZipFile(WHEEL) as archive:
        names = [n for n in archive.namelist() if n.startswith('epcsaft/') and not n.endswith('/')]
        assert names and all(archive.read(n) == (base / n).read_bytes() for n in names)


# ---------------------------------------------------------------- states

def states(stocks=None, loadings=None):
    """Enforced liquid-parent grid (dense block + census nodes) and the held-out offset grid."""
    if stocks is not None:
        return [dict(key=f'grid:{stock}:{T}:{a}:{c}', T=round(313.15+10*i,2), stock=stock, a=a, c=c)
                for stock in stocks for i in range(9) for T in [round(313.15+10*i,2)] for a in loadings for c in (1.05,3.)]
    dense = [dict(block='dense', wt=w, T=round(313.15 + 10 * i, 2), a=a, c=c)
             for w in (.15, .25, .35, .45) for i in range(9) for a in [1e-5] + [round(.025 * k, 4) for k in range(1, 25)] for c in (1.05, 3.)]
    census = [dict(block='census', wt=None, T=T, a=a, c=c) for T in CENSUS_T for a in CENSUS_A for c in (1.05, 3.)]
    offset = [dict(block='offset', wt=w, T=round(318.15 + 10 * i, 2), a=round(.0125 + .025 * k, 4), c=1.5)
              for w in (.2, .3, .4) for i in range(8) for k in range(24)]
    for i, x in enumerate(dense + census + offset):
        x['key'] = f"{x['block']}|{x['wt']}|{x['T']}|{x['a']}|{x['c']}"
    assert (len(dense), len(census), len(offset)) == (1800, 108, 576)
    return dense + census, offset


def stability_row(spec, state, scale):
    template = spec.problems[next(r['problem'] for r in spec.inputs['observations']['fitted'] if r['group'] == 'loaded density')]
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in spec.inputs['endpoint']['components']}
    mea, water = CENSUS_FEED if state['wt'] is None else (
        CENSUS_FEED[0], CENSUS_FEED[0] * masses['monoethanolamine'] * (1 - state['wt']) / (state['wt'] * masses['water']))
    feed = eq.Amounts({'monoethanolamine': mea, 'water': water, 'carbon-dioxide': state['a'] * mea})
    ids = s.COMPONENT_IDS
    common = dict(T=state['T'], feed=feed, reactions=template.reactions, neutral_reference=template.neutral_reference, row_tolerance=1e-10)
    parent = eq.Problem(P=1e5, phases=[eq.Phase('L', kind='liquid', support=ids)], **common)
    bubble = eq.Problem(P=eq.Free(2e4), phases=[eq.Phase('L', kind='liquid', support=ids),
                        eq.Phase('V', kind='vapor', support=ids[:3], amount=eq.Pinned(0.))], **common)
    return reg.stability(spec.parameters, parent, scale=scale, pressure_reference=bubble, pressure_ratio=state['c'])


_SPEC = None


TOML = OUT.parent / 'adoption-297/historical-spec/MEA.toml'
SPEC261 = OUT / 'spec-261/study.toml'


def spec_261():
    """#261's study and declarations moved to spec-261/ on the current (#260) caloric record: path prefixes and two hashes change."""
    import re
    if SPEC261.exists():
        return
    source = B / 'results/pressure-transfer-261'
    move = lambda text: re.sub(r'("path"\s*=\s*")(?!\.\./)', r'\1../../pressure-transfer-261/', text.replace('"../../../', '"../../../../'))
    SPEC261.parent.mkdir(parents=True, exist_ok=True)
    declarations = move((source / 'declarations.toml').read_text()).encode()
    (SPEC261.parent / 'declarations.toml').write_bytes(declarations)
    caloric = ROOT / 'analyses/solvent_specification_mea/inputs/caloric.json'
    text = move((source / 'study.toml').read_text()).replace('"../../pressure-transfer-261/declarations.toml"', '"declarations.toml"')
    for old, new in [('71c0f65204de5f10a22099db8ee6a939895bf280c725292e2cc46c0b1ebe9ef1', hashlib.sha256(caloric.read_bytes()).hexdigest()),
                     ('f6ae5c276979b528796564a7bf051ebeec2b138aa813de97181908e7d09e6986', hashlib.sha256(declarations).hexdigest())]:
        assert text.count(old) == 1
        text = text.replace(old, new)
    SPEC261.write_text(text)


def bind(mapping):
    """density_268.bind on the run's solvent specification (MEA.toml, or #261's study.toml for variant c)."""
    saved = d.AN
    try:
        d.AN = TOML.parent
        if TOML.name == 'MEA.toml':
            return d.bind(mapping, 'MEA.toml')
        d.SolventSpecification, original = (lambda path: original(TOML)), d.SolventSpecification
        try:
            return d.bind(mapping)
        finally:
            d.SolventSpecification = original
    finally:
        d.AN = saved


def _init(mapping, trials=None, route=None):
    global _SPEC, _TRIALS, _ROUTE
    _ROUTE = route
    _TRIALS = trials or {}
    (route.verify if route else verify)()
    _SPEC = (route.bind if route else bind)(mapping)


def _measure(state):
    started = time.monotonic()
    try:
        item = (_ROUTE.stability_row if _ROUTE else stability_row)(_SPEC, state, 1.)
        supplied, not_applicable = [], []
        support = {i for i, amount in enumerate(item.problem.feed.values) if amount > 0}
        support.update(i for reaction in item.problem.reactions for i, value in enumerate(reaction.stoichiometry) if value != 0)
        for witness in _TRIALS.get(state['key'], []):
            outside = sorted(set(witness['support']) - support)
            if outside:
                not_applicable.append(dict(witness, evidence='not applicable', support_difference=outside))
                continue
            phase = type(item.problem.phases[0])()
            phase.name, phase.kind, phase.support_declared = 'previous-split', getattr(type(item.problem.phases[0].kind), witness.get('kind','Liquid' if len(witness['support'])==len(s.COMPONENT_IDS) else 'Vapor')), True
            phase.support, phase.composition_guess, phase.packing_guess = witness['support'], witness['composition'], witness['packing']
            supplied.append(phase)
        prediction = reg.predict(_SPEC.model, item)
        out = stability_payload(prediction)
        if prediction.stability is not None:
            out['witnesses'] = [dict(resolved_descent=True, kind=t.phase.kind.name, support=list(t.phase.support), composition=list(t.composition), packing=math.exp(t.split_coordinates[-1]))
                                for t in prediction.stability.report.trials if t.resolved_descent and t.split_coordinates]
        out['optimized_available'] = out['available']
        if supplied:
            out['supplied_available'], out['supplied_trials'] = False, []
            try:
                parent = item.problem
                if prediction.pressure_reference is not None:
                    parent.pressure = type(parent.pressure).fixed(prediction.pressure_reference.value*item.pressure_ratio)
                result = eq.solve_equilibrium(_SPEC.model,parent)
                options = eq.StabilityOptions()
                options.trials, options.evaluate_supplied_trials = supplied, True
                report = eq.stability_test(eq.compile_problem(_SPEC.model,parent),result,options)
                out['supplied_parent_pressure_Pa'] = result.pressure
                out['supplied_trials'] = [dict(evidence=t.evidence,resolved_descent=t.resolved_descent,quantities=jsonable(t.quantities),message=t.message) for t in report.trials]
                out['supplied_available'] = result.requested_tolerance_met and len(report.trials)==len(supplied) and all(t.evidence=='evaluated' for t in report.trials)
            except Exception as error:
                out['supplied_error'] = f'{type(error).__name__}: {error}'
            out['available'] = out['optimized_available'] and out['supplied_available']
        if supplied or not_applicable:
            out['not_applicable_supplied_trials'] = not_applicable
            available = sum(t['evidence']=='evaluated' for t in out.get('supplied_trials',[]))
            out['supplied_trial_counts'] = dict(available=available, unavailable=len(supplied)-available, not_applicable=len(not_applicable))
    except Exception as error:
        out = dict(status='Exception', message=f'{type(error).__name__}: {error}', available=False)
    return dict(key=state['key'], seconds=time.monotonic() - started, **out)


def grid(mapping, chosen, trials=None, *, route=None):
    """Fresh Full searches at one parameter mapping, one process per core."""
    from concurrent.futures import ProcessPoolExecutor
    trials = globals().get('GRID_TRIALS') if trials is None else trials
    with ProcessPoolExecutor(min(route.workers if route else CORES, len(chosen)), initializer=_init, initargs=(mapping, trials, route)) as pool:
        measured = list(pool.map(_measure, chosen, chunksize=4))
    if trials is not None:
        for row in measured:
            trials.setdefault(row['key'], []).extend(w for w in row.get('witnesses',[]) if w not in trials.get(row['key'],[]))
    return measured


def descent(row):
    return (bool(row.get('optimized_available',row.get('available'))) and row['value'] < 0) or any(map(supplied_negative,row.get('supplied_trials',[])))


def tally(rows):
    return dict(supplied_trial_counts={key:sum(r.get('supplied_trial_counts',{}).get(key,0) for r in rows) for key in ('available','unavailable','not_applicable')},
                states=len(rows), available=sum(bool(r.get('available')) for r in rows), descent=sum(map(descent, rows)),
                unavailable=[r['key'] for r in rows if not r.get('available')],
                minimum_tau=min((r['value'] for r in rows if r.get('available') and r['value']<0), default=None),
                supplied_minimum_tpd=min((t['quantities']['tpd_over_rt'] for r in rows for t in r.get('supplied_trials',[]) if t['evidence']=='evaluated'),default=None))


# ---------------------------------------------------------------- coordinates and mappings

def coordinates(spec, shifts, held=(), extra_shifts=(), fitted=None, fixed=None, ties=None):
    """The 16 a6 coordinates and wide bounds about this spec's mapping; enthalpy totals stay in [-1e4, 1e4] J/mol."""
    values, out = s.parameter_values(spec.inputs['endpoint']), []
    identities = None if fitted is None else {q if isinstance(q, str) else q['identity'] for q in fitted}
    extra = [] if fitted is None else [q for q in fitted if isinstance(q, dict)]
    for q in read(A6)['information_coordinates'] + extra:
        if (identities is not None and q['identity'] not in identities) or q['identity'] in (fixed or {}):
            continue
        scale, bounds = q['scale'], q['bounds']
        if 'coefficient' in q:
            scale *= abs(q['source_to_native_factor'])
            bounds = sorted(v * q['source_to_native_factor'] for v in bounds)
            origin = next(r['correlation'][q['coefficient']] for r in spec.spec['chemistry']['reactions']['aqueous'] if r['name'] == q['reaction'])
            args = dict(kind='reaction_coordinate', name=q['reaction'], coefficient=q['coefficient'])
        elif q.get('enthalpy_shift'):
            if q['reaction'] in held:
                continue
            origin, bounds = 0., [-10000 - shifts[q['reaction']], 10000 - shifts[q['reaction']]]
            args = dict(kind='reaction_enthalpy_shift', name=q['reaction'], pivot_temperature=313.15)
        else:
            origin = values[q['identity']]
            args = dict(targets=[[t['family'], t['target'], t['factor']] for t in q.get('targets', [dict(q, factor=1.)])])
        if q['identity'] in (ties or {}):
            args['targets'] += ties[q['identity']]
        out.append(dict(args, identity=q['identity'], origin=origin, scale=scale, bounds=bounds))
    for name in extra_shifts:
        out.append(dict(kind='reaction_enthalpy_shift', name=name, pivot_temperature=313.15, identity=f'reaction:{name}:enthalpy_shift',
                        origin=0., scale=2500., bounds=[-10000 - shifts.get(name, 0.), 10000 - shifts.get(name, 0.)]))
    return out


def endpoint_mapping(start, report, declared):
    """Parameter mapping at a fit's returned optimizer (density_268.finish_fit, all fitted reactions)."""
    updates, index = {}, 0
    for q in declared:
        for family, target, factor in q.get('targets', []):
            identity = (f'component/{target}/{family}' if isinstance(target, str)
                        else f"pair/{'/'.join(sorted(target))}/" + ('k_ij/reciprocal_temperature_slope' if family == 'k_ij_reciprocal_temperature_slope' else family))
            updates[identity] = report['physical'][index]
            index += 1
    fitted = {q['name'] for q in declared if q.get('kind') in ('reaction_coordinate', 'reaction_enthalpy_shift')}
    for entry in report['reactions']['aqueous']:
        name, law = entry['name'], eq.ReactionLogPolynomial(**entry['correlation'])
        if name not in fitted:
            continue
        if name == 'R5':
            fields = dict(zip(('a_k', 'b', 'c_per_k'), reg.reaction_log10_reciprocal(law), strict=True))
        elif name == 'R2':
            fields = dict(a=law.a - law.c * math.log(law.reference_temperature), b_k=law.b, c=law.c, d_per_k=law.d)
        else:  # R4 is stored as a + b_k/T with no ln T term.
            assert law.c == law.d == law.e == law.f == 0.
            fields = dict(a=law.a, b_k=law.b)
        updates.update({f'reaction:{name}:correlation:{k}': v for k, v in fields.items()})
    return s.with_parameter_values(start, updates)


def shift_totals(shifts, declared, report):
    """Inherited total shifts plus this fit's increments (EvaluatedCoordinates order: active rows, then reactions)."""
    reactions = [q for q in declared if q.get('kind') in ('reaction_coordinate', 'reaction_enthalpy_shift')]
    increments = report['physical'][len(report['physical']) - len(reactions):]
    out = dict(shifts)
    for q, value in zip(reactions, increments, strict=True):
        if q['kind'] == 'reaction_enthalpy_shift':
            out[q['name']] = out.get(q['name'], 0.) + value
    return out


def segment(anchor, endpoint, t):
    """Linear segment in every differing mapping value; each is affine in the fitted coordinates."""
    a, e = s.parameter_values(anchor), s.parameter_values(endpoint)
    assert a.keys() == e.keys()
    if t == 1.:
        return endpoint
    return s.with_parameter_values(anchor, {k: a[k] + t * (e[k] - a[k]) for k in a if e[k] != a[k]})


# ---------------------------------------------------------------- replay and metrics

def replay(mapping, rows=None):
    spec = bind(mapping)
    records = spec.inputs['observations']['fitted'] if rows is None else rows(spec)
    values = d.evaluate(spec, records)
    ok = all(v['status'] == 'Available' and v.get('requested_tolerance_met') for v in values)
    return values, ok, (math.fsum(v['cost'] for v in values) if ok else None)


GROUPS = [  # (label, group, row quantity or None, rule)
    ('fitted CO2 partial pressure', 'common149', 'PartialPressure', 'aard'), ('Kiepe pressure', 'Kiepe', None, 'aard'),
    ('fitted phase mole fraction', 'common149', 'PhaseMoleFraction', 'aard'), ('restored species', 'restored species', None, 'aard'),
    ('Jakobsen ratio', 'Jakobsen', None, 'aard'), ('loaded density', 'loaded density', None, 'scaled'),
    ('CO2-free density', 'CO2-free density', None, 'scaled'), ('fitted heat of absorption', 'common149', 'AdditionEnthalpy', 'scaled'),
    ('heat capacity', 'Cp', None, 'scaled'), ('Cai MEA-water VLE', 'Cai', None, 'report')]


def metrics(values):
    out = {}
    for label, group, quantity, rule in GROUPS:
        rows = [v for v in values if v['group'] == group and (quantity is None or (v['row'].get('quantity') or v['row'].get('kind')) == quantity)]
        error = [v['value'] - v['observed'] for v in rows]
        out[label] = dict(rule=rule, n=len(rows), within_2s=sum(abs(v['residual']) <= 2 for v in rows),
                          aard_percent=100 * math.fsum(abs(v['value'] / v['observed'] - 1) for v in rows) / len(rows),
                          rmse=math.sqrt(math.fsum(x * x for x in error) / len(rows)), cost=math.fsum(v['cost'] for v in rows))
    assert sum(m['n'] for m in out.values()) == 307
    return out


def acceptance(candidate, baseline):
    checks = {}
    for label, m in candidate.items():
        b = baseline[label]
        if m['rule'] == 'aard':
            checks[label] = dict(aard_rise_points=m['aard_percent'] - b['aard_percent'], passed=m['aard_percent'] - b['aard_percent'] <= 2.)
        elif m['rule'] == 'scaled':
            checks[label] = dict(within_2s=[b['within_2s'], m['within_2s']], aard_ratio=m['aard_percent'] / b['aard_percent'],
                                 rmse_ratio=m['rmse'] / b['rmse'], passed=m['within_2s'] >= b['within_2s']
                                 and m['aard_percent'] <= 1.25 * b['aard_percent'] and m['rmse'] <= 1.25 * b['rmse'])
    return checks


# ---------------------------------------------------------------- census (stage-1 liquid + vapor parents)

def _census(task):
    import phase_diagnosis_255 as p255
    mapping, state, path, *previous = task
    if previous and previous[0]:
        original = p255.f.stability
        p255.f.stability = lambda model, problem, result: original(model, problem, result, supplied=previous[0])
    row = {k: state[k] for k in ('index', 'temperature_K', 'loading', 'pressure_Pa')}
    try:
        p255.f.family_job(mapping, p255.e.request(mapping, 313.15, .11), row, [], path)
    finally:
        if previous and previous[0]:
            p255.f.stability = original
    raw = read(path)
    path.unlink()
    reduced = p255.reduce_state(raw)
    supplied = [t for report in raw.get('stability',[]) for t in report.get('supplied_trials',[])]
    if previous and previous[0]:
        reduced['supplied_negative'] = sum(t.get('quantities',{}).get('tpd_over_rt',0.)<0 for t in supplied)
        reduced['complete'] = reduced['complete'] and len(supplied)==len(previous[0]) and all(t['evidence']=='evaluated' for t in supplied)
    return raw, reduced


def census(mapping, name, trials=None):
    from concurrent.futures import ProcessPoolExecutor
    chosen = read(B / 'results/engine-3e83e19c-phase-search/run-2/inputs/states.json')
    tmp = OUT / name / 'census-tmp'
    tmp.mkdir(parents=True, exist_ok=True)
    memory = int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1])
    with ProcessPoolExecutor(min(CORES, max(1, memory // 750000)), initializer=verify) as pool:
        out = list(pool.map(_census, [(mapping, x, tmp / f'{x["index"]}.json', (trials or {}).get(str(x['index']), [])) for x in chosen]))
    tmp.rmdir()
    write(f'{name}/census-raw.json.gz', [r for r, _ in out])
    rows = [r for _, r in out]
    summary = dict(states=len(rows), descent=sum(r['resolved'] > 0 or r.get('supplied_negative',0)>0 for r in rows), incomplete=sum(not r['complete'] for r in rows),
                   descent_indices=[r['index'] for r in rows if r['resolved'] > 0 or r.get('supplied_negative',0)>0], incomplete_indices=[r['index'] for r in rows if not r['complete']])
    write(f'{name}/census.json', dict(summary=summary, rows=rows))
    return summary


# ---------------------------------------------------------------- qualification

def old_wheel_replay():
    """Run under the repository-pinned 0d08dff9 environment: the same code and current inputs, for the wheel-to-wheel gate."""
    wheel = s.installed_wheel()
    assert s.sha256(wheel) == '0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804'
    for name in STARTS:
        values, ok, cost = replay(s.parameter_mapping(STARTS[name]))
        (OUT / 'qualification').mkdir(parents=True, exist_ok=True)
        (OUT / f'qualification/{name}-old-wheel-replay.json').write_text(json.dumps(dict(
            wheel_sha256=s.sha256(wheel), wheel=str(wheel), available=ok, cost=cost, result=jsonable(values)), indent=1, allow_nan=False) + '\n')


def compare(values, reference, keys):
    return [max(abs(v[a] - reference[v['identity']][b]) / max(1., abs(reference[v['identity']][b])) for a, b in keys) for v in values]


def qualify():
    verify()
    enforced, offset = states()
    out = {}
    for name in STARTS:
        assert hashlib.sha256(STARTS[name].read_bytes()).hexdigest() == START_SHA[name]
        mapping = s.parameter_mapping(STARTS[name])
        values, ok, cost = replay(mapping)
        same = read(OUT / f'qualification/{name}-old-wheel-replay.json')
        old_rows = {r['identity']: r for r in same['result']}
        diff = compare(values, old_rows, (('value', 'value'), ('residual', 'residual'), ('weighted_residual', 'weighted_residual')))
        old = same['cost']
        # Input attribution only: stage-1 replay predates #260's water ideal-gas record (0e216fe).
        stage1 = {r['target']: r for r in read(B / f'results/phase-diagnosis-255/{name}/replay.json')}
        moved = [dict(identity=v['identity'], group=v['group'], relative=x) for v, x in zip(values, compare(values, stage1,
                 (('value', 'predicted'), ('residual', 'residual'), ('weighted_residual', 'weighted_residual'))), strict=True) if x > 1e-8]
        retained_grid = OUT / f'qualification/{name}-grid.json.gz'
        rows = result(retained_grid.relative_to(OUT)) if retained_grid.exists() else grid(mapping, enforced + offset)
        write(f'qualification/{name}-grid.json.gz', rows)
        out[name] = dict(rows=len(values), available=ok and same['available'], cost=cost, old_wheel_cost=old, relative_cost_difference=abs(cost / old - 1),
                         stage1_cost=math.fsum(r['cost'] for r in stage1.values()), rows_moved_since_stage1_inputs=moved,
                         maximum_row_difference=max(diff), enforced=tally(rows[:len(enforced)]), offset=tally(rows[len(enforced):]),
                         census=result(f'qualification/{name}/census.json')['summary'] if (OUT / f'qualification/{name}/census.json').exists()
                         else census(mapping, f'qualification/{name}'))
        write(f'qualification/{name}-replay.json', values)
        print(name, json.dumps({k: v for k, v in out[name].items() if k not in ('enforced', 'offset')}), flush=True)
    out['passed'] = all(out[n]['available'] and out[n]['rows'] == 307 and out[n]['maximum_row_difference'] <= 1e-8
                        and out[n]['relative_cost_difference'] <= 1e-8 for n in STARTS) and out['final']['census']['descent'] == 0
    out['excluded'] = sorted(set(out['final']['enforced']['unavailable']) | set(out['wide']['enforced']['unavailable']))
    write('qualification/summary.json', out)
    assert out['passed'], 'qualification failed: see qualification/summary.json'


# ---------------------------------------------------------------- runs

def bottinger_353(spec, mapping):
    return [(x['item'], 1.) for x in bottinger_targets(spec, mapping)]


def bottinger_targets(spec, mapping):
    """#263 all-five targets: MEA + MEAH+ and carbamate at Böttinger states 063-067, (x-x_obs)/(0.1 x_obs + 0.001), weight 1."""
    # The run's start record: its reaction laws must equal the bound problems' laws (tied R5 declarations).
    packet = s.load_state_packet(B / 'results/source-corrections-152/state-packet.json.gz')['observations']
    measured = {r['target']: r for r in csv.DictReader((B / 'results/engine-3e83e19c-paper-evidence/species-figure-data.csv').open())}
    out = []
    for o in (o for o in packet if o['identity'] in {f'Bottinger2008_state_{i:03d}' for i in range(63, 68)}):
        problem = s._problem_from_request(s.corrected_request(o['request'], s.reaction_values(mapping), mapping=mapping))
        problem.row_tolerance = 1e-10
        for target in o['targets']:
            if target['identity'].endswith(('::MEA + MEAH+', '::MEACOO-')):
                r = measured[target['identity']]
                species = ('monoethanolamine', 'protonated-monoethanolamine') if r['species'] == 'MEA + MEAH+' else ('carbamate-anion',)
                item = reg.observation(spec.parameters, 'mole_fraction', problem, phase=problem.phases[0].name, species=species,
                                       observed=float(r['observed']), form='difference', scale=.1 * float(r['observed']) + .001)
                out.append(dict(identity=target['identity'], species=r['species'], observed=float(r['observed']), item=item))
    assert len(out) == 10
    return out


def r5_ln_k(mapping, temperatures):
    """The record's completed R5 law, L(T) = a + b/T + c ln(T/Tref) + dT + e/T^2 + fT^2 (Engine equations, reaction_constant_ln_polynomial)."""
    request = s.corrected_request(s.load_state_packet()['observations'][0]['request'], s.reaction_values(mapping), mapping=mapping)
    q = next(x.correlation for x in s._problem_from_request(request).reactions if x.name == 'R5')
    return [q.a + q.b / T + q.c * math.log(T / q.reference_temperature) + q.d * T + q.e / T**2 + q.f * T**2 for T in temperatures]


def extras(run):
    """Variant-specific comparisons at the final set, the primary candidate and the variant candidate (reported, never fitted here)."""
    verify()
    sets = {'final': s.parameter_mapping(STARTS['final']), 'primary': result(f"{result('primary.json')['run']}/candidate.json"),
            run: result(f'{run}/candidate.json')}
    out = {name: {} for name in sets}
    ratio = lambda values: [v['value'] / v['observed'] for v in values if v['status'] == 'Available']
    if run == 'joint-chemistry':
        hamborg = read(ROOT / 'analyses/high_temperature_chemistry/results/hamborg-law.json')['coefficients']
        temperatures = sorted({float(x['temperature_K']) for x in csv.DictReader((ROOT / 'analyses/high_temperature_chemistry/inputs/hamborg-table16.csv').open())})
        h = [hamborg['a'] + hamborg['b'] / T + hamborg['c'] * math.log(T / hamborg['reference_temperature']) for T in temperatures]
        for name, mapping in sets.items():
            spec = bind(mapping)
            rows = []
            for x in bottinger_targets(spec, mapping):
                p = reg.predict(spec.model, x['item'])
                rows.append(dict(identity=x['identity'], species=x['species'], observed=x['observed'], predicted=p.value, status=p.status.name,
                                 relative_error_percent=100 * (p.value / x['observed'] - 1)))
            v = r5_ln_k(mapping, temperatures)
            out[name] = dict(bottinger_353=rows, maximum_carbamate_excess_percent=max(x['relative_error_percent'] for x in rows if x['species'] == 'MEACOO-'),
                             R5_against_hamborg=dict(temperatures_K=temperatures, ln_K=v, hamborg_ln_K=h, difference=[a - b for a, b in zip(v, h)],
                                                     rms_difference=math.sqrt(sum((a - b)**2 for a, b in zip(v, h)) / len(h))))
    if run == 'pressure-roles-261':
        roles = read(B / 'results/pressure-transfer-261/recommendation-data-roles.json')['roles']
        for name, mapping in sets.items():
            spec = bind(mapping)
            every = spec.inputs['observations']['fitted'] + spec.inputs['observations']['comparisons']
            groups = {'standard fitted 47': [x for x in spec.inputs['observations']['fitted'] if x['kind'] == 'partial_pressure'],
                      **{k: [x for x in every if x['identity'] in set(v)] for k, v in roles.items()}}
            for group, records in groups.items():
                q = ratio(d.evaluate(spec, records))
                out[name][group] = dict(n=len(records), available=len(q), AARD_percent=100 * sum(abs(x - 1) for x in q) / len(q),
                                        mean_log_ratio=sum(math.log(x) for x in q) / len(q))
    write(f'{run}/extras.json', out)
    print(run, json.dumps(out)[:1500], flush=True)


def rows_261(spec):
    """#261 roles: non-pressure calibration rows plus the 57 candidate pressures; 106 Aronu and 89 hot rows stay outside."""
    roles = read(B / 'results/pressure-transfer-261/recommendation-data-roles.json')['roles']['candidate_reactive_pressure_fit']
    fitted, everything = spec.inputs['observations']['fitted'], spec.inputs['observations']['fitted'] + spec.inputs['observations']['comparisons']
    chosen = [r for r in fitted if r['kind'] != 'partial_pressure'] + [r for r in everything if r['identity'] in set(roles)]
    assert len(roles) == 57 and len({r['identity'] for r in chosen}) == len(chosen) == 260 + 57
    return chosen


RUNS = {'final': dict(start='final'), 'wide': dict(start='wide'),
        'r2-held': dict(start='final', held=('R2',), stages=(3e-3,)),
        'joint-chemistry': dict(start='primary', extra_shifts=('R4',), extra=bottinger_353, stages=(3e-3,)),
        'pressure-roles-261': dict(start='primary', toml=SPEC261, rows=rows_261, stages=(3e-3,))}


def rows_of(cfg):
    return cfg.get('rows')


def start_of(cfg):
    """Named start, or the selected primary candidate (final set under outcome B)."""
    if cfg['start'] in STARTS:
        return s.parameter_mapping(STARTS[cfg['start']]), SHIFTS[cfg['start']]
    chosen = result('primary.json')
    if chosen['outcome'] == 'A':
        return result(f"{chosen['run']}/candidate.json"), result(f"{chosen['run']}/retreat.json")['shifts']
    return s.parameter_mapping(STARTS['final']), SHIFTS['final']


def select():
    """Outcome class from the two primary runs (design: lower cost with t > 0 and criteria 1-3)."""
    runs = {r: result(f'{r}/assessment.json') for r in ('final', 'wide')}
    passing = [r for r, a in runs.items() if a['outcome_A']]
    run = min(passing, key=lambda r: runs[r]['cost']) if passing else None
    write('primary.json', dict(outcome='A' if run else 'B', run=run, runs={r: {k: a[k] for k in ('t', 'cost', 'passed', 'outcome_A', 'near_final', 'stability_passed')} for r, a in runs.items()}))


def stage_fit(run, index, scale, start, shifts, enforced, held=(), extra_shifts=(), rows=None, extra=None, fitted=None, fixed=None, ties=None, route=None):
    if route is not None:
        OUT, bind, write, result, replay, endpoint_mapping, stability_row = (route.out, route.bind, route.write, route.result, route.replay, route.endpoint_mapping, route.stability_row)
    else:
        OUT, bind, coordinates, write, result, replay, endpoint_mapping, stability_row = (globals()[k] for k in ("OUT", "bind", "coordinates", "write", "result", "replay", "endpoint_mapping", "stability_row"))
    rel = f'{run}/stage-{index}'
    if (OUT / rel / 'fit.json').exists():
        return result(f'{rel}/fit.json')
    spec = bind(start)
    if fitted is not None:
        spec.inputs['endpoint'] = start
    declared = spec.inputs['coordinates'] if route else coordinates(spec, shifts, held, extra_shifts, fitted=fitted, fixed=fixed, ties=ties)
    spec.inputs['coordinates'] = declared
    if rows is not None:
        spec.inputs['observations']['fitted'] = rows(spec)
    controls = route.controls if route else read(A6)['controls']
    # Workers sized by free memory (about 0.35 GB each, 7 GB kept for the parent and other work); the result does not depend on it.
    available = int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1]) / 1e6
    spec.spec['optimizer'] = dict(controls, maximum_elapsed_time_seconds=controls.get('maximum_elapsed_time_seconds', ELAPSED), workers=route.workers if route else max(1, min(CORES, int((available - 7) / .35))))
    added = extra(spec, start) if extra else []
    if (OUT / rel / 'fit-native.json').exists():  # resume after an interrupted reduction without refitting
        report = result(f'{rel}/fit-native.json')
    else:
        stability = added + [(stability_row(spec, x, scale), 1.) for x in enforced]
        started = time.monotonic()
        native, report, _ = spec.fit(stability)
        report.update(workers=spec.spec['optimizer']['workers'], maximum_elapsed_time_seconds=spec.spec['optimizer']['maximum_elapsed_time_seconds'], scale=scale, declared=declared, start_shifts=shifts, wall_s=time.monotonic() - started, statuses=[x.name for x in native.statuses],
                      enforced=[x['key'] for x in enforced], first_numerical_failure=None if native.first_numerical_failure is None else str(native.first_numerical_failure.stop))
        write(f'{rel}/fit-native.json', report)
    endpoint = None
    if report['physical'] and report['reactions']:
        endpoint = endpoint_mapping(start, report, declared)
        values, ok, cost = replay(endpoint, rows)
        report.update(endpoint_replay_available=ok, endpoint_replay_cost=cost,
                      endpoint_prediction_difference=max(abs(v['value'] - p) / max(1., abs(p)) for v, p in zip(values, report['predictions'][:len(values)], strict=True)) if ok and report['predictions'] else None,
                      endpoint_shifts=shift_totals(shifts, declared, report))
        write(f'{rel}/replay.json', values)
        write(f'{rel}/parameters.json', endpoint)
    measured = report['stability_predictions'][-len(enforced):] if enforced else []  # stability rows are the last observations
    report['stability_tally'] = tally([dict(key=k, **(p or dict(available=False))) for k, p in zip(report['enforced'], measured, strict=True)])
    write(f'{rel}/fit.json', report)
    print(run, index, report['status'], report['data_cost'], report['stability_cost'], json.dumps(report['stability_tally'])[:300], flush=True)
    return report


def run_fit(run):
    global TOML
    verify()
    q = result('qualification/summary.json')
    assert q['passed']
    cfg = RUNS[run]
    TOML = cfg.get('toml', TOML)
    enforced = [x for x in states()[0] if x['key'] not in q['excluded']]
    start, shifts = start_of(cfg)
    # Retreat anchor: the run's own start when stable (final set, variants), otherwise the final set (wide start).
    anchor, anchor_shifts = (start, shifts) if cfg['start'] != 'wide' else (s.parameter_mapping(STARTS['final']), SHIFTS['final'])
    endpoint, endpoint_shifts = None, None
    for index, scale in enumerate(cfg.get('stages', STAGES)):
        report = stage_fit(run, index, scale, start, shifts, enforced, cfg.get('held', ()), cfg.get('extra_shifts', ()),
                           rows_of(cfg), cfg.get('extra'))
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
    retreat(run, anchor, endpoint, enforced, rows_of(cfg), (anchor_shifts, endpoint_shifts))


def admissible(mapping, enforced, rows=None, suspects=(), *, route=None):
    """Admissibility on the full grid. States that failed at the previous point are searched first: any failure
    among them rejects the point without the full grid (same decision, a few searches instead of all of them)."""
    grid_call = grid if route is None else route.grid
    replay_call = replay if route is None else route.replay
    if suspects:
        tal = tally(grid_call(mapping, suspects))
        if tal['descent'] or tal['unavailable']:
            return False, dict(tal, screened=True, suspects=list(suspects)), None
    measured = grid_call(mapping, enforced)
    tal = tally(measured)
    failed = {r['key'] for r in measured if descent(r) or not r.get('available')}
    _, ok, cost = replay_call(mapping, rows)
    return tal['descent'] == 0 and not tal['unavailable'] and ok, dict(tal, suspects=[x for x in enforced if x['key'] in failed]), cost


def retreat(run, anchor, endpoint, enforced, rows=None, shifts=None, *, route=None, optimizer_report=None):
    if route is not None:
        OUT, write, segment = route.out, route.write, route.segment
        admissible = lambda *args: globals()["admissible"](*args, route=route)
    else:
        OUT, write, segment, admissible = (globals()[k] for k in ("OUT", "write", "segment", "admissible"))
    if (OUT / run / 'retreat.json').exists():
        return
    trace = []
    if endpoint is None:
        write(f'{run}/retreat.json', dict(t=0., reason='no stage returned an available 307-row endpoint', trace=trace, shifts=shifts[0]))
        ok, _, _ = admissible(anchor, enforced, rows)
        if ok:
            write(f'{run}/candidate.json', anchor)
        return
    passing, t, suspects = None, 1., ()
    while t > -1e-12:
        ok, tal, cost = admissible(segment(anchor, endpoint, t), enforced, rows, suspects)
        suspects = tal['suspects']
        trace.append(dict(t=t, admissible=ok, cost=cost, screened=tal.get('screened', False), **{k: tal[k] for k in ('descent', 'available', 'minimum_tau')}, unavailable=len(tal['unavailable'])))
        print(run, 'retreat', json.dumps(trace[-1]), flush=True)
        if ok:
            passing = t
            break
        t = round(t - .01, 10)
    if passing is not None and passing < 1.:
        low, high = passing, min(1., passing + .01)
        for _ in range(10):
            mid = (low + high) / 2
            ok, tal, cost = admissible(segment(anchor, endpoint, mid), enforced, rows, suspects)
            suspects = tal['suspects'] or suspects
            trace.append(dict(t=mid, admissible=ok, cost=cost, screened=tal.get('screened', False), **{k: tal[k] for k in ('descent', 'available', 'minimum_tau')}, unavailable=len(tal['unavailable'])))
            print(run, 'refine', json.dumps(trace[-1]), flush=True)
            low, high = (mid, high) if ok else (low, mid)
        passing = low
    t = 0. if passing is None else passing
    if passing is not None:
        write(f'{run}/candidate.json', segment(anchor, endpoint, t))
    a, e = shifts
    disposition = 'no candidate' if passing is None else 'optimizer endpoint' if t==1 else 'interpolated'
    write(f'{run}/retreat.json', dict(t=t, trace=trace, disposition=disposition,optimizer_converged=optimizer_report['status']=='converged' if optimizer_report else None,optimizer_cost=optimizer_report.get('data_cost',optimizer_report['final_cost']) if optimizer_report else None,retreat_cost=next((row['cost'] for row in reversed(trace) if row['admissible']),None),point_terminated_on_optimizer_tolerance=bool(t==1 and optimizer_report and optimizer_report['status']=='converged'), shifts={k: a.get(k, 0.) + t * (e.get(k, 0.) - a.get(k, 0.)) for k in a.keys() | e.keys()}))


def assess(run, rows=None):
    """Criteria 1-3 at a run's candidate against the final set on the same wheel; cost decides the outcome class."""
    verify()
    q = result('qualification/summary.json')
    enforced, offset = states()
    candidate = result(f'{run}/candidate.json')
    values, ok, cost = replay(candidate, rows)
    assert ok, 'candidate replay unavailable'
    g = grid(candidate, enforced + offset)
    write(f'{run}/grid.json.gz', g)
    enforced_rows = [r for r in g[:len(enforced)] if r['key'] not in q['excluded']]
    excluded_rows = [r for r in g[:len(enforced)] if r['key'] in q['excluded']]
    stab = dict(enforced=tally(enforced_rows), excluded=tally(excluded_rows), offset=tally(g[len(enforced):]), census=census(candidate, run))
    stability_pass = (stab['enforced']['descent'] == 0 and not stab['enforced']['unavailable'] and stab['offset']['descent'] == 0
                      and stab['census']['descent'] == 0 and stab['excluded']['descent'] == 0)
    base = metrics(result('qualification/final-replay.json'))
    m = metrics(values)
    checks = acceptance(m, base)
    a, f = s.parameter_values(candidate), s.parameter_values(s.parameter_mapping(STARTS['final']))
    scales = {q_['identity']: q_['scale'] for q_ in read(A6)['information_coordinates']}
    # A slope the final set does not declare is zero (#283).
    distance = {k: dict(final=f.get(k, 0.), candidate=a[k], scaled=(a[k] - f.get(k, 0.)) / scales[k] if k in scales else None)
                for k in a if a[k] != f.get(k, 0.)}
    t = result(f'{run}/retreat.json')['t']
    passed = stability_pass and all(c['passed'] for c in checks.values())
    summary = dict(run=run, t=t, cost=cost, final_cost=FINAL_COST, historical_final_cost=HISTORICAL_COST, cost_difference=cost - FINAL_COST, stability=stab, stability_passed=stability_pass,
                   metrics=m, baseline_metrics=base, checks=checks, passed=passed,
                   outcome_A=passed and t > 0 and cost < FINAL_COST * (1 - 1e-6), distance=distance,
                   near_final=all(abs(x['scaled']) <= 1 for x in distance.values() if x['scaled'] is not None),
                   candidate_sha256=hashlib.sha256(json.dumps(candidate, sort_keys=True).encode()).hexdigest())
    write(f'{run}/assessment.json', summary)
    write(f'{run}/replay.json', values)
    print(run, json.dumps({k: summary[k] for k in ('t', 'cost', 'stability_passed', 'passed', 'outcome_A', 'near_final')}), flush=True)


if __name__ == '__main__':
    # Historical #255 commands select their wheel; importing preserves the active pin.
    s.ENGINE_WHEEL_SHA256, s.ENGINE_COMMIT = SHA, COMMIT
    command = sys.argv[1]
    spec_261()
    if command == 'qualify':
        qualify()
    elif command == 'old-wheel-replay':
        old_wheel_replay()
    elif command == 'fit':
        run_fit(sys.argv[2])
    elif command == 'assess':
        TOML = RUNS[sys.argv[2]].get('toml', TOML)
        assess(sys.argv[2])  # acceptance is defined on the 307 standard rows for every run
    elif command == 'extras':
        TOML = RUNS[sys.argv[2]].get('toml', TOML)
        extras(sys.argv[2])
    elif command == 'select':
        select()
    else:
        raise SystemExit(__doc__)
