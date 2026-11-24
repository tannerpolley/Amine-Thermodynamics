"""Evaluate the fixed-parameter DEA and AMP carbamate-hydrolysis variants of #426."""
import copy
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path
from subprocess import check_output
from tempfile import TemporaryDirectory
from time import monotonic

from part_ii import ROOT, SHA, SHARED, WHEEL, Route, deviation_statistics, epcsaft, jsonable
sys.path[:0] = [str(ROOT / "analyses" / f"{amine}_transfer") for amine in ("amp", "dea")]
from amp_transfer.probe_412 import law, ln_k
from dea_transfer.reactive import A0, B0
from dea_transfer.rerun import LIMIT, digest, read
from MEA.common.analysis_io import write_csv_rows, write_json_file

R, TP = epcsaft.GAS_CONSTANT_J_PER_MOL_K, 313.15
R4 = 'carbamate-hydrolysis'
DEA_SHA = '529153f0a1262b6848471f69967112e3559d03c921dd9f75576aa50b0ff9df95'
AMP_SHA = '5c0bf32b4945d3cfdfd9bdc713799b0956adc296bbd17ba3f2450e1433bc6006'


def controls(out, dea, seed, fit, u):
    results = {}

    def record(key, outcome, **numbers):
        results[key] = dict(outcome=outcome, **numbers)
        write_json_file(out / 'controls.json', results)
        print(out.parent.parent.name, key, results[key], flush=True)
        assert outcome != 'failed', key

    if dea:
        expected = [5.12 * math.log(10), -1781 * math.log(10)]
        actual = [seed['a'], seed['b']]
        error = max(abs(a / b - 1) for a, b in zip(actual, expected, strict=True))
        record('C1', 'passed' if error <= 1e-12 else 'failed',
               coefficients=actual, reference=expected, relative_error=error, limit=1e-12)
        T, observed = [291, 298, 313], [.100, .140, .268]
        values = [math.exp(ln_k(seed, t)) for t in T]
        limits = [(1 + .0005 / k) * 10 ** (.005 + .5 / t) - 1 for t, k in zip(T, observed)]
        errors = [p / k - 1 for p, k in zip(values, observed)]
        record('C2', 'passed' if all(abs(e) <= b for e, b in zip(errors, limits)) else 'failed',
               T_K=T, reference=observed, values=values, relative_errors=errors, limits=limits)
    else:
        T, observed = [313.15, 323.15, 373.15], [.034, .024, .0089]
        values = [math.exp(-ln_k(seed, t)) for t in T]
        record('C3', 'comparison', T_K=T, reference=observed, values=values,
               relative_errors=[p / k - 1 for p, k in zip(values, observed)],
               max_abs_log_error=max(abs(math.log(p / k)) for p, k in zip(values, observed)))
    a, h = [q for q in u['coordinates'] if q.get('name') == R4]
    dh = -R * (fit['b'] - seed['b'])
    bounds = dict(level=[b + fit['b'] / TP - ln_k(seed, TP) for b in a['bounds']],
                  enthalpy=[b + dh for b in h['bounds']])
    declared = dict(level=[-3, 3] if dea else [-3, 2], enthalpy=[-30000, 10000] if dea else [-5000, 5000])
    error = max(abs(x / y - 1) for key in bounds for x, y in zip(bounds[key], declared[key], strict=True))
    record('C4', 'passed' if error <= 1e-9 else 'failed', mapped_bounds=bounds, declared=declared,
           stored_bounds=dict(level=a['bounds'], enthalpy=h['bounds']), increment_J_mol=dh,
           relative_error=error, limit=1e-9)
    return record, a['identity'], h['identity'], dh, bounds


def grid_rows(route, dea):
    amine, C = route.config['amine'], 'carbamate-anion'
    ratios = dict(phase='L', denominator_phase='L', denominator_species=[amine, 'protonated-' + amine, C])
    for T in ([TP, 393.15] if dea else [298.15, TP, 333.15, 353.15, 373.15, 393.15]):
        for i in range(1, 8 if dea else 9):
            alpha = i / 10
            bindings = dict(T=T, P=1e5, water=route.config['stocks'][0]['water'], alpha=alpha)
            for name, kind, args, unit in [
                ('carbamate', 'amount_ratio', dict(ratios, species=[C]), 'mol/mol'),
                ('bicarbonate+carbonate', 'amount_ratio', dict(ratios, species=['bicarbonate-anion', 'carbonate-anion']), 'mol/mol'),
                ('CO2 partial pressure', 'partial_pressure', dict(phase='V', species=['carbon-dioxide']), 'Pa'),
            ]:
                key = f'grid:{T}:{alpha}:{name}'
                yield dict(curve=name, loading=alpha, problems={key: dict(template='loaded-bubble', bindings=bindings)},
                           observation=dict(identity=key, problem=key, group=name, row={}, kind=kind, unit=unit,
                                            constructor='observation', arguments=dict(args, observed=1., form='difference', scale=1.)))


