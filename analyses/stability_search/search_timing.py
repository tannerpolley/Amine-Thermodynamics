"""#391 wall time of one full Part II stability search on the pinned wheel, from search start to written output.

  agent-heavy env PYTHONPATH=src uv run --no-sync python analyses/stability_search/search_timing.py amp
  ... search_timing.py mdea <temperature K>
  ... search_timing.py equivalence <temperature K> [first N states] [summary path]
  ... search_timing.py compare <run directory> <retained search JSON[.gz]> [summary path]

The AMP case is campaign-373 search 106: retreat point t = 0.6624609375000001 between the retained anchor and
endpoint, the 1,906 enforced states and the 5,895-entry initial trial record (archive/issue-344-amp-f2-f3d87a8).
The MDEA case is one temperature group of the 69,099-state Stage B search at the start-0 unpenalized endpoint, with
the declared 2,789-entry trial record (archive/issue-343-stage-b-mdea-f2). The search rows and split record stay in the ignored run directory.
"""
import json
import math
import os
from pathlib import Path
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'analyses'))
import part_ii  # noqa: E402

AMP = ROOT/'analyses/amp_transfer/inputs/retransfer-344'
MDEA = ROOT/'analyses/mdea_mea_workflow/inputs'
T106 = 0.6624609375000001  # progress.txt "start-0 refine" entry immediately before search-106.json
RUNS = ROOT/'analyses/stability_search/results/runs'
OUT = ROOT/'analyses/stability_search/results/timing-391'


def rss_kb(pid):
    """Resident set of a process and all its descendants, kB, from /proc."""
    try:
        own = next(int(x.split()[1]) for x in Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('VmRSS:'))
        children = [int(c) for task in Path(f'/proc/{pid}/task').iterdir() for c in (task/'children').read_text().split()]
    except (FileNotFoundError, ProcessLookupError, StopIteration):
        return 0, 0
    total, largest = own, own
    for child in children:
        t, l = rss_kb(child)
        total, largest = total+t, max(largest, l)
    return total, largest


def timed_search(route, point, states, trials):
    peak = dict(total_kb=0, process_kb=0)
    done = threading.Event()
    def sample():
        while not done.wait(.5):
            total, largest = rss_kb(os.getpid())
            peak.update(total_kb=max(peak['total_kb'], total), process_kb=max(peak['process_kb'], largest))
    threading.Thread(target=sample, daemon=True).start()
    started = time.monotonic()
    measured = route.grid(point, states, trial_set=trials)  # trials None: the declared record, as in a full search
    seconds = time.monotonic()-started
    done.set()
    return measured, seconds, peak


def counts(measured):
    tally = part_ii.stable.tally(measured)
    return dict(states=len(measured), available=tally['available'], unavailable=len(tally['unavailable']),
                failed=sum(r.get('status')=='Exception' for r in measured), descents=tally['descent'],
                supplied_trial_counts=tally['supplied_trial_counts'], minimum_tau=tally['minimum_tau'],
                supplied_minimum_tpd=tally['supplied_minimum_tpd'],
                state_seconds=dict(sum=math.fsum(r['seconds'] for r in measured), max=max(r['seconds'] for r in measured)))


def amp():
    run = RUNS/f"amp-106-{time.strftime('%Y%m%dT%H%M%S')}"
    route = part_ii.Route(AMP/'phase-2/AMP-373.json', run)
    load = lambda name: json.loads((AMP/'search-106'/name).read_text())
    point = route.segment(load('anchor.json'), load('endpoint.json'), T106)
    record = load('split-record-initial.json')
    trials = record['trials']+record.get('supplied_trials', [])
    for witness in trials:  # as stable_refit_255.retreat builds its fixed base list
        if witness.get('kind') in ('liquid', 'vapor'):
            witness['kind'] = witness['kind'].title()
    measured, seconds, peak = timed_search(route, point, load('enforced.json'), trials)
    summary = dict(case='AMP campaign-373 search 106', t=T106, trials=len(trials), workers=route.workers,
                   wall_seconds=seconds, wall_basis='route.grid call: parent binding, temperature grouping, worker start, all states, and search JSON',
                   peak_rss_total_MB=peak['total_kb']/1e3, peak_rss_largest_process_MB=peak['process_kb']/1e3,
                   rss_basis='VmRSS of the timing process plus descendants sampled every 0.5 s',
                   wheel_sha256=part_ii.SHA, run=str(run.relative_to(ROOT)), **counts(measured))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'amp-search-106.json').write_text(json.dumps(summary, indent=1)+'\n')
    print(json.dumps(summary, indent=1))


