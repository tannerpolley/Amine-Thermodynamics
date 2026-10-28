"""Diagnose the start-1 Carson liquid-liquid split: one-change probes, no fitting.

Each probe changes one declared quantity from start 1 (or swaps in another
declared start) and repeats the stage-2 tangent-plane search unchanged.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import concurrent.futures
import copy
import csv
import importlib.util
import json
import math
import multiprocessing
from pathlib import Path
import types

AN = Path(__file__).resolve().parents[1]
OUT = 'results/diagnosis-carson-split'
spec = importlib.util.spec_from_file_location('admission', AN/'scripts/admission_probe.py')
a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
p, eq = a.p, a.p.eq
import final_evidence as f

W, M, H, C = p.W, p.M, p.H, p.C
HCO3, H3O = 'bicarbonate-anion', 'hydronium-cation'
SPECIES = tuple(p.published.NEUTRAL) + tuple(c for c in p.published.SPECIES if c not in p.published.NEUTRAL)
T, P = 298.15, 101325.

# Reactions exactly as carson_pressure_check.py (retained shared R1-R3 plus MDEA dissociation).
recs = json.loads((AN/'inputs/probe-reaction-reference.json').read_text())['shared']
REACTIONS = [eq.Reaction({cid: v for cid, v in zip(p.shared.COMPONENT_IDS, r['stoichiometry']) if v}, name=r['reaction_id'],
                         correlation=p.shared._reaction_correlation(r, r['reaction_id']), reference=p.shared._reaction_reference(r, r['reaction_id'])) for r in recs]
REACTIONS.append(eq.Reaction({H: -1, W: -1, M: 1, H3O: 1}, name='MDEA-dissociation',
    correlation=eq.ReactionLogPolynomial(-83.491+4.0165+10.976*math.log(313.15), -819.7, 10.976, 0., 313.15, 278., 393.15, p.shared.COMMON_SOURCE_STANDARD_STATE_ID),
    reference=eq.ReactionReference(eq.ReferenceSourceBasis.CommonMolalityInfiniteDilution, 1e5)))
ROWS = {}
for r in csv.DictReader((p.DATA/'Carson2000_stage1.csv').open()):
    w = float(r['MDEA_mass_fraction']); nw = .1191622*(1-w)/w/.01801528; x = float(r['x_CO2'])
    ROWS[r['source_row']] = dict(source_row=r['source_row'], MDEA_mass_fraction=w, water=nw, alpha=x/(1-x)*(1+nw))

MEA = json.loads((p.BUNDLE/'results/selected-current-best-parameters.json').read_text())
mea_pair = lambda a_, b_: next(q for q in MEA['pairs'] if {q['component_id_a'], q['component_id_b']} == {a_, b_})
mea_value = lambda pair, family: next(c for c in pair['coefficients'] if c['family'] == family)['value']['magnitude']
K_MEA_W = mea_value(mea_pair('monoethanolamine', W), 'k_ij'), mea_value(mea_pair('monoethanolamine', W), 'k_ij_reciprocal_temperature_slope')
K_MEAH_W = mea_value(mea_pair('protonated-monoethanolamine', W), 'k_ij'), mea_value(mea_pair('protonated-monoethanolamine', W), 'k_ij_reciprocal_temperature_slope')
UK_MEAH = next(c for c in next(c for c in MEA['components'] if c['component_id'] == 'protonated-monoethanolamine')['coefficients']
               if c['family'] == 'dispersion_energy_over_k')['value']['magnitude']


def set_pair(d, i, j, k, slope=None):
    pair = next(q for q in d['pairs'] if {q['component_id_a'], q['component_id_b']} == {i, j})
    a_, b_ = pair['component_id_a'], pair['component_id_b']
    pair['coefficients'] = [dict(family='k_ij', identity=f'pair/{a_}/{b_}/k_ij', value=p.value(k, 'dimensionless'))]
    if slope is not None:
        pair['coefficients'].append(dict(family='k_ij_reciprocal_temperature_slope', identity=f'pair/{a_}/{b_}/k_ij/reciprocal_temperature_slope',
                                         value=p.value(slope, 'kelvin'), reference_temperature=p.value(313.15, 'kelvin')))


def set_component(d, cid, family, v):
    next(c for c in next(c for c in d['components'] if c['component_id'] == cid)['coefficients'] if c['family'] == family)['value']['magnitude'] = v


def electrolyte(d, choice):
    """Diagnostic electrolyte switch; the Born-only inputs (solvation factor, Born diameter, ionic-region permittivity) go with Born."""
    family = next(x for x in d['model_families'] if x['kind'] == 'electrolyte')
    family['choice'] = choice
    for key in ('c_shell', 'c_dielectric') + (('ionic_dispersion',) if choice == 'none' else ()): family.pop(key, None)
    d['model_coefficients'] = []
    for c in d['components']:
        c['coefficients'] = [x for x in c['coefficients'] if x['family'] not in ('solvation_factor', 'born_diameter')]


def sigma_A(d, s):
    # Variant A convention (prepare.py): packing 0.88 sigma, Debye-Hueckel diameter sigma.
    set_component(d, H, 'segment_diameter', s); set_component(d, H, 'packing_diameter', .88*s); set_component(d, H, 'debye_huckel_diameter', s)


def start2(d): set_pair(d, W, H, -0.2298); set_pair(d, W, M, *K_MEA_W)
def start3(d): set_component(d, H, 'dispersion_energy_over_k', UK_MEAH); set_pair(d, W, H, *K_MEAH_W)


# name: (variants, edit or start-4 file, alpha override)
PROBES = {
    'start-1': ('AB', None, None),
    'unloaded-alpha-0': ('AB', None, 0.),  # no carbon in the feed: see binary() for the unloaded check
    'near-unloaded-alpha-0.001': ('AB', None, 1e-3),
    'start-2': ('AB', start2, None),
    'start-3': ('AB', start3, None),
    'start-4': ('A', 'variant-A-start-4.json', None),
    'k(MDEA-water)=start-2': ('AB', lambda d: set_pair(d, W, M, *K_MEA_W), None),
    'k(MDEAH+-water)=-0.2298': ('AB', lambda d: set_pair(d, W, H, -0.2298), None),
    'k(MDEAH+-water)=-0.5': ('AB', lambda d: set_pair(d, W, H, -0.5), None),
    'sigma(MDEAH+)=3.563': ('A', lambda d: sigma_A(d, 3.563), None),
    'Born(MDEAH+)=3.563': ('AB', lambda d: set_component(d, H, 'born_diameter', 3.563), None),
    'Born(MDEAH+)=7': ('AB', lambda d: set_component(d, H, 'born_diameter', 7.), None),
    'u/k(MDEAH+)=177.9': ('AB', lambda d: set_component(d, H, 'dispersion_energy_over_k', UK_MEAH), None),
    **{f'k(MDEA-water)={k:g}': ('AB', lambda d, k=k: set_pair(d, W, M, k), None) for k in (-0.10, -0.12, -0.13, -0.15, -0.184, -0.25)},
    # Two changes, labelled as such: binary made miscible, then the declared MDEAH+-water values.
    'two-change k(MDEA-water)=-0.184 & k(MDEAH+-water)=-0.2298': ('AB', lambda d: (set_pair(d, W, M, -0.184), set_pair(d, W, H, -0.2298)), None),
    'two-change k(MDEA-water)=-0.184 & k(MDEAH+-water)=-0.5': ('AB', lambda d: (set_pair(d, W, M, -0.184), set_pair(d, W, H, -0.5)), None),
    **{f'two-change k(MDEA-water)={k:g} & k(MDEAH+-water)={h:g}': ('AB', lambda d, k=k, h=h: (set_pair(d, W, M, k), set_pair(d, W, H, h)), None)
       for k in (-0.10, -0.13, -0.15) for h in (-0.2298, -0.5)},
    'Born-off(diagnostic)': ('AB', lambda d: electrolyte(d, 'fully-dissociated-debye-huckel'), None),
    'electrolyte-off(diagnostic)': ('AB', lambda d: electrolyte(d, 'none'), None),
}


def document(variant, edit):
    if isinstance(edit, str):
        return json.loads((AN/'inputs'/edit).read_text())
    d = json.loads((AN/f'inputs/variant-{variant}.json').read_text())
    if edit: edit(d)
    return d


def phases(trial, ids):
    """Decode split_coordinates: per phase, supported ln x, amount mol, ln packing; existing full-support phases, then the trial support."""
    z, n, support = trial['split_coordinates'], len(ids), trial['phase']['support']
    sizes = [n+2]*((len(z)-len(support)-2)//(n+2)) + [len(support)+2]
    out, at = [], 0
    for b, size in enumerate(sizes):
        block, at = z[at:at+size], at+size
        names = ids if b < len(sizes)-1 else [ids[i] for i in support]
        x = dict.fromkeys(ids, 0.); x.update(zip(names, map(math.exp, block[:-2])))
        out.append(dict(kind='liquid' if b < len(sizes)-1 else trial['phase']['kind'], amount_mol=block[-2], packing_fraction=math.exp(block[-1]), x=x))
    assert at == len(z)
    return out


def summary(report, ids):
    trials = report['trials']
    split = [t for t in trials if t['resolved_descent']]
    best = min(split, key=lambda t: t['quantities']['split_delta_g_over_rt'], default=None)
    return dict(completed=report['completed'], message=report['message'],
        minimum_tpd_over_rt=min(t['quantities'].get('tpd_over_rt', math.inf) for t in trials),
        descending_trials=len(split), split=best is not None,
        split_delta_g_over_rt=None if best is None else best['quantities']['split_delta_g_over_rt'],
        split_error_over_rt=None if best is None else best['quantities']['split_error_estimate_over_rt'],
        split_phases=None if best is None else phases(best, ids),
        trial_minimum=[dict(kind=t['phase']['kind'], tpd_over_rt=t['quantities'].get('tpd_over_rt'), composition=dict(zip(ids, t['composition'])) if t['composition'] else None) for t in trials])


def converge_split(model, problem, split_phases, single_g_over_rt):
    """Two-liquid equilibrium seeded by the admitted finite split, then the same search on it.

    Total G/RT is the sum of phase amount times per-mole g_over_rt from the search's present phases.
    """
    two = copy.copy(problem)
    two.phases = [eq.Phase(f'L{i+1}', kind='liquid', support=p.published.SPECIES, composition_guess={c: q['x'][c] for c in p.published.SPECIES},
                           packing_guess=q['packing_fraction']) for i, q in enumerate(split_phases)]
    r = eq.solve_equilibrium(model, two)
    ids = list(model.component_ids)
    out = dict(success=r.success, message=r.message, requested_tolerance_met=r.requested_tolerance_met, amounts_mol=list(r.amounts),
               max_residual=max(map(abs, r.residuals)), phases=[dict(zip(ids, r.phase_mole_fractions(i))) for i in range(len(r.amounts))])
    if r.success:
        report = f.stability(model, two, r)
        out['stability'] = summary(report, ids)
        out['phase_g_over_rt_per_mol'] = [q['g_over_rt'] for q in report['present_phases']]
        out['delta_g_over_rt_vs_single_liquid'] = sum(n*q['g_over_rt'] for n, q in zip(r.amounts, report['present_phases'])) - single_g_over_rt
    return out


def reactive(job):
    name, variant, row_id = job
    variants, edit, alpha = PROBES[name]
    f.s = types.SimpleNamespace(COMPONENT_IDS=SPECIES, _jsonable=p.shared._jsonable)
    row = ROWS[row_id]; alpha = row['alpha'] if alpha is None else alpha
    record = dict(probe=name, variant=variant, source_row=row_id, alpha=alpha, temperature_K=T, pressure_Pa=P)
    try:
        params = p.epcsaft.Parameters.from_mapping(document(variant, edit))
        model = p.epcsaft.Mixture(params, thermochemistry=a.caloric_record(params))
        feed = {W: row['water'], M: 1., C: alpha}
        problem = eq.Problem(T=T, P=P, feed=eq.Amounts(feed), phases=[eq.Phase('L', kind='liquid', support=p.published.SPECIES)],
            reactions=REACTIONS, neutral_reference=p.published.NEUTRAL_REFERENCE, row_tolerance=1e-10)
        state = eq.solve_equilibrium(model, problem)
        ids = list(params.component_ids)
        record['liquid'] = dict(success=state.success, requested_tolerance_met=state.requested_tolerance_met,
            max_residual=max(map(abs, state.residuals)), x=dict(zip(ids, state.mole_fractions)), amount_mol=list(state.amounts))
        report = f.stability(model, problem, state)
        record.update(summary(report, ids))
        if name == 'start-1' and record['split']:
            single = state.amounts[0]*report['present_phases'][0]['g_over_rt']
            record['two_liquid'] = converge_split(model, problem, record['split_phases'], single)
    except Exception as e:  # a refusal is retained, not reinterpreted
        record['error'] = f'{type(e).__name__}: {e}'
    return record


def binary(job):
    """Non-reactive MDEA-water at the row ratio; the same search with water/MDEA trial supports."""
    label, k = job
    f.s = types.SimpleNamespace(COMPONENT_IDS=(W, M), _jsonable=p.shared._jsonable)
    d = document('A', None)
    if k is not None: set_pair(d, W, M, *k)
    params = p.epcsaft.Parameters.from_mapping(d, components=[M, W])
    model = p.epcsaft.Mixture(params, thermochemistry=a.caloric_record(params))
    problem = eq.Problem(T=T, P=P, feed=eq.Amounts({W: ROWS['10']['water'], M: 1.}), phases=[eq.Phase('L', kind='liquid', support=[W, M])], reactions=[], row_tolerance=1e-10)
    state = eq.solve_equilibrium(model, problem)
    ids = list(params.component_ids)
    return dict(probe=f'binary MDEA-water, {label}', k_MDEA_water=k, liquid=dict(success=state.success, x=dict(zip(ids, state.mole_fractions))),
                **summary(f.stability(model, problem, state), ids))


def mixing_scan(k, temperature):
    """Binary Gibbs energy of mixing on a grid; miscible iff every point lies on the lower convex hull."""
    d = document('A', None); set_pair(d, W, M, k, 0.)
    params = p.epcsaft.Parameters.from_mapping(d, components=[M, W]); model = p.epcsaft.Mixture(params)
    ids = list(params.component_ids); iM, iW = ids.index(M), ids.index(W)
    pure = {c: model.state(temperature, P=P, x={c: 1.}, phase='liquid').log_fugacity_coefficient[ids.index(c)] for c in (M, W)}
    grid = sorted({10**(-6+5*i/40) for i in range(41)} | {i/200 for i in range(1, 200)} | {1-10**(-6+5*i/40) for i in range(41)})
    g, lngM = [], None
    for x in grid:
        lf = model.state(temperature, P=P, x={M: x, W: 1-x}, phase='liquid').log_fugacity_coefficient
        g.append(x*(math.log(x)+lf[iM]-pure[M]) + (1-x)*(math.log(1-x)+lf[iW]-pure[W]))
        if lngM is None: lngM = lf[iM]-pure[M]
    # lower convex hull (monotone chain) with the pure-component endpoints g=0
    pts = [(0., 0.)] + list(zip(grid, g)) + [(1., 0.)]
    hull = []
    for q in pts:
        while len(hull) >= 2 and (hull[-1][0]-hull[-2][0])*(q[1]-hull[-2][1]) - (hull[-1][1]-hull[-2][1])*(q[0]-hull[-2][0]) <= 0:
            hull.pop()
        hull.append(q)
    off = [x for x, gx in zip(grid, g) if (x, gx) not in hull]
    return dict(k_MDEA_water=k, temperature_K=temperature, ln_gamma_MDEA_dilute=lngM, dilute_x_MDEA=grid[0], miscible=not off,
                gap_x_MDEA=[min(off), max(off)] if off else None)


def shared_species(job):
    """Frozen MEA record only: water + cation + bicarbonate at the row ionic strength, non-reactive."""
    row_id, molality, cation = job
    params = p.epcsaft.Parameters.from_mapping(MEA, components=[W, cation, HCO3])
    model = p.epcsaft.Mixture(params)
    nw = 1/.01801528
    problem = eq.Problem(T=T, P=P, feed=eq.Amounts({W: nw, cation: molality, HCO3: molality}),
                         phases=[eq.Phase('L', kind='liquid', support=[W, cation, HCO3])], reactions=[], row_tolerance=1e-10)
    state = eq.solve_equilibrium(model, problem)
    ids = list(params.component_ids)
    options = eq.StabilityOptions()
    trials = copy.copy(problem); trials.phases = [eq.Phase('trial-L', kind='liquid', support=[W, cation, HCO3]), eq.Phase('trial-V', kind='vapor', support=[W])]
    options.trials = trials._native(model).phases
    report = eq.stability_test(eq.compile_problem(model, problem), state, options)
    rows = [dict(kind=t.phase.kind.name.lower(), evidence=t.evidence, resolved_descent=t.resolved_descent, tpd_over_rt=dict(t.quantities).get('tpd_over_rt'),
                 split_delta_g_over_rt=dict(t.quantities).get('split_delta_g_over_rt'), composition=dict(zip(ids, t.composition)) if t.composition else None) for t in report.trials]
    return dict(probe='shared species only (frozen MEA record)', cation=cation, source_row=row_id, molality_mol_per_kg=molality, liquid=dict(success=state.success, x=dict(zip(ids, state.mole_fractions))),
                completed=report.completed, message=report.message, split=any(r['resolved_descent'] for r in rows), trials=rows)


if __name__ == '__main__':
    jobs = [(name, v, row) for name, (variants, _, _) in PROBES.items() for v in variants for row in ('10', '1')]
    available = next(int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
    workers = min(os.cpu_count(), max(1, available//(2*268435456)), len(jobs))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('fork')) as pool:
        bins = pool.map(binary, [('k=0 (start 1)', None), ('k=start-2 MEA-water value', K_MEA_W), ('k=start-4 Bulow projection', (-0.131933125, 104.9886164))])
        scans = pool.map(mixing_scan, *zip(*[(-i/100, t) for t in (298.15, 313.15) for i in range(0, 31)]))
        records = []
        for record in pool.map(reactive, jobs):
            records.append(record)
            print(record['probe'], record['variant'], record['source_row'], 'split', record.get('split'), record.get('split_delta_g_over_rt'), record.get('error', ''), flush=True)
        p.write(f'{OUT}/reactive-probes.json', records)
        with (AN/OUT/'summary.csv').open('w', newline='') as out:
            table = csv.writer(out, lineterminator='\n')
            table.writerow(['probe', 'variant', 'source_row', 'alpha', 'liquid_converged', 'search_completed', 'split', 'split_delta_g_over_rt', 'minimum_tpd_over_rt', 'search_message', 'refusal'])
            for r in records:
                table.writerow([r['probe'], r['variant'], r['source_row'], f"{r['alpha']:.6f}", r.get('liquid', {}).get('requested_tolerance_met'), r.get('completed'),
                                r.get('split'), '' if r.get('split_delta_g_over_rt') is None else f"{r['split_delta_g_over_rt']:.4f}",
                                '' if r.get('minimum_tpd_over_rt') is None else f"{r['minimum_tpd_over_rt']:.4f}", r.get('message', ''), r.get('error', '')])
        p.write(f'{OUT}/binary-mdea-water.json', dict(stability=list(bins), mixing_scan=list(scans)))
        # Ionic strength of the start-1 single liquid at each row, per kg water (z^2-weighted).
        z = {HCO3: 1, 'carbonate-anion': 2, H3O: 1, 'hydroxide-anion': 1, H: 1}
        strengths = {}
        for r in records:
            if r['probe'] == 'start-1' and r['variant'] == 'A':
                x = r['liquid']['x']
                strengths[r['source_row']] = .5*sum(z[c]**2*x[c] for c in z)/(x[W]*.01801528)
        strengths.update({f'scan {m:g}': m for m in (.001, .01, .03, .1, .3, 1.)})
        p.write(f'{OUT}/shared-species.json', list(pool.map(shared_species, [(k, m, c) for c in (H3O, 'protonated-monoethanolamine') for k, m in strengths.items()])))
    p.write(f'{OUT}/compute.json', dict(cpu_count=os.cpu_count(), available_memory_bytes=available, workers=workers, reactive_jobs=len(jobs),
        BLAS_threads_per_process=1, search_owner='analyses/mea_parameter_bundle/scripts/final_evidence.py::stability',
        search_owner_sha256=p.sha(Path(f.__file__)), engine_wheel_sha256=p.shared.ENGINE_WHEEL_SHA256,
        variant_sha256={v: p.sha(AN/f'inputs/variant-{v}.json') for v in 'AB'}, start4_sha256=p.sha(AN/'inputs/variant-A-start-4.json'),
        MEA_record_sha256=p.sha(p.BUNDLE/'results/selected-current-best-parameters.json')))
