"""Refit C through epcsaft.regression.fit: Ceres Levenberg-Marquardt with exact implicit derivatives, multistart.

Usage: refit.py [START ...]   (default: every start in STARTS; results merge into refit-C-multistart.json)
Refit C: four ion k_ij within +-0.3 and the MEAH+-water k_ij 1/T slope within +-300 K (T_ref 313.15 K), scales
0.01 and 10 K, with R4 held at its source correlation (probe.SOURCE_R4, both coefficients; R1-R3 and R5 are the
record's). Rows (compare.residuals scores the same rows from probe records): every packet state except 80 degC and
compare.EXCLUDED, 180 rows. pCO2: ln(pred/obs), weight 1/0.3^2. Species: (pred - obs)/(0.1 obs + 0.001), weight 1,
with the compare.pooled_species pool. Each state is declared from the base record's solve (MEA liquid anchor), as
Engine analyses/2026-mea-reactive-fit-timing/scripts/run.py declares it. Base record: probe.RECORD.
Writes refit-C-multistart.json (per start), refit-C-iterations.csv (cost and wall time per iteration) and
refit-C-jacobian.csv (per start: weighted residual and weighted physical Jacobian at the final point).
main() takes another design (coordinates, bounds, starts, output stem, and pco2_max_c: MEA #121 decision 23 drops
pCO2 rows above 80 degC, 160 rows) for the model D refits (../model-d/fit.py); the base record is probe.RECORD,
which fixes the Born form.
Diagnostic only: never writes the selected parameter record.
"""
import csv
import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

import probe
from compare import EXCLUDED, SIGMA_LN_P, in_objective, pooled_species

s, epcsaft = probe.shared, probe.epcsaft
from epcsaft import regression  # noqa: E402

HERE = Path(__file__).parent
INCUMBENT_R4 = json.loads((HERE / 'refit-C-incumbent-R4-multistart.json').read_text())
IDS = INCUMBENT_R4['provenance']['parameters']
LOWER, UPPER = INCUMBENT_R4['provenance']['bounds']
REACTIONS = probe.reactions(probe.SOURCE_R4)
assert {k: v for k, v in REACTIONS.items() if k.startswith('reaction:R4:')} == probe.SOURCE_R4, 'R4 is not the source'
STARTS = {
    'pre-refit': [s.parameter_values(probe.with_values(s.parameter_mapping(probe.RECORD), {IDS[4]: 0.0}))[i] for i in IDS],
    'incumbent-R4-C': INCUMBENT_R4['pre-refit']['fitted'],  # its optimum; every start reached it
    'seed-1': list(np.random.default_rng(1).uniform(LOWER, UPPER)),
}


def parameters(values, ids=IDS):
    return epcsaft.Parameters.from_mapping(probe.with_values(s.parameter_mapping(probe.RECORD), dict(zip(ids, values))))


def _rec(o):
    return {'T': o['request']['temperature']['value'], 'identity': o['identity']}


def states(pco2_max_c=None):
    """(packet observation, declared problem) for every calibration state (compare.in_objective)."""
    out = []
    for o in probe.OBSERVATIONS:
        if not any(in_objective(_rec(o), t, pco2_max_c) for t in o['targets']):
            continue
        base = probe.base_record(o)
        anchor = s.anchor_from(base) if base['status'] == 'evaluated' else None
        out.append((o, s._problem_from_request(s.corrected_request(o['request'], REACTIONS), anchor)))
    return out


def observations(params, o, prob, pco2_max_c=None):
    """(target identity, observation, weight) for one packet state, as compare.residuals scores it."""
    outputs = {x['identity']: x for x in o['request']['outputs']}
    rows = []
    for t in o['targets']:
        if not in_objective(_rec(o), t, pco2_max_c):
            continue
        output = outputs[t['prediction_identity']]
        support = prob.phases[[p.name for p in prob.phases].index(output['phase_identity'])].support or s.COMPONENT_IDS
        assert all(c in (0.0, 1.0) for c in output['coefficients']), output
        species = pooled_species(t['identity']) or tuple(
            name for name, c in zip(support, output['coefficients'], strict=True) if c)
        if t['prediction_identity'] == 'co2-partial-pressure':
            item = regression.observation(params, 'partial_pressure', prob, observed=t['observed'], form='log_ratio',
                                          mass_basis=False, phase=output['phase_identity'], species=species)
            rows.append((t['identity'], item, 1.0 / SIGMA_LN_P**2))
        else:
            item = regression.observation(params, 'mole_fraction', prob, observed=t['observed'], form='difference',
                                          scale=0.1 * t['observed'] + 0.001, mass_basis=False,
                                          phase=output['phase_identity'], species=species)
            rows.append((t['identity'], item, 1.0))
    return rows