def mdea(temperature):
    run = RUNS/f"mdea-{temperature}-{time.strftime('%Y%m%dT%H%M%S')}"
    route = part_ii.Route(MDEA/'stage-b.json', run)
    point = json.loads((MDEA/'stage-b-start-0-point.json').read_text())
    spec = route.bind(point)
    states = route.states(spec)
    groups = {}
    for state in states:
        groups.setdefault(route.temperature(spec, state), []).append(state)
    chosen = groups[temperature]
    measured, seconds, peak = timed_search(route, point, chosen, None)
    per_state = seconds/len(chosen)
    summary = dict(case='MDEA Stage B start-0 search, one temperature group', temperature_K=temperature, group_states=len(chosen),
                   full_states=len(states), temperature_groups={str(k): len(v) for k, v in sorted(groups.items())},
                   trials=len(route.load(route.config['split_record'])['trials']), workers_used=1, workers_available=route.workers,
                   wall_seconds=seconds, wall_basis='route.grid call for this group on one worker (one temperature per worker task), output included',
                   projected_full_seconds=per_state*len(states)/route.workers,
                   projection_basis='measured seconds per state in this group x all states / available workers; assumes equal per-state cost across groups and full worker use',
                   peak_rss_total_MB=peak['total_kb']/1e3, peak_rss_largest_process_MB=peak['process_kb']/1e3,
                   wheel_sha256=part_ii.SHA, run=str(run.relative_to(ROOT)), **counts(measured))
    summary['projected_full_hours'] = summary['projected_full_seconds']/3600
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/f'mdea-group-{temperature}.json').write_text(json.dumps(summary, indent=1)+'\n')
    print(json.dumps(summary, indent=1))


def _listed(parent, result, supplied, identities):
    """Engine list path: the same ordered supplied list evaluated fresh for this parent."""
    eq, stable = part_ii.eq, part_ii.stable
    options = eq.StabilityOptions()
    options.trials, options.evaluate_supplied_trials = supplied, True
    return eq.stability_test(eq.compile_problem(stable._SPEC.model, parent), result, options)


def _both(states):
    """Worker task: each state measured through the held prepared set, then through the list path."""
    stable, out = part_ii.stable, []
    for state in states:
        prepared = stable._measure(state)
        held, stable._supplied_report = stable._supplied_report, _listed
        try:
            listed = stable._measure(state)
        finally:
            stable._supplied_report = held
        out.append((prepared, listed))
    return out


