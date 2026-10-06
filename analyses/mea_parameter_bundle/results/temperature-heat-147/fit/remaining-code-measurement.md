# Remaining code measured for the parent amendment

No draft was executed or installed. These fragments are documentary measurements, not production code. The 37-line original fit/selection draft is the baseline. Counts include comments and blank lines; deletions provide no credit. No formatter supplied a count. Splitting named output fields follows the existing qualification code; no statements are packed with semicolons.

The shared setup diff retains one owner in timing.py and admits reuse of the verified presolve anchors without another 83-state campaign. It also corrects the heat role and asserts eight heat observations. That source change and another timing job require the parent/owner decision after the retained completeness stop.

Measurement is of a concrete reuse candidate, not proof of a mathematical lower bound. The fragments still need integration; any increase beyond the proposed limits must return to the owner.

| Piece | Gross added lines |
|---|---:|
| `assessment-fixed-pressure-heat.txt` | 40 |
| `assessment-independent-heat-and-loading.txt` | 46 |
| `assessment-limits.txt` | 28 |
| `assessment-pressure-species-wagner.txt` | 38 |
| `assessment-source-units.txt` | 12 |
| `bounded-jobs.txt` | 14 |
| `common-assessment-bindings.txt` | 25 |
| `common-fit-bindings.txt` | 20 |
| `common-input-paths-and-dispatch.txt` | 15 |
| `export-reload-rescore.txt` | 39 |
| `fit-selection.txt` | 37 |
| `freeze.txt` | 15 |
| `identification.txt` | 25 |
| Shared setup changes (diff) | 44 |

## assessment-fixed-pressure-heat.txt

```python
def heat_value(row, mapping):
    temperature, pressure, alpha = row['temperature_K'], row['system_pressure_Pa'], row['alpha_final']
    assert alpha > 0 and temperature <= 353.15
    parameters = epcsaft.Parameters.from_mapping(mapping)
    model = epcsaft.Mixture(parameters, thermochemistry=thermal.record())
    template = copy.deepcopy(observations[0]['request'])
    endpoints, checks = [], []
    for loading in (0., alpha):
        request = s.source_feed_request(template, {'source_key': row['source_key'], 'CO2_loading': loading, 'MEA_weight_fraction': .3, 'temperature_reported_C': temperature-273.15})
        request = s.corrected_request(request, reactions)
        liquid = eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)
        problem = eq.Problem(T=temperature, P=pressure, feed=eq.Amounts(dict(zip(s.COMPONENT_IDS, request['reaction_system']['feed_amounts_mol'], strict=True))), phases=[liquid], reactions=reference_problem.reactions, neutral_reference=reference_problem.neutral_reference)
        endpoints.append(problem)
        for boundary in (False, True):
            state_problem = eq.Problem(T=temperature, P=eq.Free(), feed=problem.feed, phases=[liquid, eq.Phase('V', kind='vapor', support=s.COMPONENT_IDS[:3], amount=eq.Pinned(0))], reactions=problem.reactions, neutral_reference=problem.neutral_reference) if boundary else problem
            state = eq.solve_equilibrium(model, state_problem)
            record = s._snapshot_from_result(model, state_problem, request, state)
            check = f.check_state(record, {'request': request})
            checks.append({'loading': loading, 'boundary': boundary, 'state': record, 'check': check, 'pressure': list(state.pressure)})
            f.save(case_path, {'row': row, 'checks': checks})
            assert check['complete'], check
            if loading == 0:
                amounts = [math.fsum(state.amounts[j]*state.mole_fractions[len(s.COMPONENT_IDS)*j+i] for j in range(state.phase_count)) for i in range(len(s.COMPONENT_IDS))]
                assert all(amounts[s.COMPONENT_IDS.index(i)] == 0 for i in carbon_species)
            if boundary:
                assert pressure > state.pressure[0]*(1+1e-7), 'phase boundary unavailable'
    initial, final = endpoints
    item = reg.addition_enthalpy(parameters, initial, final, {'carbon-dioxide': 1.}, alpha, temperature, pressure, phase='vapor', observed=row['observed_addition_enthalpy_J_per_mol_CO2'], form='difference', scale=row['uH_J_per_mol_CO2'])
    prediction = reg.predict(model, item)
    output = {'row': row, 'checks': checks, 'value': prediction.value, 'residual': prediction.residual, 'status': prediction.status.name, 'tolerance_met': prediction.requested_tolerance_met, 'message': prediction.message}
    feed_parameters = epcsaft.Parameters.from_mapping(mapping, components=['carbon-dioxide'])
    calorics = thermal.record()
    feed_record = epcsaft.ThermochemistryRecord(calorics.standard_pressure, [calorics.component_intervals[s.COMPONENT_IDS.index('carbon-dioxide')]])
    feed = epcsaft.Pure(feed_parameters, thermochemistry=feed_record).state(temperature, P=pressure, phase='vapor')
    output['feed'] = {key: s._jsonable(getattr(feed, key)) for key in ('stable_root_count', 'molar_density', 'pressure_density_derivative', 'total_enthalpy')}
    f.save(case_path, output)
    assert prediction.status.name == 'Available' and prediction.requested_tolerance_met is not False
    assert math.isfinite(prediction.value) and math.isfinite(prediction.residual)
    assert feed.stable_root_count == 1 and feed.molar_density > 0 and feed.pressure_density_derivative > 0 and math.isfinite(feed.total_enthalpy)
    return output
```

## assessment-independent-heat-and-loading.txt

