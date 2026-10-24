"""MEA-water permittivity at the reported parameters (#207). The 14 Agieienko-Buchner samples at 298.15 K and 101325 Pa are
evaluated as the permittivity fit evaluated them (equation-of-state liquid density, then the solvent law), with every parameter
taken from the selected record. Writes results/mea-water-permittivity/; no fitting."""
import csv, json, math, sys
from pathlib import Path
BUNDLE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(BUNDLE / 'calibration-misfit')]
import shared_evaluation as s, epcsaft

ROWS = BUNDLE / 'data/input/fit-campaigns/joint-recalibration-170-dielectric-rows.csv'
FIT_STAGE = BUNDLE / 'results/joint-recalibration-170/amendment-2/stage5-smaller-dV/rows.json'
OUT = BUNDLE / 'results/mea-water-permittivity'
T, P = 298.15, 101325.


def main(parameters=s.PARAMETERS):
    mapping = s.parameter_mapping(parameters)
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    value = {c['identity']: c['value']['magnitude'] for n in mapping['components'] for c in n['coefficients']}
    mass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']}
    d = lambda q: {k: value[f'component/{k}/dielectric_{q}'] for k in ('monoethanolamine', 'water')}
    fit_stage = {r['sample_id']: r['larger-dV_epsilon'] for r in json.loads(FIT_STAGE.read_text())}
    out = []
    for row in csv.DictReader(ROWS.open()):
        w = float(row['MEA_wt_percent']) / 100
        n = {'monoethanolamine': w / mass['monoethanolamine'], 'water': (1 - w) / mass['water']}
        x = {k: v / sum(n.values()) for k, v in n.items()}
        state = model.state(T, P=P, x=x, phase='liquid')
        assert state.pressure_density_derivative > 0 and abs(state.pressure - P) < 1e-3
        rho = state.molar_density / 1000  # mol/L, the unit of the dielectric volumes
        solvent_law = 1 + rho * sum(x[k] * d('volume')[k] for k in x) * (sum(x[k] * d('temperature')[k] for k in x) / T - 1)
        calculated = state.bulk_relative_permittivity
        assert abs(calculated - solvent_law) < 1e-10, (row['sample_id'], calculated, solvent_law)
        observed = float(row['epsilon_s'])
        out.append(dict(sample_id=row['sample_id'], MEA_wt_percent=row['MEA_wt_percent'], MEA_mole_fraction=x['monoethanolamine'],
                        temperature_K=T, pressure_Pa=P, density_kg_m3=state.molar_density * sum(x[k] * mass[k] for k in x),
                        observed_epsilon=observed, calculated_epsilon=calculated, fit_stage_epsilon=fit_stage[row['sample_id']],
                        relative_deviation=calculated / observed - 1))
    assert len(out) == 14 and out[0]['MEA_wt_percent'] == '0' and abs(out[0]['calculated_epsilon'] - out[0]['fit_stage_epsilon']) < 1e-10  # water alone is unchanged
    error = [r['calculated_epsilon'] - r['observed_epsilon'] for r in out]
    summary = dict(parameter_sha256=s.sha256(parameters), engine_commit=s.ENGINE_COMMIT, engine_wheel_sha256=s.ENGINE_WHEEL_SHA256,
                   inputs={str(p.relative_to(BUNDLE.parents[1])): s.sha256(p) for p in (ROWS, FIT_STAGE)}, n=len(out),
                   rmse=math.sqrt(sum(e * e for e in error) / len(error)), max_abs_error=max(map(abs, error)),
                   aard_percent=100 * sum(abs(r['relative_deviation']) for r in out) / len(out),
                   cost=.5 * sum((e / (.01 * r['observed_epsilon'])) ** 2 for e, r in zip(error, out)),
                   max_abs_change_from_fit_stage=max(abs(r['calculated_epsilon'] - r['fit_stage_epsilon']) for r in out),
                   checks='native permittivity equals the solvent law at the equation-of-state density within 1e-10; pure water reproduces the fit stage')
    OUT.mkdir(exist_ok=True)
    with (OUT / 'rows.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)
    s.write_json(OUT / 'summary.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