def identifiability(result, J, r, ids, lower, upper):
    """Column-normalized singular values; the cost gradient at the final point (an active-bound coordinate whose
    gradient points out of the box is held there); and, for coordinates off their bounds, the covariance
    conditional on the active-bound coordinates held fixed (the Engine withholds the full covariance there)."""
    free = [k for k in range(len(ids)) if k not in set(result.covariance.active_bounds)]
    s2 = float(r @ r / (len(r) - len(free)))
    cov = s2 * np.linalg.inv(J[:, free].T @ J[:, free])
    se = np.sqrt(np.diag(cov))
    gradient = J.T @ r  # d(0.5 sum r^2)/d(theta), physical units
    return {'column_normalized_singular_values': list(np.linalg.svd(J / np.linalg.norm(J, axis=0), compute_uv=False)),
            'cost_gradient': dict(zip(ids, gradient)),
            'active_bound_outward_descent': {  # outward is +1 at the upper bound, -1 at the lower
                ids[k]: bool(-gradient[k] * (1 if upper[k] - result.physical[k] < result.physical[k] - lower[k] else -1) > 0)
                for k in result.covariance.active_bounds},
            'free_coordinates': [ids[k] for k in free], 'residual_variance': s2,
            'conditional_standard_error': dict(zip((ids[k] for k in free), se)),
            'conditional_correlation': (cov / np.outer(se, se)).tolist()}


def write_rows(path, start, rows):
    kept = [r for r in (list(csv.DictReader(path.open())) if path.exists() else []) if r['start'] != start]
    rows = kept + rows
    if not rows:
        return
    with path.open('w', newline='') as h:
        w = csv.DictWriter(h, list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main(names, ids=IDS, lower=LOWER, upper=UPPER, starts=STARTS, stem=HERE / 'refit-C', pco2_max_c=None):
    OUT, ITERATIONS, JACOBIAN = (Path(f'{stem}-{n}') for n in ('multistart.json', 'iterations.csv', 'jacobian.csv'))
    scales = [10.0 if i.endswith(probe.SLOPE) else 0.01 for i in ids]
    clock = perf_counter()
    calibration = states(pco2_max_c)
    setup_s = perf_counter() - clock
    record = json.loads(OUT.read_text()) if OUT.exists() else {}
    for name in names or starts:
        start = starts[name]
        params = parameters(start, ids)
        rows = [row for o, prob in calibration for row in observations(params, o, prob, pco2_max_c)]
        assert len(rows) == {None: 180, 80: 160}[pco2_max_c], len(rows)
        coordinates = [regression.coordinate(params, 'k_ij_reciprocal_temperature_slope' if i.endswith(probe.SLOPE) else 'k_ij',
                                             tuple(i.split('/')[1:3]), origin=x0, scale=h, bounds=(lo, hi))
                       for i, x0, h, lo, hi in zip(ids, start, scales, lower, upper)]
        controls = regression.FitControls()
        controls.maximum_iterations = 100
        controls.maximum_elapsed_time_seconds = 7200.0
        clock = perf_counter()
        result = regression.fit(params, coordinates, [item for _, item, _ in rows], weights=[w for _, _, w in rows],
                                controls=controls)
        fit_s = perf_counter() - clock
        c = result.covariance
        # a start that ends without a final Jacobian (e.g. a failed initial evaluation) is recorded, not scored
        J = (np.array(result.optimizer_jacobian).reshape(len(rows), len(ids)) / np.array(scales)  # weighted, physical
             if len(result.optimizer_jacobian) else None)
        r = np.array(result.weighted_residuals)
        record[name] = {
            'start': start, 'fitted': list(result.physical), 'status': result.status, 'message': result.message,
            'usable': result.usable, 'initial_cost': result.initial_cost, 'final_cost': result.final_cost,
            'iterations': result.iterations, 'residual_evaluations': result.residual_evaluations,
            'jacobian_evaluations': result.jacobian_evaluations, 'trial_failures': result.trial_failures,
            'failures': [{'trial': f.trial, 'observation': rows[f.observation][0], 'status': f.status.name,
                          'message': f.message, 'jacobian': f.jacobian} for f in result.failures],
            'active_bounds': [ids[k] for k in c.active_bounds],
            'engine_covariance': {'status': c.status, 'assumption': c.assumption, 'rank': c.rank,
                                  'singular_values': list(c.singular_values), 'variance_factor': c.variance_factor},
            **(identifiability(result, J, r, ids, lower, upper) if J is not None else {}), 'fit_s': fit_s,
            'setup_s': setup_s}
        born = next(f for f in s.parameter_mapping(probe.RECORD)['model_families'] if f['kind'] == 'electrolyte')
        record['provenance'] = {'parameters': ids, 'bounds': [lower, upper], 'scales': scales, 'n_rows': len(rows),
                                'pco2_max_c': pco2_max_c,
                                'born': {k: born.get(k) for k in ('c_shell', 'c_dielectric')},
                                'reaction_overrides': probe.SOURCE_R4, 'excluded_states': sorted(EXCLUDED),
                                'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'engine_commit': s.ENGINE_COMMIT,
                                'base_record_sha256': s.sha256(probe.RECORD),
                                'state_packet_sha256': s.sha256(s.STATE_PACKET), 'script_sha256': s.sha256(Path(__file__))}
        OUT.write_text(json.dumps(record, indent=1) + '\n')
        write_rows(ITERATIONS, name, [{'start': name, 'iteration': k, 'cost': cost, 'seconds': sec} for k, (cost, sec)
                                      in enumerate(zip(result.iteration_costs, result.iteration_seconds))])
        write_rows(JACOBIAN, name, [] if J is None else [{'start': name, 'target': t, 'weight': w, 'prediction': y, 'weighted_residual': rr,
                                     **{f'd/d[{i}]': v for i, v in zip(ids, row)}}
                                    for (t, _, w), y, rr, row in zip(rows, result.predictions, r, J)])
        print(name, result.status, result.message, result.initial_cost, result.final_cost, result.iterations,
              list(result.physical), [ids[k] for k in c.active_bounds], round(fit_s), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
