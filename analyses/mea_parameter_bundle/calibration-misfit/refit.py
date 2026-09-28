"""Refit C through epcsaft.regression.fit: Ceres Levenberg-Marquardt with exact implicit derivatives, multistart.

Usage: refit.py [START ...]   (default: every start in STARTS; results merge into refit-C-multistart.json)
Coordinates, bounds and scales are refit C's (refit-C-converged.json): four ion k_ij within +-0.3 and the
MEAH+-water k_ij 1/T slope within +-300 K (T_ref 313.15 K); R4 stays at its source value.
Rows (compare.residuals scores the same rows from probe records): every packet state except 80 degC and the three
the pre-refit record failed on the old pin (compare.EXCLUDED), 180 rows. pCO2: ln(pred/obs), weight 1/0.3^2.
Species: (pred - obs)/(0.1 obs + 0.001), weight 1; the NMR "HCO3-" target is model HCO3- + CO3^2-.
Each state is declared from the base record's solve (MEA liquid anchor), as Engine
analyses/2026-mea-reactive-fit-timing/scripts/run.py declares it. Base record: probe.RECORD.
Diagnostic only: never writes the selected parameter record.
"""
import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

import probe
from compare import EXCLUDED, SIGMA_LN_P, is_validation

s, epcsaft = probe.shared, probe.epcsaft
from epcsaft import regression  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / 'refit-C-multistart.json'
REFIT_C = json.loads((HERE / 'refit-C-converged.json').read_text())  # old pin: coordinates, bounds, fitted values
IDS, (LOWER, UPPER) = REFIT_C['parameters'], REFIT_C['bounds']
SCALES = [10.0 if i.endswith(probe.SLOPE) else 0.01 for i in IDS]  # refit C's sweep steps (scipy x_scale)
HCO3_POOL = ('bicarbonate-anion', 'carbonate-anion')
REACTIONS = s._selected_reactions()


def _seeded(seed):
    return list(np.random.default_rng(seed).uniform(LOWER, UPPER))


STARTS = {
    'pre-refit': [s.parameter_values(probe.with_values(s.parameter_mapping(probe.RECORD), {IDS[4]: 0.0}))[i] for i in IDS],
    'old-refit-C': REFIT_C['fitted'],
    'zero': [0.0] * len(IDS),
    'seed-1': _seeded(1),
    'seed-2': _seeded(2),
}


def parameters(values):
    return epcsaft.Parameters.from_mapping(probe.with_values(s.parameter_mapping(probe.RECORD), dict(zip(IDS, values))))


def states():
    """(identity, packet observation, declared problem) for every calibration state."""
    out = []
    for o in probe.OBSERVATIONS:
        if is_validation({'T': o['request']['temperature']['value']}) or o['identity'] in EXCLUDED:
            continue
        base = probe.base_record(o)
        anchor = s.anchor_from(base) if base['status'] == 'evaluated' else None
        out.append((o['identity'], o, s._problem_from_request(s.corrected_request(o['request'], REACTIONS), anchor)))
    return out


