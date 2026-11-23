"""Replay the fitted MEA observations with one Born diameter changed at a time.

From the repository root, with the pinned wheel installed:
    agent-heavy uv run --no-sync python analyses/mea_parameter_bundle/scripts/born_diameter_sensitivity.py
"""
import csv
import json
import math

import stable_refit_255 as replay

s = replay.s
RESULTS = replay.B / 'results'
REFERENCE = RESULTS / 'paper-evidence-341'
RUN = RESULTS / 'runs/born-diameter-sensitivity'
RECORD = RESULTS / 'reduced-refit/F2/previous/parameters.json'
RECORD_SHA = 'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed'
IONS = ('bicarbonate-anion', 'carbonate-anion')
JOU = 'vle_obs_0202-pco2'


def group_key(record):
    # Same cost groups as paper_evidence_341.weights, including the exact scales.
    args = record['arguments']
    quantity = record['constructor'] if record['constructor'] == 'addition_enthalpy' else record['kind']
    return (record['group'], quantity, str(args.get('species')),
            float(args.get('scale', record['row'].get('scale', 1))), record['weight'])


def state(spec, record):
    states = {}
    for key in ('problem', 'initial', 'final'):
        if key in record:
            problem = spec.problems[record[key]]
            states[key] = {
                'identity': record[key],
                'temperature_K': None if isinstance(problem.T, replay.eq.Free) else problem.T,
                'pressure_Pa': None if isinstance(problem.P, replay.eq.Free) else problem.P,
                'feed': problem.feed.values,
                'feed_basis': type(problem.feed).__name__,
            }
    return states


def change(base, current, spec, declaration):
    old, new = base['value'], current['value']
    return dict(identity=base['identity'], observed=base['observed'], unit=current['unit'],
                baseline=old, perturbed=new, change=new-old,
                change_percent=100*(new-old)/abs(old) if old else None,
                state=state(spec, declaration))


def stability(spec, grid_state):
    results = []
    for scale in replay.STAGES:
        item = replay.stability_row(spec, grid_state, scale)
        prediction = replay.reg.predict(spec.model, item)
        measured = replay.stability_payload(prediction)
        assert measured['available'] and measured['completed'] and prediction.status.name == 'Available', measured
        tau = measured['value']
        residual = prediction.residual
        assert math.isclose(residual, tau/scale, rel_tol=1e-12, abs_tol=1e-15), measured
        bubble_pressure = measured.pop('pressure_Pa')
        results.append(dict(measured, scale=scale, residual=residual,
                            penalty_cost=0.5 * residual**2, bubble_pressure_Pa=bubble_pressure,
                            parent_pressure_Pa=bubble_pressure * grid_state['c']))
    return results


