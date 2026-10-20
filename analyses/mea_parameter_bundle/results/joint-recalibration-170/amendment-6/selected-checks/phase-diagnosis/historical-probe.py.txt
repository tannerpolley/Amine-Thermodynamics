"""Issue 172 fixed-parameter dielectric probe; installed Engine calculations only."""
import concurrent.futures
import copy
import csv
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
WHEEL_SHA = '3fd8140211aac1fb1e82807f066cdf507be733b36c6c27bf41377e7bb939aa86'
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
os.environ.update(SENSITIVITY_OUTPUT=str(ROOT / 'tmp/permittivity-screen-172-scratch'), FINAL_RERUN='1', FINAL_POOL='0')
sys.path[:0] = [str(BUNDLE / 'scripts'), str(BUNDLE / 'calibration-misfit'), str(ROOT / 'src')]
import shared_evaluation as s
s.ENGINE_WHEEL_SHA256 = WHEEL_SHA
s.ENGINE_COMMIT = '81d1e38a'
s.verify_wheel()
import probe as packet_probe  # Loads its wheel check before heat_160 binds the historical identity.
import heat_160 as h
s.ENGINE_WHEEL_SHA256 = WHEEL_SHA
s.ENGINE_COMMIT = '81d1e38a'
s.verify_wheel()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def table(name, rows):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(k for row in rows for k in row)), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def read(path):
    return json.loads(Path(path).read_text())


CURRENT = s.parameter_mapping()
VARIANTS = {'baseline': CURRENT, **{p.name.removesuffix('-parameters.json'): read(p)
            for p in sorted(OUT.glob('MEA-*-parameters.json'))}}
PARAMS, GROUPS, _ = h.d.rows_for(CURRENT, '11')
REQUEST = s.corrected_request(GROUPS[0][0]['request'], s.reaction_values(CURRENT))
CURRENT_REACTIONS = s._problem_from_request(REQUEST).reactions
POINTS = [tuple(map(float, row.split())) for row in (OUT / 'inputs/family-points.txt').read_text().splitlines()]
ENGINE_RECORD = read(OUT / 'inputs/engine-case7-parameters.json')
ENGINE_INPUT = read(OUT / 'inputs/engine-case7-reactions.json')
ENGINE_REACTIONS = [h.eq.Reaction(nu, correlation=h.eq.ReactionLogPolynomial(k, 0., 0., 0.,
    ENGINE_INPUT['T_ref'], ENGINE_INPUT['T_min'], ENGINE_INPUT['T_max'], h.eq.EOS_STANDARD_STATE_ID))
    for nu, k in zip(ENGINE_INPUT['stoichiometry'], ENGINE_INPUT['ln_k'], strict=True)]


def engine_variant(name):
    record = copy.deepcopy(ENGINE_RECORD)
    if name == 'baseline':
        return record
    source = VARIANTS[name]
    next(f for f in record['model_families'] if f['kind'] == 'permittivity')['choice'] = 'solvent-density-temperature'
    record['correlations'] = [r for r in record['correlations'] if r['family'] != 'relative_permittivity']
    record['sources'].extend(r for r in source['sources'] if r['source_id'] == 'permittivity-screen-172')
    for component in record['components']:
        component['coefficients'] = [r for r in component['coefficients'] if r['family'] != 'relative_permittivity']
        matching = next((c for c in source['components'] if c['component_id'] == component['component_id']), None)
        if matching:
            component['coefficients'].extend(copy.deepcopy(r) for r in matching['coefficients']
                if r['family'] in ('dielectric_volume', 'dielectric_temperature'))
    return record


def mixture(record):
    return h.epcsaft.Mixture(h.epcsaft.Parameters.from_mapping(record, components=s.COMPONENT_IDS))


def flash_problem(basis, loading, T, P, phases=None):
    return h.eq.Problem(T=T, P=P, feed=h.eq.Amounts({'monoethanolamine': 9.7292821,
        'water': 76.9751925, 'carbon-dioxide': loading * 9.7292821}),
        phases=phases or [h.eq.Phase('L', kind='liquid'), h.eq.Phase('V', kind='vapor', support=s.COMPONENT_IDS[:3])],
        reactions=CURRENT_REACTIONS if basis == 'current' else ENGINE_REACTIONS,
        neutral_reference=s._neutral_reference(REQUEST) if basis == 'current' else None, row_tolerance=1e-10)


