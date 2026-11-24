"""#413: the #398 DEA campaign with the carbamate inputs of the adopted MEA fit F2 instead of F0.

prepare: write the f2-carbamate-413-* inputs beside the #398 inputs, changing only the carbamate energy and diameters.
run OUT: replay #398, time one objective and one stability search, then run and report the unchanged campaign.
"""
import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
from time import monotonic

AN = Path(__file__).resolve().parent
sys.path.insert(0, str(AN.parent))
sys.path.insert(0, str(AN))
OLD = AN / 'inputs/part-ii-346'
P = 'f2-carbamate-413-'  # new files sit beside the #398 inputs so every relative path resolves unchanged
PREVIOUS = AN / 'results/retransfer-398'
DETAILS = AN.parents[1] / 'analyses/mea_parameter_bundle/results/reduced-refit/parameter-details.csv'
DETAILS_SHA = 'a391a1d04ae64ba7c5a9b57c2e0fd7b08290d1c81a907daa64e5a5d8c5272b0a'
C, DEA = 'carbamate-anion', 'diethanolamine'
RULE = 'design D2: MEA ion diameter x (m sigma^3 DEA / MEA)^(1/3)'
F2_SOURCE = 'analyses/mea_parameter_bundle/results/reduced-refit/parameter-details.csv (fit F2, adopted MEA record ae17803e); issue #413'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
read = lambda path: json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def mea_carbamate():
    assert sha(DETAILS) == DETAILS_SHA, DETAILS
    with DETAILS.open() as f:
        rows = {(r['fit'], r['identity'].split('/')[-1]): float(r['value']) for r in csv.DictReader(f) if r['identity'].startswith(f'component/{C}/')}
    return {fit: dict(sigma=rows[fit, 'segment_diameter'], epsilon=rows[fit, 'dispersion_energy_over_k']) for fit in ('F0', 'F2')}


def carbamate(mapping, mea):
    """Set the DEA carbamate from an MEA carbamate: same energy; diameters by the D2 cube-root m*sigma^3 rule (binary.py)."""
    value = lambda component, family: next(c['value']['magnitude'] for c in component['coefficients'] if c['family'] == family)
    dea, ion = (next(c for c in mapping['components'] if c['component_id'] == i) for i in (DEA, C))
    ratio = (value(dea, 'segment_count') * value(dea, 'segment_diameter') ** 3 / (3.0353 * 3.0435 ** 3)) ** (1 / 3)  # neutral MEA m, sigma
    sigma = ratio * mea['sigma']
    for c in ion['coefficients']:
        c['value']['magnitude'] = dict(dispersion_energy_over_k=mea['epsilon'], segment_diameter=sigma, debye_huckel_diameter=sigma,
                                       born_diameter=sigma, packing_diameter=0.88 * sigma).get(c['family'], c['value']['magnitude'])
    return mapping, {f: value(ion, f) for f in ('dispersion_energy_over_k', 'segment_diameter', 'debye_huckel_diameter', 'born_diameter', 'packing_diameter')}


def prepare():
    mea = mea_carbamate()
    route = read(OLD / 'route-current.json')
    for i, start in enumerate(route['starts']):
        old = read(OLD / start['path'])
        # The rule must reproduce the #398 inputs from F0 before it is applied to F2.
        assert carbamate(copy.deepcopy(old), mea['F0'])[0] == old, f'{start["path"]}: D2 rule does not reproduce the F0 carbamate'
        new, values = carbamate(old, mea['F2'])
        for c in next(c for c in new['components'] if c['component_id'] == C)['coefficients']:
            if c['family'] == 'dispersion_energy_over_k':
                c['provenance'] = dict(source_id='issue-413', locator=F2_SOURCE)
            elif c['family'] in values:
                c['provenance'] = dict(c['provenance'], locator=f"{c['provenance']['locator']}; MEA diameter from fit F2 (issue #413)")
        dump(OLD / (P + start['path']), new)
        route['starts'][i] = dict(start, path=P + start['path'], sha256=sha(OLD / (P + start['path'])))
    route['output'] = '../../results/runs/413'
    s0 = route['starts'][0]
    record = lambda ref: f'{{"path" = "{ref["path"]}", "sha256" = "{ref["sha256"]}"}}'
    start = f'{{"path" = "{s0["path"]}", "sha256" = "{s0["sha256"]}", "reactions" = {record(s0["reactions"])}, "coordinates" = {record(s0["coordinates"])}}}'
    lines = (OLD / 'DEA-current.toml').read_text().splitlines()
    swap = dict(start=start, endpoint=start)
    lines = [f'{line.split(" = ", 1)[0]} = {swap[line.split(" = ", 1)[0]]}' if line.split(' = ', 1)[0] in swap else line for line in lines]
    (OLD / f'{P}DEA.toml').write_text('\n'.join(lines) + '\n')
    route['specification'] = f'{P}DEA.toml'
    dump(OLD / f'{P}route.json', route)
    table = read(OLD / 'parameter-table-declarations.json')
    for row in table['rows']:
        family = row['parameter'].removeprefix(f'{C}/')
        if family == 'dispersion_energy_over_k' and row['parameter'].startswith(C):
            row['source'] = F2_SOURCE
        elif family in ('segment_diameter', 'debye_huckel_diameter', 'packing_diameter', 'born_diameter') and row['parameter'].startswith(C):
            row['source'] += '; MEA diameter from fit F2 (issue #413)'
    table.pop('endpoint_sha256')  # the #346 endpoint hash; this run reports its own selected fit
    dump(OLD / f'{P}parameter-table-declarations.json', table)
    print(json.dumps(dict(mea=mea, dea_carbamate=values), indent=2))


