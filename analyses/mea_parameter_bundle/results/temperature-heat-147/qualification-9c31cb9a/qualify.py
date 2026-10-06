"""Reuse the retained #147 driver with the successor wheel and separate outputs."""
import os
from pathlib import Path

TAG = os.environ.get('EPCSAFT_147_WHEEL_TAG', '9c31cb9a')
OUT = Path(__file__).resolve().parent.with_name(f'qualification-{TAG}')
original = OUT.parent / 'qualify.py'
source = original.read_text()
replacements = {
    'HERE = Path(__file__).resolve().parent': 'HERE = Path(__file__).resolve().parent.parent',
    'ePC-SAFT-build-717a2990': f'ePC-SAFT-build-{TAG}',
    '717a2990e443423e051fc0569f25209d04007543': os.environ.get('EPCSAFT_147_ENGINE_COMMIT', '9c31cb9a89b6fb42fd386ca44de2331601b4751c'),
    '9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4': os.environ['EPCSAFT_147_WHEEL_SHA256'],
    "RAW = BUNDLE / 'results/runs/temperature-heat-147'": f"RAW = BUNDLE / 'results/runs/temperature-heat-147/qualification-{TAG}'",
    'pa.save(HERE /': 'pa.save(OUT /',
    'pa.table(HERE /': 'pa.table(OUT /',
    "'build_jobs': len(os.sched_getaffinity(0))": "'build_jobs': 1",
    'budget_s=180, limits=s.EvaluationLimits(180, 180)': 'budget_s=175, limits=s.EvaluationLimits(175, 175)',
    "'identity': rec['identity'], 'target':": "'module_origin': probe.epcsaft.__file__, 'identity': rec['identity'], 'target':",
    "path = HERE / f'calorimetry-": "path = OUT / f'calorimetry-",
    "    path = OUT / f'calorimetry-": (
        "    if sys.argv[1] != 'Q1-heat':\n        return model, params, initial, final, item, mapping, thermal, request['reaction_system']\n    path = OUT / f'calorimetry-"),
    "if __name__ == '__main__':": f"pa.save(OUT / 'installed-record-check.json', pa.verify(RAW.parent / '.venv-{TAG}'))\nif __name__ == '__main__' and sys.argv[1] in ('freeze', 'R1', 'Q1-mapping', 'Q1-heat'):",
}
for old, new in replacements.items():
    assert old in source, old
    source = source.replace(old, new)
exec(compile(source, str(original), 'exec'), globals())
if sys.argv[1] in ('freeze', 'R1', 'Q1-mapping', 'Q1-heat'):
    sys.exit(0)
import subprocess
from epcsaft import equilibrium as eq, regression as reg