def observations(params, o, prob):
    """(target identity, observation, weight) for one packet state, as compare.residuals scores it."""
    outputs = {x['identity']: x for x in o['request']['outputs']}
    rows = []
    for t in o['targets']:
        output = outputs[t['prediction_identity']]
        support = prob.phases[[p.name for p in prob.phases].index(output['phase_identity'])].support or s.COMPONENT_IDS
        assert all(c in (0.0, 1.0) for c in output['coefficients']), output
        species = HCO3_POOL if t['identity'].endswith('::HCO3-') else tuple(
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


def identifiability(result, n_rows):
    """Column-normalized singular values and, for the coordinates off their bounds, the covariance conditional on
    the active-bound coordinates held fixed (the Engine withholds the full covariance at an active bound)."""
    J = np.array(result.optimizer_jacobian).reshape(n_rows, len(IDS)) / np.array(SCALES)  # weighted, physical units
    free = [k for k in range(len(IDS)) if k not in set(result.covariance.active_bounds)]
    r = np.array(result.weighted_residuals)
    s2 = float(r @ r / (n_rows - len(free)))
    cov = s2 * np.linalg.inv(J[:, free].T @ J[:, free])
    se = np.sqrt(np.diag(cov))
    return {'column_normalized_singular_values': list(np.linalg.svd(J / np.linalg.norm(J, axis=0), compute_uv=False)),
            'free_coordinates': [IDS[k] for k in free], 'residual_variance': s2,
            'conditional_standard_error': dict(zip((IDS[k] for k in free), se)),
            'conditional_correlation': (cov / np.outer(se, se)).tolist()}


def main(names):
    clock = perf_counter()
    calibration = states()
    setup_s = perf_counter() - clock
    record = json.loads(OUT.read_text()) if OUT.exists() else {}
    for name in names or STARTS:
        start = STARTS[name]
        params = parameters(start)
        rows = [row for _, o, prob in calibration for row in observations(params, o, prob)]
        assert len(rows) == 180, len(rows)
        coordinates = [regression.coordinate(params, 'k_ij_reciprocal_temperature_slope' if i.endswith(probe.SLOPE) else 'k_ij',
                                             tuple(i.split('/')[1:3]), origin=x0, scale=h, bounds=(lo, hi))
                       for i, x0, h, lo, hi in zip(IDS, start, SCALES, LOWER, UPPER)]
        controls = regression.FitControls()
        controls.maximum_iterations = 100
        controls.maximum_elapsed_time_seconds = 7200.0
        clock = perf_counter()
        result = regression.fit(params, coordinates, [item for _, item, _ in rows], weights=[w for _, _, w in rows],
                                controls=controls)
        fit_s = perf_counter() - clock
        c = result.covariance
        record[name] = {
            'start': start, 'fitted': list(result.physical), 'status': result.status, 'message': result.message,
            'usable': result.usable, 'initial_cost': result.initial_cost, 'final_cost': result.final_cost,
            'iterations': result.iterations, 'iteration_seconds': list(result.iteration_seconds),
            'iteration_costs': list(result.iteration_costs), 'residual_evaluations': result.residual_evaluations,
            'jacobian_evaluations': result.jacobian_evaluations, 'trial_failures': result.trial_failures,
            'failures': [{'trial': f.trial, 'observation': rows[f.observation][0], 'status': f.status.name,
                          'message': f.message, 'jacobian': f.jacobian} for f in result.failures],
            'active_bounds': [IDS[k] for k in c.active_bounds],
            'engine_covariance': {'status': c.status, 'assumption': c.assumption, 'rank': c.rank,
                                  'singular_values': list(c.singular_values), 'variance_factor': c.variance_factor,
                                  'physical': list(c.physical)},
            **identifiability(result, len(rows)),
            'rows': [{'target': t, 'weight': w, 'prediction': y, 'weighted_residual': r} for (t, _, w), y, r
                     in zip(rows, result.predictions, result.weighted_residuals)],
            'fit_s': fit_s, 'setup_s': setup_s}
        record['provenance'] = {'parameters': IDS, 'bounds': [LOWER, UPPER], 'scales': SCALES, 'n_rows': len(rows),
                                'excluded_states': sorted(EXCLUDED), 'wheel_sha256': s.ENGINE_WHEEL_SHA256,
                                'engine_commit': s.ENGINE_COMMIT, 'base_record_sha256': s.sha256(probe.RECORD),
                                'state_packet_sha256': s.sha256(s.STATE_PACKET), 'script_sha256': s.sha256(Path(__file__))}
        OUT.write_text(json.dumps(record, indent=1) + '\n')
        print(name, result.status, result.message, result.initial_cost, result.final_cost, result.iterations,
              list(result.physical), [IDS[k] for k in c.active_bounds], round(fit_s), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