def run(out):
    import rerun
    from part_ii import Route, ROOT, SHARED
    started, timings = monotonic(), {}
    shared, adopted = read(SHARED), ROOT / 'analyses/solvent_specification_mea/inputs/endpoint.json'
    # 1. Replay the selected #398 endpoint on its own route; all 299 rows must match the retained predictions.
    old = Route(OLD / 'route-current.json', Path(f'{out}-replay-398'))
    chosen = read(PREVIOUS / 'selection.json')['chosen']
    begin = monotonic()
    values, available, cost = old.replay(chosen['parameters'])
    timings['objective_evaluation_s'] = monotonic() - begin
    native = chosen['optimizer_report']
    replay = rerun.error(values, [dict(r, value=p) for r, p in zip(values, native['predictions'][:len(values)], strict=True)], cost, native['data_cost'])
    assert available and max(replay[k] for k in ('max_relative_prediction_error', 'relative_cost_error')) <= rerun.LIMIT, replay
    old.reduce(chosen['parameters'])
    with (PREVIOUS / 'paper-data.csv').open() as f:
        retained = {r['identity']: float(r['predicted']) for r in csv.DictReader(f)}
    rows = old.result('data-rows.json')
    assert len(rows) == len(retained) == 299 and all(r['status'] == 'Available' for r in rows)
    rows_error = max(abs(r['value'] / retained[r['identity']] - 1) for r in rows)
    assert rows_error <= rerun.LIMIT, rows_error
    checks = dict(replay_398=dict(replay, limit=rerun.LIMIT, all_rows=299, all_rows_max_relative_error=rows_error))
    print(f"#398 replay: cost {cost:.10g}, max rel {replay['max_relative_prediction_error']:.2e}, 299-row max rel {rows_error:.2e}; "
          f"objective {timings['objective_evaluation_s']:.1f} s", flush=True)
    # 2. Time one stability search at the new start before the campaign (separate folder: the campaign's split record stays clean).
    probe = Route(OLD / f'{P}route.json', Path(f'{out}-probe'))
    begin = monotonic()
    probe.search(probe.start(probe.config['starts'][0]))
    timings['stability_search_s'] = monotonic() - begin
    print(f"one stability search at start-0: {timings['stability_search_s']:.1f} s", flush=True)
    # 3. The #398 campaign, unchanged, on the F2-carbamate inputs.
    route = Route(OLD / f'{P}route.json', out)
    for ref in route.config['starts']:
        rerun.check_shared(route.start(ref), read(adopted), shared)
    assert not route.load(route.config['split_record'])['trials']
    checks.update(shared_inputs=dict(adopted_sha256=sha(adopted), shared_values_sha256=sha(SHARED), both_starts=True), earlier_split_compositions=0,
                  carbamate_inputs=dict(mea_parameter_details_sha256=DETAILS_SHA, **mea_carbamate()))
    route.write('checks.json', checks)
    grid = route.grid
    def timed_grid(point, states, **kwargs):
        count, begin = len(list(out.glob('search-*.json'))), monotonic()
        result = grid(point, states, **kwargs)
        if len(list(out.glob('search-*.json'))) > count:
            timings[f'search-{count}'] = monotonic() - begin
            print(f'search-{count}: {timings[f"search-{count}"]:.1f} s', flush=True)
        return result
    route.grid = timed_grid
    route.campaign()
    timings['preflight_and_campaign'] = monotonic() - started
    route.write('timings.json', timings)
    rerun.report(route, adopted, shared)


if __name__ == '__main__':
    prepare() if sys.argv[1] == 'prepare' else run(Path(sys.argv[2]))