```python
def independent_heat(selected):
    report = {}
    required = [r for r in arcis_rows if r['role_147'] == 'required_independent_heat_comparison']
    assert len(required) == 14
    for branch, chosen in selected.items():
        mapping = s.parameter_mapping(HERE / chosen['parameters_path'])
        values, limits = [], []
        for row in required:
            assert row['alpha_final']+row['u_alpha'] < row['saturation']-row['u_saturation']
            values.append(run_case(branch, row, mapping))
        for row in mathonat_required:
            estimates, refinements = [], []
            for pressure in (2e6, 5e6, 10e6):
                increments = []
                for epsilon in (1e-3, 5e-4, 2.5e-4):
                    case = {**row, 'system_pressure_Pa': pressure, 'alpha_final': epsilon}
                    increments.append(run_case(branch, case, mapping)['value'])
                difference = abs(increments[-1]-increments[-2])/1000
                refinements.append({'pressure': pressure, 'increments': increments, 'difference_kJ_mol': difference})
                assert difference <= .1, refinements[-1]
                estimates.append(increments[-1])
            mean = math.fsum(estimates)/3
            limits.append({'row': row, 'value': mean, 'pressure_values': estimates, 'pressure_spread_J_mol': max(estimates)-min(estimates), 'refinements': refinements, 'residual': (mean-row['observed_addition_enthalpy_J_per_mol_CO2'])/row['uH_J_per_mol_CO2']})
        groups = {}
        for pressure in (510000, 1030000):
            rows = [r for r in values if r['row']['system_pressure_Pa'] == pressure]
            residuals = [r['residual'] for r in rows]
            groups[str(pressure)] = {'n': len(rows), 'rms': math.sqrt(math.fsum(v*v for v in residuals)/len(rows)), 'mean': math.fsum(residuals)/len(rows)}
        residuals = [r['residual'] for r in values+limits]
        report[branch] = {'Arcis': values, 'Mathonat': limits, 'groups': groups, 'aggregate_rms': math.sqrt(math.fsum(v*v for v in residuals)/16)}
        f.save(HERE / 'assessment-independent-heat.json', report)
    report['improvement_pass'] = report['heat']['aggregate_rms'] <= report['no-heat']['aggregate_rms']
    f.save(HERE / 'assessment-independent-heat.json', report)
    return report


def loading_sensitivity(selected):
    rows = []
    for branch, chosen in selected.items():
        mapping = s.parameter_mapping(HERE / chosen['parameters_path'])
        for row in vinjarapu_rows:
            uncertainty = row['loading_uncertainty_mol_CO2_per_mol_MEA']
            predictions = [run_case(branch, {**row, 'alpha_final': row['alpha_final']+sign*uncertainty}, mapping) for sign in (-1, 1)]
            rows.append({'branch': branch, 'row': row, 'values': predictions})
            f.save(HERE / 'assessment-loading-sensitivity.json', rows)
    return rows
```

## assessment-limits.txt

```python
def assessment_limits(selected, training, pressure80, independent, identification):
    report = {}
    for branch, chosen in selected.items():
        scored = training[branch]
        heat = [r for r in scored['rows'] if target_family[r['target']] == 'heat']
        residuals = [r['residual'] for r in heat]
        groups = {alpha: [r['residual'] for r in heat if heat_by_id[r['target']]['alpha_final'] == alpha] for alpha in (.11, .22, .33, .45)}
        errors = [(r['value']-heat_by_id[r['target']]['observed_addition_enthalpy_J_per_mol_CO2'])/1000 for r in heat]
        report[branch] = {
            'pressure_cost': scored['cost_by_family']['pressure'], 'pressure_preservation': scored['cost_by_family']['pressure'] <= 9.077053756257484, 'species_cost': scored['cost_by_family']['species'],
            'species_preservation': scored['cost_by_family']['species'] <= 27.33328854377677, 'Vinjarapu_rms': math.sqrt(math.fsum(v*v for v in residuals)/8), 'loading_means': {alpha: math.fsum(values)/len(values) for alpha, values in groups.items()},
            'heat_RMSE_kJ_mol': math.sqrt(math.fsum(v*v for v in errors)/8), 'heat_bias_kJ_mol': math.fsum(errors)/8,
        }
        report[branch]['Vinjarapu_pass'] = report[branch]['Vinjarapu_rms'] <= 2 and all(abs(mean) <= 2 for mean in report[branch]['loading_means'].values())
        report[branch]['Arcis_pass'] = all(group['rms'] <= 2 and abs(group['mean']) <= 2 for group in independent[branch]['groups'].values())
        report[branch]['Mathonat_pass'] = all(abs(row['residual']) <= 2 for row in independent[branch]['Mathonat'])
        report[branch]['pressure80'] = pressure80[branch]
        report[branch]['pressure80_pass'] = pressure80[branch]['rows'] == 21 and pressure80[branch]['complete'] and pressure80[branch]['aard_percent'] <= 20.270257
        report[branch]['identification'] = identification[branch]
        mapping = s.parameter_mapping(HERE / chosen['parameters_path'])
        values = s.parameter_values(mapping)
        pairs = {identity: [values[identity]+values.get(identity+'/reciprocal_temperature_slope', 0.)*(1/temperature-1/313.15) for temperature in assessment_temperatures] for identity in values if identity.endswith('/k_ij')}
        report[branch]['effective_interactions'] = pairs
        report[branch]['effective_interactions_pass'] = all(value < 1 for temperatures in pairs.values() for value in temperatures)
    report['independent_improvement_pass'] = independent['improvement_pass']
    report['primary_minus_control'] = {key: pressure80['heat'][key]-pressure80['no-heat'][key] for key in ('aard_percent', 'rms_ln', 'mean_ln')}
    f.save(HERE / 'assessment-limits.json', report)
    return report
```

