"""#427 Stage 0: verify the MDEA–water slope bound and record start availability."""
from argparse import ArgumentParser
from collections import Counter
from itertools import product
from math import fsum
from time import monotonic

from census import record
from starts import Starts, refit
from part_ii import SHA
from calculations import MDEAWeights

M, r = refit.MDEA, refit.r

DESIGN = 'MDEA_slope_bound'
OUT = refit.OUT / DESIGN
INCUMBENT = refit.OUT / 'MDEA/A.json.gz'
KNOWN_GAP = refit.OUT / 'MDEA/LHS-53.json.gz'
COLD = 288.71
REPLAY_TOLERANCE = 1e-10  # #427 same-wheel readback of A
A0, A1 = (f'{M.PAIR}/a{i} / temperature_law_coefficient' for i in range(2))
RECORDS = ('declaration.json.gz', 'replay-A.json.gz', 'onset-S.json', 'hull-S.json', 'census-S.json.gz')


def box(route):
    bound = route.config['k_bound']
    curve = route.load(bound['critical'])
    reference, margin = bound['temperature_K'], bound['margin']
    top = next(q['k_no_gap'] for q in curve['rows'] if q['T_K'] == reference)
    slope = max((top-q['k_no_gap'])/(reference-q['T_K']) for q in curve['rows'] if q['T_K'] < reference)
    point = r.read(INCUMBENT)['endpoint']
    coordinates = {q['identity']: q for q in point['coordinates']}
    assert coordinates[A0]['bounds'][1] == top-margin
    coordinates[A1]['bounds'][0] = slope
    return dict(wheel=route.wheel_sha256, engine_commit=route.wheel.parent.name.removeprefix('main-'), design=DESIGN,
                point=point, reference_temperature_K=reference, U=top-margin, s_per_K=slope, margin=margin,
                critical_sha256=bound['critical']['sha256'], pressure_Pa=curve['pressure_Pa'],
                retained_temperatures_K=[q['T_K'] for q in curve['rows']], compositions=len(M.FINE),
                seed=refit.SEED, draws=64, reaction_reference_pressure_Pa=refit.P_REF)


def hulls(declaration):
    point = declaration['point']
    bounds = {q['identity']: q['bounds'] for q in point['coordinates']}
    temperatures = [COLD, *declaration['retained_temperatures_K']]
    cases = []
    for a0, a1 in product(bounds[A0], bounds[A1]):
        mapping = r.s.with_parameter_values(point['parameters'], {f'{M.PAIR}/a0': a0, f'{M.PAIR}/a1': a1})
        cases.append(('corner', mapping, temperatures))
    cases.append(('LHS-53', r.read(KNOWN_GAP)['endpoint']['parameters'], [COLD]))
    rows = []
    tick = monotonic()
    for case, mapping, temperatures in cases:
        model = M.binary_model(mapping)
        terms = {q['power']: q['coefficient']['value']['magnitude'] for q in M.law(mapping)['terms']}
        for T in temperatures:
            unavailable, gaps = M.binary_gaps(model, 'methyldiethanolamine', T, declaration['pressure_Pa'], M.FINE)
            rows.append(dict(case=case, a0=terms[0], a1=terms[1], T_K=T, k=M.k_at(mapping, T),
                             unavailable=unavailable, gaps=gaps))
    return dict(wheel=declaration['wheel'], rows=rows, seconds=monotonic()-tick)


def relative_max(new, old):
    if not old or new.keys() != old.keys():
        return None
    if any(value == 0 and new[key] != 0 for key, value in old.items()):
        return None
    return max(abs(new[key]-value)/abs(value) if value else 0. for key, value in old.items())


