"""Bounded start sensitivity for failed cold flash rows, with unchanged declarations."""
import concurrent.futures
import math
import multiprocessing
import time
import permittivity_probe as screen

ROWS = screen.read(screen.OUT / 'flash-family.json')
FAILED = [r for r in ROWS if not r['accepted']]


def recover(row):
    basis, name, i = row['basis'], row['variant'], row['index']
    same = [r for r in ROWS if r['basis'] == basis and r['variant'] == name and r['accepted'] and r['temperature_K'] == row['temperature_K']]
    nearest = sorted(same, key=lambda r: abs(r['loading']-row['loading']) + abs(math.log(r['pressure_Pa']/row['pressure_Pa'])))[:2]
    starts = [screen.h.eq.EquilibriumStart(coordinates=r['coordinates']) for r in nearest]
    result = dict(basis=basis, variant=name, index=i, cold_message=row['message'], seed_indices=[r['index'] for r in nearest])
    model = screen.mixture(screen.VARIANTS[name] if basis == 'current' else screen.engine_variant(name))
    problem = screen.flash_problem(basis, row['loading'], row['temperature_K'], row['pressure_Pa'])
    start = time.perf_counter()
    try:
        batch = screen.h.eq.solve_equilibrium_starts(model, problem, starts,
            screen.h.eq.EquilibriumWorkLimits(attempts=2, attempt_iterations=400, iterations=800))
        result.update(accepted=batch.selected is not None, causes=list(batch.causes), selected=batch.selected,
            attempts=[None if r is None else dict(accepted=bool(r.success and r.requested_tolerance_met), message=r.message,
                residual=r.convergence.residual, objective_over_RT=r.objective, amounts=list(r.amounts),
                mole_fractions=list(r.mole_fractions), molar_densities=list(r.molar_densities), coordinates=list(r.coordinates))
                for r in batch.results])
    except Exception as error:
        result.update(accepted=False, message=f'{type(error).__name__}: {error}')
    result['seconds'] = time.perf_counter()-start
    return result


if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(16, mp_context=multiprocessing.get_context('fork')) as pool:
        rows = list(pool.map(recover, FAILED))
    screen.save('flash-family-recovery.json', rows)
    screen.table('flash-family-recovery.csv', [{k:v for k,v in r.items() if k!='attempts'} for r in rows])
    for basis in ('current','engine-case7'):
        for name in screen.VARIANTS:
            cold = [r for r in ROWS if r['basis']==basis and r['variant']==name]
            new = [r for r in rows if r['basis']==basis and r['variant']==name]
            print(basis,name,'cold',sum(r['accepted'] for r in cold),'recovered',sum(r['accepted'] for r in new),flush=True)