## assessment-pressure-species-wagner.txt

```python
def assess_states(group, observations, selected):
    output = HERE / f'assessment-{group}.json'
    assert not output.exists(), 'single ordered assessment'
    deadline = time.perf_counter() + 1790
    rows, checks = [], []
    for branch, chosen in selected.items():
        mapping = s.parameter_mapping(HERE / chosen['parameters_path'])
        model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=thermal.record())
        s.RUNS = BUNDLE / 'results/runs/temperature-heat-147' / f'{branch}-{group}'
        for o in observations:
            result = s.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=175, limits=s.EvaluationLimits(175, 1790, deadline), model_fingerprint=s.parameter_fingerprint(mapping))
            check = f.check_state(result, o)
            checks.append({'branch': branch, 'identity': o['identity'], 'check': check})
            liquid = next((phase for phase in result.get('phases', []) if phase['role'] == 'liquid'), None)
            for target in o['targets']:
                value = f.compare.predicted({**result, 'liquid': liquid}, target) if check['complete'] else None
                pressure = target['prediction_identity'] == 'co2-partial-pressure'
                logarithm = math.log(value/target['observed']) if value is not None and value > 0 else None
                residual = logarithm/.3 if pressure and logarithm is not None else (value-target['observed'])/(.1*target['observed']+.001) if value is not None else None
                rows.append({
                    'branch': branch, 'group': group, 'identity': o['identity'],
                    'target': target['identity'], 'source': target['source_identity'], 'temperature_k': o['request']['temperature']['value'],
                    'loading': result.get('loading'), 'predicted': value, 'observed': target['observed'],
                    'quantity': 'pressure' if pressure else 'species', 'ln_pred_over_obs': logarithm, 'relative_error': value/target['observed']-1 if value is not None else None,
                    'scaled_residual': residual, 'numerically_complete': check['complete'] and value is not None,
                })
            f.save(output, {'rows': rows, 'checks': checks})
            assert check['complete'], (o['identity'], check)
    grouped = {}
    for branch in selected:
        subset = [r for r in rows if r['branch'] == branch]
        grouped[branch] = assessment.metrics(subset)
        for source, temperature in {(r['source'], r['temperature_k']) for r in subset}:
            grouped[branch][f'{source}/{temperature}'] = assessment.metrics([r for r in subset if r['source'] == source and r['temperature_k'] == temperature])
        if group == 'canonical-80C-21':
            grouped[branch]['canonical-80C-19'] = assessment.metrics([r for r in subset if r['identity'].removeprefix('canonical:') in assessment_rows['secondary_80c_pressure_19']])
    f.save(output, {'rows': rows, 'checks': checks, 'metrics': grouped})
    return grouped
```

## assessment-source-units.txt

```python
def convert_source_units(row):
    result = dict(row)
    result['temperature_K'] = float(row['temperature_K'])
    if row['record_id'].startswith('mathonat'):
        result.update(source_key='Mathonat1998', observed_addition_enthalpy_J_per_mol_CO2=-1000*float(row['minus_DeltaHabs_kJ_per_mol_CO2_reported']), uH_J_per_mol_CO2=1000*float(row['sigma_kJ_per_mol_CO2_reported']))
    else:
        for key in ('alpha_initial', 'alpha_final', 'system_pressure_Pa', 'observed_addition_enthalpy_J_per_mol_CO2'):
            result[key] = float(row[key])
        result.update(source_key=row['repository_source_key'], uH_J_per_mol_CO2=float(row['heat_residual_scale_J_per_mol_CO2']))
        result.update(u_alpha=float(row['loading_uncertainty_mol_per_mol_MEA']), saturation=float(row['source_saturation_loading']), u_saturation=float(row['source_saturation_uncertainty']))
    assert result['uH_J_per_mol_CO2'] > 0 and math.isfinite(result['observed_addition_enthalpy_J_per_mol_CO2'])
    return result
```

## bounded-jobs.txt

```python
def run_case(branch, row, mapping):
    name = f"{branch}-{row['record_id']}-{row['temperature_K']}-{row['system_pressure_Pa']}-{row['alpha_final']}".replace('/', '_')
    case_path = HERE / 'assessment-cases' / f'{name}.json'
    request_path = case_path.with_suffix('.input.json')
    f.save(request_path, {'row': row, 'mapping': mapping, 'output': str(case_path)})
    completed = subprocess.run(['timeout', '-k', '5s', '175s', 'uv', 'run', '--no-project', '--active', 'python', str(Path(__file__)), 'heat-case', str(request_path)], capture_output=True, text=True, timeout=180)
    f.save(case_path.with_suffix('.process.json'), {'returncode': completed.returncode, 'output': completed.stdout, 'error': completed.stderr})
    assert completed.returncode == 0, name
    return json.loads(case_path.read_text())

# Each F1-F8 invocation uses agent-heavy --max 2G --timeout 2400s --wait 180 with all three numerical thread variables set to 1.
# Each E1-E8 uses 1650s, each A1-A6 uses 1800s; child deadlines consume the parent deadline, not renewed budgets.
if command == 'fit' and (branch, form, start) != only:
    continue
```

## common-assessment-bindings.txt