def replay_checks(result):
    incumbent = r.read(INCUMBENT)
    replay, diagnostics = result['replay'], result['diagnostics']
    rows, old_rows = replay['rows'], incumbent['replay']['rows']
    comparable = len(rows) == len(old_rows) == 281 and all(
        q['identity'] == old['identity'] and q['status'] == old['status'] == 'Available'
        and q['requested_tolerance_met'] and 'cost' in q for q, old in zip(rows, old_rows)
    )
    error = relative_max({q['identity']: q['value'] for q in rows},
                         {q['identity']: q['value'] for q in old_rows}) if comparable else None
    se_error = relative_max(diagnostics.get('uncertainty', {}).get('conditional_standard_error', {}),
                            incumbent['diagnostics']['uncertainty']['conditional_standard_error'])
    cost = fsum(q['cost'] for q in rows) if comparable else None
    old_cost = incumbent['replay']['cost']
    active = diagnostics.get('active_bounds')
    return dict(passed=error is not None and max(error, abs(cost/old_cost-1)) <= REPLAY_TOLERANCE
                and cost == replay['cost'] and active == {A0: 'upper'}
                and se_error is not None and se_error <= REPLAY_TOLERANCE,
                rows=len(rows), unavailable=sum('cost' not in q for q in rows), cost=cost,
                retained_cost=old_cost, max_relative_prediction_difference=error, active_bounds=active,
                max_relative_conditional_se_difference=se_error, replay_seconds=result['replay_seconds'],
                diagnostic_seconds=result['diagnostic_seconds'])


def onset_check(declaration, result):
    previous = {q['T_K']: q['k_no_gap'] for q in r.read(M.RESULTS/'critical-k.json')['rows']}
    rows = {q['T_K']: q for q in result['rows']}
    errors = {str(T): abs(rows[T]['k_no_gap']-previous[T]) for T in (290, 423) if T in rows}
    k = declaration['U'] + declaration['s_per_K']*(COLD-declaration['reference_temperature_K'])
    margin = rows[COLD]['k_no_gap']-k if COLD in rows else None
    return dict(passed=len(errors) == 2 and max(errors.values()) <= M.RESOLUTION and margin is not None
                and margin >= declaration['margin'] and format(declaration['s_per_K'], '.7g') == '0.0005507469'
                and all(0 < q['k_gap']-q['k_no_gap'] <= M.RESOLUTION for q in rows.values()),
                cold_onset=rows.get(COLD), corner_k=k, corner_margin=margin, reference_errors=errors,
                s_per_K=declaration['s_per_K'], U=declaration['U'], seconds=result['seconds'])


def hull_check(declaration, result):
    corners = [q for q in result['rows'] if q['case'] == 'corner']
    known = next(q for q in result['rows'] if q['case'] == 'LHS-53')
    gap_count = sum(bool(q['gaps']) for q in corners)
    unavailable = sum(bool(q['unavailable']) for q in corners)
    bounds = {q['identity']: q['bounds'] for q in declaration['point']['coordinates']}
    expected = set(product(bounds[A0], bounds[A1], [COLD, *declaration['retained_temperatures_K']]))
    states = [(q['a0'], q['a1'], q['T_K']) for q in corners]
    return dict(passed=len(states) == len(expected) and set(states) == expected and not (gap_count or unavailable)
                and known['T_K'] == COLD and not known['unavailable'] and bool(known['gaps']),
                corner_states=len(corners), gaps=gap_count, unavailable=unavailable, known_answer=known,
                seconds=result['seconds'])


def census_check(declaration, result):
    rows = [(q['identity'], q['group']) for q in r.read(INCUMBENT)['replay']['rows']]
    coordinates = declaration['point']['coordinates']
    lower, upper = (refit.np.array([q['bounds'][i] for q in coordinates]) for i in (0, 1))
    unit = refit.qmc.LatinHypercube(d=len(coordinates), seed=declaration['seed']).random(declaration['draws'])
    vectors = (lower + (upper-lower)*unit).tolist()
    records = result['records']
    complete = [q['draw'] for q in records] == list(range(len(vectors))) and all(
        q['vector'] == vector and [(x['identity'], x['group']) for x in q['rows']] == rows
        for q, vector in zip(records, vectors)
    )
    missing = Counter((q['group'], q['status'], q['message'])
                      for candidate in records for q in candidate['rows'] if q['status'] != 'Available')
    by_family = Counter()
    for (group, _, _), count in missing.items():
        by_family[group] += count
    return dict(passed=complete and not (by_family['Kim'] + by_family['Kuranov-binary']),
                candidates=len(records), can_start=sum(all(q['status'] == 'Available' for q in x['rows']) for x in records),
                available_rows=sum(len(q['rows']) for q in records)-missing.total(), unavailable_rows=missing.total(),
                by_family=dict(by_family), by_message=[dict(family=g, status=s, message=m, rows=n)
                                                       for (g, s, m), n in sorted(missing.items())],
                workers=result['workers'], seconds=result['wall_seconds'])