def family_job(spec):
    basis, name, i = spec
    loading, T, P = POINTS[i]
    row = dict(basis=basis, variant=name, index=i, loading=loading, temperature_K=T, pressure_Pa=P)
    start = time.perf_counter()
    try:
        model = mixture(VARIANTS[name] if basis == 'current' else engine_variant(name))
        r = h.eq.solve_equilibrium(model, flash_problem(basis, loading, T, P))
        row.update(accepted=bool(r.success and r.requested_tolerance_met), message=r.message, solver_status=r.solver_status,
            iterations=r.iterations, evaluations=r.evaluations, residual=r.convergence.residual,
            amounts=list(r.amounts), mole_fractions=list(r.mole_fractions), molar_densities=list(r.molar_densities),
            objective_over_RT=r.objective, coordinates=list(r.coordinates))
    except Exception as error:
        row.update(accepted=False, message=f'{type(error).__name__}: {error}')
    row['seconds'] = time.perf_counter() - start
    return row


TARGET_TASKS = []


def target_job(i):
    name, mapping, target, item, weight, source, T = TARGET_TASKS[i]
    row = dict(variant=name, target=target, source=source, temperature_K=T, observed=item.observed)
    start = time.perf_counter()
    try:
        model = h.epcsaft.Mixture(h.epcsaft.Parameters.from_mapping(mapping), thermochemistry=h.thermal.record())
        value = h.reg.predict(model, item)
        row.update(status=value.status.name, message=value.message)
        if value.status.name == 'Available':
            y = value.value
            residual = math.sqrt(weight) * (math.log(y / item.observed) if item.form == h.reg.ResidualForm.LogRatio
                else (y - item.observed) / item.scale)
            row.update(predicted=y, weighted_residual=residual, cost=.5 * residual**2)
            assert math.isfinite(y) and math.isfinite(residual)
    except Exception as error:
        row.update(status='exception', message=f'{type(error).__name__}: {error}')
    row['seconds'] = time.perf_counter() - start
    return row


def targets():
    for name, mapping in VARIANTS.items():
        params, groups, rows = h.d.rows_for(mapping, '11')
        metadata = {t['identity']: (t['source_identity'], o['request']['temperature']['value'])
                    for o, _ in groups for t in o['targets']}
        TARGET_TASKS.extend((name, mapping, target, item, weight, *metadata[target]) for target, item, weight in rows)
        for source, sources in [('Vinjarapu2024', h.VINJARAPU), ('Arcis2011', h.ARCIS)]:
            TARGET_TASKS.extend((name, mapping, row['record_id'], item, 1., source, row['temperature_K'])
                for row, item in zip(sources, h.heat_items(mapping, params, sources), strict=True))
    with concurrent.futures.ProcessPoolExecutor(16, mp_context=multiprocessing.get_context('fork')) as pool:
        rows = list(pool.map(target_job, range(len(TARGET_TASKS))))
    save('targets.json', rows)
    table('targets.csv', rows)
    print('TARGETS', len(rows), 'available', sum(r['status'] == 'Available' for r in rows), flush=True)


def family():
    tasks = [(basis, name, i) for basis in ('current', 'engine-case7') for name in VARIANTS for i in range(73)]
    rows = []
    with concurrent.futures.ProcessPoolExecutor(16, mp_context=multiprocessing.get_context('fork')) as pool:
        for row in pool.map(family_job, tasks):
            rows.append(row)
            if row['index'] == 72:
                print('FAMILY', row['basis'], row['variant'], sum(r['accepted'] for r in rows[-73:]), '/73', flush=True)
    save('flash-family.json', rows)
    table('flash-family.csv', [{k: v for k, v in row.items() if k not in ('coordinates', 'amounts', 'mole_fractions', 'molar_densities')} for row in rows])


def shell_off(record):
    result = copy.deepcopy(record)
    next(f for f in result['model_families'] if f['kind'] == 'electrolyte')['c_dielectric'] = 0.
    return mixture(result)


def contribution(model, off, T, amount, x, rho):
    state = model.state(T, rho=rho, x=x)
    bulk = off.state(T, rho=rho, x=x).born
    return dict(amount_mol=amount, molar_density_mol_m3=rho, EOS_pressure_Pa=state.pressure,
        bulk_epsilon=state.bulk_relative_permittivity, hard_chain_over_RT=amount*state.hard_chain,
        dispersion_over_RT=amount*state.dispersion, association_over_RT=amount*state.association,
        DH_over_RT=amount*state.debye_huckel, Born_bulk_over_RT=amount*bulk,
        Born_shell_over_RT=amount*(state.born-bulk), residual_A_over_RT=amount*state.residual_helmholtz)