```python
spec = importlib.util.spec_from_file_location('assessment_140', HERE.parent.with_name('temperature-reanchor-140') / 'assessment.py')
assessment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assessment)
freeze = json.loads((HERE / 'freeze.json').read_text())
assert subprocess.run(['git', 'cat-file', '-e', 'HEAD:'+str((HERE / 'freeze.json').relative_to(BUNDLE.parents[1]))]).returncode == 0
for path, sha256 in freeze['hashes'].items():
    assert s.sha256(BUNDLE.parents[1] / path) == sha256
native = json.loads((HERE.parent / 'campaign-reactions.json').read_text())
s._engine_reaction_records = lambda request, values: assessment.engine_records(native, 353.15)
assessment_rows = json.loads(assessment_ids.read_text())
canonical = f.probe.pressure_observations(lambda row: row['observation_id'] in assessment_rows['primary_80c_pressure'])
wanted = {row['target'] for row in assessment_rows['packet_80c_species']}
species = [{**o, 'targets': [target for target in o['targets'] if target['identity'] in wanted]} for o in f.probe.OBSERVATIONS if any(target['identity'] in wanted for target in o['targets'])]
wagner = assessment.wagner(f, wagner_subset)
assert len(canonical) == 21 and len(wagner) == 11
arcis_rows = [convert_source_units(row) for row in csv.DictReader(arcis_path.open())]
mathonat_required = [convert_source_units(row) for row in csv.DictReader(mathonat_path.open()) if float(row['temperature_K']) in (313.15, 353.15)]
vinjarapu_rows = [row for row in json.loads((HERE.parent / 'heat-source-admission.json').read_text())['Vinjarapu2024']['rows'] if row['role_147'] == 'heat_calibration']
heat_by_id = {row['record_id']: row for row in vinjarapu_rows}
reference_problem = s._problem_from_request(s.corrected_request(observations[0]['request'], reactions))
carbon_species = ('carbon-dioxide', 'carbamate-anion', 'bicarbonate-anion', 'carbonate-anion')
assessment_temperatures = {o['request']['temperature']['value'] for o in observations+canonical+species+wagner} | {313.15, 322.5, 353.15}
assert all(temperature <= 353.15 for temperature in assessment_temperatures)
notebook_sha256 = s.sha256(BUNDLE / 'notebook.qmd')
adopted_sha256 = s.sha256(BUNDLE / 'results/selected-current-best-parameters.json')
```

## common-fit-bindings.txt

```python
import numpy as np
import copy
import csv
import subprocess
import timing
f, s, eq, reg, epcsaft, thermal = timing.f, timing.s, timing.eq, timing.reg, timing.epcsaft, timing.thermal
mapping, reactions, params, observations = timing.mapping, timing.reactions, timing.params, timing.observations
retained = json.loads((HERE / 'timing.json').read_text())
assert len(retained['branches']['no-heat']) == 141 and len(retained['branches']['heat']) == 149
rows, heat_rows, state_checks = timing.setup(retained)
retained_states = {r['identity']: r['state'] for r in state_checks}
expected = list(csv.DictReader((BUNDLE / 'results/source-corrections-152/accepted-wave/strict141-targets.csv').open()))
assert {(r['identity'], r['target']) for r in expected} == {(o['identity'], t['identity']) for o in observations for t in o['targets']}
target_family = {target['identity']: 'pressure' if target['prediction_identity'] == 'co2-partial-pressure' else 'species' for o in observations for target in o['targets']}
target_family.update({identity: 'heat' for identity, _, _ in heat_rows})
fit_names = [f'{branch}-{form}-start-{start}' for branch in ('no-heat', 'heat') for form in ('constant-fixed', 'slope-fixed') for start in ('1', '2')]
fits = {(branch, form, start): json.loads((HERE / f'{branch}-{form}-start-{start}-fit.json').read_text()) for branch in ('no-heat', 'heat') for form in ('constant-fixed', 'slope-fixed') for start in ('1', '2')} if command == 'select' else {}
selected = {}
assert all(math.isfinite(value) for fit in fits.values() for value in fit['physical']+fit['predictions']+fit['weighted_residuals']+fit['optimizer_jacobian'])
assert all(len(fit['predictions']) == len(fit['weighted_residuals']) == (149 if name.startswith('heat-') else 141) for name, fit in fits.items())
```

## common-input-paths-and-dispatch.txt

```python
ROOT = BUNDLE.parents[1]
assessment_ids = HERE.parent.with_name('temperature-reanchor-140') / 'assessment-row-ids.json'
arcis_path = ROOT / 'data/reference/MEA/observations/calorimetry/Arcis_2011_calorimetry_30wt.csv'
mathonat_path = ROOT / 'data/reference/MEA/observations/calorimetry/Mathonat_1998_low_loading_heat.csv'
prior_access = json.loads((HERE.parent / 'inputs.json').read_text())
wagner_subset = next(row['subset'] for row in csv.DictReader((assessment_ids.parent / 'never-accessed-vle-admission.csv').open()) if '80' in row['subset'] and row['admitted'] == 'yes')
assert len(rows) == 141 and len(heat_rows) == 8
if command == 'fit':
    only = tuple(sys.argv[2:5])
    assert only[0] in ('no-heat', 'heat') and only[1] in ('constant-fixed', 'slope-fixed') and only[2] in ('1', '2')
    assert not (HERE / f"{'-'.join(only)}-fit.json").exists()
if command == 'heat-case':
    request = json.loads(Path(sys.argv[2]).read_text())
    case_path = Path(request['output'])
    heat_value(request['row'], request['mapping'])
```

