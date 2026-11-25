"""Serial study-wheel replays with per-item deadlines and durable checkpoints."""
# ruff: noqa: E402
from collections import Counter
from copy import copy
import os
import signal
import sys
from time import monotonic
if __package__:
    from .records import HERE, ROOT, OUT, MEA, LIMITS, Sources, replay_path, write
else:
    from records import HERE, ROOT, OUT, MEA, LIMITS, Sources, replay_path, write
os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[:8]))
for name in ('AGENT_HEAVY_CORES', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS'):
    os.environ[name] = '1'
sys.path.insert(0, str(HERE.parent / 'round_7'))
from calculations import Route, a, r
from receivers import AMP, DEA, ExpandedDEA
from mdea_reference import FixedReference, predicates, route, seed_state, standard_derivatives
from part_ii import epcsaft, eq, jsonable, reg, stable
from phases import fixed
from classify_descents import COINCIDENCE, matched, pressure_roots
from shared_bicarbonate_417 import dilute_vapor_connection
from mea_pressure import membership
WORK = ROOT / 'build/round-8'
def endpoint(src, path):
    return src.core(path + '/selection.json.gz')['selected'][2]
def grid_split(src):
    d = src.core('C/salt/search-outcome.json.gz')
    return next(q for q in d['classifications'] if q['key'] in d['confirmed'])
def phase_seed(entry):
    return next(q for q in entry['attempts'] if q['confirmed'])

def feed(problem, ids):
    values = problem.feed.values
    return dict(values) if isinstance(values, dict) else dict(zip(ids,values,strict=True))

def selected_reference(spec, amine, component):
    rows = [q for q in spec.inputs['observations']['fitted'] if q.get('problem') and q['kind'] in ('pressure','partial_pressure')
            and (amine!='MEA' or q['kind']=='partial_pressure')
            and feed(spec.problems[q['problem']],spec.parameters.component_ids).get('carbon-dioxide',0) > 0]
    def meta(q):
        return membership()[q['identity']] if amine=='MEA' else q['row']
    def group(q):
        return meta(q).get('source_key',q['identity'].split(':')[0])
    source = Counter(map(group, rows)).most_common(1)[0][0]
    pool = [q for q in rows if group(q) == source]
    def loading(q):
        amounts = feed(spec.problems[q['problem']],spec.parameters.component_ids)
        return amounts['carbon-dioxide']/amounts[component]
    pool.sort(key=lambda q: (loading(q),
                             float(meta(q).get('source_row') or meta(q).get('row') or q['observation_order'])))
    return pool[len(pool)//2], source, len(pool)

def amp_caloric_model(spec, neutral, h0, s0):
    P0 = spec.thermal.standard_pressure
    zero = epcsaft.IdealInterval(250.,500.,True,True,
        epcsaft.IdealCorrelation(epcsaft.IdealPolynomial([0.],350.,0.,0.),P0))
    shifted = epcsaft.IdealInterval(250.,500.,True,True,
        epcsaft.IdealCorrelation(epcsaft.IdealPolynomial([0.],350.,h0,s0),P0))
    intervals = [[shifted] if k=='aminomethylpropanol' else [zero] if k in neutral else []
                 for k in spec.parameters.component_ids]
    return epcsaft.Mixture(spec.parameters, thermochemistry=epcsaft.ThermochemistryRecord(P0,intervals))

def derivative(spec, problem, pressure, feed_amine, amine=None):
    problem.pressure = type(problem.pressure).fixed(pressure)
    model = spec.model
    sol = eq.solve_equilibrium(model, problem)
    assert sol.requested_tolerance_met, sol.message
    warm = amine in ('MEA','DEA')
    gauge = None
    if amine == 'AMP':
        neutral = ('water','carbon-dioxide','aminomethylpropanol')
        model = amp_caloric_model(spec,neutral,0.,0.)
        shifted = amp_caloric_model(spec,neutral,1000.,1.)
        center, alternate = [eq.solve_equilibrium(m,problem) for m in (model,shifted)]
        assert center.requested_tolerance_met and alternate.requested_tolerance_met
        gauge = dict(neutral_species=neutral, shifted_species='aminomethylpropanol', anchor_T_K=350.,
                     interval_K=[250.,500.], P_Pa=spec.thermal.standard_pressure, Cp_J_mol_K=0.,
                     baseline=dict(h_J_mol=0.,s_J_mol_K=0.), shifted=dict(h_J_mol=1000.,s_J_mol_K=1.),
                     max_center_x_difference=[max(abs(x-y) for x,y in zip(
                         v.phase_mole_fractions(0),sol.phase_mole_fractions(0),strict=True)) for v in (center,alternate)])
        sol = center
    rows = standard_derivatives(model,problem,sol,gibbs_helmholtz=True,warm_start=warm)
    if gauge:
        shifted_rows = standard_derivatives(shifted,problem,alternate,gibbs_helmholtz=True)
        for row, readback in zip(rows,shifted_rows,strict=True):
            row['shifted_gauge'] = readback
    return dict(T_K=sol.temperature, P_Pa=pressure, feed_mol=feed(problem,spec.parameters.component_ids),
                amount_mol=sol.amounts[0], x=sol.phase_mole_fractions(0), amine_feed_mol=feed_amine,
                roots=pressure_roots(model, sol.temperature, pressure, sol.phase_mole_fractions(0), sol.molar_densities[0]),
                derivatives=rows, **({'caloric_gauge':gauge} if gauge else {}))

def references(src, work):
    configs = [('MEA', None, src.core('E/selection.json')['parameters']),
               ('DEA', ExpandedDEA(DEA, WORK/'DEA'), endpoint(src,'F')),
               ('AMP', AMP.ExpandedPressure(AMP.DECLARATION, WORK/'AMP-expanded'), endpoint(src,'AMP/free')),
               ('MDEA', route('salt','round-8-tracking'), endpoint(src,'C/salt'))]
    for i,(name, run, point) in enumerate(configs):
        def fitted():
            spec = run.bind(point) if run else r.bind(point)
            component = run.config['amine'] if run else 'monoethanolamine'
            row, source, count = selected_reference(spec, name, component)
            bubble = copy(spec.problems[row['problem']])
            solved = eq.solve_equilibrium(spec.model, bubble)
            assert solved.requested_tolerance_met, solved.message
            p = copy(bubble)
            p.phases = [copy(bubble.phases[0])]
            p.phases[0].amount = eq.Free()
            f = feed(bubble,spec.parameters.component_ids)
            n = f[component]+f.get(f"protonated-{component}",0)+f.get("carbamate-anion",0)
            return dict(derivative(spec, reg.stability(spec.parameters,p,scale=1.).problem, solved.pressure, n, name), observation=row['identity'], source=source,
                        source_count=count, pressure_basis='calculated absolute total bubble pressure', source_row=row['row'])
        work(name, {'MEA':'warm MEA', 'DEA':'warm DEA', 'AMP':'paired AMP gauges'}.get(name,'fitted branch'), fitted, 1)
    entry = grid_split(src)
    run, point = configs[-1][1:]
    spec = run.bind(point)
    state, P, pair = seed_state(spec, entry), entry['pressure_Pa'], phase_seed(entry)
    for index in (-1, 0, 1):
        def split_derivative():
            p = run.stability_row(spec, state, 1.).problem
            if index >= 0:
                x, n = pair['phases'][index], pair['amounts_mol'][index]
                inventory = p.feed
                inventory.values = [n*v for v in x]
                p.feed = inventory
                phase = p.phases[0]
                phase.composition_guess, phase.packing_guess = x, pair['packings'][index]
                p.phases = [phase]
            return derivative(spec, p, P, state['stock']['methyldiethanolamine'])
        work(('parent','daughter-1','daughter-2')[index+1], 'split inventory' if index >= 0 else 'grid parent',
             split_derivative, 2 if index == 0 else 1)
    for cls,label in ((Route,'tracking'),(FixedReference,'100-kPa')):
        run = route('salt','round-8-reference-control',cls)
        work(label, 'reference control', lambda: predicates(fixed(run,run.bind(point),state,P,dict(pair=pair),mdea=True),
                                                           tolerance=1e-10), 2 if cls is Route else 1)

def mdea_witnesses(src, work, *, released=None):
    if released is None:
        point = endpoint(src, 'C/salt')
        run = route('salt','round-8-witness')
        rows = src.core('C/salt/search-0.json.gz')
        classifications = src.core('C/salt/search-outcome.json.gz')['classifications']
    else:
        run,point,rows,classifications = released
    spec = run.bind(point)
    model = spec.model
    search = {q['key']:q for q in rows if q['descent']}
    entries = [e for e in classifications if not e['key'].startswith('grid:')]
    for i,e in enumerate(entries):
        def readback():
            row = search[e['key']]
            basis = row.get('pressure_basis',{})
            item = run.stability_row(spec,seed_state(spec,e),1.)
            p = item.problem
            pressure = basis.get('search_pressure_Pa') or e['pressure_Pa']
            p.pressure = type(p.pressure).fixed(pressure)
            witnesses = [dict(w,origin='native') for w in row.get('witnesses',[])]
            retained = e.get('supplied_pressure_roots',[])
            endpoints = [dict(w['witness']['phase'],origin='supplied', evidence=w,
                              P_Pa=row.get('supplied_parent_pressure_Pa') or e['pressure_Pa']) for w in retained]
            distinct = []
            for w in witnesses:
                coincident = next((v for v in endpoints+distinct if v.get('P_Pa')==pressure
                        and max(abs(w['packing']-v['packing']),*(abs(x-y) for x,y in zip(w['composition'],v['composition'],strict=True)))<COINCIDENCE),None)
                if coincident:
                    coincident.setdefault('coincident_native', []).append(w)
                else:
                    distinct.append(dict(w,P_Pa=pressure))
            if distinct:
                phases,_,repeated,_ = stable._applicable(item,distinct,set(range(len(spec.parameters.component_ids))))
                options = eq.StabilityOptions()
                options.prepared_trials = eq.prepare_supplied_trials(model,e['temperature_K'],phases)
                parent = eq.solve_equilibrium(model,p)
                assert parent.requested_tolerance_met, parent.message
                report = eq.stability_test(eq.compile_problem(model,p),parent,options)
                for idx,w in repeated:
                    t = report.trials[idx]
                    q = t.quantities
                    rho = q.get('molar_density_mol_m3')
                    w['evidence'] = dict(witness=dict(evidence=t.evidence, quantities=q),
                        roots=pressure_roots(model,e['temperature_K'],pressure,w['composition'],rho) if rho else [])
            for w in endpoints+distinct:
                q = w['evidence']['witness']['quantities']
                roots = matched(w['evidence']['roots'],1e-10)
                root = min(roots,key=lambda v:v['log_density_distance'],default={})
                if root.get('returned')=='unspecified':
                    trace, connected = dilute_vapor_connection(model,e['temperature_K'],w['composition'],q['molar_density_mol_m3'])
                    w['dilute_trace'] = dict(trace=trace,connected=connected)
            return endpoints+distinct
        if not search[e['key']].get('pressure_basis',{}).get('model_bubble_pressure_Pa'):
            def bubble():
                reference = run.stability_row(spec,seed_state(spec,e),1.).pressure_reference
                sol = eq.solve_equilibrium(model,reference)
                return dict(P_Pa=sol.pressure if sol.requested_tolerance_met else None,message=sol.message)
            work('bubble:'+e['key'],'missing matched bubble',bubble,len(entries)-i)
        work(e['key'],'matched witnesses and ambiguous-root traces',readback,len(entries)-i)

def amp_controls(src, work):
    run = Route(AMP.DECLARATION, WORK/'AMP')
    spec = run.bind(endpoint(src,'AMP/free'))
    bank = {q['key']:q for q in src.read('analyses/amp_transfer/results/retransfer-412-f2-05e94210/main/phase-classification-1.json.gz')['states']}
    controls = [q for q in src.read('analyses/round_3/results/q1.json')['rows'] if q['pressure_basis']=='measured pressure']
    for i,q in enumerate(controls):
        def evaluate():
            archive = bank[q['key']]
            witness = next(w for w in archive['supplied_pressure_roots'] if stable.supplied_negative(w['witness']))
            witness = dict(witness['witness']['phase'], packing=witness.get('reclosed_quantities',witness['witness']['quantities'])['packing_fraction'])
            old = q['free']
            result = fixed(run,spec,dict(problem=q['key']),old['P_Pa'],dict(pair=phase_seed(archive),witness=witness),assemblages=True)
            assert (result['feed_mol'],result['T_K'],result['P_Pa']) == (old['feed_mol'],old['T_K'],old['P_Pa'])
            return result
        work(q['key'], 'AMP fixed pressure', evaluate, len(controls)-i)
def endpoint_phases(src, work):
    entry = grid_split(src)
    targeted = src.core('C/salt/rms-fixed-pressures.json.gz')['pressure_262_MPa']
    for i in range(2):
        point = src.core(f'C/salt/attempts/fit-{i}.json.gz')['outcome.json']['point']
        run = route('salt', 'round-8-endpoints')
        spec = run.bind(point)
        state = seed_state(spec,entry)
        tstate = dict(T=targeted['T_K'],stock={k:v for k,v in targeted['feed'].items() if v and k!='carbon-dioxide'},a=1.368)
        cases = [(state, entry['pressure_Pa'], phase_seed(entry)), (tstate,targeted['P_Pa'],phase_seed(targeted))]
        for state,p,seed in cases:
            work(f'MDEA-{i}:{p}', 'MDEA fixed pressure', lambda: fixed(run,spec,state,p,dict(pair=seed),mdea=True), 4-2*i-cases.index((state,p,seed)))
    archive = src.display('amp-common-pressure')
    prior = archive['outcomes']['free']['fixed']
    seed = src.read('analyses/mea_parameter_bundle/results/reference-states-428/amp.json')['split']
    for i in range(2):
        run = Route(AMP.DECLARATION,WORK/'AMP')
        spec = run.bind(src.core(f'AMP/free/fit-{i}.json.gz')['point'])
        work(f'AMP-{i}', 'AMP worked state', lambda: fixed(run,spec,archive['state'],prior['P_Pa'],dict(pair=seed)), 2-i)

    state = stable.states()[0][0]
    for label in ('F2','F4'):
        def mea_control():
            mapping = src.read(MEA+f'{label}/parameters.json')
            spec = r.bind(mapping.get('result',mapping))
            item = stable.stability_row(spec,state,1.)
            item.problem.pressure = type(item.problem.pressure).fixed(100000.)
            item.pressure_reference = None
            return dict(state=state,P_Pa=100000.,search=stable.stability_payload(reg.predict(spec.model,item)))
        work(f'MEA-{label}','MEA fixed-pressure control',mea_control,2 if label=='F2' else 1)

def execute(item):
    src, rows, projections, outstanding = Sources(), {}, {}, []
    start, limit = monotonic(), 1.5*LIMITS[item-1]
    prior = r.read(replay_path(item)) if replay_path(item).exists() else {}
    rows.update(prior.get('rows',{}))
    src.hashes = prior.get('sources',{}).copy()
    projections.update(prior.get('projections',{}))
    def checkpoint():
        write(replay_path(item), jsonable(dict(rows=rows, outstanding=outstanding, seconds=monotonic()-start+prior.get('seconds',0),
                                             projections=projections, sources=src.hashes, wheel=wheel)))
    def deadline(*_):
        raise TimeoutError('per-item stop')
    def work(key, kind, fn, remaining):
        if key in rows and 'value' in rows[key] and key not in sys.argv[-1].removeprefix('--retry=').split(','):
            return
        elapsed = monotonic()-start+prior.get('seconds',0)
        projected = elapsed + projections.get(kind, 0)*remaining
        if projected >= limit:
            outstanding.append(dict(key=key, reason=f'{kind} projects {projected:.2f} s against {limit:g} s'))
        else:
            tick = monotonic()
            history = rows.get(key)
            signal.setitimer(signal.ITIMER_REAL, max(.0001, limit-elapsed))
            try:
                rows[key] = dict(value=fn())
            except (RuntimeError, ValueError, AssertionError, KeyError, TypeError, StopIteration, TimeoutError) as exc:
                rows[key] = dict(refusal=f'{type(exc).__name__}: {exc}')
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            rows[key]['seconds'] = monotonic()-tick
            if history:
                rows[key]['prior_attempt'] = history
            projections.setdefault(kind, rows[key]['seconds'])
        checkpoint()
    signal.signal(signal.SIGALRM, deadline)
    {1:references,2:mdea_witnesses,4:amp_controls,6:endpoint_phases}[item](src,work)
    checkpoint()
if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    a.study.reuse.bind_wheel()
    r.verify()
    wheel = dict(wheel_sha256=r.SHA,engine_commit=r.COMMIT,installed_members_verified=True,
                 cpu_affinity=sorted(os.sched_getaffinity(0)))
    write(OUT/'installed-wheel.json',dict(wheel_sha256=r.SHA,engine_commit=r.COMMIT,wheel_filename=r.WHEEL.name,
                                         installed_members_verified=True,cpu_affinity=wheel['cpu_affinity']))
    for arg in sys.argv[1:]:
        if not arg.startswith('--retry='):
            execute(int(arg))