def falsifier():
    T, P, loading = 318.15, 3699.0803800848512, .25557798094241313
    witnesses = {kind: read(OUT / f'inputs/falsifier-{kind}.json')['row'] for kind in ('gas', 'physical')}
    xl = ('CO2', 'MEA', 'water', 'MEAH', 'carbamate', 'HCO3', 'CO3', 'H3O', 'OH')
    rows, parts, low_density = [], [], []
    for basis in ('current', 'engine-case7'):
        for name in VARIANTS:
            record = VARIANTS[name] if basis == 'current' else engine_variant(name)
            model, off = mixture(record), shell_off(record)
            problem = flash_problem(basis, loading, T, P)
            compiled = h.eq.compile_problem(model, problem)
            result = h.eq.solve_equilibrium(model, problem)
            save(f'falsifier-{basis}-{name}-solve.json', dict(success=result.success, message=result.message,
                residual=result.convergence.residual, objective_over_RT=result.objective, amounts=list(result.amounts),
                mole_fractions=list(result.mole_fractions), densities=list(result.molar_densities), coordinates=list(result.coordinates)))
            if result.success:
                for phase, offset, width, index in [('L', 0, 9, 0), ('V', 9, 3, 1)]:
                    composition = list(result.mole_fractions[offset:offset+width]) + [0.]*(9-width)
                    parts.append(dict(basis=basis, variant=name, state='solved-physical', phase=phase,
                        **contribution(model, off, T, result.amounts[index], composition, result.molar_densities[index])))
                assert abs(compiled.evaluate(result.coordinates).objective-result.objective) < 1e-8
            for kind, witness in witnesses.items():
                point = compiled.generic_point()
                point[:16] = [*[math.log(float(witness['xL_'+v])) for v in xl], float(witness['N_L']), float(witness['lneta_L']),
                    *[math.log(float(witness['yV_'+v])) for v in xl[:3]], max(0., float(witness['N_V'])), float(witness['lneta_V'])]
                value = compiled.evaluate(point)
                row = dict(basis=basis, variant=name, state='retained-'+kind, G_over_RT=value.objective,
                    comparison_G_over_RT=result.objective if result.success else None,
                    delta_G_over_RT=value.objective-result.objective if result.success else None,
                    compared_solve_accepted=result.success, max_compiled_row= max(abs(v) for v in value.values))
                for phase, offset, width in [('L', 0, 9), ('V', 11, 3)]:
                    x = [math.exp(v) for v in point[offset:offset+width]] + [0.]*(9-width)
                    decomposition = list(csv.DictReader((OUT / 'inputs/engine-decomposition.csv').open()))
                    label = 'classA_end' if kind == 'gas' else 'physical'
                    density = float(next(r for r in decomposition if r['label'] == label and r['phase'] == phase)['rho_mol_m3'])
                    part = dict(basis=basis, variant=name, state='source-density-'+kind, phase=phase,
                        **contribution(model, off, T, point[offset+width], x, density))
                    parts.append(part)
                rows.append(row)
            witness = witnesses['gas']
            x = [float(witness['xL_'+v]) for v in xl]
            x = [v/sum(x) for v in x]
            for density in (1e-6, 1e-3, .01, .1, 1.4, 10., 100.):
                low_density.append(dict(basis=basis, variant=name, **contribution(model, off, T,
                    float(witness['N_L']), x, density)))
            for branch in ('vapor', 'liquid'):
                row = dict(basis=basis, variant=name, state='gas-composition-'+branch+'-root')
                try:
                    state = model.state(T, P=P, x=x, phase=branch)
                    row.update(stable_root_count=state.stable_root_count,
                        **contribution(model, off, T, float(witness['N_L']), x, state.molar_density))
                except Exception as error:
                    row.update(message=f'{type(error).__name__}: {error}')
                rows.append(row)
            print('FALSIFIER',basis,name,'solve',result.success, 'G',result.objective,flush=True)
    save('falsifier.json', rows)
    table('falsifier.csv', rows)
    table('falsifier-contributions.csv', parts)
    table('falsifier-low-density.csv', low_density)


if __name__ == '__main__':
    {'targets': targets, 'family': family, 'falsifier': falsifier}[sys.argv[1]]()