## export-reload-rescore.txt

```python
def rescore(name, fit):
    ids = fit['coordinates']
    final = s.with_parameter_values(mapping, dict(zip(ids, fit['physical'], strict=True)))
    final['purpose'] = 'Issue 147 conditional temperature comparison; not adopted.'
    path = HERE / f'{name}-parameters.json'
    f.save(path, final)
    reloaded = json.loads(path.read_text())
    assert s.reaction_values(reloaded) == reactions
    parameters = epcsaft.Parameters.from_mapping(reloaded)
    fitted_model = epcsaft.Mixture(parameters, thermochemistry=thermal.record())
    s.RUNS = BUNDLE / 'results/runs/temperature-heat-147' / name / 'rescore'
    assert not s.RUNS.exists(), 'one rescore, fresh cache'
    deadline = time.perf_counter() + 1645
    rows, checks = [], []
    for o in observations:
        anchor = s.anchor_from(retained_states[o['identity']])
        state = s.evaluate_state(fitted_model, o['request'], reactions, o['identity'], [anchor], budget_s=175, limits=s.EvaluationLimits(175, 1645, deadline), model_fingerprint=s.parameter_fingerprint(reloaded))
        check = f.check_state(state, o)
        checks.append({'identity': o['identity'], 'state': state, 'check': check})
        f.save(HERE / f'{name}-rescore.json', {'checks': checks, 'rows': rows})
        assert check['complete'], (o['identity'], check)
        problem = s._problem_from_request(s.corrected_request(o['request'], reactions), s.anchor_from(state))
        rows.extend(f.refit.observations(parameters, o, problem, 60))
    assert len(checks) == 83 and len(rows) == 141
    scored = []
    for identity, item, weight in rows + heat_rows:
        prediction = reg.predict(fitted_model, item)
        scored.append({'target': identity, 'value': prediction.value, 'residual': math.sqrt(weight)*prediction.residual, 'status': prediction.status.name, 'tolerance_met': prediction.requested_tolerance_met, 'message': prediction.message})
        f.save(HERE / f'{name}-rescore.json', {'checks': checks, 'rows': scored})
        assert prediction.status.name == 'Available' and prediction.requested_tolerance_met is not False, identity
        assert math.isfinite(prediction.value) and math.isfinite(prediction.residual), identity
    objective = scored if name.startswith('heat-') else scored[:141]
    assert len(scored) == 149 and len(objective) == len(fit['weighted_residuals'])
    costs = {family: math.fsum(.5*r['residual']**2 for r in scored if target_family[r['target']] == family) for family in ('pressure', 'species', 'heat')}
    result = {'rows': scored, 'checks': checks, 'cost_by_family': costs, 'native_cost_difference': math.fsum(.5*r['residual']**2 for r in objective)-fit['final_cost'], 'parameter_sha256': s.sha256(path)}
    f.save(HERE / f'{name}-rescore.json', result)
    fit.update(complete=True, rescore=result, parameters_path=path.name, parameter_sha256=s.sha256(path))
    f.save(HERE / f'{name}-fit.json', fit)
    return result
```

## fit-selection.txt

```python
for branch, items in (("no-heat", rows), ("heat", rows + heat_rows)):
    for form in ("constant-fixed", "slope-fixed"):
        for start in ("1", "2"):
            ids, bounds, scales, values = f.design(form, start)
            coordinates = []
            for identity, bound, scale, value in zip(ids, bounds, scales, values, strict=True):
                family = "k_ij_reciprocal_temperature_slope" if identity == f.SLOPE else "k_ij"
                coordinates.append(reg.coordinate(params, [(family, tuple(identity.split("/")[1:3]), 1.0)], origin=value, scale=scale, bounds=bound))
            controls = reg.FitControls()
            controls.maximum_iterations = 40
            controls.maximum_elapsed_time_seconds = 2250
            result = reg.fit(params, coordinates, [item for _, item, _ in items], weights=[weight for _, _, weight in items], controls=controls, thermochemistry=thermal.record())
            name = f"{branch}-{form}-start-{start}"
            fields = ("status", "message", "usable", "physical", "predictions", "weighted_residuals", "optimizer_jacobian", "final_cost", "iterations", "residual_evaluations", "jacobian_evaluations", "trial_failures", "iteration_costs", "iteration_seconds")
            record = {field: s._jsonable(getattr(result, field)) for field in fields}
            record["observation_statuses"] = [status.name for status in result.statuses]
            record["active_bounds"] = [ids[index] for index in result.covariance.active_bounds]
            record["coordinates"] = ids
            f.save(HERE / f"{name}-fit.json", record)
            assert result.status == "converged" and result.usable, name
            assert all(status.name == "Available" for status in result.statuses), name
            fits[branch, form, start] = record

assert len(fits) == 8, "incomplete menu cannot be selected"
for branch in ("no-heat", "heat"):
    representatives = {}
    for form in ("constant-fixed", "slope-fixed"):
        first = fits[branch, form, "1"]
        second = fits[branch, form, "2"]
        relative_cost = abs(first["final_cost"] - second["final_cost"]) / max(abs(first["final_cost"]), abs(second["final_cost"]))
        differences = [abs(a - b) for a, b in zip(first["physical"], second["physical"], strict=True)]
        assert relative_cost <= 1e-6 and max(differences[:4]) <= 1e-5, (branch, form)
        assert form == "constant-fixed" or differences[4] <= 0.1, (branch, form)
        representatives[form] = first if relative_cost <= 1e-6 or first["final_cost"] < second["final_cost"] else second
    minimum = min(fit["final_cost"] for fit in representatives.values())
    form = "constant-fixed" if representatives["constant-fixed"]["final_cost"] <= 1.01 * minimum else "slope-fixed"
    selected[branch] = representatives[form]
```

