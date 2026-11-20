"""#392 per-state cost of the MDEA Stage B stability search on the pinned wheel, and equivalence of the search after a change.

  agent-heavy env PYTHONPATH=src .venv/bin/python analyses/stability_search/search_profile.py split <run dir> <temperature K> <states>
  ... search_profile.py subset <run dir>
  ... search_profile.py compare <baseline run dir> <changed run dir>
  ... search_profile.py summary <split before> <split after> <subset before> <subset after> <retained search-0-summary.json.gz>

split: exclusive time of each step of stable_refit_255._measure for a seeded random sample of one temperature group, through
Route.grid unchanged; the Engine's predict is decomposed afterwards by repeating its bubble-pressure, parent and Full-search calls
on the same item (excluded from the per-state total). subset: every non-grid state plus 300 seeded 353.15 K grid states.
The retained search is origin/issue-343-mdea-f2 (e3d1cd8) analyses/mdea_mea_workflow/results/stage-b-f2/search-0-summary.json.gz,
wheel 0962e21d, the source of this case's inputs. For searches, use a Git-ignored run directory inside the repository.
"""
import collections
import gzip
import json
import math
from pathlib import Path
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'analyses'))
import part_ii  # noqa: E402

DECLARATION = ROOT/'analyses/mdea_mea_workflow/inputs/stage-b.json'
POINT = ROOT/'analyses/mdea_mea_workflow/inputs/stage-b-start-0-point.json'
OUT = ROOT/'analyses/stability_search/results/timing-392'
ENGINE = ('predict', 'solve', 'prepare', 'supplied_test', 'compile', 'construct/compile')  # Engine calls inside _measure


def route_and_states(out):
    route = part_ii.Route(DECLARATION, out)
    point = json.loads(POINT.read_text())
    return route, point, route.states(route.bind(point))


def split(out, temperature, size):
    stable, eq, reg = part_ii.stable, part_ii.eq, part_ii.reg
    stack, spent, captured = [], collections.defaultdict(float), {}

    def timed(function, label):
        def call(*args, **kwargs):
            stack.append([label, 0.])
            started = time.perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                elapsed = time.perf_counter()-started
                _, inner = stack.pop()
                spent['/'.join([s[0] for s in stack]+[label])] += elapsed-inner
                if stack:
                    stack[-1][1] += elapsed
        return call

    original = dict(solve=eq.solve_equilibrium, compile=eq.compile_problem, measure=eq._core.stability_measure)
    initialize, measure = stable._init, stable._measure

    def instrumented_init(*args):
        initialize(*args)
        route = stable._ROUTE
        row = route.stability_row
        def kept(*a, **k):
            captured['item'] = row(*a, **k)
            return captured['item']
        route.stability_row = timed(kept, 'construct')
        for name in ('stability_metadata', 'pressure_basis', 'branch_counts'):
            setattr(route, name, timed(getattr(route, name), name))
        for module, name, label in ((eq, 'compile_problem', 'compile'), (eq, 'solve_equilibrium', 'solve'), (eq, 'prepare_supplied_trials', 'prepare'),
                                    (eq, 'stability_test', 'supplied_test'), (reg, 'predict', 'predict'), (stable, 'stability_payload', 'payload'),
                                    (stable, 'jsonable', 'jsonable'), (stable, 'tally', 'tally'), (json, 'dumps', 'json_dumps'), (gzip, 'compress', 'gzip')):
            setattr(module, name, timed(getattr(module, name), label))
        Path.write_bytes = timed(Path.write_bytes, 'write')

        def instrumented(state):
            spent.clear(), captured.clear()
            started = time.perf_counter()
            row = timed(measure, 'measure')(state)
            total, steps, parts = time.perf_counter()-started, dict(spent), {}
            item = captured.get('item')
            if item is not None and row.get('status') != 'Exception':
                model = stable._SPEC.model
                t = time.perf_counter()
                if item.pressure_reference is not None:
                    original['solve'](model, item.pressure_reference)
                parts['bubble_solve'] = time.perf_counter()-t
                t = time.perf_counter(); result = original['solve'](model, item.problem); parts['parent_solve'] = time.perf_counter()-t
                t = time.perf_counter(); compiled = original['compile'](model, item.problem); parts['compile'] = time.perf_counter()-t
                t = time.perf_counter(); full = original['measure'](compiled, result, item.stability_options); parts['full_search'] = time.perf_counter()-t
                parts['value_matches'] = full.value == row.get('value')
            row['_profile'] = dict(total=total, steps=steps, predict_parts=parts)
            return row
        stable._measure = instrumented

    stable._init = instrumented_init
    route, point, states = route_and_states(out)
    spec = route.bind(point)
    group = [s for s in states if route.temperature(spec, s) == temperature]
    sample = random.Random(392).sample(group, size)
    started = time.perf_counter()
    measured = route.grid(point, sample)
    rows = [dict(key=r['key'], available=bool(r.get('available')), **r['_profile']) for r in measured]
    (Path(out)/'profile.json').write_text(json.dumps(dict(temperature_K=temperature, group_states=len(group), wall=time.perf_counter()-started, rows=rows), indent=1))