def deviations(rows):
    groups = defaultdict(list)
    for row in rows:
        T = row['T_K']
        band = 'absorber' if T <= 353.2 else 'stripper' if T >= 370 else 'intermediate'
        basis = row['basis']
        if row['identity'].startswith(('tong-2012:', 'hartono-2021:')) and row['role'] == 'not fitted':
            assert basis == 'Total equilibrium pressure', row['identity']
        for temperature_band in ('all', band):
            for reaction, outside in [('all', 'all'), *sorted(row['outside_ranges'].items())]:
                groups[row['group'], row['role'], basis, row['unit'], temperature_band, reaction, outside].append(row)
    for (group, role, basis, unit, band, reaction, outside), group_rows in groups.items():
        pairs = [(r['observed'], r['value']) for r in group_rows if r['status'] == 'Available' and r.get('requested_tolerance_met', True)]
        stats = deviation_statistics(pairs, unit) if pairs else {}
        yield dict(group=group, role=role, basis=basis, band=band, reaction=reaction,
                   outside_range=outside, **(stats | dict(unit=unit, rows=len(group_rows), available=len(pairs))))


def prepare(work, dea):
    directory = ROOT / 'analyses' / ('dea_transfer' if dea else 'amp_transfer')
    retained = directory / ('results/refit-413' if dea else 'results/retransfer-412-f2-05e94210/slope-150')
    declaration = directory / ('inputs/part-ii-346/f2-carbamate-413-route.json' if dea else 'inputs/retransfer-344/phase-2/AMP-05e94210.json')
    endpoint = retained / ('selection.json' if dea else 'parameters.json')
    predictions = retained / ('paper-data.csv' if dea else 'data-rows.json')
    uncertainty = retained / 'conditional-uncertainty.json'
    cost_file = endpoint if dea else retained / 'confirmation.json'
    assert digest(endpoint) == (DEA_SHA if dea else AMP_SHA), endpoint
    point = read(endpoint)['chosen']['parameters'] if dea else read(endpoint)
    cost = read(cost_file)['chosen']['cost'] if dea else read(cost_file)['selected_cost']
    with predictions.open() as file:
        all_rows = list(csv.DictReader(file)) if dea else read(predictions)
    reference = {r['identity']: float(r['predicted'] if dea else r['value']) for r in all_rows}
    # Use Route's existing wheel check. Keep its failed check in the study folder.
    out = directory / 'results/r4-shift-426'
    try:
        route = Route(declaration, work / directory.name)
    except (AssertionError, OSError) as error:
        write_json_file(out / 'controls.json', dict(C6=dict(outcome='failed', expected=SHA,
                  actual=digest(WHEEL) if WHEEL.is_file() else None, diagnostic=str(error))))
        raise
    source = read(declaration)['starts'][1]['reactions']
    seed_path = directory / 'reactive.py' if dea else declaration.parent / source['path']
    seed = dict(a=A0, b=B0) if dea else law(dict(reactions=route.load(source)), R4)
    fit, u = law(point, R4), read(uncertainty)
    record, a, h, dh, bounds = controls(out, dea, seed, fit, u)
    record('C6', 'passed', wheel_sha256=SHA)
    inputs = {endpoint, predictions, uncertainty, cost_file, declaration, seed_path, SHARED,
              declaration.parent / route.config['specification']}
    if dea:
        inputs.add(declaration.parent / route.config['curve_rows']['path'])
    write_json_file(out / 'identity.json', dict(commit=check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              wheel_sha256=SHA, engine_commit=WHEEL.parent.name.removeprefix('main-'),
              inputs={str(p.relative_to(ROOT)): digest(p) for p in sorted(inputs)}))
    fitted_rows = [r for r in all_rows if r['role'] == 'fitted']
    fitted_T = [float(r['T_K']) for r in fitted_rows if dea or r['group'] != 'binary']
    nmr_T = [float(r['T_K']) for r in fitted_rows if r['group'] == 'nmr']
    source_range = route.config['reaction_ranges_K'][R4]
    reactive_T = [float(r['T_K']) for r in all_rows if r['group'] not in ('Cai', 'Horstmann')] if dea else nmr_T
    limit_T = min(reactive_T), max(reactive_T)
    se = u['conditional_standard_error']
    corr = u['conditional_correlation'][u['free_coordinates'].index(a)][u['free_coordinates'].index(h)] if h in se else 0.
    shifts = []
    for T in sorted({298.15, TP, 393.15, max(fitted_T), *limit_T, *source_range}):
        src, fitted = ln_k(seed, T), ln_k(fit, T)
        g = -(1 / T - 1 / TP) / R
        sh = g * se.get(h, 0.)
        shifts.append(dict(T_K=T, source_ln_K4=src, fitted_ln_K4=fitted, delta_ln_K4=fitted-src,
                           K4_ratio=math.exp(fitted-src), SE_ln_K4=math.sqrt(se[a]**2 + sh**2 + 2*corr*se[a]*sh),
                           source_range='inside' if source_range[0] <= T <= source_range[1] else 'extrapolated'))
    write_csv_rows(out / 'shift.csv', shifts)
    write_json_file(out / 'table6.json', dict(delta_h_J_mol=dh, SE_h_J_mol=se.get(h), bounds=bounds,
              delta_ln_K4=ln_k(fit, TP)-ln_k(seed, TP), SE_ln_K4=se[a],
              source_h_J_mol=-R*seed['b'], fitted_h_J_mol=-R*fit['b']))
    variants = {'reported': fit, 'source': seed}
    if not dea:
        for name, increment in [('source-enthalpy', 0.), ('released', -10000.)]:
            b = seed['b'] - increment / R
            variants[name] = dict(a=ln_k(fit, TP) - b / TP, b=b)
    return route, out, point, variants, reference, cost, record, dea