## freeze.txt

```python
def freeze(selected):
    assert len(fits) == 8 and all(fit['complete'] for fit in fits.values())
    assert set(selected) == {'no-heat', 'heat'}
    assert not (HERE / 'freeze.json').exists()
    assert not list(HERE.glob('assessment-*.json'))
    wagner = BUNDLE.parents[1] / 'data/reference/MEA/observations/vapor_liquid_equilibrium/Wagner_2013_VLE.csv'
    sources = [training, f.SOURCE, HERE.parent / 'campaign-reactions.json', HERE.parent / 'heat-source-admission.json', HERE.parent / 'source-law-admission.json', HERE.parent / 'inputs.json', thermal.PHYSICAL_CALORICS, wagner, assessment_ids]
    producers = [Path(__file__), Path(timing.__file__), Path(s.__file__), Path(f.__file__), Path(f.refit.__file__), Path(assessment.__file__)]
    outcomes = [HERE / f'{name}-{suffix}.json' for name in fit_names for suffix in ('fit', 'rescore', 'parameters', 'identification')]
    hashes = {str(path.relative_to(BUNDLE.parents[1])): s.sha256(path) for path in sources+producers+outcomes}
    record = {'selected': selected, 'heat_primary': selected['heat'], 'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'module_origin': epcsaft.__file__, 'hashes': hashes, 'prior_access': prior_access, 'assessment_ids': assessment_rows, 'limits': limits, 'not_evaluated': ['vle_obs_0286', 'vle_obs_0287', 'vle_obs_0288']}
    f.save(HERE / 'freeze.json', record)
    assert s.sha256(BUNDLE / 'results/selected-current-best-parameters.json') == adopted_sha256
    assert s.sha256(BUNDLE / 'notebook.qmd') == notebook_sha256
    return record
```

## identification.txt

```python
def identification(fit):
    columns = len(fit['coordinates'])
    jacobian = np.asarray(fit['optimizer_jacobian']).reshape(len(fit['weighted_residuals']), columns)
    assert np.isfinite(jacobian).all(), 'unavailable optimizer Jacobian'
    norms = np.linalg.norm(jacobian, axis=0)
    assert np.all(norms > 0), 'unavailable zero Jacobian column'
    normalized = jacobian / norms
    singular = np.linalg.svd(normalized, compute_uv=False)
    correlations = normalized.T @ normalized
    rank_warning = singular[-1] / singular[0] < 1e-8
    correlation_warning = np.max(np.abs(correlations-np.eye(columns))) >= .95
    result = {'column_norms': norms.tolist(), 'singular_values': singular.tolist(), 'singular_value_ratio': singular[-1]/singular[0], 'uncentered_correlations': correlations.tolist(), 'rank_warning': bool(rank_warning), 'correlation_warning': bool(correlation_warning), 'active_bounds': fit['active_bounds']}
    result['pass'] = not rank_warning and not correlation_warning
    if columns == 5:
        intercepts = normalized[:, :4]
        q, values, _ = np.linalg.svd(intercepts, full_matrices=False)
        rank = np.count_nonzero(values > 1e-8*values[0])
        q = q[:, :rank]
        slope = jacobian[:, 4]
        projected = slope-q @ (q.T @ slope)
        eta = np.linalg.norm(projected)/np.linalg.norm(slope)
        interior = -1000 < fit['physical'][4] < 1000
        result.update(intercept_rank=int(rank), eta=float(eta), slope_interior=interior)
        result['pass'] = result['pass'] and rank == 4 and interior and eta > math.sqrt(1-.95**2)
    return result
```

## shared-setup-proposed-timing.txt