def subset(out):
    route, point, states = route_and_states(out)
    grid = [s for s in states if s['key'].startswith('grid:') and s['T'] == 353.15]
    chosen = [s for s in states if not s['key'].startswith('grid:')]+random.Random(7).sample(grid, 300)
    started = time.perf_counter()
    measured = route.grid(point, chosen)
    print(json.dumps(dict(states=len(chosen), wall=time.perf_counter()-started, worker=math.fsum(r['seconds'] for r in measured))))


def part(out, temperatures):
    """One part of the full search, timed from Route.grid call to written output: grid states at the listed temperatures, or 'data'."""
    route, point, states = route_and_states(out)
    chosen = [s for s in states if not s['key'].startswith('grid:')] if temperatures == 'data' else \
        [s for s in states if s['key'].startswith('grid:') and s['T'] in {float(t) for t in temperatures.split(',')}]
    started = time.perf_counter()
    measured = route.grid(point, chosen)
    result = dict(part=temperatures, states=len(chosen), full_states=len(states), wall_seconds=time.perf_counter()-started, workers=route.workers,
                  worker_seconds=math.fsum(r['seconds'] for r in measured), copies=sum('same_calculation_as' in r for r in measured),
                  available=sum(bool(r.get('available')) for r in measured), descent=sum(map(part_ii.stable.descent, measured)))
    (Path(out)/'part.json').write_text(json.dumps(result, indent=1)+'\n')
    print(json.dumps(result))


REPIN = ROOT/f'analyses/stability_search/results/repin-{part_ii.WHEEL.parent.name[5:13]}'


def cause(row):
    """Unavailability cause of one search row: Engine status and message with numbers removed, or the supplied-trial failure."""
    import re
    if not row.get('optimized_available', row.get('available')):
        return f"{row.get('status')}: {re.sub(r'-?[0-9]+(\.[0-9]+)?(e[-+]?[0-9]+)?', '#', str(row.get('message', '')))[:160]}"
    return f"supplied trials: {row.get('supplied_error') or 'not all evaluated'}"


def amp_timing(retained, e1063366):
    """#391's AMP search-106 timing on the current pin, then mismatches against the retained and e1063366 searches."""
    import search_timing
    search_timing.OUT = REPIN
    search_timing.amp()
    summary = json.loads((REPIN/'amp-search-106.json').read_text())
    run = ROOT/summary['run']
    summary['versus_retained'] = search_timing.compare(run, retained)
    summary['versus_e1063366'] = search_timing.compare(run, e1063366)
    summary['retained_sources'] = dict(retained=f'{retained} (sha256 {sha256(retained)}; #391 copy of the search-106 record)', e1063366=str(e1063366))
    (REPIN/'amp-search-106.json').write_text(json.dumps(summary, indent=1)+'\n')


