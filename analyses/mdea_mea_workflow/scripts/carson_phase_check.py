"""Carson (2000) single-liquid check using the MEA tangent-plane search."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import concurrent.futures
import hashlib
import json
import multiprocessing
from pathlib import Path
import runpy
import types

AN = Path(__file__).resolve().parents[1]
# This also repeats the two-pressure heat check against the pinned wheel.
v = runpy.run_path(str(AN/'scripts/carson_pressure_check.py'))
p, a, eq = v['p'], v['a'], v['eq']
import final_evidence as f
# Only the component identities change; the bundle's search and native
# feasibility, charge, uncertainty and descending-split checks remain intact.
neutral = tuple(p.published.NEUTRAL)
f.s = types.SimpleNamespace(
    COMPONENT_IDS=neutral + tuple(c for c in p.published.SPECIES if c not in neutral),
    _jsonable=p.shared._jsonable)


def evaluate(job):
    variant, row = job
    path = AN/f'inputs/variant-{variant}.json'
    d = json.loads(path.read_text())
    params = p.epcsaft.Parameters.from_mapping(d)
    model = p.epcsaft.Mixture(params, thermochemistry=a.caloric_record(params))
    feed = {p.W:row['water'], p.M:1., p.C:row['alpha']}
    problem = eq.Problem(T=298.15, P=101325., feed=eq.Amounts(feed),
        phases=[eq.Phase('L', kind='liquid', support=p.published.SPECIES)],
        reactions=v['reactions'], neutral_reference=p.published.NEUTRAL_REFERENCE,
        row_tolerance=1e-10)
    state = eq.solve_equilibrium(model, problem)
    report = f.stability(model, problem, state)
    return dict(variant=variant, start=1, source_row=row['source_row'],
        alpha=row['alpha'], temperature_K=298.15, pressure_Pa=101325., feed_mol=feed,
        component_ids=list(params.component_ids), parameters=str(path.relative_to(p.ROOT)),
        parameters_sha256=p.sha(path),
        liquid={k:p.shared._jsonable(getattr(state,k)) for k in
                ('success','message','requested_tolerance_met','residuals','amounts',
                 'molar_densities','mole_fractions','coordinates','reduced_hessian_minimum')},
        stability=report)


if __name__ == '__main__':
    # An adjacent row and a row below alpha=0.2 bound the exact-case failure.
    selected = [v['largest'], next(r for r in v['rows'] if r['source_row']=='9'),
                next(r for r in v['rows'] if r['source_row']=='1')]
    jobs = [(variant,row) for variant in 'AB' for row in selected]
    available = next(int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines()
                     if line.startswith('MemAvailable:'))
    workers = min(os.cpu_count(), max(1,available//268435456), len(jobs))
    records=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,
            mp_context=multiprocessing.get_context('fork')) as pool:
        for record in pool.map(evaluate, jobs):
            records.append(record)
            p.write('results/carson-phase-check.json',records)
            print(record['variant'], record['source_row'], 'completed',
                record['stability']['completed'], 'descending trials',
                sum(t['resolved_descent'] for t in record['stability']['trials']),flush=True)
    p.write('results/carson-phase-compute.json',dict(cpu_count=os.cpu_count(),
        available_memory_bytes=available, workers=workers, independent_jobs=len(jobs),
        allowance_bytes_per_process=268435456, BLAS_threads_per_process=1,
        search_owner='analyses/mea_parameter_bundle/scripts/final_evidence.py::stability',
        search_owner_sha256=p.sha(Path(f.__file__)),
        method='CSE Diagnose: exact-case repeat and adjacent printed row; no parameter, tolerance, bound or phase-search budget changed'))