```python
"""Issue 147 corrected campaign presolve and complete residual/Jacobian timing; no fit."""
import importlib.util
import json
import math
import os
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[2]
sys.path[:0] = [str(BUNDLE.parents[1] / 'src'), str(BUNDLE / 'scripts'), str(BUNDLE / 'calibration-misfit')]
import shared_evaluation as s
s.ENGINE_WHEEL_SHA256 = 'e8ad39e0c5d7da471a6d3ace6ff62d60518c57bc1c96fe5198d8bf18747ba8b5'
s.ENGINE_COMMIT = 'c106702048e87d0c583a3a5516cb5746e7a6ac07'
s.verify_wheel()
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
import verify_reference_calorics as thermal
spec = importlib.util.spec_from_file_location('low_temperature_fit', HERE.parent.with_name('temperature-reanchor-140') / 'low-temperature-fit.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
f.NATIVE_INPUTS = HERE.parent / 'campaign-reactions.json'
mapping, reactions, original = f.source_context()
params = epcsaft.Parameters.from_mapping(s.with_parameter_values(mapping, dict.fromkeys(f.IDS + [f.SLOPE], 0.0)))
model = epcsaft.Mixture(params, thermochemistry=thermal.record())
chart = reg.CoordinateSet()
chart.coordinates = [reg.coordinate(params, [('k_ij_reciprocal_temperature_slope' if i == f.SLOPE else 'k_ij', tuple(i.split('/')[1:3]), 1.0)], origin=0.0, scale=h, bounds=b) for i, b, h, _ in zip(*f.design('slope-fixed', '1'), strict=True)]
active_model = epcsaft.Mixture(params, thermochemistry=thermal.record(), active_parameters=chart.active())
training = BUNDLE / 'results/final-rerun/training-inputs.json'
assert s.sha256(training) == 'a063148a1c3c68765adbfca81e17d32cd327c68b035e19c84ebeb007f76bb369'
observations = json.loads(training.read_text())
def setup(retained=None):
    rows, checks = [], []
    anchors = {r['identity']: r['state'] for r in retained['checks']} if retained else None
    for o in observations:
        assert o['request']['temperature']['value'] <= 333.15
        if anchors is None:
            s.RUNS = BUNDLE / 'results/runs/temperature-heat-147/timing' / o['identity']
            rec = s.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=175, limits=s.EvaluationLimits(175, 175), model_fingerprint=s.parameter_fingerprint(mapping))
        else:
            rec = anchors[o['identity']]
        check = f.check_state(rec, o)
        checks.append({'identity': o['identity'], 'state': rec, 'check': check})
        assert check['complete'], (o['identity'], check)
        problem = s._problem_from_request(s.corrected_request(o['request'], reactions), s.anchor_from(rec))
        rows.extend(f.refit.observations(params, o, problem, 60))
    assert len(observations) == 83 and len(rows) == 141
    heat = [r for r in json.loads((HERE.parent / 'heat-source-admission.json').read_text())['Vinjarapu2024']['rows'] if r['role_147'] == 'heat_calibration']
    assert len(heat) == 8
    solvent = {'monoethanolamine': 1.0, 'water': 7.911062165006594}
    template = s._problem_from_request(s.corrected_request(observations[0]['request'], reactions))
    heat_rows = []
    for r in heat:
        endpoints = [eq.Problem(T=313.15, P=1734000.0, feed=eq.Amounts({**solvent, 'carbon-dioxide': a}), phases=[eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)], reactions=template.reactions, neutral_reference=template.neutral_reference) for a in (0.0, r['alpha_final'])]
        heat_rows.append((r['record_id'], reg.addition_enthalpy(params, *endpoints, {'carbon-dioxide': 1.0}, r['alpha_final'], 313.15, 1734000.0, phase='vapor', observed=r['observed_addition_enthalpy_J_per_mol_CO2'], form='difference', scale=r['uH_J_per_mol_CO2']), 1.0))
    assert len(heat_rows) == 8
    return rows, heat_rows, checks


if __name__ == '__main__':
    record = {'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'module_origin': epcsaft.__file__, 'checks': [], 'branches': {}, 'pool_size_available': len(os.sched_getaffinity(0))}
    clock = time.perf_counter()
    try:
        for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
            assert os.environ[variable] == '1'
        rows, heat_rows, record['checks'] = setup()
        for branch, items in (('no-heat', rows), ('heat', rows + heat_rows)):
            values = []
            for identity, item, weight in items:
                t = time.perf_counter()
                p = reg.predict(model, item)
                residual_s = time.perf_counter() - t
                record['current_prediction'] = {'target': identity, **{k: s._jsonable(getattr(p, k)) for k in ('value', 'status', 'message', 'residual', 'requested_tolerance_met', 'convergence', 'branch', 'stable_root_count')}}
                f.save(HERE / 'timing.json', record)
                assert p.status.name == 'Available' and p.requested_tolerance_met is not False, (identity, p.message)
                t = time.perf_counter()
                g = reg.differentiate(active_model, item)
                values.append({'target': identity, 'prediction': p.value, 'weighted_residual': math.sqrt(weight)*p.residual, 'gradient': list(g.value), 'status': g.status.name, 'message': g.message, 'residual_s': residual_s, 'jacobian_s': time.perf_counter()-t})
                record['branches'][branch] = values
                f.save(HERE / 'timing.json', record)
                assert g.status.name == 'Available' and len(g.value) == 5 and all(math.isfinite(v) for v in g.value), (identity, g.message)
                print('timing', branch, identity, flush=True)
    except Exception as error:
        record['failure'] = {'exception': type(error).__name__, 'message': str(error)}
        raise
    finally:
        record.update(wall_s=time.perf_counter()-clock, maximum_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        f.save(HERE / 'timing.json', record)
```

## shared-setup.diff.txt