def native(job, alpha, extra, output):
    model, params, initial, final, item, mapping, thermal, system = heat_case(alpha)
    assert initial.feed.values['carbon-dioxide'] == 0 and len(initial.reactions) == 5
    assert initial.reactions == final.reactions
    output['feed_balance_errors'] = {c: final.feed.values.get(c, 0)-initial.feed.values.get(c, 0)-(alpha if c == 'carbon-dioxide' else 0) for c in s.COMPONENT_IDS}
    assert max(map(abs, output['feed_balance_errors'].values())) <= 1e-12
    for field in ('solvent', 'solute_molality_ratios', 'standard_molality_mol_per_kg'):
        assert getattr(initial.neutral_reference, field) == getattr(final.neutral_reference, field)
    if job in ('state', 'bubble'):
        problem = (initial, final)[int(extra[0])]
        if job == 'bubble':
            problem = eq.Problem(T=313.15, P=eq.Free(), feed=problem.feed, reactions=problem.reactions, neutral_reference=problem.neutral_reference,
                phases=[problem.phases[0], eq.Phase('V', kind='vapor', support=s.COMPONENT_IDS[:3], amount=eq.Pinned(0))])
        result = eq.solve_equilibrium(model, problem)
        output['state'] = {k: s._jsonable(getattr(result, k)) for k in ('success', 'message', 'solver_status', 'requested_tolerance_met', 'pressure', 'amounts', 'mole_fractions', 'molar_densities', 'coordinates', 'residuals', 'classified_residuals', 'neutral_reference_diagnostics')}
        assert result.success and result.requested_tolerance_met, result.message
        output['raw_rows'] = list(eq.compile_problem(model, problem).evaluate(result.coordinates).values)
        amounts = [math.fsum(result.amounts[p]*result.mole_fractions[9*p+i] for p in range(result.phase_count)) for i in range(9)]
        delta = [n-problem.feed.values.get(c, 0) for c, n in zip(s.COMPONENT_IDS, amounts, strict=True)]
        output['material_errors_mol'] = [math.fsum(c*n for c, n in zip(row, delta, strict=True)) for row in system['balance_matrix']]
        output['charge_error_mol'] = math.fsum(c*n for c, n in zip(system['charges'], amounts, strict=True))
        if int(extra[0]) == 0:
            assert all(amounts[s.COMPONENT_IDS.index(c)] == 0 for c in ('carbon-dioxide', 'carbamate-anion', 'bicarbonate-anion', 'carbonate-anion'))
        if job == 'state':
            (h, _), (n, _) = thermal.first_actions(model, problem, result, [thermal.observable('PhaseProperty', 0, prop=thermal.PropertyObservable.TotalEnthalpy), thermal.observable('PhaseAmount', 0)], [(0., 0., None)])[0]
            output['H_J'] = h*n
        return
    if job == 'feed':
        feed_params = probe.epcsaft.Parameters.from_mapping(mapping, components=['carbon-dioxide'])
        feed_record = thermal.record()
        feed_thermal = probe.epcsaft.ThermochemistryRecord(feed_record.standard_pressure,
            [feed_record.component_intervals[s.COMPONENT_IDS.index('carbon-dioxide')]])
        feed_model = probe.epcsaft.Pure(feed_params, thermochemistry=feed_thermal)
        state = feed_model.state(313.15, P=1734000., phase='vapor')
        output['feed_root'] = {k: s._jsonable(getattr(state, k)) for k in ('molar_density', 'pressure_density_derivative', 'stable_root_count', 'density_branch', 'residual_enthalpy', 'ideal_enthalpy', 'total_enthalpy', 'thermochemistry_status')}
        assert state.stable_root_count == 1 and all(math.isfinite(x) and x > 0 for x in (state.pressure_density_derivative, state.molar_density))
        assert state.total_enthalpy is not None and math.isfinite(state.total_enthalpy)
        output['prediction'] = {'value': state.total_enthalpy, 'status': 'Available', 'message': ''}
        return
    if job == 'shift':
        thermal.CALORICS['components']['carbon-dioxide']['formation_enthalpy_j_per_mol'] += 10000.
        model = probe.epcsaft.Mixture(params, thermochemistry=thermal.record())
    if job == 'fd':
        identity, change = extra[0], float(extra[1])
        params = probe.epcsaft.Parameters.from_mapping(probe.with_values(mapping, {identity: s.parameter_values(mapping).get(identity, 0.)+change}))
        model = probe.epcsaft.Mixture(params, thermochemistry=thermal.record())
    if job == 'gradient':
        chart = reg.CoordinateSet()
        chart.coordinates = [reg.coordinate(params, 'k_ij_reciprocal_temperature_slope' if identity == pa.SLOPE else 'k_ij', tuple(identity.split('/')[1:3]), origin=0., scale=1.) for identity in pa.IDS+[pa.SLOPE]]
        model = probe.epcsaft.Mixture(params, thermochemistry=thermal.record(), active_parameters=chart.active())
    prediction = reg.differentiate(model, item) if job == 'gradient' else reg.predict(model, item)
    output['prediction'] = {k: s._jsonable(getattr(prediction, k)) for k in ('value', 'status', 'message')}
    assert prediction.status.name == 'Available', prediction.message

def run(job, alpha, *extra):
    clock = time.perf_counter()
    path = OUT / ('-'.join([job, str(alpha), *map(str, extra)]).replace('/', '_')+'.json')
    command = ['timeout', '-k', '5s', str(min(175., budgets[family]-5))+'s', 'uv', 'run', '--no-project', '--active', 'python', str(Path(__file__)), job, str(alpha), *map(str, extra)]
    assert budgets[family] > 5, 'qualification parent budget exhausted'
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    elapsed = time.perf_counter()-clock
    budgets[family] -= elapsed
    record['calls'].append({'job': job, 'alpha': alpha, 'extra': extra, 'elapsed_s': elapsed, 'exit_code': completed.returncode, 'output': completed.stdout})
    pa.save(OUT/'remaining-qualification.json', record)
    assert completed.returncode == 0, record['calls'][-1]
    return json.loads((OUT/f'calorimetry-{alpha:g}.json' if job == 'Q1-heat' else path).read_text())

