"""Pure-PZ diagnostic on the immutable Engine wheel; no parameter estimation."""
import csv
import hashlib
import json
import math
import zipfile
from pathlib import Path

import epcsaft
from epcsaft import equilibrium as eq

AN = Path(__file__).resolve().parent
WHEEL = AN.parents[1] / 'build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl'
SHA = '0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'


def write_csv(name, rows):
    with (AN / 'results' / name).open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def calculate():
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
    with zipfile.ZipFile(WHEEL) as archive:
        for name in archive.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert archive.read(name) == (Path(epcsaft.__file__).parent.parent / name).read_bytes(), name
    model = epcsaft.Pure(epcsaft.Parameters.from_mapping(json.loads((AN / 'inputs/razavi.json').read_text())))

    def solve(T, tolerance=None):
        problem = model.saturation(T)
        if tolerance is not None:
            problem.row_tolerance = tolerance
        result = eq.solve_equilibrium(model, problem)
        assert result.requested_tolerance_met and result.pressure is not None, (T, result.solver_status, result.residuals)
        assert result.molar_densities[0] > result.molar_densities[1] > 0
        return dict(T_K=T, model_kPa=result.pressure / 1000,
                    liquid_mol_m3=result.molar_densities[0], vapor_mol_m3=result.molar_densities[1],
                    max_residual=max(map(abs, result.residuals)), solver_status=result.solver_status,
                    row_tolerance=result.convergence.criterion.value)

    rows = []
    for source in csv.DictReader((AN / 'inputs/steele-table7.csv').open()):
        T, observed, sigma = (float(source[k]) for k in ('T_K', 'p_kPa', 'sigma_kPa'))
        row = solve(T)
        refined = solve(T, 1e-12)
        delta = row['model_kPa'] - observed
        row.update(observed_kPa=observed, sigma_kPa=sigma, difference_kPa=delta,
                   relative_percent=100 * delta / observed, log_ratio=math.log(row['model_kPa'] / observed),
                   residual_sigma=delta / sigma, outside_one_sigma_kPa=abs(delta) - sigma,
                   refined_kPa=refined['model_kPa'], refined_row_tolerance=refined['row_tolerance'],
                   refined_max_residual=refined['max_residual'], refinement_sigma=abs(refined['model_kPa']-row['model_kPa']) / sigma,
                   hartono_kPa=10 ** (5.9832 - 1215.77 / (T - 113.56)))
        liquid = model.state(T, rho=row['liquid_mol_m3'])
        vapor = model.state(T, rho=row['vapor_mol_m3'])
        at_observed = [model.state(T, P=observed*1000, phase=phase) for phase in ('liquid', 'vapor')]
        row.update(eos_pressure_difference_Pa=liquid.pressure-vapor.pressure,
                   log_fugacity_difference=liquid.log_fugacity_coefficient[0]-vapor.log_fugacity_coefficient[0],
                   observed_pressure_log_fugacity_difference=at_observed[0].log_fugacity_coefficient[0]-at_observed[1].log_fugacity_coefficient[0])
        rows.append(row)
        print(json.dumps(row), flush=True)
    write_csv('pressure-residuals.csv', rows)
    curve = [solve(417.997 + i * (460.477 - 417.997) / 60) for i in range(61)]
    for row in curve:
        row['hartono_kPa'] = 10 ** (5.9832 - 1215.77 / (row['T_K'] - 113.56))
    write_csv('liquid-curve.csv', curve)
    extrapolation = [dict(solve(T), classification='subcooled-liquid extrapolation' if T < 384.6 else 'liquid extrapolation below measured span')
                     for T in sorted({283., 293.15, 313.15, 333.15, 353.15, 373.15, 384.6, 393.15, *[283.+i*2 for i in range(68)]})]
    write_csv('extrapolation.csv', extrapolation)
    summary = dict(wheel_sha256=SHA, installed_files_byte_identical=True,
                   bias_kPa=sum(r['difference_kPa'] for r in rows)/len(rows),
                   mean_relative_percent=sum(r['relative_percent'] for r in rows)/len(rows),
                   AARD_percent=sum(abs(r['relative_percent']) for r in rows)/len(rows),
                   max_refinement_sigma=max(r['refinement_sigma'] for r in rows),
                   input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((AN / 'inputs').iterdir())})
    (AN / 'results/summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(summary, flush=True)


if __name__ == '__main__':
    calculate()