```diff
--- current timing.py

+++ proposed shared timing setup

@@ -31,50 +31,60 @@

 training = BUNDLE / 'results/final-rerun/training-inputs.json'
 assert s.sha256(training) == 'a063148a1c3c68765adbfca81e17d32cd327c68b035e19c84ebeb007f76bb369'
 observations = json.loads(training.read_text())
-rows = []
-record = {'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'module_origin': epcsaft.__file__, 'checks': [], 'branches': {}, 'pool_size_available': len(os.sched_getaffinity(0))}
-clock = time.perf_counter()
-try:
-    for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
-        assert os.environ[variable] == '1'
+def setup(retained=None):
+    rows, checks = [], []
+    anchors = {r['identity']: r['state'] for r in retained['checks']} if retained else None
     for o in observations:
         assert o['request']['temperature']['value'] <= 333.15
-        s.RUNS = BUNDLE / 'results/runs/temperature-heat-147/timing' / o['identity']
-        rec = s.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=175, limits=s.EvaluationLimits(175, 175), model_fingerprint=s.parameter_fingerprint(mapping))
+        if anchors is None:
+            s.RUNS = BUNDLE / 'results/runs/temperature-heat-147/timing' / o['identity']
+            rec = s.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=175, limits=s.EvaluationLimits(175, 175), model_fingerprint=s.parameter_fingerprint(mapping))
+        else:
+            rec = anchors[o['identity']]
         check = f.check_state(rec, o)
-        record['checks'].append({'identity': o['identity'], 'state': rec, 'check': check})
-        f.save(HERE / 'timing.json', record)
+        checks.append({'identity': o['identity'], 'state': rec, 'check': check})
         assert check['complete'], (o['identity'], check)
         problem = s._problem_from_request(s.corrected_request(o['request'], reactions), s.anchor_from(rec))
         rows.extend(f.refit.observations(params, o, problem, 60))
-        print('presolve', o['identity'], flush=True)
     assert len(observations) == 83 and len(rows) == 141
-    heat = [r for r in json.loads((HERE.parent / 'heat-source-admission.json').read_text())['Vinjarapu2024']['rows'] if r['role_147'] == 'calibration']
+    heat = [r for r in json.loads((HERE.parent / 'heat-source-admission.json').read_text())['Vinjarapu2024']['rows'] if r['role_147'] == 'heat_calibration']
+    assert len(heat) == 8
     solvent = {'monoethanolamine': 1.0, 'water': 7.911062165006594}
     template = s._problem_from_request(s.corrected_request(observations[0]['request'], reactions))
     heat_rows = []
     for r in heat:
         endpoints = [eq.Problem(T=313.15, P=1734000.0, feed=eq.Amounts({**solvent, 'carbon-dioxide': a}), phases=[eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)], reactions=template.reactions, neutral_reference=template.neutral_reference) for a in (0.0, r['alpha_final'])]
         heat_rows.append((r['record_id'], reg.addition_enthalpy(params, *endpoints, {'carbon-dioxide': 1.0}, r['alpha_final'], 313.15, 1734000.0, phase='vapor', observed=r['observed_addition_enthalpy_J_per_mol_CO2'], form='difference', scale=r['uH_J_per_mol_CO2']), 1.0))
-    for branch, items in (('no-heat', rows), ('heat', rows + heat_rows)):
-        values = []
-        for identity, item, weight in items:
-            t = time.perf_counter()
-            p = reg.predict(model, item)
-            residual_s = time.perf_counter() - t
-            record['current_prediction'] = {'target': identity, **{k: s._jsonable(getattr(p, k)) for k in ('value', 'status', 'message', 'residual', 'requested_tolerance_met', 'convergence', 'branch', 'stable_root_count')}}
-            f.save(HERE / 'timing.json', record)
-            assert p.status.name == 'Available' and p.requested_tolerance_met is not False, (identity, p.message)
-            t = time.perf_counter()
-            g = reg.differentiate(active_model, item)
-            values.append({'target': identity, 'prediction': p.value, 'weighted_residual': math.sqrt(weight)*p.residual, 'gradient': list(g.value), 'status': g.status.name, 'message': g.message, 'residual_s': residual_s, 'jacobian_s': time.perf_counter()-t})
-            record['branches'][branch] = values
-            f.save(HERE / 'timing.json', record)
-            assert g.status.name == 'Available' and len(g.value) == 5 and all(math.isfinite(v) for v in g.value), (identity, g.message)
-            print('timing', branch, identity, flush=True)
-except Exception as error:
-    record['failure'] = {'exception': type(error).__name__, 'message': str(error)}
-    raise
-finally:
-    record.update(wall_s=time.perf_counter()-clock, maximum_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
-    f.save(HERE / 'timing.json', record)
+    assert len(heat_rows) == 8
+    return rows, heat_rows, checks
+
+
+if __name__ == '__main__':
+    record = {'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'module_origin': epcsaft.__file__, 'checks': [], 'branches': {}, 'pool_size_available': len(os.sched_getaffinity(0))}
+    clock = time.perf_counter()
+    try:
+        for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
+            assert os.environ[variable] == '1'
+        rows, heat_rows, record['checks'] = setup()
+        for branch, items in (('no-heat', rows), ('heat', rows + heat_rows)):
+            values = []
+            for identity, item, weight in items:
+                t = time.perf_counter()
+                p = reg.predict(model, item)
+                residual_s = time.perf_counter() - t
+                record['current_prediction'] = {'target': identity, **{k: s._jsonable(getattr(p, k)) for k in ('value', 'status', 'message', 'residual', 'requested_tolerance_met', 'convergence', 'branch', 'stable_root_count')}}
+                f.save(HERE / 'timing.json', record)
+                assert p.status.name == 'Available' and p.requested_tolerance_met is not False, (identity, p.message)
+                t = time.perf_counter()
+                g = reg.differentiate(active_model, item)
+                values.append({'target': identity, 'prediction': p.value, 'weighted_residual': math.sqrt(weight)*p.residual, 'gradient': list(g.value), 'status': g.status.name, 'message': g.message, 'residual_s': residual_s, 'jacobian_s': time.perf_counter()-t})
+                record['branches'][branch] = values
+                f.save(HERE / 'timing.json', record)
+                assert g.status.name == 'Available' and len(g.value) == 5 and all(math.isfinite(v) for v in g.value), (identity, g.message)
+                print('timing', branch, identity, flush=True)
+    except Exception as error:
+        record['failure'] = {'exception': type(error).__name__, 'message': str(error)}
+        raise
+    finally:
+        record.update(wall_s=time.perf_counter()-clock, maximum_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
+        f.save(HERE / 'timing.json', record)
```
