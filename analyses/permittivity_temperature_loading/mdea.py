"""B1 MDEA same-wheel reproduction and reference-anchored permittivity sensitivity."""
import hashlib
import json
import os
from pathlib import Path
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import epcsaft
from epcsaft import equilibrium as eq
from MEA.solvent_specification import relative_error_statistic
from dielectric_volume import composition, dump, scaled, specification, verify_wheel

AN = Path(__file__).resolve().parent
SOURCE = AN.parent / 'solvent_specification_mdea'
OUT = AN / 'results/mdea'
SPEC = SOURCE / 'B1.toml'
WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-d5138209/epcsaft-1.0.0-cp313-cp313-manylinux_2_39_x86_64.whl')
SHA = 'ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5'
REFERENCE = json.loads((SOURCE / 'results/comparisons.json').read_text()) + [r for r in json.loads(
    (SOURCE / 'results/endpoint-checks.json').read_text())['R1']['records'] if r['identity'] in {f'fit:{i}' for i in range(125, 129)}]


def evaluate(case):
    name, scale, anchor = case
    spec = specification(SPEC, scale)
    rows = spec.inputs['observations']['comparisons'] + [r for r in spec.inputs['observations']['fitted'] if r['identity'] in {f'fit:{i}' for i in range(125, 129)}]
    records = [spec.prediction(row) for row in rows]
    assert len(records) == len({r['identity'] for r in records}) == 436
    if name == 'baseline':
        for result, ref in zip(records, REFERENCE, strict=True):
            assert (result['identity'], result['status']) == (ref['identity'], ref['status'])
            if ref['status'] == 'Available':
                assert result['requested_tolerance_met']
                for key in ('value', 'residual', 'saturation_loading', 'endpoint_loading'):
                    if ref.get(key) is not None:
                        assert abs(result[key] - ref[key]) <= 1e-10 * max(1, abs(ref[key])), (result['identity'], key)
    for row, result in zip(rows, records, strict=True):
        if result['identity'] == 'comparison:370' and result['status'] != 'Available':
            result['known_state_issue'] = 'tannerpolley/ePC-SAFT#1073'
        if result['status'] == 'Available':
            assert result['requested_tolerance_met']
            problem = spec.problems[row.get('problem', row.get('initial'))]
            state = eq.solve_equilibrium(spec.model, problem)
            result['epsilon_primary_state'] = dict(T_K=state.temperature, pressure_Pa=state.pressure, success=state.success,
                requested_tolerance_met=state.requested_tolerance_met, message=state.message)
            if state.success and state.requested_tolerance_met:
                result['epsilon_primary_state']['value'] = spec.model.state(state.temperature, rho=state.molar_densities[0], x=state.phase_mole_fractions(0)).bulk_relative_permittivity
    dump(OUT / name / 'observations.json', records)
    reference = {r['identity']: r for r in REFERENCE}
    groups = {}
    for group in dict.fromkeys(r['group'] for r in records):
        selected = [r for r in records if r['group'] == group]
        matched = [r for r in selected if r['status'] == reference[r['identity']]['status'] == 'Available']
        terms = [r for r in matched if r['observed'] != 0]
        groups[group] = dict(rows=len(selected), statuses={s: sum(r['status'] == s for r in selected) for s in dict.fromkeys(r['status'] for r in selected)},
            matched_available=len(matched), nonzero_terms=len(terms), AARD_percent=relative_error_statistic(terms) if terms else None,
            baseline_matched_AARD_percent=relative_error_statistic([reference[r['identity']] for r in terms]) if terms else None,
            maximum_prediction_change=max((abs(r['value'] / reference[r['identity']]['value'] - 1) for r in matched if reference[r['identity']]['value'] != 0), default=None))
    report = dict(name=name, scale=scale, anchor=anchor, groups=groups, rows=len(records), available=sum(r['status'] == 'Available' for r in records))
    dump(OUT / name / 'summary.json', report)
    print(json.dumps(report), flush=True)
    return report


def main():
    verify_wheel(WHEEL, SHA)
    spec = specification(SPEC, 1.)
    baseline = evaluate(('baseline', 1., {}))
    cases = []
    for T in (353., 393.):
        x = composition(spec.inputs['endpoint'], .30, 'methyldiethanolamine')
        ref = spec.model.state(T, P=101325., x=x, phase='liquid')
        for label, sign in [('minus5', -1), ('plus5', 1)]:
            scale = 1 + sign * .05 * ref.bulk_relative_permittivity / (ref.bulk_relative_permittivity - 1)
            check = epcsaft.Mixture(epcsaft.Parameters.from_mapping(scaled(spec.inputs['endpoint'], scale))).state(T, rho=ref.molar_density, x=x)
            assert abs(check.bulk_relative_permittivity / ref.bulk_relative_permittivity - (1 + sign * .05)) <= 1e-10
            cases.append((f'{T:g}-{label}', scale, dict(T_K=T, pressure_Pa=101325., rho_mol_m3=ref.molar_density,
                epsilon=ref.bulk_relative_permittivity, fixed_density_epsilon=check.bulk_relative_permittivity)))
    with ProcessPoolExecutor(os.cpu_count()) as pool:
        summaries = [baseline, *pool.map(evaluate, cases)]
    files = [Path(__file__), AN / 'dielectric_volume.py', ROOT / 'src/MEA/solvent_specification.py', SPEC,
        SOURCE / 'declarations.toml', *sorted((SOURCE / 'inputs').iterdir()), SOURCE / 'results/comparisons.json', SOURCE / 'results/endpoint-checks.json']
    dump(OUT / 'summary.json', dict(scenarios=summaries, engine_wheel_sha256=SHA, engine_commit='d513820994a78bfe628d42fffd55b2eeab6f89bd',
        module=epcsaft.__file__, workers=os.cpu_count(), threads={k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')},
        inputs={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))


if __name__ == '__main__':
    main()