record = {'module_origin': probe.epcsaft.__file__, 'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'producer_sha256': s.sha256(Path(__file__)), 'calls': [], 'checks': {}, 'stage': '3'}
try:
    if sys.argv[1] != 'remaining':
        job, alpha = sys.argv[1], float(sys.argv[2])
        native(job, alpha, sys.argv[3:], record)
        pa.save(OUT/('-'.join(sys.argv[1:]).replace('/', '_')+'.json'), record)
    else:
        budgets, family, cases = {'Q1': 1770.-49.79, 'Q2': 1770.}, 'Q1', {}
        for alpha in (.11, .45):
            cases[alpha] = [run('Q1-heat', alpha), run('state', alpha, 0), run('state', alpha, 1), run('feed', alpha)]
        for alpha, (heat, initial, final, feed) in cases.items():
            record['stage'] = '4'
            value, hi, hf, hfeed = heat['prediction']['value'], initial['H_J'], final['H_J'], feed['prediction']['value']
            allowance = 1e-9*abs(value)+1e-9*(abs(hi)+abs(hf))/alpha+1e-6
            row = {'direct_J_mol': (hf-hi)/alpha-hfeed, 'allowance_J_mol': allowance, 'conditioning': (abs(hi)+abs(hf))/(alpha*abs(value)), 'shift_J_mol': run('shift', alpha)['prediction']['value']}
            record['checks'][str(alpha)] = row
            assert abs(row['direct_J_mol']-value) <= allowance and abs(row['shift_J_mol']-value) <= allowance and row['conditioning'] <= 1e4, row
        family, record['stage'] = 'Q2', '5'
        for alpha in cases:
            exact = run('gradient', alpha)['prediction']['value']
            for identity, action in zip(pa.IDS+[pa.SLOPE], exact, strict=True):
                h = 1. if identity == pa.SLOPE else 1e-4
                values = [run('fd', alpha, identity, sign*step)['prediction']['value'] for step in (h, 2*h) for sign in (1, -1)]
                fine, coarse = (values[0]-values[1])/(2*h), (values[2]-values[3])/(4*h)
                row = {'identity': identity, 'exact': action, 'fine': fine, 'coarse': coarse, 'fine_ratio': abs(action-fine)/(5e-6*max(1., abs(fine))), 'coarse_ratio': abs(action-coarse)/(20e-6*max(1., abs(fine))), 'truncation_estimate': abs(coarse-fine)/3, 'roundoff_estimate': 8*max(map(math.ulp, values))/h}
                record['checks'][str(alpha)].setdefault('Jacobian', []).append(row)
                assert row['fine_ratio'] <= 1 and row['coarse_ratio'] <= 1, row
        family, record['stage'] = 'Q1', '6'
        for _, initial, final, _ in cases.values():
            for endpoint in (initial, final):
                assert max(map(abs, endpoint['raw_rows'])) <= 1e-10 and max(map(abs, endpoint['material_errors_mol'])) <= 1e-7 and abs(endpoint['charge_error_mol']) <= 1e-7, endpoint
        record['stage'] = '6.1'
        for alpha, endpoint in ((.11, 0), (.11, 1), (.45, 1)):
            boundary = run('bubble', alpha, endpoint)
            assert 1734000. > boundary['state']['pressure'][0]*(1+1e-7) and max(map(abs, boundary['raw_rows'])) <= 1e-10, boundary
            assert max(map(abs, boundary['material_errors_mol'])) <= 1e-7 and abs(boundary['charge_error_mol']) <= 1e-7, boundary
        record['passed'] = True
        pa.save(OUT/'remaining-qualification.json', record)
except Exception as error:
    record.update(exception=type(error).__name__, message=str(error))
    pa.save(OUT/('remaining-qualification.json' if sys.argv[1] == 'remaining' else '-'.join(sys.argv[1:]).replace('/', '_')+'.json'), record)
    raise