def main():
    s.verify_wheel()
    assert replay.epcsaft.__version__ == '1.3.1'
    assert s.sha256(RECORD) == RECORD_SHA
    mapping = s.parameter_mapping(RECORD)
    parameters = s.parameter_values(mapping)
    fixed = {ion: f'component/{ion}/born_diameter' for ion in IONS}
    assert all(parameters[key] == 3.0 for key in fixed.values())

    spec = replay.bind(mapping)
    declarations = spec.inputs['observations']['fitted']
    historical = replay.read(REFERENCE / 'objective-declarations.json')
    # The current loader adds unit and basis metadata to the historical declarations.
    compared = [{k: v for k, v in row.items() if k not in ('basis', 'unit')} for row in declarations]
    assert json.loads(json.dumps(compared)) == historical
    by_group = {}
    by_quantity = {}
    for index, record in enumerate(declarations):
        key = group_key(record)
        by_group.setdefault(key, []).append(index)
        by_quantity.setdefault(key[:3], []).append(index)
    ids = [record['identity'] for record in declarations]
    assert len(set(ids)) == len(ids) == 307
    _, offsets = replay.states()
    grid_state = next(row for row in offsets if (row['wt'], row['T'], row['a']) == (.3, 338.15, .5875))

    with (REFERENCE / 'objective-groups.csv').open(newline='') as stream:
        groups = list(csv.DictReader(stream))
    group_keys = [(g['group'], g['quantity'], g['species'], float(g['scale']), float(g['weight'])) for g in groups]
    assert len(group_keys) == len(by_group) and set(group_keys) == set(by_group)
    reference_path = REFERENCE / 'candidate/replay.json'
    reference = replay.read(reference_path)
    cases = [(None, 3.)] + [(ion, diameter) for ion in IONS for diameter in (2.5, 4.)]
    report = dict(parameter_sha256=RECORD_SHA, engine_version=replay.epcsaft.__version__,
                  engine_commit=s.ENGINE_COMMIT, wheel_sha256=s.ENGINE_WHEEL_SHA256,
                  stability_state=grid_state, stability_weight=1., cases=[])
    group_costs = []
    RUN.mkdir(parents=True, exist_ok=True)

    for ion, diameter in cases:
        varied = mapping if ion is None else s.with_parameter_values(mapping, {fixed[ion]: diameter})
        values, available, cost = replay.replay(varied)
        assert [row['identity'] for row in values] == ids
        replay.d.check(values)
        assert available
        name = 'baseline' if ion is None else f'{ion}-{diameter:g}'
        case = dict(ion=ion, diameter_A=diameter, rows=len(values), cost=cost)
        if ion is None:
            base, base_cost = values, cost
            assert [row['identity'] for row in reference['rows']] == ids
            relative_errors = [abs(x['value']-y['value']) / max(abs(x['value']), abs(y['value']), 1e-300)
                               for x, y in zip(base, reference['rows'], strict=True)]
            worst = max(range(len(ids)), key=relative_errors.__getitem__)
            report.update(reference_replay_sha256=s.sha256(reference_path),
                          reference_cost=reference['cost'], baseline_cost_difference=cost-reference['cost'],
                          baseline_max_relative_prediction_difference=relative_errors[worst],
                          baseline_max_difference_identity=ids[worst])
            assert relative_errors[worst] <= 1e-10 and math.isclose(cost, reference['cost'], rel_tol=1e-10)
        else:
            case['largest_absolute_changes'] = []
            for (group, quantity, species), indices in by_quantity.items():
                peak = max(indices, key=lambda i: abs(values[i]['value']-base[i]['value']))
                case['largest_absolute_changes'].append(dict(group=group, quantity=quantity, species=species,
                                                            **change(base[peak], values[peak], spec, declarations[peak])))
            jou = ids.index(JOU)
            case['jou_pressure'] = change(base[jou], values[jou], spec, declarations[jou])

        case['cost_change'] = cost - base_cost
        for group, key in zip(groups, group_keys, strict=True):
            indices = by_group[key]
            assert len(indices) == int(group['n'])
            subtotal = math.fsum(values[i]['cost'] for i in indices)
            baseline = math.fsum(base[i]['cost'] for i in indices)
            assert math.isclose(baseline, float(group['cost']), rel_tol=1e-10, abs_tol=1e-12)
            group_costs.append(dict(case=name, **{k: v for k, v in group.items() if k not in ('cost', 'cost_percent', 'rule')},
                                    baseline_cost=baseline, cost=subtotal, cost_change=subtotal-baseline))
        assert math.isclose(math.fsum(row['cost_change'] for row in group_costs[-len(groups):]),
                            case['cost_change'], abs_tol=1e-12)
        case['stability'] = stability(spec if ion is None else replay.bind(varied), grid_state)
        report['cases'].append(case)
        s.write_json(RUN / 'summary.json', report)
        print(name, 'cost', cost, 'change', case['cost_change'], flush=True)

    with (RUN / 'objective-group-costs.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=group_costs[0], lineterminator='\n')
        writer.writeheader()
        writer.writerows(group_costs)


if __name__ == '__main__':
    main()