def sha256(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mdea_full(out):
    """Full MDEA Stage B search on the current pin and the #337 rule (b) grid, timed from Route.grid call to written output."""
    import search_timing
    route, point, states = route_and_states(out)
    measured, seconds, peak = search_timing.timed_search(route, point, states, None)
    spec = route.bind(point)
    unavailable = [r for r in measured if not r.get('available')]
    by_cause = collections.Counter((('grid' if r['key'].startswith('grid:') else 'data'), cause(r)) for r in unavailable)
    descents = [r for r in measured if part_ii.stable.descent(r)]
    summary = dict(case='MDEA Stage B start-0 search, #337 rule (b) grid', wheel_sha256=part_ii.SHA, states=len(states),
                   grid_states=sum(s['key'].startswith('grid:') for s in states), copies=sum('same_calculation_as' in r for r in measured),
                   workers=route.workers, wall_seconds=seconds, wall_basis='Route.grid call: binding, duplicate detection, worker start, all states, split record and search JSON',
                   peak_rss_total_MB=peak['total_kb']/1e3, peak_rss_largest_process_MB=peak['process_kb']/1e3,
                   rss_basis='VmRSS of the timing process plus descendants sampled every 0.5 s',
                   available=len(measured)-len(unavailable), unavailable=len(unavailable),
                   failed=sum(r.get('status') == 'Exception' for r in measured),
                   unavailable_by_cause=[dict(part=p, cause=c, states=n) for (p, c), n in by_cause.most_common()],
                   descent=dict(data=sum(not r['key'].startswith('grid:') for r in descents), grid=sum(r['key'].startswith('grid:') for r in descents)),
                   descent_states=[dict(key=r['key'], T_K=route.temperature(spec, next(s for s in states if s['key'] == r['key'])),
                                        native_branch=r.get('native_branch'), supplied_branch=r.get('supplied_branch'),
                                        value=r.get('value'), supplied_minimum_tpd=r.get('supplied_minimum_tpd')) for r in descents],
                   run=str(Path(out).resolve().relative_to(ROOT)))
    REPIN.mkdir(parents=True, exist_ok=True)
    (REPIN/'mdea-full-search.json').write_text(json.dumps(summary, indent=1)+'\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'descent_states'}, indent=1))


CLASSES = ('available', 'descent', 'native_branch', 'supplied_branch', 'status')
VALUES = ('value', 'raw_minimum', 'uncertainty', 'supplied_minimum_tpd', 'pressure_Pa')


def stability_changes(old_path, new_path):
    """#393: Part II stability rows matched by key, old against new. Every state whose availability, descent, density branch or
    Engine status changed is listed with its TPD/RT values and uncertainty; value differences are summarized for the others."""
    old, new = ({r['key']: r for r in part_ii.stable.read(p)} for p in (old_path, new_path))
    keys = sorted(old.keys() & new.keys())
    descent = part_ii.stable.descent
    classify = lambda r: dict(available=bool(r.get('available')), descent=descent(r), **{k: r.get(k) for k in CLASSES[2:]})
    changed, largest = [], {}
    for key in keys:
        a, b = classify(old[key]), classify(new[key])
        recorded = [k for k in CLASSES[2:] if a[k] is not None and b[k] is not None]  # older records carry no density branch
        if {k: a[k] for k in ('available', 'descent', *recorded)} != {k: b[k] for k in ('available', 'descent', *recorded)}:
            changed.append(dict(key=key, part='grid' if key.startswith('grid:') else 'data',
                                old=dict(a, **{v: old[key].get(v) for v in VALUES}, cause=None if a['available'] else cause(old[key])),
                                new=dict(b, **{v: new[key].get(v) for v in VALUES}, cause=None if b['available'] else cause(new[key]))))
            continue
        for v in VALUES:
            x, y = old[key].get(v), new[key].get(v)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)) and abs(x-y) > largest.get(v, (0.,))[0]:
                largest[v] = (abs(x-y), key, x, y)
    count = lambda rows, part: dict(states=sum(1 for k in rows if (k.startswith('grid:')) == (part == 'grid')),
                                    available=sum(bool(r.get('available')) for k, r in rows.items() if (k.startswith('grid:')) == (part == 'grid')),
                                    descent=sum(descent(r) for k, r in rows.items() if (k.startswith('grid:')) == (part == 'grid')))
    shared = lambda rows: {k: rows[k] for k in keys}
    return dict(old=str(old_path), new=str(new_path), shared_states=len(keys), only_old=len(old.keys()-new.keys()), only_new=len(new.keys()-old.keys()),
                counts={side: {part: count(shared(rows), part) for part in ('data', 'grid')} for side, rows in (('old', old), ('new', new))},
                only_new_counts={part: count({k: new[k] for k in new.keys()-old.keys()}, part) for part in ('data', 'grid')},
                changed=changed, unchanged_value_max_abs_difference={v: dict(difference=d, key=k, old=x, new=y) for v, (d, k, x, y) in largest.items()})


