"""Issue 210: reproduce the Baygi 2B isothermal conversion on the pinned wheel."""
import copy
import csv
import importlib.metadata
import json
import math
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'src'), str(Path(__file__).parent)]
import shared_evaluation as s  # noqa: E402
import epcsaft  # noqa: E402
from epcsaft import equilibrium as eq, regression as reg  # noqa: E402
from scipy.optimize import minimize_scalar  # noqa: E402

OUT = ROOT / 'analyses/mea_parameter_bundle/results/engine-3e83e19c-association-volume'
RECORD = ROOT / 'analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/restricted-2/fit/usable-budget-endpoint.json'
MEA, EDGE = 'monoethanolamine', 'association/monoethanolamine/a/monoethanolamine/b/volume'
GRID = [293.15 + 5.0 * i for i in range(31)]
BOUNDS, BAYGI, ORIGINAL = (0.033723, 0.037470), 0.037470, 0.03628703079972324
START = time.monotonic()


def jsonable(value):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, (list, tuple, dict)):
        return {k: jsonable(v) for k, v in value.items()} if isinstance(value, dict) else [jsonable(v) for v in value]
    if hasattr(value, 'name'):
        return value.name
    return {k: jsonable(getattr(value, k)) for k in dir(value) if not k.startswith('_') and k != 'parameters' and not callable(getattr(value, k))}


def write(name, value):
    s.write_json(OUT / name, jsonable(value))


def problem(T):
    return eq.Problem(phases=[eq.Phase('L', kind='liquid', composition_guess=[1.0]),
        eq.Phase('V', kind='vapor', amount=eq.Pinned(0.0), composition_guess=[1.0])],
        T=T, P=eq.Free(math.exp(92.624 - 10367.0 / T - 9.4699 * math.log(T) + 1.9e-18 * T**6)),
        feed=eq.Amounts({MEA: 1.0}), row_tolerance=1e-10)


def parameters(kappa):
    document = copy.deepcopy(DOCUMENT)
    next(e for e in document['topology']['edges'] if e.get('volume', {}).get('identity') == EDGE)['volume']['value']['magnitude'] = kappa
    return epcsaft.Parameters.from_mapping(document, components=[MEA])


def state(kappa, T):
    result = eq.solve_equilibrium(epcsaft.Pure(parameters(kappa)), problem(T))
    p, rho = float(result.pressure), float(result.molar_densities[0])
    residuals = list(result.residuals)
    admitted = (result.success and all(math.isfinite(v) and v > 0 for v in (p, rho))
        and bool(residuals) and all(math.isfinite(v) and abs(v) <= 1e-10 for v in residuals))
    row = dict(T_K=T, kappa=kappa, p_Pa=p, rho_L_mol_m3=rho, admitted=admitted, result=jsonable(result))
    with (OUT / 'solves.jsonl').open('a') as stream:
        stream.write(json.dumps(jsonable(row), allow_nan=False) + '\n')
    if not admitted:
        raise RuntimeError(f'saturation refused at {T} K, kappa={kappa}: {result.message}')
    return {k: v for k, v in row.items() if k != 'result'}


def score(kappa):
    rows, total, squared = [], 0.0, 0.0
    for ref in REFERENCES[:21]:
        row = state(kappa, ref['T_K'])
        p, rho = row['p_Pa'] / ref['p_Pa'] - 1.0, row['rho_L_mol_m3'] / ref['rho_L_mol_m3'] - 1.0
        total += abs(p) + abs(rho)
        squared += p * p + rho * rho
        rows.append(dict(row, p_relative=p, rho_L_relative=rho))
    with (OUT / 'absolute-error-history.jsonl').open('a') as stream:
        stream.write(json.dumps(dict(kappa=kappa, J=total, least_squares_cost=0.5 * squared, rows=rows)) + '\n')
    return total, 0.5 * squared


