"""Bounded #396 evidence probe on the pinned wheel. Run from the repository root."""
import argparse
import copy
from concurrent.futures import ProcessPoolExecutor
import hashlib
import math
import os
from pathlib import Path
import time

import permittivity_refit_396 as p
import phase_diagnosis_255 as phase

r, s, f = p.r, p.s, phase.f
eq = f.eq
STATES = r.B / 'results/engine-3e83e19c-phase-search/run-2/inputs/states.json'
ENDPOINT = p.OUT / 'S1/parameters-0.json'
INDICES = (54, 81, 108)


def model(mapping):
    return f.epcsaft.Mixture(f.epcsaft.Parameters.from_mapping(mapping), thermochemistry=f.thermal.record())


def solve(mapping, problem, previous=None):
    started = time.monotonic()
    m = model(mapping)
    try:
        result = eq.solve_equilibrium(m, problem, start=previous)
    except f.epcsaft.EosError as error:
        return None, dict(exception=type(error).__name__, message=str(error), seconds=time.monotonic()-started)
    return result, dict(payload(mapping, m, problem, result), seconds=time.monotonic()-started)


def payload(mapping, m, problem, result):
    row = f.phase_payload(m, problem, result)
    values = s.parameter_values(mapping)
    charges = [c['fixed']['charge_number']['value']['magnitude'] for c in mapping['components']]
    beta = [values[p.coefficient_key(i)] if z else 0. for i, z in zip(s.COMPONENT_IDS, charges, strict=True)]
    xs = [result.phase_mole_fractions(i) for i in range(result.phase_count)] if result.success else []
    row.update(D=[1. + math.fsum(b*x for b,x in zip(beta, xs, strict=True)) for xs in xs],
               charge_per_mol=[math.fsum(z*x for z,x in zip(charges, xs, strict=True)) for xs in xs])
    if result.success:
        row['relative_permittivity'] = [m.state(result.temperature, rho=rho, x=x).bulk_relative_permittivity
                                       for rho,x in zip(result.molar_densities, xs, strict=True)]
    return row


def parent(index):
    state = r.read(STATES)[index]
    values = s.parameter_mapping(ENDPOINT)
    alpha = {p.coefficient_key(ion): s.parameter_values(values)[p.coefficient_key(ion)] for ion in p.IONS}
    request = phase.e.request(values, 313.15, .11)
    args = (request, state['loading'], state['temperature_K'], state['pressure_Pa'])
    problem = f.flash_problem(*args)
    phase_results = {}
    for topology, problem in [('LV', problem), ('L', f.flash_problem(
            *args, phases=[eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)]))]:
        _, cold = solve(values, problem)
        print(index, topology, 'cold', cold.get('success'), cold.get('D'), cold['message'], flush=True)
        path = []
        position, step, previous = 0., .125, None
        for attempt in range(29):
            fraction = 0. if attempt == 0 else min(1., position+step)
            mapping = s.with_parameter_values(values, {key: val*fraction for key,val in alpha.items()})
            result, row = solve(mapping, problem, previous)
            path.append(dict(fraction=fraction, **row))
            print(index, topology, fraction, row.get('requested_tolerance_met'), row.get('D'),
                  row.get('convergence', {}).get('residual'), flush=True)
            if result is not None and result.success and result.requested_tolerance_met:
                if fraction == 1.:
                    break
                previous, position = result, fraction
                if step < .125:
                    step = min(.125, 2*step)
            elif previous is not None and step > 2**-15:
                step *= .5
            else:
                break
        phase_results[topology] = dict(cold=cold, continuation=path)
    liquid_problem = problem
    m = model(values)
    liquid = eq.solve_equilibrium(m, liquid_problem)
    try:
        liquid_stability = f.stability(m, liquid_problem, liquid)
    except f.epcsaft.ParameterError as error:
        liquid_stability = dict(message=str(error))
    bubble_problem = copy.copy(liquid_problem)
    bubble_problem.phases = [eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS,
        composition_guess=liquid.phase_mole_fractions(0), packing_guess=liquid.packing_fractions[0]),
        eq.Phase('V', kind='vapor', support=s.COMPONENT_IDS[:3], amount=eq.Pinned(0.))]
    bubble_problem.P = eq.Free(state['pressure_Pa'])
    bubble, bubble_row = solve(values, bubble_problem)
    flash = f.flash_problem(*args)
    alternative_starts, pressure_path, shifted = None, [], []
    if bubble is not None and bubble.success:
        compositions = [bubble.phase_mole_fractions(0), bubble.phase_mole_fractions(1)[:3]]
        seed = lambda fraction: eq.EquilibriumStart(
            amounts=[bubble.amounts[0]*fraction, bubble.amounts[0]*(1-fraction)],
            compositions=compositions, packing_fractions=bubble.packing_fractions)
        starts = [seed(fraction) for fraction in (.1, .3, .5, .7, .9, .99)]
        limits = eq.EquilibriumWorkLimits(attempts=len(starts), attempt_iterations=400, seconds=25.)
        batch = eq.solve_equilibrium_starts(m, flash, starts, limits)
        alternative_starts = dict(causes=list(batch.causes), seconds=batch.seconds,
            results=[payload(values, m, flash, found) if found is not None else None for found in batch.results])
        position, step, previous = 0., .025, None
        for attempt in range(42):
            fraction = min(1., position+step)
            P = state['pressure_Pa']**fraction * bubble.pressure**(1.-fraction)
            flash.P = P
            if previous is None:
                batch = eq.solve_equilibrium_starts(m, flash, [seed(.99)],
                    eq.EquilibriumWorkLimits(attempts=1, attempt_iterations=400, seconds=5.))
                result = batch.results[0]
                row = payload(values, m, flash, result) if result is not None else dict(message=batch.causes[0])
            else:
                result, row = solve(values, flash, previous)
            pressure_path.append(dict(row, fraction=fraction, pressure_Pa=P))
            print(index, 'pressure path', fraction, P, row.get('requested_tolerance_met'), row.get('D'), flush=True)
            if result is not None and result.success and result.requested_tolerance_met:
                previous, position = result, fraction
                step = min(.125, 2*step)
                if fraction == 1.:
                    break
            elif step > 2**-15:
                step *= .5
            else:
                break
    flash.P = state['pressure_Pa']
    charges = {c['component_id']: c['fixed']['charge_number']['value']['magnitude'] for c in values['components']}
    baseline = s.parameter_values(values)
    for charge_shift in (-4.27, 1., 4.27):
        changed = s.with_parameter_values(values, {p.coefficient_key(cid):
            baseline[p.coefficient_key(cid)] + charge_shift*z for cid,z in charges.items() if z})
        result, row = solve(changed, flash)
        shifted.append(dict(charge_shift=charge_shift, **row))
    return dict(state=state, phase_results=phase_results, bubble=bubble_row, liquid_stability=liquid_stability,
                alternative_starts=alternative_starts, pressure_path=pressure_path, shifted=shifted)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    r.verify()
    started = time.monotonic()
    with ProcessPoolExecutor(int(os.environ['AGENT_HEAVY_CORES'])) as pool:
        rows = list(pool.map(parent, INDICES))
    s.write_json(args.output, dict(engine_commit=p.COMMIT, wheel_sha256=p.SHA,
        input_sha256={str(path.relative_to(r.ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in (STATES, ENDPOINT)}, seconds=time.monotonic()-started, rows=rows))


if __name__ == '__main__':
    main()