def replay(case, names):
    route, out, point, variants, reference, reference_cost, record, dea = case
    for name in names:
        start = monotonic()
        variant = copy.deepcopy(point)
        law(variant, R4).update({k: variants[name][k] for k in ('a', 'b')})
        fitted, available, cost = route.replay(variant)
        rows = route.reduce(variant, fitted=fitted)
        write_json_file(out / f'{name}-rows.json', jsonable(rows))
        seconds = monotonic() - start
        timing = dict(seconds=seconds, rows=len(rows), cost=cost,
                  coefficients={k: law(variant, R4)[k] for k in ('a', 'b')},
                  cost_by_group={group: sum(r['cost'] for r in fitted if r['group'] == group)
                                 for group in sorted({r['group'] for r in fitted})} if available else None)
        write_json_file(out / f'{name}-replay.json', timing)
        print(out.parent.parent.name, name, 'replay seconds', seconds, flush=True)
        if name == 'reported':
            matched = {r['identity'] for r in rows} == reference.keys() and len(rows) == len(reference) == (299 if dea else 270)
            errors = [abs(r['value'] / reference[r['identity']] - 1) for r in rows if r['status'] == 'Available' and r['identity'] in reference]
            prediction_error = max(errors, default=None)
            cost_error = abs(cost / reference_cost - 1) if available else None
            passed = matched and len(errors) == len(rows) and available and max(prediction_error, cost_error) <= LIMIT
            record('C5', 'passed' if passed else 'failed', matched=matched, rows=len(rows), scored=len(errors),
                   cost=cost, reference_cost=reference_cost, relative_cost_error=cost_error,
                   max_relative_prediction_error=prediction_error, limit=LIMIT)
            assert seconds * len(variants) < 600, 'Projected replay time exceeds 10 minutes'
        write_csv_rows(out / f'{name}-deviations.csv', list(deviations(rows)))
        start = monotonic()
        grid = route.curves(variant, grid_rows(route, dea))
        write_csv_rows(out / f'{name}-grid.csv', [
            {k: r.get(k) for k in ('T_K', 'loading', 'curve', 'unit', 'value', 'status', 'requested_tolerance_met', 'message', 'outside_ranges')}
            for r in grid])
        timing['grid_seconds'] = monotonic() - start
        write_json_file(out / f'{name}-replay.json', timing)
        print(out.parent.parent.name, name, 'grid seconds', timing['grid_seconds'], flush=True)
        if name == 'reported':
            assert all(r['status'] == 'Available' and r.get('requested_tolerance_met')
                       for r in grid if r['T_K'] in (TP, 393.15)), 'Reported pivot or stripper grid unavailable'
        if dea:
            start = monotonic()
            curves = route.load(route.config['curve_rows'])
            curves = route.curves(variant, (r for r in curves if r['observation']['group'].startswith('Bottinger-')))
            write_json_file(out / f'{name}-nmr-curves.json', jsonable(curves))
            timing['nmr_curve_seconds'] = monotonic() - start
            write_json_file(out / f'{name}-replay.json', timing)
            print(out.parent.parent.name, name, 'NMR curve seconds', timing['nmr_curve_seconds'], flush=True)


if __name__ == '__main__':
    with TemporaryDirectory() as tmp:
        cases = [prepare(Path(tmp), dea) for dea in (True, False)]
        for case in cases:
            replay(case, ['reported'])
        for case in cases:
            replay(case, [name for name in case[3] if name != 'reported'])