def compare(base, new):
    base, new = Path(base), Path(new)
    B, N = (json.loads((root/'search-0.json').read_text()) for root in (base, new))
    strip = lambda row: json.dumps({k: v for k, v in row.items() if k not in {'seconds', 'details', 'supplied_trial_evidence', 'same_calculation_as'}}, sort_keys=True)
    out = dict(states=len(B), same_order=[r['key'] for r in B] == [r['key'] for r in N], copies=0, row_mismatch=[])
    for b, n in zip(B, N):
        out['copies'] += 'same_calculation_as' in n
        out['row_mismatch'] += [b['key']]*(strip(b) != strip(n))
    out['split_record_identical'] = (base/'split-record.json').read_bytes() == (new/'split-record.json').read_bytes()
    out['worker_seconds'] = dict(base=math.fsum(r['seconds'] for r in B), new=math.fsum(r['seconds'] for r in N))
    out['identical'] = out['same_order'] and not out['row_mismatch'] and out['split_record_identical']
    return out


def per_state(path):
    run = json.loads((Path(path)/'profile.json').read_text())
    rows, steps = run['rows'], collections.defaultdict(float)
    for row in rows:
        for step, seconds in row['steps'].items():
            steps[step.removeprefix('measure/') if step != 'measure' else 'measure (trial list and record assembly)'] += seconds
    n, total = len(rows), math.fsum(r['total'] for r in rows)
    engine = math.fsum(steps[k] for k in ENGINE)
    parts = {k: statistics.mean(r['predict_parts'][k] for r in rows if r['available'] and k in r['predict_parts'])
             for k in ('bubble_solve', 'parent_solve', 'compile', 'full_search')}
    return dict(states=n, temperature_K=run['temperature_K'], group_states=run['group_states'], seed=392,
                mean_seconds=total/n, engine_seconds=engine/n, downstream_seconds=(total-engine)/n,
                available=sum(r['available'] for r in rows), unavailable=sum(not r['available'] for r in rows),
                mean_available_seconds=statistics.mean(r['total'] for r in rows if r['available']),
                mean_unavailable_seconds=statistics.mean(r['total'] for r in rows if not r['available']),
                steps={k: dict(seconds=v/n, percent=100*v/total) for k, v in sorted(steps.items(), key=lambda x: -x[1]) if v/n >= 5e-4},
                predict_parts_available_states=parts,
                predict_parts_value_matches=all(r['predict_parts'].get('value_matches', True) for r in rows))


