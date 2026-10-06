"""Issue 160 diagnostics: D1 isolates the water change; D2 frees separate ion segment counts."""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import density_cp_160 as m
from density_cp_160 import s, regression, IONS, DENSITIES, OUT, BUNDLE, F1, request, new_water, module, fit_summary


def run(name):
    directory = OUT / name
    directory.mkdir(parents=True, exist_ok=True)
    os.environ['SENSITIVITY_OUTPUT'] = str(directory)
    os.environ['FINAL_POOL'] = '0'
    d = module('p5160d', BUNDLE / 'model-d/born-form-diagnosis/p5conv-fit.py').d
    adopted = json.loads((OUT / 'new-water-binaries-parameters.json').read_text())
    binary_ids = ('pair/monoethanolamine/water/k_ij', 'pair/carbon-dioxide/water/k_ij')
    if name == 'D1':   # new water + refit binaries, F1 interactions, one-segment ions, no density targets
        mapping = new_water(s.parameter_mapping(F1))
        mapping = s.with_parameter_values(mapping, {i: s.parameter_values(adopted)[i] for i in binary_ids})
    else:              # D2: warm start from the selected F1' optimum, separate ion segment counts
        mapping = s.parameter_mapping(OUT / 'F1-B/parameters.json')
    params, groups, rows = d.rows_for(mapping, '11')
    if name == 'D2':
        for T, a, rho in DENSITIES:
            prob = s._problem_from_request(request(mapping, T, a, density=True))
            rows.append((f'Amundsen_{T}_{a}', regression.observation(params, 'phase_density', prob,
                phase=prob.phases[0].name, observed=rho, form='log_ratio', mass_basis=True), 3906.25))
    v = s.parameter_values(mapping)
    coords = [regression.coordinate(params, 'k_ij_reciprocal_temperature_slope' if i.endswith(d.design.probe.SLOPE) else 'k_ij',
              tuple(i.split('/')[1:3]), origin=v[i], scale=float(sc), bounds=(float(lo), float(hi)))
              for i, sc, lo, hi in zip(d.IDS, d.SCALES, d.LOWER, d.UPPER, strict=True)]
    if name == 'D2':
        coords += [regression.coordinate(params, 'segment_count', ion, origin=v[f'component/{ion}/segment_count'],
                   scale=.1, bounds=(.5, 5.)) for ion in IONS]
    controls = regression.FitControls(); controls.maximum_iterations = 40; controls.maximum_elapsed_time_seconds = 880.
    t0 = time.monotonic()
    fit = regression.fit(params, coords, [r[1] for r in rows], weights=[r[2] for r in rows], controls=controls)
    raw = fit_summary(fit, time.monotonic() - t0)
    raw.update(targets=[r[0] for r in rows], observed=[r[1].observed for r in rows])
    s.write_json(directory / 'native-fit.json', raw)
    print(name, fit.status, round(time.monotonic() - t0, 1), 's', flush=True)


if __name__ == '__main__':
    run(sys.argv[1])
