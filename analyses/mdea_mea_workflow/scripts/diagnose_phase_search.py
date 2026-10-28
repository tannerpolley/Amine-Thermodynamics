"""Issue 222 stage-2 phase-search diagnosis: unresolved trials, Merkley liquid splits, one-change probes.

Diagnosis only: no fitting, no change to frozen choices. Every search uses the
stage-2 trial declaration (liquid on all species, vapor on the neutral species)
unless a probe names a different trial support.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import collections, concurrent.futures as futures, copy, csv, gzip, hashlib, importlib.util, json, math, multiprocessing, re, sys
from pathlib import Path

AN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stage2', AN/'scripts/stage2.py')
s = importlib.util.module_from_spec(spec); sys.modules['stage2'] = s; spec.loader.exec_module(s)  # registered so pool workers can unpickle its functions
p, d, j, eq = s.p, s.d, s.j, s.eq
W, M, H, C = p.W, p.M, p.H, p.C
HCO3, CO3 = 'bicarbonate-anion', 'carbonate-anion'
OUT = 'results/diagnosis-phase-search'
WORKERS = 16  # owner cap (2026-10-28), one BLAS thread per process
NEUTRAL = list(p.published.NEUTRAL)
DEFAULT = [('liquid', list(d.SPECIES)), ('vapor', NEUTRAL)]
REGISTRY = json.loads((AN/'results/compressed-evidence.json').read_text())


def pool(fn, jobs):
    with futures.ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs)), mp_context=multiprocessing.get_context('fork')) as ex:
        return list(ex.map(fn, jobs))
s.poolmap = pool  # the stage-2 runner's searches, capped at 16 processes


def load(path):
    """Retained phase JSON; a gzip copy is decompressed in memory and checked against its raw SHA-256."""
    path = AN/path
    if path.exists():
        return json.loads(path.read_text())
    raw = gzip.decompress((path.parent/(path.name+'.gz')).read_bytes())
    key = str(path.relative_to(AN.parents[1]))
    assert hashlib.sha256(raw).hexdigest() == REGISTRY['files'][key]['raw_sha256'], key
    return json.loads(raw)


def write(path, obj):
    """JSON output; above 5 MB it is stored as level-9 gzip with mtime 0 and registered."""
    p.write(f'{OUT}/{path}', obj)
    target = AN/OUT/path
    raw = target.read_bytes()
    if len(raw) > 5*2**20:
        gz = target.parent/(target.name+'.gz')
        gz.write_bytes(gzip.compress(raw, 9, mtime=0)); target.unlink()
        REGISTRY['files'][str(target.relative_to(AN.parents[1]))] = dict(raw_bytes=len(raw), raw_sha256=hashlib.sha256(raw).hexdigest(),
            gz=str(gz.relative_to(AN.parents[1])), gz_bytes=gz.stat().st_size, gz_sha256=hashlib.sha256(gz.read_bytes()).hexdigest())
        (AN/'results/compressed-evidence.json').write_text(json.dumps(REGISTRY, indent=1)+'\n')


def vector(label):
    """Stage-2 endpoint document: A1/B1 from the joint fit; others from their retained endpoint.json."""
    return s.endpoint(label)[0] if label in ('A1', 'B1') else load(label)


def declare(doc):
    """Model and all fitted/comparison problems for one vector; problems do not depend on the parameters."""
    s.setup(doc)
    meta, _, _ = s.fitted_items()
    cmeta, _ = s.comparison_items()
    return {**{f'fit:{i}:{k}': (meta[i], q) for i, ps in enumerate(s.problems) for k, q in enumerate(ps)},
            **{f'comparison:{i}:{k}': (cmeta[i], q) for i, ps in enumerate(s.comparison_problems) for k, q in enumerate(ps)}}


def conditions(meta, prob):
    feed = prob.feed.values
    nw, nm, nc = feed.get(W, 0.), feed.get(M, 0.), feed.get(C, 0.)
    free = not isinstance(prob.P, float)
    return dict(group=meta['group'], source_row=meta['row'].get('source_row', ''), T_K=prob.T, P_Pa=prob.P.guess if free else prob.P,
                pressure='bubble (free)' if free else 'fixed', alpha=nc/nm if nm else None,
                MDEA_mass_percent=100*nm*.1191622/(nm*.1191622+nw*.01801528) if nm else 0.)


def search(prob, trials=DEFAULT):
    """Single-liquid solve, then the native tangent-plane search on the declared trial supports."""
    state = eq.solve_equilibrium(s.model, prob)
    options, t = eq.StabilityOptions(), copy.copy(prob)
    t.phases = [eq.Phase(f'trial-{n}', kind=kind, support=support) for n, (kind, support) in enumerate(trials)]
    options.trials = t._native(s.model).phases
    native = eq.stability_test(eq.compile_problem(s.model, prob), state, options)
    ids = list(s.params.component_ids)
    rows = [dict(kind=r.phase.kind.name.lower(), support=[ids[i] for i in r.phase.support], phase=dict(kind=r.phase.kind.name.lower(), support=list(r.phase.support)),
                 seed=r.seed, evidence=r.evidence, message=r.message, resolved_descent=r.resolved_descent,
                 quantities=p.shared._jsonable(r.quantities), composition=list(r.composition),
                 split_coordinates=list(r.split_coordinates), raw_coordinates=list(r.raw_coordinates)) for r in native.trials]
    liquid = [r['quantities']['split_delta_g_over_rt'] for r in rows if r['resolved_descent'] and r['kind'] == 'liquid']
    return dict(converged=state.requested_tolerance_met, state_message=state.message, x=dict(zip(ids, state.mole_fractions)),
                amounts=list(state.amounts), message=native.message, completed=native.completed,
                unresolved=int(native.message.split('unresolved trials ')[1].split(';')[0]),
                liquid_split_delta_g_over_rt=min(liquid, default=None), vapor_descent=any(r['resolved_descent'] and r['kind'] == 'vapor' for r in rows),
                trials=rows, state=state)


# ---------- 1. unresolved trials ----------
def driver(message):
    m = re.match(r'(\w+): residual (\S+) against EQUILIBRIUM_ROW_RESIDUAL \S+ after (\d+) iterations', message or '')
    return dict(driver=m[1], residual=float(m[2]), iterations=int(m[3])) if m else dict(driver=None)


def reconstruct(w, z):
    """Liquid branch of reconstruct_trial_composition at Engine 3e83e19c (phase_stability.cpp:362-407), replayed in float64."""
    w = list(w)
    pos = sum(zi*wi for zi, wi in zip(z, w) if zi > 0); neg = -sum(zi*wi for zi, wi in zip(z, w) if zi < 0)
    plus = max((i for i in range(len(w)) if z[i] > 0), key=lambda i: w[i])
    minus = max((i for i in range(len(w)) if z[i] < 0), key=lambda i: w[i])
    ratio = math.sqrt(neg/pos)
    w = [wi*ratio if zi > 0 else wi/ratio if zi < 0 else wi for zi, wi in zip(z, w)]
    total = 0.
    for wi in w: total += wi
    w = [wi/total for wi in w]
    total = charge = 0.
    for zi, wi in zip(z, w): total += wi; charge += zi*wi
    dp = (-charge + z[minus]*(total-1.))/(z[plus]-z[minus])
    pivots = dict(plus_before=w[plus], minus_before=w[minus], sum_minus_one=total-1., charge=charge, dp=dp)
    w[plus] += dp; w[minus] += 1.-total-dp
    return dict(pivots, plus=plus, minus=minus, plus_after=w[plus], minus_after=w[minus], destroys_support=min(w) <= 0.)


def trial_class(t, carbon_free):
    tail = t['message'].split('; ', 1)[1] if '; ' in t['message'] else ''
    if t['evidence'] == 'negative_plane_without_positive_donor':
        return 'negative tangent-plane distance, no positive donor phase' + (' (carbon-free state)' if carbon_free else '')
    return f"{t['evidence']}: {tail or t['message']}"


def classify():
    sets = {'A1': 'results/stage2/A1/fitted-phase.json', 'B1': 'results/stage2/B1/fitted-phase.json',
            'A1 full search': f'{OUT}/reproduce/A1/phase.json', 'B1 full search': f'{OUT}/reproduce/B1/phase.json',
            'A sensitivity': 'results/stage2-diagnostic/A1-removed-Merkley/phase.json', 'B sensitivity': 'results/stage2-diagnostic/B1-removed-Merkley/phase.json',
            **{f'{v} narrowed step {k}': f'results/stage2-narrowed/{v}1/step-{k}/phase.json' for v in 'AB' for k in range(1, 7)}}
    states = declare(vector('A1'))
    ids = list(s.params.component_ids)
    charge = {W: 0, M: 0, C: 0, H: 1, 'hydronium-cation': 1, 'hydroxide-anion': -1, HCO3: -1, CO3: -2}
    z = [charge[c] for c in ids]
    rows, trial_rows, witnesses = [], [], []
    for name, path in sets.items():
        saturation = {r['index']: r for r in load(str(Path(path).parent/'saturation-phase-inputs.json'))} if 'fitted-phase' not in path else {}
        for r in load(path):
            index = f"fit:{r['index']}" if r['index'][0].isdigit() else r['index']
            if index.startswith('saturation'):
                q = saturation[index]
                where = dict(group=index.split(':')[1], source_row=index.split(':')[2], T_K=q['T_K'], P_Pa=q['P_Pa'], pressure='fixed',
                             alpha=q.get('alpha_phase'), MDEA_mass_percent=100*q['mass_fraction'])
            else:
                where = conditions(*states[index])
            report = r.get('stability', {})
            x = dict(zip(r.get('component_ids', ids), r.get('mole_fractions', [])[:len(ids)]))
            carbon_free = bool(x) and x.get(C, 0.)+x.get(HCO3, 0.)+x.get(CO3, 0.) == 0.
            bad = [t for t in report.get('trials', []) if t['evidence'] in ('unresolved', 'indeterminate', 'negative_plane_without_positive_donor')]
            if 'error' in r: kind = f"state not searched: {r['error']}"
            elif not r.get('requested_tolerance_met'): kind = 'single-liquid solve below tolerance'
            elif not bad: kind = 'resolved'
            else: kind = ' | '.join(sorted({trial_class(t, carbon_free) for t in bad}))
            split = min((t['quantities']['split_delta_g_over_rt'] for t in report.get('trials', []) if t['resolved_descent'] and t['phase']['kind'] == 'liquid'), default=None)
            rows.append(dict(set=name, index=index, **where, carbon_free_state=carbon_free, unresolved_trials=len(bad), class_=kind, liquid_split_delta_g_over_rt=split))
            if split is not None:
                # Is the liquid-kind witness a dense liquid, or the vapor descent reached through a liquid-kind trial?
                trials = report['trials']
                best = min((t for t in trials if t['resolved_descent'] and t['phase']['kind'] == 'liquid'), key=lambda t: t['quantities']['split_delta_g_over_rt'])
                new = d.phases(best, r['component_ids'])[-1]
                vapor = min((t['quantities']['split_delta_g_over_rt'] for t in trials if t['resolved_descent'] and t['phase']['kind'] == 'vapor'), default=None)
                witnesses.append(dict(set=name, index=index, **where, liquid_split_delta_g_over_rt=split, split_error_over_rt=best['quantities']['split_error_estimate_over_rt'],
                    seed=best['seed'], present_liquid_packing_fraction=r['stability']['present_phases'][0].get('packing_fraction'),
                    trial_phase_packing_fraction=new['packing_fraction'], trial_phase_amount_mol=new['amount_mol'],
                    **{f'trial_x_{c}': new['x'][c] for c in r['component_ids']}, vapor_split_delta_g_over_rt=vapor,
                    liquid_minus_vapor_delta_g_over_rt=None if vapor is None else split-vapor))
            for t in bad:
                record = dict(set=name, index=index, group=where['group'], T_K=where['T_K'], alpha=where['alpha'], kind=t['phase']['kind'], seed=t['seed'],
                              evidence=t['evidence'], native_message=t['message'], **driver(t['message']))
                if 'reconstruction destroys support' in t['message']:
                    # raw coordinates start with ln x on the trial support (trial_coordinates, phase_stability.cpp:343)
                    support = t['phase']['support']; wv = [0.]*len(ids)
                    for i, v in zip(support, t['raw_coordinates']): wv[i] = math.exp(v)
                    replay = reconstruct([wv[i] for i in support], [z[i] for i in support])
                    record.update(raw_x={ids[i]: wv[i] for i in support}, replay=replay)
                trial_rows.append(record)
        print(name, collections.Counter(r['class_'] for r in rows if r['set'] == name), flush=True)
    write('unresolved/records.json', rows)
    write('unresolved/liquid-witnesses.json', witnesses)
    with (AN/OUT/'unresolved/liquid-witnesses.csv').open('w', newline='') as stream:
        out = csv.DictWriter(stream, fieldnames=list(witnesses[0]), lineterminator='\n'); out.writeheader(); out.writerows(witnesses)
    write('unresolved/trials.json', trial_rows)
    with (AN/OUT/'unresolved/records.csv').open('w', newline='') as stream:
        out = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n'); out.writeheader()
        out.writerows([r for r in rows if r['class_'] != 'resolved'])
    # Same physical states? Compare unresolved index sets on the shared fitted/comparison grid.
    by_set = {n: {r['index'] for r in rows if r['set'] == n and r['class_'] != 'resolved' and not r['index'].startswith('saturation')} for n in sets}
    by_class = collections.defaultdict(collections.Counter)
    for r in rows: by_class[r['set']][r['class_']] += 1
    recon = [t for t in trial_rows if 'replay' in t]
    gas = [w for w in witnesses if w['trial_phase_packing_fraction'] < .05]
    summary = dict(
        liquid_witnesses=dict(records=len(witnesses), trial_phase_packing_fraction_below_0_05=len(gas),
            max_trial_phase_packing_fraction=max(w['trial_phase_packing_fraction'] for w in witnesses),
            with_vapor_descent=sum(w['vapor_split_delta_g_over_rt'] is not None for w in witnesses),
            max_abs_liquid_minus_vapor_delta_g_over_rt=max((abs(w['liquid_minus_vapor_delta_g_over_rt']) for w in witnesses if w['vapor_split_delta_g_over_rt'] is not None), default=None),
            seeds=dict(collections.Counter(w['seed'] for w in witnesses)), groups=dict(collections.Counter(w['group'] for w in witnesses))),
        counts={n: dict(c) for n, c in by_class.items()},
        unresolved_indices_shared_by_all_754_record_sets=len(set.intersection(*[v for n, v in by_set.items() if n not in ('A1', 'B1')])),
        unresolved_indices_union_754_record_sets=len(set.union(*[v for n, v in by_set.items() if n not in ('A1', 'B1')])),
        unresolved_indices_per_set={n: len(v) for n, v in by_set.items()},
        jaccard_to_A1_full_search={n: len(v & by_set['A1 full search'])/max(1, len(v | by_set['A1 full search'])) for n, v in by_set.items()},
        trial_drivers=[dict(evidence=k[0], kind=k[1], driver=k[2], at_200_iterations=k[3], trials=v)
                       for k, v in collections.Counter((t['evidence'], t['kind'], t['driver'], t.get('iterations') == 200) for t in trial_rows).items()],
        max_trial_iterations=max((t['iterations'] for t in trial_rows if t.get('iterations')), default=None),
        native_refusal_tails=dict(collections.Counter(t['native_message'].split('; ', 1)[1] if '; ' in t['native_message'] else '(none)' for t in trial_rows)),
        reconstruction=dict(trials=len(recon), replay_reproduces_failure=sum(t['replay']['destroys_support'] for t in recon),
                            seeds=dict(collections.Counter(t['seed'] for t in recon)),
                            max_charged_pivot_before=max(max(t['replay']['plus_before'], t['replay']['minus_before']) for t in recon) if recon else None,
                            max_abs_sum_minus_one=max(abs(t['replay']['sum_minus_one']) for t in recon) if recon else None))
    write('unresolved/summary.json', summary)
    print(json.dumps({k: summary[k] for k in ('liquid_witnesses', 'native_refusal_tails', 'reconstruction')}, indent=1))


def reproduce():
    """Full stage-2 phase search (fitted, comparison and saturation states) at the A1 and B1 endpoints."""
    s.OUT = f'{OUT}/reproduce'
    for label in ('A1', 'B1'):
        s.search_document(vector(label), label)
        # stage2.write leaves files uncompressed; gzip the large one here
        path = AN/s.OUT/label/'phase.json'; obj = json.loads(path.read_text()); path.unlink()
        write(f'reproduce/{label}/phase.json', obj)


def repair_job(job):
    index, trials = job
    prob = STATES[index][1] if index in STATES else SATURATION[index]
    r = search(prob, trials); r.pop('state')
    return dict(index=index, trials_declared=trials, **r)


def repair():
    """Admitted controls at every unresolved A1/B1 state: carbon-free trial supports, or an added ion-free liquid face."""
    global STATES, SATURATION
    rows = load(f'{OUT}/unresolved/records.json')
    out = {}
    for label in ('A1', 'B1'):
        STATES = declare(vector(label))
        SATURATION = {r['index']: j.problem(r['T_K'], r['P_Pa'], j.water(r['mass_fraction']), r['alpha_phase'])
                      for r in load(f'{OUT}/reproduce/{label}/saturation-phase-inputs.json') if r.get('status') == 'Available'}
        jobs = []
        for r in rows:
            if r['set'] != f'{label} full search' or r['class_'] == 'resolved': continue
            prob = STATES[r['index']][1] if r['index'] in STATES else SATURATION[r['index']]
            support = list(prob.phases[0].support)
            if r['carbon_free_state']:
                # Trial phases restricted to species reachable from a carbon-free feed.
                jobs.append((r['index'], [('liquid', [c for c in support if c not in (C, HCO3, CO3)]), ('vapor', [c for c in NEUTRAL if c != C and c in support])]))
            else:
                jobs.append((r['index'], DEFAULT + [('liquid', [c for c in NEUTRAL if c in support])]))
        results = pool(repair_job, jobs)
        for q in results:
            q['trials'] = [{k: t[k] for k in ('kind', 'support', 'seed', 'evidence', 'message', 'resolved_descent', 'composition')} | dict(tpd_over_rt=t['quantities'].get('tpd_over_rt')) for t in q['trials']]
        out[label] = results
        print(label, collections.Counter((q['trials_declared'][0][1].__len__(), q['message']) for q in results), flush=True)
    write('unresolved/repair.json', out)


# ---------- 2. resolved splits ----------
WITNESSES = ('fit:83:0', 'fit:125:1', 'fit:126:1', 'fit:127:1', 'fit:128:1')


def apparent(x):
    amine, carbon = x[M]+x[H], x[C]+x[HCO3]+x[CO3]
    return dict(water=x[W], amine=amine, carbon=carbon, loading=carbon/amine, MDEA_mass_percent_CO2_free=100*amine*.1191622/(amine*.1191622+x[W]*.01801528),
                ions=sum(x[c] for c in x if c not in NEUTRAL))


def split_job(job):
    label, index = job
    meta, prob = STATES[index]
    r = search(prob); single = r.pop('state')
    record = dict(vector=label, index=index, **conditions(meta, prob), single_liquid=r['x'], search_message=r['message'], liquid_split_delta_g_over_rt=r['liquid_split_delta_g_over_rt'])
    ids = list(s.params.component_ids)

    def converge(kind):
        found = [t for t in r['trials'] if t['resolved_descent'] and t['kind'] == kind]
        if not found: return None
        best = min(found, key=lambda t: t['quantities']['split_delta_g_over_rt'])
        seeds = d.phases(best, ids)
        two = copy.copy(prob)
        # stage 2 converged two full-support liquids; the gas-liquid check declares the new phase vapor on the neutral species
        two.phases = [eq.Phase('L1', kind='liquid', support=p.published.SPECIES, composition_guess=seeds[0]['x'], packing_guess=seeds[0]['packing_fraction']),
                      eq.Phase('L2', kind='liquid', support=p.published.SPECIES, composition_guess=seeds[1]['x'], packing_guess=seeds[1]['packing_fraction'])
                      if kind == 'liquid' else eq.Phase('V', kind='vapor', support=NEUTRAL, composition_guess={c: seeds[1]['x'][c] for c in NEUTRAL})]
        result = eq.solve_equilibrium(s.model, two)
        phases = [dict(zip(ids, result.phase_mole_fractions(k))) for k in range(len(result.amounts))]
        total = sum(result.amounts)
        kinds = ['liquid', 'liquid' if kind == 'liquid' else 'vapor']
        density = [s.model.state(prob.T, P=prob.P, x={c: v for c, v in x.items() if v > 0}, phase=k).molar_density for x, k in zip(phases, kinds)] if result.requested_tolerance_met and len(phases) == 2 else None
        return dict(seed=best['seed'], molar_density_mol_m3=density, split_delta_g_over_rt=best['quantities']['split_delta_g_over_rt'], split_error_over_rt=best['quantities'].get('split_error_estimate_over_rt'),
                    admitted_split=seeds, converged=result.requested_tolerance_met, message=result.message, max_residual=max(map(abs, result.residuals)),
                    amounts_mol=list(result.amounts), phase_fractions=[a/total for a in result.amounts], phases=phases, apparent=[apparent(x) for x in phases])
    record.update(two_liquid=converge('liquid'), liquid_vapor=converge('vapor'))
    return record


def splits():
    global STATES
    out = []
    for label in ('A1', 'B1'):
        STATES = declare(vector(label))
        out += pool(split_job, [(label, i) for i in WITNESSES])
    write('splits/splits.json', out)
    ids = list(s.params.component_ids)
    with (AN/OUT/'splits/compositions.csv').open('w', newline='') as stream:
        w = csv.writer(stream, lineterminator='\n')
        w.writerow(['vector', 'index', 'T_K', 'MDEA_mass_percent', 'alpha', 'P_Pa', 'solve', 'split_delta_g_over_rt', 'converged', 'phase', 'phase_fraction_mol', 'molar_density_mol_m3', *ids, 'apparent_loading', 'total_ion_fraction'])
        for r in out:
            for solve in ('two_liquid', 'liquid_vapor'):
                q = r.get(solve)
                if not q or not q['converged'] or len(q['phases']) < 2: continue
                for k, x in enumerate(q['phases']):
                    w.writerow([r['vector'], r['index'], r['T_K'], f"{r['MDEA_mass_percent']:.2f}", f"{r['alpha']:.6g}", r['P_Pa'], solve, f"{q['split_delta_g_over_rt']:.6g}", q['converged'],
                                ('L1', 'L2' if solve == 'two_liquid' else 'V')[k], f"{q['phase_fractions'][k]:.6g}", f"{q['molar_density_mol_m3'][k]:.6g}", *[f'{x[c]:.6g}' for c in ids],
                                f"{q['apparent'][k]['loading']:.6g}", f"{q['apparent'][k]['ions']:.6g}"])
    for r in out:
        print(r['vector'], r['index'], *[(solve, q['converged'], [f'{v:.4g}' for v in q['phase_fractions']], q['message'][:50]) for solve in ('two_liquid', 'liquid_vapor') if (q := r.get(solve))], flush=True)


# ---------- 3. one-change probes; 4. pressure and loading sensitivity ----------
def set_k(doc, a, b, value, family='k_ij'):
    pair = next(q for q in doc['pairs'] if {q['component_id_a'], q['component_id_b']} == {a, b})
    next(c for c in pair['coefficients'] if c['family'] == family)['value']['magnitude'] = value


def set_mdea_water_slope(doc, value):
    pair = next(q for q in doc['pairs'] if {q['component_id_a'], q['component_id_b']} == {M, W})
    next(t for t in pair['coefficients'][0]['temperature_law']['terms'] if t['power'] == 1)['coefficient']['value']['magnitude'] = value


def electrolyte_off(doc):
    """Debye-Hueckel and Born off; same-sign ion pairs get k_ij = 1, which keeps their dispersion excluded as in the endpoint."""
    d.electrolyte(doc, 'none')
    z = {c['component_id']: c['fixed'].get('charge_number', {}).get('value', {}).get('magnitude', 0) for c in doc['components']}
    have = {frozenset((q['component_id_a'], q['component_id_b'])) for q in doc['pairs']}
    for a, b in ((a, b) for n, a in enumerate(z) for b in list(z)[n+1:] if z[a]*z[b] > 0 and frozenset((a, b)) not in have):
        doc['pairs'].append(dict(component_id_a=a, component_id_b=b, provenance='Issue 222 diagnosis: same-sign ion dispersion excluded',
                                 coefficients=[dict(family='k_ij', identity=f'pair/{a}/{b}/k_ij', value=p.value(1., 'dimensionless'))]))


PROBES = {
    'baseline': lambda doc: None,
    **{f'k(MDEAH+-water)={v:g}': (lambda doc, v=v: set_k(doc, H, W, v)) for v in (-0.5, -0.25, 0., 0.25)},
    **{f'k(MDEAH+-HCO3-)={v:g}': (lambda doc, v=v: set_k(doc, H, HCO3, v)) for v in (-1., -0.5, 0., 0.5, 1.)},
    **{f'Born diameter={v:g} A': (lambda doc, v=v: d.set_component(doc, H, 'born_diameter', v)) for v in (3., 4., 5., 6., 7.)},
    'k(MDEA-water) c1=0': lambda doc: set_mdea_water_slope(doc, 0.),
    'Born off (diagnostic)': lambda doc: d.electrolyte(doc, 'fully-dissociated-debye-huckel'),
    'Debye-Hueckel and Born off (diagnostic)': electrolyte_off,
}


def probe_job(job):
    label, name, index = job
    prob = FITTED.get(index) or GRID[index]  # native problems are fork-inherited, not pickled
    doc = copy.deepcopy(BASE[label]); PROBES[name](doc)
    record = dict(vector=label, probe=name, index=index, T_K=prob.T, P_Pa=prob.P if isinstance(prob.P, float) else None,
                  alpha=prob.feed.values.get(C, 0.)/prob.feed.values[M], MDEA_mass_percent=100*.1191622/(.1191622+prob.feed.values[W]*.01801528))
    try:
        s.setup(doc)
        r = search(prob); r.pop('state')
        record.update({k: r[k] for k in ('converged', 'message', 'unresolved', 'liquid_split_delta_g_over_rt', 'vapor_descent')},
                      ion_fraction=sum(v for c, v in r['x'].items() if c not in NEUTRAL))
        liquid = [t for t in r['trials'] if t['resolved_descent'] and t['kind'] == 'liquid']
        if liquid:  # density of the new phase separates gas evolution from a dense liquid split
            new = d.phases(min(liquid, key=lambda t: t['quantities']['split_delta_g_over_rt']), list(s.params.component_ids))[-1]
            record.update(trial_packing_fraction=new['packing_fraction'], trial_x=new['x'])
        # Model bubble pressure of the same feed: a descent at fixed P is gas evolution when it exceeds P.
        bubble = eq.solve_equilibrium(s.model, j.problem(prob.T, prob.P, prob.feed.values[W], prob.feed.values[C], True))
        record.update(bubble_pressure_Pa=bubble.pressure if bubble.requested_tolerance_met else None, bubble_message=bubble.message)
    except Exception as e:
        record['error'] = f'{type(e).__name__}: {e}'
    return record


def merkley_states():
    """Fitted Merkley end states (index :1) plus Jakobsen row 8, then the pressure and loading grid of question 4."""
    states = declare(vector('A1'))
    fitted = {i: states[i][1] for i in WITNESSES}
    grid = []
    for i in WITNESSES[1:]:
        prob = fitted[i]; alpha = prob.feed.values[C]
        assert states[i][0]['group'] in ('Merkley', 'Jakobsen'), i
        for P in (156e3, 500e3, 1121e3, 2500e3, 5000e3):
            grid.append((f'{i} P={P/1e3:g}kPa', j.problem(prob.T, P, prob.feed.values[W], alpha)))
        for f in (.25, .5, .75, .9, 1.1):
            q = j.problem(prob.T, prob.P, prob.feed.values[W], f*alpha); grid.append((f'{i} alpha={f:g}*alpha_LP', q))
    return fitted, grid


def saturation_job(job):
    """Model saturation loading at the declared T and P, by the stage-2 scan and Brent inversion."""
    label, i = job; s.setup(BASE[label]); prob = FITTED[i]
    w = .1191622/(.1191622+prob.feed.values[W]*.01801528)
    r = s.saturation(dict(temperature_K=str(prob.T), pressure_MPa=str(prob.P/1e6), unloaded_MDEA_mass_fraction=str(w)))
    return dict(vector=label, index=i, T_K=prob.T, P_Pa=prob.P, alpha_declared=prob.feed.values[C], **{k: v for k, v in r.items() if k != 'scan'})


def probes():
    global BASE, FITTED
    BASE = {label: vector(label) for label in ('A1', 'B1')}
    global GRID
    FITTED, grid = merkley_states(); GRID = dict(grid)
    out = pool(probe_job, [(label, name, i) for label in BASE for name in PROBES for i in FITTED])
    write('probes/probes.json', out)
    sens = pool(probe_job, [(label, 'baseline', i) for label in BASE for i in GRID])
    write('probes/sensitivity.json', dict(grid=sens, saturation=pool(saturation_job, [(label, i) for label in BASE for i in WITNESSES])))
    for r in out: print(r['vector'], r['probe'], r['index'], r.get('liquid_split_delta_g_over_rt'), r.get('unresolved'), r.get('error', ''), flush=True)


# ---------- retained summary (no model calculation) ----------
def kind_of(r):
    eta = r.get('trial_packing_fraction')
    return 'refused' if 'error' in r else 'dense liquid' if eta is not None and eta >= .05 else 'gas density' if eta is not None or r.get('vapor_descent') else 'none'


def summarize():
    rows = load(f'{OUT}/unresolved/records.json')
    clusters = {}
    for cls in sorted({r['class_'] for r in rows} - {'resolved'}):
        sel = [r for r in rows if r['class_'] == cls and r['set'] in ('A1 full search', 'B1 full search')]
        if not sel: continue
        span = lambda k: [min(r[k] for r in sel if r[k] is not None), max(r[k] for r in sel if r[k] is not None)] if any(r[k] is not None for r in sel) else None
        clusters[cls] = dict(records=len(sel), groups=dict(collections.Counter(r['group'] for r in sel)), T_K=span('T_K'), alpha=span('alpha'),
                             P_Pa=span('P_Pa'), MDEA_mass_percent=span('MDEA_mass_percent'), pressure=dict(collections.Counter(r['pressure'] for r in sel)))
    recon = collections.defaultdict(set)
    for r in rows:
        if 'reconstruction' in r['class_'] and not r['index'].startswith('saturation'): recon[r['set']].add(r['index'])
    full = [r for r in rows if r['set'] == 'A1 full search' and not r['carbon_free_state'] and r['alpha']]
    hit = {r['index'] for r in full if 'reconstruction' in r['class_']}
    by_T = collections.defaultdict(lambda: [0, 0])
    for r in full: by_T[round(r['T_K'])][0] += 1; by_T[round(r['T_K'])][1] += r['index'] in hit
    sets754 = [v for n, v in recon.items() if n not in ('A1', 'B1')]
    probes = load(f'{OUT}/probes/probes.json'); grid = load(f'{OUT}/probes/sensitivity.json')
    checked = [r for r in probes + grid['grid'] if kind_of(r) in ('gas density', 'none') and r.get('bubble_pressure_Pa')]
    agree = sum((kind_of(r) == 'gas density') == (r['bubble_pressure_Pa'] > r['P_Pa']) for r in checked)
    with (AN/OUT/'probes/table.csv').open('w', newline='') as stream:
        w = csv.writer(stream, lineterminator='\n')
        w.writerow(['vector', 'probe', 'index', 'T_K', 'MDEA_mass_percent', 'alpha', 'P_Pa', 'liquid_split_delta_g_over_rt', 'new_phase', 'new_phase_packing_fraction',
                    'model_bubble_pressure_Pa', 'unresolved_trials', 'native_refusal'])
        for r in probes + [dict(r, probe='baseline ' + r['index'].split(' ', 1)[1], index=r['index'].split(' ')[0]) for r in grid['grid']]:
            w.writerow([r['vector'], r['probe'], r['index'], r['T_K'], f"{r['MDEA_mass_percent']:.2f}", f"{r['alpha']:.6g}", r['P_Pa'], r.get('liquid_split_delta_g_over_rt'),
                        kind_of(r), r.get('trial_packing_fraction'), r.get('bubble_pressure_Pa'), r.get('unresolved'), r.get('error', '')])
    splits = load(f'{OUT}/splits/splits.json')
    same = [max(abs(r['two_liquid']['phases'][1][c]-r['liquid_vapor']['phases'][1][c]) for c in NEUTRAL)
            for r in splits if r.get('two_liquid') and r.get('liquid_vapor') and len(r['two_liquid']['phases']) == 2]
    write('summary.json', dict(
        unresolved=load(f'{OUT}/unresolved/summary.json') | dict(clusters_A1_B1_full_search=clusters,
            reconstruction_states=dict(per_754_record_set={n: len(v) for n, v in recon.items() if n not in ('A1', 'B1')}, union=len(set.union(*sets754)),
                                       in_every_754_record_set=len(set.intersection(*sets754)),
                                       A1_full_search_fraction_by_T={str(T): f'{n_hit}/{n}' for T, (n, n_hit) in sorted(by_T.items())})),
        repair={label: dict(collections.Counter(q['message'] for q in rs)) for label, rs in load(f'{OUT}/unresolved/repair.json').items()},
        gas_descent_iff_model_bubble_pressure_exceeds_declared=dict(cells=len(checked), agree=agree),
        two_liquid_second_phase_equals_vapor_phase_max_abs_mole_fraction_difference=max(same),
        saturation_at_declared_pressure=[{k: r[k] for k in ('vector', 'index', 'T_K', 'P_Pa', 'alpha_declared', 'alpha_sat', 'status')} for r in grid['saturation']]))


if __name__ == '__main__':
    runtime = s.load('inputs/runtime.json')
    assert p.sha(Path(runtime['wheel'])) == runtime['wheel_sha256'] == p.shared.ENGINE_WHEEL_SHA256
    p.write(f'{OUT}/runtime.json', dict(runtime, base_commit='962d719', workers=WORKERS, BLAS_threads_per_process=1, cpu_count=os.cpu_count()))
    {'reproduce': reproduce, 'classify': classify, 'repair': repair, 'splits': splits, 'probes': probes, 'summarize': summarize}[sys.argv[1]]()