def reduce():
    # Recompute from retained observations and binary checks; no Engine rows are solved here.
    declaration = r.read(OUT/RECORDS[0])
    result = dict(wheel=declaration['wheel'], checks={}, record_fingerprints={})
    checks = result['checks']
    for index, (name, readback) in enumerate(zip(RECORDS, (
        lambda q: dict(passed=q['wheel'] == SHA, engine_commit=q['engine_commit']),
        replay_checks, lambda q: onset_check(declaration, q), lambda q: hull_check(declaration, q),
        lambda q: census_check(declaration, q),
    ), strict=True), 1):
        path = OUT/name
        if not path.exists():
            break
        evidence = r.read(path)
        check = readback(evidence)
        check['passed'] = check['passed'] and evidence['wheel'] == SHA
        checks[str(index)] = check
        result['record_fingerprints'][name] = refit.fingerprint(evidence)
        if not check['passed']:
            break
    return result


def require(number):
    summary = reduce()
    refit.save(OUT/'checks.json.gz', summary)
    check = summary['checks'].get(str(number), {})
    if not check.get('passed'):
        raise SystemExit(f'Stage 0 stopped at check {number}. See {OUT}/checks.json.gz')
    print(f'Stage 0 check {number} passed', flush=True)


def verify():
    rebuilt, retained = reduce(), r.read(OUT/'checks.json.gz')
    if rebuilt != retained:
        raise SystemExit('Stage 0 retained checks differ from the records')
    checks = rebuilt['checks']
    if sorted(checks) != ['1', '2', '3', '4', '5'] or not all(q['passed'] for q in checks.values()):
        raise SystemExit(f'Stage 0 retained checks reproduced, but not every check passed. See {OUT}/checks.json.gz')
    print('Stage 0 retained checks reproduced')


def run():
    refit.a.study.reuse.bind_wheel()
    try:
        route = MDEAWeights(M.DECLARATION, refit.WORK/DESIGN/SHA, fixed_reference_pressure_pa=refit.P_REF)
    except (AssertionError, OSError) as error:
        refit.save(OUT/'wheel-refusal.json', dict(expected_wheel=SHA, error=f'{type(error).__name__}: {error}'))
        raise SystemExit(f'Stage 0 stopped at check 1. See {OUT}/wheel-refusal.json') from error

    declaration = box(route)
    refit.save(OUT/RECORDS[0], declaration)
    require(1)

    point = declaration['point']
    bound = route.bind(point)
    tick = monotonic()
    replay = refit.replay(bound)
    replay_seconds = monotonic()-tick
    replay_record = dict(wheel=route.wheel_sha256, replay=replay, replay_seconds=replay_seconds,
                         convergence_source=str(INCUMBENT.relative_to(refit.OUT)))
    refit.save(OUT/RECORDS[1], replay_record)
    tick = monotonic()
    diagnostics = refit.endpoint_diagnostics(bound, replay, point, r.read(INCUMBENT)['controls'])
    refit.save(OUT/RECORDS[1], dict(replay_record, diagnostics=diagnostics, diagnostic_seconds=monotonic()-tick))
    require(2)

    tick = monotonic()
    onset = dict(wheel=route.wheel_sha256, rows=[])
    try:
        for T in (290., 423., COLD):
            onset['rows'].extend(M.critical(point['parameters'], [T], declaration['pressure_Pa']))
    except AssertionError as error:
        onset['refusal'] = dict(T_K=T, message=str(error))
    finally:
        refit.save(OUT/RECORDS[2], dict(onset, seconds=monotonic()-tick))
    require(3)

    refit.save(OUT/RECORDS[3], hulls(declaration))
    require(4)

    record(Starts(route, point), OUT/RECORDS[4])
    require(5)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Recompute checks from retained records without writing')
    verify() if parser.parse_args().check else run()