def equivalence(temperature, count=None, path=OUT/'prepared-equivalence.json'):
    """List versus prepared supplied evaluation for the search-106 states at one temperature (all, or the first count)."""
    from concurrent.futures import ProcessPoolExecutor
    route = part_ii.Route(AMP/'phase-2/AMP-373.json', RUNS/f"amp-106-equivalence-{time.strftime('%Y%m%dT%H%M%S')}")
    load = lambda name: json.loads((AMP/'search-106'/name).read_text())
    point = route.segment(load('anchor.json'), load('endpoint.json'), T106)
    record = load('split-record-initial.json')
    trials = record['trials']+record.get('supplied_trials', [])
    for witness in trials:
        if witness.get('kind') in ('liquid', 'vapor'):
            witness['kind'] = witness['kind'].title()
    spec = route.bind(point)
    states = [s for s in load('enforced.json') if route.temperature(spec, s)==temperature][:count]
    chunks = [states[i::route.workers] for i in range(route.workers)]
    with ProcessPoolExecutor(route.workers, initializer=part_ii.stable._init, initargs=(point, trials, route)) as pool:
        pairs = [pair for chunk in pool.map(_both, chunks) for pair in chunk]
    fields = dict(states=0, supplied_lists=0, entries=0, order_and_multiplicity=0, evidence=0, message=0, resolved_descent=0,
                  density_side=0, tpd_exact=0, tpd_within_uncertainty=0, other_quantities=0, not_applicable=0,
                  supplied_trial_counts=0, supplied_available=0, supplied_branch=0, supplied_minimum_tpd=0, native_value=0)
    differing_quantities, max_tpd = set(), 0.
    for p, l in pairs:
        fields['states'] += 1
        a, b = p.get('supplied_trials', []), l.get('supplied_trials', [])
        fields['supplied_lists'] += bool(a)
        fields['order_and_multiplicity'] += len(a)==len(b)
        for x, y in zip(a, b):
            fields['entries'] += 1
            for key in ('evidence', 'message', 'resolved_descent'):
                fields[key] += x[key]==y[key]
            qx, qy = x['quantities'], y['quantities']
            fields['density_side'] += qx.get('density_side')==qy.get('density_side')
            if 'tpd_over_rt' in qx and 'tpd_over_rt' in qy:
                difference = abs(qx['tpd_over_rt']-qy['tpd_over_rt'])
                max_tpd = max(max_tpd, difference)
                fields['tpd_exact'] += difference==0.
                fields['tpd_within_uncertainty'] += difference<=max(qx.get('descent_error_estimate_over_rt', 0.), qy.get('descent_error_estimate_over_rt', 0.))
            else:
                fields['tpd_exact'] += qx.get('tpd_over_rt')==qy.get('tpd_over_rt')
                fields['tpd_within_uncertainty'] += qx.get('tpd_over_rt')==qy.get('tpd_over_rt')
            same = {k for k in qx.keys()|qy.keys() if qx.get(k)==qy.get(k)}
            fields['other_quantities'] += same==qx.keys()|qy.keys()
            differing_quantities |= (qx.keys()|qy.keys())-same
        fields['not_applicable'] += p.get('not_applicable_supplied_trials')==l.get('not_applicable_supplied_trials')
        for key in ('supplied_trial_counts', 'supplied_available', 'supplied_branch'):
            fields[key] += p.get(key)==l.get(key)
        fields['supplied_minimum_tpd'] += part_ii.stable.tally([p])['supplied_minimum_tpd']==part_ii.stable.tally([l])['supplied_minimum_tpd']
        fields['native_value'] += p.get('value')==l.get('value')
    summary = dict(case='AMP campaign-373 search 106 states at one temperature', temperature_K=temperature, trials=len(trials),
                   matches=fields, differing_quantity_keys=sorted(differing_quantities), max_abs_tpd_over_rt_difference=max_tpd,
                   statuses=sorted({p.get('status') for p, _ in pairs}), keys=[p['key'] for p, _ in pairs],
                   uncertainty_basis='larger descent_error_estimate_over_rt of the two evaluations', wheel_sha256=part_ii.SHA)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(summary, indent=1)+'\n')
    print(json.dumps({k: v for k, v in summary.items() if k!='keys'}, indent=1))


def compare(run, retained):
    """Per-state comparison of a timed search with the retained search of the same states and trial list."""
    new = {r['key']: r for r in json.loads(sorted(Path(run).glob('search-[0-9]*.json'))[0].read_text())}
    old = {r['key']: r for r in part_ii.stable.read(retained)}
    assert new.keys()<=old.keys()
    old = {k: old[k] for k in new}
    out = dict(states=len(new), mismatched={}, max_abs_difference={})
    for field in ('available', 'descent', 'native_branch', 'supplied_branch', 'supplied_trial_counts', 'status'):
        out['mismatched'][field] = sorted(k for k in new if new[k].get(field)!=old[k].get(field))
    for field in ('value', 'supplied_minimum_tpd', 'pressure_Pa', 'supplied_parent_pressure_Pa'):
        pairs = [(new[k].get(field), old[k].get(field)) for k in new]
        out['mismatched'][field+'_presence'] = sorted(k for k, (a, b) in zip(new, pairs) if (a is None)!=(b is None))
        out['max_abs_difference'][field] = max((abs(a-b) for a, b in pairs if a is not None and b is not None), default=None)
    return out


if __name__ == '__main__':
    if sys.argv[1]=='amp':
        amp()
    elif sys.argv[1]=='mdea':
        mdea(float(sys.argv[2]))
    elif sys.argv[1]=='equivalence':
        equivalence(float(sys.argv[2]), *([int(sys.argv[3]), sys.argv[4]] if len(sys.argv) > 4 else []))
    elif sys.argv[1]=='compare':
        result = compare(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=1))
        if len(sys.argv)>4:
            Path(sys.argv[4]).write_text(json.dumps(result, indent=1)+'\n')
    else:
        raise ValueError('Expected amp or compare')