def summary(before, after, subset_before, subset_after, retained):
    retained = json.loads(gzip.decompress(Path(retained).read_bytes()))
    copies = {r['key'] for r in json.loads((Path(subset_after)/'search-0.json').read_text()) if 'same_calculation_as' in r}
    s0, s1 = per_state(before), per_state(after)
    def projection(split_row, drop):
        available = sum(1 for r in retained if r['available'] and r['key'] not in drop)
        unavailable = sum(1 for r in retained if not r['available'] and r['key'] not in drop)
        worker = available*split_row['mean_available_seconds']+unavailable*split_row['mean_unavailable_seconds']
        return dict(available_states=available, unavailable_states=unavailable, worker_seconds=worker, wall_hours_3_workers=worker/3/3600)
    after_projection = projection(s1, copies)
    a, u = after_projection['available_states'], after_projection['unavailable_states']
    parts, steps = s1['predict_parts_available_states'], s1['steps']
    owners = {'Engine: optimized Full search': parts['full_search']*a,
              'Engine: failed bubble-pressure reference solves (unavailable states)': (s1['mean_unavailable_seconds']-s1['downstream_seconds'])*u,
              'Engine: successful bubble-pressure reference solve': parts['bubble_solve']*a,
              'Engine: parent solve inside predict': parts['parent_solve']*a,
              'Engine: supplied-trial evaluation': steps['supplied_test']['seconds']*a,
              'Downstream: second parent solve for the supplied trials': steps['solve']['seconds']*a,
              'Downstream: Python and per-state output': s1['downstream_seconds']*(a+u)}
    result = dict(case='MDEA Stage B start-0 search', wheel_sha256=part_ii.SHA, split_before=s0, split_after=s1,
                  equivalence=compare(subset_before, subset_after),
                  projection_before=projection(s0, set()), projection_after=after_projection,
                  projection_basis='353.15 K sample means for available and unavailable states x the retained full search availability per key (origin/issue-343-mdea-f2 e3d1cd8, wheel 0962e21d; 0 availability mismatches on the sample) / 3 workers; temperature-group dispatch adds about 2 %',
                  owner_hours_after={k: v/3/3600 for k, v in owners.items()})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'summary.json').write_text(json.dumps(result, indent=1)+'\n')
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    mode, args = sys.argv[1], sys.argv[2:]
    if mode == 'split':
        split(args[0], float(args[1]), int(args[2]))
    elif mode == 'subset':
        subset(args[0])
    elif mode == 'part':
        part(args[0], args[1])
    elif mode == 'amp':  # amp <retained search-106 JSON> <e1063366 search-0.json>
        amp_timing(Path(args[0]), Path(args[1]))
    elif mode == 'mdea':  # mdea <run dir>
        mdea_full(args[0])
    elif mode == 'stability':  # stability <summary name> <old search JSON[.gz]> <new search JSON>
        result = stability_changes(args[1], args[2])
        REPIN.mkdir(parents=True, exist_ok=True)
        (REPIN/f'{args[0]}.json').write_text(json.dumps(result, indent=1)+'\n')
        print(json.dumps({k: v for k, v in result.items() if k != 'changed'}, indent=1), len(result['changed']), 'changed states')
    elif mode == 'parts':  # parts <run dir>...: one full search measured in parts
        parts = [json.loads((Path(p)/'part.json').read_text()) for p in args]
        total = dict(states=sum(p['states'] for p in parts), full_states=parts[0]['full_states'], parts=parts,
                     wall_seconds_sum_of_parts=math.fsum(p['wall_seconds'] for p in parts),
                     worker_seconds=math.fsum(p['worker_seconds'] for p in parts),
                     copies=sum(p['copies'] for p in parts), available=sum(p['available'] for p in parts), descent=sum(p['descent'] for p in parts))
        total['wall_seconds_all_workers_busy'] = total['worker_seconds']/parts[0]['workers']
        assert total['states'] == total['full_states']
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT/'reduced-grid-search.json').write_text(json.dumps(total, indent=1)+'\n')
        print(json.dumps({k: v for k, v in total.items() if k != 'parts'}, indent=1))
    elif mode == 'compare':
        print(json.dumps(compare(*args), indent=1))
    elif mode == 'summary':
        summary(*args)
    else:
        raise ValueError('Expected split, subset, compare or summary')