def main():
    global DOCUMENT, REFERENCES
    OUT.mkdir(parents=True, exist_ok=False)
    s.verify_wheel()
    wheel = s.installed_wheel()
    with zipfile.ZipFile(wheel) as archive:
        assert all((Path(epcsaft.__file__).parent.parent / n).read_bytes() == archive.read(n)
            for n in archive.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
    DOCUMENT = s.parameter_mapping(RECORD)
    component = next(c for c in DOCUMENT['components'] if c['component_id'] == MEA)
    fixed = {c['family']: c['value']['magnitude'] for c in component['coefficients']}
    energy = next(e for e in DOCUMENT['topology']['edges'] if e.get('volume', {}).get('identity') == EDGE)['energy_over_k']['value']['magnitude']
    assert (fixed['segment_count'], fixed['segment_diameter'], fixed['dispersion_energy_over_k'], energy) == (3.0353, 3.0435, 277.174, 2586.3)
    assert s.sha256(RECORD) == 'e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e'
    write('provenance.json', dict(engine_commit=s.ENGINE_COMMIT, wheel_path=str(wheel), wheel_sha256=s.sha256(wheel),
        installed_files_byte_identical=True, record_path=str(RECORD.relative_to(ROOT)), record_sha256=s.sha256(RECORD),
        producer_path=str(Path(__file__).relative_to(ROOT)), producer_sha256=s.sha256(Path(__file__)), command=sys.orig_argv,
        original_commit='d0cb9b8ceb8cf9fc6cfd83b807bd3e81db703341', original_path='analyses/2026-mea-association-diameter/scripts/mea_saturation.py',
        versions={p: importlib.metadata.version(p) for p in ('epcsaft', 'numpy', 'scipy')}, fixed_parameters=fixed, association_energy_over_k_K=energy))
    REFERENCES = [state(BAYGI * (1 - 0.12 * math.exp(-3 * fixed['dispersion_energy_over_k'] / T))**3, T) for T in GRID]
    write('reference-curves.json', REFERENCES)
    best = minimize_scalar(lambda k: score(k)[0], bounds=BOUNDS, method='bounded', options={'xatol': 1e-8})
    write('absolute-error-optimum.json', dict(best))
    if not best.success:
        raise RuntimeError(f'absolute-error search did not converge: {best.message}')
    params, observations, declarations = parameters(BAYGI), [], []
    for ref in REFERENCES[:21]:
        for kind, key, extra in [('pressure', 'p_Pa', {}), ('phase_density', 'rho_L_mol_m3', dict(phase='L', mass_basis=False))]:
            observations.append(reg.observation(params, kind, problem(ref['T_K']), observed=ref[key], scale=ref[key], form='difference', **extra))
            declarations.append(dict(T_K=ref['T_K'], kind=kind, unit='Pa' if kind == 'pressure' else 'mol/m3', observed=ref[key], scale=ref[key], weight=1.0, form='difference', **extra))
    targets = [('association_volume', ((MEA, 'a'), (MEA, 'b')), 1.0)]
    controls = dict(maximum_iterations=100, maximum_elapsed_time_seconds=60, function_tolerance=1e-12, gradient_tolerance=1e-12, parameter_tolerance=1e-10, workers=0)
    write('least-squares-declaration.json', dict(observations=declarations, targets=targets, origin=BAYGI, scale=BAYGI, bounds=BOUNDS, starting_parameter=BAYGI, controls=controls, row_tolerance=1e-10))
    fitted = reg.fit(params, [reg.coordinate(params, targets, origin=BAYGI, scale=BAYGI, bounds=BOUNDS)], observations, weights=[1.0]*42, controls=reg.FitControls(**controls))
    write('least-squares-fit.json', fitted)
    if not (fitted.usable and fitted.status == 'converged' and len(fitted.statuses) == 42 and all(x.name == 'Available' for x in fitted.statuses)
        and len(fitted.predictions) == 42 and all(math.isfinite(x) for x in [*fitted.predictions, *fitted.residuals, *fitted.physical, fitted.final_cost])):
        raise RuntimeError(f'native fit incomplete: {fitted.status}; {fitted.message}')
    cross = {name: dict(kappa=k, J=(v := score(k))[0], least_squares_cost=v[1]) for name, k in [('absolute_error', best.x), ('least_squares', fitted.physical[0])]}
    write('cross-evaluation.json', cross)
    rows = []
    for name, kappa in [('printed', 0.036287), ('absolute_error', best.x), ('least_squares', fitted.physical[0]), ('unconverted', BAYGI)]:
        for ref in REFERENCES:
            row = state(kappa, ref['T_K'])
            rows.append(dict(estimator=name, **row, p_relative=row['p_Pa']/ref['p_Pa']-1, rho_L_relative=row['rho_L_mol_m3']/ref['rho_L_mol_m3']-1))
    write('reporting-grid.json', rows)
    with (OUT / 'reporting-grid.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    aad = {name: {domain: {q: 100 * sum(abs(r[q]) for r in selected) / len(selected) for q in ('p_relative', 'rho_L_relative')}
        for domain, lo, hi in [('293.15-393.15_K', 293.15, 393.15), ('303.15-443.15_K', 303.15, 443.15)]
        if (selected := [r for r in rows if r['estimator'] == name and lo <= r['T_K'] <= hi])} for name in cross.keys() | {'printed', 'unconverted'}}
    absolute_pass = bool(format(best.x, '.5g') == '0.036287' and abs(best.x / ORIGINAL - 1) <= 1e-6)
    ls_pass = format(fitted.physical[0], '.5g') == '0.036287'
    write('summary.json', dict(cross_evaluation=cross, aad_percent=aad, absolute_error_pass=absolute_pass, absolute_relative_difference=abs(best.x/ORIGINAL-1),
        five_figure_roundings={n: format(v['kappa'], '.5g') for n, v in cross.items()}, decision='pass' if absolute_pass and ls_pass else 'stop', wall_seconds=time.monotonic()-START))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        write('stopped.json', dict(cause=f'{type(exc).__name__}: {exc}', wall_seconds=time.monotonic()-START))
        raise
