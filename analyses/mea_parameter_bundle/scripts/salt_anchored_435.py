"""Issue #435 salt cascade and MEA refit on the pinned study wheel."""
# ruff: noqa: E402 -- reuse the transfer and MEA analysis owners.
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
from time import monotonic

ANALYSES = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ANALYSES), str(ANALYSES / 'mdea_mea_workflow/scripts')]

import shared_ion_electrostatics_423 as study

f, r, salt = study.f, study.r, study.salt
BASE = study.BASE
OUT = BASE.parent / 'salt-anchored-435'
REGISTRY = 'f7f02b1ef565690efb466dd6d3d73bc9c74c708116725b2b0d931486cdc1b666'
MEA_LIMIT_S = 35 * 60


def setup():
    assert 1 <= int(os.environ['AGENT_HEAVY_CORES']) <= 4
    study.reuse.bind_wheel()
    r.verify()
    f.OUT = r.OUT = OUT
    assert r.s.sha256(study.RECORD) == study.bands.RECORD_SHA


def timed(call, *args, **kwargs):
    started = monotonic()
    result = call(*args, **kwargs)
    return result, monotonic() - started


def probe():
    # F4 has both salt laws and the MEAH–bicarbonate coordinate.
    path = BASE / 'F4/parameters.json'
    mapping = r.s.parameter_mapping(path)
    spec, bind_seconds = timed(r.bind, mapping)
    bank = r.read(BASE / 'split-registry.json')['trials']
    assert len(bank) == 6121 and hashlib.sha256(json.dumps(bank, sort_keys=True).encode()).hexdigest() == REGISTRY
    main, offset = r.states()
    memory = r.read(BASE / 'split-trials.json')
    excluded = r.read(BASE.parent / 'stable-refit-255/qualification/summary.json')['result']['excluded']
    sampled_main = [x for i, x in enumerate(main) if i // 2 % 19 == 0 or x['key'] in excluded]
    sampled_offset = offset[::13]
    grid, grid_seconds = timed(r.grid, mapping, sampled_main + sampled_offset, memory, capture=True)
    f.write('probe/grid.json.gz', grid)
    # These fractions sample all census temperatures, loadings and pressure
    # brackets, with the historical state 38 explicitly included.
    indices = sorted(set(range(0, 162, 7)) | {38})
    native, native_seconds = timed(r.census, mapping, 'probe/native', indices=indices, keep_refusals=True)
    supplied, census_seconds = timed(r.census, mapping, 'probe/supplied', dict.fromkeys(map(str, indices), bank),
                                    indices=indices, keep_refusals=True, compact_supplied=True)
    native_parents = r.result('probe/native/census-raw.json.gz')
    supplied_parents = r.result('probe/supplied/census-raw.json.gz')
    parents_match = all(x.get('final', {}).get('coordinates') == y.get('final', {}).get('coordinates')
                        for x, y in zip(native_parents, supplied_parents, strict=True))
    bubble_seconds = 0.
    bubbles = []
    for state, row in zip(sampled_main + sampled_offset, grid, strict=True):
        item = r.stability_row(spec, state, 1.)
        bubble, seconds = timed(r.eq.solve_equilibrium, spec.model, item.pressure_reference)
        bubble_seconds += seconds
        bubbles.append(dict(key=state['key'], seconds=seconds, pressure_Pa=bubble.pressure,
                            regression_pressure_Pa=row.get('pressure_Pa'), message=bubble.message,
                            requested_tolerance_met=bubble.requested_tolerance_met))
    f.write('probe/bubbles.json', bubbles)
    fit_report = r.read(BASE / 'F4/current/unpenalized/declaration.json')
    spec.inputs['coordinates'] = [dict(q, origin=r.s.parameter_values(mapping)[q['identity']])
                                  for q in fit_report['declared']]
    import uncertainty_307
    derivative, derivative_seconds = timed(uncertainty_307.derivative, spec, spec.inputs['observations']['fitted'])
    grid_work = sum(x['seconds'] for x in grid)
    full_grid_work = sum(x['seconds'] for x in grid[:len(sampled_main)]) * len(main) / len(sampled_main)
    full_grid_work += sum(x['seconds'] for x in grid[len(sampled_main):]) * len(offset) / len(sampled_offset)
    # Use observed pool occupancy, including per-launch binding and serialization.
    full_grid = grid_seconds * full_grid_work / grid_work
    full_census = census_seconds * 162 / len(indices)
    full_search = full_grid + full_census
    # #430 bounds the two complete fits. Include separate final replay overhead.
    projected = 2 * full_search + 134 + 2 * bind_seconds + derivative_seconds
    summary = dict(parameter_sha256=r.s.sha256(path), wheel_sha256=r.SHA, registry_sha256=REGISTRY, workers=r.CORES,
                   sampled_main=len(sampled_main), sampled_offset=len(sampled_offset), census_indices=indices,
                   grid_wall_s=grid_seconds, grid_worker_s=grid_work, bubble_only_serial_s=bubble_seconds,
                   bind_serial_s=bind_seconds, fit_derivative_serial_s=derivative_seconds,
                   fit_derivative_statuses=[x.name for x in derivative.statuses],
                   native_census_wall_s=native_seconds, census_with_bank_wall_s=census_seconds,
                   supplied_increment_wall_s=census_seconds-native_seconds,
                   parents_match=parents_match, native=native, census_with_bank=supplied,
                   grid=r.tally(grid), projected_grid_s=full_grid, projected_census_s=full_census,
                   projected_search_s=full_search, projected_MEA_s=projected, limit_s=MEA_LIMIT_S,
                   released=parents_match and projected <= MEA_LIMIT_S)
    f.write('probe/timing.json', summary)
    print({k: v for k, v in summary.items() if k != 'fit_derivative_statuses'}, flush=True)


def salt_rows(document):
    parameters = r.epcsaft.Parameters.from_mapping(document)
    return {'NaCl': salt.predict(document, salt.nacl_rows(parameters)),
            **{name: salt.predict(document, salt.carbonate_rows(parameters, {name}))
               for name in ('NaHCO3', 'Na2CO3', 'mixed')}}


def salt_checks(rows, reference):
    checks = {}
    identity = ('salt', 'T', 'm', 'observed', 'status', 'unavailable')
    for name, values in rows.items():
        pairs = list(zip(values, reference[name], strict=True))
        assert all(all(x.get(k) == y.get(k) for k in identity) for x, y in pairs)
        maximum = max(f.a.relative(x['value'], y['value']) for x, y in pairs if x.get('status') == 'Available')
        checks[name] = dict(maximum_relative_prediction_difference=maximum,
                            relative_aard_difference=f.a.relative(salt.aard(values)['aard_percent'],
                                                                 salt.aard(reference[name])['aard_percent']))
    return checks


def calibrate():
    started = monotonic()
    fingerprints = {'hamer-wu-1972-nacl.csv': '0c434d900f9a9db8b745852765533ab692e5baecffb62a2812b8fe1455221b4c',
                    'peiper-pitzer-1982-table6.csv': '1e683e4eb7405fd5a0fb32e336309efc70ba17811e9d2b9c97e960a0985ccc29'}
    assert all(r.s.sha256(salt.INPUTS / name) == digest for name, digest in fingerprints.items())
    historical = r.read(salt.OUT / 'salt/summary.json')['result']
    coefficients = {ion: (law['a0'], law['a1']) for ion, law in historical['laws'].items()}
    control = salt.salt_document(coefficients)
    old_rows, replay_seconds = timed(salt_rows, control)
    old_checks = salt_checks(old_rows, historical['rows'])
    study_control = r.read(study.OUT / 'controls.json')['salt_rows']
    same_wheel = salt_checks({k: old_rows[k] for k in study_control}, study_control)
    passed = all(c['relative_aard_difference'] <= 1e-8 for c in old_checks.values())
    passed &= all(c['maximum_relative_prediction_difference'] <= 1e-10 for c in same_wheel.values())
    new_control = salt.salt_document(coefficients, study.RECORD)
    new_rows, new_replay_seconds = timed(salt_rows, new_control)
    f.write('salt/control.json', dict(wheel_sha256=r.SHA, fingerprints=fingerprints,
                                     historical_declaration=control, old_rows=old_rows, cross_wheel=old_checks,
                                     same_wheel=same_wheel, passed=passed, f2_declaration=new_control,
                                     f2_rows=new_rows, f2_change=salt_checks(new_rows, old_rows),
                                     seconds=replay_seconds, f2_replay_seconds=new_replay_seconds))
    assert passed, 'Salt replay did not reproduce the retained calibration'
    record, cascade_seconds = timed(salt.salt, base=study.RECORD, out=OUT)
    _, scan_seconds = timed(salt.scan, base=study.RECORD)
    values = r.s.parameter_values(record['document'])
    law_checks = []
    for ion, law in record['laws_at_record_reference'].items():
        identity = salt.LAWS[ion]
        original = record['laws'][ion]
        assert (values[identity + '/a0'], values[identity + '/a1']) == (original['a0'], original['a1'])
        for T in (278.15, 288.15, 298.15, 308.15, 313.15, 318.15):
            a, b = salt.law_value(original, T), salt.law_value(law, T)
            law_checks.append(dict(ion=ion, T_K=T, k_original=a, k_rebased=b, dk_dT_K_inverse=law['a1'],
                                   passed=law['a1'] == original['a1'] and abs(a-b) <= 2 * math.ulp(1.)))
    def bias(rows):
        scored = [x['relative_error'] for x in rows if x.get('relative_error') is not None]
        return 100 * math.fsum(scored) / len(scored) if scored else None
    signed = {name: {T: bias([x for x in rows if x['T'] == T]) for T in sorted({x['T'] for x in rows})}
              for name, rows in record['rows'].items()}
    f.write('salt/verification.json', dict(law_checks=law_checks, signed_percent_bias_by_temperature=signed,
                                          cascade_seconds=cascade_seconds, scan_seconds=scan_seconds,
                                          elapsed_s=monotonic()-started))
    assert all(row['passed'] for row in law_checks)


def mea_start(label):
    source = study.RECORD if label == 'F2' else BASE / 'F4/parameters.json'
    mapping = r.s.parameter_mapping(source)
    salt_record = r.result('salt/summary.json')
    assert salt_record['gates']['F1_passed']
    provenance = dict(source_id='issue-435', locator='salt-anchored-435/salt/summary.json')
    for ion in (salt.HCO3, salt.CO3):
        law = salt_record['laws_at_record_reference'][ion]
        salt.set_pair(mapping, ion, salt.W, salt.law_node(salt.LAWS[ion], law['a0'], law['a1'], law['t_ref'], provenance))
    if salt.MEAH_HCO3 not in r.s.parameter_values(mapping):
        salt.set_pair(mapping, salt.HCO3, salt.MEAH, salt.k_node(mapping, salt.MEAH_HCO3, 0., provenance))
    _, fitted, ties = study.reuse.f2_starts()
    fitted.remove(salt.LAWS[salt.HCO3])
    fitted.append(dict(identity=salt.MEAH_HCO3, family='k_ij', target=[salt.HCO3, salt.MEAH], scale=.01, bounds=[-1., 1.]))
    return mapping, fitted, ties


def mea_fit(label):
    mapping, fitted, ties = mea_start(label)
    name = f'MEA/{label}'
    f.write(f'{name}/start.json', mapping)
    endpoint, report = f.fit(name, mapping, f.LITERATURE, fitted, ties)
    control = r.read(OUT / 'MEA/F2-control/replay.json')
    summary = dict(status=report['status'] if report else 'unavailable', cost=None)
    if endpoint is not None:
        replay = r.read(OUT / name / 'replay.json')
        rvalues, baseline = replay['rows'], control['rows']
        assert [(x['identity'], x['group'], x['row']) for x in rvalues] == [(x['identity'], x['group'], x['row']) for x in baseline]
        metrics = r.metrics(rvalues)
        active = report['covariance']['active_bounds'] if report.get('covariance') else None
        values, old = map(r.s.parameter_values, (endpoint, r.s.parameter_mapping(study.RECORD)))
        assert all(values[q] == values[q.replace('segment_diameter', 'born_diameter')] for q in ties)
        f.write(f'{name}/parameters.json', endpoint)
        summary.update(cost=replay['cost'], delta_cost=replay['cost']-control['cost'], metrics=metrics,
                       acceptance=r.acceptance(metrics, r.metrics(baseline)), active_bounds=active,
                       coordinates=[dict(identity=q['identity'], value=values[q['identity']], F2=old.get(q['identity']),
                                         bounds=q['bounds']) for q in report['declared']])
    f.write(f'{name}/fit-summary.json', summary)


def mea_search(label):
    name = f'MEA/{label}'
    mapping = r.s.parameter_mapping(OUT / name / 'parameters.json')
    search = study.reuse.mea_search(label, mapping, None, output=OUT / name)
    search['parameter_sha256'] = r.s.sha256(OUT / name / 'parameters.json')
    search['stable'] = all(search[g]['descent'] == 0 and not search[g]['unavailable'] for g in ('grid', 'offset'))
    search['stable'] &= search['census']['descent'] == search['census']['incomplete'] == search['missing_supplied'] == 0
    f.write(f'{name}/search-summary.json', search)


def bounded(stage, label, projection, remaining):
    name = f'MEA/{label}/{stage}-timing.json'
    started = monotonic()
    if projection > remaining:
        f.write(name, dict(projection_s=projection, remaining_s=remaining, status='stopped before launch'))
        return False
    duration = min(2 * projection, remaining)
    with subprocess.Popen([sys.executable, '-u', __file__, stage, label], start_new_session=True) as child:
        try:
            status = child.wait(timeout=duration)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            child.wait()
            status = 'wall limit'
    f.write(name, dict(projection_s=projection, limit_s=duration, elapsed_s=monotonic()-started, status=status))
    return status == 0


def mea():
    timing = r.read(OUT / 'probe/timing.json')
    assert timing['released'] and timing['workers'] == r.CORES == 4
    started = monotonic()
    rows, ok, cost = r.replay(r.s.parameter_mapping(study.RECORD))
    reference = r.read(study.reuse.paper.OUT / 'candidate/replay.json')
    study.reuse.compare_rows(rows, reference['rows'], ('identity', 'group', 'status', 'observed', 'row'), 1e-10)
    assert ok and len(rows) == 307 and f.a.relative(cost, reference['cost']) <= 1e-10
    residual_difference = max(abs(x['weighted_residual']-y['weighted_residual']) for x, y in zip(rows, reference['rows'], strict=True))
    assert residual_difference <= 1e-10
    f.write('MEA/F2-control/replay.json', dict(rows=rows, cost=cost, maximum_weighted_residual_difference=residual_difference))
    pending = ['F2', 'F4']
    completed = []
    search_projection = timing['projected_search_s']
    for label in pending:
        if not bounded('fit', label, 67, MEA_LIMIT_S - (monotonic()-started) - len(pending)*search_projection):
            continue
        if (OUT / f'MEA/{label}/parameters.json').is_file():
            completed.append(label)
    searches = {}
    for index, label in enumerate(completed):
        path = OUT / f'MEA/{label}/parameters.json'
        fingerprint = r.s.parameter_fingerprint(r.s.parameter_mapping(path))
        if fingerprint in searches:
            f.write(f'MEA/{label}/search-summary.json', dict(searches[fingerprint], alias_exact_declaration=True))
            continue
        remaining = MEA_LIMIT_S - (monotonic()-started) - (len(completed)-index-1)*search_projection
        if bounded('search', label, search_projection, remaining):
            searches[fingerprint] = r.read(OUT / f'MEA/{label}/search-summary.json')
            search_projection = max(search_projection, searches[fingerprint]['seconds'])
    candidates = []
    for label in completed:
        name = f'MEA/{label}'
        path = OUT / name / 'search-summary.json'
        summary = r.read(OUT / name / 'fit-summary.json')
        if path.is_file() and r.read(path)['stable'] and summary['status'] == 'converged' and all(
                check['passed'] for check in summary['acceptance'].values()):
            candidates.append(dict(summary, label=label))
    chosen = f.lowest_cost(candidates)
    if chosen:
        tolerance = r.read(r.A6)['controls']['function_tolerance']
        chosen['tied_starts'] = [c['label'] for c in candidates if f.costs_tied(c['cost'], chosen['cost'], tolerance)]
    f.write('MEA/selection.json', dict(chosen=chosen, fit_endpoints=completed, elapsed_s=monotonic()-started,
                                      projected_s=timing['projected_MEA_s'], limit_s=MEA_LIMIT_S))


def assess():
    from part_ii import np
    import objective_weights_420 as weights
    import reference_states_428
    import uncertainty_307

    chosen = r.read(OUT / 'MEA/selection.json')['chosen']
    assert chosen is not None
    label = chosen['label']
    name = f'MEA/{label}'
    path = OUT / name / 'parameters.json'
    mapping = r.s.parameter_mapping(path)
    report = r.read(OUT / name / 'declaration.json')
    started = monotonic()
    f.information(name, mapping, report['declared'])
    info = r.read(OUT / name / 'information.json')
    spec = r.bind(mapping)
    replay = r.read(OUT / name / 'replay.json')['rows']
    coordinates = info['coordinates']
    weighted_jacobian = np.asarray(info['weighted_physical_jacobian']) * np.array([q['scale'] for q in coordinates])
    residual = np.array([x['weighted_residual'] for x in replay])
    audit, contributions = weights.information_reduction('MEA', spec.inputs['observations']['fitted'], replay,
                                                         coordinates, residual, weighted_jacobian, info, r.COMMIT)
    r.write(f'{name}/objective-information.json.gz', audit)
    f.table(f'{name}/objective-contributions.csv', contributions)
    summary, rows = salt.pool_and_shares(mapping)
    f.write(f'{name}/pools.json', dict(summary=summary, rows=rows))
    f.write(f'{name}/reference-state.json', reference_states_428.mea(path))
    f.write(f'{name}/assessment-timing.json', dict(elapsed_s=monotonic()-started))
    f.OUT, f.a.OUT = OUT / 'MEA', study.reuse.paper.OUT
    started = monotonic()
    f.evidence(label, path)
    f.scores(label, mapping)
    f.write(f'{label}/property-evidence-timing.json', dict(elapsed_s=monotonic()-started))
    def bound(_):
        fresh = r.bind(mapping)
        fresh.parameter_sha256 = r.s.sha256(path)
        fresh.inputs['coordinates'] = r.read(OUT / name / 'information.json')['coordinates']
        return fresh, fresh.inputs['coordinates'], OUT / name / 'uncertainty'
    uncertainty_307.setup = bound
    uncertainty_307.main('MEA')


if __name__ == '__main__':
    setup()
    {'probe': probe, 'salt': calibrate, 'mea': mea, 'fit': mea_fit,
     'search': mea_search, 'assess': assess}[sys.argv[1]](*sys.argv[2:])
